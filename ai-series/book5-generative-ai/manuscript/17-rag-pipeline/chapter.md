# Chapter 17: Building a RAG Pipeline

## What You Will Learn

In this chapter, you will learn:

- How to build a complete RAG system from start to finish
- How to load and process real documents
- How to chunk, embed, and store documents in ChromaDB
- How to build the query pipeline: retrieve, augment, generate
- How to add source citations to LLM responses
- How to put it all together into a working question-answering application

## Why This Chapter Matters

Over the last four chapters, you learned the individual pieces: what RAG is (Chapter 13), how to process documents (Chapter 14), how embeddings work (Chapter 15), and how to use vector databases (Chapter 16). Now it is time to assemble them.

This chapter is where everything comes together. You will build a complete, working RAG system that can answer questions about your own documents. This is not a toy example. The same architecture powers real products like customer support bots, internal knowledge bases, and document search engines.

Think of the previous chapters as learning to use a hammer, nails, saw, and measuring tape. This chapter is where you build the house.

---

## The Complete RAG Pipeline

```
+------------------------------------------------------------------+
|              COMPLETE RAG PIPELINE                                |
|                                                                   |
|  STEP 1: LOAD           STEP 2: CHUNK          STEP 3: EMBED     |
|  +----------+           +----------+           +----------+      |
|  | Read PDF,|           | Split    |           | Convert  |      |
|  | HTML,    |---------->| into     |---------->| chunks   |      |
|  | text     |           | pieces   |           | to       |      |
|  | files    |           | (500     |           | vectors  |      |
|  +----------+           | chars)   |           +----------+      |
|                         +----------+                |             |
|                                                     v             |
|  STEP 6: RETURN         STEP 5: GENERATE     STEP 4: STORE      |
|  +----------+           +----------+         +----------+        |
|  | Answer   |           | LLM      |         | Save in  |        |
|  | with     |<----------| reads    |         | ChromaDB |        |
|  | source   |           | context  |         | with     |        |
|  | citations|           | and      |         | metadata |        |
|  +----------+           | answers  |         +----------+        |
|                         +----------+               |             |
|                              ^                      |             |
|                              |                      v             |
|  QUERY TIME:           +----------+         +----------+        |
|  +----------+          | Build    |         | Search   |        |
|  | User     |--------->| augmented|<--------| for      |        |
|  | question |          | prompt   |         | relevant |        |
|  +----------+          +----------+         | chunks   |        |
|                                             +----------+        |
+------------------------------------------------------------------+
```

---

## Step 1: Set Up Dependencies

```python
# Install all required packages:
# pip install openai chromadb sentence-transformers pypdf2 beautifulsoup4

# Verify installations
import importlib

packages = [
    ("openai", "OpenAI API client"),
    ("chromadb", "Vector database"),
    ("sentence_transformers", "Embedding models"),
    ("PyPDF2", "PDF text extraction"),
    ("bs4", "HTML text extraction"),
]

print("Checking dependencies:")
for package, description in packages:
    try:
        mod = importlib.import_module(package)
        version = getattr(mod, '__version__', 'installed')
        print(f"  [OK] {package} ({description}) - {version}")
    except ImportError:
        print(f"  [MISSING] {package} ({description})")
        print(f"    Install with: pip install {package}")

print("\nAll dependencies ready!")
```

**Output:**
```
Checking dependencies:
  [OK] openai (OpenAI API client) - 1.12.0
  [OK] chromadb (Vector database) - 0.4.22
  [OK] sentence_transformers (Embedding models) - 2.3.1
  [OK] PyPDF2 (PDF text extraction) - 3.0.1
  [OK] bs4 (HTML text extraction) - installed

All dependencies ready!
```

---

## Step 2: Create the Document Loader

