# Chapter 21: LoRA and QLoRA -- Efficient Fine-Tuning

## What You Will Learn

In this chapter, you will learn:

- Why full fine-tuning of large language models is extremely expensive
- What LoRA (Low-Rank Adaptation) is and how it makes fine-tuning affordable
- How LoRA works using the analogy of sticky notes on a textbook
- What QLoRA is and how it combines quantization with LoRA
- How the rank parameter controls the balance between performance and cost
- Which layers of a model to adapt for the best results

## Why This Chapter Matters

Imagine you have a textbook with 1,000 pages. You want to customize it for your specific class. You have two choices:

1. **Rewrite the entire book** -- Copy all 1,000 pages and change every one (full fine-tuning)
2. **Add sticky notes** -- Keep the original book and add small notes on specific pages (LoRA)

Full fine-tuning of a large language model like LLaMA-70B requires multiple expensive GPUs, costs thousands of dollars, and takes days. LoRA lets you achieve similar results by training less than 1% of the model's parameters. QLoRA goes even further by shrinking the model's memory footprint using 4-bit quantization.

These techniques are what make it possible for individuals and small teams to customize large language models. Without LoRA and QLoRA, fine-tuning would remain a privilege reserved for large companies with massive GPU clusters.

---

## 21.1 The Problem: Full Fine-Tuning Is Expensive

### What Is Full Fine-Tuning?

Full fine-tuning means updating **every single parameter** (weight) in a model during training. Let us look at what this involves for different model sizes:

```
+---------------------------------------------------------------+
|          THE COST OF FULL FINE-TUNING                         |
+---------------------------------------------------------------+
|                                                               |
|  Model Size    Parameters     GPU Memory     Typical Cost     |
|  ---------     ----------     ----------     ------------     |
|  GPT-2         124 million    ~1 GB          Free (1 GPU)     |
|  LLaMA-7B      7 billion     ~28 GB         $50-100          |
|  LLaMA-13B     13 billion    ~52 GB         $200-500         |
|  LLaMA-70B     70 billion    ~280 GB        $2,000-10,000    |
|  GPT-3         175 billion   ~700 GB        $50,000+         |
|                                                               |
+---------------------------------------------------------------+
```

### Why Does It Need So Much Memory?

During training, you need to store:

1. **The model weights** -- The actual parameters of the model
2. **The gradients** -- How much each weight should change (same size as weights)
3. **The optimizer states** -- Extra information the optimizer tracks (2x the size of weights for Adam)

```python
# Understanding memory requirements for full fine-tuning

# Model parameters (in billions)
model_size_billions = 7  # LLaMA-7B

# Each parameter is stored as a 16-bit float (2 bytes)
bytes_per_param = 2  # fp16

# Memory for model weights
weight_memory_gb = (model_size_billions * 1e9 * bytes_per_param) / (1024**3)
print(f"Model weights: {weight_memory_gb:.1f} GB")

# Memory for gradients (same size as weights)
gradient_memory_gb = weight_memory_gb
print(f"Gradients: {gradient_memory_gb:.1f} GB")

# Memory for optimizer states (Adam stores 2 extra copies)
optimizer_memory_gb = weight_memory_gb * 2
print(f"Optimizer states: {optimizer_memory_gb:.1f} GB")

# Total memory needed
total_memory_gb = weight_memory_gb + gradient_memory_gb + optimizer_memory_gb
print(f"\nTotal training memory: {total_memory_gb:.1f} GB")
print(f"Number of A100 GPUs needed (80GB each): {total_memory_gb / 80:.0f}")
```

**Expected output:**

```
Model weights: 13.0 GB
Gradients: 13.0 GB
Optimizer states: 26.0 GB

Total training memory: 52.0 GB
Number of A100 GPUs needed (80GB each): 1
```

**Line-by-line explanation:**

- `model_size_billions = 7` -- We are calculating for a 7-billion-parameter model
- `bytes_per_param = 2` -- Each parameter uses 2 bytes when stored as a 16-bit float (half precision)
- `weight_memory_gb` -- We convert total bytes to gigabytes by dividing by 1024 three times
- `gradient_memory_gb` -- Gradients need the same memory as the weights themselves
- `optimizer_memory_gb` -- The Adam optimizer stores two extra values (momentum and variance) for each parameter, so it needs 2x the weight memory
- `total_memory_gb` -- The sum gives us roughly 52 GB just for a 7B model -- and this does not even include the data batches or activation memory

### The Key Insight

Most of the model's knowledge is already good. When you fine-tune for a specific task, you only need to make **small adjustments**. Updating all 7 billion parameters is like repainting an entire house when you only want to change the color of one room.

```
+---------------------------------------------------------------+
|          FULL FINE-TUNING vs WHAT WE ACTUALLY NEED            |
+---------------------------------------------------------------+
|                                                               |
|  Full Fine-Tuning:                                            |
|  [====================================================]      |
|   All 7 billion parameters updated                            |
|                                                               |
|  What actually changes meaningfully:                          |
|  [==]                                                         |
|   Only a small fraction matters for the new task              |
|                                                               |
+---------------------------------------------------------------+
```

---

## 21.2 What Is LoRA? The Sticky Note Approach

### The Core Idea

LoRA stands for **Low-Rank Adaptation**. The key idea is beautifully simple:

> Instead of changing the original weights of the model, add small trainable matrices alongside them.

Think of it this way:

```
+---------------------------------------------------------------+
|              THE STICKY NOTE ANALOGY                          |
+---------------------------------------------------------------+
|                                                               |
|  FULL FINE-TUNING:                                            |
|  You photocopy the entire 1000-page textbook and              |
|  rewrite every page. Expensive, slow, and wasteful.           |
|                                                               |
|  LoRA:                                                        |
|  You keep the original textbook untouched.                    |
|  You add small sticky notes on specific pages.                |
|  The sticky notes contain your customizations.                |
|  Original book + sticky notes = your customized version.      |
|                                                               |
|  Benefits:                                                    |
|  - The original book stays intact (reusable)                  |
|  - Sticky notes are tiny (low memory)                         |
|  - You can swap sticky note sets for different tasks          |
|  - Much cheaper than photocopying the whole book              |
|                                                               |
+---------------------------------------------------------------+
```

