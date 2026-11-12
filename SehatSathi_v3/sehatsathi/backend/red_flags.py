
# -*- coding: utf-8 -*-

"""
SehatSathi Red Flag Engine

Supports:
- Urdu script
- Roman Urdu
- English

Returns red-flag IDs for messages.py.
This is a prototype rule engine, not a clinically
validated diagnostic system.
"""

import re
import unicodedata


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", str(text)).lower()

    replacements = {
        "ي": "ی",
        "ى": "ی",
        "ك": "ک",
        "ۃ": "ہ",
        "ۂ": "ہ",
        "أ": "ا",
        "إ": "ا",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"\s+", " ", text).strip()

    return text


RED_FLAGS = {
    "breathing": [
        "سانس لینے میں مشکل",
        "سانس کی تکلیف",
        "سانس نہیں آ رہی",
        "سانس رک رہی",
        "سانس پھول رہی",
        "سانس پھولنا",
        "سانس اکھڑ",
        "saans ki takleef",
        "saans lene mein mushkil",
        "saans nahi aa rahi",
        "saans ruk rahi",
        "saans phool rahi",
        "saans phoolna",
        "breathing difficulty",
        "difficulty breathing",
        "shortness of breath",
        "cannot breathe",
        "can't breathe",
        "unable to breathe",
        "choking",
        "suffocating",
    ],

    "unconscious": [
        "بے ہوش",
        "بیہوش",
        "ہوش میں نہیں",
        "ہوش نہیں",
        "جھٹکے لگ رہے",
        "دورہ پڑا",
        "دورے پڑ رہے",
        "behosh",
        "hush mein nahi",
        "hush nahi hai",
        "jhatke lag rahe",
        "daura para",
        "daura",
        "unconscious",
        "seizure",
        "convulsion",
        "collapsed",
    ],

    "stiff_neck": [
        "گردن اکڑ گئی",
        "گردن اکڑی ہوئی",
        "گردن اکڑنا",
        "gardan akri hui",
        "gardan akar gai",
        "stiff neck",
        "neck stiffness",
    ],

    "chest_pain": [
        "سینے میں شدید درد",
        "سینے میں درد",
        "سینے میں دباؤ",
        "seene mein dard",
        "seene mein shadeed dard",
        "seene mein dabao",
        "chest pain",
        "chest pressure",
        "pain in chest",
    ],

    "not_feeding": [
        "بچہ دودھ نہیں پی رہا",
        "بچہ دودھ نہیں پی رہی",
        "بچہ پانی نہیں پی رہا",
        "دودھ بالکل نہیں پی رہا",
        "doodh nahi pee raha",
        "doodh nahi pi raha",
        "bacha doodh nahi pee raha",
        "bacha pani nahi pee raha",
        "not feeding",
        "not drinking",
        "unable to feed",
    ],

    "poison": [
        "زہر کھا لیا",
        "زہر پی لیا",
        "زہر کا شبہ",
        "زہریلی چیز کھا لی",
        "zeher kha liya",
        "zehar pee liya",
        "poisoning",
        "suspected poisoning",
        "swallowed poison",
        "toxic substance",
    ],
}


POSITIVE_PATTERNS = {
    "breathing": [
        "saans nahi aa rahi",
        "saans nahi le pa raha",
        "saans nahi le pa rahi",
        "cannot breathe",
        "can't breathe",
        "unable to breathe",
        "سانس نہیں آ رہی",
        "سانس نہیں لے پا رہا",
        "سانس نہیں لے پا رہی",
    ],

    "unconscious": [
        "hosh mein nahi",
        "hosh nahi hai",
        "hush mein nahi",
        "بے ہوش",
        "ہوش میں نہیں",
    ],

    "not_feeding": [
        "doodh nahi pee raha",
        "doodh nahi pi raha",
        "bacha pani nahi pee raha",
        "بچہ دودھ نہیں پی رہا",
    ],
}


NEGATIONS = [
    "nahi",
    "nahin",
    "nhi",
    "not",
    "no",
    "without",
    "نہیں",
    "نہ",
    "نہیں ہے",
]


def contains_phrase(text: str, phrase: str) -> bool:
    phrase = normalize(phrase)

    if re.search(r"[a-z]", phrase):
        pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"
        return bool(re.search(pattern, text))

    return phrase in text


def is_explicitly_positive(text: str, flag_id: str) -> bool:
    phrases = POSITIVE_PATTERNS.get(flag_id, [])

    return any(
        contains_phrase(text, phrase)
        for phrase in phrases
    )


def is_negated(text: str, phrase: str) -> bool:
    phrase = normalize(phrase)

    match = None

    if re.search(r"[a-z]", phrase):
        pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"
        match = re.search(pattern, text)
    else:
        start = text.find(phrase)

        if start != -1:
            class Match:
                pass

            match = Match()
            match.start = lambda: start
            match.end = lambda: start + len(phrase)

    if not match:
        return False

    before = text[max(0, match.start() - 35):match.start()]
    after = text[match.end():match.end() + 35]

    before_words = before.split()[-3:]
    after_words = after.split()[:3]

    context_words = before_words + after_words

    return any(
        word in NEGATIONS
        for word in context_words
    )


def check_red_flags(text: str) -> list[str]:

    t = normalize(text)

    flags = []

    for flag_id, phrases in RED_FLAGS.items():

        matched_phrases = [
            phrase for phrase in phrases
            if contains_phrase(t, phrase)
        ]

        if not matched_phrases:
            continue

        if is_explicitly_positive(t, flag_id):
            flags.append(flag_id)
            continue

        if any(
            not is_negated(t, phrase)
            for phrase in matched_phrases
        ):
            flags.append(flag_id)

    # Pregnancy + bleeding combination
    pregnancy_phrases = [
        "حمل",
        "حاملہ",
        "hamal",
        "hamla",
        "pregnant",
        "pregnancy",
    ]

    bleeding_phrases = [
        "خون آ رہا",
        "خون بہہ",
        "خون آنا",
        "bleeding",
        "vaginal bleeding",
        "khoon aa raha",
        "khoon beh raha",
    ]

    pregnancy_found = any(
        contains_phrase(t, phrase)
        for phrase in pregnancy_phrases
    )

    bleeding_found = any(
        contains_phrase(t, phrase)
        for phrase in bleeding_phrases
    )

    pregnancy_negative = any(
        is_negated(t, phrase)
        for phrase in pregnancy_phrases
        if contains_phrase(t, phrase)
    )

    bleeding_negative = any(
        is_negated(t, phrase)
        for phrase in bleeding_phrases
        if contains_phrase(t, phrase)
    )

    if (
        pregnancy_found
        and bleeding_found
        and not pregnancy_negative
        and not bleeding_negative
    ):
        flags.append("pregnancy_bleeding")

    return list(set(flags))
