# -*- coding: utf-8 -*-
import os, sys, time, socket, subprocess, json, uuid, csv
import streamlit as st


def _backend_up():
    s = socket.socket(); s.settimeout(0.5)
    try:
        s.connect(("127.0.0.1", 8000)); return True
    except OSError:
        return False
    finally:
        s.close()


@st.cache_resource
def start_backend():
    if _backend_up():
        return True
    here = os.path.dirname(os.path.abspath(__file__))
    subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
                     cwd=os.path.join(here, "sehatsathi", "backend"))
    for _ in range(40):
        if _backend_up():
            return True
        time.sleep(1)
    return False


start_backend()

import io, datetime, html as _h, requests
from ui_parts import hero_html, result_html, result_height, care_html, care_height, report_html

API_URL = "http://127.0.0.1:8000/triage"
HERE = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(HERE, "patients.json")

st.set_page_config(page_title="صحت ساتھی SehatSathi", page_icon="🩺", layout="wide", initial_sidebar_state="expanded")

# ================================================================ storage (patients.json)
def load_db():
    try:
        with open(DB_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_db(db):
    tmp = DB_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=1)
    os.replace(tmp, DB_FILE)


# ================================================================ text
TR = {
    "ur": {
        "pages": {"dashboard": "🏠 ڈیش بورڈ", "check": "🩺 نیا معائنہ", "records": "📂 مریضوں کا ریکارڈ"},
        "enter": "🚀 داخل ہوں", "back": "⬅️ ہوم", "lang": "زبان / Language",
        "hello": "خوش آمدید 👋", "hello_s": "آج کتنے مریضوں کو صحیح فیصلہ دینا ہے؟",
        "s_pat": "کل مریض", "s_vis": "کل معائنے", "s_em": "ہنگامی کیسز", "s_td": "آج کے معائنے",
        "dist": "📊 نتائج کی تقسیم", "recent": "🕘 حالیہ معائنے", "none": "ابھی کوئی ریکارڈ نہیں۔ پہلا معائنہ شروع کریں!",
        "q_new": "➕ نیا معائنہ شروع کریں", "q_rec": "📂 ریکارڈ دیکھیں",
        "who": "👤 مریض", "new_p": "➕ نیا مریض", "name": "نام *", "age": "عمر", "age_ph": "مثال: 2 سال",
        "gender": "جنس", "phone": "فون نمبر", "city": "شہر / گاؤں", "blood": "بلڈ گروپ",
        "allergy": "الرجی (اگر ہو)", "chronic": "پرانی بیماری (شوگر، بی پی...)",
        "need_name": "مریض کا نام ضروری ہے۔", "saved_p": "مریض محفوظ ہو گیا ✅",
        "tap": "**👆 عام علامات پر ٹچ کریں**", "symp": "علامات",
        "speak": "**🎤 یا بول کر بتائیں** (اردو)", "mic": "بولنے کے لیے مائیک دبائیں",
        "type": "✍️ یا خود لکھیں (اردو، رومن اردو یا انگریزی)", "type_ph": "مثال: تین دن سے تیز بخار اور دست",
        "check": "🔍 چیک کریں", "enter_s": "پہلے علامات لکھیں یا اوپر سے چنیں۔",
        "listen": "🔊 نتیجہ آواز میں سنیں", "more": "🩺 مزید سوالات",
        "more_cap": "AI کچھ باتیں پوچھ رہا ہے۔ جواب لکھیں اور دوبارہ چیک کریں۔",
        "yn": "جی ہاں / نہیں / تفصیل", "again": "✅ جوابات کے ساتھ دوبارہ چیک کریں",
        "tech": "🔬 تکنیکی تفصیل", "dl": "📄 پرچی ڈاؤن لوڈ کریں", "spin": "جائزہ لیا جا رہا ہے...",
        "emerg": "ہنگامی حالت! فوراً ہسپتال لے جائیں", "noserver": "سرور سے رابطہ نہیں ہو سکا۔",
        "writing": "آواز کو لکھا جا رہا ہے...", "pip_sr": "pip install SpeechRecognition",
        "no_hear": "آواز سمجھ نہیں آئی۔ دوبارہ بولیں یا لکھ دیں۔", "making": "آواز تیار ہو رہی ہے...",
        "pip_tts": "pip install gTTS", "need_net": "آواز کے لیے انٹرنیٹ چاہیے۔",
        "ai_off": "ℹ️ AI بند ہے۔ رولز، ML ماڈل اور ہوم کیئر انجن کام کر رہے ہیں۔",
        "foot": "⚠️ یہ تجرباتی نمونہ ہے، طبی تصدیق نہیں ہوئی۔ صرف فرضی ڈیٹا استعمال کریں۔",
        "male": "لڑکا / مرد", "female": "لڑکی / عورت", "search": "🔎 نام، فون یا شہر سے تلاش کریں",
        "visits": "معائنے", "last": "آخری", "del": "🗑️ مریض حذف کریں", "again_p": "➕ اس مریض کا نیا معائنہ",
        "csv": "⬇️ تمام ریکارڈ CSV", "no_vis": "کوئی معائنہ نہیں", "info": "معلومات",
        "note": "پرانی بیماری", "alg": "الرجی",
    },
    "en": {
        "pages": {"dashboard": "🏠 Dashboard", "check": "🩺 New check", "records": "📂 Patient records"},
        "enter": "🚀 Enter", "back": "⬅️ Home", "lang": "زبان / Language",
        "hello": "Welcome 👋", "hello_s": "Who needs the right decision today?",
        "s_pat": "Patients", "s_vis": "Total checks", "s_em": "Emergencies", "s_td": "Today",
        "dist": "📊 Outcome mix", "recent": "🕘 Recent checks", "none": "No records yet. Start the first check!",
        "q_new": "➕ Start new check", "q_rec": "📂 View records",
        "who": "👤 Patient", "new_p": "➕ New patient", "name": "Name *", "age": "Age", "age_ph": "e.g. 2 years",
        "gender": "Gender", "phone": "Phone", "city": "City / village", "blood": "Blood group",
        "allergy": "Allergies (if any)", "chronic": "Chronic illness (diabetes, BP...)",
        "need_name": "Patient name is required.", "saved_p": "Patient saved ✅",
        "tap": "**👆 Tap common symptoms**", "symp": "Symptoms",
        "speak": "**🎤 Or speak** (Urdu)", "mic": "Press the mic to speak",
        "type": "✍️ Or type (Urdu, Roman Urdu or English)", "type_ph": "e.g. high fever and diarrhea for 3 days",
        "check": "🔍 Check", "enter_s": "Please type symptoms or pick them above.",
        "listen": "🔊 Listen to the result", "more": "🩺 More questions",
        "more_cap": "The AI is asking a few things. Answer and check again.",
        "yn": "Yes / No / details", "again": "✅ Check again with answers",
        "tech": "🔬 Technical details", "dl": "📄 Download slip", "spin": "Assessing...",
        "emerg": "Emergency! Go to hospital immediately", "noserver": "Could not reach the server.",
        "writing": "Transcribing speech...", "pip_sr": "pip install SpeechRecognition",
        "no_hear": "Could not understand. Speak again or type it.", "making": "Preparing audio...",
        "pip_tts": "pip install gTTS", "need_net": "Internet is needed for audio.",
        "ai_off": "ℹ️ AI is off. Rules, ML model and home-care engine are still working.",
        "foot": "⚠️ Experimental prototype, not medically validated. Use fake data only.",
        "male": "Boy / Man", "female": "Girl / Woman", "search": "🔎 Search by name, phone or city",
        "visits": "visits", "last": "Last", "del": "🗑️ Delete patient", "again_p": "➕ New check for this patient",
        "csv": "⬇️ Export all as CSV", "no_vis": "No visits", "info": "Info",
        "note": "Chronic", "alg": "Allergy",
    },
}

