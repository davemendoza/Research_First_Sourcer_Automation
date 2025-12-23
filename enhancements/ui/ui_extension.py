from enhancements.core import feature_flags, registry, guardrails

registry.register("UI_DASHBOARD", feature_flags.FEATURE_FLAGS["ui_enabled"])
guardrails.assert_core_immutable()

def launch_ui():
    if not feature_flags.FEATURE_FLAGS["ui_enabled"]:
        return None
    return "UI subsystem active"
