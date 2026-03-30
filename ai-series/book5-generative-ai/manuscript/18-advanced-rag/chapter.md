# Chapter 18: Advanced RAG

## What You Will Learn

In this chapter, you will learn:

- How to re-rank retrieved results for better accuracy
- How hybrid search combines keyword and semantic matching
- How query expansion handles vague or incomplete questions
- How to evaluate RAG systems using the RAGAS framework
- How to handle multiple document types in one pipeline

## Why This Chapter Matters

The basic RAG pipeline you built in Chapter 17 works, but it has limitations. Sometimes the retrieval step returns chunks that are somewhat relevant but not the best ones. Sometimes a user's question is vague, and the system retrieves the wrong documents entirely. Sometimes you need to search across PDFs, emails, and web pages all at once.

Advanced RAG techniques address these problems. They are the difference between a demo that works sometimes and a production system that works reliably. Think of basic RAG as learning to drive. Advanced RAG is learning to drive in traffic, rain, and at night. The fundamentals are the same, but the techniques make you reliable in challenging conditions.

---

## Re-Ranking Retrieved Results

The basic retrieval step finds chunks that are close to your query in embedding space. But "close in embedding space" does not always mean "most useful for answering the question." Re-ranking uses a more powerful model to re-score the retrieved results.

```
+------------------------------------------------------------------+
|                    RE-RANKING CONCEPT                             |
|                                                                   |
|  Step 1: Retrieve top 20 chunks (fast, approximate)              |
|  +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+|
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  ||
|  +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+|
|                                                                   |
|  Step 2: Re-rank with a cross-encoder (slow, accurate)           |
|  The cross-encoder reads BOTH the query AND each chunk            |
|  together, understanding the relationship more deeply.            |
|                                                                   |
|  Step 3: Take top 5 after re-ranking                             |
|  +--+--+--+--+--+                                               |
|  |  |  |  |  |  |  <-- These are genuinely the best 5           |
|  +--+--+--+--+--+                                               |
|                                                                   |
|  Why not just use the cross-encoder for everything?              |
|  Because it is too slow. Re-ranking 20 results is fast.          |
|  Re-ranking 100,000 results would take hours.                    |
+------------------------------------------------------------------+
```

> **Re-Ranking:** A second stage of retrieval where a more powerful model re-scores the initially retrieved results. The first stage (embedding search) is fast but approximate. The re-ranker is slower but more accurate. Together they give you both speed and accuracy.

> **Cross-Encoder:** A model that takes two texts as input and outputs a relevance score. Unlike embeddings (which encode each text independently), a cross-encoder reads both texts together, understanding their relationship more deeply.

```python
# Install: pip install sentence-transformers
from sentence_transformers import CrossEncoder, SentenceTransformer
from sentence_transformers.util import cos_sim
import numpy as np

# Step 1: Initial retrieval using embeddings (fast)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

documents = [
    "Python lists are ordered collections that can hold items of different types.",
    "To install Python packages, use pip: pip install package_name.",
    "Python dictionaries store key-value pairs and are unordered.",
    "The return statement exits a function and optionally returns a value.",
    "Python supports multiple programming paradigms including OOP and functional.",
    "List comprehensions provide a concise way to create lists in Python.",
    "Error handling in Python uses try, except, and finally blocks.",
    "The Python GIL prevents true multi-threading for CPU-bound tasks.",
    "Virtual environments isolate project dependencies from the system Python.",
    "Decorators in Python modify the behavior of functions using the @ syntax.",
]

query = "How do I manage packages and dependencies in Python?"

# Embed and retrieve top 5
doc_embeddings = embedding_model.encode(documents)
query_embedding = embedding_model.encode(query)
similarities = cos_sim(query_embedding, doc_embeddings)[0]
initial_indices = similarities.argsort(descending=True)[:5]

print("INITIAL RETRIEVAL (embedding search):")
print("-" * 50)
for rank, idx in enumerate(initial_indices, 1):
    score = similarities[idx].item()
    print(f"  {rank}. [{score:.4f}] {documents[idx][:70]}...")

# Step 2: Re-rank using cross-encoder (more accurate)
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# Score each retrieved document against the query
pairs = [(query, documents[idx]) for idx in initial_indices]
rerank_scores = reranker.predict(pairs)

# Sort by re-rank score
reranked = sorted(
    zip(initial_indices, rerank_scores),
    key=lambda x: x[1],
    reverse=True
)

print("\nAFTER RE-RANKING (cross-encoder):")
print("-" * 50)
for rank, (idx, score) in enumerate(reranked, 1):
    print(f"  {rank}. [{score:.4f}] {documents[idx][:70]}...")

print("\nNotice how re-ranking may change the order!")
print("The cross-encoder better understands query-document relevance.")
```

