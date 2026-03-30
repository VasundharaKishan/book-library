# Chapter 13: Building a CNN in PyTorch

## What You Will Learn

In this chapter, you will learn:

- How to use nn.Conv2d, nn.MaxPool2d, nn.Flatten, and nn.Linear to build a CNN
- How to load image datasets using torchvision
- How to preprocess images with transforms.Compose
- How to build a complete CNN class in PyTorch
- How to write a full training loop for image classification
- How to evaluate model accuracy on test data
- How to visualize learned filters
- How to train a CNN on the CIFAR-10 dataset

## Why This Chapter Matters

You have learned what convolution is (Chapter 11) and how CNN components fit together (Chapter 12). Now it is time to build a real, working CNN from scratch. This is where theory meets practice.

Building your first CNN is a milestone. After this chapter, you will have a working image classifier that can tell apart airplanes from automobiles, cats from dogs, and ships from trucks. More importantly, you will understand every line of code that makes it work, from loading the data to evaluating the results.

The skills you learn here will be the foundation for every computer vision project you work on in the future.

---

## Setting Up: Importing Libraries

Let us start by importing everything we need.

```python
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import numpy as np

# Check if GPU is available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")
```

**Output:**
```
Using device: cpu
```

(If you have a GPU with CUDA installed, it will show `cuda`.)

**Line-by-line explanation:**

- `torch` is the main PyTorch library for tensor operations and automatic differentiation.
- `torch.nn` contains all the neural network building blocks (layers, loss functions).
- `torch.optim` has optimizers like SGD and Adam that update model weights during training.
- `torchvision` provides popular datasets, pretrained models, and image transforms.
- `torchvision.transforms` has functions for preprocessing images (resizing, normalizing, augmenting).
- `DataLoader` handles batching, shuffling, and parallel loading of data.
- `matplotlib.pyplot` is for plotting images and training graphs.
- `torch.device(...)` checks whether a GPU is available. Training on a GPU is much faster, but the code works on CPU too.

---

## Loading the CIFAR-10 Dataset

CIFAR-10 is a classic image dataset with 60,000 color images in 10 classes. Each image is 32x32 pixels with 3 color channels (RGB). It has 50,000 training images and 10,000 test images.

```
CIFAR-10 Classes:

  +----------+----------+----------+----------+----------+
  | airplane | auto-    | bird     | cat      | deer     |
  |   (0)    | mobile(1)|   (2)    |   (3)    |   (4)    |
  +----------+----------+----------+----------+----------+
  | dog      | frog     | horse    | ship     | truck    |
  |   (5)    |   (6)    |   (7)    |   (8)    |   (9)    |
  +----------+----------+----------+----------+----------+

  Each image is 32x32 pixels, RGB color
  50,000 training images + 10,000 test images
```

### Preprocessing with transforms.Compose

Before feeding images to our CNN, we need to preprocess them. The two essential steps are:

1. **Convert to tensor:** Change the image from a PIL image (values 0-255) to a PyTorch tensor (values 0-1).
2. **Normalize:** Adjust the values to have a mean near 0 and standard deviation near 1 for each channel.

```python
# Define preprocessing steps
transform = transforms.Compose([
    transforms.ToTensor(),           # Convert PIL image to tensor (0-255 -> 0-1)
    transforms.Normalize(
        mean=(0.4914, 0.4822, 0.4465),  # CIFAR-10 channel means
        std=(0.2470, 0.2435, 0.2616)    # CIFAR-10 channel stds
    )
])

# Download and load training data
train_dataset = torchvision.datasets.CIFAR10(
    root='./data',        # Where to store the data
    train=True,           # Training set
    download=True,        # Download if not present
    transform=transform   # Apply our preprocessing
)

# Download and load test data
test_dataset = torchvision.datasets.CIFAR10(
    root='./data',
    train=False,          # Test set
    download=True,
    transform=transform
)

print(f"Training samples: {len(train_dataset)}")
print(f"Test samples: {len(test_dataset)}")
print(f"Image shape: {train_dataset[0][0].shape}")
print(f"Number of classes: {len(train_dataset.classes)}")
print(f"Classes: {train_dataset.classes}")
```

**Output:**
```
Training samples: 50000
Test samples: 10000
Image shape: torch.Size([3, 32, 32])
Number of classes: 10
Classes: ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
```

**Line-by-line explanation:**

