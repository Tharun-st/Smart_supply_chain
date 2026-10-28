"""
Intelligent Supply Chain Management System
Reports API Blueprint

Generates academic reports and CSV export streams for:
  1. Product Report
  2. Supplier Report
  3. Inventory Report
  4. Order Report
  5. Delivery & Route Report
  6. Algorithm Performance Report
  7. Optimization Report
"""

from flask import Blueprint, jsonify, request, Response
from models.database import db
from models.dsa_service import dsa_service
import csv
import io
import time

reports_bp = Blueprint("reports_bp", __name__)

@reports_bp.route("/api/dashboard/stats", methods=["GET"])
def get_dashboard_stats():
    """Returns aggregated KPI counts and chart datasets for the main dashboard."""
    counts = {
        "products": db.execute_query("SELECT COUNT(*) as c FROM products", fetch="one")["c"],
        "suppliers": db.execute_query("SELECT COUNT(*) as c FROM suppliers", fetch="one")["c"],
        "inventory_items_count": db.execute_query("SELECT COUNT(*) as c FROM inventory", fetch="one")["c"],
        "inventory_total_qty": db.execute_query("SELECT COALESCE(SUM(quantity), 0) as s FROM inventory", fetch="one")["s"],
        "pending_orders": dsa_service.order_queue.get_size(),
        "processed_orders": getattr(dsa_service, "order_stack", None).get_size() if hasattr(dsa_service, "order_stack") else (db.execute_query("SELECT COUNT(*) as c FROM orders WHERE status != 'PENDING'", fetch="one") or {}).get("c", 0),
        "warehouses": db.execute_query("SELECT COUNT(*) as c FROM warehouses", fetch="one")["c"],
        "delivery_locations": db.execute_query("SELECT COUNT(*) as c FROM delivery_locations", fetch="one")["c"],
        "active_routes": db.execute_query("SELECT COUNT(*) as c FROM routes", fetch="one")["c"]
    }

    # Chart 1: Inventory status counts
    inv_rows = db.execute_query("SELECT quantity, reorder_level FROM inventory")
    avail = 0
    low = 0
    out_stock = 0
    overstock = 0
    for r in inv_rows:
        q = r["quantity"]
        rl = r["reorder_level"]
        if q <= 0:
            out_stock += 1
        elif q <= rl:
            low += 1
        elif q > rl * 6:
            overstock += 1
        else:
            avail += 1

    counts["low_stock_products"] = low
    priority_rows = db.execute_query("SELECT priority, COUNT(*) as count FROM orders GROUP BY priority ORDER BY priority ASC")

    # Chart 3: Delivery / Order status
    status_rows = db.execute_query("SELECT status, COUNT(*) as count FROM orders GROUP BY status")

    # Chart 4: Supplier performance
    supp_rows = db.execute_query("SELECT name, reliability_score FROM suppliers ORDER BY reliability_score DESC LIMIT 5")

    # Chart 5: Product categories
    cat_rows = db.execute_query("SELECT category, COUNT(*) as count FROM products GROUP BY category")

    return jsonify({
        "status": "success",
        "counts": counts,
        "dsa_status": {
            "linked_list": {"status": "ACTIVE", "nodes": len(dsa_service.product_linked_list)},
            "queue": {"status": f"{dsa_service.order_queue.get_size()} Pending", "size": dsa_service.order_queue.get_size()},
            "stack": {"status": f"{getattr(dsa_service, 'order_stack', None).get_size() if hasattr(dsa_service, 'order_stack') else 0} Processed", "size": getattr(dsa_service, 'order_stack', None).get_size() if hasattr(dsa_service, 'order_stack') else 0},
            "bst": {"status": "READY", "size": len(dsa_service.inventory_bst)},
            "graph": {"status": f"{len(dsa_service.network_graph.vertices)} Nodes", "nodes": len(dsa_service.network_graph.vertices)},
            "optimization": {"status": "READY", "mode": "DP & Backtracking Active"}
        },
        "charts": {
            "inventory_status": {
                "labels": ["Available Stock", "Low Stock", "Out of Stock", "Overstock"],
                "data": [avail, low, out_stock, overstock]
            },
            "orders_priority": {
                "labels": [f"Priority P{r['priority']}" for r in priority_rows],
                "data": [r["count"] for r in priority_rows]
            },
            "delivery_status": {
                "labels": [r["status"].replace("_", " ").title() for r in status_rows],
                "data": [r["count"] for r in status_rows]
            },
            "supplier_performance": {
                "labels": [r["name"] for r in supp_rows],
                "data": [float(r["reliability_score"]) for r in supp_rows]
            },
            "product_categories": {
                "labels": [r["category"] for r in cat_rows],
                "data": [r["count"] for r in cat_rows]
            }
        }
    })