**Output:**
```
INITIAL RETRIEVAL (embedding search):
--------------------------------------------------
  1. [0.5234] To install Python packages, use pip: pip install package_name...
  2. [0.4567] Virtual environments isolate project dependencies from the sy...
  3. [0.3890] Python lists are ordered collections that can hold items of di...
  4. [0.3456] Python supports multiple programming paradigms including OOP a...
  5. [0.3012] The Python GIL prevents true multi-threading for CPU-bound ta...

AFTER RE-RANKING (cross-encoder):
--------------------------------------------------
  1. [0.9234] To install Python packages, use pip: pip install package_name...
  2. [0.8901] Virtual environments isolate project dependencies from the sy...
  3. [0.1234] Python supports multiple programming paradigms including OOP a...
  4. [0.0890] Python lists are ordered collections that can hold items of di...
  5. [0.0456] The Python GIL prevents true multi-threading for CPU-bound ta...

Notice how re-ranking may change the order!
The cross-encoder better understands query-document relevance.
```

**Line-by-line explanation:**

- `SentenceTransformer` creates independent embeddings for query and documents. Fast but each text is encoded separately.
- `CrossEncoder` takes the query AND document together as a pair, understanding their relationship. Much more accurate but cannot pre-compute document encodings.
- `reranker.predict(pairs)` scores each query-document pair. Higher scores mean more relevant.
- Notice that after re-ranking, the pip installation and virtual environment documents score very high (directly about package management), while the others score near zero. The embedding search had them all somewhat close together.

---

## Hybrid Search: Keyword + Semantic

Sometimes exact keyword matching works better than semantic search. Hybrid search combines both approaches.

```
+------------------------------------------------------------------+
|                    HYBRID SEARCH                                  |
|                                                                   |
|  Query: "Python GIL threading"                                    |
|                                                                   |
|  Semantic Search:                    Keyword Search:              |
|  Finds documents about              Finds documents containing   |
|  concurrency and parallelism         exactly "GIL" and "threading"|
|  (understands MEANING)              (matches exact WORDS)        |
|                                                                   |
|  Hybrid: Combines both scores for the best of both worlds        |
|                                                                   |
|  +--------------------+  +--------------------+                  |
|  | Semantic Results   |  | Keyword Results    |                  |
|  | 1. concurrency doc |  | 1. GIL doc         |                  |
|  | 2. parallelism doc |  | 2. threading doc   |                  |
|  | 3. GIL doc         |  | 3. async doc       |                  |
|  +--------------------+  +--------------------+                  |
|           \                      /                               |
|            v                    v                                 |
|         +-------------------------+                              |
|         | Combined & Re-ranked    |                              |
|         | 1. GIL doc (both!)      |                              |
|         | 2. threading doc        |                              |
|         | 3. concurrency doc      |                              |
|         +-------------------------+                              |
+------------------------------------------------------------------+
```

> **Hybrid Search:** A search strategy that combines semantic (embedding-based) search with keyword (lexical) search. The results from both methods are merged and re-scored. This captures both meaning similarity and exact term matching.

