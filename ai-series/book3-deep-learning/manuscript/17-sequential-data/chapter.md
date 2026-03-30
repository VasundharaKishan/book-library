# Chapter 17: Sequential Data — When Order Matters

## What You Will Learn

- Why the order of data points matters in many real-world problems
- What sequential data is and where you encounter it every day
- How time series data works (stock prices, weather, sensor readings)
- How text is a sequence of words (and why word order changes meaning)
- Why regular neural networks cannot handle sequences (they have no memory)
- What the sliding window approach is and why it has limits
- The difference between sequence-to-one and sequence-to-sequence tasks
- Why we need special architectures designed for sequences

## Why This Chapter Matters

Imagine you are watching a movie. Each scene makes sense because of what happened before it. If you shuffle the scenes randomly, the story falls apart. The order matters.

The same is true for many types of data. The sentence "the dog chased the cat" means something very different from "the cat chased the dog." The words are the same. The order changes the meaning completely.

Stock prices, weather patterns, heart rate monitors, speech, music, and text all share one thing in common. They are **sequential**. Each data point depends on what came before it.

The neural networks we have built so far (fully connected networks and CNNs) treat every input as independent. They look at an image and classify it. But they do not remember what they saw one second ago. They have no concept of "before" and "after."

This chapter explains the problem. The next chapters will show you the solutions.

---

## 17.1 What Is Sequential Data?

Sequential data is any data where the **order matters**. Each item in the sequence has a relationship to the items that came before it and the items that come after it.

Think of it like a **chain of dominoes**:

```
+-------+    +-------+    +-------+    +-------+    +-------+
|       |    |       |    |       |    |       |    |       |
| Item  |--->| Item  |--->| Item  |--->| Item  |--->| Item  |
|   1   |    |   2   |    |   3   |    |   4   |    |   5   |
|       |    |       |    |       |    |       |    |       |
+-------+    +-------+    +-------+    +-------+    +-------+

  Each item depends on what came before it.
  The order carries meaning.
```

Here is a simple way to see why order matters:

```python
# Order changes meaning completely
sentence_1 = ["the", "dog", "bit", "the", "man"]
sentence_2 = ["the", "man", "bit", "the", "dog"]

print("Sentence 1:", " ".join(sentence_1))
print("Sentence 2:", " ".join(sentence_2))
print("Same words?", sorted(sentence_1) == sorted(sentence_2))
print("Same meaning?", "No!")
```

**Expected Output:**
```
Sentence 1: the dog bit the man
Sentence 2: the man bit the dog
Same words? True
Same meaning? No!
```

**Line-by-line explanation:**
- **Line 2:** We create a list of words in one order. A dog biting a man is a normal event.
- **Line 3:** We create a list with the same words but in a different order. A man biting a dog is very unusual.
- **Line 5:** We print the first sentence by joining the words with spaces.
- **Line 6:** We print the second sentence the same way.
- **Line 7:** We sort both lists alphabetically and compare. The words are identical.
- **Line 8:** But the meaning is completely different. Order matters.

### Examples of Sequential Data in Daily Life

```
+------------------------------------------------------------------+
|                 Sequential Data Examples                          |
+------------------------------------------------------------------+
|                                                                   |
|  TEXT:        "I love this movie" (word order = meaning)          |
|                                                                   |
|  SPEECH:      Sound waves over time (audio signal)                |
|                                                                   |
|  MUSIC:       Notes played in order (melody)                      |
|                                                                   |
|  STOCK:       Price at 9am, 10am, 11am... (time series)           |
|                                                                   |
|  WEATHER:     Temperature each hour (trends matter)               |
|                                                                   |
|  DNA:         A-T-C-G-G-A-T... (genetic code)                    |
|                                                                   |
|  VIDEO:       Frame 1, Frame 2, Frame 3... (motion)               |
|                                                                   |
|  HEARTBEAT:   ECG signal over time (rhythm)                       |
|                                                                   |
+------------------------------------------------------------------+
```

---

## 17.2 Time Series — Numbers Over Time

A **time series** is a sequence of numbers recorded at regular time intervals. Think of it as a list of measurements taken at different moments.

The word **time series** has two parts:
- **Time** means the measurements are ordered by when they happened.
- **Series** means a sequence of values, one after another.

```python
import torch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Daily temperatures for one week (in Celsius)
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
temperatures = [22, 24, 23, 25, 27, 26, 24]

print("Day-by-day temperatures:")
for day, temp in zip(days, temperatures):
    print(f"  {day}: {temp}C")

# Convert to a PyTorch tensor
temp_tensor = torch.tensor(temperatures, dtype=torch.float32)
print(f"\nAs a tensor: {temp_tensor}")
print(f"Shape: {temp_tensor.shape}")
print(f"Average temperature: {temp_tensor.mean():.1f}C")
```

