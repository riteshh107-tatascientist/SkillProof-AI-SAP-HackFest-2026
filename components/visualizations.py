import networkx as nx
import plotly.graph_objects as go
import streamlit as st
from components.charts import style
from config import ASSETS_DIR
from models.skill_model import get_taxonomy
from utils.constants import COLORS


def workflow_gif():
    p = ASSETS_DIR / "workflow.gif"
    if p.exists(): st.image(str(p), width="stretch")


def skill_network(highlight=(), missing=(), height=520):
    tax = get_taxonomy(); g = tax.graph
    pos = nx.spring_layout(g, seed=7, k=0.55)
    cats = sorted(set(tax.category.values())); cc = {c: COLORS[i % len(COLORS)] for i, c in enumerate(cats)}
    ex, ey = [], []
    for a, b in g.edges(): ex += [pos[a][0], pos[b][0], None]; ey += [pos[a][1], pos[b][1], None]
    fig = go.Figure(go.Scatter(x=ex, y=ey, mode="lines", line=dict(width=.7, color="#a9bbd8"), hoverinfo="none", showlegend=False))
    hl, ms = set(highlight), set(missing)
    for c in cats:
        ns = [n for n in g.nodes if tax.category[n] == c]
        fig.add_trace(go.Scatter(x=[pos[n][0] for n in ns], y=[pos[n][1] for n in ns], mode="markers+text", name=c, text=[n for n in ns], textposition="top center", textfont=dict(size=10, color="#0b1f44"),
                                 marker=dict(size=[20 if n in hl else (17 if n in ms else 11) for n in ns], color=cc[c], line=dict(width=[3 if n in hl else (3 if n in ms else 1) for n in ns], color=["#16a34a" if n in hl else ("#dc2626" if n in ms else "#ffffff") for n in ns])),
                                 hovertext=[f"{n} · {c}" for n in ns], hoverinfo="text"))
    fig.update_xaxes(visible=False); fig.update_yaxes(visible=False)
    return style(fig, height)
