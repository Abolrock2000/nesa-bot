from flask import Flask, request, render_template, jsonify
import requests
import json
import random
import datetime
import os
import threading
import time
import mimetypes
from itsdangerous import URLSafeSerializer, BadSignature

app = Flask(__name__)

# ============================================================
# 🔐 تنظیمات ربات
# ============================================================

TOKEN = "8967116754:AAFJlNPRH8Cht-8qKo3zEHCJvSX1JrBGGXQ"

YOUR_CHAT_ID = "1228473012"
PARTNER_CHAT_ID = "7706282234"
TEST_CHAT_ID = "7989818498"

PASSWORD = "1386"

BIRTH_DAY = 8
BIRTH_MONTH = 8
BIRTH_HOUR = 0
BIRTH_MINUTE = 0

IRAN_OFFSET = datetime.timedelta(hours=3, minutes=30)

WEBSITE_URL = "https://nesa-bot.onrender.com"

# ============================================================
# 🗂️ حافظه موقت
# ============================================================

user_access = {}
PARTNER_ACTIVITY = {}
RECONCILE_STATE = {}
PHOTO_VIEWED = {}

# ربات فعال است
BOT_ACTIVE = True

# ============================================================
# 🌹 تنظیمات صفحه گل رز
# ============================================================

ROSE_SECRET = "ROSE_SECRET_KEY_2026"

rose_signer = URLSafeSerializer(
    ROSE_SECRET,
    salt="rose-page"
)

# ============================================================
# 📸 عکس‌ها
# ============================================================

PHOTOS = {
    "📸 عکس ۱": {
        "path": "photos/IMG_20260801_224828_501.jpg",
        "caption": "🌹 عشق زندگیم... ❤️"
    },
    "📸 عکس ۲": {
        "path": "photos/null_14041109_222510829.jpg",
        "caption": "💫 قلب من... تو هستی"
    },
    "📸 عکس ۳": {
        "path": "photos/null_14041125_153021650.jpg",
        "caption": "🌸 بهار زندگی من..."
    },
    "📸 عکس ۴": {
        "path": "photos/IMG_20260707_153249_974.jpg",
        "caption": "🌙 ماه شب‌های من..."
    },
    "📸 عکس ۵": {
        "path": "photos/IMG_20260709_234307_968.jpg",
        "caption": "☀️ روشن‌ترین روز من..."
    },
    "📸 عکس ۶": {
        "path": "photos/IMG_20260719_211523_837.jpg",
        "caption": "❤️ تمام دنیای من..."
    },
    "📸 عکس ۷": {
        "path": "https://i.postimg.cc/5tDhyRgM/IMG-20260318-184739-714.jpg",
        "caption": "💖 عکس مخصوص... ❤️"
    },
    "📸 عکس جدید": {
        "path": "photos/file_00000000f1788210bc5e8d993e16a277.png",
        "caption": "🌹 این عکس مخصوص توست... ❤️"
    }
}

# ============================================================
# 🎀 پیام روز دختر
# ============================================================

GIRLS_DAY_MESSAGE = """🎀 روز دختر مبارک دخترم... 🎀

همه‌ی نبودن‌ها رو جبران میکنم واست... ❤️

✿ ✿ ✿

برای همه چیزت دلم تنگ شده...
نگاهت... لبخندت... بوت... موهات... 🤍

✿ ✿ ✿

مواظب خودت باش خانم محترم... 🥺

روزای سختیه واسم و نمیخوام کنارم شریک این همه سختی باشی...

✿ ✿ ✿

🌹 روزت مبارک... هر جا که هستی... 🌹

❤️
"""

# ============================================================
# 💕 متن‌های آشتی
# ============================================================

RECONCILE_MESSAGES = [
    "چشم آهو میای یا من میام واسه آشتی ... 🌹",
    "🥺 برای بار دوم میپرسم عروس خانوم وکیلم...",
    "💗 برای آخرین بار آتشی میپرسه وکیلم...",
    "عشقم خب تکلیف بچه تو شکمت چی میشه میخوای بدون پدر بزرگ شه😭؟",
    "🥺 چشم آهو جواب بده دیگه... وکیلم یا نه؟",
    "🌹 عروس خانوم، آتشی با دسته‌گل اومده... وکیلم؟",
    "😂 خانوم محترم، پرونده آشتی هنوز بازه... امضا می‌کنی؟",
    "💗 آهو جان یه بله کوچولو بگو، آتشی منتظره...",
    "🥺 خب دیگه قهر بسه عروس خانوم... وکیلم؟",
    "🌹 آتشی هنوز پشت در دادگاه آشتی منتظره 😂",
    "💍 عروس خانوم، جواب این خواستگار پشیمون رو نمی‌دی؟ 😂",
    "❤️ آهو جان، یه بله بگو پرونده صلح رو ببندیم...",
    "😂 قاضی محترم آهو، حکم آشتی رو صادر نمی‌کنی؟",
    "🥺 من اومدم درخواست صلح بدم... فقط یه بله می‌خوام.",
    "💗 آتشی کوتاه نمیاد... آخرش باید بگی وکیلم 😂",
    "🌹 آهو جان، قهرتم قشنگه ولی آشتی‌کردنت قشنگ‌تره...",
    "🥺 عروس خانوم، آتشی هنوز منتظر جواب نهاییه...",
    "❤️ یه آشتی کوچولو، یه بغل کوچولو، بعدش هرچی تو بگی...",
    "😂 خانوم وکیل، موکلت درخواست آشتی داده... قبول می‌کنی؟",
    "🌸 آهو جان، دلم آشتی می‌خواد... وکیلم؟"
]

LOVELY_RESPONSES = [
    "چشم آهو میای یا من میام واسه آشتی ... 🌹",
    "🥺 برای بار دوم میپرسم عروس خانوم وکیلم...",
    "💗 برای آخرین بار آتشی میپرسه وکیلم...",
    "عشقم خب تکلیف بچه تو شکمت چی میشه میخوای بدون پدر بزرگ شه😭؟",
    "🥺 آهو جان هنوز منتظر جوابتم... وکیلم؟",
    "🌹 عروس خانوم، پرونده آشتی هنوز بسته نشده 😂",
    "💗 آتشی هنوز امید داره... یه بله کوچولو؟",
    "😂 خانوم قاضی، حکم آشتی رو صادر نمی‌کنی؟",
    "🥺 قهر بسه دیگه آهو جان... بیا آشتی کنیم.",
    "❤️ یه بله کوچولو بده، آتشی خوشحال شه."
]

WIN_MESSAGES = [
    "❤️❤️❤️ یاااای! آهو گفت بله! 🥰",
    "💖 بالاخره عروس خانوم گفت وکیلم! 😂❤️",
    "🥰 میدونستم آتشی رو تنها نمیذاری! 🌹",
    "💗 آشتی تأیید شد! پرونده با موفقیت بسته شد 😂❤️",
    "🌹 یااای! بهترین جواب دنیا رو دادی... ❤️"
]

# ============================================================
# 🕐 زمان ایران
# ============================================================

def get_current_iran_time():
    utc_now = datetime.datetime.now(
        datetime.timezone.utc
    )

    return utc_now.astimezone(
        datetime.timezone(IRAN_OFFSET)
    )

# ============================================================
# 📊 ثبت فعالیت کاربر
# ============================================================

def log_partner_activity(
    chat_id,
    action="تعامل",
    first_name="",
    last_name="",
    username="",
    phone_number=""
):
    global PARTNER_ACTIVITY

    chat_id = str(chat_id)

    if chat_id == YOUR_CHAT_ID:
        return

    now = get_current_iran_time()

    if chat_id not in PARTNER_ACTIVITY:

        PARTNER_ACTIVITY[chat_id] = {
            "first_seen": now,
            "last_seen": now,
            "count": 0,
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "phone_number": phone_number,
            "last_action": action
        }

    data = PARTNER_ACTIVITY[chat_id]

    if first_name:
        data["first_name"] = first_name

    if last_name:
        data["last_name"] = last_name

    if username:
        data["username"] = username

    if phone_number:
        data["phone_number"] = phone_number

    data["last_seen"] = now
    data["last_action"] = action
    data["count"] += 1

    time_str = now.strftime("%H:%M:%S")
    date_str = now.strftime("%Y/%m/%d")

    weekdays = {
        "Monday": "دوشنبه",
        "Tuesday": "سه‌شنبه",
        "Wednesday": "چهارشنبه",
        "Thursday": "پنج‌شنبه",
        "Friday": "جمعه",
        "Saturday": "شنبه",
        "Sunday": "یک‌شنبه"
    }

    day_persian = weekdays.get(
        now.strftime("%A"),
        now.strftime("%A")
    )

    username_text = (
        "@" + username
        if username
        else "ندارد"
    )

    profile_link = (
        "https://t.me/" + username
        if username
        else "ندارد"
    )

    message = f"""👀 تعامل جدید با ربات

👤 اطلاعات کاربر:

• آیدی عددی: {chat_id}
• نام: {first_name or data.get('first_name') or 'نامشخص'}
• نام خانوادگی: {last_name or data.get('last_name') or 'نامشخص'}
• یوزرنیم: {username_text}
• شماره تلفن: {phone_number or data.get('phone_number') or 'نامشخص'}

📌 نوع تعامل:
{action}

📅 تاریخ: {date_str}
📆 روز: {day_persian}
⏰ ساعت: {time_str}

🔢 تعداد تعامل‌ها:
{data['count']}

🔗 لینک پروفایل:
{profile_link}
"""

    send_message(
        YOUR_CHAT_ID,
        message
    )

