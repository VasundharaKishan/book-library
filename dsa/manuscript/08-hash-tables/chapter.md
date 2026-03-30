# Chapter 8: Hash Tables

## What You Will Learn

- What hashing is and how hash functions work
- How hash tables store and retrieve data in O(1) average time
- What collisions are and two strategies to handle them: chaining and open addressing
- What load factor means and when rehashing happens
- How Python's `dict` and Java's `HashMap` work under the hood (simplified)
- How to solve five classic hash table interview problems

## Why This Chapter Matters

Imagine a library with a million books but no catalog system. Finding a specific book means walking through every shelf -- that is O(n). Now imagine an index card system where you look up a book title, the card tells you "Shelf 47, Slot 12," and you walk directly there -- that is O(1). Hash tables are that index card system for your data.

Hash tables are arguably the most practically important data structure in all of computer science. They power Python dictionaries, Java HashMaps, database indexes, caches, and symbol tables in compilers. The "Two Sum" problem -- the most popular interview question on LeetCode -- is fundamentally a hash table problem. If you master one data structure from this book, make it this one.

---

## 8.1 What Is Hashing?

**Hashing** is the process of converting any input (a string, number, object) into a fixed-size integer called a **hash code** or **hash value**. A **hash function** performs this conversion.

```
         Hash Function
"apple"  ------------>  247
"banana" ------------>  1082
"cherry" ------------>  519

The hash function converts keys into array indices.
```

### Properties of a Good Hash Function

1. **Deterministic**: The same input always produces the same output.
2. **Uniform distribution**: Outputs are spread evenly across the range to minimize collisions.
3. **Fast to compute**: Hashing should be O(1) -- it defeats the purpose if hashing is slow.

### Simple Hash Function Example

```python
def simple_hash(key, table_size):
    """Sum of character codes, then mod by table size."""
    total = 0
    for char in key:
        total += ord(char)
    return total % table_size

print(simple_hash("cat", 10))   # Output: 2  (99+97+116 = 312, 312%10 = 2)
print(simple_hash("dog", 10))   # Output: 4  (100+111+103 = 314, 314%10 = 4)
print(simple_hash("act", 10))   # Output: 2  (same letters as "cat"!)
```

Notice that "cat" and "act" produce the same hash. This is a **collision**, and handling collisions is the central challenge of hash table design.

---

## 8.2 Hash Table Structure

A hash table is an array of **buckets**. Each bucket holds key-value pairs. The hash function determines which bucket a key belongs to.

```
Hash Table (size = 8)

Key "name" --> hash("name") % 8 = 3 --> stored at index 3
Key "age"  --> hash("age")  % 8 = 5 --> stored at index 5

Index:  0     1     2     3           4     5         6     7
      +-----+-----+-----+-----------+-----+---------+-----+-----+
      |     |     |     | name:Alex |     | age:25  |     |     |
      +-----+-----+-----+-----------+-----+---------+-----+-----+
```

### Basic Hash Table Operations

| Operation | Average Case | Worst Case |
|-----------|-------------|------------|
| Insert    | O(1)        | O(n)       |
| Search    | O(1)        | O(n)       |
| Delete    | O(1)        | O(n)       |

The worst case of O(n) happens when all keys collide into the same bucket. In practice, with a good hash function and proper sizing, this almost never happens.

---

## 8.3 Handling Collisions: Chaining

**Chaining** (also called separate chaining) handles collisions by storing multiple key-value pairs at the same index using a linked list (or another collection).

```
Hash Table with Chaining (size = 4)

hash("cat") % 4 = 2
hash("act") % 4 = 2   <-- collision!
hash("dog") % 4 = 0

Index 0: [dog:3] -> None
Index 1: None
Index 2: [cat:1] -> [act:2] -> None    <-- chain of two entries
Index 3: None
```

### Python -- Hash Table with Chaining

