# Chapter 14: Document Processing

## What You Will Learn

In this chapter, you will learn:

- Why documents need to be split into chunks for RAG
- How to extract text from PDF files using PyPDF2
- How to extract text from HTML pages using BeautifulSoup
- How to process plain text files
- What chunking strategies exist and when to use each one
- How to choose chunk size and overlap
- How chunk quality affects RAG performance

## Why This Chapter Matters

In the previous chapter, you learned that RAG retrieves relevant documents to help the LLM answer questions. But here is the problem: most documents are too long to fit in an LLM's context window. A 100-page company manual cannot be stuffed into a prompt.

The solution is chunking. You split documents into small, meaningful pieces. When a user asks a question, you retrieve only the relevant pieces, not the entire document.

But how you split matters enormously. Split in the wrong place and you break a sentence in half, losing its meaning. Use chunks that are too small and you lose context. Use chunks that are too large and you waste tokens on irrelevant text. This chapter teaches you how to split documents intelligently.

Think of it like cutting a pizza. You could cut it into 100 tiny pieces (too small to eat), 2 huge pieces (hard to handle), or 8 proper slices (just right). Chunking is about finding the "just right" size for your documents.

---

## Why We Need Chunking

```
+------------------------------------------------------------------+
|                    WHY CHUNKING IS NEEDED                         |
|                                                                   |
|  Problem: A 50-page document has ~25,000 words                    |
|                                                                   |
|  Option 1: Put the whole document in the prompt                   |
|  +------------------------------------------------------------+  |
|  | 25,000 words in prompt + question = TOO MANY TOKENS!        |  |
|  | Expensive, slow, might exceed context window limit          |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  Option 2: Split into chunks and retrieve relevant ones           |
|  +------+ +------+ +------+ +------+ +------+ +------+          |
|  |Chunk | |Chunk | |Chunk | |Chunk | |Chunk | |Chunk |          |
|  |  1   | |  2   | |  3   | |  4   | |  5   | | ...  |          |
|  | 500  | | 500  | | 500  | | 500  | | 500  | | 500  |          |
|  |words | |words | |words | |words | |words | |words |          |
|  +------+ +------+ +------+ +------+ +------+ +------+          |
|                         |                                         |
|                         v                                         |
|              Only retrieve chunks 3 and 4                        |
|              (relevant to the question)                           |
|              = 1,000 words in prompt. Fast and cheap!            |
+------------------------------------------------------------------+
```

> **Chunk:** A small piece of text extracted from a larger document. Chunks are stored separately in the vector database and retrieved individually based on relevance to the user's query.

> **Chunking:** The process of splitting a document into smaller pieces (chunks). The goal is to create pieces that are small enough to be relevant but large enough to contain meaningful information.

---

## Extracting Text from PDF Files

PDF is one of the most common document formats. Let us extract text from PDFs using PyPDF2.

> **PyPDF2:** A Python library for reading and manipulating PDF files. It can extract text from PDF pages, merge PDFs, split PDFs, and more. Install it with `pip install pypdf2`.

```python
# Install: pip install pypdf2
from PyPDF2 import PdfReader
import os

def extract_text_from_pdf(pdf_path):
    """
    Extract all text from a PDF file.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Dictionary with page numbers and text
    """
    reader = PdfReader(pdf_path)
    pages = {}

    print(f"PDF: {os.path.basename(pdf_path)}")
    print(f"Total pages: {len(reader.pages)}")
    print()

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            pages[i + 1] = text.strip()

    return pages


# Create a sample PDF for demonstration
# In practice, you would read existing PDF files
def create_sample_pdf(filepath):
    """Create a sample PDF for testing."""
    # pip install fpdf2
    try:
        from fpdf import FPDF

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Company Handbook", ln=True, align="C")
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 8,
            "Chapter 1: Welcome\n\n"
            "Welcome to TechCorp! This handbook covers all company "
            "policies and procedures. All employees must read and "
            "understand this document.\n\n"
            "Chapter 2: Work Hours\n\n"
            "Standard work hours are 9 AM to 5 PM, Monday through "
            "Friday. Flexible scheduling is available with manager "
            "approval. Remote work is permitted up to 3 days per week."
        )
        pdf.output(filepath)
        return True
    except ImportError:
        print("Note: fpdf2 not installed. Using simulated PDF text.")
        return False

# Simulate PDF text extraction for demonstration
sample_pdf_text = {
    1: """Company Handbook

Chapter 1: Welcome

Welcome to TechCorp! This handbook covers all company
policies and procedures. All employees must read and
understand this document.""",

    2: """Chapter 2: Work Hours

Standard work hours are 9 AM to 5 PM, Monday through
Friday. Flexible scheduling is available with manager
approval. Remote work is permitted up to 3 days per week.

Chapter 3: Leave Policy

Employees receive 15 days of paid time off per year.
Sick leave is separate at 10 days per year.
Unused PTO carries over up to 5 days."""
}

# Process the extracted text
print("Extracted PDF Text:")
print("=" * 40)
for page_num, text in sample_pdf_text.items():
    print(f"\n--- Page {page_num} ---")
    print(text[:200])
    if len(text) > 200:
        print("...")
    print(f"[{len(text)} characters]")
```

