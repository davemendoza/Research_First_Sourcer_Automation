#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Progress Heartbeat
Emits periodic status so long runs never look frozen.
"""

import threading
import time
from typing import Callable


class ProgressHeartbeat(threading.Thread):
    def __init__(self, snapshot_fn: Callable[[], dict], interval_sec: int = 30):
        super().__init__(daemon=True)
        self.snapshot_fn = snapshot_fn
        self.interval_sec = interval_sec
        self._stop = threading.Event()

    def run(self):
        while not self._stop.is_set():
            snap = self.snapshot_fn()
            if snap:
                eta = snap["eta_sec"]
                eta_str = "∞" if eta == float("inf") else f"{int(eta // 60)}m {int(eta % 60)}s"
                print(
                    f"[HEARTBEAT] {snap['rows_completed']}/{snap['total_rows']} "
                    f"elapsed={int(snap['elapsed_sec'])}s "
                    f"ETA={eta_str}",
                    flush=True,
                )
            time.sleep(self.interval_sec)

    def stop(self):
        self._stop.set()
