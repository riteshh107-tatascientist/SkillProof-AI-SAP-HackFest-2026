import plotly.express as px
import plotly.graph_objects as go
from utils.constants import COLORS

INK = "#0b1f44"


def style(fig, height=380, legend=True):
    fig.update_layout(template="plotly_white", paper_bgcolor="#ffffff", plot_bgcolor="#ffffff", height=height, colorway=COLORS,
                      font=dict(color=INK, size=13, family="Inter, Segoe UI, sans-serif"), margin=dict(l=20, r=20, t=50, b=30), showlegend=legend,
                      title=dict(font=dict(color=INK, size=16)), legend=dict(font=dict(color=INK)))
    fig.update_xaxes(tickfont=dict(color=INK), title_font=dict(color=INK), gridcolor="#e5edf9", linecolor="#9fb3d1")
    fig.update_yaxes(tickfont=dict(color=INK), title_font=dict(color=INK), gridcolor="#e5edf9", linecolor="#9fb3d1")
    return fig


def bar(df, x, y, title="", orientation="v", color=None, height=380):
    fig = px.bar(df, x=x, y=y, orientation=orientation, title=title, color=color, text_auto=True)
    if orientation == "h": fig.update_yaxes(autorange="reversed")
    return style(fig, height, legend=color is not None)


def donut(df, names, values, title=""):
    fig = px.pie(df, names=names, values=values, hole=.55, title=title)
    fig.update_traces(textfont_color="#ffffff", textinfo="percent+label")
    return style(fig, 380, legend=False)


def gauge(value, title="Skill coverage"):
    fig = go.Figure(go.Indicator(mode="gauge+number", value=value, number=dict(suffix="%", font=dict(color=INK)), title=dict(text=title, font=dict(color=INK)),
                                 gauge=dict(axis=dict(range=[0, 100], tickfont=dict(color=INK)), bar=dict(color="#2563eb"),
                                            steps=[dict(range=[0, 40], color="#fde2e2"), dict(range=[40, 70], color="#fff1c9"), dict(range=[70, 100], color="#d9f5e4")])))
    return style(fig, 280, legend=False)


def heatmap(df, title=""):
    fig = px.imshow(df, aspect="auto", color_continuous_scale=["#ffffff", "#93c5fd", "#2563eb", "#4c1d95"], title=title)
    return style(fig, max(320, 28 * len(df)), legend=False)


def radar(categories, series: dict, title=""):
    fig = go.Figure()
    for name, vals in series.items(): fig.add_trace(go.Scatterpolar(r=vals + vals[:1], theta=categories + categories[:1], fill="toself", name=name))
    fig.update_layout(polar=dict(bgcolor="#ffffff", radialaxis=dict(range=[0, 100], tickfont=dict(color=INK)), angularaxis=dict(tickfont=dict(color=INK))), title=title)
    return style(fig, 420)


def line(df, x, y, title=""):
    return style(px.line(df, x=x, y=y, markers=True, title=title), 320, legend=False)
