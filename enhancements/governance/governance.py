from enhancements.core import feature_flags, registry, guardrails

registry.register("GOVERNANCE", feature_flags.FEATURE_FLAGS["governance_enabled"])
guardrails.assert_core_immutable()

def audit():
    if not feature_flags.FEATURE_FLAGS["governance_enabled"]:
        return None
    return "Audit enabled"
