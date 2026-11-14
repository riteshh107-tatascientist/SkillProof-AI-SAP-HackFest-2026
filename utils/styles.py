import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, .stApp, [class*="st-"] { font-family: 'Inter','Segoe UI',system-ui,-apple-system,sans-serif; }
.stApp { background: radial-gradient(1100px 480px at 8% -8%, #dff1ff 0%, transparent 60%), radial-gradient(900px 420px at 100% 0%, #ece8ff 0%, transparent 55%), #f6f9ff; }
[data-testid="stMainBlockContainer"] { max-width: 1280px; padding-top: 1rem; }
header[data-testid="stHeader"] { background: transparent; }
/* ---- readable text on the light workspace ---- */
[data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3, [data-testid="stMain"] h4 { color: #0b1f44; font-weight: 800; letter-spacing: -.01em; }
[data-testid="stMain"] .stMarkdown p, [data-testid="stMain"] .stMarkdown li, [data-testid="stMain"] [data-testid="stCaptionContainer"] { color: #1e293b; }
[data-testid="stMain"] [data-testid="stCaptionContainer"] { color: #475569; }
[data-testid="stWidgetLabel"] p, label p { color: #0f172a !important; font-weight: 600; }
input, textarea { color: #0f172a !important; background: #ffffff !important; }
[data-baseweb="select"] > div { background: #fff !important; color: #0f172a !important; }
[data-baseweb="select"] * { color: #0f172a; }
[data-baseweb="popover"] li, [data-baseweb="popover"] div { color: #0f172a; }
button[data-baseweb="tab"] p { color: #334155 !important; font-weight: 600; }
button[data-baseweb="tab"][aria-selected="true"] p { color: #1d4ed8 !important; }
[data-testid="stExpander"] { background: #fff; border: 1px solid #dbe6f7; border-radius: 12px; }
[data-testid="stExpander"] summary p, [data-testid="stExpander"] p, [data-testid="stExpander"] li { color: #0f172a !important; }
[data-testid="stChatMessage"] { background: #fff; border: 1px solid #dbe6f7; border-radius: 14px; box-shadow: 0 4px 14px rgba(15,35,95,.05); }
[data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li { color: #0f172a !important; }
.stButton > button, .stDownloadButton > button { border-radius: 10px; font-weight: 600; border: 1px solid #b6c8e8; color: #0b1f44; background: #fff; transition: all .2s; }
.stButton > button:hover, .stDownloadButton > button:hover { border-color: #2563eb; color: #1d4ed8; transform: translateY(-1px); box-shadow: 0 6px 16px rgba(37,99,235,.18); }
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] { background: linear-gradient(90deg,#2563eb,#7c3aed); color: #fff !important; border: 0; }
/* ---- sidebar (dark navy) ---- */
[data-testid="stSidebar"] { background: linear-gradient(180deg,#06112b 0%,#0a1d4a 60%,#0e2a63 100%); border-right: 1px solid #1e3a8a; }
[data-testid="stSidebar"] * { color: #dbe7ff; }
[data-testid="stSidebar"] .stButton > button { background: #12307a; color: #fff !important; border: 1px solid #2b5cd9; width: 100%; }
[data-testid="stSidebar"] [role="radiogroup"] label { padding: 9px 12px; border-radius: 10px; margin-bottom: 3px; transition: all .2s; width: 100%; }
[data-testid="stSidebar"] [role="radiogroup"] label:hover { background: rgba(56,189,248,.16); transform: translateX(3px); }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) { background: linear-gradient(90deg,rgba(37,99,235,.65),rgba(124,58,237,.55)); box-shadow: 0 0 16px rgba(56,189,248,.35); }
[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child { display: none; }
.sp-userbox { border: 1px solid rgba(125,170,255,.35); border-radius: 12px; padding: 10px 12px; background: rgba(255,255,255,.06); font-size: .85rem; margin: 10px 0; }
/* ---- event bar + hero ---- */
.sp-eventbar { display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap; padding:10px 18px; border-radius:14px; margin-bottom:14px; background:linear-gradient(100deg,#06112b,#0b2a6b 60%,#26237a); box-shadow:0 8px 26px rgba(11,42,107,.28); }
.sp-eventbar, .sp-eventbar * { color:#fff !important; }
.sp-event { display:inline-block; padding:6px 16px; border-radius:999px; border:1px solid rgba(34,211,238,.85); background:rgba(6,25,70,.7); letter-spacing:.13em; font-weight:800; font-size:.78rem; animation: glow 2.8s ease-in-out infinite; }
.sp-brand { font-weight:800; letter-spacing:.02em; }
.sp-disc { font-size:.72rem; opacity:.85; }
@keyframes glow { 0%,100% { box-shadow:0 0 10px rgba(34,211,238,.55),0 0 26px rgba(124,58,237,.3);} 50% { box-shadow:0 0 20px rgba(34,211,238,.95),0 0 48px rgba(124,58,237,.6);} }
.sp-hero { position:relative; overflow:hidden; border-radius:24px; padding:40px 42px; margin-bottom:18px; background:linear-gradient(120deg,#06112b,#0b2a6b 55%,#1f2a80); box-shadow:0 20px 54px rgba(11,42,107,.36); }
.sp-hero::before { content:""; position:absolute; width:520px; height:520px; right:-120px; top:-200px; background:radial-gradient(circle,rgba(34,211,238,.6),transparent 62%); animation: floaty 9s ease-in-out infinite; }
.sp-hero::after { content:""; position:absolute; width:480px; height:480px; left:-140px; bottom:-260px; background:radial-gradient(circle,rgba(139,92,246,.55),transparent 62%); animation: floaty 11s ease-in-out infinite reverse; }
.sp-sweep { position:absolute; inset:0; background:linear-gradient(100deg,transparent 35%,rgba(255,255,255,.13) 50%,transparent 65%); animation: sweep 6s linear infinite; }
.sp-hero-in { position:relative; z-index:2; }
.sp-hero.sp-hero h1, .sp-hero.sp-hero h2, .sp-hero.sp-hero p, .sp-hero.sp-hero span, .sp-hero.sp-hero div { color:#fff !important; }
.sp-hero.sp-hero h1 { font-size:3rem; font-weight:800; margin:14px 0 6px; line-height:1.05; }
.sp-grad { background:linear-gradient(90deg,#67e8f9,#c4b5fd); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent !important; color:transparent !important; }
.sp-hero.sp-hero p.sp-sub { color:#cfe0ff !important; font-size:1.08rem; max-width:760px; }
.sp-rot { position:relative; height:1.7rem; margin:8px 0 4px; }
.sp-rot span { position:absolute; left:0; opacity:0; font-weight:700; color:#67e8f9 !important; animation: rot 9s infinite; }
.sp-rot span:nth-child(2) { animation-delay:3s; } .sp-rot span:nth-child(3) { animation-delay:6s; }
@keyframes rot { 0%,3% {opacity:0; transform:translateY(8px);} 8%,30% {opacity:1; transform:none;} 36%,100% {opacity:0; transform:translateY(-8px);} }
@keyframes floaty { 0%,100% { transform:translate(0,0);} 50% { transform:translate(-30px,26px);} }
@keyframes sweep { 0% { transform:translateX(-100%);} 100% { transform:translateX(100%);} }
@keyframes fadeup { from { opacity:0; transform:translateY(14px);} to { opacity:1; transform:none;} }
.sp-marquee { overflow:hidden; border-radius:12px; background:#fff; border:1px solid #dbe6f7; margin:6px 0 18px; }
.sp-marquee div { display:inline-block; white-space:nowrap; padding:10px 0; animation: scroll 26s linear infinite; color:#0b1f44; font-weight:700; }
.sp-marquee span { margin:0 26px; color:#0b1f44 !important; }
@keyframes scroll { from { transform:translateX(0);} to { transform:translateX(-50%);} }
/* ---- cards ---- */
.sp-card { background:#fff; border:1px solid #e0e9f8; border-radius:16px; padding:18px 20px; box-shadow:0 6px 20px rgba(15,35,95,.07); animation: fadeup .6s ease both; transition: transform .2s, box-shadow .2s; height:100%; }
.sp-card:hover { transform:translateY(-3px); box-shadow:0 12px 28px rgba(37,99,235,.16); }
.sp-card h4 { margin:0 0 6px; color:#0b1f44 !important; font-size:1.02rem; }
.sp-card p { margin:0; color:#334155 !important; font-size:.92rem; line-height:1.45; }
.sp-metric { position:relative; overflow:hidden; }
.sp-metric::before { content:""; position:absolute; left:0; top:0; right:0; height:4px; background:var(--ac,#2563eb); }
.sp-metric .l { color:#475569 !important; font-size:.74rem; font-weight:700; text-transform:uppercase; letter-spacing:.07em; }
.sp-metric .v { color:#0b1f44 !important; font-size:2rem; font-weight:800; line-height:1.15; margin-top:4px; }
.sp-metric .h { color:#475569 !important; font-size:.78rem; margin-top:2px; }
.sp-pagehead { margin:4px 0 14px; } .sp-pagehead h2 { margin:0; color:#0b1f44 !important; } .sp-pagehead p { margin:2px 0 0; color:#475569 !important; }
.sp-chip { display:inline-block; padding:4px 11px; margin:3px 4px 3px 0; border-radius:999px; font-size:.8rem; font-weight:600; border:1px solid #bfd3f5; background:#eef5ff; color:#12327a !important; }
.sp-chip.ok { background:#e8f8ef; border-color:#a7e3bf; color:#0f5132 !important; } .sp-chip.miss { background:#fff1f0; border-color:#f3b8b3; color:#8a1c14 !important; } .sp-chip.tr { background:#f3edff; border-color:#cdb9f6; color:#4c1d95 !important; }
.sp-callout { border-radius:12px; padding:12px 16px; margin:8px 0; border-left:5px solid #2563eb; background:#eef5ff; color:#0f172a; } .sp-callout * { color:#0f172a !important; }
.sp-callout.warn { border-left-color:#f59e0b; background:#fff8e6; } .sp-callout.ok { border-left-color:#16a34a; background:#ecfbf1; } .sp-callout.bad { border-left-color:#dc2626; background:#fff1f1; }
.sp-live { display:inline-block; padding:3px 10px; border-radius:999px; font-size:.75rem; font-weight:700; }
.sp-live.on { background:#dcfce7; color:#14532d !important; } .sp-live.demo { background:#fef3c7; color:#78350f !important; }
@media (max-width: 760px) { .sp-hero { padding:26px 20px; } .sp-hero.sp-hero h1 { font-size:2.1rem; } [data-testid="stMainBlockContainer"] { padding-left:1rem; padding-right:1rem; } }
@media (prefers-reduced-motion: reduce) { * { animation:none !important; transition:none !important; } .sp-rot span:first-child { opacity:1; } }
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)