**Expected Output:**
```
Day-by-day temperatures:
  Mon: 22C
  Tue: 24C
  Wed: 23C
  Thu: 25C
  Fri: 27C
  Sat: 26C
  Sun: 24C

As a tensor: tensor([22., 24., 23., 25., 27., 26., 24.])
Shape: torch.Size([7])
Average temperature: 24.4C
```

**Line-by-line explanation:**
- **Line 1:** We import PyTorch for tensor operations.
- **Lines 2-3:** We import matplotlib for plotting. The `Agg` backend lets us work without a display.
- **Line 6:** A list of day names. These are our time labels.
- **Line 7:** A list of temperatures. Each number corresponds to one day.
- **Lines 9-11:** We print each day and its temperature using `zip`, which pairs items from both lists.
- **Line 14:** We convert the temperatures to a PyTorch tensor. We use `float32` because neural networks work with floating-point numbers.
- **Lines 15-17:** We print the tensor, its shape (7 values), and the average.

### Why Time Order Matters in Time Series

If you shuffle the temperatures, you lose the pattern. You can no longer see that temperatures were rising from Monday to Friday.

```python
import torch

# Original sequence - you can see the trend
original = torch.tensor([22.0, 24.0, 23.0, 25.0, 27.0, 26.0, 24.0])

# Shuffled sequence - the trend disappears
shuffled = torch.tensor([25.0, 22.0, 27.0, 24.0, 23.0, 24.0, 26.0])

print("Original (in order):", original.tolist())
print("Shuffled (random):  ", shuffled.tolist())
print(f"\nBoth have the same mean: {original.mean():.1f} vs {shuffled.mean():.1f}")
print(f"Both have the same values, but only the original shows the trend.")
```

**Expected Output:**
```
Original (in order): [22.0, 24.0, 23.0, 25.0, 27.0, 26.0, 24.0]
Shuffled (random):   [25.0, 22.0, 27.0, 24.0, 23.0, 24.0, 26.0]

Both have the same mean: 24.4 vs 24.4
Both have the same values, but only the original shows the trend.
```

---

## 17.3 Text as a Sequence

Text is one of the most common types of sequential data. Every sentence is a sequence of words. Every word is a sequence of characters.

When we want a neural network to understand text, we need to convert words into numbers. This process is called **tokenization** and **encoding**.

The word **tokenization** means breaking text into small pieces called **tokens**. A token can be a word, a part of a word, or even a single character.

```python
import torch

# A simple sentence
sentence = "I love deep learning"

# Step 1: Tokenize (split into words)
tokens = sentence.lower().split()
print("Tokens:", tokens)

# Step 2: Build a vocabulary (assign a number to each word)
vocabulary = {}
for i, word in enumerate(tokens):
    if word not in vocabulary:
        vocabulary[word] = len(vocabulary)

print("Vocabulary:", vocabulary)

# Step 3: Encode the sentence as numbers
encoded = [vocabulary[word] for word in tokens]
print("Encoded:", encoded)

# Step 4: Convert to a PyTorch tensor
tensor = torch.tensor(encoded)
print("Tensor:", tensor)
print("Shape:", tensor.shape)
```

**Expected Output:**
```
Tokens: ['i', 'love', 'deep', 'learning']
Vocabulary: {'i': 0, 'love': 1, 'deep': 2, 'learning': 3}
Encoded: [0, 1, 2, 3]
Tensor: tensor([0, 1, 2, 3])
Shape: torch.Size([4])
```

**Line-by-line explanation:**
- **Line 4:** Our input sentence. It has four words.
- **Line 7:** We convert to lowercase and split by spaces. This gives us a list of tokens (words).
- **Lines 10-13:** We build a vocabulary. A **vocabulary** is a dictionary that maps each unique word to a number. We check if the word is already in the dictionary before adding it.
- **Line 15:** We print the vocabulary. Each word has a unique number.
- **Line 18:** We replace each word with its number from the vocabulary. This is called **encoding**.
- **Lines 21-23:** We convert the list of numbers to a PyTorch tensor. The shape is `[4]` because there are four words.

### Word Order Changes Everything

