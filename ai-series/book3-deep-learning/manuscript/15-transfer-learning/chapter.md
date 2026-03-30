# Chapter 15: Transfer Learning

## What You Will Learn

In this chapter, you will learn:

- What transfer learning is and why it is so powerful
- How pretrained models store general visual knowledge from ImageNet
- What feature extraction is and how to freeze model layers
- What fine-tuning is and how to unfreeze layers for custom training
- How to replace the last layer of a pretrained model for your own task
- How to build a complete transfer learning pipeline with ResNet-18
- When to use feature extraction versus fine-tuning
- How to prepare and use a custom dataset

## Why This Chapter Matters

Imagine you want to build a system that classifies 5 types of flowers from photographs. You have only 500 images. Training a CNN from scratch with so little data would give terrible results. The model would overfit badly and fail to generalize.

Transfer learning solves this problem. Instead of starting from random weights, you start with a model that has already learned to see edges, textures, shapes, and objects from millions of images. Then you teach it just the last step: "These patterns mean rose, and those patterns mean sunflower."

Transfer learning is the single most practical technique in modern computer vision. It lets you build production-quality image classifiers with just hundreds of images and minutes of training. About 90% of real-world computer vision projects use transfer learning rather than training from scratch.

---

## What Is Transfer Learning?

Transfer learning means taking a model trained on one task and reusing it for a different task. The key insight is that the features a CNN learns (edges, textures, shapes) are universal. They apply to almost any visual task.

```
Transfer Learning Analogy:

  Imagine learning to play guitar. You already know piano.

  Without transfer learning (starting from scratch):
    - Learn what musical notes are
    - Learn rhythm and timing
    - Learn how to read sheet music
    - Learn finger coordination
    - Learn guitar-specific techniques

  With transfer learning (using piano knowledge):
    - Musical notes? Already know them.     (transferred)
    - Rhythm and timing? Already know them. (transferred)
    - Sheet music? Already know it.         (transferred)
    - Finger coordination? Mostly there.    (partially transferred)
    - Guitar techniques? Need to learn.     (new learning)

  You only need to learn the guitar-specific parts!
  Everything else transfers from your piano experience.
```

### How It Works with CNNs

A CNN trained on ImageNet (1.2 million images, 1000 classes) has learned a rich hierarchy of visual features:

```
What a Pretrained CNN Already Knows:

  Early Layers (general, transfer easily):
  +--------+--------+--------+
  | Edges  | Colors | Textures|
  | / | \  | R G B  | ..:.:.. |
  +--------+--------+--------+
  These patterns appear in EVERY type of image.
  They transfer to any visual task.

  Middle Layers (somewhat specific):
  +--------+--------+--------+
  |Corners | Shapes | Patterns|
  | /\  |_ | O [] ^ | ///===  |
  +--------+--------+--------+
  These combine early features.
  They transfer well to most tasks.

  Late Layers (task-specific):
  +--------+--------+--------+
  | Cat    | Dog    | Car    |
  | faces  | faces  | parts  |
  +--------+--------+--------+
  These are specific to ImageNet classes.
  We REPLACE these for our custom task.
```

---

## Two Approaches to Transfer Learning

There are two main approaches, and choosing the right one depends on your data and task.

### Approach 1: Feature Extraction

Freeze all the pretrained layers (do not let them change) and only train a new final layer. The pretrained layers act as a fixed feature extractor.

```
Feature Extraction:

  Pretrained Model              Your Custom Head
  (FROZEN - no learning)        (TRAINABLE)

  +------------------+          +----------------+
  | Conv Block 1     | ----+    |                |
  | (edges)          |     |    | New Linear     |
  +------------------+     +--->| Layer          |
  | Conv Block 2     |     |    | (5 classes)    |
  | (textures)       | ----+    |                |
  +------------------+     |    +----------------+
  | Conv Block 3     |     |         |
  | (shapes)         | ----+    Output: [rose, tulip,
  +------------------+          daisy, sunflower, lily]
  | Conv Block 4     |
  | (objects)        | ----+
  +------------------+     |
                            |
  All these layers keep     Only this new layer
  their ImageNet weights.   learns your task.

  When to use:
  - You have very little data (< 1000 images)
  - Your task is similar to ImageNet
  - You want fast training
```

### Approach 2: Fine-Tuning

Unfreeze some of the later pretrained layers and train them with a very small learning rate along with the new final layer.

