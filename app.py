from flask import Flask, request, render_template_string
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

user_access = {}
PARTNER_ACTIVITY = {}
RECONCILE_STATE = {}
PHOTO_VIEWED = {}  # برای ذخیره وضعیت دیده شدن عکس

WEBSITE_URL = "https://abolfazll-bot.onrender.com"

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
# 💕 متن‌های دلبرانه و احساسی
# ============================================================

LOVELY_RESPONSES = [
    "💕 میدونم دلت پشتمه... فقط نمیخوای نشون بدی. من صبر میکنم... 🌹",
    "🥺 آخی جان... دلم برات تنگ شده. بیا پیشم...",
    "💗 قلبم میگه که تو هم دوستم داری... فقط بیا...",
    "🌹 تو زیباترین احساس زندگی منی... چرا از خودت دور میشی؟",
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
    "💗 دلم میخواد صداتو بشنوم... بیا که گوشم بهانه‌ات شده...",
    "🌹 تو تنها کسی هستی که میتونم باهاش حرف بزنم... بیا...",
]

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
    "🌙 هر شب ستاره‌ها رو نگاه میکنم و برای تو آرزو میکنم... بیا که آرزوم برآورده شه...",
    "💖 تو زیباترین احساس زندگی منی... بیا که با هم قشنگتریم...",
    "🌸 دلم برات تنگ شده... بیا که قلبم تنهاست...",
    "🌹 من همیشه دوست دارم... حتی اگه تو نباشی... اما بیا که تنهام...",
    "💗 من تا آخرین نفس عاشقتم... بیا که با هم بمونیم...",
]

WIN_MESSAGES = [
    "❤️❤️❤️ یاااای! میدونستم! 🥰\n\nبهترین تصمیم دنیا رو گرفتی! من همیشه عاشقتم! 🌹",
    "💖 یااای! قلبم از خوشحالی میخواد بترکه! 😍\n\nمیدونستم که دوستم داری!",
    "🥰 میدونستم تو هنوز هم عاشقی! بیا که بغلم کنم! 💕",
    "💗 آخی جان! نمیدونی چقدر خوشحالم! تو بهترینی! 🌸",
    "🌹 عشقم... میدونستم که میای! تو همیشه قلبمی! ❤️",
]


# ============================================================
# 🕐 زمان ایران
# ============================================================

def get_current_iran_time():
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    return utc_now.astimezone(datetime.timezone(IRAN_OFFSET))


# ============================================================
# 📊 ثبت فعالیت پارتنر (با اطلاع‌رسانی کامل)
# ============================================================

def log_partner_activity(chat_id, action="ورود", first_name="", last_name="", username="", phone_number=""):
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
            "phone_number": phone_number
        }
    
    if first_name:
        PARTNER_ACTIVITY[chat_id]["first_name"] = first_name
    if last_name:
        PARTNER_ACTIVITY[chat_id]["last_name"] = last_name
    if username:
        PARTNER_ACTIVITY[chat_id]["username"] = username
    if phone_number:
        PARTNER_ACTIVITY[chat_id]["phone_number"] = phone_number
    
    PARTNER_ACTIVITY[chat_id]["last_seen"] = now
    PARTNER_ACTIVITY[chat_id]["last_action"] = action
    PARTNER_ACTIVITY[chat_id]["count"] += 1
    
    time_str = now.strftime("%H:%M:%S")
    date_str = now.strftime("%Y/%m/%d")
    date_persian = now.strftime("%A")
    
    weekdays = {
        "Monday": "دوشنبه",
        "Tuesday": "سه‌شنبه",
        "Wednesday": "چهارشنبه",
        "Thursday": "پنج‌شنبه",
        "Friday": "جمعه",
        "Saturday": "شنبه",
        "Sunday": "یک‌شنبه"
    }
    day_persian = weekdays.get(date_persian, date_persian)
    
    # پیام ورود کامل با اطلاعات
    message = f"""🌸 پارتنرت وارد ربات شد! 🌸

👤 اطلاعات کاربر:
• آیدی عددی: {chat_id}
• نام: {first_name or 'نامشخص'}
• نام خانوادگی: {last_name or 'نامشخص'}
• یوزرنیم: {'@' + username if username else 'ندارد'}
• شماره تلفن: {phone_number or 'نامشخص'}

📅 تاریخ: {date_str}
📆 روز: {day_persian}
⏰ ساعت: {time_str}

🔢 تعداد کل ورودها: {PARTNER_ACTIVITY[chat_id]['count']}
📌 آخرین اقدام: {action}

🔗 لینک پروفایل: {'https://t.me/' + username if username else 'ندارد'}

❤️ پارتنرت آنلاین شد!"""
    
    send_message(YOUR_CHAT_ID, message)
    
    if chat_id not in user_access:
        send_message(YOUR_CHAT_ID, f"💡 پارتنر برای اولین بار وارد ربات شد! (رمز گالری: {PASSWORD})")