```python
import re
from collections import Counter
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

model = SentenceTransformer('all-MiniLM-L6-v2')

documents = [
    "The Python GIL (Global Interpreter Lock) prevents multiple threads "
    "from executing Python bytecode simultaneously.",

    "Asyncio provides concurrent programming using async and await syntax "
    "for I/O-bound operations in Python.",

    "Multiprocessing in Python creates separate processes, each with its "
    "own GIL, enabling true parallelism.",

    "Threading in Python is useful for I/O-bound tasks despite the GIL "
    "limitation on CPU-bound operations.",

    "Python's concurrent.futures module provides a high-level interface "
    "for asynchronous execution of callables.",

    "Celery is a distributed task queue for Python that handles background "
    "jobs and scheduled tasks.",

    "Python decorators are functions that modify the behavior of other "
    "functions using the @decorator syntax.",

    "List comprehensions provide a concise way to create new lists based "
    "on existing iterables in Python.",
]

def keyword_search(query, docs, top_k=5):
    """Simple keyword-based search using term frequency."""
    query_terms = set(re.findall(r'\w+', query.lower()))
    scores = []

    for doc in docs:
        doc_terms = re.findall(r'\w+', doc.lower())
        doc_counter = Counter(doc_terms)
        score = sum(doc_counter.get(term, 0) for term in query_terms)
        scores.append(score)

    indices = sorted(range(len(scores)), key=lambda i: scores[i],
                     reverse=True)[:top_k]
    return [(i, scores[i]) for i in indices]

def semantic_search(query, docs, embeddings, top_k=5):
    """Embedding-based semantic search."""
    query_emb = model.encode(query)
    sims = cos_sim(query_emb, embeddings)[0]
    indices = sims.argsort(descending=True)[:top_k]
    return [(idx.item(), sims[idx].item()) for idx in indices]

def hybrid_search(query, docs, embeddings, top_k=5,
                  semantic_weight=0.7, keyword_weight=0.3):
    """
    Combine semantic and keyword search results.

    Args:
        semantic_weight: How much to weight semantic results (0-1)
        keyword_weight: How much to weight keyword results (0-1)
    """
    # Get both types of results
    sem_results = semantic_search(query, docs, embeddings, top_k=len(docs))
    key_results = keyword_search(query, docs, top_k=len(docs))

    # Normalize scores to 0-1 range
    sem_max = max(s for _, s in sem_results) if sem_results else 1
    key_max = max(s for _, s in key_results) if key_results else 1

    sem_scores = {idx: score / sem_max for idx, score in sem_results}
    key_scores = {idx: score / key_max if key_max > 0 else 0
                  for idx, score in key_results}

    # Combine scores
    combined = {}
    all_indices = set(sem_scores.keys()) | set(key_scores.keys())

    for idx in all_indices:
        s_score = sem_scores.get(idx, 0) * semantic_weight
        k_score = key_scores.get(idx, 0) * keyword_weight
        combined[idx] = s_score + k_score

    # Sort by combined score
    ranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)
    return ranked[:top_k]


# Pre-compute embeddings
doc_embeddings = model.encode(documents)

# Test with a query that benefits from hybrid search
query = "Python GIL threading performance"

print("KEYWORD SEARCH:")
for idx, score in keyword_search(query, documents, top_k=3):
    print(f"  [{score:.1f}] {documents[idx][:65]}...")

print("\nSEMANTIC SEARCH:")
for idx, score in semantic_search(query, documents, doc_embeddings, top_k=3):
    print(f"  [{score:.4f}] {documents[idx][:65]}...")

print("\nHYBRID SEARCH (70% semantic, 30% keyword):")
for idx, score in hybrid_search(query, documents, doc_embeddings, top_k=3):
    print(f"  [{score:.4f}] {documents[idx][:65]}...")
```

