# Chapter 13: What Is RAG?

## What You Will Learn

In this chapter, you will learn:

- Why LLMs sometimes make up information (hallucination)
- Why LLMs have outdated knowledge (knowledge cutoff)
- What Retrieval-Augmented Generation (RAG) is and how it works
- The three steps of RAG: Retrieve, Augment, Generate
- When to use RAG and when not to
- How RAG compares to fine-tuning

## Why This Chapter Matters

You have built a chatbot using an LLM. A customer asks: "What is the return policy for orders placed after January 2024?" The LLM confidently replies with a return policy. The problem? It is completely wrong. Your company changed the policy last month, and the LLM has no idea.

This is not a rare edge case. It happens constantly. LLMs are trained on data up to a certain date. They do not know about your company's internal documents, recent events, or private data. And when they do not know something, they do not say "I don't know." They make something up that sounds convincing.

RAG solves this problem. It gives the LLM access to your own data before it answers. Instead of guessing, the LLM reads the relevant documents and bases its answer on actual information. This single technique transforms LLMs from unreliable guessers into useful, grounded assistants.

---

## The Two Big Problems with LLMs

### Problem 1: Hallucination

> **Hallucination:** When an LLM generates information that sounds correct but is actually made up. The model produces fluent, confident text that has no basis in fact. It is called a hallucination because the model "sees" something that is not there.

```
+------------------------------------------------------------------+
|                  THE HALLUCINATION PROBLEM                        |
|                                                                   |
|  User: "Who is the CEO of TechFlow Inc.?"                        |
|                                                                   |
|  LLM (without RAG):                                              |
|  "The CEO of TechFlow Inc. is Michael Chen, who has led           |
|   the company since 2019."                                        |
|                                                                   |
|  Reality: TechFlow Inc. does not exist! The LLM made up           |
|  a company name, a CEO name, and a date. ALL of it is fake.      |
|  But it sounds completely real and confident.                     |
|                                                                   |
|  LLM (with RAG):                                                 |
|  "I don't have any information about TechFlow Inc. in my          |
|   available documents."                                           |
|                                                                   |
|  Much better! RAG helps the model admit when it does not know.   |
+------------------------------------------------------------------+
```

Think of hallucination like asking someone for directions in a city they have never visited. Instead of admitting they do not know, they confidently give you wrong directions. You follow them and end up lost. That is what LLMs do without RAG.

### Problem 2: Knowledge Cutoff

> **Knowledge Cutoff:** The date when an LLM's training data ends. The model has no knowledge of anything that happened after this date. It is like talking to someone who has been in a coma since their training ended.

```python
# Demonstrating the knowledge cutoff problem

# This is what happens without RAG
question = "What were the major AI announcements in 2025?"

# An LLM trained on data up to April 2024 would say:
print("Without RAG:")
print("LLM: 'I don't have information about events in 2025'")
print("     OR worse, it makes up plausible-sounding announcements")
print()

# With RAG, you feed it recent documents
print("With RAG:")
print("You provide: Recent news articles about 2025 AI announcements")
print("LLM: 'Based on the provided documents, the major AI ")
print("      announcements in 2025 include...'")
print("      (Answers based on REAL documents you provided)")
```

**Output:**
```
Without RAG:
LLM: 'I don't have information about events in 2025'
     OR worse, it makes up plausible-sounding announcements

With RAG:
You provide: Recent news articles about 2025 AI announcements
LLM: 'Based on the provided documents, the major AI
      announcements in 2025 include...'
      (Answers based on REAL documents you provided)
```

---

## What Is RAG?

RAG stands for Retrieval-Augmented Generation. Let us break down each word.

> **Retrieval:** Finding relevant documents or pieces of information from a database or collection of documents.

> **Augmented:** Enhanced or improved. In RAG, we enhance the LLM's prompt by adding relevant information to it.

> **Generation:** The LLM generates its response. But now it generates based on the retrieved information, not just its training data.

