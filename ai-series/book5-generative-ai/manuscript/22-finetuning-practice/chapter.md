# Chapter 22: Fine-Tuning in Practice

## What You Will Learn

In this chapter, you will learn:

- How to install and use the Hugging Face PEFT library for parameter-efficient fine-tuning
- How to load a base model and tokenizer from the Hugging Face Hub
- How to create a LoRA configuration and attach it to a model
- How to prepare a custom dataset for instruction fine-tuning
- How to train a model using SFTTrainer (Supervised Fine-Tuning Trainer)
- How to merge LoRA adapters back into the base model
- How to save, load, and share your fine-tuned model

## Why This Chapter Matters

In the previous chapter, you learned the theory behind LoRA and QLoRA. Now it is time to get your hands dirty. Think of Chapter 21 as reading the driver's manual and this chapter as actually driving the car.

Fine-tuning is how you make a general-purpose language model into YOUR model. Want a model that writes in your company's style? Fine-tune it. Need a model that understands medical terminology? Fine-tune it. Want a chatbot that follows specific instructions perfectly? Fine-tune it.

This chapter gives you the complete, practical workflow from start to finish. By the end, you will have fine-tuned a real language model on custom data -- something that would have required a team of engineers and thousands of dollars just a few years ago.

---

## 22.1 Setting Up the Environment

### Installing the Required Libraries

You need several libraries that work together:

```python
# Install all required libraries
# Run these commands in your terminal

# pip install transformers     # Hugging Face model library
# pip install peft             # Parameter-Efficient Fine-Tuning (LoRA)
# pip install trl              # Transformer Reinforcement Learning (SFTTrainer)
# pip install datasets         # Hugging Face datasets library
# pip install bitsandbytes     # For QLoRA (4-bit quantization)
# pip install accelerate       # For distributed training support
# pip install torch            # PyTorch (deep learning framework)

# Or install everything at once:
# pip install transformers peft trl datasets bitsandbytes accelerate torch
```

```
+---------------------------------------------------------------+
|              THE FINE-TUNING TOOLKIT                          |
+---------------------------------------------------------------+
|                                                               |
|  transformers  --> Load and use pre-trained models             |
|  peft          --> Add LoRA adapters to models                 |
|  trl           --> SFTTrainer for supervised fine-tuning        |
|  datasets      --> Load and process training data              |
|  bitsandbytes  --> 4-bit quantization for QLoRA                |
|  accelerate    --> Handle GPU memory and distributed training   |
|                                                               |
|  Think of it like a kitchen:                                  |
|  transformers  = The oven (core tool)                          |
|  peft          = Special attachments for the oven              |
|  trl           = The recipe book                               |
|  datasets      = The ingredients                               |
|  bitsandbytes  = A space-saving organizer                      |
|  accelerate    = An extra pair of hands                        |
|                                                               |
+---------------------------------------------------------------+
```

### Verifying the Installation

```python
# Verify all libraries are installed
import transformers
import peft
import trl
import datasets
import torch

print(f"transformers: {transformers.__version__}")
print(f"peft:         {peft.__version__}")
print(f"trl:          {trl.__version__}")
print(f"datasets:     {datasets.__version__}")
print(f"torch:        {torch.__version__}")
print(f"CUDA:         {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"GPU:          {torch.cuda.get_device_name(0)}")
    vram = torch.cuda.get_device_properties(0).total_mem / (1024**3)
    print(f"VRAM:         {vram:.1f} GB")
```

**Expected output:**

```
transformers: 4.46.0
peft:         0.13.0
trl:          0.12.0
datasets:     3.1.0
torch:        2.5.0
CUDA:         True
GPU:          NVIDIA GeForce RTX 4090
VRAM:         24.0 GB
```

---

## 22.2 Loading the Base Model

### Choosing a Base Model

For learning purposes, we will use a small model. In production, you would use a larger one:

```
+---------------------------------------------------------------+
|              CHOOSING A BASE MODEL                            |
+---------------------------------------------------------------+
|                                                               |
|  For Learning (this chapter):                                 |
|  - microsoft/phi-2 (2.7B) -- Small, fast, good quality        |
|  - TinyLlama/TinyLlama-1.1B-Chat-v1.0 -- Very small          |
|  - facebook/opt-350m -- Tiny, great for testing                |
|                                                               |
|  For Production:                                              |
|  - meta-llama/Llama-3.1-8B -- Strong general model            |
|  - mistralai/Mistral-7B-v0.3 -- Fast and capable              |
|  - Qwen/Qwen2.5-7B -- Great multilingual model                |
|                                                               |
+---------------------------------------------------------------+
```

### Loading a Model in Standard Precision

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

# Choose a small model for demonstration
model_name = "facebook/opt-350m"

