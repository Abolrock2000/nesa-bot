from flask import Flask, request
import requests
import json
import random
import datetime
import os
import threading
import time

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

WEBSITE_URL = "https://abolfazll-bot.onrender.com"

# ============================================================
# 🗂️ حافظه موقت
# ============================================================

user_access = {}
PARTNER_ACTIVITY = {}
RECONCILE_STATE = {}
PHOTO_VIEWED = {}

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
# 💕 پاسخ‌های عاشقانه
# ============================================================

LOVELY_RESPONSES = [
    "چشم آهو میای یا من میام واسه آشتی ... 🌹",
    "🥺 برای بار دوم میپرسم عروس خانوم وکیلم...",
    "💗 برای آخرین بار آتشی میپرسه وکیلم...",
    "عشقم خب تکلیف بچه تو شکمت چی میشه میخوای بدون پدر بزرگ شه😭؟",
    "💖 من بدون تو نمیتونم... بیا که با هم قشنگتریم...",
    "🌸 دلم برات تنگ شده... بیا که قلبم تنهاست...",
    "💕 با تو بودن یعنی آرامش... بیا که دلم بهانه‌ات شده...",
    "🌷 تو عشق اول و آخر منی... بیا پیشم...",
    "💗 من همیشه دوست دارم... حتی اگه تو نباشی... اما بیا که تنهام...",
    "🌹 میدونی که جای تو تو قلبم خالیه... بیا پر کن...",
    "💖 قلبم فقط برای تو میزنه... بیا که صداشو بشنوی...",
    "🌸 بدون تو زندگی بی‌رنگه... بیا که رنگی کن...",
    "💕 تو بهترین اتفاق زندگی منی... نذار از دستت بدم...",
    "🌷 با تو بودن یعنی بهشت... بیا که بهشتمو پس بده...",
    "💗 دلم میخواد صداتو بشنوم... بیا که گوشم بهانهتو گرفته ...",
    "🌹 تو تنها کسی هستی که میتونم باهاش حرف بزنم... بیا..."
]

# ============================================================
# 💔 پیام‌های آشتی
# ============================================================

RECONCILE_MESSAGES = [
    "💕 میدونم که هنوز دلت برام تنگ میشه... مثل من که هر شب بهت فکر میکنم 🌙",
    "🌸 یادته اولین بار که همدیگه رو دیدیم؟ اون روز دنیا برام قشنگ‌تر شد...",
    "💖 بیا که دیگه نمیتونم بدون تو باشم... قلبم فقط برای تو میزنه ❤️",
    "🌹 عشق من به تو مثل دریا بی‌نهایته... بیا که غرق میشیم...",
    "🥺 هر شب با یاد تو میخوابم... بیا که خوابم پر از تو باشه...",
    "💗 من به تو نیاز دارم... نه برای چیزی، فقط برای بودن با تو...",
    "🌷 تو تنها کسی هستی که میتونم بگم دوست دارم... بیا پیشم...",
    "🍃 با تو بودن آرامشه... بیا که دلم بهانه‌ات شده...",
    "💕 من هیچوقت از دوست داشتن تو دست نمیکشم... بیا که قلبم منتظرته...",
    "🌙 هر شب ستاره‌ها رو نگاه میکنم و برای تو آرزو میکنم...",
    "💖 تو زیباترین احساس زندگی منی... بیا که با هم قشنگتریم...",
    "🌸 دلم برات تنگ شده... بیا که قلبم تنهاست...",
    "🌹 من همیشه دوست دارم... حتی اگه تو نباشی... اما بیا که تنهام...",
    "💗 من تا آخرین نفس عاشقتم... بیا که با هم بمونیم..."
]

