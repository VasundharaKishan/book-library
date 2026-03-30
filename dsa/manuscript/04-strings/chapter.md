# Chapter 4: Strings

## What You Will Learn

- How strings are stored internally as arrays of characters
- Why strings are immutable in Python and Java, and what that means for performance
- Common string operations: reversal, palindrome check, anagram detection
- Brute-force string matching
- Why StringBuilder (Java) and join (Python) matter for concatenation
- Character frequency counting with hash maps
- How to solve classic problems: valid palindrome, reverse words, longest common prefix, and group anagrams

## Why This Chapter Matters

Strings appear in nearly every coding interview. They are the most common data type after integers, and string manipulation problems test your ability to think about characters, indices, and patterns. Understanding string immutability is critical -- the difference between O(n) and O(n^2) concatenation can make or break your solution. The techniques you learn here (two pointers, frequency maps, sorting) reappear in dozens of other problems.

---

## 4.1 Strings as Character Arrays

Under the hood, a string is simply an array of characters. Each character occupies a position (index) just like elements in an array.

```
    String: "HELLO"

    Index:   0     1     2     3     4
          +-----+-----+-----+-----+-----+
          | 'H' | 'E' | 'L' | 'L' | 'O' |
          +-----+-----+-----+-----+-----+

    It is an array of characters.
    - Access by index: O(1)
    - Length: O(1) (stored as metadata)
    - Search for character: O(n)
```

**Python**:
```python
s = "HELLO"

# Access by index -- O(1)
print(s[0])        # Output: H
print(s[4])        # Output: O
print(s[-1])       # Output: O (Python supports negative indexing)

# Length
print(len(s))      # Output: 5

# Iterate over characters
for char in s:
    print(char, end=" ")
# Output: H E L L O

print()

# Slicing
print(s[1:4])      # Output: ELL
print(s[::-1])     # Output: OLLEH (reverse)
```

**Java**:
```java
public class StringBasics {
    public static void main(String[] args) {
        String s = "HELLO";

        // Access by index -- O(1)
        System.out.println(s.charAt(0));  // Output: H
        System.out.println(s.charAt(4));  // Output: O

        // Length
        System.out.println(s.length());   // Output: 5

        // Iterate over characters
        for (int i = 0; i < s.length(); i++) {
            System.out.print(s.charAt(i) + " ");
        }
        // Output: H E L L O
        System.out.println();

        // Substring
        System.out.println(s.substring(1, 4));  // Output: ELL
    }
}
```

**Output**:
```
H
O
5
H E L L O
ELL
```

---

## 4.2 Immutability: The Critical Concept

In both Python and Java, strings are **immutable** -- once created, they cannot be changed. Any operation that appears to modify a string actually creates a *new* string.

```
    IMMUTABILITY EXPLAINED

    Python:
    s = "hello"
    s[0] = 'H'       # ERROR! Strings are immutable.
    s = "H" + s[1:]   # Creates a NEW string "Hello"

    What happens in memory:
    Before:  s ----> ["h", "e", "l", "l", "o"]
    After:   s ----> ["H", "e", "l", "l", "o"]  (new object!)
             (old)   ["h", "e", "l", "l", "o"]  (garbage collected)

    Java:
    String s = "hello";
    // s.charAt(0) = 'H';  // Not even valid syntax!
    s = "H" + s.substring(1);  // Creates a NEW String "Hello"
```

### Why Immutability Matters for Performance

Consider building a string character by character:

```python
# BAD: O(n^2) -- creates a new string each iteration!
result = ""
for i in range(n):
    result += str(i)     # Each += creates a new string and copies everything

# What actually happens:
# Iteration 1: "" + "0"          = "0"           (copy 1 char)
# Iteration 2: "0" + "1"         = "01"          (copy 2 chars)
# Iteration 3: "01" + "2"        = "012"         (copy 3 chars)
# ...
# Iteration n: copy n chars
# Total: 1 + 2 + 3 + ... + n = n(n+1)/2 = O(n^2)
```

```
    STRING CONCATENATION IN A LOOP

    O(n^2) approach:            O(n) approach:
    result = ""                 parts = []
    for char in data:           for char in data:
        result += char              parts.append(char)
                                result = "".join(parts)

    Why O(n^2)?                 Why O(n)?
    Each += copies the          append() is O(1) amortized.
    entire string so far.       join() copies each char once.
    Total copies: 1+2+3+...+n  Total: O(n)
    = O(n^2)
```

