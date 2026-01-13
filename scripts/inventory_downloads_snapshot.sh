#!/usr/bin/env bash
echo "▶ External Artifacts Snapshot (~/Downloads)"
echo "----------------------------------------"

DOWNLOADS="$HOME/Downloads"

if [ ! -d "$DOWNLOADS" ]; then
  echo "Downloads folder not found"
  exit 0
fi

# Show only likely-relevant artifacts
ls -lh "$DOWNLOADS" | egrep -i '\.(csv|xlsx|xls|json|docx|pdf|zip)$' || echo "No matching artifacts found"
