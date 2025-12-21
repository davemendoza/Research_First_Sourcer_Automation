"""
Phase H IO — manifests and safe JSON writes
"""

from __future__ import annotations
import json
from pathlib import Path
import shutil
from typing import Any, Dict

def atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
    shutil.move(tmp, path)

def write_manifest(manifests_dir: Path, name: str, payload: Dict[str, Any]) -> Path:
    p = manifests_dir / name
    atomic_write_json(p, payload)
    return p
