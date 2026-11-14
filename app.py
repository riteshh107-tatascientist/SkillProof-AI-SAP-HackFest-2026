"""SkillProof AI - entry point. Run: streamlit run app.py
Access control: nothing is reachable without an account. Recruiters need admin approval; admins manage users."""
import importlib, time
import streamlit as st

st.set_page_config(page_title="SkillProof AI · SAP HackFest 2026", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

from config import SESSION_TIMEOUT_MIN
from utils.styles import inject_css
from utils.constants import NAV, ROLE_PAGES
from components.sidebar import render_sidebar
from components.header import event_bar
from components.cards import callout
from database import db
from database.seed import seed_all


@st.cache_resource(show_spinner="Preparing SkillProof AI...")
def _boot():
    db.init_db(); seed_all(); return True


def _enforce_session():
    """Timeout + re-validate the account on every run (suspension / role change by an admin applies immediately)."""
    ss, now = st.session_state, time.time()
    user = ss.get("user")
    if user:
        if now - ss.get("last_active", now) > SESSION_TIMEOUT_MIN * 60:
            ss.clear(); ss["timeout_notice"] = True; return
        fresh = db.get_user(user["id"])
        if not fresh or fresh["status"] != "active": ss.clear(); ss["revoked_notice"] = True; return
        ss["user"] = fresh
    ss["last_active"] = now


def router():
    inject_css(); _boot(); _enforce_session()
    from pages import auth
    if not st.session_state.get("user"):
        if st.session_state.pop("timeout_notice", False): st.warning("You were signed out after a period of inactivity.")
        if st.session_state.pop("revoked_notice", False): st.error("Your session ended because the account is no longer active.")
        auth.render_gate(); return
    if st.session_state["user"]["must_change"]: auth.render_force_change(); return
    module = render_sidebar(); event_bar()
    role = st.session_state["user"]["role"]; allowed = {m for n, _, m in NAV if n in ROLE_PAGES[role]}
    if module not in allowed: callout("You do not have access to this section.", "bad"); return
    try:
        importlib.import_module(f"pages.{module}").render()
    except Exception as exc:  # last-resort guard: friendly message, details to audit log
        st.error("Something went wrong on this page. Please retry or open another section.")
        try: db.log_action(st.session_state["user"]["id"], "page_error", f"{module}: {type(exc).__name__}")
        except Exception: pass


st.navigation([st.Page(router, title="SkillProof AI", default=True)], position="hidden").run()
