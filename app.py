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

# ⚠️ توکن جدید رباتت را اینجا قرار بده
TOKEN ="8967116754:AAFJlNPRH8Cht-8qKo3zEHCJvSX1JrBGGXQ"

# Chat ID خودت
YOUR_CHAT_ID = "1228473012"

PASSWORD = "1386"

BIRTH_DAY = 8
BIRTH_MONTH = 8
BIRTH_HOUR = 0
BIRTH_MINUTE = 0

IRAN_OFFSET = datetime.timedelta(hours=3, minutes=30)

user_access = {}


# ============================================================
# 🕐 زمان ایران
# ============================================================

def get_current_iran_time():
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    return utc_now.astimezone(
        datetime.timezone(IRAN_OFFSET)
    )


# ============================================================
# 📸 عکسها
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
        "caption": "🌙 ماه شبهای من..."
    },

    "📸 عکس ۵": {
        "path": "photos/IMG_20260709_234307_968.jpg",
        "caption": "☀️ روشنترین روز من..."
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
فرشتهای که بعدها
تمام دنیای من شد. 🌻

🍃 تولدت مبارک، زیباترین فصل زندگی من...

هر بار که لبخند میزنی،
انگار یک گوشه از دنیا روشنتر میشود.

هر بار که صدایت را میشنوم،
قلبم آرامتر میزند.

و هر بار که به تو فکر میکنم،
میفهمم چقدر خوششانسم
که تو را در زندگیام دارم.

🌻 نسا جان...
امیدوارم امسال برایت
پر از آرامش،
خنده،
اتفاقهای قشنگ
و آرزوهای برآوردهشده باشد.

❤️ من همیشه کنارتم.
نه فقط امروز،
بلکه در تمام روزهایی که پیش رو داریم.

🎂 تولدت مبارک عشق من...
🌻 همیشه بخند
❤️ چون لبخندت زیباترین چیز دنیاست."""


# ============================================================
# 💞 متنهای روز آشنایی
# ============================================================

SECOND_QUOTES = [
    "هر ثانیهای که میگذرد، عشق من به تو عمیقتر میشود... ❤️",
    "ثانیهها میگذرند، اما عشق من به تو هرگز کهنه نمیشود... 🌹",
    "در هر ثانیهای از زندگیام، تو را نفس میکشم... 💫",
    "ثانیههای بیتو طولانیاند، اما کنار تو حتی ساعتها هم کوتاهاند... ✨",
    "هر ثانیه که میگذرد، یک دلیل تازه برای دوست داشتن تو پیدا میکنم... ❤️",
    "ثانیهها را بشمار، اما عشق را نه؛ چون عشق من به تو بینهایت است... 🌸"
]


# ============================================================
# 💌 نامههای عاشقانه
# ============================================================

LOVE_LETTERS = [

"""💌 نامهای از دل من...

نسای من،

اگر بخواهم تمام زیباییهای دنیا را
در یک کلمه خلاصه کنم،
آن کلمه برای من «تو» است.

از وقتی وارد زندگی من شدی،
خیلی از چیزها معنای تازهای پیدا کردند.

لبخند،
دلتنگی،
انتظار،
و حتی سادهترین لحظههای زندگی.

تو همان آدمی هستی که
فکر کردن به او
میتواند یک روز معمولی را
به زیباترین روز دنیا تبدیل کند.

❤️ دوستت دارم...
نه فقط برای امروز،
بلکه برای تمام فرداهایی که هنوز نرسیدهاند.""",

"""💌 نامهای برای نسا...

نسا جان،

اگر یک روز از من بپرسند
عشق یعنی چه؟

من نمیخواهم توضیح بدهم.

فقط تو را نشانشان میدهم.

چون بعضی آدمها
تعریف عشق نیستند؛
خودِ عشقاند.

تو برای من
فقط یک نفر نیستی.

تو بخشی از آرامش،
خندهها،
فکرها
و تمام رؤیاهای منی.

🌹 دوستت دارم،
بیشتر از چیزی که بتوانم
با کلمات توضیحش بدهم.""",

"""💌 از طرف قلب من...

نسای من،

گاهی با خودم فکر میکنم
چطور ممکن است یک نفر
اینقدر برای آدم مهم شود؟

بعد یاد تو میافتم
و جوابم را پیدا میکنم.

تو آمدی
و آرامآرام
جایی در قلبم ساختی
که دیگر هیچکس
نمیتواند جای آن را بگیرد.

❤️ اگر تمام دنیا را داشته باشم
ولی تو نباشی،
باز هم چیزی کم است.

چیزی به اسم «تو».""",

"""💌 نامهای که فقط برای توست...

نسا جان،

من آینده را نمیدانم.

نمیدانم فردا چه اتفاقی میافتد،
اما یک چیز را خوب میدانم:

هر جا که باشم،
یک گوشه از قلبم
همیشه برای توست.

برای خندههایت،
برای حرف زدنت،
برای نگاهت
و برای تمام لحظههایی
که کنار هم میگذرانیم.

🌻 تو یکی از قشنگترین
اتفاقهای زندگی منی.

❤️ و من بابت داشتنت
هر روز خدا را شکر میکنم."""
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
# 🎂 ساعت باقیمانده تا تولد
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

def get_main_keyboard():
    return {
        "keyboard": [
            ["📸 عکسها"],
            ["🎂 تولد نسا", "📅 روز آشنایی"],
            ["⏳ ساعت تا تولدت"],
            ["💌 نامه عشق"],
            ["❤️ صفحه عشق"],
            ["🎉 تبریک برای عشقم"],
            ["🥺 میخوام آشتی کنیم"],
            ["🔙 بازگشت به منو"]
        ],
        "resize_keyboard": True
    }


# ============================================================
# 📸 منوی عکسها
# ============================================================

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
# 🥺 منوی نوشتن پیام آشتی
# ============================================================

def get_reconcile_keyboard():
    return {
        "keyboard": [
            ["🔙 لغو"]
        ],
        "resize_keyboard": True
    }


# ============================================================
# 📤 ارسال پیام تلگرام
# ============================================================

def send_message(chat_id, text, reply_markup=None):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

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
        print("send_message error:", e)

    return False


# ============================================================
# 📸 ارسال عکس
# ============================================================

def send_photo(chat_id, photo_path, caption=""):

    try:

        # عکس اینترنتی
        if photo_path.startswith("http"):

            url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

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

        # عکس محلی
        if not os.path.exists(photo_path):

            send_message(
                chat_id,
                "❌ عکس پیدا نشد!"
            )

            return False

        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

        with open(photo_path, "rb") as photo:

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
# 🤖 پردازش پیامها
# ============================================================

def handle_message(chat_id, text):

    chat_id = str(chat_id)
    text = text.strip()

    # ========================================================
    # 🥺 حالت انتظار پیام آشتی
    # ========================================================

    if user_access.get(chat_id, {}).get(
        "waiting_for_reconcile",
        False
    ):

        # لغو
        if text == "🔙 لغو":

            user_access[chat_id][
                "waiting_for_reconcile"
            ] = False

            send_message(
                chat_id,

                """باشه ❤️

هر وقت دلت خواست دوباره بیا...

اینجا همیشه بازه برای حرفهایی
که گفتنش مستقیم سخته. 🌻❤️""",

                get_main_keyboard()
            )

            return

        # اگر متن خالی بود
        if not text:

            send_message(
                chat_id,
                "🥺 یه چیزی بنویس که دلت میخواد بهش بگی ❤️"
            )

            return

        # ----------------------------------------------------
        # ارسال پیام به صاحب ربات
        # ----------------------------------------------------

        owner_message = f"""🥺💌 پیام آشتی

👤 یک پیام جدید از بخش «آشتی کنیم» داری.

💬 متن پیام:

{text}

━━━━━━━━━━━━━━
❤️ پیام از بخش آشتی ربات ارسال شده.
"""

        sent = send_message(
            YOUR_CHAT_ID,
            owner_message
        )

        # ----------------------------------------------------
        # پاسخ به پارتنر
        # ----------------------------------------------------

        user_access[chat_id][
            "waiting_for_reconcile"
        ] = False

        if sent:

            send_message(
                chat_id,

                """💌 پیامت رسید...

من فرستادمش برای کسی که باید بخونتش. ❤️

دیگه ادامهش با دلشه...

امیدوارم این پیام
شروع دوبارهی یک لبخند باشه. 🥺🌻❤️""",

                get_main_keyboard()
            )

        else:

            send_message(
                chat_id,

                """🥺 یه مشکلی پیش اومد و پیام ارسال نشد.

لطفاً چند لحظه دیگه دوباره امتحان کن ❤️""",

                get_main_keyboard()
            )

        return


    # ========================================================
    # 🥺 درخواست آشتی
    # ========================================================

    if text == "🥺 میخوام آشتی کنیم":

        user_access[chat_id] = user_access.get(
            chat_id,
            {}
        )

        user_access[chat_id][
            "waiting_for_reconcile"
        ] = True

        send_message(
            chat_id,

            """🥺❤️

اگر دلت برایش تنگ شده
ولی غرورت اجازه نمیده
مستقیم پیام بدی...

اینجا میتونی هرچی توی دلت هست
بنویسی. 💌

لازم نیست قشنگش کنی.
لازم نیست رسمی باشه.

فقط چیزی رو بنویس
که واقعاً دلت میخواد بهش بگی. ❤️

من پیامت رو براش میفرستم.

👇 حالا پیامت رو بنویس:""",

            get_reconcile_keyboard()
        )

        return


    # ========================================================
    # 🔐 پسورد
    # ========================================================

    if user_access.get(chat_id, {}).get(
        "waiting_for_password",
        False
    ):

        if text == PASSWORD:

            user_access[chat_id]["photos"] = True
            user_access[chat_id][
                "waiting_for_password"
            ] = False

            send_message(
                chat_id,

                """✅ رمز درست بود!

🔓 گالری عکسهای اختصاصی برات باز شد ❤️""",

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


    # ========================================================
    # 📸 عکسها
    # ========================================================

    if text in PHOTOS:

        if user_access.get(chat_id, {}).get(
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

            user_access[chat_id] = user_access.get(
                chat_id,
                {}
            )

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


    # ========================================================
    # 📸 گالری
    # ========================================================

    if text == "📸 عکسها":

        if user_access.get(chat_id, {}).get(
            "photos",
            False
        ):

            send_message(
                chat_id,

                "📸 کدوم عکس رو میخوای ببینی؟ ❤️",

                get_photo_keyboard()
            )

        else:

            user_access[chat_id] = user_access.get(
                chat_id,
                {}
            )

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


    # ========================================================
    # 🎂 تولد
    # ========================================================

    if text == "🎂 تولد نسا":

        send_message(
            chat_id,
            BIRTHDAY_MESSAGE
        )

        return


    # ========================================================
    # 💞 روز آشنایی
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
یک خاطرهی قشنگه.

🌻 {days} روز از قشنگترین فصل زندگی من گذشته.

⏱️ {seconds:,} ثانیه...

{seconds:,} ثانیهای که
قلبم برای تو تپیده است. ❤️

و اگر قرار باشد
تمام این ثانیهها را دوباره زندگی کنم،

باز هم تو را انتخاب میکنم.

🌹 هر ثانیهای که با یاد تو گذشت،
برای من ارزش یک عمر داشت.

📖 {quote}

❤️ از روز آشناییمان تا همیشه...

تو یکی از زیباترین
اتفاقهای زندگی منی."""

        send_message(
            chat_id,
            message
        )

        return


    # ========================================================
    # ⏳ ساعت تولد
    # ========================================================

    if text == "⏳ ساعت تا تولدت":

        hours = hours_until_birthday()

        send_message(
            chat_id,

            f"""🎂 شمارش معکوس برای روز قشنگ تو...

🌻 تولد ahu goozlum

⏳ فقط {hours:,} ساعت دیگه مونده...

هر ساعتی که میگذره،
من یک قدم به روزی نزدیکتر میشم
که دنیا قشنگتر شد؛

روزی که تو به دنیا اومدی. ❤️🌻"""
        )

        return


    # ========================================================
    # 💌 نامه عشق
    # ========================================================

    if text == "💌 نامه عشق":

        send_message(
            chat_id,
            random.choice(LOVE_LETTERS)
        )

        return


    # ========================================================
    # ❤️ صفحه عشق
    # ========================================================

    if text == "❤️ صفحه عشق":

        send_message(
            chat_id,

            """❤️ یک سورپرایز مخصوص تو آماده کردم...

چهرهات با کلمات

I LOVE YOU NESA

ساخته شده. 🌹

👇 اینجا رو باز کن:

https://nesa-bot.onrender.com/love"""
        )

        return


    # ========================================================
    # 🎉 تبریک برای عشقم
    # ========================================================

    if text == "🎉 تبریک برای عشقم":

        send_message(
            chat_id,

            """🎁 یک هدیه مخصوص برای تو آماده شده...

آروم بازش کن 🌻❤️

👇 سورپرایز تولدت:

https://nesa-bot.onrender.com/birthday_surprise.html"""
        )

        return


    # ========================================================
    # 🔙 بازگشت به منو
    # ========================================================

    if text == "🔙 بازگشت به منو":

        old_access = user_access.get(
            chat_id,
            {}
        )

        user_access[chat_id] = {

            "photos": old_access.get(
                "photos",
                False
            ),

            "waiting_for_password": False,

            "waiting_for_reconcile": False
        }

        send_message(
            chat_id,

            """🏠 برگشتیم به منوی اصلی...

🌻 هر چیزی که بخوای اینجاست ❤️""",

            get_main_keyboard()
        )

        return


    # ========================================================
    # /start
    # ========================================================

    if text == "/start":

        user_access[chat_id] = {

            "photos": False,

            "waiting_for_password": False,

            "waiting_for_reconcile": False
        }

        send_message(
            chat_id,

            """🌻❤️ به دنیای ahu goozlum خوش اومدی ❤️🌻

🎁 اینجا یک گوشه کوچیک از قلب منه...

📸 عکسهای خصوصی
🎂 تولد نسا
💞 روز آشنایی
⏳ شمارش معکوس تولد
💌 نامههای عاشقانه
❤️ صفحه عشق
🎉 سورپرایز تولد
🥺 پیام آشتی

🌻 هر دکمه یک تکه از داستان ماست...""",

            get_main_keyboard()
        )

        return


    # ========================================================
    # ❌ دستور نامعتبر
    # ========================================================

    send_message(
        chat_id,

        """❌ این دستور رو نمیشناسم.

از دکمههای پایین استفاده کن ❤️""",

        get_main_keyboard()
    )


# ============================================================
# 🎂 ارسال خودکار تولد
# ============================================================

def birthday_timer():

    sent_today = False

    while True:

        try:

            now = get_current_iran_time()

            if (
                now.month == BIRTH_MONTH
                and now.day == BIRTH_DAY
                and now.hour == BIRTH_HOUR
                and now.minute == BIRTH_MINUTE
            ):

                if not sent_today:

                    print(
                        "🎂 ارسال پیام تولد..."
                    )

                    send_message(
                        YOUR_CHAT_ID,
                        BIRTHDAY_MESSAGE
                    )

                    photo = PHOTOS[
                        "📸 عکس ۱"
                    ]

                    if os.path.exists(
                        photo["path"]
                    ):

                        send_photo(
                            YOUR_CHAT_ID,
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
# 🎂 صفحه سورپرایز تولد
# ============================================================

BIRTHDAY_SURPRISE_PAGE = r"""
<!DOCTYPE html>
<html lang="fa" dir="rtl">

<head>

<meta charset="UTF-8">

<meta
name="viewport"
content="width=device-width, initial-scale=1.0"
>

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
        circle at center,
        #32111d 0%,
        #13070c 45%,
        #050204 100%
    );

    color:white;

    font-family:
    Tahoma,
    Arial,
    sans-serif;

    overflow:hidden;

    display:flex;

    align-items:center;

    justify-content:center;
}

.container{

    width:92%;

    max-width:520px;

    text-align:center;

    position:relative;

    z-index:20;
}

#giftPage{

    animation:
    entrance 1.5s ease;
}

@keyframes entrance{

    from{
        opacity:0;
        transform:
        scale(.6)
        translateY(40px);
    }

    to{
        opacity:1;
        transform:
        scale(1)
        translateY(0);
    }
}

.gift{

    font-size:130px;

    cursor:pointer;

    filter:
    drop-shadow(
        0 0 25px
        #ff416c
    );

    animation:
    giftFloat 2.5s
    ease-in-out infinite;

    user-select:none;
}

@keyframes giftFloat{

    0%,100%{
        transform:
        translateY(0)
        rotate(-2deg);
    }

    50%{
        transform:
        translateY(-18px)
        rotate(2deg);
    }
}

.openText{

    margin-top:20px;

    color:#ffd2dc;

    font-size:18px;

    text-shadow:
    0 0 15px
    #ff416c;
}

#passwordPage,
#birthdayPage{

    display:none;
}

.card{

    padding:30px 22px;

    border-radius:28px;

    background:
    linear-gradient(
        145deg,
        rgba(70,15,30,.92),
        rgba(15,5,10,.95)
    );

    border:
    1px solid
    rgba(255,150,170,.4);

    box-shadow:
    0 0 60px
    rgba(255,50,100,.25),

    inset 0 0 30px
    rgba(255,50,100,.08);

    backdrop-filter:blur(15px);
}

.card h1{

    color:#ff7895;

    font-size:28px;

    margin-bottom:18px;

    text-shadow:
    0 0 25px
    #ff416c;
}

.card p{

    line-height:2;

    color:#ffdbe3;
}

input{

    width:100%;

    margin-top:20px;

    padding:15px;

    border-radius:16px;

    border:
    1px solid
    #ff5577;

    background:
    rgba(0,0,0,.5);

    color:white;

    outline:none;

    text-align:center;

    font-size:20px;
}

button{

    margin-top:18px;

    padding:14px 35px;

    border:none;

    border-radius:30px;

    color:white;

    background:
    linear-gradient(
        45deg,
        #ff416c,
        #ff758c
    );

    font-size:17px;

    font-weight:bold;

    cursor:pointer;

    box-shadow:
    0 0 25px
    rgba(255,65,108,.5);
}

.birthdayTitle{

    font-size:30px;

    color:#ffd36e;

    text-shadow:
    0 0 25px
    #ff9d00;
}

.message{

    margin-top:20px;

    line-height:2.1;

    color:#ffe9ee;

    font-size:16px;
}

.photo{

    width:100%;

    max-width:340px;

    margin:22px auto;

    display:block;

    border-radius:20px;

    border:
    2px solid
    rgba(255,190,100,.6);

    box-shadow:
    0 0 35px
    rgba(255,150,0,.25);
}


/* ==========================================================
   ❤️ بارش قلب
========================================================== */

.heart-rain{

    position:fixed;

    inset:0;

    width:100%;

    height:100%;

    pointer-events:none;

    z-index:999999;

    overflow:hidden;
}

.heart-rain span{

    position:absolute;

    top:-50px;

    display:block;

    animation:
    heartFall
    linear
    infinite;

    filter:
    drop-shadow(
        0 0 8px
        rgba(255,50,100,.7)
    );
}

@keyframes heartFall{

    0%{

        transform:
        translateY(-60px)
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


/* ==========================================================
   🌻 گلها
========================================================== */

.flower{

    position:fixed;

    top:-100px;

    z-index:99999;

    pointer-events:none;

    animation:
    flowerFall
    linear
    forwards;
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
        translateY(110vh)
        rotate(720deg);

        opacity:0;
    }
}


/* ==========================================================
   ❤️ قلبهای قدیمی
========================================================== */

.heart{

    position:fixed;

    top:-60px;

    z-index:99999;

    pointer-events:none;

    animation:
    heartFallOld
    linear
    forwards;
}

@keyframes heartFallOld{

    0%{

        transform:
        translateY(-60px)
        rotate(0deg);

        opacity:0;
    }

    10%{
        opacity:1;
    }

    100%{

        transform:
        translateY(110vh)
        rotate(360deg);

        opacity:0;
    }
}

.glow{

    position:fixed;

    width:250px;

    height:250px;

    border-radius:50%;

    background:#ff416c;

    filter:blur(120px);

    opacity:.12;
}

.glow.one{

    top:-80px;

    right:-80px;
}

.glow.two{

    bottom:-100px;

    left:-100px;
}

</style>

</head>

<body>

<div class="glow one"></div>

<div class="glow two"></div>

<div
class="heart-rain"
id="heartRain">
</div>


<!-- ======================================================
     🎁 هدیه
====================================================== -->

<div
class="container"
id="giftPage">

    <div
    class="gift"
    onclick="showPassword()">

        🎁

    </div>

    <div class="openText">

        🌻 برای باز کردن هدیه کلیک کن 🌻

    </div>

</div>


<!-- ======================================================
     🔐 رمز
====================================================== -->

<div
class="container"
id="passwordPage">

    <div class="card">

        <h1>
            🔐 هدیه مخصوص تو
        </h1>

        <p>
            تاریخ تولدت رو وارد کن ❤️
        </p>

        <input
        id="passwordInput"
        type="password"
        maxlength="10"
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


<!-- ======================================================
     🎂 صفحه تولد
====================================================== -->

<div
class="container"
id="birthdayPage">

    <div class="card">

        <div
        class="birthdayTitle">

            🌻🎂 تولدت مبارک نسا 🎂🌻

        </div>

        <div class="message">

            امروز روزی نیست که فقط
            تولد تو را جشن بگیرم...

            امروز روزی است که
            از بودن تو در این دنیا
            خوشحالم. ❤️

            <br><br>

            تو یکی از زیباترین
            اتفاقهای زندگی منی.

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

const PASSWORD = "1386";


/* ========================================================
   🎁 باز کردن هدیه
======================================================== */

function showPassword(){

    document.getElementById(
        "giftPage"
    ).style.display="none";

    document.getElementById(
        "passwordPage"
    ).style.display="block";

    document.getElementById(
        "passwordInput"
    ).focus();
}


/* ========================================================
   🔐 بررسی رمز
======================================================== */

function checkPassword(){

    const input =
    document
    .getElementById(
        "passwordInput"
    )
    .value
    .trim();

    if(input === PASSWORD){

        document.getElementById(
            "passwordPage"
        ).style.display="none";

        document.getElementById(
            "birthdayPage"
        ).style.display="block";

        startHeartRain();

        startFlowers();

        startHearts();

    }else{

        document.getElementById(
            "error"
        ).style.display="block";
    }
}


/* ========================================================
   ❤️ بارش قلب
======================================================== */

function startHeartRain(){

    const container =
    document.getElementById(
        "heartRain"
    );

    const emojis = [
        "❤️",
        "💖",
        "💕",
        "💗",
        "💘",
        "❤️‍🔥",
        "🌹",
        "✨"
    ];

    for(
        let i=0;
        i<60;
        i++
    ){

        const span =
        document.createElement(
            "span"
        );

        span.textContent =
        emojis[
            Math.floor(
                Math.random()
                * emojis.length
            )
        ];

        span.style.left =
        Math.random()*100+"%";

        span.style.fontSize =
        (
            14 +
            Math.random()*30
        )+"px";

        span.style.animationDuration =
        (
            4 +
            Math.random()*6
        )+"s";

        span.style.animationDelay =
        (
            Math.random()*5
        )+"s";

        container.appendChild(
            span
        );
    }
}


/* ========================================================
   🌻 گلها
======================================================== */

function startFlowers(){

    const flowers = [
        "🌻",
        "🌼",
        "🌺",
        "🌸",
        "💐",
        "🌷",
        "🪻",
        "🌹"
    ];

    for(
        let i=0;
        i<55;
        i++
    ){

        const flower =
        document.createElement(
            "div"
        );

        flower.className =
        "flower";

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
        (
            18 +
            Math.random()*28
        )+"px";

        flower.style.animationDuration =
        (
            5 +
            Math.random()*7
        )+"s";

        flower.style.animationDelay =
        Math.random()*6+"s";

        document.body.appendChild(
            flower
        );

        setTimeout(
            () => flower.remove(),
            14000
        );
    }
}


/* ========================================================
   ❤️ قلبها
======================================================== */

function startHearts(){

    const hearts = [
        "❤️",
        "💖",
        "💕",
        "💗",
        "💘",
        "❤️‍🔥"
    ];

    for(
        let i=0;
        i<50;
        i++
    ){

        const heart =
        document.createElement(
            "div"
        );

        heart.className =
        "heart";

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
        (
            14 +
            Math.random()*25
        )+"px";

        heart.style.animationDuration =
        (
            4 +
            Math.random()*6
        )+"s";

        heart.style.animationDelay =
        Math.random()*5+"s";

        document.body.appendChild(
            heart
        );

        setTimeout(
            () => heart.remove(),
            13000
        );
    }
}


/* ========================================================
   ⌨️ Enter برای رمز
======================================================== */

document
.getElementById(
    "passwordInput"
)
.addEventListener(
    "keydown",
    function(e){

        if(
            e.key === "Enter"
        ){

            checkPassword();

        }

    }
);

</script>

</body>
</html>
"""


# ============================================================
# ❤️ صفحه موزاییک
# ============================================================

PHOTO_MOSAIC_PAGE = r"""
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta
name="viewport"
content="width=device-width,initial-scale=1.0">

<title>
❤️ I Love You Nesa ❤️
</title>

<style>

*{
    margin:0;
    padding:0;
    box-sizing:border-box;
}

body{

    background:#050505;

    display:flex;

    justify-content:center;

    align-items:center;

    min-height:100vh;

    overflow:hidden;
}

canvas{

    display:block;

    max-width:100vw;

    max-height:100vh;
}

.watermark{

    position:fixed;

    bottom:20px;

    left:0;

    right:0;

    text-align:center;

    color:#ff5577;

    font-family:Arial;

    font-size:14px;

    letter-spacing:4px;

    text-shadow:
    0 0 20px
    #ff2244;
}

</style>

</head>

<body>

<canvas id="photoCanvas"></canvas>

<div class="watermark">
❤️ AHU GOOZLUM ❤️
</div>

<script>

const imageUrl =
"https://i.postimg.cc/5tDhyRgM/IMG-20260318-184739-714.jpg";

const words = [
    "I",
    "LOVE",
    "YOU",
    "NESA"
];

const canvas =
document.getElementById(
    "photoCanvas"
);

const ctx =
canvas.getContext("2d");

const img =
new Image();

img.crossOrigin="anonymous";

img.src=imageUrl;

img.onload=()=>{

    canvas.width =
    img.width;

    canvas.height =
    img.height;

    ctx.drawImage(
        img,
        0,
        0
    );

    const pixels =
    ctx.getImageData(
        0,
        0,
        canvas.width,
        canvas.height
    ).data;

    ctx.fillStyle="#000";

    ctx.fillRect(
        0,
        0,
        canvas.width,
        canvas.height
    );

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

            const index =
            (y*canvas.width+x)*4;

            const r =
            pixels[index];

            const g =
            pixels[index+1];

            const b =
            pixels[index+2];

            const bright =
            (r+g+b)/3;

            if(bright>240)
                continue;

            ctx.fillStyle =
            `rgb(${r},${g},${b})`;

            const word =
            words[
                (x+y)
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
# 🌐 مسیر اصلی
# ============================================================

@app.route(
    "/",
    methods=["GET", "POST"]
)
def webhook():

    if request.method == "POST":

        try:

            data =
            request.get_json(
                silent=True
            )

            if (
                data
                and "message" in data
            ):

                chat_id =
                data[
                    "message"
                ][
                    "chat"
                ][
                    "id"
                ]

                text =
                data[
                    "message"
                ].get(
                    "text",
                    ""
                )

                handle_message(
                    chat_id,
                    text
                )

        except Exception as e:

            print(
                "Webhook error:",
                e
            )

    return "OK", 200


# ============================================================
# ❤️ صفحه عشق
# ============================================================

@app.route("/love")
def love_page():

    return render_template_string(
        PHOTO_MOSAIC_PAGE
    )


# ============================================================
# 🎂 صفحه سورپرایز
# ============================================================

@app.route(
    "/birthday_surprise.html"
)
def birthday_surprise():

    return render_template_string(
        BIRTHDAY_SURPRISE_PAGE
    )


# ============================================================
# 🚀 اجرای برنامه
# ============================================================

if __name__ == "__main__":

    print(
        "🚀 ربات ahu goozlum روشن شد..."
    )

    print(
        f"🎂 تولد: "
        f"{BIRTH_DAY}/{BIRTH_MONTH}"
    )

    print(
        f"📸 تعداد عکسها: "
        f"{len(PHOTOS)}"
    )

    print(
        "❤️ صفحه عشق: /love"
    )

    print(
        "🎉 صفحه تولد: "
        "/birthday_surprise.html"
    )

    print(
        "🥺 قابلیت پیام آشتی فعال است."
    )

    timer_thread = threading.Thread(
        target=birthday_timer,
        daemon=True
    )

    timer_thread.start()

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
