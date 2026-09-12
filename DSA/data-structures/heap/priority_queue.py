# DATA STRUCTURE: Min-Heap based Priority Queue
# DIFFICULTY: Medium | FREQUENCY: Very High (Dijkstra, Prim, task scheduling at Google/Amazon/Uber)

# A priority queue is an abstract data type similar to a regular queue, but where each element has a
# "priority". In a min-priority queue, elements with lower priority values are served first.

# Time Complexity:
# - Insertion (enqueue): O(log n)
# - Removal of minimum element (dequeue): O(log n)
# - Peek at minimum element: O(1)

# When to use:
# - When you need to efficiently retrieve and remove the highest-priority (lowest-value) element.
# - When implementing algorithms like Dijkstra's shortest path or Prim's minimum spanning tree.
# - When managing tasks with varying levels of urgency.

# NOTE: In idiomatic Python, use the built-in `heapq` module directly with tuples, e.g.
# heapq.heappush(pq, (priority, item)). To customize ordering, push a (key(item), item) tuple.
# This explicit class mirrors the JS MinPriorityScope with an optional `key` function
# (the Pythonic equivalent of a comparator) for teaching purposes.

import heapq
from collections.abc import Callable
from typing import Any

# COMMON MISTAKES:
# - Relying on heapq being stable / having decrease-key (it has neither).
# - Pushing raw objects that aren't comparable; use a (key, item) tuple instead.
# - Forgetting that heapq is a MIN-heap (negate the key for max-priority behaviour).
# - Peeking/popping without checking for emptiness.

# RELATED PROBLEMS:
# - Network Delay Time (LC 743)
# - K Closest Points to Origin (LC 973)
# - Task Scheduler (LC 621)
# - Merge k Sorted Lists (LC 23)


class MinPriorityQueue:
    def __init__(self, key: Callable[[Any], Any] | None = None) -> None:
        # `key` maps an element to its comparable priority. Default: the element itself.
        self._key = key if key is not None else (lambda x: x)
        self._heap: list[tuple[Any, int, Any]] = []
        # A monotonically increasing counter breaks ties so unorderable items never compare directly.
        self._counter = 0

    def enqueue(self, element: Any) -> None:
        heapq.heappush(self._heap, (self._key(element), self._counter, element))
        self._counter += 1

    def dequeue(self) -> Any | None:
        if not self._heap:
            return None
        return heapq.heappop(self._heap)[2]

    def peek(self) -> Any | None:
        return self._heap[0][2] if self._heap else None

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def size(self) -> int:
        return len(self._heap)


# Examples (only run when executed directly)
if __name__ == "__main__":
    # Simple numbers (default key)
    pq1 = MinPriorityQueue()
    pq1.enqueue(5)
    pq1.enqueue(2)
    pq1.enqueue(8)
    print(pq1.dequeue())  # 2

    # Custom key for tuples [distance, node] -> order by distance
    pq2 = MinPriorityQueue(key=lambda x: x[0])
    pq2.enqueue([10, "A"])
    pq2.enqueue([5, "B"])
    pq2.enqueue([15, "C"])
    print(pq2.dequeue())  # [5, 'B']

    # Custom key for dict-like tasks -> order by priority
    pq3 = MinPriorityQueue(key=lambda x: x["priority"])
    pq3.enqueue({"name": "Task A", "priority": 3})
    pq3.enqueue({"name": "Task B", "priority": 1})
    pq3.enqueue({"name": "Task C", "priority": 2})
    print(pq3.dequeue())  # {'name': 'Task B', 'priority': 1}
