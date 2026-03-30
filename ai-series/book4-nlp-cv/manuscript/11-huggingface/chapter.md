# Chapter 11: Hugging Face Transformers Library

## What You Will Learn

In this chapter, you will learn:

- What Hugging Face is and why it has become the center of modern NLP
- How to install the Transformers library and its dependencies
- How to use the pipeline API for common NLP tasks with just two lines of code
- How to work with AutoModel and AutoTokenizer for more control
- How to browse the Model Hub and choose the right model for your task
- How to load, use, and save pre-trained models

## Why This Chapter Matters

Imagine you want to build a house. You could cut down trees, mill your own lumber, forge your own nails, and mix your own concrete. Or you could go to a hardware store where everything is ready to use.

Hugging Face is that hardware store for machine learning. Before Hugging Face, using state-of-the-art NLP models meant reading complex research papers, writing hundreds of lines of code, and spending days just getting things to work. Hugging Face changed all of that. With just two or three lines of Python, you can now use the same models that power products at Google, Microsoft, and Meta.

This chapter is your gateway to practical NLP. Every chapter that follows in this book builds on what you learn here.

---

## 11.1 What Is Hugging Face?

### The GitHub of Machine Learning

Hugging Face is a company and an open-source community that provides tools for building applications with machine learning. Think of it as three things combined:

1. **A library** (Transformers) -- Python code that lets you use pre-trained models
2. **A model hub** -- A website where thousands of models are shared (like GitHub for ML models)
3. **A community** -- Researchers and developers sharing models, datasets, and knowledge

Here is a simple analogy:

```
+--------------------------------------------------+
|              THE HUGGING FACE ECOSYSTEM           |
+--------------------------------------------------+
|                                                    |
|  Model Hub          = App Store for AI models      |
|  Transformers lib   = The toolkit to use them      |
|  Datasets lib       = Ready-made training data     |
|  Spaces             = Free hosting for demos       |
|                                                    |
+--------------------------------------------------+
```

### Why Hugging Face Became So Popular

Before Hugging Face:

```
Step 1: Read a 20-page research paper
Step 2: Understand complex math
Step 3: Write 500+ lines of code
Step 4: Download model weights manually
Step 5: Debug for days
Step 6: Finally get a prediction
```

After Hugging Face:

```
Step 1: pip install transformers
Step 2: Write 2 lines of Python
Step 3: Get a prediction
```

That simplicity is why over 100,000 models are now hosted on the Hugging Face Hub.

---

## 11.2 Installing the Transformers Library

### Basic Installation

Open your terminal or command prompt and run:

```python
# Install the transformers library
# This is the core library you need
pip install transformers
```

**What this does:** Downloads and installs the Hugging Face Transformers library along with its dependencies (other libraries it needs to work).

### Installing with PyTorch Backend

Transformers needs a "backend" -- a deep learning framework that does the actual computation. PyTorch is the most popular choice:

```python
# Install transformers with PyTorch support
pip install transformers torch
```

**Line-by-line explanation:**
- `pip install` -- The Python package installer command
- `transformers` -- The Hugging Face library for using pre-trained models
- `torch` -- PyTorch, the deep learning framework that runs the models

### Verifying Your Installation

After installation, open Python and check that everything works:

```python
# Check that transformers is installed correctly
import transformers

# Print the version number
print(f"Transformers version: {transformers.__version__}")

# Check that PyTorch is available
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
```

**Expected output:**

```
Transformers version: 4.36.0
PyTorch version: 2.1.0
CUDA available: False
```

**Line-by-line explanation:**
- `import transformers` -- Loads the Transformers library into Python
- `transformers.__version__` -- A special variable that stores the version number
- `import torch` -- Loads PyTorch into Python
- `torch.cuda.is_available()` -- Checks if you have a GPU (graphics card) available for faster computation. `False` means you are using CPU only, which is fine for learning

> **Note:** Your version numbers may differ. That is perfectly normal. The examples in this book work with Transformers version 4.20 and above.

### What Is CUDA?

CUDA stands for Compute Unified Device Architecture. It is technology from NVIDIA that lets your graphics card (GPU) do math much faster than your regular processor (CPU).

