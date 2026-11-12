# -*- coding: utf-8 -*-
"""HTML/SVG building blocks for the SehatSathi UI (no Streamlit needed, so they can be tested alone)."""
import html as _h

FONT_LINK = ("<link href='https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;600;700"
             "&display=swap' rel='stylesheet'>")
BASE_CSS = """
*{box-sizing:border-box}
body{margin:0;font-family:'Noto Naskh Arabic','Jameel Noori Nastaleeq','Segoe UI',Tahoma,sans-serif;background:transparent}
"""

COLORS = {"emergency": "#e53935", "urgent": "#fb8c00", "home": "#43a047"}
SOFT = {"emergency": "#fdecea", "urgent": "#fff4e0", "home": "#e8f5e9"}

# ------------------------------------------------------------------ hero banner
def hero_html() -> str:
    svg = """
<svg viewBox="0 0 900 250" xmlns="http://www.w3.org/2000/svg" style="width:100%;display:block;border-radius:22px">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0ea5a4"/><stop offset="1" stop-color="#2563eb"/></linearGradient>
    <linearGradient id="hill1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#34d399"/><stop offset="1" stop-color="#059669"/></linearGradient>
  </defs>
  <rect width="900" height="250" fill="url(#sky)"/>
  <circle cx="90" cy="60" r="34" fill="#fde68a"><animate attributeName="r" values="34;38;34" dur="4s" repeatCount="indefinite"/></circle>
  <g fill="#fff" opacity=".85">
    <ellipse cx="250" cy="48" rx="44" ry="14"><animateTransform attributeName="transform" type="translate" values="0 0;30 0;0 0" dur="14s" repeatCount="indefinite"/></ellipse>
    <ellipse cx="285" cy="38" rx="28" ry="12"><animateTransform attributeName="transform" type="translate" values="0 0;30 0;0 0" dur="14s" repeatCount="indefinite"/></ellipse>
    <ellipse cx="520" cy="30" rx="36" ry="11"><animateTransform attributeName="transform" type="translate" values="0 0;-26 0;0 0" dur="16s" repeatCount="indefinite"/></ellipse>
  </g>
  <path d="M0 190 Q150 130 320 180 T640 170 T900 175 V250 H0Z" fill="url(#hill1)"/>
  <path d="M0 220 Q200 180 420 215 T900 205 V250 H0Z" fill="#047857"/>
  <!-- village houses -->
  <g>
    <rect x="40" y="170" width="70" height="50" fill="#fef3c7"/><polygon points="32,172 75,135 118,172" fill="#b45309"/>
    <rect x="62" y="190" width="18" height="30" fill="#92400e"/><rect x="88" y="185" width="14" height="14" fill="#60a5fa"/>
    <rect x="150" y="178" width="60" height="42" fill="#fde68a"/><polygon points="143,180 180,148 217,180" fill="#dc2626"/>
    <rect x="170" y="196" width="16" height="24" fill="#92400e"/>
    <circle cx="250" cy="185" r="22" fill="#16a34a"/><rect x="247" y="195" width="6" height="26" fill="#78350f"/>
    <circle cx="275" cy="195" r="16" fill="#22c55e"/><rect x="273" y="203" width="5" height="18" fill="#78350f"/>
  </g>
  <!-- health clinic with cross -->
  <g>
    <rect x="320" y="150" width="96" height="70" fill="#fff"/><polygon points="312,152 368,112 424,152" fill="#ef4444"/>
    <rect x="352" y="188" width="32" height="32" fill="#bfdbfe"/>
        <g transform="translate(368 150)"><rect x="-4" y="-16" width="8" height="32" rx="2" fill="#ef4444"/><rect x="-16" y="-4" width="32" height="8" rx="2" fill="#ef4444"/></g>
  </g>
  <!-- big heart + ECG -->
  <g transform="translate(455 92) scale(.85)">
    <path d="M0 40 C-60 -10 -30 -50 0 -20 C30 -50 60 -10 0 40Z" fill="#fff" opacity=".95">
      <animateTransform attributeName="transform" type="scale" values="1;1.08;1" dur="1.2s" repeatCount="indefinite" additive="sum"/>
    </path>
    <path d="M-70 8 H-30 L-18 -18 L-2 34 L12 -8 L22 8 H70" fill="none" stroke="#ef4444" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"
          stroke-dasharray="260" stroke-dashoffset="260"><animate attributeName="stroke-dashoffset" values="260;0;0;260" keyTimes="0;.5;.8;1" dur="2.4s" repeatCount="indefinite"/></path>
  </g>
  <!-- title -->
  <text x="870" y="105" text-anchor="end" font-size="52" font-weight="700" fill="#fff" style="font-family:'Noto Naskh Arabic','Segoe UI',serif">صحت ساتھی</text>
  <text x="870" y="150" text-anchor="end" font-size="21" fill="#e0f2fe" style="font-family:'Noto Naskh Arabic','Segoe UI',serif">صحیح وقت پر صحیح فیصلہ</text>
  <g transform="translate(870 190)" text-anchor="end" font-size="15" fill="#fff" style="font-family:'Noto Naskh Arabic','Segoe UI',serif">
    <rect x="-300" y="-20" width="300" height="32" rx="16" fill="#ffffff" opacity=".18"/>
    <text x="-14" y="2">اردو  •  رومن اردو  •  English</text>
  </g>
</svg>"""
    return f"<!doctype html><html><head><meta charset='utf-8'>{FONT_LINK}<style>{BASE_CSS}</style></head><body>{svg}</body></html>"