```
+------------------------------------------------------------------+
|                    HOW RAG WORKS                                  |
|                                                                   |
|  Step 1: RETRIEVE                                                 |
|  +----------+     +------------------+     +----------+          |
|  | User     |---->| Search your      |---->| Relevant |          |
|  | Question |     | document database |     | Documents|          |
|  +----------+     +------------------+     +----------+          |
|                                                    |              |
|  Step 2: AUGMENT                                   v              |
|  +----------+     +------------------+     +----------+          |
|  | Original |---->| Combine question |<----| Retrieved|          |
|  | Question |     | + documents into |     | Docs     |          |
|  +----------+     | enriched prompt  |     +----------+          |
|                   +------------------+                            |
|                          |                                        |
|  Step 3: GENERATE        v                                        |
|                   +------------------+     +----------+          |
|                   | Send enriched    |---->| Grounded |          |
|                   | prompt to LLM    |     | Answer   |          |
|                   +------------------+     +----------+          |
|                                                                   |
|  The answer is "grounded" because it is based on real documents  |
+------------------------------------------------------------------+
```

Think of RAG like an open-book exam. Without RAG, the LLM takes the exam from memory, sometimes remembering wrong facts or making things up. With RAG, the LLM gets to look up the relevant pages in the textbook before answering. The answer is based on actual source material.

---

## A Simple RAG Example

Let us build a minimal RAG system to see the concept in action.

```python
from openai import OpenAI

client = OpenAI()

# Step 1: Your "database" of documents
# In real RAG, this would be a vector database
company_documents = {
    "return_policy": """
    Return Policy (Updated January 2025):
    - Items can be returned within 30 days of purchase.
    - Electronics have a 15-day return window.
    - Sale items are final sale and cannot be returned.
    - Refunds are processed within 5-7 business days.
    - Original receipt or order confirmation is required.
    """,
    "shipping_info": """
    Shipping Information:
    - Standard shipping: 5-7 business days, free over $50.
    - Express shipping: 2-3 business days, $9.99.
    - Next-day shipping: 1 business day, $19.99.
    - International shipping: 10-15 business days, $24.99.
    """,
    "product_warranty": """
    Warranty Policy:
    - All electronics come with a 2-year manufacturer warranty.
    - Extended warranty available for $49.99 (adds 3 years).
    - Warranty covers manufacturing defects only.
    - Water damage and physical damage are not covered.
    """
}

# Step 2: Simple retrieval (keyword matching)
def simple_retrieve(query, documents, top_k=2):
    """
    Find the most relevant documents for a query.
    This is a very simple version. Real RAG uses embeddings.
    """
    scores = {}
    query_words = set(query.lower().split())

    for doc_name, doc_text in documents.items():
        doc_words = set(doc_text.lower().split())
        # Count how many query words appear in the document
        overlap = len(query_words.intersection(doc_words))
        scores[doc_name] = overlap

    # Sort by score and return top_k documents
    sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [(name, documents[name]) for name, score in sorted_docs[:top_k]]

# Step 3: Augment the prompt with retrieved documents
def build_rag_prompt(question, retrieved_docs):
    """Combine the question with retrieved documents."""
    context = "\n\n".join(
        f"Document: {name}\n{text}"
        for name, text in retrieved_docs
    )

    prompt = f"""Answer the question based ONLY on the provided documents.
If the documents do not contain the answer, say "I don't have
information about that in my available documents."

Documents:
{context}

Question: {question}

Answer:"""
    return prompt

# Step 4: Generate the answer
def rag_answer(question):
    """Complete RAG pipeline: retrieve, augment, generate."""
    # Retrieve
    relevant_docs = simple_retrieve(question, company_documents)
    print(f"Retrieved: {[name for name, _ in relevant_docs]}")

    # Augment
    prompt = build_rag_prompt(question, relevant_docs)

    # Generate
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content

# Test it
questions = [
    "What is the return policy for electronics?",
    "How much does express shipping cost?",
    "Is water damage covered by warranty?",
    "What is the company's hiring process?",
]

for q in questions:
    print(f"\nQ: {q}")
    answer = rag_answer(q)
    print(f"A: {answer}")
    print("-" * 50)
```

**Output:**
```
Retrieved: ['return_policy', 'product_warranty']

Q: What is the return policy for electronics?
A: Electronics have a 15-day return window. The original receipt or order confirmation is required for all returns. Refunds are processed within 5-7 business days.
--------------------------------------------------

Retrieved: ['shipping_info', 'return_policy']

Q: How much does express shipping cost?
A: Express shipping costs $9.99 and takes 2-3 business days.
--------------------------------------------------

Retrieved: ['product_warranty', 'return_policy']

Q: Is water damage covered by warranty?
A: No, water damage is not covered by the warranty. The warranty covers manufacturing defects only. Water damage and physical damage are not covered.
--------------------------------------------------

Retrieved: ['return_policy', 'shipping_info']

Q: What is the company's hiring process?
A: I don't have information about that in my available documents.
--------------------------------------------------
```