```
+------------------------------------------+
|          PROCESSING SPEED ANALOGY        |
+------------------------------------------+
|                                          |
|  CPU = One very fast chef                |
|        Can cook one dish at a time       |
|        Very good at complex recipes      |
|                                          |
|  GPU = 1000 slower cooks                 |
|        Can cook 1000 simple dishes       |
|        at the same time                  |
|        Great for repetitive tasks        |
|                                          |
+------------------------------------------+
```

For this book, a CPU is sufficient. A GPU just makes things faster.

---

## 11.3 The Pipeline API: NLP in Two Lines

The pipeline API is the simplest way to use a pre-trained model. It wraps all the complex steps (tokenization, model inference, post-processing) into a single function call.

### How Pipelines Work

```
+------------------------------------------------------------+
|                    PIPELINE INTERNALS                       |
+------------------------------------------------------------+
|                                                              |
|  Your Text --> [Tokenizer] --> [Model] --> [Post-Process]   |
|  "I love it"   Converts to     Makes a     Formats the     |
|                 numbers         prediction  result nicely    |
|                                                              |
|  You only see: pipeline("I love it") --> "POSITIVE 0.99"    |
+------------------------------------------------------------+
```

### Sentiment Analysis Pipeline

Sentiment analysis determines whether text expresses a positive or negative opinion.

```python
from transformers import pipeline

# Create a sentiment analysis pipeline
# This downloads a pre-trained model the first time you run it
classifier = pipeline("sentiment-analysis")

# Analyze the sentiment of a sentence
result = classifier("I absolutely love this movie! It was fantastic.")
print(result)
```

**Expected output:**

```
[{'label': 'POSITIVE', 'score': 0.9998}]
```

**Line-by-line explanation:**
- `from transformers import pipeline` -- Imports the pipeline function from the Transformers library
- `pipeline("sentiment-analysis")` -- Creates a sentiment analysis pipeline. The string `"sentiment-analysis"` tells Hugging Face which type of task you want. The first time you run this, it downloads a pre-trained model (about 250 MB)
- `classifier(...)` -- Passes your text into the pipeline for analysis
- `result` -- A list of dictionaries containing the label (POSITIVE or NEGATIVE) and a confidence score between 0 and 1

You can also analyze multiple texts at once:

```python
from transformers import pipeline

classifier = pipeline("sentiment-analysis")

# Analyze multiple sentences at once
texts = [
    "This restaurant has amazing food!",
    "The service was terrible and slow.",
    "The movie was okay, nothing special."
]

results = classifier(texts)

for text, result in zip(texts, results):
    print(f"Text: {text}")
    print(f"  Sentiment: {result['label']}, Confidence: {result['score']:.4f}")
    print()
```

**Expected output:**

```
Text: This restaurant has amazing food!
  Sentiment: POSITIVE, Confidence: 0.9999

Text: The service was terrible and slow.
  Sentiment: NEGATIVE, Confidence: 0.9998

Text: The movie was okay, nothing special.
  Sentiment: POSITIVE, Confidence: 0.6837
```

**Line-by-line explanation:**
- `texts = [...]` -- A list of three sentences to analyze
- `classifier(texts)` -- Processes all three sentences through the pipeline
- `zip(texts, results)` -- Pairs each text with its result so we can print them together
- `result['label']` -- Accesses the sentiment label from the result dictionary
- `result['score']:.4f` -- Formats the score to 4 decimal places

Notice that the third sentence gets a lower confidence score. The model is less certain about neutral-sounding text.

### Named Entity Recognition (NER) Pipeline

Named Entity Recognition finds and classifies names of people, places, organizations, and other entities in text.

```python
from transformers import pipeline

# Create a NER pipeline
ner = pipeline("ner", grouped_entities=True)

# Find entities in a sentence
text = "Barack Obama was born in Hawaii and served as the 44th President of the United States."
entities = ner(text)

for entity in entities:
    print(f"Entity: {entity['word']}")
    print(f"  Type: {entity['entity_group']}")
    print(f"  Confidence: {entity['score']:.4f}")
    print()
```

**Expected output:**

```
Entity: Barack Obama
  Type: PER
  Confidence: 0.9988

Entity: Hawaii
  Type: LOC
  Confidence: 0.9993

Entity: United States
  Type: LOC
  Confidence: 0.9987
```

