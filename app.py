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
# ====================== تنظیمات ربات =========================
# ============================================================

TOKEN = "8967116754:AAFJlNPRH8Cht-8qKo3zEHCJvSX1JrBGGXQ"

YOUR_CHAT_ID = "1228473012"

PASSWORD = "1386"

BIRTH_DAY = 8
BIRTH_MONTH = 8
BIRTH_HOUR = 0
BIRTH_MINUTE = 0

IRAN_OFFSET = datetime.timedelta(hours=3, minutes=30)

SETAR_LINK = "https://t.me/+robRoFDJYKtlNmRk"

# ============================================================
# ======================= زمان ایران ==========================
# ============================================================

def get_current_iran_time():
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    iran_time = utc_now.astimezone(datetime.timezone(IRAN_OFFSET))
    return iran_time

# ============================================================
# ========================== عکس‌ها ===========================
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
# ====================== صفحه خوش‌آمدگویی =====================
# ============================================================

WELCOME_PAGE = """
<!DOCTYPE html>
<html lang="fa">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>برای نسا ❤️</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;}
body{
    min-height:100vh;
    overflow:hidden;
    display:flex;
    justify-content:center;
    align-items:center;
    font-family:Tahoma,Arial,sans-serif;
    background:radial-gradient(circle at top,#432020,#120909 45%,#050505);
}
.glow{
    position:fixed;
    width:350px;
    height:350px;
    background:#ffb300;
    filter:blur(120px);
    opacity:.18;
    border-radius:50%;
}
.flower{
    position:fixed;
    top:-80px;
    z-index:2;
    animation:flowerFall linear infinite;
    pointer-events:none;
}
@keyframes flowerFall{
    0%{transform:translateY(-100px) rotate(0deg);opacity:0;}
    10%{opacity:1;}
    100%{transform:translateY(110vh) rotate(720deg);opacity:.2;}
}
.heart{
    position:fixed;
    top:-50px;
    z-index:1;
    animation:heartFall linear infinite;
}
@keyframes heartFall{
    0%{transform:translateY(-50px) rotate(0deg);opacity:0;}
    15%{opacity:1;}
    100%{transform:translateY(110vh) rotate(360deg);opacity:0;}
}
.card{
    position:relative;
    z-index:10;
    width:90%;
    max-width:430px;
    padding:35px 25px;
    text-align:center;
    background:linear-gradient(145deg,rgba(255,255,255,.10),rgba(255,255,255,.03));
    border:1px solid rgba(255,193,7,.35);
    border-radius:30px;
    backdrop-filter:blur(18px);
    box-shadow:0 0 70px rgba(255,170,0,.18);
    color:white;
}
.gift-container{
    width:180px;
    height:170px;
    margin:0 auto 20px;
    position:relative;
    cursor:pointer;
    animation:floating 3s ease-in-out infinite;
}
@keyframes floating{
    0%,100%{transform:translateY(0);}
    50%{transform:translateY(-12px);}
}
.gift{
    position:absolute;
    width:140px;
    height:100px;
    left:20px;
    bottom:10px;
    background:linear-gradient(135deg,#ff1744,#c51162);
    border-radius:8px;
    box-shadow:0 15px 40px rgba(255,0,70,.4);
}
.ribbon-v{
    position:absolute;
    width:22px;
    height:100%;
    background:#ffd54f;
    left:59px;
}
.ribbon-h{
    position:absolute;
    width:100%;
    height:20px;
    background:#ffd54f;
    top:40px;
}
.lid{
    position:absolute;
    width:155px;
    height:35px;
    left:12px;
    bottom:100px;
    background:linear-gradient(135deg,#ff4081,#d50000);
    border-radius:8px;
    transition:transform 1s,top 1s;
}
.bow{
    position:absolute;
    left:62px;
    bottom:130px;
    font-size:55px;
    z-index:5;
    transition:1s;
}
.gift-container.open .lid{
    transform:translateY(-100px) rotate(-12deg);
}
.gift-container.open .bow{
    transform:translateY(-100px) rotate(25deg);
}
h1{
    font-size:28px;
    color:#ffd54f;
    text-shadow:0 0 20px rgba(255,193,7,.5);
    margin-bottom:12px;
}
p{
    color:#ffdce5;
    line-height:2;
    font-size:15px;
}
.message{
    margin-top:20px;
    color:#ffcc80;
    font-size:14px;
    opacity:.9;
}
.open-btn{
    margin-top:22px;
    padding:13px 28px;
    border:none;
    border-radius:30px;
    background:linear-gradient(45deg,#ff9800,#ffc107,#ffca28);
    color:#3e1c00;
    font-size:16px;
    font-weight:bold;
    cursor:pointer;
    box-shadow:0 0 25px rgba(255,193,7,.35);
}
.hidden{
    display:none;
}
.final{
    margin-top:20px;
    color:#fff;
    animation:fadeIn 1.5s;
}
@keyframes fadeIn{
    from{opacity:0;transform:scale(.8);}
    to{opacity:1;transform:scale(1);}
}
.sunflower{
    font-size:45px;
    display:block;
    margin:10px;
}
</style>
</head>
<body>
<div class="glow"></div>
<div id="falling"></div>
<div class="card">
    <div class="gift-container" id="gift" onclick="openGift()">
        <div class="bow">🎀</div>
        <div class="lid"></div>
        <div class="gift">
            <div class="ribbon-v"></div>
            <div class="ribbon-h"></div>
        </div>
    </div>
    <h1>🎁 یک هدیه برای تو...</h1>
    <p>
        این کادو فقط با لمس تو باز می‌شود...
        <br>
        چون صاحبش فقط یک نفر است ❤️
    </p>
    <button class="open-btn" onclick="openGift()">🌻 بازش کن عشقم</button>
    <div id="final" class="final hidden">
        <span class="sunflower">🌻🌻🌻</span>
        <p>
            نسا جان ❤️
            <br><br>
            پشت این کادو،
            یک عالمه عشق برای تو قایم کرده‌ام...
            <br><br>
            🌻 تو قشنگ‌ترین گل زندگی منی 🌻
            <br>
            و هیچ گلی در این دنیا
            جای تو را نمی‌گیرد.
        </p>
        <span class="sunflower">🌻🌸🌺🌷🌻</span>
    </div>
</div>
<script>
const flowers = ["🌻","🌻","🌸","🌺","🌷","🌹","💮","🌼"];
const hearts = ["❤️","💖","💕","💗","💘"];
function createFalling(){
    const container = document.getElementById("falling");
    for(let i=0;i<45;i++){
        const f = document.createElement("div");
        f.className="flower";
        f.innerText = flowers[Math.floor(Math.random()*flowers.length)];
        f.style.left = Math.random()*100+"%";
        f.style.fontSize = (18+Math.random()*28)+"px";
        f.style.animationDuration = (5+Math.random()*8)+"s";
        f.style.animationDelay = Math.random()*8+"s";
        container.appendChild(f);
    }
    for(let i=0;i<35;i++){
        const h = document.createElement("div");
        h.className="heart";
        h.innerText = hearts[Math.floor(Math.random()*hearts.length)];
        h.style.left = Math.random()*100+"%";
        h.style.fontSize = (14+Math.random()*22)+"px";
        h.style.animationDuration = (5+Math.random()*7)+"s";
        h.style.animationDelay = Math.random()*8+"s";
        container.appendChild(h);
    }
}
function openGift(){
    const gift = document.getElementById("gift");
    gift.classList.add("open");
    setTimeout(()=>{
        document.getElementById("final").classList.remove("hidden");
    },800);
}
createFalling();
</script>
</body>
</html>
"""

