# ALGORITHM: KMP (Knuth-Morris-Pratt) String Search
# CATEGORY: String / Pattern Matching
# DIFFICULTY: Hard | FREQUENCY: Medium (substring search, repeated-pattern at Google/Amazon)

# PROBLEM STATEMENT:
# Given a text and a pattern, find the starting index of the pattern's first occurrence using KMP.

# WHEN TO USE:
# - Efficient substring search within a larger string.
# - Avoid re-checking characters already matched.
# - Long patterns/texts where naive O(n*m) search is too slow.

# Rabin-Karp vs KMP:
# - Rabin-Karp hashes windows; good for multiple-pattern search.
# - KMP preprocesses the pattern to skip comparisons; O(n + m) guaranteed in all cases.

# CORE IDEA (INTUITION):
# Precompute the LPS (Longest Prefix which is also Suffix) array for the pattern. On a mismatch,
# jump the pattern pointer using LPS instead of re-scanning the text.

# INVARIANTS:
# - lps[i] = length of the longest proper prefix of pattern[0..i] that is also a suffix.
# - On mismatch, the text pointer never moves backward.

# TIME: O(n + m)  |  SPACE: O(m) for the LPS array

# COMMON MISTAKES:
# - Building the LPS array incorrectly (mishandling the fallback while-loop).
# - Moving the text pointer back on a mismatch.
# - Not handling empty pattern/text edge cases.

# RELATED PROBLEMS:
# - Find the Index of the First Occurrence in a String (LC 28)
# - Repeated Substring Pattern (LC 459)
# - Shortest Palindrome (LC 214)


# Build the Longest-Proper-Prefix-which-is-also-Suffix array.
def build_lps(s: str) -> list[int]:
    lps = [0] * len(s)

    for i in range(1, len(lps)):
        prev_idx = lps[i - 1]  # start with the previous LPS length

        # Jump back until a match or the start
        while prev_idx > 0 and s[i] != s[prev_idx]:
            prev_idx = lps[prev_idx - 1]

        # Extend the length if characters match; otherwise it stays 0
        lps[i] = prev_idx + (1 if s[i] == s[prev_idx] else 0)

    return lps


# Search for 'pattern' in 'text'; return the starting index or -1 if not found.
def kmp(text: str, pattern: str) -> int:
    if not pattern:
        return 0

    lps = build_lps(pattern)
    i = 0  # text pointer
    j = 0  # pattern pointer

    while i < len(text):
        if text[i] == pattern[j]:
            i += 1
            j += 1
            if j == len(pattern):
                return i - j  # found; starting index
        elif j > 0:
            j = lps[j - 1]  # mismatch: reuse previous match info (don't move i)
        else:
            i += 1  # no match at the pattern start; advance text pointer

    return -1  # not found


# EXAMPLE USAGE:
# text:    ababcabcabababd
# pattern:            ababd  -> first occurrence starts at index 10
if __name__ == "__main__":
    print(build_lps("ababd"))               # [0, 0, 1, 2, 0]
    print(kmp("ababcabcabababd", "ababd"))  # 10
