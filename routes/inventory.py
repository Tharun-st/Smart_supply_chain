"""
Intelligent Supply Chain Management System
Inventory API Blueprint

Data Structure Demonstrated: Binary Search Tree (BST)
Features:
  - Fields: Product, Warehouse, Available Quantity, Reserved Quantity, Reorder Level, Status
  - Categories: Available Stock, Low Stock, Out of Stock, Overstock
  - Automatic Alerts: Generates proactive notifications for low stock thresholds
  - Filtering by Warehouse and Product
  - Visual BST hierarchy, In-order/Pre-order/Post-order traversals, and Search path
"""

from flask import Blueprint, jsonify, request
from models.dsa_service import dsa_service
from models.database import db

inventory_bp = Blueprint("inventory_bp", __name__)

def _calculate_status(quantity: int, reorder_level: int) -> str:
    if quantity <= 0:
        return "Out of Stock"
    elif quantity <= reorder_level:
        return "Low Stock"
    elif quantity > reorder_level * 6:
        return "Overstock"
    return "Available"

@inventory_bp.route("/api/inventory", methods=["GET"])
def get_inventory():
    """
    Returns inventory records enriched with real-time stock status,
    automatic alerts, and the serialized BST structure.
    """
    warehouse_filter = request.args.get("warehouse_id")
    product_filter = request.args.get("product_id")

    query = """
        SELECT i.*, p.name as product_name, p.product_code, p.category, p.price,
               w.name as warehouse_name, w.city as warehouse_city
        FROM inventory i
        JOIN products p ON i.product_id = p.id
        JOIN warehouses w ON i.warehouse_id = w.id
        WHERE 1=1
    """
    params = []
    if warehouse_filter:
        query += " AND i.warehouse_id = %s"
        params.append(int(warehouse_filter))
    if product_filter:
        query += " AND i.product_id = %s"
        params.append(int(product_filter))

    query += " ORDER BY i.id ASC"

    records = db.execute_query(query, tuple(params))

    # Calculate status, alerts, and summary counts
    status_counts = {"Available": 0, "Low Stock": 0, "Out of Stock": 0, "Overstock": 0}
    alerts = []

    for r in records:
        qty = int(r.get("quantity", 0))
        reorder = int(r.get("reorder_level", 50))
        status = _calculate_status(qty, reorder)
        r["status"] = status
        status_counts[status] = status_counts.get(status, 0) + 1

        if status in ("Low Stock", "Out of Stock"):
            alerts.append({
                "inventory_id": r["id"],
                "product_code": r["product_code"],
                "product_name": r["product_name"],
                "warehouse_name": r["warehouse_name"],
                "quantity": qty,
                "reorder_level": reorder,
                "severity": "critical" if status == "Out of Stock" else "warning",
                "message": f"LOW STOCK ALERT: {r['product_name']} ({r['product_code']}) in {r['warehouse_name']} is at {qty} units (Reorder level: {reorder})."
            })

    # Visual BST hierarchy & in-order traversal
    tree_hierarchy = dsa_service.inventory_bst.to_tree_structure()
    inorder_nodes = dsa_service.inventory_bst.inorder_traversal()

    return jsonify({
        "status": "success",
        "data_structure": "Binary Search Tree (BST)",
        "total_records": len(records),
        "data": records,
        "status_summary": status_counts,
        "alerts": alerts,
        "alerts_count": len(alerts),
        "tree_hierarchy": tree_hierarchy,
        "inorder_traversal": inorder_nodes,
        "bst_size": len(dsa_service.inventory_bst),
        "bst_height": dsa_service.inventory_bst.get_height(),
        "explanation": "Inventory records are stored in a hierarchical Binary Search Tree keyed by Inventory ID. Left child key < Parent key < Right child key. In-order traversal naturally yields records in sorted order in O(n) time."
    })

@inventory_bp.route("/api/inventory/alerts", methods=["GET"])
def get_inventory_alerts():
    """Returns only active low stock alerts."""
    records = db.execute_query("""
        SELECT i.*, p.name as product_name, p.product_code, w.name as warehouse_name
        FROM inventory i
        JOIN products p ON i.product_id = p.id
        JOIN warehouses w ON i.warehouse_id = w.id
        WHERE i.quantity <= i.reorder_level
        ORDER BY i.quantity ASC
    """)
    alerts = []
    for r in records:
        status = "Out of Stock" if r["quantity"] == 0 else "Low Stock"
        alerts.append({
            "product_code": r["product_code"],
            "product_name": r["product_name"],
            "warehouse_name": r["warehouse_name"],
            "quantity": r["quantity"],
            "reorder_level": r["reorder_level"],
            "status": status,
            "message": f"{status.upper()}: Product {r['product_code']} ({r['product_name']}) has reached reorder level ({r['quantity']}/{r['reorder_level']} units)."
        })
    return jsonify({"status": "success", "alerts": alerts, "count": len(alerts)})

@inventory_bp.route("/api/inventory", methods=["POST"])
def add_inventory():
    data = request.get_json() or {}
    if not data.get("product_id") or not data.get("warehouse_id"):
        return jsonify({"status": "error", "message": "Product ID and Warehouse ID are required"}), 400

    try:
        new_inv = dsa_service.insert_inventory(data)
        return jsonify({
            "status": "success",
            "message": f"Inventory record #{new_inv['id']} inserted into BST with key {new_inv['id']}",
            "data": new_inv,
            "tree_hierarchy": dsa_service.inventory_bst.to_tree_structure()
        }), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@inventory_bp.route("/api/inventory/<int:inv_id>", methods=["PUT"])
def update_inventory(inv_id):
    data = request.get_json() or {}
    quantity = data.get("quantity")
    reorder_level = data.get("reorder_level")
    reserved_qty = data.get("reserved_quantity", 0)

    if quantity is None:
        return jsonify({"status": "error", "message": "Quantity is required"}), 400

    try:
        db.execute_query("""
            UPDATE inventory 
            SET quantity = %s, reorder_level = COALESCE(%s, reorder_level), reserved_quantity = %s
            WHERE id = %s
        """, (int(quantity), reorder_level, int(reserved_qty), inv_id), fetch="none")

        dsa_service.update_stock(inv_id, int(quantity))

        return jsonify({
            "status": "success",
            "message": f"Inventory #{inv_id} updated successfully",
            "tree_hierarchy": dsa_service.inventory_bst.to_tree_structure()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@inventory_bp.route("/api/inventory/<int:inv_id>", methods=["DELETE"])
def delete_inventory(inv_id):
    try:
        success = dsa_service.delete_inventory(inv_id)
        if success:
            return jsonify({
                "status": "success",
                "message": f"Node #{inv_id} removed from BST and inventory table",
                "tree_hierarchy": dsa_service.inventory_bst.to_tree_structure()
            })
        return jsonify({"status": "error", "message": "Inventory record not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
