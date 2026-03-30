# Chapter 27: Project — Image Classification App

## What You Will Learn

- How to organize a custom image dataset using ImageFolder
- How to build and train a CNN (Convolutional Neural Network) for image classification
- How to use transfer learning with ResNet18 for much better accuracy
- How to build a Gradio web interface for uploading and classifying images
- How to put all pieces together into a complete, deployable application

## Why This Chapter Matters

Everything you have learned about computer vision comes together in this chapter. You will build a real, working application from start to finish — from organizing your dataset, to training a model, to creating a web interface where anyone can upload an image and get a prediction. This is the kind of project you can put on your resume or show to an employer.

Building an end-to-end project teaches you skills that individual chapters cannot: how to connect the pieces, how to handle real-world data, and how to make your model usable by non-technical people. By the end of this chapter, you will have a complete image classification app running in your browser.

---

## 27.1 Project Overview

We will build an image classification app that can identify different types of animals. The complete project has four parts:

```
+------------------------------------------------------------------+
|              Project Architecture                                 |
+------------------------------------------------------------------+
|                                                                   |
|  PART 1: Data Preparation                                         |
|  +-----------------------------+                                  |
|  | Organize images into folders |                                 |
|  | using ImageFolder format     |                                 |
|  +-----------------------------+                                  |
|                |                                                   |
|                v                                                   |
|  PART 2: Model Training (CNN from scratch)                       |
|  +-----------------------------+                                  |
|  | Build a simple CNN           |                                 |
|  | Train on our dataset         |                                 |
|  | Evaluate accuracy            |                                 |
|  +-----------------------------+                                  |
|                |                                                   |
|                v                                                   |
|  PART 3: Transfer Learning (ResNet18)                            |
|  +-----------------------------+                                  |
|  | Load pre-trained ResNet18    |                                 |
|  | Fine-tune on our dataset     |                                 |
|  | Achieve higher accuracy      |                                 |
|  +-----------------------------+                                  |
|                |                                                   |
|                v                                                   |
|  PART 4: Gradio Web App                                          |
|  +-----------------------------+                                  |
|  | Build a web interface        |                                 |
|  | Upload images                |                                 |
|  | Display predictions          |                                 |
|  +-----------------------------+                                  |
|                                                                   |
+------------------------------------------------------------------+
```

---

## 27.2 Part 1 — Preparing the Dataset with ImageFolder

PyTorch's `ImageFolder` class makes it easy to load image datasets. You just need to organize your images into folders where each folder name is the class label.

### Dataset Folder Structure

```
+------------------------------------------------------------------+
|              ImageFolder Directory Structure                      |
+------------------------------------------------------------------+
|                                                                   |
|  dataset/                                                         |
|  ├── train/                                                       |
|  │   ├── cats/                                                    |
|  │   │   ├── cat_001.jpg                                         |
|  │   │   ├── cat_002.jpg                                         |
|  │   │   ├── cat_003.jpg                                         |
|  │   │   └── ... (many more images)                              |
|  │   ├── dogs/                                                    |
|  │   │   ├── dog_001.jpg                                         |
|  │   │   ├── dog_002.jpg                                         |
|  │   │   └── ...                                                  |
|  │   └── birds/                                                   |
|  │       ├── bird_001.jpg                                         |
|  │       ├── bird_002.jpg                                         |
|  │       └── ...                                                  |
|  └── val/                                                         |
|      ├── cats/                                                    |
|      │   ├── cat_101.jpg                                         |
|      │   └── ...                                                  |
|      ├── dogs/                                                    |
|      │   ├── dog_101.jpg                                         |
|      │   └── ...                                                  |
|      └── birds/                                                   |
|          ├── bird_101.jpg                                         |
|          └── ...                                                  |
|                                                                   |
|  The folder name IS the label. Images inside "cats/" are         |
|  automatically labeled as class "cats".                           |
|                                                                   |
+------------------------------------------------------------------+
```

### Creating and Loading the Dataset