```python
class HashTable:
    def __init__(self, size=16):
        self.size = size
        self.buckets = [[] for _ in range(size)]
        self.count = 0

    def _hash(self, key):
        return hash(key) % self.size

    def put(self, key, value):
        index = self._hash(key)
        bucket = self.buckets[index]

        # Update if key already exists
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return

        # Add new key-value pair
        bucket.append((key, value))
        self.count += 1

        # Rehash if load factor exceeds 0.75
        if self.count / self.size > 0.75:
            self._rehash()

    def get(self, key):
        index = self._hash(key)
        bucket = self.buckets[index]

        for k, v in bucket:
            if k == key:
                return v

        raise KeyError(f"Key '{key}' not found")

    def remove(self, key):
        index = self._hash(key)
        bucket = self.buckets[index]

        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket.pop(i)
                self.count -= 1
                return v

        raise KeyError(f"Key '{key}' not found")

    def _rehash(self):
        old_buckets = self.buckets
        self.size *= 2
        self.buckets = [[] for _ in range(self.size)]
        self.count = 0

        for bucket in old_buckets:
            for key, value in bucket:
                self.put(key, value)

    def __str__(self):
        items = []
        for bucket in self.buckets:
            for key, value in bucket:
                items.append(f"{key}: {value}")
        return "{" + ", ".join(items) + "}"


# Usage
ht = HashTable()
ht.put("name", "Alice")
ht.put("age", 30)
ht.put("city", "NYC")

print(ht.get("name"))  # Output: Alice
print(ht.get("age"))   # Output: 30

ht.put("age", 31)       # Update
print(ht.get("age"))    # Output: 31

ht.remove("city")
print(ht)               # Output: {name: Alice, age: 31}
```

### Java -- Hash Table with Chaining

```java
import java.util.LinkedList;

public class HashTable<K, V> {
    private static class Entry<K, V> {
        K key;
        V value;

        Entry(K key, V value) {
            this.key = key;
            this.value = value;
        }
    }

    private LinkedList<Entry<K, V>>[] buckets;
    private int size;
    private int count;

    @SuppressWarnings("unchecked")
    public HashTable(int size) {
        this.size = size;
        this.buckets = new LinkedList[size];
        for (int i = 0; i < size; i++) {
            buckets[i] = new LinkedList<>();
        }
        this.count = 0;
    }

    private int hash(K key) {
        return Math.abs(key.hashCode() % size);
    }

    public void put(K key, V value) {
        int index = hash(key);
        LinkedList<Entry<K, V>> bucket = buckets[index];

        for (Entry<K, V> entry : bucket) {
            if (entry.key.equals(key)) {
                entry.value = value;  // Update existing
                return;
            }
        }

        bucket.add(new Entry<>(key, value));
        count++;

        if ((double) count / size > 0.75) {
            rehash();
        }
    }

    public V get(K key) {
        int index = hash(key);
        for (Entry<K, V> entry : buckets[index]) {
            if (entry.key.equals(key)) {
                return entry.value;
            }
        }
        return null;
    }

    public V remove(K key) {
        int index = hash(key);
        LinkedList<Entry<K, V>> bucket = buckets[index];

        for (int i = 0; i < bucket.size(); i++) {
            if (bucket.get(i).key.equals(key)) {
                V value = bucket.get(i).value;
                bucket.remove(i);
                count--;
                return value;
            }
        }
        return null;
    }

    @SuppressWarnings("unchecked")
    private void rehash() {
        LinkedList<Entry<K, V>>[] oldBuckets = buckets;
        size *= 2;
        buckets = new LinkedList[size];
        for (int i = 0; i < size; i++) {
            buckets[i] = new LinkedList<>();
        }
        count = 0;

        for (LinkedList<Entry<K, V>> bucket : oldBuckets) {
            for (Entry<K, V> entry : bucket) {
                put(entry.key, entry.value);
            }
        }
    }

    public static void main(String[] args) {
        HashTable<String, Integer> ht = new HashTable<>(16);
        ht.put("apple", 5);
        ht.put("banana", 3);
        ht.put("cherry", 8);

        System.out.println(ht.get("apple"));   // Output: 5
        System.out.println(ht.get("banana"));  // Output: 3

        ht.put("apple", 10);  // Update
        System.out.println(ht.get("apple"));   // Output: 10
    }
}
```

---

## 8.4 Handling Collisions: Open Addressing

With **open addressing**, all entries are stored directly in the array (no linked lists). When a collision occurs, we probe for the next available slot.

### Linear Probing

If index `h` is taken, try `h+1`, then `h+2`, and so on (wrapping around).

```
Insert keys with hash values: A->2, B->2, C->2

Step 1: Insert A at index 2
  [  ][  ][ A][  ][  ]
            ^

Step 2: Insert B, hash = 2 (taken!), try 3 (empty)
  [  ][  ][ A][ B][  ]
            ^   ^
         taken  placed here

Step 3: Insert C, hash = 2 (taken!), try 3 (taken!), try 4 (empty)
  [  ][  ][ A][ B][ C]
            ^   ^   ^
        taken taken placed here
```

