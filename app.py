from flask import Flask, request, jsonify
import requests, json, random, datetime, os, threading, time, sqlite3

app = Flask(__name__)

TOKEN = os.environ.get("BOT_TOKEN", "")
OWNER_CHAT_ID = "7989818498"
PARTNER_CHAT_ID = "7706282234"
CHANNEL_ID = "-1004499565151"
CHANNEL_NAME = "Nafas❤️Atashi"
PASSWORD = "1386"
WEBSITE_URL = "https://nesa-bot.onrender.com"

IRAN_TZ = datetime.timezone(datetime.timedelta(hours=3, minutes=30))
BIRTH_DAY, BIRTH_MONTH = 8, 8
MEETING_DATE = datetime.datetime(2026, 3, 15, tzinfo=IRAN_TZ)
DB_PATH = os.environ.get("QUEUE_DB", "channel_queue.db")
POST_INTERVAL_SECONDS = 3

user_access, PARTNER_ACTIVITY = {}, {}
BOT_ACTIVE = True

PHOTOS = {
"📸 عکس ۱": {"path":"photos/IMG_20260801_224828_501.jpg","caption":"🌹 عشق زندگیم... ❤️"},
"📸 عکس ۲": {"path":"photos/null_14041109_222510829.jpg","caption":"💫 قلب من... تو هستی"},
"📸 عکس ۳": {"path":"photos/null_14041125_153021650.jpg","caption":"🌸 بهار زندگی من..."},
"📸 عکس ۴": {"path":"photos/IMG_20260707_153249_974.jpg","caption":"🌙 ماه شب‌های من..."},
"📸 عکس ۵": {"path":"photos/IMG_20260709_234307_968.jpg","caption":"☀️ روشن‌ترین روز من..."},
"📸 عکس ۶": {"path":"photos/IMG_20260719_211523_837.jpg","caption":"❤️ تمام دنیای من..."},
"📸 عکس ۷": {"path":"https://i.postimg.cc/5tDhyRgM/IMG-20260318-184739-714.jpg","caption":"💖 عکس مخصوص... ❤️"},
"📸 عکس جدید": {"path":"photos/file_00000000f1788210bc5e8d993e16a277.png","caption":"🌹 این عکس مخصوص توست... ❤️"}
}

def now_iran():
    return datetime.datetime.now(datetime.timezone.utc).astimezone(IRAN_TZ)

def db():
    c = sqlite3.connect(DB_PATH, timeout=30)
    c.row_factory = sqlite3.Row
    c.execute("""CREATE TABLE IF NOT EXISTS queue(
        id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL,
        content TEXT NOT NULL, caption TEXT DEFAULT '', title TEXT DEFAULT '',
        performer TEXT DEFAULT '', created_at TEXT NOT NULL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS settings(
        key TEXT PRIMARY KEY, value TEXT NOT NULL)""")
    c.commit()
    return c

def setting(key, default=""):
    with db() as c:
        r = c.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return r["value"] if r else default

def set_setting(key, value):
    with db() as c:
        c.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)",
                  (key, str(value)))
        c.commit()

def post_time():
    try:
        h, m = setting("post_time", "10:10").split(":")
        return int(h), int(m)
    except Exception:
        return 10, 10

def add_queue(kind, content, caption="", title="", performer=""):
    with db() as c:
        c.execute("""INSERT INTO queue(kind,content,caption,title,performer,created_at)
                     VALUES(?,?,?,?,?,?)""",
                  (kind, content, caption, title, performer, now_iran().isoformat()))
        c.commit()

def queue_counts():
    with db() as c:
        rows = c.execute("SELECT kind,COUNT(*) n FROM queue GROUP BY kind").fetchall()
    out = {"text":0, "audio":0, "video":0}
    for r in rows: out[r["kind"]] = r["n"]
    return out

def pop_kind(kind):
    with db() as c:
        r = c.execute("SELECT * FROM queue WHERE kind=? ORDER BY id LIMIT 1",
                      (kind,)).fetchone()
        return dict(r) if r else None

def delete_item(item_id):
    with db() as c:
        c.execute("DELETE FROM queue WHERE id=?", (item_id,))
        c.commit()

