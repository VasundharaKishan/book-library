# Chapter 28: Project -- Build a RAG Chatbot

## What You Will Learn

In this chapter, you will learn:

- How to build a complete, deployable RAG chatbot from scratch
- How to load and process PDF documents for use with an LLM
- How to chunk documents and create embeddings
- How to store and search embeddings using ChromaDB
- How to build an interactive chat interface with Gradio
- How to add conversation memory so the chatbot remembers context
- How to include source citations so users can verify answers
- How to deploy the chatbot for others to use

## Why This Chapter Matters

This is the final chapter of Book 5, and it brings together nearly everything you have learned. You have studied LLMs, prompt engineering, RAG, embeddings, vector databases, and agents. Now you will combine all of these concepts into a single, practical application.

The chatbot you build in this chapter is not a toy. It is the same architecture used by companies to build customer support bots, internal knowledge assistants, and document Q&A systems. By the end of this chapter, you will have a working application that you can customize for your own documents and share with others.

Think of this project as your graduation exercise. You are building something real.

---

## 28.1 Project Overview

### What We Are Building

```
+---------------------------------------------------------------+
|              RAG CHATBOT ARCHITECTURE                         |
+---------------------------------------------------------------+
|                                                               |
|  1. DOCUMENT LOADING                                          |
|     PDF files --> Extract text                                |
|                                                               |
|  2. CHUNKING                                                  |
|     Long text --> Split into smaller pieces                   |
|                                                               |
|  3. EMBEDDING                                                 |
|     Text chunks --> Numerical vectors                         |
|                                                               |
|  4. VECTOR STORE                                              |
|     Vectors --> Store in ChromaDB                             |
|                                                               |
|  5. RETRIEVAL                                                 |
|     User question --> Find relevant chunks                    |
|                                                               |
|  6. GENERATION                                                |
|     Question + relevant chunks --> LLM --> Answer             |
|                                                               |
|  7. CHAT INTERFACE                                            |
|     Gradio web app with conversation history                  |
|                                                               |
|  User asks question                                           |
|    --> Find relevant document chunks                          |
|      --> Send question + chunks to LLM                        |
|        --> LLM generates answer with citations                |
|          --> Display in chat interface                         |
|                                                               |
+---------------------------------------------------------------+
```

### Required Libraries

```python
# Install all required libraries
# pip install langchain langchain-openai langchain-community
# pip install chromadb          # Vector database
# pip install gradio            # Chat interface
# pip install pypdf             # PDF loading
# pip install sentence-transformers  # Local embeddings (optional)

# You also need an API key for the LLM:
# export OPENAI_API_KEY="your-key-here"
```

### Project Structure

```
+---------------------------------------------------------------+
|              PROJECT FILE STRUCTURE                           |
+---------------------------------------------------------------+
|                                                               |
|  rag-chatbot/                                                 |
|  +-- documents/            # Put your PDF files here          |
|  |   +-- doc1.pdf                                             |
|  |   +-- doc2.pdf                                             |
|  +-- chroma_db/            # Vector database storage          |
|  +-- rag_chatbot.py        # Main application                 |
|  +-- requirements.txt      # Python dependencies              |
|                                                               |
+---------------------------------------------------------------+
```

---

## 28.2 Step 1: Loading PDF Documents

### Reading PDFs with PyPDF

