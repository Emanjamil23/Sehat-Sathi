
# -*- coding: utf-8 -*-

"""
SehatSathi
Language detection and patient-facing messages.

Supported input:
1. Urdu script
2. Roman Urdu
3. English

Supported output:
1. Urdu
2. English
"""

import re
import unicodedata


# --------------------------------
# 1. Language detection keywords
# --------------------------------

ROMAN_URDU_MARKERS = {
    "hai", "hain", "h", "ka", "ki", "ke", "ko",
    "mein", "main", "nahi", "nahin", "nhi",
    "se", "aur", "bacha", "bcha", "bachi",
    "bukhar", "dast", "saans", "sans", "kal",
    "din", "dard", "halka", "tez", "mareez",
    "zukam", "khansi", "ulti", "pait", "rahi",
    "raha", "rahe", "saal", "sal", "zeher",
    "kha", "lia", "liya", "gaya", "gayi",
    "hua", "hui", "behosh", "jhatke", "khoon",
    "teen", "do", "char", "paanch", "mahine",
    "aurat", "mard"
}


ENGLISH_MARKERS = {
    "the", "is", "are", "has", "have", "with",
    "since", "for", "and", "child", "fever",
    "cough", "mild", "pain", "breathing",
    "cannot", "can't", "days", "day", "years",
    "year", "old", "man", "woman", "baby",
    "patient", "severe", "high", "not", "was",
    "after", "unconscious", "vomiting",
    "diarrhea", "headache", "cold", "sore",
    "throat", "bleeding", "temperature"
}


def detect_language(text: str) -> str:
    """
    Detect incoming text language.

    Returns:
        ur       = Urdu script
        roman_ur = Roman Urdu
        en       = English
    """

    text = unicodedata.normalize("NFKC", str(text)).lower()

    if not text.strip():
        return "ur"

    # Urdu script detection
    arabic_chars = [
        c for c in text
        if "\u0600" <= c <= "\u06FF"
    ]

    if arabic_chars:
        return "ur"

    words = set(re.findall(r"[a-z']+", text))

    roman_count = len(words & ROMAN_URDU_MARKERS)
    english_count = len(words & ENGLISH_MARKERS)

    if roman_count > english_count:
        return "roman_ur"

    return "en"


# --------------------------------
# 2. Patient-facing result messages
# --------------------------------

LEVELS = {

    # Urdu output
    "ur": {

        "emergency": {
            "title": "ہنگامی حالت",
            "message": (
                "مریض کو فوری طبی امداد کی ضرورت ہو سکتی ہے۔ "
                "فوراً قریبی ایمرجنسی طبی مرکز جائیں۔"
            ),
            "steps": [
                "دیر نہ کریں، فوری طبی مدد حاصل کریں۔",
                "مریض کو اکیلا نہ چھوڑیں۔",
                "مقامی ایمرجنسی سروس سے رابطہ کریں، اگر دستیاب ہو۔"
            ]
        },

        "urgent": {
            "title": "جلد ڈاکٹر کو دکھائیں",
            "message": (
                "مریض کو آج ہی کسی مستند ڈاکٹر یا صحت کے مرکز "
                "میں معائنہ کروانے کی ضرورت ہے۔"
            ),
            "steps": [
                "آج ہی طبی معائنہ کروائیں۔",
                "ڈاکٹر کی ہدایات پر عمل کریں۔",
                "حالت خراب ہونے پر فوری ایمرجنسی مدد حاصل کریں۔"
            ]
        },

        "home": {
            "title": "گھر پر نگرانی",
            "message": (
                "موجودہ معلومات کی بنیاد پر فوری خطرے کی "
                "علامت شناخت نہیں ہوئی۔ علامات پر نظر رکھیں۔"
            ),
            "steps": [
                "مریض کو آرام کرنے دیں۔",
                "مناسب مقدار میں پانی اور سیال دیں، اگر مریض پی سکتا ہو۔",
                "علامات برقرار رہیں یا بڑھیں تو ڈاکٹر سے رابطہ کریں۔"
            ]
        }
    },


    # English output
    "en": {

        "emergency": {
            "title": "Emergency",
            "message": (
                "The patient may need immediate medical attention. "
                "Go to the nearest emergency medical facility immediately."
            ),
            "steps": [
                "Do not delay. Seek immediate medical help.",
                "Do not leave the patient alone.",
                "Contact local emergency services if available."
            ]
        },

        "urgent": {
            "title": "Medical Attention Needed Today",
            "message": (
                "The patient should be examined today by a qualified "
                "doctor or healthcare professional."
            ),
            "steps": [
                "Arrange a medical examination today.",
                "Follow the doctor's instructions.",
                "Seek emergency help immediately if the condition worsens."
            ]
        },

        "home": {
            "title": "Home Monitoring",
            "message": (
                "No immediate red-flag symptom was identified from "
                "the information provided. Continue monitoring symptoms."
            ),
            "steps": [
                "Allow the patient to rest.",
                "Offer suitable fluids if the patient can drink.",
                "Contact a doctor if symptoms persist or get worse."
            ]
        }
    }
}


# --------------------------------
# 3. Red flag names
# --------------------------------

FLAG_NAMES = {

    "ur": {
        "breathing": "سانس لینے میں دشواری",
        "unconscious": "بے ہوشی یا دورے",
        "stiff_neck": "گردن کا اکڑنا",
        "chest_pain": "سینے میں درد",
        "not_feeding": "بچہ دودھ یا پانی نہیں پی رہا",
        "poison": "زہر کا شبہ",
        "pregnancy_bleeding": "حمل کے دوران خون آنا"
    },

    "en": {
        "breathing": "Difficulty breathing",
        "unconscious": "Unconsciousness or seizures",
        "stiff_neck": "Stiff neck",
        "chest_pain": "Chest pain",
        "not_feeding": "Child unable to drink milk or water",
        "poison": "Suspected poisoning",
        "pregnancy_bleeding": "Bleeding during pregnancy"
    }
}


# --------------------------------
# 4. Medical disclaimer
# --------------------------------

DISCLAIMER = {

    "ur": (
        "یہ نظام ڈاکٹر یا طبی معائنے کا متبادل نہیں ہے۔ "
        "یہ صرف ابتدائی فیصلہ سازی میں مدد کے لیے ایک تجرباتی نظام ہے۔"
    ),

    "en": (
        "This system is not a substitute for a doctor or medical "
        "examination. It is an experimental tool designed only "
        "to support preliminary decision-making."
    )
}