- `transforms.Compose([...])` chains multiple transforms together. They are applied in order: first ToTensor, then Normalize.
- `transforms.ToTensor()` converts the image to a PyTorch tensor and scales pixel values from the range 0-255 to the range 0-1. It also rearranges dimensions from (H, W, C) to (C, H, W), which is what PyTorch expects.
- `transforms.Normalize(mean, std)` normalizes each channel by subtracting the mean and dividing by the standard deviation. The values `(0.4914, 0.4822, 0.4465)` are the precomputed means of the CIFAR-10 training set for the R, G, and B channels respectively.
- `torchvision.datasets.CIFAR10(...)` loads the CIFAR-10 dataset. Setting `download=True` downloads it the first time. The `transform` argument applies our preprocessing to every image automatically.
- `train_dataset[0]` returns a tuple of `(image_tensor, label)`. The image shape `(3, 32, 32)` means 3 channels, 32 height, 32 width.

### Creating Data Loaders

A DataLoader wraps the dataset and provides batching, shuffling, and parallel loading.

```python
# Create data loaders
batch_size = 64

train_loader = DataLoader(
    train_dataset,
    batch_size=batch_size,
    shuffle=True,          # Shuffle training data each epoch
    num_workers=2          # Use 2 background workers for loading
)

test_loader = DataLoader(
    test_dataset,
    batch_size=batch_size,
    shuffle=False,         # No need to shuffle test data
    num_workers=2
)

# Check one batch
images, labels = next(iter(train_loader))
print(f"Batch of images shape: {images.shape}")
print(f"Batch of labels shape: {labels.shape}")
print(f"First 10 labels: {labels[:10]}")
```

**Output:**
```
Batch of images shape: torch.Size([64, 3, 32, 32])
Batch of labels shape: torch.Size([64])
First 10 labels: tensor([6, 9, 9, 4, 1, 1, 2, 7, 8, 3])
```

**Line-by-line explanation:**

- `batch_size=64` means we process 64 images at a time. Larger batches are faster but use more memory. 64 is a good starting point.
- `shuffle=True` randomizes the order of training data each epoch. This helps the model learn better by seeing different orderings.
- `num_workers=2` uses 2 background processes to load data in parallel while the GPU trains. This prevents data loading from being a bottleneck.
- `next(iter(train_loader))` grabs one batch from the loader. The images have shape `(64, 3, 32, 32)`: 64 images, each with 3 channels, 32x32 pixels.

### Visualizing Sample Images

Let us look at some images from the dataset.

```python
# Class names for CIFAR-10
classes = ('airplane', 'automobile', 'bird', 'cat', 'deer',
           'dog', 'frog', 'horse', 'ship', 'truck')

def show_images(images, labels, num_images=8):
    """Display a grid of images with their labels."""
    fig, axes = plt.subplots(1, num_images, figsize=(12, 2))
    for i in range(num_images):
        # Unnormalize the image for display
        img = images[i]
        img = img * torch.tensor([0.2470, 0.2435, 0.2616]).view(3,1,1)
        img = img + torch.tensor([0.4914, 0.4822, 0.4465]).view(3,1,1)
        img = img.clamp(0, 1)

        # Convert from (C, H, W) to (H, W, C) for matplotlib
        img = img.permute(1, 2, 0).numpy()

        axes[i].imshow(img)
        axes[i].set_title(classes[labels[i]])
        axes[i].axis('off')
    plt.tight_layout()
    plt.savefig('sample_images.png', dpi=100)
    plt.show()

# Show first 8 images from the batch
show_images(images, labels, num_images=8)
print("Sample images saved to sample_images.png")
```

**Output:**
```
Sample images saved to sample_images.png
```

**Line-by-line explanation:**

- We undo the normalization to display the images correctly. We multiply by the standard deviation and add the mean back.
- `.clamp(0, 1)` ensures all values stay between 0 and 1 after unnormalization.
- `.permute(1, 2, 0)` rearranges dimensions from PyTorch format (C, H, W) to matplotlib format (H, W, C).
- Each image is shown with its class label as the title.

---

## Building the CNN Model

Now let us build our CNN class. We will create a model suitable for CIFAR-10 images (32x32 RGB).

