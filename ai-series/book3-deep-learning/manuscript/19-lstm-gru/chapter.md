# Chapter 19: LSTM and GRU — Networks That Remember

## What You Will Learn

- What LSTM (Long Short-Term Memory) is and why it was invented
- How the forget gate, input gate, and output gate work
- What the cell state is and why it acts like a conveyor belt
- What GRU (Gated Recurrent Unit) is and how it simplifies LSTM
- How the reset gate and update gate work in GRU
- How to use PyTorch's `nn.LSTM` and `nn.GRU`
- When to choose LSTM vs GRU
- How to build a complete sentiment classification model

## Why This Chapter Matters

In the previous chapter, you learned that basic RNNs suffer from the vanishing gradient problem. They forget information from early time steps because the gradient signal weakens as it travels backward through the sequence. It is like trying to remember the first sentence of a book after reading 500 pages.

LSTM and GRU solve this problem by adding **gates**. Gates are learned mechanisms that control the flow of information. They decide what to remember, what to forget, and what to output at each step.

LSTM was introduced in 1997 and became the dominant architecture for sequence tasks for nearly two decades. GRU, introduced in 2014, is a simpler alternative that works just as well in many cases. Understanding both is essential because they are widely used in production systems for speech recognition, machine translation, text generation, and time series forecasting.

---

## 19.1 The LSTM Cell — A Controlled Memory Bank

An LSTM cell is like a **safety deposit box** at a bank. You have:
- A **forget gate** that decides what to throw away from the box
- An **input gate** that decides what new items to put in the box
- An **output gate** that decides what to take out and show to the world

The box itself is called the **cell state**. It is the long-term memory.

```
+------------------------------------------------------------------+
|                    LSTM Cell Overview                              |
+------------------------------------------------------------------+
|                                                                   |
|  Regular RNN has ONE state:  hidden state (h)                     |
|                                                                   |
|  LSTM has TWO states:                                             |
|    1. Cell state (c) = long-term memory (the conveyor belt)       |
|    2. Hidden state (h) = short-term memory (the working memory)   |
|                                                                   |
|  THREE gates control the information flow:                        |
|    1. Forget gate (f) = what to remove from long-term memory      |
|    2. Input gate (i) = what to add to long-term memory            |
|    3. Output gate (o) = what to reveal as output                  |
|                                                                   |
+------------------------------------------------------------------+
```

### The Cell State — A Conveyor Belt

The **cell state** is the key innovation of LSTM. Think of it as a **conveyor belt** running through the entire sequence. Information can ride the belt from the first step to the last step with minimal change.

```
+------------------------------------------------------------------+
|              The Conveyor Belt Analogy                             |
+------------------------------------------------------------------+
|                                                                   |
|  Cell state flows straight through with minimal changes:          |
|                                                                   |
|  c(0) =====> c(1) =====> c(2) =====> c(3) =====> c(4)           |
|        remove   add  remove   add  remove   add  remove   add    |
|         some    some   some   some   some   some   some   some   |
|                                                                   |
|  At each step, the gates make small, controlled modifications:    |
|    - The forget gate removes irrelevant information               |
|    - The input gate adds new relevant information                 |
|                                                                   |
|  Because the cell state flows mostly unchanged, gradients         |
|  can flow backward through it without vanishing!                  |
|                                                                   |
+------------------------------------------------------------------+
```

---

## 19.2 The Three Gates of LSTM

### Gate 1: The Forget Gate

The **forget gate** looks at the current input and the previous hidden state and decides which parts of the cell state to keep and which to throw away.

The forget gate produces values between 0 and 1 for each number in the cell state:
- **1** means "keep this completely"
- **0** means "forget this completely"
- **0.5** means "keep half of this"

```
+------------------------------------------------------------------+
|                    Forget Gate                                     |
+------------------------------------------------------------------+
|                                                                   |
|   Previous hidden state h(t-1) ----+                              |
|                                     |                              |
|   Current input x(t) --------------+--> [sigmoid] --> f(t)        |
|                                                                   |
|   f(t) = values between 0 and 1                                  |
|                                                                   |
|   New cell state = f(t) * old cell state                          |
|                                                                   |
|   If f(t) = 1: KEEP everything                                   |
|   If f(t) = 0: FORGET everything                                 |
|                                                                   |
+------------------------------------------------------------------+
```

**Real-world analogy:** Imagine you are taking notes in a class. At the start of a new topic, you might cross out (forget) notes about the previous topic that are no longer relevant.

### Gate 2: The Input Gate

The **input gate** decides what new information to add to the cell state. It has two parts:
1. A sigmoid layer that decides *which values* to update (0 to 1)
2. A tanh layer that creates *candidate values* to add (-1 to 1)

```
+------------------------------------------------------------------+
|                     Input Gate                                     |
+------------------------------------------------------------------+
|                                                                   |
|   h(t-1) and x(t) --> [sigmoid] --> i(t)  (what to update)       |
|                                                                   |
|   h(t-1) and x(t) --> [tanh]    --> g(t)  (candidate values)     |
|                                                                   |
|   New information = i(t) * g(t)                                   |
|                                                                   |
|   Cell state update: c(t) = f(t) * c(t-1) + i(t) * g(t)         |
|                              ^^^^^^^^^^^^^   ^^^^^^^^^^^          |
|                              keep from old   add new stuff        |
|                                                                   |
+------------------------------------------------------------------+
```

