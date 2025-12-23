from enhancements.core import feature_flags, registry, guardrails

registry.register("TEMPORAL_MONITORING", feature_flags.FEATURE_FLAGS["temporal_monitoring_enabled"])
guardrails.assert_core_immutable()

def monitor_changes():
    if not feature_flags.FEATURE_FLAGS["temporal_monitoring_enabled"]:
        return None
    return "Monitoring active"
