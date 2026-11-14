import streamlit as st
from config import DATA_DIR, MAX_UPLOAD_MB
from services.resume_parser import extract_text
from utils.validators import validate_upload


def resume_input(key: str, default: str = "") -> str:
    """Upload (validated) or paste a resume. Returns the current text."""
    ss, tk = st.session_state, f"{key}_text"
    ss.setdefault(tk, default)
    up = st.file_uploader(f"Upload resume (PDF, DOCX or TXT, max {MAX_UPLOAD_MB} MB)", type=["pdf", "docx", "txt"], key=f"{key}_up")
    if st.button("📎 Use built-in sample resume", key=f"{key}_sample"):
        ss[tk] = (DATA_DIR / "sample_resume.txt").read_text(encoding="utf-8")
    if up is not None and ss.get(f"{key}_last") != (up.name, up.size):
        ok, msg, _ = validate_upload(up.name, up.getvalue())
        if not ok: st.error(msg)
        else:
            text, err = extract_text(up.name, up.getvalue())
            if err: st.error(err)
            else: ss[tk] = text; ss[f"{key}_last"] = (up.name, up.size); st.success(f"Read {len(text.split())} words from {up.name}.")
    return st.text_area("Resume text (you can edit before analysing)", key=tk, height=230)
