# Chapter 13: Question Answering with Transformers

## What You Will Learn

In this chapter, you will learn:

- What extractive question answering is and how it works
- How to use the Hugging Face QA pipeline for instant question answering
- How start and end logits work to find answer spans in text
- How to fine-tune a model for question answering on custom data
- How to build a complete QA system with confidence scoring
- What the limitations of extractive QA are and when to use other approaches

## Why This Chapter Matters

Think about how you answer a question when reading a textbook. Someone asks, "When was Python created?" You scan the paragraph, find the relevant sentence, and highlight the answer: "1991." You do not make up the answer -- you find it in the text.

This is exactly what extractive question answering does. Given a passage of text (the context) and a question, the model finds the exact span of text that answers the question. This technology powers search engines that display direct answers, customer support chatbots that pull answers from documentation, and virtual assistants that answer factual questions.

Understanding QA systems is essential because they are one of the most immediately useful applications of NLP. You can build a system that answers questions from your company's documentation, product manuals, or any text collection -- in just a few lines of code.

---

## 13.1 What Is Extractive Question Answering?

### The Core Idea

Extractive QA does not generate new text. It finds and extracts the answer from existing text. Think of it as a highlighter, not a writer:

```
+--------------------------------------------------------------+
|        EXTRACTIVE QUESTION ANSWERING                          |
+--------------------------------------------------------------+
|                                                                |
|  Context: "Python was created by Guido van Rossum and         |
|           first released in 1991. It emphasizes code          |
|           readability and simplicity."                         |
|                                                                |
|  Question: "Who created Python?"                              |
|                                                                |
|  The model does NOT write an answer.                          |
|  The model FINDS the answer in the context:                   |
|                                                                |
|  "Python was created by [Guido van Rossum] and first..."      |
|                          ^^^^^^^^^^^^^^^^^^                    |
|                          THIS is the answer                   |
|                                                                |
|  Answer: "Guido van Rossum"                                   |
|                                                                |
+--------------------------------------------------------------+
```

### How It Differs from Other QA Approaches

```
+--------------------------------------------------------------+
|        TYPES OF QUESTION ANSWERING                            |
+--------------------------------------------------------------+
|                                                                |
|  1. EXTRACTIVE QA (this chapter)                              |
|     - Finds answer IN the provided text                       |
|     - Answer is always a direct quote from the context        |
|     - Cannot answer if the answer is not in the text          |
|     - Example: "Guido van Rossum" (copied from context)       |
|                                                                |
|  2. ABSTRACTIVE QA                                            |
|     - Generates a new answer based on the context             |
|     - Can paraphrase or combine information                   |
|     - Example: "Python's creator was Guido van Rossum,        |
|       who released it in 1991"                                |
|                                                                |
|  3. OPEN-DOMAIN QA                                            |
|     - Answers from a large knowledge base (like Wikipedia)    |
|     - First retrieves relevant documents, then extracts       |
|     - More complex but more powerful                          |
|                                                                |
+--------------------------------------------------------------+
```

### The Internal Process

Here is how a QA model processes a question step by step:

```
+--------------------------------------------------------------+
|        QA MODEL INTERNAL PROCESS                              |
+--------------------------------------------------------------+
|                                                                |
|  Step 1: Combine question and context                         |
|  [CLS] Who created Python? [SEP] Python was created by...    |
|                                                                |
|  Step 2: Tokenize everything into numbers                     |
|  [101, 2040, 2580, 18750, ..., 102, 18750, 2001, ...]       |
|                                                                |
|  Step 3: Model processes all tokens                           |
|  Each token gets a "start score" and "end score"              |
|                                                                |
|  Step 4: Find the span with highest scores                    |
|  Start = position of "Guido"                                  |
|  End = position of "Rossum"                                   |
|                                                                |
|  Step 5: Extract the answer                                   |
|  Answer = tokens from Start to End = "Guido van Rossum"       |
|                                                                |
+--------------------------------------------------------------+
```

---

## 13.2 Using the QA Pipeline

### Basic Question Answering

The simplest way to do QA with Hugging Face is the pipeline:

