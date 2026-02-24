import json
import os
from collections import Counter

DATA_PATH = "outputs/gold_standard.json"

def load_data():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def ecosystem_summary():
    data = load_data()

    companies = []
    roles = []

    for person in data:
        company = person.get("company") or person.get("Company")
        role = person.get("title") or person.get("Role")

        if company:
            companies.append(company)

        if role:
            roles.append(role)

    return {
        "top_companies": Counter(companies).most_common(25),
        "top_roles": Counter(roles).most_common(25),
        "total_profiles": len(data)
    }
