from enhancements.core import feature_flags, registry, guardrails

registry.register("EXTRA_SIGNALS", feature_flags.FEATURE_FLAGS["extra_signals_enabled"])
guardrails.assert_core_immutable()

def collect_extra_signals():
    if not feature_flags.FEATURE_FLAGS["extra_signals_enabled"]:
        return []
    return []
