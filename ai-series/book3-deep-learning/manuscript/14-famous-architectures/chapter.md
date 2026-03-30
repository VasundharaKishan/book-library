# Chapter 14: Famous CNN Architectures

## What You Will Learn

In this chapter, you will learn:

- How LeNet pioneered convolutional neural networks in 1998
- How AlexNet triggered the deep learning revolution in 2012
- Why VGG proved that depth matters with simple 3x3 filters
- How ResNet's skip connections solved the problem of training very deep networks
- How EfficientNet scales CNNs smartly across width, depth, and resolution
- How to compare these architectures and choose the right one
- How to use pretrained models from torchvision.models

## Why This Chapter Matters

Building a CNN from scratch is valuable for learning, but in practice you rarely need to design an architecture from zero. Over the past three decades, brilliant researchers have designed and tested hundreds of architectures, and a handful of these have become legendary for their impact on the field.

Understanding these famous architectures is like studying the history of architecture before designing a building. You learn what works, what does not, and why. Each architecture in this chapter solved a specific problem and changed how the world thinks about deep learning.

More practically, these architectures are available as pretrained models in PyTorch. Knowing them lets you pick the right starting point for your own projects and understand why certain design choices are made.

---

## The Timeline of CNN Breakthroughs

```
Timeline of Major CNN Architectures:

  1998          2012          2014        2015          2019
   |             |             |           |             |
   v             v             v           v             v
  LeNet       AlexNet        VGG        ResNet      EfficientNet
   |             |             |           |             |
   |             |             |           |             |
  First CNN    Deep Learning  Depth      Skip         Smart
  that         revolution     with       connections   scaling
  worked       begins         simple     solve depth   across
  on real                     blocks     problem       dimensions
  problems

  Each architecture built on lessons from the previous ones.
```

---

## LeNet (1998): The Pioneer

LeNet was created by Yann LeCun and his team at Bell Labs. It was designed to read handwritten digits on bank checks. This was the first CNN that worked well enough to be deployed in a real-world application.

### Architecture

LeNet is small and simple by today's standards, but it introduced the fundamental CNN pattern that every modern architecture still follows.

```
LeNet-5 Architecture:

  Input: (1, 32, 32) - Grayscale image

  +--------------------------------------------------+
  | Conv2d(1, 6, 5)     -> (6, 28, 28)               |
  | Tanh activation                                   |
  | AvgPool2d(2, 2)     -> (6, 14, 14)               |
  +--------------------------------------------------+
                          |
  +--------------------------------------------------+
  | Conv2d(6, 16, 5)    -> (16, 10, 10)              |
  | Tanh activation                                   |
  | AvgPool2d(2, 2)     -> (16, 5, 5)                |
  +--------------------------------------------------+
                          |
  +--------------------------------------------------+
  | Flatten              -> (400,)                    |
  | Linear(400, 120)     -> (120,)                    |
  | Tanh activation                                   |
  | Linear(120, 84)      -> (84,)                     |
  | Tanh activation                                   |
  | Linear(84, 10)       -> (10,)  output classes     |
  +--------------------------------------------------+

  Total parameters: ~60,000
  That is tiny by modern standards!
```

### Key Features of LeNet

- **5x5 convolution filters:** Larger than today's typical 3x3 filters.
- **Tanh activation:** The sigmoid-like function used before ReLU was discovered to work better.
- **Average pooling:** Max pooling was not yet popular.
- **Two conv layers followed by three fully connected layers:** The basic Conv-Pool-FC pattern.