# ------------------------------------------------------------------ level illustrations
def _illustration(level: str) -> str:
    if level == "emergency":
        return """
<svg viewBox="0 0 160 110" width="150" xmlns="http://www.w3.org/2000/svg">
  <rect x="8" y="26" width="92" height="52" rx="8" fill="#fff" stroke="#cbd5e1" stroke-width="2"/>
  <path d="M100 40 H128 L148 60 V78 H100Z" fill="#fff" stroke="#cbd5e1" stroke-width="2"/>
  <path d="M110 46 H126 L140 60 H110Z" fill="#bfdbfe"/>
  <rect x="8" y="58" width="140" height="8" fill="#e53935"/>
  <g transform="translate(54 44)"><rect x="-4" y="-13" width="8" height="26" rx="2" fill="#e53935"/><rect x="-13" y="-4" width="26" height="8" rx="2" fill="#e53935"/></g>
  <g fill="#334155"><circle cx="36" cy="82" r="13"/><circle cx="118" cy="82" r="13"/></g><g fill="#cbd5e1"><circle cx="36" cy="82" r="5"/><circle cx="118" cy="82" r="5"/></g>
  <rect x="44" y="14" width="24" height="12" rx="5" fill="#e53935"><animate attributeName="fill" values="#e53935;#3b82f6;#e53935" dur=".8s" repeatCount="indefinite"/></rect>
  <g stroke="#e53935" stroke-width="3" stroke-linecap="round" opacity=".7"><path d="M38 8 L32 2"><animate attributeName="opacity" values="1;0;1" dur=".8s" repeatCount="indefinite"/></path><path d="M74 8 L80 2"><animate attributeName="opacity" values="0;1;0" dur=".8s" repeatCount="indefinite"/></path></g>
</svg>"""
    if level == "urgent":
        return """
<svg viewBox="0 0 160 110" width="150" xmlns="http://www.w3.org/2000/svg">
  <rect x="26" y="34" width="108" height="64" rx="4" fill="#fff" stroke="#fed7aa" stroke-width="3"/>
  <rect x="18" y="26" width="124" height="12" rx="3" fill="#fb8c00"/>
  <g transform="translate(80 12)"><rect x="-4" y="-10" width="8" height="20" rx="2" fill="#fb8c00"><animate attributeName="opacity" values="1;.4;1" dur="1.4s" repeatCount="indefinite"/></rect><rect x="-10" y="-4" width="20" height="8" rx="2" fill="#fb8c00"><animate attributeName="opacity" values="1;.4;1" dur="1.4s" repeatCount="indefinite"/></rect></g>
  <rect x="68" y="62" width="24" height="36" fill="#fdba74"/><circle cx="87" cy="80" r="2" fill="#fff"/>
  <rect x="38" y="48" width="20" height="18" fill="#bfdbfe"/><rect x="102" y="48" width="20" height="18" fill="#bfdbfe"/>
  <rect x="10" y="98" width="140" height="6" rx="3" fill="#fde0b8"/>
</svg>"""
    return """
<svg viewBox="0 0 160 110" width="150" xmlns="http://www.w3.org/2000/svg">
  <polygon points="80,10 138,52 22,52" fill="#16a34a"/>
  <rect x="34" y="52" width="92" height="46" fill="#fff" stroke="#bbf7d0" stroke-width="3"/>
  <rect x="68" y="66" width="24" height="32" rx="2" fill="#86efac"/>
  <rect x="42" y="62" width="18" height="16" fill="#bfdbfe"/><rect x="100" y="62" width="18" height="16" fill="#bfdbfe"/>
  <g transform="translate(80 36)"><path d="M0 8 C-14 -4 -8 -14 0 -6 C8 -14 14 -4 0 8Z" fill="#fff"><animateTransform attributeName="transform" type="scale" values="1;1.2;1" dur="1.3s" repeatCount="indefinite"/></path></g>
  <circle cx="18" cy="88" r="12" fill="#22c55e"/><rect x="16" y="94" width="4" height="12" fill="#78350f"/>
  <rect x="8" y="98" width="144" height="6" rx="3" fill="#bbf7d0"/>
</svg>"""

