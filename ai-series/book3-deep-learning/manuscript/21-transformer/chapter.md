# Chapter 21: The Transformer — Attention Is All You Need

## What You Will Learn

- Why the paper "Attention Is All You Need" changed everything in deep learning
- What "no recurrence" means and why parallel processing matters
- How multi-head attention lets the model focus on multiple things at once
- What positional encoding is and why transformers need it
- How feed-forward layers add processing power inside each block
- What layer normalization does and why it stabilizes training
- The complete encoder-decoder architecture of the original Transformer
- Why transformers dominate NLP and are spreading to vision, audio, and beyond
- A full ASCII architecture diagram you can reference anytime

## Why This Chapter Matters

Imagine you are reading a book, but you are only allowed to read one word at a time, and you must finish each word before moving to the next. That is how RNNs and LSTMs work. They process sequences one step at a time, in order. This is slow.

Now imagine you can see the entire page at once. You can read all the words simultaneously and understand how they relate to each other. That is what the Transformer does.

In 2017, researchers at Google published a paper called "Attention Is All You Need." The title made a bold claim: you do not need recurrence (the step-by-step processing of RNNs) at all. You only need attention.

This paper introduced the **Transformer** architecture, and it changed the entire field of artificial intelligence. Every major language model today — GPT, BERT, T5, LLaMA, Claude — is built on the Transformer. It has also spread beyond language to computer vision (Vision Transformer), audio processing (Whisper), protein folding (AlphaFold), and more.

Understanding the Transformer is not optional if you want to work in modern deep learning. It is the foundation of everything.

---

## 21.1 The Problem with Sequential Processing

In previous chapters, we learned about RNNs and LSTMs. These models process sequences one element at a time. The hidden state from step 1 feeds into step 2, which feeds into step 3, and so on.

The word **sequential** means "one after another in order." Sequential processing has two major problems.

**Problem 1: It is slow.** You cannot process step 5 until you have finished steps 1 through 4. This means you cannot take advantage of modern GPUs, which are designed to do many calculations at the same time (in **parallel**).

The word **parallel** means "happening at the same time." A GPU has thousands of small processors. If your computation is sequential, most of those processors sit idle, wasting computing power.

**Problem 2: Long-range dependencies are hard.** If the answer to a question depends on a word that appeared 100 steps ago, the information must survive through 100 sequential steps. Even with LSTMs and their gating mechanisms, information gets diluted over long distances.

```
+------------------------------------------------------------------+
|              Sequential vs Parallel Processing                    |
+------------------------------------------------------------------+
|                                                                   |
|  Sequential (RNN/LSTM):                                           |
|                                                                   |
|  Word1 --> Word2 --> Word3 --> Word4 --> Word5 --> Output          |
|  Step 1    Step 2    Step 3    Step 4    Step 5                    |
|                                                                   |
|  Total time: 5 steps (each must wait for the previous one)        |
|                                                                   |
|  ---------------------------------------------------------------  |
|                                                                   |
|  Parallel (Transformer):                                          |
|                                                                   |
|  Word1 --|                                                        |
|  Word2 --|                                                        |
|  Word3 --|-- All processed simultaneously --> Output              |
|  Word4 --|                                                        |
|  Word5 --|                                                        |
|                                                                   |
|  Total time: 1 step (all words processed at the same time)        |
|                                                                   |
+------------------------------------------------------------------+
```

```python
import time

# Simulating sequential vs parallel processing
def sequential_process(n_words):
    """Process words one at a time"""
    results = []
    for i in range(n_words):
        # Each word takes some time
        result = i * 2  # Simple computation
        results.append(result)
    return results

def parallel_process(n_words):
    """Process all words at once (simulated)"""
    import torch
    words = torch.arange(n_words)
    results = words * 2  # All at once
    return results

# Compare conceptual time
n_words = 1000
print("Sequential processing:")
print(f"  Steps needed: {n_words} (one per word)")
print(f"  Each step must wait for the previous one")
print()

print("Parallel processing (Transformer):")
print(f"  Steps needed: 1 (all words at once)")
print(f"  GPU processes all words simultaneously")
print()

print("Speedup potential: {:.0f}x faster".format(n_words / 1))
```

**Expected Output:**
```
Sequential processing:
  Steps needed: 1000 (one per word)
  Each step must wait for the previous one

Parallel processing (Transformer):
  Steps needed: 1 (all words at once)
  GPU processes all words simultaneously

Speedup potential: 1000x faster
```

The actual speedup depends on hardware and sequence length, but the principle is clear: parallel processing is dramatically faster.

---

## 21.2 The Key Insight: Attention Is All You Need

The authors of the Transformer paper made a revolutionary observation. The attention mechanism we learned about in Chapter 20 can do everything that recurrence does — and more.

Remember how attention works:
1. Every position can look at every other position
2. Attention weights determine how much to focus on each position
3. This creates direct connections between any two positions in the sequence

With attention, a word at position 100 can directly attend to a word at position 1. There is no chain of 99 intermediate steps. The connection is **direct**.

The word **direct** here means "without going through intermediate steps." It is like the difference between passing a message through 99 people in a line versus shouting it directly across the room.

```
+------------------------------------------------------------------+
|              Direct Connections via Attention                     |
+------------------------------------------------------------------+
|                                                                   |
|  RNN: Word1 -> Word2 -> Word3 -> ... -> Word99 -> Word100        |
|       Information must travel through 99 intermediate steps       |
|       Signal gets weaker at each step                             |
|                                                                   |
|  Transformer:                                                     |
|       Word1 <---direct attention---> Word100                      |
|       Word1 <---direct attention---> Word50                       |
|       Word37 <--direct attention---> Word100                      |
|       Every pair of words has a direct connection                 |
|                                                                   |
+------------------------------------------------------------------+
```

```python
import torch

# Demonstrating direct connections
seq_length = 100

# In an RNN: distance between positions
rnn_distance_1_to_100 = 99  # Must pass through 99 steps
rnn_distance_1_to_50 = 49

# In a Transformer: distance between ANY two positions
transformer_distance = 1  # Always direct (one attention step)

print("Distance between position 1 and position 100:")
print(f"  RNN:         {rnn_distance_1_to_100} steps")
print(f"  Transformer: {transformer_distance} step (direct attention)")
print()

print("Distance between position 1 and position 50:")
print(f"  RNN:         {rnn_distance_1_to_50} steps")
print(f"  Transformer: {transformer_distance} step (direct attention)")
print()

# Total number of direct connections in a Transformer
total_connections = seq_length * seq_length
print(f"Total attention connections for {seq_length} words:")
print(f"  {total_connections} direct connections")
print(f"  Every word can attend to every other word")
```

**Expected Output:**
```
Distance between position 1 and position 100:
  RNN:         99 steps
  Transformer: 1 step (direct attention)

Distance between position 1 and position 50:
  RNN:         49 steps
  Transformer: 1 step (direct attention)

Total attention connections for 100 words:
  10000 direct connections
  Every word can attend to every other word
```

---

## 21.3 Self-Attention Refresher

Before we build the full Transformer, let us quickly review **self-attention** from Chapter 20.

In self-attention, every element in a sequence attends to every other element in the **same** sequence. The word **self** means it is looking at itself (its own sequence), not at a different sequence.

Each element creates three vectors:
- **Query (Q):** "What am I looking for?"
- **Key (K):** "What do I contain?"
- **Value (V):** "What information do I provide?"

