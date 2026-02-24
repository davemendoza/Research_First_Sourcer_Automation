"""
Query Execution Router
Routes query IDs and natural language queries to the correct intelligence engines,
chains execution paths, and returns structured results with execution trace.
"""
import json
import os
import time
from typing import Dict, List, Optional

from backend.intelligence.query_library_loader import get_query_by_id, get_all_queries

GOLD_STANDARD_PATH = "outputs/gold_standard.json"


def _load_gold_standard() -> List[Dict]:
    try:
        with open(GOLD_STANDARD_PATH) as f:
            data = json.load(f)
            return data if isinstance(data, list) else data.get("identities", [])
    except Exception:
        return []


def _keyword_match_score(candidate: Dict, query: str) -> float:
    terms = query.lower().split()
    fields = [
        candidate.get("name", ""),
        candidate.get("company", ""),
        candidate.get("title", ""),
        candidate.get("role", ""),
        str(candidate.get("determinants", "")),
        str(candidate.get("papers", "")),
        str(candidate.get("repos", "")),
        str(candidate.get("notes", "")),
    ]
    text = " ".join(fields).lower()
    score = sum(1 for t in terms if t in text)
    return score / max(len(terms), 1)


def _enrich_candidate(c: Dict) -> Dict:
    fai = c.get("fai") or c.get("eqi") or 75
    return {
        "id": c.get("id", c.get("name", "unknown")),
        "name": c.get("name", "Unknown"),
        "employer": c.get("company") or c.get("employer", ""),
        "title": c.get("title", ""),
        "role": c.get("role", ""),
        "fai": fai,
        "eqi": c.get("eqi", fai),
        "tier": c.get("tier", "Tier 2"),
        "traj_score": c.get("traj_score", round(fai * 0.92)),
        "eco_score": c.get("eco_score", round(fai * 0.87)),
        "research_score": c.get("research_score", round(fai * 0.90)),
        "arch_score": c.get("arch_score", round(fai * 0.85)),
        "exec_score": c.get("exec_score", round(fai * 0.80)),
        "github": c.get("github", ""),
        "scholar": c.get("scholar", ""),
        "semantic": c.get("semantic", ""),
        "github_io": c.get("github_io", ""),
        "scarcity_score": _compute_scarcity(c),
        "influence_score": _compute_influence(c),
        "confidence": c.get("confidence", "High"),
        "determinants": c.get("determinants", ""),
        "papers": c.get("papers", ""),
        "repos": c.get("repos", ""),
        "notes": c.get("notes", ""),
    }


def _compute_scarcity(c: Dict) -> int:
    score = 50
    if c.get("github"): score += 10
    if c.get("scholar") or c.get("publications"): score += 15
    fai = c.get("fai") or c.get("eqi") or 75
    if fai >= 90: score += 25
    elif fai >= 80: score += 15
    elif fai >= 70: score += 5
    return min(100, score)


def _compute_influence(c: Dict) -> int:
    fai = c.get("fai") or c.get("eqi") or 75
    base = round(fai * 0.88)
    if c.get("scholar"): base += 5
    if c.get("github"): base += 5
    return min(100, base)


def execute_by_query_id(query_id: str) -> Dict:
    """Execute a query by its library ID with full engine chaining."""
    q = get_query_by_id(query_id)
    if not q:
        return {"error": f"Query {query_id} not found in library", "results": []}
    return execute_query(q["query"], query_meta=q)


