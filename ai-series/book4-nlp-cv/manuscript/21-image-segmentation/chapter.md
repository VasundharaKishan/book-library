# Chapter 21: Image Segmentation

## What You Will Learn

In this chapter, you will learn:

- What image segmentation means and why it is different from classification
- The difference between semantic segmentation and instance segmentation
- How pixel-level classification works
- What the U-Net architecture is and why it is so popular
- How to use pre-trained segmentation models from torchvision
- How to visualize segmentation masks with colors
- Real-world applications of image segmentation

## Why This Chapter Matters

In earlier chapters, you learned how to classify entire images ("this is a cat") and how to detect objects with bounding boxes ("there is a cat at this location"). But what if you need to know the exact shape of the cat, down to every single pixel?

That is what image segmentation does. Instead of drawing a rectangle around an object, segmentation labels every pixel in the image. A self-driving car does not just need to know "there is a pedestrian somewhere in this image." It needs to know exactly which pixels belong to the road, which pixels belong to pedestrians, and which pixels belong to traffic signs. A doctor reviewing a medical scan needs to see exactly which pixels show a tumor, not just a rough bounding box.

Image segmentation is one of the most powerful techniques in computer vision, and it is used everywhere: from medical imaging to satellite analysis to photo editing tools that let you remove backgrounds with one click.

---

## What Is Image Segmentation?

Image segmentation is the task of assigning a label to every pixel in an image. Think of it like coloring a coloring book: every tiny area gets filled with a specific color based on what it belongs to.

```
Image Classification:   "This image contains a cat"         -> ONE label for the WHOLE image
Object Detection:       "There is a cat at [x, y, w, h]"    -> ONE box per object
Image Segmentation:     "Pixel (0,0) = background,           -> ONE label per PIXEL
                         Pixel (0,1) = background,
                         Pixel (1,5) = cat,
                         Pixel (1,6) = cat, ..."
```

### A Simple Analogy

Imagine you have a photograph of a park scene with people, trees, and dogs:

- **Classification** is like saying "this photo was taken at a park"
- **Detection** is like drawing rectangles around each person, tree, and dog
- **Segmentation** is like carefully tracing the exact outline of every person, tree, and dog with a different colored marker

---

## Semantic Segmentation vs Instance Segmentation

There are two main types of image segmentation, and understanding the difference is important.

### Semantic Segmentation

Semantic segmentation assigns a class label to every pixel, but it does not distinguish between different objects of the same class.

```
Example: A street scene with three cars

Semantic Segmentation Result:
+--------------------------------------------------+
|  sky sky sky sky sky sky sky sky sky sky sky sky   |
|  sky sky sky sky sky sky sky sky sky sky sky sky   |
|  bld bld sky sky sky sky sky sky sky bld bld bld  |
|  bld bld bld sky sky sky sky sky bld bld bld bld |
|  bld bld bld bld sky sky sky bld bld bld bld bld |
|  car car car road road road car car road car car  |
|  car car car road road road car car road car car  |
|  road road road road road road road road road rd  |
+--------------------------------------------------+

bld = building, car = car, road = road

Notice: ALL car pixels have the same label "car".
We cannot tell which pixels belong to car #1 vs car #2 vs car #3.
```

The word "semantic" means "related to meaning." Semantic segmentation understands the meaning (class) of each pixel but does not separate individual objects.

### Instance Segmentation

Instance segmentation goes one step further. It assigns a class label AND a unique identity to every pixel. This means you can tell apart car number 1, car number 2, and car number 3.

```
Instance Segmentation Result:
+--------------------------------------------------+
|  bg  bg  bg  bg  bg  bg  bg  bg  bg  bg  bg  bg  |
|  bg  bg  bg  bg  bg  bg  bg  bg  bg  bg  bg  bg  |
|  b1  b1  bg  bg  bg  bg  bg  bg  bg  b2  b2  b2  |
|  b1  b1  b1  bg  bg  bg  bg  bg  b2  b2  b2  b2  |
|  b1  b1  b1  b1  bg  bg  bg  b2  b2  b2  b2  b2  |
|  c1  c1  c1  rd  rd  rd  c2  c2  rd  c3  c3  rd  |
|  c1  c1  c1  rd  rd  rd  c2  c2  rd  c3  c3  rd  |
|  rd  rd  rd  rd  rd  rd  rd  rd  rd  rd  rd  rd   |
+--------------------------------------------------+

c1 = car #1, c2 = car #2, c3 = car #3
b1 = building #1, b2 = building #2
bg = background, rd = road

Now we can distinguish individual objects!
```

