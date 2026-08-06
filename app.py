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
BIRTH_HOUR = 0
BIRTH_MINUTE = 0

IRAN_OFFSET = datetime.timedelta(hours=3, minutes=30)

def get_current_iran_time():
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    iran_time = utc_now.astimezone(datetime.timezone(IRAN_OFFSET))
    return iran_time

PASSWORD = "1386"

user_access = {}

PHOTOS = {
    "📸 عکس ۱": {"path": "photos/IMG_20260801_224828_501.jpg", "caption": "🌹 عشق زندگیم... ❤️"},
    "📸 عکس ۲": {"path": "photos/null_14041109_222510829.jpg", "caption": "💫 قلب من... تو هستی"},
    "📸 عکس ۳": {"path": "photos/null_14041125_153021650.jpg", "caption": "🌸 بهار زندگی من..."},
    "📸 عکس ۴": {"path": "photos/IMG_20260707_153249_974.jpg", "caption": "🌙 ماه شب‌های من..."},
    "📸 عکس ۵": {"path": "photos/IMG_20260709_234307_968.jpg", "caption": "☀️ روشن‌ترین روز من..."},
    "📸 عکس ۶": {"path": "photos/IMG_20260719_211523_837.jpg", "caption": "❤️ تمامِ دنیای من..."},
}

BIRTHDAY_MESSAGE = """🎂 **تولدت مبارک، ahu goozlum...** 🎂

امروز روزی است که زمین یک ستاره‌ی تازه پیدا کرد.
روزی که آسمان، زیباترین فرشته‌اش را به زمین فرستاد.

🍃 تولدت مبارک، ای زیباترین فصل زندگی من...
❤️ من که همیشه در کنار توام، امروز بیشتر از همیشه دوستت دارم.

🌹 عشق من، تمام هستی من... همیشه مال منی.
💫 به امید سال‌هایی پر از عشق، لبخند و آرامش..."""

SECOND_QUOTES = [
    "هر ثانیه‌ای که می‌گذرد، عشق من به تو عمیق‌تر می‌شود... ❤️",
    "ثانیه‌ها می‌گذرند، اما عشق من به تو هرگز کهنه نمی‌شود... 🌹",
    "در هر ثانیه‌ای از زندگی‌ام، تو را نفس می‌کشم... 💫",
    "ثانیه‌های بی‌تو، مثل قرن‌ها می‌گذرند... اما با تو، حتی ثانیه‌ها هم جاودانه‌اند... ✨",
    "هر ثانیه که می‌گذرد، یک دلیل تازه برای دوست داشتن تو پیدا می‌کنم... ❤️",
    "ثانیه‌ها را بشمار، اما عشق را نه... چون عشق من به تو بی‌نهایت است... 🌸",
]

LOVE_LETTERS = [
    """💌 **نامه عشق شماره ۱**

ahu goozlum,

نمی‌دونم از کجا شروع کنم...
شاید از لحظه‌ای که چشمات رو دیدم و فهمیدم که به چی بودم منتظر.

تو نه فقط عشق من، تو معنایِ زندگی‌ام... 🌹

همه چیز قبل از تو، سیاه و سفید بود.
اما تو رنگ‌های بی‌نهایت به زندگی‌ام اضافه کردی.

با تمام وجودم، تو را دوست دارم.

♾️ برای همیشه،
❤️ قلب تنهای تو""",
    
    """💌 **نامه عشق شماره ۲**

به تو، زیباترین اتفاق زندگی‌ام

هر روز بدون تو، یک سال است.
هر لحظه با تو، یک جاویدانگی است.

قلب من یک سرود ابدی برای تو است...

🌸 تو شکوفایی بهار روح‌ام.
☀️ تو نور روزهای تاریک‌ام.
🌙 تو آرامش شب‌های سرگردان‌ام.

دوستت دارم... بیشتر از خودم...

❤️ همیشه مال توام""",

    """💌 **نامه عشق شماره ۳**

نسا،

تو می‌دونی که من چند تا کلمه برای بیان احساساتم دارم...
اما هر بار که سعی می‌کنم، کلمات کمی می‌آن...

چون عشق من به تو، بیشتر از هر زبانی است.

هر لحظه با تو، برکت دارد.
هر نگاه به چشمات، معجزه‌است.
هر لمس دستت، خاک طلا برای روح‌ام...

🌹 تو داستان جاویدانی است که می‌خوام برایش زنده بمونم.
💫 تو خواب شیرینی است که می‌ترسم بیدار شوم.
❤️ تو تنها علت ضربان قلب‌ام...

با بی‌کرانِ عشق،
روح تنهای تو""",
]

