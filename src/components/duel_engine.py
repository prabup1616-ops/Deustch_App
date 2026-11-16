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


def get_topic_curriculum_questions(
    topic: str,
    category: str = "pronoun",
    count: int = 5,
    day_number: int = 1
) -> List[Dict[str, Any]]:
    """
    Fetches questions for the selected topic:
    - If baseline topic: uses standard day curriculum questions.
    - If custom unlocked topic (e.g. 'Weak Masculine Declination'):
      1. Pulls questions from questions_repo (in DB / local).
      2. If pool is small, supplements with starter topic questions from STARTER_TOPIC_QUESTIONS.
      3. Mixes in 1-2 review questions from baseline questions to reinforce prior topics.
    """
    clean_topic = topic.strip()
    is_baseline = ("baseline" in clean_topic.lower() or "possessivartikel" in clean_topic.lower() if category == "pronoun" else "nouns" in clean_topic.lower())

    if is_baseline:
        return get_day_curriculum_questions(category, day_number, count=count)

    # 1. Fetch from questions_repo in DB / storage
    repo_qs = storage.get_repo_questions_for_topic(clean_topic, category=category)

    # 2. Supplement from starter questions if repo is small
    try:
        from src.ai_service import STARTER_TOPIC_QUESTIONS
        if len(repo_qs) < 3:
            for sk, sqs in STARTER_TOPIC_QUESTIONS.items():
                if sk in clean_topic.lower() or clean_topic.lower() in sk:
                    for q in sqs:
                        if not any(eq.get("target_de") == q.get("target_de") for eq in repo_qs):
                            repo_qs.append(q)
    except Exception:
        pass

    # 3. Fallback to baseline if no questions found yet
    if not repo_qs:
        return get_day_curriculum_questions(category, day_number, count=count)

    # Target: 3-4 questions from current topic + 1-2 questions from baseline (past topics)
    topic_count = min(len(repo_qs), max(3, count - 1))
    review_count = count - topic_count

    selected_topic_qs = random.sample(repo_qs, topic_count) if len(repo_qs) >= topic_count else repo_qs

    review_qs = []
    if review_count > 0:
        base_qs = get_day_curriculum_questions(category, day_number, count=5)
        review_qs = random.sample(base_qs, min(review_count, len(base_qs)))

    final_pool = selected_topic_qs + review_qs
    random.shuffle(final_pool)
    return final_pool[:count]


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
# 2B. 10-DAY MILESTONE TOPIC UNLOCK & SELECTOR
# ==============================================================================

