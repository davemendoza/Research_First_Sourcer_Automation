from pathlib import Path

ALLOWED = {
    "_ARCHIVE_INTERNAL",
    "demo",
    "gpt_slim",
    "scenario",
    "inventory",  # archival, non-runtime
}

def enforce_outputs_root_clean(repo_root: Path):
    outputs = repo_root / "OUTPUTS"

    if not outputs.exists():
        return  # nothing to enforce yet

    for p in outputs.iterdir():
        # inventory is archival, never runtime-enforced
        if p.name == "inventory":
            continue

        if p.name not in ALLOWED:
            raise RuntimeError(
                f"OUTPUTS root contract violated: unexpected directory at OUTPUTS/: {p.name}\n"
                f"Allowed: {sorted(ALLOWED)}"
            )
