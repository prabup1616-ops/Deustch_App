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


# ==============================================================================
# 3. DYNAMIC TYPE-AHEAD PLAYER SELECTOR (BLANK INITIAL STATE)
# ==============================================================================

def render_dynamic_player_selector(category: str = "pronoun", key_prefix: str = "quiz") -> Dict[str, Any]:
    """
    Renders an initial empty input field with dynamic type-ahead suggestions from DB:
    - Initially BLANK: Does NOT expose or pre-select any player names.
    - When user types: dynamically filters and suggests matching saved players.
    - If duplicate names exist, provides choice between 'Old Player (Existing)' and 'New Player (Register New)'.
    - If 'New Player' with an existing name is chosen, assigns a unique key (e.g. 'Prabu #2', 'prabu_2').
    """
    from src.config import AVATAR_CHOICES

    all_saved = storage.get_all_saved_players()
    
    st.markdown("### 1. ✍️ Player Identification")
    typed_raw = st.text_input(
        "Enter Player Name / మీ పేరును టైప్ చేయండి / ನಿಮ್ಮ ಹೆಸರನ್ನು ನಮೂದಿಸಿ:",
        value=st.session_state.get(f"{key_prefix}_typed_name_val", ""),
        placeholder="Type your name here (e.g. Prabu)...",
        key=f"{key_prefix}_typed_name_field",
        help="Field is blank by default. Start typing to see suggestions if you have played before, or type a new name to register."
    )
    
    clean_typed = typed_raw.strip()
    
    if not clean_typed:
        st.info("👆 Please type your name in the blank box above to start or load your progress.")
        return {
            "selected_player_id": None,
            "player_name": "",
            "avatar": "🦁",
            "email": "",
            "is_ready": False,
            "is_new": False
        }

    # Search for case-insensitive matches among saved players
    matches = [p for p in all_saved if clean_typed.lower() in p.get("name", "").lower()]

    if matches:
        st.markdown(f"**🔍 Suggestions for '{clean_typed}':**")
        options = []
        for p in matches:
            options.append(f"👤 Existing Player: {p.get('avatar', '👤')} {p['name']} (ID: {p['id']})")
        options.append(f"➕ Register New Player: '{clean_typed}' (New Profile)")

        selected_opt = st.radio(
            "Select your profile / మీ ప్రొఫైల్ ఎంచుకోండి:",
            options=options,
            index=0,
            key=f"{key_prefix}_profile_match_radio"
        )

        if "Existing Player" in selected_opt:
            matched_id = selected_opt.split("ID: ")[1].split(")")[0].strip()
            chosen_player = next((p for p in matches if p["id"] == matched_id), matches[0])
            p_name = chosen_player["name"]
            p_avatar = chosen_player.get("avatar", "🦁")
            p_email = chosen_player.get("email", "")

            st.markdown(f"""
            <div style="background: #f0fdf4; border: 2px solid #86efac; border-radius: 12px; padding: 12px 18px; margin: 8px 0;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span style="font-size: 2rem;">{p_avatar}</span>
                        <div>
                            <div style="font-size: 1.15rem; font-weight: 800; color: #166534;">{p_name}</div>
                            <div style="font-size: 0.82rem; color: #64748b;">Existing Profile Verified • Continuous Journey & Scores Active</div>
                        </div>
                    </div>
                    <span style="background: #16a34a; color: white; font-size: 0.75rem; font-weight: 700; padding: 4px 10px; border-radius: 999px;">Saved Profile</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("✏️ Customize Avatar / Email (Optional)"):
                col_a, col_e = st.columns([1, 2])
                with col_a:
                    cur_idx = AVATAR_CHOICES.index(p_avatar) if p_avatar in AVATAR_CHOICES else 0
                    new_av = st.selectbox("Avatar:", options=AVATAR_CHOICES, index=cur_idx, key=f"{key_prefix}_exist_av")
                with col_e:
                    new_em = st.text_input("Email:", value=p_email, key=f"{key_prefix}_exist_em")

            return {
                "selected_player_id": chosen_player["id"],
                "player_name": p_name,
                "avatar": new_av,
                "email": new_em,
                "is_ready": True,
                "is_new": False
            }
        else:
            # Register new player with unique identifier if name is taken
            st.markdown(f"""
            <div style="background: #fefce8; border: 2px solid #fde047; border-radius: 12px; padding: 12px 18px; margin: 8px 0;">
                <span style="font-weight: 700; color: #854d0e;">➕ Creating a Brand New Profile for "{clean_typed}"</span>
                <div style="font-size: 0.82rem; color: #713f12; margin-top: 4px;">
                    A unique identifier (e.g. <code>{clean_typed} #2</code>) will be assigned so your scores and streaks remain completely independent!
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_a, col_e = st.columns([1, 2])
            with col_a:
                new_av = st.selectbox("Choose Avatar:", options=AVATAR_CHOICES, index=0, key=f"{key_prefix}_new_dup_av")
            with col_e:
                new_em = st.text_input("Your Email (Optional):", value="", placeholder="you@example.com", key=f"{key_prefix}_new_dup_em")

            return {
                "selected_player_id": None,
                "player_name": clean_typed,
                "avatar": new_av,
                "email": new_em,
                "is_ready": True,
                "is_new": True,
                "force_unique": True
            }
    else:
        # Brand new name with no matches
        st.markdown(f"""
        <div style="background: #eff6ff; border: 2px solid #bfdbfe; border-radius: 12px; padding: 12px 18px; margin: 8px 0;">
            <span style="font-weight: 700; color: #1e40af;">✨ Brand New Player: "{clean_typed}"</span>
            <div style="font-size: 0.82rem; color: #64748b; margin-top: 2px;">
                You will start fresh on <strong>Day 1</strong> of the Goethe B1 curriculum!
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_a, col_e = st.columns([1, 2])
        with col_a:
            new_av = st.selectbox("Choose Avatar:", options=AVATAR_CHOICES, index=0, key=f"{key_prefix}_new_fresh_av")
        with col_e:
            new_em = st.text_input("Your Email (Optional):", value="", placeholder="you@example.com", key=f"{key_prefix}_new_fresh_em")

        return {
            "selected_player_id": None,
            "player_name": clean_typed,
            "avatar": new_av,
            "email": new_em,
            "is_ready": True,
            "is_new": True,
            "force_unique": False
        }


# ==============================================================================
# 4. ALL-TIME HIGHS SIDEBAR CARD
# ==============================================================================

def render_all_time_highs_sidebar(category: str = "pronoun"):
    """
    Renders the All-Time Highs leaderboard on the right-hand preview column:
    - Displays all players up to top 5 players (or whoever is on top).
    - Ranked by highest single score (Best Score e.g. 5/5 ⭐), overall average, and total points.
    - Medals for Top 5 (🥇, 🥈, 🥉, 4️⃣, 5️⃣).
    """
    theme_color = "#2563eb" if category == "pronoun" else "#059669"
    st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: space-between; margin: 20px 0 6px 0;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 1.4rem;">👑</span>
            <h3 style="margin: 0; font-size: 1.25rem; color: #1e293b;">All-Time High Scores (Top 5)</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Hall of Fame: Ranked by All-Time Best Scores, Normalized Average, and Total Points.")

    all_time = storage.get_all_time_stats(category=category, include_all_players=True)
    top_5 = all_time[:5]

    if top_5:
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        for rank, p in enumerate(top_5, start=1):
            badge = medals[rank - 1] if rank <= 5 else f"#{rank}"
            best_s = p.get("best_score", 0)
            avg_s = p.get("overall_average", 0.0)
            pts = p.get("total_points", 0)
            attempts = p.get("total_attempts", 0)
            days = p.get("days_active", 0)

            is_perfect = (best_s == 5)
            star = " ⭐" if is_perfect else ""
            status_tag = f"Best: {best_s}/5{star}" if attempts > 0 else "Ready to Duel"

            st.markdown(f"""
            <div style="background: white; border: 1px solid #e2e8f0; border-left: 4px solid {theme_color if attempts > 0 else '#94a3b8'}; border-radius: 10px; padding: 10px 14px; margin-bottom: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-weight: 800; font-size: 0.98rem; color: #1e293b;">
                        {badge} {p['avatar']} {p['name']}
                    </div>
                    <div style="background: {'#fef3c7' if is_perfect else ('#eff6ff' if attempts > 0 else '#f1f5f9')}; color: {'#b45309' if is_perfect else (theme_color if attempts > 0 else '#64748b')}; font-weight: 800; font-size: 0.88rem; padding: 2px 10px; border-radius: 999px;">
                        {status_tag}
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #64748b; margin-top: 6px;">
                    <span>Overall Avg: <strong>{avg_s:.2f} / 5.0</strong></span>
                    <span>Total: <strong>{pts} pts</strong> ({attempts} tries • {days}d)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No all-time scores recorded yet. Complete your first duel to claim the #1 spot in the Hall of Fame!")
