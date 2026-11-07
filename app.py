# -*- coding: utf-8 -*-
# Ahu Goozlum Bot - diagnostic and reliability update
from flask import Flask, request, jsonify
import requests
import json
import random
import datetime
import os
import threading
import time
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("ahu_bot")

TOKEN = os.environ.get("BOT_TOKEN", "").strip()
OWNER_CHAT_ID = "7989818498"
PARTNER_CHAT_ID = "7706282234"
PASSWORD = os.environ.get("GALLERY_PASSWORD", "1386")

BIRTH_DAY, BIRTH_MONTH = 8, 8
BIRTH_HOUR, BIRTH_MINUTE = 0, 0
IRAN_TZ = datetime.timezone(datetime.timedelta(hours=3, minutes=30))
WEBSITE_URL = "https://nesa-bot.onrender.com"

AUTHORIZED_USERS = {OWNER_CHAT_ID, PARTNER_CHAT_ID}
user_access = {}
PARTNER_ACTIVITY = {}
PENDING_USERS = {}
LOGIN_PASSWORDS = {}
BOT_ACTIVE = True

PHOTOS = {
    "📸 عکس ۱": {"path": "photos/IMG_20260801_224828_501.jpg", "caption": "🌹 عشق زندگیم... ❤️"},
    "📸 عکس ۲": {"path": "photos/null_14041109_222510829.jpg", "caption": "💫 قلب من... تو هستی"},
    "📸 عکس ۳": {"path": "photos/null_14041125_153021650.jpg", "caption": "🌸 بهار زندگی من..."},
    "📸 عکس ۴": {"path": "photos/IMG_20260707_153249_974.jpg", "caption": "🌙 ماه شب‌های من..."},
    "📸 عکس ۵": {"path": "photos/IMG_20260709_234307_968.jpg", "caption": "☀️ روشن‌ترین روز من..."},
    "📸 عکس ۶": {"path": "photos/IMG_20260719_211523_837.jpg", "caption": "❤️ تمام دنیای من..."},
    "📸 عکس ۷": {"path": "https://i.postimg.cc/5tDhyRgM/IMG-20260318-184739-714.jpg", "caption": "💖 عکس مخصوص... ❤️"},
    "📸 عکس جدید": {"path": "photos/file_00000000f1788210bc5e8d993e16a277.png", "caption": "🌹 این عکس مخصوص توست... ❤️"},
}

def iran_now():
    return datetime.datetime.now(datetime.timezone.utc).astimezone(IRAN_TZ)

def api_call(method, chat_id=None, data=None, files=None, timeout=30):
    """Central Telegram API caller: logs useful errors without printing the bot token."""
    if not TOKEN:
        log.error("BOT_TOKEN is missing in Render Environment.")
        return False, {"description": "BOT_TOKEN is missing"}
    payload = dict(data or {})
    if chat_id is not None:
        payload["chat_id"] = str(chat_id)
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    try:
        response = requests.post(url, data=payload, files=files, timeout=timeout)
        try:
            body = response.json()
        except Exception:
            body = {"description": response.text[:500]}
        if response.status_code != 200 or not body.get("ok", False):
            log.error("Telegram API %s failed: HTTP %s | %s",
                      method, response.status_code, body)
            return False, body
        return True, body
    except requests.RequestException as exc:
        log.exception("Telegram API %s request exception: %s", method, exc)
        return False, {"description": str(exc)}

def send_message(chat_id, text, reply_markup=None, protect_content=True):
    data = {"text": str(text), "protect_content": str(bool(protect_content)).lower()}
    if reply_markup is not None:
        data["reply_markup"] = json.dumps(reply_markup, ensure_ascii=False)
    ok, _ = api_call("sendMessage", chat_id, data, timeout=25)
    log.info("sendMessage to chat %s: %s", str(chat_id), "OK" if ok else "FAILED")
    return ok