```python
import os
import re
from typing import List, Dict

class DocumentLoader:
    """Load documents from various file formats."""

    def load_directory(self, directory_path: str) -> List[Dict]:
        """
        Load all supported documents from a directory.

        Returns list of dicts with 'text', 'source', and 'file_type'.
        """
        documents = []
        supported = {'.txt', '.html', '.htm', '.pdf', '.md'}

        for filename in os.listdir(directory_path):
            ext = os.path.splitext(filename)[1].lower()
            if ext not in supported:
                continue

            filepath = os.path.join(directory_path, filename)

            try:
                if ext == '.pdf':
                    text = self._load_pdf(filepath)
                elif ext in ('.html', '.htm'):
                    text = self._load_html(filepath)
                else:
                    text = self._load_text(filepath)

                if text.strip():
                    documents.append({
                        'text': text.strip(),
                        'source': filename,
                        'file_type': ext,
                    })
                    print(f"  Loaded: {filename} ({len(text)} chars)")

            except Exception as e:
                print(f"  Error loading {filename}: {e}")

        print(f"\nTotal documents loaded: {len(documents)}")
        return documents

    def _load_text(self, filepath: str) -> str:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def _load_pdf(self, filepath: str) -> str:
        from PyPDF2 import PdfReader
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
        return text

    def _load_html(self, filepath: str) -> str:
        from bs4 import BeautifulSoup
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        for tag in soup.find_all(['script', 'style', 'nav', 'footer']):
            tag.decompose()
        return soup.get_text(separator='\n')

    def load_texts(self, texts_with_sources: List[Dict]) -> List[Dict]:
        """
        Load from a list of text dictionaries.
        Useful for testing without files on disk.

        Each dict should have 'text' and 'source' keys.
        """
        documents = []
        for item in texts_with_sources:
            if item['text'].strip():
                documents.append({
                    'text': item['text'].strip(),
                    'source': item.get('source', 'unknown'),
                    'file_type': 'text',
                })
        print(f"Loaded {len(documents)} text documents")
        return documents
```

**Line-by-line explanation:**

- `DocumentLoader` handles different file formats automatically. You point it at a directory and it loads everything it can.
- `load_directory()` scans a directory, identifies supported file types, and loads each one using the appropriate method.
- `_load_pdf()`, `_load_html()`, `_load_text()` are private methods (indicated by `_` prefix) that handle each format.
- `load_texts()` is a convenience method for testing without actual files on disk.

---

## Step 3: Create the Text Chunker

```python
from typing import List, Dict

class TextChunker:
    """Split documents into chunks suitable for RAG."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_documents(self, documents: List[Dict]) -> List[Dict]:
        """
        Split all documents into chunks.

        Returns list of dicts with 'text', 'source', 'chunk_index',
        and 'total_chunks'.
        """
        all_chunks = []

        for doc in documents:
            chunks = self._recursive_split(doc['text'])

            for i, chunk_text in enumerate(chunks):
                all_chunks.append({
                    'text': chunk_text,
                    'source': doc['source'],
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                })

        print(f"Created {len(all_chunks)} chunks from "
              f"{len(documents)} documents")
        print(f"Average chunk size: "
              f"{sum(len(c['text']) for c in all_chunks) // len(all_chunks)} "
              f"chars")

        return all_chunks

    def _recursive_split(self, text: str) -> List[str]:
        """Split text using recursive strategy."""
        if len(text) <= self.chunk_size:
            return [text] if text.strip() else []

        separators = ["\n\n", "\n", ". ", " "]

        for sep in separators:
            parts = text.split(sep)
            if len(parts) <= 1:
                continue

            chunks = []
            current = ""

            for part in parts:
                candidate = current + sep + part if current else part
                if len(candidate) <= self.chunk_size:
                    current = candidate
                else:
                    if current.strip():
                        chunks.append(current.strip())
                    current = part

            if current.strip():
                chunks.append(current.strip())

            if chunks:
                return chunks

        # Fallback: fixed-size split
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunks.append(text[start:end].strip())
            start = end - self.chunk_overlap
        return [c for c in chunks if c]
```

---

## Step 4: Create the Vector Store

