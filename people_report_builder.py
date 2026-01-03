import pandas as pd
from pathlib import Path
from contracts.canonical_people_schema import enforce_canonical

def write_outputs(people, outdir):
    Path(outdir).mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(people)
    csv_path = Path(outdir) / "people_master.csv"
    xlsx_path = Path(outdir) / "people_master.xlsx"
df = enforce_canonical(df)
    df.to_csv(csv_path, index=False)
    df.to_excel(xlsx_path, index=False)
    return csv_path, xlsx_path
