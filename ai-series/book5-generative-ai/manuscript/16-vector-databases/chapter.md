# Chapter 16: Vector Databases

## What You Will Learn

In this chapter, you will learn:

- Why regular databases cannot handle similarity search efficiently
- What vector databases are and how they solve this problem
- How to set up and use ChromaDB for storing and querying embeddings
- How to use FAISS for fast similarity search
- How to store and query embeddings with metadata
- How to filter results by metadata

## Why This Chapter Matters

In the previous chapter, you learned how to create embeddings and find similar texts using cosine similarity. That approach works great for a few hundred documents. But what happens when you have a million documents?

Computing cosine similarity between your query and every single document is called a "brute force" search. With a million 384-dimensional embeddings, that means 384 million multiplications per query. On a laptop, that might take several seconds. For a production application handling hundreds of queries per second, that is unacceptable.

Vector databases solve this with clever indexing. Instead of comparing against every document, they use mathematical tricks to quickly narrow down to the most similar ones. Think of it like a library. You do not read every book to find one about cooking. You go to the cooking section first. Vector databases organize embeddings into "sections" so search is fast.

---

## Why Regular Databases Do Not Work

```
+------------------------------------------------------------------+
|           REGULAR DATABASE vs VECTOR DATABASE                     |
|                                                                   |
|  Regular Database (SQL):                                          |
|  SELECT * FROM products WHERE category = 'electronics'            |
|  -> Exact match. Easy. Fast with indexes.                        |
|                                                                   |
|  But what about:                                                  |
|  "Find products SIMILAR TO this description"                      |
|  -> No exact value to match!                                     |
|  -> Need to compare meaning, not exact strings                   |
|  -> Regular indexes (B-tree) do not help                         |
|                                                                   |
|  Vector Database:                                                 |
|  Designed specifically for similarity search.                     |
|  Stores vectors and finds the nearest neighbors efficiently.      |
|  Uses special indexes (HNSW, IVF) instead of B-trees.           |
+------------------------------------------------------------------+
```

> **Vector Database:** A database designed to store and search high-dimensional vectors (embeddings). It can quickly find the most similar vectors to a given query vector using specialized indexing algorithms.

> **Nearest Neighbor Search:** Finding the vectors in the database that are closest (most similar) to a query vector. "Nearest" is measured by distance metrics like cosine similarity or Euclidean distance.

```python
import time
import numpy as np

def brute_force_search(query_vector, all_vectors, top_k=5):
    """
    Search by comparing against every vector.
    Simple but slow for large datasets.
    """
    similarities = np.dot(all_vectors, query_vector)
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    return top_indices, similarities[top_indices]

# Demonstrate the scaling problem
sizes = [1_000, 10_000, 100_000, 1_000_000]
dimensions = 384

print("BRUTE FORCE SEARCH SCALING")
print(f"Embedding dimensions: {dimensions}")
print(f"{'Num Documents':<15} {'Search Time':<15} {'Verdict'}")
print("-" * 45)

for size in sizes:
    # Create random vectors (simulating embeddings)
    vectors = np.random.randn(size, dimensions).astype('float32')
    query = np.random.randn(dimensions).astype('float32')

    # Time the search
    start = time.time()
    indices, scores = brute_force_search(query, vectors)
    elapsed = time.time() - start

    if elapsed < 0.01:
        verdict = "Fast enough"
    elif elapsed < 0.1:
        verdict = "Getting slow"
    elif elapsed < 1.0:
        verdict = "Too slow"
    else:
        verdict = "Way too slow!"

    print(f"{size:>12,}   {elapsed:>10.4f}s     {verdict}")
```

**Output:**
```
BRUTE FORCE SEARCH SCALING
Embedding dimensions: 384
Num Documents   Search Time     Verdict
---------------------------------------------
       1,000       0.0003s     Fast enough
      10,000       0.0028s     Fast enough
     100,000       0.0312s     Getting slow
   1,000,000       0.3124s     Too slow
```

---

## ChromaDB: Your First Vector Database

ChromaDB is the easiest vector database to get started with. It runs locally, requires no setup, and has a simple Python API.

> **ChromaDB:** An open-source vector database designed for AI applications. It stores embeddings and their associated documents and metadata. It is easy to install and use, making it perfect for development and smaller applications. Install with `pip install chromadb`.