### Quadratic Probing

Instead of checking `h+1, h+2, h+3`, check `h+1, h+4, h+9` (offsets are `i^2`). This reduces clustering.

### Double Hashing

Use a second hash function to determine the step size: `(h + i * h2(key)) % size`. This distributes probes more uniformly.

### Chaining vs Open Addressing

| Feature          | Chaining                  | Open Addressing         |
|------------------|---------------------------|-------------------------|
| Storage          | Linked lists at each slot | Everything in the array |
| Memory           | Extra pointers            | No extra pointers       |
| Clustering       | Not an issue              | Can degrade performance |
| Load factor > 1  | Allowed                   | Not possible            |
| Cache performance| Worse (pointer chasing)   | Better (contiguous)     |
| Deletion         | Simple                    | Requires tombstones     |

---

## 8.5 Load Factor and Rehashing

The **load factor** is the ratio of entries to buckets:

```
load_factor = number_of_entries / number_of_buckets
```

A higher load factor means more collisions. Most implementations rehash (double the array size and re-insert all entries) when the load factor exceeds a threshold.

```
Rehashing Example:

Before (size=4, entries=3, load=0.75):
  [A][B][ ][C]

After rehashing (size=8, entries=3, load=0.375):
  [ ][A][ ][ ][B][ ][C][ ]

All entries are re-hashed with the new size.
```

| Language       | Default Load Factor Threshold |
|----------------|-------------------------------|
| Python dict    | ~0.66 (2/3)                   |
| Java HashMap   | 0.75                          |

### Why Rehashing Is Amortized O(1)

Rehashing itself is O(n), but it happens rarely. If you double the table size each time, the total cost of all rehashes over n insertions is O(n), giving an amortized cost of O(1) per insertion.

---

## 8.6 Python dict and Java HashMap Internals (Simplified)

### Python dict

- Uses **open addressing** with a probing scheme
- Initial size: 8 buckets
- Rehashes when load factor exceeds ~2/3
- Since Python 3.7, dictionaries maintain **insertion order**
- Keys must be **hashable** (immutable): strings, numbers, tuples are fine; lists and dicts are not

```python
# Python dict is a hash table
d = {}
d["name"] = "Alice"   # hash("name") -> index -> store
d["age"] = 30
print(d["name"])       # hash("name") -> index -> retrieve -> "Alice"
print("age" in d)      # hash("age") -> index -> found -> True
```

### Java HashMap

- Uses **chaining** with linked lists (switches to balanced trees when a chain exceeds 8 entries)
- Initial capacity: 16 buckets
- Rehashes when load factor exceeds 0.75
- Does **not** maintain insertion order (use `LinkedHashMap` for that)
- Keys must implement `hashCode()` and `equals()`

```java
import java.util.HashMap;
import java.util.Map;

public class HashMapDemo {
    public static void main(String[] args) {
        Map<String, Integer> map = new HashMap<>();
        map.put("apple", 5);
        map.put("banana", 3);

        System.out.println(map.get("apple"));          // Output: 5
        System.out.println(map.containsKey("cherry")); // Output: false
        System.out.println(map.getOrDefault("cherry", 0)); // Output: 0

        // Iterate
        for (Map.Entry<String, Integer> entry : map.entrySet()) {
            System.out.println(entry.getKey() + ": " + entry.getValue());
        }
    }
}
```

### Essential Operations Reference

| Operation          | Python                     | Java HashMap               |
|--------------------|----------------------------|----------------------------|
| Create             | `d = {}` or `dict()`       | `new HashMap<>()`          |
| Insert/Update      | `d[key] = value`           | `map.put(key, value)`      |
| Get                | `d[key]` or `d.get(key)`   | `map.get(key)`             |
| Get with default   | `d.get(key, default)`      | `map.getOrDefault(key, d)` |
| Check key exists   | `key in d`                 | `map.containsKey(key)`     |
| Delete             | `del d[key]`               | `map.remove(key)`          |
| Size               | `len(d)`                   | `map.size()`               |
| Iterate keys       | `for k in d:`              | `for (K k : map.keySet())` |
| Iterate pairs      | `for k,v in d.items():`    | `for (Entry e : map.entrySet())` |

---

## 8.7 Common Hash Table Patterns

### Pattern 1: Counting Frequencies

