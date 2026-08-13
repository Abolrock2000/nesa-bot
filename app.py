from flask import Flask, request, render_template_string, send_from_directory
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
PASSWORD = "1386"

BIRTH_DAY = 8
BIRTH_MONTH = 8
BIRTH_HOUR = 0
BIRTH_MINUTE = 0

IRAN_OFFSET = datetime.timedelta(hours=3, minutes=30)

user_access = {}

WEBSITE_URL = "https://abolfazll-bot.onrender.com"


# ============================================================
# 🕐 زمان ایران
# ============================================================

def get_current_iran_time():
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    return utc_now.astimezone(datetime.timezone(IRAN_OFFSET))


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
    "هر ثانیه که می‌گذرد، یک دلیل تازه برای دوست داشتن تو پیدا می‌کنم... ❤️",
    "ثانیه‌ها را بشمار، اما عشق را نه؛ چون عشق من به تو بی‌نهایت است... 🌸"
]


# ============================================================
# 💌 نامه‌های عاشقانه
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

تو همان آدمی هستی که
فکر کردن به او
می‌تواند یک روز معمولی را
به زیباترین روز دنیا تبدیل کند.

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

تو برای من
فقط یک نفر نیستی.

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

چیزی به اسم «تو».""",
    """💌 نامه‌ای که فقط برای توست...

نسا جان،

من آینده را نمی‌دانم.

نمی‌دانم فردا چه اتفاقی می‌افتد،
اما یک چیز را خوب می‌دانم:

هر جا که باشم،
یک گوشه از قلبم
همیشه برای توست.

برای خنده‌هایت،
برای حرف زدنت،
برای نگاهت
و برای تمام لحظه‌هایی
که کنار هم می‌گذرانیم.

🌻 تو یکی از قشنگ‌ترین
اتفاق‌های زندگی منی.