# ------------------------------------------------------------------ gauge + bars
def _gauge(conf: float, color: str) -> str:
    r = 52
    c = 2 * 3.14159265 * r
    off = c * (1 - conf)
    return f"""
<svg viewBox="0 0 140 140" width="150" xmlns="http://www.w3.org/2000/svg">
  <circle cx="70" cy="70" r="{r}" fill="none" stroke="#e5e7eb" stroke-width="13"/>
  <circle cx="70" cy="70" r="{r}" fill="none" stroke="{color}" stroke-width="13" stroke-linecap="round"
          stroke-dasharray="{c:.1f}" style="--off:{off:.1f};stroke-dashoffset:{c:.1f};animation:fill 1.4s ease-out forwards"
          transform="rotate(-90 70 70)"/>
  <text id="pct" x="70" y="78" text-anchor="middle" font-size="30" font-weight="700" fill="{color}">0%</text>
</svg>"""

LABELS = {
    "ur": {"emergency": "ہنگامی", "urgent": "جلد ڈاکٹر", "home": "گھر پر",
           "conf": "ماڈل کا اعتماد", "note": "یہ ماڈل کا اپنا اعتماد ہے، حتمی درستگی نہیں",
           "why": "وجہ (Claude AI)", "next": "اگلا قدم", "flags": "⚠️ خطرے کے نشان ملے", "ml": "ایم ایل کا فیصلہ"},
    "en": {"emergency": "Emergency", "urgent": "Urgent", "home": "Home care",
           "conf": "Model confidence", "note": "The model's own confidence, not final accuracy",
           "why": "Why (Claude AI)", "next": "Next steps", "flags": "⚠️ Danger signs found", "ml": "ML decision"},
}

def result_height(d: dict) -> int:
    return (700 + (70 if d.get("red_flags_found") else 0) + 28 * max(0, len(d["steps"]) - 3)
            + (150 if d.get("reasoning") else 0))

