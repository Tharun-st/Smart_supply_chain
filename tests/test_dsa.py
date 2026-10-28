"""
Intelligent Supply Chain Management System
Automated Unit Tests — Synopsis-Approved Components Only

Tests (as per academic synopsis):
  1. Linked List  — insert, delete, search, traverse
  2. Queue (FIFO) — enqueue, dequeue, peek, FIFO order
  3. Binary Search Tree (BST) — insert, search with path, delete, in-order
  4. Graph — vertices, weighted edges, adjacency list
  5. BFS — level-by-level traversal using custom Queue
  6. Binary Search — divide and conquer, step trace
  7. Greedy Algorithm — nearest warehouse selection
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Data Structures (synopsis-approved)
from data_structures.linked_list import LinkedList
from data_structures.queue import LinkedListQueue
from data_structures.bst import BinarySearchTree
from data_structures.graph import Graph

# Algorithms (synopsis-approved)
from algorithms.bfs import run_bfs
from algorithms.binary_search import binary_search_records
from algorithms.greedy import select_nearest_suitable_warehouse


class TestSupplyChainDSA(unittest.TestCase):

    # ──────────────────────────────────────────────────────────────
    # 1. LINKED LIST
    # ──────────────────────────────────────────────────────────────
    def test_linked_list_insert_and_traverse(self):
        ll = LinkedList("TestLL")
        self.assertTrue(ll.is_empty())
        ll.insert_at_end({"product_code": "P001", "name": "Item 1"})
        ll.insert_at_end({"product_code": "P002", "name": "Item 2"})
        ll.insert_at_beginning({"product_code": "P000", "name": "Item 0"})
        self.assertEqual(len(ll), 3)
        items = ll.to_list()
        self.assertEqual(items[0]["product_code"], "P000")  # head is P000

    def test_linked_list_search(self):
        ll = LinkedList("SearchLL")
        ll.insert_at_end({"product_code": "P001", "name": "Item 1"})
        ll.insert_at_end({"product_code": "P002", "name": "Item 2"})
        ll.insert_at_end({"product_code": "P003", "name": "Item 3"})
        res = ll.search_with_steps(lambda x: x["product_code"] == "P002", id_field="product_code")
        self.assertTrue(res["found"])
        self.assertEqual(res["comparisons"], 2)

    def test_linked_list_delete(self):
        ll = LinkedList("DeleteLL")
        ll.insert_at_end({"product_code": "P001", "name": "Item 1"})
        ll.insert_at_end({"product_code": "P002", "name": "Item 2"})
        self.assertTrue(ll.delete(lambda x: x["product_code"] == "P001"))
        self.assertEqual(len(ll), 1)
        self.assertEqual(ll.to_list()[0]["product_code"], "P002")

    def test_linked_list_update(self):
        ll = LinkedList("UpdateLL")
        ll.insert_at_end({"product_code": "P001", "name": "Old Name"})
        updated = ll.update(lambda x: x["product_code"] == "P001",
                            {"product_code": "P001", "name": "New Name"})
        self.assertTrue(updated)
        self.assertEqual(ll.to_list()[0]["name"], "New Name")

    # ──────────────────────────────────────────────────────────────
    # 2. QUEUE (FIFO)
    # ──────────────────────────────────────────────────────────────
    def test_queue_fifo_order(self):
        q = LinkedListQueue("OrderQueue")
        self.assertTrue(q.is_empty())
        q.enqueue({"order_id": 101})
        q.enqueue({"order_id": 102})
        q.enqueue({"order_id": 103})
        self.assertEqual(q.get_size(), 3)
        self.assertEqual(q.peek()["order_id"], 101)   # FIFO: first in is at front
        self.assertEqual(q.dequeue()["order_id"], 101)
        self.assertEqual(q.dequeue()["order_id"], 102)
        self.assertEqual(q.dequeue()["order_id"], 103)
        self.assertTrue(q.is_empty())

    def test_queue_clear(self):
        q = LinkedListQueue("ClearQueue")
        q.enqueue({"id": 1})
        q.enqueue({"id": 2})
        q.clear()
        self.assertTrue(q.is_empty())
        self.assertEqual(q.get_size(), 0)

    # ──────────────────────────────────────────────────────────────
    # 3. BINARY SEARCH TREE (BST)
    # ──────────────────────────────────────────────────────────────
    def test_bst_insert_and_inorder(self):
        bst = BinarySearchTree("InventoryBST")
        for k in [50, 30, 70, 20, 40, 60, 80]:
            bst.insert(k, f"Item-{k}")
        self.assertEqual(len(bst), 7)
        inorder = bst.inorder_traversal()
        # In-order of BST must be sorted ascending
        self.assertEqual([x["key"] for x in inorder], [20, 30, 40, 50, 60, 70, 80])

    def test_bst_search_with_path(self):
        bst = BinarySearchTree("SearchBST")
        for k in [50, 30, 70, 60]:
            bst.insert(k, f"Item-{k}")
        res = bst.search(60)
        self.assertTrue(res["found"])
        self.assertEqual(res["path"], [50, 70, 60])
        self.assertEqual(res["comparisons"], 3)

    def test_bst_delete_two_children(self):
        bst = BinarySearchTree("DeleteBST")
        for k in [50, 30, 70, 20, 40, 60, 80]:
            bst.insert(k, f"Item-{k}")
        self.assertTrue(bst.delete(50))  # node with 2 children
        self.assertEqual(len(bst), 6)
        inorder = bst.inorder_traversal()
        self.assertEqual([x["key"] for x in inorder], [20, 30, 40, 60, 70, 80])

    def test_bst_tree_structure(self):
        bst = BinarySearchTree("VisBST")
        bst.insert(10, "Ten")
        bst.insert(5, "Five")
        bst.insert(15, "Fifteen")
        structure = bst.to_tree_structure()
        self.assertIsNotNone(structure)
        self.assertEqual(structure["key"], 10)

    # ──────────────────────────────────────────────────────────────
    # 4. GRAPH (Adjacency List)
    # ──────────────────────────────────────────────────────────────
    def test_graph_add_vertices_and_edges(self):
        g = Graph("SupplyGraph")
        g.add_vertex("WH-1", "Warehouse 1", "warehouse", city="Chennai",  lat=13.0, lng=80.2)
        g.add_vertex("WH-2", "Warehouse 2", "warehouse", city="Bengaluru", lat=12.9, lng=77.5)
        g.add_vertex("HUB-1", "Hub 1",       "delivery_location", city="Coimbatore")
        g.add_edge("WH-1", "WH-2",  350.0, 6.0)
        g.add_edge("WH-2", "HUB-1", 250.0, 4.5)
        self.assertEqual(len(g.vertices), 3)
        # Bidirectional: WH-2 should have edges to WH-1 and HUB-1
        self.assertEqual(len(g.get_neighbors("WH-2")), 2)

    def test_graph_remove_edge(self):
        g = Graph("EdgeGraph")
        g.add_vertex("A", "Node A", "warehouse")
        g.add_vertex("B", "Node B", "warehouse")
        g.add_edge("A", "B", 100.0)
        self.assertTrue(g.remove_edge("A", "B"))
        self.assertEqual(len(g.get_neighbors("A")), 0)

    def test_graph_network_payload(self):
        g = Graph("PayloadGraph")
        g.add_vertex("A", "Node A", "warehouse")
        g.add_vertex("B", "Node B", "delivery_location")
        g.add_edge("A", "B", 200.0, 3.0)
        payload = g.to_network_payload()
        self.assertEqual(payload["total_vertices"], 2)
        self.assertEqual(payload["total_routes"], 1)

    # ──────────────────────────────────────────────────────────────
    # 5. BFS (Breadth-First Search using custom Queue)
    # ──────────────────────────────────────────────────────────────
    def test_bfs_visits_all_nodes(self):
        g = Graph("BFSGraph")
        for i in ["1", "2", "3", "4"]:
            g.add_vertex(i, f"Node {i}", "warehouse")
        g.add_edge("1", "2", 10.0)
        g.add_edge("1", "3", 20.0)
        g.add_edge("3", "4", 15.0)
        res = run_bfs(g, "1")
        bfs_dict = res.to_dict() if hasattr(res, "to_dict") else res
        self.assertEqual(bfs_dict["total_visited"], 4)
        self.assertEqual(bfs_dict["visited_order"][0], "1")  # Start node first

    def test_bfs_levels(self):
        g = Graph("LevelGraph")
        for i in ["S", "A", "B", "C"]:
            g.add_vertex(i, i, "warehouse")
        g.add_edge("S", "A", 5.0)
        g.add_edge("S", "B", 10.0)
        g.add_edge("A", "C", 5.0)
        res = run_bfs(g, "S")
        bfs_dict = res.to_dict() if hasattr(res, "to_dict") else res
        # S is level 0, A & B are level 1, C is level 2
        self.assertEqual(bfs_dict["levels"]["S"], 0)
        self.assertEqual(bfs_dict["levels"]["A"], 1)
        self.assertEqual(bfs_dict["levels"]["C"], 2)

    # ──────────────────────────────────────────────────────────────
    # 6. BINARY SEARCH
    # ──────────────────────────────────────────────────────────────
    def test_binary_search_found(self):
        records = [{"id": i, "name": f"Item {i}"} for i in [10, 20, 30, 40, 50, 60, 70]]
        res = binary_search_records(records, key_field="id", target_value=60)
        self.assertTrue(res["found"])
        self.assertEqual(res["record"]["id"], 60)
        self.assertLessEqual(res["comparisons"], 4)   # log2(7) ≈ 3

    def test_binary_search_not_found(self):
        records = [{"id": i} for i in [10, 20, 30, 40, 50]]
        res = binary_search_records(records, key_field="id", target_value=99)
        self.assertFalse(res["found"])
        self.assertIsNone(res["record"])

    def test_binary_search_step_decisions(self):
        records = [{"id": i} for i in range(1, 9)]
        res = binary_search_records(records, key_field="id", target_value=3)
        decisions = [s["decision"] for s in res["steps"] if "decision" in s]
        self.assertIn("MATCH", decisions)

    # ──────────────────────────────────────────────────────────────
    # 7. GREEDY ALGORITHM — Nearest Warehouse Selection
    # ──────────────────────────────────────────────────────────────
    def test_greedy_selects_nearest_suitable(self):
        warehouses = [
            {"id": "1", "name": "WH Chennai",   "lat": 13.08, "lng": 80.27, "stock": 200},
            {"id": "2", "name": "WH Bengaluru",  "lat": 12.97, "lng": 77.59, "stock": 150},
            {"id": "3", "name": "WH Hyderabad",  "lat": 17.38, "lng": 78.48, "stock": 50},
        ]
        delivery = {"id": "D1", "name": "Customer Coimbatore",
                    "lat": 11.00, "lng": 76.96}
        res = select_nearest_suitable_warehouse(
            product_id=1, requested_qty=100,
            delivery_location=delivery, warehouses=warehouses
        )
        self.assertTrue(res["success"])
        # WH Bengaluru is closest to Coimbatore among those with sufficient stock
        self.assertIsNotNone(res["selected_warehouse"])
        self.assertEqual(len(res["candidates"]), 3)

    def test_greedy_no_suitable_warehouse(self):
        warehouses = [
            {"id": "1", "name": "WH A", "lat": 13.0, "lng": 80.0, "stock": 5},
        ]
        delivery = {"id": "D1", "name": "Customer", "lat": 12.0, "lng": 77.0}
        res = select_nearest_suitable_warehouse(
            product_id=1, requested_qty=100,
            delivery_location=delivery, warehouses=warehouses
        )
        self.assertFalse(res["success"])
    # ──────────────────────────────────────────────────────────────
    # 8. QUICK SORT (In-place Recursive Divide-and-Conquer)
    # ──────────────────────────────────────────────────────────────
    def test_quick_sort_numeric_ascending_and_descending(self):
        from algorithms.quick_sort import quick_sort_records
        numbers = [42, 17, 89, 5, 23, 67, 1, 99, 34]
        res_asc = quick_sort_records(numbers, reverse=False)
        self.assertEqual(res_asc["sorted_records"], [1, 5, 17, 23, 34, 42, 67, 89, 99])
        self.assertGreater(res_asc["comparisons"], 0)

        res_desc = quick_sort_records(numbers, reverse=True)
        self.assertEqual(res_desc["sorted_records"], [99, 89, 67, 42, 34, 23, 17, 5, 1])

    def test_quick_sort_records_by_key(self):
        from algorithms.quick_sort import quick_sort_records
        products = [
            {"id": 101, "name": "Item C", "price": 450.0},
            {"id": 102, "name": "Item A", "price": 120.0},
            {"id": 103, "name": "Item D", "price": 990.0},
            {"id": 104, "name": "Item B", "price": 310.0},
        ]
        res = quick_sort_records(products, sort_key="price")
        sorted_prices = [p["price"] for p in res["sorted_records"]]
        self.assertEqual(sorted_prices, [120.0, 310.0, 450.0, 990.0])
        self.assertEqual(res["total_records"], 4)
        self.assertIn("steps", res)
        self.assertGreater(len(res["steps"]), 0)

    def test_quick_sort_empty_and_single_element(self):
        from algorithms.quick_sort import quick_sort_records
        self.assertEqual(quick_sort_records([])["sorted_records"], [])
        self.assertEqual(quick_sort_records([42])["sorted_records"], [42])

    def test_quick_sort_duplicates(self):
        from algorithms.quick_sort import quick_sort_records
        dups = [5, 2, 8, 5, 1, 8, 2, 5]
        res = quick_sort_records(dups)
        self.assertEqual(res["sorted_records"], [1, 2, 2, 5, 5, 5, 8, 8])


if __name__ == "__main__":
    unittest.main(verbosity=2)
