"""Resume text extraction, section parsing and a transparent quality checklist (heuristic, not a hiring prediction)."""
import io, re
from utils.security import sanitize

SECTIONS = ["summary", "objective", "education", "skills", "projects", "experience", "internship", "certifications", "achievements", "publications"]
VERBS = {"built", "developed", "implemented", "designed", "automated", "deployed", "created", "led", "analysed", "analyzed", "optimised", "optimized",
         "improved", "reduced", "increased", "launched", "mentored", "organised", "organized", "trained", "tested", "integrated", "presented", "engineered"}


def extract_text(filename: str, data: bytes):
    """Returns (text, error). Errors are friendly strings, never stack traces."""
    ext = filename.lower().rsplit(".", 1)[-1]
    try:
        if ext == "pdf":
            from PyPDF2 import PdfReader
            reader = PdfReader(io.BytesIO(data))
            if reader.is_encrypted: return "", "This PDF is password-protected."
            text = "\n".join((p.extract_text() or "") for p in reader.pages)
        elif ext == "docx":
            import docx
            d = docx.Document(io.BytesIO(data))
            text = "\n".join(p.text for p in d.paragraphs)
            for t in d.tables:
                for row in t.rows: text += "\n" + " | ".join(c.text for c in row.cells)
        else:
            text = data.decode("utf-8", errors="ignore")
    except Exception:
        return "", "Could not read this file. It may be corrupted or scanned (image-only)."
    text = sanitize(text, 60000)
    return (text, "") if text.strip() else ("", "No selectable text found (scanned PDFs need OCR, which is not included).")


def parse_sections(text: str) -> dict:
    out, cur = {}, "header"
    for line in text.splitlines():
        key = re.sub(r"[^a-z ]", "", line.strip().lower())
        if key in SECTIONS or (key.rstrip("s") in SECTIONS and len(line.strip()) < 25): cur = key; out.setdefault(cur, []); continue
        out.setdefault(cur, []).append(line)
    return {k: "\n".join(v).strip() for k, v in out.items() if "\n".join(v).strip()}


def contact_info(text: str) -> dict:
    return {"email": bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)), "phone": bool(re.search(r"(?<!\d)(?:\+?\d{1,3}[\s-]?)?(?:\d[\s-]?){9,12}(?!\d)", text)),
            "github": "github.com" in text.lower(), "linkedin": "linkedin.com" in text.lower()}


def profile_hints(text: str) -> dict:
    s = parse_sections(text)
    edu = [l.strip() for l in s.get("education", "").splitlines() if l.strip()][:3]
    certs = [l.strip() for l in re.split(r"[;\n]", s.get("certifications", "")) if l.strip()][:6]
    return {"education": "; ".join(edu), "certifications": "; ".join(certs), "sections": list(s)}


def analyze_quality(text: str) -> dict:
    """Weighted checklist, each item scored 0..1 with a plain-language fix. Total 0-100."""
    from services.skill_extractor import extract_skills
    words = text.split(); s = parse_sections(text); low = text.lower(); c = contact_info(text)
    bullets = [l for l in text.splitlines() if len(l.split()) >= 5]
    metrics = len(re.findall(r"\b\d+(?:\.\d+)?\s?(?:%|x|k|\+)|\b\d{2,}\b", text))
    verbs = sum(1 for l in bullets if l.strip().split()[0].lower().strip("•-*") in VERBS)
    n_skills = len(extract_skills(text)); proj = len([l for l in s.get("projects", "").splitlines() if l.strip()])
    items = [
        ("Core sections present (skills, projects/experience, education)", 25, sum(k in s for k in ["skills", "education"]) / 2 * 0.5 + (0.5 if ("projects" in s or "experience" in s or "internship" in s) else 0), "Add clear SKILLS, PROJECTS/EXPERIENCE and EDUCATION headings."),
        ("Contact details (email + phone)", 10, (c["email"] + c["phone"]) / 2, "Add a professional email and phone number."),
        ("Public proof links (GitHub / LinkedIn)", 10, (c["github"] + c["linkedin"]) / 2, "Link your GitHub and LinkedIn so claims can be verified."),
        ("Quantified outcomes (numbers, %)", 15, min(metrics / 4, 1), "Add measurable results, e.g. 'reduced load time by 30%'."),
        ("Action-verb bullets", 10, min(verbs / 4, 1), "Start bullets with verbs such as Built, Implemented, Automated."),
        ("Skills backed by project evidence", 15, min(proj / 3, 1) * 0.6 + min(n_skills / 8, 1) * 0.4, "Describe 2-4 projects and name the tools used in each."),
        ("Length (250-900 words)", 10, 1.0 if 250 <= len(words) <= 900 else (0.6 if 120 <= len(words) < 250 or 900 < len(words) <= 1200 else 0.2), "Aim for a focused 1-2 page resume."),
        ("Certifications / achievements", 5, 1.0 if ("certifications" in s or "achievements" in s) else 0.0, "Add relevant certificates or achievements."),
    ]
    rows = [dict(check=n, weight=w, score=round(sc * w, 1), max=w, fix=("OK" if sc >= 0.85 else fix)) for n, w, sc, fix in items]
    return {"total": round(sum(r["score"] for r in rows)), "rows": rows, "words": len(words), "metrics_found": metrics, "sections": list(s), "contact": c}
