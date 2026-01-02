#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
macos_notify.py
Version: v1.0.0
Author: L. David Mendoza
Date: 2026-01-02
© 2025–2026 L. David Mendoza. All rights reserved.

Purpose:
- Trigger a macOS Notification Center popup (no dependencies)

Usage:
  python3 scripts/macos_notify.py "<title>" "<message>"
"""

import subprocess
import sys

if len(sys.argv) != 3:
    print("USAGE: macos_notify.py <title> <message>")
    sys.exit(2)

title = (sys.argv[1] or "").replace('"', "'")
message = (sys.argv[2] or "").replace('"', "'")

# Fail if osascript is missing (hard requirement for your "I can breathe" signal)
try:
    subprocess.run(["osascript", "-e", "return 0"], check=True, capture_output=True, text=True)
except Exception as e:
    print(f"ERROR: osascript not available or failed: {e}")
    sys.exit(3)

script = f'display notification "{message}" with title "{title}"'
subprocess.run(["osascript", "-e", script], check=True)
print("OK: popup notification sent")