def clear_kind(kind=None):
    with db() as c:
        if kind: c.execute("DELETE FROM queue WHERE kind=?", (kind,))
        else: c.execute("DELETE FROM queue")
        c.commit()

def api(method, **kwargs):
    if not TOKEN:
        print("BOT_TOKEN تنظیم نشده است.")
        return False, {}
    try:
        r = requests.post(f"https://api.telegram.org/bot{TOKEN}/{method}",
                          data=kwargs, timeout=120)
        data = r.json()
        return r.status_code == 200 and data.get("ok", False), data
    except Exception as e:
        print(method, e)
        return False, {}

def send_message(chat_id, text, keyboard=None, protect_content=False):
    data = {"chat_id":chat_id, "text":text,
            "protect_content":str(protect_content).lower()}
    if keyboard: data["reply_markup"] = json.dumps(keyboard, ensure_ascii=False)
    return api("sendMessage", **data)[0]

def send_media(method, chat_id, field, value, caption="", title="", performer="",
               protect_content=False):
    data = {"chat_id":chat_id, field:value, "caption":caption,
            "protect_content":str(protect_content).lower()}
    if method == "sendAudio":
        if title: data["title"] = title
        if performer: data["performer"] = performer
    return api(method, **data)[0]

def send_photo(chat_id, value, caption="", protect_content=False):
    return send_media("sendPhoto", chat_id, "photo", value, caption,
                      protect_content=protect_content)

def send_video(chat_id, value, caption="", protect_content=False):
    return send_media("sendVideo", chat_id, "video", value, caption,
                      protect_content=protect_content)

def send_audio(chat_id, value, caption="", title="", performer="❤️",
               protect_content=False):
    return send_media("sendAudio", chat_id, "audio", value, caption, title,
                      performer, protect_content)

def send_file_to_chat(target, f, protect=False):
    t, fid = f["type"], f.get("file_id")
    if not fid: return False
    value = "file_id:" + fid
    if t == "photo": return send_photo(target, value, f.get("caption",""), protect)
    if t == "video": return send_video(target, value, f.get("caption",""), protect)
    if t == "audio": return send_audio(target, value, f.get("caption",""),
                                       f.get("title","🎵"), f.get("performer","❤️"), protect)
    if t == "voice": return api("sendVoice", chat_id=target, voice=value,
                                 caption=f.get("caption",""),
                                 protect_content=str(protect).lower())[0]
    if t == "document": return api("sendDocument", chat_id=target, document=value,
                                    caption=f.get("caption",""),
                                    protect_content=str(protect).lower())[0]
    return False

def main_keyboard(cid):
    k = [["📸 عکس‌ها"],["📅 روز آشنایی","⏳ ساعت تا تولدت"],["💬 چت دوطرفه"]]
    if str(cid) == OWNER_CHAT_ID: k += [["📊 وضعیت پارتنر"],["📢 مدیریت کانال"]]
    k += [["🔙 بازگشت به منو"]]
    return {"keyboard":k,"resize_keyboard":True}

def photo_keyboard():
    return {"keyboard":[["📸 عکس ۱","📸 عکس ۲","📸 عکس ۳"],
                        ["📸 عکس ۴","📸 عکس ۵","📸 عکس ۶"],
                        ["📸 عکس ۷","📸 عکس جدید"],["🔙 بازگشت به منو"]],
            "resize_keyboard":True}

def chat_keyboard():
    return {"keyboard":[["📤 ارسال پیام"],["📤 ارسال عکس","📤 ارسال فیلم"],
                        ["📤 ارسال موزیک"],["🔙 بازگشت به منو"]],
            "resize_keyboard":True}

def channel_keyboard():
    return {"keyboard":[["✍️ افزودن متن کانال"],
                        ["🎵 افزودن آهنگ کانال","🎥 افزودن کلیپ کانال"],
                        ["📊 وضعیت صف کانال","🗑 پاک کردن صف کانال"],
                        ["⚡ ارسال فوری کانال","⏰ تنظیم ساعت کانال"],
                        ["🔙 بازگشت به منو"]],"resize_keyboard":True}

