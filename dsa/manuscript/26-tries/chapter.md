# Chapter 26: Tries

## What You Will Learn

- What a trie is and how it differs from hash maps and binary search trees
- How to build a TrieNode class from scratch
- How to implement insert, search, and startsWith operations
- How to visualize tries with ASCII diagrams
- Space optimization techniques for tries
- Real-world applications: autocomplete, spell checking, and IP routing
- How to solve classic trie problems: Implement Trie, Word Search II, and Design Add and Search Words

## Why This Chapter Matters

Open your phone and start typing a text message. After two letters, suggestions appear. Type "hel" and your phone offers "hello," "help," "helmet." How does it search thousands of words so fast?

The answer is a trie (pronounced "try," from re**trie**val). A trie is a tree where each path from root to leaf spells out a word. Instead of comparing entire strings like a hash map, a trie walks character by character --- making prefix-based searches almost instant.

Tries appear in autocomplete systems, spell checkers, IP routing tables, and DNA sequence matching. They also show up in medium-to-hard interview problems. This chapter gives you the complete toolkit.

---

## 26.1 What Is a Trie?

A trie (also called a prefix tree) is a tree-like data structure where:
- Each node represents a single character
- The root is empty (represents the empty string)
- Each path from root to a marked node spells a word
- Children share common prefixes

### ASCII Diagram: A Trie Containing "apple", "app", "bat", "ball", "car"

```
                    (root)
                   /  |   \
                  a   b    c
                  |   |    |
                  p   a    a
                  |   |\   |
                  p   t l  r*
                 /|   *  |
                l  *     l*
                |
                e*

  * = end of word marker

  Words stored:
    a -> p -> p -> l -> e*  = "apple"
    a -> p -> p*            = "app"
    b -> a -> t*            = "bat"
    b -> a -> l -> l*       = "ball"
    c -> a -> r*            = "car"
```

### Trie vs Hash Map vs BST

| Operation | Trie | Hash Map | BST |
|-----------|------|----------|-----|
| Search | O(m) | O(m) avg | O(m log n) |
| Insert | O(m) | O(m) avg | O(m log n) |
| Prefix search | O(m) | O(n*m) | O(m log n) |
| Sorted order | Yes (DFS) | No | Yes |
| Space | High | Medium | Medium |

Where `m` = word length, `n` = number of words.

**Key advantage:** Prefix search. A hash map cannot answer "give me all words starting with 'app'" without scanning everything. A trie does it by walking to the 'p' node and collecting descendants.

---

## 26.2 The TrieNode Class

Each node in a trie holds:
- A collection of children (one per character)
- A flag indicating whether this node marks the end of a word

### Python Implementation

```python
class TrieNode:
    def __init__(self):
        self.children = {}  # char -> TrieNode
        self.is_end = False  # marks end of a complete word


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        """Insert a word into the trie."""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True

    def search(self, word):
        """Return True if the word is in the trie."""
        node = self._find_node(word)
        return node is not None and node.is_end

    def starts_with(self, prefix):
        """Return True if any word in the trie starts with the prefix."""
        return self._find_node(prefix) is not None

    def _find_node(self, prefix):
        """Navigate to the node representing the last char of prefix."""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node


# Test
trie = Trie()
trie.insert("apple")
trie.insert("app")
trie.insert("bat")

print(trie.search("apple"))      # Output: True
print(trie.search("app"))        # Output: True
print(trie.search("ap"))         # Output: False (not a complete word)
print(trie.starts_with("ap"))    # Output: True
print(trie.starts_with("ba"))    # Output: True
print(trie.starts_with("car"))   # Output: False
```

### Java Implementation

