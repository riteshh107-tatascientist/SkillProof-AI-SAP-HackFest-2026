import re
from pathlib import Path
from config import MAX_UPLOAD_MB

EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")


def validate_email(email: str):
    email = (email or "").strip().lower()
    return (True, "") if EMAIL_RE.match(email) and len(email) <= 120 else (False, "Enter a valid email address.")


def validate_password(pw: str):
    if len(pw or "") < 8: return False, "Password must be at least 8 characters."
    if len(pw) > 64: return False, "Password must be at most 64 characters."
    if not re.search(r"[A-Z]", pw) or not re.search(r"[a-z]", pw) or not re.search(r"\d", pw):
        return False, "Use upper-case, lower-case letters and a digit."
    return True, ""


def validate_name(name: str):
    name = (name or "").strip()
    return (True, "") if 2 <= len(name) <= 80 else (False, "Name must be 2-80 characters.")


def validate_upload(filename: str, data: bytes):
    """Extension, size, empty-file and magic-byte checks. Returns (ok, message, ext)."""
    ext = Path(filename or "").suffix.lower().lstrip(".")
    if ext not in {"pdf", "docx", "txt"}: return False, "Only PDF, DOCX or TXT files are supported.", ext
    if not data: return False, "The file is empty.", ext
    if len(data) > MAX_UPLOAD_MB * 1024 * 1024: return False, f"File exceeds {MAX_UPLOAD_MB} MB.", ext
    if ext == "pdf" and not data.startswith(b"%PDF"): return False, "File content is not a valid PDF.", ext
    if ext == "docx" and not data.startswith(b"PK"): return False, "File content is not a valid DOCX.", ext
    return True, "", ext


def validate_resume_text(text: str):
    t = (text or "").strip()
    if len(t.split()) < 30: return False, "Resume text is too short (need at least ~30 words) to analyse reliably."
    return True, ""