The attention score between two positions is computed as the dot product of the Query of one position and the Key of another position. The final output is a weighted sum of the Values, where the weights come from the attention scores.

```
+------------------------------------------------------------------+
|              Self-Attention: Every Word Looks at Every Word       |
+------------------------------------------------------------------+
|                                                                   |
|  Input: "The cat sat on the mat"                                  |
|                                                                   |
|  For the word "sat":                                              |
|    Query of "sat" asks: "Who did the sitting? Where?"             |
|                                                                   |
|    Attention to each word:                                        |
|      "The"  -> 0.05  (not very relevant)                          |
|      "cat"  -> 0.40  (who sat? the cat!)                          |
|      "sat"  -> 0.15  (itself)                                     |
|      "on"   -> 0.10  (preposition, somewhat relevant)             |
|      "the"  -> 0.05  (not very relevant)                          |
|      "mat"  -> 0.25  (where? on the mat!)                         |
|                                                                   |
|    Output for "sat" = weighted combination of all word values     |
|                                                                   |
+------------------------------------------------------------------+
```

```python
import torch
import torch.nn.functional as F

# Self-attention step by step
# 4 words, each represented as a 3-dimensional vector
words = ["The", "cat", "sat", "mat"]
# These would normally come from an embedding layer
X = torch.tensor([
    [1.0, 0.0, 1.0],   # "The"
    [0.0, 1.0, 0.0],   # "cat"
    [1.0, 1.0, 0.0],   # "sat"
    [0.0, 0.0, 1.0],   # "mat"
])

d_model = 3  # Dimension of each vector

# In self-attention, Q, K, V all come from the same input
# For simplicity, we use X directly as Q, K, and V
Q = X  # Queries
K = X  # Keys
V = X  # Values

# Step 1: Compute attention scores (Q * K^T)
scores = torch.matmul(Q, K.transpose(0, 1))
print("Raw attention scores:")
print(scores)
print()

# Step 2: Scale by sqrt(d_model)
# This prevents scores from getting too large
scale = d_model ** 0.5
scaled_scores = scores / scale
print(f"Scaled scores (divided by sqrt({d_model}) = {scale:.2f}):")
print(scaled_scores.round(decimals=2))
print()

# Step 3: Apply softmax to get attention weights
weights = F.softmax(scaled_scores, dim=-1)
print("Attention weights (each row sums to 1):")
for i, word in enumerate(words):
    weight_str = " ".join(f"{w:.2f}" for w in weights[i])
    print(f"  {word:4s} attends to [{weight_str}]")
print()

# Step 4: Weighted sum of values
output = torch.matmul(weights, V)
print("Output (new representation for each word):")
for i, word in enumerate(words):
    print(f"  {word}: {output[i].tolist()}")
```

**Expected Output:**
```
Raw attention scores:
tensor([[2., 0., 1., 1.],
        [0., 1., 1., 0.],
        [1., 1., 1., 0.],
        [1., 0., 0., 1.]])

Scaled scores (divided by sqrt(3) = 1.73):
tensor([[1.15, 0.00, 0.58, 0.58],
        [0.00, 0.58, 0.58, 0.00],
        [0.58, 0.58, 0.58, 0.00],
        [0.58, 0.00, 0.00, 0.58]])

Attention weights (each row sums to 1):
  The  attends to [0.39 0.12 0.22 0.22]
  cat  attends to [0.20 0.36 0.36 0.20]
  sat  attends to [0.28 0.28 0.28 0.28]
  mat  attends to [0.36 0.20 0.20 0.36]

Output (new representation for each word):
  The: [0.7226, 0.3437, 0.6126]
  cat: [0.5574, 0.5574, 0.3917]
  sat: [0.5000, 0.5000, 0.5000]
  mat: [0.5574, 0.2509, 0.7180]
```

Each word now has a new representation that incorporates information from all other words, weighted by relevance.

---

## 21.4 Multi-Head Attention

Here is the key innovation: instead of computing attention once, the Transformer computes it **multiple times in parallel**. Each computation is called a **head**, and together they form **multi-head attention**.

The word **head** here is like a "point of view." Each head looks at the relationships between words from a different perspective.

Think of it like a group of detectives investigating a crime scene. One detective focuses on fingerprints, another on footprints, another on witness statements. Each detective (head) focuses on different types of evidence (relationships). Together, they form a much more complete picture than any single detective could.

```
+------------------------------------------------------------------+
|              Multi-Head Attention: Multiple Perspectives          |
+------------------------------------------------------------------+
|                                                                   |
|  Input: "The cat sat on the mat"                                  |
|                                                                   |
|  Head 1 (grammatical relationships):                              |
|    "cat" --> pays attention to --> "sat" (subject-verb)            |
|                                                                   |
|  Head 2 (positional relationships):                               |
|    "sat" --> pays attention to --> "on" (verb-preposition)         |
|                                                                   |
|  Head 3 (semantic relationships):                                 |
|    "cat" --> pays attention to --> "mat" (the cat is on the mat)   |
|                                                                   |
|  Head 4 (article-noun relationships):                             |
|    "The" --> pays attention to --> "cat" (article modifies noun)   |
|                                                                   |
|  All heads combined --> richer understanding of each word         |
|                                                                   |
+------------------------------------------------------------------+
```

How does multi-head attention work technically? The model splits the embedding into multiple smaller pieces, runs attention separately on each piece, and then concatenates the results.

```
+------------------------------------------------------------------+
|              How Multi-Head Attention Splits the Work             |
+------------------------------------------------------------------+
|                                                                   |
|  Input embedding: [d_model = 512]                                 |
|                                                                   |
|  Number of heads: 8                                               |
|  Each head dimension: 512 / 8 = 64                                |
|                                                                   |
|  Head 1: works with dimensions [0:64]                             |
|  Head 2: works with dimensions [64:128]                           |
|  Head 3: works with dimensions [128:192]                          |
|  Head 4: works with dimensions [192:256]                          |
|  Head 5: works with dimensions [256:320]                          |
|  Head 6: works with dimensions [320:384]                          |
|  Head 7: works with dimensions [384:448]                          |
|  Head 8: works with dimensions [448:512]                          |
|                                                                   |
|  Each head independently computes Q, K, V and attention           |
|  Results are concatenated: [64]*8 = [512]                         |
|  Then projected through a linear layer                            |
|                                                                   |
+------------------------------------------------------------------+
```

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

# Multi-head attention demonstration
d_model = 512   # Total embedding dimension
n_heads = 8     # Number of attention heads
d_head = d_model // n_heads  # Dimension per head

print(f"Model dimension (d_model): {d_model}")
print(f"Number of heads: {n_heads}")
print(f"Dimension per head (d_head): {d_head}")
print()

# Simulate input: batch of 1, sequence of 6 words
seq_length = 6
x = torch.randn(1, seq_length, d_model)
print(f"Input shape: {x.shape}")
print(f"  Batch size: {x.shape[0]}")
print(f"  Sequence length: {x.shape[1]}")
print(f"  Embedding dimension: {x.shape[2]}")
print()

# Reshape for multi-head: split d_model into n_heads * d_head
# From: (batch, seq, d_model)
# To:   (batch, n_heads, seq, d_head)
x_reshaped = x.view(1, seq_length, n_heads, d_head)
x_reshaped = x_reshaped.transpose(1, 2)  # Move heads dimension

