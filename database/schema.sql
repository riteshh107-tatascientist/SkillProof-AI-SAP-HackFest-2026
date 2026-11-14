CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, name TEXT NOT NULL,
  password_hash TEXT NOT NULL, role TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'active', must_change_password INTEGER DEFAULT 0,
  failed_attempts INTEGER DEFAULT 0, locked_until REAL DEFAULT 0, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS skills (
  id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL, category TEXT, synonyms TEXT, related TEXT);
CREATE TABLE IF NOT EXISTS candidates (
  id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER UNIQUE REFERENCES users(id), name TEXT, email TEXT,
  headline TEXT, education TEXT, certifications TEXT, summary TEXT, resume_text TEXT,
  is_synthetic INTEGER DEFAULT 0, created_at TEXT NOT NULL, updated_at TEXT);
CREATE TABLE IF NOT EXISTS candidate_skills (
  id INTEGER PRIMARY KEY AUTOINCREMENT, candidate_id INTEGER NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
  skill TEXT NOT NULL, category TEXT, confidence REAL, evidence TEXT, source TEXT, confirmed INTEGER DEFAULT 1,
  UNIQUE(candidate_id, skill));
CREATE TABLE IF NOT EXISTS jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, department TEXT, description TEXT,
  required_skills TEXT, preferred_skills TEXT, source TEXT DEFAULT 'sample', created_by INTEGER, created_at TEXT);
CREATE TABLE IF NOT EXISTS reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT, candidate_id INTEGER NOT NULL, job_id INTEGER NOT NULL, reviewer_id INTEGER NOT NULL,
  decision TEXT NOT NULL, notes TEXT NOT NULL, coverage REAL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS roadmap_progress (
  candidate_id INTEGER NOT NULL, task_key TEXT NOT NULL, done INTEGER DEFAULT 0, updated_at TEXT,
  PRIMARY KEY (candidate_id, task_key));
CREATE TABLE IF NOT EXISTS interview_attempts (
  id INTEGER PRIMARY KEY AUTOINCREMENT, candidate_id INTEGER NOT NULL, skill TEXT, question TEXT, answer TEXT,
  score REAL, feedback TEXT, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, user_id INTEGER, action TEXT NOT NULL, detail TEXT);
