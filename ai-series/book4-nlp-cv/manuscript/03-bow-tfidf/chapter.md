# Chapter 3: Text Representation -- Bag of Words and TF-IDF

## What You Will Learn

- Why computers need numbers, not words
- How Bag of Words (BoW) converts text into number vectors by counting words
- How TF-IDF improves on BoW by weighting words based on importance
- How to use sklearn's CountVectorizer and TfidfVectorizer
- How to measure document similarity using cosine similarity
- The limitations of BoW and TF-IDF and when they fall short

## Why This Chapter Matters

Machine learning models understand numbers, not words. You cannot feed the sentence "I love this movie" directly into a neural network or a logistic regression model. You must first convert it into a list of numbers -- a **vector**. This chapter teaches you two foundational ways to do this conversion: Bag of Words and TF-IDF. These methods are decades old, but they remain widely used in industry because they are simple, fast, and surprisingly effective. Every NLP practitioner should understand them before moving to more advanced representations like word embeddings.

---

## 3.1 Why Computers Need Numbers, Not Words

Let us make this concrete with a simple example:

```python
# This will NOT work -- you cannot do math on strings
sentence1 = "I love cats"
sentence2 = "I love dogs"

# How similar are these sentences?
# We cannot compute similarity on raw text
# sentence1 - sentence2 = ???  <-- Makes no sense
```

Computers do math. They add, multiply, and compare numbers. To process text, we must first convert every document into a numerical representation called a **vector**.

> **Analogy:** Imagine you are a judge at a cooking competition, but you cannot taste the food. Instead, each dish is described by numbers: spiciness level (1-10), sweetness level (1-10), and presentation score (1-10). You compare dishes using these numbers. Similarly, NLP converts text into numbers so algorithms can "compare" and "judge" documents.

```
+----------------------------------------------------------+
|        Text to Numbers: The Core Challenge                |
+----------------------------------------------------------+
|                                                           |
|  "I love cats"  -->  ???  -->  [1, 1, 1, 0]              |
|  "I love dogs"  -->  ???  -->  [1, 1, 0, 1]              |
|                                                           |
|  Now we can compare:                                      |
|  Similarity([1,1,1,0], [1,1,0,1]) = 0.67                 |
|                                                           |
|  The computer can see: these sentences are similar!       |
|                                                           |
+----------------------------------------------------------+
```

---

## 3.2 Bag of Words (BoW)

**Bag of Words** is the simplest way to convert text into numbers. The idea is straightforward: count how many times each word appears in a document.

### 3.2.1 The Concept

> **Analogy:** Imagine dumping all the words of a sentence into a bag, like Scrabble tiles. You shake the bag so the word order is lost. Then you count how many of each word tile you have. That count is your numerical representation.

```
Document: "the cat sat on the mat"

Step 1: Dump words into a bag (lose order):
        {the, cat, sat, on, the, mat}

Step 2: Count each unique word:
        the = 2, cat = 1, sat = 1, on = 1, mat = 1

Step 3: Create a vector:
        [2, 1, 1, 1, 1]
```

### 3.2.2 Building BoW by Hand

```python
from collections import Counter

documents = [
    "I love cats",
    "I love dogs",
    "cats and dogs are great",
]

# Step 1: Build vocabulary (all unique words)
vocabulary = set()
for doc in documents:
    words = doc.lower().split()
    vocabulary.update(words)

vocabulary = sorted(vocabulary)
print(f"Vocabulary: {vocabulary}")
print(f"Vocabulary size: {len(vocabulary)}")

# Step 2: Count word frequencies for each document
print("\nBag of Words vectors:")
for doc in documents:
    words = doc.lower().split()
    counts = Counter(words)
    # Create a vector: count of each vocabulary word
    vector = [counts.get(word, 0) for word in vocabulary]
    print(f"  '{doc}'")
    print(f"  Vector: {vector}")
    print()

# Show which number corresponds to which word
print("Index mapping:")
for i, word in enumerate(vocabulary):
    print(f"  Position {i}: '{word}'")
```

