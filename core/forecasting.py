"""
AI Talent Engine – Proprietary System
© Dave Mendoza – All Rights Reserved
Finalized: 2025-12-16T01:25:25.864681Z
"""
def forecast_growth(signal_count):
    if signal_count > 10:
        return "high"
    if signal_count > 3:
        return "medium"
    return "low"