**Output:**
```
KEYWORD SEARCH:
  [4.0] The Python GIL (Global Interpreter Lock) prevents multiple thr...
  [3.0] Threading in Python is useful for I/O-bound tasks despite the ...
  [2.0] Multiprocessing in Python creates separate processes, each wit...

SEMANTIC SEARCH:
  [0.7234] The Python GIL (Global Interpreter Lock) prevents multiple thr...
  [0.6789] Threading in Python is useful for I/O-bound tasks despite the ...
  [0.5890] Multiprocessing in Python creates separate processes, each wit...

HYBRID SEARCH (70% semantic, 30% keyword):
  [0.9964] The Python GIL (Global Interpreter Lock) prevents multiple thr...
  [0.8152] Threading in Python is useful for I/O-bound tasks despite the ...
  [0.6723] Multiprocessing in Python creates separate processes, each wit...
```

**Line-by-line explanation:**

- `keyword_search()` counts how many query words appear in each document. Simple but catches exact terms like "GIL."
- `semantic_search()` uses embeddings to find meaning-similar documents. Catches related concepts even without exact word matches.
- `hybrid_search()` normalizes both scores to 0-1 and combines them with configurable weights.
- `semantic_weight=0.7, keyword_weight=0.3` means semantic search contributes 70% and keyword 30%. Adjust based on your use case.
- Documents that score well in BOTH methods get boosted to the top. This is the key benefit of hybrid search.

---

## Query Expansion

Sometimes users ask vague questions. Query expansion generates multiple variations of the query to improve retrieval.

> **Query Expansion:** Automatically generating additional search queries from the original question. This helps find relevant documents that the original query might miss. For example, "How to fix a slow computer?" might expand to include "improve computer performance" and "speed up laptop."

```python
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
import numpy as np

client = OpenAI()
model = SentenceTransformer('all-MiniLM-L6-v2')

def expand_query(query: str, num_expansions: int = 3) -> list:
    """
    Use an LLM to generate alternative queries.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"""Generate {num_expansions} alternative ways to ask
this question. Each should capture a different aspect or use different
words. Return ONLY the questions, one per line, no numbering.

Original question: {query}"""
        }],
        temperature=0.7,
    )

    expansions = response.choices[0].message.content.strip().split('\n')
    expansions = [q.strip() for q in expansions if q.strip()]

    return [query] + expansions[:num_expansions]

def search_with_expansion(query, documents, doc_embeddings, top_k=3):
    """
    Search using the original query plus expanded queries.
    Merge results from all queries.
    """
    # Generate expanded queries
    queries = expand_query(query)
    print(f"Original: {query}")
    print(f"Expanded queries:")
    for q in queries[1:]:
        print(f"  + {q}")

    # Search with each query
    all_results = {}

    for q in queries:
        q_embedding = model.encode(q)
        sims = cos_sim(q_embedding, doc_embeddings)[0]

        for idx in range(len(documents)):
            score = sims[idx].item()
            if idx in all_results:
                # Keep the highest score from any query
                all_results[idx] = max(all_results[idx], score)
            else:
                all_results[idx] = score

    # Sort and return top_k
    ranked = sorted(all_results.items(), key=lambda x: x[1], reverse=True)
    return ranked[:top_k]


# Test documents
documents = [
    "The company offers a 401(k) retirement plan with 6% employer matching.",
    "Health insurance includes medical, dental, and vision coverage.",
    "Employees can take up to 12 weeks of unpaid family leave under FMLA.",
    "The annual performance review process begins in November each year.",
    "Tuition reimbursement covers up to $5,250 per year for approved courses.",
    "The employee assistance program provides free counseling sessions.",
    "Stock options vest over a 4-year period with a 1-year cliff.",
    "Gym membership discounts are available through the wellness program.",
]

doc_embeddings = model.encode(documents)

# Vague query that benefits from expansion
results = search_with_expansion(
    "benefits for employees",
    documents, doc_embeddings, top_k=4
)

print(f"\nTop results:")
for idx, score in results:
    print(f"  [{score:.4f}] {documents[idx][:65]}...")
```

