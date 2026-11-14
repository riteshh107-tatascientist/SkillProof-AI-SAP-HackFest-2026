"""Taxonomy-based skill extraction with evidence. Output = SUGGESTIONS the candidate must confirm."""
import re
from models.skill_model import get_taxonomy

PROJECT_VERBS = re.compile(r"\b(built|developed|implemented|designed|deployed|automated|created|led|integrated|analy[sz]ed|trained|optimi[sz]ed|tested|presented|mentored)\b", re.I)


def _sentences(text: str):
    parts = re.split(r"(?<=[.!?])\s+|\n+|[•▪]", text)
    return [p.strip(" -*\t") for p in parts if p and len(p.strip()) > 2]


def extract_skills(text: str, max_evidence: int = 2, semantic: bool = False):
    tax, sents, out = get_taxonomy(), _sentences(text or ""), []
    for skill, pat in tax.patterns.items():
        hits = [s for s in sents if pat.search(s)]
        if not hits: continue
        mentions = sum(len(pat.findall(s)) for s in hits)
        in_action = any(PROJECT_VERBS.search(s) for s in hits)
        in_list = any(s.count(",") >= 2 for s in hits)
        strength = min(0.50 + 0.08 * min(mentions, 3) + (0.20 if in_action else 0) + (0.07 if in_list else 0), 0.95)
        hits.sort(key=lambda s: (not PROJECT_VERBS.search(s), -len(s)))
        out.append({"skill": skill, "category": tax.category[skill], "confidence": round(strength, 2), "mentions": mentions,
                    "evidence": " | ".join(h[:220] for h in hits[:max_evidence]), "method": "taxonomy-match"})
    if semantic:  # pretrained embeddings: weak, clearly-labelled suggestions for skills implied but not named
        from models import semantic_model
        have = {r["skill"] for r in out}
        for sk, (sim, sent) in semantic_model.semantic_hits(sents, have).items():
            out.append({"skill": sk, "category": tax.category[sk], "confidence": round(min(sim, 0.65), 2), "mentions": 0, "evidence": sent[:220], "method": "semantic (embeddings)"})
    return sorted(out, key=lambda r: -r["confidence"])


def skills_in_text(text: str):
    return [r["skill"] for r in extract_skills(text)]