def send_media(method, chat_id, media_key, media_data, caption="", protect_content=True,
               extra=None, timeout=120):
    if not media_data:
        log.error("%s called with empty media data", method)
        return False
    data = {"caption": caption or "", "protect_content": str(bool(protect_content)).lower()}
    if extra:
        data.update({k: v for k, v in extra.items() if v not in (None, "")})
    files = None
    if isinstance(media_data, str) and media_data.startswith("file_id:"):
        data[media_key] = media_data.split(":", 1)[1]
    elif isinstance(media_data, str) and media_data.startswith("http"):
        data[media_key] = media_data
    elif isinstance(media_data, str) and os.path.isfile(media_data):
        try:
            f = open(media_data, "rb")
            files = {media_key: f}
        except OSError as exc:
            log.exception("Cannot open media file %s: %s", media_data, exc)
            return False
    else:
        log.error("Media not found or unsupported: %s", str(media_data)[:120])
        return False
    try:
        ok, _ = api_call(method, chat_id, data, files=files, timeout=timeout)
        return ok
    finally:
        if files:
            for f in files.values():
                f.close()

def send_photo(chat_id, photo, caption="", protect_content=True):
    return send_media("sendPhoto", chat_id, "photo", photo, caption, protect_content, timeout=60)

def send_video(chat_id, video, caption="", protect_content=True):
    return send_media("sendVideo", chat_id, "video", video, caption, protect_content, timeout=150)

def send_audio(chat_id, audio, caption="", title="", performer="", protect_content=True):
    return send_media("sendAudio", chat_id, "audio", audio, caption, protect_content,
                      {"title": title, "performer": performer}, timeout=150)

def send_document(chat_id, document, caption="", protect_content=True):
    return send_media("sendDocument", chat_id, "document", document, caption,
                      protect_content, timeout=150)

def send_voice(chat_id, voice, caption="", protect_content=True):
    return send_media("sendVoice", chat_id, "voice", voice, caption,
                      protect_content, timeout=150)

def get_main_keyboard(chat_id=None):
    rows = [["📸 عکس‌ها"], ["📅 روز آشنایی", "⏳ ساعت تا تولدت"], ["💬 چت دوطرفه"]]
    if str(chat_id) == OWNER_CHAT_ID:
        rows.append(["📊 وضعیت پارتنر"])
    rows.append(["🔙 بازگشت به منو"])
    return {"keyboard": rows, "resize_keyboard": True}

def get_photo_keyboard():
    return {"keyboard": [
        ["📸 عکس ۱", "📸 عکس ۲", "📸 عکس ۳"],
        ["📸 عکس ۴", "📸 عکس ۵", "📸 عکس ۶"],
        ["📸 عکس ۷", "📸 عکس جدید"],
        ["🔙 بازگشت به منو"]
    ], "resize_keyboard": True}

def get_chat_keyboard():
    return {"keyboard": [
        ["📤 ارسال پیام"], ["📤 ارسال عکس", "📤 ارسال فیلم"],
        ["📤 ارسال موزیک"], ["🔙 بازگشت به منو"]
    ], "resize_keyboard": True}

def get_password_keyboard():
    return {"keyboard": [["🔙 بازگشت به منو"]], "resize_keyboard": True}

