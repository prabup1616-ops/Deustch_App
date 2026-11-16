import streamlit as st
from src.components import render_grammar_chart


def render_chart_view():
    """Renders the comprehensive Goethe B1 Grammar Reference Center with interactive topic selector."""
    default_topic = st.session_state.get("active_topic") or st.session_state.get("active_gender_topic") or "Possessivartikel"
    render_grammar_chart(default_topic=default_topic)
