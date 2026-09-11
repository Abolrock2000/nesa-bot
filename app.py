from flask import Flask, request, jsonify
import os, json, datetime, threading, time, requests

app = Flask(__name__)

TOKEN = os.getenv("BOT_TOKEN", "").strip()
OWNER_CHAT_ID = "7989818498"
PARTNER_CHAT_ID = "7706282234"
PASSWORD = "1386"
IRAN_TZ = datetime.timezone(datetime.timedelta(hours=3, minutes=30))
MEETING_DATE = datetime.datetime(2026, 3, 15, tzinfo=IRAN_TZ)

def now():
    return datetime.datetime.now(datetime.timezone.utc).astimezone(IRAN_TZ)

def tg(method, data=None):
    if not TOKEN:
        print("BOT_TOKEN تنظیم نشده است")
        return {}
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/{method}",
            data=data or {}, timeout=60
        )
        return r.json()
    except Exception as e:
        print("Telegram error:", e)
        return {}

def send(cid, text, keyboard=None):
    data = {"chat_id": cid, "text": text}
    if keyboard:
        data["reply_markup"] = json.dumps(
            {"keyboard": keyboard, "resize_keyboard": True},
            ensure_ascii=False
        )
    return tg("sendMessage", data)

def send_photo(cid, photo, caption=""):
    return tg("sendPhoto", {
        "chat_id": cid, "photo": photo, "caption": caption
    })

def send_file(cid, kind, file_id, caption=""):
    methods = {
        "photo": ("sendPhoto", "photo"),
        "video": ("sendVideo", "video"),
        "audio": ("sendAudio", "audio"),
        "voice": ("sendVoice", "voice"),
        "document": ("sendDocument", "document")
    }
    method, field = methods[kind]
    return tg(method, {
        "chat_id": cid, field: file_id, "caption": caption
    })

def menu():
    return [
        ["📸 عکس‌ها"],
        ["📅 روز آشنایی", "⏳ ساعت تا تولدت"],
        ["💬 چت دوطرفه"],
        ["🔙 بازگشت"]
    ]

def chat_menu():
    return [
        ["📤 ارسال پیام"],
        ["📤 ارسال عکس", "📤 ارسال فیلم"],
        ["📤 ارسال موزیک"],
        ["🔙 بازگشت"]
    ]

PHOTOS = {
    "📸 عکس ۱": ("photos/1.jpg", "❤️ عشق زندگیم"),
    "📸 عکس ۲": ("photos/2.jpg", "💫 قلب من"),
    "📸 عکس ۳": ("photos/3.jpg", "🌸 بهار زندگی من"),
    "📸 عکس ۴": ("photos/4.jpg", "🌙 ماه شب‌های من"),
    "📸 عکس ۵": ("photos/5.jpg", "☀️ روشن‌ترین روز من"),
    "📸 عکس ۶": ("photos/6.jpg", "❤️ تمام دنیای من"),
    "📸 عکس ۷": (
        "https://i.postimg.cc/5tDhyRgM/IMG-20260318-184739-714.jpg",
        "💖 عکس مخصوص"
    )
}

sessions = {}

def session(cid):
    return sessions.setdefault(cid, {
        "photos": False,
        "password": False,
        "chat_message": False,
        "file_mode": None
    })

def get_file_type(message):
    if message.get("photo"):
        return "photo", message["photo"][-1]["file_id"], "photo.jpg"
    if message.get("video"):
        x = message["video"]
        return "video", x["file_id"], x.get("file_name", "video.mp4")
    if message.get("audio"):
        x = message["audio"]
        return "audio", x["file_id"], x.get("file_name", "audio.mp3")
    if message.get("voice"):
        return "voice", message["voice"]["file_id"], "voice.ogg"
    if message.get("document"):
        x = message["document"]
        return "document", x["file_id"], x.get("file_name", "file")
    return None, None, None

def forward_file(cid, kind, file_id, caption):
    target = PARTNER_CHAT_ID if str(cid) == OWNER_CHAT_ID else OWNER_CHAT_ID
    result = send_file(target, kind, file_id, caption)
    return result.get("ok", False)

