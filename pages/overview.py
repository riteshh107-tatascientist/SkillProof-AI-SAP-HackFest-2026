import streamlit as st
from components import charts
from components.cards import callout, info_card, metric_card
from components.header import hero
from components.tables import show_df
from components.visualizations import workflow_gif
from database import db
from pages.skill_analytics import gap_df
import pandas as pd
from utils.helpers import goto


def render():
    hero()
    s = db.stats(); cols = st.columns(5)
    data = [("Candidate profiles", s["candidates"], f"{s['synthetic']} synthetic demo", "#2563eb"), ("Open roles", s["jobs"], "sample + recruiter-added", "#06b6d4"), ("Taxonomy skills", s["skills"], "rule-based taxonomy", "#7c3aed"),
            ("Skill evidence records", s["evidence"], "confirmed, evidence-linked", "#16a34a"), ("Human reviews", s["reviews"], "recorded decisions", "#f59e0b")]
    for c, (l, v, h, a) in zip(cols, data):
        with c: metric_card(l, v, h, a)
    st.caption("Live counts from the local SQLite database. Demo candidates are synthetic; nothing here is real business data.")
    st.markdown("### Start the demo")
    b = st.columns(5)
    from utils.constants import ROLE_PAGES
    allowed = ROLE_PAGES[st.session_state["user"]["role"]]
    opts = [(l, p) for l, p in [("👤 Candidate Studio", "Candidate Studio"), ("📄 Resume Analyzer", "Resume Analyzer"), ("🧑‍💼 Recruiter Hub", "Recruiter Hub"), ("🛡️ Admin Console", "Admin Console"), ("⚖️ Fairness Lab", "Fairness Lab"), ("🤖 AI Assistant", "AI Assistant")] if p in allowed][:5]
    for col, (label, page) in zip(b, opts):
        col.button(label, on_click=goto, args=(page,), width="stretch", key=f"home_{page}")
    st.markdown("### How SkillProof AI works"); workflow_gif()
    steps = [("1 Upload", "Resume PDF/DOCX parsed locally."), ("2 Extract", "Skills + evidence suggested."), ("3 Confirm", "Candidate verifies each skill."), ("4 Match", "Explainable coverage vs role."), ("5 Grow", "30/60/90-day roadmap."), ("6 Review", "Human approves, audit logged.")]
    sc = st.columns(6)
    for c, (t, d) in zip(sc, steps):
        with c: info_card(t, d)
    left, right = st.columns(2)
    with left:
        g = gap_df(8).melt(id_vars="skill", value_vars=["required_in_roles", "candidates_with_skill"], var_name="measure", value_name="count")
        st.plotly_chart(charts.bar(g, "skill", "count", "Top skills: role demand vs candidate supply", color="measure").update_layout(barmode="group"), width="stretch")
    with right:
        cat = db.query_df("SELECT category, COUNT(*) AS records FROM candidate_skills GROUP BY category")
        if len(cat): st.plotly_chart(charts.donut(cat, "category", "records", "Skill evidence by category"), width="stretch")
    st.markdown("### Why it is different")
    f = st.columns(3)
    feats = [("Evidence, not keywords", "Every skill links to a sentence, project or certificate the candidate confirms.", "🔍"), ("Fair by design", "Matching never sees name, gender, age or college. Fairness Lab audits outcomes.", "⚖️"), ("Humans decide", "AI suggests next steps; recruiters record rationale in an audit trail.", "👩‍⚖️"),
             ("Explainable scores", "See exactly why a skill-coverage percentage is what it is.", "🧠"), ("Privacy-first AI", "PII redaction, consent toggles, Gemini/OpenAI/Demo provider choice.", "🔐"), ("Growth built in", "Gaps become a personalised roadmap and interview practice.", "🗺️")]
    for i, (t, d, ic) in enumerate(feats):
        with f[i % 3]: info_card(t, d, ic); st.write("")
    st.markdown("### Recent platform activity"); show_df(pd.DataFrame(db.recent_audit(8)), None)
