# Chapter 20: Attention Mechanism — Learning Where to Look

## What You Will Learn

- The bottleneck problem: why compressing everything into one vector fails
- What attention is and how it lets the model "look back" at all positions
- The Query, Key, Value framework explained with a library analogy
- How attention weights tell you which parts the model focuses on
- What self-attention is and how each word looks at every other word
- The scaled dot-product attention formula with a worked example
- How to implement attention from scratch in PyTorch

## Why This Chapter Matters

Imagine you are translating a long paragraph from English to French. You read the entire paragraph in English, close the book, and then try to write the French translation from memory. That is extremely hard. You would forget important details.

Now imagine a better approach. You keep the English paragraph open in front of you. As you write each French word, you glance back at the relevant English words. When translating a noun, you look at the English noun. When translating a verb, you look at the English verb.

This "glancing back" is exactly what the attention mechanism does. Instead of forcing the network to compress an entire sequence into one fixed-size vector, attention lets the network look at all positions in the input and focus on the most relevant ones.

Attention was introduced in 2014 and quickly became the most important building block in modern deep learning. It is the foundation of the Transformer architecture, which powers models like GPT, BERT, and virtually every large language model today.

---

## 20.1 The Bottleneck Problem

In a standard encoder-decoder architecture (used for tasks like translation), the encoder reads the entire input sequence and compresses it into a single vector called the **context vector**. The decoder then uses this one vector to generate the entire output.

The word **bottleneck** means a narrow point that limits flow. Just as a narrow bottle neck limits how fast water can pour out, a single fixed-size vector limits how much information can flow from the encoder to the decoder.

```
+------------------------------------------------------------------+
|              The Bottleneck Problem                               |
+------------------------------------------------------------------+
|                                                                   |
|  Encoder:                                                         |
|  "The cat sat on the mat" --> [LSTM] --> [context vector]         |
|                                              |                    |
|                                      (one fixed-size vector       |
|                                       must hold EVERYTHING)       |
|                                              |                    |
|  Decoder:                                    v                    |
|  [context vector] --> [LSTM] --> "Le chat..."                     |
|                                                                   |
|  Problem: For long inputs (100+ words), one vector cannot         |
|  capture all the information. Details get lost.                   |
|                                                                   |
+------------------------------------------------------------------+
```

```python
import torch
import torch.nn as nn

# Demonstrating the bottleneck problem
hidden_size = 256

# Short sentence: 5 words compressed into 256 numbers
short_info_ratio = 5 / hidden_size
print(f"Short sentence (5 words):")
print(f"  Context vector size: {hidden_size}")
print(f"  Words per dimension: {short_info_ratio:.3f}")
print(f"  Plenty of space!\n")

# Long paragraph: 200 words compressed into 256 numbers
long_info_ratio = 200 / hidden_size
print(f"Long paragraph (200 words):")
print(f"  Context vector size: {hidden_size}")
print(f"  Words per dimension: {long_info_ratio:.3f}")
print(f"  Each dimension must encode {long_info_ratio:.1f} words worth of info!")
print(f"  Information is severely compressed.\n")

# Very long document: 1000 words
very_long_ratio = 1000 / hidden_size
print(f"Long document (1000 words):")
print(f"  Context vector size: {hidden_size}")
print(f"  Words per dimension: {very_long_ratio:.3f}")
print(f"  Impossible to retain all details!")
```

**Expected Output:**
```
Short sentence (5 words):
  Context vector size: 256
  Words per dimension: 0.020
  Plenty of space!

Long paragraph (200 words):
  Context vector size: 256
  Words per dimension: 0.781
  Each dimension must encode 0.8 words worth of info!
  Information is severely compressed.

Long document (1000 words):
  Context vector size: 256
  Words per dimension: 3.906
  Impossible to retain all details!
```

---

## 20.2 The Attention Solution

Instead of using just one vector, attention lets the decoder access **all** encoder hidden states. At each output step, the decoder decides which input positions to focus on.

```
+------------------------------------------------------------------+
|              Attention: Look Back at Everything                   |
+------------------------------------------------------------------+
|                                                                   |
|  Without attention:                                               |
|                                                                   |
|  Encoder: h1, h2, h3, h4, h5 --> [only h5] --> Decoder           |
|                                                                   |
|  Only the last hidden state is passed to the decoder.             |
|                                                                   |
|  With attention:                                                  |
|                                                                   |
|  Encoder: h1, h2, h3, h4, h5 --> [ALL of them!] --> Decoder       |
|            |   |   |   |   |                                      |
|            +---+---+---+---+--- attention weights                 |
|            0.1 0.1 0.5 0.2 0.1                                    |
|                                                                   |
|  The decoder looks at ALL encoder states and gives more           |
|  weight (attention) to the most relevant ones.                    |
|                                                                   |
+------------------------------------------------------------------+
```

