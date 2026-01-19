# © 2026 L. David Mendoza
#
# FILE: external_ingestion_binder.py
#
# PURPOSE:
# Single, explicit wiring surface for ingesting EXTERNAL / NON-NATIVE datasets.
#
# This binder:
# - Loads external datasets (read-only)
# - Applies Day 21 ingestion contract
# - Invokes Day 22 supplemental recovery adapter
# - Produces a NEW enriched dataset (never mutates input)
# - Passes enriched rows into the canonical evaluation pipeline
# - Enforces determinism and provenance
#
# THIS IS THE ONLY LEGAL WIRING POINT BETWEEN:
# external files -> recovery -> evaluation
#
# NO SCORING LOGIC.
# NO RECOVERY LOGIC.
# NO IO SIDE EFFECTS BEYOND ORCHESTRATION.

from typing import Dict, Any, List
import hashlib
import json

from contracts.supplemental_ingestion_contract import assess_dataset
from EXECUTION_CORE.supplemental_recovery_adapter import recover_dataset


def _fingerprint_object(obj: Any) -> str:
    """
    Deterministically fingerprint a Python object.
    """
    serialized = json.dumps(obj, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


def bind_external_dataset(
    rows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Bind an external dataset into the canonical evaluation pipeline.

    Returns:
    - enriched_rows
    - lineage
    - fingerprints
    """

    if not isinstance(rows, list):
        raise TypeError("External ingestion requires a list of row dictionaries")

    input_fingerprint = _fingerprint_object(rows)

    # Day 21 — assess eligibility and missing fields
    ingestion_assessment = assess_dataset(rows)

    # Day 22 — recover public supplemental fields
    recovery_results = recover_dataset(
        rows=rows,
        recovery_plan=ingestion_assessment,
    )

    enriched_rows: List[Dict[str, Any]] = []

    for idx, row in enumerate(rows):
        new_row = dict(row)

        recovery = recovery_results.get(idx, {})
        recovered_fields = recovery.get("recovered_fields", {})

        for field, value in recovered_fields.items():
            if field not in new_row or not new_row.get(field):
                new_row[field] = value

        enriched_rows.append(new_row)

    enriched_fingerprint = _fingerprint_object(enriched_rows)

    return {
        "enriched_rows": enriched_rows,
        "lineage": {
            "input_fingerprint": input_fingerprint,
            "enriched_fingerprint": enriched_fingerprint,
            "ingestion_assessment": ingestion_assessment,
            "recovery_results": recovery_results,
        },
        "fingerprints": {
            "input": input_fingerprint,
            "enriched": enriched_fingerprint,
        },
    }
