"""
AI Service for German B1 Goethe Prep Hub.
Handles Gemini API calls for modular Goethe B1 LSRW exercises and bilingual learning.
Performance: Uses system_instruction (server-cached), trimmed history, JSON mode.
"""
from typing import Tuple, List, Dict, Any, Optional
import json
import re

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

# ==============================================================================
# SHARED HELPER: Ultra-Fast Model fallback with GenerateContentConfig
# ==============================================================================
# Robust multi-model cascade across Google Gemini Free Tier models.
# Each model has independent capacity and rate limits. If one model experiences
# 503 (high demand) or 429 (rate limit), it seamlessly fails over to the next.
CANDIDATE_MODELS = [
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-4-hydrogen",
    "gemini-2.5-pro",
]
MAX_HISTORY_TURNS = 10  # Keep last N messages to reduce latency


def _call_gemini(client, contents, system_instruction=None, json_mode=False):
    """
    Calls Gemini with automatic multi-model fallback and optional system_instruction + JSON mode.
    If a model returns 503 (High Demand), 429 (Rate Limit), 500/502/504 (Server Error),
    or 404 (Not Found), it instantly and automatically falls back to the next candidate model
    so the user's practice flow is NEVER interrupted.
    """
    config_kwargs = {}
    if system_instruction:
        config_kwargs["system_instruction"] = system_instruction
    if json_mode:
        config_kwargs["response_mime_type"] = "application/json"

    config = types.GenerateContentConfig(**config_kwargs) if config_kwargs else None

    last_err = None
    for m in CANDIDATE_MODELS:
        try:
            response = client.models.generate_content(
                model=m,
                contents=contents,
                config=config
            )
            if response and response.text:
                return response
        except Exception as err:
            last_err = err
            err_str = str(err).lower()
            # If the API key is completely invalid or unauthorized, fail immediately
            if "invalid api key" in err_str or "unauthenticated" in err_str or "api_key not valid" in err_str:
                raise
            # For 503 (high demand/unavailable), 429 (quota/rate limit), 404, 500/502/504,
            # continue immediately to the next candidate model
            continue

    if last_err:
        raise last_err
    raise RuntimeError("All Gemini candidate models failed to generate a response.")


# ==============================================================================
# LSRW CHAT MODULE (Legacy — kept for backward compatibility but optimized)
# ==============================================================================

def generate_lsrw_response(
    api_key: str,
    chat_history: List[Dict[str, Any]],
    user_message: str,
    practiced_list: List[str],
    explained_list: List[str],
    has_seen_kasus: bool = False,
    current_topic: str = "",
    current_stage: str = "none"
) -> Tuple[str, Dict[str, Any]]:
    """
    Legacy LSRW chat tutor. Now uses system_instruction + trimmed history for speed.
    """
    if not api_key:
        raise ValueError("Gemini API key is required.")
    if genai is None:
        raise ImportError("google-genai library is not installed.")

    client = genai.Client(api_key=api_key)

    system_prompt = f"""You are an expert German language tutor and Goethe-Zertifikat exam trainer.
LANGUAGE RULES: Only German, Telugu, Kannada in output. Every instruction written twice: Telugu first, then Kannada.
German grammar terms stay in German. Articles: der/die/das = ఆ/ಆ, ein/eine = ఒక/ಒಬ್ಬ/ಒಂದು.
has_seen_kasus={str(has_seen_kasus).lower()}
PRACTICED LIST: {json.dumps(practiced_list, ensure_ascii=False)}
EXPLAINED LIST: {json.dumps(explained_list, ensure_ascii=False)}
CURRENT TOPIC: "{current_topic}" | STAGE: "{current_stage}"

Append at end: <!--LSRW_STATE {{"explained_list":...,"practiced_list":...,"current_topic":"...","current_stage":"...","has_seen_kasus":true/false}} -->"""

    # Trim history to last N turns
    trimmed = chat_history[-MAX_HISTORY_TURNS:]
    contents = []
    for msg in trimmed:
        role = "User" if msg["role"] == "user" else "Tutor"
        contents.append(f"{role}: {msg['content']}")
    contents.append(f"User: {user_message}")

    response = _call_gemini(client, contents, system_instruction=system_prompt)

    raw_text = response.text or ""

    parsed_state = {
        "explained_list": list(explained_list),
        "practiced_list": list(practiced_list),
        "current_topic": current_topic,
        "current_stage": current_stage,
        "has_seen_kasus": has_seen_kasus
    }

    state_match = re.search(r"<!--LSRW_STATE\s*(\{.*?\})\s*-->", raw_text, re.DOTALL)
    if state_match:
        try:
            extracted_json = json.loads(state_match.group(1))
            for k in ("explained_list", "practiced_list", "current_topic", "current_stage"):
                if k in extracted_json:
                    parsed_state[k] = extracted_json[k]
            if "has_seen_kasus" in extracted_json:
                parsed_state["has_seen_kasus"] = bool(extracted_json["has_seen_kasus"])
        except Exception:
            pass
        cleaned_reply = raw_text[:state_match.start()].strip()
    else:
        cleaned_reply = raw_text.strip()

    return cleaned_reply, parsed_state


