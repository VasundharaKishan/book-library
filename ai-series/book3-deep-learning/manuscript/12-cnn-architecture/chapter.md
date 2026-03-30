# Chapter 12: CNN Architecture

## What You Will Learn

In this chapter, you will learn:

- How convolution layers extract features from images
- How pooling layers shrink the size while keeping important information
- The difference between MaxPool and AvgPool
- How the flatten operation converts 2D feature maps into a 1D vector
- How fully connected layers make final predictions
- How features become more abstract in deeper layers
- How all these components fit together in a complete CNN architecture

## Why This Chapter Matters

In the previous chapter, you learned how a single convolution operation detects patterns like edges. But a single filter is not enough to recognize a cat, a car, or a handwritten digit. Real-world image recognition requires combining many operations in a specific order.

A CNN architecture is like a recipe. Each ingredient (layer type) plays a specific role, and the order matters. Convolution layers find patterns. Pooling layers compress the information. Fully connected layers make decisions. Understanding this architecture is the foundation for building, debugging, and improving any image recognition system.

This chapter gives you the complete picture of how a CNN works from start to finish, from raw pixels to a final prediction.

---

## The Big Picture: How a CNN Works

Before diving into each layer type, let us see the overall flow. A CNN processes an image through a series of stages, like an assembly line in a factory.

```
Complete CNN Pipeline:

  Input Image     Conv + ReLU      Pool        Conv + ReLU      Pool
  (3, 224, 224)   (32, 222, 222)   (32,111,111) (64, 109, 109)  (64,54,54)
  +----------+    +----------+    +--------+    +----------+    +------+
  |          |    | Feature  |    | Shrunk |    | Deeper   |    |Shrunk|
  | Raw      |--->| Maps     |--->| Feature|--->| Feature  |--->|Feature|
  | Pixels   |    | (edges)  |    | Maps   |    | Maps     |    | Maps |
  +----------+    +----------+    +--------+    | (shapes) |    +------+
                                                +----------+       |
                                                                   |
      +------------------------------------------------------------+
      |
      v
  Flatten         Fully Connected    Output
  (64*54*54,)     (512,)             (10,)
  +----------+    +----------+       +--------+
  | Long     |    | Decision |       | Class  |
  | Vector   |--->| Making   |------>| Scores |
  | of       |    | Layer    |       | (prob) |
  | Numbers  |    +----------+       +--------+
  +----------+

  Stage 1: Extract features (Conv + Pool, repeated)
  Stage 2: Make decisions (Flatten + Fully Connected)
```

Think of it this way:

- **Stage 1 (Feature Extraction):** The CNN looks at the image and identifies patterns. Early layers find simple patterns like edges and colors. Deeper layers combine those into complex patterns like eyes, wheels, or letters.
- **Stage 2 (Classification):** The CNN takes all the patterns it found and decides what the image shows. "I see two eyes, a nose, whiskers, and pointy ears. This must be a cat."

---

## Convolution Layers: The Feature Extractors

You learned about convolution in Chapter 11. Now let us see how convolution layers work within a CNN.

### What a Convolution Layer Does

A convolution layer applies multiple filters to its input. Each filter produces one feature map. If a layer has 32 filters, it produces 32 feature maps.

```
One Convolution Layer with 3 Filters:

  Input Image          Filter 1        Feature Map 1 (edges)
  +----------+         +---+---+---+   +--------+
  |          |  -----> | . | . | . |   |  Edge  |
  |          |         +---+---+---+   | pattern|
  |          |                         +--------+
  |          |
  |          |         Filter 2        Feature Map 2 (corners)
  |          |  -----> +---+---+---+   +--------+
  |          |         | . | . | . |   | Corner |
  |          |         +---+---+---+   | pattern|
  |          |                         +--------+
  |          |
  |          |         Filter 3        Feature Map 3 (textures)
  |          |  -----> +---+---+---+   +--------+
  |          |         | . | . | . |   |Texture |
  +----------+         +---+---+---+   | pattern|
                                       +--------+

  3 filters = 3 feature maps stacked together
  Output shape: (3, H_out, W_out)
```

### Channels In and Channels Out

The first convolution layer takes an image with a certain number of input channels (1 for grayscale, 3 for RGB). Each subsequent layer takes the output of the previous layer as input, which has as many channels as the previous layer had filters.

```python
import torch
import torch.nn as nn

# First conv layer: takes RGB image (3 channels), produces 16 feature maps
conv1 = nn.Conv2d(in_channels=3, out_channels=16, kernel_size=3, padding=1)

# Second conv layer: takes 16 feature maps, produces 32 feature maps
conv2 = nn.Conv2d(in_channels=16, out_channels=32, kernel_size=3, padding=1)

# Create a sample RGB image: batch=1, channels=3, height=32, width=32
sample_image = torch.randn(1, 3, 32, 32)

# Pass through first conv layer
output1 = conv1(sample_image)
print("Input shape:", sample_image.shape)
print("After conv1:", output1.shape)

# Pass through second conv layer
output2 = conv2(output1)
print("After conv2:", output2.shape)
```

