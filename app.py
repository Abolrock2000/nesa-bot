from flask import Flask, request, render_template_string
import requests
import datetime
import os
import threading
import time
import random

app = Flask(__name__)

# ============================================================
# تنظیمات
# ============================================================

TOKEN = os.environ.get("BOT_TOKEN", "").strip()
YOUR_CHAT_ID = os.environ.get("YOUR_CHAT_ID", "1228473012").strip()

PASSWORD = os.environ.get("LOVE_PASSWORD", "1386")

# لینک سه‌تار
SETAR_LINK = "https://t.me/+robRoFDJYKtlNmRk"

# آدرس سایت Render خودت را اینجا بگذار
SITE_URL = os.environ.get(
    "SITE_URL",
    "https://nesa-bot.onrender.com"
).rstrip("/")

# تاریخ روز آشنایی
MEETING_DATE = datetime.datetime(
    2026, 3, 15, 0, 0, 0,
    tzinfo=datetime.timezone(datetime.timedelta(hours=3, minutes=30))
)

IRAN_TZ = datetime.timezone(datetime.timedelta(hours=3, minutes=30))

BIRTH_DAY = 8
BIRTH_MONTH = 8
BIRTH_HOUR = 0
BIRTH_MINUTE = 0

user_access = {}
reconcile_sessions = {}

# ============================================================
# عکس‌ها
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
# متن تولد
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
# نامه‌ها
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
انتظار
و حتی ساده‌ترین لحظه‌های زندگی.

تو همان آدمی هستی که
فکر کردن به او
می‌تواند یک روز معمولی را
به زیباترین روز دنیا تبدیل کند.

❤️ دوستت دارم...
نه فقط برای امروز،
بلکه برای تمام فرداهایی که هنوز نرسیده‌اند.""",

"""💌 نامه‌ای برای نسا...

نسا جان،

اگر یک روز از من بپرسند:
عشق یعنی چه؟

من توضیح نمی‌دهم.

فقط تو را نشانشان می‌دهم.

چون بعضی آدم‌ها
تعریف عشق نیستند؛
خودِ عشق‌اند.

تو برای من فقط یک نفر نیستی.

تو بخشی از آرامش،
خنده‌ها،
فکرها
و تمام رؤیاهای منی.

🌹 دوستت دارم،
بیشتر از چیزی که بتوانم
با کلمات توضیحش بدهم.""",

"""💌 از طرف قلب من...

نسای من،

گاهی با خودم فکر می‌کنم
چطور ممکن است یک نفر
این‌قدر برای آدم مهم شود؟

بعد یاد تو می‌افتم
و جوابم را پیدا می‌کنم.

تو آمدی
و آرام‌آرام
جایی در قلبم ساختی
که دیگر هیچ‌کس
نمی‌تواند جای آن را بگیرد.

❤️ اگر تمام دنیا را داشته باشم
ولی تو نباشی،
باز هم چیزی کم است.

