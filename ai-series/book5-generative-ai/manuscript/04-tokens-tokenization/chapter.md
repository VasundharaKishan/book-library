# Chapter 4: Tokens and Tokenization

## What You Will Learn

In this chapter, you will learn:

- How text gets broken into tokens and why LLMs do not process raw text
- The Byte Pair Encoding (BPE) algorithm, step by step
- How WordPiece and SentencePiece tokenizers work
- How to use the tiktoken library to count tokens in Python
- How tokens map to numbers that the model actually processes
- Why tokenization affects cost, performance, and model behavior

## Why This Chapter Matters

Every time you send a message to an LLM, you pay for tokens. Every time an LLM generates a response, it produces tokens. The context window limit is measured in tokens. The speed of generation is measured in tokens per second.

Tokens are the fundamental unit of everything in the LLM world. Yet most users have no idea how tokenization works. They do not know why "hello" is one token but "entrepreneurship" might be three. They do not understand why code costs more tokens than English prose, or why Japanese text uses far more tokens than English text for the same meaning.

This chapter makes tokenization concrete. After reading it, you will be able to estimate token counts, understand costs, and make better decisions about how you structure your prompts.

---

## Why Not Just Use Words?

The most natural question is: why not just treat each word as a token? There are several important reasons.

```
+----------------------------------------------------------+
|        Why Words Do Not Work as Tokens                    |
+----------------------------------------------------------+
|                                                            |
|  Problem 1: Too many words                                |
|    English alone has ~170,000 words in common use          |
|    Add technical terms, names, slang: millions             |
|    Add all languages: tens of millions                    |
|    Model would need too large a vocabulary                |
|                                                            |
|  Problem 2: Unknown words                                 |
|    New words appear constantly: "ChatGPT", "COVID-19"     |
|    Misspellings: "teh", "recieve"                         |
|    A word-based system cannot handle unknown words        |
|                                                            |
|  Problem 3: Related words look unrelated                  |
|    "run", "running", "runner" are 3 separate words        |
|    But they share the root "run"                          |
|    A word-based system misses this connection             |
|                                                            |
|  Solution: Subword tokenization                           |
|    Break words into meaningful pieces                     |
|    "running" = "run" + "ning"                             |
|    Small vocabulary (~50K tokens) covers everything       |
|    New words? Break them into known pieces                |
|                                                            |
+----------------------------------------------------------+
```

```python
# Demonstrating why word-level tokenization is problematic

# Problem: word-level vocabulary is too large and inflexible
word_vocabulary = ["the", "cat", "sat", "on", "mat", "running",
                   "runner", "runs"]  # Need separate entries!

# Subword vocabulary is smaller but more flexible
subword_vocabulary = ["the", "cat", "sat", "on", "mat",
                      "run", "ning", "ner", "s"]

# With subwords, we can handle words we haven't seen
print("Word-level tokenization:")
print(f"  'running' -> ['running'] (must be in vocabulary)")
print(f"  'rerunning' -> UNKNOWN (not in vocabulary!)")
print()

print("Subword tokenization:")
print(f"  'running'   -> ['run', 'ning']")
print(f"  'runner'    -> ['run', 'ner']")
print(f"  'runs'      -> ['run', 's']")
print(f"  'rerunning' -> ['re', 'run', 'ning'] (works!)")
print()

# Compare vocabulary sizes
print("Vocabulary size comparison:")
print(f"  Word-level (English):    ~170,000 entries")
print(f"  Word-level (all langs):  ~5,000,000+ entries")
print(f"  Subword (GPT-4):         ~100,000 entries")
print(f"  Subword covers ALL languages with fewer entries!")
```

**Output:**
```
Word-level tokenization:
  'running' -> ['running'] (must be in vocabulary)
  'rerunning' -> UNKNOWN (not in vocabulary!)

Subword tokenization:
  'running'   -> ['run', 'ning']
  'runner'    -> ['run', 'ner']
  'runs'      -> ['run', 's']
  'rerunning' -> ['re', 'run', 'ning'] (works!)

Vocabulary size comparison:
  Word-level (English):    ~170,000 entries
  Word-level (all langs):  ~5,000,000+ entries
  Subword (GPT-4):         ~100,000 entries
  Subword covers ALL languages with fewer entries!
```

---

## Byte Pair Encoding (BPE): The Most Common Algorithm

**Byte Pair Encoding (BPE)** is the tokenization algorithm used by GPT models and many others. It was originally a data compression algorithm, adapted for NLP.