```python
import torch

# Build vocabulary from multiple sentences
all_words = ["the", "cat", "sat", "on", "mat", "dog", "chased"]
vocab = {word: i for i, word in enumerate(all_words)}
print("Vocabulary:", vocab)

# Two sentences with different word orders
sentence_a = ["the", "cat", "chased", "the", "dog"]
sentence_b = ["the", "dog", "chased", "the", "cat"]

encoded_a = torch.tensor([vocab[w] for w in sentence_a])
encoded_b = torch.tensor([vocab[w] for w in sentence_b])

print(f"\nSentence A: {' '.join(sentence_a)}")
print(f"Encoded A:  {encoded_a.tolist()}")
print(f"\nSentence B: {' '.join(sentence_b)}")
print(f"Encoded B:  {encoded_b.tolist()}")
print(f"\nSame numbers? {set(encoded_a.tolist()) == set(encoded_b.tolist())}")
print(f"Same sequence? {torch.equal(encoded_a, encoded_b)}")
```

**Expected Output:**
```
Vocabulary: {'the': 0, 'cat': 1, 'sat': 2, 'on': 3, 'mat': 4, 'dog': 5, 'chased': 6}

Sentence A: the cat chased the dog
Encoded A:  [0, 1, 6, 0, 5]

Sentence B: the dog chased the cat
Encoded B:  [0, 5, 6, 0, 1]

Same numbers? True
Same sequence? False
```

**Line-by-line explanation:**
- **Line 4:** We define all possible words. In real applications, you would collect these from your entire dataset.
- **Line 5:** We create a vocabulary dictionary using a dictionary comprehension. Each word gets a unique integer.
- **Lines 9-10:** Two sentences with the same words but different order. The cat chases the dog in one. The dog chases the cat in the other.
- **Lines 12-13:** We encode both sentences as tensors of integers.
- **Line 19:** We check if they use the same set of numbers. Yes, they do.
- **Line 20:** We check if the tensors are identical. No. The order is different, so the meaning is different.

---

## 17.4 Why Regular Neural Networks Cannot Handle Sequences

The neural networks we have built so far are called **feedforward networks**. Data flows in one direction: from input to output. There is no loop, no memory, no concept of time.

The word **feedforward** means data moves only forward through the layers. It never goes backward or loops around.

```
+-------------------------------------------------------+
|          Feedforward Neural Network                    |
+-------------------------------------------------------+
|                                                        |
|   Input ---> Hidden Layer ---> Hidden Layer ---> Output|
|                                                        |
|   No memory. Each input is processed independently.    |
|   The network does not know what it saw before.        |
|                                                        |
+-------------------------------------------------------+
```

Here is the core problem:

```python
import torch
import torch.nn as nn

# A simple feedforward network
feedforward = nn.Sequential(
    nn.Linear(4, 8),
    nn.ReLU(),
    nn.Linear(8, 1)
)

# Two different sequences (same numbers, different order)
seq_a = torch.tensor([1.0, 2.0, 3.0, 4.0])  # ascending
seq_b = torch.tensor([4.0, 3.0, 2.0, 1.0])  # descending

# The feedforward network sees them as two separate inputs
# It does NOT know they are sequences
output_a = feedforward(seq_a)
output_b = feedforward(seq_b)

print(f"Input A (ascending):  {seq_a.tolist()}")
print(f"Output A:             {output_a.item():.4f}")
print(f"\nInput B (descending): {seq_b.tolist()}")
print(f"Output B:             {output_b.item():.4f}")
print(f"\nThe network gives different outputs,")
print(f"but it does NOT know A is ascending and B is descending.")
print(f"It simply treats them as two unrelated vectors of 4 numbers.")
```

**Expected Output:**
```
Input A (ascending):  [1.0, 2.0, 3.0, 4.0]
Output A:             -0.2731

Input B (descending): [4.0, 3.0, 2.0, 1.0]
Output B:             -0.5648

The network gives different outputs,
but it does NOT know A is ascending and B is descending.
It simply treats them as two unrelated vectors of 4 numbers.
```

(Note: Your exact numbers will differ because the network starts with random weights.)

**Line-by-line explanation:**
- **Lines 5-9:** We create a simple feedforward network. It takes 4 inputs, passes through 8 hidden neurons, and produces 1 output.
- **Lines 12-13:** Two sequences. One goes up (1, 2, 3, 4). The other goes down (4, 3, 2, 1).
- **Lines 17-18:** We pass both through the network. It processes each one separately with no concept of order or time.

### The Three Problems with Feedforward Networks for Sequences

