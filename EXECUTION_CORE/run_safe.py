#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
run_safe.py
Universal runner with timestamped outputs and auto-open.

© 2026 L. David Mendoza
"""

import sys, subprocess
from pathlib import Path
from datetime import datetime
from people_scenario_resolver import resolve_people_run

BASE=Path(__file__).resolve().parent
OUT=BASE/"outputs"/"people"

def ts(): return datetime.utcnow().strftime("%Y%m%d_%H%M%S")

def open_file(p: Path):
    try: subprocess.run(["open", str(p)], check=False)
    except Exception: pass

def main():
    if len(sys.argv)<3:
        print("Usage: python3 run_safe.py <demo|scenario|gpt_slim> <role>")
        sys.exit(1)
    mode, role = sys.argv[1].lower(), sys.argv[2].lower()
    df=resolve_people_run(mode, role)
    OUT.mkdir(parents=True, exist_ok=True)
    out=OUT/f"{role}_{mode}_{ts()}.csv"
    df.to_csv(out, index=False)
    print(f"rows: {len(df)}  cols: {df.shape[1]}  file: {out}")
    open_file(out)

if __name__=="__main__":
    main()