def render_10day_topic_unlock_card(
    player_id: str,
    player_name: str,
    category: str = "pronoun",
    key_prefix: str = "quiz"
):
    """
    Renders the 10-Day Milestone Card:
    - If player has reached Day 10+ or completed >= 10 days of duels:
      Shows an unlock card allowing the player to enter/choose their next grammar topic.
    - Shows suggestions of topics unlocked by other learners in the community.
    - Asynchronously triggers background AI question generation with Gemini and stores questions in questions_repo.
    """
    import threading

    clean_pid = str(player_id).strip().lower().replace(" ", "_")
    hist_data = storage.get_player_continuous_history(clean_pid, category=category)
    total_days = hist_data.get("total_days_completed", 0)
    cur_day = hist_data.get("current_day_number", 1)

    is_milestone_reached = (total_days >= 10 or cur_day >= 10)

    if not is_milestone_reached:
        days_left = max(1, 10 - total_days)
        st.markdown(f"""
        <div style="background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 10px; padding: 10px 14px; margin: 10px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; color: #64748b;">
                <span>🎯 <strong>10-Day Topic Unlock:</strong> {total_days}/10 days completed</span>
                <span>{days_left} more day(s) to unlock custom grammar topics!</span>
            </div>
            <div style="width: 100%; background: #e2e8f0; height: 6px; border-radius: 999px; margin-top: 6px; overflow: hidden;">
                <div style="width: {min(100, int((total_days / 10.0) * 100))}%; background: #2563eb; height: 100%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # 10 Days Milestone Reached!
    community_topics = storage.get_community_topics(category=category)
    player_unlocked = storage.get_player_unlocked_topics(clean_pid, category=category)
    current_topic = storage.get_player_current_topic(clean_pid, category=category)

    # Filter community topics that player hasn't added yet
    available_community = [t for t in community_topics if t not in player_unlocked]

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #fef9c3 0%, #fef08a 100%); border: 2px solid #eab308; border-radius: 14px; padding: 18px 22px; margin: 14px 0; box-shadow: 0 4px 12px rgba(234, 179, 8, 0.15);">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.8rem;">🎉</span>
            <div>
                <h3 style="margin: 0; font-size: 1.22rem; color: #854d0e;">10-Day Goethe B1 Milestone Unlocked!</h3>
                <p style="margin: 2px 0 0 0; font-size: 0.88rem; color: #713f12;">
                    Congratulations, <strong>{player_name}</strong>! You have reached 10 days of continuous duels. You can now unlock your next grammar topic (e.g. <em>Weak Masculine Declination</em>, <em>Passiv</em>, <em>Relativsätze</em>).
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🔓 Unlock a New Grammar Topic (Type or Choose from Community)", expanded=True):
        col_type, col_com = st.columns([1, 1], gap="medium")

        with col_type:
            st.markdown("**Option A: Type Your Next Topic**")
            new_custom_topic = st.text_input(
                "Write your next grammar topic:",
                placeholder="e.g. Weak Masculine Declination (N-Deklination)",
                key=f"{key_prefix}_custom_topic_input"
            )

        with col_com:
            st.markdown("**Option B: Community Topics from Other Learners**")
            com_selection = st.selectbox(
                "Choose from community pool:",
                options=["-- Select a community topic --"] + (available_community if available_community else community_topics),
                index=0,
                key=f"{key_prefix}_community_topic_select"
            )

        unlock_clicked = st.button("🚀 Unlock & Feed Topic into DB Repository", type="primary", key=f"{key_prefix}_submit_new_topic_btn")

        if unlock_clicked:
            chosen_topic = ""
            if new_custom_topic and new_custom_topic.strip():
                chosen_topic = new_custom_topic.strip()
            elif com_selection and not com_selection.startswith("--"):
                chosen_topic = com_selection.strip()

            if not chosen_topic:
                st.warning("⚠️ Please type a new topic or select one from the community suggestions!")
            else:
                # 1. Register topic for player & community
                storage.add_player_unlocked_topic(clean_pid, chosen_topic, category=category)
                storage.set_player_current_topic(clean_pid, chosen_topic, category=category)

                # 2. Check if questions already exist in questions_repo
                existing_qs = storage.get_repo_questions_for_topic(chosen_topic, category=category)

                # 3. Launch background AI generator with Gemini if fewer than 5 questions
                if len(existing_qs) < 5:
                    def _bg_generate(t_name, cat, pid):
                        try:
                            from src.ai_service import generate_topic_questions
                            api_k = storage.get_gemini_api_key()
                            past_t = storage.get_player_unlocked_topics(pid, category=cat)
                            new_qs = generate_topic_questions(t_name, category=cat, count=10, api_key=api_k, past_topics=past_t)
                            if new_qs:
                                storage.save_repo_questions_for_topic(t_name, cat, new_qs, created_by=f"ai_{pid}")
                        except Exception:
                            pass

                    bg_thread = threading.Thread(target=_bg_generate, args=(chosen_topic, category, clean_pid), daemon=True)
                    bg_thread.start()

                st.success(f"✨ Topic **'{chosen_topic}'** unlocked and set as your active duel topic! Questions are ready and syncing with DB in the background.")
                st.rerun()


def render_topic_selector(player_id: str, category: str = "pronoun", key_prefix: str = "quiz") -> str:
    """
    Renders the 'Choose Topic' dropdown in Step 3 of the lobby:
    - Lists all topics unlocked by this player.
    - Pre-selected with the player's active current_topic.
    - If the player switches topic, immediately updates current_topic.
    - Returns the selected topic.
    """
    clean_pid = str(player_id).strip().lower().replace(" ", "_")
    unlocked_topics = storage.get_player_unlocked_topics(clean_pid, category=category)
    current_topic = storage.get_player_current_topic(clean_pid, category=category)

    if current_topic not in unlocked_topics:
        unlocked_topics.append(current_topic)

    cur_idx = unlocked_topics.index(current_topic) if current_topic in unlocked_topics else 0

    st.markdown("---")
    st.markdown("### 📚 Choose Grammar Topic / ವ್ಯಾಕರಣ ವಿಷಯವನ್ನು ಆಯ್ಕೆಮಾಡಿ")
    st.caption("Duel questions will focus on this topic, combined with review questions from prior topics.")

    chosen_topic = st.selectbox(
        "Select Active Topic for this Duel:",
        options=unlocked_topics,
        index=cur_idx,
        key=f"{key_prefix}_active_topic_selector",
        help="Questions will be drawn from this topic and reinforced with past topics."
    )

    if chosen_topic != current_topic:
        storage.set_player_current_topic(clean_pid, chosen_topic, category=category)

    return chosen_topic


# ==============================================================================
# 3. DYNAMIC PLAYER SELECTOR (DROPDOWN FIRST: OLD VS NEW)
# ==============================================================================

def render_dynamic_player_selector(category: str = "pronoun", key_prefix: str = "quiz") -> Dict[str, Any]:
    """
    Renders the 2-step Player Identification system:
    1. Dropdown for Player Type: 'Old Player (Returning)' vs 'New Player (Register)'.
    2. If Old Player:
       - 'Search your name' blank input field.
       - As user types (e.g. 'P'), dynamic suggestions appear for matching existing profiles (Prabu, Prakash...).
    3. If New Player:
       - 'Register your name' blank input field.
       - If the name already exists, automatically creates a unique identifier (e.g. 'Prabu #2', 'prabu_2').
    """
    from src.config import AVATAR_CHOICES

    all_saved = storage.get_all_saved_players()
    
    st.markdown("### 1. ✍️ Player Identification")
    
    # Step 1: Dropdown for Old vs New Player
    player_type = st.selectbox(
        "Player Type / ప్లేయర్ రకం / ಆಟಗಾರನ ಪ್ರಕಾರ:",
        options=["👤 Existing Player (Returning)", "➕ New Player (Register)"],
        index=0,
        key=f"{key_prefix}_player_type_dropdown",
        help="Select 'Existing Player' to resume your saved streak, or 'New Player' to register fresh."
    )

    is_returning = ("Existing Player" in player_type)

    # --------------------------------------------------------------------------
    # FLOW A: EXISTING RETURNING PLAYER (INSTANT GOOGLE-STYLE AUTOCOMPLETE)
    # --------------------------------------------------------------------------
    if is_returning:
        # Search callback executed on every keystroke (real-time Google-style suggestions)
        def _search_saved_players(query: str):
            if not query or not query.strip():
                return []
            q = query.strip().lower()
            matches = [p for p in all_saved if q in p.get("name", "").lower()]
            # Returns (Label, Value) tuples for the live dropdown menu (WITHOUT ID)
            return [(f"{p.get('avatar', '👤')}  {p['name']}", p["id"]) for p in matches]

        selected_player_id = None

        try:
            from streamlit_searchbox import st_searchbox

            selected_player_id = st_searchbox(
                _search_saved_players,
                placeholder="🔍 Type to search your name (e.g. type 'P', 'Prabu', 'Prakash')...",
                label="Search your name / మీ పేరును వెతకండి / ನಿಮ್ಮ ಹೆಸರನ್ನು ಹುಡುಕಿ:",
                default=None,
                debounce=100,
                key=f"{key_prefix}_instant_player_searchbox",
            )
        except Exception:
            # Fallback to searchable selectbox if custom component not loaded
            player_options = {f"{p.get('avatar', '👤')} {p['name']}": p["id"] for p in all_saved}
            choice = st.selectbox(
                "Search your name / మీ పేరును వెతకండి / ನಿಮ್ಮ ಹೆಸರನ್ನು ಹುಡುಕಿ:",
                options=list(player_options.keys()),
                index=None,
                placeholder="🔍 Type to search your name (e.g. Prabu, Prakash)...",
                key=f"{key_prefix}_fallback_player_selectbox",
            )
            selected_player_id = player_options.get(choice) if choice else None
            selected_player_id = player_options.get(choice) if choice else None

        chosen_player = next((p for p in all_saved if p["id"] == selected_player_id), None) if selected_player_id else None

        if chosen_player:
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

            col_btn, _ = st.columns([1, 2])
            with col_btn:
                if st.button("🔄 Clear / Search Different Player", key=f"{key_prefix}_clear_search_btn"):
                    if f"{key_prefix}_instant_player_searchbox" in st.session_state:
                        del st.session_state[f"{key_prefix}_instant_player_searchbox"]
                    st.rerun()

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
            st.info("👆 Start typing your name in the search box above (e.g. type 'P') to see live Google-style suggestions, then click to select.")
            st.caption("💡 Don't see your name? Change **Player Type** above to **➕ New Player (Register)** to create your profile!")
            return {
                "selected_player_id": None,
                "player_name": "",
                "avatar": "🦁",
                "email": "",
                "is_ready": False,
                "is_new": False
            }

    # --------------------------------------------------------------------------
    # FLOW B: NEW PLAYER REGISTRATION
    # --------------------------------------------------------------------------
    else:
        new_name_raw = st.text_input(
            "Register your name / కొత్త పేరును నమోదు చేయండి / ಹೊಸ ಹೆಸರನ್ನು ನೋಂದಾಯಿಸಿ:",
            value=st.session_state.get(f"{key_prefix}_new_reg_name_val", ""),
            placeholder="Enter your name (e.g. Suresh, Kavya, Arjun, Prabu)...",
            key=f"{key_prefix}_new_reg_name_input",
            help="Type your desired name. If the name is already taken, you will be assigned a unique tag (e.g. Prabu #2)."
        )

        clean_new_name = new_name_raw.strip()

        if not clean_new_name:
            st.info("👆 Please enter your name above to register as a new player.")
            return {
                "selected_player_id": None,
                "player_name": "",
                "avatar": "🦁",
                "email": "",
                "is_ready": False,
                "is_new": True
            }

        # Check if name is taken by an existing player
        is_taken = any(p.get("name", "").strip().lower() == clean_new_name.lower() for p in all_saved)

        if is_taken:
            st.markdown(f"""
            <div style="background: #fefce8; border: 2px solid #fde047; border-radius: 12px; padding: 12px 18px; margin: 8px 0;">
                <span style="font-weight: 700; color: #854d0e;">💡 Duplicate Name Notice:</span><br>
                <span style="font-size: 0.85rem; color: #713f12;">
                    An existing player is already registered as <strong>"{clean_new_name}"</strong>.<br>
                    Your new profile will be created with a unique identifier (e.g. <code>{clean_new_name} #2</code>) so your scores and streaks remain completely separate!
                </span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: #eff6ff; border: 2px solid #bfdbfe; border-radius: 12px; padding: 12px 18px; margin: 8px 0;">
                <span style="font-weight: 700; color: #1e40af;">✨ Brand New Player: "{clean_new_name}"</span>
                <div style="font-size: 0.82rem; color: #64748b; margin-top: 2px;">
                    You will start fresh on <strong>Day 1</strong> of the Goethe B1 curriculum!
                </div>
            </div>
            """, unsafe_allow_html=True)

        col_a, col_e = st.columns([1, 2])
        with col_a:
            new_av = st.selectbox("Choose Avatar:", options=AVATAR_CHOICES, index=0, key=f"{key_prefix}_new_fresh_av")
        with col_e:
            new_em = st.text_input("Your Email (Optional):", value="", placeholder="you@example.com (for score alerts)", key=f"{key_prefix}_new_fresh_em")

        return {
            "selected_player_id": None,
            "player_name": clean_new_name,
            "avatar": new_av,
            "email": new_em,
            "is_ready": True,
            "is_new": True,
            "force_unique": is_taken
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
