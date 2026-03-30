# Chapter 12: Fine-Tuning BERT for Classification

## What You Will Learn

In this chapter, you will learn:

- Why fine-tuning is necessary and how it differs from using pre-trained models directly
- How to prepare your own dataset for training using the Dataset class
- How to tokenize text with proper padding and truncation
- How to set up the Trainer and TrainingArguments for training
- How to train, evaluate, and save a fine-tuned model
- How to build a complete movie review sentiment classifier from scratch

## Why This Chapter Matters

Imagine you hire a chef who graduated from the best culinary school in the world. This chef knows everything about cooking techniques, ingredients, and flavors. But you run a sushi restaurant, and this chef has never made sushi before.

Do you send the chef back to culinary school for four years? Of course not. You give the chef a few weeks of sushi-specific training. The chef already understands food -- they just need to learn your specialty.

That is exactly what fine-tuning does. BERT was trained on billions of words and understands language deeply. But it was not trained on your specific task. Fine-tuning takes that general knowledge and adapts it to your exact needs -- whether that is classifying movie reviews, detecting spam, or categorizing support tickets.

Fine-tuning is one of the most powerful techniques in modern NLP. It lets you build high-accuracy models with relatively little data and training time.

---

## 12.1 Understanding Fine-Tuning

### Pre-Training vs Fine-Tuning

BERT's life has two phases:

```
+--------------------------------------------------------------+
|          TWO PHASES OF BERT'S TRAINING                       |
+--------------------------------------------------------------+
|                                                                |
|  Phase 1: PRE-TRAINING (done by researchers)                  |
|  +-------------------------------------------------+          |
|  | Trained on billions of words from books & web   |          |
|  | Learns grammar, facts, word relationships       |          |
|  | Takes weeks on hundreds of GPUs                 |          |
|  | Cost: Hundreds of thousands of dollars           |          |
|  | Result: A model that "understands" language      |          |
|  +-------------------------------------------------+          |
|                                                                |
|  Phase 2: FINE-TUNING (done by you!)                          |
|  +-------------------------------------------------+          |
|  | Trained on YOUR specific data (hundreds/thousands|          |
|  | of examples)                                     |          |
|  | Adapts the model to YOUR specific task           |          |
|  | Takes minutes to hours on a single GPU           |          |
|  | Cost: Almost free                                |          |
|  | Result: A model that excels at YOUR task          |          |
|  +-------------------------------------------------+          |
|                                                                |
+--------------------------------------------------------------+
```

### What Happens During Fine-Tuning

During fine-tuning, we make small adjustments to BERT's internal weights so it performs well on our specific task:

```
+--------------------------------------------------------------+
|           FINE-TUNING ARCHITECTURE                            |
+--------------------------------------------------------------+
|                                                                |
|  Input: "This movie was terrible"                             |
|              |                                                 |
|              v                                                 |
|  +----------------------+                                      |
|  |     Tokenizer        |  Converts text to numbers           |
|  +----------------------+                                      |
|              |                                                 |
|              v                                                 |
|  +----------------------+                                      |
|  |     BERT Model       |  Pre-trained weights                |
|  |  (slightly adjusted  |  (adjusted during fine-tuning)      |
|  |   during training)   |                                      |
|  +----------------------+                                      |
|              |                                                 |
|              v                                                 |
|  +----------------------+                                      |
|  | Classification Head  |  NEW layer added on top             |
|  |  (Linear Layer)      |  (trained from scratch)             |
|  +----------------------+                                      |
|              |                                                 |
|              v                                                 |
|  Output: NEGATIVE (0.97)                                       |
|                                                                |
+--------------------------------------------------------------+
```

The key idea: We keep most of BERT's knowledge and just add a small new layer on top for our specific task.

### Why Not Train From Scratch?

```
+--------------------------------------------------------------+
|     TRAINING FROM SCRATCH vs FINE-TUNING                      |
+--------------------------------------------------------------+
|                                                                |
|  From Scratch:                                                 |
|    - Need millions of examples                                |
|    - Takes days or weeks of training                          |
|    - Requires expensive hardware (multiple GPUs)              |
|    - Model learns everything from zero                        |
|                                                                |
|  Fine-Tuning:                                                  |
|    - Need hundreds to thousands of examples                   |
|    - Takes minutes to hours                                   |
|    - Works on a single GPU or even CPU                        |
|    - Model already knows language, just learns your task      |
|                                                                |
+--------------------------------------------------------------+
```

---

## 12.2 Preparing Your Dataset

