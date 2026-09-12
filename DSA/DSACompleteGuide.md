# Complete DSA Pattern Guide

## 📑 Table of Contents

1. [Array](#1-array) — Two Pointers, Sliding Window, Prefix/Suffix, Kadane's, Exactly K Trick
2. [Dynamic Programming](#2-dynamic-programming) — 1D, 2D, Knapsack, Partition, String DP, LIS, Bitmask DP, Rerooting DP
3. [Hash Table](#3-hash-table) — O(1) Lookup, Frequency, Complement Search
4. [Segment Tree](#35-segment-tree-advanced-data-structure-) — Range Queries with Updates
5. [DFS](#4-dfs---depth-first-search) — Recursive, Iterative, Tree Traversals, Matrix, Cycle Detection, Topological Sort
6. [BFS](#5-bfs---breadth-first-search) — Level Order, Shortest Path, Multi-Source BFS
7. [Graph](#6-graph) — Dijkstra, Bellman-Ford, Floyd-Warshall, Topological Sort, Union-Find, MST, SCC
8. [String](#7-string) — KMP, Rabin-Karp, Suffix Trie, Manacher's
9. [Tree](#8-tree) — DFS Traversals, BFS Level Order
10. [Binary Search](#9-binary-search) — Standard, On Answer, Rotated Array
11. [Sorting](#10-sorting) — QuickSort, MergeSort, QuickSelect
12. [Stack](#11-stack) — Monotonic Stack, Monotonic Deque
13. [Greedy](#12-greedy) — Intervals, Jump Game
14. [Linked List](#13-linked-list) — Reverse, Cycle Detection, Merge
15. [Backtracking](#14-backtracking) — Permutations, Combinations, N-Queens
16. [Math](#15-math) — GCD, Fast Exponentiation
17. [Heap / Priority Queue](#16-heap--priority-queue) — Top K, Running Median
18. [Design](#17-design) — LRU Cache, Trie
19. [Bit Manipulation](#18-bit-manipulation) — XOR Tricks, Subset Generation

📁 See also: [DSAQuickLookup.md](DSAQuickLookup.md) for keyword → pattern mapping

---

## 🎯 CORE PATTERNS

### 1. Array

- Sort: O(n log n)

1. **Two Pointers (same/opposite direction)**
   - Fast/slow for cycle detection
   - Left/right for two sum, palindrome
   
2. **Sliding Window**
   - Fixed size: Sum/average of k elements
   - Variable: Longest substring with constraint 🔖
   
3. **Prefix/Suffix Arrays**
   - Range sum queries: O(1) after O(n) preprocessing
   - Product except self: prefix × suffix
   
4. **In-place Manipulation**
   - Use array itself to mark visited (negative, modulo)
   - Swap elements instead of creating new array
   
5. **Kadane's Algorithm**
   - Maximum subarray sum
   - Track: max_ending_here, max_so_far

**Sample Problems:** Two Sum, 3Sum, Container With Most Water, Product of Array Except Self, Maximum Subarray

Exactly K trick:
```python
# Problem: Count subarrays with EXACTLY k distinct elements
# Trick: exactly(k) = at_most(k) - at_most(k-1)
# Note: This approach only works if all nums[i] >= 0 (non-negative integers).
def exactly_k(nums, k):
    return at_most_k(nums, k) - at_most_k(nums, k - 1)


def at_most_k(nums, k):
    freq = {}
    left = 0
    count = 0

    for right in range(len(nums)):
        freq[nums[right]] = freq.get(nums[right], 0) + 1

        while len(freq) > k:
            freq[nums[left]] -= 1
            if freq[nums[left]] == 0:
                del freq[nums[left]]
            left += 1

        count += right - left + 1  # all subarrays ending at right

    return count
```

**Sample Problems:** Subarrays with K Distinct, Count Number of Nice Subarrays, Binary Subarrays With Sum, Number of Substrings Containing All Three Characters, Longest Substring with At Most K Distinct Characters

---

### 2. Dynamic Programming

**What it is:** Breaking problems into overlapping subproblems, caching results

**Mental Model:** "If I solve this for smaller inputs, can I combine those solutions?"

**DP Decision Framework:**
1. **Can I break it into subproblems?** (Optimal substructure)
2. **Do subproblems overlap?** (Need memoization)
3. **What changes between states?** (Define DP state)
4. **How do I combine subproblem results?** (Recurrence relation)
5. **What are base cases?** (Trivial solutions)

**DP Categories:**

**A. 1D DP (Linear)**
```python
# Pattern: dp[i] = answer for first i elements
# Examples: Climbing Stairs, House Robber, Decode Ways

# Template
dp = [0] * (n + 1)
dp[0] = base_case
for i in range(1, n + 1):
    dp[i] = recurrence(dp[i - 1], dp[i - 2], ...)
```

**B. 2D DP (Grid/Two Sequences)**
```python
# Pattern: dp[i][j] = answer for first i of A, first j of B
# Examples: LCS, Edit Distance, Unique Paths

# Template
dp = [[0] * (n + 1) for _ in range(m + 1)]
for i in range(m + 1):
    for j in range(n + 1):
        if i == 0 or j == 0:
            dp[i][j] = base_case
        else:
            dp[i][j] = recurrence(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
```

**C. Knapsack Variations**
- **0/1 Knapsack:** Each item once
- **Unbounded:** Items unlimited
- **Subset Sum:** Can we make target?
- **Partition:** Divide into equal sum subsets

```python
# 0/1 Knapsack Template
dp = [[0] * (W + 1) for _ in range(n + 1)]
for i in range(1, n + 1):
    for w in range(W + 1):
        if weight[i - 1] <= w:
            dp[i][w] = max(
                dp[i - 1][w],                                # don't take
                dp[i - 1][w - weight[i - 1]] + value[i - 1],  # take
            )
        else:
            dp[i][w] = dp[i - 1][w]
```

**D. Partition DP (Interval)**
```python
# Pattern: Try all split points
# Examples: MCM, Burst Balloons, Palindrome Partitioning

for length in range(2, n + 1):
    for i in range(n - length + 1):
        j = i + length - 1
        dp[i][j] = float("inf")
        for k in range(i, j):
            dp[i][j] = min(dp[i][j], dp[i][k] + dp[k + 1][j] + cost(i, k, j))
```

**E. String DP**
- Longest Common Subsequence (LCS)
- Edit Distance (Levenshtein)
- Longest Palindromic Subsequence
- Wildcard/Regex Matching

**E.5. [Longest Increasing Subsequence (LIS)](algorithms/array/lis.py)** ⭐

**Approaches:**
1. **DP:** O(n²) time, O(n) space
2. **DP + Binary Search:** O(n log n) time, O(n) space ⭐

**Optimized Binary Search Solution:**
```python
def length_of_lis(nums):
    # tails[i] = smallest possible tail for increasing subsequence of length i+1
    # e.g. tails = [2, 5, 7] means:
    #   length-1 subsequence ends with 2
    #   length-2 subsequence ends with 5
    #   length-3 subsequence ends with 7
    tails = []

    for num in nums:
        # binary search: find first tail >= num (where num "fits")
        lo, hi = 0, len(tails)
        while lo < hi:
            mid = (lo + hi) // 2
            if tails[mid] < num:
                lo = mid + 1
            else:
                hi = mid

        # lo == len(tails) -> num larger than all tails -> extends LIS
        # lo < len(tails)  -> replace tails[lo] (smaller tail = better for future)
        if lo == len(tails):
            tails.append(num)
        else:
            tails[lo] = num

    # length of tails = length of LIS
    return len(tails)
```

**Key Insight:** 
- `tails` array maintains smallest ending value for each subsequence length
- Binary search finds where current element fits
- If element is largest seen, it extends LIS (append)
- Otherwise, replace a larger tail to keep better options for future elements

**DP Approach (for reference):**
```python
# O(n^2) solution
dp = [1] * len(nums)
for i in range(1, len(nums)):
    for j in range(i):
        if nums[j] < nums[i]:
            dp[i] = max(dp[i], dp[j] + 1)
return max(dp)
```

**Variations:**
- Longest Decreasing Subsequence (reverse logic)
- Number of LIS (count DP)
- Print actual LIS (backtrack with parent pointers)

**F. DP on Trees**
- Maximum path sum
- Diameter of tree
- House Robber III

**G. Bitmask DP (State Compression)** ⭐
- Traveling Salesman Problem (TSP)
- Subset DP with constraints
- Visiting subsets of items

```python
# Pattern: dp[mask][i] = result when visiting subset 'mask' ending at node i
# TSP Example: Minimum cost to visit all cities starting from city 0
dp = [[float("inf")] * n for _ in range(1 << n)]
dp[1][0] = 0  # start from city 0

for mask in range(1, 1 << n):
    for u in range(n):
        if not (mask & (1 << u)):      # u not in mask
            continue
        if dp[mask][u] == float("inf"):
            continue
        for v in range(n):
            if mask & (1 << v):        # v already visited
                continue
            new_mask = mask | (1 << v)
            dp[new_mask][v] = min(dp[new_mask][v], dp[mask][u] + dist[u][v])
```



**Rerooting DP (Tree DP Advanced)**
- Efficiently computes DP values for all possible roots (e.g., subtree sums, distances).
- Two DFS passes:
  1. Bottom-up: Compute DP for each subtree.
  2. Top-down: Reroot and update answers for all nodes.

```python
# Example: Minimum Edge Reversals to Make All Paths Lead to Node 0
def min_edge_reversals(n, edges):
    # Rerooting DP Pattern
    # 1. DFS from root (node 0) to calculate base answer
    # 2. Reroot DFS to propagate answers to all nodes
    #
    # Key: When moving root parent -> child:
    #   Forward edge (cost=0) -> becomes backward (+1)
    #   Backward edge (cost=1) -> becomes forward (-1)

    # Build graph: (neighbor, cost)
    # cost=0: original direction, cost=1: reversed direction
    graph = [[] for _ in range(n)]
    for u, v in edges:
        graph[u].append((v, 0))  # u -> v forward
        graph[v].append((u, 1))  # v -> u backward

    dp = [0] * n

    # DFS1: reversals when node 0 is root
    def calculate_root(node, parent):
        reversals = 0
        for nei, cost in graph[node]:
            if nei == parent:
                continue
            reversals += cost + calculate_root(nei, node)
        return reversals

    # DFS2: reroot to compute for all nodes
    def reroot(node, parent):
        for nei, cost in graph[node]:
            if nei == parent:
                continue
            dp[nei] = dp[node] + (1 if cost == 0 else -1)
            reroot(nei, node)

    dp[0] = calculate_root(0, -1)
    reroot(0, -1)
    return dp
```
- **Applications:** Subtree queries, sum of distances, etc.  **Time:** O(n)



**Common Mistakes:**
- Wrong iteration order (compute dependencies first!)
- Not handling base cases
- Forgetting to consider "don't take" option
- Space complexity when it can be optimized

---

### 3. Hash Table

**What it is:** Key-value pairs with O(1) average lookup

**Mental Model:** "Trade space for time - sacrifice memory to gain speed"

**When to Use:**
- Need fast lookup/existence check
- Count frequency
- Detect duplicates
- Group by property
- Complement search (Two Sum pattern)

**Hash Table vs Array:**
- Use array/list when keys are 0 to n (frequency of characters, numbers in range)
- Use dict when keys are arbitrary or large range

**Sample Problems:** Two Sum, Subarray Sum Equals K, Group Anagrams, Longest Substring Without Repeating Characters

---

### 3.5. Segment Tree (Advanced Data Structure) ⭐

**What it is:** Binary tree built on array segments for fast range queries and updates

**When to Use:**
- Range min/max/sum queries with updates
- Point and range update queries
- Need O(log n) per operation

```python
# Segment Tree - O(n) build, O(log n) query/update (Sum example)
class SegmentTree:
    def __init__(self, arr):
        self.n = len(arr)
        self.tree = [0] * (4 * self.n)
        self.build(arr, 0, 0, self.n - 1)

    def build(self, arr, node, start, end):
        if start == end:
            self.tree[node] = arr[start]
        else:
            mid = (start + end) // 2
            self.build(arr, 2 * node + 1, start, mid)
            self.build(arr, 2 * node + 2, mid + 1, end)
            self.tree[node] = self.tree[2 * node + 1] + self.tree[2 * node + 2]

    def query(self, node, start, end, l, r):
        if r < start or end < l:
            return 0
        if l <= start and end <= r:
            return self.tree[node]
        mid = (start + end) // 2
        return (self.query(2 * node + 1, start, mid, l, r)
                + self.query(2 * node + 2, mid + 1, end, l, r))

    def range_query(self, l, r):
        return self.query(0, 0, self.n - 1, l, r)


seg = SegmentTree([1, 2, 3, 4, 5])
print(seg.range_query(1, 3))  # sum of elements 1-3 = 9
```

**Time:** Build O(n), Query O(log n), Update O(log n)  
**Space:** O(n)  
**Alternatives:** Fenwick Tree (simpler), Sparse Table (O(1) queries, no updates)

See: [Segment Tree](data-structures/tree/segment_tree.py)

---

### 4. DFS - Depth First Search

**What it is:** Explore as far as possible before backtracking

**Mental Model:** "Go deep first, use stack or recursion"

**When to Use:**
- Tree/graph traversal
- Path finding (all paths)
- Cycle detection
- Topological sort
- Backtracking
- Connected components

**DFS Implementations:**

**A. Recursive (Most Common)**
```python
def dfs(node, visited, graph):
    if node in visited:
        return
    visited.add(node)

    # Process node (preorder)

    for neighbor in graph[node]:
        dfs(neighbor, visited, graph)

    # Process node (postorder)
```

**B. Iterative with Stack**
```python
def dfs(start, graph):
    stack = [start]
    visited = {start}

    while stack:
        node = stack.pop()

        # Process node

        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                stack.append(neighbor)
```

**C. DFS for Trees (Inorder, Preorder, Postorder)**
```python
# Inorder (Left, Root, Right) - gives sorted for BST
def inorder(root, result=None):
    if result is None:
        result = []
    if not root:
        return result
    inorder(root.left, result)
    result.append(root.val)
    inorder(root.right, result)
    return result


# Preorder (Root, Left, Right)
def preorder(root, result=None):
    if result is None:
        result = []
    if not root:
        return result
    result.append(root.val)
    preorder(root.left, result)
    preorder(root.right, result)
    return result


# Postorder (Left, Right, Root)
def postorder(root, result=None):
    if result is None:
        result = []
    if not root:
        return result
    postorder(root.left, result)
    postorder(root.right, result)
    result.append(root.val)
    return result
```

**D. DFS for Matrix (4-directional)**
```python
def dfs(grid, row, col, visited):
    if row < 0 or row >= m or col < 0 or col >= n:
        return
    if visited[row][col] or grid[row][col] == 0:
        return

    visited[row][col] = True

    # 4 directions
    dfs(grid, row + 1, col, visited)  # down
    dfs(grid, row - 1, col, visited)  # up
    dfs(grid, row, col + 1, visited)  # right
    dfs(grid, row, col - 1, visited)  # left
```

**E. Cycle Detection (Directed Graph)** ⭐
```python
# Use 3 colors: 0=white (unvisited), 1=gray (in progress), 2=black (done)
def has_cycle(graph, n):
    color = [0] * n

    def dfs(node):
        color[node] = 1  # in-progress
        for neighbor in graph[node]:
            if color[neighbor] == 1:      # back edge = cycle
                return True
            if color[neighbor] == 0 and dfs(neighbor):
                return True
        color[node] = 2  # done
        return False

    for i in range(n):
        if color[i] == 0 and dfs(i):
            return True
    return False
```

**F. Topological Sort (DFS-based)** ⭐
```python
def topological_sort(graph, n):
    visited = [False] * n
    stack = []

    def dfs(node):
        visited[node] = True
        for neighbor in graph[node]:
            if not visited[neighbor]:
                dfs(neighbor)
        stack.append(node)  # postorder

    for i in range(n):
        if not visited[i]:
            dfs(i)

    return stack[::-1]
```

**Time Complexity:** O(V + E) for graphs, O(n) for trees  
**Space Complexity:** O(h) for recursion stack where h = height

**Sample Problems:** Word Search, Binary Tree Inorder Traversal, Validate BST, Number of Islands

---

### 5. BFS - Breadth First Search

**What it is:** Explore level by level using queue

**Mental Model:** "Process all neighbors first before going deeper"

**When to Use:**
- Shortest path (unweighted graph)
- Level order traversal
- Minimum steps/distance
- Nearest neighbor
- Check if reachable

**BFS Template:**
```python
from collections import deque

def bfs(start, graph):
    queue = deque([start])
    visited = {start}
    level = 0

    while queue:
        size = len(queue)

        # Process all nodes at the current level
        for _ in range(size):
            node = queue.popleft()

            # Process node
            if is_target(node):
                return level

            for neighbor in graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        level += 1

    return -1  # not found
```

**BFS for Trees (Level Order):**
```python
from collections import deque

def level_order(root):
    if not root:
        return []

    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)
        current_level = []

        for _ in range(level_size):
            node = queue.popleft()
            current_level.append(node.val)

            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        result.append(current_level)

    return result
```

**BFS for Matrix (Shortest Path):**
```python
from collections import deque

def shortest_path(grid):
    m, n = len(grid), len(grid[0])
    queue = deque([(0, 0, 0)])  # (row, col, distance)
    visited = [[False] * n for _ in range(m)]
    visited[0][0] = True

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    while queue:
        row, col, dist = queue.popleft()

        if row == m - 1 and col == n - 1:
            return dist

        for dr, dc in dirs:
            nr, nc = row + dr, col + dc
            if 0 <= nr < m and 0 <= nc < n and not visited[nr][nc] and grid[nr][nc] == 1:
                visited[nr][nc] = True
                queue.append((nr, nc, dist + 1))

    return -1
```

**Multi-Source BFS:**
```python
from collections import deque

# Start from multiple sources simultaneously
# Example: Rotting Oranges
def bfs_multi_source(grid):
    queue = deque()

    # Add all sources to the queue
    for i in range(m):
        for j in range(n):
            if is_source(i, j):
                queue.append((i, j, 0))

    # Regular BFS
    while queue:
        row, col, time = queue.popleft()
        # process neighbors
```

**BFS vs DFS:**
- **BFS:** Shortest path, level order, minimum steps
- **DFS:** All paths, backtracking, topological sort, memory efficient

**Sample Problems:** Binary Tree Level Order, Course Schedule, Rotting Oranges, Word Ladder

---

### 6. Graph

**What it is:** Nodes (vertices) connected by edges

**Mental Model:** "Network of relationships"

**Graph Representations:**

**A. Adjacency List (Most Common)**
```python
from collections import defaultdict

# For directed graph
graph = defaultdict(list)
graph[node] = [nei1, nei2]

# For undirected, add both directions
def add_edge(u, v):
    graph[u].append(v)
    graph[v].append(u)
```

**B. Adjacency Matrix**
```python
# For weighted graph
graph = [[float("inf")] * n for _ in range(n)]
for i in range(n):
    graph[i][i] = 0

# Add edge
graph[u][v] = weight
```

**C. Edge List**
```python
# For MST, Union-Find 🏷️
edges = [[u1, v1, w1], [u2, v2, w2], ...]
```

**Core Graph Algorithms:**

**1. [Dijkstra's Algorithm](algorithms/graph/dijkstra.py) (Shortest Path, Non-negative Weights)** ⭐
```python
import heapq

def dijkstra(graph, start, n):
    dist = [float("inf")] * n
    dist[start] = 0

    # Min heap: (distance, node)
    pq = [(0, start)]

    while pq:
        d, u = heapq.heappop(pq)

        if d > dist[u]:      # already processed
            continue

        for v, weight in graph[u]:
            if dist[u] + weight < dist[v]:
                dist[v] = dist[u] + weight
                heapq.heappush(pq, (dist[v], v))

    return dist
```

**2. [Bellman-Ford](algorithms/graph/bellman_ford.py) (Handles Negative Weights)** ⭐
```python
def bellman_ford(edges, n, start):
    dist = [float("inf")] * n
    dist[start] = 0

    # Relax all edges n-1 times
    for _ in range(n - 1):
        for u, v, w in edges:
            if dist[u] != float("inf") and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w

    # Check for negative cycles
    for u, v, w in edges:
        if dist[u] != float("inf") and dist[u] + w < dist[v]:
            return None  # negative cycle exists

    return dist
```

**3. [Floyd-Warshall](algorithms/graph/floyd_warshall.py) (All-Pairs Shortest Path)** ⭐
```python
def floyd_warshall(edges, n):
    dist = [[float("inf")] * n for _ in range(n)]

    # Initialize
    for i in range(n):
        dist[i][i] = 0
    for u, v, w in edges:
        dist[u][v] = w

    # Dynamic programming: try all intermediate nodes
    for k in range(n):
        for i in range(n):
            for j in range(n):
                dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

    return dist
```

**4. [Topological Sort](algorithms/graph/topological_sort.py) (DAG)** ⭐

Two methods:
1. DFS-based (postorder)
2. BFS-based (Kahn's algorithm with indegrees)

```python
from collections import deque

# Kahn's Algorithm (BFS-based)
def topological_sort(graph, n):
    indegree = [0] * n

    # Calculate indegrees
    for u in range(n):
        for v in graph[u]:
            indegree[v] += 1

    # Queue with 0 indegree
    queue = deque(i for i in range(n) if indegree[i] == 0)

    result = []
    while queue:
        u = queue.popleft()
        result.append(u)

        for v in graph[u]:
            indegree[v] -= 1
            if indegree[v] == 0:
                queue.append(v)

    return result if len(result) == n else []  # empty if cycle
```

**5. Detect Cycle (Undirected Graph)**
```python
def has_cycle_undirected(graph, n):
    visited = [False] * n

    def dfs(node, parent):
        visited[node] = True
        for neighbor in graph[node]:
            if not visited[neighbor]:
                if dfs(neighbor, node):
                    return True
            elif neighbor != parent:
                return True  # visited neighbor that's not parent = cycle
        return False

    for i in range(n):
        if not visited[i] and dfs(i, -1):
            return True
    return False
```

**6. [Union-Find](algorithms/graph/union_find.py) (Disjoint Set)** ⭐

- **Time Complexity:** O(α(n)) ≈ O(1) with path compression + union by rank

**7. [Bipartite Check](algorithms/graph/bipartite.py) (Check if Graph is Bipartite)** ⭐

**8. [Kruskal's Algorithm](algorithms/graph/kruskals.py) (Minimum Spanning Tree)** ⭐

**9. [Prim's Algorithm](algorithms/graph/prims.py) (Minimum Spanning Tree)** ⭐

**10. [Kosaraju's Algorithm](algorithms/graph/kosaraju.py) (Strongly Connected Components)** ⭐

**11. [Tarjan's Algorithm](algorithms/graph/tarjan.py) (Strongly Connected Components)** ⭐

**When to Use Which Algorithm:** ⭐
- **Shortest Path (unweighted):** BFS
- **Shortest Path (positive weights):** Dijkstra's
- **Shortest Path (any weights):** Bellman-Ford
- **All-pairs shortest path:** Floyd-Warshall
- **Cycle detection:** DFS or Union-Find
- **Topological ordering:** DFS or Kahn's algorithm
- **Strongly connected components:** Kosaraju's or Tarjan's

---

### 7. String

**Common Patterns:**

**A. [KMP](algorithms/string/kmp.py) (Pattern Matching)**

**When to use:**
- Search for a pattern in a string efficiently
- Avoid re-checking characters after a mismatch
- Find all occurrences of a pattern

**B. [Rabin-Karp](algorithms/string/rabin_karp.py) (Rolling Hash)**

**When to use:**
- Search for a pattern in a string using hashing
- Find all occurrences of a pattern
- Handle multiple pattern searches efficiently

**String Tricks:**
- Use ASCII for fast frequency: `freq[ord(char) - ord('a')] += 1`
- KMP for pattern matching (O(n + m))
- Rolling hash for substring comparison (O(n + m) average)

**C. [Suffix Trie](patterns/suffix_trie.py) (Counting Distinct Substrings)**

**When to use:**
- Count distinct substrings in a string
- Store and query all suffixes efficiently
- String processing with substring/pattern queries

**Approaches:**
```python
# 1. Brute Force: O(n^3) time, O(n^2) space
#    - Generate all substrings, use a set for uniqueness

# 2. Suffix Trie: O(n^2) time, O(n^2) space
#    - Insert all suffixes into a trie
#    - Each new node = a new distinct substring
#    - Count = number of nodes created

# 3. Suffix Array + LCP: O(n log n) time, O(n) space  (optimal)
#    - Build suffix array (sorted suffixes)
#    - Compute longest common prefix between adjacent suffixes
#    - distinct_count = sum(suffix_length - lcp_with_previous)
```

**Key Insight:** Each node in a suffix trie represents a unique substring. By sorting suffixes and using LCP, we eliminate duplicates efficiently.

**Sample Problems:** Count Distinct Substrings, Find Longest Repeated Substring, Suffix Array Construction

**Time Complexity:**
- Naive: O(n * m)
- KMP: O(n + m)
- Rabin-Karp: O(n + m) average
- Suffix Trie: O(n²)
- Suffix Array + LCP: O(n log n)

**Sample Problems:** Longest Substring Without Repeating Characters, Group Anagrams, Valid Palindrome II

**D. Manacher's Algorithm (Longest Palindromic Substring)** ⭐

**When to use:**
- Find longest palindrome in O(n) time
- More elegant than center expansion approach

```python
# Transform "abc" -> "#a#b#c#" to handle both odd/even palindromes
transformed = "#" + "#".join(s) + "#"
p = [0] * len(transformed)  # radius at each position
center = right = 0

for i in range(1, len(transformed) - 1):
    mirror = 2 * center - i
    if i < right:
        p[i] = min(right - i, p[mirror])

    while (i + p[i] + 1 < len(transformed)
           and transformed[i + p[i] + 1] == transformed[i - p[i] - 1]):
        p[i] += 1

    if i + p[i] > right:
        center = i
        right = i + p[i]
# Extract result: start = (max_center_index - max_len) // 2, length = max_len
```

**Time:** O(n), **Space:** O(n). Far superior to O(n²) center expansion.

---

### 8. Tree

**What it is:** Hierarchical data structure with nodes connected by edges (no cycles)

**Mental Model:** "Recursive by nature - solve for subtrees, combine at root"

**Tree Traversals:**

**A. DFS Traversals**
```python
# Recursive
def inorder(root, result=None):
    if result is None:
        result = []
    if not root:
        return result
    inorder(root.left, result)
    result.append(root.val)
    inorder(root.right, result)
    return result


# Iterative Inorder
def inorder_iterative(root):
    result = []
    stack = []
    curr = root

    while curr or stack:
        while curr:
            stack.append(curr)
            curr = curr.left
        curr = stack.pop()
        result.append(curr.val)
        curr = curr.right

    return result
```

**B. BFS (Level Order)**
```python
from collections import deque

def level_order(root):
    if not root:
        return []
    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)
        current_level = []

        for _ in range(level_size):
            node = queue.popleft()
            current_level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        result.append(current_level)

    return result
```

See also: [Tree Patterns](patterns/tree_patterns.py), [BST](data-structures/tree/bst.py)

---

### 9. Binary Search

**What it is:** Eliminate half the search space each iteration

**Mental Model:** "Keep halving until you find the answer"

**When to Use:**
- Sorted array
- Find first/last occurrence
- Search in rotated array
- Minimize maximum / maximize minimum (binary search on answer)

**Templates:**

**A. Standard Binary Search**
```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = left + (right - left) // 2

        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1
```

**B. Binary Search on Answer**
```python
# Example: Aggressive Cows, Minimum Days to Make Bouquets
def binary_search_on_answer(arr, k):
    left, right = 0, max(arr)
    result = -1

    def is_feasible(mid):
        # Check if answer 'mid' is possible; return True/False
        ...

    while left <= right:
        mid = left + (right - left) // 2

        if is_feasible(mid):
            result = mid
            right = mid - 1  # try to minimize
        else:
            left = mid + 1

    return result
```

**C. Search in Rotated Array**
```python
def search(nums, target):
    left, right = 0, len(nums) - 1

    while left <= right:
        mid = left + (right - left) // 2

        if nums[mid] == target:
            return mid

        # Check which half is sorted
        if nums[left] <= nums[mid]:
            # Left half is sorted
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            # Right half is sorted
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1

    return -1
```

**Common Mistakes:**
- Wrong loop condition: `left <= right` vs `left < right`
- Wrong pointer update: `mid - 1` vs `mid` vs `mid + 1`
- (In Python, integer overflow is a non-issue, but `left + (right - left) // 2` is still a good habit.)

See also: [Binary Search patterns](patterns/binary_search.py)

---

### 10. Sorting

**Key Sorting Algorithms:**

**A. [QuickSort](algorithms/sorting/quick_sort.py)**
```python
def quick_sort(arr, low=0, high=None):
    if high is None:
        high = len(arr) - 1
    if low < high:
        pi = partition(arr, low, high)
        quick_sort(arr, low, pi - 1)
        quick_sort(arr, pi + 1, high)
    return arr


def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1

    for j in range(low, high):
        if arr[j] < pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1
```

[quickSelect](algorithms/sorting/quick_select.py) (Find k-th smallest) ⭐

**B. [MergeSort](algorithms/sorting/merge_sort.py)**
```python
def merge_sort(arr):
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])

    return merge(left, right)


def merge(left, right):
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result
```

**When to Sort:**
- Two Sum → Sort first, use two pointers
- Intervals → Sort by start time, then merge
- Anagrams → Sort characters to group
- Find duplicates → Sort, then linear scan

---

### 11. Stack

**When to Use:**
- Matching parentheses/brackets
- Evaluate expressions
- Undo operations
- Function call simulation

Monotonic Stack:
**When to Use:**
- Next greater/smaller element
- Stock span
- Largest rectangle in histogram

**Example: Next Greater Element**
```python
def next_greater_element(nums):
    result = [-1] * len(nums)
    stack = []  # indices

    for i in range(len(nums)):
        while stack and nums[i] > nums[stack[-1]]:
            idx = stack.pop()
            result[idx] = nums[i]
        stack.append(i)

    return result
```

**Monotonic Deque Extension** ⭐

**When to Use:**
- Sliding window min/max queries
- Stock price span problems
- Building heights & visibility

```python
from collections import deque

# Sliding Window Maximum - O(n) using a Monotonic Deque
def max_sliding_window(nums, k):
    dq = deque()  # indices, values in decreasing order
    result = []

    for i in range(len(nums)):
        # Remove indices outside the window
        if dq and dq[0] < i - k + 1:
            dq.popleft()

        # Remove smaller elements (maintain decreasing)
        while dq and nums[dq[-1]] < nums[i]:
            dq.pop()

        dq.append(i)

        if i >= k - 1:
            result.append(nums[dq[0]])

    return result  # [1,3,-1,-3,5,3,6,7], k=3 -> [3,3,5,5,6,7]
```

**Key:** Each element added/removed once. Time O(n), Space O(k). Better than using a heap!

See also: [Monotonic Stack](patterns/monotonic_stack.py), [Monotonic Queue](patterns/monotonic_queue.py)

---

### 12. Greedy

**What it is:** Make locally optimal choice at each step

**When to Use:**
- Interval scheduling
- Activity selection
- Huffman coding
- Dijkstra's algorithm

**Key:** Must prove greedy choice property and optimal substructure

**Common Patterns:**
- **Intervals:** Sort by end time, select non-overlapping
- **Array:** Process in order, maintain running state
- **Min/Max:** Sort, pick greedily

**Example: Jump Game**
```python
def can_jump(nums):
    max_reach = 0
    for i in range(len(nums)):
        if i > max_reach:
            return False
        max_reach = max(max_reach, i + nums[i])
    return True
```

See also: [Greedy patterns](patterns/greedy.py), [Intervals](patterns/intervals.py)

---

### 13. Linked List

**Common Operations:**

**A. Reverse**
```python
def reverse_list(head):
    prev, curr = None, head

    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt

    return prev
```

**B. Fast/Slow (Cycle Detection)**
```python
def has_cycle(head):
    slow = fast = head

    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True

    return False
```

**C. Merge Two Sorted Lists**
```python
def merge_two_lists(l1, l2):
    dummy = ListNode(0)
    curr = dummy

    while l1 and l2:
        if l1.val < l2.val:
            curr.next = l1
            l1 = l1.next
        else:
            curr.next = l2
            l2 = l2.next
        curr = curr.next

    curr.next = l1 if l1 else l2
    return dummy.next
```

See also: [Linked List](data-structures/linked-list/linked_list.py)

---

### 14. Backtracking

**What it is:** Explore all possibilities by making choices and undoing them

**Framework:**
```python
def backtrack(state, choices, result):
    if is_complete(state):
        result.append(list(state))
        return

    for choice in choices:
        # Make choice
        state.append(choice)

        # Explore
        backtrack(state, get_next_choices(choice), result)

        # Undo choice
        state.pop()
```

**Common Problems:**
- Permutations
- Combinations
- Subsets
- N-Queens
- Sudoku Solver

**Optimization:**
- Prune early (check validity before recursing)
- Sort input (enables early termination)
- Use visited set

See also: [Backtracking patterns](patterns/backtracking.py)

---

### 15. Math

**Common Patterns:**
- GCD/LCM: Euclidean algorithm
- Prime factorization: Trial division
- Modular arithmetic: (a + b) % m = ((a % m) + (b % m)) % m
- Power: Fast exponentiation O(log n)

**Fast Exponentiation:**
```python
def power(x, n):
    if n == 0:
        return 1
    if n < 0:
        return 1 / power(x, -n)

    if n % 2 == 0:
        half = power(x, n // 2)
        return half * half
    return x * power(x, n - 1)
```

---

### 16. [Heap](data-structures/heap/min_heap.py) / [Priority Queue](data-structures/heap/priority_queue.py)

**What it is:** Complete binary tree with heap property (min-heap or max-heap)

**When to Use:**
- Top K elements
- Kth largest/smallest
- Merge K sorted lists
- Running median
- Dijkstra's algorithm

**Python note:** the stdlib `heapq` module is a MIN-heap. For a max-heap, negate values on push/pop.
The explicit class below is kept for teaching the internals.

**Python Implementation (Min Heap):**
```python
class MinHeap:
    def __init__(self):
        self.heap = []

    def push(self, val):
        self.heap.append(val)
        self._bubble_up(len(self.heap) - 1)

    def pop(self):
        if not self.heap:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()

        minimum = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._bubble_down(0)
        return minimum

    def peek(self):
        return self.heap[0] if self.heap else None

    def size(self):
        return len(self.heap)

    def _bubble_up(self, idx):
        while idx > 0:
            parent = (idx - 1) // 2
            if self.heap[idx] >= self.heap[parent]:
                break
            self.heap[idx], self.heap[parent] = self.heap[parent], self.heap[idx]
            idx = parent

    def _bubble_down(self, idx):
        while True:
            smallest = idx
            left = 2 * idx + 1
            right = 2 * idx + 2

            if left < len(self.heap) and self.heap[left] < self.heap[smallest]:
                smallest = left
            if right < len(self.heap) and self.heap[right] < self.heap[smallest]:
                smallest = right

            if smallest == idx:
                break
            self.heap[idx], self.heap[smallest] = self.heap[smallest], self.heap[idx]
            idx = smallest
```

See also: [Heap Patterns](patterns/heap_patterns.py)

---

### 17. Design

**Common Design Problems:**
- LRU Cache: Hash Map + Doubly Linked List
- LFU Cache: Hash Map + Min Heap + Doubly Linked List
- Trie: Prefix tree for strings
- Design Twitter: Hash Map + Heap
- Circular Queue: Array with head/tail pointers

See also: [LRU Cache](data-structures/design/lru_cache.py), [Trie](data-structures/tree/trie.py)

---

### 18. Bit Manipulation

**Common Operations:**
```python
# Check if ith bit is set
(num & (1 << i)) != 0

# Set ith bit
num | (1 << i)

# Clear ith bit
num & ~(1 << i)

# Toggle ith bit
num ^ (1 << i)

# Clear lowest set bit
num & (num - 1)

# Get lowest set bit
num & -num

# Count set bits
def count_bits(n):
    count = 0
    while n:
        count += 1
        n &= n - 1  # clear lowest set bit
    return count
```

**XOR Properties:**
- a ^ a = 0
- a ^ 0 = a
- a ^ b ^ a = b (useful for finding single number)

**Common Patterns:**
- Find single number: XOR all
- Swap without temp: `a, b = b, a` (Python) or `a ^= b; b ^= a; a ^= b`
- Power of 2: `(n & (n - 1)) == 0`
- Generate subsets: Iterate 0 to 2^n - 1

See also: [Bit Manipulation patterns](patterns/bit_manipulation.py)
