import streamlit as st
from src.config import load_template


def render_grammar_chart():
    """Renders the Possessivartikel Master Chart cleanly using external HTML template."""
    html_code = load_template("grammar_chart.html")
    st.html(html_code)