# ============================================================
# 👀 گزارش تعامل
# ============================================================

def report_user_interaction(
    chat_id,
    action,
    first_name="",
    last_name="",
    username="",
    phone_number=""
):
    chat_id = str(chat_id)

    if chat_id == YOUR_CHAT_ID:
        return

    log_partner_activity(
        chat_id,
        action,
        first_name,
        last_name,
        username,
        phone_number
    )

# ============================================================
# 💞 روز آشنایی
# ============================================================

SECOND_QUOTES = [
    "هر ثانیه‌ای که می‌گذرد، عشق من به تو عمیق‌تر می‌شود... ❤️",
    "ثانیه‌ها می‌گذرند، اما عشق من به تو هرگز کهنه نمی‌شود... 🌹",
    "در هر ثانیه‌ای از زندگی‌ام، تو را نفس می‌کشم... 💫",
    "ثانیه‌های بی‌تو طولانی‌اند، اما کنار تو حتی ساعت‌ها هم کوتاه‌اند... ✨",
    "هر ثانیه که می‌گذرد، یک دلیل تازه برای دوست داشتن تو پیدا می‌کنم... ❤️",
    "ثانیه‌ها را بشمار، اما عشق را نه؛ چون عشق من به تو بی‌نهایت است... 🌸"
]

MEETING_DATE = datetime.datetime(
    2026,
    3,
    15,
    0,
    0,
    0,
    tzinfo=datetime.timezone(IRAN_OFFSET)
)

def get_meeting_seconds():

    now = get_current_iran_time()

    if now < MEETING_DATE:
        return 0

    return int(
        (now - MEETING_DATE).total_seconds()
    )

# ============================================================
# 🎂 ساعت تا تولد
# ============================================================

def hours_until_birthday():

    now = get_current_iran_time()

    birth = datetime.datetime(
        now.year,
        BIRTH_MONTH,
        BIRTH_DAY,
        BIRTH_HOUR,
        BIRTH_MINUTE,
        tzinfo=datetime.timezone(IRAN_OFFSET)
    )

    if now >= birth:

        birth = datetime.datetime(
            now.year + 1,
            BIRTH_MONTH,
            BIRTH_DAY,
            BIRTH_HOUR,
            BIRTH_MINUTE,
            tzinfo=datetime.timezone(IRAN_OFFSET)
        )

    diff = birth - now

    return int(
        diff.total_seconds() // 3600
    )

# ============================================================
# ⌨️ منوی اصلی
# ============================================================

def get_main_keyboard(chat_id=None):

    keyboard = [
        ["📸 عکس‌ها"],
        ["📅 روز آشنایی", "⏳ ساعت تا تولدت"],
        ["💬 چت دوطرفه"],
        ["🧪 چت تست"]
    ]

    # فقط صاحب ربات
    if str(chat_id) == YOUR_CHAT_ID:

        keyboard.append(
            ["📊 وضعیت پارتنر"]
        )

        keyboard.append(
            ["💔 درخواست آشتی"]
        )

        keyboard.append(
            ["🌹 صفحه آشتی"]
        )

        keyboard.append(
            ["🖼️ ارسال عکس"]
        )

        keyboard.append(
            ["🎀 روز دختر"]
        )

    keyboard.append(
        ["🔙 بازگشت به منو"]
    )

    return {
        "keyboard": keyboard,
        "resize_keyboard": True
    }

# ============================================================
# 🌹 منوی صفحه گل رز
# ============================================================

def get_rose_menu():

    return {
        "keyboard": [
            ["🌹 ارسال صفحه به پارتنر"],
            ["🧪 ارسال صفحه به تست"],
            ["🔙 بازگشت به منو"]
        ],
        "resize_keyboard": True
    }

# ============================================================
# 🎀 منوی روز دختر
# ============================================================

def get_girls_day_menu():

    return {
        "keyboard": [
            ["🎀 ارسال به پارتنر", "🧪 ارسال به تست"],
            ["🔙 بازگشت به منو"]
        ],
        "resize_keyboard": True
    }

# ============================================================
# 📸 منوی عکس
# ============================================================

def get_photo_keyboard():

    return {
        "keyboard": [
            ["📸 عکس ۱", "📸 عکس ۲", "📸 عکس ۳"],
            ["📸 عکس ۴", "📸 عکس ۵", "📸 عکس ۶"],
            ["📸 عکس ۷", "📸 عکس جدید"],
            ["🔙 بازگشت به منو"]
        ],
        "resize_keyboard": True
    }

# ============================================================
# 🔐 منوی رمز
# ============================================================

def get_password_keyboard():

    return {
        "keyboard": [
            ["🔙 بازگشت به منو"]
        ],
        "resize_keyboard": True
    }

# ============================================================
# 💬 منوی چت دوطرفه (برای پارتنر)
# ============================================================

def get_chat_keyboard():

    return {
        "keyboard": [
            ["📤 ارسال پیام"],
            ["📤 ارسال عکس", "📤 ارسال فیلم"],
            ["📤 ارسال موزیک"],
            ["🔙 بازگشت به منو"]
        ],
        "resize_keyboard": True
    }

# ============================================================
# 🧪 منوی چت تست (برای تست)
# ============================================================

def get_test_chat_keyboard():

    return {
        "keyboard": [
            ["📤 ارسال پیام به تست"],
            ["📤 ارسال عکس به تست", "📤 ارسال فیلم به تست"],
            ["📤 ارسال موزیک به تست"],
            ["🔙 بازگشت به منو"]
        ],
        "resize_keyboard": True
    }

# ============================================================
# 💔 منوی آشتی
# ============================================================

def get_reconcile_keyboard():

    return {
        "keyboard": [
            ["❤️ بله، دوست دارم ❤️"],
            ["💔 نه، نمیتونم 😢"]
        ],
        "resize_keyboard": True
    }

# ============================================================
# 💔 انتخاب مخاطب آشتی
# ============================================================

def get_reconcile_target_menu():

    return {
        "keyboard": [
            ["❤️ ارسال به پارتنر", "🧪 ارسال به تست"],
            ["🔙 بازگشت به منو"]
        ],
        "resize_keyboard": True
    }

# ============================================================
# 🖼️ منوی ارسال عکس
# ============================================================

def get_photo_send_menu():

    return {
        "keyboard": [
            ["📤 ارسال عکس به پارتنر", "🧪 ارسال عکس به تست"],
            ["🔙 بازگشت به منو"]
        ],
        "resize_keyboard": True
    }

# ============================================================
# 📤 ارسال پیام
# ============================================================

def send_message(
    chat_id,
    text,
    reply_markup=None
):

    if not TOKEN:

        print(
            "❌ BOT_TOKEN تنظیم نشده است."
        )

        return False

    url = (
        f"https://api.telegram.org/"
        f"bot{TOKEN}/sendMessage"
    )

    try:

        payload = {
            "chat_id": chat_id,
            "text": text
        }

        if reply_markup:

            payload["reply_markup"] = json.dumps(
                reply_markup,
                ensure_ascii=False
            )

        response = requests.post(
            url,
            data=payload,
            timeout=15
        )

        if response.status_code == 200:
            return True

        print(
            "Telegram error:",
            response.status_code,
            response.text
        )

    except Exception as e:

        print(
            "send_message error:",
            e
        )

    return False

# ============================================================
# 📸 ارسال عکس (با فایل ID یا لینک)
# ============================================================