# ============================================================
# ====================== صفحه تولد =============================
# ============================================================

BIRTHDAY_SURPRISE_PAGE = """
<!DOCTYPE html>
<html lang="fa">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>تولدت مبارک نسا ❤️</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;}
body{
    min-height:100vh;
    background:radial-gradient(circle at top,#3b111b,#100509 55%,#030303);
    color:white;
    font-family:Tahoma,Arial,sans-serif;
    display:flex;
    justify-content:center;
    align-items:center;
    overflow:hidden;
}
.container{
    width:92%;
    max-width:500px;
    text-align:center;
    position:relative;
    z-index:10;
}
.birthday-content{
    padding:30px 22px;
    border-radius:28px;
    background:rgba(30,10,18,.80);
    backdrop-filter:blur(15px);
    border:1px solid rgba(255,193,7,.35);
    box-shadow:0 0 70px rgba(255,50,100,.18);
}
h1{
    color:#ffd54f;
    font-size:29px;
    margin-bottom:18px;
    text-shadow:0 0 25px #ff9800;
}
.message{
    color:#ffdce5;
    line-height:2;
    font-size:15px;
}
.highlight{
    color:#ffca28;
    font-weight:bold;
    font-size:17px;
}
.birthday-photo{
    width:100%;
    max-width:340px;
    border-radius:20px;
    margin-top:22px;
    border:3px solid rgba(255,193,7,.5);
    box-shadow:0 0 35px rgba(255,193,7,.25);
}
.fall{
    position:fixed;
    top:-60px;
    z-index:2;
    animation:falling linear infinite;
}
@keyframes falling{
    from{transform:translateY(-70px) rotate(0);opacity:0;}
    15%{opacity:1;}
    to{transform:translateY(110vh) rotate(720deg);opacity:0;}
}
.small{
    color:#ffb6c9;
    margin-top:18px;
    font-size:13px;
    line-height:1.8;
}
</style>
</head>
<body>
<div id="falling"></div>
<div class="container">
<div class="birthday-content">
<h1>🎂 تولدت مبارک عشقم ❤️</h1>
<div class="message">
امروز فقط یک روز معمولی نیست...
<br>
امروز روزی است که
دنیا یکی از زیباترین آدم‌هایش را
به خودش هدیه گرفت.
<br><br>
<span class="highlight">🌻 نسا جان، تولدت مبارک 🌻</span>
<br><br>
از وقتی وارد زندگی من شدی،
بعضی از ساده‌ترین لحظه‌ها
برای من تبدیل به قشنگ‌ترین خاطره‌ها شدند.
<br><br>
❤️ دوستت دارم؛
نه فقط برای امروز،
بلکه برای تمام روزهایی که
قرار است کنار هم بسازیم.
<br><br>
🌹 امیدوارم سال جدید زندگی‌ات
پر از آرامش،
لبخند،
موفقیت
و اتفاق‌های قشنگ باشد.
<br><br>
<span class="highlight">تو یکی از قشنگ‌ترین اتفاق‌های زندگی منی... ❤️</span>
</div>
<img class="birthday-photo" src="https://i.postimg.cc/5tDhyRgM/IMG-20260318-184739-714.jpg" alt="Nesa">
<div class="small">
❤️ این صفحه فقط برای تو ساخته شده...
<br>
🌻 با عشق، برای نسا 🌻
</div>
</div>
</div>
<script>
const items=["🌻","🌻","🌻","❤️","💖","🌹","🌸","🌺","🌷","✨"];
for(let i=0;i<70;i++){
    const el = document.createElement("div");
    el.className="fall";
    el.innerText = items[Math.floor(Math.random()*items.length)];
    el.style.left = Math.random()*100+"%";
    el.style.fontSize = (15+Math.random()*30)+"px";
    el.style.animationDuration = (5+Math.random()*8)+"s";
    el.style.animationDelay = Math.random()*8+"s";
    document.getElementById("falling").appendChild(el);
}
</script>
</body>
</html>
"""

