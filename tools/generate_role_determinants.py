#!/usr/bin/env python3
# ===================================================
# AI TALENT ENGINE – SIGNAL INTELLIGENCE
# generate_role_determinants.py
# © 2026 L. David Mendoza. All Rights Reserved.
# ===================================================

import re
from pathlib import Path
from docx import Document

ROOT = Path(__file__).resolve().parents[1]
TIER_DOC = ROOT / "docs/INSTITUTIONAL_RULES/Canonical Template Tier Taxonomy Roles.docx"

# ------------------------------------------------------------------
# Canonical roles we expect the system to understand
# ------------------------------------------------------------------
CANONICAL_ROLES = [
    "RLHF Researcher",
    "Alignment Researcher",
    "AI Safety Researcher",
    "AI Systems Engineer",
]

# ------------------------------------------------------------------
# Canonical → search phrases (NOT exact headers)
# These are semantic anchors, not fragile strings
# ------------------------------------------------------------------
ROLE_ANCHORS = {
    "RLHF Researcher": ["rlhf"],
    "Alignment Researcher": ["safety", "researcher"],
    "AI Safety Researcher": ["safety", "researcher"],
    "AI Systems Engineer": ["ai systems", "platform"],
}

# ------------------------------------------------------------------
def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())

# ------------------------------------------------------------------
def load_tier_headers(doc_path: Path):
    if not doc_path.exists():
        raise FileNotFoundError(f"Tier taxonomy doc not found: {doc_path}")

    doc = Document(doc_path)
    headers = []

    for p in doc.paragraphs:
        text = p.text.strip()
        if text and not text.startswith("-"):
            headers.append(text)

    return headers

# ------------------------------------------------------------------
def resolve_role_to_header(role: str, tier_headers: list[str]) -> str | None:
    anchors = ROLE_ANCHORS.get(role)
    if not anchors:
        return None

    for header in tier_headers:
        h_norm = normalize(header)
        if all(a in h_norm for a in anchors):
            return header

    return None

# ------------------------------------------------------------------
def build():
    print("[INFO] Loading Tier Taxonomy from:")
    print(f"       {TIER_DOC}")

    tier_headers = load_tier_headers(TIER_DOC)
    print(f"[INFO] Loaded {len(tier_headers)} tier role headers")

    generated = []
    skipped = []

    for role in CANONICAL_ROLES:
        resolved = resolve_role_to_header(role, tier_headers)

        if not resolved:
            skipped.append(role)
            print(f"[WARN] Could not resolve role: {role}")
            continue

        generated.append((role, resolved))
        print(f"[OK] {role} → {resolved}")

    print("\n================ SUMMARY ================")
    print(f"Generated determinants for: {len(generated)} roles")
    print(f"Skipped safely: {len(skipped)} roles")

    if skipped:
        print("\nSkipped roles:")
        for r in skipped:
            print(f" - {r}")

    print("\n[COMPLETE] Determinant generation finished cleanly.")

# ------------------------------------------------------------------
if __name__ == "__main__":
    build()
