"""
Learning Studio (Lernen) — Goethe-Zertifikat B1 Grammatik-Lernstudio.
Independent top-level learning arena offering bilingual grammar explanations
in Telugu (తెలుగు) & Kannada (ಕನ್ನಡ), with direct connection bridges into
Meisterstudio (LSRW: Lesen, Schreiben, Hören, Sprechen) and Duels.
"""
import streamlit as st
import storage
from src.ai_service import generate_topic_explanation
from src.components import (
    render_api_key_banner,
    render_api_key_prompt,
    render_phrase_loader,
    dismiss_phrase_loader,
)

PRESET_LEARNING_TOPICS = [
    "Präpositionen (Akkusativ und Dativ)",
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
    "N-Deklination (Weak Masculine Nouns)"
]


def _get_active_player_id():
    name = st.session_state.get("player_name", "gast")
    return name.lower().replace(" ", "_") if name else "gast"


def render_learning_view():
    """
    Renders the dedicated Goethe B1 Grammar Learning Studio (Lernen).
    Positioned outside Meisterstudio, but tightly connected to all LSRW modules and duels.
    """
    pid = _get_active_player_id()
    api_key = storage.get_gemini_api_key()

    # Guard query params
    if st.query_params.get("view") != "learning":
        st.query_params["view"] = "learning"

    # Header Card
    st.markdown("""<div class="home-hero" style="padding: 22px 30px; background: linear-gradient(135deg, #4c1d95 0%, #6d28d9 50%, #8b5cf6 100%);">
<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
    <div>
        <h1 style="font-size: 2rem; color: #fff; margin-bottom: 4px;">🧠 Goethe B1 Grammatik-Lernstudio (Lernen)</h1>
        <p style="font-size: 1rem; color: #ddd6fe; margin: 0;">
            వ్యాకరణం నేర్చుకోండి • ವ್ಯಾಕರಣ ಕಲಿಯಿರಿ — Bilingual Grammar Mastery with Direct LSRW & Duel Practice Bridges
        </p>
    </div>
</div>
</div>""", unsafe_allow_html=True)

    # Navigation bridge buttons between Lernen, Meisterstudio and Duels
    col_nav_a, col_nav_b, col_nav_c = st.columns([1, 1, 1], gap="small")
    with col_nav_a:
        if st.button("🎓 Go to Meisterstudio (LSRW) ➔", use_container_width=True, key="btn_learn_to_lsrw"):
            st.session_state.app_view = "lsrw"
            st.session_state.lsrw_module = "hub"
            st.query_params["view"] = "lsrw"
            st.query_params["mod"] = "hub"
            st.rerun()
    with col_nav_b:
        if st.button("🎯 Go to Pronoun Duel ➔", use_container_width=True, key="btn_learn_to_duel"):
            st.session_state.app_view = "quiz"
            st.query_params["view"] = "quiz"
            st.rerun()
    with col_nav_c:
        if st.button("🏷️ Go to Gender Duel ➔", use_container_width=True, key="btn_learn_to_gender"):
            st.session_state.app_view = "gender"
            st.query_params["view"] = "gender"
            st.rerun()

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

    # Active API Key Status Banner
    render_api_key_banner()

    if not api_key:
        render_api_key_prompt("Grammatik-Lernstudio (Telugu & Kannada)")
        return

    # Cumulative learned topics
    learned_list = [t["topic"] for t in storage.get_learned_topics(pid)]
    available_topics = []
    for t in learned_list:
        if t not in available_topics:
            available_topics.append(t)
    for t in PRESET_LEARNING_TOPICS:
        if t not in available_topics:
            available_topics.append(t)

    chosen_topic = st.session_state.get("learn_active_topic")
    chosen_depth = st.session_state.get("learn_depth")

    # ==========================================================================
    # STEP 1: Topic Selection
    # ==========================================================================
    if not chosen_topic:
        st.markdown("### 📌 1. వ్యాకరణ అంశాన్ని ఎంచుకోండి / ವ್ಯಾಕರಣ ವಿಷಯವನ್ನು ಆಯ್ಕೆಮಾಡಿ")
        st.caption("డ్రాప్‌డౌన్ నుండి ఎంచుకోండి లేదా మీ సొంత అంశాన్ని టైప్ చేయండి / ಡ್ರಾಪ್‌ಡೌನ್‌ನಿಂದ ಆಯ್ಕೆಮಾಡಿ ಅಥವಾ ನಿಮ್ಮ ಸ್ವಂತ ವಿಷಯವನ್ನು ಟೈಪ್ ಮಾಡಿ:")

        col_sel, col_custom = st.columns([1, 1], gap="medium")
        with col_sel:
            preset_choice = st.selectbox(
                "ప్రసిద్ధ Goethe B1 అంశాలు / ಜನಪ್ರಿಯ Goethe B1 ವಿಷಯಗಳು:",
                options=["-- ఎంచుకోండి / ಆಯ್ಕೆಮಾಡಿ --"] + available_topics,
                key="learn_preset_select_main"
            )
        with col_custom:
            custom_choice = st.text_input(
                "లేదా సొంత అంశం టైప్ చేయండి / ಅಥವಾ ಸ್ವಂತ ವಿಷಯ ಟೈಪ್ ಮಾಡಿ:",
                placeholder="ఉదా: Verben mit Präpositionen, Relativsatz, Passiv, N-Deklination...",
                key="learn_custom_input_main"
            )

        col_btn, _ = st.columns([1, 1])
        with col_btn:
            if st.button("ఈ అంశాన్ని ఎంచుకోండి / ಈ ವಿಷಯವನ್ನು ಆಯ್ಕೆಮಾಡಿ ➔", type="primary", use_container_width=True, key="btn_confirm_learn_topic_main"):
                target_topic = custom_choice.strip() if custom_choice.strip() else (preset_choice if preset_choice != "-- ఎంచుకోండి / ಆಯ್ಕೆಮಾಡಿ --" else "")
                if not target_topic:
                    st.warning("దయచేసి ఒక అంశాన్ని ఎంచుకోండి లేదా టైప్ చేయండి! / ದಯವಿಟ್ಟು ಒಂದು ವಿಷಯವನ್ನು ಆಯ್ಕೆಮಾಡಿ ಅಥವಾ ಟೈಪ್ ಮಾಡಿ!")
                else:
                    st.session_state.learn_active_topic = target_topic
                    st.session_state.pop("learn_depth", None)
                    st.session_state.pop("learn_explanation_text", None)
                    st.rerun()
        return

    # ==========================================================================
    # STEP 2: Depth Selection (Overview vs In-Detail)
    # ==========================================================================
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
<h4 style="margin: 0 0 6px 0; color: #15803d;">⚡ Overview (సమీక్ష / అవಲೋಕನ)</h4>
<p style="margin: 0; font-size: 0.88rem; color: #166534;">
సంక్షిప్త మరియు కీలక నియమం, 3-4 ముఖ్యమైన Goethe B1 ఉదాహరణలు, పరీక్ష చిట్కా.
ಸಂಕ್ಷಿಪ್ತ ಮತ್ತು ಪ್ರಮುಖ ನಿಯಮ, 3-4 ಮುಖ್ಯ Goethe B1 ಉದಾಹರಣೆಗಳು, ಪರೀಕ್ಷಾ ಸಲಹೆ.
</p>
</div>""", unsafe_allow_html=True)
            if st.button("⚡ Overview (సమీక్ష / అవಲೋಕನ) ఎంచుకోండి", type="primary", use_container_width=True, key="btn_choose_overview_main"):
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
            if st.button("📚 In-Detail (వివరణాత్మక / ವಿವರವಾದ) ఎంచుకోండి", type="primary", use_container_width=True, key="btn_choose_indetail_main"):
                st.session_state.learn_depth = "indetail"
                st.session_state.pop("learn_explanation_text", None)
                st.rerun()

        st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
        if st.button("⬅️ మరొక అంశాన్ని ఎంచుకోండి / ಮತ್ತೊಂದು ವಿಷಯವನ್ನು ಆಯ್ಕೆಮಾಡಿ (Thema wechseln)", key="btn_back_to_topics_main"):
            st.session_state.pop("learn_active_topic", None)
            st.session_state.pop("learn_depth", None)
            st.session_state.pop("learn_explanation_text", None)
            st.rerun()
        return

    # ==========================================================================
    # STEP 3: Explanation Rendering
    # ==========================================================================
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

    # Header Controls
    col_t_info, col_t_ctrl = st.columns([3, 2])
    with col_t_info:
        depth_label = "⚡ Overview (సమీక్ష / అవಲೋಕನ)" if chosen_depth == "overview" else "📚 In-Detail (వివరణాత్మక / ವಿವರವಾದ)"
        st.markdown(f"""<div style="font-size: 1.15rem; font-weight: 800; color: #1e3a8a; margin-bottom: 6px;">
