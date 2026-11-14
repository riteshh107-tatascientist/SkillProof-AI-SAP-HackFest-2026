"""OpenAI Chat Completions via REST."""
import requests
from config import get_secret, DEFAULT_MODELS


def api_key(): return get_secret("OPENAI_API_KEY")


def generate(system, messages, model=None, max_tokens=900, temperature=0.4, timeout=40):
    key = api_key()
    if not key: return "", "OpenAI API key not configured. Add OPENAI_API_KEY to Streamlit secrets or .env."
    model = model or get_secret("OPENAI_MODEL", DEFAULT_MODELS["OpenAI"])
    body = {"model": model, "messages": [{"role": "system", "content": system}] + messages, "max_completion_tokens": max_tokens, "temperature": temperature}
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    try:
        r = requests.post("https://api.openai.com/v1/chat/completions", json=body, headers=headers, timeout=timeout)
        if r.status_code == 400 and "temperature" in r.text.lower():  # some models only accept the default temperature
            body.pop("temperature"); r = requests.post("https://api.openai.com/v1/chat/completions", json=body, headers=headers, timeout=timeout)
    except requests.exceptions.Timeout: return "", "OpenAI timed out. Please retry."
    except requests.exceptions.RequestException: return "", "Network error reaching OpenAI. Check your connection."
    if r.status_code != 200:
        return "", {400: "OpenAI rejected the request (check the model name in Settings).", 401: "OpenAI API key is invalid.", 403: "OpenAI key lacks permission for this model.",
                    404: f"OpenAI model '{model}' not found. Change the model in Account & Settings.", 429: "OpenAI quota or rate limit reached. Check billing or switch provider."}.get(r.status_code, f"OpenAI service error ({r.status_code}).")
    try:
        text = (r.json()["choices"][0]["message"]["content"] or "").strip()
        return (text, "") if text else ("", "OpenAI returned an empty response.")
    except Exception:
        return "", "OpenAI returned an unexpected response."
