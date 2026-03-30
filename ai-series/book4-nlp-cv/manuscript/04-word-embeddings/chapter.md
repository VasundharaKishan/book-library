# Chapter 4: Word Embeddings

## What You Will Learn

- Why Bag of Words and TF-IDF fail to capture word meaning
- What word embeddings are and why they are revolutionary
- How Word2Vec works (Skip-gram and CBOW, explained simply)
- What GloVe is and how it differs from Word2Vec
- How to use pre-trained word embeddings with gensim
- How to visualize word embeddings in 2D using t-SNE
- How to perform word analogy tasks (king - man + woman = queen)

## Why This Chapter Matters

In the previous chapter, you learned that BoW and TF-IDF treat every word as an independent, unrelated entity. The word "happy" and the word "joyful" are as different as "happy" and "volcano." This is obviously wrong -- "happy" and "joyful" are almost identical in meaning. Word embeddings fix this by placing words in a mathematical space where similar words are close together. This single idea -- representing meaning as geometry -- transformed NLP and laid the groundwork for modern language models like BERT and GPT. If you understand word embeddings, you understand the foundation that the entire field is built on.

---

## 4.1 Why BoW and TF-IDF Fail

Let us revisit the problem from Chapter 3:

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

docs = [
    "The dog ran quickly",      # About a fast dog
    "The canine sprinted fast", # Same meaning, different words!
    "The cat slept quietly",    # Different meaning
]

vectorizer = TfidfVectorizer()
tfidf = vectorizer.fit_transform(docs)

sim_01 = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
sim_02 = cosine_similarity(tfidf[0:1], tfidf[2:3])[0][0]

print(f"'dog ran quickly' vs 'canine sprinted fast': {sim_01:.4f}")
print(f"'dog ran quickly' vs 'cat slept quietly':    {sim_02:.4f}")
```

**Output:**
```
'dog ran quickly' vs 'canine sprinted fast': 0.0000
'dog ran quickly' vs 'cat slept quietly':    0.1345
```

The first two sentences mean the same thing, but TF-IDF gives them ZERO similarity because they share no words. Meanwhile, the third sentence (with a completely different meaning) scores higher because it shares the word "the." This is fundamentally broken.

### The Three Big Problems

```
+----------------------------------------------------------+
|    Why BoW/TF-IDF Fails at Meaning                        |
+----------------------------------------------------------+
|                                                           |
|  Problem 1: NO SYNONYMS                                   |
|  "happy" and "joyful" are treated as unrelated            |
|                                                           |
|  Problem 2: NO RELATIONSHIPS                              |
|  "king" and "queen" are as different as "king" and "car"  |
|                                                           |
|  Problem 3: HUGE VECTORS                                  |
|  A vocabulary of 100,000 words means vectors of           |
|  length 100,000, mostly filled with zeros                 |
|                                                           |
|  Solution: Word Embeddings!                               |
|  Represent each word as a SHORT, DENSE vector             |
|  where similar words have similar vectors                 |
|                                                           |
+----------------------------------------------------------+
```

---

## 4.2 What Are Word Embeddings?

A **word embedding** is a way to represent a word as a list of numbers (a vector), typically with 100 to 300 numbers. The key insight is that these numbers are learned from data so that words with similar meanings end up with similar vectors.

> **Analogy:** Imagine a city map where every restaurant has a location (latitude, longitude). Italian restaurants cluster together in Little Italy. Chinese restaurants cluster together in Chinatown. Sushi places are near each other. You do not need to read the menu to know a restaurant serves Italian food -- you just look at where it sits on the map. Word embeddings are like a map for words. Similar words are close together, and you can tell what a word means by looking at its neighbors.

### BoW Vector vs Word Embedding Vector

```
+----------------------------------------------------------+
|     BoW Vector vs Word Embedding                          |
+----------------------------------------------------------+
|                                                           |
|  BoW Vector for "cat" (vocabulary of 10,000 words):       |
|  [0, 0, 0, ..., 1, ..., 0, 0, 0]                         |
|  Length: 10,000 (mostly zeros) -- SPARSE                  |
|                                                           |
|  Word Embedding for "cat" (300 dimensions):               |
|  [0.23, -0.41, 0.87, 0.15, -0.62, 0.33, ...]             |
|  Length: 300 (no zeros, every number matters) -- DENSE     |
|                                                           |
|  Key Difference:                                          |
|  BoW:       cat = [0,0,0,1,0,0,0,0,0,0]  (one-hot)       |
|  Embedding: cat = [0.23, -0.41, 0.87, ...]  (meaningful)  |
|                                                           |
|  In embeddings, "cat" and "kitten" have SIMILAR vectors   |
|  because they appear in similar contexts                  |
|                                                           |
+----------------------------------------------------------+
```

### The Distributional Hypothesis

Word embeddings are based on a simple but powerful idea called the **distributional hypothesis**:

> "You shall know a word by the company it keeps." -- J.R. Firth, 1957

This means: words that appear in similar contexts have similar meanings.

```
Context examples:

"I adopted a cute _____ from the shelter"
"The _____ chased the mouse"
"I fed my _____ this morning"

Words that fit: cat, dog, kitten, puppy

These words appear in similar contexts,
so they must have similar meanings!
```

---

## 4.3 Word2Vec: Words as Vectors

**Word2Vec** is an algorithm developed by researchers at Google in 2013 that learns word embeddings from large amounts of text. It has two variants:

### 4.3.1 Skip-gram: Predict Context from a Word

Given a center word, predict the words around it.

```
+----------------------------------------------------------+
|        Skip-gram: Predict context from center word        |
+----------------------------------------------------------+
|                                                           |
|  Sentence: "The cat sat on the mat"                       |
|                                                           |
|  Window size = 2 (look 2 words left and right)            |
|                                                           |
|  Center word: "sat"                                       |
|  Context words: "The", "cat", "on", "the"                 |
|                                                           |
|  Training examples:                                       |
|  Input: "sat" --> Predict: "The"                          |
|  Input: "sat" --> Predict: "cat"                          |
|  Input: "sat" --> Predict: "on"                           |
|  Input: "sat" --> Predict: "the"                          |
|                                                           |
|  The neural network learns to predict context words.      |
|  The hidden layer weights BECOME the word embeddings.     |
|                                                           |
+----------------------------------------------------------+
```

### 4.3.2 CBOW: Predict a Word from Context

CBOW (Continuous Bag of Words) works in the opposite direction: given the context words, predict the center word.

```
+----------------------------------------------------------+
|        CBOW: Predict center word from context             |
+----------------------------------------------------------+
|                                                           |
|  Sentence: "The cat sat on the mat"                       |
|                                                           |
|  Context words: "The", "cat", "on", "the"                 |
|  Center word: "sat"                                       |
|                                                           |
|  Training:                                                |
|  Input: ["The", "cat", "on", "the"] --> Predict: "sat"    |
|                                                           |
+----------------------------------------------------------+
```

### 4.3.3 How Training Works (Simplified)

```
+----------------------------------------------------------+
|        Word2Vec Training (Simplified)                     |
+----------------------------------------------------------+
|                                                           |
|  Step 1: Start with random vectors for each word          |
|                                                           |
|    "cat"  = [0.1, -0.3, 0.5, ...]  (random)              |
|    "dog"  = [0.8, 0.2, -0.1, ...]   (random)             |
|    "sat"  = [-0.4, 0.7, 0.3, ...]   (random)             |
|                                                           |
|  Step 2: Read millions of sentences                       |
|                                                           |
|    "The cat sat on the mat"                               |
|    "The dog sat on the rug"                               |
|    "A cat chased a mouse"                                 |
|    "A dog chased a ball"                                  |
|    ... millions more ...                                  |
|                                                           |
|  Step 3: Adjust vectors so context predictions work       |
|                                                           |
|    "cat" and "dog" appear in similar contexts             |
|    --> their vectors move closer together                 |
|                                                           |
|    "cat" and "airplane" appear in different contexts      |
|    --> their vectors stay far apart                       |
|                                                           |
|  Step 4: After training, similar words have similar       |
|          vectors automatically!                           |
|                                                           |
|    "cat"  = [0.62, -0.15, 0.48, ...]                      |
|    "dog"  = [0.58, -0.22, 0.51, ...]  (close to cat!)    |
|    "car"  = [-0.31, 0.78, -0.12, ...] (far from cat)     |
|                                                           |
+----------------------------------------------------------+
```

> **Analogy:** Imagine you are new at a company and you do not know anyone. After a year, you notice that Alice and Bob always eat lunch together, attend the same meetings, and work on the same projects. Even without being told, you can guess they work in the same department. Word2Vec does the same thing -- it watches which words "hang out together" and groups them accordingly.

---

## 4.4 GloVe: Global Vectors for Word Representation

**GloVe** (Global Vectors) is another popular word embedding method developed at Stanford in 2014. While Word2Vec learns from local context windows, GloVe learns from global word co-occurrence statistics.

### How GloVe Differs from Word2Vec

```
+----------------------------------------------------------+
|        Word2Vec vs GloVe                                  |
+----------------------------------------------------------+
|                                                           |
|  Word2Vec:                                                |
|  - Reads text one window at a time                        |
|  - Predicts context words (local)                         |
|  - Like reading a book word by word                       |
|                                                           |
|  GloVe:                                                   |
|  - First counts how often every pair of words             |
|    appears together across the ENTIRE corpus              |
|  - Then learns vectors from these counts (global)         |
|  - Like first making a frequency table, then learning     |
|                                                           |
|  Both produce similar quality embeddings.                 |
|  In practice, the choice often does not matter much.      |
|                                                           |
+----------------------------------------------------------+
```

GloVe creates a large **co-occurrence matrix** -- a table that counts how often each pair of words appears near each other. Then it factorizes this matrix to produce the word vectors.

```
Co-occurrence matrix (simplified):

           ice    steam   solid   gas    water