```python
# Part 1: Preparing the dataset with ImageFolder

import os
import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

# =============================================================
# Step 1: Create the dataset directory structure
# =============================================================
# In a real project, you would download images or use an existing
# dataset. Here we show how to create the structure and use
# a built-in dataset for demonstration.

# For this project, we will use a subset of CIFAR-10
# which contains 10 classes of small images.
# We will select 3 classes: airplane, automobile, bird

# Define image transformations
# These convert raw images into the format our model expects

train_transform = transforms.Compose([
    transforms.Resize((224, 224)),       # Resize to 224x224 pixels
    transforms.RandomHorizontalFlip(),    # Randomly flip for augmentation
    transforms.RandomRotation(10),        # Randomly rotate up to 10 degrees
    transforms.ColorJitter(               # Randomly adjust colors
        brightness=0.2, contrast=0.2
    ),
    transforms.ToTensor(),                # Convert to PyTorch tensor
    transforms.Normalize(                 # Normalize pixel values
        mean=[0.485, 0.456, 0.406],       # ImageNet mean values
        std=[0.229, 0.224, 0.225]         # ImageNet std values
    )
])

val_transform = transforms.Compose([
    transforms.Resize((224, 224)),        # Resize only (no augmentation)
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

print("Image Transformations Defined")
print("=" * 55)
print(f"\nTraining transforms (with augmentation):")
print(f"  1. Resize to 224x224")
print(f"  2. Random horizontal flip")
print(f"  3. Random rotation (up to 10 degrees)")
print(f"  4. Color jitter (brightness, contrast)")
print(f"  5. Convert to tensor")
print(f"  6. Normalize with ImageNet statistics")
print(f"\nValidation transforms (no augmentation):")
print(f"  1. Resize to 224x224")
print(f"  2. Convert to tensor")
print(f"  3. Normalize with ImageNet statistics")
```

**Expected Output:**
```
Image Transformations Defined
=======================================================

Training transforms (with augmentation):
  1. Resize to 224x224
  2. Random horizontal flip
  3. Random rotation (up to 10 degrees)
  4. Color jitter (brightness, contrast)
  5. Convert to tensor
  6. Normalize with ImageNet statistics

Validation transforms (no augmentation):
  1. Resize to 224x224
  2. Convert to tensor
  3. Normalize with ImageNet statistics
```

Let us explain each transformation:

- **Resize(224, 224)**: Most pre-trained models expect 224x224 pixel images. We resize all images to this size regardless of their original size
- **RandomHorizontalFlip()**: Randomly mirrors the image horizontally. A cat facing left or right is still a cat. This is called **data augmentation** — creating variation to help the model generalize
- **RandomRotation(10)**: Rotates the image randomly up to 10 degrees. Real-world photos are rarely perfectly straight
- **ColorJitter**: Randomly adjusts brightness and contrast, simulating different lighting conditions
- **ToTensor()**: Converts the image from a PIL Image (height x width x channels, values 0-255) to a PyTorch tensor (channels x height x width, values 0.0-1.0)
- **Normalize**: Adjusts pixel values using ImageNet statistics. These specific mean and std values are standard when using pre-trained models

### Loading the Dataset

```python
# Step 2: Load dataset using ImageFolder

# If you have your own dataset organized in the ImageFolder format:
# train_dataset = datasets.ImageFolder('dataset/train', transform=train_transform)
# val_dataset = datasets.ImageFolder('dataset/val', transform=val_transform)

# For this example, we use CIFAR-10 and filter to 3 classes
from torchvision.datasets import CIFAR10

# Download CIFAR-10
full_train = CIFAR10(root='./data', train=True, download=True,
                      transform=train_transform)
full_val = CIFAR10(root='./data', train=False, download=True,
                    transform=val_transform)

# CIFAR-10 classes
# 0: airplane, 1: automobile, 2: bird, 3: cat, 4: deer
# 5: dog, 6: frog, 7: horse, 8: ship, 9: truck

# Filter to only 3 classes: cat (3), dog (5), bird (2)
selected_classes = [3, 5, 2]  # cat, dog, bird
class_names = ['cat', 'dog', 'bird']

# Create a mapping from old labels to new labels (0, 1, 2)
label_map = {old: new for new, old in enumerate(selected_classes)}

def filter_dataset(dataset, selected_classes, label_map):
    """Filter dataset to only include selected classes."""
    indices = [i for i, (_, label) in enumerate(dataset)
               if label in selected_classes]

    # Create subset
    filtered_images = []
    filtered_labels = []
    for idx in indices:
        img, label = dataset[idx]
        filtered_images.append(img)
        filtered_labels.append(label_map[label])

    return list(zip(filtered_images, filtered_labels))

# Note: For a real project with ImageFolder, you would do:
# train_dataset = datasets.ImageFolder('path/to/train', transform=train_transform)
# val_dataset = datasets.ImageFolder('path/to/val', transform=val_transform)

# For demonstration, we create DataLoaders directly from CIFAR-10
# In practice, ImageFolder handles all of this automatically

# Create DataLoaders
train_loader = DataLoader(full_train, batch_size=32, shuffle=True)
val_loader = DataLoader(full_val, batch_size=32, shuffle=False)

print("\nDataset Information")
print("=" * 55)
print(f"Training samples:   {len(full_train)}")
print(f"Validation samples: {len(full_val)}")
print(f"Number of classes:  {len(full_train.classes)}")
print(f"Class names:        {full_train.classes}")
print(f"Batch size:         32")
print(f"Training batches:   {len(train_loader)}")
print(f"Validation batches: {len(val_loader)}")

# Show sample batch shape
sample_images, sample_labels = next(iter(train_loader))
print(f"\nSample batch shape: {sample_images.shape}")
print(f"  Batch size:  {sample_images.shape[0]}")
print(f"  Channels:    {sample_images.shape[1]} (RGB)")
print(f"  Height:      {sample_images.shape[2]} pixels")
print(f"  Width:       {sample_images.shape[3]} pixels")
```

