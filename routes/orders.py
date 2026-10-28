"""
Intelligent Supply Chain Management System
Orders API Blueprint

Data Structures Demonstrated:
  - Custom FIFO Queue (Pending Orders: Enqueue, Dequeue, Peek)
  - Custom LIFO Stack (Processed Orders: Push, Pop, Peek)
Badges: [Queue - FIFO] [Stack - LIFO]
"""

from flask import Blueprint, jsonify, request
from models.dsa_service import dsa_service
from models.database import db
import time

orders_bp = Blueprint("orders_bp", __name__)

@orders_bp.route("/api/orders", methods=["GET"])
def get_orders():
    """
    Returns all orders plus the live visual state of both the
    Pending Orders FIFO Queue and the Processed Orders LIFO Stack.
    """
    all_orders = db.execute_query("""
        SELECT o.*, p.name as product_name, p.product_code, p.price as unit_price,
               l.name as location_name, l.city as destination_city,
               w.name as warehouse_name
        FROM orders o
        JOIN products p ON o.product_id = p.id
        JOIN delivery_locations l ON o.delivery_location_id = l.id
        LEFT JOIN warehouses w ON o.assigned_warehouse_id = w.id
        ORDER BY o.id DESC
    """)

    queue_visual = dsa_service.order_queue.to_visual_queue(id_field="id", label_field="order_number")
    stack_visual = dsa_service.order_stack.to_visual_stack(id_field="id", label_field="order_number")

    return jsonify({
        "status": "success",
        "data_structures": {
            "queue": "FIFO Queue (Customer Orders Pending)",
            "stack": "LIFO Stack (Processed Orders History)"
        },
        "queue_size": dsa_service.order_queue.get_size(),
        "queue_visualization": queue_visual,
        "queue_peek": dsa_service.order_queue.peek(),
        "stack_size": dsa_service.order_stack.get_size(),
        "stack_visualization": stack_visual,
        "stack_peek": dsa_service.order_stack.peek(),
        "orders": all_orders,
        "explanation": "Pending orders wait in a strict First-In, First-Out (FIFO) Linked List Queue. When processed, they transition into a Last-In, First-Out (LIFO) Stack representing the most recent dispatch history."
    })

# ==================== FIFO QUEUE OPERATIONS ====================
@orders_bp.route("/api/orders", methods=["POST"])
def enqueue_order():
    """Places a new customer order and Enqueues it at the rear of the FIFO Queue (O(1))."""
    data = request.get_json() or {}
    customer_name = data.get("customer_name")
    product_id = data.get("product_id")
    quantity = data.get("quantity")
    delivery_location_id = data.get("delivery_location_id", 1)
    priority = data.get("priority", 1)

    if not customer_name or not product_id or not quantity:
        return jsonify({"status": "error", "message": "Customer Name, Product, and Quantity are required"}), 400

    try:
        qty = int(quantity)
        if qty <= 0:
            return jsonify({"status": "error", "message": "Quantity must be greater than zero"}), 400

        order_data = {
            "customer_name": customer_name,
            "customer_phone": data.get("customer_phone", ""),
            "customer_email": data.get("customer_email", ""),
            "product_id": int(product_id),
            "quantity": qty,
            "priority": int(priority),
            "delivery_location_id": int(delivery_location_id)
        }

        new_order = dsa_service.enqueue_order(order_data)
        queue_visual = dsa_service.order_queue.to_visual_queue(id_field="id", label_field="order_number")

        return jsonify({
            "status": "success",
            "message": f"Order #{new_order['order_number']} enqueued at position {dsa_service.order_queue.get_size()} (O(1) rear enqueue)",
            "order": new_order,
            "queue_size": dsa_service.order_queue.get_size(),
            "queue_visualization": queue_visual
        }), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@orders_bp.route("/api/orders/dequeue", methods=["POST"])
