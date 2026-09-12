# Scratch file for quickly testing a single problem in your own editor.
#
# Problem: Brace Expansion (LC 1087)
# Input:  s = "{a,b}c{d,e}f"
# Output: ["acdf", "acef", "bcdf", "bcef"]
#
# - 1 <= len(s) <= 50
# - s consists of curly brackets '{}', commas ',', and lowercase English letters.
# - No nested curly brackets; characters inside a pair are distinct.


def expand(s: str) -> list[str]:
    # 1. Parse into groups: each group is a sorted list of choices.
    groups: list[list[str]] = []
    i = 0
    while i < len(s):
        if s[i] == "{":
            j = i + 1
            while s[j] != "}":
                j += 1
            groups.append(sorted(s[i + 1:j].split(",")))
            i = j + 1
        else:
            groups.append([s[i]])
            i += 1

    # 2. Backtrack over the cartesian product of the groups.
    res: list[str] = []

    def backtrack(idx: int, path: str) -> None:
        if idx == len(groups):
            res.append(path)
            return
        for char in groups[idx]:
            backtrack(idx + 1, path + char)

    backtrack(0, "")
    return res


# Test cases
if __name__ == "__main__":
    print(expand("{a,b}c{d,e}f"))   # ['acdf', 'acef', 'bcdf', 'bcef']
    print(expand("abcd"))           # ['abcd']
    print(expand("{a,b,c}"))        # ['a', 'b', 'c']
    print(expand("a{b,c}d{e,f}"))   # ['abde', 'abdf', 'acde', 'acdf']