**Expected Output:**
```
Downloading CIFAR-10 dataset...

Dataset Information
=======================================================
Training samples:   50000
Validation samples: 10000
Number of classes:  10
Class names:        ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
Batch size:         32
Training batches:   1563
Validation batches: 313

Sample batch shape: torch.Size([32, 3, 224, 224])
  Batch size:  32
  Channels:    3 (RGB)
  Height:      224 pixels
  Width:       224 pixels
```

---

## 27.3 Part 2 — Building and Training a CNN

Now let us build a simple Convolutional Neural Network (CNN) from scratch and train it on our dataset.

```python
# Part 2: Building and training a CNN from scratch

import torch
import torch.nn as nn
import torch.optim as optim
import time

class SimpleCNN(nn.Module):
    """
    A simple CNN for image classification.

    Architecture:
    - 3 convolutional blocks (conv + relu + pool)
    - 2 fully connected layers
    - Output layer for classification
    """

    def __init__(self, num_classes=10):
        super().__init__()

        # Convolutional layers extract visual features
        self.features = nn.Sequential(
            # Block 1: 3 input channels (RGB) -> 32 feature maps
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),      # 224x224 -> 112x112

            # Block 2: 32 -> 64 feature maps
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),      # 112x112 -> 56x56

            # Block 3: 64 -> 128 feature maps
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),      # 56x56 -> 28x28
        )

        # Fully connected layers for classification
        self.classifier = nn.Sequential(
            nn.Flatten(),                    # 128 * 28 * 28 = 100352
            nn.Linear(128 * 28 * 28, 256),   # Reduce to 256
            nn.ReLU(),
            nn.Dropout(0.5),                  # Prevent overfitting
            nn.Linear(256, num_classes),      # Output: one score per class
        )

    def forward(self, x):
        x = self.features(x)     # Extract visual features
        x = self.classifier(x)   # Classify
        return x


# Create the model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = SimpleCNN(num_classes=10).to(device)

# Show model architecture
print("Simple CNN Architecture")
print("=" * 55)
total_params = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"Total parameters:     {total_params:,}")
print(f"Trainable parameters: {trainable_params:,}")
print(f"Device:               {device}")
print()

# Print layer details
print("Layer Details:")
for name, layer in model.named_modules():
    if isinstance(layer, (nn.Conv2d, nn.Linear)):
        params = sum(p.numel() for p in layer.parameters())
        print(f"  {name}: {layer} ({params:,} params)")
```

**Expected Output:**
```
Simple CNN Architecture
=======================================================
Total parameters:     25,930,378
Trainable parameters: 25,930,378
Device:               cpu

Layer Details:
  features.0: Conv2d(3, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1)) (896 params)
  features.3: Conv2d(32, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1)) (18,496 params)
  features.6: Conv2d(64, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1)) (73,856 params)
  classifier.1: Linear(in_features=100352, out_features=256, bias=True) (25,690,368 params)
  classifier.4: Linear(in_features=256, out_features=10, bias=True) (2,570 params)
```

