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

st.set_page_config(page_title="صحت ساتھی • SehatSathi Pro", page_icon="🩺", layout="wide", initial_sidebar_state="expanded")

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
        "enter": "🚀 ایپ میں داخل ہوں", "back": "⬅️ ہوم اسکرین", "lang": "زبان / Language",
        "hello": "خوش آمدید، معالج 👋", "hello_s": "آج کس مریض کو بروقت اور درست طبی رہنمائی دینی ہے؟",
        "s_pat": "کل رجسٹرڈ مریض", "s_vis": "کل معائنے", "s_em": "ہنگامی کیسز", "s_td": "آج کے معائنے",
        "dist": "📊 نتائج کی تقسیم (Triage Analytics)", "recent": "🕘 حالیہ معائنے", "none": "ابھی کوئی ریکارڈ موجود نہیں۔ پہلا معائنہ شروع کریں!",
        "q_new": "➕ نیا معائنہ شروع کریں", "q_rec": "📂 تمام ریکارڈز دیکھیں",
        "step1": "مرحلہ 1 • مریض کا انتخاب یا اندراج", "step2": "مرحلہ 2 • علامات (ٹچ، آواز یا تحریر)",
        "who": "👤 مریض", "new_p": "➕ نیا مریض رجسٹر کریں", "name": "مریض کا نام *", "age": "عمر", "age_ph": "مثال: 2 سال یا 35 سال",
        "gender": "جنس", "phone": "فون نمبر", "city": "شہر / گاؤں", "blood": "بلڈ گروپ",
        "allergy": "الرجی (اگر ہو)", "chronic": "پرانی بیماری (شوگر، بی پی...)",
        "need_name": "براہ کرم مریض کا نام درج کریں۔", "saved_p": "مریض محفوظ ہو گیا ✅",
        "tap": "👆 عام علامات پر کلک کریں (ایک یا زیادہ منتخب کریں)", "symp": "علامات",
        "speak": "🎤 یا بول کر بتائیں (اردو وائس ان پٹ)", "mic": "بولنے کے لیے مائیک دبائیں",
        "type": "✍️ یا تفصیل خود لکھیں (اردو، رومن اردو یا انگریزی)", "type_ph": "مثال: تین دن سے تیز بخار، جسم میں درد اور دست لگے ہوئے ہیں...",
        "check": "🔍 AI طبی جائزہ لیں", "enter_s": "پہلے علامات لکھیں یا اوپر دیے گئے بٹنوں سے چنیں۔",
        "listen": "🔊 نتیجہ آواز میں سنیں", "more": "🩺 AI کے مزید سوالات",
        "more_cap": "مزید درست فیصلے کے لیے نیچے دیے گئے سوالات کے مختصر جواب دیں:",
        "yn": "جی ہاں / نہیں / مختصر تفصیل", "again": "✅ جوابات کے ساتھ دوبارہ جائزہ لیں",
        "tech": "🔬 تکنیکی اور ML ماڈل کی تفصیل", "dl": "📄 طبی پرچی ڈاؤن لوڈ کریں", "spin": "AI اور ML ماڈل علامات کا تجزیہ کر رہے ہیں...",
        "emerg": "ہنگامی حالت! مریض کو فوراً قریبی ہسپتال لے جائیں", "noserver": "بیک اینڈ سرور سے رابطہ نہیں ہو سکا۔",
        "writing": "آواز کو تحریر میں بدلا جا رہا ہے...", "pip_sr": "pip install SpeechRecognition",
        "no_hear": "آواز صاف سنائی نہیں دی۔ دوبارہ بولیں یا لکھ دیں۔", "making": "آواز تیار ہو رہی ہے...",
        "pip_tts": "pip install gTTS", "need_net": "آواز سننے کے لیے انٹرنیٹ درکار ہے۔",
        "ai_off": "ℹ️ AI بند ہے۔ کلینیکل رولز، ML ماڈل اور ہوم کیئر انجن کام کر رہے ہیں۔",
        "foot": "⚠️ یہ تجرباتی AI معاون ہے، حتمی طبی تشخیص نہیں۔ صرف فرضی یا تعلیمی ڈیٹا استعمال کریں۔",
        "male": "لڑکا / مرد", "female": "لڑکی / عورت", "search": "🔎 نام، فون نمبر یا شہر سے مریض تلاش کریں...",
        "visits": "معائنے", "last": "آخری", "del": "🗑️ مریض حذف کریں", "again_p": "➕ اس مریض کا نیا معائنہ",
        "csv": "⬇️ تمام ریکارڈ CSV ایکسپورٹ کریں", "no_vis": "کوئی معائنہ ریکارڈ نہیں", "info": "معلومات",
        "note": "پرانی بیماری", "alg": "الرجی",
    },
    "en": {
        "pages": {"dashboard": "🏠 Dashboard", "check": "🩺 New Assessment", "records": "📂 Patient Directory"},
        "enter": "🚀 Launch Workspace", "back": "⬅️ Welcome Screen", "lang": "زبان / Language",
        "hello": "Welcome Back 👋", "hello_s": "Who needs timely clinical triage today?",
        "s_pat": "Total Patients", "s_vis": "Assessments", "s_em": "Emergencies", "s_td": "Checked Today",
        "dist": "📊 Triage Distribution", "recent": "🕘 Recent Assessments", "none": "No records yet. Start your first patient assessment!",
        "q_new": "➕ Start New Assessment", "q_rec": "📂 Open Patient Records",
        "step1": "Step 1 • Patient Profile", "step2": "Step 2 • Clinical Symptoms (Tap, Speak, or Type)",
        "who": "👤 Patient", "new_p": "➕ Register New Patient", "name": "Full Name *", "age": "Age", "age_ph": "e.g. 2 years or 35 yrs",
        "gender": "Gender", "phone": "Phone Number", "city": "City / Village", "blood": "Blood Group",
        "allergy": "Known Allergies", "chronic": "Chronic Conditions (Diabetes, HTN...)",
        "need_name": "Patient name is required to proceed.", "saved_p": "Patient saved ✅",
        "tap": "👆 Quick-Select Common Symptoms", "symp": "Symptoms",
        "speak": "🎤 Voice Dictation (Urdu)", "mic": "Press the mic to speak",
        "type": "✍️ Clinical Notes (Urdu, Roman Urdu, or English)", "type_ph": "e.g. High fever and diarrhea for 3 days with body aches...",
        "check": "🔍 Run AI Triage Assessment", "enter_s": "Please enter symptoms or select from the pills above.",
        "listen": "🔊 Listen to Audio Guidance", "more": "🩺 AI Follow-up Questions",
        "more_cap": "Answer these clarifying questions for higher triage accuracy:",
        "yn": "Yes / No / brief details", "again": "✅ Re-evaluate with Answers",
        "tech": "🔬 Technical & ML Model Diagnostics", "dl": "📄 Download Medical Slip", "spin": "Analyzing clinical symptoms...",
        "emerg": "Emergency! Transfer patient to hospital immediately", "noserver": "Could not reach the triage backend server.",
        "writing": "Transcribing voice input...", "pip_sr": "pip install SpeechRecognition",
        "no_hear": "Could not transcribe clearly. Please try again or type.", "making": "Synthesizing audio...",
        "pip_tts": "pip install gTTS", "need_net": "Internet connection required for audio.",
        "ai_off": "ℹ️ LLM offline. Clinical rules, ML model & home-care engine are active.",
        "foot": "⚠️ Experimental AI prototype — not a substitute for professional medical diagnosis.",
        "male": "Male", "female": "Female", "search": "🔎 Search patients by name, phone, or city...",
        "visits": "visits", "last": "Last", "del": "🗑️ Delete Record", "again_p": "➕ New Checkup",
        "csv": "⬇️ Export All Records (CSV)", "no_vis": "No visits recorded", "info": "Info",
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
LEVEL_COL = {"emergency": "#ef4444", "urgent": "#f59e0b", "home": "#10b981"}
PAGES = ["dashboard", "check", "records"]
esc = _h.escape


def render_html(html, height):
    try:
        import streamlit.components.v1 as components
        components.html(html, height=height, scrolling=False)
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
    st.markdown("""
    <div style='display:flex;align-items:center;gap:12px;padding:6px 4px 16px;border-bottom:1px solid rgba(255,255,255,0.12);margin-bottom:14px;'>
        <div style='width:42px;height:42px;border-radius:14px;background:linear-gradient(135deg,#34d399,#059669);display:grid;place-items:center;font-size:22px;box-shadow:0 6px 16px rgba(16,185,129,0.35);'>🩺</div>
        <div>
            <div style='font-size:18px;font-weight:800;color:#ffffff!important;line-height:1.1;'>صحت ساتھی</div>
            <div style='font-size:11px;font-weight:600;color:#a7f3d0!important;letter-spacing:0.06em;'>SEHATSATHI PRO</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    lang_label = st.radio("زبان / Language", ["اردو", "English"], horizontal=True, key="lang_choice")
    out_lang = "ur" if lang_label == "اردو" else "en"
    T = TR[out_lang]
    if PG != "welcome":
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.radio("nav", PAGES, index=PAGES.index(PG) if PG in PAGES else 0, key="nav_radio",
                 format_func=lambda p: T["pages"][p], on_change=on_nav, label_visibility="collapsed")
        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
        st.button(T["back"], on_click=go, args=("welcome",), use_container_width=True)

    # Backend status pill in sidebar
    status_ok = _backend_up()
    st.markdown(f"""
    <div style='margin-top:28px;padding:10px 12px;border-radius:14px;background:rgba(0,0,0,0.22);border:1px solid rgba(255,255,255,0.08);display:flex;align-items:center;gap:9px;font-size:12px;'>
        <span style='width:9px;height:9px;border-radius:50%;background:{"#34d399" if status_ok else "#f87171"};box-shadow:0 0 8px {"#34d399" if status_ok else "#f87171"};'></span>
        <span style='color:#d1fae5!important;font-weight:600;'>{"AI Engine Online" if status_ok else "Engine Starting..."}</span>
    </div>
    """, unsafe_allow_html=True)

RTL = out_lang == "ur"
DIR, ALIGN = ("rtl", "right") if RTL else ("ltr", "left")
HIDE_SB = "[data-testid='stSidebar'],[data-testid='stSidebarCollapsedControl']{display:none}" if PG == "welcome" else ""

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Noto+Naskh+Arabic:wght@400;500;600;700;800&display=swap');
:root{
 --ink:#0f172a;--muted:#64748b;--teal:#0d9488;--teal-dark:#0f766e;--blue:#2563eb;
 --line:rgba(226,232,240,0.85);--surface:rgba(255,255,255,0.88);
 --shadow:0 12px 32px -4px rgba(15,23,42,0.06), 0 4px 12px -2px rgba(15,23,42,0.03);
 --shadow-hover:0 20px 40px -8px rgba(13,148,136,0.14);
 --radius:24px;
}
*{box-sizing:border-box}
html,body,.stApp{min-width:320px}
html,body,[class*="css"],.stApp,textarea,input,button,label,p,h1,h2,h3,h4,li,span,div{
 font-family:'Plus Jakarta Sans','Noto Naskh Arabic','Jameel Noori Nastaleeq','Segoe UI',sans-serif!important;
}
.stApp{
 direction:__DIR__;text-align:__AL__;color:var(--ink);
 background:
  radial-gradient(circle at 8% 4%, rgba(20,184,166,0.13) 0%, transparent 32%),
  radial-gradient(circle at 92% 8%, rgba(59,130,246,0.11) 0%, transparent 34%),
  radial-gradient(circle at 50% 95%, rgba(16,185,129,0.08) 0%, transparent 40%),
  #f4f8fa;
}
header[data-testid="stHeader"]{background:rgba(244,248,250,0.72);backdrop-filter:blur(16px);border-bottom:1px solid rgba(226,232,240,0.6)}
[data-testid="stMainBlockContainer"], [data-testid="stAppViewContainer"]>.main .block-container{
 width:100%;max-width:1360px;padding:clamp(16px,2.5vw,32px) clamp(14px,3vw,40px) 60px;
}
[data-testid="stVerticalBlock"]{gap:1.1rem}
[data-testid="stHorizontalBlock"]{gap:clamp(14px,2vw,24px);align-items:stretch}

/* Glass Sidebar */
[data-testid="stSidebar"]{
 background:linear-gradient(175deg,#042f2e 0%,#064e3b 48%,#0f766e 100%);
 border-right:1px solid rgba(255,255,255,0.12);
 box-shadow:8px 0 30px rgba(4,47,46,0.15);
}
[data-testid="stSidebar"]>div{padding:24px 16px}
[data-testid="stSidebar"] *{color:#ecfdf5!important}
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"]{gap:9px}
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label{
 background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.09);
 border-radius:16px;padding:11px 14px;transition:all .22s cubic-bezier(.4,0,.2,1);font-weight:600;
}
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:hover{
 background:rgba(255,255,255,0.13);transform:translateX(__SHIFT__);
}
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked){
 background:linear-gradient(135deg,rgba(52,211,153,0.28),rgba(16,185,129,0.18));
 border-color:rgba(110,231,183,0.55);box-shadow:0 8px 20px rgba(0,0,0,0.15);font-weight:700;
}
[data-testid="stSidebar"] button{
 background:rgba(255,255,255,0.92)!important;color:#064e3b!important;
 border-radius:14px!important;font-weight:750!important;border:0!important;
 box-shadow:0 6px 16px rgba(0,0,0,0.12);
}

/* Typography */
h1,h2,h3,h4{color:var(--ink);letter-spacing:-.025em}
p,label,.stMarkdown{text-align:__AL__}
.stCaption,small{color:var(--muted)}

/* Glassmorphism Containers & Expanders */
div[data-testid="stVerticalBlockBorderWrapper"]{
 border:1px solid rgba(255,255,255,0.95);
 outline:1px solid rgba(203,213,225,0.55);
 border-radius:var(--radius);
 background:var(--surface);
 backdrop-filter:blur(16px);
 box-shadow:var(--shadow);
 padding:clamp(16px,2.2vw,24px);
 transition:box-shadow .25s ease, transform .25s ease;
}
div[data-testid="stExpander"]{
 border:1px solid rgba(203,213,225,0.7);
 border-radius:20px;
 background:rgba(255,255,255,0.92);
 backdrop-filter:blur(12px);
 overflow:hidden;
 box-shadow:0 6px 20px rgba(15,23,42,0.04);
 transition:all .2s ease;
}
div[data-testid="stExpander"]:hover{border-color:#5eead4;box-shadow:0 12px 26px rgba(13,148,136,0.09)}
div[data-testid="stExpander"] summary{padding:14px 18px;font-weight:700;font-size:15px}

/* Inputs & Interactive Widgets */
input,textarea,[data-baseweb="select"]>div,[data-baseweb="input"]>div{
 direction:__DIR__;text-align:__AL__;
 border-radius:16px!important;border:1.5px solid #e2e8f0!important;
 background:#ffffff!important;min-height:48px;
 transition:border-color .2s, box-shadow .2s;
}
input:focus,textarea:focus{border-color:#0d9488!important;box-shadow:0 0 0 3px rgba(13,148,136,0.14)!important}
textarea{min-height:118px!important;padding:14px 16px!important;line-height:1.6!important}
[data-testid="stTextInput"] label,[data-testid="stTextArea"] label,[data-testid="stSelectbox"] label{
 font-weight:700;color:#334155;font-size:13.5px;margin-bottom:4px;
}

/* Glowing Audio Recorder */
[data-testid="stAudioInput"]{
 padding:16px;border:1.5px dashed #2dd4bf;border-radius:20px;
 background:linear-gradient(135deg,rgba(240,253,250,0.95),rgba(239,246,255,0.95));
 box-shadow:inset 0 2px 8px rgba(20,184,166,0.06);
}

/* Interactive Symptom Pills */
[data-testid="stPills"]{gap:10px!important}
[data-testid="stPills"] button{
 border-radius:999px!important;border:1.5px solid #e2e8f0!important;
 min-height:44px;padding:8px 16px!important;font-weight:650!important;
 background:#ffffff!important;color:#1e293b!important;
 box-shadow:0 2px 6px rgba(15,23,42,0.03);
 transition:all .18s cubic-bezier(.4,0,.2,1)!important;
}
[data-testid="stPills"] button:hover{
 border-color:#5eead4!important;transform:translateY(-2px);
 box-shadow:0 6px 14px rgba(13,148,136,0.12)!important;
}
[data-testid="stPills"] button[aria-pressed="true"]{
 background:linear-gradient(135deg,#0d9488,#059669)!important;
 border-color:#0d9488!important;color:#ffffff!important;
 box-shadow:0 8px 18px rgba(13,148,136,0.28)!important;
}

/* Buttons */
div.stButton>button,div.stDownloadButton>button,[data-testid="stFormSubmitButton"] button{
 min-height:50px;border-radius:16px;border:1.5px solid #e2e8f0;
 font-weight:750;font-size:15px;background:#ffffff;color:#0f172a;
 transition:all .2s cubic-bezier(.4,0,.2,1);
}
div.stButton>button:hover,div.stDownloadButton>button:hover{
 transform:translateY(-2px);box-shadow:0 12px 24px rgba(15,23,42,0.09);border-color:#5eead4;
}
div.stButton>button[kind="primary"],[data-testid="stFormSubmitButton"] button{
 width:100%;min-height:56px;font-size:1.06rem;border:0;color:#ffffff!important;
 background:linear-gradient(120deg,#0d9488 0%,#0284c7 52%,#2563eb 100%);
 background-size:200% auto;
 box-shadow:0 12px 26px -4px rgba(13,148,136,0.36);
}
div.stButton>button[kind="primary"]:hover,[data-testid="stFormSubmitButton"] button:hover{
 background-position:right center;
 box-shadow:0 16px 32px -4px rgba(37,99,235,0.42);
}
div.stDownloadButton>button{width:100%}

/* Bento KPI Stats */
.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:18px;margin:14px 0 26px}
.stat{
 background:rgba(255,255,255,0.92);backdrop-filter:blur(14px);
 border-radius:22px;padding:22px;
 border:1px solid rgba(255,255,255,0.95);outline:1px solid rgba(226,232,240,0.75);
 box-shadow:var(--shadow);position:relative;overflow:hidden;min-width:0;
 transition:transform .22s ease, box-shadow .22s ease;
}
.stat:hover{transform:translateY(-4px);box-shadow:var(--shadow-hover)}
.stat:before{content:'';position:absolute;top:0;bottom:0;__SIDE__:0;width:5px;background:var(--c)}
.stat-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}
.stat-ico{width:42px;height:42px;border-radius:14px;display:grid;place-items:center;font-size:20px;background:color-mix(in srgb, var(--c) 12%, white)}
.stat b{display:block;font-size:clamp(30px,3.2vw,42px);line-height:1.05;color:#0f172a;font-weight:800;letter-spacing:-0.03em}
.stat span{display:block;color:#64748b;font-weight:650;font-size:13.5px;margin-top:6px}

/* Page Titles & Step Headers */
.pt{font-size:clamp(28px,3.6vw,40px);font-weight:800;margin:0;color:#0f172a;letter-spacing:-.03em;line-height:1.2}
.sub{color:#64748b;margin:6px 0 18px;font-size:15.5px}
.step-badge{
 display:inline-flex;align-items:center;gap:8px;
 background:linear-gradient(135deg,#f0fdfa,#eff6ff);
 border:1px solid #99f6e4;color:#0f766e;
 padding:6px 14px;border-radius:999px;font-size:13px;font-weight:800;margin-bottom:8px;
}

/* Triage Analytics Bar */
.mix{display:flex;height:14px;border-radius:999px;overflow:hidden;background:#e2e8f0;margin:16px 0 14px;gap:2px}
.lg{display:flex;gap:14px;flex-wrap:wrap;font-size:13px;font-weight:600;color:#475569}
.lg i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-inline-end:6px}

/* Visit & Patient Rows */
.vr{
 display:flex;align-items:center;gap:14px;padding:13px 10px;border-radius:16px;
 border-bottom:1px solid #f1f5f9;min-width:0;transition:background .15s;
}
.vr:hover{background:#f8fafc}
.vr:last-child{border-bottom:0}
.av{
 width:44px;height:44px;border-radius:15px;color:#fff;font-weight:800;font-size:16px;
 display:grid;place-items:center;flex:0 0 44px;
 background:linear-gradient(135deg,#0d9488,#2563eb);
 box-shadow:0 6px 14px rgba(13,148,136,0.22);
}
.vr>div:nth-child(2){min-width:0;flex:1}
.vr .t{font-weight:750;color:#0f172a;font-size:15px;overflow-wrap:anywhere}
.vr .s{font-size:12.5px;color:#64748b;margin-top:2px;overflow-wrap:anywhere}
.pill{
 margin-inline-start:auto;padding:6px 12px;border-radius:999px;
 font-weight:750;font-size:11.5px;color:#fff;white-space:nowrap;
 box-shadow:0 4px 10px rgba(0,0,0,0.1);
}
.pc{display:flex;gap:16px;align-items:center;padding:6px 2px;min-width:0}
.pc>div:last-child{min-width:0;overflow-wrap:anywhere}
.pc .av{width:56px;height:56px;font-size:22px;border-radius:18px;flex:0 0 56px}
.tags{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
.tg{background:#eff6ff;color:#1d4ed8;border:1px solid #dbeafe;border-radius:10px;padding:4px 10px;font-size:12px;font-weight:700}
.tg.r{background:#fef2f2;color:#b91c1c;border-color:#fecaca}

iframe{max-width:100%;border:0;border-radius:24px}

@media(max-width:1050px){
 .stats{grid-template-columns:repeat(2,minmax(0,1fr))}
}
@media(max-width:760px){
 [data-testid="stMainBlockContainer"],[data-testid="stAppViewContainer"]>.main .block-container{padding:12px 12px 36px}
 [data-testid="stHorizontalBlock"]{flex-direction:column!important;gap:12px!important}
 [data-testid="stHorizontalBlock"]>[data-testid="column"]{width:100%!important;min-width:100%!important;flex:1 1 100%!important}
 .stats{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
 .stat{padding:16px}
 div.stButton>button,div.stDownloadButton>button{width:100%}
}
__HIDE__
</style>""".replace("__DIR__", DIR).replace("__AL__", ALIGN).replace("__SIDE__", "right" if RTL else "left") \
            .replace("__SHIFT__", "-4px" if RTL else "4px").replace("__HIDE__", HIDE_SB), unsafe_allow_html=True)


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
            f"<div><div class='t'>{esc(p['name'])}</div><div class='s'>{esc(v['when'])} • {esc(v['symptoms'][:65])}</div></div>"
            f"<span class='pill' style='background:{c}'>{esc(v['title'])}</span></div>")


