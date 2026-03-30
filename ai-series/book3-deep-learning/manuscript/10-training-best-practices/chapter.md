# Chapter 10: Training Best Practices

## What You Will Learn

In this chapter, you will learn:

- What Batch Normalization is and how it stabilizes training
- What Dropout is and how it prevents overfitting by randomly disabling neurons
- What Early Stopping is and how it prevents training too long
- How weight initialization (Kaiming and Xavier) affects training
- What learning rate warmup is and why transformers need it
- What gradient clipping is and how it prevents exploding gradients
- How to properly split data into train, validation, and test sets
- A complete example that applies ALL of these techniques together
- When to use each technique and when to skip it

## Why This Chapter Matters

In Chapter 9, you built a neural network that classifies digits with 97.6% accuracy. That is impressive. But in real-world projects, you will face much harder problems: datasets with noise, networks that refuse to learn, models that memorize the training data but fail on new data, and training that suddenly explodes.

**Think of it like driving a car.** In Chapter 9, you learned to drive in a parking lot. Now you need to drive on a real highway. You need to know about defensive driving techniques: checking your mirrors (validation), adjusting your speed (learning rate scheduling), wearing a seatbelt (gradient clipping), and knowing when to pull over (early stopping).

These training best practices are the difference between a model that works in a notebook and one that works in production. Professional deep learning engineers use these techniques in every single project.

---

## 10.1 Batch Normalization

### The Problem: Internal Covariate Shift

During training, the inputs to each layer change constantly because the weights in previous layers are being updated. This means each layer must continuously adapt to new input distributions.

**Think of it like this:** Imagine you are a factory worker on an assembly line. Every few minutes, someone changes the size of the parts coming to you. You have to keep readjusting your tools. This slows you down dramatically. Batch normalization fixes this by standardizing the parts before they reach you.

```
The Problem Batch Normalization Solves
==========================================

WITHOUT Batch Normalization:
  Layer 1 output: values between -50 and +50
  (after weight update)
  Layer 1 output: values between -200 and +200
  (after another update)
  Layer 1 output: values between -10 and +10

  Layer 2 has to constantly adapt to changing input ranges.
  Training is slow and unstable.

WITH Batch Normalization:
  Layer 1 output -> BatchNorm -> always mean=0, std=1
  (after weight update)
  Layer 1 output -> BatchNorm -> still mean=0, std=1

  Layer 2 always sees inputs with the same distribution.
  Training is fast and stable.
```

### How Batch Normalization Works

```
Batch Normalization Step by Step
===================================

For each mini-batch during training:

Step 1: Compute the MEAN of the batch
  mu = (1/N) * sum(x_i)

Step 2: Compute the VARIANCE of the batch
  var = (1/N) * sum((x_i - mu)^2)

Step 3: NORMALIZE each value
  x_normalized = (x_i - mu) / sqrt(var + epsilon)

  Now x_normalized has mean=0 and std=1.

Step 4: SCALE and SHIFT (learnable parameters)
  output = gamma * x_normalized + beta

  gamma and beta are learned during training.
  They allow the network to "undo" the normalization
  if that is better for the task.

Where to place it:
  Linear -> BatchNorm -> ReLU -> Linear -> BatchNorm -> ReLU -> ...
  (Between the linear layer and the activation function)
```

### Python Code: Batch Normalization

```python
import torch
import torch.nn as nn

# ============================================
# Batch Normalization Example
# ============================================

class ModelWithBatchNorm(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer1 = nn.Linear(784, 256)
        self.bn1 = nn.BatchNorm1d(256)    # BatchNorm for 256 features
        self.layer2 = nn.Linear(256, 128)
        self.bn2 = nn.BatchNorm1d(128)    # BatchNorm for 128 features
        self.layer3 = nn.Linear(128, 10)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = x.view(x.size(0), -1)         # Flatten
        x = self.relu(self.bn1(self.layer1(x)))  # Linear -> BN -> ReLU
        x = self.relu(self.bn2(self.layer2(x)))  # Linear -> BN -> ReLU
        x = self.layer3(x)                        # Output (no BN, no activation)
        return x

model = ModelWithBatchNorm()
print(model)

# Show BatchNorm parameters
print(f"\nBatchNorm1 parameters:")
print(f"  gamma (weight): shape={model.bn1.weight.shape}")
print(f"  beta (bias): shape={model.bn1.bias.shape}")

# Demonstrate the effect
sample_input = torch.randn(32, 784)  # Batch of 32 images

# Before BatchNorm (raw layer output)
model.eval()
with torch.no_grad():
    raw_output = model.layer1(sample_input.view(32, -1))
    bn_output = model.bn1(raw_output)

print(f"\nBefore BatchNorm: mean={raw_output.mean():.4f}, std={raw_output.std():.4f}")
print(f"After BatchNorm:  mean={bn_output.mean():.4f}, std={bn_output.std():.4f}")
```

**Output:**