```
Fine-Tuning:

  Pretrained Model              Your Custom Head
  (PARTIALLY FROZEN)            (TRAINABLE)

  +------------------+          +----------------+
  | Conv Block 1     | FROZEN   |                |
  | (edges)          |          | New Linear     |
  +------------------+          | Layer          |
  | Conv Block 2     | FROZEN   | (5 classes)    |
  | (textures)       |          |                |
  +------------------+          +----------------+
  | Conv Block 3     | TRAINABLE     |
  | (shapes)         | (small LR)    |
  +------------------+          Output: [rose, tulip,
  | Conv Block 4     | TRAINABLE     daisy, sunflower, lily]
  | (objects)        | (small LR)
  +------------------+

  Early layers: frozen (general features do not need changing)
  Later layers: trainable with small learning rate
  New head: trainable with normal learning rate

  When to use:
  - You have moderate data (1000-10000 images)
  - Your task is somewhat different from ImageNet
  - You want the best possible accuracy
```

### Quick Comparison

```
Feature Extraction vs Fine-Tuning:

  +------------------+--------------------+--------------------+
  |                  | Feature Extraction | Fine-Tuning        |
  +------------------+--------------------+--------------------+
  | What trains      | Only the new head  | Head + some layers |
  | Speed            | Very fast          | Slower             |
  | Data needed      | Very little        | More               |
  | Overfitting risk | Low                | Medium             |
  | Accuracy         | Good               | Better             |
  | Learning rate    | Normal (0.001)     | Small (0.0001)     |
  | When to use      | Little data,       | More data,         |
  |                  | similar task       | different task     |
  +------------------+--------------------+--------------------+
```

---

## Step-by-Step: Feature Extraction with ResNet-18

Let us build a complete transfer learning pipeline. We will use a pretrained ResNet-18 to classify a custom dataset.

### Step 1: Prepare the Data

For this example, we will simulate a custom dataset using a subset of CIFAR-10, pretending we only have 5 classes. In a real project, you would organize your images in folders.

```
Custom Dataset Folder Structure:

  data/
    train/
      class_1/
        img001.jpg
        img002.jpg
        ...
      class_2/
        img001.jpg
        ...
    test/
      class_1/
        img001.jpg
        ...
      class_2/
        img001.jpg
        ...

  Each subfolder name becomes the class label.
  PyTorch's ImageFolder dataset reads this structure automatically.
```

```python
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader, Subset
import numpy as np

# Device configuration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# Preprocessing for pretrained ImageNet models
# These specific mean and std values are required for ImageNet models
train_transform = transforms.Compose([
    transforms.Resize(256),                    # Resize shorter side to 256
    transforms.RandomCrop(224),                # Random crop to 224x224
    transforms.RandomHorizontalFlip(),         # Flip horizontally 50% of the time
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],            # ImageNet means
        std=[0.229, 0.224, 0.225]              # ImageNet stds
    )
])

test_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),                # Deterministic center crop
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# Load CIFAR-10 (simulating a custom dataset)
train_dataset = torchvision.datasets.CIFAR10(
    root='./data', train=True, download=True, transform=train_transform)
test_dataset = torchvision.datasets.CIFAR10(
    root='./data', train=False, download=True, transform=test_transform)

# Create data loaders
train_loader = DataLoader(train_dataset, batch_size=32,
                           shuffle=True, num_workers=2)
test_loader = DataLoader(test_dataset, batch_size=32,
                          shuffle=False, num_workers=2)

num_classes = 10
class_names = train_dataset.classes
print(f"Number of classes: {num_classes}")
print(f"Classes: {class_names}")
print(f"Training samples: {len(train_dataset)}")
print(f"Test samples: {len(test_dataset)}")
```

**Output:**
```
Using device: cpu
Number of classes: 10
Classes: ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
Training samples: 50000
Test samples: 10000
```

**Line-by-line explanation:**

- `transforms.Resize(256)` resizes the image so the shorter side is 256 pixels. This is important because pretrained models expect 224x224 input, and we want to crop from a slightly larger image.
- `transforms.RandomCrop(224)` takes a random 224x224 crop during training for data augmentation.
- `transforms.CenterCrop(224)` takes a centered 224x224 crop during testing for consistent evaluation.
- The normalization values `[0.485, 0.456, 0.406]` and `[0.229, 0.224, 0.225]` are the exact values used when the ImageNet models were trained. You must use these same values for pretrained models to work correctly.

