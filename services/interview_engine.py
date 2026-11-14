"""Question generation + transparent heuristic answer scoring (optionally enriched by an LLM)."""
import random, re
from models.skill_model import get_taxonomy

BEHAVIOURAL = [
    ("Tell me about a time you learned a new skill quickly to finish a project.", ["learn", "result", "challenge", "outcome", "project"]),
    ("Describe a disagreement in a team and how you resolved it.", ["team", "listen", "resolve", "outcome", "communicat"]),
    ("Tell me about a project that failed or went wrong. What did you change afterwards?", ["mistake", "learn", "fix", "improv", "result"]),
    ("How do you prioritise when you have several deadlines at once?", ["prior", "deadline", "plan", "communicat", "trade"]),
]
TECH = {
    "Python": [("Explain the difference between a list, tuple, set and dict, and when you would use each.", ["mutable", "hash", "order", "unique", "lookup"])],
    "SQL": [("Explain INNER vs LEFT JOIN and write a query for the top 3 customers by revenue.", ["join", "null", "group by", "order by", "limit"])],
    "Machine Learning": [("How do you detect and reduce overfitting?", ["validation", "regulari", "cross", "train", "test"])],
    "Statistics": [("What does a p-value mean, and what does it NOT mean?", ["null", "probability", "hypothesis", "significan", "effect"])],
    "Git": [("Explain branching, merging and how you would resolve a merge conflict.", ["branch", "merge", "conflict", "commit", "pull"])],
    "REST API": [("What makes an API RESTful? Explain status codes you would return for create, not-found and invalid input.", ["get", "post", "201", "404", "400", "stateless"])],
}
GENERIC = ["Explain {s} in simple terms and describe a project where you used it.", "What trade-offs or common mistakes come up when working with {s}?", "How would you test or validate work done with {s}?"]


def generate_questions(skills, kind="Mixed", n=5, seed=None):
    tax, rnd, qs = get_taxonomy(), random.Random(seed), []
    if kind in ("Technical", "Mixed"):
        for s in skills:
            if s in TECH: q, kw = TECH[s][0]
            else:
                q = rnd.choice(GENERIC).format(s=s); kw = [s.lower()] + [r.lower() for r in tax.neighbors(s)][:4] + ["example", "project"]
            qs.append({"skill": s, "type": "Technical", "question": q, "keywords": kw})
    if kind in ("Behavioural", "Mixed"):
        for q, kw in BEHAVIOURAL: qs.append({"skill": "Behavioural", "type": "Behavioural", "question": q, "keywords": kw})
    rnd.shuffle(qs)
    return qs[:n]


def score_answer(answer: str, keywords, qtype="Technical"):
    """Heuristic only: keyword coverage 50%, structure 25%, specificity 25%. Returns (score 0-100, feedback list)."""
    a = (answer or "").strip(); low = a.lower(); words = len(a.split())
    if words < 15: return 10.0, ["Answer is very short. Aim for 80-200 words with a concrete example."]
    kw = sum(1 for k in keywords if k in low) / max(len(keywords), 1)
    star = sum(1 for k in ["situation", "task", "action", "result", "because", "so that", "therefore"] if k in low)
    struct = min(star / 3, 1) if qtype == "Behavioural" else min(len(re.findall(r"\b(first|then|because|for example|e\.g\.|however|trade-?off)\b", low)) / 3, 1)
    spec = min((len(re.findall(r"\d", a)) > 0) * 0.5 + (words >= 70) * 0.5, 1)
    score = round(100 * (0.5 * kw + 0.25 * struct + 0.25 * spec), 1)
    fb = []
    if kw < 0.6: fb.append(f"Cover more key ideas ({kw:.0%} of expected concepts found).")
    if struct < 0.67: fb.append("Add structure: for behavioural use Situation-Task-Action-Result; for technical give reasoning and trade-offs.")
    if spec < 1: fb.append("Add a concrete example with numbers or outcomes, and aim for 70+ words.")
    return score, fb or ["Strong, well-structured answer. Practise delivering it in under two minutes."]