```python
import torch
import torch.nn as nn

class LeNet5(nn.Module):
    """The original LeNet-5 architecture (1998)."""

    def __init__(self, num_classes=10):
        super().__init__()

        self.features = nn.Sequential(
            # Layer 1: Conv + Tanh + Pool
            nn.Conv2d(1, 6, kernel_size=5),      # (1,32,32) -> (6,28,28)
            nn.Tanh(),
            nn.AvgPool2d(kernel_size=2, stride=2), # (6,28,28) -> (6,14,14)

            # Layer 2: Conv + Tanh + Pool
            nn.Conv2d(6, 16, kernel_size=5),     # (6,14,14) -> (16,10,10)
            nn.Tanh(),
            nn.AvgPool2d(kernel_size=2, stride=2), # (16,10,10) -> (16,5,5)
        )

        self.classifier = nn.Sequential(
            nn.Flatten(),                         # (16,5,5) -> (400,)
            nn.Linear(16 * 5 * 5, 120),
            nn.Tanh(),
            nn.Linear(120, 84),
            nn.Tanh(),
            nn.Linear(84, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

model = LeNet5()
sample = torch.randn(1, 1, 32, 32)
output = model(sample)
print(f"LeNet-5 output shape: {output.shape}")
total_params = sum(p.numel() for p in model.parameters())
print(f"Total parameters: {total_params:,}")
```

**Output:**
```
LeNet-5 output shape: torch.Size([1, 10])
Total parameters: 61,706
```

**Line-by-line explanation:**

- LeNet uses `nn.Tanh()` instead of `nn.ReLU()`. Tanh squishes values between -1 and 1. It worked, but ReLU was later found to train faster and avoid the "vanishing gradient" problem.
- `nn.AvgPool2d` takes the average of each 2x2 block. Modern networks prefer MaxPool.
- With only about 62,000 parameters, LeNet is tiny. A modern phone can run this model thousands of times per second.

### Why LeNet Matters

LeNet proved that CNNs could solve real problems. It was deployed in ATMs and mail sorting machines, reading millions of checks and zip codes. It established the Conv-Pool-FC pattern that every CNN still uses.

---

## AlexNet (2012): The Deep Learning Revolution

AlexNet was created by Alex Krizhevsky, Ilya Sutskevsky, and Geoffrey Hinton. It won the ImageNet Large Scale Visual Recognition Challenge (ILSVRC) in 2012 by a huge margin, reducing the error rate from 26% to 16%. This single result convinced the world that deep learning was the future of computer vision.

### What Made AlexNet Special

AlexNet introduced several ideas that are now standard:

```
AlexNet Innovations:

  1. ReLU activation      -> Much faster training than Tanh/Sigmoid
  2. Dropout              -> Prevented overfitting
  3. GPU training         -> Made deep networks practical
  4. Data augmentation    -> More training data without more images
  5. Deeper network       -> 8 layers (5 conv + 3 FC)
  6. Large scale          -> 60 million parameters
```

### Architecture

```
AlexNet Architecture:

  Input: (3, 227, 227) - Color image

  +--------------------------------------------------+
  | Conv2d(3, 96, 11, stride=4)  -> (96, 55, 55)     |
  | ReLU                                              |
  | MaxPool2d(3, stride=2)       -> (96, 27, 27)      |
  +--------------------------------------------------+
  | Conv2d(96, 256, 5, padding=2) -> (256, 27, 27)    |
  | ReLU                                              |
  | MaxPool2d(3, stride=2)       -> (256, 13, 13)     |
  +--------------------------------------------------+
  | Conv2d(256, 384, 3, padding=1) -> (384, 13, 13)   |
  | ReLU                                              |
  +--------------------------------------------------+
  | Conv2d(384, 384, 3, padding=1) -> (384, 13, 13)   |
  | ReLU                                              |
  +--------------------------------------------------+
  | Conv2d(384, 256, 3, padding=1) -> (256, 13, 13)   |
  | ReLU                                              |
  | MaxPool2d(3, stride=2)       -> (256, 6, 6)       |
  +--------------------------------------------------+
  | Flatten                       -> (9216,)           |
  | Linear(9216, 4096) + ReLU + Dropout                |
  | Linear(4096, 4096) + ReLU + Dropout                |
  | Linear(4096, 1000)   -> 1000 ImageNet classes      |
  +--------------------------------------------------+

  Total parameters: ~60 million
```

