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
# 🔐 تنظیمات
# ============================================================

# در Render از Environment Variable با نام TOKEN استفاده کن
TOKEN = os.environ.get("TOKEN", "").strip()

YOUR_CHAT_ID = "1228473012"
PASSWORD = "1386"

BIRTH_DAY = 8
BIRTH_MONTH = 8
BIRTH_HOUR = 0
BIRTH_MINUTE = 0

IRAN_OFFSET = datetime.timedelta(hours=3, minutes=30)

user_access = {}

# آدرس سرویس Render را اینجا در Environment Variable بگذار
# مثال:
# https://nesa-bot.onrender.com
BASE_URL = os.environ.get("BASE_URL", "").rstrip("/")


# ============================================================
# 🕐 زمان ایران
# ============================================================

def get_current_iran_time():
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    return utc_now.astimezone(
        datetime.timezone(IRAN_OFFSET)
    )


# ============================================================
# 📅 تاریخ آشنایی
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


# ============================================================
# 🎂 تولد
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

    return int((birth - now).total_seconds() // 3600)


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
    }
}


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
# 💞 متن‌های روز آشنایی
# ============================================================

SECOND_QUOTES = [
    "هر ثانیه‌ای که می‌گذرد، عشق من به تو عمیق‌تر می‌شود... ❤️",
    "ثانیه‌ها می‌گذرند، اما عشق من به تو هرگز کهنه نمی‌شود... 🌹",
    "در هر ثانیه‌ای از زندگی‌ام، تو را نفس می‌کشم... 💫",
    "ثانیه‌های بی‌تو طولانی‌اند، اما کنار تو حتی ساعت‌ها هم کوتاه‌اند... ✨",
    "هر ثانیه که می‌گذرد، یک دلیل تازه برای دوست داشتن تو پیدا می‌کنم... ❤️"
]


# ============================================================
# 💌 نامه‌ها
# ============================================================

LOVE_LETTERS = [
"""💌 نامه‌ای از دل من...

نسای من،

اگر بخواهم تمام زیبایی‌های دنیا را
در یک کلمه خلاصه کنم،
آن کلمه برای من «تو» است.

از وقتی وارد زندگی من شدی،
خیلی از چیزها معنای تازه‌ای پیدا کردند.

لبخند،
دلتنگی،
انتظار،
و حتی ساده‌ترین لحظه‌های زندگی.

❤️ دوستت دارم...
نه فقط برای امروز،
بلکه برای تمام فرداهایی که هنوز نرسیده‌اند.""",

"""💌 نامه‌ای برای نسا...

نسا جان،

اگر یک روز از من بپرسند
عشق یعنی چه؟

من نمی‌خواهم توضیح بدهم.

فقط تو را نشانشان می‌دهم.

چون بعضی آدم‌ها
تعریف عشق نیستند؛
خودِ عشق‌اند.

🌹 دوستت دارم،
بیشتر از چیزی که بتوانم
با کلمات توضیحش بدهم."""
]


# ============================================================
# ⌨️ منوی اصلی
# ============================================================