from src.lsrw_cache import get_cached_exercise, store_cached_exercise

# ==============================================================================
# LSRW MODULAR EXERCISES — 100% DEUTSCH (LEAN 5-QUESTION EXAM CHUNKS + CACHE)
# ==============================================================================

def generate_reading_exercise(api_key: str, topics: List[str], lang: str = "de", force_refresh: bool = False) -> Dict[str, Any]:
    """
    Generates a Goethe B1 reading exercise in 100% German:
    - 1 cohesive German paragraph (100-140 words)
    - 5 fill-in-the-blank questions
    - 5 MCQ comprehension questions
    Loads in 0.001s if cached, or 5-8s on first AI call.
    """
    if not force_refresh:
        cached = get_cached_exercise("reading", topics)
        if cached:
            return cached

    if not api_key:
        raise ValueError("Gemini API key is required.")
    if genai is None:
        raise ImportError("google-genai library is not installed.")

    client = genai.Client(api_key=api_key)
    topics_str = ", ".join(topics) if topics else "allgemeine B1-Grammatik"

    system_prompt = f"""Du bist ein offizieller Prüfer für das Goethe-Zertifikat B1.
Erstelle eine Leseübung komplett und AUSSCHLIESSLICH auf Deutsch (kein Englisch, kein Telugu, kein Kannada).
Themen: {topics_str}.
Niveau: Goethe-Zertifikat B1 (GER). Ausgabe als valides JSON."""

    user_prompt = f"""Erstelle eine fokussierte B1-Leseübung als JSON mit exakt dieser Struktur:
{{
  "paragraph1": {{
    "title": "Deutscher Titel des Lesetextes",
    "text": "Ein authentischer deutscher Lesetext (100-140 Wörter) mit den Themen: {topics_str}. Alltagssituation."
  }},
  "fill_in_blanks": [
    {{
      "id": 1,
      "sentence": "Deutscher Satz mit ___ für die Lücke",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "korrekte Option",
      "topic_tested": "getestetes Grammatikthema",
      "explanation_de": "Kurze grammatische Erklärung auf Deutsch."
    }}
  ],
  "mcq": [
    {{
      "id": 1,
      "question": "Verständnisfrage oder Grammatikfrage auf Deutsch",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "korrekte Option",
      "topic_tested": "getestetes Thema",
      "explanation_de": "Erklärung auf Deutsch."
    }}
  ]
}}
Generiere EXAKT 5 fill_in_blanks und EXAKT 5 mcq Aufgaben (10 Aufgaben insgesamt). Alle Texte und Optionen MÜSSEN zu 100% auf Deutsch sein."""

    response = _call_gemini(client, [user_prompt], system_instruction=system_prompt, json_mode=True)
    try:
        data = json.loads(response.text)
        store_cached_exercise("reading", topics, data)
        return data
    except json.JSONDecodeError:
        text = response.text or ""
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            data = json.loads(match.group())
            store_cached_exercise("reading", topics, data)
            return data
        raise ValueError("Fehler beim Parsen der Leseübung.")