چیزی به اسم «تو»."""
]

# ============================================================
# زمان ایران
# ============================================================

def iran_now():
    return datetime.datetime.now(datetime.timezone.utc).astimezone(IRAN_TZ)


# ============================================================
# روز آشنایی
# ============================================================

def meeting_seconds():
    now = iran_now()

    if now < MEETING_DATE:
        return 0

    return int((now - MEETING_DATE).total_seconds())


# ============================================================
# شمارش تولد
# ============================================================

def birthday_countdown():
    now = iran_now()

    birth = datetime.datetime(
        now.year,
        BIRTH_MONTH,
        BIRTH_DAY,
        BIRTH_HOUR,
        BIRTH_MINUTE,
        tzinfo=IRAN_TZ
    )

    if now >= birth:
        birth = datetime.datetime(
            now.year + 1,
            BIRTH_MONTH,
            BIRTH_DAY,
            BIRTH_HOUR,
            BIRTH_MINUTE,
            tzinfo=IRAN_TZ
        )

    return max(0, int((birth - now).total_seconds()))


# ============================================================
# کیبورد اصلی
# ============================================================

def main_keyboard():
    return {
        "keyboard": [
            ["📸 عکس‌ها"],
            ["🎂 تولد نسا", "📅 روز آشنایی"],
            ["⏳ ساعت تا تولدت"],
            ["💌 نامه عشق"],
            ["❤️ صفحه عشق"],
            ["🎉 تبریک برای عشقم"],
            ["🤝 بیا آشتی کنیم"],
            ["🎵 آموزش سه‌تار"],
            ["🔙 بازگشت به منو"]
        ],
        "resize_keyboard": True
    }


def photo_keyboard():
    return {
        "keyboard": [
            ["📸 عکس ۱", "📸 عکس ۲", "📸 عکس ۳"],
            ["📸 عکس ۴", "📸 عکس ۵", "📸 عکس ۶"],
            ["📸 عکس ۷"],
            ["🔙 بازگشت به منو"]
        ],
        "resize_keyboard": True
    }


def back_keyboard():
    return {
        "keyboard": [
            ["🔙 بازگشت به منو"]
        ],
        "resize_keyboard": True
    }


# ============================================================
# تلگرام
# ============================================================

def telegram_url(method):
    return f"https://api.telegram.org/bot{TOKEN}/{method}"


def send_message(chat_id, text, keyboard=None):
    if not TOKEN:
        print("BOT_TOKEN تنظیم نشده است.")
        return False

    data = {
        "chat_id": chat_id,
        "text": text
    }

    if keyboard:
        data["reply_markup"] = keyboard

    try:
        r = requests.post(
            telegram_url("sendMessage"),
            json=data,
            timeout=12
        )

        if r.ok:
            return True

        print("Telegram sendMessage:", r.status_code, r.text)

    except Exception as e:
        print("send_message:", e)

    return False


def send_photo(chat_id, path, caption=""):
    if not TOKEN:
        return False

    try:

        # عکس اینترنتی
        if path.startswith("http"):
            r = requests.post(
                telegram_url("sendPhoto"),
                data={
                    "chat_id": chat_id,
                    "photo": path,
                    "caption": caption
                },
                timeout=20
            )

            return r.ok

        # عکس محلی
        if not os.path.exists(path):
            send_message(chat_id, "❌ عکس پیدا نشد.")
            return False

        with open(path, "rb") as f:
            r = requests.post(
                telegram_url("sendPhoto"),
                data={
                    "chat_id": chat_id,
                    "caption": caption
                },
                files={
                    "photo": f
                },
                timeout=30
            )

        return r.ok

    except Exception as e:
        print("send_photo:", e)
        return False


# ============================================================
# سیستم «بیا آشتی کنیم»
# ============================================================

def start_reconciliation(chat_id):

    reconcile_sessions[str(chat_id)] = {
        "waiting": True
    }

    send_message(
        chat_id,
        """🤍 بیا آشتی کنیم...

اگر حرفی توی دلت مونده،
اینجا بنویس.

پیامت مستقیم برای من ارسال میشه،
حتی اگر غرورت اجازه نده مستقیم بهم پیام بدی. 🥺❤️

هرچی دوست داری بگو...
من می‌خونمش. 🌷

✍️ پیامت رو بفرست:""",
        back_keyboard()
    )


def handle_reconciliation(chat_id, text):

    sid = str(chat_id)

    if sid not in reconcile_sessions:
        return False

    if not reconcile_sessions[sid].get("waiting"):
        return False

    if text == "🔙 بازگشت به منو":
        reconcile_sessions.pop(sid, None)
        send_message(
            chat_id,
            "🏠 برگشتیم به منوی اصلی ❤️",
            main_keyboard()
        )
        return True

    # پیام را برای صاحب ربات ارسال کن
    message = f"""🤍 پیام آشتی از طرف پارتنرت:

━━━━━━━━━━━━━━

{text}

━━━━━━━━━━━━━━

📩 برای پاسخ دادن، همین پیام را می‌توانی از داخل ربات مدیریت کنی."""

    ok = send_message(
        YOUR_CHAT_ID,
        message
    )

    if ok:
        send_message(
            chat_id,
            """❤️ پیامت با موفقیت ارسال شد.

حرفت بهش رسید. 🤍

حالا دیگه باقی‌ش رو بسپار به دلش...
🌷 امیدوارم خیلی زود دوباره باهم خوب بشین.""",
            main_keyboard()
        )
    else:
        send_message(
            chat_id,
            """❌ فعلاً نتونستم پیام رو ارسال کنم.