```python
def count_chars(s):
    freq = {}
    for char in s:
        freq[char] = freq.get(char, 0) + 1
    return freq

print(count_chars("hello"))
# Output: {'h': 1, 'e': 1, 'l': 2, 'o': 1}
```

### Pattern 2: Grouping by Key

```python
def group_by_length(words):
    groups = {}
    for word in words:
        length = len(word)
        if length not in groups:
            groups[length] = []
        groups[length].append(word)
    return groups

print(group_by_length(["hi", "cat", "go", "dog", "hello"]))
# Output: {2: ['hi', 'go'], 3: ['cat', 'dog'], 5: ['hello']}
```

### Pattern 3: Two-Pass Lookup

Store data in the first pass, query in the second.

```python
# Find pairs that sum to target
def has_pair_sum(nums, target):
    seen = set()  # A set is a hash table without values
    for num in nums:
        complement = target - num
        if complement in seen:
            return True
        seen.add(num)
    return False

print(has_pair_sum([2, 7, 11, 15], 9))  # Output: True (2+7)
```

---

## 8.8 Time and Space Complexity

| Operation      | Average | Worst Case | Notes                        |
|----------------|---------|------------|------------------------------|
| Insert         | O(1)    | O(n)       | Worst case: all keys collide |
| Search         | O(1)    | O(n)       | Average assumes good hash    |
| Delete         | O(1)    | O(n)       |                              |
| Space          | O(n)    | O(n)       | n = number of entries        |
| Rehashing      | O(n)    | O(n)       | Amortized O(1) per insert    |

**Why O(1) average?** With a good hash function and a load factor below 0.75, each bucket has at most 1-2 entries on average. Looking up a bucket by index is O(1), and scanning 1-2 entries is O(1).

**When does O(n) happen?** If all keys hash to the same bucket (pathological case), lookup degrades to scanning a linked list of length n.

---

## 8.9 Common Mistakes

1. **Using mutable objects as keys**: In Python, lists and dicts cannot be dictionary keys because they are not hashable. Use tuples or frozensets instead.

2. **Forgetting that hash tables are unordered**: Standard hash tables do not guarantee iteration order. In Python 3.7+, `dict` preserves insertion order, but this is implementation-specific. In Java, use `LinkedHashMap` if order matters.

3. **Not handling missing keys**: `d[key]` throws `KeyError` in Python if the key does not exist. Use `d.get(key, default)` or check with `key in d` first.

4. **Ignoring the cost of hashing**: Hashing long strings takes O(L) where L is the string length. This is usually fine but can matter in tight loops with very long keys.

5. **Overriding `hashCode()` but not `equals()` in Java**: If two objects are "equal," they must have the same hash code. Overriding one without the other causes subtle bugs.

---

## 8.10 Best Practices

1. **Use built-in hash tables**: Python's `dict` and `collections.Counter`/`defaultdict`, Java's `HashMap` and `HashSet` are highly optimized. Do not reinvent the wheel.

2. **Use `defaultdict` for cleaner code in Python**:
   ```python
   from collections import defaultdict
   freq = defaultdict(int)
   for char in "hello":
       freq[char] += 1  # No need to check if key exists
   ```

3. **Use `Counter` for frequency counting**:
   ```python
   from collections import Counter
   print(Counter("hello"))  # Counter({'l': 2, 'h': 1, 'e': 1, 'o': 1})
   ```

4. **Choose `HashSet` when you only need keys (no values)**: A set is a hash table where you only care about membership, not associated values.

5. **Think "hash table" when you see "O(1) lookup"**: If a problem requires fast lookups, membership testing, or counting, a hash table is almost always the answer.

---

## Quick Summary

A **hash table** maps keys to values using a **hash function** that converts keys into array indices. **Collisions** occur when two keys map to the same index and are handled via **chaining** (linked lists at each bucket) or **open addressing** (probing for the next open slot). The **load factor** (entries / buckets) determines when to **rehash** by doubling the array. Python uses `dict` (open addressing); Java uses `HashMap` (chaining with tree fallback). Average-case operations are O(1).

---

## Key Points

- A hash function maps keys to array indices deterministically
- Collisions are inevitable; handle them with chaining or open addressing
- Load factor = entries / buckets; rehash when it exceeds the threshold (~0.66-0.75)
- Average-case insert, search, delete: O(1); worst case: O(n)
- Python dict: open addressing, insertion-ordered since 3.7
- Java HashMap: chaining (linked list, switches to tree at 8+ entries)
- Use `defaultdict`, `Counter` (Python) and `getOrDefault` (Java) for cleaner code
- Hash tables power frequency counting, grouping, membership testing, and caching

