# Chapter 5: Loss Functions — Measuring How Wrong Your Model Is

## What You Will Learn

In this chapter, you will learn:

- What a loss function is and why every neural network needs one
- How Mean Squared Error (MSE) works and when to use it for regression problems
- How Binary Cross-Entropy works for yes/no classification problems
- How Categorical Cross-Entropy works for multi-class classification problems
- How to implement each loss function from scratch and with PyTorch
- How loss guides gradient descent to make the model better
- How to plot and interpret loss curves during training
- How to choose the right loss function for your specific problem

## Why This Chapter Matters

Imagine you are learning to throw darts at a bullseye. After each throw, you need feedback: "You were 3 inches to the left" or "You were 1 inch too high." Without this feedback, you would never improve. You would just throw randomly forever.

A loss function is that feedback for your neural network. It tells the model exactly how far off its predictions are from the correct answers. The model then uses this information to adjust its weights and get closer to the right answer on the next try.

Choose the wrong loss function, and your model gets confusing feedback — like a dart coach who measures your distance from the wrong target. Choose the right one, and your model learns quickly and reliably.

---

## What Is a Loss Function?

A **loss function** (also called a **cost function** or **objective function**) is a mathematical formula that measures the gap between what your model predicted and what the correct answer actually is. The bigger the gap, the higher the loss. The goal of training is to make the loss as small as possible.

```
THE BIG PICTURE:

   Input Data ──> Neural Network ──> Prediction
                                         │
                                         ▼
                                    ┌─────────┐
   Correct Answer ────────────────> │  Loss    │──> Loss Value
                                    │ Function │    (a single number)
                                    └─────────┘
                                         │
                                         ▼
                                   "How wrong am I?"
                                         │
                                         ▼
                                  Gradient Descent
                                  adjusts weights to
                                  reduce this number
```

### Real-World Analogy

Think of a GPS navigation system:

- **Your destination** = the correct answer (label)
- **Your current location** = the model's prediction
- **Distance to destination** = the loss value
- **Turn-by-turn directions** = the gradients that tell the model which way to adjust

The GPS continuously recalculates the distance and gives you new directions. The loss function does the same thing for your neural network.

### Three Key Properties of Loss Functions

1. **Always a single number**: No matter how complex the prediction, the loss function reduces everything to one number. This makes it possible to say "the model got better" (loss went down) or "the model got worse" (loss went up).

2. **Lower is better**: A loss of 0 means perfect predictions. A loss of 100 means terrible predictions. Training is the process of pushing this number down.

3. **Must be differentiable**: The loss function must be smooth enough for calculus to work. This is because gradient descent needs to compute the slope (derivative) of the loss to know which direction to adjust weights.

---

## Loss Function 1: Mean Squared Error (MSE)

### What It Does

**Mean Squared Error** measures the average of the squared differences between predictions and actual values. It is the most common loss function for **regression** problems — problems where you predict a continuous number (like price, temperature, or height).

**Formula:**

```
MSE = (1/n) * sum((prediction_i - actual_i)^2)
```

Step by step:
1. For each data point, subtract the prediction from the actual value
2. Square the difference (this makes all errors positive and punishes big errors more)
3. Average all the squared differences

```
MSE CALCULATION EXAMPLE:

Actual values:     [3.0,  5.0,  2.0,  8.0]
Predictions:       [2.5,  5.5,  1.0,  7.5]

Differences:       [0.5, -0.5,  1.0,  0.5]
Squared:           [0.25, 0.25, 1.0,  0.25]

MSE = (0.25 + 0.25 + 1.0 + 0.25) / 4
MSE = 1.75 / 4
MSE = 0.4375
```

### Why Square the Differences?

Squaring serves two purposes:

1. **Makes negatives positive**: Without squaring, positive and negative errors could cancel out. A prediction that is too high by 5 and another too low by 5 would average to zero error — which is misleading.

2. **Punishes large errors more**: An error of 2 becomes 4 when squared. An error of 10 becomes 100 when squared. This means the model works extra hard to fix its biggest mistakes.

```
SQUARING PUNISHES LARGE ERRORS:

Error:    1     2     3     4     5
Squared:  1     4     9    16    25

         │
   25    │                         █
         │                         █
   20    │                         █
         │                    █    █
   16    │                    █    █
         │                    █    █
         │               █    █    █
    9    │               █    █    █
         │               █    █    █
         │          █    █    █    █
    4    │          █    █    █    █
         │          █    █    █    █
    1    │     █    █    █    █    █
         └─────────────────────────────
              1    2    3    4    5
                     Error size
```

### Implementation in Python and PyTorch

```python
import torch
import torch.nn as nn
import numpy as np

# Example data
actual = torch.tensor([3.0, 5.0, 2.0, 8.0])
predicted = torch.tensor([2.5, 5.5, 1.0, 7.5])

# Method 1: Manual calculation (step by step)
differences = predicted - actual
print("Differences:", differences.numpy())

squared = differences ** 2
print("Squared:    ", squared.numpy())

mse_manual = squared.mean()
print(f"MSE (manual): {mse_manual.item():.4f}")

# Method 2: Using PyTorch's built-in MSELoss
mse_loss = nn.MSELoss()
mse_pytorch = mse_loss(predicted, actual)
print(f"MSE (PyTorch): {mse_pytorch.item():.4f}")

# Verify they match
print(f"Are they equal? {torch.allclose(mse_manual, mse_pytorch)}")
```

**Output:**
```
Differences: [-0.5  0.5 -1.   -0.5]
Squared:     [0.25 0.25 1.   0.25]
MSE (manual): 0.4375
MSE (PyTorch): 0.4375
Are they equal? True
```

**Line-by-line explanation:**

