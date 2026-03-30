# Chapter 28: Bit Manipulation

## What You Will Learn

- How computers represent numbers in binary
- The six bitwise operators: AND, OR, XOR, NOT, left shift, right shift
- Common tricks: check even/odd, multiply/divide by 2, check if a bit is set, count bits
- XOR properties and why they are so powerful
- How to solve classic bit manipulation problems: Single Number, Counting Bits, Reverse Bits, Power of Two, and Missing Number

## Why This Chapter Matters

Every number your computer stores is a sequence of 0s and 1s. Most of the time, we ignore this and work with decimal numbers. But sometimes, working directly with bits gives you solutions that are faster, use less memory, and feel like magic.

Need to find the one unique number in an array where every other number appears twice? XOR the entire array --- the answer pops out in O(n) time with O(1) space. Need to check if a number is a power of 2? One line of code: `n & (n - 1) == 0`.

Bit manipulation problems appear frequently in interviews, especially at companies that value low-level thinking. More importantly, understanding bits deepens your grasp of how computers actually work.

---

## 28.1 Binary Number Basics

Computers use **binary** (base 2). Each digit is a **bit** --- either 0 or 1.

### Decimal to Binary

```
Decimal 13 in binary:

  13 / 2 = 6  remainder 1
   6 / 2 = 3  remainder 0
   3 / 2 = 1  remainder 1
   1 / 2 = 0  remainder 1

  Read remainders bottom-up: 1101

  Verify: 1*8 + 1*4 + 0*2 + 1*1 = 8 + 4 + 0 + 1 = 13

Position values (right to left):
  Bit:      1    1    0    1
  Position: 3    2    1    0
  Value:    2^3  2^2  2^1  2^0
          = 8    4    2    1
```

### Common Binary Numbers

```
+----------+----------+------------------+
| Decimal  | Binary   | Note             |
+----------+----------+------------------+
| 0        | 0000     |                  |
| 1        | 0001     |                  |
| 2        | 0010     |                  |
| 3        | 0011     |                  |
| 4        | 0100     |                  |
| 5        | 0101     |                  |
| 7        | 0111     | all 1s (3 bits)  |
| 8        | 1000     | power of 2       |
| 10       | 1010     |                  |
| 15       | 1111     | all 1s (4 bits)  |
| 16       | 10000    | power of 2       |
| 255      | 11111111 | all 1s (8 bits)  |
+----------+----------+------------------+
```

### Python and Java Binary Representation

```python
# Python
print(bin(13))       # '0b1101'
print(int('1101', 2)) # 13
print(f"{13:08b}")   # '00001101' (8-bit padded)
```

```java
// Java
System.out.println(Integer.toBinaryString(13)); // "1101"
System.out.println(Integer.parseInt("1101", 2)); // 13
System.out.printf("%08d%n", Integer.parseInt(
    Integer.toBinaryString(13))); // 00001101
```

---

## 28.2 The Six Bitwise Operators

### AND (&) --- Both bits must be 1

```
  1 0 1 1  (11)
& 1 1 0 1  (13)
---------
  1 0 0 1  (9)

Rule: 1 & 1 = 1, everything else = 0
```

**Use cases:** Check if a bit is set, clear bits, mask bits.

### OR (|) --- At least one bit must be 1

```
  1 0 1 1  (11)
| 1 1 0 1  (13)
---------
  1 1 1 1  (15)

Rule: 0 | 0 = 0, everything else = 1
```

**Use cases:** Set bits, combine flags.

### XOR (^) --- Bits must differ

```
  1 0 1 1  (11)
^ 1 1 0 1  (13)
---------
  0 1 1 0  (6)

Rule: same bits = 0, different bits = 1
```

**Use cases:** Find unique elements, toggle bits, swap without temp.

### NOT (~) --- Flip all bits

```
~ 0 0 0 0 1 1 0 1  (13)
= 1 1 1 1 0 0 1 0  (-14 in two's complement)

In Python: ~13 = -14
In Java:   ~13 = -14 (32-bit integer)
```

**Note:** NOT in two's complement: `~n = -(n + 1)`

### Left Shift (<<) --- Shift bits left, fill with 0

```
  0 0 1 1 0 1  (13)
  << 2
  1 1 0 1 0 0  (52)

13 << 2 = 13 * 4 = 52
Left shift by k = multiply by 2^k
```