```java
import java.util.HashMap;
import java.util.Map;

public class Trie {

    static class TrieNode {
        Map<Character, TrieNode> children = new HashMap<>();
        boolean isEnd = false;
    }

    private TrieNode root;

    public Trie() {
        root = new TrieNode();
    }

    public void insert(String word) {
        TrieNode node = root;
        for (char c : word.toCharArray()) {
            node.children.putIfAbsent(c, new TrieNode());
            node = node.children.get(c);
        }
        node.isEnd = true;
    }

    public boolean search(String word) {
        TrieNode node = findNode(word);
        return node != null && node.isEnd;
    }

    public boolean startsWith(String prefix) {
        return findNode(prefix) != null;
    }

    private TrieNode findNode(String prefix) {
        TrieNode node = root;
        for (char c : prefix.toCharArray()) {
            if (!node.children.containsKey(c)) {
                return null;
            }
            node = node.children.get(c);
        }
        return node;
    }

    public static void main(String[] args) {
        Trie trie = new Trie();
        trie.insert("apple");
        trie.insert("app");
        trie.insert("bat");

        System.out.println(trie.search("apple"));     // true
        System.out.println(trie.search("app"));        // true
        System.out.println(trie.search("ap"));         // false
        System.out.println(trie.startsWith("ap"));     // true
        System.out.println(trie.startsWith("ba"));     // true
        System.out.println(trie.startsWith("car"));    // false
    }
}
```

---

## 26.3 Insert Operation --- Step by Step

Let us trace inserting "apple" and "app" into an empty trie.

```
Insert "apple":

Step 1: root -> create 'a'
    (root)
      |
      a

Step 2: 'a' -> create 'p'
    (root)
      |
      a
      |
      p

Step 3: 'p' -> create 'p'
    (root)
      |
      a
      |
      p
      |
      p

Step 4: 'p' -> create 'l'
    (root)
      |
      a
      |
      p
      |
      p
      |
      l

Step 5: 'l' -> create 'e', mark as END
    (root)
      |
      a
      |
      p
      |
      p
      |
      l
      |
      e*

Insert "app":

Step 1: root -> 'a' exists, follow it
Step 2: 'a' -> 'p' exists, follow it
Step 3: 'p' -> 'p' exists, follow it, mark as END

    (root)
      |
      a
      |
      p
      |
      p*     <-- now also marks end of "app"
      |
      l
      |
      e*
```

**Key insight:** "app" shares the prefix path of "apple." We do not create new nodes --- we just mark the existing 'p' node as an end-of-word.

**Complexity:**
- Time: O(m) where m is the word length
- Space: O(m) in the worst case (all new characters)

---

## 26.4 Search and StartsWith --- Step by Step

```
Search "app":
  root -> 'a' (exists) -> 'p' (exists) -> 'p' (exists, is_end=True)
  Return True

Search "ap":
  root -> 'a' (exists) -> 'p' (exists, is_end=False)
  Return False (reached end of query but node is not end-of-word)

StartsWith "ap":
  root -> 'a' (exists) -> 'p' (exists)
  Return True (we only need the prefix to exist)

Search "ace":
  root -> 'a' (exists) -> 'c' (does NOT exist)
  Return False (path does not exist)
```

**Complexity:**
- Time: O(m) for both operations
- Space: O(1) --- no extra space beyond the trie itself

---

## 26.5 Collecting All Words with a Prefix

A powerful trie feature: finding all words that start with a given prefix.

```python
class Trie:
    # ... (previous code) ...

    def words_with_prefix(self, prefix):
        """Return all words in the trie that start with prefix."""
        node = self._find_node(prefix)
        if node is None:
            return []

        results = []
        self._collect_words(node, prefix, results)
        return results

    def _collect_words(self, node, current_word, results):
        """DFS to collect all complete words from this node."""
        if node.is_end:
            results.append(current_word)

        for char, child in sorted(node.children.items()):
            self._collect_words(child, current_word + char, results)


# Test
trie = Trie()
for word in ["apple", "app", "application", "apply", "bat", "ball"]:
    trie.insert(word)

print(trie.words_with_prefix("app"))
# Output: ['app', 'apple', 'application', 'apply']

print(trie.words_with_prefix("ba"))
# Output: ['ball', 'bat']

print(trie.words_with_prefix("z"))
# Output: []
```

---

## 26.6 Space Optimization

### Problem: Tries Can Use a Lot of Memory

Each node stores a dictionary (or array) of children. For lowercase English letters, that is up to 26 entries per node. Most are empty.

### Optimization 1: Array-Based Children (Fixed Alphabet)

