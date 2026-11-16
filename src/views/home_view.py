import streamlit as st


def render_home_view():
    """Renders the main Exam Portal Dashboard with Practice Arenas, Speaking & Modules."""
    st.markdown("""
    <div class="home-hero">
        <h1>🇩🇪 Goethe-Zertifikat B1 Hub</h1>
        <p>Your Complete Exam Preparation & Competition Platform with Telugu & Kannada Support</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🏆 Active Practice & Competition Arenas")
    col1, col2 = st.columns(2, gap="medium")

    # 1. Pronoun Duel (Possessivartikel)
    with col1:
        st.markdown("""<div class="module-card unlocked">
<div>
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
<span style="font-size: 2.5rem;">🎯</span>
<span style="background: #dcfce7; color: #15803d; font-weight: 700; font-size: 0.82rem; padding: 4px 10px; border-radius: 999px;">
● ACTIVE / OPEN
</span>
</div>
<h3 style="margin: 0; color: #1e3a8a;">Pronoun Duel</h3>
<p style="font-size: 0.9rem; color: #475569; margin: 8px 0 16px 0;">
162 Goethe B1 Questions covering <strong>Possessivartikel</strong> (mein/dein/sein/ihr/unser). 50s timer per question & dedicated pronoun scoreboard.
</p>
</div>
</div>""", unsafe_allow_html=True)
        if st.button("🚀 Enter Pronoun Duel ➔", type="primary", use_container_width=True, key="btn_home_duel"):
            st.session_state.app_view = "quiz"
            st.rerun()

    # 2. Gender Duel (Der / Die / Das)
    with col2:
        st.markdown("""<div class="module-card unlocked" style="border-top: 4px solid #059669;">
<div>
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
<span style="font-size: 2.5rem;">🏷️</span>
<span style="background: #ecfdf5; color: #047857; font-weight: 700; font-size: 0.82rem; padding: 4px 10px; border-radius: 999px;">
● NEW / ACTIVE
</span>
</div>
<h3 style="margin: 0; color: #065f46;">Gender Duel (Artikel)</h3>
<p style="font-size: 0.9rem; color: #475569; margin: 8px 0 16px 0;">
522 Nouns from official Goethe B1 Wortliste! Plural forms & English meanings included. Type <strong>der/die/das</strong> with 50s timer & dedicated gender scoreboard.
</p>
</div>
</div>""", unsafe_allow_html=True)
        if st.button("🏷️ Enter Gender Duel ➔", type="primary", use_container_width=True, key="btn_home_gender"):
            st.session_state.app_view = "gender"
            st.rerun()

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

    # 3. Goethe B1 Meisterstudio (Lernen • Lesen • Schreiben • Hören)
    st.markdown("""<div class="module-card unlocked" style="border-top: 4px solid #3b82f6;">
<div>
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
<span style="font-size: 2.5rem;">🎓📖✍️🎧</span>
<span style="background: #eff6ff; color: #1d4ed8; font-weight: 700; font-size: 0.82rem; padding: 4px 10px; border-radius: 999px;">
● EXAM & LEARNING STUDIO
</span>
</div>
<h3 style="margin: 0; color: #1e40af;">Goethe B1 Meisterstudio (Lernen • Lesen • Schreiben • Hören)</h3>
<p style="font-size: 0.9rem; color: #475569; margin: 8px 0 16px 0;">
Vollständiges Goethe-Zertifikat B1 Prüfungs- und Lernstudio mit zweisprachiger Grammatikerklärung auf <strong>Telugu (తెలుగు)</strong> und <strong>Kannada (ಕನ್ನಡ)</strong>, modularem Training und kumulativem Wiederholungszyklus.
</p>
</div>
</div>""", unsafe_allow_html=True)
    if st.button("🎧 Enter Goethe B1 Meisterstudio ➔", type="primary", use_container_width=True, key="btn_home_lsrw"):
        st.session_state.app_view = "lsrw"
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📚 Reference & Exam Preparation Modules")
    col_ref1, col_ref2, col_ref3, col_ref4 = st.columns(4, gap="medium")

    # Grammar Reference Chart
    with col_ref1:
        st.markdown("""<div class="module-card unlocked">
<div>
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
<span style="font-size: 2.2rem;">📖</span>
<span style="background: #e0f2fe; color: #0284c7; font-weight: 700; font-size: 0.75rem; padding: 3px 8px; border-radius: 999px;">
REFERENCE
</span>
</div>
<h4 style="margin: 0; color: #1e3a8a;">Grammar Chart</h4>
<p style="font-size: 0.85rem; color: #475569; margin: 6px 0 12px 0;">
Complete color-coded Possessivartikel table covering Nom, Akk, Dat & Gen.
</p>
</div>
</div>""", unsafe_allow_html=True)
        if st.button("📖 View Chart ➔", use_container_width=True, key="btn_home_chart"):
            st.session_state.app_view = "chart"
            st.rerun()

    # Reading (Lesen)
    with col_ref2:
        st.markdown("""<div class="module-card unlocked">
<div>
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
<span style="font-size: 2.2rem;">📑</span>
<span style="background: #dbeafe; color: #1d4ed8; font-weight: 700; font-size: 0.75rem; padding: 3px 8px; border-radius: 999px;">
IN LSRW
</span>
</div>
<h4 style="margin: 0; color: #1e40af;">Reading (Lesen)</h4>
<p style="font-size: 0.85rem; color: #475569; margin: 6px 0 12px 0;">
Goethe B1 Reading parts 1 to 5: Blog posts and news articles with questions.
</p>
</div>
</div>""", unsafe_allow_html=True)
        if st.button("📑 Practice Lesen ➔", use_container_width=True, key="btn_home_lesen"):
            st.session_state.app_view = "lsrw"
            st.rerun()

    # Writing (Schreiben)
    with col_ref3:
        st.markdown("""<div class="module-card unlocked">
<div>
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
<span style="font-size: 2.2rem;">✍️</span>
<span style="background: #dbeafe; color: #1d4ed8; font-weight: 700; font-size: 0.75rem; padding: 3px 8px; border-radius: 999px;">
IN LSRW
</span>
</div>
<h4 style="margin: 0; color: #1e40af;">Writing (Schreiben)</h4>
<p style="font-size: 0.85rem; color: #475569; margin: 6px 0 12px 0;">
Formal letters, opinion essays, and apologies evaluated with AI grammar feedback.
</p>
</div>
</div>""", unsafe_allow_html=True)
        if st.button("✍️ Practice Schreiben ➔", use_container_width=True, key="btn_home_schreiben"):
            st.session_state.app_view = "lsrw"
            st.rerun()

    # Listening (Hören)
    with col_ref4:
        st.markdown("""<div class="module-card unlocked">
<div>
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
<span style="font-size: 2.2rem;">🎧</span>
<span style="background: #dbeafe; color: #1d4ed8; font-weight: 700; font-size: 0.75rem; padding: 3px 8px; border-radius: 999px;">
IN LSRW
</span>
</div>
<h4 style="margin: 0; color: #1e40af;">Listening (Hören)</h4>
<p style="font-size: 0.85rem; color: #475569; margin: 6px 0 12px 0;">
Public announcements, radio discussions, and audio comprehension tests.
</p>
</div>
</div>""", unsafe_allow_html=True)
        if st.button("🎧 Practice Hören ➔", use_container_width=True, key="btn_home_hoeren"):
            st.session_state.app_view = "lsrw"
            st.rerun()
