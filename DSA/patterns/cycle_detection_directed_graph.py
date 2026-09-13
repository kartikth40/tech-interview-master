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

# NOTE: This file is the PATTERN applied to a concrete problem (Course Schedule). For the bare
# 3-color cycle-detection algorithm (set-based, generic graph), see
# algorithms/graph/cycle_detection_directed.py. This version uses an int state[] array keyed by
# course index — the same idea, shaped for the LC 207/210 input format.


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


# (Network Delay Time / Dijkstra was moved out of this file — it's a shortest-path problem, not
# cycle detection. See algorithms/graph/dijkstra.py for Dijkstra and its Network Delay Time variant.)


if __name__ == "__main__":
    print(can_finish(2, [[1, 0]]))            # True
    print(can_finish(2, [[1, 0], [0, 1]]))    # False
