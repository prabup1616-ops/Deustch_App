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

# 2. Inject External Modular CSS & Cloud Badge Suppressor
css_content = load_css()
if css_content:
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

# Cloud Badge Suppressor (Streamlit native popstate handles browser Back/Forward smoothly)
components.html("""
<script>
(function() {
    try {
        const topWin = (window.parent && window.parent.location) ? window.parent : window;
        
        // Suppress Streamlit Cloud bottom-right viewer badge & fork widget across frames
        function purgeCloudBadge() {
            try {
                const docs = [document];
                if (topWin && topWin.document && topWin.document !== document) {
                    docs.push(topWin.document);
                }
                docs.forEach(function(d) {
                    if (!d) return;
                    // Inject hiding stylesheet to parent document if missing
                    if (!d.getElementById('agy-hide-cloud-badge')) {
                        const style = d.createElement('style');
                        style.id = 'agy-hide-cloud-badge';
                        style.innerHTML = `
                            [class*="viewerBadge"],
                            [class*="styles_viewerBadge"],
                            .viewerBadge_container__1QSob,
                            .styles_viewerBadge__1yB5_,
                            .viewerBadge_link__1S137,
                            .viewerBadge_text__1JaDK,
                            [data-testid="manage-app-button"],
                            [data-testid="stToolbarActions"],
                            div[data-testid="stDecoration"],
                            #MainMenu,
                            footer {
                                display: none !important;
                                visibility: hidden !important;
                                opacity: 0 !important;
                                pointer-events: none !important;
                                height: 0 !important;
                                width: 0 !important;
                            }
                        `;
                        d.head && d.head.appendChild(style);
                    }
                    const badges = d.querySelectorAll('[class*="viewerBadge"], [data-testid="manage-app-button"], [class*="styles_viewerBadge"]');
                    badges.forEach(function(el) {
                        el.style.setProperty('display', 'none', 'important');
                        el.style.setProperty('visibility', 'hidden', 'important');
                    });
                });
            } catch(e) {}
        }
        purgeCloudBadge();
        setInterval(purgeCloudBadge, 600);
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
            if st.query_params.get("view") != "home":
                st.query_params["view"] = "home"
            if "mod" in st.query_params:
                del st.query_params["mod"]
            st.rerun()

# Sync query params with current navigation state (ONLY when view/mod actually changes to prevent history stack pollution)
target_view = st.session_state.app_view
if st.query_params.get("view") != target_view:
    st.query_params["view"] = target_view

if target_view == "lsrw":
    target_mod = st.session_state.get("lsrw_module", "hub")
    if st.query_params.get("mod") != target_mod:
        st.query_params["mod"] = target_mod
else:
    if "mod" in st.query_params:
        del st.query_params["mod"]

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
