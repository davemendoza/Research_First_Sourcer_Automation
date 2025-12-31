# © 2025 Dave Mendoza, DBA AI Craft, Inc. All rights reserved. Strictly proprietary; no copying, derivative works, reverse engineering, redistribution, or commercial/personal use permitted without written authorization. Governed by Colorado, USA law.
import frontmatter, os

# Path to your schema file
schema_path = os.path.expanduser("~/Desktop/Research_First_Sourcer_Automation/AI_Talent_Schema_Rules.md")

# Load the Markdown front-matter
post = frontmatter.load(schema_path)
schema = post.metadata

# Display schema version and main keys
print(f"✅ Loaded schema version {schema.get('version')} OK\n")
print("Top-level keys found:")
for key in schema.keys():
    print(f" - {key}")

Proprietary Rights Notice
------------------------
All code, scripts, GitHub repositories, documentation, data, and GPT-integrated components of the AI Talent Engine – Signal Intelligence and Research_First_Sourcer_Automation Python Automation Sourcing Framework are strictly proprietary. All intellectual property rights, copyrights, trademarks, and related rights are exclusively owned by Dave Mendoza, DBA AI Craft, Inc.
No individual or entity may copy, reproduce, distribute, modify, create derivative works, reverse engineer, decompile, or otherwise use any part of this system, software, or associated materials for personal or commercial purposes without explicit written authorization from Dave Mendoza.
All rights reserved. Unauthorized use may result in legal action.
This statement is governed by the laws of the State of Colorado, USA.
