from flask import Flask, request, render_template_string
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
# ===== صفحه قلب =====
# ============================================================
HEART_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>❤️ I Love You - Ahu Goozlum ❤️</title>
    <style>
        * { margin: 0; padding: 0; background: #0a0a0a; overflow: hidden; }
        body { display: flex; justify-content: center; align-items: center; height: 100vh; }
        .heart-wrapper { position: relative; width: 500px; height: 470px; display: flex; justify-content: center; align-items: center; }
        .heart-text { position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; flex-wrap: wrap; justify-content: center; align-content: center; gap: 2px; padding: 30px 20px; }
        .word { color: #ff2244; font-family: 'Arial', sans-serif; font-size: 12px; font-weight: bold; text-shadow: 0 0 3px #ff2244, 0 0 8px #ff2244; animation: pulse 2s ease-in-out infinite alternate; user-select: none; white-space: nowrap; }
        @keyframes pulse { 0% { opacity: 0.4; transform: scale(0.85); } 100% { opacity: 1; transform: scale(1.05); } }
        .center-text { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #ff2244; font-family: 'Arial Black', sans-serif; font-size: 34px; font-weight: 900; text-shadow: 0 0 20px #ff2244, 0 0 40px #ff2244, 0 0 60px #ff4466, 0 0 80px #ff6688; z-index: 10; text-align: center; animation: centerPulse 1.5s ease-in-out infinite alternate; letter-spacing: 2px; background: transparent; pointer-events: none; }
        .center-text span { display: block; font-size: 16px; color: #ff6699; font-family: 'Arial', sans-serif; font-weight: normal; text-shadow: 0 0 10px #ff6699, 0 0 20px #ff6699; margin-top: 5px; }
        @keyframes centerPulse { 0% { transform: translate(-50%, -50%) scale(0.95); text-shadow: 0 0 20px #ff2244, 0 0 40px #ff2244; } 100% { transform: translate(-50%, -50%) scale(1.05); text-shadow: 0 0 30px #ff2244, 0 0 60px #ff4466, 0 0 80px #ff6688; } }
        @media (max-width: 550px) { .heart-wrapper { width: 320px; height: 300px; } .word { font-size: 8px; } .center-text { font-size: 22px; } .center-text span { font-size: 12px; } }
    </style>
</head>
<body>
    <div class="heart-wrapper">
        <div class="heart-text" id="heartText"></div>
        <div class="center-text">
            ❤️ ahu goozlum ❤️
            <span>i love you forever</span>
        </div>
    </div>
    <script>
        const container = document.getElementById('heartText');
        const text = "i love you";
        function isInsideHeart(x, y) {
            const scale = 0.065;
            const nx = x * scale;
            const ny = y * scale;
            const a = nx * nx + ny * ny - 1;
            return a * a * a - nx * nx * ny * ny * ny <= 0;
        }
        const rows = 32, cols = 28;
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const x = (col / cols) * 2 - 1;
                const y = (row / rows) * 2 - 1;
                if (isInsideHeart(x, y)) {
                    const word = document.createElement('span');
                    word.className = 'word';
                    word.textContent = text;
                    word.style.fontSize = `${9 + Math.random() * 6}px`;
                    word.style.animationDelay = `${Math.random() * 3}s`;
                    word.style.opacity = 0.5 + Math.random() * 0.5;
                    container.appendChild(word);
                }
            }
        }
    </script>
</body>
</html>
"""

# ============================================================
# ===== عکس‌ها با اسم‌های دقیق از لیست شما =====
# ============================================================
PHOTOS = {
    "📸 عکس ۱": "photos/IMG_20260801_224828_501.jpg",
    "📸 عکس ۲": "photos/null_14041109_222510829.jpg",
    "📸 عکس ۳": "photos/null_14041125_153021650.jpg",
    "📸 عکس ۴": "photos/IMG_20260707_153249_974.jpg",
    "📸 عکس ۵": "photos/IMG_20260709_234307_968.jpg",
    "📸 عکس ۶": "photos/IMG_20260719_211523_837.jpg",
}

# ============================================================
# ===== اشعار و محتوا =====
# ============================================================

HAIR_POEMS = [
    """🌸 **موهایت، شبِ شعرِ من است...**
موهایت را که می‌بافم، انگار که شب را به صبح گره می‌زنم.
🌹 ahu goozlum، موهایت، شاعرانه‌ترین شب‌های من است."""
]

CHEEK_POEMS = [
    """🌸 **لپ‌هایت، گل‌هایِ بهارِ من است...**
لپ‌هایت را که می‌بینم، گل‌هایِ سرخِ باغِ بهار در برابرِ تو شرمنده می‌شوند.
🌹 ahu goozlum، لپ‌هایت، گل‌هایِ جاودانه‌ی من است."""
]

MOLE_POEMS = [
    """🌸 **خال‌هایت، نقطه‌هایِ عشق است...**
خالِ صورتت را که می‌بینم، انگار که خدا یک بوسه رویِ زیباترین جایِ صورتت گذاشته است.
🌹 ahu goozlum، خال‌هایت، نقطه‌هایِ بی‌نهایتِ من است."""
]

LIPS_POEMS = [
    """🌸 **لب‌هایت، شعرِ بی‌نهایتِ من است...**
لب‌هایت را که می‌بینم، انگار که تمامِ غزل‌هایِ جهان در یک کلمه خلاصه شده است.
🌹 ahu goozlum، لب‌هایت، جوابِ تمامِ سوالاتِ من است."""
]

EYES_POEMS = [
    """🌸 **چشم‌هایت، عمیق‌ترینِ دریاهاست...**
چشم‌هایت را که می‌بینم، غرق می‌شوم در نگاهت و دیگر راهِ برگشتی نیست.
🌹 ahu goozlum، چشم‌هایت، آینه‌یِ تمامِ خوبی‌هاست."""
]

BIRTHDAY_POEMS = [
    """🎂 **تولدت مبارک، ahu goozlum...** 🎂
امروز روزی است که زمین یک ستاره‌ی تازه پیدا کرد.
روزی که آسمان، زیباترین فرشته‌اش را به زمین فرستاد.
🍃 تولدت مبارک، ای زیباترین فصل زندگی من...
❤️ من که همیشه در کنار توام، امروز بیشتر از همیشه دوستت دارم."""
]

FAL_HAFEZ = [
    "🔮 **فال حافظ:**\n\nسحرگه رهروی در سرزمینی...\n📖 نیت کن و به دل بسپار...",
]

FAL_DAILY = [
    "☀️ **فال روزانه:**\n\nامروز روز خوبی برای شروع کارهای جدید است.",
]

LOVE_POEMS = [
    "🍃 **شعر عاشقانه:**\n\nخبرت هست که دلتنگ نگاهت شده ام...\n✨ این شعر را برای تو سرودم، ahu goozlum... ❤️",
]

LOVE_STORIES = [
    "📖 **داستان عاشقانه:**\n\nلیلی و مجنون - بخش اول:\nدر میان قبیله‌ی بنی‌عامر...\n📖 ادامه دارد...",
]

LOVE_MESSAGES = [
    "💕 **دل‌نوشته‌ای برای ahu goozlum...**\n\nahu goozlum جان، هر روز که از خواب بیدار می‌شوم، اولین چیزی که به ذهنم می‌رسد، نگاه توست... ❤️",
]

DAILY_MESSAGES = [
    "🌅 صبح بخیر، ahu goozlum... امروز روز خوبی برای توست.",
]

SURPRISES = [
    "🎁 امروز یک بوسه‌ی مجازی از من دریافت کن... 😘",
]

LOVE_QUESTIONS = [
    "بهترین خاطره‌ی ما تا الان چی بوده؟",
]

# ============================================================
# ===== لیست کامل دکمه‌ها =====
# ============================================================
BUTTONS = [
    "🌸 موهای نسا",
    "🌸 لپ‌های نسا",
    "🌸 خال‌های صورت نسا",
    "🌸 لب‌های نسa",
    "🌸 چشم‌های نسا",
    "📸 عکس‌ها",
    "📸 عکس ۱",
    "📸 عکس ۲",
    "📸 عکس ۳",
    "📸 عکس ۴",
    "📸 عکس ۵",
    "📸 عکس ۶",
    "🎂 تولد نسا",
    "📅 روز آشنایی",
    "💞 بازی عاشقانه",
    "🎁 سورپرایز",
    "💬 پیام روزانه",
    "💌 دل‌نوشته",
    "💔 وقتی قهر غرور نداره...",
    "🔙 بازگشت به منو",
    "🔮 فال حافظ",
    "☀️ فال روزانه",
    "🍃 شعر عاشقانه",
    "📖 داستان عاشقانه",
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
    if not os.path.exists(photo_path):
        send_message(chat_id, "❌ عکس پیدا نشد! لطفاً مسیر رو چک کن.")
        return False
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
    
    if text in ["📸 عکس ۱", "📸 عکس ２", "📸 عکس ۳", "📸 عکس ۴", "📸 عکس ۵", "📸 عکس ６"]:
        photo_path = PHOTOS.get(text)
        if photo_path:
            send_photo(chat_id, photo_path, f"{text} مخصوص تو... ❤️")
        else:
            send_message(chat_id, "عکس پیدا نشد!")
        return
    
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
        elif text == "🔙 بازگشت به منو":
            send_message(chat_id, "به منوی اصلی برگشتی 🏠", get_main_keyboard())
        elif text == "/start":
            send_message(chat_id, 
                "🌸 **به ربات اختصاصی ahu goozlum خوش آمدی!** 🌸\n\n"
                "🌸 دکمه‌های اختصاصی:\n"
                "🌸 موهای نسا\n🌸 لپ‌های نسا\n🌸 خال‌های صورت نسا\n🌸 لب‌های نسا\n🌸 چشم‌های نسا\n"
                "🔮 فال حافظ\n☀️ فال روزانه\n🍃 شعر عاشقانه\n📖 داستان عاشقانه\n\n"
                "🎂 به زودی تولدت...\n"
                "💔 اگر قهر هستی، از دکمه‌ی پایین استفاده کن.",
                get_main_keyboard()
            )
        return
    
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
                photo_path = PHOTOS["📸 عکس ۱"]
                if os.path.exists(photo_path):
                    send_photo(YOUR_CHAT_ID, photo_path, "📸 این عکس مخصوص تولدته، ahu goozlum... ❤️")
                print("✅ پیام و عکس تولد ارسال شد!")
                time.sleep(86400)
        except Exception as e:
            print(f"Error in birthday_timer: {e}")
        time.sleep(60)

# ============================================================
# ===== Webhook =====
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
# ===== صفحه قلب =====
# ============================================================
@app.route('/heart')
def heart_page():
    return render_template_string(HEART_PAGE)

# ============================================================
# ===== اجرای اصلی =====
# ============================================================
if __name__ == "__main__":
    print("🚀 ربات ahu goozlum با عکس‌های جدید روشن شد...")
    print(f"🎂 تولد: {BIRTH_DAY}/{BIRTH_MONTH} (۱۷ مرداد)")
    print(f"📸 تعداد عکس‌ها: {len(PHOTOS)}")
    print("❤️ صفحه قلب در آدرس: /heart")
    
    timer_thread = threading.Thread(target=birthday_timer, daemon=True)
    timer_thread.start()
    
    app.run(host='0.0.0.0', port=10000, debug=False)
