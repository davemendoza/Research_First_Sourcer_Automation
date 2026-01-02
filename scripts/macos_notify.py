#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
macos_notify.py

AI Talent Engine — macOS Notification + Pop-Open Helper
Version: v1.0.0
Author: L. David Mendoza
Date: 2026-01-02

Purpose:
- Show a macOS notification via osascript
- Optionally open a path (CSV) in default app and reveal in Finder

Fail-closed behavior:
- If osascript is unavailable or fails, exit non-zero (caller can hard-fail)

Usage:
  python3 scripts/macos_notify.py --title "Title" --message "Message" --open "/path/to/file.csv"
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
import sys


def fail(msg: str, code: int = 2) -> None:
    print(f"ERROR: {msg}")
    sys.exit(code)


def run(cmd: list[str]) -> None:
    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        fail(f"Command failed: {' '.join(cmd)} :: {e}", code=3)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--message", required=True)
    ap.add_argument("--open", dest="open_path", default="")
    args = ap.parse_args()

    # Notification
    osa = [
        "osascript",
        "-e",
        f'display notification "{args.message.replace(chr(34), chr(39))}" with title "{args.title.replace(chr(34), chr(39))}"',
    ]
    run(osa)

    if args.open_path:
        p = Path(args.open_path).expanduser().resolve()
        if not p.exists():
            fail(f"--open path does not exist: {p}", code=4)

        # Reveal in Finder and open
        run(["open", "-R", str(p)])
        run(["open", str(p)])


if __name__ == "__main__":
    main()