ice        -       0       3      0       5
steam      0       -       0      4       4
solid      3       0       -      0       1
gas        0       4       0      -       1
water      5       4       1      1       -

GloVe learns vectors so that:
- "ice" and "solid" are close (high co-occurrence)
- "steam" and "gas" are close (high co-occurrence)
- "ice" and "gas" are far apart (low co-occurrence)
```

---

## 4.5 Using Pre-trained Embeddings with Gensim

Training word embeddings from scratch requires massive amounts of text and computing power. Fortunately, you can download pre-trained embeddings that others have already trained on billions of words.

**Gensim** is a Python library specifically designed for working with word embeddings.

### 4.5.1 Loading Pre-trained Word2Vec

```python
import gensim.downloader as api

# Download pre-trained Word2Vec (trained on Google News, 3 billion words)
# This model has 300-dimensional vectors for 3 million words
# Note: First download is ~1.7 GB and takes a few minutes
print("Loading pre-trained Word2Vec model...")
model = api.load("word2vec-google-news-300")
print("Model loaded!")

# Get the vector for a word
vector = model['computer']
print(f"\nVector for 'computer':")
print(f"  Dimensions: {len(vector)}")
print(f"  First 10 values: {vector[:10]}")
```

**Output:**
```
Loading pre-trained Word2Vec model...
Model loaded!

Vector for 'computer':
  Dimensions: 300
  First 10 values: [ 0.07617188  0.01416016 -0.14160156  0.18554688 -0.08398438
  -0.01367188  0.09960938  0.12695312 -0.09765625  0.04296875]
```

### 4.5.2 Finding Similar Words

```python
import gensim.downloader as api

model = api.load("word2vec-google-news-300")

# Find words most similar to "king"
similar_words = model.most_similar("king", topn=10)
print("Words most similar to 'king':")
for word, score in similar_words:
    print(f"  {word:20s} {score:.4f}")
```

**Output:**
```
Words most similar to 'king':
  kings                0.7138
  queen                0.6511
  monarch              0.6413
  crown_prince         0.6204
  prince               0.6160
  sultan               0.5866
  ruler                0.5797
  Queen_Consort        0.5367
  queens               0.5311
  princess             0.5153
```

The model correctly identifies that "kings," "queen," "monarch," and "prince" are similar to "king" -- all related to royalty.

### 4.5.3 Word Similarity Scores

```python
import gensim.downloader as api

model = api.load("word2vec-google-news-300")