چند لحظه دیگه دوباره امتحان کن. ❤️"""
        )

    reconcile_sessions.pop(sid, None)

    return True


# ============================================================
# پردازش پیام
# ============================================================

def handle_message(chat_id, text):

    chat_id = str(chat_id)
    text = (text or "").strip()

    # آشتی
    if handle_reconciliation(chat_id, text):
        return

    # -------------------------------
    # Start
    # -------------------------------

    if text == "/start":

        user_access[chat_id] = {
            "photos": False,
            "password": False
        }

        send_message(
            chat_id,
            """🌻❤️ به دنیای ahu goozlum خوش اومدی ❤️🌻

اینجا یک گوشه کوچیک از قلب منه...

📸 عکس‌های خصوصی
🎂 تولد نسا
💞 روز آشنایی
⏳ شمارش معکوس تولد
💌 نامه‌های عاشقانه
❤️ صفحه عشق
🎉 سورپرایز تولد
🤝 بیا آشتی کنیم
🎵 آموزش سه‌تار

🌻 هر دکمه یک تکه از داستان ماست...""",
            main_keyboard()
        )
        return

    # -------------------------------
    # آشتی
    # -------------------------------

    if text == "🤝 بیا آشتی کنیم":
        start_reconciliation(chat_id)
        return

    # -------------------------------
    # سه‌تار
    # -------------------------------

    if text == "🎵 آموزش سه‌تار":

        send_message(
            chat_id,
            f"""🎵 آموزش سه‌تار

اگر دوست داری آموزش سه‌تار رو ببینی،
از لینک زیر وارد شو:

{SETAR_LINK}

🎶 موفق باشی ❤️""",
            main_keyboard()
        )
        return

    # -------------------------------
    # Password
    # -------------------------------

    access = user_access.get(chat_id, {})

    if access.get("waiting_password"):

        if text == PASSWORD:

            user_access[chat_id]["photos"] = True
            user_access[chat_id]["waiting_password"] = False

            send_message(
                chat_id,
                """✅ رمز درست بود!

🔓 گالری اختصاصی برات باز شد ❤️""",
                photo_keyboard()
            )

        else:

            send_message(
                chat_id,
                """❌ رمز اشتباهه.

دوباره امتحان کن ❤️""",
                back_keyboard()
            )

        return

    # -------------------------------
    # گالری
    # -------------------------------

    if text == "📸 عکس‌ها":

        if access.get("photos"):

            send_message(
                chat_id,
                "📸 کدوم عکس رو می‌خوای ببینی؟ ❤️",
                photo_keyboard()
            )

        else:

            user_access.setdefault(chat_id, {})
            user_access[chat_id]["waiting_password"] = True

            send_message(
                chat_id,
                """🔐 این قسمت خصوصی و مخصوص خودته.

رمز مخصوص رو وارد کن ❤️""",
                back_keyboard()
            )

        return

    # -------------------------------
    # عکس
    # -------------------------------

    if text in PHOTOS:

        if access.get("photos"):

            p = PHOTOS[text]

            send_photo(
                chat_id,
                p["path"],
                p["caption"]
            )

        else:

            user_access.setdefault(chat_id, {})
            user_access[chat_id]["waiting_password"] = True

            send_message(
                chat_id,
                "🔐 اول رمز گالری رو وارد کن ❤️",
                back_keyboard()
            )

        return

    # -------------------------------
    # تولد
    # -------------------------------

    if text == "🎂 تولد نسا":

        send_message(
            chat_id,
            BIRTHDAY_MESSAGE
        )

        return

    # -------------------------------
    # روز آشنایی
    # -------------------------------

    if text == "📅 روز آشنایی":

        seconds = meeting_seconds()
        days = seconds // 86400

        quote = random.choice([
            "هر ثانیه‌ای که می‌گذرد، عشق من به تو عمیق‌تر می‌شود... ❤️",
            "ثانیه‌ها می‌گذرند، اما عشق من به تو کهنه نمی‌شود... 🌹",
            "در هر ثانیه‌ای از زندگی‌ام، تو را نفس می‌کشم... 💫",
            "هر ثانیه که می‌گذرد، یک دلیل تازه برای دوست داشتن تو پیدا می‌کنم... ❤️"
        ])

        send_message(
            chat_id,
            f"""💞 روز آشنایی ما ❤️

📅 ۲۴ اسفند ۱۴۰۴

🌻 {days:,} روز از قشنگ‌ترین فصل زندگی من گذشته.

⏱️ {seconds:,} ثانیه...

این فقط یک عدد نیست.

