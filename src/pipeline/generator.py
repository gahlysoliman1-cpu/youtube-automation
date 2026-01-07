import json
import random
from dataclasses import dataclass
from typing import Any

import requests

from config import KEYS
from pipeline.fallback import try_chain

PROMPT = """
Create one short quiz question in English for a general audience.
Return JSON with keys: question, answer, category.
Question should be under 80 characters.
Answer should be under 40 characters.
Do not include emojis.
""".strip()


@dataclass(frozen=True)
class QuestionItem:
    question: str
    answer: str
    category: str


def _extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json", "", 1).strip()
    return json.loads(cleaned)


def _call_gemini() -> QuestionItem:
    if not KEYS.gemini_api_key:
        raise RuntimeError("Missing GEMINI_API_KEY")
    headers = {"Content-Type": "application/json"}
    payload: dict[str, Any] = {
        "contents": [{"parts": [{"text": PROMPT}]}],
        "generationConfig": {"temperature": 0.9},
    }
    params = {"key": KEYS.gemini_api_key}
    model_names = ["gemini-1.5-flash-latest", "gemini-1.5-flash"]
    last_error: Exception | None = None
    for model in model_names:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        try:
            response = requests.post(url, headers=headers, params=params, json=payload, timeout=30)
            response.raise_for_status()
        except requests.HTTPError as exc:
            last_error = exc
            continue
        text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        data = _extract_json(text)
        return QuestionItem(**data)
    if last_error:
        raise last_error
    raise RuntimeError("Gemini generation failed")


def _call_groq() -> QuestionItem:
    if not KEYS.groq_api_key:
        raise RuntimeError("Missing GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {KEYS.groq_api_key}",
        "Content-Type": "application/json",
    }
    payload: dict[str, Any] = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "Return only valid JSON."},
            {"role": "user", "content": PROMPT},
        ],
        "temperature": 0.9,
    }
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    text = response.json()["choices"][0]["message"]["content"]
    data = _extract_json(text)
    return QuestionItem(**data)


def _call_openrouter() -> QuestionItem:
    if not KEYS.openrouter_key:
        raise RuntimeError("Missing OPENROUTER_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {KEYS.openrouter_key}",
        "Content-Type": "application/json",
    }
    payload: dict[str, Any] = {
        "model": "meta-llama/llama-3.1-8b-instruct:free",
        "messages": [
            {"role": "system", "content": "Return only valid JSON."},
            {"role": "user", "content": PROMPT},
        ],
        "temperature": 0.9,
    }
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    text = response.json()["choices"][0]["message"]["content"]
    data = _extract_json(text)
    return QuestionItem(**data)


def generate_question() -> QuestionItem:
    handlers = [_call_gemini, _call_groq, _call_openrouter]
    return try_chain("LLM", handlers)


def shuffle_intro() -> str:
    intros = [
        "Can you answer before 10 seconds end?",
        "Type your answer before time runs out!",
        "Guess fast and drop it in the comments!",
    ]
    return random.choice(intros)
