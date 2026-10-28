

from typing import Any, Optional, List, Dict


class QueueNode:
    """
    Represents a single element node in the Linked-List Queue.
    """
    def __init__(self, data: Any):
        self.data: Any = data
        self.next: Optional['QueueNode'] = None

    def to_dict(self) -> Dict[str, Any]:
        if hasattr(self.data, 'to_dict'):
            return self.data.to_dict()
        elif isinstance(self.data, dict):
            return self.data
        return {"value": self.data}


class LinkedListQueue:
    """
    FIFO Queue implemented with a custom Linked List.
    Maintains both 'front' and 'rear' pointers for O(1) enqueue and dequeue operations.
    """
    def __init__(self, name: str = "CustomerOrderQueue"):
        self.front: Optional[QueueNode] = None
        self.rear: Optional[QueueNode] = None
        self.size: int = 0
        self.name: str = name

    def is_empty(self) -> bool:
        """Returns True if the queue has no elements."""
        return self.front is None

    def get_size(self) -> int:
        """Returns the current number of elements in the queue."""
        return self.size

    def enqueue(self, item: Any) -> QueueNode:
        """
        Inserts a new item at the REAR of the queue.
        Time Complexity: O(1)
        """
        new_node = QueueNode(item)
        if self.rear is None:
            # Queue is currently empty
            self.front = new_node
            self.rear = new_node
        else:
            # Append after rear and advance rear pointer
            self.rear.next = new_node
            self.rear = new_node
        self.size += 1
        return new_node

    def dequeue(self) -> Optional[Any]:
        """
        Removes and returns the item at the FRONT of the queue.
        Follows FIFO (First-In, First-Out) principle.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None

        removed_node = self.front
        self.front = self.front.next

        # If front becomes None, rear must also become None
        if self.front is None:
            self.rear = None

        self.size -= 1
        return removed_node.data

    def peek(self) -> Optional[Any]:
        """
        Returns the data at the FRONT of the queue without removing it.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        return self.front.data

    def to_list(self) -> List[Any]:
        """
        Traverses the queue from FRONT to REAR and returns all items as a list.
        Time Complexity: O(n)
        """
        items = []
        current = self.front
        while current is not None:
            items.append(current.data)
            current = current.next
        return items

    def to_visual_queue(self, id_field: str = "id", label_field: str = "customer_name") -> Dict[str, Any]:
        """
        Produces a rich structured representation for the UI queue visualization:
        FRONT indicator, list of nodes with their positions, and REAR indicator.
        """
        nodes = []
        current = self.front
        position = 1
        while current is not None:
            data = current.to_dict()
            item_id = data.get(id_field, f"Order-{position}")
            item_label = data.get(label_field, f"Order #{item_id}")
            nodes.append({
                "position": position,
                "is_front": position == 1,
                "is_rear": current.next is None,
                "id": item_id,
                "label": item_label,
                "data": data
            })
            current = current.next
            position += 1

        return {
            "size": self.size,
            "is_empty": self.is_empty(),
            "front_item": self.peek() if not self.is_empty() else None,
            "nodes": nodes
        }

    def clear(self):
        """Empties the queue."""
        self.front = None
        self.rear = None
        self.size = 0

    def __len__(self) -> int:
        return self.size

    def __repr__(self) -> str:
        current = self.front
        items = []
        while current:
            items.append(str(current.data))
            current = current.next
        return "FRONT -> [" + " -> ".join(items) + "] -> REAR"