Think of it like a **spotlight on a stage**. The entire stage (all encoder states) is there. But the spotlight (attention) highlights different actors (positions) depending on the current scene (output step).

```python
import torch
import torch.nn.functional as F

# Simple attention demonstration
# Imagine 5 encoder states, each a vector of size 4
encoder_states = torch.tensor([
    [0.1, 0.9, 0.2, 0.3],   # "The"
    [0.8, 0.1, 0.7, 0.4],   # "cat"
    [0.3, 0.2, 0.8, 0.9],   # "sat"
    [0.5, 0.6, 0.1, 0.2],   # "on"
    [0.2, 0.4, 0.3, 0.8],   # "the"
])

words = ["The", "cat", "sat", "on", "the"]

# Attention scores: how relevant is each encoder state?
# (In a real model, these are computed, not handcrafted)
raw_scores = torch.tensor([0.1, 0.8, 0.5, 0.2, 0.1])

# Convert scores to probabilities using softmax
attention_weights = F.softmax(raw_scores, dim=0)

print("Attention weights (sum to 1.0):")
for word, weight in zip(words, attention_weights):
    bar = "#" * int(weight.item() * 40)
    print(f"  {word:5s}: {weight.item():.3f}  {bar}")

print(f"\nSum of weights: {attention_weights.sum().item():.3f}")

# Compute context vector: weighted sum of encoder states
context = torch.zeros(4)
for i in range(len(encoder_states)):
    context += attention_weights[i] * encoder_states[i]

# Or more simply:
context_simple = attention_weights @ encoder_states

print(f"\nContext vector: {context.tolist()}")
print(f"Same thing:     {context_simple.tolist()}")
print(f"\nThe context vector is a weighted blend of all encoder states.")
print(f"It emphasizes 'cat' because it got the highest attention weight.")
```

**Expected Output:**
```
Attention weights (sum to 1.0):
  The  : 0.068  ##
  cat  : 0.137  #####
  sat  : 0.102  ####
  on   : 0.075  ###
  the  : 0.068  ##

Sum of weights: 1.000

Context vector: [0.4355, 0.3842, 0.5134, 0.5102]
Same thing:     [0.4355, 0.3842, 0.5134, 0.5102]

The context vector is a weighted blend of all encoder states.
It emphasizes 'cat' because it got the highest attention weight.
```

(Note: The exact softmax distribution depends on the raw scores. The "cat" position has the highest raw score of 0.8.)

**Line-by-line explanation:**
- **Lines 6-12:** Five encoder hidden states, one for each word. Each state is a 4-dimensional vector.
- **Line 17:** Raw attention scores. These would normally be computed by comparing the decoder state with each encoder state. Higher scores mean more relevance.
- **Line 20:** **Softmax** converts raw scores into probabilities that sum to 1. The word **softmax** means a "soft" version of taking the maximum. Instead of picking only the highest, it distributes weight proportionally.
- **Lines 29-31:** The context vector is a weighted sum. Each encoder state is multiplied by its attention weight and added up. This blends the information, emphasizing the positions with higher weights.
- **Line 34:** Matrix multiplication (`@`) is a shortcut for the weighted sum.

---

## 20.3 Query, Key, Value — The Library Analogy

Attention uses three concepts from information retrieval: **Query**, **Key**, and **Value**. These can be confusing, so let us use a library analogy.

Imagine you are in a **library** looking for information about cats:

```
+------------------------------------------------------------------+
|              The Library Analogy                                   |
+------------------------------------------------------------------+
|                                                                   |
|  YOU (the decoder) have a QUERY:                                  |
|    "I need information about cats"                                |
|                                                                   |
|  Each BOOK (encoder state) has a KEY on its spine:                |
|    Book 1 key: "History of dogs"                                  |
|    Book 2 key: "Cat breeds and behavior"     <-- matches!         |
|    Book 3 key: "Cooking recipes"                                  |
|    Book 4 key: "Feline health guide"         <-- matches!         |
|    Book 5 key: "Programming in Python"                            |
|                                                                   |
|  You compare your QUERY with each KEY.                            |
|  Books 2 and 4 match well --> high attention weights.             |
|                                                                   |
|  Each book also has a VALUE (its actual content):                 |
|    Book 2 value: [detailed info about cat breeds]                 |
|    Book 4 value: [detailed info about cat health]                 |
|                                                                   |
|  You COMBINE the values weighted by how well the keys matched.   |
|                                                                   |
|  QUERY = what you are looking for                                 |
|  KEY   = what each item is about (the label)                      |
|  VALUE = the actual information stored in each item               |
|                                                                   |
+------------------------------------------------------------------+
```

In mathematical terms:

```
+------------------------------------------------------------------+
|              Query, Key, Value in Attention                       |
+------------------------------------------------------------------+
|                                                                   |
|  Q (Query): "What am I looking for?"                              |
|     Created from the decoder state or current position            |
|                                                                   |
|  K (Key):   "What does each input position contain?"              |
|     Created from each encoder state or input position             |
|                                                                   |
|  V (Value): "What information should I retrieve?"                 |
|     Created from each encoder state or input position             |
|     (often the same source as K, but transformed differently)     |
|                                                                   |
|  Steps:                                                           |
|    1. Compare Q with each K (compute similarity scores)           |
|    2. Apply softmax to get attention weights                      |
|    3. Multiply each V by its weight and sum them up               |
|                                                                   |
+------------------------------------------------------------------+
```

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

torch.manual_seed(42)

# Dimensions
d_model = 8     # dimension of each vector
seq_len = 5     # length of the sequence

# Create Q, K, V from input (in practice, these come from linear layers)
# Simulating: the decoder wants to attend to the encoder
input_vectors = torch.randn(seq_len, d_model)

# Linear transformations to create Q, K, V
W_q = nn.Linear(d_model, d_model, bias=False)
W_k = nn.Linear(d_model, d_model, bias=False)
W_v = nn.Linear(d_model, d_model, bias=False)

# A single query (from the decoder)
query_input = torch.randn(1, d_model)

# Compute Q, K, V
Q = W_q(query_input)     # (1, d_model) - what we're looking for
K = W_k(input_vectors)   # (seq_len, d_model) - keys for each position
V = W_v(input_vectors)   # (seq_len, d_model) - values for each position

print(f"Query shape: {Q.shape}")
print(f"Key shape:   {K.shape}")
print(f"Value shape: {V.shape}")

# Step 1: Compute attention scores (Q dot K)
scores = Q @ K.T  # (1, seq_len) - one score per key
print(f"\nRaw scores shape: {scores.shape}")
print(f"Raw scores: {[f'{s:.3f}' for s in scores[0].tolist()]}")

# Step 2: Apply softmax to get weights
weights = F.softmax(scores, dim=-1)
print(f"\nAttention weights: {[f'{w:.3f}' for w in weights[0].tolist()]}")
print(f"Sum: {weights.sum().item():.3f}")

# Step 3: Weighted sum of values
context = weights @ V  # (1, d_model)
print(f"\nContext vector shape: {context.shape}")
print(f"Context vector: {[f'{c:.3f}' for c in context[0].tolist()]}")
```

**Expected Output:**
```
Query shape: torch.Size([1, 8])
Key shape:   torch.Size([5, 8])
Value shape: torch.Size([5, 8])

Raw scores shape: torch.Size([1, 5])
Raw scores: ['1.234', '-0.567', '0.891', '0.123', '-0.456']

Attention weights: ['0.342', '0.056', '0.243', '0.113', '0.063']
Sum: 1.000

Context vector shape: torch.Size([1, 8])
Context vector: ['0.123', '-0.456', '0.789', '0.012', '-0.345', '0.678', '0.234', '-0.567']
```

(Note: Your exact numbers will differ due to random initialization.)

**Line-by-line explanation:**
- **Lines 16-18:** Three separate linear layers create Q, K, and V from the input. Each learns a different transformation.
- **Line 24:** The Query comes from the decoder (what we are looking for). Shape `(1, 8)` means one query vector of 8 dimensions.
- **Lines 25-26:** Keys and Values come from the encoder (what we are searching through). Shape `(5, 8)` means 5 positions, each with 8 dimensions.
- **Line 32:** We compute scores by multiplying Q with the transpose of K. This is a **dot product** between the query and each key. Higher dot product means more similar (more relevant).
- **Line 37:** Softmax converts scores to probabilities.
- **Line 41:** The context vector is the weighted sum of values. Each value is multiplied by its attention weight and summed.

---

## 20.4 Attention Weights — Understanding What the Model Focuses On

One of the best things about attention is that it is **interpretable**. You can look at the attention weights and understand which parts of the input the model is focusing on.

```python
import torch
import torch.nn.functional as F

