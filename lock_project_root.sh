#!/bin/zsh
# ============================================================
#  AI Talent Engine – Root Path Auto-Loader
#  Created by L. David Mendoza © 2025
# ============================================================

ROOT_PATH="/Users/davemendoza/Desktop/Research_First_Sourcer_Automation"

# 1️⃣ Add environment variable and auto-cd logic to ~/.zshrc
if ! grep -q "AI_TALENT_ENGINE_ROOT" ~/.zshrc; then
  {
    echo ""
    echo "# ============================================================"
    echo "# AI Talent Engine Environment Setup (Persistent Configuration)"
    echo "# ============================================================"
    echo "export AI_TALENT_ENGINE_ROOT=\"$ROOT_PATH\""
    echo "if [ -d \"\$AI_TALENT_ENGINE_ROOT\" ]; then"
    echo "  cd \"\$AI_TALENT_ENGINE_ROOT\""
    echo "  echo '🔹 AI Talent Engine Root Loaded: \$AI_TALENT_ENGINE_ROOT'"
    echo "else"
    echo "  echo '⚠️  AI_TALENT_ENGINE_ROOT not found: \$AI_TALENT_ENGINE_ROOT'"
    echo "fi"
  } >> ~/.zshrc
  echo "✅ Environment variable and auto-cd logic added to ~/.zshrc"
else
  echo "⚙️  AI_TALENT_ENGINE_ROOT already configured in ~/.zshrc"
fi

# 2️⃣ Safety check: ensure folder exists
mkdir -p "$ROOT_PATH"

# 3️⃣ Display confirmation
echo "------------------------------------------------------------"
echo "✅ AI Talent Engine Root Path permanently set to:"
echo "   $ROOT_PATH"
echo "------------------------------------------------------------"
echo "To apply immediately, run:"
echo "   source ~/.zshrc"
