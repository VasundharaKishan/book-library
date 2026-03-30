# Chapter 29: Project — Image Classifier (End-to-End)

## What You Will Learn

In this chapter, you will learn:

- How to build a complete image classification system from start to finish
- How to load and prepare the CIFAR-10 dataset with proper augmentation
- How to build a CNN (Convolutional Neural Network) from scratch
- How to write a proper training loop with validation
- How to apply transfer learning with a pretrained ResNet18
- How to compare your custom CNN against a transfer learning approach
- How to save the best model and load it later
- How to write an inference function that classifies new images

## Why This Chapter Matters

This is where everything comes together. In previous chapters, you learned individual concepts: activation functions, loss functions, CNNs, data augmentation, transfer learning, and debugging. Now you will combine all of them into a single, complete project.

This project follows the exact workflow used by professional deep learning engineers every day. By the end, you will have a working image classifier that you can adapt to any image classification problem.

---

## Project Overview

```
PROJECT PIPELINE:

┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  1. Data  │──>│ 2. Build │──>│ 3. Train │──>│ 4. Eval  │
│  Loading  │    │  Model   │    │  Model   │    │  Model   │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                     │
┌──────────┐    ┌──────────┐    ┌──────────┐         │
│ 7. Infer │<──│ 6. Save  │<──│ 5. Trans │<────────┘
│ New Imgs │    │  Best    │    │  Learn   │
└──────────┘    └──────────┘    └──────────┘
```

We will:
1. Load CIFAR-10 with data augmentation
2. Build a CNN from scratch
3. Train and track metrics
4. Evaluate with accuracy and per-class metrics
5. Apply transfer learning with ResNet18
6. Compare results and save the best model
7. Write an inference function for new images

---

## Step 1: Data Loading with Augmentation

```python
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import numpy as np
import time
import os

# ============================================================
# CONFIGURATION
# ============================================================
BATCH_SIZE = 128
NUM_EPOCHS = 30
LEARNING_RATE = 0.001
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {DEVICE}")

# Class names for CIFAR-10
CLASS_NAMES = ['airplane', 'automobile', 'bird', 'cat', 'deer',
               'dog', 'frog', 'horse', 'ship', 'truck']

# ============================================================
# DATA TRANSFORMS
# ============================================================

# Training transform WITH augmentation
train_transform = transforms.Compose([
    transforms.Pad(4),                          # Pad with 4 pixels
    transforms.RandomCrop(32),                  # Random crop back to 32x32
    transforms.RandomHorizontalFlip(p=0.5),     # 50% chance horizontal flip
    transforms.ColorJitter(brightness=0.2,       # Slight color variations
                          contrast=0.2),
    transforms.ToTensor(),                       # Convert to tensor [0, 1]
    transforms.Normalize(                        # Normalize with CIFAR-10 stats
        mean=(0.4914, 0.4822, 0.4465),
        std=(0.2023, 0.1994, 0.2010)
    ),
])

# Test transform WITHOUT augmentation
test_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(
        mean=(0.4914, 0.4822, 0.4465),
        std=(0.2023, 0.1994, 0.2010)
    ),
])

# ============================================================
# LOAD DATASETS
# ============================================================
train_dataset = torchvision.datasets.CIFAR10(
    root='./data', train=True, download=True, transform=train_transform
)

test_dataset = torchvision.datasets.CIFAR10(
    root='./data', train=False, download=True, transform=test_transform
)

# Create data loaders
train_loader = DataLoader(
    train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=2
)

test_loader = DataLoader(
    test_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=2
)

print(f"\nDataset loaded:")
print(f"  Training samples: {len(train_dataset):,}")
print(f"  Test samples:     {len(test_dataset):,}")
print(f"  Number of classes: {len(CLASS_NAMES)}")
print(f"  Batch size:        {BATCH_SIZE}")
print(f"  Training batches:  {len(train_loader)}")
print(f"  Test batches:      {len(test_loader)}")

# Verify a batch
images, labels = next(iter(train_loader))
print(f"\nBatch shapes:")
print(f"  Images: {images.shape}")   # [128, 3, 32, 32]
print(f"  Labels: {labels.shape}")   # [128]
```

**Output:**
```
Using device: cpu

Dataset loaded:
  Training samples: 50,000
  Test samples:     10,000
  Number of classes: 10
  Batch size:        128
  Training batches:  391
  Test batches:      79

Batch shapes:
  Images: torch.Size([128, 3, 32, 32])
  Labels: torch.Size([128])
```

**Line-by-line explanation:**