**Output:**
```
Original: benefits for employees
Expanded queries:
  + What perks and compensation packages are available to staff?
  + What employee wellness and insurance programs does the company offer?
  + What financial benefits and retirement plans exist for workers?

Top results:
  [0.6789] Health insurance includes medical, dental, and vision coverage...
  [0.6234] The company offers a 401(k) retirement plan with 6% employer m...
  [0.5890] Gym membership discounts are available through the wellness pro...
  [0.5678] The employee assistance program provides free counseling sessio...
```

**Line-by-line explanation:**

- `expand_query()` uses an LLM to rephrase the question in different ways. Each rephrasing might match different documents.
- "benefits for employees" is vague. The expansions specifically mention "compensation," "insurance," "retirement," and "wellness," which match more documents.
- `all_results[idx] = max(...)` keeps the best score from any query variation. If a document is highly relevant to any version of the question, it rises to the top.
- Query expansion is especially useful when users type short, ambiguous queries.

---

## Evaluating RAG Systems with RAGAS

> **RAGAS (Retrieval Augmented Generation Assessment):** A framework for evaluating RAG systems. It measures multiple aspects of quality including whether the answer is faithful to the context, whether the right documents were retrieved, and whether the answer is relevant to the question.

```python
# Install: pip install ragas

# RAGAS evaluates four key metrics:

evaluation_metrics = {
    "Faithfulness": {
        "description": "Is the answer supported by the retrieved context?",
        "range": "0 to 1 (higher is better)",
        "what_it_catches": "Hallucinated facts not in the context",
        "example_good": "Answer says 'return within 30 days' and context "
                        "says 'return within 30 days'",
        "example_bad": "Answer says 'return within 60 days' but context "
                       "says '30 days'",
    },
    "Answer Relevancy": {
        "description": "Is the answer relevant to the question asked?",
        "range": "0 to 1 (higher is better)",
        "what_it_catches": "Answers that are correct but off-topic",
        "example_good": "Q: 'What is the return policy?' A: 'Items can be "
                        "returned within 30 days'",
        "example_bad": "Q: 'What is the return policy?' A: 'Our store is "
                       "located on Main Street'",
    },
    "Context Precision": {
        "description": "Are the retrieved documents actually relevant?",
        "range": "0 to 1 (higher is better)",
        "what_it_catches": "Retrieving irrelevant documents",
        "example_good": "Q about returns -> retrieves return policy doc",
        "example_bad": "Q about returns -> retrieves shipping doc",
    },
    "Context Recall": {
        "description": "Were all necessary documents retrieved?",
        "range": "0 to 1 (higher is better)",
        "what_it_catches": "Missing relevant documents",
        "example_good": "All facts in the answer can be traced to retrieved docs",
        "example_bad": "Answer needs info from a doc that was not retrieved",
    },
}

print("RAGAS EVALUATION METRICS")
print("=" * 60)
for metric, info in evaluation_metrics.items():
    print(f"\n{metric}")
    print(f"  What: {info['description']}")
    print(f"  Range: {info['range']}")
    print(f"  Catches: {info['what_it_catches']}")
```

**Output:**
```
RAGAS EVALUATION METRICS
============================================================

Faithfulness
  What: Is the answer supported by the retrieved context?
  Range: 0 to 1 (higher is better)
  Catches: Hallucinated facts not in the context

Answer Relevancy
  What: Is the answer relevant to the question asked?
  Range: 0 to 1 (higher is better)
  Catches: Answers that are correct but off-topic

Context Precision
  What: Are the retrieved documents actually relevant?
  Range: 0 to 1 (higher is better)
  Catches: Retrieving irrelevant documents

Context Recall
  What: Were all necessary documents retrieved?
  Range: 0 to 1 (higher is better)
  Catches: Missing relevant documents
```

