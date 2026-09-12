# PATTERN NAME: Binary Tree Patterns
# DIFFICULTY: Medium | FREQUENCY: Very High (depth, diameter, LCA, path sum at all companies)

# WHEN TO USE:
# - Any problem involving binary trees (not just BSTs).
# - Depth, diameter, path sum, LCA, invert, serialize.
# - Most tree problems are naturally recursive: solve subtrees, combine at the root.

# CORE IDEA (INTUITION):
# - Trees are recursive: every subtree is itself a tree.
# - Most solutions follow: process left, process right, combine at the current node.
# - Two approaches: top-down (pass info down) vs bottom-up (return info up).
# - Bottom-up is usually cleaner.

# INVARIANTS:
# - Base case: a null node returns a neutral value (0, -inf, None, True).
# - Each node visited once -> O(n) time.
# - Recursion depth = tree height -> O(h) space, worst case O(n) for skewed trees.

# COMMON MISTAKES:
# - Forgetting the base case (null node).
# - Confusing top-down vs bottom-up (diameter / max path sum MUST be bottom-up).
# - In max path sum: forgetting to clamp negative paths to 0.
# - In LCA: not handling the case where p or q IS the root.
# - In serialize: not handling null markers during deserialize.

# TIME & SPACE:
# - All recursive traversals: O(n) time, O(h) space (O(n) worst case).
# - BFS (right side view): O(n) time, O(w) space (w = max width).

# RELATED PROBLEMS:
# - Maximum Depth of Binary Tree (LC 104)
# - Invert Binary Tree (LC 226)
# - Diameter of Binary Tree (LC 543)
# - Lowest Common Ancestor (LC 236)
# - Binary Tree Maximum Path Sum (LC 124)
# - Path Sum (LC 112)
# - Same Tree (LC 100)
# - Subtree of Another Tree (LC 572)
# - Serialize and Deserialize Binary Tree (LC 297)
# - Binary Tree Right Side View (LC 199)

from __future__ import annotations
from collections import deque


# Self-contained node (see also DSA/data-structures/tree/bst.py)
class TreeNode:
    def __init__(self, val: int = 0, left: TreeNode | None = None, right: TreeNode | None = None) -> None:
        self.val = val
        self.left = left
        self.right = right


# === MAX DEPTH ===
def max_depth(root: TreeNode | None) -> int:
    if not root:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))


# === INVERT BINARY TREE ===
def invert_tree(root: TreeNode | None) -> TreeNode | None:
    if not root:
        return None
    root.left, root.right = invert_tree(root.right), invert_tree(root.left)
    return root


# === DIAMETER OF BINARY TREE ===
# Longest path between any two nodes (may not pass through the root).
def diameter_of_binary_tree(root: TreeNode | None) -> int:
    diameter = 0

    def height(node: TreeNode | None) -> int:
        nonlocal diameter
        if not node:
            return 0
        left = height(node.left)
        right = height(node.right)
        diameter = max(diameter, left + right)  # path through this node
        return 1 + max(left, right)

    height(root)
    return diameter


# === LOWEST COMMON ANCESTOR (general binary tree) ===
def lowest_common_ancestor(root: TreeNode | None, p: TreeNode, q: TreeNode) -> TreeNode | None:
    if not root or root is p or root is q:
        return root
    left = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)
    if left and right:
        return root       # p and q are in different subtrees
    return left or right  # both in the same subtree


# === PATH SUM (root to leaf) ===
def has_path_sum(root: TreeNode | None, target_sum: int) -> bool:
    if not root:
        return False
    if not root.left and not root.right:
        return root.val == target_sum
    return (has_path_sum(root.left, target_sum - root.val)
            or has_path_sum(root.right, target_sum - root.val))


# === MAXIMUM PATH SUM (any node to any node) ===
def max_path_sum(root: TreeNode | None) -> int:
    max_sum = float("-inf")

    def dfs(node: TreeNode | None) -> int:
        nonlocal max_sum
        if not node:
            return 0
        left = max(0, dfs(node.left))   # ignore negative paths
        right = max(0, dfs(node.right))
        max_sum = max(max_sum, left + right + node.val)  # path through this node
        return node.val + max(left, right)               # best single path upward

    dfs(root)
    return int(max_sum)


# === SAME TREE ===
def is_same_tree(p: TreeNode | None, q: TreeNode | None) -> bool:
    if not p and not q:
        return True
    if not p or not q:
        return False
    return p.val == q.val and is_same_tree(p.left, q.left) and is_same_tree(p.right, q.right)


# === SUBTREE OF ANOTHER TREE ===
def is_subtree(root: TreeNode | None, sub_root: TreeNode | None) -> bool:
    if not root:
        return False
    if is_same_tree(root, sub_root):
        return True
    return is_subtree(root.left, sub_root) or is_subtree(root.right, sub_root)


# === SERIALIZE / DESERIALIZE (preorder with null markers) ===
def serialize(root: TreeNode | None) -> str:
    result: list[str] = []

    def dfs(node: TreeNode | None) -> None:
        if not node:
            result.append("null")
            return
        result.append(str(node.val))
        dfs(node.left)
        dfs(node.right)

    dfs(root)
    return ",".join(result)


def deserialize(data: str) -> TreeNode | None:
    vals = data.split(",")
    idx = 0

    def dfs() -> TreeNode | None:
        nonlocal idx
        if vals[idx] == "null":
            idx += 1
            return None
        node = TreeNode(int(vals[idx]))
        idx += 1
        node.left = dfs()
        node.right = dfs()
        return node

    return dfs()


# === RIGHT SIDE VIEW (BFS level order, take the last of each level) ===
def right_side_view(root: TreeNode | None) -> list[int]:
    if not root:
        return []
    result: list[int] = []
    queue: deque[TreeNode] = deque([root])

    while queue:
        size = len(queue)
        for i in range(size):
            node = queue.popleft()
            if i == size - 1:
                result.append(node.val)  # rightmost node at this level
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

    return result


if __name__ == "__main__":
    root = TreeNode(1,
                    TreeNode(2, TreeNode(4), TreeNode(5)),
                    TreeNode(3))

    print(max_depth(root))               # 3
    print(diameter_of_binary_tree(root))  # 3
    print(has_path_sum(root, 7))          # True (1 -> 2 -> 4)
    print(right_side_view(root))          # [1, 3, 5]

    serialized = serialize(root)
    print(serialized)                     # 1,2,4,null,null,5,null,null,3,null,null
    print(max_depth(deserialize(serialized)))  # 3
