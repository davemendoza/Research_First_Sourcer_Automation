#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Runtime Tracker
Tracks row progress, elapsed time, ETA, and exposes a thread-safe status snapshot.
"""

import time
import threading
from typing import Dict


class RuntimeTracker:
    def __init__(self, total_rows: int):
        self.total_rows = max(int(total_rows), 0)
        self.start_ts = time.time()
        self.last_update_ts = self.start_ts
        self.rows_completed = 0
        self.lock = threading.Lock()
        self.done = False

    def increment(self, n: int = 1) -> None:
        with self.lock:
            self.rows_completed += n
            self.last_update_ts = time.time()

    def mark_done(self) -> None:
        with self.lock:
            self.done = True
            self.last_update_ts = time.time()

    def snapshot(self) -> Dict[str, float]:
        with self.lock:
            now = time.time()
            elapsed = now - self.start_ts
            rate = self.rows_completed / elapsed if elapsed > 0 else 0.0
            remaining = self.total_rows - self.rows_completed
            eta = remaining / rate if rate > 0 else float("inf")
            return {
                "rows_completed": self.rows_completed,
                "total_rows": self.total_rows,
                "elapsed_sec": elapsed,
                "rows_per_sec": rate,
                "eta_sec": eta,
                "done": self.done,
            }
