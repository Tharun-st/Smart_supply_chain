"""
Intelligent Supply Chain Management System
Data Structures Interactive Lab API Blueprint

Endpoints for interactive testing & visualization of:
  1. Linked List (/api/dsa/linked-list/...)
  2. Queue (/api/dsa/queue/...)
  3. Binary Search Tree (/api/bst/...)
"""

from flask import Blueprint, jsonify, request
from models.dsa_service import dsa_service
from data_structures.linked_list import LinkedList
from data_structures.queue import LinkedListQueue
from data_structures.bst import BinarySearchTree
import time

dsa_routes_bp = Blueprint("dsa_routes_bp", __name__)

# Standalone playground instances for interactive student testing
demo_linked_list = LinkedList("PlaygroundLinkedList")
demo_queue = LinkedListQueue("PlaygroundQueue")
demo_bst = BinarySearchTree("PlaygroundBST")

# Pre-populate playground with sample data
for v in [50, 30, 70, 20, 40, 60, 80]:
    demo_bst.insert(v, {"label": f"BST-{v}"})

for x in ["Item Alpha", "Item Beta", "Item Gamma"]:
    demo_linked_list.insert_at_end({"id": x, "name": x})
    demo_queue.enqueue({"id": x, "order_number": x})

# ==================== 1. LINKED LIST ENDPOINTS ====================
@dsa_routes_bp.route("/api/dsa/linked-list/view", methods=["GET"])
def view_linked_list():
    nodes = demo_linked_list.to_visual_nodes(id_field="id", label_field="name")
    return jsonify({
        "status": "success",
        "total_nodes": len(demo_linked_list),
        "visual_nodes": nodes,
        "head": nodes[0] if nodes else None,
        "tail": nodes[-1] if nodes else None
    })

@dsa_routes_bp.route("/api/dsa/linked-list/insert", methods=["POST"])
def insert_linked_list():
    data = request.get_json() or {}
    val = data.get("value", "New Item")
    pos = data.get("position", "end")  # beginning or end

    item_dict = {"id": str(val), "name": str(val)}
    if pos == "beginning":
        demo_linked_list.insert_at_beginning(item_dict)
    else:
        demo_linked_list.insert_at_end(item_dict)

    return jsonify({
        "status": "success",
        "message": f"Inserted '{val}' at {pos} of Linked List",
        "visual_nodes": demo_linked_list.to_visual_nodes(id_field="id", label_field="name")
    })

@dsa_routes_bp.route("/api/dsa/linked-list/delete", methods=["POST"])
def delete_linked_list():
    data = request.get_json() or {}
    val = str(data.get("value", "")).strip().lower()
    deleted = demo_linked_list.delete(lambda x: str(x.get("id", "")).lower() == val or str(x.get("name", "")).lower() == val)

    if deleted:
        return jsonify({
            "status": "success",
            "message": f"Deleted node '{val}' from Linked List",
            "visual_nodes": demo_linked_list.to_visual_nodes(id_field="id", label_field="name")
        })
    return jsonify({"status": "error", "message": f"Node '{val}' not found"}), 404

@dsa_routes_bp.route("/api/dsa/linked-list/search", methods=["POST"])
def search_linked_list():
    data = request.get_json() or {}
    val = str(data.get("value", "")).strip().lower()
    res = demo_linked_list.search_with_steps(
        lambda x: str(x.get("id", "")).lower() == val or str(x.get("name", "")).lower() == val,
        id_field="id"
    )
    return jsonify(res)

@dsa_routes_bp.route("/api/dsa/linked-list/traverse", methods=["GET"])
def traverse_linked_list():
    return jsonify(demo_linked_list.traverse_with_steps(id_field="id"))

# ==================== 2. QUEUE ENDPOINTS ====================
@dsa_routes_bp.route("/api/dsa/queue/view", methods=["GET"])
def view_queue():
    return jsonify({
        "status": "success",
        "size": demo_queue.get_size(),
        "visual_queue": demo_queue.to_visual_queue(id_field="id", label_field="order_number"),
        "front": demo_queue.peek()
    })