When the character set is known and small (like lowercase a-z), use an array instead of a hash map.

```python
class TrieNodeArray:
    def __init__(self):
        self.children = [None] * 26  # a-z
        self.is_end = False

    def _index(self, char):
        return ord(char) - ord('a')
```

**Trade-off:** Slightly more memory per node (26 slots), but faster access (array index vs hash lookup).

### Optimization 2: Compressed Trie (Radix Tree)

Merge chains of single-child nodes into one node storing a string.

```
Standard Trie:               Compressed Trie:

    (root)                      (root)
      |                          |
      r                         rom
      |                        /    \
      o                      an      ulus
      |                       |
      m                       e*
     / \
    a    u
    |    |
    n    l
    |    |
    e*   u
         |
         s*

"romane" and "romulus" share "rom", then diverge.
```

### Optimization 3: HashMap for Sparse Tries

When words use a large character set (Unicode) or the trie is sparse, the dictionary-based approach (shown in our initial implementation) is more space-efficient than arrays.

---

## 26.7 Real-World Applications

### Application 1: Autocomplete System

```python
class AutoComplete:
    def __init__(self, words):
        self.trie = Trie()
        for word in words:
            self.trie.insert(word.lower())

    def suggest(self, prefix, max_results=5):
        """Return up to max_results suggestions for the prefix."""
        all_words = self.trie.words_with_prefix(prefix.lower())
        return all_words[:max_results]


# Test
ac = AutoComplete([
    "hello", "help", "helmet", "hero",
    "her", "heritage", "world", "work"
])

print(ac.suggest("hel"))
# Output: ['hello', 'helmet', 'help']

print(ac.suggest("her"))
# Output: ['her', 'heritage', 'hero']

print(ac.suggest("wo"))
# Output: ['work', 'world']
```

### Application 2: Spell Checker

```python
class SpellChecker:
    def __init__(self, dictionary):
        self.trie = Trie()
        for word in dictionary:
            self.trie.insert(word.lower())

    def check(self, word):
        """Check if a word is spelled correctly."""
        return self.trie.search(word.lower())

    def suggest_corrections(self, word, max_distance=1):
        """Suggest words within edit distance 1."""
        suggestions = []

        # Try deletions
        for i in range(len(word)):
            candidate = word[:i] + word[i+1:]
            if self.trie.search(candidate):
                suggestions.append(candidate)

        # Try replacements
        for i in range(len(word)):
            for c in 'abcdefghijklmnopqrstuvwxyz':
                candidate = word[:i] + c + word[i+1:]
                if candidate != word and self.trie.search(candidate):
                    suggestions.append(candidate)

        # Try insertions
        for i in range(len(word) + 1):
            for c in 'abcdefghijklmnopqrstuvwxyz':
                candidate = word[:i] + c + word[i:]
                if self.trie.search(candidate):
                    suggestions.append(candidate)

        return list(set(suggestions))


# Test
checker = SpellChecker(["hello", "help", "world", "word", "work"])
print(checker.check("hello"))                # True
print(checker.check("helo"))                 # False
print(checker.suggest_corrections("helo"))   # ['hello']
print(checker.suggest_corrections("worl"))   # ['world']
```

### Application 3: IP Routing (Longest Prefix Match)

Routers use tries to find the best matching route for an IP address. Each node represents a bit (0 or 1) of the IP address, and the longest matching prefix determines the route.

```
IP Routing Trie (simplified):

           (root)
          /      \
         0        1
        / \        \
       0   1        0
       |   |       / \
    route1 route2  0   1
                   |   |
                route3 route4

IP: 100 -> matches route3
IP: 101 -> matches route4
IP: 01  -> matches route2
```

---

## 26.8 Delete Operation

Deleting from a trie requires careful handling: remove the end-of-word marker, then clean up nodes that are no longer part of any word.