**Output:**
```
Extracted PDF Text:
========================================

--- Page 1 ---
Company Handbook

Chapter 1: Welcome

Welcome to TechCorp! This handbook covers all company
policies and procedures. All employees must read and
understand this document.
[178 characters]

--- Page 2 ---
Chapter 2: Work Hours

Standard work hours are 9 AM to 5 PM, Monday through
Friday. Flexible scheduling is available with manager
approval. Remote work is permitted up to 3 days per week.
[341 characters]
```

**Line-by-line explanation:**

- `PdfReader(pdf_path)` opens a PDF file and creates a reader object.
- `len(reader.pages)` tells you how many pages the PDF has.
- `page.extract_text()` extracts the text content from a single page. Note that PDFs with images or complex layouts may not extract cleanly.
- `text.strip()` removes leading and trailing whitespace.
- We store text by page number so you can reference which page information came from (useful for citations).

---

## Extracting Text from HTML

Web pages are another common data source. BeautifulSoup makes it easy to extract clean text from HTML.

> **BeautifulSoup:** A Python library for parsing HTML and XML documents. It creates a tree structure from the HTML that you can navigate and search. Think of it as a tool that understands the structure of web pages. Install with `pip install beautifulsoup4`.

```python
# Install: pip install beautifulsoup4
from bs4 import BeautifulSoup
import re

def extract_text_from_html(html_content, ignore_tags=None):
    """
    Extract clean text from HTML content.

    Args:
        html_content: Raw HTML string
        ignore_tags: List of HTML tags to ignore (e.g., ['script', 'style'])

    Returns:
        Clean text string
    """
    if ignore_tags is None:
        ignore_tags = ['script', 'style', 'nav', 'footer', 'header']

    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove unwanted tags
    for tag in ignore_tags:
        for element in soup.find_all(tag):
            element.decompose()

    # Get text and clean it up
    text = soup.get_text(separator='\n')

    # Clean up whitespace
    lines = [line.strip() for line in text.splitlines()]
    text = '\n'.join(line for line in lines if line)

    return text

def extract_structured_html(html_content):
    """
    Extract text with structure (headings, paragraphs, lists).
    Preserves document hierarchy for better chunking.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    sections = []
    current_section = {"heading": "Introduction", "content": []}

    for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'li']):
        if element.name in ['h1', 'h2', 'h3']:
            # Save current section and start new one
            if current_section["content"]:
                sections.append(current_section)
            current_section = {
                "heading": element.get_text().strip(),
                "content": []
            }
        elif element.name in ['p', 'li']:
            text = element.get_text().strip()
            if text:
                current_section["content"].append(text)

    # Don't forget the last section
    if current_section["content"]:
        sections.append(current_section)

    return sections


# Example HTML content
sample_html = """
<html>
<head><title>Product Guide</title></head>
<body>
    <nav>Home | Products | Support</nav>
    <h1>SmartWatch Pro User Guide</h1>
    <p>Welcome to your new SmartWatch Pro! This guide will help
    you get started with your device.</p>

    <h2>Getting Started</h2>
    <p>To turn on your SmartWatch Pro, press and hold the side
    button for 3 seconds. The screen will light up with the
    setup wizard.</p>
    <p>Follow the on-screen instructions to pair with your phone.</p>

    <h2>Features</h2>
    <p>Your SmartWatch Pro includes these features:</p>
    <ul>
        <li>Heart rate monitoring with 24/7 tracking</li>
        <li>GPS tracking for outdoor activities</li>
        <li>Water resistance up to 50 meters</li>
        <li>5-day battery life with normal usage</li>
    </ul>

    <h2>Troubleshooting</h2>
    <p>If your watch is not responding, try a force restart by
    holding the side button for 10 seconds.</p>

    <script>console.log('tracking');</script>
    <footer>Copyright 2024 TechCorp</footer>
</body>
</html>
"""

# Method 1: Simple text extraction
print("=== Simple Text Extraction ===")
simple_text = extract_text_from_html(sample_html)
print(simple_text)
print()

# Method 2: Structured extraction
print("=== Structured Extraction ===")
sections = extract_structured_html(sample_html)
for section in sections:
    print(f"\n[{section['heading']}]")
    for paragraph in section['content']:
        print(f"  {paragraph[:80]}...")
```

