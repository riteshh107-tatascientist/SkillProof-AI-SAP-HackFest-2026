# Responsible AI
1. AI never makes final hiring/rejection decisions; recruiters record a decision **and rationale**; everything is audit-logged.
2. Matching inputs = confirmed skills only. No name, gender, age, college or other protected attribute.
3. Candidate confirmation: suggestions are not facts. Self-declared skills require evidence text.
4. Blind comparison for recruiters; identity reveal needs a logged reason.
5. Fairness Lab uses demographics for **auditing only**, warns on small samples, and states disparity is a signal, not proof.
6. Privacy: PII redaction before external AI calls, consent toggles, no keys in code, bcrypt password hashes, upload validation (type, size, magic bytes), parameterised SQL, session timeout, login lockout.
7. Honesty: sample/synthetic data labelled everywhere; no fabricated metrics; Demo mode never claims to be a live LLM; SAP integrations labelled proposed.
8. Known risks: taxonomy bias toward tech skills, synonym gaps, over-reliance on scores. Mitigation: human review, evidence, periodic audits.

9. Access control: account required for everything; recruiter approval; role-based pages; admin actions audit-logged; last-admin protection; right to export/erase own data.
10. LLM extraction is constrained: taxonomy-only skill names, verbatim evidence required, PII redacted, user consent required, human confirmation always.