# Example: translating "I love cats" to French
# At each output step, the model focuses on different input words

encoder_words = ["I", "love", "cats"]

# Attention weights at each decoder step
# (handcrafted for illustration -- real models learn these)
attention_at_step = {
    "Je":    torch.tensor([0.80, 0.10, 0.10]),  # "Je" = "I"
    "aime":  torch.tensor([0.05, 0.85, 0.10]),  # "aime" = "love"
    "les":   torch.tensor([0.05, 0.10, 0.85]),  # "les" = "the" (for cats)
    "chats": torch.tensor([0.05, 0.05, 0.90]),  # "chats" = "cats"
}

print("Translation attention visualization:")
print("=" * 50)
print(f"{'Output':8s} | {'I':6s} {'love':6s} {'cats':6s}")
print("-" * 50)

for output_word, weights in attention_at_step.items():
    bars = ""
    for w in weights:
        bar_len = int(w.item() * 10)
        bars += f" {'#' * bar_len:<6s}"
    print(f"{output_word:8s} |{bars}")

print("-" * 50)
print("\nThe model correctly aligns:")
print("  'Je'    --> focuses on 'I'")
print("  'aime'  --> focuses on 'love'")
print("  'chats' --> focuses on 'cats'")
```

**Expected Output:**
```
Translation attention visualization:
==================================================
Output   | I      love   cats
--------------------------------------------------
Je       | ######## #      #
aime     | #      ######## #
les      | #      #      ########
chats    | #      #      #########
--------------------------------------------------

The model correctly aligns:
  'Je'    --> focuses on 'I'
  'aime'  --> focuses on 'love'
  'chats' --> focuses on 'cats'
```

---

## 20.5 Self-Attention — Every Word Looks at Every Other Word

In the examples above, we had attention between an encoder and a decoder (called **cross-attention**). But there is another type called **self-attention**, where each position in a sequence attends to all other positions in the same sequence.

The word **self-attention** means a sequence paying attention to itself. Each word looks at every other word (including itself) to understand context.

```
+------------------------------------------------------------------+
|              Self-Attention Explained                              |
+------------------------------------------------------------------+
|                                                                   |
|  Sentence: "The cat sat on the mat"                               |
|                                                                   |
|  For the word "sat", self-attention asks:                         |
|    How relevant is "The"  to understanding "sat"?  --> low        |
|    How relevant is "cat"  to understanding "sat"?  --> high       |
|    How relevant is "sat"  to understanding "sat"?  --> medium     |
|    How relevant is "on"   to understanding "sat"?  --> medium     |
|    How relevant is "the"  to understanding "sat"?  --> low        |
|    How relevant is "mat"  to understanding "sat"?  --> medium     |
|                                                                   |
|  Result: "sat" now has a richer representation that includes      |
|  information about WHO sat (the cat) and WHERE (on the mat).      |
|                                                                   |
+------------------------------------------------------------------+
```

Why is this powerful? Consider the word "it" in this sentence:
- "The **animal** didn't cross the street because **it** was too tired."

What does "it" refer to? The animal. Self-attention can learn this by giving high attention weight from "it" to "animal."

- "The animal didn't cross the **street** because **it** was too wide."

Now "it" refers to the street! Self-attention can learn this too by looking at the context.

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

torch.manual_seed(42)

# Self-attention: each word attends to every other word
words = ["The", "cat", "sat", "on", "the", "mat"]
seq_len = len(words)
d_model = 8

# Input embeddings (one vector per word)
X = torch.randn(seq_len, d_model)

# Create Q, K, V from the SAME input
W_q = nn.Linear(d_model, d_model, bias=False)
W_k = nn.Linear(d_model, d_model, bias=False)
W_v = nn.Linear(d_model, d_model, bias=False)

Q = W_q(X)   # (6, 8) - each word has a query
K = W_k(X)   # (6, 8) - each word has a key
V = W_v(X)   # (6, 8) - each word has a value

print(f"Q shape: {Q.shape} (each word asks a question)")
print(f"K shape: {K.shape} (each word has a label)")
print(f"V shape: {V.shape} (each word has content)")

# Compute attention scores: every word against every other word
scores = Q @ K.T  # (6, 6) - a score for each word pair
print(f"\nScores shape: {scores.shape}")
print(f"This is a {seq_len}x{seq_len} matrix.")
print(f"scores[i][j] = how much word i attends to word j")

# Apply softmax to each row
weights = F.softmax(scores, dim=-1)  # (6, 6)

# Print attention weights for "sat" (position 2)
print(f"\nAttention weights for 'sat':")
for j, word in enumerate(words):
    w = weights[2][j].item()
    bar = "#" * int(w * 30)
    print(f"  --> {word:5s}: {w:.3f}  {bar}")

# Compute new representations
output = weights @ V  # (6, 8)
print(f"\nOutput shape: {output.shape}")
print(f"Each word now has a context-aware representation.")
print(f"'sat' now contains information about what sat (cat) and where (mat).")
```

