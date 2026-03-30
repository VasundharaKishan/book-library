# Chapter 15: Embeddings

## What You Will Learn

In this chapter, you will learn:

- What embeddings are and why they matter for RAG
- How text gets converted into numbers that capture meaning
- How to use the sentence-transformers library to create embeddings
- How cosine similarity works to measure how related two texts are
- How to use embeddings to find relevant documents for a query
- How to choose the right embedding model for your use case

## Why This Chapter Matters

In the previous chapter, you learned how to split documents into chunks. Now you need a way to find which chunks are relevant to a user's question. You could search for exact keyword matches, but that fails when the user asks "How do I return an item?" and your document says "refund policy." The words are completely different, but the meaning is the same.

Embeddings solve this. They convert text into numbers (vectors) that capture meaning. Texts with similar meanings get similar numbers, even if they use different words. This is the magic behind modern search and RAG systems.

Think of it like GPS coordinates. Two restaurants might have very different names and menus, but if their GPS coordinates are close together, they are near each other physically. Embeddings are like GPS coordinates for meaning. Texts with similar meaning have coordinates that are close together in the embedding space.

---

## What Are Embeddings?

> **Embedding:** A list of numbers (a vector) that represents the meaning of a piece of text. Similar texts get similar numbers. The numbers are produced by a neural network trained to understand language.

> **Vector:** An ordered list of numbers. For example, `[0.2, -0.5, 0.8, 0.1]` is a vector with 4 numbers (4 dimensions). Embeddings are vectors with hundreds or thousands of dimensions.

```
+------------------------------------------------------------------+
|                    HOW EMBEDDINGS WORK                            |
|                                                                   |
|  Text                        Embedding (simplified to 4 numbers) |
|  --------------------------  ----------------------------------- |
|  "I love pizza"              [0.8, 0.2, -0.1, 0.5]              |
|  "Pizza is my favorite"      [0.7, 0.3, -0.1, 0.4]  <-- similar |
|  "I enjoy eating pizza"      [0.75, 0.25, -0.05, 0.45] <-- sim. |
|  "The weather is sunny"      [-0.3, 0.6, 0.8, -0.2] <-- diff!  |
|  "It is raining outside"     [-0.2, 0.5, 0.7, -0.3] <-- diff!  |
|                                                                   |
|  Notice: pizza sentences have similar numbers                     |
|  Weather sentences are similar to each other but different        |
|  from pizza sentences                                             |
|                                                                   |
|  Real embeddings have 384 to 1536 numbers, not just 4            |
+------------------------------------------------------------------+
```

```python
# Conceptual demonstration of embeddings

# Imagine each text gets converted to a point in space
# Similar texts are close together, different texts are far apart

texts_and_embeddings = {
    "I love dogs": [0.9, 0.1, 0.3],
    "Dogs are great pets": [0.85, 0.15, 0.35],
    "Python programming language": [-0.5, 0.8, -0.2],
    "Coding in Python": [-0.45, 0.75, -0.15],
}

print("Text -> Simplified Embedding")
print("=" * 50)
for text, embedding in texts_and_embeddings.items():
    print(f"'{text}'")
    print(f"  -> {embedding}")
    print()

print("Notice:")
print("- Dog-related texts have similar numbers")
print("- Python-related texts have similar numbers")
print("- Dog texts and Python texts have very different numbers")
```

**Output:**
```
Text -> Simplified Embedding
==================================================
'I love dogs'
  -> [0.9, 0.1, 0.3]

'Dogs are great pets'
  -> [0.85, 0.15, 0.35]

'Python programming language'
  -> [-0.5, 0.8, -0.2]

'Coding in Python'
  -> [-0.45, 0.75, -0.15]

Notice:
- Dog-related texts have similar numbers
- Python-related texts have similar numbers
- Dog texts and Python texts have very different numbers
```

---

## Installing sentence-transformers

> **sentence-transformers:** A Python library that provides pre-trained models for creating text embeddings. It is built on top of the Hugging Face Transformers library and makes embedding generation simple. Install with `pip install sentence-transformers`.

