#!/usr/bin/env python3
# © 2025 Dave Mendoza, DBA AI Craft, Inc. All rights reserved.
# ============================================================
#  auto_inject_legal.py
#  Injects proprietary legal notices across project files.
#  Excludes .git/ and backup directories for safety.
# ============================================================

import os
import shutil
import datetime

# Root of your repo
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Backup directory
backup_dir = os.path.join(repo_root, "backup_proprietary_notice")
os.makedirs(backup_dir, exist_ok=True)

# Legal statement text
legal_text = (
    "# ===============================================\n"
    "#  © 2025 Dave Mendoza, DBA AI Craft, Inc. All rights reserved.\n"
    "#  Proprietary and Confidential — Unauthorized copying or distribution is prohibited.\n"
    "# ===============================================\n\n"
)

# Paths to skip
EXCLUDED_FOLDERS = {".git", "backup_proprietary_notice", "__pycache__"}
EXCLUDED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".csv", ".xlsx"}

# Stats
updated_files = []
skipped_files = []

print("")
print("===============================================")
print(" Running proprietary legal injection sweep...")
print("===============================================")
print("")

# Walk repo safely
for root, dirs, files in os.walk(repo_root):
    # Skip unwanted directories
    if any(skip in root for skip in EXCLUDED_FOLDERS):
        continue

    for filename in files:
        filepath = os.path.join(root, filename)
        ext = os.path.splitext(filename)[1].lower()

        # Skip binary or irrelevant files
        if ext in EXCLUDED_EXTENSIONS:
            skipped_files.append(filepath)
            continue

        try:
            # Read file
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Skip if notice already exists
            if "© 2025 Dave Mendoza" in content:
                continue

            # Backup original safely
            rel_path = os.path.relpath(filepath, repo_root)
            backup_path = os.path.join(backup_dir, rel_path.replace("/", "__"))
            os.makedirs(os.path.dirname(backup_dir), exist_ok=True)
            shutil.copy2(filepath, backup_path)

            # Prepend legal text
            new_content = legal_text + content
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)

            updated_files.append(rel_path)

        except PermissionError:
            print(f"⚠️  Permission denied: {filepath}")
        except Exception as e:
            print(f"⚠️  Error processing {filepath}: {e}")

# Generate legal statement
legal_notice_path = os.path.join(repo_root, "Legal_Proprietary_Notice.txt")
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with open(legal_notice_path, "w", encoding="utf-8") as f:
    f.write(f"AI Talent Engine Legal Injection Summary\n")
    f.write(f"Timestamp: {timestamp}\n")
    f.write(f"Updated files: {len(updated_files)}\n\n")
    for fpath in updated_files:
        f.write(f" - {fpath}\n")

print("")
print(f"Applied proprietary notices to {len(updated_files)} file(s).")
print(f"Legal statement created: {legal_notice_path}")
print(f"Backups stored in: {backup_dir}")

if skipped_files:
    print(f"Skipped {len(skipped_files)} non-source or excluded files.")
print("")
print("===============================================")
print("  Legal injection sweep completed successfully. ")
print("===============================================")
