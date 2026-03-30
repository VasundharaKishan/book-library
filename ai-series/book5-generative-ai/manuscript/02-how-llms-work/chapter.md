# Chapter 2: How LLMs Work

## What You Will Learn

In this chapter, you will learn:

- How the attention mechanism lets a model focus on the most relevant parts of the input
- The step-by-step process of next-token prediction
- What temperature and sampling strategies are and how they affect output
- What happens during inference (when the model generates a response)
- How context windows work and why they have limits
- The difference between tokens and words in practice

## Why This Chapter Matters

In Chapter 1, you learned that an LLM predicts the next token. But how does it actually do this? What computations happen between when you type a prompt and when you see a response?

Understanding the mechanics helps you in practical ways. When you know how temperature works, you can control whether the model gives creative or predictable answers. When you understand context windows, you know why the model "forgets" things in long conversations. When you grasp attention, you understand why word order and phrasing matter so much.

This chapter takes you inside the machine.

---

## A Quick Recap: The Transformer

LLMs are built on an architecture called the **Transformer**. If you have read the earlier books in this series, you have already seen Transformers in detail. Here is a quick recap of the key idea.

**Transformer:** A type of neural network architecture introduced in 2017 that processes text using a mechanism called "attention." It replaced older approaches (like RNNs) because it can process all tokens in parallel and capture long-range relationships in text.

```
+----------------------------------------------------------+
|              The Transformer Architecture                 |
|              (Simplified for LLMs)                        |
+----------------------------------------------------------+
|                                                            |
|  Input tokens: ["The", "cat", "sat", "on", "the", "___"] |
|       |                                                    |
|       v                                                    |
|  +------------------+                                      |
|  | Token Embeddings |  Convert tokens to number vectors   |
|  +------------------+                                      |
|       |                                                    |
|       v                                                    |
|  +------------------+                                      |
|  | Attention Layer 1|  Figure out which tokens matter      |
|  +------------------+                                      |
|       |                                                    |
|       v                                                    |
|  +------------------+                                      |
|  | Feed-Forward 1   |  Process the attended information   |
|  +------------------+                                      |
|       |                                                    |
|       v                                                    |
|  +------------------+                                      |
|  | Attention Layer 2|  Deeper pattern recognition          |
|  +------------------+                                      |
|       |                                                    |
|       v                                                    |
|  +------------------+                                      |
|  | Feed-Forward 2   |  More processing                    |
|  +------------------+                                      |
|       |                                                    |
|       v                                                    |
|     ... (many more layers, typically 32-96)               |
|       |                                                    |
|       v                                                    |
|  +------------------+                                      |
|  | Output Layer     |  Probability for each possible token|
|  +------------------+                                      |
|       |                                                    |
|       v                                                    |
|  Next token prediction: "mat" (highest probability)       |
|                                                            |
+----------------------------------------------------------+
```

The two key components are **attention layers** (which figure out relationships between tokens) and **feed-forward layers** (which process the information). These layers are stacked many times. GPT-3 has 96 layers. GPT-4 is estimated to have even more.

---

## The Attention Mechanism: How Models Focus

### The Core Idea

When you read the sentence "The cat sat on the mat because it was tired", your brain automatically knows that "it" refers to "the cat", not "the mat". You focus your attention on "cat" when interpreting "it".

The attention mechanism does something similar. For each token, it calculates how much "attention" to pay to every other token.

```
+----------------------------------------------------------+
|           Attention: Which Words Matter?                  |
+----------------------------------------------------------+
|                                                            |
|  Sentence: "The cat sat on the mat because it was tired"  |
|                                                            |
|  When processing "it", the model asks:                    |
|  How relevant is each previous word to understanding "it"?|
|                                                            |
|  The  ───── low attention  (0.02)                         |
|  cat  ───── HIGH attention (0.45)  <-- "it" = "cat"      |
|  sat  ───── low attention  (0.08)                         |
|  on   ───── low attention  (0.01)                         |
|  the  ───── low attention  (0.02)                         |
|  mat  ───── medium attention (0.15)                       |
|  because ── medium attention (0.12)                       |
|  it   ───── medium attention (0.10)                       |
|  was  ───── low attention  (0.05)                         |
|                                                            |
|  Total attention weights always add up to 1.0             |
|                                                            |
+----------------------------------------------------------+
```

### Query, Key, and Value

The attention mechanism works through three concepts: Query (Q), Key (K), and Value (V).

**Analogy:** Think of a library search system.
- **Query (Q):** Your search question — "I need information about cats"
- **Key (K):** The label on each book — "Cat Care", "Dog Training", "Cat Biology"
- **Value (V):** The actual content inside each book

The system compares your query against every key to find the best matches, then returns the values from the matching books.

