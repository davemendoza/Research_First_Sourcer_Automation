# ============================================================
# RFS Menu (LOCKED) — single command surface
# ============================================================

export _RFS_ROOT="$HOME/Desktop/Research_First_Sourcer_Automation"
[[ -d "$_RFS_ROOT" ]] || { echo "❌ Missing repo at $_RFS_ROOT"; return 1; }

# Load dispatch (required)
[[ -f "$_RFS_ROOT/shell/dispatch.zsh" ]] || { echo "❌ Missing shell/dispatch.zsh"; return 1; }
source "$_RFS_ROOT/shell/dispatch.zsh" || { echo "❌ Failed to load dispatch"; return 1; }

start() {
  echo "start | inventory | demo <role> | scenario <role> | talent intelligence"
}

inventory() {
  cd "$_RFS_ROOT" || return 1
  "$_RFS_ROOT/scripts/inventory_command.sh"
}

demo() { _rfs_dispatch Demo "$@"; }
scenario() { _rfs_dispatch Scenario "$@"; }
run() { _rfs_dispatch Scenario "$@"; }

talent() {
  [[ "$1" == "intelligence" ]] || { echo "Usage: talent intelligence"; return 1; }
  cd "$_RFS_ROOT" || return 1
  python3 talent_intel_preview.py
}
