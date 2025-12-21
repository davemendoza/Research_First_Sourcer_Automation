
 #!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Talent Engine – Track B (Determinative Inference)
Version: v1.0.0
© 2025 L. David Mendoza

DETERMINISTIC, OFFLINE, PYTHON-ONLY.
Consumes Track C–enriched CSV and produces role + tier inference.
"""

import csv
import json
import argparse
import datetime as dt
from collections import defaultdict
from typing import Dict, Any, List


# -------------------------
# Utilities
# -------------------------

def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def write_csv(path: str, rows: List[Dict[str, Any]], headers: List[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def write_json(path: str, obj: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)


def write_text(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def norm(s: str) -> str:
    return (s or "").lower()


# -------------------------
# Inference Logic (minimal v1)
# -------------------------

def infer_role(text: str) -> str:
    if "research" in text or "scientist" in text:
        return "Foundational AI"
    if "infra" in text or "gpu" in text:
        return "AI Infrastructure"
    if "rlhf" in text:
        return "RLHF / Alignment"
    return "Applied AI"


def infer_signals(text: str) -> Dict[str, bool]:
    return {
        "RLHF": "rlhf" in text,
        "VectorDB": any(k in text for k in ("vector", "pinecone", "weaviate", "faiss")),
        "GPU": any(k in text for k in ("cuda", "gpu", "nvidia")),
        "RAG": "rag" in text,
    }


def infer_determinative_tier(role: str, signals: Dict[str, bool]) -> str:
    strong = sum(1 for v in signals.values() if v)
    if strong >= 3:
        return "High"
    if strong == 2:
        return "Medium"
    return "Low"


def infer_signal_tier(signals: Dict[str, bool]) -> str:
    count = sum(1 for v in signals.values() if v)
    return "Strong" if count >= 3 else "Moderate" if count == 2 else "Weak"


# -------------------------
# Main
# -------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-rows", type=int, default=None)
    args = ap.parse_args()

    rows: List[Dict[str, Any]] = []
    audit: List[Dict[str, Any]] = []
    metrics = defaultdict(int)

    with open(args.input, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []

        # Ensure output columns exist
        for col in ("AI_Role_Type", "Determinative_Tier", "Signal_Tier",
                    "RLHF", "VectorDB", "GPU", "RAG"):
            if col not in headers:
                headers.append(col)

        for i, r in enumerate(reader):
            if args.max_rows and i >= args.max_rows:
                break

            text_blob = " ".join(
                norm(str(r.get(k, "")))
                for k in r.keys()
                if k.lower() in ("title", "headline", "skills", "summary", "experience")
            )

            role = infer_role(text_blob)
            signals = infer_signals(text_blob)
            det_tier = infer_determinative_tier(role, signals)
            sig_tier = infer_signal_tier(signals)

            r["AI_Role_Type"] = role
            r["Determinative_Tier"] = det_tier
            r["Signal_Tier"] = sig_tier
            for k, v in signals.items():
                r[k] = "YES" if v else "NO"

            rows.append(r)

            audit.append({
                "row": i + 1,
                "utc": utc_now(),
                "role": role,
                "determinative_tier": det_tier,
                "signal_tier": sig_tier,
                "signals": signals,
            })

            metrics[f"role_{role}"] += 1
            metrics[f"det_{det_tier}"] += 1

    ts = utc_now().replace(":", "").replace("-", "")
    run_dir = f"outputs/run_{ts}_trackB"
    import os
    os.makedirs(run_dir, exist_ok=True)

    log_path = f"{run_dir}/track_b_log.txt"
    audit_path = f"{run_dir}/track_b_audit.json"
    metrics_path = f"{run_dir}/track_b_metrics.json"

    if not args.dry_run:
        write_csv(args.output, rows, headers)
        write_json(audit_path, audit)
        write_text(log_path, f"Rows processed: {len(rows)}\n")
        write_json(metrics_path, metrics)

    print("\nDONE")
    print(f"- Output CSV: {args.output}")
    print(f"- Log: {log_path}")
    print(f"- Audit: {audit_path}")
    print(f"- Metrics: {metrics_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

