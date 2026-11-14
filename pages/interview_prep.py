import streamlit as st
from components import charts
from components.cards import callout, provider_badge
from components.header import page_header
from database import db
from pages.auth import require_login
from services import ai_provider
from services.interview_engine import generate_questions, score_answer
from utils.helpers import active_candidate, current_user, split_pipe
from utils.security import redact_pii, sanitize


def render():
    page_header("Interview Preparation", "Role-specific practice with transparent feedback and progress tracking.", "🎤")
    if not require_login(): return
    cand = active_candidate("ip_pick")
    if not cand: return
    own = current_user()["role"] == "candidate"
    jobs = db.get_jobs(); role = st.selectbox("Role", [j["title"] for j in jobs]); job = next(j for j in jobs if j["title"] == role)
    have = [s["skill"] for s in db.get_skills(cand["id"])]; req = split_pipe(job["required_skills"])
    c1, c2 = st.columns(2)
    focus = c1.radio("Focus on", ["Role-required skills", "My verified skills", "My skill gaps"], horizontal=True)
    kind = c2.radio("Question type", ["Mixed", "Technical", "Behavioural"], horizontal=True)
    pool = {"Role-required skills": req, "My verified skills": [s for s in have if s in req] or have, "My skill gaps": [s for s in req if s not in have] or req}[focus]
    if st.button("🎲 Generate practice set", type="primary"): st.session_state["iq"] = generate_questions(pool, kind, 5); st.session_state["iq_i"] = 0
    qs = st.session_state.get("iq")
    if not qs: callout("Generate a set to begin.", ""); _history(cand); return
    labels = [f"{i+1}. [{q['skill']}] {q['question'][:70]}" for i, q in enumerate(qs)]
    i = labels.index(st.selectbox("Question", labels)); q = qs[i]
    st.markdown(f"**{q['type']} · {q['skill']}**"); st.info(q["question"])
    ans = st.text_area("Your answer", key=f"ans_{i}", height=160, placeholder="Aim for 80-200 words. Use a concrete example; for behavioural questions use Situation-Task-Action-Result.")
    if st.button("📝 Score my answer"):
        sc, fb = score_answer(ans, q["keywords"], q["type"]); st.session_state[f"res_{i}"] = (sc, fb)
        if own: db.add_attempt(cand["id"], q["skill"], q["question"], sanitize(ans, 3000), sc, " | ".join(fb))
    if f"res_{i}" in st.session_state:
        sc, fb = st.session_state[f"res_{i}"]; st.metric("Heuristic score", f"{sc}/100")
        for f in fb: st.markdown(f"- {f}")
        st.caption("Scoring is a transparent heuristic (keyword coverage, structure, specificity), not an expert judgement.")
        prov = st.session_state.get("ai_provider", "Demo")
        if prov != "Demo" and st.button(f"🤖 Deeper feedback from {prov} (sends this answer, PII-redacted)"):
            r = ai_provider.generate(prov, ai_provider.ASSISTANT_SYSTEM, [{"role": "user", "content": f"Interview question: {q['question']}\nCandidate answer: {redact_pii(ans)[:3000]}\nGive concise feedback: strengths, gaps, and an improved outline."}], st.session_state.get(f"ai_model_{prov}", ""), 600)
            if r.ok: provider_badge(r.provider, r.model, r.live); st.markdown(r.text)
            else: st.error(r.error)
    _history(cand)


def _history(cand):
    h = db.list_attempts(cand["id"])
    if len(h): st.markdown("#### 📈 Progress"); h["attempt"] = range(1, len(h) + 1); st.plotly_chart(charts.line(h, "attempt", "score", "Practice score over time"), width="stretch")