**Output:**
```
=== Simple Text Extraction ===
Product Guide
SmartWatch Pro User Guide
Welcome to your new SmartWatch Pro! This guide will help
you get started with your device.
Getting Started
To turn on your SmartWatch Pro, press and hold the side
button for 3 seconds. The screen will light up with the
setup wizard.
Follow the on-screen instructions to pair with your phone.
Features
Your SmartWatch Pro includes these features:
Heart rate monitoring with 24/7 tracking
GPS tracking for outdoor activities
Water resistance up to 50 meters
5-day battery life with normal usage
Troubleshooting
If your watch is not responding, try a force restart by
holding the side button for 10 seconds.

=== Structured Extraction ===

[SmartWatch Pro User Guide]
  Welcome to your new SmartWatch Pro! This guide will help
you get started with y...

[Getting Started]
  To turn on your SmartWatch Pro, press and hold the side
button for 3 seconds. T...
  Follow the on-screen instructions to pair with your phone....

[Features]
  Your SmartWatch Pro includes these features:...
  Heart rate monitoring with 24/7 tracking...
  GPS tracking for outdoor activities...
  Water resistance up to 50 meters...
  5-day battery life with normal usage...

[Troubleshooting]
  If your watch is not responding, try a force restart by
holding the side button...
```

**Line-by-line explanation:**

- `BeautifulSoup(html_content, 'html.parser')` parses the HTML into a navigable tree structure. The `'html.parser'` is Python's built-in HTML parser.
- `element.decompose()` removes unwanted elements like `<script>` and `<style>` tags. These contain code and styling, not useful text.
- `soup.get_text(separator='\n')` extracts all text, using newlines to separate elements.
- `extract_structured_html()` preserves the document structure by tracking which heading each paragraph belongs to. This is valuable for RAG because it keeps related content together.
- The structured approach is better for chunking because you can chunk by section rather than by arbitrary character count.

---

## Processing Plain Text Files

Plain text files are the simplest to process, but they still need cleaning.

```python
def extract_text_from_file(filepath, encoding='utf-8'):
    """
    Read and clean a plain text file.

    Args:
        filepath: Path to the text file
        encoding: File encoding (default UTF-8)

    Returns:
        Cleaned text string
    """
    with open(filepath, 'r', encoding=encoding) as f:
        text = f.read()

    # Clean the text
    text = clean_text(text)
    return text

def clean_text(text):
    """
    Clean text by removing extra whitespace and artifacts.
    """
    import re

    # Replace multiple newlines with double newline
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Replace multiple spaces with single space
    text = re.sub(r' {2,}', ' ', text)

    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.splitlines()]
    text = '\n'.join(lines)

    # Remove leading/trailing whitespace from entire text
    text = text.strip()

    return text


# Example: cleaning messy text
messy_text = """

    Chapter 1:    Introduction



    This   is  the   first    paragraph   with   extra   spaces.

    This is    the second    paragraph.



    It has    lots of    unnecessary     whitespace.


    Chapter 2:     Advanced Topics



    This chapter covers     more complex    material.

"""

cleaned = clean_text(messy_text)
print("Before cleaning:")
print(repr(messy_text[:100]))
print(f"\nLength before: {len(messy_text)}")
print()
print("After cleaning:")
print(cleaned)
print(f"\nLength after: {len(cleaned)}")
```

**Output:**
```
Before cleaning:
'\n\n    Chapter 1:    Introduction\n\n\n\n    This   is  the   first    paragraph   with   extra   '

Length before: 310

After cleaning:
Chapter 1: Introduction

This is the first paragraph with extra spaces.

This is the second paragraph.

It has lots of unnecessary whitespace.

Chapter 2: Advanced Topics

This chapter covers more complex material.

Length after: 202
```