**Output:**
```
Vocabulary: ['and', 'are', 'cats', 'dogs', 'great', 'i', 'love']
Vocabulary size: 7

Bag of Words vectors:
  'I love cats'
  Vector: [0, 0, 1, 0, 0, 1, 1]

  'I love dogs'
  Vector: [0, 0, 0, 1, 0, 1, 1]

  'cats and dogs are great'
  Vector: [1, 1, 1, 1, 1, 0, 0]

Index mapping:
  Position 0: 'and'
  Position 1: 'are'
  Position 2: 'cats'
  Position 3: 'dogs'
  Position 4: 'great'
  Position 5: 'i'
  Position 6: 'love'
```

**Line-by-line explanation:**

1. We create a **vocabulary** -- the set of all unique words across all documents.
2. `Counter(words)` counts how many times each word appears in a document.
3. `counts.get(word, 0)` gets the count for each vocabulary word. If the word is not in the document, the count is 0.
4. The resulting vector has one number for each word in the vocabulary.

### 3.2.3 Using sklearn's CountVectorizer

In practice, we use sklearn's `CountVectorizer` which does all of this automatically:

```python
from sklearn.feature_extraction.text import CountVectorizer

documents = [
    "I love cats",
    "I love dogs",
    "cats and dogs are great",
]

# Create the vectorizer
vectorizer = CountVectorizer()

# Fit (learn vocabulary) and transform (create vectors)
bow_matrix = vectorizer.fit_transform(documents)

# Show the vocabulary
print("Vocabulary:")
print(f"  {vectorizer.get_feature_names_out()}")

# Show the BoW matrix
print("\nBag of Words matrix:")
print(bow_matrix.toarray())

# Show each document's vector with labels
print("\nDetailed view:")
feature_names = vectorizer.get_feature_names_out()
for i, doc in enumerate(documents):
    print(f"\n  Document: '{doc}'")
    vector = bow_matrix.toarray()[i]
    for word, count in zip(feature_names, vector):
        if count > 0:
            print(f"    {word}: {count}")
```

**Output:**
```
Vocabulary:
  ['and' 'are' 'cats' 'dogs' 'great' 'love']

Bag of Words matrix:
[[0 0 1 0 0 1]
 [0 0 0 1 0 1]
 [1 1 1 1 1 0]]

Detailed view:

  Document: 'I love cats'
    cats: 1
    love: 1

  Document: 'I love dogs'
    dogs: 1
    love: 1

  Document: 'cats and dogs are great'
    and: 1
    are: 1
    cats: 1
    dogs: 1
    great: 1
```

**Line-by-line explanation:**

1. `CountVectorizer()` -- Creates a vectorizer object. By default, it converts to lowercase and removes single-character words (which is why "I" is not in the vocabulary).
2. `vectorizer.fit_transform(documents)` -- Two steps in one: `fit` learns the vocabulary from the documents, and `transform` converts each document into a count vector.
3. `vectorizer.get_feature_names_out()` -- Returns the vocabulary (all unique words the vectorizer learned).
4. `bow_matrix.toarray()` -- Converts the sparse matrix to a regular array for display. sklearn uses **sparse matrices** (a memory-efficient format) because most values are 0.

### 3.2.4 CountVectorizer Options

```python
from sklearn.feature_extraction.text import CountVectorizer

documents = [
    "The quick brown fox jumps over the lazy dog",
    "The dog chased the fox around the park",
    "Quick brown foxes are very lazy animals",
]

# Option 1: Limit vocabulary size
vec1 = CountVectorizer(max_features=5)
result1 = vec1.fit_transform(documents)
print("Top 5 features only:")
print(f"  Words: {vec1.get_feature_names_out()}")
print(f"  Matrix:\n{result1.toarray()}")

# Option 2: Use n-grams (word pairs, triples, etc.)
vec2 = CountVectorizer(ngram_range=(1, 2))
result2 = vec2.fit_transform(documents)
print(f"\nWith bigrams (1-2 word combinations):")
print(f"  Features: {vec2.get_feature_names_out()}")

# Option 3: Remove common and rare words
vec3 = CountVectorizer(min_df=2, max_df=0.9)
result3 = vec3.fit_transform(documents)
print(f"\nFiltered vocabulary:")
print(f"  Words: {vec3.get_feature_names_out()}")
```

