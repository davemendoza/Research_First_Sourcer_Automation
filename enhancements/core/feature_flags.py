"""
Global enhancement feature flags.
ALL FLAGS DEFAULT TO FALSE.
Enhancements must never activate implicitly.
"""

FEATURE_FLAGS = {
    "ui_enabled": False,
    "excel_narratives_enabled": False,
    "gpt_advanced_enabled": False,
    "extra_signals_enabled": False,
    "temporal_monitoring_enabled": False,
    "scaling_enabled": False,
    "devops_enabled": False,
    "governance_enabled": False,
    "demo_mode_enabled": False,
}
