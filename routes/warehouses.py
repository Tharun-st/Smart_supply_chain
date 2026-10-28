"""
Intelligent Supply Chain Management System
Warehouses API Blueprint
"""

from flask import Blueprint, jsonify, request
from models.database import db

warehouses_bp = Blueprint("warehouses_bp", __name__)

@warehouses_bp.route("/api/warehouses", methods=["GET"])
def get_warehouses():
    warehouses = db.execute_query("""
        SELECT w.*, 
               COALESCE(SUM(i.quantity), 0) as current_stock,
               COUNT(i.id) as product_types_count,
               ROUND((COALESCE(SUM(i.quantity), 0) * 100.0) / w.capacity, 1) as utilization_pct
        FROM warehouses w
        LEFT JOIN inventory i ON w.id = i.warehouse_id
        GROUP BY w.id
        ORDER BY w.id ASC
    """)
    return jsonify({
        "status": "success",
        "data": warehouses,
        "total_warehouses": len(warehouses)
    })

@warehouses_bp.route("/api/warehouses/<int:warehouse_id>", methods=["GET"])
def get_warehouse_details(warehouse_id):
    wh = db.execute_query("SELECT * FROM warehouses WHERE id = %s", (warehouse_id,), fetch="one")
    if not wh:
        return jsonify({"status": "error", "message": "Warehouse not found"}), 404

    inventory = db.execute_query("""
        SELECT i.*, p.name as product_name, p.product_code, p.category, p.price
        FROM inventory i
        JOIN products p ON i.product_id = p.id
        WHERE i.warehouse_id = %s
        ORDER BY i.quantity DESC
    """, (warehouse_id,))

    return jsonify({
        "status": "success",
        "warehouse": wh,
        "inventory": inventory
    })

@warehouses_bp.route("/api/warehouses", methods=["POST"])
def create_warehouse():
    data = request.get_json() or {}
    code = data.get("warehouse_code")
    name = data.get("name")
    location = data.get("location")
    city = data.get("city", "")
    capacity = int(data.get("capacity", 40000))

    if not name or not location:
        return jsonify({"status": "error", "message": "Warehouse name and location are required"}), 400

    if not code:
        code = f"WH-{name[:3].upper()}"

    try:
        wh_id = db.execute_query("""
            INSERT INTO warehouses (warehouse_code, name, location, city, capacity, lat, lng)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (code, name, location, city, capacity, float(data.get("lat", 0.0)), float(data.get("lng", 0.0))), fetch="insert")

        # Also add as vertex to graph
        from models.dsa_service import dsa_service
        dsa_service.network_graph.add_vertex(f"WH-{wh_id}", name, "warehouse", city)

        return jsonify({
            "status": "success",
            "message": f"Warehouse '{name}' added successfully",
            "warehouse_id": wh_id
        }), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@warehouses_bp.route("/api/warehouses/<int:warehouse_id>", methods=["PUT"])
def update_warehouse(warehouse_id):
    data = request.get_json() or {}
    name = data.get("name")
    location = data.get("location")
    city = data.get("city")
    capacity = data.get("capacity")

    try:
        db.execute_query("""
            UPDATE warehouses 
            SET name = COALESCE(%s, name), location = COALESCE(%s, location),
                city = COALESCE(%s, city), capacity = COALESCE(%s, capacity)
            WHERE id = %s
        """, (name, location, city, capacity, warehouse_id), fetch="none")
        return jsonify({"status": "success", "message": f"Warehouse #{warehouse_id} updated successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@warehouses_bp.route("/api/warehouses/<int:warehouse_id>", methods=["DELETE"])
def delete_warehouse(warehouse_id):
    try:
        db.execute_query("DELETE FROM warehouses WHERE id = %s", (warehouse_id,), fetch="none")
        from models.dsa_service import dsa_service
        dsa_service.network_graph.remove_vertex(f"WH-{warehouse_id}") if hasattr(dsa_service.network_graph, "remove_vertex") else None
        return jsonify({"status": "success", "message": f"Warehouse #{warehouse_id} deleted successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
