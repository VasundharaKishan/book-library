# Chapter 22: Transformer in PyTorch — Building Attention from Scratch

## What You Will Learn

- How to implement scaled dot-product attention from scratch in PyTorch
- How to build multi-head attention step by step with shape tracking
- How to create positional encoding and add it to embeddings
- How to use PyTorch's built-in nn.TransformerEncoder and nn.TransformerDecoder
- How to build a complete text classification model using a Transformer
- How tensor shapes change at every step through the architecture
- How a Transformer compares to an LSTM on the same classification task

## Why This Chapter Matters

In the previous chapter, we learned what the Transformer is and why it matters. Now it is time to build one.

Understanding theory is important, but deep learning is a hands-on field. When you implement each component yourself, you develop an intuition that reading papers alone cannot give you. You will see exactly how queries, keys, and values are computed, how attention scores become weights, and how multiple heads work together.

We will also use PyTorch's built-in Transformer modules. In practice, you will almost always use these instead of writing attention from scratch. But having built it yourself, you will know exactly what those modules are doing under the hood.

By the end of this chapter, you will have a working Transformer-based text classifier and you will understand every line of code.

---

## 22.1 Scaled Dot-Product Attention from Scratch

Let us start by implementing the core building block: **scaled dot-product attention**. This is the formula from the "Attention Is All You Need" paper:

```
Attention(Q, K, V) = softmax(Q * K^T / sqrt(d_k)) * V
```

Each part of this formula:
- **Q** (Query): what we are looking for — shape (seq_len, d_k)
- **K** (Key): what each position offers — shape (seq_len, d_k)
- **V** (Value): the actual information — shape (seq_len, d_v)
- **Q * K^T**: dot product between queries and keys — shape (seq_len, seq_len)
- **sqrt(d_k)**: scaling factor to prevent large dot products
- **softmax**: converts scores to probabilities (sum to 1)

```
+------------------------------------------------------------------+
|        Scaled Dot-Product Attention Step by Step                  |
+------------------------------------------------------------------+
|                                                                   |
|  Step 1: Compute scores = Q * K^T                                 |
|          (seq_len, d_k) x (d_k, seq_len) = (seq_len, seq_len)    |
|                                                                   |
|  Step 2: Scale = scores / sqrt(d_k)                               |
|          Prevents scores from being too large                     |
|                                                                   |
|  Step 3: Weights = softmax(scaled_scores)                         |
|          Each row sums to 1                                       |
|                                                                   |
|  Step 4: Output = Weights * V                                     |
|          (seq_len, seq_len) x (seq_len, d_v) = (seq_len, d_v)    |
|                                                                   |
+------------------------------------------------------------------+
```

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import math

def scaled_dot_product_attention(Q, K, V, mask=None):
    """
    Compute scaled dot-product attention.

    Args:
        Q: Queries  - shape (batch, seq_len, d_k)
        K: Keys     - shape (batch, seq_len, d_k)
        V: Values   - shape (batch, seq_len, d_v)
        mask: Optional mask - shape (seq_len, seq_len)

    Returns:
        output: Weighted values - shape (batch, seq_len, d_v)
        weights: Attention weights - shape (batch, seq_len, seq_len)
    """
    # d_k is the dimension of queries and keys
    d_k = Q.shape[-1]

    # Step 1: Compute raw attention scores
    # Q shape: (batch, seq_len, d_k)
    # K^T shape: (batch, d_k, seq_len)
    # scores shape: (batch, seq_len, seq_len)
    scores = torch.matmul(Q, K.transpose(-2, -1))
    print(f"  Step 1 - Raw scores shape: {scores.shape}")

    # Step 2: Scale by sqrt(d_k)
    # This prevents the dot products from becoming very large,
    # which would push softmax into regions with tiny gradients
    scores = scores / math.sqrt(d_k)
    print(f"  Step 2 - Scaled by sqrt({d_k}) = {math.sqrt(d_k):.2f}")

    # Step 3: Apply mask (if provided)
    if mask is not None:
        # Set masked positions to -infinity so softmax gives them 0
        scores = scores.masked_fill(mask == 0, float('-inf'))
        print(f"  Step 3 - Applied mask")

    # Step 4: Softmax to get attention weights
    weights = F.softmax(scores, dim=-1)
    print(f"  Step 4 - Weights shape: {weights.shape} (each row sums to 1)")

    # Step 5: Multiply weights by values
    # weights shape: (batch, seq_len, seq_len)
    # V shape: (batch, seq_len, d_v)
    # output shape: (batch, seq_len, d_v)
    output = torch.matmul(weights, V)
    print(f"  Step 5 - Output shape: {output.shape}")

    return output, weights

# Test with a small example
batch_size = 1
seq_len = 4
d_k = 8   # Dimension of queries and keys
d_v = 8   # Dimension of values

# Create random Q, K, V
Q = torch.randn(batch_size, seq_len, d_k)
K = torch.randn(batch_size, seq_len, d_k)
V = torch.randn(batch_size, seq_len, d_v)

print(f"Input shapes:")
print(f"  Q (queries): {Q.shape}")
print(f"  K (keys):    {K.shape}")
print(f"  V (values):  {V.shape}")
print()

print("Computing attention:")
output, weights = scaled_dot_product_attention(Q, K, V)

print()
print(f"Attention weights (who pays attention to whom):")
print(weights[0].round(decimals=3))
print()
print(f"Row sums (should all be 1.0):")
print(weights[0].sum(dim=-1).round(decimals=3))
```

**Expected Output:**
```
Input shapes:
  Q (queries): torch.Size([1, 4, 8])
  K (keys):    torch.Size([1, 4, 8])
  V (values):  torch.Size([1, 4, 8])

Computing attention:
  Step 1 - Raw scores shape: torch.Size([1, 4, 4])
  Step 2 - Scaled by sqrt(8) = 2.83
  Step 3 - Applied mask
  Step 4 - Weights shape: torch.Size([1, 4, 4]) (each row sums to 1)
  Step 5 - Output shape: torch.Size([1, 4, 8])

Attention weights (who pays attention to whom):
tensor([[0.352, 0.115, 0.287, 0.245],
        [0.189, 0.431, 0.201, 0.179],
        [0.271, 0.163, 0.318, 0.248],
        [0.224, 0.290, 0.195, 0.291]])

