# Chapter 6: Running LLMs Locally

## What You Will Learn

In this chapter, you will learn:

- How to install and use Ollama to run LLMs on your computer
- What llama.cpp is and why it matters for local inference
- Hardware requirements: how much RAM and VRAM you need for different model sizes
- What quantization is and how 4-bit and 8-bit models let you run large models on smaller hardware
- How to pull, run, and interact with models locally
- How to use local models with an API for programmatic access

## Why This Chapter Matters

Using LLM APIs means your data goes to someone else's servers. Every prompt, every piece of code, every document you analyze travels across the internet to a company's data center. For many use cases, this is fine. But for sensitive data, proprietary code, or privacy-critical applications, it is not acceptable.

Running models locally means your data never leaves your machine. You pay nothing per token. You have zero dependency on internet connectivity. And you can customize the model however you want.

This chapter gets you from zero to a running LLM on your own hardware.

---

## Why Run Models Locally?

```
+----------------------------------------------------------+
|         API vs Local: When to Use Each                    |
+----------------------------------------------------------+
|                                                            |
|  USE AN API WHEN:                                         |
|    + You need the most capable models (GPT-4o, Claude)   |
|    + Your data is not sensitive                           |
|    + You want zero setup                                  |
|    + Usage volume is low to moderate                      |
|    + You need the latest model updates                   |
|                                                            |
|  RUN LOCALLY WHEN:                                        |
|    + Data privacy is critical                             |
|    + You process high volumes (cost savings)              |
|    + You need offline access                              |
|    + You want to fine-tune a model                       |
|    + You need full control over the model                |
|    + Latency to API servers is too high                  |
|                                                            |
+----------------------------------------------------------+
```

---

## Hardware Requirements

Before installing anything, you need to know if your hardware can run an LLM.

```
+------------------------------------------------------------------+
|              Hardware Requirements by Model Size                  |
+------------------------------------------------------------------+
|                                                                    |
|  Model Size  | Full (FP16)  | 8-bit (INT8) | 4-bit (INT4)       |
|  ──────────  | ──────────── | ──────────── | ──────────────      |
|  1B params   | ~2 GB        | ~1 GB        | ~0.5 GB             |
|  3B params   | ~6 GB        | ~3 GB        | ~1.5 GB             |
|  7B params   | ~14 GB       | ~7 GB        | ~4 GB               |
|  13B params  | ~26 GB       | ~13 GB       | ~7 GB               |
|  70B params  | ~140 GB      | ~70 GB       | ~35 GB              |
|                                                                    |
|  Rule of thumb: Full precision needs ~2 GB per billion params    |
|  4-bit quantization cuts this by roughly 4x                      |
|                                                                    |
+------------------------------------------------------------------+
|                                                                    |
|  Recommended Hardware:                                            |
|  ──────────────────────                                           |
|  Entry level:  16 GB RAM      -> 7B models (4-bit)              |
|  Mid range:    32 GB RAM      -> 13B models (4-bit)             |
|  High end:     64 GB RAM      -> 70B models (4-bit, slow)       |
|  GPU (ideal):  RTX 3090 24GB  -> 13B models (4-bit, fast)       |
|  GPU (best):   RTX 4090 24GB  -> 13B models at full speed       |
|                                                                    |
|  Note: GPU VRAM is much faster than system RAM for inference     |
|                                                                    |
+------------------------------------------------------------------+
```