def get_main_keyboard():
    return {
        "keyboard": [
            ["📸 عکس‌ها"],
            ["🎂 تولد نسا", "📅 روز آشنایی"],
            ["⏳ ساعت تا تولدت"],
            ["💌 نامه عشق"],
            ["❤️ صفحه عشق"],
            ["🎉 تبریک برای عشقم"],
            ["💔 قهرم... بیا آشتی کنیم"],
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


# ============================================================
# 📤 Telegram API
# ============================================================

def telegram_api(method, data=None, files=None, timeout=15):

    if not TOKEN:
        print("❌ TOKEN تنظیم نشده است.")
        return None

    url = f"https://api.telegram.org/bot{TOKEN}/{method}"

    try:
        if files:
            response = requests.post(
                url,
                data=data,
                files=files,
                timeout=timeout
            )
        else:
            response = requests.post(
                url,
                data=data,
                timeout=timeout
            )

        print(
            f"Telegram {method}: "
            f"{response.status_code}"
        )

        return response

    except requests.RequestException as e:
        print(f"Telegram API error: {e}")
        return None


def send_message(chat_id, text, reply_markup=None):

    data = {
        "chat_id": chat_id,
        "text": text
    }

    if reply_markup:
        data["reply_markup"] = json.dumps(
            reply_markup,
            ensure_ascii=False
        )

    response = telegram_api(
        "sendMessage",
        data=data,
        timeout=15
    )

    return response is not None and response.status_code == 200


# ============================================================
# 📸 ارسال عکس
# ============================================================

def send_photo(chat_id, photo_path, caption=""):

    try:

        if photo_path.startswith("http"):

            response = telegram_api(
                "sendPhoto",
                data={
                    "chat_id": chat_id,
                    "photo": photo_path,
                    "caption": caption
                },
                timeout=30
            )

            return (
                response is not None
                and response.status_code == 200
            )

        if not os.path.exists(photo_path):

            send_message(
                chat_id,
                "❌ عکس پیدا نشد!"
            )

            return False

        with open(photo_path, "rb") as photo:

            response = telegram_api(
                "sendPhoto",
                data={
                    "chat_id": chat_id,
                    "caption": caption
                },
                files={
                    "photo": photo
                },
                timeout=30
            )

        return (
            response is not None
            and response.status_code == 200
        )

    except Exception as e:

        print("send_photo error:", e)

        return False


# ============================================================
# 💔 پیام آشتی
# ============================================================

def send_reconciliation_message(chat_id):

    text = """💔❤️ یک پیام از طرف عشقت داری...

شاید الان قهر باشی،
شاید غرورت اجازه نده مستقیم پیام بدی...

ولی اینجا می‌تونی حرف دلت رو بگی. 🌹

هرچی می‌خوای برای من بنویس
و من برات می‌فرستم. ❤️

✍️ پیامت رو در پیام بعدی بنویس."""

    send_message(chat_id, text)

    user_access[str(chat_id)] = user_access.get(
        str(chat_id),
        {}
    )

    user_access[str(chat_id)]["waiting_reconciliation"] = True


# ============================================================
# 🤖 پردازش پیام
# ============================================================

def handle_message(chat_id, text):

    chat_id = str(chat_id)
    text = text.strip()

    if chat_id not in user_access:
        user_access[chat_id] = {
            "photos": False,
            "waiting_for_password": False,
            "waiting_reconciliation": False
        }


    # --------------------------------------------------------
    # 💔 دریافت پیام آشتی
    # --------------------------------------------------------

    if user_access[chat_id].get(
        "waiting_reconciliation",
        False
    ):

        user_access[chat_id][
            "waiting_reconciliation"
        ] = False

        message = f"""💌 پیام آشتی از طرف عشقت ❤️

👤 Chat ID:
{chat_id}

💬 متن پیام:

{text}

❤️ شاید غرورش اجازه نداده مستقیم حرفش رو بزنه...
ولی دلش خواسته این پیام بهت برسه. 🌹"""

        send_message(
            YOUR_CHAT_ID,
            message
        )

        send_message(
            chat_id,
            """❤️ پیامت با موفقیت ارسال شد.

امیدوارم خیلی زود
دوباره لبخند روی لبتون باشه. 🌹❤️""",
            get_main_keyboard()
        )

        return


    # --------------------------------------------------------
    # 🔐 پسورد
    # --------------------------------------------------------

    if user_access[chat_id].get(
        "waiting_for_password",
        False
    ):

        if text == PASSWORD:

            user_access[chat_id][
                "photos"
            ] = True

            user_access[chat_id][
                "waiting_for_password"
            ] = False

            send_message(
                chat_id,
                """✅ رمز درست بود!

🔓 گالری خصوصی برات باز شد ❤️""",
                get_photo_keyboard()
            )

        else:

            send_message(
                chat_id,
                """❌ رمز اشتباهه!

دوباره امتحان کن ❤️""",
                get_password_keyboard()
            )

        return


    # --------------------------------------------------------
    # 📸 عکس
    # --------------------------------------------------------

    if text in PHOTOS:

        if user_access[chat_id].get(
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

            user_access[chat_id][
                "waiting_for_password"
            ] = True

            send_message(
                chat_id,
                """🔐 این قسمت خصوصی و مخصوص خودته.

لطفاً رمز مخصوص رو وارد کن ❤️""",
                get_password_keyboard()
            )

        return


    # --------------------------------------------------------
    # 📸 گالری
    # --------------------------------------------------------

    if text == "📸 عکس‌ها":

        if user_access[chat_id].get(
            "photos",
            False
        ):

            send_message(
                chat_id,
                "📸 کدوم عکس رو می‌خوای ببینی؟ ❤️",
                get_photo_keyboard()
            )

        else:

            user_access[chat_id][
                "waiting_for_password"
            ] = True

            send_message(
                chat_id,
                """🔐 برای ورود به گالری
رمز مخصوص رو وارد کن ❤️""",
                get_password_keyboard()
            )

        return


    # --------------------------------------------------------
    # 🎂 تولد
    # --------------------------------------------------------

    if text == "🎂 تولد نسا":

        send_message(
            chat_id,
            BIRTHDAY_MESSAGE
        )

        return


    # --------------------------------------------------------
    # 📅 روز آشنایی
    # --------------------------------------------------------

    if text == "📅 روز آشنایی":

        seconds = get_meeting_seconds()
        days = seconds // 86400

        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        quote = random.choice(
            SECOND_QUOTES
        )

        message = f"""💞 روز آشنایی ما ❤️

📅 ۲۴ اسفند ۱۴۰۴

🌻 {days} روز از روز آشنایی ما گذشته.

⏱️ و تا همین لحظه:

{seconds:,} ثانیه

{hours} ساعت و {minutes} دقیقه و {secs} ثانیه

❤️ ثانیه‌هایی که قلبم برای تو تپیده.

هر ثانیه‌ای که با تو گذشته،
برای من ارزشمند بوده.

و اگر دوباره به روز اول برگردم،
باز هم تو را انتخاب می‌کنم. 🌹

📖 {quote}

❤️ از روز آشنایی‌مان تا همیشه...
تو یکی از زیباترین اتفاق‌های زندگی منی."""

        send_message(
            chat_id,
            message
        )

        return


    # --------------------------------------------------------
    # ⏳ تولد
    # --------------------------------------------------------

    if text == "⏳ ساعت تا تولدت":

        hours = hours_until_birthday()

        send_message(
            chat_id,
            f"""🎂 شمارش معکوس برای روز قشنگ تو...

🌻 تولد ahu goozlum

⏳ فقط {hours:,} ساعت مونده...

روزی که دنیا با آمدنت
قشنگ‌تر شد. ❤️🌻"""
        )

        return


    # --------------------------------------------------------
    # 💌 نامه
    # --------------------------------------------------------

    if text == "💌 نامه عشق":

        send_message(
            chat_id,
            random.choice(
                LOVE_LETTERS
            )
        )

        return


    # --------------------------------------------------------
    # ❤️ صفحه عشق
    # --------------------------------------------------------

    if text == "❤️ صفحه عشق":

        send_message(
            chat_id,
            """❤️ یک سورپرایز مخصوص تو آماده کردم...

👇 صفحه عشق:

https://nesa-bot.onrender.com/love"""
        )

        return


    # --------------------------------------------------------
    # 🎉 تبریک
    # --------------------------------------------------------

    if text == "🎉 تبریک برای عشقم":

        send_message(
            chat_id,
            """🎁 یک هدیه مخصوص برای تو آماده شده...

🌻 آروم بازش کن ❤️

👇 سورپرایز:

https://nesa-bot.onrender.com/birthday_surprise.html"""
        )

        return


    # --------------------------------------------------------
    # 💔 آشتی
    # --------------------------------------------------------

    if text == "💔 قهرم... بیا آشتی کنیم":

        send_reconciliation_message(
            chat_id
        )

        return


    # --------------------------------------------------------
    # 🔙 بازگشت
    # --------------------------------------------------------

    if text == "🔙 بازگشت به منو":

        old = user_access.get(
            chat_id,
            {}
        )

        user_access[chat_id] = {
            "photos": old.get(
                "photos",
                False
            ),
            "waiting_for_password": False,
            "waiting_reconciliation": False
        }

        send_message(
            chat_id,
            """🏠 برگشتیم به منوی اصلی...

🌻 هر چیزی که بخوای اینجاست ❤️""",
            get_main_keyboard()
        )

        return


    # --------------------------------------------------------
    # /start
    # --------------------------------------------------------

    if text == "/start":

        old = user_access.get(
            chat_id,
            {}
        )

        user_access[chat_id] = {
            "photos": old.get(
                "photos",
                False
            ),
            "waiting_for_password": False,
            "waiting_reconciliation": False
        }

        send_message(
            chat_id,
            """🌻❤️ به دنیای ahu goozlum خوش اومدی ❤️🌻

🎁 اینجا یک گوشه کوچیک از قلب منه...

📸 عکس‌های خصوصی
🎂 تولد نسا
💞 روز آشنایی
⏳ شمارش معکوس تولد
💌 نامه‌های عاشقانه
❤️ صفحه عشق
🎉 سورپرایز تولد
💔 پیام آشتی

🌻 هر دکمه یک تکه از داستان ماست...""",
            get_main_keyboard()
        )

        return


    # --------------------------------------------------------
    # دستور نامعتبر
    # --------------------------------------------------------

    send_message(
        chat_id,
        "❌ این دستور رو نمی‌شناسم.\n\nاز دکمه‌های پایین استفاده کن ❤️",
        get_main_keyboard()
    )


# ============================================================
# 🌐 WEBHOOK
# ============================================================

@app.route("/", methods=["GET"])
def home():

    return """
    <html>
    <head>
        <meta charset="UTF-8">
        <title>❤️ Ahu Gozlum Bot</title>
    </head>
    <body style="
        background:#10050a;
        color:white;
        text-align:center;
        font-family:Arial;
        padding-top:80px;
    ">

        <h1>🌻❤️ Bot is Online ❤️🌻</h1>

        <p>Telegram Webhook is running.</p>

        <p>
            <a
                href="/love"
                style="color:#ff6688"
            >
                ❤️ صفحه عشق
            </a>
        </p>

        <p>
            <a
                href="/birthday_surprise.html"
                style="color:#ffd166"
            >
                🌻 سورپرایز تولد
            </a>
        </p>

    </body>
    </html>
    """


@app.route("/", methods=["POST"])
def telegram_webhook():

    try:

        data = request.get_json(
            silent=True
        )

        if not data:
            return "OK", 200

        if "message" not in data:
            return "OK", 200

        message = data["message"]

        chat = message.get(
            "chat",
            {}
        )

        chat_id = chat.get(
            "id"
        )

        text = message.get(
            "text",
            ""
        )

        if chat_id is not None:

            # پردازش را در Thread جدا انجام می‌دهیم
            # تا Telegram سریع 200 دریافت کند
            threading.Thread(
                target=handle_message,
                args=(chat_id, text),
                daemon=True
            ).start()

        return "OK", 200

    except Exception as e:

        print(
            "Webhook error:",
            repr(e)
        )

        # همیشه به Telegram پاسخ 200 می‌دهیم
        return "OK", 200


# ============================================================
# ❤️ صفحه عشق
# ============================================================

@app.route("/love")
def love_page():

    return """
    <!DOCTYPE html>
    <html lang="fa">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width,initial-scale=1">

    <title>❤️ I Love You Nesa ❤️</title>

    <style>

    body{
        margin:0;
        min-height:100vh;
        background:
        radial-gradient(
            circle,
            #42111f,
            #090307
        );

        display:flex;
        align-items:center;
        justify-content:center;

        color:white;
        font-family:Arial;
        text-align:center;
    }

    .heart{
        font-size:100px;
        animation:pulse 1.2s infinite;
    }

    h1{
        color:#ff6f91;
        text-shadow:
        0 0 20px #ff315d;
    }

    @keyframes pulse{

        0%,100%{
            transform:scale(1);
        }

        50%{
            transform:scale(1.25);
        }

    }

    </style>

    </head>

    <body>

    <div>

        <div class="heart">
            ❤️
        </div>

        <h1>
            I LOVE YOU NESA
        </h1>

        <p>
            🌹 تو زیباترین اتفاق زندگی منی 🌹
        </p>

    </div>

    </body>
    </html>
    """


# ============================================================
# 🎂 صفحه تولد
# ============================================================

@app.route("/birthday_surprise.html")
def birthday_surprise():

    return """
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">

    <head>

    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width,initial-scale=1">

    <title>🌻 تولدت مبارک نسا ❤️</title>

    <style>

    *{
        box-sizing:border-box;
    }

    body{

        margin:0;
        min-height:100vh;

        overflow:hidden;

        display:flex;
        justify-content:center;
        align-items:center;

        background:
        radial-gradient(
            circle,
            #42111f,
            #090307
        );

        color:white;
        font-family:Tahoma;
    }

    .card{

        width:90%;
        max-width:500px;

        padding:30px;

        text-align:center;

        border-radius:30px;

        background:
        rgba(30,5,15,.88);

        border:
        1px solid
        rgba(255,150,170,.4);

        box-shadow:
        0 0 60px
        rgba(255,60,110,.3);

        position:relative;

        z-index:100;
    }

    h1{

        color:#ffd166;

        text-shadow:
        0 0 25px
        #ff9d00;
    }

    p{

        line-height:2;

        color:#ffe5ec;
    }

    .gift{

        font-size:100px;

        cursor:pointer;

        animation:
        float 2s infinite;
    }

    @keyframes float{

        50%{
            transform:
            translateY(-15px)
            rotate(3deg);
        }

    }

    .flower{

        position:fixed;

        top:-60px;

        z-index:9999;

        pointer-events:none;

        animation:
        fall linear forwards;
    }

    @keyframes fall{

        from{

            transform:
            translateY(-80px)
            rotate(0deg);

            opacity:0;
        }

        10%{
            opacity:1;
        }

        to{

            transform:
            translateY(110vh)
            rotate(720deg);

            opacity:0;
        }

    }

    .heart{

        position:fixed;

        top:-60px;

        z-index:10000;

        animation:
        fall linear forwards;

        pointer-events:none;
    }

    </style>

    </head>

    <body>

    <div class="card">

        <div
            class="gift"
            onclick="start()"
        >
            🎁
        </div>

        <h1>
            🌻 تولدت مبارک نسا 🌻
        </h1>

        <p>

        امروز فقط تولد تو نیست...

        <br><br>

        امروز روزی است که
        دنیا یکی از زیباترین آدم‌هایش را
        به خودش دید.

        <br><br>

        ❤️ دوستت دارم ❤️

        <br><br>

        🌻 همیشه بخند 🌻

        </p>

    </div>

    <script>

    function start(){

        const flowers=[
            "🌻",
            "🌼",
            "🌺",
            "🌸",
            "🌷",
            "🪻",
            "🌹",
            "💐"
        ];

        const hearts=[
            "❤️",
            "💖",
            "💕",
            "💗",
            "💘"
        ];

        for(
            let i=0;
            i<100;
            i++
        ){

            const f=
            document.createElement("div");

            f.className="flower";

            f.innerText=
            flowers[
                Math.floor(
                    Math.random()
                    *flowers.length
                )
            ];

            f.style.left=
            Math.random()*100+"%";

            f.style.fontSize=
            (20+
            Math.random()*35)+"px";

            f.style.animationDuration=
            (4+
            Math.random()*6)+"s";

            f.style.animationDelay=
            Math.random()*3+"s";

            document.body.appendChild(f);

            setTimeout(
                ()=>f.remove(),
                12000
            );
        }

        for(
            let i=0;
            i<80;
            i++
        ){

            const h=
            document.createElement("div");

            h.className="heart";

            h.innerText=
            hearts[
                Math.floor(
                    Math.random()
                    *hearts.length
                )
            ];

            h.style.left=
            Math.random()*100+"%";

            h.style.fontSize=
            (15+
            Math.random()*25)+"px";

            h.style.animationDuration=
            (4+
            Math.random()*5)+"s";

            h.style.animationDelay=
            Math.random()*3+"s";

            document.body.appendChild(h);

            setTimeout(
                ()=>h.remove(),
                11000
            );
        }

    }

    </script>

    </body>

    </html>
    """


# ============================================================
# 🔧 ثبت Webhook
# ============================================================

def setup_webhook():

    if not TOKEN:

        print(
            "❌ TOKEN وجود ندارد."
        )

        return False

    if not BASE_URL:

        print(
            "❌ BASE_URL وجود ندارد."
        )

        return False

    webhook_url = (
        BASE_URL
        + "/"
    )

    print(
        "🔗 Webhook:",
        webhook_url
    )

    response = telegram_api(
        "setWebhook",
        data={
            "url": webhook_url,

            # جلوگیری از دریافت آپدیت‌های قدیمی
            "drop_pending_updates": True
        },
        timeout=20
    )

    if response is None:
        return False

    print(
        "Webhook response:",
        response.text
    )

    return response.status_code == 200


# ============================================================
# 🚀 اجرای Render
# ============================================================

if __name__ == "__main__":

    print(
        "🚀 Ahu Gozlum Bot starting..."
    )

    print(
        "🌐 BASE_URL:",
        BASE_URL
    )

    print(
        "🔐 TOKEN:",
        "SET" if TOKEN else "NOT SET"
    )

    # ثبت Webhook
    setup_webhook()

    port = int(
        os.environ.get(
            "PORT",
            "10000"
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        threaded=True
    )