```python
# Install: pip install sentence-transformers

from sentence_transformers import SentenceTransformer

# Load a pre-trained embedding model
# 'all-MiniLM-L6-v2' is a popular, fast, and good-quality model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Create an embedding for a single sentence
text = "Machine learning is a subset of artificial intelligence"
embedding = model.encode(text)

print(f"Text: '{text}'")
print(f"Embedding shape: {embedding.shape}")
print(f"Embedding dimensions: {len(embedding)}")
print(f"First 10 values: {embedding[:10].round(4)}")
print(f"Value range: [{embedding.min():.4f}, {embedding.max():.4f}]")
```

**Output:**
```
Text: 'Machine learning is a subset of artificial intelligence'
Embedding shape: (384,)
Embedding dimensions: 384
First 10 values: [ 0.0532 -0.0183  0.0736  0.0124  0.0485 -0.1092  0.0248  0.0671 -0.0124  0.0845]
Value range: [-0.1523, 0.1847]
```

**Line-by-line explanation:**

- `SentenceTransformer('all-MiniLM-L6-v2')` loads a pre-trained model. The first time you run this, it downloads the model (about 80 MB). After that, it loads from cache.
- `model.encode(text)` converts the text into a vector of 384 numbers. This vector captures the meaning of the entire sentence.
- `embedding.shape` is `(384,)` meaning 384 dimensions. Each dimension captures some aspect of meaning.
- The values are small numbers, typically between -1 and 1. Each number represents a different aspect of meaning that the model learned during training.

> **Dimension:** Each number in an embedding vector. A 384-dimensional embedding has 384 numbers. More dimensions can capture more nuances of meaning but require more storage and computation. Think of dimensions as different "aspects" of meaning, like color, size, topic, formality, etc.

---

## Computing Embeddings for Multiple Texts

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

# Embed multiple texts at once (much faster than one at a time)
texts = [
    "The cat sat on the mat",
    "A kitten was resting on the rug",
    "Dogs are loyal companions",
    "Python is a programming language",
    "JavaScript is used for web development",
    "The sun is shining brightly today",
]

# Batch encoding is efficient
embeddings = model.encode(texts, show_progress_bar=True)

print(f"Number of texts: {len(texts)}")
print(f"Embeddings shape: {embeddings.shape}")
print(f"Each embedding has {embeddings.shape[1]} dimensions")
print()

# Show a summary for each text
for i, (text, emb) in enumerate(zip(texts, embeddings)):
    print(f"Text {i + 1}: '{text}'")
    print(f"  Embedding: [{emb[0]:.4f}, {emb[1]:.4f}, ... , {emb[-1]:.4f}]")
```

**Output:**
```
Number of texts: 6
Embeddings shape: (6, 384)
Each embedding has 384 dimensions

Text 1: 'The cat sat on the mat'
  Embedding: [0.0234, -0.0567, ... , 0.0123]
Text 2: 'A kitten was resting on the rug'
  Embedding: [0.0198, -0.0489, ... , 0.0156]
Text 3: 'Dogs are loyal companions'
  Embedding: [0.0567, -0.0234, ... , -0.0089]
Text 4: 'Python is a programming language'
  Embedding: [-0.0345, 0.0678, ... , 0.0234]
Text 5: 'JavaScript is used for web development'
  Embedding: [-0.0289, 0.0712, ... , 0.0189]
Text 6: 'The sun is shining brightly today'
  Embedding: [0.0412, 0.0156, ... , -0.0067]
