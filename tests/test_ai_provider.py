import requests
from services import ai_provider, gemini_service, openai_service


def test_missing_keys_are_handled(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False); monkeypatch.delenv("OPENAI_API_KEY", raising=False); monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    for p in ("Gemini", "OpenAI"):
        r = ai_provider.generate(p, "sys", [{"role": "user", "content": "hi"}]); assert not r.ok and "key" in r.error.lower()


def test_demo_mode_is_labelled_not_live():
    r = ai_provider.generate("Demo", "sys", [{"role": "user", "content": "What is SQL?"}]); assert r.ok and not r.live and "SQL" in r.text


def test_error_mapping(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "k"); monkeypatch.setenv("GEMINI_API_KEY", "k")
    class R:
        def __init__(s, c): s.status_code = c; s.text = ""
        def json(s): return {}
    monkeypatch.setattr(requests, "post", lambda *a, **k: R(429))
    assert "quota" in openai_service.generate("s", [{"role": "user", "content": "x"}])[1].lower()
    assert "quota" in gemini_service.generate("s", [{"role": "user", "content": "x"}])[1].lower()
    def boom(*a, **k): raise requests.exceptions.ConnectionError()
    monkeypatch.setattr(requests, "post", boom); assert "network" in gemini_service.generate("s", [{"role": "user", "content": "x"}])[1].lower()


def test_unknown_provider_never_raises():
    assert not ai_provider.generate("Nope", "s", []).ok
