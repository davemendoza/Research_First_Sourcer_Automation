# © 2025 Dave Mendoza, DBA AI Craft, Inc. All rights reserved. Strictly proprietary; no copying, derivative works, reverse engineering, redistribution, or commercial/personal use permitted without written authorization. Governed by Colorado, USA law.
import pandas as pd
import re

def safe_text(x) -> str:
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return ""
    return str(x)

def count_matches(text: str, terms) -> int:
    t = safe_text(text).lower()
    return sum(1 for k in terms if k in t)

def slugify(name: str) -> str:
    s = safe_text(name)
    s = re.sub(r"[^a-zA-Z0-9_-]+", "_", s)
    return s[:80] if s else "candidate"

Proprietary Rights Notice
------------------------
All code, scripts, GitHub repositories, documentation, data, and GPT-integrated components of the AI Talent Engine – Signal Intelligence and Research_First_Sourcer_Automation Python Automation Sourcing Framework are strictly proprietary. All intellectual property rights, copyrights, trademarks, and related rights are exclusively owned by Dave Mendoza, DBA AI Craft, Inc.
No individual or entity may copy, reproduce, distribute, modify, create derivative works, reverse engineer, decompile, or otherwise use any part of this system, software, or associated materials for personal or commercial purposes without explicit written authorization from Dave Mendoza.
All rights reserved. Unauthorized use may result in legal action.
This statement is governed by the laws of the State of Colorado, USA.
