#!/usr/bin/env bash
set -euo pipefail

# GPT-Slim Wiring Plan Printer (Universal, Design-Only)
# Version: v1.0.0-gptslim-wiring-plan
# Owner: L. David Mendoza
# Date: 2026-01-02
#
# Purpose:
# - Prints the exact, deterministic wiring steps that WOULD be performed later.
# - Makes no edits. Performs no execution. No model calls.

echo "GPT-Slim UNIVERSAL wiring plan (design-only)."
echo
echo "0) Non-negotiable constraints:"
echo "   - No new CLI flags unless added to the underlying Python entry point and visible in --help."
echo "   - No modification of primary People CSV outputs."
echo "   - GPT-Slim writes only to outputs/gpt_slim/."
echo "   - Fail-safe separation: pipeline success must not depend on evaluator success."
echo
echo "1) Locate the post-validation hook point:"
echo "   - After the People scenario run succeeds"
echo "   - After post-generation validation passes"
echo
echo "2) Invoke evaluator as an explicit step:"
echo "   - Example (future): ./scripts/gpt_slim_eval_universal.sh <scenario> <input_csv>"
echo "   - For now (today): only dry-run planning is allowed"
echo
echo "3) Artifact rules:"
echo "   - Required: outputs/gpt_slim/<scenario>_gpt_slim_eval_<run_id>.csv"
echo "   - Optional: outputs/gpt_slim/<scenario>_gpt_slim_eval_<run_id>.json"
echo "   - Never overwrite existing eval artifacts"
echo
echo "4) Failure semantics:"
echo "   - Evaluator non-zero exit should be reported, but not break People Pipeline artifacts"
echo
echo "5) Acceptance gate for wiring phase (future):"
echo "   - A green transcript showing:"
echo "       a) primary People CSV exists"
echo "       b) validator passed"
echo "       c) evaluator produced eval artifacts"
echo "       d) no modifications to People CSV"
echo
echo "Done. No changes were made."