def send_photo(
    chat_id,
    photo_data,
    caption=""
):

    if not TOKEN:

        print(
            "❌ BOT_TOKEN تنظیم نشده است."
        )

        return False

    try:

        url = (
            f"https://api.telegram.org/"
            f"bot{TOKEN}/sendPhoto"
        )

        # اگر لینک اینترنتی است
        if isinstance(photo_data, str) and photo_data.startswith("http"):
            payload = {
                "chat_id": chat_id,
                "photo": photo_data,
                "caption": caption
            }
            response = requests.post(url, data=payload, timeout=30)
            return response.status_code == 200

        # اگر فایل ID از تلگرام است (با getFile گرفته شده)
        if isinstance(photo_data, str) and photo_data.startswith("file_id:"):
            file_id = photo_data.replace("file_id:", "")
            payload = {
                "chat_id": chat_id,
                "photo": file_id,
                "caption": caption
            }
            response = requests.post(url, data=payload, timeout=30)
            return response.status_code == 200

        # اگر مسیر فایل محلی است
        if isinstance(photo_data, str) and os.path.exists(photo_data):
            with open(photo_data, "rb") as photo:
                files = {"photo": photo}
                data = {"chat_id": chat_id, "caption": caption}
                response = requests.post(url, data=data, files=files, timeout=30)
            return response.status_code == 200

        # اگر file_id مستقیم است
        payload = {
            "chat_id": chat_id,
            "photo": photo_data,
            "caption": caption
        }
        response = requests.post(url, data=payload, timeout=30)
        return response.status_code == 200

    except Exception as e:

        print(
            "send_photo error:",
            e
        )

        return False

# ============================================================
# 🎥 ارسال فیلم (با فایل ID یا لینک)
# ============================================================

def send_video(
    chat_id,
    video_data,
    caption=""
):

    if not TOKEN:

        print(
            "❌ BOT_TOKEN تنظیم نشده است."
        )

        return False

    try:

        url = (
            f"https://api.telegram.org/"
            f"bot{TOKEN}/sendVideo"
        )

        # اگر لینک اینترنتی است
        if isinstance(video_data, str) and video_data.startswith("http"):
            payload = {
                "chat_id": chat_id,
                "video": video_data,
                "caption": caption
            }
            response = requests.post(url, data=payload, timeout=60)
            return response.status_code == 200

        # اگر فایل ID از تلگرام است
        if isinstance(video_data, str) and video_data.startswith("file_id:"):
            file_id = video_data.replace("file_id:", "")
            payload = {
                "chat_id": chat_id,
                "video": file_id,
                "caption": caption
            }
            response = requests.post(url, data=payload, timeout=60)
            return response.status_code == 200

        # اگر مسیر فایل محلی است
        if isinstance(video_data, str) and os.path.exists(video_data):
            with open(video_data, "rb") as video:
                files = {"video": video}
                data = {"chat_id": chat_id, "caption": caption}
                response = requests.post(url, data=data, files=files, timeout=60)
            return response.status_code == 200

        # اگر file_id مستقیم است
        payload = {
            "chat_id": chat_id,
            "video": video_data,
            "caption": caption
        }
        response = requests.post(url, data=payload, timeout=60)
        return response.status_code == 200

    except Exception as e:

        print(
            "send_video error:",
            e
        )

        return False

# ============================================================
# 🎵 ارسال موزیک (با فایل ID یا لینک)
# ============================================================

def send_audio(
    chat_id,
    audio_data,
    caption="",
    title="",
    performer=""
):

    if not TOKEN:

        print(
            "❌ BOT_TOKEN تنظیم نشده است."
        )

        return False

    try:

        url = (
            f"https://api.telegram.org/"
            f"bot{TOKEN}/sendAudio"
        )

        # اگر لینک اینترنتی است
        if isinstance(audio_data, str) and audio_data.startswith("http"):
            payload = {
                "chat_id": chat_id,
                "audio": audio_data,
                "caption": caption
            }
            if title:
                payload["title"] = title
            if performer:
                payload["performer"] = performer
            response = requests.post(url, data=payload, timeout=60)
            return response.status_code == 200

        # اگر فایل ID از تلگرام است
        if isinstance(audio_data, str) and audio_data.startswith("file_id:"):
            file_id = audio_data.replace("file_id:", "")
            payload = {
                "chat_id": chat_id,
                "audio": file_id,
                "caption": caption
            }
            if title:
                payload["title"] = title
            if performer:
                payload["performer"] = performer
            response = requests.post(url, data=payload, timeout=60)
            return response.status_code == 200

        # اگر مسیر فایل محلی است
        if isinstance(audio_data, str) and os.path.exists(audio_data):
            with open(audio_data, "rb") as audio:
                files = {"audio": audio}
                data = {"chat_id": chat_id, "caption": caption}
                if title:
                    data["title"] = title
                if performer:
                    data["performer"] = performer
                response = requests.post(url, data=data, files=files, timeout=60)
            return response.status_code == 200

        # اگر file_id مستقیم است
        payload = {
            "chat_id": chat_id,
            "audio": audio_data,
            "caption": caption
        }
        if title:
            payload["title"] = title
        if performer:
            payload["performer"] = performer
        response = requests.post(url, data=payload, timeout=60)
        return response.status_code == 200

    except Exception as e:

        print(
            "send_audio error:",
            e
        )

        return False

# ============================================================
# 🖼️ ارسال عکس با Tracking
# ============================================================

def send_photo_with_tracking(
    chat_id,
    photo_data,
    caption="",
    target_name="کاربر"
):

    photo_id = (
        f"PHOTO_"
        f"{int(time.time())}_"
        f"{random.randint(1000, 9999)}"
    )

    full_caption = (
        f"{caption}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 {photo_id}"
    )

    success = send_photo(
        chat_id,
        photo_data,
        full_caption
    )

    if success:

        PHOTO_VIEWED[str(chat_id)] = {
            "photo_id": photo_id,
            "sent_at": get_current_iran_time(),
            "viewed": False,
            "viewed_at": None,
            "target_name": target_name
        }

        send_message(
            YOUR_CHAT_ID,
            f"""📸 عکس ارسال شد!

👤 گیرنده: {target_name}
🆔 شناسه عکس: {photo_id}
⏰ ساعت: {get_current_iran_time().strftime('%H:%M:%S')}"""
        )

        return True

    return False

# ============================================================
# 👀 بررسی تعامل عکس
# ============================================================

def check_photo_viewed(chat_id):

    chat_id = str(chat_id)

    if chat_id in PHOTO_VIEWED:

        return PHOTO_VIEWED[
            chat_id
        ]["viewed"]

    return False

# ============================================================
# 🖼️ ارسال عکس مخصوص
# ============================================================

def send_photo_from_path(
    chat_id,
    target_name="کاربر"
):

    photo_path = (
        "photos/"
        "file_00000000f1788210bc5e8d993e16a277.png"
    )

    caption = "📸 درستش اینه ❤️"

    success = send_photo_with_tracking(
        chat_id,
        photo_path,
        caption,
        target_name
    )

    if success:

        def check_viewed():

            time.sleep(30)

            if check_photo_viewed(chat_id):

                send_message(
                    YOUR_CHAT_ID,
                    f"""👀 {target_name} بعد از ارسال عکس با ربات تعامل کرد! 🥰

⏰ {get_current_iran_time().strftime('%H:%M:%S')}"""
                )

            else:

                send_message(
                    YOUR_CHAT_ID,
                    f"""⏳ {target_name} هنوز هیچ تعامل جدیدی با ربات نداشته.

⏰ {get_current_iran_time().strftime('%H:%M:%S')}"""
                )

        threading.Thread(
            target=check_viewed,
            daemon=True
        ).start()

        return True

    send_message(
        chat_id,
        "❌ متاسفم! عکس پیدا نشد! 😢"
    )

    return False

# ============================================================
# 💔 سیستم آشتی قبلی
# ============================================================

def send_reconcile_survey(
    chat_id,
    attempt=0,
    target_name="کاربر"
):

    if attempt >= len(RECONCILE_MESSAGES):

        final_message = """💔 باشه عروس خانوم... آشتی رو فعلاً می‌ذاریم برای یه وقت دیگه 😌

🌹 هر وقت خواستی، آتشی اینجاست."""

        send_message(
            chat_id,
            final_message,
            get_main_keyboard(chat_id)
        )

        RECONCILE_STATE[
            str(chat_id)
        ] = {
            "status": "ended",
            "attempt": attempt
        }

        send_message(
            YOUR_CHAT_ID,
            f"💔 {target_name} فعلاً درخواست آشتی رو ادامه نداد."
        )

        return

    extra_messages = [
        "منتظر عشقت هستم... 🌹",
        "آتشی منتظر جوابه... 🥺",
        "عروس خانوم تصمیم بگیر دیگه 😂",
        "آهو جان وکیلم؟ ❤️",
        "یه بله کوچولو بده... 💗"
    ]

    extra = random.choice(
        extra_messages
    )

    message = (
        f"💔 {RECONCILE_MESSAGES[attempt]}\n\n"
        f"🌹 {extra}"
    )

    send_message(
        chat_id,
        message,
        get_reconcile_keyboard()
    )

    RECONCILE_STATE[
        str(chat_id)
    ] = {
        "status": "waiting",
        "attempt": attempt,
        "target_name": target_name
    }

