import pandas as pd
import streamlit as st
from components import charts
from components.cards import callout
from components.header import page_header
from components.tables import show_df
from services import fairness_engine as fe
from utils.helpers import load_csv


def _audit(df, group_opts, outcome_opts, skill_col, key):
    c1, c2 = st.columns(2); group = c1.selectbox("Group attribute (audit only)", group_opts, key=f"{key}_g"); outcome = c2.selectbox("Outcome (1 = selected)", outcome_opts, key=f"{key}_o")
    tbl, top = fe.selection_rates(df, group, outcome); sig = fe.significance(df, group, outcome)
    st.plotly_chart(charts.bar(tbl, "group", "selection_rate", f"Selection rate by {group}").update_yaxes(tickformat=".0%"), width="stretch")
    show_df(tbl.round(3), f"selection_rates_{group}.csv", f"{key}_dl")
    callout(fe.interpret(tbl, sig), "warn")
    if skill_col and skill_col in df.columns:
        st.markdown("**Does the gap persist among similarly skilled applicants?**"); s = fe.stratified(df, group, outcome, skill_col)
        if len(s): st.plotly_chart(charts.bar(s, "skill_band", "selection_rate", "Selection rate within skill bands", color="group").update_layout(barmode="group").update_yaxes(tickformat=".0%"), width="stretch")


def render():
    page_header("Fairness & Responsible AI Lab", "Audit screening outcomes. A disparity is a signal to investigate, not proof of discrimination.", "⚖️")
    callout("Protected characteristics are NEVER used to rank or reject individuals in SkillProof AI. They appear here only as audit dimensions, and real-world use must be lawful, consented and governed.", "")
    t1, t2, t3, t4 = st.tabs(["🧪 Demo audit (synthetic)", "📤 Audit your CSV", "🔁 Legacy vs skills-based", "📋 Checklist & limits"])
    demo = load_csv("fairness_demo.csv")
    with t1:
        callout("SYNTHETIC dataset (600 applicants) generated for demonstration. Skill scores are drawn from the same distribution for all groups; the 'legacy screen' outcome was deliberately simulated to favour certain institution tiers.", "warn")
        _audit(demo, ["institution_tier", "region", "gender", "age_group"], ["legacy_screen_shortlisted", "skills_screen_shortlisted"], "skill_score", "demo")
    with t2:
        up = st.file_uploader("CSV with a group column and a binary outcome column (0/1 or Yes/No)", type=["csv"])
        if up:
            try:
                df = pd.read_csv(up, nrows=100000)
                if df.shape[1] < 2: raise ValueError
            except Exception: st.error("Could not read this CSV."); df = None
            if df is not None:
                oc = [c for c in df.columns if df[c].dropna().astype(str).str.lower().isin(["0", "1", "yes", "no", "true", "false"]).all()]
                if not oc: st.error("No binary outcome column found (0/1, Yes/No, True/False).")
                else:
                    for c in oc: df[c] = df[c].astype(str).str.lower().map({"1": 1, "yes": 1, "true": 1, "0": 0, "no": 0, "false": 0})
                    _audit(df, [c for c in df.columns if c not in oc], oc, None, "up")
        else: callout("Upload a CSV to audit your own screening data. Data stays in this session and is not stored.", "")
    with t3:
        grp = st.selectbox("Compare processes by", ["institution_tier", "region", "gender", "age_group"], key="cmp_g"); rows = []
        for name, col in [("Legacy screen (pedigree-influenced)", "legacy_screen_shortlisted"), ("Skills-based screen (skill_score >= 70)", "skills_screen_shortlisted")]:
            t, _ = fe.selection_rates(demo, grp, col)
            for r in t.itertuples(): rows.append(dict(process=name, group=r.group, impact_ratio=round(r.impact_ratio, 3)))
        cdf = pd.DataFrame(rows); st.plotly_chart(charts.bar(cdf, "group", "impact_ratio", "Impact ratio by process (1.0 = parity with best-treated group; <0.8 = investigate)", color="process").update_layout(barmode="group"), width="stretch")
        callout("Illustration on synthetic data: when selection is driven by demonstrated skill, group gaps shrink. Real data needs real validation.", "ok")
    with t4:
        st.markdown("**Bias investigation checklist**\n- Is each screening criterion demonstrably job-related?\n- Are proxies (college tier, location, gaps, name) influencing outcomes?\n- Do groups have adequate sample sizes (n>=30)?\n- Is demographic data collected lawfully, with consent and access controls?\n- Is there an appeal / human review path and an audit trail?\n- Are results re-audited after every model or process change?\n\n**Limitations:** four-fifths rule is a screening heuristic, not a legal test; selection-rate parity ignores qualification differences unless stratified; small groups give unstable estimates; intersectional groups are not analysed here; correlation does not identify cause.")