### How LoRA Works Mathematically

In a neural network, each layer has a weight matrix **W**. During full fine-tuning, we update W directly:

```
W_new = W_original + delta_W
```

Where `delta_W` is the change we learn during training. The problem is that `delta_W` is the same size as `W` -- potentially millions or billions of numbers.

LoRA's insight: `delta_W` can be **approximated** using two much smaller matrices:

```
delta_W = A x B
```

Where:
- **A** is a small matrix (tall and thin)
- **B** is a small matrix (short and wide)
- Their product gives us the same shape as the original weight matrix

```
+---------------------------------------------------------------+
|              HOW LoRA DECOMPOSES THE CHANGE                   |
+---------------------------------------------------------------+
|                                                               |
|  Original weight W:     4096 x 4096 = 16,777,216 params      |
|                                                               |
|  Full fine-tuning:                                            |
|  delta_W:               4096 x 4096 = 16,777,216 params      |
|                                                               |
|  LoRA (rank = 8):                                             |
|  A:                     4096 x 8    =    32,768 params        |
|  B:                     8 x 4096    =    32,768 params        |
|  A x B:                 4096 x 4096 (reconstructed)           |
|  Total LoRA params:                 =    65,536 params        |
|                                                               |
|  Reduction: 16,777,216 / 65,536 = 256x fewer parameters!     |
|                                                               |
+---------------------------------------------------------------+
```

```python
# Demonstrating LoRA's parameter savings

import numpy as np

# Original weight matrix dimensions
d_in = 4096   # Input dimension
d_out = 4096  # Output dimension

# Full fine-tuning: update entire weight matrix
full_params = d_in * d_out
print(f"Full fine-tuning parameters: {full_params:,}")

# LoRA: use two small matrices instead
rank = 8  # The LoRA rank (a small number)

# Matrix A: d_in x rank
a_params = d_in * rank
# Matrix B: rank x d_out
b_params = rank * d_out

lora_params = a_params + b_params
print(f"LoRA parameters (rank={rank}): {lora_params:,}")

# How much smaller?
reduction = full_params / lora_params
print(f"Parameter reduction: {reduction:.0f}x fewer parameters")
print(f"LoRA is {lora_params/full_params*100:.2f}% of full fine-tuning")
```

**Expected output:**

```
Full fine-tuning parameters: 16,777,216
LoRA parameters (rank=8): 65,536
Parameter reduction: 256x fewer parameters
LoRA is 0.39% of full fine-tuning
```

**Line-by-line explanation:**

- `d_in = 4096` and `d_out = 4096` -- These are typical dimensions for weight matrices in large language models like LLaMA-7B
- `full_params = d_in * d_out` -- Full fine-tuning updates every element in the 4096x4096 matrix
- `rank = 8` -- The LoRA rank controls how many parameters we use. Lower rank means fewer parameters but less expressive power
- `a_params = d_in * rank` -- Matrix A has shape 4096x8, so it has 32,768 parameters
- `b_params = rank * d_out` -- Matrix B has shape 8x4096, so it also has 32,768 parameters
- The total LoRA parameters (65,536) are only 0.39% of the full fine-tuning parameters (16.7 million)

### What "Low-Rank" Means

The word **rank** in "Low-Rank Adaptation" comes from linear algebra. Think of rank as a measure of complexity:

```
+---------------------------------------------------------------+
|              UNDERSTANDING RANK                               |
+---------------------------------------------------------------+
|                                                               |
|  Think of rank as the number of "building blocks" you use     |
|  to construct a change.                                       |
|                                                               |
|  Rank 1:  Like having 1 crayon -- limited but fast            |
|  Rank 4:  Like having 4 crayons -- more colors available      |
|  Rank 8:  Like having 8 crayons -- good for most tasks        |
|  Rank 16: Like having 16 crayons -- very detailed             |
|  Rank 64: Like having 64 crayons -- nearly full capability    |
|                                                               |
|  Key insight: Most fine-tuning tasks do NOT need high rank.   |
|  The changes we need are often simple and low-dimensional.    |
|                                                               |
+---------------------------------------------------------------+
```

```python
# Showing how rank affects parameter count

d = 4096  # Typical hidden dimension

print(f"{'Rank':<8} {'LoRA Params':<15} {'% of Full':<12} {'Analogy'}")
print("-" * 60)

ranks_and_analogies = [
    (1, "1 crayon"),
    (4, "4 crayons"),
    (8, "8 crayons (common default)"),
    (16, "16 crayons"),
    (32, "32 crayons"),
    (64, "64 crayons"),
    (128, "128 crayons"),
]

full_params = d * d

for rank, analogy in ranks_and_analogies:
    lora_params = 2 * d * rank  # A + B matrices
    percentage = (lora_params / full_params) * 100
    print(f"{rank:<8} {lora_params:<15,} {percentage:<12.2f} {analogy}")
```

**Expected output:**

```
Rank     LoRA Params     % of Full    Analogy
------------------------------------------------------------
1        8,192           0.05         1 crayon
4        32,768          0.20         4 crayons
8        65,536          0.39         8 crayons (common default)
16       131,072         0.78         16 crayons
32       262,144         1.56         32 crayons
64       524,288         3.12         64 crayons
128      1,048,576       6.25         128 crayons
```

---

## 21.3 LoRA in Detail: How the Forward Pass Works

### During Inference (Using the Model)

When you use a LoRA-adapted model, the computation for each adapted layer looks like this:

```
output = W_original @ x + (A @ B) @ x
```

The original weight matrix processes the input as usual, and the LoRA matrices add their small correction:

```
+---------------------------------------------------------------+
|              LoRA FORWARD PASS                                |
+---------------------------------------------------------------+
|                                                               |
|  Input x                                                      |
|    |                                                          |
|    +------------------+------------------+                    |
|    |                  |                  |                    |
|    v                  v                  v                    |
|  [W_original]       [A]                                      |
|    |              (4096x8)                                    |
|    |                  |                                       |
|    |                  v                                       |
|    |                [B]                                       |
|    |              (8x4096)                                    |
|    |                  |                                       |
|    v                  v                                       |
|    +--------( + )--------+                                    |
|             |                                                 |
|             v                                                 |
|          Output                                               |
|                                                               |
|  W_original is FROZEN (not trained)                           |
|  Only A and B are trained                                     |
|                                                               |
+---------------------------------------------------------------+
```

```python
import numpy as np

# Simulating a LoRA forward pass
np.random.seed(42)

# Dimensions
d_in = 8     # Simplified input dimension
d_out = 8    # Simplified output dimension
rank = 2     # LoRA rank

# Original weight matrix (frozen -- not trained)
W_original = np.random.randn(d_out, d_in) * 0.1

# LoRA matrices (these are trained)
A = np.random.randn(d_out, rank) * 0.01  # Initialized small
B = np.zeros((rank, d_in))               # Initialized to zero

# A sample input
x = np.random.randn(d_in, 1)

# Forward pass WITHOUT LoRA (original model)
output_original = W_original @ x
print("Output without LoRA:")
print(output_original.flatten()[:4].round(3))

# Forward pass WITH LoRA
# At initialization, B is zero, so LoRA adds nothing
lora_output = (A @ B) @ x
output_with_lora = W_original @ x + lora_output
print("\nOutput with LoRA (before training, B=0):")
print(output_with_lora.flatten()[:4].round(3))
print("Same as original? ", np.allclose(output_original, output_with_lora))

# After training, B is no longer zero
B_trained = np.random.randn(rank, d_in) * 0.1  # Simulated trained values
lora_output_trained = (A @ B_trained) @ x
output_adapted = W_original @ x + lora_output_trained
print("\nOutput with LoRA (after training):")
print(output_adapted.flatten()[:4].round(3))
print("Different from original? ", not np.allclose(output_original, output_adapted))
```

**Expected output:**

```
Output without LoRA:
[ 0.004 -0.058  0.06  -0.059]

Output with LoRA (before training, B=0):
[ 0.004 -0.058  0.06  -0.059]
Same as original?  True

Output with LoRA (after training):
[-0.002 -0.056  0.06  -0.062]
Different from original?  True
```

**Line-by-line explanation:**

- `W_original` -- The frozen weight matrix from the pre-trained model. We never change this
- `A` -- One of the LoRA matrices, initialized with small random values
- `B = np.zeros(...)` -- The other LoRA matrix, initialized to all zeros. This is important because it means LoRA starts by adding nothing to the original model
- `output_original = W_original @ x` -- Standard forward pass through the original weight matrix
- `lora_output = (A @ B) @ x` -- The LoRA correction. Since B is all zeros at the start, this produces zeros, so the model behaves exactly like the original
- After training, B contains learned values, so the LoRA correction modifies the output

### Why Initialize B to Zero?

This is a clever design choice. When training starts:

- B is all zeros
- So `A @ B` is all zeros
- So the LoRA-adapted model produces exactly the same output as the original model

This means training starts from a stable point -- the pre-trained model's behavior -- and gradually learns adjustments. It is much better than starting from random noise.

---

## 21.4 Which Layers to Adapt

### Transformer Layer Structure

A transformer model has many layers, and each layer contains several weight matrices. Not all of them need LoRA adapters:

```
+---------------------------------------------------------------+
|          INSIDE A TRANSFORMER LAYER                           |
+---------------------------------------------------------------+
|                                                               |
|  Self-Attention:                                              |
|    [Q] Query projection    <-- Usually adapted with LoRA     |
|    [K] Key projection      <-- Sometimes adapted             |
|    [V] Value projection    <-- Usually adapted with LoRA     |
|    [O] Output projection   <-- Sometimes adapted             |
|                                                               |
|  Feed-Forward Network:                                        |
|    [Gate] Gate projection  <-- Sometimes adapted              |
|    [Up]   Up projection    <-- Sometimes adapted              |
|    [Down] Down projection  <-- Sometimes adapted              |
|                                                               |
+---------------------------------------------------------------+
```

### Common Choices

```python
# Common LoRA target modules for different models

# For LLaMA / Mistral models
llama_targets = {
    "minimal": ["q_proj", "v_proj"],           # Most common, least parameters
    "standard": ["q_proj", "k_proj", "v_proj", "o_proj"],  # Better quality
    "full": ["q_proj", "k_proj", "v_proj", "o_proj",       # Best quality
             "gate_proj", "up_proj", "down_proj"],
}

# Calculate parameter counts for LLaMA-7B (hidden_size=4096)
hidden_size = 4096
num_layers = 32
rank = 8

print(f"LLaMA-7B LoRA parameter counts (rank={rank}):")
print(f"{'Target':<12} {'Modules':<50} {'LoRA Params':<15}")
print("-" * 77)

for name, modules in llama_targets.items():
    params_per_layer = len(modules) * 2 * hidden_size * rank
    total_params = params_per_layer * num_layers
    print(f"{name:<12} {str(modules):<50} {total_params:>12,}")

# Total model parameters for reference
total_model_params = 7_000_000_000
print(f"\n{'Total model parameters:':<62} {total_model_params:>12,}")
```

**Expected output:**