**Output:**
```
Input shape: torch.Size([1, 3, 32, 32])
After conv1: torch.Size([1, 16, 32, 32])
After conv2: torch.Size([1, 32, 32, 32])
```

**Line-by-line explanation:**

- `nn.Conv2d(in_channels=3, out_channels=16, kernel_size=3, padding=1)` creates a convolution layer. It takes input with 3 channels (RGB), applies 16 different 3x3 filters, and uses padding=1 to keep the spatial size the same.
- `in_channels=3` means the input has 3 channels. For the first layer, this matches the RGB channels. For later layers, it matches the number of feature maps from the previous layer.
- `out_channels=16` means we use 16 filters, so we get 16 feature maps out.
- `kernel_size=3` means each filter is 3x3 pixels.
- The input is `(1, 3, 32, 32)`: 1 image, 3 channels, 32 pixels tall, 32 pixels wide.
- After conv1, the output is `(1, 16, 32, 32)`: 1 image, 16 feature maps, same height and width (because of padding=1).
- After conv2, the output is `(1, 32, 32, 32)`: 1 image, 32 feature maps, same height and width.

### ReLU Activation After Convolution

After each convolution, we typically apply the ReLU (Rectified Linear Unit) activation function. ReLU replaces all negative values with zero and keeps positive values unchanged.

```
ReLU Function:

  Input:   [-3, 5, -1, 8, 0, -7, 2]
  Output:  [ 0, 5,  0, 8, 0,  0, 2]

  Rule: if value < 0, output = 0
        if value >= 0, output = value (unchanged)

  Think of ReLU as a gate that blocks negative signals
  and lets positive signals pass through.
```

Why do we need ReLU? Without it, stacking multiple convolution layers would be the same as having one single layer (because linear operations stack into one linear operation). ReLU introduces non-linearity, which lets the network learn complex patterns.

```python
import torch
import torch.nn as nn

# Feature map with some negative values
feature_map = torch.tensor([
    [-2.0,  3.0, -1.0],
    [ 5.0, -4.0,  2.0],
    [ 0.0,  7.0, -3.0]
])

relu = nn.ReLU()
activated = relu(feature_map)

print("Before ReLU:")
print(feature_map)
print("\nAfter ReLU:")
print(activated)
```

**Output:**
```
Before ReLU:
tensor([[-2.,  3., -1.],
        [ 5., -4.,  2.],
        [ 0.,  7., -3.]])

After ReLU:
tensor([[0., 3., 0.],
        [5., 0., 2.],
        [0., 7., 0.]])
```

**Line-by-line explanation:**

- `nn.ReLU()` creates the activation function. It does not have any learnable parameters.
- Every negative value (-2, -1, -4, -3) becomes 0. Every non-negative value stays the same.
- This is fast to compute and works very well in practice, which is why it is the most popular activation function in deep learning.

---

## Pooling Layers: Shrinking the Size

After extracting features with convolution, we use pooling layers to reduce the spatial dimensions (height and width) of the feature maps. This serves two purposes:

1. **Reduces computation:** Smaller feature maps mean fewer calculations in later layers.
2. **Provides translation invariance:** The network becomes less sensitive to the exact position of features. If a cat's ear moves a few pixels, the network still recognizes it.

### How Pooling Works

Pooling works similarly to convolution: a small window slides across the feature map. But instead of multiplying and adding, it simply picks the most important value from each window.

### MaxPool: Pick the Maximum

Max pooling takes the largest value in each window. This keeps the strongest feature response and discards weaker ones.

```
Max Pooling (2x2 window, stride 2):

  Input Feature Map (4x4):
  +----+----+----+----+
  |  1 |  3 |  2 |  8 |
  +----+----+----+----+
  |  5 |  2 |  7 |  1 |
  +----+----+----+----+
  |  4 |  6 |  3 |  9 |
  +----+----+----+----+
  |  0 |  8 |  5 |  2 |
  +----+----+----+----+

  Step 1: Top-left 2x2 block    Step 2: Top-right 2x2 block
  | 1 | 3 |  -> max = 5         | 2 | 8 |  -> max = 8
  | 5 | 2 |                     | 7 | 1 |

  Step 3: Bottom-left 2x2 block Step 4: Bottom-right 2x2 block
  | 4 | 6 |  -> max = 8         | 3 | 9 |  -> max = 9
  | 0 | 8 |                     | 5 | 2 |

  Output (2x2):
  +----+----+
  |  5 |  8 |
  +----+----+
  |  8 |  9 |
  +----+----+

  The 4x4 feature map is now 2x2 (halved in each dimension).
  Only the most important values survive.
```

