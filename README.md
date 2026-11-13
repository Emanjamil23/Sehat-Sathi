# 🩺 Sehat Sathi (صحت ساتھی)

**A health triage helper for village families, in Urdu, Roman Urdu and English.**

Live app: https://sehat-sathi-guyvpuhbyyzyi9tklytzxj.streamlit.app/

> ⚠️ **Prototype only.** Sehat Sathi does not diagnose and does not replace a doctor. The training data is synthetic and has not been checked by doctors.

---

## The problem

In many villages the nearest doctor or hospital is hours away. When someone falls sick, the family often cannot tell if it is a small problem or a danger sign. They either wait too long with a serious case, or rush to the city for a small cold.

## Our solution

Sehat Sathi tells the family what to do **in the meantime**. The user speaks or types the symptoms and gets one clear answer in seconds:

| Level | Meaning |
|---|---|
| 🔴 Emergency | Go to the nearest hospital now |
| 🟠 Urgent | See a doctor today |
| 🟢 Home care | Safe care at home, with simple steps |

---

## Features

- **Speak or type:** mic input in Urdu, or write in Urdu, Roman Urdu or English.
- **Red-flag detection:** finds danger signs like breathing trouble, unconscious, fits, stiff neck, chest pain, poison, baby not feeding.
- **Age, pregnancy and duration checks:** raises the level when needed (for example a very young baby, or a cough for weeks).
- **Follow-up questions:** asks up to 3 extra questions to understand the case better.
- **Home care steps:** simple advice while waiting for the doctor.
- **Safe medicines list:** a fixed whitelist only (paracetamol, ORS, zinc, saline drops, lozenge, antacid, antiseptic). No doses, no antibiotics, no ibuprofen, no aspirin.
- **Listen:** reads the answer aloud for people who cannot read well.
- **Patient records and dashboard:** saves every case, shows totals and a triage chart.
- **Downloads:** a printable medical slip for each patient, and a CSV file of all records.
- **Works without internet or API key:** rules and the ML model run offline.

---

## How it works

```
Patient symptoms
      │
      ├─► 1. Red-flag rules      (offline)
      ├─► 2. ML model            (offline)
      ├─► 3. Gemini LLM          (optional, free tier)
      │
      ▼
 4. Safety rule: the HIGHEST level wins
    (Gemini can only raise the level, never lower it)
      │
      ▼
 Emergency / Urgent / Home care + steps
```

### The data

- **3,150 sentences** in `data/triage_data.csv`.
- **3 languages:** Urdu, Roman Urdu, English.
- **3 labels:** emergency, urgent, home (1,050 each).
- **Synthetic:** `train_triage.py` builds each sentence from hand-written symptom phrases, mixed with age words (child, woman, elderly) and time words (since yesterday, two days).

### The ML model

- **TF-IDF** on character pieces (2 to 5 letters), so spelling mistakes in Roman Urdu still work.
- **Logistic Regression** gives a percentage for each level and shows the highest.
- **Class weights:** emergency x3, urgent x1.5, home x1, so the model rarely misses a danger case.

### The LLM layer (Gemini)

The LLM layer uses the **Google Gemini API on the free tier**. It is optional and does four jobs:

1. A second opinion on the urgency level.
2. A short reason in Urdu and English.
3. Possible causes, home tips and follow-up questions.
4. Symptom tags when Roman Urdu spelling is unusual.

Gemini **never** writes medicine names or doses. Medicines come only from the fixed list in `home_care.py`. If the key is missing, there is no internet, or any error happens, the app continues without it.

---

## Results

Run `python evaluate.py` to reproduce.

| Method | Accuracy (41 test sentences) | Emergencies missed |
|---|---|---|
| Rules only | 59% | 5 |
| ML only | 85% | 1 |
| **Rules + ML (combined)** | **88%** | **0** |

- All 5 mistakes of the combined method were on the safe side (more careful, never less).
- On 18 held-out sentences in `train_triage.py`: **89%** accuracy and **0 emergencies missed**.

> These test sentences were written by the project author, not by doctors. The scores do **not** prove clinical safety.

---

## Project structure

```
SehatSathi_v3/
├── app.py                  # Streamlit app (UI, records, downloads)
├── ui_parts.py             # Result cards, report (medical slip) HTML
├── train_triage.py         # Builds the data and trains the model
├── evaluate.py             # Rules vs ML vs combined test
├── test_home_care.py       # Safety tests for home care and medicines
├── test_gemini.py          # Checks your Gemini key
├── data/triage_data.csv    # Training data (3,150 rows)
├── ml/triage_model.joblib  # Trained model
└── sehatsathi/backend/
    ├── main.py             # FastAPI /triage endpoint and final decision
    ├── red_flags.py        # Danger-sign rules and text cleaning
    ├── ml_model.py         # Loads the model and predicts
    ├── home_care.py        # Age/duration checks, home care, safe medicines
    ├── llm.py              # Gemini (or Claude) assessment layer
    └── messages.py         # Urdu and English texts, language detection
```

---

## Run it yourself

**1. Install**

```bash
cd SehatSathi_v3
pip install -r requirements.txt
```

**2. Add your Gemini key (optional)**

Create a file named `.env` in the `SehatSathi_v3` folder:

```
GEMINI_API_KEY=your-key-here
```

Get a free key from Google AI Studio. Without a key the app still works with rules and ML only.

**3. Train the model (optional, a trained model is included)**

```bash
python train_triage.py
```

**4. Start the app**

```bash
streamlit run app.py
```

The app starts the backend itself on port 8000. To run the backend alone:

```bash
uvicorn main:app --reload --app-dir sehatsathi/backend
```

On Windows you can also double-click `1_train_model.bat`, `2_run_backend.bat` and `3_run_ui.bat`.

**5. Run the tests**

```bash
python evaluate.py
python test_home_care.py
```

---

## Limits and next steps

**Limits**
- Synthetic data, not checked by doctors.
- Small test set written by the author.
- Language detection needs more work.
- Gemini free tier has usage limits.

**Next steps**
- Doctor review of the rules, the data and the medicine list.
- Real village health data.
- Offline Urdu voice input.
- SMS or WhatsApp access.
- A pilot with community health workers.

---

## Disclaimer

Sehat Sathi is a hackathon prototype for learning and demonstration. It is not a medical device. In any emergency, go to the nearest hospital or call local emergency services.