**Output:**
```
Top 5 features only:
  Words: ['brown' 'dog' 'fox' 'lazy' 'the']
  Matrix:
[[1 1 1 1 2]
 [0 1 1 0 3]
 [1 0 0 1 0]]

With bigrams (1-2 word combinations):
  Features: ['animals' 'are' 'are very' 'around' 'around the' 'brown' 'brown fox' 'brown foxes' 'chased' 'chased the' 'dog' 'dog chased' 'fox' 'fox around' 'fox jumps' 'foxes' 'foxes are' 'jumps' 'jumps over' 'lazy' 'lazy animals' 'lazy dog' 'over' 'over the' 'park' 'quick' 'quick brown' 'the' 'the dog' 'the fox' 'the lazy' 'the park' 'the quick' 'very' 'very lazy']

Filtered vocabulary:
  Words: ['brown' 'dog' 'fox' 'lazy' 'the']
```

**Key parameters explained:**

- `max_features=5` -- Keep only the top 5 most frequent words.
- `ngram_range=(1, 2)` -- Include single words (unigrams) and word pairs (bigrams). For example, "brown fox" is a bigram. This captures some word order information.
- `min_df=2` -- A word must appear in at least 2 documents to be included. Removes very rare words.
- `max_df=0.9` -- A word must appear in at most 90% of documents. Removes very common words (similar to stop word removal).

```
+----------------------------------------------------------+
|        N-grams: Capturing Word Order                      |
+----------------------------------------------------------+
|                                                           |
|  Text: "New York is great"                                |
|                                                           |
|  Unigrams (n=1): "New", "York", "is", "great"            |
|  Bigrams  (n=2): "New York", "York is", "is great"       |
|  Trigrams (n=3): "New York is", "York is great"           |
|                                                           |
|  Unigrams lose "New York" as a phrase.                    |
|  Bigrams capture it!                                      |
|                                                           |
+----------------------------------------------------------+
```

---

## 3.3 The Problem with Bag of Words

BoW has a major flaw: it treats all words equally. The word "the" and the word "revolutionary" get the same treatment, even though "the" appears in almost every document and tells us nothing, while "revolutionary" is rare and informative.

```python
from sklearn.feature_extraction.text import CountVectorizer

documents = [
    "the movie was the best movie the director ever made",
    "the food at the restaurant was the worst",
]

vectorizer = CountVectorizer()
bow = vectorizer.fit_transform(documents)

print("Vocabulary:", vectorizer.get_feature_names_out())
print("\nBoW matrix:")
print(bow.toarray())
print("\nNotice: 'the' has the highest counts (3 and 3)")
print("But 'the' tells us nothing about what the document is about!")
```

**Output:**
```
Vocabulary: ['at' 'best' 'director' 'ever' 'food' 'made' 'movie' 'restaurant' 'the' 'was' 'worst']

BoW matrix:
[[0 1 1 1 0 1 2 0 3 1 0]
 [1 0 0 0 1 0 0 1 3 1 1]]

Notice: 'the' has the highest counts (3 and 3)
But 'the' tells us nothing about what the document is about!
```

This is where TF-IDF comes in.

---

## 3.4 TF-IDF: Term Frequency-Inverse Document Frequency

**TF-IDF** solves the problem above by giving less weight to common words and more weight to rare, informative words.

### 3.4.1 The Two Parts

TF-IDF is made up of two measurements multiplied together:

**TF (Term Frequency):** How often a word appears in a specific document. More occurrences means higher TF.

```
TF(word, document) = (Number of times word appears in document)
                     / (Total number of words in document)
```

**IDF (Inverse Document Frequency):** How rare a word is across ALL documents. Rarer words get higher IDF.

```
IDF(word) = log(Total number of documents
               / Number of documents containing the word)
```

**TF-IDF = TF x IDF**

> **Analogy:** Imagine you are reading restaurant reviews. The word "food" appears in almost every review -- it is not helpful for distinguishing reviews. But the word "rancid" appears in only one review. "Rancid" is much more informative because it is rare. TF-IDF is like a scoring system that says: "Common words are boring. Rare words are interesting."

### 3.4.2 Calculating TF-IDF by Hand

