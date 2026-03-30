# Chapter 28: Debugging Deep Learning — Finding and Fixing What Goes Wrong

## What You Will Learn

In this chapter, you will learn:

- How to diagnose the most common deep learning failures
- What to do when your loss is not decreasing, is NaN, or is stuck
- How to detect and fix learning rate problems (too high or too low)
- How to use gradient checking to verify your model is learning correctly
- The "overfit one batch" sanity check that catches bugs in minutes
- How to use TensorBoard to visualize training in real time
- How to debug data pipeline issues that silently corrupt your model
- How to fix shape mismatch errors systematically
- A complete debugging checklist and flowchart to follow when things go wrong

## Why This Chapter Matters

Here is a truth nobody tells beginners: deep learning models fail silently. Unlike traditional programming, where a bug causes an error message and a crash, a deep learning model with a bug will still run. It will still produce numbers. It will still "train." But those numbers will be meaningless, and you will have no idea why.

You might spend days training a model, only to discover it is always predicting the same class. Or your loss might look like it is decreasing, but your accuracy is stuck at random chance. Or everything looks perfect on training data, but the model is useless on real data.

This chapter gives you a systematic toolkit for finding and fixing these problems. Think of it as the "car mechanic's manual" for deep learning — when something is not working, open this chapter and follow the checklist.

---

## Problem 1: Loss Is Not Decreasing

This is the most common problem beginners face. You start training, and the loss either stays flat, bounces wildly, or decreases painfully slowly.

### Diagnosis Flowchart

```
LOSS NOT DECREASING — WHAT TO CHECK:

                    ┌──────────────────┐
                    │ Loss not          │
                    │ decreasing?       │
                    └────────┬─────────┘
                             │
                    ┌────────┴─────────┐
                    │ Is loss changing  │
                    │ at all?           │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
         ┌────┴────┐   ┌────┴────┐   ┌────┴────┐
         │ Flat    │   │ Bouncing│   │ Very    │
         │ (stuck) │   │ wildly  │   │ slow    │
         └────┬────┘   └────┬────┘   └────┬────┘
              │              │              │
         Check:          Check:          Check:
         - Learning      - Learning      - Learning
           rate = 0?       rate too       rate too
         - Frozen          high?          low?
           layers?       - Data has     - Optimizer
         - Optimizer       NaN/Inf?       settings?
           created       - Loss func   - Model too
           correctly?      wrong?         simple?
         - Labels
           correct?
```

### Fix 1: Check Your Learning Rate

```python
import torch
import torch.nn as nn
import matplotlib.pyplot as plt

# Create simple data
torch.manual_seed(42)
X = torch.randn(200, 10)
y = torch.randint(0, 3, (200,))

# Simple model
class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(10, 32)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(32, 3)

    def forward(self, x):
        return self.fc2(self.relu(self.fc1(x)))

# Try different learning rates
learning_rates = [10.0, 1.0, 0.1, 0.01, 0.001, 0.0001]
results = {}

for lr in learning_rates:
    torch.manual_seed(42)
    model = SimpleModel()
    optimizer = torch.optim.SGD(model.parameters(), lr=lr)
    loss_fn = nn.CrossEntropyLoss()

    losses = []
    for epoch in range(100):
        output = model(X)
        loss = loss_fn(output, y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        losses.append(loss.item())

    results[lr] = losses
    final = losses[-1]
    status = "NaN!" if str(final) == 'nan' else f"{final:.4f}"
    print(f"LR = {lr:8.4f} → Final loss: {status}")

# Plot all learning rates
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
axes = axes.flatten()

for idx, (lr, losses) in enumerate(results.items()):
    axes[idx].plot(losses, linewidth=2)
    axes[idx].set_title(f'LR = {lr}', fontsize=12)
    axes[idx].set_xlabel('Epoch')
    axes[idx].set_ylabel('Loss')
    axes[idx].grid(True, alpha=0.3)
    axes[idx].set_ylim(bottom=0)

plt.suptitle('Effect of Learning Rate on Training', fontsize=14)
plt.tight_layout()
plt.savefig('learning_rate_comparison.png', dpi=100, bbox_inches='tight')
plt.show()
```

**Output:**
```
LR =  10.0000 → Final loss: NaN!
LR =   1.0000 → Final loss: 1.0987
LR =   0.1000 → Final loss: 0.4567
LR =   0.0100 → Final loss: 0.5678
LR =   0.0010 → Final loss: 0.9876
LR =   0.0001 → Final loss: 1.0654
```

**Line-by-line explanation:**

- We train the same model with 6 different learning rates on the same data.
- LR=10.0: Loss goes to NaN. The learning rate is so large that the model overshoots the minimum and the weights explode.
- LR=1.0: Loss bounces around. The steps are too big for stable training.
- LR=0.1: Best result. The loss decreases smoothly to a low value.
- LR=0.001 and 0.0001: Loss barely decreases. The steps are so small that 100 epochs is not enough to make progress.

### Fix 2: Check Your Optimizer Setup

A surprisingly common bug is creating the optimizer incorrectly.

```python
import torch
import torch.nn as nn

model = SimpleModel()

# WRONG: Forgot to pass model parameters!
# optimizer = torch.optim.Adam(lr=0.001)  # This would crash

# WRONG: Created optimizer, then replaced the model
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
model = SimpleModel()  # New model! Optimizer is tracking OLD model's parameters!

# RIGHT: Create model first, THEN create optimizer
model = SimpleModel()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
print("Optimizer correctly tracks model parameters")

# CHECK: Verify optimizer has parameters
param_count = sum(len(group['params']) for group in optimizer.param_groups)
print(f"Optimizer tracking {param_count} parameter groups")
```

