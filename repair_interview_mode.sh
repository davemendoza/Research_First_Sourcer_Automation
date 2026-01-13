#!/usr/bin/env bash
set -euo pipefail

# ==============================================
# AI Talent Engine — Interview-Grade Contract Repair
# © 2025 L. David Mendoza
# Purpose:
# - Fix Python contract drift (imports + expected function names)
# - Restore deterministic manifest writing
# - Enforce canonical 82-col schema read-only usage
# - Stabilize daily shell commands (start/inventory/demo/gpt)
# - Add list-roles + safe completion without colliding with 'run'
# ==============================================

ROOT="$(pwd)"
STAMP="$(date +"%Y%m%d_%H%M%S")"
BACKUP_DIR="_REPAIR_BACKUPS/${STAMP}"
mkdir -p "${BACKUP_DIR}"

fail() { echo "❌ $*" 1>&2; exit 1; }
ok() { echo "✅ $*"; }

# ----------------------------
# 0) Preconditions
# ----------------------------
[ -f "run_safe.py" ] || fail "run_safe.py not found in repo root: ${ROOT}"
[ -f "data/talent_schema_inventory.csv" ] || fail "data/talent_schema_inventory.csv missing"
python3 - <<'PY' || exit 1
from pathlib import Path
p = Path("data/talent_schema_inventory.csv")
line = p.read_text(encoding="utf-8").splitlines()[0].strip()
cols = [c for c in line.split(",") if c.strip()]
if len(cols) != 82:
    raise SystemExit(f"FATAL: schema columns {len(cols)} != 82")
PY
ok "Canonical schema present and 82 columns"

# ----------------------------
# 1) Backup the files we touch
# ----------------------------
backup_one() {
  local f="$1"
  if [ -f "$f" ]; then
    mkdir -p "${BACKUP_DIR}/$(dirname "$f")"
    cp -p "$f" "${BACKUP_DIR}/$f"
  fi
}

backup_one "run_safe.py"
backup_one "people_scenario_resolver.py"
backup_one "manifest_writer.py"
backup_one "phase_h_io.py"
backup_one "scripts/ops/run_context.py"

ok "Backups written to ${BACKUP_DIR}"

# ----------------------------
# 2) Restore a single canonical manifest writer contract
#    Contract required by your current run_safe call sites:
#      write_manifest(manifest_path, payload)
#    If manifest_writer.py is missing or wrong, we write it deterministically.
# ----------------------------
cat > manifest_writer.py <<'PY'
#!/usr/bin/env python3
"""
AI Talent Engine — Manifest Writer (Canonical Contract)
© 2025 L. David Mendoza

Non-negotiable contract:
    write_manifest(manifest_path, payload) -> str

This file exists so higher-level runners never drift on manifest plumbing.
No schema logic. No enrichment logic. Just atomic-ish JSON write.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Union


def _atomic_write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write to a temp file in the same directory then replace.
    fd, tmp = tempfile.mkstemp(prefix=".tmp_manifest_", suffix=".json", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(tmp, str(path))
    finally:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass


def write_manifest(manifest_path: Union[str, Path], payload: Dict[str, Any]) -> str:
    p = Path(manifest_path)
    _atomic_write_json(p, payload)
    return str(p)
PY

chmod 644 manifest_writer.py
ok "manifest_writer.py restored (canonical contract)"

# ----------------------------
# 3) Fix run_safe.py imports to match live contracts
#    - Ensure it imports write_manifest from manifest_writer (now canonical)
#    - Do not allow keyword-arg mismatches or missing modules
# ----------------------------
python3 - <<'PY'
from pathlib import Path
import re

p = Path("run_safe.py")
txt = p.read_text(encoding="utf-8")

# Normalize manifest import to canonical module
txt2 = re.sub(
    r'^\s*from\s+manifest_writer\s+import\s+write_manifest\s*$',
    'from manifest_writer import write_manifest',
    txt,
    flags=re.MULTILINE
)

# If it imports manifest from elsewhere, override to canonical
txt2 = re.sub(
    r'^\s*from\s+phase_h_io\s+import\s+write_manifest\s*$',
    'from manifest_writer import write_manifest',
    txt2,
    flags=re.MULTILINE
)

# If it imports tools.manifest write_manifest, override to canonical
txt2 = re.sub(
    r'^\s*from\s+tools\.manifest\s+import\s+.*write_manifest.*$',
    'from manifest_writer import write_manifest',
    txt2,
    flags=re.MULTILINE
)

# Guard: if no manifest import exists but write_manifest is referenced, inject it near top.
if "write_manifest" in txt2 and "from manifest_writer import write_manifest" not in txt2:
    # Insert after first block of imports
    lines = txt2.splitlines(True)
    insert_at = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("import") or line.strip().startswith("from"):
            insert_at = i + 1
        elif i > 5 and insert_at > 0:
            break
    lines.insert(insert_at, "from manifest_writer import write_manifest\n")
    txt2 = "".join(lines)

if txt2 != txt:
    p.write_text(txt2, encoding="utf-8")
PY
ok "run_safe.py manifest import normalized"

# ----------------------------
# 4) Restore people scenario resolver contract expected by callers
#    Your file defines run_people(...). Some callers expect run_scenario(...)
#    We add a stable wrapper run_scenario without changing existing logic.
# ----------------------------
if [ -f "people_scenario_resolver.py" ]; then
python3 - <<'PY'
from pathlib import Path
import re

p = Path("people_scenario_resolver.py")
txt = p.read_text(encoding="utf-8")

if "def run_scenario(" not in txt:
    # Append wrapper at end
    wrapper = """
