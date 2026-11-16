"""
LSRW Module — Goethe-Zertifikat B1 Meisterstudio.
Reihenfolge: Lesen (Reading) → Schreiben (Writing) → Hören (Listening) → Sprechen (Speaking)
100% DEUTSCH (Ausschließlich deutsche Sprache, keine anderen Sprachen).
"""
import time
import json
import streamlit as st
import streamlit.components.v1 as components
import storage
from src.components import render_phrase_loader, dismiss_phrase_loader
from src.ai_service import (
    generate_reading_exercise,
    generate_writing_prompt,
    evaluate_writing_submission,
    generate_listening_exercise,
    generate_real_listening_exam,
    generate_speaking_cards,
    evaluate_speaking_response,
    generate_topic_explanation,
)

PRESET_TOPICS = [
    "Präpositionen (Wechselpräpositionen)",
    "Relativsatz",
    "Passiv",
    "Konjunktiv II",
    "Perfekt vs Präteritum",
    "weil / obwohl / damit",
    "Adjektivdeklination",
    "Infinitiv mit zu",
    "wenn vs als",
    "Verben mit Dativ",
    "Verben mit Akkusativ",
    "Nebensatz (dass, ob, weil)",
    "Komparativ und Superlativ",
    "Reflexive Verben",
    "Possessivartikel",
]


def _get_active_player_id():
    name = st.session_state.get("player_name", "gast")
    return name.lower().replace(" ", "_") if name else "gast"


# ==============================================================================
# HAUPTEINSTIEG (MAIN ROUTER)
# ==============================================================================

def render_lsrw_view():
    """LSRW Hauptnavigation: Übersicht (Hub) oder aktives Modul."""
    qp_mod = st.query_params.get("mod", "hub") or "hub"
    if st.session_state.get("lsrw_module") != qp_mod and qp_mod in ("hub", "learning", "reading", "writing", "listening", "speaking"):
        st.session_state.lsrw_module = qp_mod

    # URL-Parameter zur Beibehaltung nach Aktualisierung (F5 Refresh / History)
    st.query_params["view"] = "lsrw"
    st.query_params["mod"] = st.session_state.lsrw_module

    # Header komplett auf Deutsch
    st.markdown("""<div class="home-hero" style="padding: 20px 30px; background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #0284c7 100%);">
<h1 style="font-size: 2rem; color: #fff; margin-bottom: 4px;">🎧🗣️📖✍️ Goethe B1 LSRW Meisterstudio</h1>
<p style="font-size: 1rem; color: #bae6fd; margin: 0;">Lesen • Schreiben • Hören • Sprechen — Kumulatives Prüfungstraining (100% Deutsch)</p>
</div>""", unsafe_allow_html=True)

    # Zurück zur Übersicht
    if st.session_state.lsrw_module != "hub":
        if st.button("⬅️ Zurück zur LSRW-Übersicht", key="btn_back_hub"):
            st.session_state.lsrw_module = "hub"
            st.query_params["mod"] = "hub"
            st.rerun()

    module = st.session_state.lsrw_module
    if module == "learning":
        _render_learning_module()
    elif module == "reading":
        _render_reading_module()
    elif module == "writing":
        _render_writing_module()
    elif module == "listening":
        _render_listening_module()
    elif module == "speaking":
        _render_speaking_module()
    else:
        _render_hub()


# ==============================================================================
# LSRW ÜBERSICHT (HUB)
# ==============================================================================

def _render_hub():
    pid = _get_active_player_id()
    api_key = storage.get_gemini_api_key()

    if not api_key:
        st.warning("⚠️ Bitte geben Sie Ihren kostenlosen Google AI Studio API-Schlüssel ein:")
        new_key = st.text_input("Gemini API-Schlüssel:", type="password", key="lsrw_hub_key")
        if st.button("Schlüssel speichern", key="btn_hub_save_key"):
            storage.save_gemini_api_key(new_key.strip())
            st.rerun()
        return

    # Kumulative Grammatikthemen
    st.markdown("### 📚 Ihre gelernten Grammatikthemen (Kumulativ)")
    st.caption("Themen sammeln sich an: Neue Übungen enthalten automatisch ALLE zuvor gelernten Themen.")

    learned = storage.get_learned_topics(pid)
    topic_names = [t["topic"] for t in learned]

    if topic_names:
        cols_per_row = 4
        rows = [topic_names[i:i + cols_per_row] for i in range(0, len(topic_names), cols_per_row)]
        for row_topics in rows:
            cols = st.columns(cols_per_row)
            for i, t in enumerate(row_topics):
                with cols[i]:
                    st.markdown(f"""<div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 10px; padding: 8px 12px; text-align: center; font-weight: 700; color: #1e40af; font-size: 0.9rem;">
✅ {t}
</div>""", unsafe_allow_html=True)
    else:
        st.info("Noch keine Themen hinzugefügt. Wählen Sie unten Ihr erstes Grammatikthema aus!")

    col_add1, col_add2 = st.columns([2, 1])
    with col_add1:
        new_topic = st.selectbox(
            "Neues Thema hinzufügen:",
            options=[""] + [t for t in PRESET_TOPICS if t not in topic_names] + ["✏️ Eigenes Thema eingeben..."],
            key="lsrw_add_topic_select"
        )
    with col_add2:
        if new_topic == "✏️ Eigenes Thema eingeben...":
            custom = st.text_input("Themenname:", key="lsrw_custom_topic")
            if st.button("Hinzufügen", key="btn_add_custom") and custom.strip():
                storage.add_learned_topic(pid, custom.strip())
                st.session_state.pop("lsrw_reading_data", None)
                st.session_state.pop("lsrw_writing_data", None)
                st.session_state.pop("lsrw_listening_data", None)
                st.session_state.pop("lsrw_real_data", None)
                st.session_state.pop("lsrw_speaking_cards", None)
                st.rerun()
        elif new_topic:
            if st.button(f"➕ '{new_topic}' aktivieren", key="btn_add_preset"):
                storage.add_learned_topic(pid, new_topic)
                st.session_state.pop("lsrw_reading_data", None)
                st.session_state.pop("lsrw_writing_data", None)
                st.session_state.pop("lsrw_listening_data", None)
                st.session_state.pop("lsrw_real_data", None)
                st.session_state.pop("lsrw_speaking_cards", None)
                st.rerun()

    if not topic_names:
        st.warning("⚠️ Bitte aktivieren Sie mindestens ein Grammatikthema oben, um zu beginnen.")
        return

    # Letzte Prüfungsergebnisse
    history = storage.get_lsrw_module_history(pid)
    if history:
        st.markdown("---")
        st.markdown("### 📊 Letzte Prüfungsergebnisse")
        recent = history[-6:]
        for s in reversed(recent):
            emoji = "📖" if s["module"] == "reading" else "✍️" if s["module"] == "writing" else "🎧" if s["module"] == "listening" else "🗣️"
            mod_title = "Lesen" if s["module"] == "reading" else "Schreiben" if s["module"] == "writing" else "Hören" if s["module"] == "listening" else "Sprechen"
            st.markdown(f"""<div style="display: flex; justify-content: space-between; align-items: center; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 8px 14px; margin-bottom: 6px; font-size: 0.88rem;">
<span>{emoji} <strong>{mod_title}</strong> — {', '.join(s.get('topics', []))}</span>
<span style="font-weight: 700; color: #059669;">{s['score']} / {s['total']} Punkte</span>
</div>""", unsafe_allow_html=True)

    # 5 Übungsmodule (Lernen + LSRW)
    st.markdown("---")
    st.markdown("### 🎯 Prüfungsmodule & Lernstudio")
    st.caption(f"Die Übungen testen alle Ihre {len(topic_names)} aktiven Themen: {', '.join(topic_names)}")

    # 1. Feature-Card: Lernen (Grammatikstudio auf Telugu & Kannada)
    st.markdown("""<div class="module-card unlocked" style="border-top: 4px solid #8b5cf6; background: linear-gradient(135deg, #faf5ff 0%, #ede9fe 100%); margin-bottom: 16px;">
<div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;">
<div style="display: flex; align-items: center; gap: 14px;">
<span style="font-size: 2.8rem;">🧠</span>
<div>
<h3 style="margin: 0 0 4px 0; color: #5b21b6;">Lernen (Grammatik-Lernstudio — Telugu & Kannada)</h3>
<p style="font-size: 0.92rem; color: #4c1d95; margin: 0;">
వ్యాకరణం నేర్చుకోండి (Overview / In-Detail) • ವ್ಯಾಕರಣ ಕಲಿಯಿರಿ — తెలుగు & ಕನ್ನಡ వివరణలు, ఉదాహరణలతో పాటు నేరుగా LSRW శిక్షణ లూప్!
</p>
</div>
</div>
</div>
</div>""", unsafe_allow_html=True)
    if st.button("🧠 Grammatikthema lernen & LSRW-Schleife starten ➔", type="primary", use_container_width=True, key="btn_start_learning"):
        st.session_state.lsrw_module = "learning"
        st.query_params["mod"] = "learning"
        st.session_state.pop("learn_active_topic", None)
        st.session_state.pop("learn_depth", None)
        st.session_state.pop("learn_explanation_text", None)
        st.rerun()

    col_r, col_w = st.columns(2, gap="medium")
    with col_r:
        st.markdown("""<div class="module-card unlocked" style="border-top: 4px solid #2563eb;">
<div>
<span style="font-size: 2.2rem;">📖</span>
<h3 style="margin: 8px 0 4px 0; color: #1e40af;">Lesen (Leseverstehen)</h3>
<p style="font-size: 0.88rem; color: #475569; margin: 0;">2 Lesetexte + 10 Lückenaufgaben + 10 Multiple-Choice-Verständnisfragen.</p>
</div>
</div>""", unsafe_allow_html=True)
        if st.button("📖 Leseverstehen starten ➔", type="primary", use_container_width=True, key="btn_start_reading"):
            st.session_state.lsrw_module = "reading"
            st.query_params["mod"] = "reading"
            st.session_state.pop("lsrw_reading_data", None)
            st.rerun()

    with col_w:
        st.markdown("""<div class="module-card unlocked" style="border-top: 4px solid #059669;">
<div>
<span style="font-size: 2.2rem;">✍️</span>
<h3 style="margin: 8px 0 4px 0; color: #065f46;">Schreiben (Schriftlicher Ausdruck)</h3>
<p style="font-size: 0.88rem; color: #475569; margin: 0;">E-Mail oder Forumsbeitrag nach Goethe-Kriterien mit automatischer KI-Korrektur.</p>
</div>
</div>""", unsafe_allow_html=True)
        if st.button("✍️ Schriftlichen Ausdruck starten ➔", type="primary", use_container_width=True, key="btn_start_writing"):
            st.session_state.lsrw_module = "writing"
            st.query_params["mod"] = "writing"
            st.session_state.pop("lsrw_writing_data", None)
            st.rerun()

    col_l, col_s = st.columns(2, gap="medium")
    with col_l:
        st.markdown("""<div class="module-card unlocked" style="border-top: 4px solid #d97706;">
<div>
<span style="font-size: 2.2rem;">🎧</span>
<h3 style="margin: 8px 0 4px 0; color: #92400e;">Hören (Hörverstehen)</h3>
<p style="font-size: 0.88rem; color: #475569; margin: 0;">Reines Audio (Blind-Modus). Wählen Sie zwischen Einzelsätzen (Einfach) oder echtem Goethe-Prüfungstext (max. 2x hören, 10 Fragen).</p>
</div>
</div>""", unsafe_allow_html=True)
        if st.button("🎧 Hörverstehen starten ➔", type="primary", use_container_width=True, key="btn_start_listening"):
            st.session_state.lsrw_module = "listening"
            st.query_params["mod"] = "listening"
            st.session_state.pop("lsrw_listening_data", None)
            st.rerun()

    with col_s:
        st.markdown("""<div class="module-card unlocked" style="border-top: 4px solid #7c3aed;">
<div>
<span style="font-size: 2.2rem;">🗣️</span>
<h3 style="margin: 8px 0 4px 0; color: #5b21b6;">Sprechen (Mündlicher Ausdruck)</h3>
<p style="font-size: 0.88rem; color: #475569; margin: 0;">Solitär-Karten aufdecken und spontan auf Deutsch ins Mikrofon sprechen (kein Text, nur Sprache).</p>
</div>
</div>""", unsafe_allow_html=True)
        if st.button("🗣️ Mündlichen Ausdruck starten ➔", type="primary", use_container_width=True, key="btn_start_speaking"):
            st.session_state.lsrw_module = "speaking"
            st.query_params["mod"] = "speaking"
            st.session_state.pop("lsrw_speaking_cards", None)
            st.rerun()


