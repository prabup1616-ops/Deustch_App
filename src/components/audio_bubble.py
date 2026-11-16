import json
import streamlit.components.v1 as components
from src.config import load_template


def render_voice_bubble(spoken_text: str, button_id: str, auto_play: bool = False):
    """
    Renders Frau Wagner's audio bubble in Blind Audio Mode.
    No German text is exposed. Loads external HTML template.
    """
    safe_text = json.dumps(spoken_text)
    auto_trigger = f"""
        setTimeout(() => {{
            playAudio_{button_id}();
        }}, 450);
    """ if auto_play else ""

    tmpl = load_template("voice_bubble.html")
    html_code = (
        tmpl.replace("{{button_id}}", button_id)
            .replace("{{safe_text}}", safe_text)
            .replace("{{auto_trigger}}", auto_trigger)
    )

    components.html(html_code, height=135)


def tts_button(text: str, button_id: str):
    """Interactive German Speech Synthesis button"""
    safe_text = json.dumps(text)
    html_code = f"""
    <div style="display: inline-block; margin-top: 4px;">
        <button id="btn_{button_id}" onclick="playGerman()" style="
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            border: 1px solid #cbd5e1;
            border-radius: 10px;
            padding: 7px 16px;
            font-size: 13px;
            font-weight: 700;
            color: #1e293b;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 7px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.04);
            transition: all 0.2s;
        " onmouseover="this.style.transform='scale(1.04)';" onmouseout="this.style.transform='scale(1)';">
            🔊 Hören (German Audio)
        </button>
        <script>
            function playGerman() {{
                if ('speechSynthesis' in window) {{
                    window.speechSynthesis.cancel();
                    var utter = new SpeechSynthesisUtterance({safe_text});
                    utter.lang = 'de-DE';
                    utter.rate = 0.88;
                    window.speechSynthesis.speak(utter);
                }} else {{
                    alert('Audio speech synthesis not supported in this browser.');
                }}
            }}
        </script>
    </div>
    """
    components.html(html_code, height=45)