# Load the tokenizer
# The tokenizer converts text to numbers and back
tokenizer = AutoTokenizer.from_pretrained(model_name)
print(f"Tokenizer loaded: {model_name}")
print(f"Vocabulary size: {tokenizer.vocab_size:,}")

# Load the model
# This downloads the model weights from Hugging Face
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,   # Use half precision to save memory
    device_map="auto",           # Automatically place on GPU
)

# Check model size
total_params = sum(p.numel() for p in model.parameters())
print(f"\nModel loaded: {model_name}")
print(f"Total parameters: {total_params:,}")
print(f"Model size (fp16): {total_params * 2 / (1024**3):.2f} GB")
```

**Expected output:**

```
Tokenizer loaded: facebook/opt-350m
Vocabulary size: 50,265

Model loaded: facebook/opt-350m
Total parameters: 331,195,392
Model size (fp16): 0.62 GB
```

**Line-by-line explanation:**

- `AutoModelForCausalLM` -- Automatically loads the right model class for causal language modeling (text generation). "Causal" means the model generates text left to right
- `AutoTokenizer` -- Automatically loads the matching tokenizer for the model
- `from_pretrained(model_name)` -- Downloads the model from Hugging Face Hub (or loads from cache if already downloaded)
- `torch_dtype=torch.float16` -- Stores model weights in 16-bit floating point, using half the memory of 32-bit
- `device_map="auto"` -- Automatically places the model on the GPU if available, or CPU otherwise

### Loading a Model with QLoRA (4-Bit)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

# QLoRA quantization configuration
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,              # Load model in 4-bit precision
    bnb_4bit_quant_type="nf4",      # Use NormalFloat4 quantization
    bnb_4bit_compute_dtype=torch.float16,  # Compute in fp16
    bnb_4bit_use_double_quant=True, # Double quantization for extra savings
)

model_name = "facebook/opt-350m"

# Load tokenizer (same as before)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Load model with 4-bit quantization
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,  # Apply 4-bit quantization
    device_map="auto",
)

# Check memory usage
total_params = sum(p.numel() for p in model.parameters())
print(f"Model: {model_name}")
print(f"Parameters: {total_params:,}")
print(f"Quantized model size: ~{total_params * 0.5 / (1024**3):.2f} GB (4-bit)")
```

**Expected output:**

```
Model: facebook/opt-350m
Parameters: 331,195,392
Quantized model size: ~0.15 GB (4-bit)
```

**Line-by-line explanation:**

- `BitsAndBytesConfig` -- Configuration object that tells the model how to quantize itself
- `load_in_4bit=True` -- Store each weight using only 4 bits instead of 16 or 32
- `bnb_4bit_quant_type="nf4"` -- Use the NormalFloat4 format designed specifically for neural network weights (see Chapter 21)
- `bnb_4bit_compute_dtype=torch.float16` -- Even though weights are stored in 4-bit, computations happen in fp16 for accuracy
- `bnb_4bit_use_double_quant=True` -- Also quantize the quantization constants for extra memory savings
- `quantization_config=bnb_config` -- Pass the configuration to the model loader

---

## 22.3 Creating the LoRA Configuration

### Setting Up LoRA with PEFT

```python
from peft import LoraConfig, get_peft_model, TaskType

# Create the LoRA configuration
lora_config = LoraConfig(
    r=16,                          # Rank: size of the LoRA matrices
    lora_alpha=32,                 # Alpha: scaling factor (2x rank is common)
    lora_dropout=0.05,             # Dropout: prevents overfitting
    target_modules=["q_proj", "v_proj"],  # Which layers to adapt
    bias="none",                   # Do not train bias terms
    task_type=TaskType.CAUSAL_LM,  # Task: text generation
)

print("LoRA Configuration:")
print(f"  Rank (r):          {lora_config.r}")
print(f"  Alpha:             {lora_config.lora_alpha}")
print(f"  Dropout:           {lora_config.lora_dropout}")
print(f"  Target modules:    {lora_config.target_modules}")
print(f"  Bias:              {lora_config.bias}")
print(f"  Task type:         {lora_config.task_type}")
```

**Expected output:**

```
LoRA Configuration:
  Rank (r):          16
  Alpha:             32
  Dropout:           0.05
  Target modules:    ['q_proj', 'v_proj']
  Bias:              none
  Task type:         CAUSAL_LM
```

### Attaching LoRA to the Model

```python
# Attach LoRA adapters to the model
model = get_peft_model(model, lora_config)

# Print trainable parameters summary
model.print_trainable_parameters()
```

**Expected output:**

```
trainable params: 1,572,864 || all params: 332,768,256 || trainable%: 0.4728
```

**Line-by-line explanation:**

- `get_peft_model(model, lora_config)` -- This is the magic line. It takes our base model and wraps it with LoRA adapters. The original weights are frozen, and only the new LoRA matrices are trainable
- `model.print_trainable_parameters()` -- Shows how many parameters are trainable vs frozen. Notice only 0.47% of parameters are trainable -- the rest are frozen