### Right Shift (>>) --- Shift bits right

```
  1 1 0 1  (13)
  >> 2
  0 0 1 1  (3)

13 >> 2 = 13 / 4 = 3 (integer division)
Right shift by k = divide by 2^k (floor)
```

### Summary Table

```
+----------+--------+-----------------------------+
| Operator | Symbol | Description                 |
+----------+--------+-----------------------------+
| AND      | &      | Both bits 1 -> 1            |
| OR       | |      | Either bit 1 -> 1           |
| XOR      | ^      | Different bits -> 1         |
| NOT      | ~      | Flip all bits               |
| L Shift  | <<     | Shift left (multiply by 2)  |
| R Shift  | >>     | Shift right (divide by 2)   |
+----------+--------+-----------------------------+
```

---

## 28.3 Common Bit Tricks

### Trick 1: Check Even or Odd

```python
def is_even(n):
    return (n & 1) == 0

def is_odd(n):
    return (n & 1) == 1

# Why it works:
# Even numbers end in 0 in binary (e.g., 6 = 110)
# Odd numbers end in 1 in binary  (e.g., 7 = 111)
# AND with 1 checks the last bit

print(is_even(6))  # True   (110 & 001 = 000)
print(is_odd(7))   # True   (111 & 001 = 001)
```

### Trick 2: Multiply and Divide by Powers of 2

```python
# Multiply by 2^k
x = 5
print(x << 1)  # 10  (5 * 2)
print(x << 3)  # 40  (5 * 8)

# Divide by 2^k (floor)
x = 20
print(x >> 1)  # 10  (20 / 2)
print(x >> 2)  # 5   (20 / 4)
```

### Trick 3: Check if Bit at Position k is Set

```python
def is_bit_set(n, k):
    return (n >> k) & 1 == 1

# Check bit 2 of 13 (1101):
# Shift right by 2: 1101 >> 2 = 11
# AND with 1:       11 & 01 = 01 = 1 (set!)
print(is_bit_set(13, 0))  # True  (bit 0 is 1)
print(is_bit_set(13, 1))  # False (bit 1 is 0)
print(is_bit_set(13, 2))  # True  (bit 2 is 1)
print(is_bit_set(13, 3))  # True  (bit 3 is 1)
```

### Trick 4: Set, Clear, and Toggle a Bit

```python
def set_bit(n, k):
    """Set bit k to 1."""
    return n | (1 << k)

def clear_bit(n, k):
    """Set bit k to 0."""
    return n & ~(1 << k)

def toggle_bit(n, k):
    """Flip bit k."""
    return n ^ (1 << k)

n = 13  # 1101
print(bin(set_bit(n, 1)))    # 0b1111 (15) - set bit 1
print(bin(clear_bit(n, 2)))  # 0b1001 (9)  - clear bit 2
print(bin(toggle_bit(n, 0))) # 0b1100 (12) - toggle bit 0
```

### Trick 5: Count Set Bits (Brian Kernighan's Algorithm)

```python
def count_bits(n):
    count = 0
    while n:
        n &= (n - 1)  # clears the lowest set bit
        count += 1
    return count

# How it works:
#   n = 13 = 1101
#   n-1 =    1100    n & (n-1) = 1100 (12), count=1
#   n-1 =    1011    n & (n-1) = 1000 (8),  count=2
#   n-1 =    0111    n & (n-1) = 0000 (0),  count=3
#   n = 0, stop.

print(count_bits(13))  # 3
print(count_bits(7))   # 3
print(count_bits(16))  # 1
```

### Trick 6: Check if Power of 2

```python
def is_power_of_two(n):
    return n > 0 and (n & (n - 1)) == 0

# Why: powers of 2 have exactly one set bit
# 8  = 1000,  8-1 = 0111,  1000 & 0111 = 0000
# 6  = 0110,  6-1 = 0101,  0110 & 0101 = 0100 (not 0)

print(is_power_of_two(8))   # True
print(is_power_of_two(6))   # False
print(is_power_of_two(1))   # True (2^0)
print(is_power_of_two(0))   # False
```

### Trick 7: Swap Two Numbers Without Temp