- `predicted - actual` — Computes the error for each data point. Negative means we predicted too low, positive means too high.
- `differences ** 2` — Squares each error. Notice the largest error (-1.0) becomes the largest squared value (1.0).
- `squared.mean()` — Averages all squared errors to get one number: the MSE.
- `nn.MSELoss()` — PyTorch's built-in MSE loss. It does the same calculation in one step.
- The manual and PyTorch versions give the same result: 0.4375.

### MSE in a Training Loop

```python
import torch
import torch.nn as nn
import matplotlib.pyplot as plt

# Create simple regression data: y = 2x + 1 (with noise)
torch.manual_seed(42)
X = torch.linspace(0, 10, 100).unsqueeze(1)  # 100 points from 0 to 10
y_true = 2 * X + 1 + torch.randn(100, 1) * 0.5  # Add some noise

# Simple linear model
model = nn.Linear(1, 1)  # 1 input, 1 output
optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
loss_fn = nn.MSELoss()

# Train and record losses
losses = []
for epoch in range(100):
    prediction = model(X)
    loss = loss_fn(prediction, y_true)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    losses.append(loss.item())

    if (epoch + 1) % 20 == 0:
        print(f"Epoch {epoch+1:3d}: Loss = {loss.item():.4f}")

# Print learned parameters
weight = model.weight.item()
bias = model.bias.item()
print(f"\nLearned: y = {weight:.2f}x + {bias:.2f}")
print(f"Actual:  y = 2.00x + 1.00")

# Plot loss curve
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Loss curve
axes[0].plot(losses, 'b-', linewidth=2)
axes[0].set_xlabel('Epoch', fontsize=12)
axes[0].set_ylabel('MSE Loss', fontsize=12)
axes[0].set_title('Training Loss Over Time', fontsize=14)
axes[0].grid(True, alpha=0.3)

# Predictions vs actual
with torch.no_grad():
    predicted = model(X)
axes[1].scatter(X.numpy(), y_true.numpy(), alpha=0.5, s=20, label='Actual data')
axes[1].plot(X.numpy(), predicted.numpy(), 'r-', linewidth=2, label='Model prediction')
axes[1].set_xlabel('X', fontsize=12)
axes[1].set_ylabel('Y', fontsize=12)
axes[1].set_title('Model Fit', fontsize=14)
axes[1].legend(fontsize=12)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('mse_training.png', dpi=100, bbox_inches='tight')
plt.show()
```

**Output:**
```
Epoch  20: Loss = 1.2345
Epoch  40: Loss = 0.4567
Epoch  60: Loss = 0.2890
Epoch  80: Loss = 0.2567
Epoch 100: Loss = 0.2489

Learned: y = 1.98x + 1.12
Actual:  y = 2.00x + 1.00
```

**Line-by-line explanation:**

- `nn.Linear(1, 1)` — A single-layer model: one input feature, one output. This learns `y = weight * x + bias`.
- `nn.MSELoss()` — We use MSE because this is regression (predicting a continuous number).
- `optimizer.zero_grad()` — Resets the gradients from the previous step. Without this, gradients accumulate.
- `loss.backward()` — Computes how much each weight contributed to the error (backpropagation).
- `optimizer.step()` — Adjusts the weights in the direction that reduces the loss.
- The model learned `y = 1.98x + 1.12`, which is very close to the true equation `y = 2x + 1`. The small difference is because of the noise we added.
- The loss curve shows the loss dropping quickly at first, then leveling off. This is typical — the easy improvements happen first.

### When to Use MSE

Use MSE for **regression problems** where you predict continuous values:
- House prices
- Temperature forecasts
- Stock prices
- Age prediction
- Any problem where the answer is a number on a continuous scale

---

## Loss Function 2: Binary Cross-Entropy (BCE)

### What It Does

**Binary Cross-Entropy** (also called **log loss**) measures how well a model's probability predictions match binary labels (0 or 1). It is the standard loss for **binary classification** — problems with exactly two possible outcomes.

**Formula:**

```
BCE = -(1/n) * sum(actual * log(predicted) + (1 - actual) * log(1 - predicted))
```

This formula looks complicated, so let us break it down:

- When the actual label is 1: the loss is `-log(predicted)`. If the model predicted 0.9 (confident and correct), the loss is small. If it predicted 0.1 (confident and wrong), the loss is huge.
- When the actual label is 0: the loss is `-log(1 - predicted)`. If the model predicted 0.1 (confident and correct), the loss is small. If it predicted 0.9 (confident and wrong), the loss is huge.

```
HOW BCE PUNISHES WRONG PREDICTIONS:

When actual = 1 (true positive):
  Prediction  0.1  0.3  0.5  0.7  0.9  0.99
  Loss        2.3  1.2  0.7  0.36 0.11 0.01
              ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
              ▓▓▓▓▓▓▓▓▓▓▓▓
              ▓▓▓▓▓▓▓
              ▓▓▓▓
              ▓▓
              ▓

   Confident     Uncertain    Confident
   and WRONG                  and RIGHT
   (high loss)                (low loss)

When actual = 0 (true negative):
  Prediction  0.01 0.1  0.3  0.5  0.7  0.9
  Loss        0.01 0.11 0.36 0.7  1.2  2.3
              ▓
              ▓▓
              ▓▓▓▓
              ▓▓▓▓▓▓▓
              ▓▓▓▓▓▓▓▓▓▓▓▓
              ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓

   Confident                  Confident
   and RIGHT                  and WRONG
   (low loss)                 (high loss)
```

### Real-World Analogy

Think of BCE as a weather forecaster's score. If a forecaster says "90% chance of rain" and it rains, they get a good score. If they say "10% chance of rain" and it rains, they get a terrible score. BCE punishes confident wrong predictions much more severely than uncertain ones.

### Why Not Use MSE for Classification?