```
+---------------------------------------------------------------+
|              WHAT get_peft_model DOES                         |
+---------------------------------------------------------------+
|                                                               |
|  Before:                                                      |
|  +------------------------------------------+                |
|  |  Original Model                          |                |
|  |  All 331M parameters TRAINABLE           |                |
|  +------------------------------------------+                |
|                                                               |
|  After get_peft_model():                                     |
|  +------------------------------------------+                |
|  |  Original Model (FROZEN)                 |                |
|  |  331M parameters -- NOT trained          |                |
|  |  +------------------------------------+  |                |
|  |  |  LoRA Adapters (TRAINABLE)         |  |                |
|  |  |  1.6M parameters -- trained        |  |                |
|  |  +------------------------------------+  |                |
|  +------------------------------------------+                |
|                                                               |
+---------------------------------------------------------------+
```

### Finding the Right Target Modules

If you are unsure what the layer names are for your model, you can inspect the model:

```python
# Find all linear layer names in the model
def find_target_modules(model):
    """Find all linear layer names that can be targeted by LoRA."""
    target_modules = set()
    for name, module in model.named_modules():
        if isinstance(module, torch.nn.Linear):
            # Get the last part of the name (e.g., "q_proj" from "model.layers.0.self_attn.q_proj")
            layer_name = name.split(".")[-1]
            target_modules.add(layer_name)
    return list(target_modules)

# Print available target modules
modules = find_target_modules(model)
print("Available target modules:")
for m in sorted(modules):
    print(f"  - {m}")
```

**Expected output:**

```
Available target modules:
  - fc1
  - fc2
  - k_proj
  - lm_head
  - out_proj
  - q_proj
  - v_proj
```

---

## 22.4 Preparing the Training Data

### Dataset Formats

For instruction fine-tuning, your data needs to be in a specific format:

```
+---------------------------------------------------------------+
|              COMMON DATA FORMATS                              |
+---------------------------------------------------------------+
|                                                               |
|  Format 1: Instruction-Response                               |
|  {                                                            |
|    "instruction": "What is the capital of France?",           |
|    "response": "The capital of France is Paris."              |
|  }                                                            |
|                                                               |
|  Format 2: Instruction-Input-Response                         |
|  {                                                            |
|    "instruction": "Summarize the following text",             |
|    "input": "The quick brown fox...",                         |
|    "response": "A fox jumps over a dog."                      |
|  }                                                            |
|                                                               |
|  Format 3: Chat/Conversation                                  |
|  {                                                            |
|    "messages": [                                              |
|      {"role": "user", "content": "What is AI?"},             |
|      {"role": "assistant", "content": "AI is..."}            |
|    ]                                                          |
|  }                                                            |
|                                                               |
+---------------------------------------------------------------+
```

### Creating a Custom Dataset

```python
from datasets import Dataset

# Create a simple instruction dataset
# In production, you would load from a file or the Hugging Face Hub

training_data = [
    {
        "instruction": "What is machine learning?",
        "response": "Machine learning is a branch of artificial intelligence where computers learn patterns from data instead of being explicitly programmed. For example, instead of writing rules to detect spam emails, you show the computer thousands of spam and non-spam emails, and it learns the patterns itself."
    },
    {
        "instruction": "Explain the difference between supervised and unsupervised learning.",
        "response": "Supervised learning uses labeled data where each input has a known correct answer, like predicting house prices from features. Unsupervised learning finds hidden patterns in unlabeled data, like grouping customers by shopping behavior without predefined categories."
    },
    {
        "instruction": "What is a neural network?",
        "response": "A neural network is a computing system inspired by the human brain. It consists of layers of connected nodes (neurons) that process information. Data flows through the network, getting transformed at each layer until it produces an output like a classification or prediction."
    },
    {
        "instruction": "What is overfitting?",
        "response": "Overfitting happens when a model memorizes the training data instead of learning general patterns. It performs well on training data but poorly on new, unseen data. It is like a student who memorizes test answers instead of understanding the subject -- they fail when questions change."
    },
    {
        "instruction": "What is a loss function?",
        "response": "A loss function measures how wrong a model's predictions are. It calculates the difference between what the model predicted and the correct answer. During training, the model adjusts its weights to minimize this loss, gradually getting better at its task."
    },
]

# Convert to a Hugging Face Dataset
dataset = Dataset.from_list(training_data)
print(f"Dataset size: {len(dataset)} examples")
print(f"Columns: {dataset.column_names}")
print(f"\nFirst example:")
print(f"  Instruction: {dataset[0]['instruction']}")
print(f"  Response:    {dataset[0]['response'][:80]}...")
```

**Expected output:**

```
Dataset size: 5 examples
Columns: ['instruction', 'response']

First example:
  Instruction: What is machine learning?
  Response:    Machine learning is a branch of artificial intelligence where computers learn pa...
```

