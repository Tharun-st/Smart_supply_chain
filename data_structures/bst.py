"""
Intelligent Supply Chain Management System
Custom Binary Search Tree (BST) Implementation

Academic Data Structures and Algorithmic Problem Solving Project
Data Structure: Binary Search Tree
Used for:
  - Inventory and product records indexing and rapid search
  - Keyed by numeric Product ID or Inventory ID

Operations Implemented:
  1. Insert(key, data) -> O(log n) avg, O(n) worst
  2. Search(key) -> O(log n) avg, O(n) worst
  3. Delete(key) -> O(log n) avg (handles 0, 1, and 2 children via in-order successor)
  4. In-order Traversal (L-Root-R: produces naturally sorted keys)
  5. Pre-order and Post-order Traversals
  6. to_tree_structure() (Serializes tree with hierarchy, depth, and positions for UI SVG/Canvas rendering)
"""

from typing import Any, Optional, List, Dict


class BSTNode:
    """
    Represents a single node in the Binary Search Tree.
    """
    def __init__(self, key: int, data: Any):
        self.key: int = key
        self.data: Any = data
        self.left: Optional['BSTNode'] = None
        self.right: Optional['BSTNode'] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "data": self.data if isinstance(self.data, dict) else (self.data.to_dict() if hasattr(self.data, 'to_dict') else str(self.data))
        }


class BinarySearchTree:
    """
    Custom Binary Search Tree implementation with full recursive operations
    and detailed operation step tracking for academic demonstration.
    """
    def __init__(self, name: str = "InventoryBST"):
        self.root: Optional[BSTNode] = None
        self.size: int = 0
        self.name: str = name

    def is_empty(self) -> bool:
        return self.root is None

    # ==================== INSERT ====================
    def insert(self, key: int, data: Any) -> bool:
        """
        Inserts a new key and associated data into the BST.
        Returns True if inserted, False if key already exists (updates data).
        """
        if self.root is None:
            self.root = BSTNode(key, data)
            self.size += 1
            return True

        return self._insert_recursive(self.root, key, data)

    def _insert_recursive(self, current: BSTNode, key: int, data: Any) -> bool:
        if key == current.key:
            # Duplicate key: update existing node's data
            current.data = data
            return False
        elif key < current.key:
            if current.left is None:
                current.left = BSTNode(key, data)
                self.size += 1
                return True
            else:
                return self._insert_recursive(current.left, key, data)
        else:
            if current.right is None:
                current.right = BSTNode(key, data)
                self.size += 1
                return True
            else:
                return self._insert_recursive(current.right, key, data)

    # ==================== SEARCH ====================
    def search(self, key: int) -> Optional[Dict[str, Any]]:
        """
        Searches for a key in the BST.
        Returns a dict containing the node data and the traversal path of visited keys.
        """
        path = []
        node = self._search_recursive(self.root, key, path)
        if node:
            return {
                "found": True,
                "key": node.key,
                "data": node.to_dict(),
                "path": path,
                "comparisons": len(path)
            }
        return {
            "found": False,
            "key": key,
            "data": None,
            "path": path,
            "comparisons": len(path)
        }

    def _search_recursive(self, current: Optional[BSTNode], key: int, path: List[int]) -> Optional[BSTNode]:
        if current is None:
            return None
        path.append(current.key)
        if key == current.key:
            return current
        elif key < current.key:
            return self._search_recursive(current.left, key, path)
        else:
            return self._search_recursive(current.right, key, path)

    # ==================== DELETE ====================
    def delete(self, key: int) -> bool:
        """
        Deletes a node with the given key from the BST.
        Handles three cases:
          Case 1: Leaf node (0 children) -> Simple removal
          Case 2: One child -> Replace with child
          Case 3: Two children -> Find in-order successor (min node in right subtree), copy, and delete successor
        """
        initial_size = self.size
        self.root = self._delete_recursive(self.root, key)
        return self.size < initial_size

    def _delete_recursive(self, current: Optional[BSTNode], key: int) -> Optional[BSTNode]:
        if current is None:
            return None

        if key < current.key:
            current.left = self._delete_recursive(current.left, key)
        elif key > current.key:
            current.right = self._delete_recursive(current.right, key)
        else:
            # Node found!
            self.size -= 1
            # Case 1 & 2: 0 or 1 child
            if current.left is None:
                return current.right
            elif current.right is None:
                return current.left

            # Case 3: 2 children
            # Find in-order successor (smallest in right subtree)
            successor = self._find_min(current.right)
            current.key = successor.key
            current.data = successor.data
            # Delete in-order successor from right subtree (size already adjusted, adjust back for recursive call)
            self.size += 1
            current.right = self._delete_recursive(current.right, successor.key)

        return current

    def _find_min(self, node: BSTNode) -> BSTNode:
        current = node
        while current.left is not None:
            current = current.left
        return current

    # ==================== TRAVERSALS ====================
    def inorder_traversal(self) -> List[Dict[str, Any]]:
        """
        Left -> Root -> Right traversal.
        Yields keys in strictly ascending sorted order.
        """
        result = []
        self._inorder_recursive(self.root, result)
        return result

    def _inorder_recursive(self, current: Optional[BSTNode], result: List[Dict[str, Any]]):
        if current is not None:
            self._inorder_recursive(current.left, result)
            result.append(current.to_dict())
            self._inorder_recursive(current.right, result)

    def preorder_traversal(self) -> List[Dict[str, Any]]:
        """Root -> Left -> Right traversal."""
        result = []
        self._preorder_recursive(self.root, result)
        return result

    def _preorder_recursive(self, current: Optional[BSTNode], result: List[Dict[str, Any]]):
        if current is not None:
            result.append(current.to_dict())
            self._preorder_recursive(current.left, result)
            self._preorder_recursive(current.right, result)

    def postorder_traversal(self) -> List[Dict[str, Any]]:
        """Left -> Right -> Root traversal."""
        result = []
        self._postorder_recursive(self.root, result)
        return result

    def _postorder_recursive(self, current: Optional[BSTNode], result: List[Dict[str, Any]]):
        if current is not None:
            self._postorder_recursive(current.left, result)
            self._postorder_recursive(current.right, result)
            result.append(current.to_dict())

    # ==================== VISUALIZATION EXPORT ====================
    def to_tree_structure(self) -> Optional[Dict[str, Any]]:
        """
        Serializes the entire tree into a hierarchical JSON structure
        ready for rendering with SVG/Canvas on the UI.
        """
        if self.root is None:
            return None
        return self._serialize_node(self.root, depth=0)

    def _serialize_node(self, node: Optional[BSTNode], depth: int) -> Optional[Dict[str, Any]]:
        if node is None:
            return None
        return {
            "key": node.key,
            "depth": depth,
            "data": node.to_dict()["data"],
            "left": self._serialize_node(node.left, depth + 1),
            "right": self._serialize_node(node.right, depth + 1),
            "has_left": node.left is not None,
            "has_right": node.right is not None
        }

    def get_height(self) -> int:
        """Returns height of the BST."""
        def _height(node: Optional[BSTNode]) -> int:
            if not node:
                return 0
            return 1 + max(_height(node.left), _height(node.right))
        return _height(self.root)

    def clear(self):
        self.root = None
        self.size = 0

    def __len__(self) -> int:
        return self.size