```python
from langchain_community.document_loaders import PyPDFLoader
import os

def load_pdf(file_path):
    """
    Load a single PDF file and return its pages as documents.

    Args:
        file_path: Path to the PDF file

    Returns:
        List of document objects, one per page
    """
    loader = PyPDFLoader(file_path)
    pages = loader.load()

    print(f"Loaded: {file_path}")
    print(f"  Pages: {len(pages)}")
    if pages:
        print(f"  First page preview: {pages[0].page_content[:100]}...")
        print(f"  Metadata: {pages[0].metadata}")

    return pages


def load_all_pdfs(directory):
    """
    Load all PDF files from a directory.

    Args:
        directory: Path to the directory containing PDFs

    Returns:
        List of all document objects from all PDFs
    """
    all_documents = []

    # Find all PDF files
    pdf_files = [f for f in os.listdir(directory) if f.endswith('.pdf')]

    if not pdf_files:
        print(f"No PDF files found in {directory}")
        return all_documents

    print(f"Found {len(pdf_files)} PDF files in {directory}\n")

    for pdf_file in sorted(pdf_files):
        file_path = os.path.join(directory, pdf_file)
        pages = load_pdf(file_path)
        all_documents.extend(pages)
        print()

    print(f"Total documents loaded: {len(all_documents)}")
    return all_documents


# Example usage (simulated since we may not have PDFs)
print("=== PDF Loading ===\n")
print("To load PDFs, place them in the 'documents/' folder and run:")
print("  documents = load_all_pdfs('documents/')")
print()

# Simulate loaded documents for the rest of the chapter
class SimulatedDocument:
    def __init__(self, content, metadata):
        self.page_content = content
        self.metadata = metadata

sample_documents = [
    SimulatedDocument(
        "Machine learning is a subset of artificial intelligence that enables systems to learn from data. "
        "Unlike traditional programming where rules are explicitly coded, ML algorithms discover patterns "
        "in data and use them to make predictions or decisions. Common types include supervised learning, "
        "unsupervised learning, and reinforcement learning.",
        {"source": "ai_guide.pdf", "page": 1}
    ),
    SimulatedDocument(
        "Neural networks are computing systems inspired by biological neural networks in the brain. "
        "They consist of layers of interconnected nodes called neurons. Each connection has a weight "
        "that is adjusted during training. Deep learning uses neural networks with many layers, "
        "enabling them to learn complex patterns in data like images, text, and speech.",
        {"source": "ai_guide.pdf", "page": 2}
    ),
    SimulatedDocument(
        "Transfer learning is a technique where a model trained on one task is reused for a different "
        "but related task. Instead of training from scratch, you start with a pre-trained model and "
        "fine-tune it on your specific dataset. This saves time, requires less data, and often produces "
        "better results. Popular pre-trained models include BERT, GPT, and ResNet.",
        {"source": "ai_guide.pdf", "page": 3}
    ),
    SimulatedDocument(
        "Natural language processing (NLP) is a branch of AI that helps computers understand human "
        "language. Key NLP tasks include sentiment analysis, named entity recognition, machine "
        "translation, and text summarization. Modern NLP is dominated by transformer-based models "
        "like BERT and GPT, which use attention mechanisms to process text.",
        {"source": "nlp_handbook.pdf", "page": 1}
    ),
    SimulatedDocument(
        "Retrieval-Augmented Generation (RAG) combines information retrieval with text generation. "
        "Instead of relying solely on the LLM's training data, RAG retrieves relevant documents "
        "from a knowledge base and includes them in the prompt. This reduces hallucinations, "
        "provides up-to-date information, and enables source citations.",
        {"source": "nlp_handbook.pdf", "page": 5}
    ),
]

print(f"Simulated: {len(sample_documents)} document pages loaded")
for doc in sample_documents:
    print(f"  - {doc.metadata['source']}, page {doc.metadata['page']}: {doc.page_content[:50]}...")
```

**Expected output:**

```
=== PDF Loading ===

To load PDFs, place them in the 'documents/' folder and run:
  documents = load_all_pdfs('documents/')

Simulated: 5 document pages loaded
  - ai_guide.pdf, page 1: Machine learning is a subset of artificial intelli...
  - ai_guide.pdf, page 2: Neural networks are computing systems inspired by ...
  - ai_guide.pdf, page 3: Transfer learning is a technique where a model tra...
  - nlp_handbook.pdf, page 1: Natural language processing (NLP) is a branch of A...
  - nlp_handbook.pdf, page 5: Retrieval-Augmented Generation (RAG) combines info...
```

---

## 28.3 Step 2: Chunking Documents

### Why Chunk?