```python
import torch
import torch.nn as nn

# Create a 4x4 feature map
# Shape: (batch, channels, height, width)
feature_map = torch.tensor([
    [1.0, 3.0, 2.0, 8.0],
    [5.0, 2.0, 7.0, 1.0],
    [4.0, 6.0, 3.0, 9.0],
    [0.0, 8.0, 5.0, 2.0]
]).unsqueeze(0).unsqueeze(0)

# MaxPool with 2x2 window
max_pool = nn.MaxPool2d(kernel_size=2, stride=2)
pooled = max_pool(feature_map)

print("Input shape:", feature_map.shape)
print("Input:")
print(feature_map.squeeze())

print("\nAfter MaxPool2d(2,2):")
print("Output shape:", pooled.shape)
print(pooled.squeeze())
```

**Output:**
```
Input shape: torch.Size([1, 1, 4, 4])
Input:
tensor([[1., 3., 2., 8.],
        [5., 2., 7., 1.],
        [4., 6., 3., 9.],
        [0., 8., 5., 2.]])

After MaxPool2d(2,2):
Output shape: torch.Size([1, 1, 2, 2])
tensor([[5., 8.],
        [8., 9.]])
```

**Line-by-line explanation:**

- `nn.MaxPool2d(kernel_size=2, stride=2)` creates a max pooling layer with a 2x2 window that moves 2 pixels at a time (no overlap).
- The 4x4 input becomes 2x2 output. Each value in the output is the maximum of the corresponding 2x2 block.
- `.squeeze()` removes the batch and channel dimensions for cleaner printing.

### AvgPool: Take the Average

Average pooling calculates the mean of all values in each window instead of taking the maximum.

```
Average Pooling (2x2 window, stride 2):

  Input Feature Map (4x4):
  +----+----+----+----+
  |  1 |  3 |  2 |  8 |
  +----+----+----+----+
  |  5 |  2 |  7 |  1 |
  +----+----+----+----+
  |  4 |  6 |  3 |  9 |
  +----+----+----+----+
  |  0 |  8 |  5 |  2 |
  +----+----+----+----+

  Top-left:     (1+3+5+2)/4 = 2.75
  Top-right:    (2+8+7+1)/4 = 4.50
  Bottom-left:  (4+6+0+8)/4 = 4.50
  Bottom-right: (3+9+5+2)/4 = 4.75

  Output (2x2):
  +------+------+
  | 2.75 | 4.50 |
  +------+------+
  | 4.50 | 4.75 |
  +------+------+
```

```python
import torch
import torch.nn as nn

# Same input feature map
feature_map = torch.tensor([
    [1.0, 3.0, 2.0, 8.0],
    [5.0, 2.0, 7.0, 1.0],
    [4.0, 6.0, 3.0, 9.0],
    [0.0, 8.0, 5.0, 2.0]
]).unsqueeze(0).unsqueeze(0)

# AvgPool with 2x2 window
avg_pool = nn.AvgPool2d(kernel_size=2, stride=2)
pooled_avg = avg_pool(feature_map)

# MaxPool for comparison
max_pool = nn.MaxPool2d(kernel_size=2, stride=2)
pooled_max = max_pool(feature_map)

print("Input:")
print(feature_map.squeeze())
print("\nMaxPool output:")
print(pooled_max.squeeze())
print("\nAvgPool output:")
print(pooled_avg.squeeze())
```

**Output:**
```
Input:
tensor([[1., 3., 2., 8.],
        [5., 2., 7., 1.],
        [4., 6., 3., 9.],
        [0., 8., 5., 2.]])

MaxPool output:
tensor([[5., 8.],
        [8., 9.]])

AvgPool output:
tensor([[2.7500, 4.5000],
        [4.5000, 4.7500]])
```

### MaxPool vs AvgPool: When to Use Which?

```
MaxPool vs AvgPool Comparison:

  +-------------------+---------------------------+---------------------------+
  |                   |        MaxPool             |        AvgPool            |
  +-------------------+---------------------------+---------------------------+
  | What it keeps     | Strongest activation       | Average of all values     |
  | Best for          | Object detection, edges    | Smooth features, textures |
  | Advantage         | Sharp, decisive features   | Preserves background info |
  | Used in           | Most CNN architectures     | Later layers, some models |
  | Most common?      | Yes (default choice)       | Less common               |
  +-------------------+---------------------------+---------------------------+

  Rule of thumb: Start with MaxPool. Use AvgPool if MaxPool loses
  too much information for your specific task.
```

---

## Flatten: From 2D to 1D