```python
import math

documents = [
    "the cat sat on the mat",
    "the dog sat on the log",
    "cats and dogs are friends",
]

# Step 1: Calculate TF for "the" in document 1
doc1_words = documents[0].lower().split()
tf_the = doc1_words.count("the") / len(doc1_words)
print(f"TF('the', doc1) = {doc1_words.count('the')}/{len(doc1_words)} = {tf_the:.4f}")

# Step 2: Calculate IDF for "the" across all documents
total_docs = len(documents)
docs_with_the = sum(1 for doc in documents if "the" in doc.lower())
idf_the = math.log(total_docs / docs_with_the)
print(f"IDF('the') = log({total_docs}/{docs_with_the}) = {idf_the:.4f}")

# Step 3: TF-IDF
tfidf_the = tf_the * idf_the
print(f"TF-IDF('the', doc1) = {tf_the:.4f} * {idf_the:.4f} = {tfidf_the:.4f}")

print("\n--- Now for a rare word: 'friends' ---")

# TF for "friends" in document 3
doc3_words = documents[2].lower().split()
tf_friends = doc3_words.count("friends") / len(doc3_words)
print(f"TF('friends', doc3) = {doc3_words.count('friends')}/{len(doc3_words)} = {tf_friends:.4f}")

# IDF for "friends"
docs_with_friends = sum(1 for doc in documents if "friends" in doc.lower())
idf_friends = math.log(total_docs / docs_with_friends)
print(f"IDF('friends') = log({total_docs}/{docs_with_friends}) = {idf_friends:.4f}")

# TF-IDF
tfidf_friends = tf_friends * idf_friends
print(f"TF-IDF('friends', doc3) = {tf_friends:.4f} * {idf_friends:.4f} = {tfidf_friends:.4f}")

print(f"\n'friends' TF-IDF ({tfidf_friends:.4f}) >> 'the' TF-IDF ({tfidf_the:.4f})")
print("Rare words get higher scores!")
```

**Output:**
```
TF('the', doc1) = 2/6 = 0.3333
IDF('the') = log(3/2) = 0.4055
TF-IDF('the', doc1) = 0.3333 * 0.4055 = 0.1352

--- Now for a rare word: 'friends' ---
TF('friends', doc3) = 1/5 = 0.2000
IDF('friends') = log(3/1) = 1.0986
TF-IDF('friends', doc3) = 0.2000 * 1.0986 = 0.2197

'friends' TF-IDF (0.2197) >> 'the' TF-IDF (0.1352)
Rare words get higher scores!
```

### 3.4.3 Visual Explanation

```
+----------------------------------------------------------+
|           TF-IDF: How It Works                            |
+----------------------------------------------------------+
|                                                           |
|  Word: "the"                                              |
|  TF:  High (appears often in the document)                |
|  IDF: Low  (appears in almost ALL documents)              |
|  TF-IDF = High * Low = LOW SCORE                         |
|  --> "the" is not important                               |
|                                                           |
|  Word: "revolutionary"                                    |
|  TF:  Medium (appears a few times)                        |
|  IDF: High (appears in very FEW documents)                |
|  TF-IDF = Medium * High = HIGH SCORE                     |
|  --> "revolutionary" is important!                        |
|                                                           |
+----------------------------------------------------------+
```

### 3.4.4 Using sklearn's TfidfVectorizer

```python
from sklearn.feature_extraction.text import TfidfVectorizer

documents = [
    "the cat sat on the mat",
    "the dog sat on the log",
    "cats and dogs are friends",
]

# Create TF-IDF vectorizer
vectorizer = TfidfVectorizer()

# Fit and transform
tfidf_matrix = vectorizer.fit_transform(documents)

# Show vocabulary
feature_names = vectorizer.get_feature_names_out()
print("Vocabulary:", feature_names)

# Show TF-IDF matrix (rounded for readability)
import numpy as np
print("\nTF-IDF matrix (rounded to 2 decimals):")
print(np.round(tfidf_matrix.toarray(), 2))

# Show scores for each document
print("\nDetailed scores:")
for i, doc in enumerate(documents):
    print(f"\n  Document: '{doc}'")
    vector = tfidf_matrix.toarray()[i]
    # Sort by score (highest first)
    scored_words = sorted(
        zip(feature_names, vector),
        key=lambda x: x[1],
        reverse=True
    )
    for word, score in scored_words:
        if score > 0:
            print(f"    {word:12s}: {score:.4f}")
```

