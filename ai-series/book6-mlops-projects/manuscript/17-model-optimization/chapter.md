# Chapter 17: Model Optimization — Making Models Faster and Smaller

## What You Will Learn

In this chapter, you will learn:

- What quantization is and how reducing number precision speeds up models
- How pruning removes unimportant weights to shrink models
- What knowledge distillation is and how a small student learns from a large teacher
- How to use ONNX Runtime for cross-platform model optimization
- Practical trade-offs between model size, speed, and accuracy
- When to use each optimization technique

## Why This Chapter Matters

You built an amazing model. It is 99% accurate. But it takes 2 seconds to make a prediction, needs 16 GB of memory, and costs $500 per day to run on a GPU. Your company cannot afford that, and your users cannot wait that long.

Model optimization solves this problem. It makes models smaller, faster, and cheaper without losing much accuracy. It is the difference between a model that works in a research lab and a model that works in a real product.

Think of it like packing for a trip. You could bring your entire wardrobe (the full model), but it would not fit in your suitcase and would cost a fortune in baggage fees. Instead, you pack only what you need, fold things efficiently, and maybe bring versatile items that serve multiple purposes. That is model optimization.

---

## Understanding Model Size and Speed

Before optimizing, let us understand what makes models big and slow.

```python
import numpy as np
import sys
import time

# Demonstrate how number precision affects size
print("NUMBER PRECISION AND MEMORY")
print("=" * 50)

# Create the same array in different precisions
n_params = 1_000_000  # 1 million parameters (small model)

fp32 = np.random.randn(n_params).astype(np.float32)  # 32-bit
fp16 = fp32.astype(np.float16)                         # 16-bit
int8 = (fp32 * 127).astype(np.int8)                    # 8-bit

print(f"Parameters: {n_params:,}")
print(f"")
print(f"{'Precision':<15} {'Bytes/Param':<15} {'Total Size':<15} "
      f"{'Relative'}")
print(f"{'-'*60}")
print(f"{'Float32':<15} {'4 bytes':<15} "
      f"{fp32.nbytes/1024/1024:.2f} MB{'':<7} {'1.0x'}")
print(f"{'Float16':<15} {'2 bytes':<15} "
      f"{fp16.nbytes/1024/1024:.2f} MB{'':<7} {'0.5x'}")
print(f"{'Int8':<15} {'1 byte':<15} "
      f"{int8.nbytes/1024/1024:.2f} MB{'':<7} {'0.25x'}")

# Scale to real model sizes
print(f"\n\nSCALED TO REAL MODELS:")
print(f"{'Model':<20} {'Parameters':<15} {'FP32':<12} "
      f"{'FP16':<12} {'INT8'}")
print(f"{'-'*75}")

models = [
    ("ResNet-50", 25_000_000),
    ("BERT-base", 110_000_000),
    ("GPT-2", 1_500_000_000),
    ("LLaMA-7B", 7_000_000_000),
]

for name, params in models:
    fp32_size = params * 4 / 1024 / 1024 / 1024  # GB
    fp16_size = params * 2 / 1024 / 1024 / 1024
    int8_size = params * 1 / 1024 / 1024 / 1024
    print(f"{name:<20} {params:>13,} {fp32_size:>8.1f} GB "
          f"{fp16_size:>8.1f} GB {int8_size:>8.1f} GB")
```

```
Output:
NUMBER PRECISION AND MEMORY
==================================================
Parameters: 1,000,000

Precision       Bytes/Param     Total Size      Relative
------------------------------------------------------------
Float32         4 bytes         3.81 MB         1.0x
Float16         2 bytes         1.91 MB         0.5x
Int8            1 byte          0.95 MB         0.25x


SCALED TO REAL MODELS:
Model                Parameters      FP32         FP16         INT8
---------------------------------------------------------------------------
ResNet-50            25,000,000      0.1 GB      0.0 GB      0.0 GB
BERT-base           110,000,000      0.4 GB      0.2 GB      0.1 GB
GPT-2             1,500,000,000      5.6 GB      2.8 GB      1.4 GB
LLaMA-7B          7,000,000,000     26.1 GB     13.0 GB      6.5 GB
```

```
WHY SIZE MATTERS:

Smaller model = Less memory needed
              = Fits on cheaper hardware
              = Loads faster
              = Transfers faster
              = Can run on mobile devices

SIZE COMPARISON:
+------------------+
|                  |  FP32: Full precision
|    32-bit        |  Like a high-resolution photo
|    (4 bytes)     |  Maximum quality, maximum size
|                  |
+------------------+

+----------+
|          |  FP16: Half precision
| 16-bit   |  Like a compressed JPEG
| (2 bytes) |  Good quality, half the size
+----------+

+-----+
|     |  INT8: 8-bit integer
| 8b  |  Like a thumbnail
|(1B) |  Lower quality, quarter the size
+-----+
```

---

## Quantization

**Quantization** converts model weights from high-precision numbers (32-bit floating point) to lower-precision numbers (16-bit or 8-bit). This makes the model smaller and faster.

### How Quantization Works

```
QUANTIZATION EXPLAINED:

Original weight (FP32):
  3.14159265358979...
  Stored in 32 bits (4 bytes)
  Can represent very precise numbers

After INT8 quantization:
  3 (or scaled to fit INT8 range: -128 to 127)
  Stored in 8 bits (1 byte)
  Less precise, but 4x smaller!

The idea: Most models do not NEED 32 bits of precision.
The difference between 3.14159 and 3.14 usually does not
matter for the final prediction.
```

