import json
import streamlit as st
from config import get_secret, DEFAULT_MODELS
from components.cards import callout, provider_badge
from components.header import page_header, event_bar, hero
from database import db
from services import ai_provider
from utils.constants import PROVIDERS
from utils.helpers import current_user, goto
from utils.security import sanitize
from utils.validators import validate_email, validate_name, validate_password
from database.seed import DEMO_PW_DEFAULT


def require_login(role=None) -> bool:
    """Defence in depth: the router already blocks anonymous users and disallowed roles."""
    user = current_user()
    if not user: callout("Please sign in.", "warn"); return False
    if role and user["role"] != role: callout(f"This section is for {role} accounts.", "bad"); return False
    return True


def _login(email, pw):
    user, err = db.authenticate(email, pw)
    if err: st.error(err); return
    st.session_state["user"] = user; st.rerun()


def ai_settings():
    st.markdown("#### 🤖 AI provider")
    av = ai_provider.available()
    default = "Gemini" if av["Gemini"] else ("OpenAI" if av["OpenAI"] else "Demo")
    st.session_state.setdefault("ai_provider", default)
    st.radio("Provider", PROVIDERS, key="ai_provider", horizontal=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Demo", "Ready"); c2.metric("Gemini key", "Found" if av["Gemini"] else "Missing"); c3.metric("OpenAI key", "Found" if av["OpenAI"] else "Missing")
    st.text_input("Gemini model", value=get_secret("GEMINI_MODEL", DEFAULT_MODELS["Gemini"]), key="ai_model_Gemini")
    st.text_input("OpenAI model", value=get_secret("OPENAI_MODEL", DEFAULT_MODELS["OpenAI"]), key="ai_model_OpenAI")
    st.caption("Keys are read from Streamlit secrets or environment variables and are never displayed. Demo mode is rule-based, not a live LLM.")
    st.markdown("#### 🔐 Privacy controls for AI calls")
    st.checkbox("Share my confirmed skill NAMES and target role with the AI provider (no name, contact details or resume text)", key="share_skills", value=True)
    st.checkbox("I consent to sending a PII-redacted resume excerpt to the selected external provider when I ask for resume critique", key="share_resume", value=False)
    if st.button("Test selected provider"):
        p = st.session_state["ai_provider"]
        res = ai_provider.generate(p, "Reply briefly.", [{"role": "user", "content": "Reply with the single word: ready"}], st.session_state.get(f"ai_model_{p}", ""), 20)
        if res.ok: provider_badge(res.provider, res.model, res.live); st.success(f"Provider responded: {res.text[:80]}")
        else: st.error(res.error)


def _password_form(user, forced=False):
    with st.form("pwform"):
        if not forced: old = st.text_input("Current password", type="password")
        new = st.text_input("New password", type="password"); conf = st.text_input("Confirm new password", type="password")
        if st.form_submit_button("Update password", type="primary"):
            ok, msg = validate_password(new)
            if not ok: st.error(msg)
            elif new != conf: st.error("Passwords do not match.")
            elif not forced and not db.verify_user_password(user["id"], old): st.error("Current password is incorrect.")
            elif db.verify_user_password(user["id"], new): st.error("Choose a password different from the current one.")
            else:
                db.set_password(user["id"], new, False); st.session_state["user"] = dict(user, must_change=False); st.success("Password updated."); st.rerun() if forced else None


def render_force_change():
    event_bar(); page_header("Set a new password", "An administrator reset your password. Choose a new one to continue.", "🔑")
    _password_form(current_user(), forced=True)


def render_gate():
    """Everything an unauthenticated visitor can see: create an account or sign in. Nothing else is reachable."""
    event_bar(); hero()
    callout("Create an account to use SkillProof AI. Candidates get instant access; recruiter accounts are activated after admin approval.", "")
    t1, t2 = st.tabs(["🔐 Sign in", "📝 Create account"])
    with t1:
        with st.form("login"):
            email = st.text_input("Email"); pw = st.text_input("Password", type="password")
            if st.form_submit_button("Sign in", type="primary"): _login(email, pw)
        if get_secret("SHOW_DEMO_LOGINS", "true").lower() == "true":
            with st.expander("Presentation demo accounts"):
                pwd = get_secret("DEMO_PASSWORD", DEMO_PW_DEFAULT); d1, d2, d3 = st.columns(3)
                if d1.button("▶ Demo Candidate", width="stretch"): _login("candidate@skillproof.demo", pwd)
                if d2.button("▶ Demo Recruiter", width="stretch"): _login("recruiter@skillproof.demo", pwd)
                if d3.button("▶ Demo Admin", width="stretch"): _login("admin@skillproof.demo", pwd)
                st.caption("Hide these buttons in production with SHOW_DEMO_LOGINS = \"false\" in secrets.")
    with t2:
        with st.form("register"):
            name = st.text_input("Full name"); email = st.text_input("Email", key="reg_email")
            role = st.selectbox("I am a", ["candidate", "recruiter"], format_func=lambda r: "Candidate / student" if r == "candidate" else "Recruiter (needs admin approval)")
            pw = st.text_input("Password (8+ chars, upper, lower, digit)", type="password", key="reg_pw"); pw2 = st.text_input("Confirm password", type="password", key="reg_pw2")
            if st.form_submit_button("Create account", type="primary"):
                checks = [validate_name(name), validate_email(email), validate_password(pw)]
                bad = next((m for ok, m in checks if not ok), "") or ("" if pw == pw2 else "Passwords do not match.")
                if bad: st.error(bad)
                else:
                    uid, err = db.create_user(sanitize(email, 120), sanitize(name, 80), pw, role)
                    if err: st.error(err)
                    elif role == "recruiter": st.success("Account created. An administrator must approve it before you can sign in.")
                    else: st.success("Account created. Switch to the Sign in tab.")


def render():
    page_header("Account & Settings", "Security, AI provider selection, privacy controls and your data.", "⚙️")
    user = current_user(); t1, t2, t3 = st.tabs(["🤖 AI Settings", "🔑 Security", "🗂️ My data"])
    with t1: ai_settings()
    with t2:
        st.write(f"**{user['name']}** · {user['email']} · role: {user['role']}")
        st.caption("Passwords are stored only as bcrypt hashes. Sessions expire after 60 minutes of inactivity; 5 failed sign-ins lock the account for 5 minutes.")
        _password_form(user)
    with t3:
        data = json.dumps(db.export_user_data(user["id"]), indent=2, default=str)
        st.download_button("⬇️ Download all my data (JSON)", data, "my_skillproof_data.json", "application/json")
        st.markdown("**Delete my account and data** - permanent.")
        if user["role"] == "admin": st.caption("Administrator accounts cannot be self-deleted; transfer the role first.")
        else:
            with st.form("del"):
                pw = st.text_input("Password", type="password"); conf = st.text_input("Type DELETE to confirm")
                if st.form_submit_button("Delete permanently"):
                    if conf != "DELETE" or not db.verify_user_password(user["id"], pw): st.error("Confirmation or password is incorrect.")
                    else: db.delete_user(user["id"], user["id"]); st.session_state.clear(); st.rerun()
