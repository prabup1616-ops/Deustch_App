"""
Goethe B1 German Gender / Artikel Questions Bank Loader.
Loads verified Goethe B1 Wortliste nouns with articles (der/die/das),
plural forms, English meanings, Telugu meanings, and Kannada meanings.
"""

import json
import os
import hashlib
from typing import List, Dict, Any

from src.config import GENDER_QUESTIONS_FILE as JSON_PATH


def load_all_gender_questions() -> List[Dict[str, Any]]:
    if not os.path.exists(JSON_PATH):
        try:
            from scripts import generate_gender_questions
            generate_gender_questions.build_gender_questions()
        except Exception:
            pass
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


GENDER_QUESTIONS_DATA = load_all_gender_questions()


def get_daily_gender_questions(date_str: str, count: int = 5) -> List[Dict[str, Any]]:
    """
    Returns a deterministic set of 5 gender questions for a specific calendar date (YYYY-MM-DD),
    so all players receive the same 5 nouns on that day.
    """
    total = len(GENDER_QUESTIONS_DATA)
    if total == 0:
        return []
    # Deterministic hash seed using 'gender_' prefix to differ from pronoun daily questions
    h = int(hashlib.md5(f"gender_{date_str}".encode("utf-8")).hexdigest(), 16)
    indices = []
    for i in range(count):
        idx = (h + i * 17) % total
        while idx in indices:
            idx = (idx + 1) % total
        indices.append(idx)
    return [GENDER_QUESTIONS_DATA[idx] for idx in indices]


def get_gender_pack_questions(pack_number: int, count: int = 5) -> List[Dict[str, Any]]:
    """
    Returns 5 consecutive questions for a specific pack (e.g. Pack 1 to 104),
    allowing players to practice specific batches of Goethe B1 nouns.
    """
    total = len(GENDER_QUESTIONS_DATA)
    if total == 0:
        return []
    start_idx = ((pack_number - 1) * count) % total
    selected = []
    for i in range(count):
        selected.append(GENDER_QUESTIONS_DATA[(start_idx + i) % total])
    return selected