print(f"After reshaping for multi-head:")
print(f"  Shape: {x_reshaped.shape}")
print(f"  Batch size: {x_reshaped.shape[0]}")
print(f"  Number of heads: {x_reshaped.shape[1]}")
print(f"  Sequence length: {x_reshaped.shape[2]}")
print(f"  Dimension per head: {x_reshaped.shape[3]}")
print()

# Each head can now compute attention independently
# Head 0 gets its own 64-dimensional view
# Head 1 gets a different 64-dimensional view
# ... and so on

for i in range(n_heads):
    head_data = x_reshaped[0, i]  # Shape: (seq_length, d_head)
    print(f"  Head {i}: shape {head_data.shape} "
          f"(processes {seq_length} words, each {d_head}-dim)")
```

**Expected Output:**
```
Model dimension (d_model): 512
Number of heads: 8
Dimension per head (d_head): 64

Input shape: torch.Size([1, 6, 512])
  Batch size: 1
  Sequence length: 6
  Embedding dimension: 512

After reshaping for multi-head:
  Shape: torch.Size([1, 8, 6, 64])
  Batch size: 1
  Number of heads: 8
  Sequence length: 6
  Dimension per head: 64

  Head 0: shape torch.Size([6, 64]) (processes 6 words, each 64-dim)
  Head 1: shape torch.Size([6, 64]) (processes 6 words, each 64-dim)
  Head 2: shape torch.Size([6, 64]) (processes 6 words, each 64-dim)
  Head 3: shape torch.Size([6, 64]) (processes 6 words, each 64-dim)
  Head 4: shape torch.Size([6, 64]) (processes 6 words, each 64-dim)
  Head 5: shape torch.Size([6, 64]) (processes 6 words, each 64-dim)
  Head 6: shape torch.Size([6, 64]) (processes 6 words, each 64-dim)
  Head 7: shape torch.Size([6, 64]) (processes 6 words, each 64-dim)
```

---

## 21.5 Positional Encoding

Here is a problem. Since the Transformer processes all words in parallel (not sequentially), it has no idea what **order** the words are in. The sentence "cat the sat mat on the" would look the same as "the cat sat on the mat" to the Transformer.

This is a critical problem because word order matters enormously in language. "The dog bit the man" means something very different from "The man bit the dog."

The solution is **positional encoding**. We add a special signal to each word's embedding that tells the model where that word is in the sequence. The word **positional** means "related to position" (where something is in the sequence). The word **encoding** means "a way of representing information as numbers."

The original Transformer uses sine and cosine functions to create positional encodings. Why sines and cosines? Because they create unique patterns for each position, and the model can learn to use the differences between these patterns to figure out relative positions.

```
+------------------------------------------------------------------+
|              Why Position Matters                                 |
+------------------------------------------------------------------+
|                                                                   |
|  Without positional encoding:                                     |
|    "dog bites man" and "man bites dog"                            |
|    look IDENTICAL to the Transformer                              |
|    (same words, same embeddings, just different order)            |
|                                                                   |
|  With positional encoding:                                        |
|    "dog  bites  man"                                              |
|     pos0  pos1  pos2   <-- each word gets a position signal       |
|                                                                   |
|    "man  bites  dog"                                              |
|     pos0  pos1  pos2   <-- "man" is now at pos0, "dog" at pos2   |
|                                                                   |
|    Now the Transformer can tell the difference!                   |
|                                                                   |
+------------------------------------------------------------------+
```

```python
import torch
import math
import numpy as np

def positional_encoding(seq_length, d_model):
    """
    Create positional encoding using sine and cosine functions.

    For each position and each dimension:
    - Even dimensions use sin(position / 10000^(2i/d_model))
    - Odd dimensions use cos(position / 10000^(2i/d_model))
    """
    pe = torch.zeros(seq_length, d_model)

    for pos in range(seq_length):
        for i in range(0, d_model, 2):
            # The denominator creates different frequencies
            denominator = 10000 ** (i / d_model)

            pe[pos, i] = math.sin(pos / denominator)      # Even index
            if i + 1 < d_model:
                pe[pos, i + 1] = math.cos(pos / denominator)  # Odd index

    return pe

# Create positional encoding for 10 positions, 8 dimensions
seq_length = 10
d_model = 8
pe = positional_encoding(seq_length, d_model)

print("Positional Encoding (10 positions, 8 dimensions):")
print(f"Shape: {pe.shape}")
print()

# Show first 4 positions
for pos in range(4):
    values = " ".join(f"{v:+.3f}" for v in pe[pos])
    print(f"  Position {pos}: [{values}]")

print()

# Show how position 0 and position 5 are different
print("Difference between Position 0 and Position 5:")
diff = pe[5] - pe[0]
print(f"  {diff.tolist()}")
print()

# Key property: each position has a unique encoding
print("Are all positional encodings unique?")
for i in range(seq_length):
    for j in range(i + 1, seq_length):
        if torch.allclose(pe[i], pe[j]):
            print(f"  Position {i} and {j} are the SAME (problem!)")
            break
    else:
        continue
    break
else:
    print("  Yes! Every position has a unique encoding.")
print()

# How positional encoding is added to word embeddings
word_embedding = torch.randn(1, d_model)  # Some word's embedding
position = 3
combined = word_embedding + pe[position]
print(f"Word embedding:       {word_embedding[0, :4].tolist()}")
print(f"Position {position} encoding:  {pe[position, :4].tolist()}")
print(f"Combined (sum):       {combined[0, :4].tolist()}")
print("(showing first 4 dimensions)")
```

**Expected Output:**
```
Positional Encoding (10 positions, 8 dimensions):
Shape: torch.Size([10, 8])

  Position 0: [+0.000 +1.000 +0.000 +1.000 +0.000 +1.000 +0.000 +1.000]
  Position 1: [+0.841 +0.540 +0.100 +0.995 +0.010 +1.000 +0.001 +1.000]
  Position 2: [+0.909 -0.416 +0.198 +0.980 +0.020 +1.000 +0.002 +1.000]
  Position 3: [+0.141 -0.990 +0.296 +0.955 +0.030 +1.000 +0.003 +1.000]

Difference between Position 0 and Position 5:
  [-0.9589242935180664, -1.2836622, 0.4794255, -0.1143981, 0.04998, -0.00125, 0.005, -0.0000125]

Are all positional encodings unique?
  Yes! Every position has a unique encoding.