def generate_writing_prompt(api_key: str, topics: List[str], lang: str = "de", force_refresh: bool = False) -> Dict[str, Any]:
    """
    Generates a Goethe B1 writing task prompt in 100% German.
    """
    if not force_refresh:
        cached = get_cached_exercise("writing", topics)
        if cached:
            return cached

    if not api_key:
        raise ValueError("Gemini API key is required.")
    if genai is None:
        raise ImportError("google-genai library is not installed.")

    client = genai.Client(api_key=api_key)
    topics_str = ", ".join(topics) if topics else "allgemeine B1-Grammatik"

    system_prompt = f"""Du bist Prüfer für das Goethe-Zertifikat B1 (Schreiben).
Erstelle eine Schreibaufgabe AUSSCHLIESSLICH auf Deutsch.
Die Aufgabe erfordert die Anwendung folgender Themen: {topics_str}.
Ausgabe als valides JSON."""

    user_prompt = f"""Erstelle eine B1-Schreibaufgabe als JSON:
{{
  "type": "E-Mail oder Forumsbeitrag oder Beschwerdebrief",
  "scenario_de": "Ausführliche Beschreibung der Situation auf Deutsch (Prüfungsformat B1)",
  "instructions_de": "Genaue Arbeitsanweisungen für den Teilnehmer auf Deutsch",
  "leitpunkte": ["Leitpunkt 1 auf Deutsch", "Leitpunkt 2 auf Deutsch", "Leitpunkt 3 auf Deutsch"],
  "word_count": 80,
  "topics_focus": {json.dumps(topics)},
  "example_greeting": "Liebe/r ... oder Sehr geehrte Damen und Herren,",
  "register": "informell oder formell"
}}
Die gesamte Ausgabe muss zu 100% auf Deutsch sein."""

    response = _call_gemini(client, [user_prompt], system_instruction=system_prompt, json_mode=True)
    try:
        data = json.loads(response.text)
        store_cached_exercise("writing", topics, data)
        return data
    except json.JSONDecodeError:
        text = response.text or ""
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            data = json.loads(match.group())
            store_cached_exercise("writing", topics, data)
            return data
        raise ValueError("Fehler beim Erstellen der Schreibaufgabe.")


def evaluate_writing_submission(api_key: str, prompt_data: Dict, user_text: str, topics: List[str], lang: str = "de") -> str:
    """
    Evaluates a student's writing submission in 100% German.
    """
    if not api_key:
        raise ValueError("Gemini API key is required.")
    if genai is None:
        raise ImportError("google-genai library is not installed.")

    client = genai.Client(api_key=api_key)
    topics_str = ", ".join(topics) if topics else "allgemeine B1-Grammatik"

    system_prompt = f"""Du bist Prüfer für das Goethe-Zertifikat B1 (Schreiben).
Bewerte den Text des Teilnehmers AUSSCHLIESSLICH auf Deutsch (kein Englisch, kein Telugu, kein Kannada).
Getestete Themen: {topics_str}.
Benutze ❌ für Fehler und ✅ für gelungene Formulierungen. Vergib Punkte von 0 bis 10."""

    user_prompt = f"""SCHREIBAUFGABE:
{json.dumps(prompt_data, ensure_ascii=False)}

TEXT DES TEILNEHMERS:
{user_text}

Erstelle eine professionelle Bewertung auf Deutsch:
1. Gesamtpunktzahl: X / 10 Punkte
2. Aufgabenbewältigung (wurden alle Leitpunkte behandelt?)
3. Grammatische Analyse (insbesondere zu {topics_str}): Markiere Fehler mit ❌ und Korrekturen mit ✅
4. Wortschatz und Kohärenz (Konnektoren, Satzbau)
5. Gelungene Musterlösung (vollständiger deutscher Mustertext auf B1-Niveau)"""

    response = _call_gemini(client, [user_prompt], system_instruction=system_prompt)
    return response.text or "Bewertung fehlgeschlagen."


def generate_listening_exercise(api_key: str, topics: List[str], lang: str = "de", force_refresh: bool = False) -> Dict[str, Any]:
    """
    Generates an EASY listening exercise (1 audio per question) in 100% German:
    - 5 German sentences
    - 5 MCQ questions
    Returns structured dict in under 5 seconds.
    """
    if not force_refresh:
        cached = get_cached_exercise("listening_easy", topics)
        if cached:
            return cached

    if not api_key:
        raise ValueError("Gemini API key is required.")
    if genai is None:
        raise ImportError("google-genai library is not installed.")

    client = genai.Client(api_key=api_key)
    topics_str = ", ".join(topics) if topics else "allgemeine B1-Grammatik"

    system_prompt = f"""Du bist Prüfer für das Goethe-Zertifikat B1 (Hören).
Erstelle eine Hörverstehensübung AUSSCHLIESSLICH auf Deutsch.
Themen: {topics_str}. Ausgabe als valides JSON."""

    user_prompt = f"""Erstelle eine Hörverstehensübung mit 5 Einzelsätzen als JSON:
{{
  "items": [
    {{
      "id": 1,
      "sentence_de": "Natürlicher deutscher Satz (12-25 Wörter) auf A2/B1-Niveau",
      "question_de": "Frage zum Satz auf Deutsch",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "korrekter Optionstext",
      "topic_tested": "getestetes Grammatikthema",
      "explanation_de": "Erklärung auf Deutsch, warum diese Antwort richtig ist"
    }}
  ]
}}
Generiere EXAKT 5 Elemente. Alle Texte, Fragen und Erklärungen MÜSSEN zu 100% auf Deutsch sein."""

    response = _call_gemini(client, [user_prompt], system_instruction=system_prompt, json_mode=True)
    try:
        data = json.loads(response.text)
        store_cached_exercise("listening_easy", topics, data)
        return data
    except json.JSONDecodeError:
        text = response.text or ""
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            data = json.loads(match.group())
            store_cached_exercise("listening_easy", topics, data)
            return data
        raise ValueError("Fehler beim Erstellen der Hörverstehensübung.")


