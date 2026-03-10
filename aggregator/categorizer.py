"""Categorize skills using LLM with keyword-rule fallback."""

import logging

from config import CATEGORIES, CATEGORY_KEYWORDS
from llm_client import batch_categorize

log = logging.getLogger(__name__)

CATEGORY_IDS = list(CATEGORIES.keys())
BATCH_SIZE = 8


def _keyword_categorize(skill: dict) -> str:
    """Fallback: match skill id/name/description against keyword rules."""
    text = f"{skill['id']} {skill['name']} {skill.get('description', '')}".lower()
    best_cat = "productivity"
    best_score = 0
    for cat_id, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > best_score:
            best_score = score
            best_cat = cat_id
    return best_cat


def _keyword_tags(skill: dict) -> list[str]:
    """Generate basic tags from skill metadata."""
    tags = []
    fm = skill.get("frontmatter", {})
    if isinstance(fm.get("tags"), list):
        tags.extend(fm["tags"])
    mp = skill.get("marketplace", {})
    if isinstance(mp.get("tags"), list):
        tags.extend(mp["tags"])
    # Deduplicate and normalize
    seen = set()
    result = []
    for t in tags:
        t = str(t).lower().strip().replace(" ", "-")
        if t and t not in seen:
            seen.add(t)
            result.append(t)
    return result[:10]


def categorize_all(skills: list[dict]) -> list[dict]:
    """Categorize all skills. Tries LLM in batches, falls back to keywords."""
    # Try LLM batch categorization
    llm_results = {}
    for i in range(0, len(skills), BATCH_SIZE):
        batch = skills[i : i + BATCH_SIZE]
        results = batch_categorize(batch, CATEGORY_IDS)
        if results:
            for r in results:
                sid = r.get("id", "")
                if sid:
                    llm_results[sid] = r
            log.info("LLM categorized batch %d-%d", i, i + len(batch))
        else:
            log.info("LLM unavailable for batch %d-%d, using keyword fallback", i, i + len(batch))

    # Apply results
    for skill in skills:
        sid = skill["id"]
        if sid in llm_results:
            lr = llm_results[sid]
            cat = lr.get("category_id", "")
            skill["category_id"] = cat if cat in CATEGORIES else _keyword_categorize(skill)
            skill["summary"] = lr.get("summary", skill.get("description", "")[:120])
            llm_tags = lr.get("tags", [])
            if llm_tags:
                skill["tags"] = [t.lower().strip().replace(" ", "-") for t in llm_tags][:10]
            else:
                skill["tags"] = _keyword_tags(skill)
        else:
            skill["category_id"] = _keyword_categorize(skill)
            skill["summary"] = skill.get("description", "")[:120]
            skill["tags"] = _keyword_tags(skill)

    return skills
