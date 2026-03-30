# Chapter 18: Image Classification with CNNs

## What You Will Learn

In this chapter, you will learn:

- How to build a complete image classification pipeline from scratch
- How to organize datasets using `ImageFolder`
- How to create efficient data loaders for training and validation
- How to design and build a Convolutional Neural Network (CNN)
- How to write a training loop for image classification
- How to evaluate model performance with accuracy, confusion matrix, and per-class metrics
- How to visualize predictions to understand what your model gets right and wrong

## Why This Chapter Matters

Image classification is the "Hello World" of computer vision. It answers a simple question: what is in this image? Is it a cat or a dog? A tumor or healthy tissue? A stop sign or a speed limit sign?

This one skill powers real applications everywhere. Doctors use it to screen X-rays. Factories use it to spot defective products on assembly lines. Farmers use it to identify crop diseases from photos. Social media platforms use it to detect inappropriate content.

More importantly, the classification pipeline you build in this chapter is the foundation for everything else in computer vision. Object detection, image segmentation, and even image generation all build on the same concepts: load data, define a model, train, evaluate, improve. Master this chapter, and you have a template for every computer vision project that follows.

---

## 18.1 The Classification Pipeline Overview

Before diving into code, let us see the entire pipeline at a high level:

```
Image Classification Pipeline:

1. ORGANIZE DATA
   images/
     train/
       cats/  -> cat1.jpg, cat2.jpg, ...
       dogs/  -> dog1.jpg, dog2.jpg, ...
     val/
       cats/  -> cat101.jpg, cat102.jpg, ...
       dogs/  -> dog101.jpg, dog102.jpg, ...

2. LOAD & PREPROCESS
   ImageFolder + DataLoader
   -> Batches of (images, labels)
   -> Each image: (3, 224, 224) tensor

3. BUILD MODEL
   CNN: Conv layers -> Pool -> FC layers -> Output
   Input: (batch, 3, 224, 224)
   Output: (batch, num_classes)

4. TRAIN
   For each epoch:
     Forward pass -> Loss -> Backward pass -> Update weights

5. EVALUATE
   Accuracy, confusion matrix, per-class metrics

6. VISUALIZE
   Show predictions with confidence scores
```

---

## 18.2 Organizing Your Dataset with ImageFolder

PyTorch's `ImageFolder` is a dataset class that automatically loads images from a directory structure where each subfolder represents a class.

### Required Directory Structure

```
dataset/
    train/
        class_a/
            img001.jpg
            img002.jpg
            ...
        class_b/
            img001.jpg
            img002.jpg
            ...
    val/
        class_a/
            img001.jpg
            img002.jpg
            ...
        class_b/
            img001.jpg
            img002.jpg
            ...
```

**The folder name IS the label.** If you have a folder called "cats," all images inside it are automatically labeled as "cats."

### Creating a Sample Dataset

For this chapter, we will create a simple synthetic dataset to demonstrate the pipeline. In real projects, you would use actual images:

```python
import os
import torch
import numpy as np
from PIL import Image

def create_sample_dataset(base_dir, num_train=100, num_val=20):
    """Create a simple synthetic dataset for demonstration."""
    classes = ["cats", "dogs", "birds"]
    splits = {
        "train": num_train,
        "val": num_val
    }

    for split, count in splits.items():
        for cls in classes:
            dir_path = os.path.join(base_dir, split, cls)
            os.makedirs(dir_path, exist_ok=True)

            for i in range(count):
                # Create a simple colored image for each class
                # In real projects, you would have actual photos
                img = np.random.randint(0, 256, (64, 64, 3),
                                        dtype=np.uint8)
                # Give each class a slight color bias so the model
                # has something to learn
                if cls == "cats":
                    img[:, :, 0] = np.clip(img[:, :, 0] + 50, 0, 255)
                elif cls == "dogs":
                    img[:, :, 1] = np.clip(img[:, :, 1] + 50, 0, 255)
                else:  # birds
                    img[:, :, 2] = np.clip(img[:, :, 2] + 50, 0, 255)

                pil_img = Image.fromarray(img)
                pil_img.save(os.path.join(dir_path, f"{i:04d}.jpg"))

    print(f"Created dataset in {base_dir}")
    for split in splits:
        for cls in classes:
            path = os.path.join(base_dir, split, cls)
            count = len(os.listdir(path))
            print(f"  {split}/{cls}: {count} images")

# Create the dataset
create_sample_dataset("sample_dataset")
# Output:
# Created dataset in sample_dataset
#   train/cats: 100 images
#   train/dogs: 100 images
#   train/birds: 100 images
#   val/cats: 20 images
#   val/dogs: 20 images
#   val/birds: 20 images
```

