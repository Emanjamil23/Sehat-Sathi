# -*- coding: utf-8 -*-
"""Home-care safety tests (server chalaye baghair):  python test_home_care.py"""
import sys, os
sys.path.insert(0, os.path.join("sehatsathi", "backend"))
import home_care as h

def run(age, text, level="home"):
    c = h.analyze(age, text)
    care = h.build_care(level, c, "en")
    return c, [m["id"] for m in (care or {}).get("medicines", [])]

CASES = [
 # (age, text, level, must_have_meds, must_not_have_meds, expect_escalation)
 ("woman 30 years old", "headache and sore throat", "home", {"paracetamol", "lozenge"}, set(), False),
 ("", "bacha ko bukhar", "home", set(), {"paracetamol"}, False),                 # umar nahi -> dawai nahi
 ("5 saal ki bachi", "bukhar", "home", {"paracetamol", "ors"}, set(), False),
 ("2 month old baby", "bukhar", "home", set(), {"paracetamol"}, True),            # <3 month
 ("mard 40 saal ka", "bukhar aur shugar ka mareez", "home", set(), {"paracetamol"}, False),
 ("woman 28 years", "pregnant, acidity", "home", set(), {"antacid"}, False),
 ("بچہ دو سال کا", "تین دن سے بخار", "urgent", set(), {"paracetamol"}, True),   # urgent: sirf ORS
 ("بچہ دو سال کا", "ایک دن سے بخار نہیں، زکام ہے", "home", set(), {"paracetamol"}, False),
 ("man 35 years", "cough for 3 weeks", "urgent", set(), set(), True),
 ("woman 25 years", "allergy hai, sar dard", "home", set(), {"paracetamol"}, False),
]
bad = 0
for age, text, lvl, must, mustnot, esc in CASES:
    c, meds = run(age, text, lvl)
    e = bool(h.escalation(c))
    ok = must <= set(meds) and not (mustnot & set(meds)) and e == esc
    bad += (not ok)
    print("OK  " if ok else "FAIL", age, "|", text, "->", meds, "esc" if e else "")

NEVER = {"ibuprofen", "aspirin", "diclofenac", "antibiotic"}
assert not NEVER & set(h.MEDICINES), "whitelist mein mana shuda dawai!"
for med in h.MEDICINES.values():
    assert "mg" not in " ".join(med["how"] + med["caution"]).lower(), "dose likha hai"
print("\nTotal fail:", bad)
sys.exit(1 if bad else 0)