📖 Thema: <span style="color: #2563eb;">{chosen_topic}</span> ({depth_label})
</div>""", unsafe_allow_html=True)
    with col_t_ctrl:
        c1, c2 = st.columns(2)
        with c1:
            other_depth = "indetail" if chosen_depth == "overview" else "overview"
            other_label = "📚 In-Detail" if chosen_depth == "overview" else "⚡ Overview"
            if st.button(f"Wechsel zu {other_label}", key="btn_toggle_depth_main", use_container_width=True):
                st.session_state.learn_depth = other_depth
                st.session_state.pop("learn_explanation_text", None)
                st.rerun()
        with c2:
            if st.button("➕ Neues Thema", key="btn_learn_new_topic_top_main", use_container_width=True):
                st.session_state.pop("learn_active_topic", None)
                st.session_state.pop("learn_depth", None)
                st.session_state.pop("learn_explanation_text", None)
                st.rerun()

    # The actual explanation card
    st.markdown(f"""<div style="background: white; border: 2px solid #e2e8f0; border-radius: 16px; padding: 24px 28px; margin: 12px 0 20px 0; box-shadow: 0 4px 16px rgba(0,0,0,0.04);">
{st.session_state.learn_explanation_text}
</div>""", unsafe_allow_html=True)

    # ==========================================================================
    # STEP 4: Direct Connection Bridges into Meisterstudio (LSRW) & Duels!
    # ==========================================================================
    st.markdown("---")
    st.markdown("""<div style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
