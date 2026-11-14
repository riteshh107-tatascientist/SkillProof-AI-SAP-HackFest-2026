"""Precision / recall / F1 for the skill extractor against LABELLED data. Never fabricates numbers."""
import pandas as pd
from services.skill_extractor import extract_skills
from utils.helpers import load_csv, split_pipe

CAVEAT = ("Labels come from the SYNTHETIC generator (data/generate_data.py), whose text is built from the same taxonomy. "
          "These scores validate the pipeline and show the effect of 'mentions-only' false positives; they are NOT a claim "
          "about accuracy on real-world resumes.")


def prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    return round(p, 3), round(r, 3), round(2 * p * r / (p + r), 3) if p + r else 0.0


def evaluate_extractor(df: pd.DataFrame = None):
    df = load_csv("candidates.csv") if df is None else df
    tp = fp = fn = 0
    per = {}
    for row in df.itertuples():
        truth, pred = set(split_pipe(row.true_skills)), {s["skill"] for s in extract_skills(row.resume_text)}
        for s in truth | pred:
            d = per.setdefault(s, [0, 0, 0])
            if s in truth and s in pred: tp += 1; d[0] += 1
            elif s in pred: fp += 1; d[1] += 1
            else: fn += 1; d[2] += 1
    p, r, f = prf(tp, fp, fn)
    rows = [dict(skill=s, support=v[0] + v[2], precision=prf(*v)[0], recall=prf(*v)[1], f1=prf(*v)[2]) for s, v in per.items()]
    return {"precision": p, "recall": r, "f1": f, "n_resumes": len(df), "tp": tp, "fp": fp, "fn": fn,
            "per_skill": pd.DataFrame(rows).sort_values("support", ascending=False), "caveat": CAVEAT}