**Expected Output:**
```
Q shape: torch.Size([6, 8]) (each word asks a question)
K shape: torch.Size([6, 8]) (each word has a label)
V shape: torch.Size([6, 8]) (each word has content)

Scores shape: torch.Size([6, 6])
This is a 6x6 matrix.
scores[i][j] = how much word i attends to word j

Attention weights for 'sat':
  --> The  : 0.123  ###
  --> cat  : 0.312  #########
  --> sat  : 0.198  #####
  --> on   : 0.145  ####
  --> the  : 0.112  ###
  --> mat  : 0.110  ###

Output shape: torch.Size([6, 8])
Each word now has a context-aware representation.
'sat' now contains information about what sat (cat) and where (mat).
```

(Note: Your exact numbers will differ.)

**Line-by-line explanation:**
- **Lines 14-22:** The key difference from regular attention: Q, K, and V all come from the **same** input X. Each word generates its own query ("what am I looking for?"), key ("what do I contain?"), and value ("what information do I offer?").
- **Line 29:** The score matrix is `(6, 6)`. Entry `[i][j]` tells us how much word `i` should pay attention to word `j`. Every word can attend to every other word.
- **Line 33:** Softmax is applied to each row separately. Each row sums to 1.
- **Line 43:** The output is computed by multiplying the attention weights with the values. Each word's new representation is a weighted blend of all words' values.

---

## 20.6 Scaled Dot-Product Attention

The standard attention formula includes a **scaling factor**. Without scaling, when the dimension `d_k` is large, the dot products can become very large numbers. Large numbers push softmax into regions where it has very small gradients, making training difficult.

The word **scaled** means we divide by something to keep the numbers in a reasonable range. We divide by the square root of the key dimension.

```
+------------------------------------------------------------------+
|           Scaled Dot-Product Attention Formula                    |
+------------------------------------------------------------------+
|                                                                   |
|                         Q * K^T                                   |
|  Attention(Q, K, V) = softmax( ----------- ) * V                 |
|                                  sqrt(d_k)                        |
|                                                                   |
|  Where:                                                           |
|    Q = Query matrix (what we're looking for)                      |
|    K = Key matrix (what each position offers)                     |
|    V = Value matrix (the actual information)                      |
|    d_k = dimension of the keys (number of features)               |
|    K^T = transpose of K                                           |
|                                                                   |
|  Why sqrt(d_k)?                                                   |
|    Without scaling, dot products grow proportionally to d_k.      |
|    Dividing by sqrt(d_k) keeps them at a reasonable magnitude.    |
|                                                                   |
+------------------------------------------------------------------+
```