```python
import torch
import torch.nn as nn

class CIFAR10CNN(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()

        # Convolution block 1
        # Input: (3, 32, 32) -> Output: (32, 16, 16)
        self.conv_block1 = nn.Sequential(
            nn.Conv2d(in_channels=3, out_channels=32,
                      kernel_size=3, padding=1),      # (3,32,32) -> (32,32,32)
            nn.BatchNorm2d(32),                        # Normalize
            nn.ReLU(),                                 # Activation
            nn.Conv2d(32, 32, kernel_size=3, padding=1), # (32,32,32) -> (32,32,32)
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),     # (32,32,32) -> (32,16,16)
            nn.Dropout2d(p=0.25)                       # Drop 25% of feature maps
        )

        # Convolution block 2
        # Input: (32, 16, 16) -> Output: (64, 8, 8)
        self.conv_block2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, padding=1),  # (32,16,16) -> (64,16,16)
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),  # (64,16,16) -> (64,16,16)
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),        # (64,16,16) -> (64,8,8)
            nn.Dropout2d(p=0.25)
        )

        # Convolution block 3
        # Input: (64, 8, 8) -> Output: (128, 4, 4)
        self.conv_block3 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=3, padding=1), # (64,8,8) -> (128,8,8)
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.Conv2d(128, 128, kernel_size=3, padding=1),# (128,8,8) -> (128,8,8)
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),        # (128,8,8) -> (128,4,4)
            nn.Dropout2d(p=0.25)
        )

        # Classification head
        self.classifier = nn.Sequential(
            nn.Flatten(),                                  # (128,4,4) -> (2048,)
            nn.Linear(128 * 4 * 4, 512),                   # 2048 -> 512
            nn.ReLU(),
            nn.Dropout(p=0.5),                             # Drop 50% during training
            nn.Linear(512, num_classes)                     # 512 -> 10
        )

    def forward(self, x):
        x = self.conv_block1(x)
        x = self.conv_block2(x)
        x = self.conv_block3(x)
        x = self.classifier(x)
        return x

# Create the model and move it to the device (CPU or GPU)
model = CIFAR10CNN(num_classes=10).to(device)

# Print model summary
print(model)

# Count parameters
total_params = sum(p.numel() for p in model.parameters())
print(f"\nTotal parameters: {total_params:,}")
```

**Output:**
```
CIFAR10CNN(
  (conv_block1): Sequential(
    (0): Conv2d(3, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
    (1): BatchNorm2d(32, eps=1e-05, momentum=0.1, affine=True, tracking_running_stats=True)
    (2): ReLU()
    (3): Conv2d(32, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
    (4): BatchNorm2d(32, eps=1e-05, momentum=0.1, affine=True, tracking_running_stats=True)
    (5): ReLU()
    (6): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
    (7): Dropout2d(p=0.25, inplace=False)
  )
  (conv_block2): Sequential(
    (0): Conv2d(32, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
    (1): BatchNorm2d(64, eps=1e-05, momentum=0.1, affine=True, tracking_running_stats=True)
    (2): ReLU()
    (3): Conv2d(64, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
    (4): BatchNorm2d(64, eps=1e-05, momentum=0.1, affine=True, tracking_running_stats=True)
    (5): ReLU()
    (6): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
    (7): Dropout2d(p=0.25, inplace=False)
  )
  (conv_block3): Sequential(
    (0): Conv2d(64, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
    (1): BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=True, tracking_running_stats=True)
    (2): ReLU()
    (3): Conv2d(128, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
    (4): BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=True, tracking_running_stats=True)
    (5): ReLU()
    (6): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
    (7): Dropout2d(p=0.25, inplace=False)
  )
  (classifier): Sequential(
    (0): Flatten(start_dim=1, end_dim=-1)
    (1): Linear(in_features=2048, out_features=512, bias=True)
    (2): ReLU()
    (3): Dropout(p=0.5, inplace=False)
    (4): Linear(in_features=512, out_features=10, bias=True)
  )
)

Total parameters: 1,199,882
```

**Line-by-line explanation:**

- Each convolution block follows the pattern: Conv -> BatchNorm -> ReLU -> Conv -> BatchNorm -> ReLU -> MaxPool -> Dropout. Using two convolution layers before each pooling layer lets the network learn more complex patterns before reducing the size.
- `nn.Dropout2d(p=0.25)` drops entire feature maps (channels) rather than individual values. This is more appropriate for convolution layers because neighboring pixels are correlated.
- The classifier section uses `nn.Dropout(p=0.5)`, a higher dropout rate, because fully connected layers are more prone to overfitting.
- `128 * 4 * 4 = 2048` is the size of the flattened feature maps. After three rounds of MaxPool2d(2,2), the spatial dimensions go from 32 to 16 to 8 to 4.
- `.to(device)` moves the model to the GPU if available, or keeps it on CPU.