**Line-by-line explanation:**
- `pipeline("ner", grouped_entities=True)` -- Creates a NER pipeline. The `grouped_entities=True` parameter tells it to combine related word pieces into complete entity names (for example, "Barack" and "Obama" become "Barack Obama" instead of two separate entities)
- `entity['word']` -- The text that was identified as an entity
- `entity['entity_group']` -- The type of entity: PER (person), LOC (location), ORG (organization), MISC (miscellaneous)
- `entity['score']` -- How confident the model is in its prediction

```
+------------------------------------------+
|          NER ENTITY TYPES                |
+------------------------------------------+
|                                          |
|  PER  = Person      (Barack Obama)       |
|  LOC  = Location    (Hawaii, France)     |
|  ORG  = Organization (Google, NASA)      |
|  MISC = Miscellaneous (English, GDP)     |
|                                          |
+------------------------------------------+
```

### Summarization Pipeline

Summarization condenses long text into a shorter version while keeping the key information.

```python
from transformers import pipeline

# Create a summarization pipeline
summarizer = pipeline("summarization")

# A longer text to summarize
article = """
Machine learning is a subset of artificial intelligence that focuses on
building systems that learn from data. Unlike traditional programming where
developers write explicit rules, machine learning algorithms find patterns
in data automatically. This approach has proven incredibly effective for
tasks like image recognition, natural language processing, and recommendation
systems. The field has grown rapidly in recent years, driven by increases in
computing power and the availability of large datasets. Today, machine
learning powers many of the services we use daily, from search engines to
voice assistants to social media feeds.
"""

summary = summarizer(article, max_length=50, min_length=20)
print("Summary:")
print(summary[0]['summary_text'])
```

**Expected output:**

```
Summary:
Machine learning is a subset of artificial intelligence that focuses on building systems that learn from data. It has grown rapidly in recent years, driven by increases in computing power.
```

**Line-by-line explanation:**
- `pipeline("summarization")` -- Creates a summarization pipeline using a default model (usually BART or T5)
- `max_length=50` -- The maximum number of tokens (roughly words) in the summary
- `min_length=20` -- The minimum number of tokens in the summary
- `summary[0]['summary_text']` -- Extracts the summary text from the result. The result is a list containing a dictionary

### Translation Pipeline

Translation converts text from one language to another.

```python
from transformers import pipeline

# Create a translation pipeline (English to French)
translator = pipeline("translation_en_to_fr")

# Translate a sentence
text = "Machine learning is changing the world."
result = translator(text)

print(f"English: {text}")
print(f"French:  {result[0]['translation_text']}")
```

**Expected output:**

```
English: Machine learning is changing the world.
French:  L'apprentissage automatique change le monde.
```

**Line-by-line explanation:**
- `pipeline("translation_en_to_fr")` -- Creates a pipeline that translates from English (`en`) to French (`fr`). Hugging Face supports many language pairs
- `result[0]['translation_text']` -- Extracts the translated text from the result

### Question Answering Pipeline

Question answering finds the answer to a question within a given context (a passage of text).

```python
from transformers import pipeline

# Create a question answering pipeline
qa = pipeline("question-answering")

# Provide a context and ask a question
context = """
Python was created by Guido van Rossum and first released in 1991.
It is known for its simple syntax and readability. Python is widely
used in web development, data science, artificial intelligence, and
automation. It is one of the most popular programming languages in
the world.
"""

question = "Who created Python?"
result = qa(question=question, context=context)

print(f"Question: {question}")
print(f"Answer: {result['answer']}")
print(f"Confidence: {result['score']:.4f}")
print(f"Found at position: {result['start']} to {result['end']}")
```

**Expected output:**

```
Question: Who created Python?
Answer: Guido van Rossum
Confidence: 0.9876
Found at position: 26 to 42
```

**Line-by-line explanation:**
- `pipeline("question-answering")` -- Creates a QA pipeline
- `question=question, context=context` -- You must provide both the question and the text where the answer can be found
- `result['answer']` -- The text span that the model identified as the answer
- `result['score']` -- Confidence score between 0 and 1
- `result['start']` and `result['end']` -- Character positions in the context where the answer was found

### Text Generation Pipeline

Text generation creates new text based on a prompt you provide.

```python
from transformers import pipeline

# Create a text generation pipeline
generator = pipeline("text-generation", model="gpt2")

# Generate text from a prompt
prompt = "In the future, artificial intelligence will"
result = generator(prompt, max_length=50, num_return_sequences=1)

print("Generated text:")
print(result[0]['generated_text'])
```

**Expected output:**

