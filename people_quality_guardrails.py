def is_valid_person(p):
    if not p.get("person_name"):
        return False
    if not p.get("github_url"):
        return False
    return True

def dedupe_people(people):
    uniq = {}
    for p in people:
        key = p.get("github_url") or p.get("person_name")
        uniq[key] = p
    return list(uniq.values())