**Real-world analogy:** You decide which parts of the new lecture to write down (input gate) and what exactly to write (candidate values).

### Gate 3: The Output Gate

The **output gate** decides what to output based on the cell state. Not everything stored in memory needs to be revealed right now.

```
+------------------------------------------------------------------+
|                    Output Gate                                     |
+------------------------------------------------------------------+
|                                                                   |
|   h(t-1) and x(t) --> [sigmoid] --> o(t)  (what to output)       |
|                                                                   |
|   h(t) = o(t) * tanh(c(t))                                       |
|                                                                   |
|   The hidden state h(t) is a filtered version of the cell state.  |
|   The cell state holds everything. The hidden state reveals       |
|   only what is relevant right now.                                |
|                                                                   |
+------------------------------------------------------------------+
```

**Real-world analogy:** You know many facts from a class, but on an exam question about Chapter 3, you only write (output) the information relevant to Chapter 3.

### All Gates Together

```
+------------------------------------------------------------------+
|                Complete LSTM Cell Diagram                          |
+------------------------------------------------------------------+
|                                                                   |
|            c(t-1) --------[x]----------[+]-------> c(t)          |
|                            |            |                          |
|                           f(t)       i(t)*g(t)                    |
|                            |            |                          |
|                         [sigma]      [sigma] [tanh]               |
|                            |            |      |                   |
|                            +----+-------+------+                   |
|                                 |                                  |
|  x(t) -------------------------+                                  |
|  h(t-1) -----------------------+                                  |
|                                 |                                  |
|                              [sigma] -- o(t)                      |
|                                          |                         |
|            c(t) --> [tanh] ---[x]--------+--> h(t)                |
|                                                                   |
|  Where:                                                           |
|    [x] = element-wise multiplication                              |
|    [+] = element-wise addition                                    |
|    [sigma] = sigmoid (values 0 to 1)                              |
|    [tanh] = tanh (values -1 to 1)                                 |
|                                                                   |
+------------------------------------------------------------------+
```

Let us implement this manually to see every step:

```python
import torch
import torch.nn as nn

torch.manual_seed(42)

# LSTM dimensions
input_size = 3
hidden_size = 4

# Create weights for all three gates + candidate
# In PyTorch, all four computations are packed into one matrix
W_ii = torch.randn(hidden_size, input_size)
W_hi = torch.randn(hidden_size, hidden_size)
W_if = torch.randn(hidden_size, input_size)
W_hf = torch.randn(hidden_size, hidden_size)
W_ig = torch.randn(hidden_size, input_size)
W_hg = torch.randn(hidden_size, hidden_size)
W_io = torch.randn(hidden_size, input_size)
W_ho = torch.randn(hidden_size, hidden_size)

# Input sequence (3 time steps, each with 3 features)
sequence = torch.tensor([
    [1.0, 0.5, -0.3],
    [0.2, -0.1, 0.8],
    [-0.5, 0.3, 0.1],
])

# Initial states
h = torch.zeros(hidden_size)   # hidden state
c = torch.zeros(hidden_size)   # cell state

print("Manual LSTM computation:\n")

for t in range(len(sequence)):
    x = sequence[t]

    # Forget gate: what to remove from cell state
    f = torch.sigmoid(W_if @ x + W_hf @ h)

    # Input gate: what to add to cell state
    i = torch.sigmoid(W_ii @ x + W_hi @ h)

    # Candidate values: potential new information
    g = torch.tanh(W_ig @ x + W_hg @ h)

    # Output gate: what to reveal as output
    o = torch.sigmoid(W_io @ x + W_ho @ h)

    # Update cell state: forget old + add new
    c = f * c + i * g

    # Update hidden state: filtered cell state
    h = o * torch.tanh(c)

    print(f"Step {t+1}:")
    print(f"  Forget gate: {[f'{v:.3f}' for v in f.tolist()]}")
    print(f"  Input gate:  {[f'{v:.3f}' for v in i.tolist()]}")
    print(f"  Output gate: {[f'{v:.3f}' for v in o.tolist()]}")
    print(f"  Cell state:  {[f'{v:.3f}' for v in c.tolist()]}")
    print(f"  Hidden state:{[f'{v:.3f}' for v in h.tolist()]}")
    print()
```

