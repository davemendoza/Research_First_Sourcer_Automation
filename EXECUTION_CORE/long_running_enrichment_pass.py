# ============================================================
#  long_running_enrichment_pass.py
#  FIXED: defines CACHE_DIR deterministically
# ============================================================

from __future__ import annotations

import os
import csv
import time
from typing import Dict, Any

# -----------------------------
# REQUIRED FIX (was missing)
# -----------------------------
CACHE_DIR = os.path.join("outputs", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# ------------------------------------------------------------
# Existing logic below (UNCHANGED)
# ------------------------------------------------------------

def run(input_csv: str, output_csv: str) -> None:
    rows = []
    with open(input_csv, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    # Simulated long-running enrichment
    enriched = []
    for r in rows:
        time.sleep(0.01)  # preserve timing semantics
        r = dict(r)
        r.setdefault("Enrichment_Status", "complete")
        enriched.append(r)

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=enriched[0].keys())
        w.writeheader()
        for r in enriched:
            w.writerow(r)
