# Complete DSA Pattern Guide

> **How to use this guide:** this is the *intuition + when-to-use + decision* layer. Full, runnable
> implementations live in the linked `.py` files - open those to study or run the code
> (`python <file>`). For instant keyword → pattern lookup, see [DSAQuickLookup.md](DSAQuickLookup.md).
> For the *visual* thinking layer (decision flowcharts, the mental web, constraints→complexity),
> see [DSA Mental Models](mental-models.md).

## 📑 Table of Contents

1. [Array](#1-array) - Two Pointers, Sliding Window, Prefix/Suffix, Kadane's
2. [Dynamic Programming](#2-dynamic-programming) - 1D, 2D, Knapsack, Partition, String DP, LIS
3. [Hash Table](#3-hash-table) - O(1) Lookup, Frequency, Complement Search
4. [DFS](#4-dfs) - Recursive/Iterative, Tree Traversals, Matrix, Cycle Detection, Topological Sort
5. [BFS](#5-bfs) - Level Order, Shortest Path, Multi-Source
6. [Graph](#6-graph) - Dijkstra, Bellman-Ford, Topological Sort, Union-Find, MST
7. [String](#7-string) - Pattern Matching (overview)
8. [Tree](#8-tree) - Traversals, common recursive patterns
9. [Binary Search](#9-binary-search) - Standard, On Answer, Rotated Array
10. [Sorting](#10-sorting) - QuickSort, MergeSort, QuickSelect
11. [Stack](#11-stack) - Monotonic Stack, Monotonic Deque
12. [Greedy](#12-greedy) - Intervals, Jump Game
13. [Linked List](#13-linked-list) - Reverse, Cycle Detection, Merge
14. [Backtracking](#14-backtracking) - Permutations, Combinations, Subsets, N-Queens
15. [Heap / Priority Queue](#15-heap--priority-queue) - Top K, Running Median
16. [Bit Manipulation](#16-bit-manipulation) - XOR Tricks, Subset Generation
16.5. [Matrix / Grid](#165-matrix--grid) - Islands, Spiral, Rotate, Sorted-Matrix Search
16.6. [Design a Data Structure](#166-design-a-data-structure) - LRU, Min Stack, MedianFinder, Trie
17. [Advanced / Rarely Asked](#17-advanced--rarely-asked-at-sde-2) - Segment Tree, Bitmask DP, Manacher's, SCC, string-matching

---

## 🎯 CORE PATTERNS

### 1. Array

**When to use which technique:**
- **Two Pointers** - sorted-array pair/triplet sum, palindrome, partition. Opposite ends converge, or fast/slow.
- **Sliding Window** - longest/shortest contiguous subarray/substring with a constraint. Expand right, contract left. Trick: *exactly K* = `at_most(k) - at_most(k-1)`.
- **Prefix/Suffix Arrays** - repeated range-sum queries (O(1) after O(n) prep), product-except-self.
- **In-place** - mark visited via sign/modulo, swap instead of allocating.
- **Kadane's** - maximum subarray sum in O(n); track `max_ending_here`, `max_so_far`.

**Files:** [Two Pointers](patterns/two_pointers.py) · [Sliding Window](patterns/sliding_window.py) · [Prefix Sum](patterns/prefix_sum_pattern.py) · [Kadane's](algorithms/array/kadane.py) · [kSum](algorithms/array/k_sum.py)

**Sample Problems:** Two Sum, 3Sum, Container With Most Water, Product of Array Except Self, Maximum Subarray, Subarrays with K Distinct.

---

### 2. Dynamic Programming

**Mental model:** "If I solve smaller inputs, can I combine those solutions?" DP = optimal substructure + overlapping subproblems.

**Decision framework:**
1. Can I break it into subproblems? (optimal substructure)
2. Do subproblems overlap? (memoize)
3. What defines a state? (indices, remaining capacity, flags)
4. What's the recurrence? (how states combine)
5. What are the base cases?

**Categories & the state they track:**
- **1D DP** - `dp[i]` = answer for first `i` elements (Climbing Stairs, House Robber, Decode Ways).
- **2D DP** - `dp[i][j]` = answer for first `i` of A, `j` of B (LCS, Edit Distance, Unique Paths).
- **Knapsack** - 0/1 (each item once, iterate capacity right→left), unbounded (reuse, left→right), subset-sum, partition.
- **Partition/Interval DP** - try all split points `k` in `[i, j)` (MCM, Burst Balloons, Palindrome Partitioning).
- **String DP** - LCS, Edit Distance, Longest Palindromic Subsequence, wildcard matching.
- **LIS** - O(n log n) via patience sorting: keep `tails[]` (smallest tail per length), binary-search the insert point.
- **DP on Trees** - max path sum, diameter, House Robber III (bottom-up return values).

**Common mistakes:** wrong iteration order (compute dependencies first), missing base cases, forgetting the "don't take" option, not optimizing space when only the previous row is needed.

**Files:** [DP Patterns](patterns/dp_patterns.py) · [Climbing Stairs](algorithms/dp/climbing_stairs.py) · [House Robber](algorithms/dp/house_robber.py) · [Coin Change](algorithms/dp/coin_change.py) · [Knapsack](algorithms/dp/knapsack.py) · [LCS](algorithms/dp/lcs.py) · [Edit Distance](algorithms/dp/edit_distance.py) · [Unique Paths](algorithms/dp/unique_paths.py) · [LIS](algorithms/array/lis.py)

---

### 3. Hash Table

**Mental model:** trade space for time. O(1) average lookup.

**When to use:** fast existence check, frequency counting, duplicate detection, grouping by property, complement search (Two Sum pattern).

**Hash table vs array:** use a list when keys are `0..n` (char/number frequency in range); use a dict when keys are arbitrary or a large/sparse range.

**Sample Problems:** Two Sum, Subarray Sum Equals K, Group Anagrams, Longest Substring Without Repeating Characters.

---

### 4. DFS

**Mental model:** go deep first; recursion or an explicit stack. Mark visited to avoid cycles.

**Use for:** tree/graph traversal, all-paths, cycle detection, topological sort, connected components, backtracking.

**Key variants:**
- **Recursive vs iterative (stack).** Recursion is cleaner; use an explicit stack if depth risks the recursion limit.
- **Tree traversals** - inorder (sorted for BST), preorder (serialize), postorder (delete/height).
- **Matrix DFS** - 4-directional flood fill; always bounds-check and mark visited before recursing.
- **Directed cycle detection** - 3-color (white/gray/black); a gray→gray edge is a back edge = cycle.
- **Topological sort (DFS)** - push nodes in postorder, then reverse.

**Complexity:** O(V + E) for graphs, O(n) for trees; O(h) recursion-stack space.

**Files:** [DFS](algorithms/graph/dfs.py) · [DFS Patterns](patterns/dfs_patterns.py) · [Directed Cycle Detection](algorithms/graph/cycle_detection_directed.py) · [Topological Sort](algorithms/graph/topological_sort.py) · [Tree Patterns](patterns/tree_patterns.py)

---

### 5. BFS

**Mental model:** process level by level with a queue. Gives shortest path in an **unweighted** graph.

**Use for:** shortest path (unweighted), level-order traversal, minimum steps/distance, "is it reachable".

**Key variants:**
- **Level-order** - snapshot `len(queue)` at the start of each level.
- **Matrix shortest path** - enqueue `(row, col, dist)`; mark visited on *enqueue*, not dequeue.
- **Multi-source BFS** - seed the queue with all sources at once (Rotting Oranges, nearest-exit).
- **State BFS** - the visited key includes extra state (e.g. `(row, col, remaining_eliminations)`).

**Complexity:** O(V + E) time, O(V) space. Use `collections.deque` (not `list.pop(0)`).

**Files:** [BFS](algorithms/graph/bfs.py) · [BFS Patterns](patterns/bfs_patterns.py)

---

### 6. Graph

**Representations:** adjacency list (most common, sparse), adjacency matrix (dense / O(1) edge lookup / Floyd-Warshall), edge list (MST, Union-Find).

**Algorithm selection (memorize this table):**

| Problem | Algorithm | Time |
|---------|-----------|------|
| Shortest path, unweighted | BFS | O(V+E) |
| Shortest path, non-negative weights | Dijkstra | O((V+E) log V) |
| Shortest path, negative weights / neg-cycle detect | Bellman-Ford | O(VE) |
| Shortest path with a state constraint (e.g. ≤ K stops) | Dijkstra/BFS with state in the heap/queue | - |
| Cycle detection | DFS (3-color for directed) / Union-Find | O(V+E) |
| Topological ordering (DAG) | DFS postorder / Kahn's BFS (indegrees) | O(V+E) |
| Minimum spanning tree | Kruskal (Union-Find) / Prim (heap) | O(E log E) |
| Connected components | DFS / BFS / Union-Find | O(V+E) |

**Dijkstra-with-state** is a high-value variant (common across MAANG): when the answer depends on more than distance (stops used, fuel left), add that dimension to the heap entry - see Cheapest Flights within K Stops in [dijkstra.py](algorithms/graph/dijkstra.py).

**Files:** [Dijkstra](algorithms/graph/dijkstra.py) · [Bellman-Ford](algorithms/graph/bellman_ford.py) · [Topological Sort](algorithms/graph/topological_sort.py) · [Union-Find](algorithms/graph/union_find.py) · [Kruskal's](algorithms/graph/kruskals.py) · [Prim's](algorithms/graph/prims.py) · [Bipartite](algorithms/graph/bipartite.py) · [Undirected Cycle](algorithms/graph/cycle_detection_undirected.py)

---

### 7. String

**When to reach for what:**
- **Frequency/hashing** - anagrams, "contains all chars"; a `Counter` or fixed-size array is usually enough.
- **Sliding window** - longest substring problems (see Array §1).
- **Two pointers** - palindrome checks, reversal.

Advanced pattern-matching algorithms (KMP, Rabin-Karp, suffix structures, Manacher's) are **rarely required at SDE-2** - see [§17 Advanced](#17-advanced--rarely-asked-at-sde-2).

**Sample Problems:** Longest Substring Without Repeating Characters, Group Anagrams, Valid Palindrome II.

---

### 8. Tree

**Mental model:** recursive by nature - solve subtrees, combine at the root. Base case: a null node returns a neutral value (0, `-inf`, `None`, `True`).

**Common patterns (all bottom-up unless noted):** max depth, invert, diameter (path through node = left height + right height), lowest common ancestor, path sum, max path sum (clamp negative child paths to 0), serialize/deserialize (preorder with null markers), right-side view (BFS, take last of each level).

**Complexity:** O(n) time; O(h) recursion-stack space (O(n) worst case for a skewed tree).

**Files:** [Tree Patterns](patterns/tree_patterns.py) (depth, diameter, LCA, path sum, serialize/deserialize, right-side view) · [BST](data-structures/tree/bst.py) · [Trie](data-structures/tree/trie.py) (incl. Word Search II)

---

### 9. Binary Search

**Mental model:** halve the search space each step; works on sorted data **or** any monotonic predicate.

**Templates:**
- **Standard** - find an element; `while left <= right`.
- **Boundary** - first/last occurrence; `while left < right`, don't return early.
- **On answer** - binary-search the *result value* when you can test feasibility monotonically (Ship Packages in D Days, Aggressive Cows, Split Array Largest Sum).
- **Rotated array** - determine which half is sorted, then decide which side to keep.

**Common mistakes:** wrong loop condition (`<=` vs `<`), wrong pointer update (`mid` vs `mid±1`), wrong feasibility predicate for on-answer.

**Files:** [Binary Search patterns](patterns/binary_search.py) (peak, kth-missing, ship-in-D-days, matrix median, median of two sorted arrays)

---

### 10. Sorting

**What to know:** QuickSort (O(n log n) avg, in-place, unstable), MergeSort (O(n log n) worst, stable, O(n) space), QuickSelect (O(n) avg for Kth element without full sort).

**When to sort first:** Two Sum (→ two pointers), intervals (→ sort by start/end, then merge/select), anagrams (→ sort chars to group), find duplicates (→ sort, linear scan).

**Files:** [QuickSort](algorithms/sorting/quick_sort.py) · [MergeSort](algorithms/sorting/merge_sort.py) (incl. count-smaller-after-self, sort-list) · [QuickSelect](algorithms/sorting/quick_select.py) (incl. K closest points)

---

### 11. Stack

**Use for:** matching parentheses, expression evaluation, undo, iterative DFS.

**Monotonic Stack** - next/previous greater/smaller element, stock span, largest rectangle in histogram. Maintain a monotonic (in/de)creasing stack of indices; pop on violation and that's where the popped element's "answer" is.

**Monotonic Deque** ⭐ - sliding window min/max in O(n) (each element enters/leaves once). Strong top-tech favorite; know it cold.

**Files:** [Monotonic Stack](patterns/monotonic_stack.py) · [Monotonic Queue](patterns/monotonic_queue.py)

---

### 12. Greedy

**Mental model:** make the locally optimal choice - but only when you can argue the greedy-choice property holds.

**Common patterns:** intervals (sort by end for selection/non-overlap; by start for merge), Jump Game (track max reach), activity selection, Gas Station (track running surplus, reset start on deficit), Task Scheduler.

**Files:** [Greedy](patterns/greedy.py) · [Intervals](patterns/intervals.py)

---

### 13. Linked List

**Core operations:** reverse (prev/curr/next), cycle detection (Floyd's fast/slow), find middle (fast moves 2×), merge two sorted (dummy head), remove Nth from end (two pointers n apart), palindrome (find mid → reverse half → compare).

**Tip:** use a dummy head node for merge/remove problems to avoid null-edge bugs.

**Files:** [Linked List](data-structures/linked-list/linked_list.py)

---

### 14. Backtracking

**Framework:** `choose → explore (recurse) → un-choose`. Base case captures a complete solution (append a *copy* of the path).

**Common problems:** subsets, permutations, combinations, combination sum, N-Queens, Sudoku, palindrome partitioning, Word Search.

**Optimization:** prune early (check validity before recursing), sort input to skip duplicates, use a visited set.

**Files:** [Backtracking](patterns/backtracking.py)

---

### 15. Heap / Priority Queue

**Use for:** Top K / Kth largest-smallest, merge K sorted lists, running median (two heaps), scheduling, Dijkstra.

**Key idioms:**
- **Top K largest** → **min-heap** of size k (evict the smallest). **Top K smallest** → max-heap of size k. (Counterintuitive but correct.)
- **Running median** → max-heap (lower half) + min-heap (upper half), kept balanced.
- Python's `heapq` is a **min-heap**; negate values for a max-heap.

**Files:** [Heap Patterns](patterns/heap_patterns.py) · [MinHeap](data-structures/heap/min_heap.py) · [MaxHeap](data-structures/heap/max_heap.py) · [PriorityQueue](data-structures/heap/priority_queue.py)

---

### 16. Bit Manipulation

**Core operations:** check bit `num & (1 << i)`, set `num | (1 << i)`, clear `num & ~(1 << i)`, toggle `num ^ (1 << i)`, clear lowest set bit `num & (num-1)`, lowest set bit `num & -num`.

**XOR properties:** `a ^ a = 0`, `a ^ 0 = a` → find the single number, detect missing number.

**Patterns:** single number (XOR all), power of two (`n & (n-1) == 0`), subset generation (iterate `0 .. 2^n - 1`), counting bits.

**Files:** [Bit Manipulation](patterns/bit_manipulation.py)

---

### 16.5 Matrix / Grid

**Mental model:** a grid is an implicit graph - each cell connects to its neighbors (usually 4-directional). Most grid problems are DFS/BFS + a visited marker, or in-place index manipulation.

**Core patterns:**
- **Flood fill / connected components** - DFS or BFS from each unvisited target cell (Number of Islands, Max Area of Island). Mark visited (or sink the cell) before recursing; always bounds-check.
- **Shortest path on a grid** - BFS (unweighted); enqueue `(row, col, dist)`, mark visited on enqueue. Add state to the visited key when relevant (e.g. remaining obstacle-eliminations).
- **Spiral order** - track `top/bottom/left/right` boundaries, shrink after each edge; re-check `top<=bottom && left<=right`.
- **Rotate image 90°** - transpose in place, then reverse each row.
- **Search a sorted matrix** - staircase from the top-right: move left if too big, down if too small (O(m+n)).
- **Set matrix zeroes** - use the first row/column as marker storage for O(1) extra space.

**Watch:** bounds checks before indexing; mark visited *before* enqueuing (BFS) to avoid duplicates; pick the right direction set (4- vs 8-directional).

**Files:** [Matrix Patterns](patterns/matrix.py)

---

### 16.6 Design a Data Structure

A common SDE-2 round: "design/implement X" - combine primitives to hit the required time complexity.

- **LRU Cache** - hash map + doubly linked list for O(1) get/put (evict from the tail). See [lru_cache.py](data-structures/design/lru_cache.py).
- **Min Stack** - push `(value, running_min)` (or a parallel min-stack) so `get_min()` is O(1). See [stack.py](data-structures/stack/stack.py).
- **Median from Data Stream (MedianFinder)** - two heaps: a max-heap for the lower half, a min-heap for the upper half, kept balanced; median from the tops. See [heap_patterns.py](patterns/heap_patterns.py).
- **Trie / prefix tree** - insert/search/startsWith in O(word length); backs autocomplete and Word Search II. See [trie.py](data-structures/tree/trie.py).
- **Others to know:** Hit Counter (queue/ring buffer of timestamps), Insert/Delete/GetRandom O(1) (array + index map), Design Twitter (hash maps + heap merge for the feed).

**Key move:** state the target complexity first, then pick the primitive combo that achieves it (hash map for O(1) lookup, DLL for O(1) reorder, heap for ordered access, trie for prefixes).

---

## 17. Advanced / Rarely Asked at SDE-2

> These are included for completeness and appear in some interviews, but are **low-yield for a typical
> SDE-2 coding round** - mostly competitive-programming territory. Learn the *idea* and what problem
> each solves; only go deep if a specific role or the must-knows are already solid. Don't let these
> crowd out the core patterns above.

- **Segment Tree / Fenwick (BIT)** - range query + point/range update in O(log n). Reach for it only when a problem needs *both* range queries and updates. Fenwick is the simpler cousin for prefix sums. See [segment_tree.py](data-structures/tree/segment_tree.py) and [fenwick_tree.py](data-structures/tree/fenwick_tree.py).
- **Bitmask DP / TSP** - `dp[mask][i]` = best result having visited the set `mask`, ending at `i`. State compression for small n (≤ ~20).
- **Manacher's Algorithm** - longest palindromic substring in O(n). In an interview, center-expansion (O(n²)) is almost always the accepted answer.
- **Suffix Trie / Suffix Array + LCP** - count distinct substrings, longest repeated substring. See [suffix_trie.py](patterns/suffix_trie.py).
- **KMP / Rabin-Karp / Z-Algorithm** - substring search in O(n+m). Know that they exist; the failure-function / rolling-hash derivations are seldom required. See [KMP](algorithms/string/kmp.py), [Rabin-Karp](algorithms/string/rabin_karp.py).
- **Kosaraju's / Tarjan's SCC** - strongly connected components. Uncommon at SDE-2. See [Kosaraju](algorithms/graph/kosaraju.py), [Tarjan](algorithms/graph/tarjan.py).
- **Floyd-Warshall** - all-pairs shortest path, O(V³). Simple to state; rarely the expected answer. See [floyd_warshall.py](algorithms/graph/floyd_warshall.py).
- **Rerooting DP** - recompute a tree DP for every root in O(n). Niche.

**Files (reference only):** [Segment Tree](data-structures/tree/segment_tree.py) · [Suffix Trie](patterns/suffix_trie.py) · [KMP](algorithms/string/kmp.py) · [Rabin-Karp](algorithms/string/rabin_karp.py) · [Kosaraju](algorithms/graph/kosaraju.py) · [Tarjan](algorithms/graph/tarjan.py) · [Floyd-Warshall](algorithms/graph/floyd_warshall.py)
