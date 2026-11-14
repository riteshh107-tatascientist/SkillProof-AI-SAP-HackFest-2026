import pandas as pd
import streamlit as st
from components.cards import callout, info_card
from components.header import page_header
from components.tables import show_df
from config import DISCLAIMER
from utils.helpers import inline_svg

SAP = [("SAP SuccessFactors", "Sync open roles and skill ontology; push human-approved shortlists and development plans back to talent profiles.", "Proposed"),
       ("SAP Business Technology Platform", "Host services (matching, fairness audit) on BTP with managed identity, destinations and a managed database.", "Proposed"),
       ("SAP Analytics Cloud", "Publish skill-gap and selection-rate dashboards for HR leadership.", "Proposed"),
       ("SAP Business AI / Joule", "Surface explainable skill insights and the career assistant inside HR workflows.", "Proposed")]


def render():
    page_header("About & SAP Enterprise Architecture", "Problem, solution, architecture, responsible-AI stance and proposed enterprise integration.", "🏢")
    callout(DISCLAIMER + " All SAP integrations below are PROPOSED designs - nothing here calls an SAP API or uses SAP data.", "warn")
    c = st.columns(3)
    with c[0]: info_card("The problem", "Resumes over-weight pedigree, titles and keywords, so capable people with practical skills are overlooked and organisations can't see skill gaps.", "🎯")
    with c[1]: info_card("The solution", "Evidence-linked skill profiles, explainable matching, personalised roadmaps, a fairness lab and a human approval workflow.", "🛡️")
    with c[2]: info_card("The principle", "AI assists, humans decide. No protected attributes in matching, no invented metrics, every score explained.", "⚖️")
    st.markdown("### Architecture"); st.markdown(f'<div class="sp-card">{inline_svg("architecture.svg")}</div>', unsafe_allow_html=True)
    st.markdown("### Proposed SAP integration (not implemented)")
    show_df(pd.DataFrame(SAP, columns=["SAP component", "Proposed use case", "Status"]), None)
    st.markdown("### Methods used")
    st.markdown("- **Skill extraction:** rule-based taxonomy with synonyms and evidence sentences (transparent baseline).\n- **Matching:** weighted skill coverage + taxonomy graph for transferable skills; TF-IDF cosine as a reported baseline.\n- **Fairness:** selection rates, impact ratio, Fisher/chi-square tests, sample-size warnings, skill-stratified view.\n- **AI assistant:** Gemini / OpenAI behind one provider interface, with Demo mode and PII redaction.\n- **Evaluation:** precision/recall/F1 computed only against labelled data and always caveated.")
    st.markdown("### Honest limitations")
    st.markdown("Small hand-built taxonomy; synthetic demo data; no OCR for scanned PDFs; heuristic scores are not validated on real hiring outcomes; SQLite is single-node and for prototyping; fairness metrics need legal and domain review before real use.")
    st.markdown("### Built by"); st.write("Ritesh Kumar Singh · B.Tech CSE (Data Science) · Technocrats Institute of Technology, Bhopal")