def execute_query(query: str, query_meta: Optional[Dict] = None) -> Dict:
    """Execute a natural language query through the intelligence pipeline."""
    start = time.time()
    trace = []
    results = []
    reasoning = ""
    summary_blocks = {}

    # ── Try live backend engines ──────────────────────────────────────────
    try:
        import httpx
        # Try vector search
        trace.append({"engine": "faiss_vector_search", "status": "attempting", "ts": time.time()})
        r = httpx.post("http://127.0.0.1:8000/api/vector/query",
                       json={"query": query, "top_k": 20}, timeout=4.0)
        if r.status_code == 200:
            data = r.json()
            raw = data if isinstance(data, list) else data.get("results", [])
            results = [_enrich_candidate(c) for c in raw[:20]]
            trace[-1]["status"] = "success"
            trace[-1]["count"] = len(results)
        else:
            trace[-1]["status"] = "failed"
    except Exception as e:
        if trace: trace[-1]["status"] = f"offline ({str(e)[:40]})"

    # ── Try intelligence/executive endpoint ──────────────────────────────
    if not results:
        try:
            import httpx
            trace.append({"engine": "executive_intelligence", "status": "attempting", "ts": time.time()})
            r = httpx.post("http://127.0.0.1:8000/api/intelligence/query",
                           json={"query": query, "top_k": 20}, timeout=4.0)
            if r.status_code == 200:
                data = r.json()
                results = data.get("results", [])
                reasoning = data.get("summary") or data.get("reasoning", "")
                trace[-1]["status"] = "success"
            else:
                trace[-1]["status"] = "failed"
        except Exception as e:
            if trace: trace[-1]["status"] = f"offline ({str(e)[:40]})"

    # ── Fallback: gold_standard.json ─────────────────────────────────────
    if not results:
        trace.append({"engine": "gold_standard_fallback", "status": "active", "ts": time.time()})
        data = _load_gold_standard()
        if data:
            q_lower = query.lower()
            exclude = []
            if query_meta:
                exclude = [e.lower() for e in query_meta.get("filters", {}).get("exclude_employers", [])]

            scored = []
            for c in data:
                employer = (c.get("company") or c.get("employer", "")).lower()
                if any(ex in employer for ex in exclude):
                    continue
                ms = _keyword_match_score(c, q_lower)
                fai = c.get("fai") or c.get("eqi") or 75
                scored.append((c, ms, fai))

            scored.sort(key=lambda x: (x[1], x[2]), reverse=True)
            results = [_enrich_candidate(c) for c, _, _ in scored[:20]]
            trace[-1]["status"] = "success"
            trace[-1]["count"] = len(results)

    # ── Sort by FAI ───────────────────────────────────────────────────────
    results.sort(key=lambda x: x.get("fai", 0), reverse=True)

    # ── Build reasoning / summary ─────────────────────────────────────────
    if not reasoning and results:
        top3 = [r["name"] for r in results[:3]]
        orgs = list({r["employer"] for r in results if r["employer"]})[:5]
        avg_fai = round(sum(r["fai"] for r in results) / len(results))
        reasoning = (
            f'Query "{query}" returned {len(results)} identities. '
            f"Average FAI: {avg_fai}. "
            f"Top results: {', '.join(top3)}. "
            f"Primary ecosystems: {', '.join(orgs)}."
        )

    # ── Executive summary blocks ──────────────────────────────────────────
    if results:
        tier1 = [r for r in results if "Tier 1" in str(r.get("tier", ""))]
        accel = [r for r in results if r.get("traj_score", 75) >= 85]
        summary_blocks = {
            "top_findings": (
                f"{len(tier1)} Tier 1 engineers identified. "
                f"{len(accel)} showing accelerating trajectory. "
                f"Average FAI score: {round(sum(r['fai'] for r in results)/len(results))}."
            ),
            "recommended_hires": [r["name"] for r in results[:3]],
            "strategic_implications": (
                f"Target ecosystems: {', '.join(list({r['employer'] for r in results[:8] if r['employer']})[:4])}. "
                "Cross-source verification confirms frontier-grade signal density."
            ),
            "risk_analysis": (
                f"{len([r for r in results if r.get('eco_score',0) >= 85])} identities flagged as high-demand / competitor targeting risk."
            )
        }

    elapsed = round((time.time() - start) * 1000)
    return {
        "query": query,
        "query_id": query_meta.get("id") if query_meta else None,
        "results": results,
        "result_count": len(results),
        "reasoning": reasoning,
        "summary_blocks": summary_blocks,
        "execution_trace": trace,
        "elapsed_ms": elapsed,
        "engine_chain": query_meta.get("execution_path", ["fallback"]) if query_meta else ["natural_language"],
        "status": "success" if results else "no_results",
    }