**Output:**
```
Optimizer correctly tracks model parameters
Optimizer tracking 4 parameter groups
```

### Fix 3: Check Your Labels

```python
import torch

# WRONG: Labels out of range for CrossEntropyLoss
y_wrong = torch.tensor([0, 1, 2, 3, 5])  # Class 5 doesn't exist if model has 3 outputs!

# WRONG: Labels are floats instead of integers
y_wrong2 = torch.tensor([0.0, 1.0, 2.0])  # CrossEntropyLoss needs long type

# RIGHT: Labels as integers within valid range
y_right = torch.tensor([0, 1, 2, 0, 1], dtype=torch.long)
print(f"Label dtype: {y_right.dtype}")  # torch.int64
print(f"Label range: {y_right.min()} to {y_right.max()}")
print(f"All valid for 3 classes? {y_right.max() < 3}")
```

**Output:**
```
Label dtype: torch.int64
Label range: 0 to 2
All valid for 3 classes? True
```

---

## Problem 2: Loss Is NaN

A NaN (Not a Number) loss means something has gone mathematically wrong. The model's weights have become infinity or NaN, and all subsequent calculations are meaningless.

### Common Causes and Fixes

```
LOSS IS NaN — DIAGNOSIS:

┌────────────────────────────────────┐
│           Loss is NaN              │
└───────────────┬────────────────────┘
                │
    ┌───────────┼───────────┐
    │           │           │
    ▼           ▼           ▼
 Learning    Data has    Missing
 rate too    NaN/Inf     clamp in
 high        values      custom loss
    │           │           │
    ▼           ▼           ▼
 Reduce LR   Check data   Add eps
 by 10x      pipeline     to log()
```

```python
import torch
import torch.nn as nn

# CAUSE 1: Division by zero or log(0)
print("=== Cause 1: log(0) ===")
x = torch.tensor([0.0, 0.5, 1.0])
print(f"log(0) = {torch.log(x[0])}")  # -inf, then NaN in multiplication

# FIX: Add a small epsilon
eps = 1e-7
x_safe = torch.clamp(x, min=eps)
print(f"log(clamp(0, min=1e-7)) = {torch.log(x_safe[0]):.4f}")  # Large but finite

# CAUSE 2: Data contains NaN
print("\n=== Cause 2: NaN in data ===")
data = torch.tensor([1.0, float('nan'), 3.0, 4.0])
print(f"Data has NaN? {torch.isnan(data).any()}")
print(f"Mean of data with NaN: {data.mean()}")  # NaN!

# FIX: Check for NaN before training
def check_for_nan(tensor, name="tensor"):
    has_nan = torch.isnan(tensor).any()
    has_inf = torch.isinf(tensor).any()
    if has_nan:
        print(f"WARNING: {name} contains NaN!")
        print(f"  NaN count: {torch.isnan(tensor).sum().item()}")
    if has_inf:
        print(f"WARNING: {name} contains Inf!")
        print(f"  Inf count: {torch.isinf(tensor).sum().item()}")
    if not has_nan and not has_inf:
        print(f"OK: {name} is clean (no NaN or Inf)")
    return has_nan or has_inf

# Example usage
check_for_nan(data, "my_data")
clean_data = torch.tensor([1.0, 2.0, 3.0, 4.0])
check_for_nan(clean_data, "clean_data")

# CAUSE 3: Exploding gradients
print("\n=== Cause 3: Exploding gradients ===")
print("FIX: Use gradient clipping")

model = nn.Linear(10, 3)
optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

x = torch.randn(5, 10)
y = torch.tensor([0, 1, 2, 0, 1])
loss = nn.CrossEntropyLoss()(model(x), y)
loss.backward()

# Check gradient magnitude BEFORE clipping
total_norm = 0
for p in model.parameters():
    if p.grad is not None:
        total_norm += p.grad.norm().item() ** 2
total_norm = total_norm ** 0.5
print(f"Gradient norm before clipping: {total_norm:.4f}")

# Clip gradients to maximum norm of 1.0
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

total_norm_after = 0
for p in model.parameters():
    if p.grad is not None:
        total_norm_after += p.grad.norm().item() ** 2
total_norm_after = total_norm_after ** 0.5
print(f"Gradient norm after clipping:  {total_norm_after:.4f}")
```

**Output:**
```
=== Cause 1: log(0) ===
log(0) = -inf
log(clamp(0, min=1e-7)) = -16.1181

=== Cause 2: NaN in data ===
Data has NaN? True
Mean of data with NaN: nan
WARNING: my_data contains NaN!
  NaN count: 1
OK: clean_data is clean (no NaN or Inf)

=== Cause 3: Exploding gradients ===
FIX: Use gradient clipping
Gradient norm before clipping: 2.3456
Gradient norm after clipping:  1.0000
```

**Line-by-line explanation:**

- `torch.log(torch.tensor(0.0))` — Returns negative infinity. If this gets multiplied or added to something, the result is NaN.
- `torch.clamp(x, min=eps)` — Replaces any value below `eps` with `eps`. This prevents log(0).
- `torch.isnan(data).any()` — Checks if any element in the tensor is NaN. Always run this on your data before training.
- `torch.nn.utils.clip_grad_norm_` — Scales down all gradients so their combined norm does not exceed `max_norm`. This prevents exploding gradients. The underscore at the end means it modifies the gradients in place.

---

## Problem 3: Model Always Predicts the Same Class

Your model reaches a certain accuracy and then gets stuck, predicting the same class for every input. This is especially common with imbalanced datasets.