```
+---------------------------------------------------------------+
|              WHY WE CHUNK DOCUMENTS                           |
+---------------------------------------------------------------+
|                                                               |
|  Problem: A PDF page can have 500+ words                     |
|  But embeddings work best with 100-500 word chunks            |
|  And LLM context windows have limits                          |
|                                                               |
|  Solution: Split documents into smaller, overlapping chunks   |
|                                                               |
|  Original page (1000 words):                                  |
|  [=================================================]         |
|                                                               |
|  Chunked (200 words each, 50 word overlap):                   |
|  [==========]                                                 |
|         [==========]                                          |
|                [==========]                                   |
|                       [==========]                            |
|                              [==========]                     |
|                                                               |
|  Overlap ensures no information is lost at chunk boundaries   |
|                                                               |
+---------------------------------------------------------------+
```

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_documents(documents, chunk_size=500, chunk_overlap=50):
    """
    Split documents into smaller chunks.

    Args:
        documents: List of document objects
        chunk_size: Maximum characters per chunk
        chunk_overlap: Number of characters to overlap between chunks

    Returns:
        List of chunked documents
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = text_splitter.split_documents(documents)

    print(f"Chunking results:")
    print(f"  Original documents: {len(documents)}")
    print(f"  Chunks created: {len(chunks)}")
    print(f"  Chunk size: {chunk_size} characters")
    print(f"  Overlap: {chunk_overlap} characters")

    # Show chunk details
    print(f"\nChunk details:")
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i+1}: {len(chunk.page_content)} chars | Source: {chunk.metadata.get('source', 'unknown')}")

    return chunks


# Chunk the sample documents
chunks = chunk_documents(sample_documents, chunk_size=300, chunk_overlap=30)

print(f"\nFirst chunk content:")
print(f"  {chunks[0].page_content[:150]}...")
```

**Expected output:**

```
Chunking results:
  Original documents: 5
  Chunks created: 7
  Chunk size: 300 characters
  Overlap: 30 characters

Chunk details:
  Chunk 1: 280 chars | Source: ai_guide.pdf
  Chunk 2: 245 chars | Source: ai_guide.pdf
  Chunk 3: 290 chars | Source: ai_guide.pdf
  Chunk 4: 260 chars | Source: ai_guide.pdf
  Chunk 5: 285 chars | Source: ai_guide.pdf
  Chunk 6: 275 chars | Source: nlp_handbook.pdf
  Chunk 7: 290 chars | Source: nlp_handbook.pdf

First chunk content:
  Machine learning is a subset of artificial intelligence that enables systems to learn from data. Unlike traditional programming where rules are explici...
```

**Line-by-line explanation:**

- `RecursiveCharacterTextSplitter` -- Splits text by trying different separators in order. First tries paragraph breaks (`\n\n`), then line breaks (`\n`), then sentences (`. `), then words (` `), and finally individual characters
- `chunk_size=500` -- Each chunk will be at most 500 characters long
- `chunk_overlap=50` -- The last 50 characters of one chunk appear at the beginning of the next chunk. This prevents information from being lost at chunk boundaries
- `split_documents(documents)` -- Processes all documents and returns a list of smaller chunk objects, preserving the original metadata

---

## 28.4 Step 3: Creating Embeddings and Storing in ChromaDB

### Setting Up the Vector Store

```python
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

def create_vector_store(chunks, persist_directory="./chroma_db"):
    """
    Create embeddings and store them in ChromaDB.

    Args:
        chunks: List of document chunks
        persist_directory: Where to save the database

    Returns:
        Chroma vector store object
    """
    # Create the embedding model
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",  # Fast, affordable embedding model
    )

    # Create the vector store from document chunks
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory,
    )

    print(f"Vector store created:")
    print(f"  Chunks embedded: {len(chunks)}")
    print(f"  Embedding model: text-embedding-3-small")
    print(f"  Storage: {persist_directory}")
    print(f"  Total vectors: {vector_store._collection.count()}")

    return vector_store


def load_existing_vector_store(persist_directory="./chroma_db"):
    """
    Load an existing vector store from disk.

    Args:
        persist_directory: Where the database is saved

    Returns:
        Chroma vector store object
    """
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    vector_store = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
    )

    print(f"Loaded existing vector store from {persist_directory}")
    print(f"  Total vectors: {vector_store._collection.count()}")

    return vector_store


# Example usage
print("=== Vector Store Setup ===\n")
print("To create a new vector store:")
print("  vector_store = create_vector_store(chunks)")
print()
print("To load an existing vector store:")
print("  vector_store = load_existing_vector_store()")
```

### Using Local Embeddings (No API Key Needed)

```python
from langchain_community.embeddings import HuggingFaceEmbeddings

def create_local_vector_store(chunks, persist_directory="./chroma_db"):
    """
    Create a vector store using free, local embeddings.
    No API key required.
    """
    # Use a local embedding model
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",  # Small, fast, good quality
    )

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory,
    )

    print(f"Local vector store created:")
    print(f"  Embedding model: all-MiniLM-L6-v2 (runs locally)")
    print(f"  Cost: Free")
    print(f"  No API key needed")

    return vector_store


print("Local embedding option:")
print("  Uses all-MiniLM-L6-v2 from Hugging Face")
print("  Runs on your computer (no internet needed after download)")
print("  Good for privacy-sensitive applications")
```

---

## 28.5 Step 4: Building the Retrieval Chain

### Creating the RAG Chain

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

def create_rag_chain(vector_store, model_name="gpt-4o-mini"):
    """
    Create a RAG chain that retrieves relevant documents and generates answers.

    Args:
        vector_store: ChromaDB vector store with embedded documents
        model_name: Which LLM to use

    Returns:
        A chain that takes a question and returns an answer with sources
    """
    # Create the retriever
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3},  # Return top 3 most relevant chunks
    )

    # Create the LLM
    llm = ChatOpenAI(model=model_name, temperature=0)

    # Create the prompt template
    prompt = ChatPromptTemplate.from_template("""You are a helpful assistant that answers questions based on the provided context.

IMPORTANT RULES:
1. Only answer based on the provided context
2. If the context does not contain the answer, say "I don't have enough information to answer this question based on the available documents."
3. Always cite the source document and page number
4. Be concise but thorough

Context from documents:
{context}

Question: {question}