def generate_real_listening_exam(api_key: str, topics: List[str], force_refresh: bool = False) -> Dict[str, Any]:
    """
    Generates a REAL Goethe-Zertifikat B1 listening exam:
    - 1 cohesive audio passage in German (120-150 words, A2/B1 level)
    - 5 standard Goethe B1 Teil 1 multiple-choice questions
    Returns in 5-8 seconds (or 0.001s if cached).
    """
    if not force_refresh:
        cached = get_cached_exercise("listening_real", topics)
        if cached:
            return cached

    if not api_key:
        raise ValueError("Gemini API key is required.")
    if genai is None:
        raise ImportError("google-genai library is not installed.")

    client = genai.Client(api_key=api_key)
    topics_str = ", ".join(topics) if topics else "allgemeine B1-Grammatik"

    system_prompt = f"""Du bist Prüfer für das Goethe-Zertifikat (Hören).
Erstelle einen realistischen Prüfungs-Hörtext (Goethe-Zertifikat B1 Teil 1) mit 5 Multiple-Choice-Fragen.
AUSSCHLIESSLICH auf Deutsch (kein Englisch, kein Telugu, kein Kannada).
Themen: {topics_str}. Ausgabe als valides JSON."""

    user_prompt = f"""Erstelle einen zusammenhängenden Prüfungshörtext mit 5 Fragen als JSON:
{{
  "title": "Titel des Gesprächs oder der Durchsage",
  "full_audio_text": "Ein zusammenhängender deutscher Hörtext (120 bis 150 Wörter, Dialog zwischen zwei Personen oder eine Radiodurchsage). Sprachniveau A2 bis B1 mit den Grammatikthemen: {topics_str}.",
  "questions": [
    {{
      "id": 1,
      "question_de": "Frage zum Hörtext auf Deutsch",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "korrekter Optionstext",
      "explanation_de": "Kurze Erklärung auf Deutsch mit Bezug auf den Hörtext"
    }}
  ]
}}
Generiere EXAKT 5 Fragen zum Hörtext (Goethe-Standard Teil 1). Alle Fragen und Optionen MÜSSEN zu 100% auf Deutsch sein."""

    response = _call_gemini(client, [user_prompt], system_instruction=system_prompt, json_mode=True)
    try:
        data = json.loads(response.text)
        store_cached_exercise("listening_real", topics, data)
        return data
    except json.JSONDecodeError:
        text = response.text or ""
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            data = json.loads(match.group())
            store_cached_exercise("listening_real", topics, data)
            return data
        raise ValueError("Fehler beim Erstellen der echten Hörprüfung.")