```
LLaMA-7B LoRA parameter counts (rank=8):
Target       Modules                                            LoRA Params
-----------------------------------------------------------------------------
minimal      ['q_proj', 'v_proj']                                  4,194,304
standard     ['q_proj', 'k_proj', 'v_proj', 'o_proj']             8,388,608
full         ['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate ...  14,680,064

Total model parameters:                                       7,000,000,000
```

**Line-by-line explanation:**

- `llama_targets` -- A dictionary showing three common configurations for which weight matrices to adapt
- `"minimal": ["q_proj", "v_proj"]` -- Adapting only the query and value projections in the attention mechanism. This is the most common choice because these matrices have the biggest impact on what the model attends to
- `"standard"` -- Also includes key and output projections for better quality
- `"full"` -- Includes the feed-forward network projections too, for maximum adaptation capability
- Even the "full" configuration trains only about 14.7 million parameters out of 7 billion -- that is just 0.21%

### General Guidelines

```
+---------------------------------------------------------------+
|          CHOOSING TARGET MODULES                              |
+---------------------------------------------------------------+
|                                                               |
|  Task Type              Recommended Targets                   |
|  ---------              ---------------------                 |
|  Simple classification  q_proj, v_proj (minimal)              |
|  Chat / instruction     q_proj, k_proj, v_proj, o_proj        |
|  Complex reasoning      All attention + FFN layers            |
|  Domain adaptation      All attention + FFN layers            |
|                                                               |
|  Rule of thumb:                                               |
|  - Start with q_proj and v_proj                               |
|  - Add more if results are not good enough                    |
|  - More targets = more parameters = more memory               |
|                                                               |
+---------------------------------------------------------------+
```

---

## 21.5 The Rank Parameter: Finding the Sweet Spot

### What Rank Should You Use?

The rank parameter is the most important hyperparameter in LoRA. It controls the trade-off between model quality and training cost:

```python
# Comparing different rank values for LLaMA-7B
# Target modules: q_proj, v_proj

hidden_size = 4096
num_layers = 32
num_target_modules = 2  # q_proj and v_proj

print(f"{'Rank':<6} {'LoRA Params':<15} {'Memory (MB)':<14} {'When to Use'}")
print("-" * 70)

rank_recommendations = [
    (4, "Simple tasks, limited GPU"),
    (8, "Default choice, good balance"),
    (16, "Most fine-tuning tasks"),
    (32, "Complex tasks, large datasets"),
    (64, "Maximum quality, expensive"),
    (128, "Rarely needed, diminishing returns"),
]

for rank, recommendation in rank_recommendations:
    lora_params = num_target_modules * num_layers * 2 * hidden_size * rank
    # Each param is fp16 (2 bytes), plus optimizer states (~4x for Adam)
    memory_mb = (lora_params * 2 * 5) / (1024 * 1024)  # weights + optimizer
    print(f"{rank:<6} {lora_params:<15,} {memory_mb:<14.1f} {recommendation}")
```

**Expected output:**

```
Rank   LoRA Params     Memory (MB)    When to Use
----------------------------------------------------------------------
4      2,097,152       20.0           Simple tasks, limited GPU
8      4,194,304       40.0           Default choice, good balance
16     8,388,608       80.0           Most fine-tuning tasks
32     16,777,216      160.0          Complex tasks, large datasets
64     33,554,432      320.0          Maximum quality, expensive
128    67,108,864      640.0          Rarely needed, diminishing returns
```

### The Diminishing Returns Problem

Higher rank does not always mean better results:

```
+---------------------------------------------------------------+
|          RANK vs QUALITY                                      |
+---------------------------------------------------------------+
|                                                               |
|  Quality                                                      |
|  ^                                                            |
|  |                          ..............................    |
|  |                    ......                                  |
|  |                ....                                        |
|  |            ....                                            |
|  |         ...                                                |
|  |       ..                                                   |
|  |     ..                                                     |
|  |   ..                                                       |
|  |  .                                                         |
|  | .                                                          |
|  |.                                                           |
|  +-------------------------------------------------> Rank    |
|  0    4    8   16   32   64  128  256                         |
|                                                               |
|  Quality improves rapidly at first, then plateaus.            |
|  Rank 8-16 is often the sweet spot.                           |
|                                                               |
+---------------------------------------------------------------+
```

---

## 21.6 LoRA Alpha: The Scaling Factor

### What Is LoRA Alpha?

LoRA has a second important parameter called **alpha** (written as `lora_alpha`). It controls how much the LoRA adapters influence the output:

```
Effective LoRA contribution = (alpha / rank) * (A @ B) @ x
```

The ratio `alpha / rank` is called the **scaling factor**:

```python
# Understanding the LoRA scaling factor

print(f"{'Rank':<6} {'Alpha':<7} {'Scale':<8} {'Effect'}")
print("-" * 50)

configs = [
    (8, 8, "LoRA contributes at 1x strength"),
    (8, 16, "LoRA contributes at 2x strength (common)"),
    (8, 32, "LoRA contributes at 4x strength"),
    (16, 16, "LoRA contributes at 1x strength"),
    (16, 32, "LoRA contributes at 2x strength (common)"),
    (32, 64, "LoRA contributes at 2x strength"),
]

for rank, alpha, effect in configs:
    scale = alpha / rank
    print(f"{rank:<6} {alpha:<7} {scale:<8.1f} {effect}")
```

**Expected output:**

```
Rank   Alpha   Scale    Effect
--------------------------------------------------
8      8       1.0      LoRA contributes at 1x strength
8      16      2.0      LoRA contributes at 2x strength (common)
8      32      4.0      LoRA contributes at 4x strength
16     16      1.0      LoRA contributes at 1x strength
16     32      2.0      LoRA contributes at 2x strength (common)
32     64      2.0      LoRA contributes at 2x strength
```

### Common Practice

A widely used rule of thumb is to set `lora_alpha = 2 * rank`. This gives a scaling factor of 2, which works well for most tasks.