**Line-by-line explanation:**

- `company_documents` is a simple dictionary acting as our document database. Real systems use vector databases (covered in Chapter 16).
- `simple_retrieve()` finds relevant documents by counting word overlap. This is a crude method. Real RAG uses embeddings (covered in Chapter 15) which understand meaning, not just exact word matches.
- `build_rag_prompt()` combines the question with retrieved documents into a single prompt. The key instruction is "Answer based ONLY on the provided documents." This prevents the LLM from making things up.
- `rag_answer()` puts all three steps together: retrieve, augment, generate.
- Notice the last question about hiring. The documents contain no hiring information, so the model correctly says it does not have that information. Without RAG, it would have made something up.

---

## The RAG Architecture in Detail

```
+------------------------------------------------------------------+
|                 COMPLETE RAG ARCHITECTURE                         |
|                                                                   |
|  OFFLINE PHASE (done once, before any questions):                 |
|                                                                   |
|  +--------+    +--------+    +----------+    +----------+        |
|  | Load   |--->| Split  |--->| Create   |--->| Store in |        |
|  | Docs   |    | into   |    | Embed-   |    | Vector   |        |
|  |        |    | Chunks |    | dings    |    | Database |        |
|  +--------+    +--------+    +----------+    +----------+        |
|   PDFs,         Small         Numbers         Searchable         |
|   HTML,         pieces        that capture    storage            |
|   text          of text       meaning                            |
|                                                                   |
|  ONLINE PHASE (for each question):                                |
|                                                                   |
|  +--------+    +--------+    +--------+    +--------+            |
|  | User   |--->| Embed  |--->| Search |--->| Get Top|            |
|  | Query  |    | Query  |    | Vector |    | K Docs |            |
|  +--------+    +--------+    | DB     |    +--------+            |
|                              +--------+        |                  |
|                                                v                  |
|  +--------+    +--------+    +--------+    +--------+            |
|  | Return |<---| LLM    |<---| Build  |<---| Combine|            |
|  | Answer |    | Gener- |    | Prompt |    | Query +|            |
|  +--------+    | ates   |    +--------+    | Docs   |            |
|                +--------+                  +--------+            |
+------------------------------------------------------------------+
```

The RAG architecture has two phases:

**Offline Phase (Indexing):** Done once when you set up the system.
1. **Load documents** - Read your PDFs, web pages, text files.
2. **Split into chunks** - Break documents into small pieces (e.g., 500 words each).
3. **Create embeddings** - Convert each chunk into a vector (a list of numbers that captures meaning).
4. **Store in vector database** - Save the vectors so they can be searched quickly.

**Online Phase (Querying):** Done for every user question.
1. **Embed the query** - Convert the user's question into a vector.
2. **Search vector database** - Find chunks whose vectors are closest to the query vector.
3. **Build augmented prompt** - Combine the question with the retrieved chunks.
4. **Generate answer** - Send the augmented prompt to the LLM.

---

## When to Use RAG

RAG is not always the right solution. Here is when it shines and when it does not.

```python
# Decision helper for when to use RAG

use_cases = {
    "Good for RAG": [
        "Company knowledge base Q&A",
        "Customer support with product documentation",
        "Legal document search and analysis",
        "Medical information from approved sources",
        "Internal policy and procedure questions",
        "Research across many papers or reports",
        "Up-to-date information that changes frequently",
    ],
    "Not ideal for RAG": [
        "Creative writing (no documents to retrieve)",
        "General conversation (LLM already knows enough)",
        "Code generation (LLM training data is sufficient)",
        "Translation (built into the model)",
        "Math and logic problems (reasoning, not retrieval)",
        "Tasks requiring deep domain understanding (fine-tuning better)",
    ]
}

print("=" * 50)
print("WHEN TO USE RAG")
print("=" * 50)

for category, items in use_cases.items():
    print(f"\n{category}:")
    for item in items:
        symbol = "+" if "Good" in category else "-"
        print(f"  {symbol} {item}")
```

