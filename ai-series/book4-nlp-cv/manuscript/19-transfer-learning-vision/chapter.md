# Chapter 19: Transfer Learning for Vision

## What You Will Learn

In this chapter, you will learn:

- What transfer learning is and why it is so powerful
- The difference between feature extraction and fine-tuning
- How to use pretrained models (ResNet18, ResNet50) from torchvision
- How to replace the final classification layer for your own task
- How to freeze and unfreeze layers strategically
- Learning rate strategies for transfer learning
- How to build a complete custom dataset classifier using transfer learning

## Why This Chapter Matters

In the previous chapter, you built a CNN from scratch. It worked, but training from scratch has serious limitations:

- **You need a LOT of data.** Thousands to millions of labeled images.
- **Training takes a LONG time.** Hours or days on a GPU.
- **Results are often mediocre.** Your small model cannot learn all the visual patterns that exist in the world.

Transfer learning solves all three problems. Instead of starting from zero, you start with a model that already understands images -- it knows what edges, textures, shapes, and objects look like because it was trained on 1.2 million images from ImageNet.

Think of it like hiring an experienced chef versus training someone who has never cooked. The experienced chef already knows how to chop, saute, and season. You just need to teach them your specific recipes. Transfer learning is the same idea: take a model that already "sees," and teach it your specific task.

In practice, transfer learning is used in the vast majority of real-world computer vision projects. It is not an advanced technique -- it is the default approach.

---

## 19.1 What Is Transfer Learning?

**Transfer learning** means taking knowledge learned from one task and applying it to a different but related task.

```
Training from Scratch:

  Random weights -> Train on YOUR data -> Your model
  (knows nothing)   (needs lots of data)  (limited knowledge)

Transfer Learning:

  ImageNet weights -> Adapt to YOUR data -> Your model
  (knows vision!)    (needs less data)     (leverages millions
                                            of images worth
                                            of knowledge)
```

### What Does a Pretrained Model Already Know?

A model trained on ImageNet has learned a hierarchy of visual features:

```
Layer Depth     What It Learned           Examples
----------------------------------------------------------
Early layers    Edges and textures        |||  ///  ---
(Layer 1-2)                               Lines, gradients

Middle layers   Parts and patterns        Eyes, wheels, petals
(Layer 3-5)                               Stripes, circles

Deep layers     Object parts              Cat face, car door
(Layer 6-10)                              Wing, keyboard

Final layers    Whole objects              Cat, car, bird
(Layer 11+)     (specific to ImageNet)     (1000 ImageNet classes)
```

