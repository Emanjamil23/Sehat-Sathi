# -*- coding: utf-8 -*-
"""
SehatSathi - Home-care & safe OTC medicine engine (offline, rule based)

Kya karta hai:
1. Text se patient profile nikalta hai (umar, hamal, kitne din se bimari, purani bimari/allergy)
2. Alamaat (symptoms) pehchanta hai: Urdu / Roman Urdu / English
3. Duration + umar ke hisab se level BARHA sakta hai (kabhi ghata nahi sakta)
4. Sirf level == "home" par ghar ka ilaj + OTC dawai ki SAFE list deta hai

SAFETY DESIGN (judges ko zaroor bataein):
- Dawaein sirf is file ki fixed WHITELIST se aati hain. Claude ya koi aur model naya naam add nahi kar sakta.
- Har dawai par umar / hamal / purani bimari ke filters lagte hain.
- Koi numeric dose nahi diya jata: "pack par likhi hidayat / pharmacist". Dose sirf doctor-reviewed data se add karein.
- Antibiotic, injection, steroid, aspirin, ibuprofen, diclofenac kabhi suggest nahi hote.

Yeh prototype hai, clinically validated nahi.
"""

import re

from red_flags import normalize


# ------------------------------------------------------------------
# 1. Text helpers
# ------------------------------------------------------------------

_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

_PUNCT = ".,;:!?\"'()،۔؟"
NEG_AFTER = {"nahi", "nahin", "nhi", "nai", "no", "not", "نہیں", "نھیں", "نہ"}
NEG_BEFORE = {"no", "without", "bina", "baghair", "بغیر", "بنا", "نہ"}


def _prep(text: str) -> str:
    return normalize(str(text).translate(_DIGITS))


def _tokens(text: str):
    return re.findall(r"[\w']+", text, re.U)


def _find_positive(text: str, phrases) -> bool:
    """True agar koi phrase mile aur uske foran aage/peeche negation na ho."""
    for phrase in phrases:
        p = normalize(phrase)
        if re.search(r"[a-z]", p):
            it = re.finditer(r"(?<!\w)" + re.escape(p) + r"(?!\w)", text)
        else:
            it = re.finditer(re.escape(p), text)
        for m in it:
            after = [w.strip(_PUNCT) for w in text[m.end():].split()[:1]]
            before = [w.strip(_PUNCT) for w in text[:m.start()].split()[-1:]]
            if after and after[0] in NEG_AFTER:
                continue
            if before and before[0] in NEG_BEFORE:
                continue
            return True
    return False


# ------------------------------------------------------------------
# 2. Numbers, age, duration
# ------------------------------------------------------------------

NUM = {
    # Urdu
    "ایک": 1, "دو": 2, "تین": 3, "چار": 4, "پانچ": 5, "چھ": 6, "سات": 7, "آٹھ": 8,
    "نو": 9, "دس": 10, "گیارہ": 11, "بارہ": 12, "تیرہ": 13, "چودہ": 14, "پندرہ": 15,
    "بیس": 20, "پچیس": 25, "تیس": 30, "چالیس": 40, "پچاس": 50, "پچپن": 55,
    "ساٹھ": 60, "ستر": 70, "اسی": 80,
    # Roman Urdu
    "ek": 1, "aik": 1, "do": 2, "teen": 3, "char": 4, "chaar": 4, "panch": 5,
    "paanch": 5, "chhe": 6, "chay": 6, "che": 6, "saat": 7, "aath": 8, "nau": 9,
    "das": 10, "gyarah": 11, "barah": 12, "terah": 13, "chaudah": 14, "pandrah": 15,
    "bees": 20, "pachees": 25, "tees": 30, "chalis": 40, "chalees": 40,
    "pachas": 50, "saath": 60, "sattar": 70, "assi": 80,
    # English
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "fifteen": 15,
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
    "seventy": 70, "eighty": 80,
}

YEAR = {"سال", "saal", "sal", "year", "years", "yr", "yrs"}
MONTH = {"ماہ", "مہینے", "مہینہ", "mahine", "mahina", "maah", "month", "months"}
WEEK = {"ہفتے", "ہفتہ", "hafte", "hafta", "haftay", "week", "weeks"}
DAY = {"دن", "din", "day", "days"}
DUR_MARK = {"سے", "se", "for", "since"}
AGE_MARK = {"کا", "کی", "ka", "ki", "old", "عمر"}

