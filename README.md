# 🇩🇪 German Goethe-Zertifikat B1 Hub

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://deutsch-b1.streamlit.app)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

### 🚀 Live Web Application
👉 **Click here to practice online:** **[https://deutsch-b1.streamlit.app](https://deutsch-b1.streamlit.app)**

> *No installation or setup required. Works instantly on mobile phones, tablets, and laptops.*

---

## 📖 About The Project

An interactive German Goethe-Zertifikat B1 preparation platform designed for South Indian language speakers, featuring **strict bilingual pedagogical instruction in Telugu (తెలుగు) and Kannada (ಕನ್ನಡ)** without reliance on English.

---

## ✨ Modules & Features

### 1. 🎯 Pronoun Duel (Possessivartikel)
* **162 Goethe B1 Questions** covering Nominativ, Akkusativ, Dativ, and Genitiv.
* 33 distinct Day Packs (5 questions each) covering cases, genders, and verb prepositions.
* Strict language isolation: choose between **Telugu (తెలుగు)** or **Kannada (ಕನ್ನಡ)** prompt sentences.
* 50-second timer per question with auto-advance and instant answer resolution.

### 2. 🏷️ Gender Duel (Der / Die / Das)
* **522 Verified Nouns** from the official Goethe-Zertifikat B1 Wortliste.
* Type or select `der`, `die`, or `das` with plural forms and English reference meanings.
* Dedicated high-score leaderboard and progress tracking.

### 3. 🎓 Goethe B1 Meisterstudio (LSRW)
* **🧠 Lernen (Grammar Studio):**
  * Choose any grammar topic (e.g., *Akkusativ, Dativ, Wechselpräpositionen, Konjunktiv II, Passiv, Relativsatz*).
  * Select depth: **⚡ Overview (సమీక్ష / ಅವಲೋಕನ)** or **📚 In-Detail (వివరణాత్మక / ವಿವರವಾದ)**.
  * Comprehensive grammar rules written strictly in **Telugu first, then Kannada on the next line (Zero English)**.
* **📖 Lesen (Reading):**
  * Real Goethe-style blog posts and articles with 5 fill-in-the-blank grammar questions + 5 comprehension MCQs.
* **✍️ Schreiben (Writing):**
  * Formal & informal email/letter tasks based on real Goethe B1 situations with AI grammatical evaluation and feedback.
* **🎧 Hören (Listening):**
  * Blind audio mode using German speech synthesis.
  * **Modus Einfach:** 5 individual spoken sentences with hidden text.
  * **Echter Prüfungsmodus:** 1 cohesive 150-word dialogue/announcement with a strict **max 2x play limit** and 5 Goethe Teil 1 MCQs.
* **🔄 Seamless Practice Loop:**
  * Automatically transitions from *Lernen ➔ Schreiben ➔ Lesen ➔ Hören* with 1-click continuation.

### 4. 📊 Master Possessivartikel Chart
* Complete color-coded reference table covering Nom, Akk, Dat & Gen embedded directly in the app.

---

## 🔒 Security & Privacy Notice

* **Zero Hardcoded Secrets:** All private credentials and API keys are strictly loaded via Streamlit Cloud Secrets (`st.secrets`) and environment variables (`.env`).
* This repository contains **NO API keys, passwords, or personal credentials**.
* If running locally, place your Gemini API key in `.streamlit/secrets.toml` (which is permanently excluded via `.gitignore`).

---

## 💻 Local Development Setup (Optional)

If you wish to run the app locally on your machine:

```bash
# 1. Clone the repository
git clone https://github.com/prabup1616-ops/Deustch_App.git
cd Deustch_App

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your Gemini API Key in .streamlit/secrets.toml
# GEMINI_API_KEY = "your-api-key"

# 4. Start the application
streamlit run app.py
```

---

## 👨‍💻 Author

Developed by **[prabup1616-ops](https://github.com/prabup1616-ops)**.
