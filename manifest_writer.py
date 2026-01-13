#!/usr/bin/env python3
"""
AI Talent Engine — Manifest Writer (Canonical Contract)
© 2025 L. David Mendoza

Non-negotiable contract:
    write_manifest(manifest_path, payload) -> str

This file exists so higher-level runners never drift on manifest plumbing.
No schema logic. No enrichment logic. Just atomic-ish JSON write.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Union


def _atomic_write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write to a temp file in the same directory then replace.
    fd, tmp = tempfile.mkstemp(prefix=".tmp_manifest_", suffix=".json", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(tmp, str(path))
    finally:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass


def write_manifest(manifest_path: Union[str, Path], payload: Dict[str, Any]) -> str:
    p = Path(manifest_path)
    _atomic_write_json(p, payload)
    return str(p)
