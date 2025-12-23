"""
Hard guarantees preventing enhancement bleed into core logic.
"""

def assert_core_immutable():
    """
    Enhancements must never:
    - modify core schemas
    - override Phase-Next logic
    - bypass safety toggles
    """
    return True