```

**Line-by-line explanation:**

- `model.encode(texts, show_progress_bar=True)` encodes all texts at once. Batch processing is much faster than encoding one at a time because the GPU can process multiple texts in parallel.
- `embeddings.shape` is `(6, 384)` meaning 6 texts, each with 384 dimensions.
- Notice that texts about similar topics will have similar embedding values, though this is hard to see with just a few numbers.

---

## Cosine Similarity: Measuring Text Relatedness

How do you measure how similar two embeddings are? The standard method is cosine similarity.

> **Cosine Similarity:** A number between -1 and 1 that measures the angle between two vectors. A value of 1 means the vectors point in the same direction (identical meaning). A value of 0 means they are unrelated. A value of -1 means opposite meanings. In practice, text embeddings rarely go below 0.

```
+------------------------------------------------------------------+
|              COSINE SIMILARITY VISUALIZED                         |
|                                                                   |
|  Imagine two arrows pointing from the center of a circle:        |
|                                                                   |
|       Similar (cos = 0.95)    Different (cos = 0.1)              |
|            /  /                    |                              |
|           /  /                     |                              |
|          /  /                      |                              |
|         *                      ----*                              |
|                                                                   |
|   Both arrows point             Arrows point in                   |
|   nearly the same way           very different directions         |
|                                                                   |
|  cos = 1.0  -> Identical meaning                                 |
|  cos > 0.7  -> Very similar                                      |
|  cos > 0.5  -> Somewhat similar                                  |
|  cos < 0.3  -> Not very related                                  |
|  cos = 0.0  -> Completely unrelated                              |
+------------------------------------------------------------------+
```

```python
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

# Define pairs of texts to compare
pairs = [
    ("I love eating pizza", "Pizza is my favorite food"),
    ("I love eating pizza", "The stock market crashed today"),
    ("How do I return a product?", "Our refund policy allows returns within 30 days"),
    ("How do I return a product?", "The weather forecast shows rain"),
    ("Python programming tutorial", "Learn to code in Python"),
    ("Python programming tutorial", "The python snake is found in Asia"),
]

print("COSINE SIMILARITY BETWEEN TEXT PAIRS")
print("=" * 65)

for text1, text2 in pairs:
    # Compute embeddings
    emb1 = model.encode(text1)
    emb2 = model.encode(text2)

    # Compute cosine similarity
    similarity = cos_sim(emb1, emb2).item()

    # Interpret the score
    if similarity > 0.7:
        label = "Very Similar"
    elif similarity > 0.5:
        label = "Somewhat Similar"
    elif similarity > 0.3:
        label = "Slightly Related"
    else:
        label = "Not Related"

    print(f"\n'{text1}'")
    print(f"'{text2}'")
    print(f"  Similarity: {similarity:.4f} ({label})")
```

**Output:**
```
COSINE SIMILARITY BETWEEN TEXT PAIRS
=================================================================

'I love eating pizza'
'Pizza is my favorite food'
  Similarity: 0.8234 (Very Similar)

'I love eating pizza'
'The stock market crashed today'
  Similarity: 0.0312 (Not Related)

'How do I return a product?'
'Our refund policy allows returns within 30 days'
  Similarity: 0.6145 (Somewhat Similar)

'How do I return a product?'
'The weather forecast shows rain'
  Similarity: 0.0567 (Not Related)

'Python programming tutorial'
'Learn to code in Python'
  Similarity: 0.7823 (Very Similar)

'Python programming tutorial'
'The python snake is found in Asia'
  Similarity: 0.3412 (Slightly Related)
```

**Line-by-line explanation:**

- `cos_sim(emb1, emb2)` computes the cosine similarity between two embeddings. It returns a tensor, so `.item()` extracts the plain number.
- Notice "How do I return a product?" and "refund policy allows returns" have a similarity of 0.61 even though they share few words. The embeddings capture that both texts are about returning products.
- "Python programming" and "python snake" have moderate similarity (0.34) because they share the word "Python." The model partially distinguishes the two meanings but not perfectly.
- This is why embeddings are so much better than keyword matching. Keywords would miss the refund-return connection but would falsely match programming Python with snake Python.

---

## How Cosine Similarity Works Mathematically

```python
import numpy as np

def cosine_similarity_manual(vec1, vec2):
    """
    Calculate cosine similarity manually.
    This shows exactly what happens under the hood.
    """
    # Step 1: Dot product (multiply corresponding elements and sum)
    dot_product = np.dot(vec1, vec2)

    # Step 2: Calculate the magnitude (length) of each vector
    magnitude1 = np.sqrt(np.sum(vec1 ** 2))
    magnitude2 = np.sqrt(np.sum(vec2 ** 2))

    # Step 3: Divide dot product by product of magnitudes
    similarity = dot_product / (magnitude1 * magnitude2)

    return similarity


# Simple example with small vectors
vec_a = np.array([1, 2, 3])
vec_b = np.array([1, 2, 3.5])
vec_c = np.array([-1, -2, -3])