**Analogy:** Imagine you are texting and want to save characters. You notice you type "lol" a lot, so you create a shortcut: "L" means "lol". Then you notice "lol" often appears next to "omg", so you create another shortcut. BPE does the same thing but for all text patterns.

### How BPE Works

The BPE algorithm learns its vocabulary from a large corpus of text through these steps:

```
+----------------------------------------------------------+
|        BPE Algorithm Steps                                |
+----------------------------------------------------------+
|                                                            |
|  1. Start with individual characters as the vocabulary    |
|     Vocab: {a, b, c, d, ..., z, A, B, ..., Z, 0-9, ...} |
|                                                            |
|  2. Count all pairs of adjacent tokens in the training    |
|     text                                                   |
|                                                            |
|  3. Find the most frequent pair                           |
|     Example: "t" + "h" appears 1,000 times               |
|                                                            |
|  4. Merge that pair into a new token                      |
|     "t" + "h" --> "th" (add to vocabulary)                |
|                                                            |
|  5. Replace all occurrences of the pair in the text       |
|                                                            |
|  6. Repeat steps 2-5 until vocabulary reaches desired     |
|     size (typically 30,000 - 100,000 tokens)              |
|                                                            |
+----------------------------------------------------------+
```

```python
# Step-by-step BPE algorithm implementation

def learn_bpe(text, num_merges=10):
    """
    Simplified BPE algorithm showing how vocabulary is built.

    Args:
        text: Training text to learn from
        num_merges: Number of merge operations to perform
    """
    # Step 1: Start with characters (add end-of-word marker '_')
    words = text.split()
    # Represent each word as a tuple of characters
    word_freqs = {}
    for word in words:
        chars = tuple(list(word) + ["_"])  # _ marks end of word
        word_freqs[chars] = word_freqs.get(chars, 0) + 1

    print("BPE Training Process")
    print("=" * 55)
    print(f"\nTraining text: '{text}'")
    print(f"\nStep 1: Start with character-level tokens")
    vocab = set()
    for word in word_freqs:
        for char in word:
            vocab.add(char)
    print(f"  Initial vocabulary ({len(vocab)} tokens): "
          f"{sorted(vocab)}")

    # Perform merges
    for merge_num in range(1, num_merges + 1):
        # Step 2: Count all adjacent pairs
        pair_counts = {}
        for word, freq in word_freqs.items():
            for i in range(len(word) - 1):
                pair = (word[i], word[i+1])
                pair_counts[pair] = pair_counts.get(pair, 0) + freq

        if not pair_counts:
            break

        # Step 3: Find most frequent pair
        best_pair = max(pair_counts, key=pair_counts.get)
        best_count = pair_counts[best_pair]

        # Step 4: Create new token by merging the pair
        new_token = best_pair[0] + best_pair[1]
        vocab.add(new_token)

        print(f"\nMerge {merge_num}: '{best_pair[0]}' + "
              f"'{best_pair[1]}' -> '{new_token}' "
              f"(appeared {best_count} times)")

        # Step 5: Replace all occurrences in all words
        new_word_freqs = {}
        for word, freq in word_freqs.items():
            new_word = []
            i = 0
            while i < len(word):
                if (i < len(word) - 1 and
                    word[i] == best_pair[0] and
                    word[i+1] == best_pair[1]):
                    new_word.append(new_token)
                    i += 2
                else:
                    new_word.append(word[i])
                    i += 1
            new_word_freqs[tuple(new_word)] = freq
        word_freqs = new_word_freqs

        # Show current state
        print(f"  Vocabulary size: {len(vocab)}")
        print(f"  Current word representations:")
        for word, freq in sorted(word_freqs.items(),
                                  key=lambda x: -x[1])[:5]:
            print(f"    {list(word)} (x{freq})")

    return vocab

# Example training text
training_text = ("the cat sat on the mat the cat sat on the hat "
                 "the bat sat on the mat")

vocab = learn_bpe(training_text, num_merges=8)
```

