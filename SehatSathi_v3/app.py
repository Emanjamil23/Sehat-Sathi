# -*- coding: utf-8 -*-
import os, sys, time, socket, subprocess
import streamlit as st


def _backend_up():
    s = socket.socket()
    s.settimeout(0.5)
    try:
        s.connect(("127.0.0.1", 8000))
        return True
    except OSError:
        return False
    finally:
        s.close()


@st.cache_resource
def start_backend():
    if _backend_up():
        return True
    here = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(here, "sehatsathi", "backend")
    subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app",
         "--host", "127.0.0.1", "--port", "8000"],
        cwd=backend_dir,
    )
    for _ in range(40):
        if _backend_up():
            return True
        time.sleep(1)
    return False


start_backend()

import io
import datetime
import requests
import streamlit as st
from ui_parts import hero_html, result_html, result_height, care_html, care_height, report_html

API_URL = "http://127.0.0.1:8000/triage"

st.set_page_config(page_title="صحت ساتھی SehatSathi", page_icon="🩺", layout="centered")

# ---------------------------------------------------------------- text in both languages
TR = {
    "ur": {
        "settings": "### ⚙️ ترتیبات", "lang": "زبان / Language", "new": "➕ نیا مریض",
        "today": "### 🕘 آج کے مریض", "no_hist": "ابھی کوئی ریکارڈ نہیں۔", "clear": "🗑️ ریکارڈ صاف کریں",
        "age": "👤 عمر", "age_ph": "مثال: بچہ دو سال کا", "gender": "⚧ جنس",
        "tap": "**👆 عام علامات پر ٹچ کریں** (ایک سے زیادہ چن سکتے ہیں)", "symp": "علامات",
        "speak": "**🎤 یا بول کر بتائیں** (اردو میں، انٹرنیٹ چاہیے)", "mic": "بولنے کے لیے مائیک دبائیں",
        "type": "✍️ یا خود لکھیں (اردو، رومن اردو یا انگریزی)", "type_ph": "مثال: تین دن سے تیز بخار اور دست",
        "check": "🔍 چیک کریں", "enter": "پہلے علامات لکھیں یا اوپر سے چنیں۔",
        "listen": "🔊 نتیجہ آواز میں سنیں", "more": "🩺 مزید سوالات",
        "more_cap": "AI کچھ باتیں پوچھ رہا ہے تاکہ فیصلہ بہتر ہو۔ جواب لکھیں اور دوبارہ چیک کریں۔",
        "yn": "جی ہاں / نہیں / تفصیل", "again": "✅ جوابات کے ساتھ دوبارہ چیک کریں",
        "tech": "🔬 تکنیکی تفصیل (جج حضرات کے لیے)", "dl": "📄 پرچی ڈاؤن لوڈ کریں (پرنٹ / ہسپتال کو دکھانے کے لیے)",
        "spin": "جائزہ لیا جا رہا ہے...", "emerg": "ہنگامی حالت! فوراً ہسپتال لے جائیں",
        "noserver": "سرور سے رابطہ نہیں ہو سکا۔ کیا بیک اینڈ چل رہا ہے؟",
        "writing": "آواز کو لکھا جا رہا ہے...", "pip_sr": "پہلے یہ چلائیں: pip install SpeechRecognition",
        "no_hear": "آواز سمجھ نہیں آئی۔ دوبارہ صاف بولیں یا خود لکھ دیں۔",
        "making": "آواز تیار ہو رہی ہے...", "pip_tts": "پہلے یہ چلائیں: pip install gTTS", "need_net": "آواز بنانے کے لیے انٹرنیٹ چاہیے۔",
        "ai_off": "ℹ️ AI (Claude/Gemini) بند ہے۔ ",
        "help_key": "پروجیکٹ فولڈر میں .env فائل بنا کر GEMINI_API_KEY (مفت) یا ANTHROPIC_API_KEY لکھیں۔",
        "help_pkg": "یہ چلائیں: pip install anthropic", "help_other": "انٹرنیٹ یا API key چیک کریں۔",
        "ai_off_end": " ابھی رولز، ML ماڈل اور ہوم کیئر انجن کام کر رہے ہیں۔",
        "foot": "⚠️ یہ تجرباتی نمونہ ہے، طبی تصدیق نہیں ہوئی۔ صرف فرضی ڈیٹا استعمال کریں۔",
        "male": "لڑکا / مرد", "female": "لڑکی / عورت",
    },
    "en": {
        "settings": "### ⚙️ Settings", "lang": "زبان / Language", "new": "➕ New patient",
        "today": "### 🕘 Today's patients", "no_hist": "No records yet.", "clear": "🗑️ Clear records",
        "age": "👤 Age", "age_ph": "e.g. child, 2 years old", "gender": "⚧ Gender",
        "tap": "**👆 Tap common symptoms** (you can pick several)", "symp": "Symptoms",
        "speak": "**🎤 Or speak** (in Urdu, internet needed)", "mic": "Press the mic to speak",
        "type": "✍️ Or type (Urdu, Roman Urdu or English)", "type_ph": "e.g. high fever and diarrhea for 3 days",
        "check": "🔍 Check", "enter": "Please type symptoms or pick them above.",
        "listen": "🔊 Listen to the result", "more": "🩺 More questions",
        "more_cap": "The AI is asking a few things to improve the decision. Answer and check again.",
        "yn": "Yes / No / details", "again": "✅ Check again with answers",
        "tech": "🔬 Technical details (for judges)", "dl": "📄 Download slip (print / show at hospital)",
        "spin": "Assessing...", "emerg": "Emergency! Go to hospital immediately",
        "noserver": "Could not reach the server. Is the backend running?",
        "writing": "Transcribing speech...", "pip_sr": "First run: pip install SpeechRecognition",
        "no_hear": "Could not understand. Speak clearly again or type it.",
        "making": "Preparing audio...", "pip_tts": "First run: pip install gTTS", "need_net": "Internet is needed for audio.",
        "ai_off": "ℹ️ AI (Claude/Gemini) is off. ",
        "help_key": "Create a .env file in the project folder with GEMINI_API_KEY (free) or ANTHROPIC_API_KEY.",
        "help_pkg": "Run: pip install anthropic", "help_other": "Check your internet or API key.",
        "ai_off_end": " Rules, the ML model and the home-care engine are still working.",
        "foot": "⚠️ Experimental prototype, not medically validated. Use fake data only.",
        "male": "Boy / Man", "female": "Girl / Woman",
    },
}

