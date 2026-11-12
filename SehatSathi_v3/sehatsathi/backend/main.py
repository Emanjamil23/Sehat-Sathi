
# -*- coding: utf-8 -*-

"""
SehatSathi - Offline-First Health Triage API

Input languages:
- Urdu
- Roman Urdu
- English

Output languages:
- Urdu
- English

Components:
- Local red-flag detection
- Local ML triage model
- Duration / age aware escalation (home_care.py)
- Safe home-care advice + OTC medicine whitelist (home_care.py)
- Optional Claude assessment (llm.py)

This is a prototype, not a clinically validated
diagnostic system or a replacement for medical care.
"""

import os
import sys

from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


# --------------------------------
# 1. Backend import path
# --------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


# --------------------------------
# 2. Local project imports
# --------------------------------

from red_flags import check_red_flags

from messages import (
    LEVELS,
    FLAG_NAMES,
    DISCLAIMER,
    detect_language
)

from ml_model import ml_predict

import home_care


# --------------------------------
# 3. Optional Claude import
# --------------------------------

try:
    import llm
except Exception:
    llm = None


# --------------------------------
# 4. Triage priority
# --------------------------------

ORDER = {
    "home": 0,
    "urgent": 1,
    "emergency": 2
}


# --------------------------------
# 5. FastAPI application
# --------------------------------

app = FastAPI(
    title="SehatSathi",
    description=(
        "Offline-first multilingual health "
        "triage prototype"
    ),
    version="3.0"
)


# --------------------------------
# 6. Patient input models
# --------------------------------

class FollowUp(BaseModel):
    q: str = ""
    a: str = ""


class Case(BaseModel):

    age: str = ""

    gender: str = ""

    symptoms: str = Field(
        ...,
        min_length=1,
        description="Patient symptoms in Urdu, Roman Urdu or English"
    )

    # Urdu is the default output language
    output_language: Literal["ur", "en"] = "ur"

    followup: list[FollowUp] = Field(
        default_factory=list
    )


# --------------------------------
# 7. Main triage logic
# --------------------------------