**Output:**
```
Vocabulary: ['and' 'are' 'cat' 'cats' 'dog' 'dogs' 'friends' 'log' 'mat' 'on' 'sat' 'the']

TF-IDF matrix (rounded to 2 decimals):
[[0.   0.   0.47 0.   0.   0.   0.   0.   0.47 0.3  0.3  0.61]
 [0.   0.   0.   0.   0.47 0.   0.   0.47 0.   0.3  0.3  0.61]
 [0.45 0.45 0.   0.45 0.   0.45 0.45 0.   0.   0.   0.   0.  ]]

Detailed scores:

  Document: 'the cat sat on the mat'
    the         : 0.6133
    cat         : 0.4681
    mat         : 0.4681
    on          : 0.2985
    sat         : 0.2985

  Document: 'the dog sat on the log'
    the         : 0.6133
    dog         : 0.4681
    log         : 0.4681
    on          : 0.2985
    sat         : 0.2985

  Document: 'cats and dogs are friends'
    and         : 0.4472
    are         : 0.4472
    cats        : 0.4472
    dogs        : 0.4472
    friends     : 0.4472
```

**Line-by-line explanation:**

1. `TfidfVectorizer()` -- Creates a TF-IDF vectorizer. It automatically handles tokenization, counting, and TF-IDF calculation.
2. `vectorizer.fit_transform(documents)` -- Learns the vocabulary and computes TF-IDF scores for all documents.
3. The output shows that common words shared across documents (like "on" and "sat") get lower scores, while unique words (like "cat," "mat," "log") get higher scores.

> **Note:** sklearn's TF-IDF formula is slightly different from the textbook formula. It uses smoothed IDF and L2 normalization. The concept is the same -- common words get lower scores.

---

## 3.5 Document Similarity with Cosine Similarity

Now that we have numerical vectors for our documents, we can measure how similar they are using **cosine similarity**.

### 3.5.1 What Is Cosine Similarity?

**Cosine similarity** measures the angle between two vectors. If two vectors point in the same direction, they are similar (cosine similarity = 1). If they point in perpendicular directions, they are unrelated (cosine similarity = 0).

```
+----------------------------------------------------------+
|        Cosine Similarity Visualized                       |
+----------------------------------------------------------+
|                                                           |
|  Similar documents (small angle):                         |
|                                                           |
|           B                                               |
|          /                                                |
|         / ) small angle = HIGH similarity                 |
|        /                                                  |
|       A                                                   |
|                                                           |
|  Different documents (large angle):                       |
|                                                           |
|       B                                                   |
|       |                                                   |
|       | ) large angle = LOW similarity                    |
|       |                                                   |
|       -------A                                            |
|                                                           |
|  Cosine Similarity ranges from 0 to 1:                    |
|    1.0 = identical direction (very similar)               |
|    0.0 = perpendicular (completely different)             |
|                                                           |
+----------------------------------------------------------+
```

### 3.5.2 Computing Cosine Similarity

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

documents = [
    "I love machine learning",
    "I love deep learning",
    "The weather is sunny today",
    "Machine learning is a subset of artificial intelligence",
]

# Create TF-IDF vectors
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(documents)

# Compute cosine similarity between all pairs
similarity_matrix = cosine_similarity(tfidf_matrix)

# Display results
print("Documents:")
for i, doc in enumerate(documents):
    print(f"  D{i}: {doc}")

print("\nCosine Similarity Matrix:")
print("        D0      D1      D2      D3")
for i, row in enumerate(similarity_matrix):
    scores = "  ".join(f"{score:.4f}" for score in row)
    print(f"  D{i}  {scores}")
```

**Output:**
```
Documents:
  D0: I love machine learning
  D1: I love deep learning
  D2: The weather is sunny today
  D3: Machine learning is a subset of artificial intelligence

Cosine Similarity Matrix:
        D0      D1      D2      D3
  D0  1.0000  0.5765  0.0000  0.2480
  D1  0.5765  1.0000  0.0000  0.1228
  D2  0.0000  0.0000  1.0000  0.0880
  D3  0.2480  0.1228  0.0880  1.0000
```

**Interpretation:**

- D0 and D1 are most similar (0.5765) -- both talk about "love" and "learning."
- D0 and D2 have zero similarity -- they share no words at all.
- D0 and D3 are somewhat similar (0.2480) -- they share "machine" and "learning."
- Every document is perfectly similar to itself (1.0000).

### 3.5.3 Finding the Most Similar Document

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Our document collection (like a mini search engine)
documents = [
    "Python is a great programming language",
    "Machine learning uses algorithms to learn from data",
    "Deep learning is a subset of machine learning",
    "Python has many libraries for data science",
    "The weather today is warm and sunny",
]

# Build TF-IDF vectors for all documents
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(documents)

# A new query
query = "Python for machine learning"
query_vector = vectorizer.transform([query])

# Compute similarity between query and all documents
similarities = cosine_similarity(query_vector, tfidf_matrix)[0]

# Rank documents by similarity
print(f"Query: '{query}'\n")
print("Results (ranked by similarity):")
ranked_indices = np.argsort(similarities)[::-1]
for rank, idx in enumerate(ranked_indices, 1):
    print(f"  {rank}. (score: {similarities[idx]:.4f}) {documents[idx]}")
```