```
How Dimensions Change in Our CNN:

  Layer                Input Shape       Output Shape
  -----                -----------       ------------
  Input                (3, 32, 32)       -
  conv_block1          (3, 32, 32)       (32, 16, 16)
  conv_block2          (32, 16, 16)      (64, 8, 8)
  conv_block3          (64, 8, 8)        (128, 4, 4)
  Flatten              (128, 4, 4)       (2048,)
  Linear               (2048,)           (512,)
  Linear               (512,)            (10,)
```

---

## The Training Loop

Training a CNN involves repeatedly:
1. Loading a batch of images and labels
2. Passing images through the model (forward pass)
3. Calculating the loss (how wrong the predictions are)
4. Computing gradients (backward pass)
5. Updating the model weights

```python
import torch
import torch.nn as nn
import torch.optim as optim

def train_model(model, train_loader, test_loader, num_epochs=20,
                learning_rate=0.001, device='cpu'):
    """Train a CNN model and track performance."""

    # Loss function: CrossEntropyLoss for classification
    criterion = nn.CrossEntropyLoss()

    # Optimizer: Adam with learning rate
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # Learning rate scheduler: reduce LR when progress stalls
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)

    # Track metrics
    train_losses = []
    test_accuracies = []

    for epoch in range(num_epochs):
        # ============ TRAINING PHASE ============
        model.train()  # Enable dropout and batch norm training behavior
        running_loss = 0.0
        correct = 0
        total = 0

        for batch_idx, (images, labels) in enumerate(train_loader):
            # Move data to device (CPU or GPU)
            images = images.to(device)
            labels = labels.to(device)

            # Step 1: Zero the gradients from previous iteration
            optimizer.zero_grad()

            # Step 2: Forward pass - get predictions
            outputs = model(images)

            # Step 3: Calculate loss
            loss = criterion(outputs, labels)

            # Step 4: Backward pass - compute gradients
            loss.backward()

            # Step 5: Update weights
            optimizer.step()

            # Track metrics
            running_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

            # Print progress every 200 batches
            if (batch_idx + 1) % 200 == 0:
                print(f"  Epoch [{epoch+1}/{num_epochs}], "
                      f"Batch [{batch_idx+1}/{len(train_loader)}], "
                      f"Loss: {loss.item():.4f}")

        # Calculate epoch metrics
        epoch_loss = running_loss / len(train_loader)
        train_accuracy = 100 * correct / total
        train_losses.append(epoch_loss)

        # ============ EVALUATION PHASE ============
        model.eval()  # Disable dropout and use running stats for batch norm
        test_correct = 0
        test_total = 0

        with torch.no_grad():  # No need to track gradients during evaluation
            for images, labels in test_loader:
                images = images.to(device)
                labels = labels.to(device)
                outputs = model(images)
                _, predicted = torch.max(outputs, 1)
                test_total += labels.size(0)
                test_correct += (predicted == labels).sum().item()

        test_accuracy = 100 * test_correct / test_total
        test_accuracies.append(test_accuracy)

        # Step the learning rate scheduler
        scheduler.step()

        # Print epoch summary
        print(f"Epoch [{epoch+1}/{num_epochs}] - "
              f"Train Loss: {epoch_loss:.4f}, "
              f"Train Acc: {train_accuracy:.2f}%, "
              f"Test Acc: {test_accuracy:.2f}%")
        print("-" * 60)

    return train_losses, test_accuracies

# Train the model
print("Starting training...")
print("=" * 60)
train_losses, test_accuracies = train_model(
    model, train_loader, test_loader,
    num_epochs=20, learning_rate=0.001, device=device
)
```

**Output:**
```
Starting training...
============================================================
  Epoch [1/20], Batch [200/782], Loss: 1.5234
  Epoch [1/20], Batch [400/782], Loss: 1.3456
  Epoch [1/20], Batch [600/782], Loss: 1.2345
Epoch [1/20] - Train Loss: 1.4123, Train Acc: 48.52%, Test Acc: 56.78%
------------------------------------------------------------
  Epoch [2/20], Batch [200/782], Loss: 1.0234
  ...
Epoch [2/20] - Train Loss: 1.0567, Train Acc: 62.34%, Test Acc: 64.12%
------------------------------------------------------------
  ...
Epoch [20/20] - Train Loss: 0.2345, Train Acc: 91.67%, Test Acc: 82.15%
------------------------------------------------------------
```

(Note: Exact values will vary due to random initialization.)