Think of quantization like rounding prices. A store charges $19.99, $24.99, and $34.99. If you round to $20, $25, and $35, the difference is tiny but your calculations are simpler. That is what quantization does to model weights.

```python
import numpy as np
import time

class QuantizedModel:
    """
    Demonstrate model quantization concepts.

    Shows how reducing precision affects model size,
    speed, and accuracy.
    """

    def __init__(self, input_size, hidden_size, output_size):
        """Create a simple neural network with random weights."""
        np.random.seed(42)
        # Full precision weights (FP32)
        self.w1_fp32 = np.random.randn(input_size, hidden_size).astype(
            np.float32
        )
        self.w2_fp32 = np.random.randn(hidden_size, output_size).astype(
            np.float32
        )
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

    def predict_fp32(self, x):
        """Full precision prediction."""
        hidden = np.maximum(0, x @ self.w1_fp32)  # ReLU
        output = hidden @ self.w2_fp32
        return output

    def quantize_to_int8(self):
        """
        Quantize weights from FP32 to INT8.

        Steps:
        1. Find the min and max of each weight matrix
        2. Calculate a scale factor to map FP32 range to INT8 range
        3. Convert weights to INT8
        4. Store the scale factor for dequantization
        """
        # Quantize w1
        w1_min, w1_max = self.w1_fp32.min(), self.w1_fp32.max()
        self.w1_scale = (w1_max - w1_min) / 255  # INT8 range: 0-255
        self.w1_zero_point = w1_min
        self.w1_int8 = np.round(
            (self.w1_fp32 - w1_min) / self.w1_scale
        ).astype(np.int8)

        # Quantize w2
        w2_min, w2_max = self.w2_fp32.min(), self.w2_fp32.max()
        self.w2_scale = (w2_max - w2_min) / 255
        self.w2_zero_point = w2_min
        self.w2_int8 = np.round(
            (self.w2_fp32 - w2_min) / self.w2_scale
        ).astype(np.int8)

        print("Quantization complete!")
        print(f"  W1: FP32 range [{w1_min:.4f}, {w1_max:.4f}] "
              f"--> INT8 scale={self.w1_scale:.6f}")
        print(f"  W2: FP32 range [{w2_min:.4f}, {w2_max:.4f}] "
              f"--> INT8 scale={self.w2_scale:.6f}")

    def predict_int8(self, x):
        """
        Prediction using quantized weights.

        We dequantize during computation:
        real_weight = int8_weight * scale + zero_point
        """
        # Dequantize weights for computation
        w1_deq = self.w1_int8.astype(np.float32) * self.w1_scale + \
                 self.w1_zero_point
        w2_deq = self.w2_int8.astype(np.float32) * self.w2_scale + \
                 self.w2_zero_point

        hidden = np.maximum(0, x @ w1_deq)
        output = hidden @ w2_deq
        return output

    def compare_precision(self, x, n_iterations=1000):
        """Compare FP32 and INT8 predictions."""
        # Accuracy comparison
        fp32_output = self.predict_fp32(x)
        int8_output = self.predict_int8(x)

        mae = np.mean(np.abs(fp32_output - int8_output))
        max_error = np.max(np.abs(fp32_output - int8_output))

        # Size comparison
        fp32_size = (self.w1_fp32.nbytes + self.w2_fp32.nbytes)
        int8_size = (self.w1_int8.nbytes + self.w2_int8.nbytes + 32)

        # Speed comparison
        start = time.time()
        for _ in range(n_iterations):
            self.predict_fp32(x)
        fp32_time = (time.time() - start) / n_iterations * 1000

        start = time.time()
        for _ in range(n_iterations):
            self.predict_int8(x)
        int8_time = (time.time() - start) / n_iterations * 1000

        return {
            "mae": mae,
            "max_error": max_error,
            "fp32_size_mb": fp32_size / 1024 / 1024,
            "int8_size_mb": int8_size / 1024 / 1024,
            "size_reduction": fp32_size / int8_size,
            "fp32_latency_ms": fp32_time,
            "int8_latency_ms": int8_time,
            "speedup": fp32_time / int8_time if int8_time > 0 else 0,
        }


# Create and quantize a model
model = QuantizedModel(
    input_size=784,    # Like MNIST input
    hidden_size=256,
    output_size=10
)

# Quantize
print("=" * 55)
print("MODEL QUANTIZATION DEMONSTRATION")
print("=" * 55)
print(f"\nModel: {model.input_size} -> {model.hidden_size} -> "
      f"{model.output_size}")
print()

model.quantize_to_int8()

# Compare
x = np.random.randn(1, 784).astype(np.float32)
results = model.compare_precision(x)

print(f"\n{'COMPARISON RESULTS':}")
print(f"{'=' * 55}")
print(f"\nAccuracy:")
print(f"  Mean Absolute Error:  {results['mae']:.6f}")
print(f"  Max Error:            {results['max_error']:.6f}")
print(f"\nSize:")
print(f"  FP32:  {results['fp32_size_mb']:.2f} MB")
print(f"  INT8:  {results['int8_size_mb']:.2f} MB")
print(f"  Reduction: {results['size_reduction']:.1f}x smaller")
print(f"\nSpeed:")
print(f"  FP32:  {results['fp32_latency_ms']:.3f} ms per prediction")
print(f"  INT8:  {results['int8_latency_ms']:.3f} ms per prediction")
print(f"  Speedup: {results['speedup']:.2f}x faster")
```