def get_total_gender_packs(count: int = 5) -> int:
    total = len(GENDER_QUESTIONS_DATA)
    return max(1, (total + count - 1) // count)


# ==============================================================================
# PREDEFINED ADVANCED GENDER & GRAMMAR CHAPTERS (PROGRESSION SYSTEM)
# ==============================================================================

GENDER_CHAPTERS = [
    {
        "id": "gender_cases",
        "title": "Nomen & Artikel in den 4 Kasus (Akkusativ, Dativ, Genitiv)",
        "desc": "Master German noun genders across all cases with fill-in-the-blank sentences (dem / den / der / die).",
        "badge": "Chapter 2"
    },
    {
        "id": "verbs_b1",
        "title": "Verben & Zeiten (Präsens, Präteritum, Partizip II)",
        "desc": "Conjugations, auxiliary verbs (haben/sein), and Partizip II forms up to Goethe B1.",
        "badge": "Chapter 3"
    },
    {
        "id": "n_deklination",
        "title": "N-Deklination (Schwache maskuline Nomen)",
        "desc": "Weak masculine nouns (der Student, der Kollege, der Nachbar) taking -(e)n endings.",
        "badge": "Chapter 4"
    },
    {
        "id": "adjektivdeklination",
        "title": "Adjektivdeklination (Definit, Indefinit & Nullartikel)",
        "desc": "Adjective declension rules with definite, indefinite, and zero articles.",
        "badge": "Chapter 5"
    }
]

GENDERS_IN_CASES_QUESTIONS = [
    {
        "id": 1001,
        "topic": "Nomen & Artikel in den 4 Kasus (Akkusativ, Dativ, Genitiv)",
        "sentence_de": "Ich helfe dir ____ (Tisch) umziehen.",
        "target_de": "dem",
        "options": ["dem", "den", "der", "die"],
        "correct_index": 0,
        "explanation": "Das Verb 'helfen' verlangt immer den Dativ. 'der Tisch' (maskulin) wird im Dativ zu 'dem Tisch'.",
        "case": "Dativ",
        "gender": "Maskulin",
        "meaning_en": "I help you move the table.",
        "meaning_te": "నేను నీకు టేబుల్ మార్చడంలో సహాయం చేస్తాను.",
        "meaning_kn": "ನಾನು ನಿನಗೆ ಮೇಜು ಸಾಗಿಸಲು ಸಹಾಯ ಮಾಡುತ್ತೇನೆ."
    },
    {
        "id": 1002,
        "topic": "Nomen & Artikel in den 4 Kasus (Akkusativ, Dativ, Genitiv)",
        "sentence_de": "Sie schenkt ____ (Kind) ein interessantes Buch.",
        "target_de": "dem",
        "options": ["dem", "den", "der", "das"],
        "correct_index": 0,
        "explanation": "'schenken' verlangt die Person im Dativ: 'das Kind' (neutral) wird im Dativ zu 'dem Kind'.",
        "case": "Dativ",
        "gender": "Neutral",
        "meaning_en": "She gives the child an interesting book.",
        "meaning_te": "ఆమె ఆ పిల్లాడికి ఆసక్తికరమైన పుస్తకాన్ని బహుమతిగా ఇస్తుంది.",
        "meaning_kn": "ಅವಳು ಆ ಮಗುವಿಗೆ ಆಸಕ್ತಿದಾಯಕ ಪುಸ್ತಕವನ್ನು ಉಡುಗೊರೆಯಾಗಿ ನೀಡುತ್ತಾಳೆ."
    },
    {
        "id": 1003,
        "topic": "Nomen & Artikel in den 4 Kasus (Akkusativ, Dativ, Genitiv)",
        "sentence_de": "Er hat gestern ____ (Schlüssel) im Büro vergessen.",
        "target_de": "den",
        "options": ["dem", "den", "der", "das"],
        "correct_index": 1,
        "explanation": "'vergessen' verlangt den Akkusativ: 'der Schlüssel' (maskulin) wird im Akkusativ zu 'den Schlüssel'.",
        "case": "Akkusativ",
        "gender": "Maskulin",
        "meaning_en": "He forgot the key in the office yesterday.",
        "meaning_te": "అతను నిన్న కార్యాలయంలో తాళం చెవి మరచిపోయాడు.",
        "meaning_kn": "ಅವನು ನಿನ್ನೆ ಕಚೇರಿಯಲ್ಲಿ ಕೀಲಿಯನ್ನು ಮರೆತಿದ್ದಾನೆ."
    },
    {
        "id": 1004,
        "topic": "Nomen & Artikel in den 4 Kasus (Akkusativ, Dativ, Genitiv)",
        "sentence_de": "Wir danken ____ (Lehrerin) für die hervorragende Erklärung.",
        "target_de": "der",
        "options": ["dem", "den", "der", "die"],
        "correct_index": 2,
        "explanation": "Das Verb 'danken' fordert Dativ: 'die Lehrerin' (feminin) wird im Dativ zu 'der Lehrerin'.",
        "case": "Dativ",
        "gender": "Feminin",
        "meaning_en": "We thank the teacher for the excellent explanation.",
        "meaning_te": "గొప్ప వివరణ ఇచ్చినందుకు మేము ఉపాధ్యాయురాలికి కృతజ్ఞతలు తెలుపుతున్నాము.",
        "meaning_kn": "ಉತ್ತಮ ವಿವರಣೆಗಾಗಿ ನಾವು ಶಿಕ್ಷಕಿಗೆ ಧನ್ಯವಾದ ಹೇಳುತ್ತೇವೆ."
    },
    {
        "id": 1005,
        "topic": "Nomen & Artikel in den 4 Kasus (Akkusativ, Dativ, Genitiv)",
        "sentence_de": "Wegen ____ (Regen) mussten wir die Reise absagen.",
        "target_de": "des",
        "options": ["dem", "den", "der", "des"],
        "correct_index": 3,
        "explanation": "Die Präposition 'wegen' verlangt den Genitiv: 'der Regen' (maskulin) wird zu 'des Regens'.",
        "case": "Genitiv",
        "gender": "Maskulin",
        "meaning_en": "Because of the rain, we had to cancel the trip.",
        "meaning_te": "వర్షం కారణంగా మేము ప్రయాణాన్ని రద్దు చేసుకోవాల్సి వచ్చింది.",
        "meaning_kn": "ಮಳೆಯ ಕಾರಣದಿಂದಾಗಿ ನಾವು ಪ್ರವಾಸವನ್ನು ರದ್ದುಗೊಳಿಸಬೇಕಾಯಿತು."
    },
    {
        "id": 1006,
        "topic": "Nomen & Artikel in den 4 Kasus (Akkusativ, Dativ, Genitiv)",
        "sentence_de": "Ich fahre jeden Morgen mit ____ (Bus) zur Arbeit.",
        "target_de": "dem",
        "options": ["dem", "den", "der", "das"],
        "correct_index": 0,
        "explanation": "'mit' ist eine feste Dativ-Präposition: 'der Bus' (maskulin) wird zu 'dem Bus'.",
        "case": "Dativ",
        "gender": "Maskulin",
        "meaning_en": "I go to work by bus every morning.",
        "meaning_te": "నేను ప్రతి ఉదయం బస్సులో పనికి వెళ్తాను.",
        "meaning_kn": "ನಾನು ಪ್ರತಿದಿನ ಬೆಳಿಗ್ಗೆ ಬಸ್‌ನಲ್ಲಿ ಕೆಲಸಕ್ಕೆ ಹೋಗುತ್ತೇನೆ."
    },
    {
        "id": 1007,
        "topic": "Nomen & Artikel in den 4 Kasus (Akkusativ, Dativ, Genitiv)",
        "sentence_de": "Hast du ____ (Brief) schon zur Post gebracht?",
        "target_de": "den",
        "options": ["dem", "den", "der", "das"],
        "correct_index": 1,
        "explanation": "'bringen' verlangt Akkusativ: 'der Brief' (maskulin) wird im Akkusativ zu 'den Brief'.",
        "case": "Akkusativ",
        "gender": "Maskulin",
        "meaning_en": "Have you already brought the letter to the post office?",
        "meaning_te": "నువ్వు ఉత్తరాన్ని పోస్టాఫీసుకు తీసుకెళ్లావా?",
        "meaning_kn": "ನೀವು ಪತ್ರವನ್ನು ಪೋಸ್ಟ್ ಆಫೀಸ್‌ಗೆ ಕೊಂಡೊಯ್ದಿದ್ದೀರಾ?"
    },
    {
        "id": 1008,
        "topic": "Nomen & Artikel in den 4 Kasus (Akkusativ, Dativ, Genitiv)",
        "sentence_de": "Das Hotel liegt direkt gegenüber ____ (Bahnhof).",
        "target_de": "dem",
        "options": ["dem", "den", "der", "das"],
        "correct_index": 0,
        "explanation": "'gegenüber' verlangt immer Dativ: 'der Bahnhof' (maskulin) wird zu 'dem Bahnhof'.",
        "case": "Dativ",
        "gender": "Maskulin",
        "meaning_en": "The hotel is located directly opposite the train station.",
        "meaning_te": "హోటల్ నేరుగా రైల్వే స్టేషన్ ఎదురుగా ఉంది.",
        "meaning_kn": "ಹೋಟೆಲ್ ನೇರವಾಗಿ ರೈಲ್ವೆ ನಿಲ್ದಾಣದ ಎದುರು ಇದೆ."
    },
    {
        "id": 1009,
        "topic": "Nomen & Artikel in den 4 Kasus (Akkusativ, Dativ, Genitiv)",
        "sentence_de": "Er gratuliert ____ (Freundin) herzlich zum Geburtstag.",
        "target_de": "der",
        "options": ["dem", "den", "der", "die"],
        "correct_index": 2,
        "explanation": "'gratulieren' verlangt den Dativ: 'die Freundin' (feminin) wird zu 'der Freundin'.",
        "case": "Dativ",
        "gender": "Feminin",
        "meaning_en": "He congratulates his girlfriend warmly on her birthday.",
        "meaning_te": "అతను తన స్నేహితురాలికి పుట్టినరోజు శుభాకాంక్షలు తెలుపుతున్నాడు.",
        "meaning_kn": "ಅವನು ತನ್ನ ಗೆಳತಿಗೆ ಹುಟ್ಟುಹಬ್ಬದ ಹಾರ್ದಿಕ ಶುಭಾಶಯಗಳನ್ನು ಕೋರುತ್ತಾನೆ."
    },
    {
        "id": 1010,
        "topic": "Nomen & Artikel in den 4 Kasus (Akkusativ, Dativ, Genitiv)",
        "sentence_de": "Er stellt die Blumenvase auf ____ (Tisch).",
        "target_de": "den",
        "options": ["dem", "den", "der", "das"],
        "correct_index": 1,
        "explanation": "Wechselpräposition 'auf' mit Richtung (Wohin? stellen): Akkusativ maskulin -> 'den Tisch'.",
        "case": "Akkusativ",
        "gender": "Maskulin",
        "meaning_en": "He places the flower vase onto the table.",
        "meaning_te": "అతను పూల కుండీని టేబుల్‌పై ఉంచుతున్నాడు.",
        "meaning_kn": "ಅವನು ಹೂದಾನಿಯನ್ನು ಮೇಜಿನ ಮೇಲೆ ಇಡುತ್ತಾನೆ."
    },
    {
        "id": 1011,
        "topic": "Nomen & Artikel in den 4 Kasus (Akkusativ, Dativ, Genitiv)",
        "sentence_de": "Das Buch liegt bereits auf ____ (Schreibtisch).",
        "target_de": "dem",
        "options": ["dem", "den", "der", "das"],
        "correct_index": 0,
        "explanation": "Wechselpräposition 'auf' mit Lage (Wo? liegen): Dativ maskulin -> 'dem Schreibtisch'.",
        "case": "Dativ",
        "gender": "Maskulin",
        "meaning_en": "The book is already lying on the desk.",
        "meaning_te": "పుస్తకం ఇప్పటికే డెస్క్‌పై ఉంది.",
        "meaning_kn": "ಪುಸ್ತಕವು ಈಗಾಗಲೇ ಡೆಸ್ಕ್ ಮೇಲೆ ಇದೆ."
    },
    {
        "id": 1012,
        "topic": "Nomen & Artikel in den 4 Kasus (Akkusativ, Dativ, Genitiv)",
        "sentence_de": "Sie hat ____ (Rechnung) sofort online überwiesen.",
        "target_de": "die",
        "options": ["dem", "den", "der", "die"],
        "correct_index": 3,
        "explanation": "'überweisen' verlangt Akkusativ: 'die Rechnung' (feminin) bleibt im Akkusativ 'die Rechnung'.",
        "case": "Akkusativ",
        "gender": "Feminin",
        "meaning_en": "She transferred the bill online immediately.",
        "meaning_te": "ఆమె వెంటనే బిల్లును ఆన్‌లైన్‌లో బదిలీ చేసింది.",
        "meaning_kn": "ಅವಳು ತಕ್ಷಣವೇ ಬಿಲ್ ಅನ್ನು ಆನ್‌ಲೈನ್‌ನಲ್ಲಿ ವರ್ಗಾಯಿಸಿದಳು."
    }
]

VERBS_B1_QUESTIONS = [
    {
        "id": 2001,
        "topic": "Verben & Zeiten (Präsens, Präteritum, Partizip II)",
        "sentence_de": "Gestern habe ich den ganzen Tag für die B1-Prüfung ____ (lernen).",
        "target_de": "gelernt",
        "options": ["gelernt", "gelernten", "lernten", "gelernen"],
        "correct_index": 0,
        "explanation": "Perfekt von 'lernen' mit Hilfsverb haben: regelmäßig -> 'gelernt'.",
        "case": "Perfekt",
        "meaning_en": "Yesterday I studied all day for the B1 exam.",
        "meaning_te": "నిన్న నేను B1 పరీక్ష కోసం రోజంతా చదువుకున్నాను.",
        "meaning_kn": "ನಿನ್ನೆ ನಾನು B1 ಪರೀಕ್ಷೆಗಾಗಿ ಇಡೀ ದಿನ ಓದಿದೆ."
    },
    {
        "id": 2002,
        "topic": "Verben & Zeiten (Präsens, Präteritum, Partizip II)",
        "sentence_de": "Der ICE aus Hamburg ist pünktlich am Gleis 4 ____ (ankommen).",
        "target_de": "angekommen",
        "options": ["angekommen", "angekommt", "ankamen", "ankommen"],
        "correct_index": 0,
        "explanation": "Perfekt von 'ankommen' mit Hilfsverb sein: starkes trennbares Verb -> 'angekommen'.",
        "case": "Perfekt (sein)",
        "meaning_en": "The ICE from Hamburg arrived on time at track 4.",
        "meaning_te": "హాంబర్గ్ నుండి వచ్చిన రైలు సరైన సమయానికి 4వ ప్లాట్‌ఫారమ్‌కు చేరుకుంది.",
        "meaning_kn": "ಹ್ಯಾಂಬರ್ಗ್‌ನಿಂದ ಬಂದ ರೈಲು ಸಮಯಕ್ಕೆ ಸರಿಯಾಗಿ 4ನೇ ಟ್ರ್ಯಾಕ್‌ಗೆ ತಲುಪಿತು."
    },
    {
        "id": 2003,
        "topic": "Verben & Zeiten (Präsens, Präteritum, Partizip II)",
        "sentence_de": "Als er jung war, ____ (spielen) er jeden Nachmittag Fußball im Park.",
        "target_de": "spielte",
        "options": ["spielte", "spielt", "gespielt", "spielten"],
        "correct_index": 0,
        "explanation": "Präteritum von 'spielen' für 3. Person Singular (er): 'spielte'.",
        "case": "Präteritum",
        "meaning_en": "When he was young, he played football in the park every afternoon.",
        "meaning_te": "అతను చిన్నగా ఉన్నప్పుడు ప్రతి మధ్యాహ్నం పార్కులో ఫుట్‌బాల్ ఆడేవాడు.",
        "meaning_kn": "ಅವನು ಚಿಕ್ಕವನಿದ್ದಾಗ ಪ್ರತಿದಿನ ಮಧ್ಯಾಹ್ನ ಉದ್ಯಾನದಲ್ಲಿ ಫುಟ್ಬಾಲ್ ಆಡುತ್ತಿದ್ದನು."
    },
    {
        "id": 2004,
        "topic": "Verben & Zeiten (Präsens, Präteritum, Partizip II)",
        "sentence_de": "Wir haben gestern eine offizielle Beschwerde ____ (schreiben).",
        "target_de": "geschrieben",
        "options": ["geschrieben", "geschriebt", "schrieben", "geschreiben"],
        "correct_index": 0,
        "explanation": "Perfekt von 'schreiben' mit Hilfsverb haben: unregelmäßiges Partizip II -> 'geschrieben'.",
        "case": "Perfekt",
        "meaning_en": "Yesterday we wrote an official complaint.",
        "meaning_te": "నిన్న మేము ఒక అధికారిక ఫిర్యాదు రాశాము.",
        "meaning_kn": "ನಿನ್ನೆ ನಾವು ಅಧಿಕೃತ ದೂರು ಬರೆದಿದ್ದೇವೆ."
    },
    {
        "id": 2005,
        "topic": "Verben & Zeiten (Präsens, Präteritum, Partizip II)",
        "sentence_de": "Mein Arzt hat mir viel Ruhe und frische Luft ____ (empfehlen).",
        "target_de": "empfohlen",
        "options": ["empfohlen", "empfiehlt", "empfahl", "geempfohlen"],
        "correct_index": 0,
        "explanation": "Untrennbares Verb 'empfehlen' (Vokalwechsel e -> o): Partizip II ohne ge- -> 'empfohlen'.",
        "case": "Perfekt",
        "meaning_en": "My doctor recommended plenty of rest and fresh air to me.",
        "meaning_te": "నా డాక్టర్ నాకు మంచి విశ్రాంతి మరియు స్వచ్ఛమైన గాలిని సిఫార్సు చేశారు.",
        "meaning_kn": "ನನ್ನ ವೈದ್ಯರು ನನಗೆ ಸಾಕಷ್ಟು ವಿಶ್ರಾಂತಿ ಮತ್ತು ಶುದ್ಧ ಗಾಳಿಯನ್ನು ಶಿಫಾರಸು ಮಾಡಿದರು."
    },
    {
        "id": 2006,
        "topic": "Verben & Zeiten (Präsens, Präteritum, Partizip II)",
        "sentence_de": "Wir freuen uns schon sehr ____ die bevorstehende Urlaubsreise.",
        "target_de": "auf",
        "options": ["auf", "über", "für", "an"],
        "correct_index": 0,
        "explanation": "'sich freuen auf' + Akkusativ drückt Vorfreude auf ein zukünftiges Ereignis aus.",
        "case": "Präpositionalverb",
        "meaning_en": "We are really looking forward to the upcoming holiday trip.",
        "meaning_te": "రాబోయే సెలవుల ప్రయాణం కోసం మేము ఎంతగానో ఎదురుచూస్తున్నాము.",
        "meaning_kn": "ಮುಂಬರುವ ರಜಾದಿನದ ಪ್ರವಾಸಕ್ಕಾಗಿ ನಾವು ಕಾತರದಿಂದ ಕಾಯುತ್ತಿದ್ದೇವೆ."
    }
]

N_DECLENSION_QUESTIONS = [
    {
        "id": 3001,
        "topic": "N-Deklination (Schwache maskuline Nomen)",
        "sentence_de": "Ich habe gestern ausführlich mit dem neuen ____ (Kollege) gesprochen.",
        "target_de": "Kollegen",
        "options": ["Kollegen", "Kollege", "Kolleges", "Kollegem"],
        "correct_index": 0,
        "explanation": "'der Kollege' ist ein schwaches maskulines Nomen (N-Deklination). Im Dativ: 'mit dem Kollegen'.",
        "case": "Dativ",
        "meaning_en": "I spoke in detail with the new colleague yesterday.",
        "meaning_te": "నేను నిన్న కొత్త సహోద్యోగితో వివరంగా మాట్లాడాను.",
        "meaning_kn": "ನಾನು ನಿನ್ನೆ ಹೊಸ ಸಹೋದ್ಯೋಗಿಯೊಂದಿಗೆ ವಿವರವಾಗಿ ಮಾತನಾಡಿದೆ."
    },
    {
        "id": 3002,
        "topic": "N-Deklination (Schwache maskuline Nomen)",
        "sentence_de": "Der Professor erklärt dem ausländischen ____ (Student) die Prüfungsregeln.",
        "target_de": "Studenten",
        "options": ["Studenten", "Student", "Students", "Studentem"],
        "correct_index": 0,
        "explanation": "'der Student' endet auf -ent und gehört zur N-Deklination: Dativ Singular -> 'dem Studenten'.",
        "case": "Dativ",
        "meaning_en": "The professor explains the exam rules to the international student.",
        "meaning_te": "ప్రొఫెసర్ విదేశీ విద్యార్థికి పరీక్ష నియమాలను వివరిస్తున్నారు.",
        "meaning_kn": "ಪ್ರಾಧ್ಯಾಪಕರು ವಿದೇಶಿ ವಿದ್ಯಾರ್ಥಿಗೆ ಪರೀಕ್ಷೆಯ ನಿಯಮಗಳನ್ನು ವಿವರಿಸುತ್ತಾರೆ."
    },
    {
        "id": 3003,
        "topic": "N-Deklination (Schwache maskuline Nomen)",
        "sentence_de": "Der Polizist befragt den freundlichen ____ (Herr) nach dem Unfall.",
        "target_de": "Herrn",
        "options": ["Herrn", "Herr", "Herre", "Herrem"],
        "correct_index": 0,
        "explanation": "'der Herr' erhält in allen Fällen außer Nominativ Singular die Endung -n: Akkusativ -> 'den Herrn'.",
        "case": "Akkusativ",
        "meaning_en": "The policeman questions the friendly gentleman after the accident.",
        "meaning_te": "పోలీసు అధికారి ప్రమాదం తర్వాత ఆ మర్యాదపూర్వక పెద్దమనిషిని ప్రశ్నిస్తున్నారు.",
        "meaning_kn": "ಪೊಲೀಸರು ಅಪಘಾತದ ನಂತರ ಆ ಸಭ್ಯ ವ್ಯಕ್ತಿಯನ್ನು ವಿಚಾರಿಸುತ್ತಾರೆ."
    },
    {
        "id": 3004,
        "topic": "N-Deklination (Schwache maskuline Nomen)",
        "sentence_de": "Der Arzt untersucht heute den verletzten ____ (Patient).",
        "target_de": "Patienten",
        "options": ["Patienten", "Patient", "Patients", "Patientem"],
        "correct_index": 0,
        "explanation": "'der Patient' gehört zur N-Deklination: Akkusativ Singular -> 'den Patienten'.",
        "case": "Akkusativ",
        "meaning_en": "The doctor is examining the injured patient today.",
        "meaning_te": "వైద్యుడు ఈ రోజు గాయపడిన రోగిని పరీక్షిస్తున్నాడు.",
        "meaning_kn": "ವೈದ್ಯರು ಇಂದು ಗಾಯಗೊಂಡ ರೋಗಿಯನ್ನು ಪರೀಕ್ಷಿಸುತ್ತಿದ್ದಾರೆ."
    }
]

ADJECTIVE_DECLENSION_QUESTIONS = [
    {
        "id": 4001,
        "topic": "Adjektivdeklination (Definit, Indefinit & Nullartikel)",
        "sentence_de": "Sie hat sich gestern ein ____ (neu) Auto gekauft.",
        "target_de": "neues",
        "options": ["neues", "neuem", "neuen", "neue"],
        "correct_index": 0,
        "explanation": "Unbestimmter Artikel 'ein' + Akkusativ neutral ('das Auto') -> Endung -es: 'ein neues Auto'.",
        "case": "Akkusativ (Neutral)",
        "meaning_en": "She bought herself a new car yesterday.",
        "meaning_te": "ఆమె నిన్న కొత్త కారు కొనుక్కుంది.",
        "meaning_kn": "ಅವಳು ನಿನ್ನೆ ತನಗಾಗಿ ಹೊಸ ಕಾರನ್ನು ಖರೀದಿಸಿದಳು."
    },
    {
        "id": 4002,
        "topic": "Adjektivdeklination (Definit, Indefinit & Nullartikel)",
        "sentence_de": "Ich habe mich gestern mit einem ____ (alt) Freund getroffen.",
        "target_de": "alten",
        "options": ["alten", "altem", "altes", "alter"],
        "correct_index": 0,
        "explanation": "'mit' + Dativ maskulin ('einem Freund'): Adjektiv nach unbestimmtem Artikel im Dativ endet immer auf -en -> 'einem alten Freund'.",
        "case": "Dativ (Maskulin)",
        "meaning_en": "Yesterday I met up with an old friend.",
        "meaning_te": "నిన్న నేను ఒక పాత స్నేహితుడిని కలిశాను.",
        "meaning_kn": "ನಿನ್ನೆ ನಾನು ಒಬ್ಬ ಹಳೆಯ ಸ್ನೇಹಿತನನ್ನು ಭೇಟಿಯಾದೆ."
    },
    {
        "id": 4003,
        "topic": "Adjektivdeklination (Definit, Indefinit & Nullartikel)",
        "sentence_de": "Die ____ (schön) Blumen stehen auf dem Esstisch.",
        "target_de": "schönen",
        "options": ["schönen", "schöne", "schöner", "schönem"],
        "correct_index": 0,
        "explanation": "Bestimmter Artikel 'die' im Plural: Adjektiv endet immer auf -en -> 'die schönen Blumen'.",
        "case": "Nominativ (Plural)",
        "meaning_en": "The beautiful flowers are on the dining table.",
        "meaning_te": "అందమైన పువ్వులు భోజనపు బల్లపై ఉన్నాయి.",
        "meaning_kn": "ಸುಂದರವಾದ ಹೂವುಗಳು ಊಟದ ಮೇಜಿನ ಮೇಲೆ ಇವೆ."
    },
    {
        "id": 4004,
        "topic": "Adjektivdeklination (Definit, Indefinit & Nullartikel)",
        "sentence_de": "Auf dem Wochenmarkt kaufe ich immer ____ (frisch) Obst.",
        "target_de": "frisches",
        "options": ["frisches", "frischem", "frischen", "frische"],
        "correct_index": 0,
        "explanation": "Nullartikel (ohne Artikel) + Akkusativ neutral ('das Obst') -> Adjektiv übernimmt die Signalendung -es: 'frisches Obst'.",
        "case": "Akkusativ (Nullartikel)",
        "meaning_en": "At the weekly market, I always buy fresh fruit.",
        "meaning_te": "వారాంతపు మార్కెట్‌లో నేను ఎల్లప్పుడూ తాజా పండ్లను కొంటాను.",
        "meaning_kn": "ವಾರದ ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ನಾನು ಯಾವಾಗಲೂ ತಾಜಾ ಹಣ್ಣುಗಳನ್ನು ಖರೀದಿಸುತ್ತೇನೆ."
    }
]


def get_predefined_gender_questions(topic: str) -> List[Dict[str, Any]]:
    """Returns curated question sets for advanced Gender Duel chapters."""
    t_clean = topic.strip().lower()
    if "kasus" in t_clean or "case" in t_clean:
        return GENDERS_IN_CASES_QUESTIONS
    elif "verb" in t_clean:
        return VERBS_B1_QUESTIONS
    elif "n-deklination" in t_clean or "weak masculine" in t_clean:
        return N_DECLENSION_QUESTIONS
    elif "adjektiv" in t_clean or "adjective" in t_clean:
        return ADJECTIVE_DECLENSION_QUESTIONS
    return []