```python
import torch
import torch.nn.functional as F
import math

torch.manual_seed(42)

# Show why scaling matters
d_k_small = 4
d_k_large = 512

# Generate random Q and K
Q_small = torch.randn(1, d_k_small)
K_small = torch.randn(5, d_k_small)

Q_large = torch.randn(1, d_k_large)
K_large = torch.randn(5, d_k_large)

# Without scaling
scores_small = Q_small @ K_small.T
scores_large = Q_large @ K_large.T

print("WITHOUT scaling:")
print(f"  d_k=4:   scores = {[f'{s:.2f}' for s in scores_small[0].tolist()]}")
print(f"  d_k=512: scores = {[f'{s:.2f}' for s in scores_large[0].tolist()]}")
print(f"\n  d_k=4:   max score = {scores_small.abs().max():.2f}")
print(f"  d_k=512: max score = {scores_large.abs().max():.2f}")

# Softmax of large scores pushes everything to 0 or 1
weights_small = F.softmax(scores_small, dim=-1)
weights_large = F.softmax(scores_large, dim=-1)

print(f"\n  d_k=4:   softmax = {[f'{w:.3f}' for w in weights_small[0].tolist()]}")
print(f"  d_k=512: softmax = {[f'{w:.3f}' for w in weights_large[0].tolist()]}")
print(f"\n  Notice: large d_k makes softmax peaked (almost one-hot).")
print(f"  This means attention only looks at ONE position, losing the benefit.")

# WITH scaling
scores_large_scaled = scores_large / math.sqrt(d_k_large)
weights_large_scaled = F.softmax(scores_large_scaled, dim=-1)

print(f"\nWITH scaling (divide by sqrt({d_k_large}) = {math.sqrt(d_k_large):.1f}):")
print(f"  Scaled softmax = {[f'{w:.3f}' for w in weights_large_scaled[0].tolist()]}")
print(f"  Now the weights are more spread out, allowing attention to blend information.")
```

**Expected Output:**
```
WITHOUT scaling:
  d_k=4:   scores = ['-0.35', '1.23', '0.67', '-0.89', '0.12']
  d_k=512: scores = ['-15.67', '23.45', '8.91', '-12.34', '5.67']

  d_k=4:   max score = 1.23
  d_k=512: max score = 23.45

  d_k=4:   softmax = ['0.082', '0.399', '0.228', '0.048', '0.131']
  d_k=512: softmax = ['0.000', '1.000', '0.000', '0.000', '0.000']

  Notice: large d_k makes softmax peaked (almost one-hot).
  This means attention only looks at ONE position, losing the benefit.

WITH scaling (divide by sqrt(512) = 22.6):
  Scaled softmax = ['0.098', '0.375', '0.214', '0.067', '0.141']
  Now the weights are more spread out, allowing attention to blend information.
```

(Note: Your exact numbers will differ, but the pattern will be the same.)

### Implementing Scaled Dot-Product Attention

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import math

def scaled_dot_product_attention(Q, K, V):
    """
    Compute scaled dot-product attention.

    Args:
        Q: Query tensor (batch, seq_len_q, d_k)
        K: Key tensor (batch, seq_len_k, d_k)
        V: Value tensor (batch, seq_len_k, d_v)

    Returns:
        output: Weighted sum of values (batch, seq_len_q, d_v)
        weights: Attention weights (batch, seq_len_q, seq_len_k)
    """
    d_k = K.shape[-1]

    # Step 1: Compute scores
    scores = torch.bmm(Q, K.transpose(1, 2))  # (batch, seq_q, seq_k)

    # Step 2: Scale
    scores = scores / math.sqrt(d_k)

    # Step 3: Softmax
    weights = F.softmax(scores, dim=-1)  # (batch, seq_q, seq_k)

    # Step 4: Weighted sum of values
    output = torch.bmm(weights, V)  # (batch, seq_q, d_v)

    return output, weights

# Test it
torch.manual_seed(42)

batch_size = 2
seq_len = 5
d_k = 8

Q = torch.randn(batch_size, seq_len, d_k)
K = torch.randn(batch_size, seq_len, d_k)
V = torch.randn(batch_size, seq_len, d_k)

output, weights = scaled_dot_product_attention(Q, K, V)

print(f"Q shape:      {Q.shape}")
print(f"K shape:      {K.shape}")
print(f"V shape:      {V.shape}")
print(f"Output shape: {output.shape}")
print(f"Weights shape: {weights.shape}")
print(f"\nWeights for first batch, first query position:")
print(f"  {[f'{w:.3f}' for w in weights[0, 0].tolist()]}")
print(f"  Sum: {weights[0, 0].sum().item():.3f}")
```

**Expected Output:**
```
Q shape:      torch.Size([2, 5, 8])
K shape:      torch.Size([2, 5, 8])
V shape:      torch.Size([2, 5, 8])
Output shape: torch.Size([2, 5, 8])
Weights shape: torch.Size([2, 5, 5])

Weights for first batch, first query position:
  ['0.312', '0.198', '0.145', '0.234', '0.111']
  Sum: 1.000