```
+---------------------------------------------------------------+
|          RECOMMENDED LoRA CONFIGURATIONS                      |
+---------------------------------------------------------------+
|                                                               |
|  Task               Rank    Alpha    Targets                  |
|  ----               ----    -----    -------                  |
|  Quick experiment    4       8       q_proj, v_proj           |
|  Standard tuning     8      16       q_proj, v_proj           |
|  Better quality     16      32       q_proj, k_proj, v_proj   |
|  Best quality       32      64       All attention + FFN      |
|                                                               |
+---------------------------------------------------------------+
```

---

## 21.7 QLoRA: Making It Even Cheaper

### What Is Quantization?

Before explaining QLoRA, you need to understand **quantization** (making numbers smaller):

```
+---------------------------------------------------------------+
|              WHAT IS QUANTIZATION?                            |
+---------------------------------------------------------------+
|                                                               |
|  Think of it like map resolution:                             |
|                                                               |
|  32-bit float (fp32):  Like a satellite photo                 |
|    Every tiny detail visible                                  |
|    4 bytes per number                                         |
|                                                               |
|  16-bit float (fp16):  Like a detailed road map               |
|    Most details preserved                                     |
|    2 bytes per number (2x smaller)                            |
|                                                               |
|  8-bit integer (int8):  Like a city map                       |
|    Major features visible                                     |
|    1 byte per number (4x smaller)                             |
|                                                               |
|  4-bit integer (int4):  Like a rough sketch                   |
|    Basic structure preserved                                  |
|    0.5 bytes per number (8x smaller)                          |
|                                                               |
+---------------------------------------------------------------+
```

```python
# Demonstrating quantization levels and memory savings

model_params = 7_000_000_000  # 7 billion parameters

print(f"Memory for {model_params/1e9:.0f}B parameter model:\n")
print(f"{'Precision':<20} {'Bytes/Param':<15} {'Memory (GB)':<15} {'Relative'}")
print("-" * 65)

precisions = [
    ("fp32 (32-bit)", 4, "Full precision"),
    ("fp16 (16-bit)", 2, "Half precision"),
    ("int8 (8-bit)", 1, "Standard quantization"),
    ("int4 (4-bit)", 0.5, "QLoRA quantization"),
]

base_memory = None
for name, bytes_per_param, note in precisions:
    memory_gb = (model_params * bytes_per_param) / (1024**3)
    if base_memory is None:
        base_memory = memory_gb
    ratio = memory_gb / base_memory
    print(f"{name:<20} {bytes_per_param:<15} {memory_gb:<15.1f} {ratio:.1f}x")
```

**Expected output:**

```
Memory for 7B parameter model:

Precision            Bytes/Param     Memory (GB)     Relative
-----------------------------------------------------------------
fp32 (32-bit)        4               26.1            1.0x
fp16 (16-bit)        2               13.0            0.5x
int8 (8-bit)         1               6.5             0.2x
int4 (4-bit)         0.5             3.3             0.1x
```

### What Is QLoRA?

QLoRA combines two techniques:

1. **Quantize** the base model to 4-bit (shrink it to fit in memory)
2. **Add LoRA adapters** in 16-bit precision (for training accuracy)

```
+---------------------------------------------------------------+
|              QLoRA = QUANTIZATION + LoRA                      |
+---------------------------------------------------------------+
|                                                               |
|  Step 1: Load the base model in 4-bit                         |
|  +---------------------------------------------+             |
|  |  Base Model (4-bit quantized)               |             |
|  |  7B params x 0.5 bytes = 3.3 GB             |             |
|  |  FROZEN -- not trained                       |             |
|  +---------------------------------------------+             |
|                                                               |
|  Step 2: Add LoRA adapters in 16-bit                          |
|  +---------------------------------------------+             |
|  |  LoRA Adapters (16-bit, fp16)               |             |
|  |  ~4M params x 2 bytes = ~8 MB               |             |
|  |  TRAINABLE -- updated during training        |             |
|  +---------------------------------------------+             |
|                                                               |
|  Total memory: ~3.3 GB + ~8 MB = ~3.3 GB                     |
|  Compare to full fine-tuning: ~52 GB                          |
|  Memory reduction: ~16x                                       |
|                                                               |
+---------------------------------------------------------------+
```

### QLoRA's Three Key Innovations

QLoRA introduced three techniques that make 4-bit training work:

```python
# QLoRA's memory savings compared to other approaches

model_size_b = 7  # Billion parameters

approaches = {
    "Full Fine-Tuning (fp16)": {
        "model_bytes": 2,    # fp16 weights
        "grad_bytes": 2,     # fp16 gradients
        "optim_bytes": 4,    # fp32 optimizer states (Adam)
        "lora": False,
    },
    "LoRA (fp16 base)": {
        "model_bytes": 2,    # fp16 weights (frozen)
        "grad_bytes": 0,     # No gradients for frozen weights
        "optim_bytes": 0,    # No optimizer states for frozen weights
        "lora": True,
        "lora_ratio": 0.003, # ~0.3% of params are LoRA
    },
    "QLoRA (4-bit base)": {
        "model_bytes": 0.5,  # 4-bit weights (frozen)
        "grad_bytes": 0,     # No gradients for frozen weights
        "optim_bytes": 0,    # No optimizer states for frozen weights
        "lora": True,
        "lora_ratio": 0.003,
    },
}

print(f"{'Approach':<30} {'Model (GB)':<12} {'Training (GB)':<14} {'Total (GB)'}")
print("-" * 70)

for name, config in approaches.items():
    params = model_size_b * 1e9
    model_mem = (params * config["model_bytes"]) / (1024**3)

    if config["lora"]:
        lora_params = params * config["lora_ratio"]
        # LoRA params in fp16 + optimizer states
        training_mem = (lora_params * (2 + 2 + 4)) / (1024**3)
    else:
        training_mem = (params * (config["grad_bytes"] + config["optim_bytes"])) / (1024**3)

    total = model_mem + training_mem
    print(f"{name:<30} {model_mem:<12.1f} {training_mem:<14.2f} {total:.1f}")
```