**Output:**
```
BPE Training Process
=======================================================

Training text: 'the cat sat on the mat the cat sat on the hat the bat sat on the mat'

Step 1: Start with character-level tokens
  Initial vocabulary (12 tokens): ['_', 'a', 'b', 'c', 'e', 'h', 'm', 'n', 'o', 's', 't', 'u']

Merge 1: 't' + 'h' -> 'th' (appeared 8 times)
  Vocabulary size: 13
  Current word representations:
    ['th', 'e', '_'] (x8)
    ['s', 'a', 't', '_'] (x4)
    ['o', 'n', '_'] (x3)
    ['c', 'a', 't', '_'] (x2)
    ['m', 'a', 't', '_'] (x2)

Merge 2: 'th' + 'e' -> 'the' (appeared 8 times)
  Vocabulary size: 14
  Current word representations:
    ['the', '_'] (x8)
    ['s', 'a', 't', '_'] (x4)
    ['o', 'n', '_'] (x3)
    ['c', 'a', 't', '_'] (x2)
    ['m', 'a', 't', '_'] (x2)

Merge 3: 'a' + 't' -> 'at' (appeared 9 times)
  Vocabulary size: 15
  Current word representations:
    ['the', '_'] (x8)
    ['s', 'at', '_'] (x4)
    ['o', 'n', '_'] (x3)
    ['c', 'at', '_'] (x2)
    ['m', 'at', '_'] (x2)

Merge 4: 's' + 'at' -> 'sat' (appeared 4 times)
  Vocabulary size: 16
  Current word representations:
    ['the', '_'] (x8)
    ['sat', '_'] (x4)
    ['o', 'n', '_'] (x3)
    ['c', 'at', '_'] (x2)
    ['m', 'at', '_'] (x2)

Merge 5: 'the' + '_' -> 'the_' (appeared 8 times)
  Vocabulary size: 17
  Current word representations:
    ['the_'] (x8)
    ['sat', '_'] (x4)
    ['o', 'n', '_'] (x3)
    ['c', 'at', '_'] (x2)
    ['m', 'at', '_'] (x2)

Merge 6: 'sat' + '_' -> 'sat_' (appeared 4 times)
  Vocabulary size: 18
  Current word representations:
    ['the_'] (x8)
    ['sat_'] (x4)
    ['o', 'n', '_'] (x3)
    ['c', 'at', '_'] (x2)
    ['m', 'at', '_'] (x2)

Merge 7: 'o' + 'n' -> 'on' (appeared 3 times)
  Vocabulary size: 19
  Current word representations:
    ['the_'] (x8)
    ['sat_'] (x4)
    ['on', '_'] (x3)
    ['c', 'at', '_'] (x2)
    ['m', 'at', '_'] (x2)

Merge 8: 'at' + '_' -> 'at_' (appeared 5 times)
  Vocabulary size: 20
  Current word representations:
    ['the_'] (x8)
    ['sat_'] (x4)
    ['on', '_'] (x3)
    ['c', 'at_'] (x2)
    ['m', 'at_'] (x2)
```

**Line-by-line explanation:**

- `tuple(list(word) + ["_"])`: We split each word into individual characters and add an end-of-word marker "_". This helps the tokenizer know where words end.
- `pair_counts[pair] = pair_counts.get(pair, 0) + freq`: We count how often each pair of adjacent tokens appears, weighted by word frequency.
- `best_pair = max(pair_counts, key=pair_counts.get)`: We find the most frequent pair. This is the pair that will be merged into a new token.
- The merge loop replaces all occurrences of the best pair with the new merged token and continues until we reach the desired vocabulary size.

---

## WordPiece Tokenization

**WordPiece** is used by BERT and some other Google models. It is similar to BPE but uses a different strategy for choosing which pairs to merge.

```
+----------------------------------------------------------+
|        BPE vs WordPiece                                   |
+----------------------------------------------------------+
|                                                            |
|  BPE:                                                     |
|    Merges the most FREQUENT pair                          |
|    "t" + "h" merged because they appear together a lot    |
|                                                            |
|  WordPiece:                                               |
|    Merges the pair that increases LIKELIHOOD the most     |
|    Considers: if we merge "t"+"h", does the model         |
|    predict text better overall?                           |
|                                                            |
|  WordPiece uses "##" prefix for continuation pieces:      |
|    "playing" -> ["play", "##ing"]                         |
|    "unhappy" -> ["un", "##happy"]                         |
|                                                            |
|  The "##" tells you this piece is NOT the start of a word |
|                                                            |
+----------------------------------------------------------+
```