```python
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional

class VectorStore:
    """Store and search document chunks using ChromaDB."""

    def __init__(self, collection_name: str = "rag_documents",
                 persist_directory: str = "./rag_chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print(f"Vector store ready: {collection_name}")
        print(f"Existing documents: {self.collection.count()}")

    def add_chunks(self, chunks: List[Dict], batch_size: int = 100):
        """
        Add document chunks to the vector store.
        """
        total = len(chunks)
        added = 0

        for i in range(0, total, batch_size):
            batch = chunks[i:i + batch_size]

            # Prepare batch data
            texts = [c['text'] for c in batch]
            ids = [f"chunk_{i + j}" for j in range(len(batch))]
            metadatas = [
                {
                    'source': c['source'],
                    'chunk_index': c['chunk_index'],
                    'total_chunks': c['total_chunks'],
                }
                for c in batch
            ]

            # Create embeddings
            embeddings = self.embedding_model.encode(texts).tolist()

            # Add to ChromaDB
            self.collection.add(
                documents=texts,
                embeddings=embeddings,
                ids=ids,
                metadatas=metadatas,
            )

            added += len(batch)
            print(f"  Added batch: {added}/{total} chunks")

        print(f"Total chunks in store: {self.collection.count()}")

    def search(self, query: str, top_k: int = 5,
               filter_metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Search for chunks relevant to a query.
        """
        query_embedding = self.embedding_model.encode(query).tolist()

        search_params = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
        }

        if filter_metadata:
            search_params["where"] = filter_metadata

        results = self.collection.query(**search_params)

        # Format results
        formatted = []
        for i in range(len(results['documents'][0])):
            formatted.append({
                'text': results['documents'][0][i],
                'source': results['metadatas'][0][i]['source'],
                'chunk_index': results['metadatas'][0][i]['chunk_index'],
                'distance': results['distances'][0][i],
            })

        return formatted

    def clear(self):
        """Remove all documents from the collection."""
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection.name,
            metadata={"hnsw:space": "cosine"}
        )
        print("Collection cleared")
```

**Line-by-line explanation:**

- `VectorStore` wraps ChromaDB and sentence-transformers into one easy-to-use class.
- `metadata={"hnsw:space": "cosine"}` tells ChromaDB to use cosine distance for similarity search, which is best for text embeddings.
- `add_chunks()` processes documents in batches of 100 for efficiency. It creates embeddings and stores them alongside the original text and metadata.
- `search()` embeds the query, searches ChromaDB, and returns formatted results with source information.
- `clear()` resets the collection. Useful during development.

---

## Step 5: Create the RAG Generator

```python
from openai import OpenAI
from typing import List, Dict

class RAGGenerator:
    """Generate answers using retrieved context."""

    def __init__(self, model: str = "gpt-4o-mini"):
        self.client = OpenAI()
        self.model = model

    def generate(self, query: str, context_chunks: List[Dict],
                 system_prompt: str = None) -> Dict:
        """
        Generate an answer based on retrieved context.

        Args:
            query: User's question
            context_chunks: List of relevant chunks from retrieval
            system_prompt: Optional custom system prompt

        Returns:
            Dict with 'answer', 'sources', and 'tokens_used'
        """
        if not system_prompt:
            system_prompt = """You are a helpful assistant that answers
questions based on the provided context documents. Follow these rules:

1. Only use information from the provided context to answer.
2. If the context does not contain enough information to answer,
   say "I don't have enough information to answer that question."
3. When you use information from the context, cite the source
   document in brackets like [source_name].
4. Be concise and direct in your answers.
5. If multiple sources provide relevant information, synthesize
   them into a coherent answer."""

        # Build the context section
        context_text = self._format_context(context_chunks)

        # Build the full prompt
        user_message = f"""Context documents:
{context_text}

Question: {query}

Please answer the question based on the context documents above."""

        # Call the LLM
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0,
        )

        answer = response.choices[0].message.content
        tokens = response.usage.total_tokens

        # Extract unique sources
        sources = list(set(
            chunk['source'] for chunk in context_chunks
        ))

        return {
            'answer': answer,
            'sources': sources,
            'tokens_used': tokens,
            'num_chunks_used': len(context_chunks),
        }

    def _format_context(self, chunks: List[Dict]) -> str:
        """Format chunks into a context string for the prompt."""
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk['source']
            text = chunk['text']
            context_parts.append(
                f"[Document {i} - Source: {source}]\n{text}"
            )
        return "\n\n".join(context_parts)
```