```python
class TrieWithDelete(Trie):
    def delete(self, word):
        """Delete a word from the trie."""
        self._delete_helper(self.root, word, 0)

    def _delete_helper(self, node, word, depth):
        if node is None:
            return False

        # Reached end of word
        if depth == len(word):
            if not node.is_end:
                return False  # word not found
            node.is_end = False
            # If node has no children, it can be removed
            return len(node.children) == 0

        char = word[depth]
        if char not in node.children:
            return False

        should_delete = self._delete_helper(
            node.children[char], word, depth + 1
        )

        if should_delete:
            del node.children[char]
            # This node can be removed if it is not end of
            # another word and has no other children
            return not node.is_end and len(node.children) == 0

        return False


# Test
trie = TrieWithDelete()
trie.insert("apple")
trie.insert("app")

print(trie.search("apple"))  # True
trie.delete("apple")
print(trie.search("apple"))  # False
print(trie.search("app"))    # True (still exists)
```

```
Before delete "apple":        After delete "apple":

    (root)                        (root)
      |                             |
      a                             a
      |                             |
      p                             p
      |                             |
      p*                            p*
      |
      l                   Nodes 'l' and 'e' removed
      |                   since they belong to no
      e*                  other word.
```

---

## Common Mistakes

1. **Confusing search and startsWith.** `search("app")` requires `is_end=True` at the final node. `startsWith("app")` only needs the path to exist. Many beginners return True for search when they should return False.

2. **Not marking end-of-word.** Inserting "apple" without setting `is_end=True` at 'e' means `search("apple")` returns False. Always set the flag.

3. **Memory leaks on delete.** After unmarking `is_end`, you must remove childless nodes walking back up. Otherwise, the trie grows indefinitely.

4. **Using arrays for large alphabets.** A 26-slot array per node works for lowercase English. For Unicode strings, use a hash map or you will waste enormous amounts of memory.

5. **Case sensitivity.** Forgetting to normalize to lowercase before insert/search leads to missed matches. Always convert to a consistent case.

---

## Best Practices

- **Choose the right children structure.** Use arrays for fixed small alphabets (a-z). Use hash maps for variable or large character sets.
- **Add a count field.** Track how many words pass through each node. This enables frequency-based autocomplete and efficient prefix counting.
- **Consider compressed tries (radix trees)** for datasets with many long words sharing prefixes. They reduce node count dramatically.
- **Use iterative over recursive** for insert and search. Iterative is simpler and avoids stack overflow on very long words.
- **Test with empty string.** Inserting and searching for "" is a valid edge case. Your trie should handle it (the root itself is the end marker).

---

## Quick Summary

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|-----------------|
| Insert | O(m) | O(m) worst case |
| Search | O(m) | O(1) |
| StartsWith | O(m) | O(1) |
| Delete | O(m) | O(1) |
| Prefix collection | O(m + k) | O(k) |

Where m = word length, k = number of matching words.

A trie stores strings as paths in a tree. It excels at prefix-based operations that hash maps cannot do efficiently. The trade-off is higher memory usage, which can be mitigated with compression or careful alphabet sizing.

---

## Key Points

- A trie is a tree where each root-to-node path represents a prefix and each root-to-end path represents a complete word.
- The TrieNode has two fields: a children map and an is_end boolean.
- Insert, search, and startsWith all run in O(m) time where m is the word/prefix length.
- Tries enable prefix-based operations (autocomplete, spell check) that hash maps cannot do efficiently.
- Space optimization through arrays (small alphabet), hash maps (large alphabet), or compression (radix trees) is essential for production use.

---

## Practice Questions

1. What is the maximum number of nodes in a trie that stores n words, each of length m? What is the minimum?

2. How would you modify the trie to be case-insensitive? What about supporting both letters and digits?

3. Explain the difference between a trie and a hash map for storing a dictionary. When would you choose each?

4. How would you implement a "count words with prefix" operation? What field would you add to TrieNode?

5. If you need to find the longest common prefix of all words in the trie, how would you do it?

---

## LeetCode-Style Problems

### Problem 1: Implement Trie (Prefix Tree) --- LeetCode 208 (Medium)

**Problem:** Implement a Trie class with insert, search, and startsWith methods.