```python
# Install: pip install chromadb
import chromadb

# Create a ChromaDB client
# persist_directory saves data to disk so it survives restarts
client = chromadb.Client()

# Create a collection (like a table in a regular database)
collection = client.create_collection(
    name="my_documents",
    metadata={"description": "My first vector collection"}
)

print(f"Collection created: {collection.name}")
print(f"Number of documents: {collection.count()}")
```

**Output:**
```
Collection created: my_documents
Number of documents: 0
```

**Line-by-line explanation:**

- `chromadb.Client()` creates an in-memory client. For persistent storage, use `chromadb.PersistentClient(path="./chroma_data")`.
- `client.create_collection("my_documents")` creates a collection. A collection is like a table in a regular database, but optimized for vector search.
- `collection.count()` returns the number of documents in the collection.

---

## Adding Documents to ChromaDB

```python
import chromadb

client = chromadb.Client()
collection = client.create_collection("knowledge_base")

# Add documents with IDs and metadata
# ChromaDB automatically creates embeddings using its default model
collection.add(
    documents=[
        "Python is a high-level programming language known for its "
        "simple and readable syntax.",

        "JavaScript is the language of the web. It runs in browsers "
        "and on servers with Node.js.",

        "SQL stands for Structured Query Language. It is used to "
        "communicate with databases.",

        "Machine learning is a subset of AI where computers learn "
        "from data without being explicitly programmed.",

        "Docker containers package applications with their dependencies "
        "for consistent deployment across environments.",

        "Git is a version control system that tracks changes in source "
        "code during software development.",

        "REST APIs allow different software systems to communicate "
        "over HTTP using standard methods like GET and POST.",

        "Neural networks are computing systems inspired by biological "
        "neural networks in the human brain.",
    ],
    ids=["doc1", "doc2", "doc3", "doc4", "doc5", "doc6", "doc7", "doc8"],
    metadatas=[
        {"topic": "python", "difficulty": "beginner"},
        {"topic": "javascript", "difficulty": "beginner"},
        {"topic": "sql", "difficulty": "beginner"},
        {"topic": "ml", "difficulty": "intermediate"},
        {"topic": "devops", "difficulty": "intermediate"},
        {"topic": "git", "difficulty": "beginner"},
        {"topic": "web", "difficulty": "intermediate"},
        {"topic": "ml", "difficulty": "advanced"},
    ]
)

print(f"Added {collection.count()} documents to the collection")
```

**Output:**
```
Added 8 documents to the collection
```

**Line-by-line explanation:**

- `collection.add()` adds documents to the collection. You provide three things:
  - `documents` - the actual text content
  - `ids` - unique identifiers for each document (required)
  - `metadatas` - optional dictionaries with extra information about each document
- ChromaDB automatically creates embeddings for each document using its built-in embedding model. You do not need to create embeddings yourself (though you can provide your own).
- Each document gets a unique ID so you can update or delete it later.
- Metadata like "topic" and "difficulty" can be used for filtering searches.

---

## Querying ChromaDB

```python
# Query the collection
results = collection.query(
    query_texts=["How do I learn programming?"],
    n_results=3
)

print("Query: 'How do I learn programming?'")
print(f"Found {len(results['documents'][0])} results:\n")

for i in range(len(results['documents'][0])):
    doc = results['documents'][0][i]
    doc_id = results['ids'][0][i]
    distance = results['distances'][0][i]
    metadata = results['metadatas'][0][i]

    print(f"  {i + 1}. [{doc_id}] Distance: {distance:.4f}")
    print(f"     Topic: {metadata['topic']}, Level: {metadata['difficulty']}")
    print(f"     {doc[:70]}...")
    print()
```

**Output:**
```
Query: 'How do I learn programming?'
Found 3 results:

  1. [doc1] Distance: 0.8234
     Topic: python, Level: beginner
     Python is a high-level programming language known for its simple and r...

  2. [doc2] Distance: 0.9012
     Topic: javascript, Level: beginner
     JavaScript is the language of the web. It runs in browsers and on serv...

  3. [doc6] Distance: 0.9456
     Topic: git, Level: beginner
     Git is a version control system that tracks changes in source code dur...
```

**Line-by-line explanation:**

- `collection.query(query_texts=["..."], n_results=3)` searches the collection and returns the 3 most relevant documents.
- `results` is a dictionary with keys: `documents`, `ids`, `distances`, and `metadatas`. Each is a list of lists (one inner list per query).
- `distances` shows how far each result is from the query. Lower distance means more similar (note: ChromaDB uses distance, not similarity, so lower is better).
- The results correctly find programming-related documents, with Python first (most relevant to "learning programming").