NEWBORN_WORDS = {"نومولود", "نوزائیدہ", "newborn"}
INFANT_WORDS = {"شیرخوار", "infant"}
CHILD_WORDS = {
    "بچہ", "بچی", "بچے", "بچوں", "bacha", "bachi", "bache", "bachay", "bachcha",
    "child", "baby", "kid", "toddler",
}
ADULT_WORDS = {
    "مرد", "آدمی", "عورت", "خاتون", "mard", "aadmi", "aurat", "khatoon",
    "man", "woman", "adult", "male", "female",
}
ELDER_WORDS = {"بوڑھا", "بوڑھی", "بزرگ", "boorha", "boorhi", "bujurg", "buzurg", "elderly"}


def _num(tok: str):
    if tok.isdigit():
        return float(tok)
    return NUM.get(tok)


def _scan_age_duration(tokens):
    age_years = None
    days = 0.0
    for i, tok in enumerate(tokens):
        v = _num(tok)
        if v is None or i + 1 >= len(tokens):
            continue
        unit = tokens[i + 1]
        nxt = tokens[i + 2:i + 4]
        if unit in DAY:
            days = max(days, v)
        elif unit in WEEK:
            days = max(days, v * 7)
        elif unit in YEAR:
            if nxt and nxt[0] in DUR_MARK:
                days = max(days, v * 365)
            elif age_years is None:
                age_years = v
        elif unit in MONTH:
            if any(x in AGE_MARK for x in nxt[:2]):
                if age_years is None:
                    age_years = v / 12.0
            else:
                days = max(days, v * 30)
    # "kal se / yesterday / parson se"
    for i, tok in enumerate(tokens):
        nxt = tokens[i + 1] if i + 1 < len(tokens) else ""
        if tok in {"کل", "kal"} and nxt in DUR_MARK:
            days = max(days, 1)
        if tok == "yesterday":
            days = max(days, 1)
        if tok in {"پرسوں", "parson"}:
            days = max(days, 2)
    return age_years, days


def _age_group(age_years, tokens):
    toks = set(tokens)
    if age_years is None:
        if toks & NEWBORN_WORDS:
            return "newborn", 0.05
        if toks & INFANT_WORDS:
            return "infant", 0.5
        if toks & ELDER_WORDS:
            return "elder", 70.0
        if toks & CHILD_WORDS:
            return "child", None          # umar nahi pata
        if toks & ADULT_WORDS:
            return "adult", 30.0
        return "unknown", None
    if age_years < 0.25:
        return "newborn", age_years
    if age_years < 1:
        return "infant", age_years
    if age_years < 12:
        return "child", age_years
    if age_years < 18:
        return "teen", age_years
    if age_years < 65:
        return "adult", age_years
    return "elder", age_years


# ------------------------------------------------------------------
# 3. Symptoms, pregnancy, conditions
# ------------------------------------------------------------------

SYMPTOMS = {
    "fever": ["بخار", "bukhar", "bukhaar", "fever", "high temperature"],
    "cough": ["کھانسی", "khansi", "cough", "coughing"],
    "cold": ["زکام", "نزلہ", "ناک بند", "ناک بہہ", "چھینک", "zukam", "zukaam", "nazla",
             "naak band", "naak beh", "runny nose", "blocked nose", "stuffy nose",
             "sneezing", "common cold"],
    "sore_throat": ["گلا خراب", "گلے میں درد", "گلے میں خراش", "گلے میں تکلیف",
                    "gala kharab", "gale mein dard", "gale me dard", "sore throat",
                    "throat pain"],
    "headache": ["سر درد", "سر میں درد", "سردرد", "sar dard", "sar mein dard",
                 "sar me dard", "sardard", "headache"],
    "diarrhea": ["دست", "پتلا پاخانہ", "پتلے پاخانے", "dast", "loose motion",
                 "loose motions", "patla pakhana", "diarrhea", "diarrhoea"],
    "vomiting": ["الٹی", "الٹیاں", "متلی", "ulti", "ultiyan", "matli", "vomiting",
                 "vomit", "nausea"],
    "stomach": ["پیٹ درد", "پیٹ میں درد", "تیزابیت", "گیس", "سینے میں جلن", "معدے",
                "pait dard", "pait mein dard", "pait me dard", "acidity", "gas",
                "bloating", "heartburn", "stomach ache", "stomach pain"],
    "body_ache": ["جسم درد", "بدن درد", "جسم میں درد", "کمر درد", "کمر میں درد",
                  "جوڑوں میں درد", "jism dard", "badan dard", "badan mein dard",
                  "kamar dard", "body ache", "body pain", "muscle pain", "back pain"],
    "wound": ["زخم", "چوٹ", "کٹ گیا", "خراش لگی", "زخمی", "zakhm", "chot",
              "kat gaya", "kharash lagi", "scratch", "minor cut", "cut", "wound"],
    "weakness": ["تھکاوٹ", "کمزوری", "تھکن", "thakan", "thakawat", "kamzori",
                 "tired", "tiredness", "weakness", "fatigue"],
}