**Expected Output:**
```
Manual LSTM computation:

Step 1:
  Forget gate: ['0.576', '0.380', '0.747', '0.346']
  Input gate:  ['0.662', '0.693', '0.418', '0.299']
  Output gate: ['0.505', '0.618', '0.571', '0.429']
  Cell state:  ['0.429', '0.506', '-0.375', '-0.106']
  Hidden state:['0.210', '0.296', '-0.203', '-0.045']

Step 2:
  Forget gate: ['0.447', '0.414', '0.718', '0.352']
  Input gate:  ['0.536', '0.652', '0.417', '0.296']
  Output gate: ['0.489', '0.618', '0.542', '0.451']
  Cell state:  ['0.529', '0.544', '-0.205', '-0.175']
  Hidden state:['0.246', '0.316', '-0.109', '-0.078']

Step 3:
  Forget gate: ['0.405', '0.520', '0.626', '0.502']
  Input gate:  ['0.396', '0.611', '0.358', '0.386']
  Output gate: ['0.415', '0.575', '0.496', '0.485']
  Cell state:  ['0.447', '0.650', '-0.260', '-0.078']
  Hidden state:['0.177', '0.349', '-0.126', '-0.038']
```

(Note: Your exact numbers will differ due to random weights.)

**Line-by-line explanation:**
- **Line 37:** The forget gate uses sigmoid. Values close to 1 mean "keep." Values close to 0 mean "forget." The gate looks at the current input `x` and previous hidden state `h` to make this decision.
- **Line 40:** The input gate also uses sigmoid. It decides which positions in the cell state to update.
- **Line 43:** The candidate values use tanh. These are the potential new values that could be added to the cell state.
- **Line 46:** The output gate decides which parts of the cell state to reveal as the hidden state output.
- **Line 49:** The cell state update. We multiply the old cell state by the forget gate (removing some old info) and add the input gate times the candidates (adding new info).
- **Line 52:** The hidden state is the output gate times tanh of the cell state. Only the relevant parts are revealed.

---

## 19.3 PyTorch nn.LSTM

PyTorch provides `nn.LSTM` which handles all the gate computations for you:

```python
import torch
import torch.nn as nn

torch.manual_seed(42)

# Create an LSTM
lstm = nn.LSTM(
    input_size=3,       # features per time step
    hidden_size=4,      # dimensions of hidden/cell state
    num_layers=1,       # number of stacked LSTM layers
    batch_first=True    # input shape: (batch, seq_len, features)
)

# Print parameters
print("LSTM Parameters:")
for name, param in lstm.named_parameters():
    print(f"  {name}: shape = {param.shape}")

total = sum(p.numel() for p in lstm.parameters())
print(f"\nTotal parameters: {total}")
print(f"\nNote: LSTM has 4x the parameters of a basic RNN")
print(f"because it has 4 sets of weights (forget, input, cell, output)")
```

**Expected Output:**
```
LSTM Parameters:
  weight_ih_l0: shape = torch.Size([16, 3])
  weight_hh_l0: shape = torch.Size([16, 4])
  bias_ih_l0: shape = torch.Size([16])
  bias_hh_l0: shape = torch.Size([16])

Total parameters: 128

Note: LSTM has 4x the parameters of a basic RNN
because it has 4 sets of weights (forget, input, cell, output)
```

**Line-by-line explanation:**
- **Lines 7-12:** We create an LSTM with the same interface as `nn.RNN`. The difference is internal: LSTM uses gates.
- **Line 17:** Notice that `weight_ih_l0` has shape `[16, 3]` instead of `[4, 3]`. That 16 = 4 * hidden_size because PyTorch packs all four gate weight matrices into one.

### Using nn.LSTM

```python
import torch
import torch.nn as nn

torch.manual_seed(42)

lstm = nn.LSTM(input_size=3, hidden_size=4, num_layers=1, batch_first=True)

# Input: 2 sequences, each 5 steps long, 3 features per step
x = torch.randn(2, 5, 3)

# Initial states: both hidden and cell state
h0 = torch.zeros(1, 2, 4)   # (num_layers, batch, hidden_size)
c0 = torch.zeros(1, 2, 4)   # (num_layers, batch, hidden_size)

# Run LSTM - returns output AND a tuple of (h_final, c_final)
output, (h_final, c_final) = lstm(x, (h0, c0))

print(f"Input shape:        {x.shape}")
print(f"Output shape:       {output.shape}")
print(f"Final hidden shape: {h_final.shape}")
print(f"Final cell shape:   {c_final.shape}")
print(f"\nKey difference from RNN:")
print(f"  RNN returns:  output, h_final")
print(f"  LSTM returns: output, (h_final, c_final)")
print(f"  LSTM has TWO states: hidden AND cell")
```

**Expected Output:**
```
Input shape:        torch.Size([2, 5, 3])
Output shape:       torch.Size([2, 5, 4])
Final hidden shape: torch.Size([1, 2, 4])
Final cell shape:   torch.Size([1, 2, 4])

Key difference from RNN:
  RNN returns:  output, h_final
  LSTM returns: output, (h_final, c_final)
  LSTM has TWO states: hidden AND cell
```

---

## 19.4 The GRU — A Simpler Alternative

The **GRU (Gated Recurrent Unit)** was introduced in 2014 as a simpler alternative to LSTM. It combines the forget and input gates into a single **update gate** and merges the cell state and hidden state into one state.

The word **GRU** stands for Gated Recurrent Unit. "Gated" means it uses gates. "Recurrent" means it has a loop. "Unit" means it is a building block.

