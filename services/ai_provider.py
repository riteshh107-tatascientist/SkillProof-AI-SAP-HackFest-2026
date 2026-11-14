"""Provider abstraction: Gemini | OpenAI | Demo. Callers never touch provider-specific code."""
from dataclasses import dataclass
import re
from config import DEFAULT_MODELS, get_secret
from models.skill_model import get_taxonomy
from services import gemini_service, openai_service
from utils.helpers import load_csv


@dataclass
class AIResult:
    ok: bool
    text: str = ""
    provider: str = ""
    model: str = ""
    error: str = ""
    live: bool = True


def available() -> dict:
    return {"Demo": True, "Gemini": bool(gemini_service.api_key()), "OpenAI": bool(openai_service.api_key())}


def model_for(provider: str, override: str = "") -> str:
    if provider == "Demo": return "rule-based"
    return override or get_secret(f"{provider.upper()}_MODEL", DEFAULT_MODELS[provider])


def demo_answer(question: str) -> str:
    tax, q = get_taxonomy(), question.lower()
    found = [s for s, p in tax.patterns.items() if p.search(question)][:3]
    res = load_csv("learning_resources.csv")
    out = []
    for s in found:
        rel = ", ".join(sorted(tax.neighbors(s))[:5]) or "n/a"
        out.append(f"**{s}** ({tax.category[s]}). Closely related skills: {rel}.")
        r = res[res.skill == s]
        if len(r): out.append(f"Free starting point: {r.iloc[0].title} - {r.iloc[0].url}")
        out.append(f"Interview tip: explain what {s} is, one project where you used it, one trade-off, and how you validated the result.")
    if re.search(r"resume|cv", q): out.append("**Resume tips:** use SKILLS / PROJECTS / EDUCATION headings, start bullets with action verbs, add numbers (%, users, time saved), link GitHub and name the tools in each project. Try the Resume Analyzer page for a scored checklist.")
    if re.search(r"interview|prepare|question", q): out.append("**Interview prep:** practise 3 technical and 2 behavioural questions per week in Interview Prep, and answer behavioural ones with Situation-Task-Action-Result.")
    if re.search(r"roadmap|plan|learn|gap|career", q): out.append("**Planning:** pick a target role in Job Matching, list missing required skills first, then follow the 30/60/90-day plan in Career Roadmap with one portfolio project per phase.")
    if not out: out.append("I'm in **Demo mode** (rule-based, no live LLM). Ask about a specific skill (e.g. 'What is SQL?'), your resume, interviews or a roadmap. Switch to Gemini or OpenAI in Account & Settings for open-ended answers.")
    return "\n\n".join(out)


def generate(provider: str, system: str, messages: list, model: str = "", max_tokens: int = 900) -> AIResult:
    """Single entry point. Always returns an AIResult; never raises."""
    try:
        if provider == "Demo":
            last = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
            return AIResult(True, demo_answer(last), "Demo", "rule-based", live=False)
        fn = {"Gemini": gemini_service.generate, "OpenAI": openai_service.generate}.get(provider)
        if not fn: return AIResult(False, provider=provider, error="Unknown provider.")
        text, err = fn(system, messages, model=model or None, max_tokens=max_tokens)
        return AIResult(not err, text, provider, model_for(provider, model), err)
    except Exception:
        return AIResult(False, provider=provider, error="Unexpected AI error. Please retry or switch provider.")


ASSISTANT_SYSTEM = ("You are SkillProof AI Career Assistant, helping students and job seekers with resumes, skills, career planning, interview preparation and learning guidance. "
                    "Be accurate, practical and concise; use short paragraphs or bullets; give concrete next steps. Admit uncertainty rather than guessing. "
                    "Never make or imply a hiring/rejection decision, never guess protected attributes, and never ask for personal identifiers. "
                    "Skill overlap is not a probability of being hired.")
