"""
Storage manager for German B1 Daily Duel.
Supports dynamic player names (written by players, not predefined).
Handles daily attempts, score normalization / averaging across multiple attempts,
all-time leaderboards, email notification settings, and cumulative LSRW topic tracking.
"""

import json
import os
from datetime import datetime, date
from typing import Dict, Any, List

DATA_FILE = os.path.join(os.path.dirname(__file__), "duel_data.json")

DEFAULT_SETTINGS = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_user": "",
    "smtp_pass": "",
    "email_notifications_enabled": False,
    "gemini_api_key": ""
}


def load_data() -> Dict[str, Any]:
    if not os.path.exists(DATA_FILE):
        initial_data = {
            "players": {},
            "settings": DEFAULT_SETTINGS,
            "attempts": []
        }
        save_data(initial_data)
        return initial_data
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "players" not in data or not isinstance(data["players"], dict):
                data["players"] = {}
            if "settings" not in data:
                data["settings"] = DEFAULT_SETTINGS
            if "attempts" not in data:
                data["attempts"] = []
            return data
    except Exception:
        return {
            "players": {},
            "settings": DEFAULT_SETTINGS,
            "attempts": []
        }


def save_data(data: Dict[str, Any]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_or_create_player(name: str, avatar: str = "🦁", email: str = "") -> Dict[str, Any]:
    """
    Registers or fetches a player profile case-insensitively by name.
    """
    clean_name = name.strip()
    if not clean_name:
        clean_name = "Player"

    player_id = clean_name.lower().replace(" ", "_")

    data = load_data()
    if "players" not in data:
        data["players"] = {}

    # Case-insensitive lookup among existing registered players
    matched_id = None
    for pid, p in data["players"].items():
        if pid.lower() == player_id or p.get("name", "").strip().lower() == clean_name.lower():
            matched_id = pid
            break

    if matched_id is None:
        data["players"][player_id] = {
            "id": player_id,
            "name": clean_name,
            "avatar": avatar,
            "email": email.strip()
        }
        matched_id = player_id
    else:
        # Update avatar or email if provided
        if avatar:
            data["players"][matched_id]["avatar"] = avatar
        if email:
            data["players"][matched_id]["email"] = email.strip()

    save_data(data)
    return data["players"][matched_id]


def get_all_saved_players() -> List[Dict[str, Any]]:
    """
    Returns all registered player profiles from storage, sorted alphabetically by name.
    """
    data = load_data()
    players = list(data.get("players", {}).values())
    players.sort(key=lambda p: p.get("name", "").lower())
    return players


def update_settings(smtp_server: str, smtp_port: int, smtp_user: str, smtp_pass: str, enabled: bool) -> None:
    data = load_data()
    data["settings"] = {
        "smtp_server": smtp_server.strip(),
        "smtp_port": int(smtp_port),
        "smtp_user": smtp_user.strip(),
        "smtp_pass": smtp_pass.strip(),
        "email_notifications_enabled": bool(enabled)
    }
    save_data(data)


def record_attempt(player_id: str, date_str: str, score: int, total: int = 5, details: List[Dict[str, Any]] = None, category: str = "pronoun") -> Dict[str, Any]:
    """
    Records an individual attempt for a player on a given date/pack.
    Category distinguishes between 'pronoun' (Possessivartikel) and 'gender' (Artikel: der/die/das).
    Uses case-insensitive player_id.
    """
    data = load_data()
    clean_pid = str(player_id).strip().lower().replace(" ", "_")
    record = {
        "player_id": clean_pid,
        "date": date_str,
        "score": score,
        "total": total,
        "timestamp": datetime.now().isoformat(),
        "details": details or [],
        "category": category
    }
    data["attempts"].append(record)
    save_data(data)

    return get_player_daily_stats(clean_pid, date_str, data, category=category)


def get_player_daily_stats(player_id: str, date_str: str, data: Dict[str, Any] = None, category: str = "pronoun") -> Dict[str, Any]:
    if data is None:
        data = load_data()
    clean_pid = str(player_id).strip().lower().replace(" ", "_")
    player_attempts = [
        a for a in data.get("attempts", [])
        if str(a.get("player_id", "")).strip().lower().replace(" ", "_") == clean_pid
        and a.get("date") == date_str
        and a.get("category", "pronoun") == category
    ]
    if not player_attempts:
        return {
            "attempts_count": 0,
            "total_score": 0,
            "average_score": 0.0,
            "best_score": 0,
            "scores": []
        }
    scores = [a.get("score", 0) for a in player_attempts]
    count = len(scores)
    tot = sum(scores)
    avg = round(tot / count, 2)
    best = max(scores)
    return {
        "attempts_count": count,
        "total_score": tot,
        "average_score": avg,
        "best_score": best,
        "scores": scores
    }


def get_daily_leaderboard(date_str: str, category: str = "pronoun") -> List[Dict[str, Any]]:
    """
    Ranks all players who have played on the given date/pack in the specified category based on:
    1. Average Normalized Score (higher is better)
    2. Best Score (tiebreaker)
    3. Fewest attempts
    """
    data = load_data()
    players = data.get("players", {})
    leaderboard = []

    for pid, pinfo in players.items():
        stats = get_player_daily_stats(pid, date_str, data, category=category)
        if stats["attempts_count"] > 0:
            leaderboard.append({
                "player_id": pid,
                "name": pinfo["name"],
                "avatar": pinfo.get("avatar", "👤"),
                "email": pinfo.get("email", ""),
                "attempts_count": stats["attempts_count"],
                "average_score": stats["average_score"],
                "best_score": stats["best_score"],
                "total_score": stats["total_score"],
                "scores": stats["scores"],
                "has_played": True
            })

    # Sort: highest average_score, then highest best_score, then lowest attempts
    leaderboard.sort(
        key=lambda x: (x["average_score"], x["best_score"], -x["attempts_count"]),
        reverse=True
    )
    return leaderboard


def get_all_time_stats(category: str = "pronoun") -> List[Dict[str, Any]]:
    """
    Computes all-time summary for each player for the specified category:
    - Total attempts
    - Total points earned
    - Overall average
    - Days active
    """
    data = load_data()
    players = data.get("players", {})
    attempts = data.get("attempts", [])

    summary = []
    for pid, pinfo in players.items():
        p_attempts = [
            a for a in attempts
            if str(a.get("player_id", "")).strip().lower().replace(" ", "_") == pid.lower()
            and a.get("category", "pronoun") == category
        ]
        count = len(p_attempts)
        if count == 0:
            continue
        scores = [a.get("score", 0) for a in p_attempts]
        total_pts = sum(scores)
        overall_avg = round(total_pts / count, 2) if count > 0 else 0.0
        unique_days = len(set(a.get("date") for a in p_attempts))

        summary.append({
            "player_id": pid,
            "name": pinfo["name"],
            "avatar": pinfo.get("avatar", "👤"),
            "total_attempts": count,
            "total_points": total_pts,
            "overall_average": overall_avg,
            "days_active": unique_days
        })
    summary.sort(key=lambda x: (x["total_points"], x["overall_average"]), reverse=True)
    return summary


def get_shared_creator_key() -> str:
    """Returns stored Gemini API key from Streamlit secrets, environment, or settings."""
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    env_key = os.environ.get("GEMINI_API_KEY", "")
    if env_key:
        return env_key
    data = load_data()
    return data.get("settings", {}).get("gemini_api_key", "")


def get_gemini_api_key() -> str:
    """
    Returns active Gemini API key based on visitor selection:
    1. Visitor's custom user-supplied key in session state.
    2. Shared creator key IF the user opted into Shared/Demo Mode.
    3. Empty string if not configured yet.
    """
    try:
        import streamlit as st
        custom = st.session_state.get("user_gemini_api_key", "").strip()
        if custom:
            return custom
        if st.session_state.get("use_shared_creator_key", False):
            return get_shared_creator_key()
    except Exception:
        pass
    return ""


def is_using_shared_key() -> bool:
    """Checks if current session is using the shared creator fallback key."""
    try:
        import streamlit as st
        custom = st.session_state.get("user_gemini_api_key", "").strip()
        return not bool(custom) and bool(st.session_state.get("use_shared_creator_key", False))
    except Exception:
        return False


def save_gemini_api_key(key: str) -> None:
    """Saves Gemini API key to persistent settings."""
    data = load_data()
    if "settings" not in data:
        data["settings"] = DEFAULT_SETTINGS.copy()
    data["settings"]["gemini_api_key"] = key.strip()
    save_data(data)


def get_lsrw_data(player_id: str) -> Dict[str, Any]:
    """Retrieves saved LSRW conversation state and topic tracking for a player."""
    clean_pid = str(player_id).strip().lower().replace(" ", "_")
    data = load_data()
    lsrw_store = data.get("lsrw_store", {})
    return lsrw_store.get(clean_pid, {
        "practiced_list": [],
        "explained_list": [],
        "has_seen_kasus": False,
        "chat_history": []
    })


def save_lsrw_data(player_id: str, state: Dict[str, Any]) -> None:
    """Persists LSRW conversation state and topic tracking for a player."""
    clean_pid = str(player_id).strip().lower().replace(" ", "_")
    data = load_data()
    if "lsrw_store" not in data:
        data["lsrw_store"] = {}
    data["lsrw_store"][clean_pid] = state
    save_data(data)


# ==============================================================================
# CUMULATIVE LSRW TOPIC TRACKING
# ==============================================================================

def get_learned_topics(player_id: str) -> List[Dict[str, str]]:
    """
    Returns cumulative list of learned grammar topics for a player.
    Each entry: {"topic": "Preposition", "date": "2026-11-15"}
    Topics accumulate over time. Incorporates current_topic, practiced_list,
    and explained_list from chat or manual additions.
    """
    clean_pid = str(player_id).strip().lower().replace(" ", "_")
    data = load_data()
    lsrw_store = data.get("lsrw_store", {})
    player_data = lsrw_store.get(clean_pid, {})
    learned = list(player_data.get("learned_topics", []))
    existing_lower = [t["topic"].strip().lower() for t in learned]

    # Incorporate current_topic, practiced_list, explained_list if not already present
    curr = player_data.get("current_topic")
    if curr and curr.strip().lower() not in existing_lower:
        learned.append({"topic": curr.strip(), "date": date.today().isoformat()})
        existing_lower.append(curr.strip().lower())

    for item in player_data.get("practiced_list", []):
        if item.strip().lower() not in existing_lower:
            learned.append({"topic": item.strip(), "date": date.today().isoformat()})
            existing_lower.append(item.strip().lower())

    for item in player_data.get("explained_list", []):
        if item.strip().lower() not in existing_lower:
            learned.append({"topic": item.strip(), "date": date.today().isoformat()})
            existing_lower.append(item.strip().lower())

    # Fallback to guest topics if current user has no topics yet
    if not learned and clean_pid != "guest":
        guest_topics = lsrw_store.get("guest", {}).get("learned_topics", [])
        for gt in guest_topics:
            if gt.get("topic", "").strip().lower() not in existing_lower:
                learned.append(gt)
                existing_lower.append(gt.get("topic", "").strip().lower())

    # Default fallback: at least have Perfekt vs Präteritum
    if not learned:
        learned = [
            {"topic": "Perfekt vs Präteritum", "date": date.today().isoformat()}
        ]

    return learned


def add_learned_topic(player_id: str, topic: str) -> None:
    """Adds a grammar topic to the player's cumulative learned list (no duplicates)."""
    clean_pid = str(player_id).strip().lower().replace(" ", "_")
    clean_topic = topic.strip()
    if not clean_topic:
        return

    data = load_data()
    lsrw_store = data.setdefault("lsrw_store", {})
    player_data = lsrw_store.setdefault(clean_pid, {})
    learned = player_data.setdefault("learned_topics", [])

    # Check for duplicate (case-insensitive)
    existing_lower = [t["topic"].lower() for t in learned]
    if clean_topic.lower() not in existing_lower:
        learned.append({"topic": clean_topic, "date": date.today().isoformat()})
        save_data(data)


def remove_learned_topic(player_id: str, topic: str) -> None:
    """Removes a grammar topic from the player's learned list."""
    clean_pid = str(player_id).strip().lower().replace(" ", "_")
    data = load_data()
    lsrw_store = data.get("lsrw_store", {})
    player_data = lsrw_store.get(clean_pid, {})
    learned = player_data.get("learned_topics", [])
    player_data["learned_topics"] = [t for t in learned if t["topic"].lower() != topic.strip().lower()]
    save_data(data)


def save_lsrw_module_score(player_id: str, module: str, score: int, total: int, topics_tested: List[str]) -> None:
    """
    Saves a score for a specific LSRW module attempt.
    Module: 'reading', 'writing', 'listening', 'speaking'
    """
    clean_pid = str(player_id).strip().lower().replace(" ", "_")
    data = load_data()
    lsrw_store = data.setdefault("lsrw_store", {})
    player_data = lsrw_store.setdefault(clean_pid, {})
    scores = player_data.setdefault("module_scores", [])
    scores.append({
        "module": module,
        "score": score,
        "total": total,
        "topics": topics_tested,
        "date": date.today().isoformat(),
        "timestamp": datetime.now().isoformat()
    })
    save_data(data)


def get_lsrw_module_history(player_id: str, module: str = None) -> List[Dict[str, Any]]:
    """
    Returns score history for LSRW modules. If module is None, returns all.
    """
    clean_pid = str(player_id).strip().lower().replace(" ", "_")
    data = load_data()
    lsrw_store = data.get("lsrw_store", {})
    player_data = lsrw_store.get(clean_pid, {})
    scores = player_data.get("module_scores", [])
    if module:
        return [s for s in scores if s.get("module") == module]
    return scores
