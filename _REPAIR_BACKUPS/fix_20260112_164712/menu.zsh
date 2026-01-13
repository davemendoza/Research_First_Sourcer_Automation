#!/usr/bin/env zsh
# Canonical Menu — SINGLE SOURCE OF TRUTH

export _RFS_ROOT="$HOME/Desktop/Research_First_Sourcer_Automation"

source "$_RFS_ROOT/shell/dispatch.zsh" || {
  echo "❌ dispatch.zsh missing"
  return 1
}

start() {
  echo "Research First Sourcer Automation"
  echo "Commands:"
  echo "  inventory"
  echo "  demo <role>"
  echo "  scenario <role>"
  echo "  talent intelligence"
}

inventory() {
  cd "$_RFS_ROOT" || return 1
  "$_RFS_ROOT/scripts/inventory_command.sh"
}

demo() {
  _rfs_dispatch "Demo" "$@"
}

scenario() {
  _rfs_dispatch "Scenario" "$@"
}

run() {
  scenario "$@"
}

talent() {
  [[ "$1" == "intelligence" ]] || {
    echo "Usage: talent intelligence"
    return 1
  }
  cd "$_RFS_ROOT" || return 1
  python3 EXECUTION_CORE/run_safe.py
}
