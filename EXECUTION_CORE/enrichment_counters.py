#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enrichment Counters
Tracks cumulative enrichment signals during execution.
"""

import threading
from typing import Dict


class EnrichmentCounters:
    def __init__(self):
        self._lock = threading.Lock()
        self._counters = {
            "emails_found": 0,
            "phones_found": 0,
            "github_io_found": 0,
            "cv_links_found": 0,
            "oss_signals_found": 0,
        }

    def increment(self, key: str, n: int = 1):
        if key not in self._counters:
            return
        with self._lock:
            self._counters[key] += n

    def snapshot(self) -> Dict[str, int]:
        with self._lock:
            return dict(self._counters)