### Formatting the Data for Training

The model needs the data in a specific text format. We create a **formatting function** that combines the instruction and response into a single string:

```python
def format_instruction(example):
    """Format a single example into the instruction template."""

    # This is a common instruction template
    # Different models use different templates
    text = f"""### Instruction:
{example['instruction']}

### Response:
{example['response']}"""

    return {"text": text}

# Apply formatting to the entire dataset
formatted_dataset = dataset.map(format_instruction)

# Show what the formatted data looks like
print("Formatted example:")
print("-" * 50)
print(formatted_dataset[0]["text"])
print("-" * 50)
```

**Expected output:**

```
Formatted example:
--------------------------------------------------
### Instruction:
What is machine learning?

### Response:
Machine learning is a branch of artificial intelligence where computers learn patterns from data instead of being explicitly programmed. For example, instead of writing rules to detect spam emails, you show the computer thousands of spam and non-spam emails, and it learns the patterns itself.
--------------------------------------------------
```

**Line-by-line explanation:**

- `format_instruction(example)` -- Takes one data example and formats it into a text string
- The template uses `### Instruction:` and `### Response:` as markers. The model learns to generate text after `### Response:` when given a `### Instruction:`
- `dataset.map(format_instruction)` -- Applies the formatting function to every example in the dataset

### Loading a Dataset from Hugging Face Hub

For real fine-tuning, you would use a larger dataset:

```python
from datasets import load_dataset

# Load a popular instruction dataset from Hugging Face
# This dataset has 52,000 instruction-response pairs
dataset = load_dataset("tatsu-lab/alpaca", split="train")

print(f"Dataset size: {len(dataset):,} examples")
print(f"Columns: {dataset.column_names}")
print(f"\nExample:")
print(f"  Instruction: {dataset[0]['instruction']}")
print(f"  Input:       {dataset[0]['input']}")
print(f"  Output:      {dataset[0]['output'][:100]}...")
```

**Expected output:**

```
Dataset size: 52,002 examples
Columns: ['instruction', 'input', 'output']

Example:
  Instruction: Give three tips for staying healthy.
  Input:
  Output:      1.Eat a balanced diet and make sure to include plenty of fruits and vegetables.
2. Exercise re...
```

---

## 22.5 Training with SFTTrainer

### What Is SFTTrainer?

SFTTrainer (Supervised Fine-Tuning Trainer) is a high-level training class from the `trl` library that handles all the training complexity for you:

```
+---------------------------------------------------------------+
|              WHAT SFTTrainer HANDLES                          |
+---------------------------------------------------------------+
|                                                               |
|  Without SFTTrainer (manual):          With SFTTrainer:       |
|  - Write training loop                 - Configure and go     |
|  - Handle gradient accumulation        - Automatic            |
|  - Manage mixed precision              - Automatic            |
|  - Save checkpoints                    - Automatic            |
|  - Log metrics                         - Automatic            |
|  - Handle data loading                 - Automatic            |
|  - Manage learning rate schedule       - Automatic            |
|                                                               |
|  SFTTrainer = "I handle the boring parts,                     |
|               you focus on the important parts"               |
|                                                               |
+---------------------------------------------------------------+
```

### Setting Up Training Arguments

```python
from transformers import TrainingArguments

# Define training configuration
training_args = TrainingArguments(
    # Where to save model checkpoints
    output_dir="./results",

    # Training duration
    num_train_epochs=3,              # Number of passes through the data
    max_steps=-1,                    # -1 means use num_train_epochs instead

    # Batch size
    per_device_train_batch_size=4,   # Samples per GPU per step
    gradient_accumulation_steps=4,   # Accumulate gradients over 4 steps
    # Effective batch size = 4 * 4 = 16

    # Learning rate
    learning_rate=2e-4,              # Starting learning rate
    weight_decay=0.01,               # L2 regularization
    warmup_steps=100,                # Gradually increase LR for 100 steps

    # Memory optimization
    fp16=True,                       # Use 16-bit training
    gradient_checkpointing=True,     # Trade compute for memory

    # Logging
    logging_steps=10,                # Log every 10 steps
    logging_dir="./logs",            # Where to save logs

    # Saving
    save_strategy="steps",           # Save by step count
    save_steps=500,                  # Save every 500 steps
    save_total_limit=3,              # Keep only last 3 checkpoints

    # Evaluation
    eval_strategy="no",              # No evaluation during training

    # Reproducibility
    seed=42,                         # Random seed for reproducibility

    # Report metrics to console
    report_to="none",                # Disable wandb/tensorboard
)

print("Training configuration:")
print(f"  Epochs:           {training_args.num_train_epochs}")
print(f"  Batch size:       {training_args.per_device_train_batch_size}")
print(f"  Grad accumulation: {training_args.gradient_accumulation_steps}")
print(f"  Effective batch:  {training_args.per_device_train_batch_size * training_args.gradient_accumulation_steps}")
print(f"  Learning rate:    {training_args.learning_rate}")
print(f"  FP16:             {training_args.fp16}")
```

