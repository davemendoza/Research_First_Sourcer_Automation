#!/usr/bin/env python3
import pandas as pd, os

SRC = os.path.expanduser("data/phase6_output_fixed.csv")
DST = os.path.expanduser("data/phase6_output_fixed_clean.csv")

df = pd.read_csv(SRC)
required_cols = [
    "unique_id", "full_name", "organization", "job_title",
    "email", "phone", "linkedin_url", "github_url", "huggingface_url",
    "patent_urls", "publication_urls", "portfolio_url", "cv_link",
    "signal_score", "influence_math", "influence_percentile",
    "key_determinant_skills", "likely_ai_role_type", "source_provenance"
]
for col in required_cols:
    if col not in df.columns:
        df[col] = ""
df.to_csv(DST, index=False)
print(f"✅ Fixed schema written: {DST}")
