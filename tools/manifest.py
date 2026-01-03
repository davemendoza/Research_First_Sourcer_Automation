#!/usr/bin/env python3
"""
AI Talent Engine — Run Manifest Writer
© 2025 L. David Mendoza
Version: v1.0.0
"""
from __future__ import annotations
import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Dict, Any

def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def write_manifest(manifest_path: str, payload: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)

def build_manifest(run_id: str, scenario: str, mode: str, artifacts: Dict[str, str]) -> Dict[str, Any]:
    hashed = {}
    for k, p in artifacts.items():
        if p and os.path.exists(p):
            hashed[k] = {"path": p, "sha256": _sha256_file(p)}
        else:
            hashed[k] = {"path": p, "sha256": None}
    return {
        "run_id": run_id,
        "scenario": scenario,
        "mode": mode,
        "created_utc": utc_now(),
        "artifacts": hashed
    }
