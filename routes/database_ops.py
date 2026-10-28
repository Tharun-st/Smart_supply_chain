"""
Intelligent Supply Chain Management System
ADBMS Database Operations API Blueprint

Demonstrates Advanced Database Management Systems (ADBMS) principles:
  - SELECT: Parametric queries with search, dynamic filtering, sorting, and pagination
  - INSERT: Record insertion with primary key generation and foreign key constraints
  - UPDATE: Targeted row updates by primary key
  - DELETE: Foreign key cascade awareness and constraint enforcement
  - Primary Key / Foreign Key schema relationship inspection
"""

from flask import Blueprint, jsonify, request
from models.database import db
import time

database_ops_bp = Blueprint("database_ops_bp", __name__)

TABLE_SCHEMAS = {
    "suppliers": {
        "title": "Suppliers Master Table",
        "pk": "id",
        "columns": ["id", "supplier_code", "name", "contact_person", "email", "phone", "category", "reliability_score", "avg_delivery_time_days", "status"],
        "foreign_keys": [],
        "editable": ["name", "contact_person", "email", "phone", "category", "reliability_score", "avg_delivery_time_days", "status"]
    },
    "warehouses": {
        "title": "Warehouses Master Table",
        "pk": "id",
        "columns": ["id", "warehouse_code", "name", "location", "city", "capacity", "lat", "lng"],
        "foreign_keys": [],
        "editable": ["name", "location", "city", "capacity", "lat", "lng"]
    },
    "products": {
        "title": "Products Catalog Table",
        "pk": "id",
        "columns": ["id", "product_code", "name", "category", "supplier_id", "price", "unit"],
        "foreign_keys": [
            {"column": "supplier_id", "ref_table": "suppliers", "ref_col": "id"}
        ],
        "editable": ["name", "category", "supplier_id", "price", "unit"]
    },
    "inventory": {
        "title": "Inventory Stock Bridge Table",
        "pk": "id",
        "columns": ["id", "product_id", "warehouse_id", "quantity", "reserved_quantity", "reorder_level"],
        "foreign_keys": [
            {"column": "product_id", "ref_table": "products", "ref_col": "id"},
            {"column": "warehouse_id", "ref_table": "warehouses", "ref_col": "id"}
        ],
        "editable": ["quantity", "reserved_quantity", "reorder_level"]
    },
    "orders": {
        "title": "Customer Orders Table",
        "pk": "id",
        "columns": ["id", "order_number", "customer_name", "product_id", "quantity", "priority", "delivery_location_id", "status", "assigned_warehouse_id"],
        "foreign_keys": [
            {"column": "product_id", "ref_table": "products", "ref_col": "id"},
            {"column": "delivery_location_id", "ref_table": "delivery_locations", "ref_col": "id"},
            {"column": "assigned_warehouse_id", "ref_table": "warehouses", "ref_col": "id"}
        ],
        "editable": ["customer_name", "quantity", "priority", "status", "assigned_warehouse_id"]
    },
    "delivery_locations": {
        "title": "Delivery Locations Table",
        "pk": "id",
        "columns": ["id", "hub_code", "name", "city", "state", "pin_code", "lat", "lng"],
        "foreign_keys": [],
        "editable": ["name", "city", "state", "pin_code"]
    }
}

@database_ops_bp.route("/api/database/tables", methods=["GET"])
def get_tables_overview():
    """Returns overview of all relational tables, column metadata, PKs, FKs, and row counts."""
    tables_info = []
    for table_name, schema in TABLE_SCHEMAS.items():
        try:
            cnt_row = db.execute_query(f"SELECT COUNT(*) as total FROM {table_name}", fetch="one")
            row_count = cnt_row["total"] if cnt_row else 0
        except Exception:
            row_count = 0

        tables_info.append({
            "table_name": table_name,
            "title": schema["title"],
            "primary_key": schema["pk"],
            "columns": schema["columns"],
            "foreign_keys": schema["foreign_keys"],
            "row_count": row_count
        })

    return jsonify({
        "status": "success",
        "database_engine": db.engine.upper(),
        "total_tables": len(tables_info),
        "tables": tables_info,
        "relationships": [
            {"from": "products.supplier_id", "to": "suppliers.id", "type": "Many-to-One (M:1)"},
            {"from": "inventory.product_id", "to": "products.id", "type": "Many-to-One (M:1)"},
            {"from": "inventory.warehouse_id", "to": "warehouses.id", "type": "Many-to-One (M:1)"},
            {"from": "orders.product_id", "to": "products.id", "type": "Many-to-One (M:1)"},
            {"from": "orders.delivery_location_id", "to": "delivery_locations.id", "type": "Many-to-One (M:1)"},
            {"from": "orders.assigned_warehouse_id", "to": "warehouses.id", "type": "Many-to-One (M:1)"}
        ]
    })

