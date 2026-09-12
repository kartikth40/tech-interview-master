# PATTERN NAME: Suffix Trie for Counting Distinct Substrings
# DIFFICULTY: Hard | FREQUENCY: Medium (distinct-substring / suffix-structure problems at Google)

# PROBLEM STATEMENT: Given a string s, count the number of distinct substrings of s.

# WHEN TO USE:
# - Count distinct substrings in a string.
# - Efficiently store and query all suffixes of a string.
# - String processing, pattern matching, substring queries.

# CORE IDEA (INTUITION):
# - A suffix trie stores all suffixes; each root-to-node path is a distinct substring.
# - The number of distinct substrings = number of trie nodes (excluding the root).
# - A suffix array + LCP array counts distinct substrings more efficiently.

# INVARIANTS:
# - Each trie node represents a unique substring.
# - Distinct substrings = node count (excluding the root).
# - Suffix-array approach: sum over suffixes of (length - LCP with the previous suffix).

# COMMON MISTAKES:
# - Counting the empty substring when the problem excludes it.
# - Overcounting duplicate substrings.
# - Using brute force on large inputs (TLE).
# - Missing some suffixes when building the trie/array.

# TIME & SPACE:
# - Brute force: O(n^3) time, O(n^2) space.
# - Suffix Trie: O(n^2) time and space.
# - Suffix Array + LCP: O(n^2 log n) here (simple comparator); O(n) extra space.

# RELATED PROBLEMS:
# - Longest Repeating Substring
# - Longest Common Substring of Two Strings
# - Distinct Echo Substrings (LC 1316)


def count_subs(s: str) -> int:
    # return brute_force(s)
    # return suffix_trie(s)
    return suffix_array_lcp(s)


def brute_force(s: str) -> int:
    # Time: O(n^3), Space: O(n^2)
    seen: set[str] = set()
    n = len(s)
    for i in range(n):
        cur = ""
        for j in range(i, n):
            cur += s[j]
            seen.add(cur)
    return len(seen)


def suffix_trie(s: str) -> int:
    # Time: O(n^2), Space: O(n^2)
    root: dict[str, dict] = {}
    count = 0

    for i in range(len(s)):
        node = root
        for j in range(i, len(s)):
            ch = s[j]
            if ch not in node:
                node[ch] = {}
                count += 1  # a new node = a new distinct substring
            node = node[ch]

    return count


def suffix_array_lcp(s: str) -> int:
    # Build a suffix array (by starting index), then sum (length - LCP with previous suffix).
    n = len(s)
    if n == 0:
        return 0

    suffixes = sorted(range(n), key=lambda i: s[i:])

    def lcp(i: int, j: int) -> int:
        length = 0
        while i < n and j < n and s[i] == s[j]:
            length += 1
            i += 1
            j += 1
        return length

    result = n - suffixes[0]  # first suffix contributes all its prefixes
    for i in range(1, n):
        cur_len = n - suffixes[i]
        common = lcp(suffixes[i], suffixes[i - 1])
        result += cur_len - common

    return result


if __name__ == "__main__":
    print(count_subs("abc"))  # 6 (a, b, c, ab, bc, abc)
    print(count_subs("aaa"))  # 3 (a, aa, aaa)
