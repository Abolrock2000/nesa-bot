from flask import Flask, request, render_template_string
import requests
import random
import datetime
import os
import threading
import time

app = Flask(__name__)

# ============================================================
# تنظیمات
# ============================================================

# توکن را در Render > Environment Variables با نام BOT_TOKEN بگذار.
TOKEN = os.environ.get("BOT_TOKEN", "PASTE_YOUR_NEW_BOT_TOKEN_HERE")
YOUR_CHAT_ID = os.environ.get("YOUR_CHAT_ID", "1228473012")

PASSWORD = os.environ.get("LOVE_PASSWORD", "1386")

BIRTH_DAY = 8
BIRTH_MONTH = 8
BIRTH_HOUR = 0
BIRTH_MINUTE = 0

IRAN_OFFSET = datetime.timedelta(hours=3, minutes=30)
user_access = {}

MEETING_DATE = datetime.datetime(
    2026, 3, 15, 0, 0, 0,
    tzinfo=datetime.timezone(IRAN_OFFSET)
)

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

SECOND_QUOTES = [
    "هر ثانیه‌ای که می‌گذرد، عشق من به تو عمیق‌تر می‌شود... ❤️",
    "ثانیه‌ها می‌گذرند، اما عشق من به تو هرگز کهنه نمی‌شود... 🌹",
    "در هر ثانیه‌ای از زندگی‌ام، تو را نفس می‌کشم... 💫",
    "ثانیه‌های بی‌تو طولانی‌اند، اما کنار تو حتی ساعت‌ها هم کوتاه‌اند... ✨",
    "هر ثانیه که می‌گذرد، یک دلیل تازه برای دوست داشتن تو پیدا می‌کنم... ❤️",
    "ثانیه‌ها را بشمار، اما عشق را نه؛ چون عشق من به تو بی‌نهایت است... 🌸"
]