HIGH_FEVER = ["تیز بخار", "بہت بخار", "tez bukhar", "bohat bukhar", "bohat tez bukhar",
              "high fever", "very high fever"]

PREGNANT = ["حمل", "حاملہ", "hamal", "hamla", "hamla hai", "pregnant", "pregnancy"]

BLOCKERS = {
    "allergy": ["الرجی", "الرجک", "allergy", "allergic"],
    "liver": ["جگر", "یرقان", "ہیپاٹائٹس", "liver", "hepatitis", "jaundice", "jigar", "yarqan"],
    "kidney": ["گردے", "گردہ", "kidney", "gurde", "gurday", "gurda"],
    "ulcer": ["السر", "معدے کا زخم", "ulcer"],
    "asthma": ["دمہ", "دما", "asthma", "dama", "damay"],
    "diabetes": ["شوگر", "ذیابیطس", "diabetes", "diabetic", "shugar", "shuger", "sugar ka mareez", "sugar ki bimari", "sugar ka masla"],
    "bp": ["بلڈ پریشر", "بی پی", "blood pressure", "hypertension", "bp", "high bp", "low bp"],
    "heart": ["دل کا مریض", "دل کی بیماری", "heart patient", "heart disease",
              "dil ka mareez", "dil ki bimari"],
    "on_meds": ["دوا لے رہا", "دوا لے رہی", "دوائی لے", "dawai le raha", "dawai le rahi",
                "on medication", "taking medicine", "already taking"],
}

SYMPTOM_LABEL = {
    "fever": ("بخار", "Fever"),
    "cough": ("کھانسی", "Cough"),
    "cold": ("زکام / نزلہ", "Cold / runny nose"),
    "sore_throat": ("گلے کی خرابی", "Sore throat"),
    "headache": ("سر درد", "Headache"),
    "diarrhea": ("دست", "Diarrhea"),
    "vomiting": ("الٹی / متلی", "Vomiting / nausea"),
    "stomach": ("پیٹ درد / تیزابیت", "Stomach ache / acidity"),
    "body_ache": ("جسم درد", "Body ache"),
    "wound": ("معمولی زخم / چوٹ", "Minor wound"),
    "weakness": ("تھکاوٹ / کمزوری", "Tiredness / weakness"),
}

VALID_TAGS = set(SYMPTOMS)


def analyze(age_text: str, text: str) -> dict:
    """age_text = umar wala field, text = alamaat + follow-up jawab (gender yahan MAT dein)."""
    full = _prep(f"{age_text} {text}")
    toks = _tokens(full)

    age_years, days = _scan_age_duration(toks)
    group, eff_years = _age_group(age_years, toks)

    tags = [tag for tag, phrases in SYMPTOMS.items() if _find_positive(full, phrases)]

    return {
        "tags": tags,
        "high_fever": "fever" in tags and _find_positive(full, HIGH_FEVER),
        "age_group": group,
        "age_years": None if age_years is None else round(age_years, 2),
        "eff_years": eff_years,          # None = umar maloom nahi
        "pregnant": _find_positive(full, PREGNANT),
        "duration_days": int(days),
        "blockers": [b for b, ph in BLOCKERS.items() if _find_positive(full, ph)],
    }


def merge_tags(ctx: dict, extra_tags) -> dict:
    """Claude ke tags (sirf VALID_TAGS) rules wale tags ke saath jor do."""
    for t in extra_tags or []:
        if t in VALID_TAGS and t not in ctx["tags"]:
            ctx["tags"].append(t)
    return ctx


# ------------------------------------------------------------------
# 4. Escalation: sirf level BARHA sakta hai
# ------------------------------------------------------------------