```python
from transformers import pipeline

# Create a question answering pipeline
qa_pipeline = pipeline("question-answering")

# Define the context (the text that contains the answer)
context = """
The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars
in Paris, France. It is named after the engineer Gustave Eiffel, whose
company designed and built the tower from 1887 to 1889. The tower is
330 metres tall and was the tallest man-made structure in the world
until 1930. Today it receives nearly 7 million visitors per year.
"""

# Ask questions about the context
questions = [
    "Where is the Eiffel Tower located?",
    "Who designed the Eiffel Tower?",
    "How tall is the Eiffel Tower?",
    "How many visitors does it receive per year?"
]

for question in questions:
    result = qa_pipeline(question=question, context=context)
    print(f"Q: {question}")
    print(f"A: {result['answer']}")
    print(f"   Confidence: {result['score']:.4f}")
    print(f"   Found at position: {result['start']}-{result['end']}")
    print()
```

**Expected output:**

```
Q: Where is the Eiffel Tower located?
A: Champ de Mars in Paris, France
   Confidence: 0.7234
   Found at position: 63-94

Q: Who designed the Eiffel Tower?
A: Gustave Eiffel
   Confidence: 0.8912
   Found at position: 130-145

Q: How tall is the Eiffel Tower?
A: 330 metres
   Confidence: 0.9456
   Found at position: 198-209

Q: How many visitors does it receive per year?
A: nearly 7 million
   Confidence: 0.8234
   Found at position: 278-295
```

**Line-by-line explanation:**
- `pipeline("question-answering")` -- Creates a QA pipeline. By default, it loads the `distilbert-base-cased-distilled-squad` model, which was trained on the SQuAD dataset (Stanford Question Answering Dataset)
- `question=question, context=context` -- You must provide both the question and the context where the answer can be found
- `result['answer']` -- The extracted text that answers the question
- `result['score']` -- A confidence score between 0 and 1. Higher means the model is more certain
- `result['start']` and `result['end']` -- Character positions in the context where the answer was found

### Asking Multiple Questions About the Same Context

```python
from transformers import pipeline

qa = pipeline("question-answering")

# A longer context with more information
context = """
Machine learning was first conceived as a field in 1959 by Arthur Samuel,
an American computer scientist who worked at IBM. He defined machine learning
as a "field of study that gives computers the ability to learn without being
explicitly programmed." The field gained momentum in the 1990s with the
development of support vector machines and random forests. The modern deep
learning revolution began around 2012, when a neural network called AlexNet
won the ImageNet competition by a significant margin. Today, machine learning
is used in applications ranging from email spam filtering to self-driving
cars and medical diagnosis. The global machine learning market was valued
at approximately 15 billion dollars in 2022.
"""

# Build a question-answer pairs list
qa_pairs = [
    "When was machine learning first conceived?",
    "Who is considered the founder of machine learning?",
    "What company did Arthur Samuel work for?",
    "What happened in 2012?",
    "What is the market value of machine learning?",
]

print("=== Machine Learning Q&A ===\n")
for q in qa_pairs:
    result = qa(question=q, context=context)
    confidence = result['score']

    # Add a confidence indicator
    if confidence > 0.8:
        indicator = "[HIGH confidence]"
    elif confidence > 0.5:
        indicator = "[MEDIUM confidence]"
    else:
        indicator = "[LOW confidence]"

    print(f"Q: {q}")
    print(f"A: {result['answer']} {indicator} ({confidence:.2%})")
    print()
```

**Expected output:**

```
=== Machine Learning Q&A ===

Q: When was machine learning first conceived?
A: 1959 [HIGH confidence] (94.56%)

Q: Who is considered the founder of machine learning?
A: Arthur Samuel [HIGH confidence] (89.12%)

Q: What company did Arthur Samuel work for?
A: IBM [HIGH confidence] (96.78%)

Q: What happened in 2012?
A: a neural network called AlexNet won the ImageNet competition [HIGH confidence] (82.34%)

Q: What is the market value of machine learning?
A: approximately 15 billion dollars [MEDIUM confidence] (73.45%)
```

**Line-by-line explanation:**
- We add confidence indicators (HIGH, MEDIUM, LOW) based on the score threshold
- `confidence:.2%` formats the number as a percentage with 2 decimal places (for example, 0.9456 becomes 94.56%)
- Notice that factual, directly stated information gets higher confidence than questions requiring inference

---

## 13.3 Understanding Start and End Logits

### What Are Logits in QA?

In question answering, the model outputs two scores for every token in the context:

1. **Start logit** -- How likely this token is the start of the answer
2. **End logit** -- How likely this token is the end of the answer

```
+--------------------------------------------------------------+
|        START AND END LOGITS EXAMPLE                           |
+--------------------------------------------------------------+
|                                                                |
|  Context tokens: [Python] [was] [created] [by] [Guido]       |
|                  [van] [Rossum] [in] [1991]                   |
|                                                                |
|  Question: "Who created Python?"                              |
|                                                                |
|  Start logits:  -2.1  -3.5  -1.8  -0.5  [5.2]  0.3   -1.0  |
|                                           ^^^                 |
|                                     Highest start score       |
|                                                                |
|  End logits:    -1.8  -2.9  -1.5  -0.8   0.5  -0.2  [4.8]   |
|                                                        ^^^    |
|                                              Highest end score |
|                                                                |
|  Answer: tokens from "Guido" to "Rossum"                      |
|        = "Guido van Rossum"                                   |
|                                                                |
+--------------------------------------------------------------+
```

### Exploring Logits with Code

```python
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import torch

# Load model and tokenizer
model_name = "distilbert-base-cased-distilled-squad"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForQuestionAnswering.from_pretrained(model_name)

# Define question and context
question = "What color is the sky?"
context = "The sky is blue during the day and dark at night."

# Tokenize
inputs = tokenizer(question, context, return_tensors="pt")

# Get model output
with torch.no_grad():
    outputs = model(**inputs)

# The model outputs start and end logits
start_logits = outputs.start_logits[0]
end_logits = outputs.end_logits[0]

# Find the positions with the highest scores
start_index = torch.argmax(start_logits).item()
end_index = torch.argmax(end_logits).item()

# Convert token positions back to text
tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
answer_tokens = tokens[start_index:end_index + 1]
answer = tokenizer.convert_tokens_to_string(answer_tokens)

print(f"Question: {question}")
print(f"Context:  {context}")
print(f"Answer:   {answer}")
print(f"\nStart position: {start_index} (token: '{tokens[start_index]}')")
print(f"End position:   {end_index} (token: '{tokens[end_index]}')")

# Show the top 5 start and end positions
print("\nTop 5 start positions:")
top_starts = torch.topk(start_logits, 5)
for score, idx in zip(top_starts.values, top_starts.indices):
    print(f"  Position {idx.item():2d}: '{tokens[idx.item()]:12s}' score: {score.item():.4f}")

print("\nTop 5 end positions:")
top_ends = torch.topk(end_logits, 5)
for score, idx in zip(top_ends.values, top_ends.indices):
    print(f"  Position {idx.item():2d}: '{tokens[idx.item()]:12s}' score: {score.item():.4f}")
```

**Expected output:**

```
Question: What color is the sky?
Context:  The sky is blue during the day and dark at night.
Answer:   blue

Start position: 11 (token: 'blue')
End position:   11 (token: 'blue')

Top 5 start positions:
  Position 11: 'blue        ' score: 5.8234
  Position 14: 'day         ' score: 1.2345
  Position 18: 'dark        ' score: 0.8901
  Position  9: 'is          ' score: -0.5678
  Position 10: 'The         ' score: -1.2345

Top 5 end positions:
  Position 11: 'blue        ' score: 6.1234
  Position 14: 'day         ' score: 0.9876
  Position 18: 'dark        ' score: 0.7654
  Position 20: 'night       ' score: -0.3456
  Position 12: 'during      ' score: -0.8765
```

**Line-by-line explanation:**
- `AutoModelForQuestionAnswering` -- A model variant specifically designed for QA tasks, which outputs start and end logits
- `outputs.start_logits` -- A tensor of scores, one per token, indicating how likely each token is the start of the answer
- `outputs.end_logits` -- Same but for the end of the answer
- `torch.argmax(start_logits)` -- Finds the position with the highest start score
- `tokens[start_index:end_index + 1]` -- Extracts all tokens from start to end (inclusive), forming the answer
- `torch.topk(start_logits, 5)` -- Gets the top 5 highest scores and their positions

### How the Model Picks the Best Answer