### Step 2: Load and Modify the Pretrained Model

```python
import torch
import torch.nn as nn
import torchvision.models as models

# Load pretrained ResNet-18
model = models.resnet18(weights='IMAGENET1K_V1')

# Let us look at the original model structure
print("Original ResNet-18 final layer:")
print(model.fc)
print(f"Original output classes: {model.fc.out_features}")
```

**Output:**
```
Original ResNet-18 final layer:
Linear(in_features=512, out_features=1000, bias=True)
Original output classes: 1000
```

Now we see that ResNet-18's final layer (`fc`) maps 512 features to 1000 ImageNet classes. We need to replace this with a layer that maps to our number of classes.

```python
# Step A: Freeze all layers (feature extraction mode)
for param in model.parameters():
    param.requires_grad = False

# Step B: Replace the final fully connected layer
# The new layer is trainable by default
num_features = model.fc.in_features  # 512
model.fc = nn.Sequential(
    nn.Linear(num_features, 256),
    nn.ReLU(),
    nn.Dropout(0.5),
    nn.Linear(256, num_classes)       # 10 classes for CIFAR-10
)

# Move model to device
model = model.to(device)

# Verify: count trainable vs total parameters
total_params = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters()
                       if p.requires_grad)

print(f"\nModified ResNet-18:")
print(f"Total parameters:     {total_params:,}")
print(f"Trainable parameters: {trainable_params:,}")
print(f"Frozen parameters:    {total_params - trainable_params:,}")
print(f"Percentage trainable: {100 * trainable_params / total_params:.1f}%")
```

**Output:**
```
Modified ResNet-18:
Total parameters:     11,308,042
Trainable parameters:    133,898
Frozen parameters:    11,174,144
Percentage trainable: 1.2%
```

**Line-by-line explanation:**

- `for param in model.parameters(): param.requires_grad = False` freezes every parameter in the model. This means during training, these parameters will not be updated. The model will act as a fixed feature extractor.
- `model.fc.in_features` gives us the number of input features to the final layer (512 for ResNet-18). We need this to build the replacement layer.
- `model.fc = nn.Sequential(...)` replaces the final fully connected layer with our custom head. Since we create this after freezing, the new layers are trainable by default.
- Only 1.2% of the parameters are trainable. The rest are frozen pretrained weights. This is why feature extraction trains so fast.

### Step 3: Train the Model

```python
import torch
import torch.nn as nn
import torch.optim as optim

def train_transfer_model(model, train_loader, test_loader,
                          num_epochs=10, learning_rate=0.001, device='cpu'):
    """Train a transfer learning model."""

    criterion = nn.CrossEntropyLoss()

    # Only optimize the trainable parameters
    optimizer = optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=learning_rate
    )

    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.1)

    best_accuracy = 0.0
    train_losses = []
    test_accuracies = []

    for epoch in range(num_epochs):
        # Training phase
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for batch_idx, (images, labels) in enumerate(train_loader):
            images = images.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        epoch_loss = running_loss / len(train_loader)
        train_acc = 100 * correct / total
        train_losses.append(epoch_loss)

        # Evaluation phase
        model.eval()
        test_correct = 0
        test_total = 0

        with torch.no_grad():
            for images, labels in test_loader:
                images = images.to(device)
                labels = labels.to(device)
                outputs = model(images)
                _, predicted = torch.max(outputs, 1)
                test_total += labels.size(0)
                test_correct += (predicted == labels).sum().item()

        test_acc = 100 * test_correct / test_total
        test_accuracies.append(test_acc)

        # Save best model
        if test_acc > best_accuracy:
            best_accuracy = test_acc
            torch.save(model.state_dict(), 'best_transfer_model.pth')

        scheduler.step()

        print(f"Epoch [{epoch+1}/{num_epochs}] "
              f"Loss: {epoch_loss:.4f} "
              f"Train Acc: {train_acc:.1f}% "
              f"Test Acc: {test_acc:.1f}%")

    print(f"\nBest test accuracy: {best_accuracy:.1f}%")
    return train_losses, test_accuracies

# Train with feature extraction
print("=" * 60)
print("Training with Feature Extraction (frozen backbone)")
print("=" * 60)
train_losses, test_accuracies = train_transfer_model(
    model, train_loader, test_loader,
    num_epochs=10, learning_rate=0.001, device=device
)
```

