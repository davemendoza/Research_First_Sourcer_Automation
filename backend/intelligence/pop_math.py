# ============================================================
# AI TALENT ENGINE — TALENT INTELLIGENCE PLATFORM
# File: pop_math.py
# Author: Dave Mendoza
# Layer: Citation Intelligence Layer
# Purpose: Publish-or-Perish style citation math (h-index, g-index, e-index, i10, m-quotient, velocity)
# Copyright: © 2026 L. David Mendoza. All Rights Reserved.
# ============================================================

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple
import math


@dataclass(frozen=True)
class CitationSeries:
    # citations_by_year: list of (year, citations_that_year)
    citations_by_year: List[Tuple[int, int]]
    # per_paper_citations: list of total citations per paper
    per_paper_citations: List[int]
    first_pub_year: Optional[int] = None
    last_pub_year: Optional[int] = None


def _sorted_desc(vals: List[int]) -> List[int]:
    return sorted([max(0, int(v)) for v in vals], reverse=True)


def h_index(per_paper_citations: List[int]) -> int:
    c = _sorted_desc(per_paper_citations)
    h = 0
    for i, v in enumerate(c, start=1):
        if v >= i:
            h = i
        else:
            break
    return h


def g_index(per_paper_citations: List[int]) -> int:
    c = _sorted_desc(per_paper_citations)
    g = 0
    running = 0
    for i, v in enumerate(c, start=1):
        running += v
        if running >= i * i:
            g = i
        else:
            break
    return g


def e_index(per_paper_citations: List[int]) -> float:
    # e-index = sqrt( sum_{i=1..h} c_i - h^2 )
    c = _sorted_desc(per_paper_citations)
    h = h_index(c)
    top = c[:h]
    excess = sum(top) - (h * h)
    return math.sqrt(max(0.0, float(excess)))


def i10_index(per_paper_citations: List[int]) -> int:
    return sum(1 for v in per_paper_citations if int(v) >= 10)


def m_quotient(per_paper_citations: List[int], first_pub_year: Optional[int], as_of_year: int) -> float:
    h = h_index(per_paper_citations)
    if not first_pub_year:
        return 0.0
    years = max(1, as_of_year - int(first_pub_year))
    return float(h) / float(years)


def citation_velocity(citations_by_year: List[Tuple[int, int]]) -> float:
    # simple OLS slope: citations/year, deterministic and robust for small N
    pts = [(int(y), max(0, int(c))) for y, c in citations_by_year if y and c is not None]
    if len(pts) < 2:
        return 0.0
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    xbar = sum(xs) / len(xs)
    ybar = sum(ys) / len(ys)
    num = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys))
    den = sum((x - xbar) ** 2 for x in xs)
    return float(num / den) if den != 0 else 0.0


def momentum_and_acceleration(citations_by_year: List[Tuple[int, int]]) -> Tuple[float, float]:
    # momentum: last 3 years avg; acceleration: delta between last 3 and prior 3 years avg
    pts = sorted([(int(y), max(0, int(c))) for y, c in citations_by_year if y and c is not None], key=lambda t: t[0])
    if not pts:
        return 0.0, 0.0
    years = [y for y, _ in pts]
    last_year = years[-1]
    m1 = [c for y, c in pts if last_year - 2 <= y <= last_year]
    m0 = [c for y, c in pts if last_year - 5 <= y <= last_year - 3]
    avg1 = sum(m1) / max(1, len(m1))
    avg0 = sum(m0) / max(1, len(m0))
    return float(avg1), float(avg1 - avg0)


def forecast_12m(citations_by_year: List[Tuple[int, int]]) -> float:
    # linear projection of next year citations based on slope + last year's baseline, bounded >=0
    pts = sorted([(int(y), max(0, int(c))) for y, c in citations_by_year if y and c is not None], key=lambda t: t[0])
    if not pts:
        return 0.0
    last_year, last_c = pts[-1]
    slope = citation_velocity(pts)
    pred = last_c + slope  # 1-year forward
    return float(max(0.0, pred))


def compute_pop_metrics(series: CitationSeries, as_of_year: int) -> dict:
    h = h_index(series.per_paper_citations)
    g = g_index(series.per_paper_citations)
    e = e_index(series.per_paper_citations)
    i10 = i10_index(series.per_paper_citations)
    m = m_quotient(series.per_paper_citations, series.first_pub_year, as_of_year)
    vel = citation_velocity(series.citations_by_year)
    mom, acc = momentum_and_acceleration(series.citations_by_year)
    f12 = forecast_12m(series.citations_by_year)
    return {
        "Citation_h_index": int(h),
        "Citation_g_index": int(g),
        "Citation_e_index": float(round(e, 3)),
        "Citation_i10_index": int(i10),
        "Citation_m_quotient": float(round(m, 4)),
        "Citation_Velocity": float(round(vel, 4)),
        "Citation_Momentum": float(round(mom, 2)),
        "Citation_Acceleration": float(round(acc, 2)),
        "Trajectory_Forecast_12m": float(round(f12, 2)),
    }
