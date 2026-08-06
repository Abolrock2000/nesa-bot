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

# ============================================================
# ===== صفحه فتوموزاییک عشق (چهره‌ی نساء با i love you) =====
# ============================================================
PHOTO_MOSAIC_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>❤️ I Love You - Ahu Goozlum ❤️</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            background: #0a0a0a;
            overflow: hidden;
        }
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background: #0a0a0a;
        }
        canvas {
            display: block;
            max-width: 100vw;
            max-height: 100vh;
            width: auto;
            height: auto;
        }
        .watermark {
            position: fixed;
            bottom: 20px;
            left: 0;
            right: 0;
            text-align: center;
            color: #ff224488;
            font-family: 'Arial', sans-serif;
            font-size: 14px;
            letter-spacing: 3px;
            pointer-events: none;
            z-index: 10;
            text-shadow: 0 0 20px #ff2244;
        }
    </style>
</head>
<body>
    <canvas id="photoCanvas"></canvas>
    <div class="watermark">❤️ ahu goozlum ❤️</div>
    <script>
        const text = "i love you";
        const textSize = 12;
        const cols = 90;
        const rows = 65;

        // ===== عکس نساء (لینک یا مسیر) =====
        // می‌تونی از لینک عکس استفاده کنی یا از فایل داخل پروژه
        const imageUrl = "/photos/IMG_20260801_224828_501.jpg";

        const canvas = document.getElementById('photoCanvas');
        const ctx = canvas.getContext('2d');

        const img = new Image();
        img.crossOrigin = "Anonymous";
        img.src = imageUrl;

        img.onload = function() {
            const imgWidth = img.width;
            const imgHeight = img.height;
            const aspectRatio = imgWidth / imgHeight;

            let canvasWidth, canvasHeight;
            if (aspectRatio > 1) {
                canvasWidth = 800;
                canvasHeight = 800 / aspectRatio;
            } else {
                canvasHeight = 600;
                canvasWidth = 600 * aspectRatio;
            }

            canvas.width = canvasWidth;
            canvas.height = canvasHeight;

            ctx.drawImage(img, 0, 0, canvasWidth, canvasHeight);
            const imageData = ctx.getImageData(0, 0, canvasWidth, canvasHeight);
            const data = imageData.data;

            ctx.clearRect(0, 0, canvasWidth, canvasHeight);
            ctx.fillStyle = '#0a0a0a';
            ctx.fillRect(0, 0, canvasWidth, canvasHeight);

            const cellWidth = canvasWidth / cols;
            const cellHeight = canvasHeight / rows;

            for (let row = 0; row < rows; row++) {
                for (let col = 0; col < cols; col++) {
                    const x = col * cellWidth + cellWidth / 2;
                    const y = row * cellHeight + cellHeight / 2;

                    const px = Math.floor(x);
                    const py = Math.floor(y);
                    const idx = (py * canvasWidth + px) * 4;

                    const r = data[idx] || 0;
                    const g = data[idx + 1] || 0;
                    const b = data[idx + 2] || 0;
                    const brightness = (r + g + b) / 3;

                    const fontSize = Math.max(5, (brightness / 255) * textSize);
                    const color = `rgb(${r}, ${g}, ${b})`;

                    ctx.font = `${fontSize}px Arial`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillStyle = color;
                    ctx.fillText(text, x, y);
                }
            }
        };

        img.onerror = function() {
            ctx.fillStyle = '#ff2244';
            ctx.font = '20px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('❌ عکس پیدا نشد! لطفاً مسیر رو چک کن.', canvas.width/2, canvas.height/2);
        };
    </script>
</body>
</html>
"""

def get_main_keyboard():
    return {
        "keyboard": [
            ["📸 عکس‌ها"],
            ["🎂 تولد نسا", "📅 روز آشنایی"],
            ["⏳ ساعت تا تولدت"],
            ["💌 نامه عشق"],
            ["❤️ صفحه عشق"],
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
    
    if text == "❤️ صفحه عشق":
        send_message(chat_id, "❤️ برای دیدن چهره‌ی تو با کلمات عشق، لینک زیر رو باز کن:\nhttps://nesa-bot.onrender.com/love")
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
            "❤️ صفحه عشق: /love",
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

@app.route('/love')
def love_page():
    return render_template_string(PHOTO_MOSAIC_PAGE)

if __name__ == "__main__":
    print("🚀 ربات ahu goozlum با فتوموزاییک عشق روشن شد...")
    print(f"🔑 پسورد: {PASSWORD}")
    print(f"🎂 تولد: {BIRTH_DAY}/{BIRTH_MONTH} (۱۷ مرداد) ساعت {BIRTH_HOUR}:{BIRTH_MINUTE}")
    print(f"📸 تعداد عکس‌ها: {len(PHOTOS)}")
    print("❤️ صفحه عشق در آدرس: /love")
    
    timer_thread = threading.Thread(target=birthday_timer, daemon=True)
    timer_thread.start()
    
    app.run(host='0.0.0.0', port=10000, debug=False)
