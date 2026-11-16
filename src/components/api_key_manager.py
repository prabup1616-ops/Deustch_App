"""
API Key Manager Component for German Goethe B1 Prep Hub.
Implements Bring-Your-Own-Key (BYOK) with a shared fallback demo mode and rate-limit disclaimer.
All user-facing text in clear English.
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
                <span><strong>Creator Key Active (Shared Demo Mode):</strong> Shared rate limits apply. May be throttled when multiple users practice.</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            masked = active_key[:6] + "••••••••" if len(active_key) > 6 else "••••••"
            st.markdown(f"""
            <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 6px 12px; font-size: 0.85rem; color: #166534; display: flex; align-items: center; gap: 8px;">
                <span>🟢</span>
                <span><strong>Personal API Key Active:</strong> <code>{masked}</code> (Full private unthrottled quota)</span>
            </div>
            """, unsafe_allow_html=True)

    with col_action:
        label = "🔑 Change Key" if not is_shared else "🔑 Use Your Own Key"
        if st.button(label, key="btn_toggle_api_key_settings", use_container_width=True):
            st.session_state["show_api_key_dialog"] = not st.session_state.get("show_api_key_dialog", False)
            st.rerun()

    if st.session_state.get("show_api_key_dialog", False):
        with st.expander("⚙️ Manage AI API Key Settings", expanded=True):
            render_api_key_prompt(is_dialog=True)


def render_api_key_prompt(context_title: str = "This AI Module", is_dialog: bool = False):
    """
    Renders the full API Key selection card:
    1. Custom Key input (Recommended) with free key generation guide for Gemini and other AIs.
    2. Shared Creator Key (Demo Mode) with explicit choking/throttling disclaimer.
    All in clear English.
    """
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
                border-radius: 16px; padding: 22px 24px; color: white; margin-bottom: 20px; box-shadow: 0 8px 24px rgba(59,130,246,0.2);">
        <h3 style="margin: 0 0 6px 0; color: #ffffff;">🔑 AI Activation & API Key Setup</h3>
        <p style="margin: 0; font-size: 0.92rem; color: #bfdbfe;">
            To power <strong>{context_title}</strong> (bilingual Telugu/Kannada grammar explanations, writing evaluations, and audio exams), an AI key is required.
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
                <span style="font-size: 1.1rem; font-weight: 800; color: #15803d;">Option 1: Your Own API Key</span>
                <span style="background: #dcfce7; color: #166534; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 999px;">RECOMMENDED</span>
            </div>
            <p style="font-size: 0.86rem; color: #1e293b; margin-bottom: 8px;">
                Enjoy your own private, unthrottled quota. Your key is stored only temporarily in your current browser session and is never saved or visible to anyone else.
            </p>
        </div>
        """, unsafe_allow_html=True)

        user_input_key = st.text_input(
            "Paste your Gemini API Key here:",
            type="password",
            placeholder="AIzaSy...",
            key="input_user_custom_gemini_key"
        )

        if st.button("🚀 Activate My Own Key (Save & Continue)", type="primary", use_container_width=True, key="btn_save_user_key"):
            clean_k = user_input_key.strip()
            if not clean_k:
                st.warning("Please paste a valid API key!")
            else:
                st.session_state["user_gemini_api_key"] = clean_k
                st.session_state["use_shared_creator_key"] = False
                st.session_state["show_api_key_dialog"] = False
                st.success("✅ Personal API key activated successfully!")
                st.rerun()

        # Step-by-step help guide for different AIs
        with st.expander("❓ How to get a 100% Free Gemini API Key in 30 seconds"):
            st.markdown("""
            ### 🌐 1. Google Gemini (100% Free — Required for this App)
            * **Direct Link:** [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
            * **Steps:**
              1. Sign in with any regular Google account.
              2. Click the blue **"Create API key"** button.
              3. Copy the generated key (`AIzaSy...`) and paste it in the box above.
            * *Free Quota: 15 requests per minute permanently free — no credit card or billing required.*

            ---

            ### 🔗 Other AI Providers (Reference):
            * **OpenAI (ChatGPT API):** [platform.openai.com/api-keys](https://platform.openai.com/api-keys) *(Requires paid balance)*
            * **Anthropic (Claude API):** [console.anthropic.com](https://console.anthropic.com/) *(Requires paid balance)*
            * **Groq Cloud (Llama 3):** [console.groq.com/keys](https://console.groq.com/keys) *(Free with rate limits)*

            > 💡 **Why Google Gemini?** This application specifically uses the Google Gemini engine because it is the only model that natively provides flawless bilingual **Telugu (తెలుగు)** and **Kannada (ಕನ್ನಡ)** grammar translations alongside official Goethe B1 German exam training for free.
            """)

    # ==========================================================================
    # OPTION 2: SHARED CREATOR KEY (FALLBACK DEMO)
    # ==========================================================================
    with col_shared:
        st.markdown("""
        <div style="border: 2px solid #f59e0b; border-radius: 12px; padding: 16px 18px; background: #fffbeb;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 1.1rem; font-weight: 800; color: #b45309;">Option 2: Creator Key</span>
                <span style="background: #fef3c7; color: #92400e; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 999px;">DEMO MODE</span>
            </div>
            <p style="font-size: 0.86rem; color: #1e293b; margin-bottom: 8px;">
                Try out the app immediately using the creator's shared key without creating an account.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background: #fef2f2; border: 2px solid #ef4444; border-radius: 10px; padding: 12px 14px; margin: 12px 0; font-size: 0.85rem; color: #991b1b; line-height: 1.55;">
            ⚠️ <strong>DISCLAIMER & RATE-LIMIT NOTICE:</strong><br>
            This key is shared across all visitors worldwide. 
            If multiple users practice simultaneously, the free rate limit (15 requests/min) <strong>may be throttled, delayed, or choked (HTTP 429 Too Many Requests)</strong>.<br>
            <em>If generation fails or takes too long, please switch to Option 1 and use your own free personal key.</em>
        </div>
        """, unsafe_allow_html=True)

        if st.button("⚡ Use Creator Key (Shared Demo Mode)", use_container_width=True, key="btn_use_shared_creator_key"):
            st.session_state["user_gemini_api_key"] = ""
            st.session_state["use_shared_creator_key"] = True
            st.session_state["show_api_key_dialog"] = False
            st.info("ℹ️ Creator key activated for this session.")
            st.rerun()

    st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)