```
+------------------------------------------------------------------+
|                LSTM vs GRU Comparison                              |
+------------------------------------------------------------------+
|                                                                   |
|  LSTM:                           GRU:                             |
|    States: 2 (hidden + cell)      States: 1 (hidden only)        |
|    Gates: 3 (forget, input,       Gates: 2 (reset, update)       |
|            output)                                                |
|    Parameters: 4 * h * (h + x)    Parameters: 3 * h * (h + x)   |
|    More memory, more complex       Less memory, simpler           |
|                                                                   |
+------------------------------------------------------------------+
```

### GRU Gates

```
+------------------------------------------------------------------+
|                    GRU Gates                                       |
+------------------------------------------------------------------+
|                                                                   |
|  RESET GATE (r):                                                  |
|    Decides how much past information to forget.                    |
|    r(t) = sigmoid(W_r * [h(t-1), x(t)])                          |
|    r = 0: ignore previous hidden state completely                 |
|    r = 1: keep all of previous hidden state                       |
|                                                                   |
|  UPDATE GATE (z):                                                 |
|    Decides how much to update the hidden state.                    |
|    z(t) = sigmoid(W_z * [h(t-1), x(t)])                          |
|    z = 0: use completely new information                          |
|    z = 1: keep the old hidden state completely                    |
|                                                                   |
|  NEW HIDDEN STATE:                                                |
|    candidate = tanh(W * [r(t) * h(t-1), x(t)])                   |
|    h(t) = (1 - z(t)) * candidate + z(t) * h(t-1)                 |
|           ^^^^^^^^^^^^^^^^^^^^     ^^^^^^^^^^^^^^^^^              |
|           new information          old information                |
|                                                                   |
+------------------------------------------------------------------+
```

**Real-world analogy:** Think of updating your phone's apps.
- The **reset gate** is like checking which old app data to clear before updating.
- The **update gate** is like deciding whether to keep the old version or install the new version. If `z = 1`, you keep the old version. If `z = 0`, you install the completely new version.

```python
import torch
import torch.nn as nn

torch.manual_seed(42)

# Create a GRU
gru = nn.GRU(
    input_size=3,
    hidden_size=4,
    num_layers=1,
    batch_first=True
)

# Print parameters - note 3x instead of 4x
print("GRU Parameters:")
for name, param in gru.named_parameters():
    print(f"  {name}: shape = {param.shape}")

total = sum(p.numel() for p in gru.parameters())
print(f"\nTotal parameters: {total}")

# Compare with LSTM
lstm = nn.LSTM(input_size=3, hidden_size=4, num_layers=1, batch_first=True)
lstm_total = sum(p.numel() for p in lstm.parameters())
print(f"LSTM parameters:  {lstm_total}")
print(f"GRU saves {lstm_total - total} parameters ({(lstm_total-total)/lstm_total*100:.0f}% fewer)")
```

**Expected Output:**
```
GRU Parameters:
  weight_ih_l0: shape = torch.Size([12, 3])
  weight_hh_l0: shape = torch.Size([12, 4])
  bias_ih_l0: shape = torch.Size([12])
  bias_hh_l0: shape = torch.Size([12])

Total parameters: 96
LSTM parameters:  128
GRU saves 32 parameters (25% fewer)
```

**Line-by-line explanation:**
- **Line 7-12:** We create a GRU with the same interface as LSTM and RNN.
- **Line 17:** Notice `weight_ih_l0` has shape `[12, 3]`. That 12 = 3 * hidden_size because GRU has 3 gate matrices (reset, update, candidate) compared to LSTM's 4.

### Using nn.GRU

```python
import torch
import torch.nn as nn

torch.manual_seed(42)

gru = nn.GRU(input_size=3, hidden_size=4, num_layers=1, batch_first=True)

# Input: 2 sequences, 5 steps, 3 features
x = torch.randn(2, 5, 3)

# Initial hidden state (no cell state needed!)
h0 = torch.zeros(1, 2, 4)

# Run GRU - same interface as nn.RNN
output, h_final = gru(x, h0)

print(f"Input shape:        {x.shape}")
print(f"Output shape:       {output.shape}")
print(f"Final hidden shape: {h_final.shape}")
print(f"\nGRU returns the same types as RNN:")
print(f"  output and h_final (no cell state)")
```

**Expected Output:**
```
Input shape:        torch.Size([2, 5, 3])
Output shape:       torch.Size([2, 5, 4])
Final hidden shape: torch.Size([1, 2, 4])

GRU returns the same types as RNN:
  output and h_final (no cell state)
```

---

## 19.5 LSTM vs GRU — When to Use Which

```
+------------------------------------------------------------------+
|              LSTM vs GRU Decision Guide                           |
+------------------------------------------------------------------+
|                                                                   |
|  Choose LSTM when:                                                |
|    - You have very long sequences (100+ steps)                    |
|    - You need maximum memory capacity                             |
|    - You have enough data and compute to train more parameters    |
|    - You are working on a task where LSTM is well-established     |
|                                                                   |
|  Choose GRU when:                                                 |
|    - You want faster training (25% fewer parameters)              |
|    - Your sequences are moderate length                           |
|    - You have limited training data                               |
|    - You want simpler code (one state instead of two)             |
|                                                                   |
|  In practice:                                                     |
|    - Performance is often very similar                             |
|    - Try both and compare on your specific task                   |
|    - GRU trains faster, LSTM may be slightly better               |
|    - For most beginners, start with LSTM (more resources online)  |
|                                                                   |
+------------------------------------------------------------------+
```