def result_html(d: dict) -> str:
    lang = d["language"]
    L = LABELS[lang]
    rtl = lang == "ur"
    level = d["triage_level"]
    col = COLORS[level]
    ml_col = COLORS[d["ml_level"]]
    conf = float(d["ml_confidence"])
    probs = d.get("ml_probs") or {k: 0 for k in COLORS}

    bars = ""
    for k in ["emergency", "urgent", "home"]:
        pct = round(probs.get(k, 0) * 100)
        bars += (f"<div class='bar'><span class='bl'>{L[k]}</span>"
                 f"<div class='track'><div class='fillbar' style='--w:{pct}%;background:{COLORS[k]}'></div></div>"
                 f"<span class='bp'>{pct}%</span></div>")

    steps = "".join(f"<div class='step'><div class='num' style='background:{col}'>{i}</div>"
                    f"<div class='stxt'>{_h.escape(s)}</div></div>" for i, s in enumerate(d["steps"], 1))
    flags = ""
    if d.get("red_flags_found"):
        chips = "".join(f"<span class='chip'>{_h.escape(f)}</span>" for f in d["red_flags_found"])
        flags = f"<div class='sec'>{L['flags']}</div><div class='chips'>{chips}</div>"

    ai_block = ""
    if d.get("reasoning"):
        ai_block = (f"<div class='ai'><div class='aih'>🧠 {L['why']}</div>"
                    f"<div class='ait'>{_h.escape(d['reasoning'])}</div></div>")
    pulse = "pulse" if level == "emergency" else ""
    css = f"""
{BASE_CSS}
body{{direction:{'rtl' if rtl else 'ltr'};text-align:{'right' if rtl else 'left'};padding:6px}}
@keyframes fill{{to{{stroke-dashoffset:var(--off)}}}}
@keyframes grow{{from{{width:0}}to{{width:var(--w)}}}}
@keyframes rise{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}
@keyframes glow{{0%,100%{{box-shadow:0 0 0 0 {col}66}}50%{{box-shadow:0 0 0 14px {col}00}}}}
.card{{background:#fff;border-radius:22px;border:2px solid {col}33;box-shadow:0 8px 28px #0000001a;overflow:hidden;animation:rise .6s ease-out}}
.pulse{{animation:rise .6s ease-out,glow 1.6s infinite}}
.head{{background:linear-gradient(135deg,{SOFT[level]},#fff);display:flex;align-items:center;gap:18px;padding:18px 22px;border-bottom:2px solid {col}22}}
.title{{font-size:34px;font-weight:700;color:{col};line-height:1.3}}
.msg{{font-size:19px;color:#374151;margin-top:4px;line-height:1.7}}
.row{{display:flex;align-items:center;gap:22px;padding:18px 22px;flex-wrap:wrap}}
.gwrap{{position:relative;text-align:center}}
.gl{{font-weight:700;color:#374151;font-size:16px}}
.gn{{font-size:12px;color:#6b7280;max-width:190px;margin:2px auto 0}}
.bars{{flex:1;min-width:230px}}
.bar{{display:flex;align-items:center;gap:10px;margin:9px 0;font-size:15px;color:#374151}}
.bl{{width:92px;font-weight:600}}.bp{{width:42px;font-weight:700}}
.track{{flex:1;height:14px;background:#eef0f3;border-radius:9px;overflow:hidden}}
.fillbar{{height:100%;border-radius:9px;width:0;animation:grow 1.2s .2s ease-out forwards}}
.mltag{{display:inline-block;margin-bottom:6px;padding:3px 12px;border-radius:14px;background:{ml_col}22;color:{ml_col};font-weight:700;font-size:14px}}
.sec{{padding:6px 22px 0;font-size:20px;font-weight:700;color:#1f2937}}
.step{{display:flex;align-items:center;gap:14px;margin:10px 22px;padding:12px 14px;background:{SOFT[level]};border-radius:14px;animation:rise .6s ease-out both}}
.step:nth-of-type(2){{animation-delay:.15s}}.step:nth-of-type(3){{animation-delay:.3s}}
.num{{min-width:34px;height:34px;border-radius:50%;color:#fff;font-weight:700;display:flex;align-items:center;justify-content:center}}
.stxt{{font-size:18px;color:#1f2937;line-height:1.7}}
.chips{{padding:6px 22px 14px;display:flex;flex-wrap:wrap;gap:8px}}
.chip{{background:#fee2e2;color:#b91c1c;padding:6px 14px;border-radius:16px;font-weight:700;font-size:15px}}
.ai{{margin:2px 22px 8px;padding:14px 16px;background:#f5f3ff;border:1px solid #ddd6fe;border-radius:14px}}
.aih{{font-weight:700;color:#5b21b6;font-size:17px;margin-bottom:4px}}
.ait{{font-size:18px;color:#1f2937;line-height:1.8}}
.foot{{padding:10px 22px 16px;font-size:13px;color:#6b7280}}
"""
    js = f"""
<script>
(function(){{var el=document.getElementById('pct'),t={round(conf*100)},n=0;
var iv=setInterval(function(){{n+=2;if(n>=t){{n=t;clearInterval(iv)}}el.textContent=n+'%'}},22)}})();
</script>"""
    return f"""<!doctype html><html><head><meta charset='utf-8'>{FONT_LINK}<style>{css}</style></head><body>
<div class='card {pulse}'>
  <div class='head'>{_illustration(level)}<div><div class='title'>{_h.escape(d['title'])}</div><div class='msg'>{_h.escape(d['message'])}</div></div></div>
  <div class='row'>
    <div class='gwrap'>{_gauge(conf, ml_col)}<div class='gl'>{L['conf']}</div><div class='gn'>{L['note']}</div></div>
    <div class='bars'><span class='mltag'>{L['ml']}: {L[d['ml_level']]}</span>{bars}</div>
  </div>
  {ai_block}
  <div class='sec'>{L['next']}</div>
  {steps}
  {flags}
  <div class='foot'>{_h.escape(d['disclaimer'])}</div>
</div>{js}</body></html>"""


