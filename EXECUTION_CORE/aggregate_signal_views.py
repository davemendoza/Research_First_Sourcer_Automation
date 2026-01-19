#!/usr/bin/env python3
"""
EXECUTION_CORE/aggregate_signal_views.py
============================================================
AGGREGATION LAYER (DAY 6 — POLICY-READY FACTS)

PURPOSE
- Aggregate in-memory rows into deterministic, policy-ready facts
- Emit normalized density inputs consumable by Day 7 policy
- Preserve strict separation of concerns

THIS FILE:
- IS import-only
- IS in-memory only
- IS deterministic
- EMITS facts, not judgments

THIS FILE IS NOT:
- NOT executable
- NOT a scorer
- NOT a policy engine
- NOT a CSV reader
- NOT a preview
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Sequence
from collections import OrderedDict


def _is_empty(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, str):
        return not v.strip()
    if isinstance(v, (list, tuple, set, dict)):
        return len(v) == 0
    return False


def _as_text(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip()


def _safe_div(num: float, den: float) -> float:
    return round(num / den, 3) if den else 0.0


def _stable_sort(keys: Iterable[str]) -> List[str]:
    return sorted([k for k in keys if isinstance(k, str)], key=str.lower)


def _looks_like_signal_field(field: str) -> bool:
    """
    SIGNAL fields represent technical capability signals.
    Examples: matches, vector/rag/inference, cuda/triton, rlhf, etc.
    """
    f = field.lower()
    return any(
        k in f for k in (
            "signal",
            "match",
            "matches",
            "relevance",
            "stack",
            "vector",
            "rag",
            "retrieval",
            "embedding",
            "inference",
            "cuda",
            "triton",
            "onnx",
            "tensorrt",
            "rlhf",
            "lora",
            "qlora",
            "dpo",
            "ppo",
            "deepspeed",
            "fsdp",
            "nccl",
            "kubernetes",
            "k8s",
            "distributed",
            "latency",
            "throughput",
        )
    )


def _looks_like_evidence_field(field: str) -> bool:
    """
    EVIDENCE fields represent narrative or evaluative evidence artifacts.
    Examples: strengths/weaknesses, evidence, tier labels, score summaries.
    """
    f = field.lower()
    return any(
        k in f for k in (
            "evidence",
            "strength",
            "weakness",
            "tier",
            "score",
            "summary",
            "recommendation",
            "rationale",
        )
    )


def _count_populated_fields(row: Mapping[str, Any], fields: Sequence[str]) -> int:
    c = 0
    for f in fields:
        if not _is_empty(row.get(f)):
            c += 1
    return c


def aggregate_signal_views(
    rows: Sequence[Mapping[str, Any]],
    *,
    role_key: str = "Role_Type",
    person_id_key: str = "Person_ID",
    max_fields_tracked: int = 300,
) -> Dict[str, Any]:
    """
    Aggregate rows into deterministic, policy-ready facts.

    Output contract:
      out["density_inputs"]["global"] and out["density_inputs"]["by_role"][role]
      provide the exact numeric inputs Day 7 policy consumes.

    Definitions (units are "distinct populated fields per row"):
      - nonempty_fields_avg
      - signal_fields_nonempty_avg
      - evidence_fields_nonempty_avg

    Guarantees:
      - No file IO
      - No printing
      - No CSV reading
      - No policy thresholds or judgments
    """
    safe_rows = list(rows or [])
    total_rows = len(safe_rows)

    # Collect fields observed in-memory (bounded, deterministic)
    field_set: set[str] = set()
    for r in safe_rows:
        if isinstance(r, Mapping):
            for k in r.keys():
                if isinstance(k, str):
                    field_set.add(k)
    all_fields = _stable_sort(field_set)[: max_fields_tracked]

    signal_fields = _stable_sort([f for f in all_fields if _looks_like_signal_field(f)])
    evidence_fields = _stable_sort([f for f in all_fields if _looks_like_evidence_field(f)])

    # Identity coverage facts
    person_ids: List[str] = []
    missing_person_id = 0
    for r in safe_rows:
        pid = _as_text(r.get(person_id_key)) if isinstance(r, Mapping) else ""
        if pid:
            person_ids.append(pid)
        else:
            missing_person_id += 1
    unique_people = len(set(person_ids))

    # Global density accumulation (per-row counts)
    global_nonempty_counts: List[int] = []
    global_signal_counts: List[int] = []
    global_evidence_counts: List[int] = []

    # Role buckets
    role_buckets: Dict[str, List[Mapping[str, Any]]] = {}

    for r in safe_rows:
        nonempty = _count_populated_fields(r, all_fields)
        sig = _count_populated_fields(r, signal_fields)
        ev = _count_populated_fields(r, evidence_fields)

        global_nonempty_counts.append(nonempty)
        global_signal_counts.append(sig)
        global_evidence_counts.append(ev)

        role = _as_text(r.get(role_key))
        if role:
            role_buckets.setdefault(role, []).append(r)

    density_inputs: "OrderedDict[str, Any]" = OrderedDict()

    density_inputs["global"] = OrderedDict(
        row_count=total_rows,
        unique_people=unique_people,
        missing_person_id=missing_person_id,
        nonempty_fields_avg=_safe_div(sum(global_nonempty_counts), total_rows),
        signal_fields_nonempty_avg=_safe_div(sum(global_signal_counts), total_rows),
        evidence_fields_nonempty_avg=_safe_div(sum(global_evidence_counts), total_rows),
        signal_like_field_count=len(signal_fields),
        evidence_like_field_count=len(evidence_fields),
        signal_like_fields=signal_fields,
        evidence_like_fields=evidence_fields,
    )

    by_role: "OrderedDict[str, Any]" = OrderedDict()

    for role in _stable_sort(role_buckets.keys()):
        r_rows = role_buckets[role]
        rc = len(r_rows)

        role_nonempty_counts: List[int] = []
        role_signal_counts: List[int] = []
        role_evidence_counts: List[int] = []

        for rr in r_rows:
            role_nonempty_counts.append(_count_populated_fields(rr, all_fields))
            role_signal_counts.append(_count_populated_fields(rr, signal_fields))
            role_evidence_counts.append(_count_populated_fields(rr, evidence_fields))

        by_role[role] = OrderedDict(
            row_count=rc,
            nonempty_fields_avg=_safe_div(sum(role_nonempty_counts), rc),
            signal_fields_nonempty_avg=_safe_div(sum(role_signal_counts), rc),
            evidence_fields_nonempty_avg=_safe_div(sum(role_evidence_counts), rc),
            signal_like_field_count=len(signal_fields),
            evidence_like_field_count=len(evidence_fields),
        )

    density_inputs["by_role"] = by_role

    out: "OrderedDict[str, Any]" = OrderedDict(
        meta=OrderedDict(
            module="EXECUTION_CORE.aggregate_signal_views",
            contract="in_memory_fact_aggregation",
            emits="density_inputs",
            not_executable=True,
            not_a_writer=True,
            not_a_phase=True,
            not_a_preview=True,
        ),
        density_inputs=density_inputs,
    )
    return out


__all__ = ["aggregate_signal_views"]