def handle_message(cid, message):
    s = session(cid)
    text = message.get("text", "").strip()
    kind, file_id, filename = get_file_type(message)
    caption = message.get("caption", "")

    if text == "/start":
        sessions[cid] = {
            "photos": False,
            "password": False,
            "chat_message": False,
            "file_mode": None
        }
        return send(cid, "🌻❤️ به دنیای ahu goozlum خوش آمدی ❤️🌻", menu())

    if text == "🔙 بازگشت":
        sessions[cid] = {
            "photos": False,
            "password": False,
            "chat_message": False,
            "file_mode": None
        }
        return send(cid, "🏠 منوی اصلی", menu())

    if text == "📸 عکس‌ها":
        if not s["photos"]:
            s["password"] = True
            return send(cid, "🔐 رمز گالری را وارد کن.")
        return send(cid, "📸 یک عکس انتخاب کن.", [
            ["📸 عکس ۱", "📸 عکس ۲", "📸 عکس ۳"],
            ["📸 عکس ۴", "📸 عکس ۵", "📸 عکس ۶"],
            ["📸 عکس ۷"],
            ["🔙 بازگشت"]
        ])

    if s["password"]:
        if text == PASSWORD:
            s["password"] = False
            s["photos"] = True
            return send(cid, "✅ گالری باز شد.", [
                ["📸 عکس ۱", "📸 عکس ۲", "📸 عکس ۳"],
                ["📸 عکس ۴", "📸 عکس ۵", "📸 عکس ۶"],
                ["📸 عکس ۷"],
                ["🔙 بازگشت"]
            ])
        return send(cid, "❌ رمز اشتباه است.")

    if text in PHOTOS and s["photos"]:
        path, caption_text = PHOTOS[text]
        if path.startswith("http") or os.path.exists(path):
            return send_photo(cid, path, caption_text)
        return send(cid, "❌ فایل عکس روی سرور پیدا نشد.")

    if text == "📅 روز آشنایی":
        seconds = max(0, int((now() - MEETING_DATE).total_seconds()))
        days = seconds // 86400
        return send(cid, f"💞 روز آشنایی ما ❤️\n\n📅 ۲۴ اسفند ۱۴۰۴\n🌻 {days} روز گذشته است.")

    if text == "⏳ ساعت تا تولدت":
        current = now()
        birthday = datetime.datetime(
            current.year, 8, 8, 0, 0, tzinfo=IRAN_TZ
        )
        if current >= birthday:
            birthday = birthday.replace(year=current.year + 1)
        hours = int((birthday - current).total_seconds() // 3600)
        return send(cid, f"🎂 شمارش معکوس تولد\n\n⏳ {hours:,} ساعت مانده ❤️")

    if text == "💬 چت دوطرفه":
        if str(cid) not in {OWNER_CHAT_ID, PARTNER_CHAT_ID}:
            return send(cid, "❌ دسترسی ندارید.")
        s["chat_message"] = False
        s["file_mode"] = None
        return send(cid, "💬 چت دوطرفه فعال شد.", chat_menu())

    if text == "📤 ارسال پیام":
        s["chat_message"] = True
        s["file_mode"] = None
        return send(cid, "💬 پیامت را بنویس.", chat_menu())

    if text in ["📤 ارسال عکس", "📤 ارسال فیلم", "📤 ارسال موزیک"]:
        s["file_mode"] = {
            "📤 ارسال عکس": "photo",
            "📤 ارسال فیلم": "video",
            "📤 ارسال موزیک": "audio"
        }[text]
        s["chat_message"] = False
        return send(cid, "فایل را همینجا بفرست.", chat_menu())

    if s["chat_message"] and text:
        target = PARTNER_CHAT_ID if str(cid) == OWNER_CHAT_ID else OWNER_CHAT_ID
        sender = "مالک" if str(cid) == OWNER_CHAT_ID else "پارتنر"
        result = send(target, f"💬 پیام از {sender}:\n\n{text}")
        s["chat_message"] = False
        return send(cid, "✅ پیام ارسال شد." if result.get("ok") else "❌ ارسال ناموفق بود.", chat_menu())

    if kind and s["file_mode"]:
        if kind != s["file_mode"]:
            return send(cid, f"❌ باید {s['file_mode']} ارسال کنی.")
        ok = forward_file(cid, kind, file_id, caption)
        s["file_mode"] = None
        return send(cid, "✅ فایل ارسال شد." if ok else "❌ ارسال ناموفق بود.", chat_menu())

    return send(cid, "از دکمه‌های پایین استفاده کن ❤️", menu())

@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return "ahu goozlum bot is running", 200

    try:
        update = request.get_json(silent=True) or {}
        message = update.get("message") or update.get("edited_message")
        if not message:
            return "OK", 200

        cid = str(message.get("chat", {}).get("id", ""))
        if cid:
            handle_message(cid, message)
    except Exception as e:
        print("Webhook error:", repr(e))

    return "OK", 200

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "bot_token_configured": bool(TOKEN),
        "owner": OWNER_CHAT_ID,
        "partner": PARTNER_CHAT_ID
    })

if __name__ == "__main__":
    print("🚀 ربات روشن شد")
    print("BOT_TOKEN:", "OK" if TOKEN else "MISSING")
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "10000")),
        debug=False
    )