After the convolution and pooling layers have extracted features and compressed the spatial dimensions, we need to convert the 2D feature maps into a 1D vector. This is called **flattening**.

Think of it like reading a book: you take pages (2D grids of text) and read them into a single stream of words (1D sequence).

```
Flatten Operation:

  Before Flatten (2 feature maps, each 2x2):

  Feature Map 1:     Feature Map 2:
  +----+----+        +----+----+
  |  5 |  8 |        |  3 |  7 |
  +----+----+        +----+----+
  |  8 |  9 |        |  6 |  2 |
  +----+----+        +----+----+

  Shape: (2, 2, 2) = 2 channels, 2 height, 2 width

  After Flatten:

  [5, 8, 8, 9, 3, 7, 6, 2]

  Shape: (8,) = one long vector of 2 * 2 * 2 = 8 numbers

  All the spatial information is now in a single row.
```

```python
import torch
import torch.nn as nn

# Feature maps: 2 channels, 2x2 each
feature_maps = torch.tensor([
    [[5.0, 8.0],
     [8.0, 9.0]],
    [[3.0, 7.0],
     [6.0, 2.0]]
]).unsqueeze(0)  # Add batch dimension

print("Before flatten:")
print("Shape:", feature_maps.shape)
print(feature_maps)

# Flatten (keep batch dimension, flatten everything else)
flatten = nn.Flatten()
flat = flatten(feature_maps)

print("\nAfter flatten:")
print("Shape:", flat.shape)
print(flat)
```

**Output:**
```
Before flatten:
Shape: torch.Size([1, 2, 2, 2])
tensor([[[[5., 8.],
          [8., 9.]],

         [[3., 7.],
          [6., 2.]]]])

After flatten:
Shape: torch.Size([1, 8])
tensor([[5., 8., 8., 9., 3., 7., 6., 2.]])
```

**Line-by-line explanation:**

- `nn.Flatten()` creates a flatten layer. By default, it keeps the batch dimension (dimension 0) and flattens all other dimensions into one.
- The input has shape `(1, 2, 2, 2)`: 1 image, 2 channels, 2 height, 2 width.
- After flattening, the shape is `(1, 8)`: 1 image, 8 values. The value 8 comes from 2 channels times 2 height times 2 width.
- This flat vector can now be fed into a fully connected (linear) layer.

---

## Fully Connected Layers: Making Decisions

After flattening, the feature vector is passed to one or more **fully connected layers** (also called **dense layers** or **linear layers**). These layers connect every input to every output, just like the layers in a regular neural network.

The job of fully connected layers is to take the extracted features and make a final decision. "Based on all the patterns found in the image, this is most likely a cat."

```
Fully Connected Layer:

  Input (flattened features):  [5, 8, 8, 9, 3, 7, 6, 2]
                                |  |  |  |  |  |  |  |
                    +-----------+--+--+--+--+--+--+--+----------+
                    |           |  |  |  |  |  |  |  |          |
                    v           v  v  v  v  v  v  v  v          v
              +----------+ +----------+ +----------+ +----------+
              | Neuron 1 | | Neuron 2 | | Neuron 3 | | Neuron 4 |
              +----------+ +----------+ +----------+ +----------+
                    |           |           |           |
                    v           v           v           v
  Output:       [ 0.8,        0.1,        0.05,       0.05 ]
                  cat         dog         bird        fish

  Every input is connected to every output.
  Each connection has a learnable weight.
```

```python
import torch
import torch.nn as nn

# Simulating the end of a CNN pipeline
# After conv + pool + flatten, we have a vector of 512 features
flat_features = torch.randn(1, 512)  # 1 image, 512 features

# First fully connected layer: 512 inputs -> 128 outputs
fc1 = nn.Linear(in_features=512, out_features=128)

# Second fully connected layer: 128 inputs -> 10 outputs (10 classes)
fc2 = nn.Linear(in_features=128, out_features=10)

# Activation function
relu = nn.ReLU()

# Forward pass through fully connected layers
hidden = relu(fc1(flat_features))
output = fc2(hidden)

print("Input shape:", flat_features.shape)
print("After fc1 + ReLU:", hidden.shape)
print("Final output:", output.shape)
print("Output values (raw scores for 10 classes):")
print(output)
```

**Output:**
```
Input shape: torch.Size([1, 512])
After fc1 + ReLU: torch.Size([1, 128])
Final output: torch.Size([1, 10])
Output values (raw scores for 10 classes):
tensor([[ 0.1234, -0.5678,  0.9012, -0.3456,  0.7890,
         -0.1234,  0.5678, -0.9012,  0.3456, -0.7890]],
       grad_fn=<AddmmBackward0>)
```

(Note: Your exact output values will differ because the weights are initialized randomly.)

**Line-by-line explanation:**