# ==============================================================================
# LERNSCHLEIFE CONTROLLER (LSRW LOOP BANNER)
# ==============================================================================

def _render_loop_navigation_banner(current_module: str):
    """
    Renders an interactive loop navigation banner if an LSRW learning loop is active.
    Supports Scenario 1, Scenario 2, and Scenario 3 (New Topic).
    """
    loop_topic = st.session_state.get("lsrw_loop_topic")
    if not loop_topic:
        return

    queue = st.session_state.get("lsrw_loop_queue", [])
    module_names = {
        "learning": "🧠 Lernen (Learning)",
        "reading": "📖 Lesen (Reading)",
        "writing": "✍️ Schreiben (Writing)",
        "listening": "🎧 Hören (Listening)",
        "speaking": "🗣️ Sprechen (Speaking)"
    }
    curr_label = module_names.get(current_module, current_module.title())

    st.markdown(f"""<div style="background: linear-gradient(135deg, #fdf4ff 0%, #fae8ff 100%);
border: 2px solid #d946ef; border-radius: 12px; padding: 12px 18px; margin: 10px 0 16px 0;">
<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
<div>
<div style="font-weight: 800; color: #86198f; font-size: 0.95rem;">
🔄 Aktive LSRW-Lernschleife: <strong>{loop_topic}</strong>
</div>
<div style="font-size: 0.82rem; color: #701a75; margin-top: 2px;">
Aktuelles Modul: <strong>{curr_label}</strong> | Verbleibend in Schleife: {len(queue)} Module
</div>
</div>
</div>
</div>""", unsafe_allow_html=True)

    col_next, col_new = st.columns([2, 1], gap="small")
    with col_next:
        if queue:
            next_mod = queue[0]
            next_name = module_names.get(next_mod, next_mod.title())
            if st.button(f"➔ Nächstes Modul in der Schleife: {next_name} ➔", type="primary", use_container_width=True, key=f"btn_loop_next_{current_module}"):
                st.session_state.lsrw_loop_queue.pop(0)
                st.session_state.lsrw_module = next_mod
                st.query_params["mod"] = next_mod
                if next_mod == "reading":
                    st.session_state.lsrw_current_reading_topic = loop_topic
                    st.session_state.pop("lsrw_reading_data", None)
                    st.session_state.pop("lsrw_reading_submitted", None)
                elif next_mod == "writing":
                    st.session_state.lsrw_current_writing_topic = loop_topic
                    st.session_state.pop("lsrw_writing_data", None)
                    st.session_state.pop("lsrw_writing_evaluated", None)
                elif next_mod == "listening":
                    st.session_state.lsrw_current_listening_topic = loop_topic
                    st.session_state.pop("lsrw_listening_data", None)
                    st.session_state.pop("lsrw_real_data", None)
                    st.session_state.pop("lsrw_listening_submitted", None)
                    st.session_state.pop("lsrw_real_submitted", None)
                elif next_mod == "speaking":
                    st.session_state.lsrw_current_speaking_topic = loop_topic
                    st.session_state.pop("lsrw_speaking_cards", None)
                    st.session_state.pop("lsrw_speaking_revealed", None)
                    st.session_state.pop("lsrw_speaking_evaluated", None)
                st.rerun()
        else:
            if st.button("🎉 Alle 4 Module abgeschlossen! Zurück zum Lernen ➔", type="primary", use_container_width=True, key=f"btn_loop_done_{current_module}"):
                st.session_state.lsrw_loop_queue = []
                st.session_state.lsrw_loop_topic = None
                st.session_state.lsrw_module = "learning"
                st.query_params["mod"] = "learning"
                st.rerun()

    with col_new:
        if st.button("➕ Neues Thema (కొత్త అంశం / ಹೊಸ ವಿಷಯ)", use_container_width=True, key=f"btn_loop_new_{current_module}"):
            st.session_state.lsrw_loop_queue = []
            st.session_state.lsrw_loop_topic = None
            st.session_state.pop("learn_active_topic", None)
            st.session_state.pop("learn_depth", None)
            st.session_state.pop("learn_explanation_text", None)
            st.session_state.lsrw_module = "learning"
            st.query_params["mod"] = "learning"
            st.rerun()


# ==============================================================================
# MODUL 0: LERNEN (LEARNING) — Zweisprachiges Grammatikstudio (Telugu & Kannada)
# ==============================================================================

