# ALGORITHM: Topological Sort (Kahn's BFS + DFS) + DAG shortest path
# CATEGORY: Graph / Ordering
# DIFFICULTY: Medium | FREQUENCY: Very High (course schedule, build order at Google/Amazon/Meta)

# Kahn's Algorithm (BFS-based):
# - Detects cycles in a directed graph; works only for DAGs to produce a valid ordering.
# Steps:
#   1. Compute indegrees (incoming edge count) for each node.
#   2. Start from nodes with indegree 0 (no dependencies).
#   3. Repeatedly remove an indegree-0 node, decrement its neighbors' indegrees, enqueue new zeros.
#   4. If all nodes are processed, return the order; otherwise a cycle exists.
# Time: O(V + E)  |  Space: O(V)

# COMMON MISTAKES:
# - Using list.pop(0) as a queue (O(n)); use collections.deque.
# - Forgetting to detect a cycle (result length != number of nodes).
# - For DAG shortest path: relaxing in arbitrary order instead of topological order.

# RELATED PROBLEMS:
# - Course Schedule (LC 207)
# - Course Schedule II (LC 210)
# - Alien Dictionary (LC 269)
# - Parallel Courses (LC 1136)

from collections import deque


def topo_sort(graph: dict[int, list[int]]) -> list[int] | None:
    # Step 1: compute indegrees
    indegree: dict[int, int] = {node: 0 for node in graph}
    for node in graph:
        for neighbor in graph[node]:
            indegree[neighbor] = indegree.get(neighbor, 0) + 1

    # Step 2: enqueue all indegree-0 nodes
    queue: deque[int] = deque(node for node in graph if indegree[node] == 0)

    # Step 3: process
    result: list[int] = []
    while queue:
        current = queue.popleft()
        result.append(current)
        for neighbor in graph[current]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    # Step 4: cycle check
    if len(result) != len(graph):
        return None  # cycle detected

    return result


# Alternative approach: DFS-based topological sort
def topo_sort_dfs(graph: dict[int, list[int]]) -> list[int]:
    visited: set[int] = set()
    stack: list[int] = []

    def dfs(node: int) -> None:
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                dfs(neighbor)
        stack.append(node)

    for node in graph:
        if node not in visited:
            dfs(node)

    return stack[::-1]


# Shortest Path in a DAG using topological sort.
# - Handles negative weights on acyclic graphs (unlike Dijkstra).
# - Time: O(V + E)
def shortest_path_dag(graph: dict[int, list[tuple[int, int]]], src: int) -> list[float]:
    n = len(graph)
    dist: list[float] = [float("inf")] * n
    dist[src] = 0

    stack: list[int] = []
    visited: set[int] = set()

    def t_sort(node: int) -> None:
        visited.add(node)
        for neighbor, _weight in graph[node]:
            if neighbor not in visited:
                t_sort(neighbor)
        stack.append(node)

    for node in graph:
        if node not in visited:
            t_sort(node)

    while stack:
        node = stack.pop()
        if dist[node] != float("inf"):  # relax only reachable nodes
            for neighbor, weight in graph[node]:
                if dist[node] + weight < dist[neighbor]:
                    dist[neighbor] = dist[node] + weight

    return dist


# Course Schedule II using DFS-based topological sort with cycle detection.
def find_order(num_courses: int, prerequisites: list[list[int]]) -> list[int]:
    res: list[int] = []

    pre_set: list[list[int]] = [[] for _ in range(num_courses)]
    for crs, pre in prerequisites:
        pre_set[crs].append(pre)

    visit: set[int] = set()
    cycle: set[int] = set()

    def dfs(crs: int) -> bool:
        if crs in cycle:
            return False
        if crs in visit:
            return True

        cycle.add(crs)
        for pre in pre_set[crs]:
            if not dfs(pre):
                return False
        cycle.remove(crs)
        visit.add(crs)
        res.append(crs)
        return True

    for c in range(num_courses):
        if not dfs(c):
            return []
    return res


if __name__ == "__main__":
    graph = {
        0: [1],
        1: [4],
        2: [3, 5],
        3: [4],
        4: [],
        5: [1],
        6: [0],
    }
    print("output with BFS:", topo_sort(graph))  # e.g. [2, 6, 3, 5, 0, 1, 4]
    print("output with DFS:", topo_sort_dfs(graph))  # e.g. [6, 2, 5, 3, 0, 1, 4]

    weighted_graph = {
        0: [(1, 2), (4, 1)],
        1: [(2, 3)],
        2: [(3, 6)],
        3: [],
        4: [(5, 4), (2, 2)],
        5: [(3, 1)],
    }
    print("Shortest paths from source 0:", shortest_path_dag(weighted_graph, 0))

    # [0, 2, 1, 3] or [0, 1, 2, 3]
    print("Course Schedule II order:", find_order(4, [[1, 0], [2, 0], [3, 1], [3, 2]]))