```python
class Trie:
    def __init__(self):
        self.root = {}

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node:
                node[char] = {}
            node = node[char]
        node['#'] = True  # end marker

    def search(self, word):
        node = self._find(word)
        return node is not None and '#' in node

    def startsWith(self, prefix):
        return self._find(prefix) is not None

    def _find(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node:
                return None
            node = node[char]
        return node

# Test
trie = Trie()
trie.insert("apple")
print(trie.search("apple"))      # True
print(trie.search("app"))        # False
print(trie.startsWith("app"))    # True
trie.insert("app")
print(trie.search("app"))        # True
```

**Note:** This compact version uses nested dictionaries with '#' as the end marker. Both approaches (class-based and dict-based) are valid.

**Complexity:** All operations O(m), Space O(total characters across all words)

---

### Problem 2: Design Add and Search Words --- LeetCode 211 (Medium)

**Problem:** Design a data structure that supports `addWord(word)` and `search(word)` where search can contain '.' as a wildcard matching any single character.

```python
class WordDictionary:
    def __init__(self):
        self.root = {}

    def addWord(self, word):
        node = self.root
        for char in word:
            if char not in node:
                node[char] = {}
            node = node[char]
        node['#'] = True

    def search(self, word):
        return self._search_helper(self.root, word, 0)

    def _search_helper(self, node, word, index):
        if index == len(word):
            return '#' in node

        char = word[index]

        if char == '.':
            # Wildcard: try all children
            for key in node:
                if key != '#' and self._search_helper(
                    node[key], word, index + 1
                ):
                    return True
            return False
        else:
            if char not in node:
                return False
            return self._search_helper(node[char], word, index + 1)


# Test
wd = WordDictionary()
wd.addWord("bad")
wd.addWord("dad")
wd.addWord("mad")

print(wd.search("pad"))   # False
print(wd.search("bad"))   # True
print(wd.search(".ad"))   # True (matches bad, dad, mad)
print(wd.search("b.."))   # True (matches bad)
print(wd.search("b."))    # False (too short)
```

**Complexity:** Time O(m) without wildcards, O(26^m) worst case with all dots. Space O(total chars).

---

### Problem 3: Word Search II --- LeetCode 212 (Hard)

**Problem:** Given a 2D board of characters and a list of words, find all words that can be formed by sequentially adjacent cells (horizontal or vertical). Each cell may be used only once per word.

```python
def find_words(board, words):
    # Build trie from word list
    root = {}
    for word in words:
        node = root
        for char in word:
            if char not in node:
                node[char] = {}
            node = node[char]
        node['#'] = word  # store the complete word at end

    rows, cols = len(board), len(board[0])
    result = set()

    def dfs(r, c, node):
        if r < 0 or r >= rows or c < 0 or c >= cols:
            return
        char = board[r][c]
        if char not in node:
            return

        next_node = node[char]

        if '#' in next_node:
            result.add(next_node['#'])

        # Mark as visited
        board[r][c] = '.'

        # Explore 4 directions
        dfs(r + 1, c, next_node)
        dfs(r - 1, c, next_node)
        dfs(r, c + 1, next_node)
        dfs(r, c - 1, next_node)

        # Restore
        board[r][c] = char

        # Prune: remove leaf nodes
        if not next_node or (len(next_node) == 1 and '#' in next_node):
            del node[char]

    for r in range(rows):
        for c in range(cols):
            dfs(r, c, root)

    return list(result)


# Test
board = [
    ['o','a','a','n'],
    ['e','t','a','e'],
    ['i','h','k','r'],
    ['i','f','l','v']
]
words = ["oath", "pea", "eat", "rain"]
print(find_words(board, words))
# Output: ['oath', 'eat']
```

**Why trie helps:** Without a trie, you would search the board for each word separately (expensive). With a trie, you search all words simultaneously --- if no word starts with the current path, you prune immediately.

**Complexity:** Time O(rows * cols * 4^L) where L = max word length. Space O(total chars in words).

---

## What Is Next?

You now understand tries --- a specialized tree that makes string operations like prefix search, autocomplete, and spell checking fast and elegant.

In the next chapter, we explore **Union-Find (Disjoint Set Union)** --- a data structure for grouping elements and quickly answering "are these two elements connected?" Think of it as managing friend groups: Union-Find can merge groups and check membership in nearly constant time.
