"""Generate all static JSON files for the API."""

import os
import json
import logging
from datetime import datetime, timezone

from config import CATEGORIES, SKILL_PACKS, OUTPUT_DIR, SEARCH_SYNONYMS

log = logging.getLogger(__name__)


def _write_json(path: str, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log.debug("Wrote %s", path)


def _skill_detail(skill: dict) -> dict:
    return {
        "id": skill["id"],
        "name": skill["name"],
        "description": skill.get("description", ""),
        "summary": skill.get("summary", ""),
        "source": skill["source"],
        "category_id": skill.get("category_id", "productivity"),
        "tags": skill.get("tags", []),
        "file_list": skill.get("file_list", []),
        "raw_base_url": skill.get("raw_base_url", ""),
        "security_status": skill.get("security_status", "safe"),
        "security_warnings": skill.get("security_warnings", []),
        "rating": skill.get("rating", 0),
        "rating_grade": skill.get("rating_grade", "D"),
        "rating_dimensions": skill.get("rating_dimensions", {}),
        "flow_diagram": skill.get("flow_diagram", ""),
        "output_preview": skill.get("output_preview", ""),
        "target_audience": skill.get("target_audience", ""),
        "updated_at": skill.get("updated_at", datetime.now(timezone.utc).isoformat()),
    }


def _skill_list_item(skill: dict) -> dict:
    return {
        "id": skill["id"],
        "name": skill["name"],
        "summary": skill.get("summary", ""),
        "category_id": skill.get("category_id", "productivity"),
        "tags": skill.get("tags", []),
        "source_repo": skill["source"]["repo"],
        "security_status": skill.get("security_status", "safe"),
        "rating": skill.get("rating", 0),
        "rating_grade": skill.get("rating_grade", "D"),
    }


def generate_all(skills: list[dict]):
    """Generate all static API JSON files from processed skills."""
    now = datetime.now(timezone.utc).isoformat()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # --- /api/skills/index.json ---
    items = [_skill_list_item(s) for s in skills]
    _write_json(os.path.join(OUTPUT_DIR, "skills", "index.json"), {
        "total": len(items),
        "items": items,
        "updated_at": now,
    })

    # --- /api/skills/{id}/index.json ---
    for s in skills:
        _write_json(
            os.path.join(OUTPUT_DIR, "skills", s["id"], "index.json"),
            _skill_detail(s),
        )

    # --- /api/categories/index.json ---
    cat_list = []
    cat_skills = {cid: [] for cid in CATEGORIES}
    for s in skills:
        cid = s.get("category_id", "productivity")
        if cid in cat_skills:
            cat_skills[cid].append(_skill_list_item(s))
    for cid, info in CATEGORIES.items():
        cat_list.append({
            "id": cid,
            "name": info["name"],
            "name_en": info.get("name_en", ""),
            "description": info["description"],
            "skill_count": len(cat_skills.get(cid, [])),
        })
    _write_json(os.path.join(OUTPUT_DIR, "categories", "index.json"), {
        "total": len(cat_list),
        "items": cat_list,
    })

    # --- /api/categories/{id}/index.json ---
    for cid, info in CATEGORIES.items():
        _write_json(os.path.join(OUTPUT_DIR, "categories", cid, "index.json"), {
            "id": cid,
            "name": info["name"],
            "name_en": info.get("name_en", ""),
            "description": info["description"],
            "skills": cat_skills.get(cid, []),
        })

    # --- /api/tags/index.json ---
    tag_count: dict[str, int] = {}
    for s in skills:
        for t in s.get("tags", []):
            tag_count[t] = tag_count.get(t, 0) + 1
    tag_items = [{"tag": t, "count": c} for t, c in sorted(tag_count.items(), key=lambda x: -x[1])]
    _write_json(os.path.join(OUTPUT_DIR, "tags", "index.json"), {
        "total": len(tag_items),
        "items": tag_items,
    })

    # --- /api/packs/index.json + /api/packs/{id}/index.json ---
    pack_list = []
    for pid, pinfo in SKILL_PACKS.items():
        pack_skills = [_skill_list_item(s) for s in skills if s["id"] in pinfo["skills"]]
        pack_obj = {
            "id": pid,
            "name": pinfo["name"],
            "description": pinfo["description"],
            "emoji": pinfo.get("emoji", "📦"),
            "featured": pinfo.get("featured", False),
            "skill_ids": pinfo["skills"],
            "skills": pack_skills,
        }
        _write_json(os.path.join(OUTPUT_DIR, "packs", pid, "index.json"), pack_obj)
        pack_list.append({
            "id": pid,
            "name": pinfo["name"],
            "description": pinfo["description"],
            "emoji": pinfo.get("emoji", "📦"),
            "featured": pinfo.get("featured", False),
            "skill_count": len(pack_skills),
        })
    _write_json(os.path.join(OUTPUT_DIR, "packs", "index.json"), {
        "total": len(pack_list),
        "items": pack_list,
    })

    # --- /api/search/index.json (client-side search index) ---
    search_items = []
    for s in skills:
        search_items.append({
            "id": s["id"],
            "name": s["name"],
            "summary": s.get("summary", ""),
            "category_id": s.get("category_id", ""),
            "tags": s.get("tags", []),
            "source_repo": s["source"]["repo"],
            "text": f"{s['name']} {s.get('summary','')} {' '.join(s.get('tags',[]))} {s.get('description','')[:200]}".lower(),
        })
    _write_json(os.path.join(OUTPUT_DIR, "search", "index.json"), {
        "total": len(search_items),
        "items": search_items,
    })

    # --- /api/stats/index.json ---
    repo_counts: dict[str, int] = {}
    status_counts = {"safe": 0, "warning": 0, "blocked": 0}
    for s in skills:
        repo = s["source"]["repo"]
        repo_counts[repo] = repo_counts.get(repo, 0) + 1
        st = s.get("security_status", "safe")
        if st in status_counts:
            status_counts[st] += 1
    _write_json(os.path.join(OUTPUT_DIR, "stats", "index.json"), {
        "total_skills": len(skills),
        "total_categories": len(CATEGORIES),
        "total_tags": len(tag_count),
        "total_packs": len(SKILL_PACKS),
        "by_repo": repo_counts,
        "by_security": status_counts,
        "updated_at": now,
    })

    # --- /api/rankings/index.json (top skills by rating) ---
    ranked = sorted(skills, key=lambda s: s.get("rating", 0), reverse=True)
    ranking_items = [_skill_list_item(s) for s in ranked]
    _write_json(os.path.join(OUTPUT_DIR, "rankings", "index.json"), {
        "total": len(ranking_items),
        "items": ranking_items,
        "updated_at": now,
    })

    # --- /api/synonyms/index.json (search synonyms for frontend) ---
    _write_json(os.path.join(OUTPUT_DIR, "synonyms", "index.json"), SEARCH_SYNONYMS)

    log.info("Generated all static files in %s (%d skills)", OUTPUT_DIR, len(skills))