def report_user_interaction(chat_id, action, first_name="", last_name="", username="", phone_number=""):
    chat_id = str(chat_id)
    if chat_id == OWNER_CHAT_ID:
        return
    now = iran_now()
    data = PARTNER_ACTIVITY.setdefault(chat_id, {
        "first_seen": now, "last_seen": now, "count": 0,
        "first_name": "", "last_name": "", "username": "",
        "phone_number": "", "last_action": ""
    })
    for key, value in (("first_name", first_name), ("last_name", last_name),
                       ("username", username), ("phone_number", phone_number)):
        if value:
            data[key] = value
    data["last_seen"] = now
    data["last_action"] = action
    data["count"] += 1
    weekdays = {"Monday":"دوشنبه", "Tuesday":"سه‌شنبه", "Wednesday":"چهارشنبه",
                "Thursday":"پنج‌شنبه", "Friday":"جمعه", "Saturday":"شنبه", "Sunday":"یک‌شنبه"}
    uname = data["username"]
    profile = f"https://t.me/{uname}" if uname else "ندارد"
    msg = (
        "👀 تعامل جدید با ربات\n"
        f"👤 آیدی عددی: {chat_id}\n"
        f"• نام: {data['first_name'] or 'نامشخص'}\n"
        f"• نام خانوادگی: {data['last_name'] or 'نامشخص'}\n"
        f"• یوزرنیم: @{uname if uname else 'ندارد'}\n"
        f"• شماره تلفن: {data['phone_number'] or 'نامشخص'}\n\n"
        f"📌 نوع تعامل: {action}\n"
        f"📅 تاریخ: {now:%Y/%m/%d}\n"
        f"📆 روز: {weekdays.get(now.strftime('%A'), now.strftime('%A'))}\n"
        f"⏰ ساعت: {now:%H:%M:%S}\n"
        f"🔢 تعداد تعامل‌ها: {data['count']}\n"
        f"🔗 لینک پروفایل: {profile}"
    )
    # Activity report is best-effort; its failure must not prevent the user's reply.
    try:
        send_message(OWNER_CHAT_ID, msg)
    except Exception:
        log.exception("Activity report failed")

def meeting_seconds():
    start = datetime.datetime(2026, 3, 15, tzinfo=IRAN_TZ)
    return max(0, int((iran_now() - start).total_seconds()))