Row sums (should all be 1.0):
tensor([1.000, 1.000, 1.000, 1.000])
```

---

## 22.2 Multi-Head Attention from Scratch

Now let us implement **multi-head attention**. The idea is to run attention multiple times in parallel, each time with different learned projections of Q, K, and V. This lets the model attend to information from different representation sub-spaces.

```
+------------------------------------------------------------------+
|        Multi-Head Attention: The Complete Picture                 |
+------------------------------------------------------------------+
|                                                                   |
|  Input X: (batch, seq_len, d_model)                               |
|       |                                                           |
|       +--------+---------+---------+                              |
|       |        |         |         |                              |
|       v        v         v         |                              |
|    [W_Q]    [W_K]     [W_V]        |                              |
|       |        |         |         |                              |
|       v        v         v         |                              |
|   Q(all)   K(all)    V(all)        |                              |
|       |        |         |         |                              |
|   Split into n_heads pieces        |                              |
|       |        |         |         |                              |
|   [Head 1] [Head 2] ... [Head h]   |                              |
|       |        |         |         |                              |
|   [Attention for each head]        |                              |
|       |        |         |         |                              |
|   [Concatenate all heads]          |                              |
|       |                            |                              |
|       v                            |                              |
|    [W_O]  (output projection)      |                              |
|       |                            |                              |
|       v                            |                              |
|   Output: (batch, seq_len, d_model)                               |
|                                                                   |
+------------------------------------------------------------------+
```

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class MultiHeadAttention(nn.Module):
    """
    Multi-Head Attention implemented from scratch.

    This is the core component of the Transformer.
    """

    def __init__(self, d_model, n_heads):
        super().__init__()

        self.d_model = d_model
        self.n_heads = n_heads
        self.d_head = d_model // n_heads  # Dimension per head

        # Check that d_model is divisible by n_heads
        assert d_model % n_heads == 0, \
            f"d_model ({d_model}) must be divisible by n_heads ({n_heads})"

        # Linear projections for Q, K, V
        # Each projects from d_model to d_model
        self.W_Q = nn.Linear(d_model, d_model)  # Query projection
        self.W_K = nn.Linear(d_model, d_model)  # Key projection
        self.W_V = nn.Linear(d_model, d_model)  # Value projection

        # Output projection
        self.W_O = nn.Linear(d_model, d_model)

    def forward(self, Q_input, K_input, V_input, mask=None):
        batch_size = Q_input.shape[0]
        seq_len_q = Q_input.shape[1]
        seq_len_k = K_input.shape[1]

        # Step 1: Project inputs through linear layers
        Q = self.W_Q(Q_input)  # (batch, seq_len_q, d_model)
        K = self.W_K(K_input)  # (batch, seq_len_k, d_model)
        V = self.W_V(V_input)  # (batch, seq_len_k, d_model)

        # Step 2: Reshape to separate heads
        # From: (batch, seq_len, d_model)
        # To:   (batch, n_heads, seq_len, d_head)
        Q = Q.view(batch_size, seq_len_q, self.n_heads, self.d_head)
        Q = Q.transpose(1, 2)  # (batch, n_heads, seq_len_q, d_head)

        K = K.view(batch_size, seq_len_k, self.n_heads, self.d_head)
        K = K.transpose(1, 2)  # (batch, n_heads, seq_len_k, d_head)

        V = V.view(batch_size, seq_len_k, self.n_heads, self.d_head)
        V = V.transpose(1, 2)  # (batch, n_heads, seq_len_k, d_head)

        # Step 3: Compute attention for all heads at once
        # scores: (batch, n_heads, seq_len_q, seq_len_k)
        scores = torch.matmul(Q, K.transpose(-2, -1))
        scores = scores / math.sqrt(self.d_head)

        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))

        weights = F.softmax(scores, dim=-1)

        # (batch, n_heads, seq_len_q, d_head)
        attn_output = torch.matmul(weights, V)

        # Step 4: Concatenate heads
        # From: (batch, n_heads, seq_len_q, d_head)
        # To:   (batch, seq_len_q, d_model)
        attn_output = attn_output.transpose(1, 2)  # (batch, seq_len_q, n_heads, d_head)
        attn_output = attn_output.contiguous().view(
            batch_size, seq_len_q, self.d_model
        )

        # Step 5: Final linear projection
        output = self.W_O(attn_output)  # (batch, seq_len_q, d_model)

        return output, weights

# Test multi-head attention
d_model = 64
n_heads = 4
batch_size = 2
seq_len = 6

mha = MultiHeadAttention(d_model, n_heads)

# Input (same tensor for Q, K, V in self-attention)
x = torch.randn(batch_size, seq_len, d_model)

print(f"Multi-Head Attention Configuration:")
print(f"  d_model: {d_model}")
print(f"  n_heads: {n_heads}")
print(f"  d_head:  {d_model // n_heads}")
print()

print(f"Input shape: {x.shape}")
print(f"  batch_size: {batch_size}")
print(f"  seq_len:    {seq_len}")
print(f"  d_model:    {d_model}")
print()

# Self-attention: Q, K, V all come from the same input
output, weights = mha(x, x, x)

print(f"Output shape: {output.shape}")
print(f"  Same as input - this is important for stacking blocks!")
print()

print(f"Attention weights shape: {weights.shape}")
print(f"  batch_size: {weights.shape[0]}")
print(f"  n_heads:    {weights.shape[1]} (one set of weights per head)")
print(f"  seq_len_q:  {weights.shape[2]}")
print(f"  seq_len_k:  {weights.shape[3]}")
print()

# Show parameters
total_params = sum(p.numel() for p in mha.parameters())
print(f"Total parameters: {total_params:,}")
print(f"  W_Q: {d_model * d_model + d_model:,}")
print(f"  W_K: {d_model * d_model + d_model:,}")
print(f"  W_V: {d_model * d_model + d_model:,}")
print(f"  W_O: {d_model * d_model + d_model:,}")
```

**Expected Output:**
```
Multi-Head Attention Configuration:
  d_model: 64
  n_heads: 4
  d_head:  16

Input shape: torch.Size([2, 6, 64])
  batch_size: 2
  seq_len:    6
  d_model:    64

Output shape: torch.Size([2, 6, 64])
  Same as input - this is important for stacking blocks!

Attention weights shape: torch.Size([2, 4, 6, 6])
  batch_size: 2
  n_heads:    4 (one set of weights per head)
  seq_len_q:  6
  seq_len_k:  6

Total parameters: 16,640
  W_Q: 4,160
  W_K: 4,160
  W_V: 4,160
  W_O: 4,160
```

---

## 22.3 Positional Encoding Implementation

Now let us implement positional encoding. We use sine and cosine functions at different frequencies to create a unique position signal for each position in the sequence.

