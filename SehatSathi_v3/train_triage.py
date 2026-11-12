
# -*- coding: utf-8 -*-

"""
SehatSathi multilingual triage model.

Supported languages:
1. Urdu
2. Roman Urdu
3. English

IMPORTANT:
Training data is synthetic and is NOT clinically validated.
Model predictions must not be treated as medical diagnosis.
"""

import os
import csv
import random
import sys
import joblib

from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
ML_DIR = os.path.join(BASE_DIR, "ml")
BACKEND_DIR = os.path.join(BASE_DIR, "sehatsathi", "backend")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ML_DIR, exist_ok=True)

# Use the SAME normalizer as the backend prediction model
sys.path.insert(0, BACKEND_DIR)

from red_flags import normalize


random.seed(42)


# --------------------------------------------------
# URDU SCRIPT
# --------------------------------------------------

UR_AGES = [
    "بچہ دو سال کا",
    "بچی پانچ سال کی",
    "چھ ماہ کا بچہ",
    "عورت تیس سال کی",
    "مرد پچپن سال کا",
    "بزرگ ستر سال کے",
    "مریض",
    "خاتون"
]

UR_MODS = [
    "", "", "اور", "کل سے", "دو دن سے",
    "صبح سے", "بہت", "تھوڑا سا"
]

UR = {
    "emergency": [
        "سانس نہیں آ رہی",
        "سانس پھول رہی ہے",
        "سانس لینے میں سخت تکلیف",
        "بے ہوش ہو گیا",
        "بے ہوش ہو گئی",
        "جھٹکے آ رہے ہیں",
        "دورہ پڑا ہے",
        "گردن اکڑی ہوئی ہے",
        "حمل میں خون آ رہا ہے",
        "سینے میں شدید درد اور پسینہ",
        "بہت زیادہ خون بہہ رہا ہے",
        "دودھ نہیں پی رہا اور سست ہے",
        "ہوش میں نہیں",
        "ہونٹ نیلے ہو گئے",
        "زہر کھا لیا",
        "بہت زیادہ جل گیا",
        "حاملہ کو تیز درد اور خون"
    ],

    "urgent": [
        "تین دن سے تیز بخار",
        "دست آ رہے ہیں",
        "بار بار الٹی",
        "کان میں درد اور بخار",
        "پیشاب میں جلن اور بخار",
        "دو ہفتے سے کھانسی",
        "پیٹ میں تیز درد",
        "خون والی پیچش",
        "زخم میں پیپ",
        "آنکھیں دھنسی ہوئی ہیں",
        "سست اور کمزور",
        "حمل میں پاؤں سوجے ہوئے ہیں",
        "بہت کمزوری اور چکر",
        "پانی کی کمی لگ رہی ہے",
        "بخار تیز ہے اور اترتا نہیں"
    ],

    "home": [
        "ہلکا زکام",
        "ہلکی کھانسی",
        "سر درد",
        "ہلکا بخار کل سے",
        "گلا خراب ہے",
        "تھکن محسوس ہو رہی ہے",
        "ناک بہتی ہے",
        "ہلکی خراش",
        "نیند کم آ رہی ہے",
        "پیٹ ہلکا خراب",
        "جسم میں ہلکا درد",
        "گلے میں خراش"
    ]
}


# --------------------------------------------------
# ROMAN URDU
# --------------------------------------------------

RO_AGES = [
    "bacha 2 saal ka",
    "bachi 5 saal ki",
    "6 mahine ka bacha",
    "aurat 30 saal ki",
    "mard 55 saal ka",
    "buzurg 70 saal",
    "mareez"
]

RO_MODS = [
    "", "", "aur", "kal se", "do din se",
    "subah se", "bohat", "thora sa"
]

RO = {
    "emergency": [
        "saans nahi aa rahi",
        "saans phool rahi hai",
        "behosh ho gaya",
        "jhatke aa rahe hain",
        "daura para hai",
        "gardan akri hui hai",
        "hamal mein bleeding ho rahi hai",
        "seene mein shadeed dard aur pasina",
        "bohat zyada khoon beh raha hai",
        "doodh nahi pee raha aur sust hai",
        "hosh mein nahi",
        "lips neele ho gaye",
        "difficulty breathing",
        "unconscious",
        "convulsions",
        "severe chest pain",
        "zeher kha liya",
        "jal gaya bohat zyada"
    ],

    "urgent": [
        "3 din se tez bukhar",
        "dast aa rahe hain",
        "baar baar ulti",
        "kaan mein dard aur bukhar",
        "peshab mein jalan aur bukhar",
        "khansi 2 hafte se",
        "pait mein tez dard",
        "khoon wali pechish",
        "zakhm mein peep",
        "bukhar 39 se zyada",
        "paani ki kami lag rahi hai",
        "fever for 3 days",
        "diarrhea since two days",
        "persistent vomiting",
        "wound infected",
        "aankhein dhansi hui hain",
        "sust aur kamzor"
    ],

    "home": [
        "halka zukam",
        "halki khansi",
        "sar dard",
        "halka bukhar kal se",
        "gala kharab hai",
        "thakan mehsoos ho rahi hai",
        "naak behti hai",
        "mild cold",
        "slight headache",
        "mild cough",
        "body ache",
        "halki kharash",
        "neend kam aa rahi hai",
        "pait halka kharab"
    ]
}


# --------------------------------------------------
# ENGLISH
# --------------------------------------------------

EN_AGES = [
    "child 2 years old",
    "girl 5 years old",
    "baby 6 months old",
    "woman 30 years old",
    "man 55 years old",
    "elderly person 70 years old",
    "patient"
]

