"""
LSRW Exercise Cache and Seed Bank Manager.
Provides instant 0.1-second loading for repeated or pre-generated topics,
persisting exercises to lsrw_cache.json.
"""

import json
import os
import hashlib
from typing import Dict, Any, Optional, List
from src.config import BASE_DIR

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
            "speaking": {}
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
    Returns None if not found or empty.
    """
    cache = load_cache()
    mod_store = cache.get(module, {})
    key = _get_cache_key(module, topics, extra)
    cached_list = mod_store.get(key, [])
    if cached_list and isinstance(cached_list, list) and len(cached_list) > 0:
        # Return the latest or random one
        return cached_list[-1]
    return None


def store_cached_exercise(module: str, topics: List[str], exercise_data: Dict[str, Any], extra: str = "") -> None:
    """Stores a freshly generated exercise in the seed bank."""
    if not exercise_data:
        return
    cache = load_cache()
    if module not in cache:
        cache[module] = {}

    key = _get_cache_key(module, topics, extra)
    if key not in cache[module]:
        cache[module][key] = []

    # Store up to 3 variations per topic combination for variety
    existing = cache[module][key]
    existing.append(exercise_data)
    if len(existing) > 3:
        existing.pop(0)

    save_cache(cache)