```
+------------------------------------------------------------------+
|     Why Feedforward Networks Fail with Sequences                  |
+------------------------------------------------------------------+
|                                                                   |
|  Problem 1: NO MEMORY                                             |
|  The network processes each input independently.                  |
|  It does not remember what it saw one step ago.                   |
|                                                                   |
|  Problem 2: FIXED INPUT SIZE                                      |
|  The network expects exactly N inputs.                            |
|  But sentences have different lengths (3 words, 10 words, 50).    |
|                                                                   |
|  Problem 3: NO SENSE OF POSITION                                  |
|  Input slot 1 and input slot 3 are just different features.       |
|  The network does not know that slot 3 comes after slot 1.        |
|                                                                   |
+------------------------------------------------------------------+
```

Let us demonstrate the fixed input size problem:

```python
import torch
import torch.nn as nn

# Network expects exactly 5 inputs
net = nn.Linear(5, 2)

# Short sentence (3 words) - does not fit!
short = torch.tensor([1.0, 2.0, 3.0])

# Long sentence (7 words) - does not fit!
long_sent = torch.tensor([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0])

# Just right (5 words) - fits!
just_right = torch.tensor([1.0, 2.0, 3.0, 4.0, 5.0])

try:
    output = net(short)
    print("Short sentence worked")
except RuntimeError as e:
    print(f"Short sentence FAILED: {e}")

try:
    output = net(long_sent)
    print("Long sentence worked")
except RuntimeError as e:
    print(f"Long sentence FAILED: {e}")

output = net(just_right)
print(f"Just right worked: output = {output.tolist()}")
```

**Expected Output:**
```
Short sentence FAILED: mat1 and mat2 shapes cannot be multiplied (1x3 and 5x2)
Long sentence FAILED: mat1 and mat2 shapes cannot be multiplied (1x7 and 5x2)
Just right worked: output = [0.5123, -0.3456]
```

**Line-by-line explanation:**
- **Line 5:** A linear layer expecting exactly 5 input features.
- **Line 8:** A short sequence with only 3 values. Too few for the network.
- **Line 11:** A long sequence with 7 values. Too many for the network.
- **Line 14:** Exactly 5 values. This fits the network perfectly.
- **Lines 16-26:** We try all three. Only the one with exactly 5 values works. Real text has different lengths, so this is a serious problem.

---

## 17.5 The Sliding Window Approach

One early attempt to handle sequences with feedforward networks is the **sliding window** approach. You take a fixed-size window and slide it across the sequence, looking at a few items at a time.

The word **sliding window** describes a technique where you move a small window across your data, processing only what is visible through the window at each step.

Think of it like reading through a keyhole. You can only see a few words at a time:

```
Sentence: "The cat sat on the mat and then fell asleep"

Window size = 3:

Step 1: [The, cat, sat]           --> predict next word
Step 2: [cat, sat, on]            --> predict next word
Step 3: [sat, on, the]            --> predict next word
Step 4: [on, the, mat]            --> predict next word
...and so on
```

```python
import torch

# A sequence of stock prices
prices = [100, 102, 101, 105, 107, 110, 108, 112]

# Create sliding windows of size 3
window_size = 3
windows = []
targets = []

for i in range(len(prices) - window_size):
    window = prices[i:i + window_size]       # take 3 prices
    target = prices[i + window_size]          # the next price
    windows.append(window)
    targets.append(target)
    print(f"Window {i+1}: {window} --> predict {target}")

# Convert to tensors
X = torch.tensor(windows, dtype=torch.float32)
y = torch.tensor(targets, dtype=torch.float32)

print(f"\nInput tensor shape:  {X.shape}")
print(f"Target tensor shape: {y.shape}")
```

**Expected Output:**
```
Window 1: [100, 102, 101] --> predict 105
Window 2: [102, 101, 105] --> predict 107
Window 3: [101, 105, 107] --> predict 110
Window 4: [105, 107, 110] --> predict 108
Window 5: [107, 110, 108] --> predict 112

Input tensor shape:  torch.Size([5, 3])
Target tensor shape: torch.Size([5])
```

**Line-by-line explanation:**
- **Line 4:** A list of stock prices over 8 time steps.
- **Line 7:** We choose a window size of 3. We will look at 3 prices at a time.
- **Lines 11-16:** We loop through the prices. For each position, we take 3 consecutive prices as our input and the next price as our target. This creates training data where the model learns to predict the next price from the previous 3.
- **Lines 19-20:** We convert the lists to PyTorch tensors. `X` has shape `[5, 3]` meaning 5 examples, each with 3 features.

### Why Sliding Windows Have Limits

