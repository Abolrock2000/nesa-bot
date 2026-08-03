from flask import Flask, request
import requests
import json
import random
import datetime
import os
import threading
import time

app = Flask(__name__)

TOKEN = "8967116754:AAFJlNPRH8Cht-8qKo3zEHCJvSX1JrBGGXQ"

YOUR_CHAT_ID = "1228473012"

BIRTH_DAY = 8
BIRTH_MONTH = 8

# ============================================================
# ===== عکس‌ها =====
# ============================================================
PHOTOS = {
    "عکس ۱": "photos/khode.nesa_14041113_110733733.jpg",
    "عکس ۲": "photos/khode.nesa_14041205_130846539.jpg",
    "عکس ۳": "photos/IMG_20260719_211523_837.jpg",
    "عکس ۴": "photos/IMG_20260719_211518_014.jpg",
    "عکس ۵": "photos/d36a8351-535-48d8-ad8b-ea78d54eff7e.jpg",
    "عکس ۶": "photos/IMG_20260723_132713_292.jpg",
}

# ============================================================
# ===== اشعار =====
# ============================================================

HAIR_POEMS = [
    """🌸 **موهایت، شبِ شعرِ من است...**

موهایت را که می‌بافم،
انگار که شب را به صبح گره می‌زنم.
هر تارِ مویَت، یک قصه‌ی ناگفته است،
هر پیچِ آن، رازی که فقط من می‌دانم.

🌹 ahu goozlum، موهایت، شاعرانه‌ترین شب‌های من است.""",

    """🌸 **موهایت، قصیده‌ی بی‌تکرار من است...**

هر تار مویت، یک بیت از غزل عشق است،
که شب، آن را با مهتاب می‌خواند.
💫 ahu goozlum، موهایت، قصیده‌ی بی‌تکرارِ من است.""",
]

CHEEK_POEMS = [
    """🌸 **لپ‌هایت، گل‌هایِ بهارِ من است...**

لپ‌هایت را که می‌بینم،
گل‌هایِ سرخِ باغِ بهار در برابرِ تو شرمنده می‌شوند.
هر لپِ تو، یک بوسه‌ی ناگفته است.
🌹 ahu goozlum، لپ‌هایت، گل‌هایِ جاودانه‌ی من است.""",

    """🌸 **لپ‌هایت، سرخ‌ترین غروب من است...**

لپ‌هایت را که می‌بوسم،
انگار که ماه را بوسیده‌ام.
💫 ahu goozlum، لپ‌هایت، روشن‌ترین ستاره‌ی شب‌های من است.""",
]

MOLE_POEMS = [
    """🌸 **خال‌هایت، نقطه‌هایِ عشق است...**

خالِ صورتت را که می‌بینم،
انگار که خدا یک بوسه رویِ زیباترین جایِ صورتت گذاشته است.
هر خالِ تو، یک قصه‌ی عاشقانه است.
🌹 ahu goozlum، خال‌هایت، نقطه‌هایِ بی‌نهایتِ من است.""",

    """🌸 **خالِ صورتت، بوسه‌ی خدا بر زمین است...**

خالِ صورتت را که می‌بینم،
یادِ شبِ عاشقان می‌افتم.
💫 ahu goozlum، خال‌هایت، ستاره‌هایِ راهنمایِ من است.""",
]

LIPS_POEMS = [
    """🌸 **لب‌هایت، شعرِ بی‌نهایتِ من است...**

لب‌هایت را که می‌بینم،
انگار که تمامِ غزل‌هایِ جهان در یک کلمه خلاصه شده است.
لب‌هایت، سرخ‌تر از شفقِ صبح است.
🌹 ahu goozlum، لب‌هایت، جوابِ تمامِ سوالاتِ من است.""",

    """🌸 **لب‌هایت، بوسه‌گاهِ آرزوهای من است...**

لب‌هایت را که می‌بوسم،
انگار که عطرِ بهشت را استشمام کرده‌ام.
💫 ahu goozlum، لب‌هایت، شعرِ بی‌نهایتِ من است.""",
]