Word embedding:       [0.3421, -0.8765, 1.2043, 0.5512]
Position 3 encoding:  [0.1411, -0.9900, 0.2955, 0.9553]
Combined (sum):       [0.4832, -1.8665, 1.4998, 1.5065]
(showing first 4 dimensions)
```

The sine and cosine functions at different frequencies create a unique "fingerprint" for each position. Lower dimensions change slowly (capturing coarse position), while higher dimensions change quickly (capturing fine position).

---

## 21.6 Feed-Forward Network

After the attention layer, each position's output goes through a **feed-forward network** (FFN). This is a simple two-layer neural network applied to each position independently.

The word **feed-forward** means data flows in one direction: input to output, with no loops. This is the same type of network we learned about in the early chapters.

Why do we need this? The attention layer is good at combining information across positions, but it is essentially a weighted average — a linear operation. The feed-forward network adds **non-linearity**, allowing the model to compute more complex functions.

Think of it this way: attention figures out which words are relevant to each other, and the feed-forward network processes that combined information to extract deeper meaning.

```
+------------------------------------------------------------------+
|              Feed-Forward Network in the Transformer              |
+------------------------------------------------------------------+
|                                                                   |
|  For EACH position independently:                                 |
|                                                                   |
|  Input (d_model = 512)                                            |
|       |                                                           |
|       v                                                           |
|  [Linear Layer 1: 512 --> 2048]  (expand)                         |
|       |                                                           |
|       v                                                           |
|  [ReLU Activation]               (non-linearity)                  |
|       |                                                           |
|       v                                                           |
|  [Linear Layer 2: 2048 --> 512]  (compress back)                  |
|       |                                                           |
|       v                                                           |
|  Output (d_model = 512)                                           |
|                                                                   |
|  The inner dimension (2048) is typically 4x the model dimension.  |
|  This "expand then compress" pattern lets the network learn       |
|  complex transformations.                                         |
|                                                                   |
+------------------------------------------------------------------+
```

```python
import torch
import torch.nn as nn

# Feed-forward network as used in Transformer
d_model = 512
d_ff = 2048  # Inner dimension, typically 4 * d_model

# The FFN is two linear layers with ReLU in between
ffn = nn.Sequential(
    nn.Linear(d_model, d_ff),    # Expand: 512 -> 2048
    nn.ReLU(),                    # Non-linearity
    nn.Linear(d_ff, d_model),    # Compress: 2048 -> 512
)

print("Feed-Forward Network:")
print(f"  Input dimension:  {d_model}")
print(f"  Hidden dimension: {d_ff} (4x expansion)")
print(f"  Output dimension: {d_model}")
print()

# Count parameters
total_params = sum(p.numel() for p in ffn.parameters())
print(f"  Total parameters: {total_params:,}")
print(f"    Layer 1: {d_model} * {d_ff} + {d_ff} = {d_model * d_ff + d_ff:,}")
print(f"    Layer 2: {d_ff} * {d_model} + {d_model} = {d_ff * d_model + d_model:,}")
print()

# Apply to a sequence
seq_length = 6
x = torch.randn(1, seq_length, d_model)  # (batch, seq, d_model)
print(f"Input shape:  {x.shape}")

output = ffn(x)  # Applied to each position independently
print(f"Output shape: {output.shape}")
print()

# Key point: same FFN is applied to EVERY position
# But each position is processed INDEPENDENTLY
print("Important: The FFN processes each position independently.")
print("Position 0's output does NOT depend on position 1's input.")
print("This is different from attention, where positions interact.")
```

**Expected Output:**
```
Feed-Forward Network:
  Input dimension:  512
  Hidden dimension: 2048 (4x expansion)
  Output dimension: 512

  Total parameters: 2,099,712
    Layer 1: 512 * 2048 + 2048 = 1,050,624
    Layer 2: 2048 * 512 + 512 = 1,049,088

Input shape:  torch.Size([1, 6, 512])
Output shape: torch.Size([1, 6, 512])

Important: The FFN processes each position independently.
Position 0's output does NOT depend on position 1's input.
This is different from attention, where positions interact.
```

---

## 21.7 Layer Normalization

Training deep neural networks is difficult because the values flowing through the network can become very large or very small. This makes training unstable — the model may not learn at all, or it may learn very slowly.

**Layer normalization** (LayerNorm) solves this by normalizing the values at each layer. The word **normalize** means "to adjust values so they follow a standard pattern." Specifically, LayerNorm adjusts the values so they have a mean of 0 and a standard deviation of 1.

Think of it like adjusting the volume on different speakers. If one speaker is blasting and another is whispering, it is hard to hear the music properly. LayerNorm adjusts all speakers to a comfortable, consistent volume.

```
+------------------------------------------------------------------+
|              Layer Normalization                                  |
+------------------------------------------------------------------+
|                                                                   |
|  Before LayerNorm:                                                |
|    Values: [100.5, -200.3, 0.001, 50.7]                          |
|    Mean: -12.27, Std: 130.2                                      |
|    (Values are all over the place!)                               |
|                                                                   |
|  After LayerNorm:                                                 |
|    Values: [0.87, -1.44, 0.09, 0.48]                             |
|    Mean: ~0, Std: ~1                                              |
|    (Values are nicely centered and scaled)                        |
|                                                                   |
|  LayerNorm also has learnable parameters (gamma and beta)         |
|  that let the model adjust the normalization if needed.           |
|                                                                   |
+------------------------------------------------------------------+
```

```python
import torch
import torch.nn as nn

# Layer normalization demonstration
d_model = 4

# Create a LayerNorm layer
layer_norm = nn.LayerNorm(d_model)

# Input with extreme values
x = torch.tensor([[100.5, -200.3, 0.001, 50.7]])
print(f"Before LayerNorm:")
print(f"  Values: {x[0].tolist()}")
print(f"  Mean:   {x.mean().item():.2f}")
print(f"  Std:    {x.std().item():.2f}")
print()

# Apply LayerNorm
normalized = layer_norm(x)
print(f"After LayerNorm:")
print(f"  Values: {[f'{v:.4f}' for v in normalized[0].tolist()]}")
print(f"  Mean:   {normalized.mean().item():.4f} (close to 0)")
print(f"  Std:    {normalized.std().item():.4f} (close to 1)")
print()

# In a Transformer, LayerNorm is applied after attention
# and after the feed-forward network
print("Where LayerNorm appears in a Transformer block:")
print("  1. After multi-head attention (with residual connection)")
print("  2. After feed-forward network (with residual connection)")
```

**Expected Output:**
```
Before LayerNorm:
  Values: [100.5, -200.3, 0.001, 50.7]
  Mean:   -12.27
  Std:    130.17

After LayerNorm:
  Values: ['0.8660', '-1.4424', '0.0942', '0.4823']
  Mean:   0.0000 (close to 0)
  Std:    1.0000 (close to 1)

Where LayerNorm appears in a Transformer block:
  1. After multi-head attention (with residual connection)
  2. After feed-forward network (with residual connection)
```

---

## 21.8 Residual Connections

The Transformer uses **residual connections** (also called **skip connections**). A residual connection adds the input of a layer directly to its output.

The word **residual** means "what is left over." The idea is that the layer only needs to learn the **difference** (residual) between its input and the desired output, rather than learning the entire transformation from scratch.

Think of it like editing a document. Instead of rewriting the entire document from scratch, you just make corrections (residuals) to the existing text. The original document "skips" directly to the output and your corrections are added on top.

```
+------------------------------------------------------------------+
|              Residual Connection                                  |
+------------------------------------------------------------------+
|                                                                   |
|  Without residual connection:                                     |
|                                                                   |
|    Input --> [Layer] --> Output                                   |
|    The layer must learn the ENTIRE transformation                 |
|                                                                   |
|  With residual connection:                                        |
|                                                                   |
|    Input ---+---> [Layer] ---+---> Output                         |
|             |                |                                    |
|             +--- (add) -----+                                    |
|                                                                   |
|    Output = Input + Layer(Input)                                  |
|    The layer only needs to learn the CHANGE (residual)            |
|                                                                   |
+------------------------------------------------------------------+
```

```python
import torch
import torch.nn as nn

d_model = 512