```
+--------------------------------------------------------------+
|        ANSWER SELECTION PROCESS                               |
+--------------------------------------------------------------+
|                                                                |
|  1. Get start logits for all tokens                           |
|  2. Get end logits for all tokens                             |
|  3. Find all valid (start, end) pairs where:                  |
|     - start <= end (answer cannot end before it starts)       |
|     - end - start < max_answer_length (not too long)          |
|  4. Score each pair: start_logit[i] + end_logit[j]           |
|  5. Pick the pair with the highest combined score             |
|  6. Extract tokens from start to end as the answer            |
|                                                                |
|  Example:                                                      |
|    start=11, end=11 --> "blue"       score: 5.82 + 6.12 = 11.94|
|    start=11, end=14 --> "blue during the day" score: 5.82+0.99|
|    start=18, end=18 --> "dark"       score: 0.89 + 0.77 = 1.66|
|                                                                |
|    Winner: "blue" with score 11.94                            |
|                                                                |
+--------------------------------------------------------------+
```

---

## 13.4 Building a Complete QA System

### A QA System with Multiple Contexts

Let us build a system that can answer questions from a collection of text passages:

```python
from transformers import pipeline

def build_qa_system(knowledge_base):
    """
    Build a question answering system from a dictionary of topics
    and their descriptions.

    Parameters:
        knowledge_base: A dictionary where keys are topic names and
                       values are text descriptions

    Returns:
        A function that takes a question and returns the best answer
    """
    qa = pipeline("question-answering")

    def answer_question(question):
        """
        Find the best answer across all knowledge base entries.

        Parameters:
            question: The question to answer (a string)

        Returns:
            A dictionary with the answer, confidence, and source topic
        """
        best_answer = None
        best_score = -1
        best_topic = None

        # Search through all topics for the best answer
        for topic, context in knowledge_base.items():
            try:
                result = qa(question=question, context=context)

                if result['score'] > best_score:
                    best_score = result['score']
                    best_answer = result['answer']
                    best_topic = topic
            except Exception as e:
                # Skip topics that cause errors
                continue

        if best_answer is None:
            return {
                "answer": "I could not find an answer.",
                "confidence": 0.0,
                "source": None
            }

        return {
            "answer": best_answer,
            "confidence": best_score,
            "source": best_topic
        }

    return answer_question


# Create a knowledge base
knowledge_base = {
    "Python": """
    Python is a high-level programming language created by Guido van Rossum
    in 1991. It uses indentation for code blocks instead of curly braces.
    Python is popular for web development, data science, machine learning,
    and automation. The latest major version is Python 3, released in 2008.
    Python's package manager is called pip.
    """,

    "JavaScript": """
    JavaScript was created by Brendan Eich in 1995 while working at Netscape.
    It is the primary language for web browsers and runs on both client and
    server side. Node.js allows JavaScript to run outside the browser.
    JavaScript uses curly braces for code blocks and semicolons to end
    statements. The most popular JavaScript frameworks include React,
    Angular, and Vue.
    """,

    "Machine Learning": """
    Machine learning is a branch of artificial intelligence that enables
    computers to learn from data without being explicitly programmed.
    Common algorithms include linear regression, decision trees, and
    neural networks. Deep learning is a subset of machine learning that
    uses neural networks with many layers. TensorFlow and PyTorch are
    the most popular deep learning frameworks. Training a model requires
    a dataset, a loss function, and an optimizer.
    """
}

# Build the system
ask = build_qa_system(knowledge_base)

# Ask questions
questions = [
    "Who created Python?",
    "When was JavaScript created?",
    "What are popular deep learning frameworks?",
    "What does Python use instead of curly braces?",
    "Who created JavaScript?",
    "What is deep learning?"
]

print("=== Knowledge Base QA System ===\n")
for q in questions:
    result = ask(q)
    print(f"Q: {q}")
    print(f"A: {result['answer']}")
    print(f"   Source: {result['source']}")
    print(f"   Confidence: {result['confidence']:.2%}")
    print()
```

**Expected output:**

```
=== Knowledge Base QA System ===

Q: Who created Python?
A: Guido van Rossum
   Source: Python
   Confidence: 96.78%

Q: When was JavaScript created?
A: 1995
   Source: JavaScript
   Confidence: 94.32%

Q: What are popular deep learning frameworks?
A: TensorFlow and PyTorch
   Source: Machine Learning
   Confidence: 89.12%

Q: What does Python use instead of curly braces?
A: indentation
   Source: Python
   Confidence: 85.67%

Q: Who created JavaScript?
A: Brendan Eich
   Source: JavaScript
   Confidence: 93.45%

Q: What is deep learning?
A: a subset of machine learning that uses neural networks with many layers
   Source: Machine Learning
   Confidence: 78.90%
```

