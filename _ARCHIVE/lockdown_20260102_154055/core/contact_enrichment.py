#!/usr/bin/env python3
import pandas as pd, os
input_path='output/ai_talent_master_dataset.csv'
if not os.path.exists(input_path):
    print('⚠️ Master dataset not found.')
else:
    df=pd.read_csv(input_path)
    contact_cols=[c for c in df.columns if 'email' in c.lower() or 'linkedin' in c.lower()]
    if not contact_cols:
        print('ℹ️ No contact columns detected.')
    else:
        missing=df[contact_cols].isna().sum().sum()
        print(f'✅ Contact columns found: {contact_cols} — {missing} missing values.')