```python
a, b = 5, 9
a = a ^ b  # a = 5^9
b = a ^ b  # b = 5^9^9 = 5
a = a ^ b  # a = 5^9^5 = 9

print(a, b)  # 9 5
```

### All Tricks Summary

```
+-----------------------------+------------------+
| Trick                       | Expression       |
+-----------------------------+------------------+
| Check even                  | (n & 1) == 0     |
| Check odd                   | (n & 1) == 1     |
| Multiply by 2               | n << 1           |
| Divide by 2                 | n >> 1           |
| Check bit k                 | (n >> k) & 1     |
| Set bit k                   | n | (1 << k)     |
| Clear bit k                 | n & ~(1 << k)    |
| Toggle bit k                | n ^ (1 << k)     |
| Clear lowest set bit        | n & (n - 1)      |
| Isolate lowest set bit      | n & (-n)         |
| Check power of 2            | n & (n-1) == 0   |
| Count set bits              | loop n &= (n-1)  |
+-----------------------------+------------------+
```

---

## 28.4 XOR Properties

XOR is the most important bitwise operator for interview problems. Here are its key properties:

```
Property 1: a ^ a = 0     (any number XOR itself is 0)
    1101 ^ 1101 = 0000

Property 2: a ^ 0 = a     (any number XOR 0 is itself)
    1101 ^ 0000 = 1101

Property 3: a ^ b = b ^ a (commutative)
    Order does not matter.

Property 4: (a ^ b) ^ c = a ^ (b ^ c) (associative)
    Grouping does not matter.

Property 5: a ^ b ^ a = b (self-cancellation)
    XOR-ing a number twice cancels it out.
```

### Why XOR is Powerful

If you XOR an entire array where every element appears twice except one, all the pairs cancel out and only the unique element remains:

```
[4, 1, 2, 1, 2]

4 ^ 1 ^ 2 ^ 1 ^ 2
= 4 ^ (1 ^ 1) ^ (2 ^ 2)
= 4 ^ 0 ^ 0
= 4
```

---

## 28.5 Problem Solutions

### Problem 1: Single Number

**Problem:** Given an array where every element appears twice except one, find the unique element. Use O(1) space.

```python
def single_number(nums):
    result = 0
    for num in nums:
        result ^= num
    return result

# Test
print(single_number([4, 1, 2, 1, 2]))  # Output: 4
print(single_number([2, 2, 1]))         # Output: 1
print(single_number([1]))               # Output: 1
```

```java
public class SingleNumber {
    public static int singleNumber(int[] nums) {
        int result = 0;
        for (int num : nums) {
            result ^= num;
        }
        return result;
    }

    public static void main(String[] args) {
        System.out.println(singleNumber(new int[]{4, 1, 2, 1, 2}));
        // Output: 4
    }
}
```

**Step-by-step:**

```
nums = [4, 1, 2, 1, 2]
result = 0

result ^= 4  ->  0 ^ 4 = 4     (0000 ^ 0100 = 0100)
result ^= 1  ->  4 ^ 1 = 5     (0100 ^ 0001 = 0101)
result ^= 2  ->  5 ^ 2 = 7     (0101 ^ 0010 = 0111)
result ^= 1  ->  7 ^ 1 = 6     (0111 ^ 0001 = 0110)
result ^= 2  ->  6 ^ 2 = 4     (0110 ^ 0010 = 0100)

result = 4. The unique number!
```

**Complexity:** Time O(n), Space O(1)

---

### Problem 2: Counting Bits

**Problem:** Given an integer n, return an array of n+1 elements where `ans[i]` is the number of 1-bits in the binary representation of i.

```
n = 5

i:       0    1    2    3    4    5
binary:  000  001  010  011  100  101
bits:    0    1    1    2    1    2

Output: [0, 1, 1, 2, 1, 2]
```

**Key Insight:** `i & (i - 1)` removes the lowest set bit. So `bits[i] = bits[i & (i-1)] + 1`.

```python
def count_bits(n):
    result = [0] * (n + 1)
    for i in range(1, n + 1):
        result[i] = result[i & (i - 1)] + 1
    return result

# Test
print(count_bits(5))
# Output: [0, 1, 1, 2, 1, 2]

print(count_bits(8))
# Output: [0, 1, 1, 2, 1, 2, 2, 3, 1]
```

