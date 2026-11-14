from services import ai_provider, llm_extractor
from services.skill_extractor import extract_skills

TEXT = "Built a churn model with scikit-learn and presented findings to managers. Wrote SQL reports weekly. Contact a@b.com"


def fake(text):
    return lambda *a, **k: ai_provider.AIResult(True, text, "Gemini", "m")


def test_llm_extraction_discards_hallucinated_or_unquoted(monkeypatch):
    js = ('```json\n[{"skill":"Machine Learning","evidence":"Built a churn model with scikit-learn"},'
          '{"skill":"Docker","evidence":"deployed with Docker on AWS"},{"skill":"Teamwork","evidence":"presented findings to managers"},'
          '{"skill":"NotASkill","evidence":"Wrote SQL reports weekly"},{"skill":"SQL","evidence":"x"}]\n```')
    monkeypatch.setattr(ai_provider, "generate", fake(js)); r = llm_extractor.llm_extract(TEXT, "Gemini")
    names = {s["skill"] for s in r["skills"]}
    assert r["ok"] and names == {"Machine Learning", "Teamwork"} and r["rejected"] == 3


def test_merge_and_errors(monkeypatch):
    base = extract_skills(TEXT); llm = [{"skill": "Machine Learning", "category": "Data & ML", "confidence": .75, "mentions": 1, "evidence": "e", "method": "LLM"}]
    m = {s["skill"]: s for s in llm_extractor.merge_suggestions(base, llm)}; assert m["Machine Learning"]["method"] == "LLM" or "LLM" in m["Machine Learning"]["method"]
    monkeypatch.setattr(ai_provider, "generate", lambda *a, **k: ai_provider.AIResult(False, error="Gemini quota/rate limit reached.")); r = llm_extractor.llm_extract(TEXT, "Gemini"); assert not r["ok"] and "quota" in r["error"]
    assert not llm_extractor.llm_extract(TEXT, "Demo")["ok"]