def escalation(ctx: dict):
    """Returns list of (ur, en) reasons. Khali list = koi escalation nahi."""
    reasons = []
    tags = set(ctx["tags"])
    y = ctx["eff_years"]
    d = ctx["duration_days"]

    if "fever" in tags:
        if y is not None and y < 1:
            reasons.append(("ایک سال سے کم عمر بچے میں بخار کو ڈاکٹر کو دکھانا ضروری ہے۔",
                            "Fever in a child under 1 year must be seen by a doctor."))
        if d >= 3:
            reasons.append(("تین دن یا زیادہ سے بخار ہے۔ ملیریا، ٹائیفائیڈ یا ڈینگی کے ٹیسٹ کی ضرورت ہو سکتی ہے۔",
                            "Fever for 3+ days may need malaria, typhoid or dengue tests."))
        if ctx["pregnant"]:
            reasons.append(("حمل کے دوران بخار میں ڈاکٹر سے مشورہ ضروری ہے۔",
                            "Fever during pregnancy needs a doctor's advice."))
    if "diarrhea" in tags:
        if y is not None and y < 1:
            reasons.append(("ایک سال سے کم عمر بچے میں دست جلد خطرناک ہو سکتے ہیں۔",
                            "Diarrhea can become dangerous quickly in a child under 1 year."))
        if d >= 3:
            reasons.append(("تین دن یا زیادہ سے دست ہیں۔", "Diarrhea for 3+ days."))
    if "vomiting" in tags and d >= 2:
        reasons.append(("دو دن یا زیادہ سے الٹی ہو رہی ہے۔", "Vomiting for 2+ days."))
    if "cough" in tags and d >= 14:
        reasons.append(("دو ہفتے سے زیادہ کھانسی کا ٹی بی کے لیے معائنہ ضروری ہے۔",
                        "Cough over 2 weeks should be checked for TB."))
    if ({"cold", "cough"} & tags) and y is not None and y < 0.25:
        reasons.append(("تین ماہ سے کم عمر بچے کی کھانسی/زکام ڈاکٹر کو دکھائیں۔",
                        "Cough/cold in a baby under 3 months needs a doctor."))
    if tags and d >= 7 and not reasons:
        reasons.append(("علامات ایک ہفتے سے زیادہ سے ہیں۔", "Symptoms have lasted over a week."))
    return reasons


# ------------------------------------------------------------------
# 5. Knowledge base (dawaein = FIXED WHITELIST)
# ------------------------------------------------------------------