def dequeue_order():
    """
    Dequeues the oldest pending order from the FRONT of the FIFO Queue,
    updates its status to DISPATCHED in database, and Pushes it onto the Processed Orders Stack!
    """
    if dsa_service.order_queue.is_empty():
        return jsonify({
            "status": "error",
            "message": "Queue Underflow: The order queue is empty. No pending orders to process."
        }), 400

    start_time = time.perf_counter()

    # 1. Dequeue from FIFO Queue (O(1))
    order = dsa_service.dequeue_order()
    order_id = order["id"]

    # 2. Select warehouse via Greedy nearest or default warehouse
    wh_stock = db.execute_query("""
        SELECT w.id, w.name, COALESCE(i.quantity, 0) as stock
        FROM warehouses w
        LEFT JOIN inventory i ON w.id = i.warehouse_id AND i.product_id = %s
        WHERE COALESCE(i.quantity, 0) >= %s
        LIMIT 1
    """, (order["product_id"], order["quantity"]), fetch="one")

    assigned_wh_id = wh_stock["id"] if wh_stock else 1
    assigned_wh_name = wh_stock["name"] if wh_stock else "Default Hub"

    # 3. Update status in database
    db.execute_query("""
        UPDATE orders 
        SET status = 'DISPATCHED', assigned_warehouse_id = %s, processed_at = CURRENT_TIMESTAMP
        WHERE id = %s
    """, (assigned_wh_id, order_id), fetch="none")

    # Deduct stock if warehouse found
    if wh_stock:
        db.execute_query("""
            UPDATE inventory 
            SET quantity = quantity - %s 
            WHERE warehouse_id = %s AND product_id = %s
        """, (order["quantity"], assigned_wh_id, order["product_id"]), fetch="none")
        dsa_service._load_inventory_bst()

    order["status"] = "DISPATCHED"
    order["warehouse_name"] = assigned_wh_name

    # 4. Push onto LIFO Stack (O(1))
    dsa_service.push_processed_order(order)

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 4)

    return jsonify({
        "status": "success",
        "message": f"Order #{order.get('order_number')} dequeued from Queue (FIFO) and pushed onto Processed Stack (LIFO)",
        "processed_order": order,
        "elapsed_ms": elapsed_ms,
        "queue_size": dsa_service.order_queue.get_size(),
        "queue_visualization": dsa_service.order_queue.to_visual_queue(id_field="id", label_field="order_number"),
        "stack_size": dsa_service.order_stack.get_size(),
        "stack_visualization": dsa_service.order_stack.to_visual_stack(id_field="id", label_field="order_number")
    })

@orders_bp.route("/api/orders/peek", methods=["GET"])
def peek_order_queue():
    """Inspects front of queue without removing it (O(1))."""
    front = dsa_service.order_queue.peek()
    if front:
        return jsonify({"status": "success", "front_order": front, "is_empty": False})
    return jsonify({"status": "success", "front_order": None, "is_empty": True})

# ==================== LIFO STACK OPERATIONS ====================
@orders_bp.route("/api/orders/stack", methods=["GET"])
def get_order_stack():
    """Returns visual representation of processed orders stack."""
    return jsonify({
        "status": "success",
        "data_structure": "LIFO Stack (Processed Orders)",
        "stack_size": dsa_service.order_stack.get_size(),
        "stack_visualization": dsa_service.order_stack.to_visual_stack(id_field="id", label_field="order_number"),
        "top_item": dsa_service.order_stack.peek()
    })

@orders_bp.route("/api/orders/stack/push", methods=["POST"])
def push_order_stack():
    """Manually pushes an order onto the processed orders stack (O(1))."""
    data = request.get_json() or {}
    order_id = data.get("order_id")
    if not order_id:
        return jsonify({"status": "error", "message": "Order ID is required"}), 400

    order = db.execute_query("SELECT * FROM orders WHERE id = %s", (int(order_id),), fetch="one")
    if not order:
        return jsonify({"status": "error", "message": "Order not found"}), 404

    dsa_service.push_processed_order(order)
    return jsonify({
        "status": "success",
        "message": f"Order #{order['order_number']} pushed onto Stack (O(1) Top)",
        "stack_visualization": dsa_service.order_stack.to_visual_stack(id_field="id", label_field="order_number")
    })

@orders_bp.route("/api/orders/stack/pop", methods=["POST"])
def pop_order_stack():
    """Pops the most recently processed order from the top of the stack (O(1))."""
    if dsa_service.order_stack.is_empty():
        return jsonify({"status": "error", "message": "Stack Underflow: The processed orders stack is empty."}), 400

    popped = dsa_service.pop_processed_order()
    return jsonify({
        "status": "success",
        "message": f"Order #{popped.get('order_number')} popped from TOP of stack (O(1))",
        "popped_item": popped,
        "stack_size": dsa_service.order_stack.get_size(),
        "stack_visualization": dsa_service.order_stack.to_visual_stack(id_field="id", label_field="order_number")
    })

@orders_bp.route("/api/orders/stack/peek", methods=["GET"])
def peek_order_stack():
    """Peeks at top of processed orders stack."""
    top = dsa_service.order_stack.peek()
    if top:
        return jsonify({"status": "success", "top_order": top, "is_empty": False})
    return jsonify({"status": "success", "top_order": None, "is_empty": True})