# Simulating a residual connection
x = torch.randn(1, 6, d_model)  # Input

# Some sub-layer (attention or FFN)
sublayer = nn.Linear(d_model, d_model)
sublayer_output = sublayer(x)

# Without residual: output is just the sublayer output
without_residual = sublayer_output

# With residual: add input to sublayer output
with_residual = x + sublayer_output  # This is the residual connection!

print("Without residual connection:")
print(f"  Output = sublayer(x)")
print(f"  Shape: {without_residual.shape}")
print()

print("With residual connection:")
print(f"  Output = x + sublayer(x)")
print(f"  Shape: {with_residual.shape}")
print()

# In the Transformer, the pattern is:
# output = LayerNorm(x + sublayer(x))
layer_norm = nn.LayerNorm(d_model)
transformer_output = layer_norm(x + sublayer_output)
print("Transformer pattern: LayerNorm(x + sublayer(x))")
print(f"  Shape: {transformer_output.shape}")
print()

print("Benefits of residual connections:")
print("  1. Gradients flow directly through the skip connection")
print("  2. Makes it easier to train very deep networks")
print("  3. The layer only needs to learn the 'correction'")
```

**Expected Output:**
```
Without residual connection:
  Output = sublayer(x)
  Shape: torch.Size([1, 6, 512])

With residual connection:
  Output = x + sublayer(x)
  Shape: torch.Size([1, 6, 512])

Transformer pattern: LayerNorm(x + sublayer(x))
  Shape: torch.Size([1, 6, 512])

Benefits of residual connections:
  1. Gradients flow directly through the skip connection
  2. Makes it easier to train very deep networks
  3. The layer only needs to learn the 'correction'
```

---

## 21.9 The Complete Transformer Block

Now let us put all the pieces together into a single **Transformer block** (also called a Transformer layer). One block consists of:

1. Multi-head self-attention
2. Add & Norm (residual connection + layer normalization)
3. Feed-forward network
4. Add & Norm (residual connection + layer normalization)

The original Transformer stacks 6 of these blocks in both the encoder and the decoder.

```
+------------------------------------------------------------------+
|              One Transformer Encoder Block                        |
+------------------------------------------------------------------+
|                                                                   |
|  Input (seq_length, d_model)                                      |
|       |                                                           |
|       +------+                                                    |
|       |      |                                                    |
|       v      |                                                    |
|  [Multi-Head Self-Attention]                                      |
|       |      |                                                    |
|       v      | (residual connection)                              |
|  [   Add   ]<+                                                    |
|       |                                                           |
|       v                                                           |
|  [Layer Norm]                                                     |
|       |                                                           |
|       +------+                                                    |
|       |      |                                                    |
|       v      |                                                    |
|  [Feed-Forward Network]                                           |
|       |      |                                                    |
|       v      | (residual connection)                              |
|  [   Add   ]<+                                                    |
|       |                                                           |
|       v                                                           |
|  [Layer Norm]                                                     |
|       |                                                           |
|       v                                                           |
|  Output (seq_length, d_model)                                     |
|                                                                   |
|  Note: Input and output have the SAME shape.                      |
|  This means blocks can be stacked on top of each other.           |
|                                                                   |
+------------------------------------------------------------------+
```

```python
import torch
import torch.nn as nn

class TransformerBlock(nn.Module):
    """One Transformer encoder block"""

    def __init__(self, d_model, n_heads, d_ff, dropout=0.1):
        super().__init__()

        # Multi-head self-attention
        self.attention = nn.MultiheadAttention(
            embed_dim=d_model,
            num_heads=n_heads,
            dropout=dropout,
            batch_first=True
        )

        # Feed-forward network
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.ReLU(),
            nn.Linear(d_ff, d_model),
        )

        # Layer normalization (two of them)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)

        # Dropout for regularization
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        # Step 1: Multi-head self-attention with residual + norm
        attn_output, attn_weights = self.attention(x, x, x)
        x = self.norm1(x + self.dropout(attn_output))  # Add & Norm

        # Step 2: Feed-forward with residual + norm
        ffn_output = self.ffn(x)
        x = self.norm2(x + self.dropout(ffn_output))   # Add & Norm

        return x

# Create a Transformer block
d_model = 512
n_heads = 8
d_ff = 2048
block = TransformerBlock(d_model, n_heads, d_ff)

# Test with sample input
batch_size = 2
seq_length = 10
x = torch.randn(batch_size, seq_length, d_model)

print(f"Input shape:  {x.shape}")
output = block(x)
print(f"Output shape: {output.shape}")
print()

# Count parameters in one block
total_params = sum(p.numel() for p in block.parameters())
print(f"Parameters in one Transformer block: {total_params:,}")
print()

# Stack 6 blocks (like the original Transformer)
n_layers = 6
encoder = nn.Sequential(*[
    TransformerBlock(d_model, n_heads, d_ff) for _ in range(n_layers)
])

total_encoder_params = sum(p.numel() for p in encoder.parameters())
print(f"Parameters in {n_layers}-layer encoder: {total_encoder_params:,}")
print(f"  That is {total_encoder_params / 1e6:.1f} million parameters")
```

**Expected Output:**
```
Input shape:  torch.Size([2, 10, 512])
Output shape: torch.Size([2, 10, 512])

Parameters in one Transformer block: 3,152,384
Parameters in 6-layer encoder: 18,914,304
  That is 18.9 million parameters
```

Notice that the input and output have exactly the same shape. This is crucial — it means we can stack as many blocks as we want, each one refining the representations further.

---

## 21.10 The Encoder-Decoder Architecture

The original Transformer has two main parts: an **encoder** and a **decoder**.

The **encoder** reads the input sequence and produces a rich representation of it. The **decoder** uses that representation to generate the output sequence.

For a translation task: the encoder reads English, and the decoder writes French. For a summarization task: the encoder reads the article, and the decoder writes the summary.

The decoder is similar to the encoder but has one extra component: **cross-attention** (also called **encoder-decoder attention**). This layer lets the decoder look at the encoder's output, so it can use information from the input while generating each output word.

The decoder also uses **masked self-attention**. The word **masked** means "hidden" or "blocked." In the decoder, each position can only attend to positions before it (not future positions). This is because when generating text, you cannot look at words you have not generated yet.

```
+------------------------------------------------------------------+
|          Complete Transformer Architecture                        |
+------------------------------------------------------------------+
|                                                                   |
|  INPUT SEQUENCE                    OUTPUT SEQUENCE                |
|  (e.g., English)                   (e.g., French)                 |
|       |                                 |                         |
|       v                                 v                         |
|  [Embedding +                    [Embedding +                     |
|   Positional Encoding]            Positional Encoding]            |
|       |                                 |                         |
|  +-----------+                   +-----------+                    |
|  |  ENCODER  |                   |  DECODER  |                    |
|  |           |                   |           |                    |
|  | +-------+ |                   | +-------+ |                    |
|  | | Self- | |                   | |Masked | |                    |
|  | | Attn  | |                   | | Self- | |                    |
|  | +-------+ |                   | | Attn  | |                    |
|  | | Add & | |                   | +-------+ |                    |
|  | | Norm  | |                   | | Add & | |                    |
|  | +-------+ |                   | | Norm  | |                    |
|  | | Feed- | |     Encoder       | +-------+ |                    |
|  | | Fwd   | |     Output ------>| | Cross | |                    |
|  | +-------+ |        |         | | Attn  | |                    |
|  | | Add & | |        |         | +-------+ |                    |
|  | | Norm  | |        |         | | Add & | |                    |
|  | +-------+ |        |         | | Norm  | |                    |
|  |           |        |         | +-------+ |                    |
|  |  x N=6   |        |         | | Feed- | |                    |
|  |  layers   |        |         | | Fwd   | |                    |
|  |           |        |         | +-------+ |                    |
|  +-----------+        |         | | Add & | |                    |
|                       |         | | Norm  | |                    |
|                       |         | +-------+ |                    |
|                       |         |           |                    |
|                       |         |  x N=6   |                    |
|                       |         |  layers   |                    |
|                       |         |           |                    |
|                       |         +-----------+                    |
|                       |              |                            |
|                       |              v                            |
|                       |         [Linear]                          |
|                       |              |                            |
|                       |              v                            |
|                       |         [Softmax]                         |
|                       |              |                            |
|                       |              v                            |
|                       |         Output Probabilities              |
|                       |         (next word prediction)            |
|                                                                   |
+------------------------------------------------------------------+
```

```python
import torch
import torch.nn as nn

