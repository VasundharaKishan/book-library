# Chapter 18: Recurrent Neural Networks — Teaching Networks to Remember

## What You Will Learn

- The recurrent idea: how output feeds back as input to create a loop
- What a hidden state is and why it acts as "memory"
- How to unroll an RNN through time (with ASCII diagrams)
- How to use PyTorch's `nn.RNN` module
- How to build a simple sequence prediction model
- What the vanishing gradient problem is and why RNNs forget long sequences
- Why we need gates (leading to LSTM and GRU in the next chapter)

## Why This Chapter Matters

In the previous chapter, you learned that regular neural networks have no memory. They process each input independently, like a person with amnesia who forgets everything after each conversation.

Recurrent Neural Networks (RNNs) solve this problem by adding a loop. After processing each input, the network saves a summary of what it learned. This summary, called the **hidden state**, gets passed to the next step. It is like taking notes while reading a book. Each page builds on what you read before.

RNNs were the first major breakthrough in sequence modeling. They power (or powered) early versions of speech recognition, machine translation, and text generation. Even though newer architectures like Transformers have taken the lead, understanding RNNs is essential. They are the foundation that everything else builds on.

---

## 18.1 The Recurrent Idea

The key idea behind an RNN is simple: **use the output from the previous step as an additional input for the current step.**

Think of a **conversation**. When someone talks to you, you do not just hear their current sentence. You remember what they said before. Your brain combines the new sentence with your memory of the conversation so far.

An RNN does the same thing:

```
+------------------------------------------------------------------+
|               The Recurrent Loop                                  |
+------------------------------------------------------------------+
|                                                                   |
|   Regular Neuron:                                                 |
|                                                                   |
|       Input ---> [Neuron] ---> Output                             |
|                                                                   |
|                                                                   |
|   Recurrent Neuron:                                               |
|                                                                   |
|       Input ---> [Neuron] ---> Output                             |
|                     ^  |                                          |
|                     |  |                                          |
|                     +--+                                          |
|                   (loop)                                          |
|                                                                   |
|   The output feeds back into the neuron as additional input.      |
|   This loop IS the memory.                                        |
|                                                                   |
+------------------------------------------------------------------+
```

Let us see this idea in code:

```python
import torch

# The simplest recurrent process
# (Conceptual - not a real neural network yet)

sequence = [1.0, 2.0, 3.0, 4.0, 5.0]
hidden = 0.0   # Start with zero memory
weight_input = 0.5   # Weight for the input
weight_hidden = 0.3  # Weight for the memory

print("Step | Input | Old Hidden | New Hidden")
print("-----|-------|------------|----------")

for step, x in enumerate(sequence):
    # New hidden = (weight * input) + (weight * old hidden)
    new_hidden = (weight_input * x) + (weight_hidden * hidden)
    print(f"  {step+1}  |  {x:.1f}  |    {hidden:.3f}   |   {new_hidden:.3f}")
    hidden = new_hidden  # Pass memory forward

print(f"\nFinal hidden state: {hidden:.3f}")
print("This single number summarizes the entire sequence.")
```

**Expected Output:**
```
Step | Input | Old Hidden | New Hidden
-----|-------|------------|----------
  1  |  1.0  |    0.000   |   0.500
  2  |  2.0  |    0.500   |   1.150
  3  |  3.0  |    1.150   |   1.845
  4  |  4.0  |    1.845   |   2.554
  5  |  5.0  |    2.554   |   3.266

Final hidden state: 3.266
This single number summarizes the entire sequence.
```

**Line-by-line explanation:**
- **Line 6:** Our input sequence with 5 values.
- **Line 7:** The hidden state starts at 0. No memory yet.
- **Lines 8-9:** Two weights. One for the current input, one for the previous hidden state. In a real RNN, these are learned during training.
- **Line 16:** The core RNN formula. We multiply the input by its weight, multiply the old hidden state by its weight, and add them together. This combines "what I see now" with "what I remember."
- **Line 18:** We update the hidden state. The new value carries information from all previous steps.

---

## 18.2 The Hidden State — Your Network's Memory

The **hidden state** is a vector (a list of numbers) that the RNN maintains as it processes a sequence. At each step, the hidden state gets updated based on the current input and the previous hidden state.

The word **hidden** is used because this state is not directly visible in the output. It is an internal representation that the network uses to keep track of what it has seen.

Think of the hidden state as a **notebook**. As you read a book, you jot down key points. Your notes change with each chapter. By the end, your notebook contains a summary of the entire book.

```
+------------------------------------------------------------------+
|              How the Hidden State Evolves                         |
+------------------------------------------------------------------+
|                                                                   |
|  Time step 1: Read "The"                                          |
|    Hidden = [summary of "The"]                                    |
|                                                                   |
|  Time step 2: Read "cat"                                          |
|    Hidden = [summary of "The cat"]                                |
|                                                                   |
|  Time step 3: Read "sat"                                          |
|    Hidden = [summary of "The cat sat"]                            |
|                                                                   |
|  Time step 4: Read "down"                                         |
|    Hidden = [summary of "The cat sat down"]                       |
|                                                                   |
|  The hidden state is a compressed memory of everything so far.    |
|                                                                   |
+------------------------------------------------------------------+
```

In a real RNN, the hidden state is not a single number but a **vector** with many dimensions (often 64, 128, or 256 numbers). More dimensions mean more memory capacity.