**Output:**
```
Query: 'Python for machine learning'

Results (ranked by similarity):
  1. (score: 0.4649) Machine learning uses algorithms to learn from data
  2. (score: 0.3731) Python is a great programming language
  3. (score: 0.3473) Deep learning is a subset of machine learning
  4. (score: 0.2897) Python has many libraries for data science
  5. (score: 0.0000) The weather today is warm and sunny
```

**Line-by-line explanation:**

1. `vectorizer.transform([query])` -- Note we use `transform` (not `fit_transform`) because we want to use the same vocabulary learned from our documents. If we used `fit_transform`, it would create a new vocabulary based only on the query.
2. `cosine_similarity(query_vector, tfidf_matrix)[0]` -- Compute similarity between the query and every document. `[0]` extracts the first (and only) row of results.
3. `np.argsort(similarities)[::-1]` -- Sort document indices by similarity score in descending order.

This is essentially how basic search engines work!

---

## 3.6 Comparing BoW and TF-IDF

Let us compare both methods on the same documents:

```python
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import numpy as np

documents = [
    "the the the cat sat",
    "the dog chased the cat",
    "a bird flew over the rainbow",
]

# Bag of Words
bow_vec = CountVectorizer()
bow_matrix = bow_vec.fit_transform(documents)

# TF-IDF
tfidf_vec = TfidfVectorizer()
tfidf_matrix = tfidf_vec.fit_transform(documents)

print("=== Bag of Words ===")
print(f"Features: {bow_vec.get_feature_names_out()}")
print(f"Matrix:\n{bow_matrix.toarray()}")

print("\n=== TF-IDF ===")
print(f"Features: {tfidf_vec.get_feature_names_out()}")
print(f"Matrix:\n{np.round(tfidf_matrix.toarray(), 3)}")

print("\nKey difference:")
print("  BoW: 'the' in doc 1 has count 3 (highest value)")
print("  TF-IDF: 'cat' and 'sat' in doc 1 have higher scores than 'the'")
print("  TF-IDF correctly downweights the common word 'the'")
```

**Output:**
```
=== Bag of Words ===
Features: ['bird' 'cat' 'chased' 'dog' 'flew' 'over' 'rainbow' 'sat' 'the']
Matrix:
[[0 1 0 0 0 0 0 1 3]
 [0 1 1 1 0 0 0 0 2]
 [1 0 0 0 1 1 1 0 1]]

=== TF-IDF ===
Features: ['bird' 'cat' 'chased' 'dog' 'flew' 'over' 'rainbow' 'sat' 'the']
Matrix:
[[0.    0.318 0.    0.    0.    0.    0.    0.497 0.808]
 [0.    0.315 0.492 0.492 0.    0.    0.    0.    0.529]
 [0.423 0.    0.    0.    0.423 0.423 0.423 0.    0.36 ]]

Key difference:
  BoW: 'the' in doc 1 has count 3 (highest value)
  TF-IDF: 'cat' and 'sat' in doc 1 have higher scores than 'the'
  TF-IDF correctly downweights the common word 'the'
```

---

## 3.7 Limitations of BoW and TF-IDF

Despite their usefulness, these methods have significant limitations:

### 3.7.1 No Word Order

```python
from sklearn.feature_extraction.text import CountVectorizer

# These sentences have very different meanings
# but identical BoW vectors!
docs = [
    "the dog bit the man",
    "the man bit the dog",
]

vectorizer = CountVectorizer()
bow = vectorizer.fit_transform(docs)

print("Vocabulary:", vectorizer.get_feature_names_out())
print("Vectors:")
print(bow.toarray())
print("\nBoth vectors are IDENTICAL!")
print("BoW cannot tell that these sentences mean different things.")
```

