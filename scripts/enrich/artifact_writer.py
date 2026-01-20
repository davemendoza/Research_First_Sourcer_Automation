#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Talent Engine – Research-First Sourcer Automation
Module: Artifact Writer
Version: v1.0.0-day2-artifacts
Date: 2025-12-30
Author: Dave Mendoza
© 2025 L. David Mendoza. All Rights Reserved.

Purpose
- Persist discovered artifacts per run
- JSON + CSV outputs
- Append-safe, deterministic ordering
"""

from __future__ import annotations

import csv
import json
import os
import time
from typing import List, Dict


def write_artifacts(run_dir: str, artifacts: List[Dict]) -> None:
    out_dir = os.path.join(run_dir, "artifacts")
    os.makedirs(out_dir, exist_ok=True)

    ts = time.strftime("%Y-%m-%d %H:%M:%S")

    for a in artifacts:
        a["discovered_at"] = ts

    json_path = os.path.join(out_dir, "artifacts.json")
    csv_path = os.path.join(out_dir, "artifacts.csv")

    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(artifacts, jf, indent=2, ensure_ascii=False)

    if artifacts:
        with open(csv_path, "w", encoding="utf-8", newline="") as cf:
            writer = csv.DictWriter(cf, fieldnames=artifacts[0].keys())
            writer.writeheader()
            writer.writerows(artifacts)