```
+------------------------------------------------------------------+
|              CNN Architecture Diagram                             |
+------------------------------------------------------------------+
|                                                                   |
|  Input Image: 3 x 224 x 224 (RGB, 224 pixels x 224 pixels)      |
|       |                                                           |
|       v                                                           |
|  [Conv2d 3->32] + [ReLU] + [MaxPool]                            |
|  Output: 32 x 112 x 112                                         |
|       |                                                           |
|       v                                                           |
|  [Conv2d 32->64] + [ReLU] + [MaxPool]                           |
|  Output: 64 x 56 x 56                                           |
|       |                                                           |
|       v                                                           |
|  [Conv2d 64->128] + [ReLU] + [MaxPool]                          |
|  Output: 128 x 28 x 28                                          |
|       |                                                           |
|       v                                                           |
|  [Flatten]                                                        |
|  Output: 100,352 (= 128 * 28 * 28)                              |
|       |                                                           |
|       v                                                           |
|  [Linear 100352->256] + [ReLU] + [Dropout 0.5]                  |
|  Output: 256                                                      |
|       |                                                           |
|       v                                                           |
|  [Linear 256->10]                                                |
|  Output: 10 (one score per class)                                |
|                                                                   |
+------------------------------------------------------------------+
```

### Training the CNN

```python
# Training the CNN

def train_model(model, train_loader, val_loader, epochs=5, lr=0.001):
    """
    Train the model and print progress.

    Parameters:
        model: The neural network to train
        train_loader: DataLoader for training data
        val_loader: DataLoader for validation data
        epochs: Number of times to go through the entire dataset
        lr: Learning rate (how big each update step is)
    """

    criterion = nn.CrossEntropyLoss()  # Loss function for classification
    optimizer = optim.Adam(model.parameters(), lr=lr)  # Optimizer

    print("Training Started")
    print("=" * 65)

    best_val_acc = 0.0

    for epoch in range(epochs):
        # ---- Training Phase ----
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0

        start_time = time.time()

        for batch_idx, (images, labels) in enumerate(train_loader):
            images, labels = images.to(device), labels.to(device)

            # Forward pass: compute predictions
            outputs = model(images)
            loss = criterion(outputs, labels)

            # Backward pass: compute gradients
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            # Track statistics
            train_loss += loss.item()
            _, predicted = outputs.max(1)
            train_total += labels.size(0)
            train_correct += predicted.eq(labels).sum().item()

            # Print progress every 100 batches
            if (batch_idx + 1) % 100 == 0:
                print(f"  Epoch {epoch+1}/{epochs}, "
                      f"Batch {batch_idx+1}/{len(train_loader)}, "
                      f"Loss: {loss.item():.4f}")

        train_acc = 100.0 * train_correct / train_total
        avg_train_loss = train_loss / len(train_loader)

        # ---- Validation Phase ----
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)

                val_loss += loss.item()
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()

        val_acc = 100.0 * val_correct / val_total
        avg_val_loss = val_loss / len(val_loader)

        elapsed = time.time() - start_time

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), 'best_cnn_model.pth')

        print(f"\n  Epoch {epoch+1}/{epochs} Summary ({elapsed:.1f}s):")
        print(f"    Train Loss: {avg_train_loss:.4f}, "
              f"Train Acc: {train_acc:.2f}%")
        print(f"    Val Loss:   {avg_val_loss:.4f}, "
              f"Val Acc:   {val_acc:.2f}%")
        print(f"    Best Val Acc: {best_val_acc:.2f}%")
        print()

    print("Training Complete!")
    print(f"Best Validation Accuracy: {best_val_acc:.2f}%")
    return best_val_acc


# Train for a few epochs
best_acc = train_model(model, train_loader, val_loader, epochs=5, lr=0.001)
```

**Expected Output:**
```
Training Started
=================================================================
  Epoch 1/5, Batch 100/1563, Loss: 1.8234
  Epoch 1/5, Batch 200/1563, Loss: 1.5432
  ...

  Epoch 1/5 Summary (45.2s):
    Train Loss: 1.6234, Train Acc: 42.15%
    Val Loss:   1.3456, Val Acc:   52.30%
    Best Val Acc: 52.30%

  ...

  Epoch 5/5 Summary (44.8s):
    Train Loss: 0.8765, Train Acc: 69.45%
    Val Loss:   0.9876, Val Acc:   65.80%
    Best Val Acc: 66.20%

Training Complete!
Best Validation Accuracy: 66.20%
```

The CNN achieves around 65% accuracy after 5 epochs. This is decent, but we can do much better with transfer learning.