# ============================================================
# 📸 ارسال عکس با قابلیت تشخیص دیده شدن
# ============================================================

def send_photo_with_tracking(chat_id, photo_path, caption="", target_name="کاربر"):
    """ارسال عکس و ثبت برای تشخیص دیده شدن"""
    
    # اضافه کردن شناسه منحصر به فرد به کپشن
    photo_id = f"PHOTO_{int(time.time())}_{random.randint(1000, 9999)}"
    full_caption = f"{caption}\n\n━━━━━━━━━━━━━━━━━━━━━━\n🆔 {photo_id}"
    
    success = send_photo(chat_id, photo_path, full_caption)
    
    if success:
        # ذخیره وضعیت عکس برای تشخیص دیده شدن
        PHOTO_VIEWED[chat_id] = {
            "photo_id": photo_id,
            "sent_at": get_current_iran_time(),
            "viewed": False,
            "viewed_at": None
        }
        
        # به مالک اطلاع بده که عکس ارسال شد
        send_message(YOUR_CHAT_ID, f"📸 عکس به {target_name} ارسال شد!\n🆔 {photo_id}\n⏰ {get_current_iran_time().strftime('%H:%M:%S')}")
        
        return True
    return False


def check_photo_viewed(chat_id):
    """بررسی اینکه عکس دیده شده یا نه"""
    if chat_id in PHOTO_VIEWED:
        data = PHOTO_VIEWED[chat_id]
        if data["viewed"]:
            return True
    return False


# ============================================================
# 🖼️ ارسال عکس از مسیر با تشخیص دیده شدن
# ============================================================

def send_photo_from_path(chat_id, target_name="کاربر"):
    """ارسال عکس با پیام احساسی و قابلیت تشخیص دیده شدن"""
    
    photo_path = "photos/file_00000000f1788210bc5e8d993e16a277.png"
    
    caption = f"""🌹 این عکس رو برای تو فرستادم...

💕 چون تو زیباترین اتفاق زندگی منی...
🌸 هر بار که نگاهت میکنم، قلبم میتپه...

❤️ این عکس یادگاری از عشق منه...
🌷 امیدوارم که دوست داشته باشی...

🥰 همیشه عاشقتم...

━━━━━━━━━━━━━━━━━━━━━━
📸 اسم عکس: file_00000000f1788210bc5e8d993e16a277.png
💕 درستش اینه ❤️"""
    
    success = send_photo_with_tracking(chat_id, photo_path, caption, target_name)
    
    if success:
        send_message(chat_id, "💕 عکس رو دریافت کردی؟ امیدوارم خوشت اومده باشه... 🌹")
        
        # بعد از 30 ثانیه چک کن ببینه یا نه
        def check_viewed():
            time.sleep(30)
            if check_photo_viewed(chat_id):
                send_message(YOUR_CHAT_ID, f"👀 {target_name} عکس رو دید! 🥰")
            else:
                send_message(YOUR_CHAT_ID, f"⏳ {target_name} هنوز عکس رو ندیده... 😔")
        
        threading.Thread(target=check_viewed, daemon=True).start()
        
        return True
    else:
        send_message(chat_id, "❌ متاسفم! عکس پیدا نشد! 😢\n\nمسیر عکس رو چک کن!")
        return False


# ============================================================
# 📸 ارسال عکس معمولی
# ============================================================

def send_photo(chat_id, photo_path, caption=""):
    try:
        if photo_path.startswith("http"):
            url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
            payload = {"chat_id": chat_id, "photo": photo_path, "caption": caption}
            response = requests.post(url, data=payload, timeout=30)
            return response.status_code == 200

        if not os.path.exists(photo_path):
            send_message(chat_id, "❌ عکس پیدا نشد!")
            return False

        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        with open(photo_path, "rb") as photo:
            files = {"photo": photo}
            data = {"chat_id": chat_id, "caption": caption}
            response = requests.post(url, data=data, files=files, timeout=30)
        return response.status_code == 200
    except Exception as e:
        print("send_photo error:", e)
        return False


