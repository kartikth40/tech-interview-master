# PATTERN NAME: Cycle Detection in a Directed Graph
# DIFFICULTY: Medium | FREQUENCY: Very High (course schedule, dependency resolution at all companies)

# WHEN TO USE:
# - Directed graphs where you must detect cycles.
# - Course scheduling with prerequisites.
# - Dependency resolution, topological sort applicability.

# CORE IDEA (INTUITION):
# - DFS with three states per node: UNVISITED, VISITING, VISITED.
# - Reaching a node currently in the VISITING state means a back edge -> cycle.

# INVARIANTS:
# - Each node is UNVISITED, VISITING, or VISITED.
# - A cycle is detected if a VISITING node is revisited on the current path.
# - Fully explored nodes become VISITED and are skipped later.

# COMMON MISTAKES:
# - Using a single visited set (works for undirected, not directed).
# - Forgetting to reset/track the VISITING state (recursion stack).
# - Not iterating over all nodes for disconnected graphs.
# - Misreading edge direction when building the graph.

# TIME & SPACE:
# - Time: O(V + E).
# - Space: O(V) for the recursion stack and state array.

# RELATED PROBLEMS:
# - Course Schedule (LC 207)
# - Course Schedule II (LC 210)
# - Find Eventual Safe States (LC 802)
# - Alien Dictionary (LC 269)
# - Network Delay Time (LC 743)

import heapq


# EXAMPLE: Course Schedule - can all courses be finished (is the graph acyclic)?
def can_finish(num_courses: int, prerequisites: list[list[int]]) -> bool:
    graph: list[list[int]] = [[] for _ in range(num_courses)]
    for course, prereq in prerequisites:
        graph[prereq].append(course)

    UNVISITED, VISITING, VISITED = 0, 1, 2
    state = [UNVISITED] * num_courses

    def has_cycle(course: int) -> bool:
        if state[course] == VISITING:
            return True   # cycle detected
        if state[course] == VISITED:
            return False  # already fully explored

        state[course] = VISITING
        for neighbor in graph[course]:
            if has_cycle(neighbor):
                return True
        state[course] = VISITED
        return False

    for course in range(num_courses):
        if has_cycle(course):
            return False
    return True


# EXAMPLE: Network Delay Time (Dijkstra from source k over a directed weighted graph)
def network_delay_time(times: list[list[int]], n: int, k: int) -> int:
    graph: dict[int, list[tuple[int, int]]] = {i: [] for i in range(1, n + 1)}
    for u, v, w in times:
        graph[u].append((v, w))

    dist: dict[int, int] = {}
    pq: list[tuple[int, int]] = [(0, k)]  # (time, node)

    while pq:
        time, node = heapq.heappop(pq)
        if node in dist:
            continue
        dist[node] = time
        for nei, w in graph[node]:
            if nei not in dist:
                heapq.heappush(pq, (time + w, nei))

    return max(dist.values()) if len(dist) == n else -1


if __name__ == "__main__":
    print(can_finish(2, [[1, 0]]))            # True
    print(can_finish(2, [[1, 0], [0, 1]]))    # False
    print(network_delay_time([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2))  # 2