---

## 27.4 Part 3 — Transfer Learning with ResNet18

**Transfer learning** means taking a model that was already trained on a large dataset and adapting it for your specific task. Instead of learning everything from scratch, we start with knowledge that the model has already gained.

```
+------------------------------------------------------------------+
|              Transfer Learning Concept                            |
+------------------------------------------------------------------+
|                                                                   |
|  WITHOUT Transfer Learning:                                       |
|  Random weights --> Train on YOUR data --> Moderate accuracy      |
|  (The model starts knowing nothing)                               |
|                                                                   |
|  WITH Transfer Learning:                                          |
|  Pre-trained on ImageNet --> Fine-tune on YOUR data --> HIGH acc  |
|  (The model already knows about edges, shapes, textures)         |
|                                                                   |
|  ResNet18 was pre-trained on ImageNet (1.2M images, 1000 classes)|
|  It already knows how to recognize:                              |
|    - Edges and lines (early layers)                               |
|    - Textures and patterns (middle layers)                        |
|    - Complex features like eyes, fur, wheels (later layers)      |
|                                                                   |
|  We just need to teach it OUR specific classes.                  |
|                                                                   |
+------------------------------------------------------------------+
```

### Fine-Tuning ResNet18

```python
# Part 3: Transfer learning with ResNet18

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models

def create_resnet18_model(num_classes, freeze_features=True):
    """
    Create a ResNet18 model for transfer learning.

    Parameters:
        num_classes: Number of classes in your dataset
        freeze_features: If True, freeze pre-trained layers
                        (only train the final classification layer)
    """

    # Load ResNet18 pre-trained on ImageNet
    model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)

    # Freeze all pre-trained layers (optional but recommended)
    if freeze_features:
        for param in model.parameters():
            param.requires_grad = False

    # Replace the final fully connected layer
    # ResNet18's original fc layer outputs 1000 classes (ImageNet)
    # We replace it with our number of classes
    num_features = model.fc.in_features  # 512 for ResNet18
    model.fc = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(num_features, num_classes)
    )

    return model


# Create the transfer learning model
num_classes = 10  # CIFAR-10 has 10 classes
resnet_model = create_resnet18_model(num_classes, freeze_features=True)
resnet_model = resnet_model.to(device)

# Compare parameter counts
total_params = sum(p.numel() for p in resnet_model.parameters())
trainable_params = sum(p.numel() for p in resnet_model.parameters()
                       if p.requires_grad)
frozen_params = total_params - trainable_params

print("ResNet18 Transfer Learning Model")
print("=" * 55)
print(f"Total parameters:     {total_params:,}")
print(f"Frozen parameters:    {frozen_params:,} (pre-trained, not updated)")
print(f"Trainable parameters: {trainable_params:,} (our new layers)")
print(f"Percentage trainable: {100*trainable_params/total_params:.1f}%")
print(f"\nOriginal final layer: Linear(512, 1000) for ImageNet")
print(f"Our final layer:      Linear(512, {num_classes}) for our classes")
```

**Expected Output:**
```
ResNet18 Transfer Learning Model
=======================================================
Total parameters:     11,181,642
Frozen parameters:    11,176,512 (pre-trained, not updated)
Trainable parameters: 5,130 (our new layers)
Percentage trainable: 0.0%

Original final layer: Linear(512, 1000) for ImageNet
Our final layer:      Linear(512, 10) for our classes
```

Notice that we are only training 5,130 parameters out of over 11 million. The pre-trained features (edges, textures, shapes) are frozen. We only train the final classification layer to map those features to our classes.

### Training the ResNet18 Model

```python
# Train the ResNet18 model

# Use the same train_model function from Part 2
# But with a higher learning rate since we have fewer trainable parameters

print("\nTraining ResNet18 (Transfer Learning)")
print("=" * 55)

resnet_best_acc = train_model(
    resnet_model, train_loader, val_loader,
    epochs=5, lr=0.01  # Higher LR since fewer params
)

# Compare results
print("\n" + "=" * 55)
print("Comparison: CNN from Scratch vs Transfer Learning")
print("=" * 55)
print(f"  Simple CNN:          ~65% validation accuracy")
print(f"  ResNet18 (transfer): ~{resnet_best_acc:.0f}% validation accuracy")
print(f"  Improvement:         ~{resnet_best_acc - 65:.0f} percentage points")
```