---

## Practice Questions

1. What happens when two different keys produce the same hash value? Describe two strategies for handling this.

2. A hash table has 16 buckets and 12 entries. What is the load factor? Should a rehash be triggered if the threshold is 0.75?

3. Why can you use a string as a dictionary key in Python but not a list? What property must a key have?

4. Explain why hash table operations are O(1) on average but O(n) in the worst case. Under what conditions does the worst case occur?

5. You need to count how many times each word appears in a book. What data structure and what specific Python/Java class would you use? Write the code.

---

## LeetCode-Style Problems

### Problem 1: Two Sum (LeetCode 1)

**Problem**: Given an array of integers `nums` and an integer `target`, return the indices of the two numbers that add up to `target`. Each input has exactly one solution.

**Approach**: For each number, compute its complement (`target - num`). Check if the complement is already in our hash map. If yes, we found our pair. If no, store the current number and its index.

```
nums = [2, 7, 11, 15], target = 9

Step 1: num=2, complement=7, seen={}       -> not found, store {2:0}
Step 2: num=7, complement=2, seen={2:0}    -> found! return [0, 1]
```

**Python Solution**:

```python
def two_sum(nums, target):
    seen = {}  # value -> index

    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i

    return []  # No solution found


print(two_sum([2, 7, 11, 15], 9))   # Output: [0, 1]
print(two_sum([3, 2, 4], 6))        # Output: [1, 2]
print(two_sum([3, 3], 6))           # Output: [0, 1]
```

**Java Solution**:

```java
import java.util.HashMap;
import java.util.Map;

public class TwoSum {
    public static int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> seen = new HashMap<>();

        for (int i = 0; i < nums.length; i++) {
            int complement = target - nums[i];
            if (seen.containsKey(complement)) {
                return new int[]{seen.get(complement), i};
            }
            seen.put(nums[i], i);
        }

        return new int[]{};
    }

    public static void main(String[] args) {
        int[] result = twoSum(new int[]{2, 7, 11, 15}, 9);
        System.out.println(result[0] + ", " + result[1]);  // Output: 0, 1
    }
}
```

**Complexity**: Time: O(n). Space: O(n).

---

### Problem 2: Group Anagrams (LeetCode 49)

**Problem**: Given an array of strings, group anagrams together. Anagrams are words formed by rearranging the same letters (e.g., "eat" and "tea").

**Approach**: Two strings are anagrams if they have the same characters in the same frequency. Sort each string and use the sorted version as the hash map key. All anagrams will map to the same key.

```
Input: ["eat", "tea", "tan", "ate", "nat", "bat"]

sorted("eat") = "aet" -> group 1: ["eat", "tea", "ate"]
sorted("tan") = "ant" -> group 2: ["tan", "nat"]
sorted("bat") = "abt" -> group 3: ["bat"]
```

**Python Solution**:

```python
from collections import defaultdict

def group_anagrams(strs):
    groups = defaultdict(list)

    for s in strs:
        key = ''.join(sorted(s))  # Sort characters as the key
        groups[key].append(s)

    return list(groups.values())


print(group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]))
# Output: [['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]
```

**Java Solution**:

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
        String[] input = {"eat", "tea", "tan", "ate", "nat", "bat"};
        System.out.println(groupAnagrams(input));
        // Output: [[eat, tea, ate], [tan, nat], [bat]]
    }
}
```

**Complexity**: Time: O(n * k log k) where n is the number of strings and k is the maximum string length (sorting each string). Space: O(n * k).

---

### Problem 3: Top K Frequent Elements (LeetCode 347)

**Problem**: Given an integer array and an integer `k`, return the `k` most frequent elements.

**Approach**: Count frequencies with a hash map, then use bucket sort -- create an array where index `i` holds all elements with frequency `i`. Scan from the end (highest frequency) to collect the top k elements.

```
nums = [1,1,1,2,2,3], k = 2

Step 1 - Count: {1:3, 2:2, 3:1}

Step 2 - Bucket sort by frequency:
  Index:  0   1    2    3    4   5   6
        [ ] [3]  [2]  [1]  [ ] [ ] [ ]

Step 3 - Scan from right: index 3 -> [1], index 2 -> [2]
  Result: [1, 2]
