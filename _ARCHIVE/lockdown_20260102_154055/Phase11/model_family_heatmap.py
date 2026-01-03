from openpyxl.formatting.rule import ColorScaleRule

MODEL_FAMILIES = [
    "GPT", "Claude", "LLaMA", "Mistral", "Mixtral", "Gemini",
    "Qwen", "DeepSeek", "Falcon", "Phi", "Gemma", "DBRX", "Grok"
]

def add_model_family_heatmap(wb, rows):
    ws = wb.create_sheet("MODEL_FAMILY_HEATMAP")
    ws.append(["Rank", "Name", "Organization"] + MODEL_FAMILIES)

    for r in rows:
        text = (r["Model Families Used"] or "").lower()
        ws.append(
            [r["Overall Rank"], r["Name"], r["Organization"]] +
            [1 if fam.lower() in text else 0 for fam in MODEL_FAMILIES]
        )

    start = "D2"
    end = chr(ord("C") + len(MODEL_FAMILIES)) + str(ws.max_row)
    rule = ColorScaleRule(start_type="num", start_value=0,
                          mid_type="num", mid_value=0.5,
                          end_type="num", end_value=1)
    ws.conditional_formatting.add(f"{start}:{end}", rule)

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