@reports_bp.route("/api/reports/<string:report_type>", methods=["GET"])
def get_report_data(report_type):
    """Returns structured rows for the requested academic report."""
    rep = report_type.lower().replace("-", "_")

    if rep in ("product", "products"):
        rows = db.execute_query("""
            SELECT p.id, p.product_code, p.name, p.category, p.price, p.unit,
                   s.name as supplier_name, COALESCE(SUM(i.quantity), 0) as total_stock
            FROM products p
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            LEFT JOIN inventory i ON p.id = i.product_id
            GROUP BY p.id
            ORDER BY p.id ASC
        """)
        title = "Product Catalog & Stock Report"
        headers = ["ID", "Code", "Name", "Category", "Price", "Unit", "Supplier", "Total Stock"]

    elif rep in ("supplier", "suppliers"):
        rows = db.execute_query("""
            SELECT s.id, s.supplier_code, s.name, s.category, s.contact_person, s.email,
                   s.reliability_score, s.avg_delivery_time_days, COUNT(p.id) as products_count
            FROM suppliers s
            LEFT JOIN products p ON s.id = p.supplier_id
            GROUP BY s.id
            ORDER BY s.reliability_score DESC
        """)
        title = "Supplier Performance & Reliability Report"
        headers = ["ID", "Code", "Name", "Category", "Contact", "Email", "Reliability (%)", "Avg Delivery (Days)", "Products Count"]

    elif rep in ("inventory",):
        rows = db.execute_query("""
            SELECT i.id, p.product_code, p.name as product_name, w.name as warehouse_name,
                   i.quantity, i.reserved_quantity, i.reorder_level
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            JOIN warehouses w ON i.warehouse_id = w.id
            ORDER BY i.quantity ASC
        """)
        for r in rows:
            q = r["quantity"]
            rl = r["reorder_level"]
            r["status"] = "Out of Stock" if q <= 0 else ("Low Stock" if q <= rl else "Available")
        title = "Inventory Stock & Reorder Alert Report"
        headers = ["ID", "Product Code", "Product Name", "Warehouse", "Available Qty", "Reserved Qty", "Reorder Level", "Status"]

    elif rep in ("order", "orders"):
        rows = db.execute_query("""
            SELECT o.id, o.order_number, o.customer_name, p.name as product_name,
                   o.quantity, o.priority, o.status, l.name as delivery_hub,
                   COALESCE(w.name, 'Unassigned') as assigned_warehouse, o.created_at
            FROM orders o
            JOIN products p ON o.product_id = p.id
            JOIN delivery_locations l ON o.delivery_location_id = l.id
            LEFT JOIN warehouses w ON o.assigned_warehouse_id = w.id
            ORDER BY o.id DESC
        """)
        title = "Order Fulfillment & Dispatch Report"
        headers = ["ID", "Order Number", "Customer", "Product", "Quantity", "Priority", "Status", "Hub", "Warehouse", "Order Date"]

    elif rep in ("delivery", "deliveries", "routes"):
        rows = db.execute_query("""
            SELECT r.id, r.source_type, r.source_id, r.destination_type, r.destination_id,
                   r.distance_km, r.transit_time_hrs
            FROM routes r
            ORDER BY r.distance_km ASC
        """)
        title = "Delivery Network & Transportation Routes Report"
        headers = ["Route ID", "Source Type", "Source ID", "Dest Type", "Dest ID", "Distance (KM)", "Transit Time (Hrs)"]

    elif rep in ("algorithm", "algorithms", "algorithm_performance"):
        rows = db.execute_query("SELECT * FROM algorithm_logs ORDER BY id DESC LIMIT 100")
        title = "Algorithm Execution & Complexity Audit Report"
        headers = ["ID", "Algorithm", "Data Structure", "Input Summary", "Output Summary", "Complexity", "Steps", "Time (ms)", "Executed At"]

    else:
        # Default optimization report
        rows = db.execute_query("""
            SELECT id, algorithm_name, input_summary, output_summary, time_complexity, execution_time_ms, executed_at
            FROM algorithm_logs
            WHERE algorithm_name LIKE '%Optimization%' OR algorithm_name LIKE '%Dynamic%' OR algorithm_name LIKE '%Backtracking%'
            ORDER BY id DESC
        """)
        title = "Supply Chain Optimization Intelligence Report"
        headers = ["Log ID", "Algorithm", "Input Parameters", "Optimal Decision", "Complexity", "Time (ms)", "Executed At"]

    return jsonify({
        "status": "success",
        "report_type": rep,
        "title": title,
        "headers": headers,
        "total_rows": len(rows),
        "data": rows
    })

@reports_bp.route("/api/reports/export-csv/<string:report_type>", methods=["GET"])
def export_csv(report_type):
    """Exports any report as downloadable standard CSV."""
    rep_res = get_report_data(report_type).get_json()
    headers = rep_res.get("headers", [])
    data = rep_res.get("data", [])

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)

    for item in data:
        row = [item.get(k.lower().replace(" ", "_").replace("(", "").replace(")", ""), "") for k in headers]
        writer.writerow(row)

    csv_data = output.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=iscs_{report_type}_report.csv"}
    )
