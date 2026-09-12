# PATTERN NAME: Depth-First Search (DFS)
# DIFFICULTY: Medium | FREQUENCY: Very High (connected components, backtracking, topo at all companies)

# WHEN TO USE:
# - Traversal of trees or graphs.
# - Backtracking problems (permutations, combinations, N-Queens).
# - Pathfinding, topological sorting, connected components.
# - Examples: Number of Islands, Word Search, Course Schedule.

# CORE IDEA (INTUITION):
# - Explore as far as possible along each branch before backtracking.
# - Use recursion or an explicit stack.
# - Mark nodes visited to avoid cycles and redundant work.

# INVARIANTS:
# - Each node is visited exactly once.
# - The recursion/explicit stack maintains the current path.
# - Backtracking occurs when all neighbors are explored.

# COMMON MISTAKES:
# - Not marking nodes visited (infinite loops).
# - Forgetting to backtrack properly in recursive calls.
# - Not handling disconnected components.
# - Using DFS where BFS is better (shortest path in unweighted graphs).
# - Recursion depth limits on large graphs.

# TIME & SPACE:
# - Time: O(V + E).
# - Space: O(V) for the recursion stack and visited set.

# RELATED PROBLEMS:
# - Number of Provinces (LC 547)
# - Course Schedule IV (LC 1462)
# - Number of Islands (LC 200)
# - Clone Graph (LC 133)
# - Graph Coloring / M-Coloring (classic)


# EXAMPLE: Number of Provinces (connected components in an adjacency matrix)
def find_circle_num(is_connected: list[list[int]]) -> int:
    n = len(is_connected)
    visited = [False] * n
    provinces = 0

    def dfs(city: int) -> None:
        visited[city] = True
        for i in range(n):
            if is_connected[city][i] == 1 and not visited[i]:
                dfs(i)

    for i in range(n):
        if not visited[i]:
            dfs(i)          # explore the whole component
            provinces += 1  # count it as one province

    return provinces


# EXAMPLE: Course Schedule IV (transitive prerequisites via memoized DFS)
def check_if_prerequisite(num_courses: int, prerequisites: list[list[int]],
                          queries: list[list[int]]) -> list[bool]:
    graph: list[list[int]] = [[] for _ in range(num_courses)]
    for pre, course in prerequisites:
        graph[course].append(pre)

    pre_map: dict[int, set[int]] = {}

    def dfs(course: int) -> set[int]:
        if course in pre_map:
            return pre_map[course]
        pre_set: set[int] = set()
        for nei in graph[course]:
            pre_set.add(nei)
            pre_set |= dfs(nei)  # transitive prerequisites
        pre_map[course] = pre_set
        return pre_set

    for i in range(num_courses):
        dfs(i)

    return [pre in pre_map.get(course, set()) for pre, course in queries]


# EXAMPLE: M-Coloring Problem (DFS + backtracking)
def graph_coloring(v: int, edges: list[list[int]], m: int) -> bool:
    graph: list[list[int]] = [[] for _ in range(v)]
    for u, w in edges:
        graph[u].append(w)
        graph[w].append(u)

    colors = [-1] * v

    def is_safe(node: int, col: int) -> bool:
        return all(colors[nei] != col for nei in graph[node])

    def backtrack(node: int) -> bool:
        if node == v:
            return True
        for col in range(m):
            if is_safe(node, col):
                colors[node] = col
                if backtrack(node + 1):
                    return True
                colors[node] = -1
        return False

    return backtrack(0)


if __name__ == "__main__":
    print(find_circle_num([[1, 1, 0], [1, 1, 0], [0, 0, 1]]))  # 2
    print(check_if_prerequisite(2, [[1, 0]], [[0, 1], [1, 0]]))  # [False, True]
    print(graph_coloring(4, [[0, 1], [1, 2], [2, 3], [3, 0]], 2))  # True
