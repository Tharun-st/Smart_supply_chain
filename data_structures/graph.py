"""
Intelligent Supply Chain Management System
Custom Adjacency List Graph Implementation

Academic Data Structures and Algorithmic Problem Solving Project
Data Structure: Weighted Graph via Adjacency List
Used for:
  - Supply Chain Logistics Network
  - Nodes (Vertices): Suppliers, Warehouses, Customer Delivery Hubs
  - Edges (Routes): Transportation routes with distance (km) and estimated transit time

Operations Implemented:
  1. Add Location / Vertex (with node type, name, coordinates)
  2. Add Route / Edge (bidirectional or directed, with distance weight)
  3. Remove Route / Edge
  4. Get Neighbors
  5. Get Adjacency List (formatted for textual display & API)
  6. Export for interactive graph visualizers (nodes & links list)
"""

from typing import Dict, List, Any, Optional


class GraphVertex:
    """Represents a location in the supply chain network."""
    def __init__(self, node_id: str, name: str, node_type: str, city: str = "", lat: float = 0.0, lng: float = 0.0):
        self.node_id: str = str(node_id)
        self.name: str = name
        self.node_type: str = node_type  # 'warehouse', 'supplier', 'delivery_hub'
        self.city: str = city
        self.lat: float = lat
        self.lng: float = lng

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.node_id,
            "name": self.name,
            "type": self.node_type,
            "city": self.city,
            "lat": self.lat,
            "lng": self.lng
        }


class GraphEdge:
    """Represents a transport route connection between two locations."""
    def __init__(self, destination: str, distance_km: float, transit_time_hrs: float = 0.0):
        self.destination: str = str(destination)
        self.distance_km: float = float(distance_km)
        self.transit_time_hrs: float = float(transit_time_hrs)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "destination": self.destination,
            "distance_km": self.distance_km,
            "transit_time_hrs": self.transit_time_hrs
        }


class Graph:
    """
    Adjacency List representation of the supply chain network.
    Maintains a dictionary mapping vertex_id -> list of GraphEdge objects.
    """
    def __init__(self, name: str = "SupplyChainNetworkGraph"):
        self.name: str = name
        self.vertices: Dict[str, GraphVertex] = {}
        self.adj_list: Dict[str, List[GraphEdge]] = {}

    def add_vertex(self, node_id: str, name: str, node_type: str, city: str = "", lat: float = 0.0, lng: float = 0.0) -> GraphVertex:
        """Adds a new location (vertex) to the graph."""
        nid = str(node_id)
        vertex = GraphVertex(nid, name, node_type, city, lat, lng)
        self.vertices[nid] = vertex
        if nid not in self.adj_list:
            self.adj_list[nid] = []
        return vertex

    def add_edge(self, source_id: str, destination_id: str, distance_km: float, transit_time_hrs: float = 0.0, bidirectional: bool = True) -> bool:
        """
        Adds a route (edge) between source and destination.
        Defaults to bidirectional (undirected) road networks.
        """
        src = str(source_id)
        dst = str(destination_id)

        # Auto-create vertices if not already existing
        if src not in self.adj_list:
            self.adj_list[src] = []
        if dst not in self.adj_list:
            self.adj_list[dst] = []

        # Check if edge already exists from src -> dst
        for edge in self.adj_list[src]:
            if edge.destination == dst:
                edge.distance_km = float(distance_km)
                edge.transit_time_hrs = float(transit_time_hrs)
                break
        else:
            self.adj_list[src].append(GraphEdge(dst, distance_km, transit_time_hrs))

        # Add reverse edge if bidirectional
        if bidirectional:
            for edge in self.adj_list[dst]:
                if edge.destination == src:
                    edge.distance_km = float(distance_km)
                    edge.transit_time_hrs = float(transit_time_hrs)
                    break
            else:
                self.adj_list[dst].append(GraphEdge(src, distance_km, transit_time_hrs))

        return True

    def remove_edge(self, source_id: str, destination_id: str, bidirectional: bool = True) -> bool:
        """Removes a route between two locations."""
        src = str(source_id)
        dst = str(destination_id)
        removed = False

        if src in self.adj_list:
            orig_len = len(self.adj_list[src])
            self.adj_list[src] = [e for e in self.adj_list[src] if e.destination != dst]
            if len(self.adj_list[src]) < orig_len:
                removed = True

        if bidirectional and dst in self.adj_list:
            self.adj_list[dst] = [e for e in self.adj_list[dst] if e.destination != src]

        return removed

    def get_neighbors(self, node_id: str) -> List[GraphEdge]:
        """Returns the list of outbound edges from the specified node."""
        return self.adj_list.get(str(node_id), [])

    def get_adjacency_list_display(self) -> Dict[str, Any]:
        """
        Returns a human-readable and structured dictionary of the adjacency list
        for college project demonstration and UI display:
        e.g.,
        Warehouse A:
          → Warehouse B (15 km)
          → Hub C (24 km)
        """
        display_dict = {}
        for nid, edges in self.adj_list.items():
            vertex = self.vertices.get(nid)
            v_name = vertex.name if vertex else nid
            v_type = vertex.node_type if vertex else "location"

            connections = []
            for edge in edges:
                dest_vertex = self.vertices.get(edge.destination)
                dest_name = dest_vertex.name if dest_vertex else edge.destination
                connections.append({
                    "destination_id": edge.destination,
                    "destination_name": dest_name,
                    "distance_km": edge.distance_km,
                    "transit_time_hrs": edge.transit_time_hrs
                })

            display_dict[nid] = {
                "id": nid,
                "name": v_name,
                "type": v_type,
                "connections": connections
            }
        return display_dict

    def to_network_payload(self) -> Dict[str, Any]:
        """
        Exports the graph nodes and links formatted for interactive frontend visualization
        (D3.js / Vis.js / HTML5 Canvas).
        """
        nodes = []
        for nid, vertex in self.vertices.items():
            nodes.append(vertex.to_dict())

        links = []
        seen_edges = set()
        for src, edges in self.adj_list.items():
            for edge in edges:
                dst = edge.destination
                edge_pair = tuple(sorted([src, dst]))
                if edge_pair not in seen_edges:
                    seen_edges.add(edge_pair)
                    links.append({
                        "source": src,
                        "target": dst,
                        "distance_km": edge.distance_km,
                        "transit_time_hrs": edge.transit_time_hrs
                    })

        return {
            "nodes": nodes,
            "links": links,
            "total_vertices": len(self.vertices),
            "total_routes": len(links)
        }

    def clear(self):
        self.vertices.clear()
        self.adj_list.clear()

    def __len__(self) -> int:
        return len(self.vertices)
