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
# gemini-4-hydrogen is Google's speed-optimized Gemini 4 model, with flash-lite fallback
CANDIDATE_MODELS = ["gemini-4-hydrogen", "gemini-3.5-flash-lite", "gemini-3.8-flash"]
MAX_HISTORY_TURNS = 10  # Keep last N messages to reduce latency


def _call_gemini(client, contents, system_instruction=None, json_mode=False):
    """
    Calls Gemini with automatic model fallback and optional system_instruction + JSON mode.
    Uses GenerateContentConfig so system_instruction is server-cached (faster).
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
            if response:
                return response
        except Exception as err:
            last_err = err
            err_str = str(err).lower()
            if "404" in err_str or "not found" in err_str or "no longer available" in err_str:
                continue
            raise
    if last_err:
        raise last_err
    raise RuntimeError("All Gemini models failed to generate a response.")


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