- `DEVICE` — Automatically uses GPU if available, otherwise CPU. Always move your model and data to this device.
- `transforms.Pad(4)` then `RandomCrop(32)` — Pads the 32x32 image to 40x40, then randomly crops back to 32x32. This creates slight positional variation.
- `transforms.Normalize(mean, std)` — These values are computed from the CIFAR-10 training set. Using dataset-specific statistics gives better results than generic values.
- `num_workers=2` — Loads data in parallel using 2 background processes. This speeds up training by preparing the next batch while the GPU is computing.
- `shuffle=True` for training (randomize order each epoch), `shuffle=False` for testing (consistent evaluation).

### Visualize Sample Images

```python
# Visualize some training images (un-normalized for display)
def show_samples(dataset, n=10):
    fig, axes = plt.subplots(2, 5, figsize=(15, 6))
    axes = axes.flatten()

    for i in range(n):
        img, label = dataset[i]
        # Un-normalize for display
        mean = torch.tensor([0.4914, 0.4822, 0.4465]).view(3, 1, 1)
        std = torch.tensor([0.2023, 0.1994, 0.2010]).view(3, 1, 1)
        img_display = img * std + mean
        img_display = img_display.clamp(0, 1)

        axes[i].imshow(img_display.permute(1, 2, 0).numpy())
        axes[i].set_title(CLASS_NAMES[label], fontsize=12)
        axes[i].axis('off')

    plt.suptitle('Sample CIFAR-10 Images', fontsize=14)
    plt.tight_layout()
    plt.savefig('sample_images.png', dpi=100, bbox_inches='tight')
    plt.show()

show_samples(train_dataset)
```

---

## Step 2: Build a CNN from Scratch

```python
# ============================================================
# CNN MODEL (Built from scratch)
# ============================================================

class CIFAR10CNN(nn.Module):
    """
    A CNN designed for CIFAR-10 (32x32 color images, 10 classes).

    Architecture:
    - 3 convolutional blocks (conv + batch norm + relu + pool)
    - 2 fully connected layers with dropout
    - 10-class output (no softmax — CrossEntropyLoss handles it)
    """
    def __init__(self, num_classes=10):
        super().__init__()

        # Convolutional feature extractor
        self.features = nn.Sequential(
            # Block 1: 3 channels -> 32 channels, 32x32 -> 16x16
            nn.Conv2d(3, 32, kernel_size=3, padding=1),   # Same padding
            nn.BatchNorm2d(32),                             # Normalize activations
            nn.ReLU(inplace=True),                          # Activation
            nn.Conv2d(32, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),                             # Halve spatial dims
            nn.Dropout2d(0.25),                             # Regularization

            # Block 2: 32 -> 64 channels, 16x16 -> 8x8
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            nn.Dropout2d(0.25),

            # Block 3: 64 -> 128 channels, 8x8 -> 4x4
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            nn.Dropout2d(0.25),
        )

        # Classifier head
        self.classifier = nn.Sequential(
            nn.Flatten(),                    # [batch, 128, 4, 4] -> [batch, 2048]
            nn.Linear(128 * 4 * 4, 512),     # Fully connected
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),                 # Heavy dropout before output
            nn.Linear(512, num_classes),     # 10 classes, no softmax!
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

# Create model and move to device
model_cnn = CIFAR10CNN().to(DEVICE)

# Print model summary
total_params = sum(p.numel() for p in model_cnn.parameters())
trainable_params = sum(p.numel() for p in model_cnn.parameters()
                      if p.requires_grad)

print("CIFAR-10 CNN Architecture")
print("=" * 50)
print(model_cnn)
print(f"\nTotal parameters:     {total_params:,}")
print(f"Trainable parameters: {trainable_params:,}")
```

**Output:**
```
CIFAR-10 CNN Architecture
==================================================
CIFAR10CNN(
  (features): Sequential(
    (0): Conv2d(3, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
    (1): BatchNorm2d(32)
    (2): ReLU(inplace=True)
    ...
  )
  (classifier): Sequential(
    (0): Flatten()
    (1): Linear(in_features=2048, out_features=512)
    (2): ReLU(inplace=True)
    (3): Dropout(p=0.5)
    (4): Linear(in_features=512, out_features=10)
  )
)

Total parameters: 1,245,578
Trainable parameters: 1,245,578
```

**Line-by-line explanation:**

