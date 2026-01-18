#!/usr/bin/env zsh
set -euo pipefail

# ============================================================
# Research-First Sourcer Automation — Phrase-Safe Menu
# ============================================================
# CONTRACT:
# - Menu items are ATOMIC PHRASES
# - No phrase implies another
# - No defaults are injected
# - Selection executes EXACT phrase only
# ============================================================

ROOT_DIR="$(cd "$(dirname "${(%):-%N}")/.." && pwd)"

menu() {
  echo ""
  echo "Select command:"
  echo "  1) start"
  echo "  2) inventory"
  echo "  3) demo frontier"
  echo "  4) gpt slim"
  echo "  5) talent intelligence"
  echo ""
  read "?Choice: " choice

  case "$choice" in
    1) exec "$ROOT_DIR/start" ;;
    2) exec "$ROOT_DIR/inventory" ;;
    3) exec "$ROOT_DIR/demo" "frontier" ;;
    4) exec "$ROOT_DIR/gpt" "slim" ;;
    5) exec "$ROOT_DIR/tools/talent" "intelligence" ;;
    *)
      echo "Invalid selection"
      exit 1
      ;;
  esac
}

menu
