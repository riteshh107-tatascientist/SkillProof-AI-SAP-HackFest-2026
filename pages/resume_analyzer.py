import pandas as pd
import streamlit as st
from components import charts
from components.cards import callout, chips, metric_card, provider_badge
from components.header import page_header
from components.resume_input import resume_input
from components.tables import show_df
from database import db
from pages.auth import require_login
from services import ai_provider
from services.matching_engine import match
from services.resume_parser import analyze_quality
from services.skill_extractor import extract_skills
from utils.helpers import current_user, df_csv
from utils.security import redact_pii
from utils.validators import validate_resume_text


def render():
    page_header("Resume Analyzer", "ATS-style quality checklist, skill evidence and role keyword gaps. A coaching tool - not a hiring predictor.", "📄")
    if not require_login(): return
    user = current_user(); cand = db.get_candidate_by_user(user["id"]) if user["role"] == "candidate" else None
    text = resume_input("ra", (cand or {}).get("resume_text") or "")
    jobs = db.get_jobs(); role = st.selectbox("Target role (for keyword gap)", [j["title"] for j in jobs])
    if not st.button("🚀 Analyse resume", type="primary"): return
    ok, msg = validate_resume_text(text)
    if not ok: st.error(msg); return
    q = analyze_quality(text); sk = extract_skills(text); job = next(j for j in jobs if j["title"] == role)
    res = match({s["skill"] for s in sk}, job, text)
    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("Resume quality", f"{q['total']}/100", "heuristic checklist", "#2563eb")
    with c2: metric_card("Skills detected", len(sk), "suggestions, unconfirmed", "#06b6d4")
    with c3: metric_card("Quantified results", q["metrics_found"], "numbers / % found", "#7c3aed")
    with c4: metric_card(f"Keyword fit: {role}", f"{res['score']}%", "skill overlap, not hire odds", "#16a34a")
    t1, t2, t3, t4 = st.tabs(["✅ Checklist", "🧩 Skills & evidence", "🎯 Role keyword gap", "🤖 AI critique"])
    with t1:
        df = pd.DataFrame(q["rows"]).rename(columns={"check": "Check", "weight": "Max", "score": "Score", "fix": "How to improve"})
        st.plotly_chart(charts.bar(df, "Score", "Check", "Score by check (max shown in table)", "h", height=360), width="stretch")
        show_df(df, "resume_quality.csv", "dl_rq"); st.caption("Detected sections: " + (", ".join(q["sections"]) or "none"))
    with t2:
        show_df(pd.DataFrame(sk)[["skill", "category", "confidence", "mentions", "evidence"]] if sk else pd.DataFrame(), "resume_skills.csv", "dl_rs")
        callout("Mentions are not proof. Confirm real skills in Candidate Studio so each links to evidence.", "warn")
    with t3:
        st.markdown("**Present in resume**"); chips(res["matched_required"] + res["matched_preferred"], "ok")
        st.markdown("**Add (if true) - required**"); chips(res["missing_required"], "miss"); st.markdown("**Add (if true) - preferred**"); chips(res["missing_preferred"], "")
        callout("Only add keywords for skills you genuinely have. Keyword stuffing is detectable and unfair to other candidates.", "warn")
    with t4:
        st.caption("Optional. Sends a PII-redacted excerpt to the selected provider only if you consented in Account & Settings.")
        prov = st.session_state.get("ai_provider", "Demo")
        if st.button(f"Get AI critique via {prov}"):
            if prov != "Demo" and not st.session_state.get("share_resume"): st.error("Enable resume-excerpt consent in Account & Settings first.")
            else:
                prompt = f"Critique this resume for a {role} role. Give 5 concrete improvements.\n\n{redact_pii(text)[:6000]}"
                r = ai_provider.generate(prov, ai_provider.ASSISTANT_SYSTEM, [{"role": "user", "content": prompt}], st.session_state.get(f"ai_model_{prov}", ""), 700)
                if r.ok: provider_badge(r.provider, r.model, r.live); st.markdown(r.text)
                else: st.error(r.error)
    st.download_button("⬇️ Download analysis summary (CSV)", df_csv(pd.DataFrame(q["rows"])), "resume_analysis.csv", "text/csv")