---

## Chunking Strategy 1: Fixed-Size Chunking

The simplest approach. Split text into chunks of a fixed number of characters or words.

```python
def fixed_size_chunk(text, chunk_size=500, overlap=50):
    """
    Split text into fixed-size chunks with overlap.

    Args:
        text: The text to split
        chunk_size: Number of characters per chunk
        overlap: Number of characters to overlap between chunks

    Returns:
        List of text chunks
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start = end - overlap

    return chunks


# Example
sample_text = """
The history of artificial intelligence began in the 1950s when computer
scientists first explored the idea of machines that could think. Alan
Turing proposed the famous Turing Test in 1950, asking whether machines
could exhibit intelligent behavior indistinguishable from humans.

In 1956, John McCarthy organized the Dartmouth Conference, which is
widely considered the birth of AI as a field. Researchers were optimistic
that human-level AI would be achieved within a generation.

The 1960s and 1970s saw early successes in AI, including programs that
could play chess and prove mathematical theorems. However, progress was
slower than expected, leading to the first "AI Winter" in the 1970s when
funding and interest declined.

The 1980s brought expert systems, which encoded human knowledge as rules.
Companies invested heavily in AI, but the limitations of rule-based
systems led to the second AI Winter in the late 1980s.

The modern era of AI began with the rise of machine learning in the
2000s and deep learning in the 2010s. Neural networks, powered by large
datasets and fast GPUs, achieved breakthroughs in image recognition,
natural language processing, and game playing.
""".strip()

chunks = fixed_size_chunk(sample_text, chunk_size=300, overlap=50)

print(f"Text length: {len(sample_text)} characters")
print(f"Number of chunks: {len(chunks)}")
print()

for i, chunk in enumerate(chunks):
    print(f"--- Chunk {i + 1} ({len(chunk)} chars) ---")
    print(chunk[:100] + "..." if len(chunk) > 100 else chunk)
    print()
```

**Output:**
```
Text length: 1062 characters
Number of chunks: 5

--- Chunk 1 (300 chars) ---
The history of artificial intelligence began in the 1950s when computer
scientists first explored t...

--- Chunk 2 (300 chars) ---
sked whether machines
could exhibit intelligent behavior indistinguishable from humans.

In 1956, Joh...

--- Chunk 3 (300 chars) ---
rly successes in AI, including programs that
could play chess and prove mathematical theorems. Howeve...

--- Chunk 4 (300 chars) ---
pert systems, which encoded human knowledge as rules.
Companies invested heavily in AI, but the limit...

--- Chunk 5 (212 chars) ---
e of machine learning in the
2000s and deep learning in the 2010s. Neural networks, powered by large
...
```

```
+------------------------------------------------------------------+
|              FIXED-SIZE CHUNKING WITH OVERLAP                     |
|                                                                   |
|  Original text:                                                   |
|  [=====================================================]         |
|                                                                   |
|  Chunk 1: [============]                                          |
|  Chunk 2:          [============]     <-- overlap                 |
|  Chunk 3:                  [============]                         |
|  Chunk 4:                          [============]                 |
|                                                                   |
|  The overlap ensures no information is lost at                    |
|  chunk boundaries. If a sentence spans two chunks,               |
|  it appears in both.                                              |
+------------------------------------------------------------------+
```

> **Overlap:** The number of characters (or tokens) shared between consecutive chunks. Overlap prevents information loss at chunk boundaries. If a key sentence falls at the edge of one chunk, the overlap ensures it also appears in the next chunk.

**Line-by-line explanation:**

- `chunk_size=500` sets each chunk to 500 characters. This is a common starting point.
- `overlap=50` means the last 50 characters of one chunk are repeated at the start of the next chunk. This prevents losing information at boundaries.
- `start = end - overlap` moves the starting position back by the overlap amount for each new chunk.
- The tradeoff: more overlap means better coverage but more storage and processing. Less overlap means some information might be split across chunks.

---

## Chunking Strategy 2: Recursive Character Splitting

This strategy tries to split on natural boundaries like paragraphs, sentences, and words before falling back to characters.