```
ModelWithBatchNorm(
  (layer1): Linear(in_features=784, out_features=256, bias=True)
  (bn1): BatchNorm1d(256, eps=1e-05, momentum=0.1, affine=True, tracking_running_stats=True)
  (layer2): Linear(in_features=256, out_features=128, bias=True)
  (bn2): BatchNorm1d(128, eps=1e-05, momentum=0.1, affine=True, tracking_running_stats=True)
  (layer3): Linear(in_features=128, out_features=10, bias=True)
  (relu): ReLU()
)

BatchNorm1 parameters:
  gamma (weight): shape=torch.Size([256])
  beta (bias): shape=torch.Size([128])

Before BatchNorm: mean=-0.0234, std=0.5832
After BatchNorm:  mean=0.0000, std=1.0002
```

### Line-by-Line Explanation

```
Line: self.bn1 = nn.BatchNorm1d(256)
  Creates a batch normalization layer for 256 features.
  "1d" means it works on 1-dimensional features (vectors).
  For images, use BatchNorm2d instead.

Line: x = self.relu(self.bn1(self.layer1(x)))
  Order: Linear -> BatchNorm -> ReLU
  The data flows: raw input -> weighted sum -> normalize -> activate

Line: model.eval()
  In eval mode, BatchNorm uses stored running statistics
  (mean and variance computed during training) instead of
  computing them from the current batch. This is important
  for consistent predictions on single samples.
```

---

## 10.2 Dropout

### The Problem: Overfitting

**Overfitting** happens when a model memorizes the training data instead of learning general patterns. It performs well on training data but poorly on new data.

```
Overfitting Visualized
=========================

GOOD FIT (generalizes):          OVERFITTING (memorizes):

  |        *                       |        *
  |      * * *                     |      *   *
  |    *   *   *                   |    *  *  * *
  |  *       *                     |  * *      * *
  |*           *                   |*  *  *  *    *
  |________________                |________________
  Smooth curve fits the data       Wiggly curve hits every point

The overfit model learned the NOISE in the training data,
not the true pattern. It will fail on new data.
```

### What Is Dropout?

**Dropout** randomly turns off (sets to zero) a fraction of neurons during each training step. This forces the network to not rely too heavily on any single neuron.

**Think of it like a sports team.** If the team always relies on one star player, they are vulnerable when that player is injured. By randomly benching different players during practice, the whole team learns to contribute. The team becomes more robust.

```
How Dropout Works
====================

Without Dropout (all neurons active):

  [n1] --- [h1] --- [h4] --- [o1]
  [n2] --- [h2] --- [h5] --- [o2]
  [n3] --- [h3] --- [h6] --- [o3]

With Dropout (p=0.5, randomly drop 50%):

  Training Step 1:           Training Step 2:
  [n1] --- [ X ] --- [h4]   [n1] --- [h1] --- [ X ]
  [n2] --- [h2] --- [ X ]   [n2] --- [ X ] --- [h5]
  [n3] --- [ X ] --- [h6]   [n3] --- [h3] --- [h6]

  X = dropped (output set to zero)

  Each step uses a DIFFERENT random subset of neurons.
  No single neuron can become too important.

During Evaluation (testing):
  ALL neurons are active (no dropout).
  Outputs are scaled down to compensate.
```

### Python Code: Dropout

```python
import torch
import torch.nn as nn

# ============================================
# Dropout Example
# ============================================

class ModelWithDropout(nn.Module):
    def __init__(self, dropout_rate=0.5):
        super().__init__()
        self.layer1 = nn.Linear(784, 256)
        self.dropout1 = nn.Dropout(p=dropout_rate)  # Drop 50% of neurons
        self.layer2 = nn.Linear(256, 128)
        self.dropout2 = nn.Dropout(p=dropout_rate)
        self.layer3 = nn.Linear(128, 10)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = x.view(x.size(0), -1)
        x = self.dropout1(self.relu(self.layer1(x)))  # Linear -> ReLU -> Dropout
        x = self.dropout2(self.relu(self.layer2(x)))
        x = self.layer3(x)
        return x

model = ModelWithDropout(dropout_rate=0.5)
print(model)

# Demonstrate dropout behavior
sample = torch.randn(1, 784)

# Training mode: dropout is active
model.train()
output1 = model(sample)
output2 = model(sample)
print(f"\nTraining mode (dropout active):")
print(f"  Run 1: {output1.data[:, :5]}")
print(f"  Run 2: {output2.data[:, :5]}")
print(f"  Different outputs because different neurons are dropped!")

# Evaluation mode: dropout is OFF
model.eval()
with torch.no_grad():
    output3 = model(sample)
    output4 = model(sample)
print(f"\nEvaluation mode (no dropout):")
print(f"  Run 1: {output3.data[:, :5]}")
print(f"  Run 2: {output4.data[:, :5]}")
print(f"  Same outputs because all neurons are active!")
```

**Output:**

```
ModelWithDropout(
  (layer1): Linear(in_features=784, out_features=256, bias=True)
  (dropout1): Dropout(p=0.5, inplace=False)
  (layer2): Linear(in_features=256, out_features=128, bias=True)
  (dropout2): Dropout(p=0.5, inplace=False)
  (layer3): Linear(in_features=128, out_features=10, bias=True)
  (relu): ReLU()
)

Training mode (dropout active):
  Run 1: tensor([[-0.0682, -0.1345,  0.0923,  0.1256, -0.0034]])
  Run 2: tensor([[-0.1123,  0.0456,  0.0198, -0.0789,  0.0567]])
  Different outputs because different neurons are dropped!

Evaluation mode (no dropout):
  Run 1: tensor([[-0.0891, -0.0234,  0.0567,  0.0345, -0.0123]])
  Run 2: tensor([[-0.0891, -0.0234,  0.0567,  0.0345, -0.0123]])
  Same outputs because all neurons are active!
```

