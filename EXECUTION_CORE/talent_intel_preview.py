#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Talent Intelligence Preview
Live aggregated preview printed during execution.
"""

import time
from typing import Callable


class TalentIntelPreview:
    def __init__(
        self,
        runtime_snapshot_fn: Callable[[], dict],
        counters_snapshot_fn: Callable[[], dict],
        interval_sec: int = 60,
    ):
        self.runtime_snapshot_fn = runtime_snapshot_fn
        self.counters_snapshot_fn = counters_snapshot_fn
        self.interval_sec = interval_sec
        self._last_emit = 0.0

    def maybe_emit(self):
        now = time.time()
        if now - self._last_emit < self.interval_sec:
            return
        self._last_emit = now

        rt = self.runtime_snapshot_fn()
        cnt = self.counters_snapshot_fn()

        print(
            "[TALENT PREVIEW] "
            f"rows={rt['rows_completed']}/{rt['total_rows']} | "
            f"emails={cnt['emails_found']} "
            f"phones={cnt['phones_found']} "
            f"github.io={cnt['github_io_found']} "
            f"cv={cnt['cv_links_found']} "
            f"oss={cnt['oss_signals_found']}",
            flush=True,
        )