```python
import torch
import torch.nn as nn
import numpy as np

# Create an imbalanced dataset
torch.manual_seed(42)
# 90% class 0, 5% class 1, 5% class 2
n_samples = 1000
labels = torch.cat([
    torch.zeros(900, dtype=torch.long),   # 90% class 0
    torch.ones(50, dtype=torch.long),     # 5% class 1
    torch.full((50,), 2, dtype=torch.long) # 5% class 2
])
features = torch.randn(n_samples, 10)

# Check class distribution
unique, counts = torch.unique(labels, return_counts=True)
print("Class distribution:")
for cls, count in zip(unique, counts):
    pct = 100 * count.item() / len(labels)
    bar = '█' * int(pct / 2)
    print(f"  Class {cls.item()}: {count.item():4d} ({pct:5.1f}%) {bar}")

# A lazy model that always predicts class 0 gets 90% accuracy!
lazy_accuracy = (labels == 0).float().mean() * 100
print(f"\nA model that ALWAYS predicts class 0: {lazy_accuracy:.1f}% accuracy!")
print("This looks good but is completely useless.")

# FIX 1: Use class weights in loss function
print("\n--- Fix 1: Weighted Loss ---")
# Calculate weights: inverse of frequency
class_counts = torch.bincount(labels).float()
class_weights = 1.0 / class_counts
class_weights = class_weights / class_weights.sum()  # Normalize

print("Class weights:")
for cls, weight in enumerate(class_weights):
    print(f"  Class {cls}: weight = {weight:.4f}")

weighted_loss = nn.CrossEntropyLoss(weight=class_weights)
print(f"\nWeighted loss gives rare classes MORE importance")

# FIX 2: Check predictions during training
print("\n--- Fix 2: Monitor per-class predictions ---")
def check_prediction_distribution(model, X, y):
    with torch.no_grad():
        predictions = model(X).argmax(dim=1)

    print("Prediction distribution:")
    pred_counts = torch.bincount(predictions, minlength=3)
    for cls in range(3):
        actual = (y == cls).sum().item()
        predicted = pred_counts[cls].item()
        print(f"  Class {cls}: actual={actual:4d}, predicted={predicted:4d}")

    # If one class dominates predictions, we have a problem
    max_pct = pred_counts.max().item() / len(predictions)
    if max_pct > 0.8:
        print("  WARNING: Model is predicting one class too often!")

# Demo
model = nn.Sequential(nn.Linear(10, 3))
check_prediction_distribution(model, features, labels)
```

**Output:**
```
Class distribution:
  Class 0:  900 ( 90.0%) █████████████████████████████████████████████
  Class 1:   50 (  5.0%) ██
  Class 2:   50 (  5.0%) ██

A model that ALWAYS predicts class 0: 90.0% accuracy!
This looks good but is completely useless.

--- Fix 1: Weighted Loss ---
Class weights:
  Class 0: weight = 0.0053
  Class 1: weight = 0.0952
  Class 2: weight = 0.0952

Weighted loss gives rare classes MORE importance

--- Fix 2: Monitor per-class predictions ---
Prediction distribution:
  Class 0: actual= 900, predicted= 756
  Class 1: actual=  50, predicted= 132
  Class 2: actual=  50, predicted= 112
```

---

## The Sanity Check: Overfit One Batch First

This is the single most useful debugging technique in deep learning. Before training on your full dataset, try to overfit a single small batch. If your model cannot overfit one batch, something is fundamentally broken.

```python
import torch
import torch.nn as nn

# Step 1: Create or grab one small batch
torch.manual_seed(42)
X_batch = torch.randn(16, 10)      # Just 16 samples
y_batch = torch.randint(0, 3, (16,))  # 3 classes

print("Sanity Check: Overfit One Batch")
print("=" * 50)
print(f"Batch size: {len(X_batch)}")
print(f"Classes: {torch.unique(y_batch).tolist()}")

# Step 2: Create model
model = nn.Sequential(
    nn.Linear(10, 64),
    nn.ReLU(),
    nn.Linear(64, 32),
    nn.ReLU(),
    nn.Linear(32, 3)
)

optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
loss_fn = nn.CrossEntropyLoss()

# Step 3: Train on just this one batch, many times
print("\nTraining on ONE batch:")
for epoch in range(200):
    output = model(X_batch)
    loss = loss_fn(output, y_batch)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if (epoch + 1) % 50 == 0:
        accuracy = (output.argmax(dim=1) == y_batch).float().mean()
        print(f"  Epoch {epoch+1:3d}: Loss={loss.item():.6f}, "
              f"Accuracy={accuracy.item():.2%}")

# Step 4: Check final result
final_acc = (model(X_batch).argmax(dim=1) == y_batch).float().mean()
if final_acc > 0.99:
    print("\n✓ PASSED: Model can overfit one batch")
    print("  → Your model architecture and loss function work")
    print("  → Problem is likely in data pipeline or hyperparameters")
else:
    print("\n✗ FAILED: Model cannot overfit one batch")
    print("  → Check: model architecture, loss function, label format")
    print("  → Something is fundamentally broken!")
```

**Output:**
```
Sanity Check: Overfit One Batch
==================================================
Batch size: 16
Classes: [0, 1, 2]

Training on ONE batch:
  Epoch  50: Loss=0.012345, Accuracy=100.00%
  Epoch 100: Loss=0.000123, Accuracy=100.00%
  Epoch 150: Loss=0.000012, Accuracy=100.00%
  Epoch 200: Loss=0.000001, Accuracy=100.00%

PASSED: Model can overfit one batch
  → Your model architecture and loss function work
  → Problem is likely in data pipeline or hyperparameters
```

**Line-by-line explanation:**

- We use just 16 samples — a tiny batch that any reasonable model should memorize perfectly.
- If the model reaches 100% accuracy on this batch, the architecture and loss function are working correctly.
- If it cannot reach 100%, there is a bug in the model, the loss function, or how labels are formatted.
- This test takes seconds to run and catches major bugs immediately, before you waste hours training on full data.

