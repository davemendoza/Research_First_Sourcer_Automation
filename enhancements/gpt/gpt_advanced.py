from enhancements.core import feature_flags, registry, guardrails

registry.register("GPT_ADVANCED", feature_flags.FEATURE_FLAGS["gpt_advanced_enabled"])
guardrails.assert_core_immutable()

def advanced_reasoning():
    if not feature_flags.FEATURE_FLAGS["gpt_advanced_enabled"]:
        return None
    return "Advanced GPT reasoning applied"
