# Architecture
Layers: **pages/** (Streamlit UI, one `render()` each) -> **services/** (extraction, matching, fairness, roadmap, interview, AI providers) -> **models/** (taxonomy graph, TF-IDF maths, evaluation) -> **database/** (SQLite, parameterised queries). **components/** and **utils/** hold shared UI, styling, validation and security code. `app.py` boots the DB, enforces session timeout and routes pages via `st.navigation` (hidden) + a custom dark sidebar.

Data flow: resume -> `resume_parser` (text, sections, quality checklist) -> `skill_extractor` (suggestions + evidence) -> **candidate confirms** -> `candidate_skills` -> `matching_engine` (coverage, transferable via graph) -> `recommendation_engine` (30/60/90 roadmap) -> recruiter blind review -> human decision + `audit_log`.

AI: `ai_provider.generate(provider, system, messages)` is the only entry point; Gemini/OpenAI use REST with graceful errors (missing key, 429, timeout, network, bad model); Demo is a rule-based answerer.

Proposed (NOT implemented): SAP SuccessFactors (roles/talent profiles), SAP BTP (hosting, identity, Postgres), SAP Analytics Cloud (dashboards), SAP Business AI / Joule (in-flow assistant). See `assets/architecture.svg`.