# (id, Urdu label, English label, text sent to backend)
QUICK = [
    ("fever", "🤒 تیز بخار", "🤒 High fever", "تیز بخار"),
    ("cold", "🤧 زکام / کھانسی", "🤧 Cold / cough", "زکام اور کھانسی"),
    ("vomit", "🤮 الٹی", "🤮 Vomiting", "بار بار الٹی"),
    ("diar", "💧 دست", "💧 Diarrhea", "دست"),
    ("head", "🤕 سر درد", "🤕 Headache", "سر درد"),
    ("breath", "😮‍💨 سانس کی تکلیف", "😮‍💨 Breathing trouble", "سانس نہیں آ رہی"),
    ("faint", "😵 بے ہوشی / جھٹکے", "😵 Fainting / fits", "بے ہوش اور جھٹکے"),
    ("bleed", "🩸 خون آنا", "🩸 Bleeding", "خون آ رہا ہے"),
    ("preg", "🤰 حمل", "🤰 Pregnancy", "حمل"),
    ("milk", "🍼 دودھ نہیں پی رہا", "🍼 Not feeding", "دودھ نہیں پی رہا"),
    ("poison", "☠️ زہر", "☠️ Poison", "زہر کھا لیا"),
]
QUICK_TEXT = {q[0]: q[3] for q in QUICK}

LEVEL_ICON = {"emergency": "🔴", "urgent": "🟠", "home": "🟢"}


def render_html(html: str, height: int):
    """Render an HTML/SVG block (iframe so animations + fonts always work)."""
    try:
        import streamlit.components.v1 as components
        components.html(html, height=height)
    except Exception:
        st.markdown(html, unsafe_allow_html=True)