```python
import torch
import torch.nn as nn

class AlexNet(nn.Module):
    """Simplified AlexNet architecture (2012)."""

    def __init__(self, num_classes=1000):
        super().__init__()

        self.features = nn.Sequential(
            nn.Conv2d(3, 96, kernel_size=11, stride=4, padding=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),

            nn.Conv2d(96, 256, kernel_size=5, padding=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),

            nn.Conv2d(256, 384, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),

            nn.Conv2d(384, 384, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),

            nn.Conv2d(384, 256, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),
        )

        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(p=0.5),
            nn.Linear(256 * 6 * 6, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.5),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),
            nn.Linear(4096, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

model = AlexNet()
sample = torch.randn(1, 3, 227, 227)
output = model(sample)
print(f"AlexNet output shape: {output.shape}")
total_params = sum(p.numel() for p in model.parameters())
print(f"Total parameters: {total_params:,}")
```

**Output:**
```
AlexNet output shape: torch.Size([1, 1000])
Total parameters: 61,100,840
```

**Line-by-line explanation:**

- The first conv layer uses a large 11x11 kernel with stride 4 to quickly reduce the spatial dimensions. Modern networks avoid such large kernels.
- `ReLU(inplace=True)` modifies the tensor in place to save memory. This is a minor optimization.
- `Dropout(p=0.5)` drops 50% of neurons during training, which was crucial for preventing overfitting with 60 million parameters.
- The three fully connected layers have 4096 neurons each, containing the majority of the parameters.
- The output has 1000 units for the 1000 ImageNet classes.

---

## VGG (2014): Deep but Simple

VGG was created by the Visual Geometry Group at Oxford University. Its key insight was beautifully simple: **use only 3x3 convolution filters and just stack more of them.**

### The VGG Philosophy

Instead of using large filters (5x5, 7x7, 11x11), VGG showed that stacking multiple 3x3 filters achieves the same receptive field with fewer parameters.

```
Why 3x3 Filters Are Better:

  One 7x7 filter:
    Parameters: 7 * 7 = 49 per filter
    Receptive field: 7x7

  Three stacked 3x3 filters:
    Parameters: 3 * (3 * 3) = 27 per filter
    Receptive field: 7x7 (same!)

  Three 3x3 layers give the same receptive field as one 7x7 layer,
  but with:
  - 45% fewer parameters (27 vs 49)
  - Three ReLU activations instead of one (more non-linearity)
  - Better at learning complex patterns
```

### VGG-16 Architecture

The number 16 refers to the total number of layers with learnable parameters (13 conv layers plus 3 FC layers).

```
VGG-16 Architecture (simplified):

  Input: (3, 224, 224)

  Block 1: 2x Conv(64, 3x3)  + MaxPool  ->  (64, 112, 112)
  Block 2: 2x Conv(128, 3x3) + MaxPool  ->  (128, 56, 56)
  Block 3: 3x Conv(256, 3x3) + MaxPool  ->  (256, 28, 28)
  Block 4: 3x Conv(512, 3x3) + MaxPool  ->  (512, 14, 14)
  Block 5: 3x Conv(512, 3x3) + MaxPool  ->  (512, 7, 7)

  Flatten -> FC(4096) -> FC(4096) -> FC(1000)

  Total parameters: ~138 million

  Pattern: Double the channels after each pooling:
           64 -> 128 -> 256 -> 512 -> 512
```

```python
import torch
import torch.nn as nn

def make_vgg_block(in_channels, out_channels, num_convs):
    """Create a VGG block with multiple conv layers."""
    layers = []
    for i in range(num_convs):
        if i == 0:
            layers.append(nn.Conv2d(in_channels, out_channels, 3, padding=1))
        else:
            layers.append(nn.Conv2d(out_channels, out_channels, 3, padding=1))
        layers.append(nn.ReLU(inplace=True))
    layers.append(nn.MaxPool2d(kernel_size=2, stride=2))
    return nn.Sequential(*layers)

class VGG16(nn.Module):
    """VGG-16 architecture (2014)."""

    def __init__(self, num_classes=1000):
        super().__init__()

        self.features = nn.Sequential(
            make_vgg_block(3, 64, 2),     # Block 1: 2 conv layers
            make_vgg_block(64, 128, 2),   # Block 2: 2 conv layers
            make_vgg_block(128, 256, 3),  # Block 3: 3 conv layers
            make_vgg_block(256, 512, 3),  # Block 4: 3 conv layers
            make_vgg_block(512, 512, 3),  # Block 5: 3 conv layers
        )

        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(512 * 7 * 7, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(4096, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

model = VGG16()
sample = torch.randn(1, 3, 224, 224)
output = model(sample)
print(f"VGG-16 output shape: {output.shape}")
total_params = sum(p.numel() for p in model.parameters())
print(f"Total parameters: {total_params:,}")
```