```python
def recursive_chunk(text, chunk_size=500, overlap=50):
    """
    Split text recursively, trying natural boundaries first.

    Tries to split on:
    1. Double newlines (paragraphs)
    2. Single newlines
    3. Sentences (periods)
    4. Words (spaces)
    5. Characters (last resort)
    """
    separators = ["\n\n", "\n", ". ", " ", ""]

    def split_text(text, separators):
        # Base case: text is small enough
        if len(text) <= chunk_size:
            return [text]

        # Try each separator
        for sep in separators:
            if sep == "":
                # Last resort: split by character
                return fixed_size_chunk(text, chunk_size, overlap)

            parts = text.split(sep)
            if len(parts) == 1:
                continue

            # Build chunks from parts
            chunks = []
            current_chunk = ""

            for part in parts:
                test_chunk = current_chunk + sep + part if current_chunk else part

                if len(test_chunk) <= chunk_size:
                    current_chunk = test_chunk
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = part

            if current_chunk:
                chunks.append(current_chunk.strip())

            # Check if any chunk is still too large
            final_chunks = []
            for chunk in chunks:
                if len(chunk) > chunk_size:
                    # Recursively split with next separator
                    remaining_seps = separators[separators.index(sep) + 1:]
                    final_chunks.extend(split_text(chunk, remaining_seps))
                else:
                    final_chunks.append(chunk)

            return final_chunks

        return [text]

    return split_text(text, separators)


# Compare fixed vs recursive chunking
print("=== Fixed-Size Chunking ===")
fixed_chunks = fixed_size_chunk(sample_text, chunk_size=300, overlap=0)
for i, chunk in enumerate(fixed_chunks):
    print(f"Chunk {i + 1}: {chunk[:60]}...")
    # Check if chunk ends mid-sentence
    if not chunk.rstrip().endswith(('.', '!', '?', '"')):
        print(f"  WARNING: Chunk ends mid-sentence!")
    print()

print("\n=== Recursive Chunking ===")
recursive_chunks = recursive_chunk(sample_text, chunk_size=300)
for i, chunk in enumerate(recursive_chunks):
    print(f"Chunk {i + 1}: {chunk[:60]}...")
    if not chunk.rstrip().endswith(('.', '!', '?', '"')):
        print(f"  Note: Ends at paragraph boundary")
    print()
```

**Output:**
```
=== Fixed-Size Chunking ===
Chunk 1: The history of artificial intelligence began in the 1950s...
  WARNING: Chunk ends mid-sentence!

Chunk 2: ked whether machines
could exhibit intelligent behavior i...
  WARNING: Chunk ends mid-sentence!

Chunk 3: arly considered the birth of AI as a field. Researchers we...
  WARNING: Chunk ends mid-sentence!

Chunk 4: cond AI Winter in the late 1980s.

The modern era of AI be...
  WARNING: Chunk ends mid-sentence!


=== Recursive Chunking ===
Chunk 1: The history of artificial intelligence began in the 1950s...

Chunk 2: In 1956, John McCarthy organized the Dartmouth Conference...

Chunk 3: The 1960s and 1970s saw early successes in AI, including ...

Chunk 4: The 1980s brought expert systems, which encoded human kno...

Chunk 5: The modern era of AI began with the rise of machine learn...
```

**Line-by-line explanation:**

- The function tries splitting on paragraph breaks (`\n\n`) first. Paragraphs are natural content boundaries.
- If paragraphs are too large, it tries single newlines, then sentences (`. `), then words (` `), and finally characters.
- This produces cleaner chunks that preserve meaning. Notice that recursive chunks start at sentence boundaries, while fixed chunks cut sentences in half.
- This is the most commonly used chunking strategy in production RAG systems.

---

## Chunking Strategy 3: Semantic Chunking

Semantic chunking groups text by meaning rather than by size.