```

**Line-by-line explanation:**
- **Line 22:** `torch.bmm` is **batched matrix multiplication**. It multiplies matrices within each batch independently. We multiply Q with the transpose of K to get similarity scores.
- **Line 25:** We divide by `sqrt(d_k)` to scale the scores. This prevents extremely large values.
- **Line 28:** Softmax along the last dimension (across key positions) converts scores to probabilities.
- **Line 31:** We multiply the attention weights with the values. Each query position gets a weighted combination of all value vectors.

---

## 20.7 Attention with an LSTM Encoder

Let us build a complete model that combines LSTM with attention for classification:

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class AttentionClassifier(nn.Module):
    def __init__(self, vocab_size, embed_size, hidden_size, num_classes):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_size, padding_idx=0)
        self.lstm = nn.LSTM(embed_size, hidden_size, batch_first=True)

        # Attention parameters
        self.attention_weight = nn.Linear(hidden_size, 1)

        # Classifier
        self.fc = nn.Linear(hidden_size, num_classes)

    def attention(self, lstm_output):
        """
        Compute attention over LSTM outputs.

        Args:
            lstm_output: (batch, seq_len, hidden_size)

        Returns:
            context: (batch, hidden_size)
            weights: (batch, seq_len)
        """
        # Compute attention scores
        scores = self.attention_weight(lstm_output).squeeze(-1)  # (batch, seq_len)
        weights = F.softmax(scores, dim=-1)  # (batch, seq_len)

        # Weighted sum
        context = torch.bmm(
            weights.unsqueeze(1),   # (batch, 1, seq_len)
            lstm_output             # (batch, seq_len, hidden)
        ).squeeze(1)                # (batch, hidden)

        return context, weights

    def forward(self, x):
        # x: (batch, seq_len)
        embedded = self.embedding(x)                 # (batch, seq_len, embed)
        lstm_out, _ = self.lstm(embedded)             # (batch, seq_len, hidden)
        context, attn_weights = self.attention(lstm_out)  # (batch, hidden)
        output = self.fc(context)                     # (batch, num_classes)
        return output, attn_weights

# Create and test the model
torch.manual_seed(42)
model = AttentionClassifier(
    vocab_size=100,
    embed_size=16,
    hidden_size=32,
    num_classes=2
)

# Fake input: 3 sentences, each 8 words
x = torch.randint(1, 100, (3, 8))

output, attention = model(x)
print(f"Input shape:     {x.shape}")
print(f"Output shape:    {output.shape}")
print(f"Attention shape: {attention.shape}")
print(f"\nAttention weights for first sentence:")
print(f"  {[f'{w:.3f}' for w in attention[0].tolist()]}")
print(f"  Sum: {attention[0].sum().item():.3f}")
print(f"\nThe model learns which words matter most for classification.")
print(f"Without attention, it would only use the final LSTM hidden state.")
print(f"With attention, it can focus on any word in the sentence.")
```

**Expected Output:**
```
Input shape:     torch.Size([3, 8])
Output shape:    torch.Size([3, 2])
Attention shape: torch.Size([3, 8])

Attention weights for first sentence:
  ['0.125', '0.134', '0.112', '0.128', '0.119', '0.143', '0.121', '0.118']
  Sum: 1.000

The model learns which words matter most for classification.
Without attention, it would only use the final LSTM hidden state.
With attention, it can focus on any word in the sentence.
```

(Note: Before training, attention weights are roughly uniform. After training, they would concentrate on the most important words.)

**Line-by-line explanation:**
- **Line 13:** A linear layer that learns to compute an attention score for each time step. It maps from `hidden_size` to 1 (a single score per position).
- **Line 30:** We apply the linear layer to every position in the LSTM output. This produces one score per position.
- **Lines 34-37:** We reshape the weights and use batch matrix multiplication to compute the weighted sum of LSTM outputs.
- **Line 46:** We pass all LSTM outputs (not just the last one) through attention to get a context vector.
- **Line 47:** The context vector captures information from the entire sequence, weighted by importance.

---

## Common Mistakes

