# DATA STRUCTURE: MinHeap
# DIFFICULTY: Medium | FREQUENCY: Very High (Dijkstra, Prim, Top-K, Median at Google/Meta/Amazon)

# A MinHeap is a binary tree where the value of each node is less than or equal to the values of its
# children. This implementation uses a list to represent the heap.
# The root of the heap is at index 0, and for any node at index i:
# - The left child is at index 2*i + 1
# - The right child is at index 2*i + 2
# - The parent is at index (i - 1) // 2
# The main operations are push (to add an element) and pop (to remove the minimum element).
# Both operations maintain the heap property by bubbling elements up or down as necessary.

# Time Complexity:
# - push: O(log n) in the worst case, where n is the number of elements in the heap.
# - pop: O(log n) in the worst case.

# NOTE: In idiomatic Python, prefer the built-in `heapq` module for a min-heap
# (heapq.heappush / heapq.heappop). This explicit class is kept for teaching the internals.

# COMMON MISTAKES:
# - Forgetting to bubble up after push or bubble down after pop.
# - Comparing with '<' vs '<=' inconsistently in _up/_down (can loop or break heap order).
# - Off-by-one in child/parent index math: left = 2*i+1, right = 2*i+2, parent = (i-1)//2.
# - Popping from an empty heap without a guard.

# RELATED PROBLEMS:
# - Kth Largest Element in an Array (LC 215)
# - Top K Frequent Elements (LC 347)
# - Find Median from Data Stream (LC 295)
# - Merge k Sorted Lists (LC 23)


class MinHeap:
    def __init__(self) -> None:
        # Initialize empty heap list
        self.h: list[int] = []

    def push(self, val: int) -> None:
        # Add new value to end of heap
        self.h.append(val)
        # Bubble up to maintain heap property
        self._up(len(self.h) - 1)

    def pop(self) -> int | None:
        # Return None if heap is empty
        if not self.h:
            return None
        # Return last element if only one element
        if len(self.h) == 1:
            return self.h.pop()

        # Store minimum value (root)
        top = self.h[0]
        # Move last element to root
        self.h[0] = self.h.pop()
        # Bubble down to maintain heap property
        self._down(0)
        return top

    def peek(self) -> int | None:
        return self.h[0] if self.h else None

    def size(self) -> int:
        return len(self.h)

    def _up(self, i: int) -> None:
        h = self.h
        while i > 0:
            # Calculate parent index
            p = (i - 1) // 2
            # Stop if parent is smaller (heap property satisfied)
            if h[p] <= h[i]:
                break
            # Swap with parent
            h[p], h[i] = h[i], h[p]
            i = p

    def _down(self, i: int) -> None:
        h = self.h
        n = len(h)
        while True:
            smallest = i
            # Calculate left and right child indices
            left = 2 * i + 1
            right = 2 * i + 2
            # Find smallest among node and its children
            if left < n and h[left] < h[smallest]:
                smallest = left
            if right < n and h[right] < h[smallest]:
                smallest = right
            # Stop if current node is smallest (heap property satisfied)
            if smallest == i:
                break
            # Swap with smallest child
            h[i], h[smallest] = h[smallest], h[i]
            i = smallest


# Examples (only run when executed directly)
if __name__ == "__main__":
    min_heap = MinHeap()
    min_heap.push(5)
    min_heap.push(3)
    min_heap.push(8)
    min_heap.push(1)

    print(min_heap.pop())  # 1
