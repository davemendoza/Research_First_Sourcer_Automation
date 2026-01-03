#!/usr/bin/env python3
"""
AI Talent Engine — Scenario Completion Notifier

Sends an email when a long or unattended scenario run completes.
Designed for routine runs with hundreds or thousands of results.
"""

import smtplib
from email.message import EmailMessage
from datetime import datetime
import sys

# =====================================================
# CONFIGURATION — EDIT ONCE
# =====================================================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SMTP_USER = "YOUR_EMAIL@gmail.com"
SMTP_APP_PASSWORD = "YOUR_GMAIL_APP_PASSWORD"

TO_EMAIL = "YOUR_EMAIL@gmail.com"
# =====================================================

scenario = sys.argv[1] if len(sys.argv) > 1 else "unknown"

msg = EmailMessage()
msg["From"] = SMTP_USER
msg["To"] = TO_EMAIL
msg["Subject"] = f"AI Talent Engine Run Complete — {scenario}"

msg.set_content(
    f"""
Your AI Talent Engine scenario run has completed successfully.

Scenario: {scenario}
Completed at: {datetime.now().isoformat(timespec="seconds")}

You can now return to your computer to review the results.

— AI Talent Engine
""".strip()
)

try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_APP_PASSWORD)
        server.send_message(msg)

    print("Run completion email sent.")

except Exception as e:
    print("ERROR: Failed to send completion email.")
    print(str(e))
    sys.exit(1)
