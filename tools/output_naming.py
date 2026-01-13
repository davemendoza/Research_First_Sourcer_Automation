#!/usr/bin/env python3
"""
output_naming.py
Canonical timestamped output filename utilities

© 2026 L. David Mendoza
AI Talent Engine – Research-First Sourcer Automation
"""

from pathlib import Path
from datetime import datetime
import subprocess
import sys


def timestamp():
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")


def build_csv_path(base_dir: Path, stem: str) -> Path:
    base_dir.mkdir(parents=True, exist_ok=True)
    fname = f"{stem}_{timestamp()}.csv"
    path = base_dir / fname

    if path.exists():
        raise RuntimeError(f"Refusing to overwrite existing file: {path}")

    return path


def auto_open_csv(path: Path):
    try:
        if sys.platform == "darwin":
            subprocess.run(["open", str(path)], check=False)
        elif sys.platform.startswith("linux"):
            subprocess.run(["xdg-open", str(path)], check=False)
        elif sys.platform.startswith("win"):
            subprocess.run(["start", str(path)], shell=True, check=False)
    except Exception:
        pass