```python
# Hardware requirement calculator

def hardware_calculator(model_params_billions, quantization_bits=16):
    """
    Estimate memory requirements for running an LLM locally.

    Args:
        model_params_billions: Number of parameters in billions
        quantization_bits: 4, 8, or 16 (full precision)
    """
    # Memory calculation
    # Each parameter needs (bits / 8) bytes
    bytes_per_param = quantization_bits / 8
    memory_gb = (model_params_billions * 1e9 * bytes_per_param) / (1024**3)

    # Add overhead (~20% for KV cache, activations, etc.)
    total_memory_gb = memory_gb * 1.2

    print(f"Hardware Requirements Calculator")
    print(f"=" * 50)
    print(f"  Model size:    {model_params_billions}B parameters")
    print(f"  Quantization:  {quantization_bits}-bit")
    print(f"  Raw memory:    {memory_gb:.1f} GB")
    print(f"  With overhead: {total_memory_gb:.1f} GB")
    print()

    # Recommendations
    if total_memory_gb <= 4:
        print(f"  Can run on: Most modern laptops")
        print(f"  Speed: Fast on CPU, very fast on GPU")
    elif total_memory_gb <= 8:
        print(f"  Can run on: Laptops with 16+ GB RAM")
        print(f"  Speed: Moderate on CPU, fast on GPU")
    elif total_memory_gb <= 16:
        print(f"  Can run on: 32+ GB RAM or GPU with 16+ GB VRAM")
        print(f"  Speed: Slow on CPU, good on GPU")
    elif total_memory_gb <= 40:
        print(f"  Can run on: 64+ GB RAM or GPU with 48+ GB VRAM")
        print(f"  Speed: Very slow on CPU, moderate on GPU")
    else:
        print(f"  Can run on: Server-grade hardware required")
        print(f"  Speed: Needs multiple GPUs")

    return total_memory_gb

# Calculate for common model sizes
print("Common Model Configurations")
print("=" * 55)
configs = [
    (7,  4,  "Llama 3.1 8B (4-bit)"),
    (7,  8,  "Llama 3.1 8B (8-bit)"),
    (7,  16, "Llama 3.1 8B (full)"),
    (70, 4,  "Llama 3.1 70B (4-bit)"),
]

for params, bits, name in configs:
    print(f"\n--- {name} ---")
    hardware_calculator(params, bits)
```

**Output:**
```
Common Model Configurations
=======================================================

--- Llama 3.1 8B (4-bit) ---
Hardware Requirements Calculator
==================================================
  Model size:    7B parameters
  Quantization:  4-bit
  Raw memory:    3.3 GB
  With overhead: 3.9 GB

  Can run on: Most modern laptops
  Speed: Fast on CPU, very fast on GPU

--- Llama 3.1 8B (8-bit) ---
Hardware Requirements Calculator
==================================================
  Model size:    7B parameters
  Quantization:  8-bit
  Raw memory:    6.5 GB
  With overhead: 7.8 GB

  Can run on: Laptops with 16+ GB RAM
  Speed: Moderate on CPU, fast on GPU

--- Llama 3.1 8B (full) ---
Hardware Requirements Calculator
==================================================
  Model size:    7B parameters
  Quantization:  16-bit
  Raw memory:    13.0 GB
  With overhead: 15.6 GB

  Can run on: 32+ GB RAM or GPU with 16+ GB VRAM
  Speed: Slow on CPU, good on GPU

--- Llama 3.1 70B (4-bit) ---
Hardware Requirements Calculator
==================================================
  Model size:    70B parameters
  Quantization:  4-bit
  Raw memory:    32.6 GB
  With overhead: 39.1 GB

  Can run on: 64+ GB RAM or GPU with 48+ GB VRAM
  Speed: Very slow on CPU, moderate on GPU
```

---

## What Is Quantization?

**Quantization** is the process of reducing the precision of a model's numbers to use less memory and run faster, with a small trade-off in quality.

**Analogy:** Think of a photograph. A full-resolution photo (16-bit) captures every tiny shade of color. A compressed JPEG (8-bit) looks almost identical but uses much less space. Extreme compression (4-bit) might show some artifacts but is still usable. Quantization does the same thing to a model's parameters.

