"""
Pydantic V2 Request & Response Schemas for Goethe B1 Master API.
Provides type validation, constraints, and OpenAPI documentation generation.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# ==============================================================================
# SYSTEM & HEALTH
# ==============================================================================

class HealthCheckResponse(BaseModel):
    status: str = Field(default="ok", example="ok")
    app_version: str = Field(default="2.0.0")
    database_connected: bool
    timestamp: str


# ==============================================================================
# LSRW SCHEMAS
# ==============================================================================

class ExerciseGenerateRequest(BaseModel):
    module: str = Field(..., description="Module name: reading, writing, listening, speaking", example="writing")
    topics: List[str] = Field(default=["Präpositionen (Wechselpräpositionen)"], description="Target grammar topics")
    force_refresh: bool = Field(default=False, description="Bypass cache and generate fresh AI scenario")
    player_id: Optional[str] = Field(default="gast", description="Player identifier for scenario personalization")


class WritingSubmissionRequest(BaseModel):
    player_id: str = Field(default="gast")
    topic: str = Field(..., example="Präpositionen (Wechselpräpositionen)")
    prompt_data: Dict[str, Any] = Field(..., description="The prompt and leitpunkte provided by the task")
    user_text: str = Field(..., min_length=5, description="Student's German written essay")


class WritingEvaluationResponse(BaseModel):
    score: int = Field(..., ge=0, le=10, description="Score between 0 and 10")
    total: int = Field(default=10)
    feedback: str = Field(..., description="Comprehensive Goethe B1 evaluation and model answer")
    word_count: int
    topic: str


class SpeakingSubmissionRequest(BaseModel):
    player_id: str = Field(default="gast")
    topic_de: str = Field(..., example="Wohnen und Möbel")
    grammar_focus: str = Field(default="Präpositionen")
    typed_text: Optional[str] = Field(default=None, description="Typed text if microphone was not used")
    audio_base64: Optional[str] = Field(default=None, description="Base64 encoded audio string if spoken")
    audio_mime: Optional[str] = Field(default="audio/webm")


class SpeakingEvaluationResponse(BaseModel):
    score: int = Field(..., ge=0, le=10)
    total: int = Field(default=10)
    feedback: str
    topic: str


class SubmissionRecordResponse(BaseModel):
    module: str
    topic: str
    score: int
    total: int
    date: str
    prompt_data: Dict[str, Any]
    user_submission: str
    feedback: str


# ==============================================================================
# ANALYTICS & MACHINE LEARNING SCHEMAS
# ==============================================================================

class ModuleBreakdown(BaseModel):
    reading_pct: float
    writing_pct: float
    listening_pct: float
    speaking_pct: float


class B1ReadinessResponse(BaseModel):
    player_id: str
    readiness_percentage: float = Field(..., description="ML Predicted CEFR B1 Readiness Index (0-100%)")
    verdict: str
    recommendation: str
    module_breakdown: ModuleBreakdown
    modules_at_pass_threshold: str
    total_practice_sessions: int


class SpacedRepetitionItem(BaseModel):
    topic: str
    retention_probability: float = Field(..., description="Calculated recall probability percentage")
    days_since_last_practice: int
    practice_count: int
    mean_score_pct: float
    status: str


class SpacedRepetitionResponse(BaseModel):
    player_id: str
    items: List[SpacedRepetitionItem]
    urgent_review_count: int


class WeakTopicsResponse(BaseModel):
    player_id: str
    weakest_topics: List[Dict[str, Any]]
    strongest_topics: List[Dict[str, Any]]
    overall_average: float
    total_exercises_completed: int


# ==============================================================================
# DUEL SCHEMAS
# ==============================================================================

class LeaderboardEntry(BaseModel):
    rank: int
    name: str
    score: int
    streak: int
    accuracy: float
