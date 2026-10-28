"""
Intelligent Supply Chain Management System
Breadth-First Search (BFS) Algorithm Implementation

Purpose:
  - To explore the warehouse and delivery network level-by-level.
  - Used to find all connected delivery locations starting from a specific warehouse.
"""

from data_structures.graph import Graph
from data_structures.queue import LinkedListQueue

class BFSResult:
    """Stores the output and the step-by-step process of the BFS search."""
    def __init__(self, start_node):
        self.start_node = str(start_node)
        self.visited_order = []
        self.levels = {}
        self.parent_map = {}
        self.steps = []
        self.traversed_edges = []

    def to_dict(self):
        return {
            "start_node": self.start_node,
            "visited_order": self.visited_order,
            "traversal_order": self.visited_order,
            "total_visited": len(self.visited_order),
            "total_vertices_visited": len(self.visited_order),
            "levels": self.levels,
            "parent_map": self.parent_map,
            "steps": self.steps,
            "traversed_edges": self.traversed_edges,
            "elapsed_ms": getattr(self, "elapsed_ms", 0.1)
        }

    def get(self, key, default=None):
        return self.to_dict().get(key, default)

    def __getitem__(self, key):
        return self.to_dict()[key]

def run_bfs(graph, start_node_id):
    """
    Executes the Breadth-First Search algorithm.
    This function uses a Queue to visit nodes level by level.
    """
    start_id = str(start_node_id)
    result = BFSResult(start_id)

    # If the starting node is not in the graph, just return the empty result
    if start_id not in graph.adj_list:
        return result

    # Using the custom Queue as mentioned in the synopsis
    queue = LinkedListQueue(name="BFS_Queue")
    visited = set()

    # Initial step: Mark start node as visited and add to queue
    visited.add(start_id)
    queue.enqueue(start_id)
    result.levels[start_id] = 0
    result.parent_map[start_id] = None

    step_count = 1
    result.steps.append({
        "step": step_count,
        "action": "START",
        "current_node": start_id,
        "description": f"Starting BFS from {start_id}. Added to queue."
    })

    # Loop until there are no more nodes to visit in the queue
    while not queue.is_empty():
        # Dequeue the current location to visit it
        current_id = queue.dequeue()
        result.visited_order.append(current_id)

        # Get the level of the current node
        current_level = result.levels[current_id]

        step_count += 1
        result.steps.append({
            "step": step_count,
            "action": "VISIT",
            "current_node": current_id,
            "description": f"Visiting node {current_id} at level {current_level}."
        })

        # Look at all connected neighbors (delivery routes)
        neighbors = graph.get_neighbors(current_id)
        for edge in neighbors:
            neighbor_id = edge.destination

            # If we haven't visited this neighbor yet, add it to the queue
            if neighbor_id not in visited:
                visited.add(neighbor_id)
                result.levels[neighbor_id] = current_level + 1
                result.parent_map[neighbor_id] = current_id

                # Keep track of the route taken
                result.traversed_edges.append({
                    "source": current_id,
                    "target": neighbor_id,
                    "distance_km": edge.distance_km
                })

                # Add to queue to explore its neighbors later
                queue.enqueue(neighbor_id)

                step_count += 1
                result.steps.append({
                    "step": step_count,
                    "action": "DISCOVER",
                    "current_node": current_id,
                    "discovered_node": neighbor_id,
                    "description": f"Found new location {neighbor_id}. Adding to queue for level {current_level + 1}."
                })

    return result