**Key insight:** The early and middle layers learn **universal** visual features that apply to almost any image task. Only the final layers are specific to the original task (ImageNet's 1000 classes).

```
Transfer Learning Strategy:

Pretrained Model:
+------------------+------------------+-----------+
| Universal        | General          | Specific  |
| Features         | Patterns         | to        |
| (edges, colors)  | (shapes, parts)  | ImageNet  |
+------------------+------------------+-----------+
  KEEP THESE         KEEP (or fine-tune)  REPLACE!

Your Model:
+------------------+------------------+-----------+
| Universal        | General          | Specific  |
| Features         | Patterns         | to YOUR   |
| (edges, colors)  | (shapes, parts)  | task      |
+------------------+------------------+-----------+
  Same as before     Same (or adjusted)  New layer!
```

---

## 19.2 Feature Extraction vs. Fine-Tuning

There are two main approaches to transfer learning:

### Approach 1: Feature Extraction

Use the pretrained model as a fixed feature extractor. Freeze all layers and only train a new classification head.

```
Feature Extraction:

Pretrained CNN (frozen - not updated)     New Head (trained)
+-----+-----+-----+-----+-----+         +--------+
|  C1 |  C2 |  C3 |  C4 |  C5 |  --->   | Linear |
| FRZ | FRZ | FRZ | FRZ | FRZ |         | (new)  |
+-----+-----+-----+-----+-----+         +--------+
                                              |
  These layers DO NOT change                  v
  during training. They act as           Predictions
  a feature extraction machine.          (your classes)

Pros: Fast, works with very little data (even 50 images per class)
Cons: Cannot adapt features to your specific domain
```

### Approach 2: Fine-Tuning

Start with pretrained weights, then train (fine-tune) some or all layers on your data.

```
Fine-Tuning:

Pretrained CNN                            New Head
+-----+-----+-----+-----+-----+         +--------+
|  C1 |  C2 |  C3 |  C4 |  C5 |  --->   | Linear |
| FRZ | FRZ | UPD | UPD | UPD |         | (new)  |
+-----+-----+-----+-----+-----+         +--------+
                                              |
  Early layers frozen                         v
  Later layers updated                   Predictions
  with a small learning rate

Pros: Better accuracy, adapts features to your domain
Cons: Needs more data, risk of overfitting, slower training
```

### When to Use Which?

```
Decision Guide:

                    Little Data              Lots of Data
                    (< 1000 images)          (> 5000 images)
                +--------------------+--------------------+
Similar to      | Feature Extraction | Fine-tune last     |
ImageNet        | (freeze all)       | few layers         |
(natural photos)|                    |                    |
                +--------------------+--------------------+
Different from  | Feature Extraction | Fine-tune most     |
ImageNet        | (might struggle)   | or all layers      |
(medical, sat.) |                    |                    |
                +--------------------+--------------------+
```

---

## 19.3 Loading Pretrained Models

PyTorch's `torchvision.models` provides many pretrained architectures:

```python
import torchvision.models as models
import torch

# Load a pretrained ResNet18
model = models.resnet18(weights="IMAGENET1K_V1")

# Check the model structure
print(model)
```

**Partial output:**
```
ResNet(
  (conv1): Conv2d(3, 64, kernel_size=(7, 7), stride=(2, 2), padding=(3, 3), bias=False)
  (bn1): BatchNorm2d(64)
  (relu): ReLU(inplace=True)
  (maxpool): MaxPool2d(kernel_size=3, stride=2, padding=1)
  (layer1): Sequential(...)
  (layer2): Sequential(...)
  (layer3): Sequential(...)
  (layer4): Sequential(...)
  (avgpool): AdaptiveAvgPool2d(output_size=(1, 1))
  (fc): Linear(in_features=512, out_features=1000, bias=True)  <-- THIS!
)
```

**Key observation:** The last layer `(fc)` has `out_features=1000` because ImageNet has 1000 classes. We need to replace this for our task.

### Available Pretrained Models

```python
# Common pretrained models
resnet18 = models.resnet18(weights="IMAGENET1K_V1")    # 11.7M params
resnet50 = models.resnet50(weights="IMAGENET1K_V1")    # 25.6M params
vgg16 = models.vgg16(weights="IMAGENET1K_V1")          # 138M params
mobilenet_v2 = models.mobilenet_v2(weights="IMAGENET1K_V1")  # 3.4M params

# Check parameters
for name, m in [("ResNet18", resnet18), ("ResNet50", resnet50),
                ("VGG16", vgg16), ("MobileNetV2", mobilenet_v2)]:
    params = sum(p.numel() for p in m.parameters())
    print(f"{name}: {params/1e6:.1f}M parameters")

# Output:
# ResNet18: 11.7M parameters
# ResNet50: 25.6M parameters
# VGG16: 138.4M parameters
# MobileNetV2: 3.5M parameters
```

```
Choosing a Model:

Model         Params    Accuracy   Speed    Best For
----------------------------------------------------------
MobileNetV2   3.5M      71.9%      Fast     Mobile/edge devices
ResNet18      11.7M     69.8%      Fast     Quick experiments
ResNet50      25.6M     76.1%      Medium   Good balance
VGG16         138.4M    71.6%      Slow     Legacy, simple
EfficientNet  5.3M      77.1%      Medium   Best accuracy/size

For most projects, start with ResNet18 (fast iteration)
and move to ResNet50 or EfficientNet for production.
```

---

## 19.4 Replacing the Final Layer

The final layer must be replaced to match your number of classes:

### ResNet

```python
import torch
import torch.nn as nn
import torchvision.models as models

# Load pretrained ResNet18
model = models.resnet18(weights="IMAGENET1K_V1")

# Check the original final layer
print(f"Original fc layer: {model.fc}")
# Output: Original fc layer: Linear(in_features=512, out_features=1000, bias=True)

# Replace with your number of classes
num_classes = 5   # e.g., 5 types of flowers

# Get the number of input features
num_features = model.fc.in_features
print(f"Number of input features: {num_features}")
# Output: Number of input features: 512

# Replace the final layer
model.fc = nn.Linear(num_features, num_classes)

print(f"New fc layer: {model.fc}")
# Output: New fc layer: Linear(in_features=512, out_features=5, bias=True)

# Test with a dummy input
dummy = torch.randn(2, 3, 224, 224)
output = model(dummy)
print(f"Output shape: {output.shape}")
# Output: Output shape: torch.Size([2, 5])
```

**Line-by-line explanation:**

- `model.fc.in_features`: Gets the number of features the final layer expects as input. This is 512 for ResNet18 and 2048 for ResNet50.
- `model.fc = nn.Linear(num_features, num_classes)`: Replaces the final layer. The new layer has random weights -- this is the only part that needs training from scratch.

### ResNet50 (Different Input Features)

```python
# ResNet50 has more features in the final layer
model50 = models.resnet50(weights="IMAGENET1K_V1")
print(f"ResNet50 fc input features: {model50.fc.in_features}")
# Output: ResNet50 fc input features: 2048

model50.fc = nn.Linear(2048, num_classes)
print(f"New fc layer: {model50.fc}")
# Output: New fc layer: Linear(in_features=2048, out_features=5, bias=True)
```

### Adding a More Complex Head

For better performance, you can replace the single linear layer with a small network:

```python
num_features = model.fc.in_features

model.fc = nn.Sequential(
    nn.Linear(num_features, 256),
    nn.ReLU(),
    nn.Dropout(0.5),
    nn.Linear(256, num_classes)
)

print(f"New classifier head:\n{model.fc}")
# Output:
# New classifier head:
# Sequential(
#   (0): Linear(in_features=512, out_features=256, bias=True)
#   (1): ReLU()
#   (2): Dropout(p=0.5, inplace=False)
#   (3): Linear(in_features=256, out_features=5, bias=True)
# )
```

---

## 19.5 Freezing and Unfreezing Layers

**Freezing** a layer means preventing its weights from being updated during training. You do this by setting `requires_grad = False` on its parameters.

### Freezing All Layers (Feature Extraction)

```python
import torchvision.models as models
import torch.nn as nn

# Load pretrained model
model = models.resnet18(weights="IMAGENET1K_V1")

# Freeze ALL parameters
for param in model.parameters():
    param.requires_grad = False

# Replace the final layer (new layer has requires_grad=True by default)
num_features = model.fc.in_features
model.fc = nn.Linear(num_features, 5)

# Verify: count trainable vs frozen parameters
trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
frozen = sum(p.numel() for p in model.parameters() if not p.requires_grad)
total = trainable + frozen

print(f"Trainable parameters: {trainable:,}")
print(f"Frozen parameters: {frozen:,}")
print(f"Total parameters: {total:,}")
print(f"Trainable: {trainable/total*100:.1f}%")

# Output:
# Trainable parameters: 2,565
# Frozen parameters: 11,176,512
# Total parameters: 11,179,077
# Trainable: 0.0%
```

**Line-by-line explanation:**

- `param.requires_grad = False`: Tells PyTorch not to compute gradients for this parameter. No gradients means no weight updates.
- The new `nn.Linear` layer has `requires_grad=True` by default, so it WILL be trained.
- Only 2,565 out of 11 million parameters will be updated. This is extremely fast to train.

### Freezing Early Layers, Unfreezing Later Layers (Fine-Tuning)

```python
import torchvision.models as models
import torch.nn as nn

model = models.resnet18(weights="IMAGENET1K_V1")

# First, freeze everything
for param in model.parameters():
    param.requires_grad = False

# Unfreeze layer4 (the last conv block)
for param in model.layer4.parameters():
    param.requires_grad = True

# Replace and unfreeze the final layer
num_features = model.fc.in_features
model.fc = nn.Linear(num_features, 5)
# (model.fc parameters have requires_grad=True by default)

# Check what is trainable
print("Layer-by-layer trainability:")
for name, param in model.named_parameters():
    status = "TRAINABLE" if param.requires_grad else "frozen"
    print(f"  {name:40s} {str(param.shape):20s} {status}")

# Count
trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
total = sum(p.numel() for p in model.parameters())
print(f"\nTrainable: {trainable:,} / {total:,} ({trainable/total*100:.1f}%)")

# Output (abbreviated):
#   conv1.weight                              torch.Size([64, 3, 7, 7])  frozen
#   ...
#   layer3.1.conv2.weight                     torch.Size([256, 256, 3, 3])  frozen
#   layer4.0.conv1.weight                     torch.Size([512, 256, 3, 3])  TRAINABLE
#   layer4.0.conv2.weight                     torch.Size([512, 512, 3, 3])  TRAINABLE
#   ...
#   fc.weight                                 torch.Size([5, 512])  TRAINABLE
#   fc.bias                                   torch.Size([5])  TRAINABLE
# Trainable: 2,621,957 / 11,179,077 (23.5%)
```

```
Freezing Strategy:

Freeze everything, unfreeze last block:
+-----+-----+-----+-----+-----+-----+
| C1  | C2  | L1  | L2  | L3  | L4  |  FC
| FRZ | FRZ | FRZ | FRZ | FRZ | UPD |  UPD
+-----+-----+-----+-----+-----+-----+

The more layers you unfreeze:
  - More flexibility to adapt to your task
  - But more risk of overfitting
  - And slower training

Start frozen, gradually unfreeze if needed.
```

### Gradual Unfreezing

A popular technique is to gradually unfreeze layers during training:

```python
def unfreeze_model_gradually(model, epoch):
    """Unfreeze more layers as training progresses."""
    if epoch == 0:
        # Epoch 0: Only train fc layer (everything else frozen)
        for param in model.parameters():
            param.requires_grad = False
        for param in model.fc.parameters():
            param.requires_grad = True

    elif epoch == 3:
        # Epoch 3: Also unfreeze layer4
        for param in model.layer4.parameters():
            param.requires_grad = True

    elif epoch == 6:
        # Epoch 6: Also unfreeze layer3
        for param in model.layer3.parameters():
            param.requires_grad = True

    elif epoch == 9:
        # Epoch 9: Unfreeze everything
        for param in model.parameters():
            param.requires_grad = True

    trainable = sum(p.numel() for p in model.parameters()
                    if p.requires_grad)
    print(f"Epoch {epoch}: {trainable:,} trainable parameters")
```

---

## 19.6 Learning Rate Strategies

Transfer learning requires careful learning rate management. The pretrained layers already have good weights -- you do not want to destroy them with large updates.

### Strategy 1: Small Learning Rate for Everything

```python
import torch.optim as optim

# Use a learning rate 10x smaller than training from scratch
optimizer = optim.Adam(model.parameters(), lr=0.0001)
```

### Strategy 2: Discriminative Learning Rates

Use different learning rates for different parts of the model. The pretrained layers get a tiny learning rate; the new layers get a larger one.

```python
import torch.optim as optim

# Group parameters with different learning rates
param_groups = [
    # Pretrained layers: very small learning rate
    {
        "params": [p for name, p in model.named_parameters()
                   if "fc" not in name and p.requires_grad],
        "lr": 0.00001   # 10x smaller
    },
    # New classification head: normal learning rate
    {
        "params": model.fc.parameters(),
        "lr": 0.001     # Standard learning rate
    },
]

optimizer = optim.Adam(param_groups)

# Verify
for i, group in enumerate(optimizer.param_groups):
    num_params = sum(p.numel() for p in group["params"])
    print(f"Group {i}: lr={group['lr']}, params={num_params:,}")

# Output:
# Group 0: lr=1e-05, params=2,619,392
# Group 1: lr=0.001, params=2,565
```

```
Discriminative Learning Rates:

Pretrained layers:  lr = 0.00001 (tiny adjustments)
  +-----+-----+-----+-----+-----+
  |     |     |     |     |     |
  | barely change   | slightly  |
  +-----+-----+-----+-----+-----+

New head:           lr = 0.001  (normal updates)
  +--------+
  |        |
  | learns |
  | fast   |
  +--------+

This prevents destroying the pretrained knowledge
while allowing the new head to learn quickly.
```

### Strategy 3: Learning Rate Scheduler

Reduce the learning rate over time for better convergence:

```python
import torch.optim as optim
from torch.optim import lr_scheduler

optimizer = optim.Adam(model.parameters(), lr=0.001)

# Reduce lr by 0.1 every 7 epochs
scheduler = lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)

# In your training loop:
# for epoch in range(num_epochs):
#     train_one_epoch(...)
#     scheduler.step()  # <-- Call after each epoch
#     print(f"Current lr: {scheduler.get_last_lr()}")

# Alternative: Reduce when validation loss stops improving
scheduler = lr_scheduler.ReduceLROnPlateau(
    optimizer,
    mode="min",        # Monitor a metric that should decrease
    factor=0.1,        # Multiply lr by 0.1 when triggered
    patience=3,        # Wait 3 epochs of no improvement
    verbose=True       # Print a message when lr changes
)

# Usage in training loop:
# scheduler.step(val_loss)  # Pass the metric to monitor
```

---

## 19.7 Complete Transfer Learning Pipeline

Here is a complete, production-ready transfer learning pipeline:

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
import time
import copy
import numpy as np
import matplotlib.pyplot as plt

# ============================================
# Step 1: Data Preparation
# ============================================

train_transforms = transforms.Compose([
    transforms.RandomResizedCrop(224),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225]),
])

