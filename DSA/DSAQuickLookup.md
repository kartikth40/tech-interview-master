# DSA Pattern Recognition Cheat Sheet

> 🧭 Want the *visual* thinking layer - decision flowcharts, the mental web, and
> constraints→complexity reasoning? See **[DSA Mental Models](mental-models.md)**.

## Problem → Pattern Quick Guide

### Keywords → Pattern Map

| **Keyword/Phrase** | **Pattern** | **Time** | **Space** | **Approach** |
|-------------------|-------------|---------|-----------|--------------|
| Two elements sum to X | Two Pointers | O(n log n) | O(1) | Sort + two pointers |
| Two elements sum to X | Hash Map | O(n) | O(n) | Store complements |
| K elements sum to X | Two Pointers | O(n^k) | O(1) | Reduce to two-sum recursively |
| Subarray sum equals K | Prefix Sum + Hash Map | O(n) | O(n) | Track cumulative sums |
| Exactly K distinct | Sliding Window | O(n) | O(k) | atMost(k) - atMost(k-1) |
| Maximum subarray sum | Kadane's Algorithm | O(n) | O(1) | DP: track maxEndingHere |
| Longest substring with X | Sliding Window | O(n) | O(n) | Expand right, contract left |
| All subsets/combinations | Backtracking | O(2^n) | O(n) | Include/exclude each element |
| All permutations | Backtracking | O(n!) | O(n) | Swap elements, backtrack |
| Next greater/smaller | Monotonic Stack | O(n) | O(n) | Maintain decreasing/increasing stack |
| Find in rotated array | Binary Search | O(log n) | O(1) | Check which half is sorted |
| Find first/last occurrence | Binary Search | O(log n) | O(1) | Boundary binary search |
| Minimize maximum | Binary Search on Answer | O(n log n) | O(1) | Check if answer X is feasible |
| Shortest path (unweighted) | BFS | O(V+E) | O(V) | Level-order traversal |
| Shortest path (positive) | Dijkstra's | O((V+E)logV) | O(V) | Priority queue with distances |
| Shortest path (any weight) | Bellman-Ford | O(VE) | O(V) | Relax edges V-1 times |
| All pairs shortest path | Floyd-Warshall | O(V³) | O(V²) | DP: dist[i][j] via k |
| Detect cycle (undirected) | DFS / Union-Find | O(V+E) | O(V) | Visit neighbors or find operation |
| Detect cycle (directed) | DFS (3-color) | O(V+E) | O(V) | Color states: white/gray/black |
| Topological sort (DAG) | DFS / Kahn's BFS | O(V+E) | O(V) | Postorder DFS or indegree-based |
| Connected components | DFS / BFS / Union-Find | O(V+E) | O(V) | Visit all nodes, count components |
| Strongly connected components | Kosaraju's / Tarjan's | O(V+E) | O(V) | Two DFS passes or Tarjan's algorithm |
| Bipartite check | BFS / DFS coloring | O(V+E) | O(V) | 2-color the graph |
| Minimum spanning tree | Kruskal's | O(E log E) | O(E) | Sort edges, use Union-Find |
| Minimum spanning tree | Prim's | O((V+E)logV) | O(V) | Greedy with min-heap |
| Pattern matching | KMP | O(n+m) | O(m) | Build failure function |
| Pattern matching | Rabin-Karp | O(n+m) avg | O(1) | Rolling hash |
| Distinct substrings | Suffix Trie | O(n²) | O(n²) | Insert all suffixes into trie |
| Distinct substrings | Suffix Array + LCP | O(n log n) | O(n) | Sort suffixes, compute LCP _(advanced, rare)_ |
| Count ways to X | DP | O(?) | O(?) | Define dp[state] = ways to reach |
| Minimum steps/cost to X | DP / BFS | O(?) | O(?) | BFS for unweighted, DP for weighted |
| Longest increasing subsequence | 1D DP | O(n²) | O(n) | Compare all previous elements |
| Longest increasing subsequence | Binary Search | O(n log n) | O(n) | Maintain sorted tails array |
| Edit distance | 2D DP | O(mn) | O(mn) | dp[i][j] = min(insert, delete, replace) |
| 0/1 Knapsack | DP | O(nW) | O(nW) | dp[i][w] = max value |
| Unbounded knapsack | DP | O(nW) | O(nW) | Can reuse items |
| Palindrome partitioning | DP + Precomputation | O(n²) | O(n²) | Precompute isPalindrome[i][j] |
| Valid parentheses | Stack | O(n) | O(n) | Push open, pop on close |
| Evaluate expression | Stack | O(n) | O(n) | Two stacks: numbers & operators |
| Level order traversal | BFS | O(n) | O(w) | Queue, process by levels (w=width) |
| Inorder/Preorder/Postorder | DFS (recursive) | O(n) | O(h) | h=height; recursive traversal |
| Inorder/Preorder/Postorder | Iterative Stack | O(n) | O(h) | Use explicit stack |
| Lowest common ancestor | DFS / Binary Lifting | O(n) / O(log n) | O(n) | Find where paths diverge |
| BST operations | Binary Search Tree | O(log n) avg | O(1) | Left < Root < Right property |
| Trie prefix search | Trie | O(m) | O(n) | m=prefix length; n=total chars |
| Find duplicates in array | Hash Set | O(n) | O(n) | Store seen elements |
| Find duplicates in array | Cycle Detection | O(n) | O(1) | Floyd's tortoise & hare |
| Find missing number | XOR | O(n) | O(1) | XOR all elements |
| Intervals: merge | Sorting + Greedy | O(n log n) | O(n) | Sort by start, merge overlapping |
| Meeting rooms | Sorting + Greedy | O(n log n) | O(n) | Sort by end time, count non-overlapping |
| Reverse linked list | Two Pointers | O(n) | O(1) | Iterative pointer manipulation |
| Cycle detection (list) | Fast/Slow Pointer | O(n) | O(1) | Floyd's algorithm |
| Top K elements | Heap / Quick Select | O(n log k) / O(n) | O(k) | Min-heap or Quick Select |
| Running median | Heaps (max+min) | O(log n) | O(n) | Two heaps approach |
| Merge K sorted lists | Priority Queue | O(nk log k) | O(k) | Min-heap of first elements |
| Power of 2 check | Bit Manipulation | O(1) | O(1) | (n & (n-1)) == 0 |
| Single number (XOR) | XOR | O(n) | O(1) | XOR all: duplicates cancel |
| Subsets generation | Bit Manipulation | O(2^n) | O(2^n) | Iterate 0 to 2^n - 1 |
| Range min/max query | Segment Tree | O(log n) | O(n) | Build tree, query/update O(log n) |
| Constraint based DP (TSP, state) | Bitmask DP | O(2^n * n) | O(2^n * n) | State compression: dp[mask][i] |
| Longest palindrome substring | Manacher's Algorithm | O(n) | O(n) | Expand around centers efficiently |
| Sliding window min/max | Monotonic Deque | O(n) | O(n) | Maintain deque of useful elements |
| Merge overlapping intervals | Sorting + Sweep | O(n log n) | O(n) | Sort by start, merge adjacent |
| Meeting rooms / resources | Sweep Line | O(n log n) | O(n) | Separate starts/ends, count active |
| All permutations | Backtracking | O(n!) | O(n) | Swap elements, backtrack |
| All subsets/combinations | Backtracking | O(2^n) | O(n) | Include/exclude each element |
| N-Queens / Sudoku | Backtracking | O(N!) | O(n) | Place + validate + backtrack |
| Reverse linked list | Pointer Manipulation | O(n) | O(1) | prev/curr/next pointers |
| Cycle in linked list | Fast/Slow Pointer | O(n) | O(1) | Floyd's tortoise & hare |
| Middle of linked list | Fast/Slow Pointer | O(n) | O(1) | Fast moves 2x, slow moves 1x |
| Merge sorted lists | Two Pointers | O(n+m) | O(1) | Dummy head, compare and link |
| LRU Cache | Hash Map + DLL | O(1) | O(n) | Map for lookup, DLL for order |
| Validate BST | DFS + Range | O(n) | O(h) | Pass min/max bounds recursively |
| Kth smallest in BST | Inorder DFS | O(h+k) | O(h) | Inorder gives sorted, stop at k |
| Number of islands | DFS/BFS on Grid | O(m*n) | O(m*n) | Flood fill connected components |
| Spiral matrix traversal | Boundary Shrinking | O(m*n) | O(1) | top/bottom/left/right pointers |
| Rotate matrix 90° | Transpose + Reverse | O(n²) | O(1) | In-place: transpose then reverse rows |
| Search in 2D sorted matrix | Staircase Search | O(m+n) | O(1) | Start top-right, eliminate row/col |

