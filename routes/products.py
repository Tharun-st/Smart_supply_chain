"""
Intelligent Supply Chain Management System
Products API Blueprint

Data Structure Demonstrated: Singly Linked List
Features:
  - Full CRUD (Create, Read, Update, Delete)
  - Interactive Linked List Operations (Insert, Delete, Search, Traverse)
  - Step-by-step traversal logging for animated UI visualization
  - Pointer metadata: HEAD, TAIL, Next Pointers, Operations Count
"""

from flask import Blueprint, jsonify, request
from models.dsa_service import dsa_service
from models.database import db
import time

products_bp = Blueprint("products_bp", __name__)

@products_bp.route("/api/products", methods=["GET"])
def get_products():
    """Traverses product records from the custom Linked List."""
    records = dsa_service.product_linked_list.to_list()
    visual_nodes = dsa_service.product_linked_list.to_visual_nodes(id_field="product_code", label_field="name")
    head_node = visual_nodes[0] if visual_nodes else None
    tail_node = visual_nodes[-1] if visual_nodes else None

    return jsonify({
        "status": "success",
        "data_structure": "Singly Linked List",
        "total_count": len(records),
        "head": head_node,
        "tail": tail_node,
        "data": records,
        "visual_nodes": visual_nodes,
        "time_complexity": {
            "insert_head": "O(1)",
            "insert_end": "O(n)",
            "search": "O(n)",
            "delete": "O(n)"
        },
        "space_complexity": "O(n)",
        "explanation": "Product records are dynamically chained within our custom Singly Linked List. Inserting new catalog items is performed via pointer linkage."
    })

@products_bp.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """Searches for a single product in the Linked List."""
    node = dsa_service.product_linked_list.search(lambda p: p["id"] == product_id)
    if node:
        return jsonify({"status": "success", "data": node.data})
    return jsonify({"status": "error", "message": f"Product #{product_id} not found"}), 404

@products_bp.route("/api/products", methods=["POST"])
def create_product():
    """Adds a new product and links it into the custom Linked List."""
    data = request.get_json() or {}
    if not data.get("name") or not data.get("category"):
        return jsonify({"status": "error", "message": "Product name and category are required"}), 400

    try:
        new_prod = dsa_service.add_product(data)
        visual_nodes = dsa_service.product_linked_list.to_visual_nodes(id_field="product_code", label_field="name")
        return jsonify({
            "status": "success",
            "message": f"Product '{new_prod['name']}' linked into catalog list (O(n) tail insertion)",
            "data": new_prod,
            "visual_nodes": visual_nodes,
            "total_count": len(visual_nodes)
        }), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@products_bp.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    """Updates product record in database and synchronized Linked List."""
    data = request.get_json() or {}
    name = data.get("name")
    category = data.get("category")
    price = float(data.get("price", 0.0))
    unit = data.get("unit", "units")
    supplier_id = data.get("supplier_id")

    if not name:
        return jsonify({"status": "error", "message": "Product name is required"}), 400

    try:
        db.execute_query("""
            UPDATE products 
            SET name = %s, category = %s, price = %s, unit = %s, supplier_id = %s
            WHERE id = %s
        """, (name, category, price, unit, supplier_id, product_id), fetch="none")

        dsa_service.product_linked_list.update(lambda p: p["id"] == product_id, {
            "id": product_id,
            "name": name,
            "category": category,
            "price": price,
            "unit": unit,
            "supplier_id": supplier_id
        })
        dsa_service._load_products()

        return jsonify({
            "status": "success",
            "message": f"Product #{product_id} updated successfully",
            "visual_nodes": dsa_service.product_linked_list.to_visual_nodes(id_field="product_code", label_field="name")
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@products_bp.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    """Unlinks and deletes a product from the Linked List and database."""
    try:
        success = dsa_service.delete_product(product_id)
        if success:
            visual_nodes = dsa_service.product_linked_list.to_visual_nodes(id_field="product_code", label_field="name")
            return jsonify({
                "status": "success",
                "message": f"Product #{product_id} unlinked and deleted from Linked List",
                "visual_nodes": visual_nodes,
                "total_count": len(visual_nodes)
            })
        return jsonify({"status": "error", "message": "Product not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ==================== DSA SPECIFIC OPERATIONS ====================
@products_bp.route("/api/products/ll-traverse", methods=["POST"])
def traverse_linked_list():
    """Traverses Linked List and returns animated step sequence."""
    start = time.perf_counter()
    res = dsa_service.product_linked_list.traverse_with_steps(id_field="product_code")
    elapsed_ms = round((time.perf_counter() - start) * 1000, 4)
    res["elapsed_ms"] = elapsed_ms
    res["visual_nodes"] = dsa_service.product_linked_list.to_visual_nodes(id_field="product_code", label_field="name")
    return jsonify(res)

@products_bp.route("/api/products/ll-search", methods=["POST"])
def search_linked_list():
    """Searches Linked List node-by-node and records step history."""
    data = request.get_json() or {}
    query = str(data.get("query", "")).strip().lower()

    if not query:
        return jsonify({"status": "error", "message": "Search query is required"}), 400

    start = time.perf_counter()
    res = dsa_service.product_linked_list.search_with_steps(
        lambda p: (
            str(p.get("product_code", "")).lower() == query or
            str(p.get("id", "")) == query or
            query in str(p.get("name", "")).lower()
        ),
        id_field="product_code"
    )
    res["elapsed_ms"] = round((time.perf_counter() - start) * 1000, 4)
    return jsonify(res)
