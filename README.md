# 🇩🇪 German B1 Daily Duel (Telugu & Kannada $\rightarrow$ German)

An interactive, 3-player competitive learning app with **162 comprehensive questions** designed to master German B1 **Possessivartikel (Possessive Determiners)** across **Nominativ, Akkusativ, Dativ, and Genitiv** using authentic vocabulary from the official **Goethe-Zertifikat B1 Wortliste**.

---

## 🌐 Real-Time Sharing (How to Use Your PC as a Server)

You and your friends can play together in real time from phones, tablets, or laptops while this PC is running!

### Option 1: On the Same Wi-Fi / Local Network
If your friends are in the same house, room, or connected to the same Wi-Fi router:
- Double click **`run_app.bat`**
- Give your friends your Wi-Fi URL:
  ```
  http://192.168.158.14:8501
  ```
- They can open it directly in Chrome/Safari on their smartphones!

### Option 2: Internet Sharing (Anywhere in the World / Mobile Data)
If your friends are in different locations or using mobile data:
- Double click **`share_with_friends.bat`**
- This automatically starts the server and opens a secure **Cloudflare Tunnel** (pre-installed on your system).
- It will display a public HTTPS link (e.g. `https://xxxx.trycloudflare.com`).
- Send that link to your friends on WhatsApp—they can play in real time with you!

### Option 3: Tailscale Mesh Network
Both you and your friends can connect securely via your machine's Tailscale IP:
```
http://100.101.253.123:8501
```

---

## ✨ Features

1. **162 High-Quality B1 Questions**:
   - Covers 33 distinct Day Packs (5 questions each) covering verbs, prepositions, cases, and genders.
   - Choose between **Today's Challenge (date-seeded)** or **Day Pack Selector (1 to 33)** for extra practice rounds 3 times a week!
2. **Strict Language Isolation**:
   - Selecting **Telugu (తెలుగు)** displays **ONLY** Telugu sentence prompts.
   - Selecting **Kannada (ಕನ್ನಡ)** displays **ONLY** Kannada sentence prompts.
3. **3-Player Competition & Custom Profiles**:
   - Supports 3 players with customizable names, avatars, and email addresses.
4. **Multi-Attempt Score Normalization**:
   - If a player retries multiple times, scores are normalized to their daily average:
     $$\text{Daily Average} = \frac{\text{Total Marks}}{\text{Number of Attempts}}$$
   - Leaderboard ranks players by normalized average with best-score tiebreaker.
5. **Real Email Notifications**:
   - When a player submits their test, an alert email can be automatically dispatched to notify the other 2 players with their score.
6. **Native Audio Pronunciation (TTS)**:
   - Built-in **🔊 Hören (Audio)** button on every German sentence using browser speech synthesis.
7. **Color-Coded Possessivartikel Master Chart**:
   - Complete reference table from your study image embedded in the app.
8. **Pure Voice-to-Voice Speaking Practice (Frau Wagner AI)**:
   - **Blind Audio Mode**: Frau Wagner's German text is hidden so your oral listening comprehension is tested under real Goethe B1 exam conditions.
   - **Microphone Input**: Speak in German via your microphone (no typing needed).
   - **Instant Feedback**: Spoken German reply with audio waveforms, replay buttons, and an expandable transcript with Telugu/Kannada grammar corrections.
   - **Free AI Key**: Uses Google Gemini 3.8 Flash free tier (15 requests/minute). Get key free at [Google AI Studio](https://aistudio.google.com/app/apikey).

---

## 🛠️ Build System & Project Automation (Gradle-Style)

The project includes a standard build configuration [pyproject.toml](file:///c:/Users/PRABU/OneDrive/Documents/German_App/pyproject.toml) (PEP 517/518/621) and a Gradle-like build runner [build.bat](file:///c:/Users/PRABU/OneDrive/Documents/German_App/build.bat) / [build.py](file:///c:/Users/PRABU/OneDrive/Documents/German_App/build.py):

| Gradle Command | Python Equivalent | Purpose |
|:---|:---|:---|
| `gradle run` | `build run` or `python build.py run` | Starts the Streamlit application server |
| `gradle test` | `build test` or `python build.py test` | Runs automated verification tests |
| `gradle build` | `build build` or `python build.py build` | Compiles sources, checks templates, runs test suite |
| `gradle clean` | `build clean` or `python build.py clean` | Removes bytecode, cache, and build artifacts |
| `gradle tasks` | `build tasks` or `python build.py tasks` | Displays all available build tasks |

---

## 📁 Modular Project Structure

```
German_App/
│
├── pyproject.toml              # Build & dependency specification (equivalent to build.gradle)
├── requirements.txt            # Streamlit Cloud deployment requirements
├── build.py / build.bat        # Gradle-like task runner CLI
├── app.py                      # Clean application entry point & router (< 80 lines)
│
├── static/                     # External Static Resources
│   ├── css/
│   │   └── main.css            # All styles, animations, and typography
│   └── templates/
│       ├── timer.html          # 50s Per-Question Countdown Timer template
│       ├── voice_bubble.html   # Blind Audio Player & Replay Voice template
│       ├── confetti.html       # Web Audio & Particle Confetti burst template
│       └── grammar_chart.html  # Possessivartikel color-coded master table
│
├── src/                        # Python Source Modules
│   ├── config.py               # Paths, constants, and resource loaders
│   ├── ai_service.py           # Gemini 3.8 Flash speaking conversation engine
│   ├── components/             # Reusable UI component wrappers
│   │   ├── timer.py            # Timer component
│   │   ├── audio_bubble.py     # Blind Audio Bubble component
│   │   ├── confetti.py         # Confetti celebration component
│   │   └── chart.py            # Master Grammar Chart component
│   └── views/                  # Streamlit Page Views
│       ├── home_view.py        # Exam Portal Dashboard (4 modules + Daily Duel)
│       ├── speaking_view.py    # Blind Voice-to-Voice AI Avatar Arena
│       ├── quiz_view.py        # Lobby, Arena (50s timer), and Results/Scoreboard
│       └── chart_view.py       # Full grammar reference view
│
├── questions_bank.json         # 162 verified Goethe B1 questions
├── duel_data.json              # Clean persistent player & attempt storage
└── storage.py / questions.py   # Core data services
```