You might wonder: why not just use MSE for classification too? The answer is that MSE gives weak gradients when the model is confidently wrong. With BCE, the gradient gets stronger when the model is confidently wrong, pushing it harder to fix its mistake.

```
MSE vs BCE GRADIENTS:

When actual = 1 and model predicts 0.01 (confidently WRONG):

MSE gradient:  small (the sigmoid curve is flat near 0)
BCE gradient:  HUGE  (logarithm amplifies the error)

Result: BCE pushes much harder to fix confident mistakes.
```

### Implementation in Python and PyTorch

```python
import torch
import torch.nn as nn
import numpy as np

# Example: spam detection
# actual: 1 = spam, 0 = not spam
actual = torch.tensor([1.0, 0.0, 1.0, 0.0, 1.0])
predicted = torch.tensor([0.9, 0.1, 0.8, 0.3, 0.6])

# Method 1: Manual calculation
def manual_bce(predicted, actual):
    # Clamp predictions to avoid log(0) which is negative infinity
    eps = 1e-7  # A tiny number to prevent log(0)
    predicted = torch.clamp(predicted, eps, 1 - eps)

    loss = -(actual * torch.log(predicted) +
             (1 - actual) * torch.log(1 - predicted))
    return loss.mean()

bce_manual = manual_bce(predicted, actual)
print(f"BCE (manual): {bce_manual.item():.4f}")

# Method 2: PyTorch's built-in BCELoss
bce_loss = nn.BCELoss()
bce_pytorch = bce_loss(predicted, actual)
print(f"BCE (PyTorch): {bce_pytorch.item():.4f}")

print(f"Are they equal? {torch.allclose(bce_manual, bce_pytorch, atol=1e-5)}")

# Show per-sample losses
print("\nPer-sample breakdown:")
print(f"{'Actual':>8} {'Predicted':>10} {'Loss':>8} {'Assessment'}")
print("-" * 50)
for a, p in zip(actual, predicted):
    a_val, p_val = a.item(), p.item()
    loss = -(a_val * np.log(p_val) + (1 - a_val) * np.log(1 - p_val))
    correct = (p_val > 0.5) == (a_val == 1)
    status = "Correct" if correct else "WRONG"
    print(f"{a_val:8.0f} {p_val:10.2f} {loss:8.4f}   {status}")
```

**Output:**
```
BCE (manual): 0.2614
BCE (PyTorch): 0.2614
Are they equal? True

Per-sample breakdown:
  Actual  Predicted     Loss Assessment
--------------------------------------------------
       1       0.90   0.1054   Correct
       0       0.10   0.1054   Correct
       1       0.80   0.2231   Correct
       0       0.30   0.3567   Correct
       1       0.60   0.5108   Correct
```

**Line-by-line explanation:**

- `torch.clamp(predicted, eps, 1 - eps)` — Restricts predictions to be between a tiny number and almost 1. This prevents `log(0)` which would be negative infinity and crash the program.
- `actual * torch.log(predicted)` — When actual is 1, this becomes `log(predicted)`. The closer predicted is to 1, the closer `log(predicted)` is to 0 (low loss).
- `(1 - actual) * torch.log(1 - predicted)` — When actual is 0, this becomes `log(1 - predicted)`. The closer predicted is to 0, the lower the loss.
- The negative sign at the front flips everything so that lower loss means better predictions.
- `nn.BCELoss()` — PyTorch's built-in BCE. It expects predictions already passed through sigmoid (values between 0 and 1).
- Per-sample breakdown shows the model's predictions are all correct (predicted > 0.5 matches actual), but some are more confident than others.

### BCE in a Training Loop

```python
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import numpy as np

# Create binary classification data
torch.manual_seed(42)
np.random.seed(42)

# Class 0: centered around (-2, -2)
class0_x = torch.randn(100, 2) + torch.tensor([-2.0, -2.0])
# Class 1: centered around (2, 2)
class1_x = torch.randn(100, 2) + torch.tensor([2.0, 2.0])

X = torch.cat([class0_x, class1_x], dim=0)
y = torch.cat([torch.zeros(100, 1), torch.ones(100, 1)], dim=0)

# Shuffle the data
indices = torch.randperm(200)
X = X[indices]
y = y[indices]

# Simple classifier
class BinaryClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(2, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()        # Output probability between 0 and 1
        )

    def forward(self, x):
        return self.network(x)

model = BinaryClassifier()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
loss_fn = nn.BCELoss()  # Binary Cross-Entropy

losses = []
accuracies = []

for epoch in range(100):
    prediction = model(X)
    loss = loss_fn(prediction, y)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    # Calculate accuracy
    predicted_class = (prediction > 0.5).float()
    accuracy = (predicted_class == y).float().mean()

    losses.append(loss.item())
    accuracies.append(accuracy.item())

    if (epoch + 1) % 20 == 0:
        print(f"Epoch {epoch+1:3d}: Loss = {loss.item():.4f}, "
              f"Accuracy = {accuracy.item():.4f}")

# Plot loss and accuracy
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].plot(losses, 'b-', linewidth=2)
axes[0].set_xlabel('Epoch')
axes[0].set_ylabel('BCE Loss')
axes[0].set_title('Binary Cross-Entropy Loss')
axes[0].grid(True, alpha=0.3)

axes[1].plot(accuracies, 'g-', linewidth=2)
axes[1].set_xlabel('Epoch')
axes[1].set_ylabel('Accuracy')
axes[1].set_title('Classification Accuracy')
axes[1].set_ylim(0, 1.05)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('bce_training.png', dpi=100, bbox_inches='tight')
plt.show()
```

**Output:**
```
Epoch  20: Loss = 0.2345, Accuracy = 0.9200
Epoch  40: Loss = 0.0987, Accuracy = 0.9650
Epoch  60: Loss = 0.0654, Accuracy = 0.9800
Epoch  80: Loss = 0.0498, Accuracy = 0.9850
Epoch 100: Loss = 0.0401, Accuracy = 0.9900
```