این {seconds:,} ثانیه،
بخشی از زمانی است که
قلبم با یاد تو تپیده. ❤️

اگر دوباره به اولین روز برگردم،
باز هم تو را انتخاب می‌کنم.

🌹 {quote}

❤️ از روز آشنایی‌مان تا همیشه..."""
        )

        return

    # -------------------------------
    # شمارش تولد
    # -------------------------------

    if text == "⏳ ساعت تا تولدت":

        total = birthday_countdown()

        days = total // 86400
        hours = (total % 86400) // 3600
        minutes = (total % 3600) // 60
        seconds = total % 60

        send_message(
            chat_id,
            f"""🎂 شمارش معکوس برای روز قشنگ تو...

🌻 تولد ahu goozlum

⏳ {days} روز
🕐 {hours} ساعت
⏱️ {minutes} دقیقه
⏰ {seconds} ثانیه

تا روزی که دنیا قشنگ‌تر شد؛
روزی که تو به دنیا اومدی. ❤️🌻"""
        )

        return

    # -------------------------------
    # نامه
    # -------------------------------

    if text == "💌 نامه عشق":

        send_message(
            chat_id,
            random.choice(LOVE_LETTERS)
        )

        return

    # -------------------------------
    # صفحه عشق
    # -------------------------------

    if text == "❤️ صفحه عشق":

        send_message(
            chat_id,
            f"""❤️ یک سورپرایز مخصوص تو آماده کردم...

چهره‌ات با کلمات
I LOVE YOU NESA
ساخته شده. 🌹

👇 بازش کن:

{SITE_URL}/love"""
        )

        return

    # -------------------------------
    # سورپرایز
    # -------------------------------

    if text == "🎉 تبریک برای عشقم":

        send_message(
            chat_id,
            f"""🎁 یک هدیه مخصوص برای تو آماده شده...

آروم بازش کن 🌻❤️

👇 سورپرایز تولدت:

{SITE_URL}/birthday_surprise.html"""
        )

        return

    # -------------------------------
    # بازگشت
    # -------------------------------

    if text == "🔙 بازگشت به منو":

        old = user_access.get(chat_id, {})

        user_access[chat_id] = {
            "photos": old.get("photos", False),
            "waiting_password": False
        }

        reconcile_sessions.pop(chat_id, None)

        send_message(
            chat_id,
            """🏠 برگشتیم به منوی اصلی...

🌻 هر چیزی که بخوای اینجاست ❤️""",
            main_keyboard()
        )

        return

    # -------------------------------
    # نامعتبر
    # -------------------------------

    send_message(
        chat_id,
        """❌ این دستور رو نمی‌شناسم.

از دکمه‌های پایین استفاده کن ❤️""",
        main_keyboard()
    )


# ============================================================
# تولد خودکار
# ============================================================

def birthday_timer():

    last_sent_date = None

    while True:

        try:

            now = iran_now()

            if (
                now.month == BIRTH_MONTH
                and now.day == BIRTH_DAY
                and now.hour == BIRTH_HOUR
                and now.minute == BIRTH_MINUTE
            ):

                today = now.date()

                if last_sent_date != today:

                    print("🎂 ارسال پیام تولد...")

                    send_message(
                        YOUR_CHAT_ID,
                        BIRTHDAY_MESSAGE
                    )

                    photo = PHOTOS["📸 عکس ۱"]

                    if os.path.exists(photo["path"]):

                        send_photo(
                            YOUR_CHAT_ID,
                            photo["path"],
                            photo["caption"]
                        )

                    last_sent_date = today

                    print("✅ تولد ارسال شد.")

        except Exception as e:

            print("birthday_timer:", e)

        time.sleep(20)


# ============================================================
# صفحه تولد
# ============================================================

BIRTHDAY_PAGE = r"""
<!DOCTYPE html>
<html lang="fa" dir="rtl">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width,initial-scale=1.0">

<title>🌻 تولدت مبارک نسا ❤️</title>

<style>

*{
    box-sizing:border-box;
    margin:0;
    padding:0;
}

body{

    min-height:100vh;

    background:
    radial-gradient(
        circle at 50% 30%,
        #54152d 0%,
        #200914 35%,
        #050205 100%
    );

    color:white;

    font-family:
    Tahoma,
    Arial,
    sans-serif;

    overflow:hidden;

    display:flex;

    justify-content:center;

    align-items:center;
}