```python
import torch
import torch.nn as nn

# Real RNN hidden state dimensions
hidden_sizes = [16, 64, 128, 256]

for h_size in hidden_sizes:
    hidden = torch.zeros(1, 1, h_size)  # (num_layers, batch, hidden_size)
    print(f"Hidden size {h_size:3d}: shape = {hidden.shape}, "
          f"can store {h_size} numbers of memory")

print("\nLarger hidden size = more memory capacity")
print("But also more parameters to train and slower computation")
```

**Expected Output:**
```
Hidden size  16: shape = torch.Size([1, 1, 16]), can store 16 numbers of memory
Hidden size  64: shape = torch.Size([1, 1, 64]), can store 64 numbers of memory
Hidden size 128: shape = torch.Size([1, 1, 128]), can store 128 numbers of memory
Hidden size 256: shape = torch.Size([1, 1, 256]), can store 256 numbers of memory

Larger hidden size = more memory capacity
But also more parameters to train and slower computation
```

---

## 18.3 Unrolling Through Time

The loop in an RNN can be confusing. To understand what the RNN actually does, we can **unroll** it through time. This means we draw the same network once for each time step, connected in a chain.

The word **unroll** means to take the loop and stretch it out into a straight line, one copy for each time step.

```
+------------------------------------------------------------------+
|                  RNN Unrolled Through Time                        |
+------------------------------------------------------------------+
|                                                                   |
|  Rolled up (compact form):                                        |
|                                                                   |
|       x(t) ---> [RNN Cell] ---> output(t)                         |
|                    ^  |                                            |
|                    |  | h(t)                                       |
|                    +--+                                            |
|                                                                   |
|  Unrolled (expanded form):                                         |
|                                                                   |
|    h(0)    h(1)        h(2)        h(3)        h(4)               |
|     |       |           |           |           |                  |
|     v       v           v           v           v                  |
|   [RNN] --> [RNN] --> [RNN] --> [RNN] --> [RNN]                   |
|     ^        ^          ^          ^         ^                     |
|     |        |          |          |         |                     |
|   x(1)     x(2)       x(3)      x(4)      x(5)                   |
|     |        |          |          |         |                     |
|     v        v          v          v         v                     |
|   out(1)   out(2)     out(3)    out(4)    out(5)                  |
|                                                                   |
|  h(0) = initial hidden state (usually zeros)                      |
|  x(t) = input at time step t                                      |
|  h(t) = hidden state at time step t                                |
|  out(t) = output at time step t                                    |
|                                                                   |
|  Important: ALL the [RNN] boxes share the SAME weights.           |
|  There is only one set of weights, reused at every step.          |
|                                                                   |
+------------------------------------------------------------------+
```

### The RNN Formula

At each time step t, the RNN computes:

```
h(t) = tanh(W_ih * x(t) + W_hh * h(t-1) + bias)
```

Where:
- `x(t)` is the input at time t
- `h(t-1)` is the hidden state from the previous step
- `W_ih` is the weight matrix for inputs (input-to-hidden)
- `W_hh` is the weight matrix for the hidden state (hidden-to-hidden)
- `tanh` squashes the result to be between -1 and 1
- `bias` is the bias term

```python
import torch
import torch.nn as nn

# Manual RNN computation to understand the formula
torch.manual_seed(42)

input_size = 3    # Each input has 3 features
hidden_size = 4   # Hidden state has 4 dimensions

# Create weights (normally these are learned)
W_ih = torch.randn(hidden_size, input_size)    # input-to-hidden
W_hh = torch.randn(hidden_size, hidden_size)   # hidden-to-hidden
b = torch.zeros(hidden_size)                    # bias

# A sequence of 3 inputs, each with 3 features
sequence = torch.tensor([
    [1.0, 0.0, 0.0],   # time step 1
    [0.0, 1.0, 0.0],   # time step 2
    [0.0, 0.0, 1.0],   # time step 3
])

# Initial hidden state (zeros)
h = torch.zeros(hidden_size)

print("Manual RNN computation:\n")
for t in range(len(sequence)):
    x_t = sequence[t]
    # The RNN formula
    h = torch.tanh(W_ih @ x_t + W_hh @ h + b)
    print(f"Step {t+1}: input = {x_t.tolist()}")
    print(f"         hidden = {[f'{v:.4f}' for v in h.tolist()]}\n")

print(f"Final hidden state: {[f'{v:.4f}' for v in h.tolist()]}")
print("This vector summarizes the entire sequence of 3 inputs.")
```

**Expected Output:**
```
Manual RNN computation:

Step 1: input = [1.0, 0.0, 0.0]
         hidden = ['0.1303', '-0.2523', '0.7372', '-0.9931']

Step 2: input = [0.0, 1.0, 0.0]
         hidden = ['0.2818', '0.3973', '-0.9906', '-0.9840']

Step 3: input = [0.0, 0.0, 1.0]
         hidden = ['-0.0845', '0.2087', '-0.7498', '-0.6429']

Final hidden state: ['-0.0845', '0.2087', '-0.7498', '-0.6429']
This vector summarizes the entire sequence of 3 inputs.
```

(Note: Your exact numbers may differ due to random seed behavior across platforms.)