def _render_learning_module():
    pid = _get_active_player_id()
    api_key = storage.get_gemini_api_key()

    st.markdown("""<div style="background: linear-gradient(135deg, #4c1d95 0%, #6d28d9 50%, #8b5cf6 100%);
border-radius: 16px; padding: 22px 28px; color: white; margin-bottom: 20px; box-shadow: 0 10px 25px rgba(109,40,217,0.25);">
<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 6px;">
<span style="font-size: 2.2rem;">🧠</span>
<h2 style="margin: 0; color: #f5f3ff;">Lernen: Grammatik-Lernstudio (Telugu & Kannada)</h2>
</div>
<p style="margin: 0; color: #ddd6fe; font-size: 1rem;">
వ్యాకరణ అంశాన్ని తెలుగు & కన్నడలలో నేర్చుకోండి • ವ್ಯಾಕರಣ ವಿಷಯವನ್ನು ತೆಲುಗು & ಕನ್ನಡದಲ್ಲಿ ಕಲಿಯಿರಿ
</p>
</div>""", unsafe_allow_html=True)

    learned_list = [t["topic"] for t in storage.get_learned_topics(pid)]
    available_topics = []
    for t in learned_list:
        if t not in available_topics:
            available_topics.append(t)
    for t in PRESET_TOPICS:
        if t not in available_topics:
            available_topics.append(t)

    chosen_topic = st.session_state.get("learn_active_topic")
    chosen_depth = st.session_state.get("learn_depth")

    # STEP 1: Topic Selection
    if not chosen_topic:
        st.markdown("### 📌 1. వ్యాకరణ అంశాన్ని ఎంచుకోండి / ವ್ಯಾಕರಣ ವಿಷಯವನ್ನು ಆಯ್ಕೆಮಾಡಿ")
        st.caption("డ్రాప్‌డౌన్ నుండి ఎంచుకోండి లేదా మీ సొంత అంశాన్ని టైప్ చేయండి / ಡ್ರಾಪ್‌ಡೌನ್‌ನಿಂದ ಆಯ್ಕೆಮಾಡಿ ಅಥವಾ ನಿಮ್ಮ ಸ್ವಂತ ವಿಷಯವನ್ನು ಟೈಪ್ ಮಾಡಿ:")

        col_sel, col_custom = st.columns([1, 1], gap="medium")
        with col_sel:
            preset_choice = st.selectbox(
                "ప్రసిద్ధ Goethe B1 అంశాలు / ಜನಪ್ರಿಯ Goethe B1 ವಿಷಯಗಳು:",
                options=["-- ఎంచుకోండి / ಆಯ್ಕೆಮಾಡಿ --"] + available_topics,
                key="learn_preset_select"
            )
        with col_custom:
            custom_choice = st.text_input(
                "లేదా సొంత అంశం టైప్ చేయండి / ಅಥವಾ ಸ್ವಂತ ವಿಷಯ ಟೈಪ್ ಮಾಡಿ:",
                placeholder="ఉదా: Verben mit Präpositionen, Relativsatz, Passiv...",
                key="learn_custom_input"
            )

        col_btn, _ = st.columns([1, 1])
        with col_btn:
            if st.button("ఈ అంశాన్ని ఎంచుకోండి / ಈ ವಿಷಯವನ್ನು ಆಯ್ಕೆಮಾಡಿ ➔", type="primary", use_container_width=True, key="btn_confirm_learn_topic"):
                target_topic = custom_choice.strip() if custom_choice.strip() else (preset_choice if preset_choice != "-- ఎంచుకోండి / ಆಯ್ಕೆಮಾಡಿ --" else "")
                if not target_topic:
                    st.warning("దయచేసి ఒక అంశాన్ని ఎంచుకోండి లేదా టైప్ చేయండి! / ದಯವಿಟ್ಟು ಒಂದು ವಿಷಯವನ್ನು ಆಯ್ಕೆಮಾಡಿ ಅಥವಾ ಟೈಪ್ ಮಾಡಿ!")
                else:
                    st.session_state.learn_active_topic = target_topic
                    st.session_state.pop("learn_depth", None)
                    st.session_state.pop("learn_explanation_text", None)
                    st.rerun()
        return

    # STEP 2: Depth Selection (Overview vs In-Detail)
    if not chosen_depth:
        st.markdown(f"""<div style="background: #eff6ff; border: 2px solid #3b82f6; border-radius: 12px; padding: 14px 20px; margin-bottom: 16px;">
<div style="font-size: 1.1rem; font-weight: 800; color: #1e40af;">
📌 ఎంచుకున్న అంశం / ಆಯ್ಕೆಮಾಡಿದ ವಿಷಯ: <span style="color: #2563eb;">{chosen_topic}</span>
</div>
<div style="font-size: 0.88rem; color: #475569; margin-top: 4px;">
దయచేసి వివరణ రకాన్ని ఎంచుకోండి / ದಯವಿಟ್ಟು ವಿವರಣೆಯ ಪ್ರಕಾರವನ್ನು ಆಯ್ಕೆಮಾಡಿ:
</div>
</div>""", unsafe_allow_html=True)

        col_ov, col_det = st.columns(2, gap="medium")
        with col_ov:
            st.markdown("""<div style="background: #f0fdf4; border: 2px solid #22c55e; border-radius: 12px; padding: 16px; min-height: 110px;">
<h4 style="margin: 0 0 6px 0; color: #15803d;">⚡ Overview (సమీక్ష / అవలోకన)</h4>
<p style="margin: 0; font-size: 0.88rem; color: #166534;">
సంక్షిప్త మరియు కీలక నియమం, 3-4 ముఖ్యమైన Goethe B1 ఉదాహరణలు, పరీక్ష చిట్కా.
ಸಂಕ್ಷಿಪ್ತ ಮತ್ತು ಪ್ರಮುಖ ನಿಯಮ, 3-4 ಮುಖ್ಯ Goethe B1 ಉದಾಹರಣೆಗಳು, ಪರೀಕ್ಷಾ ಸಲಹೆ.
</p>
</div>""", unsafe_allow_html=True)
            if st.button("⚡ Overview (సమీక్ష / అవలోకన) ఎంచుకోండి", type="primary", use_container_width=True, key="btn_choose_overview"):
                st.session_state.learn_depth = "overview"
                st.session_state.pop("learn_explanation_text", None)
                st.rerun()

        with col_det:
            st.markdown("""<div style="background: #fdf4ff; border: 2px solid #c026d3; border-radius: 12px; padding: 16px; min-height: 110px;">
<h4 style="margin: 0 0 6px 0; color: #86198f;">📚 In-Detail (వివరణాత్మక / ವಿವರವಾದ)</h4>
<p style="margin: 0; font-size: 0.88rem; color: #701a75;">
పూర్తి విశ్లేషణ, నియమాలు, మినహాయింపులు, వాక్య నిర్మాణం, 6+ రిజిస్టర్ ఉదాహరణలు, తప్పుల నివారణ.
ಪೂರ್ಣ ವಿಶ್ಲೇಷಣೆ, ನಿಯಮಗಳು, ಅಪವಾದಗಳು, ವಾಕ್ಯ ರಚನೆ, 6+ ರಿಜಿಸ್ಟರ್ ಉದಾಹರಣೆಗಳು, ತಪ್ಪುಗಳ ತಡೆಗಟ್ಟುವಿಕೆ.
</p>
</div>""", unsafe_allow_html=True)
            if st.button("📚 In-Detail (వివరణాత్మక / ವಿವರವಾದ) ఎంచుకోండి", type="primary", use_container_width=True, key="btn_choose_indetail"):
                st.session_state.learn_depth = "indetail"
                st.session_state.pop("learn_explanation_text", None)
                st.rerun()

        st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
        if st.button("⬅️ మరొక అంశాన్ని ఎంచుకోండి / ಮತ್ತೊಂದು ವಿಷಯವನ್ನು ಆಯ್ಕೆಮಾಡಿ (Thema wechseln)", key="btn_back_to_topics"):
            st.session_state.pop("learn_active_topic", None)
            st.session_state.pop("learn_depth", None)
            st.session_state.pop("learn_explanation_text", None)
            st.rerun()
        return

    # STEP 3: Explanation Rendering
    if not st.session_state.get("learn_explanation_text"):
        render_phrase_loader(f"🧠 Erstelle zweisprachige Grammatikerklärung ({chosen_depth.upper()}) zu '{chosen_topic}'...")
        try:
            exp_text = generate_topic_explanation(api_key, chosen_topic, depth=chosen_depth)
            st.session_state.learn_explanation_text = exp_text
            # Automatically add to cumulative learned topics
            storage.add_learned_topic(pid, chosen_topic)
            st.rerun()
        except Exception as e:
            st.error(f"Fehler bei der Erklärungserstellung: {e}")
            return

    dismiss_phrase_loader()

    # Header badge with options to switch depth or pick new topic
    col_t_info, col_t_ctrl = st.columns([3, 2])
    with col_t_info:
        depth_label = "⚡ Overview (సమీక్ష / అవలోకన)" if chosen_depth == "overview" else "📚 In-Detail (వివరణాత్మక / ವಿವರವಾದ)"
        st.markdown(f"""<div style="font-size: 1.15rem; font-weight: 800; color: #1e3a8a; margin-bottom: 6px;">
📖 Thema: <span style="color: #2563eb;">{chosen_topic}</span> ({depth_label})
</div>""", unsafe_allow_html=True)
    with col_t_ctrl:
        c1, c2 = st.columns(2)
        with c1:
            other_depth = "indetail" if chosen_depth == "overview" else "overview"
            other_label = "📚 In-Detail" if chosen_depth == "overview" else "⚡ Overview"
            if st.button(f"Wechsel zu {other_label}", key="btn_toggle_depth", use_container_width=True):
                st.session_state.learn_depth = other_depth
                st.session_state.pop("learn_explanation_text", None)
                st.rerun()
        with c2:
            if st.button("➕ Neues Thema", key="btn_learn_new_topic_top", use_container_width=True):
                st.session_state.pop("learn_active_topic", None)
                st.session_state.pop("learn_depth", None)
                st.session_state.pop("learn_explanation_text", None)
                st.rerun()

    # The actual explanation card
    st.markdown(f"""<div style="background: white; border: 2px solid #e2e8f0; border-radius: 16px; padding: 24px 28px; margin: 12px 0 20px 0; box-shadow: 0 4px 16px rgba(0,0,0,0.04);">
{st.session_state.learn_explanation_text}
</div>""", unsafe_allow_html=True)

    # STEP 4: Post-Explanation Action Links & Looping Flow
    st.markdown("---")
    st.markdown("""<div style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
border: 2px solid #22c55e; border-radius: 14px; padding: 18px 24px; margin-bottom: 16px;">
<h3 style="margin: 0 0 6px 0; color: #166534;">🎯 Goethe B1 LSRW శిక్షణ ప్రారంభించండి / Goethe B1 LSRW ತರಬೇತಿ ಪ್ರಾರಂಭಿಸಿ</h3>
<p style="margin: 0; font-size: 0.95rem; color: #15803d;">
ఈ అంశంపై మీ ప్రాక్టీస్‌ను ప్రారంభించడానికి ఒక మాడ్యూల్‌ను ఎంచుకోండి (ఇది లూప్‌గా కొనసాగుతుంది):<br>
ಈ ವಿಷಯದ ಮೇಲೆ ನಿಮ್ಮ ಅಭ್ಯಾಸವನ್ನು ಪ್ರಾರಂಭಿಸಲು ಒಂದು ಮಾಡ್ಯೂಲ್ ಆಯ್ಕೆಮಾಡಿ (ಇದು ಲೂಪ್ ಆಗಿ ಮುಂದುವರಿಯುತ್ತದೆ):
</p>
</div>""", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4, gap="small")
    with col1:
        if st.button("✍️ 1. Schreiben (Writing)", type="primary", use_container_width=True, key="btn_flow_writing"):
            st.session_state.lsrw_loop_topic = chosen_topic
            st.session_state.lsrw_loop_queue = ["reading", "listening", "speaking"]
            st.session_state.lsrw_current_writing_topic = chosen_topic
            st.session_state.pop("lsrw_writing_data", None)
            st.session_state.pop("lsrw_writing_evaluated", None)
            st.session_state.lsrw_module = "writing"
            st.query_params["mod"] = "writing"
            st.rerun()

    with col2:
        if st.button("📖 2. Lesen (Reading)", type="primary", use_container_width=True, key="btn_flow_reading"):
            st.session_state.lsrw_loop_topic = chosen_topic
            st.session_state.lsrw_loop_queue = ["writing", "listening", "speaking"]
            st.session_state.lsrw_current_reading_topic = chosen_topic
            st.session_state.pop("lsrw_reading_data", None)
            st.session_state.pop("lsrw_reading_submitted", None)
            st.session_state.lsrw_module = "reading"
            st.query_params["mod"] = "reading"
            st.rerun()

    with col3:
        if st.button("🎧 3. Hören (Listening)", type="primary", use_container_width=True, key="btn_flow_listening"):
            st.session_state.lsrw_loop_topic = chosen_topic
            st.session_state.lsrw_loop_queue = ["speaking", "reading", "writing"]
            st.session_state.lsrw_current_listening_topic = chosen_topic
            st.session_state.pop("lsrw_listening_data", None)
            st.session_state.pop("lsrw_real_data", None)
            st.session_state.pop("lsrw_listening_submitted", None)
            st.session_state.pop("lsrw_real_submitted", None)
            st.session_state.lsrw_module = "listening"
            st.query_params["mod"] = "listening"
            st.rerun()

    with col4:
        if st.button("🗣️ 4. Sprechen (Speaking)", type="primary", use_container_width=True, key="btn_flow_speaking"):
            st.session_state.lsrw_loop_topic = chosen_topic
            st.session_state.lsrw_loop_queue = ["listening", "reading", "writing"]
            st.session_state.lsrw_current_speaking_topic = chosen_topic
            st.session_state.pop("lsrw_speaking_cards", None)
            st.session_state.pop("lsrw_speaking_revealed", None)
            st.session_state.pop("lsrw_speaking_evaluated", None)
            st.session_state.lsrw_module = "speaking"
            st.query_params["mod"] = "speaking"
            st.rerun()

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    if st.button("➕ Neues Thema lernen (కొత్త అంశం / ಹೊಸ ವಿಷಯ)", use_container_width=True, key="btn_flow_new_topic"):
        st.session_state.pop("learn_active_topic", None)
        st.session_state.pop("learn_depth", None)
        st.session_state.pop("learn_explanation_text", None)
        st.session_state.lsrw_loop_queue = []
        st.session_state.lsrw_loop_topic = None
        st.rerun()