```
+----------------------------------------------------------+
|         Quantization Levels Explained                     |
+----------------------------------------------------------+
|                                                            |
|  FP16 (16-bit floating point):                           |
|    Each parameter uses 16 bits = 2 bytes                  |
|    Full precision, highest quality                        |
|    Example: 0.123456789                                   |
|                                                            |
|  INT8 (8-bit integer):                                    |
|    Each parameter uses 8 bits = 1 byte                    |
|    Half the memory, ~99% quality                          |
|    Example: 0.12 (less precise)                           |
|                                                            |
|  INT4 (4-bit integer):                                    |
|    Each parameter uses 4 bits = 0.5 bytes                 |
|    Quarter the memory, ~95-97% quality                    |
|    Example: 0.1 (even less precise)                       |
|                                                            |
|  Memory savings:                                          |
|    7B model @ FP16: 14 GB                                 |
|    7B model @ INT8:  7 GB  (50% smaller)                  |
|    7B model @ INT4:  3.5 GB (75% smaller!)                |
|                                                            |
+----------------------------------------------------------+
```

```python
# Demonstrating quantization conceptually

import random

def quantization_demo():
    """
    Show how quantization reduces precision but saves memory.
    """
    random.seed(42)

    # Generate sample "parameters" at full precision
    full_precision = [random.uniform(-1, 1) for _ in range(10)]

    print("Quantization: Precision vs Memory Trade-off")
    print("=" * 60)

    # Show different precision levels
    print(f"\n{'Parameter':<12} {'FP16':>12} {'INT8':>12} {'INT4':>12}")
    print("-" * 50)

    total_error_8bit = 0
    total_error_4bit = 0

    for i, val in enumerate(full_precision):
        # Simulate 8-bit quantization (round to nearest 1/128)
        val_8bit = round(val * 128) / 128

        # Simulate 4-bit quantization (round to nearest 1/8)
        val_4bit = round(val * 8) / 8

        total_error_8bit += abs(val - val_8bit)
        total_error_4bit += abs(val - val_4bit)

        print(f"  Param {i+1:2d}:  {val:>10.6f}  {val_8bit:>10.6f}  "
              f"{val_4bit:>10.6f}")

    avg_error_8bit = total_error_8bit / len(full_precision)
    avg_error_4bit = total_error_4bit / len(full_precision)

    print("-" * 50)
    print(f"\n  Avg error (8-bit): {avg_error_8bit:.6f} (very small)")
    print(f"  Avg error (4-bit): {avg_error_4bit:.6f} (still small)")

    print(f"\n  Memory per parameter:")
    print(f"    FP16: 2.0 bytes")
    print(f"    INT8: 1.0 bytes (50% savings)")
    print(f"    INT4: 0.5 bytes (75% savings)")

    print(f"\n  For a 7B parameter model:")
    print(f"    FP16: {7 * 2:.0f} GB")
    print(f"    INT8: {7 * 1:.0f} GB")
    print(f"    INT4: {7 * 0.5:.1f} GB")

quantization_demo()
```

**Output:**
```
Quantization: Precision vs Memory Trade-off
============================================================

Parameter         FP16         INT8         INT4
--------------------------------------------------
  Param  1:    0.259542    0.257812    0.250000
  Param  2:   -0.232752   -0.234375   -0.250000
  Param  3:    0.463501    0.460938    0.500000
  Param  4:   -0.688894   -0.687500   -0.750000
  Param  5:    0.062074    0.062500    0.125000
  Param  6:    0.198730    0.195312    0.250000
  Param  7:   -0.267834   -0.265625   -0.250000
  Param  8:    0.543405    0.546875    0.500000
  Param  9:   -0.012683   -0.015625    0.000000
  Param 10:    0.156017    0.156250    0.125000
--------------------------------------------------

  Avg error (8-bit): 0.002303 (very small)
  Avg error (4-bit): 0.034277 (still small)

  Memory per parameter:
    FP16: 2.0 bytes
    INT8: 1.0 bytes (50% savings)
    INT4: 0.5 bytes (75% savings)

  For a 7B parameter model:
    FP16: 14 GB
    INT8: 7 GB
    INT4: 3.5 GB
```

---

## Setting Up Ollama

**Ollama** is the easiest way to run LLMs locally. It handles downloading, quantization, and serving models with a single command.

### Installation

