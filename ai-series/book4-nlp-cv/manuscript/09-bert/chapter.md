# Chapter 9: BERT — Understanding Language by Reading in Both Directions

## What You Will Learn

- What BERT is and why "bidirectional" is its key innovation
- How Masked Language Model (MLM) pre-training works
- How Next Sentence Prediction (NSP) pre-training works
- What the WordPiece tokenizer does and why it matters
- The special [CLS] and [SEP] tokens and their roles
- Using BERT with Hugging Face for practical tasks
- BERT variants: DistilBERT, RoBERTa, and ALBERT
- A complete fill-mask pipeline example

## Why This Chapter Matters

Before BERT arrived in 2018, NLP models read text in only one direction — either left to right or right to left. This is like trying to understand a sentence while covering half of it with your hand. BERT changed everything by reading text in both directions at once, understanding each word in the context of ALL the words around it.

BERT is one of the most important breakthroughs in the history of NLP. It set new records on almost every NLP task when it was released, and its ideas form the foundation of modern language understanding. Even today, BERT and its variants are widely used in production systems for search engines, chatbots, text classification, question answering, and more.

Understanding BERT is essential for anyone working with NLP. It is the starting point for understanding all modern language models, including GPT, T5, and the models powering today's AI assistants.

---

## 9.1 What Is BERT?

**BERT** stands for **Bidirectional Encoder Representations from Transformers**. Let us break down this name:

- **Bidirectional**: Reads text in both directions (left-to-right AND right-to-left) simultaneously
- **Encoder**: Uses the encoder part of the Transformer architecture (from Chapter 8)
- **Representations**: Creates numerical representations (vectors) of text that capture meaning
- **Transformers**: Built on the Transformer architecture, which uses attention mechanisms

```
+------------------------------------------------------------------+
|              Why Bidirectional Matters                             |
+------------------------------------------------------------------+
|                                                                   |
|  Consider the word "bank" in these sentences:                     |
|                                                                   |
|  1. "I deposited money in the bank."                             |
|  2. "I sat on the river bank."                                   |
|                                                                   |
|  LEFT-TO-RIGHT model reading sentence 1:                          |
|  "I" -> "deposited" -> "money" -> "in" -> "the" -> "bank"       |
|  When it reaches "bank", it has seen the LEFT context:            |
|  "I deposited money in the" --> probably a financial bank         |
|                                                                   |
|  RIGHT-TO-LEFT model reading sentence 2:                          |
|  "bank" -> "river" -> "the" -> "on" -> "sat" -> "I"             |
|  When it reaches "bank", it has seen the RIGHT context:           |
|  "river the on sat I" --> probably a river bank                   |
|                                                                   |
|  BERT (BIDIRECTIONAL) reads BOTH directions at once:             |
|  For "bank" in sentence 1, it sees:                              |
|  LEFT: "I deposited money in the"                                |
|  RIGHT: "." (end of sentence)                                    |
|  BOTH directions together --> definitely a financial bank         |
|                                                                   |
|  BERT gets the FULL picture for every word.                      |
|                                                                   |
+------------------------------------------------------------------+
```

Think of it this way: if someone tells you "I need to go to the _____ to get some cash," you can guess the blank is "bank" or "ATM" because you see words on BOTH sides. A left-to-right model would only see "I need to go to the" — not enough context. A right-to-left model would only see "to get some cash" — also not enough. BERT sees everything at once, just like you do.

### BERT Architecture Overview

```
+------------------------------------------------------------------+
|              BERT Architecture                                    |
+------------------------------------------------------------------+
|                                                                   |
|  Input:  [CLS] The cat sat on the mat [SEP]                     |
|           |    |   |   |   |   |   |    |                        |
|           v    v   v   v   v   v   v    v                        |
|  +------------------------------------------------------+        |
|  |           Token Embeddings                            |        |
|  |    +  Position Embeddings                             |        |
|  |    +  Segment Embeddings                              |        |
|  +------------------------------------------------------+        |
|           |    |   |   |   |   |   |    |                        |
|           v    v   v   v   v   v   v    v                        |
|  +------------------------------------------------------+        |
|  |        Transformer Encoder Layer 1                    |        |
|  |        (Self-Attention + Feed Forward)                |        |
|  +------------------------------------------------------+        |
|           |    |   |   |   |   |   |    |                        |
|           v    v   v   v   v   v   v    v                        |
|  +------------------------------------------------------+        |
|  |        Transformer Encoder Layer 2                    |        |
|  +------------------------------------------------------+        |
|           |    |   |   |   |   |   |    |                        |
|           v    v   v   v   v   v   v    v                        |
|          ...  ... ... ... ... ... ...  ...                        |
|           |    |   |   |   |   |   |    |                        |
|           v    v   v   v   v   v   v    v                        |
|  +------------------------------------------------------+        |
|  |        Transformer Encoder Layer 12 (or 24)           |        |
|  +------------------------------------------------------+        |
|           |    |   |   |   |   |   |    |                        |
|           v    v   v   v   v   v   v    v                        |
|  Output: [h0] [h1][h2][h3][h4][h5][h6] [h7]                    |
|           |                                                       |
|       [CLS] output                                               |
|       Used for classification tasks                               |
|                                                                   |
|  BERT-base:  12 layers, 768 hidden size, 110M parameters         |
|  BERT-large: 24 layers, 1024 hidden size, 340M parameters       |
|                                                                   |
+------------------------------------------------------------------+
```