**Expected output:**

```
Training configuration:
  Epochs:           3
  Batch size:       4
  Grad accumulation: 4
  Effective batch:  16
  Learning rate:    0.0002
  FP16:             True
```

**Line-by-line explanation:**

- `output_dir` -- Directory where checkpoints and the final model will be saved
- `num_train_epochs=3` -- Go through the entire dataset 3 times. More epochs mean more training but risk overfitting
- `per_device_train_batch_size=4` -- Process 4 examples at a time per GPU. Larger batch sizes need more memory
- `gradient_accumulation_steps=4` -- Instead of updating weights every 4 examples, accumulate gradients over 4 batches (16 examples) before updating. This simulates a larger batch size without needing more memory
- `learning_rate=2e-4` -- 0.0002, a common starting point for LoRA fine-tuning. Too high causes instability, too low causes slow learning
- `warmup_steps=100` -- Start with a very small learning rate and gradually increase to the target over 100 steps. This prevents early training from being too aggressive
- `fp16=True` -- Use 16-bit floating point for training computations. This halves memory usage with minimal quality loss
- `gradient_checkpointing=True` -- A memory optimization that recomputes intermediate values instead of storing them. Uses ~30% less memory at the cost of ~20% slower training

### Running the Training

```python
from trl import SFTTrainer

# Create the trainer
trainer = SFTTrainer(
    model=model,                     # The model with LoRA adapters
    args=training_args,              # Training configuration
    train_dataset=formatted_dataset, # The formatted training data
    tokenizer=tokenizer,             # The tokenizer
    dataset_text_field="text",       # Column containing the formatted text
    max_seq_length=512,              # Maximum sequence length
    packing=False,                   # Do not pack multiple examples into one sequence
)

# Start training
print("Starting training...")
train_result = trainer.train()

# Print training summary
print(f"\nTraining complete!")
print(f"  Total steps: {train_result.global_step}")
print(f"  Training loss: {train_result.training_loss:.4f}")
print(f"  Training time: {train_result.metrics['train_runtime']:.1f} seconds")
```

**Expected output:**

```
Starting training...
[30/30 00:45, Epoch 3/3]
Step    Training Loss
10      2.4531
20      1.8672
30      1.5234

Training complete!
  Total steps: 30
  Training loss: 1.9479
  Training time: 45.3 seconds
```

**Line-by-line explanation:**

- `SFTTrainer` -- The supervised fine-tuning trainer that handles the entire training loop
- `model=model` -- Our model with LoRA adapters already attached
- `train_dataset=formatted_dataset` -- The dataset we formatted earlier
- `dataset_text_field="text"` -- Tells the trainer which column contains the text to train on
- `max_seq_length=512` -- Truncate sequences longer than 512 tokens. Longer sequences need more memory
- `packing=False` -- Each example is processed individually. Setting to True would pack short examples together for efficiency
- `trainer.train()` -- This single line runs the entire training loop: batching, forward pass, loss computation, backward pass, weight updates, checkpointing, and logging

---

## 22.6 Complete Fine-Tuning Example

Here is a complete, end-to-end example that you can run:

```python
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    BitsAndBytesConfig,
)
from peft import LoraConfig, get_peft_model, TaskType
from trl import SFTTrainer
from datasets import Dataset

# ============================================
# Step 1: Configuration
# ============================================
model_name = "facebook/opt-350m"    # Small model for demonstration
output_dir = "./my-finetuned-model"

# ============================================
# Step 2: Load the base model with QLoRA
# ============================================
print("Step 2: Loading base model...")

# 4-bit quantization config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token  # Set padding token
tokenizer.padding_side = "right"           # Pad on the right side

# Load model
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto",
)

print(f"  Model loaded: {model_name}")

# ============================================
# Step 3: Add LoRA adapters
# ============================================
print("Step 3: Adding LoRA adapters...")

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    target_modules=["q_proj", "v_proj"],
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# ============================================
# Step 4: Prepare training data
# ============================================
print("Step 4: Preparing training data...")

# Sample instruction-following dataset
data = [
    {"instruction": "Explain what Python is.", "response": "Python is a high-level programming language known for its simple, readable syntax. It is widely used in web development, data science, artificial intelligence, and automation. Python's design philosophy emphasizes code readability, making it an excellent choice for beginners."},
    {"instruction": "What is a variable in programming?", "response": "A variable is a named container that stores a value in a computer's memory. Think of it as a labeled box where you can put information. For example, 'age = 25' creates a variable called 'age' and stores the number 25 in it."},
    {"instruction": "Describe what an API is.", "response": "An API (Application Programming Interface) is a set of rules that allows different software programs to communicate with each other. Think of it as a waiter in a restaurant -- you tell the waiter what you want (your request), and they bring it from the kitchen (the server)."},
    {"instruction": "What is version control?", "response": "Version control is a system that tracks changes to files over time. It lets you go back to previous versions, see who made changes, and collaborate with others without overwriting each other's work. Git is the most popular version control system."},
    {"instruction": "Explain what a database is.", "response": "A database is an organized collection of data stored electronically. It allows you to efficiently store, retrieve, update, and delete information. Think of it as a digital filing cabinet where data is organized into tables with rows and columns."},
]

# Format the data
def format_example(example):
    return {"text": f"### Instruction:\n{example['instruction']}\n\n### Response:\n{example['response']}"}

dataset = Dataset.from_list(data)
dataset = dataset.map(format_example)
print(f"  Dataset size: {len(dataset)} examples")

# ============================================
# Step 5: Configure training
# ============================================
print("Step 5: Configuring training...")

training_args = TrainingArguments(
    output_dir=output_dir,
    num_train_epochs=3,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=2,
    learning_rate=2e-4,
    fp16=True,
    logging_steps=5,
    save_strategy="epoch",
    report_to="none",
    seed=42,
)

# ============================================
# Step 6: Train
# ============================================
print("Step 6: Starting training...")

trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=tokenizer,
    dataset_text_field="text",
    max_seq_length=256,
)

result = trainer.train()
print(f"  Training loss: {result.training_loss:.4f}")

# ============================================
# Step 7: Save the LoRA adapters
# ============================================
print("Step 7: Saving LoRA adapters...")
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)
print(f"  Adapters saved to: {output_dir}")

print("\nFine-tuning complete!")
```

**Expected output:**

```
Step 2: Loading base model...
  Model loaded: facebook/opt-350m
Step 3: Adding LoRA adapters...
trainable params: 1,572,864 || all params: 332,768,256 || trainable%: 0.4728
Step 4: Preparing training data...
  Dataset size: 5 examples
Step 5: Configuring training...
Step 6: Starting training...
[9/9 00:12, Epoch 3/3]
  Training loss: 1.8234
Step 7: Saving LoRA adapters...
  Adapters saved to: ./my-finetuned-model

Fine-tuning complete!
```

---

## 22.7 Loading and Using the Fine-Tuned Model

### Loading LoRA Adapters

After training, you can load your adapters and use the model:

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load the base model
base_model_name = "facebook/opt-350m"
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_name,
    torch_dtype=torch.float16,
    device_map="auto",
)
tokenizer = AutoTokenizer.from_pretrained(base_model_name)

# Load the LoRA adapters on top of the base model
adapter_path = "./my-finetuned-model"
model = PeftModel.from_pretrained(base_model, adapter_path)
print("Model with LoRA adapters loaded!")

# Generate text
prompt = "### Instruction:\nWhat is machine learning?\n\n### Response:\n"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

outputs = model.generate(
    **inputs,
    max_new_tokens=100,
    temperature=0.7,
    do_sample=True,
)

response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(response)
```

**Expected output:**

```
Model with LoRA adapters loaded!
### Instruction:
What is machine learning?

### Response:
Machine learning is a branch of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. It uses algorithms to find patterns in data and make decisions or predictions based on those patterns.
```

**Line-by-line explanation:**

- `PeftModel.from_pretrained(base_model, adapter_path)` -- Loads the saved LoRA adapters and attaches them to the base model. The base model is loaded normally, then the tiny adapter files are applied on top
- `max_new_tokens=100` -- Generate up to 100 new tokens
- `temperature=0.7` -- Controls randomness. Lower values make output more deterministic, higher values make it more creative
- `do_sample=True` -- Use sampling instead of always picking the most likely next token

---

## 22.8 Merging Adapters into the Base Model

### Why Merge?

If you want to deploy the model without needing the PEFT library, you can merge the LoRA weights directly into the base model:

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load base model (must be in full precision for merging)
base_model = AutoModelForCausalLM.from_pretrained(
    "facebook/opt-350m",
    torch_dtype=torch.float16,
    device_map="cpu",  # Merge on CPU to avoid memory issues
)
tokenizer = AutoTokenizer.from_pretrained("facebook/opt-350m")

# Load adapters
model = PeftModel.from_pretrained(base_model, "./my-finetuned-model")
print("Adapters loaded.")

# Merge LoRA weights into the base model
merged_model = model.merge_and_unload()
print("Adapters merged into base model.")

# Save the merged model
merged_model.save_pretrained("./merged-model")
tokenizer.save_pretrained("./merged-model")
print("Merged model saved to ./merged-model")

# Now you can load this model without PEFT
# Just use AutoModelForCausalLM.from_pretrained("./merged-model")
```

**Expected output:**

