import streamlit.components.v1 as components
from src.config import load_template


def trigger_confetti_and_sound(score: int, total: int = 5):
    """Canvas particle confetti burst + Web Audio sound effect"""
    is_perfect = (score == total)
    particle_count = 150 if is_perfect else 80
    freq_start = 587.33 if is_perfect else 440.0
    freq_end = 880.0 if is_perfect else 554.37

    tmpl = load_template("confetti.html")
    html_code = (
        tmpl.replace("{{particle_count}}", str(particle_count))
            .replace("{{freq_start}}", str(freq_start))
            .replace("{{freq_end}}", str(freq_end))
    )

    components.html(html_code, height=0)