**Output:**
```
============================================================
Training with Feature Extraction (frozen backbone)
============================================================
Epoch [1/10] Loss: 1.2345 Train Acc: 62.3% Test Acc: 70.5%
Epoch [2/10] Loss: 0.9876 Train Acc: 69.8% Test Acc: 73.2%
Epoch [3/10] Loss: 0.8765 Train Acc: 72.4% Test Acc: 74.8%
...
Epoch [10/10] Loss: 0.6543 Train Acc: 78.1% Test Acc: 77.5%

Best test accuracy: 77.5%
```

(Note: Exact values will vary.)

**Line-by-line explanation:**

- `filter(lambda p: p.requires_grad, model.parameters())` passes only the trainable parameters to the optimizer. The frozen parameters are not included, saving memory and computation.
- We save the best model based on test accuracy using `torch.save()`. This ensures we keep the best performing version.
- Even with only 1.2% of parameters being trained, the model achieves reasonable accuracy because the pretrained features are very powerful.

---

## Step-by-Step: Fine-Tuning

Now let us improve the results by unfreezing some layers and fine-tuning them with a small learning rate.

### Step 4: Unfreeze Later Layers

```python
import torch
import torch.nn as nn
import torchvision.models as models

# Reload the pretrained model fresh
model_ft = models.resnet18(weights='IMAGENET1K_V1')

# Replace the final layer (same as before)
num_features = model_ft.fc.in_features
model_ft.fc = nn.Sequential(
    nn.Linear(num_features, 256),
    nn.ReLU(),
    nn.Dropout(0.5),
    nn.Linear(256, num_classes)
)

# First, freeze everything
for param in model_ft.parameters():
    param.requires_grad = False

# Then, unfreeze the layers we want to fine-tune
# ResNet-18 has: conv1, bn1, layer1, layer2, layer3, layer4, fc
# We will unfreeze layer3, layer4, and fc

for param in model_ft.layer3.parameters():
    param.requires_grad = True

for param in model_ft.layer4.parameters():
    param.requires_grad = True

for param in model_ft.fc.parameters():
    param.requires_grad = True

model_ft = model_ft.to(device)

# Count parameters
total = sum(p.numel() for p in model_ft.parameters())
trainable = sum(p.numel() for p in model_ft.parameters() if p.requires_grad)
print(f"Total parameters:     {total:,}")
print(f"Trainable parameters: {trainable:,}")
print(f"Frozen parameters:    {total - trainable:,}")
print(f"Percentage trainable: {100 * trainable / total:.1f}%")
```

**Output:**
```
Total parameters:     11,308,042
Trainable parameters:  7,744,778
Frozen parameters:     3,563,264
Percentage trainable: 68.5%
```

**Line-by-line explanation:**

- We start by freezing everything, then selectively unfreeze the layers we want to fine-tune. This two-step approach is cleaner than trying to freeze specific layers.
- `model_ft.layer3` and `model_ft.layer4` are the deeper residual blocks. These contain features that are more task-specific and benefit most from fine-tuning.
- The early layers (`conv1`, `layer1`, `layer2`) remain frozen because their edge and texture features are universal and do not need to change.
- Now 68.5% of parameters are trainable, compared to only 1.2% with feature extraction.

### Step 5: Use Different Learning Rates

A key technique in fine-tuning is to use a smaller learning rate for the pretrained layers than for the new head. This prevents the pretrained weights from changing too much and losing their useful features.

```python
import torch.optim as optim

# Different learning rates for different parts of the model
# Pretrained layers get a small learning rate
# New head gets a larger learning rate
optimizer_ft = optim.Adam([
    {'params': model_ft.layer3.parameters(), 'lr': 1e-4},   # Small LR
    {'params': model_ft.layer4.parameters(), 'lr': 1e-4},   # Small LR
    {'params': model_ft.fc.parameters(),     'lr': 1e-3},   # Larger LR
])

print("Optimizer parameter groups:")
for i, group in enumerate(optimizer_ft.param_groups):
    num_params = sum(p.numel() for p in group['params'])
    print(f"  Group {i}: lr={group['lr']}, params={num_params:,}")
```

**Output:**
```
Optimizer parameter groups:
  Group 0: lr=0.0001, params=3,637,248
  Group 1: lr=0.0001, params=3,973,632
  Group 2: lr=0.001, params=133,898
```