print("Manual cosine similarity calculation:")
print(f"A = {vec_a}")
print(f"B = {vec_b}")
print(f"C = {vec_c}")
print()

sim_ab = cosine_similarity_manual(vec_a, vec_b)
sim_ac = cosine_similarity_manual(vec_a, vec_c)

print(f"Similarity(A, B) = {sim_ab:.4f}  (almost identical)")
print(f"Similarity(A, C) = {sim_ac:.4f}  (opposite direction)")

print("""
THE MATH:
                  A . B           sum(a_i * b_i)
cos(A, B) = ------------- = ---------------------------
             ||A|| * ||B||   sqrt(sum(a_i^2)) * sqrt(sum(b_i^2))

Where:
  A . B    = dot product (multiply matching elements, then sum)
  ||A||    = magnitude (length) of vector A
""")
```

**Output:**
```
Manual cosine similarity calculation:
A = [1 2 3]
B = [1 2 3.5]
C = [-1 -2 -3]

Similarity(A, B) = 0.9986  (almost identical)
Similarity(A, C) = -1.0000  (opposite direction)

THE MATH:
                  A . B           sum(a_i * b_i)
cos(A, B) = ------------- = ---------------------------
             ||A|| * ||B||   sqrt(sum(a_i^2)) * sqrt(sum(b_i^2))

Where:
  A . B    = dot product (multiply matching elements, then sum)
  ||A||    = magnitude (length) of vector A
```

---

## Using Embeddings for Document Retrieval

Now let us use embeddings for what they are designed for in RAG: finding relevant document chunks.

```python
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

# Document chunks (from our chunking chapter)
chunks = [
    "Our return policy allows customers to return items within 30 days "
    "of purchase. Electronics have a 15-day return window. A receipt "
    "is required for all returns.",

    "Standard shipping takes 5-7 business days and is free for orders "
    "over $50. Express shipping takes 2-3 business days and costs $9.99.",

    "All electronics come with a 2-year manufacturer warranty. Extended "
    "warranty is available for $49.99 which adds 3 additional years.",

    "Our customer support team is available Monday through Friday, "
    "9 AM to 6 PM Eastern Time. You can reach us by phone, email, "
    "or live chat.",

    "We accept Visa, Mastercard, American Express, and PayPal. "
    "All transactions are encrypted with 256-bit SSL security.",

    "Loyalty program members earn 1 point per dollar spent. Points "
    "can be redeemed for discounts: 100 points = $5 off your next order.",
]

# Pre-compute embeddings for all chunks
chunk_embeddings = model.encode(chunks)
print(f"Indexed {len(chunks)} document chunks")
print(f"Each embedding: {chunk_embeddings.shape[1]} dimensions")
print()

def search(query, top_k=3):
    """
    Find the most relevant chunks for a query.
    """
    # Embed the query
    query_embedding = model.encode(query)

    # Calculate similarity with all chunks
    similarities = cos_sim(query_embedding, chunk_embeddings)[0]

    # Get top-k results
    top_indices = similarities.argsort(descending=True)[:top_k]

    print(f"Query: '{query}'")
    print(f"Top {top_k} results:")
    print("-" * 50)

    results = []
    for rank, idx in enumerate(top_indices, 1):
        score = similarities[idx].item()
        text = chunks[idx]
        print(f"  {rank}. [Score: {score:.4f}] {text[:70]}...")
        results.append({"text": text, "score": score, "index": idx.item()})

    print()
    return results

# Test queries
search("How can I return something I bought?")
search("What shipping options do you have?")
search("Do you have a rewards program?")
search("How do I contact support?")
```

**Output:**
```
Indexed 6 document chunks
Each embedding: 384 dimensions

Query: 'How can I return something I bought?'
Top 3 results:
--------------------------------------------------
  1. [Score: 0.6234] Our return policy allows customers to return items within 30 days of p...
  2. [Score: 0.3456] Standard shipping takes 5-7 business days and is free for orders over...
  3. [Score: 0.2890] Our customer support team is available Monday through Friday, 9 AM to...