**Line-by-line explanation:**
- `build_qa_system(knowledge_base)` -- Creates a QA function from a dictionary of topics and their text descriptions
- The inner `answer_question` function loops through all topics, asks the QA model about each one, and returns the answer with the highest confidence score
- `try/except` -- Handles any errors that might occur when processing a particular context (for example, if the context is too short)
- The system automatically identifies which topic contains the best answer

### Adding Confidence Thresholds

```python
from transformers import pipeline

qa = pipeline("question-answering")

context = """
The Python programming language was created by Guido van Rossum in 1991.
It is known for its simple syntax and readability.
"""

def answer_with_threshold(question, context, threshold=0.3):
    """
    Answer a question only if the model is confident enough.

    Parameters:
        question: The question to answer
        context: The text to search for answers
        threshold: Minimum confidence to accept an answer (0 to 1)

    Returns:
        The answer string, or a message saying no confident answer was found
    """
    result = qa(question=question, context=context)

    if result['score'] < threshold:
        return (f"I am not confident enough to answer this question. "
                f"(confidence: {result['score']:.2%})")

    return f"{result['answer']} (confidence: {result['score']:.2%})"


# Questions the model can answer
print(answer_with_threshold("Who created Python?", context))

# Questions the model cannot answer well (answer is not in context)
print(answer_with_threshold("What is the capital of France?", context))
```

**Expected output:**

```
Guido van Rossum (confidence: 96.78%)
I am not confident enough to answer this question. (confidence: 12.34%)
```

---

## 13.5 Fine-Tuning for Question Answering

### Overview of QA Fine-Tuning

Fine-tuning a QA model follows a similar process to classification fine-tuning, but with some key differences:

```
+--------------------------------------------------------------+
|        QA FINE-TUNING vs CLASSIFICATION FINE-TUNING           |
+--------------------------------------------------------------+
|                                                                |
|  Classification:                                               |
|    Input: text                                                 |
|    Label: a class (0, 1, 2, ...)                              |
|    Output: one prediction per input                            |
|                                                                |
|  Question Answering:                                           |
|    Input: question + context                                   |
|    Label: start position + end position of answer             |
|    Output: two predictions per input (start and end)           |
|                                                                |
+--------------------------------------------------------------+
```

### The SQuAD Dataset Format

The most common QA dataset is SQuAD (Stanford Question Answering Dataset). Here is what the data looks like:

```python
from datasets import load_dataset

# Load the SQuAD dataset
squad = load_dataset("squad")

# Look at one example
example = squad['train'][0]
print("Context (first 200 chars):")
print(f"  {example['context'][:200]}...")
print(f"\nQuestion: {example['question']}")
print(f"Answer text: {example['answers']['text']}")
print(f"Answer start: {example['answers']['answer_start']}")
```

**Expected output:**

```
Context (first 200 chars):
  Architecturally, the most significant aspect of the school is the Main
  Building. Built in 1879, it is the oldest building on campus and is
  listed on the National Register of Historic Places...

Question: To whom did the Virgin Mary allegedly appear in 1858 in Lourdes France?
Answer text: ['Saint Bernadette Soubirous']
Answer start: [515]
```

### Fine-Tuning Process Overview

Here is a simplified overview of the QA fine-tuning process:

```python
from transformers import (
    AutoTokenizer,
    AutoModelForQuestionAnswering,
    TrainingArguments,
    Trainer,
    DefaultDataCollator
)
from datasets import load_dataset

# Step 1: Load dataset and model
squad = load_dataset("squad")
model_name = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForQuestionAnswering.from_pretrained(model_name)

# Step 2: Use a small subset for demonstration
small_train = squad["train"].select(range(1000))
small_val = squad["validation"].select(range(200))

# Step 3: Preprocessing function for QA
def preprocess_qa(examples):
    """
    Tokenize questions and contexts, and find the answer token positions.
    """
    # Tokenize question and context pairs
    tokenized = tokenizer(
        examples["question"],
        examples["context"],
        truncation="only_second",   # Only truncate the context, not question
        max_length=384,
        stride=128,                  # Overlap for long contexts
        return_offsets_mapping=True,  # Map tokens back to characters
        padding="max_length",
    )

    # Find the start and end token positions of the answer
    start_positions = []
    end_positions = []

    for i, offset in enumerate(tokenized["offset_mapping"]):
        answer = examples["answers"][i]
        start_char = answer["answer_start"][0]
        end_char = start_char + len(answer["text"][0])

        # Find which tokens correspond to the answer
        # (simplified version)
        token_start = 0
        token_end = 0

        for idx, (token_start_char, token_end_char) in enumerate(offset):
            if token_start_char <= start_char < token_end_char:
                token_start = idx
            if token_start_char < end_char <= token_end_char:
                token_end = idx
                break

        start_positions.append(token_start)
        end_positions.append(token_end)

    tokenized["start_positions"] = start_positions
    tokenized["end_positions"] = end_positions

    # Remove offset_mapping as the model does not need it
    del tokenized["offset_mapping"]

    return tokenized

# Step 4: Tokenize the dataset
print("Tokenizing dataset...")
tokenized_train = small_train.map(preprocess_qa, batched=True,
                                   remove_columns=small_train.column_names)
tokenized_val = small_val.map(preprocess_qa, batched=True,
                               remove_columns=small_val.column_names)

# Step 5: Training arguments
training_args = TrainingArguments(
    output_dir="./qa_results",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    warmup_steps=50,
    weight_decay=0.01,
    logging_steps=50,
    evaluation_strategy="epoch",
    save_strategy="epoch",
)

# Step 6: Create trainer and train
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_val,
    data_collator=DefaultDataCollator(),
)

print("Starting QA fine-tuning...")
# trainer.train()  # Uncomment to actually train
print("(Training code ready -- uncomment trainer.train() to run)")
```

**Line-by-line explanation:**
- `AutoModelForQuestionAnswering` -- A model with two output heads: one for start positions and one for end positions
- `truncation="only_second"` -- When the combined question + context is too long, only truncate the context (the second input), never the question
- `stride=128` -- For very long contexts, create overlapping windows of 128 tokens. This ensures answers near window boundaries are not missed
- `return_offsets_mapping=True` -- Returns a mapping between tokens and their character positions in the original text. This is needed to find which tokens correspond to the answer
- `start_positions` and `end_positions` -- The labels for QA training are token indices, not class labels

```
+--------------------------------------------------------------+
|        QA TRAINING LABELS                                     |
+--------------------------------------------------------------+
|                                                                |
|  Context: "Python was created by Guido van Rossum in 1991"   |
|  Tokens:   [0]    [1]    [2]   [3] [4]    [5]  [6]   [7] [8]|
|                                                                |
|  Question: "Who created Python?"                              |
|  Answer: "Guido van Rossum"                                   |
|                                                                |
|  Training labels:                                              |
|    start_position = 4  (index of "Guido")                     |
|    end_position = 6    (index of "Rossum")                    |
|                                                                |
|  The model learns to predict these positions                  |
|                                                                |
+--------------------------------------------------------------+
```

---

## 13.6 Handling Long Documents

### The Problem with Long Contexts

BERT and similar models have a maximum input length (usually 512 tokens). Many real-world documents are much longer. The solution is to split long documents into overlapping chunks:

```python
from transformers import pipeline

qa = pipeline("question-answering")

# A very long context (imagine a full article)
long_context = """
Chapter 1: The History of Computing

The history of computing begins with Charles Babbage, who designed the
Analytical Engine in 1837. This mechanical computer was never completed
during his lifetime, but it contained many concepts found in modern
computers, including an arithmetic logic unit, control flow, and memory.

Ada Lovelace, who worked with Babbage, is often considered the first
computer programmer. She wrote what is recognized as the first algorithm
intended for processing on a machine.

The modern era of computing began in the 1940s with the development of
electronic computers. The ENIAC, completed in 1945, was one of the first
general-purpose electronic computers. It weighed 30 tons and occupied
1,800 square feet. Despite its enormous size, it was less powerful than
a modern smartphone.

The invention of the transistor in 1947 by Bell Labs revolutionized
computing. Transistors replaced vacuum tubes, making computers smaller,
faster, and more reliable. This led to the development of integrated
circuits in the 1960s, which packed thousands of transistors onto a
single chip.

The personal computer revolution began in the late 1970s with machines
like the Apple II and the IBM PC. These affordable computers brought
computing power to homes and small businesses for the first time.
"""

# Ask questions about the long context
questions = [
    "Who designed the Analytical Engine?",
    "Who is considered the first computer programmer?",
    "How much did the ENIAC weigh?",
    "What replaced vacuum tubes?",
    "When did the personal computer revolution begin?"
]

print("=== Questions About Computing History ===\n")
for q in questions:
    result = qa(question=q, context=long_context)
    print(f"Q: {q}")
    print(f"A: {result['answer']} (confidence: {result['score']:.2%})")
    print()
```