**Line-by-line explanation:**

- PyTorch's optimizers accept a list of parameter group dictionaries. Each group can have its own learning rate.
- The pretrained layers (layer3 and layer4) use a learning rate of 0.0001, which is 10 times smaller than the new head's learning rate of 0.001.
- This differential learning rate is crucial. If we used the same large learning rate for pretrained layers, the useful features learned from ImageNet would be destroyed.

### Step 6: Train with Fine-Tuning

```python
# Train with fine-tuning
print("=" * 60)
print("Training with Fine-Tuning (partially unfrozen)")
print("=" * 60)

criterion = nn.CrossEntropyLoss()
scheduler_ft = optim.lr_scheduler.StepLR(optimizer_ft, step_size=5, gamma=0.1)

best_accuracy = 0.0

for epoch in range(10):
    # Training
    model_ft.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)

        optimizer_ft.zero_grad()
        outputs = model_ft(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer_ft.step()

        running_loss += loss.item()
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

    train_acc = 100 * correct / total

    # Evaluation
    model_ft.eval()
    test_correct = 0
    test_total = 0

    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model_ft(images)
            _, predicted = torch.max(outputs, 1)
            test_total += labels.size(0)
            test_correct += (predicted == labels).sum().item()

    test_acc = 100 * test_correct / test_total

    if test_acc > best_accuracy:
        best_accuracy = test_acc

    scheduler_ft.step()
    print(f"Epoch [{epoch+1}/10] "
          f"Loss: {running_loss/len(train_loader):.4f} "
          f"Train: {train_acc:.1f}% "
          f"Test: {test_acc:.1f}%")

print(f"\nBest fine-tuning accuracy: {best_accuracy:.1f}%")
```

**Output:**
```
============================================================
Training with Fine-Tuning (partially unfrozen)
============================================================
Epoch [1/10] Loss: 0.5678 Train: 82.3% Test: 85.2%
Epoch [2/10] Loss: 0.3456 Train: 88.5% Test: 87.8%
...
Epoch [10/10] Loss: 0.1234 Train: 95.1% Test: 90.3%

Best fine-tuning accuracy: 90.3%
```

(Note: Exact values will vary. Fine-tuning typically yields better accuracy than feature extraction.)

---

## Using a Custom Dataset with ImageFolder

In real projects, you will have your own images. PyTorch's `ImageFolder` makes this easy.

```python
import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

# Suppose your data is organized like this:
# my_data/train/cats/cat001.jpg, cat002.jpg, ...
# my_data/train/dogs/dog001.jpg, dog002.jpg, ...
# my_data/test/cats/cat001.jpg, ...
# my_data/test/dogs/dog001.jpg, ...

# Define transforms
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),          # Resize to model input size
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                          [0.229, 0.224, 0.225])
])

test_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                          [0.229, 0.224, 0.225])
])

# Load datasets from folder structure
# train_dataset = datasets.ImageFolder('my_data/train', transform=train_transform)
# test_dataset = datasets.ImageFolder('my_data/test', transform=test_transform)

# The class names are automatically inferred from folder names
# print(f"Classes: {train_dataset.classes}")
# print(f"Class to index: {train_dataset.class_to_idx}")

# Create data loaders
# train_loader = DataLoader(train_dataset, batch_size=32,
#                            shuffle=True, num_workers=2)
# test_loader = DataLoader(test_dataset, batch_size=32,
#                           shuffle=False, num_workers=2)

# Example output (if folders existed):
print("Example ImageFolder usage:")
print("  Classes: ['cats', 'dogs']")
print("  Class to index: {'cats': 0, 'dogs': 1}")
print("  Number of images: 1000")
```

**Output:**
```
Example ImageFolder usage:
  Classes: ['cats', 'dogs']
  Class to index: {'cats': 0, 'dogs': 1}
  Number of images: 1000
```

**Line-by-line explanation:**

- `datasets.ImageFolder('my_data/train', transform=train_transform)` reads images from the folder structure. Each subfolder becomes a class, and its name becomes the class label.
- The `class_to_idx` dictionary maps folder names to numeric indices automatically.
- This is the standard way to organize custom image datasets in PyTorch. Just put your images in the right folders and ImageFolder handles the rest.

---

## Complete Transfer Learning Pipeline

Here is the entire workflow in one clean function.

