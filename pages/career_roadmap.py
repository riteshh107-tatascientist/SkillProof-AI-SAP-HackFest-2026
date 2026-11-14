import streamlit as st
from components.cards import callout
from components.header import page_header
from database import db
from pages.auth import require_login
from services.matching_engine import match
from services.recommendation_engine import build_roadmap, roadmap_rows
from utils.helpers import active_candidate, current_user, df_csv, goto, split_pipe


def render():
    page_header("Career Roadmap", "Personalised 30 / 60 / 90-day plan built from your skill gaps.", "🗺️")
    if not require_login(): return
    cand = active_candidate("cr_pick")
    if not cand: return
    have = {s["skill"] for s in db.get_skills(cand["id"])}
    if not have: callout("Confirm your skills in Candidate Studio to generate a roadmap.", "warn"); st.button("Open Candidate Studio", on_click=goto, args=("Candidate Studio",)); return
    jobs = db.get_jobs(); titles = [j["title"] for j in jobs]
    idx = titles.index(st.session_state["target_job_title"]) if st.session_state.get("target_job_title") in titles else 0
    role = st.selectbox("Target role", titles, index=idx); job = jobs[titles.index(role)]
    res = match(have, job, cand.get("resume_text") or ""); plan = build_roadmap(res, job, have)
    own = current_user()["role"] == "candidate"; done = db.get_progress(cand["id"]) if own else set()
    total = sum(len(p["tasks"]) for p in plan.values()); finished = 0
    st.markdown(f"**Current coverage for {role}: {res['score']}%** · {len(res['missing_required'])} required and {len(res['missing_preferred'])} preferred skills to build.")
    bar = st.progress(0.0)
    if total == 0: callout("You already cover every listed skill for this role. Focus on projects, interviews and applications.", "ok")
    tabs = st.tabs(["📅 30 days", "📅 60 days", "📅 90 days"])
    for tab, d in zip(tabs, (30, 60, 90)):
        with tab:
            p = plan[d]
            for t in p["tasks"]:
                key = f"{role}|{d}|{t['skill']}"; r = t["resource"]
                link = f" - [{r['title']}]({r['url']})" if r["url"] else f" - {r['title']}"
                new = st.checkbox(f"**{t['skill']}** ({t['priority']}){link} · ~{r['hours']}h · {r['type']}", value=key in done, key=f"rm_{key}", disabled=not own)
                if own and new != (key in done): db.set_progress(cand["id"], key, new)
                finished += int(new)
            st.markdown(f"🛠️ **Project:** {p['project']}"); st.markdown(f"💡 **Habit:** {p['habit']}")
    bar.progress(finished / total if total else 1.0, text=f"Progress: {finished}/{total} skill tasks") if total else None
    st.caption("Resource links point to official or well-known free sources; verify availability. Progress is saved to your account.")
    st.download_button("⬇️ Download roadmap (CSV)", df_csv(roadmap_rows(plan, role)), f"roadmap_{role.replace(' ', '_')}.csv", "text/csv")
    st.button("🎤 Practise interview questions", on_click=goto, args=("Interview Prep",))