**Output:**
```
VGG-16 output shape: torch.Size([1, 1000])
Total parameters: 138,357,544
```

**Line-by-line explanation:**

- `make_vgg_block` is a helper function that creates a VGG-style block: several 3x3 conv layers followed by max pooling. This shows how modular design makes complex networks manageable.
- Each block follows the same pattern: 2 or 3 convolution layers (each followed by ReLU), then a max pool layer.
- The channel count doubles after each block: 64, 128, 256, 512, 512. This is a design pattern you see in many architectures.
- VGG-16 has 138 million parameters, mostly in the fully connected layers. This made it slow and memory-hungry, motivating future architectures to be more efficient.

---

## ResNet (2015): The Skip Connection Breakthrough

ResNet (Residual Network) was created by Kaiming He and his team at Microsoft Research. It solved the biggest problem in deep learning at the time: **networks stopped learning when they got too deep.**

### The Degradation Problem

Before ResNet, researchers noticed a strange phenomenon. Making a network deeper (adding more layers) should theoretically make it at least as good as the shallower version. But in practice, very deep networks performed worse than shallower ones.

```
The Degradation Problem:

  Accuracy
      |
      |   *
      |  * *
      | *   *     <- 20-layer network peaks here
      |*     *
      |       *
      |  +     *
      | + +     *  <- 56-layer network is WORSE
      |+   +     *
      |     +
      +------------------------->
           Training epochs

  More layers should help, but they make things WORSE.
  This is NOT overfitting (training accuracy is worse too).
  The deeper network simply cannot learn as well.
```

### The Skip Connection (Residual Connection)

ResNet's solution was elegant: add a shortcut that lets the input bypass one or more layers.

```
Regular Block vs Residual Block:

  Regular Block:                 Residual Block:
  +----------+                   +----------+
  |  Input   |                   |  Input   |----+
  +----------+                   +----------+    |
       |                              |          |
  +----------+                   +----------+    |
  | Conv+ReLU|                   | Conv+ReLU|    |  (skip
  +----------+                   +----------+    |  connection)
       |                              |          |
  +----------+                   +----------+    |
  | Conv     |                   | Conv     |    |
  +----------+                   +----------+    |
       |                              |          |
  +----------+                   +----+-----+    |
  |   ReLU   |                   |   ADD    |<---+
  +----------+                   +----------+
       |                              |
  +----------+                   +----------+
  |  Output  |                   |   ReLU   |
  +----------+                   +----------+
                                      |
                                 +----------+
                                 |  Output  |
                                 +----------+

  In the residual block, the output = F(x) + x
  where F(x) is what the conv layers learned and x is the original input.
  This is called a "skip connection" or "shortcut connection."
```

### Why Skip Connections Work

Think of it this way. Without skip connections, each layer must learn the complete transformation from input to desired output. With skip connections, each layer only needs to learn the **difference** (the residual) between the input and the desired output.

```
Intuition Behind Skip Connections:

  Without skip connection:
    Layer must learn: Output = ComplexFunction(Input)
    This is hard when the function is nearly identity.

  With skip connection:
    Layer must learn: Output = Input + SmallAdjustment(Input)
    If the layer has nothing useful to add, SmallAdjustment = 0,
    and the output equals the input (no harm done).

  It is much easier to learn "what to add" than "the whole thing."

  Analogy: Instead of painting a picture from scratch,
  you start with a photocopy and just paint the corrections.
```

### ResNet Architecture

