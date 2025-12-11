#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-Injection of Proprietary Notices
Author: Dave Mendoza
Purpose: Add single-line header and full proprietary footer to repo files and create standalone legal notice.
"""

import os
import shutil

# Resolve repo root dynamically based on the script's location
REPO_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
BACKUP_DIR = os.path.join(REPO_ROOT, "backup_proprietary_notice")

HEADER_LINE = "# © 2025 Dave Mendoza, DBA AI Craft, Inc. All rights reserved. Strictly proprietary; no copying, derivative works, reverse engineering, redistribution, or commercial/personal use permitted without written authorization. Governed by Colorado, USA law."

FOOTER_TEXT = """
Proprietary Rights Notice
------------------------
All code, scripts, GitHub repositories, documentation, data, and GPT-integrated components of the AI Talent Engine – Signal Intelligence and Research_First_Sourcer_Automation Python Automation Sourcing Framework are strictly proprietary. All intellectual property rights, copyrights, trademarks, and related rights are exclusively owned by Dave Mendoza, DBA AI Craft, Inc.
No individual or entity may copy, reproduce, distribute, modify, create derivative works, reverse engineer, decompile, or otherwise use any part of this system, software, or associated materials for personal or commercial purposes without explicit written authorization from Dave Mendoza.
All rights reserved. Unauthorized use may result in legal action.
This statement is governed by the laws of the State of Colorado, USA.
"""

LEGAL_FILE = os.path.join(REPO_ROOT, "Legal_Proprietary_Notice.txt")

HEADER_FILES = (".py", ".sh", ".command")
FOOTER_FILES = (".py", ".sh", ".command", ".md", ".txt")

os.makedirs(BACKUP_DIR, exist_ok=True)
updated_files = []

for root, dirs, files in os.walk(REPO_ROOT):
    for f in files:
        filepath = os.path.join(root, f)
        relpath = os.path.relpath(filepath, REPO_ROOT)

        # Skip backup directory itself
        if BACKUP_DIR in filepath:
            continue

        ext = os.path.splitext(f)[1].lower()

        # Skip binaries
        if ext in (".xlsx", ".xls", ".csv", ".png", ".jpg", ".jpeg", ".gif"):
            continue

        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()
        except Exception:
            continue  # Skip unreadable files

        modified = False

        # Backup original file
        backup_path = os.path.join(BACKUP_DIR, relpath.replace("/", "__"))
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        shutil.copy2(filepath, backup_path)

        # Insert header if missing
        if ext in HEADER_FILES and HEADER_LINE not in content:
            lines = content.splitlines()
            # If a shebang exists, header goes after line 0
            shebang_idx = 1 if (lines and lines[0].startswith("#!")) else 0
            lines.insert(shebang_idx, HEADER_LINE)
            content = "\n".join(lines)
            modified = True

        # Append footer if missing
        if ext in FOOTER_FILES and FOOTER_TEXT.strip() not in content:
            content = content.rstrip() + "\n\n" + FOOTER_TEXT.strip() + "\n"
            modified = True

        if modified:
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(content)
            updated_files.append(relpath)

# Write standalone legal file
with open(LEGAL_FILE, "w", encoding="utf-8") as f:
    f.write(FOOTER_TEXT.strip() + "\n")

print(f"Applied proprietary notices to {len(updated_files)} file(s).")
print(f"Legal statement created: {LEGAL_FILE}")
print(f"Backups stored in: {BACKUP_DIR}")

if updated_files:
    print("Updated files:")
    for uf in updated_files:
        print(f" - {uf}")