```
+------------------------------------------------------------------+
|           Limitations of the Sliding Window                       |
+------------------------------------------------------------------+
|                                                                   |
|  1. LIMITED CONTEXT                                               |
|     Window of 3 cannot see patterns that span 10 steps.           |
|     "The man who went to the store bought milk."                  |
|     A window of 3 starting at "store" cannot see "man".           |
|                                                                   |
|  2. FIXED WINDOW SIZE                                             |
|     How big should the window be? 3? 5? 100?                      |
|     Too small = miss long patterns.                               |
|     Too big = too many parameters, slow training.                 |
|                                                                   |
|  3. NO TRUE MEMORY                                                |
|     Each window is processed independently.                       |
|     Information from window 1 does not carry to window 5.         |
|                                                                   |
+------------------------------------------------------------------+
```

```python
import torch

# Showing the limited context problem
long_sequence = list(range(1, 21))  # 1 to 20
print("Full sequence:", long_sequence)

# With window size 3, we can only see 3 numbers at a time
window_size = 3
print(f"\nWindow size: {window_size}")
print(f"At position 15, the window sees: {long_sequence[14:14+window_size]}")
print(f"It CANNOT see what happened at position 1: {long_sequence[0]}")
print(f"The gap is {14 - 0} = 14 steps away. That context is lost.")

# Even with a bigger window of 5
window_size = 5
print(f"\nWindow size: {window_size}")
print(f"At position 15, the window sees: {long_sequence[14:14+window_size]}")
print(f"Still cannot see position 1. The gap is still too large.")
print(f"\nWe need a network that can REMEMBER information over long distances.")
```

**Expected Output:**
```
Full sequence: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

Window size: 3
At position 15, the window sees: [15, 16, 17]
It CANNOT see what happened at position 1: 1
The gap is 14 = 14 steps away. That context is lost.

Window size: 5
At position 15, the window sees: [15, 16, 17, 18, 19]
Still cannot see position 1. The gap is still too large.

We need a network that can REMEMBER information over long distances.
```

---

## 17.6 Sequence-to-One vs Sequence-to-Sequence

Before we build solutions, let us understand two common types of sequence tasks.

### Sequence-to-One

In a **sequence-to-one** task, you feed in a whole sequence and get back a single output.

Think of reading an entire movie review and giving it one rating: thumbs up or thumbs down.

```
+---------------------------------------------------+
|              Sequence-to-One                       |
+---------------------------------------------------+
|                                                    |
|  Input:  [word1, word2, word3, ..., wordN]         |
|                      |                             |
|                      v                             |
|               [Neural Network]                     |
|                      |                             |
|                      v                             |
|  Output:        ONE value                          |
|           (positive / negative)                    |
|                                                    |
+---------------------------------------------------+
|                                                    |
|  Examples:                                         |
|  - Sentiment analysis (review --> rating)           |
|  - Spam detection (email --> spam or not)           |
|  - Stock prediction (past prices --> tomorrow's)    |
|  - Music genre (audio --> genre label)              |
|                                                    |
+---------------------------------------------------+
```

```python
import torch

# Sentiment analysis: sequence of words --> one label
review_positive = torch.tensor([45, 12, 78, 3, 91])   # "I love this great movie"
review_negative = torch.tensor([45, 67, 23, 88, 14])   # "I hate this awful movie"

label_positive = torch.tensor([1])   # 1 = positive
label_negative = torch.tensor([0])   # 0 = negative

print("Positive review (encoded):", review_positive.tolist())
print("Label:", label_positive.item(), "(positive)")
print()
print("Negative review (encoded):", review_negative.tolist())
print("Label:", label_negative.item(), "(negative)")
print()
print("Input: a SEQUENCE of word IDs")
print("Output: ONE number (0 or 1)")
```

**Expected Output:**
```
Positive review (encoded): [45, 12, 78, 3, 91]
Label: 1 (positive)

Negative review (encoded): [45, 67, 23, 88, 14]
Label: 0 (negative)

Input: a SEQUENCE of word IDs
Output: ONE number (0 or 1)
```

### Sequence-to-Sequence

In a **sequence-to-sequence** task, you feed in a sequence and get back another sequence. The output has a value for every position in the input (or even a different length).

Think of translating a sentence from English to French. You feed in a sequence of English words and get back a sequence of French words.

```
+---------------------------------------------------+
|           Sequence-to-Sequence                     |
+---------------------------------------------------+
|                                                    |
|  Input:  [word1, word2, word3, ..., wordN]         |
|             |      |      |            |           |
|             v      v      v            v           |
|          [Neural Network at each step]             |
|             |      |      |            |           |
|             v      v      v            v           |
|  Output: [out1,  out2,  out3,  ...,  outN]         |
|                                                    |
+---------------------------------------------------+
|                                                    |
|  Examples:                                         |
|  - Translation (English --> French)                 |
|  - Named entity recognition (words --> labels)      |
|  - Text generation (input text --> continued text)   |
|  - Speech recognition (audio --> text)               |
|                                                    |
+---------------------------------------------------+
```