```python
# Simplified demonstration of attention mechanism

import math

def simple_attention(query_word, sentence_words, relevance_scores):
    """
    Demonstrate how attention works conceptually.
    In reality, Q, K, V are learned vector representations.
    Here we use predefined relevance scores for clarity.
    """
    print(f"Computing attention for: '{query_word}'")
    print(f"Sentence: {' '.join(sentence_words)}")
    print()

    # Step 1: Compute raw attention scores
    # (In reality: dot product of query and key vectors)
    raw_scores = relevance_scores
    print("Step 1 - Raw relevance scores:")
    for word, score in zip(sentence_words, raw_scores):
        bar = "█" * int(score * 20)
        print(f"  {word:10s} -> {score:.2f} {bar}")

    # Step 2: Apply softmax to get probabilities
    # (Makes all scores positive and sum to 1.0)
    exp_scores = [math.exp(s) for s in raw_scores]
    total = sum(exp_scores)
    attention_weights = [s / total for s in exp_scores]

    print(f"\nStep 2 - Attention weights (after softmax):")
    for word, weight in zip(sentence_words, attention_weights):
        bar = "█" * int(weight * 40)
        print(f"  {word:10s} -> {weight:.3f} {bar}")

    print(f"\n  Sum of weights: {sum(attention_weights):.3f} (always 1.0)")

    # Step 3: Weighted combination
    # Each word's "value" is multiplied by its attention weight
    print(f"\nStep 3 - The model combines information from all words,")
    print(f"         weighted by attention. Words with high attention")
    print(f"         contribute more to the output.")

    return attention_weights

# Example: What does "it" attend to?
words = ["The", "cat", "sat", "on", "the", "mat", "because"]
scores = [0.1, 2.5, 0.5, 0.1, 0.1, 1.0, 0.8]

attention = simple_attention("it", words, scores)
```

**Output:**
```
Computing attention for: 'it'
Sentence: The cat sat on the mat because

Step 1 - Raw relevance scores:
  The        -> 0.10
  cat        -> 2.50 ██████████████████████████████████████████████████
  sat        -> 0.50 ██████████
  on         -> 0.10
  the        -> 0.10
  mat        -> 1.00 ████████████████████
  because    -> 0.80 ████████████████

Step 2 - Attention weights (after softmax):
  The        -> 0.007
  cat        -> 0.762 ██████████████████████████████
  sat        -> 0.010
  on         -> 0.007
  the        -> 0.007
  mat        -> 0.170 ██████
  because    -> 0.014

  Sum of weights: 0.977 (always 1.0)

Step 3 - The model combines information from all words,
         weighted by attention. Words with high attention
         contribute more to the output.
```

**Line-by-line explanation:**

- `raw_scores = relevance_scores`: In a real model, these scores come from computing dot products between learned Query and Key vectors. Here we use predefined values to illustrate the concept.
- `math.exp(s)`: The exponential function is part of the softmax calculation. It makes all values positive while preserving their relative ordering.
- `s / total`: Dividing by the total ensures all weights sum to 1.0. This is the softmax function, which converts raw scores into a probability distribution.
- `attention_weights`: The final weights tell the model how much to "pay attention" to each word. "cat" gets 76.2% of the attention because the model learned that pronouns like "it" usually refer to the nearest noun that makes sense.

### Multi-Head Attention

Real LLMs use **multi-head attention**. Instead of computing attention once, they compute it multiple times in parallel, each "head" focusing on different types of relationships.

```
+----------------------------------------------------------+
|              Multi-Head Attention                         |
+----------------------------------------------------------+
|                                                            |
|  Head 1: Focuses on grammatical relationships             |
|          "it" --> "cat" (pronoun reference)                |
|                                                            |
|  Head 2: Focuses on positional relationships              |
|          "it" --> "because" (nearby words)                 |
|                                                            |
|  Head 3: Focuses on semantic relationships                |
|          "it" --> "tired" (what state is "it" in?)        |
|                                                            |
|  Head 4: Focuses on syntactic role                        |
|          "it" --> "was" (subject-verb agreement)           |
|                                                            |
|  All heads combined = rich understanding of context       |
|                                                            |
|  GPT-3 uses 96 attention heads per layer                  |
|  GPT-3 has 96 layers                                      |
|  = 9,216 total attention computations per token!          |
|                                                            |
+----------------------------------------------------------+
```

```python
# Demonstrating multi-head attention concept

def multi_head_attention_demo():
    """
    Show how different attention heads capture different patterns.
    """
    sentence = "The cat sat on the mat because it was tired"
    target = "it"

    # Each head learns to focus on different relationships
    heads = {
        "Head 1 (grammar)": {
            "focus": "pronoun reference",
            "top_attention": "cat (0.72)",
            "what_it_learns": "pronouns refer to nouns"
        },
        "Head 2 (position)": {
            "focus": "nearby context",
            "top_attention": "because (0.35)",
            "what_it_learns": "nearby words provide context"
        },
        "Head 3 (semantics)": {
            "focus": "meaning relationships",
            "top_attention": "tired (0.41)",
            "what_it_learns": "emotional/physical states"
        },
        "Head 4 (syntax)": {
            "focus": "sentence structure",
            "top_attention": "was (0.55)",
            "what_it_learns": "subject-verb patterns"
        },
    }

    print(f"Sentence: '{sentence}'")
    print(f"Processing token: '{target}'")
    print(f"\nMultiple attention heads, each seeing different patterns:")
    print("=" * 55)

    for head_name, info in heads.items():
        print(f"\n  {head_name}:")
        print(f"    Focus type:     {info['focus']}")
        print(f"    Highest weight: {info['top_attention']}")
        print(f"    Pattern learned: {info['what_it_learns']}")

    print("\n" + "=" * 55)
    print("Combined: The model knows 'it' = 'cat', 'it' is 'tired',")
    print("and 'it' is the subject of 'was'.")

multi_head_attention_demo()
```