# Compare word pairs
pairs = [
    ("cat", "dog"),        # Both animals
    ("cat", "kitten"),     # Very related
    ("cat", "car"),        # Unrelated
    ("happy", "joyful"),   # Synonyms
    ("happy", "sad"),      # Antonyms
    ("king", "queen"),     # Related concepts
    ("paris", "france"),   # Capital and country
]

print("Word Similarity Scores:")
print(f"{'Word 1':15s} {'Word 2':15s} {'Similarity':>10s}")
print("-" * 42)
for w1, w2 in pairs:
    try:
        sim = model.similarity(w1, w2)
        print(f"{w1:15s} {w2:15s} {sim:10.4f}")
    except KeyError as e:
        print(f"{w1:15s} {w2:15s} {'Not found':>10s}")
```

**Output:**
```
Word Similarity Scores:
Word 1          Word 2           Similarity
------------------------------------------
cat             dog                  0.7609
cat             kitten               0.7840
cat             car                  0.1164
happy           joyful               0.5715
happy           sad                  0.3848
king            queen                0.6511
paris           france               0.4543
```

**Interpretation:**
- "cat" and "kitten" (0.78) are more similar than "cat" and "dog" (0.76), which makes sense.
- "cat" and "car" (0.12) are barely similar -- they just happen to share letters.
- "happy" and "joyful" (0.57) are recognized as synonyms.
- "happy" and "sad" (0.38) have some similarity because they both relate to emotions, even though they are opposites.

### 4.5.4 Using a Smaller Model (GloVe)

If you want a faster download, use the smaller GloVe model:

```python
import gensim.downloader as api

# GloVe model (smaller, faster to download)
# 50-dimensional vectors trained on Wikipedia + Gigaword
model = api.load("glove-wiki-gigaword-50")

# Find similar words
print("Words similar to 'python':")
for word, score in model.most_similar("python", topn=5):
    print(f"  {word:15s} {score:.4f}")

print("\nWords similar to 'university':")
for word, score in model.most_similar("university", topn=5):
    print(f"  {word:15s} {score:.4f}")
```

**Output:**
```
Words similar to 'python':
  perl            0.7873
  snake           0.6928
  scripting       0.6623
  java            0.6519
  ruby            0.6408

Words similar to 'university':
  college         0.9218
  school          0.8032
  campus          0.7927
  graduate        0.7596
  universities    0.7566
```

Notice how "python" finds both programming languages (perl, java, ruby) and snake-related words -- it captures multiple meanings.

---

## 4.6 Word Analogies

One of the most impressive properties of word embeddings is their ability to solve analogies using simple vector arithmetic.

### 4.6.1 The King - Man + Woman = Queen Example

The most famous example:

```
king - man + woman = ???

In vector space:
vector("king") - vector("man") + vector("woman") ≈ vector("queen")
```

> **Analogy:** Think of it this way. If you take the concept of "king" and remove the "maleness" from it, then add "femaleness," you get "queen." The embedding vectors capture these abstract concepts as directions in space.

```
+----------------------------------------------------------+
|        Word Analogy in Vector Space                       |
+----------------------------------------------------------+
|                                                           |
|             queen *                                       |
|            /     |                                        |
|           /      | "royalty"                              |
|          /       |    direction                           |
|    woman *-------*                                        |
|         |       king                                      |
|         |      /                                          |
|  "gender"|    /                                           |
| direction|   /                                            |
|         |  /                                              |
|     man *                                                 |
|                                                           |
|  king - man = "royalty" direction                         |
|  "royalty" direction + woman = queen                      |
|                                                           |
+----------------------------------------------------------+
```

### 4.6.2 Code Example

```python
import gensim.downloader as api

model = api.load("word2vec-google-news-300")

# king - man + woman = ?
result = model.most_similar(
    positive=["king", "woman"],
    negative=["man"],
    topn=3
)

print("king - man + woman = ?")
for word, score in result:
    print(f"  {word:15s} {score:.4f}")
```

**Output:**
```
king - man + woman = ?
  queen           0.7118
  monarch         0.6189
  princess         0.5902
```

### 4.6.3 More Analogy Examples

```python
import gensim.downloader as api

model = api.load("word2vec-google-news-300")

