"""
Query Library Loader
Reads query_library.json and serves structured query templates
to the Executive Intelligence Console.
"""
import json
import os
from typing import Dict, List, Optional

QUERY_LIBRARY_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "query_library.json"
)

_cache: Optional[Dict] = None


def load_query_library() -> Dict:
    global _cache
    if _cache is not None:
        return _cache
    try:
        with open(QUERY_LIBRARY_PATH, "r") as f:
            _cache = json.load(f)
            return _cache
    except FileNotFoundError:
        return {"categories": {}, "execution_engine_map": {}}


def get_all_queries() -> List[Dict]:
    library = load_query_library()
    queries = []
    for cat_key, cat in library.get("categories", {}).items():
        for q in cat.get("queries", []):
            queries.append({**q, "category": cat_key, "category_label": cat.get("label", cat_key)})
    return queries


def get_query_by_id(query_id: str) -> Optional[Dict]:
    for q in get_all_queries():
        if q.get("id") == query_id:
            return q
    return None


def get_categories_summary() -> List[Dict]:
    library = load_query_library()
    result = []
    for cat_key, cat in library.get("categories", {}).items():
        result.append({
            "key": cat_key,
            "label": cat.get("label", cat_key),
            "description": cat.get("description", ""),
            "icon": cat.get("icon", "⚡"),
            "color": cat.get("color", "#60a5fa"),
            "query_count": len(cat.get("queries", [])),
            "queries": [
                {"id": q["id"], "short_label": q.get("short_label", q["query"][:60]), "query": q["query"]}
                for q in cat.get("queries", [])
            ]
        })
    return result


def get_engine_map() -> Dict:
    library = load_query_library()
    return library.get("execution_engine_map", {})


def get_demo_queries() -> List[Dict]:
    library = load_query_library()
    showcase_ids = library.get("demo_showcase_queries", [])
    return [q for q in get_all_queries() if q["id"] in showcase_ids]
