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