```
Adapters loaded.
Adapters merged into base model.
Merged model saved to ./merged-model
```

**Line-by-line explanation:**

- `device_map="cpu"` -- We load the model on CPU for merging because merging temporarily needs extra memory
- `model.merge_and_unload()` -- This adds the LoRA matrices (scaled by alpha/rank) to the original weight matrices, then removes the LoRA wrapper. The result is a standard model with the fine-tuned weights baked in
- After merging, the model is just a regular Hugging Face model. You do not need PEFT to load or use it

```
+---------------------------------------------------------------+
|              BEFORE AND AFTER MERGING                         |
+---------------------------------------------------------------+
|                                                               |
|  Before merge (2 files needed):                               |
|  +------------------+  +------------------+                   |
|  |  Base Model      |  |  adapter_model   |                  |
|  |  (700 MB)        |  |  (6 MB)          |                  |
|  +------------------+  +------------------+                   |
|  Requires: transformers + peft libraries                      |
|                                                               |
|  After merge (1 file):                                        |
|  +---------------------------------------+                    |
|  |  Merged Model                         |                   |
|  |  (700 MB)                             |                   |
|  +---------------------------------------+                    |
|  Requires: transformers library only                          |
|                                                               |
+---------------------------------------------------------------+
```

---

## 22.9 Loading Data from Files

### Loading from JSON

```python
import json
from datasets import Dataset

# If your data is in a JSON file
# File: training_data.json
sample_json = [
    {"instruction": "What is gravity?", "response": "Gravity is a force that attracts objects toward each other."},
    {"instruction": "What is photosynthesis?", "response": "Photosynthesis is the process plants use to convert sunlight into food."},
]

# Save sample data to a file (for demonstration)
with open("training_data.json", "w") as f:
    json.dump(sample_json, f, indent=2)

# Load from JSON file
with open("training_data.json", "r") as f:
    data = json.load(f)

dataset = Dataset.from_list(data)
print(f"Loaded {len(dataset)} examples from JSON")
print(f"Columns: {dataset.column_names}")
```

**Expected output:**

```
Loaded 2 examples from JSON
Columns: ['instruction', 'response']
```

### Loading from CSV

```python
from datasets import load_dataset

# Load from a CSV file
# Assumes columns: instruction, response
# dataset = load_dataset("csv", data_files="training_data.csv", split="train")

# Load from Hugging Face Hub
# dataset = load_dataset("your-username/your-dataset", split="train")
print("You can load datasets from CSV, JSON, Parquet, or Hugging Face Hub")
```

### Splitting Data for Validation

```python
from datasets import Dataset

# Create a dataset
data = [{"text": f"Example {i}"} for i in range(100)]
dataset = Dataset.from_list(data)

# Split into training and validation sets
split_dataset = dataset.train_test_split(test_size=0.1, seed=42)

print(f"Training examples: {len(split_dataset['train'])}")
print(f"Validation examples: {len(split_dataset['test'])}")
```

**Expected output:**

```
Training examples: 90
Validation examples: 10
```

---

## 22.10 Training Tips and Tricks

### Learning Rate Selection

```python
# Common learning rates for different scenarios

learning_rates = {
    "Full fine-tuning (small model)": 5e-5,
    "Full fine-tuning (large model)": 1e-5,
    "LoRA fine-tuning (default)": 2e-4,
    "LoRA fine-tuning (aggressive)": 5e-4,
    "LoRA fine-tuning (conservative)": 1e-4,
    "QLoRA fine-tuning": 2e-4,
}

print(f"{'Scenario':<40} {'Learning Rate'}")
print("-" * 55)
for scenario, lr in learning_rates.items():
    print(f"{scenario:<40} {lr}")
```

**Expected output:**

```
Scenario                                 Learning Rate
-------------------------------------------------------
Full fine-tuning (small model)           5e-05
Full fine-tuning (large model)           1e-05
LoRA fine-tuning (default)               0.0002
LoRA fine-tuning (aggressive)            0.0005
LoRA fine-tuning (conservative)          0.0001
QLoRA fine-tuning                        0.0002
```

### Monitoring Training Loss

```
+---------------------------------------------------------------+
|          READING THE TRAINING LOSS                            |
+---------------------------------------------------------------+
|                                                               |
|  Loss going down steadily:     GOOD -- model is learning      |
|  Loss going down then up:      BAD -- overfitting             |
|  Loss not going down:          BAD -- LR too low or data issue|
|  Loss jumping wildly:          BAD -- LR too high             |
|  Loss hitting 0.0:             BAD -- severe overfitting      |
|                                                               |
|  Healthy training loss curve:                                 |
|                                                               |
|  Loss                                                         |
|  ^                                                            |
|  | \                                                          |
|  |  \                                                         |
|  |   \                                                        |
|  |    \_                                                      |
|  |      \___                                                  |
|  |          \______                                           |
|  |                 \_____________  <-- Plateaus (normal)       |
|  +------------------------------------> Steps                 |
|                                                               |
+---------------------------------------------------------------+
```