### Our Task: Movie Review Sentiment Classification

We will build a model that reads movie reviews and predicts whether the review is positive or negative. We will use the IMDB dataset, which contains 50,000 movie reviews.

### Loading the Dataset

Hugging Face provides a `datasets` library that makes loading datasets easy:

```python
# First, install the datasets library
# pip install datasets

from datasets import load_dataset

# Load the IMDB movie review dataset
# This downloads the dataset the first time you run it
dataset = load_dataset("imdb")

# Let us see what we got
print("Dataset structure:")
print(dataset)
print()

# Look at the training set
print(f"Training examples: {len(dataset['train'])}")
print(f"Test examples: {len(dataset['test'])}")
```

**Expected output:**

```
Dataset structure:
DatasetDict({
    train: Dataset({
        features: ['text', 'label'],
        num_rows: 25000
    })
    test: Dataset({
        features: ['text', 'label'],
        num_rows: 25000
    })
})

Training examples: 25000
Test examples: 25000
```

**Line-by-line explanation:**
- `from datasets import load_dataset` -- Imports the dataset loading function from Hugging Face's datasets library
- `load_dataset("imdb")` -- Downloads and loads the IMDB dataset. The string `"imdb"` is the dataset name on the Hugging Face Hub
- `dataset['train']` -- The training portion of the dataset
- `dataset['test']` -- The test portion used to evaluate the model

### Exploring the Dataset

```python
from datasets import load_dataset

dataset = load_dataset("imdb")

# Look at the first example
example = dataset['train'][0]
print(f"Label: {example['label']} ({'positive' if example['label'] == 1 else 'negative'})")
print(f"Review (first 200 chars): {example['text'][:200]}...")
print()

# Check the label distribution
# Count how many positive and negative reviews there are
labels = dataset['train']['label']
positive_count = sum(labels)
negative_count = len(labels) - positive_count

print(f"Positive reviews: {positive_count}")
print(f"Negative reviews: {negative_count}")
print(f"Balance: {'balanced' if abs(positive_count - negative_count) < 100 else 'imbalanced'}")
```

**Expected output:**

```
Label: 0 (negative)
Review (first 200 chars): I rented I AM CURIOUS-YELLOW from my video store because of all the controversy that surrounded it when it was first released in 1969. I also heard that at first it was seized by U.S. customs if it...

Positive reviews: 12500
Negative reviews: 12500
Balance: balanced
```

**Line-by-line explanation:**
- `dataset['train'][0]` -- Gets the first example from the training set
- `example['label']` -- The label is 0 (negative) or 1 (positive)
- `example['text']` -- The actual review text
- `example['text'][:200]` -- Shows only the first 200 characters to keep output manageable
- The dataset is balanced: equal numbers of positive and negative reviews

### Using a Smaller Subset for Faster Training

Training on 25,000 examples takes time. For learning, let us use a smaller subset:

```python
from datasets import load_dataset

dataset = load_dataset("imdb")

# Use a smaller subset for faster training
# select() picks specific indices from the dataset
small_train = dataset['train'].select(range(2000))
small_test = dataset['test'].select(range(500))

print(f"Small training set: {len(small_train)} examples")
print(f"Small test set: {len(small_test)} examples")
```

**Expected output:**

```
Small training set: 2000 examples
Small test set: 500 examples
```

**Line-by-line explanation:**
- `dataset['train'].select(range(2000))` -- Picks the first 2,000 examples from the training set. `range(2000)` generates numbers 0 through 1999
- This smaller dataset trains much faster while still producing good results

---

## 12.3 Tokenizing the Data

### Why Tokenization Matters for Fine-Tuning

Before we can feed text into BERT, we must convert it to numbers. But there are important details to handle:

```
+--------------------------------------------------------------+
|           TOKENIZATION CHALLENGES                             |
+--------------------------------------------------------------+
|                                                                |
|  Problem 1: Different reviews have different lengths          |
|    "Great movie!"          --> 3 tokens                       |
|    "This was the best..."  --> 250 tokens                     |
|    BERT processes batches, so all inputs must be same length  |
|                                                                |
|  Solution: PADDING and TRUNCATION                             |
|                                                                |
|  Padding:    Add zeros to make short texts longer             |
|  Truncation: Cut long texts to fit maximum length             |
|                                                                |
|  "Great movie!"  --> [101, 2307, 3185, 999, 102, 0, 0, 0]   |
|                                              ^^^^^^^^^^^      |
|                                              padding          |
|                                                                |
+--------------------------------------------------------------+
```