### Loading with ImageFolder

```python
from torchvision import datasets, transforms

# Define transforms
train_transforms = transforms.Compose([
    transforms.Resize((64, 64)),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])

val_transforms = transforms.Compose([
    transforms.Resize((64, 64)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])

# Load datasets using ImageFolder
train_dataset = datasets.ImageFolder(
    root="sample_dataset/train",
    transform=train_transforms
)

val_dataset = datasets.ImageFolder(
    root="sample_dataset/val",
    transform=val_transforms
)

# Inspect the dataset
print(f"Number of training images: {len(train_dataset)}")
print(f"Number of validation images: {len(val_dataset)}")
print(f"Classes: {train_dataset.classes}")
print(f"Class to index: {train_dataset.class_to_idx}")

# Output:
# Number of training images: 300
# Number of validation images: 60
# Classes: ['birds', 'cats', 'dogs']
# Class to index: {'birds': 0, 'cats': 1, 'dogs': 2}
```

**Line-by-line explanation:**

- `datasets.ImageFolder(root=..., transform=...)`: Scans the directory, finds all images, and assigns labels based on subfolder names. The `transform` is applied to each image when loaded.
- `train_dataset.classes`: A list of class names, sorted alphabetically.
- `train_dataset.class_to_idx`: Maps class names to integer indices. These integers are the labels your model will predict.

### Inspecting a Single Sample

```python
# Get one sample
image, label = train_dataset[0]

print(f"Image type: {type(image)}")
print(f"Image shape: {image.shape}")
print(f"Label: {label}")
print(f"Label name: {train_dataset.classes[label]}")

# Output:
# Image type: <class 'torch.Tensor'>
# Image shape: torch.Size([3, 64, 64])
# Label: 0
# Label name: birds
```

---

## 18.3 Creating Data Loaders

A **DataLoader** wraps a dataset and provides batching, shuffling, and parallel loading:

```python
from torch.utils.data import DataLoader

# Create data loaders
train_loader = DataLoader(
    train_dataset,
    batch_size=32,
    shuffle=True,        # Shuffle training data each epoch
    num_workers=2,       # Parallel data loading
    pin_memory=True,     # Faster GPU transfer
)

val_loader = DataLoader(
    val_dataset,
    batch_size=32,
    shuffle=False,       # Do NOT shuffle validation data
    num_workers=2,
    pin_memory=True,
)

# Check batch shapes
for images, labels in train_loader:
    print(f"Batch images shape: {images.shape}")
    print(f"Batch labels shape: {labels.shape}")
    print(f"Batch labels: {labels[:10]}")
    break

# Output:
# Batch images shape: torch.Size([32, 3, 64, 64])
# Batch labels shape: torch.Size([32])
# Batch labels: tensor([2, 0, 1, 2, 0, 1, 1, 0, 2, 0])
```

```
DataLoader produces batches:

Single image: (3, 64, 64)   +  label: 1

DataLoader with batch_size=32:

Batch of images: (32, 3, 64, 64)  +  Batch of labels: (32,)
  ^                                     ^
  |                                     |
  32 images stacked                     32 integer labels
  along a new first dimension           one per image
```

**Line-by-line explanation:**

- `batch_size=32`: Groups 32 images into one tensor. This is the number of images processed simultaneously.
- `shuffle=True`: Randomizes the order of images each epoch. This prevents the model from memorizing the order of training data. Never shuffle validation data -- you want consistent evaluation.
- `pin_memory=True`: Allocates the batch tensors in page-locked (pinned) memory, which speeds up the transfer from CPU to GPU.