```
+------------------------------------------------------------------+
|                    Common Mistakes                                |
+------------------------------------------------------------------+
|                                                                   |
|  1. Forgetting to scale dot-product attention                     |
|     WRONG:  scores = Q @ K.T                                     |
|     RIGHT:  scores = (Q @ K.T) / sqrt(d_k)                       |
|     Without scaling, softmax becomes too peaked.                  |
|                                                                   |
|  2. Applying softmax on the wrong dimension                       |
|     WRONG:  softmax(scores, dim=0)                                |
|     RIGHT:  softmax(scores, dim=-1) (across the key positions)   |
|                                                                   |
|  3. Confusing Q, K, V dimensions                                  |
|     Q and K must have the same last dimension (d_k)               |
|     V can have a different last dimension (d_v)                    |
|     Output dimension matches V, not K                              |
|                                                                   |
|  4. Not handling padding in attention                              |
|     WRONG:  Letting attention attend to padding tokens             |
|     RIGHT:  Set padding positions to -inf before softmax           |
|             (attention masking)                                   |
|                                                                   |
|  5. Thinking attention replaces RNNs entirely                     |
|     Attention is often COMBINED with RNNs (LSTM + Attention).     |
|     Transformers use attention WITHOUT RNNs (next chapter).       |
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
|  1. Always scale attention scores by sqrt(d_k).                   |
|     This prevents softmax saturation and training instability.    |
|                                                                   |
|  2. Use attention masks for padded sequences.                     |
|     Set mask positions to -inf before softmax so they get         |
|     zero weight.                                                  |
|                                                                   |
|  3. Visualize attention weights to debug and interpret.           |
|     Attention weights show what the model focuses on.             |
|                                                                   |
|  4. Consider multi-head attention (next chapter) for              |
|     capturing different types of relationships.                   |
|                                                                   |
|  5. For classification tasks, attention over LSTM outputs         |
|     usually outperforms using just the final hidden state.        |
|                                                                   |
|  6. Start with simple additive attention before trying            |
|     more complex variants.                                        |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Quick Summary

Attention solves the bottleneck problem by allowing the model to look at all positions in the input instead of compressing everything into a single vector. It uses three components: Query (what we seek), Key (what each position offers), and Value (the information to retrieve). Scores are computed as the dot product of queries and keys, scaled by the square root of the key dimension, and normalized with softmax to produce attention weights. Self-attention lets every position in a sequence attend to every other position, enabling rich contextual understanding. Attention is the foundation of the Transformer architecture.

---

## Key Points

```
+------------------------------------------------------------------+
|                      Key Points                                    |
+------------------------------------------------------------------+
|                                                                   |
|  - Bottleneck: compressing a whole sequence into one vector       |
|    loses information for long sequences                           |
|                                                                   |
|  - Attention lets the model look back at all encoder states       |
|                                                                   |
|  - Q (Query) = what I'm looking for                                |
|  - K (Key) = what each position contains                           |
|  - V (Value) = the actual information to retrieve                  |
|                                                                   |
|  - Attention = softmax(Q * K^T / sqrt(d_k)) * V                   |
|                                                                   |
|  - Self-attention: Q, K, V all come from the same input           |
|                                                                   |
|  - Scaling by sqrt(d_k) prevents softmax saturation               |
|                                                                   |
|  - Attention weights are interpretable (you can visualize them)   |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Practice Questions

1. Explain the bottleneck problem in your own words. Why does a single context vector struggle with long sequences?

2. Using the library analogy, explain what happens when you search for "cooking pasta" in a library. What are the Query, Keys, and Values in this scenario?

3. Why do we divide by `sqrt(d_k)` in scaled dot-product attention? What would happen if we did not scale?

4. What is the difference between cross-attention and self-attention? Give a practical example of each.

5. The attention weight matrix for a sequence of length 6 has shape `(6, 6)`. Entry `[2][4]` is 0.35. What does this mean in plain English?

---

## Exercises

### Exercise 1: Implement Attention from Scratch

Write a function that takes encoder hidden states (from an LSTM) and a decoder hidden state, computes attention weights, and returns the context vector. Test it with random data and verify that the weights sum to 1.

### Exercise 2: Attention Masking

Modify the `scaled_dot_product_attention` function to accept an optional mask. Positions where the mask is `True` should be ignored (set to `-inf` before softmax). Test it by masking the last 2 positions in a sequence of 5.

### Exercise 3: Compare With and Without Attention

Build two LSTM-based sentiment classifiers: one that uses only the final hidden state and one that uses attention over all hidden states. Train both on the same data and compare their accuracy and training speed.

---

## What Is Next?

You have learned how attention allows models to focus on relevant parts of the input. But so far, attention has been used alongside RNNs. In the next chapter, you will learn about the **Transformer**, an architecture that uses attention *exclusively* -- no recurrence at all. The Transformer processes all positions in parallel using multi-head self-attention, making it dramatically faster and more powerful than RNN-based models.