def transcribe_urdu(wav_bytes: bytes) -> str:
    """Urdu speech -> text (Google free web speech, needs internet). pip install SpeechRecognition"""
    import speech_recognition as sr
    rec = sr.Recognizer()
    with sr.AudioFile(io.BytesIO(wav_bytes)) as src:
        audio = rec.record(src)
    return rec.recognize_google(audio, language="ur-PK")


def speak(text: str, lang: str) -> bytes:
    """Text -> speech mp3 (needs internet). pip install gTTS"""
    from gtts import gTTS
    fp = io.BytesIO()
    gTTS(text, lang=lang).write_to_fp(fp)
    return fp.getvalue()


def new_patient():
    for k in ("typed", "result", "last_input"):
        st.session_state.pop(k, None)
    st.session_state["typed"] = ""
    for k in [k for k in st.session_state if str(k).startswith("fu_")]:
        st.session_state.pop(k, None)


# ---------------------------------------------------------------- sidebar (language FIRST)
with st.sidebar:
    lang_label = st.radio("زبان / Language", ["اردو", "English"], horizontal=True, key="lang_choice")
    out_lang = "ur" if lang_label == "اردو" else "en"
    T = TR[out_lang]
    st.markdown(T["settings"])
    st.button(T["new"], on_click=new_patient, use_container_width=True)
    st.markdown(T["today"])
    hist = st.session_state.get("history", [])
    if not hist:
        st.caption(T["no_hist"])
    for h in reversed(hist[-8:]):
        st.markdown(f"{LEVEL_ICON[h['level']]} **{h['time']}** — {h['text']}")
    if hist and st.button(T["clear"], use_container_width=True):
        st.session_state["history"] = []
        st.rerun()

RTL = out_lang == "ur"
DIR, ALIGN = ("rtl", "right") if RTL else ("ltr", "left")

