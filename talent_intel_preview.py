#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
import subprocess
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent
CORE_PREVIEW = REPO_ROOT / "EXECUTION_CORE" / "talent_intel_preview.py"
OUTPUTS = REPO_ROOT / "outputs"

def die(msg: str, code: int = 1) -> None:
  print(f"❌ {msg}", file=sys.stderr)
  raise SystemExit(code)

def latest_csv() -> Optional[Path]:
  if not OUTPUTS.exists():
    return None
  files = sorted(OUTPUTS.glob("*_CANONICAL.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
  return files[0] if files else None

def role_from_name(p: Path) -> str:
  stem = re.sub(r"_CANONICAL$", "", p.stem, flags=re.I).replace("_", " ").strip()
  return stem.title() if stem else "Unknown Role"

def main(argv: list[str]) -> int:
  if not CORE_PREVIEW.exists():
    die(f"Missing core preview: {CORE_PREVIEW}")

  csv = None
  mode = "demo"
  role = ""

  if len(argv) >= 2 and argv[1].strip():
    csv = Path(argv[1]).expanduser()
    if not csv.is_absolute():
      csv = (REPO_ROOT / csv).resolve()
  else:
    csv = latest_csv()

  if csv is None or not csv.exists():
    die("No CSV provided and no *_CANONICAL.csv found in outputs/")

  if len(argv) >= 3 and argv[2].strip():
    mode = argv[2].strip().lower()
  if mode not in {"demo", "scenario"}:
    mode = "demo"

  if len(argv) >= 4 and argv[3].strip():
    role = argv[3].strip()
  else:
    role = role_from_name(csv)

  cmd = [sys.executable, str(CORE_PREVIEW), str(csv), mode, role]
  return subprocess.call(cmd, cwd=str(REPO_ROOT))

if __name__ == "__main__":
  raise SystemExit(main(sys.argv))