@database_ops_bp.route("/api/database/query", methods=["GET"])
def execute_select():
    """
    Demonstrates ADBMS SELECT with parameterization, search, filtering, and sorting.
    """
    table = request.args.get("table", "products").lower()
    if table not in TABLE_SCHEMAS:
        return jsonify({"status": "error", "message": f"Table '{table}' does not exist."}), 400

    search = request.args.get("search", "").strip()
    sort_col = request.args.get("sort_by", "id")
    sort_dir = "DESC" if request.args.get("order", "").upper() == "DESC" else "ASC"
    limit = int(request.args.get("limit", 50))

    schema = TABLE_SCHEMAS[table]
    if sort_col not in schema["columns"]:
        sort_col = schema["pk"]

    start_time = time.perf_counter()
    params = []
    where_clauses = []

    if search:
        # Search text columns
        text_cols = [c for c in schema["columns"] if "name" in c or "code" in c or "category" in c or "city" in c or "status" in c]
        if text_cols:
            clause = " OR ".join([f"{c} LIKE %s" for c in text_cols])
            where_clauses.append(f"({clause})")
            for _ in text_cols:
                params.append(f"%{search}%")

    sql = f"SELECT * FROM {table}"
    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)
    sql += f" ORDER BY {sort_col} {sort_dir} LIMIT {limit}"

    try:
        rows = db.execute_query(sql, tuple(params), fetch="all")
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 3)

        return jsonify({
            "status": "success",
            "operation": "SELECT",
            "table": table,
            "executed_sql": sql.replace("%s", "'?'") if db.engine == "mysql" else sql.replace("?", "'?'"),
            "columns": schema["columns"],
            "primary_key": schema["pk"],
            "foreign_keys": schema["foreign_keys"],
            "total_rows": len(rows),
            "execution_time_ms": elapsed_ms,
            "data": rows
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@database_ops_bp.route("/api/database/insert", methods=["POST"])
def execute_insert():
    """
    Demonstrates ADBMS INSERT with parameterized query and FK validation.
    """
    data = request.get_json() or {}
    table = data.get("table", "").lower()
    fields = data.get("fields", {})

    if table not in TABLE_SCHEMAS:
        return jsonify({"status": "error", "message": f"Invalid table '{table}'"}), 400

    schema = TABLE_SCHEMAS[table]
    valid_cols = [k for k in fields.keys() if k in schema["columns"] and k != schema["pk"]]
    if not valid_cols:
        return jsonify({"status": "error", "message": "No valid column values provided."}), 400

    col_names = ", ".join(valid_cols)
    placeholders = ", ".join(["%s" for _ in valid_cols])
    values = tuple(fields[c] for c in valid_cols)

    sql = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"

    try:
        new_id = db.execute_query(sql, values, fetch="insert")
        return jsonify({
            "status": "success",
            "operation": "INSERT",
            "table": table,
            "new_id": new_id,
            "message": f"Record inserted successfully into {table} with Primary Key ID #{new_id}."
        }), 201
    except Exception as e:
        return jsonify({"status": "error", "message": f"Insert failed: {str(e)}"}), 500

@database_ops_bp.route("/api/database/update/<table_name>/<int:record_id>", methods=["PUT"])
def execute_update(table_name, record_id):
    """
    Demonstrates ADBMS UPDATE by Primary Key.
    """
    table = table_name.lower()
    if table not in TABLE_SCHEMAS:
        return jsonify({"status": "error", "message": f"Invalid table '{table}'"}), 400

    data = request.get_json() or {}
    fields = data.get("fields", {})
    schema = TABLE_SCHEMAS[table]

    valid_cols = [k for k in fields.keys() if k in schema["editable"]]
    if not valid_cols:
        return jsonify({"status": "error", "message": "No editable fields provided."}), 400

    set_clause = ", ".join([f"{c} = %s" for c in valid_cols])
    values = list(fields[c] for c in valid_cols)
    values.append(record_id)

    sql = f"UPDATE {table} SET {set_clause} WHERE {schema['pk']} = %s"

    try:
        db.execute_query(sql, tuple(values), fetch="none")
        return jsonify({
            "status": "success",
            "operation": "UPDATE",
            "table": table,
            "record_id": record_id,
            "message": f"Record #{record_id} in '{table}' updated successfully."
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"Update failed: {str(e)}"}), 500

@database_ops_bp.route("/api/database/delete/<table_name>/<int:record_id>", methods=["DELETE"])
def execute_delete(table_name, record_id):
    """
    Demonstrates ADBMS DELETE with constraint awareness.
    """
    table = table_name.lower()
    if table not in TABLE_SCHEMAS:
        return jsonify({"status": "error", "message": f"Invalid table '{table}'"}), 400

    schema = TABLE_SCHEMAS[table]
    pk_col = schema["pk"]

    # Check child dependencies before deleting parent
    if table == "suppliers":
        child_count = db.execute_query("SELECT COUNT(*) as cnt FROM products WHERE supplier_id = %s", (record_id,), fetch="one")
        if child_count and child_count.get("cnt", 0) > 0:
            return jsonify({
                "status": "error",
                "message": f"Foreign Key Constraint: Cannot delete Supplier #{record_id} because {child_count['cnt']} product(s) reference it."
            }), 400
    elif table == "products":
        inv_count = db.execute_query("SELECT COUNT(*) as cnt FROM inventory WHERE product_id = %s", (record_id,), fetch="one")
        if inv_count and inv_count.get("cnt", 0) > 0:
            return jsonify({
                "status": "error",
                "message": f"Foreign Key Constraint: Cannot delete Product #{record_id} because active inventory exists."
            }), 400

    sql = f"DELETE FROM {table} WHERE {pk_col} = %s"
    try:
        db.execute_query(sql, (record_id,), fetch="none")
        return jsonify({
            "status": "success",
            "operation": "DELETE",
            "table": table,
            "record_id": record_id,
            "message": f"Record #{record_id} deleted successfully from '{table}'."
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"Delete failed: {str(e)}"}), 500