**Expected output:**

```
Approach                       Model (GB)   Training (GB)  Total (GB)
----------------------------------------------------------------------
Full Fine-Tuning (fp16)        13.0         39.12          52.1
LoRA (fp16 base)               13.0         0.16           13.1
QLoRA (4-bit base)             3.3          0.16           3.4
```

**Line-by-line explanation:**

- Full fine-tuning needs 52 GB -- requires multiple expensive GPUs
- LoRA reduces training memory dramatically, but still loads the full model in fp16 (13 GB)
- QLoRA shrinks the model itself to 4-bit (3.3 GB) and adds tiny LoRA adapters
- QLoRA makes it possible to fine-tune a 7B model on a single consumer GPU with 6 GB of VRAM

### NF4: The Special 4-Bit Format

QLoRA does not use standard 4-bit integers. It uses a special format called **NF4** (NormalFloat4):

```
+---------------------------------------------------------------+
|              NF4 vs STANDARD INT4                             |
+---------------------------------------------------------------+
|                                                               |
|  Standard int4:                                               |
|    16 evenly spaced values: -8, -7, -6 ... 0 ... 6, 7        |
|    Problem: Neural network weights follow a bell curve         |
|    Many values are wasted on rare extreme values               |
|                                                               |
|  NF4 (NormalFloat4):                                          |
|    16 values spaced to match the bell curve of weights         |
|    More values near zero (where most weights are)              |
|    Fewer values at extremes (where few weights are)            |
|    Result: Much better approximation with the same 4 bits      |
|                                                               |
|  Standard int4:   |--|--|--|--|--|--|--|--|--|--|--|--|--|--|   |
|  NF4:             |-|--|---|-----|-----|---|--|-|              |
|                    ^  More values packed near center  ^        |
|                                                               |
+---------------------------------------------------------------+
```

### Double Quantization

QLoRA also quantizes the **quantization constants** themselves (yes, really):

```
+---------------------------------------------------------------+
|              DOUBLE QUANTIZATION                              |
+---------------------------------------------------------------+
|                                                               |
|  Regular quantization:                                        |
|    Weights are 4-bit                                          |
|    But each group of 64 weights needs a scaling factor         |
|    These scaling factors are stored in fp32 (4 bytes each)     |
|    Extra memory: 0.5 bits per parameter                        |
|                                                               |
|  Double quantization:                                         |
|    The scaling factors are ALSO quantized to 8-bit             |
|    Extra memory: 0.125 bits per parameter                      |
|    Saves ~3 GB for a 65B parameter model                       |
|                                                               |
+---------------------------------------------------------------+
```

---

## 21.8 LoRA vs QLoRA: When to Use Which

```
+---------------------------------------------------------------+
|              LoRA vs QLoRA COMPARISON                          |
+---------------------------------------------------------------+
|                                                               |
|  Feature           LoRA              QLoRA                    |
|  -------           ----              -----                    |
|  Base model        fp16 (full)       4-bit (quantized)        |
|  Training speed    Faster            Slightly slower           |
|  Memory needed     Moderate          Much less                 |
|  Quality           Excellent         Nearly as good            |
|  GPU required      16+ GB VRAM       6+ GB VRAM               |
|  Best for          Production        Learning, prototyping     |
|                                                               |
|  When to use LoRA:                                            |
|  - You have a good GPU (A100, H100)                           |
|  - Maximum training speed matters                             |
|  - You want the highest possible quality                      |
|                                                               |
|  When to use QLoRA:                                           |
|  - You have a consumer GPU (RTX 3060, 3070, etc.)             |
|  - Memory is your bottleneck                                  |
|  - You are experimenting or prototyping                       |
|  - You want to fine-tune models that do not fit in fp16       |
|                                                               |
+---------------------------------------------------------------+
```

```python
# Decision helper: LoRA vs QLoRA

def recommend_approach(gpu_vram_gb, model_size_b):
    """Recommend LoRA or QLoRA based on available GPU memory."""

    # Memory needed for fp16 model + LoRA training
    lora_memory = (model_size_b * 1e9 * 2) / (1024**3) + 2  # +2 GB overhead

    # Memory needed for 4-bit model + LoRA training
    qlora_memory = (model_size_b * 1e9 * 0.5) / (1024**3) + 2  # +2 GB overhead

    print(f"\nGPU VRAM: {gpu_vram_gb} GB | Model: {model_size_b}B parameters")
    print(f"  LoRA needs:  ~{lora_memory:.0f} GB")
    print(f"  QLoRA needs: ~{qlora_memory:.0f} GB")

    if gpu_vram_gb >= lora_memory:
        print(f"  Recommendation: Use LoRA (faster training, best quality)")
    elif gpu_vram_gb >= qlora_memory:
        print(f"  Recommendation: Use QLoRA (fits in your GPU!)")
    else:
        print(f"  Recommendation: Need a bigger GPU or smaller model")

# Test different scenarios
recommend_approach(gpu_vram_gb=24, model_size_b=7)   # RTX 3090/4090
recommend_approach(gpu_vram_gb=8, model_size_b=7)    # RTX 3070
recommend_approach(gpu_vram_gb=16, model_size_b=13)  # RTX 4080/A4000
recommend_approach(gpu_vram_gb=80, model_size_b=70)  # A100
```

**Expected output:**