.container{

    width:92%;
    max-width:540px;

    text-align:center;

    position:relative;

    z-index:100;
}

.gift{

    font-size:130px;

    cursor:pointer;

    animation:
    floatGift 2.4s ease-in-out infinite;

    filter:
    drop-shadow(
        0 0 35px
        rgba(255,80,130,.8)
    );
}

@keyframes floatGift{

    0%,100%{
        transform:
        translateY(0)
        rotate(-3deg);
    }

    50%{
        transform:
        translateY(-22px)
        rotate(3deg);
    }
}

.openText{

    margin-top:20px;

    color:#ffd8e3;

    font-size:18px;
}

.card{

    padding:30px 22px;

    border-radius:30px;

    background:
    linear-gradient(
        145deg,
        rgba(80,15,40,.92),
        rgba(15,4,12,.95)
    );

    border:
    1px solid
    rgba(255,160,190,.4);

    box-shadow:
    0 0 70px
    rgba(255,50,110,.3),

    inset 0 0 35px
    rgba(255,70,120,.08);

    backdrop-filter:blur(15px);
}

h1{

    color:#ffd46d;

    margin-bottom:20px;

    text-shadow:
    0 0 25px
    #ff9b20;
}

input{

    width:100%;

    padding:15px;

    margin-top:20px;

    border-radius:16px;

    border:
    1px solid
    #ff5577;

    background:
    rgba(0,0,0,.55);

    color:white;

    text-align:center;

    font-size:20px;

    outline:none;
}

button{

    margin-top:18px;

    padding:14px 32px;

    border:0;

    border-radius:30px;

    background:
    linear-gradient(
        45deg,
        #ff416c,
        #ff758c
    );

    color:white;

    font-size:17px;

    font-weight:bold;

    cursor:pointer;
}

.message{

    line-height:2.1;

    color:#ffe9ee;

    font-size:16px;
}

.photo{

    width:100%;

    max-width:340px;

    margin:22px auto;

    display:block;

    border-radius:22px;

    border:2px solid
    rgba(255,200,100,.7);

    box-shadow:
    0 0 35px
    rgba(255,150,0,.35);
}

#passwordPage,
#birthdayPage{

    display:none;
}


/* ==========================================
   گل‌ها در جلوی صفحه
========================================== */

.flower-layer{

    position:fixed;

    inset:0;

    pointer-events:none;

    overflow:hidden;

    z-index:10000;
}

.flower{

    position:absolute;

    top:-80px;

    animation:
    flowerFall linear forwards;

    filter:
    drop-shadow(
        0 0 10px
        rgba(255,180,60,.8)
    );
}

@keyframes flowerFall{

    0%{
        transform:
        translateY(-100px)
        rotate(0deg);

        opacity:0;
    }

    10%{
        opacity:1;
    }

    100%{
        transform:
        translateY(115vh)
        rotate(720deg);

        opacity:.95;
    }
}


/* ==========================================
   قلب‌ها کاملاً جلو
========================================== */

.heart-layer{

    position:fixed;

    inset:0;

    pointer-events:none;

    overflow:hidden;

    z-index:11000;
}

.heart{

    position:absolute;

    top:-60px;

    animation:
    heartFall linear forwards;

    filter:
    drop-shadow(
        0 0 10px
        rgba(255,40,100,.8)
    );
}

@keyframes heartFall{

    0%{

        transform:
        translateY(-70px)
        rotate(0deg);

        opacity:0;
    }

    10%{
        opacity:1;
    }

    100%{

        transform:
        translateY(115vh)
        rotate(720deg);

        opacity:0;
    }
}

</style>

</head>

<body>

<div class="flower-layer"
id="flowers"></div>

<div class="heart-layer"
id="hearts"></div>


<div class="container"
id="giftPage">

    <div class="gift"
    onclick="showPassword()">

        🎁

    </div>

    <div class="openText">

        🌻 برای باز کردن هدیه کلیک کن 🌻

    </div>

</div>


<div class="container"
id="passwordPage">

    <div class="card">

        <h1>
            🔐 هدیه مخصوص تو
        </h1>

        <p>
            تاریخ تولدت رو وارد کن ❤️
        </p>

        <input
        id="password"
        type="password"
        maxlength="20"
        placeholder="رمز مخصوص">

        <button
        onclick="checkPassword()">

            🌻 باز کردن هدیه

        </button>

        <p
        id="error"
        style="
        display:none;
        color:#ff5577;
        margin-top:15px">

            ❌ رمز اشتباهه

        </p>

    </div>

