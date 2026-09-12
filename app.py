from flask import Flask, request, jsonify
import requests
import json
import random
import datetime
import os
import sqlite3
import threading
import time
from zoneinfo import ZoneInfo

app = Flask(__name__)

# ============================================================
# تنظیمات
# ============================================================
TOKEN = os.environ.get("BOT_TOKEN", "")
OWNER_CHAT_ID = "7989818498"
PARTNER_CHAT_ID = "7706282234"
PASSWORD = "1386"

CHANNEL_ID = "-1004499565151"
CHANNEL_NAME = "Nafas❤️Atashi"
IRAN_TZ = ZoneInfo("Asia/Tehran")
DB_PATH = os.environ.get("CHANNEL_DB", "channel_queue.db")

DEFAULT_HOUR = 10
DEFAULT_MINUTE = 10
POST_GAP_SECONDS = 5

BOT_API = f"https://api.telegram.org/bot{TOKEN}"

# ============================================================
# دیتابیس صف کانال
# ============================================================
def db():
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    con.execute("""
        CREATE TABLE IF NOT EXISTS queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL,
            content TEXT NOT NULL,
            caption TEXT DEFAULT '',
            created_at TEXT NOT NULL
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    con.execute(
        "INSERT OR IGNORE INTO settings(key,value) VALUES('hour',?)",
        (str(DEFAULT_HOUR),)
    )
    con.execute(
        "INSERT OR IGNORE INTO settings(key,value) VALUES('minute',?)",
        (str(DEFAULT_MINUTE),)
    )
    con.commit()
    con.close()

def setting(key, default=None):
    con = db()
    row = con.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    con.close()
    return row["value"] if row else default

def set_setting(key, value):
    con = db()
    con.execute(
        "INSERT INTO settings(key,value) VALUES(?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, str(value))
    )
    con.commit()
    con.close()

def add_queue(kind, content, caption=""):
    con = db()
    con.execute(
        "INSERT INTO queue(kind,content,caption,created_at) VALUES(?,?,?,?)",
        (kind, content, caption or "", datetime.datetime.now(IRAN_TZ).isoformat())
    )
    con.commit()
    con.close()

def get_queue():
    con = db()
    rows = con.execute("SELECT * FROM queue ORDER BY id").fetchall()
    con.close()
    return rows

def delete_queue_item(item_id):
    con = db()
    con.execute("DELETE FROM queue WHERE id=?", (item_id,))
    con.commit()
    con.close()

def clear_queue():
    con = db()
    con.execute("DELETE FROM queue")
    con.commit()
    con.close()

# ============================================================
# تلگرام
# ============================================================
def tg(method, data=None, files=None):
    if not TOKEN:
        return {"ok": False, "description": "BOT_TOKEN تنظیم نشده است"}
    try:
        if files:
            r = requests.post(f"{BOT_API}/{method}", data=data or {}, files=files, timeout=60)
        else:
            r = requests.post(f"{BOT_API}/{method}", data=data or {}, timeout=60)
        return r.json()
    except Exception as e:
        return {"ok": False, "description": str(e)}

def send_text(chat_id, text, reply_markup=None):
    data = {"chat_id": chat_id, "text": text}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup, ensure_ascii=False)
    return tg("sendMessage", data)

def clean_file_id(value):
    # شناسه‌ای که در صف ذخیره شده ممکن است با file_id: شروع شود.
    if isinstance(value, str) and value.startswith("file_id:"):
        return value[len("file_id:"):]
    return value

def send_media(method, field, chat_id, value, caption=""):
    value = clean_file_id(value)
    data = {"chat_id": chat_id, field: value}
    if caption:
        data["caption"] = caption
    return tg(method, data)

def send_photo(chat_id, value, caption=""):
    return send_media("sendPhoto", "photo", chat_id, value, caption)

def send_audio(chat_id, value, caption=""):
    return send_media("sendAudio", "audio", chat_id, value, caption)

def send_video(chat_id, value, caption=""):
    return send_media("sendVideo", "video", chat_id, value, caption)

def send_document(chat_id, value, caption=""):
    return send_media("sendDocument", "document", chat_id, value, caption)

def send_voice(chat_id, value, caption=""):
    return send_media("sendVoice", "voice", chat_id, value, caption)

def send_message_to_queue(kind, file_id, caption=""):
    add_queue(kind, file_id, caption)
    return True

# ============================================================
# منوها
# ============================================================
def main_keyboard():
    return {
        "keyboard": [
            [{"text": "📢 مدیریت کانال"}],
            [{"text": "💬 ارسال پیام به پارتنر"}],
            [{"text": "📊 وضعیت"}]
        ],
        "resize_keyboard": True
    }

def channel_keyboard():
    return {
        "keyboard": [
            [{"text": "➕ افزودن متن"}, {"text": "🎵 افزودن آهنگ"}],
            [{"text": "🎬 افزودن کلیپ"}, {"text": "📋 وضعیت صف"}],
            [{"text": "🗑 پاک کردن صف"}, {"text": "⚡ ارسال فوری"}],
            [{"text": "⏰ تغییر ساعت"}, {"text": "🔙 بازگشت"}]
        ],
        "resize_keyboard": True
    }

def is_owner(chat_id):
    return str(chat_id) == str(OWNER_CHAT_ID)

# حالت‌های موقت
STATE = {}
# STATE[chat_id] = "channel_text" / "channel_audio" / ...

# ============================================================
# انتشار صف
# ============================================================
def publish_daily(force=False):
    rows = get_queue()
    if not rows:
        return

    for item in rows:
        kind = item["kind"]
        content = clean_file_id(item["content"])
        caption = item["caption"] or ""
        if kind == "text":
            result = send_text(CHANNEL_ID, content)
        elif kind == "audio":
            result = send_audio(CHANNEL_ID, content, caption)
        elif kind == "video":
            result = send_video(CHANNEL_ID, content, caption)
        else:
            result = {"ok": False, "description": "نوع ناشناخته"}

        if result.get("ok"):
            delete_queue_item(item["id"])
        else:
            send_text(
                OWNER_CHAT_ID,
                f"❌ ارسال آیتم شماره {item['id']} انجام نشد:\n"
                f"{result.get('description', 'خطای نامشخص')}"
            )
            # آیتم حذف نمی‌شود تا بعداً دوباره امتحان شود.
            if not force:
                break
        time.sleep(POST_GAP_SECONDS)

def scheduler():
    last_run = None
    while True:
        try:
            now = datetime.datetime.now(IRAN_TZ)
            hour = int(setting("hour", DEFAULT_HOUR))
            minute = int(setting("minute", DEFAULT_MINUTE))
            key = now.strftime("%Y-%m-%d")
            if now.hour == hour and now.minute == minute and last_run != key:
                last_run = key
                publish_daily()
            time.sleep(20)
        except Exception as e:
            print("scheduler error:", e)
            time.sleep(20)

# ============================================================
# دریافت فایل و صف
# ============================================================
def get_file_id_from_message(message):
    if message.get("audio"):
        a = message["audio"]
        return "audio", a["file_id"], a.get("file_name", ""), a.get("duration", "")
    if message.get("video"):
        v = message["video"]
        return "video", v["file_id"], v.get("file_name", ""), v.get("duration", "")
    if message.get("document"):
        d = message["document"]
        name = d.get("file_name", "")
        mime = d.get("mime_type", "")
        # MP3هایی که به‌صورت فایل فرستاده می‌شوند هم آهنگ محسوب شوند.
        if mime.startswith("audio/") or name.lower().endswith(
            (".mp3", ".m4a", ".wav", ".ogg", ".flac")
        ):
            return "audio", d["file_id"], name, ""
        return "document", d["file_id"], name, ""
    return None, None, "", ""

def queue_status():
    rows = get_queue()
    hour = int(setting("hour", DEFAULT_HOUR))
    minute = int(setting("minute", DEFAULT_MINUTE))
    lines = [
        f"📢 {CHANNEL_NAME}",
        f"⏰ زمان انتشار روزانه: {hour:02d}:{minute:02d} به وقت ایران",
        f"📦 تعداد صف: {len(rows)}",
        ""
    ]
    for i, row in enumerate(rows, 1):
        label = {"text": "متن", "audio": "آهنگ", "video": "کلیپ"}.get(row["kind"], row["kind"])
        lines.append(f"{i}. {label} — شناسه {row['id']}")
    return "\n".join(lines)

def handle_channel(chat_id, message, text):
    state = STATE.get(str(chat_id), "")
    if state == "channel_text":
        if text:
            add_queue("text", text)
            STATE.pop(str(chat_id), None)
            send_text(chat_id, "✅ متن به صف اضافه شد.", channel_keyboard())
        else:
            send_text(chat_id, "یک متن بفرست.", channel_keyboard())
        return

    if state in ("channel_audio", "channel_video"):
        kind, file_id, name, extra = get_file_id_from_message(message)
        wanted = "audio" if state == "channel_audio" else "video"
        if file_id and kind == wanted:
            caption = text if text else ""
            add_queue(wanted, file_id, caption)
            STATE.pop(str(chat_id), None)
            send_text(chat_id, f"✅ {('آهنگ' if wanted == 'audio' else 'کلیپ')} به صف اضافه شد.", channel_keyboard())
        else:
            send_text(chat_id, "فایل مناسب بفرست؛ برای آهنگ MP3 یا فایل صوتی و برای کلیپ ویدیو.", channel_keyboard())
        return

    if state == "channel_time":
        try:
            parts = text.replace("：", ":").split(":")
            h, m = int(parts[0]), int(parts[1])
            if not (0 <= h <= 23 and 0 <= m <= 59):
                raise ValueError
            set_setting("hour", h)
            set_setting("minute", m)
            STATE.pop(str(chat_id), None)
            send_text(chat_id, f"✅ ساعت انتشار روی {h:02d}:{m:02d} تنظیم شد.", channel_keyboard())
        except Exception:
            send_text(chat_id, "فرمت درست: 10:10", channel_keyboard())
        return

    if text == "➕ افزودن متن":
        STATE[str(chat_id)] = "channel_text"
        send_text(chat_id, "متن موردنظر را بفرست.", channel_keyboard())
    elif text == "🎵 افزودن آهنگ":
        STATE[str(chat_id)] = "channel_audio"
        send_text(chat_id, "آهنگ را به‌صورت Audio یا فایل MP3 بفرست.", channel_keyboard())
    elif text == "🎬 افزودن کلیپ":
        STATE[str(chat_id)] = "channel_video"
        send_text(chat_id, "کلیپ را بفرست.", channel_keyboard())
    elif text == "📋 وضعیت صف":
        send_text(chat_id, queue_status(), channel_keyboard())
    elif text == "🗑 پاک کردن صف":
        clear_queue()
        send_text(chat_id, "🗑 صف کامل پاک شد.", channel_keyboard())
    elif text == "⚡ ارسال فوری":
        send_text(chat_id, "⏳ در حال ارسال صف...", channel_keyboard())
        threading.Thread(target=publish_daily, kwargs={"force": True}, daemon=True).start()
    elif text == "⏰ تغییر ساعت":
        STATE[str(chat_id)] = "channel_time"
        send_text(chat_id, f"ساعت جدید را مثل 10:10 بفرست.\nساعت فعلی: {int(setting('hour', DEFAULT_HOUR)):02d}:{int(setting('minute', DEFAULT_MINUTE)):02d}", channel_keyboard())
    elif text == "🔙 بازگشت":
        STATE.pop(str(chat_id), None)
        send_text(chat_id, "منوی اصلی", main_keyboard())
    else:
        send_text(chat_id, "از گزینه‌های منو استفاده کن.", channel_keyboard())

# ============================================================
# وبهوک
# ============================================================
@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return "OK", 200

    update = request.get_json(silent=True) or {}
    message = update.get("message") or update.get("edited_message") or {}
    chat = message.get("chat") or {}
    chat_id = str(chat.get("id", ""))
    text = (message.get("text") or "").strip()

    if not chat_id:
        return jsonify(ok=True)

    if not is_owner(chat_id):
        # فقط پارتنر می‌تواند پیام عادی بفرستد؛ مدیریت کانال فقط مالک.
        if chat_id == str(PARTNER_CHAT_ID):
            send_text(OWNER_CHAT_ID, f"💬 پیام پارتنر:\n{text or '[فایل ارسال شد]'}")
        return jsonify(ok=True)

    if text == "/start":
        send_text(chat_id, "سلام. رمز را بفرست.", main_keyboard())
        STATE[chat_id] = "password"
        return jsonify(ok=True)

    if STATE.get(chat_id) == "password":
        if text == PASSWORD:
            STATE.pop(chat_id, None)
            send_text(chat_id, "ورود موفق بود.", main_keyboard())
        else:
            send_text(chat_id, "رمز اشتباه است.")
        return jsonify(ok=True)

    # برای سادگی مالک پس از یک بار ورود می‌تواند منو را استفاده کند.
    if text == "📢 مدیریت کانال" or STATE.get(chat_id, "").startswith("channel"):
        if text == "📢 مدیریت کانال":
            STATE.pop(chat_id, None)
            send_text(chat_id, f"مدیریت {CHANNEL_NAME}", channel_keyboard())
        else:
            handle_channel(chat_id, message, text)
        return jsonify(ok=True)

    if text == "📊 وضعیت":
        send_text(chat_id, queue_status(), main_keyboard())
        return jsonify(ok=True)

    if text == "💬 ارسال پیام به پارتنر":
        STATE[chat_id] = "partner_text"
        send_text(chat_id, "پیامت را بفرست.")
        return jsonify(ok=True)

    if STATE.get(chat_id) == "partner_text":
        result = send_text(PARTNER_CHAT_ID, text or "[پیام بدون متن]")
        STATE.pop(chat_id, None)
        send_text(chat_id, "ارسال شد." if result.get("ok") else "خطا در ارسال.", main_keyboard())
        return jsonify(ok=True)

    send_text(chat_id, "از منوی اصلی استفاده کن.", main_keyboard())
    return jsonify(ok=True)

@app.route("/health")
def health():
    return "healthy", 200

# ============================================================
# اجرا
# ============================================================
init_db()
threading.Thread(target=scheduler, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