- `nn.Linear(in_features=512, out_features=128)` creates a fully connected layer. It takes a vector of 512 numbers and produces a vector of 128 numbers. Internally, it has a 512x128 weight matrix and a bias vector of size 128.
- `fc2 = nn.Linear(128, 10)` maps 128 features to 10 output classes. If we are classifying images into 10 categories (like the digits 0-9), we need 10 outputs.
- We apply ReLU between fully connected layers for the same reason we apply it after convolution: to introduce non-linearity.
- The final output has 10 raw scores (called **logits**). The class with the highest score is the network's prediction. To convert these to probabilities, we would apply softmax.

---

## How Features Become More Abstract in Deeper Layers

One of the most fascinating aspects of CNNs is how each layer builds on the previous one to detect increasingly complex patterns.

```
Feature Hierarchy in a CNN:

  Layer 1 (Early):     Layer 2 (Middle):    Layer 3 (Deep):
  Simple Patterns      Combined Patterns    Complex Objects

  +--------+           +--------+           +--------+
  |  ---   | edges     | /\     | corners   | /\_/\  | cat ears
  |  |||   | lines     | |__|   | shapes    | (o o)  | cat face
  |  ///   | textures  |  ()    | curves    |  > <   | cat nose
  +--------+           +--------+           +--------+

  Edges combine       Shapes combine       Object parts combine
  to form shapes      to form object       to form complete
                      parts                objects

  Each layer uses the output of the previous layer as input.
  This is why deeper networks can recognize more complex things.
```

This is exactly how our own visual system works. Neurons in the early visual cortex detect edges and colors. Neurons in later areas combine those into shapes. And neurons in higher areas recognize complete objects and faces.

```python
import torch
import torch.nn as nn

# Demonstrate feature progression through layers
class FeatureDemo(nn.Module):
    def __init__(self):
        super().__init__()
        # Layer 1: 3 RGB channels -> 16 feature maps (edges, colors)
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, padding=1)

        # Layer 2: 16 -> 32 feature maps (shapes, corners)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)

        # Layer 3: 32 -> 64 feature maps (object parts)
        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, padding=1)

        # Layer 4: 64 -> 128 feature maps (complex objects)
        self.conv4 = nn.Conv2d(64, 128, kernel_size=3, padding=1)

        self.relu = nn.ReLU()
        self.pool = nn.MaxPool2d(2, 2)

    def forward(self, x):
        print(f"Input:           {x.shape}")

        x = self.pool(self.relu(self.conv1(x)))
        print(f"After conv1+pool: {x.shape}  (16 edge detectors)")

        x = self.pool(self.relu(self.conv2(x)))
        print(f"After conv2+pool: {x.shape}  (32 shape detectors)")

        x = self.pool(self.relu(self.conv3(x)))
        print(f"After conv3+pool: {x.shape}  (64 part detectors)")

        x = self.pool(self.relu(self.conv4(x)))
        print(f"After conv4+pool: {x.shape} (128 object detectors)")

        return x

model = FeatureDemo()
sample = torch.randn(1, 3, 64, 64)  # A 64x64 RGB image
output = model(sample)
```

**Output:**
```
Input:           torch.Size([1, 3, 64, 64])
After conv1+pool: torch.Size([1, 16, 32, 32])  (16 edge detectors)
After conv2+pool: torch.Size([1, 32, 16, 16])  (32 shape detectors)
After conv3+pool: torch.Size([1, 64, 8, 8])  (64 part detectors)
After conv4+pool: torch.Size([1, 128, 4, 4]) (128 object detectors)
```

**Line-by-line explanation:**

- The input image is 64x64 pixels with 3 color channels.
- After each Conv+ReLU+Pool block, two things change: the number of channels increases (more types of features are detected) and the spatial size decreases (pooling halves the dimensions).
- By the final layer, we have 128 feature maps, each only 4x4 pixels. These tiny, numerous feature maps encode high-level information about the image content.
- The spatial size shrank from 64x64 to 4x4, but the depth grew from 3 to 128. We traded spatial resolution for feature richness.

```
How Dimensions Change Through a CNN:

  Layer          Channels    Height    Width     Total Values
  -------        --------    ------    -----     ------------
  Input             3         64       64        12,288
  conv1+pool       16         32       32        16,384
  conv2+pool       32         16       16         8,192
  conv3+pool       64          8        8         4,096
  conv4+pool      128          4        4         2,048

  Notice: spatial size shrinks, channels grow.
  The network compresses spatial info into feature info.
```

---

## Complete CNN Architecture Diagram

Now let us put all the pieces together. Here is a complete CNN architecture for classifying images into 10 categories:

