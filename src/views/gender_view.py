import time
from datetime import date
import streamlit as st
import storage
import email_service
from src.gender_questions import (
    get_daily_gender_questions,
    get_gender_pack_questions,
    get_total_gender_packs,
    GENDER_QUESTIONS_DATA
)
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
    """Safely retrieves all saved players from storage."""
    if hasattr(storage, "get_all_saved_players"):
        return storage.get_all_saved_players()
    data = storage.load_data()
    players = list(data.get("players", {}).values())
    players.sort(key=lambda p: p.get("name", "").lower())
    return players


def render_gender_view():
    """
    Renders the Gender Duel (Der, Die, Das) Arena:
    - Dedicated to German Noun Genders from official Goethe B1 Wortliste.
    - Shows German noun, plural form, and English (+ regional) meaning.
    - User types 'der', 'die', or 'das' (or uses quick-tap buttons).
    - 50-second timer per question with auto-skip on timeout.
    - Strict separate scoreboard and statistics from Pronouns.
    """
    if "gender_stage" not in st.session_state:
        st.session_state.gender_stage = "lobby"
    if "gender_q_idx" not in st.session_state:
        st.session_state.gender_q_idx = 0
    if "gender_per_q_results" not in st.session_state:
        st.session_state.gender_per_q_results = []
    if "gender_q_start_time" not in st.session_state:
        st.session_state.gender_q_start_time = time.time()
    if "gender_result" not in st.session_state:
        st.session_state.gender_result = None
    if "gender_pack_choice" not in st.session_state:
        st.session_state.gender_pack_choice = date.today().isoformat()
    if "gender_pack_title" not in st.session_state:
        st.session_state.gender_pack_title = "Today's Gender Challenge"

    # ==========================================================================
    # STAGE 1: LOBBY (Player Selection & Challenge Mode)
    # ==========================================================================
    if st.session_state.gender_stage == "lobby":
        st.markdown("""
        <div class="home-hero" style="padding: 24px 30px; background: linear-gradient(135deg, #065f46 0%, #047857 50%, #059669 100%);">
            <h1 style="font-size: 2.2rem; color: #ecfdf5;">🏷️ German Gender Duel (Der • Die • Das)</h1>
            <p style="font-size: 1.05rem; color: #a7f3d0;">
                Master German Noun Genders from the Official Goethe-Zertifikat B1 Wortliste • Plurals & English Meanings Included • 50s Per Question
            </p>
        </div>
        """, unsafe_allow_html=True)

        col_setup, col_preview = st.columns([3, 2], gap="large")

        with col_setup:
            player_info = render_dynamic_player_selector(category="gender", key_prefix="gender")
            active_player_name = player_info["player_name"]
            is_player_ready = player_info["is_ready"]
            is_new_player = player_info.get("is_new", False)
            force_unique = player_info.get("force_unique", False)
            avatar_input = player_info["avatar"]
            email_input = player_info["email"]
            player_id_input = player_info.get("selected_player_id")

            if is_player_ready and active_player_name:
                clean_pid = player_id_input or active_player_name.strip().lower().replace(" ", "_")
                player_hist = storage.get_player_continuous_history(clean_pid, category="gender")
                cur_day = player_hist["current_day_number"]
                is_today_done = player_hist["is_played_today"]

                # Continuous Journey Progress Tracker for Selected Player (Gender)
                render_player_progress_dashboard(clean_pid, active_player_name, category="gender", title_prefix="🏷️ Gender Duel (Der • Die • Das)")

                # 10-Day Milestone Topic Unlock & Community Suggestions
                render_10day_topic_unlock_card(clean_pid, active_player_name, category="gender", key_prefix="gender")
            else:
                cur_day = 1
                is_today_done = False

            st.markdown("---")
            st.markdown("### 2. 🌐 Meaning Annotations Language")
            st.caption("Each question displays the German noun, its plural form, and English translation. Choose your preferred regional language annotation:")

            lang_input = st.radio(
                "Secondary Language Annotation:",
                options=["Telugu (తెలుగు)", "Kannada (ಕನ್ನಡ)", "English Only"],
                index=0 if st.session_state.lang_choice == "te" else 1,
                key="gender_lang_choice"
            )

            st.markdown("---")
            st.markdown("### 3. 🎯 Choose Gender Quiz Set")
            total_packs = get_total_gender_packs(count=5)

            if is_today_done:
                cont_opt_label = f"🗓️ Continuous Journey: Day - {cur_day} (Played Today — Retake to improve score average)"
            else:
                cont_opt_label = f"🗓️ Continuous Journey: Day - {cur_day} Challenge (Next in Sequence)"

            mode_input = st.radio(
                "Which question set do you want to play?",
                options=[
                    cont_opt_label,
                    f"📦 Practice Packs (Pack 1 to {total_packs} from 522 Goethe B1 Nouns)"
                ],
                index=0,
                key="gender_mode_choice"
            )

            if "Continuous Journey" in mode_input:
                pack_tag = f"gender-{date.today().isoformat()}"
                pack_title = f"Gender Day - {cur_day} Challenge ({date.today().strftime('%B %d, %Y')})"
                chosen_is_continuous = True
            else:
                pack_num = st.slider(f"Select Pack Number (1 to {total_packs}):", min_value=1, max_value=total_packs, value=1, key="gender_pack_slider")
                pack_tag = f"gender-pack-{pack_num}"
                pack_title = f"Gender Pack #{pack_num} (Nouns {(pack_num-1)*5 + 1} to {min(pack_num*5, len(GENDER_QUESTIONS_DATA))})"
                chosen_is_continuous = False

            # Choose Active Topic (Pre-selected with player's current topic)
            if is_player_ready and active_player_name:
                active_topic = render_topic_selector(clean_pid, category="gender", key_prefix="gender")
            else:
                active_topic = "Goethe B1 Nouns (Baseline)"

            st.markdown("<br>", unsafe_allow_html=True)

            start_btn = st.button("🚀 START GENDER QUIZ NOW ➔", type="primary", use_container_width=True, key="gender_start_btn")
            if start_btn:
                clean_name = active_player_name.strip()
                if not is_player_ready or not clean_name:
                    st.error("⚠️ Please type or select your name above to start the Gender duel!")
                else:
                    if is_new_player:
                        saved_prof = storage.create_unique_player(clean_name, avatar_input, email_input.strip())
                    else:
                        saved_prof = storage.get_or_create_player(clean_name, avatar_input, email_input.strip())
                    canonical_name = saved_prof.get("name", clean_name)

                    st.session_state.player_name = canonical_name
                    st.session_state.player_avatar = saved_prof.get("avatar", avatar_input)
                    st.session_state.player_email = saved_prof.get("email", email_input.strip())
                    
                    if "Telugu" in lang_input:
                        st.session_state.lang_choice = "te"
                    elif "Kannada" in lang_input:
                        st.session_state.lang_choice = "kn"
                    else:
                        st.session_state.lang_choice = "en"

                    st.session_state.gender_pack_choice = pack_tag
                    st.session_state.gender_pack_title = pack_title
                    st.session_state.active_gender_topic = active_topic
                    st.session_state.gender_retake_notice = None

                    if chosen_is_continuous:
                        initial_questions = get_topic_curriculum_questions(active_topic, category="gender", count=5, day_number=cur_day)
                    else:
                        initial_questions = get_gender_pack_questions(pack_num, count=5)

                    st.session_state.gender_active_questions = initial_questions
                    st.session_state.gender_seen_q_ids = [q["id"] for q in initial_questions]

                    st.session_state.gender_q_idx = 0
                    st.session_state.gender_per_q_results = []
                    st.session_state.gender_q_start_time = time.time()
                    st.session_state.gender_result = None

                    st.session_state.gender_stage = "arena"
                    st.rerun()

        with col_preview:
            st.markdown("### 🏆 Real-Time Gender Standings")
            st.caption("This scoreboard is **completely isolated** from the Pronoun leaderboard.")
            
            today_gender_board = storage.get_daily_leaderboard(f"gender-{date.today().isoformat()}", category="gender")
            if today_gender_board:
                st.write(f"**Today's Gender Leaderboard ({len(today_gender_board)} player(s)):**")
                for rank, p in enumerate(today_gender_board[:5], start=1):
                    medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
                    st.markdown(f"""<div style="display: flex; justify-content: space-between; align-items: center; background: white; border: 1px solid #d1fae5; border-radius: 10px; padding: 10px 14px; margin-bottom: 8px;">
<div><strong>{medal} {p['avatar']} {p['name']}</strong> ({p['attempts_count']} attempts)</div>
<div style="font-weight: 700; color: #059669;">{p['average_score']:.2f} / 5.0</div>
</div>""", unsafe_allow_html=True)
            else:
                st.info("No one has taken today's Gender Challenge yet. Be the first to rank on the Gender scoreboard!")

            # 🌟 All-Time High Scores Leaderboard on the right hand side
            render_all_time_highs_sidebar(category="gender")

            # Quick Tips on Articles
            st.markdown("---")
            st.markdown("""<div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px;">
<h4 style="margin-top: 0; color: #1e3a8a;">💡 Gender Hints (Artikel-Tipps):</h4>
<ul style="font-size: 0.85rem; color: #334155; margin-bottom: 0; padding-left: 20px;">
<li><strong>der (Maskulin):</strong> -ling, -or, -us, -er (most agents), days, months, seasons.</li>
<li><strong>die (Feminin):</strong> -ung, -heit, -keit, -schaft, -tät, -tion, -ie, -e (90%).</li>
<li><strong>das (Neutrum):</strong> -chen, -lein, -ment, -tum, -um, infinitives used as nouns.</li>
</ul>
</div>""", unsafe_allow_html=True)

    # ==========================================================================
    # STAGE 2: ARENA (Strict 50s Timer per question, Type der/die/das)
    # ==========================================================================
    elif st.session_state.gender_stage == "arena":
        p_name = st.session_state.player_name
        p_avatar = st.session_state.player_avatar
        lang = st.session_state.lang_choice
        pack_tag = st.session_state.gender_pack_choice
        pack_title = st.session_state.gender_pack_title
        curr_idx = st.session_state.gender_q_idx

        if "gender_active_questions" not in st.session_state or not st.session_state.gender_active_questions:
            if "gender-pack-" in pack_tag:
                pack_idx = int(pack_tag.split("gender-pack-")[1])
                st.session_state.gender_active_questions = get_gender_pack_questions(pack_idx, count=5)
            else:
                clean_date = pack_tag.replace("gender-", "")
                st.session_state.gender_active_questions = get_daily_gender_questions(clean_date, count=5)
            st.session_state.gender_seen_q_ids = [q["id"] for q in st.session_state.gender_active_questions]

        current_q = st.session_state.gender_active_questions[curr_idx]

        # Top Bar
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #065f46 0%, #059669 100%); padding: 14px 20px; border-radius: 14px; color: white; display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <div style="font-size: 1.15rem; font-weight: 700;">
                {p_avatar} Player: <strong>{p_name}</strong> | 🏷️ {pack_title} • 📚 {st.session_state.get('active_gender_topic', 'Goethe B1 Nouns')}
            </div>
            <div style="font-size: 0.95rem; background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 20px;">
                Mode: <strong>Gender Duel (Der / Die / Das)</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.get("gender_retake_notice"):
            st.info(st.session_state.gender_retake_notice)

        st.progress((curr_idx + 1) / 5.0, text=f"Question {curr_idx + 1} of 5")

        # 50s Countdown Timer strictly per question
        render_50sec_timer(curr_idx, st.session_state.gender_q_start_time)

        # Main Question Card - Cleanly formatted without markdown indentation issues
        st.markdown(f"""<div class="question-card-anim" style="border-left: 6px solid #059669; padding: 24px; background: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); margin-bottom: 20px;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
<span style="font-weight: 800; color: #065f46; font-size: 1.15rem; letter-spacing: 0.5px;">
QUESTION {curr_idx + 1} OF 5 • GOETHE B1 WORTLISTE
</span>
<span style="color: #64748b; font-size: 0.85rem; font-weight: 600; background: #f1f5f9; padding: 4px 10px; border-radius: 999px;">
⏱️ 50 Seconds Limit
</span>
</div>
<div style="text-align: center; padding: 20px 10px; background: #f0fdf4; border-radius: 14px; border: 2px dashed #86efac; margin-bottom: 18px;">
<div style="font-size: 0.9rem; color: #166534; font-weight: 700; text-transform: uppercase; margin-bottom: 6px;">
Type the correct German Gender (der / die / das):
</div>
<div style="font-size: 2.8rem; font-weight: 900; color: #1e3a8a; letter-spacing: 1px;">
<span style="color: #94a3b8; font-weight: 400; font-size: 2.2rem;">[ ? ]</span> {current_q['noun']}
</div>
<div style="margin-top: 10px; display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
<span style="background: white; border: 1px solid #cbd5e1; padding: 4px 14px; border-radius: 20px; font-size: 0.95rem; color: #334155;">
📚 Plural: <strong>{current_q['plural']}</strong>
</span>
<span style="background: white; border: 1px solid #cbd5e1; padding: 4px 14px; border-radius: 20px; font-size: 0.95rem; color: #334155;">
🇬🇧 English: <strong>{current_q['meaning_en']}</strong>
</span>
</div>
</div>
</div>""", unsafe_allow_html=True)

        # Optional Regional Language Annotations
        if lang == "te" and current_q.get("meaning_te"):
            st.markdown(f"""<div style="background: #fdf4ff; border-left: 4px solid #c026d3; border-radius: 8px; padding: 10px 16px; margin-bottom: 14px; font-size: 0.95rem; color: #701a75;">
🇮🇳 తెలుగు అర్థం: <strong>{current_q['meaning_te']}</strong>
</div>""", unsafe_allow_html=True)
        elif lang == "kn" and current_q.get("meaning_kn"):
            st.markdown(f"""<div style="background: #fefce8; border-left: 4px solid #ca8a04; border-radius: 8px; padding: 10px 16px; margin-bottom: 14px; font-size: 0.95rem; color: #713f12;">
🇮🇳 ಕನ್ನಡ ಅರ್ಥ: <strong>{current_q['meaning_kn']}</strong>
</div>""", unsafe_allow_html=True)

        # Contextual Sentence from Wortliste
        if current_q.get("example_de"):
            st.markdown(f"""<div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 16px; margin-bottom: 16px;">
<span style="font-size: 0.8rem; font-weight: 700; color: #64748b; text-transform: uppercase;">Context Example (B1 Wortliste):</span><br>
<span style="font-size: 1.02rem; color: #1e293b; font-style: italic;">„{current_q['example_de']}“</span>
</div>""", unsafe_allow_html=True)

        # Gender Input Field (Typing der / die / das as requested)
        st.markdown("##### ✍️ Type German Gender (`der` / `die` / `das`):")
        
        typed_key = f"gender_input_{curr_idx}_{current_q['id']}"
        
        col_type, col_quick1, col_quick2, col_quick3 = st.columns([3, 1, 1, 1])
        
        with col_type:
            typed_answer = st.text_input(
                "Type Gender:",
                value="",
                placeholder="Type 'der', 'die', or 'das'...",
                key=typed_key,
                label_visibility="collapsed"
            )

        # Quick 1-tap badges for mobile/convenience
        with col_quick1:
            der_btn = st.button("🔵 der (M)", use_container_width=True, key=f"quick_der_{curr_idx}")
        with col_quick2:
            die_btn = st.button("🔴 die (F)", use_container_width=True, key=f"quick_die_{curr_idx}")
        with col_quick3:
            das_btn = st.button("🟢 das (N)", use_container_width=True, key=f"quick_das_{curr_idx}")

        final_typed = typed_answer.strip()
        if der_btn:
            final_typed = "der"
        elif die_btn:
            final_typed = "die"
        elif das_btn:
            final_typed = "das"

        col_submit, col_exit = st.columns([3, 1])
        with col_submit:
            btn_label = "✅ Lock In Gender & Next Question ➔" if curr_idx < 4 else "🚀 Submit Final Gender Quiz & See Score 🏆"
            lock_clicked = st.button(btn_label, type="primary", use_container_width=True, key=f"btn_gender_lock_{curr_idx}")
        with col_exit:
            exit_clicked = st.button("❌ Quit to Lobby", use_container_width=True, key=f"btn_gender_exit_{curr_idx}")

        if exit_clicked:
            st.session_state.gender_stage = "lobby"
            st.rerun()

        now = time.time()
        elapsed = now - st.session_state.gender_q_start_time

        # Auto-advance if 50s expired OR lock button clicked OR quick badge pressed
        if lock_clicked or der_btn or die_btn or das_btn or elapsed >= 50.0:
            is_timeout = (elapsed >= 50.0)

            if is_timeout:
                is_correct = False
                user_article = "⏰ Timed Out (>50s) - 0 Marks (Skipped)"
            else:
                user_article = final_typed.strip().lower()
                if not user_article:
                    is_correct = False
                    user_article = "No Answer Typed (0 Marks)"
                else:
                    correct_article = current_q["article"].strip().lower()
                    is_correct = (user_article == correct_article)

            st.session_state.gender_per_q_results.append({
                "question": current_q,
                "user_choice": user_article,
                "correct_article": current_q["article"],
                "is_correct": is_correct,
                "is_timeout": is_timeout,
                "elapsed": min(50.0, round(elapsed, 1))
            })

            if curr_idx < 4:
                st.session_state.gender_q_idx += 1
                st.session_state.gender_q_start_time = time.time()  # STRICT 50s RESET FOR NEXT QUESTION
                st.rerun()
            else:
                score = sum(1 for r in st.session_state.gender_per_q_results if r["is_correct"])
                player_id = p_name.lower().replace(" ", "_")

                # Store with category="gender" for STRICT SEPARATE SCOREBOARD
                stats = storage.record_attempt(
                    player_id=player_id,
                    date_str=pack_tag,
                    score=score,
                    total=5,
                    details=st.session_state.gender_per_q_results,
                    category="gender"
                )

                st.session_state.gender_result = {
                    "score": score,
                    "stats": stats,
                    "details": st.session_state.gender_per_q_results
                }
                st.session_state.gender_stage = "results"
                st.rerun()

    # ==========================================================================
    # STAGE 3: RESULTS & SEPARATE GENDER SCOREBOARD
    # ==========================================================================
    elif st.session_state.gender_stage == "results":
        res = st.session_state.gender_result
        p_name = st.session_state.player_name
        p_avatar = st.session_state.player_avatar
        pack_tag = st.session_state.gender_pack_choice
        pack_title = st.session_state.gender_pack_title

        score = res["score"]
        stats = res["stats"]

        trigger_confetti_and_sound(score, 5)

        badge_title = "🎉 AUSGEZEICHNET! (PERFECT SCORE)" if score == 5 else "👏 SEHR GUT! (GREAT JOB)" if score >= 3 else "💪 GUTER VERSUCH! (GOOD EFFORT)"

        st.markdown(f"""<div class="score-burst-card" style="background: linear-gradient(135deg, #065f46 0%, #047857 50%, #059669 100%);">
<h2 style="margin: 0; color: #fef08a; font-size: 1.6rem;">{badge_title}</h2>
<div class="score-number">{score} <span style="font-size: 2rem; color: #a7f3d0;">/ 5</span></div>
<p style="font-size: 1.25rem; font-weight: 600; margin: 4px 0 16px 0;">{p_avatar} {p_name} — 🏷️ Gender Duel</p>
<div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
<div style="background: rgba(255,255,255,0.15); padding: 8px 18px; border-radius: 12px;">
<div style="font-size: 0.85rem; color: #a7f3d0;">Normalized Gender Average</div>
<div style="font-size: 1.4rem; font-weight: 700; color: #67e8f9;">{stats['average_score']:.2f} / 5.0</div>
</div>
<div style="background: rgba(255,255,255,0.15); padding: 8px 18px; border-radius: 12px;">
<div style="font-size: 0.85rem; color: #a7f3d0;">Attempts on this Gender Set</div>
<div style="font-size: 1.4rem; font-weight: 700; color: #ecfdf5;">{stats['attempts_count']}</div>
</div>
<div style="background: rgba(255,255,255,0.15); padding: 8px 18px; border-radius: 12px;">
<div style="font-size: 0.85rem; color: #a7f3d0;">Best Gender Score</div>
<div style="font-size: 1.4rem; font-weight: 700; color: #fde047;">{stats['best_score']} / 5</div>
</div>
</div>
</div>""", unsafe_allow_html=True)

        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            if st.button("🔄 Retake Gender Quiz (Improve Average)", type="primary", use_container_width=True, key="gender_retake_btn"):
                prev_results = res.get("details", [])
                seen_ids = set(st.session_state.get("gender_seen_q_ids", []))
                retake_questions, updated_seen, wrong_cnt = build_retake_question_set(
                    prev_results,
                    GENDER_QUESTIONS_DATA,
                    seen_ids,
                    target_count=5
                )
                st.session_state.gender_active_questions = retake_questions
                st.session_state.gender_seen_q_ids = updated_seen
                st.session_state.gender_q_idx = 0
                st.session_state.gender_per_q_results = []
                st.session_state.gender_q_start_time = time.time()
                st.session_state.gender_result = None
                st.session_state.gender_stage = "arena"
                st.session_state.gender_retake_notice = f"🔄 Smart Retake Active: {wrong_cnt} incorrect noun(s) reappeared for a second chance + {5 - wrong_cnt} fresh new noun(s) added!"
                st.rerun()
        with col_b2:
            if st.button("📦 Choose Another Gender Pack", use_container_width=True, key="gender_pack_btn"):
                st.session_state.gender_stage = "lobby"
                st.rerun()
        with col_b3:
            if st.button("🏠 Back to Home Dashboard", use_container_width=True, key="gender_home_btn"):
                st.session_state.app_view = "home"
                st.session_state.gender_stage = "lobby"
                st.rerun()

        st.caption("💡 **Smart Retake Engine**: Nouns answered correctly disappear; your incorrect nouns reappear for a second chance, plus fresh new nouns are added to make 5!")

        # Continuous Journey Progress Dashboard in Results
        player_id = p_name.lower().replace(" ", "_")
        render_player_progress_dashboard(player_id, p_name, category="gender", title_prefix="🏷️ Gender Duel (Der • Die • Das)")

        # Detailed Question Review
        st.markdown("---")
        st.markdown("### 📝 Detailed Question Review")

        for idx, item in enumerate(res["details"], start=1):
            q = item["question"]
            correct_art = item["correct_article"]
            user_art = item["user_choice"]
            is_corr = item["is_correct"]
            is_tout = item.get("is_timeout", False)
            elapsed_sec = item.get("elapsed", 0.0)

            border_color = "#10b981" if is_corr else "#ef4444"
            status_badge = "✅ CORRECT (+1 Mark)" if is_corr else ("⏰ TIMEOUT (>50s) (0 Marks)" if is_tout else "❌ INCORRECT (0 Marks)")
            status_bg = "#ecfdf5" if is_corr else "#fef2f2"
            status_fg = "#047857" if is_corr else "#b91c1c"

            art_color = "#2563eb" if correct_art == "der" else "#db2777" if correct_art == "die" else "#059669"

            st.markdown(f"""<div style="border-left: 6px solid {border_color}; background: white; border-radius: 12px; padding: 18px 22px; margin-bottom: 14px; box-shadow: 0 2px 10px rgba(0,0,0,0.04);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
<div style="font-weight: 800; font-size: 1.1rem; color: #1e3a8a;">
Question {idx}: <span style="color: {art_color}; font-size: 1.3rem;">{correct_art} {q['noun']}</span>
</div>
<div style="display: flex; gap: 10px; align-items: center;">
<span style="font-size: 0.8rem; color: #64748b;">⏱️ {elapsed_sec:.1f}s / 50s</span>
<span style="background: {status_bg}; color: {status_fg}; font-weight: 700; font-size: 0.82rem; padding: 4px 12px; border-radius: 999px;">
{status_badge}
</span>
</div>
</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; font-size: 0.92rem;">
<div><strong>Your Answer:</strong> <span style="font-weight: 700; color: {'#15803d' if is_corr else '#dc2626'};">{user_art}</span></div>
<div><strong>Correct Gender:</strong> <span style="font-weight: 800; color: {art_color};">{correct_art}</span></div>
<div><strong>Plural Form:</strong> <span style="font-weight: 700; color: #0284c7;">{q['plural']}</span></div>
<div><strong>English Meaning:</strong> <span style="font-weight: 700; color: #1e293b;">{q['meaning_en']}</span></div>
</div>
<div style="background: #f8fafc; border-radius: 8px; padding: 10px 14px; font-size: 0.9rem; color: #475569;">
💬 <strong>Goethe B1 Example:</strong> <em>„{q.get('example_de', '')}“</em>
</div>
</div>""", unsafe_allow_html=True)

        # SEPARATE GENDER LEADERBOARD
        st.markdown("---")
        st.markdown("### 🏆 Dedicated Gender Leaderboard")
        st.caption("Tracking all registered players on this Gender Challenge set:")

        gender_board = storage.get_daily_leaderboard(pack_tag, category="gender")
        if gender_board:
            for rank, p in enumerate(gender_board, start=1):
                medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
                is_active = (p["player_id"] == p_name.lower().replace(" ", "_"))
                bg_color = "#f0fdf4" if is_active else "white"
                border_style = "2px solid #86efac" if is_active else "1fr solid #e2e8f0"

                st.markdown(f"""<div style="display: flex; justify-content: space-between; align-items: center; background: {bg_color}; border: {border_style}; border-radius: 10px; padding: 12px 18px; margin-bottom: 8px;">
<div style="display: flex; align-items: center; gap: 12px;">
<span style="font-size: 1.3rem;">{medal}</span>
<span style="font-size: 1.5rem;">{p['avatar']}</span>
<div>
<div style="font-weight: 800; color: #065f46; font-size: 1.05rem;">
{p['name']} {'(You)' if is_active else ''}
</div>
<div style="font-size: 0.8rem; color: #64748b;">
Attempts: <strong>{p['attempts_count']}</strong> • Best: <strong>{p['best_score']} / 5</strong>
</div>
</div>
</div>
<div style="text-align: right;">
<div style="font-size: 1.35rem; font-weight: 800; color: #059669;">
{p['average_score']:.2f} <span style="font-size: 0.85rem; color: #64748b;">/ 5.0</span>
</div>
<div style="font-size: 0.75rem; color: #64748b;">Normalized Average</div>
</div>
</div>""", unsafe_allow_html=True)
        else:
            st.info("No leaderboard data yet for this set.")
