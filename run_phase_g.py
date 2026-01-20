#!/usr/bin/env python3
"""
AI Talent Engine – Phase g Runner
© 2025 L. David Mendoza. All rights reserved.
"""

import argparse
import sys
from runners._runner_utils import discover_and_run

def main():
    parser = argparse.ArgumentParser(
        description="AI Talent Engine Phase g Runner"
    )
    parser.add_argument("--verbose", action="store_true")
    args, remainder = parser.parse_known_args()
    return discover_and_run("g", remainder, verbose=args.verbose)

if __name__ == "__main__":
    sys.exit(main())