Answer (with source citations):""")

    # Helper function to format retrieved documents
    def format_docs(docs):
        formatted = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", "?")
            formatted.append(f"[Source {i}: {source}, Page {page}]\n{doc.page_content}")
        return "\n\n".join(formatted)

    # Create the chain
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain, retriever


# Example
print("=== RAG Chain ===\n")
print("The RAG chain works like this:")
print("  1. User asks a question")
print("  2. Retriever finds the 3 most relevant chunks")
print("  3. Chunks are formatted with source citations")
print("  4. Question + chunks are sent to the LLM")
print("  5. LLM generates an answer with citations")
print("  6. Answer is returned to the user")
```

---

## 28.6 Step 5: Adding Conversation Memory

### Remembering Previous Questions

```python
from langchain_core.messages import HumanMessage, AIMessage

class ChatMemory:
    """
    Simple conversation memory that stores the last N exchanges.
    """

    def __init__(self, max_exchanges=5):
        self.messages = []
        self.max_exchanges = max_exchanges

    def add_exchange(self, question, answer):
        """Add a question-answer pair to memory."""
        self.messages.append({"question": question, "answer": answer})
        # Keep only the last N exchanges
        if len(self.messages) > self.max_exchanges:
            self.messages = self.messages[-self.max_exchanges:]

    def get_context(self):
        """Get conversation history as formatted string."""
        if not self.messages:
            return "No previous conversation."

        history = []
        for msg in self.messages:
            history.append(f"User: {msg['question']}")
            history.append(f"Assistant: {msg['answer']}")

        return "\n".join(history)

    def clear(self):
        """Clear all conversation history."""
        self.messages = []

    def __len__(self):
        return len(self.messages)


# Test the memory
memory = ChatMemory(max_exchanges=3)

# Simulate a conversation
exchanges = [
    ("What is machine learning?", "Machine learning is a subset of AI that learns from data."),
    ("How does it differ from traditional programming?", "Traditional programming uses explicit rules, while ML discovers patterns."),
    ("What are the main types?", "The main types are supervised, unsupervised, and reinforcement learning."),
]

print("=== Conversation Memory ===\n")
for q, a in exchanges:
    memory.add_exchange(q, a)
    print(f"  Q: {q}")
    print(f"  A: {a}\n")

print(f"Memory contains {len(memory)} exchanges")
print(f"\nFormatted context:")
print(memory.get_context())
```

**Expected output:**

```
=== Conversation Memory ===

  Q: What is machine learning?
  A: Machine learning is a subset of AI that learns from data.

  Q: How does it differ from traditional programming?
  A: Traditional programming uses explicit rules, while ML discovers patterns.

  Q: What are the main types?
  A: The main types are supervised, unsupervised, and reinforcement learning.

Memory contains 3 exchanges

Formatted context:
User: What is machine learning?
Assistant: Machine learning is a subset of AI that learns from data.
User: How does it differ from traditional programming?
Assistant: Traditional programming uses explicit rules, while ML discovers patterns.
User: What are the main types?
Assistant: The main types are supervised, unsupervised, and reinforcement learning.
```

### RAG Chain with Memory

```python
def create_rag_chain_with_memory(vector_store, model_name="gpt-4o-mini"):
    """
    Create a RAG chain that includes conversation history.
    """
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    llm = ChatOpenAI(model=model_name, temperature=0)

    # Prompt that includes conversation history
    prompt = ChatPromptTemplate.from_template("""You are a helpful assistant that answers questions based on documents.

Previous conversation:
{chat_history}

Context from documents:
{context}

Current question: {question}

Instructions:
1. Use the conversation history to understand context and follow-up questions
2. Answer based on the provided document context
3. If you cannot answer from the documents, say so clearly
4. Cite sources using [Source: filename, Page X] format