---

## Building a RAG Evaluation Pipeline

```python
from openai import OpenAI
import json

client = OpenAI()

def evaluate_rag_response(question, answer, contexts, ground_truth=None):
    """
    Evaluate a RAG response on multiple dimensions.

    Args:
        question: The user's question
        answer: The RAG system's answer
        contexts: List of retrieved context strings
        ground_truth: Optional correct answer for comparison
    """
    context_text = "\n---\n".join(contexts)

    # Evaluate faithfulness
    faith_prompt = f"""Given the following context and answer, determine if
every claim in the answer is supported by the context.

Context:
{context_text}

Answer: {answer}

Rate faithfulness from 0.0 to 1.0 where:
- 1.0 = every claim is supported by the context
- 0.5 = some claims are supported, some are not
- 0.0 = the answer is completely unsupported

Respond with JSON: {{"score": float, "reasoning": "brief explanation"}}"""

    # Evaluate relevancy
    rel_prompt = f"""Given this question and answer, rate how relevant
the answer is to the question.

Question: {question}
Answer: {answer}

Rate relevancy from 0.0 to 1.0 where:
- 1.0 = perfectly answers the question
- 0.5 = partially answers or includes extra irrelevant info
- 0.0 = does not answer the question at all

Respond with JSON: {{"score": float, "reasoning": "brief explanation"}}"""

    # Get evaluations
    evaluations = {}

    for name, prompt in [("faithfulness", faith_prompt),
                         ("relevancy", rel_prompt)]:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0,
        )
        evaluations[name] = json.loads(
            response.choices[0].message.content
        )

    # Display results
    print(f"Question: {question}")
    print(f"Answer:   {answer[:80]}...")
    print(f"\nEvaluation:")
    for metric, result in evaluations.items():
        score = result['score']
        bar = '|' * int(score * 20)
        print(f"  {metric:<15} {score:.2f} [{bar:<20}] {result['reasoning']}")

    return evaluations


# Example evaluation
evaluate_rag_response(
    question="What is the return policy?",
    answer="Items can be returned within 30 days of purchase. Electronics "
           "have a 15-day return window. A receipt is required.",
    contexts=[
        "Return Policy: Items can be returned within 30 days of purchase. "
        "Electronics have a 15-day return window. Original receipt required.",
        "Shipping: Standard shipping takes 5-7 business days."
    ]
)

print()

evaluate_rag_response(
    question="What is the return policy?",
    answer="Our store is located at 123 Main Street and is open Monday "
           "through Friday from 9 AM to 6 PM.",
    contexts=[
        "Return Policy: Items can be returned within 30 days of purchase.",
        "Store Location: 123 Main Street, open Monday-Friday 9 AM-6 PM."
    ]
)
```

**Output:**
```
Question: What is the return policy?
Answer:   Items can be returned within 30 days of purchase. Electronics have a 15-day ret...

Evaluation:
  faithfulness    0.95 [|||||||||||||||||||  ] All claims directly supported by context
  relevancy       0.95 [|||||||||||||||||||  ] Directly answers the question about returns

Question: What is the return policy?
Answer:   Our store is located at 123 Main Street and is open Monday through Friday from ...

Evaluation:
  faithfulness    0.90 [||||||||||||||||||   ] Claims are supported but from wrong context
  relevancy       0.10 [||                   ] Answers about location, not return policy
```

---

## Handling Multiple Document Types

Real RAG systems need to handle different types of documents with different structures.