**Expected Output:**
```
Training ResNet18 (Transfer Learning)
=======================================================
  Epoch 1/5, Batch 100/1563, Loss: 0.9876
  ...

  Epoch 1/5 Summary (38.5s):
    Train Loss: 0.8765, Train Acc: 72.30%
    Val Loss:   0.5432, Val Acc:   82.50%
    Best Val Acc: 82.50%

  ...

  Epoch 5/5 Summary (37.9s):
    Train Loss: 0.4321, Train Acc: 86.70%
    Val Loss:   0.3987, Val Acc:   87.40%
    Best Val Acc: 87.80%

Training Complete!
Best Validation Accuracy: 87.80%

=======================================================
Comparison: CNN from Scratch vs Transfer Learning
=======================================================
  Simple CNN:          ~65% validation accuracy
  ResNet18 (transfer): ~88% validation accuracy
  Improvement:         ~23 percentage points
```

Transfer learning gives us a massive accuracy boost — from about 65% to about 88% — while training fewer parameters and converging faster.

### Saving the Model for Deployment

```python
# Save the trained model for later use in our app

# Save just the model weights
torch.save(resnet_model.state_dict(), 'image_classifier.pth')

# Also save the class names for our app
import json

class_info = {
    'class_names': ['airplane', 'automobile', 'bird', 'cat', 'deer',
                    'dog', 'frog', 'horse', 'ship', 'truck'],
    'num_classes': 10,
    'model_name': 'resnet18',
    'image_size': 224,
}

with open('class_info.json', 'w') as f:
    json.dump(class_info, f, indent=2)

print("Model saved!")
print(f"  Model weights: image_classifier.pth")
print(f"  Class info:    class_info.json")
print(f"\nClass names: {class_info['class_names']}")
```

**Expected Output:**
```
Model saved!
  Model weights: image_classifier.pth
  Class info:    class_info.json

Class names: ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
```

---

## 27.5 Part 4 — Building the Gradio Web App

**Gradio** is a Python library that creates web interfaces for machine learning models with just a few lines of code. It allows anyone to interact with your model through a browser — no web development knowledge needed.

First, install Gradio:
```bash
pip install gradio
```

### Building the Complete App

```python
# Part 4: Complete Gradio web app for image classification

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import gradio as gr
import json

# =============================================================
# Step 1: Load the trained model
# =============================================================

def load_model(model_path, class_info_path):
    """Load the trained model and class information."""

    # Load class info
    with open(class_info_path, 'r') as f:
        class_info = json.load(f)

    num_classes = class_info['num_classes']
    class_names = class_info['class_names']

    # Recreate the model architecture
    model = models.resnet18(weights=None)  # No pre-trained weights
    num_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(num_features, num_classes)
    )

    # Load trained weights
    model.load_state_dict(torch.load(model_path, map_location='cpu'))
    model.eval()  # Set to evaluation mode

    return model, class_names


# Load model (use pre-trained ResNet18 if saved model not available)
try:
    model, class_names = load_model('image_classifier.pth', 'class_info.json')
    print("Loaded custom trained model")
except FileNotFoundError:
    # Fallback: use pre-trained ImageNet model for demonstration
    model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
    model.eval()

    # Load ImageNet class names
    weights = models.ResNet18_Weights.IMAGENET1K_V1
    class_names = weights.meta["categories"]
    print("Loaded pre-trained ImageNet model (1000 classes)")


# =============================================================
# Step 2: Define the prediction function
# =============================================================

# Image preprocessing (same as validation transform)
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


def classify_image(image):
    """
    Classify an uploaded image and return predictions.

    Parameters:
        image: A PIL Image uploaded by the user

    Returns:
        A dictionary mapping class names to confidence scores
    """

    if image is None:
        return {"No image provided": 1.0}

    # Preprocess the image
    input_tensor = preprocess(image)

    # Add batch dimension: (3, 224, 224) -> (1, 3, 224, 224)
    input_batch = input_tensor.unsqueeze(0)

    # Make prediction
    with torch.no_grad():
        outputs = model(input_batch)

    # Convert to probabilities using softmax
    probabilities = torch.nn.functional.softmax(outputs[0], dim=0)

    # Get top 5 predictions
    top5_probs, top5_indices = torch.topk(probabilities, 5)

    # Create results dictionary
    results = {}
    for i in range(5):
        class_idx = top5_indices[i].item()
        prob = top5_probs[i].item()
        class_name = class_names[class_idx]
        results[class_name] = float(prob)

    return results


# =============================================================
# Step 3: Create the Gradio interface
# =============================================================

# Build the web interface
demo = gr.Interface(
    fn=classify_image,           # Our prediction function
    inputs=gr.Image(type="pil"), # Input: image upload widget
    outputs=gr.Label(num_top_classes=5),  # Output: top-5 labels
    title="Image Classification App",
    description=(
        "Upload an image and the model will classify it. "
        "The model uses ResNet18 with transfer learning. "
        "It returns the top 5 predicted classes with confidence scores."
    ),
    examples=[
        # Add example images if you have them
        # ["example_cat.jpg"],
        # ["example_dog.jpg"],
    ],
    theme="default",
)

# =============================================================
# Step 4: Launch the app
# =============================================================

print("\nGradio App Configuration")
print("=" * 55)
print(f"Model:          ResNet18")
print(f"Classes:        {len(class_names)}")
print(f"Input:          Image upload (any size)")
print(f"Output:         Top 5 predictions with confidence")
print(f"Image size:     Resized to 224x224 internally")
print()
print("Starting the web app...")
print("Open your browser to the URL shown below.")
print()

# Launch the app
# share=True creates a public URL (useful for sharing)
demo.launch(share=False)  # Set share=True for a public link
```