### Tokenizing with Padding and Truncation

```python
from transformers import AutoTokenizer
from datasets import load_dataset

# Load the tokenizer for BERT
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Load dataset
dataset = load_dataset("imdb")
small_train = dataset['train'].select(range(2000))
small_test = dataset['test'].select(range(500))

# Define a tokenization function
def tokenize_function(examples):
    """
    Tokenize a batch of examples.

    Parameters:
        examples: A dictionary with 'text' and 'label' keys

    Returns:
        Tokenized examples with input_ids, attention_mask, etc.
    """
    return tokenizer(
        examples["text"],
        padding="max_length",
        truncation=True,
        max_length=256
    )

# Apply tokenization to the entire dataset
# The map() function applies our function to every example
tokenized_train = small_train.map(tokenize_function, batched=True)
tokenized_test = small_test.map(tokenize_function, batched=True)

print("Tokenization complete!")
print(f"Columns in tokenized data: {tokenized_train.column_names}")
print(f"First example keys: {list(tokenized_train[0].keys())}")
print(f"Input IDs length: {len(tokenized_train[0]['input_ids'])}")
```

**Expected output:**

```
Tokenization complete!
Columns in tokenized data: ['text', 'label', 'input_ids', 'token_type_ids', 'attention_mask']
First example keys: ['text', 'label', 'input_ids', 'token_type_ids', 'attention_mask']
Input IDs length: 256
```

**Line-by-line explanation:**
- `AutoTokenizer.from_pretrained("bert-base-uncased")` -- Loads BERT's tokenizer. "uncased" means all text is converted to lowercase
- `tokenizer(examples["text"], ...)` -- Tokenizes the text with several important parameters:
  - `padding="max_length"` -- Adds zeros at the end until every input is exactly `max_length` tokens long
  - `truncation=True` -- If a text is longer than `max_length`, cut it off
  - `max_length=256` -- The maximum number of tokens. BERT can handle up to 512, but 256 is faster and usually sufficient
- `small_train.map(tokenize_function, batched=True)` -- Applies the tokenization function to every example in the dataset. `batched=True` processes multiple examples at once for speed

### Understanding Padding and Attention Masks

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Tokenize a short sentence with padding
short_text = "I love this movie!"
tokens = tokenizer(short_text, padding="max_length", max_length=10,
                   truncation=True, return_tensors="pt")

print("Text:", short_text)
print("Input IDs: ", tokens["input_ids"][0].tolist())
print("Attention:  ", tokens["attention_mask"][0].tolist())

# Decode back to see what each ID means
decoded = tokenizer.convert_ids_to_tokens(tokens["input_ids"][0])
print("Tokens:     ", decoded)
```

**Expected output:**

```
Text: I love this movie!
Input IDs:  [101, 1045, 2293, 2023, 3185, 999, 102, 0, 0, 0]
Attention:   [1, 1, 1, 1, 1, 1, 1, 0, 0, 0]
Tokens:      ['[CLS]', 'i', 'love', 'this', 'movie', '!', '[SEP]', '[PAD]', '[PAD]', '[PAD]']
```

**Line-by-line explanation:**
- The sentence has 7 real tokens (including [CLS] and [SEP])
- Three `[PAD]` tokens (ID = 0) are added to reach the `max_length` of 10
- The attention mask is `1` for real tokens and `0` for padding
- The `0` in the attention mask tells the model: "ignore these positions, they are not real text"

```
+--------------------------------------------------------------+
|          PADDING AND ATTENTION MASK                           |
+--------------------------------------------------------------+
|                                                                |
|  Input IDs:    [101, 1045, 2293, 2023, 3185, 999, 102, 0, 0] |
|  Attention:    [ 1,    1,    1,    1,    1,   1,   1,  0, 0]  |
|                                                                |
|  The model:                                                    |
|    - Processes tokens where attention = 1                      |
|    - Ignores tokens where attention = 0 (padding)              |
|    - This way, padding does not affect the prediction          |
|                                                                |
+--------------------------------------------------------------+
```

---

## 12.4 Setting Up the Trainer

### What Is the Trainer API?

The Trainer is Hugging Face's high-level training loop. It handles all the complex training logic for you:

```
+--------------------------------------------------------------+
|          WHAT THE TRAINER DOES FOR YOU                        |
+--------------------------------------------------------------+
|                                                                |
|  Without Trainer (manual training loop):                      |
|    - Write your own training loop                             |
|    - Handle batching manually                                 |
|    - Compute loss and gradients yourself                      |
|    - Update weights manually                                  |
|    - Track metrics yourself                                   |
|    - Save checkpoints yourself                                |
|    - Handle GPU/CPU device placement                          |
|    = 50-100 lines of code                                     |
|                                                                |
|  With Trainer:                                                 |
|    - Configure with TrainingArguments                         |
|    - Call trainer.train()                                      |
|    - Everything else is automatic                              |
|    = 10-15 lines of code                                      |
|                                                                |
+--------------------------------------------------------------+
```

### Loading the Model for Classification

For fine-tuning, we use `AutoModelForSequenceClassification` instead of `AutoModel`. This version has an extra classification layer on top:

```python
from transformers import AutoModelForSequenceClassification

