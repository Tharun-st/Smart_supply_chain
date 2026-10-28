"""
Intelligent Supply Chain Management System
Suppliers API Blueprint

Data Structure Demonstrated: Singly Linked List
Features:
  - Full CRUD (Create, Read, Update, Delete)
  - Supplier Performance Ranking (1st, 2nd, 3rd Best Supplier)
  - Fields: Supplier ID, Supplier Name, Contact, Location, Reliability, Avg Delivery Time
"""

from flask import Blueprint, jsonify, request
from models.dsa_service import dsa_service
from models.database import db

suppliers_bp = Blueprint("suppliers_bp", __name__)

@suppliers_bp.route("/api/suppliers", methods=["GET"])
def get_suppliers():
    """Traverses supplier records from custom Linked List with performance metrics."""
    records = dsa_service.supplier_linked_list.to_list()
    visual_nodes = dsa_service.supplier_linked_list.to_visual_nodes(id_field="supplier_code", label_field="name")

    return jsonify({
        "status": "success",
        "data_structure": "Singly Linked List",
        "total_count": len(records),
        "data": records,
        "visual_nodes": visual_nodes,
        "explanation": "Suppliers are stored and traversed via a custom Singly Linked List (Node -> Next). Each node maintains a pointer to the subsequent supplier record."
    })

@suppliers_bp.route("/api/suppliers/<int:supplier_id>", methods=["GET"])
def get_supplier(supplier_id):
    """Searches for a single supplier in the Linked List."""
    node = dsa_service.supplier_linked_list.search(lambda s: s["id"] == supplier_id)
    if node:
        return jsonify({"status": "success", "data": node.data})
    return jsonify({"status": "error", "message": f"Supplier #{supplier_id} not found"}), 404

@suppliers_bp.route("/api/suppliers/performance", methods=["GET"])
def get_supplier_performance():
    """
    Computes performance rankings based on composite score:
    Score = (Reliability * 0.7) + ((10 - Avg Delivery Time) * 3)
    Returns Top 3 suppliers and full ranked list.
    """
    suppliers = dsa_service.supplier_linked_list.to_list()

    ranked = []
    for s in suppliers:
        rel = float(s.get("reliability_score", 95.0) or 95.0)
        del_time = float(s.get("avg_delivery_time_days", 3.0) or 3.0)
        composite = round((rel * 0.7) + (max(0.0, 10.0 - del_time) * 3.0), 2)
        
        ranked.append({
            "id": s.get("id"),
            "supplier_code": s.get("supplier_code"),
            "name": s.get("name"),
            "category": s.get("category"),
            "location": s.get("address", "N/A"),
            "contact_person": s.get("contact_person"),
            "reliability": rel,
            "avg_delivery_time": del_time,
            "performance_score": composite,
            "products_count": s.get("products_count", 0)
        })

    # Sort descending by composite score
    ranked.sort(key=lambda x: x["performance_score"], reverse=True)

    # Assign ranks
    for idx, item in enumerate(ranked):
        item["rank"] = idx + 1
        if idx == 0:
            item["badge"] = "🥇 1. Best Supplier"
        elif idx == 1:
            item["badge"] = "🥈 2. Second Supplier"
        elif idx == 2:
            item["badge"] = "🥉 3. Third Supplier"
        else:
            item["badge"] = f"#{idx + 1}"

    top_3 = ranked[:3]

    return jsonify({
        "status": "success",
        "total_suppliers": len(ranked),
        "top_3_ranking": top_3,
        "all_ranked": ranked
    })

@suppliers_bp.route("/api/suppliers", methods=["POST"])
def create_supplier():
    data = request.get_json() or {}
    if not data.get("name"):
        return jsonify({"status": "error", "message": "Supplier name is required"}), 400

    try:
        new_supplier = dsa_service.add_supplier(data)
        return jsonify({
            "status": "success",
            "message": f"Supplier '{new_supplier['name']}' inserted into Linked List (O(1) tail pointer)",
            "data": new_supplier
        }), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@suppliers_bp.route("/api/suppliers/<int:supplier_id>", methods=["PUT"])
def update_supplier(supplier_id):
    data = request.get_json() or {}
    try:
        success = dsa_service.update_supplier(supplier_id, data)
        if success:
            return jsonify({"status": "success", "message": f"Supplier #{supplier_id} updated in Linked List"})
        return jsonify({"status": "error", "message": "Supplier not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@suppliers_bp.route("/api/suppliers/<int:supplier_id>", methods=["DELETE"])
def delete_supplier(supplier_id):
    try:
        success = dsa_service.delete_supplier(supplier_id)
        if success:
            return jsonify({"status": "success", "message": f"Supplier #{supplier_id} unlinked and removed from Linked List"})
        return jsonify({"status": "error", "message": "Supplier not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