Answer:""")

    def format_docs(docs):
        formatted = []
        for doc in docs:
            source = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", "?")
            formatted.append(f"[{source}, Page {page}]: {doc.page_content}")
        return "\n\n".join(formatted)

    return prompt, llm, retriever, format_docs


print("RAG chain with memory created.")
print("The chain now considers previous conversation when answering.")
```

---

## 28.7 Step 6: Building the Chat Interface with Gradio

### What Is Gradio?

```
+---------------------------------------------------------------+
|              WHAT IS GRADIO?                                  |
+---------------------------------------------------------------+
|                                                               |
|  Gradio is a Python library for creating web-based UIs        |
|  for machine learning applications.                           |
|                                                               |
|  Benefits:                                                    |
|  - Create a web interface in ~10 lines of Python              |
|  - No HTML, CSS, or JavaScript knowledge needed               |
|  - Built-in chat interface component                          |
|  - Automatic sharing via public URLs                          |
|  - Easy deployment to Hugging Face Spaces                     |
|                                                               |
|  Install: pip install gradio                                  |
|                                                               |
+---------------------------------------------------------------+
```

### Building the Chat Interface

```python
import gradio as gr

def build_chat_interface():
    """
    Build a Gradio chat interface for the RAG chatbot.
    """

    # In production, these would be initialized with real components
    memory = ChatMemory(max_exchanges=5)

    def respond(message, chat_history):
        """
        Process a user message and return a response.

        Args:
            message: The user's question
            chat_history: List of [user_msg, bot_msg] pairs from Gradio

        Returns:
            Updated chat history
        """
        # Step 1: Retrieve relevant documents
        # docs = retriever.get_relevant_documents(message)
        # context = format_docs(docs)

        # Simulated retrieval
        simulated_context = "Machine learning is a subset of AI. Neural networks are inspired by the brain."
        simulated_sources = ["ai_guide.pdf (Page 1)", "ai_guide.pdf (Page 2)"]

        # Step 2: Generate response using RAG
        # response = chain.invoke({
        #     "question": message,
        #     "context": context,
        #     "chat_history": memory.get_context(),
        # })

        # Simulated response
        response = f"Based on the documents: {simulated_context[:100]}...\n\nSources: {', '.join(simulated_sources)}"

        # Step 3: Update memory
        memory.add_exchange(message, response)

        # Step 4: Update chat history for Gradio
        chat_history.append([message, response])

        return "", chat_history

    # Build the Gradio interface
    with gr.Blocks(title="RAG Chatbot") as demo:
        gr.Markdown("# RAG Document Chatbot")
        gr.Markdown("Ask questions about your documents. The chatbot will find relevant information and cite sources.")

        chatbot = gr.Chatbot(
            height=400,
            label="Chat",
            show_label=True,
        )

        with gr.Row():
            msg = gr.Textbox(
                placeholder="Ask a question about your documents...",
                label="Your Question",
                scale=4,
            )
            submit_btn = gr.Button("Send", variant="primary", scale=1)

        with gr.Row():
            clear_btn = gr.Button("Clear Chat")

        # Event handlers
        msg.submit(respond, [msg, chatbot], [msg, chatbot])
        submit_btn.click(respond, [msg, chatbot], [msg, chatbot])
        clear_btn.click(lambda: ([], None), None, [chatbot, msg])

    return demo


print("=== Gradio Chat Interface ===\n")
print("To launch the chatbot:")
print("  demo = build_chat_interface()")
print("  demo.launch()")
print()
print("The interface includes:")
print("  - Chat window with conversation history")
print("  - Text input for questions")
print("  - Send button")
print("  - Clear chat button")
print("  - Source citations in responses")
```

---

## 28.8 Step 7: The Complete Application

### Putting It All Together

```python
"""
RAG Chatbot -- Complete Application
====================================

A complete RAG chatbot that loads PDF documents, creates embeddings,
stores them in ChromaDB, and provides a chat interface with Gradio.

Usage:
    1. Place PDF files in the 'documents/' folder
    2. Run: python rag_chatbot.py
    3. Open the URL shown in the terminal
"""

import os
import gradio as gr
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


# ============================================
# Configuration
# ============================================
DOCUMENTS_DIR = "./documents"
CHROMA_DIR = "./chroma_db"
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K = 3
MAX_MEMORY = 5


# ============================================
# Step 1: Load Documents
# ============================================
def load_documents(directory):
    """Load all PDFs from a directory."""
    documents = []
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created {directory}/ -- please add PDF files and restart.")
        return documents

    pdf_files = [f for f in os.listdir(directory) if f.lower().endswith('.pdf')]
    print(f"Found {len(pdf_files)} PDF files")

    for pdf_file in sorted(pdf_files):
        file_path = os.path.join(directory, pdf_file)
        try:
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            documents.extend(pages)
            print(f"  Loaded: {pdf_file} ({len(pages)} pages)")
        except Exception as e:
            print(f"  Error loading {pdf_file}: {e}")

    return documents


# ============================================
# Step 2: Chunk Documents
# ============================================
def chunk_documents(documents):
    """Split documents into smaller chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    chunks = splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks from {len(documents)} pages")
    return chunks


# ============================================
# Step 3: Create or Load Vector Store
# ============================================
def setup_vector_store(chunks=None):
    """Create a new vector store or load an existing one."""
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    if chunks:
        # Create new vector store
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=CHROMA_DIR,
        )
        print(f"Created new vector store with {len(chunks)} vectors")
    else:
        # Load existing vector store
        vector_store = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=embeddings,
        )
        count = vector_store._collection.count()
        print(f"Loaded existing vector store with {count} vectors")

    return vector_store


# ============================================
# Step 4: Create RAG Chain
# ============================================
def create_chain(vector_store):
    """Create the RAG chain with retrieval and generation."""
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": TOP_K},
    )

    llm = ChatOpenAI(model=LLM_MODEL, temperature=0)

    prompt = ChatPromptTemplate.from_template("""You are a helpful assistant that answers questions based on the provided documents.

RULES:
1. Answer ONLY based on the provided context
2. If the context does not contain the answer, say: "I could not find this information in the uploaded documents."
3. Always cite sources in [Source: filename, Page X] format
4. Consider the conversation history for follow-up questions
5. Be concise and accurate

Conversation History:
{chat_history}

Document Context:
{context}

Question: {question}

Answer:""")

    def format_docs(docs):
        parts = []
        for doc in docs:
            source = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", "?")
            parts.append(f"[{source}, Page {page}]:\n{doc.page_content}")
        return "\n\n---\n\n".join(parts)

    def get_sources(docs):
        sources = set()
        for doc in docs:
            source = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", "?")
            sources.add(f"{source}, Page {page}")
        return list(sources)

    return retriever, llm, prompt, format_docs, get_sources