# ============================================================
# 📤 ارسال پیام
# ============================================================

def send_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        payload = {"chat_id": chat_id, "text": text}
        if reply_markup:
            payload["reply_markup"] = json.dumps(reply_markup, ensure_ascii=False)
        response = requests.post(url, data=payload, timeout=15)
        if response.status_code == 200:
            return True
        print("Telegram error:", response.status_code, response.text)
    except Exception as e:
        print("send_message error:", e)
    return False


# ============================================================
# 💞 متن‌های روز آشنایی
# ============================================================

SECOND_QUOTES = [
    "هر ثانیه‌ای که می‌گذرد، عشق من به تو عمیق‌تر می‌شود... ❤️",
    "ثانیه‌ها می‌گذرند، اما عشق من به تو هرگز کهنه نمی‌شود... 🌹",
    "در هر ثانیه‌ای از زندگی‌ام، تو را نفس می‌کشم... 💫",
    "ثانیه‌های بی‌تو طولانی‌اند، اما کنار تو حتی ساعت‌ها هم کوتاه‌اند... ✨",
    "هر ثانیه که می‌گذرد، یک دلیل تازه برای دوست داشتن تو پیدا می‌کنم... ❤️",
    "ثانیه‌ها را بشمار، اما عشق را نه؛ چون عشق من به تو بی‌نهایت است... 🌸"
]


# ============================================================
# ⏳ روز آشنایی
# ============================================================

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
    return int((now - MEETING_DATE).total_seconds())


def get_meeting_days():
    seconds = get_meeting_seconds()
    return seconds // 86400


