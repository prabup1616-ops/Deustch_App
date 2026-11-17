"""
Goethe B1 German Questions Bank Loader
Loads the complete database of 162 verified questions covering
Possessivartikel across Nominativ, Akkusativ, Dativ, and Genitiv
with Goethe B1 Wortliste vocabulary and authentic Telugu & Kannada sentences.
"""

import json
import os
import hashlib
from typing import List, Dict, Any

from src.config import QUESTIONS_FILE as JSON_PATH

def load_all_questions() -> List[Dict[str, Any]]:
    if not os.path.exists(JSON_PATH):
        try:
            from scripts import generate_questions
            q = generate_questions.generate_162_questions()
            with open(JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(q, f, ensure_ascii=False, indent=2)
            return q
        except Exception:
            pass
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

QUESTIONS_DATA = load_all_questions()

def get_daily_questions(date_str: str, count: int = 5) -> List[Dict[str, Any]]:
    """
    Returns a deterministic set of 5 questions for a specific calendar date (YYYY-MM-DD),
    so that all players get the exact same questions on that day.
    """
    total = len(QUESTIONS_DATA)
    # Generate seed from date string
    h = int(hashlib.md5(date_str.encode("utf-8")).hexdigest(), 16)
    indices = []
    for i in range(count):
        idx = (h + i * 13) % total
        while idx in indices:
            idx = (idx + 1) % total
        indices.append(idx)
    return [QUESTIONS_DATA[idx] for idx in indices]

def get_day_pack_questions(day_number: int, count: int = 5) -> List[Dict[str, Any]]:
    """
    Returns 5 consecutive questions for a specific day pack (Day 1 to 33),
    allowing players to practice specific day packs.
    """
    total = len(QUESTIONS_DATA)
    start_idx = ((day_number - 1) * count) % total
    selected = []
    for i in range(count):
        selected.append(QUESTIONS_DATA[(start_idx + i) % total])
    return selected
