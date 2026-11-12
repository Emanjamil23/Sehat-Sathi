import joblib, os
from red_flags import normalize

BASE = os.path.dirname(os.path.abspath(__file__))
model = joblib.load(os.path.join(BASE, "..", "..", "ml", "triage_model.joblib"))
ORDER = {"home": 0, "urgent": 1, "emergency": 2}

def ml_predict(text):
    probs = dict(zip(model.classes_, model.predict_proba([normalize(text)])[0]))
    return max(probs, key=probs.get), probs