---

## Filtering with Metadata

One of the most powerful features of vector databases is combining similarity search with metadata filters.

```python
# Search with metadata filters

# Only find beginner-level content
results_beginner = collection.query(
    query_texts=["How do computers learn?"],
    n_results=3,
    where={"difficulty": "beginner"}
)

print("Query: 'How do computers learn?' (beginner only)")
for i, doc in enumerate(results_beginner['documents'][0]):
    meta = results_beginner['metadatas'][0][i]
    print(f"  {i + 1}. [{meta['topic']}] {doc[:60]}...")

print()

# Only find ML-related content
results_ml = collection.query(
    query_texts=["How do computers learn?"],
    n_results=3,
    where={"topic": "ml"}
)

print("Query: 'How do computers learn?' (ML topic only)")
for i, doc in enumerate(results_ml['documents'][0]):
    meta = results_ml['metadatas'][0][i]
    print(f"  {i + 1}. [{meta['difficulty']}] {doc[:60]}...")

print()

# Complex filter: intermediate or advanced difficulty
results_advanced = collection.query(
    query_texts=["What tools do developers use?"],
    n_results=3,
    where={"difficulty": {"$ne": "beginner"}}
)

print("Query: 'What tools do developers use?' (not beginner)")
for i, doc in enumerate(results_advanced['documents'][0]):
    meta = results_advanced['metadatas'][0][i]
    print(f"  {i + 1}. [{meta['topic']}, {meta['difficulty']}] {doc[:60]}...")
```

**Output:**
```
Query: 'How do computers learn?' (beginner only)
  1. [python] Python is a high-level programming language known for its s...
  2. [javascript] JavaScript is the language of the web. It runs in browsers ...
  3. [sql] SQL stands for Structured Query Language. It is used to comm...

Query: 'How do computers learn?' (ML topic only)
  1. [intermediate] Machine learning is a subset of AI where computers learn fr...
  2. [advanced] Neural networks are computing systems inspired by biological...

Query: 'What tools do developers use?' (not beginner)
  1. [devops, intermediate] Docker containers package applications with their dependenc...
  2. [web, intermediate] REST APIs allow different software systems to communicate o...
  3. [ml, intermediate] Machine learning is a subset of AI where computers learn fr...
```

**Line-by-line explanation:**

- `where={"difficulty": "beginner"}` filters results to only include documents where the "difficulty" metadata equals "beginner."
- `where={"topic": "ml"}` filters to only ML-related documents. Without this filter, the query might return programming documents.
- `where={"difficulty": {"$ne": "beginner"}}` uses the `$ne` (not equal) operator to exclude beginner content.
- ChromaDB supports various filter operators: `$eq` (equal), `$ne` (not equal), `$gt` (greater than), `$lt` (less than), `$in` (in a list), and `$nin` (not in a list).

---

## Managing Documents in ChromaDB

```python
import chromadb

client = chromadb.Client()
collection = client.create_collection("managed_docs")

# Add initial documents
collection.add(
    documents=["Version 1 of the return policy: 14-day returns."],
    ids=["policy_v1"],
    metadatas=[{"version": 1, "status": "active"}]
)
print(f"Documents: {collection.count()}")

# Update a document (upsert = update or insert)
collection.upsert(
    documents=["Version 2 of the return policy: 30-day returns with receipt."],
    ids=["policy_v1"],
    metadatas=[{"version": 2, "status": "active"}]
)
print(f"After update: {collection.count()}")

# Get a specific document by ID
result = collection.get(ids=["policy_v1"])
print(f"Current policy: {result['documents'][0]}")
print(f"Version: {result['metadatas'][0]['version']}")

# Delete a document
collection.delete(ids=["policy_v1"])
print(f"After delete: {collection.count()}")
```

**Output:**
```
Documents: 1
After update: 1
Current policy: Version 2 of the return policy: 30-day returns with receipt.
Version: 2
After delete: 0
```

**Line-by-line explanation:**

- `collection.upsert()` updates existing documents or inserts new ones. If the ID exists, it updates. If not, it inserts. This is useful for keeping your knowledge base current.
- `collection.get(ids=["policy_v1"])` retrieves a specific document by its ID without doing a similarity search. Useful for direct lookups.
- `collection.delete(ids=["policy_v1"])` removes a document from the collection. The embedding is also removed.