# ---------------------------------------------------------------- page style
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;600;700&display=swap');
html, body, [class*="css"], .stApp, textarea, input, button, label, p, h1, h2, h3, li {
    font-family: 'Noto Naskh Arabic', 'Jameel Noori Nastaleeq', 'Segoe UI', Tahoma, serif !important;
}
.stApp { direction: __DIR__; text-align: __ALIGN__;
         background: linear-gradient(180deg, #f0fdfa 0%, #ffffff 40%); }
header[data-testid="stHeader"] { background: transparent; }
textarea, input { direction: __DIR__; text-align: __ALIGN__; font-size: 1.15rem !important; border-radius: 14px !important; }
label, .stMarkdown, p { text-align: __ALIGN__; }
div.stButton > button[kind="primary"] {
    width: 100%; font-size: 1.3rem; padding: .6rem 1rem; border-radius: 16px; border: none;
    background: linear-gradient(135deg, #0ea5a4, #2563eb); color: #fff; font-weight: 700;
    box-shadow: 0 6px 18px #2563eb44; transition: transform .15s;
}
div.stButton > button[kind="primary"]:hover { transform: translateY(-2px) scale(1.01); }
.hint { color:#6b7280; font-size:.95rem; margin:-.3rem 0 .6rem 0; }
</style>
""".replace("__DIR__", DIR).replace("__ALIGN__", ALIGN), unsafe_allow_html=True)

# ---------------------------------------------------------------- hero banner
render_html(hero_html(), 235)

# ---------------------------------------------------------------- input form
col1, col2 = st.columns(2)
age = col1.text_input(T["age"], placeholder=T["age_ph"])
gender = col2.selectbox(T["gender"], ["لڑکا / مرد", "لڑکی / عورت"],
                        format_func=lambda v: T["male"] if v == "لڑکا / مرد" else T["female"])

st.markdown(T["tap"])
label_of = {q[0]: (q[1] if RTL else q[2]) for q in QUICK}
try:
    picked = st.pills(T["symp"], [q[0] for q in QUICK], selection_mode="multi",
                      format_func=lambda k: label_of[k], label_visibility="collapsed")
except Exception:
    picked = st.multiselect(T["symp"], [q[0] for q in QUICK], format_func=lambda k: label_of[k],
                            label_visibility="collapsed")
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


def run_check(age_, gender_, symptoms_, followup=None, record=True):
    try:
        with st.spinner(T["spin"]):
            r = requests.post(API_URL, json={"age": age_, "gender": gender_, "symptoms": symptoms_,
                                             "output_language": out_lang,
                                             "followup": followup or []}, timeout=60)
            r.raise_for_status()
            st.session_state["result"] = r.json()
            st.session_state["last_input"] = (age_, gender_, symptoms_)
            if record:
                st.session_state.setdefault("history", []).append({
                    "time": datetime.datetime.now().strftime("%H:%M"),
                    "text": symptoms_[:40] + ("…" if len(symptoms_) > 40 else ""),
                    "level": st.session_state["result"]["triage_level"]})
        if st.session_state["result"]["triage_level"] == "emergency":
            st.toast(T["emerg"], icon="🚨")
        return True
    except Exception as e:
        st.error(f"{T['noserver']} ({e})")
        return False


if st.button(T["check"], type="primary"):
    if not symptoms:
        st.warning(T["enter"])
    else:
        run_check(age, gender, symptoms)

# ---------------------------------------------------------------- language switched after a result? redo it
res = st.session_state.get("result")
if res and res.get("language") != out_lang and st.session_state.get("last_input"):
    a0, g0, s0 = st.session_state["last_input"]
    if run_check(a0, g0, s0, record=False):
        st.rerun()

# ---------------------------------------------------------------- result
res = st.session_state.get("result")
if res:
    render_html(result_html(res), result_height(res))
    if res.get("care"):
        render_html(care_html(res), care_height(res))
    if st.button(T["listen"]):
        care = res.get("care") or {}
        say = " ۔ ".join([res["title"], res["message"], res.get("reasoning", "")] + res["steps"]
                         + care.get("tips", [])[:3])
        try:
            with st.spinner(T["making"]):
                st.audio(speak(say, res["language"]), format="audio/mp3", autoplay=True)
        except ImportError:
            st.error(T["pip_tts"])
        except Exception:
            st.warning(T["need_net"])
    if res.get("follow_ups"):
        st.subheader(T["more"])
        st.caption(T["more_cap"])
        with st.form("followup"):
            answers = [st.text_input(q, key=f"fu_{i}", placeholder=T["yn"])
                       for i, q in enumerate(res["follow_ups"])]
            again = st.form_submit_button(T["again"])
        if again:
            fu = [{"q": q, "a": x} for q, x in zip(res["follow_ups"], answers) if x.strip()]
            a0, g0, s0 = st.session_state["last_input"]
            if run_check(a0, g0, s0, fu, record=False):
                st.rerun()
    elif not res.get("llm_used"):
        why = (res.get("llm_status") or {}).get("reason", "")
        help_txt = {"no_api_key": T["help_key"], "anthropic_package_missing": T["help_pkg"]}.get(why, T["help_other"])
        st.caption(T["ai_off"] + help_txt + T["ai_off_end"])
        looked = (res.get("llm_status") or {}).get("looked_in")
        if why == "no_api_key" and looked:
            st.code(("Backend ne .env yahan dhoondi:\n" if RTL else "The backend looked for .env here:\n") + "\n".join(looked))
    with st.expander(T["tech"]):
        st.json({
            "language": res["language"],
            "final_level": res["triage_level"],
            "ml_level": res["ml_level"],
            "ml_probabilities": res.get("ml_probs"),
            "llm_used": res.get("llm_used"),
            "llm_level": res.get("llm_level"),
            "red_flag_rules_triggered": res["red_flags_found"],
            "profile": res.get("profile"),
            "escalation_reasons": res.get("escalation_reasons"),
            "medicine_ids_shown": [m["id"] for m in (res.get("care") or {}).get("medicines", [])],
            "ai_status": res.get("llm_status"),
        })

    a1, g1, s1 = st.session_state.get("last_input", ("", "", ""))
    st.download_button(T["dl"],
                       data=report_html(res, a1, g1, s1, datetime.datetime.now().strftime("%d-%m-%Y %H:%M")),
                       file_name="sehatsathi_parchi.html", mime="text/html")

st.divider()
st.caption(T["foot"])