analogies = [
    # (word1, word2, word3) --> word4
    # word1 is to word2 as word3 is to ???
    ("Paris", "France", "Tokyo", "Japan"),
    ("big", "bigger", "small", "smaller"),
    ("man", "doctor", "woman", "doctor/nurse"),
    ("walk", "walked", "run", "ran"),
]

print("Word Analogies:")
print("=" * 60)
for w1, w2, w3, expected in analogies:
    try:
        result = model.most_similar(
            positive=[w2, w3],
            negative=[w1],
            topn=3
        )
        print(f"\n{w1} is to {w2} as {w3} is to ???")
        print(f"Expected: {expected}")
        print("Got:")
        for word, score in result:
            print(f"  {word:20s} {score:.4f}")
    except KeyError as e:
        print(f"Word not found: {e}")
```

**Output:**
```
Word Analogies:
============================================================

Paris is to France as Tokyo is to ???
Expected: Japan
Got:
  Japan                0.6697
  Japanese             0.5970
  Osaka                0.5387

big is to bigger as small is to ???
Expected: smaller
Got:
  smaller              0.6852
  larger               0.6478
  Bigger               0.5847

man is to doctor as woman is to ???
Expected: doctor/nurse
Got:
  physician            0.5895
  gynecologist         0.5627
  nurse                0.5490

walk is to walked as run is to ???
Expected: ran
Got:
  ran                  0.6095
  running              0.5359
  walks                0.5044
```

**Line-by-line explanation:**

1. `model.most_similar(positive=[w2, w3], negative=[w1], topn=3)` -- This computes `w2 - w1 + w3` and finds the closest words to the result.
2. `positive` means "add these vectors" and `negative` means "subtract these vectors."
3. The analogy `Paris:France :: Tokyo:???` becomes `France - Paris + Tokyo = ???`, and the answer is Japan.

---

## 4.7 Visualizing Embeddings with t-SNE

Word embeddings typically have 100-300 dimensions. We cannot visualize that many dimensions, but we can use **t-SNE** (t-distributed Stochastic Neighbor Embedding) to compress them down to 2 dimensions for plotting.

> **Analogy:** Imagine you have a 3D globe with cities marked on it. You want to draw a flat 2D map. You will lose some accuracy (distances will be slightly off), but the general relationships are preserved -- cities that are close on the globe will be close on the map. t-SNE does this for high-dimensional word vectors.

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
import gensim.downloader as api

# Load a pre-trained model
model = api.load("glove-wiki-gigaword-50")

# Choose words from different categories
words = {
    'Animals': ['cat', 'dog', 'horse', 'fish', 'bird', 'mouse'],
    'Countries': ['france', 'germany', 'japan', 'china', 'brazil', 'india'],
    'Colors': ['red', 'blue', 'green', 'yellow', 'purple', 'orange'],
    'Numbers': ['one', 'two', 'three', 'four', 'five', 'six'],
}

# Get vectors for all words
all_words = []
all_vectors = []
all_categories = []
colors_map = {
    'Animals': 'red',
    'Countries': 'blue',
    'Colors': 'green',
    'Numbers': 'purple'
}

for category, word_list in words.items():
    for word in word_list:
        if word in model:
            all_words.append(word)
            all_vectors.append(model[word])
            all_categories.append(category)

vectors_array = np.array(all_vectors)

# Apply t-SNE to reduce to 2 dimensions
tsne = TSNE(n_components=2, random_state=42, perplexity=5)
vectors_2d = tsne.fit_transform(vectors_array)

# Plot
plt.figure(figsize=(12, 8))
for category in words.keys():
    indices = [i for i, c in enumerate(all_categories) if c == category]
    x = vectors_2d[indices, 0]
    y = vectors_2d[indices, 1]
    plt.scatter(x, y, c=colors_map[category], label=category, s=100)

    for i in indices:
        plt.annotate(
            all_words[i],
            (vectors_2d[i, 0], vectors_2d[i, 1]),
            fontsize=10,
            ha='center',
            va='bottom'
        )

plt.title("Word Embeddings Visualized with t-SNE")
plt.xlabel("t-SNE Dimension 1")
plt.ylabel("t-SNE Dimension 2")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("word_embeddings_tsne.png", dpi=100)
plt.show()
print("Plot saved as 'word_embeddings_tsne.png'")
```

