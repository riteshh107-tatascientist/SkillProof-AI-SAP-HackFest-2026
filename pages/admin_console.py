import secrets
import pandas as pd
import streamlit as st
from components.cards import callout, metric_card
from components.header import page_header
from components.tables import show_df
from config import get_secret
from database import db
from database.seed import DEMO_PW_DEFAULT
from pages.auth import require_login
from services import ai_provider
from utils.helpers import current_user


def render():
    page_header("Admin Console", "User approval, roles, password resets, platform health and the full audit trail.", "🛡️")
    if not require_login("admin"): return
    me = current_user(); users = db.list_users()
    if not get_secret("ADMIN_PASSWORD") and not get_secret("DEMO_PASSWORD"):
        callout("Demo credentials are active (default demo password). Before any public deployment set ADMIN_EMAIL, ADMIN_PASSWORD and DEMO_PASSWORD in secrets, and SHOW_DEMO_LOGINS = \"false\".", "warn")
    c = st.columns(4); stt = db.stats()
    with c[0]: metric_card("Users", len(users), "all roles", "#2563eb")
    with c[1]: metric_card("Pending approval", int((users.status == "pending").sum()), "recruiters waiting", "#f59e0b")
    with c[2]: metric_card("Suspended", int((users.status == "suspended").sum()), "blocked accounts", "#dc2626")
    with c[3]: metric_card("Human reviews", stt["reviews"], "decisions on record", "#16a34a")
    t1, t2, t3, t4 = st.tabs(["✅ Approvals", "👥 Users", "🩺 Platform", "🕵️ Audit log"])
    with t1:
        pend = users[users.status == "pending"]
        if pend.empty: callout("No accounts waiting for approval.", "ok")
        for r in pend.itertuples():
            a, b, d = st.columns([4, 1, 1]); a.write(f"**{r.name}** · {r.email} · {r.role}")
            if b.button("Approve", key=f"ap{r.id}"): db.set_status(r.id, "active", me["id"]); st.rerun()
            if d.button("Reject", key=f"rj{r.id}"): db.delete_user(r.id, me["id"]); st.rerun()
    with t2:
        show_df(users, "users.csv", "dl_users")
        label = {f"#{r.id} · {r.name} ({r.role}, {r.status})": r.id for r in users.itertuples()}
        uid = label[st.selectbox("Manage user", list(label))]; target = users[users.id == uid].iloc[0]; self_ = uid == me["id"]
        c1, c2, c3 = st.columns(3)
        new_role = c1.selectbox("Role", list(db.ROLES), index=list(db.ROLES).index(target.role))
        if c1.button("Apply role", disabled=new_role == target.role):
            if target.role == "admin" and db.count_admins() <= 1: st.error("Cannot demote the last active administrator.")
            else: db.set_role(uid, new_role, me["id"]); st.rerun()
        if target.status == "suspended":
            if c2.button("Reactivate"): db.set_status(uid, "active", me["id"]); st.rerun()
        elif c2.button("Suspend", disabled=self_):
            if target.role == "admin" and db.count_admins() <= 1: st.error("Cannot suspend the last active administrator.")
            else: db.set_status(uid, "suspended", me["id"]); st.rerun()
        if c3.button("Reset password"):
            temp = "Aa1-" + secrets.token_urlsafe(9); db.set_password(uid, temp, True, me["id"])
            st.session_state["temp_pw"] = (uid, temp)
        if st.session_state.get("temp_pw", (None,))[0] == uid: st.success(f"Temporary password (shown once; the user must change it at next sign-in): `{st.session_state['temp_pw'][1]}`")
        with st.popover("Delete user", disabled=self_):
            st.warning("Deletes the account and all its data permanently.")
            if st.button("Confirm delete", key="cdel"):
                if target.role == "admin" and db.count_admins() <= 1: st.error("Cannot delete the last administrator.")
                else: db.delete_user(uid, me["id"]); st.rerun()
    with t3:
        av = ai_provider.available(); st.write(f"Gemini key: **{'configured' if av['Gemini'] else 'missing'}** · OpenAI key: **{'configured' if av['OpenAI'] else 'missing'}** (values are never displayed)")
        st.write(f"Candidates: {stt['candidates']} ({stt['synthetic']} synthetic) · Roles: {stt['jobs']} · Skill evidence records: {stt['evidence']}")
        st.caption("Session timeout 60 min · login lockout after 5 failures · bcrypt password hashes · parameterised SQL · every admin action is audit-logged.")
    with t4:
        n = st.slider("Entries", 20, 500, 100, 20); show_df(pd.DataFrame(db.recent_audit(n)), "audit_log_full.csv", "dl_audit_full")
