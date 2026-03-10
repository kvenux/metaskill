"""Git clone/pull source repositories using git CLI (no gitpython dependency)."""

import os
import subprocess
import logging

from config import SOURCE_REPOS, REPOS_DIR

log = logging.getLogger(__name__)

# Map repo id to possible local directory names (for pre-cloned repos)
_ALT_NAMES = {
    "anthropics-skills": "skills",
    "baoyu-skills": "baoyu-skills",
    "awesome-claude-skills": "awesome-claude-skills",
    "myclaude": "myclaude",
}


def _run_git(args: list[str], cwd: str = None) -> bool:
    try:
        subprocess.run(
            ["git"] + args, cwd=cwd, check=True,
            capture_output=True, text=True, timeout=120,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        log.error("git %s failed: %s", " ".join(args), e)
        return False


def clone_or_pull_all() -> dict[str, str]:
    """Clone or pull all source repos. Returns {repo_id: local_path}."""
    os.makedirs(REPOS_DIR, exist_ok=True)
    alt_repos_dir = os.path.join(os.path.dirname(__file__), "..", "repos")
    result = {}

    for repo_cfg in SOURCE_REPOS:
        rid = repo_cfg["id"]
        local = os.path.join(REPOS_DIR, rid)

        # Check alternative location (pre-cloned repos/ directory)
        if not os.path.isdir(os.path.join(local, ".git")):
            alt_name = _ALT_NAMES.get(rid, rid)
            alt_path = os.path.join(alt_repos_dir, alt_name)
            if os.path.isdir(os.path.join(alt_path, ".git")):
                log.info("Using pre-cloned repo for %s at %s", rid, alt_path)
                result[rid] = os.path.abspath(alt_path)
                continue

        if os.path.isdir(os.path.join(local, ".git")):
            log.info("Pulling %s", rid)
            _run_git(["pull"], cwd=local)
            result[rid] = local
        else:
            log.info("Cloning %s", rid)
            if _run_git(["clone", "--depth", "1", repo_cfg["url"], local]):
                result[rid] = local

    return result
