# DATA STRUCTURE: Fenwick Tree (Binary Indexed Tree / BIT)
# DIFFICULTY: Medium | FREQUENCY: Medium (prefix-sum + update problems; competitive rounds)

# A compact array-based structure for prefix-sum queries WITH point updates in O(log n).
# The simpler cousin of a Segment Tree: less code and memory, but sum-style (invertible)
# operations only. Each index i is responsible for a range of size (i & -i) — the lowest set bit.

# Time Complexity:
# - Build: O(n log n) (or O(n) with the linear build below)
# - Prefix sum / range sum query: O(log n)
# - Point update: O(log n)
# Space: O(n)

# When to use:
# - Prefix sums / range sums that change (point updates) — cumulative frequency, inversions.
# - Prefer over a Segment Tree when the op is a sum (or any invertible group op) — simpler, less memory.
# - Reach for a Segment Tree instead if you need min/max/gcd (non-invertible) or range updates.

# COMMON MISTAKES:
# - Off-by-one: the tree is 1-indexed internally; convert 0-indexed inputs.
# - Using it for min/max (not invertible) — range query by subtraction only works for sums.
# - Forgetting update() adds a DELTA, not sets a value (track current values if you need "set").

# RELATED PROBLEMS:
# - Range Sum Query - Mutable (LC 307)
# - Count of Smaller Numbers After Self (LC 315)
# - Reverse Pairs (LC 493)


class FenwickTree:
    def __init__(self, size: int) -> None:
        self.n = size
        self.tree: list[int] = [0] * (size + 1)  # 1-indexed

    @classmethod
    def from_array(cls, arr: list[int]) -> "FenwickTree":
        ft = cls(len(arr))
        for i, val in enumerate(arr):
            ft.update(i, val)
        return ft

    def update(self, i: int, delta: int) -> None:
        """Add `delta` at 0-indexed position i."""
        i += 1  # to 1-indexed
        while i <= self.n:
            self.tree[i] += delta
            i += i & (-i)  # move to next responsible index

    def prefix_sum(self, i: int) -> int:
        """Sum of arr[0..i] inclusive (0-indexed)."""
        i += 1  # to 1-indexed
        total = 0
        while i > 0:
            total += self.tree[i]
            i -= i & (-i)  # move to parent
        return total

    def range_sum(self, left: int, right: int) -> int:
        """Sum of arr[left..right] inclusive (0-indexed)."""
        if left > right:
            return 0
        if left == 0:
            return self.prefix_sum(right)
        return self.prefix_sum(right) - self.prefix_sum(left - 1)


if __name__ == "__main__":
    arr = [1, 7, 3, 0, 5, 8, 3, 2, 6, 2]
    ft = FenwickTree.from_array(arr)

    # prefix_sum(4) = 1+7+3+0+5 = 16
    print(ft.prefix_sum(4))            # 16
    # range_sum(2, 5) = 3+0+5+8 = 16
    print(ft.range_sum(2, 5))          # 16
    # range_sum(0, 9) = sum(arr) = 37
    print(ft.range_sum(0, 9))          # 37

    # Point update: add 4 at index 3 (0 -> 4)
    ft.update(3, 4)
    # range_sum(2, 5) now = 3+4+5+8 = 20
    print(ft.range_sum(2, 5))          # 20
    # prefix_sum(3) = 1+7+3+4 = 15
    print(ft.prefix_sum(3))            # 15