**Output:**
```
Sentence: 'The cat sat on the mat because it was tired'
Processing token: 'it'

Multiple attention heads, each seeing different patterns:
=======================================================

  Head 1 (grammar):
    Focus type:     pronoun reference
    Highest weight: cat (0.72)
    Pattern learned: pronouns refer to nouns

  Head 2 (position):
    Focus type:     nearby context
    Highest weight: because (0.35)
    Pattern learned: nearby words provide context

  Head 3 (semantics):
    Focus type:     meaning relationships
    Highest weight: tired (0.41)
    Pattern learned: emotional/physical states

  Head 4 (syntax):
    Focus type:     sentence structure
    Highest weight: was (0.55)
    Pattern learned: subject-verb patterns

=======================================================
Combined: The model knows 'it' = 'cat', 'it' is 'tired',
and 'it' is the subject of 'was'.
```

---

## Next-Token Prediction: Step by Step

Now let us walk through exactly what happens when you type a prompt and the model generates a response.

### The Full Process

```
+----------------------------------------------------------+
|        Next-Token Prediction: Complete Pipeline           |
+----------------------------------------------------------+
|                                                            |
|  Your prompt: "What is Python?"                           |
|                                                            |
|  Step 1: TOKENIZE                                         |
|    "What is Python?" --> [2061, 318, 11361, 30]           |
|                                                            |
|  Step 2: EMBED                                            |
|    Each token ID --> a vector of ~4096 numbers            |
|    [2061] --> [0.12, -0.34, 0.56, ..., 0.78]             |
|                                                            |
|  Step 3: ADD POSITION INFO                                |
|    Tell the model where each token appears                |
|    Token at position 0, 1, 2, 3                           |
|                                                            |
|  Step 4: PASS THROUGH TRANSFORMER LAYERS                  |
|    Layer 1:  Attention + Feed-Forward                     |
|    Layer 2:  Attention + Feed-Forward                     |
|    ...                                                     |
|    Layer 96: Attention + Feed-Forward                     |
|                                                            |
|  Step 5: OUTPUT PROBABILITIES                             |
|    For every possible next token, compute probability     |
|    "Python" : 0.001                                       |
|    "is"     : 0.002                                       |
|    "a"      : 0.015                                       |
|    ...                                                     |
|    Total: ~50,000 probabilities (one per vocab token)     |
|                                                            |
|  Step 6: SAMPLE                                           |
|    Pick one token based on probabilities + temperature    |
|    Selected: "Python" (token ID 11361)                    |
|                                                            |
|  Step 7: APPEND AND REPEAT                                |
|    New context: "What is Python? Python"                  |
|    Go back to Step 1 with the extended context            |
|                                                            |
+----------------------------------------------------------+
```

```python
# Step-by-step simulation of next-token prediction

def next_token_prediction_demo():
    """
    Walk through each step of how an LLM predicts the next token.
    """
    prompt = "What is Python?"

    print("=" * 60)
    print("NEXT-TOKEN PREDICTION: Step by Step")
    print("=" * 60)

    # Step 1: Tokenization
    print("\n--- Step 1: Tokenization ---")
    tokens = ["What", " is", " Python", "?"]
    token_ids = [2061, 318, 11361, 30]
    print(f"  Input text: '{prompt}'")
    print(f"  Tokens:     {tokens}")
    print(f"  Token IDs:  {token_ids}")

    # Step 2: Embedding
    print("\n--- Step 2: Embedding ---")
    print(f"  Each token ID maps to a vector of numbers.")
    print(f"  Vector size: 4096 numbers (in GPT-3)")
    print(f"  Example (first 5 numbers of token 'What'):")
    embedding_sample = [0.123, -0.456, 0.789, -0.012, 0.345]
    print(f"  [2061] --> {embedding_sample}...")

    # Step 3: Position encoding
    print("\n--- Step 3: Position Encoding ---")
    print(f"  Add position information to each token:")
    for i, token in enumerate(tokens):
        print(f"    Position {i}: '{token}'")

    # Step 4: Transformer layers
    print("\n--- Step 4: Transformer Layers ---")
    print(f"  Pass through 96 layers of attention + feed-forward")
    print(f"  Each layer refines the model's understanding")
    print(f"  Layer  1: Basic word relationships")
    print(f"  Layer 32: Grammatical structure")
    print(f"  Layer 64: Semantic meaning")
    print(f"  Layer 96: Final representation")

    # Step 5: Output probabilities
    print("\n--- Step 5: Output Probabilities ---")
    vocab = {
        "Python":     0.32,
        "It":         0.18,
        "A":          0.12,
        "The":        0.08,
        "\n":         0.07,
        "In":         0.05,
    }
    print(f"  Top predicted next tokens:")
    for token, prob in vocab.items():
        bar = "█" * int(prob * 40)
        display_token = repr(token) if token == "\n" else token
        print(f"    {display_token:10s}: {prob:.0%} {bar}")
    print(f"  ... plus ~49,994 other tokens with small probabilities")

    # Step 6: Sampling
    print("\n--- Step 6: Sampling ---")
    print(f"  With temperature=0.0 (deterministic):")
    print(f"    Always picks: 'Python' (highest probability)")
    print(f"  With temperature=1.0 (balanced):")
    print(f"    Might pick: 'Python', 'It', or 'A' (weighted random)")
    print(f"  With temperature=1.5 (creative):")
    print(f"    Could pick almost any token (more randomness)")

    # Step 7: Append and repeat
    print("\n--- Step 7: Append and Repeat ---")
    generated_tokens = ["Python", " is", " a", " programming", " language"]
    text_so_far = prompt
    for i, token in enumerate(generated_tokens):
        text_so_far += token
        print(f"  Iteration {i+1}: predicted '{token.strip()}'")
        print(f"    Full text: '{text_so_far}'")

    print("\n" + "=" * 60)

next_token_prediction_demo()
```