```python
import torch

# Named Entity Recognition: label each word
words =  ["John",   "lives", "in", "New",      "York"]
labels = ["PERSON", "O",     "O",  "LOCATION", "LOCATION"]

# O means "Other" (not an entity)

# Encode words and labels as numbers
word_ids =  torch.tensor([0, 1, 2, 3, 4])
label_ids = torch.tensor([1, 0, 0, 2, 2])
# 0 = O (other), 1 = PERSON, 2 = LOCATION

print("Words: ", words)
print("Labels:", labels)
print()
print("Word IDs: ", word_ids.tolist())
print("Label IDs:", label_ids.tolist())
print()
print("Input: a SEQUENCE of word IDs (length 5)")
print("Output: a SEQUENCE of label IDs (length 5)")
print("Each word gets its own label.")
```

**Expected Output:**
```
Words:  ['John', 'lives', 'in', 'New', 'York']
Labels: ['PERSON', 'O', 'O', 'LOCATION', 'LOCATION']

Word IDs:  [0, 1, 2, 3, 4]
Label IDs: [1, 0, 0, 2, 2]

Input: a SEQUENCE of word IDs (length 5)
Output: a SEQUENCE of label IDs (length 5)
Each word gets its own label.
```

### Other Sequence Task Types

```
+------------------------------------------------------------------+
|               All Sequence Task Types                             |
+------------------------------------------------------------------+
|                                                                   |
|  ONE-TO-SEQUENCE:                                                 |
|    One input --> sequence output                                  |
|    Example: Image captioning (image --> "a cat on a mat")         |
|                                                                   |
|  SEQUENCE-TO-ONE:                                                 |
|    Sequence input --> one output                                  |
|    Example: Sentiment analysis ("great movie" --> positive)       |
|                                                                   |
|  SEQUENCE-TO-SEQUENCE (same length):                              |
|    Sequence input --> sequence output (same length)               |
|    Example: POS tagging (each word --> noun/verb/adjective)       |
|                                                                   |
|  SEQUENCE-TO-SEQUENCE (different length):                         |
|    Sequence input --> sequence output (different length)          |
|    Example: Translation ("I am happy" --> "Je suis content")      |
|                                                                   |
+------------------------------------------------------------------+
```

---

## 17.7 Preparing Sequential Data in PyTorch

Let us put it all together and create a proper sequential dataset that PyTorch can use.

```python
import torch
from torch.utils.data import Dataset, DataLoader

class SequenceDataset(Dataset):
    """A dataset of sequences for next-value prediction."""

    def __init__(self, data, window_size):
        self.data = torch.tensor(data, dtype=torch.float32)
        self.window_size = window_size

    def __len__(self):
        return len(self.data) - self.window_size

    def __getitem__(self, idx):
        x = self.data[idx:idx + self.window_size]
        y = self.data[idx + self.window_size]
        return x, y

# Create some sequential data (sine wave)
import math
sequence = [math.sin(i * 0.1) for i in range(100)]

# Create dataset with window size 5
dataset = SequenceDataset(sequence, window_size=5)
print(f"Total data points: {len(sequence)}")
print(f"Window size: 5")
print(f"Number of training examples: {len(dataset)}")

# Look at a few examples
for i in range(3):
    x, y = dataset[i]
    print(f"\nExample {i+1}:")
    print(f"  Input (5 values):  {[f'{v:.3f}' for v in x.tolist()]}")
    print(f"  Target (next value): {y:.3f}")

# Create a DataLoader for batching
loader = DataLoader(dataset, batch_size=16, shuffle=True)
batch_x, batch_y = next(iter(loader))
print(f"\nBatch shape: X={batch_x.shape}, y={batch_y.shape}")
```

**Expected Output:**
```
Total data points: 100
Window size: 5
Number of training examples: 95

Example 1:
  Input (5 values):  ['0.000', '0.100', '0.199', '0.296', '0.389']
  Target (next value): 0.479

Example 2:
  Input (5 values):  ['0.100', '0.199', '0.296', '0.389', '0.479']
  Target (next value): 0.565

Example 3:
  Input (5 values):  ['0.199', '0.296', '0.389', '0.479', '0.565']
  Target (next value): 0.644

Batch shape: X=torch.Size([16, 5]), y=torch.Size([16])
```