# Load BERT with a classification head on top
# num_labels=2 means two classes: negative (0) and positive (1)
model = AutoModelForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    num_labels=2
)

# Let us see the model structure
print(f"Model type: {model.config.model_type}")
print(f"Number of labels: {model.config.num_labels}")
print(f"Total parameters: {sum(p.numel() for p in model.parameters()):,}")
```

**Expected output:**

```
Model type: bert
Number of labels: 2
Total parameters: 109,483,778
```

**Line-by-line explanation:**
- `AutoModelForSequenceClassification` -- A version of AutoModel designed for classification tasks. It adds a linear layer on top of BERT that outputs scores for each class
- `num_labels=2` -- We have two classes: negative and positive
- `sum(p.numel() for p in model.parameters())` -- Counts the total number of trainable parameters. About 109 million for BERT base

### Configuring TrainingArguments

TrainingArguments controls every aspect of training:

```python
from transformers import TrainingArguments

# Define training configuration
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    warmup_steps=100,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=50,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
)

print("Training configuration set!")
print(f"  Epochs: {training_args.num_train_epochs}")
print(f"  Batch size: {training_args.per_device_train_batch_size}")
print(f"  Output directory: {training_args.output_dir}")
```

**Expected output:**

```
Training configuration set!
  Epochs: 3
  Batch size: 16
  Output directory: ./results
```

**Line-by-line explanation:**
- `output_dir="./results"` -- Where to save model checkpoints and training outputs
- `num_train_epochs=3` -- How many times to go through the entire training dataset. An epoch is one complete pass through all training data
- `per_device_train_batch_size=16` -- How many examples to process at once. Larger batches are faster but use more memory
- `per_device_eval_batch_size=16` -- Batch size for evaluation (can be larger since we do not need gradients)
- `warmup_steps=100` -- Gradually increase the learning rate for the first 100 steps. This helps training stability
- `weight_decay=0.01` -- A regularization technique that prevents the model from overfitting (memorizing training data instead of learning general patterns)
- `logging_dir="./logs"` -- Where to save training logs
- `logging_steps=50` -- Print training metrics every 50 steps
- `evaluation_strategy="epoch"` -- Evaluate the model after each epoch
- `save_strategy="epoch"` -- Save a checkpoint after each epoch
- `load_best_model_at_end=True` -- After training, load the checkpoint that performed best on evaluation

### Understanding Training Terms

```
+--------------------------------------------------------------+
|          TRAINING VOCABULARY                                  |
+--------------------------------------------------------------+
|                                                                |
|  Epoch: One complete pass through all training data           |
|    If you have 2000 examples and batch size 16:               |
|    1 epoch = 2000/16 = 125 steps                              |
|                                                                |
|  Batch: A group of examples processed together                |
|    Batch size 16 = process 16 reviews at once                 |
|                                                                |
|  Step: Processing one batch                                   |
|    Each step updates the model weights once                   |
|                                                                |
|  Learning Rate: How big each weight update is                 |
|    Too high = model overshoots, training is unstable          |
|    Too low = training takes forever                           |
|                                                                |
|  Warmup: Gradually increase learning rate at the start        |
|    Like warming up before exercise                            |
|                                                                |
|  Weight Decay: Penalty for large weights                      |
|    Prevents overfitting (memorizing training data)            |
|                                                                |
+--------------------------------------------------------------+
```

---

## 12.5 Defining Evaluation Metrics

We need to tell the Trainer how to measure the model's performance:

```python
import numpy as np
from datasets import load_metric

# Load the accuracy metric
# Accuracy = percentage of predictions that are correct
metric = load_metric("accuracy")

