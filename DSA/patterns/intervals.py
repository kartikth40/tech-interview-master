# PATTERN NAME: Interval Problems
# DIFFICULTY: Medium | FREQUENCY: Very High (merge/insert/meeting-rooms at Google/Meta/Amazon)

# WHEN TO USE:
# - Merge overlapping intervals.
# - Find conflicts/overlaps between intervals.
# - Insert a new interval into a sorted list.
# - Minimum resources for overlapping tasks (meeting rooms).
# - Sweep-line problems.

# CORE IDEA (INTUITION):
# - Sort intervals (usually by start, sometimes by end).
# - Process left-to-right, tracking the "active" state.
# - [a, b] and [c, d] overlap iff a <= d AND c <= b.
# - For minimum resources: sweep line (separate starts and ends).

# INVARIANTS:
# - After sorting by start: if current.start > prev.end, there's no overlap.
# - Sweep line: active count = starts seen - ends seen.
# - For selection problems: sort by END time (greedy).

# COMMON MISTAKES:
# - Sorting by start when you should sort by end (selection vs merge).
# - Off-by-one on touching intervals ([1,2] vs [2,3]) - depends on the problem.
# - Not handling empty input.
# - Forgetting to take max when extending a merged interval's end.
# - Sweep line: ends should process before starts at the same time.

# TIME & SPACE:
# - All interval problems: O(n log n) time (sorting), O(n) space.

# RELATED PROBLEMS:
# - Merge Intervals (LC 56)
# - Insert Interval (LC 57)
# - Non-overlapping Intervals (LC 435)
# - Meeting Rooms (LC 252) / Meeting Rooms II (LC 253)
# - Interval List Intersections (LC 986)
# - Minimum Number of Arrows to Burst Balloons (LC 452)


# Merge Intervals
def merge(intervals: list[list[int]]) -> list[list[int]]:
    intervals.sort(key=lambda x: x[0])
    result = [intervals[0]]

    for i in range(1, len(intervals)):
        last = result[-1]
        if intervals[i][0] <= last[1]:
            last[1] = max(last[1], intervals[i][1])
        else:
            result.append(intervals[i])

    return result


# Insert Interval into a sorted, non-overlapping list
def insert(intervals: list[list[int]], new_interval: list[int]) -> list[list[int]]:
    result: list[list[int]] = []
    i = 0

    while i < len(intervals) and intervals[i][1] < new_interval[0]:
        result.append(intervals[i])
        i += 1

    while i < len(intervals) and intervals[i][0] <= new_interval[1]:
        new_interval[0] = min(new_interval[0], intervals[i][0])
        new_interval[1] = max(new_interval[1], intervals[i][1])
        i += 1
    result.append(new_interval)

    while i < len(intervals):
        result.append(intervals[i])
        i += 1

    return result


# Interval Intersection (two sorted lists)
def interval_intersection(first_list: list[list[int]], second_list: list[list[int]]) -> list[list[int]]:
    result: list[list[int]] = []
    i = j = 0

    while i < len(first_list) and j < len(second_list):
        lo = max(first_list[i][0], second_list[j][0])
        hi = min(first_list[i][1], second_list[j][1])

        if lo <= hi:
            result.append([lo, hi])

        # advance the one that ends first
        if first_list[i][1] < second_list[j][1]:
            i += 1
        else:
            j += 1

    return result


# Meeting Rooms - can attend all meetings (no overlaps)?
def can_attend_meetings(intervals: list[list[int]]) -> bool:
    intervals.sort(key=lambda x: x[0])
    for i in range(1, len(intervals)):
        if intervals[i][0] < intervals[i - 1][1]:
            return False
    return True


# Meeting Rooms II - minimum rooms needed (sweep line)
def min_meeting_rooms(intervals: list[list[int]]) -> int:
    events: list[tuple[int, int]] = []
    for start, end in intervals:
        events.append((start, 1))   # meeting starts
        events.append((end, -1))    # meeting ends

    # sort by time; on a tie, end (-1) before start (+1)
    events.sort(key=lambda e: (e[0], e[1]))

    rooms = max_rooms = 0
    for _, delta in events:
        rooms += delta
        max_rooms = max(max_rooms, rooms)

    return max_rooms


# Minimum Number of Arrows to Burst Balloons - sort by end, shoot at earliest end
def find_min_arrow_shots(points: list[list[int]]) -> int:
    points.sort(key=lambda x: x[1])
    arrows = 1
    prev_end = points[0][1]

    for i in range(1, len(points)):
        if points[i][0] > prev_end:
            arrows += 1
            prev_end = points[i][1]

    return arrows


if __name__ == "__main__":
    print(merge([[1, 3], [2, 6], [8, 10], [15, 18]]))  # [[1, 6], [8, 10], [15, 18]]
    print(insert([[1, 3], [6, 9]], [2, 5]))            # [[1, 5], [6, 9]]
    print(interval_intersection([[0, 2], [5, 10]], [[1, 5], [8, 12]]))  # [[1, 2], [5, 5], [8, 10]]
    print(can_attend_meetings([[0, 30], [5, 10], [15, 20]]))  # False
    print(min_meeting_rooms([[0, 30], [5, 10], [15, 20]]))    # 2
    print(find_min_arrow_shots([[10, 16], [2, 8], [1, 6], [7, 12]]))  # 2
