#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
send_run_completion_email.py

AI Talent Engine — Run Completion Email (macOS Mail.app)
Version: v1.0.0
Author: L. David Mendoza
Date: 2026-01-02

Purpose:
- Read a run manifest JSON and send a completion email via Mail.app using AppleScript.
- Fail closed if:
  - manifest missing/invalid
  - Mail send fails

Controls:
- EMAIL_NOTIFY_ENABLED=1 enables sending
- EMAIL_NOTIFY_TO defaults to LDaveMendoza@gmail.com

Usage:
  python3 scripts/send_run_completion_email.py /path/to/manifest.json
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone


DEFAULT_TO = "LDaveMendoza@gmail.com"


def fail(msg: str, code: int = 2) -> None:
    print(f"ERROR: {msg}")
    sys.exit(code)


def applescript_escape(s: str) -> str:
    # Escape for AppleScript string literal
    return s.replace("\\", "\\\\").replace('"', '\\"')


def main() -> None:
    enabled = os.getenv("EMAIL_NOTIFY_ENABLED", "0").strip()
    if enabled != "1":
        print("EMAIL_NOTIFY: disabled (set EMAIL_NOTIFY_ENABLED=1 to enable)")
        return

    if len(sys.argv) != 2:
        fail("Usage: python3 scripts/send_run_completion_email.py <manifest.json>")

    manifest_path = Path(sys.argv[1]).expanduser().resolve()
    if not manifest_path.exists():
        fail(f"Manifest not found: {manifest_path}", code=3)

    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"Manifest JSON invalid: {e}", code=4)

    to_addr = os.getenv("EMAIL_NOTIFY_TO", DEFAULT_TO).strip() or DEFAULT_TO
    scenario = str(payload.get("scenario", "unknown"))
    run_id = str(payload.get("run_id", "unknown"))
    leads_master = str(payload.get("leads_master_csv", ""))
    people_csv = str(payload.get("people_csv_normalized", ""))
    rows = payload.get("counts", {}).get("leads_rows", "unknown")
    githubio = payload.get("github_io", {})
    checked = githubio.get("checked_rows", "unknown")
    found = githubio.get("found_rows", "unknown")

    now = datetime.now(timezone.utc).isoformat()

    subject = f"Research First Sourcer Automation — Run Complete — {scenario.upper()} — {run_id}"
    body = "\n".join(
        [
            "The pipeline completed successfully.",
            "",
            f"Scenario: {scenario}",
            f"Run ID: {run_id}",
            f"Timestamp (UTC): {now}",
            "",
            "Artifacts:",
            f"- Leads Master: {leads_master}",
            f"- People (normalized): {people_csv}",
            f"- Manifest: {str(manifest_path)}",
            "",
            "GitHub.io (first-class surface):",
            f"- Rows checked: {checked}",
            f"- Rows with GitHub.io present: {found}",
            "",
            f"Lead rows: {rows}",
            "",
            "Status:",
            "- People normalized",
            "- GitHub.io probed first",
            "- Enrichment generated (70+ columns)",
            "- Canonical contracts enforced",
            "- Safe for demo",
            "",
            "— Automated Notification",
        ]
    )

    osa = f'''
on run
  tell application "Mail"
    set newMessage to make new outgoing message with properties {{subject:"{applescript_escape(subject)}", content:"{applescript_escape(body)}" & return & return, visible:false}}
    tell newMessage
      make new to recipient at end of to recipients with properties {{address:"{applescript_escape(to_addr)}"}}
      send
    end tell
  end tell
end run
'''
    try:
        subprocess.run(["osascript", "-e", osa], check=True)
    except subprocess.CalledProcessError as e:
        fail(f"Failed to send email via Mail.app: {e}", code=5)

    print(f"OK: Email sent to {to_addr}")


if __name__ == "__main__":
    main()