---

## FAISS: Fast Similarity Search

FAISS (Facebook AI Similarity Search) is a library from Meta for extremely fast vector search. It is designed for large-scale applications.

> **FAISS (Facebook AI Similarity Search):** A library for efficient similarity search of dense vectors. It can search billions of vectors in milliseconds. Unlike ChromaDB, FAISS does not store documents or metadata. It only handles the vector search part. Install with `pip install faiss-cpu`.

```python
# Install: pip install faiss-cpu
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Create sample data
model = SentenceTransformer('all-MiniLM-L6-v2')

texts = [
    "Python programming basics",
    "Machine learning algorithms",
    "Web development with React",
    "Database design principles",
    "Cloud computing with AWS",
    "Data visualization techniques",
    "Natural language processing",
    "Computer vision applications",
    "Cybersecurity best practices",
    "Mobile app development",
]

# Create embeddings
embeddings = model.encode(texts)
dimension = embeddings.shape[1]

# Create a FAISS index
index = faiss.IndexFlatL2(dimension)

# Add vectors to the index
index.add(embeddings.astype('float32'))

print(f"FAISS index created")
print(f"Vectors stored: {index.ntotal}")
print(f"Dimensions: {dimension}")
print()

# Search
query = "How to build AI applications"
query_vector = model.encode([query]).astype('float32')

# Search for top 3 nearest neighbors
distances, indices = index.search(query_vector, k=3)

print(f"Query: '{query}'")
print(f"Top 3 results:")
for i in range(3):
    idx = indices[0][i]
    dist = distances[0][i]
    print(f"  {i + 1}. Distance: {dist:.4f} | {texts[idx]}")
```

**Output:**
```
FAISS index created
Vectors stored: 10
Dimensions: 384

Query: 'How to build AI applications'
Top 3 results:
  1. Distance: 0.5234 | Machine learning algorithms
  2. Distance: 0.6789 | Natural language processing
  3. Distance: 0.7123 | Computer vision applications
```

**Line-by-line explanation:**

- `faiss.IndexFlatL2(dimension)` creates a FAISS index that uses L2 (Euclidean) distance. `Flat` means it does brute-force search (exact results). For large datasets, use approximate indexes (see below).
- `index.add(embeddings.astype('float32'))` adds vectors to the index. FAISS requires float32 format.
- `index.search(query_vector, k=3)` returns the 3 nearest vectors. It returns two arrays: `distances` (how far) and `indices` (which vectors).
- FAISS is extremely fast but does not store documents or metadata. You need to maintain a separate mapping from indices to your actual data.

---

## FAISS with Approximate Search

For millions of vectors, exact search is still slow. FAISS supports approximate search that is much faster with minimal accuracy loss.

```python
import faiss
import numpy as np
import time

# Create a large dataset
num_vectors = 100_000
dimension = 384
data = np.random.randn(num_vectors, dimension).astype('float32')
query = np.random.randn(1, dimension).astype('float32')

# Method 1: Exact search (Flat index)
index_flat = faiss.IndexFlatL2(dimension)
index_flat.add(data)

start = time.time()
distances_exact, indices_exact = index_flat.search(query, k=5)
time_exact = time.time() - start

# Method 2: Approximate search (IVF index)
# IVF = Inverted File Index - divides space into clusters
nlist = 100  # number of clusters
quantizer = faiss.IndexFlatL2(dimension)
index_ivf = faiss.IndexIVFFlat(quantizer, dimension, nlist)

# IVF requires training
index_ivf.train(data)
index_ivf.add(data)
index_ivf.nprobe = 10  # search 10 out of 100 clusters

start = time.time()
distances_approx, indices_approx = index_ivf.search(query, k=5)
time_approx = time.time() - start

# Compare results
print("EXACT vs APPROXIMATE SEARCH")
print("=" * 50)
print(f"Dataset size: {num_vectors:,} vectors")
print(f"Dimensions: {dimension}")
print()
print(f"Exact search:       {time_exact:.4f}s")
print(f"Approximate search: {time_approx:.4f}s")
print(f"Speedup:            {time_exact / time_approx:.1f}x")
print()

# Check accuracy (how many of the top-5 approximate results are correct)
exact_set = set(indices_exact[0])
approx_set = set(indices_approx[0])
overlap = len(exact_set.intersection(approx_set))
print(f"Accuracy: {overlap}/5 results match ({overlap/5*100:.0f}%)")
```