# ================================================================== v3: home-care card
CARE_LABELS = {
    "ur": {
        "title_home": "🏠 گھر پر دیکھ بھال",
        "title_interim": "🚑 ڈاکٹر تک پہنچنے سے پہلے",
        "why_up": "⏱️ فیصلہ سخت کیوں ہوا",
        "detected": "🔎 پہچانی گئی علامات",
        "causes": "💡 ممکنہ وجوہات (یہ تشخیص نہیں)",
        "tips": "✅ کیا کریں",
        "meds": "💊 عام دوا کی تجویز (بغیر نسخے کی)",
        "meds_hint": "مقدار ہمیشہ پیکٹ پر لکھی ہدایت یا فارماسسٹ سے لیں۔ یہ ڈاکٹر کے نسخے کا متبادل نہیں۔",
        "avoid": "🚫 کیا نہ کریں",
        "doctor": "⚠️ ان صورتوں میں فوراً ڈاکٹر کے پاس جائیں",
        "how": "کیسے", "caution": "احتیاط",
        "no_med": "ℹ️ دوا کے بارے میں",
    },
    "en": {
        "title_home": "🏠 Home care",
        "title_interim": "🚑 Until you reach a doctor",
        "why_up": "⏱️ Why the advice was raised",
        "detected": "🔎 Symptoms recognised",
        "causes": "💡 Possible causes (not a diagnosis)",
        "tips": "✅ What to do",
        "meds": "💊 Common over-the-counter options",
        "meds_hint": "Always follow the pack instructions or ask a pharmacist for the amount. Not a substitute for a prescription.",
        "avoid": "🚫 What not to do",
        "doctor": "⚠️ Go to a doctor immediately if",
        "how": "How", "caution": "Caution",
        "no_med": "ℹ️ About medicines",
    },
}


def care_height(d: dict) -> int:
    c = d.get("care")
    if not c:
        return 0
    lines = (len(c["tips"]) + len(c["avoid"]) + len(c["see_doctor_if"]) + len(c.get("medicines_note", []))
             + len(d.get("escalation_reasons", [])) + len(d.get("ai_causes", [])) + len(d.get("ai_tips", [])))
    return int(330 + lines * 58 + len(c["medicines"]) * 215)


def _li(items, cls=""):
    return "".join(f"<li class='{cls}'>{_h.escape(x)}</li>" for x in items)


