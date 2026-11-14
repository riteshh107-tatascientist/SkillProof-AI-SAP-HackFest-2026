import html, re
import bcrypt

_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE = re.compile(r"(?<!\d)(?:\+?\d{1,3}[\s-]?)?(?:\d[\s-]?){9,12}(?!\d)")
_URL = re.compile(r"(?:https?://|www\.|linkedin\.com/|github\.com/)\S+", re.I)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def sanitize(text, max_len: int = 2000) -> str:
    return _CTRL.sub("", str(text or "")).strip()[:max_len]


def esc(text) -> str:
    return html.escape(str(text if text is not None else ""))


def redact_pii(text: str) -> str:
    """Data minimisation before any text leaves the app for an external AI provider."""
    text = _EMAIL.sub("[EMAIL]", text or "")
    text = _URL.sub("[LINK]", text)
    return _PHONE.sub("[PHONE]", text)
