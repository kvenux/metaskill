"""Security scanner: detect malicious patterns in skill files."""

import os
import re
import logging

from config import (
    SECURITY_CRITICAL_PATTERNS,
    SECURITY_CRITICAL_EXTENSIONS,
    SECURITY_WARNING_PATTERNS,
    SECURITY_SCAN_EXTENSIONS,
    SECURITY_MAX_FILE_SIZE,
)

log = logging.getLogger(__name__)

_critical_re = [re.compile(p, re.IGNORECASE) for p in SECURITY_CRITICAL_PATTERNS]
_warning_re = [re.compile(p, re.IGNORECASE) for p in SECURITY_WARNING_PATTERNS]


def scan_skill(skill_path: str) -> tuple[str, list[str]]:
    """Scan a skill directory. Returns (status, warnings_list).
    status: 'safe' | 'warning' | 'blocked'
    """
    warnings = []
    blocked = False

    for root, _dirs, files in os.walk(skill_path):
        for fname in files:
            fpath = os.path.join(root, fname)
            ext = os.path.splitext(fname)[1].lower()
            rel = os.path.relpath(fpath, skill_path)

            # Check binary extensions
            if ext in SECURITY_CRITICAL_EXTENSIONS:
                warnings.append(f"CRITICAL: Binary file detected: {rel}")
                blocked = True
                continue

            # Check file size
            try:
                size = os.path.getsize(fpath)
            except OSError:
                continue
            if size > SECURITY_MAX_FILE_SIZE:
                warnings.append(f"WARNING: Large file ({size} bytes): {rel}")

            # Only scan text files with known extensions
            if ext not in SECURITY_SCAN_EXTENSIONS:
                continue

            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except OSError:
                continue

            for pat in _critical_re:
                if pat.search(content):
                    warnings.append(f"CRITICAL: Pattern '{pat.pattern}' in {rel}")
                    blocked = True

            for pat in _warning_re:
                if pat.search(content):
                    warnings.append(f"WARNING: Pattern '{pat.pattern}' in {rel}")

    # Check for empty SKILL.md
    skill_md = os.path.join(skill_path, "SKILL.md")
    if os.path.exists(skill_md):
        try:
            if os.path.getsize(skill_md) == 0:
                warnings.append("WARNING: Empty SKILL.md")
        except OSError:
            pass

    if blocked:
        return "blocked", warnings
    if warnings:
        return "warning", warnings
    return "safe", []
