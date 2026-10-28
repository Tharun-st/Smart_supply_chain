"""
Intelligent Supply Chain Management System
Optimization API Blueprint

Project Scope Algorithms:
  D1. Greedy — Nearest Suitable Warehouse Selection
      (Selects the warehouse with sufficient stock that is geographically closest
       to the delivery destination — making a locally optimal choice at each step.)
"""

from flask import Blueprint, jsonify, request
from models.database import db
from models.dsa_service import dsa_service
from algorithms.greedy import select_nearest_suitable_warehouse
import time

optimization_bp = Blueprint("optimization_bp", __name__)


# ==================== GREEDY: NEAREST WAREHOUSE SELECTION ====================
@optimization_bp.route("/api/optimization/greedy", methods=["POST"])
def run_greedy_warehouse():
    """
    Executes the Greedy Nearest Suitable Warehouse Selection Algorithm.

    Given a product ID, required quantity, and delivery location:
    1. Feasibility Check: Filter warehouses with stock >= requested_qty.
    2. Distance Calculation: Compute distance to each eligible warehouse.
    3. Greedy Choice: Select warehouse with minimum distance (locally optimal).
    4. Cost Estimation: Output transportation cost estimate.

    Time Complexity: O(W) where W = number of warehouses evaluated.
    """
    data = request.get_json() or {}
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)
    delivery_location_id = data.get("delivery_location_id")

    if not product_id or not delivery_location_id:
        return jsonify({
            "status": "error",
            "message": "product_id and delivery_location_id are required"
        }), 400

    try:
        product_id = int(product_id)
        quantity = int(quantity)
        delivery_location_id = int(delivery_location_id)
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "product_id and quantity must be integers"}), 400

    # Fetch delivery location
    delivery_location = db.execute_query(
        "SELECT * FROM delivery_locations WHERE id = %s", (delivery_location_id,), fetch="one"
    )
    if not delivery_location:
        return jsonify({"status": "error", "message": f"Delivery location #{delivery_location_id} not found"}), 404

    # Fetch all warehouses with their stock for this product
    warehouses = db.execute_query("""
        SELECT w.id, w.name, w.city, w.location, w.lat, w.lng, w.warehouse_code,
               COALESCE(i.quantity, 0) as stock
        FROM warehouses w
        LEFT JOIN inventory i ON w.id = i.warehouse_id AND i.product_id = %s
        ORDER BY w.id ASC
    """, (product_id,))

    if not warehouses:
        return jsonify({"status": "error", "message": "No warehouses found in the system"}), 404

    # Build routes map from graph for better distance accuracy
    routes_map = {}
    for src_id, edges in dsa_service.network_graph.adj_list.items():
        for edge in edges:
            routes_map[(src_id, edge.destination)] = edge.distance_km

    start_time = time.perf_counter()

    # Execute Greedy Algorithm
    result = select_nearest_suitable_warehouse(
        product_id=product_id,
        requested_qty=quantity,
        delivery_location=delivery_location,
        warehouses=warehouses,
        routes_map=routes_map,
        cost_per_km=float(data.get("cost_per_km", 18.0)),
        base_handling_fee=float(data.get("base_handling_fee", 150.0))
    )

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 4)

    # Log in database
    db.execute_query("""
        INSERT INTO algorithm_logs
        (algorithm_name, data_structure_used, input_summary, output_summary, time_complexity, execution_steps_count, execution_time_ms)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        "Greedy — Nearest Suitable Warehouse Selection",
        "Adjacency List Graph (distance lookup) + Linear Scan",
        f"Product #{product_id}, Qty={quantity}, Dest=Location#{delivery_location_id}",
        (f"Selected: {result['selected_warehouse']['warehouse_name']} "
         f"({result['selected_warehouse']['distance_km']} km)"
         if result.get("success") else "No suitable warehouse found"),
        "O(W)", len(result.get("steps", [])), elapsed_ms
    ), fetch="none")

    return jsonify({
        "status": "success" if result["success"] else "no_candidate",
        "algorithm": "Greedy — Nearest Suitable Warehouse Selection",
        "paradigm": "Greedy (Local Optimal Choice at Each Step)",
        "time_complexity": "O(W)",
        "space_complexity": "O(W)",
        "elapsed_ms": elapsed_ms,
        "success": result["success"],
        "selected_warehouse": result.get("selected_warehouse"),
        "candidates": result.get("candidates", []),
        "eligible_candidates": result.get("eligible_candidates", []),
        "ineligible_candidates": result.get("ineligible_candidates", []),
        "decision_summary": result.get("decision_summary", ""),
        "steps": result.get("steps", []),
        "product_id": product_id,
        "requested_qty": quantity,
        "delivery_location": delivery_location
    })


# ==================== SUPPLIER SELECTION (Multi-Criteria Greedy Ranking) ====================
@optimization_bp.route("/api/optimization/supplier-selection", methods=["POST"])
def run_supplier_selection():
    """
    Executes Multi-Criteria Supplier Selection Optimization.
    Uses a greedy weighted ranking strategy:
    Compares suppliers based on Cost, Reliability, and Delivery Speed.
    """
    data = request.get_json() or {}
    weight_cost = float(data.get("weight_cost", 0.35))
    weight_reliability = float(data.get("weight_reliability", 0.35))
    weight_speed = float(data.get("weight_speed", 0.30))

    start_time = time.perf_counter()
    suppliers = db.execute_query("""
        SELECT s.id, s.supplier_code, s.name, s.category, s.reliability_score,
               s.avg_delivery_time_days, s.address as location,
               COUNT(p.id) as products_supplied,
               COALESCE(AVG(p.price), 500.0) as avg_supply_cost
        FROM suppliers s
        LEFT JOIN products p ON s.id = p.supplier_id
        GROUP BY s.id
        ORDER BY s.id ASC
    """)

    if not suppliers:
        return jsonify({"status": "error", "message": "No suppliers available for evaluation."}), 404

    max_cost = max((float(s["avg_supply_cost"]) for s in suppliers), default=1000.0) or 1000.0
    evaluated = []

    for s in suppliers:
        cost = float(s["avg_supply_cost"])
        reliability = float(s["reliability_score"])
        delivery_days = float(s["avg_delivery_time_days"])

        cost_score = max(0.0, 100.0 - (cost / max_cost * 100.0))
        rel_score = reliability
        speed_score = max(0.0, 100.0 - (delivery_days * 12.0))

        composite_score = (cost_score * weight_cost) + (rel_score * weight_reliability) + (speed_score * weight_speed)

        evaluated.append({
            "id": s["id"],
            "code": s["supplier_code"],
            "name": s["name"],
            "category": s["category"],
            "location": s["location"],
            "supply_cost": round(cost, 2),
            "reliability_score": reliability,
            "avg_delivery_days": delivery_days,
            "cost_score": round(cost_score, 1),
            "reliability_component": round(rel_score, 1),
            "speed_component": round(speed_score, 1),
            "composite_score": round(composite_score, 2),
            "availability": "HIGH" if reliability >= 95.0 else ("MEDIUM" if reliability >= 90.0 else "FAIR")
        })

    evaluated.sort(key=lambda x: x["composite_score"], reverse=True)
    for rank, s in enumerate(evaluated, start=1):
        s["rank"] = rank

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 3)

    return jsonify({
        "status": "success",
        "algorithm": "Multi-Criteria Weighted Ranking (Greedy Supplier Selection)",
        "total_evaluated": len(evaluated),
        "best_supplier": evaluated[0],
        "rankings": evaluated,
        "weights": {"cost": weight_cost, "reliability": weight_reliability, "delivery_time": weight_speed},
        "elapsed_ms": elapsed_ms,
        "time_complexity": "O(n log n) sorting",
        "space_complexity": "O(n)"
    })


# ==================== OUT-OF-SCOPE STUBS ====================
@optimization_bp.route("/api/optimization/dp", methods=["POST"])
def run_dp_optimization():
    """Dynamic Programming is not in this project's algorithm scope."""
    return jsonify({
        "status": "info",
        "message": "Dynamic Programming (Knapsack) is not in this project's algorithm scope.",
        "scope": ["Linked List", "Queue (FIFO)", "Binary Search Tree", "Graph + BFS", "Binary Search", "Greedy Nearest Warehouse"]
    }), 200


@optimization_bp.route("/api/optimization/backtracking", methods=["POST"])
def run_backtracking_route():
    """Backtracking is not in this project's algorithm scope."""
    return jsonify({
        "status": "info",
        "message": "Backtracking Route Optimization is not in this project's algorithm scope.",
        "scope": ["Linked List", "Queue (FIFO)", "Binary Search Tree", "Graph + BFS", "Binary Search", "Greedy Nearest Warehouse"]
    }), 200