# ============================================================
# 💔 پاسخ آشتی
# ============================================================

def handle_reconcile_response(
    chat_id,
    response
):

    chat_id = str(chat_id)

    state = RECONCILE_STATE.get(
        chat_id,
        {}
    )

    if state.get("status") != "waiting":
        return

    attempt = state.get(
        "attempt",
        0
    )

    target_name = state.get(
        "target_name",
        "کاربر"
    )

    if response == "❤️ بله، دوست دارم ❤️":

        send_message(
            chat_id,
            random.choice(
                WIN_MESSAGES
            )
        )

        send_message(
            chat_id,
            random.choice([
                "💕 آشتی ثبت شد عروس خانوم 😂❤️",
                "🌹 وکیلم تأیید شد! 😂",
                "💖 بالاخره آهو راضی شد 🥰",
                "🌸 پرونده آشتی بسته شد ❤️",
                "🥰 آتشی خوشحال شد!"
            ]),
            get_main_keyboard(chat_id)
        )

        send_message(
            YOUR_CHAT_ID,
            f"""🎉 {target_name} گفت بله! ❤️

🆔 {chat_id}

🥰 درخواست آشتی قبول شد!"""
        )

        RECONCILE_STATE[
            chat_id
        ] = {
            "status": "accepted",
            "attempt": attempt
        }

        return

    if response == "💔 نه، نمیتونم 😢":

        send_message(
            chat_id,
            random.choice(
                LOVELY_RESPONSES
            )
        )

        send_message(
            YOUR_CHAT_ID,
            f"""💔 {target_name} فعلاً گفت نه.

🆔 {chat_id}
🔢 تلاش: {attempt + 1}"""
        )

        send_reconcile_survey(
            chat_id,
            attempt + 1,
            target_name
        )

# ============================================================
# 🌹 ساخت لینک صفحه رز
# ============================================================

def create_rose_link(target_chat_id):

    token = rose_signer.dumps({
        "target": str(target_chat_id)
    })

    return (
        f"{WEBSITE_URL}/rose/{token}"
    )

# ============================================================
# 🌹 ارسال صفحه رز به پارتنر
# ============================================================

def send_rose_page_to_partner(
    owner_chat_id
):

    link = create_rose_link(
        PARTNER_CHAT_ID
    )

    message = """🌹 یه چیز کوچیک برات آماده کردم...

لازم نیست عجله کنی.
هر وقت خودت آمادگی داشتی بازش کن ❤️"""

    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "🌹 باز کردن صفحه",
                    "url": link
                }
            ]
        ]
    }

    success = send_message(
        PARTNER_CHAT_ID,
        message,
        keyboard
    )

    if success:

        send_message(
            owner_chat_id,
            "✅ صفحه گل رز برای پارتنر ارسال شد. 🌹"
        )

    else:

        send_message(
            owner_chat_id,
            "❌ ارسال صفحه گل رز ناموفق بود."
        )

# ============================================================
# 🧪 ارسال صفحه رز به تست
# ============================================================

def send_rose_page_to_test(
    owner_chat_id
):

    link = create_rose_link(
        TEST_CHAT_ID
    )

    message = """🧪 صفحه تست گل رز آماده است.

برای مشاهده صفحه روی دکمه زیر بزن. 🌹"""

    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "🌹 باز کردن صفحه تست",
                    "url": link
                }
            ]
        ]
    }

    success = send_message(
        TEST_CHAT_ID,
        message,
        keyboard
    )

    if success:

        send_message(
            owner_chat_id,
            "🧪 صفحه گل رز برای اکانت تست ارسال شد."
        )

    else:

        send_message(
            owner_chat_id,
            "❌ ارسال صفحه تست ناموفق بود."
        )

# ============================================================
# 📥 دریافت فایل از تلگرام
# ============================================================