def generate_speaking_cards(api_key: str, topics: List[str], force_refresh: bool = False) -> List[Dict[str, str]]:
    """
    Generates 8 speaking topic cards in 100% German for the solitaire-style card flip.
    """
    if not force_refresh:
        cached = get_cached_exercise("speaking", topics)
        if cached and isinstance(cached, list):
            return cached

    if not api_key:
        raise ValueError("Gemini API key is required.")
    if genai is None:
        raise ImportError("google-genai library is not installed.")

    client = genai.Client(api_key=api_key)
    topics_str = ", ".join(topics) if topics else "allgemeine B1-Themen"

    system_prompt = """Du bist Prüfer für das Goethe-Zertifikat B1 (Sprechen).
Erstelle 8 Themenkarten AUSSCHLIESSLICH auf Deutsch. Ausgabe als valides JSON."""

    user_prompt = f"""Erstelle 8 Sprechkarten als JSON:
{{
  "cards": [
    {{
      "id": 1,
      "topic_de": "Deutsches Thema (z.B. Spielen, Reisen, Wohnen, Gesundheit, Umweltschutz, Arbeit)",
      "hint_de": "Kurzer deutscher Leitfaden/Impuls, worüber der Teilnehmer sprechen soll (2-3 Sätze)",
      "grammar_focus": "Grammatikalischer Schwerpunkt aus: {topics_str}"
    }}
  ]
}}
Generiere 8 Karten. Alles muss zu 100% auf Deutsch sein."""

    response = _call_gemini(client, [user_prompt], system_instruction=system_prompt, json_mode=True)
    try:
        data = json.loads(response.text)
        cards = data.get("cards", [])
        if cards:
            store_cached_exercise("speaking", topics, cards)
        return cards
    except json.JSONDecodeError:
        fallback = [
            {"id": i + 1, "topic_de": t, "hint_de": f"Sprechen Sie über Ihre persönlichen Erfahrungen mit {t}.", "grammar_focus": topics_str}
            for i, t in enumerate(["Spielen", "Reisen", "Familie", "Arbeit", "Essen", "Gesundheit", "Freizeit", "Wohnung"])
        ]
        store_cached_exercise("speaking", topics, fallback)
        return fallback


def evaluate_speaking_response(
    api_key: str,
    topic: str,
    grammar_focus: str,
    lang: str = "de",
    raw_audio: Optional[bytes] = None,
    audio_mime: str = "audio/wav",
    typed_text: Optional[str] = None
) -> str:
    """
    Evaluates a student's spoken German in 100% German.
    """
    if not api_key:
        raise ValueError("Gemini API key is required.")
    if genai is None:
        raise ImportError("google-genai library is not installed.")

    client = genai.Client(api_key=api_key)

    system_prompt = f"""Du bist Prüfer für das Goethe-Zertifikat B1 (Sprechen).
Bewerte die mündliche Leistung des Teilnehmers AUSSCHLIESSLICH auf Deutsch (kein Englisch, kein Telugu, kein Kannada).
Thema: "{topic}".
Grammatischer Fokus: {grammar_focus}.
Vergib Punkte von 0 bis 10. Markiere Fehler mit ❌ und Korrekturen mit ✅."""

    contents = []
    if raw_audio is not None and types is not None:
        contents.append(f"Der Teilnehmer sprach zum Thema: {topic} (Fokus: {grammar_focus})")
        contents.append(types.Part.from_bytes(data=raw_audio, mime_type=audio_mime))
    elif typed_text:
        contents.append(f"Der Teilnehmer sprach zum Thema: {topic} (Fokus: {grammar_focus})")
        contents.append(f"Teilnehmer sagte: {typed_text}")
    else:
        return "Keine Audio- oder Texteingabe empfangen."

    contents.append(f"""Erstelle eine mündliche Prüfungsbewertung komplett auf Deutsch:
1. Gesamtpunktzahl: X / 10 Punkte
2. Transkription des Gesagten (Deutsch)
3. Grammatische Analyse (insbesondere zu {grammar_focus}): ❌ Fehler und ✅ Korrekturen
4. Flüssigkeit, Aussprache und Wortschatz
5. Deutsche Musterantwort (Musterpräsentation auf B1-Niveau zum Thema "{topic}")""")

    response = _call_gemini(client, contents, system_instruction=system_prompt)
    return response.text or "Bewertung fehlgeschlagen."


# ==============================================================================
# GRAMMAR LEARNING MODULE: Bilingual Explanation (Telugu & Kannada Strictly)
# ==============================================================================