def compute_metrics(eval_pred):
    """
    Compute accuracy from model predictions.

    Parameters:
        eval_pred: A tuple of (predictions, labels)
            predictions: Raw model outputs (logits) for each example
            labels: True labels for each example

    Returns:
        A dictionary with the accuracy score
    """
    logits, labels = eval_pred

    # Convert logits to predicted labels
    # argmax finds the class with the highest score
    predictions = np.argmax(logits, axis=-1)

    # Compute and return accuracy
    return metric.compute(predictions=predictions, references=labels)
```

**Line-by-line explanation:**
- `load_metric("accuracy")` -- Loads a pre-built accuracy calculator
- `eval_pred` -- A tuple containing two arrays: the model's raw output scores (logits) and the true labels
- `logits, labels = eval_pred` -- Unpacks the tuple into two variables
- `np.argmax(logits, axis=-1)` -- For each example, finds which class (0 or 1) got the highest score. `axis=-1` means "along the last dimension" (the class dimension)
- `metric.compute(predictions=predictions, references=labels)` -- Compares predictions with true labels and calculates the percentage that match

> **What are logits?** Logits are the raw, unnormalized scores that the model outputs before they are converted to probabilities. For a two-class problem, the model outputs two numbers (one for each class). The class with the higher number is the prediction.

```
+--------------------------------------------------------------+
|           FROM LOGITS TO PREDICTIONS                          |
+--------------------------------------------------------------+
|                                                                |
|  Model outputs logits: [-1.5, 2.3]                            |
|                          ^     ^                               |
|                        neg   pos                               |
|                                                                |
|  argmax picks the higher one: index 1 (positive)             |
|                                                                |
|  To get probabilities, apply softmax:                         |
|    softmax([-1.5, 2.3]) = [0.02, 0.98]                       |
|    = 2% negative, 98% positive                                |
|                                                                |
+--------------------------------------------------------------+
```

---

## 12.6 Training the Model

### The Complete Training Setup

Now let us put everything together:

```python
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)
from datasets import load_dataset
import numpy as np

# ============================================================
# STEP 1: Load the dataset
# ============================================================
print("Step 1: Loading dataset...")
dataset = load_dataset("imdb")

# Use a smaller subset for faster training
small_train = dataset['train'].select(range(2000))
small_test = dataset['test'].select(range(500))

print(f"  Training examples: {len(small_train)}")
print(f"  Test examples: {len(small_test)}")

# ============================================================
# STEP 2: Load tokenizer and tokenize the data
# ============================================================
print("\nStep 2: Tokenizing data...")
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        padding="max_length",
        truncation=True,
        max_length=256
    )

tokenized_train = small_train.map(tokenize_function, batched=True)
tokenized_test = small_test.map(tokenize_function, batched=True)
print("  Tokenization complete!")

# ============================================================
# STEP 3: Load the model
# ============================================================
print("\nStep 3: Loading model...")
model = AutoModelForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    num_labels=2
)
print("  Model loaded!")

# ============================================================
# STEP 4: Define training arguments
# ============================================================
print("\nStep 4: Setting up training configuration...")
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    warmup_steps=100,
    weight_decay=0.01,
    logging_steps=50,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
)

# ============================================================
# STEP 5: Define metrics
# ============================================================
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    accuracy = (predictions == labels).mean()
    return {"accuracy": accuracy}

# ============================================================
# STEP 6: Create the Trainer
# ============================================================
print("\nStep 5: Creating Trainer...")
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_test,
    compute_metrics=compute_metrics,
)

# ============================================================
# STEP 7: Train!
# ============================================================
print("\nStep 6: Starting training...")
print("=" * 50)
trainer.train()
print("=" * 50)
print("Training complete!")
```

**Expected output:**

```
Step 1: Loading dataset...
  Training examples: 2000
  Test examples: 500

Step 2: Tokenizing data...
  Tokenization complete!

Step 3: Loading model...
  Model loaded!

Step 4: Setting up training configuration...

Step 5: Creating Trainer...

Step 6: Starting training...
==================================================
{'loss': 0.6891, 'learning_rate': 5e-05, 'epoch': 0.4}
{'loss': 0.5234, 'learning_rate': 4.2e-05, 'epoch': 0.8}
{'eval_loss': 0.3891, 'eval_accuracy': 0.8440, 'epoch': 1.0}
{'loss': 0.3102, 'learning_rate': 3.0e-05, 'epoch': 1.6}
{'eval_loss': 0.3012, 'eval_accuracy': 0.8780, 'epoch': 2.0}
{'loss': 0.1856, 'learning_rate': 1.5e-05, 'epoch': 2.4}
{'eval_loss': 0.3245, 'eval_accuracy': 0.8840, 'epoch': 3.0}
==================================================
Training complete!
```

**Key observations from the output:**
- `loss` decreases over time (from 0.69 to 0.19), meaning the model is learning
- `eval_accuracy` increases over time (from 0.84 to 0.88), meaning the model gets better at classifying reviews it has not seen before
- `learning_rate` decreases over time (this is expected with warmup and decay)

---

## 12.7 Evaluating the Model

### Running Evaluation

After training, let us evaluate the model's performance on the test set:

```python
# Evaluate the model on the test set
results = trainer.evaluate()