```

**Python Solution**:

```python
from collections import Counter

def top_k_frequent(nums, k):
    count = Counter(nums)

    # Bucket sort: index = frequency, value = list of elements
    buckets = [[] for _ in range(len(nums) + 1)]
    for num, freq in count.items():
        buckets[freq].append(num)

    result = []
    for i in range(len(buckets) - 1, -1, -1):
        for num in buckets[i]:
            result.append(num)
            if len(result) == k:
                return result

    return result


print(top_k_frequent([1, 1, 1, 2, 2, 3], 2))  # Output: [1, 2]
print(top_k_frequent([1], 1))                   # Output: [1]
```

**Java Solution**:

```java
import java.util.*;

public class TopKFrequent {
    public static int[] topKFrequent(int[] nums, int k) {
        Map<Integer, Integer> count = new HashMap<>();
        for (int num : nums) {
            count.put(num, count.getOrDefault(num, 0) + 1);
        }

        // Bucket sort
        List<Integer>[] buckets = new List[nums.length + 1];
        for (int i = 0; i < buckets.length; i++) {
            buckets[i] = new ArrayList<>();
        }
        for (Map.Entry<Integer, Integer> entry : count.entrySet()) {
            buckets[entry.getValue()].add(entry.getKey());
        }

        int[] result = new int[k];
        int idx = 0;
        for (int i = buckets.length - 1; i >= 0 && idx < k; i--) {
            for (int num : buckets[i]) {
                result[idx++] = num;
                if (idx == k) break;
            }
        }

        return result;
    }

    public static void main(String[] args) {
        System.out.println(Arrays.toString(
            topKFrequent(new int[]{1, 1, 1, 2, 2, 3}, 2)
        ));  // Output: [1, 2]
    }
}
```

**Complexity**: Time: O(n). Space: O(n).

---

### Problem 4: Longest Consecutive Sequence (LeetCode 128)

**Problem**: Given an unsorted array of integers, find the length of the longest consecutive elements sequence (e.g., [1, 2, 3, 4]) in O(n) time.

**Approach**: Put all numbers in a `set` (hash set). For each number, check if it is the start of a sequence (`num - 1` not in the set). If it is, count how many consecutive numbers follow.

```
nums = [100, 4, 200, 1, 3, 2]
Set: {100, 4, 200, 1, 3, 2}

Check each number:
  100: is 99 in set? No -> start of sequence. 100,101? No. Length=1
  4:   is 3 in set? Yes -> skip (not the start)
  200: is 199 in set? No -> start of sequence. 200,201? No. Length=1
  1:   is 0 in set? No -> start of sequence. 1,2,3,4,5? No 5. Length=4
  3:   is 2 in set? Yes -> skip
  2:   is 1 in set? Yes -> skip

Longest = 4  (the sequence [1,2,3,4])
```

**Python Solution**:

```python
def longest_consecutive(nums):
    num_set = set(nums)
    longest = 0

    for num in num_set:
        # Only start counting from the beginning of a sequence
        if num - 1 not in num_set:
            current = num
            length = 1

            while current + 1 in num_set:
                current += 1
                length += 1

            longest = max(longest, length)

    return longest


print(longest_consecutive([100, 4, 200, 1, 3, 2]))  # Output: 4
print(longest_consecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]))  # Output: 9
```

**Java Solution**:

```java
import java.util.HashSet;
import java.util.Set;

public class LongestConsecutive {
    public static int longestConsecutive(int[] nums) {
        Set<Integer> numSet = new HashSet<>();
        for (int num : nums) {
            numSet.add(num);
        }

        int longest = 0;

        for (int num : numSet) {
            if (!numSet.contains(num - 1)) {  // Start of a sequence
                int current = num;
                int length = 1;

                while (numSet.contains(current + 1)) {
                    current++;
                    length++;
                }

                longest = Math.max(longest, length);
            }
        }

        return longest;
    }

    public static void main(String[] args) {
        System.out.println(longestConsecutive(
            new int[]{100, 4, 200, 1, 3, 2}
        ));  // Output: 4
    }
}
```

**Complexity**: Time: O(n) -- each number is visited at most twice. Space: O(n).

---

### Problem 5: LRU Cache Design (LeetCode 146)

**Problem**: Design a Least Recently Used (LRU) cache with `get(key)` and `put(key, value)` operations in O(1) time. When the cache exceeds capacity, evict the least recently used item.

**Approach**: Combine a **hash map** (for O(1) key lookup) with a **doubly linked list** (for O(1) insertion/removal to track recency). The most recently used item is at the tail; the least recently used is at the head.

```
Capacity = 3

