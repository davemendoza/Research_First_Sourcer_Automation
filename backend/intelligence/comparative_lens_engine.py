###############################################################################
# COMPARATIVE LENS ENGINE
# © 2026 L. David Mendoza. All Rights Reserved.
###############################################################################

import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[1] / "storage" / "identity_graph.json"

class ComparativeLensEngine:

    def compare(self, id1, id2):

        graph = json.loads(DATA_PATH.read_text())

        neighbors1 = set()
        neighbors2 = set()

        for e in graph["edges"]:
            if e["source"] == id1:
                neighbors1.add(e["target"])
            if e["source"] == id2:
                neighbors2.add(e["target"])

        overlap = neighbors1.intersection(neighbors2)

        return list(overlap)
