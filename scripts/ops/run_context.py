#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Talent Engine – Research-First Sourcer Automation
Module: Run Context + Manifest
Version: v1.0.0-day1-runcontext
Date: 2025-12-30
Author: Dave Mendoza
© 2025 L. David Mendoza. All Rights Reserved.

Purpose
- Standardize run boundary and canonical output layout.
- Create per-run folders under output/people/run_<timestamp>/.
- Write a run_manifest.json capturing inputs, outputs, and metrics.

Contract Requirements Satisfied
- Full-file generation
- Deterministic outputs
- No side effects outside declared output directory

Validation Steps
1) python3 -c "from scripts.ops.run_context import RunContext; print('OK')"
2) Create a context and ensure dirs/manifest are written.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


def _now_run_id() -> str:
    return time.strftime("run_%Y%m%d_%H%M%S")


def _atomic_write_json(path: str, payload: Dict[str, Any]) -> None:
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
    os.replace(tmp, path)


@dataclass
class RunContext:
    project_root: str
    run_id: str = field(default_factory=_now_run_id)
    out_root: str = "output"
    people_root: str = "people"

    def run_dir(self) -> str:
        return os.path.join(self.project_root, self.out_root, self.people_root, self.run_id)

    def demo_dir(self) -> str:
        return os.path.join(self.run_dir(), "demo_results")

    def checkpoints_dir(self) -> str:
        return os.path.join(self.run_dir(), "checkpoints")

    def manifest_path(self) -> str:
        return os.path.join(self.run_dir(), "run_manifest.json")

    def ensure_dirs(self) -> None:
        os.makedirs(self.run_dir(), exist_ok=True)
        os.makedirs(self.demo_dir(), exist_ok=True)
        os.makedirs(self.checkpoints_dir(), exist_ok=True)

    def write_manifest(
        self,
        *,
        status: str,
        metrics: Optional[Dict[str, int]] = None,
        notes: Optional[str] = None,
        inputs: Optional[Dict[str, str]] = None,
        outputs: Optional[Dict[str, str]] = None,
    ) -> None:
        self.ensure_dirs()
        payload: Dict[str, Any] = {
            "run_id": self.run_id,
            "status": status,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "project_root": self.project_root,
            "run_dir": self.run_dir(),
        }
        if metrics:
            payload["metrics"] = {str(k): int(v) for k, v in metrics.items()}
        if notes:
            payload["notes"] = str(notes)
        if inputs:
            payload["inputs"] = {str(k): str(v) for k, v in inputs.items()}
        if outputs:
            payload["outputs"] = {str(k): str(v) for k, v in outputs.items()}
        _atomic_write_json(self.manifest_path(), payload)