# Har tip: (urdu, english, min_years or None, interim_ok)
TIPS = {
    "fever": [
        ("ہلکے کپڑے پہنائیں اور موٹے کمبل میں نہ لپیٹیں۔",
         "Dress lightly; do not wrap in thick blankets.", None, True),
        ("نیم گرم (نہ کہ ٹھنڈے) پانی سے جسم پونچھیں۔ برف یا الکحل نہ لگائیں۔",
         "Sponge with lukewarm (not cold) water. No ice or alcohol rubs.", None, True),
        ("پانی، سوپ اور دیگر سیال بار بار دیں۔", "Offer water, soup and fluids often.", None, True),
        ("ہر چند گھنٹے بعد درجہ حرارت اور حالت دیکھتے رہیں۔",
         "Check temperature and general condition every few hours.", None, True),
    ],
    "cough": [
        ("گرم پانی یا چائے کے چھوٹے گھونٹ لیں۔", "Take small sips of warm fluids.", 1, False),
        ("ایک سال سے بڑے مریض کو ایک چمچ شہد دیا جا سکتا ہے۔",
         "Honey (one spoon) can be given to anyone over 1 year.", 1, False),
        ("چولہے، سگریٹ اور دھوئیں سے دور رکھیں۔", "Keep away from stove smoke, cigarettes and dust.", None, True),
        ("سر اونچا رکھ کر سلائیں۔", "Sleep with the head raised.", None, True),
        ("چھوٹے بچوں کو کھانسی کا شربت خود سے نہ دیں۔",
         "Do not give cough syrup to young children on your own.", None, True),
    ],
    "cold": [
        ("آرام کریں اور گرم سیال پئیں۔", "Rest and drink warm fluids.", None, True),
        ("ناک بند ہو تو نمکین پانی کے قطرے ڈالیں اور نرمی سے صاف کریں۔",
         "For a blocked nose use saline drops and wipe gently.", None, True),
        ("شیر خوار بچے کو ماں کا دودھ جاری رکھیں۔",
         "Continue breastfeeding for babies.", None, True),
    ],
    "sore_throat": [
        ("نیم گرم نمک والے پانی سے غرارے کریں (چھ سال سے بڑے مریض)۔",
         "Gargle with warm salt water (children over 6 and adults).", 6, False),
        ("گرم سیال پئیں اور ٹھنڈی چیزوں سے پرہیز کریں۔",
         "Drink warm fluids; avoid cold drinks.", None, True),
        ("آواز کو آرام دیں، زیادہ نہ بولیں۔", "Rest the voice.", 6, False),
    ],
    "headache": [
        ("پرسکون، ہلکی روشنی والی جگہ پر آرام کریں۔", "Rest in a quiet, dim room.", None, True),
        ("پانی پئیں اور وقت پر کھانا کھائیں۔", "Drink water and eat on time.", None, True),
        ("ماتھے پر ٹھنڈا گیلا کپڑا رکھیں۔", "Place a cool damp cloth on the forehead.", None, True),
    ],
    "diarrhea": [
        ("او آر ایس بار بار تھوڑا تھوڑا پلائیں۔", "Give ORS often in small amounts.", None, True),
        ("بچے کو ماں کا دودھ اور معمول کی خوراک جاری رکھیں۔",
         "Continue breastfeeding and normal feeding.", None, True),
        ("پینے کا پانی ابال کر ٹھنڈا کر کے دیں، ہاتھ صابن سے دھوئیں۔",
         "Use boiled, cooled water and wash hands with soap.", None, True),
        ("بغیر ڈاکٹر کے اینٹی بائیوٹک یا دست روکنے والی دوا نہ دیں۔",
         "No antibiotics or anti-diarrheal tablets without a doctor.", None, True),
    ],
    "vomiting": [
        ("پانی یا او آر ایس کے چھوٹے گھونٹ لیں، الٹی ہو تو دس منٹ رک کر دوبارہ شروع کریں۔",
         "Take small sips of water/ORS; if vomiting, wait 10 minutes and restart slowly.", None, True),
        ("تلی ہوئی اور مسالے دار چیزوں سے پرہیز کریں۔",
         "Avoid oily and spicy food.", None, True),
    ],
    "stomach": [
        ("ہلکی اور کم مقدار میں خوراک لیں؛ تلی ہوئی، مرچ مسالے اور چائے سے پرہیز کریں۔",
         "Eat light, small meals; avoid fried, spicy food and tea.", None, True),
        ("کھانے کے فوراً بعد لیٹیں نہیں۔", "Do not lie down right after eating.", None, True),
        ("پیٹ پر نیم گرم کپڑے کی ہلکی سینک لے سکتے ہیں۔",
         "A warm cloth on the belly may soothe.", None, True),
    ],
    "body_ache": [
        ("آرام کریں اور درد والی جگہ پر نیم گرم سینک دیں۔",
         "Rest and apply a warm compress.", None, True),
        ("پانی اور غذائیت والی خوراک لیں۔", "Drink fluids and eat nutritious food.", None, True),
    ],
    "wound": [
        ("زخم کو صاف بہتے پانی اور صابن سے دھوئیں۔",
         "Wash the wound with clean running water and soap.", None, True),
        ("خون بہہ رہا ہو تو صاف کپڑے سے دس منٹ دبائے رکھیں۔",
         "If bleeding, press with a clean cloth for 10 minutes.", None, True),
        ("صاف پٹی سے ڈھانپیں اور روز بدلیں۔", "Cover with a clean dressing; change daily.", None, True),
        ("گہرا یا زنگ آلود چیز سے لگا زخم ہو تو ٹیٹنس کے لیے ڈاکٹر کو دکھائیں۔",
         "A deep or rusty-object wound needs a doctor (tetanus).", None, True),
    ],
    "weakness": [
        ("پورا آرام اور نیند لیں۔", "Get enough rest and sleep.", None, True),
        ("دال، گوشت، سبزیاں، پھل اور کافی پانی لیں۔",
         "Eat lentils, meat, vegetables, fruit and drink enough water.", None, True),
    ],
}

SEE_DOCTOR = {
    "fever": [("بخار تین دن میں نہ اترے یا بار بار چڑھے", "Fever not gone in 3 days or keeps returning"),
              ("جسم پر دانے، خون آنا، شدید کمزوری یا بہت نیند", "Rash, bleeding, extreme weakness or drowsiness"),
              ("بچہ دودھ/پانی چھوڑ دے یا جھٹکے آئیں", "Child stops drinking or has fits")],
    "cough": [("سانس تیز چلنا یا سانس میں آواز", "Fast breathing or wheezing"),
              ("کھانسی میں خون یا دو ہفتے سے زیادہ", "Blood in cough or lasting over 2 weeks")],
    "cold": [("سات دن میں بہتری نہ آئے", "No improvement in 7 days"),
             ("کان درد یا تیز بخار شروع ہو جائے", "Ear pain or high fever starts")],
    "sore_throat": [("نگلنے میں بہت مشکل یا منہ سے رال بہنا", "Great difficulty swallowing or drooling"),
                    ("تین دن سے زیادہ تکلیف", "Pain lasting over 3 days")],
    "headache": [("اچانک بہت شدید درد، الٹی یا نظر دھندلانا", "Sudden severe pain, vomiting or blurred vision"),
                 ("سر کی چوٹ کے بعد درد", "Headache after a head injury")],
    "diarrhea": [("پیشاب بہت کم، منہ خشک، آنکھیں دھنسی ہوئی", "Little urine, dry mouth, sunken eyes"),
                 ("پاخانے میں خون یا مسلسل الٹی", "Blood in stool or constant vomiting")],
    "vomiting": [("الٹی میں خون یا ہرا پانی", "Blood or green fluid in vomit"),
                 ("کچھ بھی پی نہ سکے", "Cannot keep any fluid down")],
    "stomach": [("شدید یا بڑھتا ہوا درد، کالا پاخانہ", "Severe or worsening pain, black stool"),
                ("دو ہفتے سے زیادہ تیزابیت", "Acidity lasting over 2 weeks")],
    "body_ache": [("ٹانگ سوجن یا سرخی، چلنے سے قاصر", "Leg swelling/redness or unable to walk")],
    "wound": [("زخم میں پیپ، سرخی بڑھنا یا بدبو", "Pus, spreading redness or smell"),
              ("خون دس منٹ دبانے پر بھی نہ رکے", "Bleeding not stopping after 10 minutes of pressure")],
    "weakness": [("چکر آنا، رنگ پیلا یا وزن کم ہونا", "Dizziness, pale skin or weight loss")],
}