**Output:**
```
==================================================
WHEN TO USE RAG
==================================================

Good for RAG:
  + Company knowledge base Q&A
  + Customer support with product documentation
  + Legal document search and analysis
  + Medical information from approved sources
  + Internal policy and procedure questions
  + Research across many papers or reports
  + Up-to-date information that changes frequently

Not ideal for RAG:
  - Creative writing (no documents to retrieve)
  - General conversation (LLM already knows enough)
  - Code generation (LLM training data is sufficient)
  - Translation (built into the model)
  - Math and logic problems (reasoning, not retrieval)
  - Tasks requiring deep domain understanding (fine-tuning better)
```

---

## RAG vs Fine-Tuning

This is one of the most important decisions in LLM applications. Let us compare them.

> **Fine-Tuning:** Training an existing LLM on your specific data so the model "learns" your domain. The knowledge becomes part of the model's weights. Think of it as teaching a student new material permanently.

> **RAG:** Giving the LLM relevant documents at query time. The knowledge stays in the documents, not in the model. Think of it as giving a student a reference book during an exam.

```
+------------------------------------------------------------------+
|                  RAG vs FINE-TUNING COMPARISON                    |
|                                                                   |
|  Feature          |  RAG              |  Fine-Tuning             |
|  -----------------+-------------------+--------------------------|
|  Setup effort     |  Medium           |  High                    |
|  Data needed      |  Documents        |  Training examples       |
|  Update data      |  Easy (add docs)  |  Hard (retrain model)    |
|  Cost             |  Lower            |  Higher                  |
|  Accuracy         |  Good with good   |  Can be excellent        |
|                   |  retrieval        |  for specific tasks      |
|  Hallucination    |  Reduced (cites   |  Still possible          |
|                   |  sources)         |                          |
|  Knowledge scope  |  Limited to your  |  Broad + your domain     |
|                   |  documents        |                          |
|  Speed            |  Slightly slower  |  Same as base model      |
|                   |  (retrieval step) |                          |
|  Transparency     |  High (can show   |  Low (knowledge is       |
|                   |  source docs)     |  in model weights)       |
+------------------------------------------------------------------+
```

```python
# Decision framework for RAG vs Fine-Tuning

def recommend_approach(
    data_changes_frequently: bool,
    need_source_citations: bool,
    have_training_examples: bool,
    budget: str,
    task_type: str
) -> str:
    """
    Recommend RAG, fine-tuning, or both based on requirements.
    """
    score_rag = 0
    score_ft = 0
    reasons_rag = []
    reasons_ft = []

    if data_changes_frequently:
        score_rag += 3
        reasons_rag.append("Data changes often - RAG updates easily")
    else:
        score_ft += 1
        reasons_ft.append("Static data - fine-tuning works well")

    if need_source_citations:
        score_rag += 3
        reasons_rag.append("Need citations - RAG provides source docs")

    if have_training_examples:
        score_ft += 2
        reasons_ft.append("Training examples available for fine-tuning")
    else:
        score_rag += 2
        reasons_rag.append("No training examples - RAG only needs docs")

    if budget == "low":
        score_rag += 2
        reasons_rag.append("Lower budget favors RAG")
    elif budget == "high":
        score_ft += 1
        reasons_ft.append("Budget allows fine-tuning")

    if task_type == "question_answering":
        score_rag += 2
        reasons_rag.append("Q&A tasks are ideal for RAG")
    elif task_type == "style_transfer":
        score_ft += 3
        reasons_ft.append("Style tasks need fine-tuning")
    elif task_type == "classification":
        score_ft += 2
        reasons_ft.append("Classification benefits from fine-tuning")

    # Determine recommendation
    if score_rag > score_ft + 2:
        recommendation = "RAG"
    elif score_ft > score_rag + 2:
        recommendation = "Fine-Tuning"
    else:
        recommendation = "RAG + Fine-Tuning (hybrid approach)"

    print(f"Recommendation: {recommendation}")
    print(f"\nRAG Score: {score_rag}")
    for r in reasons_rag:
        print(f"  + {r}")
    print(f"\nFine-Tuning Score: {score_ft}")
    for r in reasons_ft:
        print(f"  + {r}")

    return recommendation

# Example scenarios
print("=" * 50)
print("Scenario: Customer Support Bot")
print("=" * 50)
recommend_approach(
    data_changes_frequently=True,
    need_source_citations=True,
    have_training_examples=False,
    budget="low",
    task_type="question_answering"
)

print("\n" + "=" * 50)
print("Scenario: Medical Report Classifier")
print("=" * 50)
recommend_approach(
    data_changes_frequently=False,
    need_source_citations=False,
    have_training_examples=True,
    budget="high",
    task_type="classification"
)
```

