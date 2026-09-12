# ALGORITHM: Kosaraju's Algorithm (Strongly Connected Components)
# CATEGORY: Graph / SCC / DFS
# DIFFICULTY: Hard | FREQUENCY: Medium (SCC / dependency-cycle analysis at Google/competitive)

# WHEN TO USE:
# - Find strongly connected components (SCCs) in a directed graph.
# - Analyze structure in social/web/dependency graphs, or condense a graph into its SCCs.
# - Identify cycles in a directed graph (each non-trivial SCC is a cycle).

# CORE IDEA (INTUITION):
# 1. First DFS on the original graph, pushing nodes onto a stack in finishing-time (post) order.
# 2. Transpose the graph (reverse every edge).
# 3. Second DFS on the transposed graph, popping nodes in decreasing finishing time.
#    Each DFS tree in this pass is one SCC.

# INVARIANTS:
# - Each vertex is visited exactly once per DFS pass.
# - The stack yields vertices in decreasing finishing-time order.
# - The transposed graph has the same vertices with reversed edges.

# TIME: O(V + E)  |  SPACE: O(V)

# COMMON MISTAKES:
# - Reversing the graph incorrectly.
# - Not processing nodes in finishing-time order during the second DFS.
# - Failing to reset the visited marks between the two passes.

# RELATED PROBLEMS:
# - Critical Connections in a Network (LC 1192) - related (Tarjan bridges)
# - Course Schedule II (LC 210) - ordering / cycle detection


def kosaraju(adj: list[list[int]]) -> int:
    n = len(adj)
    stack: list[int] = []
    vis = [False] * n

    # First pass: order by finishing time
    for i in range(n):
        if not vis[i]:
            _dfs(i, adj, vis, stack)

    # Transpose / reverse edges
    adj_t: list[list[int]] = [[] for _ in range(n)]
    for i in range(n):
        vis[i] = False
        for nei in adj[i]:
            adj_t[nei].append(i)

    # Second pass: count SCCs
    scc = 0
    while stack:
        node = stack.pop()
        if not vis[node]:
            scc += 1
            _dfs(node, adj_t, vis, None)
    return scc


def _dfs(i: int, adj: list[list[int]], vis: list[bool], stack: list[int] | None) -> None:
    vis[i] = True
    for nei in adj[i]:
        if not vis[nei]:
            _dfs(nei, adj, vis, stack)
    if stack is not None:
        stack.append(i)


# EXAMPLE:
if __name__ == "__main__":
    adj = [[2, 3], [0], [1], [4], []]
    print(kosaraju(adj))  # 3