def generate_topic_explanation(
    api_key: str,
    topic: str,
    depth: str = "overview",
    has_seen_kasus: bool = False,
    force_refresh: bool = False
) -> str:
    """
    Generates a bilingual German grammar explanation strictly in Telugu and Kannada.
    NO English is used except in Section 0 (Topic title, level).
    Depth: 'overview' (concise) or 'indetail' (deep dive).
    """
    depth_clean = "overview" if "overview" in depth.lower() else "indetail"
    if not force_refresh:
        cached = get_cached_exercise("explanation", [topic], extra=depth_clean)
        if cached:
            # If cached as dict with "text" or str
            if isinstance(cached, dict) and "text" in cached:
                return cached["text"]
            if isinstance(cached, str):
                return cached

    if not api_key:
        raise ValueError("Gemini API key is required.")
    if genai is None:
        raise ImportError("google-genai library is not installed.")

    client = genai.Client(api_key=api_key)

    is_overview = (depth_clean == "overview")
    depth_instructions = """
    DEPTH: OVERVIEW (సమీక్ష / ಅವಲೋಕನ)
    - Keep explanation concise, punchy, and clear.
    - Rule definition (Telugu line first, then Kannada line next).
    - 3-4 golden German example sentences labeled with [Neutral], [Schriftlich (Prüfung)], or [Gesprochen (Alltag)].
    - Each example must have Telugu translation on one line, and Kannada translation on the next line.
    - 1 practical Goethe B1 exam tip (Telugu line first, then Kannada line next).
    """ if is_overview else """
    DEPTH: IN-DETAIL (వివరణాత్మక / ವಿವರವಾದ)
    - Comprehensive step-by-step breakdown.
    - Full explanation of rules, formation, and Wortstellung (Telugu line first, then Kannada line next).
    - Exceptions and prepositions / endings guide.
    - 6+ distinct German example sentences covering all registers [Neutral], [Schriftlich (Prüfung)], [Gesprochen (Alltag)].
    - Each example must have Telugu translation on one line, and Kannada translation on the next line.
    - Common Goethe B1 exam traps and mistakes to avoid (Telugu line first, then Kannada line next).
    """

    system_prompt = f"""You are an expert German language tutor and Goethe-Zertifikat exam trainer.
Explain the German grammar topic "{topic}".

==================================================
LANGUAGE RULES (Strict, apply to the entire output)
==================================================
1. You NEVER write English, except in Section 0 (Topic name, level e.g. B1, one-line intro).
2. ONLY THREE LANGUAGES appear in the output: German, Telugu, Kannada.
3. Every explanation, rule, note, correction, instruction, and heading is written TWICE: Telugu first, then Kannada on the next line. Same content, same order.
4. German examples are in German. Every German sentence gets a Telugu translation on the next line and a Kannada translation on the following line.
5. German grammar terms stay in German and are never translated: Nominativ, Akkusativ, Dativ, Genitiv, Nomen, Artikel, Endung, Adjektiv, Verb, Nebensatz, Wortstellung, Singular, Plural, Präposition, etc.
6. KASUS REFERENCE (Include once at the beginning of the explanation):
   Nominativ = ఎవరు / ಯಾರು (Subjekt)
   Akkusativ = ఎవరిని / ಯಾರನ್ನು
   Dativ = ఎవరికి / ಯಾರಿಗೆ
   Genitiv = ఎవరి / ಯಾರ
7. TRANSLATING ARTICLES:
   - der / die / das = specific: translate as ఆ (Telugu) / ಆ (Kannada), e.g., "der Junge" = ఆ అబ్బాయి / ಆ ಹುಡುಗ.
   - ein / eine = ఒక (Telugu); in Kannada use ಒಬ್ಬ for a person and ಒಂದು for a thing or animal.
   - In general statements, do NOT add ఆ / ಆ.
8. German examples are B1 level or below by default.
9. REGISTER RULE:
   Every example sentence must be labeled with one of the registers:
   - [Neutral]
   - [Schriftlich (Prüfung)]
   - [Gesprochen (Alltag)]

{depth_instructions}
"""

    user_prompt = f"""దయచేసి '{topic}' అంశాన్ని {'సమీక్ష (Overview)' if is_overview else 'వివరణాత్మకంగా (In-detail)'} తెలుగు మరియు కన్నడలలో వివరించండి.
ದಯವಿಟ್ಟು '{topic}' ವಿಷಯವನ್ನು {'ಅವಲೋಕನ (Overview)' if is_overview else 'ವಿವರವಾಗಿ (In-detail)'} ತೆಲುಗು ಮತ್ತು ಕನ್ನಡದಲ್ಲಿ ವಿವರಿಸಿ."""

    response = _call_gemini(client, [user_prompt], system_instruction=system_prompt)
    result_text = response.text or ""

    if result_text:
        store_cached_exercise("explanation", [topic], {"text": result_text}, extra=depth_clean)

    return result_text


# ==============================================================================
# DYNAMIC TOPIC QUESTION GENERATOR (GOETHE B1 LEVEL)
# ==============================================================================

