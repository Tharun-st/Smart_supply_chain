"""
Intelligent Supply Chain Management System
Delivery Network & Graph API Blueprint

Data Structure: Adjacency List Graph
Algorithms: Breadth-First Search (BFS) & Depth-First Search (DFS)
Features:
  - Full Node & Edge Graph Manipulation (Add/Remove Vertices and Edges)
  - Interactive BFS with Queue state
  - Interactive DFS with Stack state
  - Shortest Path / Route Discovery
"""

from flask import Blueprint, jsonify, request
from models.dsa_service import dsa_service
from models.database import db
from algorithms.bfs import run_bfs
import time

network_bp = Blueprint("network_bp", __name__)

@network_bp.route("/api/network", methods=["GET"])
def get_network():
    """Returns the complete supply chain logistics graph payload and adjacency list."""
    network_data = dsa_service.network_graph.to_network_payload()
    adjacency_list = dsa_service.network_graph.get_adjacency_list_display()

    return jsonify({
        "status": "success",
        "data_structure": "Adjacency List Graph",
        "total_vertices": len(dsa_service.network_graph.vertices),
        "graph": network_data,
        "adjacency_list": adjacency_list,
        "explanation": "The delivery network is modeled as a weighted graph using an Adjacency List representation (Vertex -> List[Edges]). Vertices represent Warehouses, Suppliers, and Customer Hubs; Edges represent transportation links."
    })

@network_bp.route("/api/network/nodes", methods=["POST"])
def add_node():
    """Adds a new vertex to the network graph."""
    data = request.get_json() or {}
    node_id = data.get("node_id")
    name = data.get("name")
    node_type = data.get("node_type", "warehouse")
    city = data.get("city", "")

    if not node_id or not name:
        return jsonify({"status": "error", "message": "Node ID and Name are required"}), 400

    vertex = dsa_service.network_graph.add_vertex(
        node_id=str(node_id),
        name=name,
        node_type=node_type,
        city=city,
        lat=float(data.get("lat", 0.0)),
        lng=float(data.get("lng", 0.0))
    )

    return jsonify({
        "status": "success",
        "message": f"Node '{name}' ({node_id}) added to Adjacency List graph",
        "node": vertex.to_dict(),
        "graph": dsa_service.network_graph.to_network_payload()
    }), 201

@network_bp.route("/api/network/nodes/<string:node_id>", methods=["DELETE"])
def remove_node(node_id):
    """Removes a vertex and all its connected edges from the network graph."""
    nid = str(node_id)
    if nid not in dsa_service.network_graph.vertices:
        return jsonify({"status": "error", "message": f"Node '{nid}' not found"}), 404

    # Remove vertex
    del dsa_service.network_graph.vertices[nid]
    # Remove outbound edges
    if nid in dsa_service.network_graph.adj_list:
        del dsa_service.network_graph.adj_list[nid]
    # Remove inbound edges
    for src in dsa_service.network_graph.adj_list:
        dsa_service.network_graph.adj_list[src] = [
            e for e in dsa_service.network_graph.adj_list[src] if e.destination != nid
        ]

    return jsonify({
        "status": "success",
        "message": f"Node '{nid}' and all its connected edges removed from graph",
        "graph": dsa_service.network_graph.to_network_payload()
    })

@network_bp.route("/api/network/edges", methods=["POST"])
def add_edge():
    """Adds a route edge between two locations."""
    data = request.get_json() or {}
    src = data.get("source_id")
    dst = data.get("destination_id")
    dist = data.get("distance_km")
    transit = data.get("transit_time_hrs", 0.0)

    if not src or not dst or dist is None:
        return jsonify({"status": "error", "message": "Source, Destination, and Distance are required"}), 400

    try:
        dist = float(dist)
        transit = float(transit)
        dsa_service.network_graph.add_edge(str(src), str(dst), dist, transit)
        return jsonify({
            "status": "success",
            "message": f"Route from {src} to {dst} ({dist} km) added to graph",
            "graph": dsa_service.network_graph.to_network_payload()
        }), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@network_bp.route("/api/network/edges", methods=["DELETE"])
def remove_edge():
    """Removes a route edge between two locations."""
    data = request.get_json() or {}
    src = data.get("source_id")
    dst = data.get("destination_id")
    if not src or not dst:
        return jsonify({"status": "error", "message": "Source and destination are required"}), 400

    removed = dsa_service.network_graph.remove_edge(str(src), str(dst))
    if removed:
        return jsonify({
            "status": "success",
            "message": f"Route between {src} and {dst} removed from graph",
            "graph": dsa_service.network_graph.to_network_payload()
        })
    return jsonify({"status": "error", "message": "Route not found"}), 404