```python
def semantic_chunk_by_headers(text):
    """
    Split text by headers/sections.
    Each section becomes its own chunk.
    """
    import re

    # Find sections marked by common header patterns
    # Supports: "Chapter X:", "Section X:", "## Header", numbered headers
    header_pattern = r'(?=(?:Chapter \d+|Section \d+|#{1,3} |\d+\.\s+[A-Z]))'

    sections = re.split(header_pattern, text)
    sections = [s.strip() for s in sections if s.strip()]

    return sections

def semantic_chunk_by_topic(paragraphs, max_chunk_size=500):
    """
    Group related paragraphs together based on simple heuristics.

    In production, you would use embeddings to measure similarity
    between paragraphs and group similar ones together.
    """
    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        # Check if adding this paragraph exceeds the limit
        if len(current_chunk) + len(paragraph) > max_chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = paragraph
        else:
            current_chunk += "\n\n" + paragraph if current_chunk else paragraph

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


# Example with headers
document_with_headers = """
Chapter 1: Getting Started

Welcome to our platform. This guide will help you set up your account
and start using our services. Follow the steps below carefully.

To create an account, visit our website and click the Sign Up button.
Enter your email address and create a strong password.

Chapter 2: Dashboard Overview

The dashboard is your main control center. Here you can see all your
projects, recent activity, and notifications.

The left sidebar contains navigation links to different sections:
Projects, Analytics, Settings, and Help.

Chapter 3: Advanced Features

Power users can take advantage of our API for custom integrations.
API documentation is available at docs.example.com.

You can also set up webhooks to receive real-time notifications
when events occur in your account.
"""

print("=== Semantic Chunking by Headers ===")
header_chunks = semantic_chunk_by_headers(document_with_headers)
for i, chunk in enumerate(header_chunks):
    lines = chunk.strip().split('\n')
    title = lines[0] if lines else "No title"
    print(f"\nChunk {i + 1}: '{title}'")
    print(f"  Length: {len(chunk)} characters")
    print(f"  Paragraphs: {chunk.count(chr(10) + chr(10)) + 1}")
```

**Output:**
```
=== Semantic Chunking by Headers ===

Chunk 1: 'Chapter 1: Getting Started'
  Length: 274 characters
  Paragraphs: 3

Chunk 2: 'Chapter 2: Dashboard Overview'
  Length: 260 characters
  Paragraphs: 3

Chunk 3: 'Chapter 3: Advanced Features'
  Length: 247 characters
  Paragraphs: 3
```

**Line-by-line explanation:**

- `semantic_chunk_by_headers()` splits on section headings. Each section becomes one chunk, keeping all related content together.
- The regex `header_pattern` looks for common header formats like "Chapter 1:", "## Header", or numbered sections.
- `re.split(header_pattern, text)` splits the text at each header while keeping the header with its content.
- This is the most meaningful chunking strategy because sections are written to be self-contained units of information.

---

## Choosing Chunk Size and Overlap

Chunk size and overlap significantly affect RAG quality.

```python
def analyze_chunk_settings(text, settings):
    """
    Compare different chunk size and overlap settings.
    """
    print(f"Text length: {len(text)} characters")
    print(f"{'Setting':<25} {'Chunks':<8} {'Avg Size':<10} {'Min':<6} {'Max':<6}")
    print("-" * 55)

    for chunk_size, overlap in settings:
        chunks = fixed_size_chunk(text, chunk_size, overlap)
        sizes = [len(c) for c in chunks]

        label = f"size={chunk_size}, overlap={overlap}"
        avg = sum(sizes) / len(sizes)
        print(f"{label:<25} {len(chunks):<8} {avg:<10.0f} "
              f"{min(sizes):<6} {max(sizes):<6}")

# Test different settings
settings = [
    (100, 0),
    (100, 20),
    (250, 0),
    (250, 50),
    (500, 0),
    (500, 100),
    (1000, 0),
    (1000, 200),
]

analyze_chunk_settings(sample_text, settings)

print("""
CHUNK SIZE GUIDELINES:
+------------------------------------------------------------------+
| Chunk Size  | Best For                | Trade-off                 |
|-------------|-------------------------|---------------------------|
| 100-200     | Precise retrieval,      | May lose context,         |
|             | short answers           | more chunks to search     |
|             |                         |                           |
| 300-500     | General purpose,        | Good balance of           |
|             | most RAG systems        | context and precision     |
|             |                         |                           |
| 500-1000    | Complex topics,         | May include irrelevant    |
|             | longer context needed   | text, fewer chunks        |
|             |                         |                           |
| 1000+       | Summaries, topics       | Less precise retrieval,   |
|             | needing broad context   | expensive per retrieval   |
+------------------------------------------------------------------+

OVERLAP GUIDELINES:
- 10-20% of chunk size is a good starting point
- More overlap = better coverage but more storage
- Zero overlap risks losing information at boundaries
""")
```