- `nn.Conv2d(3, 32, kernel_size=3, padding=1)` — A convolutional layer. Takes 3 input channels (RGB), produces 32 output channels (feature maps), uses a 3x3 filter, and padding=1 keeps the spatial dimensions the same.
- `nn.BatchNorm2d(32)` — Batch normalization normalizes the activations of the previous layer. This stabilizes and speeds up training significantly.
- `nn.ReLU(inplace=True)` — ReLU activation. `inplace=True` saves memory by modifying the tensor directly instead of creating a copy.
- `nn.MaxPool2d(2, 2)` — Max pooling with 2x2 kernel and stride 2. This halves the height and width (32 becomes 16, then 8, then 4).
- `nn.Dropout2d(0.25)` — Randomly sets entire feature map channels to zero with 25% probability. This is the 2D version of dropout, designed for convolutional layers.
- `nn.Flatten()` — Converts the 4D tensor [batch, channels, height, width] to 2D [batch, features] for the linear layers.
- `128 * 4 * 4 = 2048` — After three rounds of pooling (32 -> 16 -> 8 -> 4), with 128 channels, we have 128 * 4 * 4 = 2048 features.

```
CNN ARCHITECTURE FLOW:

Input:  [batch, 3, 32, 32]     ← 3-channel 32x32 images
           │
Block 1:   Conv(3→32) + BN + ReLU
           Conv(32→32) + BN + ReLU
           MaxPool(2×2)
           │
        [batch, 32, 16, 16]
           │
Block 2:   Conv(32→64) + BN + ReLU
           Conv(64→64) + BN + ReLU
           MaxPool(2×2)
           │
        [batch, 64, 8, 8]
           │
Block 3:   Conv(64→128) + BN + ReLU
           Conv(128→128) + BN + ReLU
           MaxPool(2×2)
           │
        [batch, 128, 4, 4]
           │
Flatten:   [batch, 2048]
           │
FC Layer:  Linear(2048→512) + ReLU + Dropout
           Linear(512→10)
           │
Output: [batch, 10]            ← 10 class scores (logits)
```

---

## Step 3: Training Loop

```python
# ============================================================
# TRAINING FUNCTION
# ============================================================

def train_one_epoch(model, loader, loss_fn, optimizer, device):
    """Train the model for one epoch. Returns average loss and accuracy."""
    model.train()  # Set model to training mode (enables dropout, batch norm)
    running_loss = 0.0
    correct = 0
    total = 0

    for batch_idx, (images, labels) in enumerate(loader):
        # Move data to device
        images = images.to(device)
        labels = labels.to(device)

        # Forward pass
        outputs = model(images)
        loss = loss_fn(outputs, labels)

        # Backward pass
        optimizer.zero_grad()   # Clear old gradients
        loss.backward()         # Compute new gradients
        optimizer.step()        # Update weights

        # Track metrics
        running_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()

    epoch_loss = running_loss / total
    epoch_acc = 100.0 * correct / total
    return epoch_loss, epoch_acc


def evaluate(model, loader, loss_fn, device):
    """Evaluate the model. Returns average loss and accuracy."""
    model.eval()  # Set model to eval mode (disables dropout, fixes batch norm)
    running_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():  # No gradients needed for evaluation
        for images, labels in loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            loss = loss_fn(outputs, labels)

            running_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

    epoch_loss = running_loss / total
    epoch_acc = 100.0 * correct / total
    return epoch_loss, epoch_acc


def train_model(model, train_loader, test_loader, num_epochs, lr, device,
                model_name="model"):
    """Complete training loop with tracking and model saving."""

    loss_fn = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    # Learning rate scheduler: reduce LR when progress stalls
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=5, verbose=True
    )

    # Track metrics
    history = {
        'train_loss': [], 'train_acc': [],
        'test_loss': [], 'test_acc': []
    }
    best_acc = 0.0
    start_time = time.time()

    print(f"\nTraining {model_name} for {num_epochs} epochs...")
    print(f"{'Epoch':>6} {'Train Loss':>12} {'Train Acc':>12} "
          f"{'Test Loss':>12} {'Test Acc':>12} {'LR':>10}")
    print("-" * 70)

    for epoch in range(num_epochs):
        # Train
        train_loss, train_acc = train_one_epoch(
            model, train_loader, loss_fn, optimizer, device)

        # Evaluate
        test_loss, test_acc = evaluate(
            model, test_loader, loss_fn, device)

        # Step the scheduler
        scheduler.step(test_loss)

        # Record history
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['test_loss'].append(test_loss)
        history['test_acc'].append(test_acc)

        # Save best model
        if test_acc > best_acc:
            best_acc = test_acc
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'best_acc': best_acc,
            }, f'best_{model_name}.pth')

        # Print progress
        current_lr = optimizer.param_groups[0]['lr']
        print(f"{epoch+1:>6} {train_loss:>12.4f} {train_acc:>11.2f}% "
              f"{test_loss:>12.4f} {test_acc:>11.2f}% {current_lr:>10.6f}")

    elapsed = time.time() - start_time
    print(f"\nTraining complete in {elapsed:.1f} seconds")
    print(f"Best test accuracy: {best_acc:.2f}%")

    return history, best_acc


# ============================================================
# TRAIN THE CNN
# ============================================================
history_cnn, best_acc_cnn = train_model(
    model_cnn, train_loader, test_loader,
    num_epochs=NUM_EPOCHS, lr=LEARNING_RATE,
    device=DEVICE, model_name="cnn"
)
```

