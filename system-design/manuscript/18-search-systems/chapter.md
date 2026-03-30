# Chapter 18: Search Systems

## What You Will Learn

- Why full-text search is fundamentally different from SQL LIKE queries
- How an inverted index works (and why it is like a book's index)
- How Elasticsearch organizes data into indexes, shards, and replicas
- How an indexing pipeline keeps search data fresh
- How relevance scoring works with TF-IDF and BM25
- How fuzzy matching handles typos and misspellings
- How autocomplete and typeahead suggestions work
- How to design a search architecture for an e-commerce platform

## Why This Chapter Matters

Imagine you are looking for a specific topic in a 500-page textbook. You have two options. Option one: start at page one and read every single page until you find what you need. Option two: open the index at the back of the book, look up the topic alphabetically, and jump directly to the right page.

Nobody chooses option one. It is absurdly slow. Yet that is exactly what a SQL `LIKE '%search term%'` query does -- it scans every single row in the table looking for a match. When your database has 100 million products, this takes minutes.

Search systems solve this by building the equivalent of a book's index for your data. They make it possible to search billions of documents and get relevant results in milliseconds. Every application with a search bar -- Google, Amazon, Netflix, Spotify -- depends on these concepts. Understanding search systems is essential for system design interviews and for building products that users actually enjoy.

---

## Full-Text Search vs LIKE

### The Problem with LIKE

SQL databases support the `LIKE` operator for text matching. It works for small datasets, but it falls apart at scale.

```
  SQL LIKE Query:

  SELECT * FROM products WHERE name LIKE '%running shoes%';

  What the database does:

  Row 1:  "Blue T-Shirt"           -- scan... no match
  Row 2:  "Red Dress"              -- scan... no match
  Row 3:  "Running Shoes Nike"     -- scan... MATCH!
  Row 4:  "Green Hat"              -- scan... no match
  Row 5:  "Black Jacket"           -- scan... no match
  ...
  Row 10,000,000: "Yellow Socks"   -- scan... no match

  Scanned ALL 10 million rows to find matches.
  Time: 8 seconds. Unacceptable for a user-facing search.

  Problems with LIKE:
  1. Full table scan (no index can help with leading %)
  2. No relevance ranking (which result is "best"?)
  3. No fuzzy matching ("runnng shoes" returns nothing)
  4. No stemming ("run" does not match "running")
  5. No synonym support ("sneakers" does not match "shoes")
```

### Full-Text Search

Full-text search pre-processes your data into a structure optimized for text queries. Instead of scanning every document at query time, it looks up pre-built indexes in milliseconds.

```
  Full-Text Search:

  Step 1: At index time, build an inverted index (done once, updated incrementally)

  Step 2: At query time, look up the index (instant)

  Query: "running shoes"

  Inverted Index Lookup:
    "running" --> [doc 3, doc 47, doc 982, doc 5,401]
    "shoes"   --> [doc 3, doc 12, doc 47, doc 1,203]

  Intersection: [doc 3, doc 47]  (both words appear)

  Time: 5 milliseconds (even with 10 million documents)
```

| Feature | SQL LIKE | Full-Text Search |
|---|---|---|
| Speed (10M docs) | Seconds to minutes | Milliseconds |
| Relevance ranking | No | Yes (scored results) |
| Fuzzy matching | No | Yes (handles typos) |
| Stemming | No | Yes (run = running) |
| Synonyms | No | Yes (shoes = sneakers) |
| Index usage | Cannot use index with leading % | Purpose-built inverted index |

---

## The Inverted Index

The inverted index is the core data structure that makes full-text search fast. It is called "inverted" because it inverts the relationship between documents and words.

### Forward Index vs Inverted Index

A **forward index** maps documents to words (what words does this document contain?). An **inverted index** maps words to documents (which documents contain this word?).

```
  Forward Index (Document -> Words):
  Like reading a book page by page.

  Doc 1: "The quick brown fox"     --> [the, quick, brown, fox]
  Doc 2: "The lazy brown dog"      --> [the, lazy, brown, dog]
  Doc 3: "Quick fox jumps high"    --> [quick, fox, jumps, high]

  To find "fox": Must check EVERY document. Slow.


  Inverted Index (Word -> Documents):
  Like using a book's index at the back.

  "brown"  --> [Doc 1, Doc 2]
  "dog"    --> [Doc 2]
  "fox"    --> [Doc 1, Doc 3]
  "high"   --> [Doc 3]
  "jumps"  --> [Doc 3]
  "lazy"   --> [Doc 2]
  "quick"  --> [Doc 1, Doc 3]
  "the"    --> [Doc 1, Doc 2]

  To find "fox": Look up one entry. Instant.
```

### The Book Index Analogy

Think of a textbook on computer science. At the back, you find an index:

```
  Book Index (This IS an inverted index!):

  Algorithm .............. 12, 45, 78, 203
  Binary Search .......... 45, 89
  Cache .................. 34, 67, 201
  Database ............... 12, 56, 99, 145
  Hash Table ............. 78, 112
  ...

  Want to learn about "Cache"?
  Go directly to pages 34, 67, and 201.
  No need to read all 500 pages.

  This is exactly how a search engine works:
  - "Pages" = documents in your database
  - "Topics" = words/terms in the inverted index
  - "Page numbers" = document IDs
```

### Building an Inverted Index

The process of building an inverted index involves several text processing steps.

```
  Building an Inverted Index:

  Input Documents:
  Doc 1: "Nike Running Shoes - Lightweight and comfortable"
  Doc 2: "Adidas Running Sneakers for Marathon Runners"
  Doc 3: "Nike Air Max - Comfortable Walking Shoes"

  Step 1: Tokenization (split into words)
  Doc 1: [Nike, Running, Shoes, Lightweight, and, comfortable]
  Doc 2: [Adidas, Running, Sneakers, for, Marathon, Runners]
  Doc 3: [Nike, Air, Max, Comfortable, Walking, Shoes]

  Step 2: Lowercasing
  Doc 1: [nike, running, shoes, lightweight, and, comfortable]
  Doc 2: [adidas, running, sneakers, for, marathon, runners]
  Doc 3: [nike, air, max, comfortable, walking, shoes]

  Step 3: Stop word removal (remove "and", "for", "the", etc.)
  Doc 1: [nike, running, shoes, lightweight, comfortable]
  Doc 2: [adidas, running, sneakers, marathon, runners]
  Doc 3: [nike, air, max, comfortable, walking, shoes]

  Step 4: Stemming (reduce words to root form)
  Doc 1: [nike, run, shoe, lightweight, comfort]
  Doc 2: [adidas, run, sneaker, marathon, runner]
  Doc 3: [nike, air, max, comfort, walk, shoe]

  Step 5: Build Inverted Index
  +-------------+------------------+
  | Term        | Document IDs     |
  +-------------+------------------+
  | adidas      | [2]              |
  | air         | [3]              |
  | comfort     | [1, 3]          |
  | lightweight | [1]              |
  | marathon    | [2]              |
  | max         | [3]              |
  | nike        | [1, 3]          |
  | run         | [1, 2]          |
  | runner      | [2]              |
  | shoe        | [1, 3]          |
  | sneaker     | [2]              |
  | walk        | [3]              |
  +-------------+------------------+

  Now searching for "comfortable running shoes":
  - "comfort" -> [1, 3]
  - "run"     -> [1, 2]
  - "shoe"    -> [1, 3]

  Intersection: Doc 1 matches all three terms. Best match!
  Doc 3 matches "comfort" and "shoe" but not "run". Second best.
  Doc 2 matches "run" only. Third.
```

---

## Elasticsearch: Index, Shard, Replica

Elasticsearch is the most popular open-source search engine. It is built on Apache Lucene and designed for distributed, scalable search.

### Core Concepts

```
  Elasticsearch Architecture:

  CLUSTER (group of nodes working together)
  +------------------------------------------------------------------+
  |                                                                    |
  |  NODE 1 (Server)        NODE 2 (Server)        NODE 3 (Server)    |
  |  +------------------+  +------------------+   +------------------+ |
  |  |                  |  |                  |   |                  | |
  |  |  Shard 0         |  |  Shard 1         |   |  Shard 2         | |
  |  |  (Primary)       |  |  (Primary)       |   |  (Primary)       | |
  |  |  +------------+  |  |  +------------+  |   |  +------------+  | |
  |  |  | Inverted   |  |  |  | Inverted   |  |   |  | Inverted   |  | |
  |  |  | Index      |  |  |  | Index      |  |   |  | Index      |  | |
  |  |  +------------+  |  |  +------------+  |   |  +------------+  | |
  |  |                  |  |                  |   |                  | |
  |  |  Shard 1         |  |  Shard 2         |   |  Shard 0         | |
  |  |  (Replica)       |  |  (Replica)       |   |  (Replica)       | |
  |  |  +------------+  |  |  +------------+  |   |  +------------+  | |
  |  |  | Inverted   |  |  |  | Inverted   |  |   |  | Inverted   |  | |
  |  |  | Index      |  |  |  | Index      |  |   |  | Index      |  | |
  |  |  +------------+  |  |  +------------+  |   |  +------------+  | |
  |  |                  |  |                  |   |                  | |
  |  +------------------+  +------------------+   +------------------+ |
  |                                                                    |
  +------------------------------------------------------------------+

  INDEX: A collection of documents (like a database table)
    Example: "products" index with 10 million product documents

  SHARD: A horizontal partition of an index
    The "products" index is split into 3 shards
    Each shard holds ~3.3 million documents
    Each shard is a self-contained Lucene index

  REPLICA: A copy of a shard on a different node
    Each primary shard has one replica
    If Node 1 dies, Shard 0's replica on Node 3 takes over
```

### Why Sharding?

```
  Without Sharding:                 With Sharding:

  One huge index:                   Split across nodes:

  +------------------+              +--------+ +--------+ +--------+
  | 10M documents    |              | 3.3M   | | 3.3M   | | 3.3M   |
  | One server       |              | Node 1 | | Node 2 | | Node 3 |
  | All queries hit  |              +--------+ +--------+ +--------+
  | this one server  |                 |           |           |
  +------------------+              Query hits all 3 in parallel
                                    Results merged and returned
  Limited by single                 3x throughput, 3x capacity
  server capacity
```

### How a Search Query Works in Elasticsearch

```
  Search Query Flow:

  1. Client sends query to any node (coordinator)
  +--------+   "running shoes"   +--------+
  | Client | ------------------> | Node 1 |  (Coordinator)
  +--------+                     +--------+
                                      |
  2. Coordinator sends query to one copy of each shard
                                      |
                    +-----------------+-----------------+
                    |                                   |
                    v                                   v
              +--------+                         +--------+
              | Node 2 |                         | Node 3 |
              | Shard 1|                         | Shard 2|
              +--------+                         +--------+
                    |                                   |
  3. Each shard searches its local inverted index
     and returns top matching document IDs + scores
                    |                                   |
                    v                                   v
              [doc 47: 8.5]                      [doc 982: 9.1]
              [doc 103: 7.2]                     [doc 501: 6.8]
                    |                                   |
                    +-----------------+-----------------+
                                      |
  4. Coordinator merges results, sorts by score
                                      |
                                      v
              Final results: [doc 982: 9.1, doc 47: 8.5,
                              doc 103: 7.2, doc 501: 6.8]
                                      |
  5. Coordinator fetches full documents for top results
                                      |
                                      v
  +--------+   [results with data]   +--------+
  | Client | <--------------------- | Node 1 |
  +--------+                         +--------+
```

---

## Indexing Pipeline

The indexing pipeline is how data gets from your primary database into the search engine. This is a critical but often overlooked part of search architecture.

### The Challenge

Your primary data lives in a relational database (PostgreSQL, MySQL). Your search engine (Elasticsearch) needs a copy of that data in its inverted index format. How do you keep them in sync?

```
  Indexing Pipeline:

  +------------+                          +---------------+
  | PostgreSQL |                          | Elasticsearch |
  | (Source of |    Indexing Pipeline      | (Search       |
  |  Truth)    | -----------------------> |  Engine)      |
  +------------+                          +---------------+

  Options:

  1. Dual Write (Simple but Risky)
  +------+    Write    +--------+
  | App  | ----------> | Postgres|
  |      | ----------> | Elastic |  <-- What if one write fails?
  +------+             +--------+      Data gets out of sync.

  2. Change Data Capture (CDC) - Recommended
  +------+    Write    +----------+    CDC Stream    +----------+
  | App  | ----------> | Postgres | --------------> | Indexer  |
  +------+             +----------+    (Debezium)   +----+-----+
                                                         |
                                                         v
                                                    +----------+
                                                    | Elastic  |
                                                    +----------+

  CDC reads the database's transaction log (WAL)
  and streams changes to the indexer in real time.
  No risk of dual-write inconsistency.

  3. Periodic Batch Reindex
  +----------+   Every 5 min   +----------+    Bulk Index    +----------+
  | Postgres | -------------> | Batch Job | --------------> | Elastic  |
  +----------+   (cron job)    +----------+                  +----------+

  Simple but introduces up to 5 minutes of delay.
  Acceptable for some use cases (product catalog).
```

### Recommended Architecture

```
  Production Indexing Pipeline:

  +--------+  Write  +----------+  WAL Stream  +----------+
  | App    | ------> | Postgres | -----------> | Debezium |
  | Server |         | (Source  |  (CDC)       | (CDC     |
  +--------+         |  of Truth|              |  Tool)   |
                     +----------+              +----+-----+
                                                    |
                                              +-----v-----+
                                              |   Kafka    |
                                              | (Buffer)   |
                                              +-----+------+
                                                    |
                                              +-----v------+
                                              |  Indexer   |
                                              |  Service   |
                                              | - Transform|
                                              | - Enrich   |
                                              | - Validate |
                                              +-----+------+
                                                    |
                                              +-----v--------+
                                              | Elasticsearch |
                                              +---------------+

  The indexer service:
  - Reads change events from Kafka
  - Transforms data (flatten nested objects, combine fields)
  - Enriches data (add category names, compute popularity)
  - Validates (skip invalid records)
  - Bulk-indexes into Elasticsearch
```

---

## Relevance Scoring: TF-IDF and BM25

When a user searches for "running shoes," the search engine does not just find matching documents. It **ranks** them by relevance. The most relevant document appears first.

### TF-IDF: Term Frequency - Inverse Document Frequency

TF-IDF is the foundational relevance scoring formula. It combines two ideas.

**Term Frequency (TF):** How often does the search term appear in this document? More occurrences = more relevant.

**Inverse Document Frequency (IDF):** How rare is this term across all documents? Rare terms are more important than common ones.

```
  TF-IDF Example:

  Search: "running shoes"

  Document A: "Running shoes for marathon running. Best running shoes."
  Document B: "Nike shoes for casual walking."
  Document C: "The best running shoes guide for beginners."

  Term Frequency (TF) for "running":
  Doc A: 3 occurrences in 8 words  = 3/8 = 0.375
  Doc B: 0 occurrences in 5 words  = 0/5 = 0.000
  Doc C: 1 occurrence  in 7 words  = 1/7 = 0.143

  Inverse Document Frequency (IDF) for "running":
  3 total documents, 2 contain "running"
  IDF = log(3/2) = 0.176  (not very rare)

  IDF for "shoes":
  3 total documents, 3 contain "shoes"
  IDF = log(3/3) = 0.000  (appears everywhere, not discriminating)

  IDF for "marathon":
  3 total documents, 1 contains "marathon"
  IDF = log(3/1) = 0.477  (rare, very discriminating!)

  Key insight: Common words like "the" and "shoes" have low IDF.
  Rare, specific words like "marathon" have high IDF.
```

### BM25: The Modern Standard

BM25 (Best Matching 25) is an improved version of TF-IDF used by Elasticsearch and most modern search engines. It fixes two problems with basic TF-IDF.

**Problem 1: TF saturation.** In TF-IDF, a document mentioning "running" 100 times scores much higher than one mentioning it 5 times. But is it really 20 times more relevant? BM25 adds a saturation curve: after a certain point, additional occurrences matter less and less.

**Problem 2: Document length bias.** A 10,000-word document is more likely to contain a search term than a 50-word document, simply because it has more words. BM25 normalizes for document length.

```
  TF-IDF vs BM25: Term Frequency Curves

  Score
  ^
  |          TF-IDF (linear)
  |         /
  |        /
  |       /              BM25 (saturating)
  |      /          ___________
  |     /       ___/
  |    /    ___/
  |   / ___/
  |  //
  | /
  +-------------------------> Term Frequency

  BM25 says: "Yes, mentioning 'running' 5 times is better
  than 1 time. But mentioning it 50 times is only slightly
  better than 5 times."
```

### Boosting

You can boost the importance of certain fields. A match in the product title is more relevant than a match in the description.

```
  Field Boosting:

  Search: "running shoes"

  Product:
    title: "Nike Running Shoes"          (boost: 3x)
    description: "Great for running..."   (boost: 1x)
    category: "Footwear"                 (boost: 0.5x)

  A match in the title contributes 3x more to the score
  than a match in the description.
```

---

## Fuzzy Matching

Users make typos. A search engine that returns zero results for "runnng shoes" is frustrating. Fuzzy matching finds results even when the query has spelling errors.

### Edit Distance (Levenshtein Distance)

Fuzzy matching uses **edit distance**: the minimum number of single-character edits (insertions, deletions, or substitutions) needed to transform one word into another.

```
  Edit Distance Examples:

  "runnng" -> "running"    (1 insertion: add 'i')     Distance: 1
  "shoez"  -> "shoes"      (1 substitution: z -> s)   Distance: 1
  "rnning" -> "running"    (1 insertion: add 'u')     Distance: 1
  "cat"    -> "car"        (1 substitution: t -> r)   Distance: 1
  "cat"    -> "cart"       (1 insertion: add 't')     Distance: 1
  "kitten" -> "sitting"    (3 edits)                  Distance: 3

  Elasticsearch default: Allow edit distance of 2
  "runnng shoes" matches "running shoes" (distance 1)
```

### How Fuzzy Search Works

```
  Fuzzy Search Flow:

  Query: "runnng"  (typo)

  Step 1: Generate variations within edit distance 2
    runng, running, runnig, runnin, runnmg, ...

  Step 2: Look up each variation in the inverted index
    "running" --> [Doc 1, Doc 3, Doc 47]   FOUND!

  Step 3: Return results with slightly lower score
    (penalize fuzzy matches vs exact matches)

  User sees results for "running" even though they typed "runnng"
```

---

## Autocomplete

Autocomplete (typeahead) suggests results as the user types, before they press Enter. It requires a different index structure optimized for prefix matching.

### How Autocomplete Works

```
  Autocomplete Flow:

  User types: "r"  -> [running shoes, red dress, rain jacket]
  User types: "ru" -> [running shoes, rubber boots, rug]
  User types: "run" -> [running shoes, running watch, run tracker]
  User types: "runn" -> [running shoes, running watch]

  Each keystroke triggers a search.
  Results must return in under 100ms or the UI feels laggy.
```

### Implementation Approaches

**1. Prefix Index (Edge N-grams)**

Break each word into prefixes and index them separately.

```
  Edge N-grams for "running":

  r
  ru
  run
  runn
  runni
  runnin
  running

  Each prefix is a separate entry in the inverted index.
  When user types "run", instant lookup finds all words
  starting with "run".
```

**2. Completion Suggester (Elasticsearch)**

Elasticsearch has a built-in completion suggester that uses an in-memory data structure (FST: Finite State Transducer) for extremely fast prefix lookups.

```
  Completion Suggester Architecture:

  +--------+   "run"    +-------------+   FST Lookup   +-----------+
  | Client | ---------> | Elasticsearch| ------------> | In-Memory |
  +--------+            | API          |               | FST       |
                        +-------------+               +-----------+
       ^                                                    |
       |                                                    v
       |              Suggestions:                    [running shoes,
       +--------------------------------------------- running watch,
                      (under 5ms)                      run tracker]

  FST: Finite State Transducer
  - Compresses all terms into a compact graph
  - Prefix lookups in microseconds
  - Lives entirely in memory
```

**3. Popular Queries (Search-as-You-Type)**

Instead of searching the product index, search a separate index of popular queries.

```
  Popular Query Autocomplete:

  +-------------------------------------------+
  | Popular Queries Index                      |
  +-------------------------------------------+
  | Query              | Count  | Last 7 Days |
  +-------------------------------------------+
  | running shoes      | 45,000 | 12,000      |
  | running watch      | 8,200  | 2,100       |
  | running shorts     | 6,500  | 1,800       |
  | run tracker app    | 3,100  | 900         |
  +-------------------------------------------+

  User types "run" -> return top queries by popularity
  Much faster than searching millions of products
  Shows what other users searched for (social proof)
```

---

## E-Commerce Search Architecture

Let us design a complete search system for an e-commerce platform like Amazon or Shopify.

### Requirements

- 50 million products
- 10,000 search queries per second at peak
- Results in under 200 milliseconds
- Relevance ranking, fuzzy matching, filtering, sorting
- Autocomplete with under 100 millisecond latency

### Architecture

```
  E-Commerce Search Architecture:

  +----------+                              +------------------+
  | Mobile/  |   "blue running shoes"       |   API Gateway    |
  | Web App  | ---------------------------> | (Rate Limiting,  |
  +----------+                              |  Auth)           |
                                            +--------+---------+
                                                     |
                                            +--------v---------+
                                            |  Search Service  |
                                            |                  |
                                            | - Parse query    |
                                            | - Apply filters  |
                                            | - Build ES query |
                                            +--------+---------+
                                                     |
                              +----------------------+
                              |                      |
                              v                      v
                     +--------+--------+    +--------+--------+
                     |  Elasticsearch   |    |  Autocomplete   |
                     |  Cluster         |    |  Index          |
                     |  (Main Search)   |    |  (Suggestions)  |
                     |                  |    |                  |
                     |  50M products    |    |  Popular queries |
                     |  5 shards        |    |  In-memory FST   |
                     |  1 replica each  |    +--------+--------+
                     +--------+--------+
                              |
                    +---------+---------+
                    |                   |
                    v                   v
              +-----------+      +-----------+
              | Relevance |      | Filters   |
              | Scoring   |      | & Facets  |
              | (BM25)    |      | (brand,   |
              |           |      |  price,   |
              |           |      |  size,    |
              |           |      |  color)   |
              +-----------+      +-----------+


  Data Flow (Indexing Pipeline):

  +-----------+   CDC    +----------+   Kafka   +----------+   Bulk    +----------+
  | Product   | -------> | Debezium | -------> | Indexer  | -------> | Elastic  |
  | Database  |          +----------+          | Service  |          | search   |
  | (Postgres)|                                +----------+          +----------+
  +-----------+                                     |
                                              +-----v------+
                                              | Enrichment |
                                              | - Synonyms |
                                              | - Spelling |
                                              | - Category |
                                              | - Popularity|
                                              +------------+
```

### Query Processing Flow

```
  What Happens When You Search "blue runnng shoes size 10":

  Step 1: Query Parsing
  +----------------------------------------------------------+
  | Input: "blue runnng shoes size 10"                        |
  |                                                           |
  | - Tokenize: [blue, runnng, shoes, size, 10]               |
  | - Spell check: runnng -> running                          |
  | - Identify filters: size=10                               |
  | - Remaining search terms: [blue, running, shoes]          |
  +----------------------------------------------------------+

  Step 2: Query Building
  +----------------------------------------------------------+
  | Elasticsearch Query:                                      |
  | {                                                         |
  |   "query": {                                              |
  |     "bool": {                                             |
  |       "must": [                                           |
  |         {"multi_match": {                                 |
  |           "query": "blue running shoes",                  |
  |           "fields": ["title^3", "description", "brand^2"],|
  |           "fuzziness": "AUTO"                             |
  |         }}                                                |
  |       ],                                                  |
  |       "filter": [                                         |
  |         {"term": {"sizes": "10"}},                        |
  |         {"term": {"in_stock": true}}                      |
  |       ]                                                   |
  |     }                                                     |
  |   },                                                      |
  |   "aggs": {                                               |
  |     "brands": {"terms": {"field": "brand"}},              |
  |     "price_ranges": {"range": {"field": "price", ...}}    |
  |   }                                                       |
  | }                                                         |
  +----------------------------------------------------------+

  Step 3: Results
  +----------------------------------------------------------+
  | Results (sorted by relevance score):                      |
  |                                                           |
  | 1. Nike Air Zoom Running Shoes - Blue (Score: 12.4)       |
  |    Size 10 in stock. $129.99                              |
  |                                                           |
  | 2. Adidas Ultraboost Running Shoes - Blue (Score: 11.2)   |
  |    Size 10 in stock. $179.99                              |
  |                                                           |
  | 3. New Balance Fresh Foam - Blue (Score: 9.8)             |
  |    Size 10 in stock. $99.99                               |
  |                                                           |
  | Facets:                                                   |
  |   Brands: Nike (45), Adidas (38), New Balance (22)        |
  |   Price: Under $100 (12), $100-$200 (28), Over $200 (5)  |
  |   Colors: Blue (45), Black (32), White (18)               |
  +----------------------------------------------------------+
```

### Faceted Search

Facets are the filter counts you see on the left side of e-commerce search results. They tell the user how many products match each filter option.

```
  Faceted Search:

  Search: "running shoes"

  +-------------------+     +-----------------------------+
  |  FACETS (Filters) |     |  RESULTS                    |
  |                   |     |                             |
  |  Brand:           |     |  1. Nike Air Zoom           |
  |  [ ] Nike (245)   |     |     $129.99 ****            |
  |  [ ] Adidas (189) |     |                             |
  |  [ ] New Bal (98) |     |  2. Adidas Ultraboost       |
  |                   |     |     $179.99 ****             |
  |  Price:           |     |                             |
  |  [ ] Under $50    |     |  3. New Balance 1080        |
  |  [ ] $50-$100     |     |     $149.99 ***              |
  |  [ ] $100-$200    |     |                             |
  |  [ ] Over $200    |     |  4. Brooks Ghost 15         |
  |                   |     |     $139.99 ****             |
  |  Size:            |     |                             |
  |  [ ] 8  (120)     |     |                             |
  |  [ ] 9  (145)     |     |                             |
  |  [ ] 10 (138)     |     |                             |
  |  [ ] 11 (98)      |     |                             |
  +-------------------+     +-----------------------------+

  Elasticsearch aggregations compute these counts
  alongside the search results in a single query.
```

---

## Trade-offs

| Decision | Option A | Option B |
|---|---|---|
| Search engine | Elasticsearch (feature-rich, complex) | Database full-text (simpler, limited) |
| Indexing | Real-time CDC (fresh data, complex) | Batch reindex (delayed, simple) |
| Autocomplete | Edge n-grams (flexible, more storage) | Completion suggester (fast, less flexible) |
| Relevance | BM25 default (good enough for most) | Custom scoring with ML (better, complex) |
| Sharding | More shards (parallelism, overhead) | Fewer shards (simpler, limited throughput) |
| Consistency | Real-time index (always fresh) | Near-real-time (seconds delay, less load) |

---

## Common Mistakes

1. **Using SQL LIKE for user-facing search.** It does not scale, does not rank by relevance, and does not handle typos. Use a proper search engine for any search feature users interact with.

2. **Not handling synonyms.** Users search for "sneakers" but your products say "shoes." Without a synonym dictionary, they get zero results. Configure synonyms in your analyzer.

3. **Over-sharding.** Creating 20 shards for an index with 100,000 documents wastes resources. Each shard has overhead. A good rule: aim for 10 to 50 GB per shard.

4. **Dual-writing to the database and search engine.** If one write succeeds and the other fails, your data is out of sync. Use CDC (Change Data Capture) to stream changes from the database to the search engine.

5. **Ignoring relevance tuning.** The default BM25 scoring works but is rarely optimal. Invest time in field boosting, custom scoring, and A/B testing different relevance formulas.

6. **Not monitoring search quality.** Track click-through rates, zero-result rates, and search abandonment. If 20% of searches return no results, your search is broken.

---

## Best Practices

1. **Use Change Data Capture for indexing.** CDC (tools like Debezium) reads the database transaction log and streams changes to your indexer. This is the most reliable way to keep search in sync with your primary database.

2. **Configure analyzers thoughtfully.** Choose the right tokenizer, stemmer, and stop word list for your language. Test with real user queries.

3. **Add synonyms and spelling correction.** Build a synonym dictionary for your domain. Use fuzzy matching with edit distance 1-2 to handle typos.

4. **Monitor zero-result rates.** Track how often searches return no results. These are failed user experiences. Add the missing terms to your synonym dictionary or adjust your analyzer.

5. **Use field boosting.** Matches in the product title should score higher than matches in the description. Experiment with boost values and measure click-through rates.

6. **Separate autocomplete from search.** Use a dedicated completion suggester index for autocomplete. It is faster and can be optimized independently.

7. **Plan shard allocation.** Aim for 10 to 50 GB per shard. Use time-based indices for logs (one index per day). Monitor shard size and rebalance when needed.

8. **Implement search analytics.** Log every search query, the results shown, and which result the user clicked. This data is essential for improving relevance.

---

## Quick Summary

Full-text search uses inverted indexes to find matching documents in milliseconds, unlike SQL LIKE which scans every row. An inverted index maps terms to document IDs, just like a book's index maps topics to page numbers. Building the index involves tokenization, lowercasing, stop word removal, and stemming. Elasticsearch distributes data across shards for parallelism and replicas for fault tolerance. An indexing pipeline using Change Data Capture keeps search data in sync with the primary database. BM25 scores relevance by combining term frequency with inverse document frequency, adding saturation and length normalization. Fuzzy matching handles typos using edit distance. Autocomplete uses edge n-grams or completion suggesters for sub-100-millisecond prefix lookups. E-commerce search combines full-text search with filters, facets, and relevance tuning to help users find products fast.

---

## Key Points

- Inverted indexes map terms to documents, enabling millisecond lookups instead of full table scans
- Text processing (tokenization, stemming, stop words) is critical for accurate matching
- Elasticsearch shards data for parallelism and replicates for fault tolerance
- BM25 improves on TF-IDF by adding term frequency saturation and document length normalization
- Fuzzy matching with edit distance handles typos without requiring exact spelling
- Autocomplete needs a separate, optimized index for sub-100-millisecond responses
- Change Data Capture is the safest way to keep search indexes in sync with primary databases
- Relevance tuning, synonyms, and search analytics are essential for a good search experience

---

## Practice Questions

1. Your e-commerce site has 50 million products. Users report that search results take 3 seconds. You are using a single Elasticsearch node with one shard. What changes would you make to bring latency under 200 milliseconds?

2. Users search for "iPhone charger" but your products are listed as "Lightning cable." How would you solve this? What are the trade-offs between synonyms, query expansion, and manual curation?

3. Your autocomplete suggestions take 500 milliseconds to return. The product index has 50 million documents. How would you redesign the autocomplete system to achieve sub-100-millisecond latency?

4. You are indexing product data from PostgreSQL into Elasticsearch using a cron job every 5 minutes. A product's price changes, but the old price shows in search results for up to 5 minutes. How would you reduce this delay without overloading either system?

5. Your search analytics show that 15% of queries return zero results. What strategies would you use to reduce this rate? How would you measure improvement?

---

## Exercises

**Exercise 1: Build an Inverted Index**

Given these five product descriptions, manually build an inverted index. Apply tokenization, lowercasing, stop word removal, and stemming. Then trace how the search query "comfortable waterproof jacket" would be processed against your index. Which documents match? How would you rank them?

Products:
- Doc 1: "Waterproof Rain Jacket - Lightweight and Breathable"
- Doc 2: "Comfortable Cotton T-Shirt for Everyday Wear"
- Doc 3: "Men's Waterproof Hiking Jacket - Ultra Comfortable"
- Doc 4: "Leather Jacket - Classic Style"
- Doc 5: "Women's Comfortable Running Shoes - Waterproof"

**Exercise 2: Design a Recipe Search Engine**

Design the search architecture for a recipe website with 5 million recipes. Users should be able to search by ingredients ("chicken, garlic, lemon"), cooking time ("under 30 minutes"), dietary restrictions ("gluten-free"), and free text ("easy weeknight dinner"). Define the Elasticsearch index mapping, the indexing pipeline, and the query structure. Include autocomplete suggestions.

**Exercise 3: Search Relevance Experiment**

You run a bookstore with 1 million books. A user searches for "python programming." Currently, the top result is "Python: The Complete Reference" (published 2005, 2 reviews). But users consistently click on "Python Crash Course" (published 2023, 5000 reviews). Design a custom scoring formula that incorporates publication date, review count, and rating alongside BM25 text relevance. Explain how you would A/B test your new formula against the default.

---

## What Is Next?

You now know how to build search systems that find relevant results in milliseconds across millions of documents. But finding information is only half the challenge. Users also need to be notified when things happen: when their order ships, when someone messages them, when a price drops. In the next chapter, you will learn how to design a notification system that delivers push notifications, SMS, emails, and in-app alerts at scale, handling millions of notifications per day with proper prioritization, throttling, and delivery tracking.
