import streamlit as st
from components.cards import callout, provider_badge
from components.header import page_header
from database import db
from services import ai_provider
from utils.constants import PROVIDERS
from utils.helpers import current_user
from utils.security import sanitize

QUICK = ["How do I explain a skill gap in an interview?", "What is the difference between precision and recall?", "Make a 30-day plan to learn SQL", "How can I improve my resume bullets?"]


def _context():
    user = current_user(); parts = []
    if user and user["role"] == "candidate" and st.session_state.get("share_skills", True):
        c = db.get_candidate_by_user(user["id"])
        if c:
            sk = [s["skill"] for s in db.get_skills(c["id"])]
            if sk: parts.append("Candidate's confirmed skills: " + ", ".join(sk[:40]) + ".")
            if st.session_state.get("target_job_title"): parts.append(f"Target role: {st.session_state['target_job_title']}.")
    return " ".join(parts)


def render():
    page_header("AI Career Assistant", "Ask anything about careers, skills, resumes or interviews. Choose Gemini, OpenAI or Demo.", "🤖")
    av = ai_provider.available(); st.session_state.setdefault("ai_provider", "Gemini" if av["Gemini"] else ("OpenAI" if av["OpenAI"] else "Demo"))
    c1, c2 = st.columns([2, 3])
    c1.selectbox("Provider", PROVIDERS, key="ai_provider", format_func=lambda p: f"{p} {'✅' if av[p] else '⚠️ key missing'}")
    prov = st.session_state["ai_provider"]; model = st.session_state.get(f"ai_model_{prov}", "")
    with c2:
        st.write(""); provider_badge(prov, ai_provider.model_for(prov, model), prov != "Demo")
    if prov != "Demo" and not av[prov]: callout(f"No {prov} API key found. Add it to .streamlit/secrets.toml or .env, or use Demo mode.", "warn")
    hist = st.session_state.setdefault("chat", [])
    qcols = st.columns(len(QUICK))
    for i, qtxt in enumerate(QUICK):
        if qcols[i].button(qtxt, key=f"q{i}", width="stretch"): st.session_state["pending"] = qtxt
    for m in hist:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    typed = st.chat_input("Ask the career assistant...")
    prompt = typed or st.session_state.pop("pending", None)
    if prompt:
        prompt = sanitize(prompt, 1500); hist.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        system = ai_provider.ASSISTANT_SYSTEM + (" Context (no personal identifiers): " + _context() if _context() else "")
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                r = ai_provider.generate(prov, system, hist[-12:], model)
            if r.ok:
                st.markdown(r.text); hist.append({"role": "assistant", "content": r.text})
                if not r.live: st.caption("Demo mode: rule-based answer, not a live LLM.")
            else:
                st.error(r.error); st.caption("Tip: switch provider above, or use Demo mode to keep presenting.")
                hist.pop()
    if hist and st.button("🧹 Clear conversation"): st.session_state["chat"] = []; st.rerun()
    st.caption("AI assistance is advisory. It cannot make hiring decisions and can be wrong - verify important facts.")
