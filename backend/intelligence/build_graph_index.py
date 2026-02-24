# ==================================================================================================
# AI TALENT ENGINE — GRAPH INDEX BUILDER
# ==================================================================================================

import os
import json

SOURCE_FILE = "outputs/gold_standard.json"
GRAPH_FILE = "outputs/ecosystem_graph.json"

def build_graph():

    if not os.path.exists(SOURCE_FILE):
        raise RuntimeError("gold_standard.json missing")

    with open(SOURCE_FILE, "r") as f:
        identities = json.load(f)

    nodes = []
    edges = []

    company_map = {}

    for identity in identities:

        name = identity.get("Name") or identity.get("name")
        company = identity.get("Company") or identity.get("company")

        nodes.append({
            "id": name,
            "company": company
        })

        if company not in company_map:
            company_map[company] = []

        company_map[company].append(name)

    for company, people in company_map.items():

        for i in range(len(people) - 1):

            edges.append({
                "source": people[i],
                "target": people[i+1]
            })

    graph = {
        "nodes": nodes,
        "edges": edges
    }

    with open(GRAPH_FILE, "w") as f:
        json.dump(graph, f)

    print("Graph index built")

if __name__ == "__main__":
    build_graph()