</div>


<div class="container"
id="birthdayPage">

    <div class="card">

        <h1>

            🌻🎂 تولدت مبارک نسا 🎂🌻

        </h1>

        <div class="message">

            امروز روزی نیست که فقط تولد تو را جشن بگیرم...

            <br>

            امروز روزی است که
            از بودن تو در این دنیا خوشحالم. ❤️

            <br><br>

            تو یکی از زیباترین
            اتفاق‌های زندگی منی.

            <br><br>

            🌻 امیدوارم همیشه بخندی،
            همیشه خوشحال باشی
            و به تمام آرزوهایت برسی.

            <br><br>

            ❤️ تولدت مبارک عشق من ❤️

            <br>

            🌻 دوستت دارم 🌻

        </div>

        <img
        class="photo"
        src="https://i.postimg.cc/5tDhyRgM/IMG-20260318-184739-714.jpg">

    </div>

</div>


<script>

const PASSWORD =
"1386";


function showPassword(){

    document.getElementById(
        "giftPage"
    ).style.display="none";

    document.getElementById(
        "passwordPage"
    ).style.display="block";

    document.getElementById(
        "password"
    ).focus();
}


function checkPassword(){

    const input =
    document.getElementById(
        "password"
    ).value.trim();

    if(input === PASSWORD){

        document.getElementById(
            "passwordPage"
        ).style.display="none";

        document.getElementById(
            "birthdayPage"
        ).style.display="block";

        startFlowers();

        startHearts();

    }else{

        document.getElementById(
            "error"
        ).style.display="block";

    }
}


/* گل‌های فراوان */

function startFlowers(){

    const flowers=[
        "🌻",
        "🌼",
        "🌺",
        "🌸",
        "💐",
        "🌷",
        "🪻",
        "🌹"
    ];

    const container =
    document.getElementById(
        "flowers"
    );

    for(let i=0;i<90;i++){

        const flower =
        document.createElement(
            "div"
        );

        flower.className="flower";

        flower.textContent =
        flowers[
            Math.floor(
                Math.random()
                * flowers.length
            )
        ];

        flower.style.left =
        Math.random()*100+"%";

        flower.style.fontSize =
        (18+Math.random()*35)+"px";

        flower.style.animationDuration =
        (5+Math.random()*8)+"s";

        flower.style.animationDelay =
        Math.random()*6+"s";

        container.appendChild(
            flower
        );

        setTimeout(
            ()=>{
                flower.remove();
            },
            16000
        );
    }
}


/* قلب‌های فراوان */

function startHearts(){

    const hearts=[
        "❤️",
        "💖",
        "💕",
        "💗",
        "💘",
        "❤️‍🔥"
    ];

    const container =
    document.getElementById(
        "hearts"
    );

    for(let i=0;i<80;i++){

        const heart =
        document.createElement(
            "div"
        );

        heart.className="heart";

        heart.textContent =
        hearts[
            Math.floor(
                Math.random()
                * hearts.length
            )
        ];

        heart.style.left =
        Math.random()*100+"%";

        heart.style.fontSize =
        (14+Math.random()*30)+"px";

        heart.style.animationDuration =
        (4+Math.random()*7)+"s";

        heart.style.animationDelay =
        Math.random()*6+"s";

        container.appendChild(
            heart
        );

        setTimeout(
            ()=>{
                heart.remove();
            },
            15000
        );
    }
}


document.getElementById(
    "password"
).addEventListener(
    "keydown",
    function(e){

        if(e.key==="Enter"){
            checkPassword();
        }

    }
);

</script>

</body>
</html>
"""


# ============================================================
# صفحه عشق
# ============================================================

LOVE_PAGE = r"""
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width,initial-scale=1">

<title>I LOVE YOU NESA ❤️</title>

<style>

*{
    margin:0;
    padding:0;
    box-sizing:border-box;
}

body{

    min-height:100vh;

    background:#030303;

    display:flex;

    justify-content:center;

    align-items:center;

    overflow:hidden;
}

canvas{

    max-width:100vw;

    max-height:100vh;

    display:block;
}

.title{

    position:fixed;

    top:20px;

    width:100%;

    text-align:center;

    color:#ff6688;

    font-family:Arial;

    font-size:18px;

    letter-spacing:5px;

    text-shadow:
    0 0 15px #ff2244,
    0 0 35px #ff2244;

    z-index:20;
}

