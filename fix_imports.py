import os
import re

files_to_patch = [
    "tests/test_dsa.py",
    "services/complexity_service.py",
    "routes/algorithms.py",
    "routes/dsa_routes.py",
    "routes/network.py",
    "routes/optimization.py",
    "routes/demo.py",
    "models/dsa_service.py"
]

patterns_to_remove = [
    r"from data_structures\.stack import Stack",
    r"from data_structures\.binary_tree import BinaryTree",
    r"from algorithms\.searching import linear_search, binary_search",
    r"from algorithms\.searching import linear_search",
    r"from algorithms\.searching import binary_search",
    r"from algorithms\.sorting import insertion_sort, merge_sort, quick_sort",
    r"from algorithms\.sorting import insertion_sort, merge_sort, quick_sort, bubble_sort",
    r"from algorithms\.sorting import insertion_sort",
    r"from algorithms\.sorting import merge_sort",
    r"from algorithms\.sorting import quick_sort",
    r"from algorithms\.bfs_dfs import run_bfs, run_dfs",
    r"from algorithms\.dynamic_programming import optimize_inventory_dp",
    r"from algorithms\.backtracking import optimize_delivery_route_backtracking"
]

for filepath in files_to_patch:
    full_path = os.path.join(r"c:\Users\tharu\OneDrive\Desktop\DS PROJECT", filepath)
    if not os.path.exists(full_path):
        continue
    with open(full_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        match = False
        for pattern in patterns_to_remove:
            if re.search(pattern, line):
                match = True
                break
        if not match:
            new_lines.append(line)
            
    with open(full_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