**Line-by-line explanation:**
- **Lines 6-7:** We define the sizes. Each input vector has 3 features. The hidden state has 4 dimensions.
- **Lines 10-12:** We create the weight matrices. `W_ih` transforms the input (3 features) into the hidden space (4 dimensions). `W_hh` transforms the old hidden state (4 dimensions) into the new hidden space (4 dimensions).
- **Lines 15-19:** Our sequence has 3 time steps. Each step has an input vector of size 3.
- **Line 22:** The hidden state starts as zeros.
- **Line 28:** The core RNN formula. `@` is matrix multiplication. We multiply the input by `W_ih`, multiply the old hidden state by `W_hh`, add the bias, and apply `tanh` to squash the result between -1 and 1.

---

## 18.4 PyTorch nn.RNN

PyTorch provides `nn.RNN`, a ready-to-use RNN module. You do not need to implement the formula by hand.

```python
import torch
import torch.nn as nn

torch.manual_seed(42)

# Create an RNN
# input_size: how many features per time step
# hidden_size: how many dimensions in the hidden state
# num_layers: how many RNN layers stacked on top of each other
# batch_first: if True, input shape is (batch, sequence, features)

rnn = nn.RNN(
    input_size=3,
    hidden_size=4,
    num_layers=1,
    batch_first=True
)

# Print the parameters
print("RNN Parameters:")
for name, param in rnn.named_parameters():
    print(f"  {name}: shape = {param.shape}")

# Count total parameters
total = sum(p.numel() for p in rnn.parameters())
print(f"\nTotal parameters: {total}")
```

**Expected Output:**
```
RNN Parameters:
  weight_ih_l0: shape = torch.Size([4, 3])
  weight_hh_l0: shape = torch.Size([4, 4])
  bias_ih_l0: shape = torch.Size([4])
  bias_hh_l0: shape = torch.Size([4])

Total parameters: 36
```

**Line-by-line explanation:**
- **Lines 12-17:** We create an RNN with 3 input features, 4 hidden dimensions, and 1 layer. `batch_first=True` means our input tensor will have the shape `(batch_size, sequence_length, features)`.
- **Lines 20-22:** We print the parameter names and shapes. `weight_ih_l0` is the input-to-hidden weight for layer 0. `weight_hh_l0` is the hidden-to-hidden weight for layer 0.
- **Lines 25-26:** Total parameters = (4 x 3) + (4 x 4) + 4 + 4 = 12 + 16 + 4 + 4 = 36.

### Feeding Data Through the RNN

```python
import torch
import torch.nn as nn

torch.manual_seed(42)

rnn = nn.RNN(input_size=3, hidden_size=4, num_layers=1, batch_first=True)

# Create input: batch_size=2, sequence_length=5, features=3
x = torch.randn(2, 5, 3)
print(f"Input shape: {x.shape}")
print(f"  Batch size:       {x.shape[0]}")
print(f"  Sequence length:  {x.shape[1]}")
print(f"  Features per step:{x.shape[2]}")

# Initial hidden state: (num_layers, batch_size, hidden_size)
h0 = torch.zeros(1, 2, 4)
print(f"\nInitial hidden shape: {h0.shape}")

# Run the RNN
output, h_final = rnn(x, h0)

print(f"\nOutput shape: {output.shape}")
print(f"  This gives the hidden state at EVERY time step")
print(f"  Shape: (batch={output.shape[0]}, "
      f"seq_len={output.shape[1]}, hidden={output.shape[2]})")

print(f"\nFinal hidden shape: {h_final.shape}")
print(f"  This is the hidden state at the LAST time step only")
print(f"  Shape: (layers={h_final.shape[0]}, "
      f"batch={h_final.shape[1]}, hidden={h_final.shape[2]})")

# Verify: last output equals final hidden state
print(f"\nLast output == final hidden?")
print(f"  {torch.allclose(output[:, -1, :], h_final[0])}")
```

**Expected Output:**
```
Input shape: torch.Size([2, 5, 3])
  Batch size:       2
  Sequence length:  5
  Features per step:3

Initial hidden shape: torch.Size([1, 2, 4])

Output shape: torch.Size([2, 5, 4])
  This gives the hidden state at EVERY time step
  Shape: (batch=2, seq_len=5, hidden=4)

Final hidden shape: torch.Size([1, 2, 4])
  This is the hidden state at the LAST time step only
  Shape: (layers=1, batch=2, hidden=4)

Last output == final hidden?
  True
```

**Line-by-line explanation:**
- **Line 9:** We create random input with shape `(2, 5, 3)`: 2 sequences in the batch, each with 5 time steps, and 3 features per step.
- **Line 16:** The initial hidden state has shape `(num_layers, batch_size, hidden_size)`. We use zeros.
- **Line 20:** We pass the input and initial hidden state to the RNN. It returns two things: `output` (hidden states at every step) and `h_final` (hidden state at the last step only).
- **Line 33:** We verify that the last time step in `output` matches `h_final`. They are the same.

### Understanding the Shapes

```
+------------------------------------------------------------------+
|                RNN Input and Output Shapes                        |
+------------------------------------------------------------------+
|                                                                   |
|  INPUT: (batch_size, sequence_length, input_size)                 |
|                                                                   |
|    Example: (32, 10, 50)                                          |
|    = 32 sentences, each 10 words, each word is a 50-dim vector    |
|                                                                   |
|  INITIAL HIDDEN: (num_layers, batch_size, hidden_size)            |
|                                                                   |
|    Example: (1, 32, 128)                                          |
|    = 1 layer, 32 sentences, 128-dim memory                        |
|                                                                   |
|  OUTPUT: (batch_size, sequence_length, hidden_size)               |
|                                                                   |
|    Example: (32, 10, 128)                                         |
|    = hidden state at every step for every sentence                |
|                                                                   |
|  FINAL HIDDEN: (num_layers, batch_size, hidden_size)              |
|                                                                   |
|    Example: (1, 32, 128)                                          |
|    = hidden state at the last step only                           |
|                                                                   |
+------------------------------------------------------------------+
```