```
ResNet-18 Architecture:

  Input: (3, 224, 224)

  +-----------------------------------------------+
  | Initial: Conv(7x7, stride 2) + MaxPool        |
  |          -> (64, 56, 56)                       |
  +-----------------------------------------------+
       |
  +-----------------------------------------------+
  | Block 1: 2 Residual blocks, 64 filters         |
  |          -> (64, 56, 56)                       |
  +-----------------------------------------------+
       |
  +-----------------------------------------------+
  | Block 2: 2 Residual blocks, 128 filters        |
  |          -> (128, 28, 28)  (stride 2 at start) |
  +-----------------------------------------------+
       |
  +-----------------------------------------------+
  | Block 3: 2 Residual blocks, 256 filters        |
  |          -> (256, 14, 14)  (stride 2 at start) |
  +-----------------------------------------------+
       |
  +-----------------------------------------------+
  | Block 4: 2 Residual blocks, 512 filters        |
  |          -> (512, 7, 7)   (stride 2 at start)  |
  +-----------------------------------------------+
       |
  +-----------------------------------------------+
  | AdaptiveAvgPool -> (512, 1, 1)                 |
  | Flatten -> (512,)                              |
  | Linear(512, 1000)                              |
  +-----------------------------------------------+

  Total parameters: ~11.7 million (much less than VGG!)
```

```python
import torch
import torch.nn as nn

class ResidualBlock(nn.Module):
    """A single residual block with skip connection."""

    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()

        # Main path: two conv layers
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3,
                                stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, 3,
                                stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)

        # Skip connection: if dimensions change, adjust with 1x1 conv
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, 1,
                          stride=stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )

    def forward(self, x):
        # Save input for skip connection
        identity = x

        # Main path
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))

        # Add skip connection
        out = out + self.shortcut(identity)

        # Final activation
        out = self.relu(out)
        return out

class ResNet18(nn.Module):
    """Simplified ResNet-18 architecture."""

    def __init__(self, num_classes=1000):
        super().__init__()

        # Initial convolution
        self.initial = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        )

        # Residual blocks
        self.layer1 = nn.Sequential(
            ResidualBlock(64, 64),
            ResidualBlock(64, 64)
        )
        self.layer2 = nn.Sequential(
            ResidualBlock(64, 128, stride=2),
            ResidualBlock(128, 128)
        )
        self.layer3 = nn.Sequential(
            ResidualBlock(128, 256, stride=2),
            ResidualBlock(256, 256)
        )
        self.layer4 = nn.Sequential(
            ResidualBlock(256, 512, stride=2),
            ResidualBlock(512, 512)
        )

        # Classification head
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512, num_classes)

    def forward(self, x):
        x = self.initial(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        return x

model = ResNet18()
sample = torch.randn(1, 3, 224, 224)
output = model(sample)
print(f"ResNet-18 output shape: {output.shape}")
total_params = sum(p.numel() for p in model.parameters())
print(f"Total parameters: {total_params:,}")
```

**Output:**
```
ResNet-18 output shape: torch.Size([1, 1000])
Total parameters: 11,689,512
```

**Line-by-line explanation:**

- `ResidualBlock` is the core building block. It has two convolution layers with batch normalization and a skip connection that adds the input to the output.
- `self.shortcut` handles the case where the input and output dimensions differ. A 1x1 convolution adjusts the channel count and spatial size to match.
- `out = out + self.shortcut(identity)` is the skip connection. The output of the convolutions is added to the (possibly adjusted) input.
- `nn.AdaptiveAvgPool2d((1, 1))` reduces any spatial size to 1x1 by averaging all values. This replaces the flatten + large FC layer approach of VGG.
- ResNet-18 has only 11.7 million parameters, compared to VGG-16's 138 million, yet it performs better.

---

## EfficientNet (2019): Scaling Smartly

EfficientNet was created by Mingxing Tan and Quoc Le at Google. It introduced a principled way to scale CNNs by balancing three dimensions: depth (number of layers), width (number of channels), and resolution (input image size).

### The Scaling Problem

