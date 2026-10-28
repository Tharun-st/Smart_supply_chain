"""
Intelligent Supply Chain Management System
Custom Linked List Implementation

Academic Data Structures and Algorithmic Problem Solving Project
Data Structure: Singly Linked List
Used for:
  - Supplier records management
  - Product records management
  - Dynamic inventory-related records

Operations Implemented:
  1. Insert (At beginning, at end, after specific key)
  2. Delete (By identifier)
  3. Update (By identifier)
  4. Search (By identifier / field predicate)
  5. Traverse / Display (With node pointers and link metadata for UI visualization)
"""

from typing import Any, Optional, Callable, List, Dict


class Node:
    """
    Represents a single node in a Singly Linked List.
    Holds a data payload and a reference pointer to the next node.
    """
    def __init__(self, data: Any):
        self.data: Any = data
        self.next: Optional['Node'] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert node data to dictionary format."""
        if hasattr(self.data, 'to_dict'):
            return self.data.to_dict()
        elif isinstance(self.data, dict):
            return self.data
        return {"value": self.data}


class LinkedList:
    """
    Singly Linked List data structure.
    Maintains a head pointer and provides O(1) head insertion,
    O(n) search, update, deletion, and linear traversal.
    """
    def __init__(self, name: str = "GenericLinkedList"):
        self.head: Optional[Node] = None
        self.size: int = 0
        self.name: str = name

    def is_empty(self) -> bool:
        """Returns True if the linked list has no nodes."""
        return self.head is None

    def insert_at_beginning(self, data: Any) -> Node:
        """
        Inserts a new node at the beginning (head) of the linked list.
        Time Complexity: O(1)
        """
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        self.size += 1
        return new_node

    def insert_at_end(self, data: Any) -> Node:
        """
        Inserts a new node at the end (tail) of the linked list.
        Time Complexity: O(n)
        """
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
            self.size += 1
            return new_node

        current = self.head
        while current.next is not None:
            current = current.next
        current.next = new_node
        self.size += 1
        return new_node

    def insert_after(self, key_func: Callable[[Any], bool], data: Any) -> bool:
        """
        Inserts a new node immediately after the first node satisfying key_func.
        Time Complexity: O(n)
        """
        current = self.head
        while current is not None:
            if key_func(current.data):
                new_node = Node(data)
                new_node.next = current.next
                current.next = new_node
                self.size += 1
                return True
            current = current.next
        return False

    def search(self, key_func: Callable[[Any], bool]) -> Optional[Node]:
        """
        Searches for the first node that satisfies key_func.
        Time Complexity: O(n)
        """
        current = self.head
        while current is not None:
            if key_func(current.data):
                return current
            current = current.next
        return None

    def search_with_steps(self, key_func: Callable[[Any], bool], id_field: str = "product_code") -> Dict[str, Any]:
        """
        Searches while recording step-by-step trace for animated UI visualization.
        """
        steps = []
        current = self.head
        comparisons = 0
        found = False
        found_node = None

        while current is not None:
            comparisons += 1
            node_data = current.to_dict()
            node_id = node_data.get(id_field, f"Node-{comparisons-1}")
            is_match = key_func(current.data)
            steps.append({
                "step": comparisons,
                "node_id": node_id,
                "label": node_data.get("name", node_id),
                "matched": is_match
            })
            if is_match:
                found = True
                found_node = node_data
                break
            current = current.next

        return {
            "found": found,
            "comparisons": comparisons,
            "steps": steps,
            "node": found_node,
            "time_complexity": "O(n)",
            "space_complexity": "O(1)"
        }

    def traverse_with_steps(self, id_field: str = "product_code") -> Dict[str, Any]:
        """
        Traverses all nodes, logging step-by-step visited order for frontend animations.
        """
        steps = []
        current = self.head
        idx = 0
        while current is not None:
            node_data = current.to_dict()
            node_id = node_data.get(id_field, f"Node-{idx}")
            steps.append({
                "step": idx + 1,
                "node_id": node_id,
                "label": node_data.get("name", node_id),
                "is_head": (idx == 0),
                "is_tail": (current.next is None)
            })
            current = current.next
            idx += 1

        return {
            "total_nodes": idx,
            "steps": steps,
            "time_complexity": "O(n)",
            "space_complexity": "O(1)"
        }

    def update(self, key_func: Callable[[Any], bool], new_data: Any) -> bool:
        """
        Updates the data of the first node matching key_func.
        Time Complexity: O(n)
        """
        target_node = self.search(key_func)
        if target_node:
            target_node.data = new_data
            return True
        return False

    def delete(self, key_func: Callable[[Any], bool]) -> bool:
        """
        Deletes the first node matching key_func from the linked list.
        Time Complexity: O(n)
        """
        if self.head is None:
            return False

        # If head node matches
        if key_func(self.head.data):
            self.head = self.head.next
            self.size -= 1
            return True

        # Traverse and find the node preceding the target node
        current = self.head
        while current.next is not None:
            if key_func(current.next.data):
                current.next = current.next.next
                self.size -= 1
                return True
            current = current.next

        return False

    def to_list(self) -> List[Any]:
        """
        Traverses the linked list and returns all data elements as a Python list.
        Time Complexity: O(n)
        """
        elements = []
        current = self.head
        while current is not None:
            elements.append(current.data)
            current = current.next
        return elements

    def to_visual_nodes(self, id_field: str = "id", label_field: str = "name") -> List[Dict[str, Any]]:
        """
        Traverses the linked list and produces structured node objects
        specifically formatted for UI Linked List visualization showing:
        Node ID, Node Label, Memory/Pointer representation, and Next pointer.
        """
        nodes = []
        current = self.head
        idx = 0
        while current is not None:
            node_data = current.to_dict()
            node_id = node_data.get(id_field, f"Node-{idx}")
            node_label = node_data.get(label_field, str(node_data))
            next_id = None
            if current.next is not None:
                next_dict = current.next.to_dict()
                next_id = next_dict.get(id_field, f"Node-{idx+1}")

            nodes.append({
                "index": idx,
                "node_id": node_id,
                "label": node_label,
                "data": node_data,
                "has_next": current.next is not None,
                "next_id": next_id
            })
            current = current.next
            idx += 1
        return nodes

    def clear(self):
        """Clears all nodes in the linked list."""
        self.head = None
        self.size = 0

    def __len__(self) -> int:
        return self.size

    def __repr__(self) -> str:
        current = self.head
        chain = []
        while current:
            chain.append(str(current.data))
            current = current.next
        return " -> ".join(chain) + " -> NULL"
