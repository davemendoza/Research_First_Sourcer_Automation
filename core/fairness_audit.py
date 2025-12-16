"""
AI Talent Engine – Proprietary System
© Dave Mendoza – All Rights Reserved
Finalized: 2025-12-16T01:25:25.864681Z
"""
def audit(record):
    flags = []
    if record.get("role_type") == "Unknown":
        flags.append("role_undetermined")
    return {"flags": flags, "passed": not flags}