```
Complete CNN Architecture:

  INPUT (1, 28, 28) - Grayscale image, 28x28 pixels
    |
    v
  +--------------------------------------------------+
  | CONV BLOCK 1                                      |
  | Conv2d(1->16, 3x3, padding=1)  -> (16, 28, 28)   |
  | ReLU                            -> (16, 28, 28)   |
  | MaxPool2d(2x2)                  -> (16, 14, 14)   |
  +--------------------------------------------------+
    |
    v
  +--------------------------------------------------+
  | CONV BLOCK 2                                      |
  | Conv2d(16->32, 3x3, padding=1) -> (32, 14, 14)   |
  | ReLU                            -> (32, 14, 14)   |
  | MaxPool2d(2x2)                  -> (32,  7,  7)   |
  +--------------------------------------------------+
    |
    v
  +--------------------------------------------------+
  | FLATTEN                                           |
  | Reshape (32, 7, 7) -> (1568,)                     |
  | 32 * 7 * 7 = 1568 values in a single vector      |
  +--------------------------------------------------+
    |
    v
  +--------------------------------------------------+
  | FULLY CONNECTED BLOCK                             |
  | Linear(1568 -> 128)             -> (128,)         |
  | ReLU                             -> (128,)         |
  | Linear(128 -> 10)               -> (10,)          |
  +--------------------------------------------------+
    |
    v
  OUTPUT (10,) - Scores for each of the 10 classes
  [0.1, 0.05, 0.7, 0.02, 0.03, 0.01, 0.04, 0.02, 0.01, 0.02]
       Prediction: Class 2 (highest score = 0.7)
```

### Building the Complete Architecture in PyTorch

```python
import torch
import torch.nn as nn

class SimpleCNN(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()

        # Convolution block 1
        self.conv_block1 = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=16,
                      kernel_size=3, padding=1),    # (1,28,28) -> (16,28,28)
            nn.ReLU(),                               # Activation
            nn.MaxPool2d(kernel_size=2, stride=2)    # (16,28,28) -> (16,14,14)
        )

        # Convolution block 2
        self.conv_block2 = nn.Sequential(
            nn.Conv2d(in_channels=16, out_channels=32,
                      kernel_size=3, padding=1),    # (16,14,14) -> (32,14,14)
            nn.ReLU(),                               # Activation
            nn.MaxPool2d(kernel_size=2, stride=2)    # (32,14,14) -> (32,7,7)
        )

        # Flatten layer
        self.flatten = nn.Flatten()                  # (32,7,7) -> (1568,)

        # Fully connected layers
        self.fc_block = nn.Sequential(
            nn.Linear(32 * 7 * 7, 128),              # 1568 -> 128
            nn.ReLU(),                                # Activation
            nn.Linear(128, num_classes)               # 128 -> 10
        )

    def forward(self, x):
        x = self.conv_block1(x)
        x = self.conv_block2(x)
        x = self.flatten(x)
        x = self.fc_block(x)
        return x

# Create the model
model = SimpleCNN(num_classes=10)

# Test with a sample input (batch of 4 grayscale 28x28 images)
sample_batch = torch.randn(4, 1, 28, 28)
output = model(sample_batch)

print("Model architecture:")
print(model)
print(f"\nInput shape:  {sample_batch.shape}")
print(f"Output shape: {output.shape}")

# Count total parameters
total_params = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"\nTotal parameters: {total_params:,}")
print(f"Trainable parameters: {trainable_params:,}")
```

**Output:**
```
Model architecture:
SimpleCNN(
  (conv_block1): Sequential(
    (0): Conv2d(1, 16, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
    (1): ReLU()
    (2): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
  )
  (conv_block2): Sequential(
    (0): Conv2d(16, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
    (1): ReLU()
    (2): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
  )
  (flatten): Flatten(start_dim=1, end_dim=-1)
  (fc_block): Sequential(
    (0): Linear(in_features=1568, out_features=128, bias=True)
    (1): ReLU()
    (2): Linear(in_features=128, out_features=10, bias=True)
  )
)

Input shape:  torch.Size([4, 1, 28, 28])
Output shape: torch.Size([4, 10])

Total parameters: 205,898
Trainable parameters: 205,898
```

**Line-by-line explanation:**

- `class SimpleCNN(nn.Module)` defines our CNN as a PyTorch module. All neural network models in PyTorch inherit from `nn.Module`.
- `super().__init__()` initializes the parent class. This is required for PyTorch to properly track all layers and parameters.
- `nn.Sequential(...)` groups layers that are applied one after another. It is a convenient way to chain operations.
- `self.conv_block1` takes 1-channel input (grayscale), applies a 3x3 convolution to produce 16 feature maps, then ReLU, then max pooling to halve the dimensions.
- `self.conv_block2` takes the 16 feature maps, produces 32 feature maps, applies ReLU and max pooling again.
- `self.flatten` converts the 3D tensor (32 channels, 7 height, 7 width) into a 1D vector of 1568 values.
- `self.fc_block` has two linear layers. The first reduces 1568 features to 128, and the second maps 128 features to 10 class scores.
- The model has about 206,000 trainable parameters. Most of them are in the first fully connected layer (1568 * 128 = 200,704).