### When to Use Which

```
+----------------------+------------------+---------------------+
| Task                 | Semantic         | Instance            |
+----------------------+------------------+---------------------+
| Road surface         | Yes (one class)  | Not needed          |
| Count people         | Cannot count     | Yes (each separate) |
| Medical tumor area   | Yes (tumor/not)  | Not needed          |
| Track specific cars  | Cannot track     | Yes (each has ID)   |
| Background removal   | Yes              | Yes                 |
+----------------------+------------------+---------------------+
```

---

## How Pixel-Level Classification Works

At its core, segmentation is classification applied to every pixel. Instead of one prediction for the whole image, the model makes a prediction for each pixel.

### The Input and Output

For a regular classifier:
- Input: an image of shape (3, 224, 224) — 3 color channels, 224 height, 224 width
- Output: a vector of shape (num_classes,) — one probability per class

For a segmentation model:
- Input: an image of shape (3, H, W)
- Output: a tensor of shape (num_classes, H, W) — one probability per class, for every pixel

```
Input Image: (3, 256, 256)
         |
    [Segmentation Model]
         |
Output: (num_classes, 256, 256)

For each pixel at position (row, col):
  output[:, row, col] = [prob_background, prob_cat, prob_dog, ...]

The class with highest probability becomes that pixel's label.
```

### The Segmentation Mask

The final output is called a segmentation mask. It is a 2D image where each pixel value represents a class number instead of a color.

```python
import numpy as np

# Example: a tiny 4x4 segmentation mask
# 0 = background, 1 = cat, 2 = dog
mask = np.array([
    [0, 0, 0, 0],
    [0, 1, 1, 0],
    [0, 1, 1, 0],
    [0, 0, 2, 2]
])

print("Segmentation mask:")
print(mask)
print()
print("Pixel (1,1) is class:", mask[1, 1], "-> cat")
print("Pixel (3,2) is class:", mask[3, 2], "-> dog")
print("Pixel (0,0) is class:", mask[0, 0], "-> background")
```

**Output:**
```
Segmentation mask:
[[0 0 0 0]
 [0 1 1 0]
 [0 1 1 0]
 [0 0 2 2]]

Pixel (1,1) is class: 1 -> cat
Pixel (3,2) is class: 2 -> dog
Pixel (0,0) is class: 0 -> background
```

**Line-by-line explanation:**

- `mask = np.array([...])` creates a 4-by-4 grid where each value is a class label.
- Value 0 means that pixel belongs to the background.
- Value 1 means that pixel belongs to a cat.
- Value 2 means that pixel belongs to a dog.
- We can look up any pixel's class by indexing into the mask with `mask[row, col]`.

---

## The U-Net Architecture

U-Net is one of the most important segmentation architectures ever created. It was originally designed for medical image segmentation in 2015 and is still widely used today.

### Why Is It Called U-Net?

The architecture looks like the letter "U" when you draw it as a diagram. It has two main parts:

1. **Encoder (left side of the U):** This path goes downward. It shrinks the image and captures "what" is in the image (features).
2. **Decoder (right side of the U):** This path goes upward. It expands the features back to the original image size to produce a pixel-level prediction.
3. **Skip Connections (horizontal bridges):** These connect the encoder to the decoder at each level, passing fine details that would otherwise be lost.