val_transforms = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225]),
])

# Load datasets
train_dataset = datasets.ImageFolder("dataset/train",
                                      transform=train_transforms)
val_dataset = datasets.ImageFolder("dataset/val",
                                    transform=val_transforms)

train_loader = DataLoader(train_dataset, batch_size=32,
                          shuffle=True, num_workers=4)
val_loader = DataLoader(val_dataset, batch_size=32,
                        shuffle=False, num_workers=4)

class_names = train_dataset.classes
num_classes = len(class_names)
print(f"Classes: {class_names}")
print(f"Training images: {len(train_dataset)}")
print(f"Validation images: {len(val_dataset)}")

# ============================================
# Step 2: Build Transfer Learning Model
# ============================================

def create_transfer_model(num_classes, freeze_backbone=True):
    """Create a ResNet18 model for transfer learning."""

    # Load pretrained ResNet18
    model = models.resnet18(weights="IMAGENET1K_V1")

    # Optionally freeze the backbone
    if freeze_backbone:
        for param in model.parameters():
            param.requires_grad = False

    # Replace the final layer
    num_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Linear(num_features, 256),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(256, num_classes)
    )

    return model

model = create_transfer_model(num_classes, freeze_backbone=True)

# Count parameters
trainable = sum(p.numel() for p in model.parameters()
                if p.requires_grad)
