"""
Intelligent Supply Chain Management System
DSA Integration & Synchronization Service

Maintains in-memory custom Python data structure instances synchronized with the database
(as per academic synopsis scope):
  1. supplier_linked_list : LinkedList           (Supplier records)
  2. product_linked_list  : LinkedList           (Product records)
  3. order_queue          : LinkedListQueue FIFO (Customer order processing)
  4. inventory_bst        : BinarySearchTree     (Inventory indexed by ID)
  5. network_graph        : Graph (Adj. List)    (Warehouses, Suppliers, Hubs & Routes)
"""

from data_structures.linked_list import LinkedList
from data_structures.queue import LinkedListQueue
from data_structures.stack import Stack
from data_structures.bst import BinarySearchTree
from data_structures.graph import Graph
from models.database import db
from typing import Dict, Any, List, Optional
import time

class DSAService:
    _instance = None

    def __init__(self):
        # In-memory data structures
        self.supplier_linked_list = LinkedList(name="SuppliersLinkedList")
        self.product_linked_list = LinkedList(name="ProductsLinkedList")
        self.order_queue = LinkedListQueue(name="OrdersFIFOQueue")
        self.order_stack = Stack(name="ProcessedOrderStack")
        self.inventory_bst = BinarySearchTree(name="InventoryBST")
        self.network_graph = Graph(name="LogisticsNetworkGraph")

        self.reload_all_from_db()

    def sync_all_from_database(self):
        """Synchronizes all in-memory Python structures from DB."""
        self.reload_all_from_db()

    def reload_all_from_db(self):
        """Loads and builds all custom data structures from the database."""
        self._load_suppliers()
        self._load_products()
        self._load_orders_queue()
        self._load_inventory_bst()
        self._load_network_graph()

    # ==================== 1. SUPPLIERS (LINKED LIST) ====================
    def _load_suppliers(self):
        self.supplier_linked_list.clear()
        suppliers = db.execute_query("SELECT * FROM suppliers ORDER BY id ASC")
        for s in suppliers:
            p_res = db.execute_query("SELECT COUNT(*) as cnt FROM products WHERE supplier_id = %s", (s["id"],), fetch="one")
            s["products_count"] = p_res["cnt"] if p_res else 0
            self.supplier_linked_list.insert_at_end(s)

    def add_supplier(self, data: Dict[str, Any]) -> Dict[str, Any]:
        code = data.get("supplier_code", f"SUP-{int(time.time())%1000:03d}")
        supplier_id = db.execute_query(
            """INSERT INTO suppliers (supplier_code, name, contact_person, email, phone, address, category)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (code, data["name"], data.get("contact_person", ""), data.get("email", ""),
             data.get("phone", ""), data.get("address", ""), data.get("category", "General")),
            fetch="insert"
        )
        data["id"] = supplier_id
        data["supplier_code"] = code
        data["products_count"] = 0
        self.supplier_linked_list.insert_at_end(data)
        return data

    def update_supplier(self, supplier_id: int, data: Dict[str, Any]) -> bool:
        db.execute_query(
            """UPDATE suppliers SET name = %s, contact_person = %s, email = %s, phone = %s, address = %s, category = %s
               WHERE id = %s""",
            (data["name"], data.get("contact_person", ""), data.get("email", ""),
             data.get("phone", ""), data.get("address", ""), data.get("category", "General"), supplier_id),
            fetch="none"
        )
        return self.supplier_linked_list.update(lambda s: s["id"] == supplier_id, data)

    def delete_supplier(self, supplier_id: int) -> bool:
        db.execute_query("DELETE FROM suppliers WHERE id = %s", (supplier_id,), fetch="none")
        return self.supplier_linked_list.delete(lambda s: s["id"] == supplier_id)

    # ==================== 2. PRODUCTS (LINKED LIST) ====================
    def _load_products(self):
        self.product_linked_list.clear()
        products = db.execute_query("""
            SELECT p.*, s.name as supplier_name,
                   COALESCE(SUM(i.quantity), 0) as total_stock
            FROM products p
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            LEFT JOIN inventory i ON p.id = i.product_id
            GROUP BY p.id
            ORDER BY p.id ASC
        """)
        for p in products:
            self.product_linked_list.insert_at_end(p)

    def add_product(self, data: Dict[str, Any]) -> Dict[str, Any]:
        code = data.get("product_code", f"PRD-{int(time.time())%1000:03d}")
        product_id = db.execute_query(
            """INSERT INTO products (product_code, name, category, supplier_id, price, unit)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (code, data["name"], data.get("category", "General"), data.get("supplier_id"),
             float(data.get("price", 0.0)), data.get("unit", "units")),
            fetch="insert"
        )
        data["id"] = product_id
        data["product_code"] = code
        data["total_stock"] = 0
        if data.get("supplier_id"):
            s_row = db.execute_query("SELECT name FROM suppliers WHERE id = %s", (data["supplier_id"],), fetch="one")
            data["supplier_name"] = s_row["name"] if s_row else "Unknown"
        else:
            data["supplier_name"] = "None"
        self.product_linked_list.insert_at_end(data)
        return data

    def delete_product(self, product_id: int) -> bool:
        db.execute_query("DELETE FROM products WHERE id = %s", (product_id,), fetch="none")
        self.product_linked_list.delete(lambda p: p["id"] == product_id)
        self.inventory_bst.delete(product_id)
        return True

    # ==================== 3. ORDERS QUEUE (FIFO) ====================
    def _load_orders_queue(self):
        self.order_queue.clear()
        self.order_stack.clear()
        pending_orders = db.execute_query("""
            SELECT o.*, p.name as product_name, p.price as unit_price,
                   l.name as location_name, l.city as destination_city
            FROM orders o
            JOIN products p ON o.product_id = p.id
            JOIN delivery_locations l ON o.delivery_location_id = l.id
            WHERE o.status = 'PENDING_IN_QUEUE'
            ORDER BY o.id ASC
        """)
        for o in pending_orders:
            self.order_queue.enqueue(o)

        dispatched_orders = db.execute_query("""
            SELECT o.*, p.name as product_name, p.product_code, p.price as unit_price,
                   l.name as location_name, l.city as destination_city,
                   w.name as warehouse_name
            FROM orders o
            JOIN products p ON o.product_id = p.id
            JOIN delivery_locations l ON o.delivery_location_id = l.id
            LEFT JOIN warehouses w ON o.assigned_warehouse_id = w.id
            WHERE o.status != 'PENDING_IN_QUEUE'
            ORDER BY o.id ASC
        """)
        for o in (dispatched_orders or []):
            self.order_stack.push(o)

    def enqueue_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        order_num = f"ORD-{int(time.time()) % 100000:05d}"
        queue_pos = self.order_queue.get_size() + 1
        order_id = db.execute_query(
            """INSERT INTO orders (order_number, customer_name, customer_phone, customer_email,
                                  product_id, quantity, delivery_location_id, status, queue_position)
               VALUES (%s, %s, %s, %s, %s, %s, %s, 'PENDING_IN_QUEUE', %s)""",
            (order_num, order_data["customer_name"], order_data.get("customer_phone", ""),
             order_data.get("customer_email", ""), order_data["product_id"],
             order_data["quantity"], order_data["delivery_location_id"], queue_pos),
            fetch="insert"
        )
        enriched = db.execute_query("""
            SELECT o.*, p.name as product_name, p.price as unit_price,
                   l.name as location_name, l.city as destination_city
            FROM orders o
            JOIN products p ON o.product_id = p.id
            JOIN delivery_locations l ON o.delivery_location_id = l.id
            WHERE o.id = %s
        """, (order_id,), fetch="one")

        self.order_queue.enqueue(enriched)
        return enriched

    def dequeue_order(self) -> Optional[Dict[str, Any]]:
        if self.order_queue.is_empty():
            return None
        return self.order_queue.dequeue()

    # ==================== 4. INVENTORY (BINARY SEARCH TREE) ====================
    def _load_inventory_bst(self):
        self.inventory_bst.clear()
        inventory_records = db.execute_query("""
            SELECT i.*, p.name as product_name, p.product_code, p.category, p.price,
                   w.name as warehouse_name, w.location as warehouse_location
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            JOIN warehouses w ON i.warehouse_id = w.id
            ORDER BY i.id ASC
        """)
        for inv in inventory_records:
            self.inventory_bst.insert(key=inv["id"], data=inv)

    def insert_inventory(self, data: Dict[str, Any]) -> Dict[str, Any]:
        inv_id = db.execute_query(
            """INSERT INTO inventory (product_id, warehouse_id, quantity, reorder_level)
               VALUES (%s, %s, %s, %s)""",
            (data["product_id"], data["warehouse_id"], data.get("quantity", 0), data.get("reorder_level", 50)),
            fetch="insert"
        )
        enriched = db.execute_query("""
            SELECT i.*, p.name as product_name, p.product_code, p.category, p.price,
                   w.name as warehouse_name, w.location as warehouse_location
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            JOIN warehouses w ON i.warehouse_id = w.id
            WHERE i.id = %s
        """, (inv_id,), fetch="one")
        self.inventory_bst.insert(key=inv_id, data=enriched)
        self._load_products()
        return enriched

    def update_stock(self, inventory_id: int, new_quantity: int) -> bool:
        db.execute_query("UPDATE inventory SET quantity = %s WHERE id = %s", (new_quantity, inventory_id), fetch="none")
        node_res = self.inventory_bst.search(inventory_id)
        if node_res and node_res["found"]:
            curr_data = node_res["data"]["data"]
            curr_data["quantity"] = new_quantity
            self.inventory_bst.insert(inventory_id, curr_data)
        self._load_products()
        return True

    def delete_inventory(self, inventory_id: int) -> bool:
        db.execute_query("DELETE FROM inventory WHERE id = %s", (inventory_id,), fetch="none")
        self.inventory_bst.delete(inventory_id)
        self._load_products()
        return True

    # ==================== 5. DELIVERY NETWORK (GRAPH) ====================
    def _load_network_graph(self):
        self.network_graph.clear()
        warehouses = db.execute_query("SELECT * FROM warehouses")
        for w in warehouses:
            self.network_graph.add_vertex(
                node_id=f"WH-{w['id']}",
                name=w["name"],
                node_type="warehouse",
                city=w["city"],
                lat=w["lat"],
                lng=w["lng"]
            )
        suppliers = db.execute_query("SELECT * FROM suppliers")
        for s in suppliers:
            self.network_graph.add_vertex(
                node_id=f"SUP-{s['id']}",
                name=s["name"],
                node_type="supplier",
                city=s.get("category", "Supplier")
            )
        locations = db.execute_query("SELECT * FROM delivery_locations")
        for l in locations:
            self.network_graph.add_vertex(
                node_id=f"HUB-{l['id']}",
                name=l["name"],
                node_type="delivery_location",
                city=l["city"],
                lat=l["lat"],
                lng=l["lng"]
            )
        routes = db.execute_query("SELECT * FROM routes")
        for r in routes:
            prefix_map = {"warehouse": "WH-", "supplier": "SUP-", "delivery_location": "HUB-"}
            src = f"{prefix_map.get(r['source_type'], 'WH-')}{r['source_id']}"
            dst = f"{prefix_map.get(r['destination_type'], 'HUB-')}{r['destination_id']}"
            self.network_graph.add_edge(src, dst, r["distance_km"], r["transit_time_hrs"])

# Global DSA service instance
dsa_service = DSAService()