print("\n=== Evaluation Results ===")
print(f"Loss: {results['eval_loss']:.4f}")
print(f"Accuracy: {results['eval_accuracy']:.4f}")
print(f"This means the model correctly classifies "
      f"{results['eval_accuracy']*100:.1f}% of reviews")
```

**Expected output:**

```
=== Evaluation Results ===
Loss: 0.3012
Accuracy: 0.8840
This means the model correctly classifies 88.4% of reviews
```

### Testing on Your Own Reviews

```python
from transformers import pipeline

# Create a pipeline using our fine-tuned model
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model=model,
    tokenizer=tokenizer
)

# Test with custom reviews
test_reviews = [
    "This movie was absolutely fantastic! The acting was superb.",
    "Terrible film. I wasted two hours of my life.",
    "It was okay. Not great, not terrible. Just average.",
    "The plot was confusing but the visuals were stunning.",
    "Best movie I have seen this year! Highly recommended!"
]

print("=== Testing Our Fine-Tuned Model ===\n")
for review in test_reviews:
    result = sentiment_pipeline(review)
    label = result[0]['label']
    score = result[0]['score']

    # Map LABEL_0/LABEL_1 to negative/positive
    sentiment = "POSITIVE" if label == "LABEL_1" else "NEGATIVE"

    print(f"Review: {review}")
    print(f"  Prediction: {sentiment} (confidence: {score:.4f})")
    print()
```

**Expected output:**

```
=== Testing Our Fine-Tuned Model ===

Review: This movie was absolutely fantastic! The acting was superb.
  Prediction: POSITIVE (confidence: 0.9987)

Review: Terrible film. I wasted two hours of my life.
  Prediction: NEGATIVE (confidence: 0.9965)

Review: It was okay. Not great, not terrible. Just average.
  Prediction: NEGATIVE (confidence: 0.6234)

Review: The plot was confusing but the visuals were stunning.
  Prediction: POSITIVE (confidence: 0.7102)

Review: Best movie I have seen this year! Highly recommended!
  Prediction: POSITIVE (confidence: 0.9991)
```

Notice that the model is very confident about clearly positive or negative reviews but less certain about ambiguous ones.

---

## 12.8 Saving and Loading the Fine-Tuned Model

### Saving the Model

```python
# Save the fine-tuned model and tokenizer
save_directory = "./fine_tuned_sentiment_model"

model.save_pretrained(save_directory)
tokenizer.save_pretrained(save_directory)

print(f"Model saved to: {save_directory}")

# List the saved files
import os
files = os.listdir(save_directory)
print(f"Saved files: {files}")
```

**Expected output:**

```
Model saved to: ./fine_tuned_sentiment_model
Saved files: ['config.json', 'model.safetensors', 'tokenizer.json',
              'tokenizer_config.json', 'vocab.txt', 'special_tokens_map.json']
```

**Line-by-line explanation:**
- `model.save_pretrained(save_directory)` -- Saves the model weights and configuration
- `tokenizer.save_pretrained(save_directory)` -- Saves the tokenizer files
- The saved files include:
  - `config.json` -- Model architecture configuration
  - `model.safetensors` -- The trained model weights
  - `tokenizer.json` and related files -- The tokenizer vocabulary and settings

### Loading the Saved Model

```python
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    pipeline
)

# Load the saved model and tokenizer
save_directory = "./fine_tuned_sentiment_model"
loaded_tokenizer = AutoTokenizer.from_pretrained(save_directory)
loaded_model = AutoModelForSequenceClassification.from_pretrained(save_directory)

# Create a pipeline with the loaded model
loaded_pipeline = pipeline(
    "sentiment-analysis",
    model=loaded_model,
    tokenizer=loaded_tokenizer
)

