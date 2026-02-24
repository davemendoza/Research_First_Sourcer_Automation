def generate_narrative(profile):

    score = profile.get("signal_score", 0)

    if score > 90:
        return "Frontier-tier engineer with exceptional influence."

    if score > 70:
        return "Strong engineer with high ecosystem influence."

    return "Emerging engineer with growth trajectory."