EYES_POEMS = [
    """🌸 **چشم‌هایت، عمیق‌ترینِ دریاهاست...**

چشم‌هایت را که می‌بینم،
غرق می‌شوم در نگاهت و دیگر راهِ برگشتی نیست.
چشم‌هایت، عمیق‌تر از دریا است.
🌹 ahu goozlum، چشم‌هایت، آینه‌یِ تمامِ خوبی‌هاست.""",

    """🌸 **چشم‌هایت، روشن‌ترینِ شب‌هایِ من است...**

چشم‌هایت را که می‌بینم،
انگار که تمامِ ستاره‌ها در نگاهت جمع شده‌اند.
💫 ahu goozlum، چشم‌هایت، روشن‌ترینِ شب‌هایِ من است.""",
]

BIRTHDAY_POEMS = [
    """🎂 **تولدت مبارک، ahu goozlum...** 🎂

امروز روزی است که زمین یک ستاره‌ی تازه پیدا کرد.
روزی که آسمان، زیباترین فرشته‌اش را به زمین فرستاد.
🍃 تولدت مبارک، ای زیباترین فصل زندگی من...
❤️ من که همیشه در کنار توام، امروز بیشتر از همیشه دوستت دارم.""",

    """🎂 **تولدت مبارک، ahu goozlum...** 🎂

هر سال که می‌گذرد، عشق من به تو عمیق‌تر می‌شود.
۱۷ مرداد، روزی که خدا تصمیم گرفت زیباترین اثر هنری‌اش را خلق کند...
❤️ تولدت مبارک، ای تمامِ دنیای من...""",
]

FAL_HAFEZ = [
    "🔮 **فال حافظ:**\n\nسحرگه رهروی در سرزمینی\nهمی‌گفت این سخن با انجمنی...\n📖 نیت کن و به دل بسپار...",
    "🔮 **فال حافظ:**\n\nدل می‌رود ز دستم، صاحب دلان خدا را...\n📖 نیت کن و به دل بسپار...",
]

FAL_DAILY = [
    "☀️ **فال روزانه:**\n\nامروز روز خوبی برای شروع کارهای جدید است.\nانرژی مثبت امروز همراه توست.",
    "☀️ **فال روزانه:**\n\nصبور باش و به زمان اعتماد کن.\nفردا روز بهتری خواهد بود.",
]

LOVE_POEMS = [
    "🍃 **شعر عاشقانه:**\n\nخبرت هست که دلتنگ نگاهت شده ام...\n✨ این شعر را برای تو سرودم، ahu goozlum... ❤️",
]

LOVE_STORIES = [
    "📖 **داستان عاشقانه:**\n\nلیلی و مجنون - بخش اول:\nدر میان قبیله‌ی بنی‌عامر...\n📖 ادامه دارد...",
]

LOVE_MESSAGES = [
    "💕 **دل‌نوشته‌ای برای ahu goozlum...**\n\nahu goozlum جان، هر روز که از خواب بیدار می‌شوم، اولین چیزی که به ذهنم می‌رسد، نگاه توست. تو آن رویایی هستی که خدا در گوش باد زمزمه کرد... ❤️",
]

DAILY_MESSAGES = [
    "🌅 صبح بخیر، ahu goozlum... امروز روز خوبی برای توست.",
    "🌙 شب بخیر، ahu goozlum... فردا روز بهتری خواهد بود.",
]

SURPRISES = [
    "🎁 امروز یک بوسه‌ی مجازی از من دریافت کن... 😘",
    "🎁 امروز می‌خوام بگم که عاشقتم... ❤️",
]

LOVE_QUESTIONS = [
    "بهترین خاطره‌ی ما تا الان چی بوده؟",
    "اولین باری که من رو دیدی، چی به ذهنت رسید؟",
]

# ============================================================
# ===== لیست دکمه‌ها =====
# ============================================================
BUTTONS = [
    "🌸 موهای نسا", "🌸 لپ‌های نسا", "🌸 خال‌های صورت نسا",
    "🌸 لب‌های نسا", "🌸 چشم‌های نسا", "📸 عکس‌ها",
    "🎂 تولد نسا", "📅 روز آشنایی", "💞 بازی عاشقانه",
    "🎁 سورپرایز", "💬 پیام روزانه", "💌 دل‌نوشته",
    "💔 وقتی قهر غرور نداره...", "🔙 بازگشت به منو",
    "🔮 فال حافظ", "☀️ فال روزانه",
    "🍃 شعر عاشقانه", "📖 داستان عاشقانه",
]