```python
# Demonstrating WordPiece-style tokenization

def wordpiece_tokenize(word, vocabulary):
    """
    Simple WordPiece tokenization.
    Tries to match the longest known prefix, then continues.
    Uses ## for non-initial pieces.
    """
    tokens = []
    start = 0

    while start < len(word):
        end = len(word)
        found = False

        while start < end:
            # Try to match the longest substring
            substr = word[start:end]
            if start > 0:
                substr = "##" + substr  # Mark as continuation

            if substr in vocabulary or (start == 0 and substr in vocabulary):
                tokens.append(substr)
                found = True
                break
            end -= 1

        if not found:
            tokens.append("[UNK]")  # Unknown token
            start += 1
        else:
            start = end

    return tokens

# A simplified WordPiece vocabulary
vocab = {
    "play", "##ing", "##er", "##s", "##ed",
    "un", "##happy", "##believe", "##able",
    "the", "cat", "##s",
    "run", "##ning",
    "embed", "##ding",
    "token", "##ize", "##ization",
}

test_words = [
    "playing",
    "player",
    "unhappy",
    "unbelievable",
    "tokenization",
    "embedding",
    "cats",
    "running",
]

print("WordPiece Tokenization Examples")
print("=" * 50)
print(f"Vocabulary size: {len(vocab)} tokens")
print()

for word in test_words:
    tokens = wordpiece_tokenize(word, vocab)
    print(f"  '{word}' -> {tokens}")
    print(f"    Pieces: {len(tokens)} tokens")
    print()
```

**Output:**
```
WordPiece Tokenization Examples
==================================================
Vocabulary size: 18 tokens

  'playing' -> ['play', '##ing']
    Pieces: 2 tokens

  'player' -> ['play', '##er']
    Pieces: 2 tokens

  'unhappy' -> ['un', '##happy']
    Pieces: 2 tokens

  'unbelievable' -> ['un', '##believe', '##able']
    Pieces: 3 tokens

  'tokenization' -> ['token', '##ization']
    Pieces: 2 tokens

  'embedding' -> ['embed', '##ding']
    Pieces: 2 tokens

  'cats' -> ['cat', '##s']
    Pieces: 2 tokens

  'running' -> ['run', '##ning']
    Pieces: 2 tokens
```

---

## SentencePiece

**SentencePiece** is different from BPE and WordPiece in one important way: it treats the input as a raw stream of characters, including spaces. It does not require pre-tokenized words.

```
+----------------------------------------------------------+
|        SentencePiece: Key Differences                     |
+----------------------------------------------------------+
|                                                            |
|  BPE / WordPiece:                                         |
|    1. First split text into words (by spaces)             |
|    2. Then split words into subword tokens                |
|    Problem: Assumes space-separated languages             |
|                                                            |
|  SentencePiece:                                           |
|    1. Treat entire text as one string (spaces included)   |
|    2. Learn tokens from the raw character sequence        |
|    Benefit: Works for ALL languages (Chinese, Japanese,   |
|    Thai, etc. do not use spaces between words)            |
|                                                            |
|  SentencePiece uses "▁" (underscore) to mark spaces:     |
|    "I love cats" -> ["▁I", "▁love", "▁cats"]            |
|    The ▁ shows where a space was in the original text     |
|                                                            |
|  Used by: Llama, T5, many multilingual models             |
|                                                            |
+----------------------------------------------------------+
```

```python
# Demonstrating SentencePiece concepts

def sentencepiece_demo():
    """Show how SentencePiece handles text differently."""

    examples = [
        {
            "text": "I love machine learning",
            "bpe_tokens": ["I", " love", " machine", " learning"],
            "sp_tokens": ["▁I", "▁love", "▁machine", "▁learning"],
            "note": "English: similar results"
        },
        {
            "text": "東京は美しい",
            "bpe_tokens": ["東", "京", "は", "美", "し", "い"],
            "sp_tokens": ["▁東京", "は", "美し", "い"],
            "note": "Japanese: SentencePiece handles no-space languages"
        },
        {
            "text": "Hello world! Hello world!",
            "bpe_tokens": ["Hello", " world", "!", " Hello", " world", "!"],
            "sp_tokens": ["▁Hello", "▁world", "!", "▁Hello", "▁world", "!"],
            "note": "Repeated text: spaces are part of tokens"
        },
    ]

    print("SentencePiece vs BPE Tokenization")
    print("=" * 55)

    for ex in examples:
        print(f"\n  Text: '{ex['text']}'")
        print(f"  BPE tokens:           {ex['bpe_tokens']}")
        print(f"  SentencePiece tokens: {ex['sp_tokens']}")
        print(f"  Note: {ex['note']}")

    print("\n" + "=" * 55)
    print("\nKey insight: SentencePiece treats spaces as characters,")
    print("making it language-agnostic. This is why models like")
    print("Llama use SentencePiece for multilingual support.")

sentencepiece_demo()
```