**Line-by-line explanation:**

- `nn.CrossEntropyLoss()` is the standard loss function for multi-class classification. It combines softmax and negative log-likelihood loss. It expects raw logits (not probabilities).
- `optim.Adam(model.parameters(), lr=0.001)` creates the Adam optimizer. Adam adapts the learning rate for each parameter, which often works better than plain SGD.
- `optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)` reduces the learning rate by a factor of 10 every 10 epochs. This helps the model converge to a better solution.
- `model.train()` enables training-specific behaviors: dropout is active, batch norm uses batch statistics.
- `optimizer.zero_grad()` clears old gradients. Without this, gradients would accumulate from previous iterations.
- `outputs = model(images)` runs the forward pass: images go through all layers and produce class scores.
- `loss = criterion(outputs, labels)` computes how wrong the predictions are.
- `loss.backward()` computes gradients of the loss with respect to every model parameter.
- `optimizer.step()` updates the parameters using the computed gradients.
- `torch.max(outputs, 1)` returns the index of the highest score for each image, which is the predicted class.
- `model.eval()` and `torch.no_grad()` disable dropout and gradient tracking during evaluation for correct and efficient testing.

---

## Plotting Training Progress

Visualizing the training process helps you understand how your model is learning.

```python
import matplotlib.pyplot as plt

def plot_training(train_losses, test_accuracies):
    """Plot training loss and test accuracy."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    # Plot training loss
    ax1.plot(range(1, len(train_losses) + 1), train_losses, 'b-')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Training Loss')
    ax1.set_title('Training Loss Over Time')
    ax1.grid(True)

    # Plot test accuracy
    ax2.plot(range(1, len(test_accuracies) + 1), test_accuracies, 'r-')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Test Accuracy (%)')
    ax2.set_title('Test Accuracy Over Time')
    ax2.grid(True)

    plt.tight_layout()
    plt.savefig('training_progress.png', dpi=100)
    plt.show()

plot_training(train_losses, test_accuracies)
print("Training progress saved to training_progress.png")
```

**Output:**
```
Training progress saved to training_progress.png
```

```
What Good Training Curves Look Like:

  Loss (should decrease):        Accuracy (should increase):

  |*                             |              ************
  | *                            |         *****
  |  **                          |      ***
  |    ***                       |    **
  |       ****                   |  **
  |           ******             | *
  |                 ********     |*
  +-------------------------->   +-------------------------->
    Epochs                         Epochs

  Warning signs:
  - Loss goes UP = learning rate too high
  - Loss stays FLAT = learning rate too low or model too simple
  - Train accuracy high but test accuracy low = overfitting
```

---

## Evaluating the Model

Let us evaluate the model in more detail, including per-class accuracy.

```python
def evaluate_model(model, test_loader, classes, device='cpu'):
    """Evaluate model and show per-class accuracy."""
    model.eval()

    # Overall accuracy
    correct = 0
    total = 0

    # Per-class accuracy
    class_correct = [0] * len(classes)
    class_total = [0] * len(classes)

    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            labels = labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs, 1)

            total += labels.size(0)
            correct += (predicted == labels).sum().item()

            # Per-class tracking
            for i in range(labels.size(0)):
                label = labels[i].item()
                class_total[label] += 1
                if predicted[i] == labels[i]:
                    class_correct[label] += 1

    # Print overall accuracy
    overall_acc = 100 * correct / total
    print(f"Overall Test Accuracy: {overall_acc:.2f}%")
    print(f"Correct: {correct} / {total}")
    print()

    # Print per-class accuracy
    print("Per-Class Accuracy:")
    print("-" * 40)
    for i, cls in enumerate(classes):
        if class_total[i] > 0:
            acc = 100 * class_correct[i] / class_total[i]
            print(f"  {cls:>12}: {acc:5.1f}%  "
                  f"({class_correct[i]}/{class_total[i]})")
    print("-" * 40)

classes = ('airplane', 'automobile', 'bird', 'cat', 'deer',
           'dog', 'frog', 'horse', 'ship', 'truck')

evaluate_model(model, test_loader, classes, device)
```

**Output:**
```
Overall Test Accuracy: 82.15%
Correct: 8215 / 10000

Per-Class Accuracy:
----------------------------------------
      airplane:  85.3%  (853/1000)
    automobile:  91.2%  (912/1000)
          bird:  72.1%  (721/1000)
           cat:  64.5%  (645/1000)
          deer:  78.9%  (789/1000)
           dog:  73.4%  (734/1000)
          frog:  88.7%  (887/1000)
         horse:  86.3%  (863/1000)
          ship:  90.1%  (901/1000)
         truck:  90.0%  (900/1000)
----------------------------------------
```

