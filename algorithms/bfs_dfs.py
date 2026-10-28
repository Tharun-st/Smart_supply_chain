"""
Intelligent Supply Chain Management System
BFS & DFS Traversal Module
"""

import time
from data_structures.graph import Graph
from data_structures.stack import Stack
from algorithms.bfs import run_bfs


def run_dfs(graph: Graph, start_node_id: str):
    """Executes DFS using LIFO Stack."""
    t0 = time.perf_counter()
    start_id = str(start_node_id)
    if start_id not in graph.vertices:
        return {
            "start_node": start_id,
            "traversal_order": [],
            "total_vertices_visited": 0,
            "elapsed_ms": 0.0
        }

    visited = set()
    order = []
    stack = Stack("DFSStack")
    stack.push(start_id)

    while not stack.is_empty():
        curr = stack.pop()
        if curr not in visited:
            visited.add(curr)
            order.append(curr)
            neighbors = graph.get_neighbors(curr)
            # Push in reverse order for consistent traversal
            for nbr in reversed(neighbors):
                nbr_id = getattr(nbr, "destination", None) or (nbr.get("to_id") if isinstance(nbr, dict) else None)
                if nbr_id and nbr_id not in visited:
                    stack.push(nbr_id)

    elapsed_ms = round((time.perf_counter() - t0) * 1000, 3)
    return {
        "start_node": start_id,
        "traversal_order": order,
        "total_vertices_visited": len(order),
        "elapsed_ms": elapsed_ms
    }