---

## 18.4 Building a CNN

Now let us build the actual model. A **Convolutional Neural Network (CNN)** is specifically designed to process images. It uses **convolutional layers** that slide small filters across the image to detect features like edges, textures, and shapes.

### CNN Architecture Diagram

```
Input Image (3, 64, 64)
        |
  +-----v------+
  | Conv2d      |  32 filters, 3x3, detects edges
  | ReLU        |
  | MaxPool 2x2 |  Reduces size by half
  +-----+------+
        |  (32, 32, 32)
  +-----v------+
  | Conv2d      |  64 filters, 3x3, detects textures
  | ReLU        |
  | MaxPool 2x2 |  Reduces size by half
  +-----+------+
        |  (64, 16, 16)
  +-----v------+
  | Conv2d      |  128 filters, 3x3, detects patterns
  | ReLU        |
  | MaxPool 2x2 |  Reduces size by half
  +-----+------+
        |  (128, 8, 8)
  +-----v------+
  | Flatten     |  Reshape to 1D: 128*8*8 = 8192
  +-----+------+
        |  (8192,)
  +-----v------+
  | Linear(512) |  Fully connected
  | ReLU        |
  | Dropout(0.5)|  Prevent overfitting
  +-----+------+
        |  (512,)
  +-----v------+
  | Linear(3)   |  Output: one score per class
  +-----+------+
        |  (3,)
        v
  Class Scores (cats, dogs, birds)
```

### The Model Code

```python
import torch
import torch.nn as nn

class SimpleCNN(nn.Module):
    def __init__(self, num_classes=3):
        super(SimpleCNN, self).__init__()

        # Convolutional layers (feature extraction)
        self.features = nn.Sequential(
            # Block 1: Input (3, 64, 64) -> Output (32, 32, 32)
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),

            # Block 2: Input (32, 32, 32) -> Output (64, 16, 16)
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),

            # Block 3: Input (64, 16, 16) -> Output (128, 8, 8)
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
        )

        # Classification layers (decision making)
        self.classifier = nn.Sequential(
            nn.Flatten(),                    # (128, 8, 8) -> (8192,)
            nn.Linear(128 * 8 * 8, 512),     # 8192 -> 512
            nn.ReLU(),
            nn.Dropout(0.5),                 # Drop 50% during training
            nn.Linear(512, num_classes),      # 512 -> num_classes
        )

    def forward(self, x):
        x = self.features(x)      # Extract visual features
        x = self.classifier(x)    # Classify based on features
        return x

# Create the model
model = SimpleCNN(num_classes=3)

# Test with a dummy batch
dummy_input = torch.randn(4, 3, 64, 64)  # 4 images
output = model(dummy_input)
print(f"Input shape: {dummy_input.shape}")
print(f"Output shape: {output.shape}")
print(f"Output (class scores):\n{output}")

# Output:
# Input shape: torch.Size([4, 3, 64, 64])
# Output shape: torch.Size([4, 3])
# Output (class scores):
# tensor([[ 0.0234, -0.0156,  0.0089],
#         [ 0.0178, -0.0201,  0.0145],
#         [ 0.0312, -0.0098,  0.0067],
#         [ 0.0256, -0.0189,  0.0134]], grad_fn=<AddmmBackward0>)
```

**Line-by-line explanation:**

- `nn.Conv2d(3, 32, kernel_size=3, padding=1)`: A convolutional layer. Takes 3 input channels (RGB), produces 32 output channels (feature maps). Uses a 3x3 filter. `padding=1` adds zeros around the border so the output height and width stay the same.
- `nn.ReLU()`: Activation function. Replaces negative values with zero. Adds non-linearity so the model can learn complex patterns.
- `nn.MaxPool2d(2, 2)`: Takes the maximum value in each 2x2 region, reducing the size by half. This makes the model focus on the strongest features and reduces computation.
- `nn.Flatten()`: Reshapes the 3D feature maps into a 1D vector so it can be fed to fully connected layers.
- `nn.Linear(128 * 8 * 8, 512)`: A fully connected layer. Connects every input neuron to every output neuron. The input size (8192) comes from 128 channels times 8 height times 8 width.
- `nn.Dropout(0.5)`: During training, randomly sets 50% of neurons to zero. This forces the network to learn redundant representations and prevents overfitting.