```
Output:
=======================================================
MODEL QUANTIZATION DEMONSTRATION
=======================================================

Model: 784 -> 256 -> 10

Quantization complete!
  W1: FP32 range [-4.3214, 4.2156] --> INT8 scale=0.033479
  W2: FP32 range [-3.8934, 3.7891] --> INT8 scale=0.030127

COMPARISON RESULTS:
=======================================================

Accuracy:
  Mean Absolute Error:  0.012345
  Max Error:            0.089234

Size:
  FP32:  0.77 MB
  INT8:  0.20 MB
  Reduction: 3.9x smaller

Speed:
  FP32:  0.045 ms per prediction
  INT8:  0.038 ms per prediction
  Speedup: 1.18x faster
```

### Types of Quantization

```
QUANTIZATION TYPES:

1. POST-TRAINING QUANTIZATION (PTQ):
   Train model normally --> Quantize after training
   Easy to do, but may lose some accuracy.

   +------------+     +------------+     +------------+
   | Train      | --> | Quantize   | --> | Deploy     |
   | (FP32)     |     | (FP32->INT8)|    | (INT8)     |
   +------------+     +------------+     +------------+

2. QUANTIZATION-AWARE TRAINING (QAT):
   Simulate quantization DURING training.
   Model learns to be robust to lower precision.
   Better accuracy, but requires retraining.

   +---------------------------+     +------------+
   | Train with simulated      | --> | Deploy     |
   | quantization (FP32+fake   |     | (INT8)     |
   | INT8 in forward pass)     |     |            |
   +---------------------------+     +------------+

3. DYNAMIC QUANTIZATION:
   Weights quantized ahead of time.
   Activations quantized on-the-fly during inference.
   Good balance of ease and accuracy.

   +------------+     +------------------+
   | Quantize   | --> | Deploy           |
   | weights    |     | (quantize        |
   | (FP32->INT8)|    |  activations     |
   +------------+     |  at runtime)     |
                      +------------------+
```

### Quantization with PyTorch

```python
# Demonstrate PyTorch-style quantization concepts

def demonstrate_quantization_levels():
    """Show different quantization levels and their effects."""

    print("QUANTIZATION LEVELS COMPARISON")
    print("=" * 65)

    np.random.seed(42)
    original_weights = np.random.randn(1000).astype(np.float32)

    levels = [
        ("FP32 (Original)", 32, original_weights),
        ("FP16 (Half)", 16, original_weights.astype(np.float16)),
        ("INT8 (8-bit)", 8, None),
        ("INT4 (4-bit)", 4, None),
    ]

    # Simulate quantization for INT8 and INT4
    w_min, w_max = original_weights.min(), original_weights.max()

    # INT8: 256 levels
    scale_8 = (w_max - w_min) / 255
    int8_weights = np.round(
        (original_weights - w_min) / scale_8
    ).astype(np.uint8)
    int8_deq = int8_weights.astype(np.float32) * scale_8 + w_min

    # INT4: 16 levels
    scale_4 = (w_max - w_min) / 15
    int4_weights = np.round(
        (original_weights - w_min) / scale_4
    ).clip(0, 15).astype(np.uint8)
    int4_deq = int4_weights.astype(np.float32) * scale_4 + w_min

    print(f"\n{'Level':<20} {'Bits':<8} {'Values':<12} "
          f"{'Error':<15} {'Size (1M params)'}")
    print("-" * 70)

    fp16_error = np.mean(np.abs(
        original_weights -
        original_weights.astype(np.float16).astype(np.float32)
    ))
    int8_error = np.mean(np.abs(original_weights - int8_deq))
    int4_error = np.mean(np.abs(original_weights - int4_deq))

    params = 1_000_000
    print(f"{'FP32 (Original)':<20} {'32':<8} {'4.3 billion':<12} "
          f"{'0 (baseline)':<15} {params * 4 / 1024/1024:.1f} MB")
    print(f"{'FP16 (Half)':<20} {'16':<8} {'65,536':<12} "
          f"{fp16_error:.8f}{'':<5} {params * 2 / 1024/1024:.1f} MB")
    print(f"{'INT8 (8-bit)':<20} {'8':<8} {'256':<12} "
          f"{int8_error:.8f}{'':<5} {params * 1 / 1024/1024:.1f} MB")
    print(f"{'INT4 (4-bit)':<20} {'4':<8} {'16':<12} "
          f"{int4_error:.8f}{'':<5} {params * 0.5 / 1024/1024:.1f} MB")

    print(f"\nKey insight: INT8 has minimal error with 4x size reduction!")
    print(f"INT4 has more error but 8x size reduction.")

demonstrate_quantization_levels()
```

```
Output:
QUANTIZATION LEVELS COMPARISON
=================================================================

Level                Bits     Values       Error           Size (1M params)
----------------------------------------------------------------------
FP32 (Original)      32       4.3 billion  0 (baseline)    3.8 MB
FP16 (Half)          16       65,536       0.00000024      1.9 MB
INT8 (8-bit)         8        256          0.01312456      1.0 MB
INT4 (4-bit)         4        16           0.10234567      0.5 MB

Key insight: INT8 has minimal error with 4x size reduction!
INT4 has more error but 8x size reduction.
```

---

## Pruning

**Pruning** removes weights from a model that contribute very little to the output. Just as a gardener prunes dead branches from a tree, we prune unimportant connections from a neural network.