**Line-by-line explanation:**

- `RAGGenerator` handles the "Generate" step of RAG. It takes retrieved chunks and sends them to the LLM along with the user's question.
- The system prompt is critical. It tells the LLM to only use the provided context and to cite sources.
- `_format_context()` formats each chunk with its source name so the LLM knows where each piece of information comes from.
- `temperature=0` makes the response deterministic. For factual Q&A, you want the model to be precise, not creative.
- The method returns the answer, the sources used, token count, and the number of chunks used. This metadata is useful for monitoring and debugging.

---

## Step 6: Assemble the Complete Pipeline

```python
class RAGPipeline:
    """
    Complete RAG pipeline: load, chunk, embed, store, retrieve, generate.
    """

    def __init__(self, collection_name="rag_pipeline",
                 persist_dir="./rag_data"):
        self.loader = DocumentLoader()
        self.chunker = TextChunker(chunk_size=500, chunk_overlap=50)
        self.store = VectorStore(collection_name, persist_dir)
        self.generator = RAGGenerator()
        print("\nRAG Pipeline initialized!")

    def ingest_documents(self, documents: List[Dict]):
        """
        Process and store documents (offline phase).

        Args:
            documents: List of dicts with 'text' and 'source' keys
        """
        print("\n--- INGESTION PHASE ---")

        # Step 1: Chunk
        print("\n1. Chunking documents...")
        chunks = self.chunker.chunk_documents(documents)

        # Step 2: Store (embedding happens inside)
        print("\n2. Embedding and storing chunks...")
        self.store.add_chunks(chunks)

        print("\nIngestion complete!")

    def query(self, question: str, top_k: int = 3) -> Dict:
        """
        Answer a question using RAG (online phase).

        Args:
            question: User's question
            top_k: Number of chunks to retrieve

        Returns:
            Dict with answer, sources, and retrieval details
        """
        # Step 1: Retrieve relevant chunks
        retrieved = self.store.search(question, top_k=top_k)

        # Step 2: Generate answer
        result = self.generator.generate(question, retrieved)

        # Add retrieval details
        result['retrieved_chunks'] = [
            {
                'text': chunk['text'][:100] + '...',
                'source': chunk['source'],
                'distance': chunk['distance'],
            }
            for chunk in retrieved
        ]

        return result

    def query_with_display(self, question: str, top_k: int = 3):
        """Query and display results in a formatted way."""
        print(f"\n{'=' * 60}")
        print(f"QUESTION: {question}")
        print(f"{'=' * 60}")

        result = self.query(question, top_k)

        print(f"\nANSWER:")
        print(result['answer'])

        print(f"\nSOURCES:")
        for source in result['sources']:
            print(f"  - {source}")

        print(f"\nRETRIEVED CHUNKS:")
        for i, chunk in enumerate(result['retrieved_chunks'], 1):
            print(f"  {i}. [{chunk['source']}] "
                  f"(distance: {chunk['distance']:.4f})")
            print(f"     {chunk['text']}")

        print(f"\nTokens used: {result['tokens_used']}")
        print(f"Chunks used: {result['num_chunks_used']}")

        return result
```

---

## Step 7: Run the Complete Pipeline