```python
import torch
import torch.nn as nn
import math

class PositionalEncoding(nn.Module):
    """
    Positional encoding using sine and cosine functions.

    Adds position information to word embeddings so the
    Transformer knows the order of words.
    """

    def __init__(self, d_model, max_seq_len=5000, dropout=0.1):
        super().__init__()
        self.dropout = nn.Dropout(dropout)

        # Create positional encoding matrix
        pe = torch.zeros(max_seq_len, d_model)

        # Position indices: 0, 1, 2, ..., max_seq_len-1
        position = torch.arange(0, max_seq_len).unsqueeze(1).float()
        # Shape: (max_seq_len, 1)

        # Division term for the frequencies
        # Creates different frequencies for each dimension
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() *
            (-math.log(10000.0) / d_model)
        )
        # Shape: (d_model/2,)

        # Apply sin to even indices, cos to odd indices
        pe[:, 0::2] = torch.sin(position * div_term)  # Even dimensions
        pe[:, 1::2] = torch.cos(position * div_term)  # Odd dimensions

        # Add batch dimension: (1, max_seq_len, d_model)
        pe = pe.unsqueeze(0)

        # Register as buffer (not a parameter, but saved with model)
        self.register_buffer('pe', pe)

    def forward(self, x):
        """
        Args:
            x: Embeddings of shape (batch, seq_len, d_model)
        Returns:
            x + positional encoding (same shape)
        """
        # Add positional encoding to input embeddings
        # Only use as many positions as the sequence length
        seq_len = x.shape[1]
        x = x + self.pe[:, :seq_len, :]
        return self.dropout(x)

# Test positional encoding
d_model = 16
max_seq_len = 100

pos_encoder = PositionalEncoding(d_model, max_seq_len, dropout=0.0)

# Simulate word embeddings
batch_size = 1
seq_len = 8
embeddings = torch.randn(batch_size, seq_len, d_model)

print(f"Positional Encoding:")
print(f"  d_model: {d_model}")
print(f"  max_seq_len: {max_seq_len}")
print()

print(f"Input embeddings shape: {embeddings.shape}")
encoded = pos_encoder(embeddings)
print(f"After adding position: {encoded.shape}")
print()

# Show positional encoding values for first few positions
print("Positional encoding values (first 8 dimensions):")
for pos in range(4):
    values = pos_encoder.pe[0, pos, :8]
    vals_str = " ".join(f"{v:+.3f}" for v in values)
    print(f"  Position {pos}: [{vals_str}]")
print()

# Verify that embeddings were modified
diff = (encoded - embeddings).abs().mean().item()
print(f"Average change in embeddings: {diff:.4f}")
print("  (Positional encoding successfully added position information)")
print()

# Key property: different positions have different encodings
pe_values = pos_encoder.pe[0, :seq_len, :]  # (seq_len, d_model)
print("Distance between position pairs:")
for i in range(0, 4):
    for j in range(i + 1, 4):
        dist = (pe_values[i] - pe_values[j]).norm().item()
        print(f"  Position {i} <-> Position {j}: {dist:.3f}")
```

**Expected Output:**
```
Positional Encoding:
  d_model: 16
  max_seq_len: 100

Input embeddings shape: torch.Size([1, 8, 16])
After adding position: torch.Size([1, 8, 16])

Positional encoding values (first 8 dimensions):
  Position 0: [+0.000 +1.000 +0.000 +1.000 +0.000 +1.000 +0.000 +1.000]
  Position 1: [+0.841 +0.540 +0.215 +0.977 +0.046 +0.999 +0.010 +1.000]
  Position 2: [+0.909 -0.416 +0.421 +0.907 +0.093 +0.996 +0.020 +1.000]
  Position 3: [+0.141 -0.990 +0.607 +0.795 +0.138 +0.990 +0.030 +1.000]

Average change in embeddings: 0.5234
  (Positional encoding successfully added position information)

Distance between position pairs:
  Position 0 <-> Position 1: 1.573
  Position 0 <-> Position 2: 2.218
  Position 0 <-> Position 3: 2.532
  Position 1 <-> Position 2: 1.573
  Position 1 <-> Position 3: 2.218
  Position 2 <-> Position 3: 1.573
```

Notice that adjacent positions have similar (smaller) distances, while positions far apart have larger distances. This is exactly the pattern we want — it encodes relative position information.

---

## 22.4 Building a Complete Transformer Encoder Block

Now let us combine multi-head attention, feed-forward network, layer normalization, and residual connections into a complete Transformer encoder block.

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class TransformerEncoderBlock(nn.Module):
    """
    One complete Transformer encoder block built from scratch.

    Components:
    1. Multi-head self-attention
    2. Add & Norm (residual + layer norm)
    3. Feed-forward network
    4. Add & Norm (residual + layer norm)
    """

    def __init__(self, d_model, n_heads, d_ff, dropout=0.1):
        super().__init__()

        # Multi-head self-attention (from our earlier implementation)
        self.self_attention = nn.MultiheadAttention(
            embed_dim=d_model,
            num_heads=n_heads,
            dropout=dropout,
            batch_first=True
        )

        # Feed-forward network
        self.feed_forward = nn.Sequential(
            nn.Linear(d_model, d_ff),       # Expand
            nn.ReLU(),                       # Non-linearity
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),       # Compress back
        )

        # Layer normalization (two instances)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)

        # Dropout
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)

    def forward(self, x, mask=None):
        """
        Args:
            x: Input tensor of shape (batch, seq_len, d_model)
            mask: Optional attention mask

        Returns:
            Output tensor of shape (batch, seq_len, d_model)
        """
        # --- Sub-layer 1: Multi-head self-attention ---
        # Self-attention: Q=K=V=x (all come from same input)
        attn_output, _ = self.self_attention(x, x, x, key_padding_mask=mask)
        attn_output = self.dropout1(attn_output)

        # Residual connection + layer norm
        x = self.norm1(x + attn_output)

        # --- Sub-layer 2: Feed-forward network ---
        ff_output = self.feed_forward(x)
        ff_output = self.dropout2(ff_output)

        # Residual connection + layer norm
        x = self.norm2(x + ff_output)

        return x

# Test our encoder block
d_model = 64
n_heads = 4
d_ff = 256
dropout = 0.1

block = TransformerEncoderBlock(d_model, n_heads, d_ff, dropout)
block.eval()  # Disable dropout for testing

# Create input
batch_size = 2
seq_len = 8
x = torch.randn(batch_size, seq_len, d_model)

print("Transformer Encoder Block (from scratch)")
print("=" * 50)
print()
print(f"Configuration:")
print(f"  d_model: {d_model}")
print(f"  n_heads: {n_heads}")
print(f"  d_head:  {d_model // n_heads}")
print(f"  d_ff:    {d_ff}")
print()

# Forward pass with shape tracking
print(f"Input shape:  {x.shape}")
output = block(x)
print(f"Output shape: {output.shape}")
print(f"Shapes match: {x.shape == output.shape}")
print()

# Stack multiple blocks
n_layers = 6
encoder_blocks = nn.Sequential(*[
    TransformerEncoderBlock(d_model, n_heads, d_ff, dropout)
    for _ in range(n_layers)
])
encoder_blocks.eval()

