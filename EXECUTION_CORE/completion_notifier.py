#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Completion Notifier
Explicit terminal notification on run completion.
"""

import time


def notify_completion(runtime_snapshot: dict):
    elapsed = int(runtime_snapshot.get("elapsed_sec", 0))
    mins = elapsed // 60
    secs = elapsed % 60

    banner = "=" * 72
    print(banner)
    print(" RUN COMPLETE ")
    print(f" Elapsed time: {mins}m {secs}s")
    print(f" Rows processed: {runtime_snapshot.get('rows_completed')}")
    print(banner, flush=True)