```
U-Net Architecture (Simplified):

Input Image (256x256)                    Output Mask (256x256)
       |                                        ^
       v                                        |
  [Conv Block] 64 filters  ---- SKIP ----> [Conv Block] 64 filters
       |          (256x256)   CONNECTION      ^    (256x256)
       v                                      |
  [MaxPool] Shrink to 128x128           [UpConv] Expand to 256x256
       |                                      ^
       v                                      |
  [Conv Block] 128 filters ---- SKIP ----> [Conv Block] 128 filters
       |          (128x128)   CONNECTION      ^    (128x128)
       v                                      |
  [MaxPool] Shrink to 64x64             [UpConv] Expand to 128x128
       |                                      ^
       v                                      |
  [Conv Block] 256 filters ---- SKIP ----> [Conv Block] 256 filters
       |          (64x64)     CONNECTION      ^    (64x64)
       v                                      |
  [MaxPool] Shrink to 32x32             [UpConv] Expand to 64x64
       |                                      ^
       v                                      |
  [Conv Block] 512 filters ---- SKIP ----> [Conv Block] 512 filters
       |          (32x32)     CONNECTION      ^    (32x32)
       v                                      |
  [MaxPool] Shrink to 16x16             [UpConv] Expand to 32x32
       |                                      ^
       v                                      |
       +-----> [Conv Block] 1024 filters -----+
                   (16x16)
                 "Bottleneck"
                 (Bottom of the U)
```

### Why Skip Connections Matter

When the encoder shrinks the image, it captures high-level features (like "this area contains a dog") but loses fine details (like exact edges). The skip connections copy the detailed information from the encoder directly to the decoder, so the final output has both:

- **What** each region is (from the encoder)
- **Where** the exact boundaries are (from the skip connections)

```
Think of it like giving driving directions:

Without skip connections:
  "Turn right somewhere around the big mall area"
  (You know the general area but lost the precise details)

With skip connections:
  "Turn right at 123 Main Street, the red building on the corner"
  (You have both the general area AND the precise location)
```

### A Simple U-Net in PyTorch

Here is a simplified U-Net implementation to help you understand the structure:

```python
import torch
import torch.nn as nn

class SimpleUNet(nn.Module):
    """A simplified U-Net for understanding the architecture."""

    def __init__(self, in_channels=3, num_classes=2):
        super(SimpleUNet, self).__init__()

        # ---- Encoder (Downsampling Path) ----
        # Each block: two convolutions + ReLU
        self.enc1 = self.conv_block(in_channels, 64)
        self.enc2 = self.conv_block(64, 128)
        self.enc3 = self.conv_block(128, 256)

        # Max pooling to shrink spatial dimensions by half
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)

        # ---- Bottleneck ----
        self.bottleneck = self.conv_block(256, 512)

        # ---- Decoder (Upsampling Path) ----
        # Transpose convolution doubles spatial dimensions
        self.up3 = nn.ConvTranspose2d(512, 256, kernel_size=2, stride=2)
        self.dec3 = self.conv_block(512, 256)  # 512 because of skip connection

        self.up2 = nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2)
        self.dec2 = self.conv_block(256, 128)  # 256 because of skip connection

        self.up1 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2)
        self.dec1 = self.conv_block(128, 64)   # 128 because of skip connection

        # ---- Final 1x1 Convolution ----
        # Converts 64 feature channels to num_classes
        self.final = nn.Conv2d(64, num_classes, kernel_size=1)

    def conv_block(self, in_ch, out_ch):
        """Two convolution layers with ReLU activation."""
        return nn.Sequential(
            nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, kernel_size=3, padding=1),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        # Encoder
        e1 = self.enc1(x)          # Shape: (B, 64, H, W)
        e2 = self.enc2(self.pool(e1))  # Shape: (B, 128, H/2, W/2)
        e3 = self.enc3(self.pool(e2))  # Shape: (B, 256, H/4, W/4)

        # Bottleneck
        b = self.bottleneck(self.pool(e3))  # Shape: (B, 512, H/8, W/8)

        # Decoder with skip connections
        d3 = self.up3(b)                    # Shape: (B, 256, H/4, W/4)
        d3 = torch.cat([d3, e3], dim=1)     # Concatenate skip: (B, 512, H/4, W/4)
        d3 = self.dec3(d3)                  # Shape: (B, 256, H/4, W/4)

        d2 = self.up2(d3)                   # Shape: (B, 128, H/2, W/2)
        d2 = torch.cat([d2, e2], dim=1)     # Concatenate skip: (B, 256, H/2, W/2)
        d2 = self.dec2(d2)                  # Shape: (B, 128, H/2, W/2)

        d1 = self.up1(d2)                   # Shape: (B, 64, H, W)
        d1 = torch.cat([d1, e1], dim=1)     # Concatenate skip: (B, 128, H, W)
        d1 = self.dec1(d1)                  # Shape: (B, 64, H, W)

        # Final classification layer
        out = self.final(d1)                # Shape: (B, num_classes, H, W)
        return out

# Test the model
model = SimpleUNet(in_channels=3, num_classes=5)
dummy_input = torch.randn(1, 3, 128, 128)  # Batch of 1, RGB, 128x128
output = model(dummy_input)

print("Input shape: ", dummy_input.shape)
print("Output shape:", output.shape)
print("Number of classes:", output.shape[1])
```