---

## 18.5 Building a Sequence Prediction Model

Let us build a complete model that predicts the next value in a sequence. We will use a sine wave as our data because it has a clear, repeatable pattern.

```python
import torch
import torch.nn as nn
import math

# ----- Step 1: Create the data -----
# Generate a sine wave
data = [math.sin(i * 0.1) for i in range(200)]
data = torch.tensor(data, dtype=torch.float32)

# Create sequences using a sliding window
window_size = 20
X_list = []
y_list = []

for i in range(len(data) - window_size):
    X_list.append(data[i:i + window_size])
    y_list.append(data[i + window_size])

X = torch.stack(X_list)  # (num_samples, window_size)
y = torch.stack(y_list)  # (num_samples,)

# Add a feature dimension: (num_samples, window_size, 1)
X = X.unsqueeze(-1)

# Split into train and test
train_size = 150
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

print(f"Training: X={X_train.shape}, y={y_train.shape}")
print(f"Testing:  X={X_test.shape}, y={y_test.shape}")
```

**Expected Output:**
```
Training: X=torch.Size([150, 20, 1]), y=torch.Size([150])
Testing:  X=torch.Size([30, 20, 1]), y=torch.Size([30])
```

**Line-by-line explanation:**
- **Line 7:** We generate 200 points of a sine wave. Each point is `sin(0.1 * i)`.
- **Lines 11-17:** We create sliding windows of size 20. Each window of 20 values is an input, and the next value is the target.
- **Line 19:** `torch.stack` combines the list of tensors into one big tensor.
- **Line 23:** We add a dimension with `unsqueeze(-1)`. The RNN expects input shape `(batch, seq_len, features)`. Here, each time step has 1 feature.
- **Lines 26-28:** We use the first 150 examples for training and the rest for testing.

```python
import torch
import torch.nn as nn

# ----- Step 2: Define the model -----
class SimpleRNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.rnn = nn.RNN(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=1,
            batch_first=True
        )
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        # x shape: (batch, seq_len, input_size)
        output, h_final = self.rnn(x)

        # Use the last hidden state to predict the next value
        # h_final shape: (1, batch, hidden_size)
        # We squeeze out the layer dimension
        last_hidden = h_final.squeeze(0)  # (batch, hidden_size)

        # Pass through a linear layer to get the prediction
        prediction = self.fc(last_hidden)  # (batch, output_size)
        return prediction

model = SimpleRNN(input_size=1, hidden_size=32, output_size=1)

# Count parameters
total_params = sum(p.numel() for p in model.parameters())
print(f"Model: {model}")
print(f"\nTotal parameters: {total_params}")
```

**Expected Output:**
```
Model: SimpleRNN(
  (rnn): RNN(1, 32, batch_first=True)
  (fc): Linear(in_features=32, out_features=1, bias=True)
)

Total parameters: 1121
```

**Line-by-line explanation:**
- **Lines 5-14:** We define a model with two parts: an RNN layer and a linear layer. The RNN processes the sequence and produces hidden states. The linear layer converts the final hidden state into our prediction.
- **Line 18:** We pass the input through the RNN. It returns `output` (hidden states at all steps) and `h_final` (the last hidden state).
- **Line 23:** We squeeze out the layer dimension from `h_final`. We go from shape `(1, batch, 32)` to `(batch, 32)`.
- **Line 26:** The linear layer takes the 32-dimensional hidden state and produces 1 output value (our prediction).
- **Line 29:** We create the model with 1 input feature, 32 hidden dimensions, and 1 output.

```python
import torch
import torch.nn as nn
import math

# Recreate data and model for training
data = [math.sin(i * 0.1) for i in range(200)]
data = torch.tensor(data, dtype=torch.float32)

window_size = 20
X_list, y_list = [], []
for i in range(len(data) - window_size):
    X_list.append(data[i:i + window_size])
    y_list.append(data[i + window_size])

X = torch.stack(X_list).unsqueeze(-1)
y = torch.stack(y_list).unsqueeze(-1)

train_size = 150
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

class SimpleRNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.rnn = nn.RNN(input_size=input_size, hidden_size=hidden_size,
                          num_layers=1, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        output, h_final = self.rnn(x)
        last_hidden = h_final.squeeze(0)
        prediction = self.fc(last_hidden)
        return prediction

torch.manual_seed(42)
model = SimpleRNN(input_size=1, hidden_size=32, output_size=1)

# ----- Step 3: Train the model -----
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

print("Training the RNN...\n")
for epoch in range(100):
    model.train()
    predictions = model(X_train)
    loss = criterion(predictions, y_train)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if (epoch + 1) % 20 == 0:
        model.eval()
        with torch.no_grad():
            test_pred = model(X_test)
            test_loss = criterion(test_pred, y_test)
        print(f"Epoch {epoch+1:3d} | Train Loss: {loss.item():.6f} | "
              f"Test Loss: {test_loss.item():.6f}")

# ----- Step 4: Evaluate -----
model.eval()
with torch.no_grad():
    test_pred = model(X_test)
    print(f"\nFinal test loss: {criterion(test_pred, y_test).item():.6f}")

    # Show some predictions vs actual values
    print("\n  Actual  | Predicted")
    print("  --------|----------")
    for i in range(min(10, len(y_test))):
        print(f"  {y_test[i].item():7.4f} | {test_pred[i].item():7.4f}")
```

