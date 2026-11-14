"""End-to-end demo story executed through the real services and UI (Demo AI mode, no network)."""
from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest
import config
from database import db, seed
from services.interview_engine import generate_questions, score_answer
from services.matching_engine import match, report_df
from services.recommendation_engine import build_roadmap, roadmap_rows
from services.resume_parser import analyze_quality, extract_text
from services.skill_extractor import extract_skills
from utils.validators import validate_upload

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def tmpdb(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "e.db"); db.init_db(); seed.seed_all()


def test_candidate_to_recruiter_story():
    text, err = extract_text("cv.txt", (ROOT / "data/sample_resume.txt").read_bytes()); assert not err and validate_upload("cv.txt", b"x")[0]
    q = analyze_quality(text); assert 0 < q["total"] <= 100
    sk = extract_skills(text); assert {"Python", "Pandas", "SQL", "Streamlit"} <= {s["skill"] for s in sk}
    cand = db.get_candidate_by_user(db.query("SELECT id FROM users WHERE role='candidate'")[0]["id"])
    db.save_skills(cand["id"], [dict(s, source="resume") for s in sk if s["confidence"] >= .7]); have = {s["skill"] for s in db.get_skills(cand["id"])}
    job = next(j for j in db.get_jobs() if j["title"] == "Data Analyst"); res = match(have, job, text)
    assert res["score"] > 0 and not report_df(res).empty
    plan = build_roadmap(res, job, have); assert set(plan) == {30, 60, 90} and not roadmap_rows(plan, job["title"]).empty
    qs = generate_questions(["SQL", "Python"], "Mixed", 4, seed=1); assert qs
    sc, fb = score_answer("First I would use an INNER JOIN because I need matching rows, then GROUP BY customer and ORDER BY revenue with LIMIT 3. For example in my project I cut query time by 40% and handled NULL values with a LEFT JOIN when needed.", ["join", "group by", "order by", "limit", "null"]); assert sc > 50
    rid = db.query("SELECT id FROM users WHERE role='recruiter'")[0]["id"]; db.add_review(cand["id"], job["id"], rid, "Advance to interview", "Evidence supports interview.", res["score"]); assert len(db.list_reviews()) == 1


def test_ui_resume_analyzer_and_assistant_demo():
    cand = db.query("SELECT id,email,name,role FROM users WHERE role='candidate'")[0]
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60); at.session_state["user"] = cand; at.session_state["nav"] = "📄  Resume Analyzer"; at.run()
    next(b for b in at.button if b.key == "ra_sample").click().run()
    next(b for b in at.button if b.label.startswith("🚀")).click().run()
    assert not at.exception and any("Resume quality" in m.value for m in at.markdown)
    at2 = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60); at2.session_state["user"] = cand; at2.session_state["nav"] = "🤖  AI Assistant"; at2.session_state["ai_provider"] = "Demo"; at2.run()
    at2.chat_input[0].set_value("What is SQL and how do I learn it?").run()
    assert not at2.exception and any("SQL" in m.value for m in at2.chat_message[-1].markdown)
