# PATTERN NAME: Backtracking
# DIFFICULTY: Medium | FREQUENCY: Very High (subsets, permutations, combinations at all companies)

# WHEN TO USE:
# - Generate all combinations / permutations / subsets.
# - Constraint satisfaction (N-Queens, Sudoku).
# - Path finding with all solutions.
# - "Find all ways to..." problems.

# CORE IDEA (INTUITION):
# - Build the solution incrementally, one choice at a time.
# - Explore a choice (recurse), then UNDO it (backtrack) to try the next.
# - Prune branches that cannot lead to a valid solution.
# - Template: choose -> explore -> unchoose.

# INVARIANTS:
# - The current path always represents a valid partial solution.
# - After exploring a choice, state is restored exactly (undo the choice).
# - Base case captures a complete solution.

# COMMON MISTAKES:
# - Forgetting to undo the choice (state leaks between branches).
# - Appending a reference to the mutable path instead of a copy (path[:]).
# - Wrong start index for combinations (causes duplicates or misses).
# - Not skipping duplicates when the input has repeats.

# TIME & SPACE:
# - Subsets: O(2^n) subsets, O(n) per subset.
# - Permutations: O(n! * n).
# - Combinations: O(C(n, k) * k).
# - Space: O(n) recursion depth (excluding output).

# RELATED PROBLEMS:
# - Subsets (LC 78) / Subsets II (LC 90)
# - Permutations (LC 46) / Permutations II (LC 47)
# - Combination Sum (LC 39) / Combination Sum II (LC 40)
# - N-Queens (LC 51)
# - Word Search (LC 79)
# - Palindrome Partitioning (LC 131)


# === SUBSETS ===
def subsets(nums: list[int]) -> list[list[int]]:
    result: list[list[int]] = []

    def backtrack(start: int, path: list[int]) -> None:
        result.append(path[:])  # every path is a valid subset
        for i in range(start, len(nums)):
            path.append(nums[i])     # choose
            backtrack(i + 1, path)   # explore
            path.pop()               # unchoose

    backtrack(0, [])
    return result


# === PERMUTATIONS ===
def permute(nums: list[int]) -> list[list[int]]:
    result: list[list[int]] = []

    def backtrack(path: list[int], used: list[bool]) -> None:
        if len(path) == len(nums):
            result.append(path[:])
            return
        for i in range(len(nums)):
            if used[i]:
                continue
            used[i] = True
            path.append(nums[i])
            backtrack(path, used)
            path.pop()
            used[i] = False

    backtrack([], [False] * len(nums))
    return result


# === COMBINATION SUM (unlimited reuse) ===
def combination_sum(candidates: list[int], target: int) -> list[list[int]]:
    result: list[list[int]] = []

    def backtrack(start: int, path: list[int], remaining: int) -> None:
        if remaining == 0:
            result.append(path[:])
            return
        if remaining < 0:
            return
        for i in range(start, len(candidates)):
            path.append(candidates[i])
            backtrack(i, path, remaining - candidates[i])  # i (not i+1): reuse allowed
            path.pop()

    backtrack(0, [], target)
    return result


# === SUBSETS II (with duplicates) ===
def subsets_with_dup(nums: list[int]) -> list[list[int]]:
    result: list[list[int]] = []
    nums.sort()

    def backtrack(start: int, path: list[int]) -> None:
        result.append(path[:])
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue  # skip duplicates at the same level
            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()

    backtrack(0, [])
    return result


# === N-QUEENS (count solutions) ===
def total_n_queens(n: int) -> int:
    cols: set[int] = set()
    diag1: set[int] = set()  # r - c
    diag2: set[int] = set()  # r + c
    count = 0

    def backtrack(row: int) -> None:
        nonlocal count
        if row == n:
            count += 1
            return
        for col in range(n):
            if col in cols or (row - col) in diag1 or (row + col) in diag2:
                continue
            cols.add(col)
            diag1.add(row - col)
            diag2.add(row + col)
            backtrack(row + 1)
            cols.remove(col)
            diag1.remove(row - col)
            diag2.remove(row + col)

    backtrack(0)
    return count


if __name__ == "__main__":
    print(subsets([1, 2, 3]))
    # [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]
    print(permute([1, 2, 3]))
    # [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]
    print(combination_sum([2, 3, 6, 7], 7))    # [[2, 2, 3], [7]]
    print(subsets_with_dup([1, 2, 2]))         # [[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]
    print(total_n_queens(4))                   # 2
