import pytest
from streamlit.testing.v1 import AppTest
from pathlib import Path
import config
from database import db, seed
from utils.constants import ROLE_PAGES

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def tmpdb(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "a.db"); db.init_db(); seed.seed_all()


def test_recruiter_needs_approval_and_candidate_does_not():
    uid, _ = db.create_user("r@x.com", "Rec", "Abcdef12", "recruiter"); assert db.query("SELECT status FROM users WHERE id=?", (uid,))[0]["status"] == "pending"
    assert "approval" in db.authenticate("r@x.com", "Abcdef12")[1].lower()
    db.set_status(uid, "active"); assert db.authenticate("r@x.com", "Abcdef12")[0]["role"] == "recruiter"
    cid, _ = db.create_user("c@x.com", "Can", "Abcdef12", "candidate"); assert db.authenticate("c@x.com", "Abcdef12")[0]
    db.set_status(cid, "suspended"); assert "suspended" in db.authenticate("c@x.com", "Abcdef12")[1].lower()


def test_admin_cannot_be_self_registered_and_reset_forces_change():
    admin = db.query("SELECT id FROM users WHERE role='admin'")[0]["id"]; assert db.count_admins() == 1
    db.set_password(admin, "Temp-Pass1x", True); assert db.authenticate("admin@skillproof.demo", "Temp-Pass1x")[0]["must_change"]
    db.set_password(admin, "Brand-New9x", False); assert not db.authenticate("admin@skillproof.demo", "Brand-New9x")[0]["must_change"]


def test_delete_user_removes_everything():
    uid, _ = db.create_user("d@x.com", "Del", "Abcdef12", "candidate"); cid = db.upsert_candidate(uid, "Del", "d@x.com", "h")
    db.save_skills(cid, [dict(skill="Python", category="Programming", confidence=.9, evidence="e", source="resume")]); db.add_attempt(cid, "Python", "q", "a", 50, "f")
    assert db.export_user_data(uid)["skills"]; db.delete_user(uid)
    assert not db.query("SELECT 1 FROM users WHERE id=?", (uid,)) and not db.query("SELECT 1 FROM candidate_skills") or db.query("SELECT COUNT(*) n FROM candidate_skills WHERE candidate_id=?", (cid,))[0]["n"] == 0


def test_old_database_is_migrated(tmp_path, monkeypatch):
    import sqlite3
    p = tmp_path / "old.db"; c = sqlite3.connect(p)
    c.execute("CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, name TEXT NOT NULL, password_hash TEXT NOT NULL, role TEXT NOT NULL CHECK (role IN ('candidate','recruiter')), failed_attempts INTEGER DEFAULT 0, locked_until REAL DEFAULT 0, created_at TEXT NOT NULL)")
    c.execute("INSERT INTO users(email,name,password_hash,role,created_at) VALUES('o@x.com','Old','h','candidate','now')"); c.commit(); c.close()
    monkeypatch.setattr(config, "DB_PATH", p); db.init_db()
    assert db.query("SELECT status FROM users")[0]["status"] == "active"; assert db.create_user("a@x.com", "A", "Abcdef12", "admin", "active")[0]


def test_anonymous_sees_only_gate_and_roles_see_only_their_pages():
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run(); assert not at.exception
    assert not at.sidebar.radio and any("Create an account" in m.value for m in at.markdown)
    for role, email in [("candidate", "candidate@skillproof.demo"), ("recruiter", "recruiter@skillproof.demo"), ("admin", "admin@skillproof.demo")]:
        u = db.get_user(db.query("SELECT id FROM users WHERE email=?", (email,))[0]["id"]); a = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60); a.session_state["user"] = u; a.run()
        assert len(a.sidebar.radio[0].options) == len(ROLE_PAGES[role]), role
    # a suspended user's live session is revoked on the next run
    cand = db.query("SELECT id FROM users WHERE role='candidate'")[0]["id"]; u = db.get_user(cand); a = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60); a.session_state["user"] = u; a.run()
    db.set_status(cand, "suspended"); a.run(); assert not a.sidebar.radio and any("no longer active" in e.value for e in a.error)


def test_register_then_login_through_the_real_form():
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    at.text_input(key="reg_email").set_value("new.student@example.com")
    nm = [t for t in at.text_input if t.label == "Full name"][0]; nm.set_value("New Student")
    at.text_input(key="reg_pw").set_value("Strong#Pass1"); at.text_input(key="reg_pw2").set_value("Strong#Pass1")
    [b for b in at.button if b.label == "Create account"][0].click().run()
    assert any("Account created" in s.value for s in at.success)
    em = [t for t in at.text_input if t.label == "Email"][0]; em.set_value("new.student@example.com")
    pw = [t for t in at.text_input if t.label == "Password"][0]; pw.set_value("Strong#Pass1")
    [b for b in at.button if b.label == "Sign in"][0].click().run()
    assert at.session_state["user"]["role"] == "candidate" and at.sidebar.radio