# ================================================================ PAGE: welcome
def landing_html():
    return f"""<!doctype html><html><head><meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1, viewport-fit=cover'>
<link href='https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Noto+Naskh+Arabic:wght@400;700;800&display=swap' rel='stylesheet'>
<style>
*{{box-sizing:border-box}}html,body{{margin:0;width:100%;font-family:'Plus Jakarta Sans','Noto Naskh Arabic','Segoe UI',sans-serif;background:transparent}}
.w{{
 position:relative;isolation:isolate;overflow:hidden;min-height:510px;border-radius:32px;color:#fff;
 padding:clamp(30px,5vw,56px) clamp(18px,4vw,46px);text-align:center;
 background:
  radial-gradient(750px 380px at 85% 0%,rgba(59,130,246,0.48),transparent),
  radial-gradient(650px 400px at 10% 100%,rgba(16,185,129,0.42),transparent),
  linear-gradient(135deg,#042f2e 0%,#064e3b 52%,#0f172a 100%);
 box-shadow:0 24px 60px rgba(4,47,46,0.28);
 border:1px solid rgba(255,255,255,0.14);
}}
.w:before{{
 content:'';position:absolute;inset:0;z-index:-1;opacity:.14;
 background-image:linear-gradient(rgba(255,255,255,0.16) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,0.16) 1px,transparent 1px);
 background-size:36px 36px;mask-image:radial-gradient(ellipse at center,black 40%,transparent 85%);
}}
.orb{{position:absolute;z-index:-1;border-radius:50%;filter:blur(40px);opacity:0.45;animation:float 8s ease-in-out infinite}}
@keyframes float{{50%{{transform:translateY(-24px) scale(1.06)}}}}
.ecg{{position:absolute;left:0;right:0;top:46%;opacity:.2;pointer-events:none}}
.ecg path{{stroke:#34d399;stroke-width:2.5;fill:none;stroke-dasharray:900;stroke-dashoffset:900;animation:dash 3.8s linear infinite}}
@keyframes dash{{to{{stroke-dashoffset:-900}}}}
.in{{position:relative;z-index:1;max-width:940px;margin:auto}}
.brand-pill{{
 display:inline-flex;align-items:center;gap:8px;border:1px solid rgba(110,231,183,0.4);
 background:rgba(255,255,255,0.1);backdrop-filter:blur(10px);
 padding:8px 18px;border-radius:999px;color:#a7f3d0;font-size:12.5px;font-weight:700;letter-spacing:.06em;
}}
.lg{{font-size:clamp(46px,6vw,64px);margin:14px 0 2px;filter:drop-shadow(0 10px 22px rgba(0,0,0,0.3));animation:pulse 2.6s ease-in-out infinite}}
@keyframes pulse{{50%{{transform:scale(1.08)}}}}
h1{{font-size:clamp(40px,7vw,76px);margin:4px 0 4px;font-weight:800;line-height:1.22;letter-spacing:-.03em;color:#fff}}
.subline{{font-size:clamp(16px,2vw,21px);color:#a7f3d0;margin:0 0 28px;line-height:1.6;font-weight:500}}
.g{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;max-width:920px;margin:0 auto}}
.c{{
 background:linear-gradient(155deg,rgba(255,255,255,0.14),rgba(255,255,255,0.04));
 border:1px solid rgba(255,255,255,0.22);backdrop-filter:blur(12px);
 border-radius:22px;padding:20px 12px;font-weight:700;font-size:14.5px;
 transition:transform .2s;box-shadow:inset 0 1px rgba(255,255,255,0.2);
}}
.c:hover{{transform:translateY(-4px);border-color:rgba(110,231,183,0.6)}}
.c span{{display:block;font-size:30px;margin-bottom:8px}}
.c small{{display:block;font-weight:500;color:#d1fae5;margin-top:6px;font-size:12px;line-height:1.5}}
.trust{{margin:24px 0 0;color:#99f6e4;font-size:12.5px;letter-spacing:.03em;opacity:0.9}}
@media(max-width:700px){{.w{{min-height:0;border-radius:24px;padding:28px 14px}}.g{{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}}}}
</style></head><body><div class='w'>
<div class='orb' style='width:260px;height:260px;background:#10b981;left:-60px;top:-60px'></div>
<div class='orb' style='width:240px;height:240px;background:#3b82f6;right:-40px;bottom:-50px;animation-delay:2s'></div>
<svg class='ecg' viewBox='0 0 800 80' preserveAspectRatio='none' height='95' width='100%'><path d='M0 40H150L170 40L185 8L205 72L222 40H420L440 40L455 14L475 66L492 40H800'/></svg>
<div class='in'>
 <div class='brand-pill'>✦ NEXT-GEN AI CLINICAL TRIAGE SYSTEM</div>
 <div class='lg'>🩺</div>
 <h1>صحت ساتھی</h1>
 <p class='subline'>SehatSathi Pro &nbsp;•&nbsp; صحیح وقت پر صحیح طبی فیصلہ</p>
 <div class='g'>
  <div class='c'><span>🧠</span>Hybrid AI + ML<small>ہنگامی / جلد / گھر پر علاج</small></div>
  <div class='c'><span>🎤</span>Urdu Voice AI<small>بول کر علامات درج کریں</small></div>
  <div class='c'><span>📂</span>Smart EHR<small>مریضوں کا مکمل ریکارڈ</small></div>
  <div class='c'><span>🚑</span>Instant Alert<small>ہنگامی صورتحال کی نشاندہی</small></div>
 </div>
 <div class='trust'>اردو &nbsp;•&nbsp; Roman Urdu &nbsp;•&nbsp; English &nbsp;|&nbsp; Built for Fast Community Healthcare</div>
</div></div></body></html>"""


