# DATA STRUCTURE: Stack (LIFO) + MinStack
# DIFFICULTY: Easy | FREQUENCY: Very High (parentheses, monotonic stack, DFS at all top companies)

# A stack is a LIFO (Last In, First Out) data structure.
# Think of it like a stack of plates - you add and remove from the top.

# Time Complexity:
# - push: O(1)
# - pop: O(1)
# - peek: O(1)
# - is_empty: O(1)

# When to use:
# - Matching parentheses/brackets
# - Undo/redo operations
# - DFS traversal (iterative)
# - Expression evaluation (infix, postfix)
# - Monotonic stack problems (next greater element)
# - Function call simulation (recursion stack)

# NOTE: In idiomatic Python, a plain `list` already works as a stack (append / pop). This class
# is kept for teaching the ADT explicitly.

from typing import Any

# COMMON MISTAKES:
# - Popping/peeking an empty stack (list.pop() raises IndexError).
# - For MinStack: forgetting to push the running min on EVERY push so pop stays O(1).
# - Comparing with the wrong end of the list (top is index -1, not 0).

# RELATED PROBLEMS:
# - Valid Parentheses (LC 20)
# - Min Stack (LC 155)
# - Next Greater Element I (LC 496)
# - Evaluate Reverse Polish Notation (LC 150)


class Stack:
    def __init__(self) -> None:
        self.s: list[Any] = []

    def push(self, x: Any) -> None:
        self.s.append(x)

    def pop(self) -> Any:
        return self.s.pop()

    def peek(self) -> Any:
        return self.s[-1]

    def is_empty(self) -> bool:
        return len(self.s) == 0

    def size(self) -> int:
        return len(self.s)


# === MIN STACK (O(1) get_min) ===
# Common interview problem: design a stack that supports get_min in O(1).
class MinStack:
    def __init__(self) -> None:
        self.stack: list[int] = []
        self.min_stack: list[int] = []  # tracks minimum at each level

    def push(self, val: int) -> None:
        self.stack.append(val)
        cur_min = val if not self.min_stack else min(val, self.min_stack[-1])
        self.min_stack.append(cur_min)

    def pop(self) -> None:
        self.stack.pop()
        self.min_stack.pop()

    def top(self) -> int:
        return self.stack[-1]

    def get_min(self) -> int:
        return self.min_stack[-1]


# Examples (only run when executed directly)
if __name__ == "__main__":
    stack = Stack()
    stack.push(1)
    stack.push(2)
    stack.push(3)
    print(stack.peek())     # 3
    print(stack.pop())      # 3
    print(stack.size())     # 2
    print(stack.is_empty())  # False

    min_stack = MinStack()
    min_stack.push(5)
    min_stack.push(2)
    min_stack.push(7)
    print(min_stack.get_min())  # 2
    min_stack.pop()
    print(min_stack.get_min())  # 2
    min_stack.pop()
    print(min_stack.get_min())  # 5