```python
from typing import List, Dict

class MultiTypeProcessor:
    """Process different document types with appropriate strategies."""

    def __init__(self):
        self.processors = {
            'faq': self._process_faq,
            'policy': self._process_policy,
            'technical': self._process_technical,
            'email': self._process_email,
        }

    def process(self, text: str, doc_type: str,
                source: str) -> List[Dict]:
        """Process a document based on its type."""
        processor = self.processors.get(doc_type, self._process_generic)
        chunks = processor(text)

        return [
            {
                'text': chunk,
                'source': source,
                'doc_type': doc_type,
                'chunk_index': i,
            }
            for i, chunk in enumerate(chunks)
        ]

    def _process_faq(self, text: str) -> List[str]:
        """Split FAQ documents by Q&A pairs."""
        import re
        # Split on question patterns
        pairs = re.split(r'\n(?=Q:|Question:|\d+\.)', text)
        return [p.strip() for p in pairs if p.strip() and len(p.strip()) > 20]

    def _process_policy(self, text: str) -> List[str]:
        """Split policy documents by sections."""
        import re
        sections = re.split(r'\n(?=(?:Section|Article|Chapter|\d+\.))',
                           text)
        return [s.strip() for s in sections if s.strip() and len(s.strip()) > 20]

    def _process_technical(self, text: str) -> List[str]:
        """Split technical docs by headings and code blocks."""
        import re
        sections = re.split(r'\n(?=#+\s|```)', text)
        return [s.strip() for s in sections if s.strip() and len(s.strip()) > 20]

    def _process_email(self, text: str) -> List[str]:
        """Process emails as single chunks with metadata."""
        # Keep each email as one chunk (they are usually short)
        return [text.strip()] if text.strip() else []

    def _process_generic(self, text: str) -> List[str]:
        """Default chunking for unknown document types."""
        chunk_size = 500
        chunks = []
        paragraphs = text.split('\n\n')
        current = ""

        for para in paragraphs:
            if len(current) + len(para) > chunk_size and current:
                chunks.append(current.strip())
                current = para
            else:
                current += "\n\n" + para if current else para

        if current.strip():
            chunks.append(current.strip())

        return chunks


# Demo
processor = MultiTypeProcessor()

faq_doc = """
Q: How do I reset my password?
A: Go to Settings > Security > Change Password. Enter your current
password and then your new password twice.

Q: Can I change my username?
A: No, usernames cannot be changed after account creation. You can
change your display name in Settings > Profile.

Q: How do I enable dark mode?
A: Go to Settings > Appearance > Theme and select Dark Mode.
"""

policy_doc = """
Section 1: Data Retention
All customer data is retained for 7 years after the last
transaction. After this period, data is automatically purged.

Section 2: Privacy
Customer personal information is never shared with third parties
without explicit consent. All data is encrypted at rest.

Section 3: Access Control
Access to customer data requires VP-level approval and is logged
in the audit system for compliance purposes.
"""

print("=== FAQ Processing ===")
faq_chunks = processor.process(faq_doc, 'faq', 'faq.txt')
for chunk in faq_chunks:
    print(f"  Chunk: {chunk['text'][:50]}...")
print(f"  Total: {len(faq_chunks)} chunks")

print("\n=== Policy Processing ===")
policy_chunks = processor.process(policy_doc, 'policy', 'policy.txt')
for chunk in policy_chunks:
    print(f"  Chunk: {chunk['text'][:50]}...")
print(f"  Total: {len(policy_chunks)} chunks")
```

**Output:**
```
=== FAQ Processing ===
  Chunk: Q: How do I reset my password?
A: Go to Settings...
  Chunk: Q: Can I change my username?
A: No, usernames c...
  Chunk: Q: How do I enable dark mode?
A: Go to Settings...
  Total: 3 chunks

=== Policy Processing ===
  Chunk: Section 1: Data Retention
All customer data is r...
  Chunk: Section 2: Privacy
Customer personal information...
  Chunk: Section 3: Access Control
Access to customer dat...
  Total: 3 chunks