### Understanding Parameter Count

```
Where Do the Parameters Come From?

  Layer                    Parameters
  -----                    ----------
  Conv2d(1, 16, 3x3)      (1 * 3 * 3 + 1) * 16  =     160
                           (in * k * k + bias) * out

  Conv2d(16, 32, 3x3)     (16 * 3 * 3 + 1) * 32  =   4,640

  Linear(1568, 128)        1568 * 128 + 128       = 200,832

  Linear(128, 10)          128 * 10 + 10          =   1,290
                                                   ---------
  Total                                            = 206,922

  Notice: The fully connected layer has the most parameters!
  This is why modern architectures try to minimize FC layers.
```

---

## Batch Normalization: Helping the Network Learn

You will often see **Batch Normalization** (BatchNorm) in CNN architectures. It normalizes the values in each feature map to have a mean near 0 and a standard deviation near 1.

Think of it like keeping all the values on a similar scale. Without normalization, values in different feature maps can have wildly different ranges, making it harder for the network to learn.

```python
import torch
import torch.nn as nn

class CNNWithBatchNorm(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 16, 3, padding=1),
            nn.BatchNorm2d(16),    # Normalize the 16 feature maps
            nn.ReLU(),
            nn.MaxPool2d(2, 2),

            nn.Conv2d(16, 32, 3, padding=1),
            nn.BatchNorm2d(32),    # Normalize the 32 feature maps
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
        )

    def forward(self, x):
        return self.features(x)

model = CNNWithBatchNorm()
sample = torch.randn(8, 1, 28, 28)  # Batch of 8 images
output = model(sample)
print("Output shape:", output.shape)
```

**Output:**
```
Output shape: torch.Size([8, 32, 7, 7])
```

**Line-by-line explanation:**

- `nn.BatchNorm2d(16)` creates a batch normalization layer for 16 feature maps. The number must match the number of output channels from the preceding convolution layer.
- BatchNorm is placed between the convolution and the activation function (though some practitioners place it after ReLU). Both orderings work in practice.
- It helps the network train faster and more stably. Think of it as keeping the data "well-behaved" as it flows through the network.

---

## Dropout: Preventing Overfitting

**Dropout** randomly sets some neurons to zero during training. This forces the network to not rely too heavily on any single neuron, which helps prevent overfitting.

Think of dropout like a sports team practicing with random players sitting out. Each remaining player must learn to perform well regardless of who else is playing. This makes the whole team more robust.

```
Dropout in Action (rate = 0.5):

  Before Dropout:        After Dropout (training):
  [3.2, 1.7, 0.5,       [3.2, 0.0, 0.5,        <- 1.7 dropped
   4.1, 2.3, 0.8,        0.0, 2.3, 0.8,        <- 4.1 dropped
   1.5, 3.6, 2.1]        1.5, 0.0, 2.1]        <- 3.6 dropped

  About 50% of values become 0 (randomly chosen each time).
  During testing/inference, dropout is turned OFF.
```

```python
import torch
import torch.nn as nn

class CNNWithDropout(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 16, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(16, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(32 * 7 * 7, 128),
            nn.ReLU(),
            nn.Dropout(p=0.5),       # Drop 50% of neurons during training
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

model = CNNWithDropout()

# During training, dropout is active
model.train()
sample = torch.randn(1, 1, 28, 28)
train_output = model(sample)
print("Training mode output shape:", train_output.shape)

# During evaluation, dropout is disabled
model.eval()
eval_output = model(sample)
print("Eval mode output shape:", eval_output.shape)
```

**Output:**
```
Training mode output shape: torch.Size([1, 10])
Eval mode output shape: torch.Size([1, 10])
```

**Line-by-line explanation:**

- `nn.Dropout(p=0.5)` randomly zeroes 50% of the input values during training. The remaining values are scaled up by a factor of 2 to maintain the expected sum.
- `model.train()` puts the model in training mode, where dropout is active.
- `model.eval()` puts the model in evaluation mode, where dropout is disabled. All neurons are used, giving consistent predictions.
- Dropout is placed after the ReLU activation in the fully connected section, not in the convolution section (though you could use it there too with `nn.Dropout2d`).

---

## Common Mistakes

1. **Wrong input size for the first linear layer.** The most common CNN bug. After all the convolution and pooling layers, you need to calculate the exact size of the flattened feature maps. If your conv/pool layers change the spatial dimensions, the linear layer's input size must match.

