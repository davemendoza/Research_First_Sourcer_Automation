"""
Phase G IO
Deterministic JSON read/write with atomic writes.
"""

from __future__ import annotations
import json
from pathlib import Path
import shutil
from typing import Any, Dict

def read_json(path: Path) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
    shutil.move(tmp, path)

def write_run_manifest(out_dir: Path, manifest: Dict[str, Any]) -> Path:
    p = out_dir / "scores" / "run_manifest.json"
    atomic_write_json(p, manifest)
    return p
