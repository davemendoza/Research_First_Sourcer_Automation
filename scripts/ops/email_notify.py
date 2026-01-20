#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Talent Engine – Research-First Sourcer Automation
Module: Email Notification (SMTP, Success/Failure)
Version: v1.0.0-day1-notify
Date: 2025-12-30
Author: Dave Mendoza
© 2025 L. David Mendoza. All Rights Reserved.

Purpose
- Send a completion email when a run succeeds or fails.
- Uses plain SMTP with environment variables.
- No Slack, no webhook.

Environment Variables
- RFS_SMTP_HOST
- RFS_SMTP_PORT (default 587)
- RFS_SMTP_USER
- RFS_SMTP_PASS
- RFS_EMAIL_FROM
- RFS_EMAIL_TO (comma-separated)

Optional
- RFS_SMTP_TLS (default true)

Contract Requirements Satisfied
- Explicit Python 3
- No hidden side effects unless called
- Full-file generation only

Validation Steps
1) python3 -c "from scripts.ops.email_notify import EmailNotifier; print('OK')"
2) Set env vars and call send_test()
"""

from __future__ import annotations

import os
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from typing import Optional


def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    v = os.environ.get(name)
    if v is None or v.strip() == "":
        return default
    return v.strip()


@dataclass
class EmailNotifier:
    host: str
    port: int
    user: Optional[str]
    password: Optional[str]
    email_from: str
    email_to: str
    use_tls: bool = True

    @classmethod
    def from_env(cls) -> "EmailNotifier":
        host = _env("RFS_SMTP_HOST")
        if not host:
            raise RuntimeError("Missing env var: RFS_SMTP_HOST")
        port = int(_env("RFS_SMTP_PORT", "587"))
        user = _env("RFS_SMTP_USER")
        password = _env("RFS_SMTP_PASS")
        email_from = _env("RFS_EMAIL_FROM")
        email_to = _env("RFS_EMAIL_TO")
        if not email_from:
            raise RuntimeError("Missing env var: RFS_EMAIL_FROM")
        if not email_to:
            raise RuntimeError("Missing env var: RFS_EMAIL_TO")
        use_tls = (_env("RFS_SMTP_TLS", "true") or "true").lower() in ("1", "true", "yes", "y")
        return cls(host=host, port=port, user=user, password=password, email_from=email_from, email_to=email_to, use_tls=use_tls)

    def _build_message(self, subject: str, body: str) -> EmailMessage:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.email_from
        msg["To"] = self.email_to
        msg.set_content(body)
        return msg

    def send(self, subject: str, body: str) -> None:
        msg = self._build_message(subject, body)
        with smtplib.SMTP(self.host, self.port, timeout=30) as s:
            if self.use_tls:
                s.starttls()
            if self.user and self.password:
                s.login(self.user, self.password)
            s.send_message(msg)

    def send_run_success(self, run_id: str, out_dir: str, summary: str) -> None:
        subject = f"✅ RFS Run Complete: {run_id}"
        body = f"Run ID: {run_id}\nOutput: {out_dir}\n\nSummary:\n{summary}\n"
        self.send(subject, body)

    def send_run_failure(self, run_id: str, out_dir: str, err: str) -> None:
        subject = f"❌ RFS Run Failed: {run_id}"
        body = f"Run ID: {run_id}\nOutput: {out_dir}\n\nError:\n{err}\n"
        self.send(subject, body)

    def send_test(self) -> None:
        self.send("RFS SMTP Test", "If you received this, SMTP notifications are wired correctly.")