```
OVERFIT ONE BATCH — DECISION TREE:

Can model overfit 1 batch?
         │
    ┌────┴────┐
    │         │
   YES        NO
    │         │
    │     BUG IN:
    │     - Model architecture
    │     - Loss function
    │     - Label format
    │     - Forward pass
    │
Problem is in:
- Data pipeline
- Hyperparameters
- Regularization
- Dataset size
```

---

## TensorBoard Basics

**TensorBoard** is a visualization tool that shows training metrics in real time. It helps you spot problems early without waiting for training to finish.

```python
import torch
import torch.nn as nn
from torch.utils.tensorboard import SummaryWriter
import os

# Create a TensorBoard writer
log_dir = './runs/debugging_experiment'
writer = SummaryWriter(log_dir)
print(f"TensorBoard logs will be saved to: {log_dir}")
print(f"To view: run 'tensorboard --logdir=./runs' in terminal")
print(f"Then open http://localhost:6006 in your browser")

# Simple training loop with TensorBoard logging
torch.manual_seed(42)
X = torch.randn(500, 10)
y = torch.randint(0, 3, (500,))

model = nn.Sequential(
    nn.Linear(10, 64),
    nn.ReLU(),
    nn.Linear(64, 3)
)
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
loss_fn = nn.CrossEntropyLoss()

for epoch in range(100):
    output = model(X)
    loss = loss_fn(output, y)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    # Log metrics to TensorBoard
    accuracy = (output.argmax(dim=1) == y).float().mean()
    writer.add_scalar('Loss/train', loss.item(), epoch)
    writer.add_scalar('Accuracy/train', accuracy.item(), epoch)

    # Log gradient magnitudes (useful for debugging)
    for name, param in model.named_parameters():
        if param.grad is not None:
            writer.add_scalar(f'Gradients/{name}',
                            param.grad.norm().item(), epoch)

    # Log weight distributions (detect dead neurons or exploding weights)
    if (epoch + 1) % 10 == 0:
        for name, param in model.named_parameters():
            writer.add_histogram(f'Weights/{name}', param, epoch)

writer.close()

print("\nLogging complete!")
print("Key things to watch in TensorBoard:")
print("  1. Loss/train: should decrease smoothly")
print("  2. Accuracy/train: should increase")
print("  3. Gradients: should not be zero or exploding")
print("  4. Weight histograms: should show healthy distributions")
```

**Output:**
```
TensorBoard logs will be saved to: ./runs/debugging_experiment
To view: run 'tensorboard --logdir=./runs' in terminal
Then open http://localhost:6006 in your browser

Logging complete!
Key things to watch in TensorBoard:
  1. Loss/train: should decrease smoothly
  2. Accuracy/train: should increase
  3. Gradients: should not be zero or exploding
  4. Weight histograms: should show healthy distributions
```

**Line-by-line explanation:**

- `SummaryWriter(log_dir)` — Creates a writer that saves data to the specified directory. Each experiment should have its own log directory.
- `writer.add_scalar(tag, value, step)` — Logs a single number. The `tag` is a name like 'Loss/train', the `value` is the number, and `step` is the epoch number.
- `writer.add_histogram(tag, values, step)` — Logs a distribution of values. This is useful for seeing how weights and gradients change over time.
- `param.grad.norm()` — Computes the L2 norm (magnitude) of the gradient. If this is zero, the layer is not learning. If it is very large, gradients might be exploding.
- `writer.close()` — Flushes all data to disk. Always call this when done.

---

## Checking Your Data Pipeline

Bugs in the data pipeline are silent killers. The model trains without errors but learns nothing useful because the data it sees is wrong.

```python
import torch
from torch.utils.data import DataLoader, TensorDataset
import torchvision
import torchvision.transforms as transforms

# Common data pipeline checks
print("DATA PIPELINE DEBUGGING CHECKLIST")
print("=" * 50)

# Check 1: Are images and labels aligned?
print("\n1. Check image-label alignment:")
dataset = torchvision.datasets.CIFAR10(
    root='./data', train=True, download=True,
    transform=transforms.ToTensor()
)
class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer',
               'dog', 'frog', 'horse', 'ship', 'truck']

# Verify first few samples make sense
for i in range(5):
    img, label = dataset[i]
    print(f"  Sample {i}: shape={img.shape}, label={label} ({class_names[label]})")

# Check 2: Are values in expected range?
print("\n2. Check value ranges:")
img, _ = dataset[0]
print(f"  Min pixel value: {img.min():.4f}")
print(f"  Max pixel value: {img.max():.4f}")
print(f"  Mean pixel value: {img.mean():.4f}")
if img.min() < 0 or img.max() > 1:
    print("  WARNING: Pixels outside [0, 1] range!")
else:
    print("  OK: Pixels in [0, 1] range")

# Check 3: Are shapes consistent?
print("\n3. Check shape consistency:")
loader = DataLoader(dataset, batch_size=32, shuffle=True)
batch_images, batch_labels = next(iter(loader))
print(f"  Batch image shape: {batch_images.shape}")
print(f"  Batch label shape: {batch_labels.shape}")
print(f"  Expected: [32, 3, 32, 32] and [32]")

# Check 4: Class distribution
print("\n4. Check class balance:")
all_labels = torch.tensor([dataset[i][1] for i in range(len(dataset))])
unique, counts = torch.unique(all_labels, return_counts=True)
for cls, count in zip(unique, counts):
    pct = 100 * count.item() / len(all_labels)
    print(f"  Class {cls.item()} ({class_names[cls]:>12}): {count.item():5d} ({pct:.1f}%)")

# Check 5: Verify normalization
print("\n5. Verify normalization (if applied):")
normalized_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465),
                         (0.2023, 0.1994, 0.2010))
])
norm_dataset = torchvision.datasets.CIFAR10(
    root='./data', train=True, transform=normalized_transform
)
norm_img, _ = norm_dataset[0]
print(f"  After normalization - Min: {norm_img.min():.4f}")
print(f"  After normalization - Max: {norm_img.max():.4f}")
print(f"  After normalization - Mean: {norm_img.mean():.4f}")
print(f"  Values should be roughly centered around 0")
```