**Expected Output:**
```
Loaded pre-trained ImageNet model (1000 classes)

Gradio App Configuration
=======================================================
Model:          ResNet18
Classes:        1000
Input:          Image upload (any size)
Output:         Top 5 predictions with confidence
Image size:     Resized to 224x224 internally

Starting the web app...
Open your browser to the URL shown below.

Running on local URL:  http://127.0.0.1:7860
```

```
+------------------------------------------------------------------+
|              Gradio Web Interface                                 |
+------------------------------------------------------------------+
|                                                                   |
|  +-----------------------------------------------------------+   |
|  |          Image Classification App                          |   |
|  +-----------------------------------------------------------+   |
|  |                                                             |   |
|  | Upload an image and the model will classify it.             |   |
|  |                                                             |   |
|  | +------------------------+  +---------------------------+  |   |
|  | |                        |  |  Top 5 Predictions:       |  |   |
|  | |                        |  |                           |  |   |
|  | |    [Drop image here]   |  |  1. Golden Retriever 89%  |  |   |
|  | |    or click to upload  |  |  2. Labrador       5%    |  |   |
|  | |                        |  |  3. Cocker Spaniel 2%    |  |   |
|  | |                        |  |  4. Irish Setter   1%    |  |   |
|  | +------------------------+  |  5. Beagle         1%    |  |   |
|  |                              +---------------------------+  |   |
|  |                                                             |   |
|  |  [Submit]  [Clear]                                          |   |
|  +-----------------------------------------------------------+   |
|                                                                   |
+------------------------------------------------------------------+
```

### Putting It All Together — Complete App File

Here is the complete, self-contained application file:

```python
# complete_app.py
# Run with: python complete_app.py

"""
Complete Image Classification App
Uses ResNet18 with transfer learning for image classification.
Provides a Gradio web interface for easy interaction.
"""

import torch
import torch.nn as nn
from torchvision import models, transforms
import gradio as gr

# ---- Model Setup ----
print("Loading model...")
model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
model.eval()

weights = models.ResNet18_Weights.IMAGENET1K_V1
class_names = weights.meta["categories"]
print(f"Model loaded with {len(class_names)} classes")

# ---- Image Preprocessing ----
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])

# ---- Prediction Function ----
def predict(image):
    """Classify an image and return top 5 predictions."""
    if image is None:
        return {}

    input_tensor = preprocess(image).unsqueeze(0)

    with torch.no_grad():
        output = model(input_tensor)

    probs = torch.nn.functional.softmax(output[0], dim=0)
    top5_probs, top5_ids = torch.topk(probs, 5)

    return {
        class_names[top5_ids[i]]: float(top5_probs[i])
        for i in range(5)
    }

# ---- Gradio Interface ----
demo = gr.Interface(
    fn=predict,
    inputs=gr.Image(type="pil"),
    outputs=gr.Label(num_top_classes=5),
    title="Image Classification App",
    description="Upload any image to classify it using ResNet18.",
)

if __name__ == "__main__":
    demo.launch()
```