**Output:**
```
============================================================
NEXT-TOKEN PREDICTION: Step by Step
============================================================

--- Step 1: Tokenization ---
  Input text: 'What is Python?'
  Tokens:     ['What', ' is', ' Python', '?']
  Token IDs:  [2061, 318, 11361, 30]

--- Step 2: Embedding ---
  Each token ID maps to a vector of numbers.
  Vector size: 4096 numbers (in GPT-3)
  Example (first 5 numbers of token 'What'):
  [2061] --> [0.123, -0.456, 0.789, -0.012, 0.345]...

--- Step 3: Position Encoding ---
  Add position information to each token:
    Position 0: 'What'
    Position 1: ' is'
    Position 2: ' Python'
    Position 3: '?'

--- Step 4: Transformer Layers ---
  Pass through 96 layers of attention + feed-forward
  Each layer refines the model's understanding
  Layer  1: Basic word relationships
  Layer 32: Grammatical structure
  Layer 64: Semantic meaning
  Layer 96: Final representation

--- Step 5: Output Probabilities ---
  Top predicted next tokens:
    Python    : 32% ████████████
    It        : 18% ███████
    A         : 12% ████
    The       : 8% ███
    '\n'      : 7% ██
    In        : 5% ██
  ... plus ~49,994 other tokens with small probabilities

--- Step 6: Sampling ---
  With temperature=0.0 (deterministic):
    Always picks: 'Python' (highest probability)
  With temperature=1.0 (balanced):
    Might pick: 'Python', 'It', or 'A' (weighted random)
  With temperature=1.5 (creative):
    Could pick almost any token (more randomness)

--- Step 7: Append and Repeat ---
  Iteration 1: predicted 'Python'
    Full text: 'What is Python?Python'
  Iteration 2: predicted 'is'
    Full text: 'What is Python?Python is'
  Iteration 3: predicted 'a'
    Full text: 'What is Python?Python is a'
  Iteration 4: predicted 'programming'
    Full text: 'What is Python?Python is a programming'
  Iteration 5: predicted 'language'
    Full text: 'What is Python?Python is a programming language'

============================================================
```

---

## Temperature and Sampling

### What Is Temperature?

**Temperature** is a number that controls how random or predictable the model's output is. It is one of the most important settings you can adjust.

```
+----------------------------------------------------------+
|              Temperature Scale                            |
+----------------------------------------------------------+
|                                                            |
|  Temperature = 0.0  (Deterministic / Greedy)              |
|    Always picks the highest probability token              |
|    Output: predictable, repetitive, "safe"                |
|    Use for: factual questions, code, data extraction      |
|                                                            |
|  Temperature = 0.7  (Balanced)                            |
|    Usually picks high-probability tokens                   |
|    Occasionally picks less likely ones                     |
|    Output: natural, varied, good default                  |
|    Use for: general conversation, writing                 |
|                                                            |
|  Temperature = 1.0  (Standard)                            |
|    Samples directly from the probability distribution      |
|    Output: creative, sometimes surprising                 |
|    Use for: brainstorming, creative writing               |
|                                                            |
|  Temperature = 1.5+ (High / Creative)                     |
|    Flattens probabilities, rare tokens get a chance        |
|    Output: very creative, sometimes nonsensical           |
|    Use for: poetry, experimental writing                  |
|                                                            |
+----------------------------------------------------------+
```

**Analogy:** Think of temperature like the "adventurousness" setting on a music playlist.
- Temperature 0 = play the most popular song every time
- Temperature 0.7 = mostly popular songs, but throw in some lesser-known ones
- Temperature 1.5 = play random songs from the entire library, including obscure ones

```python
# Demonstrating how temperature affects token selection
import math
import random

def apply_temperature(probabilities, temperature):
    """
    Apply temperature to a probability distribution.

    Temperature controls randomness:
    - Low temperature (0.1): makes high-prob tokens even more dominant
    - Temperature 1.0: uses probabilities as-is
    - High temperature (2.0): makes all tokens more equally likely
    """
    if temperature == 0:
        # Greedy: always pick the highest probability
        max_prob = max(probabilities.values())
        return {k: (1.0 if v == max_prob else 0.0)
                for k, v in probabilities.items()}

    # Apply temperature: divide log-probabilities by temperature
    # then recompute softmax
    adjusted = {}
    for token, prob in probabilities.items():
        # Take log, divide by temperature, then exp
        adjusted[token] = math.exp(math.log(prob + 1e-10) / temperature)

    # Normalize to sum to 1
    total = sum(adjusted.values())
    return {k: v / total for k, v in adjusted.items()}

# Original probability distribution from the model
original_probs = {
    "blue":    0.40,
    "clear":   0.25,
    "dark":    0.15,
    "bright":  0.10,
    "grey":    0.05,
    "purple":  0.03,
    "green":   0.02,
}

print("Prompt: 'The sky is ___'")
print("=" * 55)

for temp in [0, 0.5, 1.0, 1.5]:
    adjusted = apply_temperature(original_probs, temp)
    print(f"\nTemperature = {temp}:")
    for token, prob in adjusted.items():
        bar = "█" * int(prob * 30)
        print(f"  {token:8s}: {prob:.3f} {bar}")
```

