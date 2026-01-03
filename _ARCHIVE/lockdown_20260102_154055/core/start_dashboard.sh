#!/bin/bash
# ===========================================================
#  AI Talent Engine — Streamlit Dashboard Launcher
#  © 2025 L. David Mendoza — All Rights Reserved
# ===========================================================

DASHBOARD_SCRIPT="core/dashboard_connector.py"
LOG_FILE="logs/dashboard_startup.log"

echo "🔍 Running dashboard startup sequence..."
date +"[%Y-%m-%d %H:%M:%S] Dashboard startup initiated." >> "$LOG_FILE"

# --- Check Python ---
if ! command -v python3 &>/dev/null; then
  echo "❌ Python3 not found. Please install it first."
  exit 1
fi

# --- Check Streamlit ---
if ! python3 -m streamlit --version &>/dev/null; then
  echo "⚙️ Installing Streamlit..."
  python3 -m pip install --quiet streamlit
  echo "✅ Streamlit installed."
fi

# --- Check Dashboard Script ---
if [ ! -f "$DASHBOARD_SCRIPT" ]; then
  echo "❌ Dashboard script not found: $DASHBOARD_SCRIPT"
  exit 1
fi

# --- Kill any previous Streamlit processes ---
echo "🧹 Cleaning up previous Streamlit sessions..."
pkill -f "streamlit run" &>/dev/null

# --- Launch Streamlit ---
echo "🚀 Starting AI Talent Engine Dashboard..."
nohup python3 -m streamlit run "$DASHBOARD_SCRIPT" --server.headless true \
  >> "$LOG_FILE" 2>&1 &

sleep 3

# --- Open browser automatically ---
echo "🌐 Opening Safari to http://localhost:8501 ..."
open -a "Safari" http://localhost:8501

echo "✅ Dashboard live at http://localhost:8501"
echo "📄 Logs available at: $LOG_FILE"

