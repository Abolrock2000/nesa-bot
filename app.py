from flask import Flask, request, render_template_string, send_file
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
    "📸 عکس ۷": {"path": "https://i.postimg.cc/5tDhyRgM/IMG-20260318-184739-714.jpg", "caption": "💖 عکس مخصوص... ❤️"},
}

# ============================================================
# ===== صفحه سورپرایز تولد =====
# ============================================================
BIRTHDAY_SURPRISE_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎉 تبریک برای عشقم - Ahu Goozlum ❤️</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #0a0a0a;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-family: 'Arial', sans-serif;
            overflow: hidden;
            flex-direction: column;
        }
        .container {
            text-align: center;
            padding: 20px;
            max-width: 500px;
            width: 100%;
        }
        #giftBox { cursor: pointer; transition: transform 0.5s; animation: float 3s ease-in-out infinite; }
        #giftBox:hover { transform: scale(1.05); }
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-15px); }
        }
        .gift-img {
            width: 280px;
            height: auto;
            filter: drop-shadow(0 0 30px #ff224466);
            transition: all 0.5s;
        }
        #passwordPage { display: none; animation: fadeIn 0.8s; }
        @keyframes fadeIn {
            from { opacity: 0; transform: scale(0.9); }
            to { opacity: 1; transform: scale(1); }
        }
        .password-box {
            background: #1a1a1a;
            padding: 40px 30px;
            border-radius: 20px;
            border: 2px solid #ff224488;
            box-shadow: 0 0 50px #ff224422;
        }
        .password-box h2 { color: #ff2244; font-size: 22px; margin-bottom: 15px; text-shadow: 0 0 20px #ff2244; }
        .password-box p { color: #ff6699; font-size: 14px; margin-bottom: 20px; }
        .password-box input {
            width: 100%;
            padding: 14px;
            background: #0a0a0a;
            border: 2px solid #ff224466;
            border-radius: 12px;
            color: #fff;
            font-size: 18px;
            text-align: center;
            outline: none;
            transition: 0.3s;
        }
        .password-box input:focus { border-color: #ff2244; box-shadow: 0 0 20px #ff224466; }
        .password-box button {
            margin-top: 20px;
            padding: 14px 40px;
            background: linear-gradient(45deg, #ff2244, #ff4466);
            border: none;
            border-radius: 30px;
            color: #fff;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.3s;
            box-shadow: 0 0 30px #ff224466;
        }
        .password-box button:hover { transform: scale(1.05); box-shadow: 0 0 50px #ff224488; }
        .error-msg { color: #ff2244; margin-top: 12px; font-size: 14px; display: none; }
        #birthdayPage { display: none; animation: fadeIn 1.2s; }
        .birthday-content {
            background: #1a1a1a;
            padding: 30px 20px;
            border-radius: 20px;
            border: 2px solid #ff224488;
            box-shadow: 0 0 60px #ff224422;
        }
        .birthday-content h1 { color: #ff2244; font-size: 28px; text-shadow: 0 0 30px #ff2244; margin-bottom: 10px; }
        .birthday-content .message { color: #ff6699; font-size: 16px; line-height: 1.8; margin: 15px 0; }
        .birthday-content .message span { color: #ff2244; font-weight: bold; }
        .birthday-photo {
            width: 100%;
            max-width: 350px;
            border-radius: 16px;
            margin: 15px auto;
            display: block;
            border: 3px solid #ff224466;
            box-shadow: 0 0 40px #ff224422;
        }
        .heart-rain { position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 999; }
        .heart-rain span {
            position: absolute;
            font-size: 24px;
            animation: fall linear infinite;
            opacity: 0.8;
        }
        @keyframes fall {
            0% { transform: translateY(-10vh) rotate(0deg); opacity: 1; }
            100% { transform: translateY(110vh) rotate(720deg); opacity: 0; }
        }
        @media (max-width: 500px) {
            .gift-img { width: 200px; }
            .password-box { padding: 25px 20px; }
            .birthday-content h1 { font-size: 22px; }
        }
    </style>
</head>
<body>

    <div class="container" id="giftPage">
        <div id="giftBox" onclick="showPassword()">
            <img src="https://cdn-icons-png.flaticon.com/512/1068/1068649.png" alt="🎁" class="gift-img">
            <p style="color: #ff6699; margin-top: 15px; font-size: 18px; letter-spacing: 2px;">❤️ برای باز کردن، کلیک کن...</p>
        </div>
    </div>

    <div class="container" id="passwordPage">
        <div class="password-box">
            <h2>🔒 کد مخصوص</h2>
            <p>تاریخ تولد عشقم رو وارد کن...</p>
            <input type="password" id="passwordInput" placeholder="مثلاً 1386" maxlength="10">
            <button onclick="checkPassword()">🎉 تبریک</button>
            <div class="error-msg" id="errorMsg">❌ کد اشتباه است! دوباره تلاش کن.</div>
        </div>
    </div>

    <div class="container" id="birthdayPage">
        <div class="birthday-content">
            <h1>🎉 تبریک برای عشقم! ❤️</h1>
            <div class="message">
                امروز روزی است که زمین یک ستاره‌ی تازه پیدا کرد.<br>
                روزی که آسمان، زیباترین فرشته‌اش را به زمین فرستاد.<br><br>
                <span>🍃 تولدت مبارک، ای زیباترین فصل زندگی من...</span><br>
                ❤️ من که همیشه در کنار توام، امروز بیشتر از همیشه دوستت دارم.<br><br>
                🌹 عشق من، تمام هستی من... همیشه مال منی.<br>
                💫 به امید سال‌هایی پر از عشق، لبخند و آرامش...
            </div>
            <img src="https://i.postimg.cc/5tDhyRgM/IMG-20260318-184739-714.jpg" alt="Nesa" class="birthday-photo">
            <p style="color: #ff6699; margin-top: 15px; font-size: 14px;">
                ❤️ این چهره‌ات، با کلمات <span style="color: #ff2244;">I LOVE YOU NESA</span> ساخته شده...
            </p>
        </div>
    </div>

    <div class="heart-rain" id="heartRain"></div>

    <script>
        const CORRECT_PASSWORD = "1386";

        function showPassword() {
            document.getElementById('giftPage').style.display = 'none';
            document.getElementById('passwordPage').style.display = 'block';
            document.getElementById('passwordInput').focus();
        }

        function checkPassword() {
            const input = document.getElementById('passwordInput').value.trim();
            const errorMsg = document.getElementById('errorMsg');

            if (input === CORRECT_PASSWORD) {
                errorMsg.style.display = 'none';
                document.getElementById('passwordPage').style.display = 'none';
                document.getElementById('birthdayPage').style.display = 'block';
                startHeartRain();
                playConfetti();
            } else {
                errorMsg.style.display = 'block';
                document.getElementById('passwordInput').value = '';
                document.getElementById('passwordInput').focus();
                setTimeout(() => { errorMsg.style.display = 'none'; }, 3000);
            }
        }

        function startHeartRain() {
            const container = document.getElementById('heartRain');
            const emojis = ['❤️', '💖', '💕', '💗', '❤️‍🔥', '💘', '🌹', '✨'];
            for (let i = 0; i < 60; i++) {
                const span = document.createElement('span');
                span.textContent = emojis[Math.floor(Math.random() * emojis.length)];
                span.style.left = Math.random() * 100 + '%';
                span.style.fontSize = (14 + Math.random() * 30) + 'px';
                span.style.animationDuration = (4 + Math.random() * 6) + 's';
                span.style.animationDelay = (Math.random() * 5) + 's';
                container.appendChild(span);
            }
        }

        function playConfetti() {
            const colors = ['#ff2244', '#ff6699', '#ff88aa', '#ffffff', '#ffaa00'];
            for (let i = 0; i < 50; i++) {
                const el = document.createElement('div');
                el.style.cssText = `
                    position: fixed;
                    width: 8px;
                    height: 8px;
                    background: ${colors[Math.floor(Math.random() * colors.length)]};
                    left: ${Math.random() * 100}%;
                    top: -10px;
                    border-radius: ${Math.random() > 0.5 ? '50%' : '2px'};
                    z-index: 1000;
                    animation: confettiFall ${2 + Math.random() * 3}s linear forwards;
                    animation-delay: ${Math.random() * 1.5}s;
                    transform: rotate(${Math.random() * 360}deg);
                `;
                document.body.appendChild(el);
                setTimeout(() => el.remove(), 5000);
            }
        }

        const style = document.createElement('style');
        style.textContent = `
            @keyframes confettiFall {
                0% { transform: translateY(0) rotate(0deg); opacity: 1; }
                100% { transform: translateY(110vh) rotate(720deg); opacity: 0; }
            }
        `;
        document.head.appendChild(style);

        document.getElementById('passwordInput').addEventListener('keydown', function(e) {
            if (e.key === 'Enter') { checkPassword(); }
        });
    </script>
</body>
</html>
"""

# ============================================================
# ===== صفحه فتوموزاییک =====
# ============================================================
PHOTO_MOSAIC_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>❤️ I Love You Nesa - Ahu Goozlum ❤️</title>
    <style>
        * { margin: 0; padding: 0; background: #0a0a0a; overflow: hidden; }
        body { display: flex; justify-content: center; align-items: center; height: 100vh; }
        canvas { display: block; max-width: 100vw; max-height: 100vh; width: auto; height: auto; }
        .watermark { position: fixed; bottom: 20px; left: 0; right: 0; text-align: center; color: #ff224488; font-family: 'Arial', sans-serif; font-size: 14px; letter-spacing: 3px; pointer-events: none; z-index: 10; text-shadow: 0 0 20px #ff2244; }
    </style>
</head>
<body>
    <canvas id="photoCanvas"></canvas>
    <div class="watermark">❤️ ahu goozlum ❤️</div>
    <script>
        const imageUrl = "https://i.postimg.cc/5tDhyRgM/IMG-20260318-184739-714.jpg";
        const words = ["I", "LOVE", "YOU", "NESA"];

        const canvas = document.getElementById("photoCanvas");
        const ctx = canvas.getContext("2d");

        const img = new Image();
        img.crossOrigin = "anonymous";
        img.src = imageUrl;

        img.onload = () => {
            canvas.width = img.width;
            canvas.height = img.height;

            ctx.drawImage(img, 0, 0);

            const pixels = ctx.getImageData(0, 0, canvas.width, canvas.height).data;

            ctx.fillStyle = "#000";
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.font = "7px Arial";

            const step = 7;

            for (let y = 0; y < canvas.height; y += step) {
                for (let x = 0; x < canvas.width; x += step) {
                    let index = (y * canvas.width + x) * 4;

                    let r = pixels[index];
                    let g = pixels[index + 1];
                    let b = pixels[index + 2];

                    let bright = (r + g + b) / 3;

                    if (bright > 240) continue;

                    ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;

                    let word = words[(x + y) % words.length];

                    ctx.fillText(word, x, y);
                }
            }
        };

        img.onerror = () => {
            ctx.fillStyle = '#ff2244';
            ctx.font = '20px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('❌ عکس پیدا نشد! لینک رو چک کن.', canvas.width/2, canvas.height/2);
        };
    </script>
</body>
</html>
"""

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

# ============================================================
# ===== نامه‌های عاشقانه (انگار خودت نوشتی) =====
# ============================================================
LOVE_LETTERS = [
    """💌 **نامه‌ای از دل من...**

نسای من،
اگر تو را با تمام زیبایی‌های جهان مقایسه کنم، از همه دلپذیرتری.
گرما و زیبایی تو، هرگز رنگ نمی‌بازد،
و در نگاهت، چیزی هست که جاودانه می‌ماند.
هر بار که به تو فکر می‌کنم، دنیا برایم زیباتر می‌شود.
دوستت دارم، نه برای امروز، که برای همیشه.
هر ضربان قلبم، یک بیت از عشق توست.
هر نگاهم، یک غزل.
و هر لحظه‌ای که بی‌تو می‌گذرد، یک فصل بی‌معناست.
❤️""",

    """💌 **نامه‌ای از دل من...**

ای نسا، ای زیباترین اتفاق زندگی‌ام،
دلم هر روز پر از تو می‌شود،
و هر شب، خوابت را می‌بینم.
اگر روزی از من بپرسند که عشق یعنی چه،
فقط نگاهت را نشانشان می‌دهم.
در این دنیای شلوغ،
تنها تو را برای همیشه انتخاب کرده‌ام.
با تو، حتی ساده‌ترین لحظات هم به یادماندنی‌ترین‌هاست.
و بدون تو، همه‌چیز بی‌رنگ است.
🌹""",

    """💌 **نامه‌ای از دل من...**

نسای من،
من در این راه عشق، فقط تو را می‌بینم.
چون پروانه‌ای که گرد شمع می‌گردد،
من نیز گرد تو می‌چرخم.
نه برای سوختن، که برای رسیدن به نوری که فقط در چشمانت می‌درخشد.
همه‌ی هستی من، یک کلمه‌ست: «تو».
هر روز، هر شب، هر لحظه،
تنها به تو فکر می‌کنم.
🦋""",

    """💌 **نامه‌ای از دل من...**

اگر روزی از من بپرسند که عشق را از که آموختی،
می‌گویم از نگاه تو.
با تو، حتی غم نیز شیرین است،
و بی‌تو، شادی هم بی‌رنگ.
زندگی‌ام، در سایه‌ی مهربانی‌ات شکوفا شد.
نسای من، اگر روزی از این نامه‌ها اثری نماند،
بدان که نفس‌هایم، هنوز نام تو را زمزمه می‌کنند.
🌸""",

    """💌 **نامه‌ای از دل من...**

نسای من،
در این دنیای پر از پیچ و خم،
من نه عاقل بودم و نه دیوانه –
من عاشق بودم، و این هر دو را در خود جمع می‌کردم.
تو را که می‌بینم، آسمان را در چشمانت می‌بینم،
و زمین را در قدم‌هایت.
با تو، من به جایی رسیده‌ام که نه من باقی‌ام و نه تو –
فقط «ما» هستیم، در میان شعله‌های این عشق پاک.
بیا، تا از این دو جهان بگذریم،
و تنها در نگاه یکدیگر، بهشت را ببینیم.
❤️‍🔥""",

    """💌 **نامه‌ای از دل من...**

نسای من،
در این روزگار که همه‌چیز می‌گذرد،
من تو را یافتم، و این بزرگترین راز زندگی من است.
اگر امروز را با تو ننوشم،
فردا هیچ لحظه‌ای برای به یاد آوردن نخواهم داشت.
بیا، پیش از آنکه روزها بگذرند،
با هم زندگی کنیم، با هم بخندیم، با هم عشق بورزیم.
این لحظه، همه‌ی هستی من است.
تو، همه‌ی زیبایی من.
و این عشق، همه‌ی جاودانگی من.
🍷""",

    """💌 **نامه‌ای از دل من...**

نسای من،
در شب‌های بی‌ستاره،
تنها نگاه توست که راه را روشن می‌کند.
من از پسِ هر دیوار، صدای تو را می‌شنوم،
و در هر پیچِ جاده، ردِ پای تو را می‌بینم.
این عشق، نه برای من و نه برای توست –
برای «ما»ست.
برای کسی که میانِ من و تو نفس می‌کشد.
نسای من، در تمامِ شب‌های زندگی،
تو تنها صبحی هستی که هیچ‌وقت غروب نمی‌کند.
✨"""
]

def get_main_keyboard():
    return {
        "keyboard": [
            ["📸 عکس‌ها"],
            ["🎂 تولد نسا", "📅 روز آشنایی"],
            ["⏳ ساعت تا تولدت"],
            ["💌 نامه عشق"],
            ["❤️ صفحه عشق"],
            ["🎉 تبریک برای عشقم"],
            ["🎸 آموزش سه تار"],
            ["🔙 بازگشت به منو"]
        ],
        "resize_keyboard": True
    }

def get_photo_keyboard():
    return {
        "keyboard": [
            ["📸 عکس ۱", "📸 عکس ۲", "📸 عکس ۳"],
            ["📸 عکس ۴", "📸 عکس ۵", "📸 عکس ۶"],
            ["📸 عکس ۷"],
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
    if photo_path.startswith("http"):
        urls = [
            f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
            f"https://telegram.dog/bot{TOKEN}/sendPhoto",
            f"https://tg.i-c-a.com/bot{TOKEN}/sendPhoto",
        ]
        for url in urls:
            try:
                payload = {"chat_id": chat_id, "photo": photo_path, "caption": caption}
                r = requests.post(url, data=payload, timeout=20)
                if r.status_code == 200:
                    return True
            except:
                continue
        send_message(chat_id, "❌ ارسال عکس از لینک ناموفق بود!")
        return False
    
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
    
    if text in ["📸 عکس ۱", "📸 عکس ۲", "📸 عکس ۳", "📸 عکس ۴", "📸 عکس ۵", "📸 عکس ۶", "📸 عکس ۷"]:
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
    
    if text == "🎉 تبریک برای عشقم":
        send_message(chat_id, "🎉 برای دیدن تبریک مخصوص عشقم، لینک زیر رو باز کن:\nhttps://nesa-bot.onrender.com/birthday_surprise.html")
        return
    
    if text == "🎸 آموزش سه تار":
        send_message(chat_id, "🎸 برای دانلود آموزش ویدئویی سه تار، لینک زیر رو باز کن:\nhttps://www.mediafire.com/file/b58ae3ost3729bw/%D8%A2%D9%85%D9%88%D8%B2%D8%B4+%D9%88%DB%8C%D8%AF%D8%A6%D9%88%DB%8C%DB%8C+%D8%B3%D9%87+%D8%AA%D8%A7%D8%B1.zip/file")
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
            "❤️ صفحه عشق: /love\n"
            "🎉 تبریک برای عشقم: /birthday_surprise.html\n"
            "🎸 آموزش سه تار: لینک دانلود",
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

@app.route('/birthday_surprise.html')
def birthday_surprise():
    return render_template_string(BIRTHDAY_SURPRISE_PAGE)

if __name__ == "__main__":
    print("🚀 ربات ahu goozlum با تمام ویژگی‌ها روشن شد...")
    print(f"🔑 پسورد: {PASSWORD}")
    print(f"🎂 تولد: {BIRTH_DAY}/{BIRTH_MONTH} (۱۷ مرداد) ساعت {BIRTH_HOUR}:{BIRTH_MINUTE}")
    print(f"📸 تعداد عکس‌ها: {len(PHOTOS)}")
    print("❤️ صفحه عشق در آدرس: /love")
    print("🎉 تبریک برای عشقم: /birthday_surprise.html")
    print("🎸 آموزش سه تار: https://www.mediafire.com/file/...")
    
    timer_thread = threading.Thread(target=birthday_timer, daemon=True)
    timer_thread.start()
    
    app.run(host='0.0.0.0', port=10000, debug=False)
