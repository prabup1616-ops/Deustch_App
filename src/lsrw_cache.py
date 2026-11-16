"""
LSRW Exercise Cache and Seed Bank Manager.
Provides instant 0.1-second loading for repeated or pre-generated topics.
Supports both Cloud PostgreSQL (Supabase / Neon) and local lsrw_cache.json fallback.
"""

import json
import os
import hashlib
import random
from typing import Dict, Any, Optional, List
from src.config import BASE_DIR
from src.db import (
    is_db_connected,
    db_save_exercise_to_bank,
    db_get_bank_exercises,
    db_count_bank_exercises
)

CACHE_FILE = os.path.join(BASE_DIR, "lsrw_cache.json")


def _get_cache_key(module: str, topics: List[str], extra: str = "") -> str:
    """Computes a normalized cache key from sorted topic names."""
    clean_topics = sorted([t.strip().lower() for t in topics if t.strip()])
    key_str = f"{module.lower()}::" + ",".join(clean_topics)
    if extra:
        key_str += f"::{extra.lower()}"
    return hashlib.md5(key_str.encode("utf-8")).hexdigest()


def load_cache() -> Dict[str, Any]:
    """Loads all cached LSRW exercises from disk."""
    if not os.path.exists(CACHE_FILE):
        initial = {
            "reading": {},
            "writing": {},
            "listening_easy": {},
            "listening_real": {},
            "speaking": {},
            "explanation": {}
        }
        save_cache(initial)
        return initial

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            for mod in ("reading", "writing", "listening_easy", "listening_real", "speaking", "explanation"):
                if mod not in data or not isinstance(data[mod], dict):
                    data[mod] = {}
            return data
    except Exception:
        return {
            "reading": {},
            "writing": {},
            "listening_easy": {},
            "listening_real": {},
            "speaking": {},
            "explanation": {}
        }


def save_cache(data: Dict[str, Any]) -> None:
    """Saves LSRW exercises cache to disk."""
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def get_cached_exercise(module: str, topics: List[str], extra: str = "") -> Optional[Dict[str, Any]]:
    """
    Retrieves a cached exercise in 0.001 seconds if available.
    Checks PostgreSQL first if online, falls back to local seed bank.
    """
    topic_str = ", ".join(sorted([t.strip() for t in topics if t.strip()]))
    if is_db_connected():
        bank = db_get_bank_exercises(module, topic_str)
        if bank:
            return bank[0]

    cache = load_cache()
    mod_store = cache.get(module, {})
    key = _get_cache_key(module, topics, extra)
    cached_list = mod_store.get(key, [])
    if cached_list and isinstance(cached_list, list) and len(cached_list) > 0:
        return cached_list[-1]
    return None


def store_cached_exercise(module: str, topics: List[str], exercise_data: Dict[str, Any], extra: str = "") -> None:
    """Stores a freshly generated exercise in both PostgreSQL DB bank and local cache."""
    if not exercise_data:
        return

    topic_str = ", ".join(sorted([t.strip() for t in topics if t.strip()]))
    if is_db_connected():
        try:
            db_save_exercise_to_bank(module, topic_str, exercise_data)
        except Exception:
            pass

    cache = load_cache()
    if module not in cache:
        cache[module] = {}

    key = _get_cache_key(module, topics, extra)
    if key not in cache[module]:
        cache[module][key] = []

    existing = cache[module][key]
    existing.append(exercise_data)
    if len(existing) > 5:
        existing.pop(0)

    save_cache(cache)


def get_bank_count(module: str, topics: List[str]) -> int:
    """Returns number of exercises stored in DB bank or local cache for this topic."""
    topic_str = ", ".join(sorted([t.strip() for t in topics if t.strip()]))
    if is_db_connected():
        ct = db_count_bank_exercises(module, topic_str)
        if ct > 0:
            return ct

    cache = load_cache()
    key = _get_cache_key(module, topics)
    return len(cache.get(module, {}).get(key, []))


def get_bank_previous_exercise(module: str, topics: List[str]) -> Optional[Dict[str, Any]]:
    """Returns a previous exercise from DB bank or local cache for instant replay (0 AI tokens)."""
    topic_str = ", ".join(sorted([t.strip() for t in topics if t.strip()]))
    if is_db_connected():
        exercises = db_get_bank_exercises(module, topic_str)
        if exercises:
            return random.choice(exercises)

    cache = load_cache()
    mod_store = cache.get(module, {})
    key = _get_cache_key(module, topics)
    cached_list = mod_store.get(key, [])
    if cached_list:
        return random.choice(cached_list)
    return None