def log_activity(cid, action, chat):
    cid = str(cid)
    if cid == OWNER_CHAT_ID: return
    d = PARTNER_ACTIVITY.setdefault(cid, {"count":0,"first_seen":now_iran(),
        "first_name":"","last_name":"","username":"","last_seen":now_iran(),"last_action":""})
    for k in ("first_name","last_name","username"):
        if chat.get(k): d[k] = chat[k]
    d.update(last_seen=now_iran(), last_action=action)
    d["count"] += 1
    send_message(OWNER_CHAT_ID, f"👀 تعامل جدید\n👤 {d.get('first_name') or 'نامشخص'}\n"
                f"🆔 {cid}\n📌 {action}\n🔢 {d['count']}")

def get_access(cid):
    return user_access.setdefault(str(cid), {"photos":False,"waiting":None,
        "mode":None,"target":None})

def meeting_text():
    sec=max(0,int((now_iran()-MEETING_DATE).total_seconds()))
    return f"💞 روز آشنایی ما ❤️\n📅 ۲۴ اسفند ۱۴۰۴\n\n🌻 {sec//86400:,} روز\n⏱️ {sec:,} ثانیه\n\nهر ثانیه با تو یک خاطره است. ❤️"

def handle(cid, text, f=None):
    cid=str(cid); text=(text or "").strip(); u=get_access(cid)
    if not BOT_ACTIVE and cid != OWNER_CHAT_ID:
        return send_message(cid,"🔒 ربات غیرفعال شده است.")
    if text == "/start":
        user_access[cid]={"photos":False,"waiting":None,"mode":None,"target":None}
        return send_message(cid,"🌻❤️ به دنیای ahu goozlum خوش اومدی ❤️🌻",main_keyboard(cid))
    if text=="🔙 بازگشت به منو":
        u.update(waiting=None,mode=None,target=None)
        return send_message(cid,"🏠 منوی اصلی",main_keyboard(cid))

    if cid==OWNER_CHAT_ID and text=="📢 مدیریت کانال":
        u.update(mode="channel",waiting=None)
        return send_message(cid,f"📢 مدیریت {CHANNEL_NAME}\n⏰ ساعت فعلی: {setting('post_time','10:10')}",
                            channel_keyboard())
    if cid==OWNER_CHAT_ID and u.get("mode")=="channel":
        return handle_channel(cid,text,f,u)

    if text=="💬 چت دوطرفه":
        if cid not in (OWNER_CHAT_ID,PARTNER_CHAT_ID):
            return send_message(cid,"❌ دسترسی ندارید.",main_keyboard(cid))
        u.update(mode="chat",waiting=None,target="partner")
        return send_message(cid,"💬 پیام، عکس، فیلم، موزیک، فایل یا ویس را ارسال کن.",chat_keyboard())
    if u.get("mode")=="chat":
        if text=="📤 ارسال پیام":
            u["waiting"]="chat_text"; return send_message(cid,"💬 پیام را بنویس:",chat_keyboard())
        if text=="📤 ارسال عکس":
            u["waiting"]="photo"; return send_message(cid,"📸 عکس را بفرست:",chat_keyboard())
        if text=="📤 ارسال فیلم":
            u["waiting"]="video"; return send_message(cid,"🎥 فیلم را بفرست:",chat_keyboard())
        if text=="📤 ارسال موزیک":
            u["waiting"]="audio"; return send_message(cid,"🎵 MP3 یا فایل صوتی را بفرست:",chat_keyboard())
        if f:
            target=PARTNER_CHAT_ID if cid==OWNER_CHAT_ID else OWNER_CHAT_ID
            ok=send_file_to_chat(target,f,cid==OWNER_CHAT_ID and target==PARTNER_CHAT_ID)
            u["waiting"]=None
            return send_message(cid,"✅ ارسال شد ❤️" if ok else "❌ ارسال ناموفق بود.",chat_keyboard())
        if u.get("waiting")=="chat_text" and text:
            target=PARTNER_CHAT_ID if cid==OWNER_CHAT_ID else OWNER_CHAT_ID
            ok=send_message(target,f"💬 پیام از {'عشقت' if cid==OWNER_CHAT_ID else 'پارتنرت'}:\n\n{text}")
            u["waiting"]=None
            return send_message(cid,"✅ پیام ارسال شد ❤️" if ok else "❌ ارسال ناموفق بود.",chat_keyboard())

    if text=="📸 عکس‌ها":
        if not u["photos"]: u["waiting"]="password"; return send_message(cid,"🔐 رمز را وارد کن.")
        return send_message(cid,"📸 عکس را انتخاب کن:",photo_keyboard())
    if u.get("waiting")=="password":
        if text==PASSWORD: u.update(photos=True,waiting=None); return send_message(cid,"🔓 گالری باز شد ❤️",photo_keyboard())
        return send_message(cid,"❌ رمز اشتباه است.")
    if text in PHOTOS:
        if not u["photos"]: u["waiting"]="password"; return send_message(cid,"🔐 رمز را وارد کن.")
        p=PHOTOS[text]; return send_photo(cid,p["path"],p["caption"])
    if text=="📅 روز آشنایی": return send_message(cid,meeting_text())
    if text=="⏳ ساعت تا تولدت":
        n=now_iran(); b=datetime.datetime(n.year,8,8,tzinfo=IRAN_TZ)
        if n>=b: b=b.replace(year=n.year+1)
        return send_message(cid,f"🎂 تا تولدت {int((b-n).total_seconds()//3600):,} ساعت مانده ❤️")
    if text=="📊 وضعیت پارتنر" and cid==OWNER_CHAT_ID:
        d=PARTNER_ACTIVITY.get(PARTNER_CHAT_ID)
        return send_message(cid,"❌ هنوز تعاملی ثبت نشده." if not d else
            f"📊 وضعیت پارتنر\n🆔 {PARTNER_CHAT_ID}\n🔢 {d['count']}\n"
            f"📅 آخرین تعامل: {d['last_seen'].strftime('%Y/%m/%d %H:%M:%S')}")
    return send_message(cid,"❌ دستور ناشناخته است.",main_keyboard(cid))

