from flask import Flask, request, jsonify
import requests
import json
import random
import datetime
import os
import threading
import time

app = Flask(name)

============================================================

🔐 تنظیمات ربات

============================================================

TOKEN = os.environ.get("BOT_TOKEN", "")

============================================================

👑 مالک جدید ربات

============================================================

OWNER_CHAT_ID = "7989818498"

============================================================

❤️ پارتنر

============================================================

PARTNER_CHAT_ID = "7706282234"

PASSWORD = "1386"

BIRTH_DAY = 8
BIRTH_MONTH = 8
BIRTH_HOUR = 0
BIRTH_MINUTE = 0

IRAN_OFFSET = datetime.timedelta(
hours=3,
minutes=30
)

WEBSITE_URL = "https://nesa-bot.onrender.com"

============================================================

🗂️ حافظه موقت

============================================================

user_access = {}

PARTNER_ACTIVITY = {}

BOT_ACTIVE = True

============================================================

📸 عکس‌های گالری

============================================================

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
},  

"📸 عکس جدید": {  
    "path": "photos/file_00000000f1788210bc5e8d993e16a277.png",  
    "caption": "🌹 این عکس مخصوص توست... ❤️"  
}

}

============================================================

🕐 زمان ایران

============================================================

def get_current_iran_time():

utc_now = datetime.datetime.now(  
    datetime.timezone.utc  
)  

return utc_now.astimezone(  
    datetime.timezone(IRAN_OFFSET)  
)

============================================================

📊 ثبت فعالیت کاربر

============================================================

def log_partner_activity(
chat_id,
action="تعامل",
first_name="",
last_name="",
username="",
phone_number=""
):

global PARTNER_ACTIVITY  

chat_id = str(chat_id)  

# ========================================================  
# 👑 مالک هرگز به عنوان پارتنر گزارش نمی‌شود  
# ========================================================  

if chat_id == OWNER_CHAT_ID:  
    return  

now = get_current_iran_time()  

if chat_id not in PARTNER_ACTIVITY:  

    PARTNER_ACTIVITY[chat_id] = {  

        "first_seen": now,  

        "last_seen": now,  

        "count": 0,  

        "first_name": first_name,  

        "last_name": last_name,  

        "username": username,  

        "phone_number": phone_number,  

        "last_action": action  
    }  

data = PARTNER_ACTIVITY[chat_id]  

if first_name:  
    data["first_name"] = first_name  

if last_name:  
    data["last_name"] = last_name  

if username:  
    data["username"] = username  

if phone_number:  
    data["phone_number"] = phone_number  

data["last_seen"] = now  

data["last_action"] = action  

data["count"] += 1  

time_str = now.strftime("%H:%M:%S")  

date_str = now.strftime("%Y/%m/%d")  

weekdays = {  

    "Monday": "دوشنبه",  
    "Tuesday": "سه‌شنبه",  
    "Wednesday": "چهارشنبه",  
    "Thursday": "پنج‌شنبه",  
    "Friday": "جمعه",  
    "Saturday": "شنبه",  
    "Sunday": "یک‌شنبه"  
}  

day_persian = weekdays.get(  
    now.strftime("%A"),  
    now.strftime("%A")  
)  

username_text = (  
    "@" + username  
    if username  
    else "ندارد"  
)  

profile_link = (  
    "https://t.me/" + username  
    if username  
    else "ندارد"  
)  

message = f"""

👀 تعامل جدید با ربات

👤 اطلاعات کاربر:

• آیدی عددی: {chat_id}
• نام: {first_name or data.get('first_name') or 'نامشخص'}
• نام خانوادگی: {last_name or data.get('last_name') or 'نامشخص'}
• یوزرنیم: {username_text}
• شماره تلفن: {phone_number or data.get('phone_number') or 'نامشخص'}

📌 نوع تعامل:
{action}

📅 تاریخ: {date_str}
📆 روز: {day_persian}
⏰ ساعت: {time_str}

🔢 تعداد تعامل‌ها: {data['count']}

🔗 لینک پروفایل:
{profile_link}
"""

send_message(  
    OWNER_CHAT_ID,  
    message  
)

============================================================

👀 گزارش تعامل

============================================================

def report_user_interaction(
chat_id,
action,
first_name="",
last_name="",
username="",
phone_number=""
):

chat_id = str(chat_id)  

if chat_id == OWNER_CHAT_ID:  
    return  

log_partner_activity(  
    chat_id,  
    action,  
    first_name,  
    last_name,  
    username,  
    phone_number  
)

============================================================

💕 روز آشنایی

============================================================

SECOND_QUOTES = [

"هر ثانیه‌ای که می‌گذرد، عشق من به تو عمیق‌تر می‌شود... ❤️",  

"ثانیه‌ها می‌گذرند، اما عشق من به تو هرگز کهنه نمی‌شود... 🌹",  

"در هر ثانیه‌ای از زندگی‌ام، تو را نفس می‌کشم... 💫",  

"ثانیه‌های بی‌تو طولانی‌اند، اما کنار تو حتی ساعت‌ها هم کوتاه‌اند... ✨",  

"هر ثانیه که می‌گذرد، یک دلیل تازه برای دوست داشتن تو پیدا می‌کنم... ❤️",  

"ثانیه‌ها را بشمار، اما عشق را نه؛ چون عشق من به تو بی‌نهایت است... 🌸"

]

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

return int(  
    (now - MEETING_DATE).total_seconds()  
)

============================================================

🎂 ساعت تا تولد

============================================================

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

return int(  
    diff.total_seconds() // 3600  
)

============================================================

⌨️ منوی اصلی

============================================================

def get_main_keyboard(chat_id=None):

keyboard = [  

    ["📸 عکس‌ها"],  

    ["📅 روز آشنایی", "⏳ ساعت تا تولدت"],  

    ["💬 چت دوطرفه"]  
]  

