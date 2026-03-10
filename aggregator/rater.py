"""AI rating module: 5-dimension scoring with LLM + heuristic fallback."""

import logging

from config import CATEGORIES
from llm_client import chat_json

log = logging.getLogger(__name__)

RATING_DIMENSIONS = ["practicality", "clarity", "automation", "quality", "impact"]
RATING_WEIGHTS = {
    "practicality": 0.25,
    "clarity": 0.20,
    "automation": 0.20,
    "quality": 0.20,
    "impact": 0.15,
}
RATING_BATCH_SIZE = 5


def _grade(score: float) -> str:
    if score >= 9.0:
        return "S"
    if score >= 8.0:
        return "A"
    if score >= 7.0:
        return "B"
    if score >= 6.0:
        return "C"
    return "D"


def _weighted_avg(dims: dict) -> float:
    total = sum(dims.get(d, 5) * RATING_WEIGHTS[d] for d in RATING_DIMENSIONS)
    return round(total, 1)


def _heuristic_rate(skill: dict) -> dict:
    """Fallback rating based on metadata signals."""
    desc = skill.get("description", "") or ""
    tags = skill.get("tags", []) or []
    files = skill.get("file_list", []) or []
    content = skill.get("skill_md_content", "") or ""

    # practicality: more files + longer content = more practical
    p = min(10, 5 + len(files) * 0.5 + (1 if len(content) > 500 else 0))
    # clarity: longer description = clearer
    c = min(10, 5 + len(desc) / 80 + (1 if len(content) > 300 else 0))
    # automation: presence of scripts
    has_script = any(f.endswith(('.py', '.sh', '.ps1', '.js', '.ts')) for f in files)
    a = 7.5 if has_script else 5.5
    # quality: tags + description quality
    q = min(10, 5 + len(tags) * 0.4 + (1 if len(desc) > 50 else 0))
    # impact: category relevance
    i = 7.0 if skill.get("category_id") in CATEGORIES else 5.5

    dims = {
        "practicality": round(min(p, 10), 1),
        "clarity": round(min(c, 10), 1),
        "automation": round(min(a, 10), 1),
        "quality": round(min(q, 10), 1),
        "impact": round(min(i, 10), 1),
    }
    return dims


def _llm_rate_batch(batch: list[dict]) -> dict:
    """Rate a batch of skills via LLM. Returns {skill_id: {dims...}} or None."""
    system_prompt = (
        "You are a skill quality rater. For each skill, score 5 dimensions (1-10):\n"
        "- practicality: How useful is this skill for real-world tasks?\n"
        "- clarity: How clear and well-structured are the instructions?\n"
        "- automation: How much does it automate vs require manual work?\n"
        "- quality: Overall code/content quality, error handling, edge cases?\n"
        "- impact: How significant is the productivity improvement?\n\n"
        'Return JSON: {"results": [{"id": "skill-id", "practicality": 8, "clarity": 7, ...}, ...]}\n'
        "Be fair but discriminating. Reserve 9-10 for truly exceptional skills."
    )
    items = []
    for s in batch:
        content = (s.get("skill_md_content", "") or "")[:2000]
        items.append(f"ID: {s['id']}\nName: {s['name']}\nDescription: {s.get('description', '')}\nContent:\n{content}\n---")
    user_prompt = "\n".join(items)

    result = chat_json(system_prompt, user_prompt)
    if result and "results" in result:
        out = {}
        for r in result["results"]:
            sid = r.get("id", "")
            if sid:
                dims = {}
                for d in RATING_DIMENSIONS:
                    v = r.get(d, 5)
                    try:
                        dims[d] = max(1, min(10, round(float(v), 1)))
                    except (ValueError, TypeError):
                        dims[d] = 5.0
                out[sid] = dims
        return out
    return None


def rate_all(skills: list[dict]) -> list[dict]:
    """Rate all skills. Tries LLM in batches, falls back to heuristics."""
    llm_results = {}
    for i in range(0, len(skills), RATING_BATCH_SIZE):
        batch = skills[i : i + RATING_BATCH_SIZE]
        results = _llm_rate_batch(batch)
        if results:
            llm_results.update(results)
            log.info("LLM rated batch %d-%d", i, i + len(batch))
        else:
            log.info("LLM unavailable for rating batch %d-%d, using heuristic", i, i + len(batch))

    for skill in skills:
        sid = skill["id"]
        if sid in llm_results:
            dims = llm_results[sid]
        else:
            dims = _heuristic_rate(skill)

        score = _weighted_avg(dims)
        skill["rating_dimensions"] = dims
        skill["rating"] = score
        skill["rating_grade"] = _grade(score)

    return skills