# ==============================================================================
# MODUL 1: LESEN (READING) — 2 Texte + 10 Lücken + 10 MCQs (index=None)
# ==============================================================================

def _render_reading_module():
    pid = _get_active_player_id()
    api_key = storage.get_gemini_api_key()

    learned_list = [t["topic"] for t in storage.get_learned_topics(pid)]
    available_topics = []
    for t in learned_list:
        if t not in available_topics:
            available_topics.append(t)
    for t in PRESET_TOPICS:
        if t not in available_topics:
            available_topics.append(t)

    st.markdown("## 📖 Modul 1: Leseverstehen")
    _render_loop_navigation_banner("reading")

    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        topic_options = available_topics if len(learned_list) <= 1 else [f"🎯 Alle {len(learned_list)} aktiven Themen (Kumulativ)"] + available_topics
        chosen_topic = st.selectbox(
            "🎯 Grammatikthema für Leseverstehen wählen:",
            options=topic_options,
            key="lsrw_reading_topic_choice"
        )
    with col_t2:
        if st.button("🔄 Neue Lesetexte", key="btn_refresh_reading", use_container_width=True):
            st.session_state.pop("lsrw_reading_data", None)
            st.session_state["lsrw_force_refresh_reading"] = True
            st.rerun()

    active_topics = learned_list if ("Alle" in chosen_topic and "aktiven Themen" in chosen_topic) else [chosen_topic]
    topics = active_topics

    last_r_topic = st.session_state.get("lsrw_current_reading_topic", None)
    if last_r_topic != chosen_topic:
        st.session_state.lsrw_current_reading_topic = chosen_topic
        st.session_state.pop("lsrw_reading_data", None)
        st.session_state.pop("lsrw_reading_submitted", None)

    if "lsrw_reading_data" not in st.session_state:
        force_r = st.session_state.pop("lsrw_force_refresh_reading", False)
        # Full-Screen Blur Modal Overlay with Catching Phrases (25s rotation)
        render_phrase_loader("📖 Erstelle Lesetexte und Aufgaben zu Ihren Grammatikthemen...")
        try:
            data = generate_reading_exercise(api_key, active_topics, lang="de", force_refresh=force_r)
            st.session_state.lsrw_reading_data = data
            st.session_state.lsrw_reading_submitted = False
            st.rerun()
        except Exception as e:
            st.error(f"Fehler bei der Aufgabenerstellung: {e}")
            return

    dismiss_phrase_loader()
    data = st.session_state.lsrw_reading_data
    submitted = st.session_state.get("lsrw_reading_submitted", False)

    # 2 Lesetexte anzeigen
    for key in ["paragraph1", "paragraph2"]:
        p = data.get(key, {})
        title = p.get("title", "Lesetext")
        text = p.get("text", "")
        st.markdown(f"""<div style="background: #f0fdf4; border: 2px solid #bbf7d0; border-radius: 14px; padding: 16px 20px; margin-bottom: 16px;">
<h4 style="margin: 0 0 8px 0; color: #166534;">📄 {title}</h4>
<p style="font-size: 1rem; color: #1e293b; line-height: 1.7; margin: 0;">{text}</p>
</div>""", unsafe_allow_html=True)

    # Teil 1: 5 Lückenaufgaben (index=None)
    st.markdown("### ✏️ Teil A: Lückentext (5 Aufgaben)")
    st.caption("Wählen Sie das grammatisch passende Wort für die Lücke:")
    blanks = data.get("fill_in_blanks", [])[:5]

    for i, q in enumerate(blanks):
        st.markdown(f"**{i + 1}.** {q.get('sentence', '')}")
        options = q.get("options", [])
        key = f"reading_blank_{i}"
        if not submitted:
            st.radio(
                f"Antwort für Aufgabe {i + 1}:",
                options=options,
                index=None,  # WICHTIG: Keine Vorbelegung!
                key=key,
                label_visibility="collapsed",
                horizontal=True
            )
        else:
            user_ans = st.session_state.get(key, None)
            correct = q.get("answer", "")
            is_right = str(user_ans).strip().lower() == correct.strip().lower()
            icon = "✅" if is_right else "❌"
            st.markdown(f"{icon} Ihre Antwort: **{user_ans or 'Keine Antwort'}** | Richtige Lösung: **{correct}**")
            exp = q.get("explanation_de", "")
            if exp:
                st.caption(f"💡 Erklärung: {exp}")

    # Teil 2: 5 Multiple-Choice-Fragen (index=None)
    st.markdown("### 📋 Teil B: Textverständnis (5 Fragen)")
    st.caption("Beantworten Sie die Fragen zum Inhalt und Satzbau:")
    mcqs = data.get("mcq", [])[:5]

    for i, q in enumerate(mcqs):
        st.markdown(f"**{i + 6}.** {q.get('question', '')}")
        options = q.get("options", [])
        key = f"reading_mcq_{i}"
        if not submitted:
            st.radio(
                f"Antwort für Frage {i + 6}:",
                options=options,
                index=None,  # WICHTIG: Keine Vorbelegung!
                key=key,
                label_visibility="collapsed"
            )
        else:
            user_ans = st.session_state.get(key, None)
            correct = q.get("answer", "")
            is_right = str(user_ans).strip().lower() == correct.strip().lower()
            icon = "✅" if is_right else "❌"
            st.markdown(f"{icon} Ihre Antwort: **{user_ans or 'Keine Antwort'}** | Richtige Lösung: **{correct}**")
            exp = q.get("explanation_de", "")
            if exp:
                st.caption(f"💡 Erklärung: {exp}")

    if not submitted:
        if st.button("🚀 Leseverstehen abgeben & bewerten", type="primary", use_container_width=True, key="btn_submit_reading"):
            score = 0
            for i, q in enumerate(blanks):
                user_ans = st.session_state.get(f"reading_blank_{i}", "")
                if user_ans and user_ans.strip().lower() == q.get("answer", "").strip().lower():
                    score += 1
            for i, q in enumerate(mcqs):
                user_ans = st.session_state.get(f"reading_mcq_{i}", "")
                if user_ans and user_ans.strip().lower() == q.get("answer", "").strip().lower():
                    score += 1
            total = len(blanks) + len(mcqs)
            storage.save_lsrw_module_score(pid, "reading", score, total, topics)
            st.session_state.lsrw_reading_score = score
            st.session_state.lsrw_reading_total = total
            st.session_state.lsrw_reading_submitted = True
            st.rerun()
    else:
        score = st.session_state.get("lsrw_reading_score", 0)
        total = st.session_state.get("lsrw_reading_total", 10)
        pct = round(score / total * 100) if total > 0 else 0
        badge = "🎉 AUSGEZEICHNET!" if pct >= 90 else "👏 SEHR GUT!" if pct >= 70 else "💪 WEITER SO!"
        st.markdown(f"""<div style="background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%); border-radius: 16px; padding: 24px; text-align: center; color: white; margin: 20px 0;">
<h2 style="margin: 0; color: #fef08a;">{badge}</h2>
<div style="font-size: 3rem; font-weight: 900; margin: 8px 0;">{score} <span style="font-size: 1.5rem; color: #93c5fd;">/ {total}</span></div>
<p style="margin: 0; color: #bfdbfe;">Getestete Grammatikthemen: {', '.join(topics)}</p>
</div>""", unsafe_allow_html=True)

        _render_loop_navigation_banner("reading")

        if st.button("🔄 Neue Leseübung generieren", use_container_width=True, key="btn_new_reading"):
            st.session_state.pop("lsrw_reading_data", None)
            st.session_state.pop("lsrw_reading_submitted", None)
            st.session_state["lsrw_force_refresh_reading"] = True
            st.rerun()


