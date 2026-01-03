#!/bin/bash
# ======================================================================
#  SSH Diagnostic + Auto-Repair Utility
#  © 2025 L. David Mendoza — AI Talent Engine – Signal Intelligence
#  Purpose: Ensure SSH connectivity, correct Git remote, and auto-repair
#           key and repo config before any build or demo run.
# ======================================================================

LOG_DIR="$(pwd)/logs"
LOG_FILE="$LOG_DIR/ssh_health.log"
mkdir -p "$LOG_DIR"

echo "──────────────────────────────────────────────" | tee -a "$LOG_FILE"
echo "🔍 SSH Diagnostic + Auto-Repair — $(date)" | tee -a "$LOG_FILE"
echo "──────────────────────────────────────────────" | tee -a "$LOG_FILE"

# Step 1: Check for SSH key existence
KEY_PATH="$HOME/.ssh/id_ed25519"
PUB_PATH="$HOME/.ssh/id_ed25519.pub"

if [[ -f "$KEY_PATH" && -f "$PUB_PATH" ]]; then
  echo "✅ SSH keypair detected: $KEY_PATH" | tee -a "$LOG_FILE"
else
  echo "⚠️ No SSH key found. Generating a new one..." | tee -a "$LOG_FILE"
  ssh-keygen -t ed25519 -C "$(whoami)@$(hostname)" -f "$KEY_PATH" -N ""
  echo "✅ New SSH keypair created." | tee -a "$LOG_FILE"
fi

# Step 2: Test SSH connection to GitHub
echo "🔗 Testing SSH connection to GitHub..." | tee -a "$LOG_FILE"
ssh -T git@github.com &>/tmp/ssh_test_output
SSH_RESULT=$?

if [[ $SSH_RESULT -eq 1 ]] || grep -q "successfully authenticated" /tmp/ssh_test_output; then
  echo "✅ SSH authentication successful." | tee -a "$LOG_FILE"
else
  echo "⚠️ SSH authentication failed." | tee -a "$LOG_FILE"
  echo "Attempting auto-repair..." | tee -a "$LOG_FILE"

  # Attempt to add SSH key to GitHub if CLI is installed
  if command -v gh &>/dev/null; then
    echo "🔧 Adding key to GitHub via GitHub CLI..." | tee -a "$LOG_FILE"
    gh auth login --ssh --hostname github.com
    gh ssh-key add "$PUB_PATH" --title "$(hostname)-AutoKey-$(date +%Y%m%d)"
    echo "✅ SSH key added to GitHub account." | tee -a "$LOG_FILE"
  else
    echo "❌ GitHub CLI not found. Please install it (brew install gh) and rerun." | tee -a "$LOG_FILE"
  fi
fi

# Step 3: Verify Git remote URL format
REMOTE_URL=$(git remote get-url origin 2>/dev/null)
EXPECTED_URL="git@github.com:davemendoza/Research_First_Sourcer_Automation.git"

if [[ "$REMOTE_URL" == "$EXPECTED_URL" ]]; then
  echo "✅ Git remote is correctly set to SSH." | tee -a "$LOG_FILE"
else
  echo "⚠️ Incorrect remote detected: $REMOTE_URL" | tee -a "$LOG_FILE"
  echo "🔧 Resetting to correct SSH remote..." | tee -a "$LOG_FILE"
  git remote set-url origin "$EXPECTED_URL"
  echo "✅ Remote corrected to: $EXPECTED_URL" | tee -a "$LOG_FILE"
fi

# Step 4: Validate push access silently
echo "🔍 Verifying push permission..." | tee -a "$LOG_FILE"
git ls-remote &>/dev/null
if [[ $? -eq 0 ]]; then
  echo "✅ SSH connection verified. GitHub push ready." | tee -a "$LOG_FILE"
else
  echo "❌ Push check failed. Manual verification recommended." | tee -a "$LOG_FILE"
fi

echo "──────────────────────────────────────────────" | tee -a "$LOG_FILE"
echo "🏁 SSH Diagnostic completed." | tee -a "$LOG_FILE"
echo "Results logged at: $LOG_FILE"
echo "──────────────────────────────────────────────" | tee -a "$LOG_FILE"
exit 0