```
Generated text:
In the future, artificial intelligence will be able to understand human
emotions and respond appropriately. This technology could transform
healthcare, education, and how we interact with machines on a daily basis.
```

**Line-by-line explanation:**
- `pipeline("text-generation", model="gpt2")` -- Creates a text generation pipeline using the GPT-2 model specifically
- `max_length=50` -- Maximum number of tokens to generate
- `num_return_sequences=1` -- How many different versions of text to generate
- `result[0]['generated_text']` -- The generated text, which includes your original prompt

> **Note:** Text generation is not deterministic. Each time you run this code, you will likely get different output. This is because the model uses random sampling to choose the next word.

### All Pipeline Tasks at a Glance

```
+--------------------------------------------------------------+
|              HUGGING FACE PIPELINE TASKS                      |
+--------------------------------------------------------------+
|                                                                |
|  Task                    | What It Does                       |
|  ------------------------|----------------------------------- |
|  sentiment-analysis      | Positive/negative classification   |
|  ner                     | Find people, places, orgs in text  |
|  summarization           | Shorten long text                  |
|  translation_xx_to_yy    | Convert between languages          |
|  question-answering      | Find answers in a passage          |
|  text-generation         | Generate new text from a prompt    |
|  fill-mask               | Predict missing words              |
|  zero-shot-classification| Classify without training          |
|  text2text-generation    | General text-to-text tasks         |
|  feature-extraction      | Get numerical representations      |
|                                                                |
+--------------------------------------------------------------+
```

---

## 11.4 AutoModel and AutoTokenizer: More Control

The pipeline API is convenient, but sometimes you need more control. That is where AutoModel and AutoTokenizer come in.

### What Are Tokenizers?

A tokenizer converts human-readable text into numbers that a model can understand.

```
+------------------------------------------------------------+
|                HOW TOKENIZATION WORKS                       |
+------------------------------------------------------------+
|                                                              |
|  "I love cats"                                               |
|       |                                                      |
|       v                                                      |
|  [Tokenizer]                                                 |
|       |                                                      |
|       v                                                      |
|  ["I", "love", "cats"]     <-- Split into tokens             |
|       |                                                      |
|       v                                                      |
|  [1045, 2293, 8870]        <-- Convert to numbers (IDs)      |
|       |                                                      |
|       v                                                      |
|  [Model processes these numbers]                             |
|                                                              |
+------------------------------------------------------------+
```

### Using AutoTokenizer

```python
from transformers import AutoTokenizer

# Load a tokenizer for BERT
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Tokenize a sentence
text = "Hugging Face makes NLP easy!"
tokens = tokenizer(text, return_tensors="pt")

# See what the tokenizer produced
print("Input text:", text)
print("Token IDs:", tokens["input_ids"])
print("Attention mask:", tokens["attention_mask"])

# Convert IDs back to tokens to see how text was split
token_list = tokenizer.convert_ids_to_tokens(tokens["input_ids"][0])
print("Tokens:", token_list)
```

**Expected output:**

```
Input text: Hugging Face makes NLP easy!
Token IDs: tensor([[  101,  17662,  2227,  3084,  17953,  2959,   999,   102]])
Attention mask: tensor([[1, 1, 1, 1, 1, 1, 1, 1]])
Tokens: ['[CLS]', 'hugging', 'face', 'makes', 'nl', '##p', 'easy', '!', '[SEP]']
```

**Line-by-line explanation:**
- `AutoTokenizer.from_pretrained("bert-base-uncased")` -- Downloads and loads the tokenizer that was used to train the BERT model. "uncased" means it converts everything to lowercase
- `tokenizer(text, return_tensors="pt")` -- Tokenizes the text and returns PyTorch tensors (`"pt"` stands for PyTorch)
- `tokens["input_ids"]` -- The numerical IDs assigned to each token
- `tokens["attention_mask"]` -- A mask of 1s and 0s. A `1` means "pay attention to this token" and `0` means "ignore this (it is padding)"
- `[CLS]` -- A special token BERT adds at the beginning of every input (stands for "classification")
- `[SEP]` -- A special token BERT adds at the end (stands for "separator")
- `##p` -- The `##` prefix means this is a sub-word. "NLP" was split into "nl" and "##p" because the tokenizer breaks unknown words into smaller known pieces

### Understanding Sub-word Tokenization