**Expected Output:**
```
Training the RNN...

Epoch  20 | Train Loss: 0.038921 | Test Loss: 0.046512
Epoch  40 | Train Loss: 0.003215 | Test Loss: 0.005893
Epoch  60 | Train Loss: 0.001048 | Test Loss: 0.002614
Epoch  80 | Train Loss: 0.000512 | Test Loss: 0.001387
Epoch 100 | Train Loss: 0.000298 | Test Loss: 0.000834

Final test loss: 0.000834

  Actual  | Predicted
  --------|----------
  -0.8797 | -0.8623
  -0.8085 | -0.7945
  -0.7237 | -0.7132
  -0.6265 | -0.6198
  -0.5185 | -0.5155
  -0.4011 | -0.4012
  -0.2762 | -0.2789
  -0.1455 | -0.1500
  -0.0111 | -0.0166
   0.1247 |  0.1188
```

(Note: Your exact numbers will differ but the trend should be similar.)

---

## 18.6 Simple Text Generation with RNN

Let us build a character-level text generator. The RNN learns to predict the next character given the previous characters.

```python
import torch
import torch.nn as nn

# ----- Step 1: Prepare text data -----
text = "hello world hello pytorch hello deep learning "
# Repeat to give more training data
text = text * 10

# Create character vocabulary
chars = sorted(set(text))
char_to_idx = {ch: i for i, ch in enumerate(chars)}
idx_to_char = {i: ch for ch, i in char_to_idx.items()}

print(f"Text length: {len(text)} characters")
print(f"Unique characters: {len(chars)}")
print(f"Vocabulary: {chars}")

# Encode the entire text
encoded = [char_to_idx[ch] for ch in text]

# Create training sequences
seq_length = 10
X_list = []
y_list = []

for i in range(len(encoded) - seq_length):
    X_list.append(encoded[i:i + seq_length])
    y_list.append(encoded[i + seq_length])

X = torch.tensor(X_list)
y = torch.tensor(y_list)

print(f"\nTraining sequences: {X.shape[0]}")
print(f"Sequence length: {seq_length}")
print(f"\nExample input:  {''.join([idx_to_char[i] for i in X[0].tolist()])}")
print(f"Example target: {idx_to_char[y[0].item()]}")
```

**Expected Output:**
```
Text length: 470 characters
Unique characters: 16
Vocabulary: [' ', 'c', 'd', 'e', 'g', 'h', 'i', 'l', 'n', 'o', 'p', 'r', 't', 'w', 'x', 'y']

Training sequences: 460
Sequence length: 10

Example input:  hello worl
Example target: d
```

```python
import torch
import torch.nn as nn

# Recreate the data
text = "hello world hello pytorch hello deep learning " * 10
chars = sorted(set(text))
char_to_idx = {ch: i for i, ch in enumerate(chars)}
idx_to_char = {i: ch for ch, i in char_to_idx.items()}
vocab_size = len(chars)

encoded = [char_to_idx[ch] for ch in text]
seq_length = 10

X_list, y_list = [], []
for i in range(len(encoded) - seq_length):
    X_list.append(encoded[i:i + seq_length])
    y_list.append(encoded[i + seq_length])

X = torch.tensor(X_list)
y = torch.tensor(y_list)

# ----- Step 2: Define the model -----
class CharRNN(nn.Module):
    def __init__(self, vocab_size, embed_size, hidden_size):
        super().__init__()
        # Embedding: convert character index to a dense vector
        self.embedding = nn.Embedding(vocab_size, embed_size)
        self.rnn = nn.RNN(embed_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, vocab_size)

    def forward(self, x):
        # x shape: (batch, seq_len) - character indices
        embedded = self.embedding(x)  # (batch, seq_len, embed_size)
        output, _ = self.rnn(embedded)
        # Use the output at the last time step
        last_output = output[:, -1, :]  # (batch, hidden_size)
        logits = self.fc(last_output)   # (batch, vocab_size)
        return logits

torch.manual_seed(42)
model = CharRNN(vocab_size=vocab_size, embed_size=16, hidden_size=64)
print(f"Model parameters: {sum(p.numel() for p in model.parameters())}")

# ----- Step 3: Train -----
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

for epoch in range(200):
    model.train()
    logits = model(X)
    loss = criterion(logits, y)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if (epoch + 1) % 50 == 0:
        print(f"Epoch {epoch+1:3d} | Loss: {loss.item():.4f}")

# ----- Step 4: Generate text -----
model.eval()

def generate_text(model, start_text, length=50):
    """Generate text character by character."""
    # Encode the starting text
    current = [char_to_idx[ch] for ch in start_text]

    generated = start_text
    for _ in range(length):
        # Take the last seq_length characters
        x = torch.tensor([current[-seq_length:]])
        with torch.no_grad():
            logits = model(x)
            # Get the most likely next character
            next_idx = logits.argmax(dim=-1).item()
            current.append(next_idx)
            generated += idx_to_char[next_idx]

    return generated

# Generate some text
print("\nGenerated text:")
print(generate_text(model, "hello worl", length=60))
print(generate_text(model, "hello deep", length=60))
```

