"""
Intelligent Supply Chain Management System
Algorithms API Blueprint

Project Scope Algorithms:
  1. Binary Search — with step-by-step comparison trace on sorted supply chain records
  2. BFS — Graph traversal (handled by network.py)
  3. Greedy — Nearest Warehouse Selection (handled by optimization.py)
"""

from flask import Blueprint, jsonify, request
from models.database import db
from models.dsa_service import dsa_service
from algorithms.binary_search import binary_search_records
from services.complexity_service import THEORETICAL_COMPLEXITY_TABLE
import time

algorithms_bp = Blueprint("algorithms_bp", __name__)

# ==================== 1. BINARY SEARCH ====================
@algorithms_bp.route("/api/algorithms/search", methods=["POST"])
def execute_search():
    """
    Executes Binary Search on chosen entity records (Products, Suppliers, or Orders).
    Returns full step-by-step comparison trace for UI visualization.
    """
    data = request.get_json() or {}
    algorithm = data.get("algorithm", "binary_search")
    entity_type = data.get("entity_type", "product")
    target = data.get("target")

    if target is None:
        return jsonify({"status": "error", "message": "Search target is required"}), 400

    # Retrieve records
    if entity_type == "product":
        records = db.execute_query("SELECT id, product_code, name, category, price FROM products ORDER BY id ASC")
        key_field = "id"
        label_field = "name"
    elif entity_type == "supplier":
        records = db.execute_query("SELECT id, supplier_code, name, contact_person, category FROM suppliers ORDER BY id ASC")
        key_field = "id"
        label_field = "name"
    elif entity_type == "order":
        records = db.execute_query("SELECT id, order_number, customer_name, quantity, status FROM orders ORDER BY id ASC")
        key_field = "id"
        label_field = "customer_name"
    else:
        return jsonify({"status": "error", "message": f"Unknown entity type '{entity_type}'"}), 400

    start_time = time.perf_counter()

    if algorithm == "binary_search":
        result = binary_search_records(records, key_field=key_field, target_value=target, key_type=int)
        algo_name = "Binary Search"
        time_complexity = {"average": "O(log n)", "best": "O(1)", "worst": "O(log n)"}
        space_complexity = "O(1)"
    else:
        # Linear search fallback (simple sequential scan)
        comparisons = 0
        found_record = None
        steps = []
        target_val = str(target)
        for i, rec in enumerate(records):
            comparisons += 1
            val = str(rec.get(key_field, ""))
            match = (val == target_val)
            steps.append({
                "iteration": comparisons,
                "index": i,
                "key_value": val,
                "target": target_val,
                "decision": "EQUAL" if match else "NOT_EQUAL",
                "description": f"Comparison #{comparisons}: Record key '{val}' {'matches' if match else 'does not match'} target '{target_val}'."
            })
            if match:
                found_record = rec
                break

        result = {
            "found": found_record is not None,
            "target": target,
            "key_field": key_field,
            "found_index": comparisons - 1 if found_record else -1,
            "record": found_record,
            "total_records": len(records),
            "comparisons": comparisons,
            "steps": steps,
            "dataset_keys": [rec.get(key_field) for rec in records]
        }
        algo_name = "Linear Search"
        time_complexity = {"average": "O(n)", "best": "O(1)", "worst": "O(n)"}
        space_complexity = "O(1)"

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 4)

    # Log in database
    db.execute_query("""
        INSERT INTO algorithm_logs
        (algorithm_name, data_structure_used, input_summary, output_summary, time_complexity, execution_steps_count, execution_time_ms)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        algo_name,
        "Sorted Array Records",
        f"Search {key_field}={target} in {len(records)} {entity_type} records",
        f"{'Found' if result['found'] else 'Not Found'} in {result['comparisons']} comparisons",
        time_complexity["average"], result["comparisons"], elapsed_ms
    ), fetch="none")

    return jsonify({
        "status": "success",
        "algorithm": algo_name,
        "entity_type": entity_type,
        "found": result["found"],
        "comparisons": result["comparisons"],
        "record": result.get("record"),
        "found_index": result.get("found_index", -1),
        "total_records": result.get("total_records", len(records)),
        "steps": result.get("steps", []),
        "dataset_keys": result.get("dataset_keys", []),
        "max_theoretical_comparisons": result.get("max_theoretical_comparisons"),
        "time_complexity": time_complexity,
        "space_complexity": space_complexity,
        "elapsed_ms": elapsed_ms
    })


# ==================== 2. QUICK SORT & SORTING LABORATORY ====================
@algorithms_bp.route("/api/algorithms/sort", methods=["POST"])
def execute_sort():
    """
    Executes Quick Sort on chosen supply chain records (Products, Suppliers, Orders, Inventory)
    or custom numeric/record arrays.
    Returns full step-by-step partition trace, Big-O metrics, comparisons, and swaps.
    """
    from algorithms.quick_sort import quick_sort_records

    data = request.get_json() or {}
    algorithm = data.get("algorithm", "quick_sort").lower()
    entity_type = data.get("entity_type", "product")
    sort_field = data.get("sort_field", "price")
    order = data.get("order", "asc").lower()
    reverse = (order == "desc")
    custom_data = data.get("custom_data")

    if custom_data is not None and isinstance(custom_data, list):
        records = custom_data
        field_to_sort = sort_field if (records and isinstance(records[0], dict)) else None
    elif entity_type == "product":
        records = db.execute_query("""
            SELECT p.id, p.product_code, p.name, p.category, p.price,
                   COALESCE(SUM(i.quantity), 0) as stock
            FROM products p
            LEFT JOIN inventory i ON p.id = i.product_id
            GROUP BY p.id
            ORDER BY p.id ASC
        """)
        field_to_sort = sort_field or "price"
    elif entity_type == "supplier":
        records = db.execute_query("""
            SELECT id, supplier_code, name, category,
                   reliability_score, avg_delivery_time_days
            FROM suppliers
            ORDER BY id ASC
        """)
        field_to_sort = sort_field or "reliability_score"
    elif entity_type == "order":
        records = db.execute_query("""
            SELECT id, order_number, customer_name, quantity, total_amount, status
            FROM orders
            ORDER BY id ASC
        """)
        field_to_sort = sort_field or "quantity"
    elif entity_type == "inventory":
        records = db.execute_query("""
            SELECT i.id, i.product_id, p.name as product_name, i.warehouse_id, i.quantity, i.reorder_level
            FROM inventory i
            LEFT JOIN products p ON i.product_id = p.id
            ORDER BY i.id ASC
        """)
        field_to_sort = sort_field or "quantity"
    else:
        return jsonify({"status": "error", "message": f"Unsupported entity type '{entity_type}'"}), 400

    # Quick Sort is the single, exclusive sorting algorithm for the project
    result = quick_sort_records(records, sort_key=field_to_sort, reverse=reverse)
    algo_name = "Quick Sort"
    ds_used = "In-Place Pivot Partitioning"

    # Log in database audit trail
    try:
        db.execute_query("""
            INSERT INTO algorithm_logs
            (algorithm_name, data_structure_used, input_summary, output_summary, time_complexity, execution_steps_count, execution_time_ms)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            algo_name,
            ds_used,
            f"Sort {len(records)} {entity_type} records by '{field_to_sort}' ({order.upper()})",
            f"Sorted {len(records)} records in {result['comparisons']} comparisons, {result.get('swaps', 0)} swaps",
            result["time_complexity"]["average"],
            result["comparisons"],
            result["elapsed_ms"]
        ), fetch="none")
    except Exception:
        pass

    return jsonify({
        "status": "success",
        "algorithm": algo_name,
        "entity_type": entity_type,
        "sort_field": field_to_sort,
        "order": order,
        "reverse": reverse,
        "total_records": result["total_records"],
        "comparisons": result["comparisons"],
        "swaps": result.get("swaps", 0),
        "elapsed_ms": result["elapsed_ms"],
        "time_complexity": result["time_complexity"],
        "space_complexity": result["space_complexity"],
        "steps": result.get("steps", []),
        "sorted_records": result["sorted_records"]
    })