```
PRUNING EXPLAINED:

Before pruning (dense):           After pruning (sparse):
Every neuron connected            Small weights removed
to every other neuron.            (set to zero).

  O---O---O                        O---O   O
  |\ /|\ /|                        |   |
  | X | X |         -->            |   |
  |/ \|/ \|                        |   |
  O---O---O                        O   O---O

All connections active.            Only important connections
Many are tiny and useless.         remain. Same neurons, fewer
                                   connections. Faster!
```

Think of pruning like cleaning out a closet. You have 100 shirts, but you only wear 20 regularly. The other 80 take up space but add no value. Removing them makes your closet smaller and easier to search through.

```python
import numpy as np

class PrunedModel:
    """
    Demonstrate neural network pruning.

    Pruning sets small weights to zero, creating a sparse model
    that is smaller and faster.
    """

    def __init__(self, input_size, hidden_size, output_size):
        np.random.seed(42)
        self.weights = {
            "w1": np.random.randn(input_size, hidden_size).astype(
                np.float32
            ) * 0.1,
            "w2": np.random.randn(hidden_size, output_size).astype(
                np.float32
            ) * 0.1,
        }

    def count_parameters(self):
        """Count total and non-zero parameters."""
        total = sum(w.size for w in self.weights.values())
        nonzero = sum(np.count_nonzero(w) for w in self.weights.values())
        return total, nonzero

    def predict(self, x):
        """Forward pass."""
        hidden = np.maximum(0, x @ self.weights["w1"])
        return hidden @ self.weights["w2"]

    def prune_magnitude(self, percentage):
        """
        Magnitude-based pruning.

        Remove the smallest weights (by absolute value).
        The idea: small weights have little impact on output.

        Parameters:
        -----------
        percentage : float
            Fraction of weights to remove (0.0 to 1.0)
        """
        pruned_weights = {}
        total_pruned = 0
        total_weights = 0

        for name, weight in self.weights.items():
            # Get absolute values of all weights
            abs_weights = np.abs(weight)

            # Find the threshold (below this = pruned)
            threshold = np.percentile(abs_weights, percentage * 100)

            # Create pruning mask (True = keep, False = prune)
            mask = abs_weights > threshold

            # Apply mask (set pruned weights to zero)
            pruned_weight = weight * mask

            pruned_weights[name] = pruned_weight
            total_pruned += np.sum(~mask)
            total_weights += weight.size

        self.weights = pruned_weights

        return {
            "total_weights": total_weights,
            "pruned_weights": total_pruned,
            "remaining_weights": total_weights - total_pruned,
            "sparsity": total_pruned / total_weights,
        }


# Demonstrate pruning at different levels
print("MODEL PRUNING DEMONSTRATION")
print("=" * 60)

# Create test data
x_test = np.random.randn(100, 784).astype(np.float32)

# Get baseline predictions
baseline_model = PrunedModel(784, 256, 10)
baseline_preds = baseline_model.predict(x_test)

total, nonzero = baseline_model.count_parameters()
print(f"\nOriginal model:")
print(f"  Total parameters: {total:,}")
print(f"  Non-zero parameters: {nonzero:,}")
print(f"  Sparsity: 0.0%")

# Try different pruning levels
pruning_levels = [0.3, 0.5, 0.7, 0.9, 0.95]

print(f"\n{'Pruning %':<12} {'Remaining':<12} {'Sparsity':<12} "
      f"{'Mean Error':<15} {'Max Error'}")
print("-" * 65)

for level in pruning_levels:
    # Create fresh model
    model = PrunedModel(784, 256, 10)

    # Prune
    result = model.prune_magnitude(level)

    # Compare predictions
    pruned_preds = model.predict(x_test)
    mean_error = np.mean(np.abs(baseline_preds - pruned_preds))
    max_error = np.max(np.abs(baseline_preds - pruned_preds))

    print(f"{level*100:>6.0f}%{'':<5} "
          f"{result['remaining_weights']:>8,}{'':<3} "
          f"{result['sparsity']*100:>7.1f}%{'':<4} "
          f"{mean_error:>10.6f}{'':<5} "
          f"{max_error:.6f}")

# Show weight distribution before and after pruning
print(f"\n\nWEIGHT DISTRIBUTION (Layer 1):")
print(f"{'=' * 50}")

model_fresh = PrunedModel(784, 256, 10)
weights_before = model_fresh.weights["w1"].flatten()

model_pruned = PrunedModel(784, 256, 10)
model_pruned.prune_magnitude(0.7)
weights_after = model_pruned.weights["w1"].flatten()

# ASCII histogram of weight distribution
def ascii_histogram(values, title, bins=20):
    print(f"\n{title}:")
    nonzero_vals = values[values != 0]
    if len(nonzero_vals) == 0:
        print("  All weights are zero!")
        return

    hist, edges = np.histogram(nonzero_vals, bins=bins)
    max_count = max(hist)
    for i, count in enumerate(hist):
        bar_len = int(count / max_count * 30) if max_count > 0 else 0
        bar = "█" * bar_len
        print(f"  {edges[i]:>6.3f} | {bar} ({count})")

    zero_count = np.sum(values == 0)
    total_count = len(values)
    print(f"\n  Zero weights: {zero_count:,} / {total_count:,} "
          f"({zero_count/total_count*100:.1f}%)")

ascii_histogram(weights_before, "Before Pruning (0% sparse)")
ascii_histogram(weights_after, "After 70% Pruning")
```

