"""Generates local SVG illustrations and the animated workflow GIF (no external images). Run: python assets/generate_assets.py"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
A = Path(__file__).parent; (A / "illustrations").mkdir(exist_ok=True)
DEFS = '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#22d3ee"/><stop offset="1" stop-color="#8b5cf6"/></linearGradient></defs>'
(A / "logo.svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">{DEFS}<rect width="64" height="64" rx="16" fill="#0b2a6b"/><path d="M32 10 L50 17 V31 C50 42 42 50 32 54 C22 50 14 42 14 31 V17 Z" fill="none" stroke="url(#g)" stroke-width="3.5"/><path d="M23 32 L30 39 L42 25" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg>')
nodes = [(60, 70), (180, 30), (300, 80), (420, 35), (540, 75), (660, 40), (120, 130), (260, 140), (400, 125), (560, 140)]
edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (0, 6), (6, 7), (2, 7), (7, 8), (3, 8), (8, 9), (4, 9)]
lines = "".join(f'<line x1="{nodes[a][0]}" y1="{nodes[a][1]}" x2="{nodes[b][0]}" y2="{nodes[b][1]}" stroke="#67e8f9" stroke-opacity=".55" stroke-width="1.5"/>' for a, b in edges)
dots = "".join(f'<circle cx="{x}" cy="{y}" r="7" fill="url(#g)"><animate attributeName="r" values="6;10;6" dur="{2 + i % 3}s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;.6;1" dur="{2 + i % 3}s" repeatCount="indefinite"/></circle>' for i, (x, y) in enumerate(nodes))
(A / "hero.svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 170" width="100%">{DEFS}{lines}{dots}<circle r="4" fill="#fff"><animateMotion dur="6s" repeatCount="indefinite" path="M60 70 L180 30 L300 80 L420 35 L540 75 L660 40"/></circle></svg>')
(A / "skill_network.svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 170">{DEFS}<rect width="720" height="170" fill="#f4f8ff"/>{lines}{dots}</svg>')
def box(x, y, w, h, t, fill="#0b2a6b", dash=False, tc="#fff"):
    d = ' stroke="#7c3aed" stroke-width="2" stroke-dasharray="6 4"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}"{d}/><text x="{x + w/2}" y="{y + h/2 + 4}" text-anchor="middle" font-family="Segoe UI,Arial" font-size="12" font-weight="700" fill="{tc}">{t}</text>'
def arrow(x1, y1, x2, y2, dash=False): return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#2563eb" stroke-width="2"{" stroke-dasharray=\"5 4\"" if dash else ""} marker-end="url(#a)"/>'
arch = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 360" width="100%"><defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#2563eb"/></marker></defs><rect width="900" height="360" fill="#ffffff"/>'
arch += box(20, 30, 150, 44, "Candidate UI") + box(20, 100, 150, 44, "Recruiter UI") + box(20, 170, 150, 44, "Fairness Lab")
arch += box(230, 60, 190, 150, "Streamlit App · pages / components", "#1d4ed8")
arch += box(480, 20, 170, 40, "Skill extraction · NLP") + box(480, 72, 170, 40, "Matching · TF-IDF") + box(480, 124, 170, 40, "Fairness engine") + box(480, 176, 170, 40, "Roadmap · Interview")
arch += box(710, 30, 170, 44, "SQLite · audit log", "#0e7490") + box(710, 100, 170, 44, "AI provider layer", "#6d28d9") + box(710, 170, 80, 40, "Gemini", "#4c1d95") + box(800, 170, 80, 40, "OpenAI", "#4c1d95")
arch += box(230, 270, 190, 40, "SAP SuccessFactors (proposed)", "#f3edff", True, "#4c1d95") + box(440, 270, 150, 40, "SAP BTP (proposed)", "#f3edff", True, "#4c1d95") + box(610, 270, 130, 40, "SAP Analytics Cloud (proposed)", "#f3edff", True, "#4c1d95") + box(760, 270, 120, 40, "Joule (proposed)", "#f3edff", True, "#4c1d95")
arch += arrow(170, 52, 230, 110) + arrow(170, 122, 230, 130) + arrow(170, 192, 230, 160) + arrow(420, 135, 480, 90) + arrow(650, 50, 710, 52) + arrow(650, 130, 710, 122) + arrow(325, 210, 325, 270, True) + arrow(515, 210, 515, 270, True)
(A / "architecture.svg").write_text(arch + "</svg>")
def ill(name, body): (A / "illustrations" / name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 200">{DEFS}<rect width="320" height="200" rx="16" fill="#eef5ff"/>{body}</svg>')
ill("recruitment.svg", '<rect x="40" y="40" width="110" height="120" rx="10" fill="#fff" stroke="#2563eb"/><circle cx="95" cy="75" r="16" fill="url(#g)"/><rect x="62" y="100" width="66" height="8" rx="4" fill="#93c5fd"/><rect x="62" y="118" width="50" height="8" rx="4" fill="#bfdbfe"/><circle cx="215" cy="95" r="38" fill="none" stroke="#7c3aed" stroke-width="8"/><line x1="243" y1="123" x2="275" y2="155" stroke="#7c3aed" stroke-width="10" stroke-linecap="round"/>')
ill("analytics.svg", '<rect x="50" y="110" width="30" height="50" fill="#93c5fd"/><rect x="100" y="80" width="30" height="80" fill="#2563eb"/><rect x="150" y="55" width="30" height="105" fill="#7c3aed"/><rect x="200" y="95" width="30" height="65" fill="#22d3ee"/><polyline points="55,100 115,70 165,45 215,80" fill="none" stroke="#0b1f44" stroke-width="3"/>')
ill("learning.svg", '<path d="M60 60 L160 40 L260 60 L260 150 L160 130 L60 150 Z" fill="#fff" stroke="#2563eb" stroke-width="3"/><line x1="160" y1="40" x2="160" y2="130" stroke="#2563eb" stroke-width="3"/><path d="M80 170 Q160 120 250 170" fill="none" stroke="url(#g)" stroke-width="5" stroke-dasharray="8 6"/>')
(A / "candidate.svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">{DEFS}<circle cx="100" cy="70" r="34" fill="url(#g)"/><path d="M40 170 C40 120 160 120 160 170 Z" fill="#0b2a6b"/><circle cx="150" cy="150" r="22" fill="#16a34a"/><path d="M140 150 L148 158 L162 142" stroke="#fff" stroke-width="4" fill="none"/></svg>')
# animated GIF: pipeline highlight
stages = ["Upload", "Extract", "Confirm", "Match", "Roadmap", "Review"]
def font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "arialbd.ttf"):
        try: return ImageFont.truetype(p, sz)
        except Exception: pass
    return ImageFont.load_default()
frames = []
for step in range(len(stages) * 3):
    im = Image.new("RGB", (960, 190), "#06112b"); d = ImageDraw.Draw(im); cur = step // 3; ph = step % 3
    for i, s in enumerate(stages):
        x = 30 + i * 155; on = i == cur; done = i < cur
        fill = "#2563eb" if on else ("#0e7490" if done else "#12307a")
        d.rounded_rectangle([x, 55, x + 135, 135], 16, fill=fill, outline="#67e8f9" if on else "#2b5cd9", width=4 if on else 2)
        d.text((x + 67, 82), f"{i+1}", font=font(26), fill="#ffffff", anchor="mm"); d.text((x + 67, 114), s, font=font(17), fill="#ffffff", anchor="mm")
        if i < len(stages) - 1: d.polygon([(x + 140, 95), (x + 150, 89), (x + 150, 101)], fill="#67e8f9")
    px = 30 + cur * 155 + 20 + ph * 40; d.ellipse([px, 150, px + 12, 162], fill="#c4b5fd")
    d.text((480, 22), "SkillProof AI · resume to roadmap to human-reviewed decision", font=font(16), fill="#cfe0ff", anchor="mm")
    frames.append(im)
frames[0].save(A / "workflow.gif", save_all=True, append_images=frames[1:], duration=380, loop=0, optimize=True)
