from enhancements.core import feature_flags, registry, guardrails

registry.register("SCALING", feature_flags.FEATURE_FLAGS["scaling_enabled"])
guardrails.assert_core_immutable()

def scale():
    if not feature_flags.FEATURE_FLAGS["scaling_enabled"]:
        return None
    return "Scaling enabled"