# ==============================================================================
# MODUL 2: SCHREIBEN (WRITING) — 100% Deutsch
# ==============================================================================

def _render_writing_module():
    pid = _get_active_player_id()
    api_key = storage.get_gemini_api_key()

    learned_list = [t["topic"] for t in storage.get_learned_topics(pid)]
    available_topics = []
    for t in learned_list:
        if t not in available_topics:
            available_topics.append(t)
    for t in PRESET_TOPICS:
        if t not in available_topics:
            available_topics.append(t)

    st.markdown("## ✍️ Modul 2: Schriftlicher Ausdruck")
    _render_loop_navigation_banner("writing")

    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        topic_options = available_topics if len(learned_list) <= 1 else [f"🎯 Alle {len(learned_list)} aktiven Themen (Kumulativ)"] + available_topics
        chosen_topic = st.selectbox(
            "🎯 Grammatikthema für Schriftlichen Ausdruck wählen:",
            options=topic_options,
            key="lsrw_writing_topic_choice"
        )
    with col_t2:
        if st.button("🔄 Neue Schreibaufgabe", key="btn_refresh_writing", use_container_width=True):
            st.session_state.pop("lsrw_writing_data", None)
            st.rerun()

    active_topics = learned_list if ("Alle" in chosen_topic and "aktiven Themen" in chosen_topic) else [chosen_topic]
    topics = active_topics

    last_w_topic = st.session_state.get("lsrw_current_writing_topic", None)
    if last_w_topic != chosen_topic:
        st.session_state.lsrw_current_writing_topic = chosen_topic
        st.session_state.pop("lsrw_writing_data", None)
        st.session_state.pop("lsrw_writing_evaluated", None)
        st.session_state.pop("lsrw_writing_feedback", None)

    if "lsrw_writing_data" not in st.session_state:
        # Full-Screen Blur Modal Overlay with Catching Phrases (25s rotation)
        render_phrase_loader("✍️ Erstelle Prüfungsaufgabe (Schreiben)...")
        try:
            data = generate_writing_prompt(api_key, active_topics, lang="de")
            st.session_state.lsrw_writing_data = data
            st.session_state.lsrw_writing_evaluated = False
            st.rerun()
        except Exception as e:
            st.error(f"Fehler bei der Aufgabenerstellung: {e}")
            return

    dismiss_phrase_loader()
    data = st.session_state.lsrw_writing_data
    evaluated = st.session_state.get("lsrw_writing_evaluated", False)

    task_type = data.get("type", "E-Mail")
    register = data.get("register", "informell")
    scenario_de = data.get("scenario_de", "")
    instructions_de = data.get("instructions_de", "")

    st.markdown(f"""<div style="background: #fefce8; border: 2px solid #fde047; border-radius: 14px; padding: 16px 20px; margin-bottom: 16px;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
<h4 style="margin: 0; color: #854d0e;">📝 Schreibaufgabe: {task_type}</h4>
<span style="background: #fbbf24; color: #78350f; padding: 3px 10px; border-radius: 999px; font-size: 0.8rem; font-weight: 700;">Stil: {register}</span>
</div>
<p style="font-size: 1rem; color: #1e293b; line-height: 1.6; margin-bottom: 6px;"><strong>Situation:</strong> {scenario_de}</p>
{f'<p style="font-size: 0.92rem; color: #713f12; margin: 0;"><strong>Anweisung:</strong> {instructions_de}</p>' if instructions_de else ''}
</div>""", unsafe_allow_html=True)

    st.markdown("**Leitpunkte (Gehen Sie auf alle Punkte ein):**")
    points = data.get("leitpunkte", [])
    for i, p in enumerate(points):
        st.markdown(f"  {i + 1}. {p}")

    word_count = data.get("word_count", 80)
    st.caption(f"Umfang: ca. {word_count} Wörter | Zu verwendende Grammatik: {', '.join(topics)}")

    if not evaluated:
        user_text = st.text_area(
            "Verfassen Sie hier Ihren deutschen Text:",
            height=260,
            placeholder="Sehr geehrte Damen und Herren, ... / Liebe/r ...,",
            key="lsrw_writing_input"
        )
        word_ct = len(user_text.split()) if user_text.strip() else 0
        st.caption(f"Aktuelle Wortanzahl: {word_ct} / ca. {word_count} Wörter")

        if st.button("🚀 Text zur Korrektur einreichen", type="primary", use_container_width=True, key="btn_submit_writing"):
            if not user_text.strip():
                st.warning("Bitte schreiben Sie zuerst einen Text, bevor Sie ihn einreichen!")
            else:
                with st.spinner("👩‍🏫 Prüfer analysiert Ihren Text und bewertet die Grammatik..."):
                    try:
                        feedback = evaluate_writing_submission(api_key, data, user_text, topics, lang="de")
                        st.session_state.lsrw_writing_feedback = feedback
                        st.session_state.lsrw_writing_evaluated = True
                        st.session_state.lsrw_writing_user_text = user_text
                        storage.save_lsrw_module_score(pid, "writing", 8, 10, topics)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Bewertungsfehler: {e}")
    else:
        st.markdown("**Ihr eingereichter Text:**")
        st.markdown(f"> {st.session_state.get('lsrw_writing_user_text', '')}")
        st.markdown("---")
        st.markdown("### 📋 Prüfungsbewertung & Korrektur")
        st.markdown(st.session_state.get("lsrw_writing_feedback", ""))

        _render_loop_navigation_banner("writing")

        if st.button("🔄 Neue Schreibaufgabe starten", use_container_width=True, key="btn_new_writing"):
            st.session_state.pop("lsrw_writing_data", None)
            st.session_state.pop("lsrw_writing_evaluated", None)
            st.session_state.pop("lsrw_writing_feedback", None)
            st.rerun()