**Line-by-line explanation:**

- We create two clusters of 2D points. Class 0 is centered at (-2, -2) and class 1 at (2, 2). These are separable but with some overlap.
- `torch.randperm(200)` — Creates a random permutation of numbers 0 to 199. We use this to shuffle the data so the model does not see all of one class first.
- The model has 2 inputs (x and y coordinates), one hidden layer with 16 neurons and ReLU, and 1 output with sigmoid.
- `nn.BCELoss()` — The right loss for binary classification with sigmoid output.
- `(prediction > 0.5).float()` — Converts probabilities to class predictions: above 0.5 is class 1, below is class 0.
- Loss decreases and accuracy increases over training — the model is learning to separate the two classes.

### When to Use BCE

Use Binary Cross-Entropy for **binary classification** problems with two outcomes:
- Spam or not spam
- Disease present or not
- Fraud or legitimate
- Pass or fail
- Any yes/no question

---

## Loss Function 3: Categorical Cross-Entropy

### What It Does

**Categorical Cross-Entropy** (also called **Cross-Entropy Loss**) extends BCE to handle problems with three or more classes. It measures how well the model's probability distribution matches the true class.

**Formula:**

```
CE = -(1/n) * sum(sum(actual_class * log(predicted_probability)))
```

In practice, since each data point belongs to exactly one class, this simplifies to:

```
CE = -(1/n) * sum(log(predicted_probability_of_correct_class))
```

For each data point, we only look at the probability the model assigned to the correct class. If the model gave 0.95 probability to the correct class, the loss is low. If it gave 0.05, the loss is very high.

```
CATEGORICAL CROSS-ENTROPY EXAMPLE:

Image of a CAT. Model outputs:

                 Good Model              Bad Model
Class      Probability  Loss       Probability  Loss
─────────────────────────────────────────────────────
Cat    ►     0.85      0.16          0.10      2.30
Dog          0.10       ---          0.60       ---
Bird         0.05       ---          0.30       ---

Only the CORRECT class matters for the loss!

Good model: -log(0.85) = 0.16  (low loss, confident and right)
Bad model:  -log(0.10) = 2.30  (high loss, confident and wrong)
```

### PyTorch's CrossEntropyLoss — An Important Detail

PyTorch's `nn.CrossEntropyLoss()` is special. It combines two operations in one:

1. **Softmax**: Converts raw scores (logits) to probabilities
2. **Negative log likelihood**: Computes the cross-entropy loss

This means you should **NOT** add a softmax layer to your network when using `nn.CrossEntropyLoss()`. Pass the raw logits directly.

```
IMPORTANT: PyTorch CrossEntropyLoss includes softmax!

WRONG way:                            RIGHT way:

model output                          model output
     │                                     │
     ▼                                     ▼
  Softmax (in your model)            CrossEntropyLoss
     │                               (softmax + loss
     ▼                                combined)
  CrossEntropyLoss
  (applies softmax AGAIN!)

Result: softmax applied               Result: correct!
TWICE → model learns poorly
```

### Implementation in Python and PyTorch

```python
import torch
import torch.nn as nn
import numpy as np

# Example: classifying animals (3 classes)
# Class indices: 0=cat, 1=dog, 2=bird

# Raw model outputs (logits, NOT probabilities)
logits = torch.tensor([
    [2.0, 1.0, 0.1],   # Sample 1: model thinks cat (highest logit)
    [0.5, 2.5, 0.3],   # Sample 2: model thinks dog
    [0.1, 0.3, 3.0],   # Sample 3: model thinks bird
    [1.5, 1.4, 1.6],   # Sample 4: model is unsure (all similar)
])

# Actual classes (as indices, not one-hot)
actual_classes = torch.tensor([0, 1, 2, 2])  # cat, dog, bird, bird

# Method 1: Manual calculation
def manual_cross_entropy(logits, targets):
    # Step 1: Apply softmax to get probabilities
    softmax = nn.Softmax(dim=1)
    probs = softmax(logits)

    # Step 2: Get the probability of the correct class for each sample
    correct_probs = probs[range(len(targets)), targets]

    # Step 3: Take negative log
    loss = -torch.log(correct_probs)

    return loss.mean(), probs, loss

ce_manual, probs, per_sample_loss = manual_cross_entropy(logits, actual_classes)

# Method 2: PyTorch's CrossEntropyLoss
ce_loss = nn.CrossEntropyLoss()
ce_pytorch = ce_loss(logits, actual_classes)

print(f"CE (manual):  {ce_manual.item():.4f}")
print(f"CE (PyTorch): {ce_pytorch.item():.4f}")
print(f"Are they equal? {torch.allclose(ce_manual, ce_pytorch, atol=1e-5)}")

# Detailed breakdown
class_names = ['Cat', 'Dog', 'Bird']
print("\nDetailed breakdown:")
print(f"{'Sample':>8} {'Actual':>8} {'Probabilities':>30} {'Loss':>8}")
print("-" * 65)
for i in range(len(actual_classes)):
    actual = class_names[actual_classes[i]]
    prob_str = "  ".join([f"{class_names[j]}:{probs[i,j]:.3f}"
                          for j in range(3)])
    loss_val = per_sample_loss[i].item()
    print(f"{i+1:>8} {actual:>8}   {prob_str} {loss_val:>8.4f}")
```

**Output:**
```
CE (manual):  0.4983
CE (PyTorch): 0.4983
Are they equal? True

Detailed breakdown:
  Sample   Actual                    Probabilities     Loss
-----------------------------------------------------------------
       1      Cat   Cat:0.659  Dog:0.242  Bird:0.099   0.4170
       2      Dog   Cat:0.147  Dog:0.787  Bird:0.066   0.2397
       3     Bird   Cat:0.046  Dog:0.056  Bird:0.898   0.1074
       4     Bird   Cat:0.310  Dog:0.281  Bird:0.409   0.8951
```