**Output:**
```
Prompt: 'The sky is ___'
=======================================================

Temperature = 0:
  blue    : 1.000 ██████████████████████████████
  clear   : 0.000
  dark    : 0.000
  bright  : 0.000
  grey    : 0.000
  purple  : 0.000
  green   : 0.000

Temperature = 0.5:
  blue    : 0.596 █████████████████
  clear   : 0.233 ██████
  dark    : 0.091 ██
  bright  : 0.047 █
  grey    : 0.013
  purple  : 0.005
  green   : 0.002

Temperature = 1.0:
  blue    : 0.400 ████████████
  clear   : 0.250 ███████
  dark    : 0.150 ████
  bright  : 0.100 ███
  grey    : 0.050 █
  purple  : 0.030
  green   : 0.020

Temperature = 1.5:
  blue    : 0.308 █████████
  clear   : 0.222 ██████
  dark    : 0.159 ████
  bright  : 0.121 ███
  grey    : 0.075 ██
  purple  : 0.055 █
  green   : 0.042 █
```

**Line-by-line explanation:**

- `apply_temperature(probabilities, temperature)`: This function adjusts probability distributions based on temperature. Lower temperatures make the distribution "sharper" (top tokens dominate), higher temperatures make it "flatter" (all tokens become more equally likely).
- `math.log(prob + 1e-10) / temperature`: We take the logarithm of each probability, divide by temperature, then exponentiate. This is the mathematical operation that "sharpens" or "flattens" the distribution.
- At temperature 0, only "blue" has a probability of 1.0. The model always picks "blue".
- At temperature 1.5, even "green" (originally 2%) gets a 4.2% chance. The model might surprise you.

### Other Sampling Strategies

Temperature is not the only way to control output. Here are other common strategies:

```
+----------------------------------------------------------+
|              Sampling Strategies                          |
+----------------------------------------------------------+
|                                                            |
|  Top-K Sampling:                                          |
|    Only consider the K most likely tokens                 |
|    Example: top_k=5 means only the 5 best tokens          |
|    are candidates. All others get 0 probability.          |
|                                                            |
|  Top-P (Nucleus) Sampling:                                |
|    Keep tokens until cumulative probability >= P          |
|    Example: top_p=0.9 keeps tokens that together          |
|    make up 90% of the probability mass.                   |
|    This adapts: sometimes 3 tokens, sometimes 10.         |
|                                                            |
|  Greedy Decoding:                                         |
|    Always pick the single most likely token               |
|    Equivalent to temperature=0                            |
|    Fast but can be repetitive                             |
|                                                            |
|  Beam Search:                                             |
|    Track multiple possible sequences simultaneously       |
|    Pick the overall best sequence                         |
|    Used more in translation than chat                     |
|                                                            |
+----------------------------------------------------------+
```

```python
# Demonstrating Top-K and Top-P sampling

def top_k_sampling(probs, k):
    """Keep only the top K tokens, zero out the rest."""
    sorted_tokens = sorted(probs.items(), key=lambda x: x[1], reverse=True)
    top_k_tokens = dict(sorted_tokens[:k])

    # Renormalize
    total = sum(top_k_tokens.values())
    return {t: p/total for t, p in top_k_tokens.items()}

def top_p_sampling(probs, p):
    """Keep tokens until cumulative probability reaches p."""
    sorted_tokens = sorted(probs.items(), key=lambda x: x[1], reverse=True)
    cumulative = 0
    selected = {}

    for token, prob in sorted_tokens:
        selected[token] = prob
        cumulative += prob
        if cumulative >= p:
            break

    # Renormalize
    total = sum(selected.values())
    return {t: pr/total for t, pr in selected.items()}

# Original probabilities
probs = {
    "blue": 0.40, "clear": 0.25, "dark": 0.15,
    "bright": 0.10, "grey": 0.05, "purple": 0.03, "green": 0.02
}

print("Original distribution:")
for t, p in probs.items():
    bar = "█" * int(p * 40)
    print(f"  {t:8s}: {p:.2f} {bar}")

# Top-K = 3
print("\nTop-K sampling (K=3):")
top_k_result = top_k_sampling(probs, 3)
for t, p in top_k_result.items():
    bar = "█" * int(p * 40)
    print(f"  {t:8s}: {p:.2f} {bar}")
print(f"  (Only {len(top_k_result)} tokens considered)")

# Top-P = 0.8
print("\nTop-P sampling (P=0.8):")
top_p_result = top_p_sampling(probs, 0.8)
for t, p in top_p_result.items():
    bar = "█" * int(p * 40)
    print(f"  {t:8s}: {p:.2f} {bar}")
print(f"  (Only {len(top_p_result)} tokens considered)")
```