GENERAL_SEE_DOCTOR = [
    ("کوئی بھی علامت بگڑ جائے یا نئی خطرناک علامت آئے تو فوراً ڈاکٹر کے پاس جائیں",
     "If anything gets worse or a new danger sign appears, go to a doctor immediately"),
]

AVOID = [
    ("بغیر ڈاکٹر کے اینٹی بائیوٹک، انجکشن، ڈرپ یا سٹیرائیڈ نہ لیں۔",
     "No antibiotics, injections, drips or steroids without a doctor."),
    ("بخار یا درد میں ایسپرین، بروفین یا ڈکلوفینک نہ لیں (ڈینگی میں خون بہنے کا خطرہ؛ بچوں میں ایسپرین خطرناک)۔",
     "For fever/pain avoid aspirin, ibuprofen and diclofenac (bleeding risk in dengue; aspirin is dangerous in children)."),
    ("ایک ہی جزو (جیسے پیراسیٹامول) والی دو دوائیں ساتھ نہ لیں۔",
     "Never combine two products with the same ingredient (e.g. paracetamol)."),
]

# --- Medicine whitelist --------------------------------------------------
# min_years: kam az kam umar (0 = sab). max_years: zyada se zyada. allow_pregnant: hamal mein ok?
# open_to_all=True matlab purani bimari wale marizon ko bhi (ORS/saline) - sirf kidney/heart mein nahi.
MEDICINES = {
    "paracetamol": {
        "tags": {"fever", "headache", "body_ache"},
        "min_years": 0.25, "max_years": None, "allow_pregnant": True, "open_to_all": False,
        "name": ("پیراسیٹامول (مثلاً پینیڈول / کالپول)", "Paracetamol (e.g. Panadol / Calpol)"),
        "for": ("بخار اور درد کے لیے", "For fever and pain"),
        "how": ("پیکٹ یا شربت پر عمر/وزن کے مطابق لکھی مقدار ہی دیں۔ شک ہو تو فارماسسٹ سے پوچھیں۔",
                "Use only the amount on the pack for the age/weight. Ask a pharmacist if unsure."),
        "caution": ("24 گھنٹے میں پیکٹ پر لکھی زیادہ سے زیادہ مقدار سے زیادہ نہ دیں۔ جگر کی بیماری میں خود سے نہ لیں۔",
                    "Never exceed the maximum per 24 hours on the pack. Not on your own with liver disease."),
    },
    "ors": {
        "tags": {"diarrhea", "vomiting", "fever"},
        "min_years": 0, "max_years": None, "allow_pregnant": True, "open_to_all": True,
        "name": ("او آر ایس (نمکیات کا محلول)", "ORS (oral rehydration salts)"),
        "for": ("پانی کی کمی سے بچاؤ کے لیے", "To prevent dehydration"),
        "how": ("پیکٹ پر لکھی ہدایت کے مطابق صاف ابلے ٹھنڈے پانی میں گھولیں اور تھوڑا تھوڑا بار بار پلائیں۔",
                "Mix exactly as on the packet in clean boiled, cooled water; sip little and often."),
        "caution": ("اس میں اضافی چینی یا نمک نہ ملائیں۔ 24 گھنٹے بعد بچا محلول پھینک دیں۔",
                    "Do not add extra sugar or salt. Throw away leftover solution after 24 hours."),
    },
    "zinc": {
        "tags": {"diarrhea"},
        "min_years": 0.25, "max_years": 5, "allow_pregnant": False, "open_to_all": False,
        "name": ("زنک (بچوں کے دست میں)", "Zinc (for children's diarrhea)"),
        "for": ("پانچ سال تک کے بچوں میں دست کے دوران", "For children under 5 with diarrhea"),
        "how": ("صحت کارکن یا فارماسسٹ کی بتائی مقدار اور پورے کورس کے مطابق دیں۔",
                "Give the amount and full course advised by the health worker or pharmacist."),
        "caution": ("کورس بیچ میں نہ چھوڑیں۔", "Do not stop the course half-way."),
    },
    "saline_drops": {
        "tags": {"cold"},
        "min_years": 0, "max_years": None, "allow_pregnant": True, "open_to_all": True,
        "name": ("نمکین پانی کے ناک کے قطرے", "Saline nasal drops"),
        "for": ("بند ناک کھولنے کے لیے", "To clear a blocked nose"),
        "how": ("پیکٹ پر لکھی ہدایت کے مطابق ناک میں ڈالیں۔",
                "Use as directed on the pack."),
        "caution": ("اس میں دوا نہیں ہوتی، شیر خوار بچوں کے لیے بھی محفوظ ہے۔",
                    "Contains no drug; safe even for babies."),
    },
    "lozenge": {
        "tags": {"sore_throat"},
        "min_years": 12, "max_years": None, "allow_pregnant": False, "open_to_all": False,
        "name": ("گلے کی سادہ گولیاں (لوزنج)", "Plain throat lozenges"),
        "for": ("گلے کی خراش کے لیے", "For a scratchy throat"),
        "how": ("پیکٹ پر لکھی ہدایت کے مطابق چوسیں، چبائیں نہیں۔",
                "Suck as directed on the pack; do not chew."),
        "caution": ("چھوٹے بچوں کو نہ دیں، گلے میں پھنس سکتی ہیں۔",
                    "Not for young children: choking risk."),
    },
    "antacid": {
        "tags": {"stomach"},
        "min_years": 12, "max_years": None, "allow_pregnant": False, "open_to_all": False,
        "name": ("اینٹاسڈ (تیزابیت کی عام دوا)", "Antacid (common acidity medicine)"),
        "for": ("تیزابیت اور سینے کی جلن کے لیے", "For acidity and heartburn"),
        "how": ("پیکٹ پر لکھی مقدار اور وقت کے مطابق لیں۔",
                "Take the amount and timing stated on the pack."),
        "caution": ("دو ہفتے سے زیادہ ضرورت پڑے تو ڈاکٹر کو دکھائیں۔",
                    "See a doctor if needed for more than 2 weeks."),
    },
    "antiseptic": {
        "tags": {"wound"},
        "min_years": 1, "max_years": None, "allow_pregnant": False, "open_to_all": False,
        "name": ("ہلکا اینٹی سیپٹک (مثلاً پووڈون آیوڈین)", "Mild antiseptic (e.g. povidone-iodine)"),
        "for": ("زخم دھونے کے بعد معمولی زخم پر", "On a minor wound after washing"),
        "how": ("صرف تھوڑی مقدار صاف زخم کے ارد گرد لگائیں۔",
                "Apply a small amount around the cleaned wound only."),
        "caution": ("گہرے زخم پر نہ لگائیں۔ آیوڈین سے الرجی ہو تو استعمال نہ کریں۔",
                    "Not on deep wounds. Do not use if allergic to iodine."),
    },
}