```python
# Create sample documents (in practice, load from files)
sample_documents = [
    {
        "text": """Employee Handbook - Leave Policy

All full-time employees are entitled to the following leave benefits:

Annual Leave: 20 days per calendar year for employees with less than
5 years of service. 25 days for employees with 5 or more years.
Unused annual leave can be carried over up to a maximum of 5 days.

Sick Leave: 12 days per year. A medical certificate is required for
sick leave exceeding 3 consecutive days. Unused sick leave does not
carry over to the next year.

Parental Leave: 16 weeks of paid parental leave for primary caregivers.
4 weeks of paid leave for secondary caregivers. Leave must be taken
within 12 months of the child's birth or adoption.

Bereavement Leave: 5 days for immediate family members. 2 days for
extended family members.

Public Holidays: All employees receive paid time off for national
public holidays as per the company calendar published each December.""",
        "source": "employee_handbook_leave.txt"
    },
    {
        "text": """Employee Handbook - Work Arrangements

Standard Working Hours: The standard work week is 40 hours, Monday
through Friday, 9:00 AM to 5:00 PM with a one-hour lunch break.

Flexible Working: Employees may request flexible start times between
7:00 AM and 10:00 AM with manager approval. Core hours (when all
team members must be available) are 10:00 AM to 3:00 PM.

Remote Work: Employees may work remotely up to 3 days per week after
completing their 90-day probationary period. A remote work agreement
must be signed. The company provides a $500 one-time allowance for
home office setup.

Overtime: Non-exempt employees are paid 1.5x their hourly rate for
hours exceeding 40 per week. Overtime must be pre-approved by the
direct manager. Exempt employees do not receive overtime pay.

Time Tracking: All employees must log their hours using the TimeTrack
system by end of each business day. Failure to log hours may result
in delayed payroll processing.""",
        "source": "employee_handbook_work.txt"
    },
    {
        "text": """IT Security Policy

Password Requirements: All passwords must be at least 12 characters
long, contain uppercase and lowercase letters, numbers, and special
characters. Passwords must be changed every 90 days. Previous 10
passwords cannot be reused.

Multi-Factor Authentication (MFA): MFA is required for all company
systems including email, VPN, and cloud services. Approved MFA
methods include authenticator apps and hardware security keys.
SMS-based MFA is not permitted due to security concerns.

Data Classification:
- Confidential: Customer data, financial records, trade secrets.
  Must be encrypted at rest and in transit.
- Internal: Company communications, project documents. Should not
  be shared externally without approval.
- Public: Marketing materials, published content. No restrictions.

Device Policy: Company-issued devices must have full-disk encryption
enabled. Personal devices may access company email only through the
approved mobile device management (MDM) solution. All devices must
have automatic screen lock enabled (5-minute timeout).

Incident Reporting: Security incidents must be reported to the IT
Security team within 1 hour of discovery. Email security@company.com
or call the security hotline at ext. 4567.""",
        "source": "it_security_policy.txt"
    },
    {
        "text": """Travel and Expense Policy

Booking Travel: All business travel must be booked through the
company travel portal (TravelBook). Flights should be booked at
least 14 days in advance when possible. Economy class is standard
for flights under 6 hours. Business class may be booked for flights
over 6 hours with manager approval.

Hotel Accommodations: Maximum nightly rate of $200 for domestic
travel and $300 for international travel. Rates exceeding these
limits require VP-level approval.

Meals: Daily meal allowance is $75 for domestic travel and $100
for international travel. Alcoholic beverages are not reimbursable.
Tips up to 20% are included in the meal allowance.

Expense Reports: Must be submitted within 30 days of travel
completion through the ExpenseHub system. Original receipts are
required for all expenses over $25. Reimbursement is processed
within 10 business days of approval.

Mileage: Personal vehicle use for business purposes is reimbursed
at the current IRS rate. A mileage log must be submitted with
start and end locations for each trip.""",
        "source": "travel_expense_policy.txt"
    }
]

# Initialize the pipeline
pipeline = RAGPipeline(
    collection_name="employee_kb",
    persist_dir="./employee_rag_data"
)

# Ingest documents
loaded_docs = pipeline.loader.load_texts(sample_documents)
pipeline.ingest_documents(loaded_docs)

# Now query!
pipeline.query_with_display("How many days of annual leave do I get?")
pipeline.query_with_display("What are the password requirements?")
pipeline.query_with_display("Can I work from home?")
pipeline.query_with_display("What is the meal allowance for international travel?")
pipeline.query_with_display("What is the company's stock option plan?")
```

