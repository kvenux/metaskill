# CodeSkill API Reference

## Base URL

Default: `http://127.0.0.1:8000`
Override: set `CODESKILL_API_BASE` environment variable.

All endpoints return JSON. Static files are served from GitHub Pages.

---

## Endpoints

### GET /api/skills/index.json
List all skills (summary view).

**Response:**
```json
{
  "total": 909,
  "items": [
    {
      "id": "algorithmic-art",
      "name": "Algorithmic Art",
      "summary": "算法艺术生成技能",
      "category_id": "generative-art",
      "tags": ["generative-art", "p5js"],
      "source_repo": "anthropics-skills",
      "security_status": "safe"
    }
  ],
  "updated_at": "2026-03-09T00:00:00Z"
}
```

### GET /api/skills/{id}/index.json
Get skill detail.

**Response:**
```json
{
  "id": "algorithmic-art",
  "name": "Algorithmic Art",
  "description": "Full description...",
  "summary": "算法艺术生成技能",
  "source": {
    "repo": "anthropics-skills",
    "repo_url": "https://github.com/anthropics/skills",
    "path": "algorithmic-art"
  },
  "category_id": "generative-art",
  "tags": ["generative-art", "p5js"],
  "file_list": ["SKILL.md", "templates/generator.js"],
  "raw_base_url": "https://raw.githubusercontent.com/.../algorithmic-art",
  "security_status": "safe",
  "security_warnings": [],
  "updated_at": "2026-03-09T00:00:00Z"
}
```

### GET /api/categories/index.json
List all categories.

### GET /api/categories/{id}/index.json
Get category detail with skill list.

### GET /api/tags/index.json
List all tags with counts.

### GET /api/packs/index.json
List all skill packs.

### GET /api/packs/{id}/index.json
Get pack detail with skill list.

### GET /api/search/index.json
Client-side search index (all skills with searchable text).

### GET /api/stats/index.json
Aggregation statistics.

### GET /api/codeskill/setup
Installation instructions (plain text).

### GET /api/codeskill/install-sh
Bash install script.

### GET /api/codeskill/install-ps1
PowerShell install script.

### GET /api/codeskill/files/{path}
Meta-skill source files (SKILL.md, scripts/codeskill_cli.py, etc).

---

## Error Format

```json
{
  "error": true,
  "code": "SKILL_NOT_FOUND",
  "message": "Skill 'xyz' not found"
}
```

## Error Codes

| Code | Description |
|---|---|
| SERVICE_UNAVAILABLE | API server not reachable |
| SKILL_NOT_FOUND | Skill ID does not exist |
| CATEGORY_NOT_FOUND | Category ID does not exist |
| PACK_NOT_FOUND | Pack ID does not exist |
| NETWORK_ERROR | Network connection failed |
| DOWNLOAD_FAILED | File download or extraction failed |
