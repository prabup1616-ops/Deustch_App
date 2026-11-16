import streamlit as st
from src.components import render_grammar_chart


def render_chart_view():
    """Renders the full Goethe B1 Possessivartikel Master Chart."""
    st.header("📖 Possessivartikel Master Chart (Goethe B1)")
    st.caption("Color-coded reference for every case, gender, and personal pronoun.")
    render_grammar_chart()