# ==================== GRAPH ALGORITHMS ====================
@network_bp.route("/api/network/bfs", methods=["POST"])
def execute_bfs():
    """Executes Breadth-First Search on the network graph using custom LinkedListQueue."""
    data = request.get_json() or {}
    start_node = data.get("start_node", "WH-1")

    start_time = time.perf_counter()
    bfs_result = run_bfs(dsa_service.network_graph, str(start_node))
    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 4)

    result = bfs_result.to_dict()
    result["status"] = "success"
    result["algorithm"] = "Breadth-First Search (BFS)"
    result["data_structure_used"] = "Adjacency List Graph + Custom FIFO LinkedListQueue"
    result["time_complexity"] = "O(V + E)"
    result["space_complexity"] = "O(V)"
    result["elapsed_ms"] = elapsed_ms
    result["total_vertices_visited"] = len(bfs_result.visited_order)
    result["traversal_order"] = bfs_result.visited_order

    # Audit in database
    db.execute_query("""
        INSERT INTO algorithm_logs
        (algorithm_name, data_structure_used, input_summary, output_summary, time_complexity, execution_steps_count, execution_time_ms)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        "Breadth-First Search (BFS)",
        "Adjacency List Graph + FIFO Queue",
        f"Start Node: {start_node}",
        f"Visited {result['total_vertices_visited']} nodes in BFS order",
        "O(V + E)", len(bfs_result.steps), elapsed_ms
    ), fetch="none")

    return jsonify(result)

@network_bp.route("/api/network/bfs-map", methods=["POST"])
def execute_bfs_map():
    """
    Executes BFS and returns result enriched with lat/lng coordinates for each
    visited node and each traversed edge — designed for Leaflet.js map rendering.
    """
    data = request.get_json() or {}
    start_node = str(data.get("start_node", "WH-1"))

    start_time = time.perf_counter()
    bfs_result = run_bfs(dsa_service.network_graph, start_node)
    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 4)

    # Build node map with coordinates
    all_nodes_geo = []
    for nid, vertex in dsa_service.network_graph.vertices.items():
        all_nodes_geo.append({
            "id": nid,
            "name": vertex.name,
            "type": vertex.node_type,
            "city": vertex.city,
            "lat": vertex.lat,
            "lng": vertex.lng,
            "bfs_level": bfs_result.levels.get(nid),
            "visited": nid in bfs_result.visited_order,
            "is_start": nid == start_node
        })

    # Enrich traversed edges with full coordinate pairs
    edges_geo = []
    for edge in bfs_result.traversed_edges:
        src_v = dsa_service.network_graph.vertices.get(edge["source"])
        dst_v = dsa_service.network_graph.vertices.get(edge["target"])
        if src_v and dst_v and src_v.lat and dst_v.lat:
            edges_geo.append({
                "source": edge["source"],
                "target": edge["target"],
                "distance_km": edge["distance_km"],
                "source_lat": src_v.lat,
                "source_lng": src_v.lng,
                "target_lat": dst_v.lat,
                "target_lng": dst_v.lng,
                "source_name": src_v.name,
                "target_name": dst_v.name
            })

    # All graph edges (for background display)
    all_edges_geo = []
    seen = set()
    for src, edges in dsa_service.network_graph.adj_list.items():
        for e in edges:
            pair = tuple(sorted([src, e.destination]))
            if pair not in seen:
                seen.add(pair)
                sv = dsa_service.network_graph.vertices.get(src)
                dv = dsa_service.network_graph.vertices.get(e.destination)
                if sv and dv and sv.lat and dv.lat:
                    all_edges_geo.append({
                        "source": src, "target": e.destination,
                        "distance_km": e.distance_km,
                        "source_lat": sv.lat, "source_lng": sv.lng,
                        "target_lat": dv.lat, "target_lng": dv.lng
                    })

    return jsonify({
        "status": "success",
        "algorithm": "Breadth-First Search (BFS)",
        "start_node": start_node,
        "visited_order": bfs_result.visited_order,
        "steps": bfs_result.steps,
        "levels": bfs_result.levels,
        "time_complexity": "O(V + E)",
        "elapsed_ms": elapsed_ms,
        "all_nodes": all_nodes_geo,
        "traversed_edges": edges_geo,
        "all_edges": all_edges_geo
    })

@network_bp.route("/api/network/dfs", methods=["POST"])
def execute_dfs():
    """DFS is not in the project scope. Returns a message directing to BFS."""
    return jsonify({
        "status": "info",
        "message": "DFS is not in the project algorithm scope. Please use BFS (/api/network/bfs) for graph traversal.",
        "algorithm": "BFS (Breadth-First Search)",
        "redirect_to": "/api/network/bfs"
    }), 200

@network_bp.route("/api/network/find-route", methods=["POST"])
def find_route():
    """Finds route between two nodes using BFS shortest-path in hops."""
    data = request.get_json() or {}
    start_id = str(data.get("start_node", "WH-1"))
    end_id = str(data.get("end_node", "HUB-1"))

    if start_id not in dsa_service.network_graph.vertices or end_id not in dsa_service.network_graph.vertices:
        return jsonify({"status": "error", "message": "Start or destination node not found"}), 404

    # BFS path reconstruction
    visited = {start_id: None}
    queue = [start_id]
    found = False

    while queue:
        curr = queue.pop(0)
        if curr == end_id:
            found = True
            break
        for edge in dsa_service.network_graph.get_neighbors(curr):
            if edge.destination not in visited:
                visited[edge.destination] = curr
                queue.append(edge.destination)

    if not found:
        return jsonify({"status": "error", "message": f"No route path exists between {start_id} and {end_id}"}), 404

    # Reconstruct path
    path = []
    curr = end_id
    while curr is not None:
        path.append(curr)
        curr = visited[curr]
    path.reverse()

    path_details = []
    total_km = 0.0
    for idx, nid in enumerate(path):
        v = dsa_service.network_graph.vertices.get(nid)
        seg_dist = 0.0
        if idx > 0:
            prev_nid = path[idx - 1]
            for edge in dsa_service.network_graph.get_neighbors(prev_nid):
                if edge.destination == nid:
                    seg_dist = edge.distance_km
                    total_km += seg_dist
                    break
        path_details.append({
            "node_id": nid,
            "name": v.name if v else nid,
            "type": v.node_type if v else "hub",
            "distance_from_prev_km": seg_dist
        })

    return jsonify({
        "status": "success",
        "start_node": start_id,
        "end_node": end_id,
        "total_distance_km": round(total_km, 2),
        "total_hops": len(path) - 1,
        "path": path,
        "path_details": path_details
    })

# ==================== DELIVERIES MANAGEMENT CRUD ====================
@network_bp.route("/api/deliveries", methods=["GET"])
def get_deliveries():
    """
    Returns active deliveries joined with Orders, Source Warehouses, and Destination Hubs.
    Fields: Delivery ID, Order ID, Source Warehouse, Destination, Delivery Date, Delivery Status, Estimated Time
    """
    search = request.args.get("search", "").strip()
    sort_by = request.args.get("sort_by", "estimated_time")  # 'estimated_time', 'id', 'date'

    query = """
        SELECT o.id as delivery_id, o.id as order_id, o.order_number, o.customer_name,
               p.name as product_name, o.quantity,
               COALESCE(w.name, 'North Regional Mega-Hub (WH-DEL)') as source_warehouse,
               COALESCE(w.warehouse_code, 'WH-DEL') as source_warehouse_code,
               l.name as destination_hub, l.city as destination_city,
               DATE(o.created_at) as delivery_date,
               o.status as delivery_status,
               COALESCE(o.distance_km, 350.0) as distance_km,
               ROUND(COALESCE(o.distance_km, 350.0) / 60.0 + 1.5, 1) as estimated_time_hrs
        FROM orders o
        JOIN products p ON o.product_id = p.id
        JOIN delivery_locations l ON o.delivery_location_id = l.id
        LEFT JOIN warehouses w ON o.assigned_warehouse_id = w.id
    """
    params = []
    if search:
        query += " WHERE o.order_number LIKE %s OR o.customer_name LIKE %s OR l.name LIKE %s OR l.city LIKE %s"
        params = [f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"]

    if sort_by == "estimated_time":
        query += " ORDER BY estimated_time_hrs ASC"
    elif sort_by == "date":
        query += " ORDER BY o.created_at DESC"
    else:
        query += " ORDER BY o.id DESC"

    try:
        deliveries = db.execute_query(query, tuple(params), fetch="all")
        return jsonify({
            "status": "success",
            "total_deliveries": len(deliveries),
            "deliveries": deliveries
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@network_bp.route("/api/deliveries/<int:delivery_id>", methods=["PUT"])
def update_delivery_status(delivery_id):
    """Updates status or assigned warehouse of a delivery."""
    data = request.get_json() or {}
    new_status = data.get("status", "DISPATCHED")
    wh_id = data.get("assigned_warehouse_id")

    try:
        if wh_id:
            db.execute_query(
                "UPDATE orders SET status = %s, assigned_warehouse_id = %s WHERE id = %s",
                (new_status, wh_id, delivery_id),
                fetch="none"
            )
        else:
            db.execute_query(
                "UPDATE orders SET status = %s WHERE id = %s",
                (new_status, delivery_id),
                fetch="none"
            )
        return jsonify({
            "status": "success",
            "message": f"Delivery #{delivery_id} status updated to '{new_status}'."
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

