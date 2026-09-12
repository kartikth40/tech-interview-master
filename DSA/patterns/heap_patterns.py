# PATTERN NAME: Heap / Priority Queue Patterns
# DIFFICULTY: Medium | FREQUENCY: Very High (Top-K, merge-K, running median at Google/Meta/Amazon)

# WHEN TO USE:
# - Top K / Kth largest or smallest element.
# - Merge K sorted lists/arrays.
# - Running median (two heaps).
# - Scheduling problems (tasks with deadlines/priorities).
# - Any problem needing repeated access to the min or max element.

# CORE IDEA (INTUITION):
# - A heap gives O(log n) insert and O(1) access to the min/max.
# - For "Top K largest": use a MIN-heap of size k (evict the smallest when full).
# - For "Top K smallest": use a MAX-heap of size k (evict the largest when full).
# - For "Merge K sorted": push the first element of each list, pop then push its successor.

# INVARIANTS:
# - Heap size is kept at k for Top-K problems.
# - For the two-heap median: len(lo) >= len(hi), differ by at most 1.

# NOTE: Python's heapq is a MIN-heap. For a max-heap, negate values (push -x). This file uses heapq
# directly (idiomatic) rather than the explicit heap classes in DSA/data-structures/heap/.

# COMMON MISTAKES:
# - Using a max-heap where a min-heap is needed for Top-K (for K largest, use a MIN-heap of size k).
# - Forgetting to seed the merge-K heap with the first element of each list.
# - Not rebalancing the two heaps after every insertion in the median finder.
# - Pushing non-comparable objects; push a (key, item) tuple instead.

# TIME & SPACE:
# - Top K Frequent / Kth Largest / K Closest: O(n log k) time, O(k) space.
# - Merge K Sorted: O(N log k) time, O(k) space.
# - Running Median: O(log n) per add, O(n) space.
# - Reorganize String: ~O(n) time, O(26) space.

# RELATED PROBLEMS:
# - Top K Frequent Elements (LC 347)
# - Kth Largest Element (LC 215)
# - Merge K Sorted Lists (LC 23)
# - K Closest Points to Origin (LC 973)
# - Find Median from Data Stream (LC 295)
# - Reorganize String (LC 767)
# - Last Stone Weight (LC 1046)

import heapq
from collections import Counter


# === KTH LARGEST ELEMENT ===
# Min-heap of size k: the root is always the kth largest seen so far.
def find_kth_largest(nums: list[int], k: int) -> int:
    heap: list[int] = []
    for n in nums:
        heapq.heappush(heap, n)
        if len(heap) > k:
            heapq.heappop(heap)
    return heap[0]


# === TOP K FREQUENT ELEMENTS ===
# Min-heap ordered by frequency; keep the k most frequent.
def top_k_frequent(nums: list[int], k: int) -> list[int]:
    freq = Counter(nums)
    heap: list[tuple[int, int]] = []  # (count, num)
    for num, count in freq.items():
        heapq.heappush(heap, (count, num))
        if len(heap) > k:
            heapq.heappop(heap)
    return [num for _, num in heap]


# === MERGE K SORTED LISTS ===
# Push (value, list_index, element_index); always pop the global minimum.
def merge_k_lists(lists: list[list[int]]) -> list[int]:
    heap: list[tuple[int, int, int]] = []
    result: list[int] = []

    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst[0], i, 0))

    while heap:
        val, li, ei = heapq.heappop(heap)
        result.append(val)
        if ei + 1 < len(lists[li]):
            heapq.heappush(heap, (lists[li][ei + 1], li, ei + 1))

    return result


# === K CLOSEST POINTS TO ORIGIN ===
# Max-heap of size k on distance (negate distance); evict the farthest.
def k_closest(points: list[list[int]], k: int) -> list[list[int]]:
    def dist(p: list[int]) -> int:
        return p[0] * p[0] + p[1] * p[1]

    heap: list[tuple[int, list[int]]] = []  # (-distance, point)
    for p in points:
        heapq.heappush(heap, (-dist(p), p))
        if len(heap) > k:
            heapq.heappop(heap)
    return [p for _, p in heap]


# === RUNNING MEDIAN (two heaps) ===
class MedianFinder:
    def __init__(self) -> None:
        self.lo: list[int] = []  # max-heap (store negatives): smaller half
        self.hi: list[int] = []  # min-heap: larger half

    def add_num(self, num: int) -> None:
        heapq.heappush(self.lo, -num)
        # Ensure max(lo) <= min(hi)
        heapq.heappush(self.hi, -heapq.heappop(self.lo))
        # Rebalance: lo may have at most 1 more element than hi
        if len(self.lo) < len(self.hi):
            heapq.heappush(self.lo, -heapq.heappop(self.hi))

    def find_median(self) -> float:
        if len(self.lo) > len(self.hi):
            return -self.lo[0]
        return (-self.lo[0] + self.hi[0]) / 2


# === REORGANIZE STRING ===
# Max-heap by frequency: always place the two most frequent remaining chars.
def reorganize_string(s: str) -> str:
    freq = Counter(s)
    if max(freq.values()) > (len(s) + 1) // 2:
        return ""

    heap: list[tuple[int, str]] = [(-count, ch) for ch, count in freq.items()]
    heapq.heapify(heap)

    result: list[str] = []
    while len(heap) > 1:
        count1, c1 = heapq.heappop(heap)
        count2, c2 = heapq.heappop(heap)
        result.append(c1)
        result.append(c2)
        if count1 + 1 < 0:
            heapq.heappush(heap, (count1 + 1, c1))
        if count2 + 1 < 0:
            heapq.heappush(heap, (count2 + 1, c2))

    if heap:
        result.append(heap[0][1])

    return "".join(result)


if __name__ == "__main__":
    print(find_kth_largest([3, 2, 1, 5, 6, 4], 2))       # 5
    print(sorted(top_k_frequent([1, 1, 1, 2, 2, 3], 2)))  # [1, 2]
    print(merge_k_lists([[1, 4, 5], [1, 3, 4], [2, 6]]))  # [1, 1, 2, 3, 4, 4, 5, 6]
    print(k_closest([[1, 3], [-2, 2], [5, 8], [0, 1]], 2))  # closest 2 points

    mf = MedianFinder()
    mf.add_num(1)
    mf.add_num(2)
    print(mf.find_median())  # 1.5
    mf.add_num(3)
    print(mf.find_median())  # 2

    print(reorganize_string("aab"))   # e.g. "aba"
    print(reorganize_string("aaab"))  # ""