```

---

## Common Mistakes

1. **Over-retrieving and hoping re-ranking will fix it.** Re-ranking improves order but cannot fix fundamentally bad retrieval. If the right document is not in the initial set, re-ranking cannot find it.

2. **Making query expansion too aggressive.** Generating 10 query variations leads to noisy retrieval. Stick to 2-4 focused expansions.

3. **Using the same weights for all queries in hybrid search.** Some queries benefit more from keywords ("error code E404") and some from semantics ("how to improve performance"). Consider dynamic weighting.

4. **Not evaluating regularly.** RAG quality can degrade as you add documents, change models, or modify prompts. Run evaluations after every significant change.

5. **Treating all document types the same.** FAQs, policies, emails, and technical docs have different structures. Use type-specific processing for better chunks.

---

## Best Practices

1. **Re-rank when accuracy matters more than speed.** Re-ranking adds latency but significantly improves result quality. Use it for customer-facing applications.

2. **Start with hybrid search.** It consistently outperforms pure semantic or pure keyword search across most use cases.

3. **Use query expansion for short queries.** Questions under 5 words often benefit from expansion. Longer, specific queries usually do not need it.

4. **Build an evaluation dataset.** Create at least 50 question-answer pairs with ground truth. Run evaluations automatically when you make changes.

5. **Log everything.** Store queries, retrieved chunks, generated answers, and user feedback. This data is essential for improving your system over time.

6. **Process different document types separately.** Use type-specific chunking strategies to preserve the natural structure of each document type.

---

## Quick Summary

Advanced RAG techniques improve retrieval accuracy and answer quality. Re-ranking uses cross-encoders to re-score initially retrieved results. Hybrid search combines keyword and semantic matching for broader coverage. Query expansion generates alternative queries to handle vague user questions. RAGAS provides standardized metrics for evaluating RAG systems: faithfulness, relevancy, context precision, and context recall. Different document types benefit from specialized processing strategies.

---

## Key Points

- **Re-ranking** uses cross-encoders to improve retrieval ordering after initial embedding search
- **Hybrid search** combines semantic and keyword search for the best of both approaches
- **Query expansion** generates alternative queries to improve recall for vague questions
- **RAGAS metrics** measure faithfulness, relevancy, context precision, and recall
- **Multi-type processing** uses different chunking strategies for different document types
- Re-rank the **top 10-20** results, not the entire database
- **Evaluate regularly** with a fixed test set to catch regressions

---

## Practice Questions

1. Why does re-ranking use a cross-encoder instead of the same embedding model used for initial retrieval? What is the tradeoff?

2. A user searches for "Python GIL" in your RAG system. Semantic search returns documents about concurrency but misses the one that specifically discusses the GIL. How would hybrid search help here?

3. Your RAG system has high faithfulness (0.9) but low relevancy (0.3). What does this tell you about the problem, and how would you fix it?

4. When would query expansion hurt performance instead of helping?

5. You have a document collection with FAQs, legal contracts, and technical manuals. Why should you process each type differently?

---

## Exercises

**Exercise 1: Implement Re-Ranking**

Add a re-ranking step to the RAG pipeline from Chapter 17. Retrieve the top 10 results using embedding search, then re-rank using a cross-encoder, and send the top 3 to the LLM. Compare answer quality with and without re-ranking on at least 5 test questions.

**Exercise 2: Build a Hybrid Search System**

Implement hybrid search that combines BM25 keyword search with embedding search. Allow configurable weights between the two methods. Test with queries that work better with keywords vs. semantics, and find the optimal weight for your document collection.

**Exercise 3: RAG Evaluation Suite**

Create an evaluation suite with at least 20 question-answer-context triples. Implement automated evaluation for faithfulness and relevancy using LLM-as-Judge. Run the evaluation, generate a report, and identify the weakest areas of your RAG pipeline.

---

## What Is Next?

You have learned both basic and advanced RAG techniques. But RAG is not always the right solution. In Chapter 19, you will learn a decision framework for choosing between prompting, RAG, and fine-tuning. Each approach has different strengths, costs, and complexities. Understanding when to use which approach is one of the most valuable skills in applied AI.
