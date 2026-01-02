#!/usr/bin/env python3
"""
Universal Canonical Enforcement Autogen (Allowlist, Multi-Writer Safe)
© 2025 L. David Mendoza
"""

from pathlib import Path
import re
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]

ALLOWLIST = {
    "run_safe.py",
    "ai_talent_scenario_runner.py",
    "people_scenario_resolver.py",
    "people_enrichment.py",
    "people_report_builder.py",
    "ai_talent_enrichment_pro.py",
    "demo/generate_ai_talent_master_v34.py",
    "tracks/scenario_runner.py",
    "tracks/track_a_assembly_export.py",
    "tracks/track_b_determinative_inference.py",
    "tracks/track_c_public_discovery.py",
}

CANONICAL_IMPORT = "from contracts.canonical_people_schema import enforce_canonical\n"

# ✅ THIS REGEX IS CORRECT — DO NOT CHANGE
CSV_RE = re.compile(r"(\w+)\.to_csv\(")


def patch_file(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    matches = list(CSV_RE.finditer(text))

    # Non-writer files are valid
    if not matches:
        return "OK (non-writer)"

    df_name = matches[-1].group(1)
    inject_pos = matches[-1].start()

    if f"{df_name} = enforce_canonical({df_name})" in text:
        return "OK"

    # Ensure canonical import exists
    if CANONICAL_IMPORT not in text:
        lines = text.splitlines(keepends=True)
        out = []
        inserted = False

        for line in lines:
            if not inserted and not line.startswith(("import ", "from ")):
                out.append(CANONICAL_IMPORT)
                inserted = True
            out.append(line)

        text = "".join(out)

    # Inject enforcement immediately before final to_csv
    new_text = (
        text[:inject_pos]
        + f"{df_name} = enforce_canonical({df_name})\n"
        + text[inject_pos:]
    )

    path.write_text(new_text, encoding="utf-8")
    return "PATCHED"


def main():
    failures = []

    print("\n=== Canonical People Schema Enforcement (Allowlist) ===\n")

    for rel in sorted(ALLOWLIST):
        path = REPO_ROOT / rel
        if not path.exists():
            failures.append(f"MISSING: {rel}")
            continue

        try:
            result = patch_file(path)
            print(f"{result:16} {rel}")
        except Exception as e:
            failures.append(f"FAIL: {rel} → {e}")

    if failures:
        print("\n❌ FAILURES — refusing silent completion:\n")
        for f in failures:
            print(f)
        sys.exit(1)

    print("\n✅ Canonical enforcement wired for all people outputs.\n")


if __name__ == "__main__":
    main()
