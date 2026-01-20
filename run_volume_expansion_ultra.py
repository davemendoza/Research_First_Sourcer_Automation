#!/usr/bin/env python3
"""
Run Volume Expansion (Scenario expansion + People expansion)
© 2025 L. David Mendoza
"""
import subprocess, sys

def run(cmd):
    print(f"▶️  {' '.join(cmd)}")
    r = subprocess.run(cmd)
    if r.returncode != 0:
        sys.exit(r.returncode)

def main():
    run(["python3", "scenario_matrix_builder_ultra.py"])
    run(["python3", "people_volume_expander_ultra.py"])
    print("\n✅ Volume expansion run complete.")
    print("Next:")
    print("  python3 people_enrichment.py   (will enrich latest output/people/VOL_* / people_master.csv)")
    print("  python3 frontier_scientist_radar.py (after enrichment)")
if __name__ == "__main__":
    main()