### The Right Way: StringBuilder / join

**Python**:
```python
# GOOD: O(n) -- use a list and join
parts = []
for i in range(10):
    parts.append(str(i))
result = "".join(parts)
print(result)  # Output: 0123456789

# Even more Pythonic:
result = "".join(str(i) for i in range(10))
print(result)  # Output: 0123456789
```

**Java**:
```java
public class StringBuilderDemo {
    public static void main(String[] args) {
        // GOOD: O(n) -- use StringBuilder
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 10; i++) {
            sb.append(i);
        }
        String result = sb.toString();
        System.out.println(result);  // Output: 0123456789
    }
}
```

**Output**:
```
0123456789
0123456789
```

---

## 4.3 Common String Operations

### Reversing a String

**Python**:
```python
def reverse_string(s):
    """Reverse using slicing -- O(n) time, O(n) space."""
    return s[::-1]

def reverse_string_manual(s):
    """Reverse using two pointers on a list -- O(n) time, O(n) space."""
    chars = list(s)
    left, right = 0, len(chars) - 1
    while left < right:
        chars[left], chars[right] = chars[right], chars[left]
        left += 1
        right -= 1
    return "".join(chars)

# Test
print(reverse_string("hello"))         # Output: olleh
print(reverse_string_manual("hello"))  # Output: olleh
```

**Java**:
```java
public class ReverseString {
    public static String reverse(String s) {
        char[] chars = s.toCharArray();
        int left = 0, right = chars.length - 1;
        while (left < right) {
            char temp = chars[left];
            chars[left] = chars[right];
            chars[right] = temp;
            left++;
            right--;
        }
        return new String(chars);
    }

    public static void main(String[] args) {
        System.out.println(reverse("hello"));  // Output: olleh
    }
}
```

**Output**:
```
olleh
```

---

### Palindrome Check

A palindrome reads the same forward and backward: "racecar", "madam", "level".

```
    Is "racecar" a palindrome?

    r  a  c  e  c  a  r
    ^                 ^    r == r  Yes
       ^           ^       a == a  Yes
          ^     ^          c == c  Yes
             ^             middle reached -- it IS a palindrome!
```

**Python**:
```python
def is_palindrome(s):
    """Two-pointer approach -- O(n) time, O(1) space."""
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True

# Pythonic one-liner:
def is_palindrome_simple(s):
    return s == s[::-1]

# Test
print(is_palindrome("racecar"))    # Output: True
print(is_palindrome("hello"))      # Output: False
print(is_palindrome("a"))          # Output: True
print(is_palindrome(""))           # Output: True
```

**Java**:
```java
public class PalindromeCheck {
    public static boolean isPalindrome(String s) {
        int left = 0, right = s.length() - 1;
        while (left < right) {
            if (s.charAt(left) != s.charAt(right)) return false;
            left++;
            right--;
        }
        return true;
    }

    public static void main(String[] args) {
        System.out.println(isPalindrome("racecar")); // true
        System.out.println(isPalindrome("hello"));   // false
    }
}
```

**Output**:
```
True
False
True
True
```

---

### Anagram Check

Two strings are anagrams if they contain the same characters in the same quantities: "listen" and "silent", "anagram" and "nagaram".

```
    Are "listen" and "silent" anagrams?

    Frequency count:
    "listen": {l:1, i:1, s:1, t:1, e:1, n:1}
    "silent": {s:1, i:1, l:1, e:1, n:1, t:1}
    Same frequencies --> Anagrams!
```

**Python**:
```python
def is_anagram(s, t):
    """Frequency counting -- O(n) time, O(1) space (26 letters)."""
    if len(s) != len(t):
        return False

    count = {}
    for char in s:
        count[char] = count.get(char, 0) + 1
    for char in t:
        count[char] = count.get(char, 0) - 1
        if count[char] < 0:
            return False
    return True

# Pythonic approach using Counter:
from collections import Counter
def is_anagram_simple(s, t):
    return Counter(s) == Counter(t)

# Test
print(is_anagram("listen", "silent"))    # Output: True
print(is_anagram("hello", "world"))      # Output: False
print(is_anagram("anagram", "nagaram"))  # Output: True
```

