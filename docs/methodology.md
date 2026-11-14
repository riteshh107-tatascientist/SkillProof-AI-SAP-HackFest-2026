# Data-science methodology
- **Extraction:** taxonomy of 58 skills with synonyms; boundary-aware regex (so "Java" != "JavaScript"); ambiguous names (R, Excel) need explicit synonyms. Evidence = the sentences containing the match. "Evidence strength" = heuristic from mention count and action-verb context - **not a probability**.
- **Matching:** coverage = matched/required and matched/preferred; score = 0.7 x required + 0.3 x preferred. Transferable skills = taxonomy-graph neighbours (adjacent) or same-category skills. TF-IDF cosine reported separately as a baseline.
- **Fairness:** selection rate per group, impact ratio vs best group (four-fifths guide), Fisher exact (2x2) or chi-square, sample-size warnings (n<30 or <5 selected), skill-stratified rates.
- **Resume quality:** 8-item weighted checklist (sections, contacts, links, quantified results, action verbs, project evidence, length, certifications).
- **Evaluation:** precision/recall/F1 of the extractor vs labels of 40 SYNTHETIC resumes (includes deliberate "curious about X" distractors). This validates the pipeline only; real-world accuracy is unknown until labelled real resumes are used.
- **Limitations:** small taxonomy, no skill-depth measurement, weights not learned from outcomes, synthetic data.