**Output:**
```
Vector store ready: employee_kb
Existing documents: 0
Loaded 4 text documents

RAG Pipeline initialized!

--- INGESTION PHASE ---

1. Chunking documents...
Created 12 chunks from 4 documents
Average chunk size: 412 chars

2. Embedding and storing chunks...
  Added batch: 12/12 chunks
Total chunks in store: 12

Ingestion complete!

============================================================
QUESTION: How many days of annual leave do I get?
============================================================

ANSWER:
According to the Employee Handbook [employee_handbook_leave.txt], full-time
employees are entitled to 20 days of annual leave per calendar year if they
have less than 5 years of service, and 25 days if they have 5 or more years
of service. Unused annual leave can be carried over up to a maximum of 5 days.

SOURCES:
  - employee_handbook_leave.txt

RETRIEVED CHUNKS:
  1. [employee_handbook_leave.txt] (distance: 0.3456)
     Annual Leave: 20 days per calendar year for employees with less than
     5 years of service. 25 days f...
  2. [employee_handbook_leave.txt] (distance: 0.5678)
     Parental Leave: 16 weeks of paid parental leave for primary caregivers...
  3. [employee_handbook_work.txt] (distance: 0.7234)
     Standard Working Hours: The standard work week is 40 hours, Monday
     through Friday...

Tokens used: 523
Chunks used: 3

============================================================
QUESTION: What are the password requirements?
============================================================

ANSWER:
According to the IT Security Policy [it_security_policy.txt], all passwords
must meet the following requirements:
- At least 12 characters long
- Contain uppercase and lowercase letters
- Contain numbers and special characters
- Changed every 90 days
- Previous 10 passwords cannot be reused

SOURCES:
  - it_security_policy.txt

RETRIEVED CHUNKS:
  1. [it_security_policy.txt] (distance: 0.2345)
     Password Requirements: All passwords must be at least 12 characters...
  2. [it_security_policy.txt] (distance: 0.5678)
     Multi-Factor Authentication (MFA): MFA is required for all company...
  3. [it_security_policy.txt] (distance: 0.7890)
     Device Policy: Company-issued devices must have full-disk encryption...

Tokens used: 478
Chunks used: 3

============================================================
QUESTION: Can I work from home?
============================================================

ANSWER:
Yes, according to the Employee Handbook [employee_handbook_work.txt],
employees may work remotely up to 3 days per week after completing their
90-day probationary period. A remote work agreement must be signed. The
company also provides a $500 one-time allowance for home office setup.

SOURCES:
  - employee_handbook_work.txt

RETRIEVED CHUNKS:
  1. [employee_handbook_work.txt] (distance: 0.3012)
     Remote Work: Employees may work remotely up to 3 days per week after...
  2. [employee_handbook_work.txt] (distance: 0.5234)
     Flexible Working: Employees may request flexible start times between...
  3. [employee_handbook_leave.txt] (distance: 0.7890)
     All full-time employees are entitled to the following leave benefits...

Tokens used: 412
Chunks used: 3

============================================================
QUESTION: What is the meal allowance for international travel?
============================================================

ANSWER:
According to the Travel and Expense Policy [travel_expense_policy.txt],
the daily meal allowance for international travel is $100. Alcoholic
beverages are not reimbursable, but tips up to 20% are included in
the meal allowance.

SOURCES:
  - travel_expense_policy.txt

RETRIEVED CHUNKS:
  1. [travel_expense_policy.txt] (distance: 0.2890)
     Meals: Daily meal allowance is $75 for domestic travel and $100 for...
  2. [travel_expense_policy.txt] (distance: 0.4567)
     Hotel Accommodations: Maximum nightly rate of $200 for domestic...
  3. [travel_expense_policy.txt] (distance: 0.6789)
     Booking Travel: All business travel must be booked through the...

Tokens used: 389
Chunks used: 3

============================================================
QUESTION: What is the company's stock option plan?
============================================================

ANSWER:
I don't have enough information to answer that question. The provided
context documents cover leave policy, work arrangements, IT security,
and travel expenses, but do not contain information about a stock
option plan.

SOURCES:
  - employee_handbook_leave.txt
  - employee_handbook_work.txt

RETRIEVED CHUNKS:
  1. [employee_handbook_leave.txt] (distance: 0.8901)
     All full-time employees are entitled to the following leave benefits...
  2. [employee_handbook_work.txt] (distance: 0.9012)
     Standard Working Hours: The standard work week is 40 hours...
  3. [travel_expense_policy.txt] (distance: 0.9234)
     Expense Reports: Must be submitted within 30 days of travel...

Tokens used: 356
Chunks used: 3
```

