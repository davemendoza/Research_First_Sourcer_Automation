def compute_velocity(candidate):

    candidate["trajectory_score"] = (
        candidate.get("citation_velocity",0) +
        candidate.get("repo_velocity",0)
    )

    return candidate
