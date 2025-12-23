# -*- coding: utf-8 -*-
"""
Track D Adapter Registry
(c) 2025 L. David Mendoza. All Rights Reserved.

Version: v1.0.0-trackd-hardreset
Date: 2025-12-22

Contract:
- Expose a single authoritative mapping named SEED_HUB_TYPE_TO_ADAPTER
- Track D currently supports ONLY:
    "GitHub_Repo_Contributors" -> RepoContribAdapter
- Any attempt to access an unknown Seed_Hub_Type must hard-fail.

Changelog:
- v1.0.0-trackd-hardreset: Registry locked to RepoContribAdapter only.

Validation (manual):
- python3 -m tracks.track_d.run_track_d --seed-hubs data/AI_Talent_Landscape_Seed_Hubs.xlsx --out outputs/track_d

Git (manual):
- git status
- git add tracks/track_d/adapter_registry.py
- git commit -m "Track D: lock adapter registry to GitHub_Repo_Contributors only"
- git push
"""

from __future__ import annotations

from typing import Dict, Type

from tracks.track_d.adapters.repo_contrib_adapter import RepoContribAdapter

# Authoritative mapping (do not rename).
SEED_HUB_TYPE_TO_ADAPTER: Dict[str, Type[RepoContribAdapter]] = {
    "GitHub_Repo_Contributors": RepoContribAdapter,
}


def get_adapter_class_for_seed_hub_type(seed_hub_type: str) -> Type[RepoContribAdapter]:
    """
    Hard-fails for any unknown Seed_Hub_Type.
    """
    key = (seed_hub_type or "").strip()
    if not key:
        raise KeyError("Seed_Hub_Type is empty.")
    if key not in SEED_HUB_TYPE_TO_ADAPTER:
        raise KeyError(
            f"Unsupported Seed_Hub_Type={key!r}. Track D is hard-locked to only: {sorted(SEED_HUB_TYPE_TO_ADAPTER.keys())}"
        )
    return SEED_HUB_TYPE_TO_ADAPTER[key]