Before EfficientNet, researchers would scale up networks in one dimension at a time. Need better accuracy? Add more layers. Or use more channels. Or use bigger images. EfficientNet showed that scaling all three dimensions together, in the right proportions, is much more efficient.

```
Three Dimensions of Scaling:

  Width Scaling:          Depth Scaling:        Resolution Scaling:
  (more channels)         (more layers)         (bigger images)

  +----+  +--------+     +--+    +--+          +--+    +------+
  | 64 |  |  128   |     |  |    |  |          |  |    |      |
  | ch |  |  ch    |     |  |    |  |          |  |    |      |
  +----+  +--------+     |  |    |  |          +--+    |      |
                          |  |    |  |        128x128  |      |
  Narrow   Wide           +--+    |  |                 +------+
                         4 layers |  |                 256x256
                                  |  |
                                  +--+
                                 8 layers

  EfficientNet: Scale all three together with a compound coefficient.

  If you want 2x more computation:
    - Depth:      increase by alpha^phi
    - Width:      increase by beta^phi
    - Resolution: increase by gamma^phi

  where alpha * beta^2 * gamma^2 ≈ 2
```

### EfficientNet Family

EfficientNet comes in sizes from B0 (smallest) to B7 (largest). Each size scales up all three dimensions proportionally.

```
EfficientNet Family:

  +----------+----------+--------+--------+----------+-----------+
  | Model    | Params   | Top-1  | Input  | Depth    | Width     |
  |          | (M)      | Acc(%) | Size   | coeff    | coeff     |
  +----------+----------+--------+--------+----------+-----------+
  | B0       |   5.3    | 77.1   | 224    |  1.0     |  1.0      |
  | B1       |   7.8    | 79.1   | 240    |  1.1     |  1.0      |
  | B2       |   9.2    | 80.1   | 260    |  1.1     |  1.1      |
  | B3       |  12.0    | 81.6   | 300    |  1.2     |  1.1      |
  | B4       |  19.0    | 82.9   | 380    |  1.4     |  1.2      |
  | B5       |  30.0    | 83.6   | 456    |  1.6     |  1.4      |
  | B6       |  43.0    | 84.0   | 528    |  1.8     |  1.6      |
  | B7       |  66.0    | 84.3   | 600    |  2.0     |  1.8      |
  +----------+----------+--------+--------+----------+-----------+

  More parameters = higher accuracy, but also slower.
  Choose based on your compute budget.
```

---

## Comparison of All Architectures

```
Architecture Comparison Table:

  +----------------+------+--------+--------+--------+--------------------+
  | Architecture   | Year | Params | Layers | Top-1  | Key Innovation     |
  |                |      | (M)    |        | Acc(%) |                    |
  +----------------+------+--------+--------+--------+--------------------+
  | LeNet-5        | 1998 |  0.06  |   7    |  N/A   | First practical CNN|
  | AlexNet        | 2012 | 61     |   8    | 63.3   | ReLU, GPU, Dropout |
  | VGG-16         | 2014 | 138    |  16    | 74.4   | 3x3 filters only  |
  | ResNet-50      | 2015 | 25.6   |  50    | 76.1   | Skip connections   |
  | ResNet-152     | 2015 | 60.2   | 152    | 78.3   | Very deep networks |
  | EfficientNet-B0| 2019 |  5.3   |   -    | 77.1   | Compound scaling   |
  | EfficientNet-B7| 2019 | 66     |   -    | 84.3   | Compound scaling   |
  +----------------+------+--------+--------+--------+--------------------+

  Note: Top-1 accuracy is on the ImageNet validation set.
  Accuracy numbers are approximate and may vary by implementation.
```

```
Which Architecture Should You Use?

  +---------------------------+---------------------------+
  | Situation                 | Recommendation            |
  +---------------------------+---------------------------+
  | Learning / prototyping    | ResNet-18 or ResNet-34    |
  | Best accuracy, any cost   | EfficientNet-B7           |
  | Good accuracy, limited    | EfficientNet-B0 or B1     |
  |   compute                 |                           |
  | Mobile / edge devices     | EfficientNet-B0,          |
  |                           | MobileNet                 |
  | Transfer learning         | ResNet-50 or              |
  |                           | EfficientNet-B0           |
  +---------------------------+---------------------------+
```