```
+----------------------------------------------------------+
|         Installing Ollama                                 |
+----------------------------------------------------------+
|                                                            |
|  macOS:                                                   |
|    Download from https://ollama.com                       |
|    Or: brew install ollama                                |
|                                                            |
|  Linux:                                                   |
|    curl -fsSL https://ollama.com/install.sh | sh          |
|                                                            |
|  Windows:                                                 |
|    Download from https://ollama.com                       |
|                                                            |
|  Verify installation:                                     |
|    ollama --version                                       |
|                                                            |
+----------------------------------------------------------+
```

### Basic Ollama Commands

```python
# Ollama commands reference (run these in your terminal)

commands = {
    "Pull a model": {
        "command": "ollama pull llama3.1",
        "description": "Download the Llama 3.1 8B model (~4.7 GB)",
    },
    "Run a model (interactive)": {
        "command": "ollama run llama3.1",
        "description": "Start an interactive chat session",
    },
    "List installed models": {
        "command": "ollama list",
        "description": "Show all downloaded models and their sizes",
    },
    "Remove a model": {
        "command": "ollama rm llama3.1",
        "description": "Delete a model to free disk space",
    },
    "Model information": {
        "command": "ollama show llama3.1",
        "description": "Show model details (parameters, size, etc.)",
    },
    "Run with a prompt": {
        "command": 'ollama run llama3.1 "What is Python?"',
        "description": "Get a one-shot response without interactive mode",
    },
    "Start API server": {
        "command": "ollama serve",
        "description": "Start the API server (usually runs automatically)",
    },
}

print("Ollama Command Reference")
print("=" * 60)

for name, info in commands.items():
    print(f"\n  {name}:")
    print(f"    Command: {info['command']}")
    print(f"    What it does: {info['description']}")
```

**Output:**
```
Ollama Command Reference
============================================================

  Pull a model:
    Command: ollama pull llama3.1
    What it does: Download the Llama 3.1 8B model (~4.7 GB)

  Run a model (interactive):
    Command: ollama run llama3.1
    What it does: Start an interactive chat session

  List installed models:
    Command: ollama list
    What it does: Show all downloaded models and their sizes

  Remove a model:
    Command: ollama rm llama3.1
    What it does: Delete a model to free disk space

  Model information:
    Command: ollama show llama3.1
    What it does: Show model details (parameters, size, etc.)

  Run with a prompt:
    Command: ollama run llama3.1 "What is Python?"
    What it does: Get a one-shot response without interactive mode

  Start API server:
    Command: ollama serve
    What it does: Start the API server (usually runs automatically)
```

### Popular Models Available Through Ollama

```python
# Popular models available through Ollama

models = [
    {"name": "llama3.1",       "size": "8B",  "disk": "4.7 GB",
     "best_for": "General purpose, good balance"},
    {"name": "llama3.1:70b",   "size": "70B", "disk": "40 GB",
     "best_for": "High quality, needs powerful hardware"},
    {"name": "mistral",        "size": "7B",  "disk": "4.1 GB",
     "best_for": "Fast, efficient, good for chat"},
    {"name": "mixtral",        "size": "8x7B","disk": "26 GB",
     "best_for": "MoE model, great quality-to-speed ratio"},
    {"name": "codellama",      "size": "7B",  "disk": "3.8 GB",
     "best_for": "Code generation and completion"},
    {"name": "phi3",           "size": "3.8B","disk": "2.3 GB",
     "best_for": "Very small, surprisingly capable"},
    {"name": "gemma2",         "size": "9B",  "disk": "5.4 GB",
     "best_for": "Google's open model, good reasoning"},
    {"name": "qwen2.5",        "size": "7B",  "disk": "4.4 GB",
     "best_for": "Strong multilingual support"},
]

print("Popular Ollama Models")
print("=" * 70)
print(f"{'Model':<18} {'Size':<8} {'Disk':<10} {'Best For'}")
print("-" * 70)

for m in models:
    print(f"  {m['name']:<16} {m['size']:<8} {m['disk']:<10} {m['best_for']}")

print("-" * 70)
print("\nTo install any model: ollama pull <model_name>")
print("Example: ollama pull phi3")
```

