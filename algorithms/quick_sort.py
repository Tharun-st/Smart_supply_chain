"""
Intelligent Supply Chain Management System
Quick Sort Algorithm Implementation

Academic Data Structures & Algorithms Implementation:
- Divide-and-Conquer Recursive Partitioning
- In-place partitioning with Pivot selection (Lomuto Partition Scheme)
- Average Time Complexity: O(n log n)
- Best Time Complexity:    O(n log n)
- Worst Time Complexity:   O(n²)
- Auxiliary Space:         O(log n) call stack frames
- Real-time step telemetry: tracks pivot selections, subarray intervals, comparisons, and element swaps.
"""

import time
from typing import Any, Dict, List, Optional, Union, Callable


def _extract_sort_key(item: Any, sort_key: Optional[str] = None, key_type: Optional[type] = None) -> Any:
    """Helper to extract comparable value from a primitive or dict record."""
    if isinstance(item, dict):
        val = item.get(sort_key) if sort_key else next(iter(item.values()), 0)
    else:
        val = item

    if val is None:
        return 0

    if key_type is not None:
        try:
            return key_type(val)
        except (ValueError, TypeError):
            return val
    
    # Auto-cast numeric strings to float/int if possible
    if isinstance(val, str):
        try:
            if "." in val:
                return float(val)
            return int(val)
        except ValueError:
            return val.lower()
    return val


def quick_sort_records(
    records: List[Any],
    sort_key: Optional[str] = None,
    reverse: bool = False,
    key_type: Optional[type] = None
) -> Dict[str, Any]:
    """
    Executes Quick Sort on a list of records or primitives.
    
    Parameters:
      records  : List of dictionaries or primitive values to sort.
      sort_key : Key attribute name if records are dictionaries (e.g., 'price', 'quantity', 'id').
      reverse  : False for Ascending, True for Descending.
      key_type : Optional type casting (e.g. float, int, str).

    Returns:
      Dict containing:
        - sorted_records: The sorted list of items.
        - total_records: Count of items.
        - comparisons: Total comparisons performed.
        - swaps: Total element swaps performed.
        - elapsed_ms: Execution duration in milliseconds.
        - steps: Step-by-step trace of partitions for visualization.
        - time_complexity: Big-O analysis dictionary.
        - space_complexity: Auxiliary memory footprint.
    """
    start_time = time.perf_counter()

    if not records:
        return {
            "sorted_records": [],
            "total_records": 0,
            "comparisons": 0,
            "swaps": 0,
            "elapsed_ms": 0.0,
            "steps": [],
            "sort_key": sort_key,
            "reverse": reverse,
            "time_complexity": {"best": "O(n log n)", "average": "O(n log n)", "worst": "O(n²)"},
            "space_complexity": "O(log n)"
        }

    # Work on a shallow copy of records to keep function pure
    arr = list(records)
    n = len(arr)

    comparisons = 0
    swaps = 0
    steps: List[Dict[str, Any]] = []

    def get_key(idx: int):
        return _extract_sort_key(arr[idx], sort_key, key_type)

    def is_in_order(val1, val2):
        nonlocal comparisons
        comparisons += 1
        if reverse:
            return val1 >= val2  # Descending
        return val1 <= val2      # Ascending

    def partition(low: int, high: int, depth: int) -> int:
        nonlocal swaps
        pivot_val = get_key(high)
        pivot_item = arr[high]
        i = low - 1

        step_info = {
            "step_number": len(steps) + 1,
            "depth": depth,
            "low": low,
            "high": high,
            "pivot_index": high,
            "pivot_value": pivot_val,
            "pivot_label": str(pivot_item.get("name", pivot_val) if isinstance(pivot_item, dict) else pivot_val),
            "initial_keys": [str(get_key(k)) for k in range(low, high + 1)],
            "action": f"Partitioning range [{low}..{high}] with pivot '{pivot_val}'"
        }

        for j in range(low, high):
            curr_val = get_key(j)
            if is_in_order(curr_val, pivot_val):
                i += 1
                if i != j:
                    arr[i], arr[j] = arr[j], arr[i]
                    swaps += 1

        # Place pivot at correct position (i + 1)
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        swaps += 1
        pivot_idx = i + 1

        step_info["final_pivot_index"] = pivot_idx
        step_info["left_partition"] = [str(get_key(k)) for k in range(low, pivot_idx)]
        step_info["right_partition"] = [str(get_key(k)) for k in range(pivot_idx + 1, high + 1)]
        step_info["array_snapshot"] = [str(get_key(k)) for k in range(len(arr))]
        step_info["description"] = (
            f"Pivot '{pivot_val}' placed at index {pivot_idx}. "
            f"Left: {len(step_info['left_partition'])} items, Right: {len(step_info['right_partition'])} items."
        )
        steps.append(step_info)

        return pivot_idx

    def quick_sort_recursive(low: int, high: int, depth: int):
        if low < high:
            pi = partition(low, high, depth)
            quick_sort_recursive(low, pi - 1, depth + 1)
            quick_sort_recursive(pi + 1, high, depth + 1)

    quick_sort_recursive(0, n - 1, depth=1)

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 4)

    return {
        "sorted_records": arr,
        "total_records": n,
        "comparisons": comparisons,
        "swaps": swaps,
        "elapsed_ms": elapsed_ms,
        "steps": steps,
        "sort_key": sort_key,
        "reverse": reverse,
        "time_complexity": {
            "best": "O(n log n)",
            "average": "O(n log n)",
            "worst": "O(n²)"
        },
        "space_complexity": "O(log n)"
    }


def quick_sort(records: List[Any], sort_key: Optional[str] = None, reverse: bool = False) -> Dict[str, Any]:
    """Standard alias for quick_sort_records."""
    return quick_sort_records(records, sort_key=sort_key, reverse=reverse)
