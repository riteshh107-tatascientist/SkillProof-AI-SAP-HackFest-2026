import streamlit as st
from utils.helpers import compact
from utils.security import esc


def metric_card(label, value, hint="", accent="#2563eb"):
    st.markdown(compact(f'<div class="sp-card sp-metric" style="--ac:{accent}"><div class="l">{esc(label)}</div><div class="v">{esc(value)}</div><div class="h">{esc(hint)}</div></div>'), unsafe_allow_html=True)


def info_card(title, body, icon=""):
    st.markdown(compact(f'<div class="sp-card"><h4>{icon} {esc(title)}</h4><p>{esc(body)}</p></div>'), unsafe_allow_html=True)


def chips(items, kind=""):
    if not items: return
    st.markdown("".join(f'<span class="sp-chip {kind}">{esc(i)}</span>' for i in items), unsafe_allow_html=True)


def callout(text, kind=""):
    st.markdown(f'<div class="sp-callout {kind}">{esc(text)}</div>', unsafe_allow_html=True)


def empty_state(text, icon="📭"):
    callout(f"{icon} {text}")


def provider_badge(provider, model, live):
    cls, txt = ("on", f"LIVE · {provider} · {model}") if live else ("demo", "DEMO MODE · rule-based, not a live LLM")
    st.markdown(f'<span class="sp-live {cls}">{esc(txt)}</span>', unsafe_allow_html=True)