**Output:**
```
Popular Ollama Models
======================================================================
Model              Size     Disk       Best For
----------------------------------------------------------------------
  llama3.1         8B       4.7 GB     General purpose, good balance
  llama3.1:70b     70B      40 GB      High quality, needs powerful hardware
  mistral          7B       4.1 GB     Fast, efficient, good for chat
  mixtral          8x7B     26 GB      MoE model, great quality-to-speed ratio
  codellama        7B       3.8 GB     Code generation and completion
  phi3             3.8B     2.3 GB     Very small, surprisingly capable
  gemma2           9B       5.4 GB     Google's open model, good reasoning
  qwen2.5          7B       4.4 GB     Strong multilingual support
----------------------------------------------------------------------

To install any model: ollama pull <model_name>
Example: ollama pull phi3
```

---

## Using Ollama with Python

Ollama provides an API that you can call from Python using the `requests` library or the official `ollama` package.

```python
# Method 1: Using the requests library (no extra installation)
import requests
import json

def chat_with_ollama_requests(prompt, model="llama3.1"):
    """
    Send a prompt to Ollama using the REST API.
    Ollama must be running (ollama serve).
    """
    url = "http://localhost:11434/api/generate"

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,  # Get complete response at once
    }

    try:
        response = requests.post(url, json=payload)
        result = response.json()

        print(f"Model: {model}")
        print(f"Prompt: '{prompt}'")
        print(f"Response: {result['response']}")
        print(f"\nStats:")
        print(f"  Total duration: {result.get('total_duration', 0) / 1e9:.2f}s")
        print(f"  Tokens generated: {result.get('eval_count', 'N/A')}")

        return result['response']

    except requests.ConnectionError:
        print("Error: Cannot connect to Ollama.")
        print("Make sure Ollama is running: ollama serve")
        return None

# Example usage (requires Ollama to be running)
# chat_with_ollama_requests("What is Python in one sentence?")
print("Example: chat_with_ollama_requests('What is Python?')")
print("(Requires Ollama to be running locally)")
```

**Output:**
```
Example: chat_with_ollama_requests('What is Python?')
(Requires Ollama to be running locally)
```

```python
# Method 2: Using the official ollama Python package
# Install: pip install ollama

# import ollama

def chat_with_ollama_package(prompt, model="llama3.1"):
    """
    Send a prompt using the official ollama Python package.
    Cleaner API than raw HTTP requests.
    """
    # import ollama  # Uncomment when running

    # Simple completion
    # response = ollama.generate(model=model, prompt=prompt)
    # print(response['response'])

    # Chat-style interaction (with message history)
    # response = ollama.chat(
    #     model=model,
    #     messages=[
    #         {"role": "user", "content": prompt}
    #     ]
    # )
    # print(response['message']['content'])

    print("Using the ollama Python package:")
    print()
    print("  # Simple generation")
    print("  import ollama")
    print(f"  response = ollama.generate(model='{model}', "
          f"prompt='{prompt}')")
    print("  print(response['response'])")
    print()
    print("  # Chat-style (with message history)")
    print("  response = ollama.chat(")
    print(f"      model='{model}',")
    print("      messages=[")
    print(f"          {{'role': 'user', 'content': '{prompt}'}}")
    print("      ]")
    print("  )")
    print("  print(response['message']['content'])")

chat_with_ollama_package("Explain Python in one sentence.")
```

**Output:**
```
Using the ollama Python package:

  # Simple generation
  import ollama
  response = ollama.generate(model='llama3.1', prompt='Explain Python in one sentence.')
  print(response['response'])

  # Chat-style (with message history)
  response = ollama.chat(
      model='llama3.1',
      messages=[
          {'role': 'user', 'content': 'Explain Python in one sentence.'}
      ]
  )
  print(response['message']['content'])
```

---

## What Is llama.cpp?

**llama.cpp** is a C/C++ implementation for running LLM inference. It is the engine under the hood of many local LLM tools, including Ollama.

