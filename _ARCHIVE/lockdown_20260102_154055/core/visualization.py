"""
AI Talent Engine – Proprietary System
© Dave Mendoza – All Rights Reserved
Finalized: 2025-12-16T01:25:25.864681Z
"""
def summarize(records):
    return {
        "total": len(records),
        "avg_signals": sum(r.get("enriched", {}).get("signal_count", 0) for r in records) / max(len(records),1)
    }
