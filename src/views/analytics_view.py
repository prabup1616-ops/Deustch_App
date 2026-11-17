"""
Learning Analytics & Goethe B1 Exam Readiness View.
Presents learner performance, memory retention schedules,
and grammar skill breakdowns in clean, student-facing English.
"""

import streamlit as st
import pandas as pd
from src.services.analytics_service import (
    predict_goethe_b1_readiness,
    calculate_ebbinghaus_spaced_repetition,
    analyze_weak_grammar_topics
)


def render_analytics_view():
    pid = st.session_state.get("player_name", "gast").strip().lower().replace(" ", "_")
    st.markdown("## 📊 Learning Progress & Goethe B1 Exam Readiness")
    st.caption("Personalized performance analytics, spaced repetition memory tracking, and exam pass readiness.")

    tab_pred, tab_curve, tab_topics = st.tabs([
        "🎯 Exam Readiness Predictor",
        "🧠 Memory Retention Schedule",
        "🔍 Grammar Strengths & Weaknesses"
    ])

    # --------------------------------------------------------------------------
    # TAB 1: B1 READINESS PREDICTOR
    # --------------------------------------------------------------------------
    with tab_pred:
        pred = predict_goethe_b1_readiness(pid)
        score_val = pred["readiness_percentage"]
        color = "#10b981" if score_val >= 75 else "#f59e0b" if score_val >= 60 else "#ef4444"

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e293b, #0f172a); border-radius: 16px; padding: 26px; text-align: center; color: white; margin-bottom: 20px; border: 2px solid {color};">
            <h3 style="margin: 0 0 6px 0; color: #94a3b8; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1px;">Projected Goethe B1 Exam Readiness</h3>
            <div style="font-size: 3.8rem; font-weight: 900; color: {color}; margin: 8px 0;">{score_val}%</div>
            <div style="font-size: 1.2rem; font-weight: 700; color: #f8fafc; margin-bottom: 6px;">{pred['verdict']}</div>
            <p style="margin: 0; color: #cbd5e1; font-size: 0.95rem; max-width: 600px; margin: 0 auto;">{pred['recommendation']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 📋 Skill Breakdown (4 Goethe B1 Competencies):")
        c1, c2, c3, c4 = st.columns(4)
        breakdown = pred["module_breakdown"]
        with c1:
            st.metric("📖 Reading (Lesen)", f"{breakdown['reading_pct']}%", delta="Passing (>=60%)" if breakdown['reading_pct'] >= 60 else "Needs Practice")
        with c2:
            st.metric("✍️ Writing (Schreiben)", f"{breakdown['writing_pct']}%", delta="Passing (>=60%)" if breakdown['writing_pct'] >= 60 else "Needs Practice")
        with c3:
            st.metric("🎧 Listening (Hören)", f"{breakdown['listening_pct']}%", delta="Passing (>=60%)" if breakdown['listening_pct'] >= 60 else "Needs Practice")
        with c4:
            st.metric("🗣️ Speaking (Sprechen)", f"{breakdown['speaking_pct']}%", delta="Passing (>=60%)" if breakdown['speaking_pct'] >= 60 else "Needs Practice")

        st.info(f"📌 **Official Goethe-Zertifikat B1 Requirement:** To pass the overall exam, a candidate must score at least **60% in each individual module**. Your current status: **{pred['modules_at_pass_threshold']}**.")

    # --------------------------------------------------------------------------
    # TAB 2: MEMORY RETENTION SCHEDULE (SPACED REPETITION)
    # --------------------------------------------------------------------------
    with tab_curve:
        st.markdown("### 🧠 Spaced Repetition & Memory Retention Forecast")
        st.caption("Calculates your estimated memory retention per topic over time to ensure you review grammar before forgetting.")
        items = calculate_ebbinghaus_spaced_repetition(pid)

        if not items:
            st.info("No grammar practice recorded yet. Complete any LSRW exercise to view your memory retention schedule.")
        else:
            table_data = []
            for itm in items:
                table_data.append({
                    "Grammar Topic": itm["topic"],
                    "Estimated Retention": f"{itm['retention_probability']}%",
                    "Days Since Last Practice": f"{itm['days_since_last_practice']} days ago",
                    "Times Practiced": f"{itm['practice_count']} sessions",
                    "Average Score": f"{itm['mean_score_pct']}%",
                    "Review Status": itm["status"]
                })
            st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

    # --------------------------------------------------------------------------
    # TAB 3: GRAMMAR STRENGTHS & WEAKNESSES
    # --------------------------------------------------------------------------
    with tab_topics:
        st.markdown("### 🔍 Grammar Strengths & Weaknesses Analysis")
        st.caption("Detailed breakdown of your topics ranked by consistency and average score.")
        weak_data = analyze_weak_grammar_topics(pid)

        col_w, col_s = st.columns(2, gap="medium")
        with col_w:
            st.markdown("#### ⚠️ Topics Needing Review Most:")
            weak_list = weak_data.get("weakest_topics", [])
            if not weak_list:
                st.info("Complete more exercises across different topics to generate recommendations.")
            else:
                for w in weak_list:
                    st.warning(f"**{w['topic']}** — Average Score: `{w['mean_pct']}%` ({w['attempts']} attempts)")

        with col_s:
            st.markdown("#### 🌟 Your Strongest Grammar Topics:")
            strong_list = weak_data.get("strongest_topics", [])
            if not strong_list:
                st.info("No mastered topics recorded yet.")
            else:
                for s in strong_list:
                    st.success(f"**{s['topic']}** — Average Score: `{s['mean_pct']}%` ({s['attempts']} attempts)")
