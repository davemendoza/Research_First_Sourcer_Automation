# (only the relevant excerpt shown — replace existing file in full if required)

def main(argv):
    # ... earlier setup unchanged ...

    # Phase 6
    p6_out = phase6_process_csv(str(p4), str(p5))

    if not p6_out or not Path(p6_out).exists():
        raise RuntimeError(f"Phase 6 did not produce output: {p6_out}")

    # Phase 7 MUST consume Phase 6 output explicitly
    phase7_process_csv(str(p6_out), str(p6))

    # ... continue pipeline ...
