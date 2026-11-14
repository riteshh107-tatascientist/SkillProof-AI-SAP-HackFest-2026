import streamlit as st
from components import charts
from components.cards import callout, chips
from components.header import page_header
from components.tables import show_df
from components.visualizations import skill_network
from database import db
from pages.auth import require_login
from services.matching_engine import match, rank_jobs, report_df
from utils.helpers import active_candidate, df_csv, goto, split_pipe


def render():
    page_header("Fair Job Matching", "Skill coverage against a role - computed from confirmed skills only.", "🎯")
    if not require_login(): return
    cand = active_candidate("jm_pick")
    if not cand: return
    have = {s["skill"] for s in db.get_skills(cand["id"])}
    if not have:
        callout("No confirmed skills yet. Confirm skills in Candidate Studio first.", "warn"); st.button("Open Candidate Studio", on_click=goto, args=("Candidate Studio",)); return
    jobs = db.get_jobs(); resume = cand.get("resume_text") or ""
    callout("The percentage is a skill-OVERLAP measure. It is not a probability of being hired and it never uses name, gender, age, college or other protected attributes.", "")
    t1, t2, t3, t4 = st.tabs(["🎯 Role match", "🏁 All roles", "⚔️ Compare roles", "📘 Methodology"])
    with t1:
        role = st.selectbox("Role", [j["title"] for j in jobs], key="jm_role"); job = next(j for j in jobs if j["title"] == role)
        st.session_state["target_job_title"] = role; res = match(have, job, resume)
        a, b = st.columns([1, 2])
        with a: st.plotly_chart(charts.gauge(res["score"]), width="stretch")
        with b:
            st.markdown("**✅ Matched required**"); chips(res["matched_required"], "ok"); st.markdown("**❌ Missing required**"); chips(res["missing_required"], "miss")
            st.markdown("**✅ Matched preferred**"); chips(res["matched_preferred"], "ok"); st.markdown("**➕ Missing preferred**"); chips(res["missing_preferred"], "")
        st.markdown("**🔁 Transferable skill suggestions**")
        if res["transferable"]:
            for t in res["transferable"]: st.markdown(f"- **{t['missing']}** ← {t['reason']} _({t['strength']})_")
        else: st.caption("No related skills found for the gaps.")
        with st.expander("Why this score? (explainability)"):
            for e in res["explain"]: st.markdown(f"- {e}")
            st.markdown(f"- Text similarity via {res['text_method']} (resume vs role description): **{res['text_similarity']}** - shown for transparency only, not part of the score.")
        with st.expander("Skill network (green outline = yours, red = missing)"): st.plotly_chart(skill_network(have, res["missing_required"]), width="stretch")
        st.download_button("⬇️ Download matching report (CSV)", df_csv(report_df(res)), f"match_report_{role.replace(' ', '_')}.csv", "text/csv")
        st.button("🗺️ Build my roadmap for this role", on_click=goto, args=("Career Roadmap",), type="primary")
    with t2:
        df = rank_jobs(have, jobs, resume); st.plotly_chart(charts.bar(df, "coverage_score", "role", "Skill coverage by role (%)", "h", height=440), width="stretch"); show_df(df, "role_ranking.csv", "dl_rank")
    with t3:
        picks = st.multiselect("Roles to compare", [j["title"] for j in jobs], default=[j["title"] for j in jobs][:3], max_selections=4)
        rows = []
        for j in jobs:
            if j["title"] in picks:
                r = match(have, j, resume); rows += [dict(role=j["title"], measure="Required coverage %", value=round(100 * r["req_cov"], 1)), dict(role=j["title"], measure="Preferred coverage %", value=round(100 * r["pref_cov"], 1))]
        if rows:
            import pandas as pd
            st.plotly_chart(charts.bar(pd.DataFrame(rows), "role", "value", "Role comparison", color="measure").update_layout(barmode="group"), width="stretch")
    with t4:
        st.markdown("**Method:** score = 70% x required-skill coverage + 30% x preferred-skill coverage. Transferable suggestions use the taxonomy graph (adjacent or same-category skills). Text similarity uses TF-IDF + cosine and is reported separately.\n\n**Limitations:** the taxonomy is hand-built and small; coverage cannot measure depth of skill; synonyms outside the taxonomy are missed; the weights are a transparent default, not learned from outcomes. Use as decision support with human review.")