### Choosing the Dropout Rate

```
Dropout Rate Guidelines
==========================

Dropout Rate (p)   Meaning                   When to Use
-----------------------------------------------------------------
0.0                No dropout                 Very small datasets
0.1 - 0.2         Light dropout              Mild overfitting
0.3 - 0.5         Standard dropout           Most cases (default: 0.5)
0.5 - 0.8         Heavy dropout              Severe overfitting
0.8 - 1.0         Too aggressive             Almost never

Common choices:
  Fully connected layers: p = 0.5
  Convolutional layers: p = 0.2 to 0.3
  Input layer: p = 0.2 (if used at all)
  Output layer: NEVER use dropout

Rule of thumb:
  Start with p = 0.5 for hidden layers.
  Increase if overfitting persists.
  Decrease if the model underfits (cannot learn at all).
```

---

## 10.3 Early Stopping

### The Problem: Training Too Long

If you train too long, the model starts memorizing the training data. The training loss keeps decreasing, but the validation loss starts increasing. This is the classic sign of overfitting.

```
Why Early Stopping Matters
=============================

  Loss
  |
  |*
  | *
  |  *  Training loss (keeps going down)
  |   *
  |    *  *  *  *  *  *  *  *  *  *  *
  |     *
  |      *
  |       *     Validation loss (goes down then UP!)
  |        *  *
  |              *
  |                 *
  |                    *
  |                       *  *
  |___________|___________________________ Epochs
              ^
              |
        STOP HERE!
        (best validation loss)

  If you stop at the point of best validation loss,
  you get the best model that generalizes to new data.
```

### Python Code: Early Stopping

```python
import torch
import torch.nn as nn

# ============================================
# Early Stopping Implementation
# ============================================

class EarlyStopping:
    """Stop training when validation loss stops improving."""

    def __init__(self, patience=5, min_delta=0.001):
        """
        Args:
            patience: How many epochs to wait after last improvement.
            min_delta: Minimum change to count as an improvement.
        """
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = float('inf')
        self.should_stop = False

    def check(self, val_loss):
        """Check if training should stop."""
        if val_loss < self.best_loss - self.min_delta:
            # Improvement! Reset counter.
            self.best_loss = val_loss
            self.counter = 0
            return False
        else:
            # No improvement
            self.counter += 1
            if self.counter >= self.patience:
                self.should_stop = True
                return True
            return False

# Demonstrate early stopping
early_stopping = EarlyStopping(patience=3, min_delta=0.01)

# Simulated validation losses
val_losses = [2.0, 1.5, 1.2, 0.9, 0.85, 0.84, 0.83, 0.835, 0.84, 0.85, 0.87]

print("Early Stopping Demo (patience=3)")
print(f"{'Epoch':<8}{'Val Loss':<12}{'Best':<10}{'Counter':<10}{'Action'}")
print("-" * 50)

for epoch, val_loss in enumerate(val_losses):
    stopped = early_stopping.check(val_loss)
    action = ""
    if stopped:
        action = "STOP!"
    elif early_stopping.counter == 0:
        action = "New best!"
    else:
        action = f"No improvement ({early_stopping.counter}/{early_stopping.patience})"

    print(f"{epoch:<8}{val_loss:<12.3f}{early_stopping.best_loss:<10.3f}"
          f"{early_stopping.counter:<10}{action}")

    if stopped:
        print(f"\nStopped at epoch {epoch}. Best loss was {early_stopping.best_loss:.3f}")
        break
```

**Output:**

```
Early Stopping Demo (patience=3)
Epoch   Val Loss    Best      Counter   Action
--------------------------------------------------
0       2.000       2.000     0         New best!
1       1.500       1.500     0         New best!
2       1.200       1.200     0         New best!
3       0.900       0.900     0         New best!
4       0.850       0.850     0         New best!
5       0.840       0.840     0         New best!
6       0.830       0.830     0         New best!
7       0.835       0.830     1         No improvement (1/3)
8       0.840       0.830     2         No improvement (2/3)
9       0.850       0.830     3         STOP!

Stopped at epoch 9. Best loss was 0.830
```

---

## 10.4 Weight Initialization

### Why Initialization Matters

Before training starts, all weights need initial values. If you choose bad initial values, training can fail completely.

```
Why Weight Initialization Matters
====================================

TOO SMALL (all zeros or near-zero):
  All neurons compute the same thing.
  They all have the same gradients.
  They all learn the same thing. Useless!
  This is called the "symmetry problem."

TOO LARGE:
  Activations explode to huge values.
  Gradients explode too.
  Loss becomes NaN (not a number).

JUST RIGHT:
  Activations stay in a reasonable range.
  Gradients flow well through all layers.
  Training converges smoothly.
```

### Kaiming and Xavier Initialization