# ============================================================
# ====================== صفحه عشق =============================
# ============================================================

PHOTO_MOSAIC_PAGE = """
<!DOCTYPE html>
<html lang="fa">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>❤️ I LOVE YOU NESA ❤️</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{
    background:#050505;
    display:flex;
    justify-content:center;
    align-items:center;
    height:100vh;
    overflow:hidden;
}
canvas{
    display:block;
    max-width:100vw;
    max-height:100vh;
    width:auto;
    height:auto;
}
.watermark{
    position:fixed;
    bottom:18px;
    left:0;
    right:0;
    text-align:center;
    color:#ff446688;
    font-family:Arial;
    font-size:14px;
    letter-spacing:3px;
    text-shadow:0 0 20px #ff2244;
    pointer-events:none;
}
</style>
</head>
<body>
<canvas id="photoCanvas"></canvas>
<div class="watermark">❤️ ahu goozlum ❤️</div>
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
            let index=(y*canvas.width+x)*4;
            let r=pixels[index];
            let g=pixels[index+1];
            let b=pixels[index+2];
            let bright=(r+g+b)/3;
            if(bright>240) continue;
            ctx.fillStyle=`rgb(${r},${g},${b})`;
            let word=words[(x+y)%words.length];
            ctx.fillText(word,x,y);
        }
    }
};
</script>
</body>
</html>
"""