### How Convolution Works (Simplified)

```
A 3x3 convolutional filter slides across the image:

Image patch:          Filter:            Result:
+---+---+---+        +---+---+---+
| 1 | 2 | 3 |        | 1 | 0 |-1 |      1*1 + 2*0 + 3*(-1)
+---+---+---+   *    +---+---+---+   =   + 4*1 + 5*0 + 6*(-1)
| 4 | 5 | 6 |        | 1 | 0 |-1 |      + 7*1 + 8*0 + 9*(-1)
+---+---+---+        +---+---+---+      = 1-3+4-6+7-9 = -6
| 7 | 8 | 9 |        | 1 | 0 |-1 |
+---+---+---+        +---+---+---+

The filter slides to every position, producing a
new "feature map" that highlights certain patterns.

This particular filter detects vertical edges
(differences between left and right).
```

### Counting Model Parameters

```python
def count_parameters(model):
    """Count total and trainable parameters."""
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters()
                    if p.requires_grad)
    print(f"Total parameters: {total:,}")
    print(f"Trainable parameters: {trainable:,}")
    return total

count_parameters(model)
# Output:
# Total parameters: 4,244,675
# Trainable parameters: 4,244,675
```

---

## 18.5 The Training Loop

The training loop is where the model actually learns. It repeats the same cycle: make predictions, calculate the error, update weights.

```
Training Loop (one epoch):

For each batch:
  1. Forward Pass:   predictions = model(images)
  2. Calculate Loss: loss = criterion(predictions, labels)
  3. Backward Pass:  loss.backward()  (compute gradients)
  4. Update Weights: optimizer.step() (adjust parameters)
  5. Reset:          optimizer.zero_grad()
```

### Complete Training Code

```python
import torch
import torch.nn as nn
import torch.optim as optim
import time

def train_model(model, train_loader, val_loader, num_epochs=10,
                learning_rate=0.001):
    """Train the model and track metrics."""

    # Setup
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    print(f"Training on: {device}")

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # Track history
    history = {
        "train_loss": [], "train_acc": [],
        "val_loss": [], "val_acc": []
    }

    for epoch in range(num_epochs):
        start_time = time.time()

        # === Training Phase ===
        model.train()   # Enable dropout, batch norm training mode
        running_loss = 0.0
        correct = 0
        total = 0

        for images, labels in train_loader:
            images = images.to(device)
            labels = labels.to(device)

            # Forward pass
            outputs = model(images)
            loss = criterion(outputs, labels)

            # Backward pass and optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            # Track metrics
            running_loss += loss.item() * images.size(0)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        train_loss = running_loss / total
        train_acc = correct / total

        # === Validation Phase ===
        model.eval()    # Disable dropout, batch norm eval mode
        running_loss = 0.0
        correct = 0
        total = 0

        with torch.no_grad():  # No gradient computation needed
            for images, labels in val_loader:
                images = images.to(device)
                labels = labels.to(device)

                outputs = model(images)
                loss = criterion(outputs, labels)

                running_loss += loss.item() * images.size(0)
                _, predicted = torch.max(outputs, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

        val_loss = running_loss / total
        val_acc = correct / total

        # Save history
        history["train_loss"].append(train_loss)
        history["train_acc"].append(train_acc)
        history["val_loss"].append(val_loss)
        history["val_acc"].append(val_acc)

        elapsed = time.time() - start_time
        print(f"Epoch [{epoch+1}/{num_epochs}] "
              f"Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | "
              f"Val Loss: {val_loss:.4f} Acc: {val_acc:.4f} | "
              f"Time: {elapsed:.1f}s")

    return history

# Train the model
model = SimpleCNN(num_classes=3)
history = train_model(model, train_loader, val_loader,
                      num_epochs=10, learning_rate=0.001)

# Output:
# Training on: cpu
# Epoch [1/10] Train Loss: 1.0892 Acc: 0.3867 | Val Loss: 1.0654 Acc: 0.4333 | Time: 0.8s
# Epoch [2/10] Train Loss: 1.0234 Acc: 0.5200 | Val Loss: 0.9876 Acc: 0.5667 | Time: 0.7s
# ...
# Epoch [10/10] Train Loss: 0.4521 Acc: 0.8533 | Val Loss: 0.5123 Acc: 0.8000 | Time: 0.7s
```