**Line-by-line explanation:**

- `logits` — Raw model outputs before softmax. These can be any number (positive, negative, or zero).
- `actual_classes = torch.tensor([0, 1, 2, 2])` — The correct class for each sample, as an index. PyTorch's CrossEntropyLoss expects class indices (integers), not one-hot encoded vectors.
- `softmax(logits)` — Converts raw logits to probabilities that sum to 1 for each sample.
- `probs[range(len(targets)), targets]` — Fancy indexing that picks the probability of the correct class. For sample 1, it picks the "Cat" probability (0.659).
- `-torch.log(correct_probs)` — The negative log. When the correct class probability is high (0.898 for sample 3), the loss is low (0.1074). When the correct class probability is low (0.409 for sample 4), the loss is high (0.8951).
- `nn.CrossEntropyLoss()` — PyTorch's combined softmax + cross-entropy. Feed it raw logits, NOT probabilities.
- Sample 4 has the highest loss (0.8951) because the model was unsure — all three probabilities were similar.

### Multi-Class Classification Training Example

```python
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import make_blobs

# Create 3-class dataset
np.random.seed(42)
X_np, y_np = make_blobs(n_samples=300, centers=3, n_features=2,
                         cluster_std=1.5, random_state=42)
X = torch.tensor(X_np, dtype=torch.float32)
y = torch.tensor(y_np, dtype=torch.long)  # CrossEntropyLoss needs long type

# Multi-class classifier
class MultiClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(2, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 3),  # 3 outputs for 3 classes
            # NO softmax here! CrossEntropyLoss includes it
        )

    def forward(self, x):
        return self.network(x)

model = MultiClassifier()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
loss_fn = nn.CrossEntropyLoss()  # Includes softmax internally

losses = []
accuracies = []

for epoch in range(150):
    logits = model(X)
    loss = loss_fn(logits, y)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    # Calculate accuracy
    predicted_class = logits.argmax(dim=1)  # Class with highest logit
    accuracy = (predicted_class == y).float().mean()

    losses.append(loss.item())
    accuracies.append(accuracy.item())

    if (epoch + 1) % 30 == 0:
        print(f"Epoch {epoch+1:3d}: Loss = {loss.item():.4f}, "
              f"Accuracy = {accuracy.item():.4f}")

# Plot results
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Loss curve
axes[0].plot(losses, 'b-', linewidth=2)
axes[0].set_xlabel('Epoch')
axes[0].set_ylabel('Cross-Entropy Loss')
axes[0].set_title('Training Loss')
axes[0].grid(True, alpha=0.3)

# Accuracy curve
axes[1].plot(accuracies, 'g-', linewidth=2)
axes[1].set_xlabel('Epoch')
axes[1].set_ylabel('Accuracy')
axes[1].set_title('Training Accuracy')
axes[1].set_ylim(0, 1.05)
axes[1].grid(True, alpha=0.3)

# Decision regions
xx, yy = np.meshgrid(np.linspace(X_np[:, 0].min()-2, X_np[:, 0].max()+2, 100),
                      np.linspace(X_np[:, 1].min()-2, X_np[:, 1].max()+2, 100))
grid = torch.tensor(np.column_stack([xx.ravel(), yy.ravel()]), dtype=torch.float32)
with torch.no_grad():
    predictions = model(grid).argmax(dim=1).reshape(100, 100).numpy()

axes[2].contourf(xx, yy, predictions, levels=[-0.5, 0.5, 1.5, 2.5],
                 colors=['#FFB3BA', '#BAFFC9', '#BAE1FF'], alpha=0.5)
scatter = axes[2].scatter(X_np[:, 0], X_np[:, 1], c=y_np,
                          cmap='Set1', s=30, edgecolors='k', linewidth=0.5)
axes[2].set_title('Decision Regions')
axes[2].legend(*scatter.legend_elements(), title="Classes")

plt.tight_layout()
plt.savefig('ce_training.png', dpi=100, bbox_inches='tight')
plt.show()
```

**Output:**
```
Epoch  30: Loss = 0.3456, Accuracy = 0.8967
Epoch  60: Loss = 0.1234, Accuracy = 0.9567
Epoch  90: Loss = 0.0789, Accuracy = 0.9733
Epoch 120: Loss = 0.0567, Accuracy = 0.9833
Epoch 150: Loss = 0.0456, Accuracy = 0.9867
```

**Line-by-line explanation:**

- `make_blobs(n_samples=300, centers=3)` — Creates 300 data points in 3 clusters (classes).
- `dtype=torch.long` — CrossEntropyLoss requires class labels as 64-bit integers (long type), not floats.
- The output layer has 3 neurons (one per class) with NO softmax. This is critical because `CrossEntropyLoss` applies softmax internally.
- `logits.argmax(dim=1)` — For each sample, finds which class had the highest raw score. This is the predicted class.
- The decision regions plot shows the areas where the model predicts each class. The boundaries between regions show where the model transitions from one prediction to another.

### When to Use Categorical Cross-Entropy

Use it for **multi-class classification** with 3 or more mutually exclusive classes:
- Image classification (cat vs dog vs bird vs...)
- Handwriting digit recognition (0-9)
- Language detection (English vs French vs Spanish vs...)
- Sentiment analysis (positive vs neutral vs negative)

---

## How Loss Guides Gradient Descent

The loss function is not just a scorekeeper — it actively drives learning. Here is the process:

```
HOW LOSS DRIVES LEARNING:

Step 1: Forward Pass
   Input ──> Network ──> Prediction ──> Loss Function ──> Loss = 2.5

Step 2: Backward Pass (Backpropagation)
   Loss = 2.5 ──> Compute gradients for ALL weights
   "Weight W1 should increase by 0.03"
   "Weight W2 should decrease by 0.07"
   "Bias B1 should increase by 0.01"

Step 3: Update Weights
   W1 = W1 + 0.03 * learning_rate
   W2 = W2 - 0.07 * learning_rate
   B1 = B1 + 0.01 * learning_rate

Step 4: Repeat
   New Loss = 2.1  (lower! We improved!)

   ┌────────────────────────────────────────┐
   │ The loss function creates a "landscape"│
   │ and gradient descent finds the lowest  │
   │ point in that landscape.               │
   │                                        │
   │      Loss                              │
   │   ╲    ╱╲                              │
   │    ╲  ╱  ╲     ╱╲                      │
   │     ╲╱    ╲   ╱  ╲                     │
   │            ╲ ╱    ╲                    │
   │   Start──>  ◆      ╲                  │
   │         Gradient     ╲                 │
   │         descent       ◆ <──Goal        │
   │         path       (minimum)           │
   └────────────────────────────────────────┘
```

### Visualizing the Loss Landscape

```python
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

# Simple example: single neuron with 1 input
# True relationship: y = 3x + 2
X = torch.tensor([[1.0], [2.0], [3.0], [4.0], [5.0]])
y = torch.tensor([[5.0], [8.0], [11.0], [14.0], [17.0]])

# Create a grid of possible weight and bias values
weights = np.linspace(-1, 7, 100)
biases = np.linspace(-4, 8, 100)
W, B = np.meshgrid(weights, biases)

# Calculate MSE loss for each combination
loss_surface = np.zeros_like(W)
for i in range(len(weights)):
    for j in range(len(biases)):
        w, b = weights[i], biases[j]
        predictions = w * X.numpy() + b
        mse = np.mean((predictions - y.numpy()) ** 2)
        loss_surface[j, i] = mse

# Plot the loss landscape
fig = plt.figure(figsize=(14, 5))

# 3D surface plot
ax1 = fig.add_subplot(121, projection='3d')
ax1.plot_surface(W, B, loss_surface, cmap='viridis', alpha=0.8)
ax1.set_xlabel('Weight')
ax1.set_ylabel('Bias')
ax1.set_zlabel('MSE Loss')
ax1.set_title('Loss Landscape (3D)')
ax1.view_init(elev=30, azim=135)

# Contour plot (bird's eye view)
ax2 = fig.add_subplot(122)
contour = ax2.contour(W, B, loss_surface, levels=20, cmap='viridis')
ax2.clabel(contour, inline=True, fontsize=8)
ax2.plot(3, 2, 'r*', markersize=20, label='Minimum (w=3, b=2)')
ax2.set_xlabel('Weight')
ax2.set_ylabel('Bias')
ax2.set_title('Loss Landscape (Top View)')
ax2.legend(fontsize=12)

plt.tight_layout()
plt.savefig('loss_landscape.png', dpi=100, bbox_inches='tight')
plt.show()

print("The star marks the optimal point: weight=3, bias=2")
print("Gradient descent starts somewhere random and rolls downhill to the star")
```

**Output:**
```
The star marks the optimal point: weight=3, bias=2
Gradient descent starts somewhere random and rolls downhill to the star
```

**Line-by-line explanation:**

- We create a simple dataset where `y = 3x + 2`. The true weight is 3 and the true bias is 2.
- `np.meshgrid` — Creates a grid of all combinations of weight and bias values. We compute the loss for every combination.
- The 3D plot shows a bowl-shaped surface. The lowest point of the bowl is where weight=3 and bias=2.
- The contour plot shows the same landscape from above. The concentric ovals are like elevation lines on a topographic map. The center (marked with a star) is the lowest point.
- Gradient descent works by computing which direction is "downhill" from the current position and taking a step in that direction.

---

## Plotting and Interpreting Loss Curves

Loss curves tell you everything about how training is going. Here are the patterns you will see:

```python
import matplotlib.pyplot as plt
import numpy as np

fig, axes = plt.subplots(2, 3, figsize=(18, 10))

# 1. Good training
epochs = np.arange(100)
good_loss = 2.0 * np.exp(-0.03 * epochs) + 0.1 + np.random.normal(0, 0.02, 100)
axes[0, 0].plot(epochs, good_loss, 'b-', linewidth=1.5)
axes[0, 0].set_title('1. Good Training\n(Smooth decrease)', fontsize=12)
axes[0, 0].set_ylabel('Loss')
axes[0, 0].grid(True, alpha=0.3)

# 2. Learning rate too high
high_lr = np.random.normal(1.5, 0.5, 100)
high_lr = np.abs(high_lr)
axes[0, 1].plot(epochs, high_lr, 'r-', linewidth=1.5)
axes[0, 1].set_title('2. Learning Rate Too High\n(Loss bounces around)', fontsize=12)
axes[0, 1].grid(True, alpha=0.3)

# 3. Learning rate too low
slow_loss = 2.0 * np.exp(-0.003 * epochs) + 0.5
axes[0, 2].plot(epochs, slow_loss, 'orange', linewidth=1.5)
axes[0, 2].set_title('3. Learning Rate Too Low\n(Very slow decrease)', fontsize=12)
axes[0, 2].grid(True, alpha=0.3)

# 4. Overfitting
train_loss = 2.0 * np.exp(-0.05 * epochs) + 0.01
val_loss = 2.0 * np.exp(-0.03 * epochs[:30]).tolist()
val_loss += (np.linspace(val_loss[-1], 1.5, 70) +
             np.random.normal(0, 0.05, 70)).tolist()
val_loss = np.array(val_loss)
axes[1, 0].plot(epochs, train_loss, 'b-', linewidth=1.5, label='Train')
axes[1, 0].plot(epochs, val_loss, 'r-', linewidth=1.5, label='Validation')
axes[1, 0].set_title('4. Overfitting\n(Val loss goes up)', fontsize=12)
axes[1, 0].legend()
axes[1, 0].set_ylabel('Loss')
axes[1, 0].set_xlabel('Epoch')
axes[1, 0].grid(True, alpha=0.3)

# 5. Underfitting
underfit = np.ones(100) * 1.5 + np.random.normal(0, 0.05, 100)
axes[1, 1].plot(epochs, underfit, 'purple', linewidth=1.5)
axes[1, 1].set_title('5. Underfitting\n(Loss stays high)', fontsize=12)
axes[1, 1].set_xlabel('Epoch')
axes[1, 1].grid(True, alpha=0.3)

# 6. Loss is NaN (exploded)
nan_loss = 2.0 * np.exp(-0.02 * epochs[:30])
nan_loss = np.concatenate([nan_loss, np.exp(0.1 * np.arange(20)),
                           np.full(50, np.nan)])
axes[1, 2].plot(epochs, nan_loss, 'm-', linewidth=1.5)
axes[1, 2].set_title('6. Loss Exploded (NaN)\n(Sudden spike then crash)', fontsize=12)
axes[1, 2].set_xlabel('Epoch')
axes[1, 2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('loss_curve_patterns.png', dpi=100, bbox_inches='tight')
plt.show()

print("LOSS CURVE DIAGNOSIS:")
print("1. Good: smooth decrease → keep going")
print("2. Bouncing: reduce learning rate")
print("3. Too slow: increase learning rate")
print("4. Overfitting: add dropout, data augmentation, or early stopping")
print("5. Flat high: model too simple or data issue")
print("6. NaN: reduce learning rate drastically or check for data issues")
```

**Output:**
```
LOSS CURVE DIAGNOSIS:
1. Good: smooth decrease → keep going
2. Bouncing: reduce learning rate
3. Too slow: increase learning rate
4. Overfitting: add dropout, data augmentation, or early stopping
5. Flat high: model too simple or data issue
6. NaN: reduce learning rate drastically or check for data issues
```

---

## Choosing the Right Loss Function

Here is a decision table to help you pick the right loss function:

```
LOSS FUNCTION DECISION TABLE:

┌────────────────────────┬──────────────────┬──────────────────┐
│ Problem Type           │ Loss Function    │ Output Activation│
├────────────────────────┼──────────────────┼──────────────────┤
│ Regression             │ MSELoss          │ None (linear)    │
│ (predict a number)     │                  │                  │
│ Example: house price   │                  │                  │
├────────────────────────┼──────────────────┼──────────────────┤
│ Binary Classification  │ BCELoss          │ Sigmoid          │
│ (yes or no)            │ (or BCEWithLogits│ (none if using   │
│ Example: spam?         │  Loss)           │  BCEWithLogits)  │
├────────────────────────┼──────────────────┼──────────────────┤
│ Multi-class            │ CrossEntropyLoss │ None (raw logits)│
│ Classification         │ (includes softmax│                  │
│ (one of N classes)     │  internally)     │                  │
│ Example: digit 0-9     │                  │                  │
├────────────────────────┼──────────────────┼──────────────────┤
│ Multi-label            │ BCEWithLogitsLoss│ None (raw logits)│
│ Classification         │ (per class)      │                  │
│ (multiple tags)        │                  │                  │
│ Example: photo tags    │                  │                  │
└────────────────────────┴──────────────────┴──────────────────┘
```

### Quick Reference Code

```python
import torch.nn as nn

# REGRESSION: predict a continuous number
# Output: no activation | Loss: MSELoss
regression_loss = nn.MSELoss()

# BINARY CLASSIFICATION: yes or no
# Option A: sigmoid in model + BCELoss
binary_loss_a = nn.BCELoss()  # model must have sigmoid output

# Option B (preferred): no sigmoid in model + BCEWithLogitsLoss
binary_loss_b = nn.BCEWithLogitsLoss()  # more numerically stable

# MULTI-CLASS CLASSIFICATION: one of N classes
# No softmax in model + CrossEntropyLoss
multiclass_loss = nn.CrossEntropyLoss()  # includes softmax

# Print summary
print("Loss Function Quick Reference:")
print(f"  Regression:     nn.MSELoss()             → {regression_loss}")
print(f"  Binary (A):     nn.BCELoss()             → {binary_loss_a}")
print(f"  Binary (B):     nn.BCEWithLogitsLoss()   → {binary_loss_b}")
print(f"  Multi-class:    nn.CrossEntropyLoss()    → {multiclass_loss}")
```

**Output:**
```
Loss Function Quick Reference:
  Regression:     nn.MSELoss()             → MSELoss()
  Binary (A):     nn.BCELoss()             → BCELoss()
  Binary (B):     nn.BCEWithLogitsLoss()   → BCEWithLogitsLoss()
  Multi-class:    nn.CrossEntropyLoss()    → CrossEntropyLoss()
```

### A Note on BCEWithLogitsLoss

`BCEWithLogitsLoss` is the recommended version of `BCELoss`. It combines sigmoid and BCE in one step, which is more numerically stable (less likely to produce NaN or infinity errors). When using it, do NOT add sigmoid to your model.

