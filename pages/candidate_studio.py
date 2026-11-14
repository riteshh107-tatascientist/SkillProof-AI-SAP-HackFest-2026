import pandas as pd
import streamlit as st
from components.cards import callout, chips, metric_card
from components.header import page_header
from components.resume_input import resume_input
from components.tables import show_df
from database import db
from models.skill_model import get_taxonomy
from pages.auth import require_login
from services.resume_parser import profile_hints
from models import semantic_model
from services import ai_provider
from services.llm_extractor import llm_extract, merge_suggestions
from services.skill_extractor import extract_skills
from utils.helpers import active_candidate, current_user, df_csv
from utils.security import sanitize
from utils.validators import validate_resume_text


def _profile_tab(user, cand):
    with st.form("profile"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Full name", value=(cand or {}).get("name") or user["name"])
        headline = c2.text_input("Headline (e.g. Aspiring Data Analyst)", value=(cand or {}).get("headline") or "")
        edu = st.text_input("Education", value=(cand or {}).get("education") or "")
        certs = st.text_input("Certifications (separate with ;)", value=(cand or {}).get("certifications") or "")
        summ = st.text_area("Profile summary (your own words)", value=(cand or {}).get("summary") or "", height=110)
        st.caption("Stored locally in SQLite. Matching never uses your name, college or any protected attribute - only confirmed skills and evidence.")
        if st.form_submit_button("💾 Save profile", type="primary"):
            if len(name.strip()) < 2: st.error("Please enter your name.")
            else:
                cid = db.upsert_candidate(user["id"], sanitize(name, 80), user["email"], sanitize(headline, 100), sanitize(edu, 200), sanitize(certs, 300), sanitize(summ, 1000))
                db.log_action(user["id"], "profile_saved", f"cand={cid}"); st.success("Profile saved."); st.rerun()


def _skills_tab(user, cand):
    if not cand: callout("Save your profile first (tab 1).", "warn"); return
    tax = get_taxonomy()
    text = resume_input(f"resume_{cand['id']}", cand.get("resume_text") or "")
    prov = st.session_state.get("ai_provider", "Demo"); consent = st.session_state.get("share_resume", False)
    can_ai = prov != "Demo" and ai_provider.available().get(prov, False) and consent
    use_ai = st.checkbox(f"🤖 Also use {prov} AI to find skills the rules miss (sends a PII-redacted resume to the provider)", value=can_ai, disabled=not can_ai,
                         help="Needs a Gemini/OpenAI key in secrets, the provider selected and the consent box ticked in Account & Settings.")
    st.caption(f"Engines: taxonomy rules + {semantic_model.engine_name()}" + (f" + {prov} LLM (evidence must be quoted from your resume)" if use_ai else ""))
    if st.button("🔎 Analyse resume & suggest skills", type="primary"):
        ok, msg = validate_resume_text(text)
        if not ok: st.error(msg)
        else:
            res = extract_skills(text, semantic=semantic_model.available())
            if use_ai:
                with st.spinner(f"Asking {prov}..."):
                    ex = llm_extract(text, prov, st.session_state.get(f"ai_model_{prov}", ""))
                if ex["ok"]: res = merge_suggestions(res, ex["skills"]); st.toast(f"AI added/confirmed {len(ex['skills'])} skills; {ex['rejected']} unsupported suggestions were discarded.")
                else: st.warning(f"AI extraction skipped: {ex['error']} (rule-based results shown).")
            st.session_state[f"sugg_{cand['id']}"] = res; st.session_state[f"hints_{cand['id']}"] = profile_hints(text)
    sugg = st.session_state.get(f"sugg_{cand['id']}")
    if sugg is None: callout("Upload or paste your resume, then click Analyse. Suggestions are NOT facts - you decide what is true.", ""); return
    existing = {s["skill"]: s for s in db.get_skills(cand["id"])}
    rows = [dict(Confirm=(s["confidence"] >= 0.7) or s["skill"] in existing, Skill=s["skill"], Category=s["category"], Found_by=s.get("method", ""), Strength=s["confidence"], Mentions=s["mentions"], Evidence=existing.get(s["skill"], s)["evidence"]) for s in sugg]
    for sk, s in existing.items():
        if sk not in {r["Skill"] for r in rows}: rows.append(dict(Confirm=True, Skill=sk, Category=s["category"], Found_by="saved profile", Strength=s["confidence"] or 0.0, Mentions=0, Evidence=s["evidence"]))
    st.markdown(f"**{len(rows)} suggested skills.** Pre-ticked where the resume shows the skill in an action sentence. Untick anything you cannot demonstrate and edit the evidence.")
    edited = st.data_editor(pd.DataFrame(rows), hide_index=True, width="stretch", key=f"ed_{cand['id']}", disabled=["Skill", "Category", "Found_by", "Strength", "Mentions"],
                            column_config={"Strength": st.column_config.ProgressColumn("Evidence strength", min_value=0, max_value=1, format="%.2f", help="Heuristic score from mentions and context. Not a probability."),
                                           "Evidence": st.column_config.TextColumn(width="large")})
    manual = st.multiselect("Add skills the resume missed (evidence required)", [s for s in tax.names if s not in set(edited.Skill)])
    mev = st.text_area("Evidence for added skills (project, certificate, link)", height=70) if manual else ""
    agree = st.checkbox("I confirm the selected skills are accurate and I can demonstrate them.")
    if st.button("✅ Save confirmed skills", disabled=not agree):
        if manual and len(mev.strip()) < 10: st.error("Please give evidence (10+ characters) for the skills you added."); return
        keep = [dict(skill=r.Skill, category=r.Category, confidence=r.Strength, evidence=sanitize(r.Evidence, 600), source="resume") for r in edited.itertuples() if r.Confirm]
        keep += [dict(skill=m, category=tax.category[m], confidence=None, evidence=sanitize(mev, 600), source="self-declared") for m in manual]
        if not keep: st.error("Select at least one skill."); return
        db.save_skills(cand["id"], keep); db.update_resume(cand["id"], text)
        h = st.session_state.get(f"hints_{cand['id']}") or {}
        if h and not cand.get("education"): db.upsert_candidate(user["id"], cand["name"], cand["email"], cand["headline"], h.get("education", ""), cand.get("certifications") or h.get("certifications", ""), cand.get("summary") or "")
        db.log_action(user["id"], "skills_confirmed", f"cand={cand['id']} n={len(keep)}"); st.success(f"Saved {len(keep)} confirmed skills. Continue to Job Matching."); st.balloons()


def _verified_tab(cand):
    skills = db.get_skills(cand["id"]) if cand else []
    if not skills: callout("No confirmed skills yet. Complete step 2.", "warn"); return
    df = pd.DataFrame(skills)[["skill", "category", "confidence", "source", "evidence"]]
    c1, c2, c3 = st.columns(3)
    with c1: metric_card("Verified skills", len(df), "confirmed by you", "#16a34a")
    with c2: metric_card("Skill areas", df.category.nunique(), "categories covered", "#7c3aed")
    with c3: metric_card("With evidence text", int((df.evidence.str.len() > 5).sum()), "linked to evidence", "#06b6d4")
    top = df.category.value_counts().index[:2].tolist()
    st.markdown(f"**Profile summary:** {cand.get('headline') or 'Candidate'} with {len(df)} verified skills, strongest in {' and '.join(top)}. Every skill below links to evidence.")
    for cat, g in df.groupby("category"):
        st.markdown(f"**{cat}**"); chips(g.skill.tolist(), "ok")
    with st.expander("Evidence behind each skill"): show_df(df, f"skill_evidence_{cand['id']}.csv")


def render():
    page_header("Candidate Studio", "Build an evidence-backed skill profile. AI suggests; you confirm.", "👤")
    if not require_login(): return
    user = current_user()
    if user["role"] == "recruiter":
        callout("Recruiters see pseudonymised profiles here. Candidate editing is for candidate accounts.", ""); cand = active_candidate("cs_pick"); _verified_tab(cand); return
    cand = db.get_candidate_by_user(user["id"])
    t1, t2, t3 = st.tabs(["1 · Profile", "2 · Resume → Skills", "3 · Verified profile"])
    with t1: _profile_tab(user, cand)
    with t2: _skills_tab(user, cand)
    with t3: _verified_tab(cand)