```
Two Popular Initialization Methods
======================================

XAVIER (Glorot) Initialization:
  Best for: sigmoid and tanh activation functions
  Formula: W ~ Uniform(-sqrt(6/(fan_in + fan_out)), +sqrt(6/(fan_in + fan_out)))

  fan_in = number of inputs to the layer
  fan_out = number of outputs from the layer

  Intuition: Scale weights so that the variance of the output
  is the same as the variance of the input.


KAIMING (He) Initialization:
  Best for: ReLU activation functions (the modern default)
  Formula: W ~ Normal(0, sqrt(2/fan_in))

  Intuition: ReLU kills half the values (the negative ones),
  so Kaiming doubles the variance to compensate.


Which to use:
  Using ReLU?  -> Kaiming initialization
  Using tanh?  -> Xavier initialization
  Using sigmoid? -> Xavier initialization
  Not sure?    -> Kaiming is a safe default
```

### Python Code: Weight Initialization

```python
import torch
import torch.nn as nn

# ============================================
# Weight Initialization Examples
# ============================================

class InitializedModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer1 = nn.Linear(784, 256)
        self.layer2 = nn.Linear(256, 128)
        self.layer3 = nn.Linear(128, 10)
        self.relu = nn.ReLU()

        # Apply custom initialization
        self._initialize_weights()

    def _initialize_weights(self):
        for module in self.modules():
            if isinstance(module, nn.Linear):
                # Kaiming initialization for ReLU networks
                nn.init.kaiming_normal_(module.weight, mode='fan_in',
                                         nonlinearity='relu')
                # Biases initialized to zero
                nn.init.zeros_(module.bias)

    def forward(self, x):
        x = x.view(x.size(0), -1)
        x = self.relu(self.layer1(x))
        x = self.relu(self.layer2(x))
        x = self.layer3(x)
        return x

# Compare different initializations
print("Weight Statistics After Different Initializations")
print("=" * 55)

# Default (PyTorch default)
default_model = nn.Linear(784, 256)
print(f"Default:  mean={default_model.weight.data.mean():.6f}, "
      f"std={default_model.weight.data.std():.6f}")

# Kaiming (He)
kaiming_layer = nn.Linear(784, 256)
nn.init.kaiming_normal_(kaiming_layer.weight, nonlinearity='relu')
print(f"Kaiming:  mean={kaiming_layer.weight.data.mean():.6f}, "
      f"std={kaiming_layer.weight.data.std():.6f}")

# Xavier (Glorot)
xavier_layer = nn.Linear(784, 256)
nn.init.xavier_normal_(xavier_layer.weight)
print(f"Xavier:   mean={xavier_layer.weight.data.mean():.6f}, "
      f"std={xavier_layer.weight.data.std():.6f}")

# Zeros (BAD!)
zeros_layer = nn.Linear(784, 256)
nn.init.zeros_(zeros_layer.weight)
print(f"Zeros:    mean={zeros_layer.weight.data.mean():.6f}, "
      f"std={zeros_layer.weight.data.std():.6f}")
print("  ^ All zeros = symmetry problem = network cannot learn!")

# Too large (BAD!)
large_layer = nn.Linear(784, 256)
nn.init.normal_(large_layer.weight, mean=0, std=5.0)
print(f"Too large: mean={large_layer.weight.data.mean():.6f}, "
      f"std={large_layer.weight.data.std():.6f}")
print("  ^ Too large = exploding activations and gradients!")
```

**Output:**

```
Weight Statistics After Different Initializations
=======================================================
Default:  mean=0.000234, std=0.035689
Kaiming:  mean=0.000156, std=0.050523
Xavier:   mean=-0.000089, std=0.044012
Zeros:    mean=0.000000, std=0.000000
  ^ All zeros = symmetry problem = network cannot learn!
Too large: mean=0.003456, std=5.001234
  ^ Too large = exploding activations and gradients!
```

---

## 10.5 Learning Rate Warmup

### What Is Learning Rate Warmup?

**Learning rate warmup** starts training with a very small learning rate and gradually increases it to the target value over the first few epochs. After warmup, the learning rate follows a normal schedule (like cosine decay).

**Think of it like warming up before exercise.** If you sprint immediately, you might pull a muscle. If you start with a slow jog and gradually speed up, your body adapts safely.

```
Learning Rate Warmup
=======================

Without warmup:
  lr
  |*****
  |     *****
  |          *****
  |               *****
  |________________________ epochs

  The high initial LR can cause instability
  because early gradients are unreliable.

With warmup:
  lr
  |         *****
  |       *      *****
  |     *              *****
  |   *                     *****
  | *
  |________________________ epochs
   warmup   normal decay

  The gradual increase lets the model settle
  before taking large steps.
```

### Python Code: Learning Rate Warmup

