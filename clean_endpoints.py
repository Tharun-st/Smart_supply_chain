import os
import re

base = r"c:\Users\tharu\OneDrive\Desktop\DS PROJECT"

def remove_between(text, start_str, end_str=None):
    if end_str is None:
        idx = text.find(start_str)
        if idx != -1:
            return text[:idx]
        return text
    
    idx1 = text.find(start_str)
    if idx1 != -1:
        idx2 = text.find(end_str, idx1 + len(start_str))
        if idx2 != -1:
            return text[:idx1] + text[idx2:]
    return text

# 1. optimization.py
p = os.path.join(base, "routes", "optimization.py")
if os.path.exists(p):
    with open(p, "r", encoding="utf-8") as f:
        content = f.read()
    content = remove_between(content, "@optimization_bp.route(\"/api/optimization/dp\"", "@optimization_bp.route(\"/api/optimization/supplier-selection\"")
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)

# 2. dsa_routes.py
p = os.path.join(base, "routes", "dsa_routes.py")
if os.path.exists(p):
    with open(p, "r", encoding="utf-8") as f:
        content = f.read()
    content = remove_between(content, "# ==================== 2. STACK ENDPOINTS ====================", "# ==================== 3. QUEUE ENDPOINTS ====================")
    content = remove_between(content, "# ==================== 4. BINARY TREE ENDPOINTS ====================", "# ==================== 5. BINARY SEARCH TREE ENDPOINTS ====================")
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)

# 3. network.py
p = os.path.join(base, "routes", "network.py")
if os.path.exists(p):
    with open(p, "r", encoding="utf-8") as f:
        content = f.read()
    content = re.sub(r'elif algorithm == "dfs":.*?result = run_dfs.*?else:', 'else:', content, flags=re.DOTALL)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)

# 4. algorithms.py
p = os.path.join(base, "routes", "algorithms.py")
if os.path.exists(p):
    with open(p, "r", encoding="utf-8") as f:
        content = f.read()
    # Remove sorting lab, comparison lab, and modify searching to only binary search
    content = remove_between(content, "# ==================== 2. SORTING LAB ====================", "# ==================== 4. COMPLEXITY ANALYZER ====================")
    content = re.sub(r'if algorithm == "binary_search":.*?result = binary_search.*?else:.*?result = linear_search.*?\n', 'result = binary_search(records, target, key_field=key_field, label_field=label_field, key_type=int)\n', content, flags=re.DOTALL)
    content = content.replace('linear_search(records, target, key_field=key_field, label_field=label_field)', 'binary_search(records, target, key_field=key_field, label_field=label_field, key_type=int)')
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)

print("Done cleaning endpoints")
