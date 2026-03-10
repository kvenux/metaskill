"""Aggregator pipeline entry point."""

import os
import sys
import shutil
import logging

# Ensure aggregator dir is on path
sys.path.insert(0, os.path.dirname(__file__))

from config import OUTPUT_DIR
from cloner import clone_or_pull_all
from parser import parse_repo
from categorizer import categorize_all
from security_scanner import scan_skill
from static_generator import generate_all

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("aggregator")


def _generate_codeskill_files():
    """Copy meta-skill files to site/api/codeskill/."""
    skill_src = os.path.join(os.path.dirname(__file__), "..", "skill")
    codeskill_dir = os.path.join(OUTPUT_DIR, "codeskill")
    files_dir = os.path.join(codeskill_dir, "files")
    os.makedirs(files_dir, exist_ok=True)

    # Copy skill files
    for rel in ["SKILL.md", "scripts/codeskill_cli.py", "references/API_REFERENCE.md"]:
        src = os.path.join(skill_src, rel)
        dst = os.path.join(files_dir, rel)
        if os.path.isfile(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)

    # Generate setup instructions
    base = "https://kvenux.github.io/metaskill"
    setup_text = f"""# CodeSkill 安装指引

Fetch the installation guide and follow it:
  curl -s {base}/api/codeskill/setup | cat

## 一键安装

Linux / macOS:
  curl -s {base}/api/codeskill/install-sh | bash

Windows (PowerShell):
  irm {base}/api/codeskill/install-ps1 | iex

## 手动安装

1. 创建目录:
   mkdir -p ~/.config/opencode/skills/codeskill/scripts ~/.config/opencode/skills/codeskill/references

2. 下载文件:
   curl -o ~/.config/opencode/skills/codeskill/SKILL.md {base}/api/codeskill/files/SKILL.md
   curl -o ~/.config/opencode/skills/codeskill/scripts/codeskill_cli.py {base}/api/codeskill/files/scripts/codeskill_cli.py
   curl -o ~/.config/opencode/skills/codeskill/references/API_REFERENCE.md {base}/api/codeskill/files/references/API_REFERENCE.md

3. 验证:
   python ~/.config/opencode/skills/codeskill/scripts/codeskill_cli.py --help
"""
    with open(os.path.join(codeskill_dir, "setup"), "w", encoding="utf-8") as f:
        f.write(setup_text)

    # Generate bash install script
    bash_script = r"""#!/usr/bin/env bash
set -e
SKILL_DIR="$HOME/.config/opencode/skills/codeskill"
API_BASE="${CODESKILL_API_BASE:-https://kvenux.github.io/metaskill}"
echo "Installing codeskill to $SKILL_DIR ..."
mkdir -p "$SKILL_DIR/scripts" "$SKILL_DIR/references"
curl -sfL "$API_BASE/api/codeskill/files/SKILL.md" -o "$SKILL_DIR/SKILL.md"
curl -sfL "$API_BASE/api/codeskill/files/scripts/codeskill_cli.py" -o "$SKILL_DIR/scripts/codeskill_cli.py"
curl -sfL "$API_BASE/api/codeskill/files/references/API_REFERENCE.md" -o "$SKILL_DIR/references/API_REFERENCE.md"
chmod +x "$SKILL_DIR/scripts/codeskill_cli.py"
echo "codeskill installed successfully!"
echo "Verify: python $SKILL_DIR/scripts/codeskill_cli.py --help"
"""
    with open(os.path.join(codeskill_dir, "install-sh"), "w", encoding="utf-8", newline="\n") as f:
        f.write(bash_script)

    # Generate PowerShell install script
    ps_script = r"""$ErrorActionPreference = "Stop"
$SkillDir = "$env:USERPROFILE\.config\opencode\skills\codeskill"
$ApiBase = if ($env:CODESKILL_API_BASE) { $env:CODESKILL_API_BASE } else { "https://kvenux.github.io/metaskill" }
Write-Host "Installing codeskill to $SkillDir ..."
New-Item -ItemType Directory -Force -Path "$SkillDir\scripts","$SkillDir\references" | Out-Null
Invoke-WebRequest -Uri "$ApiBase/api/codeskill/files/SKILL.md" -OutFile "$SkillDir\SKILL.md"
Invoke-WebRequest -Uri "$ApiBase/api/codeskill/files/scripts/codeskill_cli.py" -OutFile "$SkillDir\scripts\codeskill_cli.py"
Invoke-WebRequest -Uri "$ApiBase/api/codeskill/files/references/API_REFERENCE.md" -OutFile "$SkillDir\references\API_REFERENCE.md"
Write-Host "codeskill installed successfully!"
Write-Host "Verify: python $SkillDir\scripts\codeskill_cli.py --help"
"""
    with open(os.path.join(codeskill_dir, "install-ps1"), "w", encoding="utf-8") as f:
        f.write(ps_script)

    log.info("Generated codeskill meta-files in %s", codeskill_dir)


def main():
    log.info("=== MetaSkill Aggregator ===")

    # Step 1: Clone/pull repos
    log.info("Step 1: Cloning/pulling source repos...")
    repo_paths = clone_or_pull_all()
    if not repo_paths:
        log.error("No repos available")
        sys.exit(1)

    # Step 2: Parse skills
    log.info("Step 2: Parsing skills...")
    all_skills = []
    for repo_id, repo_path in repo_paths.items():
        skills = parse_repo(repo_id, repo_path)
        all_skills.extend(skills)
    log.info("Total raw skills: %d", len(all_skills))

    # Deduplicate by id (first occurrence wins)
    seen = set()
    unique_skills = []
    for s in all_skills:
        if s["id"] not in seen:
            seen.add(s["id"])
            unique_skills.append(s)
    log.info("Unique skills after dedup: %d", len(unique_skills))

    # Step 3: Security scan
    log.info("Step 3: Security scanning...")
    for s in unique_skills:
        # Reconstruct skill path for scanning
        repo_cfg = None
        for r in __import__("config").SOURCE_REPOS:
            if r["id"] == s["source"]["repo"]:
                repo_cfg = r
                break
        if repo_cfg:
            from config import REPOS_DIR
            skill_path = os.path.join(REPOS_DIR, repo_cfg["id"], s["source"]["path"])
            if os.path.isdir(skill_path):
                status, warnings = scan_skill(skill_path)
                s["security_status"] = status
                s["security_warnings"] = warnings

    blocked = sum(1 for s in unique_skills if s.get("security_status") == "blocked")
    warned = sum(1 for s in unique_skills if s.get("security_status") == "warning")
    log.info("Security: %d blocked, %d warnings", blocked, warned)

    # Step 4: Categorize (LLM + fallback)
    log.info("Step 4: Categorizing skills...")
    unique_skills = categorize_all(unique_skills)

    # Step 5: Generate static files
    log.info("Step 5: Generating static API files...")
    generate_all(unique_skills)

    # Step 6: Generate codeskill meta-files
    log.info("Step 6: Generating codeskill install files...")
    _generate_codeskill_files()

    log.info("=== Done! %d skills processed ===", len(unique_skills))


if __name__ == "__main__":
    main()