```java
public class CountingBits {
    public static int[] countBits(int n) {
        int[] result = new int[n + 1];
        for (int i = 1; i <= n; i++) {
            result[i] = result[i & (i - 1)] + 1;
        }
        return result;
    }

    public static void main(String[] args) {
        int[] bits = countBits(5);
        for (int b : bits) {
            System.out.print(b + " ");
        }
        // Output: 0 1 1 2 1 2
    }
}
```

**Step-by-step:**

```
i=1: 1 & 0 = 0  -> result[0] + 1 = 1
i=2: 2 & 1 = 0  -> result[0] + 1 = 1
i=3: 3 & 2 = 2  -> result[2] + 1 = 2
i=4: 4 & 3 = 0  -> result[0] + 1 = 1
i=5: 5 & 4 = 4  -> result[4] + 1 = 2
```

**Complexity:** Time O(n), Space O(n) for the result

---

### Problem 3: Reverse Bits

**Problem:** Reverse the bits of a 32-bit unsigned integer.

```
Input:  00000010100101000001111010011100  (43261596)
Output: 00111001011110000010100101000000  (964176192)
```

```python
def reverse_bits(n):
    result = 0
    for i in range(32):
        # Get the rightmost bit of n
        bit = n & 1
        # Place it at position (31 - i) in result
        result = (result << 1) | bit
        # Shift n right
        n >>= 1
    return result

# Test
print(reverse_bits(43261596))
# Output: 964176192
```

```java
public class ReverseBits {
    public static int reverseBits(int n) {
        int result = 0;
        for (int i = 0; i < 32; i++) {
            result = (result << 1) | (n & 1);
            n >>= 1;
        }
        return result;
    }

    public static void main(String[] args) {
        System.out.println(Integer.toUnsignedString(
            reverseBits(43261596)));
        // Output: 964176192
    }
}
```

**Step-by-step (simplified with 8-bit example):**

```
Reverse bits of 13 (00001101) in 8 bits:

i=0: bit=1, result=00000001, n=00000110
i=1: bit=0, result=00000010, n=00000011
i=2: bit=1, result=00000101, n=00000001
i=3: bit=1, result=00001011, n=00000000
i=4: bit=0, result=00010110, n=00000000
i=5: bit=0, result=00101100, n=00000000
i=6: bit=0, result=01011000, n=00000000
i=7: bit=0, result=10110000, n=00000000

Result: 10110000 (176)
```

**Complexity:** Time O(1) --- always 32 iterations. Space O(1).

---

### Problem 4: Power of Two

**Problem:** Determine if a given integer is a power of two.

```python
def is_power_of_two(n):
    return n > 0 and (n & (n - 1)) == 0

# Test
print(is_power_of_two(1))    # True  (2^0)
print(is_power_of_two(16))   # True  (2^4)
print(is_power_of_two(3))    # False
print(is_power_of_two(0))    # False
print(is_power_of_two(-4))   # False
```

```java
public class PowerOfTwo {
    public static boolean isPowerOfTwo(int n) {
        return n > 0 && (n & (n - 1)) == 0;
    }

    public static void main(String[] args) {
        System.out.println(isPowerOfTwo(16));  // true
        System.out.println(isPowerOfTwo(3));   // false
    }
}
```

**Why it works:**

```
Powers of 2 have exactly one 1-bit:

  1  = 00000001     1-1  = 00000000    AND = 0
  2  = 00000010     2-1  = 00000001    AND = 0
  4  = 00000100     4-1  = 00000011    AND = 0
  8  = 00001000     8-1  = 00000111    AND = 0
  16 = 00010000     16-1 = 00001111    AND = 0

Non-powers of 2 have multiple 1-bits:

  6  = 00000110     6-1  = 00000101    AND = 00000100 (not 0)
  10 = 00001010     10-1 = 00001001    AND = 00001000 (not 0)
```

**Complexity:** Time O(1), Space O(1)

---

### Problem 5: Missing Number

**Problem:** Given an array of n distinct numbers from the range [0, n], find the missing number.

```
Input: [3, 0, 1]
Range: [0, 1, 2, 3]
Missing: 2
```

**Approach 1: XOR**

XOR all numbers from 0 to n, then XOR with all array elements. Pairs cancel, leaving the missing number.

