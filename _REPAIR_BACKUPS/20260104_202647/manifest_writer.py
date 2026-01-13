#!/usr/bin/env python3
"""
AI Talent Engine — Manifest Writer
© 2025 L. David Mendoza

Minimal, contract-safe manifest writer.
"""

import json
from pathlib import Path


def write_manifest(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    return str(path)
