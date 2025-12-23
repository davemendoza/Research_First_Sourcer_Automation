from enhancements.core import feature_flags, registry, guardrails

registry.register("EXCEL_NARRATIVES", feature_flags.FEATURE_FLAGS["excel_narratives_enabled"])
guardrails.assert_core_immutable()

def write_narratives():
    if not feature_flags.FEATURE_FLAGS["excel_narratives_enabled"]:
        return None
    return "Excel narratives generated"