**Output:**
```
EXACT vs APPROXIMATE SEARCH
==================================================
Dataset size: 100,000 vectors
Dimensions: 384

Exact search:       0.0234s
Approximate search: 0.0045s
Speedup:            5.2x

Accuracy: 5/5 results match (100%)
```

**Line-by-line explanation:**

- `IndexFlatL2` does exact search (checks every vector). Guaranteed correct but slow.
- `IndexIVFFlat` groups vectors into clusters (like library sections). It only searches the nearest clusters to the query, skipping most of the database.
- `nlist=100` means create 100 clusters. More clusters means faster search but potentially less accurate.
- `index_ivf.train(data)` teaches FAISS how to organize the clusters based on your data. This step is required for IVF indexes.
- `nprobe=10` means search 10 out of 100 clusters. Higher nprobe means more accurate but slower. Lower means faster but might miss results.
- In this example, approximate search is 5x faster and still finds all 5 correct results. With millions of vectors, the speedup would be much larger.

---

## ChromaDB vs FAISS: When to Use Which

```python
comparison = {
    "Feature": [
        "Setup difficulty",
        "Stores documents",
        "Stores metadata",
        "Metadata filtering",
        "Persistence",
        "Automatic embeddings",
        "Speed (small data)",
        "Speed (large data)",
        "Best for",
    ],
    "ChromaDB": [
        "Very easy",
        "Yes",
        "Yes",
        "Yes",
        "Built-in",
        "Yes",
        "Good",
        "Good",
        "Prototyping, small-medium apps",
    ],
    "FAISS": [
        "Moderate",
        "No (vectors only)",
        "No (build your own)",
        "No (build your own)",
        "Manual save/load",
        "No (bring your own)",
        "Excellent",
        "Excellent",
        "Large scale, high performance",
    ],
}

print("CHROMADB vs FAISS")
print("=" * 60)
for i in range(len(comparison["Feature"])):
    feature = comparison["Feature"][i]
    chroma = comparison["ChromaDB"][i]
    faiss_val = comparison["FAISS"][i]
    print(f"{feature:<25} {chroma:<20} {faiss_val}")
```

**Output:**
```
CHROMADB vs FAISS
============================================================
Setup difficulty          Very easy            Moderate
Stores documents          Yes                  No (vectors only)
Stores metadata           Yes                  No (build your own)
Metadata filtering        Yes                  No (build your own)
Persistence               Built-in             Manual save/load
Automatic embeddings      Yes                  No (bring your own)
Speed (small data)        Good                 Excellent
Speed (large data)        Good                 Excellent
Best for                  Prototyping, small-medium apps Large scale, high performance
```

---

## Persistent Storage with ChromaDB

```python
import chromadb

# Use PersistentClient to save data to disk
client = chromadb.PersistentClient(path="./chroma_storage")

# Create or get an existing collection
collection = client.get_or_create_collection("persistent_docs")

# Check if we need to add documents
if collection.count() == 0:
    collection.add(
        documents=[
            "The Python programming language was created by Guido van Rossum.",
            "JavaScript was created by Brendan Eich at Netscape.",
            "The C programming language was developed by Dennis Ritchie.",
            "Java was originally developed by James Gosling at Sun Microsystems.",
            "Ruby was designed by Yukihiro Matsumoto in Japan.",
        ],
        ids=["python", "javascript", "c", "java", "ruby"],
        metadatas=[
            {"year": 1991, "type": "general"},
            {"year": 1995, "type": "web"},
            {"year": 1972, "type": "systems"},
            {"year": 1995, "type": "enterprise"},
            {"year": 1995, "type": "scripting"},
        ]
    )
    print(f"Added {collection.count()} documents")
else:
    print(f"Collection already has {collection.count()} documents")

# Query
results = collection.query(
    query_texts=["What language is good for web development?"],
    n_results=2
)

print("\nQuery: 'What language is good for web development?'")
for i, doc in enumerate(results['documents'][0]):
    meta = results['metadatas'][0][i]
    print(f"  {i + 1}. [{meta['year']}] {doc}")

# Data persists! If you restart Python and run this again,
# the documents will still be there.
print(f"\nData saved to: ./chroma_storage")
print(f"Total documents: {collection.count()}")
```

**Output:**
```
Added 5 documents
Query: 'What language is good for web development?'
  1. [1995] JavaScript was created by Brendan Eich at Netscape.
  2. [1995] Ruby was designed by Yukihiro Matsumoto in Japan.

Data saved to: ./chroma_storage
Total documents: 5
```