def get_file_path(file_id):
    """دریافت مسیر فایل از تلگرام"""
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getFile"
        response = requests.post(url, json={"file_id": file_id}, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                file_path = data["result"]["file_path"]
                return f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
        return None
    except Exception as e:
        print("get_file_path error:", e)
        return None

# ============================================================
# 🤖 پردازش پیام
# ============================================================

def handle_message(
    chat_id,
    text,
    file_data=None
):

    chat_id = str(chat_id)

    text = (
        text or ""
    ).strip()

    # ========================================================
    # 🚫 اگر ربات غیرفعال است (به جز مالک)
    # ========================================================

    if not BOT_ACTIVE and chat_id != YOUR_CHAT_ID:
        send_message(
            chat_id,
            "🔒 ربات غیرفعال شده است."
        )
        return

    user_access.setdefault(
        chat_id,
        {
            "photos": False,
            "waiting_for_password": False,
            "waiting_for_reconcile": False,
            "waiting_for_chat_message": False,
            "waiting_for_file": False,
            "mode": None
        }
    )

    user = user_access[
        chat_id
    ]

    # ========================================================
    # 🧪 چت تست - فقط برای شما
    # ========================================================

    if text == "🧪 چت تست":
        if chat_id == YOUR_CHAT_ID:
            user["mode"] = "test_chat"
            user["waiting_for_chat_message"] = False
            send_message(
                chat_id,
                "🧪 چت تست با اکانت تست باز شد!\n\nاز دکمه‌های زیر برای ارسال استفاده کن.",
                get_test_chat_keyboard()
            )
            return
        else:
            send_message(
                chat_id,
                "❌ این بخش فقط برای صاحب ربات است.",
                get_main_keyboard(chat_id)
            )
            return

    # ========================================================
    # 📤 ارسال پیام به تست
    # ========================================================

    if text == "📤 ارسال پیام به تست":
        if chat_id == YOUR_CHAT_ID and user.get("mode") == "test_chat":
            user["waiting_for_chat_message"] = True
            user["chat_target"] = "test"
            send_message(
                chat_id,
                "💬 پیامت رو برای تست بنویس:",
                get_test_chat_keyboard()
            )
        return

    # ========================================================
    # 📤 ارسال عکس به تست
    # ========================================================

    if text == "📤 ارسال عکس به تست":
        if chat_id == YOUR_CHAT_ID and user.get("mode") == "test_chat":
            user["waiting_for_file"] = "photo"
            user["chat_target"] = "test"
            send_message(
                chat_id,
                "📸 عکس رو بفرست (با دکمه پیوست یا لینک):",
                get_test_chat_keyboard()
            )
        return

    # ========================================================
    # 📤 ارسال فیلم به تست
    # ========================================================

    if text == "📤 ارسال فیلم به تست":
        if chat_id == YOUR_CHAT_ID and user.get("mode") == "test_chat":
            user["waiting_for_file"] = "video"
            user["chat_target"] = "test"
            send_message(
                chat_id,
                "🎥 فیلم رو بفرست (با دکمه پیوست یا لینک):",
                get_test_chat_keyboard()
            )
        return

    # ========================================================
    # 📤 ارسال موزیک به تست
    # ========================================================

    if text == "📤 ارسال موزیک به تست":
        if chat_id == YOUR_CHAT_ID and user.get("mode") == "test_chat":
            user["waiting_for_file"] = "audio"
            user["chat_target"] = "test"
            send_message(
                chat_id,
                "🎵 فایل صوتی/موزیک رو بفرست (با دکمه پیوست یا لینک):",
                get_test_chat_keyboard()
            )
        return

    # ========================================================
    # 🔙 بازگشت
    # ========================================================

    if text == "🔙 بازگشت به منو":

        photos_access = user.get(
            "photos",
            False
        )

        user_access[chat_id] = {
            "photos": photos_access,
            "waiting_for_password": False,
            "waiting_for_reconcile": False,
            "waiting_for_chat_message": False,
            "waiting_for_file": False,
            "mode": None,
            "chat_target": None
        }

        send_message(
            chat_id,
            "🏠 برگشتیم به منوی اصلی...\n\n🌻 هر چیزی که بخوای اینجاست ❤️",
            get_main_keyboard(chat_id)
        )

        return

    # ========================================================
    # /start
    # ========================================================

    if text == "/start":

        user_access[chat_id] = {
            "photos": False,
            "waiting_for_password": False,
            "waiting_for_reconcile": False,
            "waiting_for_chat_message": False,
            "waiting_for_file": False,
            "mode": None,
            "chat_target": None
        }

        send_message(
            chat_id,
            """🌻❤️ به دنیای ahu goozlum خوش اومدی ❤️🌻

🎁 اینجا یک گوشه کوچیک از قلب منه...

📸 عکس‌های خصوصی
📅 روز آشنایی
⏳ شمارش معکوس تولد
💬 چت دوطرفه
🧪 چت تست

🌻 هر دکمه یک تکه از داستان ماست...""",
            get_main_keyboard(chat_id)
        )

        return

    # ========================================================
    # 💬 چت دوطرفه (پارتنر)
    # ========================================================

    if text == "💬 چت دوطرفه":

        if chat_id != YOUR_CHAT_ID and chat_id != TEST_CHAT_ID:
            send_message(
                chat_id,
                "❌ این بخش فقط برای پارتنر است."
            )
            return

        user["mode"] = "partner_chat"
        user["waiting_for_chat_message"] = False
        send_message(
            chat_id,
            "💬 چت دوطرفه با عشقت باز شد!\n\nاز دکمه‌های زیر برای ارسال استفاده کن.",
            get_chat_keyboard()
        )
        return

    # ========================================================
    # 📤 ارسال پیام (پارتنر)
    # ========================================================

    if text == "📤 ارسال پیام":
        if user.get("mode") == "partner_chat":
            user["waiting_for_chat_message"] = True
            user["chat_target"] = "partner"
            send_message(
                chat_id,
                "💬 پیامت رو برای عشقت بنویس:",
                get_chat_keyboard()
            )
        return

    # ========================================================
    # 📤 ارسال عکس (پارتنر)
    # ========================================================

    if text == "📤 ارسال عکس":
        if user.get("mode") == "partner_chat":
            user["waiting_for_file"] = "photo"
            user["chat_target"] = "partner"
            send_message(
                chat_id,
                "📸 عکس رو بفرست (با دکمه پیوست یا لینک):",
                get_chat_keyboard()
            )
        return

    # ========================================================
    # 📤 ارسال فیلم (پارتنر)
    # ========================================================

    if text == "📤 ارسال فیلم":
        if user.get("mode") == "partner_chat":
            user["waiting_for_file"] = "video"
            user["chat_target"] = "partner"
            send_message(
                chat_id,
                "🎥 فیلم رو بفرست (با دکمه پیوست یا لینک):",
                get_chat_keyboard()
            )
        return

    # ========================================================
    # 📤 ارسال موزیک (پارتنر)
    # ========================================================

    if text == "📤 ارسال موزیک":
        if user.get("mode") == "partner_chat":
            user["waiting_for_file"] = "audio"
            user["chat_target"] = "partner"
            send_message(
                chat_id,
                "🎵 فایل صوتی/موزیک رو بفرست (با دکمه پیوست یا لینک):",
                get_chat_keyboard()
            )
        return

    # ========================================================
    # 📥 پردازش فایل‌ها (عکس، فیلم، موزیک)
    # ========================================================

    if file_data:
        file_type = file_data.get("type")
        file_id = file_data.get("file_id")
        file_path = file_data.get("path")
        target = user.get("chat_target", "partner")
        file_caption = file_data.get("caption", "")

        if target == "partner":
            target_id = PARTNER_CHAT_ID if chat_id != PARTNER_CHAT_ID else YOUR_CHAT_ID
        elif target == "test":
            target_id = TEST_CHAT_ID if chat_id != TEST_CHAT_ID else YOUR_CHAT_ID
        else:
            target_id = PARTNER_CHAT_ID

        # اگر file_path وجود ندارد و file_id داریم، مسیر رو بگیر
        if not file_path and file_id:
            file_path = get_file_path(file_id)

        # ارسال فایل به مقصد
        if file_type == "photo":
            # اگر لینک مستقیم داریم استفاده کن، وگرنه از file_id
            if file_path:
                success = send_photo(target_id, file_path, file_caption)
            else:
                success = send_photo(target_id, f"file_id:{file_id}", file_caption)
            
            if success:
                send_message(chat_id, "✅ عکس ارسال شد! 📸", get_chat_keyboard() if user.get("mode") == "partner_chat" else get_test_chat_keyboard())
            else:
                send_message(chat_id, "❌ ارسال عکس ناموفق بود!", get_chat_keyboard() if user.get("mode") == "partner_chat" else get_test_chat_keyboard())

        elif file_type == "video":
            if file_path:
                success = send_video(target_id, file_path, file_caption)
            else:
                success = send_video(target_id, f"file_id:{file_id}", file_caption)
            
            if success:
                send_message(chat_id, "✅ فیلم ارسال شد! 🎥", get_chat_keyboard() if user.get("mode") == "partner_chat" else get_test_chat_keyboard())
            else:
                send_message(chat_id, "❌ ارسال فیلم ناموفق بود!", get_chat_keyboard() if user.get("mode") == "partner_chat" else get_test_chat_keyboard())

        elif file_type == "audio":
            title = file_data.get("title", "🎵")
            performer = file_data.get("performer", "❤️")
            
            if file_path:
                success = send_audio(target_id, file_path, file_caption, title, performer)
            else:
                success = send_audio(target_id, f"file_id:{file_id}", file_caption, title, performer)
            
            if success:
                send_message(chat_id, "✅ موزیک ارسال شد! 🎵", get_chat_keyboard() if user.get("mode") == "partner_chat" else get_test_chat_keyboard())
            else:
                send_message(chat_id, "❌ ارسال موزیک ناموفق بود!", get_chat_keyboard() if user.get("mode") == "partner_chat" else get_test_chat_keyboard())

        user["waiting_for_file"] = False
        return

    # ========================================================
    # 💬 ارسال پیام متنی
    # ========================================================

    if user.get("waiting_for_chat_message", False):
        target = user.get("chat_target", "partner")

        if target == "partner":
            target_id = PARTNER_CHAT_ID if chat_id != PARTNER_CHAT_ID else YOUR_CHAT_ID
            sender_name = "عشقت" if chat_id != PARTNER_CHAT_ID else "پارتنرت"
        elif target == "test":
            target_id = TEST_CHAT_ID if chat_id != TEST_CHAT_ID else YOUR_CHAT_ID
            sender_name = "تست" if chat_id != TEST_CHAT_ID else "مالک"
        else:
            target_id = PARTNER_CHAT_ID
            sender_name = "کاربر"

        if text:
            send_message(
                target_id,
                f"💬 پیام از {sender_name}:\n\n{text}"
            )
            send_message(
                chat_id,
                "✅ پیام ارسال شد! ❤️",
                get_chat_keyboard() if user.get("mode") == "partner_chat" else get_test_chat_keyboard()
            )

        user["waiting_for_chat_message"] = False
        return

    # ========================================================
    # 🌹 صفحه گل رز
    # ========================================================

    if text == "🌹 صفحه آشتی":

        if chat_id == YOUR_CHAT_ID:

            user["mode"] = "rose"

            send_message(
                chat_id,
                "🌹 صفحه گل رز رو برای چه کسی بفرستم؟",
                get_rose_menu()
            )

        else:

            send_message(
                chat_id,
                "❌ این بخش فقط برای صاحب ربات است.",
                get_main_keyboard(chat_id)
            )

        return

    # ========================================================
    # 🌹 ارسال رز به پارتنر
    # ========================================================

    if (
        text == "🌹 ارسال صفحه به پارتنر"
        and
        user.get("mode") == "rose"
    ):

        if chat_id == YOUR_CHAT_ID:

            send_rose_page_to_partner(
                chat_id
            )

            user["mode"] = None

            send_message(
                chat_id,
                "🏠 برگشتیم به منوی اصلی.",
                get_main_keyboard(chat_id)
            )

        return

    # ========================================================
    # 🧪 ارسال رز به تست
    # ========================================================

    if (
        text == "🧪 ارسال صفحه به تست"
        and
        user.get("mode") == "rose"
    ):

        if chat_id == YOUR_CHAT_ID:

            send_rose_page_to_test(
                chat_id
            )

            user["mode"] = None

            send_message(
                chat_id,
                "🏠 برگشتیم به منوی اصلی.",
                get_main_keyboard(chat_id)
            )

        return

    # ========================================================
    # 🎀 روز دختر
    # ========================================================

    if text == "🎀 روز دختر":

        if chat_id == YOUR_CHAT_ID:

            user["mode"] = "girls_day"

            send_message(
                chat_id,
                "🎀 پیام روز دختر رو به چه کسی می‌خوای ارسال کنی؟",
                get_girls_day_menu()
            )

        else:

            send_message(
                chat_id,
                "❌ این بخش فقط برای صاحب ربات است."
            )

        return

    # ========================================================
    # 🎀 ارسال روز دختر به پارتنر
    # ========================================================

    if (
        text == "🎀 ارسال به پارتنر"
        and
        user.get("mode") == "girls_day"
    ):

        if chat_id == YOUR_CHAT_ID:

            send_message(
                chat_id,
                "🎀 در حال ارسال پیام روز دختر..."
            )

            success = send_message(
                PARTNER_CHAT_ID,
                GIRLS_DAY_MESSAGE
            )

            if success:

                send_message(
                    chat_id,
                    "✅ پیام روز دختر به پارتنر ارسال شد! 🎀",
                    get_main_keyboard(chat_id)
                )

            else:

                send_message(
                    chat_id,
                    "❌ ارسال پیام روز دختر ناموفق بود."
                )

            user["mode"] = None

        return

    # ========================================================
    # 🧪 ارسال روز دختر به تست
    # ========================================================

    if (
        text == "🧪 ارسال به تست"
        and
        user.get("mode") == "girls_day"
    ):

        if chat_id == YOUR_CHAT_ID:

            send_message(
                chat_id,
                "🧪 در حال ارسال پیام روز دختر به تست..."
            )

            success = send_message(
                TEST_CHAT_ID,
                GIRLS_DAY_MESSAGE
            )

            if success:

                send_message(
                    chat_id,
                    "✅ پیام روز دختر به اکانت تست ارسال شد! 🎀",
                    get_main_keyboard(chat_id)
                )

            else:

                send_message(
                    chat_id,
                    "❌ ارسال پیام روز دختر ناموفق بود."
                )

            user["mode"] = None

        return

    # ========================================================
    # 💔 درخواست آشتی
    # ========================================================

    if text == "💔 درخواست آشتی":

        if chat_id == YOUR_CHAT_ID:

            user["mode"] = "reconcile"

            send_message(
                chat_id,
                "💔 به چه کسی می‌خوای درخواست آشتی بدی؟",
                get_reconcile_target_menu()
            )

        else:

            send_message(
                chat_id,
                "❌ این بخش فقط برای صاحب ربات است.",
                get_main_keyboard(chat_id)
            )

        return

    # ========================================================
    # ❤️ ارسال درخواست آشتی به پارتنر
    # ========================================================

    if (
        text == "❤️ ارسال به پارتنر"
        and
        user.get("mode") == "reconcile"
    ):

        if chat_id == YOUR_CHAT_ID:

            send_message(
                chat_id,
                "💔 در حال ارسال درخواست آشتی..."
            )

            state = RECONCILE_STATE.get(
                PARTNER_CHAT_ID,
                {}
            )

            if state.get("status") == "accepted":

                send_message(
                    chat_id,
                    "❤️ پارتنرت قبلاً آشتی رو قبول کرده! 🥰",
                    get_main_keyboard(chat_id)
                )

                user["mode"] = None

                return

            send_reconcile_survey(
                PARTNER_CHAT_ID,
                0,
                "پارتنر"
            )

            send_message(
                chat_id,
                "✅ درخواست آشتی ارسال شد! ❤️",
                get_main_keyboard(chat_id)
            )

            user["mode"] = None

        return

    # ========================================================
    # 🧪 ارسال درخواست آشتی به تست
    # ========================================================

    if (
        text == "🧪 ارسال به تست"
        and
        user.get("mode") == "reconcile"
    ):

        if chat_id == YOUR_CHAT_ID:

            send_message(
                chat_id,
                "🧪 در حال ارسال درخواست آشتی به تست..."
            )

            send_reconcile_survey(
                TEST_CHAT_ID,
                0,
                "تست"
            )

            send_message(
                chat_id,
                "🧪 درخواست آشتی به اکانت تست ارسال شد! ❤️",
                get_main_keyboard(chat_id)
            )

            user["mode"] = None

        return

    # ========================================================
    # 👀 تعامل بعد از ارسال عکس
    # ========================================================

    if chat_id != YOUR_CHAT_ID:

        if (
            chat_id in PHOTO_VIEWED
            and
            not PHOTO_VIEWED[chat_id]["viewed"]
        ):

            PHOTO_VIEWED[
                chat_id
            ]["viewed"] = True

            PHOTO_VIEWED[
                chat_id
            ]["viewed_at"] = get_current_iran_time()

            name = (
                PARTNER_ACTIVITY
                .get(chat_id, {})
                .get("first_name")
                or
                PHOTO_VIEWED[
                    chat_id
                ].get(
                    "target_name",
                    "کاربر"
                )
            )

            send_message(
                YOUR_CHAT_ID,
                f"""👀 {name} بعد از ارسال عکس با ربات تعامل کرد!

⏰ {get_current_iran_time().strftime('%H:%M:%S')}"""
            )

    # ========================================================
    # 💔 پاسخ آشتی
    # ========================================================

    if text in [
        "❤️ بله، دوست دارم ❤️",
        "💔 نه، نمیتونم 😢"
    ]:

        if chat_id != YOUR_CHAT_ID:

            handle_reconcile_response(
                chat_id,
                text
            )

        return

    # ========================================================
    # 🖼️ ارسال عکس
    # ========================================================

    if text == "🖼️ ارسال عکس":

        if chat_id == YOUR_CHAT_ID:

            send_message(
                chat_id,
                "🖼️ عکس رو به چه کسی می‌خوای ارسال کنی؟",
                get_photo_send_menu()
            )

        return

    # ========================================================
    # 📤 عکس به پارتنر
    # ========================================================

    if text == "📤 ارسال عکس به پارتنر":

        if chat_id == YOUR_CHAT_ID:

            send_message(
                chat_id,
                "📤 ارسال عکس به پارتنر..."
            )

            success = send_photo_from_path(
                PARTNER_CHAT_ID,
                "پارتنر"
            )

            if success:

                send_message(
                    chat_id,
                    "✅ عکس با موفقیت ارسال شد! 🌹"
                )

            else:

                send_message(
                    chat_id,
                    "❌ ارسال عکس ناموفق بود."
                )

        return

    # ========================================================
    # 🧪 عکس تست
    # ========================================================

    if text == "🧪 ارسال عکس به تست":

        if chat_id == YOUR_CHAT_ID:

            send_message(
                chat_id,
                "🧪 ارسال عکس به اکانت تست..."
            )

            success = send_photo_from_path(
                TEST_CHAT_ID,
                "تست"
            )

            if success:

                send_message(
                    chat_id,
                    "✅ عکس به تست ارسال شد! 🌹"
                )

            else:

                send_message(
                    chat_id,
                    "❌ ارسال عکس ناموفق بود."
                )

        return

    # ========================================================
    # 📊 وضعیت پارتنر
    # ========================================================

    if text == "📊 وضعیت پارتنر":

        if chat_id != YOUR_CHAT_ID:

            send_message(
                chat_id,
                "❌ دسترسی ندارید."
            )

            return

        if not PARTNER_ACTIVITY:

            send_message(
                chat_id,
                "❌ هنوز هیچ تعاملی ثبت نشده است."
            )

            return

        partner_id = (
            PARTNER_CHAT_ID
            if PARTNER_CHAT_ID in PARTNER_ACTIVITY
            else list(
                PARTNER_ACTIVITY.keys()
            )[0]
        )

        data = PARTNER_ACTIVITY[
            partner_id
        ]

        last_seen = data[
            "last_seen"
        ]

        first_seen = data[
            "first_seen"
        ]

        now = get_current_iran_time()

        diff = (
            now - last_seen
        ).total_seconds()

        status = (
            "🟢 اخیراً فعال بوده"
            if diff < 300
            else
            "🔴 بیش از ۵ دقیقه تعامل نداشته"
        )

        reconcile_status = RECONCILE_STATE.get(
            partner_id,
            {}
        )

        if reconcile_status.get(
            "status"
        ) == "accepted":

            reconcile_text = "❤️ آشتی کرد 🥰"

        elif reconcile_status.get(
            "status"
        ) == "ended":

            reconcile_text = "💔 پایان یافت"

        elif reconcile_status.get(
            "status"
        ) == "waiting":

            reconcile_text = "⏳ منتظر پاسخ"

        else:

            reconcile_text = "❓ درخواستی نشده"

        photo_status = "📸 عکسی ارسال نشده"

        if partner_id in PHOTO_VIEWED:

            if PHOTO_VIEWED[
                partner_id
            ]["viewed"]:

                photo_status = (
                    "👀 بعد از ارسال عکس "
                    "تعامل ثبت شد"
                )

            else:

                photo_status = (
                    "⏳ عکس ارسال شده؛ "
                    "هنوز تعامل جدیدی ثبت نشده"
                )

        username = data.get(
            "username"
        )

        username_text = (
            "@" + username
            if username
            else "ندارد"
        )

        message = f"""📊 وضعیت کاربر

👤 اطلاعات:

• آیدی: {partner_id}
• نام: {data.get('first_name') or 'نامشخص'}
• نام خانوادگی: {data.get('last_name') or 'نامشخص'}
• یوزرنیم: {username_text}
• شماره تلفن: {data.get('phone_number') or 'نامشخص'}

📅 اولین تعامل:
{first_seen.strftime('%Y/%m/%d - %H:%M:%S')}

📅 آخرین تعامل:
{last_seen.strftime('%Y/%m/%d - %H:%M:%S')}

🔢 تعداد تعامل‌ها:
{data['count']}

📌 آخرین اقدام:
{data.get('last_action', 'نامشخص')}

❤️ وضعیت:
{status}

💔 آشتی:
{reconcile_text}

🖼️ وضعیت عکس:
{photo_status}
"""

        send_message(
            chat_id,
            message,
            get_main_keyboard(chat_id)
        )

        return

    # ========================================================
    # 🔐 رمز
    # ========================================================

    if user.get(
        "waiting_for_password",
        False
    ):

        if text == PASSWORD:

            user["photos"] = True

            user[
                "waiting_for_password"
            ] = False

            send_message(
                chat_id,
                "✅ رمز درست بود!\n\n🔓 گالری باز شد ❤️",
                get_photo_keyboard()
            )

        else:

            send_message(
                chat_id,
                "❌ رمز اشتباهه!\n\nدوباره امتحان کن ❤️",
                get_password_keyboard()
            )

        return

    # ========================================================
    # 📸 عکس‌ها
    # ========================================================

    if text in PHOTOS:

        if user.get(
            "photos",
            False
        ):

            photo = PHOTOS[text]

            send_photo(
                chat_id,
                photo["path"],
                photo["caption"]
            )

        else:

            user[
                "waiting_for_password"
            ] = True

            send_message(
                chat_id,
                "🔐 این قسمت خصوصی است.\n\nلطفاً رمز مخصوص رو وارد کن ❤️",
                get_password_keyboard()
            )

        return

    # ========================================================
    # 📸 گالری
    # ========================================================

    if text == "📸 عکس‌ها":

        if user.get(
            "photos",
            False
        ):

            send_message(
                chat_id,
                "📸 کدوم عکس رو می‌خوای ببینی؟ ❤️",
                get_photo_keyboard()
            )

        else:

            user[
                "waiting_for_password"
            ] = True

            send_message(
                chat_id,
                "🔐 برای ورود به گالری\nرمز مخصوص رو وارد کن ❤️",
                get_password_keyboard()
            )

        return

    # ========================================================
    # 📅 روز آشنایی
    # ========================================================

    if text == "📅 روز آشنایی":

        seconds = get_meeting_seconds()

        days = seconds // 86400

        quote = random.choice(
            SECOND_QUOTES
        )

        message = f"""💞 روز آشنایی ما ❤️

📅 ۲۴ اسفند ۱۴۰۴

از روزی که وارد زندگی من شدی،
تا امروز، هر ثانیه برای من
یک خاطره‌ی قشنگه.

🌻 {days} روز از قشنگ‌ترین فصل زندگی من گذشته.

⏱️ {seconds:,} ثانیه...

{seconds:,} ثانیه‌ای که
قلبم برای تو تپیده است. ❤️

📖 {quote}

❤️ از روز آشنایی‌مان تا همیشه...
تو یکی از زیباترین اتفاق‌های زندگی منی."""

        send_message(
            chat_id,
            message
        )

        return

    # ========================================================
    # ⏳ تولد
    # ========================================================

    if text == "⏳ ساعت تا تولدت":

        hours = hours_until_birthday()

        send_message(
            chat_id,
            f"""🎂 شمارش معکوس برای روز قشنگ تو...

🌻 تولد ahu goozlum

⏳ فقط {hours:,} ساعت دیگه مونده...

هر ساعتی که می‌گذره،
من یک قدم به روزی نزدیک‌تر می‌شم
که دنیا قشنگ‌تر شد؛
روزی که تو به دنیا اومدی. ❤️🌻"""
        )

        return

    # ========================================================
    # ❌ دستور ناشناخته
    # ========================================================

    send_message(
        chat_id,
        "❌ این دستور رو نمی‌شناسم.\n\nاز دکمه‌های پایین استفاده کن ❤️",
        get_main_keyboard(chat_id)
    )

# ============================================================
# 🎂 پیام تولد
# ============================================================

BIRTHDAY_MESSAGE = """🎂 تولدت مبارک، ahu goozlum... ❤️

امروز فقط یک روز معمولی نیست...

امروز روزی است که یک فرشته
پا به این دنیا گذاشت؛
فرشته‌ای که بعدها
تمام دنیای من شد. 🌻

🍃 تولدت مبارک، زیباترین فصل زندگی من...

هر بار که لبخند می‌زنی،
انگار یک گوشه از دنیا روشن‌تر می‌شود.

هر بار که صدایت را می‌شنوم،
قلبم آرام‌تر می‌زند.

و هر بار که به تو فکر می‌کنم،
می‌فهمم چقدر خوش‌شانسم
که تو را در زندگی‌ام دارم.

🌻 نسا جان...
امیدوارم امسال برایت
پر از آرامش،
خنده،
اتفاق‌های قشنگ
و آرزوهای برآورده‌شده باشد.

❤️ من همیشه کنارتم.
نه فقط امروز،
بلکه در تمام روزهایی که پیش رو داریم.

🎂 تولدت مبارک عشق من...
🌻 همیشه بخند
❤️ چون لبخندت زیباترین چیز دنیاست."""

# ============================================================
# 🎂 تایمر تولد
# ============================================================

def birthday_timer():

    sent_today = False

    while True:

        try:

            now = get_current_iran_time()

            if (
                now.month == BIRTH_MONTH
                and
                now.day == BIRTH_DAY
                and
                now.hour == BIRTH_HOUR
                and
                now.minute == BIRTH_MINUTE
            ):

                if not sent_today:

                    print(
                        "🎂 ارسال پیام تولد..."
                    )

                    send_message(
                        YOUR_CHAT_ID,
                        BIRTHDAY_MESSAGE
                    )

                    send_message(
                        PARTNER_CHAT_ID,
                        BIRTHDAY_MESSAGE
                    )

                    photo = PHOTOS[
                        "📸 عکس ۱"
                    ]

                    if os.path.exists(
                        photo["path"]
                    ):

                        send_photo(
                            YOUR_CHAT_ID,
                            photo["path"],
                            photo["caption"]
                        )

                        send_photo(
                            PARTNER_CHAT_ID,
                            photo["path"],
                            photo["caption"]
                        )

                    sent_today = True

                    print(
                        "✅ پیام تولد ارسال شد."
                    )

            else:

                sent_today = False

        except Exception as e:

            print(
                "birthday_timer error:",
                e
            )

        time.sleep(30)

# ============================================================
# 🌹 صفحه گل رز (با HTML مستقیم)
# ============================================================

@app.route("/rose/<token>", methods=["GET"])
def rose_page(token):
    try:
        data = rose_signer.loads(token)
        target = str(data.get("target", ""))
        
        if target not in [PARTNER_CHAT_ID, TEST_CHAT_ID]:
            return "Invalid rose link", 403

        # صفحه HTML مستقیم در کد
        html = '''
        <!DOCTYPE html>
        <html lang="fa" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>🌹 برای تو</title>
            <style>
                *{margin:0;padding:0;box-sizing:border-box}
                body{min-height:100vh;background:radial-gradient(circle at center,#1a0a0e 0%,#0d0508 100%);display:flex;justify-content:center;align-items:center;font-family:Tahoma,Arial,sans-serif;padding:20px;position:relative}
                .container{text-align:center;z-index:10;max-width:420px;width:100%}
                .flower-big{font-size:130px;animation:floatFlower 3s ease-in-out infinite;filter:drop-shadow(0 0 60px rgba(255,80,130,0.4));display:block;margin-bottom:10px}
                @keyframes floatFlower{0%,100%{transform:translateY(0px) rotate(-3deg)}50%{transform:translateY(-25px) rotate(3deg)}}
                .title{color:#ffa0b5;font-size:32px;font-weight:bold;margin-bottom:15px;text-shadow:0 0 40px rgba(255,80,130,0.3);letter-spacing:2px}
                .subtitle{color:#ffccd5;font-size:16px;margin-bottom:30px;opacity:0.9;line-height:2;padding:0 10px}
                .btn{display:block;width:100%;padding:18px 20px;margin-bottom:14px;border:none;border-radius:16px;font-size:18px;font-weight:bold;cursor:pointer;transition:all 0.3s ease;color:white}
                .btn-primary{background:linear-gradient(135deg,#ff416c,#ff758c);box-shadow:0 5px 30px rgba(255,65,108,0.3)}
                .btn-primary:hover{transform:scale(1.03);box-shadow:0 8px 40px rgba(255,65,108,0.5)}
                .btn-secondary{background:rgba(255,255,255,0.08);border:1px solid rgba(255,150,180,0.2);backdrop-filter:blur(10px);color:#ffccd5}
                .btn-secondary:hover{background:rgba(255,80,130,0.2);border-color:#ff416c;transform:scale(1.03)}
                .hearts{margin-top:25px;font-size:28px;letter-spacing:10px;animation:pulse 1.8s ease-in-out infinite}
                @keyframes pulse{0%,100%{transform:scale(1);opacity:0.7}50%{transform:scale(1.08);opacity:1}}
                .glow{position:fixed;width:350px;height:350px;border-radius:50%;background:radial-gradient(circle,rgba(255,50,100,0.08),transparent);pointer-events:none}
                .glow1{top:-120px;right:-120px}
                .glow2{bottom:-120px;left:-120px}
            </style>
        </head>
        <body>
            <div class="glow glow1"></div>
            <div class="glow glow2"></div>
            <div class="container">
                <div class="flower-big">🌹</div>
                <div class="title">برای تو</div>
                <div class="subtitle">💕 بعضی احساس‌ها رو نمیشه با کلمه گفت...<br>🌹 پس این رو برای تو کدنویسی کردم ❤️</div>
                <button class="btn btn-primary" onclick="sendChoice('talk')">❤️ بیا حرف بزنیم</button>
                <button class="btn btn-secondary" onclick="sendChoice('time')">🌱 فعلاً زمان می‌خوام</button>
                <div class="hearts">❤️ 💖 💕 💗 💘</div>
            </div>
            <script>
                const token = "''' + token + '''";
                function sendChoice(choice) {
                    fetch('/rose/'+token+'/response', {
                        method:'POST',
                        headers:{'Content-Type':'application/json'},
                        body:JSON.stringify({choice:choice})
                    })
                    .then(r=>r.json())
                    .then(d=>{
                        if(d.ok) {
                            alert(choice==='talk' ? '❤️ بیا حرف بزنیم... منتظرم' : '🌱 باشه... هر وقت آماده بودی');
                        } else {
                            alert('❌ خطا! دوباره تلاش کن');
                        }
                    })
                    .catch(()=>alert('❌ خطا! دوباره تلاش کن'));
                }
            </script>
        </body>
        </html>
        '''
        return html

    except BadSignature:
        return """
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"><title>🌹</title></head>
        <body style="background:#0d0508;color:white;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;font-family:Arial;text-align:center;flex-direction:column">
            <div style="font-size:80px">🌹</div>
            <h2>این لینک معتبر نیست</h2>
        </body>
        </html>
        """, 403

# ============================================================
# ❤️ پاسخ صفحه گل رز
# ============================================================

@app.route("/rose/<token>/response", methods=["POST"])
def rose_response(token):
    try:
        data = rose_signer.loads(token)
        target = str(data.get("target", ""))
        if target not in [PARTNER_CHAT_ID, TEST_CHAT_ID]:
            return jsonify({"ok": False}), 403
    except BadSignature:
        return jsonify({"ok": False}), 403

    body = request.get_json(silent=True) or {}
    choice = body.get("choice", "")

    if choice == "talk":
        send_message(YOUR_CHAT_ID, "❤️ پارتنرت از صفحه گل رز گزینه «بیا حرف بزنیم» را انتخاب کرد.")
    elif choice == "time":
        send_message(YOUR_CHAT_ID, "🌱 پارتنرت از صفحه گل رز گزینه «فعلاً زمان می‌خوام» را انتخاب کرد.")
    else:
        return jsonify({"ok": False}), 400

    return jsonify({"ok": True})

# ============================================================
# 🌐 Webhook
# ============================================================

@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "POST":
        try:
            data = request.get_json(silent=True)
            if not data:
                return "OK", 200

            if "message" in data:
                message = data["message"]
                chat = message["chat"]
                chat_id = str(chat["id"])
                text = message.get("text", "")
                
                # دریافت اطلاعات فایل
                file_data = None
                caption = message.get("caption", "")
                
                if "photo" in message:
                    # عکس - بزرگترین سایز رو انتخاب کن
                    photo = message["photo"][-1]
                    file_data = {
                        "type": "photo",
                        "file_id": photo["file_id"],
                        "caption": caption
                    }
                    
                elif "video" in message:
                    video = message["video"]
                    file_data = {
                        "type": "video",
                        "file_id": video["file_id"],
                        "caption": caption
                    }
                    
                elif "audio" in message:
                    audio = message["audio"]
                    file_data = {
                        "type": "audio",
                        "file_id": audio["file_id"],
                        "caption": caption,
                        "title": audio.get("title", "🎵"),
                        "performer": audio.get("performer", "❤️")
                    }
                    
                elif "document" in message:
                    # فایل معمولی - بررسی MIME type
                    doc = message["document"]
                    mime = doc.get("mime_type", "")
                    
                    if mime.startswith("image/"):
                        file_data = {
                            "type": "photo",
                            "file_id": doc["file_id"],
                            "caption": caption
                        }
                    elif mime.startswith("video/"):
                        file_data = {
                            "type": "video",
                            "file_id": doc["file_id"],
                            "caption": caption
                        }
                    elif mime.startswith("audio/"):
                        file_data = {
                            "type": "audio",
                            "file_id": doc["file_id"],
                            "caption": caption,
                            "title": doc.get("file_name", "🎵"),
                            "performer": "❤️"
                        }

                first_name = chat.get("first_name", "")
                last_name = chat.get("last_name", "")
                username = chat.get("username", "")
                contact = message.get("contact")
                phone_number = ""

                if contact:
                    phone_number = contact.get("phone_number", "")

                if text == "/start":
                    action = "🚀 کاربر /start زد"
                elif text:
                    action = f"🖱️ کاربر دکمه/پیام فرستاد:\n{text}"
                else:
                    action = "💬 کاربر یک Update بدون متن فرستاد"

                report_user_interaction(chat_id, action, first_name, last_name, username, phone_number)
                
                # اگر فایل وجود داره، handle_message رو با file_data صدا بزن
                if file_data:
                    handle_message(chat_id, text, file_data)
                else:
                    handle_message(chat_id, text)

            elif "callback_query" in data:
                callback = data["callback_query"]
                from_user = callback["from"]
                chat_id = str(from_user["id"])
                first_name = from_user.get("first_name", "")
                last_name = from_user.get("last_name", "")
                username = from_user.get("username", "")
                report_user_interaction(chat_id, "🖱️ کاربر روی Inline Button کلیک کرد", first_name, last_name, username, "")

            elif "edited_message" in data:
                edited = data["edited_message"]
                chat = edited["chat"]
                chat_id = str(chat["id"])
                report_user_interaction(chat_id, "✏️ پیام ویرایش شد", chat.get("first_name", ""), chat.get("last_name", ""), chat.get("username", ""), "")

        except Exception as e:
            print("Webhook error:", e)

    return "OK", 200

# ============================================================
# 🩺 Health
# ============================================================

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "rose-bot"})

# ============================================================
# 🚀 اجرای برنامه
# ============================================================

if __name__ == "__main__":
    print("🚀 ربات ahu goozlum روشن شد...")
    print(f"🎂 تولد: {BIRTH_DAY}/{BIRTH_MONTH}")
    print(f"📸 تعداد عکس‌ها: {len(PHOTOS)}")
    print("🩺 مسیر سلامت: /health")
    print(f"💬 پارتنر: {PARTNER_CHAT_ID}")
    print(f"🧪 تست: {TEST_CHAT_ID}")
    print("👀 گزارش تعامل‌های واقعی فعال است!")
    print("🎀 منوی روز دختر مستقل از آشتی است!")
    print("💔 منوی درخواست آشتی مستقل از روز دختر است!")
    print("🌹 صفحه گل رز فعال است!")
    print("🧪 چت تست فعال است!")
    print("📸 ارسال عکس/فیلم/موزیک در چت دوطرفه فعال است!")
    print(f"🌐 آدرس وب‌سایت: {WEBSITE_URL}")

    timer_thread = threading.Thread(target=birthday_timer, daemon=True)
    timer_thread.start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
