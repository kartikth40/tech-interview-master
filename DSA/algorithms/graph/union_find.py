# ALGORITHM: Union-Find (Disjoint Set Union) with path compression + union by rank
# CATEGORY: Graph / Data Structure
# DIFFICULTY: Medium | FREQUENCY: Very High (connectivity, MST, grouping at Google/Amazon/Meta)

# Detect cycles in an undirected graph, track connected components, and back Kruskal's MST.
# Algorithm steps:
# 1. Initialize each element as its own parent (self root) with rank 0.
# 2. For each union, find the roots of both elements.
# 3. If roots differ, union them by rank.
# 4. If roots are the same, a cycle is detected.

# Time Complexity: O(alpha(N)) per operation (inverse Ackermann - effectively O(1) amortized).
# Space Complexity: O(N) for parent and rank arrays.

# Uses of Union-Find:
# 1. Cycle detection in undirected graphs
# 2. Connected components in graphs
# 3. Kruskal's algorithm for Minimum Spanning Tree
# 4. Network connectivity problems

# COMMON MISTAKES:
# - Skipping path compression / union by rank (degrades to O(n) per op).
# - Forgetting union() should report whether a merge happened (useful for cycle detection).
# - Sizing parent/rank arrays incorrectly for the number of nodes.

# RELATED PROBLEMS:
# - Number of Connected Components in an Undirected Graph (LC 323)
# - Redundant Connection (LC 684)
# - Accounts Merge (LC 721)
# - Checking Existence of Edge Length Limited Paths (LC 1697)


class UnionFind:
    def __init__(self, n: int) -> None:
        self.parent = list(range(n))  # each element is its own parent
        self.rank = [0] * n           # initial rank is 0

    def find(self, x: int) -> int:
        # Path compression
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x == root_y:
            return False  # already in the same set

        # Union by rank
        if self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        elif self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1
        return True

    def connected(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)


# Example usage:
if __name__ == "__main__":
    uf = UnionFind(7)  # nodes 0-6
    uf.union(1, 2)
    uf.union(2, 3)
    uf.union(4, 5)
    uf.union(5, 6)

    print(uf.connected(1, 3))  # True
    print(uf.connected(1, 4))  # False
    uf.union(3, 4)
    print(uf.connected(1, 4))  # True