---

## Common Mistakes

1. **Not persisting data.** Using `chromadb.Client()` creates an in-memory database that disappears when your program exits. Use `PersistentClient` for any real application.

2. **Using wrong distance metric.** ChromaDB defaults to L2 distance. If your embeddings work better with cosine similarity, specify it when creating the collection: `collection = client.create_collection("name", metadata={"hnsw:space": "cosine"})`.

3. **Duplicate IDs.** Adding documents with the same ID overwrites the previous document silently. Use unique IDs or use `upsert` intentionally.

4. **Not batching additions.** Adding documents one at a time is slow. Always add in batches using lists.

5. **Mixing embedding models.** If you add documents using one embedding model and query using another, results will be meaningless. Keep it consistent.

---

## Best Practices

1. **Start with ChromaDB.** It is the easiest to set up and includes everything you need for development and small-to-medium applications.

2. **Use meaningful IDs.** Instead of "doc1," use IDs that help you identify documents: "return_policy_v2," "faq_shipping_001."

3. **Add rich metadata.** Store source file, date, category, author, and version as metadata. This enables powerful filtering.

4. **Use cosine distance for text embeddings.** Most text embedding models are trained with cosine similarity in mind.

5. **Batch your operations.** Add, update, and delete documents in batches for much better performance.

6. **Monitor collection size.** As collections grow, query latency increases. Consider splitting very large collections by topic or date.

---

## Quick Summary

Vector databases store embeddings and enable fast similarity search. ChromaDB is the easiest option, handling documents, metadata, and embeddings in one package. FAISS provides raw performance for large-scale applications but requires you to manage documents and metadata separately. ChromaDB supports metadata filtering so you can combine similarity search with exact filters. For most RAG applications, start with ChromaDB and switch to FAISS only if you need to handle millions of vectors with sub-millisecond latency.

---

## Key Points

- **Regular databases** use B-tree indexes for exact matching. They cannot do similarity search efficiently.
- **Vector databases** use specialized indexes (HNSW, IVF) for fast approximate nearest neighbor search.
- **ChromaDB** is an all-in-one solution: stores documents, embeddings, and metadata together.
- **FAISS** is a pure vector search library: fastest performance but no document/metadata storage.
- **Metadata filtering** lets you combine similarity search with exact filters (topic, date, etc.).
- **Persistent storage** saves your data to disk so it survives application restarts.
- **Batch operations** are much faster than one-at-a-time operations.
- **Approximate search** trades tiny accuracy loss for massive speed gains on large datasets.

---

## Practice Questions

1. Why can a regular SQL database not efficiently handle the query "find documents with similar meaning to this text"?

2. What is the difference between exact search (`IndexFlatL2`) and approximate search (`IndexIVFFlat`) in FAISS? When would you accept approximate results?

3. You have a ChromaDB collection with metadata fields "topic" and "date." Write the query to find documents about "machine learning" that are only from the "python" topic.

4. Your FAISS IVF index has `nlist=100` and `nprobe=5`. What do these parameters mean, and how would you change them to get more accurate results?

5. You are building a RAG system for a company with 10,000 internal documents. Would you choose ChromaDB or FAISS? Explain your reasoning.

---

## Exercises

**Exercise 1: Build a Document Store**

Create a ChromaDB-based document store that can add, search, update, and delete documents. Store at least 15 documents about different topics. Implement a search function that supports both similarity search and metadata filtering. Test with at least 5 different queries.

**Exercise 2: FAISS Performance Test**

Create FAISS indexes of different sizes (1,000 / 10,000 / 100,000 vectors) and measure query time for each. Compare flat (exact) vs IVF (approximate) indexes. Plot or display the results in a formatted table. What is the crossover point where approximate search becomes worth it?

**Exercise 3: Hybrid Search**

Build a search system that combines ChromaDB similarity search with keyword-based filtering. For each query, first do a similarity search for the top 10 results, then re-rank them based on whether they contain specific keywords from the query. Compare the results to pure similarity search.

---

## What Is Next?

You now have all the pieces: document processing (Chapter 14), embeddings (Chapter 15), and vector databases (Chapter 16). In Chapter 17, you will put them all together into a complete RAG pipeline. You will load documents, chunk them, embed them, store them in ChromaDB, and build a question-answering system that retrieves relevant information and generates grounded answers. It is time to build the real thing.
