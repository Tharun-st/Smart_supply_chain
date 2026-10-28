"""
Intelligent Supply Chain Optimization System
Academic Data Structures and Algorithmic Problem Solving Project

Main Flask Application Entrypoint
"""

from flask import Flask, render_template, jsonify
from flask_cors import CORS
from config import Config

# Import Blueprints
from routes.auth import auth_bp
from routes.database_ops import database_ops_bp
from routes.suppliers import suppliers_bp
from routes.products import products_bp
from routes.inventory import inventory_bp
from routes.orders import orders_bp
from routes.warehouses import warehouses_bp
from routes.network import network_bp
from routes.algorithms import algorithms_bp
from routes.reports import reports_bp
from routes.dsa_routes import dsa_routes_bp
from routes.optimization import optimization_bp
from routes.analytics import analytics_bp
from routes.demo import demo_bp

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)

    # Enable CORS for all REST API endpoints
    CORS(app)

    # Register API Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(database_ops_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(warehouses_bp)
    app.register_blueprint(network_bp)
    app.register_blueprint(algorithms_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(dsa_routes_bp)
    app.register_blueprint(optimization_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(demo_bp)

    # ==================== HTML PAGE ROUTES ====================
    # 1. Dashboard
    @app.route("/")
    @app.route("/dashboard")
    def page_dashboard():
        return render_template("dashboard.html", active_page="dashboard", page_title="Dashboard")

    # 2. Supply Chain Core
    @app.route("/products")
    def page_products():
        return render_template("products.html", active_page="products", page_title="Products Management")

    @app.route("/suppliers")
    def page_suppliers():
        return render_template("suppliers.html", active_page="suppliers", page_title="Suppliers & Reliability")

    @app.route("/inventory")
    def page_inventory():
        return render_template("inventory.html", active_page="inventory", page_title="Inventory Management")

    @app.route("/orders")
    def page_orders():
        return render_template("orders.html", active_page="orders", page_title="Customer Orders & Queue")

    @app.route("/warehouses")
    def page_warehouses():
        return render_template("warehouses.html", active_page="warehouses", page_title="Warehouses Network")

    @app.route("/deliveries")
    @app.route("/network")
    def page_deliveries():
        return render_template("deliveries.html", active_page="deliveries", page_title="Deliveries & Routes")

    # 3. Data Structures & Operations
    @app.route("/dsa-operations")
    @app.route("/dsa")
    def page_dsa_operations():
        return render_template("dsa_operations.html", active_page="dsa_operations", page_title="DSA Operations")

    @app.route("/ds/linked-list")
    def page_ds_linked_list():
        return render_template("dsa_lab.html", active_page="ds_linked_list", tab="linked_list", page_title="Linked List Visualizer")

    @app.route("/ds/stack")
    def page_ds_stack():
        return render_template("dsa_lab.html", active_page="ds_stack", tab="stack", page_title="Stack Visualizer (LIFO)")

    @app.route("/ds/queue")
    def page_ds_queue():
        return render_template("dsa_lab.html", active_page="ds_queue", tab="queue", page_title="Queue Visualizer (FIFO)")

    @app.route("/ds/binary-tree")
    def page_ds_binary_tree():
        return render_template("dsa_lab.html", active_page="ds_binary_tree", tab="binary_tree", page_title="Binary Tree Visualizer")

    @app.route("/ds/bst")
    def page_ds_bst():
        return render_template("dsa_lab.html", active_page="ds_bst", tab="bst", page_title="Binary Search Tree (BST)")

    @app.route("/ds/graph")
    def page_ds_graph():
        return render_template("dsa_lab.html", active_page="ds_graph", tab="graph", page_title="Graph Visualizer")

    # 4. Searching & Sorting Laboratory
    @app.route("/search-sort")
    @app.route("/algorithms")
    @app.route("/search")
    def page_search_sort():
        return render_template("search.html", active_page="search", page_title="Binary Search Laboratory")

    @app.route("/algorithms/searching")
    def page_searching_lab():
        return render_template("search.html", active_page="search", page_title="Binary Search Laboratory")

    @app.route("/algorithms/sorting")
    def page_sorting_lab():
        return render_template("dsa_operations.html", active_page="dsa_operations", page_title="DSA Operations Laboratory")

    @app.route("/algorithms/bfs-dfs")
    def page_bfs_dfs():
        return render_template("dsa_lab.html", active_page="ds_graph", tab="graph", page_title="Graph & BFS Visualizer")

    @app.route("/algorithms/complexity")
    def page_complexity():
        return render_template("dsa_operations.html", active_page="dsa_operations", page_title="Complexity Analyzer")

    # 5. Supply Chain Optimization
    @app.route("/optimization")
    @app.route("/greedy")
    @app.route("/optimization/dp")
    def page_opt_dp():
        return render_template("greedy.html", active_page="optimization", page_title="Greedy Warehouse Selection")

    @app.route("/optimization/backtracking")
    def page_opt_backtracking():
        return render_template("optimization.html", active_page="optimization", tab="backtracking", page_title="Backtracking Route Optimizer")

    # 6. Database Operations (ADBMS)
    @app.route("/database-ops")
    @app.route("/adbms")
    def page_database_ops():
        return render_template("database_ops.html", active_page="database_ops", page_title="Database Operations (ADBMS)")

    # 7. Analytics, Reports, Activity Log, Settings
    @app.route("/analytics")
    def page_analytics():
        return render_template("analytics.html", active_page="analytics", page_title="Supply Chain Analytics")

    @app.route("/reports")
    def page_reports():
        return render_template("reports.html", active_page="reports", page_title="Enterprise Reports")

    @app.route("/activity-log")
    def page_activity_log():
        return render_template("activity_log.html", active_page="activity_log", page_title="Activity Timeline & Audit")

    @app.route("/settings")
    @app.route("/profile")
    def page_settings():
        return render_template("settings.html", active_page="settings", page_title="System Settings & Profile")

    @app.route("/overview")
    def page_overview():
        return render_template("overview.html", active_page="overview", page_title="Academic Project Overview")

    # Error Handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template("layout.html", error_msg="Page or endpoint not found", page_title="Page Not Found"), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"status": "error", "message": "Internal Server Error", "detail": str(e)}), 500

    return app

app = create_app()

if __name__ == "__main__":
    print("====================================================================")
    print("  INTELLIGENT SUPPLY CHAIN OPTIMIZATION SYSTEM")
    print("  Academic Data Structures & Algorithms Project")
    print("  Running on: http://127.0.0.1:5000")
    print("====================================================================")
    app.run(host="127.0.0.1", port=5000, debug=False)
