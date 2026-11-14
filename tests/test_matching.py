from models.matching_model import coverage, weighted_score
from services.matching_engine import match, rank_jobs
from services.skill_extractor import extract_skills
from utils.helpers import load_csv


def test_coverage_math():
    c, m, miss = coverage({"A", "B"}, ["A", "B", "C", "D"]); assert c == 0.5 and m == ["A", "B"] and miss == ["C", "D"]
    assert weighted_score(1.0, 0.0) == 70.0 and weighted_score(1.0, 1.0) == 100.0 and coverage(set(), [])[0] == 1.0


def test_extraction_boundaries_and_evidence():
    names = {s["skill"]: s for s in extract_skills("Built a dashboard with JavaScript and numpy. Knows C++ and Node.js.")}
    assert "JavaScript" in names and "NumPy" in names and "Java" not in names and "C++" in names and "Node.js" in names
    assert names["JavaScript"]["evidence"]
    assert "R" not in names and "Excel" not in {s["skill"] for s in extract_skills("I excel in teamwork")}


def test_match_uses_only_skills_and_explains():
    job = load_csv("jobs.csv").iloc[0].to_dict(); job["id"] = 1; job["required_skills"] = job["required_skills"]; job["preferred_skills"] = job["preferred_skills"]
    r = match({"SQL", "Python", "Pandas"}, job, "sql python")
    assert 0 < r["score"] < 100 and r["missing_required"] and r["explain"]
    assert any(t["missing"] == "Data Analysis" for t in r["transferable"])


def test_rank_jobs_sorted():
    jobs = load_csv("jobs.csv").to_dict("records")
    df = rank_jobs({"Python", "SQL"}, jobs); assert df.coverage_score.is_monotonic_decreasing