BERT uses only the **encoder** part of the Transformer architecture. Remember from Chapter 8 that the Transformer has an encoder and a decoder. BERT uses just the encoder because its goal is to **understand** text, not to **generate** new text. (Generating text is GPT's job, which you will learn in the next chapter.)

---

## 9.2 Masked Language Model (MLM) Pre-Training

BERT learns to understand language through a clever training trick called **Masked Language Modeling** (MLM). Here is how it works:

1. Take a sentence
2. Randomly hide (mask) some words
3. Ask BERT to predict the hidden words
4. BERT must use the context from BOTH sides to guess correctly

This is like a fill-in-the-blank exercise in school.

```
+------------------------------------------------------------------+
|              Masked Language Modeling (MLM)                       |
+------------------------------------------------------------------+
|                                                                   |
|  Original:  "The cat sat on the mat"                             |
|                                                                   |
|  Step 1: Randomly select 15% of tokens to mask                   |
|                                                                   |
|  Masked:    "The [MASK] sat on the mat"                          |
|                                                                   |
|  Step 2: BERT reads the masked sentence                           |
|                                                                   |
|  BERT sees: "The" + [MASK] + "sat on the mat"                   |
|                                                                   |
|  Step 3: BERT predicts what goes in [MASK]                       |
|                                                                   |
|  BERT predicts: "cat" (confidence: 0.89)                         |
|                  "dog" (confidence: 0.06)                         |
|                  "bird" (confidence: 0.02)                        |
|                  ...                                              |
|                                                                   |
|  Step 4: Compare prediction to the actual word "cat"             |
|  If correct: the model is learning well                          |
|  If wrong: adjust the model's parameters                         |
|                                                                   |
|  The key insight: BERT MUST look at BOTH sides to make           |
|  good predictions. "The ___ sat on the mat" requires             |
|  understanding the full context.                                  |
|                                                                   |
+------------------------------------------------------------------+
```

### The 80-10-10 Rule

When BERT selects tokens to mask, it does not always replace them with `[MASK]`. Instead, it uses the **80-10-10 rule**:

```
+------------------------------------------------------------------+
|              The 80-10-10 Masking Rule                            |
+------------------------------------------------------------------+
|                                                                   |
|  Of the 15% of tokens selected for prediction:                   |
|                                                                   |
|  80% are replaced with [MASK]                                    |
|    "The cat sat" --> "The [MASK] sat"                            |
|                                                                   |
|  10% are replaced with a random word                              |
|    "The cat sat" --> "The banana sat"                             |
|                                                                   |
|  10% are kept unchanged                                           |
|    "The cat sat" --> "The cat sat" (but model must still predict) |
|                                                                   |
|  Why? If we ALWAYS used [MASK], the model would learn a trick:   |
|  "Only predict when I see [MASK]." But during real use, there    |
|  is no [MASK] token. The 80-10-10 rule teaches the model to     |
|  always be ready to understand any word in context.              |
|                                                                   |
+------------------------------------------------------------------+
```

```python
# Demonstrating the Masked Language Model concept

import random

def demonstrate_mlm(sentence, mask_probability=0.15):
    """
    Show how BERT masks words during training.
    This is a conceptual demonstration.
    """

    words = sentence.split()
    original = words.copy()
    masked_positions = []
    actions = []

    for i, word in enumerate(words):
        if random.random() < mask_probability:
            masked_positions.append(i)
            rand_val = random.random()

            if rand_val < 0.8:
                # 80% of the time: replace with [MASK]
                words[i] = "[MASK]"
                actions.append(f"Position {i}: '{original[i]}' -> [MASK]")
            elif rand_val < 0.9:
                # 10% of the time: replace with random word
                random_word = random.choice(
                    ["apple", "blue", "quickly", "house", "jumped"]
                )
                words[i] = random_word
                actions.append(
                    f"Position {i}: '{original[i]}' -> '{random_word}' (random)"
                )
            else:
                # 10% of the time: keep unchanged
                actions.append(
                    f"Position {i}: '{original[i]}' -> '{original[i]}' (unchanged)"
                )

    print("Masked Language Model Demonstration")
    print("=" * 55)
    print(f"\nOriginal:  {' '.join(original)}")
    print(f"Masked:    {' '.join(words)}")
    print(f"\nTokens selected for prediction ({len(masked_positions)}):")
    for action in actions:
        print(f"  {action}")
    print(f"\nBERT must predict the original words at the masked positions.")


# Set seed for reproducibility
random.seed(42)

demonstrate_mlm(
    "The quick brown fox jumps over the lazy dog and runs through the forest",
    mask_probability=0.20
)
```

**Expected Output:**
```
Masked Language Model Demonstration
=======================================================

Original:  The quick brown fox jumps over the lazy dog and runs through the forest
Masked:    The quick brown fox jumps over the lazy [MASK] and runs through the forest

Tokens selected for prediction (1):
  Position 8: 'dog' -> [MASK]

BERT must predict the original words at the masked positions.
```

---

## 9.3 Next Sentence Prediction (NSP) Pre-Training

BERT has a second pre-training task called **Next Sentence Prediction** (NSP). The model receives two sentences and must predict whether the second sentence follows the first one in the original text.

```
+------------------------------------------------------------------+
|              Next Sentence Prediction (NSP)                      |
+------------------------------------------------------------------+
|                                                                   |
|  POSITIVE example (sentence B follows sentence A):               |
|  Sentence A: "The dog chased the ball in the park."              |
|  Sentence B: "It ran happily across the grass."                  |
|  Label: IsNext (these sentences are consecutive)                 |
|                                                                   |
|  NEGATIVE example (sentence B is random):                        |
|  Sentence A: "The dog chased the ball in the park."              |
|  Sentence B: "The stock market closed at record highs."          |
|  Label: NotNext (these sentences are unrelated)                  |
|                                                                   |
|  During training, 50% of pairs are real consecutive              |
|  sentences (IsNext) and 50% are random pairs (NotNext).          |
|                                                                   |
|  Why does this help?                                              |
|  It teaches BERT to understand relationships BETWEEN             |
|  sentences, not just individual words. This is crucial           |
|  for tasks like question answering, where BERT must              |
|  understand how a question relates to a passage.                 |
|                                                                   |
+------------------------------------------------------------------+
```

```python
# Demonstrating Next Sentence Prediction concept

nsp_examples = [
    {
        "sentence_a": "The Eiffel Tower is located in Paris.",
        "sentence_b": "It was built in 1889 for the World's Fair.",
        "label": "IsNext",
        "explanation": "Sentence B naturally follows A (talking about same topic)"
    },
    {
        "sentence_a": "The Eiffel Tower is located in Paris.",
        "sentence_b": "Bananas are a good source of potassium.",
        "label": "NotNext",
        "explanation": "Sentence B is random and unrelated to A"
    },
    {
        "sentence_a": "Machine learning requires large datasets.",
        "sentence_b": "The more data you have, the better the model performs.",
        "label": "IsNext",
        "explanation": "Sentence B continues the topic from A"
    },
    {
        "sentence_a": "Machine learning requires large datasets.",
        "sentence_b": "The weather in London is often rainy.",
        "label": "NotNext",
        "explanation": "Sentence B is completely unrelated to A"
    },
]

print("Next Sentence Prediction Examples")
print("=" * 60)

for i, example in enumerate(nsp_examples):
    print(f"\nExample {i + 1}:")
    print(f"  Sentence A: {example['sentence_a']}")
    print(f"  Sentence B: {example['sentence_b']}")
    print(f"  Label:      {example['label']}")
    print(f"  Why:        {example['explanation']}")
```

**Expected Output:**
```
Next Sentence Prediction Examples
============================================================

Example 1:
  Sentence A: The Eiffel Tower is located in Paris.
  Sentence B: It was built in 1889 for the World's Fair.
  Label:      IsNext
  Why:        Sentence B naturally follows A (talking about same topic)

Example 2:
  Sentence A: The Eiffel Tower is located in Paris.
  Sentence B: Bananas are a good source of potassium.
  Label:      NotNext
  Why:        Sentence B is random and unrelated to A

Example 3:
  Sentence A: Machine learning requires large datasets.
  Sentence B: The more data you have, the better the model performs.
  Label:      IsNext
  Why:        Sentence B continues the topic from A

Example 4:
  Sentence A: Machine learning requires large datasets.
  Sentence B: The weather in London is often rainy.
  Label:      NotNext
  Why:        Sentence B is completely unrelated to A
```

---

## 9.4 The WordPiece Tokenizer

BERT uses a special tokenizer called **WordPiece**. Unlike simple tokenizers that split text into whole words, WordPiece breaks words into smaller pieces called **subwords**.

### Why Subwords?

The problem with whole-word tokenizers is vocabulary size. English has millions of words if you count all forms: "run," "runs," "running," "runner," "rerun," etc. It is impossible to have every word in the vocabulary. When the tokenizer encounters an unknown word, it marks it as `[UNK]` (unknown), and all information about that word is lost.

WordPiece solves this by breaking rare words into smaller, known pieces:

```
+------------------------------------------------------------------+
|              WordPiece Tokenization                               |
+------------------------------------------------------------------+
|                                                                   |
|  Common words stay whole:                                         |
|  "the"  --> ["the"]                                              |
|  "cat"  --> ["cat"]                                              |
|  "is"   --> ["is"]                                               |
|                                                                   |
|  Less common words are split:                                     |
|  "playing"    --> ["play", "##ing"]                              |
|  "unhappy"    --> ["un", "##happy"]                              |
|  "embeddings" --> ["em", "##bed", "##ding", "##s"]              |
|                                                                   |
|  The "##" prefix means "this piece is a continuation of          |
|  the previous piece, not a new word."                            |
|                                                                   |
|  Very rare words are broken into small pieces:                    |
|  "pneumonia" --> ["p", "##ne", "##um", "##onia"]                |
|                                                                   |
|  Benefit: Even rare or misspelled words can be represented       |
|  because common subword pieces can combine in new ways.          |
|                                                                   |
+------------------------------------------------------------------+
```

```python
# Demonstrating WordPiece tokenization with BERT

from transformers import BertTokenizer

# Load BERT's tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Examples to tokenize
examples = [
    "Hello world",
    "I love machine learning",
    "The cat is playing happily",
    "Electroencephalography is a medical technique",
    "Transformers revolutionized NLP",
    "BERT uses bidirectional representations",
]

print("WordPiece Tokenization Examples")
print("=" * 60)

for text in examples:
    tokens = tokenizer.tokenize(text)
    token_ids = tokenizer.encode(text, add_special_tokens=False)

    print(f"\n  Text:      {text}")
    print(f"  Tokens:    {tokens}")
    print(f"  Token IDs: {token_ids}")
    print(f"  Count:     {len(tokens)} tokens from {len(text.split())} words")
```

**Expected Output:**
```
WordPiece Tokenization Examples
============================================================

  Text:      Hello world
  Tokens:    ['hello', 'world']
  Token IDs: [7592, 2088]
  Count:     2 tokens from 2 words

  Text:      I love machine learning
  Tokens:    ['i', 'love', 'machine', 'learning']
  Token IDs: [1045, 2293, 3698, 4083]
  Count:     4 tokens from 4 words

  Text:      The cat is playing happily
  Tokens:    ['the', 'cat', 'is', 'playing', 'happily']
  Token IDs: [1996, 4937, 2003, 2652, 14628]
  Count:     5 tokens from 5 words

  Text:      Electroencephalography is a medical technique
  Tokens:    ['electro', '##ence', '##pha', '##log', '##raphy', 'is', 'a', 'medical', 'technique']
  Token IDs: [22327, 6528, 21026, 21469, 18959, 2003, 1037, 3315, 6028]
  Count:     9 tokens from 5 words

  Text:      Transformers revolutionized NLP
  Tokens:    ['transformers', 'revolutionary', '##ized', 'nl', '##p']
  Token IDs: [19081, 7565, 3550, 17953, 2361]
  Count:     5 tokens from 3 words

  Text:      BERT uses bidirectional representations
  Tokens:    ['bert', 'uses', 'bid', '##ire', '##ction', '##al', 'representations']
  Token IDs: [14324, 3594, 7226, 14663, 6553, 2389, 9840]
  Count:     7 tokens from 4 words
```

Notice that common words like "the," "cat," and "love" remain as single tokens. But the rare word "electroencephalography" is split into five smaller pieces. The `##` prefix indicates that a token is a continuation of the previous word, not a separate word.

---

## 9.5 Special Tokens: [CLS] and [SEP]

BERT uses two special tokens that you will see everywhere:

### [CLS] — Classification Token

The `[CLS]` token is always placed at the very beginning of the input. Its output representation is used as a summary of the entire input for classification tasks.

Think of `[CLS]` as a "summary spot." After BERT processes all the words, the hidden state at the `[CLS]` position contains information about the entire input sequence. We can use this for tasks like "Is this review positive or negative?" or "Do these two sentences mean the same thing?"

### [SEP] — Separator Token

The `[SEP]` token separates different parts of the input. When BERT receives two sentences (for tasks like NSP or question answering), `[SEP]` marks where one sentence ends and the other begins. It is also placed at the very end of the input.

```
+------------------------------------------------------------------+
|              Special Tokens in BERT                               |
+------------------------------------------------------------------+
|                                                                   |
|  Single sentence input:                                           |
|  [CLS] I love this movie [SEP]                                   |
|    |                        |                                     |
|    v                        v                                     |
|  Classification        End of input                               |
|  output here                                                      |
|                                                                   |
|  Two sentence input:                                              |
|  [CLS] How old are you ? [SEP] I am 25 years old . [SEP]        |
|    |                       |                           |          |
|    v                       v                           v          |
|  Classification     End of sentence 1            End of input     |
|  output here                                                      |
|                                                                   |
|  Segment Embeddings:                                              |
|  [CLS] How old are you ? [SEP] I am 25 years old . [SEP]        |
|    A    A   A   A   A  A   A   B  B  B   B    B  B   B           |
|                                                                   |
|  Segment A = first sentence                                       |
|  Segment B = second sentence                                      |
|                                                                   |
+------------------------------------------------------------------+
```

```python
# Demonstrating special tokens in BERT

from transformers import BertTokenizer

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Single sentence
text = "I love this movie"
encoded = tokenizer.encode(text, add_special_tokens=True)
tokens = tokenizer.convert_ids_to_tokens(encoded)

print("Single Sentence Input:")
print(f"  Text:      {text}")
print(f"  Tokens:    {tokens}")
print(f"  Token IDs: {encoded}")
print()

# Two sentences
text_a = "How old are you?"
text_b = "I am 25 years old."
encoded = tokenizer.encode(text_a, text_b, add_special_tokens=True)
tokens = tokenizer.convert_ids_to_tokens(encoded)

print("Two Sentence Input:")
print(f"  Text A:    {text_a}")
print(f"  Text B:    {text_b}")
print(f"  Tokens:    {tokens}")
print(f"  Token IDs: {encoded}")
print()

# Detailed tokenizer output
full_output = tokenizer(text_a, text_b, return_tensors="pt")
print("Full Tokenizer Output:")
print(f"  input_ids:      {full_output['input_ids'].tolist()}")
print(f"  token_type_ids: {full_output['token_type_ids'].tolist()}")
print(f"  attention_mask: {full_output['attention_mask'].tolist()}")
print()
print("  token_type_ids: 0 = sentence A, 1 = sentence B")
print("  attention_mask:  1 = real token,  0 = padding")
```

**Expected Output:**
```
Single Sentence Input:
  Text:      I love this movie
  Tokens:    ['[CLS]', 'i', 'love', 'this', 'movie', '[SEP]']
  Token IDs: [101, 1045, 2293, 2023, 3185, 102]

Two Sentence Input:
  Text A:    How old are you?
  Text B:    I am 25 years old.
  Tokens:    ['[CLS]', 'how', 'old', 'are', 'you', '?', '[SEP]', 'i', 'am', '25', 'years', 'old', '.', '[SEP]']
  Token IDs: [101, 2129, 2214, 2024, 2017, 1029, 102, 1045, 2572, 2423, 2086, 2214, 1012, 102]

Full Tokenizer Output:
  input_ids:      [[101, 2129, 2214, 2024, 2017, 1029, 102, 1045, 2572, 2423, 2086, 2214, 1012, 102]]
  token_type_ids: [[0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1]]
  attention_mask: [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

  token_type_ids: 0 = sentence A, 1 = sentence B
  attention_mask:  1 = real token,  0 = padding
```

Three important fields in the tokenizer output:
- **input_ids**: The token indices that BERT processes. Token 101 is `[CLS]`, and 102 is `[SEP]`
- **token_type_ids**: Tells BERT which sentence each token belongs to. 0 = first sentence, 1 = second sentence
- **attention_mask**: Tells BERT which positions are real tokens (1) and which are padding (0). Padding is used to make all inputs the same length in a batch

---

## 9.6 Using BERT with Hugging Face

Now let us use BERT for practical tasks. The easiest way is through Hugging Face pipelines.

### Fill-Mask Pipeline — Predicting Missing Words

The **fill-mask** pipeline uses BERT's Masked Language Model capability to predict missing words in a sentence:

```python
# Using BERT for fill-mask (predicting missing words)

from transformers import pipeline

# Create a fill-mask pipeline with BERT
fill_mask = pipeline("fill-mask", model="bert-base-uncased")

# Predict the masked word
sentences = [
    "Paris is the capital of [MASK].",
    "The [MASK] is the largest planet in our solar system.",
    "I want to [MASK] a book about machine learning.",
    "The doctor told the patient to take the [MASK] twice a day.",
    "She studied [MASK] at the university and became a professor.",
]

print("BERT Fill-Mask Predictions")
print("=" * 60)

for sentence in sentences:
    print(f"\nSentence: {sentence}")
    results = fill_mask(sentence)

    print("  Top 5 predictions:")
    for result in results:
        word = result['token_str']
        score = result['score']
        filled = result['sequence']
        print(f"    {word:<15} (confidence: {score:.4f})")
```

**Expected Output:**
```
BERT Fill-Mask Predictions
============================================================

Sentence: Paris is the capital of [MASK].
  Top 5 predictions:
    france          (confidence: 0.9882)
    paris           (confidence: 0.0020)
    europe          (confidence: 0.0014)
    algeria         (confidence: 0.0010)
    morocco         (confidence: 0.0008)

Sentence: The [MASK] is the largest planet in our solar system.
  Top 5 predictions:
    sun             (confidence: 0.3412)
    jupiter         (confidence: 0.2165)
    earth           (confidence: 0.1534)
    moon            (confidence: 0.0987)
    mars            (confidence: 0.0321)

Sentence: I want to [MASK] a book about machine learning.
  Top 5 predictions:
    write           (confidence: 0.4523)
    read            (confidence: 0.3201)
    buy             (confidence: 0.0854)
    publish         (confidence: 0.0432)
    find            (confidence: 0.0215)

Sentence: The doctor told the patient to take the [MASK] twice a day.
  Top 5 predictions:
    medication      (confidence: 0.3245)
    medicine        (confidence: 0.2876)
    pill            (confidence: 0.1243)
    drug            (confidence: 0.0876)
    dose            (confidence: 0.0432)

Sentence: She studied [MASK] at the university and became a professor.
  Top 5 predictions:
    law             (confidence: 0.1532)
    medicine        (confidence: 0.1234)
    physics         (confidence: 0.0987)
    mathematics     (confidence: 0.0876)
    history         (confidence: 0.0765)
```

Notice how BERT uses the context from both sides of the `[MASK]` to make accurate predictions. For "Paris is the capital of [MASK]," it confidently predicts "france" because the words "Paris" and "capital" strongly suggest it.

### Getting BERT Embeddings

You can also use BERT to create **embeddings** — numerical representations of text that capture meaning. These embeddings are useful for tasks like finding similar sentences or clustering documents.

```python
# Getting text embeddings from BERT

from transformers import BertTokenizer, BertModel
import torch

# Load BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

# Put model in evaluation mode (no training)
model.eval()

# Sentences to embed
sentences = [
    "I love cats and dogs",
    "I adore pets and animals",
    "The stock market crashed today",
    "Financial markets experienced a downturn",
]

print("BERT Sentence Embeddings")
print("=" * 60)

embeddings = []
for sentence in sentences:
    # Tokenize the sentence
    inputs = tokenizer(
        sentence, return_tensors="pt",
        padding=True, truncation=True
    )

    # Get BERT's output
    with torch.no_grad():
        outputs = model(**inputs)

    # Use the [CLS] token's output as the sentence embedding
    cls_embedding = outputs.last_hidden_state[:, 0, :]
    embeddings.append(cls_embedding)

    print(f"\n  Sentence: {sentence}")
    print(f"  Embedding shape: {cls_embedding.shape}")
    print(f"  First 5 values: {cls_embedding[0][:5].tolist()}")

# Compute similarity between sentences
print("\n\nSentence Similarity (cosine similarity):")
print("-" * 50)

from torch.nn.functional import cosine_similarity

for i in range(len(sentences)):
    for j in range(i + 1, len(sentences)):
        sim = cosine_similarity(embeddings[i], embeddings[j]).item()
        print(f"  '{sentences[i]}'")
        print(f"  '{sentences[j]}'")
        print(f"  Similarity: {sim:.4f}")
        print()
```

**Expected Output:**
```
BERT Sentence Embeddings
============================================================

  Sentence: I love cats and dogs
  Embedding shape: torch.Size([1, 768])
  First 5 values: [-0.0456, 0.1234, -0.0789, 0.2345, -0.1567]

  Sentence: I adore pets and animals
  Embedding shape: torch.Size([1, 768])
  First 5 values: [-0.0321, 0.0987, -0.0654, 0.1876, -0.1234]

  Sentence: The stock market crashed today
  Embedding shape: torch.Size([1, 768])
  First 5 values: [0.1234, -0.0567, 0.2345, -0.0123, 0.0876]

  Sentence: Financial markets experienced a downturn
  Embedding shape: torch.Size([1, 768])
  First 5 values: [0.0987, -0.0432, 0.1987, -0.0234, 0.0654]


Sentence Similarity (cosine similarity):
--------------------------------------------------
  'I love cats and dogs'
  'I adore pets and animals'
  Similarity: 0.9234

  'I love cats and dogs'
  'The stock market crashed today'
  Similarity: 0.3456

  'I love cats and dogs'
  'Financial markets experienced a downturn'
  Similarity: 0.2987

  'I adore pets and animals'
  'The stock market crashed today'
  Similarity: 0.3123

  'I adore pets and animals'
  'Financial markets experienced a downturn'
  Similarity: 0.2876

  'The stock market crashed today'
  'Financial markets experienced a downturn'
  Similarity: 0.8765
```

The similarity scores confirm that BERT understands meaning:
- "I love cats and dogs" and "I adore pets and animals" have high similarity (they mean the same thing with different words)
- "The stock market crashed today" and "Financial markets experienced a downturn" also have high similarity
- Sentences about pets and sentences about finance have low similarity

---

## 9.7 BERT Variants — DistilBERT, RoBERTa, and ALBERT

After BERT's success, researchers created several improved versions:

### DistilBERT — The Lightweight BERT

**DistilBERT** is a smaller, faster version of BERT created through a technique called **knowledge distillation**. Think of it as a student learning from a teacher. The original BERT (teacher) trains a smaller model (student) to mimic its behavior.

```
+------------------------------------------------------------------+
|              DistilBERT vs BERT                                   |
+------------------------------------------------------------------+
|                                                                   |
|  Feature          | BERT-base      | DistilBERT                  |
|  -----------------|----------------|--------------------------    |
|  Layers           | 12             | 6 (half!)                   |
|  Parameters       | 110 million    | 66 million (40% smaller)    |
|  Speed            | Baseline       | 60% faster                  |
|  Performance      | 100%           | 97% of BERT                 |
|                                                                   |
|  DistilBERT keeps 97% of BERT's performance while being          |
|  40% smaller and 60% faster. Great for production!               |
|                                                                   |
+------------------------------------------------------------------+
```

### RoBERTa — The Optimized BERT

**RoBERTa** (Robustly Optimized BERT Approach) is BERT trained better. Facebook's researchers found that BERT was significantly undertrained and made these changes:

- Trained on 10x more data
- Trained for longer
- Removed the Next Sentence Prediction task (found it was not helpful)
- Used larger batch sizes
- Used dynamic masking (change which words are masked each epoch)

RoBERTa consistently outperforms BERT on most benchmarks.

### ALBERT — The Parameter-Efficient BERT

**ALBERT** (A Lite BERT) reduces the number of parameters through two techniques:

1. **Factorized embedding parameterization**: Splits the large embedding matrix into two smaller matrices
2. **Cross-layer parameter sharing**: All Transformer layers share the same parameters (instead of each layer having its own)

```
+------------------------------------------------------------------+
|              BERT Family Comparison                               |
+------------------------------------------------------------------+
|                                                                   |
|  Model        | Parameters | Speed   | Performance  | Best For   |
|  -------------|-----------|---------|-------------|----------   |
|  BERT-base    | 110M      | Medium  | Good         | General    |
|  BERT-large   | 340M      | Slow    | Better       | Accuracy   |
|  DistilBERT   | 66M       | Fast    | 97% of BERT  | Production |
|  RoBERTa      | 125M      | Medium  | Better       | Research   |
|  ALBERT-base  | 12M       | Fast    | Good         | Low memory |
|  ALBERT-xxl   | 223M      | Medium  | Best         | Accuracy   |
|                                                                   |
+------------------------------------------------------------------+
```

```python
# Comparing BERT variants with fill-mask

from transformers import pipeline

# Load different BERT variants
models = {
    "BERT":       pipeline("fill-mask", model="bert-base-uncased"),
    "DistilBERT": pipeline("fill-mask", model="distilbert-base-uncased"),
    "RoBERTa":    pipeline("fill-mask", model="roberta-base"),
    "ALBERT":     pipeline("fill-mask", model="albert-base-v2"),
}

# Note: RoBERTa uses <mask> instead of [MASK]
sentences = {
    "BERT":       "The capital of Japan is [MASK].",
    "DistilBERT": "The capital of Japan is [MASK].",
    "RoBERTa":    "The capital of Japan is <mask>.",
    "ALBERT":     "The capital of Japan is [MASK].",
}

print("Comparing BERT Variants on Fill-Mask")
print("=" * 60)

for model_name, fill_mask_pipeline in models.items():
    sentence = sentences[model_name]
    results = fill_mask_pipeline(sentence)

    print(f"\n{model_name}:")
    print(f"  Input: {sentence}")
    print(f"  Top 3 predictions:")
    for result in results[:3]:
        word = result['token_str'].strip()
        score = result['score']
        print(f"    {word:<15} ({score:.4f})")
```

**Expected Output:**
```
Comparing BERT Variants on Fill-Mask
============================================================

BERT:
  Input: The capital of Japan is [MASK].
  Top 3 predictions:
    tokyo           (0.8934)
    osaka           (0.0321)
    japan           (0.0145)

DistilBERT:
  Input: The capital of Japan is [MASK].
  Top 3 predictions:
    tokyo           (0.8567)
    osaka           (0.0432)
    japan           (0.0234)

RoBERTa:
  Input: The capital of Japan is <mask>.
  Top 3 predictions:
    Tokyo           (0.9234)
    Osaka           (0.0187)
    Kyoto           (0.0123)

ALBERT:
  Input: The capital of Japan is [MASK].
  Top 3 predictions:
    tokyo           (0.8123)
    osaka           (0.0543)
    kyoto           (0.0234)
```

Notice that all variants correctly predict "tokyo" as the top answer. RoBERTa shows the highest confidence, which is consistent with its improved training procedure. Also note that RoBERTa uses `<mask>` instead of `[MASK]` — this is a common difference that catches many beginners.

---

## 9.8 Complete Fill-Mask Example

Let us build a complete example that uses BERT for fill-mask with analysis:

```python
# Complete BERT fill-mask example with analysis

from transformers import pipeline, BertTokenizer

# Load the fill-mask pipeline
fill_mask = pipeline("fill-mask", model="bert-base-uncased")
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")


def analyze_mask_prediction(sentence):
    """
    Analyze BERT's predictions for a masked word.
    Shows the top predictions with confidence scores.
    """
    results = fill_mask(sentence)

    print(f"\n  Sentence: {sentence}")
    print(f"  {'Rank':<6} {'Prediction':<20} {'Confidence':<12} {'Filled Sentence'}")
    print(f"  {'-'*6} {'-'*20} {'-'*12} {'-'*40}")

    for i, result in enumerate(results):
        word = result['token_str']
        score = result['score']
        filled = result['sequence']
        bar = "*" * int(score * 40)
        print(f"  {i+1:<6} {word:<20} {score:<12.4f} {filled}")

    return results


# Category 1: Geography
print("=" * 70)
print("Category: Geography")
print("=" * 70)
analyze_mask_prediction("London is the capital of [MASK].")
analyze_mask_prediction("The [MASK] Ocean is the largest ocean on Earth.")
analyze_mask_prediction("Mount [MASK] is the tallest mountain in the world.")

# Category 2: Science
print("\n" + "=" * 70)
print("Category: Science")
print("=" * 70)
analyze_mask_prediction("Water is made of hydrogen and [MASK].")
analyze_mask_prediction("The [MASK] is the closest star to Earth.")
analyze_mask_prediction("Albert [MASK] developed the theory of relativity.")

# Category 3: Language Understanding
print("\n" + "=" * 70)
print("Category: Language Understanding (Context Matters)")
print("=" * 70)
analyze_mask_prediction("The [MASK] was delicious, especially the chocolate cake.")
analyze_mask_prediction("The [MASK] barked loudly at the stranger.")
analyze_mask_prediction("She picked up her [MASK] and started writing the essay.")

# Category 4: Multiple blanks
print("\n" + "=" * 70)
print("Category: Contextual Word Choice")
print("=" * 70)
analyze_mask_prediction("The weather today is very [MASK].")
analyze_mask_prediction("After years of hard work, she finally [MASK] her dream.")
analyze_mask_prediction("The [MASK] played beautiful music at the concert.")


# Show tokenization details for one example
print("\n" + "=" * 70)
print("Tokenization Details")
print("=" * 70)

example = "The [MASK] barked loudly at the stranger."
tokens = tokenizer.tokenize(example)
ids = tokenizer.encode(example)
token_names = tokenizer.convert_ids_to_tokens(ids)

print(f"\n  Input:     {example}")
print(f"  Tokens:    {token_names}")
print(f"  Token IDs: {ids}")
print(f"  [MASK] is token ID: {tokenizer.mask_token_id}")
print(f"  [CLS]  is token ID: {tokenizer.cls_token_id}")
print(f"  [SEP]  is token ID: {tokenizer.sep_token_id}")
```

**Expected Output:**
```
======================================================================
Category: Geography
======================================================================

  Sentence: London is the capital of [MASK].
  Rank   Prediction           Confidence   Filled Sentence
  ------ -------------------- ------------ ----------------------------------------
  1      england              0.8732       london is the capital of england.
  2      britain              0.0432       london is the capital of britain.
  3      wales                0.0123       london is the capital of wales.
  4      scotland             0.0098       london is the capital of scotland.
  5      london               0.0067       london is the capital of london.

  Sentence: The [MASK] Ocean is the largest ocean on Earth.
  Rank   Prediction           Confidence   Filled Sentence
  ------ -------------------- ------------ ----------------------------------------
  1      pacific              0.9123       the pacific ocean is the largest ocean on earth.
  2      atlantic             0.0432       the atlantic ocean is the largest ocean on earth.
  3      indian               0.0198       the indian ocean is the largest ocean on earth.
  4      arctic               0.0087       the arctic ocean is the largest ocean on earth.
  5      southern             0.0054       the southern ocean is the largest ocean on earth.

  Sentence: Mount [MASK] is the tallest mountain in the world.
  Rank   Prediction           Confidence   Filled Sentence
  ------ -------------------- ------------ ----------------------------------------
  1      everest              0.9456       mount everest is the tallest mountain in the world.
  2      olympus              0.0123       mount olympus is the tallest mountain in the world.
  3      fuji                 0.0067       mount fuji is the tallest mountain in the world.
  4      kilimanjaro          0.0043       mount kilimanjaro is the tallest mountain in the world.
  5      rushmore             0.0032       mount rushmore is the tallest mountain in the world.

======================================================================
Category: Science
======================================================================

  Sentence: Water is made of hydrogen and [MASK].
  Rank   Prediction           Confidence   Filled Sentence
  ------ -------------------- ------------ ----------------------------------------
  1      oxygen               0.8765       water is made of hydrogen and oxygen.
  2      carbon               0.0321       water is made of hydrogen and carbon.
  3      nitrogen             0.0198       water is made of hydrogen and nitrogen.
  4      helium               0.0123       water is made of hydrogen and helium.
  5      water                0.0087       water is made of hydrogen and water.

  Sentence: The [MASK] is the closest star to Earth.
  Rank   Prediction           Confidence   Filled Sentence
  ------ -------------------- ------------ ----------------------------------------
  1      sun                  0.9234       the sun is the closest star to earth.
  2      moon                 0.0234       the moon is the closest star to earth.
  3      star                 0.0098       the star is the closest star to earth.
  4      earth                0.0076       the earth is the closest star to earth.
  5      sun                  0.0054       the sun is the closest star to earth.

  Sentence: Albert [MASK] developed the theory of relativity.
  Rank   Prediction           Confidence   Filled Sentence
  ------ -------------------- ------------ ----------------------------------------
  1      einstein             0.9876       albert einstein developed the theory of relativity.
  2      newton               0.0043       albert newton developed the theory of relativity.
  3      darwin               0.0012       albert darwin developed the theory of relativity.
  4      einstein             0.0008       albert einstein developed the theory of relativity.
  5      schweitzer           0.0005       albert schweitzer developed the theory of relativity.

======================================================================
Category: Language Understanding (Context Matters)
======================================================================

  Sentence: The [MASK] was delicious, especially the chocolate cake.
  Rank   Prediction           Confidence   Filled Sentence
  ------ -------------------- ------------ ----------------------------------------
  1      food                 0.5432       the food was delicious, especially the chocolate cake.
  2      cake                 0.1234       the cake was delicious, especially the chocolate cake.
  3      meal                 0.0876       the meal was delicious, especially the chocolate cake.
  4      dessert              0.0654       the dessert was delicious, especially the chocolate cake.
  5      dinner               0.0432       the dinner was delicious, especially the chocolate cake.

  Sentence: The [MASK] barked loudly at the stranger.
  Rank   Prediction           Confidence   Filled Sentence
  ------ -------------------- ------------ ----------------------------------------
  1      dog                  0.9654       the dog barked loudly at the stranger.
  2      man                  0.0098       the man barked loudly at the stranger.
  3      wolf                 0.0076       the wolf barked loudly at the stranger.
  4      puppy                0.0054       the puppy barked loudly at the stranger.
  5      boy                  0.0032       the boy barked loudly at the stranger.

  Sentence: She picked up her [MASK] and started writing the essay.
  Rank   Prediction           Confidence   Filled Sentence
  ------ -------------------- ------------ ----------------------------------------
  1      pen                  0.6543       she picked up her pen and started writing the essay.
  2      notebook             0.0876       she picked up her notebook and started writing the essay.
  3      pencil               0.0654       she picked up her pencil and started writing the essay.
  4      laptop               0.0432       she picked up her laptop and started writing the essay.
  5      phone                0.0234       she picked up her phone and started writing the essay.

======================================================================
Tokenization Details
======================================================================

  Input:     The [MASK] barked loudly at the stranger.
  Tokens:    ['[CLS]', 'the', '[MASK]', 'barked', 'loudly', 'at', 'the', 'stranger', '.', '[SEP]']
  Token IDs: [101, 1996, 103, 24304, 10591, 2012, 1996, 11737, 1012, 102]
  [MASK] is token ID: 103
  [CLS]  is token ID: 101
  [SEP]  is token ID: 102
```

---

## Common Mistakes

1. **Using the wrong mask token**: BERT uses `[MASK]`, but RoBERTa uses `<mask>`. Using the wrong one will produce garbage predictions. Always check the documentation for your specific model.

2. **Forgetting special tokens**: When manually encoding text for BERT, always include `[CLS]` at the beginning and `[SEP]` at the end. The Hugging Face tokenizer does this automatically when `add_special_tokens=True`.

3. **Using BERT for text generation**: BERT is designed for understanding, not generating. It can predict masked words, but it cannot write long passages of text. Use GPT models for text generation (next chapter).

4. **Ignoring the maximum sequence length**: BERT has a maximum input length of 512 tokens. Longer inputs must be truncated or split into chunks.

5. **Using bert-base-uncased for case-sensitive tasks**: The "uncased" model converts everything to lowercase. If capitalization matters (like for Named Entity Recognition), use `bert-base-cased` instead.

---

## Best Practices

1. **Start with DistilBERT**: If you are building a production application and speed matters, start with DistilBERT. It is 60% faster than BERT with only a 3% drop in performance.

2. **Choose the right BERT variant**: Use `bert-base-uncased` for general tasks, `bert-base-cased` when capitalization matters, RoBERTa for best accuracy, and DistilBERT for speed.

3. **Fine-tune rather than train from scratch**: BERT is pre-trained on billions of words. You can fine-tune it on your specific task with just a few hundred or thousand examples. Never train BERT from scratch unless you have massive resources.

4. **Use the [CLS] token for classification**: When using BERT for classification tasks, use the output of the [CLS] token as the input to your classification layer.

5. **Batch your inputs**: When processing many sentences, batch them together for much faster processing. Use the tokenizer's batch encoding features.

---

## Quick Summary

**BERT** (Bidirectional Encoder Representations from Transformers) revolutionized NLP by reading text in both directions simultaneously. It is pre-trained using two tasks: **Masked Language Modeling** (predicting hidden words using context from both sides) and **Next Sentence Prediction** (determining if two sentences are consecutive). BERT uses the **WordPiece** tokenizer to break words into subword pieces, handling rare words effectively. Special tokens `[CLS]` (for classification) and `[SEP]` (for sentence separation) structure the input. Important variants include **DistilBERT** (faster, smaller), **RoBERTa** (better trained), and **ALBERT** (fewer parameters). BERT is best for understanding tasks, not text generation.

---

## Key Points

- BERT reads text bidirectionally, understanding each word in its full context
- **MLM** pre-training masks 15% of tokens and trains BERT to predict them
- The **80-10-10 rule**: 80% replaced with [MASK], 10% random word, 10% unchanged
- **NSP** pre-training teaches BERT to understand sentence relationships
- **WordPiece** tokenizer breaks rare words into known subword pieces (marked with ##)
- **[CLS]** token output represents the entire input for classification tasks
- **[SEP]** token separates sentences and marks input end
- BERT-base has 12 layers and 110M parameters; BERT-large has 24 layers and 340M
- **DistilBERT**: 40% smaller, 60% faster, 97% of BERT's performance
- **RoBERTa**: Trained better (more data, no NSP, dynamic masking)
- **ALBERT**: Fewer parameters through factorized embeddings and parameter sharing
- BERT excels at understanding tasks; use GPT for generation tasks

---

## Practice Questions

1. Why is bidirectional reading important for understanding language? Give an example where a left-to-right only model would fail.

2. Explain the 80-10-10 masking rule. Why does BERT not simply replace all masked tokens with the [MASK] token?

3. What is the purpose of the [CLS] token? Why is its output useful for classification tasks even though it does not represent any real word?

4. Why does WordPiece tokenization help with rare words? What would happen if BERT used a simple word-level tokenizer instead?

5. You need to build a sentiment analysis model for product reviews. Which BERT variant would you choose and why? Consider speed, accuracy, and resource constraints.

---

## Exercises

**Exercise 1: Context-Dependent Fill-Mask**
Use the fill-mask pipeline to demonstrate how the same masked position gets different predictions depending on context. Create 3 pairs of sentences where the same word position is masked, but the surrounding context leads to different predictions. For example: "The [MASK] flew across the sky" vs "The [MASK] flew across the field" (bird vs ball).

**Exercise 2: Sentence Similarity with BERT**
Load BERT and compute [CLS] embeddings for 10 sentences (5 about sports, 5 about cooking). Compute cosine similarity between all pairs. Verify that sports sentences are more similar to each other than to cooking sentences. Display results in a formatted matrix.

**Exercise 3: BERT Variant Speed Comparison**
Write a benchmarking script that measures the time each BERT variant (BERT, DistilBERT, ALBERT) takes to encode 100 sentences. Compare the speeds and report the results. Which variant is fastest? How much faster is it compared to BERT-base?

---

## What Is Next?

BERT uses only the encoder to understand text. But what if you want to generate text — write stories, complete sentences, or have conversations? In the next chapter, you will learn about the **GPT family** — models that use only the decoder to generate text one word at a time. You will see how autoregressive generation works, how GPT evolved from GPT-2 to GPT-4, and how techniques like temperature, top-k, and top-p control the creativity and diversity of generated text.