# ==============================================================================
# MODUL 3: HÖREN (LISTENING) — Modus: Einfach vs. Prüfung/Real (max. 2x)
# ==============================================================================

def _render_listening_module():
    pid = _get_active_player_id()
    api_key = storage.get_gemini_api_key()

    learned_list = [t["topic"] for t in storage.get_learned_topics(pid)]
    available_topics = []
    for t in learned_list:
        if t not in available_topics:
            available_topics.append(t)
    for t in PRESET_TOPICS:
        if t not in available_topics:
            available_topics.append(t)

    st.markdown("## 🎧 Modul 3: Hörverstehen (Blind-Modus)")
    _render_loop_navigation_banner("listening")

    col_mode, col_topic = st.columns([1, 1], gap="medium")
    with col_mode:
        selected_mode = st.selectbox(
            "Hörverstehensmodus wählen:",
            options=[
                "Einfach (Easy: 1 Audio pro Frage)",
                "Prüfung / Real (Goethe-Format: 1 Hörtext, max. 2x hören, 5 Fragen)"
            ],
            key="lsrw_hoeren_mode"
        )

    with col_topic:
        topic_options = available_topics if len(learned_list) <= 1 else [f"🎯 Alle {len(learned_list)} aktiven Themen (Kumulativ)"] + available_topics
        chosen_topic = st.selectbox(
            "🎯 Grammatikthema für Hörverstehen wählen:",
            options=topic_options,
            key="lsrw_listening_topic_choice"
        )

    # Bei Themen- oder Moduswechsel Daten gezielt zurücksetzen
    last_mode = st.session_state.get("lsrw_current_listening_mode", None)
    last_topic = st.session_state.get("lsrw_current_listening_topic", None)

    if last_mode != selected_mode or last_topic != chosen_topic:
        st.session_state.lsrw_current_listening_mode = selected_mode
        st.session_state.lsrw_current_listening_topic = chosen_topic
        st.session_state.pop("lsrw_listening_data", None)
        st.session_state.pop("lsrw_real_data", None)
        st.session_state.pop("lsrw_listening_submitted", None)
        st.session_state.pop("lsrw_real_submitted", None)
        st.session_state["lsrw_real_play_count"] = 0

    active_topics = learned_list if ("Alle" in chosen_topic and "aktiven Themen" in chosen_topic) else [chosen_topic]
    topics = active_topics
    is_real_mode = "Prüfung" in selected_mode

    if is_real_mode:
        _render_listening_real_exam(api_key, active_topics, pid)
    else:
        _render_listening_easy_mode(api_key, active_topics, pid)


def _render_listening_easy_mode(api_key, topics, pid):
    """Einfacher Modus: 10 Sätze, jeweils 1 Audio pro Frage."""
    st.markdown("""<div style="background: #fef3c7; border: 2px solid #fbbf24; border-radius: 12px; padding: 12px 18px; margin: 12px 0 16px 0;">
<strong>🎧 Modus Einfach:</strong> Sie hören für jede Frage einen einzelnen deutschen Satz.
Klicken Sie auf 🔊, um den Satz anzuhören. Der Satztext bleibt verborgen!
</div>""", unsafe_allow_html=True)

    if "lsrw_listening_data" not in st.session_state:
        force_r = st.session_state.pop("lsrw_force_refresh_listening_easy", False)
        # Full-Screen Blur Modal Overlay with Catching Phrases (25s rotation)
        render_phrase_loader("🎧 Erstelle 5 Hörübungen zu Ihren Grammatikthemen...")
        try:
            data = generate_listening_exercise(api_key, topics, lang="de", force_refresh=force_r)
            st.session_state.lsrw_listening_data = data
            st.session_state.lsrw_listening_submitted = False
            st.rerun()
        except Exception as e:
            st.error(f"Fehler bei der Audioerstellung: {e}")
            return

    dismiss_phrase_loader()
    data = st.session_state.lsrw_listening_data
    items = data.get("items", [])[:5]
    submitted = st.session_state.get("lsrw_listening_submitted", False)

    if not items:
        st.error("Keine Hörübungen vorhanden. Bitte erneut versuchen.")
        return

    if not submitted:
        for i, item in enumerate(items):
            sentence = item.get("sentence_de", "")
            question = item.get("question_de", "Was ist richtig?")
            options = item.get("options", [])
            safe_text = json.dumps(sentence)

            st.markdown("---")
            st.markdown(f"#### Frage {i + 1} von {len(items)}")

            # Audio-Button (Kein Text sichtbar!)
            components.html(f"""
<div style="display: flex; align-items: center; gap: 12px; margin: 6px 0;">
<button onclick="playEasy{i}()" style="
background: linear-gradient(135deg, #2563eb, #1d4ed8); color: white; border: none;
border-radius: 10px; padding: 10px 20px; font-size: 14px; font-weight: 700;
cursor: pointer; display: flex; align-items: center; gap: 8px;
box-shadow: 0 4px 12px rgba(37,99,235,0.25);
" onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
🔊 Satz {i + 1} anhören
</button>
<span id="st_easy_{i}" style="font-size: 0.85rem; color: #64748b;">Klicken zum Anhören</span>
</div>
<script>
function playEasy{i}() {{
if ('speechSynthesis' in window) {{
window.speechSynthesis.cancel();
var u = new SpeechSynthesisUtterance({safe_text});
u.lang = 'de-DE'; u.rate = 0.85;
document.getElementById('st_easy_{i}').innerText = '▶️ Audio wird abgespielt...';
u.onend = function() {{ document.getElementById('st_easy_{i}').innerText = '✅ Angehört. Bitte Antwort wählen.'; }};
window.speechSynthesis.speak(u);
}}
}}
</script>""", height=55)

            st.markdown(f"**❓ {question}**")
            st.radio(
                f"Antwort für Frage {i + 1}:",
                options=options,
                index=None,  # WICHTIG: Keine Vorbelegung!
                key=f"listening_q_{i}",
                label_visibility="collapsed"
            )

        if st.button("🚀 Alle 5 Antworten abgeben", type="primary", use_container_width=True, key="btn_submit_easy_hoeren"):
            score = 0
            for i, item in enumerate(items):
                user_ans = st.session_state.get(f"listening_q_{i}", "")
                correct = item.get("answer", "")
                if user_ans and user_ans.strip().lower() == correct.strip().lower():
                    score += 1
            st.session_state.lsrw_listening_score = score
            st.session_state.lsrw_listening_submitted = True
            storage.save_lsrw_module_score(pid, "listening", score, len(items), topics)
            st.rerun()

    else:
        score = st.session_state.get("lsrw_listening_score", 0)
        total = len(items)
        pct = round(score / total * 100) if total > 0 else 0
        badge = "🎉 AUSGEZEICHNET!" if pct >= 90 else "👏 SEHR GUT!" if pct >= 70 else "💪 WEITER SO!"

        st.markdown(f"""<div style="background: linear-gradient(135deg, #92400e 0%, #d97706 100%); border-radius: 16px; padding: 24px; text-align: center; color: white; margin: 16px 0;">
<h2 style="margin: 0; color: #fef08a;">{badge}</h2>
<div style="font-size: 3rem; font-weight: 900; margin: 8px 0;">{score} <span style="font-size: 1.5rem; color: #fde68a;">/ {total}</span></div>
<p style="margin: 0; color: #fef3c7;">Hörverstehen (Einfach) — Themen: {', '.join(topics)}</p>
</div>""", unsafe_allow_html=True)

        st.markdown("### 📋 Auflösung & Transkripte")
        for i, item in enumerate(items):
            user_ans = st.session_state.get(f"listening_q_{i}", None)
            correct = item.get("answer", "")
            is_right = str(user_ans).strip().lower() == correct.strip().lower()
            icon = "✅" if is_right else "❌"
            sentence = item.get("sentence_de", "")

            st.markdown(f"**{i + 1}.** {icon} {item.get('question_de', '')}")
            st.markdown(f"   🔊 **Gesprochener Satz:** *\"{sentence}\"*")
            st.markdown(f"   Ihre Antwort: **{user_ans or 'Keine Antwort'}** | Richtige Lösung: **{correct}**")
            exp = item.get("explanation_de", "")
            if exp:
                st.caption(f"   💡 {exp}")

        _render_loop_navigation_banner("listening")

        if st.button("🔄 Neue Hörverstehensrunde starten", use_container_width=True, key="btn_new_listening_easy"):
            st.session_state.pop("lsrw_listening_data", None)
            st.session_state.pop("lsrw_listening_submitted", None)
            st.session_state["lsrw_force_refresh_listening_easy"] = True
            st.rerun()