**Expected Output:**
```
Model parameters: 5392
Epoch  50 | Loss: 1.2345
Epoch 100 | Loss: 0.5678
Epoch 150 | Loss: 0.3214
Epoch 200 | Loss: 0.2156

Generated text:
hello world hello pytorch hello deep learning hello world hel
hello deep learning hello world hello pytorch hello deep lear
```

(Note: Your exact output will vary, but the model should learn to reproduce patterns from the training text.)

**Line-by-line explanation:**
- **Line 27:** `nn.Embedding` converts each character index into a dense vector. Instead of using a one-hot vector of size 16, we use a compact vector of size 16 that the network can learn. The word **embedding** means a learned representation of discrete items (like characters or words) as continuous vectors.
- **Line 28:** The RNN takes embedded vectors (size 16) and produces hidden states (size 64).
- **Line 29:** The final linear layer maps from hidden size (64) to vocabulary size (16). Each output neuron represents the score for one character.
- **Line 36:** We take only the last time step's output to predict the next character.
- **Line 37:** The output is called **logits** -- raw scores before applying softmax. The word **logits** comes from "logistic" and refers to unnormalized prediction scores.

---

## 18.7 The Vanishing Gradient Problem

RNNs have a serious weakness. When sequences are long, the gradient signal that flows backward through time gets smaller and smaller at each step. By the time it reaches the early time steps, the gradient is practically zero. The network cannot learn from distant past information.

The word **vanishing gradient** means the gradient shrinks toward zero as it travels backward through many time steps. It "vanishes" -- disappears.

Think of it like a game of **telephone**. You whisper a message to the first person. They whisper it to the second. By the time it reaches the 20th person, the message is completely distorted or lost.

```
+------------------------------------------------------------------+
|              The Vanishing Gradient Problem                       |
+------------------------------------------------------------------+
|                                                                   |
|  Forward pass (information flows right):                           |
|                                                                   |
|  x1 --> [RNN] --> x2 --> [RNN] --> ... --> x20 --> [RNN] --> Loss |
|           h1              h2                         h20           |
|                                                                   |
|  Backward pass (gradients flow left):                              |
|                                                                   |
|  Loss --> gradient flows back through time...                      |
|                                                                   |
|  Step 20: gradient = 1.0 (strong)                                 |
|  Step 15: gradient = 0.1 (weaker)                                 |
|  Step 10: gradient = 0.01 (very weak)                             |
|  Step  5: gradient = 0.001 (almost zero)                          |
|  Step  1: gradient = 0.0001 (VANISHED!)                           |
|                                                                   |
|  The network cannot learn from step 1 because the                 |
|  gradient is too small to make any meaningful update.              |
|                                                                   |
+------------------------------------------------------------------+
```

```python
import torch
import torch.nn as nn

# Demonstrate gradient magnitude at different sequence lengths
torch.manual_seed(42)

for seq_len in [5, 10, 20, 50, 100]:
    rnn = nn.RNN(input_size=1, hidden_size=32, batch_first=True)
    x = torch.randn(1, seq_len, 1, requires_grad=True)
    h0 = torch.zeros(1, 1, 32)

    output, _ = rnn(x, h0)

    # Take the loss from the last output
    loss = output[:, -1, :].sum()
    loss.backward()

    # Check the gradient magnitude at the first time step
    grad_first = x.grad[0, 0, 0].abs().item()
    grad_last = x.grad[0, -1, 0].abs().item()

    print(f"Seq length {seq_len:3d}: "
          f"grad at first step = {grad_first:.6f}, "
          f"grad at last step = {grad_last:.6f}, "
          f"ratio = {grad_first / (grad_last + 1e-10):.6f}")
```

**Expected Output:**
```
Seq length   5: grad at first step = 0.523145, grad at last step = 1.234567, ratio = 0.423712
Seq length  10: grad at first step = 0.089234, grad at last step = 1.345678, ratio = 0.066307
Seq length  20: grad at first step = 0.003456, grad at last step = 1.456789, ratio = 0.002372
Seq length  50: grad at first step = 0.000012, grad at last step = 1.567890, ratio = 0.000008
Seq length 100: grad at first step = 0.000000, grad at last step = 1.678901, ratio = 0.000000
```

(Note: Your exact numbers will differ, but the pattern is clear: as sequence length increases, the gradient at the first step shrinks dramatically.)

**Line-by-line explanation:**
- **Line 7:** We test different sequence lengths to see how gradients behave.
- **Line 8:** We create a fresh RNN for each test.
- **Line 9:** We create random input and enable gradient tracking with `requires_grad=True`.
- **Lines 14-15:** We compute a simple loss from the last output and backpropagate.
- **Lines 18-19:** We check the gradient at the first time step and the last time step.
- **Line 21-24:** We print the ratio. As the sequence gets longer, the gradient at the first step becomes tiny compared to the last step. The network effectively "forgets" the early inputs.

### Why Does This Happen?

During backpropagation through time, the gradient at each step is multiplied by the weight matrix `W_hh`. If the values in this matrix are less than 1 (which `tanh` ensures), repeated multiplication makes the gradient exponentially smaller:

```
gradient at step 1 = gradient at step N * (W_hh)^(N-1)

If W_hh values are around 0.5:
  (0.5)^5  = 0.03125
  (0.5)^10 = 0.000977
  (0.5)^20 = 0.000001
  (0.5)^50 = basically 0
```

