"""SQLite access layer. Parameterised queries only (no string-built SQL)."""
import sqlite3, time
from contextlib import contextmanager
from pathlib import Path
import pandas as pd
import config
from utils.helpers import now_iso
from utils.security import hash_password, verify_password

SCHEMA = Path(__file__).with_name("schema.sql")


@contextmanager
def conn():
    Path(config.DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(config.DB_PATH, timeout=10)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    try:
        yield c; c.commit()
    except Exception:
        c.rollback(); raise
    finally:
        c.close()


def _migrate():
    """Upgrade databases created by older versions (role CHECK, missing status columns)."""
    if not Path(config.DB_PATH).exists(): return
    c = sqlite3.connect(config.DB_PATH)
    try:
        row = c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'").fetchone()
        if not row: return
        if "CHECK" in row[0].upper():
            c.executescript("""PRAGMA foreign_keys=OFF; BEGIN;
              CREATE TABLE users_new (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, name TEXT NOT NULL, password_hash TEXT NOT NULL, role TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active', must_change_password INTEGER DEFAULT 0, failed_attempts INTEGER DEFAULT 0, locked_until REAL DEFAULT 0, created_at TEXT NOT NULL);
              INSERT INTO users_new(id,email,name,password_hash,role,failed_attempts,locked_until,created_at) SELECT id,email,name,password_hash,role,failed_attempts,locked_until,created_at FROM users;
              DROP TABLE users; ALTER TABLE users_new RENAME TO users; COMMIT; PRAGMA foreign_keys=ON;""")
        cols = {r[1] for r in c.execute("PRAGMA table_info(users)")}
        if "status" not in cols: c.execute("ALTER TABLE users ADD COLUMN status TEXT NOT NULL DEFAULT 'active'")
        if "must_change_password" not in cols: c.execute("ALTER TABLE users ADD COLUMN must_change_password INTEGER DEFAULT 0")
        c.commit()
    finally:
        c.close()


def init_db():
    _migrate()
    with conn() as c: c.executescript(SCHEMA.read_text(encoding="utf-8"))


def query(sql, params=()):
    with conn() as c: return [dict(r) for r in c.execute(sql, params).fetchall()]


def execute(sql, params=()):
    with conn() as c: return c.execute(sql, params).lastrowid


def query_df(sql, params=()):
    return pd.DataFrame(query(sql, params))


# ---- audit
def log_action(user_id, action, detail=""):
    execute("INSERT INTO audit_log(ts,user_id,action,detail) VALUES(?,?,?,?)", (now_iso(), user_id, action, str(detail)[:500]))


def recent_audit(limit=50):
    return query("SELECT a.ts, COALESCE(u.name,'system') AS actor, a.action, a.detail FROM audit_log a LEFT JOIN users u ON u.id=a.user_id ORDER BY a.id DESC LIMIT ?", (limit,))


# ---- users
ROLES = ("candidate", "recruiter", "admin")


def _public(u):
    return {"id": u["id"], "email": u["email"], "name": u["name"], "role": u["role"], "status": u["status"], "must_change": bool(u["must_change_password"])}


def create_user(email, name, password, role="candidate", status=None, must_change=0):
    """Self-registered candidates are active at once; recruiters wait for admin approval. Admins are never self-registered."""
    if role not in ROLES: return None, "Invalid role."
    status = status or ("pending" if role == "recruiter" else "active")
    try:
        uid = execute("INSERT INTO users(email,name,password_hash,role,status,must_change_password,created_at) VALUES(?,?,?,?,?,?,?)",
                      (email.strip().lower(), name.strip(), hash_password(password), role, status, int(must_change), now_iso()))
    except sqlite3.IntegrityError:
        return None, "An account with this email already exists."
    log_action(uid, "register", f"{role}/{status}")
    return uid, ""


def authenticate(email, password):
    rows = query("SELECT * FROM users WHERE email=?", ((email or "").strip().lower(),))
    if not rows: return None, "Invalid email or password."
    u = rows[0]
    if u["locked_until"] and u["locked_until"] > time.time():
        return None, "Too many failed attempts. Try again in a few minutes."
    if not verify_password(password, u["password_hash"]):
        fails = u["failed_attempts"] + 1
        execute("UPDATE users SET failed_attempts=?, locked_until=? WHERE id=?", (fails, time.time() + 300 if fails >= 5 else 0, u["id"]))
        log_action(u["id"], "login_failed", f"attempt {fails}")
        return None, "Invalid email or password."
    if u["status"] == "pending": return None, "Your recruiter account is waiting for admin approval."
    if u["status"] == "suspended": return None, "This account has been suspended. Contact an administrator."
    execute("UPDATE users SET failed_attempts=0, locked_until=0 WHERE id=?", (u["id"],))
    log_action(u["id"], "login", u["role"])
    return _public(u), ""


def get_user(uid):
    r = query("SELECT * FROM users WHERE id=?", (uid,)); return _public(r[0]) if r else None


def list_users():
    return query_df("SELECT id, name, email, role, status, must_change_password AS must_change, created_at FROM users ORDER BY id")


def count_admins():
    return query("SELECT COUNT(*) n FROM users WHERE role='admin' AND status='active'")[0]["n"]


def set_status(uid, status, actor=None):
    execute("UPDATE users SET status=? WHERE id=?", (status, uid)); log_action(actor, "user_status", f"user={uid} -> {status}")


def set_role(uid, role, actor=None):
    if role not in ROLES: return
    execute("UPDATE users SET role=? WHERE id=?", (role, uid)); log_action(actor, "user_role", f"user={uid} -> {role}")


def set_password(uid, password, must_change=False, actor=None):
    execute("UPDATE users SET password_hash=?, must_change_password=?, failed_attempts=0, locked_until=0 WHERE id=?", (hash_password(password), int(must_change), uid))
    log_action(actor or uid, "password_changed" if not must_change else "password_reset", f"user={uid}")


def verify_user_password(uid, password):
    r = query("SELECT password_hash FROM users WHERE id=?", (uid,)); return bool(r) and verify_password(password, r[0]["password_hash"])


def export_user_data(uid):
    u = get_user(uid); out = {"account": u, "candidate": None, "skills": [], "interview_attempts": [], "roadmap_progress": []}
    c = get_candidate_by_user(uid)
    if c:
        out["candidate"] = c; out["skills"] = get_skills(c["id"])
        out["interview_attempts"] = query("SELECT created_at,skill,question,answer,score,feedback FROM interview_attempts WHERE candidate_id=?", (c["id"],))
        out["roadmap_progress"] = query("SELECT task_key,done,updated_at FROM roadmap_progress WHERE candidate_id=?", (c["id"],))
    return out


def delete_user(uid, actor=None):
    """Removes the account and every record tied to it (right to erasure). Audit entries are kept, de-linked."""
    c = get_candidate_by_user(uid)
    with conn() as k:
        if c:
            for t in ("interview_attempts", "roadmap_progress", "reviews", "candidate_skills"): k.execute(f"DELETE FROM {t} WHERE candidate_id=?", (c["id"],))
            k.execute("DELETE FROM candidates WHERE id=?", (c["id"],))
        k.execute("UPDATE audit_log SET user_id=NULL WHERE user_id=?", (uid,)); k.execute("UPDATE jobs SET created_by=NULL WHERE created_by=?", (uid,))
        k.execute("DELETE FROM reviews WHERE reviewer_id=?", (uid,)); k.execute("DELETE FROM users WHERE id=?", (uid,))
    log_action(actor, "user_deleted", f"user={uid}")


# ---- candidates
def get_candidate_by_user(user_id):
    r = query("SELECT * FROM candidates WHERE user_id=?", (user_id,)); return r[0] if r else None


def get_candidate(cid):
    r = query("SELECT * FROM candidates WHERE id=?", (cid,)); return r[0] if r else None


def list_candidates(include_synthetic=True):
    sql = "SELECT * FROM candidates" + ("" if include_synthetic else " WHERE is_synthetic=0") + " ORDER BY id"
    return query(sql)


def upsert_candidate(user_id, name, email, headline="", education="", certifications="", summary="", is_synthetic=0, resume_text=None):
    ex = get_candidate_by_user(user_id) if user_id else None
    if ex:
        execute("UPDATE candidates SET name=?,email=?,headline=?,education=?,certifications=?,summary=?,updated_at=? WHERE id=?",
                (name, email, headline, education, certifications, summary, now_iso(), ex["id"]))
        return ex["id"]
    return execute("INSERT INTO candidates(user_id,name,email,headline,education,certifications,summary,resume_text,is_synthetic,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                   (user_id, name, email, headline, education, certifications, summary, resume_text, is_synthetic, now_iso(), now_iso()))


def update_resume(cid, text):
    execute("UPDATE candidates SET resume_text=?, updated_at=? WHERE id=?", (text, now_iso(), cid))


def save_skills(cid, rows):
    """Replace a candidate's skill records. rows: dicts with skill, category, confidence, evidence, source."""
    with conn() as c:
        c.execute("DELETE FROM candidate_skills WHERE candidate_id=?", (cid,))
        c.executemany("INSERT OR REPLACE INTO candidate_skills(candidate_id,skill,category,confidence,evidence,source,confirmed) VALUES(?,?,?,?,?,?,1)",
                      [(cid, r["skill"], r.get("category"), r.get("confidence"), str(r.get("evidence", ""))[:600], r.get("source", "resume")) for r in rows])


def get_skills(cid):
    return query("SELECT * FROM candidate_skills WHERE candidate_id=? AND confirmed=1 ORDER BY category, skill", (cid,))


# ---- skills & jobs
def add_skill_record(name, category, synonyms, related):
    execute("INSERT OR IGNORE INTO skills(name,category,synonyms,related) VALUES(?,?,?,?)", (name, category, synonyms, related))


def get_jobs():
    return query("SELECT * FROM jobs ORDER BY id")


def add_job(title, department, description, required, preferred, created_by=None, source="user"):
    return execute("INSERT INTO jobs(title,department,description,required_skills,preferred_skills,source,created_by,created_at) VALUES(?,?,?,?,?,?,?,?)",
                   (title, department, description, "|".join(required), "|".join(preferred), source, created_by, now_iso()))


# ---- reviews, progress, interviews
def add_review(cid, job_id, reviewer_id, decision, notes, coverage):
    rid = execute("INSERT INTO reviews(candidate_id,job_id,reviewer_id,decision,notes,coverage,created_at) VALUES(?,?,?,?,?,?,?)",
                  (cid, job_id, reviewer_id, decision, notes, coverage, now_iso()))
    log_action(reviewer_id, "human_review", f"cand={cid} job={job_id} decision={decision}")
    return rid


def list_reviews():
    return query_df("SELECT r.created_at, 'CAND-'||printf('%04d',r.candidate_id) AS candidate, j.title AS role, r.decision, r.coverage, r.notes, u.name AS reviewer "
                    "FROM reviews r JOIN jobs j ON j.id=r.job_id JOIN users u ON u.id=r.reviewer_id ORDER BY r.id DESC")


def set_progress(cid, key, done):
    execute("INSERT OR REPLACE INTO roadmap_progress(candidate_id,task_key,done,updated_at) VALUES(?,?,?,?)", (cid, key, int(done), now_iso()))


def get_progress(cid):
    return {r["task_key"] for r in query("SELECT task_key FROM roadmap_progress WHERE candidate_id=? AND done=1", (cid,))}


def add_attempt(cid, skill, question, answer, score, feedback):
    execute("INSERT INTO interview_attempts(candidate_id,skill,question,answer,score,feedback,created_at) VALUES(?,?,?,?,?,?,?)",
            (cid, skill, question, answer[:3000], score, feedback[:2000], now_iso()))


def list_attempts(cid):
    return query_df("SELECT created_at, skill, question, score FROM interview_attempts WHERE candidate_id=? ORDER BY id", (cid,))


def stats():
    q = lambda s: query(s)[0]["n"]
    return {"candidates": q("SELECT COUNT(*) n FROM candidates"), "synthetic": q("SELECT COUNT(*) n FROM candidates WHERE is_synthetic=1"),
            "jobs": q("SELECT COUNT(*) n FROM jobs"), "skills": q("SELECT COUNT(*) n FROM skills"),
            "evidence": q("SELECT COUNT(*) n FROM candidate_skills"), "reviews": q("SELECT COUNT(*) n FROM reviews")}