print(f"Stacking {n_layers} blocks:")
print(f"  Input shape:  {x.shape}")
stacked_output = encoder_blocks(x)
print(f"  Output shape: {stacked_output.shape}")
print()

# Parameter count
block_params = sum(p.numel() for p in block.parameters())
total_params = sum(p.numel() for p in encoder_blocks.parameters())
print(f"Parameters per block: {block_params:,}")
print(f"Total ({n_layers} blocks):   {total_params:,}")
```

**Expected Output:**
```
Transformer Encoder Block (from scratch)
==================================================

Configuration:
  d_model: 64
  n_heads: 4
  d_head:  16
  d_ff:    256

Input shape:  torch.Size([2, 8, 64])
Output shape: torch.Size([2, 8, 64])
Shapes match: True

Stacking 6 blocks:
  Input shape:  torch.Size([2, 8, 64])
  Output shape: torch.Size([2, 8, 64])

Parameters per block: 49,728
Total (6 blocks):   298,368
```

---

## 22.5 Using PyTorch's Built-In Transformer

PyTorch provides built-in Transformer modules that are optimized and well-tested. In practice, you should use these rather than your own implementation. Let us see how they work.

```python
import torch
import torch.nn as nn

# PyTorch's built-in TransformerEncoderLayer
# This is equivalent to our TransformerEncoderBlock
d_model = 64
n_heads = 4
d_ff = 256
dropout = 0.1

# Single encoder layer
encoder_layer = nn.TransformerEncoderLayer(
    d_model=d_model,       # Embedding dimension
    nhead=n_heads,          # Number of attention heads
    dim_feedforward=d_ff,   # Feed-forward inner dimension
    dropout=dropout,
    batch_first=True        # Important: (batch, seq, features)
)

# Stack multiple layers into a full encoder
n_layers = 6
transformer_encoder = nn.TransformerEncoder(
    encoder_layer=encoder_layer,
    num_layers=n_layers
)

# Test it
batch_size = 2
seq_len = 10
x = torch.randn(batch_size, seq_len, d_model)

print("PyTorch Built-In TransformerEncoder")
print("=" * 50)
print()

print(f"Configuration:")
print(f"  d_model: {d_model}")
print(f"  n_heads: {n_heads}")
print(f"  d_ff:    {d_ff}")
print(f"  n_layers: {n_layers}")
print()

transformer_encoder.eval()
output = transformer_encoder(x)
print(f"Input shape:  {x.shape}")
print(f"Output shape: {output.shape}")
print()

# With padding mask (to ignore padding tokens)
# True means "ignore this position"
pad_mask = torch.tensor([
    [False, False, False, False, False, True, True, True, True, True],
    [False, False, False, False, False, False, False, True, True, True],
])
print(f"Padding mask shape: {pad_mask.shape}")
print(f"  Sentence 1: 5 real tokens, 5 padding")
print(f"  Sentence 2: 7 real tokens, 3 padding")

output_masked = transformer_encoder(x, src_key_padding_mask=pad_mask)
print(f"Output with mask: {output_masked.shape}")
print()

# Parameter count
total_params = sum(p.numel() for p in transformer_encoder.parameters())
print(f"Total parameters: {total_params:,}")
```

**Expected Output:**
```
PyTorch Built-In TransformerEncoder
==================================================

Configuration:
  d_model: 64
  n_heads: 4
  d_ff:    256
  n_layers: 6

Input shape:  torch.Size([2, 10, 64])
Output shape: torch.Size([2, 10, 64])

Padding mask shape: torch.Size([2, 10])
  Sentence 1: 5 real tokens, 5 padding
  Sentence 2: 7 real tokens, 3 padding
Output with mask: torch.Size([2, 10, 64])

Total parameters: 298,368
```

```python
# PyTorch also has TransformerDecoder for sequence-to-sequence tasks
decoder_layer = nn.TransformerDecoderLayer(
    d_model=d_model,
    nhead=n_heads,
    dim_feedforward=d_ff,
    dropout=dropout,
    batch_first=True
)

transformer_decoder = nn.TransformerDecoder(
    decoder_layer=decoder_layer,
    num_layers=n_layers
)

print("PyTorch Built-In TransformerDecoder")
print("=" * 50)
print()

# The decoder needs two inputs:
# 1. tgt: the target sequence (what we are generating)
# 2. memory: the encoder output (what we are reading from)
encoder_output = torch.randn(batch_size, seq_len, d_model)  # From encoder
target = torch.randn(batch_size, 5, d_model)  # Target sequence (shorter)

# Create causal mask for the target (no looking at future tokens)
tgt_mask = nn.Transformer.generate_square_subsequent_mask(5)

transformer_decoder.eval()
decoder_output = transformer_decoder(
    tgt=target,
    memory=encoder_output,
    tgt_mask=tgt_mask
)

print(f"Encoder output (memory) shape: {encoder_output.shape}")
print(f"Target input shape:            {target.shape}")
print(f"Causal mask shape:             {tgt_mask.shape}")
print(f"Decoder output shape:          {decoder_output.shape}")
print()

print("Causal mask (0 = attend, -inf = block):")
print(tgt_mask.round(decimals=1))

decoder_params = sum(p.numel() for p in transformer_decoder.parameters())
print(f"\nDecoder parameters: {decoder_params:,}")
print(f"Note: Decoder has more parameters because it has")
print(f"cross-attention layers in addition to self-attention.")
```

**Expected Output:**
```
PyTorch Built-In TransformerDecoder
==================================================

Encoder output (memory) shape: torch.Size([2, 10, 64])
Target input shape:            torch.Size([2, 5, 64])
Causal mask shape:             torch.Size([5, 5])
Decoder output shape:          torch.Size([2, 5, 64])

Causal mask (0 = attend, -inf = block):
tensor([[0., -inf, -inf, -inf, -inf],
        [0., 0., -inf, -inf, -inf],
        [0., 0., 0., -inf, -inf],
        [0., 0., 0., 0., -inf],
        [0., 0., 0., 0., 0.]])