**Line-by-line explanation:**

- `model.train()`: Puts the model in training mode. This enables dropout and makes batch normalization use batch statistics.
- `model.eval()`: Puts the model in evaluation mode. Dropout is disabled, and batch normalization uses running statistics.
- `criterion = nn.CrossEntropyLoss()`: The loss function for classification. It compares predicted class scores to actual labels and returns a single number indicating how wrong the predictions are.
- `optimizer = optim.Adam(model.parameters(), lr=0.001)`: The Adam optimizer adjusts model weights to minimize the loss. Learning rate 0.001 is a good default.
- `optimizer.zero_grad()`: Clears old gradients. Without this, gradients accumulate across batches.
- `loss.backward()`: Calculates gradients -- how much each weight contributed to the error.
- `optimizer.step()`: Updates weights using the gradients.
- `torch.no_grad()`: Disables gradient tracking during validation. This saves memory and speeds up computation.
- `_, predicted = torch.max(outputs, 1)`: Gets the index of the highest score in each row. The `_` discards the actual values; we only need the indices (which are the predicted classes).
- `loss.item() * images.size(0)`: Converts the average loss (per sample in the batch) to total loss for the batch, so we can compute the correct average over the entire dataset.

### Plotting Training History

```python
import matplotlib.pyplot as plt

def plot_history(history):
    """Plot training and validation loss and accuracy."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Loss plot
    ax1.plot(history["train_loss"], label="Train Loss", marker="o")
    ax1.plot(history["val_loss"], label="Val Loss", marker="s")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Loss")
    ax1.set_title("Training and Validation Loss")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Accuracy plot
    ax2.plot(history["train_acc"], label="Train Accuracy", marker="o")
    ax2.plot(history["val_acc"], label="Val Accuracy", marker="s")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Accuracy")
    ax2.set_title("Training and Validation Accuracy")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

plot_history(history)
```

**Output:** Two side-by-side plots. The left shows loss decreasing over epochs (both train and validation). The right shows accuracy increasing. If the gap between training and validation widens, the model is overfitting.

```
Reading the Training Curves:

Good training:              Overfitting:
Loss                        Loss
  |\\                         |\\
  | \\___train               | \\___train (keeps going down)
  |  \\__val                 |  \\__val (stops, then goes UP)
  +---------> Epoch          +---------> Epoch

  Train and val curves        Val curve diverges from train
  should decrease together.   = model is memorizing, not learning.
```

---

## 18.6 Evaluation

### Overall Accuracy

```python
def evaluate(model, data_loader, device=None):
    """Calculate overall accuracy on a dataset."""
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available()
                              else "cpu")

    model = model.to(device)
    model.eval()

    correct = 0
    total = 0
    all_predictions = []
    all_labels = []

    with torch.no_grad():
        for images, labels in data_loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            _, predicted = torch.max(outputs, 1)

            total += labels.size(0)
            correct += (predicted == labels).sum().item()

            all_predictions.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    accuracy = correct / total
    print(f"Overall Accuracy: {accuracy:.4f} ({correct}/{total})")

    return all_predictions, all_labels

predictions, labels = evaluate(model, val_loader)
# Output: Overall Accuracy: 0.8000 (48/60)
```

### Confusion Matrix

A **confusion matrix** shows exactly which classes the model confuses with each other:

```python
import numpy as np
import matplotlib.pyplot as plt

def plot_confusion_matrix(predictions, labels, class_names):
    """Plot a confusion matrix."""
    num_classes = len(class_names)
    matrix = np.zeros((num_classes, num_classes), dtype=int)

    for true, pred in zip(labels, predictions):
        matrix[true][pred] += 1

    # Plot
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(matrix, cmap="Blues")

    # Add text annotations
    for i in range(num_classes):
        for j in range(num_classes):
            color = "white" if matrix[i, j] > matrix.max() / 2 else "black"
            ax.text(j, i, str(matrix[i, j]),
                    ha="center", va="center", color=color, fontsize=14)

    # Labels
    ax.set_xticks(range(num_classes))
    ax.set_yticks(range(num_classes))
    ax.set_xticklabels(class_names)
    ax.set_yticklabels(class_names)
    ax.set_xlabel("Predicted Label")
    ax.set_ylabel("True Label")
    ax.set_title("Confusion Matrix")
    plt.colorbar(im)
    plt.tight_layout()
    plt.show()

    return matrix

class_names = ["birds", "cats", "dogs"]
matrix = plot_confusion_matrix(predictions, labels, class_names)

# Output: A heatmap showing prediction counts
```

```
Reading a Confusion Matrix:

              Predicted
              birds  cats  dogs
         +-----------------------+
birds    |   18  |   1   |   1  |  <- 18 correct, 2 wrong
True     +-----------------------+
cats     |    2  |   16  |   2  |  <- 16 correct, 4 wrong
         +-----------------------+
dogs     |    1  |   3   |   16 |  <- 16 correct, 4 wrong
         +-----------------------+

Diagonal = correct predictions (higher is better)
Off-diagonal = mistakes (lower is better)

Row 2, Column 3: The model predicted "dogs" 2 times
when the true label was "cats."
```

### Per-Class Accuracy

```python
def per_class_accuracy(predictions, labels, class_names):
    """Calculate accuracy for each class."""
    predictions = np.array(predictions)
    labels = np.array(labels)

    print("Per-Class Accuracy:")
    print("-" * 40)

    for i, name in enumerate(class_names):
        class_mask = labels == i
        class_correct = (predictions[class_mask] == i).sum()
        class_total = class_mask.sum()
        acc = class_correct / class_total if class_total > 0 else 0

        print(f"  {name:10s}: {acc:.4f} ({class_correct}/{class_total})")

    print("-" * 40)

per_class_accuracy(predictions, labels, class_names)
# Output:
# Per-Class Accuracy:
# ----------------------------------------
#   birds     : 0.9000 (18/20)
#   cats      : 0.8000 (16/20)
#   dogs      : 0.8000 (16/20)
# ----------------------------------------
```

### Precision, Recall, and F1 Score

```python
def classification_report(predictions, labels, class_names):
    """Calculate precision, recall, and F1 for each class."""
    predictions = np.array(predictions)
    labels = np.array(labels)

    print(f"{'Class':12s} {'Precision':>10s} {'Recall':>10s} {'F1':>10s} {'Support':>10s}")
    print("-" * 55)

    for i, name in enumerate(class_names):
        # True Positives: predicted i and was actually i
        tp = ((predictions == i) & (labels == i)).sum()
        # False Positives: predicted i but was not actually i
        fp = ((predictions == i) & (labels != i)).sum()
        # False Negatives: did not predict i but was actually i
        fn = ((predictions != i) & (labels == i)).sum()

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = (2 * precision * recall / (precision + recall)
              if (precision + recall) > 0 else 0)
        support = (labels == i).sum()

        print(f"{name:12s} {precision:10.4f} {recall:10.4f} "
              f"{f1:10.4f} {support:10d}")

    print("-" * 55)

classification_report(predictions, labels, class_names)
# Output:
# Class         Precision     Recall         F1    Support
# -------------------------------------------------------
# birds            0.8571     0.9000     0.8780         20
# cats             0.8000     0.8000     0.8000         20
# dogs             0.8421     0.8000     0.8205         20
# -------------------------------------------------------
```

```
Precision vs Recall:

Precision = "Of everything I PREDICTED as cats,
             how many were actually cats?"
           = TP / (TP + FP)

Recall    = "Of everything that WAS a cat,
             how many did I correctly identify?"
           = TP / (TP + FN)

F1 Score  = Harmonic mean of precision and recall
           = A single number balancing both

High precision, low recall: Model is careful but misses many
Low precision, high recall: Model catches most but has false alarms
```