**Expected behavior:** The plot will show four distinct clusters. Animal words cluster together, country words cluster together, color words cluster together, and number words cluster together. This visually proves that word embeddings capture meaning.

**Line-by-line explanation:**

1. We select words from four categories to see if embeddings group them correctly.
2. `model[word]` retrieves the pre-trained vector for each word.
3. `TSNE(n_components=2)` reduces 50-dimensional vectors to 2 dimensions.
4. `tsne.fit_transform(vectors_array)` applies the dimensionality reduction.
5. We plot each category in a different color to see the clustering.

```
+----------------------------------------------------------+
|        What the t-SNE Plot Looks Like                     |
+----------------------------------------------------------+
|                                                           |
|         * france                                          |
|     * germany   * japan                                   |
|       * india  * china                                    |
|          * brazil                                         |
|                                                           |
|                        * one                              |
|                     * two  * three                        |
|                       * four * five                       |
|    * cat                 * six                            |
|  * dog  * horse                                           |
|    * mouse  * bird                                        |
|      * fish            * red                              |
|                      * blue * green                       |
|                        * yellow * purple                  |
|                          * orange                         |
|                                                           |
|  Similar words cluster together automatically!            |
|                                                           |
+----------------------------------------------------------+
```

---

## 4.8 Using Word Embeddings in Practice

### 4.8.1 Computing Document Vectors

To represent an entire document, you can average the word vectors of all its words:

```python
import numpy as np
import gensim.downloader as api
from sklearn.metrics.pairwise import cosine_similarity

model = api.load("glove-wiki-gigaword-50")

def document_vector(text, model):
    """Compute the average word vector for a document."""
    words = text.lower().split()
    vectors = []
    for word in words:
        if word in model:
            vectors.append(model[word])

    if len(vectors) == 0:
        return np.zeros(model.vector_size)

    return np.mean(vectors, axis=0)

# Compare documents
docs = [
    "The cat chased the mouse",
    "A kitten ran after a small rodent",
    "The stock market crashed today",
]

print("Document Similarity using Word Embeddings:")
print("=" * 50)

# Compute vectors for all documents
doc_vectors = np.array([document_vector(doc, model) for doc in docs])

# Compare all pairs
for i in range(len(docs)):
    for j in range(i + 1, len(docs)):
        sim = cosine_similarity(
            doc_vectors[i].reshape(1, -1),
            doc_vectors[j].reshape(1, -1)
        )[0][0]
        print(f"\nDoc {i}: '{docs[i]}'")
        print(f"Doc {j}: '{docs[j]}'")
        print(f"Similarity: {sim:.4f}")
```

**Output:**
```
Document Similarity using Word Embeddings:
==================================================

Doc 0: 'The cat chased the mouse'
Doc 1: 'A kitten ran after a small rodent'
Similarity: 0.8924

Doc 0: 'The cat chased the mouse'
Doc 2: 'The stock market crashed today'
Similarity: 0.5013

Doc 1: 'A kitten ran after a small rodent'
Doc 2: 'The stock market crashed today'
Similarity: 0.3618
```

Now "The cat chased the mouse" and "A kitten ran after a small rodent" are correctly identified as highly similar (0.89), even though they share almost no words. This is a massive improvement over TF-IDF.

### 4.8.2 Finding Odd One Out

```python
import gensim.downloader as api

model = api.load("word2vec-google-news-300")

# Which word does not belong?
groups = [
    ["cat", "dog", "horse", "computer"],
    ["happy", "joyful", "glad", "table"],
    ["paris", "london", "berlin", "banana"],
]

print("Odd One Out:")
for group in groups:
    odd = model.doesnt_match(group)
    print(f"  {group} --> '{odd}' does not belong")
```

**Output:**
```
Odd One Out:
  ['cat', 'dog', 'horse', 'computer'] --> 'computer' does not belong
  ['happy', 'joyful', 'glad', 'table'] --> 'table' does not belong
  ['paris', 'london', 'berlin', 'banana'] --> 'banana' does not belong
```

---

## 4.9 Word Embeddings with PyTorch

In deep learning models, you use an **embedding layer** that learns embeddings during training:

```python
import torch
import torch.nn as nn

# Create an embedding layer
# 10000 = vocabulary size (number of unique words)
# 100 = embedding dimension (length of each vector)
embedding_layer = nn.Embedding(num_embeddings=10000, embedding_dim=100)

# Look up embeddings for some word indices
# Suppose: 0=the, 1=cat, 2=sat, 3=on, 4=mat
word_indices = torch.tensor([1, 2, 3])  # "cat sat on"

# Get embeddings
embedded = embedding_layer(word_indices)

print(f"Input shape:  {word_indices.shape}")
print(f"Output shape: {embedded.shape}")
print(f"\nEmbedding for word index 1 ('cat'):")
print(f"  First 10 values: {embedded[0][:10].detach().numpy()}")
```

**Output:**
```
Input shape:  torch.Size([3])
Output shape: torch.Size([3, 100])

Embedding for word index 1 ('cat'):
  First 10 values: [-0.5246  1.3406 -0.1488  0.7630  0.9472
  -0.2115  1.0423  0.1535  0.7291 -0.3845]
```

**Line-by-line explanation:**

1. `nn.Embedding(num_embeddings=10000, embedding_dim=100)` -- Creates a lookup table of 10,000 words, each represented by a 100-dimensional vector. Initially, these vectors are random.
2. `word_indices = torch.tensor([1, 2, 3])` -- Words are represented by their index in the vocabulary. Index 1 might be "cat," index 2 might be "sat," etc.
3. `embedding_layer(word_indices)` -- Looks up the vector for each word index. Input is 3 word indices, output is 3 vectors of 100 dimensions each.
4. During training, these embedding vectors are updated by backpropagation, just like other neural network weights.

### Loading Pre-trained Embeddings into PyTorch

```python
import torch
import torch.nn as nn
import numpy as np
import gensim.downloader as api

# Load pre-trained GloVe
model = api.load("glove-wiki-gigaword-50")

# Create vocabulary from your data
vocab = ["cat", "dog", "bird", "fish", "car", "bus"]

# Build embedding matrix
embedding_dim = 50
vocab_size = len(vocab)
embedding_matrix = np.zeros((vocab_size, embedding_dim))

for i, word in enumerate(vocab):
    if word in model:
        embedding_matrix[i] = model[word]
    else:
        # Random vector for unknown words
        embedding_matrix[i] = np.random.normal(0, 0.1, embedding_dim)

# Create PyTorch embedding layer with pre-trained weights
embedding_layer = nn.Embedding.from_pretrained(
    torch.FloatTensor(embedding_matrix),
    freeze=False  # Allow fine-tuning during training
)

print(f"Embedding matrix shape: {embedding_matrix.shape}")
print(f"Embedding layer weight shape: {embedding_layer.weight.shape}")

# Verify: cat (index 0) and dog (index 1) should be similar
cat_vec = embedding_layer(torch.tensor(0))
dog_vec = embedding_layer(torch.tensor(1))
car_vec = embedding_layer(torch.tensor(4))

cat_dog_sim = torch.cosine_similarity(cat_vec.unsqueeze(0), dog_vec.unsqueeze(0))
cat_car_sim = torch.cosine_similarity(cat_vec.unsqueeze(0), car_vec.unsqueeze(0))

print(f"\nSimilarity (cat, dog): {cat_dog_sim.item():.4f}")
print(f"Similarity (cat, car): {cat_car_sim.item():.4f}")
```

**Output:**
```
Embedding matrix shape: (6, 50)
Embedding layer weight shape: torch.Size([6, 50])

Similarity (cat, dog): 0.9218
Similarity (cat, car): 0.4517
```

---

## Common Mistakes

1. **Training embeddings on too little data** -- Word2Vec needs millions of sentences to learn good embeddings. For small datasets, use pre-trained embeddings instead.

2. **Comparing embeddings from different models** -- A vector from Word2Vec and a vector from GloVe live in different spaces. Never mix them.

3. **Ignoring out-of-vocabulary (OOV) words** -- Pre-trained models do not have vectors for every word. Always check if a word exists in the model before accessing its vector.

4. **Using embeddings without fine-tuning** -- Pre-trained embeddings are good starting points, but fine-tuning them on your specific task usually improves performance.