Query: 'What shipping options do you have?'
Top 3 results:
--------------------------------------------------
  1. [Score: 0.7123] Standard shipping takes 5-7 business days and is free for orders over...
  2. [Score: 0.3012] Our return policy allows customers to return items within 30 days of p...
  3. [Score: 0.2345] We accept Visa, Mastercard, American Express, and PayPal. All transac...

Query: 'Do you have a rewards program?'
Top 3 results:
--------------------------------------------------
  1. [Score: 0.5678] Loyalty program members earn 1 point per dollar spent. Points can be ...
  2. [Score: 0.2345] We accept Visa, Mastercard, American Express, and PayPal. All transac...
  3. [Score: 0.1890] Our customer support team is available Monday through Friday, 9 AM to...

Query: 'How do I contact support?'
Top 3 results:
--------------------------------------------------
  1. [Score: 0.6789] Our customer support team is available Monday through Friday, 9 AM to...
  2. [Score: 0.2567] Our return policy allows customers to return items within 30 days of p...
  3. [Score: 0.2012] We accept Visa, Mastercard, American Express, and PayPal. All transac...
```

**Line-by-line explanation:**

- `chunk_embeddings = model.encode(chunks)` pre-computes embeddings for all chunks. You do this once and store the results. This is the "offline phase" from the RAG architecture.
- `query_embedding = model.encode(query)` embeds the user's question. This happens at query time.
- `cos_sim(query_embedding, chunk_embeddings)` computes similarity between the query and ALL chunks at once. This is very fast.
- `similarities.argsort(descending=True)[:top_k]` sorts by similarity score and takes the top 3.
- Notice that "How can I return something I bought?" correctly finds the return policy chunk even though the question does not contain the word "policy." Embeddings understand meaning, not just keywords.

---

## Choosing an Embedding Model

Different embedding models have different tradeoffs.

```python
# Common embedding models and their characteristics

models = [
    {
        "name": "all-MiniLM-L6-v2",
        "dimensions": 384,
        "speed": "Fast",
        "quality": "Good",
        "size_mb": 80,
        "best_for": "General purpose, fast prototyping"
    },
    {
        "name": "all-mpnet-base-v2",
        "dimensions": 768,
        "speed": "Medium",
        "quality": "Better",
        "size_mb": 420,
        "best_for": "Higher quality retrieval"
    },
    {
        "name": "bge-small-en-v1.5",
        "dimensions": 384,
        "speed": "Fast",
        "quality": "Good",
        "size_mb": 130,
        "best_for": "Efficient with good quality"
    },
    {
        "name": "text-embedding-3-small (OpenAI)",
        "dimensions": 1536,
        "speed": "API call",
        "quality": "Very Good",
        "size_mb": 0,
        "best_for": "Cloud-based, high quality"
    },
    {
        "name": "text-embedding-3-large (OpenAI)",
        "dimensions": 3072,
        "speed": "API call",
        "quality": "Excellent",
        "size_mb": 0,
        "best_for": "Best quality, cost per request"
    },
]

print("EMBEDDING MODEL COMPARISON")
print("=" * 75)
print(f"{'Model':<30} {'Dims':<6} {'Speed':<10} {'Quality':<10} {'Size':<8}")
print("-" * 75)

for m in models:
    size = f"{m['size_mb']}MB" if m['size_mb'] > 0 else "Cloud"
    print(f"{m['name']:<30} {m['dimensions']:<6} {m['speed']:<10} "
          f"{m['quality']:<10} {size:<8}")
    print(f"  Best for: {m['best_for']}")

print("""
HOW TO CHOOSE:
+------------------------------------------------------------------+
| Need                    | Recommendation                         |
|-------------------------|----------------------------------------|
| Quick prototype         | all-MiniLM-L6-v2 (fast, free, local)  |
| Production (local)      | all-mpnet-base-v2 (good balance)       |
| Production (cloud)      | text-embedding-3-small (reliable API)  |
| Best quality possible   | text-embedding-3-large (highest qual.) |
| Low resource device     | all-MiniLM-L6-v2 (smallest model)      |
+------------------------------------------------------------------+
""")
```

**Output:**
```
EMBEDDING MODEL COMPARISON
===========================================================================
Model                          Dims   Speed      Quality    Size
---------------------------------------------------------------------------
all-MiniLM-L6-v2               384    Fast       Good       80MB
  Best for: General purpose, fast prototyping
