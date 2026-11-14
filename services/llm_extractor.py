"""LLM-assisted skill extraction (Gemini / OpenAI). Anti-hallucination: every skill must be in the taxonomy AND quote
evidence that literally appears in the (PII-redacted) resume text; anything else is dropped. Output = suggestions only."""
import json, re
from models.skill_model import get_taxonomy
from services import ai_provider
from utils.security import redact_pii

SYSTEM = "You extract skills from resumes. Output ONLY a JSON array, no prose, no markdown."


def _norm(t): return re.sub(r"\s+", " ", t).strip().lower()


def _parse(text):
    m = re.search(r"\[.*\]", text, re.S)
    if not m: return []
    try: data = json.loads(m.group(0))
    except Exception: return []
    return data if isinstance(data, list) else []


def llm_extract(resume_text: str, provider: str, model: str = ""):
    """Returns {'ok', 'skills', 'rejected', 'error'}. Never raises."""
    if provider == "Demo": return {"ok": False, "skills": [], "rejected": 0, "error": "Select Gemini or OpenAI for AI extraction."}
    tax = get_taxonomy(); text = redact_pii(resume_text)[:9000]
    prompt = ("From the resume below, list the skills the candidate demonstrably has. Use ONLY skill names from this list (exact spelling):\n"
              + ", ".join(tax.names) + "\n\nFor each skill return {\"skill\": <name>, \"evidence\": <a short VERBATIM quote (max 200 chars) copied from the resume>}. "
              "Include a skill only if the resume gives concrete evidence of using it (a project, job, certificate). Do not infer skills that are not supported by a quote.\n\nRESUME:\n" + text)
    r = ai_provider.generate(provider, SYSTEM, [{"role": "user", "content": prompt}], model, 1800)
    if not r.ok: return {"ok": False, "skills": [], "rejected": 0, "error": r.error}
    norm_text, kept, rejected, seen = _norm(text), [], 0, set()
    for item in _parse(r.text):
        sk = item.get("skill") if isinstance(item, dict) else None; ev = str(item.get("evidence", "")).strip(" \"'") if isinstance(item, dict) else ""
        if sk in tax.category and sk not in seen and len(ev) >= 8 and _norm(ev) in norm_text:
            seen.add(sk); kept.append({"skill": sk, "category": tax.category[sk], "confidence": 0.75, "mentions": 1, "evidence": ev[:220], "method": f"LLM ({r.provider})"})
        else: rejected += 1
    return {"ok": True, "skills": kept, "rejected": rejected, "error": ""}


def merge_suggestions(base: list, llm: list) -> list:
    """Union of rule-based and LLM suggestions; agreement between the two raises evidence strength."""
    by = {s["skill"]: dict(s) for s in base}
    for s in llm:
        if s["skill"] in by:
            b = by[s["skill"]]; b["confidence"] = round(min(b["confidence"] + 0.08, 0.97), 2); b["method"] = "taxonomy + LLM"
        else: by[s["skill"]] = dict(s)
    return sorted(by.values(), key=lambda r: -r["confidence"])
