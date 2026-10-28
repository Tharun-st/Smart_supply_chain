"""
Intelligent Supply Chain Management System
Binary Search Algorithm Implementation

Purpose:
  - Efficiently search for a specific record (Product, Supplier, etc.) in a sorted list.
  - Instead of checking one by one, it splits the list in half each time.
"""

import math

def binary_search_records(records, key_field, target_value, key_type=int):
    """
    Performs a Binary Search on a list of records sorted by the given key_field.
    """
    # Try to convert target value to the correct type (e.g., int)
    try:
        target = key_type(target_value)
    except (ValueError, TypeError):
        target = target_value

    # Helper function to get the value from a record
    def get_val(rec):
        val = rec.get(key_field, 0)
        try:
            return key_type(val)
        except (ValueError, TypeError):
            return str(val)

    # First, make sure the records are sorted by the key we are searching for
    sorted_records = sorted(records, key=get_val)
    keys_list = [get_val(r) for r in sorted_records]
    n = len(sorted_records)

    low = 0
    high = n - 1
    comparisons = 0
    steps = []
    found_record = None
    found_index = -1

    # Keep searching while the range is valid
    while low <= high:
        comparisons += 1
        mid = (low + high) // 2
        mid_record = sorted_records[mid]
        mid_val = get_val(mid_record)

        # Log the current step for the UI
        step_info = {
            "iteration": comparisons,
            "low": low,
            "high": high,
            "mid": mid,
            "mid_value": mid_val,
            "target": target,
            "visible_keys": keys_list[low:high + 1],
            "all_keys": keys_list
        }

        if mid_val == target:
            # Found the record!
            step_info["decision"] = "MATCH"
            step_info["description"] = f"Comparison #{comparisons}: Found the value {mid_val} at index {mid}."
            steps.append(step_info)
            found_record = mid_record
            found_index = mid
            break
        elif target < mid_val:
            # Target is in the left half
            step_info["decision"] = "LEFT"
            step_info["description"] = f"Comparison #{comparisons}: Target {target} is smaller than {mid_val}. Searching left half."
            steps.append(step_info)
            high = mid - 1
        else:
            # Target is in the right half
            step_info["decision"] = "RIGHT"
            step_info["description"] = f"Comparison #{comparisons}: Target {target} is larger than {mid_val}. Searching right half."
            steps.append(step_info)
            low = mid + 1

    # If we finished the loop without finding anything
    if found_record is None:
        steps.append({
            "iteration": comparisons + 1,
            "low": low,
            "high": high,
            "decision": "NOT_FOUND",
            "description": f"Searched all records but could not find value {target}.",
            "all_keys": keys_list
        })

    # Max comparisons possible for this list size
    max_theoretical = math.ceil(math.log2(n)) if n > 0 else 0

    return {
        "found": found_record is not None,
        "target": target,
        "found_index": found_index,
        "record": found_record,
        "total_records": n,
        "comparisons": comparisons,
        "max_theoretical_comparisons": max_theoretical,
        "steps": steps,
        "dataset_keys": keys_list
    }