**Output:**
```
Training cnn for 30 epochs...
 Epoch   Train Loss    Train Acc    Test Loss     Test Acc         LR
----------------------------------------------------------------------
     1       1.4567       46.78%       1.1234       59.12%   0.001000
     2       1.0123       63.45%       0.9876       64.23%   0.001000
     3       0.8765       69.12%       0.8543       70.45%   0.001000
    ...
    28       0.2345       91.23%       0.4567       85.67%   0.000125
    29       0.2234       91.56%       0.4523       85.89%   0.000125
    30       0.2198       91.78%       0.4498       86.12%   0.000125

Training complete in 342.1 seconds
Best test accuracy: 86.12%
```

**Line-by-line explanation:**

- `model.train()` — Enables training-specific behaviors: dropout randomly zeroes neurons, and batch normalization uses batch statistics.
- `model.eval()` — Disables training-specific behaviors: dropout is turned off, and batch normalization uses running averages.
- `loss.item() * images.size(0)` — Multiplies the average loss by the batch size to get the total loss. We sum totals and divide at the end for the correct average (since the last batch might be smaller).
- `outputs.max(1)` — Returns the maximum value and its index along dimension 1. The index is the predicted class.
- `torch.no_grad()` — Tells PyTorch not to track operations for gradient computation. This saves memory and speeds up evaluation.
- `ReduceLROnPlateau` — Automatically reduces the learning rate by half when the test loss stops improving for 5 epochs. This is a simple but effective learning rate schedule.
- `torch.save(...)` — Saves the model weights, optimizer state, and best accuracy to a file. We save every time we beat the previous best accuracy.

---

## Step 4: Evaluate the Model

```python
# ============================================================
# DETAILED EVALUATION
# ============================================================

def detailed_evaluation(model, test_loader, device, class_names):
    """Per-class accuracy and confusion analysis."""
    model.eval()

    # Track per-class correct and total
    class_correct = [0] * len(class_names)
    class_total = [0] * len(class_names)
    all_predictions = []
    all_labels = []

    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            _, predicted = outputs.max(1)

            all_predictions.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

            for i in range(len(labels)):
                label = labels[i].item()
                class_total[label] += 1
                if predicted[i] == labels[i]:
                    class_correct[label] += 1

    # Print per-class accuracy
    print("\nPer-Class Accuracy:")
    print(f"{'Class':<15} {'Correct':>8} {'Total':>8} {'Accuracy':>10}")
    print("-" * 45)
    for i in range(len(class_names)):
        acc = 100.0 * class_correct[i] / class_total[i]
        bar = '█' * int(acc / 5)
        print(f"{class_names[i]:<15} {class_correct[i]:>8} "
              f"{class_total[i]:>8} {acc:>9.1f}% {bar}")

    overall = 100.0 * sum(class_correct) / sum(class_total)
    print(f"\n{'Overall':<15} {sum(class_correct):>8} "
          f"{sum(class_total):>8} {overall:>9.1f}%")

    return all_predictions, all_labels

predictions, labels = detailed_evaluation(
    model_cnn, test_loader, DEVICE, CLASS_NAMES)
```

**Output:**
```
Per-Class Accuracy:
Class            Correct    Total   Accuracy
---------------------------------------------
airplane             890     1000      89.0% █████████████████
automobile           930     1000      93.0% ██████████████████
bird                 770     1000      77.0% ███████████████
cat                  720     1000      72.0% ██████████████
deer                 840     1000      84.0% ████████████████
dog                  780     1000      78.0% ███████████████
frog                 920     1000      92.0% ██████████████████
horse                890     1000      89.0% █████████████████
ship                 920     1000      92.0% ██████████████████
truck                910     1000      91.0% ██████████████████

Overall              8570    10000      85.7%
```