**Output:**
```
Input shape:  torch.Size([1, 3, 128, 128])
Output shape: torch.Size([1, 5, 128, 128])
Number of classes: 5
```

**Line-by-line explanation:**

- `self.enc1, enc2, enc3` are encoder blocks. Each contains two convolution layers with ReLU activation. They extract features at different scales.
- `self.pool = nn.MaxPool2d(kernel_size=2, stride=2)` halves the height and width, making the feature maps smaller.
- `self.bottleneck` is the bottom of the U. It processes the most compressed representation.
- `self.up3, up2, up1` are transpose convolutions (also called deconvolutions). They double the spatial dimensions, making the feature maps larger again.
- `torch.cat([d3, e3], dim=1)` concatenates the upsampled features with the encoder features along the channel dimension. This is the skip connection.
- `self.final` is a 1x1 convolution that converts 64 feature channels into the number of output classes.
- The output has the same height and width as the input, with one channel per class.

---

## Using Pre-Trained Segmentation Models

Training a segmentation model from scratch requires large datasets and significant computing power. Fortunately, PyTorch provides pre-trained models through the `torchvision` library.

### DeepLabV3 with ResNet Backbone

DeepLabV3 is a powerful segmentation model. The torchvision version is trained on the COCO dataset and can segment 21 different classes including person, car, dog, cat, and more.

```python
import torch
import torchvision
from torchvision import transforms
from PIL import Image
import numpy as np

# Load a pre-trained DeepLabV3 model
# The model comes with weights trained on COCO dataset
model = torchvision.models.segmentation.deeplabv3_resnet101(
    weights='DeepLabV3_ResNet101_Weights.DEFAULT'
)
model.eval()  # Set to evaluation mode (no training)

print("Model loaded successfully!")
print("Number of output classes: 21")
print()

# The 21 COCO classes this model can segment
classes = [
    'background', 'aeroplane', 'bicycle', 'bird', 'boat',
    'bottle', 'bus', 'car', 'cat', 'chair',
    'cow', 'diningtable', 'dog', 'horse', 'motorbike',
    'person', 'pottedplant', 'sheep', 'sofa', 'train',
    'tvmonitor'
]

for i, name in enumerate(classes):
    print(f"  Class {i:2d}: {name}")
```

**Output:**
```
Model loaded successfully!
Number of output classes: 21

  Class  0: background
  Class  1: aeroplane
  Class  2: bicycle
  Class  3: bird
  Class  4: boat
  Class  5: bottle
  Class  6: bus
  Class  7: car
  Class  8: cat
  Class  9: chair
  Class 10: cow
  Class 11: diningtable
  Class 12: dog
  Class 13: horse
  Class 14: motorbike
  Class 15: person
  Class 16: pottedplant
  Class 17: sheep
  Class 18: sofa
  Class 19: train
  Class 20: tvmonitor
```

**Line-by-line explanation:**

- `torchvision.models.segmentation.deeplabv3_resnet101(...)` loads the DeepLabV3 model with a ResNet-101 backbone. The backbone is the encoder part that extracts features.
- `weights='DeepLabV3_ResNet101_Weights.DEFAULT'` loads the best available pre-trained weights.
- `model.eval()` switches the model from training mode to evaluation mode. This disables dropout and uses stored batch normalization statistics.
- The model can identify 21 object categories. Class 0 is always "background" (everything that is not one of the 20 specific categories).

### Running Segmentation on an Image

