"""Idempotent seeding: taxonomy, sample roles, demo accounts, synthetic demo candidates."""
from config import get_secret
from database import db
from utils.helpers import load_csv, split_pipe

DEMO_PW_DEFAULT = "Demo@12345"  # demo-only credential; override with DEMO_PASSWORD in secrets/.env


def seed_all():
    if not db.query("SELECT 1 FROM skills LIMIT 1"):
        for r in load_csv("skills.csv").fillna("").itertuples(): db.add_skill_record(r.skill, r.category, r.synonyms, r.related)
    if not db.query("SELECT 1 FROM jobs LIMIT 1"):
        for r in load_csv("jobs.csv").itertuples():
            db.add_job(r.title, r.department, r.description, split_pipe(r.required_skills), split_pipe(r.preferred_skills), None, "sample")
    pw = get_secret("DEMO_PASSWORD", DEMO_PW_DEFAULT)
    for email, name, role in [("candidate@skillproof.demo", "Demo Candidate", "candidate"), ("recruiter@skillproof.demo", "Demo Recruiter", "recruiter")]:
        if not db.query("SELECT 1 FROM users WHERE email=?", (email,)):
            uid, _ = db.create_user(email, name, pw, role, status="active")
            if role == "candidate": db.upsert_candidate(uid, name, email, headline="Aspiring Data Professional")
    # Admin: set ADMIN_EMAIL + ADMIN_PASSWORD in Streamlit secrets for real use; otherwise a demo-only admin is created.
    a_email, a_pw = get_secret("ADMIN_EMAIL").strip().lower(), get_secret("ADMIN_PASSWORD")
    if a_email and a_pw:
        if not db.query("SELECT 1 FROM users WHERE email=?", (a_email,)): db.create_user(a_email, "Administrator", a_pw, "admin", status="active")
    elif not db.query("SELECT 1 FROM users WHERE role='admin'"):
        db.create_user("admin@skillproof.demo", "Demo Admin", pw, "admin", status="active")
    if not db.query("SELECT 1 FROM candidates WHERE is_synthetic=1 LIMIT 1"):
        from services.skill_extractor import extract_skills
        for r in load_csv("candidates.csv").itertuples():
            cid = db.upsert_candidate(None, r.name, f"{r.candidate_id.lower()}@synthetic.demo", r.headline, r.education, "", "Synthetic demo candidate.", 1, r.resume_text)
            db.save_skills(cid, [dict(s, source="synthetic-seed") for s in extract_skills(r.resume_text)])
