"""
AI Talent Engine – Proprietary System
© Dave Mendoza – All Rights Reserved
Finalized: 2025-12-16T01:25:25.864681Z
"""
def validate_schema(record):
    required = ["id", "role_type", "signals"]
    missing = [k for k in required if k not in record]
    return {"valid": not missing, "missing": missing}
