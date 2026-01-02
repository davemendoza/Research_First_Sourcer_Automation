#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
send_run_completion_email.py
Version: v1.1.0
Author: L. David Mendoza
Date: 2026-01-02
© 2025–2026 L. David Mendoza. All rights reserved.

Purpose:
- Send a completion email using macOS Mail.app via AppleScript
- Deterministic subject/body including manifest path

Usage:
  python3 scripts/send_run_completion_email.py <manifest_json_path>

Env:
  PIPELINE_NOTIFY_TO  (default: LDaveMendoza@gmail.com)
  PIPELINE_NOTIFY_SUBJECT_PREFIX (default: "RUN COMPLETE")
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timezone

def die(msg: str, code: int = 2) -> None:
    print(f"ERROR: {msg}")
    sys.exit(code)

if len(sys.argv) != 2:
    die("USAGE: send_run_completion_email.py <manifest_json_path>", 2)

manifest_path = Path(sys.argv[1]).resolve()
if not manifest_path.exists():
    die(f"Manifest not found: {manifest_path}", 2)

to_addr = os.getenv("PIPELINE_NOTIFY_TO", "LDaveMendoza@gmail.com").strip()
prefix = os.getenv("PIPELINE_NOTIFY_SUBJECT_PREFIX", "RUN COMPLETE").strip()

try:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
except Exception as e:
    die(f"Unable to parse manifest JSON: {e}", 3)

scenario = str(manifest.get("scenario","")).strip() or "unknown"
run_id = str(manifest.get("run_id","")).strip() or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
leads_csv = str(manifest.get("leads_master_csv","") or manifest.get("leads_csv","") or "").strip()

subject = f"{prefix} — {scenario} — {run_id}"
body_lines = [
    f"Run complete (UTC): {manifest.get('completed_utc','')}",
    f"Scenario: {scenario}",
    "",
    f"Leads CSV: {leads_csv}",
    f"Manifest: {str(manifest_path)}",
    "",
    "This message was generated automatically by the Universal Lead Pipeline.",
]
body = "\\n".join(body_lines).replace('"', "'")

# Hard require osascript
try:
    subprocess.run(["osascript", "-e", "return 0"], check=True, capture_output=True, text=True)
except Exception as e:
    die(f"osascript not available or failed: {e}", 4)

# AppleScript to create and send message in Mail.app
applescript = f'''
tell application "Mail"
    set newMessage to make new outgoing message with properties {{subject:"{subject}", content:"{body}" & return & return, visible:false}}
    tell newMessage
        make new to recipient at end of to recipients with properties {{address:"{to_addr}"}}
        send
    end tell
end tell
'''

subprocess.run(["osascript", "-e", applescript], check=True)
print(f"OK: completion email sent to {to_addr}")