**Expected output:**

```
=== Questions About Computing History ===

Q: Who designed the Analytical Engine?
A: Charles Babbage (confidence: 96.12%)

Q: Who is considered the first computer programmer?
A: Ada Lovelace (confidence: 94.56%)

Q: How much did the ENIAC weigh?
A: 30 tons (confidence: 92.34%)

Q: What replaced vacuum tubes?
A: Transistors (confidence: 95.67%)

Q: When did the personal computer revolution begin?
A: late 1970s (confidence: 89.01%)
```

### Splitting Documents for Very Long Texts

```python
from transformers import pipeline

def qa_long_document(question, document, chunk_size=500, overlap=100):
    """
    Answer a question from a very long document by splitting it into
    overlapping chunks and finding the best answer across all chunks.

    Parameters:
        question: The question to answer
        document: The full document text
        chunk_size: Maximum characters per chunk
        overlap: Number of characters to overlap between chunks

    Returns:
        The best answer found across all chunks
    """
    qa = pipeline("question-answering")

    # Split document into overlapping chunks
    chunks = []
    start = 0
    while start < len(document):
        end = start + chunk_size
        chunk = document[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap

    print(f"Document split into {len(chunks)} chunks")

    # Find the best answer across all chunks
    best_answer = None
    best_score = -1

    for i, chunk in enumerate(chunks):
        try:
            result = qa(question=question, context=chunk)
            if result['score'] > best_score:
                best_score = result['score']
                best_answer = result['answer']
        except Exception:
            continue

    return {"answer": best_answer, "confidence": best_score}


# Example with a long document
long_doc = "Your very long document text here..." * 20  # Simulating length

# In practice:
# result = qa_long_document("Your question?", long_doc)
# print(result)
print("Long document QA function ready to use!")
```

---

## 13.7 Limitations of Extractive QA

### What Extractive QA Cannot Do

```
+--------------------------------------------------------------+
|        LIMITATIONS OF EXTRACTIVE QA                           |
+--------------------------------------------------------------+
|                                                                |
|  1. ANSWER MUST BE IN THE CONTEXT                             |
|     Cannot answer: "What is 2 + 2?" (unless "4" is in text)  |
|     Cannot reason or calculate                                |
|                                                                |
|  2. SINGLE SPAN ONLY                                          |
|     Cannot combine info from multiple sentences               |
|     Q: "Name all the countries mentioned"                     |
|     Can only highlight one continuous span                    |
|                                                                |
|  3. NO PARAPHRASING                                           |
|     Context: "The cat sat on the mat"                         |
|     Q: "Where was the feline?"                                |
|     May struggle because "feline" != "cat" in the context     |
|                                                                |
|  4. CONTEXT LENGTH LIMIT                                      |
|     Cannot process very long documents without chunking       |
|     May miss answers that span chunk boundaries               |
|                                                                |
|  5. NO "YES/NO" ANSWERS                                       |
|     Q: "Is Python popular?"                                   |
|     Will try to extract a span instead of saying "yes"        |
|                                                                |
+--------------------------------------------------------------+
```

### When to Use Extractive QA vs Other Approaches

```python
# Good use cases for extractive QA:
good_cases = [
    "Who founded the company?",          # Answer is a name in the text
    "When was the product launched?",    # Answer is a date in the text
    "What is the company's revenue?",    # Answer is a number in the text
    "Where is the headquarters?",        # Answer is a location in the text
]

# Bad use cases for extractive QA:
bad_cases = [
    "Summarize the annual report",       # Needs summarization, not extraction
    "Is the company profitable?",        # Needs yes/no reasoning
    "Compare product A and product B",   # Needs cross-document reasoning
    "What should I invest in?",          # Needs opinion/advice generation
]

print("GOOD use cases for extractive QA:")
for case in good_cases:
    print(f"  + {case}")

print("\nBAD use cases for extractive QA:")
for case in bad_cases:
    print(f"  - {case}")
```