@dsa_routes_bp.route("/api/dsa/queue/enqueue", methods=["POST"])
def enqueue_queue():
    data = request.get_json() or {}
    val = data.get("value", f"Order-{demo_queue.get_size()+1}")
    demo_queue.enqueue({"id": str(val), "order_number": str(val)})
    return jsonify({
        "status": "success",
        "message": f"Enqueued '{val}' at rear of Queue",
        "size": demo_queue.get_size(),
        "visual_queue": demo_queue.to_visual_queue(id_field="id", label_field="order_number")
    })

@dsa_routes_bp.route("/api/dsa/queue/dequeue", methods=["POST"])
def dequeue_queue():
    if demo_queue.is_empty():
        return jsonify({"status": "error", "message": "Queue Underflow: Queue is empty"}), 400
    dequeued = demo_queue.dequeue()
    return jsonify({
        "status": "success",
        "dequeued": dequeued,
        "size": demo_queue.get_size(),
        "visual_queue": demo_queue.to_visual_queue(id_field="id", label_field="order_number")
    })

@dsa_routes_bp.route("/api/dsa/queue/peek", methods=["GET"])
def peek_queue():
    front = demo_queue.peek()
    return jsonify({"status": "success", "front": front, "is_empty": demo_queue.is_empty()})

# ==================== 3. BINARY SEARCH TREE ENDPOINTS ====================
@dsa_routes_bp.route("/api/bst/view", methods=["GET"])
def view_bst():
    return jsonify({
        "status": "success",
        "tree": demo_bst.to_tree_structure(),
        "node_count": len(demo_bst),
        "height": demo_bst.get_height()
    })

@dsa_routes_bp.route("/api/bst/insert", methods=["POST"])
def insert_bst():
    data = request.get_json() or {}
    try:
        val = int(data.get("value", 50))
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "Numeric value is required"}), 400

    start = time.perf_counter()
    inserted = demo_bst.insert(val, {"label": f"BST-{val}"})
    elapsed_ms = round((time.perf_counter() - start) * 1000, 4)

    return jsonify({
        "status": "success",
        "inserted": inserted,
        "value": val,
        "node_count": len(demo_bst),
        "height": demo_bst.get_height(),
        "elapsed_ms": elapsed_ms,
        "time_complexity": "O(log n) avg / O(n) worst",
        "space_complexity": "O(1)",
        "tree": demo_bst.to_tree_structure()
    })

@dsa_routes_bp.route("/api/bst/delete", methods=["POST"])
def delete_bst():
    data = request.get_json() or {}
    try:
        val = int(data.get("value"))
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "Numeric value is required"}), 400

    start = time.perf_counter()
    deleted = demo_bst.delete(val)
    elapsed_ms = round((time.perf_counter() - start) * 1000, 4)

    if deleted:
        return jsonify({
            "status": "success",
            "message": f"Key {val} deleted from BST",
            "node_count": len(demo_bst),
            "height": demo_bst.get_height(),
            "elapsed_ms": elapsed_ms,
            "tree": demo_bst.to_tree_structure()
        })
    return jsonify({"status": "error", "message": f"Key {val} not found in BST"}), 404

@dsa_routes_bp.route("/api/bst/search", methods=["POST"])
def search_bst():
    data = request.get_json() or {}
    try:
        val = int(data.get("value"))
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "Numeric value is required"}), 400

    start = time.perf_counter()
    res = demo_bst.search(val)
    elapsed_ms = round((time.perf_counter() - start) * 1000, 4)

    path_nodes = res.get("path", [])
    if res.get("found"):
        path_str = " -> ".join(map(str, path_nodes)) + " -> FOUND"
    else:
        path_str = " -> ".join(map(str, path_nodes)) + " -> NOT FOUND" if path_nodes else "EMPTY"

    return jsonify({
        "status": "success",
        "target": val,
        "found": res.get("found", False),
        "path": path_nodes,
        "formatted_path": path_str,
        "comparisons": res.get("comparisons", 0),
        "node_count": len(demo_bst),
        "height": demo_bst.get_height(),
        "elapsed_ms": elapsed_ms,
        "time_complexity": "O(log n) avg / O(n) worst",
        "space_complexity": "O(1)"
    })

@dsa_routes_bp.route("/api/bst/traversal", methods=["GET"])
def traverse_bst():
    return jsonify({
        "status": "success",
        "inorder": demo_bst.inorder_traversal(),
        "preorder": demo_bst.preorder_traversal(),
        "postorder": demo_bst.postorder_traversal()
    })
