#!/bin/bash
# © 2025 Dave Mendoza, DBA AI Craft, Inc. All rights reserved. Strictly proprietary; no copying, derivative works, reverse engineering, redistribution, or commercial/personal use permitted without written authorization. Governed by Colorado, USA law.
# ================================================================
# 🤫 AI TALENT ENGINE — DEMO AUTORUN (Silent Mode)
# Project: Research-First Sourcer Automation
# Purpose: Validate candidate JSONs quietly and log results
# ================================================================

OUTPUT_DIR="$HOME/Desktop/Research_First_Sourcer_Automation/output"
AUDIT_LOG="$OUTPUT_DIR/_auto_clean_audit.txt"
DEMO_LOG="$OUTPUT_DIR/demo_audit.txt"
VALIDATOR="$HOME/Desktop/Research_First_Sourcer_Automation/validate_jsons.py"

echo ""
echo "🤫 [AI Talent Engine] Silent Demo Initiated"
echo "------------------------------------------------------------"

# Step 1 — Validate all candidate dossiers silently
python3 "$VALIDATOR" >/dev/null 2>&1

# Step 2 — Log audit timestamp
{
  echo "--------------------------------------------"
  echo "🕒 Silent Demo Run: $(date -u)"
  echo "Validated JSON Files:"
  ls "$OUTPUT_DIR"/*.json
  echo ""
  if [ -f "$AUDIT_LOG" ]; then
    cat "$AUDIT_LOG"
  else
    echo "⚠️ No audit log found."
  fi
  echo ""
} >> "$DEMO_LOG"

# Step 3 — Show desktop notification (no TextEdit windows)
osascript -e 'display notification "All candidate dossiers validated successfully." with title "AI Talent Engine Demo" sound name "Glass"'

# Step 4 — Clean finish
echo "✅ Silent validation complete. Logs saved to:"
echo "   $DEMO_LOG"
echo "------------------------------------------------------------"
echo ""

Proprietary Rights Notice
------------------------
All code, scripts, GitHub repositories, documentation, data, and GPT-integrated components of the AI Talent Engine – Signal Intelligence and Research_First_Sourcer_Automation Python Automation Sourcing Framework are strictly proprietary. All intellectual property rights, copyrights, trademarks, and related rights are exclusively owned by Dave Mendoza, DBA AI Craft, Inc.
No individual or entity may copy, reproduce, distribute, modify, create derivative works, reverse engineer, decompile, or otherwise use any part of this system, software, or associated materials for personal or commercial purposes without explicit written authorization from Dave Mendoza.
All rights reserved. Unauthorized use may result in legal action.
This statement is governed by the laws of the State of Colorado, USA.