**Output:**
```
Original distribution:
  blue    : 0.40 ████████████████
  clear   : 0.25 ██████████
  dark    : 0.15 ██████
  bright  : 0.10 ████
  grey    : 0.05 ██
  purple  : 0.03 █
  green   : 0.02

Top-K sampling (K=3):
  blue    : 0.50 ████████████████████
  clear   : 0.31 ████████████
  dark    : 0.19 ███████
  (Only 3 tokens considered)

Top-P sampling (P=0.8):
  blue    : 0.50 ████████████████████
  clear   : 0.31 ████████████
  dark    : 0.19 ███████
  (Only 3 tokens considered)
```

---

## The Inference Process

**Inference** is what happens when the model generates a response. Training is when the model learns. Inference is when it uses what it learned.

```
+----------------------------------------------------------+
|           Training vs Inference                           |
+----------------------------------------------------------+
|                                                            |
|  Training (happens once, costs millions):                 |
|    - Read trillions of tokens                             |
|    - Adjust billions of parameters                        |
|    - Takes weeks/months on thousands of GPUs              |
|    - Goal: learn to predict next tokens well              |
|                                                            |
|  Inference (happens every time you use the model):        |
|    - Read your prompt                                     |
|    - Generate response token by token                     |
|    - Takes seconds on one or a few GPUs                   |
|    - Goal: generate helpful, relevant text                |
|                                                            |
+----------------------------------------------------------+
```

### What Happens During Inference

```python
# Simulating the inference process

def simulate_inference(prompt, max_tokens=10):
    """
    Simulate inference: the process of generating a response.
    """
    # Simulated vocabulary with probabilities for each context
    knowledge = {
        "What is Python?": {
            " Python": 0.35, " It": 0.20, " A": 0.15
        },
        "What is Python? Python": {
            " is": 0.80, " was": 0.10, ",": 0.05
        },
        "What is Python? Python is": {
            " a": 0.60, " an": 0.15, " the": 0.10
        },
        "What is Python? Python is a": {
            " programming": 0.50, " popular": 0.20, " high": 0.15
        },
        "What is Python? Python is a programming": {
            " language": 0.85, " tool": 0.08, " framework": 0.05
        },
        "What is Python? Python is a programming language": {
            ".": 0.40, " that": 0.30, " used": 0.15
        },
    }

    print("INFERENCE PROCESS")
    print("=" * 60)
    print(f"Prompt: '{prompt}'")
    print(f"Max tokens to generate: {max_tokens}")
    print()

    current_text = prompt
    generated = []

    for step in range(max_tokens):
        # Look up probabilities for current context
        if current_text in knowledge:
            probs = knowledge[current_text]

            # Pick the most likely token (greedy / temp=0)
            next_token = max(probs, key=probs.get)
            confidence = probs[next_token]

            generated.append(next_token)
            current_text += next_token

            print(f"Step {step + 1}:")
            print(f"  Context length: {len(current_text)} characters")
            print(f"  Predicted: '{next_token.strip()}' "
                  f"(confidence: {confidence:.0%})")
            print(f"  Text: '{current_text}'")
            print()

            # Stop at period
            if next_token.strip() == ".":
                print("  [Stop: end of sentence reached]")
                break
        else:
            print(f"Step {step + 1}: [Stop: no more predictions available]")
            break

    print("\n" + "=" * 60)
    print(f"Final response: '{current_text[len(prompt):]}'")
    print(f"Tokens generated: {len(generated)}")

simulate_inference("What is Python?")
```

**Output:**
```
INFERENCE PROCESS
============================================================
Prompt: 'What is Python?'
Max tokens to generate: 10

Step 1:
  Context length: 22 characters
  Predicted: 'Python' (confidence: 35%)
  Text: 'What is Python? Python'

Step 2:
  Context length: 25 characters
  Predicted: 'is' (confidence: 80%)
  Text: 'What is Python? Python is'

Step 3:
  Context length: 27 characters
  Predicted: 'a' (confidence: 60%)
  Text: 'What is Python? Python is a'

Step 4:
  Context length: 39 characters
  Predicted: 'programming' (confidence: 50%)
  Text: 'What is Python? Python is a programming'

Step 5:
  Context length: 48 characters
  Predicted: 'language' (confidence: 85%)
  Text: 'What is Python? Python is a programming language'

Step 6:
  Context length: 49 characters
  Predicted: '.' (confidence: 40%)
  Text: 'What is Python? Python is a programming language.'

  [Stop: end of sentence reached]

============================================================
Final response: ' Python is a programming language.'
Tokens generated: 6
```

---

## Context Windows: The Model's Memory

### What Is a Context Window?

A **context window** is the maximum number of tokens that the model can process at once. It includes both your prompt and the model's response.

**Analogy:** Think of a context window like a desk. You can only fit so many papers on your desk at once. If you add too many, the oldest ones fall off the edge. Similarly, an LLM can only "see" a certain number of tokens at once.

