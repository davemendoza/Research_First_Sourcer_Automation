#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Talent Engine – Research-First Sourcer Automation
Module: Checkpoints (Resume-on-Crash)
Version: v1.0.0-day1-resilience
Date: 2025-12-30
Author: Dave Mendoza
© 2025 L. David Mendoza. All Rights Reserved.

Purpose
- Provide crash-safe checkpoints for:
  - scenario index / stage
  - seen people
  - seen repos
- Enable safe resume without duplication.

Contract Requirements Satisfied
- Full-file generation only
- Python 3.x
- No partial edits
- Deterministic JSON writes (atomic replace)

Changelog
- v1.0.0: Initial release (atomic JSON checkpointing)

Validation Steps
1) python3 -c "from scripts.ops.checkpoints import CheckpointStore; print('OK')"
2) Create a store, write/read, verify values persist
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


def _atomic_write_json(path: str, payload: Dict[str, Any]) -> None:
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
    os.replace(tmp, path)


@dataclass
class CheckpointStore:
    """
    Minimal checkpoint store.

    Files are JSON dicts, written atomically:
      - run_checkpoint.json
      - seen_people.json
      - seen_repos.json
    """

    root_dir: str
    run_checkpoint_name: str = "run_checkpoint.json"
    seen_people_name: str = "seen_people.json"
    seen_repos_name: str = "seen_repos.json"
    _cache: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def _path(self, name: str) -> str:
        return os.path.join(self.root_dir, name)

    def ensure(self) -> None:
        os.makedirs(self.root_dir, exist_ok=True)

    def load(self, name: str) -> Dict[str, Any]:
        path = self._path(name)
        if path in self._cache:
            return self._cache[path]
        if not os.path.exists(path):
            self._cache[path] = {}
            return self._cache[path]
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    data = {}
        except Exception:
            data = {}
        self._cache[path] = data
        return data

    def save(self, name: str, data: Dict[str, Any]) -> None:
        self.ensure()
        path = self._path(name)
        data = dict(data)
        data["_updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        _atomic_write_json(path, data)
        self._cache[path] = data

    def get_run_state(self) -> Dict[str, Any]:
        return self.load(self.run_checkpoint_name)

    def set_run_state(
        self,
        *,
        stage: str,
        scenario_index: Optional[int] = None,
        notes: Optional[str] = None,
        metrics: Optional[Dict[str, int]] = None,
    ) -> None:
        state = self.get_run_state()
        state["stage"] = str(stage)
        if scenario_index is not None:
            state["scenario_index"] = int(scenario_index)
        if notes is not None:
            state["notes"] = str(notes)
        if metrics is not None:
            state["metrics"] = {str(k): int(v) for k, v in metrics.items()}
        self.save(self.run_checkpoint_name, state)

    def get_seen_people(self) -> Dict[str, Any]:
        return self.load(self.seen_people_name)

    def add_seen_person(self, key: str) -> None:
        data = self.get_seen_people()
        data[str(key)] = True
        self.save(self.seen_people_name, data)

    def get_seen_repos(self) -> Dict[str, Any]:
        return self.load(self.seen_repos_name)

    def add_seen_repo(self, key: str) -> None:
        data = self.get_seen_repos()
        data[str(key)] = True
        self.save(self.seen_repos_name, data)