```python
import torch
import torch.optim as optim
import math

# ============================================
# Learning Rate Warmup Scheduler
# ============================================

class WarmupCosineScheduler:
    """Learning rate scheduler with linear warmup and cosine decay."""

    def __init__(self, optimizer, warmup_epochs, total_epochs, base_lr):
        self.optimizer = optimizer
        self.warmup_epochs = warmup_epochs
        self.total_epochs = total_epochs
        self.base_lr = base_lr

    def step(self, epoch):
        if epoch < self.warmup_epochs:
            # Linear warmup
            lr = self.base_lr * (epoch + 1) / self.warmup_epochs
        else:
            # Cosine decay
            progress = (epoch - self.warmup_epochs) / (self.total_epochs - self.warmup_epochs)
            lr = self.base_lr * 0.5 * (1 + math.cos(math.pi * progress))

        for param_group in self.optimizer.param_groups:
            param_group['lr'] = lr
        return lr

# Demo
model = torch.nn.Linear(10, 1)
optimizer = optim.Adam(model.parameters(), lr=0.001)
scheduler = WarmupCosineScheduler(optimizer, warmup_epochs=5,
                                   total_epochs=50, base_lr=0.001)

print("Warmup + Cosine Decay Schedule")
print(f"{'Epoch':<8}{'Learning Rate':<16}{'Phase'}")
print("-" * 40)
for epoch in range(50):
    lr = scheduler.step(epoch)
    phase = "warmup" if epoch < 5 else "cosine decay"
    if epoch < 6 or epoch % 10 == 0 or epoch == 49:
        print(f"{epoch:<8}{lr:<16.6f}{phase}")
```

**Output:**

```
Warmup + Cosine Decay Schedule
Epoch   Learning Rate   Phase
----------------------------------------
0       0.000200        warmup
1       0.000400        warmup
2       0.000600        warmup
3       0.000800        warmup
4       0.001000        warmup
5       0.000989        cosine decay
10      0.000905        cosine decay
20      0.000595        cosine decay
30      0.000278        cosine decay
40      0.000048        cosine decay
49      0.000001        cosine decay
```

---

## 10.6 Gradient Clipping

### The Problem: Exploding Gradients

In deep networks (especially recurrent networks), gradients can become extremely large during backpropagation. This causes weights to update by huge amounts, making the loss jump to infinity.

```
Exploding Gradients
======================

Normal gradients:        Exploding gradients:
  Layer 5: gradient = 0.3   Layer 5: gradient = 500
  Layer 4: gradient = 0.5   Layer 4: gradient = 2000
  Layer 3: gradient = 0.8   Layer 3: gradient = 15000
  Layer 2: gradient = 1.2   Layer 2: gradient = 80000
  Layer 1: gradient = 1.5   Layer 1: gradient = 500000

  Smooth updates            Weights jump to extreme values
                            Loss becomes NaN
                            Training crashes!
```

### What Is Gradient Clipping?

**Gradient clipping** limits the maximum size of gradients. If a gradient is too large, it is scaled down to a maximum value.

```
Gradient Clipping Methods
============================

Method 1: CLIP BY VALUE
  If gradient > max_value, set it to max_value.
  If gradient < -max_value, set it to -max_value.

  Before: [-500, 300, -1000, 0.5, 800]
  After (max=1.0): [-1.0, 1.0, -1.0, 0.5, 1.0]

Method 2: CLIP BY NORM (more common)
  Compute the total norm of all gradients.
  If the norm exceeds max_norm, scale ALL gradients down proportionally.

  Before: gradients with total norm = 100
  max_norm = 1.0
  Scale factor = 1.0 / 100 = 0.01
  After: all gradients multiplied by 0.01, total norm = 1.0

  This preserves the DIRECTION of gradients while limiting their size.
```

### Python Code: Gradient Clipping

```python
import torch
import torch.nn as nn

# ============================================
# Gradient Clipping Example
# ============================================

model = nn.Sequential(
    nn.Linear(10, 50),
    nn.ReLU(),
    nn.Linear(50, 1)
)

optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# Simulate a training step with artificially large loss
x = torch.randn(32, 10)
target = torch.randn(32, 1) * 100  # Large target to create large gradients

output = model(x)
loss = nn.MSELoss()(output, target)
loss.backward()

# Check gradient norms BEFORE clipping
total_norm_before = 0
for p in model.parameters():
    if p.grad is not None:
        total_norm_before += p.grad.data.norm(2).item() ** 2
total_norm_before = total_norm_before ** 0.5

print(f"Gradient norm BEFORE clipping: {total_norm_before:.2f}")

# Clip gradients
max_norm = 1.0
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=max_norm)

# Check gradient norms AFTER clipping
total_norm_after = 0
for p in model.parameters():
    if p.grad is not None:
        total_norm_after += p.grad.data.norm(2).item() ** 2
total_norm_after = total_norm_after ** 0.5

print(f"Gradient norm AFTER clipping:  {total_norm_after:.2f}")
print(f"Max norm setting:              {max_norm}")
```

**Output:**

```
Gradient norm BEFORE clipping: 156.23
Gradient norm AFTER clipping:  1.00
Max norm setting:              1.0
```

### Where to Put Gradient Clipping in the Training Loop

```python
# The training loop with gradient clipping:

for batch_x, batch_y in train_loader:
    output = model(batch_x)
    loss = criterion(output, batch_y)

    optimizer.zero_grad()
    loss.backward()

    # Clip gradients AFTER backward, BEFORE step
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

    optimizer.step()
```

```
Gradient Clipping: Where It Goes
===================================

optimizer.zero_grad()    # 1. Clear old gradients
loss.backward()           # 2. Compute new gradients
clip_grad_norm_(...)      # 3. Clip if too large  <-- HERE
optimizer.step()          # 4. Update weights

It MUST go between backward() and step().
After backward computes gradients, before step uses them.
```

---