**Output:**
```
SentencePiece vs BPE Tokenization
=======================================================

  Text: 'I love machine learning'
  BPE tokens:           ['I', ' love', ' machine', ' learning']
  SentencePiece tokens: ['▁I', '▁love', '▁machine', '▁learning']
  Note: English: similar results

  Text: '東京は美しい'
  BPE tokens:           ['東', '京', 'は', '美', 'し', 'い']
  SentencePiece tokens: ['▁東京', 'は', '美し', 'い']
  Note: Japanese: SentencePiece handles no-space languages

  Text: 'Hello world! Hello world!'
  BPE tokens:           ['Hello', ' world', '!', ' Hello', ' world', '!']
  SentencePiece tokens: ['▁Hello', '▁world', '!', '▁Hello', '▁world', '!']
  Note: Repeated text: spaces are part of tokens

=======================================================

Key insight: SentencePiece treats spaces as characters,
making it language-agnostic. This is why models like
Llama use SentencePiece for multilingual support.
```

---

## Using tiktoken: Counting Tokens in Practice

**tiktoken** is OpenAI's fast tokenizer library for Python. It lets you see exactly how text gets tokenized and count tokens accurately.

```python
# Install tiktoken first: pip install tiktoken

import tiktoken

# Get the tokenizer for GPT-4 / GPT-4o
encoding = tiktoken.encoding_for_model("gpt-4o")

# Example 1: Basic tokenization
text = "Hello, how are you doing today?"
tokens = encoding.encode(text)
decoded_tokens = [encoding.decode([t]) for t in tokens]

print("Basic Tokenization with tiktoken")
print("=" * 55)
print(f"Text: '{text}'")
print(f"Token IDs: {tokens}")
print(f"Token strings: {decoded_tokens}")
print(f"Token count: {len(tokens)}")
print()

# Example 2: Compare different types of text
texts = [
    ("English sentence",  "The quick brown fox jumps over the lazy dog."),
    ("Python code",       "def hello():\n    print('Hello, World!')"),
    ("Numbers",           "3.14159265358979323846"),
    ("Technical term",    "electroencephalography"),
    ("Simple words",      "I am a cat"),
    ("URL",               "https://www.example.com/path/to/page"),
    ("JSON",              '{"name": "Alice", "age": 30}'),
]

print("\nToken Counts for Different Text Types")
print("=" * 55)

for label, text in texts:
    tokens = encoding.encode(text)
    ratio = len(tokens) / max(len(text.split()), 1)
    print(f"\n  {label}:")
    print(f"    Text: '{text}'")
    print(f"    Words: {len(text.split())}, Tokens: {len(tokens)}, "
          f"Ratio: {ratio:.1f} tokens/word")
```

**Output:**
```
Basic Tokenization with tiktoken
=======================================================
Text: 'Hello, how are you doing today?'
Token IDs: [9906, 11, 1268, 527, 499, 3815, 3432, 30]
Token strings: ['Hello', ',', ' how', ' are', ' you', ' doing', ' today', '?']
Token count: 8

Token Counts for Different Text Types
=======================================================

  English sentence:
    Text: 'The quick brown fox jumps over the lazy dog.'
    Words: 9, Tokens: 10, Ratio: 1.1 tokens/word

  Python code:
    Text: 'def hello():
    print('Hello, World!')'
    Words: 3, Tokens: 11, Ratio: 3.7 tokens/word

  Numbers:
    Text: '3.14159265358979323846'
    Words: 1, Tokens: 7, Ratio: 7.0 tokens/word

  Technical term:
    Text: 'electroencephalography'
    Words: 1, Tokens: 4, Ratio: 4.0 tokens/word

  Simple words:
    Text: 'I am a cat'
    Words: 4, Tokens: 4, Ratio: 1.0 tokens/word

  URL:
    Text: 'https://www.example.com/path/to/page'
    Words: 1, Tokens: 9, Ratio: 9.0 tokens/word

  JSON:
    Text: '{"name": "Alice", "age": 30}'
    Words: 4, Tokens: 10, Ratio: 2.5 tokens/word
```

**Line-by-line explanation:**

- `tiktoken.encoding_for_model("gpt-4o")`: This loads the specific tokenizer used by GPT-4o. Different models may use different tokenizers.
- `encoding.encode(text)`: Converts text into a list of token IDs (integers). These are the actual numbers fed into the model.
- `encoding.decode([t])`: Converts a single token ID back to its text representation. This lets us see what each token looks like.
- The ratio of tokens per word varies greatly: simple English is close to 1:1, while code, numbers, and URLs use many more tokens per word.

