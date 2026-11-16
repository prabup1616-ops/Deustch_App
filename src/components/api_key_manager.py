"""
API Key Manager Component for German Goethe B1 Prep Hub.
Implements Bring-Your-Own-Key (BYOK) with a shared fallback demo mode and rate-limit disclaimer.
"""
import streamlit as st
import storage


def render_api_key_banner():
    """
    Renders a compact top banner indicating whether a custom or shared key is in use,
    with a button to change or switch keys.
    """
    active_key = storage.get_gemini_api_key()
    if not active_key:
        return

    is_shared = storage.is_using_shared_key()

    col_info, col_action = st.columns([4, 1])
    with col_info:
        if is_shared:
            st.markdown("""
            <div style="background: #fefce8; border: 1px solid #fef08a; border-radius: 8px; padding: 6px 12px; font-size: 0.85rem; color: #854d0e; display: flex; align-items: center; gap: 8px;">
                <span>🟡</span>
                <span><strong>Entwickler-Schlüssel aktiv (Shared Demo Mode):</strong> Geteilte Rate-Limits. Kann bei gleichzeitigen Nutzern gedrosselt werden.</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            masked = active_key[:6] + "••••••••" if len(active_key) > 6 else "••••••"
            st.markdown(f"""
            <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 6px 12px; font-size: 0.85rem; color: #166534; display: flex; align-items: center; gap: 8px;">
                <span>🟢</span>
                <span><strong>Eigener API-Schlüssel aktiv:</strong> <code>{masked}</code> (Volles, privates Kontingent)</span>
            </div>
            """, unsafe_allow_html=True)

    with col_action:
        label = "🔑 Schlüssel ändern" if not is_shared else "🔑 Eigenen Key nutzen"
        if st.button(label, key="btn_toggle_api_key_settings", use_container_width=True):
            st.session_state["show_api_key_dialog"] = not st.session_state.get("show_api_key_dialog", False)
            st.rerun()

    if st.session_state.get("show_api_key_dialog", False):
        with st.expander("⚙️ API-Schlüssel Einstellungen verwalten", expanded=True):
            render_api_key_prompt(is_dialog=True)


def render_api_key_prompt(context_title: str = "Dieses KI-Modul", is_dialog: bool = False):
    """
    Renders the full API Key selection card:
    1. Custom Key input (Recommended) with free key generation guide for Gemini and other AIs.
    2. Shared Creator Key (Demo Mode) with explicit choking/throttling disclaimer.
    """
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
                border-radius: 16px; padding: 22px 24px; color: white; margin-bottom: 20px; box-shadow: 0 8px 24px rgba(59,130,246,0.2);">
        <h3 style="margin: 0 0 6px 0; color: #ffffff;">🔑 KI-Aktivierung / AI API Key Setup</h3>
        <p style="margin: 0; font-size: 0.92rem; color: #bfdbfe;">
            Für <strong>{context_title}</strong> (zweisprachige Grammatikerklärungen auf Telugu/Kannada, Schreibkorrektur und Hörprüfungen) wird ein KI-Schlüssel benötigt.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_user, col_shared = st.columns([1, 1], gap="medium")

    # ==========================================================================
    # OPTION 1: USER'S OWN KEY (RECOMMENDED)
    # ==========================================================================
    with col_user:
        st.markdown("""
        <div style="border: 2px solid #22c55e; border-radius: 12px; padding: 16px 18px; background: #f0fdf4;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 1.1rem; font-weight: 800; color: #15803d;">Option 1: Eigener API-Schlüssel</span>
                <span style="background: #dcfce7; color: #166534; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 999px;">EMPFOHLEN</span>
            </div>
            <p style="font-size: 0.86rem; color: #1e293b; margin-bottom: 8px;">
                Nutzen Sie Ihr persönliches Kontingent. Ihr Schlüssel wird nur temporär in Ihrer aktuellen Sitzung gespeichert und ist für niemanden sichtbar.
            </p>
        </div>
        """, unsafe_allow_html=True)

        user_input_key = st.text_input(
            "Gemini API-Schlüssel hier einfügen (Paste your API key):",
            type="password",
            placeholder="AIzaSy...",
            key="input_user_custom_gemini_key"
        )

        if st.button("🚀 Eigenen Schlüssel aktivieren (Save & Continue)", type="primary", use_container_width=True, key="btn_save_user_key"):
            clean_k = user_input_key.strip()
            if not clean_k:
                st.warning("Bitte fügen Sie einen gültigen API-Schlüssel ein!")
            else:
                st.session_state["user_gemini_api_key"] = clean_k
                st.session_state["use_shared_creator_key"] = False
                st.session_state["show_api_key_dialog"] = False
                st.success("✅ Eigener API-Schlüssel erfolgreich aktiviert!")
                st.rerun()

        # Step-by-step help guide for different AIs
        with st.expander("❓ Wie erhalte ich einen kostenlosen API-Schlüssel? (How to get API keys)"):
            st.markdown("""
            ### 🌐 1. Google Gemini (100% Kostenlos — Für diese App benötigt)
            * **Direktlink:** [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
            * **Schritte:**
              1. Mit Ihrem Google-Konto anmelden.
              2. Auf **"Create API key"** klicken.
              3. Den Schlüssel (`AIzaSy...`) kopieren und oben einfügen.
            * *Kostenlos: 15 Anfragen pro Minute dauerhaft gratis, keine Kreditkarte nötig.*

            ---

            ### 🔗 Weitere KI-Anbieter (Referenz):
            * **OpenAI (ChatGPT API):** [platform.openai.com/api-keys](https://platform.openai.com/api-keys) *(Erfordert Guthaben)*
            * **Anthropic (Claude API):** [console.anthropic.com](https://console.anthropic.com/) *(Erfordert Guthaben)*
            * **Groq Cloud (Llama 3):** [console.groq.com/keys](https://console.groq.com/keys) *(Kostenlos mit Limit)*

            > 💡 **Hinweis:** Diese App verwendet das Google Gemini Modell, da es als einziges Modell nativ **Telugu (తెలుగు)**, **Kannada (ಕನ್ನಡ)** und deutsches Goethe-B1-Prüfungswissen kostenlos und fehlerfrei beherrscht.
            """)

    # ==========================================================================
    # OPTION 2: SHARED CREATOR KEY (FALLBACK DEMO)
    # ==========================================================================
    with col_shared:
        st.markdown("""
        <div style="border: 2px solid #f59e0b; border-radius: 12px; padding: 16px 18px; background: #fffbeb;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 1.1rem; font-weight: 800; color: #b45309;">Option 2: Entwickler-Schlüssel</span>
                <span style="background: #fef3c7; color: #92400e; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 999px;">DEMO-MODUS</span>
            </div>
            <p style="font-size: 0.86rem; color: #1e293b; margin-bottom: 8px;">
                Testen Sie die App sofort mit dem bereitgestellten Entwickler-Schlüssel, ohne einen eigenen Account anzulegen.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background: #fef2f2; border: 2px solid #ef4444; border-radius: 10px; padding: 12px 14px; margin: 12px 0; font-size: 0.85rem; color: #991b1b; line-height: 1.55;">
            ⚠️ <strong>Haftungsausschluss / Disclaimer:</strong><br>
            Dieser Schlüssel wird von allen Besuchern der Website weltweit gemeinsam genutzt. 
            Wenn mehrere Nutzer gleichzeitig lernen, kann das Ratenlimit <strong>jederzeit überlastet werden (Choking / HTTP 429 Too Many Requests)</strong>.<br>
            <em>Falls Anfragen fehlschlagen, wechseln Sie bitte zu Option 1 (eigener kostenloser Schlüssel).</em>
        </div>
        """, unsafe_allow_html=True)

        if st.button("⚡ Entwickler-Schlüssel nutzen (Demo Mode)", use_container_width=True, key="btn_use_shared_creator_key"):
            st.session_state["user_gemini_api_key"] = ""
            st.session_state["use_shared_creator_key"] = True
            st.session_state["show_api_key_dialog"] = False
            st.info("ℹ️ Entwickler-Schlüssel für diese Sitzung aktiviert.")
            st.rerun()

    st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)