def handle_channel(cid,text,f,u):
    if text=="✍️ افزودن متن کانال":
        u["waiting"]="channel_text"; return send_message(cid,"✍️ متن را بفرست:",channel_keyboard())
    if text=="🎵 افزودن آهنگ کانال":
        u["waiting"]="channel_audio"; return send_message(cid,"🎵 آهنگ یا MP3 را بفرست:",channel_keyboard())
    if text=="🎥 افزودن کلیپ کانال":
        u["waiting"]="channel_video"; return send_message(cid,"🎥 کلیپ را بفرست:",channel_keyboard())
    if text=="📊 وضعیت صف کانال":
        c=queue_counts(); h,m=post_time()
        return send_message(cid,f"📊 صف کانال\n✍️ متن: {c['text']}\n🎵 آهنگ: {c['audio']}\n🎥 کلیپ: {c['video']}\n⏰ ساعت: {h:02d}:{m:02d}",channel_keyboard())
    if text=="🗑 پاک کردن صف کانال":
        clear_kind(); return send_message(cid,"🗑 کل صف پاک شد.",channel_keyboard())
    if text=="⏰ تنظیم ساعت کانال":
        u["waiting"]="channel_time"; return send_message(cid,"⏰ ساعت را مثل 14:30 بفرست:",channel_keyboard())
    if text=="⚡ ارسال فوری کانال":
        u["waiting"]="channel_now"; return send_message(cid,"⚡ متن، آهنگ یا کلیپ را بفرست:",channel_keyboard())
    w=u.get("waiting")
    if w=="channel_time":
        try:
            h,m=map(int,text.split(":"))
            if not(0<=h<=23 and 0<=m<=59): raise ValueError
            set_setting("post_time",f"{h:02d}:{m:02d}"); u["waiting"]=None
            return send_message(cid,f"✅ ساعت روی {h:02d}:{m:02d} تنظیم شد.",channel_keyboard())
        except: return send_message(cid,"❌ قالب نادرست است؛ نمونه: 14:30")
    if w=="channel_text" and text:
        add_queue("text",text); u["waiting"]=None
        return send_message(cid,"✅ متن به صف اضافه شد.",channel_keyboard())
    if f and w in ("channel_audio","channel_video","channel_now"):
        kind=f["type"]
        if kind not in ("audio","video"):
            return send_message(cid,"❌ برای این بخش فقط آهنگ یا ویدیو بفرست.")
        if w=="channel_now":
            ok=send_audio(cid if False else CHANNEL_ID,"file_id:"+f["file_id"],f.get("caption",""),
                          f.get("title","🎵"),f.get("performer","❤️")) if kind=="audio" else send_video(CHANNEL_ID,"file_id:"+f["file_id"],f.get("caption",""))
            u["waiting"]=None
            return send_message(cid,"✅ فوری در کانال منتشر شد." if ok else "❌ انتشار ناموفق بود.",channel_keyboard())
        add_queue(kind,f["file_id"],f.get("caption",""),f.get("title","🎵"),f.get("performer","❤️"))
        u["waiting"]=None
        return send_message(cid,"✅ به صف اضافه شد.",channel_keyboard())
    if w=="channel_audio" and f and f["type"]=="document": pass
    return send_message(cid,"از دکمه‌های مدیریت کانال استفاده کن.",channel_keyboard())