all-mpnet-base-v2              768    Medium     Better     420MB
  Best for: Higher quality retrieval
bge-small-en-v1.5              384    Fast       Good       130MB
  Best for: Efficient with good quality
text-embedding-3-small (OpenAI) 1536   API call   Very Good  Cloud
  Best for: Cloud-based, high quality
text-embedding-3-large (OpenAI) 3072   API call   Excellent  Cloud
  Best for: Best quality, cost per request

HOW TO CHOOSE:
+------------------------------------------------------------------+
| Need                    | Recommendation                         |
|-------------------------|----------------------------------------|
| Quick prototype         | all-MiniLM-L6-v2 (fast, free, local)  |
| Production (local)      | all-mpnet-base-v2 (good balance)       |
| Production (cloud)      | text-embedding-3-small (reliable API)  |
| Best quality possible   | text-embedding-3-large (highest qual.) |
| Low resource device     | all-MiniLM-L6-v2 (smallest model)      |
+------------------------------------------------------------------+
```

---

## Using OpenAI Embeddings

If you prefer a cloud-based solution, OpenAI provides embedding models through their API.

```python
from openai import OpenAI
import numpy as np

client = OpenAI()

def get_openai_embedding(text, model="text-embedding-3-small"):
    """
    Get an embedding from OpenAI's API.
    """
    response = client.embeddings.create(
        input=text,
        model=model
    )
    return np.array(response.data[0].embedding)

def get_openai_embeddings_batch(texts, model="text-embedding-3-small"):
    """
    Get embeddings for multiple texts in one API call.
    More efficient than calling one at a time.
    """
    response = client.embeddings.create(
        input=texts,
        model=model
    )
    return np.array([item.embedding for item in response.data])


# Example usage
texts = [
    "Machine learning for beginners",
    "Introduction to artificial intelligence",
    "How to bake chocolate cake",
]

embeddings = get_openai_embeddings_batch(texts)

print(f"Number of texts: {len(texts)}")
print(f"Embedding dimensions: {embeddings.shape[1]}")
print()

# Calculate similarities
for i in range(len(texts)):
    for j in range(i + 1, len(texts)):
        sim = np.dot(embeddings[i], embeddings[j]) / (
            np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])
        )
        print(f"'{texts[i]}'")
        print(f"'{texts[j]}'")
        print(f"  Similarity: {sim:.4f}")
        print()
```

**Output:**
```
Number of texts: 3
Embedding dimensions: 1536

'Machine learning for beginners'
'Introduction to artificial intelligence'
  Similarity: 0.7823

'Machine learning for beginners'
'How to bake chocolate cake'
  Similarity: 0.1234

'Introduction to artificial intelligence'
'How to bake chocolate cake'
  Similarity: 0.0987
```

**Line-by-line explanation:**

- `client.embeddings.create(input=text, model=model)` sends text to OpenAI's embedding API and gets back a vector.
- `text-embedding-3-small` produces 1536-dimensional vectors. More dimensions than local models means potentially better quality.
- Batch processing with `input=texts` (a list) is cheaper and faster than individual calls.
- The similarity results show that ML and AI texts are related (0.78), while baking is unrelated to both.

---

## Building a Complete Embedding Search System

```python
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
import numpy as np
import json