# Overview of the Transformer architecture
print("=" * 60)
print("THE TRANSFORMER ARCHITECTURE")
print("=" * 60)
print()

# Hyperparameters from the original paper
d_model = 512      # Embedding dimension
n_heads = 8        # Number of attention heads
d_ff = 2048        # Feed-forward inner dimension
n_layers = 6       # Number of encoder/decoder layers
vocab_size = 32000  # Vocabulary size
max_seq_len = 512  # Maximum sequence length

print("Original Transformer hyperparameters:")
print(f"  d_model (embedding dimension): {d_model}")
print(f"  n_heads (attention heads):     {n_heads}")
print(f"  d_ff (feed-forward dimension): {d_ff}")
print(f"  n_layers (encoder + decoder):  {n_layers} each")
print(f"  vocab_size:                    {vocab_size:,}")
print(f"  max_seq_len:                   {max_seq_len}")
print()

# Encoder components
print("ENCODER (one block):")
print("  1. Multi-Head Self-Attention")
print("  2. Add & Norm")
print("  3. Feed-Forward Network")
print("  4. Add & Norm")
print()

# Decoder components (extra cross-attention)
print("DECODER (one block):")
print("  1. Masked Multi-Head Self-Attention")
print("  2. Add & Norm")
print("  3. Multi-Head Cross-Attention (attends to encoder output)")
print("  4. Add & Norm")
print("  5. Feed-Forward Network")
print("  6. Add & Norm")
print()

# Total parameter count (approximate)
# Embeddings
embed_params = vocab_size * d_model * 2  # Input + output embeddings
# Attention per layer: 4 * d_model^2 (Q, K, V projections + output projection)
attn_params_per_layer = 4 * d_model * d_model
# FFN per layer: 2 * d_model * d_ff
ffn_params_per_layer = 2 * d_model * d_ff
# Encoder: 6 layers * (attention + ffn)
encoder_params = n_layers * (attn_params_per_layer + ffn_params_per_layer)
# Decoder: 6 layers * (masked attn + cross attn + ffn)
decoder_params = n_layers * (2 * attn_params_per_layer + ffn_params_per_layer)

total = embed_params + encoder_params + decoder_params
print(f"Approximate parameter count:")
print(f"  Embeddings:  {embed_params:>12,}")
print(f"  Encoder:     {encoder_params:>12,}")
print(f"  Decoder:     {decoder_params:>12,}")
print(f"  Total:       {total:>12,}")
print(f"  That is about {total / 1e6:.0f} million parameters")
```

**Expected Output:**
```
============================================================
THE TRANSFORMER ARCHITECTURE
============================================================

Original Transformer hyperparameters:
  d_model (embedding dimension): 512
  n_heads (attention heads):     8
  d_ff (feed-forward dimension): 2048
  n_layers (encoder + decoder):  6 each
  vocab_size:                    32,000
  max_seq_len:                   512

ENCODER (one block):
  1. Multi-Head Self-Attention
  2. Add & Norm
  3. Feed-Forward Network
  4. Add & Norm

DECODER (one block):
  1. Masked Multi-Head Self-Attention
  2. Add & Norm
  3. Multi-Head Cross-Attention (attends to encoder output)
  4. Add & Norm
  5. Feed-Forward Network
  6. Add & Norm

Approximate parameter count:
  Embeddings:    32,768,000
  Encoder:       18,874,368
  Decoder:       25,165,824
  Total:         76,808,192
  That is about 77 million parameters
```

---

## 21.11 Masked Attention in the Decoder

The decoder uses **masked self-attention** to prevent looking at future tokens. When generating a sequence, the model predicts one word at a time. When predicting word 5, it should only see words 1 through 4, not words 5, 6, 7, etc.

The mask is a matrix that sets attention scores to negative infinity for positions that should not be attended to. After applying softmax, negative infinity becomes zero, effectively hiding those positions.

```
+------------------------------------------------------------------+
|              Masked Self-Attention                                |
+------------------------------------------------------------------+
|                                                                   |
|  Generating: "The cat sat on the mat"                             |
|                                                                   |
|  When predicting "sat" (position 3):                              |
|  Can see:    "The" (pos 1), "cat" (pos 2)                        |
|  Cannot see: "on" (pos 4), "the" (pos 5), "mat" (pos 6)          |
|                                                                   |
|  Attention mask (1 = can attend, 0 = blocked):                    |
|                                                                   |
|          The  cat  sat   on  the  mat                             |
|  The  [   1    0    0    0    0    0  ]                            |
|  cat  [   1    1    0    0    0    0  ]                            |
|  sat  [   1    1    1    0    0    0  ]                            |
|  on   [   1    1    1    1    0    0  ]                            |
|  the  [   1    1    1    1    1    0  ]                            |
|  mat  [   1    1    1    1    1    1  ]                            |
|                                                                   |
|  This is called a "causal mask" or "look-ahead mask"              |
|                                                                   |
+------------------------------------------------------------------+
```

```python
import torch
import torch.nn.functional as F

# Creating a causal mask for the decoder
seq_length = 6
words = ["The", "cat", "sat", "on", "the", "mat"]

# Create mask: upper triangle is True (positions to BLOCK)
mask = torch.triu(torch.ones(seq_length, seq_length), diagonal=1).bool()

print("Causal mask (True = BLOCKED):")
print(mask.int())
print()

# Show which words each position can attend to
for i, word in enumerate(words):
    visible = [words[j] for j in range(seq_length) if not mask[i][j]]
    blocked = [words[j] for j in range(seq_length) if mask[i][j]]
    print(f"  '{word}' can see: {visible}")
    if blocked:
        print(f"         blocked: {blocked}")
    print()

# How the mask is applied to attention scores
# Random attention scores for demonstration
scores = torch.randn(seq_length, seq_length)
print("Raw attention scores (before masking):")
print(scores.round(decimals=2))
print()

# Apply mask: set blocked positions to -infinity
masked_scores = scores.masked_fill(mask, float('-inf'))
print("After masking (blocked positions = -inf):")
# Replace -inf with '-inf' for display
for i in range(seq_length):
    row = []
    for j in range(seq_length):
        if masked_scores[i][j] == float('-inf'):
            row.append("  -inf")
        else:
            row.append(f"{masked_scores[i][j]:6.2f}")
    print(f"  [{', '.join(row)}]")