BLOCK_MSG = {
    "conditions": ("آپ نے کسی بیماری، الرجی یا دوا کا ذکر کیا ہے، اس لیے خود سے کوئی دوا نہ لیں۔ ڈاکٹر یا فارماسسٹ سے پوچھیں۔",
                   "A health condition, allergy or current medicine was mentioned, so do not self-medicate. Ask a doctor or pharmacist."),
    "pregnant": ("حمل میں خود سے دوا نہ لیں (پیراسیٹامول اور او آر ایس کے علاوہ)۔ ڈاکٹر سے پوچھیں۔",
                 "In pregnancy do not self-medicate (except paracetamol and ORS). Ask a doctor."),
    "age_unknown": ("مریض کی عمر معلوم نہیں، اس لیے دوا کی تجویز نہیں دی جا رہی۔ عمر لکھ کر دوبارہ چیک کریں۔",
                    "The patient's age is unknown, so no medicine is suggested. Enter the age and check again."),
    "too_young": ("چھوٹی عمر کی وجہ سے کچھ دوائیں نہیں دکھائی گئیں۔ ڈاکٹر یا فارماسسٹ سے پوچھیں۔",
                  "Some medicines are hidden because of the patient's young age. Ask a doctor or pharmacist."),
    "too_old": ("عمر کی حد کی وجہ سے کچھ دوائیں نہیں دکھائی گئیں۔",
                "Some medicines are hidden because of the age limit."),
}

