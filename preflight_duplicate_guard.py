#!/usr/bin/env python3
"""
AI Talent Engine — Preflight Duplicate Guard (Fail-Closed)
© 2025 L. David Mendoza
Version: v1.1.0-ignore-init

Rules:
- Ignore __init__.py (package markers)
- Fail on all other duplicate basenames
"""

import argparse
import os
from collections import defaultdict

EXCLUDE_DIRS = {
    ".git", "__pycache__", ".venv", "venv",
    "_ARCHIVE", "_QUARANTINE",
    "backup", "backups", "backup_proprietary_notice",
    "dist", "build"
}

def main():
    repo = os.getcwd()
    seen = defaultdict(list)

    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            if not f.endswith(".py"):
                continue
            if f == "__init__.py":
                continue
            seen[f].append(os.path.join(root, f))

    collisions = {k: v for k, v in seen.items() if len(v) > 1}

    if collisions:
        print("❌ PREFLIGHT FAILURE: Duplicate Python basenames detected.\n")
        for name, paths in sorted(collisions.items()):
            print(f"{name}:")
            for p in paths:
                print(f"  - {p}")
            print()
        print("Action required: archive duplicates so only ONE copy remains import-visible.")
        raise SystemExit(2)

    print("✅ PREFLIGHT OK: No duplicate module basenames detected.")
    return 0

if __name__ == "__main__":
    main()