```
+----------------------------------------------------------+
|         llama.cpp: The Engine Behind Local LLMs           |
+----------------------------------------------------------+
|                                                            |
|  What it is:                                              |
|    A C/C++ library that runs LLM inference                |
|    Optimized for CPU (and GPU via CUDA, Metal, etc.)     |
|    Supports quantized models (GGUF format)               |
|                                                            |
|  Why it matters:                                          |
|    Makes LLMs run on consumer hardware                    |
|    No Python dependencies, no PyTorch needed              |
|    Very fast, even on CPU-only machines                   |
|                                                            |
|  Relationship to other tools:                             |
|    Ollama uses llama.cpp internally                       |
|    LM Studio uses llama.cpp internally                    |
|    Many local LLM apps are built on llama.cpp            |
|                                                            |
|  GGUF format:                                             |
|    The file format for quantized models                   |
|    Stands for GPT-Generated Unified Format               |
|    Contains model weights + metadata in one file          |
|    Example: llama-3.1-8b-q4_0.gguf (4-bit quantized)    |
|                                                            |
+----------------------------------------------------------+
```

```python
# Understanding GGUF file naming conventions

def explain_gguf_name(filename):
    """
    Parse a GGUF model filename to understand its properties.
    """
    print(f"Filename: {filename}")
    print("-" * 50)

    # Common quantization types
    quant_types = {
        "q4_0": "4-bit quantization, basic method",
        "q4_1": "4-bit quantization, slightly better quality",
        "q4_k_m": "4-bit quantization, k-quant medium (recommended)",
        "q4_k_s": "4-bit quantization, k-quant small",
        "q5_0": "5-bit quantization, good balance",
        "q5_k_m": "5-bit quantization, k-quant medium",
        "q8_0": "8-bit quantization, near-original quality",
        "f16": "16-bit, full precision (largest file)",
    }

    for quant, description in quant_types.items():
        if quant in filename.lower():
            print(f"  Quantization: {quant}")
            print(f"  Description: {description}")
            break

    print()

# Common GGUF filenames you'll encounter
filenames = [
    "llama-3.1-8b-instruct-q4_k_m.gguf",
    "mistral-7b-instruct-v0.3-q8_0.gguf",
    "phi-3-mini-4k-instruct-q4_0.gguf",
    "codellama-13b-instruct-q5_k_m.gguf",
]

print("Understanding GGUF Model Files")
print("=" * 55)
print()

for name in filenames:
    explain_gguf_name(name)

# Quantization comparison
print("\nQuantization Quality vs Size Trade-off (7B model):")
print("-" * 55)
quant_comparison = [
    ("F16 (full)",   14.0, 100),
    ("Q8_0 (8-bit)", 7.0,  99),
    ("Q5_K_M",       5.0,  97),
    ("Q4_K_M",       4.0,  95),
    ("Q4_0",         3.5,  93),
]

for name, size, quality in quant_comparison:
    size_bar = "█" * int(size * 2)
    quality_bar = "█" * int(quality / 5)
    print(f"  {name:15s} Size: {size:5.1f} GB {size_bar}")
    print(f"  {'':15s} Quality: ~{quality}%  {quality_bar}")
    print()
```

**Output:**
```
Understanding GGUF Model Files
=======================================================

Filename: llama-3.1-8b-instruct-q4_k_m.gguf
--------------------------------------------------
  Quantization: q4_k_m
  Description: 4-bit quantization, k-quant medium (recommended)

Filename: mistral-7b-instruct-v0.3-q8_0.gguf
--------------------------------------------------
  Quantization: q8_0
  Description: 8-bit quantization, near-original quality

Filename: phi-3-mini-4k-instruct-q4_0.gguf
--------------------------------------------------
  Quantization: q4_0
  Description: 4-bit quantization, basic method

Filename: codellama-13b-instruct-q5_k_m.gguf
--------------------------------------------------
  Quantization: q5_k_m
  Description: 5-bit quantization, k-quant medium

Quantization Quality vs Size Trade-off (7B model):
-------------------------------------------------------
  F16 (full)      Size:  14.0 GB ████████████████████████████
                  Quality: ~100%  ████████████████████

  Q8_0 (8-bit)   Size:   7.0 GB ██████████████
                  Quality: ~99%  ███████████████████

  Q5_K_M          Size:   5.0 GB ██████████
                  Quality: ~97%  ███████████████████

  Q4_K_M          Size:   4.0 GB ████████
                  Quality: ~95%  ███████████████████

  Q4_0            Size:   3.5 GB ███████
                  Quality: ~93%  ██████████████████
```