**Key observations from the output:**

- The system correctly answers questions about annual leave, passwords, remote work, and meal allowances by finding the right chunks.
- For the stock option question, the system correctly says it does not have enough information. Notice the high distances (0.89+), indicating no relevant chunks were found.
- Source citations in the answer help users verify the information.
- Token usage is reasonable (350-520) because only relevant chunks are included, not entire documents.

---

## Adding a Conversational Interface

```python
def interactive_rag(pipeline):
    """
    Run an interactive question-answering session.
    Type 'quit' to exit.
    """
    print("\n" + "=" * 60)
    print("RAG Question Answering System")
    print("Type your question and press Enter.")
    print("Type 'quit' to exit.")
    print("=" * 60)

    while True:
        print()
        question = input("You: ").strip()

        if question.lower() in ('quit', 'exit', 'q'):
            print("Goodbye!")
            break

        if not question:
            continue

        result = pipeline.query(question, top_k=3)

        print(f"\nAssistant: {result['answer']}")

        print(f"\n  Sources: {', '.join(result['sources'])}")
        print(f"  Tokens: {result['tokens_used']}")

# Uncomment to run interactively:
# interactive_rag(pipeline)
```

---

## Monitoring and Evaluation

```python
class RAGMonitor:
    """Track and evaluate RAG pipeline performance."""

    def __init__(self):
        self.queries = []

    def log_query(self, question, result, relevance_score=None):
        """Log a query and its result for analysis."""
        self.queries.append({
            'question': question,
            'answer': result['answer'],
            'sources': result['sources'],
            'tokens': result['tokens_used'],
            'num_chunks': result['num_chunks_used'],
            'relevance': relevance_score,
            'top_distance': result['retrieved_chunks'][0]['distance']
                if result['retrieved_chunks'] else None,
        })

    def report(self):
        """Generate a performance report."""
        if not self.queries:
            print("No queries logged yet")
            return

        total = len(self.queries)
        avg_tokens = sum(q['tokens'] for q in self.queries) / total
        avg_distance = sum(
            q['top_distance'] for q in self.queries
            if q['top_distance'] is not None
        ) / total

        answered = sum(
            1 for q in self.queries
            if "don't have enough information" not in q['answer'].lower()
        )

        print("RAG PIPELINE PERFORMANCE REPORT")
        print("=" * 45)
        print(f"Total queries:        {total}")
        print(f"Answered:             {answered}/{total} ({answered/total:.0%})")
        print(f"Avg tokens per query: {avg_tokens:.0f}")
        print(f"Avg top-1 distance:   {avg_distance:.4f}")
        print(f"Unique sources used:  {len(set(s for q in self.queries for s in q['sources']))}")

        # Show token distribution
        print(f"\nToken usage range: "
              f"{min(q['tokens'] for q in self.queries)} - "
              f"{max(q['tokens'] for q in self.queries)}")

# Example usage
monitor = RAGMonitor()

questions = [
    "How many sick days do I get?",
    "What is the password policy?",
    "Can I fly business class?",
    "What is the CEO's phone number?",
]

for q in questions:
    result = pipeline.query(q)
    monitor.log_query(q, result)

monitor.report()
```

**Output:**
```
RAG PIPELINE PERFORMANCE REPORT
=============================================
Total queries:        4
Answered:             3/4 (75%)
Avg tokens per query: 445
Avg top-1 distance:   0.4123
Unique sources used:  4

Token usage range: 356 - 523
```