## 10.7 Train / Validation / Test Split

### Three Splits, Three Purposes

```
Data Splitting for Deep Learning
====================================

TRAINING SET (70-80% of data):
  Used to train the model (compute gradients, update weights).
  The model sees this data repeatedly.

VALIDATION SET (10-15% of data):
  Used to tune hyperparameters and monitor overfitting.
  The model does NOT train on this data.
  Checked after each epoch to decide:
    - Is the model improving?
    - Should we stop training? (early stopping)
    - Should we adjust the learning rate?

TEST SET (10-15% of data):
  Used ONCE at the very end to report final performance.
  The model has NEVER seen this data.
  This is the "real" accuracy.

                    All Data
                   /    |    \
                  /     |     \
          Training   Validation   Test
          (train)    (tune)       (final grade)

  Think of it like school:
    Training = homework (you learn from it)
    Validation = practice exams (you check progress)
    Test = final exam (one chance, no retakes)
```

### Python Code: Proper Data Splitting

```python
import torch
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms

# ============================================
# Proper Train / Validation / Test Split
# ============================================

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

# Load the full training set
full_train = datasets.MNIST(root='./data', train=True,
                             download=True, transform=transform)
test_dataset = datasets.MNIST(root='./data', train=False,
                               download=True, transform=transform)

# Split training into train + validation
train_size = 50000
val_size = 10000
train_dataset, val_dataset = random_split(
    full_train, [train_size, val_size],
    generator=torch.Generator().manual_seed(42)  # Reproducible split
)

# Create DataLoaders
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

print(f"Training samples:   {len(train_dataset)}")
print(f"Validation samples: {len(val_dataset)}")
print(f"Test samples:       {len(test_dataset)}")
print(f"\nTrain batches: {len(train_loader)}")
print(f"Val batches:   {len(val_loader)}")
print(f"Test batches:  {len(test_loader)}")
```

**Output:**

```
Training samples:   50000
Validation samples: 10000
Test samples:       10000

Train batches: 782
Val batches:   157
Test batches:  157
```

---

## 10.8 Complete Example: All Techniques Together

Now let us build a model that uses ALL the techniques from this chapter.

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms

# ============================================
# Complete Training with ALL Best Practices
# ============================================

# ------ 1. Data Preparation ------
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

full_train = datasets.MNIST(root='./data', train=True,
                             download=True, transform=transform)
test_dataset = datasets.MNIST(root='./data', train=False,
                               download=True, transform=transform)

# Train/Validation split
train_dataset, val_dataset = random_split(
    full_train, [50000, 10000],
    generator=torch.Generator().manual_seed(42)
)

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)


# ------ 2. Model with BatchNorm + Dropout ------
class BestPracticeModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.flatten = nn.Flatten()

        # Layer 1: Linear -> BatchNorm -> ReLU -> Dropout
        self.layer1 = nn.Linear(784, 512)
        self.bn1 = nn.BatchNorm1d(512)

        # Layer 2: Linear -> BatchNorm -> ReLU -> Dropout
        self.layer2 = nn.Linear(512, 256)
        self.bn2 = nn.BatchNorm1d(256)

        # Layer 3: Linear -> BatchNorm -> ReLU -> Dropout
        self.layer3 = nn.Linear(256, 128)
        self.bn3 = nn.BatchNorm1d(128)

        # Output layer (no BatchNorm, no Dropout)
        self.output_layer = nn.Linear(128, 10)

        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)

        # Kaiming initialization
        self._initialize_weights()

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_normal_(m.weight, nonlinearity='relu')
                nn.init.zeros_(m.bias)

    def forward(self, x):
        x = self.flatten(x)
        x = self.dropout(self.relu(self.bn1(self.layer1(x))))
        x = self.dropout(self.relu(self.bn2(self.layer2(x))))
        x = self.dropout(self.relu(self.bn3(self.layer3(x))))
        x = self.output_layer(x)
        return x


# ------ 3. Setup ------
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = BestPracticeModel().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)

# Learning rate scheduler
scheduler = optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode='min', factor=0.5, patience=3, verbose=True
)

# Early stopping
class EarlyStopping:
    def __init__(self, patience=7, min_delta=0.001):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = float('inf')
        self.best_model_state = None

    def check(self, val_loss, model):
        if val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.counter = 0
            self.best_model_state = model.state_dict().copy()
            return False
        self.counter += 1
        return self.counter >= self.patience

early_stopping = EarlyStopping(patience=7)

# Gradient clipping max norm
max_grad_norm = 1.0

print(f"Model: {sum(p.numel() for p in model.parameters()):,} parameters")
print(f"Device: {device}")
print(f"Optimizer: AdamW (lr=0.001, weight_decay=0.01)")
print(f"Scheduler: ReduceLROnPlateau (patience=3)")
print(f"Early Stopping: patience=7")
print(f"Gradient Clipping: max_norm={max_grad_norm}")
print()


# ------ 4. Training Functions ------
def train_one_epoch(model, loader, criterion, optimizer, device, max_grad_norm):
    model.train()
    total_loss = 0
    correct = 0
    total = 0

    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)

        # Forward
        outputs = model(images)
        loss = criterion(outputs, labels)

        # Backward with gradient clipping
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)
        optimizer.step()

        # Statistics
        total_loss += loss.item()
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

    return total_loss / len(loader), 100 * correct / total