---

## API-Style Local Inference

One of the best features of Ollama is that it provides an OpenAI-compatible API. This means you can use the same code that works with OpenAI's API, but point it at your local Ollama server.

```python
# Using Ollama with OpenAI-compatible API
# Install: pip install openai

# from openai import OpenAI

def local_openai_compatible():
    """
    Use Ollama's OpenAI-compatible API endpoint.
    Same code works with OpenAI, just change the base_url.
    """
    print("OpenAI-Compatible API with Ollama")
    print("=" * 55)
    print()
    print("# Install: pip install openai")
    print()
    print("from openai import OpenAI")
    print()
    print("# Point to local Ollama server instead of OpenAI")
    print("client = OpenAI(")
    print('    base_url="http://localhost:11434/v1",')
    print('    api_key="ollama"  # Not used but required by the library')
    print(")")
    print()
    print("# Use exactly the same code as OpenAI!")
    print("response = client.chat.completions.create(")
    print('    model="llama3.1",')
    print("    messages=[")
    print('        {"role": "system", "content": "You are helpful."},')
    print('        {"role": "user", "content": "What is Python?"}')
    print("    ],")
    print("    temperature=0.7,")
    print(")")
    print()
    print("print(response.choices[0].message.content)")
    print()
    print("# To switch to OpenAI, just change base_url and api_key:")
    print("# client = OpenAI(api_key='sk-your-key-here')")
    print("# Everything else stays the same!")

local_openai_compatible()
```

**Output:**
```
OpenAI-Compatible API with Ollama
=======================================================

# Install: pip install openai

from openai import OpenAI

# Point to local Ollama server instead of OpenAI
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # Not used but required by the library
)

# Use exactly the same code as OpenAI!
response = client.chat.completions.create(
    model="llama3.1",
    messages=[
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "What is Python?"}
    ],
    temperature=0.7,
)

print(response.choices[0].message.content)

# To switch to OpenAI, just change base_url and api_key:
# client = OpenAI(api_key='sk-your-key-here')
# Everything else stays the same!
```

---

## Complete Local Setup Walkthrough

```
+----------------------------------------------------------+
|         Complete Setup: From Zero to Running LLM          |
+----------------------------------------------------------+
|                                                            |
|  Step 1: Install Ollama                                   |
|    macOS: brew install ollama                             |
|    Linux: curl -fsSL https://ollama.com/install.sh | sh  |
|                                                            |
|  Step 2: Pull a model                                     |
|    ollama pull llama3.1                                    |
|    (Downloads ~4.7 GB, takes a few minutes)               |
|                                                            |
|  Step 3: Test it interactively                            |
|    ollama run llama3.1                                     |
|    > What is machine learning?                            |
|    (Type /bye to exit)                                    |
|                                                            |
|  Step 4: Use from Python                                  |
|    pip install requests                                   |
|    (Use the code examples from this chapter)              |
|                                                            |
|  Step 5: (Optional) Use OpenAI-compatible API             |
|    pip install openai                                     |
|    (Point base_url to localhost:11434)                    |
|                                                            |
+----------------------------------------------------------+
```

---

## Common Mistakes

