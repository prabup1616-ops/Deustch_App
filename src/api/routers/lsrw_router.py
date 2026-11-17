"""
FastAPI Router for Goethe B1 LSRW Modules.
Exposes REST endpoints for exercise generation, evaluation, and historical archives.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import base64
import re
import storage
from src.ai_service import (
    generate_reading_exercise,
    generate_writing_prompt,
    evaluate_writing_submission,
    generate_listening_exercise,
    generate_real_listening_exam,
    generate_speaking_cards,
    evaluate_speaking_response
)
from src.api.schemas import (
    ExerciseGenerateRequest,
    WritingSubmissionRequest,
    WritingEvaluationResponse,
    SpeakingSubmissionRequest,
    SpeakingEvaluationResponse,
    SubmissionRecordResponse
)

router = APIRouter(prefix="/api/v1/lsrw", tags=["LSRW Exam Training"])


@router.post("/generate", summary="Generate a targeted Goethe B1 exercise")
async def generate_exercise(req: ExerciseGenerateRequest):
    """
    Generates an exam-accurate Goethe B1 exercise with anti-repetition filtering.
    """
    api_key = storage.get_gemini_api_key()
    if not api_key:
        raise HTTPException(status_code=400, detail="Gemini API key is not configured in settings.")

    mod = req.module.lower().strip()
    topics = req.topics or ["Präpositionen (Wechselpräpositionen)"]

    # Gather user's past scenarios for negative prompting
    past_subs = storage.get_lsrw_submissions(req.player_id, module=mod, limit=25)
    past_scenarios = []
    for s in past_subs:
        pd = s.get("prompt_data", {})
        sc = pd.get("scenario_de") or pd.get("title") or pd.get("type")
        if sc and sc not in past_scenarios:
            past_scenarios.append(str(sc)[:75])

    learned = storage.get_learned_topics(req.player_id)
    prior_topics = [t["topic"] for t in learned if t["topic"] not in topics]

    try:
        if mod == "writing":
            data = generate_writing_prompt(
                api_key, topics, lang="de",
                force_refresh=req.force_refresh,
                exclude_scenarios=past_scenarios,
                prior_topics=prior_topics
            )
        elif mod == "reading":
            data = generate_reading_exercise(
                api_key, topics, lang="de",
                force_refresh=req.force_refresh,
                exclude_scenarios=past_scenarios,
                prior_topics=prior_topics
            )
        elif mod == "listening":
            data = generate_real_listening_exam(
                api_key, topics,
                force_refresh=req.force_refresh,
                exclude_scenarios=past_scenarios,
                prior_topics=prior_topics
            )
        elif mod == "speaking":
            data = generate_speaking_cards(
                api_key, topics,
                force_refresh=req.force_refresh,
                exclude_scenarios=past_scenarios,
                prior_topics=prior_topics
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown module '{mod}'. Expected: reading, writing, listening, speaking")

        return {"module": mod, "topics": topics, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


@router.post("/writing/evaluate", response_model=WritingEvaluationResponse, summary="Evaluate a B1 essay")
async def evaluate_writing(req: WritingSubmissionRequest):
    """
    Evaluates a written submission against Goethe B1 rubrics with automatic grade parsing.
    """
    api_key = storage.get_gemini_api_key()
    if not api_key:
        raise HTTPException(status_code=400, detail="Gemini API key is not configured.")

    try:
        feedback = evaluate_writing_submission(
            api_key, req.prompt_data, req.user_text, [req.topic], lang="de"
        )
        score = 8
        match = re.search(r'(\d+[\.,]?\d*)\s*/\s*10', feedback)
        if match:
            try:
                score = int(round(float(match.group(1).replace(",", "."))))
            except Exception:
                pass

        # Save to database
        storage.save_lsrw_submission(
            player_id=req.player_id,
            module="writing",
            topic=req.topic,
            prompt_data=req.prompt_data,
            user_submission=req.user_text,
            feedback=feedback,
            score=score,
            total=10
        )

        word_count = len(req.user_text.split())
        return WritingEvaluationResponse(
            score=score,
            total=10,
            feedback=feedback,
            word_count=word_count,
            topic=req.topic
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Writing evaluation error: {str(e)}")


@router.post("/speaking/evaluate", response_model=SpeakingEvaluationResponse, summary="Evaluate oral response")
async def evaluate_speaking(req: SpeakingSubmissionRequest):
    """
    Evaluates speech response (supports base64 audio or fallback typed text).
    """
    api_key = storage.get_gemini_api_key()
    if not api_key:
        raise HTTPException(status_code=400, detail="Gemini API key is not configured.")

    raw_audio = None
    if req.audio_base64:
        try:
            raw_audio = base64.b64decode(req.audio_base64)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid audio_base64 encoding")

    try:
        feedback = evaluate_speaking_response(
            api_key=api_key,
            topic=req.topic_de,
            grammar=req.grammar_focus,
            lang="de",
            typed_text=req.typed_text,
            raw_audio=raw_audio,
            audio_mime=req.audio_mime or "audio/webm"
        )
        score = 8
        match = re.search(r'(\d+[\.,]?\d*)\s*/\s*10', feedback)
        if match:
            try:
                score = int(round(float(match.group(1).replace(",", "."))))
            except Exception:
                pass

        user_sub_desc = req.typed_text if req.typed_text else f"Audio Submission ({req.audio_mime})"
        storage.save_lsrw_submission(
            player_id=req.player_id,
            module="speaking",
            topic=req.topic_de,
            prompt_data={"topic_de": req.topic_de, "grammar": req.grammar_focus},
            user_submission=user_sub_desc,
            feedback=feedback,
            score=score,
            total=10
        )

        return SpeakingEvaluationResponse(
            score=score,
            total=10,
            feedback=feedback,
            topic=req.topic_de
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speaking evaluation error: {str(e)}")


@router.get("/submissions/{player_id}", response_model=List[SubmissionRecordResponse], summary="Get learner history")
async def get_submissions(player_id: str, module: Optional[str] = Query(default=None)):
    """
    Fetches past attempts, scores, and AI evaluations for a learner.
    """
    subs = storage.get_lsrw_submissions(player_id, module=module, limit=50)
    records = []
    for s in subs:
        records.append(SubmissionRecordResponse(
            module=s.get("module", "lsrw"),
            topic=s.get("topic", "General"),
            score=s.get("score", 0),
            total=s.get("total", 10),
            date=s.get("date") or str(s.get("timestamp", ""))[:10] or "Today",
            prompt_data=s.get("prompt_data") or {},
            user_submission=s.get("user_submission") or "",
            feedback=s.get("feedback") or ""
        ))
    return records


@router.delete("/submissions/{player_id}", summary="Clear learner history")
async def clear_submissions(player_id: str):
    """
    Clears all saved submissions for a learner.
    """
    storage.clear_lsrw_submissions(player_id)
    return {"status": "cleared", "player_id": player_id}
