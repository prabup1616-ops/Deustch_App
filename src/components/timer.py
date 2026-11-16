import time
import streamlit.components.v1 as components
from src.config import load_template


def render_50sec_timer(curr_idx: int, q_start_time: float):
    """
    Dedicated 50-second timer strictly per question.
    Loads external HTML template and resets on every question transition (curr_idx).
    """
    now = time.time()
    elapsed = max(0.0, now - q_start_time)
    remaining = max(0.0, 50.0 - elapsed)
    init_pct = max(0.0, min(100.0, (remaining / 50.0) * 100.0))

    tmpl = load_template("timer.html")
    html_code = (
        tmpl.replace("{{curr_idx}}", str(curr_idx))
            .replace("{{curr_num}}", str(curr_idx + 1))
            .replace("{{remaining}}", f"{remaining:.1f}")
            .replace("{{remaining_int}}", str(int(remaining)))
            .replace("{{init_pct}}", f"{init_pct:.1f}")
    )

    components.html(html_code, height=72)