print()

# After softmax, -inf becomes 0
weights = F.softmax(masked_scores, dim=-1)
print("After softmax (blocked positions become 0):")
print(weights.round(decimals=3))
print("Each row sums to 1, but only over allowed positions")
```

**Expected Output:**
```
Causal mask (True = BLOCKED):
tensor([[0, 1, 1, 1, 1, 1],
        [0, 0, 1, 1, 1, 1],
        [0, 0, 0, 1, 1, 1],
        [0, 0, 0, 0, 1, 1],
        [0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0]])

  'The' can see: ['The']
         blocked: ['cat', 'sat', 'on', 'the', 'mat']

  'cat' can see: ['The', 'cat']
         blocked: ['sat', 'on', 'the', 'mat']

  'sat' can see: ['The', 'cat', 'sat']
         blocked: ['on', 'the', 'mat']

  'on' can see: ['The', 'cat', 'sat', 'on']
         blocked: ['the', 'mat']

  'the' can see: ['The', 'cat', 'sat', 'on', 'the']
         blocked: ['mat']

  'mat' can see: ['The', 'cat', 'sat', 'on', 'the', 'mat']

Raw attention scores (before masking):
tensor([[ 0.12, -0.43,  1.02,  0.55, -0.87,  0.23],
        [-0.31,  0.76,  0.44, -0.18,  0.92, -0.56],
        ...])

After masking (blocked positions = -inf):
  [  0.12,   -inf,   -inf,   -inf,   -inf,   -inf]
  [ -0.31,   0.76,   -inf,   -inf,   -inf,   -inf]
  ...

After softmax (blocked positions become 0):
tensor([[1.000, 0.000, 0.000, 0.000, 0.000, 0.000],
        [0.255, 0.745, 0.000, 0.000, 0.000, 0.000],
        ...])
Each row sums to 1, but only over allowed positions
```

---

## 21.12 Why Transformers Dominate

The Transformer has become the dominant architecture in deep learning for several reasons.

```
+------------------------------------------------------------------+
|              Why Transformers Won                                 |
+------------------------------------------------------------------+
|                                                                   |
|  1. PARALLELISM                                                   |
|     - All positions processed simultaneously                     |
|     - Takes full advantage of GPU hardware                        |
|     - Training is much faster than RNNs                           |
|                                                                   |
|  2. LONG-RANGE DEPENDENCIES                                      |
|     - Direct connections between any two positions                |
|     - No information loss over distance                           |
|     - Attention scores show exactly what the model focuses on     |
|                                                                   |
|  3. SCALABILITY                                                   |
|     - Can scale to billions of parameters                         |
|     - Performance improves with more data and compute             |
|     - Stacking more layers gives better results                   |
|                                                                   |
|  4. FLEXIBILITY                                                   |
|     - Works for text, images, audio, video, proteins, ...         |
|     - Same architecture, different data                           |
|     - Transfer learning works extremely well                      |
|                                                                   |
|  5. INTERPRETABILITY                                              |
|     - Attention weights show what the model "looks at"            |
|     - Easier to debug than RNN hidden states                      |
|     - Multi-head attention reveals different patterns             |
|                                                                   |
+------------------------------------------------------------------+
```

```python
# Comparison: Transformer vs RNN/LSTM
print("=" * 60)
print("TRANSFORMER vs RNN/LSTM COMPARISON")
print("=" * 60)
print()

comparisons = [
    ("Processing", "Parallel", "Sequential"),
    ("Long-range dependencies", "Direct (1 step)", "Indirect (N steps)"),
    ("Training speed", "Fast (GPU-friendly)", "Slow (hard to parallelize)"),
    ("Maximum sequence length", "Thousands of tokens", "Hundreds (practical)"),
    ("Scalability", "Billions of parameters", "Millions (practical)"),
    ("Memory (inference)", "O(n^2) for attention", "O(1) per step"),
    ("Interpretability", "Attention weights", "Hidden states (opaque)"),
]

print(f"{'Feature':<28} {'Transformer':<25} {'RNN/LSTM':<25}")
print("-" * 78)
for feature, transformer, rnn in comparisons:
    print(f"{feature:<28} {transformer:<25} {rnn:<25}")

print()
print("Note: Transformers do have a weakness!")
print("  Attention is O(n^2) in sequence length.")
print("  For 1000 tokens: 1,000,000 attention computations.")
print("  For 10000 tokens: 100,000,000 attention computations.")
print("  This is why researchers are working on efficient attention.")

# Models built on the Transformer
print()
print("Major models built on the Transformer:")
print("  - GPT (Generative Pre-trained Transformer): decoder-only")
print("  - BERT (Bidirectional Encoder Representations): encoder-only")
print("  - T5 (Text-to-Text Transfer Transformer): encoder-decoder")
print("  - Vision Transformer (ViT): images as patches")
print("  - Whisper: audio to text")
print("  - AlphaFold: protein structure prediction")
print("  - DALL-E: text to images")
```

**Expected Output:**
```
============================================================
TRANSFORMER vs RNN/LSTM COMPARISON
============================================================

Feature                      Transformer               RNN/LSTM
------------------------------------------------------------------------------
Processing                   Parallel                  Sequential
Long-range dependencies      Direct (1 step)           Indirect (N steps)
Training speed               Fast (GPU-friendly)       Slow (hard to parallelize)
Maximum sequence length      Thousands of tokens       Hundreds (practical)
Scalability                  Billions of parameters    Millions (practical)
Memory (inference)           O(n^2) for attention      O(1) per step
Interpretability             Attention weights         Hidden states (opaque)

Note: Transformers do have a weakness!
  Attention is O(n^2) in sequence length.
  For 1000 tokens: 1,000,000 attention computations.
  For 10000 tokens: 100,000,000 attention computations.
  This is why researchers are working on efficient attention.

Major models built on the Transformer:
  - GPT (Generative Pre-trained Transformer): decoder-only
  - BERT (Bidirectional Encoder Representations): encoder-only
  - T5 (Text-to-Text Transfer Transformer): encoder-decoder
  - Vision Transformer (ViT): images as patches
  - Whisper: audio to text
  - AlphaFold: protein structure prediction
  - DALL-E: text to images
```

---

## 21.13 The Three Transformer Variants

Since the original Transformer paper, three main variants have emerged. Each variant uses a different part of the original architecture.

```
+------------------------------------------------------------------+
|              Three Transformer Variants                           |
+------------------------------------------------------------------+
|                                                                   |
|  1. ENCODER-ONLY (e.g., BERT)                                    |
|     - Uses only the encoder                                       |
|     - Bidirectional: each position sees ALL other positions       |
|     - Best for: classification, NER, sentence embeddings          |
|     - "Understanding" tasks                                       |
|                                                                   |
|  2. DECODER-ONLY (e.g., GPT)                                     |
|     - Uses only the decoder                                       |
|     - Causal: each position only sees PREVIOUS positions          |
|     - Best for: text generation, chatbots, code generation        |
|     - "Generation" tasks                                          |
|                                                                   |
|  3. ENCODER-DECODER (e.g., T5, original Transformer)             |
|     - Uses both encoder and decoder                               |
|     - Encoder reads input, decoder generates output               |
|     - Best for: translation, summarization, question answering    |
|     - "Transformation" tasks (input -> output)                    |
|                                                                   |
+------------------------------------------------------------------+
```

```python
print("Transformer Variants and Their Uses")
print("=" * 50)
print()