def publish_daily():
    h,m=post_time(); sent=False
    for kind in ("text","audio","video"):
        item=pop_kind(kind)
        if not item: continue
        if kind=="text": ok=send_message(CHANNEL_ID,item["content"])
        elif kind=="audio": ok=send_audio(CHANNEL_ID,"file_id:"+item["content"],item["caption"],item["title"],item["performer"])
        else: ok=send_video(CHANNEL_ID,"file_id:"+item["content"],item["caption"])
        if ok: delete_item(item["id"]); sent=True
        time.sleep(POST_INTERVAL_SECONDS)
    return sent

def scheduler():
    db().close()
    last=setting("last_post_date","")
    while True:
        try:
            n=now_iran(); h,m=post_time(); today=n.strftime("%Y-%m-%d")
            if n.hour==h and n.minute==m and last!=today:
                publish_daily(); set_setting("last_post_date",today); last=today
        except Exception as e: print("scheduler:",e)
        time.sleep(20)

@app.route("/",methods=["GET","POST"])
def webhook():
    if request.method=="POST":
        try:
            d=request.get_json(silent=True) or {}
            msg=d.get("message")
            if msg:
                chat=msg.get("chat",{}); cid=str(chat.get("id"))
                text=msg.get("text",""); caption=msg.get("caption",""); f=None
                if msg.get("photo"):
                    f={"type":"photo","file_id":msg["photo"][-1]["file_id"],"caption":caption}
                elif msg.get("video"):
                    f={"type":"video","file_id":msg["video"]["file_id"],"caption":caption}
                elif msg.get("audio"):
                    a=msg["audio"]; f={"type":"audio","file_id":a["file_id"],"caption":caption,
                        "title":a.get("title","🎵"),"performer":a.get("performer","❤️")}
                elif msg.get("voice"):
                    f={"type":"voice","file_id":msg["voice"]["file_id"],"caption":caption}
                elif msg.get("document"):
                    x=msg["document"]; name=x.get("file_name","").lower(); mime=x.get("mime_type","")
                    typ="audio" if mime.startswith("audio/") or name.endswith((".mp3",".m4a",".wav",".ogg",".flac")) else "video" if mime.startswith("video/") or name.endswith((".mp4",".mov",".mkv",".webm")) else "document"
                    f={"type":typ,"file_id":x["file_id"],"caption":caption,"title":name or "🎵","performer":"❤️"}
                action=text or ("📎 فایل ارسال کرد" if f else "Update")
                log_activity(cid,action,chat); handle(cid,text,f)
        except Exception as e: print("webhook:",e)
    return "OK",200

@app.route("/health")
def health():
    return jsonify(status="ok", channel=CHANNEL_ID, post_time=setting("post_time","10:10"),
                   queue=queue_counts())

if __name__=="__main__":
    set_setting("post_time",setting("post_time","10:10"))
    threading.Thread(target=scheduler,daemon=True).start()
    print("🚀 ربات روشن شد؛ کانال:",CHANNEL_ID)
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