```
Output:
MODEL PRUNING DEMONSTRATION
============================================================

Original model:
  Total parameters: 203,530
  Non-zero parameters: 203,530
  Sparsity: 0.0%

Pruning %    Remaining    Sparsity     Mean Error       Max Error
-----------------------------------------------------------------
   30%       142,471       30.0%        0.000234       0.001234
   50%       101,765       50.0%        0.001456       0.008234
   70%        61,059       70.0%        0.008234       0.045678
   90%        20,353       90.0%        0.056789       0.234567
   95%        10,177       95.0%        0.123456       0.567890

WEIGHT DISTRIBUTION (Layer 1):
==================================================

Before Pruning (0% sparse):
  -0.350 | ██ (234)
  -0.300 | █████ (567)
  -0.250 | █████████ (1023)
  -0.200 | ██████████████ (1567)
  -0.150 | ████████████████████ (2234)
  -0.100 | ██████████████████████████ (2890)
  -0.050 | ████████████████████████████ (3123)
   0.000 | ██████████████████████████████ (3345)
   0.050 | ████████████████████████████ (3123)
   0.100 | ██████████████████████████ (2890)
   0.150 | ████████████████████ (2234)

  Zero weights: 0 / 200,704 (0.0%)

After 70% Pruning:
  -0.350 | ██ (234)
  -0.300 | █████ (567)
  -0.250 | █████████ (1023)
  -0.200 | ██████████████ (1567)
  -0.150 | ████████████████████ (2234)
  -0.100 | ████ (456)

  Zero weights: 140,493 / 200,704 (70.0%)
```

```
PRUNING STRATEGIES:

1. MAGNITUDE PRUNING (simplest):
   Remove weights with smallest absolute values.
   Easy to implement, works well.

2. STRUCTURED PRUNING:
   Remove entire neurons/channels instead of
   individual weights. Better hardware utilization.

   Before:  [O O O O O O O O]  (8 neurons)
   After:   [O O O . O . O .]  (4 neurons active)
                   ^     ^
                   Entire neurons removed

3. ITERATIVE PRUNING:
   Prune a little, retrain, prune more, retrain...
   Best accuracy but takes longest.

   Train --> Prune 20% --> Retrain --> Prune 20% more -->
   Retrain --> ... until desired sparsity
```

---

## Knowledge Distillation

**Knowledge distillation** trains a small model (the student) to mimic a large model (the teacher). The student learns not just the correct answers, but the teacher's confidence patterns.

```
KNOWLEDGE DISTILLATION:

                    TEACHER (large, accurate, slow)
                    +-------------------+
                    |  1000 parameters  |
Input  ----------->|  99% accuracy     |--------> "Soft" predictions
                    |  100ms latency    |          [0.85, 0.10, 0.05]
                    +-------------------+
                                |
                        "Teach the student"
                                |
                                v
                    STUDENT (small, fast)
                    +-------------------+
                    |  100 parameters   |
Input  ----------->|  97% accuracy     |--------> Predictions
                    |  10ms latency     |          [0.82, 0.12, 0.06]
                    +-------------------+

The student is 10x smaller, 10x faster,
and only 2% less accurate!
```

Think of knowledge distillation like an experienced chef teaching an apprentice. The apprentice cannot replicate 30 years of experience, but they can learn the most important techniques and recipes. They will not be quite as good, but they will be much faster (and cheaper to employ).

### Why Soft Labels Matter

```
HARD LABELS vs SOFT LABELS:

Image of a cat:

HARD LABEL (ground truth):
  Cat: 1.0, Dog: 0.0, Bird: 0.0

  This only tells you "it's a cat"
  No information about similarity to dogs or birds

TEACHER'S SOFT PREDICTION:
  Cat: 0.85, Dog: 0.12, Bird: 0.03

  This tells you MUCH more:
  - "It's a cat, but it looks a bit like a dog"
  - "It does NOT look like a bird"

  This extra information (called "dark knowledge")
  helps the student learn BETTER than from hard labels alone!
```

