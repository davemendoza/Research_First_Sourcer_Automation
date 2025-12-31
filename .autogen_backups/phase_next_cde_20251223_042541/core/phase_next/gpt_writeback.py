from .control_plane import GPT_WRITEBACK_ENABLED

def prepare_gpt_writeback_payload(row, analysis):
    """
    Dormant GPT writeback payload generator.
    Exists for import safety only.
    """
    if not GPT_WRITEBACK_ENABLED:
        return None

    return {
        "Strengths": analysis.get("strengths"),
        "Weaknesses": analysis.get("weaknesses"),
        "Notes": analysis.get("notes"),
    }

def writeback(row, analysis):
    return prepare_gpt_writeback_payload(row, analysis)