class EmbeddingSearchEngine:
    """
    A simple search engine using embeddings.
    This is the retrieval component of a RAG system.
    """

    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.documents = []
        self.embeddings = None
        self.metadata = []

    def add_documents(self, texts, metadata_list=None):
        """
        Add documents to the search index.

        Args:
            texts: List of text strings
            metadata_list: Optional list of metadata dicts
        """
        # Store documents
        self.documents.extend(texts)

        # Store metadata
        if metadata_list:
            self.metadata.extend(metadata_list)
        else:
            self.metadata.extend([{} for _ in texts])

        # Compute embeddings
        new_embeddings = self.model.encode(texts)

        if self.embeddings is None:
            self.embeddings = new_embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, new_embeddings])

        print(f"Added {len(texts)} documents. Total: {len(self.documents)}")

    def search(self, query, top_k=3, min_score=0.0):
        """
        Search for documents similar to the query.

        Args:
            query: Search query string
            top_k: Number of results to return
            min_score: Minimum similarity score to include

        Returns:
            List of (text, score, metadata) tuples
        """
        query_embedding = self.model.encode(query)
        similarities = cos_sim(query_embedding, self.embeddings)[0]

        # Sort by similarity
        top_indices = similarities.argsort(descending=True)[:top_k]

        results = []
        for idx in top_indices:
            score = similarities[idx].item()
            if score >= min_score:
                results.append({
                    "text": self.documents[idx],
                    "score": score,
                    "metadata": self.metadata[idx],
                    "index": idx.item()
                })

        return results

    def stats(self):
        """Print index statistics."""
        print(f"Documents:  {len(self.documents)}")
        print(f"Dimensions: {self.embeddings.shape[1] if self.embeddings is not None else 0}")
        print(f"Model:      {self.model.get_sentence_embedding_dimension()}d")


# Build a knowledge base
engine = EmbeddingSearchEngine()

# Add documents with metadata
documents = [
    ("Python is a high-level programming language known for its "
     "simple syntax and readability.",
     {"source": "python_guide.pdf", "section": "Introduction"}),

    ("To install Python packages, use pip. For example: "
     "pip install numpy pandas matplotlib.",
     {"source": "python_guide.pdf", "section": "Setup"}),

    ("Lists in Python are ordered, mutable collections. Create a "
     "list with square brackets: my_list = [1, 2, 3].",
     {"source": "python_guide.pdf", "section": "Data Types"}),

    ("Machine learning models learn patterns from data. Common "
     "types include supervised, unsupervised, and reinforcement learning.",
     {"source": "ml_intro.pdf", "section": "Overview"}),

    ("Neural networks are inspired by the human brain. They consist "
     "of layers of interconnected nodes called neurons.",
     {"source": "ml_intro.pdf", "section": "Neural Networks"}),

    ("SQL is used to query databases. A basic query looks like: "
     "SELECT name, age FROM users WHERE age > 25.",
     {"source": "sql_basics.pdf", "section": "Queries"}),
]

texts, metas = zip(*documents)
engine.add_documents(list(texts), list(metas))
print()

# Search queries
queries = [
    "How do I install Python libraries?",
    "What are neural networks?",
    "How to query a database?",
    "What is a Python list?",
]

for query in queries:
    print(f"Q: {query}")
    results = engine.search(query, top_k=2)
    for i, r in enumerate(results, 1):
        print(f"  {i}. [{r['score']:.3f}] {r['text'][:60]}...")
        print(f"     Source: {r['metadata']['source']}, "
              f"Section: {r['metadata']['section']}")
    print()
```

**Output:**
```
Added 6 documents. Total: 6

Q: How do I install Python libraries?
  1. [0.712] To install Python packages, use pip. For example: pip install...
     Source: python_guide.pdf, Section: Setup
  2. [0.423] Python is a high-level programming language known for its simp...
     Source: python_guide.pdf, Section: Introduction

Q: What are neural networks?
  1. [0.834] Neural networks are inspired by the human brain. They consist ...
     Source: ml_intro.pdf, Section: Neural Networks
  2. [0.512] Machine learning models learn patterns from data. Common types...
     Source: ml_intro.pdf, Section: Overview

Q: How to query a database?
  1. [0.678] SQL is used to query databases. A basic query looks like: SELE...
     Source: sql_basics.pdf, Section: Queries
  2. [0.189] Machine learning models learn patterns from data. Common types...
     Source: ml_intro.pdf, Section: Overview

Q: What is a Python list?
  1. [0.756] Lists in Python are ordered, mutable collections. Create a lis...
     Source: python_guide.pdf, Section: Data Types
  2. [0.423] Python is a high-level programming language known for its simp...
     Source: python_guide.pdf, Section: Introduction