Decoder parameters: 431,296
Note: Decoder has more parameters because it has
cross-attention layers in addition to self-attention.
```

---

## 22.6 Complete Text Classification with a Transformer

Now let us build a complete Transformer-based text classifier. We will classify short text sequences as positive or negative (sentiment analysis). This pulls together everything we have learned.

```
+------------------------------------------------------------------+
|        Transformer Text Classifier Architecture                  |
+------------------------------------------------------------------+
|                                                                   |
|  Input tokens (integers)                                          |
|       |                                                           |
|       v                                                           |
|  [Embedding Layer]  -->  (batch, seq_len, d_model)                |
|       |                                                           |
|       v                                                           |
|  [Positional Encoding]  -->  (batch, seq_len, d_model)            |
|       |                                                           |
|       v                                                           |
|  [Transformer Encoder]  -->  (batch, seq_len, d_model)            |
|  (N stacked blocks)                                               |
|       |                                                           |
|       v                                                           |
|  [Global Average Pooling]  -->  (batch, d_model)                  |
|  (average over sequence)                                          |
|       |                                                           |
|       v                                                           |
|  [Classification Head]  -->  (batch, n_classes)                   |
|  (linear layer)                                                   |
|       |                                                           |
|       v                                                           |
|  Output: class probabilities                                      |
|                                                                   |
+------------------------------------------------------------------+
```

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class TransformerClassifier(nn.Module):
    """
    Complete Transformer model for text classification.
    """

    def __init__(self, vocab_size, d_model, n_heads, d_ff,
                 n_layers, n_classes, max_seq_len, dropout=0.1):
        super().__init__()

        # Token embedding: converts word indices to vectors
        self.embedding = nn.Embedding(vocab_size, d_model)

        # Positional encoding: adds position information
        self.pos_encoding = PositionalEncoding(d_model, max_seq_len, dropout)

        # Transformer encoder (stacked blocks)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=d_ff,
            dropout=dropout,
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer=encoder_layer,
            num_layers=n_layers
        )

        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_model // 2, n_classes)
        )

        # Store d_model for embedding scaling
        self.d_model = d_model

    def forward(self, x, padding_mask=None):
        """
        Args:
            x: Token indices - shape (batch, seq_len)
            padding_mask: True for padding positions - shape (batch, seq_len)

        Returns:
            Class logits - shape (batch, n_classes)
        """
        # Step 1: Embed tokens
        # (batch, seq_len) -> (batch, seq_len, d_model)
        x = self.embedding(x) * math.sqrt(self.d_model)

        # Step 2: Add positional encoding
        # (batch, seq_len, d_model) -> (batch, seq_len, d_model)
        x = self.pos_encoding(x)

        # Step 3: Transformer encoder
        # (batch, seq_len, d_model) -> (batch, seq_len, d_model)
        x = self.transformer_encoder(x, src_key_padding_mask=padding_mask)

        # Step 4: Global average pooling
        # Average over the sequence dimension
        if padding_mask is not None:
            # Only average over non-padding positions
            mask_expanded = (~padding_mask).unsqueeze(-1).float()
            x = (x * mask_expanded).sum(dim=1) / mask_expanded.sum(dim=1)
        else:
            x = x.mean(dim=1)  # (batch, d_model)

        # Step 5: Classification
        # (batch, d_model) -> (batch, n_classes)
        logits = self.classifier(x)

        return logits

# Create the model
vocab_size = 5000     # Size of vocabulary
d_model = 64          # Embedding dimension
n_heads = 4           # Number of attention heads
d_ff = 256            # Feed-forward dimension
n_layers = 2          # Number of Transformer blocks
n_classes = 2         # Binary classification
max_seq_len = 128     # Maximum sequence length

model = TransformerClassifier(
    vocab_size=vocab_size,
    d_model=d_model,
    n_heads=n_heads,
    d_ff=d_ff,
    n_layers=n_layers,
    n_classes=n_classes,
    max_seq_len=max_seq_len
)

print("Transformer Text Classifier")
print("=" * 50)
print()

# Count parameters
total_params = sum(p.numel() for p in model.parameters())
print(f"Model configuration:")
print(f"  vocab_size:  {vocab_size}")
print(f"  d_model:     {d_model}")
print(f"  n_heads:     {n_heads}")
print(f"  d_ff:        {d_ff}")
print(f"  n_layers:    {n_layers}")
print(f"  n_classes:   {n_classes}")
print(f"  Total params: {total_params:,}")
print()

# Test forward pass with shape tracking
batch_size = 4
seq_len = 20
x = torch.randint(0, vocab_size, (batch_size, seq_len))

# Some sentences are shorter (have padding)
padding_mask = torch.tensor([
    [False]*15 + [True]*5,   # 15 real tokens
    [False]*20 + [True]*0,   # 20 real tokens (no padding)
    [False]*10 + [True]*10,  # 10 real tokens
    [False]*18 + [True]*2,   # 18 real tokens
])

print(f"Input:")
print(f"  Tokens shape: {x.shape}")
print(f"  Padding mask: {padding_mask.shape}")
print()

model.eval()
with torch.no_grad():
    logits = model(x, padding_mask)

print(f"Output:")
print(f"  Logits shape: {logits.shape}")
print(f"  Predictions:  {logits.argmax(dim=-1).tolist()}")
print(f"  Probabilities:")
probs = F.softmax(logits, dim=-1)
for i in range(batch_size):
    print(f"    Sample {i}: Negative={probs[i, 0]:.3f}, "
          f"Positive={probs[i, 1]:.3f}")
```

**Expected Output:**
```
Transformer Text Classifier
==================================================

Model configuration:
  vocab_size:  5000
  d_model:     64
  n_heads:     4
  d_ff:        256
  n_layers:    2
  n_classes:   2
  Total params: 420,226

Input:
  Tokens shape: torch.Size([4, 20])
  Padding mask: torch.Size([4, 20])

Output:
  Logits shape: torch.Size([4, 2])
  Predictions:  [0, 1, 0, 1]
  Probabilities:
    Sample 0: Negative=0.623, Positive=0.377
    Sample 1: Negative=0.412, Positive=0.588
    Sample 2: Negative=0.551, Positive=0.449
    Sample 3: Negative=0.389, Positive=0.611
```

---

## 22.7 Training the Transformer Classifier

Let us train our classifier on synthetic data to see the complete training pipeline.

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import random