```python
import torch
import torchvision
from torchvision import transforms
from PIL import Image
import numpy as np

# Load the pre-trained model
model = torchvision.models.segmentation.deeplabv3_resnet101(
    weights='DeepLabV3_ResNet101_Weights.DEFAULT'
)
model.eval()

# Define the image preprocessing pipeline
# The model expects images normalized with ImageNet statistics
preprocess = transforms.Compose([
    transforms.Resize(520),                 # Resize shortest side to 520
    transforms.CenterCrop(480),             # Crop to 480x480
    transforms.ToTensor(),                  # Convert to tensor (0-1 range)
    transforms.Normalize(                   # Normalize with ImageNet stats
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# Create a sample image (in practice, load a real image)
# image = Image.open("street_scene.jpg").convert("RGB")
# For demonstration, create a random image
sample_image = Image.fromarray(
    np.random.randint(0, 255, (400, 600, 3), dtype=np.uint8)
)

# Preprocess the image
input_tensor = preprocess(sample_image)
input_batch = input_tensor.unsqueeze(0)  # Add batch dimension

print("Input tensor shape:", input_batch.shape)

# Run inference (no gradient calculation needed)
with torch.no_grad():
    output = model(input_batch)

# The model returns a dictionary
# 'out' contains the segmentation logits
output_logits = output['out']
print("Output logits shape:", output_logits.shape)

# Get the predicted class for each pixel
# argmax along the class dimension (dim=1) gives the most likely class
predictions = torch.argmax(output_logits, dim=1)
print("Predictions shape:", predictions.shape)

# Convert to numpy for further processing
mask = predictions.squeeze(0).numpy()
print("Mask shape:", mask.shape)
print("Unique classes found:", np.unique(mask))
```

**Output:**
```
Input tensor shape: torch.Size([1, 3, 480, 480])
Output logits shape: torch.Size([1, 21, 480, 480])
Predictions shape: torch.Size([1, 480, 480])
Mask shape: (480, 480)
Unique classes found: [0]
```

**Line-by-line explanation:**

- `transforms.Compose([...])` chains multiple image transformations together. Each one runs in order.
- `transforms.Resize(520)` resizes the image so its shortest side is 520 pixels.
- `transforms.CenterCrop(480)` crops the center 480-by-480 region. This ensures a consistent input size.
- `transforms.ToTensor()` converts the PIL image to a PyTorch tensor and scales pixel values from 0-255 to 0.0-1.0.
- `transforms.Normalize(mean, std)` normalizes the image using the ImageNet dataset statistics. This is required because the model was trained with this normalization.
- `input_tensor.unsqueeze(0)` adds a batch dimension. The model expects input shape (batch, channels, height, width).
- `with torch.no_grad()` tells PyTorch not to track gradients, which saves memory during inference.
- `output['out']` extracts the segmentation logits. The shape is (1, 21, 480, 480) meaning 21 class scores for each of the 480x480 pixels.
- `torch.argmax(output_logits, dim=1)` finds which class has the highest score for each pixel. This produces the final segmentation mask.

---

## Visualizing Segmentation Masks

A segmentation mask is just numbers. To make it human-readable, we assign a unique color to each class.

### Creating a Color Map

```python
import numpy as np
import matplotlib.pyplot as plt

def create_color_map(num_classes):
    """
    Create a color map where each class gets a unique color.
    Uses a simple algorithm to generate visually distinct colors.
    """
    colors = np.zeros((num_classes, 3), dtype=np.uint8)

    for i in range(num_classes):
        r, g, b = 0, 0, 0
        class_id = i
        for j in range(8):
            r = r | ((class_id >> 0) & 1) << (7 - j)
            g = g | ((class_id >> 1) & 1) << (7 - j)
            b = b | ((class_id >> 2) & 1) << (7 - j)
            class_id = class_id >> 3
        colors[i] = [r, g, b]

    return colors

def colorize_mask(mask, num_classes=21):
    """
    Convert a segmentation mask (2D array of class IDs)
    into an RGB image where each class has a unique color.
    """
    colors = create_color_map(num_classes)
    h, w = mask.shape
    color_mask = np.zeros((h, w, 3), dtype=np.uint8)

    for class_id in range(num_classes):
        # Find all pixels belonging to this class
        class_pixels = (mask == class_id)
        # Assign the class color to those pixels
        color_mask[class_pixels] = colors[class_id]

    return color_mask

# Example: create a small mask and colorize it
example_mask = np.array([
    [0, 0, 0, 0, 0, 15, 15, 15],
    [0, 0, 0, 0, 15, 15, 15, 15],
    [0, 8, 8, 0, 15, 15, 15, 0],
    [0, 8, 8, 0, 0, 15, 0, 0],
    [0, 8, 8, 8, 0, 0, 0, 0],
    [0, 0, 8, 0, 0, 12, 12, 0],
    [0, 0, 0, 0, 12, 12, 12, 0],
    [0, 0, 0, 0, 12, 12, 0, 0],
])

# Class 0 = background, 8 = cat, 12 = dog, 15 = person

print("Original mask (class IDs):")
print(example_mask)
print()

colored = colorize_mask(example_mask)
print("Colored mask shape:", colored.shape)
print("Color for background (class 0):", colored[0, 0])
print("Color for cat (class 8):       ", colored[2, 1])
print("Color for person (class 15):   ", colored[0, 5])

# To display with matplotlib:
# fig, axes = plt.subplots(1, 2, figsize=(12, 5))
# axes[0].imshow(original_image)
# axes[0].set_title("Original Image")
# axes[1].imshow(colored)
# axes[1].set_title("Segmentation Mask")
# plt.show()
```