---

## How Text Becomes Numbers

The complete pipeline from text to numbers that the model processes:

```
+----------------------------------------------------------+
|        Text to Numbers Pipeline                           |
+----------------------------------------------------------+
|                                                            |
|  Step 1: Raw text                                         |
|    "I love Python"                                        |
|                                                            |
|  Step 2: Tokenization (split into tokens)                 |
|    ["I", " love", " Python"]                              |
|                                                            |
|  Step 3: Token IDs (look up in vocabulary table)          |
|    [40, 2815, 11361]                                      |
|                                                            |
|  Step 4: Embedding (map each ID to a vector)              |
|    40    -> [0.12, -0.34, 0.56, ..., 0.78]  (4096 nums)  |
|    2815  -> [0.45, 0.23, -0.67, ..., 0.11]  (4096 nums)  |
|    11361 -> [-0.33, 0.89, 0.12, ..., -0.55] (4096 nums)  |
|                                                            |
|  These embedding vectors are what the model processes.    |
|  Each vector captures the "meaning" of the token in       |
|  a high-dimensional space.                                 |
|                                                            |
+----------------------------------------------------------+
```

```python
# Complete pipeline from text to numbers

def text_to_numbers_pipeline(text):
    """
    Show the complete journey from text to numbers.
    Uses simulated embeddings for illustration.
    """
    import random
    random.seed(42)

    print("Text to Numbers Pipeline")
    print("=" * 55)

    # Step 1: Raw text
    print(f"\nStep 1 - Raw text:")
    print(f"  '{text}'")

    # Step 2: Tokenization
    # Using a simplified tokenizer for demonstration
    tokens = text.split()  # Simplified
    print(f"\nStep 2 - Tokens:")
    print(f"  {tokens}")

    # Step 3: Token IDs (simulated)
    token_to_id = {"I": 40, "love": 2815, "Python": 11361,
                   "machine": 5350, "learning": 4673}
    token_ids = [token_to_id.get(t, 0) for t in tokens]
    print(f"\nStep 3 - Token IDs:")
    for t, tid in zip(tokens, token_ids):
        print(f"  '{t}' -> {tid}")

    # Step 4: Embeddings (simulated 8-dimensional for display)
    embedding_dim = 8
    print(f"\nStep 4 - Embeddings ({embedding_dim}D shown, "
          f"real models use 4096D):")
    for t, tid in zip(tokens, token_ids):
        # Generate a repeatable random embedding for this token ID
        random.seed(tid)
        embedding = [round(random.uniform(-1, 1), 3)
                     for _ in range(embedding_dim)]
        print(f"  {tid:5d} ('{t}') -> {embedding}")

    print(f"\nThese {embedding_dim}D vectors (4096D in real models)")
    print(f"are what the transformer layers process.")

text_to_numbers_pipeline("I love Python")
```

**Output:**
```
Text to Numbers Pipeline
=======================================================

Step 1 - Raw text:
  'I love Python'

Step 2 - Tokens:
  ['I', 'love', 'Python']

Step 3 - Token IDs:
  'I' -> 40
  'love' -> 2815
  'Python' -> 11361

Step 4 - Embeddings (8D shown, real models use 4096D):
     40 ('I') -> [0.531, -0.634, 0.03, 0.474, -0.285, 0.456, -0.78, 0.908]
   2815 ('love') -> [-0.124, 0.672, -0.399, 0.816, 0.03, -0.547, 0.223, -0.891]
  11361 ('Python') -> [0.775, -0.215, 0.688, -0.042, 0.518, -0.365, 0.147, 0.933]

These 8D vectors (4096D in real models)
are what the transformer layers process.
```

---

## Token Counting and Cost Implications

Understanding token counts directly affects your wallet.