def _render_listening_real_exam(api_key, topics, pid):
    """Echter Prüfungsmodus: 1 zusammenhängender A2/B1 Hörtext, max. 2x abspielen, 10 Fragen."""
    st.markdown("""<div style="background: #eff6ff; border: 2px solid #3b82f6; border-radius: 14px; padding: 14px 20px; margin: 12px 0 16px 0;">
<h4 style="margin: 0 0 6px 0; color: #1e40af;">🎓 Goethe-Zertifikat B1 Prüfungssimulation (Hören)</h4>
<p style="margin: 0; font-size: 0.95rem; color: #1e293b;">
<strong>Prüfungsregel:</strong> Sie hören diesen zusammenhängenden Text <strong>genau zweimal (max. 2x)</strong>.
Nach dem zweiten Mal ist das Abspielen gesperrt. Beantworten Sie anschließend die 10 Prüfungsfragen unten.
</p>
</div>""", unsafe_allow_html=True)

    if "lsrw_real_data" not in st.session_state:
        force_r = st.session_state.pop("lsrw_force_refresh_listening_real", False)
        # Full-Screen Blur Modal Overlay with Catching Phrases (25s rotation)
        render_phrase_loader("🎧 Generiere zusammenhängenden Goethe-Prüfungstext und 5 Fragen...")
        try:
            data = generate_real_listening_exam(api_key, topics, force_refresh=force_r)
            st.session_state.lsrw_real_data = data
            st.session_state.lsrw_real_submitted = False
            st.session_state["lsrw_real_play_count"] = 0
            st.rerun()
        except Exception as e:
            st.error(f"Fehler bei der Prüfungserstellung: {e}")
            return

    dismiss_phrase_loader()
    data = st.session_state.lsrw_real_data
    title = data.get("title", "Prüfungshörtext")
    full_audio = data.get("full_audio_text", "")
    questions = data.get("questions", [])[:5]
    submitted = st.session_state.get("lsrw_real_submitted", False)

    play_count = st.session_state.get("lsrw_real_play_count", 0)
    safe_full_text = json.dumps(full_audio)

    # Audio-Bedienfeld mit 2x-Beschränkung
    st.markdown("### 🎙️ Audio-Wiedergabe (Maximal 2x)")

    col_btn, col_status = st.columns([1, 2])
    with col_btn:
        if play_count < 2 and not submitted:
            btn_label = f"🔊 Hörtext abspielen ({play_count + 1} / 2)"
            if st.button(btn_label, type="primary", use_container_width=True, key=f"btn_real_play_{play_count}"):
                st.session_state["lsrw_real_play_count"] = play_count + 1
                st.session_state["lsrw_real_trigger_audio"] = True
                st.rerun()
        else:
            st.button("⛔ Limit erreicht (2 von 2 Mal)", disabled=True, use_container_width=True, key="btn_real_play_locked")

    with col_status:
        if play_count == 0:
            st.info("Noch nicht abgespielt. Klicken Sie links auf den Button, um den Text zum 1. Mal zu hören.")
        elif play_count == 1:
            st.warning("1 von 2 Mal gehört. Sie können den Text noch **ein einziges Mal** wiederholen.")
        else:
            st.error("⛔ Sie haben den Text bereits 2 Mal gehört (Prüfungslimit erreicht). Beantworten Sie nun die Fragen.")

    # JavaScript Audio-Player, wenn Play geklickt wurde
    if st.session_state.get("lsrw_real_trigger_audio", False):
        st.session_state["lsrw_real_trigger_audio"] = False
        components.html(f"""
<div id="playing_status" style="padding: 10px; background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 8px; color: #065f46; font-size: 14px; font-weight: 700;">
▶️ Hörtext wird abgespielt... Bitte aufmerksam zuhören!
</div>
<script>
if ('speechSynthesis' in window) {{
    window.speechSynthesis.cancel();
    var u = new SpeechSynthesisUtterance({safe_full_text});
    u.lang = 'de-DE';
    u.rate = 0.88;
    u.onend = function() {{
        var el = document.getElementById('playing_status');
        if (el) {{
            el.innerText = '✅ Wiedergabe beendet.';
            el.style.background = '#eff6ff';
            el.style.color = '#1e40af';
        }}
    }};
    window.speechSynthesis.speak(u);
}} else {{
    alert('Sprachausgabe im Browser nicht unterstützt.');
}}
</script>
""", height=50)

    # 5 Prüfungsfragen
    st.markdown("---")
    st.markdown("### 📋 Prüfungsfragen (5 Aufgaben zum Hörtext - Goethe Teil 1 Standard)")

    if not submitted:
        for i, q in enumerate(questions):
            q_text = q.get("question_de", f"Frage {i + 1}")
            options = q.get("options", [])
            key = f"real_exam_q_{i}"

            st.markdown(f"**{i + 1}. {q_text}**")
            st.radio(
                f"Auswahl zu Frage {i + 1}:",
                options=options,
                index=None,  # WICHTIG: Keine Vorbelegung!
                key=key,
                label_visibility="collapsed"
            )
            st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)

        if st.button("🚀 Prüfungsergebnis abgeben & auswerten", type="primary", use_container_width=True, key="btn_submit_real_exam"):
            score = 0
            for i, q in enumerate(questions):
                user_ans = st.session_state.get(f"real_exam_q_{i}", "")
                correct = q.get("answer", "")
                if user_ans and user_ans.strip().lower() == correct.strip().lower():
                    score += 1
            st.session_state.lsrw_real_score = score
            st.session_state.lsrw_real_submitted = True
            storage.save_lsrw_module_score(pid, "listening", score, len(questions), topics)
            st.rerun()

    else:
        score = st.session_state.get("lsrw_real_score", 0)
        total = len(questions)
        pct = round(score / total * 100) if total > 0 else 0
        badge = "🎉 BESTANDEN (AUSGEZEICHNET)!" if pct >= 90 else "👏 BESTANDEN (SEHR GUT)!" if pct >= 60 else "💪 NICHT BESTANDEN (NOCHMAL ÜBEN)!"

        st.markdown(f"""<div style="background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%); border-radius: 16px; padding: 24px; text-align: center; color: white; margin: 16px 0;">
<h2 style="margin: 0; color: #fef08a;">{badge}</h2>
<div style="font-size: 3rem; font-weight: 900; margin: 8px 0;">{score} <span style="font-size: 1.5rem; color: #93c5fd;">/ {total}</span></div>
<p style="margin: 0; color: #bfdbfe;">Goethe B1 Hörverstehen (Echte Prüfung) — Themen: {', '.join(topics)}</p>
</div>""", unsafe_allow_html=True)

        # Transkript offenlegen
        with st.expander("📄 Vollständiges Prüfungs-Transkript anzeigen (Text zum Nachlesen)"):
            st.markdown(f"**Titel:** {title}")
            st.markdown(f"> {full_audio}")

        st.markdown("### 📋 Detailauswertung der 10 Fragen")
        for i, q in enumerate(questions):
            user_ans = st.session_state.get(f"real_exam_q_{i}", None)
            correct = q.get("answer", "")
            is_right = str(user_ans).strip().lower() == correct.strip().lower()
            icon = "✅" if is_right else "❌"

            st.markdown(f"**{i + 1}.** {icon} {q.get('question_de', '')}")
            st.markdown(f"   Ihre Antwort: **{user_ans or 'Keine Antwort'}** | Richtige Lösung: **{correct}**")
            exp = q.get("explanation_de", "")
            if exp:
                st.caption(f"   💡 Erklärung: {exp}")

        _render_loop_navigation_banner("listening")

        if st.button("🔄 Neue Prüfungssimulation starten", use_container_width=True, key="btn_new_real_exam"):
            st.session_state.pop("lsrw_real_data", None)
            st.session_state.pop("lsrw_real_submitted", None)
            st.session_state["lsrw_real_play_count"] = 0
            st.session_state["lsrw_force_refresh_listening_real"] = True
            st.rerun()


