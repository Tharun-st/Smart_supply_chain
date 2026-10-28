"""
Intelligent Supply Chain Management System
Dynamic Programming (0/1 Knapsack) Inventory Optimization
"""

import time
from typing import List, Dict, Any


def optimize_inventory_dp(warehouse_capacity: int, products: List[Dict[str, Any]], transport_cost_per_unit: float = 10.0) -> Dict[str, Any]:
    """
    0/1 Knapsack Dynamic Programming algorithm for warehouse inventory allocation.
    """
    t0 = time.perf_counter()
    n = len(products)
    W = int(warehouse_capacity)

    weights = [int(p.get("weight", p.get("id", 1)) * 5) for p in products]
    values = [int(float(p.get("price", 100))) for p in products]

    # DP Table: (n+1) x (W+1)
    dp = [[0] * (W + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        wt = weights[i - 1]
        val = values[i - 1]
        for w in range(W + 1):
            if wt <= w:
                dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - wt] + val)
            else:
                dp[i][w] = dp[i - 1][w]

    optimal_utility = dp[n][W]
    
    # Backtrack to find chosen items
    chosen_indices = []
    curr_w = W
    for i in range(n, 0, -1):
        if dp[i][curr_w] != dp[i - 1][curr_w]:
            chosen_indices.append(i - 1)
            curr_w -= weights[i - 1]

    used_capacity = W - curr_w
    utilization_pct = round((used_capacity / W) * 100, 1) if W > 0 else 0
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 3)

    return {
        "optimal_utility": optimal_utility,
        "total_allocated_products": len(chosen_indices),
        "capacity_utilization_pct": utilization_pct,
        "allocated_indices": chosen_indices,
        "elapsed_ms": elapsed_ms
    }
