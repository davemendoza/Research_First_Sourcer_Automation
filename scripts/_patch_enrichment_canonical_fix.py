#!/usr/bin/env python3

from pathlib import Path
import re

path = Path("scripts/universal_enrichment_pipeline.py")
text = path.read_text(encoding="utf-8")

old = '''
    if cols[:len(CANON_PREFIX)] != CANON_PREFIX:
        print("ERROR: input CSV not canonical-normalized. Expected prefix: " + ", ".join(CANON_PREFIX))
        sys.exit(3)
'''

new = '''
    # Canonical enforcement: ensure prefix columns exist and are ordered first
    for i, col in enumerate(CANON_PREFIX):
        if i >= len(cols) or cols[i] != col:
            print("ERROR: input CSV failed canonical prefix check.")
            print("Expected prefix:", CANON_PREFIX)
            print("Found prefix:", cols[:len(CANON_PREFIX)])
            sys.exit(3)
'''

if old not in text:
    raise SystemExit("Canonical block not found — aborting")

path.write_text(text.replace(old, new), encoding="utf-8")
print("✓ Canonical enforcement patch applied")