---

## Common Mistakes

1. **Forgetting to set the pad token** -- Many models do not have a pad token set by default. Always add `tokenizer.pad_token = tokenizer.eos_token` before training.

2. **Using too high a learning rate** -- LoRA fine-tuning works best with learning rates around 1e-4 to 5e-4. Using 1e-2 or higher will cause the model to produce garbage.

3. **Not using gradient checkpointing** -- Without `gradient_checkpointing=True`, large models will run out of memory. Always enable it unless you have plenty of GPU memory.

4. **Training for too many epochs** -- With small datasets, 3-5 epochs is usually enough. Training for 20+ epochs will cause severe overfitting.

5. **Merging with a quantized model** -- You cannot merge LoRA adapters into a 4-bit quantized model directly. Load the base model in fp16 first, then merge.

6. **Wrong template format** -- Each model family expects a specific prompt template. Using the wrong template leads to poor results even with good data.

---

## Best Practices

1. **Start with a small dataset** -- Test your entire pipeline with 10-50 examples before scaling up to thousands. This catches bugs early.

2. **Use gradient accumulation** -- Instead of a large batch size (which needs more memory), use small batches with gradient accumulation.

3. **Save checkpoints regularly** -- Training can crash due to hardware issues. Save checkpoints every few hundred steps so you can resume.

4. **Validate on held-out data** -- Split your data into training (90%) and validation (10%). Monitor validation loss to detect overfitting.

5. **Use the right prompt template** -- Match the template used during the base model's training. Check the model card on Hugging Face for the correct template.

6. **Clean your data thoroughly** -- Bad data leads to a bad model. Remove duplicates, fix formatting issues, and ensure consistent quality.

---

## Quick Summary

Fine-tuning a language model with LoRA/QLoRA follows a clear pipeline: install the libraries (transformers, peft, trl), load a base model (optionally in 4-bit with BitsAndBytes), create a LoRA configuration (rank, alpha, dropout, target modules), prepare your training data in the right format, train using SFTTrainer, and save/merge the results. The entire process can be done on a single consumer GPU and takes minutes to hours depending on the model and dataset size.

---

## Key Points

- **PEFT** (Parameter-Efficient Fine-Tuning) is the Hugging Face library for LoRA
- `get_peft_model()` attaches LoRA adapters to a model and freezes the base weights
- **BitsAndBytesConfig** enables 4-bit quantization for QLoRA
- **SFTTrainer** from the `trl` library handles the entire training loop
- Training data should be formatted with a consistent template (e.g., Instruction/Response)
- **Gradient accumulation** simulates larger batch sizes without extra memory
- **Gradient checkpointing** trades compute time for memory savings
- LoRA adapters can be **saved separately** (small files, ~10 MB) or **merged** into the base model
- Always set `pad_token` and `padding_side` before training
- Learning rate of 2e-4 is a good default for LoRA fine-tuning

---

## Practice Questions

1. You have a dataset of 1,000 customer service conversations. Walk through the steps you would take to fine-tune a model on this data using QLoRA.

2. What is the purpose of `gradient_accumulation_steps`? If your `per_device_train_batch_size` is 2 and `gradient_accumulation_steps` is 8, what is the effective batch size?

3. Explain the difference between saving LoRA adapters separately and merging them into the base model. When would you choose each approach?

4. You are training a model and notice the loss goes down for the first epoch, then starts going back up. What is happening and what should you do?

5. Why do you need to set `tokenizer.pad_token = tokenizer.eos_token`? What would happen if you skipped this step?

---

## Exercises

### Exercise 1: Fine-Tune on Custom Q&A

Create a dataset of 20 question-answer pairs about a topic you know well (your favorite hobby, your field of study, etc.). Fine-tune `facebook/opt-350m` using LoRA with rank=8. Compare the model's answers before and after fine-tuning.

### Exercise 2: Hyperparameter Experiment

Fine-tune the same model with three different configurations: (a) rank=4, alpha=8; (b) rank=16, alpha=32; (c) rank=64, alpha=128. Compare the final training loss and the quality of generated text for each configuration.

### Exercise 3: Full Pipeline with Validation

Build a complete fine-tuning pipeline that includes: loading data from a JSON file, splitting into train/validation sets, training with early stopping (stop if validation loss increases for 3 consecutive evaluations), and saving the best model.

---

## What Is Next?

You have now mastered the practical side of fine-tuning language models. In Chapter 23, we shift gears to an exciting new topic: AI Agents. You will learn how language models can be given tools, reasoning abilities, and autonomy to accomplish complex tasks on their own -- going from simple chatbots to intelligent assistants that can browse the web, write code, and solve multi-step problems.
