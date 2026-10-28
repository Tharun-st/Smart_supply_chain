"""
Intelligent Supply Chain Management System
Greedy Algorithm: Nearest Suitable Warehouse Selection

Purpose:
  - Find the best warehouse to fulfill an order.
  - The "Greedy" part is choosing the warehouse that is closest (local best choice)
    while making sure it has enough stock.
"""

import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculates distance between two points in km."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def select_nearest_suitable_warehouse(product_id, requested_qty, delivery_location, warehouses, routes_map=None, cost_per_km=18.0, base_handling_fee=150.0):
    """
    Uses a Greedy approach to select the nearest warehouse with enough stock.
    """
    routes_map = routes_map or {}
    dest_id = str(delivery_location.get("id", ""))
    dest_name = delivery_location.get("name", "Customer Location")
    dest_lat = float(delivery_location.get("lat", 0.0))
    dest_lng = float(delivery_location.get("lng", 0.0))

    all_candidates = []
    eligible_warehouses = []

    steps = []

    # Step 1: Check which warehouses have enough stock (Feasibility)
    steps.append({
        "step_number": 1,
        "step_name": "Stock Check",
        "description": f"Checking all warehouses for product {product_id}. Need at least {requested_qty} units."
    })

    for wh in warehouses:
        wh_id = str(wh.get("id", wh.get("warehouse_id", "")))
        wh_name = wh.get("name", f"Warehouse {wh_id}")
        wh_stock = int(wh.get("stock", wh.get("quantity", 0)))
        wh_lat = float(wh.get("lat", 0.0))
        wh_lng = float(wh.get("lng", 0.0))

        # Determine distance (check map first, then calculate coordinates)
        if (wh_id, dest_id) in routes_map:
            dist = routes_map[(wh_id, dest_id)]
        elif (dest_id, wh_id) in routes_map:
            dist = routes_map[(dest_id, wh_id)]
        else:
            dist = calculate_distance(wh_lat, wh_lng, dest_lat, dest_lng)

        cost = round(base_handling_fee + (dist * cost_per_km), 2)

        # A warehouse is suitable only if it has enough stock
        is_suitable = wh_stock >= requested_qty

        info = {
            "warehouse_id": wh_id,
            "warehouse_name": wh_name,
            "stock": wh_stock,
            "is_suitable": is_suitable,
            "distance_km": dist,
            "estimated_cost": cost
        }

        all_candidates.append(info)
        if is_suitable:
            eligible_warehouses.append(info)

    # Step 2: Comparison
    steps.append({
        "step_number": 2,
        "step_name": "Distance Calculation",
        "description": f"Found {len(eligible_warehouses)} warehouses with enough stock. Now finding the closest one."
    })

    if not eligible_warehouses:
        msg = "No warehouse has enough stock for this order."
        steps.append({"step_number": 3, "step_name": "Failed", "description": msg})
        return {
            "success": False,
            "selected_warehouse": None,
            "candidates": all_candidates,
            "decision_summary": msg,
            "steps": steps
        }

    # Step 3: Greedy Choice - Pick the warehouse with the minimum distance
    # We sort by distance and pick the first one (the shortest)
    eligible_warehouses.sort(key=lambda x: x["distance_km"])
    best_wh = eligible_warehouses[0]

    steps.append({
        "step_number": 3,
        "step_name": "Greedy Selection",
        "description": f"Greedy Choice: Picked {best_wh['warehouse_name']} because it is the closest ({best_wh['distance_km']} km)."
    })

    # Final Summary
    summary = (f"Selected {best_wh['warehouse_name']} (Distance: {best_wh['distance_km']} km, "
               f"Cost: ₹{best_wh['estimated_cost']}) as it is the nearest suitable facility.")

    steps.append({"step_number": 4, "step_name": "Final Decision", "description": summary})

    return {
        "success": True,
        "selected_warehouse": best_wh,
        "candidates": all_candidates,
        "eligible_candidates": eligible_warehouses,
        "decision_summary": summary,
        "steps": steps
    }