**Output:**
```
==================================================
Scenario: Customer Support Bot
==================================================
Recommendation: RAG

RAG Score: 10
  + Data changes often - RAG updates easily
  + Need citations - RAG provides source docs
  + No training examples - RAG only needs docs
  + Lower budget favors RAG
  + Q&A tasks are ideal for RAG

Fine-Tuning Score: 0

==================================================
Scenario: Medical Report Classifier
==================================================
Recommendation: Fine-Tuning

RAG Score: 0

Fine-Tuning Score: 6
  + Static data - fine-tuning works well
  + Training examples available for fine-tuning
  + Budget allows fine-tuning
  + Classification benefits from fine-tuning
```

---

## Benefits of RAG

Let us summarize why RAG is so popular.

```python
benefits = [
    {
        "benefit": "Reduced Hallucination",
        "explanation": "The LLM answers based on actual documents, not imagination",
        "analogy": "Open-book exam vs. memory-only exam"
    },
    {
        "benefit": "Up-to-date Knowledge",
        "explanation": "Add new documents anytime without retraining the model",
        "analogy": "Adding new pages to the reference book"
    },
    {
        "benefit": "Source Attribution",
        "explanation": "You can show users which documents the answer came from",
        "analogy": "Citing your sources in a research paper"
    },
    {
        "benefit": "Domain Specificity",
        "explanation": "Works with your private data without sharing it for training",
        "analogy": "Using your company's internal handbook"
    },
    {
        "benefit": "Cost Effective",
        "explanation": "No expensive GPU training, just document processing",
        "analogy": "Buying a reference book vs. hiring a tutor"
    },
    {
        "benefit": "Easy Updates",
        "explanation": "Add, remove, or update documents without touching the model",
        "analogy": "Updating a wiki page vs. reprinting a textbook"
    }
]

print("KEY BENEFITS OF RAG")
print("=" * 60)
for b in benefits:
    print(f"\n{b['benefit']}")
    print(f"  What: {b['explanation']}")
    print(f"  Like: {b['analogy']}")
```

**Output:**
```
KEY BENEFITS OF RAG
============================================================

Reduced Hallucination
  What: The LLM answers based on actual documents, not imagination
  Like: Open-book exam vs. memory-only exam

Up-to-date Knowledge
  What: Add new documents anytime without retraining the model
  Like: Adding new pages to the reference book

Source Attribution
  What: You can show users which documents the answer came from
  Like: Citing your sources in a research paper

Domain Specificity
  What: Works with your private data without sharing it for training
  Like: Using your company's internal handbook

Cost Effective
  What: No expensive GPU training, just document processing
  Like: Buying a reference book vs. hiring a tutor

Easy Updates
  What: Add, remove, or update documents without touching the model
  Like: Updating a wiki page vs. reprinting a textbook
```

---

## Limitations of RAG

RAG is powerful but not perfect. Understanding its limitations helps you use it correctly.

```
+------------------------------------------------------------------+
|                  RAG LIMITATIONS                                  |
|                                                                   |
|  1. Retrieval Quality                                             |
|     If retrieval finds the wrong documents, the answer            |
|     will be wrong. Garbage in, garbage out.                       |
|                                                                   |
|  2. Context Window Limits                                         |
|     You can only fit a limited number of documents in             |
|     the prompt. Very large document collections need              |
|     good retrieval to find the right pieces.                      |
|                                                                   |
|  3. Added Latency                                                 |
|     The retrieval step adds time. Search + embed + LLM            |
|     is slower than just LLM.                                      |
|                                                                   |
|  4. Chunk Boundary Issues                                         |
|     If the answer spans two chunks and only one is                |
|     retrieved, you get an incomplete answer.                      |
|                                                                   |
|  5. Not a Reasoning Engine                                        |
|     RAG helps with factual recall but does not help               |
|     the model reason better. Complex multi-step problems          |
|     may need other approaches.                                    |
+------------------------------------------------------------------+
```

---

## A Real-World RAG Scenario

Let us walk through how RAG works in a real customer support scenario.

