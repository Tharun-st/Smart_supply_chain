"""
Intelligent Supply Chain Management System
Analytics API Blueprint

Supplies executive metrics and charts data:
  1. Inventory distribution across categories and warehouses
  2. Order volume trends by priority and status
  3. Delivery performance (distance, duration, route counts)
  4. Supplier performance ratings
  5. Algorithm execution frequencies and average execution times
"""

from flask import Blueprint, jsonify, request
from models.database import db

analytics_bp = Blueprint("analytics_bp", __name__)

@analytics_bp.route("/api/analytics", methods=["GET"])
def get_analytics():
    """Aggregates all key performance indicators and chart series."""
    # 1. Product Categories distribution
    cat_rows = db.execute_query("""
        SELECT category, COUNT(*) as product_count, 
               ROUND(AVG(price), 2) as avg_price,
               SUM(price) as total_value
        FROM products
        GROUP BY category
    """)

    # 2. Inventory distribution by Warehouse
    wh_inv_rows = db.execute_query("""
        SELECT w.name as warehouse_name, w.city,
               COALESCE(SUM(i.quantity), 0) as total_units,
               w.capacity,
               ROUND((COALESCE(SUM(i.quantity), 0) * 100.0) / w.capacity, 1) as utilization_pct
        FROM warehouses w
        LEFT JOIN inventory i ON w.id = i.warehouse_id
        GROUP BY w.id
    """)

    # 3. Orders breakdown by status and priority
    orders_status = db.execute_query("""
        SELECT status, COUNT(*) as count 
        FROM orders 
        GROUP BY status
    """)

    orders_priority = db.execute_query("""
        SELECT priority, COUNT(*) as count 
        FROM orders 
        GROUP BY priority 
        ORDER BY priority ASC
    """)

    # 4. Supplier performance
    supplier_perf = db.execute_query("""
        SELECT name, category, reliability_score, avg_delivery_time_days 
        FROM suppliers 
        ORDER BY reliability_score DESC 
        LIMIT 6
    """)

    # 5. Algorithm Execution Logs summary
    algo_stats = db.execute_query("""
        SELECT algorithm_name, COUNT(*) as executions_count,
               ROUND(AVG(execution_time_ms), 3) as avg_time_ms,
               MIN(execution_time_ms) as min_time_ms,
               MAX(execution_time_ms) as max_time_ms
        FROM algorithm_logs
        GROUP BY algorithm_name
        ORDER BY executions_count DESC
    """)

    # 6. Overall Summary KPIs
    tot_products = db.execute_query("SELECT COUNT(*) as c FROM products", fetch="one")["c"]
    tot_suppliers = db.execute_query("SELECT COUNT(*) as c FROM suppliers", fetch="one")["c"]
    tot_warehouses = db.execute_query("SELECT COUNT(*) as c FROM warehouses", fetch="one")["c"]
    tot_orders = db.execute_query("SELECT COUNT(*) as c FROM orders", fetch="one")["c"]
    pending_orders = db.execute_query("SELECT COUNT(*) as c FROM orders WHERE status = 'PENDING_IN_QUEUE'", fetch="one")["c"]
    processed_orders = db.execute_query("SELECT COUNT(*) as c FROM orders WHERE status IN ('DISPATCHED', 'DELIVERED')", fetch="one")["c"]
    tot_routes = db.execute_query("SELECT COUNT(*) as c FROM routes", fetch="one")["c"]
    tot_hubs = db.execute_query("SELECT COUNT(*) as c FROM delivery_locations", fetch="one")["c"]

    return jsonify({
        "status": "success",
        "kpis": {
            "total_products": tot_products,
            "total_suppliers": tot_suppliers,
            "total_warehouses": tot_warehouses,
            "total_orders": tot_orders,
            "pending_orders": pending_orders,
            "processed_orders": processed_orders,
            "total_routes": tot_routes,
            "total_delivery_hubs": tot_hubs
        },
        "charts": {
            "categories": {
                "labels": [r["category"] for r in cat_rows],
                "counts": [r["product_count"] for r in cat_rows]
            },
            "warehouse_utilization": {
                "labels": [r["warehouse_name"] for r in wh_inv_rows],
                "utilization": [r["utilization_pct"] for r in wh_inv_rows],
                "stock": [r["total_units"] for r in wh_inv_rows]
            },
            "order_status": {
                "labels": [r["status"].replace("_", " ").title() for r in orders_status],
                "counts": [r["count"] for r in orders_status]
            },
            "order_priority": {
                "labels": [f"Priority P{r['priority']}" for r in orders_priority],
                "counts": [r["count"] for r in orders_priority]
            },
            "supplier_reliability": {
                "labels": [r["name"] for r in supplier_perf],
                "scores": [float(r["reliability_score"]) for r in supplier_perf],
                "delivery_times": [float(r["avg_delivery_time_days"]) for r in supplier_perf]
            },
            "algorithm_performance": {
                "labels": [r["algorithm_name"] for r in algo_stats],
                "times": [float(r["avg_time_ms"]) for r in algo_stats],
                "frequencies": [r["executions_count"] for r in algo_stats]
            }
        }
    })