**Output:**
```
Original mask (class IDs):
[[ 0  0  0  0  0 15 15 15]
 [ 0  0  0  0 15 15 15 15]
 [ 0  8  8  0 15 15 15  0]
 [ 0  8  8  0  0 15  0  0]
 [ 0  8  8  8  0  0  0  0]
 [ 0  0  8  0  0 12 12  0]
 [ 0  0  0  0 12 12 12  0]
 [ 0  0  0  0 12 12  0  0]]

Colored mask shape: (8, 8, 3)
Color for background (class 0): [0 0 0]
Color for cat (class 8):        [  0   0 128]
Color for person (class 15):    [128 128 128]
```

**Line-by-line explanation:**

- `create_color_map(num_classes)` generates a unique RGB color for each class using a bit-shifting algorithm. This ensures visually distinct colors.
- `colorize_mask(mask)` takes a 2D mask of class IDs and returns a 3D RGB image.
- `class_pixels = (mask == class_id)` creates a boolean array that is True wherever the mask equals the current class ID.
- `color_mask[class_pixels] = colors[class_id]` sets all pixels of that class to the corresponding color.
- The result is an image you can display using matplotlib, where each object class appears in a different color.

### Overlaying the Mask on the Original Image

Often, you want to see the segmentation mask on top of the original image:

```python
import numpy as np

def overlay_mask(image, mask, num_classes=21, alpha=0.5):
    """
    Overlay a colored segmentation mask on the original image.

    Parameters:
        image: numpy array of shape (H, W, 3), the original image
        mask: numpy array of shape (H, W), class IDs per pixel
        num_classes: total number of classes
        alpha: transparency (0 = only image, 1 = only mask)

    Returns:
        blended: numpy array of shape (H, W, 3)
    """
    # Create colored mask
    colored_mask = colorize_mask(mask, num_classes)

    # Blend: overlay = image * (1 - alpha) + mask * alpha
    # Only overlay where mask is not background (class 0)
    blended = image.copy()
    non_background = mask > 0

    blended[non_background] = (
        image[non_background] * (1 - alpha) +
        colored_mask[non_background] * alpha
    ).astype(np.uint8)

    return blended

# Example usage:
# original = np.array(Image.open("photo.jpg"))
# blended = overlay_mask(original, mask, alpha=0.5)
# plt.imshow(blended)
# plt.show()

print("overlay_mask function defined successfully!")
print("Use it to blend segmentation results with original images.")
print("alpha=0.5 means 50% image + 50% mask color")
```

**Output:**
```
overlay_mask function defined successfully!
Use it to blend segmentation results with original images.
alpha=0.5 means 50% image + 50% mask color
```

---

## Complete Segmentation Pipeline

Let us put everything together into a complete, reusable pipeline:

```python
import torch
import torchvision
from torchvision import transforms
from PIL import Image
import numpy as np

class ImageSegmenter:
    """A complete image segmentation pipeline using DeepLabV3."""

    # COCO class names
    CLASSES = [
        'background', 'aeroplane', 'bicycle', 'bird', 'boat',
        'bottle', 'bus', 'car', 'cat', 'chair',
        'cow', 'diningtable', 'dog', 'horse', 'motorbike',
        'person', 'pottedplant', 'sheep', 'sofa', 'train',
        'tvmonitor'
    ]

    def __init__(self):
        """Load the model and define preprocessing."""
        print("Loading DeepLabV3 model...")
        self.model = torchvision.models.segmentation.deeplabv3_resnet101(
            weights='DeepLabV3_ResNet101_Weights.DEFAULT'
        )
        self.model.eval()

        self.preprocess = transforms.Compose([
            transforms.Resize(520),
            transforms.CenterCrop(480),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        print("Model ready!")

    def segment(self, image):
        """
        Segment an image.

        Parameters:
            image: PIL Image

        Returns:
            mask: numpy array of shape (H, W) with class IDs
        """
        # Preprocess
        input_tensor = self.preprocess(image).unsqueeze(0)

        # Run inference
        with torch.no_grad():
            output = self.model(input_tensor)

        # Get predictions
        predictions = torch.argmax(output['out'], dim=1)
        mask = predictions.squeeze(0).numpy()

        return mask

    def describe_scene(self, mask):
        """
        Describe what objects were found in the segmentation.

        Parameters:
            mask: numpy array with class IDs
        """
        unique_classes = np.unique(mask)
        total_pixels = mask.size

        print("\nObjects found in the image:")
        print("-" * 40)

        for class_id in unique_classes:
            class_name = self.CLASSES[class_id]
            pixel_count = np.sum(mask == class_id)
            percentage = (pixel_count / total_pixels) * 100
            print(f"  {class_name:15s}: {percentage:5.1f}% of image "
                  f"({pixel_count:,} pixels)")

# Example usage
segmenter = ImageSegmenter()

# In practice, load a real image:
# image = Image.open("street.jpg").convert("RGB")
# mask = segmenter.segment(image)
# segmenter.describe_scene(mask)

print("\nSegmenter is ready to use!")
print("Call segmenter.segment(image) with a PIL Image.")
```

**Output:**
```
Loading DeepLabV3 model...
Model ready!

Segmenter is ready to use!
Call segmenter.segment(image) with a PIL Image.
```

**Line-by-line explanation:**

- The `ImageSegmenter` class wraps the entire pipeline: model loading, preprocessing, inference, and result analysis.
- `segment(image)` takes a PIL Image and returns a numpy mask where each pixel has a class ID.
- `describe_scene(mask)` analyzes the mask and prints a summary of what was found, including the percentage of the image each object occupies.
- Using a class like this makes the code reusable and organized. You can segment many images with just `segmenter.segment(image)`.

---

## Applications of Image Segmentation

Image segmentation powers many real-world applications:

```
+------------------------+---------------------------------------------+
| Application            | How Segmentation Helps                      |
+------------------------+---------------------------------------------+
| Self-Driving Cars      | Identifies road, lanes, pedestrians,        |
|                        | traffic signs at the pixel level            |
+------------------------+---------------------------------------------+
| Medical Imaging        | Outlines tumors, organs, and blood          |
|                        | vessels in CT scans and MRIs                |
+------------------------+---------------------------------------------+
| Satellite Analysis     | Maps forests, water bodies, urban areas,    |
|                        | and agricultural land from aerial images    |
+------------------------+---------------------------------------------+
| Photo Editing          | Powers "remove background" and "select      |
|                        | subject" features in apps like Photoshop    |
+------------------------+---------------------------------------------+
| Video Conferencing     | Creates virtual backgrounds by separating   |
|                        | the person from the real background         |
+------------------------+---------------------------------------------+
| Agriculture            | Detects plant diseases, measures crop       |
|                        | coverage, identifies weeds vs crops         |
+------------------------+---------------------------------------------+
| Robotics               | Helps robots understand their environment   |
|                        | and navigate around obstacles               |
+------------------------+---------------------------------------------+
```

---

## Common Mistakes

1. **Forgetting to set the model to evaluation mode.** Always call `model.eval()` before inference. Without it, batch normalization and dropout behave differently and produce wrong results.