# ========================================================  
# 👑 منوی مخصوص مالک  
# ========================================================  

if str(chat_id) == OWNER_CHAT_ID:  

    keyboard.append(  
        ["📊 وضعیت پارتنر"]  
    )  

keyboard.append(  
    ["🔙 بازگشت به منو"]  
)  

return {  

    "keyboard": keyboard,  

    "resize_keyboard": True  
}

============================================================

📸 منوی عکس

============================================================

def get_photo_keyboard():

return {  

    "keyboard": [  

        ["📸 عکس ۱", "📸 عکس ۲", "📸 عکس ۳"],  

        ["📸 عکس ۴", "📸 عکس ۵", "📸 عکس ۶"],  

        ["📸 عکس ۷", "📸 عکس جدید"],  

        ["🔙 بازگشت به منو"]  
    ],  

    "resize_keyboard": True  
}

============================================================

🔐 منوی رمز

============================================================

def get_password_keyboard():

return {  

    "keyboard": [  

        ["🔙 بازگشت به منو"]  

    ],  

    "resize_keyboard": True  
}

============================================================

💬 منوی چت دوطرفه

============================================================

def get_chat_keyboard():

return {  

    "keyboard": [  

        ["📤 ارسال پیام"],  

        ["📤 ارسال عکس", "📤 ارسال فیلم"],  

        ["📤 ارسال موزیک"],  

        ["🔙 بازگشت به منو"]  
    ],  

    "resize_keyboard": True  
}

============================================================

📤 ارسال پیام تلگرام

============================================================

def send_message(
chat_id,
text,
reply_markup=None,
protect_content=False
):

if not TOKEN:  

    print(  
        "❌ BOT_TOKEN تنظیم نشده است."  
    )  

    return False  

url = (  
    f"https://api.telegram.org/"  
    f"bot{TOKEN}/sendMessage"  
)  