WIN_MESSAGES = [
    "❤️❤️❤️ یاااای! میدونستم! 🥰\n\nبهترین تصمیم دنیا رو گرفتی! من همیشه عاشقتم! 🌹",
    "💖 یااای! قلبم از خوشحالی میخواد بترکه! 😍\n\nمیدونستم که دوستم داری!",
    "🥰 میدونستم تو هنوز هم عاشقی! بیا که بغلم کنم! 💕",
    "💗 آخی جان! نمیدونی چقدر خوشحالم! تو بهترینی! 🌸",
    "🌹 عشقم... میدونستم که میای! تو همیشه قلبمی! ❤️"
]

# ============================================================
# 🕐 زمان ایران
# ============================================================

def get_current_iran_time():
    utc_now = datetime.datetime.now(datetime.timezone.utc)
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
        ["💬 چت دوطرفه"]
    ]

    if str(chat_id) == YOUR_CHAT_ID:

        keyboard.append(
            ["📊 وضعیت پارتنر"]
        )

        keyboard.append(
            ["💔 درخواست آشتی"]
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
# 💬 منوی چت
# ============================================================

def get_chat_keyboard():

    return {
        "keyboard": [
            ["📤 ارسال پیام به پارتنر"],
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
# 📸 ارسال عکس
# ============================================================

def send_photo(
    chat_id,
    photo_path,
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

        if photo_path.startswith("http"):

            payload = {
                "chat_id": chat_id,
                "photo": photo_path,
                "caption": caption
            }

            response = requests.post(
                url,
                data=payload,
                timeout=30
            )

            return response.status_code == 200

        if not os.path.exists(photo_path):

            send_message(
                chat_id,
                "❌ عکس پیدا نشد!"
            )

            return False

        with open(
            photo_path,
            "rb"
        ) as photo:

            files = {
                "photo": photo
            }

            data = {
                "chat_id": chat_id,
                "caption": caption
            }

            response = requests.post(
                url,
                data=data,
                files=files,
                timeout=30
            )

        return response.status_code == 200

    except Exception as e:

        print(
            "send_photo error:",
            e
        )

        return False

# ============================================================
# 🖼️ ارسال عکس با Tracking
# ============================================================

def send_photo_with_tracking(
    chat_id,
    photo_path,
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
        photo_path,
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
⏰ ساعت: {get_current_iran_time().strftime('%H:%M:%S')}

⚠️ تلگرام به ربات Read Receipt واقعی برای عکس نمی‌دهد."""
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
# 💔 سیستم آشتی
# ============================================================

def send_reconcile_survey(
    chat_id,
    attempt=0,
    target_name="کاربر"
):

    if attempt >= len(RECONCILE_MESSAGES):

        final_message = """💔 باشه... من میمونم با عشقم...

اما میدونم که تو هم دوستم داری... فقط زمان میخواد.

🌹 من همیشه منتظرتم... با تمام قلبم.

💕 دوستت دارم، حتی اگه الان نتونی بیای...

🍃 هر وقت آماده شدی، من اینجام..."""

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
            f"💔 {target_name} درخواست آشتی را ادامه نداد."
        )

        return

    message = f"""💔 {RECONCILE_MESSAGES[attempt]}

🌹 {random.choice([
    'منتظر عشقت هستم...',
    'قلبم برای تو میتپه...',
    'بیا که عاشقتم...',
    'دلم برات تنگ شده...',
    'تو بهترینی...'
])}
"""

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
            random.choice(WIN_MESSAGES)
        )

        send_message(
            chat_id,
            random.choice([
                "💕 میدونستم! عشقم!",
                "🌹 تو همیشه قلبمی!",
                "💖 من همیشه عاشقتم!",
                "🌸 بهترین خبر زندگی‌ام!",
                "🥰 عشق منی! همیشه!"
            ]),
            get_main_keyboard(chat_id)
        )

        send_message(
            YOUR_CHAT_ID,
            f"""🎉🎉🎉 {target_name} گفت بله! ❤️

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
            random.choice(LOVELY_RESPONSES)
        )

        send_message(
            chat_id,
            random.choice([
                "💕 میدونم که دوستم داری... فقط زمان میخواد...",
                "🌹 من صبر میکنم... تا ابد...",
                "💖 قلبم برای تو میزنه... همیشه...",
                "🌸 تو بهترین اتفاق زندگی منی...",
                "🥺 دلم برات تنگ شده... بیا..."
            ])
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
# 🤖 پردازش پیام
# ============================================================

def handle_message(
    chat_id,
    text
):

    chat_id = str(chat_id)
    text = (text or "").strip()

    # ساخت حافظه کاربر
    user_access.setdefault(
        chat_id,
        {
            "photos": False,
            "waiting_for_password": False,
            "waiting_for_reconcile": False,
            "waiting_for_chat_message": False,
            "mode": None
        }
    )

    user = user_access[chat_id]

    # ========================================================
    # 🔙 بازگشت به منو - باید قبل از stateها بررسی شود
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
            "mode": None
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
            "mode": None
        }

        send_message(
            chat_id,
            """🌻❤️ به دنیای ahu goozlum خوش اومدی ❤️🌻

🎁 اینجا یک گوشه کوچیک از قلب منه...

📸 عکس‌های خصوصی
📅 روز آشنایی
⏳ شمارش معکوس تولد
💬 چت دوطرفه

🌻 هر دکمه یک تکه از داستان ماست...""",
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
                PHOTO_VIEWED[chat_id].get(
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
    # 💬 حالت ارسال پیام
    # ========================================================

    if user.get(
        "waiting_for_chat_message",
        False
    ):

        if text in [
            "🔙 لغو",
            "🔙 بازگشت به منو"
        ]:

            user[
                "waiting_for_chat_message"
            ] = False

            send_message(
                chat_id,
                "❌ ارسال پیام لغو شد.",
                get_main_keyboard(chat_id)
            )

            return

        if not text:

            send_message(
                chat_id,
                "📝 لطفاً یک پیام بنویس."
            )

            return

        if chat_id == YOUR_CHAT_ID:

            sent = send_message(
                PARTNER_CHAT_ID,
                f"💬 پیام از طرف عشقت:\n\n{text}"
            )

        else:

            sent = send_message(
                YOUR_CHAT_ID,
                f"💬 پیام از طرف پارتنرت:\n\n{text}"
            )

        if sent:

            send_message(
                chat_id,
                "✅ پیامت ارسال شد ❤️",
                get_chat_keyboard()
            )

        else:

            send_message(
                chat_id,
                "❌ ارسال پیام ناموفق بود.",
                get_chat_keyboard()
            )

        user[
            "waiting_for_chat_message"
        ] = False

        return

    # ========================================================
    # 💬 چت دوطرفه
    # ========================================================

    if text == "💬 چت دوطرفه":

        user[
            "waiting_for_chat_message"
        ] = False

        send_message(
            chat_id,
            "💬 چت دوطرفه\n\nاز اینجا می‌تونی با عشقت حرف بزنی.",
            get_chat_keyboard()
        )

        return

    # ========================================================
    # 📤 ارسال پیام به پارتنر
    # ========================================================

    if text == "📤 ارسال پیام به پارتنر":

        user[
            "waiting_for_chat_message"
        ] = True

        send_message(
            chat_id,
            "💬 پیامت رو بنویس:",
            get_chat_keyboard()
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
            else list(PARTNER_ACTIVITY.keys())[0]
        )

        data = PARTNER_ACTIVITY[
            partner_id
        ]

        last_seen = data["last_seen"]
        first_seen = data["first_seen"]

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

        if reconcile_status.get("status") == "accepted":

            reconcile_text = "❤️ آشتی کرد 🥰"

        elif reconcile_status.get("status") == "ended":

            reconcile_text = "💔 پایان یافت"

        elif reconcile_status.get("status") == "waiting":

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
            user["waiting_for_password"] = False

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

                    photo = PHOTOS["📸 عکس ۱"]

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
# 🌐 Webhook
# ============================================================

@app.route(
    "/",
    methods=["GET", "POST"]
)
def webhook():

    if request.method == "POST":

        try:

            data = request.get_json(
                silent=True
            )

            if not data:
                return "OK", 200

            # =================================================
            # پیام معمولی
            # =================================================

            if "message" in data:

                message = data["message"]

                chat = message["chat"]

                chat_id = str(
                    chat["id"]
                )

                text = message.get(
                    "text",
                    ""
                )

                first_name = chat.get(
                    "first_name",
                    ""
                )

                last_name = chat.get(
                    "last_name",
                    ""
                )

                username = chat.get(
                    "username",
                    ""
                )

                contact = message.get(
                    "contact"
                )

                phone_number = ""

                if contact:

                    phone_number = contact.get(
                        "phone_number",
                        ""
                    )

                if text == "/start":

                    action = "🚀 کاربر /start زد"

                elif text:

                    action = (
                        f"🖱️ کاربر دکمه/پیام فرستاد:\n"
                        f"{text}"
                    )

                else:

                    action = (
                        "💬 کاربر یک Update بدون متن فرستاد"
                    )

                report_user_interaction(
                    chat_id,
                    action,
                    first_name,
                    last_name,
                    username,
                    phone_number
                )

                handle_message(
                    chat_id,
                    text
                )

            # =================================================
            # Callback Query
            # =================================================

            elif "callback_query" in data:

                callback = data[
                    "callback_query"
                ]

                from_user = callback["from"]

                chat_id = str(
                    from_user["id"]
                )

                first_name = from_user.get(
                    "first_name",
                    ""
                )

                last_name = from_user.get(
                    "last_name",
                    ""
                )

                username = from_user.get(
                    "username",
                    ""
                )

                report_user_interaction(
                    chat_id,
                    "🖱️ کاربر روی Inline Button کلیک کرد",
                    first_name,
                    last_name,
                    username,
                    ""
                )

            # =================================================
            # Edited Message
            # =================================================

            elif "edited_message" in data:

                edited = data[
                    "edited_message"
                ]

                chat = edited["chat"]

                chat_id = str(
                    chat["id"]
                )

                report_user_interaction(
                    chat_id,
                    "✏️ پیام ویرایش شد",
                    chat.get(
                        "first_name",
                        ""
                    ),
                    chat.get(
                        "last_name",
                        ""
                    ),
                    chat.get(
                        "username",
                        ""
                    ),
                    ""
                )

        except Exception as e:

            print(
                "Webhook error:",
                e
            )

    return "OK", 200

# ============================================================
# 🩺 Health
# ============================================================

@app.route(
    "/health",
    methods=["GET"]
)
def health():

    return "OK", 200

# ============================================================
# 🚀 اجرای برنامه
# ============================================================

if __name__ == "__main__":

    print(
        "🚀 ربات ahu goozlum روشن شد..."
    )

    print(
        f"🎂 تولد: {BIRTH_DAY}/{BIRTH_MONTH}"
    )

    print(
        f"📸 تعداد عکس‌ها: {len(PHOTOS)}"
    )

    print(
        "🩺 مسیر سلامت: /health"
    )

    print(
        f"💬 پارتنر: {PARTNER_CHAT_ID}"
    )

    print(
        f"🧪 تست: {TEST_CHAT_ID}"
    )

    print(
        "👀 گزارش تعامل‌های واقعی فعال است!"
    )

    print(
        "🎀 منوی روز دختر مستقل از آشتی است!"
    )

    print(
        "💔 منوی درخواست آشتی مستقل از روز دختر است!"
    )

    # ========================================================
    # Thread تولد
    # ========================================================

    timer_thread = threading.Thread(
        target=birthday_timer,
        daemon=True
    )

    timer_thread.start()

    # ========================================================
    # پورت Render
    # ========================================================

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
