#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/runtime_tracker.py
============================================================
STAGE TIMING + ETA (DETERMINISTIC, LOCAL)

Maintainer: L. David Mendoza © 2026
Version: v1.0.0

Purpose
- Track per-stage durations
- Estimate remaining time using rolling averages stored locally
- Never affects pipeline success (fail-open)

Storage
- OUTPUTS/_ARCHIVE_INTERNAL/runtime_history.json

Validation
python3 -c "from EXECUTION_CORE.runtime_tracker import RuntimeTracker; t=RuntimeTracker('.', 'demo', 'x'); t.start('a'); t.end('a'); print('ok')"

Git Commands
git add EXECUTION_CORE/runtime_tracker.py
git commit -m "Add stage timing + ETA tracker (fail-open)"
git push
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Any


class RuntimeTracker:
    def __init__(self, repo_root: str | Path, mode: str, role: str) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.mode = (mode or "demo").strip().lower()
        self.role = (role or "").strip()
        self._t0 = time.time()
        self._stage_start: Dict[str, float] = {}
        self._durations: Dict[str, float] = {}

        hist_dir = (self.repo_root / "OUTPUTS" / "_ARCHIVE_INTERNAL").resolve()
        hist_dir.mkdir(parents=True, exist_ok=True)
        self.hist_path = (hist_dir / "runtime_history.json").resolve()

        self.history = self._load_history()

    def _load_history(self) -> Dict[str, Any]:
        if not self.hist_path.exists():
            return {}
        try:
            obj = json.loads(self.hist_path.read_text(encoding="utf-8"))
            return obj if isinstance(obj, dict) else {}
        except Exception:
            return {}

    def _save_history(self) -> None:
        try:
            self.hist_path.write_text(json.dumps(self.history, indent=2, sort_keys=True), encoding="utf-8")
        except Exception:
            pass

    def start(self, stage: str) -> None:
        self._stage_start[stage] = time.time()

    def end(self, stage: str) -> float:
        t1 = time.time()
        t0 = self._stage_start.get(stage, t1)
        dur = max(0.0, t1 - t0)
        self._durations[stage] = dur

        key = f"{self.mode}:{stage}"
        arr = self.history.get(key, [])
        if not isinstance(arr, list):
            arr = []
        arr.append(dur)
        arr = arr[-20:]
        self.history[key] = arr
        self._save_history()
        return dur

    def elapsed(self) -> float:
        return max(0.0, time.time() - self._t0)

    def estimate_remaining(self, remaining_stages: list[str]) -> float:
        est = 0.0
        for st in remaining_stages:
            key = f"{self.mode}:{st}"
            arr = self.history.get(key, [])
            if isinstance(arr, list) and arr:
                est += float(sum(arr) / len(arr))
            else:
                est += 5.0
        return est

    @staticmethod
    def fmt(seconds: float) -> str:
        s = int(max(0, seconds))
        h = s // 3600
        m = (s % 3600) // 60
        ss = s % 60
        if h > 0:
            return f"{h:02d}:{m:02d}:{ss:02d}"
        return f"{m:02d}:{ss:02d}"