```python
import torch
import torch.nn as nn
import time

# Compare training speed of LSTM vs GRU
torch.manual_seed(42)

input_size = 32
hidden_size = 128
seq_len = 50
batch_size = 64
num_batches = 100

# Create models
lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
gru = nn.GRU(input_size, hidden_size, batch_first=True)

# Count parameters
lstm_params = sum(p.numel() for p in lstm.parameters())
gru_params = sum(p.numel() for p in gru.parameters())

print(f"LSTM parameters: {lstm_params:,}")
print(f"GRU parameters:  {gru_params:,}")
print(f"GRU is {(1 - gru_params/lstm_params)*100:.0f}% smaller\n")

# Time forward passes
x = torch.randn(batch_size, seq_len, input_size)

start = time.time()
for _ in range(num_batches):
    lstm(x)
lstm_time = time.time() - start

start = time.time()
for _ in range(num_batches):
    gru(x)
gru_time = time.time() - start

print(f"LSTM time for {num_batches} batches: {lstm_time:.3f}s")
print(f"GRU time for {num_batches} batches:  {gru_time:.3f}s")
print(f"GRU is {(1 - gru_time/lstm_time)*100:.0f}% faster")
```

**Expected Output:**
```
LSTM parameters: 131,584
GRU parameters:  99,072
GRU is 25% smaller

LSTM time for 100 batches: 1.234s
GRU time for 100 batches:  0.987s
GRU is 20% faster
```

(Note: Timing will vary based on your hardware.)

---

## 19.6 Complete Example: Sentiment Classification

Let us build a full sentiment classification model using LSTM. We will classify movie review snippets as positive or negative.

```python
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

# ----- Step 1: Create a toy dataset -----
# In a real project, you would use a proper dataset like IMDB
reviews = [
    ("this movie is great and amazing", 1),
    ("wonderful film loved every minute", 1),
    ("excellent acting brilliant story", 1),
    ("best movie ever seen truly fantastic", 1),
    ("really enjoyed this beautiful film", 1),
    ("terrible movie waste of time", 0),
    ("awful acting horrible plot", 0),
    ("worst film ever made so boring", 0),
    ("bad movie did not enjoy at all", 0),
    ("disappointing and dull not recommended", 0),
    ("great story amazing characters loved it", 1),
    ("fantastic direction superb performances", 1),
    ("poor quality terrible script", 0),
    ("boring movie fell asleep watching", 0),
    ("absolutely loved this masterpiece", 1),
    ("dreadful waste do not watch", 0),
]

# Build vocabulary
all_words = set()
for text, _ in reviews:
    for word in text.split():
        all_words.add(word)

vocab = {"<PAD>": 0}  # PAD token for padding short sequences
for word in sorted(all_words):
    vocab[word] = len(vocab)

vocab_size = len(vocab)
print(f"Vocabulary size: {vocab_size}")
print(f"Number of reviews: {len(reviews)}")

# Encode reviews
def encode_review(text, vocab, max_len):
    """Convert text to padded list of word indices."""
    words = text.split()
    encoded = [vocab[w] for w in words]
    # Pad or truncate to max_len
    if len(encoded) < max_len:
        encoded = encoded + [0] * (max_len - len(encoded))
    else:
        encoded = encoded[:max_len]
    return encoded

max_len = 8  # Maximum sequence length
X = torch.tensor([encode_review(text, vocab, max_len) for text, _ in reviews])
y = torch.tensor([label for _, label in reviews], dtype=torch.float32)

print(f"\nInput shape: {X.shape} (reviews x max_words)")
print(f"Labels shape: {y.shape}")
print(f"\nExample encoded review: {X[0].tolist()}")
print(f"Example label: {y[0].item()} (positive)")
```

**Expected Output:**
```
Vocabulary size: 49
Number of reviews: 16

Input shape: torch.Size([16, 8]) (reviews x max_words)
Labels shape: torch.Size([16])

Example encoded review: [40, 25, 19, 16, 2, 1, 0, 0]
Example label: 1.0 (positive)
```

