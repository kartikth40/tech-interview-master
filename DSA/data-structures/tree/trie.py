# DATA STRUCTURE: Trie (Prefix Tree)
# DIFFICULTY: Medium | FREQUENCY: High (autocomplete, word search, prefix queries at Google/Amazon)

# A trie is a tree-like data structure that stores a dynamic set of strings, where the keys are
# usually strings. It is used for efficient retrieval of strings, especially for prefix-based searches.

# Time Complexity:
# - Insertion: O(m), where m is the length of the word being inserted.
# - Search: O(m), where m is the length of the word being searched.
# - Prefix Search: O(m), where m is the length of the prefix being searched.

# When to use:
# - When you need to store a large number of strings and perform quick lookups.
# - When you want to implement features like autocomplete or spell checking.
# - When you need to efficiently find all words with a given prefix.

# COMMON MISTAKES:
# - Confusing "word exists" (is_end flag) with "prefix exists" (node reachable).
# - Forgetting to set is_end at the end of insert.
# - Not handling the empty-string edge case.
# - Using a fixed-size array of 26 when the charset is unknown (a dict is safer/general).

# RELATED PROBLEMS:
# - Implement Trie (Prefix Tree) (LC 208)
# - Design Add and Search Words Data Structure (LC 211)
# - Word Search II (LC 212)
# - Replace Words (LC 648)


class TrieNode:
    def __init__(self) -> None:
        self.children: dict[str, "TrieNode"] = {}
        self.is_end = False


class Trie:
    def __init__(self) -> None:
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        cur = self.root
        for ch in word:
            if ch not in cur.children:
                cur.children[ch] = TrieNode()
            cur = cur.children[ch]
        cur.is_end = True

    def search(self, word: str) -> bool:
        cur = self.root
        for ch in word:
            if ch not in cur.children:
                return False
            cur = cur.children[ch]
        return cur.is_end

    def starts_with(self, prefix: str) -> bool:
        cur = self.root
        for ch in prefix:
            if ch not in cur.children:
                return False
            cur = cur.children[ch]
        return True


# Examples (only run when executed directly)
if __name__ == "__main__":
    trie = Trie()
    trie.insert("apple")
    trie.insert("app")
    trie.insert("banana")

    print(trie.search("apple"))      # True
    print(trie.search("app"))        # True
    print(trie.search("ap"))         # False
    print(trie.starts_with("ap"))    # True
    print(trie.starts_with("ban"))   # True
    print(trie.starts_with("cat"))   # False