QUICK = [
    ("fever", "🤒 تیز بخار", "🤒 High fever", "تیز بخار"), ("cold", "🤧 زکام / کھانسی", "🤧 Cold / cough", "زکام اور کھانسی"),
    ("vomit", "🤮 الٹی", "🤮 Vomiting", "بار بار الٹی"), ("diar", "💧 دست", "💧 Diarrhea", "دست"),
    ("head", "🤕 سر درد", "🤕 Headache", "سر درد"), ("breath", "😮‍💨 سانس کی تکلیف", "😮‍💨 Breathing trouble", "سانس نہیں آ رہی"),
    ("faint", "😵 بے ہوشی / جھٹکے", "😵 Fainting / fits", "بے ہوش اور جھٹکے"), ("bleed", "🩸 خون آنا", "🩸 Bleeding", "خون آ رہا ہے"),
    ("preg", "🤰 حمل", "🤰 Pregnancy", "حمل"), ("milk", "🍼 دودھ نہیں پی رہا", "🍼 Not feeding", "دودھ نہیں پی رہا"),
    ("poison", "☠️ زہر", "☠️ Poison", "زہر کھا لیا"),
]
QUICK_TEXT = {q[0]: q[3] for q in QUICK}
LEVEL_ICON = {"emergency": "🔴", "urgent": "🟠", "home": "🟢"}
LEVEL_COL = {"emergency": "#e53935", "urgent": "#fb8c00", "home": "#2e9e5b"}
PAGES = ["dashboard", "check", "records"]
esc = _h.escape