**Java**:
```java
public class AnagramCheck {
    public static boolean isAnagram(String s, String t) {
        if (s.length() != t.length()) return false;

        int[] count = new int[26]; // Assuming lowercase English letters
        for (char c : s.toCharArray()) count[c - 'a']++;
        for (char c : t.toCharArray()) count[c - 'a']--;

        for (int c : count) {
            if (c != 0) return false;
        }
        return true;
    }

    public static void main(String[] args) {
        System.out.println(isAnagram("listen", "silent"));   // true
        System.out.println(isAnagram("hello", "world"));     // false
        System.out.println(isAnagram("anagram", "nagaram")); // true
    }
}
```

**Output**:
```
True
False
True
```

**Complexity**: Time O(n), Space O(1) (fixed 26-character alphabet).

---

## 4.4 String Matching: Brute Force

**Problem**: Given a text and a pattern, find where (or if) the pattern occurs in the text.

```
    Text:    "AABAACAADAABAABA"
    Pattern: "AABA"

    Slide the pattern across the text:

    AABAACAADAABAABA
    AABA              Match at position 0!
     AABA             No match (A != B at position 2)
      AABA            No match
       ...
              AABA    Match at position 9!
               AABA   Match at position 12!
```

**Python**:
```python
def brute_force_search(text, pattern):
    """O(n * m) where n = len(text), m = len(pattern)."""
    positions = []
    n, m = len(text), len(pattern)

    for i in range(n - m + 1):
        match = True
        for j in range(m):
            if text[i + j] != pattern[j]:
                match = False
                break
        if match:
            positions.append(i)

    return positions

# Test
print(brute_force_search("AABAACAADAABAABA", "AABA"))
# Output: [0, 9, 12]

print(brute_force_search("hello world", "world"))
# Output: [6]

print(brute_force_search("aaaa", "aa"))
# Output: [0, 1, 2]
```

**Java**:
```java
import java.util.ArrayList;
import java.util.List;

public class BruteForceSearch {
    public static List<Integer> search(String text, String pattern) {
        List<Integer> positions = new ArrayList<>();
        int n = text.length(), m = pattern.length();

        for (int i = 0; i <= n - m; i++) {
            boolean match = true;
            for (int j = 0; j < m; j++) {
                if (text.charAt(i + j) != pattern.charAt(j)) {
                    match = false;
                    break;
                }
            }
            if (match) positions.add(i);
        }
        return positions;
    }

    public static void main(String[] args) {
        System.out.println(search("AABAACAADAABAABA", "AABA"));
        // Output: [0, 9, 12]
    }
}
```

**Output**:
```
[0, 9, 12]
[6]
[0, 1, 2]
```

**Complexity**: Time O(n * m) worst case, where n is text length and m is pattern length. In practice, the early `break` makes it faster on average.

---

## 4.5 Character Frequency Counting

Frequency counting is one of the most useful string techniques. Build a map of character -> count, then use it to solve problems.

**Python**:
```python
def char_frequency(s):
    """Count frequency of each character."""
    freq = {}
    for char in s:
        freq[char] = freq.get(char, 0) + 1
    return freq

# Test
print(char_frequency("abracadabra"))
# Output: {'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1}

# Find the first non-repeating character
def first_unique_char(s):
    freq = char_frequency(s)
    for i, char in enumerate(s):
        if freq[char] == 1:
            return i
    return -1

print(first_unique_char("leetcode"))    # Output: 0 ('l')
print(first_unique_char("loveleetcode")) # Output: 2 ('v')
print(first_unique_char("aabb"))         # Output: -1
```

**Java**:
```java
import java.util.HashMap;
import java.util.Map;

public class CharFrequency {
    public static int firstUniqueChar(String s) {
        Map<Character, Integer> freq = new HashMap<>();
        for (char c : s.toCharArray()) {
            freq.put(c, freq.getOrDefault(c, 0) + 1);
        }
        for (int i = 0; i < s.length(); i++) {
            if (freq.get(s.charAt(i)) == 1) return i;
        }
        return -1;
    }

    public static void main(String[] args) {
        System.out.println(firstUniqueChar("leetcode"));     // 0
        System.out.println(firstUniqueChar("loveleetcode")); // 2
        System.out.println(firstUniqueChar("aabb"));         // -1
    }
}
```

**Output**:
```
{'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1}
0
2
-1
```

---

## Common Mistakes