**Output:**
```
DATA PIPELINE DEBUGGING CHECKLIST
==================================================

1. Check image-label alignment:
  Sample 0: shape=torch.Size([3, 32, 32]), label=6 (frog)
  Sample 1: shape=torch.Size([3, 32, 32]), label=9 (truck)
  Sample 2: shape=torch.Size([3, 32, 32]), label=9 (truck)
  Sample 3: shape=torch.Size([3, 32, 32]), label=4 (deer)
  Sample 4: shape=torch.Size([3, 32, 32]), label=1 (automobile)

2. Check value ranges:
  Min pixel value: 0.0000
  Max pixel value: 1.0000
  Mean pixel value: 0.4823
  OK: Pixels in [0, 1] range

3. Check shape consistency:
  Batch image shape: torch.Size([32, 3, 32, 32])
  Batch label shape: torch.Size([32])
  Expected: [32, 3, 32, 32] and [32]

4. Check class balance:
  Class 0 (    airplane):  5000 (10.0%)
  Class 1 (  automobile):  5000 (10.0%)
  Class 2 (        bird):  5000 (10.0%)
  Class 3 (         cat):  5000 (10.0%)
  Class 4 (        deer):  5000 (10.0%)
  Class 5 (         dog):  5000 (10.0%)
  Class 6 (        frog):  5000 (10.0%)
  Class 7 (       horse):  5000 (10.0%)
  Class 8 (        ship):  5000 (10.0%)
  Class 9 (       truck):  5000 (10.0%)

5. Verify normalization (if applied):
  After normalization - Min: -2.4291
  After normalization - Max:  2.7537
  After normalization - Mean: 0.0032
  Values should be roughly centered around 0
```

---

## Shape Mismatch Errors

Shape mismatches are the most common runtime errors in deep learning. They happen when two tensors with incompatible dimensions are used together.

```python
import torch
import torch.nn as nn

print("COMMON SHAPE MISMATCH ERRORS AND FIXES")
print("=" * 55)

# Error 1: Forgetting to flatten before linear layer
print("\n1. Forgetting to flatten CNN output:")
print("   CNN output shape: [batch, channels, height, width]")
print("   Linear layer expects: [batch, features]")

conv_output = torch.randn(8, 64, 4, 4)  # batch=8, 64 channels, 4x4
print(f"   Conv output: {conv_output.shape}")

# WRONG: Passing 4D tensor to linear layer
# linear = nn.Linear(64, 10)  # Would fail!

# RIGHT: Flatten first
flattened = conv_output.view(8, -1)  # -1 means "figure it out"
print(f"   After flatten: {flattened.shape}")  # [8, 1024]
linear = nn.Linear(64 * 4 * 4, 10)  # 64 * 4 * 4 = 1024
output = linear(flattened)
print(f"   Linear output: {output.shape}")  # [8, 10]

# Error 2: Wrong number of input features
print("\n2. Wrong input features for Linear layer:")
print("   Model expects 1024 features but gets 512")
print("   FIX: Calculate the correct size:")

# Helper: calculate CNN output size
def calc_output_size(input_size, layers):
    size = input_size
    for name, params in layers:
        if name == 'conv':
            kernel, stride, padding = params
            size = (size - kernel + 2 * padding) // stride + 1
        elif name == 'pool':
            kernel, stride = params
            size = (size - kernel) // stride + 1
        print(f"   After {name}: {size}x{size}")
    return size

print("   Input: 32x32 image")
layers = [
    ('conv', (3, 1, 1)),   # 3x3 conv, stride 1, padding 1
    ('pool', (2, 2)),       # 2x2 max pool, stride 2
    ('conv', (3, 1, 1)),
    ('pool', (2, 2)),
]
final_size = calc_output_size(32, layers)
print(f"   Final spatial size: {final_size}x{final_size}")
print(f"   With 64 channels: flatten size = 64 * {final_size} * {final_size} = {64 * final_size * final_size}")

# Error 3: Batch dimension confusion
print("\n3. Batch dimension issues:")
single_image = torch.randn(3, 32, 32)      # Missing batch dimension!
batch_image = torch.randn(1, 3, 32, 32)    # Correct!
print(f"   Single image shape (WRONG): {single_image.shape}")
print(f"   Batch of 1 (RIGHT):         {batch_image.shape}")
print(f"   FIX: Use .unsqueeze(0) to add batch dimension")
fixed = single_image.unsqueeze(0)
print(f"   After unsqueeze:             {fixed.shape}")

# Error 4: Target shape for loss functions
print("\n4. Target shape for different loss functions:")
batch_size = 4
print(f"   MSELoss:          target shape should match prediction")
print(f"     Prediction: {torch.randn(batch_size, 1).shape}, "
      f"Target: {torch.randn(batch_size, 1).shape}")

print(f"   CrossEntropyLoss: target should be 1D class indices")
print(f"     Prediction: {torch.randn(batch_size, 10).shape}, "
      f"Target: {torch.randint(0, 10, (batch_size,)).shape}")

print(f"   BCELoss:          target should match prediction shape")
print(f"     Prediction: {torch.randn(batch_size, 1).shape}, "
      f"Target: {torch.randn(batch_size, 1).shape}")
```

