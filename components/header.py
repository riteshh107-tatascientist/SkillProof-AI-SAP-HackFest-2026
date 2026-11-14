import streamlit as st
from config import APP_NAME, EVENT, THEME, DISCLAIMER, TAGLINE
from utils.helpers import compact, inline_svg
from utils.security import esc


def event_bar():
    st.markdown(compact(f'<div class="sp-eventbar"><span class="sp-event">✦ {esc(EVENT)} · {esc(THEME).upper()}</span><span class="sp-brand">🛡️ {esc(APP_NAME)}</span><span class="sp-disc">{esc(DISCLAIMER)}</span></div>'), unsafe_allow_html=True)


def page_header(title, subtitle="", icon=""):
    st.markdown(compact(f'<div class="sp-pagehead"><h2>{icon} {esc(title)}</h2><p>{esc(subtitle)}</p></div>'), unsafe_allow_html=True)


def hero():
    st.markdown(compact(f'''<div class="sp-hero"><div class="sp-sweep"></div><div class="sp-hero-in">
      <span class="sp-event">✦ {esc(EVENT)} · INCLUSIVE WORKFORCE</span>
      <h1>Skill<span class="sp-grad">Proof</span> AI</h1>
      <div class="sp-rot"><span>Fair Skills. Evidence over pedigree.</span><span>Inclusive Talent. Every pathway counts.</span><span>Smarter Workforces. Humans decide.</span></div>
      <p class="sp-sub">{esc(TAGLINE)} An explainable, human-in-the-loop platform that proves capability through evidence - from resume to roadmap to fairness audit.</p>
      <div style="margin-top:14px;max-width:760px">{inline_svg("hero.svg")}</div></div></div>'''), unsafe_allow_html=True)
    items = ["✅ Skills over pedigree", "🔍 Evidence-linked skills", "👩‍⚖️ Human approval workflow", "⚖️ Fairness audit lab", "🔐 Privacy-first AI", "🧠 Explainable matching", "🗺️ 30/60/90 roadmaps", "🤖 Gemini · OpenAI · Demo"]
    strip = "".join(f"<span>{i}</span>" for i in items)
    st.markdown(f'<div class="sp-marquee"><div>{strip}{strip}</div></div>', unsafe_allow_html=True)