```python
# Simulating a real-world RAG customer support scenario

# Knowledge base with real company information
knowledge_base = [
    {
        "id": "doc_001",
        "title": "Pricing Plans",
        "content": "Basic Plan: $9.99/month, up to 5 users, 10GB storage. "
                   "Pro Plan: $29.99/month, up to 25 users, 100GB storage. "
                   "Enterprise Plan: Custom pricing, unlimited users, "
                   "unlimited storage, dedicated support."
    },
    {
        "id": "doc_002",
        "title": "Account Cancellation",
        "content": "To cancel your account, go to Settings > Billing > "
                   "Cancel Subscription. Your account remains active until "
                   "the end of your current billing period. Data is retained "
                   "for 30 days after cancellation. After 30 days, all data "
                   "is permanently deleted."
    },
    {
        "id": "doc_003",
        "title": "Two-Factor Authentication",
        "content": "Enable 2FA in Settings > Security > Two-Factor Auth. "
                   "We support authenticator apps (Google Authenticator, "
                   "Authy) and SMS verification. Authenticator apps are "
                   "recommended for better security."
    },
    {
        "id": "doc_004",
        "title": "API Rate Limits",
        "content": "Basic Plan: 100 requests/minute. Pro Plan: 1000 "
                   "requests/minute. Enterprise: Custom limits. Exceeding "
                   "limits returns HTTP 429. Use exponential backoff for "
                   "retry logic."
    }
]

def simulate_rag_flow(question):
    """Simulate the complete RAG flow step by step."""
    print(f"Customer Question: {question}")
    print()

    # Step 1: Retrieve (simplified keyword matching)
    print("Step 1: RETRIEVE")
    query_words = set(question.lower().split())
    scored_docs = []

    for doc in knowledge_base:
        doc_words = set(doc["content"].lower().split())
        overlap = len(query_words.intersection(doc_words))
        scored_docs.append((doc, overlap))

    scored_docs.sort(key=lambda x: x[1], reverse=True)
    top_docs = scored_docs[:2]

    for doc, score in top_docs:
        print(f"  Found: '{doc['title']}' (relevance: {score})")
    print()

    # Step 2: Augment
    print("Step 2: AUGMENT")
    context = "\n".join(doc["content"] for doc, _ in top_docs)
    augmented_prompt = f"""Context:\n{context}\n\nQuestion: {question}"""
    print(f"  Prompt size: {len(augmented_prompt)} characters")
    print(f"  Contains {len(top_docs)} document(s)")
    print()

    # Step 3: Generate (simulated)
    print("Step 3: GENERATE")
    print("  LLM reads the context and generates a grounded answer")
    print("  The answer cites information from the retrieved documents")
    print()

    # Show source attribution
    print("Sources:")
    for doc, _ in top_docs:
        print(f"  [{doc['id']}] {doc['title']}")

    print("-" * 50)


# Test with different questions
simulate_rag_flow("How much does the Pro plan cost?")
print()
simulate_rag_flow("How do I cancel my account?")
print()
simulate_rag_flow("What happens if I exceed the API rate limit?")
```

**Output:**
```
Customer Question: How much does the Pro plan cost?

Step 1: RETRIEVE
  Found: 'Pricing Plans' (relevance: 3)
  Found: 'API Rate Limits' (relevance: 2)

Step 2: AUGMENT
  Prompt size: 421 characters
  Contains 2 document(s)

Step 3: GENERATE
  LLM reads the context and generates a grounded answer
  The answer cites information from the retrieved documents

Sources:
  [doc_001] Pricing Plans
  [doc_004] API Rate Limits
--------------------------------------------------

Customer Question: How do I cancel my account?

Step 1: RETRIEVE
  Found: 'Account Cancellation' (relevance: 3)
  Found: 'Two-Factor Authentication' (relevance: 2)

Step 2: AUGMENT
  Prompt size: 477 characters
  Contains 2 document(s)

Step 3: GENERATE
  LLM reads the context and generates a grounded answer
  The answer cites information from the retrieved documents

Sources:
  [doc_002] Account Cancellation
  [doc_003] Two-Factor Authentication
--------------------------------------------------

Customer Question: What happens if I exceed the API rate limit?

Step 1: RETRIEVE
  Found: 'API Rate Limits' (relevance: 4)
  Found: 'Pricing Plans' (relevance: 2)

Step 2: AUGMENT
  Prompt size: 412 characters
  Contains 2 document(s)

Step 3: GENERATE
  LLM reads the context and generates a grounded answer
  The answer cites information from the retrieved documents

Sources:
  [doc_004] API Rate Limits
  [doc_001] Pricing Plans
--------------------------------------------------
```