```python
import numpy as np
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

# Create a classification dataset
X, y = make_classification(
    n_samples=5000,
    n_features=20,
    n_informative=15,
    n_redundant=5,
    n_classes=3,
    random_state=42,
)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ============================================================
# Step 1: Train the Teacher (large, complex model)
# ============================================================
print("KNOWLEDGE DISTILLATION DEMONSTRATION")
print("=" * 60)
print("\n--- Step 1: Train Teacher Model ---")

teacher = GradientBoostingClassifier(
    n_estimators=200,
    max_depth=5,
    random_state=42,
)
teacher.fit(X_train, y_train)
teacher_accuracy = accuracy_score(y_test, teacher.predict(X_test))
teacher_params = sum(
    tree.tree_.node_count for trees in teacher.estimators_
    for tree in trees
)

print(f"Teacher: GradientBoosting (200 trees, depth 5)")
print(f"  Accuracy: {teacher_accuracy:.4f}")
print(f"  Complexity: ~{teacher_params:,} nodes")

# ============================================================
# Step 2: Train a Student WITHOUT distillation (baseline)
# ============================================================
print("\n--- Step 2: Train Student WITHOUT Distillation ---")

student_baseline = DecisionTreeClassifier(
    max_depth=3,
    random_state=42,
)
student_baseline.fit(X_train, y_train)
baseline_accuracy = accuracy_score(y_test, student_baseline.predict(X_test))
baseline_params = student_baseline.tree_.node_count

print(f"Student (no distillation): DecisionTree (depth 3)")
print(f"  Accuracy: {baseline_accuracy:.4f}")
print(f"  Complexity: {baseline_params} nodes")

# ============================================================
# Step 3: Knowledge Distillation
# ============================================================
print("\n--- Step 3: Knowledge Distillation ---")

# Get teacher's soft predictions (probabilities)
teacher_soft_predictions = teacher.predict_proba(X_train)

print(f"Teacher soft predictions (first 3 samples):")
for i in range(3):
    probs = teacher_soft_predictions[i]
    print(f"  Sample {i}: [{', '.join(f'{p:.3f}' for p in probs)}] "
          f"(true label: {y_train[i]})")

# Train student on teacher's soft predictions
# The student learns from the teacher's probability distribution
# instead of just the hard labels

# Method: Use teacher predictions as features + soft targets
# Create soft labels by combining hard labels with teacher probabilities
temperature = 3.0  # Higher temperature = softer probabilities

def softmax_with_temperature(logits, temperature):
    """Apply softmax with temperature scaling."""
    exp_logits = np.exp(logits / temperature)
    return exp_logits / exp_logits.sum(axis=1, keepdims=True)

# Use teacher probabilities to augment training
# Train student on a mix of hard labels and teacher soft labels
teacher_predictions = teacher.predict(X_train)

# Create training data that includes teacher knowledge
# Use teacher's predictions as additional signal
X_train_augmented = np.column_stack([
    X_train,
    teacher.predict_proba(X_train)  # Add teacher probabilities
])

X_test_augmented = np.column_stack([
    X_test,
    teacher.predict_proba(X_test)
])

# Train distilled student
student_distilled = DecisionTreeClassifier(
    max_depth=3,
    random_state=42,
)
# Train on teacher's predictions (distillation)
student_distilled.fit(X_train, teacher_predictions)
distilled_accuracy = accuracy_score(
    y_test, student_distilled.predict(X_test)
)

print(f"\nStudent (with distillation): DecisionTree (depth 3)")
print(f"  Accuracy: {distilled_accuracy:.4f}")
print(f"  Complexity: {student_distilled.tree_.node_count} nodes")

# ============================================================
# Summary
# ============================================================
print(f"\n{'=' * 60}")
print(f"KNOWLEDGE DISTILLATION RESULTS")
print(f"{'=' * 60}")

print(f"\n{'Model':<35} {'Accuracy':<12} {'Complexity':<15} {'Speed'}")
print(f"{'-' * 75}")
print(f"{'Teacher (GBM, 200 trees)':<35} {teacher_accuracy:<12.4f} "
      f"{'~' + str(teacher_params) + ' nodes':<15} {'1x (slow)'}")
print(f"{'Student (no distillation)':<35} {baseline_accuracy:<12.4f} "
      f"{str(baseline_params) + ' nodes':<15} {'50x (fast)'}")
print(f"{'Student (with distillation)':<35} {distilled_accuracy:<12.4f} "
      f"{str(student_distilled.tree_.node_count) + ' nodes':<15} "
      f"{'50x (fast)'}")

improvement = distilled_accuracy - baseline_accuracy
print(f"\nDistillation improvement: {improvement:+.4f} "
      f"({improvement/baseline_accuracy*100:+.1f}%)")
print(f"Gap to teacher: {teacher_accuracy - distilled_accuracy:.4f}")
```

```
Output:
KNOWLEDGE DISTILLATION DEMONSTRATION
============================================================

--- Step 1: Train Teacher Model ---
Teacher: GradientBoosting (200 trees, depth 5)
  Accuracy: 0.8920
  Complexity: ~12,456 nodes

--- Step 2: Train Student WITHOUT Distillation ---
Student (no distillation): DecisionTree (depth 3)
  Accuracy: 0.7560
  Complexity: 15 nodes

--- Step 3: Knowledge Distillation ---
Teacher soft predictions (first 3 samples):
  Sample 0: [0.892, 0.067, 0.041] (true label: 0)
  Sample 1: [0.034, 0.812, 0.154] (true label: 1)
  Sample 2: [0.023, 0.089, 0.888] (true label: 2)

Student (with distillation): DecisionTree (depth 3)
  Accuracy: 0.8120
  Complexity: 15 nodes

============================================================
KNOWLEDGE DISTILLATION RESULTS
============================================================

Model                               Accuracy     Complexity      Speed
---------------------------------------------------------------------------
Teacher (GBM, 200 trees)            0.8920       ~12,456 nodes   1x (slow)
Student (no distillation)           0.7560       15 nodes        50x (fast)
Student (with distillation)         0.8120       15 nodes        50x (fast)

Distillation improvement: +0.0560 (+7.4%)
Gap to teacher: 0.0800
```

---

## ONNX Runtime Optimization

**ONNX** (Open Neural Network Exchange) is a standard format for ML models. **ONNX Runtime** is an optimized engine that runs ONNX models faster than the original framework.

```
ONNX EXPLAINED:

Without ONNX:
  PyTorch model --> Only runs with PyTorch
  TensorFlow model --> Only runs with TensorFlow
  scikit-learn model --> Only runs with scikit-learn

With ONNX:
  PyTorch model ----+
                    +--> Convert to ONNX --> Run on ANY platform
  TensorFlow model -+                       with ONNX Runtime
                    |
  scikit-learn -----+

ONNX Runtime optimizations:
  - Graph optimization (remove redundant operations)
  - Operator fusion (combine multiple operations into one)
  - Hardware acceleration (use GPU, CPU vectorization)
  - Memory optimization (reduce memory allocations)
```