---

## Using Pretrained Models from torchvision.models

You do not need to implement these architectures yourself. PyTorch provides them ready to use, with weights pretrained on ImageNet.

```python
import torch
import torchvision.models as models

# Load pretrained ResNet-18
resnet18 = models.resnet18(weights='IMAGENET1K_V1')
print("ResNet-18 loaded with ImageNet weights")

# Load pretrained VGG-16
vgg16 = models.vgg16(weights='IMAGENET1K_V1')
print("VGG-16 loaded with ImageNet weights")

# Load pretrained EfficientNet-B0
efficientnet = models.efficientnet_b0(weights='IMAGENET1K_V1')
print("EfficientNet-B0 loaded with ImageNet weights")

# Compare parameter counts
for name, model in [('ResNet-18', resnet18),
                     ('VGG-16', vgg16),
                     ('EfficientNet-B0', efficientnet)]:
    params = sum(p.numel() for p in model.parameters())
    print(f"{name:20s}: {params:>12,} parameters")
```

**Output:**
```
ResNet-18 loaded with ImageNet weights
VGG-16 loaded with ImageNet weights
EfficientNet-B0 loaded with ImageNet weights
ResNet-18           :   11,689,512 parameters
VGG-16              :  138,357,544 parameters
EfficientNet-B0     :    5,288,548 parameters
```

**Line-by-line explanation:**

- `models.resnet18(weights='IMAGENET1K_V1')` loads ResNet-18 with weights trained on ImageNet (1.2 million images, 1000 classes). The `'IMAGENET1K_V1'` string specifies which pretrained weights to use.
- These pretrained models can classify images into 1000 categories right out of the box.
- In the next chapter, you will learn how to adapt these pretrained models for your own custom classification tasks using transfer learning.

### Making Predictions with a Pretrained Model

```python
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image

# Load pretrained ResNet-18
model = models.resnet18(weights='IMAGENET1K_V1')
model.eval()

# Preprocessing pipeline for ImageNet models
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])

# Load and preprocess an image
# (In practice, replace with your own image path)
# img = Image.open('your_image.jpg')
# input_tensor = preprocess(img).unsqueeze(0)

# Simulate with random data for demonstration
input_tensor = torch.randn(1, 3, 224, 224)

# Get prediction
with torch.no_grad():
    output = model(input_tensor)
    probabilities = torch.softmax(output, dim=1)
    top5_prob, top5_idx = torch.topk(probabilities, 5)

print("Top 5 predictions:")
for i in range(5):
    print(f"  Class {top5_idx[0][i].item():4d}: "
          f"{top5_prob[0][i].item()*100:.2f}%")
```

**Output:**
```
Top 5 predictions:
  Class  234: 1.23%
  Class  567: 0.98%
  Class  123: 0.87%
  Class  890: 0.76%
  Class  345: 0.65%
```

(Note: With random input, the predictions are meaningless. With a real image, the model would give high confidence for the correct class.)

**Line-by-line explanation:**

- The preprocessing pipeline resizes the image, center-crops to 224x224, converts to tensor, and normalizes with ImageNet statistics.
- `torch.softmax(output, dim=1)` converts raw scores to probabilities.
- `torch.topk(probabilities, 5)` returns the 5 highest probabilities and their indices.
- The class indices correspond to ImageNet categories. You can look them up to get human-readable names.

---

## Common Mistakes

1. **Using the wrong input size.** Each architecture expects a specific input size: LeNet needs 32x32, AlexNet needs 227x227, and VGG/ResNet/EfficientNet typically need 224x224. Using the wrong size will cause shape mismatch errors.

2. **Forgetting model.eval() for pretrained models.** Batch normalization and dropout behave differently during training and evaluation. Always call model.eval() before inference.

3. **Using the wrong normalization values.** ImageNet pretrained models expect specific mean and std values: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]. Using different values will give poor results.