# ============================================================
# 🎂 ساعت باقی‌مانده تا تولد
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
    return int(diff.total_seconds() // 3600)


# ============================================================
# ⌨️ منوی اصلی
# ============================================================

def get_main_keyboard(chat_id=None):
    keyboard = [
        ["📸 عکس‌ها"],
        ["📅 روز آشنایی", "⏳ ساعت تا تولدت"],
        ["💬 چت دوطرفه"]
    ]
    
    if chat_id == YOUR_CHAT_ID:
        keyboard.append(["📊 وضعیت پارتنر"])
        keyboard.append(["💔 درخواست آشتی"])
        keyboard.append(["🖼️ ارسال عکس"])
    
    keyboard.append(["🔙 بازگشت به منو"])
    
    return {
        "keyboard": keyboard,
        "resize_keyboard": True
    }


# ============================================================
# 📸 منوی عکس‌ها
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
# 🔐 منوی پسورد
# ============================================================

def get_password_keyboard():
    return {
        "keyboard": [
            ["🔙 بازگشت به منو"]
        ],
        "resize_keyboard": True
    }


# ============================================================
# 💬 منوی چت دوطرفه
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
# 💔 منوی نظرسنجی آشتی
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
# 💔 منوی انتخاب مخاطب برای آشتی
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
# 💔 سیستم نظرسنجی آشتی
# ============================================================

def send_reconcile_survey(chat_id, attempt=0, target_name="کاربر"):
    """ارسال نظرسنجی آشتی با متن‌های عاشقانه و احساسی"""
    
    if attempt >= len(RECONCILE_MESSAGES):
        final_message = f"""💔 باشه... من میمونم با عشقم...

اما میدونم که تو هم دوستم داری... فقط زمان میخواد.

🌹 من همیشه منتظرتم... با تمام قلبم.

💕 دوستت دارم، حتی اگه الان نتونی بیای...

🍃 هر وقت آماده شدی، من اینجام... منتظر عشقت..."""
        send_message(chat_id, final_message)
        RECONCILE_STATE[chat_id] = {"status": "ended", "attempt": attempt}
        
        if chat_id == TEST_CHAT_ID:
            send_message(YOUR_CHAT_ID, f"🧪 تست به پایان رسید! 😔\n\nولی میدونم که دلش میخواد بیاد...")
        else:
            send_message(YOUR_CHAT_ID, f"💔 پارتنر نتونست بیاد...\n\nولی عشق من همیشه باقیه... ❤️")
        return
    
    message = f"""💔 {RECONCILE_MESSAGES[attempt]}

🌹 {random.choice(['منتظر عشقت هستم...', 'قلبم برای تو میتپه...', 'بیا که عاشقتم...', 'دلم برات تنگ شده...', 'تو بهترینی...'])}
"""
    
    send_message(chat_id, message, get_reconcile_keyboard())
    RECONCILE_STATE[chat_id] = {"status": "waiting", "attempt": attempt, "target_name": target_name}


def handle_reconcile_response(chat_id, response):
    """پردازش پاسخ مخاطب با عشق و احساس"""
    
    chat_id = str(chat_id)
    state = RECONCILE_STATE.get(chat_id, {})
    
    if state.get("status") != "waiting":
        return
    
    attempt = state.get("attempt", 0)
    target_name = state.get("target_name", "کاربر")
    
    if response == "❤️ بله، دوست دارم ❤️":
        win_msg = random.choice(WIN_MESSAGES)
        send_message(chat_id, win_msg)
        
        extra_msgs = [
            "💕 میدونستم! عشقم!",
            "🌹 تو همیشه قلبمی!",
            "💖 من همیشه عاشقتم!",
            "🌸 بهترین خبر زندگی‌ام!",
            "🥰 عشق منی! همیشه!"
        ]
        send_message(chat_id, random.choice(extra_msgs))
        
        if chat_id == TEST_CHAT_ID:
            send_message(YOUR_CHAT_ID, f"🧪 تست: ❤️ بله گفت!\n\nسیستم عالی کار کرد! 🌹")
            send_message(YOUR_CHAT_ID, f"💕 حالا برو پیش پارتنرت! عشق رو ثابت کن! 😍")
        else:
            send_message(YOUR_CHAT_ID, f"🎉🎉🎉 پارتنرت گفت بله! ❤️\n\n{chat_id} قبول کرد که آشتی کنه! 🥳\n\n{random.choice(['تبریک! عشق پیروز شد! 🥰', 'بهترین خبر! 😍', 'حالا عشق رو جشن بگیر! 💖'])}")
        
        RECONCILE_STATE[chat_id] = {"status": "accepted", "attempt": attempt}
        return
    
    elif response == "💔 نه، نمیتونم 😢":
        lovely_msg = random.choice(LOVELY_RESPONSES)
        send_message(chat_id, lovely_msg)
        
        extra_lovely = [
            "💕 میدونم که دوستم داری... فقط زمان میخواد...",
            "🌹 من صبر میکنم... تا ابد...",
            "💖 قلبم برای تو میزنه... همیشه...",
            "🌸 تو بهترین اتفاق زندگی منی...",
            "🥺 دلم برات تنگ شده... بیا...",
        ]
        send_message(chat_id, random.choice(extra_lovely))
        
        if chat_id == TEST_CHAT_ID:
            send_message(YOUR_CHAT_ID, f"🧪 تست: نه گفت... (تلاش {attempt + 1}) 😢")
            send_message(YOUR_CHAT_ID, f"💕 عشق رو ادامه بده... بالاخره میاد...")
        else:
            send_message(YOUR_CHAT_ID, f"💔 {target_name} نتونست بیاد... (تلاش {attempt + 1})\n{random.choice(['عشق رو ادامه بده... 🌹', 'منتظرش باش... 💕', 'قلبش پشتمه... ❤️'])}")
        
        send_reconcile_survey(chat_id, attempt + 1, target_name)
        return


# ============================================================
# 🤖 پردازش پیام‌ها (با تشخیص دیده شدن عکس)
# ============================================================

def handle_message(chat_id, text):
    global PARTNER_ACTIVITY, PHOTO_VIEWED
    
    chat_id = str(chat_id)
    text = text.strip()

    # ========================================================
    # 📸 تشخیص دیده شدن عکس (هر پیامی = دیده شدن)
    # ========================================================
    
    if chat_id != YOUR_CHAT_ID:
        # اگه پارتنر هر پیامی بفرسته، یعنی آنلاین شده و عکس رو دیده
        if chat_id in PHOTO_VIEWED and not PHOTO_VIEWED[chat_id]["viewed"]:
            PHOTO_VIEWED[chat_id]["viewed"] = True
            PHOTO_VIEWED[chat_id]["viewed_at"] = get_current_iran_time()
            send_message(YOUR_CHAT_ID, f"👀 پارتنر عکس رو دید! 🥰\n⏰ {get_current_iran_time().strftime('%H:%M:%S')}")

    # ========================================================
    # 💔 پاسخ به نظرسنجی آشتی
    # ========================================================
    
    if text in ["❤️ بله، دوست دارم ❤️", "💔 نه، نمیتونم 😢"]:
        if chat_id != YOUR_CHAT_ID:
            handle_reconcile_response(chat_id, text)
        return

    # ========================================================
    # 💬 حالت چت دوطرفه - ارسال پیام
    # ========================================================
    
    if user_access.get(chat_id, {}).get("waiting_for_chat_message", False):
        if text == "🔙 لغو" or text == "🔙 بازگشت به منو":
            user_access[chat_id]["waiting_for_chat_message"] = False
            send_message(chat_id, "❌ ارسال پیام لغو شد.", get_main_keyboard(chat_id))
            return
        
        if not text:
            send_message(chat_id, "📝 لطفاً یک پیام بنویس.")
            return
        
        if chat_id == YOUR_CHAT_ID:
            sent = send_message(PARTNER_CHAT_ID, f"💬 پیام از طرف عشقت:\n\n{text}")
            if sent:
                send_message(chat_id, f"✅ پیامت به پارتنر فرستاده شد:\n\n{text}", get_chat_keyboard())
            else:
                send_message(chat_id, "❌ ارسال پیام ناموفق بود.", get_chat_keyboard())
        else:
            sent = send_message(YOUR_CHAT_ID, f"💬 پیام از طرف پارتنرت:\n\n{text}")
            if sent:
                send_message(chat_id, f"✅ پیامت به عشقت فرستاده شد:\n\n{text}", get_chat_keyboard())
            else:
                send_message(chat_id, "❌ ارسال پیام ناموفق بود!", get_chat_keyboard())
        
        user_access[chat_id]["waiting_for_chat_message"] = False
        return

    # ========================================================
    # 💬 چت دوطرفه
    # ========================================================
    
    if text == "💬 چت دوطرفه":
        user_access[chat_id] = user_access.get(chat_id, {})
        user_access[chat_id]["waiting_for_chat_message"] = False
        send_message(chat_id, "💬 چت دوطرفه\n\nاز اینجا می‌تونی با عشقت حرف بزنی.", get_chat_keyboard())
        return
    
    if text == "📤 ارسال پیام به پارتنر":
        user_access[chat_id] = user_access.get(chat_id, {})
        user_access[chat_id]["waiting_for_chat_message"] = True
        send_message(chat_id, "💬 پیامت رو بنویس:\n\n(برای لغو دکمه لغو رو بزن)", get_chat_keyboard())
        return

    # ========================================================
    # 💔 درخواست آشتی (فقط برای صاحب ربات)
    # ========================================================
    
    if text == "💔 درخواست آشتی":
        if chat_id == YOUR_CHAT_ID:
            send_message(
                chat_id, 
                "💔 به چه کسی می‌خوای درخواست آشتی بدی؟\n\n"
                "🌹 با عشق و احساس برنده شو!",
                get_reconcile_target_menu()
            )
        else:
            send_message(chat_id, "❌ این بخش فقط برای صاحب ربات dostęp است.", get_main_keyboard(chat_id))
        return
    
    # ========================================================
    # ❤️ ارسال به پارتنر (آشتی)
    # ========================================================
    
    if text == "❤️ ارسال به پارتنر":
        if chat_id == YOUR_CHAT_ID:
            send_message(chat_id, "📤 ارسال درخواست آشتی به پارتنر... 💕")
            
            state = RECONCILE_STATE.get(PARTNER_CHAT_ID, {})
            if state.get("status") == "accepted":
                send_message(chat_id, "❤️ پارتنرت قبلاً آشتی رو قبول کرده! 🥰")
                return
            
            send_reconcile_survey(PARTNER_CHAT_ID, 0, "پارتنر")
            send_message(chat_id, "✅ درخواست آشتی به پارتنر ارسال شد!\n\nمنتظر عشقش باش... ❤️")
            send_message(chat_id, "🌹 عشق پیروز میشه... مطمئنم! 💕")
        else:
            send_message(chat_id, "❌ این بخش فقط برای صاحب ربات dostęp است.", get_main_keyboard(chat_id))
        return
    
    # ========================================================
    # 🧪 ارسال به تست (آشتی)
    # ========================================================
    
    if text == "🧪 ارسال به تست":
        if chat_id == YOUR_CHAT_ID:
            send_message(chat_id, "🧪 ارسال درخواست آشتی به اکانت تست (7989818498)...")
            
            state = RECONCILE_STATE.get(TEST_CHAT_ID, {})
            if state.get("status") == "accepted":
                send_message(chat_id, "🧪 قبلاً تست رو قبول کردی! 🥰")
                send_message(chat_id, "💕 حالا برو سراغ پارتنرت! عشق رو ادامه بده! 😍")
                return
            
            send_reconcile_survey(TEST_CHAT_ID, 0, "تست")
            send_message(chat_id, "🧪 درخواست آشتی به اکانت تست ارسال شد!\n\nحالا برو به اکانت تست و پاسخ بده...")
            send_message(chat_id, "🌹 با عشق و احساس برنده شو! 💕")
        else:
            send_message(chat_id, "❌ این بخش فقط برای صاحب ربات dostęp است.", get_main_keyboard(chat_id))
        return

    # ========================================================
    # 🖼️ ارسال عکس (فقط برای صاحب ربات)
    # ========================================================
    
    if text == "🖼️ ارسال عکس":
        if chat_id == YOUR_CHAT_ID:
            send_message(
                chat_id,
                "🖼️ عکس رو به چه کسی می‌خوای ارسال کنی؟\n\n"
                "🌸 این عکس یادگاری از عشق منه...",
                get_photo_send_menu()
            )
        else:
            send_message(chat_id, "❌ این بخش فقط برای صاحب ربات dostęp است.", get_main_keyboard(chat_id))
        return
    
    # ========================================================
    # 📤 ارسال عکس به پارتنر
    # ========================================================
    
    if text == "📤 ارسال عکس به پارتنر":
        if chat_id == YOUR_CHAT_ID:
            send_message(chat_id, "📤 ارسال عکس به پارتنر... 🌹")
            
            success = send_photo_from_path(PARTNER_CHAT_ID, "پارتنر")
            
            if success:
                send_message(chat_id, "✅ عکس با موفقیت به پارتنر ارسال شد! 🌹")
                send_message(chat_id, "💕 منتظر بمون تا ببینم عکس رو دید یا نه... 👀")
            else:
                send_message(chat_id, "❌ ارسال عکس ناموفق بود! مسیر عکس رو چک کن!")
        else:
            send_message(chat_id, "❌ این بخش فقط برای صاحب ربات dostęp است.", get_main_keyboard(chat_id))
        return
    
    # ========================================================
    # 🧪 ارسال عکس به تست
    # ========================================================
    
    if text == "🧪 ارسال عکس به تست":
        if chat_id == YOUR_CHAT_ID:
            send_message(chat_id, "🧪 ارسال عکس به اکانت تست (7989818498)...")
            
            success = send_photo_from_path(TEST_CHAT_ID, "تست")
            
            if success:
                send_message(chat_id, "✅ عکس با موفقیت به اکانت تست ارسال شد! 🌹")
                send_message(chat_id, "🧪 حالا برو به اکانت تست و عکس رو ببین!\n\nاگه راضی بودی، به پارتنرت بفرست! 💕")
            else:
                send_message(chat_id, "❌ ارسال عکس ناموفق بود! مسیر عکس رو چک کن!")
        else:
            send_message(chat_id, "❌ این بخش فقط برای صاحب ربات dostęp است.", get_main_keyboard(chat_id))
        return

    # ========================================================
    # 📊 وضعیت پارتنر
    # ========================================================
    
    if text == "📊 وضعیت پارتنر":
        if chat_id == YOUR_CHAT_ID:
            if PARTNER_ACTIVITY:
                partner_id = list(PARTNER_ACTIVITY.keys())[0]
                data = PARTNER_ACTIVITY[partner_id]
                last_seen = data["last_seen"]
                first_seen = data["first_seen"]
                
                time_str = last_seen.strftime("%H:%M:%S")
                date_str = last_seen.strftime("%Y/%m/%d")
                first_time = first_seen.strftime("%H:%M:%S")
                first_date = first_seen.strftime("%Y/%m/%d")
                
                now = get_current_iran_time()
                diff = (now - last_seen).total_seconds()
                status = "🟢 آنلاین" if diff < 300 else "🔴 آفلاین"
                
                reconcile_status = RECONCILE_STATE.get(partner_id, {})
                reconcile_text = ""
                if reconcile_status.get("status") == "accepted":
                    reconcile_text = "❤️ آشتی کرد 🥰"
                elif reconcile_status.get("status") == "ended":
                    reconcile_text = "💔 نتونست بیاد... 😢"
                elif reconcile_status.get("status") == "waiting":
                    reconcile_text = "⏳ منتظر عشقش... 🌹"
                else:
                    reconcile_text = "❓ هنوز درخواستی نشده"
                
                test_state = RECONCILE_STATE.get(TEST_CHAT_ID, {})
                test_text = ""
                if test_state.get("status") == "accepted":
                    test_text = "✅ تست قبول شد 🥰"
                elif test_state.get("status") == "ended":
                    test_text = "❌ تست رد شد 😔"
                elif test_state.get("status") == "waiting":
                    test_text = "⏳ تست در حال بررسی..."
                else:
                    test_text = "❓ تست انجام نشده"
                
                # وضعیت دیده شدن عکس
                photo_status = "📸 عکسی ارسال نشده"
                if partner_id in PHOTO_VIEWED:
                    if PHOTO_VIEWED[partner_id]["viewed"]:
                        photo_status = f"👀 عکس دیده شد! ({PHOTO_VIEWED[partner_id]['viewed_at'].strftime('%H:%M:%S')})"
                    else:
                        photo_status = f"⏳ عکس ارسال شده، هنوز دیده نشده"
                
                message = f"""📊 وضعیت کامل پارتنر

👤 اطلاعات کاربر:
• آیدی عددی: {partner_id}
• نام: {data.get('first_name', 'نامشخص')}
• نام خانوادگی: {data.get('last_name', 'نامشخص')}
• یوزرنیم: {'@' + data.get('username') if data.get('username') else 'ندارد'}
• شماره تلفن: {data.get('phone_number', 'نامشخص')}

📅 اولین ورود: {first_date} - {first_time}
📅 آخرین ورود: {date_str} - {time_str}

🔢 تعداد کل ورودها: {data['count']}

📌 آخرین اقدام: {data['last_action']}

❤️ وضعیت: {status}

💔 وضعیت آشتی: {reconcile_text}

🧪 وضعیت تست: {test_text}

🖼️ {photo_status}

🔗 لینک پروفایل: {'https://t.me/' + data.get('username') if data.get('username') else 'ندارد'}

{'💬 پارتنر در ۵ دقیقه گذشته آنلاین بوده!' if diff < 300 else '⏳ پارتنر بیش از ۵ دقیقه است آنلاین نبوده.'}
"""
            else:
                message = "❌ پارتنر هنوز وارد ربات نشده است."
            
            send_message(chat_id, message, get_main_keyboard(chat_id))
        else:
            send_message(chat_id, "❌ این بخش فقط برای صاحب ربات dostęp است.", get_main_keyboard(chat_id))
        return

    # ========================================================
    # 🔐 پسورد
    # ========================================================
    
    if user_access.get(chat_id, {}).get("waiting_for_password", False):
        if text == PASSWORD:
            user_access[chat_id]["photos"] = True
            user_access[chat_id]["waiting_for_password"] = False
            send_message(chat_id, "✅ رمز درست بود!\n\n🔓 گالری عکس‌های اختصاصی برات باز شد ❤️", get_photo_keyboard())
        else:
            send_message(chat_id, "❌ رمز اشتباهه!\n\nدوباره امتحان کن ❤️", get_password_keyboard())
        return

    # ========================================================
    # 📸 عکس‌ها
    # ========================================================
    
    if text in PHOTOS:
        if user_access.get(chat_id, {}).get("photos", False):
            photo = PHOTOS[text]
            send_photo(chat_id, photo["path"], photo["caption"])
        else:
            user_access[chat_id] = user_access.get(chat_id, {})
            user_access[chat_id]["waiting_for_password"] = True
            send_message(chat_id, "🔐 این قسمت خصوصی و مخصوص خودته.\n\nلطفاً رمز مخصوص رو وارد کن ❤️", get_password_keyboard())
        return

    # ========================================================
    # 📸 گالری
    # ========================================================
    
    if text == "📸 عکس‌ها":
        if user_access.get(chat_id, {}).get("photos", False):
            send_message(chat_id, "📸 کدوم عکس رو می‌خوای ببینی؟ ❤️", get_photo_keyboard())
        else:
            user_access[chat_id] = user_access.get(chat_id, {})
            user_access[chat_id]["waiting_for_password"] = True
            send_message(chat_id, "🔐 برای ورود به گالری\nرمز مخصوص رو وارد کن ❤️", get_password_keyboard())
        return

    # ========================================================
    # 📅 روز آشنایی
    # ========================================================
    
    if text == "📅 روز آشنایی":
        seconds = get_meeting_seconds()
        days = seconds // 86400
        quote = random.choice(SECOND_QUOTES)
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
        send_message(chat_id, message)
        return

    # ========================================================
    # ⏳ ساعت تا تولد
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
    # 🔙 بازگشت به منو
    # ========================================================
    
    if text == "🔙 بازگشت به منو":
        old_access = user_access.get(chat_id, {})
        user_access[chat_id] = {
            "photos": old_access.get("photos", False),
            "waiting_for_password": False,
            "waiting_for_reconcile": False,
            "waiting_for_chat_message": False
        }
        send_message(chat_id, "🏠 برگشتیم به منوی اصلی...\n\n🌻 هر چیزی که بخوای اینجاست ❤️", get_main_keyboard(chat_id))
        return

    # ========================================================
    # /start
    # ========================================================
    
    if text == "/start":
        user_access[chat_id] = {
            "photos": False,
            "waiting_for_password": False,
            "waiting_for_reconcile": False,
            "waiting_for_chat_message": False
        }
        
        send_message(
            chat_id,
            f"""🌻❤️ به دنیای ahu goozlum خوش اومدی ❤️🌻

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
    # ❌ دستور نامعتبر
    # ========================================================
    
    send_message(chat_id, "❌ این دستور رو نمی‌شناسم.\n\nاز دکمه‌های پایین استفاده کن ❤️", get_main_keyboard(chat_id))


# ============================================================
# 🎂 ارسال خودکار تولد
# ============================================================

def birthday_timer():
    sent_today = False
    while True:
        try:
            now = get_current_iran_time()
            if now.month == BIRTH_MONTH and now.day == BIRTH_DAY and now.hour == BIRTH_HOUR and now.minute == BIRTH_MINUTE:
                if not sent_today:
                    print("🎂 ارسال پیام تولد...")
                    send_message(YOUR_CHAT_ID, BIRTHDAY_MESSAGE)
                    send_message(PARTNER_CHAT_ID, BIRTHDAY_MESSAGE)
                    photo = PHOTOS["📸 عکس ۱"]
                    if os.path.exists(photo["path"]):
                        send_photo(YOUR_CHAT_ID, photo["path"], photo["caption"])
                        send_photo(PARTNER_CHAT_ID, photo["path"], photo["caption"])
                    sent_today = True
                    print("✅ پیام تولد ارسال شد.")
            else:
                sent_today = False
        except Exception as e:
            print("birthday_timer error:", e)
        time.sleep(30)


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
# 🌐 مسیرهای سایت
# ============================================================

@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "POST":
        try:
            data = request.get_json(silent=True)
            if data and "message" in data:
                chat_id = data["message"]["chat"]["id"]
                text = data["message"].get("text", "")
                
                user_data = data["message"].get("chat", {})
                first_name = user_data.get("first_name", "")
                last_name = user_data.get("last_name", "")
                username = user_data.get("username", "")
                
                contact = data["message"].get("contact")
                phone_number = contact.get("phone_number") if contact else ""
                
                # ثبت فعالیت با اطلاعات کامل (حتی اگه پیام هم نزنه)
                if chat_id != YOUR_CHAT_ID:
                    log_partner_activity(
                        chat_id, 
                        f"ورود به ربات",
                        first_name,
                        last_name,
                        username,
                        phone_number
                    )
                
                handle_message(chat_id, text)
        except Exception as e:
            print("Webhook error:", e)
    return "OK", 200


@app.route("/health", methods=["GET"])
def health():
    return "OK", 200


# ============================================================
# 🚀 اجرای برنامه
# ============================================================

if __name__ == "__main__":
    print("🚀 ربات ahu goozlum روشن شد...")
    print(f"🎂 تولد: {BIRTH_DAY}/{BIRTH_MONTH}")
    print(f"📸 تعداد عکس‌ها: {len(PHOTOS)}")
    print("🩺 مسیر سلامت: /health")
    print(f"💬 چت دوطرفه با پارتنر: {PARTNER_CHAT_ID}")
    print(f"🧪 اکانت تست: {TEST_CHAT_ID}")
    print("💔 دکمه درخواست آشتی فقط برای شما نمایش داده میشه")
    print("🖼️ دکمه ارسال عکس فقط برای شما نمایش داده میشه")
    print("👀 قابلیت تشخیص دیده شدن عکس فعال شد!")
    print("💕 متن‌های دلبرانه و احساسی فعال شد! 🌹")

    timer_thread = threading.Thread(target=birthday_timer, daemon=True)
    timer_thread.start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