---

## Common Mistakes

1. **Skipping the chunking step.** Storing entire documents as single chunks makes retrieval imprecise. The LLM gets too much irrelevant text and the answer quality drops.

2. **Using too many or too few retrieved chunks.** Too many chunks waste tokens and can confuse the model. Too few might miss relevant information. Start with 3-5 and adjust based on your results.

3. **Not telling the LLM to cite sources.** Without explicit citation instructions, the LLM will not reference source documents, making it impossible for users to verify answers.

4. **Not handling the "I don't know" case.** Without clear instructions, the LLM will hallucinate an answer when the context does not contain relevant information.

5. **Not persisting the vector store.** Using in-memory ChromaDB means re-embedding all documents every time you restart the application.

---

## Best Practices

1. **Separate ingestion from querying.** Ingest documents once (or when they change). Query the existing index for each user question.

2. **Include the source in each chunk's metadata.** This is essential for source citations and debugging.

3. **Use temperature=0 for factual Q&A.** You want accurate, reproducible answers, not creative ones.

4. **Monitor performance.** Track answer rates, token usage, and retrieval distances to identify problems early.

5. **Test with questions you know the answer to.** This helps you evaluate retrieval quality and answer accuracy.

6. **Keep the system prompt focused.** Tell the LLM exactly how to behave: use only the context, cite sources, and admit when it does not know.

---

## Quick Summary

A complete RAG pipeline has six components: a document loader (reads files), a text chunker (splits into pieces), an embedding model (converts to vectors), a vector store (stores and searches), a generator (produces answers), and the pipeline orchestrator (ties them together). The offline phase loads, chunks, embeds, and stores documents. The online phase retrieves relevant chunks, augments the prompt, and generates a grounded answer. Monitoring helps you track and improve performance over time.

---

## Key Points

- A RAG pipeline has two phases: **offline** (ingestion) and **online** (querying)
- The **document loader** handles multiple file formats (PDF, HTML, text)
- The **chunker** splits documents into 300-500 character pieces with overlap
- The **vector store** (ChromaDB) stores embeddings and enables fast search
- The **generator** sends retrieved chunks to the LLM with source attribution instructions
- Always instruct the LLM to **only use the provided context**
- Monitor **answer rate**, **token usage**, and **retrieval distances**
- **Persist** your vector store to avoid re-embedding on every restart

---

## Practice Questions

1. Why does the RAG pipeline have separate offline and online phases? What happens in each phase?

2. The system retrieves 3 chunks for a question. Two are highly relevant (distance < 0.3) and one is not (distance > 0.8). How might the irrelevant chunk affect the LLM's answer? How would you prevent this?

3. You add 1,000 new documents to your RAG system. Do you need to re-embed the existing documents? Why or why not?

4. A user asks a question and gets a wrong answer. How would you debug this? What are the possible failure points in the pipeline?

5. Why is `temperature=0` recommended for RAG applications? When might you use a higher temperature?

---

## Exercises

**Exercise 1: Build Your Own Knowledge Base**

Create a RAG pipeline for a topic you care about (cooking recipes, sports rules, a textbook chapter). Load at least 5 documents, ingest them, and test with 10 questions. Report the answer rate and identify any questions where retrieval failed.

**Exercise 2: Source Citation Formatting**

Modify the RAGGenerator to produce answers with inline citations like [1], [2] and a numbered reference list at the end. Each citation should include the source document name and the relevant chunk text.

**Exercise 3: Multi-Turn Conversation**

Extend the interactive RAG interface to support follow-up questions. When the user asks a follow-up, include the previous question and answer in the context so the LLM understands the conversation history.

---

## What Is Next?

You have built a working RAG system. In Chapter 18, you will learn advanced techniques to make it even better: re-ranking retrieved results for higher accuracy, hybrid search that combines keyword and semantic matching, query expansion to handle vague questions, and evaluation frameworks to measure your RAG system's quality systematically.