EN_MODS = [
    "", "", "since yesterday",
    "for two days", "this morning",
    "very", "slightly"
]

EN = {
    "emergency": [
        "cannot breathe",
        "severe breathing difficulty",
        "unconscious",
        "having seizures",
        "convulsions",
        "stiff neck",
        "pregnant woman has vaginal bleeding",
        "severe chest pain and sweating",
        "heavy bleeding",
        "baby is not feeding and is very weak",
        "blue lips",
        "swallowed poison",
        "severe burn"
    ],

    "urgent": [
        "high fever for three days",
        "repeated vomiting",
        "diarrhea",
        "ear pain with fever",
        "painful urination with fever",
        "cough for two weeks",
        "severe abdominal pain",
        "bloody diarrhea",
        "pus in wound",
        "sunken eyes",
        "dehydration symptoms",
        "dizziness and weakness",
        "persistent high fever"
    ],

    "home": [
        "mild cold",
        "mild cough",
        "slight headache",
        "mild fever",
        "sore throat",
        "feeling tired",
        "runny nose",
        "mild body ache",
        "slight throat irritation",
        "mild stomach discomfort"
    ]
}


# --------------------------------------------------
# LANGUAGE CONFIGURATION
# --------------------------------------------------

LANGUAGES = {
    "urdu": (UR_AGES, UR_MODS, UR),
    "roman_urdu": (RO_AGES, RO_MODS, RO),
    "english": (EN_AGES, EN_MODS, EN)
}


# --------------------------------------------------
# GENERATE TRAINING DATA
# --------------------------------------------------

def make(n_per_class_per_language=350):

    rows = []

    for language, (ages, mods, phrases_by_label) in LANGUAGES.items():

        for label in ["emergency", "urgent", "home"]:

            phrases = phrases_by_label[label]

            for i in range(n_per_class_per_language):

                selected = random.sample(
                    phrases,
                    k=random.choice([1, 1, 2])
                )

                age = random.choice(ages)
                modifier = random.choice(mods)

                text = f"{age} {modifier} {' '.join(selected)}"

                rows.append((
                    " ".join(text.split()),
                    label
                ))

    random.shuffle(rows)

    return rows


# --------------------------------------------------
# HELD-OUT TEST DATA
# --------------------------------------------------

HELD_OUT = [

    # Urdu
    ("بچے کو سانس لینے میں بہت مشکل ہو رہی ہے", "emergency"),
    ("مریض بالکل بے ہوش پڑا ہے", "emergency"),
    ("حاملہ عورت کو تیز خون آ رہا ہے", "emergency"),
    ("بچے کو دو دن سے بخار اور دست ہیں", "urgent"),
    ("تین دن سے الٹی نہیں رک رہی", "urgent"),
    ("ہلکا سا زکام ہے", "home"),

    # Roman Urdu
    ("bachay ko saans lene mein bohat mushkil", "emergency"),
    ("mareez bilkul behosh para hai", "emergency"),
    ("hamla aurat ko khoon aa raha hai", "emergency"),
    ("bachay ko do din se bukhar aur dast", "urgent"),
    ("teen din se ulti ho rahi hai", "urgent"),
    ("halka sa zukam hai", "home"),

    # English
    ("patient is unable to breathe", "emergency"),
    ("patient is completely unconscious", "emergency"),
    ("pregnant woman has heavy bleeding", "emergency"),
    ("child has fever and diarrhea for two days", "urgent"),
    ("vomiting has continued for three days", "urgent"),
    ("slight runny nose", "home")
]


# --------------------------------------------------
# MAIN TRAINING
# --------------------------------------------------

if __name__ == "__main__":

    print("\nGenerating training data...")

    rows = make()

    csv_path = os.path.join(
        DATA_DIR,
        "triage_data.csv"
    )

    # Save generated dataset
    with open(
        csv_path,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.writer(f)
        writer.writerow(["text", "label"])
        writer.writerows(rows)

    print("Training rows:", len(rows))
    print("Languages:", list(LANGUAGES.keys()))

    # Apply SAME normalization used during prediction
    X = [normalize(text) for text, label in rows]
    y = [label for text, label in rows]

    print("\nTraining ML model...")

    model = make_pipeline(
        TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(2, 5),
            lowercase=True
        ),

        LogisticRegression(
            max_iter=3000,
            class_weight={
                "emergency": 3,
                "urgent": 1.5,
                "home": 1
            },
            random_state=42
        )
    )

    model.fit(X, y)

    # Normalize held-out test data
    tx = [
        normalize(text)
        for text, label in HELD_OUT
    ]

    ty = [
        label
        for text, label in HELD_OUT
    ]

    predictions = model.predict(tx)

    print("\nHELD-OUT TEST RESULTS")

    print(
        classification_report(
            ty,
            predictions,
            zero_division=0
        )
    )

    labels = ["emergency", "urgent", "home"]

    print("Confusion Matrix:")

    print(
        confusion_matrix(
            ty,
            predictions,
            labels=labels
        )
    )

    missed = sum(
        1
        for actual, predicted in zip(ty, predictions)
        if actual == "emergency" and predicted != "emergency"
    )

    print("\nEmergency cases missed:", missed)

    # Save model to existing model location
    model_path = os.path.join(
        ML_DIR,
        "triage_model.joblib"
    )

    joblib.dump(model, model_path)

    print("\nModel successfully saved!")
    print(model_path)

    print("\nTraining completed.")
    print(
        "IMPORTANT: Synthetic test scores do not "
        "establish clinical safety."
    )