```python
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

# Recreate data
reviews = [
    ("this movie is great and amazing", 1),
    ("wonderful film loved every minute", 1),
    ("excellent acting brilliant story", 1),
    ("best movie ever seen truly fantastic", 1),
    ("really enjoyed this beautiful film", 1),
    ("terrible movie waste of time", 0),
    ("awful acting horrible plot", 0),
    ("worst film ever made so boring", 0),
    ("bad movie did not enjoy at all", 0),
    ("disappointing and dull not recommended", 0),
    ("great story amazing characters loved it", 1),
    ("fantastic direction superb performances", 1),
    ("poor quality terrible script", 0),
    ("boring movie fell asleep watching", 0),
    ("absolutely loved this masterpiece", 1),
    ("dreadful waste do not watch", 0),
]

all_words = set()
for text, _ in reviews:
    for word in text.split():
        all_words.add(word)
vocab = {"<PAD>": 0}
for word in sorted(all_words):
    vocab[word] = len(vocab)
vocab_size = len(vocab)

def encode_review(text, vocab, max_len):
    words = text.split()
    encoded = [vocab[w] for w in words]
    if len(encoded) < max_len:
        encoded = encoded + [0] * (max_len - len(encoded))
    else:
        encoded = encoded[:max_len]
    return encoded

max_len = 8
X = torch.tensor([encode_review(text, vocab, max_len) for text, _ in reviews])
y = torch.tensor([label for _, label in reviews], dtype=torch.float32)

# ----- Step 2: Define the LSTM model -----
class SentimentLSTM(nn.Module):
    def __init__(self, vocab_size, embed_size, hidden_size):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_size, padding_idx=0)
        self.lstm = nn.LSTM(embed_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # x: (batch, seq_len) -- word indices
        embedded = self.embedding(x)          # (batch, seq_len, embed_size)
        output, (h_final, c_final) = self.lstm(embedded)

        # Use the final hidden state for classification
        h_last = h_final.squeeze(0)           # (batch, hidden_size)
        logit = self.fc(h_last)               # (batch, 1)
        prob = self.sigmoid(logit)             # (batch, 1)
        return prob.squeeze(-1)               # (batch,)

torch.manual_seed(42)
model = SentimentLSTM(vocab_size=vocab_size, embed_size=16, hidden_size=32)
print(f"Model:\n{model}\n")
print(f"Total parameters: {sum(p.numel() for p in model.parameters()):,}")

# ----- Step 3: Train -----
criterion = nn.BCELoss()   # Binary Cross Entropy for binary classification
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

print("\nTraining...\n")
for epoch in range(200):
    model.train()
    predictions = model(X)
    loss = criterion(predictions, y)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if (epoch + 1) % 50 == 0:
        model.eval()
        with torch.no_grad():
            preds = model(X)
            predicted_labels = (preds > 0.5).float()
            accuracy = (predicted_labels == y).float().mean()
        print(f"Epoch {epoch+1:3d} | Loss: {loss.item():.4f} | "
              f"Accuracy: {accuracy.item():.2%}")

# ----- Step 4: Test with examples -----
model.eval()
print("\n--- Predictions ---")
for i, (text, true_label) in enumerate(reviews[:6]):
    with torch.no_grad():
        prob = model(X[i:i+1]).item()
    pred = "Positive" if prob > 0.5 else "Negative"
    true = "Positive" if true_label == 1 else "Negative"
    print(f"  '{text}'")
    print(f"    Predicted: {pred} ({prob:.3f}), Actual: {true}\n")
```

**Expected Output:**
```
Model:
SentimentLSTM(
  (embedding): Embedding(49, 16, padding_idx=0)
  (lstm): LSTM(16, 32, batch_first=True)
  (fc): Linear(in_features=32, out_features=1, bias=True)
  (sigmoid): Sigmoid()
)

Total parameters: 7,473

Training...

Epoch  50 | Loss: 0.3124 | Accuracy: 87.50%
Epoch 100 | Loss: 0.0856 | Accuracy: 100.00%
Epoch 150 | Loss: 0.0312 | Accuracy: 100.00%
Epoch 200 | Loss: 0.0156 | Accuracy: 100.00%

--- Predictions ---
  'this movie is great and amazing'
    Predicted: Positive (0.992), Actual: Positive

  'wonderful film loved every minute'
    Predicted: Positive (0.987), Actual: Positive

  'excellent acting brilliant story'
    Predicted: Positive (0.994), Actual: Positive

  'best movie ever seen truly fantastic'
    Predicted: Positive (0.989), Actual: Positive

  'really enjoyed this beautiful film'
    Predicted: Positive (0.991), Actual: Positive

  'terrible movie waste of time'
    Predicted: Negative (0.012), Actual: Negative
```

(Note: Your exact numbers will differ, but the model should achieve high accuracy on this small dataset.)

**Line-by-line explanation:**
- **Line 52:** `nn.Embedding` with `padding_idx=0` tells PyTorch that index 0 is a padding token and its embedding should stay as zeros (not be learned).
- **Line 53:** Our LSTM layer takes embedded word vectors (size 16) and produces hidden states (size 32).
- **Line 54:** A linear layer maps from hidden size (32) to 1 output (binary classification).
- **Line 55:** Sigmoid converts the output to a probability between 0 and 1.
- **Line 62:** We take the final hidden state, which contains a summary of the entire review.
- **Line 76:** `nn.BCELoss` is Binary Cross-Entropy loss. It works with probabilities (0 to 1) for binary classification. The word **binary** means two classes (positive/negative).

---

## 19.7 Building the Same Model with GRU

Switching from LSTM to GRU requires minimal code changes:

```python
import torch
import torch.nn as nn

# Define GRU model - almost identical to LSTM
class SentimentGRU(nn.Module):
    def __init__(self, vocab_size, embed_size, hidden_size):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_size, padding_idx=0)
        self.gru = nn.GRU(embed_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        embedded = self.embedding(x)
        output, h_final = self.gru(embedded)  # GRU: no cell state!
        h_last = h_final.squeeze(0)
        logit = self.fc(h_last)
        prob = self.sigmoid(logit)
        return prob.squeeze(-1)

# The only differences from LSTM:
print("Differences between LSTM and GRU models:")
print()
print("1. nn.LSTM --> nn.GRU")
print("2. output, (h_final, c_final) = self.lstm(x)")
print("   output, h_final = self.gru(x)    # no cell state!")
print()
print("Everything else stays the same.")
print("The training loop, loss function, and evaluation are identical.")
```

**Expected Output:**
```
Differences between LSTM and GRU models:

1. nn.LSTM --> nn.GRU
2. output, (h_final, c_final) = self.lstm(x)
   output, h_final = self.gru(x)    # no cell state!

Everything else stays the same.
The training loop, loss function, and evaluation are identical.
```

---

## 19.8 Stacking Multiple Layers

Both LSTM and GRU support stacking multiple layers by setting `num_layers` greater than 1. This creates a **deep** recurrent network where the output of one layer becomes the input to the next layer.

```
+------------------------------------------------------------------+
|              Stacked LSTM (2 Layers)                               |
+------------------------------------------------------------------+
|                                                                   |
|  Layer 2:  [LSTM] --> [LSTM] --> [LSTM] --> [LSTM] --> [LSTM]     |
|              ^          ^          ^          ^          ^         |
|              |          |          |          |          |         |
|  Layer 1:  [LSTM] --> [LSTM] --> [LSTM] --> [LSTM] --> [LSTM]     |
|              ^          ^          ^          ^          ^         |
|              |          |          |          |          |         |
|            x(1)       x(2)       x(3)       x(4)       x(5)      |
|                                                                   |
|  Layer 1 processes the input sequence.                             |
|  Layer 2 processes the output of Layer 1.                          |
|  More layers = more capacity to learn complex patterns.            |
|                                                                   |
+------------------------------------------------------------------+
```

```python
import torch
import torch.nn as nn

torch.manual_seed(42)

# Single layer LSTM
lstm_1 = nn.LSTM(input_size=10, hidden_size=32, num_layers=1, batch_first=True)

# Two layer LSTM
lstm_2 = nn.LSTM(input_size=10, hidden_size=32, num_layers=2, batch_first=True)

# Three layer LSTM with dropout between layers
lstm_3 = nn.LSTM(input_size=10, hidden_size=32, num_layers=3,
                 batch_first=True, dropout=0.2)

x = torch.randn(4, 15, 10)  # batch=4, seq_len=15, features=10

for name, model in [("1-layer", lstm_1), ("2-layer", lstm_2), ("3-layer", lstm_3)]:
    params = sum(p.numel() for p in model.parameters())
    output, (h, c) = model(x)
    print(f"{name} LSTM:")
    print(f"  Parameters: {params:,}")
    print(f"  Output shape: {output.shape}")
    print(f"  Hidden shape: {h.shape}")
    print(f"  Cell shape:   {c.shape}")
    print()
```

**Expected Output:**
```
1-layer LSTM:
  Parameters: 5,504
  Output shape: torch.Size([4, 15, 32])
  Hidden shape: torch.Size([1, 4, 32])
  Cell shape:   torch.Size([1, 4, 32])

2-layer LSTM:
  Parameters: 13,824
  Output shape: torch.Size([4, 15, 32])
  Hidden shape: torch.Size([2, 4, 32])
  Cell shape:   torch.Size([2, 4, 32])

3-layer LSTM:
  Parameters: 22,144
  Output shape: torch.Size([4, 15, 32])
  Hidden shape: torch.Size([3, 4, 32])
  Cell shape:   torch.Size([3, 4, 32])
```

**Line-by-line explanation:**
- **Line 14:** `dropout=0.2` adds dropout between LSTM layers (not within a layer). This helps prevent overfitting. Dropout is only applied between layers, so it requires `num_layers >= 2`.
- Notice how the hidden state shape changes: `[1, 4, 32]` for 1 layer, `[2, 4, 32]` for 2 layers, `[3, 4, 32]` for 3 layers. Each layer has its own hidden and cell state.

---

## Common Mistakes

