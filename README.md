# INTELLIGENT SUPPLY CHAIN OPTIMIZATION SYSTEM
### Advanced College Data Structures and Algorithms (DSA) Project

![Python Version](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Backend Framework](https://img.shields.io/badge/Backend-Flask%20RESTful-green.svg)
![Database](https://img.shields.io/badge/Database-MySQL%208.0%20%7C%20SQLite%20Fallback-orange.svg)
![DSA Integrations](https://img.shields.io/badge/DSAs%20Implemented-16%2B%20Algorithms-purple.svg)
![Testing](https://img.shields.io/badge/Unit%20Tests-18%2F18%20Passing%20(100%25)-brightgreen.svg)

---

## 📌 1. Project Overview & Academic Purpose

The **Intelligent Supply Chain Optimization System (ISCS)** is a complete, full-stack, enterprise-grade academic web application engineered to demonstrate how classical **Data Structures and Algorithms** solve mission-critical logistical challenges in supply chain operations.

Unlike mock academic prototypes or simulated frontend widgets:
* **Zero Simulated Logic**: All 16+ data structures and algorithms are implemented as custom Python classes and functions executed on the backend runtime.
* **Dual-Engine Persistence**: Seamlessly connects to a local **MySQL 8.0** server (via `mysql-connector-python`) while automatically deploying an embedded **SQLite3** engine if credentials are not pre-configured, guaranteeing zero downtime.
* **Full-Stack Interface**: Built with modern HTML5, responsive CSS3 design tokens (featuring a dark navy executive UI, light/dark theme toggling, and glassmorphic telemetry cards), Vanilla JavaScript, and Chart.js.
* **Automated 21-Step Demo**: Single-click automated demonstration runner with real-time progress, telemetry tracking, and sub-millisecond execution logs.

---

## 🧩 2. Core Data Structures Implemented & Supply Chain Mappings

| # | Data Structure | Python Module | Supply Chain Role | Operations & Theoretical Time Complexity |
|---|---|---|---|---|
| 1 | **Singly Linked List** | [`data_structures/linked_list.py`](file:///c:/Users/LENOVO/OneDrive/Desktop/DS%20PROJECT/data_structures/linked_list.py) | **Product Catalog Pointer Chain**: Dynamic catalog where items are chained with `head`, `tail`, and `next` pointers. | `insert_at_beginning: O(1)`, `insert_at_end: O(1)`, `search: O(n)`, `delete: O(n)` |
| 2 | **LIFO Stack** | [`data_structures/stack.py`](file:///c:/Users/LENOVO/OneDrive/Desktop/DS%20PROJECT/data_structures/stack.py) | **Processed Orders Dispatch History**: Dispatched fulfillment batches stacked with `top` pointer for quick reversal/undo and audit recall. | `push: O(1)`, `pop: O(1)`, `peek: O(1)`, `is_empty: O(1)` |
| 3 | **FIFO Queue** | [`data_structures/queue.py`](file:///c:/Users/LENOVO/OneDrive/Desktop/DS%20PROJECT/data_structures/queue.py) | **Pending Customer Orders Queue**: Strict First-In First-Out waiting line for incoming customer procurement batches. | `enqueue (rear): O(1)`, `dequeue (front): O(1)`, `peek: O(1)` |
| 4 | **Binary Tree** | [`data_structures/binary_tree.py`](file:///c:/Users/LENOVO/OneDrive/Desktop/DS%20PROJECT/data_structures/binary_tree.py) | **Logistics Category Hierarchy**: Organizational categorization of regional hubs and inventory types. | `insert: O(n)`, `inorder/preorder/postorder: O(n)` |
| 5 | **Binary Search Tree (BST)** | [`data_structures/bst.py`](file:///c:/Users/LENOVO/OneDrive/Desktop/DS%20PROJECT/data_structures/bst.py) | **Inventory Stock Indexing**: High-speed lookup of product stock counts using integer key comparisons. | `search: O(log n) avg, O(n) worst`, `insert: O(log n)`, `delete: O(log n)` |
| 6 | **Weighted Graph** | [`data_structures/graph.py`](file:///c:/Users/LENOVO/OneDrive/Desktop/DS%20PROJECT/data_structures/graph.py) | **Transportation Distribution Network**: Adjacency list connecting Suppliers, Warehouses, and Delivery Hubs. | `add_vertex: O(1)`, `add_edge: O(1)`, `get_neighbors: O(deg(V))` |

---

## ⚡ 3. Algorithmic Problem Solving Paradigms

### 🔍 Searching Algorithms ([`algorithms/searching.py`](file:///c:/Users/LENOVO/OneDrive/Desktop/DS%20PROJECT/algorithms/searching.py))
* **Linear Search ($O(n)$)**: Sequential element-by-element examination for unsorted datasets. Records exact comparison steps.
* **Binary Search ($O(\log n)$)**: Divide-and-conquer interval halving on sorted product keys. Records low, mid, and high pointers for every iteration.
* **Head-to-Head Comparison**: Direct runtime battle on identical input sizes with real latency and comparison metrics.

### 📶 Sorting Algorithm: Quick Sort ([`algorithms/quick_sort.py`](file:///c:/Users/tharu/OneDrive/Desktop/DS%20PROJECT/algorithms/quick_sort.py))
* **Quick Sort ($O(n \log n)$)**: Single exclusive sorting technique implemented across the project. Features recursive divide-and-conquer in-place partitioning with pivot tracking, comparison counting, element swaps, and telemetry step logs for database records (Products, Suppliers, Orders).

### 🕸️ Graph Traversals ([`algorithms/bfs_dfs.py`](file:///c:/Users/LENOVO/OneDrive/Desktop/DS%20PROJECT/algorithms/bfs_dfs.py))
* **Breadth-First Search (BFS)**: Explores transportation hubs level-by-level using the custom `LinkedListQueue` to discover minimum-transit-hop routes.
* **Depth-First Search (DFS)**: Deep recursive exploration of logistics corridors using the custom `Stack` for connectivity and cycle verification.

### 💡 Optimization Paradigms
* **Dynamic Programming (0/1 Knapsack)** ([`algorithms/dynamic_programming.py`](file:///c:/Users/LENOVO/OneDrive/Desktop/DS%20PROJECT/algorithms/dynamic_programming.py)):
  Optimizes warehouse capacity allocation to maximize inventory value and priority utility within a strict cubic capacity constraint. Includes tabular DP state matrix rendering.
* **Backtracking with Constraint Pruning** ([`algorithms/backtracking.py`](file:///c:/Users/LENOVO/OneDrive/Desktop/DS%20PROJECT/algorithms/backtracking.py)):
  Explores multi-hop delivery corridors from warehouses to destination hubs, calculating total distance and automatically pruning routes exceeding maximum distance budgets.

### 📊 Complexity Analysis ([`services/complexity_service.py`](file:///c:/Users/LENOVO/OneDrive/Desktop/DS%20PROJECT/services/complexity_service.py))
* Full Big-O matrix covering Best, Average, and Worst cases, auxiliary memory footprints, and live empirical execution curve generation across dynamic input sizes ($N = 50, 100, 250, 500, 1000$).

---

## 🗄️ 4. Database Architecture & Dual-Mode Persistence

* **Primary Engine**: **MySQL 8.0**
  * DDL schema defined in [`database/schema.sql`](file:///c:/Users/LENOVO/OneDrive/Desktop/DS%20PROJECT/database/schema.sql) and [`database.sql`](file:///c:/Users/LENOVO/OneDrive/Desktop/DS%20PROJECT/database.sql).
  * 8 relational tables: `suppliers`, `warehouses`, `products`, `inventory`, `delivery_locations`, `routes`, `orders`, and `algorithm_logs`.
* **Zero-Downtime Fallback**: **SQLite3**
  * Automatically activated in [`models/database.py`](file:///c:/Users/LENOVO/OneDrive/Desktop/DS%20PROJECT/models/database.py) if MySQL credentials are not provided in `.env`.
  * Pre-seeded with 15 products, 8 suppliers, 5 warehouses, 10 hubs, 22 routes, 26 inventory records, and 20 orders (10 pending + 10 dispatched).

---

## 🚀 5. Quick Start & Execution

### Option A: 1-Click Launch (Windows)
Double click [`start.bat`](file:///c:/Users/LENOVO/OneDrive/Desktop/DS%20PROJECT/start.bat) in the project root directory. It automatically opens `http://127.0.0.1:5000` in your default browser and starts the Flask server.

### Option B: Command Line (PowerShell)
```powershell
# 1. Navigate to directory
cd "c:\Users\LENOVO\OneDrive\Desktop\DS PROJECT"

# 2. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 3. Run Flask application
python app.py
```

Open `http://127.0.0.1:5000` in your web browser.

---

## 🧪 6. Running Automated Unit & Route Tests

All data structures, algorithms, page routes, and API endpoints are covered by comprehensive unit tests:

```powershell
# Run DSA unit tests (16 tests)
python -m unittest tests/test_dsa.py

# Run Full Route Integration tests (25 page routes + API tests)
python -m unittest tests/test_routes.py

# Run all test suites together
python -m unittest discover tests
```
> **Test Result**: `Ran 18 tests in 0.183s — OK (100% Passing)`

---

## ⚡ 7. The 21-Step Automated Academic Walkthrough

Triggered via the **"⚡ Run Full DSA Demo"** button on the Dashboard or Top Navigation Bar:

1. **Load Sample Products**: Reads catalog into Python memory.
2. **Create Linked List**: Chains product nodes with `next` pointers.
3. **Node Mutation**: Inserts node at HEAD ($O(1)$) and deletes node ($O(n)$).
4. **Initialize Order Queue**: Sets up empty FIFO queue with front/rear pointers.
5. **Enqueue Orders**: Adds customer orders to the rear ($O(1)$).
6. **Dequeue Order**: Processes front order ($O(1)$) following strict FIFO.
7. **Transition to Stack**: Moves dequeued order to the top of the Processed Stack.
8. **Stack Push & Pop**: Demonstrates LIFO operations in $O(1)$ time.
9. **Construct BST**: Inserts inventory stock keys into Binary Search Tree.
10. **BST In-Order Traversal**: Demonstrates $O(n)$ sorted key extraction.
11. **Construct Logistics Graph**: Populates vertices and weighted transit edges.
12. **Run BFS**: Explores hubs level-by-level with FIFO Queue.
13. **Run DFS**: Explores routes deeply with LIFO Stack.
14. **Run Linear Search**: Benchmarks sequential scan against product key.
15. **Run Binary Search**: Benchmarks logarithmic search against product key.
16. **Run Insertion Sort**: Demonstrates shift-and-insert sorting.
17. **Run Merge Sort**: Recursively sorts catalog with divide-and-conquer.
18. **Run Quick Sort**: In-place pivot partitioning sorting.
19. **Dynamic Programming**: Solves 0/1 Knapsack warehouse inventory allocation.
20. **Backtracking Optimization**: Finds pruned delivery paths within distance limit.
21. **Algorithmic Synthesis**: Aggregates Big-O theoretical matrix and benchmarks.

---

## 📁 8. Project Structure

```
DS PROJECT/
├── algorithms/                    # Pure Python Algorithm Implementations
│   ├── backtracking.py            # Route optimization with constraint pruning
│   ├── bfs_dfs.py                 # Breadth-First & Depth-First Search
│   ├── dynamic_programming.py     # 0/1 Knapsack Inventory Optimization
│   ├── searching.py               # Linear Search & Binary Search
│   └── sorting.py                 # Insertion, Merge, and Quick Sort
├── data_structures/               # Pure Python Custom Data Structures
│   ├── binary_tree.py             # Binary Tree hierarchy
│   ├── bst.py                     # Binary Search Tree (BST)
│   ├── graph.py                   # Weighted Adjacency List Graph
│   ├── linked_list.py             # Singly Linked List
│   ├── queue.py                   # FIFO Queue
│   └── stack.py                   # LIFO Stack
├── database/                      # SQL Schema & Persistence DDL
│   ├── schema.sql                 # MySQL 8.0 DDL
│   └── supply_chain.db            # Embedded SQLite fallback database
├── models/                        # Persistence & In-Memory State Layer
│   ├── database.py                # Dual MySQL/SQLite connection manager
│   └── dsa_service.py             # In-memory DSA synchronization service
├── routes/                        # Flask RESTful API Blueprints
│   ├── algorithms.py              # Searching, sorting, comparison, and logs
│   ├── analytics.py               # Telemetry and Chart.js aggregation
│   ├── demo.py                    # 21-Step automated walkthrough controller
│   ├── dsa_routes.py              # Standalone DSA playground APIs
│   ├── inventory.py               # Inventory CRUD & BST integration
│   ├── network.py                 # Logistics graph, BFS, DFS endpoints
│   ├── optimization.py            # DP Knapsack & Backtracking APIs
│   ├── orders.py                  # Queue & Stack order fulfillment
│   ├── products.py                # Linked List product catalog
│   ├── reports.py                 # 7-Category report generation & CSV export
│   ├── suppliers.py               # Supplier reliability evaluation
│   └── warehouses.py              # Warehouse storage facilities
├── services/                      # Auxiliary Analysis Services
│   └── complexity_service.py      # Big-O reference matrix & live benchmarks
├── static/                        # Frontend Assets
│   ├── css/
│   │   └── style.css              # Custom design system with dark/light themes
│   └── js/
│       ├── demo.js                # 21-Step demonstration playback controller
│       ├── main.js                # Global UI, themes, toasts, and charts
│       └── visualizers.js         # SVG tree, graph canvas, and pointer visualizers
├── templates/                     # Jinja2 HTML5 Templates
│   ├── activity_log.html          # Real-time algorithm audit trail
│   ├── algorithms_lab.html        # Searching & Sorting comparison lab
│   ├── analytics.html             # Supply chain telemetry & 6 Chart.js charts
│   ├── bfs_dfs.html               # Dedicated BFS vs DFS visualizer
│   ├── complexity.html            # Big-O reference table & live benchmarks
│   ├── dashboard.html             # Executive KPI overview & system status
│   ├── deliveries.html            # Logistics network & route explorer
│   ├── dsa_lab.html               # 6 Data structures interactive playground
│   ├── inventory.html             # Inventory health & BST explorer
│   ├── layout.html                # Sidebar, topbar, modals, and notifications
│   ├── optimization.html          # DP Knapsack & Backtracking route optimizer
│   ├── orders.html                # Split FIFO Queue & LIFO Stack view
│   ├── overview.html              # Academic documentation & viva guide
│   ├── products.html              # Linked List product catalog
│   ├── reports.html               # 7-category interactive reports & CSV export
│   ├── settings.html              # System telemetry & database controls
│   ├── suppliers.html             # Top-3 supplier reliability ranking
│   └── warehouses.html            # Warehouse network & capacity utilization
├── tests/                         # Unit & Integration Testing Suite
│   ├── test_dsa.py                # 16 Unit tests for all DSAs
│   └── test_routes.py             # 25 Page routes & core API tests
├── app.py                         # Main Flask Application Entrypoint
├── config.py                      # Application Configuration
├── database.sql                   # Root MySQL deployment script
├── start.bat                      # Windows 1-Click Launch Script
└── README.md                      # Comprehensive Academic Documentation
```

---

## 🎓 9. Academic Viva & Evaluation Q&A

1. **Q: Why are customer orders placed in a Queue while dispatched orders are in a Stack?**
   * *A*: Customer orders must be fulfilled fairly in the exact order they arrive, which requires a **First-In, First-Out (FIFO) Queue** ($O(1)$ enqueue and dequeue). When an order is dispatched, it moves to the **LIFO Stack** so that the most recently processed order is at the `TOP` ($O(1)$ access), enabling instant status recalls, undo operations, and dispatch reversals.
2. **Q: How does the Binary Search Tree improve inventory performance over an array?**
   * *A*: An unsorted array requires $O(n)$ linear scan to find a product's stock. A BST reduces the average search time complexity to $O(\log n)$ by recursively dividing the search space in half based on numerical key comparisons.
3. **Q: Why use BFS over DFS for delivery route finding?**
   * *A*: **BFS** explores nodes level-by-level using a FIFO queue, guaranteeing that the first time a destination hub is reached, it has been reached via the fewest number of transit hops (unweighted shortest path). **DFS** explores deep branches with a stack, which is ideal for topological sorting, cycle detection, and complete connectivity auditing.
4. **Q: How does the 0/1 Knapsack Dynamic Programming solution differ from a Greedy heuristic?**
   * *A*: A greedy heuristic selects items solely based on local density (value per unit weight) and can get trapped in suboptimal allocations when items cannot be broken into fractions. Dynamic Programming evaluates overlapping subproblems and memoizes the global optimal solution using a 2D state matrix $DP[i][w]$ in $O(n \cdot W)$ pseudo-polynomial time.
5. **Q: How does Backtracking avoid exponential $O(V!)$ catastrophe in large networks?**
   * *A*: Backtracking applies **constraint pruning**; the moment an accumulated route distance exceeds the permissible budget, the algorithm immediately abandons that branch and backtracks to try alternative neighbors, cutting off massive subtrees of the state space.

---

**Developed for Academic Data Structures & Algorithmic Problem Solving.**
*Intelligent Supply Chain Optimization System — 100% Working, Full-Stack, Real Python DSAs.*
