"""
Central enhancement registry.
All enhancements must register here explicitly.
"""

ENHANCEMENTS = []

def register(name: str, enabled: bool):
    ENHANCEMENTS.append({
        "name": name,
        "enabled": enabled
    })