# ============================================================
# ===== کیبوردها =====
# ============================================================
def get_main_keyboard():
    return {
        "keyboard": [
            ["🌸 موهای نسا", "🌸 لپ‌های نسا"],
            ["🌸 خال‌های صورت نسا", "🌸 لب‌های نسا"],
            ["🌸 چشم‌های نسا", "📸 عکس‌ها"],
            ["🎂 تولد نسا", "📅 روز آشنایی"],
            ["💞 بازی عاشقانه", "🎁 سورپرایز"],
            ["💬 پیام روزانه", "💌 دل‌نوشته"],
            ["🔮 فال حافظ", "☀️ فال روزانه"],
            ["🍃 شعر عاشقانه", "📖 داستان عاشقانه"],
            ["💔 وقتی قهر غرور نداره...", "🔙 بازگشت به منو"]
        ],
        "resize_keyboard": True
    }

def get_photo_keyboard():
    return {
        "keyboard": [
            ["📸 عکس ۱", "📸 عکس ۲", "📸 عکس ۳"],
            ["📸 عکس ۴", "📸 عکس ۵", "📸 عکس ۶"],
            ["🔙 بازگشت به منو"]
        ],
        "resize_keyboard": True
    }

# ============================================================
# ===== توابع ارسال =====
# ============================================================
def send_message(chat_id, text, reply_markup=None):
    urls = [
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        f"https://telegram.dog/bot{TOKEN}/sendMessage",
        f"https://tg.i-c-a.com/bot{TOKEN}/sendMessage",
    ]
    for url in urls:
        try:
            payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
            if reply_markup:
                payload["reply_markup"] = json.dumps(reply_markup)
            r = requests.post(url, data=payload, timeout=10)
            if r.status_code == 200:
                return True
        except:
            continue
    return False

def send_photo(chat_id, photo_path, caption=""):
    urls = [
        f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
        f"https://telegram.dog/bot{TOKEN}/sendPhoto",
        f"https://tg.i-c-a.com/bot{TOKEN}/sendPhoto",
    ]
    for url in urls:
        try:
            with open(photo_path, "rb") as f:
                files = {"photo": f}
                data = {"chat_id": chat_id, "caption": caption}
                r = requests.post(url, data=data, files=files, timeout=20)
                if r.status_code == 200:
                    return True
        except:
            continue
    return False

def get_days_since(day, month, year):
    try:
        today = datetime.datetime.now()
        start = datetime.datetime(year, month, day)
        diff = today - start
        return diff.days
    except:
        return 0