</style>

</head>

<body>

<div class="title">

❤️ I LOVE YOU NESA ❤️

</div>

<canvas id="canvas"></canvas>

<script>

const imageUrl =
"https://i.postimg.cc/5tDhyRgM/IMG-20260318-184739-714.jpg";

const canvas =
document.getElementById("canvas");

const ctx =
canvas.getContext("2d");

const img =
new Image();

img.crossOrigin="anonymous";

img.src=imageUrl;


img.onload=function(){

    const maxWidth =
    Math.min(
        window.innerWidth,
        900
    );

    const scale =
    maxWidth / img.width;

    canvas.width =
    maxWidth;

    canvas.height =
    img.height * scale;

    ctx.drawImage(
        img,
        0,
        0,
        canvas.width,
        canvas.height
    );

    const pixels =
    ctx.getImageData(
        0,
        0,
        canvas.width,
        canvas.height
    ).data;

    ctx.fillStyle="#020202";

    ctx.fillRect(
        0,
        0,
        canvas.width,
        canvas.height
    );

    const words=[
        "I",
        "LOVE",
        "YOU",
        "NESA"
    ];

    ctx.textAlign="center";
    ctx.textBaseline="middle";
    ctx.font="7px Arial";

    const step=7;

    for(
        let y=0;
        y<canvas.height;
        y+=step
    ){

        for(
            let x=0;
            x<canvas.width;
            x+=step
        ){

            const index=
            (y*canvas.width+x)*4;

            const r=
            pixels[index];

            const g=
            pixels[index+1];

            const b=
            pixels[index+2];

            const brightness=
            (r+g+b)/3;

            if(brightness<25){
                continue;
            }

            ctx.fillStyle=
            `rgb(${r},${g},${b})`;

            const word=
            words[
                Math.floor(
                    (x+y)/step
                )
                % words.length
            ];

            ctx.fillText(
                word,
                x,
                y
            );
        }
    }
};

</script>

</body>

</html>
"""


# ============================================================
# Webhook
# ============================================================

@app.route("/", methods=["GET", "POST"])
def webhook():

    if request.method == "GET":
        return "❤️ Bot is alive.", 200

    try:

        data = request.get_json(silent=True)  # ✅ خطا رفع شد

        if not data:
            return "OK", 200

        message = data.get("message")

        if not message:
            return "OK", 200

        chat = message.get("chat", {})
        chat_id = chat.get("id")
        text = message.get("text", "")

        if chat_id is not None:

            threading.Thread(
                target=handle_message,
                args=(chat_id, text),
                daemon=True
            ).start()

    except Exception as e:

        print("Webhook error:", e)

    return "OK", 200


# ============================================================
# صفحات سایت
# ============================================================

@app.route("/love")
def love():

    return render_template_string(
        LOVE_PAGE
    )


@app.route("/birthday_surprise.html")
def birthday():

    return render_template_string(
        BIRTHDAY_PAGE
    )


@app.route("/health")
def health():

    return {
        "status": "ok",
        "bot": bool(TOKEN),
        "time": iran_now().isoformat()
    }, 200


# ============================================================
# Webhook Telegram
# ============================================================

def set_webhook():

    if not TOKEN:
        print("⚠️ BOT_TOKEN تنظیم نشده است.")
        return

    webhook_url = SITE_URL + "/"

    try:

        r = requests.post(
            telegram_url("setWebhook"),
            json={
                "url": webhook_url,
                "drop_pending_updates": False
            },
            timeout=15
        )

        print("Webhook:", r.status_code, r.text)

    except Exception as e:

        print("Webhook error:", e)


# ============================================================
# اجرای برنامه
# ============================================================

if __name__ == "__main__":

    print("🚀 Bot starting...")
    print("🌐 SITE_URL:", SITE_URL)
    print("❤️ Love:", SITE_URL + "/love")
    print("🎂 Birthday:", SITE_URL + "/birthday_surprise.html")
    print("🤖 Token:", "OK" if TOKEN else "MISSING")

    # ست کردن Webhook
    set_webhook()

    # تایمر تولد
    threading.Thread(
        target=birthday_timer,
        daemon=True
    ).start()

    port = int(os.environ.get("PORT", "10000"))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        threaded=True
    )
