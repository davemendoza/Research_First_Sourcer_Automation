#!/usr/bin/env python3
"""
people_scenario_resolver.py
---------------------------------------
Purpose:
Resolve scenario parameters and orchestrate a single,
deterministic people pipeline run per scenario.

Guarantees:
• ONE scenario → ONE CSV
• No subfolders
• No enrichment logic
• No schema logic
• Explicit scenario naming
"""

import sys
from pathlib import Path


def resolve_scenario(scenario_name: str):
    """
    Map scenario name to prefix and seed config.
    This file DOES NOT run enrichment; it only resolves intent.
    """

    scenario_name = scenario_name.strip().lower()

    if scenario_name in ("demo", "demo_frontier", "frontier"):
        return {
            "prefix": "demo_frontier_ai_scientist",
            "seed": "frontier_ai_scientist",
        }

    if scenario_name in ("gpt_slim", "slim"):
        return {
            "prefix": "gpt_slim_frontier_ai_scientist",
            "seed": "frontier_ai_scientist",
        }

    # Default: treat scenario name as-is
    return {
        "prefix": scenario_name.replace(" ", "_"),
        "seed": scenario_name,
    }


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: people_scenario_resolver.py <scenario_name>",
            file=sys.stderr,
        )
        sys.exit(1)

    scenario = sys.argv[1]
    resolved = resolve_scenario(scenario)

    # Emit resolved scenario as simple stdout contract
    print(f"SCENARIO_PREFIX={resolved['prefix']}")
    print(f"SCENARIO_SEED={resolved['seed']}")


if __name__ == "__main__":
    main()
