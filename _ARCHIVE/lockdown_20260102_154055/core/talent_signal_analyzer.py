import pandas as pd, glob, os
out='output/ai_talent_master_dataset.csv'
frames=[pd.read_csv(f) for f in glob.glob('output/*.csv') if f.endswith('.csv')]
if frames: pd.concat(frames).to_csv(out,index=False); print('✅ Master dataset written →',out)
else: print('⚠️ No CSVs found for aggregation.')
