#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Talent Engine – Research-First Sourcer Automation
Module: Progress Tracker (Non-Spam, Interval-Based)
Version: v1.0.0-day1-instrumentation
Date: 2025-12-30
Author: Dave Mendoza
© 2025 L. David Mendoza. All Rights Reserved.

Purpose
- Provide interval-based progress reporting for long-running jobs.
- Prevent per-item log spam.
- Support executive-safe, interview-safe runtime visibility.

Contract Requirements Satisfied
- Python 3.x
- Deterministic output
- No external side effects beyond stdout
- Safe to import anywhere

Changelog
- v1.0.0: Initial release (interval-based progress, ETA estimate)

Validation Steps
1) python3 -c "from scripts.ops.progress_tracker import ProgressTracker; print('OK')"
2) Ensure no per-item spam occurs (only interval-based updates)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class ProgressSnapshot:
    scenarios_processed: int = 0
    scenarios_total: Optional[int] = None
    people_discovered: int = 0
    repos_scanned: int = 0
    stage: str = "init"
    extra: Dict[str, int] = field(default_factory=dict)


class ProgressTracker:
    """
    Interval-based progress tracker.

    Usage:
        pt = ProgressTracker(interval_seconds=20)
        pt.update(stage="people_enum", people_discovered=120)
        pt.maybe_emit()
    """

    def __init__(self, interval_seconds: int = 20, prefix: str = "⏱️  PROGRESS"):
        self.interval_seconds = max(5, int(interval_seconds))
        self.prefix = prefix
        self._last_emit = 0.0
        self._start = time.time()
        self.snapshot = ProgressSnapshot()

    def update(
        self,
        *,
        stage: Optional[str] = None,
        scenarios_processed: Optional[int] = None,
        scenarios_total: Optional[int] = None,
        people_discovered: Optional[int] = None,
        repos_scanned: Optional[int] = None,
        extra: Optional[Dict[str, int]] = None,
    ) -> None:
        if stage is not None:
            self.snapshot.stage = stage
        if scenarios_processed is not None:
            self.snapshot.scenarios_processed = int(scenarios_processed)
        if scenarios_total is not None:
            self.snapshot.scenarios_total = int(scenarios_total)
        if people_discovered is not None:
            self.snapshot.people_discovered = int(people_discovered)
        if repos_scanned is not None:
            self.snapshot.repos_scanned = int(repos_scanned)
        if extra:
            for k, v in extra.items():
                self.snapshot.extra[str(k)] = int(v)

    def _eta_seconds(self) -> Optional[int]:
        total = self.snapshot.scenarios_total
        done = self.snapshot.scenarios_processed
        if total is None or total <= 0 or done <= 0 or done > total:
            return None
        elapsed = time.time() - self._start
        rate = done / elapsed if elapsed > 0 else 0
        if rate <= 0:
            return None
        remaining = total - done
        return int(remaining / rate)

    @staticmethod
    def _fmt_hms(seconds: int) -> str:
        seconds = max(0, int(seconds))
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        if h > 0:
            return f"{h}h {m}m {s}s"
        if m > 0:
            return f"{m}m {s}s"
        return f"{s}s"

    def maybe_emit(self, force: bool = False) -> None:
        now = time.time()
        if not force and (now - self._last_emit) < self.interval_seconds:
            return
        self._last_emit = now

        elapsed = int(now - self._start)
        eta = self._eta_seconds()

        parts = [
            f"{self.prefix}",
            f"stage={self.snapshot.stage}",
            f"elapsed={self._fmt_hms(elapsed)}",
            f"people={self.snapshot.people_discovered}",
            f"repos={self.snapshot.repos_scanned}",
        ]
        if self.snapshot.scenarios_total is not None:
            parts.append(f"scenarios={self.snapshot.scenarios_processed}/{self.snapshot.scenarios_total}")
        else:
            parts.append(f"scenarios={self.snapshot.scenarios_processed}")

        if eta is not None:
            parts.append(f"eta={self._fmt_hms(eta)}")

        if self.snapshot.extra:
            extras = " ".join([f"{k}={v}" for k, v in sorted(self.snapshot.extra.items())])
            parts.append(extras)

        print(" | ".join(parts), flush=True)
