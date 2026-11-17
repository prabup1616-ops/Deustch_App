"""
FastAPI Router for Daily Duel & Gamification.
Exposes leaderboard endpoints and community topic repositories.
"""

from fastapi import APIRouter
from typing import List, Dict, Any
import storage

router = APIRouter(prefix="/api/v1/duel", tags=["Daily Duel & Leaderboard"])


@router.get("/leaderboard", summary="Get global duel leaderboard")
async def get_leaderboard():
    """
    Retrieves all-time leaderboard rankings and streaks.
    """
    all_time = storage.get_all_time_stats()
    results = []
    for rank, p in enumerate(all_time, start=1):
        results.append({
            "rank": rank,
            "player_id": p.get("player_id", ""),
            "name": p.get("name", ""),
            "score": p.get("total_score", 0),
            "streak": p.get("streak", 0),
            "accuracy": p.get("avg_score", 0.0)
        })
    return results


@router.get("/topics", summary="Get community unlocked topics")
async def get_community_topics():
    """
    Returns grammar topics unlocked by the community.
    """
    topics = storage.get_community_topics()
    return {"topics": topics}
