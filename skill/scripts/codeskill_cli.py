#!/usr/bin/env python3
"""CodeSkill CLI — browse, search, install and download skills.

Pure stdlib, zero dependencies. All output is JSON to stdout.
Exit 0 on success, exit 1 on failure.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import shutil

API_BASE = os.environ.get("CODESKILL_API_BASE", "http://127.0.0.1:8000")
INSTALL_DIR = os.path.join(
    os.environ.get("USERPROFILE", os.environ.get("HOME", "~")),
    ".config", "opencode", "skills",
)


def _out(data):
    json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    sys.exit(0)


def _err(code: str, message: str):
    json.dump({"error": True, "code": code, "message": message}, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    sys.exit(1)


def _fetch(path: str):
    url = f"{API_BASE}/api/{path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "codeskill-cli/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            resource = path.split("/")[0].upper()
            _err(f"{resource}_NOT_FOUND", f"Not found: {path}")
        _err("NETWORK_ERROR", f"HTTP {e.code}: {url}")
    except urllib.error.URLError as e:
        _err("SERVICE_UNAVAILABLE", f"Cannot connect to {API_BASE}: {e.reason}")
    except Exception as e:
        _err("NETWORK_ERROR", str(e))


def _download_raw(url: str, dest: str):
    """Download a raw file from URL to local path."""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "codeskill-cli/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(dest, "wb") as f:
                shutil.copyfileobj(resp, f)
    except Exception as e:
        _err("DOWNLOAD_FAILED", f"Failed to download {url}: {e}")


# --- Subcommands ---

def cmd_list_skills(args):
    data = _fetch("skills/index.json")
    items = data.get("items", [])
    if args.category:
        items = [i for i in items if i.get("category_id") == args.category]
    if args.tag:
        items = [i for i in items if args.tag in i.get("tags", [])]
    _out({"total": len(items), "items": items})


def cmd_search_skills(args):
    data = _fetch("search/index.json")
    q = args.query.lower()
    results = [i for i in data.get("items", []) if q in i.get("text", "")]
    # Strip search text from output
    for r in results:
        r.pop("text", None)
    _out({"total": len(results), "items": results})


def cmd_get_skill(args):
    data = _fetch(f"skills/{args.skill_id}/index.json")
    _out(data)


def cmd_list_categories(args):
    _out(_fetch("categories/index.json"))


def cmd_get_category(args):
    _out(_fetch(f"categories/{args.category_id}/index.json"))


def cmd_list_tags(args):
    _out(_fetch("tags/index.json"))


def cmd_list_packs(args):
    _out(_fetch("packs/index.json"))


def cmd_get_pack(args):
    _out(_fetch(f"packs/{args.pack_id}/index.json"))


def cmd_stats(args):
    _out(_fetch("stats/index.json"))


def cmd_install(args):
    skill = _fetch(f"skills/{args.skill_id}/index.json")
    raw_base = skill.get("raw_base_url", "")
    file_list = skill.get("file_list", [])
    if not raw_base or not file_list:
        _err("DOWNLOAD_FAILED", "Skill has no downloadable files")

    dest_dir = os.path.join(INSTALL_DIR, args.skill_id)
    downloaded = []
    for rel in file_list:
        if rel == "skill.json":
            continue
        url = f"{raw_base}/{rel}"
        dest = os.path.join(dest_dir, rel)
        _download_raw(url, dest)
        downloaded.append(rel)

    _out({
        "installed": True,
        "skill_id": args.skill_id,
        "path": dest_dir,
        "files": downloaded,
    })


def cmd_download(args):
    skill = _fetch(f"skills/{args.skill_id}/index.json")
    raw_base = skill.get("raw_base_url", "")
    file_list = skill.get("file_list", [])
    if not raw_base or not file_list:
        _err("DOWNLOAD_FAILED", "Skill has no downloadable files")

    dest_dir = args.output_dir or os.path.join(INSTALL_DIR, args.skill_id)
    downloaded = []
    for rel in file_list:
        if rel == "skill.json":
            continue
        url = f"{raw_base}/{rel}"
        dest = os.path.join(dest_dir, rel)
        _download_raw(url, dest)
        downloaded.append(rel)

    _out({
        "downloaded": True,
        "skill_id": args.skill_id,
        "path": dest_dir,
        "files": downloaded,
    })


# --- Main ---

def main():
    parser = argparse.ArgumentParser(prog="codeskill_cli", description="CodeSkill CLI")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("list-skills", help="List all skills")
    p.add_argument("--category", default=None)
    p.add_argument("--tag", default=None)

    p = sub.add_parser("search-skills", help="Search skills")
    p.add_argument("query")

    p = sub.add_parser("get-skill", help="Get skill detail")
    p.add_argument("skill_id")

    sub.add_parser("list-categories", help="List categories")

    p = sub.add_parser("get-category", help="Get category detail")
    p.add_argument("category_id")

    sub.add_parser("list-tags", help="List tags")
    sub.add_parser("list-packs", help="List skill packs")

    p = sub.add_parser("get-pack", help="Get pack detail")
    p.add_argument("pack_id")

    p = sub.add_parser("install", help="Install a skill")
    p.add_argument("skill_id")

    p = sub.add_parser("download", help="Download a skill")
    p.add_argument("skill_id")
    p.add_argument("--output-dir", default=None)

    sub.add_parser("stats", help="Show statistics")

    args = parser.parse_args()
    commands = {
        "list-skills": cmd_list_skills,
        "search-skills": cmd_search_skills,
        "get-skill": cmd_get_skill,
        "list-categories": cmd_list_categories,
        "get-category": cmd_get_category,
        "list-tags": cmd_list_tags,
        "list-packs": cmd_list_packs,
        "get-pack": cmd_get_pack,
        "install": cmd_install,
        "download": cmd_download,
        "stats": cmd_stats,
    }
    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