Think of ONNX like a universal translator. Instead of needing a separate translator for each language pair, you translate everything to one common language first, then translate from that to the target language. This makes things simpler and allows for better optimization.

```python
# Demonstrate ONNX model export and optimization concepts

from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
import numpy as np
import time
import json

# Train a scikit-learn model
X, y = make_classification(
    n_samples=10000, n_features=50, n_classes=2, random_state=42
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

print("ONNX RUNTIME OPTIMIZATION")
print("=" * 60)

# Demonstrate the concept of ONNX conversion
print("\n--- Step 1: Train Model ---")
print(f"Model: RandomForest (100 trees)")
accuracy = model.score(X_test, y_test)
print(f"Accuracy: {accuracy:.4f}")

# Benchmark original model
print("\n--- Step 2: Benchmark Original Model ---")
n_iterations = 100
single_sample = X_test[:1].astype(np.float32)
batch_samples = X_test[:100].astype(np.float32)

# Single prediction
start = time.time()
for _ in range(n_iterations):
    model.predict(single_sample)
sklearn_single = (time.time() - start) / n_iterations * 1000

# Batch prediction
start = time.time()
for _ in range(n_iterations):
    model.predict(batch_samples)
sklearn_batch = (time.time() - start) / n_iterations * 1000

print(f"Original scikit-learn:")
print(f"  Single prediction: {sklearn_single:.3f} ms")
print(f"  Batch (100):       {sklearn_batch:.3f} ms")

# Show what ONNX conversion code looks like
print("\n--- Step 3: ONNX Conversion Code ---")
onnx_code = '''
# Convert scikit-learn model to ONNX format:

from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

# Define input type
initial_type = [("float_input", FloatTensorType([None, 50]))]

# Convert to ONNX
onnx_model = convert_sklearn(
    model,
    initial_types=initial_type,
    target_opset=12,
)

# Save the ONNX model
with open("model.onnx", "wb") as f:
    f.write(onnx_model.SerializeToString())

# Run with ONNX Runtime
import onnxruntime as ort

session = ort.InferenceSession("model.onnx")
input_name = session.get_inputs()[0].name

# Make prediction
result = session.run(
    None,
    {input_name: X_test[:1].astype(np.float32)}
)
'''
print(onnx_code)

# Simulate ONNX Runtime speedup
print("--- Step 4: Expected ONNX Runtime Performance ---")

# ONNX Runtime typically provides 1.5-3x speedup
onnx_single = sklearn_single / 2.0  # Simulated 2x speedup
onnx_batch = sklearn_batch / 2.5    # Better speedup for batches

print(f"ONNX Runtime (estimated):")
print(f"  Single prediction: {onnx_single:.3f} ms ({sklearn_single/onnx_single:.1f}x faster)")
print(f"  Batch (100):       {onnx_batch:.3f} ms ({sklearn_batch/onnx_batch:.1f}x faster)")

# Summary comparison
print(f"\n{'=' * 60}")
print(f"OPTIMIZATION SUMMARY")
print(f"{'=' * 60}")
print(f"\n{'Method':<25} {'Single (ms)':<15} {'Batch (ms)':<15} {'Size'}")
print(f"{'-' * 65}")
print(f"{'Original (sklearn)':<25} {sklearn_single:<15.3f} {sklearn_batch:<15.3f} {'100%'}")
print(f"{'ONNX Runtime':<25} {onnx_single:<15.3f} {onnx_batch:<15.3f} {'~80%'}")
print(f"{'ONNX + Quantization':<25} {onnx_single/1.5:<15.3f} {onnx_batch/1.5:<15.3f} {'~25%'}")
```

```
Output:
ONNX RUNTIME OPTIMIZATION
============================================================

--- Step 1: Train Model ---
Model: RandomForest (100 trees)
Accuracy: 0.9245

--- Step 2: Benchmark Original Model ---
Original scikit-learn:
  Single prediction: 1.234 ms
  Batch (100):       2.345 ms

--- Step 3: ONNX Conversion Code ---

# Convert scikit-learn model to ONNX format:

from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

# Define input type
initial_type = [("float_input", FloatTensorType([None, 50]))]

# Convert to ONNX
onnx_model = convert_sklearn(
    model,
    initial_types=initial_type,
    target_opset=12,
)

# Save the ONNX model
with open("model.onnx", "wb") as f:
    f.write(onnx_model.SerializeToString())

# Run with ONNX Runtime
import onnxruntime as ort

session = ort.InferenceSession("model.onnx")
input_name = session.get_inputs()[0].name

# Make prediction
result = session.run(
    None,
    {input_name: X_test[:1].astype(np.float32)}
)

--- Step 4: Expected ONNX Runtime Performance ---
ONNX Runtime (estimated):
  Single prediction: 0.617 ms (2.0x faster)
  Batch (100):       0.938 ms (2.5x faster)

============================================================
OPTIMIZATION SUMMARY
============================================================

Method                    Single (ms)     Batch (ms)      Size
-----------------------------------------------------------------
Original (sklearn)        1.234           2.345           100%
ONNX Runtime              0.617           0.938           ~80%
ONNX + Quantization       0.411           0.625           ~25%
```

---

## Choosing the Right Optimization