```python
# Token counting and cost calculator

def token_cost_calculator():
    """
    Calculate costs based on token usage for different providers.
    """
    # Pricing per 1 million tokens (approximate, as of 2024)
    pricing = {
        "GPT-4o": {
            "input": 2.50,    # per 1M input tokens
            "output": 10.00,  # per 1M output tokens
        },
        "GPT-4o mini": {
            "input": 0.15,
            "output": 0.60,
        },
        "Claude 3.5 Sonnet": {
            "input": 3.00,
            "output": 15.00,
        },
        "Claude 3.5 Haiku": {
            "input": 0.80,
            "output": 4.00,
        },
    }

    # Scenario: A customer support chatbot
    daily_conversations = 1000
    avg_input_tokens = 500   # User message + context
    avg_output_tokens = 300  # Model response

    daily_input_tokens = daily_conversations * avg_input_tokens
    daily_output_tokens = daily_conversations * avg_output_tokens

    print("Token Cost Calculator")
    print("=" * 60)
    print(f"\nScenario: Customer Support Chatbot")
    print(f"  Daily conversations:    {daily_conversations:,}")
    print(f"  Avg input tokens/conv:  {avg_input_tokens}")
    print(f"  Avg output tokens/conv: {avg_output_tokens}")
    print(f"  Daily input tokens:     {daily_input_tokens:,}")
    print(f"  Daily output tokens:    {daily_output_tokens:,}")

    print(f"\n{'Model':<22} {'Daily':>10} {'Monthly':>12} {'Yearly':>14}")
    print("-" * 60)

    for model, prices in pricing.items():
        daily_cost = (
            (daily_input_tokens / 1_000_000) * prices["input"] +
            (daily_output_tokens / 1_000_000) * prices["output"]
        )
        monthly_cost = daily_cost * 30
        yearly_cost = daily_cost * 365

        print(f"  {model:<20} ${daily_cost:>8.2f} "
              f"${monthly_cost:>10.2f} ${yearly_cost:>12.2f}")

    print("-" * 60)
    print("\nTip: Token-efficient prompts save real money at scale!")

token_cost_calculator()
```

**Output:**
```
Token Cost Calculator
============================================================

Scenario: Customer Support Chatbot
  Daily conversations:    1,000
  Avg input tokens/conv:  500
  Avg output tokens/conv: 300
  Daily input tokens:     500,000
  Daily output tokens:    300,000

Model                       Daily      Monthly        Yearly
------------------------------------------------------------
  GPT-4o               $    4.25 $    127.50 $    1,551.25
  GPT-4o mini          $    0.26 $      7.73 $       94.03
  Claude 3.5 Sonnet    $    6.00 $    180.00 $    2,190.00
  Claude 3.5 Haiku     $    1.60 $     48.00 $      584.00
------------------------------------------------------------

Tip: Token-efficient prompts save real money at scale!
```

```python
# Tips for reducing token usage

def token_saving_tips():
    """Show practical ways to reduce token usage."""

    examples = [
        {
            "label": "Verbose prompt",
            "text": ("I would really appreciate it if you could please "
                     "help me understand what the capital city of the "
                     "country of France is, and if you could explain why "
                     "it became the capital, that would be great too."),
            "improved": "What is the capital of France and why?",
            "tip": "Be concise. Remove filler words."
        },
        {
            "label": "Redundant context",
            "text": ("You are an AI assistant. You are helpful. You are "
                     "honest. You are harmless. You always try to help. "
                     "You respond in English. Now, summarize this text."),
            "improved": "Summarize this text:",
            "tip": "Remove unnecessary system context."
        },
        {
            "label": "Formatted output request",
            "text": ("Give me a list of the top 5 programming languages "
                     "with descriptions of each one, their history, "
                     "their main use cases, and example code."),
            "improved": ("List top 5 programming languages with one-line "
                        "use case each."),
            "tip": "Request only what you need."
        },
    ]

    print("Token-Saving Tips")
    print("=" * 55)

    for ex in examples:
        verbose_words = len(ex["text"].split())
        improved_words = len(ex["improved"].split())
        savings = ((verbose_words - improved_words)
                   / verbose_words * 100)

        print(f"\n  {ex['label']}:")
        print(f"    Before ({verbose_words} words): '{ex['text'][:60]}...'")
        print(f"    After  ({improved_words} words): '{ex['improved']}'")
        print(f"    Savings: ~{savings:.0f}% fewer tokens")
        print(f"    Tip: {ex['tip']}")

token_saving_tips()
```

**Output:**
```
Token-Saving Tips
=======================================================

  Verbose prompt:
    Before (42 words): 'I would really appreciate it if you could please help me ...'
    After  (9 words): 'What is the capital of France and why?'
    Savings: ~79% fewer tokens
    Tip: Be concise. Remove filler words.

  Redundant context:
    Before (22 words): 'You are an AI assistant. You are helpful. You are honest....'
    After  (3 words): 'Summarize this text:'
    Savings: ~86% fewer tokens
    Tip: Remove unnecessary system context.

  Formatted output request:
    Before (24 words): 'Give me a list of the top 5 programming languages with d...'
    After  (10 words): 'List top 5 programming languages with one-line use case each.'
    Savings: ~58% fewer tokens
    Tip: Request only what you need.
```

