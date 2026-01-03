from pathlib import Path
import shutil

def promote_people_master_to_leads(scenario: str, run_id: str):
    people_master = Path("outputs/people/people_master.csv")
    if not people_master.exists():
        raise RuntimeError("people_master.csv not produced")

    leads_dir = Path("outputs/leads") / f"run_{run_id}"
    leads_dir.mkdir(parents=True, exist_ok=True)

    leads_path = leads_dir / f"LEADS_MASTER_{scenario}_{run_id}.csv"
    shutil.copy(people_master, leads_path)

    print(f"✅ LEADS_MASTER written → {leads_path}")
    return leads_path
