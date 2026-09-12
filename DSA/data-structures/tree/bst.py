# DATA STRUCTURE: Binary Search Tree (BST)
# DIFFICULTY: Medium | FREQUENCY: High (validate BST, kth smallest, LCA at Google/Meta/Amazon)

# A BST is a binary tree where for every node:
#   - All values in left subtree < node.val
#   - All values in right subtree > node.val

# Time Complexity (balanced):
# - Search: O(log n)
# - Insert: O(log n)
# - Delete: O(log n)
# Worst case (skewed): O(n) for all operations

# When to use:
# - Ordered data with dynamic insertions/deletions
# - Range queries, floor/ceiling lookups
# - Inorder traversal gives sorted output
# - Interview problems: validate BST, kth smallest, LCA in BST

from __future__ import annotations

# COMMON MISTAKES:
# - Validating a BST by only comparing a node with its direct children (must carry min/max bounds).
# - Mishandling the two-children delete case (replace with inorder successor, then delete it).
# - Using <= instead of < for the "all left < node" invariant (duplicates policy).
# - Recursing into both subtrees for LCA in a BST instead of exploiting the ordering.

# RELATED PROBLEMS:
# - Validate Binary Search Tree (LC 98)
# - Kth Smallest Element in a BST (LC 230)
# - Lowest Common Ancestor of a BST (LC 235)
# - Convert Sorted Array to Binary Search Tree (LC 108)


class TreeNode:
    def __init__(self, val: int = 0, left: TreeNode | None = None, right: TreeNode | None = None) -> None:
        self.val = val
        self.left = left
        self.right = right


class BST:
    def __init__(self) -> None:
        self.root: TreeNode | None = None

    # Insert a value
    def insert(self, val: int) -> None:
        self.root = self._insert_node(self.root, val)

    def _insert_node(self, node: TreeNode | None, val: int) -> TreeNode:
        if not node:
            return TreeNode(val)
        if val < node.val:
            node.left = self._insert_node(node.left, val)
        elif val > node.val:
            node.right = self._insert_node(node.right, val)
        return node  # duplicates ignored

    # Search for a value
    def search(self, val: int) -> bool:
        return self._search_node(self.root, val)

    def _search_node(self, node: TreeNode | None, val: int) -> bool:
        if not node:
            return False
        if val == node.val:
            return True
        if val < node.val:
            return self._search_node(node.left, val)
        return self._search_node(node.right, val)

    # Delete a value
    def delete(self, val: int) -> None:
        self.root = self._delete_node(self.root, val)

    def _delete_node(self, node: TreeNode | None, val: int) -> TreeNode | None:
        if not node:
            return None

        if val < node.val:
            node.left = self._delete_node(node.left, val)
        elif val > node.val:
            node.right = self._delete_node(node.right, val)
        else:
            # Found the node to delete
            # Case 1: leaf node
            if not node.left and not node.right:
                return None
            # Case 2: one child
            if not node.left:
                return node.right
            if not node.right:
                return node.left
            # Case 3: two children - replace with inorder successor
            successor = self._find_min(node.right)
            node.val = successor.val
            node.right = self._delete_node(node.right, successor.val)

        return node

    def _find_min(self, node: TreeNode) -> TreeNode:
        while node.left:
            node = node.left
        return node

    # Inorder traversal (sorted output)
    def inorder(self) -> list[int]:
        result: list[int] = []
        self._inorder_helper(self.root, result)
        return result

    def _inorder_helper(self, node: TreeNode | None, result: list[int]) -> None:
        if not node:
            return
        self._inorder_helper(node.left, result)
        result.append(node.val)
        self._inorder_helper(node.right, result)


# === COMMON BST INTERVIEW PROBLEMS ===

# Validate BST
def is_valid_bst(root: TreeNode | None, low: float = float("-inf"), high: float = float("inf")) -> bool:
    if not root:
        return True
    if root.val <= low or root.val >= high:
        return False
    return is_valid_bst(root.left, low, root.val) and is_valid_bst(root.right, root.val, high)


# Kth Smallest Element in BST (inorder traversal)
def kth_smallest(root: TreeNode | None, k: int) -> int | None:
    count = 0
    result: int | None = None

    def inorder(node: TreeNode | None) -> None:
        nonlocal count, result
        if not node or result is not None:
            return
        inorder(node.left)
        count += 1
        if count == k:
            result = node.val
            return
        inorder(node.right)

    inorder(root)
    return result


# Lowest Common Ancestor in BST
# Exploit BST property: if both values < node, go left; both > node, go right.
def lowest_common_ancestor(root: TreeNode | None, p: int, q: int) -> TreeNode | None:
    while root:
        if p < root.val and q < root.val:
            root = root.left
        elif p > root.val and q > root.val:
            root = root.right
        else:
            return root  # split point = LCA
    return None


# Convert Sorted Array to Balanced BST
def sorted_array_to_bst(nums: list[int]) -> TreeNode | None:
    def build(lo: int, hi: int) -> TreeNode | None:
        if lo > hi:
            return None
        mid = (lo + hi) >> 1
        node = TreeNode(nums[mid])
        node.left = build(lo, mid - 1)
        node.right = build(mid + 1, hi)
        return node

    return build(0, len(nums) - 1)


# Examples (only run when executed directly)
if __name__ == "__main__":
    bst = BST()
    for value in [5, 3, 7, 1, 4, 6, 8]:
        bst.insert(value)
    print(bst.inorder())    # [1, 3, 4, 5, 6, 7, 8]
    print(bst.search(4))    # True
    print(bst.search(9))    # False

    bst.delete(3)
    print(bst.inorder())    # [1, 4, 5, 6, 7, 8]

    balanced = sorted_array_to_bst([1, 2, 3, 4, 5, 6, 7])
    print(is_valid_bst(balanced))     # True
    print(kth_smallest(balanced, 3))  # 3
