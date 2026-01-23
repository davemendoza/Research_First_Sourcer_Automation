# ============================================================
#  Research_First_Sourcer_Automation
#  File: EXECUTION_CORE/deep_inference_graph_pass.py
#
#  Purpose:
#    Deep inference graph generation (demo-safe, deterministic).
#    Builds a JSON graph from CSV rows:
#      - Person nodes (GitHub identity)
#      - Repo nodes (repo evidence URLs)
#      - Edge: contributed_to
#
#  Contract:
#    run(input_csv: str, output_csv: str) -> None
#
#  Version: v1.8.0-deep-graph
#  Author: Dave Mendoza
# ============================================================

from __future__ import annotations

import csv
import hashlib
import json
import os
from typing import Dict, List, Tuple

PIPELINE_VERSION = "v1.8.0-deep-graph"

def run(input_csv: str, output_csv: str) -> None:
    rows, cols = _read_rows(input_csv)
    if not rows:
        _write_header_only(output_csv, cols)
        return

    graph_path = _sidecar_graph_path(output_csv)
    graph = _build_graph(rows)
    _write_json(graph_path, graph)

    if "Graph_Evidence_JSON" not in cols:
        cols.append("Graph_Evidence_JSON")

    out_rows: List[Dict[str, str]] = []
    for r in rows:
        rr = dict(r)
        rr["Graph_Evidence_JSON"] = json.dumps(
            {
                "graph_sidecar_path": os.path.abspath(graph_path),
                "graph_version": PIPELINE_VERSION,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        out_rows.append(rr)

    _write_rows(output_csv, out_rows, cols)

def _build_graph(rows: List[Dict[str, str]]) -> Dict[str, object]:
    nodes: Dict[str, Dict[str, object]] = {}
    edges: List[Dict[str, object]] = []

    for r in rows:
        gh_user = (r.get("GitHub_Username") or "").strip()
        gh_url = (r.get("GitHub_Profile_URL") or r.get("GitHub_URL") or "").strip()
        repo_urls = (r.get("Repo_Evidence_URLs") or "").strip()

        if gh_user:
            pid = _node_id("person", gh_user.lower())
            if pid not in nodes:
                nodes[pid] = {
                    "id": pid,
                    "type": "person",
                    "github_username": gh_user,
                    "github_url": gh_url,
                }

            if repo_urls and "github.com/" in repo_urls:
                rid = _node_id("repo", repo_urls.lower())
                if rid not in nodes:
                    nodes[rid] = {"id": rid, "type": "repo", "url": repo_urls}
                edges.append(
                    {
                        "type": "contributed_to",
                        "from": pid,
                        "to": rid,
                        "evidence_url": repo_urls,
                    }
                )

    return {
        "version": PIPELINE_VERSION,
        "nodes": list(nodes.values()),
        "edges": edges,
    }

def _node_id(prefix: str, key: str) -> str:
    h = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{h}"

def _sidecar_graph_path(output_csv: str) -> str:
    base = output_csv[:-4] if output_csv.lower().endswith(".csv") else output_csv
    return base + ".graph.json"

def _write_json(path: str, data: Dict[str, object]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _read_rows(path: str) -> Tuple[List[Dict[str, str]], List[str]]:
    if not path or not os.path.exists(path):
        return [], []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        cols = list(reader.fieldnames or [])
        if not cols:
            return [], []
        rows: List[Dict[str, str]] = []
        for row in reader:
            if row and any((vv or "").strip() for vv in row.values()):
                rows.append({k: (v if v is not None else "") for k, v in row.items()})
        return rows, cols

def _write_header_only(path: str, cols: List[str]) -> None:
    _write_rows(path, [], cols)

def _write_rows(path: str, rows: List[Dict[str, str]], cols: List[str]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow({c: ("" if r.get(c) is None else str(r.get(c, ""))) for c in cols})