# ============================================================
# ======================= متن تولد ============================
# ============================================================

BIRTHDAY_MESSAGE = """
🎂 تولدت مبارک، ahu goozlum... ❤️

🌻 امروز روزی است که دنیا یکی از زیباترین آدم‌هایش را پیدا کرد.

روزی که آسمان،
یکی از قشنگ‌ترین فرشته‌هایش را به زمین فرستاد.

🌹 نسا جان،
تولدت مبارک،
ای زیباترین فصل زندگی من...

❤️ امیدوارم همیشه لبخند روی لبت باشد،
دلت آرام باشد
و زندگی برایت پر از اتفاق‌های قشنگ باشد.

💫 من که همیشه در کنار توام،
امروز بیشتر از همیشه دوستت دارم.

🌻 تو برای من فقط یک نفر نیستی؛
تو بخشی از قشنگ‌ترین احساس‌های زندگی منی.

❤️ به امید سال‌هایی پر از عشق،
آرامش،
خنده
و خاطره‌های قشنگ...
"""

# ============================================================
# ====================== متن روز آشنایی =======================
# ============================================================

SECOND_QUOTES = [
    "هر ثانیه‌ای که می‌گذرد، عشق من به تو عمیق‌تر می‌شود... ❤️",
    "ثانیه‌ها می‌گذرند، اما چیزی که بین قلب من و تو ساخته شده، کهنه نمی‌شود... 🌹",
    "اگر تمام دنیا را در ثانیه‌ها خلاصه کنم، باز هم هر ثانیه‌اش را با تو می‌خواهم... 💫",
    "هر ثانیه که می‌گذرد، یک دلیل تازه برای دوست داشتن تو پیدا می‌کنم... ❤️",
    "زمان جلو می‌رود، اما قلب من هنوز همان‌جایی است که تو را پیدا کرد... 🌻",
    "ثانیه‌ها را می‌شود شمرد، اما عشق من به تو را نه... چون انتهایی ندارد. ❤️"
]

# ============================================================
# ======================== نامه‌ها =============================
# ============================================================