# ==================== 3. ALGORITHM COMPARISON ====================
@algorithms_bp.route("/api/algorithms/compare", methods=["POST"])
def compare_algorithms():
    """
    Compares algorithms head-to-head on synthetic data.
    Supports Searching (Binary vs Linear) and Sorting (Quick Sort vs Insertion Sort).
    """
    data = request.get_json() or {}
    comp_type = data.get("comparison_type", "search")
    input_size = int(data.get("input_size", 500))

    from services.complexity_service import benchmark_algorithm

    if comp_type == "sorting":
        res_insertion = benchmark_algorithm("insertion_sort", min(input_size, 1000))
        res_quick = benchmark_algorithm("quick_sort", input_size)

        speedup = round(max(1.0, res_insertion["elapsed_ms"]) / max(0.001, res_quick["elapsed_ms"]), 1)
        winner = "Quick Sort"
        reason = (f"Quick Sort finished in {res_quick['elapsed_ms']} ms ({res_quick['comparisons']} comparisons O(n log n)) vs "
                  f"{res_insertion['elapsed_ms']} ms ({res_insertion['comparisons']} comparisons O(n²)) for Insertion Sort, a {speedup}x speedup!")

        return jsonify({
            "status": "success",
            "comparison_type": "sorting",
            "input_size": input_size,
            "algorithm_1": {
                "name": "Insertion Sort",
                "elapsed_ms": res_insertion["elapsed_ms"],
                "comparisons": res_insertion["comparisons"],
                "swaps": res_insertion.get("swaps", 0),
                "time_complexity": "O(n²)"
            },
            "algorithm_2": {
                "name": "Quick Sort",
                "elapsed_ms": res_quick["elapsed_ms"],
                "comparisons": res_quick["comparisons"],
                "swaps": res_quick.get("swaps", 0),
                "time_complexity": "O(n log n)"
            },
            "winner": winner,
            "reason": reason
        })

    # Default: search comparison
    res_linear = benchmark_algorithm("linear_search", input_size)
    res_binary = benchmark_algorithm("binary_search", input_size)

    speedup = round(max(1, res_linear["comparisons"]) / max(1, res_binary["comparisons"]), 1)
    winner = "Binary Search"
    reason = (f"Binary Search completed in {res_binary['comparisons']} comparisons O(log n) vs "
              f"{res_linear['comparisons']} comparisons for Linear Search O(n), a {speedup}x efficiency gain!")

    return jsonify({
        "status": "success",
        "comparison_type": "linear_vs_binary",
        "input_size": input_size,
        "algorithm_1": {
            "name": "Linear Search",
            "elapsed_ms": res_linear["elapsed_ms"],
            "comparisons": res_linear["comparisons"],
            "time_complexity": "O(n)"
        },
        "algorithm_2": {
            "name": "Binary Search",
            "elapsed_ms": res_binary["elapsed_ms"],
            "comparisons": res_binary["comparisons"],
            "time_complexity": "O(log n)"
        },
        "winner": winner,
        "reason": reason
    })


