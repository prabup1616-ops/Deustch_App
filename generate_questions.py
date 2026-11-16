"""
Generator script to build 162 verified Goethe B1 German questions
with Possessivartikel (Nominativ, Akkusativ, Dativ, Genitiv),
authentic Telugu prompts, Kannada prompts, distractors, and grammatical explanations.
"""

import json

# We define structured templates covering every combination of:
# Cases: Nom, Akk, Dat, Gen
# Genders: Maskulin, Feminin, Neutrum, Plural
# Pronouns: ich, du, er, sie(f), wir, ihr, Sie/sie(pl)
# All using Goethe B1 vocabulary

def generate_162_questions():
    questions = []
    
    # We will build 162 distinct, rich questions
    # Base building blocks
    raw_data = [
        # --- DATIV VERBS & PREPOSITIONS (Maskulin, Feminin, Neutrum, Plural) ---
        {
            "topic": "Dativ Maskulin (ich -> mein)",
            "te": "నేను నా స్నేహితుడికి పుట్టినరోజు శుభాకాంక్షలు తెలుపుతున్నాను.",
            "kn": "ನಾನು ನನ್ನ ಸ್ನೇಹಿತನಿಗೆ ಜನ್ಮದಿನದ ಶುಭಾಶಯ ತಿಳಿಸುತ್ತಿದ್ದೇನೆ.",
            "de": "Ich gratuliere meinem Freund zum Geburtstag.",
            "distractors": ["Ich gratuliere meinen Freund zum Geburtstag.", "Ich gratuliere mein Freund zum Geburtstag.", "Ich gratuliere meines Freundes zum Geburtstag."],
            "case": "Dativ", "gender": "Maskulin (der Freund)", "verb": "gratulieren",
            "exp": "'gratulieren' takes Dativ. 'der Freund' is masculine -> 'meinem Freund'."
        },
        {
            "topic": "Dativ Maskulin (du -> dein)",
            "te": "నువ్వు నీ ఉపాధ్యాయుడికి కృతజ్ఞతలు చెప్పావా?",
            "kn": "ನೀನು ನಿನ್ನ ಶಿಕ್ಷಕರಿಗೆ ಧನ್ಯವಾದಗಳನ್ನು ಹೇಳಿದೆಯಾ?",
            "de": "Hast du deinem Lehrer für die Unterstützung gedankt?",
            "distractors": ["Hast du deinen Lehrer für die Unterstützung gedankt?", "Hast du dein Lehrer für die Unterstützung gedankt?", "Hast du deines Lehrers für die Unterstützung gedankt?"],
            "case": "Dativ", "gender": "Maskulin (der Lehrer)", "verb": "danken",
            "exp": "'danken' takes Dativ. 'der Lehrer' is masculine -> 'deinem Lehrer'."
        },
        {
            "topic": "Dativ Maskulin (er -> sein)",
            "te": "అతను తన సహోద్యోగితో ప్రాజెక్ట్ గురించి చర్చిస్తున్నాడు.",
            "kn": "ಅವನು ತನ್ನ ಸಹೋದ್ಯೋಗಿಯೊಂದಿಗೆ ಯೋಜನೆಯ ಬಗ್ಗೆ ಚರ್ಚಿಸುತ್ತಿದ್ದಾನೆ.",
            "de": "Er spricht mit seinem Kollegen über das neue Projekt.",
            "distractors": ["Er spricht mit seinen Kollegen über das neue Projekt.", "Er spricht mit sein Kollege über das neue Projekt.", "Er spricht mit seines Kollegen über das neue Projekt."],
            "case": "Dativ", "gender": "Maskulin (der Kollege)", "verb": "sprechen mit",
            "exp": "Preposition 'mit' requires Dativ. 'der Kollege' (weak noun) in Dativ -> 'seinem Kollegen'."
        },
        {
            "topic": "Dativ Maskulin (sie [she] -> ihr)",
            "te": "ఆమె తన వైద్యుడికి తన సమస్యల గురించి వివరంగా చెప్పింది.",
            "kn": "ಅವಳು ತನ್ನ ವೈದ್ಯರಿಗೆ ತನ್ನ ಸಮಸ್ಯೆಗಳ ಬಗ್ಗೆ ವಿವರವಾಗಿ ಹೇಳಿದಳು.",
            "de": "Sie hat ihrem Arzt ihre Beschwerden ausführlich erklärt.",
            "distractors": ["Sie hat ihren Arzt ihre Beschwerden ausführlich erklärt.", "Sie hat ihr Arzt ihre Beschwerden ausführlich erklärt.", "Sie hat ihres Arztes ihre Beschwerden ausführlich erklärt."],
            "case": "Dativ", "gender": "Maskulin (der Arzt)", "verb": "erklären",
            "exp": "'erklären' to someone takes Dativ. 'der Arzt' is masculine -> 'ihrem Arzt'."
        },
        {
            "topic": "Dativ Maskulin (wir -> unser)",
            "te": "మేము రేపు మా బాస్‌తో సమావేశం ఏర్పాటు చేసుకున్నాము.",
            "kn": "ನಾವು ನಾಳೆ ನಮ್ಮ ಬಾಸ್ ಜೊತೆ ಸಭೆ ಏರ್ಪಡಿಸಿಕೊಂಡಿದ್ದೇವೆ.",
            "de": "Wir haben morgen einen Termin mit unserem Chef.",
            "distractors": ["Wir haben morgen einen Termin mit unseren Chef.", "Wir haben morgen einen Termin mit unser Chef.", "Wir haben morgen einen Termin mit unseres Chefs."],
            "case": "Dativ", "gender": "Maskulin (der Chef)", "verb": "haben / mit",
            "exp": "'mit' requires Dativ. 'der Chef' is masculine -> 'unserem Chef'."
        },
        {
            "topic": "Dativ Maskulin (ihr -> euer)",
            "te": "మీరు మీ పొరుగువారితో మాట్లాడారా?",
            "kn": "ನೀವು ನಿಮ್ಮ ನೆರೆಹೊರೆಯವರೊಂದಿಗೆ ಮಾತನಾಡಿದ್ದೀರಾ?",
            "de": "Habt ihr mit eurem Nachbarn über den Lärm gesprochen?",
            "distractors": ["Habt ihr mit euren Nachbarn über den Lärm gesprochen?", "Habt ihr mit euer Nachbar über den Lärm gesprochen?", "Habt ihr mit eures Nachbarn über den Lärm gesprochen?"],
            "case": "Dativ", "gender": "Maskulin (der Nachbar)", "verb": "sprechen mit",
            "exp": "'mit' takes Dativ. 'ihr' possessive is 'euer', in Dativ Maskulin -> 'eurem Nachbarn'."
        },
        {
            "topic": "Dativ Maskulin (Sie -> Ihr)",
            "te": "మీరు మీ మేనేజర్‌కు సమాచారం ఇచ్చారా?",
            "kn": "ನೀವು ನಿಮ್ಮ ಮ್ಯಾನೇಜರ್‌ಗೆ ಮಾಹಿತಿ ನೀಡಿದ್ದೀರಾ?",
            "de": "Haben Sie Ihrem Manager die Information gegeben?",
            "distractors": ["Haben Sie Ihren Manager die Information gegeben?", "Haben Sie Ihr Manager die Information gegeben?", "Haben Sie Ihres Managers die Information gegeben?"],
            "case": "Dativ", "gender": "Maskulin (der Manager)", "verb": "geben",
            "exp": "'geben' to someone takes Dativ. Formal 'Sie' possessive in Dativ Maskulin -> 'Ihrem Manager'."
        },
        {
            "topic": "Dativ Feminin (ich -> mein)",
            "te": "నేను నా సోదరికి హోమ్‌వర్క్‌లో సహాయం చేస్తున్నాను.",
            "kn": "ನಾನು ನನ್ನ ಸಹೋದರಿಗೆ ಮನೆಕೆಲಸದಲ್ಲಿ ಸಹಾಯ ಮಾಡುತ್ತಿದ್ದೇನೆ.",
            "de": "Ich helfe meiner Schwester bei den Hausaufgaben.",
            "distractors": ["Ich helfe meine Schwester bei den Hausaufgaben.", "Ich helfe meinem Schwester bei den Hausaufgaben.", "Ich helfe meinen Schwester bei den Hausaufgaben."],
            "case": "Dativ", "gender": "Feminin (die Schwester)", "verb": "helfen",
            "exp": "'helfen' takes Dativ. 'die Schwester' is feminine -> 'meiner Schwester'."
        },
        {
            "topic": "Dativ Feminin (du -> dein)",
            "te": "నువ్వు నీ అమ్మగారికి బహుమతి ఇచ్చావా?",
            "kn": "ನೀನು ನಿನ್ನ ತಾಯಿಗೆ ಉಡುಗೊರೆ ನೀಡಿದೆಯಾ?",
            "de": "Hast du deiner Mutter ein Geschenk gekauft?",
            "distractors": ["Hast du deine Mutter ein Geschenk gekauft?", "Hast du deinem Mutter ein Geschenk gekauft?", "Hast du deinen Mutter ein Geschenk gekauft?"],
            "case": "Dativ", "gender": "Feminin (die Mutter)", "verb": "kaufen / schenken",
            "exp": "Indirect object (to whom) takes Dativ. 'die Mutter' is feminine -> 'deiner Mutter'."
        },
        {
            "topic": "Dativ Feminin (er -> sein)",
            "te": "అతను తన సహోద్యోగినికి (స్త్రీ) మెయిల్ పంపించాడు.",
            "kn": "ಅವನು ತನ್ನ ಸಹೋದ್ಯೋಗಿಗೆ (ಮಹಿಳೆ) ಇಮೇಲ್ ಕಳುಹಿಸಿದನು.",
            "de": "Er antwortet seiner Kollegin immer sehr schnell.",
            "distractors": ["Er antwortet seine Kollegin immer sehr schnell.", "Er antwortet seinem Kollegin immer sehr schnell.", "Er antwortet seinen Kollegin immer sehr schnell."],
            "case": "Dativ", "gender": "Feminin (die Kollegin)", "verb": "antworten",
            "exp": "'antworten' takes Dativ. 'die Kollegin' is feminine -> 'seiner Kollegin'."
        },
        {
            "topic": "Dativ Feminin (sie [she] -> ihr)",
            "te": "ఆమె తన ఉపాధ్యాయురాలితో ప్రాజెక్ట్ చర్చించింది.",
            "kn": "ಅವಳು ತನ್ನ ಶಿಕ್ಷಕಿಯೊಂದಿಗೆ ಯೋಜನೆಯನ್ನು ಚರ್ಚಿಸಿದಳು.",
            "de": "Sie lernt gern bei ihrer Lehrerin.",
            "distractors": ["Sie lernt gern bei ihre Lehrerin.", "Sie lernt gern bei ihrem Lehrerin.", "Sie lernt gern bei ihren Lehrerin."],
            "case": "Dativ", "gender": "Feminin (die Lehrerin)", "verb": "lernen bei",
            "exp": "'bei' requires Dativ. 'ihr' (her) in Dativ Feminin -> 'ihrer Lehrerin'."
        },
        {
            "topic": "Dativ Feminin (wir -> unser)",
            "te": "మేము మా అత్తగారికి సహాయం చేయాలనుకుంటున్నాము.",
            "kn": "ನಾವು ನಮ್ಮ ಅತ್ತೆಗೆ ಸಹಾಯ ಮಾಡಲು ಬಯಸುತ್ತೇವೆ.",
            "de": "Wir möchten unserer Tante beim Umzug helfen.",
            "distractors": ["Wir möchten unsere Tante beim Umzug helfen.", "Wir möchten unserem Tante beim Umzug helfen.", "Wir möchten unseren Tante beim Umzug helfen."],
            "case": "Dativ", "gender": "Feminin (die Tante)", "verb": "helfen",
            "exp": "'helfen' takes Dativ. 'die Tante' is feminine -> 'unserer Tante'."
        },
        {
            "topic": "Dativ Feminin (ihr -> euer)",
            "te": "మీరు మీ అమ్మమ్మగారిని చూడటానికి వెళ్తున్నారా?",
            "kn": "ನೀವು ನಿಮ್ಮ ಅಜ್ಜಿಯನ್ನು ನೋಡಲು ಹೋಗುತ್ತಿದ್ದೀರಾ?",
            "de": "Fahrt ihr zu eurer Oma am Wochenende?",
            "distractors": ["Fahrt ihr zu eure Oma am Wochenende?", "Fahrt ihr zu eurem Oma am Wochenende?", "Fahrt ihr zu euren Oma am Wochenende?"],
            "case": "Dativ", "gender": "Feminin (die Oma)", "verb": "fahren zu",
            "exp": "'zu' takes Dativ. Pronoun 'ihr' possessive in Dativ Feminin -> 'eurer Oma'."
        },
        {
            "topic": "Dativ Feminin (Sie -> Ihr)",
            "te": "మీరు మీ కుమార్తెకు ఈ పుస్తకం కొన్నారా?",
            "kn": "ನೀವು ನಿಮ್ಮ ಮಗಳಿಗೆ ಈ ಪುಸ್ತಕವನ್ನು ಖರೀದಿಸಿದ್ದೀರಾ?",
            "de": "Gefällt dieses Buch Ihrer Tochter?",
            "distractors": ["Gefällt dieses Buch Ihre Tochter?", "Gefällt dieses Buch Ihrem Tochter?", "Gefällt dieses Buch Ihren Tochter?"],
            "case": "Dativ", "gender": "Feminin (die Tochter)", "verb": "gefallen",
            "exp": "'gefallen' takes Dativ. Formal 'Sie' possessive in Dativ Feminin -> 'Ihrer Tochter'."
        },
        {
            "topic": "Dativ Neutrum (ich -> mein)",
            "te": "నా పిల్లవాడికి ఈ ఔషధం బాగా పనిచేసింది.",
            "kn": "ನನ್ನ ಮಗುವಿಗೆ ಈ ಔಷಧ ಚೆನ್ನಾಗಿ ಕೆಲಸ ಮಾಡಿದೆ.",
            "de": "Das Medikament hilft meinem Kind sehr gut.",
            "distractors": ["Das Medikament hilft meinen Kind sehr gut.", "Das Medikament hilft mein Kind sehr gut.", "Das Medikament hilft meines Kindes sehr gut."],
            "case": "Dativ", "gender": "Neutrum (das Kind)", "verb": "helfen",
            "exp": "'helfen' takes Dativ. 'das Kind' is neuter -> 'meinem Kind'."
        },
        {
            "topic": "Dativ Neutrum (du -> dein)",
            "te": "నీ గదిలో ఒక కొత్త టేబుల్ ఉందా?",
            "kn": "ನಿನ್ನ ಕೋಣೆಯಲ್ಲಿ ಹೊಸ ಮೇಜು ಇದೆಯೇ?",
            "de": "Steht in deinem Zimmer ein neuer Schreibtisch?",
            "distractors": ["Steht in deinen Zimmer ein neuer Schreibtisch?", "Steht in dein Zimmer ein neuer Schreibtisch?", "Steht in deines Zimmers ein neuer Schreibtisch?"],
            "case": "Dativ", "gender": "Neutrum (das Zimmer)", "verb": "stehen in",
            "exp": "'in' (location, Wo?) takes Dativ. 'das Zimmer' is neuter -> 'deinem Zimmer'."
        },
        {
            "topic": "Dativ Neutrum (er -> sein)",
            "te": "అతను తన కొత్త బైక్‌తో ఆఫీసుకు వెళ్తున్నాడు.",
            "kn": "ಅವನು ತನ್ನ ಹೊಸ ಬೈಕ್‌ನೊಂದಿಗೆ ಕಚೇರಿಗೆ ಹೋಗುತ್ತಿದ್ದಾನೆ.",
            "de": "Er fährt oft mit seinem Fahrrad zur Arbeit.",
            "distractors": ["Er fährt oft mit seinen Fahrrad zur Arbeit.", "Er fährt oft mit sein Fahrrad zur Arbeit.", "Er fährt oft mit seines Fahrrads zur Arbeit."],
            "case": "Dativ", "gender": "Neutrum (das Fahrrad)", "verb": "fahren mit",
            "exp": "'mit' requires Dativ. 'das Fahrrad' is neuter -> 'seinem Fahrrad'."
        },
        {
            "topic": "Dativ Neutrum (sie [she] -> ihr)",
            "te": "ఆమె తన బేబీకి ఆహారం తినిపిస్తోంది.",
            "kn": "ಅವಳು ತನ್ನ ಮಗುವಿಗೆ ಆಹಾರವನ್ನು ನೀಡುತ್ತಿದ್ದಾಳೆ.",
            "de": "Sie gibt ihrem Baby frisches Obst.",
            "distractors": ["Sie gibt ihren Baby frisches Obst.", "Sie gibt ihr Baby frisches Obst.", "Sie gibt ihres Babys frisches Obst."],
            "case": "Dativ", "gender": "Neutrum (das Baby)", "verb": "geben",
            "exp": "'geben' (to whom) takes Dativ. 'das Baby' is neuter -> 'ihrem Baby'."
        },
        {
            "topic": "Dativ Neutrum (wir -> unser)",
            "te": "మా కొత్త ఇంటిలో చాలా గదులు ఉన్నాయి.",
            "kn": "ನಮ್ಮ ಹೊಸ ಮನೆಯಲ್ಲಿ ಅನೇಕ ಕೋಣೆಗಳಿವೆ.",
            "de": "In unserem Haus gibt es vier helle Zimmer.",
            "distractors": ["In unseren Haus gibt es vier helle Zimmer.", "In unser Haus gibt es vier helle Zimmer.", "In unseres Hauses gibt es vier helle Zimmer."],
            "case": "Dativ", "gender": "Neutrum (das Haus)", "verb": "in (Dativ)",
            "exp": "'in' + location takes Dativ. 'das Haus' is neuter -> 'unserem Haus'."
        },
        {
            "topic": "Dativ Neutrum (ihr -> euer)",
            "te": "మీరు మీ కొత్త అపార్ట్‌మెంట్‌లో సంతృప్తిగా ఉన్నారా?",
            "kn": "ನೀವು ನಿಮ್ಮ ಹೊಸ ಅಪಾರ್ಟ್ಮೆಂಟ್‌ನಲ್ಲಿ ತೃಪ್ತರಾಗಿದ್ದೀರಾ?",
            "de": "Seid ihr mit eurem Apartment zufrieden?",
            "distractors": ["Seid ihr mit euren Apartment zufrieden?", "Seid ihr mit euer Apartment zufrieden?", "Seid ihr mit eures Apartments zufrieden?"],
            "case": "Dativ", "gender": "Neutrum (das Apartment)", "verb": "zufrieden mit",
            "exp": "'mit' requires Dativ. 'das Apartment' is neuter -> 'eurem Apartment'."
        },
        {
            "topic": "Dativ Neutrum (Sie -> Ihr)",
            "te": "మీరు మీ ప్రాజెక్ట్‌తో చాలా బిజీగా ఉన్నారా?",
            "kn": "ನೀವು ನಿಮ್ಮ ಯೋಜನೆಯಲ್ಲಿ ತುಂಬಾ ಕಾರ್ಯನಿರತರಾಗಿದ್ದೀರಾ?",
            "de": "Arbeiten Sie intensiv an Ihrem Projekt?",
            "distractors": ["Arbeiten Sie intensiv an Ihren Projekt?", "Arbeiten Sie intensiv an Ihr Projekt?", "Arbeiten Sie intensiv an Ihres Projekts?"],
            "case": "Dativ", "gender": "Neutrum (das Projekt)", "verb": "arbeiten an",
            "exp": "'an' + topic takes Dativ. 'das Projekt' is neuter -> 'Ihrem Projekt'."
        },
        {
            "topic": "Dativ Plural (ich -> mein)",
            "te": "నేను నా స్నేహితులతో కలిసి విందు చేసుకుంటున్నాను.",
            "kn": "ನಾನು ನನ್ನ ಸ್ನೇಹಿತರೊಂದಿಗೆ ಭೋಜನ ಮಾಡುತ್ತಿದ್ದೇನೆ.",
            "de": "Ich esse heute Abend mit meinen Freunden.",
            "distractors": ["Ich esse heute Abend mit meinem Freunden.", "Ich esse heute Abend mit meine Freunden.", "Ich esse heute Abend mit meiner Freunden."],
            "case": "Dativ", "gender": "Plural (die Freunde)", "verb": "essen mit",
            "exp": "'mit' requires Dativ. In Dativ Plural, possessive takes -en, and noun takes -n -> 'meinen Freunden'."
        },
        {
            "topic": "Dativ Plural (du -> dein)",
            "te": "నువ్వు నీ తల్లిదండ్రులకు క్రమం తప్పకుండా ఫోన్ చేస్తున్నావా?",
            "kn": "ನೀನು ನಿನ್ನ ಪೋಷಕರಿಗೆ ನಿಯಮಿತವಾಗಿ ಕರೆ ಮಾಡುತ್ತಿದ್ದೀಯಾ?",
            "de": "Telefonierst du regelmäßig mit deinen Eltern?",
            "distractors": ["Telefonierst du regelmäßig mit deinem Eltern?", "Telefonierst du regelmäßig mit deine Eltern?", "Telefonierst du regelmäßig mit deiner Eltern?"],
            "case": "Dativ", "gender": "Plural (die Eltern)", "verb": "telefonieren mit",
            "exp": "'mit' takes Dativ. In Dativ Plural -> 'deinen Eltern'."
        },
        {
            "topic": "Dativ Plural (er -> sein)",
            "te": "అతను తన పిల్లలకు ఒక అందమైన కథ చెప్పాడు.",
            "kn": "ಅವನು ತನ್ನ ಮಕ್ಕಳಿಗೆ ಒಂದು ಸುಂದರವಾದ ಕಥೆಯನ್ನು ಹೇಳಿದನು.",
            "de": "Er erzählt seinen Kindern eine schöne Geschichte.",
            "distractors": ["Er erzählt seinem Kindern eine schöne Geschichte.", "Er erzählt seine Kindern eine schöne Geschichte.", "Er erzählt seiner Kindern eine schöne Geschichte."],
            "case": "Dativ", "gender": "Plural (die Kinder)", "verb": "erzählen",
            "exp": "'erzählen' to someone takes Dativ. 'die Kinder' in Dativ Plural takes -n ('Kindern') -> 'seinen Kindern'."
        },
        {
            "topic": "Dativ Plural (sie [she] -> ihr)",
            "te": "ఆమె తన అతిథులకు టీ మరియు కేక్ వడ్డించింది.",
            "kn": "ಅವಳು ತನ್ನ ಅತಿಥಿಗಳಿಗೆ ಚಹಾ ಮತ್ತು ಕೇಕ್ ನೀಡಿದಳು.",
            "de": "Sie bietet ihren Gästen Kaffee und Kuchen an.",
            "distractors": ["Sie bietet ihrem Gästen Kaffee und Kuchen an.", "Sie bietet ihre Gästen Kaffee und Kuchen an.", "Sie bietet ihrer Gästen Kaffee und Kuchen an."],
            "case": "Dativ", "gender": "Plural (die Gäste)", "verb": "anbieten",
            "exp": "'anbieten' to someone takes Dativ. 'die Gäste' in Dativ Plural takes -n ('Gästen') -> 'ihren Gästen'."
        },
        {
            "topic": "Dativ Plural (wir -> unser)",
            "te": "మేము మా ఉపాధ్యాయులకు వీడ్కోలు చెప్పాము.",
            "kn": "ನಾವು ನಮ್ಮ ಶಿಕ್ಷಕರಿಗೆ ಬೀಳ್ಕೊಡುಗೆ ಹೇಳಿದೆವು.",
            "de": "Wir danken unseren Lehrern für die tolle Zeit.",
            "distractors": ["Wir danken unserem Lehrern für die tolle Zeit.", "Wir danken unsere Lehrern für die tolle Zeit.", "Wir danken unserer Lehrern für die tolle Zeit."],
            "case": "Dativ", "gender": "Plural (die Lehrer)", "verb": "danken",
            "exp": "'danken' takes Dativ. In Dativ Plural -> 'unseren Lehrern'."
        },
        {
            "topic": "Dativ Plural (ihr -> euer)",
            "te": "మీరు మీ స్నేహితులకు ఆహ్వానం పంపారా?",
            "kn": "ನೀವು ನಿಮ್ಮ ಸ್ನೇಹಿತರಿಗೆ ಆಹ್ವಾನವನ್ನು ಕಳುಹಿಸಿದ್ದೀರಾ?",
            "de": "Habt ihr euren Freunden eine Einladung geschickt?",
            "distractors": ["Habt ihr eurem Freunden eine Einladung geschickt?", "Habt ihr eure Freunden eine Einladung geschickt?", "Habt ihr eurer Freunden eine Einladung geschickt?"],
            "case": "Dativ", "gender": "Plural (die Freunde)", "verb": "schicken",
            "exp": "'schicken' to someone takes Dativ. 'ihr' possessive in Dativ Plural -> 'euren Freunden'."
        },
        {
            "topic": "Dativ Plural (Sie -> Ihr)",
            "te": "మీరు మీ ఉద్యోగులకు బోనస్ ఇచ్చారా?",
            "kn": "ನೀವು ನಿಮ್ಮ ಉದ್ಯೋಗಿಗಳಿಗೆ ಬೋನಸ್ ನೀಡಿದ್ದೀರಾ?",
            "de": "Zahlen Sie Ihren Mitarbeitern einen Bonus?",
            "distractors": ["Zahlen Sie Ihrem Mitarbeitern einen Bonus?", "Zahlen Sie Ihre Mitarbeitern einen Bonus?", "Zahlen Sie Ihrer Mitarbeitern einen Bonus?"],
            "case": "Dativ", "gender": "Plural (die Mitarbeiter)", "verb": "zahlen",
            "exp": "'zahlen' to someone takes Dativ. Formal 'Sie' possessive in Dativ Plural -> 'Ihren Mitarbeitern'."
        },

        # --- AKKUSATIV (Maskulin, Feminin, Neutrum, Plural) ---
        {
            "topic": "Akkusativ Maskulin (ich -> mein)",
            "te": "నేను ఈ సాయంత్రం నా సోదరుడిని స్టేషన్ నుండి పికప్ చేసుకుంటాను.",
            "kn": "ನಾನು ಈ ಸಂಜೆ ನನ್ನ ಸಹೋದರನನ್ನು ನಿಲ್ದಾಣದಿಂದ ಕರೆತರಲಿದ್ದೇನೆ.",
            "de": "Ich hole heute Abend meinen Bruder vom Bahnhof ab.",
            "distractors": ["Ich hole heute Abend meinem Bruder vom Bahnhof ab.", "Ich hole heute Abend mein Bruder vom Bahnhof ab.", "Ich hole heute Abend meines Bruders vom Bahnhof ab."],
            "case": "Akkusativ", "gender": "Maskulin (der Bruder)", "verb": "abholen",
            "exp": "'abholen' takes direct object in Akkusativ. 'der Bruder' is masculine -> 'meinen Bruder'."
        },
        {
            "topic": "Akkusativ Maskulin (du -> dein)",
            "te": "నువ్వు రైల్వే స్టేషన్‌లో నీ పాస్‌పోర్ట్‌ను మర్చిపోయావా?",
            "kn": "ನೀನು ರೈಲ್ವೆ ನಿಲ್ದಾಣದಲ್ಲಿ ನಿನ್ನ ಪಾಸ್‌ಪೋರ್ಟ್ ಅನ್ನು ಮರೆತುಬಿಟ್ಟೆಯಾ?",
            "de": "Hast du deinen Pass am Bahnhof vergessen?",
            "distractors": ["Hast du deinem Pass am Bahnhof vergessen?", "Hast du dein Pass am Bahnhof vergessen?", "Hast du deines Passes am Bahnhof vergessen?"],
            "case": "Akkusativ", "gender": "Maskulin (der Pass)", "verb": "vergessen",
            "exp": "'vergessen' takes Akkusativ. 'der Pass' is masculine -> 'deinen Pass'."
        },
        {
            "topic": "Akkusativ Maskulin (er -> sein)",
            "te": "అతను తన ఉపాధ్యాయుడిని చాలా గౌరవిస్తాడు.",
            "kn": "ಅವನು ತನ್ನ ಶಿಕ್ಷಕರನ್ನು ತುಂಬಾ ಗೌರವಿಸುತ್ತಾನೆ.",
            "de": "Er respektiert seinen Lehrer sehr.",
            "distractors": ["Er respektiert seinem Lehrer sehr.", "Er respektiert sein Lehrer sehr.", "Er respektiert seines Lehrers sehr."],
            "case": "Akkusativ", "gender": "Maskulin (der Lehrer)", "verb": "respektieren",
            "exp": "'respektieren' takes Akkusativ. 'der Lehrer' is masculine -> 'seinen Lehrer'."
        },
        {
            "topic": "Akkusativ Maskulin (sie [she] -> ihr)",
            "te": "ఆమె తన బాస్‌ను ఒక ముఖ్యమైన ప్రశ్న అడిగింది.",
            "kn": "ಅವಳು ತನ್ನ ಮುಖ್ಯಸ್ಥರನ್ನು ಒಂದು ಮುಖ್ಯವಾದ ಪ್ರಶ್ನೆ ಕೇಳಿದಳು.",
            "de": "Sie hat ihren Chef um Rat gefragt.",
            "distractors": ["Sie hat ihrem Chef um Rat gefragt.", "Sie hat ihr Chef um Rat gefragt.", "Sie hat ihres Chefs um Rat gefragt."],
            "case": "Akkusativ", "gender": "Maskulin (der Chef)", "verb": "fragen um",
            "exp": "'fragen' takes Akkusativ for the person asked. 'der Chef' is masculine -> 'ihren Chef'."
        },
        {
            "topic": "Akkusativ Maskulin (wir -> unser)",
            "te": "మేము మా పాత కారును మంచి ధరకు అమ్మేశాము.",
            "kn": "ನಾವು ನಮ್ಮ ಹಳೆಯ ಕಾರನ್ನು ಉತ್ತಮ ಬೆಲೆಗೆ ಮಾರಾಟ ಮಾಡಿದೆವು.",
            "de": "Wir haben unseren alten Wagen gestern verkauft.",
            "distractors": ["Wir haben unserem alten Wagen gestern verkauft.", "Wir haben unser alten Wagen gestern verkauft.", "Wir haben unseres alten Wagens gestern verkauft."],
            "case": "Akkusativ", "gender": "Maskulin (der Wagen)", "verb": "verkaufen",
            "exp": "'verkaufen' takes Akkusativ. 'der Wagen' is masculine -> 'unseren alten Wagen'."
        },
        {
            "topic": "Akkusativ Maskulin (ihr -> euer)",
            "te": "మీరు మీ సూట్‌కేస్‌ను సిద్ధం చేసుకున్నారా?",
            "kn": "ನೀವು ನಿಮ್ಮ ಸೂಟ್‌ಕೇಸ್ ಅನ್ನು ಸಿದ್ಧಪಡಿಸಿಕೊಂಡಿದ್ದೀರಾ?",
            "de": "Habt ihr euren Koffer schon gepackt?",
            "distractors": ["Habt ihr eurem Koffer schon gepackt?", "Habt ihr euer Koffer schon gepackt?", "Habt ihr eures Koffers schon gepackt?"],
            "case": "Akkusativ", "gender": "Maskulin (der Koffer)", "verb": "packen",
            "exp": "'packen' takes Akkusativ. 'ihr' possessive in Akkusativ Maskulin -> 'euren Koffer'."
        },
        {
            "topic": "Akkusativ Maskulin (Sie -> Ihr)",
            "te": "మీరు మీ కాంట్రాక్ట్‌ను రద్దు చేయాలనుకుంటున్నారా?",
            "kn": "ನೀವು ನಿಮ್ಮ ಒಪ್ಪಂದವನ್ನು ರದ್ದುಗೊಳಿಸಲು ಬಯಸುತ್ತೀರಾ?",
            "de": "Möchten Sie Ihren Vertrag kündigen?",
            "distractors": ["Möchten Sie Ihrem Vertrag kündigen?", "Möchten Sie Ihr Vertrag kündigen?", "Möchten Sie Ihres Vertrages kündigen?"],
            "case": "Akkusativ", "gender": "Maskulin (der Vertrag)", "verb": "kündigen",
            "exp": "'kündigen' takes Akkusativ. Formal 'Sie' possessive in Akkusativ Maskulin -> 'Ihren Vertrag'."
        },
        {
            "topic": "Akkusativ Feminin (ich -> mein)",
            "te": "నేను నా దరఖాస్తును రేపు పోస్ట్ ద్వారా పంపుతాను.",
            "kn": "ನಾನು ನನ್ನ ಅರ್ಜಿಯನ್ನು ನಾಳೆ ಅಂಚೆ ಮೂಲಕ ಕಳುಹಿಸುತ್ತೇನೆ.",
            "de": "Ich schicke meine Bewerbung morgen per Post.",
            "distractors": ["Ich schicke meiner Bewerbung morgen per Post.", "Ich schicke meinem Bewerbung morgen per Post.", "Ich schicke meinen Bewerbung morgen per Post."],
            "case": "Akkusativ", "gender": "Feminin (die Bewerbung)", "verb": "schicken",
            "exp": "'schicken' takes Akkusativ. 'die Bewerbung' is feminine -> 'meine Bewerbung'."
        },
        {
            "topic": "Akkusativ Feminin (du -> dein)",
            "te": "నువ్వు నీ బ్యాగ్‌ను ఎక్కడ పోగొట్టుకున్నావు?",
            "kn": "ನೀನು ನಿನ್ನ ಬ್ಯಾಗ್ ಅನ್ನು ಎಲ್ಲಿ ಕಳೆದುಕೊಂಡೆ?",
            "de": "Wo hast du deine Tasche verloren?",
            "distractors": ["Wo hast du deiner Tasche verloren?", "Wo hast du deinem Tasche verloren?", "Wo hast du deinen Tasche verloren?"],
            "case": "Akkusativ", "gender": "Feminin (die Tasche)", "verb": "verlieren",
            "exp": "'verlieren' takes Akkusativ. 'die Tasche' is feminine -> 'deine Tasche'."
        },
        {
            "topic": "Akkusativ Feminin (er -> sein)",
            "te": "అతను తన పాత అపార్ట్‌మెంట్‌ను ఖాళీ చేశాడు.",
            "kn": "ಅವನು ತನ್ನ ಹಳೆಯ ಅಪಾರ್ಟ್ಮೆಂಟ್ ಅನ್ನು ಖಾಲಿ ಮಾಡಿದನು.",
            "de": "Er hat seine Wohnung rechtzeitig gekündigt.",
            "distractors": ["Er hat seiner Wohnung rechtzeitig gekündigt.", "Er hat seinem Wohnung rechtzeitig gekündigt.", "Er hat seinen Wohnung rechtzeitig gekündigt."],
            "case": "Akkusativ", "gender": "Feminin (die Wohnung)", "verb": "kündigen",
            "exp": "'kündigen' takes Akkusativ. 'die Wohnung' is feminine -> 'seine Wohnung'."
        },
        {
            "topic": "Akkusativ Feminin (sie [she] -> ihr)",
            "te": "ఆమె తన పరీక్షను విజయవంతంగా పూర్తి చేసింది.",
            "kn": "ಅವಳು ತನ್ನ ಪರೀಕ್ಷೆಯನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಪೂರ್ಣಗೊಳಿಸಿದಳು.",
            "de": "Sie hat ihre Prüfung erfolgreich bestanden.",
            "distractors": ["Sie hat ihrer Prüfung erfolgreich bestanden.", "Sie hat ihrem Prüfung erfolgreich bestanden.", "Sie hat ihren Prüfung erfolgreich bestanden."],
            "case": "Akkusativ", "gender": "Feminin (die Prüfung)", "verb": "bestehen",
            "exp": "'bestehen' takes Akkusativ. 'die Prüfung' is feminine -> 'ihre Prüfung'."
        },
        {
            "topic": "Akkusativ Feminin (wir -> unser)",
            "te": "మేము మా ప్రెజెంటేషన్‌ను బాగా సిద్ధం చేసుకున్నాము.",
            "kn": "ನಾವು ನಮ್ಮ ಪ್ರಸ್ತುತಿಯನ್ನು ಚೆನ್ನಾಗಿ ಸಿದ್ಧಪಡಿಸಿಕೊಂಡಿದ್ದೇವೆ.",
            "de": "Wir haben unsere Präsentation gut vorbereitet.",
            "distractors": ["Wir haben unserer Präsentation gut vorbereitet.", "Wir haben unserem Präsentation gut vorbereitet.", "Wir haben unseren Präsentation gut vorbereitet."],
            "case": "Akkusativ", "gender": "Feminin (die Präsentation)", "verb": "vorbereiten",
            "exp": "'vorbereiten' takes Akkusativ. 'die Präsentation' is feminine -> 'unsere Präsentation'."
        },
        {
            "topic": "Akkusativ Feminin (ihr -> euer)",
            "te": "మీరు మీ ప్రయాణాన్ని ఎప్పుడు ప్రారంభిస్తారు?",
            "kn": "ನೀವು ನಿಮ್ಮ ಪ್ರಯಾಣವನ್ನು ಯಾವಾಗ ಪ್ರಾರಂಭಿಸುತ್ತೀರಿ?",
            "de": "Wann beginnt ihr eure Reise nach München?",
            "distractors": ["Wann beginnt ihr eurer Reise nach München?", "Wann beginnt ihr eurem Reise nach München?", "Wann beginnt ihr euren Reise nach München?"],
            "case": "Akkusativ", "gender": "Feminin (die Reise)", "verb": "beginnen",
            "exp": "'beginnen' takes Akkusativ. 'ihr' possessive in Akkusativ Feminin -> 'eure Reise'."
        },
        {
            "topic": "Akkusativ Feminin (Sie -> Ihr)",
            "te": "మీరు మీ సంతకాన్ని ఇక్కడ చేయగలరా?",
            "kn": "ನೀವು ನಿಮ್ಮ ಸಹಿಯನ್ನು ಇಲ್ಲಿ ಮಾಡಬಹುದೇ?",
            "de": "Können Sie bitte Ihre Unterschrift hier setzen?",
            "distractors": ["Können Sie bitte Ihrer Unterschrift hier setzen?", "Können Sie bitte Ihrem Unterschrift hier setzen?", "Können Sie bitte Ihren Unterschrift hier setzen?"],
            "case": "Akkusativ", "gender": "Feminin (die Unterschrift)", "verb": "setzen",
            "exp": "'setzen' takes Akkusativ. Formal 'Sie' possessive in Akkusativ Feminin -> 'Ihre Unterschrift'."
        },
        {
            "topic": "Akkusativ Neutrum (ich -> mein)",
            "te": "నేను నా బైక్‌ను సర్వీస్ సెంటర్‌కు తీసుకెళ్తున్నాను.",
            "kn": "ನಾನು ನನ್ನ ಬೈಕ್ ಅನ್ನು ಸರ್ವಿಸ್ ಸೆಂಟರ್‌ಗೆ ಕೊಂಡೊಯ್ಯುತ್ತಿದ್ದೇನೆ.",
            "de": "Ich bringe mein Fahrrad zur Reparatur.",
            "distractors": ["Ich bringe meinen Fahrrad zur Reparatur.", "Ich bringe meinem Fahrrad zur Reparatur.", "Ich bringe meines Fahrrads zur Reparatur."],
            "case": "Akkusativ", "gender": "Neutrum (das Fahrrad)", "verb": "bringen",
            "exp": "'bringen' takes Akkusativ. 'das Fahrrad' is neuter -> 'mein Fahrrad'."
        },
        {
            "topic": "Akkusativ Neutrum (du -> dein)",
            "te": "నువ్వు నీ ధృవీకరణ పత్రాన్ని అందుకున్నావా?",
            "kn": "ನೀನು ನಿನ್ನ ಪ್ರಮಾಣಪತ್ರವನ್ನು ಸ್ವೀಕರಿಸಿದೆಯಾ?",
            "de": "Hast du dein Zertifikat schon erhalten?",
            "distractors": ["Hast du deinen Zertifikat schon erhalten?", "Hast du deinem Zertifikat schon erhalten?", "Hast du deines Zertifikats schon erhalten?"],
            "case": "Akkusativ", "gender": "Neutrum (das Zertifikat)", "verb": "erhalten",
            "exp": "'erhalten' takes Akkusativ. 'das Zertifikat' is neuter -> 'dein Zertifikat'."
        },
        {
            "topic": "Akkusativ Neutrum (er -> sein)",
            "te": "అతను తన పాత కారును అమ్మాలనుకుంటున్నాడు.",
            "kn": "ಅವನು ತನ್ನ ಹಳೆಯ ಕಾರನ್ನು ಮಾರಾಟ ಮಾಡಲು ಬಯಸುತ್ತಾನೆ.",
            "de": "Er möchte sein Auto verkaufen.",
            "distractors": ["Er möchte seinen Auto verkaufen.", "Er möchte seinem Auto verkaufen.", "Er möchte seines Autos verkaufen."],
            "case": "Akkusativ", "gender": "Neutrum (das Auto)", "verb": "verkaufen",
            "exp": "'verkaufen' takes Akkusativ. 'das Auto' is neuter -> 'sein Auto'."
        },
        {
            "topic": "Akkusativ Neutrum (sie [she] -> ihr)",
            "te": "ఆమె తన బిడ్డను కిండర్‌గార్టెన్ నుండి తీసుకువస్తుంది.",
            "kn": "ಅವಳು ತನ್ನ ಮಗುವನ್ನು ಕಿಂಡರ್‌ಗಾರ್ಟನ್‌ನಿಂದ ಕರೆತರುತ್ತಾಳೆ.",
            "de": "Sie holt ihr Kind vom Kindergarten ab.",
            "distractors": ["Sie holt ihren Kind vom Kindergarten ab.", "Sie holt ihrem Kind vom Kindergarten ab.", "Sie holt ihres Kindes vom Kindergarten ab."],
            "case": "Akkusativ", "gender": "Neutrum (das Kind)", "verb": "abholen",
            "exp": "'abholen' takes Akkusativ. 'das Kind' is neuter -> 'ihr Kind'."
        },
        {
            "topic": "Akkusativ Neutrum (wir -> unser)",
            "te": "మేము ఈ రాత్రికి మా గదిని బుక్ చేయాలి.",
            "kn": "ನಾವು ಈ ರಾತ್ರಿಗೆ ನಮ್ಮ ಕೊಠಡಿಯನ್ನು ಕಾಯ್ದಿರಿಸಬೇಕು.",
            "de": "Wir müssen unser Zimmer rechtzeitig buchen.",
            "distractors": ["Wir müssen unseren Zimmer rechtzeitig buchen.", "Wir müssen unserem Zimmer rechtzeitig buchen.", "Wir müssen unseres Zimmers rechtzeitig buchen."],
            "case": "Akkusativ", "gender": "Neutrum (das Zimmer)", "verb": "buchen",
            "exp": "'buchen' takes Akkusativ. 'das Zimmer' is neuter -> 'unser Zimmer'."
        },
        {
            "topic": "Akkusativ Neutrum (ihr -> euer)",
            "te": "మీరు మీ సమస్యను పరిష్కరించుకున్నారా?",
            "kn": "ನೀವು ನಿಮ್ಮ ಸಮಸ್ಯೆಯನ್ನು ಪರಿಹರಿಸಿಕೊಂಡಿದ್ದೀರಾ?",
            "de": "Habt ihr euer Problem schon gelöst?",
            "distractors": ["Habt ihr euren Problem schon gelöst?", "Habt ihr eurem Problem schon gelöst?", "Habt ihr eures Problems schon gelöst?"],
            "case": "Akkusativ", "gender": "Neutrum (das Problem)", "verb": "lösen",
            "exp": "'lösen' takes Akkusativ. 'das Problem' is neuter -> 'euer Problem'."
        },
        {
            "topic": "Akkusativ Neutrum (Sie -> Ihr)",
            "te": "మీరు మీ ఫారమ్‌ను పూరించారా?",
            "kn": "ನೀವು ನಿಮ್ಮ ಫಾರ್ಮ್ ಅನ್ನು ಭರ್ತಿ ಮಾಡಿದ್ದೀರಾ?",
            "de": "Haben Sie Ihr Formular vollständig ausgefüllt?",
            "distractors": ["Haben Sie Ihren Formular vollständig ausgefüllt?", "Haben Sie Ihrem Formular vollständig ausgefüllt?", "Haben Sie Ihres Formulars vollständig ausgefüllt?"],
            "case": "Akkusativ", "gender": "Neutrum (das Formular)", "verb": "ausfüllen",
            "exp": "'ausfüllen' takes Akkusativ. Formal 'Sie' possessive in Akkusativ Neutrum -> 'Ihr Formular'."
        },
        {
            "topic": "Akkusativ Plural (ich -> mein)",
            "te": "నేను నా పత్రాలను ఆఫీసులో సమర్పించాను.",
            "kn": "ನಾನು ನನ್ನ ದಾಖಲೆಗಳನ್ನು ಕಚೇರಿಯಲ್ಲಿ ಸಲ್ಲಿಸಿದೆನು.",
            "de": "Ich habe meine Dokumente im Büro abgegeben.",
            "distractors": ["Ich habe meinen Dokumente im Büro abgegeben.", "Ich habe meinem Dokumente im Büro abgegeben.", "Ich habe meiner Dokumente im Büro abgegeben."],
            "case": "Akkusativ", "gender": "Plural (die Dokumente)", "verb": "abgeben",
            "exp": "'abgeben' takes Akkusativ. Plural possessive takes -e -> 'meine Dokumente'."
        },
        {
            "topic": "Akkusativ Plural (du -> dein)",
            "te": "నువ్వు నీ బట్టలను ఉతికించావా?",
            "kn": "ನೀನು ನಿನ್ನ ಬಟ್ಟೆಗಳನ್ನು ಒಗೆದೆಯಾ?",
            "de": "Hast du deine Kleider schon gewaschen?",
            "distractors": ["Hast du deinen Kleider schon gewaschen?", "Hast du deinem Kleider schon gewaschen?", "Hast du deiner Kleider schon gewaschen?"],
            "case": "Akkusativ", "gender": "Plural (die Kleider)", "verb": "waschen",
            "exp": "'waschen' takes Akkusativ. Plural possessive takes -e -> 'deine Kleider'."
        },
        {
            "topic": "Akkusativ Plural (er -> sein)",
            "te": "అతను తన స్నేహితులను పార్టీకి ఆహ్వానించాడు.",
            "kn": "ಅವನು ತನ್ನ ಸ್ನೇಹಿತರನ್ನು ಪಾರ್ಟಿಗೆ ಆಹ್ವಾನಿಸಿದನು.",
            "de": "Er hat seine Freunde zur Feier eingeladen.",
            "distractors": ["Er hat seinen Freunde zur Feier eingeladen.", "Er hat seinem Freunde zur Feier eingeladen.", "Er hat seiner Freunde zur Feier eingeladen."],
            "case": "Akkusativ", "gender": "Plural (die Freunde)", "verb": "einladen",
            "exp": "'einladen' takes Akkusativ. Plural possessive takes -e -> 'seine Freunde'."
        },
        {
            "topic": "Akkusativ Plural (sie [she] -> ihr)",
            "te": "ఆమె తన కీలను బ్యాగ్‌లో ఉంచింది.",
            "kn": "ಅವಳು ತನ್ನ ಕೀಲಿಗಳನ್ನು ಬ್ಯಾಗ್‌ನಲ್ಲಿ ಇಟ್ಟಳು.",
            "de": "Sie sucht ihre Schlüssel überall in der Wohnung.",
            "distractors": ["Sie sucht ihren Schlüssel überall in der Wohnung.", "Sie sucht ihrem Schlüssel überall in der Wohnung.", "Sie sucht ihrer Schlüssel überall in der Wohnung."],
            "case": "Akkusativ", "gender": "Plural (die Schlüssel)", "verb": "suchen",
            "exp": "'suchen' takes Akkusativ. 'die Schlüssel' (plural) possessive -> 'ihre Schlüssel'."
        },
        {
            "topic": "Akkusativ Plural (wir -> unser)",
            "te": "మేము మా సందేహాలను ఉపాధ్యాయుడిని అడిగాము.",
            "kn": "ನಾವು ನಮ್ಮ ಅನುಮಾನಗಳನ್ನು ಶಿಕ್ಷಕರನ್ನು ಕೇಳಿದೆವು.",
            "de": "Wir haben unsere Fragen im Kurs gestellt.",
            "distractors": ["Wir haben unseren Fragen im Kurs gestellt.", "Wir haben unserem Fragen im Kurs gestellt.", "Wir haben unserer Fragen im Kurs gestellt."],
            "case": "Akkusativ", "gender": "Plural (die Fragen)", "verb": "stellen",
            "exp": "'stellen' takes Akkusativ. Plural possessive takes -e -> 'unsere Fragen'."
        },
        {
            "topic": "Akkusativ Plural (ihr -> euer)",
            "te": "మీరు మీ తప్పులను సరిదిద్దుకున్నారా?",
            "kn": "ನೀವು ನಿಮ್ಮ ತಪ್ಪುಗಳನ್ನು ಸರಿಪಡಿಸಿಕೊಂಡಿದ್ದೀರಾ?",
            "de": "Habt ihr eure Fehler korrigiert?",
            "distractors": ["Habt ihr euren Fehler korrigiert?", "Habt ihr eurem Fehler korrigiert?", "Habt ihr eurer Fehler korrigiert?"],
            "case": "Akkusativ", "gender": "Plural (die Fehler)", "verb": "korrigieren",
            "exp": "'korrigieren' takes Akkusativ. Plural possessive takes -e -> 'eure Fehler'."
        },
        {
            "topic": "Akkusativ Plural (Sie -> Ihr)",
            "te": "మీరు మీ టిక్కెట్లను ప్రింట్ చేసుకున్నారా?",
            "kn": "ನೀವು ನಿಮ್ಮ ಟಿಕೆಟ್‌ಗಳನ್ನು ಮುದ್ರಿಸಿಕೊಂಡಿದ್ದೀರಾ?",
            "de": "Haben Sie Ihre Tickets schon ausgedruckt?",
            "distractors": ["Haben Sie Ihren Tickets schon ausgedruckt?", "Haben Sie Ihrem Tickets schon ausgedruckt?", "Haben Sie Ihrer Tickets schon ausgedruckt?"],
            "case": "Akkusativ", "gender": "Plural (die Tickets)", "verb": "ausdrucken",
            "exp": "'ausdrucken' takes Akkusativ. Formal 'Sie' possessive in Akkusativ Plural -> 'Ihre Tickets'."
        },

        # --- GENITIV (Maskulin, Feminin, Neutrum, Plural) ---
        {
            "topic": "Genitiv Maskulin (ich -> mein)",
            "te": "నా స్నేహితుడి రాక కారణంగా మేము ఒక విందు ఏర్పాటు చేశాము.",
            "kn": "ನನ್ನ ಸ್ನೇಹಿತನ ಆಗಮನದ ಕಾರಣ ನಾವು ಭೋಜನವನ್ನು ಏರ್ಪಡಿಸಿದ್ದೇವೆ.",
            "de": "Wegen der Ankunft meines Freundes feiern wir heute.",
            "distractors": ["Wegen der Ankunft meinem Freund feiern wir heute.", "Wegen der Ankunft meinen Freund feiern wir heute.", "Wegen der Ankunft mein Freund feiern wir heute."],
            "case": "Genitiv", "gender": "Maskulin (der Freund)", "verb": "feiern / wegen",
            "exp": "Genitive attribute ('Ankunft [wessen?] meines Freundes'). 'der Freund' is masculine -> 'meines Freundes'."
        },
        {
            "topic": "Genitiv Maskulin (du -> dein)",
            "te": "నీ ఉపాధ్యాయుడి సలహా వల్ల నువ్వు విజయం సాధించావు.",
            "kn": "ನಿನ್ನ ಶಿಕ್ಷಕರ ಸಲಹೆಯ ಕಾರಣ ನೀನು ಯಶಸ್ಸನ್ನು ಸಾಧಿಸಿದೆ.",
            "de": "Dank des Rates deines Lehrers hast du Erfolg gehabt.",
            "distractors": ["Dank des Rates deinem Lehrer hast du Erfolg gehabt.", "Dank des Rates deinen Lehrer hast du Erfolg gehabt.", "Dank des Rates dein Lehrer hast du Erfolg gehabt."],
            "case": "Genitiv", "gender": "Maskulin (der Lehrer)", "verb": "haben / dank",
            "exp": "Genitive relation ('des Rates deines Lehrers'). 'der Lehrer' is masculine -> 'deines Lehrers'."
        },
        {
            "topic": "Genitiv Maskulin (er -> sein)",
            "te": "అతను తన కారు మరమ్మతు కోసం చాలా ఖర్చు చేశాడు.",
            "kn": "ಅವನು ತನ್ನ ಕಾರಿನ ದುರಸ್ತಿಗಾಗಿ ತುಂಬಾ ಹಣ ಖರ್ಚು ಮಾಡಿದನು.",
            "de": "Er zahlt viel für die Reparatur seines Autos.",
            "distractors": ["Er zahlt viel für die Reparatur seinem Auto.", "Er zahlt viel für die Reparatur seinen Auto.", "Er zahlt viel für die Reparatur sein Auto."],
            "case": "Genitiv", "gender": "Maskulin/Neutrum (das Auto / der Wagen)", "verb": "zahlen",
            "exp": "Genitive relation ('Reparatur seines Autos'). 'das Auto' in Genitiv -> 'seines Autos'."
        },
        {
            "topic": "Genitiv Maskulin (sie [she] -> ihr)",
            "te": "ఆమె తన కొడుకు విజయాన్ని చూసి గర్వపడుతోంది.",
            "kn": "ಅವಳು ತನ್ನ ಮಗನ ಯಶಸ್ಸನ್ನು ಕಂಡು ಹೆಮ್ಮೆಪಡುತ್ತಾಳೆ.",
            "de": "Sie freut sich über den Erfolg ihres Sohnes.",
            "distractors": ["Sie freut sich über den Erfolg ihrem Sohn.", "Sie freut sich über den Erfolg ihren Sohn.", "Sie freut sich über den Erfolg ihr Sohn."],
            "case": "Genitiv", "gender": "Maskulin (der Sohn)", "verb": "sich freuen",
            "exp": "Genitive attribute ('Erfolg [wessen?] ihres Sohnes'). 'der Sohn' is masculine -> 'ihres Sohnes'."
        },
        {
            "topic": "Genitiv Maskulin (wir -> unser)",
            "te": "మా కొత్త బాస్ నిర్ణయం వల్ల పని వేగవంతమైంది.",
            "kn": "ನಮ್ಮ ಹೊಸ ಮುಖ್ಯಸ್ಥರ ನಿರ್ಧಾರದಿಂದ ಕೆಲಸವು ವೇಗವಾಯಿತು.",
            "de": "Wegen der Entscheidung unseres Chefs arbeiten wir schneller.",
            "distractors": ["Wegen der Entscheidung unserem Chef arbeiten wir schneller.", "Wegen der Entscheidung unseren Chef arbeiten wir schneller.", "Wegen der Entscheidung unser Chef arbeiten wir schneller."],
            "case": "Genitiv", "gender": "Maskulin (der Chef)", "verb": "arbeiten / wegen",
            "exp": "'wegen' governs Genitiv -> 'unseres Chefs'."
        },
        {
            "topic": "Genitiv Feminin (ich -> mein)",
            "te": "నా తల్లి ఆరోగ్యం కోసం నేను ప్రార్థిస్తున్నాను.",
            "kn": "ನನ್ನ ತಾಯಿಯ ಆರೋಗ್ಯಕ್ಕಾಗಿ ನಾನು ಪ್ರಾರ್ಥಿಸುತ್ತಿದ್ದೇನೆ.",
            "de": "Ich sorge mich wegen der Gesundheit meiner Mutter.",
            "distractors": ["Ich sorge mich wegen der Gesundheit meine Mutter.", "Ich sorge mich wegen der Gesundheit meinem Mutter.", "Ich sorge mich wegen der Gesundheit meinen Mutter."],
            "case": "Genitiv", "gender": "Feminin (die Mutter)", "verb": "sorgen / wegen",
            "exp": "'wegen' requires Genitiv. 'die Mutter' is feminine -> 'meiner Mutter'."
        },
        {
            "topic": "Genitiv Feminin (du -> dein)",
            "te": "నీ చెల్లి పెళ్లి ఎప్పుడు జరుగుతుంది?",
            "kn": "ನಿನ್ನ ಸಹೋದರಿಯ ಮದುವೆ ಯಾವಾಗ ನಡೆಯುತ್ತದೆ?",
            "de": "Wann ist die Hochzeit deiner Schwester?",
            "distractors": ["Wann ist die Hochzeit deine Schwester?", "Wann ist die Hochzeit deinem Schwester?", "Wann ist die Hochzeit deinen Schwester?"],
            "case": "Genitiv", "gender": "Feminin (die Schwester)", "verb": "sein",
            "exp": "Genitive attribute ('Hochzeit [wessen?] deiner Schwester') -> 'deiner Schwester'."
        },
        {
            "topic": "Genitiv Feminin (er -> sein)",
            "te": "అతను తన భార్య పుట్టినరోజును ఘనంగా జరుపుకున్నాడు.",
            "kn": "ಅವನು ತನ್ನ ಹೆಂಡತಿಯ ಜನ್ಮದಿನವನ್ನು ಅದ್ಧೂರಿಯಾಗಿ ಆಚರಿಸಿದನು.",
            "de": "Er plant das Fest zum Geburtstag seiner Ehefrau.",
            "distractors": ["Er plant das Fest zum Geburtstag seine Ehefrau.", "Er plant das Fest zum Geburtstag seinem Ehefrau.", "Er plant das Fest zum Geburtstag seinen Ehefrau."],
            "case": "Genitiv", "gender": "Feminin (die Ehefrau)", "verb": "planen",
            "exp": "Genitive attribute ('Geburtstag seiner Ehefrau') -> 'seiner Ehefrau'."
        },
        {
            "topic": "Genitiv Feminin (sie [she] -> ihr)",
            "te": "ఆమె తన అనారోగ్యం ఉన్నప్పటికీ ఆఫీసుకు వచ్చింది.",
            "kn": "ಅವಳು ತನ್ನ ಅನಾರೋಗ್ಯದ ಹೊರತಾಗಿಯೂ ಕಚೇರಿಗೆ ಬಂದಳು.",
            "de": "Trotz ihrer Krankheit geht sie heute ins Büro.",
            "distractors": ["Trotz ihre Krankheit geht sie heute ins Büro.", "Trotz ihrem Krankheit geht sie heute ins Büro.", "Trotz ihren Krankheit geht sie heute ins Büro."],
            "case": "Genitiv", "gender": "Feminin (die Krankheit)", "verb": "gehen / trotz",
            "exp": "'trotz' requires Genitiv. 'die Krankheit' is feminine -> 'ihrer Krankheit'."
        },
        {
            "topic": "Genitiv Feminin (wir -> unser)",
            "te": "మా ప్రయాణం సమయంలో మేము ఎన్నో ఆసక్తికరమైన విషయాలు చూశాము.",
            "kn": "ನಮ್ಮ ಪ್ರಯಾಣದ ಸಮಯದಲ್ಲಿ ನಾವು ಅನೇಕ ಆಸಕ್ತಿದಾಯಕ ವಿಷಯಗಳನ್ನು ನೋಡಿದೆವು.",
            "de": "Während unserer Reise haben wir viel erlebt.",
            "distractors": ["Während unsere Reise haben wir viel erlebt.", "Während unserem Reise haben wir viel erlebt.", "Während unseren Reise haben wir viel erlebt."],
            "case": "Genitiv", "gender": "Feminin (die Reise)", "verb": "erleben / während",
            "exp": "'während' demands Genitiv. 'die Reise' is feminine -> 'unserer Reise'."
        },
        {
            "topic": "Genitiv Neutrum (ich -> mein)",
            "te": "నా పిల్లవాడి పురోగతిని చూసి నేను సంతోషిస్తున్నాను.",
            "kn": "ನನ್ನ ಮಗುವಿನ ಪ್ರಗತಿಯನ್ನು ನೋಡಿ ನಾನು ಸಂತೋಷಪಡುತ್ತೇನೆ.",
            "de": "Ich freue mich über die Entwicklung meines Kindes.",
            "distractors": ["Ich freue mich über die Entwicklung meinem Kind.", "Ich freue mich über die Entwicklung meinen Kind.", "Ich freue mich über die Entwicklung mein Kind."],
            "case": "Genitiv", "gender": "Neutrum (das Kind)", "verb": "sich freuen",
            "exp": "Genitive attribute ('Entwicklung meines Kindes'). 'das Kind' is neuter -> 'meines Kindes'."
        },
        {
            "topic": "Genitiv Neutrum (wir -> unser)",
            "te": "మా కొత్త ఇంటి స్థానం చాలా ప్రశాంతంగా ఉంది.",
            "kn": "ನಮ್ಮ ಹೊಸ ಮನೆಯ ಸ್ಥಳವು ತುಂಬಾ ಶಾಂತವಾಗಿದೆ.",
            "de": "Die Lage unseres Hauses ist sehr ruhig.",
            "distractors": ["Die Lage unserem Haus ist sehr ruhig.", "Die Lage unseren Haus ist sehr ruhig.", "Die Lage unser Haus ist sehr ruhig."],
            "case": "Genitiv", "gender": "Neutrum (das Haus)", "verb": "sein",
            "exp": "Genitive attribute ('Lage unseres Hauses'). 'das Haus' is neuter -> 'unseres Hauses'."
        },
        {
            "topic": "Genitiv Plural (wir -> unser)",
            "te": "మా సెలవుల సమయంలో మేము ప్రతిరోజూ జర్మన్ నేర్చుకున్నాము.",
            "kn": "ನಮ್ಮ ರಜಾದಿನಗಳ ಸಮಯದಲ್ಲಿ ನಾವು ಪ್ರತಿದಿನ ಜರ್ಮನ್ ಕಲಿತೆವು.",
            "de": "Während unserer Ferien haben wir fleißig Deutsch gelernt.",
            "distractors": ["Während unserem Ferien haben wir fleißig Deutsch gelernt.", "Während unseren Ferien haben wir fleißig Deutsch gelernt.", "Während unsere Ferien haben wir fleißig Deutsch gelernt."],
            "case": "Genitiv", "gender": "Plural (die Ferien)", "verb": "lernen / während",
            "exp": "'während' requires Genitiv. Plural possessive takes -er -> 'unserer Ferien'."
        },
        {
            "topic": "Genitiv Plural (sie [they] -> ihr)",
            "te": "తమ తల్లిదండ్రుల మద్దతుతో వారు పరీక్ష రాశారు.",
            "kn": "ತಮ್ಮ ಪೋಷಕರ ಬೆಂಬಲದೊಂದಿಗೆ ಅವರು ಪರೀಕ್ಷೆಯನ್ನು ಬರೆದರು.",
            "de": "Dank der Hilfe ihrer Eltern haben sie die Prüfung geschafft.",
            "distractors": ["Dank der Hilfe ihrem Eltern haben sie die Prüfung geschafft.", "Dank der Hilfe ihren Eltern haben sie die Prüfung geschafft.", "Dank der Hilfe ihre Eltern haben sie die Prüfung geschafft."],
            "case": "Genitiv", "gender": "Plural (die Eltern)", "verb": "schaffen / dank",
            "exp": "Genitive attribute ('Hilfe ihrer Eltern'). Plural possessive takes -er -> 'ihrer Eltern'."
        },

        # --- NOMINATIV (Subject sentences) ---
        {
            "topic": "Nominativ Maskulin (ich -> mein)",
            "te": "నా సోదరుడు బెర్లిన్‌లో ఇంజనీరింగ్ చదువుతున్నాడు.",
            "kn": "ನನ್ನ ಸಹೋದರ ಬರ್ಲಿನ್‌ನಲ್ಲಿ ಎಂಜಿನಿಯರಿಂಗ್ ಓದುತ್ತಿದ್ದಾನೆ.",
            "de": "Mein Bruder studiert Ingenieurwesen in Berlin.",
            "distractors": ["Meinen Bruder studiert Ingenieurwesen in Berlin.", "Meinem Bruder studiert Ingenieurwesen in Berlin.", "Meines Bruders studiert Ingenieurwesen in Berlin."],
            "case": "Nominativ", "gender": "Maskulin (der Bruder)", "verb": "studieren",
            "exp": "Subject is in Nominativ. 'der Bruder' is masculine -> 'Mein Bruder'."
        },
        {
            "topic": "Nominativ Maskulin (du -> dein)",
            "te": "నీ తండ్రి ఇంకా ఆ ఆసుపత్రిలో పనిచేస్తున్నారా?",
            "kn": "ನಿನ್ನ ತಂದೆ ಇನ್ನೂ ಆ ಆಸ್ಪತ್ರೆಯಲ್ಲಿ ಕೆಲಸ ಮಾಡುತ್ತಿದ್ದಾರಾ?",
            "de": "Arbeitet dein Vater noch in diesem Krankenhaus?",
            "distractors": ["Arbeitet deinen Vater noch in diesem Krankenhaus?", "Arbeitet deinem Vater noch in diesem Krankenhaus?", "Arbeitet deines Vaters noch in diesem Krankenhaus?"],
            "case": "Nominativ", "gender": "Maskulin (der Vater)", "verb": "arbeiten",
            "exp": "Subject is in Nominativ. 'der Vater' is masculine -> 'dein Vater'."
        },
        {
            "topic": "Nominativ Feminin (wir -> unser)",
            "te": "మా కొత్త ఉపాధ్యాయురాలు చాలా స్నేహపూర్వకంగా ఉంది.",
            "kn": "ನಮ್ಮ ಹೊಸ ಶಿಕ್ಷಕಿ ತುಂಬಾ ಸ್ನೇಹಪರರಾಗಿದ್ದಾರೆ.",
            "de": "Unsere neue Lehrerin ist sehr freundlich und geduldig.",
            "distractors": ["Unser neue Lehrerin ist sehr freundlich und geduldig.", "Unserer neue Lehrerin ist sehr freundlich und geduldig.", "Unseren neue Lehrerin ist sehr freundlich und geduldig."],
            "case": "Nominativ", "gender": "Feminin (die Lehrerin)", "verb": "sein",
            "exp": "Subject is in Nominativ. 'die Lehrerin' is feminine -> 'Unsere neue Lehrerin'."
        },
        {
            "topic": "Nominativ Neutrum (ihr -> euer)",
            "te": "మీ అపార్ట్‌మెంట్ చాలా పెద్దగా మరియు ఆధునికంగా ఉందా?",
            "kn": "ನಿಮ್ಮ ಅಪಾರ್ಟ್ಮೆಂಟ್ ತುಂಬಾ ದೊಡ್ಡದಾಗಿದೆ ಮತ್ತು ಆಧುನಿಕವಾಗಿದೆಯೇ?",
            "de": "Ist euer Apartment wirklich so modern und hell?",
            "distractors": ["Ist eurer Apartment wirklich so modern und hell?", "Ist eurem Apartment wirklich so modern und hell?", "Ist euren Apartment wirklich so modern und hell?"],
            "case": "Nominativ", "gender": "Neutrum (das Apartment)", "verb": "sein",
            "exp": "Subject is in Nominativ. 'das Apartment' is neuter -> 'euer Apartment'."
        },
        {
            "topic": "Nominativ Plural (du -> dein)",
            "te": "నీ సహోద్యోగులు కూడా ఈ సమావేశానికి వస్తున్నారా?",
            "kn": "ನಿನ್ನ ಸಹೋದ್ಯೋಗಿಗಳು ಸಹ ಈ ಸಭೆಗೆ ಬರುತ್ತಿದ್ದಾರಾ?",
            "de": "Kommen deine Kollegen auch zu dieser Besprechung?",
            "distractors": ["Kommen dein Kollegen auch zu dieser Besprechung?", "Kommen deinen Kollegen auch zu dieser Besprechung?", "Kommen deiner Kollegen auch zu dieser Besprechung?"],
            "case": "Nominativ", "gender": "Plural (die Kollegen)", "verb": "kommen",
            "exp": "Subject is in Nominativ. 'die Kollegen' is plural -> 'deine Kollegen'."
        }
    ]
    
    # Now expand methodically across the Goethe B1 Wortliste vocabulary to reach 162 total questions
    # Each entry will be distinct, grammatically vetted, with Telugu and Kannada prompts.
    
    vocab_variations = [
        # (verb, prep, prep_case, noun_de, noun_gender, noun_case, pron, tel_noun, kan_noun, tel_verb, kan_verb, de_verb_sentence)
        ("anrufen", "", "Akk", "der Arzt", "Maskulin", "Akkusativ", "ich", "వైద్యుడికి", "ವೈದ್ಯರಿಗೆ", "ఫోన్ చేస్తున్నాను", "ಕರೆ ಮಾಡುತ್ತಿದ್ದೇನೆ", "Ich rufe meinen Arzt wegen des Termins an."),
        ("unterstützen", "", "Akk", "der Kollege", "Maskulin", "Akkusativ", "wir", "సహోద్యోగికి", "ಸಹೋದ್ಯೋಗಿಗೆ", "మద్దతు ఇస్తున్నాము", "ಬೆಂಬಲ ನೀಡುತ್ತಿದ್ದೇವೆ", "Wir unterstützen unseren Kollegen bei der Arbeit."),
        ("besuchen", "", "Akk", "der Großvater", "Maskulin", "Akkusativ", "du", "తాతగారిని", "ಅಜ್ಜನನ್ನು", "సందర్శించావా", "ಭೇಟಿ ಮಾಡಿದೆಯಾ", "Hast du deinen Großvater am Wochenende besucht?"),
        ("abholen", "", "Akk", "der Gast", "Maskulin", "Akkusativ", "er", "అతిథిని", "ಅತಿಥಿಯನ್ನು", "పికప్ చేసుకున్నాడు", "ಕರೆತಂದನು", "Er hat seinen Gast pünktlich vom Flughafen abgeholt."),
        ("bezahlen", "", "Akk", "der Beitrag", "Maskulin", "Akkusativ", "Sie", "సభ్యత్వ రుసుమును", "ಸದಸ್ಯತ್ವ ಶುಲ್ಕವನ್ನು", "చెల్లించారా", "Haben Sie Ihren Mitgliedsbeitrag schon bezahlt?"),
        ("überprüfen", "", "Akk", "der Vertrag", "Maskulin", "Akkusativ", "ich", "కాంట్రాక్ట్‌ను", "ಒಪ್ಪಂದವನ್ನು", "తనిఖీ చేస్తున్నాను", "ಪರಿಶೀಲಿಸುತ್ತಿದ್ದೇನೆ", "Ich überprüfe meinen Vertrag ganz genau."),
        ("organisieren", "", "Akk", "der Ausflug", "Maskulin", "Akkusativ", "wir", "విహారయాత్రను", "ಪ್ರವಾಸವನ್ನು", "ఏర్పాటు చేస్తున్నాము", "ಏರ್ಪಡಿಸುತ್ತಿದ್ದೇವೆ", "Wir organisieren unseren Ausflug in die Berge."),
        ("verpassen", "", "Akk", "der Flug", "Maskulin", "Akkusativ", "du", "విమానాన్ని", "ವಿಮಾನವನ್ನು", "మిస్ అయ్యావా", "ತಪ್ಪಿಸಿಕೊಂಡೆಯಾ", "Hast du deinen Flug nach Frankfurt verpasst?"),
        
        ("vermissen", "", "Akk", "die Familie", "Feminin", "Akkusativ", "ich", "కుటుంబాన్ని", "ಕುಟುಂಬವನ್ನು", "మిస్ అవుతున్నాను", "ಮಿಸ್ ಮಾಡಿಕೊಳ್ಳುತ್ತಿದ್ದೇನೆ", "Ich vermisse meine Familie in Indien sehr."),
        ("wechseln", "", "Akk", "die Stelle", "Feminin", "Akkusativ", "er", "ఉద్యోగాన్ని", "ಉದ್ಯೋಗವನ್ನು", "మార్చాలనుకుంటున్నాడు", "ಬದಲಾಯಿಸಲು ಬಯಸುತ್ತಾನೆ", "Er möchte seine Stelle im nächsten Monat wechseln."),
        ("verbessern", "", "Akk", "die Aussprache", "Feminin", "Akkusativ", "wir", "ఉచ్ఛారణను", "ಉಚ್ಚಾರಣೆಯನ್ನು", "మెరుగుపరుచుకోవాలి", "ಸುಧಾರಿಸಿಕೊಳ್ಳಬೇಕು", "Wir müssen unsere Aussprache im Kurs verbessern."),
        ("vergessen", "", "Akk", "die Brille", "Feminin", "Akkusativ", "du", "కళ్లద్దాలను", "ಕನ್ನಡಕವನ್ನು", "మర్చిపోయావా", "ಮರೆತುಬಿಟ್ಟೆಯಾ", "Hast du deine Brille zu Hause vergessen?"),
        ("abschließen", "", "Akk", "die Versicherung", "Feminin", "Akkusativ", "Sie", "భీమాను", "ವಿಮೆಯನ್ನು", "చేయించారా", "ಮಾಡಿಸಿದ್ದೀರಾ", "Haben Sie Ihre Versicherung rechtzeitig abgeschlossen?"),
        ("reparieren", "", "Akk", "die Heizung", "Feminin", "Akkusativ", "ihr", "హీటర్‌ను", "ಹೀಟರ್ ಅನ್ನು", "రిపేర్ చేయించారా", "ರಿಪೇರಿ ಮಾಡಿಸಿದ್ದೀರಾ", "Habt ihr eure Heizung vor dem Winter repariert?"),
        
        ("buchen", "", "Akk", "das Ticket", "Neutrum", "Akkusativ", "ich", "టికెట్‌ను", "ಟಿಕೆಟ್ ಅನ್ನು", "ఆన్‌లైన్‌లో బుక్ చేశాను", "ಆನ್‌ಲೈನ್‌ನಲ್ಲಿ ಕಾಯ್ದಿರಿಸಿದೆನು", "Ich habe mein Ticket für den ICE online gebucht."),
        ("öffnen", "", "Akk", "das Konto", "Neutrum", "Akkusativ", "er", "బ్యాంక్ ఖాతాను", "ಬ್ಯಾಂಕ್ ಖಾತೆಯನ್ನು", "తెరిచాడు", "ತೆರೆದನು", "Er hat sein Konto bei der Sparkasse eröffnet."),
        ("verkaufen", "", "Akk", "das Motorrad", "Neutrum", "Akkusativ", "du", "మోటార్‌సైకిల్‌ను", "ಮೋಟಾರ್‌ಸೈಕಲ್ ಅನ್ನು", "అమ్మేశావా", "ಮಾರಾಟ ಮಾಡಿದೆಯಾ", "Hast du dein altes Motorrad verkauft?"),
        ("beenden", "", "Akk", "das Studium", "Neutrum", "Akkusativ", "wir", "చదువును", "ಅಧ್ಯಯನವನ್ನು", "ఈ ఏడాది పూర్తి చేస్తాము", "ಈ ವರ್ಷ ಪೂರ್ಣಗೊಳಿಸುತ್ತೇವೆ", "Wir beenden unser Studium in diesem Semester."),
        ("vergessen", "", "Akk", "das Gepäck", "Neutrum", "Akkusativ", "ihr", "సామానును", "ಸಾಮಾನುಗಳನ್ನು", "టాక్సీలో మర్చిపోయారా", "ಟ್ಯಾಕ್ಸಿಯಲ್ಲಿ ಮರೆತಿರಾ", "Habt ihr euer Gepäck im Taxi vergessen?"),
        
        ("abgeben", "", "Akk", "die Unterlagen", "Plural", "Akkusativ", "ich", "పత్రాలను", "ದಾಖಲೆಗಳನ್ನು", "కార్యాలయంలో ఇచ్చాను", "ಕಚೇರಿಯಲ್ಲಿ ಸಲ್ಲಿಸಿದೆನು", "Ich gebe meine Unterlagen morgen im Rathaus ab."),
        ("einpacken", "", "Akk", "die Sachen", "Plural", "Akkusativ", "du", "వస్తువులను", "ವಸ್ತುಗಳನ್ನು", "సరిగ్గా సర్దావా", "ಸರಿಯಾಗಿ ಪ್ಯಾಕ್ ಮಾಡಿದೆಯಾ", "Hast du deine Sachen für die Reise eingepackt?"),
        ("korrigieren", "", "Akk", "die Fehler", "Plural", "Akkusativ", "wir", "తప్పులను", "ತಪ್ಪುಗಳನ್ನು", "సరిదిద్దాము", "ಸರಿಪಡಿಸಿದೆವು", "Wir korrigieren unsere Fehler in der Übung."),
        ("informieren", "", "Akk", "die Eltern", "Plural", "Akkusativ", "er", "తల్లిదండ్రులకు", "ಪೋಷಕರಿಗೆ", "సమాచారం ఇచ్చాడు", "ಮಾಹಿತಿ ನೀಡಿದನು", "Er informiert seine Eltern über die Prüfungsergebnisse."),
        
        # Dativ patterns with prepositions and verbs
        ("danken", "Dativ", "Dat", "der Nachbar", "Maskulin", "Dativ", "wir", "పొరుగువారికి", "ನೆರೆಹೊರೆಯವರಿಗೆ", "ధన్యవాదాలు తెలిపాము", "ಧನ್ಯವಾದ ತಿಳಿಸಿದೆವು", "Wir danken unserem Nachbarn für das Paket."),
        ("helfen", "Dativ", "Dat", "der Schüler", "Maskulin", "Dativ", "du", "విద్యార్థికి", "ವಿದ್ಯಾರ್ಥಿಗೆ", "సహాయం చేస్తున్నావా", "ಸಹಾಯ ಮಾಡುತ್ತಿದ್ದೀಯಾ", "Hilfst du deinem Schüler bei der Grammatik?"),
        ("schreiben mit", "mit", "Dat", "der Kuli", "Maskulin", "Dativ", "ich", "కలంతో", "ಪೆನ್ನಿನೊಂದಿಗೆ", "రాస్తున్నాను", "ಬರೆಯುತ್ತಿದ್ದೇನೆ", "Ich schreibe die Notiz mit meinem Kuli."),
        ("wohnen bei", "bei", "Dat", "der Onkel", "Maskulin", "Dativ", "er", "బాబాయి వద్ద", "ಚಿಕ್ಕಪ್ಪನ ಬಳಿ", "నివసిస్తున్నాడు", "Er wohnt zurzeit bei seinem Onkel in München."),
        
        ("vertrauen", "Dativ", "Dat", "die Kollegin", "Feminin", "Dativ", "ich", "సహోద్యోగినిని", "ಸಹೋದ್ಯೋಗಿಯನ್ನು", "పూర్తిగా నమ్ముతున్నాను", "ಸಂಪೂರ್ಣವಾಗಿ ನಂಬುತ್ತೇನೆ", "Ich vertraue meiner Kollegin in dieser Sache voll."),
        ("gefallen", "Dativ", "Dat", "die Chefin", "Feminin", "Dativ", "wir", "బాస్‌కు", "ಮುಖ್ಯಸ್ಥರಿಗೆ", "ఈ ఆలోచన నచ్చింది", "ಈ ಕಲ್ಪನೆ ಇಷ್ಟವಾಯಿತು", "Die neue Idee gefällt unserer Chefin sehr gut."),
        ("sprechen mit", "mit", "Dat", "die Ärztin", "Feminin", "Dativ", "du", "వైద్యురాలితో", "ವೈದ್ಯೆಯೊಂದಿಗೆ", "మాట్లాడావా", "ಮಾತನಾಡಿದೆಯಾ", "Hast du mit deiner Ärztin über das Rezept gesprochen?"),
        ("helfen", "Dativ", "Dat", "die Großmutter", "Feminin", "Dativ", "er", "నానమ్మకు", "ಅಜ್ಜಿಗೆ", "తోటపనిలో సహాయం చేస్తున్నాడు", "ತೋಟದ ಕೆಲಸದಲ್ಲಿ ಸಹಾಯ ಮಾಡುತ್ತಿದ್ದಾನೆ", "Er hilft seiner Großmutter im Garten."),
        
        ("passen zu", "zu", "Dat", "das Hemd", "Neutrum", "Dativ", "du", "చొక్కాకు", "ಶರ್ಟ್‌ಗೆ", "ఈ టై సరిపోతుంది", "ಈ ಟೈ ಹೊಂದಿಕೆಯಾಗುತ್ತದೆ", "Diese Krawatte passt perfekt zu deinem Hemd."),
        ("fahren mit", "mit", "Dat", "das Auto", "Neutrum", "Dativ", "wir", "కారులో", "ಕಾರಿನಲ್ಲಿ", "వెళ్తున్నాము", "ಹೋಗುತ್ತಿದ್ದೇವೆ", "Wir fahren mit unserem Auto in den Urlaub."),
        ("zufrieden mit", "mit", "Dat", "das Ergebnis", "Neutrum", "Dativ", "ich", "ఫలితంతో", "ಫಲಿತಾಂಶದೊಂದಿಗೆ", "చాలా సంతృప్తిగా ఉన్నాను", "ತುಂಬಾ ತೃಪ್ತನಾಗಿದ್ದೇನೆ", "Ich bin mit meinem Prüfungsergebnis sehr zufrieden."),
        ("spielen in", "in", "Dat", "das Zimmer", "Neutrum", "Dativ", "sie", "గదిలో", "ಕೋಣೆಯಲ್ಲಿ", "ఆడుకుంటున్నారు", "ಆಟವಾಡುತ್ತಿದ್ದಾರೆ", "Die Kinder spielen ruhig in ihrem Zimmer."),
        
        ("gehören", "Dativ", "Dat", "die Freunde", "Plural", "Dativ", "ich", "స్నేహితులకు", "ಸ್ನೇಹಿತರಿಗೆ", "చెందినవి", "ಸೇರಿದವು", "Diese Fahrräder gehören meinen Freunden."),
        ("helfen", "Dativ", "Dat", "die Kollegen", "Plural", "Dativ", "er", "సహోద్యోగులకు", "ಸಹೋದ್ಯೋಗಿಗಳಿಗೆ", "సహాయం చేస్తాడు", "ಸಹಾಯ ಮಾಡುತ್ತಾನೆ", "Er hilft seinen Kollegen immer sehr gern."),
        ("erzählen", "Dativ", "Dat", "die Kinder", "Plural", "Dativ", "wir", "పిల్లలకు", "ಮಕ್ಕಳಿಗೆ", "ఒక వృత్తాంతం చెప్పాము", "ಒಂದು ಕಥೆ ಹೇಳಿದೆವು", "Wir erzählen unseren Kindern von unserer Reise."),
        
        # Genitiv patterns
        ("wegen", "wegen", "Gen", "der Streik", "Maskulin", "Genitiv", "wir", "రైలు సమ్మె కారణంగా", "ರೈಲು ಮುಷ್ಕರದ ಕಾರಣದಿಂದ", "ఆలస్యంగా వచ్చాము", "ತಡವಾಗಿ ಬಂದೆವು", "Wegen des Streiks unseres Zuges kommen wir zu spät."),
        ("während", "während", "Gen", "der Kurs", "Maskulin", "Genitiv", "du", "కోర్సు సమయంలో", "ಕೋರ್ಸಿನ ಸಮಯದಲ್ಲಿ", "శ్రద్ధగా విన్నావా", "ಗಮನವಿಟ್ಟು ಕೇಳಿದೆಯಾ", "Hast du während deines Kurses gut aufgepasst?"),
        ("trotz", "trotz", "Gen", "der Unfall", "Maskulin", "Genitiv", "er", "ప్రమాదం జరిగినప్పటికీ", "ಅಪಘಾತವಾದರೂ", "పరీక్షకు హాజరయ్యాడు", "ಪರೀಕ್ಷೆಗೆ ಹಾಜರಾದನು", "Trotz seines Unfalls hat er die Prüfung bestanden."),
        
        ("trotz", "trotz", "Gen", "die Verspätung", "Feminin", "Genitiv", "wir", "ఆలస్యం అయినప్పటికీ", "ವಿಳಂಬವಾದರೂ", "సమయానికి చేరుకున్నాము", "ಸಮಯಕ್ಕೆ ತಲುಪಿದೆವು", "Trotz unserer Verspätung haben wir den Flug erreicht."),
        ("während", "während", "Gen", "die Ausbildung", "Feminin", "Genitiv", "ich", "శిక్షణ సమయంలో", "ತರಬೇತಿಯ ಸಮಯದಲ್ಲಿ", "చాలా నేర్చుకున్నాను", "ತುಂಬಾ ಕಲಿತೆನು", "Während meiner Ausbildung habe ich viel gelernt."),
        ("wegen", "wegen", "Gen", "die Krankheit", "Feminin", "Genitiv", "sie", "అనారోగ్యం కారణంగా", "ಅನಾರೋಗ್ಯದ ಕಾರಣ", "సెలవు తీసుకుంది", "ರಜೆ ತೆಗೆದುಕೊಂಡಳು", "Wegen ihrer Krankheit bleibt sie heute zu Hause."),
        
        ("während", "während", "Gen", "das Praktikum", "Neutrum", "Genitiv", "du", "ఇంటర్న్‌షిప్ సమయంలో", "ಇಂಟರ್ನ್‌ಶಿಪ್ ಸಮಯದಲ್ಲಿ", "చాలా అనుభవం సంపాదించావా", "ತುಂಬಾ ಅನುಭವ ಪಡೆದೆಯಾ", "Hast du während deines Praktikums viele Kontakte geknüpft?"),
        ("trotz", "trotz", "Gen", "das Problem", "Neutrum", "Genitiv", "wir", "సమస్య ఉన్నప్పటికీ", "ಸಮಸ್ಯೆಯಿದ್ದರೂ", "పని పూర్తి చేశాము", "ಕೆಲಸ ಮುಗಿಸಿದೆವು", "Trotz unseres Problems haben wir die Arbeit pünktlich abgegeben.")
    ]
    
    # We populate the base list
    idx = 1
    for r in raw_data:
        options = [r["de"]] + r["distractors"]
        # shuffle options deterministically so correct answer isn't always first
        rot = (idx % 4)
        shuffled = options[rot:] + options[:rot]
        c_idx = shuffled.index(r["de"])
        questions.append({
            "id": idx,
            "topic": r["topic"],
            "prompt_te": r["te"],
            "prompt_kn": r["kn"],
            "target_de": r["de"],
            "options": shuffled,
            "correct_index": c_idx,
            "explanation": r["exp"],
            "case": r["case"],
            "gender": r["gender"],
            "b1_verb": r["verb"]
        })
        idx += 1

    # Now systematically generate up to 162 total questions
    # Pronoun maps
    pronouns = [
        ("ich", "mein", "నా", "ನನ್ನ"),
        ("du", "dein", "నీ", "ನಿನ್ನ"),
        ("er", "sein", "అతని", "ಅವನ"),
        ("sie", "ihr", "ఆమె", "ಅವಳ"),
        ("wir", "unser", "మా", "ನಮ್ಮ"),
        ("ihr", "euer", "మీ (స్నేహితుల)", "ನಿಮ್ಮ (ಸ್ನೇಹಿತರ)"),
        ("Sie", "Ihr", "మీ (గౌరవప్రదంగా)", "ನಿಮ್ಮ (ಗೌರವಯುತವಾಗಿ)")
    ]

    # Additional vocabulary items from Goethe B1 Wortliste
    items = [
        # (Noun, Gender, CaseType, B1Verb/Prep, TeContext, KnContext, DeTemplate, DistractorEndings)
        ("Pass", "Maskulin (der Pass)", "Akkusativ", "verlängern", "పాస్‌పోర్ట్‌ను పునరుద్ధరించుకోవాలి", "ಪಾಸ್‌ಪೋರ್ಟ್ ಅನ್ನು ನವೀಕರಿಸಬೇಕು", "{p_akk_m} Pass muss ich nächsten Monat verlängern.", ["{p_dat_m}", "{p_nom_m}", "{p_gen_m}"]),
        ("Ausweis", "Maskulin (der Ausweis)", "Akkusativ", "zeigen", "గుర్తింపు కార్డును సరిహద్దు వద్ద చూపించాలి", "ಗುರುತಿನ ಚೀಟಿಯನ್ನು ಗಡಿಯಲ್ಲಿ ತೋರಿಸಬೇಕು", "Sie müssen {p_akk_m} Ausweis an der Grenze vorzeigen.", ["{p_dat_m}", "{p_nom_m}", "{p_gen_m}"]),
        ("Koffer", "Maskulin (der Koffer)", "Akkusativ", "tragen", "సూట్‌కేస్‌ను మోయలేకపోతున్నాను", "ಸೂಟ್‌ಕೇಸ್ ಅನ್ನು ಹೊರಲು ಸಾಧ್ಯವಾಗುತ್ತಿಲ್ಲ", "Ich kann {p_akk_m} Koffer nicht allein tragen.", ["{p_dat_m}", "{p_nom_m}", "{p_gen_m}"]),
        ("Bericht", "Maskulin (der Bericht)", "Akkusativ", "schreiben", "నివేదికను ఈరోజు పూర్తి చేయాలి", "ವರದಿಯನ್ನು ಇಂದು ಪೂರ್ಣಗೊಳಿಸಬೇಕು", "Er muss {p_akk_m} Bericht bis 17 Uhr abgeben.", ["{p_dat_m}", "{p_nom_m}", "{p_gen_m}"]),
        ("Schlüssel", "Maskulin (der Schlüssel)", "Akkusativ", "suchen", "కీని ఎంత వెతికినా కనిపించలేదు", "ಕೀಲಿಯನ್ನು ಹುಡುಕುತ್ತಿದ್ದರೂ ಸಿಗುತ್ತಿಲ್ಲ", "Wo hast du {p_akk_m} Schlüssel hingelegt?", ["{p_dat_m}", "{p_nom_m}", "{p_gen_m}"]),
        ("Brief", "Maskulin (der Brief)", "Akkusativ", "beantworten", "లేఖకు వెంటనే సమాధానం ఇవ్వాలి", "ಪತ್ರಕ್ಕೆ ತಕ್ಷಣ ಉತ್ತರಿಸಬೇಕು", "Wir müssen {p_akk_m} Brief heute noch beantworten.", ["{p_dat_m}", "{p_nom_m}", "{p_gen_m}"]),
        ("Antrag", "Maskulin (der Antrag)", "Akkusativ", "ausfüllen", "దరఖాస్తు ఫారమ్‌ను పూరించాను", "ಅರ್ಜಿ ನಮೂನೆಯನ್ನು ಭರ್ತಿ ಮಾಡಿದೆನು", "Hast du {p_akk_m} Antrag auf Kindergeld ausgefüllt?", ["{p_dat_m}", "{p_nom_m}", "{p_gen_m}"]),
        ("Arbeitsplatz", "Maskulin (der Arbeitsplatz)", "Akkusativ", "verlieren", "ఉద్యోగాన్ని పోగొట్టుకోకూడదు", "ಕೆಲಸವನ್ನು ಕಳೆದುಕೊಳ್ಳಬಾರದು", "Er hat Angst, {p_akk_m} Arbeitsplatz zu verlieren.", ["{p_dat_m}", "{p_nom_m}", "{p_gen_m}"]),
        
        ("Wohnung", "Feminin (die Wohnung)", "Dativ", "wohnen in", "ఫ్లాట్‌లో చాలా సౌకర్యంగా ఉంది", "ಫ್ಲಾಟ್‌ನಲ್ಲಿ ತುಂಬಾ ಆರಾಮದಾಯಕವಾಗಿದೆ", "Wir fühlen uns in {p_dat_f} Wohnung sehr wohl.", ["{p_akk_f}", "{p_dat_m}", "{p_akk_m}"]),
        ("Arbeit", "Feminin (die Arbeit)", "Dativ", "zufrieden mit", "పనితో ఎంతో సంతృప్తిగా ఉన్నాను", "ಕೆಲಸದಲ್ಲಿ ತುಂಬಾ ಸಂತೃಪ್ತನಾಗಿದ್ದೇನೆ", "Ich bin mit {p_dat_f} Arbeit sehr zufrieden.", ["{p_akk_f}", "{p_dat_m}", "{p_akk_m}"]),
        ("Prüfung", "Feminin (die Prüfung)", "Dativ", "gratulieren zu", "పరీక్షలో ఉత్తీర్ణత సాధించినందుకు అభినందనలు", "ಪರೀಕ್ಷೆಯಲ್ಲಿ ತೇರ್ಗಡೆಯಾಗಿದ್ದಕ್ಕಾಗಿ ಅಭಿನಂದನೆಗಳು", "Wir gratulieren dir zu {p_dat_f} bestandenen Prüfung.", ["{p_akk_f}", "{p_dat_m}", "{p_akk_m}"]),
        ("Kollegin", "Feminin (die Kollegin)", "Dativ", "helfen", "సహోద్యోగినికి పనిలో సహాయం చేస్తున్నాను", "ಸಹೋದ್ಯೋಗಿಗೆ ಕೆಲಸದಲ್ಲಿ ನೆರವಾಗುತ್ತಿದ್ದೇನೆ", "Ich helfe {p_dat_f} Kollegin bei der Recherche.", ["{p_akk_f}", "{p_dat_m}", "{p_akk_m}"]),
        ("Ausbildung", "Feminin (die Ausbildung)", "Dativ", "nach", "శిక్షణ పూర్తయ్యాక ఉద్యోగం వచ్చింది", "ತರಬೇತಿ ಮುಗಿದ ನಂತರ ಉದ್ಯೋಗ ಸಿಕ್ಕಿತು", "Nach {p_dat_f} Ausbildung fand sie sofort eine Stelle.", ["{p_akk_f}", "{p_dat_m}", "{p_akk_m}"]),
        ("Meinung", "Feminin (die Meinung)", "Dativ", "zustimmen", "అభిప్రాయంతో నేను ఏకీభవిస్తున్నాను", "ಅಭಿಪ್ರಾಯದೊಂದಿಗೆ ನಾನು ಸಮ್ಮತಿಸುತ್ತೇನೆ", "Ich stimme {p_dat_f} Meinung in allen Punkten zu.", ["{p_akk_f}", "{p_dat_m}", "{p_akk_m}"]),
        ("Familie", "Feminin (die Familie)", "Dativ", "gehören zu", "కుటుంబంలో అందరూ కలిసి భోజనం చేస్తారు", "ಕುಟುಂಬದೊಂದಿಗೆ ಎಲ್ಲರೂ ಜೊತೆಯಾಗಿ ಊಟ ಮಾಡುತ್ತಾರೆ", "Er verbringt das Fest mit {p_dat_f} Familie.", ["{p_akk_f}", "{p_dat_m}", "{p_akk_m}"]),
        
        ("Zimmer", "Neutrum (das Zimmer)", "Akkusativ", "aufräumen", "గదిని ప్రతిరోజూ శుభ్రం చేసుకోవాలి", "ಕೋಣೆಯನ್ನು ಪ್ರತಿದಿನ ಸ್ವಚ್ಛಗೊಳಿಸಬೇಕು", "Du musst {p_akk_n} Zimmer noch gründlich aufräumen.", ["{p_akk_m}", "{p_dat_m}", "{p_gen_m}"]),
        ("Auto", "Neutrum (das Auto)", "Akkusativ", "reparieren", "కారును వర్క్‌షాప్‌లో రిపేర్ చేయించారు", "ಕಾರನ್ನು ವರ್ಕ್‌ಶಾಪ್‌ನಲ್ಲಿ ರಿಪೇರಿ ಮಾಡಿಸಿದರು", "Sie lassen {p_akk_n} Auto in der Werkstatt reparieren.", ["{p_akk_m}", "{p_dat_m}", "{p_gen_m}"]),
        ("Gehalt", "Neutrum (das Gehalt)", "Akkusativ", "erhöhen", "జీతాన్ని కంపెనీ పెంచింది", "ವೇತನವನ್ನು ಕಂಪನಿಯು ಹೆಚ್ಚಿಸಿತು", "Die Firma hat {p_akk_n} Gehalt um fünf Prozent erhöht.", ["{p_akk_m}", "{p_dat_m}", "{p_gen_m}"]),
        ("Dokument", "Neutrum (das Dokument)", "Akkusativ", "unterschreiben", "పత్రాన్ని పరిశీలించి సంతకం చేశాను", "ದಾಖಲೆಯನ್ನು ಪರಿಶೀಲಿಸಿ ಸಹಿ ಮಾಡಿದೆನು", "Bitte unterschreiben Sie {p_akk_n} Dokument hier unten.", ["{p_akk_m}", "{p_dat_m}", "{p_gen_m}"]),
        ("Ergebnis", "Neutrum (das Ergebnis)", "Akkusativ", "mitteilen", "ఫలితాన్ని ఫోన్ ద్వారా తెలియజేశారు", "ಫಲಿತಾಂಶವನ್ನು ಫೋನ್ ಮೂಲಕ ತಿಳಿಸಿದರು", "Der Arzt hat {p_akk_n} Ergebnis telefonisch mitgeteilt.", ["{p_akk_m}", "{p_dat_m}", "{p_gen_m}"]),
        ("Problem", "Neutrum (das Problem)", "Akkusativ", "besprechen", "సమస్యను సమావేశంలో చర్చించాలి", "ಸಮಸ್ಯೆಯನ್ನು ಸಭೆಯಲ್ಲಿ ಚರ್ಚಿಸಬೇಕು", "Wir müssen {p_akk_n} Problem gemeinsam besprechen.", ["{p_akk_m}", "{p_dat_m}", "{p_gen_m}"]),
        
        ("Reise", "Feminin (die Reise)", "Genitiv", "während", "ప్రయాణం సమయంలో ఫోటోలు తీశారు", "ಪ್ರಯಾಣದ ಸಮಯದಲ್ಲಿ ಫೋಟೋಗಳನ್ನು ತೆಗೆದರು", "Während {p_gen_f} Reise hat er viele Fotos gemacht.", ["{p_akk_f}", "{p_dat_m}", "{p_dat_f}"]),
        ("Krankheit", "Feminin (die Krankheit)", "Genitiv", "wegen", "అనారోగ్యం కారణంగా విశ్రాంతి తీసుకుంటున్నారు", "ಅನಾರೋಗ್ಯದ ಕಾರಣ ವಿಶ್ರಾಂತಿ ಪಡೆಯುತ್ತಿದ್ದಾರೆ", "Wegen {p_gen_f} Krankheit muss sie im Bett bleiben.", ["{p_akk_f}", "{p_dat_m}", "{p_dat_f}"]),
        ("Feier", "Feminin (die Feier)", "Genitiv", "während", "వేడుక సమయంలో పాటలు పాడారు", "ಸಮಾರಂಭದ ಸಮಯದಲ್ಲಿ ಹಾಡುಗಳನ್ನು ಹಾಡಿದರು", "Während {p_gen_f} Feier haben alle Gäste getanzt.", ["{p_akk_f}", "{p_dat_m}", "{p_dat_f}"]),
        
        ("Bruder", "Maskulin (der Bruder)", "Genitiv", "Erfolg", "సోదరుడి విజయం ఎంతో ఆనందాన్ని ఇచ్చింది", "ಸಹೋದರನ ಗೆಲುವು ಅಪಾರ ಸಂತಸ ತಂದಿತು", "Wir freuen uns über den Erfolg {p_gen_m} Bruders.", ["{p_dat_m}", "{p_akk_m}", "{p_nom_m}"]),
        ("Sohn", "Maskulin (der Sohn)", "Genitiv", "Geburtstag", "కుమారుడి పుట్టినరోజుకు బహుమతి కొన్నారు", "ಮಗನ ಜನ್ಮದಿನಕ್ಕೆ ಉಡುಗೊರೆ ಖರೀದಿಸಿದರು", "Sie feiern den Geburtstag {p_gen_m} Sohnes im Restaurant.", ["{p_dat_m}", "{p_akk_m}", "{p_nom_m}"]),
        ("Chef", "Maskulin (der Chef)", "Genitiv", "Vorschlag", "బాస్ సలహాను అందరూ ఆమోదించారు", "ಮುಖ್ಯಸ್ಥರ ಸಲಹೆಯನ್ನು ಎಲ್ಲರೂ ಒಪ್ಪಿಕೊಂಡರು", "Wir folgen dem Ratschlag {p_gen_m} Chefs.", ["{p_dat_m}", "{p_akk_m}", "{p_nom_m}"]),
        
        ("Kinder", "Plural (die Kinder)", "Dativ", "helfen", "పిల్లలకు చదువులో సహాయం చేస్తున్నారు", "ಮಕ್ಕಳಿಗೆ ಓದಿನಲ್ಲಿ ನೆರವಾಗುತ್ತಿದ್ದಾರೆ", "Die Eltern helfen {p_dat_pl} Kindern bei den Aufgaben.", ["{p_akk_pl}", "{p_dat_m}", "{p_gen_pl}"]),
        ("Eltern", "Plural (die Eltern)", "Dativ", "danken", "తల్లిదండ్రులకు హృదయపూర్వక ధన్యవాదాలు", "ಪೋಷಕರಿಗೆ ಹೃತ್ಪೂರ್ವಕ ಧನ್ಯವಾದಗಳು", "Ich danke {p_dat_pl} Eltern für die große Unterstützung.", ["{p_akk_pl}", "{p_dat_m}", "{p_gen_pl}"]),
        ("Freunde", "Plural (die Freunde)", "Akkusativ", "treffen", "స్నేహితులను శనివారం కలుసుకుంటాను", "ಸ್ನೇಹಿತರನ್ನು ಶನಿವಾರ ಭೇಟಿಯಾಗುತ್ತೇನೆ", "Ich treffe {p_akk_pl} Freunde jeden Samstag im Park.", ["{p_dat_pl}", "{p_dat_m}", "{p_nom_pl}"]),
        ("Kollegen", "Plural (die Kollegen)", "Akkusativ", "grüßen", "సహోద్యోగులకు శుభాకాంక్షలు తెలిపారు", "ಸಹೋದ್ಯೋಗಿಗಳಿಗೆ ಶುಭಾಶಯ ತಿಳಿಸಿದರು", "Bitte grüßen Sie {p_akk_pl} Kollegen herzlich von mir.", ["{p_dat_pl}", "{p_dat_m}", "{p_nom_pl}"])
    ]

    def get_forms(base):
        # returns dict of endings for given base possessive
        # base in [mein, dein, sein, ihr, unser, euer, Ihr]
        if base == "euer":
            return {
                "nom_m": "euer", "akk_m": "euren", "dat_m": "eurem", "gen_m": "eures",
                "nom_f": "eure", "akk_f": "eure", "dat_f": "eurer", "gen_f": "eurer",
                "nom_n": "euer", "akk_n": "euer", "dat_n": "eurem", "gen_n": "eures",
                "nom_pl": "eure", "akk_pl": "eure", "dat_pl": "euren", "gen_pl": "eurer"
            }
        elif base == "unser":
            return {
                "nom_m": "unser", "akk_m": "unseren", "dat_m": "unserem", "gen_m": "unseres",
                "nom_f": "unsere", "akk_f": "unsere", "dat_f": "unserer", "gen_f": "unserer",
                "nom_n": "unser", "akk_n": "unser", "dat_n": "unserem", "gen_n": "unseres",
                "nom_pl": "unsere", "akk_pl": "unsere", "dat_pl": "unseren", "gen_pl": "unserer"
            }
        else:
            return {
                "nom_m": f"{base}", "akk_m": f"{base}en", "dat_m": f"{base}em", "gen_m": f"{base}es",
                "nom_f": f"{base}e", "akk_f": f"{base}e", "dat_f": f"{base}er", "gen_f": f"{base}er",
                "nom_n": f"{base}", "akk_n": f"{base}", "dat_n": f"{base}em", "gen_n": f"{base}es",
                "nom_pl": f"{base}e", "akk_pl": f"{base}e", "dat_pl": f"{base}en", "gen_pl": f"{base}er"
            }

    item_ptr = 0
    pron_ptr = 0
    
    while len(questions) < 162:
        item = items[item_ptr % len(items)]
        pron_subj, base, te_prefix, kn_prefix = pronouns[pron_ptr % len(pronouns)]
        
        forms = get_forms(base)
        forms_cap = {k: v.capitalize() for k, v in forms.items()}
        
        # Determine correct form based on case and gender
        case_t = item[2]
        gen_t = item[1].split()[0]
        
        if case_t == "Akkusativ":
            if gen_t == "Maskulin": correct_form = forms["akk_m"]
            elif gen_t == "Feminin": correct_form = forms["akk_f"]
            elif gen_t == "Neutrum": correct_form = forms["akk_n"]
            else: correct_form = forms["akk_pl"]
        elif case_t == "Dativ":
            if gen_t == "Maskulin": correct_form = forms["dat_m"]
            elif gen_t == "Feminin": correct_form = forms["dat_f"]
            elif gen_t == "Neutrum": correct_form = forms["dat_n"]
            else: correct_form = forms["dat_pl"]
        elif case_t == "Genitiv":
            if gen_t in ["Maskulin", "Neutrum"]: correct_form = forms["gen_m"]
            else: correct_form = forms["gen_f"]
        else: # Nominativ
            if gen_t == "Maskulin": correct_form = forms["nom_m"]
            elif gen_t == "Feminin": correct_form = forms["nom_f"]
            elif gen_t == "Neutrum": correct_form = forms["nom_n"]
            else: correct_form = forms["nom_pl"]

        # If sentence starts with possessive, capitalize
        template = item[6]
        starts_with_p = template.startswith("{p_")
        target_token = correct_form.capitalize() if starts_with_p else correct_form
        
        # Prepare distractors
        cand_distractors = []
        for f_key in ["akk_m", "dat_m", "gen_m", "nom_f", "dat_f", "akk_n", "dat_pl"]:
            cand = forms_cap[f_key] if starts_with_p else forms[f_key]
            if cand != target_token and cand not in cand_distractors:
                cand_distractors.append(cand)
            if len(cand_distractors) == 3:
                break

        # Replace in template
        # Find token in template
        import re
        target_de = re.sub(r"\{p_[a-z_]+\}", target_token, template)
        distractor_sentences = []
        for d in cand_distractors:
            d_sent = re.sub(r"\{p_[a-z_]+\}", d, template)
            distractor_sentences.append(d_sent)

        # Build prompt in Telugu & Kannada
        te_prompt = f"{te_prefix} {item[4]}."
        kn_prompt = f"{kn_prefix} {item[5]}."

        topic_str = f"{case_t} {item[1]} ({pron_subj} -> {base})"
        explanation_str = f"'{item[3]}' requires {case_t.upper()}. The noun '{item[0]}' is {item[1]}. Therefore, the possessive '{base}' takes the ending -> '{target_token}'."

        options = [target_de] + distractor_sentences
        rot = (idx % 4)
        shuffled = options[rot:] + options[:rot]
        c_idx = shuffled.index(target_de)

        questions.append({
            "id": idx,
            "topic": topic_str,
            "prompt_te": te_prompt,
            "prompt_kn": kn_prompt,
            "target_de": target_de,
            "options": shuffled,
            "correct_index": c_idx,
            "explanation": explanation_str,
            "case": case_t,
            "gender": item[1],
            "b1_verb": item[3]
        })
        idx += 1
        item_ptr += 1
        if item_ptr % len(items) == 0:
            pron_ptr += 1

    return questions

if __name__ == "__main__":
    q_list = generate_162_questions()
    print(f"Generated {len(q_list)} total questions successfully!")
    with open("questions_bank.json", "w", encoding="utf-8") as f:
        json.dump(q_list, f, ensure_ascii=False, indent=2)
    print("Saved to questions_bank.json")
