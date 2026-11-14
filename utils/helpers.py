import functools
from datetime import datetime, timezone
import pandas as pd
import streamlit as st
from config import DATA_DIR, ASSETS_DIR
from utils.constants import NAV


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


@functools.lru_cache(maxsize=16)
def _read(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / name)


def load_csv(name: str) -> pd.DataFrame:
    return _read(name).copy()


def split_pipe(value) -> list:
    if value is None or (isinstance(value, float) and pd.isna(value)): return []
    return [x.strip() for x in str(value).split("|") if x.strip()]


def df_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def compact(html: str) -> str:
    return " ".join(l.strip() for l in html.splitlines() if l.strip())


def inline_svg(name: str) -> str:
    return compact((ASSETS_DIR / name).read_text(encoding="utf-8"))


def nav_label(name: str) -> str:
    for n, icon, _ in NAV:
        if n == name: return f"{icon}  {n}"
    return name


def goto(name: str):
    """Use as a button on_click callback (widget state may only change in callbacks)."""
    st.session_state["nav"] = nav_label(name)


def current_user():
    return st.session_state.get("user")


def active_candidate(key: str = "cand_pick"):
    """Candidate -> own profile. Recruiter -> pick any candidate (shown pseudonymously)."""
    from database import db
    user = current_user()
    if not user: return None
    if user["role"] == "candidate":
        cand = db.get_candidate_by_user(user["id"])
        if not cand:
            st.info("Create your profile in Candidate Studio first.")
            st.button("Open Candidate Studio", on_click=goto, args=("Candidate Studio",), key=f"{key}_go")
        return cand
    cands = db.list_candidates()
    if not cands:
        st.info("No candidates yet."); return None
    labels = {f"CAND-{c['id']:04d} · {c['headline'] or 'Candidate'}": c for c in cands}
    return labels[st.selectbox("Candidate (pseudonymised)", list(labels), key=key)]