4. **Trying to train VGG from scratch without enough GPU memory.** VGG-16 has 138 million parameters and requires significant GPU memory. Use pretrained weights or choose a smaller architecture.

5. **Not understanding that deeper is not always better without skip connections.** Adding more layers to a plain CNN (without residual connections) can actually decrease performance due to the degradation problem.

---

## Best Practices

1. **Start with a pretrained model** rather than training from scratch. Transfer learning (covered in the next chapter) almost always gives better results with less data and less training time.

2. **Use ResNet as your default architecture.** ResNet variants (18, 34, 50, 101) offer a great balance of performance and simplicity. ResNet-18 is great for learning, ResNet-50 for production.

3. **Choose model size based on your compute budget.** If you have limited GPU memory, use EfficientNet-B0 or ResNet-18. If you have powerful hardware, try EfficientNet-B4 or ResNet-101.

4. **Always use batch normalization** in your own architectures. It stabilizes training and allows you to use higher learning rates.

5. **Add skip connections** when building deep networks. Even in custom architectures, residual connections help gradients flow and enable deeper networks.

---

## Quick Summary

CNN architectures have evolved dramatically from LeNet's 60,000 parameters in 1998 to EfficientNet's sophisticated scaling in 2019. LeNet proved CNNs work, AlexNet proved they scale with GPUs, VGG proved that simple 3x3 filters are best, ResNet proved that skip connections enable very deep networks, and EfficientNet proved that balanced scaling across depth, width, and resolution is optimal. All of these architectures are available as pretrained models in PyTorch's torchvision.models, ready to be used for transfer learning.

---

## Key Points

- LeNet (1998) was the first practical CNN, using 5x5 filters and tanh activation for digit recognition.
- AlexNet (2012) started the deep learning revolution with ReLU, dropout, and GPU training.
- VGG (2014) showed that stacking 3x3 filters is more effective than using larger filters.
- ResNet (2015) solved the degradation problem with skip connections, enabling networks with 100+ layers.
- Skip connections let layers learn residual adjustments (what to add) instead of complete transformations.
- EfficientNet (2019) introduced compound scaling to balance depth, width, and resolution together.
- Pretrained models are available in torchvision.models with ImageNet weights.
- ResNet is the best default choice for most projects due to its balance of performance and simplicity.

---

## Practice Questions

1. Why did AlexNet's victory in the 2012 ImageNet competition have such a big impact on the field of AI?

2. Explain why two stacked 3x3 convolution layers cover the same receptive field as one 5x5 layer, but with fewer parameters. Calculate the exact number of parameters for each case (ignoring bias and assuming single-channel input and output).

3. What is the degradation problem that ResNet solved? Why is this different from overfitting?

4. How does a skip connection (residual connection) work? Why does adding the input back to the output make training easier?

5. EfficientNet scales three dimensions: depth, width, and resolution. If you could only scale one dimension, which would you choose and why?

---

## Exercises

### Exercise 1: Build a Mini-ResNet

Create a small ResNet with only 4 residual blocks (instead of 18 layers) that works on CIFAR-10 (32x32 images). Use blocks with 16, 32, 64, and 64 channels. Train it and compare the accuracy to the plain CNN from Chapter 13.

### Exercise 2: Compare Pretrained Models

Load three pretrained models from torchvision (ResNet-18, VGG-16, and EfficientNet-B0). For each model:
- Print the total number of parameters
- Measure the time it takes to process a batch of 32 images
- Compare accuracy on a sample dataset

Which model gives the best trade-off between speed and accuracy?

### Exercise 3: Visualize Skip Connections

Create two versions of a small network (one with skip connections, one without) with 10 layers. Train both on CIFAR-10 for 20 epochs and plot the training loss curves. Does the network with skip connections train better?

---

## What Is Next?

Now that you know the famous architectures, you are ready to use them in practice. In the next chapter, you will learn transfer learning, which lets you take a model trained on millions of images (like ImageNet) and adapt it for your own custom task with much less data. This is the most practical and powerful technique in modern computer vision.