# ============================================
# Step 5: Chat Memory
# ============================================
class ConversationMemory:
    def __init__(self, max_exchanges=MAX_MEMORY):
        self.history = []
        self.max = max_exchanges

    def add(self, question, answer):
        self.history.append({"q": question, "a": answer})
        if len(self.history) > self.max:
            self.history = self.history[-self.max:]

    def format(self):
        if not self.history:
            return "No previous conversation."
        lines = []
        for h in self.history:
            lines.append(f"User: {h['q']}")
            lines.append(f"Assistant: {h['a']}")
        return "\n".join(lines)

    def clear(self):
        self.history = []


# ============================================
# Step 6: Build the Application
# ============================================
def build_app():
    """Build the complete RAG chatbot application."""

    print("=" * 60)
    print("  RAG CHATBOT -- INITIALIZATION")
    print("=" * 60)

    # Load and process documents
    print("\n1. Loading documents...")
    documents = load_documents(DOCUMENTS_DIR)

    if documents:
        print("\n2. Chunking documents...")
        chunks = chunk_documents(documents)

        print("\n3. Creating vector store...")
        vector_store = setup_vector_store(chunks)
    else:
        print("\n2-3. Loading existing vector store...")
        vector_store = setup_vector_store()

    # Create the RAG chain
    print("\n4. Creating RAG chain...")
    retriever, llm, prompt, format_docs, get_sources = create_chain(vector_store)
    print("   RAG chain ready.")

    # Create memory
    memory = ConversationMemory()

    # Define the chat function
    def chat(message, history):
        # Retrieve relevant documents
        docs = retriever.invoke(message)
        context = format_docs(docs)
        sources = get_sources(docs)

        # Build the full prompt
        messages = prompt.format_messages(
            chat_history=memory.format(),
            context=context,
            question=message,
        )

        # Generate response
        response = llm.invoke(messages)
        answer = response.content

        # Add source citations
        if sources:
            source_text = "\n\nSources:\n" + "\n".join(f"  - {s}" for s in sources)
            full_answer = answer + source_text
        else:
            full_answer = answer

        # Update memory
        memory.add(message, answer)

        return full_answer

    # Build Gradio interface
    print("\n5. Building chat interface...")

    with gr.Blocks(
        title="RAG Document Chatbot",
        theme=gr.themes.Soft(),
    ) as demo:
        gr.Markdown("""
        # RAG Document Chatbot
        Ask questions about your uploaded documents.
        The chatbot retrieves relevant passages and generates answers with source citations.
        """)

        chatbot = gr.Chatbot(
            height=450,
            label="Conversation",
            type="messages",
        )

        with gr.Row():
            msg = gr.Textbox(
                placeholder="Type your question here...",
                label="Question",
                scale=4,
                lines=1,
            )
            send = gr.Button("Send", variant="primary", scale=1)

        with gr.Row():
            clear = gr.Button("Clear Chat")
            info = gr.Markdown(f"Connected to {vector_store._collection.count()} document chunks")

        def respond(message, chat_history):
            answer = chat(message, chat_history)
            chat_history.append({"role": "user", "content": message})
            chat_history.append({"role": "assistant", "content": answer})
            return "", chat_history

        def clear_chat():
            memory.clear()
            return [], ""

        msg.submit(respond, [msg, chatbot], [msg, chatbot])
        send.click(respond, [msg, chatbot], [msg, chatbot])
        clear.click(clear_chat, None, [chatbot, msg])

    print("   Interface ready.")
    print(f"\n{'='*60}")
    print("  READY! Run demo.launch() to start the chatbot.")
    print(f"{'='*60}")

    return demo


# ============================================
# Main Entry Point
# ============================================
# if __name__ == "__main__":
#     demo = build_app()
#     demo.launch(
#         server_name="0.0.0.0",  # Allow external access
#         server_port=7860,        # Port number
#         share=False,             # Set True for public URL
#     )

print("=== COMPLETE RAG CHATBOT APPLICATION ===\n")
print("To run the chatbot:")
print("  1. Place PDF files in ./documents/")
print("  2. Set OPENAI_API_KEY environment variable")
print("  3. Run: python rag_chatbot.py")
print("  4. Open http://localhost:7860 in your browser")
print()
print("To share publicly:")
print("  demo.launch(share=True)")
print("  This creates a temporary public URL anyone can access")
```

**Expected output:**

```
=== COMPLETE RAG CHATBOT APPLICATION ===

To run the chatbot:
  1. Place PDF files in ./documents/
  2. Set OPENAI_API_KEY environment variable
  3. Run: python rag_chatbot.py
  4. Open http://localhost:7860 in your browser

To share publicly:
  demo.launch(share=True)
  This creates a temporary public URL anyone can access
