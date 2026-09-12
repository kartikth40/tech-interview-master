# PATTERN NAME: Bit Manipulation
# DIFFICULTY: Medium | FREQUENCY: High (XOR tricks, masks, single-number at Google/Amazon)

# WHEN TO USE:
# - Space-optimized flags/sets (bitmask).
# - Finding unique/missing numbers (XOR tricks).
# - Subset generation via bitmask.
# - Counting bits, power-of-two checks.

# CORE IDEA (INTUITION):
# - Numbers are sequences of bits; use bitwise ops to manipulate them directly.
# - XOR: a ^ a = 0, a ^ 0 = a  (cancels pairs).
# - AND with (1 << i): check the i-th bit.
# - OR with (1 << i): set the i-th bit.
# - n & (n - 1): clears the lowest set bit.

# COMMON OPERATIONS:
# - Check i-th bit:  (num >> i) & 1
# - Set i-th bit:    num | (1 << i)
# - Clear i-th bit:  num & ~(1 << i)
# - Toggle i-th bit: num ^ (1 << i)
# - Lowest set bit:  num & (-num)
# - Clear lowest set bit: num & (num - 1)

# COMMON MISTAKES:
# - Python ints are arbitrary precision (no 32-bit overflow); mask with & 0xFFFFFFFF when a
#   fixed-width result is required (e.g. LC 371 "Sum of Two Integers").
# - Operator precedence: bitwise ops are lower than comparison; parenthesize.
# - Confusing logical (and/or) with bitwise (&/|).

# TIME & SPACE:
# - Most bit operations: O(1) or O(number of bits) = O(32).
# - Subset generation: O(2^n).

# RELATED PROBLEMS:
# - Single Number (LC 136) / Single Number II (LC 137) / III (LC 260)
# - Number of 1 Bits (LC 191)
# - Counting Bits (LC 338)
# - Missing Number (LC 268)
# - Subsets (LC 78) - bitmask approach
# - Power of Two (LC 231)


# Single Number - every element appears twice except one (XOR cancels pairs)
def single_number(nums: list[int]) -> int:
    result = 0
    for num in nums:
        result ^= num
    return result


# Number of 1 Bits (Hamming weight) - Brian Kernighan's algorithm
def hamming_weight(n: int) -> int:
    count = 0
    while n:
        n &= n - 1  # clear the lowest set bit
        count += 1
    return count


# Counting Bits - count set bits for every number 0..n
# dp[i] = dp[i >> 1] + (i & 1)
def count_bits(n: int) -> list[int]:
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        dp[i] = dp[i >> 1] + (i & 1)
    return dp


# Missing Number - XOR all indices and values
def missing_number(nums: list[int]) -> int:
    missing = len(nums)
    for i, num in enumerate(nums):
        missing ^= i ^ num
    return missing


# Power of Two - a power of two has exactly one set bit
def is_power_of_two(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0


# Generate all subsets using bitmask
def subsets_bitmask(nums: list[int]) -> list[list[int]]:
    n = len(nums)
    result: list[list[int]] = []

    for mask in range(1 << n):  # 2^n masks
        subset: list[int] = []
        for i in range(n):
            if mask & (1 << i):  # is the i-th bit set?
                subset.append(nums[i])
        result.append(subset)

    return result


# Sum of Two Integers without + or - (mask to 32 bits)
def get_sum(a: int, b: int) -> int:
    mask = 0xFFFFFFFF
    while b & mask:
        carry = (a & b) << 1
        a = a ^ b
        b = carry
    a &= mask
    # handle negative results (32-bit two's complement)
    return a if a <= 0x7FFFFFFF else ~(a ^ mask)


if __name__ == "__main__":
    print(single_number([4, 1, 2, 1, 2]))   # 4
    print(hamming_weight(11))                # 3 (1011)
    print(count_bits(5))                     # [0, 1, 1, 2, 1, 2]
    print(missing_number([3, 0, 1]))         # 2
    print(is_power_of_two(16))               # True
    print(is_power_of_two(18))               # False
    print(subsets_bitmask([1, 2, 3]))
    # [[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]
    print(get_sum(2, 3))                     # 5
