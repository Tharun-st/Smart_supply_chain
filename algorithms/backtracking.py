"""
Intelligent Supply Chain Management System
Backtracking Route Optimizer with Constraint Pruning
"""

import time
from typing import Dict, Any
from data_structures.graph import Graph


def optimize_delivery_route_backtracking(
    graph: Graph,
    start_node: str,
    end_node: str,
    max_distance_km: float = 2500.0
) -> Dict[str, Any]:
    """
    Backtracking route exploration with distance budget pruning.
    """
    t0 = time.perf_counter()
    routes_explored = 0
    valid_routes = []
    pruned_count = 0

    def backtrack(curr: str, path: list, dist: float, visited: set):
        nonlocal routes_explored, pruned_count
        routes_explored += 1

        if dist > max_distance_km:
            pruned_count += 1
            return

        if curr == end_node and len(path) > 1:
            valid_routes.append({"path": list(path), "distance": dist})
            return

        for edge in graph.get_neighbors(curr):
            nbr = getattr(edge, "destination", None) or (edge.get("to_id") if isinstance(edge, dict) else None)
            w = getattr(edge, "distance_km", None) or (edge.get("distance_km", 50.0) if isinstance(edge, dict) else 50.0)
            if nbr and nbr not in visited:
                visited.add(nbr)
                path.append(nbr)
                backtrack(nbr, path, dist + w, visited)
                path.pop()
                visited.remove(nbr)

    backtrack(start_node, [start_node], 0.0, {start_node})

    selected = min(valid_routes, key=lambda r: r["distance"]) if valid_routes else {"path": [start_node, end_node], "distance": 0.0}
    selected["labels"] = [
        getattr(graph.vertices[n], "name", n) if n in graph.vertices else n
        for n in selected["path"]
    ]

    elapsed_ms = round((time.perf_counter() - t0) * 1000, 3)
    return {
        "routes_explored": max(routes_explored, 1),
        "valid_routes_count": len(valid_routes),
        "invalid_routes_count": pruned_count,
        "selected_route": selected,
        "elapsed_ms": elapsed_ms
    }
