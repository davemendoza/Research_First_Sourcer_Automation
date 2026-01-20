from pathlib import Path

ALLOWED = {"_ARCHIVE_INTERNAL", "demo", "gpt_slim", "scenario"}

def enforce_outputs_root_clean(repo_root: Path):
    outputs = repo_root / "OUTPUTS"
    for p in outputs.iterdir():
        if p.name == "inventory":
            continue  # inventory is archival, never runtime
        if p.name not in ALLOWED:
            raise RuntimeError(
                f"OUTPUTS root contract violated: unexpected directory at OUTPUTS/: {p.name}\n"
                f"Allowed: {sorted(ALLOWED)}"
            )