LOVE_LETTERS = [
    """
💌 نامه‌ای از دل من...

نسای من ❤️

گاهی فکر می‌کنم اگر قرار بود
تمام زیبایی‌های دنیا را
در یک نفر جمع کنند،
آخرش باز هم کم می‌آوردند...

چون تو برای من
فقط زیبایی نیستی؛
تو آرامش،
لبخند،
خاطره
و قشنگ‌ترین قسمت زندگی منی.

هر بار که به تو فکر می‌کنم،
دنیا کمی زیباتر می‌شود.

دوستت دارم...
نه فقط برای امروز،
بلکه برای تمام فرداهایی که
قرار است با خاطره‌های تو بسازم.

❤️🌻
""",
    """
💌 برای نسا...

اگر یک روز از من بپرسند
عشق یعنی چه؟

من جواب نمی‌دهم...

فقط لبخند می‌زنم
و تو را نشانشان می‌دهم.

چون بعضی احساس‌ها
قابل توضیح نیستند.

باید آن‌ها را زندگی کرد...

و من زیباترین قسمت زندگی‌ام را
با دوست داشتن تو پیدا کردم.

🌹❤️
""",
    """
💌 نسای من...

در میان تمام اتفاق‌هایی که
می‌توانست در زندگی‌ام بیفتد،
آشنایی با تو
یکی از قشنگ‌ترین‌هایشان بود.

از همان روزی که آمدی،
بعضی از لحظه‌های معمولی
دیگر معمولی نبودند.

چون تو در آن‌ها بودی.

❤️
هر روز بیشتر از دیروز...
""",
    """
💌 یک حرف از قلبم...

من تو را فقط در روزهای خوب نمی‌خواهم.

در روزهای خسته،
در روزهای سخت،
در سکوت‌ها،
در خنده‌ها،
در تمام لحظه‌های زندگی...

می‌خواهم کنارت باشم.

🌻
چون دوست داشتن واقعی
فقط گفتن «دوستت دارم» نیست؛
کنار هم ماندن است.

❤️
""",
    """
💌 نسا جان...

اگر زندگی یک کتاب باشد،
من دوست دارم
زیباترین فصل‌هایش
کنار تو نوشته شوند.

با خنده‌هایت،
با حرف‌هایت،
با خاطره‌هایت
و حتی با سکوت‌هایت.

تو یکی از قشنگ‌ترین
صفحه‌های زندگی منی.

❤️🌹
""",
    """
💌 از من برای تو...

گاهی یک نفر وارد زندگی آدم می‌شود
و بدون اینکه بفهمی چطور،
می‌شود بخشی از قلبت.

برای من،
آن آدم تویی نسا.

🌻
و اگر دوباره به گذشته برگردم،
باز هم دوست دارم
تو را پیدا کنم.

❤️
"""
]

# ============================================================
# ====================== کیبورد اصلی ==========================
# ============================================================