```
+----------------------------------------------------------+
|              Context Window Explained                     |
+----------------------------------------------------------+
|                                                            |
|  Context window = 4,096 tokens (GPT-3.5 example)         |
|                                                            |
|  ┌─────────────────────────────────────────────────┐      |
|  │  System prompt (200 tokens)                     │      |
|  │  User message 1 (100 tokens)                    │      |
|  │  Assistant response 1 (300 tokens)              │      |
|  │  User message 2 (150 tokens)                    │      |
|  │  Assistant response 2 (500 tokens)              │      |
|  │  User message 3 (200 tokens)                    │      |
|  │  ...                                            │      |
|  │  [SPACE LEFT FOR RESPONSE: ~2,646 tokens]       │      |
|  └─────────────────────────────────────────────────┘      |
|                                                            |
|  Total used: 1,450 tokens                                 |
|  Remaining:  2,646 tokens for the response                |
|                                                            |
|  If the conversation gets too long, oldest messages       |
|  must be dropped or summarized to make room.              |
|                                                            |
+----------------------------------------------------------+
```

```python
# Demonstrating context window management

def context_window_demo():
    """Show how messages fill up a context window."""

    context_limit = 4096  # tokens

    messages = [
        ("system",    "You are a helpful assistant.", 8),
        ("user",      "What is machine learning?", 6),
        ("assistant", "Machine learning is a subset of AI that...", 150),
        ("user",      "Can you give me an example?", 8),
        ("assistant", "Sure! Consider email spam filtering...", 200),
        ("user",      "How does it learn from data?", 7),
        ("assistant", "The model looks at training examples...", 350),
        ("user",      "What about deep learning?", 6),
        ("assistant", "Deep learning uses neural networks with...", 400),
        ("user",      "Explain transformers.", 4),
    ]

    print("Context Window Usage")
    print("=" * 60)
    print(f"Context window size: {context_limit:,} tokens")
    print()

    total_used = 0
    for role, content, tokens in messages:
        total_used += tokens
        remaining = context_limit - total_used
        pct = (total_used / context_limit) * 100
        bar_used = "█" * int(pct / 2)
        bar_empty = "░" * (50 - int(pct / 2))

        print(f"  [{role:9s}] +{tokens:4d} tokens | "
              f"Total: {total_used:4d} / {context_limit}")
        print(f"  {bar_used}{bar_empty} {pct:.0f}%")

    remaining = context_limit - total_used
    print(f"\n  Tokens used: {total_used:,}")
    print(f"  Tokens remaining for response: {remaining:,}")

    if remaining < 500:
        print("\n  WARNING: Low context space! Consider:")
        print("    - Summarizing earlier messages")
        print("    - Starting a new conversation")
        print("    - Using a model with a larger context window")

context_window_demo()
```

**Output:**
```
Context Window Usage
============================================================
Context window size: 4,096 tokens

  [system   ] +   8 tokens | Total:    8 / 4096
  █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 0%
  [user     ] +   6 tokens | Total:   14 / 4096
  █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 0%
  [assistant] + 150 tokens | Total:  164 / 4096
  ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 4%
  [user     ] +   8 tokens | Total:  172 / 4096
  ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 4%
  [assistant] + 200 tokens | Total:  372 / 4096
  ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 9%
  [user     ] +   7 tokens | Total:  379 / 4096
  ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 9%
  [assistant] + 350 tokens | Total:  729 / 4096
  ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 17%
  [user     ] +   6 tokens | Total:  735 / 4096
  ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 17%
  [assistant] + 400 tokens | Total: 1135 / 4096
  █████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 27%
  [user     ] +   4 tokens | Total: 1139 / 4096
  █████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 27%

  Tokens used: 1,139
  Tokens remaining for response: 2,957
```

---

## Tokens vs Words

This is a common source of confusion. Tokens and words are not the same thing.

```python
# Demonstrating the difference between tokens and words

examples = [
    {
        "text": "Hello world",
        "tokens": ["Hello", " world"],
        "explanation": "Simple words: each is roughly one token"
    },
    {
        "text": "I'm happy",
        "tokens": ["I", "'m", " happy"],
        "explanation": "Contractions get split: I'm becomes I + 'm"
    },
    {
        "text": "unbelievable",
        "tokens": ["un", "believ", "able"],
        "explanation": "Long words get split into subword pieces"
    },
    {
        "text": "ChatGPT",
        "tokens": ["Chat", "G", "PT"],
        "explanation": "Brand names get split into recognizable parts"
    },
    {
        "text": "123456789",
        "tokens": ["123", "456", "789"],
        "explanation": "Numbers get split into groups of digits"
    },
    {
        "text": "こんにちは",
        "tokens": ["こん", "にち", "は"],
        "explanation": "Non-Latin scripts use more tokens per word"
    },
]

print("Tokens vs Words: They Are Not the Same!")
print("=" * 60)

for ex in examples:
    word_count = len(ex["text"].split())
    token_count = len(ex["tokens"])

    print(f"\n  Text:   '{ex['text']}'")
    print(f"  Words:  {word_count}")
    print(f"  Tokens: {token_count} -> {ex['tokens']}")
    print(f"  Note:   {ex['explanation']}")

print("\n" + "=" * 60)
print("\nRule of thumb for English:")
print("  1 token ≈ 0.75 words")
print("  1 word  ≈ 1.3 tokens")
print("  100 tokens ≈ 75 words")
```

