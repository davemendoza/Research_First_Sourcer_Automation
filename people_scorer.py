def score_person(p):
    score = 0
    if p.get("followers", 0) >= 100: score += 2
    if p.get("repos", 0) >= 10: score += 2
    if "ai" in (p.get("bio","").lower()): score += 1
    p["signal_score"] = score
    return p
