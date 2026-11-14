import streamlit as st
from utils.constants import NAV, ROLE_PAGES
from utils.helpers import current_user, nav_label, inline_svg
from utils.security import esc


def allowed_labels(role: str):
    return [nav_label(n) for n, _, _ in NAV if n in ROLE_PAGES.get(role, [])]


def render_sidebar() -> str:
    user = current_user()
    labels = allowed_labels(user["role"]); to_mod = {nav_label(n): m for n, _, m in NAV}
    if st.session_state.get("nav") not in labels: st.session_state["nav"] = labels[0]
    with st.sidebar:
        st.markdown(f'<div style="display:flex;align-items:center;gap:10px;margin:4px 0 12px"><div style="width:42px">{inline_svg("logo.svg")}</div><div><div style="font-weight:800;font-size:1.15rem;color:#fff">SkillProof AI</div><div style="font-size:.72rem;color:#8fb4ff">Fair skills. Inclusive talent.</div></div></div>', unsafe_allow_html=True)
        st.radio("Navigate", labels, key="nav", label_visibility="collapsed")
        st.markdown(f'<div class="sp-userbox">Signed in as<br><b>{esc(user["name"])}</b><br><span style="opacity:.8">{esc(user["role"]).title()}</span></div>', unsafe_allow_html=True)
        if st.button("Sign out", key="signout"):
            from database import db
            db.log_action(user["id"], "logout"); st.session_state.clear(); st.rerun()
        st.markdown('<div style="font-size:.68rem;color:#8fb4ff;margin-top:14px;line-height:1.4">Independent student project. Not affiliated with or endorsed by SAP. AI assists; humans decide.</div>', unsafe_allow_html=True)
    return to_mod[st.session_state["nav"]]