try:  

    payload = {  

        "chat_id": chat_id,  

        "text": text,  

        "protect_content": protect_content  
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

    print(  
        "send_message error:",  
        e  
    )  

return False

============================================================

📸 ارسال عکس

============================================================

def send_photo(
chat_id,
photo_data,
caption="",
protect_content=False
):

if not TOKEN:  

    print(  
        "❌ BOT_TOKEN تنظیم نشده است."  
    )  

    return False  

try:  

    url = (  
        f"https://api.telegram.org/"  
        f"bot{TOKEN}/sendPhoto"  
    )  

    # ====================================================  
    # لینک اینترنتی  
    # ====================================================  

    if (  
        isinstance(photo_data, str)  
        and photo_data.startswith("http")  
    ):  

        payload = {  

            "chat_id": chat_id,  

            "photo": photo_data,  

            "caption": caption,  

            "protect_content": protect_content  
        }  

        response = requests.post(  
            url,  
            data=payload,  
            timeout=30  
        )  

        return response.status_code == 200  

    # ====================================================  
    # file_id  
    # ====================================================  

    if (  
        isinstance(photo_data, str)  
        and photo_data.startswith("file_id:")  
    ):  

        file_id = photo_data.replace(  
            "file_id:",  
            "",  
            1  
        )  

        payload = {  

            "chat_id": chat_id,  

            "photo": file_id,  

            "caption": caption,  

            "protect_content": protect_content  
        }  

        response = requests.post(  
            url,  
            data=payload,  
            timeout=30  
        )  

        return response.status_code == 200  

    # ====================================================  
    # فایل محلی  
    # ====================================================  

    if (  
        isinstance(photo_data, str)  
        and os.path.exists(photo_data)  
    ):  

        with open(  
            photo_data,  
            "rb"  
        ) as photo:  

            files = {  

                "photo": photo  
            }  

            data = {  

                "chat_id": chat_id,  

                "caption": caption,  

                "protect_content": protect_content  
            }  

            response = requests.post(  

                url,  

                data=data,  

                files=files,  

                timeout=60  
            )  

        return response.status_code == 200  

    return False  

except Exception as e:  

    print(  
        "send_photo error:",  
        e  
    )  

    return False

============================================================

🎥 ارسال فیلم

============================================================

def send_video(
chat_id,
video_data,
caption="",
protect_content=False
):

if not TOKEN:  

    print(  
        "❌ BOT_TOKEN تنظیم نشده است."  
    )  

    return False  

try:  

    url = (  
        f"https://api.telegram.org/"  
        f"bot{TOKEN}/sendVideo"  
    )  

    # لینک  
    if (  
        isinstance(video_data, str)  
        and video_data.startswith("http")  
    ):  

        payload = {  

            "chat_id": chat_id,  

            "video": video_data,  

            "caption": caption,  

            "protect_content": protect_content  
        }  

        response = requests.post(  
            url,  
            data=payload,  
            timeout=120  
        )  

        return response.status_code == 200  

    # file_id  
    if (  
        isinstance(video_data, str)  
        and video_data.startswith("file_id:")  
    ):  

        file_id = video_data.replace(  
            "file_id:",  
            "",  
            1  
        )  

        payload = {  

            "chat_id": chat_id,  

            "video": file_id,  

            "caption": caption,  

            "protect_content": protect_content  
        }  

        response = requests.post(  
            url,  
            data=payload,  
            timeout=120  
        )  

        return response.status_code == 200  

    # فایل محلی  
    if (  
        isinstance(video_data, str)  
        and os.path.exists(video_data)  
    ):  

        with open(  
            video_data,  
            "rb"  
        ) as video:  

            files = {  

                "video": video  
            }  

            data = {  

                "chat_id": chat_id,  

                "caption": caption,  

                "protect_content": protect_content  
            }  

            response = requests.post(  

                url,  

                data=data,  

                files=files,  

                timeout=120  
            )  

        return response.status_code == 200  

    return False  

except Exception as e:  

    print(  
        "send_video error:",  
        e  
    )  

    return False

============================================================

🎵 ارسال موزیک

============================================================

def send_audio(
chat_id,
audio_data,
caption="",
title="",
performer="",
protect_content=False
):

if not TOKEN:  

    print(  
        "❌ BOT_TOKEN تنظیم نشده است."  
    )  

    return False  

try:  

    url = (  
        f"https://api.telegram.org/"  
        f"bot{TOKEN}/sendAudio"  
    )  

    # ====================================================  
    # لینک  
    # ====================================================  

    if (  
        isinstance(audio_data, str)  
        and audio_data.startswith("http")  
    ):  

        payload = {  

            "chat_id": chat_id,  

            "audio": audio_data,  

            "caption": caption,  

            "protect_content": protect_content  
        }  

        if title:  
            payload["title"] = title  

        if performer:  
            payload["performer"] = performer  

        response = requests.post(  
            url,  
            data=payload,  
            timeout=120  
        )  

        return response.status_code == 200  

    # ====================================================  
    # file_id  
    # ====================================================  

    if (  
        isinstance(audio_data, str)  
        and audio_data.startswith("file_id:")  
    ):  

        file_id = audio_data.replace(  
            "file_id:",  
            "",  
            1  
        )  

        payload = {  

            "chat_id": chat_id,  

            "audio": file_id,  

            "caption": caption,  

            "protect_content": protect_content  
        }  

        if title:  
            payload["title"] = title  

        if performer:  
            payload["performer"] = performer  

        response = requests.post(  
            url,  
            data=payload,  
            timeout=120  
        )  

        return response.status_code == 200  

    # ====================================================  
    # فایل محلی  
    # ====================================================  

    if (  
        isinstance(audio_data, str)  
        and os.path.exists(audio_data)  
    ):  

        with open(  
            audio_data,  
            "rb"  
        ) as audio:  

            files = {  

                "audio": audio  
            }  

            data = {  

                "chat_id": chat_id,  

                "caption": caption,  

                "protect_content": protect_content  
            }  

            if title:  
                data["title"] = title  

            if performer:  
                data["performer"] = performer  

            response = requests.post(  
                url,  
                data=data,  
                files=files,  
                timeout=120  
            )  

        return response.status_code == 200  

    return False  

except Exception as e:  

    print(  
        "send_audio error:",  
        e  
    )  

    return False

============================================================

📎 ارسال Document

============================================================

def send_document(
chat_id,
document_data,
caption="",
protect_content=False
):

if not TOKEN:  

    print(  
        "❌ BOT_TOKEN تنظیم نشده است."  
    )  

    return False  

try:  

    url = (  
        f"https://api.telegram.org/"  
        f"bot{TOKEN}/sendDocument"  
    )  

    # file_id  
    if (  
        isinstance(document_data, str)  
        and document_data.startswith("file_id:")  
    ):  

        file_id = document_data.replace(  
            "file_id:",  
            "",  
            1  
        )  

        payload = {  

            "chat_id": chat_id,  

            "document": file_id,  

            "caption": caption,  

            "protect_content": protect_content  
        }  

        response = requests.post(  
            url,  
            data=payload,  
            timeout=120  
        )  

        return response.status_code == 200  

    # لینک  
    if (  
        isinstance(document_data, str)  
        and document_data.startswith("http")  
    ):  

        payload = {  

            "chat_id": chat_id,  

            "document": document_data,  

            "caption": caption,  

            "protect_content": protect_content  
        }  

        response = requests.post(  
            url,  
            data=payload,  
            timeout=120  
        )  

        return response.status_code == 200  

    # فایل محلی  
    if (  
        isinstance(document_data, str)  
        and os.path.exists(document_data)  
    ):  

        with open(  
            document_data,  
            "rb"  
        ) as document:  

            files = {  

                "document": document  
            }  

            data = {  

                "chat_id": chat_id,  

                "caption": caption,  

                "protect_content": protect_content  
            }  

            response = requests.post(  
                url,  
                data=data,  
                files=files,  
                timeout=120  
            )  

        return response.status_code == 200  

    return False  

except Exception as e:  

    print(  
        "send_document error:",  
        e  
    )  

    return False

============================================================

🎤 ارسال Voice

============================================================

def send_voice(
chat_id,
voice_data,
caption="",
protect_content=False
):

if not TOKEN:  

    print(  
        "❌ BOT_TOKEN تنظیم نشده است."  
    )  

    return False  

try:  

    url = (  
        f"https://api.telegram.org/"  
        f"bot{TOKEN}/sendVoice"  
    )  

    if (  
        isinstance(voice_data, str)  
        and voice_data.startswith("file_id:")  
    ):  

        file_id = voice_data.replace(  
            "file_id:",  
            "",  
            1  
        )  

        payload = {  

            "chat_id": chat_id,  

            "voice": file_id,  

            "caption": caption,  

            "protect_content": protect_content  
        }  

        response = requests.post(  
            url,  
            data=payload,  
            timeout=120  
        )  

        return response.status_code == 200  

    if (  
        isinstance(voice_data, str)  
        and voice_data.startswith("http")  
    ):  

        payload = {  

            "chat_id": chat_id,  

            "voice": voice_data,  

            "caption": caption,  

            "protect_content": protect_content  
        }  

        response = requests.post(  
            url,  
            data=payload,  
            timeout=120  
        )  

        return response.status_code == 200  

    return False  

except Exception as e:  

    print(  
        "send_voice error:",  
        e  
    )  

    return False

============================================================

🎵 ارسال موزیک با file_id

============================================================

def send_audio_file_id(
chat_id,
file_id,
caption="",
title="🎵",
performer="❤️",
protect_content=False
):

return send_audio(  

    chat_id,  

    f"file_id:{file_id}",  

    caption,  

    title,  

    performer,  

    protect_content  
)

============================================================

📤 ارسال فایل در چت

============================================================

def send_chat_file(
target_id,
file_data,
protect_content=False
):

file_type = file_data.get(  
    "type"  
)  

file_id = file_data.get(  
    "file_id"  
)  

caption = file_data.get(  
    "caption",  
    ""  
)  

if not file_id:  

    return False  

# ========================================================  
# 📸 عکس  
# ========================================================  

if file_type == "photo":  

    return send_photo(  

        target_id,  

        f"file_id:{file_id}",  

        caption,  

        protect_content  
    )  

# ========================================================  
# 🎥 فیلم  
# ========================================================  

if file_type == "video":  

    return send_video(  

        target_id,  

        f"file_id:{file_id}",  

        caption,  

        protect_content  
    )  

# ========================================================  
# 🎵 موزیک  
# ========================================================  

if file_type == "audio":  

    title = file_data.get(  
        "title",  
        "🎵"  
    )  

    performer = file_data.get(  
        "performer",  
        "❤️"  
    )  

    return send_audio_file_id(  

        target_id,  

        file_id,  

        caption,  

        title,  

        performer,  

        protect_content  
    )  

# ========================================================  
# 📎 فایل  
# ========================================================  

if file_type == "document":  

    return send_document(  

        target_id,  

        f"file_id:{file_id}",  

        caption,  

        protect_content  
    )  

# ========================================================  
# 🎤 ویس  
# ========================================================  

if file_type == "voice":  

    return send_voice(  

        target_id,  

        f"file_id:{file_id}",  

        caption,  

        protect_content  
    )  

return False

============================================================

🤖 پردازش پیام

============================================================

def handle_message(
chat_id,
text,
file_data=None
):

chat_id = str(chat_id)  

text = (  
    text or ""  
).strip()  


# ========================================================  
# 🚫 ربات غیرفعال  
# ========================================================  

if (  
    not BOT_ACTIVE  
    and chat_id != OWNER_CHAT_ID  
):  

    send_message(  

        chat_id,  

        "🔒 ربات غیرفعال شده است."  
    )  

    return  


# ========================================================  
# 👤 ساخت اطلاعات کاربر  
# ========================================================  

user_access.setdefault(  

    chat_id,  

    {  

        "photos": False,  

        "waiting_for_password": False,  

        "waiting_for_chat_message": False,  

        "waiting_for_file": False,  

        "mode": None,  

        "chat_target": None  
    }  
)  

user = user_access[chat_id]  


# ========================================================  
# 🔙 بازگشت به منو  
# ========================================================  

if text == "🔙 بازگشت به منو":  

    photos_access = user.get(  
        "photos",  
        False  
    )  

    user_access[chat_id] = {  

        "photos": photos_access,  

        "waiting_for_password": False,  

        "waiting_for_chat_message": False,  

        "waiting_for_file": False,  

        "mode": None,  

        "chat_target": None  
    }  

    send_message(  

        chat_id,  

        "🏠 برگشتیم به منوی اصلی...\n\n"  
        "🌻 هر چیزی که بخوای اینجاست ❤️",  

        get_main_keyboard(chat_id)  
    )  

    return  


# ========================================================  
# /start  
# ========================================================  

if text == "/start":  

    user_access[chat_id] = {  

        "photos": False,  

        "waiting_for_password": False,  

        "waiting_for_chat_message": False,  

        "waiting_for_file": False,  

        "mode": None,  

        "chat_target": None  
    }  

    send_message(  

        chat_id,  

        """🌻❤️ به دنیای ahu goozlum خوش اومدی ❤️🌻

🎁 اینجا یک گوشه کوچیک از قلب منه...

📸 عکس‌های خصوصی
📅 روز آشنایی
⏳ شمارش معکوس تولد
💬 چت دوطرفه

🌻 هر دکمه یک تکه از داستان ماست...""",

get_main_keyboard(chat_id)  
    )  

    return  


# ========================================================  
# 💬 چت دوطرفه  
# ========================================================  

if text == "💬 چت دوطرفه":  

    if (  
        chat_id != OWNER_CHAT_ID  
        and chat_id != PARTNER_CHAT_ID  
    ):  

        send_message(  

            chat_id,  

            "❌ این بخش فقط برای مالک و پارتنر است.",  

            get_main_keyboard(chat_id)  
        )  

        return  


    user["mode"] = "partner_chat"  

    user[  
        "waiting_for_chat_message"  
    ] = False  

    user[  
        "waiting_for_file"  
    ] = False  


    send_message(  

        chat_id,  

        """💬 چت دوطرفه باز شد ❤️

از اینجا می‌تونی برای طرف مقابل بفرستی:

💬 پیام
📸 عکس
🎥 فیلم
🎵 موزیک / MP3
📎 فایل
🎤 ویس

فایل رو مستقیم همینجا بفرست.""",

get_chat_keyboard()  
    )  

    return  


# ========================================================  
# 📤 ارسال پیام در چت  
# ========================================================  

if text == "📤 ارسال پیام":  

    if user.get("mode") == "partner_chat":  

        user[  
            "waiting_for_chat_message"  
        ] = True  

        user[  
            "waiting_for_file"  
        ] = False  

        user[  
            "chat_target"  
        ] = "partner"  

        send_message(  

            chat_id,  

            "💬 پیامت رو برای طرف مقابل بنویس:",  

            get_chat_keyboard()  
        )  

    return  


# ========================================================  
# 📤 ارسال عکس در چت  
# ========================================================  

if text == "📤 ارسال عکس":  

    if user.get("mode") == "partner_chat":  

        user[  
            "waiting_for_file"  
        ] = "photo"  

        user[  
            "waiting_for_chat_message"  
        ] = False  

        user[  
            "chat_target"  
        ] = "partner"  

        send_message(  

            chat_id,  

            "📸 عکس رو همینجا بفرست:",  

            get_chat_keyboard()  
        )  

    return  


# ========================================================  
# 📤 ارسال فیلم در چت  
# ========================================================  

if text == "📤 ارسال فیلم":  

    if user.get("mode") == "partner_chat":  

        user[  
            "waiting_for_file"  
        ] = "video"  

        user[  
            "waiting_for_chat_message"  
        ] = False  

        user[  
            "chat_target"  
        ] = "partner"  

        send_message(  

            chat_id,  

            "🎥 فیلم رو همینجا بفرست:",  

            get_chat_keyboard()  
        )  

    return  


# ========================================================  
# 📤 ارسال موزیک در چت  
# ========================================================  

if text == "📤 ارسال موزیک":  

    if user.get("mode") == "partner_chat":  

        user[  
            "waiting_for_file"  
        ] = "audio"  

        user[  
            "waiting_for_chat_message"  
        ] = False  

        user[  
            "chat_target"  
        ] = "partner"  

        send_message(  

            chat_id,  

            """🎵 موزیک رو همینجا بفرست.

برای MP3 می‌تونی:

📎 Attach
→ Music

یا

📎 Attach
→ File

رو انتخاب کنی.

ربات هر دو حالت رو تشخیص میده. ❤️""",

get_chat_keyboard()  
        )  

    return  


# ========================================================  
# 📥 پردازش فایل‌ها  
# ========================================================  

if file_data:  

    file_type = file_data.get(  
        "type"  
    )  

    target = user.get(  
        "chat_target",  
        "partner"  
    )  


    # ====================================================  
    # مقصد  
    # ====================================================  

    if target == "partner":  

        if chat_id == OWNER_CHAT_ID:  

            target_id = PARTNER_CHAT_ID  

        elif chat_id == PARTNER_CHAT_ID:  

            target_id = OWNER_CHAT_ID  

        else:  

            send_message(  
                chat_id,  
                "❌ شما اجازه استفاده از چت دوطرفه را ندارید."  
            )  

            return  

    else:  

        target_id = PARTNER_CHAT_ID  


    # ====================================================  
    # 🔐 محافظت  
    #  
    # مالک → پارتنر = محافظت‌شده  
    #  
    # پارتنر → مالک = معمولی  
    # ====================================================  

    protect_for_recipient = (  

        chat_id == OWNER_CHAT_ID  
        and  
        target_id == PARTNER_CHAT_ID  
    )  


    success = send_chat_file(  

        target_id,  

        file_data,  

        protect_for_recipient  
    )  


    # ====================================================  
    # نتیجه  
    # ====================================================  

    if success:  

        if file_type == "photo":  

            success_text = (  
                "✅ عکس با موفقیت ارسال شد! 📸"  
            )  

        elif file_type == "video":  

            success_text = (  
                "✅ فیلم با موفقیت ارسال شد! 🎥"  
            )  

        elif file_type == "audio":  

            success_text = (  
                "✅ موزیک / MP3 با موفقیت ارسال شد! 🎵"  
            )  

        elif file_type == "document":  

            success_text = (  
                "✅ فایل با موفقیت ارسال شد! 📎"  
            )  

        elif file_type == "voice":  

            success_text = (  
                "✅ ویس با موفقیت ارسال شد! 🎤"  
            )  

        else:  

            success_text = (  
                "✅ فایل ارسال شد! ❤️"  
            )  


        if protect_for_recipient:  

            success_text += (  
                "\n\n🔐 نسخه‌ای که برای پارتنر ارسال شد "  
                "محافظت‌شده است."  
            )  


        send_message(  

            chat_id,  

            success_text,  

            get_chat_keyboard()  
        )  

    else:  

        send_message(  

            chat_id,  

            """❌ ارسال فایل ناموفق بود.

اگر موزیک است، مطمئن شو فایل به‌صورت MP3 یا فایل صوتی ارسال شده باشد.""",

get_chat_keyboard()  
        )  


    user[  
        "waiting_for_file"  
    ] = False  

    return  


# ========================================================  
# 💬 ارسال پیام متنی  
# ========================================================  

if user.get(  
    "waiting_for_chat_message",  
    False  
):  

    target = user.get(  
        "chat_target",  
        "partner"  
    )  


    if target == "partner":  

        if chat_id == OWNER_CHAT_ID:  

            target_id = PARTNER_CHAT_ID  

            sender_name = "عشقت"  

        elif chat_id == PARTNER_CHAT_ID:  

            target_id = OWNER_CHAT_ID  

            sender_name = "پارتنرت"  

        else:  

            send_message(  
                chat_id,  
                "❌ اجازه ارسال پیام نداری."  
            )  

            return  


    if text:  

        success = send_message(  

            target_id,  

            f"💬 پیام از {sender_name}:\n\n{text}"  
        )  


        if success:  

            send_message(  

                chat_id,  

                "✅ پیام ارسال شد! ❤️",  

                get_chat_keyboard()  
            )  

        else:  

            send_message(  

                chat_id,  

                "❌ ارسال پیام ناموفق بود."  
            )  


    user[  
        "waiting_for_chat_message"  
    ] = False  

    return  


# ========================================================  
# 📊 وضعیت پارتنر  
# ========================================================  

if text == "📊 وضعیت پارتنر":  

    if chat_id != OWNER_CHAT_ID:  

        send_message(  

            chat_id,  

            "❌ دسترسی ندارید."  
        )  

        return  


    if not PARTNER_ACTIVITY:  

        send_message(  

            chat_id,  

            "❌ هنوز هیچ تعاملی ثبت نشده است."  
        )  

        return  


    partner_id = (  

        PARTNER_CHAT_ID  

        if PARTNER_CHAT_ID in PARTNER_ACTIVITY  

        else list(  
            PARTNER_ACTIVITY.keys()  
        )[0]  
    )  


    data = PARTNER_ACTIVITY[  
        partner_id  
    ]  


    last_seen = data[  
        "last_seen"  
    ]  

    first_seen = data[  
        "first_seen"  
    ]  


    now = get_current_iran_time()  


    diff = (  

        now - last_seen  
    ).total_seconds()  


    status = (  

        "🟢 اخیراً فعال بوده"  

        if diff < 300  

        else  

        "🔴 بیش از ۵ دقیقه تعامل نداشته"  
    )  


    username = data.get(  
        "username"  
    )  


    username_text = (  

        "@" + username  

        if username  

        else "ندارد"  
    )  


    message = f"""

📊 وضعیت پارتنر

👤 اطلاعات:

• آیدی: {partner_id}
• نام: {data.get('first_name') or 'نامشخص'}
• نام خانوادگی: {data.get('last_name') or 'نامشخص'}
• یوزرنیم: {username_text}

📅 اولین تعامل:
{first_seen.strftime('%Y/%m/%d - %H:%M:%S')}

📅 آخرین تعامل:
{last_seen.strftime('%Y/%m/%d - %H:%M:%S')}

🔢 تعداد تعامل‌ها:
{data['count']}

📌 آخرین اقدام:
{data.get('last_action', 'نامشخص')}

❤️ وضعیت:
{status}
"""

send_message(  

        chat_id,  

        message,  

        get_main_keyboard(chat_id)  
    )  

    return  


# ========================================================  
# 🔐 بررسی رمز  
# ========================================================  

if user.get(  
    "waiting_for_password",  
    False  
):  

    if text == PASSWORD:  

        user[  
            "photos"  
        ] = True  

        user[  
            "waiting_for_password"  
        ] = False  


        send_message(  

            chat_id,  

            "✅ رمز درست بود!\n\n"  
            "🔓 گالری باز شد ❤️",  

            get_photo_keyboard()  
        )  

    else:  

        send_message(  

            chat_id,  

            "❌ رمز اشتباهه!\n\n"  
            "دوباره امتحان کن ❤️",  

            get_password_keyboard()  
        )  

    return  


# ========================================================  
# 📸 انتخاب عکس  
# ========================================================  

if text in PHOTOS:  

    if user.get(  
        "photos",  
        False  
    ):  

        photo = PHOTOS[text]  


        success = send_photo(  

            chat_id,  

            photo["path"],  

            photo["caption"]  
        )  


        if not success:  

            send_message(  

                chat_id,  

                "❌ ارسال عکس ناموفق بود."  
            )  

    else:  

        user[  
            "waiting_for_password"  
        ] = True  


        send_message(  

            chat_id,  

            "🔐 این قسمت خصوصی است.\n\n"  
            "لطفاً رمز مخصوص رو وارد کن ❤️",  

            get_password_keyboard()  
        )  

    return  


# ========================================================  
# 📸 گالری  
# ========================================================  

if text == "📸 عکس‌ها":  

    if user.get(  
        "photos",  
        False  
    ):  

        send_message(  

            chat_id,  

            "📸 کدوم عکس رو می‌خوای ببینی؟ ❤️",  

            get_photo_keyboard()  
        )  

    else:  

        user[  
            "waiting_for_password"  
        ] = True  


        send_message(  

            chat_id,  

            "🔐 برای ورود به گالری\n"  
            "رمز مخصوص رو وارد کن ❤️",  

            get_password_keyboard()  
        )  

    return  


# ========================================================  
# 📅 روز آشنایی  
# ========================================================  

if text == "📅 روز آشنایی":  

    seconds = get_meeting_seconds()  

    days = seconds // 86400  

    quote = random.choice(  
        SECOND_QUOTES  
    )  


    message = f"""

💞 روز آشنایی ما ❤️

📅 ۲۴ اسفند ۱۴۰۴

از روزی که وارد زندگی من شدی،
تا امروز، هر ثانیه برای من یک خاطره‌ی قشنگه.

🌻 {days} روز از قشنگ‌ترین فصل زندگی من گذشته.

⏱️ {seconds:,} ثانیه...

{seconds:,} ثانیه‌ای که قلبم برای تو تپیده است. ❤️

📖 {quote}

❤️ از روز آشنایی‌مان تا همیشه...
تو یکی از زیباترین اتفاق‌های زندگی منی.
"""

send_message(  

        chat_id,  

        message  
    )  

    return  


# ========================================================  
# ⏳ تولد  
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
# ❌ دستور ناشناخته  
# ========================================================  

send_message(  

    chat_id,  

    "❌ این دستور رو نمی‌شناسم.\n\n"  
    "از دکمه‌های پایین استفاده کن ❤️",  

    get_main_keyboard(chat_id)  
)

============================================================

🎂 پیام تولد

============================================================

BIRTHDAY_MESSAGE = """🎂 تولدت مبارک، ahu goozlum... ❤️

امروز فقط یک روز معمولی نیست...

امروز روزی است که یک فرشته پا به این دنیا گذاشت؛
فرشته‌ای که بعدها تمام دنیای من شد. 🌻

🍃 تولدت مبارک، زیباترین فصل زندگی من...

هر بار که لبخند می‌زنی،
انگار یک گوشه از دنیا روشن‌تر می‌شود.

هر بار که صدایت را می‌شنوم،
قلبم آرام‌تر می‌زند.

و هر بار که به تو فکر می‌کنم،
می‌فهمم چقدر خوش‌شانسم که تو را در زندگی‌ام دارم.

🌻 نسا جان...
امیدوارم امسال برایت پر از آرامش،
خنده، اتفاق‌های قشنگ
و آرزوهای برآورده‌شده باشد.

❤️ من همیشه کنارتم.
نه فقط امروز،
بلکه در تمام روزهایی که پیش رو داریم.

🎂 تولدت مبارک عشق من... 🌻

همیشه بخند ❤️
چون لبخندت زیباترین چیز دنیاست."""

============================================================

🎂 تایمر تولد

============================================================

def birthday_timer():

sent_today = False  

while True:  

    try:  

        now = get_current_iran_time()  


        if (  
            now.month == BIRTH_MONTH  
            and  
            now.day == BIRTH_DAY  
            and  
            now.hour == BIRTH_HOUR  
            and  
            now.minute == BIRTH_MINUTE  
        ):  

            if not sent_today:  

                print(  
                    "🎂 ارسال پیام تولد..."  
                )  


                # 👑 مالک جدید  

                send_message(  

                    OWNER_CHAT_ID,  

                    BIRTHDAY_MESSAGE  
                )  


                # ❤️ پارتنر  

                send_message(  

                    PARTNER_CHAT_ID,  

                    BIRTHDAY_MESSAGE  
                )  


                photo = PHOTOS[  
                    "📸 عکس ۱"  
                ]  


                if os.path.exists(  
                    photo["path"]  
                ):  

                    send_photo(  

                        OWNER_CHAT_ID,  

                        photo["path"],  

                        photo["caption"]  
                    )  


                    send_photo(  

                        PARTNER_CHAT_ID,  

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

============================================================

🌐 Webhook

============================================================

@app.route(
"/",
methods=["GET", "POST"]
)
def webhook():

if request.method == "POST":  

    try:  

        data = request.get_json(  
            silent=True  
        )  


        if not data:  

            return "OK", 200  


        # =================================================  
        # پیام  
        # =================================================  

        if "message" in data:  

            message = data[  
                "message"  
            ]  

            chat = message[  
                "chat"  
            ]  

            chat_id = str(  
                chat["id"]  
            )  


            text = message.get(  
                "text",  
                ""  
            )  


            caption = message.get(  
                "caption",  
                ""  
            )  


            # =============================================  
            # 📦 تشخیص فایل  
            # =============================================  

            file_data = None  


            # =============================================  
            # 📸 عکس  
            # =============================================  

            if "photo" in message:  

                photo = message[  
                    "photo"  
                ][-1]  


                file_data = {  

                    "type": "photo",  

                    "file_id": photo[  
                        "file_id"  
                    ],  

                    "caption": caption  
                }  


            # =============================================  
            # 🎥 فیلم  
            # =============================================  

            elif "video" in message:  

                video = message[  
                    "video"  
                ]  


                file_data = {  

                    "type": "video",  

                    "file_id": video[  
                        "file_id"  
                    ],  

                    "caption": caption  
                }  


            # =============================================  
            # 🎵 Audio / MP3  
            # =============================================  

            elif "audio" in message:  

                audio = message[  
                    "audio"  
                ]  


                file_data = {  

                    "type": "audio",  

                    "file_id": audio[  
                        "file_id"  
                    ],  

                    "caption": caption,  

                    "title": audio.get(  
                        "title",  
                        "🎵"  
                    ),  

                    "performer": audio.get(  
                        "performer",  
                        "❤️"  
                    )  
                }  


            # =============================================  
            # 🎤 Voice  
            # =============================================  

            elif "voice" in message:  

                voice = message[  
                    "voice"  
                ]  

                file_data = {  

                    "type": "voice",  

                    "file_id": voice[  
                        "file_id"  
                    ],  

                    "caption": caption  
                }  


            # =============================================  
            # 📎 Document  
            # =============================================  

            elif "document" in message:  

                doc = message[  
                    "document"  
                ]  


                mime = doc.get(  
                    "mime_type",  
                    ""  
                ).lower()  


                file_name = doc.get(  
                    "file_name",  
                    ""  
                ).lower()  


                # -----------------------------------------  
                # عکس  
                # -----------------------------------------  

                if (  
                    mime.startswith("image/")  
                    or  
                    file_name.endswith(  
                        (  
                            ".jpg",  
                            ".jpeg",  
                            ".png",  
                            ".webp",  
                            ".gif"  
                        )  
                    )  
                ):  

                    file_data = {  

                        "type": "photo",  

                        "file_id": doc[  
                            "file_id"  
                        ],  

                        "caption": caption  
                    }  


                # -----------------------------------------  
                # فیلم  
                # -----------------------------------------  

                elif (  
                    mime.startswith("video/")  
                    or  
                    file_name.endswith(  
                        (  
                            ".mp4",  
                            ".mov",  
                            ".mkv",  
                            ".avi",  
                            ".webm"  
                        )  
                    )  
                ):  

                    file_data = {  

                        "type": "video",  

                        "file_id": doc[  
                            "file_id"  
                        ],  

                        "caption": caption  
                    }  


                # -----------------------------------------  
                # موزیک  
                # -----------------------------------------  

                elif (  
                    mime.startswith("audio/")  
                    or  
                    file_name.endswith(  
                        (  
                            ".mp3",  
                            ".m4a",  
                            ".aac",  
                            ".ogg",  
                            ".wav",  
                            ".flac"  
                        )  
                    )  
                ):  

                    file_data = {  

                        "type": "audio",  

                        "file_id": doc[  
                            "file_id"  
                        ],  

                        "caption": caption,  

                        "title": file_name or "🎵",  

                        "performer": "❤️"  
                    }  


                # -----------------------------------------  
                # سایر فایل‌ها  
                # -----------------------------------------  

                else:  

                    file_data = {  

                        "type": "document",  

                        "file_id": doc[  
                            "file_id"  
                        ],  

                        "caption": caption,  

                        "file_name": doc.get(  
                            "file_name",  
                            ""  
                        )  
                    }  


            # =============================================  
            # 👤 اطلاعات کاربر  
            # =============================================  

            first_name = chat.get(  
                "first_name",  
                ""  
            )  

            last_name = chat.get(  
                "last_name",  
                ""  
            )  

            username = chat.get(  
                "username",  
                ""  
            )  


            contact = message.get(  
                "contact"  
            )  


            phone_number = ""  


            if contact:  

                phone_number = contact.get(  
                    "phone_number",  
                    ""  
                )  


            # =============================================  
            # 📊 گزارش تعامل  
            # =============================================  

            if text == "/start":  

                action = (  
                    "🚀 کاربر /start زد"  
                )  

            elif text:  

                action = (  
                    "🖱️ کاربر دکمه/پیام فرستاد:\n"  
                    + text  
                )  

            elif file_data:  

                if file_data["type"] == "photo":  

                    action = (  
                        "📸 کاربر عکس ارسال کرد"  
                    )  

                elif file_data["type"] == "video":  

                    action = (  
                        "🎥 کاربر فیلم ارسال کرد"  
                    )  

                elif file_data["type"] == "audio":  

                    action = (  
                        "🎵 کاربر موزیک/MP3 ارسال کرد"  
                    )  

                elif file_data["type"] == "voice":  

                    action = (  
                        "🎤 کاربر ویس ارسال کرد"  
                    )  

                elif file_data["type"] == "document":  

                    action = (  
                        "📎 کاربر فایل ارسال کرد"  
                    )  

                else:  

                    action = (  
                        "📎 کاربر فایل ارسال کرد"  
                    )  

            else:  

                action = (  
                    "💬 کاربر یک Update بدون متن فرستاد"  
                )  


            report_user_interaction(  

                chat_id,  

                action,  

                first_name,  

                last_name,  

                username,  

                phone_number  
            )  


            # =============================================  
            # 🤖 پردازش  
            # =============================================  

            handle_message(  

                chat_id,  

                text,  

                file_data  
            )  


        # =================================================  
        # Callback  
        # =================================================  

        elif "callback_query" in data:  

            callback = data[  
                "callback_query"  
            ]  

            from_user = callback[  
                "from"  
            ]  

            chat_id = str(  
                from_user["id"]  
            )  

            first_name = from_user.get(  
                "first_name",  
                ""  
            )  

            last_name = from_user.get(  
                "last_name",  
                ""  
            )  

            username = from_user.get(  
                "username",  
                ""  
            )  

            report_user_interaction(  

                chat_id,  

                "🖱️ کاربر روی Inline Button کلیک کرد",  

                first_name,  

                last_name,  

                username,  

                ""  
            )  


        # =================================================  
        # Edited Message  
        # =================================================  

        elif "edited_message" in data:  

            edited = data[  
                "edited_message"  
            ]  

            chat = edited[  
                "chat"  
            ]  

            chat_id = str(  
                chat["id"]  
            )  


            report_user_interaction(  

                chat_id,  

                "✏️ پیام ویرایش شد",  

                chat.get(  
                    "first_name",  
                    ""  
                ),  

                chat.get(  
                    "last_name",  
                    ""  
                ),  

                chat.get(  
                    "username",  
                    ""  
                ),  

                ""  
            )  


    except Exception as e:  

        print(  
            "Webhook error:",  
            e  
        )  


return "OK", 200

============================================================

🩺 Health

============================================================

@app.route(
"/health",
methods=["GET"]
)
def health():

return jsonify({  

    "status": "ok",  

    "service": "rose-bot",  

    "owner": OWNER_CHAT_ID,  

    "partner": PARTNER_CHAT_ID,  

    "chat": "enabled",  

    "audio": "enabled",  

    "mp3": "enabled",  

    "protected_media": "enabled",  

    "documents": "enabled",  

    "voice": "enabled"  
})

============================================================

🚀 اجرای برنامه

============================================================

if name == "main":

print(  
    "🚀 ربات ahu goozlum روشن شد..."  
)  

print(  
    f"👑 مالک جدید: {OWNER_CHAT_ID}"  
)  

print(  
    f"❤️ پارتنر: {PARTNER_CHAT_ID}"  
)  

print(  
    f"🎂 تولد: {BIRTH_DAY}/{BIRTH_MONTH}"  
)  

print(  
    f"📸 تعداد عکس‌ها: {len(PHOTOS)}"  
)  

print(  
    "🩺 مسیر سلامت: /health"  
)  

print(  
    "📊 گزارش تعامل‌ها فعال است!"  
)  

print(  
    "💬 چت دوطرفه فعال است!"  
)  

print(  
    "📸 ارسال عکس دوطرفه فعال است!"  
)  

print(  
    "🎥 ارسال فیلم دوطرفه فعال است!"  
)  

print(  
    "🎵 ارسال موزیک و MP3 دوطرفه فعال است!"  
)  

print(  
    "📎 ارسال فایل فعال است!"  
)  

print(  
    "🎤 ارسال ویس فعال است!"  
)  

print(  
    "🔐 محافظت از رسانه برای پارتنر فعال است!"  
)  

print(  
    f"🌐 آدرس وب‌سایت: {WEBSITE_URL}"  
)  


# =========================================  
# 🎂 تایمر تولد  
# =========================================  

timer_thread = threading.Thread(  

    target=birthday_timer,  

    daemon=True  
)  

timer_thread.start()  


# =========================================  
# 🌐 اجرای Flask  
# =========================================  

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

میخوام واسه این کد تو ترموکس چیزی اضافه کنم مثلا یک فضای ابری اضافه کنم که پاتنرم تمام ویدیو هاشو اونجا سیو کنه خودش مثلا دکمه ربات بزنه ویدیو عکس بفرست اونحا وقتی هم خواست دکمه رو بزنه همش بیاد بالا عکس و فیلم ها رو میگم