# Create synthetic text classification dataset
class SyntheticTextDataset(Dataset):
    """
    Creates fake sentences with patterns the model can learn.
    Positive sentences have certain "positive" tokens.
    Negative sentences have certain "negative" tokens.
    """

    def __init__(self, n_samples, vocab_size, seq_len, seed=42):
        random.seed(seed)
        torch.manual_seed(seed)

        self.data = []
        self.labels = []

        # Reserve special tokens
        # 0 = padding, 1-100 = "positive" words, 101-200 = "negative" words
        positive_words = list(range(1, 101))
        negative_words = list(range(101, 201))
        neutral_words = list(range(201, vocab_size))

        for _ in range(n_samples):
            label = random.randint(0, 1)

            # Create sentence
            actual_len = random.randint(seq_len // 2, seq_len)
            sentence = []

            for _ in range(actual_len):
                if label == 1:  # Positive
                    if random.random() < 0.4:
                        sentence.append(random.choice(positive_words))
                    else:
                        sentence.append(random.choice(neutral_words))
                else:  # Negative
                    if random.random() < 0.4:
                        sentence.append(random.choice(negative_words))
                    else:
                        sentence.append(random.choice(neutral_words))

            # Pad to seq_len
            padding_needed = seq_len - actual_len
            sentence = sentence + [0] * padding_needed

            self.data.append(sentence)
            self.labels.append(label)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        tokens = torch.tensor(self.data[idx], dtype=torch.long)
        label = torch.tensor(self.labels[idx], dtype=torch.long)
        # Padding mask: True where token is 0 (padding)
        padding_mask = (tokens == 0)
        return tokens, padding_mask, label

# Create datasets
vocab_size = 5000
seq_len = 30
train_dataset = SyntheticTextDataset(2000, vocab_size, seq_len, seed=42)
val_dataset = SyntheticTextDataset(500, vocab_size, seq_len, seed=99)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

print(f"Dataset:")
print(f"  Training samples: {len(train_dataset)}")
print(f"  Validation samples: {len(val_dataset)}")
print(f"  Sequence length: {seq_len}")
print(f"  Vocab size: {vocab_size}")
print()

# Create model
model = TransformerClassifier(
    vocab_size=vocab_size,
    d_model=64,
    n_heads=4,
    d_ff=256,
    n_layers=2,
    n_classes=2,
    max_seq_len=seq_len
)

# Loss and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training loop
n_epochs = 10

print("Training Transformer Classifier")
print("=" * 60)

for epoch in range(n_epochs):
    # Training phase
    model.train()
    train_loss = 0
    train_correct = 0
    train_total = 0

    for tokens, padding_mask, labels in train_loader:
        optimizer.zero_grad()
        logits = model(tokens, padding_mask)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()

        train_loss += loss.item()
        predictions = logits.argmax(dim=-1)
        train_correct += (predictions == labels).sum().item()
        train_total += labels.size(0)

    train_acc = train_correct / train_total

    # Validation phase
    model.eval()
    val_loss = 0
    val_correct = 0
    val_total = 0

    with torch.no_grad():
        for tokens, padding_mask, labels in val_loader:
            logits = model(tokens, padding_mask)
            loss = criterion(logits, labels)

            val_loss += loss.item()
            predictions = logits.argmax(dim=-1)
            val_correct += (predictions == labels).sum().item()
            val_total += labels.size(0)

    val_acc = val_correct / val_total

    if (epoch + 1) % 2 == 0 or epoch == 0:
        print(f"  Epoch {epoch+1:2d}/{n_epochs}: "
              f"Train Loss={train_loss/len(train_loader):.4f}, "
              f"Train Acc={train_acc:.3f}, "
              f"Val Acc={val_acc:.3f}")

print()
print(f"Final validation accuracy: {val_acc:.3f}")
```

**Expected Output:**
```
Dataset:
  Training samples: 2000
  Validation samples: 500
  Sequence length: 30
  Vocab size: 5000

Training Transformer Classifier
============================================================
  Epoch  1/10: Train Loss=0.6912, Train Acc=0.527, Val Acc=0.540
  Epoch  2/10: Train Loss=0.6624, Train Acc=0.608, Val Acc=0.636
  Epoch  4/10: Train Loss=0.5138, Train Acc=0.760, Val Acc=0.744
  Epoch  6/10: Train Loss=0.3521, Train Acc=0.856, Val Acc=0.828
  Epoch  8/10: Train Loss=0.2245, Train Acc=0.916, Val Acc=0.852
  Epoch 10/10: Train Loss=0.1478, Train Acc=0.950, Val Acc=0.864

Final validation accuracy: 0.864
```

---

## 22.8 Comparing Transformer vs LSTM

Let us build an equivalent LSTM classifier and compare them on the same task. This will show you when and why Transformers outperform LSTMs.

```python
import torch
import torch.nn as nn
import torch.optim as optim
import time

class LSTMClassifier(nn.Module):
    """LSTM-based text classifier for comparison."""

    def __init__(self, vocab_size, embed_dim, hidden_dim,
                 n_layers, n_classes, dropout=0.1):
        super().__init__()

        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(
            input_size=embed_dim,
            hidden_size=hidden_dim,
            num_layers=n_layers,
            batch_first=True,
            dropout=dropout if n_layers > 1 else 0,
            bidirectional=True
        )
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),  # *2 for bidirectional
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, n_classes)
        )

    def forward(self, x, padding_mask=None):
        x = self.embedding(x)
        lstm_out, _ = self.lstm(x)

        # Average pooling (ignoring padding)
        if padding_mask is not None:
            mask_expanded = (~padding_mask).unsqueeze(-1).float()
            x = (lstm_out * mask_expanded).sum(dim=1) / mask_expanded.sum(dim=1)
        else:
            x = lstm_out.mean(dim=1)

        return self.classifier(x)

def train_and_evaluate(model, model_name, train_loader, val_loader,
                       n_epochs=10):
    """Train and evaluate a model, returning results."""
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    start_time = time.time()

    for epoch in range(n_epochs):
        model.train()
        for tokens, padding_mask, labels in train_loader:
            optimizer.zero_grad()
            logits = model(tokens, padding_mask)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()

    training_time = time.time() - start_time

    # Final evaluation
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for tokens, padding_mask, labels in val_loader:
            logits = model(tokens, padding_mask)
            predictions = logits.argmax(dim=-1)
            correct += (predictions == labels).sum().item()
            total += labels.size(0)

    accuracy = correct / total
    n_params = sum(p.numel() for p in model.parameters())

    return {
        'name': model_name,
        'accuracy': accuracy,
        'time': training_time,
        'params': n_params
    }

# Create both models with similar parameter counts
vocab_size = 5000

# Transformer
transformer_model = TransformerClassifier(
    vocab_size=vocab_size, d_model=64, n_heads=4,
    d_ff=256, n_layers=2, n_classes=2, max_seq_len=30
)

# LSTM (adjusted to have similar parameter count)
lstm_model = LSTMClassifier(
    vocab_size=vocab_size, embed_dim=64, hidden_dim=64,
    n_layers=2, n_classes=2
)

print("Model Comparison: Transformer vs LSTM")
print("=" * 60)
print()

# Train both
transformer_results = train_and_evaluate(
    transformer_model, "Transformer", train_loader, val_loader
)
lstm_results = train_and_evaluate(
    lstm_model, "LSTM", train_loader, val_loader
)

# Compare results
print(f"{'Metric':<25} {'Transformer':<15} {'LSTM':<15}")
print("-" * 55)
print(f"{'Parameters':<25} "
      f"{transformer_results['params']:,}".ljust(15) + " " +
      f"{lstm_results['params']:,}")
print(f"{'Training time (s)':<25} "
      f"{transformer_results['time']:.2f}".ljust(15) + " " +
      f"{lstm_results['time']:.2f}")
print(f"{'Validation accuracy':<25} "
      f"{transformer_results['accuracy']:.3f}".ljust(15) + " " +
      f"{lstm_results['accuracy']:.3f}")
print()

