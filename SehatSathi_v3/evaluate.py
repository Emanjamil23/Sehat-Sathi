# -*- coding: utf-8 -*-
"""SehatSathi evaluation: rules vs ML vs combined, Urdu + Roman Urdu + English.
Run from project root:  python evaluate.py
Add your own CASES, ideally verified by a doctor / medical student."""
import sys, os
sys.path.insert(0, os.path.join("sehatsathi", "backend"))
from red_flags import check_red_flags
from ml_model import ml_predict
from messages import detect_language

CASES = [
 # ---- Urdu script ----
 ("بچے کو سانس لینے میں بہت مشکل ہے", "emergency"),
 ("مریض بالکل بے ہوش پڑا ہے", "emergency"),
 ("بچے کو جھٹکے آ رہے ہیں اور بخار ہے", "emergency"),
 ("حاملہ عورت کو تیز خون آ رہا ہے", "emergency"),
 ("مرد کو سینے میں درد اور پسینہ", "emergency"),
 ("بچے کی گردن اکڑ گئی ہے اور تیز بخار", "emergency"),
 ("بچی دودھ نہیں پی رہی بہت سست ہے", "emergency"),
 ("بچے نے زہر پی لیا", "emergency"),
 ("آدمی گر گیا اور ہوش نہیں", "emergency"),
 ("بچے کو دو دن سے بخار اور دست", "urgent"),
 ("تین دن سے الٹی نہیں رک رہی", "urgent"),
 ("پیشاب میں جلن ہے", "urgent"),
 ("زخم میں پیپ پڑ گئی ہے", "urgent"),
 ("بچے کی آنکھیں دھنس گئی ہیں", "urgent"),
 ("دو ہفتے سے کھانسی اور کمزوری", "urgent"),
 ("خونی پیچش آ رہی ہے", "urgent"),
 ("پیٹ میں شدید درد کل سے", "urgent"),
 ("ہلکا سا زکام ہے", "home"),
 ("سر میں ہلکا درد", "home"),
 ("تھوڑی سی کھانسی بخار نہیں", "home"),
 ("گلا خراب ہے صبح سے", "home"),
 ("تھکاوٹ ہے بس", "home"),
 ("ناک بند ہے", "home"),
 ("ہلکی سی خراش لگی ہے", "home"),
 # ---- Roman Urdu / English ----
 ("bacha 1 saal ka, saans lene mein bohat takleef", "emergency"),
 ("mareez bilkul behosh para hai", "emergency"),
 ("bachay ko jhatke aa rahe hain aur bukhar hai", "emergency"),
 ("aurat 8 mahine hamla, tez khoon beh raha hai", "emergency"),
 ("child 4 years cannot breathe properly, lips blue", "emergency"),
 ("bachay ne zeher kha liya", "emergency"),
 ("bacha 2 saal ka, 3 din se tez bukhar aur dast", "urgent"),
 ("teen din se ulti ruk nahi rahi", "urgent"),
 ("peshab mein jalan aur halka bukhar", "urgent"),
 ("zakhm mein peep pad gayi hai", "urgent"),
 ("child with high fever for three days", "urgent"),
 ("khoon wali pechish aa rahi hai", "urgent"),
 ("halka zukam hai", "home"),
 ("khansi thori si, bukhar nahi", "home"),
 ("mild sore throat since morning", "home"),
 ("thakan mehsoos ho rahi hai", "home"),
 ("gala kharab hai", "home"),
]

LANG_CASES = [("zehar kha lia h", "ur"), ("teen sal ka bcha", "ur"), ("بچے کو بخار ہے", "ur"), ("bacha 2 saal ka bukhar hai", "ur"),
              ("child has fever since two days", "en"), ("mild cough", "en")]

def combined(text):
    flags = check_red_flags(text)
    ml, _ = ml_predict(text)
    return "emergency" if flags else ml
def rules_only(t): return "emergency" if check_red_flags(t) else "urgent"
def ml_only(t): return ml_predict(t)[0]

def score(name, fn):
    ok, missed, wrong = 0, 0, []
    for text, exp in CASES:
        got = fn(text)
        if got == exp: ok += 1
        else: wrong.append((text, exp, got))
        if exp == "emergency" and got != "emergency": missed += 1
    print(f"{name:10s} accuracy: {ok}/{len(CASES)} = {100*ok/len(CASES):.0f}%   emergencies missed: {missed}")
    return wrong

if __name__ == "__main__":
    score("Rules", rules_only)
    score("ML", ml_only)
    wrong = score("Combined", combined)
    ok = sum(detect_language(t) == l for t, l in LANG_CASES)
    print(f"Language detection: {ok}/{len(LANG_CASES)}")
    print("\nGalat cases (Combined):")
    for t, e, g in wrong: print(f" - {t}\n     expected={e}  got={g}")
