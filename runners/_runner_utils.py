#!/usr/bin/env python3
"""
AI Talent Engine – Phase & Track Runner Utilities
© 2025 L. David Mendoza. All rights reserved.

FINAL LOCKED EXECUTION CONTRACT
"""

import importlib
import inspect
import runpy
import sys
import traceback

ENTRYPOINTS = ("main", "cli_main", "run", "entrypoint")

PHASE_MODULES = {
    # Tracks
    "a": ["generate_synthetic_evaluations"],          # Track A
    "b": ["generate_synthetic_evaluations_full"],     # Track B (CONFIRMED)
    "c": ["citation_intelligence_api"],               # Track C

    # Phases
    "d": ["phase_d_escalation_flags"],
    "e": ["phase_e_conference_parser", "phase_e_emergence_detector"],
    "f": ["phase_f_velocity_analyzer", "phase_f_transition_detector"],
    "g": ["phase_g_signal_scoring", "phase_g_cluster_detector"],
}

def discover_and_run(phase, argv, verbose=False):
    last_error = None

    for module_name in PHASE_MODULES.get(phase, []):
        try:
            module = importlib.import_module(module_name)
        except Exception as e:
            last_error = e
            continue

        # Prefer callable entrypoints
        for ep in ENTRYPOINTS:
            if hasattr(module, ep) and callable(getattr(module, ep)):
                try:
                    fn = getattr(module, ep)
                    sig = inspect.signature(fn)
                    if len(sig.parameters) == 0:
                        return fn() or 0
                    return fn(argv) or 0
                except SystemExit as se:
                    return int(se.code) if isinstance(se.code, int) else 1
                except Exception:
                    if verbose:
                        traceback.print_exc()
                    return 1

        # Fallback: run as module
        try:
            old_argv = sys.argv[:]
            sys.argv = [module_name] + argv
            runpy.run_module(module_name, run_name="__main__")
            return 0
        except SystemExit as se:
            return int(se.code) if isinstance(se.code, int) else 1
        except Exception:
            if verbose:
                traceback.print_exc()
            return 1
        finally:
            sys.argv = old_argv

    if verbose:
        print(f"[runner] import failed for phase '{phase}': {last_error}", file=sys.stderr)
    return 1