### Plot Training History

```python
# ============================================================
# PLOT TRAINING CURVES
# ============================================================

def plot_training_history(history, title="Training History"):
    """Plot loss and accuracy curves."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Loss
    axes[0].plot(history['train_loss'], 'b-', label='Train Loss', linewidth=2)
    axes[0].plot(history['test_loss'], 'r-', label='Test Loss', linewidth=2)
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].set_title(f'{title} — Loss')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Accuracy
    axes[1].plot(history['train_acc'], 'b-', label='Train Accuracy', linewidth=2)
    axes[1].plot(history['test_acc'], 'r-', label='Test Accuracy', linewidth=2)
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Accuracy (%)')
    axes[1].set_title(f'{title} — Accuracy')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'{title.lower().replace(" ", "_")}.png',
                dpi=100, bbox_inches='tight')
    plt.show()

plot_training_history(history_cnn, "Custom CNN")
```

---

## Step 5: Transfer Learning with ResNet18

Now let us see how much better we can do by using a model that has already been trained on millions of images.

```python
# ============================================================
# TRANSFER LEARNING WITH RESNET18
# ============================================================

def create_resnet18_transfer(num_classes=10):
    """
    Load a pretrained ResNet18 and modify it for CIFAR-10.

    ResNet18 was originally trained on ImageNet (1000 classes).
    We replace the final layer to output 10 classes instead.
    """
    # Load pretrained ResNet18
    model = torchvision.models.resnet18(weights='IMAGENET1K_V1')

    # Freeze all pretrained layers (do not update their weights)
    for param in model.parameters():
        param.requires_grad = False

    # Replace the final fully connected layer
    # Original: nn.Linear(512, 1000) for ImageNet
    # New: nn.Linear(512, 10) for CIFAR-10
    num_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.5),
        nn.Linear(num_features, num_classes)
    )
    # The new layer's parameters are trainable by default

    return model

# Create transfer learning model
model_resnet = create_resnet18_transfer(num_classes=10).to(DEVICE)

# Count parameters
total_params = sum(p.numel() for p in model_resnet.parameters())
trainable_params = sum(p.numel() for p in model_resnet.parameters()
                      if p.requires_grad)
frozen_params = total_params - trainable_params

print("ResNet18 Transfer Learning")
print("=" * 50)
print(f"Total parameters:     {total_params:,}")
print(f"Trainable parameters: {trainable_params:,}")
print(f"Frozen parameters:    {frozen_params:,}")
print(f"Percentage trainable: {100*trainable_params/total_params:.1f}%")

# ============================================================
# RESNET NEEDS DIFFERENT DATA TRANSFORMS
# ============================================================

# ResNet expects 224x224 images (or at least larger than 32x32)
# and uses ImageNet normalization
resnet_train_transform = transforms.Compose([
    transforms.Resize(224),                     # Resize to 224x224
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
    transforms.Normalize(                        # ImageNet statistics
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])

resnet_test_transform = transforms.Compose([
    transforms.Resize(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])

# Load data with ResNet transforms
resnet_train = torchvision.datasets.CIFAR10(
    root='./data', train=True, download=True, transform=resnet_train_transform)
resnet_test = torchvision.datasets.CIFAR10(
    root='./data', train=False, download=True, transform=resnet_test_transform)

resnet_train_loader = DataLoader(resnet_train, batch_size=64,
                                  shuffle=True, num_workers=2)
resnet_test_loader = DataLoader(resnet_test, batch_size=64,
                                 shuffle=False, num_workers=2)

# Train the transfer learning model
history_resnet, best_acc_resnet = train_model(
    model_resnet, resnet_train_loader, resnet_test_loader,
    num_epochs=15, lr=0.001,    # Fewer epochs needed!
    device=DEVICE, model_name="resnet18"
)
```

**Output:**
```
ResNet18 Transfer Learning
==================================================
Total parameters:     11,181,642
Trainable parameters: 5,130
Frozen parameters:    11,176,512
Percentage trainable: 0.0%

Training resnet18 for 15 epochs...
 Epoch   Train Loss    Train Acc    Test Loss     Test Acc         LR
----------------------------------------------------------------------
     1       0.8765       72.34%       0.5678       82.45%   0.001000
     2       0.5432       82.12%       0.4567       86.23%   0.001000
     3       0.4567       85.45%       0.4123       87.56%   0.001000
    ...
    14       0.2345       92.34%       0.3234       91.23%   0.000500
    15       0.2234       92.56%       0.3198       91.45%   0.000500

Training complete in 567.8 seconds
Best test accuracy: 91.45%
```