def render_html(html, height):
    try:
        import streamlit.components.v1 as components
        components.html(html, height=height)
    except Exception:
        st.markdown(html, unsafe_allow_html=True)


def transcribe_urdu(wav):
    import speech_recognition as sr
    rec = sr.Recognizer()
    with sr.AudioFile(io.BytesIO(wav)) as src:
        audio = rec.record(src)
    return rec.recognize_google(audio, language="ur-PK")


def speak(text, lang):
    from gtts import gTTS
    fp = io.BytesIO(); gTTS(text, lang=lang).write_to_fp(fp)
    return fp.getvalue()


# ================================================================ navigation
st.session_state.setdefault("pg", "welcome")


def go(p):
    st.session_state["pg"] = p
    st.session_state["nav_radio"] = p


def on_nav():
    st.session_state["pg"] = st.session_state["nav_radio"]


def new_patient():
    for k in ("result", "last_input", "cur_pid", "last_audio"):
        st.session_state.pop(k, None)
    st.session_state["typed"] = ""
    for k in [k for k in st.session_state if str(k).startswith("fu_")]:
        st.session_state.pop(k, None)


def check_for(pid):
    new_patient()
    st.session_state["sel_pid"] = pid
    go("check")


PG = st.session_state["pg"]

with st.sidebar:
    lang_label = st.radio("زبان / Language", ["اردو", "English"], horizontal=True, key="lang_choice")
    out_lang = "ur" if lang_label == "اردو" else "en"
    T = TR[out_lang]
    if PG != "welcome":
        st.markdown("### 🩺 SehatSathi")
        st.radio("nav", PAGES, index=PAGES.index(PG) if PG in PAGES else 0, key="nav_radio",
                 format_func=lambda p: T["pages"][p], on_change=on_nav, label_visibility="collapsed")
        st.button(T["back"], on_click=go, args=("welcome",), use_container_width=True)