Most modern tokenizers do not split text into whole words. They use sub-word tokenization, which breaks rare or unknown words into smaller pieces:

```
+------------------------------------------------------------+
|           SUB-WORD TOKENIZATION EXAMPLE                     |
+------------------------------------------------------------+
|                                                              |
|  "unhappiness"  -->  ["un", "##happiness"]                  |
|                                                              |
|  Why? The model learned "un" and "happiness" separately.    |
|  It can now understand any word starting with "un-"          |
|  even if it never saw "unhappiness" during training.         |
|                                                              |
|  "transformers"  -->  ["transform", "##ers"]                |
|  "ChatGPT"       -->  ["chat", "##g", "##pt"]               |
|                                                              |
+------------------------------------------------------------+
```

This is clever because it means the model can handle words it has never seen before by breaking them into known pieces.

### Using AutoModel

```python
from transformers import AutoTokenizer, AutoModel
import torch

# Load model and tokenizer
model_name = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# Tokenize input text
text = "Transformers are amazing!"
inputs = tokenizer(text, return_tensors="pt")

# Run the model (no gradient computation needed for inference)
with torch.no_grad():
    outputs = model(**inputs)

# The output contains hidden states (numerical representations)
print("Output shape:", outputs.last_hidden_state.shape)
print("This means:")
print(f"  - Batch size: {outputs.last_hidden_state.shape[0]} (one sentence)")
print(f"  - Sequence length: {outputs.last_hidden_state.shape[1]} tokens")
print(f"  - Hidden size: {outputs.last_hidden_state.shape[2]} dimensions")
```

**Expected output:**

```
Output shape: torch.Size([1, 6, 768])
This means:
  - Batch size: 1 (one sentence)
  - Sequence length: 6 tokens
  - Hidden size: 768 dimensions
```

**Line-by-line explanation:**
- `AutoModel.from_pretrained(model_name)` -- Downloads and loads the pre-trained BERT model (about 440 MB the first time)
- `with torch.no_grad():` -- Tells PyTorch not to track computations for gradient calculation. This saves memory and speeds things up. We only need this during training, not when making predictions
- `model(**inputs)` -- The `**` unpacks the dictionary into keyword arguments. It is the same as writing `model(input_ids=..., attention_mask=...)`
- `outputs.last_hidden_state` -- The model's output: a numerical representation of each token. Each token is represented by 768 numbers (for BERT base)

### AutoModel vs Pipeline: When to Use Which

```
+--------------------------------------------------------------+
|         PIPELINE vs AUTOMODEL COMPARISON                      |
+--------------------------------------------------------------+
|                                                                |
|  Pipeline:                                                     |
|    + Simple: 2 lines of code                                   |
|    + Handles all pre/post processing                           |
|    + Perfect for quick prototyping                             |
|    - Less control over model behavior                          |
|    - Cannot access intermediate outputs                        |
|                                                                |
|  AutoModel + AutoTokenizer:                                    |
|    + Full control over every step                              |
|    + Access to raw model outputs                               |
|    + Can customize processing                                  |
|    + Required for fine-tuning                                  |
|    - More code to write                                        |
|    - Need to handle pre/post processing yourself               |
|                                                                |
+--------------------------------------------------------------+
```

---

## 11.5 The Model Hub: Finding the Right Model

### What Is the Model Hub?

The Hugging Face Model Hub is a website (huggingface.co/models) where anyone can share pre-trained models. Think of it as an app store, but for AI models.

```
+--------------------------------------------------------------+
|              THE MODEL HUB                                    |
+--------------------------------------------------------------+
|                                                                |
|  100,000+ models available                                    |
|                                                                |
|  Filter by:                                                    |
|    - Task (text classification, translation, etc.)            |
|    - Language (English, French, Chinese, etc.)                |
|    - Library (PyTorch, TensorFlow, JAX)                       |
|    - Dataset (what data it was trained on)                     |
|    - License (can you use it commercially?)                    |
|                                                                |
|  Each model page includes:                                    |
|    - Description and documentation                             |
|    - Example code                                              |
|    - Performance metrics                                       |
|    - Download statistics                                       |
|                                                                |
+--------------------------------------------------------------+
```

### Loading a Specific Model

Instead of using the default model, you can specify exactly which model to use:

```python
from transformers import pipeline

# Use a specific model for sentiment analysis
# This model was trained on product reviews
classifier = pipeline(
    "sentiment-analysis",
    model="nlptown/bert-base-multilingual-uncased-sentiment"
)

# This model gives star ratings (1-5) instead of positive/negative
review = "The product quality is excellent and delivery was fast!"
result = classifier(review)

print(f"Review: {review}")
print(f"Rating: {result[0]['label']}")
print(f"Confidence: {result[0]['score']:.4f}")
```

**Expected output:**

```
Review: The product quality is excellent and delivery was fast!
Rating: 5 stars
Confidence: 0.7342
```

**Line-by-line explanation:**
- `model="nlptown/bert-base-multilingual-uncased-sentiment"` -- Specifies a particular model from the Hub. The format is `username/model-name`
- This model was trained on product reviews in multiple languages and gives star ratings from 1 to 5 instead of simple positive/negative

### How to Choose the Right Model

Choosing the right model depends on your specific needs. Here is a decision framework:

```
+--------------------------------------------------------------+
|           MODEL SELECTION DECISION TREE                       |
+--------------------------------------------------------------+
|                                                                |
|  1. What TASK do you need?                                    |
|     --> Filter models by task on the Hub                      |
|                                                                |
|  2. What LANGUAGE is your text in?                            |
|     --> English: most models work                             |
|     --> Other: look for multilingual or language-specific      |
|                                                                |
|  3. How much COMPUTING POWER do you have?                     |
|     --> Limited: use "small" or "tiny" models                 |
|     --> Good GPU: use "base" or "large" models                |
|                                                                |
|  4. What is your use case LICENSE?                            |
|     --> Personal/research: most models are fine               |
|     --> Commercial: check the model's license                 |
|                                                                |
|  5. How many DOWNLOADS does the model have?                   |
|     --> More downloads usually means more reliable             |
|                                                                |
+--------------------------------------------------------------+
```

### Popular Models for Common Tasks

```python
from transformers import pipeline

# Sentiment analysis - good default model
sentiment = pipeline("sentiment-analysis",
                     model="distilbert-base-uncased-finetuned-sst-2-english")

# Named Entity Recognition - good default model
ner = pipeline("ner",
               model="dbmdz/bert-large-cased-finetuned-conll03-english",
               grouped_entities=True)

# Summarization - good default model
summarizer = pipeline("summarization",
                      model="facebook/bart-large-cnn")

# Translation (English to German)
translator = pipeline("translation",
                      model="Helsinki-NLP/opus-mt-en-de")

# Text generation
generator = pipeline("text-generation",
                     model="gpt2")

# Let us test each one
print("=== Sentiment ===")
print(sentiment("I love learning about AI!"))

print("\n=== NER ===")
print(ner("Apple Inc. is based in Cupertino, California."))

print("\n=== Translation ===")
print(translator("Hello, how are you?"))
```

**Expected output:**

```
=== Sentiment ===
[{'label': 'POSITIVE', 'score': 0.9998}]

=== NER ===
[{'entity_group': 'ORG', 'score': 0.9975, 'word': 'Apple Inc.', 'start': 0, 'end': 10},
 {'entity_group': 'LOC', 'score': 0.9990, 'word': 'Cupertino', 'start': 23, 'end': 32},
 {'entity_group': 'LOC', 'score': 0.9987, 'word': 'California', 'start': 34, 'end': 44}]

=== Translation ===
[{'translation_text': 'Hallo, wie geht es Ihnen?'}]
```

---

## 11.6 Loading and Saving Models

### Saving a Model Locally

Once you have downloaded a model, you can save it to your computer so you do not need to download it again:

```python
from transformers import AutoTokenizer, AutoModel

# Load model and tokenizer from the Hub
model_name = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# Save to a local directory
save_path = "./my_saved_model"
tokenizer.save_pretrained(save_path)
model.save_pretrained(save_path)

print(f"Model saved to {save_path}")
```

**Expected output:**

```
Model saved to ./my_saved_model
```

**Line-by-line explanation:**
- `save_pretrained(save_path)` -- Saves all model files and tokenizer files to the specified directory
- This creates several files: model weights, configuration, tokenizer vocabulary, and more

### Loading a Model from a Local Directory

```python
from transformers import AutoTokenizer, AutoModel

# Load from your saved local directory (no internet needed!)
save_path = "./my_saved_model"
tokenizer = AutoTokenizer.from_pretrained(save_path)
model = AutoModel.from_pretrained(save_path)

print("Model loaded from local directory!")
print(f"Model type: {model.config.model_type}")
print(f"Vocabulary size: {tokenizer.vocab_size}")
```

