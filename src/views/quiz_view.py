import time
from datetime import date
import streamlit as st
import storage
import email_service
from questions import get_daily_questions, get_day_pack_questions, QUESTIONS_DATA
from src.config import AVATAR_CHOICES
from src.components import render_50sec_timer, trigger_confetti_and_sound, tts_button
from src.components.duel_engine import (
    get_day_curriculum_questions,
    get_topic_curriculum_questions,
    build_retake_question_set,
    render_player_progress_dashboard,
    render_10day_topic_unlock_card,
    render_topic_selector,
    render_dynamic_player_selector,
    render_all_time_highs_sidebar
)


def get_app_saved_players():
    """Safely retrieves all saved players even if module cache is stale."""
    if hasattr(storage, "get_all_saved_players"):
        return storage.get_all_saved_players()
    data = storage.load_data()
    players = list(data.get("players", {}).values())
    players.sort(key=lambda p: p.get("name", "").lower())
    return players


def render_quiz_view():
    """Renders the 3 stages of the Daily Duel Quiz: Lobby, Arena, and Results."""
    
    # ==========================================================================
    # SUB-STAGE 1: LOBBY (Player Selection & Quiz Setup)
    # ==========================================================================
    if st.session_state.quiz_stage == "lobby":
        st.markdown("""
        <div class="home-hero" style="padding: 24px 30px;">
            <h1 style="font-size: 2.2rem;">🎯 German B1 Daily Duel</h1>
            <p style="font-size: 1.05rem;">162 Goethe B1 Questions • 50s Timer Per Question • Multi-Attempt Normalization</p>
        </div>
        """, unsafe_allow_html=True)

        col_setup, col_preview = st.columns([3, 2], gap="large")

        with col_setup:
            player_info = render_dynamic_player_selector(category="pronoun", key_prefix="quiz")
            active_player_name = player_info["player_name"]
            is_player_ready = player_info["is_ready"]
            is_new_player = player_info.get("is_new", False)
            force_unique = player_info.get("force_unique", False)
            avatar_input = player_info["avatar"]
            email_input = player_info["email"]
            player_id_input = player_info.get("selected_player_id")

            if is_player_ready and active_player_name:
                clean_pid = player_id_input or active_player_name.strip().lower().replace(" ", "_")
                player_hist = storage.get_player_continuous_history(clean_pid, category="pronoun")
                cur_day = player_hist["current_day_number"]
                is_today_done = player_hist["is_played_today"]

                # Continuous Journey Progress Tracker for Selected Player
                render_player_progress_dashboard(clean_pid, active_player_name, category="pronoun", title_prefix="🎯 Translation Duel")

                # 10-Day Milestone Topic Unlock & Community Suggestions
                render_10day_topic_unlock_card(clean_pid, active_player_name, category="pronoun", key_prefix="quiz")
            else:
                cur_day = 1
                is_today_done = False

            st.markdown("---")
            st.markdown("### 2. 🌐 Choose Prompt Language")
            st.caption("STRICT ISOLATION: Selecting Telugu shows ONLY Telugu sentences. Selecting Kannada shows ONLY Kannada sentences.")

            lang_input = st.radio(
                "Select Language:",
                options=["Telugu (తెలుగు)", "Kannada (ಕನ್ನಡ)"],
                index=0 if st.session_state.lang_choice == "te" else 1
            )

            st.markdown("---")
            st.markdown("### 3. 🎯 Choose Quiz Set")
            
            if is_today_done:
                cont_opt_label = f"🗓️ Continuous Journey: Day - {cur_day} (Played Today — Retake to improve score average)"
            else:
                cont_opt_label = f"🗓️ Continuous Journey: Day - {cur_day} Challenge (Next in Sequence)"

            mode_input = st.radio(
                "Which set do you want to play?",
                options=[cont_opt_label, "📦 Practice Packs (Day 1 - 33 from 162 Bank)"],
                index=0
            )

            if "Continuous Journey" in mode_input:
                pack_tag = date.today().isoformat()
                pack_title = f"Day - {cur_day} Challenge ({date.today().strftime('%B %d, %Y')})"
                chosen_is_continuous = True
            else:
                pack_num = st.slider("Select Pack Number (1 to 33):", min_value=1, max_value=33, value=1)
                pack_tag = f"pack-{pack_num}"
                pack_title = f"Pack #{pack_num} (Questions {(pack_num-1)*5 + 1} to {min(pack_num*5, len(QUESTIONS_DATA))})"
                chosen_is_continuous = False

            # Choose Active Topic (Pre-selected with player's current topic)
            if is_player_ready and active_player_name:
                active_topic = render_topic_selector(clean_pid, category="pronoun", key_prefix="quiz")
            else:
                active_topic = "Possessivartikel (Baseline)"

            st.markdown("<br>", unsafe_allow_html=True)

            start_btn = st.button("🚀 START QUIZ NOW / క్విజ్ ప్రారంభించండి / ರಸಪ್ರಶ್ನೆ ಪ್ರಾರಂಭಿಸಿ", type="primary", use_container_width=True)
            if start_btn:
                clean_name = active_player_name.strip()
                if not is_player_ready or not clean_name:
                    st.error("⚠️ Please type or select your name above to start the quiz!")
                else:
                    if is_new_player:
                        saved_prof = storage.create_unique_player(clean_name, avatar_input, email_input.strip())
                    else:
                        saved_prof = storage.get_or_create_player(clean_name, avatar_input, email_input.strip())
                    canonical_name = saved_prof.get("name", clean_name)

                    st.session_state.player_name = canonical_name
                    st.session_state.player_avatar = saved_prof.get("avatar", avatar_input)
                    st.session_state.player_email = saved_prof.get("email", email_input.strip())
                    st.session_state.lang_choice = "te" if "Telugu" in lang_input else "kn"
                    st.session_state.pack_choice = pack_tag
                    st.session_state.pack_title = pack_title
                    st.session_state.active_topic = active_topic
                    st.session_state.retake_notice = None

                    if chosen_is_continuous:
                        initial_questions = get_topic_curriculum_questions(active_topic, category="pronoun", count=5, day_number=cur_day)
                    else:
                        initial_questions = get_day_pack_questions(pack_num, count=5)

                    st.session_state.active_questions = initial_questions
                    st.session_state.quiz_seen_q_ids = [q["id"] for q in initial_questions]

                    st.session_state.current_q_idx = 0
                    st.session_state.per_q_results = []
                    st.session_state.q_start_time = time.time()
                    st.session_state.quiz_result = None

                    st.session_state.quiz_stage = "arena"
                    st.rerun()

        with col_preview:
            st.markdown("### 🏆 Real-Time Duel Standings")
            today_board = storage.get_daily_leaderboard(date.today().isoformat())
            if today_board:
                st.write(f"**Today's Leaderboard ({len(today_board)} player(s) played):**")
                for rank, p in enumerate(today_board[:5], start=1):
                    medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
                    st.markdown(f"""<div style="display: flex; justify-content: space-between; align-items: center; background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px 14px; margin-bottom: 8px;">
<div><strong>{medal} {p['avatar']} {p['name']}</strong> ({p['attempts_count']} attempts)</div>
<div style="font-weight: 700; color: #2563eb;">{p['average_score']:.2f} / 5.0</div>
</div>""", unsafe_allow_html=True)
            else:
                st.info("No one has taken today's challenge yet. Be the first to set the high score!")

            # 🌟 All-Time High Scores Leaderboard on the right hand side
            render_all_time_highs_sidebar(category="pronoun")

    # ==========================================================================
    # SUB-STAGE 2: QUIZ ARENA (Pure Focus - 50s Timer Reset Per Question)
    # ==========================================================================
    elif st.session_state.quiz_stage == "arena":
        p_name = st.session_state.player_name
        p_avatar = st.session_state.player_avatar
        lang = st.session_state.lang_choice
        pack_tag = st.session_state.pack_choice
        pack_title = st.session_state.pack_title
        curr_idx = st.session_state.current_q_idx

        if "active_questions" not in st.session_state or not st.session_state.active_questions:
            if pack_tag.startswith("pack-"):
                pack_idx = int(pack_tag.split("-")[1])
                st.session_state.active_questions = get_day_pack_questions(pack_idx, count=5)
            else:
                st.session_state.active_questions = get_daily_questions(pack_tag, count=5)
            st.session_state.quiz_seen_q_ids = [q["id"] for q in st.session_state.active_questions]

        current_q = st.session_state.active_questions[curr_idx]

        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #1e3a8a 0%, #2563eb 100%); padding: 14px 20px; border-radius: 14px; color: white; display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <div style="font-size: 1.15rem; font-weight: 700;">
                {p_avatar} Player: <strong>{p_name}</strong> | 🎯 {pack_title} • 📚 {st.session_state.get('active_topic', 'Possessivartikel')}
            </div>
            <div style="font-size: 0.95rem; background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 20px;">
                Language: <strong>{'Telugu (తెలుగు)' if lang == 'te' else 'Kannada (ಕನ್ನಡ)'}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.get("retake_notice"):
            st.info(st.session_state.retake_notice)

        st.progress((curr_idx + 1) / 5.0, text=f"Question {curr_idx + 1} of 5")

        # 50s Countdown Timer strictly per question
        render_50sec_timer(curr_idx, st.session_state.q_start_time)

        # Question Card with Language Isolation
        prompt_html = f'<div class="prompt-box-te">నెం. {curr_idx + 1}: {current_q["prompt_te"]}</div>' if lang == "te" else f'<div class="prompt-box-kn">ಸಂ. {curr_idx + 1}: {current_q["prompt_kn"]}</div>'
        st.markdown(f"""<div class="question-card-anim">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
<span style="font-weight: 800; color: #1e3a8a; font-size: 1.25rem;">QUESTION {curr_idx + 1} OF 5</span>
<span style="color: #64748b; font-size: 0.9rem; font-weight: 600;">50 Seconds Limit</span>
</div>
{prompt_html}
</div>""", unsafe_allow_html=True)

        choice_key = f"q_step_{curr_idx}_{current_q['id']}"
        selected_option = st.radio(
            f"Select translation for Question {curr_idx + 1}:",
            options=current_q["options"],
            index=None,
            key=choice_key,
            label_visibility="collapsed"
        )

        col_submit, col_exit = st.columns([3, 1])
        with col_submit:
            btn_label = "✅ Lock In Answer & Next Question ➔" if curr_idx < 4 else "🚀 Submit Final Quiz & See Score 🏆"
            lock_clicked = st.button(btn_label, type="primary", use_container_width=True, key=f"btn_lock_{curr_idx}")
        with col_exit:
            exit_clicked = st.button("❌ Quit to Lobby", use_container_width=True)

        if exit_clicked:
            st.session_state.quiz_stage = "lobby"
            st.rerun()

        now = time.time()
        elapsed = now - st.session_state.q_start_time

        # Auto-advance if 50s expired OR if lock button was clicked
        if lock_clicked or elapsed >= 50.0:
            is_timeout = (elapsed >= 50.0)

            if is_timeout:
                is_correct = False
                choice_saved = "⏰ Timed Out (>50s) - 0 Marks (Skipped)"
            else:
                if selected_option is None:
                    is_correct = False
                    choice_saved = "No Option Selected (0 Marks)"
                else:
                    is_correct = (selected_option == current_q["target_de"])
                    choice_saved = selected_option

            st.session_state.per_q_results.append({
                "question": current_q,
                "user_choice": choice_saved,
                "target_de": current_q["target_de"],
                "is_correct": is_correct,
                "is_timeout": is_timeout,
                "elapsed": min(50.0, round(elapsed, 1))
            })

            if curr_idx < 4:
                st.session_state.current_q_idx += 1
                st.session_state.q_start_time = time.time()  # STRICT 50s RESET FOR NEXT QUESTION
                st.rerun()
            else:
                score = sum(1 for r in st.session_state.per_q_results if r["is_correct"])
                player_id = p_name.lower().replace(" ", "_")

                stats = storage.record_attempt(
                    player_id=player_id,
                    date_str=pack_tag,
                    score=score,
                    total=5,
                    details=st.session_state.per_q_results
                )

                data_all = storage.load_data()
                email_service.notify_other_players(
                    active_player_id=player_id,
                    active_player_name=p_name,
                    score=score,
                    total=5,
                    daily_stats=stats,
                    all_players=data_all.get("players", {}),
                    settings=data_all.get("settings", {})
                )

                st.session_state.quiz_result = {
                    "score": score,
                    "stats": stats,
                    "details": st.session_state.per_q_results
                }
                st.session_state.quiz_stage = "results"
                st.rerun()

    # ==========================================================================
    # SUB-STAGE 3: RESULTS & SCOREBOARD
    # ==========================================================================
    elif st.session_state.quiz_stage == "results":
        res = st.session_state.quiz_result
        p_name = st.session_state.player_name
        p_avatar = st.session_state.player_avatar
        lang = st.session_state.lang_choice
        pack_tag = st.session_state.pack_choice
        pack_title = st.session_state.pack_title

        score = res["score"]
        stats = res["stats"]

        trigger_confetti_and_sound(score, 5)

        badge_title = "🎉 AUSGEZEICHNET! (PERFECT SCORE)" if score == 5 else "👏 SEHR GUT! (GREAT JOB)" if score >= 3 else "💪 GUTER VERSUCH! (GOOD EFFORT)"

        st.markdown(f"""<div class="score-burst-card">
<h2 style="margin: 0; color: #fef08a; font-size: 1.6rem;">{badge_title}</h2>
<div class="score-number">{score} <span style="font-size: 2rem; color: #cbd5e1;">/ 5</span></div>
<p style="font-size: 1.25rem; font-weight: 600; margin: 4px 0 16px 0;">{p_avatar} {p_name}</p>
<div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
<div style="background: rgba(255,255,255,0.12); padding: 8px 18px; border-radius: 12px;">
<div style="font-size: 0.85rem; color: #cbd5e1;">Normalized Daily Average</div>
<div style="font-size: 1.4rem; font-weight: 700; color: #67e8f9;">{stats['average_score']:.2f} / 5.0</div>
</div>
<div style="background: rgba(255,255,255,0.12); padding: 8px 18px; border-radius: 12px;">
<div style="font-size: 0.85rem; color: #cbd5e1;">Attempts on this Set</div>
<div style="font-size: 1.4rem; font-weight: 700; color: #a7f3d0;">{stats['attempts_count']}</div>
</div>
<div style="background: rgba(255,255,255,0.12); padding: 8px 18px; border-radius: 12px;">
<div style="font-size: 0.85rem; color: #cbd5e1;">Best Score</div>
<div style="font-size: 1.4rem; font-weight: 700; color: #fde047;">{stats['best_score']} / 5</div>
</div>
</div>
</div>""", unsafe_allow_html=True)

        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            if st.button("🔄 Retake Quiz (Improve Average)", type="primary", use_container_width=True):
                prev_results = res.get("details", [])
                seen_ids = set(st.session_state.get("quiz_seen_q_ids", []))
                retake_questions, updated_seen, wrong_cnt = build_retake_question_set(
                    prev_results,
                    QUESTIONS_DATA,
                    seen_ids,
                    target_count=5
                )
                st.session_state.active_questions = retake_questions
                st.session_state.quiz_seen_q_ids = updated_seen
                st.session_state.current_q_idx = 0
                st.session_state.per_q_results = []
                st.session_state.q_start_time = time.time()
                st.session_state.quiz_result = None
                st.session_state.quiz_stage = "arena"
                st.session_state.retake_notice = f"🔄 Smart Retake Active: {wrong_cnt} incorrect question(s) reappeared for a second chance + {5 - wrong_cnt} fresh new question(s) added!"
                st.rerun()
        with col_b2:
            if st.button("👤 Switch Player / New Game", use_container_width=True):
                st.session_state.quiz_stage = "lobby"
                st.rerun()
        with col_b3:
            if st.button("🏠 Back to Portal Home", use_container_width=True):
                st.session_state.app_view = "home"
                st.rerun()

        st.caption("💡 **Smart Retake Engine**: Questions answered correctly disappear; your incorrect questions reappear for a second chance, plus fresh new questions are added to make 5!")

        # Continuous Journey Progress Dashboard in Results
        player_id = p_name.lower().replace(" ", "_")
        render_player_progress_dashboard(player_id, p_name, category="pronoun", title_prefix="🎯 Translation Duel")

        # Scoreboard Reveal
        st.markdown("---")
        st.header(f"🏆 Scoreboard & Competitor Standings ({pack_title})")
        st.caption("Ranked by Normalized Daily Average Score (Total Marks / Total Attempts).")

        board = storage.get_daily_leaderboard(pack_tag)
        if board:
            cols = st.columns(min(len(board), 3))
            medals = ["🥇 1st Place", "🥈 2nd Place", "🥉 3rd Place"]
            border_colors = ["#f59e0b", "#94a3b8", "#b45309"]

            for idx in range(min(len(board), 3)):
                entry = board[idx]
                is_active = (entry["name"].lower() == p_name.lower())
                with cols[idx]:
                    st.markdown(f"""
                    <div class="podium-card" style="border-color: {'#2563eb' if is_active else border_colors[idx]}; {'background: #f8fafc;' if is_active else ''}">
                        <div style="font-size: 2.4rem;">{entry['avatar']}</div>
                        <h3 style="margin: 4px 0; color: #1e293b;">{entry['name']} {'(You)' if is_active else ''}</h3>
                        <span style="font-weight: 700; color: {border_colors[idx]}; font-size: 0.95rem;">{medals[idx]}</span>
                        <hr style="margin: 10px 0; border: none; border-top: 1px solid #e2e8f0;">
                        <div style="font-size: 1.7rem; font-weight: 800; color: #2563eb;">
                            {entry['average_score']:.2f} <span style="font-size: 0.95rem; color: #64748b;">/ 5.0</span>
                        </div>
                        <div style="font-size: 0.85rem; color: #64748b; margin-top: 4px;">Normalized Average</div>
                        <div style="background: #f1f5f9; border-radius: 8px; padding: 6px; font-size: 0.82rem; text-align: left; margin-top: 8px;">
                            <div>🎯 <strong>Attempts:</strong> {entry['attempts_count']}</div>
                            <div>⭐ <strong>Best:</strong> {entry['best_score']} / 5</div>
                            <div>📊 <strong>Log:</strong> {entry['scores']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            table_rows = []
            for rank, b_entry in enumerate(board, start=1):
                table_rows.append({
                    "Rank": f"#{rank}",
                    "Player": f"{b_entry['avatar']} {b_entry['name']}",
                    "Daily Average (Normalized)": f"{b_entry['average_score']:.2f} / 5.0",
                    "Attempts": b_entry["attempts_count"],
                    "Best Score": f"{b_entry['best_score']} / 5",
                    "Scores Log": str(b_entry["scores"])
                })
            st.table(table_rows)

        # Question Breakdown
        st.markdown("---")
        st.header("🔍 Question-by-Question Review & Grammar Breakdown")

        for i, item in enumerate(res["details"], start=1):
            q = item["question"]
            is_right = item["is_correct"]
            u_ans = item["user_choice"]
            is_timeout = item.get("is_timeout", False)
            elapsed_t = item.get("elapsed", 50.0)

            status_badge = "⏰ TIMEOUT (0 Marks)" if is_timeout else "✅ CORRECT" if is_right else "❌ INCORRECT"

            with st.expander(f"{status_badge} - Question {i}: {q['topic']} (Time: {elapsed_t}s / 50s)", expanded=True):
                if lang == "te":
                    st.markdown(f"**తెలుగు వాక్యం:** *{q['prompt_te']}*")
                else:
                    st.markdown(f"**ಕನ್ನಡ ವಾಕ್ಯ:** *{q['prompt_kn']}*")

                st.markdown(f"**Correct German:** `{q['target_de']}`")

                tts_button(q["target_de"], f"rev_btn_{q['id']}")

                if not is_right:
                    st.markdown(f"<span style='color: #dc2626; font-weight: 600;'>Your Answer: {u_ans}</span>", unsafe_allow_html=True)

                st.markdown(f"""**Grammar Breakdown:**
{q['explanation']}
- **Case:** `{q['case']}`
- **Noun Gender:** `{q['gender']}`
- **Governing B1 Word:** `{q['b1_verb']}`""")