1. **String concatenation in a loop.** Using `+=` in a loop creates O(n^2) behavior. Use `"".join(list)` in Python or `StringBuilder` in Java.
2. **Forgetting that strings are immutable.** Trying to modify a character in place (`s[i] = 'x'` in Python) throws an error. Convert to a list first.
3. **Not handling case sensitivity.** "Racecar" is not a palindrome unless you convert to lowercase first. Always clarify with the interviewer.
4. **Not handling non-alphanumeric characters.** In many problems, spaces and punctuation should be ignored. Use `isalnum()` (Python) or `Character.isLetterOrDigit()` (Java) to filter.
5. **Using sort for anagram check when frequency counting is better.** Sorting is O(n log n); frequency counting is O(n). Both work, but know the trade-off.

## Best Practices

1. **Convert strings to character arrays/lists** when you need to modify individual characters.
2. **Use frequency maps** (hash maps or arrays of size 26) for character counting problems.
3. **Use two pointers** for palindrome checks and in-place modifications.
4. **Normalize input early**: convert to lowercase, strip spaces, filter non-alphanumeric characters at the start.
5. **Know your language's string API**: `lower()`, `upper()`, `strip()`, `split()`, `join()`, `isalnum()`, `startswith()` (Python) or `toLowerCase()`, `trim()`, `split()`, `startsWith()`, `substring()`, `toCharArray()` (Java).

---

## Quick Summary

Strings are arrays of characters. In Python and Java, they are immutable -- every modification creates a new string. This makes naive concatenation in loops O(n^2). Use `"".join()` or `StringBuilder` instead. Key string patterns include two-pointer palindrome checks, frequency counting for anagram detection, and brute-force pattern matching. Most string problems boil down to: convert to array, use a hash map for counting, or use two pointers for comparisons.

## Key Points

- **Strings are character arrays** with O(1) index access and O(n) search.
- **Immutability** means every modification creates a new string. Concatenation in loops is O(n^2).
- Use **`"".join(list)`** in Python and **`StringBuilder`** in Java for efficient string building.
- **Frequency counting** with hash maps solves anagram, unique character, and permutation problems in O(n).
- **Two pointers** from both ends is the standard technique for palindrome checks.
- **Brute-force string matching** is O(n * m) but works well for most interview problems.
- Always clarify: case sensitivity, whitespace handling, character set (lowercase only? Unicode?).

---

## Practice Questions

1. Why is `result += char` inside a loop O(n^2) for strings but O(n) for lists? Explain the difference in terms of immutability.

2. Given the string "programming", count the frequency of each character by hand. Which character appears most frequently?

3. Are "triangle" and "integral" anagrams? Verify by computing frequency counts for each.

4. Trace through the brute-force string matching algorithm for text = "AAAAAB" and pattern = "AAB". How many character comparisons are made?

5. Write a function that checks if a string is a rotation of another string. For example, "waterbottle" is a rotation of "erbottlewat". (Hint: what happens when you concatenate a string with itself?)

---

## LeetCode-Style Problems

### Problem 1: Valid Palindrome (Easy)

**Problem**: Given a string, determine if it is a palindrome considering only alphanumeric characters and ignoring case. An empty string is a valid palindrome.

**Example**: "A man, a plan, a canal: Panama" -> true

```
    Walkthrough:
    Original: "A man, a plan, a canal: Panama"
    Cleaned:  "amanaplanacanalpanama"

    Two pointers:
    a m a n a p l a n a c a n a l p a n a m a
    ^                                       ^   a == a
      ^                                   ^     m == m
        ^                               ^       a == a
    ... all match --> Palindrome!
```

**Python**:
```python
def is_valid_palindrome(s):
    left, right = 0, len(s) - 1

    while left < right:
        # Skip non-alphanumeric characters
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1

        if s[left].lower() != s[right].lower():
            return False

        left += 1
        right -= 1

    return True

# Test
print(is_valid_palindrome("A man, a plan, a canal: Panama"))  # Output: True
print(is_valid_palindrome("race a car"))                       # Output: False
print(is_valid_palindrome(" "))                                # Output: True
```

