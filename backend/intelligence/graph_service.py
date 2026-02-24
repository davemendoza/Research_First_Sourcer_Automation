# ============================================================
# AI TALENT ENGINE - SIGNAL INTELLIGENCE PLATFORM
# © 2026 L. David Mendoza. All Rights Reserved.
# ============================================================
"""
backend/intelligence/graph_service.py

ExecutiveGraphService: loads real identity and intelligence graph artifacts from backend/storage
and exposes normalized nodes/edges for the Executive Intelligence Console.

Data sources (real, on-disk):
- backend/storage/identity_graph.json
- backend/storage/ecosystem_state_store.json (optional)
- backend/storage/signal_history_store.json (optional)
- backend/storage/trajectory_store.json (optional)
- backend/storage/intelligence_cache.json (optional)

This intentionally avoids placeholder data. If a file is missing, it returns empty arrays plus
a diagnostics block so the UI can show what is missing instead of going blank.

Version: v6.0.1
Changelog:
- v6.0.1 (2026-02-21): Introduce normalized real-data loaders and stable graph contract.
- v6.0.0: Hyperscale v6 baseline.

Validation:
- python3 -c "from backend.intelligence.graph_service import ExecutiveGraphService; print(ExecutiveGraphService().get_summary())"

Git:
- git add backend/intelligence/graph_service.py
- git commit -m "Fix: executive graph service real-data loaders"
- git push
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


ROOT = _repo_root()
STORAGE_DIR = ROOT / "backend" / "storage"


class ExecutiveGraphService:
    def __init__(self) -> None:
        self.storage_dir = STORAGE_DIR

    def _read_json(self, path: Path) -> Tuple[bool, Any, str]:
        try:
            if not path.exists():
                return False, None, f"missing: {path}"
            raw = path.read_text(encoding="utf-8")
            return True, json.loads(raw), ""
        except Exception as e:
            return False, None, f"error reading {path}: {e}"

    def _normalize_identity_graph(self, data: Any) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Accepts common shapes:
        - { "nodes": [...], "edges": [...] }
        - { "identities": [...], "links": [...] }
        - { ... } unknown -> empty
        """
        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, Any]] = []

        if isinstance(data, dict):
            if isinstance(data.get("nodes"), list):
                nodes = [self._norm_node(x) for x in data.get("nodes", []) if isinstance(x, dict)]
                edges = [self._norm_edge(x) for x in data.get("edges", []) if isinstance(x, dict)]
            elif isinstance(data.get("identities"), list):
                nodes = [self._norm_node(x) for x in data.get("identities", []) if isinstance(x, dict)]
                edges = [self._norm_edge(x) for x in data.get("links", []) if isinstance(x, dict)]
            elif isinstance(data.get("people"), list):
                nodes = [self._norm_node(x) for x in data.get("people", []) if isinstance(x, dict)]
                edges = [self._norm_edge(x) for x in data.get("edges", []) if isinstance(x, dict)]
        elif isinstance(data, list):
            # If identity graph is a list of people objects
            nodes = [self._norm_node(x) for x in data if isinstance(x, dict)]

        # Remove empty ids
        nodes = [n for n in nodes if n.get("id")]
        edges = [e for e in edges if e.get("source") and e.get("target")]

        return nodes, edges

    def _norm_node(self, n: Dict[str, Any]) -> Dict[str, Any]:
        node_id = n.get("id") or n.get("Identity_Key") or n.get("identity_key") or n.get("person_id") or n.get("Person_ID") or n.get("key")
        label = n.get("label") or n.get("name") or n.get("Name") or n.get("full_name") or n.get("handle") or node_id
        company = n.get("company") or n.get("Company") or n.get("org") or n.get("organization")
        role = n.get("role") or n.get("Role") or n.get("title") or n.get("Title")
        cluster = n.get("cluster") or n.get("ecosystem_cluster") or n.get("ecosystem") or n.get("Cluster")

        out = dict(n)
        out["id"] = str(node_id) if node_id is not None else ""
        out["label"] = str(label) if label is not None else out["id"]
        if company is not None:
            out["company"] = company
        if role is not None:
            out["role"] = role
        if cluster is not None:
            out["cluster"] = cluster
        return out

    def _norm_edge(self, e: Dict[str, Any]) -> Dict[str, Any]:
        src = e.get("source") or e.get("src") or e.get("from") or e.get("a")
        tgt = e.get("target") or e.get("dst") or e.get("to") or e.get("b")
        rel = e.get("type") or e.get("relationship") or e.get("rel") or e.get("label") or "link"
        weight = e.get("weight") or e.get("score") or 1

        out = dict(e)
        out["source"] = str(src) if src is not None else ""
        out["target"] = str(tgt) if tgt is not None else ""
        out["type"] = str(rel)
        out["weight"] = weight
        return out

    def get_graph(self) -> Dict[str, Any]:
        diag: Dict[str, Any] = {"storage_dir": str(self.storage_dir), "files": {}}

        identity_path = self.storage_dir / "identity_graph.json"
        ok, data, err = self._read_json(identity_path)
        diag["files"]["identity_graph.json"] = {"ok": ok, "error": err}

        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, Any]] = []

        if ok:
            nodes, edges = self._normalize_identity_graph(data)

        # Optional enrichment overlays
        overlays = {}
        for fname in [
            "ecosystem_state_store.json",
            "signal_history_store.json",
            "trajectory_store.json",
            "intelligence_cache.json",
        ]:
            p = self.storage_dir / fname
            ok2, data2, err2 = self._read_json(p)
            diag["files"][fname] = {"ok": ok2, "error": err2}
            if ok2:
                overlays[fname] = data2

        return {
            "nodes": nodes,
            "edges": edges,
            "overlays": overlays,
            "diagnostics": diag,
        }

    def get_identities(self) -> List[Dict[str, Any]]:
        g = self.get_graph()
        nodes = g.get("nodes", [])
        # Return a compact identity list for executive tables
        out: List[Dict[str, Any]] = []
        for n in nodes:
            out.append(
                {
                    "id": n.get("id"),
                    "label": n.get("label"),
                    "company": n.get("company"),
                    "role": n.get("role"),
                    "cluster": n.get("cluster"),
                }
            )
        return out

    def get_summary(self) -> Dict[str, Any]:
        g = self.get_graph()
        nodes = g.get("nodes", [])
        edges = g.get("edges", [])
        overlays = g.get("overlays", {}) or {}

        clusters: Dict[str, int] = {}
        companies: Dict[str, int] = {}
        for n in nodes:
            c = n.get("cluster") or "Unclustered"
            clusters[str(c)] = clusters.get(str(c), 0) + 1
            comp = n.get("company")
            if comp:
                companies[str(comp)] = companies.get(str(comp), 0) + 1

        top_clusters = sorted(clusters.items(), key=lambda x: x[1], reverse=True)[:25]
        top_companies = sorted(companies.items(), key=lambda x: x[1], reverse=True)[:25]

        return {
            "counts": {
                "nodes": len(nodes),
                "edges": len(edges),
                "overlay_files_loaded": len(overlays.keys()),
            },
            "top_clusters": [{"cluster": k, "count": v} for k, v in top_clusters],
            "top_companies": [{"company": k, "count": v} for k, v in top_companies],
            "diagnostics": g.get("diagnostics", {}),
        }

    def get_telemetry_summary(self) -> Dict[str, Any]:
        """
        Best effort telemetry summary:
        - If backend/storage/telemetry.json exists, use it.
        - Else if backend/storage/backend_autoreload.log exists, return last lines count only.
        """
        telemetry_path = self.storage_dir / "telemetry.json"
        ok, data, err = self._read_json(telemetry_path)
        if ok and isinstance(data, dict):
            return {"source": "telemetry.json", "telemetry": data}

        # Fallback: do not fabricate events, only return diagnostics
        log_path = ROOT / "backend_autoreload.log"
        if log_path.exists():
            try:
                lines = log_path.read_text(encoding="utf-8", errors="ignore").splitlines()
                tail = lines[-50:]
                return {"source": "backend_autoreload.log", "lines_total": len(lines), "tail": tail}
            except Exception as e:
                return {"source": "backend_autoreload.log", "error": str(e)}

        return {"source": "none", "error": f"telemetry unavailable ({err})"}