---

## Pattern Categories & Complexity Summary

### 1. **ARRAY PATTERNS**
| Method | Time | Space | Best For |
|--------|------|-------|----------|
| Two Pointers | O(n log n) | O(1) | Sorted arrays, palindromes |
| Sliding Window | O(n) | O(n) | Longest/shortest substring |
| Prefix/Suffix | O(n) | O(n) | Range queries, products |
| Kadane's | O(n) | O(1) | Max subarray sum |
| Exactly K Trick | O(n) | O(n) | atMost(k) - atMost(k-1) |

### 2. **DYNAMIC PROGRAMMING**
| Type | Time | Space | Pattern |
|------|------|-------|---------|
| 1D DP | O(n) | O(n) | dp[i] = state for first i elements |
| 2D DP | O(mn) | O(mn) | dp[i][j] = state for i of A, j of B |
| Knapsack | O(nW) | O(nW) | Capacity-based; can optimize to O(W) |
| Partition | O(n³) | O(n²) | Try all split points (MCM, etc) |
| String DP | O(mn) | O(mn) | LCS, Edit Distance, Matching |
| Bitmask DP | O(2^n * n) | O(2^n * n) | State compression: TSP, subset constraints _(advanced, rare)_ |
### 3. **GRAPH ALGORITHMS** ⭐
| Algorithm | Time | Space | Use When |
|-----------|------|-------|----------|
| BFS | O(V+E) | O(V) | Shortest path (unweighted) |
| DFS | O(V+E) | O(h) | Traversal, cycles, paths |
| Dijkstra's | O((V+E)logV) | O(V) | Shortest path (positive weights) |
| Bellman-Ford | O(VE) | O(V) | Shortest path (any weights) |
| Floyd-Warshall | O(V³) | O(V²) | All-pairs shortest path |
| Kruskal's | O(E log E) | O(E) | MST (with Union-Find) |
| Prim's | O((V+E)logV) | O(V) | MST (with heap) |
| Topological Sort | O(V+E) | O(V) | DAG ordering (DFS/Kahn's) |
| Kosaraju's | O(V+E) | O(V) | Strongly connected components |
| Tarjan's | O(V+E) | O(V) | Strongly connected components |
| Bipartite Check | O(V+E) | O(V) | 2-coloring graph |

### 4. **STRING ALGORITHMS**
| Algorithm | Time | Space | Use When |
|-----------|------|-------|----------|
| KMP | O(n+m) | O(m) | Pattern matching (n=text, m=pattern) |
| Rabin-Karp | O(n+m) avg | O(1) | Multiple pattern searches |
| Suffix Trie | O(n²) | O(n²) | Distinct substrings, all suffixes |
| Suffix Array + LCP | O(n log n) | O(n) | Distinct substrings _(advanced, rarely asked)_ |
| Manacher's Algorithm | O(n) | O(n) | Longest palindrome _(advanced; center-expansion is the accepted answer)_ |

### 5. **TREE TRAVERSALS**
| Traversal | Order | Use |
|-----------|-------|-----|
| Inorder | Left → Root → Right | BST gives sorted |
| Preorder | Root → Left → Right | Tree serialization |
| Postorder | Left → Right → Root | Delete nodes, height calc |
| Level Order | BFS | Level-by-level processing |

### 6. **BINARY SEARCH**
| Variant | Time | Space | Problem |
|---------|------|-------|---------|
| Standard | O(log n) | O(1) | Find element in sorted array |
| Boundary | O(log n) | O(1) | Find first/last occurrence |
| On Answer | O(n log n) | O(1) | Minimize/maximize with feasibility |
| Rotated Array | O(log n) | O(1) | Find in rotated sorted array |

### 7. **SORTING**
| Algorithm | Best | Avg | Worst | Space | Stable |
|-----------|------|-----|-------|-------|--------|
| Quick Sort | O(n log n) | O(n log n) | O(n²) | O(log n) | No |
| Merge Sort | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes |
| Quick Select | O(n) | O(n) | O(n²) | O(log n) | No |

### 8. **STACK & QUEUE PATTERNS**
| Pattern | Time | Space | Use |
|---------|------|-------|-----|
| Matching Brackets | O(n) | O(n) | Validate parentheses |
| Monotonic Stack | O(n) | O(n) | Next/previous greater/smaller |
| Monotonic Deque | O(n) | O(n) | Sliding window min/max ⭐ |
| Expression Eval | O(n) | O(n) | Infix to postfix conversion |

### 9. **HEAP / PRIORITY QUEUE**
| Operation | Time | Use |
|-----------|------|-----|
| Push/Pop | O(log n) | Top K elements, Dijkstra's |
| Heapify | O(n) | Build heap from array |
| Top K Frequent | O(n log k) | Find K elements with highest freq |
| Merge K Lists | O(nk log k) | Merge sorted lists |

### 10. **LINKED LIST**
| Operation | Time | Space | Method |
|-----------|------|-------|--------|
| Reverse | O(n) | O(1) | Two pointer manipulation |
| Cycle Detect | O(n) | O(1) | Floyd's fast/slow |
| Merge | O(n+m) | O(1) | Two pointer iteration |
| Find Kth | O(n) | O(1) | Two pointer k-step apart |

### 11. **BIT MANIPULATION**
| Operation | Time | Use |
|-----------|------|-----|
| Check ith bit | O(1) | (num & (1 << i)) != 0 |
| Set ith bit | O(1) | num \| (1 << i) |
| Count set bits | O(log n) | Loop: num &= (num - 1) |
| XOR properties | O(1) | Find single element, swap |

### 12. **BACKTRACKING**
| Problem | Time | Space | Approach |
|---------|------|-------|----------|
| Permutations | O(n!) | O(n) | Swap elements recursively |
| Combinations | O(2^n) | O(n) | Include/exclude each element |
| Subsets | O(2^n) | O(n) | Generate all combinations |
| N-Queens | O(N!) | O(n) | Backtrack on invalid placements |
| Sudoku | O(9^(81)) | O(1) | Try digits 1-9, backtrack |

### 13. **GREEDY PATTERNS**
| Problem | Time | Space | Strategy |
|---------|------|-------|----------|
| Interval Scheduling | O(n log n) | O(1) | Sort by end time, select non-overlapping |
| Jump Game | O(n) | O(1) | Track max reachable distance |
| Activity Selection | O(n log n) | O(1) | Greedy by end time |
| Task Scheduler | O(n) | O(1) | Fill idle slots around max-freq task |
| Gas Station | O(n) | O(1) | Track surplus, reset start on deficit |

### 14. **UNION-FIND (DISJOINT SET)**
| Operation | Time | Use |
|-----------|------|-----|
| Find | O(α(n)) ≈ O(1) | Path compression |
| Union | O(α(n)) ≈ O(1) | Union by rank |
| Connected | O(α(n)) ≈ O(1) | Graph connectivity |

### 15. **RANGE QUERIES & ADVANCED DATA STRUCTURES** ⭐
| Data Structure | Operation | Time | Space | Use When |
|----------------|-----------|------|-------|----------|
| Segment Tree | Build | O(n) | O(n) | Range min/max/sum with updates |
| Segment Tree | Query | O(log n) | - | Find result in range [l, r] |
| Segment Tree | Update | O(log n) | - | Point/range updates |
| Fenwick Tree | Query/Update | O(log n) | O(n) | Simpler alternative to Seg Tree |

### 16. **ADVANCED STRING PATTERNS** ⭐
| Algorithm | Time | Space | Problem |
|-----------|------|-------|---------|
| Manacher's | O(n) | O(n) | Longest palindrome substring |
| Z-Algorithm | O(n) | O(n) | Pattern matching alternative |

### 17. **INTERVAL PATTERNS**
| Problem | Time | Space | Strategy |
|---------|------|-------|----------|
| Merge Intervals | O(n log n) | O(n) | Sort by start, merge overlapping |
| Insert Interval | O(n) | O(n) | Three-phase: before, merge, after |
| Meeting Rooms II | O(n log n) | O(n) | Sweep line: separate starts/ends |
| Interval Intersection | O(n+m) | O(n) | Two pointers, advance earlier end |
| Min Arrows (Balloons) | O(n log n) | O(1) | Sort by end, greedy shoot |

### 18. **MATRIX / GRID PATTERNS**
| Problem | Time | Space | Strategy |
|---------|------|-------|----------|
| Number of Islands | O(m*n) | O(m*n) | DFS/BFS flood fill |
| Spiral Order | O(m*n) | O(1) | Boundary shrinking (top/bottom/left/right) |
| Rotate 90° | O(n²) | O(1) | Transpose + reverse rows |
| Search Sorted 2D | O(m+n) | O(1) | Staircase from top-right |
| Set Matrix Zeroes | O(m*n) | O(1) | Use first row/col as markers |

### 19. **LINKED LIST PATTERNS**
| Operation | Time | Space | Method |
|-----------|------|-------|--------|
| Reverse | O(n) | O(1) | prev/curr/next pointer swap |
| Detect Cycle | O(n) | O(1) | Floyd's fast/slow |
| Find Cycle Start | O(n) | O(1) | Meet point → reset one to head |
| Find Middle | O(n) | O(1) | Fast moves 2x, slow 1x |
| Merge Two Sorted | O(n+m) | O(1) | Dummy head + compare |
| Remove Nth from End | O(n) | O(1) | Two pointers n apart |
| Palindrome Check | O(n) | O(1) | Find mid → reverse 2nd half → compare |

### 20. **DESIGN PATTERNS (DATA STRUCTURE DESIGN)**
| Problem | Time | Space | Approach |
|---------|------|-------|----------|
| LRU Cache | O(1) get/put | O(n) | HashMap + Doubly Linked List |
| Min Stack | O(1) all ops | O(n) | Auxiliary stack tracking mins |
| MedianFinder | O(log n) add | O(n) | MaxHeap (lower) + MinHeap (upper) |

---

## Quick Decision Tree

```
Choose Your Pattern:

📊 ARRAY
├─ Need sorted? → Two Pointers
├─ Window sliding? → Sliding Window
├─ Max subarray? → Kadane's
└─ Frequency? → Hash Map / Prefix Sum

🔄 GRAPH
├─ Unweighted graph? → BFS
├─ Positive weights? → Dijkstra's
├─ Any weights? → Bellman-Ford
├─ All pairs? → Floyd-Warshall
├─ Tree edges? → Kruskal's / Prim's
├─ Ordering? → Topological Sort
└─ Components? → DFS / Union-Find

↩️ STRING
├─ Pattern match? → KMP / Rabin-Karp
└─ Distinct subs? → Suffix Array + LCP

📈 DYNAMIC PROGRAMMING
├─ Sequence? → 1D DP
├─ 2D problem? → 2D DP
├─ Capacity? → Knapsack
├─ State constraints (small n)? → Bitmask DP (advanced)
├─ Edit? → 2D DP (Edit Distance)
└─ Ways/Min cost? → DP with states

🔍 SEARCH
├─ Sorted array? → Binary Search
├─ Find answer? → Binary Search on Answer
└─ Rotated? → Special Binary Search

📜 TREE & STRINGS
├─ Tree - Sorted? → Inorder
├─ Tree - Copy? → Preorder
├─ Tree - Delete? → Postorder
├─ Tree - Levels? → Level Order (BFS)
├─ Palindrome? → Expand-around-center (Manacher's only if O(n) required)
└─ Pattern match? → KMP / Rabin-Karp

⚙️ SPECIALIZED
├─ Range query? → Segment Tree ⭐
├─ Window min/max? → Monotonic Deque ⭐
├─ Top K? → Heap / Quick Select
├─ Cycle? → DFS (3-color) / Union-Find
├─ LCA? → DFS / Binary Lifting
├─ Parentheses? → Stack
├─ Next Greater? → Monotonic Stack
└─ Single element? → XOR

🔗 LINKED LIST
├─ Reverse? → prev/curr/next pointers
├─ Cycle? → Floyd's fast/slow
├─ Middle? → Fast/slow pointer
├─ Merge sorted? → Dummy head + two pointers
└─ Kth from end? → Two pointers k apart

📐 MATRIX / GRID
├─ Islands/components? → DFS/BFS flood fill
├─ Shortest path? → BFS
├─ Spiral? → Boundary shrinking
├─ Rotate? → Transpose + reverse
└─ Search sorted? → Staircase (top-right)

🎒 BACKTRACKING
├─ All subsets? → Include/exclude
├─ Permutations? → Swap + backtrack
├─ Constraint satisfaction? → Place + validate + undo
└─ Partition? → Try all split points

📦 DESIGN
├─ O(1) cache? → LRU Cache (Map + DLL)
├─ Prefix search? → Trie
└─ Running median? → Two heaps (max + min)
```

---

## Common Mistakes to Avoid

| Mistake | Fix |
|---------|-----|
| Integer overflow in binary search | Use `left + (right - left) / 2` |
| Wrong loop condition | Use `left <= right` for inclusive, `left < right` for exclusive |
| Forgetting base cases in DP | Always initialize dp[0], dp[1] correctly |
| Not handling edge cases | Check empty arrays, null pointers, single elements |
| Modifying array during iteration | Use copy or iterate backwards |
| Not resetting data structures | Clear visited sets, maps between test cases |
| Wrong recursion order in DP | Compute dependencies before using them |
| Greedy without proof | Ensure greedy choice property holds |

---

## File References

- **Arrays:** [Two Pointers](patterns/two_pointers.py), [Sliding Window](patterns/sliding_window.py), [Prefix Sum](patterns/prefix_sum_pattern.py), [kSum Reduction](patterns/k_sum_reduction.py)
- **Graphs:** [DFS](algorithms/graph/dfs.py), [BFS](algorithms/graph/bfs.py), [Dijkstra's](algorithms/graph/dijkstra.py), [Bellman-Ford](algorithms/graph/bellman_ford.py), [Floyd-Warshall](algorithms/graph/floyd_warshall.py), [Kruskal's](algorithms/graph/kruskals.py), [Prim's](algorithms/graph/prims.py), [Kosaraju's](algorithms/graph/kosaraju.py), [Tarjan's](algorithms/graph/tarjan.py)
- **Strings:** [KMP](algorithms/string/kmp.py), [Rabin-Karp](algorithms/string/rabin_karp.py), [Suffix Trie](patterns/suffix_trie.py)
- **Search:** [Binary Search](patterns/binary_search.py)
- **Sorting:** [QuickSort](algorithms/sorting/quick_sort.py), [MergeSort](algorithms/sorting/merge_sort.py), [QuickSelect](algorithms/sorting/quick_select.py)
- **Trees:** [BST](data-structures/tree/bst.py), [Trie](data-structures/tree/trie.py), [Segment Tree](data-structures/tree/segment_tree.py)
- **Graph DS:** [Graph](data-structures/graph/graph.py) (adjacency list, matrix, weighted builders)
- **Heaps:** [MinHeap](data-structures/heap/min_heap.py), [MaxHeap](data-structures/heap/max_heap.py), [PriorityQueue](data-structures/heap/priority_queue.py)
- **Linked List:** [LinkedList](data-structures/linked-list/linked_list.py)
- **Stack:** [Stack + MinStack](data-structures/stack/stack.py), [Monotonic Stack](patterns/monotonic_stack.py), [Monotonic Queue](patterns/monotonic_queue.py)
- **DP:** [DP Patterns](patterns/dp_patterns.py), [Climbing Stairs](algorithms/dp/climbing_stairs.py), [House Robber](algorithms/dp/house_robber.py), [Coin Change](algorithms/dp/coin_change.py), [Knapsack](algorithms/dp/knapsack.py), [LCS](algorithms/dp/lcs.py), [Edit Distance](algorithms/dp/edit_distance.py), [Unique Paths](algorithms/dp/unique_paths.py)
- **Patterns:** [Backtracking](patterns/backtracking.py), [Greedy](patterns/greedy.py), [Intervals](patterns/intervals.py), [Matrix](patterns/matrix.py), [Tree Patterns](patterns/tree_patterns.py), [Heap Patterns](patterns/heap_patterns.py)
- **Other:** [Union-Find](patterns/union_find_patterns.py), [Bit Manipulation](patterns/bit_manipulation.py), [Boyer-Moore Voting](patterns/boyer_moore_majority_voting.py), [LRU Cache](data-structures/design/lru_cache.py)

---

## Top-Tech Must-Knows (high frequency - prioritize these)

These come up again and again in real interview loops across MAANG and top Indian unicorns. Be fluent, not just familiar.

**Monotonic Deque** - Sliding window min/max in O(n) (all top companies)  
**Union-Find** - Connectivity, grouping, cycle detection (Redundant Connection, Accounts Merge)  
**Dijkstra + BFS/DFS on grids & graphs** - the graph workhorses  
**Backtracking** - subsets/permutations/combinations, Word Search  
**Heaps / Top-K / two-heap median** - Kth Largest, Merge K Lists, Median from Data Stream  
**Trie + grid DFS** - Word Search II  
**DP** - 1D/2D, knapsack, LIS (O(n log n)), edit distance, coin change

---

## Advanced / Rarely Asked (study last, or skip)

These appear in the repo for completeness, but are **low-yield for a typical coding round** (MAANG
or top unicorns) - they are mostly competitive-programming territory. Don't spend core prep time here
until the must-knows above are solid. Know that they exist and what problem they solve; deep
memorization is rarely rewarded.

**Segment Tree / Fenwick (BIT)** - range query + update. Rarely asked; only if the JD hints at it.  
**Bitmask DP / TSP** - constraint-based state compression. Edge case.  
**Manacher's Algorithm** - O(n) longest palindrome. Center-expansion (O(n²)) is the accepted answer.  
**Suffix Trie / Suffix Array + LCP** - distinct substrings. Competitive-programming topic.  
**KMP / Rabin-Karp / Z-Algorithm** - the failure-function / rolling-hash derivations are seldom required.  
**Kosaraju's / Tarjan's SCC** - strongly connected components. Uncommon.  
**Rerooting DP / Floyd-Warshall** - niche; know the idea, not the code from memory.