```

---

## 28.9 Deployment Options

### Deploying Your Chatbot

```
+---------------------------------------------------------------+
|              DEPLOYMENT OPTIONS                               |
+---------------------------------------------------------------+
|                                                               |
|  Option 1: Hugging Face Spaces (FREE)                        |
|  - Upload to spaces.huggingface.co                           |
|  - Free hosting for Gradio apps                              |
|  - Public URL for anyone to access                           |
|  - Limited GPU (CPU-only on free tier)                       |
|                                                               |
|  Option 2: Local Network                                      |
|  - Run on your own machine                                   |
|  - demo.launch(server_name="0.0.0.0")                        |
|  - Accessible from other devices on your network             |
|                                                               |
|  Option 3: Cloud Server (AWS, GCP, Azure)                    |
|  - Deploy to a cloud virtual machine                         |
|  - More control and resources                                |
|  - Costs money for the server                                |
|                                                               |
|  Option 4: Docker Container                                   |
|  - Package everything in a Docker image                       |
|  - Portable and reproducible                                 |
|  - Easy to deploy anywhere                                   |
|                                                               |
+---------------------------------------------------------------+
```

### Creating a requirements.txt

```python
# Generate requirements.txt for the project

requirements = """langchain>=0.3.0
langchain-openai>=0.2.0
langchain-community>=0.3.0
chromadb>=0.5.0
gradio>=5.0.0
pypdf>=4.0.0
sentence-transformers>=3.0.0
"""

print("requirements.txt:")
print("-" * 40)
print(requirements)
print("Install with: pip install -r requirements.txt")
```

### Deploying to Hugging Face Spaces

```python
# Steps to deploy to Hugging Face Spaces

deployment_steps = """
Deploying to Hugging Face Spaces:

1. Create a Hugging Face account at huggingface.co

2. Create a new Space:
   - Go to huggingface.co/new-space
   - Choose "Gradio" as the SDK
   - Name your space (e.g., "my-rag-chatbot")

3. Upload your files:
   - rag_chatbot.py (renamed to app.py)
   - requirements.txt
   - documents/ folder with your PDFs

4. Set your API key:
   - Go to Space Settings -> Repository secrets
   - Add OPENAI_API_KEY as a secret

5. The Space will automatically build and deploy.
   Your chatbot will be available at:
   https://huggingface.co/spaces/your-username/my-rag-chatbot
"""

print(deployment_steps)
```

---

## 28.10 Improvements and Extensions

### Ideas for Enhancing Your Chatbot

```python
# Potential improvements to the RAG chatbot

improvements = {
    "Better Retrieval": [
        "Use hybrid search (combine keyword + semantic search)",
        "Implement re-ranking to improve result quality",
        "Add metadata filtering (by date, document type, etc.)",
    ],
    "Better Answers": [
        "Use a more powerful LLM (GPT-4, Claude 3)",
        "Add chain-of-thought prompting for complex questions",
        "Implement answer verification against source documents",
    ],
    "Better Interface": [
        "Add file upload in the UI (let users upload PDFs)",
        "Show source snippets alongside answers",
        "Add a sidebar with document list and search",
        "Support dark mode and custom themes",
    ],
    "Better Performance": [
        "Cache embeddings to avoid recomputing",
        "Use async processing for faster responses",
        "Implement streaming for real-time answer display",
    ],
    "Security": [
        "Add user authentication",
        "Rate limiting to prevent abuse",
        "Input validation to prevent prompt injection",
    ],
}

print("Ideas for Improving Your RAG Chatbot:")
print("=" * 60)
for category, ideas in improvements.items():
    print(f"\n  {category}:")
    for idea in ideas:
        print(f"    - {idea}")
```

**Expected output:**

```
Ideas for Improving Your RAG Chatbot:
============================================================

  Better Retrieval:
    - Use hybrid search (combine keyword + semantic search)
    - Implement re-ranking to improve result quality
    - Add metadata filtering (by date, document type, etc.)

  Better Answers:
    - Use a more powerful LLM (GPT-4, Claude 3)
    - Add chain-of-thought prompting for complex questions
    - Implement answer verification against source documents

  Better Interface:
    - Add file upload in the UI (let users upload PDFs)
    - Show source snippets alongside answers
    - Add a sidebar with document list and search
    - Support dark mode and custom themes

  Better Performance:
    - Cache embeddings to avoid recomputing
    - Use async processing for faster responses
    - Implement streaming for real-time answer display

  Security:
    - Add user authentication
    - Rate limiting to prevent abuse
    - Input validation to prevent prompt injection