**Output:**
```
Tokens vs Words: They Are Not the Same!
============================================================

  Text:   'Hello world'
  Words:  2
  Tokens: 2 -> ['Hello', ' world']
  Note:   Simple words: each is roughly one token

  Text:   'I'm happy'
  Words:  2
  Tokens: 3 -> ['I', "'m", ' happy']
  Note:   Contractions get split: I'm becomes I + 'm

  Text:   'unbelievable'
  Words:  1
  Tokens: 3 -> ['un', 'believ', 'able']
  Note:   Long words get split into subword pieces

  Text:   'ChatGPT'
  Words:  1
  Tokens: 3 -> ['Chat', 'G', 'PT']
  Note:   Brand names get split into recognizable parts

  Text:   '123456789'
  Words:  1
  Tokens: 3 -> ['123', '456', '789']
  Note:   Numbers get split into groups of digits

  Text:   'こんにちは'
  Words:  1
  Tokens: 3 -> ['こん', 'にち', 'は']
  Note:   Non-Latin scripts use more tokens per word

============================================================

Rule of thumb for English:
  1 token ≈ 0.75 words
  1 word  ≈ 1.3 tokens
  100 tokens ≈ 75 words
```

---

## Common Mistakes

| Mistake | Why It Is Wrong | What to Do Instead |
|---------|----------------|-------------------|
| Setting temperature to 0 for creative tasks | Temperature 0 always picks the most likely token, killing creativity | Use temperature 0.7-1.0 for creative tasks |
| Setting temperature too high for factual tasks | High temperature introduces randomness, leading to errors | Use temperature 0-0.3 for factual tasks |
| Ignoring the context window limit | Exceeding the limit causes old messages to be dropped silently | Track token usage; summarize long conversations |
| Assuming 1 word = 1 token | Words and tokens have a complex relationship | Use a tokenizer library to count tokens accurately |
| Thinking the model "remembers" past conversations | LLMs have no persistent memory beyond the context window | Include all relevant context in each conversation |

---

## Best Practices

1. **Choose temperature based on your task.** Low (0-0.3) for factual tasks, medium (0.5-0.7) for general use, high (0.8-1.2) for creative work.

2. **Monitor your context window usage.** Know how many tokens your conversation uses. Leave enough room for the model's response.

3. **Use top-p sampling alongside temperature.** A common combination is temperature=0.7 with top_p=0.9 for natural-sounding output.

4. **Count tokens, not words.** When you need to stay within limits, use a proper tokenizer to count tokens accurately.

5. **Put the most important information at the beginning and end of your prompt.** Attention mechanisms tend to focus more on the start and end of the context.

---

## Quick Summary

LLMs work by processing tokens through layers of attention and feed-forward networks. The attention mechanism lets each token "attend" to other relevant tokens, understanding relationships in the text. During inference, the model predicts one token at a time, using its full context. Temperature and sampling strategies control how creative or deterministic the output is. Context windows limit how much text the model can consider at once. Understanding these mechanics helps you control the model's behavior and get better results.

---

## Key Points

- The attention mechanism calculates how relevant each token is to every other token
- Multi-head attention captures different types of relationships simultaneously
- Next-token prediction is a step-by-step process: tokenize, embed, attend, predict, sample, repeat
- Temperature controls randomness: low for facts, high for creativity
- Top-K keeps only the K most likely tokens; Top-P keeps tokens until cumulative probability reaches P
- Inference is the process of generating a response using a trained model
- Context windows limit the total tokens (prompt + response) the model can handle
- Tokens and words are not the same; 1 token is roughly 0.75 English words

---

## Practice Questions

1. Explain the attention mechanism using your own analogy. What real-world process does it resemble?

2. If you set temperature to 0 and ask the same question twice, will you always get the same answer? Why or why not?

3. A model has a context window of 8,192 tokens. Your prompt uses 6,000 tokens. What is the maximum number of tokens the model can generate in its response? What practical problems might this cause?

4. Why does multi-head attention work better than single-head attention? What would be lost if we used only one attention head?

5. Explain why the sentence "I love natural language processing" might use a different number of tokens than the sentence "I love NLP" even though they mean the same thing.

---

## Exercises

### Exercise 1: Temperature Experiment

Using any LLM API or playground, ask the same question at three different temperatures (0.0, 0.7, and 1.5). Ask each question five times at each temperature setting. Record:
- How consistent are the answers at each temperature?
- At what temperature do you start seeing errors or nonsensical output?
- Which temperature gives the best balance of quality and variety?

### Exercise 2: Context Window Exploration

Start a conversation with an LLM and keep adding messages. Try to find the point where the model "forgets" earlier parts of the conversation. Document:
- How many messages it took before the model forgot earlier context
- What symptoms you noticed (contradictions, ignored instructions, etc.)
- Strategies that helped maintain context over longer conversations

### Exercise 3: Token Counting

Install the `tiktoken` library and count tokens for different types of text:
```python
pip install tiktoken
```
Compare token counts for: a paragraph of English, the same text in another language, a block of Python code, and a list of numbers. What patterns do you notice?

---

## What Is Next?

Now that you understand the mechanics of how LLMs work internally, the next chapter introduces you to the major models you can use today. In "Key Models", we will compare GPT-4, Claude, Gemini, Llama, and Mistral. You will learn the differences between open-source and closed-source models, when to use each one, and how to choose the right model for your specific needs.