2. **Forgetting to match in_channels to the previous layer's out_channels.** Each convolution layer's `in_channels` must equal the previous layer's `out_channels`. If conv1 outputs 16 channels, conv2 must take 16 channels as input.

3. **Not using model.eval() during testing.** If you forget to switch to eval mode, dropout and batch normalization will behave as if you are still training, giving worse and inconsistent results.

4. **Too many fully connected parameters.** If your feature maps are still large when you flatten, the first linear layer will have an enormous number of parameters. Use more pooling or larger strides to reduce spatial dimensions before flattening.

5. **Applying pooling too aggressively.** Each 2x2 pooling layer halves the dimensions. If your input image is small (like 28x28), you can only pool a few times before the feature maps become too small. A 28x28 image can be pooled twice (to 7x7) before things get tight.

---

## Best Practices

1. **Follow the pattern: Conv -> BatchNorm -> ReLU -> Pool.** This ordering is used in most successful architectures and provides stable training.

2. **Increase channels as spatial size decreases.** A common pattern is to double the number of channels each time you halve the spatial dimensions: 16 -> 32 -> 64 -> 128.

3. **Use 3x3 convolutions with padding=1.** This is the most common configuration. Two 3x3 convolutions cover the same receptive field as one 5x5 convolution but with fewer parameters.

4. **Add dropout before the final linear layers** to reduce overfitting. Values between 0.25 and 0.5 are common starting points.

5. **Print shapes during development.** When building a new CNN, add print statements in the forward method to track how the tensor shape changes through each layer. This helps you catch dimension mismatches early.

---

## Quick Summary

A CNN architecture consists of two main stages: feature extraction and classification. The feature extraction stage uses convolution layers (to detect patterns), ReLU activation (to introduce non-linearity), and pooling layers (to reduce spatial size). The classification stage uses flatten (to convert 2D maps to a 1D vector) and fully connected layers (to make predictions). MaxPool keeps the strongest activations while AvgPool keeps the average. As data flows through deeper layers, features become more abstract: edges combine into shapes, shapes into object parts, and parts into complete objects. Batch normalization stabilizes training, and dropout prevents overfitting.

---

## Key Points

- A CNN has two stages: feature extraction (Conv + Pool) and classification (Flatten + FC).
- Convolution layers detect patterns using learned filters. Each filter produces one feature map.
- ReLU activation introduces non-linearity, allowing the network to learn complex patterns.
- MaxPool keeps the maximum value in each window. AvgPool keeps the average. MaxPool is more common.
- Pooling reduces spatial dimensions (height and width) while keeping the most important information.
- Flatten converts 2D feature maps into a 1D vector for the fully connected layers.
- Fully connected layers combine all extracted features to make the final classification.
- Deeper layers detect more abstract and complex features.
- Batch normalization stabilizes training by normalizing feature map values.
- Dropout randomly disables neurons during training to prevent overfitting.

---

## Practice Questions

1. A CNN takes a 32x32 RGB image as input. The first conv layer has 16 filters of size 3x3 with padding=1, followed by MaxPool(2,2). What is the output shape?

2. Why do we use ReLU activation after convolution layers? What would happen if we did not use any activation function?

3. You have a CNN where the feature maps before flattening have shape (64, 4, 4). How many input features does the first fully connected layer need?

4. What is the difference between MaxPool and AvgPool? Give a scenario where you might prefer AvgPool over MaxPool.

5. Why does the number of channels typically increase while spatial dimensions decrease as we go deeper in a CNN?

---

## Exercises

### Exercise 1: Calculate Output Shapes

Given this sequence of layers and an input of shape (1, 3, 32, 32), calculate the output shape after each layer:
- Conv2d(3, 32, kernel_size=3, padding=1)
- ReLU()
- MaxPool2d(2, 2)
- Conv2d(32, 64, kernel_size=3, padding=1)
- ReLU()
- MaxPool2d(2, 2)
- Flatten()
- Linear(?, 256)
- Linear(256, 10)

What value should replace the `?` in the Linear layer?

### Exercise 2: Build a Deeper CNN

Modify the SimpleCNN class to add a third convolution block with 64 filters. Adjust the fully connected layer sizes accordingly. Test it with a 28x28 input and verify the output shape is still (batch_size, 10).

### Exercise 3: Compare MaxPool and AvgPool

Create a feature map with a mixture of high and low values. Apply both MaxPool2d and AvgPool2d with the same kernel size and stride. Compare the outputs and explain which one preserves more detail and which one is more selective.

---

## What Is Next?

You now understand the building blocks of a CNN and how they fit together. In the next chapter, we will get our hands dirty and build a complete CNN in PyTorch from scratch. You will load real image datasets, define a CNN class, write a training loop, evaluate accuracy, and even visualize what the filters have learned. Everything you learned in this chapter will come to life with working code.
