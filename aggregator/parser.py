"""Parse skill directories: extract SKILL.md frontmatter and marketplace.json."""

import os
import re
import json
import logging

import yaml

from config import SOURCE_REPOS

log = logging.getLogger(__name__)

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)

# Directories to skip (not skills)
_SKIP_DIRS = {
    ".git", ".github", "node_modules", "__pycache__", ".vscode",
    "docs", "scripts", "tests", "examples", ".devcontainer",
}


def _parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown content."""
    m = _FRONTMATTER_RE.match(content)
    if m:
        try:
            return yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            return {}
    return {}


def _is_skill_dir(path: str) -> bool:
    """Check if a directory looks like a skill (has SKILL.md or marketplace.json)."""
    return (
        os.path.isfile(os.path.join(path, "SKILL.md"))
        or os.path.isfile(os.path.join(path, "marketplace.json"))
    )


def _list_files(skill_path: str) -> list[str]:
    """List all files in a skill directory, relative paths."""
    files = []
    for root, _dirs, fnames in os.walk(skill_path):
        for fn in fnames:
            rel = os.path.relpath(os.path.join(root, fn), skill_path)
            rel = rel.replace("\\", "/")
            files.append(rel)
    return sorted(files)


def _find_repo_config(repo_id: str) -> dict | None:
    for r in SOURCE_REPOS:
        if r["id"] == repo_id:
            return r
    return None


def parse_repo(repo_id: str, repo_path: str) -> list[dict]:
    """Parse all skills in a repo. Returns list of raw skill records."""
    repo_cfg = _find_repo_config(repo_id)
    if not repo_cfg:
        log.error("Unknown repo_id: %s", repo_id)
        return []

    skills = []
    skills_dirs = repo_cfg.get("skills_dirs", [""])

    for skills_dir in skills_dirs:
        scan_root = os.path.join(repo_path, skills_dir) if skills_dir else repo_path

        if not os.path.isdir(scan_root):
            log.warning("Scan root not found: %s", scan_root)
            continue

        for entry in sorted(os.listdir(scan_root)):
            if entry.startswith(".") or entry.lower() in _SKIP_DIRS:
                continue
            skill_path = os.path.join(scan_root, entry)
            if not os.path.isdir(skill_path):
                continue
            if not _is_skill_dir(skill_path):
                continue

            skill = _parse_single_skill(entry, skill_path, repo_cfg, skills_dir)
            if skill:
                skills.append(skill)

    log.info("Parsed %d skills from %s", len(skills), repo_id)
    return skills


def _parse_single_skill(dir_name: str, skill_path: str, repo_cfg: dict, skills_dir: str) -> dict | None:
    """Parse a single skill directory into a raw record."""
    skill_md_path = os.path.join(skill_path, "SKILL.md")
    marketplace_path = os.path.join(skill_path, "marketplace.json")

    name = dir_name
    description = ""
    skill_md_content = ""
    frontmatter = {}
    marketplace = {}

    # Parse SKILL.md
    if os.path.isfile(skill_md_path):
        try:
            with open(skill_md_path, "r", encoding="utf-8", errors="ignore") as f:
                skill_md_content = f.read()
            frontmatter = _parse_frontmatter(skill_md_content)
            name = frontmatter.get("name", dir_name)
            description = frontmatter.get("description", "")
        except OSError as e:
            log.warning("Error reading %s: %s", skill_md_path, e)

    # Parse marketplace.json
    if os.path.isfile(marketplace_path):
        try:
            with open(marketplace_path, "r", encoding="utf-8") as f:
                marketplace = json.load(f)
            if not name or name == dir_name:
                name = marketplace.get("name", name)
            if not description:
                description = marketplace.get("description", "")
        except (OSError, json.JSONDecodeError) as e:
            log.warning("Error reading %s: %s", marketplace_path, e)

    # Build relative path within repo
    rel_path = f"{skills_dir}/{dir_name}" if skills_dir else dir_name
    raw_base = repo_cfg["raw_base"]

    return {
        "id": dir_name.lower(),
        "dir_name": dir_name,
        "name": name,
        "description": description if isinstance(description, str) else str(description),
        "skill_md_content": skill_md_content,
        "frontmatter": frontmatter,
        "marketplace": marketplace,
        "source": {
            "repo": repo_cfg["id"],
            "repo_url": repo_cfg["repo_url"],
            "path": rel_path,
        },
        "file_list": _list_files(skill_path),
        "raw_base_url": f"{raw_base}/{rel_path}",
    }
