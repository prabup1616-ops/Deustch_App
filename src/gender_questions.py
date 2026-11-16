"""
Goethe B1 German Gender / Artikel Questions Bank Loader.
Loads verified Goethe B1 Wortliste nouns with articles (der/die/das),
plural forms, English meanings, Telugu meanings, and Kannada meanings.
"""

import json
import os
import hashlib
from typing import List, Dict, Any

JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "gender_questions_bank.json")


def load_all_gender_questions() -> List[Dict[str, Any]]:
    if not os.path.exists(JSON_PATH):
        # Fallback to generating if missing
        import generate_gender_questions
        generate_gender_questions.build_gender_questions()
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


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