**Output:**
```
Vocabulary: ['bit' 'dog' 'man' 'the']
Vectors:
[[1 1 1 2]
 [1 1 1 2]]

Both vectors are IDENTICAL!
BoW cannot tell that these sentences mean different things.
```

### 3.7.2 No Semantic Understanding

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# These sentences mean the same thing but use different words
docs = [
    "The movie was excellent",    # positive
    "The film was wonderful",     # positive (same meaning!)
    "The movie was terrible",     # negative
]

vectorizer = TfidfVectorizer()
tfidf = vectorizer.fit_transform(docs)

sim_01 = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
sim_02 = cosine_similarity(tfidf[0:1], tfidf[2:3])[0][0]

print(f"'excellent movie' vs 'wonderful film': {sim_01:.4f}")
print(f"'excellent movie' vs 'terrible movie': {sim_02:.4f}")
print(f"\nProblem: 'terrible movie' is MORE similar than 'wonderful film'!")
print("TF-IDF matches words, not meanings.")
```

**Output:**
```
'excellent movie' vs 'wonderful film': 0.1218
'excellent movie' vs 'terrible movie': 0.4640

Problem: 'terrible movie' is MORE similar than 'wonderful film'!
TF-IDF matches words, not meanings.
```

This is because "excellent movie" and "terrible movie" share the word "movie," while "excellent movie" and "wonderful film" share no words at all. BoW and TF-IDF do not understand that "excellent" and "wonderful" are synonyms, or that "movie" and "film" mean the same thing.

### 3.7.3 High Dimensionality

```python
from sklearn.feature_extraction.text import CountVectorizer

# Even a small collection creates a large vocabulary
documents = [
    "Natural language processing enables computers to understand text",
    "Machine learning algorithms can classify documents automatically",
    "Deep neural networks have revolutionized artificial intelligence",
    "Text classification is a fundamental NLP task",
    "Sentiment analysis determines whether text is positive or negative",
]

vectorizer = CountVectorizer()
bow = vectorizer.fit_transform(documents)