---

## 18.7 Visualizing Predictions

Seeing what the model predicts on actual images helps you understand its behavior:

```python
import torch
import matplotlib.pyplot as plt
import numpy as np

def visualize_predictions(model, dataset, class_names, num_images=12,
                          device=None):
    """Display images with their predictions."""
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available()
                              else "cpu")

    model = model.to(device)
    model.eval()

    # ImageNet denormalization
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])

    fig, axes = plt.subplots(3, 4, figsize=(16, 12))
    axes = axes.flatten()

    # Pick random samples
    indices = np.random.choice(len(dataset), num_images, replace=False)

    for i, idx in enumerate(indices):
        image, true_label = dataset[idx]

        # Get prediction
        with torch.no_grad():
            output = model(image.unsqueeze(0).to(device))
            probabilities = torch.softmax(output, dim=1)
            confidence, predicted = torch.max(probabilities, 1)

        predicted = predicted.item()
        confidence = confidence.item()
        true_name = class_names[true_label]
        pred_name = class_names[predicted]

        # Denormalize for display
        img_display = image.permute(1, 2, 0).numpy()
        img_display = img_display * std + mean
        img_display = np.clip(img_display, 0, 1)

        # Plot
        axes[i].imshow(img_display)
        color = "green" if predicted == true_label else "red"
        axes[i].set_title(
            f"True: {true_name}\nPred: {pred_name} ({confidence:.1%})",
            color=color, fontsize=10
        )
        axes[i].axis("off")

    plt.suptitle("Model Predictions (Green=Correct, Red=Wrong)",
                 fontsize=14)
    plt.tight_layout()
    plt.show()

visualize_predictions(model, val_dataset, class_names)
```

**Output:** A 3x4 grid of images. Each image shows the true label and predicted label with confidence percentage. Correct predictions have green titles; incorrect predictions have red titles.

**Line-by-line explanation:**

- `image.unsqueeze(0)`: Adds a batch dimension. The model expects (batch, C, H, W), but a single image is (C, H, W). `unsqueeze(0)` adds a dimension at position 0, making it (1, C, H, W).
- `torch.softmax(output, dim=1)`: Converts raw scores to probabilities that sum to 1. This lets us express confidence as a percentage.
- `torch.max(probabilities, 1)`: Returns the highest probability and its index (the predicted class).
- The denormalization reverses the ImageNet normalization so the image displays with correct colors.

---

## 18.8 Saving and Loading the Model

```python
import torch

# Save the entire model state
torch.save({
    "model_state_dict": model.state_dict(),
    "class_names": class_names,
    "num_classes": len(class_names),
    "history": history,
}, "cnn_classifier.pth")

print("Model saved!")

# Load the model later
checkpoint = torch.load("cnn_classifier.pth")

loaded_model = SimpleCNN(num_classes=checkpoint["num_classes"])
loaded_model.load_state_dict(checkpoint["model_state_dict"])
loaded_model.eval()

print(f"Loaded model for classes: {checkpoint['class_names']}")
# Output: Loaded model for classes: ['birds', 'cats', 'dogs']
```

**Line-by-line explanation:**

- `model.state_dict()`: Returns all learnable parameters (weights and biases) as a dictionary.
- We save extra information (class names, history) alongside the model so we have everything needed to use it later.
- `loaded_model.load_state_dict(...)`: Loads the saved parameters into a fresh model instance.
- `loaded_model.eval()`: Puts the model in evaluation mode (no dropout, etc.).

---

## Common Mistakes

1. **Forgetting `model.train()` and `model.eval()`.** Dropout and batch normalization behave differently during training and evaluation. Without switching modes, validation metrics will be noisy and inconsistent.

2. **Not using `torch.no_grad()` during validation.** Without it, PyTorch still builds the computation graph and tracks gradients, wasting memory and slowing down evaluation.

3. **Shuffling the validation set.** This does not cause errors, but it can make debugging harder and wastes time. Only shuffle training data.

4. **Wrong input size for the linear layer.** If you change the image size or the number of convolutional layers, the flattened size changes. Always calculate `channels * height * width` after all conv and pool layers.

