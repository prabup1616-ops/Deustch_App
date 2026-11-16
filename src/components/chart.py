"""
Grammar Chart & Reference Center for German Goethe B1 Hub.
Provides visual, color-coded grammar reference charts for every duel topic:
1. Possessivartikel across all cases and genders
2. Weak Masculine Declination (N-Deklination) with cases, articles, and noun endings
3. Relativsätze (Relative Clauses & Relative Pronouns matrix)
4. Passiv (Vorgangspassiv in Präsens, Präteritum, Perfekt & Modalverben)
5. Konjunktiv II (Wünsche, Höflichkeit & Ratschläge)
6. Nebensätze mit Konjunktionen (weil, obwohl, dass, wenn vs. denn/deshalb)
7. Adjektivdeklination (Typ 1, Typ 2, Typ 3)
8. Dynamic Community Topics unlocked by learners in the Duels
"""
import streamlit as st
import storage
from src.config import load_template


def render_grammar_chart(default_topic: str = None):
    """
    Renders the interactive Grammar Reference Center with a topic selector
    covering all topics presented in the Duels.
    """
    community_topics = storage.get_community_topics(category="pronoun")
    core_topics = [
        "Possessivartikel (Possessive Pronouns)",
        "Weak Masculine Declination (N-Deklination)",
        "Relativsätze (Relative Clauses & Pronouns)",
        "Passiv (Vorgangspassiv)",
        "Konjunktiv II (Wünsche & Ratschläge)",
        "Nebensätze mit Konjunktionen (weil, obwohl, dass)",
        "Adjektivdeklination (Typ 1, 2, 3)"
    ]

    # Combine core topics and any custom topics unlocked by learners
    all_options = list(core_topics)
    for t in community_topics:
        # Avoid duplicate labels
        if not any(t.lower() in opt.lower() or opt.lower() in t.lower() for opt in all_options):
            all_options.append(t)

    # Determine default index
    def_idx = 0
    if default_topic:
        for idx, opt in enumerate(all_options):
            if default_topic.lower() in opt.lower() or opt.lower() in default_topic.lower():
                def_idx = idx
                break

    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%); padding: 18px 24px; border-radius: 14px; color: white; margin-bottom: 20px;">
        <h2 style="margin: 0; color: white; font-size: 1.6rem;">📖 Goethe B1 Grammar Reference & Master Charts</h2>
        <p style="margin: 6px 0 0 0; color: #bfdbfe; font-size: 0.95rem;">
            Color-coded structural rules, case declinations, conjunctions, and bilingual annotations (Telugu & Kannada) for every Duel topic.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_sel, col_info = st.columns([2, 1], gap="medium")
    with col_sel:
        selected_topic = st.selectbox(
            "Select Grammar Topic / ವ್ಯಾಕರಣ ವಿಷಯವನ್ನು ಆಯ್ಕೆಮಾಡಿ / వ్యాకరణ అంశాన్ని ఎంచుకోండి:",
            options=all_options,
            index=def_idx,
            key="grammar_chart_topic_selector",
            help="Switch between topics to view structural rules, case declinations, and formulas."
        )

    with col_info:
        st.markdown(f"""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px 14px; margin-top: 18px;">
            <span style="font-size: 0.85rem; color: #64748b;">Active Duel Reference:</span><br>
            <strong style="color: #1e293b; font-size: 0.92rem;">{selected_topic.split('(')[0].strip()}</strong>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Route to specific topic chart
    topic_lower = selected_topic.lower()

    if "weak masculine" in topic_lower or "n-deklination" in topic_lower:
        _render_n_deklination_chart()
    elif "relativ" in topic_lower:
        _render_relativsatz_chart()
    elif "passiv" in topic_lower:
        _render_passiv_chart()
    elif "konjunktiv" in topic_lower:
        _render_konjunktiv_chart()
    elif "konjunktion" in topic_lower or "nebensatz" in topic_lower:
        _render_nebensatz_chart()
    elif "adjektiv" in topic_lower:
        _render_adjektiv_chart()
    elif "possessiv" in topic_lower:
        _render_possessiv_chart()
    else:
        _render_custom_community_chart(selected_topic)


# ==============================================================================
# 1. POSSESSIVARTIKEL MASTER CHART
# ==============================================================================

def _render_possessiv_chart():
    st.markdown("### 🏷️ Possessivartikel Master Chart (All Cases & Genders)")
    st.caption("Color-coded reference for every case, gender, and personal pronoun.")

    html_code = load_template("grammar_chart.html")
    if html_code:
        st.html(html_code)
    else:
        st.info("Template grammar_chart.html loaded.")

    with st.expander("💡 Key Rules & Exam Tips for Possessivartikel"):
        st.markdown("""
        * **Akkusativ Maskulin:** Always takes **-en** (`meinen`, `deinen`, `seinen`, `ihren`, `unseren`, `euren`).
        * **Dativ:** Maskulin/Neutrum take **-em** (`meinem`); Feminin takes **-er** (`meiner`); Plural takes **-en** + adds **-n** to the noun (`meinen Freunden`).
        * **Genitiv:** Maskulin/Neutrum take **-es** + adds **-s/-es** to noun (`meines Bruders`); Feminin/Plural take **-er** (`meiner Schwester`).
        """)


# ==============================================================================
# 2. WEAK MASCULINE DECLINATION (N-DEKLINATION)
# ==============================================================================

def _render_n_deklination_chart():
    st.markdown("### 🦁 Weak Masculine Declination (N-Deklination)")
    st.caption("Masculine nouns that take an extra <strong>-(e)n</strong> ending in all singular cases (Akkusativ, Dativ, Genitiv) except Nominativ.")

    st.markdown("""
    <div style="overflow-x: auto; margin: 16px 0;">
        <table style="width: 100%; border-collapse: collapse; text-align: center; font-size: 14px;">
            <thead>
                <tr style="background-color: #0f172a; color: white;">
                    <th style="padding: 12px; border: 1px solid #cbd5e1;">Kasus (Case)</th>
                    <th style="padding: 12px; border: 1px solid #cbd5e1;">Bestimmter Artikel</th>
                    <th style="padding: 12px; border: 1px solid #cbd5e1;">Unbestimmter Artikel</th>
                    <th style="padding: 12px; border: 1px solid #cbd5e1; background-color: #b45309;">Noun Ending</th>
                    <th style="padding: 12px; border: 1px solid #cbd5e1; background-color: #1e3a8a;">Beispiel: der Student</th>
                    <th style="padding: 12px; border: 1px solid #cbd5e1; background-color: #047857;">Beispiel: der Kollege</th>
                    <th style="padding: 12px; border: 1px solid #cbd5e1; background-color: #6d28d9;">Plural Form</th>
                </tr>
            </thead>
            <tbody>
                <tr style="background-color: #f8fafc; font-weight: bold;">
                    <td style="border: 1px solid #cbd5e1; font-weight: 800; color: #1e293b;">Nominativ (Subjekt)</td>
                    <td style="border: 1px solid #cbd5e1;">der</td>
                    <td style="border: 1px solid #cbd5e1;">ein</td>
                    <td style="border: 1px solid #cbd5e1; color: #64748b;">— (keine Endung)</td>
                    <td style="border: 1px solid #cbd5e1;">der <strong>Student</strong></td>
                    <td style="border: 1px solid #cbd5e1;">der <strong>Kollege</strong></td>
                    <td style="border: 1px solid #cbd5e1;">die <strong>Studenten / Kollegen</strong></td>
                </tr>
                <tr style="background-color: #fed7aa; font-weight: bold;">
                    <td style="border: 1px solid #cbd5e1; font-weight: 800; color: #9a3412;">Akkusativ (Objekt)</td>
                    <td style="border: 1px solid #cbd5e1; color: #b45309;">den</td>
                    <td style="border: 1px solid #cbd5e1; color: #b45309;">einen</td>
                    <td style="border: 1px solid #cbd5e1; color: #b45309; font-size: 1.1rem;">-(e)n</td>
                    <td style="border: 1px solid #cbd5e1; color: #b45309;">den <strong>Studenten</strong></td>
                    <td style="border: 1px solid #cbd5e1; color: #b45309;">den <strong>Kollegen</strong></td>
                    <td style="border: 1px solid #cbd5e1;">die <strong>Studenten / Kollegen</strong></td>
                </tr>
                <tr style="background-color: #fbcfe8; font-weight: bold;">
                    <td style="border: 1px solid #cbd5e1; font-weight: 800; color: #831843;">Dativ (Indirekt)</td>
                    <td style="border: 1px solid #cbd5e1; color: #be185d;">dem</td>
                    <td style="border: 1px solid #cbd5e1; color: #be185d;">einem</td>
                    <td style="border: 1px solid #cbd5e1; color: #be185d; font-size: 1.1rem;">-(e)n</td>
                    <td style="border: 1px solid #cbd5e1; color: #be185d;">dem <strong>Studenten</strong></td>
                    <td style="border: 1px solid #cbd5e1; color: #be185d;">dem <strong>Kollegen</strong></td>
                    <td style="border: 1px solid #cbd5e1;">den <strong>Studenten / Kollegen</strong></td>
                </tr>
                <tr style="background-color: #bbf7d0; font-weight: bold;">
                    <td style="border: 1px solid #cbd5e1; font-weight: 800; color: #14532d;">Genitiv (Besitz)</td>
                    <td style="border: 1px solid #cbd5e1; color: #15803d;">des</td>
                    <td style="border: 1px solid #cbd5e1; color: #15803d;">eines</td>
                    <td style="border: 1px solid #cbd5e1; color: #15803d; font-size: 1.1rem;">-(e)n</td>
                    <td style="border: 1px solid #cbd5e1; color: #15803d;">des <strong>Studenten</strong></td>
                    <td style="border: 1px solid #cbd5e1; color: #15803d;">des <strong>Kollegen</strong></td>
                    <td style="border: 1px solid #cbd5e1;">der <strong>Studenten / Kollegen</strong></td>
                </tr>
            </tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        st.markdown("""
        <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 12px; padding: 14px 18px;">
            <h4 style="margin: 0 0 8px 0; color: #1e40af;">📌 Which Nouns Belong to N-Deklination?</h4>
            <ul style="margin: 0; padding-left: 20px; font-size: 0.9rem; color: #1e293b; line-height: 1.6;">
                <li><strong>1. Masculine persons ending in -e:</strong><br>
                    <em>der Junge, der Kollege, der Kunde, der Zeuge, der Nachbar, der Neffe, der Experte</em>.
                </li>
                <li><strong>2. Foreign words (Greek/Latin) ending in:</strong><br>
                    <strong>-ent / -ant:</strong> <em>der Student, der Patient, der Assistent, der Elefant</em><br>
                    <strong>-ist:</strong> <em>der Polizist, der Tourist, der Journalist, der Spezialist</em><br>
                    <strong>-at / -ot:</strong> <em>der Soldat, der Diplomat, der Pilot</em><br>
                    <strong>-oge:</strong> <em>der Biologe, der Psychologe</em>
                </li>
                <li><strong>3. Special Noun: der Herr:</strong><br>
                    Singular: <em>Herrn</em> (Akk, Dat, Gen) | Plural: <em>Herren</em>
                </li>
                <li><strong>4. Single Neuter Exception:</strong><br>
                    <em>das Herz</em> (Nom/Akk: <em>das Herz</em>, Dat: <em>dem Herzen</em>, Gen: <em>des Herzens</em>)
                </li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px; padding: 14px 18px;">
            <h4 style="margin: 0 0 8px 0; color: #166534;">🗣️ Bilingual Examples (Telugu & Kannada)</h4>
            <div style="font-size: 0.88rem; color: #1e293b; line-height: 1.6;">
                <div style="margin-bottom: 10px; border-bottom: 1px dashed #cbd5e1; padding-bottom: 8px;">
                    🇩🇪 <strong>Ich kenne den neuen Studenten.</strong><br>
                    🇮🇳 <em>(TE)</em> నేను ఆ కొత్త విద్యార్థిని (Akkusativ) ఎరుగుదును.<br>
                    🇮🇳 <em>(KN)</em> ನಾನು ಆ ಹೊಸ ವಿದ್ಯಾರ್ಥಿಯನ್ನು (Akkusativ) ಬಲ್ಲೆ.
                </div>
                <div style="margin-bottom: 10px; border-bottom: 1px dashed #cbd5e1; padding-bottom: 8px;">
                    🇩🇪 <strong>Wir helfen dem kranken Patienten.</strong><br>
                    🇮🇳 <em>(TE)</em> మేము ఆ అనారోగ్య రోగికి (Dativ) సహాయం చేస్తున్నాము.<br>
                    🇮🇳 <em>(KN)</em> ನಾವು ಆ ಅನಾರೋಗ್ಯ ರೋಗಿಗೆ (Dativ) ಸಹಾಯ ಮಾಡುತ್ತಿದ್ದೇವೆ.
                </div>
                <div>
                    🇩🇪 <strong>Das Auto gehört meinem Kollegen.</strong><br>
                    🇮🇳 <em>(TE)</em> ఆ కారు నా సహోద్యోగికి (Dativ) చెందినది.<br>
                    🇮🇳 <em>(KN)</em> ಆ ಕಾರು ನನ್ನ ಸಹೋದ್ಯೋಗಿಗೆ (Dativ) ಸೇರಿದ್ದು.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# 3. RELATIVSÄTZE (RELATIVE CLAUSES)
# ==============================================================================

def _render_relativsatz_chart():
    st.markdown("### 🔗 Relativsätze (Relative Clauses & Pronouns)")
    st.caption("Relative clauses give extra information about a noun. The relative pronoun matches the noun in gender and number, and its case is determined by its role in the relative clause.")

    st.markdown("""
    <div style="overflow-x: auto; margin: 16px 0;">
        <table style="width: 100%; border-collapse: collapse; text-align: center; font-size: 14px;">
            <thead>
                <tr style="background-color: #0f172a; color: white;">
                    <th style="padding: 12px; border: 1px solid #cbd5e1;">Kasus (Case)</th>
                    <th style="padding: 12px; border: 1px solid #cbd5e1; background-color: #1e3a8a;">Maskulin (der)</th>
                    <th style="padding: 12px; border: 1px solid #cbd5e1; background-color: #be185d;">Feminin (die)</th>
                    <th style="padding: 12px; border: 1px solid #cbd5e1; background-color: #047857;">Neutrum (das)</th>
                    <th style="padding: 12px; border: 1px solid #cbd5e1; background-color: #6d28d9;">Plural (die)</th>
                </tr>
            </thead>
            <tbody>
                <tr style="background-color: #f8fafc; font-weight: bold;">
                    <td style="border: 1px solid #cbd5e1; font-weight: 800; color: #1e293b;">Nominativ (Subjekt)</td>
                    <td style="border: 1px solid #cbd5e1; color: #1e3a8a;">der</td>
                    <td style="border: 1px solid #cbd5e1; color: #be185d;">die</td>
                    <td style="border: 1px solid #cbd5e1; color: #047857;">das</td>
                    <td style="border: 1px solid #cbd5e1; color: #6d28d9;">die</td>
                </tr>
                <tr style="background-color: #fed7aa; font-weight: bold;">
                    <td style="border: 1px solid #cbd5e1; font-weight: 800; color: #9a3412;">Akkusativ (Objekt)</td>
                    <td style="border: 1px solid #cbd5e1; color: #b45309; font-weight: 800;">den</td>
                    <td style="border: 1px solid #cbd5e1; color: #be185d;">die</td>
                    <td style="border: 1px solid #cbd5e1; color: #047857;">das</td>
                    <td style="border: 1px solid #cbd5e1; color: #6d28d9;">die</td>
                </tr>
                <tr style="background-color: #fbcfe8; font-weight: bold;">
                    <td style="border: 1px solid #cbd5e1; font-weight: 800; color: #831843;">Dativ (Indirekt)</td>
                    <td style="border: 1px solid #cbd5e1; color: #9d174d;">dem</td>
                    <td style="border: 1px solid #cbd5e1; color: #9d174d;">der</td>
                    <td style="border: 1px solid #cbd5e1; color: #9d174d;">dem</td>
                    <td style="border: 1px solid #cbd5e1; color: #be185d; font-weight: 800; background: #fdf2f8;">denen ⭐ (Special!)</td>
                </tr>
                <tr style="background-color: #bbf7d0; font-weight: bold;">
                    <td style="border: 1px solid #cbd5e1; font-weight: 800; color: #14532d;">Genitiv (Besitz)</td>
                    <td style="border: 1px solid #cbd5e1; color: #166534; font-weight: 800;">dessen</td>
                    <td style="border: 1px solid #cbd5e1; color: #166534; font-weight: 800;">deren</td>
                    <td style="border: 1px solid #cbd5e1; color: #166534; font-weight: 800;">dessen</td>
                    <td style="border: 1px solid #cbd5e1; color: #166534; font-weight: 800;">deren</td>
                </tr>
            </tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        st.markdown("""
        <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 12px; padding: 14px 18px;">
            <h4 style="margin: 0 0 8px 0; color: #1e40af;">📐 Word Order Formula (Satzstruktur)</h4>
            <div style="background: white; border: 2px dashed #3b82f6; border-radius: 8px; padding: 10px; text-align: center; font-weight: 700; color: #1e3a8a; margin: 8px 0;">
                Hauptsatz , [ Relativpronomen + ... + finites Verb am Ende ] .
            </div>
            <ul style="margin: 0; padding-left: 20px; font-size: 0.88rem; color: #1e293b; line-height: 1.6;">
                <li>The relative clause is ALWAYS separated by a comma (<strong>,</strong>).</li>
                <li>The conjugated verb ALWAYS moves to the very end of the clause.</li>
                <li><strong>Prepositions:</strong> When a preposition is used, it precedes the relative pronoun and determines its case (e.g. <em>mit dem</em>, <em>über das</em>, <em>für die</em>).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px; padding: 14px 18px;">
            <h4 style="margin: 0 0 8px 0; color: #166534;">🗣️ Bilingual Examples (Telugu & Kannada)</h4>
            <div style="font-size: 0.88rem; color: #1e293b; line-height: 1.6;">
                <div style="margin-bottom: 8px; border-bottom: 1px dashed #cbd5e1; padding-bottom: 6px;">
                    🇩🇪 <strong>Das ist der Mann, den ich gestern gesehen habe.</strong><br>
                    🇮🇳 <em>(TE)</em> నిన్న నేను చూసిన మనిషి ఈయనే.<br>
                    🇮🇳 <em>(KN)</em> ನಿನ್ನೆ ನಾನು ನೋಡಿದ ವ್ಯಕ್ತಿ ಇವರೇ.
                </div>
                <div style="margin-bottom: 8px; border-bottom: 1px dashed #cbd5e1; padding-bottom: 6px;">
                    🇩🇪 <strong>Die Kollegin, mit der ich arbeite, ist nett.</strong><br>
                    🇮🇳 <em>(TE)</em> నేను ఎవరితోనైతే పని చేస్తున్నానో ఆ సహోద్యోగి మంచిది.<br>
                    🇮🇳 <em>(KN)</em> ನಾನು ಯಾರೊಂದಿಗೆ ಕೆಲಸ ಮಾಡುತ್ತಿದ್ದೇನೋ ಆ ಸಹೋದ್ಯೋಗಿ ಒಳ್ಳೆಯವರು.
                </div>
                <div>
                    🇩🇪 <strong>Die Freunde, denen wir helfen, kommen morgen.</strong><br>
                    🇮🇳 <em>(TE)</em> మనం ఎవరికైతే సహాయం చేస్తున్నామో ఆ స్నేహితులు రేపు వస్తున్నారు.<br>
                    🇮🇳 <em>(KN)</em> ನಾವು ಯಾರಿಗೆ ಸಹಾಯ ಮಾಡುತ್ತಿದ್ದೇವೋ ಆ ಸ್ನೇಹಿತರು ನಾಳೆ ಬರುತ್ತಿದ್ದಾರೆ.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# 4. PASSIV (VORGANGSPASSIV)
# ==============================================================================

def _render_passiv_chart():
    st.markdown("### ⚙️ Passiv (Vorgangspassiv - Process Passive)")
    st.caption("Focuses on the action rather than who performs it. Formed with <strong>werden + Partizip II</strong>.")

    st.markdown("""
    <div style="overflow-x: auto; margin: 16px 0;">
        <table style="width: 100%; border-collapse: collapse; text-align: center; font-size: 14px;">
            <thead>
                <tr style="background-color: #0f172a; color: white;">
                    <th style="padding: 12px; border: 1px solid #cbd5e1;">Zeitform (Tense)</th>
                    <th style="padding: 12px; border: 1px solid #cbd5e1;">Grammatische Formel</th>
                    <th style="padding: 12px; border: 1px solid #cbd5e1;">Aktiv (Active)</th>
                    <th style="padding: 12px; border: 1px solid #cbd5e1; background-color: #2563eb;">Passiv (Passive)</th>
                </tr>
            </thead>
            <tbody>
                <tr style="background-color: #f8fafc;">
                    <td style="border: 1px solid #cbd5e1; font-weight: 800;">Präsens</td>
                    <td style="border: 1px solid #cbd5e1; font-weight: 700; color: #1e40af;">werden (Präsens) + Partizip II</td>
                    <td style="border: 1px solid #cbd5e1;">Der Mechaniker repariert das Auto.</td>
                    <td style="border: 1px solid #cbd5e1; font-weight: 700; color: #2563eb;">Das Auto <strong>wird repariert</strong>.</td>
                </tr>
                <tr style="background-color: #f1f5f9;">
                    <td style="border: 1px solid #cbd5e1; font-weight: 800;">Präteritum</td>
                    <td style="border: 1px solid #cbd5e1; font-weight: 700; color: #1e40af;">wurden (Präteritum) + Partizip II</td>
                    <td style="border: 1px solid #cbd5e1;">Der Mechaniker reparierte das Auto.</td>
                    <td style="border: 1px solid #cbd5e1; font-weight: 700; color: #2563eb;">Das Auto <strong>wurde repariert</strong>.</td>
                </tr>
                <tr style="background-color: #f8fafc;">
                    <td style="border: 1px solid #cbd5e1; font-weight: 800;">Perfekt</td>
                    <td style="border: 1px solid #cbd5e1; font-weight: 700; color: #1e40af;">sein + Partizip II + worden</td>
                    <td style="border: 1px solid #cbd5e1;">Der Mechaniker hat das Auto repariert.</td>
                    <td style="border: 1px solid #cbd5e1; font-weight: 700; color: #2563eb;">Das Auto <strong>ist repariert worden</strong>.</td>
                </tr>
                <tr style="background-color: #eff6ff;">
                    <td style="border: 1px solid #cbd5e1; font-weight: 800;">Mit Modalverb</td>
                    <td style="border: 1px solid #cbd5e1; font-weight: 700; color: #1e40af;">Modalverb + Partizip II + werden</td>
                    <td style="border: 1px solid #cbd5e1;">Man muss das Auto reparieren.</td>
                    <td style="border: 1px solid #cbd5e1; font-weight: 700; color: #2563eb;">Das Auto <strong>muss repariert werden</strong>.</td>
                </tr>
            </tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background: #fefce8; border: 1px solid #fde047; border-radius: 12px; padding: 14px 18px; margin-top: 10px;">
        <h4 style="margin: 0 0 6px 0; color: #854d0e;">💡 Indicating the Agent: von vs. durch</h4>
        <div style="font-size: 0.9rem; color: #713f12; line-height: 1.6;">
            • <strong>von + Dativ:</strong> Used for persons or living beings (e.g. <em>Das Auto wird <strong>vom Mechaniker</strong> repariert</em>).<br>
            • <strong>durch + Akkusativ:</strong> Used for tools, causes, mediums, or natural events (e.g. <em>Das Haus wurde <strong>durch den Sturm</strong> beschädigt</em>).
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# 5. KONJUNKTIV II
# ==============================================================================

def _render_konjunktiv_chart():
    st.markdown("### ✨ Konjunktiv II (Unreal Wishes, Politeness & Advice)")
    st.caption("Used for polite requests (Höflichkeit), hypothetical wishes (Träume), and giving advice (Ratschläge).")

    st.markdown("""
    <div style="overflow-x: auto; margin: 16px 0;">
        <table style="width: 100%; border-collapse: collapse; text-align: center; font-size: 14px;">
            <thead>
                <tr style="background-color: #0f172a; color: white;">
                    <th style="padding: 12px; border: 1px solid #cbd5e1;">Personalpronomen</th>
                    <th style="padding: 12px; border: 1px solid #cbd5e1; background-color: #1e3a8a;">würde + Infinitiv</th>
                    <th style="padding: 12px; border: 1px solid #cbd5e1; background-color: #047857;">sein (wäre)</th>
                    <th style="padding: 12px; border: 1px solid #cbd5e1; background-color: #b45309;">haben (hätte)</th>
                    <th style="padding: 12px; border: 1px solid #cbd5e1; background-color: #6d28d9;">können (könnte)</th>
                    <th style="padding: 12px; border: 1px solid #cbd5e1; background-color: #be185d;">sollen (sollte)</th>
                </tr>
            </thead>
            <tbody>
                <tr style="background-color: #f8fafc;">
                    <td style="border: 1px solid #cbd5e1; font-weight: 800;">ich</td><td>würde</td><td>wäre</td><td>hätte</td><td>könnte</td><td>sollte</td>
                </tr>
                <tr style="background-color: #f1f5f9;">
                    <td style="border: 1px solid #cbd5e1; font-weight: 800;">du</td><td>würdest</td><td>wärst / wärest</td><td>hättest</td><td>könntest</td><td>solltest</td>
                </tr>
                <tr style="background-color: #f8fafc;">
                    <td style="border: 1px solid #cbd5e1; font-weight: 800;">er / sie / es</td><td>würde</td><td>wäre</td><td>hätte</td><td>könnte</td><td>sollte</td>
                </tr>
                <tr style="background-color: #f1f5f9;">
                    <td style="border: 1px solid #cbd5e1; font-weight: 800;">wir</td><td>würden</td><td>wären</td><td>hätten</td><td>könnten</td><td>sollten</td>
                </tr>
                <tr style="background-color: #f8fafc;">
                    <td style="border: 1px solid #cbd5e1; font-weight: 800;">ihr</td><td>würdet</td><td>wärt / wäret</td><td>hättet</td><td>könntet</td><td>solltet</td>
                </tr>
                <tr style="background-color: #f1f5f9;">
                    <td style="border: 1px solid #cbd5e1; font-weight: 800;">sie / Sie</td><td>würden</td><td>wären</td><td>hätten</td><td>könnten</td><td>sollten</td>
                </tr>
            </tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# 6. NEBENSÄTZE MIT KONJUNKTIONEN
# ==============================================================================

def _render_nebensatz_chart():
    st.markdown("### 🔀 Nebensätze mit Konjunktionen (Subordinate Clauses)")
    st.caption("How connectors change the German word order and sentence structure.")

    st.markdown("""
    <div style="overflow-x: auto; margin: 16px 0;">
        <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 14px;">
            <thead>
                <tr style="background-color: #0f172a; color: white;">
                    <th style="padding: 12px; border: 1px solid #cbd5e1; width: 22%;">Konjunktion / Typ</th>
                    <th style="padding: 12px; border: 1px solid #cbd5e1; width: 28%;">Verbposition</th>
                    <th style="padding: 12px; border: 1px solid #cbd5e1; width: 50%;">Beispielsatz</th>
                </tr>
            </thead>
            <tbody>
                <tr style="background-color: #eff6ff;">
                    <td style="padding: 10px; border: 1px solid #cbd5e1;"><strong>Subjunktionen</strong><br>(weil, da, obwohl, dass, wenn, als, damit)</td>
                    <td style="padding: 10px; border: 1px solid #cbd5e1; color: #1e40af; font-weight: bold;">Verb am ENDE (Nebensatz)</td>
                    <td style="padding: 10px; border: 1px solid #cbd5e1;">Ich lerne Deutsch, <strong>weil</strong> ich in Deutschland arbeiten <strong>möchte</strong>.</td>
                </tr>
                <tr style="background-color: #f0fdf4;">
                    <td style="padding: 10px; border: 1px solid #cbd5e1;"><strong>Nebenordnend (ADUSO)</strong><br>(aber, denn, und, sondern, oder)</td>
                    <td style="padding: 10px; border: 1px solid #cbd5e1; color: #166534; font-weight: bold;">Position 0 (Hauptsatz Wortstellung: S + V + O)</td>
                    <td style="padding: 10px; border: 1px solid #cbd5e1;">Ich bleibe zu Hause, <strong>denn</strong> es <strong>regnet</strong> heute stark.</td>
                </tr>
                <tr style="background-color: #fefce8;">
                    <td style="padding: 10px; border: 1px solid #cbd5e1;"><strong>Konjunktionaladverbien</strong><br>(deshalb, darum, trotzdem, sonst)</td>
                    <td style="padding: 10px; border: 1px solid #cbd5e1; color: #854d0e; font-weight: bold;">Inversion (Verb direkt auf Position 2!)</td>
                    <td style="padding: 10px; border: 1px solid #cbd5e1;">Es regnet, <strong>trotzdem</strong> <strong>gehe</strong> ich spazieren.</td>
                </tr>
            </tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# 7. ADJEKTIVDEKLINATION
# ==============================================================================

def _render_adjektiv_chart():
    st.markdown("### 🎨 Adjektivdeklination (Adjective Endings: Typ 1, 2, 3)")
    st.caption("How adjective endings adapt according to the preceding article and grammatical case.")

    st.markdown("""
    <div style="overflow-x: auto; margin: 16px 0;">
        <table style="width: 100%; border-collapse: collapse; text-align: center; font-size: 14px;">
            <thead>
                <tr style="background-color: #0f172a; color: white;">
                    <th style="padding: 12px; border: 1px solid #cbd5e1;">Kasus</th>
                    <th style="padding: 12px; border: 1px solid #cbd5e1; background-color: #1e3a8a;">Maskulin</th>
                    <th style="padding: 12px; border: 1px solid #cbd5e1; background-color: #be185d;">Feminin</th>
                    <th style="padding: 12px; border: 1px solid #cbd5e1; background-color: #047857;">Neutrum</th>
                    <th style="padding: 12px; border: 1px solid #cbd5e1; background-color: #6d28d9;">Plural</th>
                </tr>
            </thead>
            <tbody>
                <tr style="background-color: #f8fafc; font-weight: bold;">
                    <td colspan="5" style="background: #e2e8f0; text-align: left; padding: 6px 12px; color: #1e293b;">
                        <strong>Typ 1: Nach bestimmtem Artikel (der, die, das)</strong>
                    </td>
                </tr>
                <tr><td>Nominativ</td><td>der neu<strong>e</strong></td><td>die neu<strong>e</strong></td><td>das neu<strong>e</strong></td><td style="color:#b45309;font-weight:bold;">die neu<strong>en</strong></td></tr>
                <tr><td>Akkusativ</td><td style="color:#b45309;font-weight:bold;">den neu<strong>en</strong></td><td>die neu<strong>e</strong></td><td>das neu<strong>e</strong></td><td style="color:#b45309;font-weight:bold;">die neu<strong>en</strong></td></tr>
                <tr><td>Dativ</td><td style="color:#b45309;font-weight:bold;">dem neu<strong>en</strong></td><td style="color:#b45309;font-weight:bold;">der neu<strong>en</strong></td><td style="color:#b45309;font-weight:bold;">dem neu<strong>en</strong></td><td style="color:#b45309;font-weight:bold;">den neu<strong>en</strong></td></tr>
                <tr><td>Genitiv</td><td style="color:#b45309;font-weight:bold;">des neu<strong>en</strong></td><td style="color:#b45309;font-weight:bold;">der neu<strong>en</strong></td><td style="color:#b45309;font-weight:bold;">des neu<strong>en</strong></td><td style="color:#b45309;font-weight:bold;">der neu<strong>en</strong></td></tr>
                <tr style="background-color: #f8fafc; font-weight: bold;">
                    <td colspan="5" style="background: #fed7aa; text-align: left; padding: 6px 12px; color: #9a3412;">
                        <strong>Typ 2: Nach unbestimmtem Artikel / kein / Possessivartikel (ein, mein, kein)</strong>
                    </td>
                </tr>
                <tr><td>Nominativ</td><td style="color:#1e3a8a;font-weight:bold;">ein neu<strong>er</strong></td><td>eine neu<strong>e</strong></td><td style="color:#047857;font-weight:bold;">ein neu<strong>es</strong></td><td style="color:#b45309;font-weight:bold;">keine neu<strong>en</strong></td></tr>
                <tr><td>Akkusativ</td><td style="color:#b45309;font-weight:bold;">einen neu<strong>en</strong></td><td>eine neu<strong>e</strong></td><td style="color:#047857;font-weight:bold;">ein neu<strong>es</strong></td><td style="color:#b45309;font-weight:bold;">keine neu<strong>en</strong></td></tr>
                <tr><td>Dativ</td><td style="color:#b45309;font-weight:bold;">einem neu<strong>en</strong></td><td style="color:#b45309;font-weight:bold;">einer neu<strong>en</strong></td><td style="color:#b45309;font-weight:bold;">einem neu<strong>en</strong></td><td style="color:#b45309;font-weight:bold;">keinen neu<strong>en</strong></td></tr>
                <tr><td>Genitiv</td><td style="color:#b45309;font-weight:bold;">eines neu<strong>en</strong></td><td style="color:#b45309;font-weight:bold;">einer neu<strong>en</strong></td><td style="color:#b45309;font-weight:bold;">eines neu<strong>en</strong></td><td style="color:#b45309;font-weight:bold;">keiner neu<strong>en</strong></td></tr>
            </tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# 8. DYNAMIC COMMUNITY TOPIC CHART
# ==============================================================================

def _render_custom_community_chart(topic: str):
    st.markdown(f"### 📚 {topic} (Community Topic Reference)")
    st.caption("Grammar rules and sample structures extracted from Goethe B1 Duel questions.")

    # Fetch stored questions for this topic to extract patterns and examples
    qs = storage.get_repo_questions_for_topic(topic, category="pronoun")
    if not qs:
        qs = storage.get_repo_questions_for_topic(topic, category="gender")

    if qs:
        st.markdown(f"Found **{len(qs)} verified Goethe B1 Duel questions & explanations** for this topic in the database:")
        for idx, q in enumerate(qs[:6], start=1):
            with st.expander(f"Question #{idx}: {q.get('target_de', 'Sample Sentence')}"):
                st.markdown(f"""
                * 🇩🇪 **German Sentence:** `{q.get('target_de', '')}`
                * 🇮🇳 **Telugu (తెలుగు):** {q.get('prompt_te', '')}
                * 🇮🇳 **Kannada (ಕನ್ನಡ):** {q.get('prompt_kn', '')}
                * 💡 **Grammatical Rule:** {q.get('explanation', '')}
                * 🏷️ **Kasus / Category:** `{q.get('case', 'B1')} • {q.get('gender', 'Rule')}`
                """)
    else:
        st.info(f"Questions and detailed rules for **'{topic}'** are syncing with the database. Start a duel to trigger fresh examples!")