**Output:**
```
Text length: 1062 characters
Setting                  Chunks   Avg Size   Min    Max
-------------------------------------------------------
size=100, overlap=0      11       96         62     100
size=100, overlap=20     14       97         62     100
size=250, overlap=0      5        212        62     250
size=250, overlap=50     6        227        78     250
size=500, overlap=0      3        354        62     500
size=500, overlap=100    3        400        162    500
size=1000, overlap=0     2        531        62     1000
size=1000, overlap=200   2        594        188    1000

CHUNK SIZE GUIDELINES:
+------------------------------------------------------------------+
| Chunk Size  | Best For                | Trade-off                 |
|-------------|-------------------------|---------------------------|
| 100-200     | Precise retrieval,      | May lose context,         |
|             | short answers           | more chunks to search     |
|             |                         |                           |
| 300-500     | General purpose,        | Good balance of           |
|             | most RAG systems        | context and precision     |
|             |                         |                           |
| 500-1000    | Complex topics,         | Less precise retrieval,   |
|             | longer context needed   | fewer chunks              |
|             |                         |                           |
| 1000+       | Summaries, topics       | Less precise retrieval,   |
|             | needing broad context   | expensive per retrieval   |
+------------------------------------------------------------------+

OVERLAP GUIDELINES:
- 10-20% of chunk size is a good starting point
- More overlap = better coverage but more storage
- Zero overlap risks losing information at boundaries
```

---

## Complete Document Processing Pipeline

Let us build a complete pipeline that handles multiple document types.

```python
import os
import re

class DocumentProcessor:
    """Process documents from various formats into chunks for RAG."""

    def __init__(self, chunk_size=500, chunk_overlap=50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def process_file(self, filepath):
        """
        Process a single file and return chunks with metadata.
        """
        extension = os.path.splitext(filepath)[1].lower()

        if extension == '.txt':
            text = self._read_text_file(filepath)
        elif extension == '.html' or extension == '.htm':
            text = self._read_html_file(filepath)
        elif extension == '.pdf':
            text = self._read_pdf_file(filepath)
        else:
            raise ValueError(f"Unsupported file type: {extension}")

        # Clean the text
        text = self._clean_text(text)

        # Chunk the text
        chunks = self._recursive_chunk(text)

        # Add metadata to each chunk
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            processed_chunks.append({
                "text": chunk,
                "source": filepath,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "char_count": len(chunk),
                "word_count": len(chunk.split()),
            })

        return processed_chunks

    def _read_text_file(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def _read_html_file(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            html = f.read()
        soup = BeautifulSoup(html, 'html.parser')
        for tag in soup.find_all(['script', 'style']):
            tag.decompose()
        return soup.get_text(separator='\n')

    def _read_pdf_file(self, filepath):
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
        return text

    def _clean_text(self, text):
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        lines = [line.strip() for line in text.splitlines()]
        return '\n'.join(lines).strip()

    def _recursive_chunk(self, text):
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
                    if current:
                        chunks.append(current.strip())
                    current = part

            if current:
                chunks.append(current.strip())

            if chunks:
                return chunks

        # Fallback: fixed size
        return fixed_size_chunk(text, self.chunk_size, self.chunk_overlap)


# Demonstrate the pipeline
processor = DocumentProcessor(chunk_size=300, chunk_overlap=30)

# Simulate processing
sample_doc = """
Introduction to Machine Learning

Machine learning is a branch of artificial intelligence that focuses on
building systems that learn from data. Instead of being explicitly
programmed, these systems improve their performance through experience.

Types of Machine Learning

There are three main types of machine learning:

Supervised Learning: The model learns from labeled examples. You provide
input-output pairs, and the model learns the mapping between them.
Common tasks include classification and regression.

Unsupervised Learning: The model finds patterns in unlabeled data.
There are no correct answers provided. Common tasks include clustering
and dimensionality reduction.

Reinforcement Learning: The model learns by interacting with an
environment and receiving rewards or penalties. It is used in robotics,
game playing, and autonomous vehicles.

Applications

Machine learning is used in many fields: healthcare for diagnosis,
finance for fraud detection, technology for recommendation systems,
and transportation for self-driving cars.
"""

# Simulate file processing by directly chunking
chunks = processor._recursive_chunk(processor._clean_text(sample_doc))

print(f"Document: {len(sample_doc)} characters")
print(f"Chunks:   {len(chunks)}")
print()

for i, chunk in enumerate(chunks):
    print(f"--- Chunk {i + 1} ({len(chunk)} chars, {len(chunk.split())} words) ---")
    print(chunk[:80] + "..." if len(chunk) > 80 else chunk)
    print()
```

