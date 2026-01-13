from docx import Document
from pathlib import Path
import sys

DOCX = Path("1 AI_Talent_Engine_Canonical_People_Schema_LOCKED_82_DETERMINATIVE_FIRST.docx")
OUT  = Path("data/talent_schema_inventory.csv")

if not DOCX.exists():
    sys.exit(f"FATAL: DOCX not found: {DOCX}")

doc = Document(DOCX)

cols = []
started = False

for p in doc.paragraphs:
    text = p.text.strip()
    if not text:
        continue

    # Detect first real column anchor
    if text.startswith("Person_ID"):
        started = True

    if not started:
        continue

    # Expect format: "Column_Name — description" or "Column_Name – description"
    if "—" in text:
        col = text.split("—", 1)[0].strip()
    elif "–" in text:
        col = text.split("–", 1)[0].strip()
    else:
        continue

    cols.append(col)

# De-duplicate while preserving order
seen = set()
cols = [c for c in cols if not (c in seen or seen.add(c))]

if len(cols) != 82:
    print("EXTRACTED COLUMNS:")
    for i, c in enumerate(cols, 1):
        print(f"{i:02d}: {c}")
    sys.exit(f"FATAL: extracted {len(cols)} columns, expected 82")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(",".join(cols) + "\n", encoding="utf-8")

print("CANONICAL_SCHEMA_WRITTEN")
print("COLUMNS", len(cols))
print("FILE", OUT)
