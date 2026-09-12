# ALGORITHM: Primality Testing (Sieve of Eratosthenes + single check)
# CATEGORY: Array / Math
# DIFFICULTY: Easy | FREQUENCY: Medium (math-flavored problems, count-primes at Amazon/Microsoft)

# PROBLEM:
# Determine which numbers are prime. For many queries up to n, precompute with a sieve;
# for a single number, trial-divide up to sqrt(n).

# INTUITION:
# Sieve: every composite has a smallest prime factor; mark multiples of each prime starting at i*i
# (smaller multiples are already marked by smaller primes).

# TIME: sieve O(n log log n), single check O(sqrt(n))  |  SPACE: O(n) for the sieve

# COMMON MISTAKES:
# - Forgetting that 0 and 1 are not prime.
# - Starting the inner marking loop at 2*i instead of i*i (correct but redundant work).
# - Looping i while i <= n instead of i*i <= n in the outer sieve loop.

# RELATED PROBLEMS:
# - Count Primes (LC 204)
# - Ugly Number II (LC 264)


# For multiple queries: Sieve of Eratosthenes.
# If checking many numbers up to n:
def sieve_of_eratosthenes(n: int) -> list[bool]:
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False

    i = 2
    while i * i <= n:
        if is_prime[i]:
            # Mark all multiples as not prime.
            # Start from i*i to avoid redundant work.
            for j in range(i * i, n + 1, i):
                is_prime[j] = False
        i += 1

    return is_prime  # list where is_prime[i] tells if i is prime


# For a single number: trial division up to sqrt(n).
def is_prime(n: int) -> bool:
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


if __name__ == "__main__":
    sieve = sieve_of_eratosthenes(20)
    print([i for i, p in enumerate(sieve) if p])  # [2, 3, 5, 7, 11, 13, 17, 19]
    print(is_prime(17))  # True
    print(is_prime(18))  # False
