#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json

def write_artifact_manifest(
    *,
    run_id: str,
    mode: str,
    scenario: str,
    artifacts: list[dict],
    csv_expected: bool,
    output_dir: Path,
):
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "run_id": run_id,
        "mode": mode,
        "scenario": scenario,
        "csv_expected": csv_expected,
        "artifacts": artifacts,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    }

    path = output_dir / "artifact_manifest.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path
