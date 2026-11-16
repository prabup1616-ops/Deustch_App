"""
Duel Engine & Continuous Progression Manager
Provides:
1. Continuous Daily Progression (Day 1, Day 2, Day 3...) tracking per player.
2. Smart Retake Question Builder: preserves wrong questions, discards correct ones, and adds fresh new questions.
3. Comprehensive Player Progress Dashboard with trend analysis (improving / steady / needs review).
Applies symmetrically to both:
- Translation Duel (Possessivartikel & Cases in Telugu/Kannada)
- Der/Die/Das Gender Duel (Goethe B1 Nouns)
"""
import random
from datetime import date
from typing import List, Dict, Any, Set, Tuple
import streamlit as st
import storage
import questions
import src.gender_questions as gq


# ==============================================================================
# 1. CURRICULUM & RETAKE QUESTION BUILDERS
# ==============================================================================

def get_day_curriculum_questions(category: str, day_number: int, count: int = 5) -> List[Dict[str, Any]]:
    """
    Returns the progressive batch of 5 questions for Day N:
    - Day 1: Questions 1 to 5
    - Day 2: Questions 6 to 10
    - Day 3: Questions 11 to 15
    """
    safe_day = max(1, day_number)
    if category == "gender":
        total_packs = gq.get_total_gender_packs(count=count)
        pack_idx = ((safe_day - 1) % total_packs) + 1
        return gq.get_gender_pack_questions(pack_idx, count=count)
    else:
        total_packs = max(1, (len(questions.QUESTIONS_DATA) + count - 1) // count)
        pack_idx = ((safe_day - 1) % total_packs) + 1
        return questions.get_day_pack_questions(pack_idx, count=count)


def build_retake_question_set(
    per_q_results: List[Dict[str, Any]],
    all_pool: List[Dict[str, Any]],
    seen_ids: Set[int],
    target_count: int = 5
) -> Tuple[List[Dict[str, Any]], List[int], int]:
    """
    Constructs a smart retake question set:
    1. Preserves ONLY the questions the player answered incorrectly (second chance).
    2. Completely DISCARDS the questions the player got right.
    3. Fills up the remaining slots with BRAND NEW questions from the pool.
    
    Returns:
    - retake_set: list of questions (length == target_count)
    - updated_seen_ids: list of all IDs encountered so far
    - wrong_count: count of wrong questions preserved
    """
    # 1. Isolate the questions answered incorrectly
    wrong_questions = [r["question"] for r in per_q_results if not r.get("is_correct", False)]
    wrong_ids = {q["id"] for q in wrong_questions}
    wrong_count = len(wrong_questions)

    # 2. Number of fresh questions needed
    needed = max(0, target_count - wrong_count)

    # 3. Find candidates not seen yet and not in wrong_questions
    candidates = [q for q in all_pool if q["id"] not in seen_ids and q["id"] not in wrong_ids]
    if len(candidates) < needed:
        # Fallback if pool exhausted: any question not currently in wrong_questions
        candidates = [q for q in all_pool if q["id"] not in wrong_ids]

    # Sample needed fresh questions
    new_questions = random.sample(candidates, min(needed, len(candidates))) if candidates else []

    # Combine: wrong questions + brand new questions
    retake_set = wrong_questions + new_questions

    # Shuffle order so the retake feels fresh
    random.shuffle(retake_set)

    # Make sure we return exactly target_count
    final_set = retake_set[:target_count]
    updated_seen = list(seen_ids.union({q["id"] for q in final_set}))

    return final_set, updated_seen, wrong_count


# ==============================================================================
# 2. CONTINUOUS JOURNEY PROGRESS DASHBOARD
# ==============================================================================

def render_player_progress_dashboard(
    player_id: str,
    player_name: str,
    category: str = "pronoun",
    title_prefix: str = "🎯 Translation Duel"
):
    """
    Renders the continuous progress tracker for any player:
    - Day-by-day progression table
    - Trend analysis & improvement score indicator
    - Visual history spark/metrics
    """
    hist_data = storage.get_player_continuous_history(player_id, category=category)
    history = hist_data["history"]
    cur_day = hist_data["current_day_number"]
    total_days = hist_data["total_days_completed"]
    overall_avg = hist_data["overall_average"]
    overall_pct = hist_data["overall_pct"]
    is_today = hist_data["is_played_today"]

    theme_color = "#2563eb" if category == "pronoun" else "#059669"
    badge_bg = "#eff6ff" if category == "pronoun" else "#f0fdf4"
    border_c = "#bfdbfe" if category == "pronoun" else "#bbf7d0"

    st.markdown(f"""
    <div style="background: {badge_bg}; border: 2px solid {border_c}; border-radius: 14px; padding: 18px 22px; margin: 16px 0;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 10px;">
            <div>
                <span style="font-size: 1.15rem; font-weight: 800; color: {theme_color};">
                    📈 Continuous Progress Tracker • {player_name}
                </span>
                <div style="font-size: 0.85rem; color: #64748b; margin-top: 2px;">
                    {title_prefix} • Daily Learning Journey & Score Improvement History
                </div>
            </div>
            <div style="display: flex; gap: 10px; align-items: center;">
                <span style="background: {theme_color}; color: white; padding: 4px 14px; border-radius: 999px; font-weight: 800; font-size: 0.85rem;">
                    {'🗓️ Day ' + str(cur_day) + ' Active' if not is_today else '✅ Day ' + str(cur_day) + ' Completed Today'}
                </span>
            </div>
        </div>
        <p style="font-size: 0.92rem; color: #1e293b; margin: 0 0 14px 0;">
            {hist_data['improvement_summary']}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 4 Quick Metric Cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(
            label="Current Day",
            value=f"Day {cur_day}",
            delta="Next Day" if not is_today else "Played Today"
        )
    with m2:
        st.metric(
            label="Overall Average",
            value=f"{overall_avg:.2f} / 5.0",
            delta=f"{overall_pct}% Mastery"
        )
    with m3:
        st.metric(
            label="Days Practiced",
            value=f"{total_days} Days",
            delta=f"{hist_data['total_attempts']} Attempts"
        )
    with m4:
        # Latest day trend delta
        if history:
            latest_delta = history[-1].get("trend_delta", 0.0)
            st.metric(
                label="Latest Trend",
                value="Improving" if latest_delta > 0 else ("Steady" if latest_delta == 0 else "Review"),
                delta=f"{latest_delta:+.2f} marks" if latest_delta != 0 else "Stable"
            )
        else:
            st.metric(label="Latest Trend", value="Day 1 Ready", delta="Start Now")

    # Detailed Daily Breakdown
    if history:
        with st.expander(f"📜 View All Completed Days & Score Logs ({len(history)} Day(s))", expanded=False):
            table_rows = []
            for h in history:
                table_rows.append({
                    "Day Number": f"🗓️ Day {h['day_number']}",
                    "Date / Session": h["date"],
                    "Normalized Average": f"{h['average_score']:.2f} / 5.0 ({h['pct']}%)",
                    "Best Score": f"{h['best_score']} / 5",
                    "Attempts": h["attempts_count"],
                    "Trend": h["trend"],
                    "Scores Log": str(h["scores"])
                })
            st.table(table_rows)
