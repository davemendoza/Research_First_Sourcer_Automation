#!/usr/bin/env python3
"""
AI Talent Engine — Track D Full Generator
© 2025 L. David Mendoza

Purpose:
- Autogenerate / overwrite ALL Track D files
- No snippets
- No mutation of Seed Hub workbook
"""

from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parents[1]

FILES = {
    "requirements_track_d.txt": """
requests>=2.31.0
openpyxl>=3.1.2
pydantic>=2.6.0
python-dateutil>=2.9.0.post0
beautifulsoup4>=4.12.2
lxml>=5.1.0
""",

    "tracks/track_d/__init__.py": """
\"\"\"Track D — Discovery + Evidence Intake\"\"\"
""",

    "tracks/track_d/adapter_registry.py": """
from .adapters.repo_contrib_adapter import RepoContribAdapter

SEED_HUB_TYPE_TO_ADAPTER = {
    "GitHub_Repo_Contributors": RepoContribAdapter,
}
""",

    "scenarios/run_s13_s15_track_d.py": """
import subprocess, sys

if __name__ == "__main__":
    scenario = sys.argv[1]
    subprocess.check_call([
        sys.executable, "-m", "tracks.track_d.run_track_d",
        "--scenario", scenario
    ])
"""
}

def main():
    for rel, content in FILES.items():
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content).lstrip())
        print(f"WROTE: {rel}")

if __name__ == "__main__":
    main()
