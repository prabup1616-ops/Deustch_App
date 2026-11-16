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

try:
    from src.db import (
        is_db_connected,
        init_db,
        db_save_player,
        db_get_players,
        db_save_attempt,
        db_get_attempts,
        db_add_learned_topic,
        db_get_learned_topics
    )
    if is_db_connected():
        init_db()
except Exception:
    def is_db_connected():
        return False

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
    if is_db_connected():
        try:
            db_save_player(matched_id, clean_name, avatar, email)
        except Exception:
            pass
    return data["players"][matched_id]


def create_unique_player(name: str, avatar: str = "🦁", email: str = "") -> Dict[str, Any]:
    """
    Creates a brand new player profile even if the base name already exists,
    assigning a unique identifier and display tag (e.g. 'Prabu #2', 'prabu_2').
    """
    clean_name = name.strip()
    if not clean_name:
        clean_name = "Player"

    data = load_data()
    if "players" not in data:
        data["players"] = {}

    base_id = clean_name.lower().replace(" ", "_")
    new_id = base_id
    new_display = clean_name
    counter = 2

    existing_pids = set(data["players"].keys())
    existing_names = {p.get("name", "").strip().lower() for p in data["players"].values()}

    if new_id in existing_pids or clean_name.lower() in existing_names:
        while f"{base_id}_{counter}" in existing_pids:
            counter += 1
        new_id = f"{base_id}_{counter}"
        new_display = f"{clean_name} #{counter}"

    new_profile = {
        "id": new_id,
        "name": new_display,
        "avatar": avatar,
        "email": email.strip()
    }
    data["players"][new_id] = new_profile
    save_data(data)

    if is_db_connected():
        try:
            db_save_player(new_id, new_display, avatar, email)
        except Exception:
            pass

    return new_profile


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

    if is_db_connected():
        try:
            db_save_attempt(clean_pid, category, score, total, "", date_str)
        except Exception:
            pass

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


def get_all_time_stats(category: str = "pronoun", include_all_players: bool = True) -> List[Dict[str, Any]]:
    """
    Computes all-time summary for each player for the specified category:
    - Best single score (High Score)
    - Total points earned
    - Overall average
    - Total attempts & days active
    - If include_all_players=True, includes all registered players even if 0 attempts.
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
        if count == 0 and not include_all_players:
            continue
        scores = [a.get("score", 0) for a in p_attempts]
        total_pts = sum(scores)
        overall_avg = round(total_pts / count, 2) if count > 0 else 0.0
        best_score = max(scores) if scores else 0
        unique_days = len(set(a.get("date") for a in p_attempts))

        summary.append({
            "player_id": pid,
            "name": pinfo["name"],
            "avatar": pinfo.get("avatar", "👤"),
            "total_attempts": count,
            "total_points": total_pts,
            "best_score": best_score,
            "overall_average": overall_avg,
            "days_active": unique_days
        })
    summary.sort(key=lambda x: (x["best_score"], x["overall_average"], x["total_points"]), reverse=True)
    return summary


def get_player_continuous_history(player_id: str, category: str = "pronoun") -> Dict[str, Any]:
    """
    Computes a player's continuous daily journey across all their sessions:
    - Automatically segments attempts into chronological distinct days (Day 1, Day 2, Day 3...)
    - Tracks whether today has already been played
    - Computes current day number for the player
    - Calculates daily averages, score logs, and improvement trends
    """
    from collections import OrderedDict
    from datetime import date

    data = load_data()
    clean_pid = str(player_id).strip().lower().replace(" ", "_")
    p_attempts = [
        a for a in data.get("attempts", [])
        if str(a.get("player_id", "")).strip().lower().replace(" ", "_") == clean_pid
        and a.get("category", "pronoun") == category
    ]

    p_attempts.sort(key=lambda a: a.get("timestamp", ""))

    days_map = OrderedDict()
    for a in p_attempts:
        d = a.get("date", "")
        cal_date = a.get("timestamp", "")[:10] or d
        key = cal_date if cal_date and not d.startswith("pack-") else d
        if not key:
            key = "day-1"
        if key not in days_map:
            days_map[key] = []
        days_map[key].append(a)

    today_iso = date.today().isoformat()
    history = []
    prev_avg = None

    for idx, (day_key, att_list) in enumerate(days_map.items(), start=1):
        scores = [a.get("score", 0) for a in att_list]
        avg = round(sum(scores) / len(scores), 2)
        best = max(scores)
        pct = round((avg / 5.0) * 100, 1)

        if prev_avg is None:
            trend = "🚀 Initial Baseline"
            trend_delta = 0.0
        else:
            diff = round(avg - prev_avg, 2)
            trend_delta = diff
            if diff > 0:
                trend = f"📈 +{diff:.2f} (+{round(diff/5.0*100, 1)}%) Improving!"
            elif diff < 0:
                trend = f"📉 {diff:.2f} Needs Review"
            else:
                trend = "🎯 Steady Performance"
        prev_avg = avg

        is_today = (day_key == today_iso)
        history.append({
            "day_number": idx,
            "date": day_key,
            "label": f"Day {idx} ({day_key})",
            "attempts_count": len(scores),
            "scores": scores,
            "average_score": avg,
            "best_score": best,
            "pct": pct,
            "trend": trend,
            "trend_delta": trend_delta,
            "is_today": is_today
        })

    is_played_today = any(h["is_today"] for h in history)
    if is_played_today:
        today_record = next(h for h in history if h["is_today"])
        current_day_number = today_record["day_number"]
        today_stats = today_record
    else:
        current_day_number = len(history) + 1
        today_stats = None

    all_scores = [a.get("score", 0) for a in p_attempts]
    overall_avg = round(sum(all_scores) / len(all_scores), 2) if all_scores else 0.0
    overall_pct = round((overall_avg / 5.0) * 100, 1) if all_scores else 0.0

    if len(history) >= 2:
        first_avg = history[0]["average_score"]
        last_avg = history[-1]["average_score"]
        total_diff = round(last_avg - first_avg, 2)
        if total_diff > 0:
            improvement_summary = f"📈 Excellent! Overall score improved by +{total_diff:.2f} marks (+{round(total_diff/5.0*100, 1)}%) since Day 1!"
        elif total_diff == 0:
            improvement_summary = f"🎯 Solid consistency! Maintaining {overall_avg:.2f}/5.0 average across {len(history)} days."
        else:
            improvement_summary = f"💪 Practicing consistently. Keep retaking to boost your score to the next tier!"
    elif len(history) == 1:
        improvement_summary = f"🌟 Great start! Completed Day 1 with an average of {history[0]['average_score']:.2f}/5.0. Come back tomorrow for Day 2!"
    else:
        improvement_summary = "👋 Welcome! Start Day 1 today to begin your continuous Goethe B1 journey!"

    return {
        "player_id": clean_pid,
        "history": history,
        "current_day_number": current_day_number,
        "is_played_today": is_played_today,
        "today_stats": today_stats,
        "total_days_completed": len(history),
        "total_attempts": len(p_attempts),
        "overall_average": overall_avg,
        "overall_pct": overall_pct,
        "improvement_summary": improvement_summary
    }


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

    if is_db_connected():
        try:
            db_add_learned_topic(clean_pid, clean_topic)
        except Exception:
            pass


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

    if is_db_connected():
        try:
            db_save_attempt(clean_pid, f"lsrw_{module}", score, total, ", ".join(topics_tested), date.today().isoformat())
        except Exception:
            pass


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