total = sum(p.numel() for p in model.parameters())
print(f"\nTrainable: {trainable:,} / {total:,} "
      f"({trainable/total*100:.2f}%)")

# ============================================
# Step 3: Training
# ============================================

def train_transfer_model(model, train_loader, val_loader,
                         num_epochs=15, lr=0.001):
    """Train with early stopping and best model tracking."""

    device = torch.device("cuda" if torch.cuda.is_available()
                          else "cpu")
    model = model.to(device)
    print(f"Training on: {device}")

    # Only optimize parameters that require gradients
    params_to_optimize = [p for p in model.parameters()
                          if p.requires_grad]
    print(f"Optimizing {len(params_to_optimize)} parameter groups")

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(params_to_optimize, lr=lr)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.1, patience=3, verbose=True
    )

    # Track best model
    best_val_acc = 0.0
    best_model_weights = copy.deepcopy(model.state_dict())
    history = {"train_loss": [], "train_acc": [],
               "val_loss": [], "val_acc": []}

    for epoch in range(num_epochs):
        start_time = time.time()

        # --- Training ---
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        train_loss = running_loss / total
        train_acc = correct / total

        # --- Validation ---
        model.eval()
        running_loss = 0.0
        correct = 0
        total = 0

        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)

                outputs = model(images)
                loss = criterion(outputs, labels)

                running_loss += loss.item() * images.size(0)
                _, predicted = torch.max(outputs, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

        val_loss = running_loss / total
        val_acc = correct / total

        # Update scheduler
        scheduler.step(val_loss)

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_model_weights = copy.deepcopy(model.state_dict())

        # Record history
        history["train_loss"].append(train_loss)
        history["train_acc"].append(train_acc)
        history["val_loss"].append(val_loss)
        history["val_acc"].append(val_acc)

        elapsed = time.time() - start_time
        print(f"Epoch [{epoch+1}/{num_epochs}] "
              f"Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | "
              f"Val Loss: {val_loss:.4f} Acc: {val_acc:.4f} | "
              f"Time: {elapsed:.1f}s")

    # Load best model weights
    model.load_state_dict(best_model_weights)
    print(f"\nBest Validation Accuracy: {best_val_acc:.4f}")

    return model, history

# Train
model, history = train_transfer_model(
    model, train_loader, val_loader,
    num_epochs=15, lr=0.001
)

# Output:
# Training on: cuda
# Optimizing 4 parameter groups
# Epoch [1/15] Train Loss: 1.2345 Acc: 0.5200 | Val Loss: 0.8765 Acc: 0.7200 | Time: 2.3s
# Epoch [2/15] Train Loss: 0.7654 Acc: 0.7800 | Val Loss: 0.5432 Acc: 0.8500 | Time: 2.1s
# ...
# Epoch [15/15] Train Loss: 0.1234 Acc: 0.9700 | Val Loss: 0.2345 Acc: 0.9400 | Time: 2.2s
# Best Validation Accuracy: 0.9500
```

**Line-by-line explanation:**

- `params_to_optimize = [p for p in model.parameters() if p.requires_grad]`: Only includes parameters that are not frozen. This is crucial -- passing frozen parameters to the optimizer wastes memory and can cause subtle bugs.
- `copy.deepcopy(model.state_dict())`: Saves a deep copy of the best model weights. This way, even if later epochs make the model worse, we keep the best version.
- `scheduler.step(val_loss)`: Tells the scheduler the current validation loss. If it has not improved for `patience` epochs, the learning rate is reduced.

### Step 4: Fine-Tuning After Feature Extraction

A common workflow is to first train with frozen backbone (feature extraction), then unfreeze and fine-tune:

```python
# Phase 1: Feature extraction (already done above)
# model has been trained with frozen backbone

# Phase 2: Unfreeze and fine-tune
print("\n=== Phase 2: Fine-tuning ===")

# Unfreeze the last two residual blocks
for param in model.layer3.parameters():
    param.requires_grad = True
for param in model.layer4.parameters():
    param.requires_grad = True

trainable = sum(p.numel() for p in model.parameters()
                if p.requires_grad)
total = sum(p.numel() for p in model.parameters())
print(f"Trainable: {trainable:,} / {total:,} ({trainable/total*100:.1f}%)")

# Fine-tune with a smaller learning rate
model, history_ft = train_transfer_model(
    model, train_loader, val_loader,
    num_epochs=10,
    lr=0.0001   # 10x smaller than before!
)
```

```
Two-Phase Training:

Phase 1: Feature Extraction
  - Freeze backbone, train only new head
  - Learning rate: 0.001
  - Epochs: 10-15
  - Purpose: Get the new head working

Phase 2: Fine-Tuning
  - Unfreeze some backbone layers
  - Learning rate: 0.0001 (smaller!)
  - Epochs: 5-10
  - Purpose: Adapt features to your domain
```

---

## 19.8 Comparing From-Scratch vs. Transfer Learning

Let us compare the results side by side:

```python
import matplotlib.pyplot as plt

def compare_approaches(scratch_history, transfer_history):
    """Compare training from scratch vs transfer learning."""

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Loss comparison
    ax1.plot(scratch_history["val_loss"], label="From Scratch",
             linestyle="--", marker="o")
    ax1.plot(transfer_history["val_loss"], label="Transfer Learning",
             marker="s")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Validation Loss")
    ax1.set_title("Validation Loss Comparison")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Accuracy comparison
    ax2.plot(scratch_history["val_acc"], label="From Scratch",
             linestyle="--", marker="o")
    ax2.plot(transfer_history["val_acc"], label="Transfer Learning",
             marker="s")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Validation Accuracy")
    ax2.set_title("Validation Accuracy Comparison")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

# compare_approaches(scratch_history, transfer_history)
```

```
Typical Results:

                     From Scratch    Transfer Learning
---------------------------------------------------------
Training time         Long (hours)   Short (minutes)
Data needed           Thousands+     Hundreds
Best val accuracy     ~70-80%        ~90-95%
Epochs to converge    50+            10-15
```

---

## 19.9 Using ResNet50 for Higher Accuracy

For better accuracy, use a deeper model like ResNet50:

```python
import torch
import torch.nn as nn
import torchvision.models as models

def create_resnet50_model(num_classes, freeze_backbone=True):
    """Create a ResNet50 transfer learning model."""

    model = models.resnet50(weights="IMAGENET1K_V1")

    if freeze_backbone:
        for param in model.parameters():
            param.requires_grad = False

    # ResNet50 fc layer has 2048 input features (vs 512 for ResNet18)
    num_features = model.fc.in_features
    print(f"ResNet50 fc input features: {num_features}")

    model.fc = nn.Sequential(
        nn.Linear(num_features, 512),
        nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(512, num_classes)
    )

    trainable = sum(p.numel() for p in model.parameters()
                    if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"Trainable: {trainable:,} / {total:,}")

    return model

model_r50 = create_resnet50_model(num_classes=5, freeze_backbone=True)
# Output:
# ResNet50 fc input features: 2048
# Trainable: 1,049,093 / 24,606,533
```

---

## 19.10 Practical Tips

### Tip 1: Check If Transfer Learning Is Helping

```python
import torch
import torchvision.models as models
import torch.nn as nn

# Model A: Random weights (no transfer learning)
model_random = models.resnet18(weights=None)  # No pretrained weights
model_random.fc = nn.Linear(512, num_classes)

# Model B: Pretrained weights (transfer learning)
model_pretrained = models.resnet18(weights="IMAGENET1K_V1")
model_pretrained.fc = nn.Linear(512, num_classes)

# Train both and compare. If pretrained is not better,
# your data might be too different from ImageNet.
```

### Tip 2: Handling Small Datasets

```python
# For very small datasets (< 100 images per class):

# 1. Use aggressive augmentation
aggressive_transforms = transforms.Compose([
    transforms.RandomResizedCrop(224, scale=(0.5, 1.0)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomVerticalFlip(),        # If orientation does not matter
    transforms.RandomRotation(30),
    transforms.ColorJitter(0.3, 0.3, 0.3, 0.15),
    transforms.RandomGrayscale(p=0.1),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225]),
])