def triage_logic(
    age: str,
    gender: str,
    symptoms: str,
    followup=None,
    output_language: str = "ur"
) -> dict:

    # Validate output language
    if output_language not in LEVELS:
        raise ValueError("Unsupported output language")

    followup = followup or []

    # Remove empty follow-up answers
    valid_followups = [
        item for item in followup
        if str(item.a).strip()
    ]

    # Collect follow-up answers
    answers = " ".join(
        item.a for item in valid_followups
    )

    # Combine patient information
    text = (
        f"{age} {gender} {symptoms} {answers}"
    ).strip()

    if not text:
        raise HTTPException(
            status_code=400,
            detail="Please provide patient symptoms."
        )

    # --------------------------------
    # 8. Input language detection
    # --------------------------------

    input_language = detect_language(text)

    # Selected output language
    lang = output_language

    # --------------------------------
    # 9. Local red-flag detection
    # --------------------------------

    flags = check_red_flags(text)

    flag_names = [
        FLAG_NAMES[lang].get(flag, flag)
        for flag in flags
    ]

    # --------------------------------
    # 9b. Patient profile (age, pregnancy, duration, symptoms)
    #     gender yahan bhejna nahi: "ladka / mard" jaisi value umar ghalat batati hai
    # --------------------------------

    ctx = home_care.analyze(age, f"{symptoms} {answers}")

    # --------------------------------
    # 10. Local ML prediction
    # --------------------------------

    try:

        ml_level, probs = ml_predict(text)

        if ml_level not in ORDER:
            raise ValueError(
                "Invalid ML triage level"
            )

        if not isinstance(probs, dict) or not probs:
            raise ValueError(
                "Invalid ML probabilities"
            )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Local ML model could not process "
                "this case. Check the trained model."
            )
        ) from error

    # --------------------------------
    # 11. Optional Claude assessment
    # --------------------------------

    ai = None

    followup_data = [
        (
            item.model_dump()
            if hasattr(item, "model_dump")
            else item.dict()
        )
        for item in valid_followups
    ]

    if llm is not None:

        try:

            ai = llm.assess(
                text,
                ml_level,
                flag_names,
                followup_data,
                home_care.profile_summary(ctx)
            )

        except Exception:
            # Continue with local system if Claude fails
            ai = None

    # Validate Claude response
    if not isinstance(ai, dict):
        ai = None

    if ai and ai.get("triage_level") not in ORDER:
        ai = None

    # --------------------------------
    # 12. Final safety decision
    # --------------------------------

    levels = [ml_level]

    # Red flags always force emergency level
    if flags:
        levels.append("emergency")

    # Claude can increase risk, never decrease it
    if ai:
        levels.append(ai["triage_level"])

    # Claude ke symptom tags sirf tab jab rules ko kuch na mila ho
    # (Roman Urdu ki ghalat spelling). Is se Claude naye symptom bana kar dawai nahi barha sakta.
    if ai and not ctx["tags"]:
        home_care.merge_tags(ctx, ai.get("symptom_tags"))

    # Duration / umar / hamal ke hisab se escalation (sirf barhata hai)
    esc = home_care.escalation(ctx)

    if esc:
        levels.append("urgent")

    level = max(
        levels,
        key=lambda item: ORDER[item]
    )

    esc_index = 0 if lang == "ur" else 1
    escalation_reasons = [reason[esc_index] for reason in esc]

    # --------------------------------
    # 13. Patient-facing response
    # --------------------------------

    info = LEVELS[lang][level]

    # Language-specific reasoning
    reasoning = ""

    if ai:

        if lang == "ur":
            reasoning = ai.get("reasoning_ur", "")

        elif lang == "en":
            reasoning = ai.get("reasoning_en", "")

    # Claude ki mumkina wajohat + ghar ki hidayaat (dawai ka zikr filter ho chuka hai)
    ai_causes = []
    ai_tips = []

    if ai and level != "emergency":
        ai_causes = ai.get(f"causes_{lang}", [])
        ai_tips = ai.get(f"tips_{lang}", [])

    # Ghar ka ilaj + dawai (emergency mein None)
    care = home_care.build_care(level, ctx, lang)

    # Follow-up questions
    ai_followups = []

    if ai and level != "emergency":

        ai_followups = ai.get(
            f"follow_ups_{lang}",
            []
        ) or ai.get("follow_ups_ur", [])

        if not isinstance(ai_followups, list):
            ai_followups = []

    # --------------------------------
    # 14. Final API response
    # --------------------------------

    return {

        "triage_level": level,

        # Selected output language
        "language": lang,

        # Automatically detected input language
        "input_language": input_language,

        "title": info["title"],

        "message": info["message"],

        "steps": info["steps"],

        "red_flags_found": flag_names,

        "ml_level": ml_level,

        "ml_confidence": round(
            max(
                float(value)
                for value in probs.values()
            ),
            2
        ),

        "ml_probs": {
            key: round(float(value), 3)
            for key, value in probs.items()
        },

        "llm_used": ai is not None,

        "llm_level": (
            ai["triage_level"]
            if ai else None
        ),

        "reasoning": reasoning,

        "escalation_reasons": escalation_reasons,

        "care": care,

        "ai_causes": ai_causes,

        "ai_tips": ai_tips,

        "profile": home_care.profile_summary(ctx),

        "llm_status": (
            llm.status() if llm is not None
            else {"enabled": False, "reason": "llm_import_failed"}
        ),

        "follow_ups": ai_followups,

        "disclaimer": DISCLAIMER[lang]
    }


# --------------------------------
# 15. Triage API endpoint
# --------------------------------

@app.post("/triage")
def triage(c: Case):

    return triage_logic(
        age=c.age,
        gender=c.gender,
        symptoms=c.symptoms,
        followup=c.followup,
        output_language=c.output_language
    )


# --------------------------------
# 16. Home / status endpoint
# --------------------------------

@app.get("/")
def home():

    return {

        "project": "SehatSathi",

        "version": "3.0",

        "status": "running",

        "supported_input_languages": [
            "Urdu",
            "Roman Urdu",
            "English"
        ],

        "supported_output_languages": [
            "Urdu",
            "English"
        ],

        "default_output_language": "Urdu",

        "local_ml_enabled": True,

        "red_flag_detection": True,

        "optional_claude_enabled": (
            llm is not None and llm.status()["enabled"]
        ),

        "claude_status": (
            llm.status() if llm is not None
            else {"enabled": False, "reason": "llm_import_failed"}
        ),

        "features": [
            "red_flag_rules",
            "ml_triage",
            "duration_age_escalation",
            "home_care_and_otc_whitelist",
            "claude_second_opinion",
        ],

        "endpoint": "/triage"
    }
