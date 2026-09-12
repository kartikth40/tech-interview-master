# PATTERN NAME: Monotonic Stack
# DIFFICULTY: Medium | FREQUENCY: Very High (next-greater-element family at Google/Amazon/Meta)

# WHEN TO USE:
# - Next/previous greater or smaller element.
# - Largest rectangle in a histogram.
# - Stock span, daily temperatures.
# - Problems asking "for each element, find the nearest X".

# CORE IDEA (INTUITION):
# - Maintain a stack whose elements are monotonic (increasing or decreasing).
# - Before pushing, pop all elements that violate the monotonic property.
# - The popped elements have found their "answer" (the current element).
# - Store indices (not values) when you need distances.

# INVARIANTS:
# - Decreasing stack: each element is smaller than the one below it (top is smallest).
# - When we pop, the current element is the "next greater" for the popped element.
# - Each element is pushed and popped at most once -> O(n) total.

# COMMON MISTAKES:
# - Storing values when you need indices (for distances).
# - Wrong monotonic direction (increasing vs decreasing).
# - Forgetting to process remaining stack elements after the loop.
# - Off-by-one in histogram width calculation.

# TIME & SPACE:
# - Time: O(n) - each element pushed/popped once.
# - Space: O(n) for the stack.

# RELATED PROBLEMS:
# - Next Greater Element I (LC 496) / II (LC 503)
# - Daily Temperatures (LC 739)
# - Largest Rectangle in Histogram (LC 84)
# - Trapping Rain Water (LC 42)
# - Remove K Digits (LC 402)
# - Sum of Subarray Minimums (LC 907)


# Daily Temperatures - days until a warmer temperature (decreasing stack of indices)
def daily_temperatures(temperatures: list[int]) -> list[int]:
    result = [0] * len(temperatures)
    stack: list[int] = []  # indices, temperatures decreasing

    for i, temp in enumerate(temperatures):
        while stack and temperatures[stack[-1]] < temp:
            prev_index = stack.pop()
            result[prev_index] = i - prev_index
        stack.append(i)

    return result


# Next Greater Element (circular array)
def next_greater_elements(nums: list[int]) -> list[int]:
    n = len(nums)
    result = [-1] * n
    stack: list[int] = []  # indices

    # iterate twice to simulate the circular array
    for i in range(2 * n):
        idx = i % n
        while stack and nums[stack[-1]] < nums[idx]:
            result[stack.pop()] = nums[idx]
        if i < n:
            stack.append(idx)

    return result


# Largest Rectangle in Histogram
def largest_rectangle_area(heights: list[int]) -> int:
    stack: list[int] = []  # indices, heights increasing
    max_area = 0
    heights = heights + [0]  # sentinel to flush the stack

    for i, h in enumerate(heights):
        while stack and heights[stack[-1]] > h:
            height = heights[stack.pop()]
            width = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, height * width)
        stack.append(i)

    return max_area


if __name__ == "__main__":
    print(daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]))
    # [1, 1, 4, 2, 1, 1, 0, 0]
    print(next_greater_elements([1, 2, 1]))    # [2, -1, 2]
    print(largest_rectangle_area([2, 1, 5, 6, 2, 3]))  # 10