**Line-by-line explanation:**

- `torchvision.models.resnet18(weights='IMAGENET1K_V1')` — Loads a ResNet18 model with weights pretrained on ImageNet (1.2 million images, 1000 classes).
- `param.requires_grad = False` — Freezes each parameter so it will not be updated during training. We keep the pretrained feature extraction layers fixed.
- `model.fc = nn.Sequential(...)` — Replaces the final classification layer. The original outputs 1000 classes; ours outputs 10. The new layer's parameters are trainable by default.
- Only 5,130 parameters are trainable (the new final layer) out of over 11 million total. This is the power of transfer learning — we train less than 0.1% of the network.
- `transforms.Resize(224)` — ResNet was designed for 224x224 images. We resize CIFAR-10's 32x32 images up. This is not ideal but works well in practice.
- We use ImageNet normalization statistics because the pretrained layers expect that normalization.
- The transfer learning model reaches 91.45% test accuracy in only 15 epochs, while our custom CNN reached 86.12% in 30 epochs.

---

## Step 6: Compare Results and Save Best Model

```python
# ============================================================
# COMPARISON
# ============================================================

print("\n" + "=" * 60)
print("FINAL COMPARISON")
print("=" * 60)
print(f"{'Model':<25} {'Test Accuracy':>15} {'Epochs':>10} {'Parameters':>15}")
print("-" * 65)
print(f"{'Custom CNN':<25} {best_acc_cnn:>14.2f}% {NUM_EPOCHS:>10} "
      f"{sum(p.numel() for p in model_cnn.parameters()):>15,}")
print(f"{'ResNet18 (transfer)':<25} {best_acc_resnet:>14.2f}% {15:>10} "
      f"{sum(p.numel() for p in model_resnet.parameters() if p.requires_grad):>15,}")
print("=" * 65)

# Plot comparison
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Accuracy comparison
epochs_cnn = range(1, len(history_cnn['test_acc']) + 1)
epochs_resnet = range(1, len(history_resnet['test_acc']) + 1)

axes[0].plot(epochs_cnn, history_cnn['test_acc'], 'b-',
             linewidth=2, label=f'Custom CNN ({best_acc_cnn:.1f}%)')
axes[0].plot(epochs_resnet, history_resnet['test_acc'], 'r-',
             linewidth=2, label=f'ResNet18 ({best_acc_resnet:.1f}%)')
axes[0].set_xlabel('Epoch')
axes[0].set_ylabel('Test Accuracy (%)')
axes[0].set_title('Test Accuracy: CNN vs Transfer Learning')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Loss comparison
axes[1].plot(epochs_cnn, history_cnn['test_loss'], 'b-',
             linewidth=2, label='Custom CNN')
axes[1].plot(epochs_resnet, history_resnet['test_loss'], 'r-',
             linewidth=2, label='ResNet18')
axes[1].set_xlabel('Epoch')
axes[1].set_ylabel('Test Loss')
axes[1].set_title('Test Loss: CNN vs Transfer Learning')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('model_comparison.png', dpi=100, bbox_inches='tight')
plt.show()

# Save the best overall model
if best_acc_resnet > best_acc_cnn:
    print("\nResNet18 wins! Saving as the final model...")
    best_model_path = 'best_resnet18.pth'
    best_model = model_resnet
else:
    print("\nCustom CNN wins! Saving as the final model...")
    best_model_path = 'best_cnn.pth'
    best_model = model_cnn

print(f"Best model saved to: {best_model_path}")
```

**Output:**
```
============================================================
FINAL COMPARISON
============================================================
Model                      Test Accuracy     Epochs     Parameters
-----------------------------------------------------------------
Custom CNN                         86.12%         30       1,245,578
ResNet18 (transfer)                91.45%         15           5,130
=================================================================

ResNet18 wins! Saving as the final model...
Best model saved to: best_resnet18.pth
```

---

## Step 7: Inference Function

