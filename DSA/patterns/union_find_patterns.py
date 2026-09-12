# PATTERN NAME: Union-Find (Disjoint Set Union)
# DIFFICULTY: Medium | FREQUENCY: Very High (connectivity, grouping, MST at Google/Amazon/Meta)

# PROBLEM TYPES:
# - Dynamic connectivity problems.
# - Network connectivity, clustering.
# - Connected components (image processing).
# - Kruskal's Minimum Spanning Tree.

# WHEN TO USE:
# - Efficiently manage and merge disjoint sets.
# - Check if two elements are in the same set.
# - Dynamically connect components / track connected components.

# CORE IDEA (INTUITION):
# - Represent each element as a node in a tree; each tree is a set with a root representative.
# - Path compression flattens the tree during find.
# - Union by rank/size keeps trees shallow.

# INVARIANTS:
# - Each element points to its parent; the root points to itself.
# - Rank/size is maintained to optimize unions.
# - Path compression speeds up future finds.

# COMMON OPERATIONS:
# - find(x): representative (root) of x's set.
# - union(x, y): merge the sets of x and y.
# - is_connected(x, y): whether x and y share a root.

# COMMON MISTAKES:
# - Skipping path compression in find.
# - Skipping union by rank/size in union.
# - Forgetting to lazily initialize new elements (this dict-based version does it in find).
# - Assuming all elements are known beforehand.

# TIME & SPACE:
# - Time: O(alpha(N)) per operation (inverse Ackermann - effectively O(1) amortized).
# - Space: O(N) for parent and rank maps.

# RELATED PROBLEMS:
# - Number of Connected Components (LC 323)
# - Redundant Connection (LC 684)
# - Accounts Merge (LC 721)
# - Graph Valid Tree (LC 261)
# - Checking Existence of Edge Length Limited Paths (LC 1697)


# Dict-based Union-Find that lazily initializes unknown elements (handy for sparse/string keys).
class UnionFind:
    def __init__(self) -> None:
        self.parents: dict[int, int] = {}
        self.ranks: dict[int, int] = {}

    def find(self, x: int) -> int:
        if x not in self.parents:
            self.parents[x] = x
            self.ranks[x] = 0

        if self.parents[x] != x:
            self.parents[x] = self.find(self.parents[x])  # path compression
        return self.parents[x]

    def union(self, x: int, y: int) -> bool:
        root_x, root_y = self.find(x), self.find(y)
        if root_x == root_y:
            return False  # already united

        if self.ranks[root_x] > self.ranks[root_y]:
            self.parents[root_y] = root_x
        elif self.ranks[root_y] > self.ranks[root_x]:
            self.parents[root_x] = root_y
        else:
            self.parents[root_y] = root_x
            self.ranks[root_x] += 1
        return True

    def is_connected(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)


# EXAMPLE: Checking Existence of Edge Length Limited Paths
# Offline queries: sort queries and edges by limit, union edges under the limit, then answer.
def distance_limited_paths_exist(n: int, edge_list: list[list[int]],
                                 queries: list[list[int]]) -> list[bool]:
    answer = [False] * len(queries)

    # attach the original index so we can restore order after sorting
    indexed_queries = [(*q, i) for i, q in enumerate(queries)]
    indexed_queries.sort(key=lambda q: q[2])
    edge_list.sort(key=lambda e: e[2])

    uf = UnionFind()
    edge_idx = 0

    for p, q, limit, org_idx in indexed_queries:
        while edge_idx < len(edge_list) and limit > edge_list[edge_idx][2]:
            x, y, _ = edge_list[edge_idx]
            uf.union(x, y)
            edge_idx += 1

        if uf.is_connected(p, q):
            answer[org_idx] = True

    return answer


if __name__ == "__main__":
    edge_list = [[0, 2, 4], [1, 2, 3], [2, 3, 1], [4, 5, 5]]
    queries = [[2, 3, 2], [1, 3, 3], [2, 0, 5], [0, 5, 6]]
    print(distance_limited_paths_exist(6, edge_list, queries))
    # [True, False, True, False]
