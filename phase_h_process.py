"""
Phase H Process Runner
- Runs child scripts deterministically using subprocess
- Captures stdout/stderr
- Enforces non-zero exit stop unless --continue-on-error
"""

from __future__ import annotations
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any

@dataclass
class StepResult:
    name: str
    cmd: List[str]
    returncode: int
    stdout: str
    stderr: str

def run_step(
    name: str,
    cmd: List[str],
    cwd: Path,
    env: Optional[Dict[str, str]] = None,
    timeout_s: Optional[int] = None
) -> StepResult:
    p = subprocess.run(
        cmd,
        cwd=str(cwd),
        env=env,
        text=True,
        capture_output=True,
        timeout=timeout_s
    )
    return StepResult(
        name=name,
        cmd=cmd,
        returncode=p.returncode,
        stdout=p.stdout or "",
        stderr=p.stderr or ""
    )