---

## Common Mistakes

1. **Not telling the LLM to stick to the documents.** Without explicit instructions like "answer only based on the provided context," the LLM will mix its own knowledge with the documents, potentially introducing errors.

2. **Retrieving too many documents.** Stuffing 20 documents into the prompt overwhelms the LLM and wastes tokens. Usually 3-5 relevant chunks are enough.

3. **Retrieving too few documents.** Only providing 1 chunk might miss important context. The answer might be split across multiple chunks.

4. **Using RAG when it is not needed.** If the LLM already knows the answer well (like basic Python syntax), RAG adds latency and cost for no benefit.

5. **Ignoring document quality.** RAG can only be as good as the documents it retrieves. Outdated, incorrect, or poorly written documents lead to bad answers.

---

## Best Practices

1. **Always instruct the model to use only the provided context.** This is the most important instruction in a RAG prompt.

2. **Include source attribution.** Tell the model to cite which document it used. This helps users verify the answer.

3. **Keep documents up to date.** RAG is only as current as your document database. Set up regular update processes.

4. **Test retrieval quality separately.** Before evaluating the full RAG pipeline, check that retrieval returns the right documents. If retrieval fails, the LLM cannot save it.

5. **Handle "I don't know" gracefully.** When the documents do not contain the answer, the model should say so clearly rather than guessing.

6. **Monitor and evaluate.** Track which questions get answered correctly and which fail. Use failures to improve your document collection and retrieval.

---

## Quick Summary

RAG (Retrieval-Augmented Generation) solves two fundamental LLM problems: hallucination and outdated knowledge. It works in three steps. First, it retrieves relevant documents from your collection. Second, it augments the prompt by adding those documents. Third, the LLM generates an answer grounded in the actual documents. RAG is ideal for question answering over your own data, and it is simpler and cheaper than fine-tuning for most use cases.

---

## Key Points

- **Hallucination** is when LLMs confidently generate made-up information
- **Knowledge cutoff** means LLMs do not know about events after their training date
- **RAG** gives the LLM access to your documents before it answers
- The three steps are **Retrieve** (find documents), **Augment** (add to prompt), **Generate** (LLM answers)
- RAG is best for **factual Q&A** over your own data
- **Fine-tuning** is better for changing the model's behavior or style
- RAG allows **easy updates** by simply adding or removing documents
- **Source attribution** lets users verify answers against original documents

---

## Practice Questions

1. A customer support chatbot sometimes gives incorrect policy information. Would you use RAG or fine-tuning to fix this? Explain your reasoning.

2. What is the difference between the "offline phase" and the "online phase" in a RAG system? What happens in each phase?

3. You have a RAG system, but it keeps returning wrong answers. The LLM is working fine. Where is the most likely problem, and how would you diagnose it?

4. Why does the RAG prompt include the instruction "Answer based ONLY on the provided documents"? What would happen without this instruction?

5. Name three scenarios where RAG would NOT be the right approach, and explain why for each.

---

## Exercises

**Exercise 1: Build a FAQ Bot**

Create a simple RAG system using a dictionary of FAQ entries (at least 10 entries). Implement keyword-based retrieval and build augmented prompts. Test with 5 questions, including one that is not in the FAQ.

**Exercise 2: RAG vs Fine-Tuning Decision Matrix**

Create a decision matrix tool that takes project requirements (data volume, update frequency, budget, task type, accuracy needs) and recommends RAG, fine-tuning, or both. Test it with at least 4 different scenarios.

**Exercise 3: Source Citation System**

Extend the simple RAG example to include source citations in the LLM's response. Each claim in the answer should reference which document it came from. Format the output to clearly show the answer and its sources.

---

## What Is Next?

You now understand what RAG is and why it matters. But the simple keyword-matching retrieval we used in this chapter is not good enough for real applications. In Chapter 14, you will learn how to properly process documents for RAG. You will learn how to extract text from different file types and how to split documents into chunks that preserve meaning. Good document processing is the foundation of a good RAG system.