**Line-by-line explanation:**
- **Lines 4-17:** We create a custom Dataset class. The `__init__` method stores the data and window size. The `__len__` method returns how many windows fit. The `__getitem__` method returns one window (input) and the next value (target).
- **Line 21:** We generate a sine wave. This is a smooth, predictable sequence that is good for testing.
- **Line 24:** We create the dataset with a window of 5 values.
- **Lines 30-33:** We look at 3 examples. Each input has 5 consecutive values, and the target is the next value after those 5.
- **Lines 36-38:** We create a DataLoader that groups examples into batches of 16. The batch shape is `[16, 5]` meaning 16 examples, each with 5 values.

---

## 17.8 The Need for Recurrent Architectures

We have seen the problem. Feedforward networks have no memory, and sliding windows have limited context. We need something fundamentally different.

The solution is a **recurrent** architecture. The word **recurrent** means "happening again and again." In a recurrent network, information loops back. The output from one step becomes part of the input for the next step.

```
+------------------------------------------------------------------+
|           The Big Idea: Recurrence                                |
+------------------------------------------------------------------+
|                                                                   |
|  Feedforward (no memory):                                         |
|                                                                   |
|    Input1 --> [Network] --> Output1                                |
|    Input2 --> [Network] --> Output2    (independent)               |
|    Input3 --> [Network] --> Output3                                |
|                                                                   |
|  Recurrent (with memory):                                         |
|                                                                   |
|    Input1 --> [Network] --> Output1                                |
|                  |                                                 |
|                  v  (pass memory forward)                          |
|    Input2 --> [Network] --> Output2                                |
|                  |                                                 |
|                  v  (pass memory forward)                          |
|    Input3 --> [Network] --> Output3                                |
|                                                                   |
|  Each step remembers what happened before.                        |
|                                                                   |
+------------------------------------------------------------------+
```

Think of it like a **relay race**. Each runner carries a baton. When they finish their part, they hand the baton to the next runner. The baton represents the information (memory) passed from one step to the next.

```python
# Conceptual example: a simple recurrent process
# (Not a real neural network - just showing the idea)

sequence = [1, 2, 3, 4, 5]
memory = 0  # Start with no memory

print("Processing a sequence with memory:\n")
for step, value in enumerate(sequence):
    # Combine current input with memory
    new_memory = memory + value
    print(f"Step {step+1}: input={value}, old_memory={memory}, "
          f"new_memory={new_memory}")
    memory = new_memory  # Pass memory to next step

print(f"\nFinal memory: {memory}")
print(f"The memory accumulated information from ALL previous steps.")
print(f"At step 5, the network 'remembers' steps 1, 2, 3, and 4.")
```

**Expected Output:**
```
Processing a sequence with memory:

Step 1: input=1, old_memory=0, new_memory=1
Step 2: input=2, old_memory=1, new_memory=3
Step 3: input=3, old_memory=3, new_memory=6
Step 4: input=4, old_memory=6, new_memory=10
Step 5: input=5, old_memory=10, new_memory=15

Final memory: 15
The memory accumulated information from ALL previous steps.
At step 5, the network 'remembers' steps 1, 2, 3, and 4.
```

**Line-by-line explanation:**
- **Line 4:** Our input sequence has 5 values.
- **Line 5:** We start with a memory of 0. In a real network, this would be a vector of numbers (called the hidden state).
- **Lines 8-13:** For each step, we combine the current input with the old memory to create a new memory. In a real network, this combination uses learned weights instead of simple addition.
- **Line 14:** We update the memory for the next step. This is the key idea: information flows forward through time.

In the next chapter, you will see how this idea becomes a real neural network called a **Recurrent Neural Network (RNN)**.

---

## Common Mistakes