print(f"Number of documents: {bow.shape[0]}")
print(f"Vocabulary size: {bow.shape[1]}")
print(f"Matrix size: {bow.shape[0]} x {bow.shape[1]} = {bow.shape[0] * bow.shape[1]} cells")
print(f"Non-zero cells: {bow.nnz}")
print(f"Sparsity: {(1 - bow.nnz / (bow.shape[0] * bow.shape[1])) * 100:.1f}%")
print("\nWith real datasets (millions of documents), the vocabulary")
print("can be hundreds of thousands of words. Most vectors are mostly zeros.")
```

**Output:**
```
Number of documents: 5
Vocabulary size: 29
Matrix size: 5 x 29 = 145 cells
Non-zero cells: 34
Sparsity: 76.6%
```

### Summary of Limitations

```
+----------------------------------------------------------+
|        Limitations of BoW and TF-IDF                      |
+----------------------------------------------------------+
|                                                           |
|  1. NO WORD ORDER                                         |
|     "dog bit man" == "man bit dog" (same vector!)         |
|                                                           |
|  2. NO SEMANTIC UNDERSTANDING                             |
|     "excellent" and "wonderful" are treated as            |
|     completely unrelated words                            |
|                                                           |
|  3. HIGH DIMENSIONALITY                                   |
|     Large vocabularies create sparse, high-dimensional    |
|     vectors that waste memory                             |
|                                                           |
|  4. NO CONTEXT                                            |
|     "bank" always gets the same representation            |
|     whether it means river bank or money bank             |
|                                                           |
|  Solution: Word Embeddings (Chapter 4)                    |
|                                                           |
+----------------------------------------------------------+
```

---

## Common Mistakes

1. **Using `fit_transform` on test data** -- Always use `fit_transform` on training data and `transform` on test/new data. If you use `fit_transform` on test data, it creates a different vocabulary and your model will not work.

2. **Ignoring the sparsity issue** -- BoW and TF-IDF vectors are mostly zeros. Use sklearn's sparse matrices instead of converting to dense arrays (with `.toarray()`) unless you need to for display purposes.

3. **Not setting `max_features`** -- With large datasets, the vocabulary can grow to hundreds of thousands of words. Use `max_features` to limit it to a manageable size.

4. **Forgetting to preprocess first** -- If you do not lowercase and clean your text before vectorizing, "Great" and "great" become separate features. CountVectorizer does lowercase by default, but be aware of this.

5. **Assuming high cosine similarity means documents are about the same topic** -- Two documents might share common words without being semantically related.

---

## Best Practices

1. **Use TF-IDF over raw BoW for most tasks** -- TF-IDF almost always outperforms raw word counts because it downweights common, uninformative words.

2. **Experiment with n-grams** -- Adding bigrams (`ngram_range=(1, 2)`) often improves performance by capturing some word order.

3. **Set `min_df` and `max_df`** -- Remove very rare words (`min_df=2` or `min_df=5`) and very common words (`max_df=0.95`) to keep a clean vocabulary.

4. **Use `max_features` for large datasets** -- Limiting to the top 10,000 or 50,000 features keeps your vectors manageable without losing much signal.

5. **Always split data before fitting the vectorizer** -- Fit the vectorizer on training data only. Transform test data using the same fitted vectorizer.

---

## Quick Summary

Bag of Words (BoW) converts text into numerical vectors by counting how many times each word appears. TF-IDF improves on this by giving higher scores to rare, informative words and lower scores to common words. Both methods use sklearn's CountVectorizer and TfidfVectorizer. Cosine similarity measures how similar two document vectors are. While BoW and TF-IDF are simple and effective for many tasks, they have important limitations: they ignore word order, do not understand word meaning, and create high-dimensional sparse vectors.

---

## Key Points

- Computers need numbers, not words. **Vectorization** is the process of converting text to numbers.
- **Bag of Words** counts word occurrences. Simple but treats all words equally.
- **TF-IDF** weighs words by their importance: rare words get high scores, common words get low scores.
- **TF** (Term Frequency) measures how often a word appears in a document.
- **IDF** (Inverse Document Frequency) measures how rare a word is across all documents.
- **CountVectorizer** creates BoW vectors; **TfidfVectorizer** creates TF-IDF vectors.
- **Cosine similarity** measures how similar two vectors are, from 0 (unrelated) to 1 (identical).
- BoW and TF-IDF ignore word order, do not understand synonyms, and create sparse vectors.
- Always use `fit_transform` on training data and `transform` on new/test data.

---

## Practice Questions

1. Explain in your own words why TF-IDF gives the word "the" a low score. What does "Inverse Document Frequency" mean intuitively?

2. Given the documents "I like cats" and "I like dogs," draw the Bag of Words representation. What is the vocabulary? What is each document's vector?

3. Why does cosine similarity show that "the movie was terrible" is more similar to "the movie was excellent" than "the film was wonderful" is? What fundamental limitation does this reveal?

4. What is the difference between `fit_transform` and `transform`? Why is it important to use the right one on test data?

5. How do bigrams help address one of BoW's limitations? Give an example where unigrams would fail but bigrams would succeed.

---

## Exercises

### Exercise 1: Build a Simple Search Engine

Create a basic search engine using TF-IDF and cosine similarity:
1. Define a collection of at least 10 documents (use short paragraphs about different topics).
2. Build a TF-IDF matrix from the collection.
3. Write a function `search(query, n=3)` that takes a search query and returns the top `n` most similar documents.
4. Test it with at least 5 different queries.

### Exercise 2: Compare BoW, TF-IDF, and N-grams

Using a collection of at least 20 product reviews:
1. Create BoW vectors (unigrams only)
2. Create TF-IDF vectors (unigrams only)
3. Create TF-IDF vectors with bigrams (`ngram_range=(1, 2)`)
4. For each method, find the top 10 most important features. Which method produces the most meaningful features?

### Exercise 3: Document Clustering

Using TF-IDF vectors and sklearn's KMeans:
1. Create 15 short documents about 3 different topics (5 each about sports, technology, and cooking).
2. Convert them to TF-IDF vectors.
3. Apply KMeans clustering with `n_clusters=3`.
4. Check if the clusters align with the topics. Print each cluster's documents and top TF-IDF terms.

---

## What Is Next?

In this chapter, you learned that BoW and TF-IDF convert text into numbers by counting words. But you also saw their biggest weakness: they treat every word as independent and cannot understand that "excellent" and "wonderful" mean similar things. In **Chapter 4: Word Embeddings**, you will discover a revolutionary approach that represents words as dense vectors in a mathematical space where similar words are close together. This idea -- that meaning can be captured in geometry -- is one of the most important breakthroughs in NLP history.
