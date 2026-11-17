"""
Phrase Loader Component.
Renders an elegant, 30%-width floating card centered on the screen.
Allows the background page to remain fully scrollable and visible (softly blurred).
Features a cancel button, 25-second rotation, and guaranteed clean DOM injection
via components.html() so raw HTML or markdown code is NEVER shown to the user.
"""

import json
import random
import os
import streamlit.components.v1 as components
from src.config import BASE_DIR, PHRASES_FILE


def load_german_phrases():
    """Loads catchy German phrases and fixed expressions."""
    if os.path.exists(PHRASES_FILE):
        try:
            with open(PHRASES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def dismiss_phrase_loader():
    """Removes any existing phrase loading overlay from the parent page."""
    dismiss_js = """<script>
(function() {
    try {
        const pDoc = (window.parent && window.parent.document) ? window.parent.document : document;
        const ov = pDoc.getElementById('lsrw_phrase_overlay_root');
        if (ov) ov.remove();
    } catch(e) {}
})();
</script>"""
    components.html(dismiss_js, height=0)


def render_phrase_loader(status_text: str = "Prüfungsunterlagen werden vorbereitet..."):
    """
    Renders an animated floating learning window occupying ~30% of the screen,
    centered in the viewport.
    Background is softly blurred and remains fully scrollable.
    Each phrase displays for 25 seconds. No counters shown.
    Includes a cancel button.
    Injected directly into parent DOM so it CANNOT be converted into markdown code blocks.
    """
    phrases = load_german_phrases()
    if not phrases:
        return

    init_p = random.choice(phrases)
    safe_phrases_json = json.dumps(phrases, ensure_ascii=False)
    safe_init_phrase = json.dumps(init_p.get("phrase_de", ""), ensure_ascii=False)
    safe_init_meaning = json.dumps(init_p.get("meaning_en", ""), ensure_ascii=False)
    safe_init_example = json.dumps(init_p.get("example_de", ""), ensure_ascii=False)
    safe_status = json.dumps(status_text, ensure_ascii=False)

    component_code = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin: 0; padding: 0;">
<script>
(function() {{
    try {{
        const pDoc = (window.parent && window.parent.document) ? window.parent.document : document;
        const phrases = {safe_phrases_json};

        // Remove any prior instance
        const old = pDoc.getElementById('lsrw_phrase_overlay_root');
        if (old) old.remove();

        // 1. Create Overlay container
        const overlay = pDoc.createElement('div');
        overlay.id = 'lsrw_phrase_overlay_root';
        overlay.style.cssText = [
            'position: fixed !important',
            'top: 0 !important',
            'left: 0 !important',
            'width: 100vw !important',
            'height: 100vh !important',
            'z-index: 2147483647 !important',
            'background: rgba(15, 23, 42, 0.45) !important',
            'backdrop-filter: blur(5px) !important',
            '-webkit-backdrop-filter: blur(5px) !important',
            'display: flex !important',
            'align-items: center !important',
            'justify-content: center !important',
            'pointer-events: none !important', /* Allows user to scroll the underlying page */
            'box-sizing: border-box !important',
            'font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important'
        ].join(';');

        // 2. Build Card HTML
        overlay.innerHTML = `
        <div id="lsrw_phrase_card" style="
            pointer-events: auto !important;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
            border: 2px solid #3b82f6 !important;
            border-radius: 18px !important;
            padding: 22px 26px !important;
            width: 32vw !important;
            max-width: 490px !important;
            min-width: 320px !important;
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.65), 0 0 30px rgba(59, 130, 246, 0.35) !important;
            color: #ffffff !important;
            box-sizing: border-box !important;
        ">
            <!-- Header -->
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; padding-bottom: 10px; border-bottom: 1px solid rgba(255, 255, 255, 0.12);">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 10px; height: 10px; background-color: #3b82f6; border-radius: 50%; box-shadow: 0 0 8px #60a5fa;"></div>
                    <span style="font-weight: 800; font-size: 0.85rem; color: #93c5fd; letter-spacing: 0.5px;">💡 DEUTSCHE REDEWENDUNGEN</span>
                </div>
                <button type="button" id="lsrw_btn_dismiss" style="
                    background: rgba(239, 68, 68, 0.15);
                    border: 1px solid #ef4444;
                    color: #fca5a5;
                    font-size: 0.78rem;
                    font-weight: 700;
                    border-radius: 8px;
                    padding: 3px 10px;
                    cursor: pointer;
                ">✕ Abbrechen</button>
            </div>

            <!-- Body -->
            <div style="min-height: 115px; display: flex; flex-direction: column; justify-content: center;">
                <div id="lsrw_phrase_title" style="
                    font-size: 1.55rem;
                    font-weight: 900;
                    color: #fde047;
                    letter-spacing: 0.4px;
                    margin-bottom: 6px;
                    line-height: 1.25;
                    transition: opacity 0.35s ease;
                ">${{{safe_init_phrase}}}</div>

                <div id="lsrw_phrase_scenario" style="
                    font-size: 0.88rem;
                    color: #94a3b8;
                    margin-bottom: 10px;
                    line-height: 1.4;
                    transition: opacity 0.35s ease;
                ">🇬🇧 <em>${{{safe_init_meaning}}}</em></div>

                <div style="
                    background: rgba(255, 255, 255, 0.05);
                    border-left: 3px solid #3b82f6;
                    border-radius: 6px;
                    padding: 8px 12px;
                    margin-bottom: 12px;
                ">
                    <span style="font-size: 0.72rem; color: #60a5fa; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px;">🇩🇪 BEISPIELSATZ:</span>
                    <div id="lsrw_phrase_example" style="font-size: 0.95rem; color: #f8fafc; font-style: italic; margin-top: 2px; line-height: 1.35; transition: opacity 0.35s ease;">
                        "${{{safe_init_example}}}"
                    </div>
                </div>
            </div>

            <!-- 25-Second Animated Progress Bar -->
            <div style="width: 100%; height: 4px; background: rgba(255, 255, 255, 0.1); border-radius: 2px; overflow: hidden; margin-top: 10px;">
                <div id="lsrw_phrase_bar" style="height: 100%; width: 0%; background: linear-gradient(90deg, #3b82f6, #60a5fa); border-radius: 2px;"></div>
            </div>

            <!-- Footer -->
            <div style="display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 12px; font-size: 0.8rem; color: #94a3b8;">
                <span>⏳</span>
                <span>${{{safe_status}}}</span>
            </div>
        </div>
        `;

        pDoc.body.appendChild(overlay);

        // Cancel button click handler
        const dismissBtn = overlay.querySelector('#lsrw_btn_dismiss');
        if (dismissBtn) {{
            dismissBtn.onclick = function() {{
                overlay.remove();
            }};
        }}

        // 25-second animation controller
        const DURATION = 25000;
        let idx = Math.floor(Math.random() * phrases.length);
        const bar = overlay.querySelector('#lsrw_phrase_bar');

        function startBarAnimation() {{
            if (!bar) return;
            bar.style.transition = 'none';
            bar.style.width = '0%';
            setTimeout(() => {{
                bar.style.transition = 'width 25s linear';
                bar.style.width = '100%';
            }}, 50);
        }}
        startBarAnimation();

        function rotate() {{
            if (!overlay || !overlay.parentNode) return;
            const titleEl = overlay.querySelector('#lsrw_phrase_title');
            const scenEl = overlay.querySelector('#lsrw_phrase_scenario');
            const exEl = overlay.querySelector('#lsrw_phrase_example');

            if (!titleEl) return;
            titleEl.style.opacity = '0';
            if (scenEl) scenEl.style.opacity = '0';
            if (exEl) exEl.style.opacity = '0';

            setTimeout(() => {{
                idx = (idx + 1) % phrases.length;
                const nextItem = phrases[idx];
                titleEl.innerText = nextItem.phrase_de;
                if (scenEl) scenEl.innerHTML = '🇬🇧 <em>' + nextItem.meaning_en + '</em>';
                if (exEl) exEl.innerText = '"' + nextItem.example_de + '"';

                titleEl.style.opacity = '1';
                if (scenEl) scenEl.style.opacity = '1';
                if (exEl) exEl.style.opacity = '1';

                startBarAnimation();
            }}, 350);
        }}

        const timer = setInterval(rotate, DURATION);

        // Cleanup timer if overlay is removed
        const observer = new MutationObserver(() => {{
            if (!pDoc.getElementById('lsrw_phrase_overlay_root')) {{
                clearInterval(timer);
                observer.disconnect();
            }}
        }});
        observer.observe(pDoc.body, {{ childList: true }});

    }} catch(e) {{
        console.warn('LSRW phrase loader injection:', e);
    }}
}})();
</script>
</body>
</html>"""

    components.html(component_code, height=0)