variants = {
    "Encoder-Only": {
        "examples": ["BERT", "RoBERTa", "DistilBERT"],
        "attention": "Bidirectional (sees everything)",
        "tasks": [
            "Text classification",
            "Named entity recognition",
            "Sentence similarity",
            "Feature extraction",
        ],
        "analogy": "A reader who sees the whole book at once",
    },
    "Decoder-Only": {
        "examples": ["GPT-2", "GPT-3/4", "LLaMA"],
        "attention": "Causal (sees only past)",
        "tasks": [
            "Text generation",
            "Chatbots",
            "Code generation",
            "Story writing",
        ],
        "analogy": "A writer who writes word by word",
    },
    "Encoder-Decoder": {
        "examples": ["T5", "BART", "mBART"],
        "attention": "Encoder: bidirectional, Decoder: causal + cross",
        "tasks": [
            "Translation",
            "Summarization",
            "Question answering",
            "Data-to-text generation",
        ],
        "analogy": "A translator who reads then writes",
    },
}

for variant, info in variants.items():
    print(f"{variant}")
    print(f"  Examples: {', '.join(info['examples'])}")
    print(f"  Attention: {info['attention']}")
    print(f"  Best for:")
    for task in info['tasks']:
        print(f"    - {task}")
    print(f"  Analogy: {info['analogy']}")
    print()
```

**Expected Output:**
```
Transformer Variants and Their Uses
==================================================

Encoder-Only
  Examples: BERT, RoBERTa, DistilBERT
  Attention: Bidirectional (sees everything)
  Best for:
    - Text classification
    - Named entity recognition
    - Sentence similarity
    - Feature extraction
  Analogy: A reader who sees the whole book at once

Decoder-Only
  Examples: GPT-2, GPT-3/4, LLaMA
  Attention: Causal (sees only past)
  Best for:
    - Text generation
    - Chatbots
    - Code generation
    - Story writing
  Analogy: A writer who writes word by word

Encoder-Decoder
  Examples: T5, BART, mBART
  Attention: Encoder: bidirectional, Decoder: causal + cross
  Best for:
    - Translation
    - Summarization
    - Question answering
    - Data-to-text generation
  Analogy: A translator who reads then writes
```

---

## Common Mistakes

1. **Confusing self-attention with cross-attention.** Self-attention is when a sequence looks at itself. Cross-attention is when one sequence (the decoder) looks at a different sequence (the encoder output). Both use Q, K, V, but the sources are different.

2. **Forgetting positional encoding.** Without positional encoding, the Transformer cannot distinguish word order. "Dog bites man" and "Man bites dog" would look identical. Always add positional encoding to your input embeddings.

3. **Thinking transformers are always better.** For very short sequences or when you have limited data, simpler models like LSTMs might work just as well or even better. Transformers shine with large data and long sequences.

4. **Ignoring the O(n^2) cost.** Self-attention computes scores between every pair of positions. For a sequence of length 1000, that is 1,000,000 score computations. For length 10,000, that is 100,000,000. Very long sequences require special techniques (efficient attention, chunking).

5. **Confusing the number of heads with the model dimension.** The total dimension stays the same — multi-head attention just divides it into smaller pieces. More heads does not mean a bigger model; it means the same capacity is split into more specialized sub-spaces.

---

## Best Practices

1. **Start with pre-trained models.** Training a Transformer from scratch requires massive amounts of data and compute. For most tasks, start with a pre-trained model and fine-tune it.

2. **Choose the right variant.** Use encoder-only for understanding tasks (classification), decoder-only for generation tasks, and encoder-decoder for sequence-to-sequence tasks (translation, summarization).

3. **Use warmup for learning rate.** The original Transformer paper uses a learning rate schedule with a warmup period. This helps stabilize training in the early stages.

4. **Pay attention to sequence length.** Remember the quadratic cost. If your sequences are very long, consider techniques like sliding window attention, sparse attention, or chunking.

5. **Monitor attention weights.** Visualizing what each head attends to can help you understand and debug your model. Some heads may learn grammar, others may learn coreference, and some may not learn anything useful.

---

## Quick Summary

The Transformer is a neural network architecture that processes sequences entirely through attention, without any recurrence. It was introduced in the 2017 paper "Attention Is All You Need" and has become the foundation of modern deep learning.

Key components:
- **Self-attention:** Every position attends to every other position, creating direct connections
- **Multi-head attention:** Multiple attention computations in parallel, each learning different patterns
- **Positional encoding:** Sine/cosine signals added to embeddings to encode word order
- **Feed-forward network:** Two-layer network applied independently to each position
- **Layer normalization:** Normalizes values to stabilize training
- **Residual connections:** Skip connections that add input directly to output

The architecture has two main parts (encoder and decoder), and three variants have emerged: encoder-only (BERT), decoder-only (GPT), and encoder-decoder (T5).

---

## Key Points

- The Transformer eliminates recurrence, enabling full parallel processing of sequences
- Self-attention creates direct connections between any two positions, solving the long-range dependency problem
- Multi-head attention computes attention from multiple perspectives simultaneously
- Positional encoding uses sine and cosine functions to inject word order information
- Each Transformer block has self-attention, feed-forward network, layer normalization, and residual connections
- The encoder reads the input; the decoder generates the output using masked attention and cross-attention
- Transformers scale to billions of parameters and dominate virtually all areas of deep learning
- The O(n^2) attention cost is the main limitation for very long sequences

---

## Practice Questions

1. Why does the Transformer not need recurrence? What mechanism replaces it, and what advantage does this give?

2. If you have a Transformer with d_model=256 and 4 attention heads, what is the dimension that each head works with? Why does the total dimension stay the same?

3. Why does the decoder use masked self-attention? What would happen if the decoder could see future tokens during training?

4. Explain the purpose of positional encoding. Why can the Transformer not figure out word order without it?

5. What is the difference between self-attention and cross-attention? In which part of the Transformer does each appear?

---

## Exercises

**Exercise 1: Mask Creation**
Write a function that creates a causal mask for a sequence of any length. The mask should be True for positions that should be blocked (future positions) and False for positions that should be visible. Test it with sequences of length 4, 8, and 12. Verify that the first row has all True except the first position, and the last row has all False.

**Exercise 2: Positional Encoding Visualization**
Create a positional encoding for 50 positions with dimension 16. Print the encoding values for positions 0, 25, and 49. Verify that each position has a unique encoding by computing the pairwise distances between all positions. Which two positions are most similar? Which two are most different?

**Exercise 3: Parameter Counting**
Calculate the total number of parameters in a Transformer with the following specifications: d_model=256, n_heads=4, d_ff=1024, n_layers=4 (encoder only), vocab_size=10000. Break down the count by component: embeddings, attention layers (Q, K, V, and output projections), feed-forward layers, and layer normalization.

---

## What Is Next?

Now that you understand the Transformer architecture conceptually, it is time to build one in PyTorch. In Chapter 22, we will implement self-attention from scratch, build multi-head attention, add positional encoding, and use PyTorch's built-in Transformer modules for a complete text classification example. You will see every tensor shape at every step and compare the Transformer's performance against the LSTM from earlier chapters.