**Java**:
```java
public class ValidPalindrome {
    public static boolean isPalindrome(String s) {
        int left = 0, right = s.length() - 1;

        while (left < right) {
            while (left < right && !Character.isLetterOrDigit(s.charAt(left)))
                left++;
            while (left < right && !Character.isLetterOrDigit(s.charAt(right)))
                right--;

            if (Character.toLowerCase(s.charAt(left)) !=
                Character.toLowerCase(s.charAt(right)))
                return false;

            left++;
            right--;
        }
        return true;
    }

    public static void main(String[] args) {
        System.out.println(isPalindrome("A man, a plan, a canal: Panama")); // true
        System.out.println(isPalindrome("race a car"));                     // false
    }
}
```

**Output**:
```
True
False
True
```

**Complexity**: Time O(n), Space O(1). Two pointers with character filtering.

---

### Problem 2: Reverse Words in a String (Medium)

**Problem**: Given a string, reverse the order of words. Words are separated by spaces. Remove leading/trailing spaces and reduce multiple spaces to a single space.

**Example**: "  the sky  is blue  " -> "blue is sky the"

**Python**:
```python
def reverse_words(s):
    # Split handles multiple spaces and strips leading/trailing
    words = s.split()
    return " ".join(reversed(words))

# Manual approach (more interview-friendly):
def reverse_words_manual(s):
    # Step 1: Split into words (skip extra spaces)
    words = []
    word = []
    for char in s:
        if char != ' ':
            word.append(char)
        elif word:
            words.append("".join(word))
            word = []
    if word:
        words.append("".join(word))

    # Step 2: Reverse the list of words
    left, right = 0, len(words) - 1
    while left < right:
        words[left], words[right] = words[right], words[left]
        left += 1
        right -= 1

    return " ".join(words)

# Test
print(reverse_words("the sky is blue"))       # Output: blue is sky the
print(reverse_words("  hello world  "))       # Output: world hello
print(reverse_words("a good   example"))      # Output: example good a
print(reverse_words_manual("the sky is blue"))# Output: blue is sky the
```

**Java**:
```java
public class ReverseWords {
    public static String reverseWords(String s) {
        String[] words = s.trim().split("\\s+");
        StringBuilder sb = new StringBuilder();

        for (int i = words.length - 1; i >= 0; i--) {
            sb.append(words[i]);
            if (i > 0) sb.append(" ");
        }
        return sb.toString();
    }

    public static void main(String[] args) {
        System.out.println(reverseWords("the sky is blue"));   // blue is sky the
        System.out.println(reverseWords("  hello world  "));   // world hello
        System.out.println(reverseWords("a good   example"));  // example good a
    }
}
```

**Output**:
```
blue is sky the
world hello
example good a
```

**Complexity**: Time O(n), Space O(n) for the word list.

---

### Problem 3: Longest Common Prefix (Easy)

**Problem**: Find the longest common prefix string among an array of strings. If there is no common prefix, return "".

**Example**: ["flower", "flow", "flight"] -> "fl"

```
    Vertical scanning:

    f l o w e r
    f l o w
    f l i g h t
    ^ ^
    f l -- both columns match

    f l o w e r
    f l o w
    f l i g h t
        ^
    o != i -- Stop! Prefix is "fl"
```

**Python**:
```python
def longest_common_prefix(strs):
    if not strs:
        return ""

    # Use the first string as reference
    prefix = strs[0]

    for s in strs[1:]:
        # Shrink prefix until it matches the start of s
        while not s.startswith(prefix):
            prefix = prefix[:-1]  # Remove last character
            if not prefix:
                return ""

    return prefix

# Test
print(longest_common_prefix(["flower", "flow", "flight"]))  # Output: fl
print(longest_common_prefix(["dog", "racecar", "car"]))     # Output: (empty)
print(longest_common_prefix(["interspecies", "interstellar", "interstate"]))
# Output: inters
```

**Java**:
```java
public class LongestCommonPrefix {
    public static String longestCommonPrefix(String[] strs) {
        if (strs == null || strs.length == 0) return "";

        String prefix = strs[0];
        for (int i = 1; i < strs.length; i++) {
            while (!strs[i].startsWith(prefix)) {
                prefix = prefix.substring(0, prefix.length() - 1);
                if (prefix.isEmpty()) return "";
            }
        }
        return prefix;
    }

    public static void main(String[] args) {
        System.out.println(longestCommonPrefix(
            new String[]{"flower", "flow", "flight"}));  // fl
        System.out.println(longestCommonPrefix(
            new String[]{"dog", "racecar", "car"}));     // (empty)
    }
}
```

**Output**:
```
fl

inters
```