STARTER_TOPIC_QUESTIONS = {
    "weak masculine declination (n-deklination)": [
        {
            "topic": "Weak Masculine Declination (N-Deklination)",
            "prompt_te": "నేను ఆ విద్యార్థిని (student) లైబ్రరీలో కలిశాను.",
            "prompt_kn": "ನಾನು ಆ ವಿದ್ಯಾರ್ಥಿಯನ್ನು (student) ಗ್ರಂಥಾಲಯದಲ್ಲಿ ಭೇಟಿಯಾದೆ.",
            "target_de": "Ich habe den Studenten in der Bibliothek getroffen.",
            "options": [
                "Ich habe den Student in der Bibliothek getroffen.",
                "Ich habe den Studenten in der Bibliothek getroffen.",
                "Ich habe dem Student in der Bibliothek getroffen.",
                "Ich habe des Studenten in der Bibliothek getroffen."
            ],
            "correct_index": 1,
            "explanation": "'treffen' requires Akkusativ. 'der Student' is a weak masculine noun (N-Deklination), adding -(e)n in all cases except Nominativ Singular -> 'den Studenten'.",
            "case": "Akkusativ",
            "gender": "Maskulin (N-Deklination)"
        },
        {
            "topic": "Weak Masculine Declination (N-Deklination)",
            "prompt_te": "వైద్యుడు ఆ రోగికి (patient) చాలా ఓపికగా సహాయం చేస్తున్నాడు.",
            "prompt_kn": "ವೈದ್ಯರು ಆ ರೋಗಿಗೆ (patient) ಬಹಳ ತಾಳ್ಮೆಯಿಂದ ಸಹಾಯ ಮಾಡುತ್ತಿದ್ದಾರೆ.",
            "target_de": "Der Arzt hilft dem Patienten sehr geduldig.",
            "options": [
                "Der Arzt hilft dem Patient sehr geduldig.",
                "Der Arzt hilft den Patienten sehr geduldig.",
                "Der Arzt hilft dem Patienten sehr geduldig.",
                "Der Arzt hilft des Patienten sehr geduldig."
            ],
            "correct_index": 2,
            "explanation": "'helfen' takes Dativ. 'der Patient' belongs to N-Deklination, so Dativ Singular is 'dem Patienten'.",
            "case": "Dativ",
            "gender": "Maskulin (N-Deklination)"
        },
        {
            "topic": "Weak Masculine Declination (N-Deklination)",
            "prompt_te": "మేము మా కొత్త పొరుగువారితో (neighbor) తరచుగా మాట్లాడుతాము.",
            "prompt_kn": "ನಾವು ನಮ್ಮ ಹೊಸ ನೆರೆಹೊರೆಯವರೊಂದಿಗೆ (neighbor) ಆಗಾಗ ಮಾತನಾಡುತ್ತೇವೆ.",
            "target_de": "Wir sprechen oft mit unserem neuen Nachbarn.",
            "options": [
                "Wir sprechen oft mit unserem neuen Nachbar.",
                "Wir sprechen oft mit unserem neuen Nachbarn.",
                "Wir sprechen oft mit unseren neuen Nachbar.",
                "Wir sprechen oft mit unserem neuem Nachbarn."
            ],
            "correct_index": 1,
            "explanation": "Preposition 'mit' governs Dativ. 'der Nachbar' is an N-Deklination noun, taking '-n' -> 'unserem neuen Nachbarn'.",
            "case": "Dativ",
            "gender": "Maskulin (N-Deklination)"
        },
        {
            "topic": "Weak Masculine Declination (N-Deklination)",
            "prompt_te": "బెర్లిన్ నుండి వచ్చిన ఈ ప్రసిద్ధ ఫోటోగ్రాఫర్ (photographer) నీకు తెలుసా?",
            "prompt_kn": "ಬರ್ಲಿನ್‌ನ ಈ ಪ್ರಸಿದ್ಧ ಛಾಯಾಗ್ರಾಹಕ (photographer) ನಿನಗೆ ಗೊತ್ತೇ?",
            "target_de": "Kennst du diesen bekannten Fotografen aus Berlin?",
            "options": [
                "Kennst du dieser bekannte Fotograf aus Berlin?",
                "Kennst du diesem bekannten Fotografen aus Berlin?",
                "Kennst du diesen bekannten Fotografen aus Berlin?",
                "Kennst du diesen bekannten Fotograf aus Berlin?"
            ],
            "correct_index": 2,
            "explanation": "'kennen' takes Akkusativ object. 'der Fotograf' is N-Deklination -> 'diesen bekannten Fotografen'.",
            "case": "Akkusativ",
            "gender": "Maskulin (N-Deklination)"
        },
        {
            "topic": "Weak Masculine Declination (N-Deklination)",
            "prompt_te": "పోలీసు ఆ ప్రమాదం గురించి సాక్షిని (witness) ప్రశ్నిస్తున్నాడు.",
            "prompt_kn": "ಪೊಲೀಸರು ಅಪಘಾತದ ಬಗ್ಗೆ ಸಾಕ್ಷಿಯನ್ನು (witness) ವಿಚಾರಿಸುತ್ತಿದ್ದಾರೆ.",
            "target_de": "Der Polizist befragt den Zeugen zum Unfall.",
            "options": [
                "Der Polizist befragt der Zeuge zum Unfall.",
                "Der Polizist befragt den Zeugen zum Unfall.",
                "Der Polizist befragt dem Zeugen zum Unfall.",
                "Der Polizist befragt den Zeuge zum Unfall."
            ],
            "correct_index": 1,
            "explanation": "'befragen' takes Akkusativ. 'der Zeuge' ends in -e and is masculine N-Deklination -> 'den Zeugen'.",
            "case": "Akkusativ",
            "gender": "Maskulin (N-Deklination)"
        }
    ]
}


