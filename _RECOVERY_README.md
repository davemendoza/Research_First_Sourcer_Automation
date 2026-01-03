# AI Talent Engine — Recovery Pack (v1.0.0)

This recovery pack exists to prevent a third incident.

## What it generates
- `preflight_duplicate_guard.py`  
  Fail-closed duplicate module baseline detector (import shadow prevention)

- `lockdown_import_scope.sh`  
  Idempotent isolation of duplicate-prone folders into `_ARCHIVE/`

- `tools/extract_canonical_schema_82.py`  
  Generates `schemas/canonical_people_schema_82.json` from the authoritative DOCX

## Run order (do not reorder)
1) `./preflight_duplicate_guard.py`  
2) `./lockdown_import_scope.sh`  
3) `./preflight_duplicate_guard.py` (must pass)  
4) `python3 tools/extract_canonical_schema_82.py`

## Definition of done
- No duplicate `.py` basenames in import-visible scope
- Canonical schema JSON exists and is count=82
