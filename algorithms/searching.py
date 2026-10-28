"""
Intelligent Supply Chain Management System
Searching Algorithms Module
"""

import time
from typing import Any, Dict, List, Optional
from algorithms.binary_search import binary_search_records


def linear_search(records: List[Any], target: Any, key_field: str = "id") -> Dict[str, Any]:
    """Sequential search through unsorted records."""
    t0 = time.perf_counter()
    comparisons = 0
    found_rec = None
    target_str = str(target)

    for i, r in enumerate(records):
        comparisons += 1
        val_str = str(r.get(key_field, "") if isinstance(r, dict) else r)
        if val_str == target_str:
            found_rec = r
            break

    elapsed_ms = round((time.perf_counter() - t0) * 1000, 4)
    return {
        "found": found_rec is not None,
        "record": found_rec,
        "comparisons": comparisons,
        "elapsed_ms": elapsed_ms,
        "time_complexity": "O(n)"
    }


def binary_search(records: List[Any], target: Any, key_field: str = "id") -> Dict[str, Any]:
    """Divide-and-conquer binary search."""
    t0 = time.perf_counter()
    res = binary_search_records(records, key_field=key_field, target_value=target, key_type=int)
    res["elapsed_ms"] = round((time.perf_counter() - t0) * 1000, 4)
    return res