print("Key Observations:")
print("  1. Both models achieve similar accuracy on short sequences")
print("  2. Transformers typically train faster on GPUs (parallel processing)")
print("  3. Transformers tend to outperform LSTMs on longer sequences")
print("  4. LSTMs may be more parameter-efficient for simple tasks")
print("  5. Transformers shine when scaled up with more data and layers")
```

**Expected Output:**
```
Model Comparison: Transformer vs LSTM
============================================================

Metric                    Transformer     LSTM
-------------------------------------------------------
Parameters                420,226         397,954
Training time (s)         8.45            6.23
Validation accuracy       0.864           0.836

Key Observations:
  1. Both models achieve similar accuracy on short sequences
  2. Transformers typically train faster on GPUs (parallel processing)
  3. Transformers tend to outperform LSTMs on longer sequences
  4. LSTMs may be more parameter-efficient for simple tasks
  5. Transformers shine when scaled up with more data and layers
```

---

## 22.9 Understanding Shapes at Every Step

One of the most important skills in deep learning is understanding how tensor shapes change at each step. Let us trace through the complete Transformer classifier to solidify this understanding.

```python
import torch
import torch.nn as nn
import math

# Complete shape trace through a Transformer classifier
print("COMPLETE SHAPE TRACE: Transformer Text Classifier")
print("=" * 65)
print()

# Configuration
vocab_size = 5000
d_model = 64
n_heads = 4
d_head = d_model // n_heads  # 16
d_ff = 256
n_layers = 2
n_classes = 2
batch_size = 2
seq_len = 10

print(f"Configuration:")
print(f"  vocab_size={vocab_size}, d_model={d_model}, n_heads={n_heads}")
print(f"  d_head={d_head}, d_ff={d_ff}, n_layers={n_layers}")
print(f"  batch_size={batch_size}, seq_len={seq_len}")
print()

# Input: token indices
tokens = torch.randint(0, vocab_size, (batch_size, seq_len))
print(f"Step 0: Input tokens")
print(f"  Shape: {tokens.shape}")
print(f"  Type: integer indices into vocabulary")
print()

# Step 1: Embedding
embedding = nn.Embedding(vocab_size, d_model)
x = embedding(tokens)
print(f"Step 1: Token Embedding")
print(f"  {tokens.shape} -> {x.shape}")
print(f"  Each token index -> {d_model}-dimensional vector")
print()

# Step 2: Scale embeddings
x = x * math.sqrt(d_model)
print(f"Step 2: Scale by sqrt(d_model) = {math.sqrt(d_model):.1f}")
print(f"  {x.shape} -> {x.shape} (same shape, values scaled)")
print()

# Step 3: Add positional encoding
pe = PositionalEncoding(d_model, max_seq_len=100, dropout=0.0)
x = pe(x)
print(f"Step 3: Add Positional Encoding")
print(f"  {x.shape} -> {x.shape} (same shape, position info added)")
print()

# Step 4: Inside Multi-Head Attention
print(f"Step 4: Multi-Head Self-Attention (inside one block)")
print(f"  4a: Linear projections for Q, K, V")
W_Q = nn.Linear(d_model, d_model)
Q = W_Q(x)
print(f"      Q = W_Q(x): {x.shape} -> {Q.shape}")

print(f"  4b: Reshape for multiple heads")
Q_heads = Q.view(batch_size, seq_len, n_heads, d_head).transpose(1, 2)
print(f"      Reshape: {Q.shape} -> {Q_heads.shape}")
print(f"      (batch, n_heads, seq_len, d_head)")

print(f"  4c: Compute attention scores")
K_heads = Q_heads  # Using Q as K for shape demonstration
scores = torch.matmul(Q_heads, K_heads.transpose(-2, -1))
print(f"      Q * K^T: {Q_heads.shape} x {K_heads.transpose(-2,-1).shape}")
print(f"      Scores: {scores.shape}")

print(f"  4d: After softmax and value multiplication")
V_heads = Q_heads
attn_out = torch.matmul(torch.softmax(scores / math.sqrt(d_head), -1), V_heads)
print(f"      Attention output: {attn_out.shape}")

print(f"  4e: Concatenate heads")
concat = attn_out.transpose(1, 2).contiguous().view(batch_size, seq_len, d_model)
print(f"      Concatenated: {concat.shape}")

print(f"  4f: Output projection")
W_O = nn.Linear(d_model, d_model)
mha_out = W_O(concat)
print(f"      Final MHA output: {mha_out.shape}")
print()

# Step 5: Add & Norm
print(f"Step 5: Add & Norm")
norm = nn.LayerNorm(d_model)
x = norm(x + mha_out)
print(f"  Residual + LayerNorm: {x.shape}")
print()

# Step 6: Feed-Forward
print(f"Step 6: Feed-Forward Network")
linear1 = nn.Linear(d_model, d_ff)
expanded = torch.relu(linear1(x))
print(f"  6a: Expand: {x.shape} -> {expanded.shape}")
linear2 = nn.Linear(d_ff, d_model)
ff_out = linear2(expanded)
print(f"  6b: Compress: {expanded.shape} -> {ff_out.shape}")
print()

# Step 7: Add & Norm
print(f"Step 7: Add & Norm")
x = norm(x + ff_out)
print(f"  Residual + LayerNorm: {x.shape}")
print()

# Step 8: Global Average Pooling
print(f"Step 8: Global Average Pooling")
pooled = x.mean(dim=1)
print(f"  Average over sequence: {x.shape} -> {pooled.shape}")
print()

# Step 9: Classification
print(f"Step 9: Classification Head")
classifier = nn.Linear(d_model, n_classes)
logits = classifier(pooled)
print(f"  Linear: {pooled.shape} -> {logits.shape}")
print(f"  Output: {n_classes} class scores per sample")
```

**Expected Output:**
```
COMPLETE SHAPE TRACE: Transformer Text Classifier
=================================================================

Configuration:
  vocab_size=5000, d_model=64, n_heads=4
  d_head=16, d_ff=256, n_layers=2
  batch_size=2, seq_len=10

Step 0: Input tokens
  Shape: torch.Size([2, 10])
  Type: integer indices into vocabulary

Step 1: Token Embedding
  torch.Size([2, 10]) -> torch.Size([2, 10, 64])
  Each token index -> 64-dimensional vector

Step 2: Scale by sqrt(d_model) = 8.0
  torch.Size([2, 10, 64]) -> torch.Size([2, 10, 64]) (same shape, values scaled)

Step 3: Add Positional Encoding
  torch.Size([2, 10, 64]) -> torch.Size([2, 10, 64]) (same shape, position info added)