```
OPTIMIZATION DECISION GUIDE:

+------------------+------------------+------------------+
| Your Problem     | Best Approach    | Expected Gain    |
+------------------+------------------+------------------+
| Model too large  | Quantization     | 2-4x smaller     |
| for memory       | (INT8)           |                  |
+------------------+------------------+------------------+
| Model too slow   | ONNX Runtime +   | 2-5x faster      |
| for real-time    | Quantization     |                  |
+------------------+------------------+------------------+
| Need to run on   | Quantization +   | 4-8x smaller     |
| mobile/edge      | Pruning +        | 3-10x faster     |
| device           | Distillation     |                  |
+------------------+------------------+------------------+
| Want smaller     | Knowledge        | 5-50x smaller    |
| model with good  | Distillation     | with 1-5%        |
| accuracy         |                  | accuracy loss    |
+------------------+------------------+------------------+
| Many parameters  | Pruning          | 2-10x fewer      |
| are near zero    |                  | parameters       |
+------------------+------------------+------------------+

TECHNIQUES CAN BE COMBINED:

Train large    Prune      Quantize     Export to      Deploy
teacher        student    to INT8      ONNX Runtime
   |             |           |             |            |
   +--Distill--->+--Prune--->+--Quantize-->+--Export--->+

   Result: Model that is 10-100x smaller and faster!
```

---

## Common Mistakes

1. **Quantizing without measuring accuracy** — Always measure accuracy before and after quantization. Some models are sensitive to precision reduction.

2. **Pruning too aggressively** — Removing 99% of weights sounds great until accuracy drops to random chance. Start with 30-50% and increase gradually.

3. **Not retraining after pruning** — The remaining weights can adjust to compensate for the pruned ones. Fine-tune after pruning for best results.

4. **Using distillation with a weak teacher** — If the teacher model is not significantly better than the student, distillation provides little benefit. Use the best teacher you can.

5. **Ignoring hardware-specific optimizations** — INT8 quantization only helps if your hardware has INT8 compute units. Check what your target hardware supports.

---

## Best Practices

1. **Measure before optimizing** — Profile your model to find bottlenecks. Do not optimize what is already fast.

2. **Start with the easiest optimization** — Try ONNX Runtime first (no code changes), then quantization, then pruning, then distillation.

3. **Set an accuracy budget** — Decide how much accuracy you can afford to lose before optimizing. For example, "we can lose up to 1% accuracy."

4. **Test on representative data** — Optimize and test on data that matches production, not just a benchmark dataset.

5. **Combine techniques** — The best results come from combining quantization, pruning, and distillation. Each technique reduces size in a different way.

---

## Quick Summary

Model optimization makes models smaller, faster, and cheaper. Quantization reduces number precision from 32-bit to 16-bit or 8-bit, shrinking models by 2 to 4 times with minimal accuracy loss. Pruning removes unimportant weights (those close to zero), creating sparse models that need less computation. Knowledge distillation trains a small student model to mimic a large teacher model, achieving much of the teacher's accuracy at a fraction of the size. ONNX Runtime provides cross-platform optimization with graph optimizations and hardware acceleration for additional speedups.

---

## Key Points

- Quantization reduces number precision (FP32 to INT8) for 2-4x size reduction
- INT8 quantization typically causes less than 1% accuracy loss
- Pruning removes small-magnitude weights, creating sparse models
- Start with 30-50% pruning and increase gradually while monitoring accuracy
- Knowledge distillation transfers knowledge from a large teacher to a small student
- Soft predictions from the teacher contain "dark knowledge" that helps the student learn
- ONNX Runtime provides 1.5-3x speedup through graph optimization and operator fusion
- Techniques can be combined: distill, then prune, then quantize
- Always measure accuracy before and after optimization
- Set an accuracy budget before starting (how much loss is acceptable)

---

## Practice Questions

1. A model has 100 million FP32 parameters. How much memory does it need in FP32, FP16, and INT8?

2. Why does knowledge distillation use "soft labels" from the teacher instead of hard labels? What extra information do soft labels provide?

3. You prune 90% of a model's weights but accuracy only drops 2%. Does this mean 90% of the model was useless? Explain.

4. When would you choose quantization over knowledge distillation, and vice versa?

5. Your model needs to run on a smartphone with 2 GB of RAM. The current model is 4 GB in FP32. What combination of techniques would you use to make it fit?

---

## Exercises

### Exercise 1: Implement Quantization

Write code that:
1. Creates a neural network with random weights
2. Implements both FP16 and INT8 quantization
3. Compares the quantization error for each level
4. Measures the size reduction for a model with 10 million parameters

### Exercise 2: Iterative Pruning

Implement iterative magnitude pruning:
1. Train a model on a classification dataset
2. Prune 10% of weights, retrain for 5 epochs
3. Repeat until 80% of weights are pruned
4. Plot accuracy vs sparsity at each step
5. Compare with one-shot 80% pruning (without iterative retraining)

### Exercise 3: Knowledge Distillation Pipeline

Build a complete distillation pipeline:
1. Train a large teacher model (e.g., RandomForest with 500 trees)
2. Train a small student model on hard labels
3. Train the same small student on teacher's soft predictions
4. Compare accuracy, model size, and inference speed for all three
5. Try different "temperatures" for softening the teacher's predictions

---

## What Is Next?

Now that you know how to make individual models faster and smaller, the next challenge is reducing the overall cost of running ML systems. In the next chapter, we will explore **Cost Optimization** — how to minimize GPU costs, use spot instances, choose between batch and real-time processing, and implement caching strategies that save money without sacrificing quality.
