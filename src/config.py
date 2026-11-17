import os
import socket

# Base Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
CSS_DIR = os.path.join(STATIC_DIR, "css")
TEMPLATES_DIR = os.path.join(STATIC_DIR, "templates")
DATA_DIR = os.path.join(BASE_DIR, "data")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

# Data File Paths (with fallback to root if not in data/)
def _get_data_path(filename: str) -> str:
    path_in_data = os.path.join(DATA_DIR, filename)
    path_in_root = os.path.join(BASE_DIR, filename)
    if os.path.exists(path_in_data):
        return path_in_data
    if os.path.exists(path_in_root):
        return path_in_root
    return path_in_data

DATA_FILE = _get_data_path("duel_data.json")
QUESTIONS_FILE = _get_data_path("questions_bank.json")
GENDER_QUESTIONS_FILE = _get_data_path("gender_questions_bank.json")
PHRASES_FILE = _get_data_path("german_phrases.json")
LSRW_CACHE_FILE = _get_data_path("lsrw_cache.json")

# App Constants
APP_TITLE = "German B1 Goethe Prep & Duel | జర్మన్ B1 | ಜರ್ಮನ್ B1"
APP_ICON = "🇩🇪"

AVATAR_CHOICES = ["🦁", "🦊", "🐼", "🐯", "🚀", "⚡", "🌟", "🦉", "🎯", "🔥", "💎", "🐬", "👑"]

GOETHE_SPEAKING_TOPICS = [
    "Thema 1: Eine Geburtstagsparty gemeinsam planen (B1 Teil 1)",
    "Thema 2: Einen Wochenendausflug organisieren (B1 Teil 1)",
    "Thema 3: Haustiere - Vorteile und Nachteile (B1 Teil 2)",
    "Thema 4: Soziale Medien im Alltag von Jugendlichen (B1 Teil 2)",
    "Thema 5: Braucht man heute noch ein eigenes Auto? (B1 Teil 3)"
]


def get_local_ip() -> str:
    """Detects local LAN IP for Wi-Fi sharing."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "192.168.158.14"


def load_css() -> str:
    """Reads external CSS file."""
    css_path = os.path.join(CSS_DIR, "main.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def load_template(template_name: str) -> str:
    """Reads an external HTML template."""
    tmpl_path = os.path.join(TEMPLATES_DIR, template_name)
    if os.path.exists(tmpl_path):
        with open(tmpl_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""
