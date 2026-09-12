# DATA STRUCTURE: MaxHeap
# DIFFICULTY: Medium | FREQUENCY: Very High (Top-K, running median, scheduling at Google/Meta/Amazon)

# A MaxHeap is a binary tree where the value of each node is greater than
# or equal to the values of its children. The root always holds the maximum.

# Time Complexity:
# - push: O(log n)
# - pop: O(log n)
# - peek: O(1)

# When to use:
# - Kth smallest element (maintain max-heap of size k)
# - Running median (pair with MinHeap)
# - Priority scheduling (highest priority first)
# - Merge K sorted lists (less common, usually MinHeap)

# NOTE: Python's `heapq` is a MIN-heap only. The idiomatic way to get a max-heap is to push
# negated values (heapq.heappush(h, -x)) and negate on pop. This explicit class is kept for
# teaching the internals; in real interviews mention the "negate values" trick with heapq.

from min_heap import MinHeap

# COMMON MISTAKES:
# - Assuming heapq is a max-heap (it is min-only; negate values or use this class).
# - Using '>' vs '>=' inconsistently in _up/_down, corrupting heap order.
# - Off-by-one in child/parent index math.
# - Integer vs float division for the running-median average.

# RELATED PROBLEMS:
# - Kth Largest Element in an Array (LC 215)
# - Find Median from Data Stream (LC 295)
# - Top K Frequent Elements (LC 347)
# - Last Stone Weight (LC 1046)


class MaxHeap:
    def __init__(self) -> None:
        self.h: list[int] = []

    def push(self, val: int) -> None:
        self.h.append(val)
        self._up(len(self.h) - 1)

    def pop(self) -> int | None:
        if not self.h:
            return None
        if len(self.h) == 1:
            return self.h.pop()

        top = self.h[0]
        self.h[0] = self.h.pop()
        self._down(0)
        return top

    def peek(self) -> int | None:
        return self.h[0] if self.h else None

    def size(self) -> int:
        return len(self.h)

    def _up(self, i: int) -> None:
        h = self.h
        while i > 0:
            p = (i - 1) >> 1
            if h[p] >= h[i]:
                break
            h[p], h[i] = h[i], h[p]
            i = p

    def _down(self, i: int) -> None:
        h = self.h
        n = len(h)
        while True:
            largest = i
            left = 2 * i + 1
            right = 2 * i + 2
            if left < n and h[left] > h[largest]:
                largest = left
            if right < n and h[right] > h[largest]:
                largest = right
            if largest == i:
                break
            h[i], h[largest] = h[largest], h[i]
            i = largest


# === RUNNING MEDIAN (classic SDE-2 problem) ===
# Use MaxHeap for lower half, MinHeap for upper half.
# Median is always accessible from the tops of the heaps.
class MedianFinder:
    def __init__(self) -> None:
        self.lo = MaxHeap()  # max-heap: stores smaller half
        self.hi = MinHeap()  # min-heap: stores larger half

    def add_num(self, num: int) -> None:
        self.lo.push(num)
        # Ensure max of lo <= min of hi
        self.hi.push(self.lo.pop())

        # Balance: lo can have at most 1 more element than hi
        if self.lo.size() < self.hi.size():
            self.lo.push(self.hi.pop())

    def find_median(self) -> float:
        if self.lo.size() > self.hi.size():
            return self.lo.peek()
        return (self.lo.peek() + self.hi.peek()) / 2


# Examples (only run when executed directly)
if __name__ == "__main__":
    max_heap = MaxHeap()
    max_heap.push(3)
    max_heap.push(1)
    max_heap.push(5)
    max_heap.push(2)
    print(max_heap.pop())   # 5
    print(max_heap.pop())   # 3
    print(max_heap.peek())  # 2

    mf = MedianFinder()
    mf.add_num(1)
    mf.add_num(2)
    print(mf.find_median())  # 1.5
    mf.add_num(3)
    print(mf.find_median())  # 2
    mf.add_num(4)
    print(mf.find_median())  # 2.5