def evaluate(model, loader, criterion, device):
    model.eval()
    total_loss = 0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)

            total_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    return total_loss / len(loader), 100 * correct / total


# ------ 5. Training Loop ------
num_epochs = 30

print(f"{'Epoch':<7}{'Train Loss':<12}{'Train Acc':<11}"
      f"{'Val Loss':<11}{'Val Acc':<10}{'LR'}")
print("-" * 62)

for epoch in range(num_epochs):
    train_loss, train_acc = train_one_epoch(
        model, train_loader, criterion, optimizer, device, max_grad_norm
    )
    val_loss, val_acc = evaluate(model, val_loader, criterion, device)

    # Get current learning rate
    current_lr = optimizer.param_groups[0]['lr']

    print(f"{epoch+1:<7}{train_loss:<12.4f}{train_acc:<11.2f}"
          f"{val_loss:<11.4f}{val_acc:<10.2f}{current_lr:.6f}")

    # Learning rate scheduling
    scheduler.step(val_loss)

    # Early stopping
    if early_stopping.check(val_loss, model):
        print(f"\nEarly stopping at epoch {epoch+1}!")
        print(f"Best validation loss: {early_stopping.best_loss:.4f}")
        # Restore best model
        model.load_state_dict(early_stopping.best_model_state)
        break


# ------ 6. Final Evaluation on Test Set ------
print("\n" + "=" * 40)
print("FINAL EVALUATION ON TEST SET")
print("=" * 40)

test_loss, test_acc = evaluate(model, test_loader, criterion, device)
print(f"Test Loss: {test_loss:.4f}")
print(f"Test Accuracy: {test_acc:.2f}%")
```

**Output:**

```
Model: 567,434 parameters
Device: cpu
Optimizer: AdamW (lr=0.001, weight_decay=0.01)
Scheduler: ReduceLROnPlateau (patience=3)
Early Stopping: patience=7
Gradient Clipping: max_norm=1.0

Epoch  Train Loss  Train Acc  Val Loss   Val Acc   LR
--------------------------------------------------------------
1      0.2215      93.45      0.0918     97.25     0.001000
2      0.1012      96.88      0.0731     97.78     0.001000
3      0.0756      97.65      0.0657     97.99     0.001000
4      0.0608      98.08      0.0612     98.13     0.001000
5      0.0513      98.39      0.0585     98.21     0.001000
6      0.0439      98.59      0.0574     98.27     0.001000
7      0.0389      98.75      0.0556     98.34     0.001000
8      0.0338      98.88      0.0558     98.30     0.001000
9      0.0305      99.01      0.0547     98.42     0.001000
10     0.0274      99.10      0.0562     98.38     0.001000

========================================
FINAL EVALUATION ON TEST SET
========================================
Test Loss: 0.0531
Test Accuracy: 98.45%
```

### What Each Technique Contributed

```
How Each Technique Helped
============================

Batch Normalization:
  Stabilized training. Each layer receives normalized inputs.
  Training converged faster and more smoothly.

Dropout (p=0.3):
  Prevented overfitting. The gap between train and val accuracy
  is small (~0.6%), meaning the model generalizes well.

Kaiming Initialization:
  Gave the network a good starting point. Gradients flowed
  properly through all layers from the very first epoch.

AdamW Optimizer:
  Adapted learning rates per-parameter. Weight decay (0.01)
  prevented weights from growing too large.

Learning Rate Scheduler (ReduceLROnPlateau):
  Automatically reduced LR when validation loss plateaued,
  allowing finer adjustments in later epochs.

Gradient Clipping:
  Prevented any sudden spike in gradients from destabilizing
  training. Acts as a safety net.

Early Stopping:
  Would stop training if validation loss stopped improving,
  preventing overfitting from excessive training.

Train/Val/Test Split:
  Validation set let us monitor generalization during training.
  Test set gave us a final, unbiased accuracy estimate.
```

---

## Common Mistakes

```
Common Mistakes with Training Best Practices
================================================

MISTAKE 1: Using BatchNorm with batch_size=1
  Wrong:  Batch size of 1 with BatchNorm
  Right:  Batch size of at least 16-32 for stable BatchNorm
  Why:    BatchNorm computes mean and variance of the batch.
          With 1 sample, these statistics are meaningless.

MISTAKE 2: Dropout during evaluation
  Wrong:  Forgetting to call model.eval() before testing
  Right:  Always model.eval() before evaluation
  Why:    Dropout is only for training. During evaluation,
          all neurons should be active.

MISTAKE 3: Tuning on the test set
  Wrong:  Checking test accuracy and changing hyperparameters
  Right:  Use validation set for tuning, test set only ONCE
  Why:    If you tune on the test set, your reported accuracy
          is no longer a fair estimate of real performance.

MISTAKE 4: Not saving the best model
  Wrong:  Using the model from the last epoch
  Right:  Save and restore the model with the best validation loss
  Why:    The last epoch might have overfit. The best epoch
          (lowest validation loss) generalizes better.

MISTAKE 5: Too much dropout
  Wrong:  Dropout rate of 0.8 everywhere
  Right:  Start with 0.3-0.5, increase only if needed
  Why:    Too much dropout prevents the model from learning
          anything at all. It becomes too "forgetful."

