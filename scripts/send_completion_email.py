#!/usr/bin/env python3
"""
send_completion_email.py

Universal Run Completion Notifier (macOS Mail)
Version: v1.0.0
Author: L. David Mendoza
Date: 2026-01-02

Purpose:
- Send a completion email via native macOS Mail.app
- Driven by a run manifest JSON
- Fail-open (never blocks pipeline)
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

if len(sys.argv) != 2:
    print("USAGE: send_completion_email.py <run_manifest.json>")
    sys.exit(2)

manifest_path = Path(sys.argv[1])
if not manifest_path.exists():
    print(f"EMAIL_NOTIFY: manifest not found: {manifest_path}")
    sys.exit(0)

with manifest_path.open(encoding="utf-8") as f:
    manifest = json.load(f)

scenario = manifest.get("scenario", "UNKNOWN")
people_raw = manifest.get("people_csv_raw", "N/A")
people_norm = manifest.get("people_csv_normalized", "N/A")
outputs_dir = manifest.get("scenario_outputs_dir", "N/A")
timestamp = manifest.get("completed_utc", datetime.now(timezone.utc).isoformat())

recipient = "LDaveMendoza@gmail.com"
subject = f"Pipeline Complete — {scenario}"

body = f"""Pipeline run completed successfully.

Scenario:
  {scenario}

People CSV (raw):
  {people_raw}

People CSV (normalized):
  {people_norm}

Scenario outputs:
  {outputs_dir}

Completed (UTC):
  {timestamp}

This run passed:
- Repo inventory gate
- People inventory gate
- Canonical Person_ID / Role_Type enforcement
- Demo bounds validation
- Scenario contract enforcement

This message was sent automatically.
"""

applescript = f'''
tell application "Mail"
    set newMessage to make new outgoing message with properties {{
        subject:"{subject}",
        content:"{body}",
        visible:false
    }}
    tell newMessage
        make new to recipient at end of to recipients with properties {{address:"{recipient}"}}
        send
    end tell
end tell
'''

try:
    subprocess.run(
        ["osascript", "-e", applescript],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print("EMAIL_NOTIFY: completion email sent via Mail.app")
except Exception as e:
    print(f"EMAIL_NOTIFY: failed (non-blocking): {e}")