**Expected output:**

```
Model loaded from local directory!
Model type: distilbert
Vocabulary size: 30522
```

### Understanding Model Sizes

Different model sizes trade off between speed and accuracy:

```
+--------------------------------------------------------------+
|              MODEL SIZE COMPARISON                            |
+--------------------------------------------------------------+
|                                                                |
|  Model Name              | Parameters | Size  | Speed        |
|  ------------------------|------------|-------|-------------- |
|  distilbert-base-uncased | 66M        | 250MB | Very fast    |
|  bert-base-uncased       | 110M       | 440MB | Fast         |
|  bert-large-uncased      | 340M       | 1.3GB | Moderate     |
|  gpt2                    | 117M       | 500MB | Fast         |
|  gpt2-medium             | 345M       | 1.4GB | Moderate     |
|  gpt2-large              | 774M       | 3.1GB | Slow         |
|                                                                |
|  Rule of thumb:                                               |
|  Larger model = Better accuracy but slower and more memory     |
|  Smaller model = Faster but may sacrifice some accuracy        |
|                                                                |
+--------------------------------------------------------------+
```

> **Tip:** Start with DistilBERT for classification tasks and GPT-2 (small) for generation tasks. Move to larger models only if accuracy is not sufficient.

---

## 11.7 Putting It All Together: A Complete Example

Let us build a small text analysis tool that uses multiple pipelines:

```python
from transformers import pipeline

def analyze_text(text):
    """
    Analyze a piece of text using multiple NLP techniques.

    Parameters:
        text: The text to analyze (a string)

    Returns:
        A dictionary containing analysis results
    """

    # Initialize pipelines (in practice, do this once, not every call)
    print("Loading models... (this may take a moment the first time)")
    sentiment_analyzer = pipeline("sentiment-analysis")
    ner_analyzer = pipeline("ner", grouped_entities=True)

    # Step 1: Sentiment Analysis
    print("\n--- Sentiment Analysis ---")
    sentiment = sentiment_analyzer(text)
    print(f"Sentiment: {sentiment[0]['label']}")
    print(f"Confidence: {sentiment[0]['score']:.4f}")

    # Step 2: Named Entity Recognition
    print("\n--- Named Entities ---")
    entities = ner_analyzer(text)
    if entities:
        for entity in entities:
            print(f"  {entity['word']} ({entity['entity_group']})"
                  f" - confidence: {entity['score']:.4f}")
    else:
        print("  No named entities found.")

    # Step 3: Basic statistics
    print("\n--- Text Statistics ---")
    words = text.split()
    sentences = text.count('.') + text.count('!') + text.count('?')
    print(f"  Word count: {len(words)}")
    print(f"  Sentence count: {sentences}")
    print(f"  Average words per sentence: {len(words)/max(sentences,1):.1f}")

    return {
        "sentiment": sentiment[0],
        "entities": entities,
        "word_count": len(words),
        "sentence_count": sentences
    }


# Test with a sample text
sample_text = """
Apple announced its new iPhone today in Cupertino.
Tim Cook presented the device at the Steve Jobs Theater.
The audience was thrilled with the new features and design.
"""

results = analyze_text(sample_text.strip())
```

**Expected output:**

```
Loading models... (this may take a moment the first time)

--- Sentiment Analysis ---
Sentiment: POSITIVE
Confidence: 0.9985

--- Named Entities ---
  Apple (ORG) - confidence: 0.9978
  iPhone (MISC) - confidence: 0.9432
  Cupertino (LOC) - confidence: 0.9991
  Tim Cook (PER) - confidence: 0.9988
  Steve Jobs Theater (LOC) - confidence: 0.9845

--- Text Statistics ---
  Word count: 27
  Sentence count: 3
  Average words per sentence: 9.0
```

**Line-by-line explanation:**
- `def analyze_text(text):` -- Defines a function that takes any text and runs multiple analyses on it
- We create two pipeline objects: one for sentiment and one for NER
- The function runs sentiment analysis, finds named entities, and calculates basic text statistics
- It returns a dictionary with all results for further use
- `text.strip()` -- Removes leading and trailing whitespace from the sample text

---

## Common Mistakes