❤️ و من بابت داشتنت
هر روز خدا را شکر می‌کنم."""
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

def get_main_keyboard():
    return {
        "keyboard": [
            ["📸 عکس‌ها"],
            ["🎂 تولد نسا", "📅 روز آشنایی"],
            ["⏳ ساعت تا تولدت"],
            ["💌 نامه عشق"],
            ["❤️ صفحه عشق"],
            ["🎉 تبریک برای عشقم"],
            ["🌹 رز برای نسا"],
            ["🥺 میخوام آشتی کنیم"],
            ["💬 چت دوطرفه"],
            ["🔙 بازگشت به منو"]
        ],
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
# 📤 ارسال پیام تلگرام
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
# 📸 ارسال عکس
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
# 🌹 صفحه رز برای نسا
# ============================================================

ROSE_PAGE = r"""
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌹 Rose Blooming for Nesa ❤️</title>
    <meta name="description" content="A beautiful blooming 3D rose for Nesa">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link
        href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400;1,700&family=Inter:wght@500;700&family=Fira+Code:wght@500&display=swap"
        rel="stylesheet">
    <style>
        *,
        *::before,
        *::after {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html,
        body {
            width: 100%;
            height: 100%;
            overflow: hidden;
            font-family: 'Inter', sans-serif;
        }

        body {
            background: #020002;
            background: radial-gradient(ellipse at 50% 75%, #120105 0%, #050002 55%, #000 100%);
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .vignette {
            position: fixed;
            inset: 0;
            background: radial-gradient(ellipse at center, transparent 35%, rgba(0, 0, 0, 0.9) 100%);
            z-index: 100;
            pointer-events: none;
        }

        .spotlight {
            position: fixed;
            top: 35%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 85vw;
            height: 85vh;
            background: radial-gradient(circle, rgba(255, 30, 80, 0.06) 0%, transparent 70%);
            filter: blur(50px);
            pointer-events: none;
            z-index: 1;
        }

        .trigger-overlay {
            position: fixed;
            inset: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            z-index: 200;
            opacity: 1;
            transition: opacity 0.8s cubic-bezier(0.25, 1, 0.5, 1), visibility 0.8s;
            visibility: visible;
        }

        .trigger-overlay.fade-out {
            opacity: 0;
            visibility: hidden;
            pointer-events: none;
        }

        .glass-card {
            position: relative;
            width: min(85vw, 340px);
            background: rgba(22, 10, 15, 0.55);
            border: 1px solid rgba(255, 40, 100, 0.2);
            border-radius: 24px;
            padding: 35px 24px;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.6), 0 0 40px rgba(255, 30, 80, 0.1);
            transform: scale(1);
            transition: transform 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
            overflow: hidden;
        }

        .trigger-overlay.fade-out .glass-card {
            transform: scale(0.85);
        }

        .card-glow {
            position: absolute;
            width: 150px;
            height: 150px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(255, 30, 80, 0.15) 0%, transparent 70%);
            top: -40px;
            left: -40px;
            filter: blur(15px);
            pointer-events: none;
        }

        .rose-icon {
            font-size: 54px;
            margin-bottom: 12px;
            filter: drop-shadow(0 4px 12px rgba(255, 30, 80, 0.4));
            animation: pulseIcon 2s ease-in-out infinite;
        }

        @keyframes pulseIcon {

            0%,
            100% {
                transform: scale(1);
            }

            50% {
                transform: scale(1.08);
            }
        }

        .glass-card .title {
            color: #fff;
            font-family: 'Playfair Display', serif;
            font-size: 26px;
            font-weight: 700;
            letter-spacing: 1px;
            margin-bottom: 22px;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.1);
        }

        .loading-bar-container {
            width: 100%;
            height: 6px;
            background: rgba(255, 255, 255, 0.06);
            border-radius: 3px;
            overflow: hidden;
            margin-bottom: 10px;
        }

        .loading-bar {
            width: 0%;
            height: 100%;
            background: linear-gradient(to right, #ff2e5e, #ff0044);
            border-radius: 3px;
            transition: width 0.1s linear;
        }

        .status-text {
            font-size: 12px;
            color: #b5a2b0;
            font-family: 'Fira Code', monospace;
            margin-bottom: 26px;
        }

        .start-button {
            position: relative;
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #ff2e5e 0%, #ff0044 100%);
            border: none;
            border-radius: 12px;
            color: #fff;
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            font-size: 14px;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            cursor: pointer;
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s, opacity 0.3s;
            box-shadow: 0 5px 20px rgba(255, 0, 68, 0.3);
        }

        .start-button:disabled {
            background: rgba(255, 255, 255, 0.08);
            color: rgba(255, 255, 255, 0.3);
            cursor: not-allowed;
            box-shadow: none;
            transform: none !important;
        }

        .start-button:not(:disabled):hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(255, 0, 68, 0.5), 0 0 15px rgba(255, 50, 90, 0.3);
        }

        .start-button:active {
            transform: translateY(1px);
        }

        .btn-shine {
            position: absolute;
            top: 0;
            left: -100%;
            width: 50%;
            height: 100%;
            background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.2), transparent);
            transform: skewX(-25deg);
        }

        .start-button:not(:disabled):hover .btn-shine {
            animation: shine 1.2s ease-in-out infinite;
        }

        @keyframes shine {
            100% {
                left: 150%;
            }
        }

        .ambient-light {
            position: fixed;
            width: 500px;
            height: 500px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(255, 30, 60, 0.10) 0%, rgba(255, 20, 50, 0.04) 40%, transparent 65%);
            top: 32%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 5;
            pointer-events: none;
            opacity: 0;
            transition: opacity 3s ease;
        }

        .ambient-light.visible {
            opacity: 1;
        }

        .scene {
            perspective: 1200px;
            perspective-origin: 50% 35%;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            padding-bottom: 6vh;
            z-index: 20;
            transform: scale(0.95);
        }

        .rose-wrapper {
            transform-style: preserve-3d;
            position: relative;
            width: 300px;
            height: 480px;
            transform: rotateX(-22deg) rotateY(0deg);
            will-change: transform;
        }

        .rose-wrapper.rotating {
            animation: rotateRose 28s linear infinite;
        }

        @keyframes rotateRose {
            from {
                transform: rotateX(-22deg) rotateY(0deg);
            }

            to {
                transform: rotateX(-22deg) rotateY(360deg);
            }
        }

        .stem-group {
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 10px;
            height: 250px;
            transform-style: preserve-3d;
        }

        .stem {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 0%;
            background: linear-gradient(to top, #092e12 0%, #114c23 30%, #1a6f35 70%, #114c23 100%);
            border-radius: 5px;
            transition: height 2.2s cubic-bezier(0.22, 1, 0.36, 1);
            overflow: hidden;
            will-change: height;
        }

        .stem.grow {
            height: 100%;
        }

        .stem-highlight {
            position: absolute;
            top: 0;
            left: 1px;
            width: 2.5px;
            height: 100%;
            background: linear-gradient(to bottom, transparent, rgba(150, 255, 180, 0.15), transparent);
        }

        .thorn {
            position: absolute;
            width: 11px;
            height: 6px;
            opacity: 0;
            transition: opacity 0.5s ease 0.4s;
            z-index: 2;
        }

        .thorn::before {
            content: '';
            position: absolute;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #1a6f35, #092e12);
            clip-path: polygon(0% 85%, 100% 50%, 30% 0%);
        }

        .thorn-1 {
            right: -9px;
            bottom: 65%;
            transform: scaleX(-1);
        }

        .thorn-2 {
            left: -9px;
            bottom: 42%;
        }

        .stem.grow~.thorn {
            opacity: 0.75;
        }

        .leaf {
            position: absolute;
            width: 52px;
            height: 25px;
            opacity: 0;
            transition: opacity 0.6s ease, transform 1.1s cubic-bezier(0.34, 1.45, 0.64, 1);
            z-index: 2;
            will-change: transform, opacity;
        }

        .leaf::before {
            content: '';
            position: absolute;
            width: 100%;
            height: 100%;
            background: linear-gradient(160deg, #2a944e 0%, #1a6f35 40%, #092e12 100%);
            border-radius: 2px 65% 2px 65%;
        }

        .leaf-vein {
            position: absolute;
            width: 60%;
            height: 1px;
            background: rgba(150, 255, 180, 0.12);
            top: 48%;
            left: 20%;
            z-index: 1;
        }

        .leaf-left {
            left: -52px;
            bottom: 56%;
            transform-origin: right center;
            transform: rotate(35deg) scale(0);
        }

        .leaf-left::before {
            border-radius: 65% 2px 65% 2px;
        }

        .leaf-right {
            left: 10px;
            bottom: 38%;
            transform-origin: left center;
            transform: rotate(-35deg) scale(0);
        }

        .leaf-right::before {
            border-radius: 2px 65% 2px 65%;
        }

        .leaf.visible {
            opacity: 1;
        }

        .leaf-left.visible {
            transform: rotate(15deg) scale(1);
        }

        .leaf-right.visible {
            transform: rotate(-15deg) scale(1);
        }

        .calyx {
            position: absolute;
            bottom: 242px;
            left: 50%;
            transform: translateX(-50%);
            width: 0;
            height: 0;
            transform-style: preserve-3d;
            z-index: 1;
        }

        .sepal {
            position: absolute;
            bottom: -4px;
            left: 50%;
            width: 14px;
            height: 32px;
            transform-origin: 50% 100%;
            background: linear-gradient(to top, #092e12 0%, #15582b 40%, #299c4c 100%);
            border-radius: 50% 50% 10% 10% / 80% 80% 20% 20%;
            clip-path: polygon(10% 100%, 0% 30%, 50% 0%, 100% 30%, 90% 100%);
            opacity: 0;
            transform: translateX(-50%) rotateY(var(--sepal-angle, 0deg)) rotateX(60deg) scale(0.5);
            transition: transform 1.3s cubic-bezier(0.25, 1, 0.5, 1) var(--sepal-delay, 0s), opacity 0.5s ease var(--sepal-delay, 0s);
            will-change: transform, opacity;
        }

        .calyx.visible .sepal {
            opacity: 0.95;
            transform: translateX(-50%) rotateY(var(--sepal-angle, 0deg)) rotateX(var(--sepal-curl, 22deg)) scale(1);
        }

        .rose-head {
            position: absolute;
            bottom: 245px;
            left: 50%;
            transform: translateX(-50%);
            width: 0;
            height: 0;
            transform-style: preserve-3d;
            z-index: 10;
        }

        .rose-glow {
            position: absolute;
            width: 400px;
            height: 400px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(160, 5, 30, 0.18) 0%, rgba(100, 0, 20, 0.05) 45%, transparent 65%);
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            opacity: 0;
            transition: opacity 3.5s ease;
            z-index: -1;
            pointer-events: none;
        }

        .rose-glow-inner {
            position: absolute;
            width: 200px;
            height: 200px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(180, 40, 60, 0.15) 0%, transparent 65%);
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            opacity: 0;
            transition: opacity 2s ease 0.8s;
            z-index: -1;
            pointer-events: none;
        }

        .rose-head.blooming .rose-glow {
            opacity: 1;
        }

        .rose-head.blooming .rose-glow-inner {
            opacity: 1;
        }

        .petal {
            position: absolute;
            bottom: 0;
            left: 50%;
            transform-origin: 50% 100%;
            opacity: 0.002;
            will-change: transform, opacity;
            border-radius: 50% 50% 35% 35% / 45% 45% 55% 55%;
            transform: translateX(-50%) rotateY(var(--angle, 0deg)) translateZ(0px) rotateX(90deg) scale(0.1);
            transition: transform var(--bloom-dur, 2.4s) ease-in-out var(--delay, 0s), opacity 0.7s ease var(--delay, 0s);
        }

        .rose-head.blooming .petal {
            opacity: 1;
            transform: translateX(-50%) rotateY(var(--angle, 0deg)) translateZ(var(--tz, 0px)) rotateX(var(--curl, 30deg)) scale(var(--scale, 1));
        }

        .petal-bud {
            background: linear-gradient(to bottom, #3d0008 0%, #220003 40%, #100001 75%, #040000 100%);
        }

        .petal-core {
            background: linear-gradient(to bottom, #52000c 0%, #350005 40%, #1a0002 75%, #080000 100%);
        }

        .petal-inner {
            background: linear-gradient(to bottom, #6d0012 0%, #480008 40%, #250003 75%, #0c0000 100%);
        }

        .petal-mid-inner {
            background: linear-gradient(to bottom, #850018 0%, #5c000d 40%, #310004 75%, #120000 100%);
        }

        .petal-mid {
            background: linear-gradient(to bottom, #9a001d 0%, #6e0011 40%, #3b0005 75%, #160000 100%);
        }

        .petal-outer {
            background: linear-gradient(to bottom, #ad0022 0%, #7e0014 40%, #440007 75%, #1a0001 100%);
        }

        .petal-blush {
            background: linear-gradient(to bottom, #bf0028 0%, #8e0018 40%, #4e0008 75%, #1e0001 100%);
        }

        .falling-petal {
            position: fixed;
            width: var(--fp-w, 13px);
            height: var(--fp-h, 17px);
            background: radial-gradient(ellipse at 40% 30%, var(--fp-c1, #9a001d), var(--fp-c2, #3d0008) 75%);
            border-radius: 50% 50% 45% 55% / 60% 60% 40% 40%;
            opacity: 0;
            pointer-events: none;
            z-index: 50;
            animation: fallSway var(--f-dur, 7s) linear forwards;
            animation-delay: var(--f-delay, 0s);
            will-change: transform, opacity;
        }

        @keyframes fallSway {
            0% {
                opacity: 0;
                transform: translateX(0) translateY(0) rotate(0deg) rotateY(0deg) scale(1);
            }

            8% {
                opacity: 0.85;
            }

            25% {
                transform: translateX(var(--s1, 35px)) translateY(20vh) rotate(70deg) rotateY(40deg) scale(0.95);
            }

            50% {
                transform: translateX(var(--s2, -25px)) translateY(48vh) rotate(160deg) rotateY(90deg) scale(0.88);
            }

            75% {
                transform: translateX(var(--s3, 35px)) translateY(75vh) rotate(270deg) rotateY(150deg) scale(0.78);
                opacity: 0.55;
            }

            100% {
                opacity: 0;
                transform: translateX(var(--s4, 10px)) translateY(108vh) rotate(390deg) rotateY(210deg) scale(0.55);
            }
        }

        .end-text {
            position: fixed;
            bottom: 8%;
            left: 50%;
            transform: translateX(-50%);
            text-align: center;
            opacity: 0;
            transition: opacity 2s ease;
            z-index: 60;
        }

        .end-text.visible {
            opacity: 1;
        }

        .tagline {
            font-family: 'Playfair Display', serif;
            font-style: italic;
            font-size: clamp(18px, 5.5vw, 30px);
            color: rgba(255, 195, 215, 0.95);
            letter-spacing: 4px;
            text-transform: lowercase;
            text-shadow: 0 0 25px rgba(255, 80, 130, 0.4), 0 0 60px rgba(255, 50, 100, 0.15);
            margin-bottom: 8px;
        }

        .rose-emoji {
            font-size: 32px;
            display: block;
            animation: floatEmoji 3s ease-in-out infinite;
        }

        @keyframes floatEmoji {

            0%,
            100% {
                transform: translateY(0);
            }

            50% {
                transform: translateY(-8px);
            }
        }

        @media (max-width: 480px) {
            .rose-wrapper {
                transform: scale(0.82);
            }

            .tagline {
                letter-spacing: 2px;
            }
        }

        @media (max-height: 600px) {
            .rose-wrapper {
                transform: scale(0.68);
            }

            .end-text {
                bottom: 3%;
            }
        }
    </style>
</head>

<body>
    <div class="vignette"></div>
    <div class="spotlight"></div>
    <div class="ambient-light" id="ambientLight"></div>

    <div class="trigger-overlay" id="triggerOverlay">
        <div class="glass-card">
            <div class="card-glow"></div>
            <div class="rose-icon">🌹</div>
            <h2 class="title">برای نسا 🌹</h2>
            <div class="loading-bar-container">
                <div class="loading-bar" id="loadingBar"></div>
            </div>
            <p class="status-text" id="statusText">در حال آماده‌سازی...</p>
            <button class="start-button" id="startButton" disabled>
                <span class="btn-text">🌸 برای شکوفه کردن بزن</span>
                <span class="btn-shine"></span>
            </button>
        </div>
    </div>

    <div class="scene">
        <div class="rose-wrapper" id="roseWrapper">
            <div class="stem-group">
                <div class="stem" id="stem">
                    <div class="stem-highlight"></div>
                </div>
                <div class="thorn thorn-1" id="thorn1"></div>
                <div class="thorn thorn-2" id="thorn2"></div>
                <div class="leaf leaf-left" id="leafLeft">
                    <div class="leaf-vein"></div>
                </div>
                <div class="leaf leaf-right" id="leafRight">
                    <div class="leaf-vein"></div>
                </div>
            </div>

            <div class="calyx" id="calyx"></div>

            <div class="rose-head" id="roseHead">
                <div class="rose-glow"></div>
                <div class="rose-glow-inner"></div>
            </div>
        </div>
    </div>

    <div class="end-text" id="endText">
        <p class="tagline" id="tagline">❤️ این رز رو برای تو کد زدم ❤️</p>
        <span class="rose-emoji">🌹</span>
    </div>

    <div id="fallingPetals"></div>

    <script>
        document.addEventListener('DOMContentLoaded', () => {

            const triggerOverlay = document.getElementById('triggerOverlay');
            const startButton = document.getElementById('startButton');
            const loadingBar = document.getElementById('loadingBar');
            const statusText = document.getElementById('statusText');
            const ambientLight = document.getElementById('ambientLight');
            const roseWrapper = document.getElementById('roseWrapper');
            const roseHead = document.getElementById('roseHead');
            const calyx = document.getElementById('calyx');
            const stem = document.getElementById('stem');
            const leafLeft = document.getElementById('leafLeft');
            const leafRight = document.getElementById('leafRight');
            const endText = document.getElementById('endText');
            const fallingPetalsEl = document.getElementById('fallingPetals');

            const PETAL_LAYERS = [
                { count: 4, w: 24, h: 46, curl: 78, delayBase: 0, tz: 2, cls: 'petal-bud' },
                { count: 5, w: 34, h: 58, curl: 65, delayBase: 0.25, tz: 9, cls: 'petal-core' },
                { count: 6, w: 46, h: 72, curl: 48, delayBase: 0.55, tz: 18, cls: 'petal-inner' },
                { count: 7, w: 58, h: 88, curl: 22, delayBase: 0.90, tz: 30, cls: 'petal-mid-inner' },
                { count: 8, w: 72, h: 104, curl: -5, delayBase: 1.30, tz: 44, cls: 'petal-mid' },
                { count: 9, w: 86, h: 118, curl: -25, delayBase: 1.75, tz: 60, cls: 'petal-outer' },
                { count: 10, w: 98, h: 130, curl: -48, delayBase: 2.25, tz: 76, cls: 'petal-blush' },
            ];

            const SEPALS_COUNT = 5;

            const FALLING_PETAL_COLORS = [
                ['#9a001d', '#3d0008'],
                ['#850018', '#2b0005'],
                ['#ad0022', '#480008'],
                ['#bf0028', '#52000c'],
            ];

            let fallingPetalInterval = null;

            function startCardLoader() {
                const duration = 2400;
                const steps = [
                    { threshold: 20, text: 'در حال بارگذاری Love.css...' },
                    { threshold: 50, text: 'در حال رشد گلبرگ‌ها...' },
                    { threshold: 80, text: 'افزودن بافت مخملی...' },
                    { threshold: 95, text: 'بهینه‌سازی رندرینگ...' },
                    { threshold: 100, text: 'آماده برای شکوفه! 🌹' }
                ];

                let startTimestamp = null;

                function animateLoader(timestamp) {
                    if (!startTimestamp) startTimestamp = timestamp;
                    const progress = Math.min((timestamp - startTimestamp) / duration, 1);
                    const percent = Math.floor(progress * 100);

                    loadingBar.style.width = `${percent}%`;
                    const activeStep = steps.find(s => percent <= s.threshold) || steps[steps.length - 1];
                    statusText.textContent = activeStep.text;

                    if (progress < 1) {
                        requestAnimationFrame(animateLoader);
                    } else {
                        startButton.removeAttribute('disabled');
                    }
                }

                requestAnimationFrame(animateLoader);
            }

            function createSepals() {
                const step = 360 / SEPALS_COUNT;
                for (let i = 0; i < SEPALS_COUNT; i++) {
                    const sepal = document.createElement('div');
                    sepal.className = 'sepal';
                    const angle = i * step + (Math.random() - 0.5) * 5;
                    const delay = 0.3 + i * 0.06;
                    const curl = 18 + Math.random() * 8;

                    sepal.style.setProperty('--sepal-angle', `${angle}deg`);
                    sepal.style.setProperty('--sepal-curl', `${curl}deg`);
                    sepal.style.setProperty('--sepal-delay', `${delay}s`);
                    calyx.appendChild(sepal);
                }
            }

            function createPetals() {
                PETAL_LAYERS.forEach((layer, li) => {
                    const angleStep = 360 / layer.count;
                    const layerOffset = li * 24 + (Math.random() - 0.5) * 8;

                    for (let i = 0; i < layer.count; i++) {
                        const petal = document.createElement('div');
                        petal.className = `petal ${layer.cls}`;

                        const angle = layerOffset + i * angleStep + (Math.random() - 0.5) * 5;
                        const delay = layer.delayBase + i * 0.05;
                        const curlJitter = (Math.random() - 0.5) * 6;
                        const scaleJitter = 0.94 + Math.random() * 0.12;
                        const bloomDur = 2.1 + Math.random() * 0.4;

                        petal.style.width = `${layer.w}px`;
                        petal.style.height = `${layer.h}px`;
                        petal.style.setProperty('--angle', `${angle}deg`);
                        petal.style.setProperty('--curl', `${layer.curl + curlJitter}deg`);
                        petal.style.setProperty('--scale', scaleJitter);
                        petal.style.setProperty('--delay', `${delay}s`);
                        petal.style.setProperty('--tz', `${layer.tz}px`);
                        petal.style.setProperty('--bloom-dur', `${bloomDur}s`);

                        roseHead.appendChild(petal);
                    }
                });
            }

            function growStem() {
                return new Promise(resolve => {
                    stem.classList.add('grow');

                    setTimeout(() => {
                        leafLeft.classList.add('visible');
                    }, 800);

                    setTimeout(() => {
                        leafRight.classList.add('visible');
                    }, 1100);

                    setTimeout(resolve, 2200);
                });
            }

            function bloom() {
                calyx.classList.add('visible');
                ambientLight.classList.add('visible');
                roseHead.classList.add('blooming');
            }

            function spawnFallingPetal() {
                if (fallingPetalsEl.childElementCount > 10) return;

                const petal = document.createElement('div');
                petal.className = 'falling-petal';

                const w = 10 + Math.random() * 12;
                const h = w * (1.25 + Math.random() * 0.15);
                const x = 20 + Math.random() * 60;
                const y = 3 + Math.random() * 10;
                const dur = 5.5 + Math.random() * 3.5;
                const delay = Math.random() * 0.6;

                const colors = FALLING_PETAL_COLORS[Math.floor(Math.random() * FALLING_PETAL_COLORS.length)];

                const sign = () => (Math.random() > 0.5 ? 1 : -1);
                const s1 = sign() * (15 + Math.random() * 25);
                const s2 = sign() * (10 + Math.random() * 20);
                const s3 = sign() * (20 + Math.random() * 30);
                const s4 = sign() * (10 + Math.random() * 15);

                petal.style.left = `${x}vw`;
                petal.style.top = `${y}vh`;
                petal.style.setProperty('--fp-w', `${w}px`);
                petal.style.setProperty('--fp-h', `${h}px`);
                petal.style.setProperty('--fp-c1', colors[0]);
                petal.style.setProperty('--fp-c2', colors[1]);
                petal.style.setProperty('--f-dur', `${dur}s`);
                petal.style.setProperty('--f-delay', `${delay}s`);
                petal.style.setProperty('--s1', `${s1}px`);
                petal.style.setProperty('--s2', `${s2}px`);
                petal.style.setProperty('--s3', `${s3}px`);
                petal.style.setProperty('--s4', `${s4}px`);

                fallingPetalsEl.appendChild(petal);

                setTimeout(() => {
                    if (petal.parentNode) petal.remove();
                }, (dur + delay) * 1000 + 300);
            }

            function startFallingPetals() {
                for (let i = 0; i < 3; i++) {
                    setTimeout(() => spawnFallingPetal(), i * 300);
                }

                fallingPetalInterval = setInterval(() => {
                    spawnFallingPetal();
                }, 2200);
            }

            async function startAnimationSequence() {
                await growStem();
                await delay(100);
                bloom();

                setTimeout(() => {
                    roseWrapper.classList.add('rotating');
                }, 2600);

                setTimeout(() => startFallingPetals(), 3400);

                setTimeout(() => {
                    endText.classList.add('visible');
                }, 4600);
            }

            function delay(ms) {
                return new Promise(resolve => setTimeout(resolve, ms));
            }

            startButton.addEventListener('click', () => {
                triggerOverlay.classList.add('fade-out');

                setTimeout(() => {
                    startAnimationSequence();
                }, 800);
            });

            createSepals();
            createPetals();

            setTimeout(() => {
                startCardLoader();
            }, 400);

        });
    </script>
</body>

</html>
"""


# ============================================================
# 🤖 پردازش پیام‌ها
# ============================================================

def handle_message(chat_id, text):
    chat_id = str(chat_id)
    text = text.strip()

    # ========================================================
    # 💬 حالت چت دوطرفه - ارسال پیام
    # ========================================================
    
    if user_access.get(chat_id, {}).get("waiting_for_chat_message", False):
        if text == "🔙 لغو" or text == "🔙 بازگشت به منو":
            user_access[chat_id]["waiting_for_chat_message"] = False
            send_message(chat_id, "❌ ارسال پیام لغو شد.", get_main_keyboard())
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
    # 🥺 حالت انتظار پیام آشتی
    # ========================================================
    
    if user_access.get(chat_id, {}).get("waiting_for_reconcile", False):
        if text == "🔙 لغو":
            user_access[chat_id]["waiting_for_reconcile"] = False
            send_message(chat_id, "باشه ❤️\n\nهر وقت دلت خواست دوباره بیا...", get_main_keyboard())
            return
        
        if not text:
            send_message(chat_id, "🥺 یه چیزی بنویس که دلت میخواد بهش بگی ❤️")
            return
        
        owner_message = f"""🥺💌 پیام آشتی

👤 یک پیام جدید از بخش «آشتی کنیم» داری.

💬 متن پیام:

{text}

━━━━━━━━━━━━━━
❤️ پیام از بخش آشتی ربات ارسال شده.
"""
        sent = send_message(YOUR_CHAT_ID, owner_message)
        user_access[chat_id]["waiting_for_reconcile"] = False
        
        if sent:
            send_message(chat_id, "💌 پیامت رسید...\n\nمن فرستادمش برای کسی که باید بخونتش. ❤️", get_main_keyboard())
        else:
            send_message(chat_id, "🥺 یه مشکلی پیش اومد و پیام ارسال نشد.", get_main_keyboard())
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
    # 🥺 درخواست آشتی
    # ========================================================
    
    if text == "🥺 میخوام آشتی کنیم":
        user_access[chat_id] = user_access.get(chat_id, {})
        user_access[chat_id]["waiting_for_reconcile"] = True
        send_message(
            chat_id,
            """🥺❤️

اگر دلت برایش تنگ شده
ولی غرورت اجازه نمی‌ده
مستقیم پیام بدی...

اینجا می‌تونی هرچی توی دلت هست
بنویسی. 💌

👇 حالا پیامت رو بنویس:""",
            get_reconcile_keyboard()
        )
        return

    # ========================================================
    # 🌹 رز برای نسا
    # ========================================================
    
    if text == "🌹 رز برای نسا":
        send_message(
            chat_id,
            f"""🌹 یک رز ۳ بعدی مخصوص برای تو شکوفا شده...

نسای عزیزم، این رز رو با عشق برای تو کد زدم. ❤️

👇 برای دیدن رز کلیک کن:

{WEBSITE_URL}/rose

❤️ این رز نماد عشق من به توست..."""
        )
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
    # 🎂 تولد
    # ========================================================
    
    if text == "🎂 تولد نسا":
        send_message(chat_id, BIRTHDAY_MESSAGE)
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
    # 💌 نامه عشق
    # ========================================================
    
    if text == "💌 نامه عشق":
        send_message(chat_id, random.choice(LOVE_LETTERS))
        return

    # ========================================================
    # ❤️ صفحه عشق
    # ========================================================
    
    if text == "❤️ صفحه عشق":
        send_message(
            chat_id,
            f"""❤️ یک سورپرایز مخصوص تو آماده کردم...

چهره‌ات با کلمات
I LOVE YOU NESA
ساخته شده. 🌹

👇 اینجا رو باز کن:

{WEBSITE_URL}/love"""
        )
        return

    # ========================================================
    # 🎉 تبریک برای عشقم
    # ========================================================
    
    if text == "🎉 تبریک برای عشقم":
        send_message(
            chat_id,
            f"""🎁 یک هدیه مخصوص برای تو آماده شده...

آروم بازش کن 🌻❤️

👇 سورپرایز تولدت:

{WEBSITE_URL}/birthday_surprise.html"""
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
        send_message(chat_id, "🏠 برگشتیم به منوی اصلی...\n\n🌻 هر چیزی که بخوای اینجاست ❤️", get_main_keyboard())
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
🎂 تولد نسا
💞 روز آشنایی
⏳ شمارش معکوس تولد
💌 نامه‌های عاشقانه
❤️ صفحه عشق
🎉 سورپرایز تولد
🌹 رز برای نسا
🥺 پیام آشتی
💬 چت دوطرفه

🌻 هر دکمه یک تکه از داستان ماست...

🌹 صفحه رز: {WEBSITE_URL}/rose""",
            get_main_keyboard()
        )
        return

    # ========================================================
    # ❌ دستور نامعتبر
    # ========================================================
    
    send_message(chat_id, "❌ این دستور رو نمی‌شناسم.\n\nاز دکمه‌های پایین استفاده کن ❤️", get_main_keyboard())


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
# ❤️ صفحه موزاییک
# ============================================================

PHOTO_MOSAIC_PAGE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>❤️ I Love You Nesa ❤️</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{background:#050505;display:flex;justify-content:center;align-items:center;min-height:100vh;overflow:hidden;}
canvas{display:block;max-width:100vw;max-height:100vh;}
.watermark{position:fixed;bottom:20px;left:0;right:0;text-align:center;color:#ff5577;font-family:Arial;font-size:14px;letter-spacing:4px;text-shadow:0 0 20px #ff2244;}
</style>
</head>
<body>
<canvas id="photoCanvas"></canvas>
<div class="watermark">❤️ AHU GOOZLUM ❤️</div>
<script>
const imageUrl = "https://i.postimg.cc/5tDhyRgM/IMG-20260318-184739-714.jpg";
const words = ["I","LOVE","YOU","NESA"];
const canvas = document.getElementById("photoCanvas");
const ctx = canvas.getContext("2d");
const img = new Image();
img.crossOrigin="anonymous";
img.src=imageUrl;
img.onload=()=>{
    canvas.width=img.width;
    canvas.height=img.height;
    ctx.drawImage(img,0,0);
    const pixels = ctx.getImageData(0,0,canvas.width,canvas.height).data;
    ctx.fillStyle="#000";
    ctx.fillRect(0,0,canvas.width,canvas.height);
    ctx.textAlign="center";
    ctx.textBaseline="middle";
    ctx.font="7px Arial";
    const step=7;
    for(let y=0;y<canvas.height;y+=step){
        for(let x=0;x<canvas.width;x+=step){
            const index=(y*canvas.width+x)*4;
            const r=pixels[index];
            const g=pixels[index+1];
            const b=pixels[index+2];
            const bright=(r+g+b)/3;
            if(bright>240) continue;
            ctx.fillStyle=`rgb(${r},${g},${b})`;
            const word=words[(x+y)%words.length];
            ctx.fillText(word,x,y);
        }
    }
};
</script>
</body>
</html>
"""


# ============================================================
# 🎂 صفحه سورپرایز تولد
# ============================================================

BIRTHDAY_SURPRISE_PAGE = r"""
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🌻 تولدت مبارک نسا ❤️</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;}
body{
    min-height:100vh;
    background:radial-gradient(circle at center,#32111d 0%,#13070c 45%,#050204 100%);
    color:white;
    font-family:Tahoma,Arial,sans-serif;
    overflow:hidden;
    display:flex;
    align-items:center;
    justify-content:center;
}
.container{width:92%;max-width:520px;text-align:center;position:relative;z-index:20;}
#giftPage{animation:entrance 1.5s ease;}
@keyframes entrance{
    from{opacity:0;transform:scale(.6) translateY(40px);}
    to{opacity:1;transform:scale(1) translateY(0);}
}
.gift{font-size:130px;cursor:pointer;filter:drop-shadow(0 0 25px #ff416c);animation:giftFloat 2.5s ease-in-out infinite;user-select:none;}
@keyframes giftFloat{
    0%,100%{transform:translateY(0) rotate(-2deg);}
    50%{transform:translateY(-18px) rotate(2deg);}
}
.openText{margin-top:20px;color:#ffd2dc;font-size:18px;text-shadow:0 0 15px #ff416c;}
#passwordPage,#birthdayPage{display:none;}
.card{padding:30px 22px;border-radius:28px;background:linear-gradient(145deg,rgba(70,15,30,.92),rgba(15,5,10,.95));border:1px solid rgba(255,150,170,.4);box-shadow:0 0 60px rgba(255,50,100,.25),inset 0 0 30px rgba(255,50,100,.08);backdrop-filter:blur(15px);}
.card h1{color:#ff7895;font-size:28px;margin-bottom:18px;text-shadow:0 0 25px #ff416c;}
.card p{line-height:2;color:#ffdbe3;}
input{width:100%;margin-top:20px;padding:15px;border-radius:16px;border:1px solid #ff5577;background:rgba(0,0,0,.5);color:white;outline:none;text-align:center;font-size:20px;}
button{margin-top:18px;padding:14px 35px;border:none;border-radius:30px;color:white;background:linear-gradient(45deg,#ff416c,#ff758c);font-size:17px;font-weight:bold;cursor:pointer;box-shadow:0 0 25px rgba(255,65,108,.5);}
.birthdayTitle{font-size:30px;color:#ffd36e;text-shadow:0 0 25px #ff9d00;}
.message{margin-top:20px;line-height:2.1;color:#ffe9ee;font-size:16px;}
.photo{width:100%;max-width:340px;margin:22px auto;display:block;border-radius:20px;border:2px solid rgba(255,190,100,.6);box-shadow:0 0 35px rgba(255,150,0,.25);}
.flower{position:fixed;top:-100px;z-index:5;pointer-events:none;animation:flowerFall linear forwards;}
@keyframes flowerFall{
    0%{transform:translateY(-100px) rotate(0deg);opacity:0;}
    10%{opacity:1;}
    100%{transform:translateY(110vh) rotate(720deg);opacity:0;}
}
.heart{position:fixed;top:-60px;z-index:4;pointer-events:none;animation:heartFall linear forwards;}
@keyframes heartFall{
    0%{transform:translateY(-60px) rotate(0deg);opacity:0;}
    10%{opacity:1;}
    100%{transform:translateY(110vh) rotate(360deg);opacity:0;}
}
.glow{position:fixed;width:250px;height:250px;border-radius:50%;background:#ff416c;filter:blur(120px);opacity:.12;}
.glow.one{top:-80px;right:-80px;}
.glow.two{bottom:-100px;left:-100px;}
</style>
</head>
<body>
<div class="glow one"></div>
<div class="glow two"></div>
<div class="container" id="giftPage">
    <div class="gift" onclick="showPassword()">🎁</div>
    <div class="openText">🌻 برای باز کردن هدیه کلیک کن 🌻</div>
</div>
<div class="container" id="passwordPage">
    <div class="card">
        <h1>🔐 هدیه مخصوص تو</h1>
        <p>تاریخ تولدت رو وارد کن ❤️</p>
        <input id="passwordInput" type="password" maxlength="10" placeholder="رمز مخصوص">
        <button onclick="checkPassword()">🌻 باز کردن هدیه</button>
        <p id="error" style="display:none;color:#ff5577;margin-top:15px">❌ رمز اشتباهه</p>
    </div>
</div>
<div class="container" id="birthdayPage">
    <div class="card">
        <div class="birthdayTitle">🌻🎂 تولدت مبارک نسا 🎂🌻</div>
        <div class="message">
            امروز روزی نیست که فقط تولد تو را جشن بگیرم...
            امروز روزی است که از بودن تو در این دنیا خوشحالم. ❤️
            <br><br>
            تو یکی از زیباترین اتفاق‌های زندگی منی.
            <br><br>
            🌻 امیدوارم همیشه بخندی، همیشه خوشحال باشی و به تمام آرزوهایت برسی.
            <br><br>
            ❤️ تولدت مبارک عشق من ❤️
            <br>
            🌻 دوستت دارم 🌻
        </div>
        <img class="photo" src="https://i.postimg.cc/5tDhyRgM/IMG-20260318-184739-714.jpg">
    </div>
</div>
<script>
const PASSWORD = "1386";
function showPassword(){
    document.getElementById("giftPage").style.display="none";
    document.getElementById("passwordPage").style.display="block";
    document.getElementById("passwordInput").focus();
}
function checkPassword(){
    const input = document.getElementById("passwordInput").value.trim();
    if(input === PASSWORD){
        document.getElementById("passwordPage").style.display="none";
        document.getElementById("birthdayPage").style.display="block";
        startFlowers();
        startHearts();
    }else{
        document.getElementById("error").style.display="block";
    }
}
function startFlowers(){
    const flowers=["🌻","🌼","🌺","🌸","💐","🌷","🪻","🌹"];
    for(let i=0;i<55;i++){
        const flower=document.createElement("div");
        flower.className="flower";
        flower.textContent=flowers[Math.floor(Math.random()*flowers.length)];
        flower.style.left=Math.random()*100+"%";
        flower.style.fontSize=(18+Math.random()*28)+"px";
        flower.style.animationDuration=(5+Math.random()*7)+"s";
        flower.style.animationDelay=Math.random()*6+"s";
        document.body.appendChild(flower);
        setTimeout(()=>flower.remove(),14000);
    }
}
function startHearts(){
    const hearts=["❤️","💖","💕","💗","💘","❤️‍🔥"];
    for(let i=0;i<50;i++){
        const heart=document.createElement("div");
        heart.className="heart";
        heart.textContent=hearts[Math.floor(Math.random()*hearts.length)];
        heart.style.left=Math.random()*100+"%";
        heart.style.fontSize=(14+Math.random()*25)+"px";
        heart.style.animationDuration=(4+Math.random()*6)+"s";
        heart.style.animationDelay=Math.random()*5+"s";
        document.body.appendChild(heart);
        setTimeout(()=>heart.remove(),13000);
    }
}
document.getElementById("passwordInput").addEventListener("keydown", function(e){
    if(e.key==="Enter"){checkPassword();}
});
</script>
</body>
</html>
"""


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
                handle_message(chat_id, text)
        except Exception as e:
            print("Webhook error:", e)
    return "OK", 200


@app.route("/health", methods=["GET"])
def health():
    return "OK", 200


@app.route("/love")
def love_page():
    return render_template_string(PHOTO_MOSAIC_PAGE)


@app.route("/birthday_surprise.html")
def birthday_surprise():
    return render_template_string(BIRTHDAY_SURPRISE_PAGE)


@app.route("/rose")
def rose_page():
    return render_template_string(ROSE_PAGE)


# ============================================================
# 🚀 اجرای برنامه
# ============================================================

if __name__ == "__main__":
    print("🚀 ربات ahu goozlum روشن شد...")
    print(f"🎂 تولد: {BIRTH_DAY}/{BIRTH_MONTH}")
    print(f"📸 تعداد عکس‌ها: {len(PHOTOS)}")
    print("🌹 صفحه رز: /rose")
    print("❤️ صفحه عشق: /love")
    print("🎉 صفحه تولد: /birthday_surprise.html")
    print("🩺 مسیر سلامت: /health")
    print(f"💬 چت دوطرفه با آیدی: {PARTNER_CHAT_ID}")

    timer_thread = threading.Thread(target=birthday_timer, daemon=True)
    timer_thread.start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