INTERIM_ONLY = {"ors"}      # urgent level par sirf yeh (dawa nahi, sirf ORS)


def _gate(med: dict, med_id: str, ctx: dict):
    """(ok, reason_code)."""
    blockers = set(ctx["blockers"])
    if blockers:
        if med["open_to_all"] and not (blockers & {"kidney", "heart"}):
            pass
        else:
            return False, "conditions"
    if ctx["pregnant"] and not med["allow_pregnant"]:
        return False, "pregnant"
    y = ctx["eff_years"]
    if med["min_years"] > 0 or med["max_years"] is not None:
        if y is None:
            return False, "age_unknown"
        if y < med["min_years"]:
            return False, "too_young"
        if med["max_years"] is not None and y >= med["max_years"]:
            return False, "too_old"
    return True, ""


# ------------------------------------------------------------------
# 6. Build the care plan
# ------------------------------------------------------------------

def build_care(level: str, ctx: dict, lang: str = "ur"):
    """level: home | urgent | emergency. Emergency par None (sirf hospital)."""
    if level == "emergency" or not ctx["tags"]:
        return None

    i = 0 if lang == "ur" else 1
    interim = level == "urgent"
    y = ctx["eff_years"]
    tags = ctx["tags"]

    tips, seen = [], set()
    for tag in tags:
        for ur, en, min_y, interim_ok in TIPS.get(tag, []):
            if interim and not interim_ok:
                continue
            if min_y is not None and (y is None or y < min_y):
                continue
            text = (ur, en)[i]
            if text not in seen:
                seen.add(text)
                tips.append(text)

    medicines, notes = [], []
    for med_id, med in MEDICINES.items():
        if not (med["tags"] & set(tags)):
            continue
        if interim and med_id not in INTERIM_ONLY:
            continue
        ok, why = _gate(med, med_id, ctx)
        if not ok:
            if why not in notes:
                notes.append(why)
            continue
        medicines.append({
            "id": med_id,
            "name": med["name"][i],
            "for": med["for"][i],
            "how": med["how"][i],
            "caution": med["caution"][i],
        })

    # Eik hi dafa dawai ki hadd: bahut zyada na dikhayen
    medicines = medicines[:4]

    see_doctor = []
    for tag in tags:
        for ur, en in SEE_DOCTOR.get(tag, []):
            text = (ur, en)[i]
            if text not in see_doctor:
                see_doctor.append(text)
    see_doctor += [(ur, en)[i] for ur, en in GENERAL_SEE_DOCTOR]

    return {
        "mode": "interim" if interim else "home",
        "symptoms": [{"id": t, "label": SYMPTOM_LABEL[t][i]} for t in tags],
        "tips": tips,
        "medicines": medicines,
        "medicines_note": [BLOCK_MSG[n][i] for n in notes],
        "avoid": [(ur, en)[i] for ur, en in AVOID],
        "see_doctor_if": see_doctor,
    }


def profile_summary(ctx: dict) -> dict:
    return {
        "age_group": ctx["age_group"],
        "age_years": ctx["age_years"],
        "pregnant": ctx["pregnant"],
        "duration_days": ctx["duration_days"],
        "symptom_tags": list(ctx["tags"]),
        "has_conditions": bool(ctx["blockers"]),
    }


# ------------------------------------------------------------------
# 7. Claude text sanitizer (Claude dawai ka naam / dose na likh sakay)
# ------------------------------------------------------------------

_BAD = re.compile(
    r"(\d\s*(mg|ml|mcg|gm|g\b|tablet|tab\b|cap\b|capsule|drop)|ملی گرام|ملی لیٹر|گولی|ٹیبلٹ|کیپسول|"
    r"amoxi|augmentin|azithro|ciprofloxacin|flagyl|metronidazole|brufen|ibuprofen|diclofenac|"
    r"voltaren|aspirin|disprin|panadol|calpol|paracetamol|پیراسیٹامول|بروفین|ڈسپرین|پینیڈول|کالپول|ڈائیکلوفینک|بروفن|"
    r"اینٹی بائیوٹک|antibiotic|injection|انجکشن|steroid|سٹیرائیڈ|prednisolone)",
    re.I,
)


def safe_text(items, limit: int = 4):
    """Claude ki list se woh lines rakho jin mein dawai/dose nahi."""
    out = []
    for item in items or []:
        s = str(item).strip()
        if s and not _BAD.search(s) and len(s) <= 220:
            out.append(s)
        if len(out) >= limit:
            break
    return out
