"""Explainable candidate-to-role matching on CONFIRMED skills only. No name, gender, college or other protected attributes."""
import pandas as pd
from models.skill_model import get_taxonomy
from models.matching_model import coverage, weighted_score
from models import semantic_model
from utils.helpers import split_pipe


def match(have, job: dict, resume_text: str = ""):
    have, tax = set(have), get_taxonomy()
    req, pref = split_pipe(job["required_skills"]), split_pipe(job["preferred_skills"])
    rc, rm, rmiss = coverage(have, req)
    pc, pm, pmiss = coverage(have, pref)
    transferable = []
    for m in rmiss + pmiss:
        adj = sorted(tax.neighbors(m) & have)
        if adj: transferable.append({"missing": m, "via": adj, "reason": f"You already show {', '.join(adj)}, which is closely related to {m}.", "strength": "adjacent"})
        else:
            same = sorted(tax.same_category(m) & have)
            if len(same) >= 2: transferable.append({"missing": m, "via": same[:3], "reason": f"Experience in the same area ({tax.category[m]}) may transfer: {', '.join(same[:3])}.", "strength": "same-category"})
    score = weighted_score(rc, pc)
    explain = [f"Required skills covered: {len(rm)}/{len(req)} ({rc:.0%}) - weight 70%.", f"Preferred skills covered: {len(pm)}/{len(pref)} ({pc:.0%}) - weight 30%.",
               f"Skill coverage score = 0.7 x {rc:.2f} + 0.3 x {pc:.2f} = {score}%.", "Only candidate-confirmed skills are counted. Protected attributes are never inputs."]
    return {"job_id": job.get("id"), "role": job["title"], "score": score, "req_cov": rc, "pref_cov": pc, "matched_required": rm, "missing_required": rmiss,
            "matched_preferred": pm, "missing_preferred": pmiss, "transferable": transferable, "explain": explain,
            "text_similarity": round(semantic_model.similarity(resume_text, f"{job['title']} {job['description']} {' '.join(req + pref)}"), 3), "text_method": semantic_model.engine_name()}


def rank_jobs(have, jobs, resume_text=""):
    rows = [match(have, j, resume_text) for j in jobs]
    return pd.DataFrame([dict(role=r["role"], coverage_score=r["score"], required_covered=f"{len(r['matched_required'])}/{len(r['matched_required']) + len(r['missing_required'])}",
                              missing_required=", ".join(r["missing_required"]) or "-", text_similarity_baseline=r["text_similarity"]) for r in rows]).sort_values("coverage_score", ascending=False)


def report_df(res: dict) -> pd.DataFrame:
    rows = [dict(role=res["role"], type="matched-required", skill=s, note="") for s in res["matched_required"]]
    rows += [dict(role=res["role"], type="missing-required", skill=s, note="") for s in res["missing_required"]]
    rows += [dict(role=res["role"], type="matched-preferred", skill=s, note="") for s in res["matched_preferred"]]
    rows += [dict(role=res["role"], type="missing-preferred", skill=s, note="") for s in res["missing_preferred"]]
    rows += [dict(role=res["role"], type="transferable", skill=t["missing"], note=t["reason"]) for t in res["transferable"]]
    rows.append(dict(role=res["role"], type="summary", skill="skill_coverage_score", note=f"{res['score']}% (overlap measure, NOT a probability of being hired)"))
    return pd.DataFrame(rows)