5. **Overinterpreting individual dimensions** -- Unlike BoW where each dimension corresponds to a word, individual dimensions of word embeddings do not have clear interpretations.

---

## Best Practices

1. **Use pre-trained embeddings as a starting point** -- GloVe (glove-wiki-gigaword-50 or glove-wiki-gigaword-300) and Word2Vec (word2vec-google-news-300) are good defaults.

2. **Choose the right dimensionality** -- 50 dimensions for small projects, 100-300 for most tasks. More dimensions can capture more nuance but need more data.

3. **Handle unknown words gracefully** -- Use the average of all word vectors, or a special random vector, for words not in your vocabulary.

4. **Use averaging for simple tasks, weighted averaging for better results** -- TF-IDF-weighted word vectors often outperform simple averaging for document representation.

5. **Visualize your embeddings** -- Use t-SNE to check that your embeddings make sense. If "cat" and "banana" are close together, something is wrong.

---

## Quick Summary

Word embeddings represent words as dense vectors where similar words have similar vectors. Word2Vec learns embeddings by predicting context words (Skip-gram) or center words (CBOW) from large text corpora. GloVe learns from global word co-occurrence statistics. Pre-trained embeddings can be loaded using gensim and used immediately for tasks like finding similar words, solving analogies, and computing document similarity. The t-SNE algorithm can compress high-dimensional embeddings to 2D for visualization. In PyTorch, the nn.Embedding layer creates trainable embedding vectors that can be initialized with pre-trained weights.

---

## Key Points

- **Word embeddings** represent words as dense vectors (100-300 numbers) where meaning is encoded in the numbers.
- **Distributional hypothesis:** Words in similar contexts have similar meanings and therefore similar vectors.
- **Word2Vec** has two architectures: Skip-gram (predict context from center word) and CBOW (predict center word from context).
- **GloVe** learns from global co-occurrence statistics rather than local context windows.
- **Pre-trained embeddings** (gensim) let you use high-quality vectors without training from scratch.
- Word embeddings can solve **analogies**: king - man + woman = queen.
- **t-SNE** reduces high-dimensional embeddings to 2D for visualization.
- In PyTorch, `nn.Embedding` creates an embedding lookup table that can be initialized with pre-trained weights.
- **Average word vectors** to represent entire documents.

---

## Practice Questions

1. Why do word embeddings represent "cat" and "kitten" as similar vectors but "cat" and "car" as different vectors? What principle makes this work?

2. Explain the difference between Skip-gram and CBOW in Word2Vec. Which one is generally considered better for rare words and why?

3. The analogy "king - man + woman = queen" works because of a mathematical property of word vectors. Explain in simple terms what this means geometrically.

4. What is the difference between Word2Vec and GloVe? When might you choose one over the other?

5. Why is t-SNE useful for word embeddings? What information might be lost when reducing from 300 dimensions to 2 dimensions?

---

## Exercises

### Exercise 1: Explore Word Relationships

Using gensim with a pre-trained model:
1. Find the 10 most similar words to "computer," "doctor," "university," and "music."
2. Try at least 5 word analogies of your own (e.g., "man is to king as woman is to ???").
3. Find 3 analogies that work well and 3 that fail. Explain why some might fail.

### Exercise 2: Build a Synonym Finder

Write a function `find_synonyms(word, n=5)` that:
1. Takes a word and returns its `n` most similar words from a pre-trained model.
2. Filters out words that are just different forms of the same word (e.g., "running" should not be a synonym of "run").
3. Test it on 10 different words across different categories (emotions, animals, verbs, adjectives).

### Exercise 3: Document Similarity with Embeddings vs TF-IDF

Create a set of 10 document pairs where each pair consists of sentences with the same meaning but different words (paraphrases). Compare:
1. TF-IDF cosine similarity
2. Average word embedding cosine similarity
Which method correctly identifies more paraphrases? By how much?

---

## What Is Next?

Now that you understand how to represent words and documents as numbers -- from simple counts (BoW) to intelligent vectors (embeddings) -- you are ready to build real NLP applications. In **Chapter 5: Text Classification**, you will combine preprocessing, text representation, and machine learning to build systems that can automatically categorize text. You will build a spam detector, a sentiment analyzer, and learn how to evaluate these systems properly.
