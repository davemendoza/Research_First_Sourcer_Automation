#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/completion_notifier.py
============================================================
RUN COMPLETION NOTIFIER (FAIL-OPEN)

Maintainer: L. David Mendoza © 2026
Version: v1.0.0

Purpose
- Always print completion summary
- Optionally send macOS notification (osascript)
- Optionally send email via SMTP (if configured)
- NEVER fails the pipeline (fail-open)

Env (optional)
- AI_TALENT_NOTIFY_MAC=1
- AI_TALENT_NOTIFY_EMAIL_TO=<email>
- AI_TALENT_SMTP_HOST
- AI_TALENT_SMTP_PORT
- AI_TALENT_SMTP_USER
- AI_TALENT_SMTP_PASS

Validation
python3 -c "from EXECUTION_CORE.completion_notifier import notify; notify('demo','x','ok','/tmp/a.csv',123,'00:01')"

Git Commands
git add EXECUTION_CORE/completion_notifier.py
git commit -m "Add fail-open completion notifier (macOS + optional SMTP)"
git push
"""

from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage


def _try_macos_notify(title: str, message: str) -> None:
    if os.environ.get("AI_TALENT_NOTIFY_MAC", "").strip() not in ("1", "true", "yes"):
        return
    try:
        import subprocess
        script = f'display notification "{message}" with title "{title}"'
        subprocess.run(["osascript", "-e", script], check=False)
    except Exception:
        return


def _try_email_notify(subject: str, body: str) -> None:
    to_addr = (os.environ.get("AI_TALENT_NOTIFY_EMAIL_TO") or "").strip()
    host = (os.environ.get("AI_TALENT_SMTP_HOST") or "").strip()
    port = int((os.environ.get("AI_TALENT_SMTP_PORT") or "587").strip() or "587")
    user = (os.environ.get("AI_TALENT_SMTP_USER") or "").strip()
    pwd = (os.environ.get("AI_TALENT_SMTP_PASS") or "").strip()

    if not (to_addr and host and user and pwd):
        return

    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = user
        msg["To"] = to_addr
        msg.set_content(body)

        with smtplib.SMTP(host, port, timeout=10) as s:
            s.starttls()
            s.login(user, pwd)
            s.send_message(msg)
    except Exception:
        return


def notify(mode: str, role: str, status: str, out_csv: str, rows: int, elapsed_hhmmss: str) -> None:
    title = f"AI Talent Engine: {status}"
    msg = f"{mode} | {role} | rows={rows} | elapsed={elapsed_hhmmss}"

    print("\nNOTIFY")
    print("Status:", status)
    print("Mode:", mode)
    print("Role:", role)
    print("Rows:", rows)
    print("Elapsed:", elapsed_hhmmss)
    print("Output:", out_csv)

    _try_macos_notify(title, msg)
    _try_email_notify(
        subject=title,
        body=f"{msg}\nOutput: {out_csv}\n",
    )


__all__ = ["notify"]