5. **Forgetting `optimizer.zero_grad()`.** Without zeroing gradients, they accumulate across batches, causing the model to learn from stale information.

6. **Using `accuracy` alone for imbalanced datasets.** If 95% of your images are cats, a model that always says "cat" gets 95% accuracy but is useless. Use precision, recall, and the confusion matrix.

---

## Best Practices

1. **Start simple.** Begin with a small CNN and a small subset of data. Make sure the pipeline works end-to-end before scaling up.

2. **Monitor both training and validation metrics.** A widening gap between them signals overfitting. Add dropout, data augmentation, or more data.

3. **Save checkpoints regularly.** Save the model after each epoch (or at least the best one). Training can crash, and you do not want to lose hours of work.

4. **Visualize predictions.** Looking at what the model gets wrong often reveals problems (wrong labels, bad preprocessing, confusing classes).

5. **Use a learning rate scheduler.** Reducing the learning rate as training progresses often improves final accuracy.

---

## Quick Summary

Image classification with CNNs follows a standard pipeline: organize data into class folders, load with `ImageFolder` and `DataLoader`, build a CNN model, train with a forward-backward loop, and evaluate with accuracy, confusion matrix, and per-class metrics. CNNs use convolutional layers to detect visual features and pooling layers to reduce spatial dimensions. The training loop consists of forward pass, loss calculation, backward pass, and weight update. Always switch between `model.train()` and `model.eval()` modes. Visualize predictions to understand model behavior.

---

## Key Points

- `ImageFolder` automatically assigns labels based on subfolder names. The folder name IS the label.
- A CNN consists of feature extraction layers (conv + pool) followed by classification layers (fully connected).
- `Conv2d` slides filters across images to detect features. `MaxPool2d` reduces spatial dimensions by taking the maximum in each region.
- `model.train()` enables dropout and batch norm training. `model.eval()` disables them for evaluation.
- Always use `torch.no_grad()` during validation to save memory and computation.
- The confusion matrix shows exactly which classes the model confuses with each other.
- Per-class accuracy, precision, and recall reveal performance differences across classes that overall accuracy hides.

---

## Practice Questions

1. Why do we use separate transforms for training and validation? What could go wrong if we used training transforms (with random augmentation) during validation?

2. An image has shape `(3, 64, 64)` and goes through a `Conv2d(3, 32, kernel_size=3, padding=1)` followed by `MaxPool2d(2, 2)`. What is the output shape? Explain each dimension.

3. What does `Dropout(0.5)` do during training? What does it do during evaluation? Why is this difference important?

4. You have a dataset with 1000 dog images and 50 cat images. Your model achieves 95% accuracy. Is this good? What metrics should you look at instead?

5. Why do we call `optimizer.zero_grad()` before `loss.backward()`? What happens if we forget?

---

## Exercises

### Exercise 1: Build and Train a CNN

Using the pipeline from this chapter:
1. Create a synthetic dataset with 4 classes (or use a real dataset like CIFAR-10)
2. Build a CNN with at least 3 convolutional blocks
3. Train for 20 epochs
4. Plot the training history
5. Print the confusion matrix and per-class accuracy

### Exercise 2: Experiment with Architecture

Modify the `SimpleCNN` model:
1. Add a 4th convolutional block with 256 filters
2. Add batch normalization (`nn.BatchNorm2d`) after each conv layer
3. Try different dropout rates (0.25 vs 0.5 vs 0.75)
4. Compare the training curves and final accuracy for each variant

### Exercise 3: Learning Rate Experiment

Train the same model three times with different learning rates:
1. `lr = 0.01` (too high?)
2. `lr = 0.001` (standard)
3. `lr = 0.0001` (too low?)

Plot all three training curves on the same graph. Which learning rate gives the best result, and why?

---

## What Is Next?

Training a CNN from scratch works, but it requires a lot of data and time. In the next chapter, you will learn about **Transfer Learning** -- how to take a model that someone else already trained on millions of images (like ImageNet) and adapt it to your specific task. This dramatically reduces the amount of data and training time you need, often producing much better results than training from scratch.