```python
def missing_number_xor(nums):
    n = len(nums)
    result = n  # start with n (since we XOR 0 to n-1 in loop)

    for i in range(n):
        result ^= i ^ nums[i]

    return result

# Test
print(missing_number_xor([3, 0, 1]))  # Output: 2
print(missing_number_xor([0, 1]))     # Output: 2
print(missing_number_xor([9,6,4,2,3,5,7,0,1]))  # Output: 8
```

**Step-by-step:**

```
nums = [3, 0, 1], n = 3

result = 3                     (start with n)
i=0: result ^= 0 ^ 3 = 3 ^ 0 ^ 3 = 0
i=1: result ^= 1 ^ 0 = 0 ^ 1 ^ 0 = 1
i=2: result ^= 2 ^ 1 = 1 ^ 2 ^ 1 = 2

result = 2. Missing number!
```

**Approach 2: Sum Formula**

```python
def missing_number_sum(nums):
    n = len(nums)
    expected = n * (n + 1) // 2
    actual = sum(nums)
    return expected - actual

print(missing_number_sum([3, 0, 1]))  # Output: 2
```

```java
public class MissingNumber {
    public static int missingNumber(int[] nums) {
        int n = nums.length;
        int result = n;
        for (int i = 0; i < n; i++) {
            result ^= i ^ nums[i];
        }
        return result;
    }

    public static void main(String[] args) {
        System.out.println(missingNumber(new int[]{3, 0, 1}));
        // Output: 2
    }
}
```

**Complexity:** Time O(n), Space O(1) for both approaches.

---

## 28.6 Two's Complement (How Negative Numbers Work)

Understanding negative numbers in binary helps avoid bugs.

```
In 8-bit two's complement:

 5 = 00000101
-5 = 11111011  (flip all bits of 5, then add 1)

Verification: 5 + (-5) = 00000101 + 11111011 = 100000000
              The 9th bit overflows, leaving 00000000 = 0

Range of 8-bit signed: -128 to 127
Range of 32-bit signed (Java int): -2^31 to 2^31 - 1
```

**Python note:** Python integers have unlimited precision, so there is no overflow. Negative numbers are handled differently internally. Use `& 0xFFFFFFFF` to simulate 32-bit behavior when needed.

---

## Common Mistakes

1. **Operator precedence.** In most languages, `==` has higher precedence than `&`. Write `(n & 1) == 0`, not `n & 1 == 0` (which evaluates as `n & (1 == 0)` = `n & 0` = always 0).

2. **Confusing logical and bitwise operators.** `&&` (logical AND) is not the same as `&` (bitwise AND). `||` is not `|`. In Python, use `and`/`or` for logic and `&`/`|` for bits.

3. **Signed vs unsigned right shift.** In Java, `>>` preserves the sign bit (arithmetic shift), while `>>>` fills with 0 (logical shift). Python only has `>>` (arithmetic) since integers have no fixed size.

4. **Forgetting n > 0 check.** In "power of 2" check, `0 & (-1) = 0`, so `n & (n-1) == 0` is true for n=0. Always check `n > 0`.

5. **Python's infinite-precision integers.** `~13` in Python is -14 (not a 32-bit flip). To get the 32-bit flip, use `n ^ 0xFFFFFFFF`.

---

## Best Practices

- **Memorize the tricks table.** The 12 common bit tricks cover 90% of interview bit problems. Know them cold.
- **Use parentheses generously.** Bitwise operator precedence is confusing. Parentheses make intent clear.
- **Think in terms of XOR properties** for "find the unique/missing" problems. Self-cancellation (a^a=0) is the key insight.
- **Draw the binary.** When debugging, write out the binary representation of each number. Bit manipulation is visual.
- **Use built-in functions for verification.** `bin()` in Python, `Integer.toBinaryString()` in Java. Compare your manual result.

---

## Quick Summary

| Operation | Expression | Description |
|-----------|-----------|-------------|
| AND | a & b | Both bits must be 1 |
| OR | a \| b | Either bit must be 1 |
| XOR | a ^ b | Bits must differ |
| NOT | ~a | Flip all bits |
| Left shift | a << k | Multiply by 2^k |
| Right shift | a >> k | Divide by 2^k |

XOR is the star of bit manipulation: `a^a=0`, `a^0=a`, and self-cancellation enable O(n)/O(1) solutions to uniqueness and missing-element problems.

