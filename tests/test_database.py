import pytest
import config
from database import db, seed


@pytest.fixture()
def fresh(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "t.db"); db.init_db(); return db


def test_register_login_lockout(fresh):
    uid, err = db.create_user("a@b.com", "Ann", "Abcdef12", "candidate"); assert uid and not err
    assert db.create_user("a@b.com", "Ann", "Abcdef12", "candidate")[0] is None
    assert db.query("SELECT password_hash FROM users")[0]["password_hash"].startswith("$2")
    assert db.authenticate("a@b.com", "Abcdef12")[0]["role"] == "candidate"
    for _ in range(5): db.authenticate("a@b.com", "wrong")
    user, msg = db.authenticate("a@b.com", "Abcdef12"); assert user is None and "too many" in msg.lower()


def test_seed_and_flow(fresh):
    seed.seed_all(); seed.seed_all()
    s = db.stats(); assert s["skills"] >= 50 and s["jobs"] == 12 and s["synthetic"] == 40 and s["evidence"] > 100
    cand = db.get_candidate_by_user(db.query("SELECT id FROM users WHERE role='candidate'")[0]["id"]); assert cand
    db.save_skills(cand["id"], [dict(skill="Python", category="Programming", confidence=.9, evidence="x", source="resume")]); assert len(db.get_skills(cand["id"])) == 1
    db.set_progress(cand["id"], "k", True); assert "k" in db.get_progress(cand["id"])
    rid = db.query("SELECT id FROM users WHERE role='recruiter'")[0]["id"]; db.add_review(cand["id"], 1, rid, "Hold for later", "notes here ok", 50.0); assert len(db.list_reviews()) == 1
    assert db.recent_audit()