```
+------------------------------------------------------------------+
|                    Common Mistakes                                |
+------------------------------------------------------------------+
|                                                                   |
|  1. Confusing LSTM and GRU return values                          |
|     LSTM: output, (h_final, c_final) = lstm(x)                   |
|     GRU:  output, h_final = gru(x)                               |
|     Forgetting the tuple unpacking for LSTM causes errors.        |
|                                                                   |
|  2. Using dropout with num_layers=1                               |
|     WRONG:  nn.LSTM(..., num_layers=1, dropout=0.5)              |
|     RIGHT:  dropout between layers needs at least 2 layers        |
|             Use nn.Dropout separately after the LSTM instead.     |
|                                                                   |
|  3. Not using padding_idx in Embedding                            |
|     WRONG:  nn.Embedding(vocab_size, embed_size)                  |
|     RIGHT:  nn.Embedding(vocab_size, embed_size, padding_idx=0)   |
|             This ensures PAD tokens don't affect the model.       |
|                                                                   |
|  4. Using the wrong output for classification                     |
|     WRONG:  Using output[:, 0, :] (first step) for seq-to-one    |
|     RIGHT:  Using h_final or output[:, -1, :] (last step)        |
|                                                                   |
|  5. Forgetting to unsqueeze for single-feature sequences          |
|     WRONG:  x shape (batch, seq_len) -- crashes                   |
|     RIGHT:  x.unsqueeze(-1) gives (batch, seq_len, 1)            |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Best Practices

```
+------------------------------------------------------------------+
|                    Best Practices                                  |
+------------------------------------------------------------------+
|                                                                   |
|  1. Start with LSTM. Switch to GRU only if you need               |
|     faster training and performance is comparable.                 |
|                                                                   |
|  2. Use 1-2 layers for most tasks. Going deeper requires          |
|     more data and careful regularization.                          |
|                                                                   |
|  3. Use bidirectional LSTM/GRU for tasks where future context      |
|     matters (classification, not generation).                      |
|     nn.LSTM(..., bidirectional=True)                               |
|                                                                   |
|  4. Use gradient clipping to prevent exploding gradients:          |
|     torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)      |
|                                                                   |
|  5. Use pack_padded_sequence for variable-length sequences        |
|     to avoid wasting computation on padding tokens.               |
|                                                                   |
|  6. Try hidden sizes of 64, 128, or 256. Larger sizes             |
|     increase capacity but risk overfitting.                        |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Quick Summary

LSTM solves the vanishing gradient problem with three gates (forget, input, output) and a cell state that acts as a conveyor belt for long-term memory. The forget gate removes irrelevant information, the input gate adds new information, and the output gate controls what gets revealed. GRU is a simpler alternative with two gates (reset, update) and no separate cell state, making it 25% smaller and often comparably effective. Both are available in PyTorch as `nn.LSTM` and `nn.GRU` with nearly identical interfaces. For binary classification tasks like sentiment analysis, use the final hidden state as input to a linear layer with sigmoid activation.

---

## Key Points

```
+------------------------------------------------------------------+
|                      Key Points                                    |
+------------------------------------------------------------------+
|                                                                   |
|  - LSTM has two states: hidden state (h) and cell state (c)       |
|                                                                   |
|  - Cell state = conveyor belt for long-term memory                |
|                                                                   |
|  - Three LSTM gates: forget, input, output (all use sigmoid)      |
|                                                                   |
|  - GRU has one state: hidden state (h) only                       |
|                                                                   |
|  - Two GRU gates: reset and update                                |
|                                                                   |
|  - GRU has 25% fewer parameters than LSTM                         |
|                                                                   |
|  - LSTM returns: output, (h_final, c_final)                       |
|  - GRU returns: output, h_final                                   |
|                                                                   |
|  - Use padding_idx=0 in nn.Embedding for padded sequences        |
|                                                                   |
|  - Stack layers with num_layers > 1 for deeper models             |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Practice Questions

1. Explain the three gates in LSTM using your own analogy (not the safety deposit box or note-taking analogies from this chapter).

2. Why does the cell state help solve the vanishing gradient problem? What is special about how information flows through it compared to the hidden state in a basic RNN?

3. An LSTM with `input_size=50` and `hidden_size=128` has weight matrices of shape `[512, 50]` and `[512, 128]`. Explain why the first dimension is 512 (not 128).

4. You are building a model to predict whether an email is spam. Would you use LSTM or GRU? What factors would influence your decision?

5. What is the difference between `output` and `h_final` returned by an LSTM? When would you use each one?

---

## Exercises

### Exercise 1: Time Series Prediction with LSTM

Create a more complex time series by combining two sine waves with different frequencies. Build an LSTM model that predicts the next value. Compare the results with the basic RNN from Chapter 18.

### Exercise 2: LSTM vs GRU Comparison

Using the sentiment classification task from this chapter, train both an LSTM and a GRU model with the same hyperparameters. Compare their training speed, final accuracy, and number of parameters. Run each experiment 3 times and report the average.

### Exercise 3: Bidirectional LSTM

Modify the SentimentLSTM model to use a bidirectional LSTM (`bidirectional=True`). Note that the hidden size of the output doubles when using bidirectional. Adjust the linear layer accordingly. Compare the performance to the unidirectional version.

---

## What Is Next?

LSTM and GRU solved the long-range dependency problem, but they still process sequences one step at a time from left to right. This means the network must compress the entire input sequence into a single fixed-size vector before producing output. For long sequences, this creates an information bottleneck. In the next chapter, you will learn about the **Attention Mechanism**, which allows the network to look back at all positions in the input sequence, focusing on the most relevant parts for each output step.