def care_html(d: dict) -> str:
    c = d.get("care")
    if not c:
        return ""
    lang = d["language"]
    L = CARE_LABELS[lang]
    rtl = lang == "ur"
    interim = c["mode"] == "interim"
    col = "#fb8c00" if interim else "#43a047"

    parts = []
    if d.get("escalation_reasons"):
        parts.append(f"<div class='warn'><b>{L['why_up']}</b><ul>{_li(d['escalation_reasons'])}</ul></div>")

    chips = "".join(f"<span class='chip'>{_h.escape(s['label'])}</span>" for s in c["symptoms"])
    parts.append(f"<div class='sh'>{L['detected']}</div><div class='chips'>{chips}</div>")

    if d.get("ai_causes"):
        parts.append(f"<div class='sh'>{L['causes']}</div><ul class='ul'>{_li(d['ai_causes'])}</ul>")

    tips = list(c["tips"]) + list(d.get("ai_tips", []))
    if tips:
        parts.append(f"<div class='sh'>{L['tips']}</div><ul class='ul tip'>{_li(tips)}</ul>")

    if c["medicines"]:
        cards = ""
        for m in c["medicines"]:
            cards += (f"<div class='med'><div class='mn'>{_h.escape(m['name'])}</div>"
                      f"<div class='mf'>{_h.escape(m['for'])}</div>"
                      f"<div class='mr'><b>{L['how']}:</b> {_h.escape(m['how'])}</div>"
                      f"<div class='mr c'><b>{L['caution']}:</b> {_h.escape(m['caution'])}</div></div>")
        parts.append(f"<div class='sh'>{L['meds']}</div><div class='mh'>{L['meds_hint']}</div>{cards}")
    if c.get("medicines_note"):
        parts.append(f"<div class='info'><b>{L['no_med']}</b><ul>{_li(c['medicines_note'])}</ul></div>")

    parts.append(f"<div class='sh'>{L['avoid']}</div><ul class='ul bad'>{_li(c['avoid'])}</ul>")
    parts.append(f"<div class='doc'><b>{L['doctor']}</b><ul>{_li(c['see_doctor_if'])}</ul></div>")

    css = f"""
{BASE_CSS}
body{{direction:{'rtl' if rtl else 'ltr'};text-align:{'right' if rtl else 'left'};padding:6px}}
@keyframes rise{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}
.card{{background:#fff;border-radius:22px;border:2px solid {col}33;box-shadow:0 8px 28px #0000001a;overflow:hidden;animation:rise .6s ease-out}}
.top{{background:linear-gradient(135deg,{'#fff4e0' if interim else '#e8f5e9'},#fff);padding:16px 22px;border-bottom:2px solid {col}22;
      font-size:28px;font-weight:700;color:{col}}}
.body{{padding:6px 22px 18px}}
.sh{{font-size:20px;font-weight:700;color:#1f2937;margin:16px 0 6px}}
.chips{{display:flex;flex-wrap:wrap;gap:8px}}
.chip{{background:#e0f2fe;color:#075985;padding:5px 14px;border-radius:16px;font-weight:700;font-size:15px}}
.ul{{margin:4px 0;padding-{'right' if rtl else 'left'}:22px;font-size:18px;line-height:1.8;color:#1f2937}}
.ul.tip li::marker{{color:#16a34a}} .ul.bad li::marker{{color:#dc2626}}
.med{{background:#f0fdf4;border:1px solid #bbf7d0;border-radius:16px;padding:12px 16px;margin:10px 0}}
.mn{{font-size:21px;font-weight:700;color:#166534}} .mf{{font-size:16px;color:#374151;margin:2px 0 6px}}
.mr{{font-size:16px;color:#1f2937;line-height:1.7}} .mr.c{{color:#92400e}}
.mh{{font-size:14px;color:#b45309;background:#fffbeb;border-radius:10px;padding:6px 12px;margin-bottom:4px}}
.warn{{background:#fff7ed;border:1px solid #fdba74;border-radius:14px;padding:10px 16px;margin:12px 0;font-size:17px;color:#9a3412}}
.info{{background:#eff6ff;border:1px solid #bfdbfe;border-radius:14px;padding:10px 16px;margin:10px 0;font-size:16px;color:#1e3a8a}}
.doc{{background:#fef2f2;border:1px solid #fecaca;border-radius:14px;padding:10px 16px;margin:16px 0 0;font-size:17px;color:#991b1b}}
.warn ul,.info ul,.doc ul{{margin:4px 0;padding-{'right' if rtl else 'left'}:20px;line-height:1.8}}
"""
    title = L["title_interim"] if interim else L["title_home"]
    return (f"<!doctype html><html><head><meta charset='utf-8'>{FONT_LINK}<style>{css}</style></head><body>"
            f"<div class='card'><div class='top'>{title}</div><div class='body'>{''.join(parts)}</div></div></body></html>")