# ==================================================
# Contract Compatibility Wrapper (Do Not Remove)
# Some runners import run_scenario from this module.
# ==================================================
def run_scenario(
    scenario: str,
    mode: str = "demo",
    min_rows: int = 25,
    max_rows: int = 50,
    outdir: str = None
):
    return run_people(
        scenario=scenario,
        mode=mode,
        min_rows=min_rows,
        max_rows=max_rows,
        outdir=outdir
    )
"""
    txt = txt.rstrip() + "\n" + wrapper
    p.write_text(txt, encoding="utf-8")
PY
ok "people_scenario_resolver.py now exports run_scenario()"
else
ok "people_scenario_resolver.py not present, skipping wrapper"
fi

# ----------------------------
# 5) Create locked role list used by help + completion
# ----------------------------
mkdir -p data
cat > data/ai_role_types.locked <<'TXT'
frontier
foundational_ai
ai_research_scientist
research_scientist_llm
rlhf_researcher
alignment_researcher
ai_engineer
genai_engineer
machine_learning_engineer
ml_engineer
applied_ai_engineer
ai_performance_engineer
inference_engineer
llm_inference_engineer
model_optimization_engineer
ai_infra
ai_infrastructure_engineer
ml_infra_engineer
platform_engineer_ai
gpu_infra_engineer
distributed_systems_engineer
TXT
chmod 444 data/ai_role_types.locked
ok "Locked role list written: data/ai_role_types.locked"

# ----------------------------
# 6) Install a safe CLI wrapper that does NOT collide with 'run'
#    Command: aite
#    - aite demo frontier
#    - aite scenario <role>
#    - aite slim
#    - aite list-roles
# ----------------------------
mkdir -p "${HOME}/bin"
cat > "${HOME}/bin/aite" <<'BASH'
#!/usr/bin/env bash
set -euo pipefail

ROOT="${HOME}/Desktop/Research_First_Sourcer_Automation"
cd "${ROOT}" || { echo "❌ Repo root not found: ${ROOT}" 1>&2; exit 1; }

usage() {
  cat <<'TXT'
AI Talent Engine — Daily Ops

Commands:
  aite demo frontier
  aite scenario <role>
  aite slim
  aite list-roles
TXT
}

list_roles() {
  if [ -f "data/ai_role_types.locked" ]; then
    cat "data/ai_role_types.locked"
  else
    echo "❌ data/ai_role_types.locked missing" 1>&2
    exit 1
  fi
}

MODE="${1:-}"
ROLE="${2:-}"

case "${MODE}" in
  demo)
    [ "${ROLE}" = "frontier" ] || { echo "Usage: aite demo frontier" 1>&2; exit 1; }
    python3 run_safe.py frontier
    ;;
  scenario)
    [ -n "${ROLE}" ] || (usage; exit 1)
    python3 run_safe.py "${ROLE}"
    ;;
  slim)
    python3 gpt_slim_from_people_csv.py
    ;;
  list-roles)
    list_roles
    ;;
  ""|-h|--help|help)
    usage
    ;;
  *)
    echo "❌ Unknown command: ${MODE}" 1>&2
    usage
    exit 1
    ;;
esac
BASH
chmod 755 "${HOME}/bin/aite"
ok "Installed ${HOME}/bin/aite"

# Ensure PATH contains ~/bin
if ! echo "$PATH" | tr ':' '\n' | grep -qx "${HOME}/bin"; then
  echo 'export PATH="$HOME/bin:$PATH"' >> "${HOME}/.zshrc"
  ok "Added ~/bin to PATH in ~/.zshrc"
fi

# ----------------------------
# 7) Zsh completion for aite (safe, no 'run' collisions)
# ----------------------------
mkdir -p "${HOME}/.zsh/completion"
cat > "${HOME}/.zsh/completion/_aite" <<'ZSH'
#compdef aite

local -a modes roles
modes=(demo scenario slim list-roles)

if [[ -f "$HOME/Desktop/Research_First_Sourcer_Automation/data/ai_role_types.locked" ]]; then
  roles=("${(@f)$(<"$HOME/Desktop/Research_First_Sourcer_Automation/data/ai_role_types.locked")}")
else
  roles=()
fi

if (( CURRENT == 2 )); then
  _describe 'mode' modes
elif (( CURRENT == 3 )); then
  case "$words[2]" in
    scenario)
      _describe 'role' roles
      ;;
    demo)
      _describe 'role' (frontier)
      ;;
  esac
fi
ZSH
chmod 644 "${HOME}/.zsh/completion/_aite"
ok "Installed zsh completion: ~/.zsh/completion/_aite"

# Ensure fpath includes ~/.zsh/completion and compinit is run
if ! grep -q 'fpath=.*\.zsh/completion' "${HOME}/.zshrc" 2>/dev/null; then
  cat >> "${HOME}/.zshrc" <<'ZRC'

# ==================================================
# AI TALENT ENGINE — Completion (Safe)
# ==================================================
fpath=("$HOME/.zsh/completion" $fpath)
autoload -Uz compinit && compinit
ZRC
  ok "Enabled completion path + compinit in ~/.zshrc"
fi

# ----------------------------
# 8) Final validation (no guessing)
# ----------------------------
python3 - <<'PY'
import importlib
import sys

for mod in ("manifest_writer",):
    importlib.import_module(mod)
print("manifest_writer import OK")

# Confirm schema count
from pathlib import Path
line = Path("data/talent_schema_inventory.csv").read_text(encoding="utf-8").splitlines()[0].strip()
cols = [c for c in line.split(",") if c.strip()]
assert len(cols) == 82, len(cols)
print("schema 82 OK")
PY
ok "Validation OK"

echo ""
echo "✅ REPAIR COMPLETE"
echo "Next:"
echo "  source ~/.zshrc"
echo "  aite demo frontier"
echo "  aite list-roles"
echo "  aite scenario ai_engineer"