---

## Key Points

- Every integer is a sequence of bits. Understanding binary unlocks a set of constant-time tricks.
- AND masks bits, OR sets bits, XOR toggles/finds differences, NOT flips everything.
- `n & (n-1)` clears the lowest set bit --- the foundation for counting bits and checking powers of 2.
- XOR's self-cancellation property (`a^a=0`) solves "find the unique element" in O(1) space.
- Bit manipulation produces the most efficient possible solutions for certain problem classes.

---

## Practice Questions

1. What is the binary representation of -7 in 8-bit two's complement? Verify by adding 7 + (-7).

2. Given `n & (n-1)` clears the lowest set bit, how can you isolate the lowest set bit? (Hint: think about `n & (-n)`.)

3. How would you find two unique numbers in an array where every other number appears twice? (Hint: XOR all, then split by a distinguishing bit.)

4. Explain why left shifting by 1 is equivalent to multiplying by 2. What happens if the highest bit overflows?

5. Can you check if a 32-bit integer has alternating bits (like 1010...10) using bit manipulation?

---

## LeetCode-Style Problems

### Problem 1: Hamming Distance --- LeetCode 461 (Easy)

**Problem:** The Hamming distance between two integers is the number of positions at which the corresponding bits differ.

```python
def hamming_distance(x, y):
    xor = x ^ y  # bits that differ are 1
    count = 0
    while xor:
        xor &= (xor - 1)  # clear lowest set bit
        count += 1
    return count

print(hamming_distance(1, 4))   # Output: 2
# 1 = 001, 4 = 100, XOR = 101 (2 set bits)

print(hamming_distance(3, 1))   # Output: 1
# 3 = 11, 1 = 01, XOR = 10 (1 set bit)
```

**Complexity:** Time O(1) (at most 32 bits), Space O(1)

---

### Problem 2: Number Complement --- LeetCode 476 (Easy)

**Problem:** Given a positive integer, flip all bits in its binary representation. Do not include leading zeros.

```python
def find_complement(num):
    # Create a mask with all 1s of the same length as num
    mask = 1
    while mask <= num:
        mask <<= 1
    mask -= 1  # e.g., for 5 (101), mask = 111

    return num ^ mask

print(find_complement(5))   # Output: 2  (101 ^ 111 = 010)
print(find_complement(1))   # Output: 0  (1 ^ 1 = 0)
print(find_complement(7))   # Output: 0  (111 ^ 111 = 000)
```

**Complexity:** Time O(log n), Space O(1)

---

### Problem 3: Sum of Two Integers Without + or - --- LeetCode 371 (Medium)

**Problem:** Calculate the sum of two integers without using + or -.

```python
def get_sum(a, b):
    # 32-bit mask
    MASK = 0xFFFFFFFF
    MAX = 0x7FFFFFFF

    while b != 0:
        carry = (a & b) & MASK
        a = (a ^ b) & MASK
        b = (carry << 1) & MASK

    # Handle negative results in Python
    return a if a <= MAX else ~(a ^ MASK)

print(get_sum(1, 2))    # Output: 3
print(get_sum(-2, 3))   # Output: 1
```

```java
public class SumWithoutPlus {
    public static int getSum(int a, int b) {
        while (b != 0) {
            int carry = a & b;
            a = a ^ b;
            b = carry << 1;
        }
        return a;
    }

    public static void main(String[] args) {
        System.out.println(getSum(1, 2));   // 3
        System.out.println(getSum(-2, 3));  // 1
    }
}
```

**How it works:**
- XOR gives the sum without carries: `1 ^ 1 = 0` (like 1+1=0 carry 1)
- AND gives the carry bits: `1 & 1 = 1`
- Shift carry left and repeat until no carry remains

**Complexity:** Time O(1) (at most 32 iterations), Space O(1)

---

## What Is Next?

You have learned to think in binary --- to see numbers not as decimal values but as sequences of bits you can manipulate directly. These techniques produce solutions that are often the fastest and most space-efficient possible.

In the next chapter, we step back and look at the big picture with **Problem-Solving Patterns**. We catalog all the major algorithm patterns you have learned --- Two Pointers, Sliding Window, BFS/DFS, DP, and more --- and build a decision framework for matching problems to the right technique.
