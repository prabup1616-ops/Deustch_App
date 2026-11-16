"""
Root forwarding module for gender questions.
"""
from src.gender_questions import (
    load_all_gender_questions,
    get_daily_gender_questions,
    get_gender_pack_questions,
    get_total_gender_packs,
    GENDER_QUESTIONS_DATA
)

__all__ = [
    "load_all_gender_questions",
    "get_daily_gender_questions",
    "get_gender_pack_questions",
    "get_total_gender_packs",
    "GENDER_QUESTIONS_DATA"
]