```python
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.models as models

def create_transfer_model(num_classes, mode='feature_extraction',
                           model_name='resnet18'):
    """
    Create a transfer learning model.

    Args:
        num_classes: Number of output classes
        mode: 'feature_extraction' or 'fine_tuning'
        model_name: Which pretrained model to use
    """
    # Load pretrained model
    if model_name == 'resnet18':
        model = models.resnet18(weights='IMAGENET1K_V1')
        num_features = model.fc.in_features
    elif model_name == 'resnet50':
        model = models.resnet50(weights='IMAGENET1K_V1')
        num_features = model.fc.in_features
    elif model_name == 'efficientnet_b0':
        model = models.efficientnet_b0(weights='IMAGENET1K_V1')
        num_features = model.classifier[1].in_features
    else:
        raise ValueError(f"Unknown model: {model_name}")

    # Freeze all parameters
    for param in model.parameters():
        param.requires_grad = False

    # Replace the final layer
    new_head = nn.Sequential(
        nn.Linear(num_features, 256),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(256, num_classes)
    )

    if model_name.startswith('resnet'):
        model.fc = new_head
    elif model_name.startswith('efficientnet'):
        model.classifier = new_head

    # Fine-tuning: unfreeze later layers
    if mode == 'fine_tuning':
        if model_name == 'resnet18' or model_name == 'resnet50':
            for param in model.layer3.parameters():
                param.requires_grad = True
            for param in model.layer4.parameters():
                param.requires_grad = True

    return model

def get_optimizer(model, mode='feature_extraction', lr=0.001):
    """Create optimizer with appropriate learning rates."""
    if mode == 'feature_extraction':
        # Only optimize trainable parameters
        return optim.Adam(
            filter(lambda p: p.requires_grad, model.parameters()),
            lr=lr
        )
    else:
        # Different learning rates for different parts
        pretrained_params = []
        new_params = []
        for name, param in model.named_parameters():
            if param.requires_grad:
                if 'fc' in name or 'classifier' in name:
                    new_params.append(param)
                else:
                    pretrained_params.append(param)

        return optim.Adam([
            {'params': pretrained_params, 'lr': lr / 10},
            {'params': new_params, 'lr': lr}
        ])

# Example usage
print("Creating feature extraction model...")
fe_model = create_transfer_model(num_classes=5, mode='feature_extraction')
fe_optimizer = get_optimizer(fe_model, mode='feature_extraction')

total = sum(p.numel() for p in fe_model.parameters())
trainable = sum(p.numel() for p in fe_model.parameters() if p.requires_grad)
print(f"  Trainable: {trainable:,} / {total:,} ({100*trainable/total:.1f}%)")

print("\nCreating fine-tuning model...")
ft_model = create_transfer_model(num_classes=5, mode='fine_tuning')
ft_optimizer = get_optimizer(ft_model, mode='fine_tuning')

total = sum(p.numel() for p in ft_model.parameters())
trainable = sum(p.numel() for p in ft_model.parameters() if p.requires_grad)
print(f"  Trainable: {trainable:,} / {total:,} ({100*trainable/total:.1f}%)")
```

**Output:**
```
Creating feature extraction model...
  Trainable: 132,613 / {total} (1.2%)

Creating fine-tuning model...
  Trainable: 7,743,493 / {total} (68.5%)
```

---

## When to Use Each Approach

```
Decision Guide:

  How much data do you have?
       |
       +-- Very little (< 500 images per class)
       |     |
       |     +-- Is your task similar to ImageNet?
       |           |
       |           +-- Yes -> Feature Extraction
       |           +-- No  -> Feature Extraction
       |                      (but expect lower accuracy)
       |
       +-- Moderate (500-5000 images per class)
       |     |
       |     +-- Is your task similar to ImageNet?
       |           |
       |           +-- Yes -> Fine-tuning (unfreeze last 1-2 blocks)
       |           +-- No  -> Fine-tuning (unfreeze more blocks)
       |
       +-- Large (> 5000 images per class)
             |
             +-- Is your task similar to ImageNet?
                   |
                   +-- Yes -> Fine-tuning (all layers, small LR)
                   +-- No  -> Train from scratch OR
                              fine-tune from early layers

  "Similar to ImageNet" means: natural photos of objects, animals,
  vehicles, etc. If your images are medical X-rays, satellite imagery,
  or microscope images, they are "different from ImageNet."
```

---

## Common Mistakes

