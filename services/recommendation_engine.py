"""Turns a match result into a 30/60/90-day learning roadmap with resources and projects."""
from models.skill_model import get_taxonomy
from utils.helpers import load_csv


def _resource(skill, res):
    r = res[res.skill == skill]
    if len(r): x = r.iloc[0]; return {"title": x.title, "provider": x.provider, "type": x.type, "hours": int(x.hours), "url": x.url if isinstance(x.url, str) else ""}
    return {"title": f"Official documentation + one mini-project for {skill}", "provider": "self-directed", "type": "Practice", "hours": 6, "url": ""}


def build_roadmap(result: dict, job: dict, have: set):
    tax, res = get_taxonomy(), load_csv("learning_resources.csv")
    ranked = lambda L: sorted(L, key=lambda s: (-len(tax.neighbors(s) & set(have)), s))  # easiest (most adjacent) first
    todo = ranked(result["missing_required"]) + ranked(result["missing_preferred"])
    n = len(todo); cut1, cut2 = -(-n // 3), -(-2 * n // 3)
    chunks = {30: todo[:cut1], 60: todo[cut1:cut2], 90: todo[cut2:]}
    focus = list(have & set(result["matched_required"]))[:2] or [job["title"]]
    plan = {}
    for d, skills in chunks.items():
        tasks = [{"skill": s, "task": f"Learn and practise {s}", "resource": _resource(s, res), "priority": "Required" if s in result["missing_required"] else "Preferred"} for s in skills]
        names = ", ".join(skills[:3]) or "your strongest skills"
        proj = {30: f"Mini-project: a small demo that uses {names}.", 60: f"Portfolio project: build a {job['title']} style project combining {names} with {focus[0]}; publish on GitHub with README and tests.",
                90: f"Capstone: end-to-end project for a {job['title']} scenario; write a 1-page case study with measurable outcomes."}[d]
        extra = {30: "Rewrite resume bullets with measurable outcomes.", 60: "Do 3 mock technical interviews in Interview Prep.", 90: "Apply to 5 roles; request a mentor review of your portfolio."}[d]
        plan[d] = {"tasks": tasks, "project": proj, "habit": extra}
    return plan


def roadmap_rows(plan, role):
    import pandas as pd
    rows = []
    for d, p in plan.items():
        for t in p["tasks"]: rows.append(dict(role=role, phase=f"{d}-day", item=t["task"], priority=t["priority"], resource=t["resource"]["title"], hours=t["resource"]["hours"], link=t["resource"]["url"]))
        rows.append(dict(role=role, phase=f"{d}-day", item=p["project"], priority="Project", resource="", hours="", link=""))
    return pd.DataFrame(rows)