def get_main_keyboard():
    return {
        "keyboard": [
            ["📸 عکس‌ها"],
            ["🎂 تولد نسا", "📅 روز آشنایی"],
            ["⏳ ساعت تا تولدت"],
            ["💌 نامه عشق"],
            ["❤️ صفحه قلب"],
            ["🔙 بازگشت به منو"]
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

def get_password_keyboard():
    return {
        "keyboard": [
            ["🔙 بازگشت به منو"]
        ],
        "resize_keyboard": True
    }

def hours_until_birthday():
    now = get_current_iran_time()
    birth = datetime.datetime(now.year, BIRTH_MONTH, BIRTH_DAY, BIRTH_HOUR, BIRTH_MINUTE)
    birth = birth.replace(tzinfo=datetime.timezone(IRAN_OFFSET))
    if now > birth:
        birth = datetime.datetime(now.year + 1, BIRTH_MONTH, BIRTH_DAY, BIRTH_HOUR, BIRTH_MINUTE)
        birth = birth.replace(tzinfo=datetime.timezone(IRAN_OFFSET))
    diff = birth - now
    return int(diff.total_seconds() // 3600)

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
        send_message(chat_id, "❌ عکس پیدا نشد!")
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
        now = get_current_iran_time()
        start = datetime.datetime(year, month, day, tzinfo=datetime.timezone(IRAN_OFFSET))
        diff = now - start
        return diff.days
    except:
        return 0

def handle_message(chat_id, text):
    text = text.strip()
    chat_id = str(chat_id)
    
    if user_access.get(chat_id, {}).get("waiting_for_password"):
        if text == PASSWORD:
            user_access[chat_id]["photos"] = True
            user_access[chat_id]["waiting_for_password"] = False
            send_message(chat_id, "✅ دسترسی به عکس‌ها باز شد!", get_photo_keyboard())
        else:
            send_message(chat_id, "❌ پسورد اشتباه است! دوباره تلاش کن.", get_password_keyboard())
        return
    
    if text in ["📸 عکس ۱", "📸 عکس ۲", "📸 عکس ۳", "📸 عکس ۴", "📸 عکس ۵", "📸 عکس ۶"]:
        if user_access.get(chat_id, {}).get("photos", False):
            photo = PHOTOS.get(text)
            if photo:
                send_photo(chat_id, photo["path"], photo["caption"])
            else:
                send_message(chat_id, "عکس پیدا نشد!")
        else:
            send_message(chat_id, "🔒 برای دیدن عکس‌ها، ابتدا پسورد رو وارد کن.", get_password_keyboard())
        return
    
    if text == "📸 عکس‌ها":
        if user_access.get(chat_id, {}).get("photos", False):
            send_message(chat_id, "📸 کدوم عکس رو می‌خوای ببینی؟", get_photo_keyboard())
        else:
            user_access[chat_id] = user_access.get(chat_id, {})
            user_access[chat_id]["waiting_for_password"] = True
            send_message(chat_id, "🔒 لطفاً پسورد رو وارد کن:", get_password_keyboard())
        return
    
    if text == "🎂 تولد نسا":
        send_message(chat_id, BIRTHDAY_MESSAGE)
        return
    
    if text == "📅 روز آشنایی":
        days = get_days_since(24, 12, 1404)
        if days > 0:
            seconds = days * 24 * 60 * 60
            quote = random.choice(SECOND_QUOTES)
            send_message(chat_id, 
                f"💞 **روز آشنایی ما:**\n\n"
                f"۲۴ اسفند ۱۴۰۴، روزی که قلبم برای تو تپیدن را آغاز کرد.\n\n"
                f"از آن روز تا امروز، دقیقاً **{seconds:,} ثانیه** می‌گذرد...\n"
                f"و در تمام این ثانیه‌ها، قلبم فقط برای تو می‌تپد.\n\n"
                f"📖 {quote}\n\n"
                f"❤️ هر ثانیه‌اش، یک نفس عشق بود..."
            )
        else:
            send_message(chat_id, "📅 روز آشنایی ما ۲۴ اسفند ۱۴۰۴ است.")
        return
    
    if text == "⏳ ساعت تا تولدت":
        hours = hours_until_birthday()
        send_message(chat_id, f"🎂 تا تولد ahu goozlum، {hours:,} ساعت مونده... ❤️")
        return
    
    if text == "💌 نامه عشق":
        send_message(chat_id, random.choice(LOVE_LETTERS))
        return
    
    if text == "❤️ صفحه قلب":
        send_message(chat_id, "❤️ برای دیدن صفحه قلب، لینک زیر رو باز کن:\nhttps://nesa-bot.onrender.com/heart")
        return
    
    if text == "🔙 بازگشت به منو":
        user_access[chat_id] = {"photos": user_access.get(chat_id, {}).get("photos", False), "waiting_for_password": False}
        send_message(chat_id, "به منوی اصلی برگشتی 🏠", get_main_keyboard())
        return
    
    if text == "/start":
        user_access[chat_id] = {"photos": False, "waiting_for_password": False}
        send_message(chat_id, 
            "🌸 **به ربات اختصاصی ahu goozlum خوش آمدی!** 🌸\n\n"
            "📸 برای دیدن عکس‌ها، دکمه‌ی «عکس‌ها» رو بزن و پسورد رو وارد کن.\n"
            "🎂 تولدت رو هم می‌تونی ببینی.\n"
            "⏳ ساعت باقی‌مونده تا تولدت رو چک کن.\n"
            "💌 نامه‌های عاشقانه رو هم می‌تونی بخونی.\n"
            "❤️ صفحه قلب: /heart",
            get_main_keyboard()
        )
        return
    
    send_message(chat_id, "❌ دستور نامعتبر! لطفاً از دکمه‌ها استفاده کن.", get_main_keyboard())

def birthday_timer():
    while True:
        try:
            now = get_current_iran_time()
            if (now.month == BIRTH_MONTH and 
                now.day == BIRTH_DAY and 
                now.hour == BIRTH_HOUR and 
                now.minute == BIRTH_MINUTE):
                
                print("🎂 امروز تولد ahu goozlum است! ارسال پیام...")
                send_message(YOUR_CHAT_ID, BIRTHDAY_MESSAGE)
                photo = PHOTOS["📸 عکس ۱"]
                if os.path.exists(photo["path"]):
                    send_photo(YOUR_CHAT_ID, photo["path"], photo["caption"])
                print("✅ پیام و عکس تولد ارسال شد!")
                time.sleep(86400)
        except Exception as e:
            print(f"Error in birthday_timer: {e}")
        time.sleep(60)

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

@app.route('/heart')
def heart_page():
    return render_template_string("""
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
        <div class="center-text">❤️ ahu goozlum ❤️<span>i love you forever</span></div>
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
    """)

if __name__ == "__main__":
    print("🚀 ربات ahu goozlum با تمام ویژگی‌ها روشن شد...")
    print(f"🔑 پسورد: {PASSWORD}")
    print(f"🎂 تولد: {BIRTH_DAY}/{BIRTH_MONTH} (۱۷ مرداد) ساعت {BIRTH_HOUR}:{BIRTH_MINUTE}")
    print(f"📸 تعداد عکس‌ها: {len(PHOTOS)}")
    print("❤️ صفحه قلب در آدرس: /heart")
    
    timer_thread = threading.Thread(target=birthday_timer, daemon=True)
    timer_thread.start()
    
    app.run(host='0.0.0.0', port=10000, debug=False)
