"""Person A owns this file. LLM call abstraction. See CONTRACT.md."""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

_DEFAULTS = {
    "groq": "llama-3.3-70b-versatile",
    "gemini": "gemini-2.5-flash",
}

_ENDPOINTS = {
    "groq": "https://api.groq.com/openai/v1/chat/completions",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
}


def call_llm(prompt: str) -> str:
    """Call the configured LLM provider and return the raw text response.

    Raises on any failure so the pipeline can catch and fall back to cache.
    """
    provider = os.getenv("LLM_PROVIDER", "groq").lower()
    model = os.getenv("LLM_MODEL", "") or _DEFAULTS.get(provider, "")

    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            raise ValueError("GROQ_API_KEY not set")
        resp = requests.post(
            _ENDPOINTS["groq"],
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "response_format": {"type": "json_object"},
            },
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    elif provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set")
        url = _ENDPOINTS["gemini"].format(model=model) + f"?key={api_key}"
        resp = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"},
            },
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"]

    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider}")
