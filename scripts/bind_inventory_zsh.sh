#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ZSHRC="${HOME}/.zshrc"

MARK_BEGIN="# >>> AI_TALENT_ENGINE_INVENTORY_BIND >>>"
MARK_END="# <<< AI_TALENT_ENGINE_INVENTORY_BIND <<<"

BLOCK="${MARK_BEGIN}
# AI Talent Engine: hard bind inventory command to canonical runner
inventory() {
  local repo=\"${REPO_ROOT}\"
  if [[ ! -d \"\$repo\" ]]; then
    echo \"❌ Repo root not found: \$repo\"
    return 1
  fi
  ( cd \"\$repo\" && ./scripts/inventory_command.sh )
}
${MARK_END}
"

# Remove any prior block
if [[ -f "$ZSHRC" ]]; then
  awk -v b="$MARK_BEGIN" -v e="$MARK_END" '
    $0==b {skip=1}
    !skip {print}
    $0==e {skip=0}
  ' "$ZSHRC" > "${ZSHRC}.tmp"
  mv "${ZSHRC}.tmp" "$ZSHRC"
fi

# Append fresh block
printf "\n%s\n" "$BLOCK" >> "$ZSHRC"

echo "✅ Bound: inventory -> ${REPO_ROOT}/scripts/inventory_command.sh"
echo "Now run: source ~/.zshrc"