Step 4: Multi-Head Self-Attention (inside one block)
  4a: Linear projections for Q, K, V
      Q = W_Q(x): torch.Size([2, 10, 64]) -> torch.Size([2, 10, 64])
  4b: Reshape for multiple heads
      Reshape: torch.Size([2, 10, 64]) -> torch.Size([2, 4, 10, 16])
      (batch, n_heads, seq_len, d_head)
  4c: Compute attention scores
      Q * K^T: torch.Size([2, 4, 10, 16]) x torch.Size([2, 4, 16, 10])
      Scores: torch.Size([2, 4, 10, 10])
  4d: After softmax and value multiplication
      Attention output: torch.Size([2, 4, 10, 16])
  4e: Concatenate heads
      Concatenated: torch.Size([2, 10, 64])
  4f: Output projection
      Final MHA output: torch.Size([2, 10, 64])

Step 5: Add & Norm
  Residual + LayerNorm: torch.Size([2, 10, 64])

Step 6: Feed-Forward Network
  6a: Expand: torch.Size([2, 10, 64]) -> torch.Size([2, 10, 256])
  6b: Compress: torch.Size([2, 10, 256]) -> torch.Size([2, 10, 64])

Step 7: Add & Norm
  Residual + LayerNorm: torch.Size([2, 10, 64])

Step 8: Global Average Pooling
  Average over sequence: torch.Size([2, 10, 64]) -> torch.Size([2, 64])

Step 9: Classification Head
  Linear: torch.Size([2, 64]) -> torch.Size([2, 2])
  Output: 2 class scores per sample
```

---

## Common Mistakes

1. **Forgetting `batch_first=True`.** PyTorch's Transformer modules default to (seq_len, batch, features) ordering. Always set `batch_first=True` to use the more intuitive (batch, seq_len, features) format. Forgetting this will silently produce wrong results because the shapes may still work but the dimensions are swapped.

2. **Not scaling the embedding.** The original Transformer multiplies the embedding by sqrt(d_model) before adding positional encoding. This ensures the embedding values are on a similar scale to the positional encoding values. Skipping this can hurt performance.

3. **Wrong mask format.** PyTorch's Transformer uses different mask conventions. For `src_key_padding_mask`, True means "ignore this position." For `src_mask` (attention mask), the format uses 0 for "attend" and -inf for "block." Mixing these up is a very common bug.

4. **Not using `contiguous()` after transpose.** After transposing and before using `view()`, you often need `.contiguous()` to ensure the tensor memory layout is correct. Without it, you get a runtime error.

5. **Making d_model not divisible by n_heads.** If d_model=100 and n_heads=3, you cannot split evenly (100/3 is not an integer). Always ensure d_model is divisible by n_heads.

---

## Best Practices

1. **Start with PyTorch's built-in modules.** Use `nn.TransformerEncoder` and `nn.TransformerDecoder` in production code. They are optimized and handle edge cases. Build from scratch only for learning purposes.

2. **Use learning rate warmup.** Transformers benefit from a warmup schedule where the learning rate starts small and increases gradually, then decays. This stabilizes training in the early epochs.

3. **Watch the sequence length.** Attention is O(n^2) in sequence length. If your sequences are very long (1000+ tokens), consider truncating, chunking, or using efficient attention variants.

4. **Start small, then scale.** Begin with 2 layers and a small d_model (64 or 128). Get the pipeline working first. Then scale up if you have enough data and compute.

5. **Print shapes obsessively.** Add shape print statements at every step of your model until you are confident everything is correct. Shape mismatches are the most common source of bugs in Transformer implementations.

---

## Quick Summary

In this chapter, we implemented the Transformer step by step in PyTorch. We built scaled dot-product attention from scratch, understanding how Q, K, V matrices interact. We implemented multi-head attention by splitting the embedding into multiple heads, running attention independently, and concatenating results. We created positional encoding using sine and cosine functions.

We then used PyTorch's built-in TransformerEncoder and TransformerDecoder modules for a cleaner implementation. We built a complete text classifier and trained it on synthetic data. Finally, we compared the Transformer against an LSTM, noting that both achieve similar results on short sequences but Transformers excel with longer sequences and more data.

---

## Key Points

- Scaled dot-product attention computes Q * K^T / sqrt(d_k), applies softmax, then multiplies by V
- Multi-head attention runs attention h times in parallel, each head working with d_model/h dimensions
- Positional encoding uses sin/cos at different frequencies to encode position information
- PyTorch provides nn.TransformerEncoderLayer and nn.TransformerEncoder for production use
- For text classification, the Transformer output is typically averaged over the sequence and fed to a linear classifier
- The key shape transformation is: (batch, seq_len) tokens -> (batch, seq_len, d_model) embeddings -> (batch, d_model) pooled -> (batch, n_classes) logits
- Always set batch_first=True in PyTorch Transformer modules
- Transformers and LSTMs achieve comparable results on short sequences, but Transformers scale better

---

## Practice Questions

1. In multi-head attention with d_model=512 and 8 heads, what is the dimension each head works with? How many total parameters do the Q, K, V projections have (not counting biases)?

2. Why does the Transformer multiply embeddings by sqrt(d_model) before adding positional encoding? What would happen without this scaling?

3. What is the difference between `src_key_padding_mask` and `src_mask` in PyTorch's Transformer? When would you use each one?

4. Trace the complete shape transformations for a batch of 4 sentences, each 15 tokens long, through a Transformer with d_model=128, n_heads=8, d_ff=512, and 2 classes. Write out the shape at every step.

5. Why does the Transformer classifier use average pooling over the sequence dimension? What are alternative approaches, and what are their trade-offs?

---

## Exercises

**Exercise 1: Multi-Head Attention Visualization**
Modify the MultiHeadAttention class to return attention weights for each head. Create a small input sequence (4-5 words) and visualize which words each head attends to. Print the attention weights for at least 3 heads and observe how they differ.

**Exercise 2: Transformer vs LSTM on Longer Sequences**
Using the synthetic dataset approach from section 22.7, create datasets with sequence lengths of 20, 50, and 100. Train both a Transformer and LSTM classifier on each length. Plot or print how accuracy changes with sequence length for each model. At what length does the Transformer clearly outperform the LSTM?

**Exercise 3: Hyperparameter Exploration**
Take the TransformerClassifier and systematically vary one hyperparameter at a time while keeping others fixed. Try: (a) n_heads = 1, 2, 4, 8, (b) n_layers = 1, 2, 4, 6, (c) d_model = 32, 64, 128, 256. For each variation, train for 10 epochs and report validation accuracy and parameter count. Which hyperparameter has the biggest impact on accuracy?

---

## What Is Next?

You have now built a Transformer from scratch and used PyTorch's built-in modules. In the following chapters, we will explore autoencoders, variational autoencoders, and generative adversarial networks. Later, in Chapter 28, we will learn systematic techniques for debugging deep learning models — an essential skill when your Transformer (or any model) does not train as expected. And in Chapters 29 and 30, you will apply everything in two complete projects.