# ==================== 4. COMPLEXITY TABLE ====================
@algorithms_bp.route("/api/algorithms/complexity/table", methods=["GET"])
def get_complexity_table():
    """Returns theoretical Big-O complexity reference table for in-scope algorithms."""
    in_scope_ids = {"binary_search", "bfs", "bst_search", "quick_sort", "linear_search"}
    filtered = [row for row in THEORETICAL_COMPLEXITY_TABLE if row["id"] in in_scope_ids]
    return jsonify({
        "status": "success",
        "table": filtered
    })


@algorithms_bp.route("/api/algorithms/complexity/benchmark", methods=["POST"])
def run_benchmark():
    """Runs empirical benchmark across multiple input sizes."""
    data = request.get_json() or {}
    algorithm_id = data.get("algorithm_id", "quick_sort")
    if algorithm_id not in ("binary_search", "bfs", "bst_search", "linear_search", "quick_sort", "insertion_sort", "merge_sort"):
        algorithm_id = "quick_sort"
    sizes = data.get("sizes", [50, 100, 250, 500, 1000])
    from services.complexity_service import run_benchmark_curve
    curve_data = run_benchmark_curve(algorithm_id, sizes)
    return jsonify({"status": "success", "result": curve_data})


# ==================== 5. ALGORITHM AUDIT LOGS ====================
@algorithms_bp.route("/api/algorithms/logs", methods=["GET"])
def get_algorithm_logs():
    """Returns recent algorithm audit trail logs."""
    limit = request.args.get("limit", 100, type=int)
    logs = db.execute_query("SELECT * FROM algorithm_logs ORDER BY id DESC LIMIT %s", (limit,))
    return jsonify({"status": "success", "count": len(logs), "logs": logs})


@algorithms_bp.route("/api/algorithms/logs/clear", methods=["POST"])
def clear_algorithm_logs():
    """Clears all algorithm audit logs."""
    db.execute_query("DELETE FROM algorithm_logs")
    return jsonify({"status": "success", "message": "Algorithm audit logs cleared successfully"})