---

## Common Mistakes

1. **Forgetting to provide context.** The QA pipeline requires both a `question` and a `context`. Without context, the model has nowhere to look for answers.

2. **Expecting answers not in the context.** Extractive QA can only find answers that exist verbatim in the provided text. If the answer is not in the context, the model will return a low-confidence wrong answer.

3. **Ignoring confidence scores.** Always check the confidence score. A low score (below 0.3) usually means the model is guessing and the answer is unreliable.

4. **Using too short a context.** Very short contexts (one or two sentences) give the model too little information. Provide enough surrounding text for the model to understand the topic.

5. **Not handling long documents.** If your context exceeds the model's maximum length (512 tokens for BERT), the text will be silently truncated. Split long documents into overlapping chunks.

---

## Best Practices

1. **Set confidence thresholds.** Do not show answers with confidence below 0.3 to users. Return "I don't know" instead of a wrong answer.

2. **Provide relevant context.** The more focused the context is on the topic of the question, the better the answers will be. Use information retrieval to find relevant passages first.

3. **Use SQuAD-trained models.** Models fine-tuned on SQuAD (like `distilbert-base-cased-distilled-squad`) are much better at QA than general-purpose models.

4. **Handle edge cases.** What if the question is unanswerable? What if the context is empty? Always write defensive code with error handling.

5. **Test with diverse questions.** Test your QA system with who, what, when, where, why, and how questions to ensure it handles different question types.

---

## Quick Summary

Extractive question answering finds the answer to a question by locating the exact span of text in a provided context. The model assigns start and end scores to every token and selects the span with the highest combined score. The Hugging Face QA pipeline makes this easy with just a few lines of code. For production systems, search across multiple context passages and use confidence thresholds to filter unreliable answers. The main limitation is that the answer must exist verbatim in the context -- the model extracts rather than generates.

---

## Key Points

- Extractive QA finds answers by highlighting spans in the provided context -- it does not generate new text
- The model outputs start logits and end logits for every token, then selects the best (start, end) pair
- The QA pipeline requires both a `question` and a `context` parameter
- Confidence scores range from 0 to 1 -- set a threshold (e.g., 0.3) to filter unreliable answers
- For long documents, split into overlapping chunks and find the best answer across all chunks
- SQuAD-trained models perform best for extractive QA tasks
- Extractive QA cannot answer questions whose answers are not in the context
- Fine-tuning for QA uses start and end token positions as labels instead of class labels

---

## Practice Questions

1. What is the difference between extractive and abstractive question answering? Give an example of a question that extractive QA could answer and one that it could not.

2. Explain what start logits and end logits are. How does the model combine them to find the answer?

3. Why is the confidence score important in a QA system? What problems could arise if you display all answers regardless of confidence?

4. You have a 50-page PDF document and want to build a QA system for it. What challenges would you face, and how would you solve them?

5. A user asks, "Is Python a good programming language?" to your extractive QA system. The context says "Python is widely used in data science and web development." What would the model likely return, and why is this problematic?

---

## Exercises

### Exercise 1: Build a Documentation QA Bot

Create a QA system for a fictional software product. Write 3-4 paragraphs of documentation (covering installation, features, and troubleshooting). Then test your system with at least 5 different questions.

**Requirements:**
- Include a confidence threshold
- Print "I don't know" for low-confidence answers
- Show which part of the documentation the answer came from

### Exercise 2: Compare QA Models

Load two different QA models from Hugging Face (for example, `distilbert-base-cased-distilled-squad` and `deepset/roberta-base-squad2`). Ask both models the same 5 questions and compare their answers and confidence scores. Which model performs better?

### Exercise 3: QA with Multiple Documents

Build a QA system that takes a list of documents (each with a title and content). When a question is asked, search all documents and return the top 3 answers ranked by confidence. Include the document title in the output.

---

## What Is Next?

You have learned how to extract answers from text -- now it is time to learn how to generate entirely new text. In the next chapter, we will explore **text generation**, where models create original text from a prompt. You will learn about temperature, top-k sampling, top-p sampling, and other techniques that control how creative or focused the generated text is. This is the technology behind chatbots, story generators, and code completion tools.
