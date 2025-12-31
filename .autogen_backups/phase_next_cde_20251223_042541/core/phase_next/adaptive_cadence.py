from datetime import timedelta

TIER_TO_CADENCE = {
    "T0": timedelta(days=90),
    "T1": timedelta(days=30),
    "T2": timedelta(days=14),
    "T3": timedelta(days=7),
}

def plan_from_tier(tier):
    return TIER_TO_CADENCE.get(tier or "T0", TIER_TO_CADENCE["T0"])
