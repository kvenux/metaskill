"""OpenAI-compatible API client with caching and retry."""

import os
import json
import hashlib
import logging
import time

from config import LLM_API_BASE, LLM_API_KEY, LLM_MODEL, LLM_CACHE_DIR

log = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if _client is None:
        from openai import OpenAI
        _client = OpenAI(base_url=LLM_API_BASE, api_key=LLM_API_KEY)
    return _client


def _cache_path(key: str) -> str:
    os.makedirs(LLM_CACHE_DIR, exist_ok=True)
    h = hashlib.sha256(key.encode()).hexdigest()[:16]
    return os.path.join(LLM_CACHE_DIR, f"{h}.json")


def _read_cache(key: str):
    p = _cache_path(key)
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def _write_cache(key: str, value):
    p = _cache_path(key)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False)


def chat_json(system_prompt: str, user_prompt: str, max_retries: int = 3):
    """Send a chat request expecting JSON response. Returns parsed dict or None."""
    cache_key = hashlib.sha256((system_prompt + user_prompt).encode()).hexdigest()
    cached = _read_cache(cache_key)
    if cached is not None:
        return cached

    if not LLM_API_KEY:
        log.warning("LLM_API_KEY not set, skipping LLM call")
        return None

    client = _get_client()
    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
            )
            text = resp.choices[0].message.content.strip()
            data = json.loads(text)
            _write_cache(cache_key, data)
            return data
        except Exception as e:
            log.warning("LLM attempt %d failed: %s", attempt + 1, e)
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    return None


def batch_categorize(skills_batch: list[dict], category_ids: list[str]):
    """Categorize a batch of skills via LLM. Returns list of result dicts."""
    system_prompt = (
        "You are a skill categorization assistant. For each skill, return a JSON object with:\n"
        '- "results": array of objects, each with "id", "category_id", "summary" (one-line Chinese summary ≤120 chars), "tags" (3-8 English tags).\n'
        f"Valid category_ids: {json.dumps(category_ids)}\n"
        "Only pick from the valid category_ids. Tags should be lowercase kebab-case."
    )
    items = []
    for s in skills_batch:
        content = s.get("skill_md_content", "")[:2000]
        items.append(f"ID: {s['id']}\nName: {s['name']}\nContent:\n{content}\n---")
    user_prompt = "\n".join(items)

    result = chat_json(system_prompt, user_prompt)
    if result and "results" in result:
        return result["results"]
    return None
