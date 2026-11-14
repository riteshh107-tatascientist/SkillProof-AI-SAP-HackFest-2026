# 🛡️ SkillProof AI
**Fair Skills. Inclusive Talent. Smarter Workforces.**
AI-powered, explainable, human-in-the-loop skills-based recruitment and workforce-development platform.
Built for **SAP HackFest 2026 - Theme 02: Inclusive Workforce**.

> Independent student project. Not developed, certified, sponsored or endorsed by SAP. All SAP integrations are *proposed designs only*.
> Built by Ritesh Kumar Singh - B.Tech CSE (Data Science), Technocrats Institute of Technology, Bhopal.

## Modules
Home (animated) · Candidate Studio · **Resume Analyzer** · Fair Job Matching · Career Roadmap (30/60/90) · Interview Prep · **AI Assistant (Gemini / OpenAI / Demo)** · Skill Analytics · Recruiter Hub (blind comparison, human approval, audit log) · Fairness & Responsible AI Lab · About & SAP architecture · Account & Settings.

## Access control (new)
No account, no access: visitors only see the sign-in / create-account screen. Candidates get instant access; **recruiter accounts stay pending until an admin approves them**. Admins are never self-registered.
Roles see only their pages (candidate / recruiter / admin). The **Admin Console** handles approvals, role changes, suspend/reactivate, temporary-password resets (user must change it at next sign-in), user deletion, platform health and the full audit log. Suspensions apply to live sessions on the next click. Users can change their password, download all their data (JSON) and delete their account.
Set a real admin in Streamlit secrets: `ADMIN_EMAIL`, `ADMIN_PASSWORD` (plus `DEMO_PASSWORD`, and `SHOW_DEMO_LOGINS = "false"` to hide the presentation demo buttons). Without them a demo-only admin `admin@skillproof.demo` is created with the demo password.

## AI models (beyond rules)
- **LLM extraction (Gemini/OpenAI):** in Candidate Studio, tick *Also use AI*. Every AI-suggested skill must be in the taxonomy and quote evidence that literally appears in the resume, otherwise it is discarded (anti-hallucination). Candidates still confirm each skill.
- **Pretrained embeddings (optional):** `pip install -r requirements-optional.txt` enables sentence-transformers (all-MiniLM-L6-v2) for semantic skill hints and semantic resume-to-role similarity; without it the app falls back to TF-IDF automatically. Turn off with `ENABLE_SEMANTIC = "off"`.
- Keys are read only from Streamlit secrets / environment; they are never typed into the app or chat.

## Run on Windows (PowerShell) / macOS / Linux
```powershell
cd SkillProof_AI
python -m venv .venv
.venv\Scripts\Activate.ps1          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env              # optional: add keys (or use .streamlit/secrets.toml)
streamlit run app.py
```
Python 3.10+. The database, sample roles, demo accounts and 40 synthetic candidates are created automatically on first run.

**Demo accounts** (buttons on *Account & Settings*): `candidate@skillproof.demo`, `recruiter@skillproof.demo` - demo password defaults to `Demo@12345`; override with `DEMO_PASSWORD` (this is a demo-only credential, change it for any public deployment).

## API keys (never commit them)
Local: put `GEMINI_API_KEY` / `OPENAI_API_KEY` in `.env` or `.streamlit/secrets.toml` (both git-ignored; see the `.example` files).
Streamlit Community Cloud: *App settings -> Secrets*, paste the same TOML. Optional `GEMINI_MODEL` / `OPENAI_MODEL`
(defaults `gemini-2.5-flash`, `gpt-4o-mini`; you can also type any model name in *Account & Settings* if a default is retired).
Pick the provider in *AI Assistant* or *Account & Settings*. With no key, **Demo mode** works and is labelled as rule-based, not a live LLM.

## Tests
```bash
python -m pytest -q tests      # 27 tests: validators, security, matching, fairness, DB + migration, access control and approvals, admin actions, AI provider errors, LLM-extractor guardrails, every page x 3 roles, e2e story
```
Re-generate assets/data: `python data/generate_data.py` and `python assets/generate_assets.py`.

## Deploy
Push to GitHub (keys stay out via `.gitignore`) -> share.streamlit.io -> select `app.py` -> add Secrets. SQLite on Streamlit Cloud is ephemeral (resets on restart): fine for demos; use PostgreSQL (e.g. on SAP BTP) for production.

## Honest limitations
Core extraction is a rule-based taxonomy (58 skills) with optional LLM/embedding layers (not benchmarked on real resumes); demo candidates and fairness data are **synthetic**; evaluation metrics are computed only on synthetic labelled data and are caveated in-app; no OCR for scanned PDFs; scores are decision support, never hiring decisions or hiring probabilities. See `docs/`.