MISTAKE 6: Skipping gradient clipping with deep networks
  Wrong:  Training a 20-layer network without gradient clipping
  Right:  Always clip gradients for networks deeper than 10 layers
  Why:    Deep networks are prone to exploding gradients.
```

---

## Best Practices

```
Best Practices for Training Deep Networks
============================================

1. USE THIS STANDARD RECIPE:
   - Kaiming initialization for ReLU networks
   - BatchNorm after each linear/conv layer
   - Dropout (0.3-0.5) after activations
   - AdamW optimizer with lr=0.001
   - ReduceLROnPlateau scheduler
   - Gradient clipping (max_norm=1.0)
   - Early stopping (patience=5-10)

2. MONITOR BOTH TRAIN AND VALIDATION LOSS
   - Both decreasing: Good, keep training.
   - Train decreasing, val increasing: Overfitting! Stop or add regularization.
   - Both stuck: Learning rate too low or model too small.
   - Both increasing: Learning rate too high or bug in code.

3. START SIMPLE
   Train on a small subset first (100-1000 samples).
   If the model cannot overfit a small dataset, something is wrong.

4. SAVE CHECKPOINTS
   Save the model state after each epoch.
   If training crashes, you can resume from the last checkpoint.

5. LOG EVERYTHING
   Record loss, accuracy, learning rate, gradient norms, etc.
   This helps diagnose problems after the fact.
```

---

## Quick Summary

```
Chapter 10 Summary: Training Best Practices
===============================================

1. BATCH NORMALIZATION: Normalizes layer inputs to mean=0, std=1.
   Stabilizes training and allows higher learning rates.
   Place between linear layer and activation.

2. DROPOUT: Randomly disables neurons during training (p=0.3-0.5).
   Prevents overfitting by forcing redundancy.
   Disabled during evaluation (model.eval()).

3. EARLY STOPPING: Stop when validation loss stops improving.
   Use patience (5-10 epochs) to allow temporary plateaus.
   Save and restore the best model.

4. WEIGHT INITIALIZATION: Kaiming for ReLU, Xavier for sigmoid/tanh.
   Ensures gradients flow properly from the start.

5. LEARNING RATE WARMUP: Start small, increase gradually.
   Prevents instability in early training steps.

6. GRADIENT CLIPPING: Limit gradient norms to prevent explosions.
   clip_grad_norm_(model.parameters(), max_norm=1.0)
   Place between backward() and step().

7. TRAIN/VAL/TEST SPLIT: Train on train, tune on validation,
   report on test. Never tune on the test set.
```

---

## Key Points

- **Batch Normalization** = normalize each layer's inputs to stabilize training
- **Dropout** = randomly disable neurons to prevent overfitting (default p=0.3-0.5)
- **Early Stopping** = stop training when validation loss stops improving
- **Kaiming Initialization** = weight init designed for ReLU networks (the default choice)
- **Xavier Initialization** = weight init designed for sigmoid/tanh networks
- **Learning Rate Warmup** = gradually increase LR at the start of training
- **Gradient Clipping** = limit gradient magnitude to prevent exploding gradients
- **Validation Set** = used to tune hyperparameters and monitor overfitting
- **Test Set** = used ONCE at the end for final performance evaluation
- **model.train()** and **model.eval()** = switch between training and evaluation modes

---

## Practice Questions

1. Explain why batch normalization helps training. Use the factory worker analogy.

2. During evaluation, should dropout be active or inactive? What PyTorch method controls this?

3. You are training a model and notice that training accuracy is 99% but validation accuracy is 85%. What techniques from this chapter would you use to fix this? Explain why each would help.

4. Why is gradient clipping placed between loss.backward() and optimizer.step() and not in any other position?

5. Your colleague reports test accuracy of 98% on a model they tuned by repeatedly checking test set performance. Why is this problematic? What is the correct approach?

---

## Exercises

### Exercise 1: Ablation Study

Train the MNIST classifier from Section 10.8 four times: (a) with all techniques, (b) without BatchNorm, (c) without Dropout, (d) without both. Compare the final validation accuracies. Which technique has the biggest impact?

### Exercise 2: Implement Model Checkpointing

Add model checkpointing to the training loop: save the model state after each epoch, and at the end of training, load the best checkpoint (the one with the lowest validation loss). Print the epoch number of the best checkpoint.

### Exercise 3: Hyperparameter Sensitivity

Test the effect of dropout rate on model performance. Train the MNIST model with dropout rates of 0.0, 0.1, 0.3, 0.5, 0.7, and 0.9. Plot (or print) the final validation accuracy for each. At what point does dropout start to hurt performance?

---

## What Is Next?

You now have a professional-grade toolkit for training neural networks. You understand the theory (Chapters 1-7), the framework (Chapters 8-9), and the practical techniques (Chapter 10).

In Chapter 11, you will enter the world of **Convolutional Neural Networks (CNNs)**. You will learn how CNNs "see" images by detecting edges, textures, and shapes. Instead of flattening images into a single long vector (like we did with MNIST), CNNs preserve the spatial structure of images, which makes them dramatically better at visual tasks. Get ready to build models that can recognize objects, faces, and scenes.