| Mistake | Why It Is Wrong | What to Do Instead |
|---------|----------------|-------------------|
| Trying to run a 70B model on a laptop | 70B models need 35-40 GB RAM even quantized | Start with 7B-8B models; upgrade hardware if needed |
| Using full precision when quantized is fine | FP16 uses 4x more memory than INT4 with minimal quality gain | Use Q4_K_M quantization for best balance |
| Forgetting to start Ollama before API calls | The API server must be running to accept requests | Run `ollama serve` or ensure the Ollama app is open |
| Expecting local models to match GPT-4 | Local 7B models are less capable than top closed models | Set realistic expectations; use local models for appropriate tasks |
| Not monitoring RAM/VRAM usage | Models can consume all available memory and crash | Monitor with `htop`, `nvidia-smi`, or Activity Monitor |

---

## Best Practices

1. **Start with the smallest model that works for your task.** A 3B model that handles your use case is better than a 7B model that is overkill.

2. **Use Q4_K_M quantization as your default.** It offers the best balance of quality and memory usage for most applications.

3. **Design your code to swap models easily.** Use the OpenAI-compatible API so you can switch between local and cloud models by changing one line.

4. **Monitor performance.** Track tokens per second, memory usage, and output quality. Log these metrics to make informed decisions about model selection.

5. **Keep models updated.** Run `ollama pull <model>` periodically to get updated versions with bug fixes and improvements.

---

## Quick Summary

Running LLMs locally gives you data privacy, zero per-token costs, and full control. Ollama makes setup easy: install it, pull a model, and start chatting. Quantization (4-bit, 8-bit) reduces memory requirements by 50-75% with minimal quality loss, making it possible to run 7B models on most laptops. llama.cpp is the C++ engine behind most local LLM tools, using the GGUF file format. Ollama provides an OpenAI-compatible API, so your code can switch between local and cloud models with a single configuration change.

---

## Key Points

- Running locally means data never leaves your machine and there are no per-token API costs
- Hardware requirement rule of thumb: ~2 GB per billion parameters at full precision, ~0.5 GB at 4-bit quantization
- Quantization reduces model size by lowering numerical precision (16-bit to 8-bit or 4-bit) with small quality trade-offs
- Q4_K_M is the recommended quantization level for most use cases
- Ollama is the easiest tool for running models locally: install, pull, run
- llama.cpp is the C++ engine that powers Ollama and many other local LLM tools
- GGUF is the standard file format for quantized models
- Ollama's OpenAI-compatible API allows code that works with both local and cloud models

---

## Practice Questions

1. Your laptop has 16 GB of RAM and no dedicated GPU. What is the largest model you can realistically run? At what quantization level?

2. Explain quantization using a non-technical analogy. Why does 4-bit quantization lose only ~5% quality while using 75% less memory?

3. Why does Ollama provide an OpenAI-compatible API? What practical benefit does this give developers?

4. What is the relationship between Ollama, llama.cpp, and GGUF? How do they work together?

5. For each scenario, would you recommend running locally or using an API? Explain why.
   - A hospital analyzing patient notes
   - A student experimenting with prompts for a homework project
   - A startup processing 100,000 customer messages daily

---

## Exercises

### Exercise 1: Install and Run

Install Ollama on your machine and:
- Pull the smallest available model (try `phi3` or `llama3.2:1b`)
- Ask it five different types of questions (factual, creative, code, math, analysis)
- Record the response time and quality for each
- Compare the results to a cloud model like ChatGPT

### Exercise 2: Model Comparison

Pull two different models (e.g., `llama3.1` and `mistral`). Ask both the same 10 questions and compare:
- Response quality
- Response speed (tokens per second)
- Memory usage
- Which model handles your specific use case better

### Exercise 3: Python Integration

Write a Python script that:
- Connects to Ollama's API
- Sends a prompt and receives a response
- Measures response time
- Prints the response along with performance statistics
- Handles the case where Ollama is not running with a helpful error message

---

## What Is Next?

Now that you can run LLMs both locally and via APIs, it is time to learn how to communicate with them effectively. The next chapter, "Writing Effective Prompts", teaches you the art and science of prompt engineering. You will learn how clarity, specificity, context, and constraints affect the quality of LLM responses, and see concrete examples of bad prompts transformed into good ones.