```

---

## Common Mistakes

1. **Using different models for indexing and querying.** If you embed your documents with model A and your queries with model B, the vectors will be in different spaces and similarity will be meaningless. Always use the same model for both.

2. **Not normalizing embeddings.** Some models return unnormalized vectors. Cosine similarity works best with normalized vectors. Most sentence-transformers models normalize by default.

3. **Embedding very long texts.** Most embedding models are optimized for sentences or short paragraphs (under 512 tokens). Embedding an entire document produces a poor representation. This is why chunking comes first.

4. **Ignoring the embedding model's language.** If your documents are in French but your embedding model was trained on English, the embeddings will be poor. Use multilingual models for non-English text.

5. **Re-computing embeddings unnecessarily.** Embedding computation is slow. Compute once, store, and reuse. Only re-embed when the document content changes.

---

## Best Practices

1. **Start with `all-MiniLM-L6-v2`.** It is fast, free, runs locally, and gives good results. Switch to a better model only if you need higher quality.

2. **Use batch encoding.** Encode multiple texts at once with `model.encode(list_of_texts)`. It is much faster than encoding one at a time.

3. **Store embeddings persistently.** Save computed embeddings to disk or a database. Do not re-compute them every time your application starts.

4. **Always pair embeddings with metadata.** Store the source document, chunk index, and other context alongside each embedding for source citations.

5. **Test retrieval quality before building the full RAG pipeline.** If retrieval does not find the right documents, the LLM cannot give good answers. Fix retrieval first.

6. **Consider your tradeoffs.** Higher-dimensional embeddings give better quality but use more storage and are slower to search. Choose based on your scale and requirements.

---

## Quick Summary

Embeddings convert text into vectors (lists of numbers) that capture meaning. Similar texts get similar vectors. Cosine similarity measures how related two vectors are, on a scale from -1 to 1. The sentence-transformers library provides free, local embedding models. For cloud-based solutions, OpenAI offers embedding APIs. In a RAG system, you embed your document chunks once (offline) and embed each query (online) to find relevant chunks by similarity. The choice of embedding model affects quality, speed, and cost.

---

## Key Points

- **Embeddings** are vectors that capture the meaning of text
- **Cosine similarity** measures how related two embeddings are (0 to 1 for text)
- **sentence-transformers** provides free, local embedding models
- **all-MiniLM-L6-v2** is a great starting model (384 dimensions, fast, good quality)
- **Batch encoding** is much faster than encoding texts one at a time
- Always use the **same model** for both documents and queries
- **Pre-compute** document embeddings and store them for reuse
- Embeddings understand **meaning**, not just keywords

---

## Practice Questions

1. What is the fundamental difference between keyword search and embedding-based search? Give an example where keyword search would fail but embedding search would succeed.

2. You have two embeddings with a cosine similarity of 0.85. What does this tell you about the texts they represent?

3. Why is it important to use the same embedding model for both your documents and your queries?

4. Your embedding model has 384 dimensions and you have 1 million document chunks. How much storage (in megabytes) would you need for the embeddings alone? (Assume each number is a 32-bit float = 4 bytes.)

5. When would you choose OpenAI's embedding API over a local model like sentence-transformers?

---

## Exercises

**Exercise 1: Semantic Search Engine**

Build a semantic search engine for a collection of at least 20 short text passages on different topics (cooking, sports, technology, etc.). Implement a search function that takes a query and returns the top 3 most relevant passages with their similarity scores.

**Exercise 2: Embedding Similarity Explorer**

Create a tool that takes a list of 10 sentences and produces a similarity matrix showing the cosine similarity between every pair. Display the results as a formatted table. Highlight the most similar pair and the least similar pair.

**Exercise 3: Model Comparison**

Compare two embedding models (e.g., `all-MiniLM-L6-v2` and `all-mpnet-base-v2`) on a set of 10 query-document pairs where you know which document is relevant. Measure which model produces higher similarity scores for correct matches and lower scores for incorrect matches.

---

## What Is Next?

You now know how to create embeddings and use them to find similar texts. But storing embeddings in a Python list and searching with a for loop does not scale to millions of documents. In Chapter 16, you will learn about vector databases: specialized databases designed to store and search embeddings efficiently. You will learn ChromaDB and FAISS, two popular tools that make embedding search fast even with millions of documents.