# Test it
result = loaded_pipeline("This loaded model works perfectly!")
print(f"Result: {result}")
```

**Expected output:**

```
Result: [{'label': 'LABEL_1', 'score': 0.9978}]
```

### Adding Label Names

By default, the model uses generic labels like LABEL_0 and LABEL_1. Let us fix that:

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

save_directory = "./fine_tuned_sentiment_model"

# Load model with proper label names
model = AutoModelForSequenceClassification.from_pretrained(save_directory)

# Set human-readable label names
model.config.id2label = {0: "NEGATIVE", 1: "POSITIVE"}
model.config.label2id = {"NEGATIVE": 0, "POSITIVE": 1}

# Save again with the updated config
model.save_pretrained(save_directory)

# Now the pipeline will use readable labels
tokenizer = AutoTokenizer.from_pretrained(save_directory)
classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

result = classifier("I absolutely loved this film!")
print(f"Result: {result}")
```

**Expected output:**

```
Result: [{'label': 'POSITIVE', 'score': 0.9993}]
```

---

## 12.9 Complete Movie Review Classifier

Here is the complete, self-contained code for the movie review sentiment classifier:

```python
"""
Complete Movie Review Sentiment Classifier
Using BERT fine-tuned on the IMDB dataset.
"""

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    pipeline
)
from datasets import load_dataset
import numpy as np

# ============================================================
# Configuration
# ============================================================
MODEL_NAME = "bert-base-uncased"
MAX_LENGTH = 256
TRAIN_SIZE = 2000       # Use full 25000 for production
TEST_SIZE = 500         # Use full 25000 for production
EPOCHS = 3
BATCH_SIZE = 16
SAVE_DIR = "./movie_sentiment_model"

# ============================================================
# 1. Load and prepare data
# ============================================================
print("Loading IMDB dataset...")
dataset = load_dataset("imdb")
train_data = dataset["train"].select(range(TRAIN_SIZE))
test_data = dataset["test"].select(range(TEST_SIZE))

# ============================================================
# 2. Tokenize
# ============================================================
print("Tokenizing...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def tokenize(examples):
    return tokenizer(examples["text"], padding="max_length",
                     truncation=True, max_length=MAX_LENGTH)

train_data = train_data.map(tokenize, batched=True)
test_data = test_data.map(tokenize, batched=True)

# ============================================================
# 3. Load model
# ============================================================
print("Loading model...")
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME, num_labels=2
)
model.config.id2label = {0: "NEGATIVE", 1: "POSITIVE"}
model.config.label2id = {"NEGATIVE": 0, "POSITIVE": 1}

# ============================================================
# 4. Setup training
# ============================================================
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    warmup_steps=100,
    weight_decay=0.01,
    logging_steps=50,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    accuracy = (preds == labels).mean()
    return {"accuracy": accuracy}

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_data,
    eval_dataset=test_data,
    compute_metrics=compute_metrics,
)

# ============================================================
# 5. Train and evaluate
# ============================================================
print("Training...")
trainer.train()

print("\nEvaluation:")
results = trainer.evaluate()
print(f"  Accuracy: {results['eval_accuracy']:.4f}")

# ============================================================
# 6. Save the model
# ============================================================
model.save_pretrained(SAVE_DIR)
tokenizer.save_pretrained(SAVE_DIR)
print(f"\nModel saved to {SAVE_DIR}")

# ============================================================
# 7. Test the model
# ============================================================
print("\n=== Testing the Fine-Tuned Model ===\n")
classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

test_reviews = [
    "One of the best films I have ever seen!",
    "Complete waste of time. Avoid at all costs.",
    "Decent movie but could have been better.",
]

for review in test_reviews:
    result = classifier(review)
    print(f"  '{review}'")
    print(f"  --> {result[0]['label']} ({result[0]['score']:.4f})\n")
```

**Expected output:**

```
Loading IMDB dataset...
Tokenizing...
Loading model...
Training...
[training progress bars and metrics]

Evaluation:
  Accuracy: 0.8840

Model saved to ./movie_sentiment_model

=== Testing the Fine-Tuned Model ===

  'One of the best films I have ever seen!'
  --> POSITIVE (0.9992)

  'Complete waste of time. Avoid at all costs.'
  --> NEGATIVE (0.9988)

  'Decent movie but could have been better.'
  --> POSITIVE (0.6543)
```

---

## Common Mistakes

1. **Using `AutoModel` instead of `AutoModelForSequenceClassification`.** The plain `AutoModel` does not have a classification head. You need the task-specific version for fine-tuning.

2. **Forgetting to set `num_labels`.** If you do not specify `num_labels`, the model defaults to 2 labels. For multi-class problems (3 or more classes), you must set this parameter.