def get_main_keyboard():
    return {
        "keyboard": [
            ["🌻 شروع سورپرایز"],
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
            ["📸 عکس ۱", "📸 عکس ۲"],
            ["📸 عکس ۳", "📸 عکس ۴"],
            ["📸 عکس ۵", "📸 عکس ۶"],
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
# ======================= محاسبات =============================
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

def get_days_since_meet():
    start = datetime.datetime(1404, 12, 24, tzinfo=datetime.timezone(IRAN_OFFSET))
    now = get_current_iran_time()
    diff = now - start
    return diff.days

# ============================================================
# ====================== ارسال پیام ===========================
# ============================================================

def send_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        payload = {"chat_id": chat_id, "text": text}
        if reply_markup:
            payload["reply_markup"] = json.dumps(reply_markup, ensure_ascii=False)
        r = requests.post(url, data=payload, timeout=15)
        return r.status_code == 200
    except Exception as e:
        print("send_message error:", e)
        return False

# ============================================================
# ======================= ارسال عکس ===========================
# ============================================================

def send_photo(chat_id, photo_path, caption=""):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    try:
        if photo_path.startswith("http"):
            payload = {"chat_id": chat_id, "photo": photo_path, "caption": caption}
            r = requests.post(url, data=payload, timeout=20)
            return r.status_code == 200
        if not os.path.exists(photo_path):
            send_message(chat_id, "❌ عکس پیدا نشد!")
            return False
        with open(photo_path, "rb") as f:
            files = {"photo": f}
            data = {"chat_id": chat_id, "caption": caption}
            r = requests.post(url, data=data, files=files, timeout=20)
        return r.status_code == 200
    except Exception as e:
        print("send_photo error:", e)
        return False

# ============================================================
# ==================== پردازش پیام‌ها =========================
# ============================================================

user_access = {}

def handle_message(chat_id, text):
    text = text.strip()
    chat_id = str(chat_id)

    # ===== پسورد عکس‌ها =====
    if user_access.get(chat_id, {}).get("waiting_for_password"):
        if text == PASSWORD:
            user_access[chat_id]["photos"] = True
            user_access[chat_id]["waiting_for_password"] = False
            send_message(
                chat_id,
                "🌻 دسترسی باز شد!\nحالا می‌تونی عکس‌های مخصوص رو ببینی ❤️",
                get_photo_keyboard()
            )
        else:
            send_message(
                chat_id,
                "❌ پسورد اشتباهه عزیزم...\nدوباره امتحان کن 🔐",
                get_password_keyboard()
            )
        return

    # ===== عکس‌ها =====
    if text in PHOTOS:
        if user_access.get(chat_id, {}).get("photos", False):
            photo = PHOTOS[text]
            send_photo(chat_id, photo["path"], photo["caption"])
        else:
            send_message(
                chat_id,
                "🔐 این قسمت مخصوصه...\nبرای دیدن عکس‌ها رمز مخصوص رو وارد کن ❤️",
                get_password_keyboard()
            )
        return

    # ===== منوی عکس =====
    if text == "📸 عکس‌ها":
        if user_access.get(chat_id, {}).get("photos", False):
            send_message(chat_id, "🌹 کدوم عکس رو می‌خوای ببینی؟", get_photo_keyboard())
        else:
            user_access[chat_id] = {"photos": False, "waiting_for_password": True}
            send_message(
                chat_id,
                "🔐 قسمت خصوصی!\nرمز مخصوص رو وارد کن:",
                get_password_keyboard()
            )
        return

    # ===== سورپرایز =====
    if text == "🌻 شروع سورپرایز":
        send_message(
            chat_id,
            "🎁 یک سورپرایز مخصوص برای تو آماده شده...\n\n🌻 پر از گل\n❤️ پر از عشق\n✨ پر از خاطره\n\n👇 این صفحه رو باز کن:\nhttps://nesa-bot.onrender.com/welcome"
        )
        return

    # ===== تولد =====
    if text == "🎂 تولد نسا":
        send_message(chat_id, BIRTHDAY_MESSAGE)
        return

    # ===== روز آشنایی =====
    if text == "📅 روز آشنایی":
        days = get_days_since_meet()
        seconds = days * 24 * 60 * 60
        quote = random.choice(SECOND_QUOTES)
        send_message(
            chat_id,
            f"""
💞 روز آشنایی ما ❤️

📅 ۲۴ اسفند ۱۴۰۴

🌻 تا امروز، دقیقاً:

✨ {days:,} روز
⏱️ {seconds:,} ثانیه

از آن روز تا امروز،
{seconds:,} ثانیه گذشته...

و در تمام این ثانیه‌ها،
یک جمله در قلب من زنده بوده:

❤️ قلبم برای تو می‌تپد.

نه فقط در روزهای خوب،
بلکه در تمام لحظه‌ها...

🌹 هر ثانیه‌ای که گذشت،
یک خاطره با تو ساخت.

📖 {quote}

❤️ و اگر دوباره به همان روز برگردم،
باز هم تو را انتخاب می‌کنم.
""".replace(",", "٬")
        )
        return

    # ===== ساعت تا تولد =====
    if text == "⏳ ساعت تا تولدت":
        hours = hours_until_birthday()
        send_message(
            chat_id,
            f"""
🎂 شمارش معکوس تولد عشقم...

⏳ {hours:,} ساعت تا تولدت باقی مانده ❤️

🌻 هرچه زمان نزدیک‌تر می‌شود،
دل من برای دیدن لبخندت بیشتر ذوق می‌کند.

🎁 تولدت مبارک، حتی قبل از رسیدنش...
❤️
""".replace(",", "٬")
        )
        return

    # ===== نامه عشق =====
    if text == "💌 نامه عشق":
        send_message(chat_id, random.choice(LOVE_LETTERS))
        return

    # ===== صفحه عشق =====
    if text == "❤️ صفحه عشق":
        send_message(
            chat_id,
            """
❤️ صفحه‌ای که برای تو ساخته شده...

🌹 چهره‌ات با کلمات
«I LOVE YOU NESA»
ساخته می‌شود.

👇 بازش کن:

https://nesa-bot.onrender.com/love
"""
        )
        return

    # ===== صفحه تبریک =====
    if text == "🎉 تبریک برای عشقم":
        send_message(
            chat_id,
            """
🎉 یک تبریک مخصوص برای عشقم آماده شده...

🌻👇 بازش کن:

https://nesa-bot.onrender.com/birthday_surprise.html
"""
        )
        return

    # ===== آموزش سه تار =====
    if text == "🎸 آموزش سه تار":
        send_message(
            chat_id,
            f"""
🎸 آموزش سه تار

برای ورود به آموزش و دریافت فایل:

👇
{SETAR_LINK}

🎵 امیدوارم از یادگیری سه تار لذت ببری ❤️
"""
        )
        return

    # ===== بازگشت =====
    if text == "🔙 بازگشت به منو":
        old_access = user_access.get(chat_id, {}).get("photos", False)
        user_access[chat_id] = {"photos": old_access, "waiting_for_password": False}
        send_message(
            chat_id,
            "🏠 برگشتی به خانه ❤️\n\n🌻 منوی اصلی آماده است...",
            get_main_keyboard()
        )
        return

    # ===== استارت =====
    if text == "/start":
        user_access[chat_id] = {"photos": False, "waiting_for_password": False}
        send_message(
            chat_id,
            """
🌻❤️ به دنیای ahu goozlum خوش آمدی ❤️🌻

اینجا همه‌چیز برای یک نفر ساخته شده...

🌹 برای کسی که دوستش دارم
🌻 برای کسی که لبخندش قشنگ‌ترین اتفاق دنیاست
❤️ برای نسا...

🎁 یک سورپرایز مخصوص هم آماده کردم:

https://nesa-bot.onrender.com/welcome

👇 از منوی پایین انتخاب کن.
""",
            get_main_keyboard()
        )
        return

    # ===== دستور نامعتبر =====
    send_message(
        chat_id,
        "🌻 این گزینه رو پیدا نکردم...\nاز دکمه‌های منو استفاده کن ❤️",
        get_main_keyboard()
    )

# ============================================================
# ====================== تایمر تولد ===========================
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
                    photo = PHOTOS["📸 عکس ۱"]
                    if os.path.exists(photo["path"]):
                        send_photo(YOUR_CHAT_ID, photo["path"], photo["caption"])
                    sent_today = True
            else:
                sent_today = False
        except Exception as e:
            print("Birthday timer error:", e)
        time.sleep(30)

# ============================================================
# ====================== صفحه ۴۰۴ =============================
# ============================================================

@app.errorhandler(404)
def page_not_found(e):
    return """
    <html>
    <head><title>❌ صفحه پیدا نشد</title></head>
    <body style="background:#0a0a0a;color:#ff6699;display:flex;justify-content:center;align-items:center;height:100vh;font-family:Tahoma;text-align:center;">
        <div>
            <h1 style="font-size:60px;">🌻</h1>
            <h2>صفحه‌ای که دنبالش بودی پیدا نشد...</h2>
            <p style="color:#ffb3b3;">❤️ اما هنوز عشق من به تو پیدا شدنی‌ست ❤️</p>
            <a href="/" style="color:#ffd54f;">برگشت به خانه</a>
        </div>
    </body>
    </html>
    """, 404

# ============================================================
# ========================= Webhook ===========================
# ============================================================

@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "POST":
        try:
            data = request.get_json()
            if data and "message" in data:
                chat_id = data["message"]["chat"]["id"]
                text = data["message"].get("text", "")
                handle_message(chat_id, text)
        except Exception as e:
            print("Webhook error:", e)
    return "OK", 200

# ============================================================
# ========================== صفحات =============================
# ============================================================

@app.route("/welcome")
def welcome():
    return render_template_string(WELCOME_PAGE)

@app.route("/love")
def love_page():
    return render_template_string(PHOTO_MOSAIC_PAGE)

@app.route("/birthday_surprise.html")
def birthday_surprise():
    return render_template_string(BIRTHDAY_SURPRISE_PAGE)

# ============================================================
# ========================== اجرا ==============================
# ============================================================

if __name__ == "__main__":
    print("🚀 ربات ahu goozlum روشن شد...")
    print("🌻 صفحه سورپرایز: https://nesa-bot.onrender.com/welcome")
    print("❤️ صفحه عشق: https://nesa-bot.onrender.com/love")
    print("🎂 صفحه تولد: https://nesa-bot.onrender.com/birthday_surprise.html")
    print("🎸 آموزش سه تار:", SETAR_LINK)

    timer_thread = threading.Thread(target=birthday_timer, daemon=True)
    timer_thread.start()

    app.run(host="0.0.0.0", port=10000, debug=False)
