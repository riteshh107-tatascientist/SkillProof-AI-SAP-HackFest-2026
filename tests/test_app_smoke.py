"""Boots the real Streamlit app headlessly and visits every page as guest, candidate and recruiter."""
import pytest
from pathlib import Path
from streamlit.testing.v1 import AppTest
import config
from database import db, seed
from utils.constants import NAV, ROLE_PAGES

LABELS = {r: [f"{i}  {n}" for n, i, _ in NAV if n in pages] for r, pages in ROLE_PAGES.items()}


@pytest.fixture(autouse=True)
def tmpdb(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "s.db"); db.init_db(); seed.seed_all()


def run(user=None, nav=None):
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=60)
    if user: at.session_state["user"] = user
    if nav: at.session_state["nav"] = nav
    return at.run()


def test_every_page_renders_for_each_role():
    run()  # boots + seeds
    users = {"candidate": db.query("SELECT id,email,name,role FROM users WHERE role='candidate'")[0], "recruiter": db.query("SELECT id,email,name,role FROM users WHERE role='recruiter'")[0], "admin": db.query("SELECT id,email,name,role FROM users WHERE role='admin'")[0]}
    for who, u in users.items():
        u = db.get_user(u["id"])
        for label in LABELS[who]:
            at = run(u, label); assert not at.exception, f"{who} / {label}: {at.exception}"; assert not at.error or all("went wrong" not in e.value for e in at.error), f"{who} / {label}"