(Note: Your exact numbers will differ.)

**Line-by-line explanation:**

- We track two things: overall accuracy (how many images were correctly classified out of all images) and per-class accuracy (how well the model does on each individual class).
- `class_correct` and `class_total` are lists that count correct predictions and total images for each class.
- Per-class accuracy reveals where the model struggles. Cats and dogs are harder to tell apart than ships and trucks, so they typically have lower accuracy.

---

## Visualizing Learned Filters

One of the fascinating things about CNNs is that you can actually see what the filters learned. The first layer's filters are easiest to interpret because they operate directly on the image pixels.

```python
import matplotlib.pyplot as plt
import numpy as np

def visualize_filters(model):
    """Visualize the learned filters from the first conv layer."""
    # Get the weights of the first convolution layer
    # Shape: (out_channels, in_channels, height, width) = (32, 3, 3, 3)
    first_conv = model.conv_block1[0]
    filters = first_conv.weight.data.cpu().clone()

    print(f"First conv layer filter shape: {filters.shape}")
    print(f"Number of filters: {filters.shape[0]}")

    # Normalize filters for display
    filters = filters - filters.min()
    filters = filters / filters.max()

    # Display first 16 filters
    fig, axes = plt.subplots(2, 8, figsize=(12, 3))
    for i in range(16):
        row = i // 8
        col = i % 8
        # Each filter has 3 channels (RGB), so we can display it as a color image
        filt = filters[i].permute(1, 2, 0).numpy()  # (3,3,3) -> (3,3,3)
        axes[row, col].imshow(filt)
        axes[row, col].set_title(f'Filter {i}', fontsize=8)
        axes[row, col].axis('off')

    plt.suptitle('Learned Filters (First Conv Layer)', fontsize=12)
    plt.tight_layout()
    plt.savefig('learned_filters.png', dpi=100)
    plt.show()

visualize_filters(model)
print("Filters saved to learned_filters.png")
```

**Output:**
```
First conv layer filter shape: torch.Size([32, 3, 3, 3])
Number of filters: 32
Filters saved to learned_filters.png
```

**Line-by-line explanation:**

- `model.conv_block1[0]` accesses the first Conv2d layer. The `[0]` index refers to the first layer in the Sequential block.
- `.weight.data` gets the raw weight tensor. For a Conv2d(3, 32, 3), this has shape (32, 3, 3, 3): 32 filters, each looking at 3 input channels, each 3x3 pixels.
- We normalize the filters to the range 0-1 for visualization purposes.
- Since the first layer takes RGB input, each filter can be displayed as a tiny 3x3 color image. You will typically see patterns resembling edge detectors at various angles and colors.

```
What Learned Filters Typically Look Like:

  First Layer Filters:
  +-----+  +-----+  +-----+  +-----+
  |  |  |  | --- |  | / / |  | \ \ |
  |  |  |  | --- |  | / / |  | \ \ |
  |  |  |  | --- |  | / / |  | \ \ |
  +-----+  +-----+  +-----+  +-----+
  Vertical  Horizontal Diagonal Diagonal
  edges     edges      /        \

  These are similar to the hand-designed filters from Chapter 11,
  but the network discovered them on its own through training!
```

---

## Saving and Loading the Model

After training, you should save your model so you do not have to retrain it every time.

```python
# Save the model
model_path = 'cifar10_cnn.pth'
torch.save({
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'train_losses': train_losses,
    'test_accuracies': test_accuracies,
}, model_path)
print(f"Model saved to {model_path}")

# Load the model (how you would do it later)
checkpoint = torch.load(model_path, map_location=device)

loaded_model = CIFAR10CNN(num_classes=10).to(device)
loaded_model.load_state_dict(checkpoint['model_state_dict'])
loaded_model.eval()

print("Model loaded successfully!")
```

**Output:**
```
Model saved to cifar10_cnn.pth
Model loaded successfully!
```

**Line-by-line explanation:**

- `model.state_dict()` returns a dictionary of all the model's parameters (weights and biases). This is the recommended way to save models in PyTorch.
- `torch.save({...}, model_path)` saves the parameters and training history to a file. We save the optimizer state too so we could resume training later.
- `torch.load(model_path, map_location=device)` loads the saved file. The `map_location` argument ensures the model loads to the correct device (CPU or GPU).
- `loaded_model.load_state_dict(...)` applies the saved parameters to a new model instance. The model architecture must match.