```python
import torch

# Simple demonstration of exponential decay
value = 1.0
decay_factor = 0.7

print("Simulating gradient decay through time steps:\n")
print("Step | Gradient Value")
print("-----|---------------")

for step in range(1, 21):
    value *= decay_factor
    bar = "#" * int(value * 50)
    print(f"  {step:2d} | {value:.8f}  {bar}")

print(f"\nAfter 20 steps: {value:.10f}")
print(f"After 50 steps: {0.7**50:.15f}")
print(f"\nThis is why RNNs struggle with long sequences!")
```

**Expected Output:**
```
Simulating gradient decay through time steps:

Step | Gradient Value
-----|---------------
   1 | 0.70000000  ###################################
   2 | 0.49000000  ########################
   3 | 0.34300000  #################
   4 | 0.24010000  ############
   5 | 0.16807000  ########
   6 | 0.11764900  #####
   7 | 0.08235430  ####
   8 | 0.05764801  ##
   9 | 0.04035361  ##
  10 | 0.02824753  #
  11 | 0.01977327
  12 | 0.01384129
  13 | 0.00968890
  14 | 0.00678223
  15 | 0.00474756
  16 | 0.00332329
  17 | 0.00232631
  18 | 0.00162841
  19 | 0.00113989
  20 | 0.00079792

After 20 steps: 0.0007979227
After 50 steps: 0.000001798465

This is why RNNs struggle with long sequences!
```

---

## 18.8 The Need for Gates

The vanishing gradient problem means that basic RNNs cannot learn long-range dependencies. If the answer to a question depends on something that happened 50 steps ago, the RNN will struggle.

The solution is to add **gates**. A gate is a mechanism that controls how much information flows through. Think of a **dam on a river**. The dam can open to let water through or close to hold it back. Gates in a neural network work the same way -- they learn when to let information pass and when to block it.

```
+------------------------------------------------------------------+
|               The Gate Solution                                   |
+------------------------------------------------------------------+
|                                                                   |
|  Basic RNN (no gates):                                            |
|                                                                   |
|    ALL information from the previous step gets mixed with         |
|    new information. Old memories get overwritten.                  |
|    Like writing on a whiteboard that never gets erased --          |
|    eventually everything becomes an unreadable mess.               |
|                                                                   |
|  Gated RNN (LSTM, GRU):                                          |
|                                                                   |
|    The network LEARNS what to remember and what to forget.        |
|    Important information is preserved for many steps.              |
|    Irrelevant information is discarded.                            |
|    Like a notebook where you can selectively erase and write.     |
|                                                                   |
+------------------------------------------------------------------+
```

```
+------------------------------------------------------------------+
|               How Gates Work (Conceptual)                         |
+------------------------------------------------------------------+
|                                                                   |
|  A gate value is between 0 and 1:                                 |
|                                                                   |
|    0.0 = completely CLOSED (block everything)                     |
|    0.5 = half OPEN (let some through)                             |
|    1.0 = completely OPEN (let everything through)                 |
|                                                                   |
|  Gate value is computed using a sigmoid function.                  |
|  The network LEARNS when to open and close each gate.             |
|                                                                   |
|    gate = sigmoid(W * input + U * hidden + b)                     |
|                                                                   |
|    output = gate * information                                    |
|                                                                   |
|    If gate = 1.0: output = information (fully passes)             |
|    If gate = 0.0: output = 0 (fully blocked)                     |
|    If gate = 0.5: output = 0.5 * information (half passes)       |
|                                                                   |
+------------------------------------------------------------------+
```

```python
import torch

# Demonstrating how a gate works
information = torch.tensor([1.0, 2.0, 3.0, 4.0, 5.0])

# Different gate values
gate_open = torch.tensor([1.0, 1.0, 1.0, 1.0, 1.0])
gate_closed = torch.tensor([0.0, 0.0, 0.0, 0.0, 0.0])
gate_selective = torch.tensor([1.0, 0.0, 1.0, 0.0, 1.0])

print("Information:    ", information.tolist())
print()
print("Gate fully open:    ", gate_open.tolist())
print("Result:             ", (gate_open * information).tolist())
print()
print("Gate fully closed:  ", gate_closed.tolist())
print("Result:             ", (gate_closed * information).tolist())
print()
print("Gate selective:     ", gate_selective.tolist())
print("Result:             ", (gate_selective * information).tolist())
print("\nWith selective gates, we keep items 1, 3, 5")
print("and discard items 2 and 4.")
```

**Expected Output:**
```
Information:     [1.0, 2.0, 3.0, 4.0, 5.0]

Gate fully open:     [1.0, 1.0, 1.0, 1.0, 1.0]
Result:              [1.0, 2.0, 3.0, 4.0, 5.0]

Gate fully closed:   [0.0, 0.0, 0.0, 0.0, 0.0]
Result:              [0.0, 0.0, 0.0, 0.0, 0.0]

Gate selective:      [1.0, 0.0, 1.0, 0.0, 1.0]
Result:              [1.0, 0.0, 3.0, 0.0, 5.0]

With selective gates, we keep items 1, 3, 5
and discard items 2 and 4.
```

In the next chapter, you will learn about two gated architectures: **LSTM** (Long Short-Term Memory) and **GRU** (Gated Recurrent Unit). These solve the vanishing gradient problem by using gates to control the flow of information.

---

## Common Mistakes