if PG == "welcome":
    render_html(landing_html(), 560)
    _, mid, _ = st.columns([1, 1.3, 1])
    mid.button(T["enter"], type="primary", on_click=go, args=("dashboard",))
    st.caption(T["foot"])
    st.stop()

db = load_db()

# ================================================================ PAGE: dashboard
if PG == "dashboard":
    S = stats(db)
    st.markdown(f"<p class='pt'>{T['hello']}</p><p class='sub'>{T['hello_s']}</p>", unsafe_allow_html=True)

    cards = [
        (T["s_pat"], S["pat"], "#2563eb", "👥"),
        (T["s_vis"], S["vis"], "#0d9488", "🩺"),
        (T["s_em"], S["em"], "#ef4444", "🚨"),
        (T["s_td"], S["td"], "#f59e0b", "📅"),
    ]
    st.markdown("<div class='stats'>" + "".join(
        f"<div class='stat' style='--c:{c}'><div class='stat-top'><div class='stat-ico'>{ico}</div></div><b>{n}</b><span>{l}</span></div>"
        for l, n, c, ico in cards) + "</div>", unsafe_allow_html=True)

    b1, b2 = st.columns(2)
    b1.button(T["q_new"], type="primary", on_click=check_for, args=("__new__",))
    b2.button(T["q_rec"], on_click=go, args=("records",), use_container_width=True)

    c1, c2 = st.columns([1, 1.45])
    with c1, st.container(border=True):
        st.markdown(f"#### {T['dist']}")
        tot = max(S["vis"], 1)
        em_p = 100 * S["mix"]["emergency"] / tot
        ur_p = 100 * S["mix"]["urgent"] / tot
        hm_p = 100 * S["mix"]["home"] / tot

        # Clean SVG Donut visualization
        st.markdown(f"""
        <div style='display:flex;align-items:center;justify-content:center;margin:14px 0 8px;'>
            <div style='width:148px;height:148px;border-radius:50%;
                background:conic-gradient(#ef4444 0% {em_p}%, #f59e0b {em_p}% {em_p+ur_p}%, #10b981 {em_p+ur_p}% 100%);
                display:grid;place-items:center;box-shadow:0 8px 20px rgba(15,23,42,0.08);'>
                <div style='width:98px;height:98px;border-radius:50%;background:#ffffff;display:flex;flex-direction:column;align-items:center;justify-content:center;'>
                    <b style='font-size:26px;color:#0f172a;line-height:1;'>{S['vis']}</b>
                    <span style='font-size:11px;color:#64748b;font-weight:700;margin-top:3px;'>TOTAL</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        bar = "".join(f"<div style='width:{100 * S['mix'][k] / tot}%;background:{LEVEL_COL[k]}'></div>" for k in LEVEL_COL)
        lab = {"ur": {"emergency": "ہنگامی", "urgent": "جلد ڈاکٹر", "home": "گھر پر"},
               "en": {"emergency": "Emergency", "urgent": "Urgent", "home": "Home Care"}}[out_lang]
        lg = "".join(f"<span><i style='background:{LEVEL_COL[k]}'></i>{lab[k]}: <b>{S['mix'][k]}</b></span>" for k in LEVEL_COL)
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
        with st.expander(f"{last}  {p['name']}   •   {p.get('age') or '-'}   •   {len(vs)} {T['visits']}"):
            tags = "".join(f"<span class='tg'>{esc(x)}</span>" for x in [p.get("gender"), p.get("city"), p.get("phone"), p.get("blood")] if x)
            tags += "".join(f"<span class='tg r'>{T[k]}: {esc(p[f])}</span>" for k, f in [("alg", "allergy"), ("note", "chronic")] if p.get(f))
            st.markdown(f"<div class='pc'><div class='av'>{esc(initials(p['name']))}</div><div><b style='font-size:20px'>{esc(p['name'])}</b><div class='tags'>{tags}</div></div></div>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:10px 0;border:0;border-top:1px solid #f1f5f9'>", unsafe_allow_html=True)
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
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
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

    # ---- Step 1: Patient Profile
    st.markdown(f"<div class='step-badge'>{T['step1']}</div>", unsafe_allow_html=True)
    with st.container(border=True):
        ids = ["__new__"] + sorted(db, key=lambda i: db[i]["name"].lower())
        sel = st.selectbox(T["who"], ids, key="sel_pid", label_visibility="collapsed",
                           format_func=lambda i: T["new_p"] if i == "__new__" else f"{db[i]['name']} • {db[i].get('age') or '-'}")
        if sel == "__new__":
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

    # ---- Step 2: Symptoms Input
    st.markdown(f"<div class='step-badge'>{T['step2']}</div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(f"**{T['tap']}**")
        label_of = {q[0]: (q[1] if RTL else q[2]) for q in QUICK}
        try:
            picked = st.pills(T["symp"], [q[0] for q in QUICK], selection_mode="multi", format_func=lambda k: label_of[k], label_visibility="collapsed")
        except Exception:
            picked = st.multiselect(T["symp"], [q[0] for q in QUICK], format_func=lambda k: label_of[k], label_visibility="collapsed")
        picked = picked or []

        col_voice, col_text = st.columns([1, 1.6])
        with col_voice:
            st.markdown(f"**{T['speak']}**")
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

        with col_text:
            typed = st.text_area(T["type"], key="typed", placeholder=T["type_ph"], height=120)

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
        render_html(result_html(res), result_height(res) + 180)
        if res.get("care"):
            render_html(care_html(res), care_height(res))

        act1, act2, act3 = st.columns(3)
        with act1:
            if st.button(T["listen"], use_container_width=True):
                care = res.get("care") or {}
                say = " ۔ ".join([res["title"], res["message"], res.get("reasoning", "")] + res["steps"] + care.get("tips", [])[:3])
                try:
                    with st.spinner(T["making"]):
                        st.audio(speak(say, res["language"]), format="audio/mp3", autoplay=True)
                except ImportError:
                    st.error(T["pip_tts"])
                except Exception:
                    st.warning(T["need_net"])
        with act2:
            a1, g1, s1 = st.session_state.get("last_input", ("", "", ""))
            st.download_button(T["dl"], report_html(res, a1, g1, s1, datetime.datetime.now().strftime("%d-%m-%Y %H:%M")),
                               file_name="sehatsathi_parchi.html", mime="text/html", use_container_width=True)
        with act3:
            st.button(T["new_p"], on_click=check_for, args=("__new__",), use_container_width=True)

        if res.get("follow_ups"):
            with st.container(border=True):
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

st.divider()
st.caption(T["foot"])