put(1,A):  Head <-> [1:A] <-> Tail              Map: {1:node1}
put(2,B):  Head <-> [1:A] <-> [2:B] <-> Tail    Map: {1:node1, 2:node2}
put(3,C):  Head <-> [1:A] <-> [2:B] <-> [3:C] <-> Tail
get(1):    Head <-> [2:B] <-> [3:C] <-> [1:A] <-> Tail   (1 moved to tail)
put(4,D):  Head <-> [3:C] <-> [1:A] <-> [4:D] <-> Tail   (2 evicted from head)
           Map: {3:node3, 1:node1, 4:node4}
```

**Python Solution**:

```python
class Node:
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}  # key -> Node

        # Dummy head and tail for easy insertion/removal
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        """Remove a node from the doubly linked list."""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_tail(self, node):
        """Add a node right before the tail (most recently used)."""
        node.prev = self.tail.prev
        node.next = self.tail
        self.tail.prev.next = node
        self.tail.prev = node

    def get(self, key):
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._add_to_tail(node)  # Mark as recently used
        return node.value

    def put(self, key, value):
        if key in self.cache:
            self._remove(self.cache[key])

        node = Node(key, value)
        self._add_to_tail(node)
        self.cache[key] = node

        if len(self.cache) > self.capacity:
            # Evict least recently used (right after head)
            lru = self.head.next
            self._remove(lru)
            del self.cache[lru.key]


# Test
cache = LRUCache(2)
cache.put(1, 1)
cache.put(2, 2)
print(cache.get(1))    # Output: 1
cache.put(3, 3)         # Evicts key 2
print(cache.get(2))    # Output: -1 (evicted)
cache.put(4, 4)         # Evicts key 1
print(cache.get(1))    # Output: -1 (evicted)
print(cache.get(3))    # Output: 3
print(cache.get(4))    # Output: 4
```

**Java Solution**:

```java
import java.util.HashMap;
import java.util.Map;

public class LRUCache {
    private static class Node {
        int key, value;
        Node prev, next;

        Node(int key, int value) {
            this.key = key;
            this.value = value;
        }
    }

    private int capacity;
    private Map<Integer, Node> cache;
    private Node head, tail;

    public LRUCache(int capacity) {
        this.capacity = capacity;
        this.cache = new HashMap<>();
        this.head = new Node(0, 0);
        this.tail = new Node(0, 0);
        head.next = tail;
        tail.prev = head;
    }

    private void remove(Node node) {
        node.prev.next = node.next;
        node.next.prev = node.prev;
    }

    private void addToTail(Node node) {
        node.prev = tail.prev;
        node.next = tail;
        tail.prev.next = node;
        tail.prev = node;
    }

    public int get(int key) {
        if (!cache.containsKey(key)) return -1;
        Node node = cache.get(key);
        remove(node);
        addToTail(node);
        return node.value;
    }

    public void put(int key, int value) {
        if (cache.containsKey(key)) {
            remove(cache.get(key));
        }
        Node node = new Node(key, value);
        addToTail(node);
        cache.put(key, node);

        if (cache.size() > capacity) {
            Node lru = head.next;
            remove(lru);
            cache.remove(lru.key);
        }
    }

    public static void main(String[] args) {
        LRUCache cache = new LRUCache(2);
        cache.put(1, 1);
        cache.put(2, 2);
        System.out.println(cache.get(1));   // Output: 1
        cache.put(3, 3);                     // Evicts 2
        System.out.println(cache.get(2));   // Output: -1
        cache.put(4, 4);                     // Evicts 1
        System.out.println(cache.get(1));   // Output: -1
        System.out.println(cache.get(3));   // Output: 3
        System.out.println(cache.get(4));   // Output: 4
    }
}
```

**Complexity**: Time: O(1) for both `get` and `put`. Space: O(capacity).

---

## What Is Next?

Hash tables give you O(1) lookups -- a superpower for many problems. In the next chapter, we explore **Recursion**, a problem-solving technique where a function calls itself. Recursion is the foundation for divide-and-conquer algorithms, tree traversals, and dynamic programming. Think of it like Russian nesting dolls -- each doll opens to reveal a smaller version of itself, until you reach the smallest one.
