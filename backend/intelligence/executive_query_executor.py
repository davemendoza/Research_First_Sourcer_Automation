import json
import os
from backend.intelligence.vector_search_engine import vector_search
from backend.intelligence.ecosystem_engine import ecosystem_summary
from backend.intelligence.trajectory_engine import trajectory_analysis

DATA_PATH = "outputs/gold_standard.json"

def execute_query(query: str):

    query_lower = query.lower()

    if "similar" in query_lower:
        return vector_search(query)

    if "ecosystem" in query_lower or "companies" in query_lower:
        return ecosystem_summary()

    if "trajectory" in query_lower or "emerging" in query_lower:
        return trajectory_analysis()

    # fallback
    return vector_search(query)
