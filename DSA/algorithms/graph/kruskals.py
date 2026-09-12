# ALGORITHM: Kruskal's Minimum Spanning Tree (MST)
# CATEGORY: Graph / Greedy / MST
# DIFFICULTY: Medium | FREQUENCY: High (MST / connecting-cities problems at Google/Amazon)

# Solves undirected, connected, cyclic graphs with non-negative weights.
# Greedy: always add the smallest edge that doesn't form a cycle.
# Time Complexity: O(E log E) (dominated by sorting the edges).

# CORE IDEA (INTUITION):
# Sort all edges by weight, then add them one by one, skipping any edge that would connect two
# vertices already in the same component (a cycle). Union-Find tracks components efficiently.

# INVARIANTS:
# - The chosen edges never form a cycle.
# - Edges are considered in non-decreasing weight order.

# Requires the Union-Find (Disjoint Set Union) data structure.

# COMMON MISTAKES:
# - Forgetting to sort edges by weight first.
# - Sizing Union-Find for the wrong number of vertices.
# - Not using union()'s boolean result to skip cycle-forming edges.

# RELATED PROBLEMS:
# - Min Cost to Connect All Points (LC 1584)
# - Connecting Cities With Minimum Cost (LC 1135)
# - Optimize Water Distribution in a Village (LC 1168)

from union_find import UnionFind


def spanning_tree(V: int, edges: list[list[int]]) -> int:
    edges.sort(key=lambda e: e[2])
    uf = UnionFind(V)

    total = 0
    for u, v, w in edges:
        if not uf.connected(u, v):
            uf.union(u, v)
            total += w
    return total


# Example usage:
if __name__ == "__main__":
    V = 5
    edges = [
        [0, 1, 2],
        [0, 3, 6],
        [1, 2, 3],
        [1, 3, 8],
        [1, 4, 5],
        [2, 4, 7],
        [3, 4, 9],
    ]
    print(spanning_tree(V, edges))  # 16