```
GPU VRAM: 24 GB | Model: 7B parameters
  LoRA needs:  ~15 GB
  QLoRA needs: ~5 GB
  Recommendation: Use LoRA (faster training, best quality)

GPU VRAM: 8 GB | Model: 7B parameters
  LoRA needs:  ~15 GB
  QLoRA needs: ~5 GB
  Recommendation: Use QLoRA (fits in your GPU!)

GPU VRAM: 16 GB | Model: 13B parameters
  LoRA needs:  ~26 GB
  QLoRA needs: ~8 GB
  Recommendation: Use QLoRA (fits in your GPU!)

GPU VRAM: 80 GB | Model: 70B parameters
  LoRA needs:  ~132 GB
  QLoRA needs: ~35 GB
  Recommendation: Use QLoRA (fits in your GPU!)
```

---

## 21.9 Merging LoRA Adapters

### After Training: Merge or Keep Separate?

Once training is done, you have two options:

```
+---------------------------------------------------------------+
|          MERGE vs KEEP SEPARATE                               |
+---------------------------------------------------------------+
|                                                               |
|  Option 1: Keep adapters separate                             |
|  +------------------+  +------------------+                   |
|  |  Base Model      |  |  LoRA Adapter    |                  |
|  |  (7 GB)          |  |  (16 MB)         |                  |
|  +------------------+  +------------------+                   |
|  Pros: Swap adapters, share base model                        |
|  Cons: Slightly slower inference                              |
|                                                               |
|  Option 2: Merge into one model                               |
|  +---------------------------------------+                    |
|  |  Merged Model (Base + LoRA)           |                   |
|  |  (7 GB)                               |                   |
|  +---------------------------------------+                    |
|  Pros: Simpler deployment, normal speed                       |
|  Cons: Cannot swap adapters, larger file                      |
|                                                               |
+---------------------------------------------------------------+
```

```python
import numpy as np

# Simulating the merge process

# Original weight matrix
W = np.array([
    [1.0, 2.0, 3.0],
    [4.0, 5.0, 6.0],
    [7.0, 8.0, 9.0],
])

# LoRA matrices (after training)
rank = 2
alpha = 4
A = np.array([
    [0.1, 0.2],
    [0.3, 0.4],
    [0.5, 0.6],
])
B = np.array([
    [0.01, 0.02, 0.03],
    [0.04, 0.05, 0.06],
])

# Scaling factor
scaling = alpha / rank
print(f"Scaling factor (alpha/rank): {alpha}/{rank} = {scaling}")

# Compute the LoRA delta
delta_W = scaling * (A @ B)
print(f"\nLoRA delta (change to weights):\n{delta_W.round(4)}")

# Merge: add LoRA delta to original weights
W_merged = W + delta_W
print(f"\nOriginal weights:\n{W}")
print(f"\nMerged weights:\n{W_merged.round(4)}")

# Verify: merged model gives same output as separate model
x = np.array([1.0, 2.0, 3.0])

output_separate = W @ x + scaling * (A @ B) @ x
output_merged = W_merged @ x

print(f"\nOutput (separate): {output_separate.round(4)}")
print(f"Output (merged):   {output_merged.round(4)}")
print(f"Same result: {np.allclose(output_separate, output_merged)}")
```

**Expected output:**

```
Scaling factor (alpha/rank): 4/2 = 2.0

LoRA delta (change to weights):
[[0.018  0.024  0.03 ]
 [0.038  0.052  0.066]
 [0.058  0.08   0.102]]

Original weights:
[[1. 2. 3.]
 [4. 5. 6.]
 [7. 8. 9.]]

Merged weights:
[[1.018  2.024  3.03  ]
 [4.038  5.052  6.066 ]
 [7.058  8.08   9.102 ]]

Output (separate): [14.162 32.346 50.53 ]
Output (merged):   [14.162 32.346 50.53 ]
Same result: True
```

---

## 21.10 LoRA Dropout

### Preventing Overfitting

Like other neural network techniques, LoRA can overfit (memorize the training data instead of learning general patterns). LoRA includes a **dropout** parameter to help prevent this:

```
+---------------------------------------------------------------+
|              LoRA DROPOUT                                     |
+---------------------------------------------------------------+
|                                                               |
|  Dropout randomly "turns off" some connections during          |
|  training, forcing the model to not rely too heavily on        |
|  any single connection.                                       |
|                                                               |
|  Without dropout:     With dropout (p=0.1):                   |
|  x --> [A] --> [B]    x --> [A] --> [B]                       |
|  All paths active     10% of paths randomly blocked            |
|                                                               |
|  Typical values:                                              |
|  - 0.0:  No dropout (for large datasets)                      |
|  - 0.05: Light dropout (default for most tasks)               |
|  - 0.1:  Moderate dropout (small datasets)                    |
|  - 0.2:  Heavy dropout (very small datasets)                  |
|                                                               |
+---------------------------------------------------------------+
```

---

## 21.11 Putting It All Together: LoRA Configuration

Here is a complete LoRA configuration with explanations:

```python
# Complete LoRA configuration example
# This is what you would use with the PEFT library (covered in Chapter 22)

lora_config = {
    # Rank: controls adapter size
    # Higher = more parameters, potentially better quality
    # Lower = fewer parameters, faster training
    "r": 16,

    # Alpha: scaling factor
    # Common choice: alpha = 2 * rank
    "lora_alpha": 32,

    # Dropout: regularization to prevent overfitting
    # Use higher values for smaller datasets
    "lora_dropout": 0.05,

    # Target modules: which weight matrices to adapt
    # For LLaMA models, these are the attention projections
    "target_modules": ["q_proj", "v_proj", "k_proj", "o_proj"],

    # Bias: whether to train bias terms too
    # "none" = only train LoRA matrices (most common)
    # "all" = also train all bias terms
    # "lora_only" = only train biases in LoRA layers
    "bias": "none",

    # Task type: what kind of task we are fine-tuning for
    # CAUSAL_LM = text generation (like chatbots)
    # SEQ_CLS = classification
    # SEQ_2_SEQ_LM = translation, summarization
    "task_type": "CAUSAL_LM",
}

# Print the configuration
print("LoRA Configuration:")
print("=" * 50)
for key, value in lora_config.items():
    print(f"  {key}: {value}")

# Calculate total trainable parameters
hidden_size = 4096  # LLaMA-7B
num_layers = 32
rank = lora_config["r"]
num_modules = len(lora_config["target_modules"])

trainable_params = num_modules * num_layers * 2 * hidden_size * rank
total_params = 7_000_000_000

print(f"\nTrainable parameters: {trainable_params:,}")
print(f"Total model parameters: {total_params:,}")
print(f"Percentage trainable: {trainable_params/total_params*100:.4f}%")
```