```

---

## Common Mistakes

1. **Not setting the pad token or chunk overlap** -- Zero overlap means information at chunk boundaries can be lost. Always use at least 10-20% overlap.

2. **Chunks too large or too small** -- Chunks that are too large contain noise. Chunks that are too small lack context. 300-500 characters is a good starting point.

3. **Not handling empty documents** -- Some PDF pages may be blank or contain only images. Filter these out before embedding.

4. **Forgetting to persist the vector store** -- If you do not save the vector store to disk, you will need to re-embed all documents every time you restart.

5. **Not limiting conversation memory** -- Unlimited memory fills the context window. Keep only the last 3-5 exchanges.

6. **Not telling the LLM to cite sources** -- Without explicit instructions to cite sources, the LLM will answer without citations. Always include citation instructions in the prompt.

---

## Best Practices

1. **Test with a small document set first** -- Start with 1-2 PDFs to verify your pipeline works before scaling to hundreds of documents.

2. **Use the right embedding model** -- `text-embedding-3-small` is a good balance of quality and cost. Use `text-embedding-3-large` for higher quality.

3. **Include source citations in every answer** -- This builds trust and lets users verify the information.

4. **Handle edge cases gracefully** -- What if no relevant documents are found? What if the PDF is corrupted? Add error handling for all cases.

5. **Monitor costs** -- Track your API usage. Embedding a large document corpus can cost several dollars. LLM calls add up during active conversations.

6. **Provide clear instructions in the UI** -- Tell users what documents are available and what kinds of questions they can ask.

---

## Quick Summary

This chapter walked through building a complete RAG chatbot from scratch. The pipeline loads PDF documents, chunks them into smaller pieces, creates embeddings, stores them in ChromaDB, retrieves relevant chunks when a user asks a question, sends the question and context to an LLM, and displays the answer with source citations in a Gradio web interface. Conversation memory allows follow-up questions, and the application can be deployed to Hugging Face Spaces for free public access.

---

## Key Points

- The RAG chatbot pipeline: Load -> Chunk -> Embed -> Store -> Retrieve -> Generate -> Display
- **PyPDF** loads PDF files into text documents with page metadata
- **RecursiveCharacterTextSplitter** chunks text with overlap to preserve context
- **ChromaDB** stores embeddings persistently on disk for fast similarity search
- The **RAG prompt** instructs the LLM to answer only from provided context and cite sources
- **Conversation memory** enables follow-up questions by including chat history in the prompt
- **Gradio** creates a web chat interface with just a few lines of Python
- Local embeddings (HuggingFace) provide a free, private alternative to API embeddings
- The chatbot can be deployed to **Hugging Face Spaces** for free public access
- Always include **source citations** to build trust and verifiability

---

## Practice Questions

1. Why do we use overlapping chunks instead of splitting text at exact boundaries? What problems would non-overlapping chunks cause?

2. You have 1,000 PDFs totaling 50,000 pages. Estimate the cost of embedding all documents using OpenAI's text-embedding-3-small model. What strategies could reduce this cost?

3. A user asks a follow-up question: "Tell me more about that." How does the conversation memory help the chatbot understand what "that" refers to?

4. Compare ChromaDB with other vector databases (Pinecone, Weaviate, FAISS). What are the trade-offs of using a local database like ChromaDB?

5. How would you modify the RAG prompt to handle questions that span multiple documents? For example, "Compare the approaches described in document A and document B."

---

## Exercises

### Exercise 1: Add File Upload

Modify the Gradio interface to include a file upload component. When a user uploads a PDF, process it (chunk, embed, store) and make it available for querying immediately.

### Exercise 2: Implement Streaming

Modify the chatbot to stream the LLM's response token by token, so the user sees the answer being generated in real time instead of waiting for the full response.

### Exercise 3: Source Highlighting

When the chatbot returns an answer with source citations, add a feature that displays the actual source text snippets below the answer, so users can see exactly which parts of the documents were used.

---

## Congratulations!

You have completed Book 5: Generative AI & Large Language Models.

Take a moment to appreciate what you have accomplished. You started with the fundamentals of how LLMs work and progressed all the way to building a production-grade RAG chatbot. Along the way, you mastered:

- **LLM Fundamentals** -- How large language models are built and how they generate text
- **Prompt Engineering** -- Writing effective prompts, few-shot learning, chain-of-thought reasoning
- **RAG** -- Retrieval-Augmented Generation, embeddings, vector databases
- **Fine-Tuning** -- LoRA, QLoRA, and practical fine-tuning with PEFT
- **AI Agents** -- Function calling, tool use, LangChain, multi-agent systems
- **Multimodal AI** -- Vision, speech, and text models working together
- **Real Projects** -- A complete, deployable RAG chatbot

These skills represent the cutting edge of AI application development. You are now equipped to build intelligent systems that combine the power of large language models with external knowledge, tools, and multiple data modalities.

---

## What Is Next? Book 6: MLOps -- Taking AI to Production

In Book 6, you will learn how to take your AI models from experiments to production systems that serve real users reliably. You will cover:

- **Model Serving** -- Deploying models as APIs with FastAPI and Docker
- **CI/CD for ML** -- Automated testing and deployment pipelines
- **Monitoring** -- Tracking model performance, drift detection, and alerting
- **Experiment Tracking** -- MLflow, Weights & Biases for managing experiments
- **Data Pipelines** -- Building reliable data processing workflows
- **Scaling** -- Handling thousands of requests per second
- **Cost Optimization** -- Reducing compute costs in production
- **Security** -- Protecting models and data in production environments

Building a great model is only half the job. Getting it to production and keeping it running reliably is the other half. Book 6 teaches you that other half.

See you in Book 6!
