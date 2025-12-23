from enhancements.core import feature_flags, registry, guardrails

registry.register("DEMO_MODE", feature_flags.FEATURE_FLAGS["demo_mode_enabled"])
guardrails.assert_core_immutable()

def demo():
    if not feature_flags.FEATURE_FLAGS["demo_mode_enabled"]:
        return None
    return "Demo mode active"