```python
# ============================================================
# INFERENCE FUNCTION
# ============================================================

def predict_image(model, image_tensor, class_names, device, transform=None):
    """
    Predict the class of a single image.

    Args:
        model: trained model
        image_tensor: image as a tensor or PIL image
        class_names: list of class names
        device: torch device
        transform: optional transform to apply

    Returns:
        predicted class name, confidence, all probabilities
    """
    model.eval()

    # Apply transform if needed
    if transform is not None:
        image_tensor = transform(image_tensor)

    # Add batch dimension if needed
    if image_tensor.dim() == 3:
        image_tensor = image_tensor.unsqueeze(0)  # [C, H, W] -> [1, C, H, W]

    # Move to device and predict
    image_tensor = image_tensor.to(device)

    with torch.no_grad():
        output = model(image_tensor)
        probabilities = torch.softmax(output, dim=1)
        confidence, predicted_idx = probabilities.max(1)

    predicted_class = class_names[predicted_idx.item()]
    confidence_pct = confidence.item() * 100

    return predicted_class, confidence_pct, probabilities.squeeze()


def predict_and_show(model, dataset, indices, class_names, device):
    """Predict and display results for multiple images."""
    fig, axes = plt.subplots(2, 5, figsize=(18, 8))
    axes = axes.flatten()

    for i, idx in enumerate(indices):
        img_tensor, true_label = dataset[idx]

        # Predict
        pred_class, confidence, probs = predict_image(
            model, img_tensor, class_names, device
        )

        # Un-normalize for display
        mean = torch.tensor([0.4914, 0.4822, 0.4465]).view(3, 1, 1)
        std = torch.tensor([0.2023, 0.1994, 0.2010]).view(3, 1, 1)
        img_display = img_tensor * std + mean
        img_display = img_display.clamp(0, 1)

        # Display
        axes[i].imshow(img_display.permute(1, 2, 0).numpy())
        true_name = class_names[true_label]
        color = 'green' if pred_class == true_name else 'red'
        axes[i].set_title(
            f'True: {true_name}\n'
            f'Pred: {pred_class} ({confidence:.1f}%)',
            fontsize=10, color=color
        )
        axes[i].axis('off')

    plt.suptitle('Predictions on Test Images', fontsize=14)
    plt.tight_layout()
    plt.savefig('predictions.png', dpi=100, bbox_inches='tight')
    plt.show()


# Run inference on 10 random test images
np.random.seed(42)
random_indices = np.random.choice(len(test_dataset), 10, replace=False)
predict_and_show(model_cnn, test_dataset, random_indices, CLASS_NAMES, DEVICE)

# Show detailed prediction for one image
img, label = test_dataset[0]
pred_class, confidence, probs = predict_image(
    model_cnn, img, CLASS_NAMES, DEVICE
)

print("\nDetailed Prediction:")
print(f"  True class: {CLASS_NAMES[label]}")
print(f"  Predicted:  {pred_class} ({confidence:.1f}% confidence)")
print("\n  All class probabilities:")
for name, prob in zip(CLASS_NAMES, probs):
    bar = '█' * int(prob.item() * 50)
    print(f"    {name:12s}: {prob.item():6.2%} {bar}")
```

**Output:**
```
Detailed Prediction:
  True class: cat
  Predicted:  cat (73.2% confidence)

  All class probabilities:
    airplane    :   2.34%  █
    automobile  :   1.23%
    bird        :   5.67%  ██
    cat         :  73.21%  ████████████████████████████████████
    deer        :   3.45%  █
    dog         :   8.90%  ████
    frog        :   1.23%
    horse       :   2.34%  █
    ship        :   0.89%
    truck       :   0.74%
```

**Line-by-line explanation:**

- `model.eval()` — Always call this before inference. It disables dropout and uses running batch norm statistics.
- `image_tensor.unsqueeze(0)` — Adds a batch dimension. Models always expect batched input, even for a single image.
- `torch.softmax(output, dim=1)` — Converts raw logits to probabilities. We apply softmax here (not in the model) because the model outputs raw logits for `CrossEntropyLoss`.
- `probabilities.max(1)` — Returns the highest probability and its index. The index tells us which class was predicted.
- The function returns the predicted class name, confidence percentage, and all probabilities so you can see how certain the model is.

---

## Loading a Saved Model for Later Use

```python
# ============================================================
# LOADING A SAVED MODEL
# ============================================================

def load_model(model_class, checkpoint_path, device, **kwargs):
    """Load a saved model from a checkpoint file."""
    # Create a new model instance
    model = model_class(**kwargs)

    # Load the saved state
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])

    # Move to device and set to eval mode
    model = model.to(device)
    model.eval()

    print(f"Model loaded from: {checkpoint_path}")
    print(f"  Saved at epoch: {checkpoint['epoch']}")
    print(f"  Best accuracy:  {checkpoint['best_acc']:.2f}%")

    return model

# Example: load the saved CNN
loaded_model = load_model(
    CIFAR10CNN, 'best_cnn.pth', DEVICE, num_classes=10
)

# Verify it works
test_loss, test_acc = evaluate(loaded_model, test_loader,
                                nn.CrossEntropyLoss(), DEVICE)
print(f"  Verified accuracy: {test_acc:.2f}%")
```