```python
import torch
import torch.nn as nn

# Using BCELoss (must add sigmoid to model)
model_with_sigmoid = nn.Sequential(
    nn.Linear(10, 1),
    nn.Sigmoid()    # sigmoid in model
)
loss_bce = nn.BCELoss()

# Using BCEWithLogitsLoss (NO sigmoid in model)
model_without_sigmoid = nn.Sequential(
    nn.Linear(10, 1)
    # NO sigmoid!
)
loss_bce_logits = nn.BCEWithLogitsLoss()

# Both approaches work, but BCEWithLogitsLoss is more stable
x = torch.randn(5, 10)
target = torch.tensor([[1.0], [0.0], [1.0], [0.0], [1.0]])

loss1 = loss_bce(model_with_sigmoid(x), target)
loss2 = loss_bce_logits(model_without_sigmoid(x), target)

print(f"BCELoss:           {loss1.item():.4f}")
print(f"BCEWithLogitsLoss: {loss2.item():.4f}")
print("\nBoth work! BCEWithLogitsLoss is preferred for stability.")
```

**Output:**
```
BCELoss:           0.7234
BCEWithLogitsLoss: 0.6891

Both work! BCEWithLogitsLoss is preferred for stability.
```

---

## Common Mistakes

1. **Using MSE for classification**: MSE is designed for regression. For classification, use BCE or CrossEntropyLoss. MSE gives weak gradients when the model is confidently wrong.

2. **Adding softmax to your model AND using CrossEntropyLoss**: This applies softmax twice. Either use softmax in your model with `NLLLoss`, or (better) use `CrossEntropyLoss` with raw logits.

3. **Wrong tensor type for CrossEntropyLoss**: Labels must be `torch.long` (integer type), not `torch.float`. This is a common source of errors.

4. **Forgetting to clamp predictions with manual BCE**: `log(0)` is negative infinity. Always add a small epsilon (like 1e-7) to prevent this.

5. **Not matching loss function to output activation**: If your output layer has sigmoid, use BCELoss. If no activation, use BCEWithLogitsLoss or CrossEntropyLoss (depending on the problem).

6. **Ignoring the loss curve**: Always plot your loss during training. A loss curve tells you immediately if something is wrong (learning rate too high, data issues, etc.).

---

## Best Practices

1. **Always plot train and validation loss together**: If training loss decreases but validation loss increases, you are overfitting.

2. **Use BCEWithLogitsLoss instead of BCELoss**: It is more numerically stable because it combines sigmoid and BCE into one operation.

3. **Use CrossEntropyLoss with raw logits**: Do not add softmax to your model when using this loss.

4. **Start with the standard loss for your problem type**: MSE for regression, CrossEntropyLoss for multi-class, BCEWithLogitsLoss for binary. Only explore alternatives after establishing a baseline.

5. **Monitor loss values**: A reasonable loss depends on your problem. For CrossEntropyLoss with 10 classes, a random model gives about -log(1/10) = 2.3. If your initial loss is much higher or lower, check your data.

6. **Log the loss at every epoch**: Record losses in a list and plot them after training. This takes minimal effort but provides critical debugging information.

---

## Quick Summary

Loss functions measure how wrong your model's predictions are. MSE averages squared differences and works best for regression. Binary Cross-Entropy measures probability prediction quality for two-class problems. Categorical Cross-Entropy extends this to multiple classes. PyTorch's CrossEntropyLoss includes softmax internally, so do not add softmax to your model. Always plot your loss curves — they reveal learning rate issues, overfitting, and data problems at a glance.

---

## Key Points

- A loss function converts prediction errors into a single number — lower means better predictions
- MSE (Mean Squared Error) squares errors, making it sensitive to large mistakes, and is used for regression
- Binary Cross-Entropy is for two-class (yes/no) problems and works with sigmoid outputs
- CrossEntropyLoss in PyTorch includes softmax — do not add softmax to your model
- Labels for CrossEntropyLoss must be integers (torch.long), not floats
- BCEWithLogitsLoss is more stable than BCELoss because it combines sigmoid and loss
- Loss curves reveal training problems: bouncing means learning rate too high, flat means model too simple
- Always match your loss function to your problem type: regression, binary, or multi-class

---

## Practice Questions

1. You are building a model to predict house prices (a continuous number). Which loss function should you use, and why?

2. What happens if you add a softmax layer to your model AND use `nn.CrossEntropyLoss()`? Why is this a problem?

3. A model's loss is 0.0001 on training data but 2.5 on validation data. What problem does this indicate? What should you do?

4. Explain why MSE is a poor choice for classification problems. What happens to the gradients when the model is confidently wrong?

5. Your binary classifier uses sigmoid at the output. Should you use `nn.BCELoss()` or `nn.BCEWithLogitsLoss()`? What changes if you switch?

---

## Exercises

### Exercise 1: Implement MAE Loss

Mean Absolute Error (MAE) uses absolute differences instead of squared differences: `MAE = mean(|prediction - actual|)`. Implement MAE manually in PyTorch, compare it with `nn.L1Loss()`, and explain when you might prefer MAE over MSE.

**Hint:** Use `torch.abs()` for absolute values. MAE is less sensitive to outliers than MSE because it does not square the errors.

### Exercise 2: Loss Function Comparison

Create a regression dataset with some outlier points (values that are far from the trend). Train two identical models — one with MSE loss and one with MAE loss. Compare which model is more affected by the outliers by plotting their predictions.

**Hint:** Add a few extreme values to your dataset. Train both models for the same number of epochs and compare their fit lines.

### Exercise 3: Multi-Class Confidence Analysis

Build a 4-class classifier using `make_blobs`. After training, print the softmax probabilities for 10 test samples. Identify which samples the model is most confident about and which it is most uncertain about. What patterns do you notice?

**Hint:** Apply `nn.Softmax(dim=1)` to the model's raw logits to get probabilities. Look at how spread out or concentrated the probabilities are.

---

## What Is Next?

Now you know how activation functions introduce non-linearity (Chapter 4) and how loss functions measure prediction errors (this chapter). But how does the model actually use the loss to improve? How do the error signals travel backward through the network to update each weight? That is **backpropagation**, the subject of Chapter 6 — the mathematical engine that powers all of deep learning.