2. **Not normalizing the input image.** Pre-trained models expect images normalized with specific mean and standard deviation values (usually ImageNet statistics). Feeding raw pixel values will produce garbage output.

3. **Ignoring the output format.** Segmentation models often return dictionaries (not plain tensors). For DeepLabV3 in torchvision, the main output is in `output['out']`.

4. **Expecting perfect boundaries.** Segmentation models are not perfect. Boundaries between objects may be slightly imprecise, especially for small or thin objects.

5. **Using the wrong input size.** While many models accept variable-sized inputs, using very small images will produce poor results. Stick to the recommended input sizes (typically 480-520 pixels).

---

## Best Practices

1. **Start with pre-trained models.** Unless you have a very specific use case and a large labeled dataset, use pre-trained models from torchvision or Hugging Face. They save weeks of training time.

2. **Resize outputs to match the original image.** The model may change the image dimensions during preprocessing. Resize the output mask back to the original size if you need pixel-accurate results on the original image.

3. **Use GPU for faster inference.** Segmentation models are computationally expensive. Move the model and input to GPU with `.to('cuda')` for significant speedups.

4. **Consider model size vs speed tradeoffs.** DeepLabV3 with ResNet-101 is accurate but slow. For real-time applications, consider lighter models like FCN with ResNet-50 or mobile-optimized architectures.

5. **Post-process the mask.** Apply morphological operations (like opening and closing) to clean up noisy segmentation boundaries.

---

## Quick Summary

Image segmentation assigns a class label to every pixel in an image, going beyond classification (one label per image) and detection (one box per object). Semantic segmentation labels pixels by class but does not distinguish individual objects, while instance segmentation identifies each object separately. The U-Net architecture, shaped like a U, uses an encoder to capture features, a decoder to restore spatial resolution, and skip connections to preserve fine details. Pre-trained models like DeepLabV3 from torchvision can segment images into 21 categories out of the box. The output is a segmentation mask that can be colorized and overlaid on the original image for visualization.

---

## Key Points

- **Image segmentation** classifies every pixel, not just the whole image
- **Semantic segmentation** assigns class labels to pixels (all cars are "car")
- **Instance segmentation** also distinguishes individual objects (car #1, car #2)
- **U-Net** has an encoder path, decoder path, and skip connections shaped like a "U"
- **Skip connections** pass fine-grained details from encoder to decoder
- **Pre-trained models** like DeepLabV3 provide accurate segmentation without training
- **Segmentation masks** are 2D arrays where each value is a class ID
- **Colorization** maps class IDs to colors for human-readable visualization

---

## Practice Questions

1. What is the key difference between semantic segmentation and instance segmentation? Give an example where instance segmentation is needed but semantic segmentation is not enough.

2. Why does U-Net use skip connections? What information would be lost without them?

3. If a segmentation model has 10 classes and the input image is 256x256, what is the shape of the model's output tensor? Explain each dimension.

4. Why must we normalize images with ImageNet statistics before feeding them to a pre-trained segmentation model?

5. A self-driving car needs to know exactly which pixels are road and which are sidewalk. Would you use classification, detection, or segmentation? Explain why.

---

## Exercises

### Exercise 1: Analyze a Segmentation Mask

Create a 10x10 numpy array representing a segmentation mask with three classes (background=0, tree=1, house=2). Count the number of pixels for each class and calculate the percentage each class occupies.

### Exercise 2: Build a Segmentation Visualizer

Write a function that takes a segmentation mask and a dictionary mapping class IDs to class names, and prints a "legend" showing which color corresponds to which class. Test it with a mask containing at least 4 different classes.

### Exercise 3: Compare Two Segmentation Masks

Write a function that takes two segmentation masks (predicted and ground truth) and calculates the Intersection over Union (IoU) for each class. IoU = (area of overlap) / (area of union). This is the standard metric for evaluating segmentation quality.

---

## What Is Next?

Now that you can segment images at the pixel level, the next chapter takes on a specific and important challenge: faces. You will learn how to detect faces in images using Haar cascades and MTCNN, how face recognition works through embeddings, and the critical ethical considerations around facial recognition technology. Face detection combines many of the techniques you have learned so far, from image preprocessing to deep learning models, and adds important discussions about bias, privacy, and responsible AI.