1. **Not having enough disk space.** Pre-trained models can be several gigabytes. Make sure you have at least 5 GB of free space before downloading large models.

2. **Forgetting `return_tensors="pt"` when using AutoTokenizer.** Without this parameter, the tokenizer returns plain Python lists instead of PyTorch tensors, and the model will not accept them.

3. **Using the wrong model for the task.** A model trained for sentiment analysis cannot do translation. Always match the model to your task.

4. **Running models without `torch.no_grad()` during inference.** This wastes memory by tracking gradients you do not need. Always wrap inference code in `with torch.no_grad():`.

5. **Expecting identical output every time from text generation.** Generation models use random sampling by default. Set `do_sample=False` for deterministic output if needed.

---

## Best Practices

1. **Start with pipelines.** Use the pipeline API for quick experiments and prototyping. Switch to AutoModel only when you need more control.

2. **Save models locally.** After downloading a model once, save it locally to avoid repeated downloads and to work offline.

3. **Choose the smallest model that meets your accuracy needs.** DistilBERT is 60% smaller and 60% faster than BERT with 97% of the accuracy.

4. **Reuse pipeline objects.** Create the pipeline once and reuse it for multiple predictions. Do not create a new pipeline for every prediction.

5. **Check model cards on the Hub.** Every good model has a "model card" that explains what it was trained on, its limitations, and how to use it properly.

---

## Quick Summary

Hugging Face Transformers is a Python library that gives you access to thousands of pre-trained NLP models. The pipeline API lets you perform common tasks like sentiment analysis, NER, summarization, translation, question answering, and text generation with just two lines of code. For more control, use AutoModel and AutoTokenizer to handle tokenization and model inference manually. The Model Hub hosts over 100,000 models that you can filter by task, language, and size. Always start with a small model and scale up only if needed.

---

## Key Points

- Hugging Face is the central ecosystem for modern NLP, providing models, datasets, and tools
- The `pipeline()` function is the easiest way to use pre-trained models -- just specify the task name
- Common pipeline tasks include sentiment-analysis, ner, summarization, translation, question-answering, and text-generation
- AutoTokenizer converts text to numbers, AutoModel processes those numbers
- Sub-word tokenization lets models handle words they have never seen before
- The Model Hub has over 100,000 models filterable by task, language, and size
- Smaller models (like DistilBERT) are often good enough and much faster
- Save models locally with `save_pretrained()` to avoid repeated downloads

---

## Practice Questions

1. What is the difference between using `pipeline("sentiment-analysis")` and using `AutoTokenizer` plus `AutoModel` separately? When would you choose one approach over the other?

2. Explain what sub-word tokenization is and why it is useful. What does the `##` prefix mean in BERT tokenizer output?

3. You need to build an NLP application that detects the names of people, companies, and locations in news articles. Which pipeline task would you use, and what entity types would the model return?

4. A colleague says their model is too slow. It is using `bert-large-uncased` (340M parameters). What model would you suggest as a faster alternative, and what trade-off would they be making?

5. Why is it important to use `with torch.no_grad():` when making predictions with AutoModel? What happens if you forget it?

---

## Exercises

### Exercise 1: Multi-Language Sentiment Analysis

Create a program that uses the `nlptown/bert-base-multilingual-uncased-sentiment` model to analyze product reviews. The program should accept a list of reviews and print the star rating for each one.

**Hint:** This model returns labels like "1 star", "2 stars", etc.

### Exercise 2: Build a Simple FAQ Bot

Using the question-answering pipeline, build a program that:
- Stores a company FAQ as a string (make up a small company and 3-4 FAQ entries)
- Accepts user questions
- Returns the answer found in the FAQ along with the confidence score

**Hint:** Combine all FAQ text into one context string and use `pipeline("question-answering")`.

### Exercise 3: Text Analysis Dashboard

Create a function that takes any text and produces a complete analysis report including:
- Sentiment (positive/negative and confidence)
- Named entities found (with types)
- A one-sentence summary (using the summarization pipeline)
- Word count and sentence count

Print the results in a nicely formatted report.

---

## What Is Next?

Now that you know how to use pre-trained models, the next chapter takes things further. You will learn how to **fine-tune** a BERT model on your own data. Fine-tuning is like taking a general-purpose tool and sharpening it for your specific task. Instead of using a model trained on generic text, you will create a model that is an expert in exactly what you need -- starting with movie review sentiment classification.