RTL = out_lang == "ur"
DIR, ALIGN = ("rtl", "right") if RTL else ("ltr", "left")
HIDE_SB = "[data-testid='stSidebar'],[data-testid='stSidebarCollapsedControl']{display:none}" if PG == "welcome" else ""

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;600;700;800&display=swap');
html,body,[class*="css"],.stApp,textarea,input,button,label,p,h1,h2,h3,h4,li{font-family:'Noto Naskh Arabic','Jameel Noori Nastaleeq','Segoe UI',Tahoma,sans-serif!important}
.stApp{direction:__DIR__;text-align:__AL__;background:radial-gradient(circle at 8% 3%,rgba(20,184,166,.12),transparent 25rem),radial-gradient(circle at 95% 10%,rgba(37,99,235,.08),transparent 22rem),linear-gradient(180deg,#f3fbfb,#f8fafc 45%,#fff)}
header[data-testid="stHeader"]{background:transparent}
[data-testid="stMainBlockContainer"],[data-testid="stAppViewContainer"]>.main .block-container{max-width:1240px;padding:1.4rem clamp(1rem,3vw,2.5rem) 3rem;animation:pg .45s ease-out}
@keyframes pg{from{opacity:0;transform:translateX(__SLIDE__px)}to{opacity:1;transform:none}}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#063b3d,#0a5f61);}
[data-testid="stSidebar"] *{color:#e6fffb!important}
[data-testid="stSidebar"] button{color:#063b3d!important}
h1,h2,h3{letter-spacing:-.02em;color:#172b3a}
p,label,.stMarkdown{text-align:__AL__}
div[data-testid="stVerticalBlockBorderWrapper"]{border:1px solid rgba(148,163,184,.25);border-radius:22px;background:rgba(255,255,255,.9);box-shadow:0 8px 28px rgba(15,23,42,.05)}
textarea,input,[data-baseweb="select"]>div{direction:__DIR__;text-align:__AL__;border-radius:13px!important}
div.stButton>button,div.stDownloadButton>button,[data-testid="stFormSubmitButton"] button{min-height:46px;border-radius:14px;font-weight:700;border:1px solid #dbe7eb;transition:transform .18s,box-shadow .18s}
div.stButton>button[kind="primary"],[data-testid="stFormSubmitButton"] button{width:100%;min-height:54px;font-size:1.1rem;border:0;color:#fff;background:linear-gradient(115deg,#0f9f98,#2563eb);box-shadow:0 8px 20px rgba(37,99,235,.2)}
div.stButton>button:hover{transform:translateY(-2px);box-shadow:0 8px 18px rgba(15,23,42,.12)}
[data-testid="stPills"] button{border-radius:999px!important}
[data-testid="stAudioInput"]{padding:.8rem;border:1px dashed #9ccdc8;border-radius:16px;background:#f0fdfa}
[data-testid="stExpander"]{border:1px solid #e2e8f0;border-radius:16px;background:#fff}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;margin:6px 0 18px}
.stat{background:#fff;border-radius:22px;padding:18px 20px;border:1px solid #e2e8f0;box-shadow:0 8px 24px rgba(15,23,42,.05);position:relative;overflow:hidden}
.stat:before{content:'';position:absolute;top:0;bottom:0;__SIDE__:0;width:6px;background:var(--c)}
.stat b{display:block;font-size:38px;line-height:1.1;color:var(--c)}.stat span{color:#64748b;font-weight:600}
.pt{font-size:clamp(26px,3.5vw,38px);font-weight:800;margin:0}.sub{color:#64748b;margin:2px 0 14px}
.mix{display:flex;height:18px;border-radius:12px;overflow:hidden;background:#eef0f3;margin:10px 0 8px}
.lg{display:flex;gap:16px;flex-wrap:wrap;font-size:14px;color:#475569}.lg i{display:inline-block;width:11px;height:11px;border-radius:50%;margin-inline-end:6px}
.vr{display:flex;align-items:center;gap:12px;padding:11px 4px;border-bottom:1px solid #eef2f6}
.vr:last-child{border:0}.av{width:42px;height:42px;border-radius:14px;color:#fff;font-weight:800;display:grid;place-items:center;flex:0 0 42px}
.vr .t{font-weight:700;color:#172b3a}.vr .s{font-size:14px;color:#64748b}
.pill{margin-inline-start:auto;padding:4px 12px;border-radius:14px;font-weight:700;font-size:13px;color:#fff}
.pc{display:flex;gap:14px;align-items:center;padding:6px 2px}.pc .av{width:54px;height:54px;font-size:24px;border-radius:18px;background:linear-gradient(135deg,#0f9f98,#2563eb)}
.tags{display:flex;gap:8px;flex-wrap:wrap;margin-top:6px}.tg{background:#e0f2fe;color:#075985;border-radius:14px;padding:3px 12px;font-size:14px;font-weight:700}.tg.r{background:#fee2e2;color:#b91c1c}
@media(max-width:760px){[data-testid="column"]{min-width:100%!important;flex:1 1 100%!important}div.stButton>button{width:100%}}
@media(prefers-reduced-motion:reduce){*{animation:none!important}}
__HIDE__
</style>""".replace("__DIR__", DIR).replace("__AL__", ALIGN).replace("__SIDE__", "right" if RTL else "left")
            .replace("__SLIDE__", "-24" if RTL else "24").replace("__HIDE__", HIDE_SB), unsafe_allow_html=True)


# ================================================================ helpers
def initials(n):
    return (n.strip()[:1] or "?").upper()


def stats(db):
    vs = [(p, v) for p in db.values() for v in p.get("visits", [])]
    today = datetime.date.today().strftime("%d-%m-%Y")
    return {"pat": len(db), "vis": len(vs), "em": sum(v["level"] == "emergency" for _, v in vs),
            "td": sum(v["when"].startswith(today) for _, v in vs),
            "mix": {k: sum(v["level"] == k for _, v in vs) for k in LEVEL_COL}, "all": vs}


def visit_row(p, v):
    c = LEVEL_COL[v["level"]]
    return (f"<div class='vr'><div class='av' style='background:{c}'>{esc(initials(p['name']))}</div>"
            f"<div><div class='t'>{esc(p['name'])}</div><div class='s'>{esc(v['when'])} • {esc(v['symptoms'][:60])}</div></div>"
            f"<span class='pill' style='background:{c}'>{esc(v['title'])}</span></div>")


# ================================================================ PAGE: welcome
def landing_html():
    return f"""<!doctype html><html><head><meta charset='utf-8'>
<link href='https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;700;800&display=swap' rel='stylesheet'>
<style>*{{box-sizing:border-box}}body{{margin:0;font-family:'Noto Naskh Arabic','Segoe UI',sans-serif}}
.w{{position:relative;overflow:hidden;min-height:520px;border-radius:34px;color:#fff;padding:46px 38px;text-align:center;
background:radial-gradient(700px 360px at 80% 0,#2563eb88,transparent),radial-gradient(600px 380px at 10% 100%,#10b98166,transparent),#052f31}}
.o{{position:absolute;border-radius:50%;filter:blur(2px);background:#ffffff10;animation:f 9s ease-in-out infinite}}
@keyframes f{{50%{{transform:translateY(-26px)}}}}
.ecg{{position:absolute;left:0;right:0;top:50%;opacity:.22}}.ecg path{{stroke:#6ee7b7;stroke-width:2.5;fill:none;stroke-dasharray:900;stroke-dashoffset:900;animation:d 4s linear infinite}}
@keyframes d{{to{{stroke-dashoffset:-900}}}}
.in{{position:relative;z-index:1}}.lg{{font-size:64px;animation:b 2.4s ease-in-out infinite}}@keyframes b{{50%{{transform:scale(1.12)}}}}
h1{{font-size:clamp(44px,8vw,84px);margin:6px 0;font-weight:800;line-height:1.2}}
p{{font-size:clamp(17px,2.4vw,24px);color:#a7f3d0;margin:0 0 26px}}
.g{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;max-width:880px;margin:0 auto}}
.c{{background:#ffffff14;border:1px solid #ffffff2e;backdrop-filter:blur(8px);border-radius:22px;padding:18px 12px;font-weight:700}}
.c span{{display:block;font-size:34px;margin-bottom:6px}}.c small{{display:block;font-weight:400;color:#bbf7d0;margin-top:4px}}
</style></head><body><div class='w'>
<div class='o' style='width:220px;height:220px;left:-60px;top:-60px'></div><div class='o' style='width:140px;height:140px;right:8%;bottom:-40px;animation-delay:2s'></div>
<svg class='ecg' viewBox='0 0 800 80' preserveAspectRatio='none' height='90' width='100%'><path d='M0 40H150L170 40L185 8L205 72L222 40H420L440 40L455 14L475 66L492 40H800'/></svg>
<div class='in'><div class='lg'>🩺</div><h1>صحت ساتھی</h1><p>SehatSathi • صحیح وقت پر صحیح فیصلہ</p>
<div class='g'><div class='c'><span>🧠</span>AI + ML Triage<small>ہنگامی / جلد / گھر</small></div>
<div class='c'><span>🎤</span>Voice<small>بول کر علامات بتائیں</small></div>
<div class='c'><span>📂</span>Patient Records<small>ہر مریض کی ہسٹری</small></div>
<div class='c'><span>🚑</span>Rescue 1122<small>ایک ٹچ کال</small></div></div></div></div></body></html>"""


if PG == "welcome":
    render_html(landing_html(), 560)
    _, mid, _ = st.columns([1, 1.2, 1])
    mid.button(T["enter"], type="primary", on_click=go, args=("dashboard",))
    st.caption(T["foot"])
    st.stop()

db = load_db()

# ================================================================ PAGE: dashboard
if PG == "dashboard":
    S = stats(db)
    st.markdown(f"<p class='pt'>{T['hello']}</p><p class='sub'>{T['hello_s']}</p>", unsafe_allow_html=True)
    cards = [(T["s_pat"], S["pat"], "#2563eb"), (T["s_vis"], S["vis"], "#0f9f98"),
             (T["s_em"], S["em"], "#e53935"), (T["s_td"], S["td"], "#fb8c00")]
    st.markdown("<div class='stats'>" + "".join(f"<div class='stat' style='--c:{c}'><b>{n}</b><span>{l}</span></div>"
                                                for l, n, c in cards) + "</div>", unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    b1.button(T["q_new"], type="primary", on_click=check_for, args=("__new__",))
    b2.button(T["q_rec"], on_click=go, args=("records",), use_container_width=True)
    c1, c2 = st.columns([1, 1.4])
    with c1, st.container(border=True):
        st.markdown(f"#### {T['dist']}")
        tot = max(S["vis"], 1)
        names = {"emergency": TR[out_lang]["s_em"], "urgent": "🟠", "home": "🟢"}
        bar = "".join(f"<div style='width:{100 * S['mix'][k] / tot}%;background:{LEVEL_COL[k]}'></div>" for k in LEVEL_COL)
        lab = {"ur": {"emergency": "ہنگامی", "urgent": "جلد ڈاکٹر", "home": "گھر پر"},
               "en": {"emergency": "Emergency", "urgent": "Urgent", "home": "Home"}}[out_lang]
        lg = "".join(f"<span><i style='background:{LEVEL_COL[k]}'></i>{lab[k]}: {S['mix'][k]}</span>" for k in LEVEL_COL)
        st.markdown(f"<div class='mix'>{bar}</div><div class='lg'>{lg}</div>", unsafe_allow_html=True)
    with c2, st.container(border=True):
        st.markdown(f"#### {T['recent']}")
        rows = sorted(S["all"], key=lambda pv: pv[1]["ts"], reverse=True)[:6]
        st.markdown("".join(visit_row(p, v) for p, v in rows) if rows else f"<p class='sub'>{T['none']}</p>",
                    unsafe_allow_html=True)

# ================================================================ PAGE: records
elif PG == "records":
    st.markdown(f"<p class='pt'>{T['pages']['records']}</p>", unsafe_allow_html=True)
    q = st.text_input(T["search"], label_visibility="collapsed", placeholder=T["search"]).strip().lower()
    items = [(pid, p) for pid, p in db.items()
             if q in (p["name"] + p.get("phone", "") + p.get("city", "")).lower()]
    if not items:
        st.info(T["none"])
    for pid, p in sorted(items, key=lambda x: x[1].get("created", ""), reverse=True):
        vs = p.get("visits", [])
        last = LEVEL_ICON[vs[-1]["level"]] if vs else "⚪"
        with st.expander(f"{last} {p['name']} • {p.get('age') or '-'} • {len(vs)} {T['visits']}"):
            tags = "".join(f"<span class='tg'>{esc(x)}</span>" for x in [p.get("gender"), p.get("city"), p.get("phone"), p.get("blood")] if x)
            tags += "".join(f"<span class='tg r'>{T[k]}: {esc(p[f])}</span>" for k, f in [("alg", "allergy"), ("note", "chronic")] if p.get(f))
            st.markdown(f"<div class='pc'><div class='av'>{esc(initials(p['name']))}</div><div><b style='font-size:20px'>{esc(p['name'])}</b><div class='tags'>{tags}</div></div></div>", unsafe_allow_html=True)
            st.markdown("".join(visit_row(p, v) for v in reversed(vs)) or f"<p class='sub'>{T['no_vis']}</p>", unsafe_allow_html=True)
            a, b, c = st.columns(3)
            a.button(T["again_p"], key=f"ag_{pid}", on_click=check_for, args=(pid,), use_container_width=True)
            if vs and vs[-1].get("res"):
                v = vs[-1]
                b.download_button(T["dl"], report_html(v["res"], p.get("age", ""), p.get("gender", ""), v["symptoms"], v["when"]),
                                  file_name=f"parchi_{p['name']}.html", mime="text/html", key=f"dl_{pid}", use_container_width=True)
            if c.button(T["del"], key=f"rm_{pid}", use_container_width=True):
                db.pop(pid, None); save_db(db); st.rerun()
    if db:
        buf = io.StringIO(); w = csv.writer(buf)
        w.writerow(["name", "age", "gender", "phone", "city", "blood", "allergy", "chronic", "when", "symptoms", "level", "title"])
        for p in db.values():
            for v in p.get("visits", []):
                w.writerow([p["name"], p.get("age"), p.get("gender"), p.get("phone"), p.get("city"), p.get("blood"),
                            p.get("allergy"), p.get("chronic"), v["when"], v["symptoms"], v["level"], v["title"]])
        st.download_button(T["csv"], "\ufeff" + buf.getvalue(), file_name="sehatsathi_records.csv", mime="text/csv")

# ================================================================ PAGE: check
else:
    render_html(hero_html(), 255)

    def run_check(pid, age_, gender_, symptoms_, followup=None, record=True):
        try:
            with st.spinner(T["spin"]):
                r = requests.post(API_URL, json={"age": age_, "gender": gender_, "symptoms": symptoms_,
                                                 "output_language": out_lang, "followup": followup or []}, timeout=60)
                r.raise_for_status()
                res_ = r.json()
            st.session_state["result"] = res_
            st.session_state["last_input"] = (age_, gender_, symptoms_)
            if record and pid in db:
                now = datetime.datetime.now()
                db[pid].setdefault("visits", []).append({
                    "ts": now.timestamp(), "when": now.strftime("%d-%m-%Y %H:%M"), "symptoms": symptoms_,
                    "level": res_["triage_level"], "title": res_["title"], "res": res_})
                save_db(db)
            if res_["triage_level"] == "emergency":
                st.toast(T["emerg"], icon="🚨")
            return True
        except Exception as e:
            st.error(f"{T['noserver']} ({e})")
            return False

    # ---- patient
    st.markdown(f"#### {T['who']}")
    ids = ["__new__"] + sorted(db, key=lambda i: db[i]["name"].lower())
    sel = st.selectbox(T["who"], ids, key="sel_pid", label_visibility="collapsed",
                       format_func=lambda i: T["new_p"] if i == "__new__" else f"{db[i]['name']} • {db[i].get('age') or '-'}")
    if sel == "__new__":
        with st.container(border=True):
            r1 = st.columns(3)
            name = r1[0].text_input(T["name"], key="f_name")
            age = r1[1].text_input(T["age"], key="f_age", placeholder=T["age_ph"])
            gender = r1[2].selectbox(T["gender"], ["لڑکا / مرد", "لڑکی / عورت"], key="f_gender",
                                     format_func=lambda v: T["male"] if v == "لڑکا / مرد" else T["female"])
            r2 = st.columns(3)
            phone = r2[0].text_input(T["phone"], key="f_phone")
            city = r2[1].text_input(T["city"], key="f_city")
            blood = r2[2].selectbox(T["blood"], ["", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"], key="f_blood")
            r3 = st.columns(2)
            allergy = r3[0].text_input(T["allergy"], key="f_alg")
            chronic = r3[1].text_input(T["chronic"], key="f_chr")
        pdata = dict(name=name.strip(), age=age.strip(), gender=gender, phone=phone.strip(), city=city.strip(),
                     blood=blood, allergy=allergy.strip(), chronic=chronic.strip())
    else:
        pdata = db[sel]
        tags = "".join(f"<span class='tg'>{esc(x)}</span>" for x in [pdata.get("gender"), pdata.get("city"), pdata.get("phone"), pdata.get("blood")] if x)
        tags += "".join(f"<span class='tg r'>{T[k]}: {esc(pdata[f])}</span>" for k, f in [("alg", "allergy"), ("note", "chronic")] if pdata.get(f))
        st.markdown(f"<div class='pc'><div class='av'>{esc(initials(pdata['name']))}</div><div><b style='font-size:20px'>{esc(pdata['name'])}</b> "
                    f"• {esc(pdata.get('age') or '')}<div class='tags'>{tags}</div></div></div>", unsafe_allow_html=True)

    # ---- symptoms
    st.markdown(T["tap"])
    label_of = {q[0]: (q[1] if RTL else q[2]) for q in QUICK}
    try:
        picked = st.pills(T["symp"], [q[0] for q in QUICK], selection_mode="multi", format_func=lambda k: label_of[k], label_visibility="collapsed")
    except Exception:
        picked = st.multiselect(T["symp"], [q[0] for q in QUICK], format_func=lambda k: label_of[k], label_visibility="collapsed")
    picked = picked or []

    st.markdown(T["speak"])
    try:
        audio = st.audio_input(T["mic"], label_visibility="collapsed")
    except Exception:
        audio = None
    if audio is not None:
        data = audio.getvalue()
        if st.session_state.get("last_audio") != hash(data):
            st.session_state["last_audio"] = hash(data)
            try:
                with st.spinner(T["writing"]):
                    st.session_state["typed"] = transcribe_urdu(data)
            except ImportError:
                st.error(T["pip_sr"])
            except Exception:
                st.warning(T["no_hear"])

    typed = st.text_area(T["type"], key="typed", placeholder=T["type_ph"], height=110)
    symptoms = " ".join([typed.strip()] + [QUICK_TEXT[p] for p in picked]).strip()

    if st.button(T["check"], type="primary"):
        if sel == "__new__" and not pdata["name"]:
            st.warning(T["need_name"])
        elif not symptoms:
            st.warning(T["enter_s"])
        else:
            pid = sel
            if sel == "__new__":
                pid = uuid.uuid4().hex[:8]
                db[pid] = {**pdata, "created": datetime.datetime.now().isoformat(), "visits": []}
                save_db(db)
            st.session_state["cur_pid"] = pid
            ctx = " ".join(x for x in [f"(پرانی بیماری: {db[pid]['chronic']})" if db[pid].get("chronic") else "",
                                       f"(الرجی: {db[pid]['allergy']})" if db[pid].get("allergy") else ""] if x)
            st.session_state["ctx"] = ctx
            run_check(pid, db[pid].get("age", ""), db[pid].get("gender", "لڑکا / مرد"), (symptoms + " " + ctx).strip())

    # ---- language switch re-run
    res = st.session_state.get("result")
    if res and res.get("language") != out_lang and st.session_state.get("last_input"):
        a0, g0, s0 = st.session_state["last_input"]
        if run_check(st.session_state.get("cur_pid"), a0, g0, s0, record=False):
            st.rerun()

    res = st.session_state.get("result")
    if res:
        render_html(result_html(res), result_height(res))
        if res.get("care"):
            render_html(care_html(res), care_height(res))
        if st.button(T["listen"]):
            care = res.get("care") or {}
            say = " ۔ ".join([res["title"], res["message"], res.get("reasoning", "")] + res["steps"] + care.get("tips", [])[:3])
            try:
                with st.spinner(T["making"]):
                    st.audio(speak(say, res["language"]), format="audio/mp3", autoplay=True)
            except ImportError:
                st.error(T["pip_tts"])
            except Exception:
                st.warning(T["need_net"])
        if res.get("follow_ups"):
            st.subheader(T["more"]); st.caption(T["more_cap"])
            with st.form("followup"):
                answers = [st.text_input(q, key=f"fu_{i}", placeholder=T["yn"]) for i, q in enumerate(res["follow_ups"])]
                again = st.form_submit_button(T["again"])
            if again:
                fu = [{"q": q, "a": x} for q, x in zip(res["follow_ups"], answers) if x.strip()]
                a0, g0, s0 = st.session_state["last_input"]
                if run_check(st.session_state.get("cur_pid"), a0, g0, s0, fu, record=False):
                    st.rerun()
        elif not res.get("llm_used"):
            st.caption(T["ai_off"])
        with st.expander(T["tech"]):
            st.json({"final_level": res["triage_level"], "ml_level": res["ml_level"], "ml_probabilities": res.get("ml_probs"),
                     "llm_used": res.get("llm_used"), "red_flag_rules_triggered": res["red_flags_found"],
                     "profile": res.get("profile"), "escalation_reasons": res.get("escalation_reasons"),
                     "ai_status": res.get("llm_status")})
        a1, g1, s1 = st.session_state.get("last_input", ("", "", ""))
        st.download_button(T["dl"], report_html(res, a1, g1, s1, datetime.datetime.now().strftime("%d-%m-%Y %H:%M")),
                           file_name="sehatsathi_parchi.html", mime="text/html")
        st.button(T["new_p"], on_click=check_for, args=("__new__",))

st.divider()
st.caption(T["foot"])
