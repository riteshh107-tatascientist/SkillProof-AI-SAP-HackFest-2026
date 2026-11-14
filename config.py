"""Central configuration. Secrets come from Streamlit secrets or environment variables - never hardcoded."""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
DATA_DIR, ASSETS_DIR = BASE_DIR / "data", BASE_DIR / "assets"
DB_PATH = Path(os.getenv("SKILLPROOF_DB", BASE_DIR / "database" / "skillproof.db"))
APP_NAME = "SkillProof AI"
TAGLINE = "Fair Skills. Inclusive Talent. Smarter Workforces."
EVENT = "SAP HACKFEST 2026"
THEME = "Theme 02 - Inclusive Workforce"
DISCLAIMER = "Independent student project. Not developed, certified, sponsored or endorsed by SAP."
MAX_UPLOAD_MB = 5
SESSION_TIMEOUT_MIN = 60
DEFAULT_MODELS = {"Gemini": "gemini-2.5-flash", "OpenAI": "gpt-4o-mini"}


def get_secret(name: str, default: str = "") -> str:
    """Streamlit secrets first, then environment variables."""
    try:
        import streamlit as st
        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        pass
    return os.getenv(name, default)