**Expected output:**

```
LoRA Configuration:
==================================================
  r: 16
  lora_alpha: 32
  lora_dropout: 0.05
  target_modules: ['q_proj', 'v_proj', 'k_proj', 'o_proj']
  bias: none
  task_type: CAUSAL_LM

Trainable parameters: 16,777,216
Total model parameters: 7,000,000,000
Percentage trainable: 0.2397%
```

---

## Common Mistakes

1. **Setting rank too high** -- Using rank=256 wastes memory and does not improve quality much. Start with 8 or 16 and increase only if needed.

2. **Forgetting to freeze the base model** -- LoRA only works if the base model weights are frozen. If you accidentally train everything, you lose the memory benefits.

3. **Wrong target modules** -- Different model architectures use different names for their layers. LLaMA uses `q_proj`, `v_proj`, etc. GPT-2 uses `c_attn`, `c_proj`. Always check the model's architecture.

4. **Misunderstanding alpha** -- Alpha is not "how much to train." It is a scaling factor. Setting alpha=1000 will not make training better; it will make the LoRA contribution too large and destabilize training.

5. **Not using QLoRA when memory is tight** -- If your model barely fits in GPU memory, training will crash during the forward pass. Use QLoRA to free up memory.

---

## Best Practices

1. **Start with rank=8, alpha=16** -- This is a good default for most tasks. Only change these if you have evidence they need adjustment.

2. **Always use dropout with small datasets** -- If you have fewer than 10,000 examples, use `lora_dropout=0.05` or higher to prevent overfitting.

3. **Target attention layers first** -- Start with `q_proj` and `v_proj`, then add more targets if results are not satisfactory.

4. **Use QLoRA for models over 7B** -- Unless you have a very powerful GPU, QLoRA makes large model fine-tuning practical.

5. **Save adapters separately** -- Keep your LoRA adapters in separate files. This lets you share the base model and swap adapters for different tasks.

6. **Test different ranks** -- Try rank 4, 8, 16, and 32 on a small subset of your data. Pick the lowest rank that gives good results.

---

## Quick Summary

LoRA and QLoRA make fine-tuning large language models accessible to everyone. Instead of updating billions of parameters (full fine-tuning), LoRA adds small trainable matrices called adapters that capture task-specific knowledge. QLoRA goes further by loading the base model in 4-bit precision, reducing memory requirements by up to 16x. The key parameters are rank (adapter size), alpha (scaling factor), dropout (regularization), and target modules (which layers to adapt). Together, these techniques let you fine-tune a 7B parameter model on a consumer GPU that costs a few hundred dollars.

---

## Key Points

- **Full fine-tuning** updates all model parameters and requires enormous GPU memory
- **LoRA** adds small trainable matrices (adapters) alongside frozen model weights
- The **rank** parameter controls adapter size -- lower rank means fewer parameters
- **LoRA alpha** scales the adapter contribution -- commonly set to 2x the rank
- **QLoRA** combines 4-bit quantization with LoRA for maximum memory efficiency
- **NF4** is a special 4-bit format optimized for neural network weight distributions
- **Target modules** determine which layers get adapters -- attention layers are the priority
- LoRA adapters can be **merged** into the base model for simpler deployment
- LoRA adapters can also be **kept separate** for easy swapping between tasks
- Even with aggressive LoRA settings, you train less than 1% of the total parameters

---

## Practice Questions

1. A model has weight matrices of size 2048x2048. You apply LoRA with rank=4. How many trainable parameters does each adapted layer have? How does this compare to the full weight matrix size?

2. You have a GPU with 12 GB of VRAM and want to fine-tune a 7B parameter model. Should you use LoRA or QLoRA? Explain your reasoning with memory calculations.

3. Explain why initializing the B matrix to zero is important for LoRA training. What would happen if both A and B were initialized randomly?

4. You set rank=8 and lora_alpha=32. What is the scaling factor? How would the model's behavior change if you doubled the alpha to 64?

5. Why is it generally better to adapt the query and value projection matrices rather than the key projection matrix? (Hint: think about what queries and values do in attention.)

---

## Exercises

### Exercise 1: LoRA Parameter Calculator

Write a Python function that takes a model's hidden size, number of layers, rank, and target modules, and calculates the total number of LoRA parameters, the percentage of the model that is trainable, and the estimated memory savings compared to full fine-tuning.

### Exercise 2: Rank Comparison Experiment

Using NumPy, simulate a LoRA decomposition at different ranks (1, 2, 4, 8, 16, 32). Start with a random 256x256 matrix, decompose it into A and B matrices at each rank, and compute the reconstruction error. Plot how the error decreases as rank increases.

### Exercise 3: Memory Budget Planner

Create a function that takes a GPU memory budget (in GB) and a model size (in billions of parameters) and recommends the best approach: full fine-tuning, LoRA, or QLoRA. It should also suggest the maximum rank that fits within the memory budget.

---

## What Is Next?

Now that you understand the theory behind LoRA and QLoRA, it is time to put them into practice. In Chapter 22, you will use the Hugging Face PEFT library to actually fine-tune a language model. You will load a base model, configure LoRA adapters, train on custom data, and merge the adapters back into the model. Everything you learned in this chapter -- rank, alpha, target modules -- will come alive in real code.