# ================================================================== v3: printable referral slip
def report_html(d: dict, age: str, gender: str, symptoms: str, when: str) -> str:
    """Download hone wali parchi (browser mein Print -> PDF). Hospital/BHU ko dikhane ke liye."""
    lang = d["language"]
    rtl = lang == "ur"
    T = {
        "ur": ("صحت ساتھی - ابتدائی جائزہ پرچی", "تاریخ", "عمر", "جنس", "علامات", "نتیجہ",
               "خطرے کے نشان", "وجہ", "اگلے قدم", "گھر پر دیکھ بھال", "دوا (عام، بغیر نسخے)", "ڈاکٹر کو دکھانے کی علامات"),
        "en": ("SehatSathi - Preliminary Assessment Slip", "Date", "Age", "Gender", "Symptoms", "Result",
               "Danger signs", "Reason", "Next steps", "Home care", "Medicines (common, OTC)", "See a doctor if"),
    }[lang]
    col = COLORS[d["triage_level"]]
    e = _h.escape

    def sec(title, items):
        if not items:
            return ""
        return f"<h3>{e(title)}</h3><ul>{''.join(f'<li>{e(x)}</li>' for x in items)}</ul>"

    c = d.get("care") or {}
    meds = [f"{m['name']} - {m['for']}. {m['how']}" for m in c.get("medicines", [])]
    rows = "".join(f"<tr><th>{e(k)}</th><td>{e(v)}</td></tr>" for k, v in
                   [(T[1], when), (T[2], age or "-"), (T[3], gender or "-"), (T[4], symptoms)])
    return f"""<!doctype html><html><head><meta charset='utf-8'><title>{e(T[0])}</title>{FONT_LINK}
<style>body{{font-family:'Noto Naskh Arabic','Segoe UI',Tahoma,sans-serif;max-width:760px;margin:24px auto;padding:0 18px;
direction:{'rtl' if rtl else 'ltr'};color:#111}}
h1{{font-size:26px;border-bottom:3px solid {col};padding-bottom:8px}} h3{{margin:18px 0 4px;color:#1f2937}}
table{{border-collapse:collapse;width:100%}} th,td{{border:1px solid #d1d5db;padding:6px 10px;text-align:{'right' if rtl else 'left'}}}
th{{background:#f3f4f6;width:22%}} .lvl{{display:inline-block;background:{col};color:#fff;padding:6px 20px;border-radius:20px;font-size:22px;font-weight:700;margin:12px 0}}
.dis{{margin-top:24px;font-size:13px;color:#6b7280;border-top:1px solid #e5e7eb;padding-top:8px}}
@media print{{body{{margin:0}}}}</style></head><body>
<h1>🩺 {e(T[0])}</h1><table>{rows}</table>
<div class='lvl'>{e(T[5])}: {e(d['title'])}</div><p>{e(d['message'])}</p>
{sec(T[6], d.get('red_flags_found', []))}{sec(T[7], [d['reasoning']] if d.get('reasoning') else [])}
{sec(T[8], d['steps'])}{sec(T[9], c.get('tips', []))}{sec(T[10], meds)}{sec(T[11], c.get('see_doctor_if', []))}
<div class='dis'>{e(d['disclaimer'])}</div></body></html>"""