border: 2px solid #22c55e; border-radius: 14px; padding: 18px 24px; margin-bottom: 16px;">
<h3 style="margin: 0 0 6px 0; color: #166534;">🎯 Meisterstudio (LSRW) & Duel శిక్షణ ప్రారంభించండి / ಅಭ್ಯಾಸ ಪ್ರಾರಂಭಿಸಿ</h3>
<p style="margin: 0; font-size: 0.95rem; color: #15803d;">
ఈ అంశంపై నేరుగా Meisterstudio మాడ్యూల్స్ లేదా Duels లో ప్రాక్టీస్ చేయండి:<br>
ಈ ವಿಷಯದ ಮೇಲೆ ನೇರವಾಗಿ Meisterstudio ಮಾಡ್ಯೂಲ್ಸ್ ಅಥವಾ Duels ನಲ್ಲಿ ಅಭ್ಯಾಸ ಮಾಡಿ:
</p>
</div>""", unsafe_allow_html=True)

    # Row 1: Meisterstudio LSRW Bridges
    st.markdown("**🎓 Meisterstudio Prüfungsmodule:**")
    col1, col2, col3, col4 = st.columns(4, gap="small")
    with col1:
        if st.button("✍️ 1. Schreiben (Writing)", type="primary", use_container_width=True, key="btn_bridge_writing"):
            st.session_state.app_view = "lsrw"
            st.session_state.lsrw_loop_topic = chosen_topic
            st.session_state.lsrw_loop_queue = ["reading", "listening", "speaking"]
            st.session_state.lsrw_current_writing_topic = chosen_topic
            st.session_state.pop("lsrw_writing_data", None)
            st.session_state.pop("lsrw_writing_evaluated", None)
            st.session_state.lsrw_module = "writing"
            st.query_params["view"] = "lsrw"
            st.query_params["mod"] = "writing"
            st.rerun()

    with col2:
        if st.button("📖 2. Lesen (Reading)", type="primary", use_container_width=True, key="btn_bridge_reading"):
            st.session_state.app_view = "lsrw"
            st.session_state.lsrw_loop_topic = chosen_topic
            st.session_state.lsrw_loop_queue = ["writing", "listening", "speaking"]
            st.session_state.lsrw_current_reading_topic = chosen_topic
            st.session_state.pop("lsrw_reading_data", None)
            st.session_state.pop("lsrw_reading_submitted", None)
            st.session_state.lsrw_module = "reading"
            st.query_params["view"] = "lsrw"
            st.query_params["mod"] = "reading"
            st.rerun()

    with col3:
        if st.button("🎧 3. Hören (Listening)", type="primary", use_container_width=True, key="btn_bridge_listening"):
            st.session_state.app_view = "lsrw"
            st.session_state.lsrw_loop_topic = chosen_topic
            st.session_state.lsrw_loop_queue = ["speaking", "reading", "writing"]
            st.session_state.lsrw_current_listening_topic = chosen_topic
            st.session_state.pop("lsrw_listening_data", None)
            st.session_state.pop("lsrw_real_data", None)
            st.session_state.pop("lsrw_listening_submitted", None)
            st.session_state.pop("lsrw_real_submitted", None)
            st.session_state.lsrw_module = "listening"
            st.query_params["view"] = "lsrw"
            st.query_params["mod"] = "listening"
            st.rerun()

    with col4:
        if st.button("🗣️ 4. Sprechen (Speaking)", type="primary", use_container_width=True, key="btn_bridge_speaking"):
            st.session_state.app_view = "lsrw"
            st.session_state.lsrw_loop_topic = chosen_topic
            st.session_state.lsrw_loop_queue = ["listening", "reading", "writing"]
            st.session_state.lsrw_current_speaking_topic = chosen_topic
            st.session_state.pop("lsrw_speaking_cards", None)
            st.session_state.pop("lsrw_speaking_revealed", None)
            st.session_state.pop("lsrw_speaking_evaluated", None)
            st.session_state.lsrw_module = "speaking"
            st.query_params["view"] = "lsrw"
            st.query_params["mod"] = "speaking"
            st.rerun()

    st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)

    # Row 2: Duel Bridges
    st.markdown("**⚔️ Goethe B1 Duels:**")
    col_d1, col_d2 = st.columns(2, gap="medium")
    with col_d1:
        if st.button(f"🎯 Practice '{chosen_topic}' in Translation Duel ➔", use_container_width=True, key="btn_bridge_duel"):
            st.session_state.app_view = "quiz"
            st.session_state.active_topic = chosen_topic
            storage.set_player_current_topic(pid, chosen_topic, category="pronoun")
            st.query_params["view"] = "quiz"
            st.rerun()

    with col_d2:
        if st.button(f"🏷️ Practice in Gender Duel (Der • Die • Das) ➔", use_container_width=True, key="btn_bridge_gender"):
            st.session_state.app_view = "gender"
            st.query_params["view"] = "gender"
            st.rerun()

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    if st.button("➕ Neues Thema lernen (కొత్త అంశం / ಹೊಸ ವಿಷಯ)", use_container_width=True, key="btn_flow_new_topic_main"):
        st.session_state.pop("learn_active_topic", None)
        st.session_state.pop("learn_depth", None)
        st.session_state.pop("learn_explanation_text", None)
        st.session_state.lsrw_loop_queue = []
        st.session_state.lsrw_loop_topic = None
        st.rerun()