# 2. Use feature extraction (freeze everything)
# 3. Use a simpler head (fewer parameters = less overfitting)
model.fc = nn.Linear(num_features, num_classes)  # No hidden layers
```

### Tip 3: Saving the Complete Pipeline

```python
import torch

# Save everything needed to recreate the model
torch.save({
    "model_name": "resnet18",
    "num_classes": num_classes,
    "class_names": class_names,
    "model_state_dict": model.state_dict(),
    "freeze_backbone": False,
    "best_val_acc": best_val_acc,
}, "transfer_model.pth")

# Load and recreate
checkpoint = torch.load("transfer_model.pth")
model = create_transfer_model(
    checkpoint["num_classes"],
    freeze_backbone=checkpoint["freeze_backbone"]
)
model.load_state_dict(checkpoint["model_state_dict"])
model.eval()

print(f"Loaded model for: {checkpoint['class_names']}")
print(f"Best accuracy: {checkpoint['best_val_acc']:.4f}")
```

---

## Common Mistakes

1. **Not freezing pretrained layers during feature extraction.** If you train all 11 million parameters on 200 images, the model will massively overfit and forget everything it learned from ImageNet.

2. **Using too high a learning rate for fine-tuning.** A learning rate of 0.01 will destroy the pretrained weights in a few batches. Use 0.0001 or smaller for fine-tuning pretrained layers.

3. **Forgetting to only optimize unfrozen parameters.** Passing frozen parameters to the optimizer does not cause errors, but it wastes memory. Filter with `[p for p in model.parameters() if p.requires_grad]`.

4. **Not using ImageNet normalization.** Pretrained models expect input normalized with ImageNet statistics. Using different normalization (or none) throws off all the learned features.

5. **Using training transforms during inference.** Random augmentations during prediction make results non-deterministic and often worse. Always use deterministic validation transforms.

---

## Best Practices

1. **Start with feature extraction** (frozen backbone). If accuracy is not good enough, switch to fine-tuning.

2. **Use discriminative learning rates.** Smaller learning rate for pretrained layers, larger for new layers.

3. **Monitor for overfitting carefully.** Transfer learning models can overfit quickly on small datasets because they are so powerful. Use dropout, early stopping, and data augmentation.

4. **Save the best model based on validation accuracy,** not the final epoch's model. The best epoch is often not the last one.

5. **Start with ResNet18 for prototyping,** then try ResNet50 or EfficientNet for production. Bigger models are slower but more accurate.

---

## Quick Summary

Transfer learning takes a model pretrained on ImageNet and adapts it to your task. Feature extraction freezes all pretrained layers and only trains a new classification head -- fast and works with little data. Fine-tuning unfreezes some pretrained layers and updates them with a small learning rate -- slower but more accurate. Replace the model's final layer to match your number of classes. Use discriminative learning rates (small for pretrained layers, larger for new layers). A two-phase approach (feature extraction first, then fine-tuning) often gives the best results.

---

## Key Points

- Transfer learning reuses knowledge from models trained on millions of images, dramatically reducing data and time requirements.
- Feature extraction (frozen backbone) trains only the new head. Fine-tuning also updates some pretrained layers.
- Always replace the final classification layer to match your number of classes.
- Freeze layers with `param.requires_grad = False`. New layers have `requires_grad = True` by default.
- Use a 10x smaller learning rate for fine-tuning pretrained layers compared to the new head.
- ImageNet normalization (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]) is mandatory for pretrained models.
- Save the best model weights during training, not just the final weights.

---

## Practice Questions

1. Why do early layers of a pretrained CNN learn features that are useful for almost any image task? What types of features do they learn?

2. You have 50 images per class. Should you use feature extraction or fine-tuning? Explain your reasoning.

3. What happens if you fine-tune a pretrained model with a learning rate of 0.01 (same as training from scratch)? Why is this bad?

4. Explain why you need to use ImageNet normalization when using a model pretrained on ImageNet, even if your images are very different from ImageNet images.

5. You replaced ResNet18's final layer with `nn.Linear(512, 10)`. But when you try ResNet50, it crashes. What went wrong, and how do you fix it?

---

## Exercises

### Exercise 1: Feature Extraction Pipeline

Build a complete feature extraction pipeline:
1. Load a pretrained ResNet18
2. Freeze all layers
3. Replace the final layer for 3 classes
4. Train on a small dataset for 10 epochs
5. Report training and validation accuracy
6. Save the best model

### Exercise 2: Feature Extraction vs. Fine-Tuning

Compare two approaches on the same dataset:
1. Feature extraction (frozen backbone, lr=0.001)
2. Fine-tuning (unfreeze layer4, lr=0.0001)

Plot both training curves on the same graph and compare final accuracies.

### Exercise 3: Discriminative Learning Rates

Implement discriminative learning rates for ResNet18:
- conv1, layer1, layer2: lr = 0.00001
- layer3, layer4: lr = 0.0001
- fc (new head): lr = 0.001

Train for 15 epochs and compare results to using a single learning rate for all layers.

---

## What Is Next?

So far, you have learned to classify entire images -- answering "what is this image?" The next chapter takes you further: **Object Detection**. Instead of just classifying an image, object detection finds AND locates every object in an image, drawing bounding boxes around them. You will learn about YOLO, one of the most popular real-time object detection systems, and use it to detect objects in your own images.
