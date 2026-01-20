from contracts.canonical_people_schema import enforce_canonical
#!/usr/bin/env python3
import pandas as pd, os

SRC = os.path.expanduser("~/Desktop/Research_First_Sourcer_Automation/data/frontier_phase7_enriched.csv")
DST = os.path.expanduser("~/Desktop/Research_First_Sourcer_Automation/data/frontier_phase7_enriched_fixed.csv")

if not os.path.exists(SRC):
    print(f"❌ Missing source file: {SRC}")
    exit(1)

df = pd.read_csv(SRC)

rename_map = {
    "Full Name": "full_name",
    "Citations_Raw": "citations_raw",
    "Citation_Normalized": "citation_normalized",
    "Citation_Tier": "citation_tier",
    "GitHub_IO_URL": "github_io_url",
    "Resume_Link": "resume_link"
}
df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

required_cols = [
    "full_name", "organization", "affiliation", "likely_ai_role_type",
    "signal_skill_tier", "key_determinant_skills", "citation_normalized",
    "citation_tier", "github_io_url", "linkedin_url", "resume_link",
    "email", "phone", "source_provenance"
]

for col in required_cols:
    if col not in df.columns:
        df[col] = "UNKNOWN"

df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

df = enforce_canonical(df)
df.to_csv(DST, index=False)
print(f"✅ Fixed Phase 7 file written: {DST}")