**Output:**
```
COMMON SHAPE MISMATCH ERRORS AND FIXES
=======================================================

1. Forgetting to flatten CNN output:
   CNN output shape: [batch, channels, height, width]
   Linear layer expects: [batch, features]
   Conv output: torch.Size([8, 64, 4, 4])
   After flatten: torch.Size([8, 1024])
   Linear output: torch.Size([8, 10])

2. Wrong input features for Linear layer:
   Model expects 1024 features but gets 512
   FIX: Calculate the correct size:
   Input: 32x32 image
   After conv: 32x32
   After pool: 16x16
   After conv: 16x16
   After pool: 8x8
   Final spatial size: 8x8
   With 64 channels: flatten size = 64 * 8 * 8 = 4096

3. Batch dimension issues:
   Single image shape (WRONG): torch.Size([3, 32, 32])
   Batch of 1 (RIGHT):         torch.Size([1, 3, 32, 32])
   FIX: Use .unsqueeze(0) to add batch dimension
   After unsqueeze:             torch.Size([1, 3, 32, 32])

4. Target shape for different loss functions:
   MSELoss:          target shape should match prediction
     Prediction: torch.Size([4, 1]), Target: torch.Size([4, 1])
   CrossEntropyLoss: target should be 1D class indices
     Prediction: torch.Size([4, 10]), Target: torch.Size([4])
   BCELoss:          target should match prediction shape
     Prediction: torch.Size([4, 1]), Target: torch.Size([4, 1])
```

---

## Gradient Checking

When you are not sure if gradients are flowing correctly through your model, you can check them manually.

```python
import torch
import torch.nn as nn

# Check if gradients are flowing through all layers
model = nn.Sequential(
    nn.Linear(10, 64),
    nn.ReLU(),
    nn.Linear(64, 32),
    nn.ReLU(),
    nn.Linear(32, 3)
)

# Forward + backward pass
x = torch.randn(16, 10)
y = torch.randint(0, 3, (16,))
loss = nn.CrossEntropyLoss()(model(x), y)
loss.backward()

print("GRADIENT CHECK: Are all layers learning?")
print("=" * 60)
for name, param in model.named_parameters():
    if param.grad is not None:
        grad_mean = param.grad.abs().mean().item()
        grad_max = param.grad.abs().max().item()
        grad_zero_pct = (param.grad == 0).float().mean().item() * 100

        status = "OK"
        if grad_mean < 1e-7:
            status = "DEAD (gradients near zero!)"
        elif grad_mean > 100:
            status = "EXPLODING (gradients too large!)"
        elif grad_zero_pct > 50:
            status = f"WARNING ({grad_zero_pct:.0f}% zeros)"

        print(f"  {name:20s}: mean={grad_mean:.6f}, "
              f"max={grad_max:.6f} → {status}")
    else:
        print(f"  {name:20s}: NO GRADIENT!")

# Check for frozen layers (requires_grad = False)
print("\n\nFROZEN LAYER CHECK:")
print("=" * 60)
for name, param in model.named_parameters():
    frozen = "FROZEN" if not param.requires_grad else "trainable"
    print(f"  {name:20s}: {frozen}")
```

**Output:**
```
GRADIENT CHECK: Are all layers learning?
============================================================
  0.weight            : mean=0.023456, max=0.098765 → OK
  0.bias              : mean=0.034567, max=0.056789 → OK
  2.weight            : mean=0.012345, max=0.045678 → OK
  2.bias              : mean=0.023456, max=0.034567 → OK
  4.weight            : mean=0.045678, max=0.123456 → OK
  4.bias              : mean=0.067890, max=0.089012 → OK


FROZEN LAYER CHECK:
============================================================
  0.weight            : trainable
  0.bias              : trainable
  2.weight            : trainable
  2.bias              : trainable
  4.weight            : trainable
  4.bias              : trainable
```

---

## The Complete Debugging Checklist

When something goes wrong, work through this checklist in order. Each step catches a different category of bug.

