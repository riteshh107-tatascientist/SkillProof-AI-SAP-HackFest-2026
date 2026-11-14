import pandas as pd
import streamlit as st
from collections import Counter
from components import charts
from components.cards import callout
from components.header import page_header
from components.tables import show_df
from components.visualizations import skill_network
from database import db
from models.model_evaluation import evaluate_extractor
from models.skill_model import get_taxonomy
from utils.helpers import split_pipe


def demand_df(jobs=None):
    jobs = jobs or db.get_jobs(); req, pref = Counter(), Counter()
    for j in jobs: req.update(split_pipe(j["required_skills"])); pref.update(split_pipe(j["preferred_skills"]))
    df = pd.DataFrame([dict(skill=s, required_in_roles=req[s], preferred_in_roles=pref[s]) for s in set(req) | set(pref)])
    return df.assign(total=df.required_in_roles + df.preferred_in_roles).sort_values(["required_in_roles", "total"], ascending=False)


def supply_df():
    return db.query_df("SELECT skill, COUNT(*) AS candidates_with_skill FROM candidate_skills GROUP BY skill")


def gap_df(top=12):
    d, s = demand_df(), supply_df()
    m = d.merge(s, on="skill", how="left").fillna({"candidates_with_skill": 0}).head(top)
    return m


def render():
    page_header("Skill Analytics", "Demand, supply and structure of skills across roles and candidates.", "📊")
    jobs = db.get_jobs(); tax = get_taxonomy(); n_syn = db.stats()["synthetic"]
    callout(f"Data sources: roles = {len([j for j in jobs if j['source']=='sample'])} SAMPLE roles (data/jobs.csv) + {len([j for j in jobs if j['source']!='sample'])} recruiter-added; candidates = {n_syn} SYNTHETIC demo candidates + registered users. No real market dataset is bundled.", "warn")
    t1, t2, t3, t4, t5 = st.tabs(["🔥 Demand vs supply", "🧩 Categories", "🎭 Role comparison", "🕸️ Skill network", "🧪 Extractor evaluation"])
    with t1:
        d = demand_df(); st.plotly_chart(charts.bar(d.head(15), "required_in_roles", "skill", "Most-required skills across roles", "h", height=430), width="stretch")
        g = gap_df().melt(id_vars="skill", value_vars=["required_in_roles", "candidates_with_skill"], var_name="measure", value_name="count")
        st.plotly_chart(charts.bar(g, "skill", "count", "Demand (roles) vs supply (candidates) for top skills", color="measure").update_layout(barmode="group"), width="stretch")
        show_df(gap_df(30), "skill_demand_supply.csv", "dl_gap")
    with t2:
        c = pd.Series({s: tax.category[s] for s in d.skill}).value_counts().reset_index(); c.columns = ["category", "skills_in_demand"]
        st.plotly_chart(charts.donut(c, "category", "skills_in_demand", "Skill categories demanded by sample roles"), width="stretch")
    with t3:
        sel = st.multiselect("Roles", [j["title"] for j in jobs], default=[j["title"] for j in jobs][:2], max_selections=3)
        cats = sorted(set(tax.category.values())); series = {}
        for j in jobs:
            if j["title"] in sel:
                sk = split_pipe(j["required_skills"]); series[j["title"]] = [round(100 * sum(tax.category[s] == c for s in sk) / max(len(sk), 1), 1) for c in cats]
        if series: st.plotly_chart(charts.radar(cats, series, "Share of required skills by category (%)"), width="stretch")
        mat = pd.DataFrame({j["title"]: {s: 1 if s in split_pipe(j["required_skills"]) else (0.5 if s in split_pipe(j["preferred_skills"]) else 0) for s in d.skill.head(25)} for j in jobs})
        st.plotly_chart(charts.heatmap(mat, "Role x skill (1 = required, 0.5 = preferred)"), width="stretch")
    with t4:
        st.caption("Edges = related skills from the taxonomy (used for transferable-skill suggestions)."); st.plotly_chart(skill_network(), width="stretch")
    with t5:
        ev = evaluate_extractor(); a, b, c = st.columns(3); a.metric("Precision", ev["precision"]); b.metric("Recall", ev["recall"]); c.metric("F1", ev["f1"])
        callout(ev["caveat"], "warn"); st.caption(f"Computed live on {ev['n_resumes']} synthetic labelled resumes (TP={ev['tp']}, FP={ev['fp']}, FN={ev['fn']}).")
        show_df(ev["per_skill"], "extractor_per_skill.csv", "dl_ev")
