# ALGORITHM: Rabin-Karp String Search (rolling hash)
# CATEGORY: String / Pattern Matching / Hashing
# DIFFICULTY: Medium | FREQUENCY: Medium (substring search, plagiarism/dup detection at Google/Amazon)

# PROBLEM STATEMENT:
# Given a text and a pattern, find the starting index of the pattern's first occurrence using Rabin-Karp.

# WHEN TO USE:
# - Efficient substring search, especially for multiple patterns in the same text.
# - When a rolling hash can turn window comparisons into O(1) updates.

# CORE IDEA (INTUITION):
# Hash the pattern and each text window of the same length. Compare hashes first; only on a hash
# match do a direct character comparison to rule out collisions. A rolling hash updates the window
# hash in O(1) as it slides.

# INVARIANTS:
# - The hash function minimizes collisions (large prime modulus).
# - The rolling update correctly removes the outgoing char and adds the incoming char.

# TIME: O(n + m) average, O(n * m) worst case (many collisions)  |  SPACE: O(1)

# COMMON MISTAKES:
# - Skipping the character-by-character verification (hash collisions cause false positives).
# - Incorrect rolling-hash update (wrong power weight or missing modulo).
# - Using a modulus small enough to overflow / collide often.

# RELATED PROBLEMS:
# - Find the Index of the First Occurrence in a String (LC 28)
# - Repeated DNA Sequences (LC 187)
# - Longest Duplicate Substring (LC 1044)


def rabin_karp(text: str, pattern: str) -> int:
    BASE = 256          # treat chars as base-256 (ASCII range)
    MOD = 10**9 + 7     # large prime to avoid overflow / reduce collisions
    m = len(pattern)
    n = len(text)

    if m > n:
        return -1

    # STEP 1: hash of the pattern
    pattern_hash = 0
    for i in range(m):
        pattern_hash = (pattern_hash * BASE + ord(pattern[i])) % MOD

    # STEP 2: precompute BASE^(m-1) % MOD (weight of the leftmost char)
    power = 1
    for _ in range(m - 1):
        power = (power * BASE) % MOD

    # STEP 3: hash of the first window
    current_hash = 0
    for i in range(m):
        current_hash = (current_hash * BASE + ord(text[i])) % MOD

    def verify_match(start: int) -> bool:
        return text[start:start + m] == pattern

    # STEP 4: check the first window
    if current_hash == pattern_hash and verify_match(0):
        return 0

    # STEP 5: slide the window with a rolling hash
    for i in range(m, n):
        old_char = text[i - m]  # leaving the window
        current_hash = (current_hash - (ord(old_char) * power) % MOD + MOD) % MOD

        new_char = text[i]      # entering the window
        current_hash = (current_hash * BASE + ord(new_char)) % MOD

        # STEP 6: hash match + verification
        if current_hash == pattern_hash and verify_match(i - m + 1):
            return i - m + 1

    return -1


# EXAMPLE USAGE:
if __name__ == "__main__":
    print(rabin_karp("ababcabcabababd", "ababd"))  # 10