To run this app, save it as `complete_app.py` and run `python complete_app.py`. Open the URL shown in the terminal in your browser, upload an image, and see the predictions.

---

## Common Mistakes

1. **Not matching transforms between training and inference**: The preprocessing applied during inference must match the validation transforms used during training. If you trained with `Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])`, you must use the same values during inference.

2. **Forgetting model.eval()**: When using the model for predictions, always call `model.eval()` first. This disables dropout and batch normalization updates, which are only needed during training.

3. **Not using torch.no_grad() during inference**: Wrap your prediction code with `with torch.no_grad():` to save memory and speed up inference. Without this, PyTorch records operations for gradient computation, which is unnecessary during prediction.

4. **Wrong image format for Gradio**: Gradio provides images as PIL Images by default (when `type="pil"`). Make sure your preprocessing pipeline starts from a PIL Image.

5. **Not saving class names with the model**: When deploying a model, always save the class names alongside the weights. Without class names, you can only see class indices (0, 1, 2) instead of meaningful labels.

---

## Best Practices

1. **Always use transfer learning**: Unless you have millions of training images, transfer learning with a pre-trained model will almost always outperform training from scratch.

2. **Start with frozen features**: Begin by freezing the pre-trained layers and only training the final classifier. If accuracy is not sufficient, gradually unfreeze later layers and fine-tune with a very small learning rate.

3. **Use data augmentation**: Random flips, rotations, and color adjustments help prevent overfitting and improve generalization, especially with small datasets.

4. **Validate on unseen data**: Always evaluate on a separate validation set. Training accuracy can be misleadingly high if the model memorizes the training data.

5. **Save models with metadata**: Save class names, image size, and model architecture alongside the weights so that anyone can reload and use the model correctly.

---

## Quick Summary

This project brought together dataset preparation, CNN training, transfer learning, and web deployment into a complete application. We used PyTorch's **ImageFolder** to organize images by class, built a **simple CNN** from scratch (achieving about 65% accuracy), then used **transfer learning with ResNet18** to jump to about 88% accuracy by leveraging features pre-trained on ImageNet. Finally, we wrapped the model in a **Gradio web interface** that allows anyone to upload images and get predictions in their browser with just a few lines of code.

---

## Key Points

- **ImageFolder** organizes images by placing them in class-named subdirectories
- Data augmentation (flips, rotations, color jitter) improves model robustness
- A simple CNN can achieve reasonable accuracy but has limitations
- **Transfer learning** with pre-trained models dramatically improves accuracy
- **ResNet18** pre-trained on ImageNet provides excellent visual features
- Freezing pre-trained layers and training only the classifier is efficient and effective
- **Gradio** creates web interfaces with just `gr.Interface(fn, inputs, outputs)`
- Always preprocess inference images identically to training validation images
- Save both model weights and class metadata for deployment

---

## Practice Questions

1. Why do we use different transforms for training and validation? Why is data augmentation only applied during training?

2. Explain why transfer learning with ResNet18 achieves much higher accuracy than a CNN trained from scratch, even though the ResNet18 classifier layer has far fewer trainable parameters.

3. What does `model.eval()` do, and why is it important to call it before making predictions?

4. If you wanted to classify medical X-ray images (a very different domain from ImageNet), would transfer learning from ResNet18 still help? Why or why not?

5. How would you modify this project to support 100 classes instead of 10?

---

## Exercises

**Exercise 1: Unfreeze and Fine-Tune**
Modify the ResNet18 training to first train with frozen features for 3 epochs, then unfreeze the last 2 residual blocks and continue training for 3 more epochs with a learning rate 10 times smaller. Compare the accuracy to the fully-frozen approach.

**Exercise 2: Add Confidence Threshold**
Modify the Gradio app to show a warning when the model's top prediction has confidence below 50%. Display a message like "Low confidence prediction — the model is uncertain about this image."

**Exercise 3: Multi-Image Classification**
Extend the Gradio app to accept multiple images at once (using `gr.File` with `file_count="multiple"`). Process each image, and display all results in a summary table showing the filename, top prediction, and confidence for each image.

---

## What Is Next?

You have built a complete image classification app — from data preparation to web deployment. In the next chapter, you will tackle a more advanced computer vision task: **object detection**. Instead of classifying what is in an image, you will build a system that finds WHERE objects are in an image and draws boxes around them. You will use YOLOv8, one of the fastest object detection models, and create another Gradio app for real-time detection.
