import pandas as pd
import streamlit as st
from components import charts
from components.cards import callout, chips
from components.header import page_header
from components.tables import show_df
from database import db
from models.skill_model import get_taxonomy
from pages.auth import require_login
from pages.skill_analytics import gap_df
from services.matching_engine import match
from services.skill_extractor import skills_in_text
from utils.constants import DECISIONS
from utils.helpers import current_user, split_pipe
from utils.security import sanitize


def _jobs_tab(user):
    jobs = db.get_jobs(); show_df(pd.DataFrame(jobs)[["id", "title", "department", "required_skills", "preferred_skills", "source"]], "roles.csv", "dl_roles")
    st.markdown("#### ➕ Add a role")
    c1, c2 = st.columns(2); title = c1.text_input("Role title"); dept = c2.text_input("Department")
    desc = st.text_area("Job description (paste)", height=120)
    if st.button("🔎 Suggest skills from description"):
        st.session_state["jd_sk"] = skills_in_text(desc)
    names = get_taxonomy().names; sug = [s for s in st.session_state.get("jd_sk", []) if s in names]
    req = st.multiselect("Required skills", names, default=sug[:6]); pref = st.multiselect("Preferred skills", [n for n in names if n not in req], default=[s for s in sug[6:10] if s not in req])
    if st.button("Add role", type="primary"):
        if len(title.strip()) < 3 or not req: st.error("Title and at least one required skill are needed.")
        else: db.add_job(sanitize(title, 100), sanitize(dept, 80), sanitize(desc, 3000), req, pref, user["id"]); db.log_action(user["id"], "job_added", title); st.success("Role added."); st.rerun()


def _compare_tab():
    jobs = db.get_jobs(); job = next(j for j in jobs if j["title"] == st.selectbox("Role", [j["title"] for j in jobs], key="rc_role"))
    rows = []
    for c in db.list_candidates():
        sk = {s["skill"] for s in db.get_skills(c["id"])}
        if not sk: continue
        r = match(sk, job, ""); rows.append(dict(candidate=f"CAND-{c['id']:04d}", coverage_score=r["score"], required_covered=f"{len(r['matched_required'])}/{len(r['matched_required']) + len(r['missing_required'])}", missing_required=", ".join(r["missing_required"]) or "-", verified_skills=len(sk), data="synthetic" if c["is_synthetic"] else "registered", _id=c["id"]))
    df = pd.DataFrame(rows).sort_values("coverage_score", ascending=False) if rows else pd.DataFrame()
    callout("Blind view: names, colleges and demographics are hidden. This ordering is decision SUPPORT; a human reviews every candidate.", "")
    if len(df):
        show_df(df.drop(columns="_id"), "candidate_comparison.csv", "dl_cc")
        reveal = st.checkbox("Reveal identities (reason is logged)")
        if reveal:
            why = st.text_input("Reason for reveal (required)")
            if len(why.strip()) >= 8:
                db.log_action(current_user()["id"], "identity_reveal", f"{why[:120]} job={job['id']}")
                st.dataframe(pd.DataFrame([dict(candidate=r["candidate"], name=db.get_candidate(r["_id"])["name"]) for r in rows[:50]]), hide_index=True)


def _review_tab(user):
    jobs = db.get_jobs(); cands = [c for c in db.list_candidates() if db.get_skills(c["id"])]
    if not cands: callout("No candidates with confirmed skills yet.", "warn"); return
    cl = {f"CAND-{c['id']:04d} · {c['headline']}": c for c in cands}; c = cl[st.selectbox("Candidate", list(cl))]
    job = next(j for j in jobs if j["title"] == st.selectbox("Role", [j["title"] for j in jobs], key="rv_role"))
    skills = db.get_skills(c["id"]); have = {s["skill"] for s in skills}; r = match(have, job, c.get("resume_text") or "")
    st.metric("Skill coverage", f"{r['score']}%"); st.markdown("**Matched with evidence**")
    ev = pd.DataFrame([dict(skill=s["skill"], evidence=s["evidence"], source=s["source"]) for s in skills if s["skill"] in r["matched_required"] + r["matched_preferred"]]); show_df(ev, None)
    st.markdown("**Gaps**"); chips(r["missing_required"], "miss")
    hint = "Evidence supports a structured interview." if r["score"] >= 70 else ("Partial coverage - probe the gaps and learning potential." if r["score"] >= 40 else "Large gaps - consider other roles or a development path.")
    callout(f"AI suggested next step (non-binding): {hint}", "warn")
    decision = st.selectbox("Your decision (human)", DECISIONS); notes = st.text_area("Rationale / notes (required, min 10 chars)")
    if st.button("Record human decision", type="primary"):
        if len(notes.strip()) < 10: st.error("Please document your rationale.")
        else: db.add_review(c["id"], job["id"], user["id"], decision, sanitize(notes, 800), r["score"]); st.success("Decision recorded in the audit trail.")
    rv = db.list_reviews()
    if len(rv): st.markdown("**Review history**"); show_df(rv, "reviews.csv", "dl_rev")


def _inventory_tab():
    df = db.query_df("SELECT category, skill, COUNT(*) AS people FROM candidate_skills GROUP BY category, skill")
    if df.empty: callout("No skill records yet.", "warn"); return
    st.plotly_chart(charts.bar(df.groupby("category").people.sum().reset_index().sort_values("people"), "people", "category", "Workforce skill inventory by category", "h"), width="stretch")
    g = gap_df(20); g["shortfall"] = g.required_in_roles - g.candidates_with_skill / max(db.stats()["candidates"], 1) * 10
    st.markdown("**Development focus**: skills required by many roles but held by few candidates"); show_df(g.sort_values("candidates_with_skill").head(8)[["skill", "required_in_roles", "candidates_with_skill"]], "development_focus.csv", "dl_dev")


def render():
    page_header("Recruiter Intelligence", "Role management, blind candidate comparison, evidence review and human approval with a full audit trail.", "🧑‍💼")
    if not require_login("recruiter"): return
    user = current_user()
    t = st.tabs(["📋 Roles", "👥 Blind comparison", "🧾 Evidence review & decision", "🏭 Workforce inventory", "🕵️ Audit history"])
    with t[0]: _jobs_tab(user)
    with t[1]: _compare_tab()
    with t[2]: _review_tab(user)
    with t[3]: _inventory_tab()
    with t[4]: show_df(pd.DataFrame(db.recent_audit(100)), "audit_log.csv", "dl_audit")