```
+------------------------------------------------------------------+
|                    Common Mistakes                                |
+------------------------------------------------------------------+
|                                                                   |
|  1. Treating sequential data as independent data points           |
|     WRONG:  Shuffle time series data randomly                     |
|     RIGHT:  Keep the time order when creating train/test splits   |
|                                                                   |
|  2. Using a feedforward network for sequences                     |
|     WRONG:  nn.Linear(100, 10) for a sentence of 100 words       |
|     RIGHT:  Use RNN, LSTM, or Transformer (coming in next        |
|             chapters)                                             |
|                                                                   |
|  3. Choosing the wrong window size                                |
|     WRONG:  Window of 2 for data with patterns spanning 50 steps  |
|     RIGHT:  Analyze your data to find the pattern length first    |
|                                                                   |
|  4. Forgetting to normalize sequential data                       |
|     WRONG:  Feed raw stock prices (100, 50000, 3) directly       |
|     RIGHT:  Normalize or standardize values to a similar range    |
|                                                                   |
|  5. Confusing sequence tasks                                      |
|     WRONG:  Using sequence-to-one when you need per-step output  |
|     RIGHT:  Choose the task type that matches your problem        |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Best Practices

```
+------------------------------------------------------------------+
|                    Best Practices                                  |
+------------------------------------------------------------------+
|                                                                   |
|  1. Always preserve time order in your data splits.               |
|     Use earlier data for training and later data for testing.     |
|                                                                   |
|  2. Normalize your sequences before feeding them to a network.    |
|     Subtract the mean and divide by the standard deviation.       |
|                                                                   |
|  3. Start with a simple model (like sliding window) as a          |
|     baseline before trying complex architectures.                 |
|                                                                   |
|  4. Visualize your sequences before building models.              |
|     Plotting helps you see patterns and anomalies.                |
|                                                                   |
|  5. Understand your task type (seq-to-one, seq-to-seq)            |
|     before choosing an architecture.                              |
|                                                                   |
|  6. Pad shorter sequences to match the longest sequence           |
|     in a batch, or use variable-length handling.                  |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Quick Summary

Sequential data is data where order matters. Text, time series, audio, and video are all sequences. Regular feedforward neural networks cannot handle sequences because they have no memory and require fixed-size inputs. The sliding window approach works as a simple baseline but cannot capture long-range patterns. Sequence tasks come in different types: sequence-to-one (like sentiment analysis) and sequence-to-sequence (like translation). To properly handle sequences, we need recurrent architectures that pass information from one step to the next.

---

## Key Points

```
+------------------------------------------------------------------+
|                      Key Points                                    |
+------------------------------------------------------------------+
|                                                                   |
|  - Sequential data: data where ORDER matters                      |
|                                                                   |
|  - Time series: numbers measured at regular time intervals         |
|                                                                   |
|  - Text is a sequence of tokens (words or characters)             |
|                                                                   |
|  - Feedforward networks have no memory and fixed input size        |
|                                                                   |
|  - Sliding window: look at N items at a time (limited context)    |
|                                                                   |
|  - Sequence-to-one: whole sequence --> single output              |
|                                                                   |
|  - Sequence-to-sequence: sequence --> sequence                    |
|                                                                   |
|  - Recurrent idea: pass memory from step to step                  |
|                                                                   |
|  - PyTorch Dataset and DataLoader work for sequences too          |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Practice Questions

1. Give three real-world examples of sequential data that were not mentioned in this chapter. Explain why order matters for each one.

2. You have a dataset of daily stock prices for 5 years (about 1,250 data points). You want to predict tomorrow's price. Would you use a sequence-to-one or sequence-to-sequence approach? Why?

3. A feedforward network with `nn.Linear(10, 5)` can only process inputs of size 10. You have sentences ranging from 3 to 50 words. What are two possible solutions to this problem? What are the downsides of each?

4. You are using a sliding window of size 3 on the sentence "The president of the United States visited France." To predict the word "France," the window sees "States visited ___." Is this enough context? Why or why not?

5. Explain in your own words what "recurrence" means and why it helps with sequential data. Use an analogy from daily life.

---

## Exercises

### Exercise 1: Build a Text Encoder

Create a function that takes a list of sentences, builds a vocabulary, and encodes each sentence as a list of integers. Handle the case where sentences have different lengths by padding shorter sentences with a special `<PAD>` token (index 0).

**Hint:** First find the longest sentence. Then add zeros to shorter sentences until they match that length.

### Exercise 2: Create a Time Series Dataset

Download or create a dataset of 200 data points (you can use a sine wave with some noise added). Create a `SequenceDataset` with a window size of 10. Split it into training (first 150 points) and test (last 50 points) sets. Print the shapes of your training and test tensors.

### Exercise 3: Compare Window Sizes

Using the sine wave data from Exercise 2, create datasets with window sizes of 3, 5, 10, and 20. For each window size, print how many training examples you get and show the first example. Discuss which window size might work best for predicting a sine wave and why.

---

## What Is Next?

Now that you understand the problem of sequential data and why regular neural networks fall short, you are ready for the solution. In the next chapter, you will learn about **Recurrent Neural Networks (RNNs)**. RNNs are neural networks with a loop that allows information to flow from one time step to the next. You will see how a hidden state acts as memory, learn to unroll RNNs through time, and build your first sequence model in PyTorch.