# ============================================================
# ===== پردازش پیام‌ها =====
# ============================================================
def handle_message(chat_id, text):
    text = text.strip()
    
    if text in BUTTONS:
        if text == "🌸 موهای نسا":
            send_message(chat_id, random.choice(HAIR_POEMS))
        elif text == "🌸 لپ‌های نسا":
            send_message(chat_id, random.choice(CHEEK_POEMS))
        elif text == "🌸 خال‌های صورت نسا":
            send_message(chat_id, random.choice(MOLE_POEMS))
        elif text == "🌸 لب‌های نسا":
            send_message(chat_id, random.choice(LIPS_POEMS))
        elif text == "🌸 چشم‌های نسا":
            send_message(chat_id, random.choice(EYES_POEMS))
        elif text == "🎂 تولد نسا":
            send_message(chat_id, random.choice(BIRTHDAY_POEMS))
        elif text == "🔮 فال حافظ":
            send_message(chat_id, random.choice(FAL_HAFEZ))
        elif text == "☀️ فال روزانه":
            send_message(chat_id, random.choice(FAL_DAILY))
        elif text == "🍃 شعر عاشقانه":
            send_message(chat_id, random.choice(LOVE_POEMS))
        elif text == "📖 داستان عاشقانه":
            send_message(chat_id, random.choice(LOVE_STORIES))
        elif text == "📅 روز آشنایی":
            days = get_days_since(24, 12, 1404)
            if days > 0:
                send_message(chat_id, f"💞 **روز آشنایی ما:**\n\n۲۴ اسفند ۱۴۰۴\nالان {days} روز می‌شود که قلبم برای تو می‌تپد... ❤️")
            else:
                send_message(chat_id, "📅 روز آشنایی ما ۲۴ اسفند ۱۴۰۴ است.")
        elif text == "💞 بازی عاشقانه":
            send_message(chat_id, f"💞 **سوال عاشقانه:**\n\n{random.choice(LOVE_QUESTIONS)}\n\nپاسخ خود را برای من بنویس... ❤️")
        elif text == "🎁 سورپرایز":
            send_message(chat_id, random.choice(SURPRISES))
        elif text == "💬 پیام روزانه":
            send_message(chat_id, random.choice(DAILY_MESSAGES))
        elif text == "💌 دل‌نوشته":
            send_message(chat_id, random.choice(LOVE_MESSAGES))
        elif text == "💔 وقتی قهر غرور نداره...":
            send_message(chat_id, "💔 **وقتی قهر غرور نداره...**\n\nahu goozlum، اگه دلت گرفته، هر چی دوست داری برام بنویس...\n💬 من اینجام، بدون غرور، بدون قهر...")
        elif text == "📸 عکس‌ها":
            send_message(chat_id, "📸 کدوم عکس رو می‌خوای ببینی؟", get_photo_keyboard())
        elif text.startswith("📸 عکس"):
            for key, path in PHOTOS.items():
                if text == f"📸 {key}":
                    if os.path.exists(path):
                        send_photo(chat_id, path, f"{key} مخصوص تو... ❤️")
                    else:
                        send_message(chat_id, "عکس پیدا نشد!")
                    break
        elif text == "🔙 بازگشت به منو":
            send_message(chat_id, "به منوی اصلی برگشتی 🏠", get_main_keyboard())
        elif text == "/start":
            send_message(chat_id, 
                "🌸 **به ربات اختصاصی ahu goozlum خوش آمدی!** 🌸\n\n"
                "این ربات فقط برای توست.\n"
                "🌸 دکمه‌های اختصاصی:\n"
                "🌸 موهای نسا\n🌸 لپ‌های نسا\n🌸 خال‌های صورت نسا\n🌸 لب‌های نسا\n🌸 چشم‌های نسا\n"
                "🔮 فال حافظ\n☀️ فال روزانه\n🍃 شعر عاشقانه\n📖 داستان عاشقانه\n\n"
                "🎂 به زودی تولدت...\n"
                "💔 اگر قهر هستی، از دکمه‌ی پایین استفاده کن.",
                get_main_keyboard()
            )
        return
    
    # ===== پیام متنی معمولی =====
    if str(chat_id) != YOUR_CHAT_ID:
        user_message = f"📩 **پیام جدید از ahu goozlum:**\n\n{text}"
        send_message(YOUR_CHAT_ID, user_message)
        send_message(chat_id, "💌 پیامت رو خوندم، ahu goozlum...\n\nبه زودی جوابت رو می‌دم ❤️")
    else:
        send_message(chat_id, "🔹 برای استفاده از ربات، لطفاً از دکمه‌ها استفاده کنید.", get_main_keyboard())

# ============================================================
# ===== تایمر تولد =====
# ============================================================
def birthday_timer():
    while True:
        try:
            now = datetime.datetime.now()
            if now.month == BIRTH_MONTH and now.day == BIRTH_DAY and now.hour == 0 and now.minute == 0:
                print("🎂 امروز تولد ahu goozlum است! ارسال پیام...")
                birthday_message = random.choice(BIRTHDAY_POEMS)
                send_message(YOUR_CHAT_ID, birthday_message)
                photo_path = PHOTOS["عکس ۱"]
                if os.path.exists(photo_path):
                    send_photo(YOUR_CHAT_ID, photo_path, "📸 این عکس مخصوص تولدته، ahu goozlum... ❤️")
                print("✅ پیام و عکس تولد ارسال شد!")
                time.sleep(86400)
        except Exception as e:
            print(f"Error in birthday_timer: {e}")
        time.sleep(60)

# ============================================================
# ===== Webhook (با GET و POST) =====
# ============================================================
@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        try:
            data = request.get_json()
            if data and "message" in data:
                chat_id = data["message"]["chat"]["id"]
                text = data["message"].get("text", "")
                handle_message(chat_id, text)
        except Exception as e:
            print(f"Error: {e}")
    return "OK", 200

# ============================================================
# ===== اجرای اصلی =====
# ============================================================
if __name__ == "__main__":
    print("🚀 ربات ahu goozlum با Webhook روشن شد...")
    print(f"🎂 تولد: {BIRTH_DAY}/{BIRTH_MONTH} (۱۷ مرداد)")
    print(f"📸 تعداد عکس‌ها: {len(PHOTOS)}")
    
    timer_thread = threading.Thread(target=birthday_timer, daemon=True)
    timer_thread.start()
    
    app.run(host='0.0.0.0', port=10000, debug=False)
