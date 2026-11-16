import os
import time
from datetime import date

import streamlit as st
import streamlit.components.v1 as components

import storage
from src.config import APP_ICON, APP_TITLE, load_css
from src.views import (
    render_chart_view,
    render_home_view,
    render_quiz_view,
    render_gender_view,
    render_lsrw_view,
)

# 1. Page Configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Inject External Modular CSS & Browser History Popstate Controller
css_content = load_css()
if css_content:
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

# Browser Back/Forward (←/→) Button Controller
components.html("""
<script>
(function() {
    try {
        const topWin = (window.parent && window.parent.location) ? window.parent : window;
        if (!topWin._agy_popstate_ready) {
            topWin._agy_popstate_ready = true;
            topWin.addEventListener('popstate', function() {
                topWin.location.reload();
            });
        }
    } catch(e) {}
})();
</script>
""", height=0)


# 3. Session State Initialization
def init_session_state():
    # Sync view and module from URL query params (supports Browser Back/Forward and Refresh!)
    qp_view = st.query_params.get("view", None) or "home"
    qp_mod = st.query_params.get("mod", None) or "hub"

    last_view = st.session_state.get("_last_synced_view", None)
    last_mod = st.session_state.get("_last_synced_mod", None)

    if last_view is None:
        # First load from URL
        st.session_state.app_view = qp_view
        st.session_state.lsrw_module = qp_mod
        st.session_state._last_synced_view = qp_view
        st.session_state._last_synced_mod = qp_mod
    elif last_view != qp_view or last_mod != qp_mod:
        # Browser Back or Forward was clicked!
        st.session_state.app_view = qp_view
        st.session_state.lsrw_module = qp_mod
        st.session_state._last_synced_view = qp_view
        st.session_state._last_synced_mod = qp_mod
    else:
        # App-driven interaction: update tracking
        st.session_state._last_synced_view = st.session_state.get("app_view", "home")
        st.session_state._last_synced_mod = st.session_state.get("lsrw_module", "hub")

    # Pronoun Duel state
    if "quiz_stage" not in st.session_state:
        st.session_state.quiz_stage = "lobby"  # 'lobby', 'arena', 'results'

    if "player_name" not in st.session_state:
        st.session_state.player_name = ""

    if "player_avatar" not in st.session_state:
        st.session_state.player_avatar = "🦁"

    if "player_email" not in st.session_state:
        st.session_state.player_email = ""

    if "lang_choice" not in st.session_state:
        st.session_state.lang_choice = "te"

    if "pack_choice" not in st.session_state:
        st.session_state.pack_choice = date.today().isoformat()

    if "current_q_idx" not in st.session_state:
        st.session_state.current_q_idx = 0

    if "q_start_time" not in st.session_state:
        st.session_state.q_start_time = time.time()

    if "per_q_results" not in st.session_state:
        st.session_state.per_q_results = []

    # Gender Duel state
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

    if "gemini_api_key" not in st.session_state:
        st.session_state.gemini_api_key = storage.get_gemini_api_key()


init_session_state()

# 4. Top Navigation Bar
col_nav1, col_nav2 = st.columns([4, 1])
with col_nav1:
    st.markdown("### 🇩🇪 German Goethe-Zertifikat B1 Hub")
with col_nav2:
    if st.session_state.app_view != "home":
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state.app_view = "home"
            st.query_params["view"] = "home"
            st.query_params.pop("mod", None)
            st.rerun()

# Sync query params with current navigation state
st.query_params["view"] = st.session_state.app_view
if st.session_state.app_view == "lsrw":
    st.query_params["mod"] = st.session_state.get("lsrw_module", "hub")
else:
    st.query_params.pop("mod", None)

# 5. Route to Views
if st.session_state.app_view == "home":
    render_home_view()
elif st.session_state.app_view == "quiz":
    render_quiz_view()
elif st.session_state.app_view == "gender":
    render_gender_view()
elif st.session_state.app_view == "lsrw":
    render_lsrw_view()
elif st.session_state.app_view == "chart":
    render_chart_view()