---

## Making Predictions on New Images

Let us use our trained model to make predictions.

```python
import torch
import matplotlib.pyplot as plt

def predict_images(model, test_loader, classes, device, num_images=8):
    """Show predictions on test images."""
    model.eval()

    # Get one batch of test images
    images, labels = next(iter(test_loader))
    images = images.to(device)

    # Get predictions
    with torch.no_grad():
        outputs = model(images)
        probabilities = torch.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probabilities, 1)

    # Display results
    fig, axes = plt.subplots(2, num_images // 2, figsize=(12, 6))
    axes = axes.flatten()

    for i in range(num_images):
        # Unnormalize image for display
        img = images[i].cpu()
        img = img * torch.tensor([0.2470, 0.2435, 0.2616]).view(3,1,1)
        img = img + torch.tensor([0.4914, 0.4822, 0.4465]).view(3,1,1)
        img = img.clamp(0, 1).permute(1, 2, 0).numpy()

        true_label = classes[labels[i]]
        pred_label = classes[predicted[i]]
        conf = confidence[i].item() * 100

        # Green title if correct, red if wrong
        color = 'green' if predicted[i] == labels[i] else 'red'

        axes[i].imshow(img)
        axes[i].set_title(f'Pred: {pred_label}\n({conf:.0f}%)\nTrue: {true_label}',
                          color=color, fontsize=9)
        axes[i].axis('off')

    plt.tight_layout()
    plt.savefig('predictions.png', dpi=100)
    plt.show()

predict_images(model, test_loader, classes, device)
print("Predictions saved to predictions.png")
```

**Output:**
```
Predictions saved to predictions.png
```

**Line-by-line explanation:**

- `torch.softmax(outputs, dim=1)` converts raw logits into probabilities that sum to 1. This tells us how confident the model is about each class.
- `torch.max(probabilities, 1)` returns both the highest probability (confidence) and the index of the highest probability (predicted class).
- We color the title green for correct predictions and red for incorrect ones, making it easy to spot mistakes at a glance.

---

## Complete Training Script

Here is the entire training pipeline in one clean script for reference.

```python
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader

# ==================== Configuration ====================
BATCH_SIZE = 64
NUM_EPOCHS = 20
LEARNING_RATE = 0.001
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# ==================== Data ====================
transform_train = transforms.Compose([
    transforms.RandomHorizontalFlip(),
    transforms.RandomCrop(32, padding=4),
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465),
                          (0.2470, 0.2435, 0.2616))
])

transform_test = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465),
                          (0.2470, 0.2435, 0.2616))
])

train_dataset = torchvision.datasets.CIFAR10(
    root='./data', train=True, download=True, transform=transform_train)
test_dataset = torchvision.datasets.CIFAR10(
    root='./data', train=False, download=True, transform=transform_test)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE,
                           shuffle=True, num_workers=2)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE,
                          shuffle=False, num_workers=2)

# ==================== Model ====================
model = CIFAR10CNN(num_classes=10).to(DEVICE)

# ==================== Training ====================
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)

for epoch in range(NUM_EPOCHS):
    model.train()
    running_loss = 0.0

    for images, labels in train_loader:
        images, labels = images.to(DEVICE), labels.to(DEVICE)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

    scheduler.step()

    # Evaluate
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            outputs = model(images)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    print(f"Epoch {epoch+1}/{NUM_EPOCHS} - "
          f"Loss: {running_loss/len(train_loader):.4f} - "
          f"Test Acc: {100*correct/total:.2f}%")

# Save the trained model
torch.save(model.state_dict(), 'cifar10_cnn_final.pth')
print("Training complete! Model saved.")
```

**Output:**
```
Epoch 1/20 - Loss: 1.4123 - Test Acc: 56.78%
Epoch 2/20 - Loss: 1.0567 - Test Acc: 64.12%
...
Epoch 20/20 - Loss: 0.2345 - Test Acc: 84.50%
Training complete! Model saved.
```

---

## Common Mistakes

1. **Wrong flatten size.** The most common error. If you change the input image size or the number of pooling layers, you must recalculate `128 * 4 * 4`. An easy way to debug: pass a dummy tensor through the convolution layers and print the shape before flattening.

