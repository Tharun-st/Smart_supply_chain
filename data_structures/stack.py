"""
Intelligent Supply Chain Management System
LIFO Stack Implementation
"""

from typing import Any, Optional, List, Dict


class StackNode:
    """Represents an element node in the Linked List Stack."""
    def __init__(self, data: Any):
        self.data: Any = data
        self.next: Optional['StackNode'] = None


class Stack:
    """
    LIFO Stack implemented with linked nodes.
    Maintains 'top' pointer for O(1) push, pop, and peek operations.
    """
    def __init__(self, name: str = "ProcessedOrderStack"):
        self.top: Optional[StackNode] = None
        self.size: int = 0
        self.name: str = name

    def is_empty(self) -> bool:
        return self.top is None

    def get_size(self) -> int:
        return self.size

    def push(self, item: Any) -> StackNode:
        """Push an element onto the stack top. O(1)"""
        node = StackNode(item)
        node.next = self.top
        self.top = node
        self.size += 1
        return node

    def pop(self) -> Optional[Any]:
        """Pop the element from the stack top. O(1)"""
        if self.is_empty():
            return None
        popped = self.top
        self.top = self.top.next
        self.size -= 1
        return popped.data

    def peek(self) -> Optional[Any]:
        """View top element without removing. O(1)"""
        return self.top.data if self.top else None

    def clear(self):
        self.top = None
        self.size = 0

    def to_visual_stack(self, id_field: str = "id", label_field: str = "order_number") -> Dict[str, Any]:
        """Formats the stack for frontend visualization."""
        nodes = []
        curr = self.top
        pos = 1
        while curr:
            data = curr.data
            item_id = data.get(id_field, pos) if isinstance(data, dict) else pos
            item_label = data.get(label_field, str(data)) if isinstance(data, dict) else str(data)
            nodes.append({
                "position": pos,
                "is_top": (pos == 1),
                "id": item_id,
                "label": item_label,
                "data": data
            })
            curr = curr.next
            pos += 1
        return {
            "size": self.size,
            "is_empty": self.is_empty(),
            "top_item": self.peek(),
            "nodes": nodes
        }