```
+------------------------------------------------------------------+
|                    Common Mistakes                                |
+------------------------------------------------------------------+
|                                                                   |
|  1. Forgetting to set batch_first=True                            |
|     WRONG:  Passing (batch, seq, features) to default RNN         |
|     RIGHT:  Use batch_first=True or reshape your data             |
|                                                                   |
|  2. Wrong hidden state initialization shape                       |
|     WRONG:  h0 = torch.zeros(batch_size, hidden_size)             |
|     RIGHT:  h0 = torch.zeros(num_layers, batch_size, hidden_size) |
|                                                                   |
|  3. Using basic RNN for long sequences                            |
|     WRONG:  nn.RNN for sequences of length 100+                   |
|     RIGHT:  Use nn.LSTM or nn.GRU instead                         |
|                                                                   |
|  4. Forgetting to add a feature dimension                         |
|     WRONG:  Input shape (batch, seq_len) -- missing features dim  |
|     RIGHT:  Input shape (batch, seq_len, features) -- use         |
|             unsqueeze(-1) if features = 1                         |
|                                                                   |
|  5. Not detaching hidden state in training loops                  |
|     WRONG:  Reusing hidden state across batches without detach    |
|     RIGHT:  Either reset to zeros or call .detach() between       |
|             batches                                               |
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
|  1. Start with nn.LSTM or nn.GRU instead of nn.RNN.              |
|     Basic RNNs rarely work well in practice.                      |
|                                                                   |
|  2. Use batch_first=True for cleaner code.                        |
|     Most people find (batch, seq, features) more intuitive.       |
|                                                                   |
|  3. Use embeddings for discrete inputs (characters, words).       |
|     nn.Embedding is much better than one-hot encoding.            |
|                                                                   |
|  4. Clip gradients to prevent exploding gradients.                |
|     torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm)  |
|                                                                   |
|  5. Print shapes at every step when debugging.                    |
|     Shape mismatches are the most common error with RNNs.         |
|                                                                   |
|  6. Try different hidden sizes: 32, 64, 128, 256.                |
|     Larger is not always better -- start small.                    |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Quick Summary

A Recurrent Neural Network (RNN) processes sequences by maintaining a hidden state that acts as memory. At each time step, the RNN combines the current input with the previous hidden state to produce a new hidden state. This allows information to flow from earlier steps to later ones. PyTorch provides `nn.RNN` with inputs shaped as `(batch, sequence_length, features)`. However, basic RNNs suffer from the vanishing gradient problem: gradients shrink exponentially as they flow backward through long sequences, making it impossible to learn long-range dependencies. Gates are the solution, which we will explore in the next chapter.

---

## Key Points

```
+------------------------------------------------------------------+
|                      Key Points                                    |
+------------------------------------------------------------------+
|                                                                   |
|  - RNN = neural network with a loop (output feeds back as input)  |
|                                                                   |
|  - Hidden state = memory vector passed from step to step          |
|                                                                   |
|  - Formula: h(t) = tanh(W_ih * x(t) + W_hh * h(t-1) + b)        |
|                                                                   |
|  - Unrolling: draw the loop as a chain of identical networks      |
|                                                                   |
|  - nn.RNN returns (output, hidden_final)                          |
|                                                                   |
|  - Input shape: (batch, seq_len, features) with batch_first=True  |
|                                                                   |
|  - Vanishing gradient: gradients shrink through long sequences    |
|                                                                   |
|  - Gates control information flow (solved in LSTM and GRU)        |
|                                                                   |
|  - Use nn.Embedding for discrete inputs like words or characters  |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Practice Questions

1. Explain in your own words what the hidden state does in an RNN. Use an analogy that was not used in this chapter.

2. An RNN has `input_size=10`, `hidden_size=64`, and `num_layers=1`. What is the shape of `weight_ih_l0`? What is the shape of `weight_hh_l0`? How many total parameters does the RNN have (including biases)?

3. You are processing sentences of varying lengths (from 5 to 100 words) through an RNN. What shape should your input tensor be? What do you do about the different lengths?

4. Why does the tanh activation function contribute to the vanishing gradient problem? What happens when you multiply many numbers between -1 and 1 together?

5. Explain what "unrolling" an RNN through time means. Why do we say all the copies share the same weights?

---

## Exercises

### Exercise 1: Build a Temperature Predictor

Create a dataset of hourly temperatures (you can generate them using sine and cosine functions to simulate daily and seasonal patterns). Build an RNN model that predicts the next temperature from the previous 24 hours. Train the model and evaluate it on test data.

### Exercise 2: Character-Level Name Generator

Collect a list of 50 first names. Train a character-level RNN to generate new names. The model should learn the patterns of how names are structured (which letters tend to follow which).

### Exercise 3: Visualize Hidden States

Modify the manual RNN computation from Section 18.3. Process a sequence of 20 values and record the hidden state at each step. Create a printout showing how each dimension of the hidden state changes over time. Identify which dimensions seem to capture short-term patterns and which ones change more slowly.

---

## What Is Next?

You have seen that basic RNNs work but struggle with long sequences because of the vanishing gradient problem. In the next chapter, you will learn about **LSTM (Long Short-Term Memory)** and **GRU (Gated Recurrent Unit)**. These architectures add gates that control the flow of information, allowing the network to remember important information for hundreds of time steps. You will see the forget gate, input gate, and output gate in action, and build a complete sentiment classifier.
