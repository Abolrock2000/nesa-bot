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

# ===== پسورد اختصاصی (تاریخ تولد پارتنر) =====
PASSWORD = "1386"  # اینجا تاریخ تولد رو بذار

# ============================================================
# ===== دیکشنری برای ذخیره‌ی وضعیت کاربران =====
# ============================================================
user_access = {}  # {chat_id: {"photos": False, "birthday": False, "meet": False, "timer": False}}

# ============================================================
# ===== عکس‌ها =====
# ============================================================
PHOTOS = {
    "📸 عکس ۱": {"path": "photos/IMG_20260801_224828_501.jpg", "caption": "🌹 عشق زندگیم... ❤️"},
    "📸 عکس ۲": {"path": "photos/null_14041109_222510829.jpg", "caption": "💫 قلب من... تو هستی"},
    "📸 عکس ۳": {"path": "photos/null_14041125_153021650.jpg", "caption": "🌸 بهار زندگی من..."},
    "📸 عکس ۴": {"path": "photos/IMG_20260707_153249_974.jpg", "caption": "🌙 ماه شب‌های من..."},
    "📸 عکس ۵": {"path": "photos/IMG_20260709_234307_968.jpg", "caption": "☀️ روشن‌ترین روز من..."},
    "📸 عکس ۶": {"path": "photos/IMG_20260719_211523_837.jpg", "caption": "❤️ تمامِ دنیای من..."},
}

# ============================================================
# ===== پیام تولد =====
# ============================================================
BIRTHDAY_MESSAGE = """🎂 **تولدت مبارک، ahu goozlum...** 🎂

امروز روزی است که زمین یک ستاره‌ی تازه پیدا کرد.
روزی که آسمان، زیباترین فرشته‌اش را به زمین فرستاد.

🍃 تولدت مبارک، ای زیباترین فصل زندگی من...
❤️ من که همیشه در کنار توام، امروز بیشتر از همیشه دوستت دارم.

🌹 عشق من، تمام هستی من... همیشه مال منی.
💫 به امید سال‌هایی پر از عشق، لبخند و آرامش..."""

# ============================================================
# ===== کیبوردها =====
# ============================================================
def get_main_keyboard():
    return {
        "keyboard": [
            ["📸 عکس‌ها"],
            ["🎂 تولد نسا", "📅 روز آشنایی"],
            ["⏳ تا تولدت"],
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

# ============================================================
# ===== توابع =====
# ============================================================
def days_until_birthday():
    today = datetime.datetime.now()
    birth = datetime.datetime(today.year, BIRTH_MONTH, BIRTH_DAY, BIRTH_HOUR, BIRTH_MINUTE)
    if today > birth:
        birth = datetime.datetime(today.year + 1, BIRTH_MONTH, BIRTH_DAY, BIRTH_HOUR, BIRTH_MINUTE)
    diff = birth - today
    return diff

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
        today = datetime.datetime.now()
        start = datetime.datetime(year, month, day)
        diff = today - start
        return diff.days
    except:
        return 0

# ============================================================
# ===== پردازش پیام‌ها با پسورد =====
# ============================================================
def handle_message(chat_id, text):
    text = text.strip()
    chat_id = str(chat_id)
    
    # ===== اگر کاربر در حالت وارد کردن پسورد است =====
    if user_access.get(chat_id, {}).get("waiting_for_password"):
        if text == PASSWORD:
            user_access[chat_id]["photos"] = True
            user_access[chat_id]["waiting_for_password"] = False
            send_message(chat_id, "✅ دسترسی به عکس‌ها باز شد! عکس مورد نظر رو انتخاب کن.", get_photo_keyboard())
        else:
            send_message(chat_id, "❌ پسورد اشتباه است! دوباره تلاش کن.", get_password_keyboard())
        return
    
    # ===== عکس‌ها =====
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
    
    # ===== تولد =====
    if text == "🎂 تولد نسا":
        send_message(chat_id, BIRTHDAY_MESSAGE)
        return
    
    # ===== روز آشنایی =====
    if text == "📅 روز آشنایی":
        days = get_days_since(24, 12, 1404)
        if days > 0:
            hours = days * 24
            send_message(chat_id, f"💞 **روز آشنایی ما:**\n\n۲۴ اسفند ۱۴۰۴\nالان {hours} ساعت می‌شود که قلبم برای تو می‌تپد... ❤️")
        else:
            send_message(chat_id, "📅 روز آشنایی ما ۲۴ اسفند ۱۴۰۴ است.")
        return
    
    # ===== تا تولدت =====
    if text == "⏳ تا تولدت":
        diff = days_until_birthday()
        days = diff.days
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        send_message(chat_id, f"🎂 تا تولد ahu goozlum، {days} روز و {hours} ساعت و {minutes} دقیقه مونده... ❤️")
        return
    
    # ===== بازگشت به منو =====
    if text == "🔙 بازگشت به منو":
        user_access[chat_id] = {"photos": user_access.get(chat_id, {}).get("photos", False), "waiting_for_password": False}
        send_message(chat_id, "به منوی اصلی برگشتی 🏠", get_main_keyboard())
        return
    
    # ===== استارت =====
    if text == "/start":
        user_access[chat_id] = {"photos": False, "waiting_for_password": False}
        send_message(chat_id, 
            "🌸 **به ربات اختصاصی ahu goozlum خوش آمدی!** 🌸\n\n"
            "📸 برای دیدن عکس‌ها، دکمه‌ی «عکس‌ها» رو بزن و پسورد رو وارد کن.\n"
            "🎂 تولدت رو هم می‌تونی ببینی.\n"
            "⏳ تعداد روزهای باقی‌مونده تا تولدت رو چک کن.\n"
            "❤️ صفحه قلب: /heart",
            get_main_keyboard()
        )
        return
    
    # ===== دستور نامعتبر =====
    send_message(chat_id, "❌ دستور نامعتبر! لطفاً از دکمه‌ها استفاده کن.", get_main_keyboard())

# ============================================================
# ===== تایمر تولد =====
# ============================================================
def birthday_timer():
    while True:
        try:
            now = datetime.datetime.now()
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

# ============================================================
# ===== اجرای اصلی =====
# ============================================================
if __name__ == "__main__":
    print("🚀 ربات ahu goozlum با پسورد برای عکس‌ها روشن شد...")
    print(f"🔑 پسورد: {PASSWORD}")
    print(f"🎂 تولد: {BIRTH_DAY}/{BIRTH_MONTH} (۱۷ مرداد) ساعت {BIRTH_HOUR}:{BIRTH_MINUTE}")
    print(f"📸 تعداد عکس‌ها: {len(PHOTOS)}")
    print("❤️ صفحه قلب در آدرس: /heart")
    
    timer_thread = threading.Thread(target=birthday_timer, daemon=True)
    timer_thread.start()
    
    app.run(host='0.0.0.0', port=10000, debug=False)