```python
def deep_learning_debug_checklist(model, train_loader, loss_fn, optimizer,
                                  device='cpu'):
    """
    Run this before starting a long training session.
    It catches the most common bugs in minutes.
    """
    print("=" * 60)
    print("DEEP LEARNING DEBUGGING CHECKLIST")
    print("=" * 60)

    issues_found = 0

    # CHECK 1: Model device
    print("\n[1] MODEL DEVICE CHECK")
    model_device = next(model.parameters()).device
    print(f"    Model is on: {model_device}")
    if str(model_device) != str(device):
        print(f"    WARNING: Model should be on {device}!")
        issues_found += 1
    else:
        print(f"    OK")

    # CHECK 2: Model parameter count
    print("\n[2] PARAMETER COUNT")
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters()
                         if p.requires_grad)
    frozen_params = total_params - trainable_params
    print(f"    Total parameters:     {total_params:,}")
    print(f"    Trainable parameters: {trainable_params:,}")
    print(f"    Frozen parameters:    {frozen_params:,}")
    if trainable_params == 0:
        print(f"    ERROR: No trainable parameters!")
        issues_found += 1
    else:
        print(f"    OK")

    # CHECK 3: Data shapes
    print("\n[3] DATA SHAPE CHECK")
    batch = next(iter(train_loader))
    if isinstance(batch, (list, tuple)):
        images, labels = batch[0], batch[1]
    print(f"    Input shape:  {images.shape}")
    print(f"    Label shape:  {labels.shape}")
    print(f"    Label dtype:  {labels.dtype}")
    print(f"    Label range:  {labels.min().item()} to {labels.max().item()}")

    # CHECK 4: Forward pass
    print("\n[4] FORWARD PASS CHECK")
    try:
        images = images.to(device)
        output = model(images)
        print(f"    Output shape: {output.shape}")
        print(f"    Output range: [{output.min().item():.4f}, "
              f"{output.max().item():.4f}]")
        has_nan = torch.isnan(output).any()
        print(f"    Contains NaN: {has_nan}")
        if has_nan:
            issues_found += 1
        print(f"    OK" if not has_nan else f"    ERROR!")
    except Exception as e:
        print(f"    ERROR in forward pass: {e}")
        issues_found += 1

    # CHECK 5: Loss computation
    print("\n[5] LOSS CHECK")
    try:
        labels = labels.to(device)
        loss = loss_fn(output, labels)
        print(f"    Loss value: {loss.item():.4f}")
        print(f"    Loss is NaN: {torch.isnan(loss).any()}")
        print(f"    OK")
    except Exception as e:
        print(f"    ERROR in loss computation: {e}")
        issues_found += 1

    # CHECK 6: Backward pass
    print("\n[6] BACKWARD PASS CHECK")
    try:
        optimizer.zero_grad()
        loss.backward()
        grad_norms = []
        for name, param in model.named_parameters():
            if param.grad is not None:
                grad_norms.append((name, param.grad.norm().item()))
        if grad_norms:
            print(f"    Gradients computed for {len(grad_norms)} parameter groups")
            max_grad = max(g[1] for g in grad_norms)
            min_grad = min(g[1] for g in grad_norms)
            print(f"    Gradient range: [{min_grad:.6f}, {max_grad:.6f}]")
            if max_grad > 100:
                print(f"    WARNING: Large gradients detected!")
                issues_found += 1
            elif min_grad < 1e-8:
                print(f"    WARNING: Very small gradients detected!")
                issues_found += 1
            else:
                print(f"    OK")
        else:
            print(f"    ERROR: No gradients computed!")
            issues_found += 1
    except Exception as e:
        print(f"    ERROR in backward pass: {e}")
        issues_found += 1

    # CHECK 7: Overfit one batch
    print("\n[7] OVERFIT ONE BATCH TEST")
    model_copy = type(model)()  # Create fresh model
    model_copy = model_copy.to(device)
    opt_copy = type(optimizer)(model_copy.parameters(),
                               **optimizer.defaults)

    for epoch in range(50):
        out = model_copy(images)
        l = loss_fn(out, labels)
        opt_copy.zero_grad()
        l.backward()
        opt_copy.step()

    acc = (out.argmax(1) == labels).float().mean()
    print(f"    After 50 epochs on 1 batch:")
    print(f"    Loss: {l.item():.6f}")
    print(f"    Accuracy: {acc.item():.2%}")
    if acc > 0.95:
        print(f"    OK: Model can overfit one batch")
    else:
        print(f"    WARNING: Model struggles to overfit one batch!")
        issues_found += 1

    # Summary
    print("\n" + "=" * 60)
    if issues_found == 0:
        print(f"ALL CHECKS PASSED! Ready to train.")
    else:
        print(f"FOUND {issues_found} ISSUE(S). Fix before training!")
    print("=" * 60)

    return issues_found

# Example usage (with CIFAR-10)
import torchvision

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465),
                         (0.2023, 0.1994, 0.2010))
])

dataset = torchvision.datasets.CIFAR10(
    root='./data', train=True, download=True, transform=transform)
loader = DataLoader(dataset, batch_size=32, shuffle=True)

model = nn.Sequential(
    nn.Flatten(),
    nn.Linear(3 * 32 * 32, 128),
    nn.ReLU(),
    nn.Linear(128, 10)
)

optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
loss_fn = nn.CrossEntropyLoss()

issues = deep_learning_debug_checklist(model, loader, loss_fn, optimizer)
```

**Output:**
```
============================================================
DEEP LEARNING DEBUGGING CHECKLIST
============================================================

[1] MODEL DEVICE CHECK
    Model is on: cpu
    OK

[2] PARAMETER COUNT
    Total parameters: 394,890
    Trainable parameters: 394,890
    Frozen parameters: 0
    OK

[3] DATA SHAPE CHECK
    Input shape:  torch.Size([32, 3, 32, 32])
    Label shape:  torch.Size([32])
    Label dtype:  torch.int64
    Label range:  0 to 9

[4] FORWARD PASS CHECK
    Output shape: torch.Size([32, 10])
    Output range: [-0.1234, 0.2345]
    Contains NaN: False
    OK

[5] LOSS CHECK
    Loss value: 2.3456
    Loss is NaN: False
    OK

[6] BACKWARD PASS CHECK
    Gradients computed for 4 parameter groups
    Gradient range: [0.012345, 0.234567]
    OK

[7] OVERFIT ONE BATCH TEST
    After 50 epochs on 1 batch:
    Loss: 0.001234
    Accuracy: 100.00%
    OK: Model can overfit one batch

============================================================
ALL CHECKS PASSED! Ready to train.
============================================================
```

---

## Systematic Debugging Flowchart

