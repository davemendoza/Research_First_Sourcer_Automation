"""
AI Talent Engine – Proprietary System
© Dave Mendoza – All Rights Reserved
Finalized: 2025-12-16T01:25:25.864681Z
"""
def enrich_record(record):
    signals = record.get("signals", {})
    record["enriched"] = {
        "signal_count": len(signals),
        "has_llm": any("gpt" in s.lower() or "llama" in s.lower() for s in signals)
    }
    return record
