"""Google Gemini via REST (key sent in a header, never in the URL or logs)."""
import requests
from config import get_secret, DEFAULT_MODELS


def api_key(): return get_secret("GEMINI_API_KEY") or get_secret("GOOGLE_API_KEY")


def generate(system, messages, model=None, max_tokens=900, temperature=0.4, timeout=40):
    """Returns (text, error). messages: [{'role':'user'|'assistant','content':str}]"""
    key = api_key()
    if not key: return "", "Gemini API key not configured. Add GEMINI_API_KEY to Streamlit secrets or .env."
    model = model or get_secret("GEMINI_MODEL", DEFAULT_MODELS["Gemini"])
    body = {"systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in messages],
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}}
    try:
        r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent", json=body, headers={"x-goog-api-key": key}, timeout=timeout)
    except requests.exceptions.Timeout: return "", "Gemini timed out. Please retry."
    except requests.exceptions.RequestException: return "", "Network error reaching Gemini. Check your connection."
    if r.status_code != 200:
        return "", {400: "Gemini rejected the request or the API key is invalid.", 401: "Gemini API key is not authorised.", 403: "Gemini API key lacks permission.",
                    404: f"Gemini model '{model}' not found. Change the model in Account & Settings.", 429: "Gemini quota/rate limit reached. Wait a moment or switch provider."}.get(r.status_code, f"Gemini service error ({r.status_code}).")
    try:
        data = r.json()
        parts = data["candidates"][0]["content"]["parts"]
        text = "".join(p.get("text", "") for p in parts).strip()
        return (text, "") if text else ("", "Gemini returned an empty response (possibly blocked by safety filters).")
    except Exception:
        return "", "Gemini returned an unexpected response."
