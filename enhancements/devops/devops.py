from enhancements.core import feature_flags, registry, guardrails

registry.register("DEVOPS", feature_flags.FEATURE_FLAGS["devops_enabled"])
guardrails.assert_core_immutable()

def setup_ci():
    if not feature_flags.FEATURE_FLAGS["devops_enabled"]:
        return None
    return "CI configured"