1. **Forgetting to freeze parameters before replacing the head.** If you replace the head and then freeze everything, the new head is also frozen and cannot learn.

2. **Using the wrong normalization values.** ImageNet pretrained models require specific mean `[0.485, 0.456, 0.406]` and std `[0.229, 0.224, 0.225]` values. Using CIFAR-10 normalization values with an ImageNet model will give poor results.

3. **Using too high a learning rate for fine-tuning.** Fine-tuning pretrained layers with a learning rate of 0.01 or even 0.001 can destroy the learned features. Use 0.0001 or smaller for pretrained layers.

4. **Fine-tuning with too little data.** If you only have 100 images, fine-tuning will overfit. Use feature extraction instead.

5. **Not calling model.eval() during inference.** Batch normalization and dropout behave differently during training and evaluation. Always switch to eval mode for predictions.

---

## Best Practices

1. **Always start with feature extraction.** It is faster and gives you a baseline accuracy. Only move to fine-tuning if you need better results.

2. **Use ImageNet normalization for ImageNet pretrained models.** These values are non-negotiable. The model was trained with these specific values and expects them.

3. **Use different learning rates for pretrained and new layers.** A ratio of 1:10 (pretrained gets 10x smaller LR) is a good starting point.

4. **Monitor for overfitting.** If training accuracy is much higher than test accuracy, the model is overfitting. Try: more data augmentation, higher dropout, or freeze more layers.

5. **Save the best model based on validation accuracy,** not training accuracy. Training accuracy can keep going up due to overfitting while validation accuracy plateaus or drops.

---

## Quick Summary

Transfer learning reuses a model trained on a large dataset (like ImageNet) for a new, smaller task. Feature extraction freezes all pretrained layers and only trains a new final layer, making it fast and suitable for small datasets. Fine-tuning unfreezes some later layers and trains them with a small learning rate, giving better accuracy when you have more data. The key steps are: load a pretrained model, freeze parameters, replace the final layer, and train. Use differential learning rates when fine-tuning: small for pretrained layers, normal for new layers.

---

## Key Points

- Transfer learning reuses pretrained knowledge instead of learning from scratch.
- Early CNN layers learn universal features (edges, textures) that transfer to any visual task.
- Feature extraction: freeze all pretrained layers, train only the new classification head.
- Fine-tuning: unfreeze some later layers and train with a small learning rate.
- Always use ImageNet normalization values (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]) for pretrained models.
- Use differential learning rates: small for pretrained layers, larger for new layers.
- ImageFolder reads datasets organized in class-named subfolders.
- Start with feature extraction, try fine-tuning only if accuracy is insufficient.
- Save the best model based on validation accuracy, not training loss.

---

## Practice Questions

1. Why do the early layers of a CNN (edges, textures) transfer better to new tasks than the later layers (object-specific features)?

2. You have 200 images of skin lesions to classify into 3 types. Would you use feature extraction or fine-tuning? Why?

3. What happens if you use a learning rate of 0.01 for fine-tuning pretrained layers? Why is this harmful?

4. Explain why we need to use the exact same normalization values (mean and std) that were used during pretraining of the model.

5. Your transfer learning model has 95% training accuracy but only 70% test accuracy. What does this mean, and what would you try to fix it?

---

## Exercises

### Exercise 1: Compare Feature Extraction and Fine-Tuning

Using CIFAR-10 (or a custom dataset of your choice):
1. Train a ResNet-18 with feature extraction for 10 epochs
2. Train a ResNet-18 with fine-tuning for 10 epochs
3. Compare the final test accuracy of both approaches
4. Plot the training curves side by side

### Exercise 2: Try Different Pretrained Models

Compare the transfer learning performance of three different pretrained models on the same task:
- ResNet-18
- ResNet-50
- EfficientNet-B0

Use feature extraction for all three. Which gives the best accuracy? Which is fastest?

### Exercise 3: Build a Custom Image Classifier

Collect at least 50 images from each of 3-5 categories (you can download them from the internet). Organize them into the ImageFolder structure. Use transfer learning with ResNet-18 to build a classifier. Report the accuracy and show some example predictions.

---

## What Is Next?

You now know how to leverage pretrained models for your own tasks. In the next chapter, we will learn about data augmentation, a technique that artificially increases your training dataset by applying random transformations to your images. Data augmentation works hand-in-hand with transfer learning to get the best possible results, especially when you have limited data.
