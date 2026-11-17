"""
FastAPI Router for Learning Analytics & Machine Learning Models.
Exposes CEFR B1 Readiness Prediction, Ebbinghaus Forgetting Curves, and Topic Aggregations.
"""

from fastapi import APIRouter
from src.services.analytics_service import (
    predict_goethe_b1_readiness,
    calculate_ebbinghaus_spaced_repetition,
    analyze_weak_grammar_topics
)
from src.api.schemas import (
    B1ReadinessResponse,
    SpacedRepetitionResponse,
    WeakTopicsResponse
)

router = APIRouter(prefix="/api/v1/analytics", tags=["Machine Learning & Analytics"])


@router.get("/readiness/{player_id}", response_model=B1ReadinessResponse, summary="ML CEFR B1 Exam Readiness Index")
async def get_readiness_prediction(player_id: str):
    """
    Computes a weighted regression model over the learner's 4 LSRW modules
    to output the projected probability of passing the Goethe-Zertifikat B1 exam.
    """
    res = predict_goethe_b1_readiness(player_id)
    return B1ReadinessResponse(
        player_id=player_id,
        readiness_percentage=res["readiness_percentage"],
        verdict=res["verdict"],
        recommendation=res["recommendation"],
        module_breakdown=res["module_breakdown"],
        modules_at_pass_threshold=res["modules_at_pass_threshold"],
        total_practice_sessions=res["total_practice_sessions"]
    )


@router.get("/forgetting-curve/{player_id}", response_model=SpacedRepetitionResponse, summary="Ebbinghaus Spaced Repetition Forecast")
async def get_forgetting_curve(player_id: str):
    """
    Vectorized NumPy implementation of the Ebbinghaus memory decay equation R = e^(-t/S).
    Returns prioritized topics sorted by lowest recall probability.
    """
    items = calculate_ebbinghaus_spaced_repetition(player_id)
    urgent = sum(1 for itm in items if "Urgent" in itm["status"] or "Immediate" in itm["status"])
    return SpacedRepetitionResponse(
        player_id=player_id,
        items=items,
        urgent_review_count=urgent
    )


@router.get("/weak-topics/{player_id}", response_model=WeakTopicsResponse, summary="Pandas GroupBy Topic Analysis")
async def get_weak_topics(player_id: str):
    """
    Pandas groupby aggregation analyzing performance consistency and identifying lowest-scoring topics.
    """
    res = analyze_weak_grammar_topics(player_id)
    return WeakTopicsResponse(
        player_id=player_id,
        weakest_topics=res["weakest_topics"],
        strongest_topics=res["strongest_topics"],
        overall_average=res["overall_average"],
        total_exercises_completed=res["total_exercises_completed"]
    )