**Complexity**: Time O(S) where S is the total number of characters across all strings. Space O(1).

---

### Problem 4: Group Anagrams (Medium)

**Problem**: Given an array of strings, group the anagrams together. Return the groups in any order.

**Example**: ["eat","tea","tan","ate","nat","bat"] -> [["eat","tea","ate"], ["tan","nat"], ["bat"]]

```
    Key Insight: Anagrams, when sorted, produce the same string.
    "eat" sorted --> "aet"
    "tea" sorted --> "aet"    Same!
    "ate" sorted --> "aet"    Same!
    "tan" sorted --> "ant"
    "nat" sorted --> "ant"    Same!
    "bat" sorted --> "abt"

    Use the sorted string as a hash map key:
    {
        "aet": ["eat", "tea", "ate"],
        "ant": ["tan", "nat"],
        "abt": ["bat"]
    }
```

**Python**:
```python
from collections import defaultdict

def group_anagrams(strs):
    groups = defaultdict(list)

    for s in strs:
        # Sort the string to create the key
        key = "".join(sorted(s))
        groups[key].append(s)

    return list(groups.values())

# Alternative: Use character count tuple as key (avoids sorting)
def group_anagrams_count(strs):
    groups = defaultdict(list)

    for s in strs:
        count = [0] * 26
        for char in s:
            count[ord(char) - ord('a')] += 1
        key = tuple(count)  # Lists are not hashable, tuples are
        groups[key].append(s)

    return list(groups.values())

# Test
result = group_anagrams(["eat","tea","tan","ate","nat","bat"])
for group in sorted(result, key=len, reverse=True):
    print(sorted(group))
# Output:
# ['ate', 'eat', 'tea']
# ['nat', 'tan']
# ['bat']
```

**Java**:
```java
import java.util.*;

public class GroupAnagrams {
    public static List<List<String>> groupAnagrams(String[] strs) {
        Map<String, List<String>> groups = new HashMap<>();

        for (String s : strs) {
            char[] chars = s.toCharArray();
            Arrays.sort(chars);
            String key = new String(chars);

            groups.computeIfAbsent(key, k -> new ArrayList<>()).add(s);
        }
        return new ArrayList<>(groups.values());
    }

    public static void main(String[] args) {
        String[] input = {"eat","tea","tan","ate","nat","bat"};
        List<List<String>> result = groupAnagrams(input);
        for (List<String> group : result) {
            System.out.println(group);
        }
        // Output (order may vary):
        // [eat, tea, ate]
        // [tan, nat]
        // [bat]
    }
}
```

**Output**:
```
['ate', 'eat', 'tea']
['nat', 'tan']
['bat']
```

**Complexity**:
- Sorting approach: Time O(n * k log k) where n is the number of strings and k is the max string length. Space O(n * k).
- Counting approach: Time O(n * k). Space O(n * k). Faster when strings are long.

---

### Problem 5: Valid Anagram (Easy)

**Problem**: Given two strings s and t, return true if t is an anagram of s.

**Python**:
```python
def is_anagram(s, t):
    if len(s) != len(t):
        return False

    count = [0] * 26
    for i in range(len(s)):
        count[ord(s[i]) - ord('a')] += 1
        count[ord(t[i]) - ord('a')] -= 1

    return all(c == 0 for c in count)

# Test
print(is_anagram("anagram", "nagaram"))  # Output: True
print(is_anagram("rat", "car"))          # Output: False
```

**Java**:
```java
public class ValidAnagram {
    public static boolean isAnagram(String s, String t) {
        if (s.length() != t.length()) return false;

        int[] count = new int[26];
        for (int i = 0; i < s.length(); i++) {
            count[s.charAt(i) - 'a']++;
            count[t.charAt(i) - 'a']--;
        }

        for (int c : count) {
            if (c != 0) return false;
        }
        return true;
    }

    public static void main(String[] args) {
        System.out.println(isAnagram("anagram", "nagaram")); // true
        System.out.println(isAnagram("rat", "car"));         // false
    }
}
```

**Output**:
```
True
False
```

**Complexity**: Time O(n), Space O(1) (26-element array is constant).

---

## What Is Next?

In Chapter 5, you will learn about **Linked Lists** -- a data structure where elements are not stored contiguously in memory but instead linked together with pointers. You will discover when linked lists outperform arrays, how to manipulate pointers to reverse a list, detect cycles, and merge sorted lists.