def generate_topic_questions(
    topic: str,
    category: str = "pronoun",
    count: int = 5,
    api_key: str = "",
    past_topics: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Generates Goethe B1 level questions for a newly unlocked grammar topic.
    Combines vocabulary from Goethe B1 Wortliste and reinforces past topics.
    Returns a list of standardized question dicts.
    """
    clean_topic = topic.strip()
    topic_key = clean_topic.lower()

    # If key is missing, check starter templates
    for starter_key, q_list in STARTER_TOPIC_QUESTIONS.items():
        if starter_key in topic_key or topic_key in starter_key:
            return q_list

    if not api_key:
        return STARTER_TOPIC_QUESTIONS.get("weak masculine declination (n-deklination)", [])

    client = _get_client(api_key)
    past_topics_str = ", ".join(past_topics) if past_topics else "Possessivartikel in Nominativ/Akkusativ/Dativ/Genitiv"

    system_instruction = f"""You are an elite Goethe-Institut German B1 exam creator.
Generate authentic, high-quality multiple choice German questions for the grammar topic: '{clean_topic}'.

RULES:
1. German level must strictly be Goethe-Zertifikat B1.
2. Incorporate real Goethe B1 Wortliste vocabulary.
3. If appropriate, subtly combine this with prior learned topics ({past_topics_str}).
4. For each question, provide:
   - prompt_te: Natural, grammatically accurate translation in Telugu.
   - prompt_kn: Natural, grammatically accurate translation in Kannada.
   - target_de: The correct full German sentence.
   - options: Array of 4 German options. Only ONE is grammatically correct. The other 3 must reflect common student errors (wrong ending, wrong case, incorrect article).
   - correct_index: Integer 0, 1, 2, or 3 indicating the index of the correct option in the options array.
   - explanation: Clear, concise explanation in English of why the correct option is right and the grammar rule applied.
   - case: e.g. "Akkusativ", "Dativ", "Nominativ", etc.
   - gender: e.g. "Maskulin", "Feminin", "Neutral", etc.
5. Return strictly valid JSON array of objects.
"""

    user_prompt = f"""Generate {count} distinct Goethe B1 questions for the topic '{clean_topic}'.
Format as JSON array of objects with keys: topic, prompt_te, prompt_kn, target_de, options, correct_index, explanation, case, gender."""

    try:
        response = _call_gemini(client, [user_prompt], system_instruction=system_instruction, json_mode=True)
        text = response.text or ""
        # Clean markdown wrappers if any
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        parsed = json.loads(text)
        if isinstance(parsed, list) and len(parsed) > 0:
            for idx, q in enumerate(parsed, start=1001):
                q["id"] = idx
                q["topic"] = clean_topic
                q["category"] = category
            return parsed
    except Exception as e:
        logger.warning(f"Gemini topic question generation failed: {e}")

    # Fallback to starter questions if API failed
    return STARTER_TOPIC_QUESTIONS.get("weak masculine declination (n-deklination)", [])

