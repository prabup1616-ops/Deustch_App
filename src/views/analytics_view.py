"""
Machine Learning & Learning Analytics Dashboard View.
Visualizes CEFR B1 Exam Readiness Prediction, Ebbinghaus Forgetting Curves,
and weak grammar topic breakdowns using Pandas, NumPy, and Scikit-Learn.
"""

import streamlit as st
import pandas as pd
from src.services.analytics_service import (
    predict_goethe_b1_readiness,
    calculate_ebbinghaus_spaced_repetition,
    analyze_weak_grammar_topics,
    get_learner_performance_dataframe
)


def render_analytics_view():
    pid = st.session_state.get("player_name", "gast").strip().lower().replace(" ", "_")
    st.markdown("## 📊 KI-Lernanalyse & Goethe B1 Prüfungsbereitschaft")
    st.caption("Echtzeit-Berechnung mit Machine Learning, Pandas & NumPy auf Basis Ihrer bisherigen LSRW-Prüfungsdaten.")

    tab_pred, tab_curve, tab_topics, tab_api = st.tabs([
        "🎯 B1 Readiness Predictor (ML)",
        "🧠 Ebbinghaus Forgetting Curve (NumPy)",
        "🔍 Schwachstellen-Analyse (Pandas)",
        "🚀 FastAPI Backend & Swagger Docs"
    ])

    # --------------------------------------------------------------------------
    # TAB 1: B1 READINESS PREDICTOR
    # --------------------------------------------------------------------------
    with tab_pred:
        pred = predict_goethe_b1_readiness(pid)
        score_val = pred["readiness_percentage"]
        color = "#10b981" if score_val >= 75 else "#f59e0b" if score_val >= 60 else "#ef4444"

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e293b, #0f172a); border-radius: 16px; padding: 24px; text-align: center; color: white; margin-bottom: 20px; border: 2px solid {color};">
            <h3 style="margin: 0 0 6px 0; color: #94a3b8; font-size: 1rem; text-transform: uppercase; letter-spacing: 1px;">Projizierter Goethe B1 Erfolgsindex (ML)</h3>
            <div style="font-size: 3.5rem; font-weight: 900; color: {color}; margin: 8px 0;">{score_val}%</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #f8fafc; margin-bottom: 6px;">{pred['verdict']}</div>
            <p style="margin: 0; color: #cbd5e1; font-size: 0.95rem;">{pred['recommendation']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 📋 Modul-Bereitschaft (4 Fertigkeiten):")
        c1, c2, c3, c4 = st.columns(4)
        breakdown = pred["module_breakdown"]
        with c1:
            st.metric("📖 Lesen (Reading)", f"{breakdown['reading_pct']}%", delta="Bestanden (>=60%)" if breakdown['reading_pct'] >= 60 else "Noch Üben")
        with c2:
            st.metric("✍️ Schreiben (Writing)", f"{breakdown['writing_pct']}%", delta="Bestanden (>=60%)" if breakdown['writing_pct'] >= 60 else "Noch Üben")
        with c3:
            st.metric("🎧 Hören (Listening)", f"{breakdown['listening_pct']}%", delta="Bestanden (>=60%)" if breakdown['listening_pct'] >= 60 else "Noch Üben")
        with c4:
            st.metric("🗣️ Sprechen (Speaking)", f"{breakdown['speaking_pct']}%", delta="Bestanden (>=60%)" if breakdown['speaking_pct'] >= 60 else "Noch Üben")

        st.info(f"📌 **Goethe-Zertifikat B1 Regel:** Zum Bestehen der Gesamtprüfung müssen alle 4 Module mindestens 60% erreichen. Aktueller Status: **{pred['modules_at_pass_threshold']}**.")

    # --------------------------------------------------------------------------
    # TAB 2: EBBINGHAUS FORGETTING CURVE
    # --------------------------------------------------------------------------
    with tab_curve:
        st.markdown("### 🧠 Ebbinghaus Vergessenskurve (Spaced Repetition)")
        st.caption("Berechnet die geschätzte Erinnerungswahrscheinlichkeit $R = e^{-\\Delta t / S}$ mit Vektor-Operationen in NumPy.")
        items = calculate_ebbinghaus_spaced_repetition(pid)

        if not items:
            st.info("Noch keine Grammatikthemen vorhanden. Absolvieren Sie eine LSRW-Übung, um Ihre Kurve zu visualisieren.")
        else:
            table_data = []
            for itm in items:
                table_data.append({
                    "Grammatikthema": itm["topic"],
                    "Erinnerungs-Wahrscheinlichkeit": f"{itm['retention_probability']}%",
                    "Tage seit letzter Übung": f"{itm['days_since_last_practice']} Tage",
                    "Übungsanzahl": itm["practice_count"],
                    "Durchschnittsnote": f"{itm['mean_score_pct']}%",
                    "Status": itm["status"]
                })
            st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

    # --------------------------------------------------------------------------
    # TAB 3: WEAKEST TOPICS
    # --------------------------------------------------------------------------
    with tab_topics:
        st.markdown("### 🔍 Grammatik-Schwachstellen-Analyse (Pandas GroupBy)")
        weak_data = analyze_weak_grammar_topics(pid)

        col_w, col_s = st.columns(2)
        with col_w:
            st.markdown("#### ⚠️ Themen mit höchstem Wiederholungsbedarf:")
            weak_list = weak_data.get("weakest_topics", [])
            if not weak_list:
                st.info("Noch nicht genügend Daten für Schwachstellenanalyse.")
            else:
                for w in weak_list:
                    st.warning(f"**{w['topic']}**: Durchschnitt `{w['mean_pct']}%` ({w['attempts']} Versuche)")

        with col_s:
            st.markdown("#### 🌟 Ihre stärksten Grammatikthemen:")
            strong_list = weak_data.get("strongest_topics", [])
            if not strong_list:
                st.info("Noch keine starken Themen registriert.")
            else:
                for s in strong_list:
                    st.success(f"**{s['topic']}**: Durchschnitt `{s['mean_pct']}%` ({s['attempts']} Versuche)")

    # --------------------------------------------------------------------------
    # TAB 4: FASTAPI & SWAGGER DOCS
    # --------------------------------------------------------------------------
    with tab_api:
        st.markdown("### 🚀 Integrierte FastAPI REST-Schnittstelle")
        st.markdown("""
        Dieses Projekt verfügt über eine vollwertige **FastAPI-Backend-Architektur** (`src/api/`):
        - **Swagger UI Dokumentation**: Interaktive API-Testumgebung unter `/docs`
        - **ReDoc Dokumentation**: Unter `/redoc`
        - **Pydantic V2 Schemas**: Strikte Validierung für alle Prüfungs- und Bewertungseingaben
        - **CORS Middleware**: Nahtlose Anbindung an mobile Apps und externe Clients
        """)

        st.code("""# FastAPI Server lokal starten:
python run_api.py

# Anschließend im Browser öffnen:
http://localhost:8000/docs
        """, language="bash")