# ==============================================================================
# MODUL 4: SPRECHEN (SPEAKING) — Solitär-Karten & Mikrofon (100% Deutsch)
# ==============================================================================

def _render_speaking_module():
    pid = _get_active_player_id()
    api_key = storage.get_gemini_api_key()

    learned_list = [t["topic"] for t in storage.get_learned_topics(pid)]
    available_topics = []
    for t in learned_list:
        if t not in available_topics:
            available_topics.append(t)
    for t in PRESET_TOPICS:
        if t not in available_topics:
            available_topics.append(t)

    st.markdown("## 🗣️ Modul 4: Mündlicher Ausdruck (Sprechen)")
    _render_loop_navigation_banner("speaking")

    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        topic_options = available_topics if len(learned_list) <= 1 else [f"🎯 Alle {len(learned_list)} aktiven Themen (Kumulativ)"] + available_topics
        chosen_topic = st.selectbox(
            "🎯 Grammatikthema für Mündlichen Ausdruck wählen:",
            options=topic_options,
            key="lsrw_speaking_topic_choice"
        )
    with col_t2:
        if st.button("🔄 Neue Karten", key="btn_refresh_speaking", use_container_width=True):
            st.session_state.pop("lsrw_speaking_cards", None)
            st.session_state["lsrw_force_refresh_speaking"] = True
            st.rerun()

    active_topics = learned_list if ("Alle" in chosen_topic and "aktiven Themen" in chosen_topic) else [chosen_topic]
    topics = active_topics

    last_s_topic = st.session_state.get("lsrw_current_speaking_topic", None)
    if last_s_topic != chosen_topic:
        st.session_state.lsrw_current_speaking_topic = chosen_topic
        st.session_state.pop("lsrw_speaking_cards", None)
        st.session_state.pop("lsrw_speaking_revealed", None)
        st.session_state.pop("lsrw_speaking_evaluated", None)

    st.markdown("""<div style="background: #f5f3ff; border: 2px solid #c4b5fd; border-radius: 12px; padding: 12px 18px; margin-bottom: 16px;">
<strong>🃏 Solitär-Modus:</strong> Decken Sie eine der verdeckten Themenkarten auf.
Sprechen Sie anschließend frei und auf Deutsch über das Thema in Ihr Mikrofon (kein Lesen oder Schreiben!).
</div>""", unsafe_allow_html=True)

    if "lsrw_speaking_cards" not in st.session_state:
        force_r = st.session_state.pop("lsrw_force_refresh_speaking", False)
        # Full-Screen Blur Modal Overlay with Catching Phrases (25s rotation)
        render_phrase_loader("🃏 Generiere 8 Prüfungskarten...")
        try:
            cards = generate_speaking_cards(api_key, active_topics, force_refresh=force_r)
            st.session_state.lsrw_speaking_cards = cards
            st.session_state.lsrw_speaking_revealed = None
            st.session_state.lsrw_speaking_evaluated = False
            st.rerun()
        except Exception as e:
            st.error(f"Fehler beim Erstellen der Karten: {e}")
            return

    dismiss_phrase_loader()
    cards = st.session_state.lsrw_speaking_cards
    revealed = st.session_state.get("lsrw_speaking_revealed", None)
    evaluated = st.session_state.get("lsrw_speaking_evaluated", False)

    if revealed is None and not evaluated:
        st.markdown("### 🃏 Wählen Sie eine verdeckte Karte:")
        cols_per_row = 4
        rows = [cards[i:i + cols_per_row] for i in range(0, len(cards), cols_per_row)]
        for row_cards in rows:
            cols = st.columns(cols_per_row)
            for j, card in enumerate(row_cards):
                with cols[j]:
                    card_id = card.get("id", j + 1)
                    st.markdown(f"""<div style="background: linear-gradient(135deg, #312e81, #4c1d95); border-radius: 16px;
padding: 26px 10px; text-align: center; min-height: 110px; display: flex; flex-direction: column; align-items: center; justify-content: center;
box-shadow: 0 6px 18px rgba(76,29,149,0.25); border: 2px solid #7c3aed;">
<span style="font-size: 2.3rem;">🂠</span>
<span style="color: #c4b5fd; font-size: 0.85rem; margin-top: 6px; font-weight: 700;">Karte {card_id}</span>
</div>""", unsafe_allow_html=True)
                    if st.button(f"Karte {card_id} aufdecken", use_container_width=True, key=f"flip_{card_id}"):
                        st.session_state.lsrw_speaking_revealed = card
                        st.rerun()

    elif revealed and not evaluated:
        topic_de = revealed.get("topic_de", "Thema")
        hint_de = revealed.get("hint_de", "Sprechen Sie frei über Ihre Erfahrungen.")
        grammar = revealed.get("grammar_focus", ", ".join(topics))

        st.markdown(f"""<div style="background: linear-gradient(135deg, #7c3aed, #a78bfa); border-radius: 20px;
padding: 28px; text-align: center; color: white; margin: 16px 0;
box-shadow: 0 8px 30px rgba(124,58,237,0.3);">
<div style="font-size: 0.9rem; color: #ddd6fe; margin-bottom: 6px;">IHRE THEMENKARTE:</div>
<div style="font-size: 3rem; font-weight: 900; margin: 6px 0;">🎤 {topic_de}</div>
<div style="font-size: 1.05rem; color: #f5f3ff; margin-top: 10px; line-height: 1.5;">{hint_de}</div>
<div style="margin-top: 10px; font-size: 0.85rem; color: #e9d5ff;">Grammatik-Fokus: <strong>{grammar}</strong></div>
</div>""", unsafe_allow_html=True)

        st.markdown("### 🎙️ Sprechen Sie jetzt (Sprechen Sie Deutsch)")
        st.caption("Drücken Sie auf 🔴, um die Aufnahme zu starten. Sprechen Sie mindestens 1-2 Minuten frei auf Deutsch.")

        audio_capture = st.audio_input(
            "Mikrofon-Eingabe (Deutsch):",
            key=f"speaking_audio_{revealed.get('id', 0)}"
        )

        col_voice, col_text = st.columns([2, 1])
        with col_voice:
            if st.button("🚀 Sprachaufnahme zur Bewertung einreichen", type="primary", use_container_width=True,
                         key="btn_submit_speaking", disabled=(audio_capture is None)):
                raw_bytes = audio_capture.getvalue()
                audio_mime = audio_capture.type or "audio/wav"
                with st.spinner("🎧 Prüfer hört Ihre Aufnahme an und bewertet Aussprache und Grammatik..."):
                    try:
                        feedback = evaluate_speaking_response(
                            api_key, topic_de, grammar,
                            lang="de",
                            raw_audio=raw_bytes,
                            audio_mime=audio_mime
                        )
                        st.session_state.lsrw_speaking_feedback = feedback
                        st.session_state.lsrw_speaking_evaluated = True
                        storage.save_lsrw_module_score(pid, "speaking", 8, 10, topics)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Bewertungsfehler: {e}")

        with col_text:
            with st.expander("⌨️ Textuelle Eingabe (falls kein Mikrofon verfügbar)"):
                typed = st.text_input("Geben Sie Ihren gesprochenen Text ein:", key="speaking_typed_fallback")
                if st.button("Text absenden", key="btn_speaking_typed"):
                    if typed.strip():
                        with st.spinner("Bewerte mündlichen Text..."):
                            try:
                                feedback = evaluate_speaking_response(
                                    api_key, topic_de, grammar,
                                    lang="de", typed_text=typed.strip()
                                )
                                st.session_state.lsrw_speaking_feedback = feedback
                                st.session_state.lsrw_speaking_evaluated = True
                                storage.save_lsrw_module_score(pid, "speaking", 8, 10, topics)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Bewertungsfehler: {e}")

    else:
        st.markdown("### 📝 Bewertung des mündlichen Ausdrucks")
        st.markdown(st.session_state.get("lsrw_speaking_feedback", ""))

        _render_loop_navigation_banner("speaking")

        col_new, col_hub = st.columns(2)
        with col_new:
            if st.button("🃏 Andere Karte aufdecken", use_container_width=True, key="btn_new_card"):
                st.session_state.lsrw_speaking_revealed = None
                st.session_state.lsrw_speaking_evaluated = False
                st.session_state.pop("lsrw_speaking_feedback", None)
                st.rerun()
        with col_hub:
            if st.button("🔄 Neue Kartenserie generieren", use_container_width=True, key="btn_new_cards"):
                st.session_state.pop("lsrw_speaking_cards", None)
                st.session_state.pop("lsrw_speaking_revealed", None)
                st.session_state.pop("lsrw_speaking_evaluated", None)
                st.session_state["lsrw_force_refresh_speaking"] = True
                st.rerun()
