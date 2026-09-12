# DATA STRUCTURE: Segment Tree
# DIFFICULTY: Hard | FREQUENCY: Medium (range query + update problems at Google/competitive rounds)

# A binary tree built on array segments for fast range queries and point updates.
# Each node stores aggregate info (sum, min, max) for a range of the array.

# Time Complexity:
# - Build: O(n)
# - Query: O(log n)
# - Update: O(log n)
# Space: O(4n) ~= O(n)

# When to use:
# - Range sum/min/max queries WITH updates
# - Need O(log n) per query AND per update
# - Alternatives: Fenwick Tree (simpler, sum only), Sparse Table (O(1) query, no updates)

# COMMON MISTAKES:
# - Under-sizing the tree array; 4*n is the safe bound.
# - Mixing up the no-overlap / complete-overlap / partial-overlap cases in query.
# - Forgetting to re-aggregate the parent after a child update.
# - Using the wrong identity value (0 for sum, +inf for min, -inf for max).

# RELATED PROBLEMS:
# - Range Sum Query - Mutable (LC 307)
# - Count of Smaller Numbers After Self (LC 315)
# - The Skyline Problem (LC 218)


class SegmentTree:
    def __init__(self, arr: list[int]) -> None:
        self.n = len(arr)
        self.tree: list[int] = [0] * (4 * self.n)
        if self.n > 0:
            self._build(arr, 0, 0, self.n - 1)

    def _build(self, arr: list[int], node: int, start: int, end: int) -> None:
        if start == end:
            self.tree[node] = arr[start]
            return

        mid = (start + end) >> 1
        self._build(arr, 2 * node + 1, start, mid)
        self._build(arr, 2 * node + 2, mid + 1, end)
        self.tree[node] = self.tree[2 * node + 1] + self.tree[2 * node + 2]

    # Point update: set arr[idx] = val
    def update(self, idx: int, val: int) -> None:
        self._update_helper(0, 0, self.n - 1, idx, val)

    def _update_helper(self, node: int, start: int, end: int, idx: int, val: int) -> None:
        if start == end:
            self.tree[node] = val
            return

        mid = (start + end) >> 1
        if idx <= mid:
            self._update_helper(2 * node + 1, start, mid, idx, val)
        else:
            self._update_helper(2 * node + 2, mid + 1, end, idx, val)

        self.tree[node] = self.tree[2 * node + 1] + self.tree[2 * node + 2]

    # Range sum query [l, r]
    def query(self, l: int, r: int) -> int:
        return self._query_helper(0, 0, self.n - 1, l, r)

    def _query_helper(self, node: int, start: int, end: int, l: int, r: int) -> int:
        # No overlap
        if r < start or end < l:
            return 0
        # Complete overlap
        if l <= start and end <= r:
            return self.tree[node]
        # Partial overlap
        mid = (start + end) >> 1
        return (self._query_helper(2 * node + 1, start, mid, l, r)
                + self._query_helper(2 * node + 2, mid + 1, end, l, r))


# Min Segment Tree variant
class MinSegmentTree:
    def __init__(self, arr: list[int]) -> None:
        self.n = len(arr)
        self.tree: list[float] = [float("inf")] * (4 * self.n)
        if self.n > 0:
            self._build(arr, 0, 0, self.n - 1)

    def _build(self, arr: list[int], node: int, start: int, end: int) -> None:
        if start == end:
            self.tree[node] = arr[start]
            return

        mid = (start + end) >> 1
        self._build(arr, 2 * node + 1, start, mid)
        self._build(arr, 2 * node + 2, mid + 1, end)
        self.tree[node] = min(self.tree[2 * node + 1], self.tree[2 * node + 2])

    def update(self, idx: int, val: int) -> None:
        self._update_helper(0, 0, self.n - 1, idx, val)

    def _update_helper(self, node: int, start: int, end: int, idx: int, val: int) -> None:
        if start == end:
            self.tree[node] = val
            return

        mid = (start + end) >> 1
        if idx <= mid:
            self._update_helper(2 * node + 1, start, mid, idx, val)
        else:
            self._update_helper(2 * node + 2, mid + 1, end, idx, val)

        self.tree[node] = min(self.tree[2 * node + 1], self.tree[2 * node + 2])

    def query(self, l: int, r: int) -> float:
        return self._query_helper(0, 0, self.n - 1, l, r)

    def _query_helper(self, node: int, start: int, end: int, l: int, r: int) -> float:
        if r < start or end < l:
            return float("inf")
        if l <= start and end <= r:
            return self.tree[node]
        mid = (start + end) >> 1
        return min(
            self._query_helper(2 * node + 1, start, mid, l, r),
            self._query_helper(2 * node + 2, mid + 1, end, l, r),
        )


# Examples (only run when executed directly)
if __name__ == "__main__":
    seg = SegmentTree([1, 3, 5, 7, 9, 11])
    print(seg.query(1, 3))   # 15 (3 + 5 + 7)
    seg.update(2, 10)        # change index 2 from 5 to 10
    print(seg.query(1, 3))   # 20 (3 + 10 + 7)

    min_seg = MinSegmentTree([2, 5, 1, 4, 9, 3])
    print(min_seg.query(0, 5))  # 1
    print(min_seg.query(3, 5))  # 3
    min_seg.update(2, 7)
    print(min_seg.query(0, 2))  # 2