3. **Using too large a `max_length`.** Setting `max_length=512` (BERT's maximum) uses four times more memory than `max_length=128`. Start small and increase only if accuracy suffers.

4. **Training for too many epochs.** With pre-trained models, 2-5 epochs is usually enough. Training for 20+ epochs often leads to overfitting, where the model memorizes training data but performs poorly on new data.

5. **Not using `load_best_model_at_end=True`.** Without this, the Trainer keeps the model from the last epoch, which might not be the best one. The middle epochs sometimes perform better.

---

## Best Practices

1. **Start with a small subset.** Train on 1,000-2,000 examples first to make sure everything works. Then scale up to the full dataset.

2. **Monitor evaluation loss.** If training loss keeps decreasing but evaluation loss starts increasing, your model is overfitting. Stop training or reduce epochs.

3. **Use DistilBERT for faster experiments.** Replace `"bert-base-uncased"` with `"distilbert-base-uncased"` for a model that is 60% smaller and trains much faster with minimal accuracy loss.

4. **Set a random seed for reproducibility.** Add `seed=42` to TrainingArguments so you get the same results each time you train.

5. **Save your model frequently.** Use `save_strategy="epoch"` to save after each epoch. If training crashes, you can resume from the last checkpoint.

---

## Quick Summary

Fine-tuning takes a pre-trained model like BERT and adapts it to your specific task using your own data. The process involves loading a dataset, tokenizing the text with proper padding and truncation, configuring training with TrainingArguments, and using the Trainer API to handle the training loop. For classification tasks, use `AutoModelForSequenceClassification` which adds a classification layer on top of BERT. With just 2,000 training examples and 3 epochs, you can achieve over 88% accuracy on movie review sentiment classification. Save your fine-tuned model with `save_pretrained()` and load it later for predictions.

---

## Key Points

- Fine-tuning adapts a pre-trained model to a specific task, requiring far less data and time than training from scratch
- Use `AutoModelForSequenceClassification` for classification tasks -- it adds a classification head on top of BERT
- Tokenization must include padding (to equalize lengths) and truncation (to handle long texts)
- The attention mask tells the model which tokens are real (1) and which are padding (0)
- TrainingArguments controls epochs, batch size, learning rate, and saving behavior
- The Trainer API handles the entire training loop automatically
- Monitor both training loss (should decrease) and evaluation accuracy (should increase)
- `load_best_model_at_end=True` ensures you keep the best-performing checkpoint
- Save models with `save_pretrained()` for later use without retraining

---

## Practice Questions

1. What is the difference between pre-training and fine-tuning? Why is fine-tuning so much faster and cheaper than training from scratch?

2. Explain what padding and truncation do during tokenization. Why are both necessary when fine-tuning a model?

3. What is the attention mask, and why is it important when we use padding? What would happen if we did not use it?

4. You fine-tuned a model for 10 epochs. The training loss is very low (0.01) but the evaluation accuracy dropped from 89% at epoch 3 to 82% at epoch 10. What happened, and how would you fix it?

5. What is the purpose of `warmup_steps` in TrainingArguments? Why not just start with the full learning rate immediately?

---

## Exercises

### Exercise 1: Fine-Tune DistilBERT

Repeat the movie review classification task but use `"distilbert-base-uncased"` instead of `"bert-base-uncased"`. Compare the training time and accuracy. How much faster is DistilBERT? How much accuracy do you lose?

### Exercise 2: Multi-Class Classification

Modify the complete example to classify text into 3 categories instead of 2. Use the `"ag_news"` dataset from Hugging Face (news articles classified as World, Sports, Business, or Science/Tech -- 4 classes). You will need to change `num_labels` and update the label mapping.

**Hint:** Load the dataset with `load_dataset("ag_news")` and set `num_labels=4`.

### Exercise 3: Experiment with Hyperparameters

Using the IMDB dataset, train three models with different settings:
- Model A: learning_rate=2e-5, epochs=2, batch_size=8
- Model B: learning_rate=5e-5, epochs=3, batch_size=16
- Model C: learning_rate=1e-4, epochs=5, batch_size=32

Compare their evaluation accuracy. Which configuration works best? Why do you think that is?

---

## What Is Next?

You have learned how to fine-tune BERT for classification -- one of the most practical skills in NLP. In the next chapter, we will explore another powerful application of transformers: **Question Answering**. You will learn how to build a system that can read a passage of text and answer questions about it, just like a reading comprehension test. This is the technology behind virtual assistants and search engines that give direct answers to your questions.