**Output:**
```
Document: 1049 characters
Chunks:   4

--- Chunk 1 (278 chars, 45 words) ---
Introduction to Machine Learning

Machine learning is a branch of artificial in...

--- Chunk 2 (277 chars, 42 words) ---
Types of Machine Learning

There are three main types of machine learning:

Supe...

--- Chunk 3 (259 chars, 39 words) ---
Unsupervised Learning: The model finds patterns in unlabeled data.
There are no...

--- Chunk 4 (207 chars, 34 words) ---
Applications

Machine learning is used in many fields: healthcare for diagnosis,...
```

---

## Common Mistakes

1. **Splitting mid-sentence.** Fixed-size chunking often cuts sentences in half. Use recursive chunking to split on natural boundaries.

2. **Chunks too small.** Chunks under 100 characters often lack enough context for the LLM to understand them. Aim for at least 200-500 characters.

3. **Chunks too large.** Chunks over 2000 characters waste tokens on irrelevant content and make retrieval less precise.

4. **Zero overlap.** Without overlap, information at chunk boundaries gets lost. Use at least 10% overlap.

5. **Not cleaning text before chunking.** Extra whitespace, headers, footers, and formatting artifacts create noisy chunks that hurt retrieval quality.

6. **Ignoring document structure.** Many documents have natural sections (chapters, headings). Splitting on these boundaries produces more meaningful chunks than arbitrary size splits.

---

## Best Practices

1. **Use recursive chunking as your default.** It handles most documents well by respecting natural text boundaries.

2. **Start with 300-500 character chunks.** This is a good default for most RAG applications. Adjust based on your specific use case.

3. **Add metadata to every chunk.** Store the source document, page number, section heading, and chunk index. This enables source citations.

4. **Test chunk quality manually.** Read 20-30 chunks and ask: "Does this chunk make sense on its own?" If not, adjust your strategy.

5. **Preserve section headings in chunks.** When splitting by sections, include the heading in each chunk so the LLM knows the topic.

6. **Handle different file types.** Build a pipeline that automatically detects file type and uses the right extraction method.

---

## Quick Summary

Document processing is the foundation of any RAG system. You extract text from various formats (PDF, HTML, plain text), clean it, and split it into chunks. Fixed-size chunking is simple but breaks sentences. Recursive chunking respects natural boundaries. Semantic chunking groups by meaning. Chunk size and overlap are critical parameters: too small loses context, too large wastes tokens. The right chunking strategy dramatically affects RAG quality.

---

## Key Points

- **Chunking** splits documents into small pieces for retrieval
- **PyPDF2** extracts text from PDF files
- **BeautifulSoup** extracts clean text from HTML pages
- **Fixed-size chunking** is simple but often splits mid-sentence
- **Recursive chunking** tries paragraph, sentence, and word boundaries first
- **Semantic chunking** splits by document sections or topic changes
- **Chunk size** of 300-500 characters is a good starting point
- **Overlap** of 10-20% prevents information loss at boundaries
- **Metadata** (source, page, section) enables source citations

---

## Practice Questions

1. Why can you not just put an entire 100-page document into the LLM prompt instead of chunking it?

2. What is the difference between fixed-size chunking and recursive chunking? When would you prefer one over the other?

3. You have a technical manual with clear chapter headings. Which chunking strategy would you use and why?

4. Your RAG system is returning incomplete answers. You suspect the relevant information is being split across two chunks. What two parameters would you adjust?

5. Why is it important to add metadata (like source file and page number) to each chunk?

---

## Exercises

**Exercise 1: Multi-Format Processor**

Build a document processor that can handle `.txt`, `.html`, and `.csv` files. For CSV files, convert each row into a descriptive text chunk. Process at least one file of each type and display the resulting chunks with metadata.

**Exercise 2: Chunk Quality Analyzer**

Write a function that analyzes the quality of chunks. For each chunk, check: (1) Does it start mid-sentence? (2) Does it end mid-sentence? (3) Is it under 50 characters (too small)? (4) Is it over 2000 characters (too large)? Report a quality score for the entire chunking.

**Exercise 3: Chunking Strategy Comparison**

Take a 2000+ character document and chunk it using all three strategies (fixed-size, recursive, and semantic). For each strategy, report: number of chunks, average chunk size, number of chunks that start or end mid-sentence. Which strategy produces the best results for your document?

---

## What Is Next?

Now that you can process documents into chunks, you need a way to find which chunks are relevant to a user's question. Simple keyword matching is not good enough. In Chapter 15, you will learn about embeddings, which are numbers that capture the meaning of text. Embeddings let you find relevant chunks even when the user's question uses completely different words than the document.
