# PATTERN NAME: Greedy
# DIFFICULTY: Medium | FREQUENCY: Very High (intervals, jump game, scheduling at all companies)

# WHEN TO USE:
# - When a locally optimal choice at each step leads to a globally optimal solution.
# - Interval scheduling (merge, meeting rooms, non-overlapping).
# - Activity selection, job sequencing, Jump Game variants.
# - Huffman coding, fractional knapsack.
# - When you can prove the greedy-choice property holds.

# CORE IDEA (INTUITION):
# - At each step make the choice that looks best right now; never reconsider (no backtracking).
# - Works when: greedy-choice property + optimal substructure.
# - Key question: "Can I prove that being greedy never hurts?"

# INVARIANTS:
# - The greedy choice is always part of some optimal solution.
# - After a greedy choice, the remaining problem is a smaller instance of the same problem.
# - Sorting is often a prerequisite.

# COMMON MISTAKES:
# - Applying greedy without proving the greedy-choice property.
# - Sorting by the wrong key (start vs end time matters).
# - Not considering edge cases (empty input, single element).
# - For intervals: sort by START for merge, by END for selection/removal.

# TIME & SPACE:
# - Most greedy: O(n log n) due to sorting, O(1) extra space.
# - Meeting Rooms II: O(n log n) time, O(n) space.
# - Task Scheduler: O(n) time, O(1) space (26 letters).

# RELATED PROBLEMS:
# - Merge Intervals (LC 56)
# - Non-overlapping Intervals (LC 435)
# - Meeting Rooms II (LC 253)
# - Jump Game (LC 55) / Jump Game II (LC 45)
# - Task Scheduler (LC 621)
# - Gas Station (LC 134)
# - Partition Labels (LC 763)

from collections import Counter


# === INTERVAL SCHEDULING ===

# Merge Intervals - sort by start, merge overlapping
def merge(intervals: list[list[int]]) -> list[list[int]]:
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]

    for i in range(1, len(intervals)):
        last = merged[-1]
        if intervals[i][0] <= last[1]:
            last[1] = max(last[1], intervals[i][1])
        else:
            merged.append(intervals[i])

    return merged


# Insert Interval
def insert(intervals: list[list[int]], new_interval: list[int]) -> list[list[int]]:
    result: list[list[int]] = []
    i = 0

    # intervals ending before new_interval starts
    while i < len(intervals) and intervals[i][1] < new_interval[0]:
        result.append(intervals[i])
        i += 1

    # merge overlapping intervals with new_interval
    while i < len(intervals) and intervals[i][0] <= new_interval[1]:
        new_interval[0] = min(new_interval[0], intervals[i][0])
        new_interval[1] = max(new_interval[1], intervals[i][1])
        i += 1
    result.append(new_interval)

    # remaining intervals
    while i < len(intervals):
        result.append(intervals[i])
        i += 1

    return result


# Non-overlapping Intervals (minimum removals) - sort by END time
def erase_overlap_intervals(intervals: list[list[int]]) -> int:
    intervals.sort(key=lambda x: x[1])
    removals = 0
    prev_end = float("-inf")

    for start, end in intervals:
        if start >= prev_end:
            prev_end = end  # keep this interval
        else:
            removals += 1   # remove (overlaps)

    return removals


# Meeting Rooms II (minimum rooms) - sweep two sorted arrays
def min_meeting_rooms(intervals: list[list[int]]) -> int:
    starts = sorted(i[0] for i in intervals)
    ends = sorted(i[1] for i in intervals)

    rooms = max_rooms = 0
    s = e = 0

    while s < len(starts):
        if starts[s] < ends[e]:
            rooms += 1
            s += 1
        else:
            rooms -= 1
            e += 1
        max_rooms = max(max_rooms, rooms)

    return max_rooms


# === JUMP GAME ===

# Jump Game I - can you reach the last index?
def can_jump(nums: list[int]) -> bool:
    max_reach = 0
    for i in range(len(nums)):
        if i > max_reach:
            return False
        max_reach = max(max_reach, i + nums[i])
    return True


# Jump Game II - minimum jumps to reach the end
def jump(nums: list[int]) -> int:
    jumps = cur_end = farthest = 0

    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == cur_end:
            jumps += 1
            cur_end = farthest

    return jumps


# === TASK SCHEDULING ===

# Task Scheduler - minimum intervals with cooldown n
def least_interval(tasks: list[str], n: int) -> int:
    freq = Counter(tasks)
    max_freq = max(freq.values())
    max_count = sum(1 for f in freq.values() if f == max_freq)

    # (max_freq - 1) groups of (n + 1) slots + a final group of max_count tasks
    return max(len(tasks), (max_freq - 1) * (n + 1) + max_count)


# === GAS STATION ===
def can_complete_circuit(gas: list[int], cost: list[int]) -> int:
    total_surplus = current_surplus = start = 0

    for i in range(len(gas)):
        diff = gas[i] - cost[i]
        total_surplus += diff
        current_surplus += diff
        if current_surplus < 0:
            start = i + 1
            current_surplus = 0

    return start if total_surplus >= 0 else -1


if __name__ == "__main__":
    print(merge([[1, 3], [2, 6], [8, 10], [15, 18]]))  # [[1, 6], [8, 10], [15, 18]]
    print(erase_overlap_intervals([[1, 2], [2, 3], [3, 4], [1, 3]]))  # 1
    print(can_jump([2, 3, 1, 1, 4]))    # True
    print(can_jump([3, 2, 1, 0, 4]))    # False
    print(jump([2, 3, 1, 1, 4]))        # 2
    print(least_interval(["A", "A", "A", "B", "B", "B"], 2))  # 8
    print(can_complete_circuit([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]))  # 3
