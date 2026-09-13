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
        self.word: str | None = None  # used by find_words (Word Search II) to stash the full word


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


# === WORD SEARCH II (LC 212): trie + grid DFS ===
# Classic Google problem combining two structures already here. Build a trie of all words, then DFS
# the grid following only paths that exist in the trie (prunes dead branches early). Storing the full
# word on the terminal node avoids rebuilding strings during DFS.
def find_words(board: list[list[str]], words: list[str]) -> list[str]:
    root = TrieNode()
    for word in words:
        node = root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.is_end = True
        node.word = word  # stash the word on the terminal node

    rows, cols = len(board), len(board[0])
    found: list[str] = []

    def dfs(r: int, c: int, node: TrieNode) -> None:
        ch = board[r][c]
        if ch not in node.children:
            return
        nxt = node.children[ch]
        if nxt.is_end:
            found.append(nxt.word)
            nxt.is_end = False  # dedupe: don't report the same word twice

        board[r][c] = "#"  # mark visited
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != "#":
                dfs(nr, nc, nxt)
        board[r][c] = ch  # restore

    for r in range(rows):
        for c in range(cols):
            dfs(r, c, root)

    return found


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

    # Word Search II
    board = [
        ["o", "a", "a", "n"],
        ["e", "t", "a", "e"],
        ["i", "h", "k", "r"],
        ["i", "f", "l", "v"],
    ]
    print(sorted(find_words(board, ["oath", "pea", "eat", "rain"])))  # ['eat', 'oath']