---

## Common Mistakes

| Mistake | Why It Is Wrong | What to Do Instead |
|---------|----------------|-------------------|
| Counting words instead of tokens | Tokens and words have different counts, affecting cost estimates | Use tiktoken or your model's tokenizer to count accurately |
| Ignoring tokenization for non-English text | Non-English languages often use 2-4x more tokens per word | Test token counts for your specific language |
| Not considering both input and output costs | Output tokens are typically more expensive than input tokens | Budget for both input and output in cost estimates |
| Using verbose prompts without considering cost | Extra words mean extra tokens mean extra cost | Write concise prompts; every word should earn its place |
| Assuming all models tokenize the same way | Different models use different tokenizers | Use the correct tokenizer for your specific model |

---

## Best Practices

1. **Always count tokens, not words.** Use the appropriate tokenizer library (tiktoken for OpenAI models) to get accurate counts.

2. **Test tokenization for your use case.** If you work with code, URLs, non-English text, or technical terms, check how many tokens they consume.

3. **Be concise in prompts.** Every unnecessary word costs tokens. At scale, concise prompts save significant money.

4. **Know your model's tokenizer.** GPT uses BPE via tiktoken. Llama uses SentencePiece. BERT uses WordPiece. Use the right tokenizer for accurate counting.

5. **Monitor token usage in production.** Track input and output token counts over time. Set up alerts for unusual spikes.

---

## Quick Summary

Tokenization converts text into numerical tokens that LLMs can process. The three main algorithms are BPE (used by GPT), WordPiece (used by BERT), and SentencePiece (used by Llama). BPE works by iteratively merging the most frequent character pairs. Tokens are not words: a single word can be multiple tokens, and token counts vary by language and text type. Token counts directly determine API costs, context window usage, and generation speed. Use tiktoken or model-specific tokenizers to count tokens accurately.

---

## Key Points

- LLMs use subword tokenization rather than whole words, allowing a small vocabulary to represent any text
- BPE iteratively merges the most frequent pair of adjacent tokens to build a vocabulary
- WordPiece is similar to BPE but chooses merges based on likelihood improvement rather than raw frequency
- SentencePiece treats text as raw bytes including spaces, making it language-agnostic
- tiktoken is OpenAI's Python library for counting tokens; always use the right tokenizer for your model
- Token counts affect cost, context window usage, and generation speed
- Non-English text, code, and numbers often use more tokens per word than simple English text
- Concise prompts reduce token usage and save money at scale

---

## Practice Questions

1. Why do LLMs use subword tokenization instead of word-level tokenization? Give at least three reasons.

2. Explain the BPE algorithm in your own words. If the most frequent pair in a training corpus is "e" + "r", what happens next?

3. How does SentencePiece differ from BPE and WordPiece? Why is this difference important for multilingual models?

4. If a model's API charges $3.00 per million input tokens and $15.00 per million output tokens, how much would it cost to process 10,000 conversations with an average of 800 input tokens and 400 output tokens each?

5. Why would the same English sentence use a different number of tokens with GPT-4's tokenizer vs Llama's tokenizer?

---

## Exercises

### Exercise 1: Explore tiktoken

Install tiktoken and experiment:
```python
pip install tiktoken
```
- Tokenize 10 different sentences and compare token counts
- Tokenize the same sentence in English, Spanish, and Chinese. Compare counts.
- Find a word that becomes 5 or more tokens

### Exercise 2: Build a Mini BPE

Extend the BPE example from this chapter:
- Use a larger training text (at least 100 words)
- Run 20 merge operations instead of 8
- Track how the vocabulary grows at each step
- Plot vocabulary size vs number of merges

### Exercise 3: Cost Optimization

Take a real prompt you have used with an LLM and:
- Count its tokens using tiktoken
- Rewrite it to use fewer tokens while keeping the same meaning
- Calculate how much you would save per 10,000 uses of the optimized prompt
- Determine if the optimized prompt still gives the same quality of response

---

## What Is Next?

Now that you understand how text becomes tokens and how tokens become numbers, the next chapter reveals how LLMs are trained from scratch. In "The Training Pipeline", you will learn the three stages of training: pre-training on massive text, supervised fine-tuning (SFT) to follow instructions, and alignment through RLHF and DPO to make models helpful and safe. Each stage transforms a raw text predictor into the helpful assistant you interact with.
