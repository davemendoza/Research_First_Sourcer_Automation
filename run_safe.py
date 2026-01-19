#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
CORE = REPO_ROOT / "EXECUTION_CORE" / "run_safe.py"

def die(msg: str, code: int = 1) -> None:
  print(f"❌ {msg}", file=sys.stderr)
  raise SystemExit(code)

def main(argv: list[str]) -> int:
  if not CORE.exists():
    die(f"Missing core runner: {CORE}")

  if len(argv) < 2:
    die("Usage: run_safe.py <scenario_slug> [demo|scenario]")

  scenario = argv[1].strip()
  mode = argv[2].strip().lower() if len(argv) >= 3 else "scenario"
  if mode not in {"demo", "scenario"}:
    die("Mode must be demo or scenario")

  env = os.environ.copy()
  env["RFS_MODE"] = mode

  # Core runner should take scenario only; mode is passed via env.
  cmd = [sys.executable, str(CORE), scenario]
  return subprocess.call(cmd, cwd=str(REPO_ROOT), env=env)

if __name__ == "__main__":
  raise SystemExit(main(sys.argv))