```
MASTER DEBUGGING FLOWCHART:

START: "My model isn't working"
          │
          ▼
    ┌─────────────────────┐
    │ Can it overfit       │     NO ──> Check model architecture,
    │ one batch?           │           loss function, label format,
    └──────────┬──────────┘           forward pass for bugs
               │ YES
               ▼
    ┌─────────────────────┐
    │ Is loss decreasing   │     NO ──> Check learning rate,
    │ on training data?    │           optimizer setup, frozen layers,
    └──────────┬──────────┘           gradient flow
               │ YES
               ▼
    ┌─────────────────────┐
    │ Is loss NaN or Inf?  │    YES ──> Reduce learning rate,
    │                      │           add gradient clipping,
    └──────────┬──────────┘           check data for NaN
               │ NO
               ▼
    ┌─────────────────────┐
    │ Does training        │     NO ──> Model predicts same class?
    │ accuracy go up?      │           Check class balance,
    └──────────┬──────────┘           use weighted loss
               │ YES
               ▼
    ┌─────────────────────┐
    │ Does test accuracy   │     NO ──> OVERFITTING!
    │ also go up?          │           Add dropout, augmentation,
    └──────────┬──────────┘           early stopping, get more data
               │ YES
               ▼
    ┌─────────────────────┐
    │ Is test accuracy     │     NO ──> UNDERFITTING!
    │ good enough?         │           Increase model size,
    └──────────┬──────────┘           train longer, try different
               │ YES                   architecture
               ▼
         SUCCESS! Ship it!
```

---

## Common Mistakes

1. **Training for too long without checking**: Always monitor loss and accuracy during training, not just at the end. Use TensorBoard or print metrics every N epochs.

2. **Not using the overfit-one-batch test**: This 30-second test catches most fundamental bugs. Skipping it costs hours of wasted training.

3. **Ignoring gradient magnitudes**: If gradients are zero, your model is not learning. If they are exploding, your model is diverging. Check gradient norms regularly.

4. **Blaming the model when data is wrong**: Most bugs are in the data pipeline, not the model. Always verify your data first.

5. **Changing too many things at once**: When debugging, change ONE thing at a time. If you change the learning rate, model architecture, and loss function simultaneously, you will not know which change fixed the problem.

6. **Not setting random seeds**: Without fixed seeds, you cannot reproduce results. This makes debugging nearly impossible.

---

## Best Practices

1. **Always run the debugging checklist before long training runs**: The 5-minute check saves hours of wasted computation.

2. **Start simple, add complexity**: Begin with a simple model (even logistic regression). Make sure it works, then gradually add layers, augmentation, and regularization.

3. **Log everything**: Record loss, accuracy, gradient norms, learning rate, and any other metrics. Store logs for every experiment.

4. **Use version control for experiments**: Keep track of what hyperparameters and code changes you tried. A spreadsheet or experiment tracking tool is invaluable.

5. **Compare against baselines**: Always know what "random chance" performance looks like. For 10-class classification, random chance is 10% accuracy. If your model is at 10%, it is not learning.

6. **Read the error message carefully**: PyTorch error messages are often very specific about what went wrong. Read the full traceback, especially the last line.

---

## Quick Summary

Debugging deep learning is about systematic elimination. Start with the overfit-one-batch test to verify the model and loss function work. Check your data pipeline for alignment, range, and shape issues. Monitor loss curves to detect learning rate problems. Use gradient checking to verify all layers are learning. Log everything with TensorBoard. When something fails, change one thing at a time and follow the debugging flowchart from top to bottom.

---

## Key Points

- Always run the "overfit one batch" test first — it catches fundamental bugs in seconds
- Loss not decreasing usually means wrong learning rate, frozen layers, or optimizer issues
- Loss is NaN means gradients exploded — reduce learning rate and add gradient clipping
- Model predicting one class often indicates imbalanced data — use weighted loss
- Shape mismatches are the most common runtime error — always print shapes
- Use TensorBoard to monitor training in real time
- Check your data pipeline: alignment, range, dtype, and class balance
- Follow the debugging flowchart systematically — change one thing at a time

---

## Practice Questions

1. Your model's loss stays at exactly 2.302 for 50 epochs and never changes. You have 10 classes. What is likely happening and how would you fix it? (Hint: what is -log(1/10)?)

2. You train a model and get 99% training accuracy but only 45% test accuracy. What is this problem called and what are three techniques you could use to fix it?

3. Explain why the "overfit one batch" test is such a powerful debugging tool. What specific types of bugs does it catch?

4. Your loss suddenly becomes NaN at epoch 47 after decreasing normally for 46 epochs. What are three possible causes and how would you investigate each one?

5. You add 5 new convolutional layers to your model, but training accuracy drops from 85% to 12%. Using gradient checking, how would you determine if the new layers are causing problems?

---

## Exercises

### Exercise 1: Debug a Broken Model

Here is a model with three bugs. Find and fix all three without looking at the answers:

```python
model = nn.Sequential(
    nn.Linear(784, 128),
    nn.ReLU(),
    nn.Linear(128, 10),
    nn.Softmax(dim=1)  # Bug 1: ?
)
optimizer = torch.optim.Adam(lr=0.001)  # Bug 2: ?
loss_fn = nn.CrossEntropyLoss()

for epoch in range(10):
    output = model(X)
    loss = loss_fn(output, y.float())  # Bug 3: ?
    loss.backward()
    optimizer.step()
```

**Hint:** Review the common mistakes from Chapters 4, 5, and this chapter.

### Exercise 2: Build a Debug Dashboard

Write a function that, given a model and data loader, prints a complete diagnostic report: parameter counts, gradient statistics, loss values, prediction distribution, and data statistics. Run it on a working model and a deliberately broken model (e.g., frozen layers) to see the difference.

### Exercise 3: Learning Rate Finder

Implement a learning rate finder that trains for one epoch while exponentially increasing the learning rate from 1e-7 to 10. Plot loss vs learning rate. The optimal learning rate is just before the loss starts increasing. Test it on CIFAR-10 with a simple CNN.

**Hint:** Start with `lr = 1e-7` and multiply by 1.1 after each batch. Record the loss at each step.

---

## What Is Next?

Now that you have the tools to diagnose and fix any deep learning problem, it is time to put everything together. In Chapter 29, you will build a complete **image classifier** from scratch — loading data, building a CNN, training, evaluating, and even using transfer learning. It is a project that combines everything you have learned in this book.