2. **Forgetting model.train() and model.eval().** If you train without `model.train()`, dropout and batch norm will not work correctly. If you evaluate without `model.eval()`, results will be noisy and inconsistent.

3. **Not using torch.no_grad() during evaluation.** Without it, PyTorch still tracks gradients, wasting memory and computation. This can even cause out-of-memory errors on large datasets.

4. **Applying data augmentation to test data.** Augmentation (random flips, crops) should only be applied to training data. Test data should use deterministic transforms (just ToTensor and Normalize).

5. **Forgetting to move data to the same device as the model.** If the model is on GPU and the data is on CPU (or vice versa), you will get a runtime error. Always use `.to(device)` for both.

---

## Best Practices

1. **Start simple, then add complexity.** Begin with a basic CNN (2-3 conv layers) and see how it performs. Only add more layers, batch norm, or dropout if needed.

2. **Monitor both training and test accuracy.** If training accuracy is much higher than test accuracy, the model is overfitting. Add dropout, data augmentation, or reduce model size.

3. **Use a learning rate scheduler.** Reducing the learning rate during training often improves final accuracy. StepLR and CosineAnnealingLR are good choices.

4. **Save model checkpoints regularly.** Save the model after each epoch or when test accuracy improves. This way, you do not lose progress if training is interrupted.

5. **Use data augmentation for training.** Simple augmentations like random flips and crops can significantly improve test accuracy with no additional data needed. We will cover this in detail in Chapter 16.

---

## Quick Summary

Building a CNN in PyTorch involves loading data with torchvision, defining a model class that inherits from nn.Module, setting up a training loop with a loss function and optimizer, and evaluating on test data. The CIFAR-10 dataset provides a good starting point with 10 classes of 32x32 color images. Key PyTorch components include nn.Conv2d for convolution, nn.MaxPool2d for pooling, nn.Flatten to reshape, and nn.Linear for classification. The training loop follows five steps: zero gradients, forward pass, compute loss, backward pass, update weights. Visualizing filters and tracking metrics helps you understand what the model learns.

---

## Key Points

- torchvision.datasets provides standard datasets like CIFAR-10 with automatic downloading.
- transforms.Compose chains preprocessing steps: ToTensor converts images to tensors, Normalize standardizes values.
- DataLoader handles batching, shuffling, and parallel data loading.
- A CNN model class inherits from nn.Module and defines layers in __init__ and the forward pass in forward.
- The training loop: zero_grad, forward pass, loss, backward, optimizer step.
- Use model.train() for training and model.eval() with torch.no_grad() for evaluation.
- CrossEntropyLoss is the standard loss for multi-class classification.
- Adam optimizer adapts learning rates automatically and works well out of the box.
- Save models with torch.save(model.state_dict()) and load with model.load_state_dict().
- First-layer filters can be visualized to see what patterns the CNN learned.

---

## Practice Questions

1. Why do we need to call optimizer.zero_grad() before each training step? What would happen if we did not?

2. What is the purpose of transforms.Normalize? Why do we use specific mean and std values for CIFAR-10?

3. Explain the difference between model.train() and model.eval(). Which layers behave differently between these two modes?

4. Why do we use torch.no_grad() during evaluation? What would happen if we did not use it?

5. Our CNN has about 1.2 million parameters. Most of them are in the first fully connected layer. Why is this, and what could we do to reduce the parameter count?

---

## Exercises

### Exercise 1: Train on MNIST

Modify the CIFAR10CNN class to work with the MNIST dataset (grayscale, 28x28, 10 digit classes). Hints: change in_channels from 3 to 1, and adjust the flatten size since MNIST images are 28x28 instead of 32x32.

### Exercise 2: Experiment with Hyperparameters

Train the CIFAR-10 model with different settings and compare results:
- Learning rate: try 0.01, 0.001, 0.0001
- Batch size: try 32, 64, 128
- Number of filters: try starting with 16, 32, or 64 in the first block

Record the final test accuracy for each configuration.

### Exercise 3: Add More Convolution Layers

Add a fourth convolution block with 256 filters to the CNN. Calculate the new flatten size and adjust the linear layer accordingly. Does adding more layers improve accuracy? Does it slow down training?

---

## What Is Next?

You have just built and trained a CNN from scratch. In the next chapter, we will explore the famous CNN architectures that have shaped the field of deep learning: LeNet, AlexNet, VGG, ResNet, and EfficientNet. You will learn why each one was groundbreaking, how skip connections solved the problem of training very deep networks, and how to use these pretrained architectures in your own projects.