def hours_until_birthday():
    now = iran_now()
    target = datetime.datetime(now.year, BIRTH_MONTH, BIRTH_DAY,
                               BIRTH_HOUR, BIRTH_MINUTE, tzinfo=IRAN_TZ)
    if now >= target:
        target = datetime.datetime(now.year + 1, BIRTH_MONTH, BIRTH_DAY,
                                   BIRTH_HOUR, BIRTH_MINUTE, tzinfo=IRAN_TZ)
    return int((target - now).total_seconds() // 3600)

def send_chat_file(target_id, file_data, protect=True):
    kind, fid = file_data.get("type"), file_data.get("file_id")
    cap = file_data.get("caption", "")
    if not fid:
        return False
    ref = "file_id:" + fid
    if kind == "photo": return send_photo(target_id, ref, cap, protect)
    if kind == "video": return send_video(target_id, ref, cap, protect)
    if kind == "audio":
        return send_audio(target_id, ref, cap, file_data.get("title", "🎵"),
                          file_data.get("performer", "❤️"), protect)
    if kind == "document": return send_document(target_id, ref, cap, protect)
    if kind == "voice": return send_voice(target_id, ref, cap, protect)
    return False

def request_access(user_id, first_name="", username=""):
    user_id = str(user_id)
    if user_id in AUTHORIZED_USERS:
        return
    PENDING_USERS[user_id] = {"first_name": first_name, "username": username}
    keyboard = {"inline_keyboard": [[
        {"text":"✅ تایید", "callback_data":"approve_" + user_id},
        {"text":"❌ رد", "callback_data":"reject_" + user_id}
    ]]}
    send_message(OWNER_CHAT_ID,
        f"🚨 درخواست ورود جدید\n👤 نام: {first_name}\n🆔 آیدی: {user_id}\n"
        f"👤 یوزرنیم: @{username or 'ندارد'}\nپس از تایید، رمز ورود را ارسال کن.", keyboard)

def generate_login_password(user_id):
    pwd = str(random.randint(100000, 999999))
    LOGIN_PASSWORDS[str(user_id)] = pwd
    return pwd

SECOND_QUOTES = [
    "هر ثانیه‌ای که می‌گذرد، عشق من به تو عمیق‌تر می‌شود... ❤️",
    "ثانیه‌ها می‌گذرند، اما عشق من به تو هرگز کهنه نمی‌شود... 🌹",
    "در هر ثانیه‌ای از زندگی‌ام، تو را نفس می‌کشم... 💫",
    "هر ثانیه که می‌گذرد، یک دلیل تازه برای دوست داشتن تو پیدا می‌کنم... ❤️"
]

def handle_message(chat_id, text, file_data=None):
    chat_id, text = str(chat_id), (text or "").strip()
    log.info("handle_message entered: chat=%s text=%r file=%s",
             chat_id, text[:100], (file_data or {}).get("type"))

    if chat_id not in AUTHORIZED_USERS:
        user = user_access.setdefault(chat_id, {"login_ok": False})
        if text == "/start":
            request_access(chat_id)
            send_message(chat_id, "⏳ درخواست ورود شما برای صاحب ربات ارسال شد.")
            return
        if not user.get("login_ok"):
            if LOGIN_PASSWORDS.get(chat_id) and text == LOGIN_PASSWORDS[chat_id]:
                user["login_ok"] = True
                send_message(chat_id, "✅ رمز صحیح است.", get_main_keyboard(chat_id))
            else:
                send_message(chat_id, "🔒 ابتدا باید توسط صاحب ربات تایید شوید.")
            return

    if not BOT_ACTIVE and chat_id != OWNER_CHAT_ID:
        send_message(chat_id, "🔒 ربات غیرفعال شده است.")
        return

    user = user_access.setdefault(chat_id, {
        "photos": False, "waiting_for_password": False,
        "waiting_for_chat_message": False, "waiting_for_file": False,
        "mode": None, "chat_target": None
    })

    if text == "🔙 بازگشت به منو":
        keep_photos = user.get("photos", False)
        user_access[chat_id] = {
            "photos": keep_photos, "waiting_for_password": False,
            "waiting_for_chat_message": False, "waiting_for_file": False,
            "mode": None, "chat_target": None
        }
        send_message(chat_id, "🏠 برگشتیم به منوی اصلی ❤️", get_main_keyboard(chat_id)); return

    if text == "/start":
        user_access[chat_id] = {
            "photos": False, "waiting_for_password": False,
            "waiting_for_chat_message": False, "waiting_for_file": False,
            "mode": None, "chat_target": None
        }
        send_message(chat_id,
            "🌻❤️ به دنیای ahu goozlum خوش اومدی ❤️🌻\n\n"
            "📸 عکس‌های خصوصی\n📅 روز آشنایی\n⏳ شمارش معکوس تولد\n💬 چت دوطرفه",
            get_main_keyboard(chat_id)); return

    if text == "💬 چت دوطرفه":
        if chat_id not in (OWNER_CHAT_ID, PARTNER_CHAT_ID):
            send_message(chat_id, "❌ این بخش فقط برای مالک و پارتنر است.", get_main_keyboard(chat_id)); return
        user.update(mode="partner_chat", waiting_for_chat_message=False, waiting_for_file=False)
        send_message(chat_id, "💬 چت دوطرفه باز شد ❤️\nپیام، عکس، فیلم، موزیک، فایل یا ویس بفرست.",
                     get_chat_keyboard()); return

    if text in ("📤 ارسال پیام", "📤 ارسال عکس", "📤 ارسال فیلم", "📤 ارسال موزیک"):
        if user.get("mode") != "partner_chat":
            send_message(chat_id, "ابتدا وارد بخش چت دوطرفه شو.", get_main_keyboard(chat_id)); return
        user["chat_target"] = "partner"
        user["waiting_for_chat_message"] = (text == "📤 ارسال پیام")
        user["waiting_for_file"] = {"📤 ارسال عکس":"photo", "📤 ارسال فیلم":"video",
                                    "📤 ارسال موزیک":"audio"}.get(text, False)
        prompts = {"📤 ارسال پیام":"💬 پیامت رو بنویس:",
                   "📤 ارسال عکس":"📸 عکس رو همینجا بفرست:",
                   "📤 ارسال فیلم":"🎥 فیلم رو همینجا بفرست:",
                   "📤 ارسال موزیک":"🎵 موزیک یا MP3 رو همینجا بفرست:"}
        send_message(chat_id, prompts[text], get_chat_keyboard()); return

    if file_data:
        if chat_id == OWNER_CHAT_ID: target_id = PARTNER_CHAT_ID
        elif chat_id == PARTNER_CHAT_ID: target_id = OWNER_CHAT_ID
        else:
            send_message(chat_id, "❌ اجازه استفاده از چت دوطرفه را نداری."); return
        protect = (chat_id == OWNER_CHAT_ID and target_id == PARTNER_CHAT_ID)
        if user.get("mode") != "partner_chat" or not user.get("waiting_for_file"):
            send_message(chat_id, "برای ارسال فایل، ابتدا وارد چت دوطرفه شو و نوع فایل را انتخاب کن.", get_chat_keyboard()); return
        ok = send_chat_file(target_id, file_data, protect)
        send_message(chat_id, "✅ فایل با موفقیت ارسال شد ❤️" if ok else
                     "❌ ارسال فایل ناموفق بود؛ جزئیات خطا در لاگ Render ثبت شده است.",
                     get_chat_keyboard())
        user["waiting_for_file"] = False
        return

    if user.get("waiting_for_chat_message"):
        if chat_id == OWNER_CHAT_ID:
            target_id, sender = PARTNER_CHAT_ID, "عشقت"
        elif chat_id == PARTNER_CHAT_ID:
            target_id, sender = OWNER_CHAT_ID, "پارتنرت"
        else:
            send_message(chat_id, "❌ اجازه ارسال پیام نداری."); return
        ok = send_message(target_id, f"💬 پیام از {sender}:\n\n{text}") if text else False
        send_message(chat_id, "✅ پیام ارسال شد! ❤️" if ok else "❌ ارسال پیام ناموفق بود.")
        user["waiting_for_chat_message"] = False
        return

    if text == "📊 وضعیت پارتنر":
        if chat_id != OWNER_CHAT_ID:
            send_message(chat_id, "❌ دسترسی ندارید."); return
        d = PARTNER_ACTIVITY.get(PARTNER_CHAT_ID)
        if not d:
            send_message(chat_id, "❌ هنوز تعاملی ثبت نشده است.", get_main_keyboard(chat_id)); return
        diff = (iran_now() - d["last_seen"]).total_seconds()
        status = "🟢 اخیراً فعال بوده" if diff < 300 else "🔴 بیش از ۵ دقیقه تعامل نداشته"
        send_message(chat_id,
            f"📊 وضعیت پارتنر\n👤 نام: {d['first_name'] or 'نامشخص'}\n"
            f"📅 اولین تعامل: {d['first_seen']:%Y/%m/%d %H:%M:%S}\n"
            f"📅 آخرین تعامل: {d['last_seen']:%Y/%m/%d %H:%M:%S}\n"
            f"🔢 تعداد تعامل‌ها: {d['count']}\n📌 آخرین اقدام: {d['last_action']}\n❤️ {status}",
            get_main_keyboard(chat_id)); return

    if user.get("waiting_for_password"):
        if text == PASSWORD:
            user["photos"] = True
            user["waiting_for_password"] = False
            send_message(chat_id, "✅ رمز درست بود! گالری باز شد ❤️", get_photo_keyboard())
        else:
            send_message(chat_id, "❌ رمز اشتباهه! دوباره امتحان کن ❤️", get_password_keyboard())
        return

    if text == "📸 عکس‌ها":
        if user.get("photos"):
            send_message(chat_id, "📸 کدوم عکس رو می‌خوای ببینی؟ ❤️", get_photo_keyboard())
        else:
            user["waiting_for_password"] = True
            send_message(chat_id, "🔐 برای ورود به گالری رمز مخصوص رو وارد کن ❤️", get_password_keyboard())
        return

    if text in PHOTOS:
        if not user.get("photos"):
            user["waiting_for_password"] = True
            send_message(chat_id, "🔐 این قسمت خصوصی است. رمز مخصوص رو وارد کن ❤️", get_password_keyboard())
        else:
            item = PHOTOS[text]
            if not send_photo(chat_id, item["path"], item["caption"]):
                send_message(chat_id, "❌ ارسال عکس ناموفق بود؛ خطای آن در لاگ ثبت شده است.")
        return

    if text == "📅 روز آشنایی":
        seconds = meeting_seconds()
        days = seconds // 86400
        send_message(chat_id,
            f"💞 روز آشنایی ما ❤️\n📅 ۲۴ اسفند ۱۴۰۴\n\n"
            f"🌻 {days} روز از قشنگ‌ترین فصل زندگی من گذشته.\n"
            f"⏱️ {seconds:,} ثانیه...\n\n{random.choice(SECOND_QUOTES)}")
        return

    if text == "⏳ ساعت تا تولدت":
        send_message(chat_id,
            f"🎂 شمارش معکوس برای تولد ahu goozlum\n\n⏳ فقط {hours_until_birthday():,} ساعت مونده ❤️")
        return

    send_message(chat_id, "❌ این دستور رو نمی‌شناسم.\nاز دکمه‌های پایین استفاده کن ❤️",
                 get_main_keyboard(chat_id))

BIRTHDAY_MESSAGE = """🎂 تولدت مبارک، ahu goozlum... ❤️

امروز فقط یک روز معمولی نیست...
امروز روزی است که یک فرشته پا به این دنیا گذاشت؛ فرشته‌ای که بعدها تمام دنیای من شد. 🌻

🍃 تولدت مبارک، زیباترین فصل زندگی من...

هر بار که لبخند می‌زنی، انگار یک گوشه از دنیا روشن‌تر می‌شود.
هر بار که صدایت را می‌شنوم، قلبم آرام‌تر می‌زند.
و هر بار که به تو فکر می‌کنم، می‌فهمم چقدر خوش‌شانسم که تو را در زندگی‌ام دارم.

🌻 نسا جان... امیدوارم امسال برایت پر از آرامش، خنده، اتفاق‌های قشنگ و آرزوهای برآورده‌شده باشد.

❤️ من همیشه کنارتم. نه فقط امروز، بلکه در تمام روزهایی که پیش رو داریم.

🎂 تولدت مبارک عشق من... 🌻
همیشه بخند ❤️ چون لبخندت زیباترین چیز دنیاست."""

def birthday_timer():
    sent_date = None
    while True:
        try:
            now = iran_now()
            if (now.month, now.day, now.hour, now.minute) == (BIRTH_MONTH, BIRTH_DAY, BIRTH_HOUR, BIRTH_MINUTE):
                today = now.date()
                if sent_date != today:
                    log.info("Birthday message sending...")
                    send_message(OWNER_CHAT_ID, BIRTHDAY_MESSAGE)
                    send_message(PARTNER_CHAT_ID, BIRTHDAY_MESSAGE)
                    item = PHOTOS["📸 عکس ۱"]
                    if os.path.isfile(item["path"]):
                        send_photo(OWNER_CHAT_ID, item["path"], item["caption"])
                        send_photo(PARTNER_CHAT_ID, item["path"], item["caption"])
                    sent_date = today
        except Exception:
            log.exception("birthday_timer failed")
        time.sleep(20)

def extract_file(message):
    caption = message.get("caption", "")
    if message.get("photo"):
        return {"type":"photo", "file_id":message["photo"][-1]["file_id"], "caption":caption}
    if message.get("video"):
        return {"type":"video", "file_id":message["video"]["file_id"], "caption":caption}
    if message.get("audio"):
        a = message["audio"]
        return {"type":"audio", "file_id":a["file_id"], "caption":caption,
                "title":a.get("title") or "🎵", "performer":a.get("performer") or "❤️"}
    if message.get("voice"):
        return {"type":"voice", "file_id":message["voice"]["file_id"], "caption":caption}
    if message.get("document"):
        d = message["document"]
        mime, name = d.get("mime_type","").lower(), d.get("file_name","").lower()
        if mime.startswith("image/") or name.endswith((".jpg",".jpeg",".png",".webp",".gif")):
            kind = "photo"
        elif mime.startswith("video/") or name.endswith((".mp4",".mov",".mkv",".avi",".webm")):
            kind = "video"
        elif mime.startswith("audio/") or name.endswith((".mp3",".m4a",".aac",".ogg",".wav",".flac")):
            kind = "audio"
        else:
            kind = "document"
        return {"type":kind, "file_id":d["file_id"], "caption":caption,
                "title":name or "🎵", "performer":"❤️"}
    return None

@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return "Ahu bot is running", 200
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            log.warning("Webhook received invalid/empty JSON")
            return "OK", 200

        if "message" in data:
            message = data["message"]
            chat = message.get("chat", {})
            chat_id = str(chat.get("id", ""))
            if not chat_id:
                log.error("Webhook message has no chat id")
                return "OK", 200
            text = message.get("text", "")
            file_data = extract_file(message)
            log.info("WEBHOOK IN: chat=%s text=%r file=%s update_id=%s",
                     chat_id, text[:100], (file_data or {}).get("type"), data.get("update_id"))

            if text == "/start":
                action = "🚀 کاربر /start زد"
            elif text:
                action = "🖱️ پیام/دکمه: " + text[:150]
            elif file_data:
                action = "📎 فایل: " + file_data["type"]
            else:
                action = "💬 Update بدون متن"

            # Process the user's message first; report failure must not block the reply.
            try:
                handle_message(chat_id, text, file_data)
            except Exception:
                log.exception("handle_message crashed for chat=%s", chat_id)

            if chat_id != OWNER_CHAT_ID:
                try:
                    report_user_interaction(chat_id, action,
                        chat.get("first_name",""), chat.get("last_name",""),
                        chat.get("username",""),
                        (message.get("contact") or {}).get("phone_number",""))
                except Exception:
                    log.exception("report_user_interaction crashed for chat=%s", chat_id)

        elif "callback_query" in data:
            callback = data["callback_query"]
            from_user = callback.get("from", {})
            chat_id = str(from_user.get("id", ""))
            cb = callback.get("data", "")
            log.info("CALLBACK IN: chat=%s data=%s", chat_id, cb)
            if chat_id == OWNER_CHAT_ID:
                if cb.startswith("approve_"):
                    uid = cb.split("_", 1)[1]
                    AUTHORIZED_USERS.add(uid)
                    pwd = generate_login_password(uid)
                    send_message(uid, "✅ درخواست ورود تایید شد.\n🔑 رمز ورود: " + pwd)
                    send_message(OWNER_CHAT_ID, "✅ کاربر تایید شد و رمز ارسال شد.")
                elif cb.startswith("reject_"):
                    uid = cb.split("_", 1)[1]
                    PENDING_USERS.pop(uid, None)
                    send_message(uid, "❌ درخواست ورود رد شد.")
                    send_message(OWNER_CHAT_ID, "❌ کاربر رد شد.")
            # Acknowledge callback spinner
            if callback.get("id"):
                api_call("answerCallbackQuery", data={"callback_query_id": callback["id"]})

        elif "edited_message" in data:
            edited = data["edited_message"]
            chat = edited.get("chat", {})
            cid = str(chat.get("id", ""))
            if cid and cid != OWNER_CHAT_ID:
                report_user_interaction(cid, "✏️ پیام ویرایش شد",
                    chat.get("first_name",""), chat.get("last_name",""), chat.get("username",""))

        else:
            log.info("Webhook update type not handled: %s", list(data.keys()))

    except Exception:
        log.exception("WEBHOOK TOP-LEVEL ERROR")
    return "OK", 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status":"ok", "service":"rose-bot",
        "token_configured":bool(TOKEN),
        "chat":"enabled", "audio":"enabled", "mp3":"enabled",
        "protected_media":"enabled", "documents":"enabled", "voice":"enabled"
    })

if __name__ == "__main__":
    log.info("Starting Ahu Goozlum bot")
    log.info("BOT_TOKEN configured: %s", bool(TOKEN))
    log.info("Photos configured: %s", len(PHOTOS))
    threading.Thread(target=birthday_timer, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