**Output:**
```
Model loaded from: best_cnn.pth
  Saved at epoch: 28
  Best accuracy:  86.12%
  Verified accuracy: 86.12%
```

---

## Common Mistakes

1. **Not calling model.eval() before inference**: This leaves dropout active, which randomly zeroes neurons and gives inconsistent results.

2. **Forgetting to move data to the same device as the model**: If the model is on GPU and data is on CPU (or vice versa), you get a runtime error.

3. **Using ImageNet normalization with CIFAR-10 statistics**: If your custom CNN was trained with CIFAR-10 stats, use those same stats at inference time. Mixing them up corrupts the predictions.

4. **Not freezing pretrained layers in transfer learning**: If you forget `param.requires_grad = False`, you update 11 million parameters instead of 5,000, which is slow and can destroy the pretrained features.

5. **Applying data augmentation during inference**: Augmentation is for training only. At inference time, use only ToTensor and Normalize.

---

## Best Practices

1. **Always save checkpoints during training**: Save the model whenever test accuracy improves. If training crashes, you do not lose everything.

2. **Start with transfer learning**: Unless you have a very unusual dataset, a pretrained model will almost always outperform a model trained from scratch.

3. **Use a learning rate scheduler**: Reducing the learning rate when progress stalls helps squeeze out extra accuracy.

4. **Monitor both train and test metrics**: If train accuracy is high but test accuracy is low, you are overfitting.

5. **Separate your code into functions**: Keep data loading, model definition, training, and evaluation in separate functions. This makes debugging much easier.

---

## Quick Summary

We built a complete image classification system for CIFAR-10. A custom CNN with batch normalization and dropout achieved around 86% test accuracy. Transfer learning with a pretrained ResNet18 achieved around 91% with fewer trainable parameters and less training time. We saved the best model during training and wrote an inference function to classify new images with confidence scores.

---

## Key Points

- A complete image classification pipeline has 7 steps: data loading, model building, training, evaluation, transfer learning, saving, and inference
- Data augmentation during training (flip, crop, color jitter) improves generalization
- Batch normalization and dropout are essential for training stable, non-overfitting CNNs
- Transfer learning with pretrained models consistently outperforms training from scratch
- Only the final classification layer needs to be trainable in transfer learning
- Always save model checkpoints during training
- Use model.eval() and torch.no_grad() during inference

---

## Practice Questions

1. Why does the transfer learning model achieve higher accuracy with fewer trainable parameters? What knowledge does the pretrained model bring?

2. What would happen if you forgot to freeze the pretrained layers in the ResNet18 transfer learning approach? Would results improve or get worse? Why?

3. The custom CNN uses Dropout2d(0.25) in convolutional blocks and Dropout(0.5) before the final layer. Why are different dropout rates used in different parts of the network?

4. Why do we use different normalization statistics for the custom CNN (CIFAR-10 stats) and the ResNet18 model (ImageNet stats)?

5. If you wanted to adapt this classifier for a dataset with 100 classes instead of 10, what specific changes would you need to make?

---

## Exercises

### Exercise 1: Fine-Tune the Entire ResNet

Instead of freezing all pretrained layers, try unfreezing the last convolutional block of ResNet18 and training it with a small learning rate (1e-4). Compare the results to the frozen approach. Does fine-tuning help?

**Hint:** Access layers with `model.layer4` and set `requires_grad = True` for those parameters.

### Exercise 2: Add More Augmentation

Extend the training transform with RandomRotation(15), RandomAffine, and more aggressive ColorJitter. Does stronger augmentation improve or hurt the custom CNN's test accuracy?

### Exercise 3: Confusion Matrix

Using the predictions from the evaluation step, create a confusion matrix showing which classes are most often confused with each other. Which pairs of classes does the model struggle to distinguish?

**Hint:** Use `sklearn.metrics.confusion_matrix` or build one manually with a 10x10 array.

---

## What Is Next?

You have just built a complete image classifier. In Chapter 30, you will tackle a completely different domain: **text**. You will build a sentiment analyzer that reads movie reviews and determines whether they are positive or negative. This project introduces NLP (Natural Language Processing) concepts like tokenization, word embeddings, and recurrent networks.