LOVE_LETTERS = [
"""💌 نامه‌ای از دل من...

نسای من،

اگر بخواهم تمام زیبایی‌های دنیا را
در یک کلمه خلاصه کنم،
آن کلمه برای من «تو» است.

از وقتی وارد زندگی من شدی،
خیلی از چیزها معنای تازه‌ای پیدا کردند.

لبخند، دلتنگی، انتظار،
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

تو برای من فقط یک نفر نیستی.

تو بخشی از آرامش،
خنده‌ها، فکرها
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

تو آمدی و آرام‌آرام
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

def get_current_iran_time():
    return datetime.datetime.now(datetime.timezone.utc).astimezone(
        datetime.timezone(IRAN_OFFSET)
    )

def get_meeting_seconds():
    now = get_current_iran_time()
    return max(0, int((now - MEETING_DATE).total_seconds()))

def get_main_keyboard():
    return {
        "keyboard": [
            ["📸 عکس‌ها"],
            ["🎂 تولد نسا", "📅 روز آشنایی"],
            ["⏳ ساعت تا تولدت"],
            ["💌 نامه عشق"],
            ["❤️ صفحه عشق"],
            ["🎉 تبریک برای عشقم"],
            ["🤝 آشتی کنیم"],
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
        "keyboard": [["🔙 بازگشت به منو"]],
        "resize_keyboard": True
    }

def telegram_url(method):
    return f"https://api.telegram.org/bot{TOKEN}/{method}"

def send_message(chat_id, text, reply_markup=None):
    try:
        payload = {"chat_id": chat_id, "text": text}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        r = requests.post(telegram_url("sendMessage"), json=payload, timeout=12)
        return r.ok
    except Exception as e:
        print("send_message:", e)
        return False

def send_photo(chat_id, photo_path, caption=""):
    try:
        if photo_path.startswith("http"):
            r = requests.post(
                telegram_url("sendPhoto"),
                data={"chat_id": chat_id, "photo": photo_path, "caption": caption},
                timeout=20
            )
            return r.ok

        if not os.path.exists(photo_path):
            send_message(chat_id, "❌ عکس پیدا نشد!")
            return False

        with open(photo_path, "rb") as photo:
            r = requests.post(
                telegram_url("sendPhoto"),
                data={"chat_id": chat_id, "caption": caption},
                files={"photo": photo},
                timeout=30
            )
        return r.ok
    except Exception as e:
        print("send_photo:", e)
        return False

def handle_message(chat_id, text):
    chat_id = str(chat_id)
    text = (text or "").strip()

    if text == "/start":
        user_access[chat_id] = {"photos": False, "waiting_for_password": False}
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
🤝 اگر غرورت اجازه نداد پیام بدی، از اینجا آشتی کن

🌻 هر دکمه یک تکه از داستان ماست...""",
            get_main_keyboard()
        )
        return

    state = user_access.setdefault(
        chat_id, {"photos": False, "waiting_for_password": False}
    )

    if text == "🔙 بازگشت به منو":
        state["waiting_for_password"] = False
        send_message(chat_id, "🏠 برگشتیم به منوی اصلی ❤️", get_main_keyboard())
        return

    if state.get("waiting_for_password"):
        if text == PASSWORD:
            state["photos"] = True
            state["waiting_for_password"] = False
            send_message(
                chat_id,
                "✅ رمز درست بود!\n\n🔓 گالری اختصاصی باز شد ❤️",
                get_photo_keyboard()
            )
        else:
            send_message(
                chat_id,
                "❌ رمز اشتباهه!\n\nدوباره امتحان کن ❤️",
                get_password_keyboard()
            )
        return

    if text == "📸 عکس‌ها" or text in PHOTOS:
        if not state.get("photos"):
            state["waiting_for_password"] = True
            send_message(
                chat_id,
                "🔐 این قسمت خصوصی و مخصوص خودته.\n\nلطفاً رمز مخصوص رو وارد کن ❤️",
                get_password_keyboard()
            )
            return

        if text == "📸 عکس‌ها":
            send_message(chat_id, "📸 کدوم عکس رو می‌خوای ببینی؟ ❤️", get_photo_keyboard())
        else:
            p = PHOTOS[text]
            send_photo(chat_id, p["path"], p["caption"])
        return

    if text == "🎂 تولد نسا":
        send_message(chat_id, BIRTHDAY_MESSAGE)
        return

    if text == "📅 روز آشنایی":
        seconds = get_meeting_seconds()
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        send_message(
            chat_id,
            f"""💞 روز آشنایی ما ❤️

📅 ۲۴ اسفند ۱۴۰۴

🌻 {days} روز از قشنگ‌ترین فصل زندگی ما گذشته.

⏱️ {seconds:,} ثانیه
یعنی:
{days} روز و {hours} ساعت و {minutes} دقیقه و {secs} ثانیه

❤️ تمام این ثانیه‌ها برای من
یعنی زمانی که قلبم برای تو تپیده است.

و اگر قرار باشد تمام این لحظه‌ها را
دوباره زندگی کنم،
باز هم تو را انتخاب می‌کنم.

🌹 {random.choice(SECOND_QUOTES)}

❤️ از روز آشنایی‌مان تا همیشه...
تو یکی از زیباترین اتفاق‌های زندگی منی."""
        )
        return

    if text == "⏳ ساعت تا تولدت":
        now = get_current_iran_time()
        birth = datetime.datetime(
            now.year, BIRTH_MONTH, BIRTH_DAY,
            BIRTH_HOUR, BIRTH_MINUTE,
            tzinfo=datetime.timezone(IRAN_OFFSET)
        )
        if now >= birth:
            birth = datetime.datetime(
                now.year + 1, BIRTH_MONTH, BIRTH_DAY,
                BIRTH_HOUR, BIRTH_MINUTE,
                tzinfo=datetime.timezone(IRAN_OFFSET)
            )
        total = max(0, int((birth - now).total_seconds()))
        days, rem = divmod(total, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, seconds = divmod(rem, 60)

        send_message(
            chat_id,
            f"""🎂 شمارش معکوس برای روز قشنگ تو...

🌻 تولد ahu goozlum

⏳ {days} روز
🕐 {hours} ساعت
⏱️ {minutes} دقیقه
⏲️ {seconds} ثانیه

هر لحظه که می‌گذره،
یک قدم به روزی نزدیک‌تر می‌شیم
که دنیا قشنگ‌تر شد؛
روزی که تو به دنیا اومدی. ❤️🌻"""
        )
        return

    if text == "💌 نامه عشق":
        send_message(chat_id, random.choice(LOVE_LETTERS))
        return

    if text == "❤️ صفحه عشق":
        send_message(
            chat_id,
            """❤️ یک سورپرایز مخصوص تو آماده کردم...

چهره‌ات با کلمات
I LOVE YOU NESA
ساخته شده. ✨❤️

👇 بازش کن:

https://nesa-bot.onrender.com/love"""
        )
        return

    if text == "🎉 تبریک برای عشقم":
        send_message(
            chat_id,
            """🎁 یک هدیه مخصوص برای تو آماده شده...

آروم بازش کن 🌻❤️

👇 سورپرایز تولدت:

https://nesa-bot.onrender.com/birthday_surprise.html"""
        )
        return

    if text == "🤝 آشتی کنیم":
        send_message(
            chat_id,
            """🤍 اگر دلت گرفته و غرورت اجازه نمی‌ده مستقیم پیام بدی...

اینجا فقط حرف دلت رو بنویس.
من پیام رو برای صاحب این ربات می‌فرستم.

💌 هرچی می‌خوای بگو؛
حتی فقط بنویس «دلم برات تنگ شده»."""
        )
        state["waiting_for_reconciliation"] = True
        return

    if state.get("waiting_for_reconciliation"):
        state["waiting_for_reconciliation"] = False
        message = f"""🤝 پیام آشتی جدید ❤️

از طرف:
{chat_id}

💌 متن پیام:
{text}"""
        send_message(YOUR_CHAT_ID, message)
        send_message(
            chat_id,
            "❤️ پیامت با موفقیت بهش رسید.\n\nامیدوارم خیلی زود آشتی کنید 🌹"
        )
        return

    send_message(chat_id, "❌ از دکمه‌های پایین استفاده کن ❤️", get_main_keyboard())

# ============================================================
# صفحه تولد
# ============================================================

BIRTHDAY_PAGE = r"""
<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>🌻 تولدت مبارک نسا ❤️</title>
<style>
*{box-sizing:border-box}
html,body{margin:0;width:100%;height:100%;overflow:hidden}
body{
 background:radial-gradient(circle,#401522,#12070b 55%,#030204);
 color:#fff;font-family:Tahoma,Arial,sans-serif;
 display:flex;align-items:center;justify-content:center;
}
#scene{position:fixed;inset:0;overflow:hidden;pointer-events:none;z-index:1}
.container{width:min(92%,520px);position:relative;z-index:10;text-align:center}
.card{
 padding:28px 22px;border-radius:28px;
 background:rgba(28,7,15,.82);
 border:1px solid rgba(255,190,120,.45);
 box-shadow:0 0 60px rgba(255,80,120,.25),inset 0 0 30px rgba(255,180,70,.08);
 backdrop-filter:blur(12px)
}
.gift{font-size:125px;cursor:pointer;animation:float 2.5s ease-in-out infinite;filter:drop-shadow(0 0 25px #ff416c)}
@keyframes float{50%{transform:translateY(-18px) rotate(3deg)}}
#password,#birthday{display:none}
h1{color:#ffd36e;text-shadow:0 0 25px #ff9d00}
p{line-height:2}
input{width:100%;padding:14px;border-radius:15px;background:#090308;color:#fff;border:1px solid #ff6685;text-align:center;font-size:20px}
button{padding:14px 28px;margin-top:15px;border:0;border-radius:30px;background:linear-gradient(45deg,#ff416c,#ff758c);color:white;font-weight:bold;font-size:17px}
.photo{width:min(100%,340px);border-radius:20px;margin-top:18px;border:2px solid #ffc66d;box-shadow:0 0 35px #ff9d0055}
.fall{position:absolute;top:-80px;animation:fall linear forwards;user-select:none}
@keyframes fall{0%{transform:translateY(-80px) rotate(0);opacity:0}10%{opacity:1}100%{transform:translateY(115vh) rotate(720deg);opacity:0}}
.sun{position:absolute;bottom:-120px;animation:sunrise linear forwards;filter:drop-shadow(0 0 12px #ffb000)}
@keyframes sunrise{0%{transform:translateY(150px) rotate(-20deg);opacity:0}15%{opacity:1}100%{transform:translateY(-120vh) rotate(360deg);opacity:0}}
</style>
</head>
<body>
<div id="scene"></div>

<div class="container" id="giftBox">
 <div class="gift" onclick="openGift()">🎁</div>
 <p>🌻 برای باز کردن هدیه کلیک کن 🌻</p>
</div>

<div class="container" id="password">
 <div class="card">
  <h1>🔐 هدیه مخصوص تو</h1>
  <p>تاریخ تولدت رو وارد کن ❤️</p>
  <input id="pass" type="password" placeholder="رمز مخصوص">
  <button onclick="check()">🌻 باز کردن هدیه</button>
  <p id="err" style="display:none;color:#ff6685">❌ رمز اشتباهه</p>
 </div>
</div>

<div class="container" id="birthday">
 <div class="card">
  <h1>🌻🎂 تولدت مبارک نسا 🎂🌻</h1>
  <p>
  امروز فقط تولد تو نیست؛
  روزیه که دنیا یک دلیل تازه برای زیباتر شدن پیدا کرد. ❤️
  <br><br>
  تو یکی از قشنگ‌ترین اتفاق‌های زندگی منی.
  <br><br>
  🌻 امیدوارم همیشه بخندی، خوشحال باشی
  و به تمام آرزوهات برسی.
  <br><br>
  ❤️ تولدت مبارک عشق من ❤️
  <br>
  🌻 دوستت دارم 🌻
  </p>
  <img class="photo" src="https://i.postimg.cc/5tDhyRgM/IMG-20260318-184739-714.jpg">
 </div>
</div>

<script>
const PASSWORD = "1386";

function openGift(){
 document.getElementById("giftBox").style.display="none";
 document.getElementById("password").style.display="block";
 document.getElementById("pass").focus();
}

function check(){
 if(document.getElementById("pass").value.trim()===PASSWORD){
  document.getElementById("password").style.display="none";
  document.getElementById("birthday").style.display="block";
  startFlowers();
 }else document.getElementById("err").style.display="block";
}

function startFlowers(){
 const scene=document.getElementById("scene");
 const flowers=["🌻","🌻","🌻","🌼","🌺","🌸","🌷","🪻","🌹","💐"];
 const hearts=["❤️","💖","💕","💗","💘","❤️‍🔥","✨"];
 for(let i=0;i<75;i++){
  let x=document.createElement("div");
  x.className="fall";
  x.textContent=flowers[Math.floor(Math.random()*flowers.length)];
  x.style.left=Math.random()*100+"%";
  x.style.fontSize=(18+Math.random()*35)+"px";
  x.style.animationDuration=(5+Math.random()*7)+"s";
  x.style.animationDelay=Math.random()*4+"s";
  scene.appendChild(x);
  setTimeout(()=>x.remove(),15000);
 }
 for(let i=0;i<55;i++){
  let x=document.createElement("div");
  x.className="fall";
  x.textContent=hearts[Math.floor(Math.random()*hearts.length)];
  x.style.left=Math.random()*100+"%";
  x.style.fontSize=(14+Math.random()*28)+"px";
  x.style.animationDuration=(4+Math.random()*6)+"s";
  x.style.animationDelay=Math.random()*4+"s";
  scene.appendChild(x);
  setTimeout(()=>x.remove(),14000);
 }
}
document.getElementById("pass").addEventListener("keydown",e=>{if(e.key==="Enter")check()});
</script>
</body>
</html>
"""

LOVE_PAGE = r"""
<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>❤️ I Love You Nesa ❤️</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#030303;min-height:100vh;display:flex;align-items:center;justify-content:center;overflow:hidden}
canvas{max-width:100vw;max-height:100vh}.txt{position:fixed;bottom:18px;width:100%;text-align:center;color:#ff6685;font:14px Arial;letter-spacing:4px;text-shadow:0 0 18px #f24}
</style></head>
<body>
<canvas id="c"></canvas><div class="txt">❤️ AHU GOOZLUM ❤️</div>
<script>
const url="https://i.postimg.cc/5tDhyRgM/IMG-20260318-184739-714.jpg";
const c=document.getElementById("c"),x=c.getContext("2d"),img=new Image();
img.crossOrigin="anonymous";img.src=url;
img.onload=()=>{
 c.width=img.width;c.height=img.height;x.drawImage(img,0,0);
 const p=x.getImageData(0,0,c.width,c.height).data;
 x.fillStyle="#000";x.fillRect(0,0,c.width,c.height);
 x.textAlign="center";x.textBaseline="middle";x.font="7px Arial";
 const words=["I","LOVE","YOU","NESA"],step=7;
 for(let y=0;y<c.height;y+=step)for(let z=0;z<c.width;z+=step){
  let i=(y*c.width+z)*4,b=(p[i]+p[i+1]+p[i+2])/3;
  if(b>240)continue;
  x.fillStyle=`rgb(${p[i]},${p[i+1]},${p[i+2]})`;
  x.fillText(words[(z+y)%words.length],z,y);
 }
}
</script></body></html>
"""

@app.route("/", methods=["GET","POST"])
def webhook():
    if request.method == "POST":
        try:
            data=request.get_json(silent=True) or {}
            if "message" in data:
                msg=data["message"]
                chat_id=msg["chat"]["id"]
                text=msg.get("text","")
                handle_message(chat_id,text)
        except Exception as e:
            print("Webhook error:",e)
    return "OK",200

@app.route("/love")
def love():
    return render_template_string(LOVE_PAGE)

@app.route("/birthday_surprise.html")
def birthday():
    return render_template_string(BIRTHDAY_PAGE)

@app.route("/health")
def health():
    return "OK",200

def birthday_timer():
    sent=False
    while True:
        try:
            now=get_current_iran_time()
            if now.month==BIRTH_MONTH and now.day==BIRTH_DAY and now.hour==BIRTH_HOUR and now.minute==BIRTH_MINUTE:
                if not sent:
                    send_message(YOUR_CHAT_ID,BIRTHDAY_MESSAGE)
                    sent=True
            else:
                sent=False
        except Exception as e:
            print("timer:",e)
        time.sleep(30)

if __name__=="__main__":
    print("❤️ Bot starting...")
    threading.Thread(target=birthday_timer,daemon=True).start()
    port=int(os.environ.get("PORT","10000"))
    app.run(host="0.0.0.0",port=port,debug=False)
