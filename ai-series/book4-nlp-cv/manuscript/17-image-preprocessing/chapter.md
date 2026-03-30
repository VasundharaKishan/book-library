# Chapter 17: Image Preprocessing

## What You Will Learn

In this chapter, you will learn:

- Why images need preprocessing before feeding them to deep learning models
- How to resize images to the exact dimensions models expect
- How to normalize pixel values using 0-1 scaling and ImageNet statistics
- How to convert between color spaces for model input
- How to use torchvision transforms to build preprocessing pipelines
- The differences between PIL and OpenCV for preprocessing
- How to build reusable preprocessing pipelines
- How to preprocess batches of images efficiently

## Why This Chapter Matters

Imagine trying to compare the height of buildings using photos taken from different distances, angles, and cameras. Some photos are close-up, some are far away, some are dark, some are bright. You cannot compare them fairly until you standardize them.

Deep learning models face the same problem. Raw images come in all sizes, brightness levels, and color ranges. A model trained on 224x224 images will crash if you feed it a 4000x3000 photo from your phone. A model expecting pixel values between 0 and 1 will produce garbage if you give it values between 0 and 255.

Image preprocessing is the bridge between raw, messy real-world images and the clean, standardized input that models need. Get this wrong, and even the best model will fail. Get it right, and you are halfway to a working computer vision system.

---

## 17.1 Why Preprocess Images?

Deep learning models are surprisingly picky about their input. Here is why preprocessing matters:

### Problem 1: Images Have Different Sizes

```
Your photos might be:
  Photo A: 4032 x 3024 pixels (12 megapixels)
  Photo B: 1920 x 1080 pixels (1080p)
  Photo C:  640 x  480 pixels (VGA)

But your model expects:
  Input: 224 x 224 pixels (exactly!)

Without resizing, the model cannot even accept these images.
```

### Problem 2: Pixel Values Are Too Large

```
Raw pixel values: 0 to 255 (integers)

Neural networks work best with small floating-point numbers.
Large values cause:
  - Gradient explosion (weights grow out of control)
  - Slow convergence (takes forever to train)
  - Numerical instability (math errors)

After normalization: roughly -2.5 to 2.5 (floats)
```

### Problem 3: Different Libraries Use Different Formats

```
PIL image:      (W, H) size,   RGB,   0-255, PIL Image object
OpenCV image:   (H, W, C),     BGR,   0-255, NumPy array
PyTorch tensor: (C, H, W),     RGB,   0-1,   torch.Tensor

A preprocessing pipeline handles ALL these conversions.
```

### The Preprocessing Pipeline

```
Raw Image File
      |
      v
  Load Image (PIL or OpenCV)
      |
      v
  Resize (e.g., to 224x224)
      |
      v
  Convert to RGB (if needed)
      |
      v
  Convert to Float (0-255 -> 0.0-1.0)
      |
      v
  Normalize (subtract mean, divide by std)
      |
      v
  Convert to Tensor (H,W,C -> C,H,W)
      |
      v
  Ready for Model!
```

---

## 17.2 Resizing Images for Models

Every major model architecture expects a specific input size. Here are the most common ones:

```
Model               Expected Input Size
-----------------------------------------
AlexNet             227 x 227
VGG-16/19           224 x 224
ResNet              224 x 224
Inception v3        299 x 299
EfficientNet-B0     224 x 224
EfficientNet-B7     600 x 600
ViT (Vision Transf) 224 x 224
```

### Simple Resize

```python
from PIL import Image

# Load a large image
image = Image.open("photo.jpg")
print(f"Original size: {image.size}")
# Output: Original size: (4032, 3024)

# Resize to 224x224
resized = image.resize((224, 224), resample=Image.LANCZOS)
print(f"Resized: {resized.size}")
# Output: Resized: (224, 224)
```

**Problem with simple resize:** If the original image is not square, resizing to a square will stretch or squish the image, distorting objects.

```
Original (4:3 ratio):          After resize to 224x224:
+------------------+           +------------+
|                  |           |            |
|   Normal cat     |  ----->   | Squished   |
|                  |           | cat        |
+------------------+           +------------+

The cat looks wider/shorter. Not ideal!
```

### Resize Then Center Crop (Better Approach)

A better strategy is to resize the shorter side to the target size, then crop the center:

```python
from PIL import Image

def resize_and_center_crop(image, target_size=224):
    """Resize shorter side to target_size, then center crop."""
    width, height = image.size

    # Step 1: Resize so shorter side = target_size
    if width < height:
        new_width = target_size
        new_height = int(height * target_size / width)
    else:
        new_height = target_size
        new_width = int(width * target_size / height)

    resized = image.resize((new_width, new_height), resample=Image.LANCZOS)

    # Step 2: Center crop to target_size x target_size
    left = (new_width - target_size) // 2
    top = (new_height - target_size) // 2
    right = left + target_size
    bottom = top + target_size

    cropped = resized.crop((left, top, right, bottom))
    return cropped

# Usage
image = Image.open("photo.jpg")
result = resize_and_center_crop(image, 224)
print(f"Result size: {result.size}")
# Output: Result size: (224, 224)
```

```
Resize + Center Crop:

Original (640x480):     Resize shorter side:    Center crop:
+------------------+   +------------------+    +------------+
|                  |   |                  |    |            |
|   Normal cat     |-->| Still normal     |--> | Normal cat |
|                  |   | proportions     |    | (centered) |
+------------------+   +------------------+    +------------+
                       (298 x 224)              (224 x 224)

No distortion! We just lose a bit of the edges.
```

**Line-by-line explanation:**

- We calculate the aspect ratio and resize so the shorter side matches the target.
- `(new_width - target_size) // 2`: Calculates how many pixels to cut from each side to center the crop.
- The result is a square image with correct proportions.

---

## 17.3 Normalization

**Normalization** means adjusting pixel values to a standard range. This is one of the most important preprocessing steps.

### Method 1: Simple 0-1 Scaling

The simplest normalization: divide every pixel by 255 to get values between 0 and 1.

```python
import numpy as np
from PIL import Image

image = Image.open("cat.jpg")
pixels = np.array(image)

print(f"Before normalization:")
print(f"  dtype: {pixels.dtype}")        # Output: dtype: uint8
print(f"  range: [{pixels.min()}, {pixels.max()}]")
# Output: range: [0, 255]

# Normalize to 0-1
normalized = pixels.astype(np.float32) / 255.0

print(f"\nAfter normalization:")
print(f"  dtype: {normalized.dtype}")     # Output: dtype: float32
print(f"  range: [{normalized.min():.4f}, {normalized.max():.4f}]")
# Output: range: [0.0000, 1.0000]
```

**Line-by-line explanation:**

- `pixels.astype(np.float32)`: Converts from integer (uint8) to floating point. This is necessary because dividing integers in NumPy can produce unexpected results.
- `/ 255.0`: Divides every value by 255, mapping 0 to 0.0 and 255 to 1.0.

```
0-1 Normalization:

Before:  [0,   128,   255]  (integers, 0 to 255)
           |      |      |
           v      v      v
After:   [0.0, 0.502, 1.0]  (floats, 0.0 to 1.0)

Formula: normalized_value = original_value / 255.0
```

### Method 2: ImageNet Normalization

Most pretrained models (ResNet, VGG, etc.) were trained on the ImageNet dataset. They expect pixel values normalized using ImageNet's **mean** and **standard deviation** for each channel.

```
ImageNet Statistics:

Channel    Mean     Std Dev
-----------------------------
Red        0.485    0.229
Green      0.456    0.224
Blue       0.406    0.225

These numbers come from calculating the average
pixel value across all 1.2 million ImageNet images.
```

The normalization formula:

```
normalized = (pixel_value / 255.0 - mean) / std

Step 1: Scale to 0-1       (divide by 255)
Step 2: Subtract the mean   (center around 0)
Step 3: Divide by std       (standardize spread)
```

```python
import numpy as np
from PIL import Image

# ImageNet normalization values
IMAGENET_MEAN = np.array([0.485, 0.456, 0.406])
IMAGENET_STD = np.array([0.229, 0.224, 0.225])

# Load and convert to float
image = Image.open("cat.jpg")
pixels = np.array(image).astype(np.float32) / 255.0

print(f"After 0-1 scaling:")
print(f"  Red channel mean: {pixels[:,:,0].mean():.4f}")
print(f"  Green channel mean: {pixels[:,:,1].mean():.4f}")
print(f"  Blue channel mean: {pixels[:,:,2].mean():.4f}")
# Output varies by image, e.g.:
# Red channel mean: 0.5123
# Green channel mean: 0.4456
# Blue channel mean: 0.3789

# Apply ImageNet normalization
normalized = (pixels - IMAGENET_MEAN) / IMAGENET_STD

print(f"\nAfter ImageNet normalization:")
print(f"  Red channel mean: {normalized[:,:,0].mean():.4f}")
print(f"  Range: [{normalized.min():.4f}, {normalized.max():.4f}]")
# Output varies by image, e.g.:
# Red channel mean: 0.1192
# Range: [-2.1179, 2.6400]
```

**Why does this work?** When you use a pretrained model, you must preprocess your images the same way the training images were preprocessed. ImageNet models "learned" what the world looks like with these specific normalization values baked in. Using different normalization is like speaking a different language -- the model will not understand.

```
Why ImageNet Normalization Matters:

Training:                        Inference:
ImageNet images                  Your images
       |                              |
  Normalize with                 Normalize with
  mean=[0.485,0.456,0.406]      mean=[0.485,0.456,0.406]  <- SAME!
  std=[0.229,0.224,0.225]       std=[0.229,0.224,0.225]   <- SAME!
       |                              |
       v                              v
  Model learns patterns          Model recognizes patterns
  from these values              using the same scale

If you skip normalization or use different values,
the model sees garbage, not images.
```

### Method 3: Custom Normalization

If you train a model from scratch on your own dataset, you should calculate your own mean and standard deviation:

```python
import numpy as np
from PIL import Image
import os

def calculate_dataset_stats(image_dir):
    """Calculate mean and std of a dataset."""
    pixel_sum = np.zeros(3)
    pixel_sq_sum = np.zeros(3)
    num_pixels = 0

    for filename in os.listdir(image_dir):
        if filename.endswith((".jpg", ".png")):
            path = os.path.join(image_dir, filename)
            img = np.array(Image.open(path).convert("RGB"))
            img = img.astype(np.float32) / 255.0

            pixel_sum += img.sum(axis=(0, 1))
            pixel_sq_sum += (img ** 2).sum(axis=(0, 1))
            num_pixels += img.shape[0] * img.shape[1]

    mean = pixel_sum / num_pixels
    std = np.sqrt(pixel_sq_sum / num_pixels - mean ** 2)

    return mean, std

# Usage
# mean, std = calculate_dataset_stats("my_dataset/train/")
# print(f"Mean: {mean}")  # e.g., [0.512, 0.478, 0.401]
# print(f"Std: {std}")    # e.g., [0.267, 0.251, 0.274]
```

**Line-by-line explanation:**

- `pixel_sum += img.sum(axis=(0, 1))`: Sums all pixel values along height (axis 0) and width (axis 1), keeping the channel dimension. This accumulates the total across all images.
- `pixel_sq_sum`: Accumulates squared values, needed for the standard deviation formula.
- `std = sqrt(E[X^2] - (E[X])^2)`: This is the mathematical formula for standard deviation, calculated efficiently in one pass.

---

## 17.4 Color Space Conversions

### Ensuring RGB Input

Most deep learning models expect RGB images. Here is how to handle different sources:

```python
from PIL import Image
import cv2
import numpy as np

# === PIL: Already RGB ===
pil_image = Image.open("photo.jpg")
print(f"PIL mode: {pil_image.mode}")  # Output: PIL mode: RGB
# No conversion needed!

# But sometimes images are grayscale or RGBA
gray_image = Image.open("gray_photo.jpg")
print(f"Gray mode: {gray_image.mode}")  # Output: Gray mode: L

# Convert grayscale to RGB (creates 3 identical channels)
rgb_from_gray = gray_image.convert("RGB")
print(f"Converted mode: {rgb_from_gray.mode}")  # Output: Converted mode: RGB

# Handle RGBA (with transparency)
png_image = Image.open("logo.png")
print(f"PNG mode: {png_image.mode}")  # Output: PNG mode: RGBA

# Convert RGBA to RGB (drops alpha channel)
rgb_from_rgba = png_image.convert("RGB")
print(f"Converted mode: {rgb_from_rgba.mode}")  # Output: Converted mode: RGB

# === OpenCV: BGR by default ===
cv_image = cv2.imread("photo.jpg")
# MUST convert to RGB for deep learning
rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
```

### Safe Image Loading Function

```python
from PIL import Image
import numpy as np

def safe_load_image(path):
    """Load any image and ensure it is RGB format."""
    image = Image.open(path)

    # Handle different modes
    if image.mode == "RGB":
        return image
    elif image.mode == "RGBA":
        # Create white background and paste image
        background = Image.new("RGB", image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])  # Use alpha as mask
        return background
    elif image.mode == "L":
        # Grayscale to RGB
        return image.convert("RGB")
    elif image.mode == "P":
        # Palette mode (like some GIFs)
        return image.convert("RGB")
    else:
        return image.convert("RGB")

# Usage
image = safe_load_image("any_image.png")
print(f"Mode: {image.mode}")  # Output: Mode: RGB (always!)
```

**Line-by-line explanation:**

- `image.mode == "RGBA"`: RGBA images have a transparency channel. Simply converting to RGB can produce artifacts (black areas where transparency was). Instead, we paste onto a white background.
- `image.split()[3]`: Splits the image into channels. Index 3 is the alpha (transparency) channel.
- `image.mode == "P"`: Palette mode uses a lookup table for colors. Common in GIF files.

---

## 17.5 Torchvision Transforms

**Torchvision** is PyTorch's computer vision library. Its `transforms` module provides ready-made preprocessing functions that you can chain together into pipelines.

### Installing Torchvision

```python
# Install PyTorch and torchvision
# Run in your terminal:
# pip install torch torchvision
```

### Basic Transforms

```python
from torchvision import transforms
from PIL import Image

# Load image
image = Image.open("cat.jpg")
print(f"Original: size={image.size}, mode={image.mode}")
# Output: Original: size=(640, 480), mode=RGB

# === Individual transforms ===

# 1. Resize
resize_transform = transforms.Resize((224, 224))
resized = resize_transform(image)
print(f"Resized: {resized.size}")
# Output: Resized: (224, 224)

# 2. Center Crop
crop_transform = transforms.CenterCrop(224)
cropped = crop_transform(image)
print(f"Cropped: {cropped.size}")
# Output: Cropped: (224, 224)

# 3. Convert to Tensor (also scales 0-255 to 0-1)
tensor_transform = transforms.ToTensor()
tensor = tensor_transform(image)
print(f"Tensor shape: {tensor.shape}")
print(f"Tensor range: [{tensor.min():.4f}, {tensor.max():.4f}]")
# Output: Tensor shape: torch.Size([3, 480, 640])
# Output: Tensor range: [0.0000, 1.0000]

# 4. Normalize with ImageNet stats
normalize_transform = transforms.Normalize(
    mean=[0.485, 0.456, 0.406],
    std=[0.229, 0.224, 0.225]
)
normalized = normalize_transform(tensor)
print(f"Normalized range: [{normalized.min():.4f}, {normalized.max():.4f}]")
# Output: Normalized range: [-2.1179, 2.6400]  (approximately)
```

**Line-by-line explanation:**

- `transforms.Resize((224, 224))`: Creates a transform that resizes images to 224x224. You can also pass a single number like `transforms.Resize(256)` to resize the shorter side to 256 while keeping the aspect ratio.
- `transforms.CenterCrop(224)`: Crops the center 224x224 region.
- `transforms.ToTensor()`: This does THREE things at once: (1) converts PIL Image to PyTorch tensor, (2) changes shape from (H, W, C) to (C, H, W), and (3) scales values from 0-255 to 0.0-1.0.
- `transforms.Normalize(mean, std)`: Applies per-channel normalization. This expects values already in the 0-1 range (i.e., after `ToTensor()`).

### Composing a Pipeline with transforms.Compose

The real power comes from chaining transforms together:

```python
from torchvision import transforms
from PIL import Image

# Define the preprocessing pipeline
preprocess = transforms.Compose([
    transforms.Resize(256),              # Resize shorter side to 256
    transforms.CenterCrop(224),          # Crop center 224x224
    transforms.ToTensor(),               # PIL -> Tensor, 0-255 -> 0-1
    transforms.Normalize(                # ImageNet normalization
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])

# Apply the entire pipeline in one call
image = Image.open("cat.jpg")
tensor = preprocess(image)

print(f"Input: PIL Image {image.size}")
print(f"Output: Tensor {tensor.shape}")
print(f"Output range: [{tensor.min():.4f}, {tensor.max():.4f}]")
# Output: Input: PIL Image (640, 480)
# Output: Output: Tensor torch.Size([3, 224, 224])
# Output: Output range: [-2.1179, 2.6400]
```

```
transforms.Compose Pipeline:

PIL Image (640, 480)
       |
  Resize(256)         -> PIL Image (341, 256)
       |                  (shorter side = 256)
  CenterCrop(224)     -> PIL Image (224, 224)
       |                  (center square)
  ToTensor()          -> Tensor (3, 224, 224)
       |                  (channels first, 0-1 range)
  Normalize(...)      -> Tensor (3, 224, 224)
       |                  (centered, standardized)
       v
  Ready for model!
```

### Training vs. Validation Transforms

During training, you typically apply **data augmentation** (random changes) to make the model more robust. During validation and testing, you use deterministic (non-random) transforms:

```python
from torchvision import transforms

# Training: includes random augmentations
train_transforms = transforms.Compose([
    transforms.RandomResizedCrop(224),      # Random crop + resize
    transforms.RandomHorizontalFlip(),       # 50% chance to flip
    transforms.ColorJitter(                  # Random color changes
        brightness=0.2,
        contrast=0.2,
        saturation=0.2,
        hue=0.1
    ),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])

# Validation/Testing: deterministic, no randomness
val_transforms = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])
```

**Line-by-line explanation:**

- `RandomResizedCrop(224)`: Randomly picks a region of the image, crops it, and resizes to 224x224. This teaches the model to recognize objects at different scales and positions.
- `RandomHorizontalFlip()`: Flips the image left-to-right with 50% probability. A cat is still a cat when flipped.
- `ColorJitter(...)`: Randomly adjusts brightness, contrast, saturation, and hue. This teaches the model to handle different lighting conditions.

```
Training Augmentation:

Same image, 4 different random transforms:

  +--------+  +--------+  +--------+  +--------+
  |  Cat   |  | Cat    |  |   Cat  |  |  taC   |
  | (dark) |  | (zoom) |  | (crop) |  | (flip) |
  +--------+  +--------+  +--------+  +--------+

The model sees many variations of each image,
making it more robust to real-world conditions.
```

---

## 17.6 PIL vs. OpenCV for Preprocessing

Both PIL and OpenCV can preprocess images. Here is when to use each:

### Comparison Table

```
Feature              PIL (Pillow)         OpenCV
-------------------------------------------------
Default format       PIL Image object     NumPy array
Color order          RGB                  BGR
Speed                Slower               Faster
Ease of use          Simpler API          More complex
PyTorch integration  Excellent            Needs conversion
Image operations     Basic but good       Very comprehensive
Memory efficiency    Lazy loading         Loads everything
Best for             Deep learning prep   Computer vision tasks
```

### Side-by-Side Preprocessing

```python
from PIL import Image
import cv2
import numpy as np
import torch

# === PIL Pipeline ===
def preprocess_pil(path):
    # Load
    image = Image.open(path).convert("RGB")

    # Resize
    image = image.resize((224, 224), resample=Image.LANCZOS)

    # To NumPy and normalize
    pixels = np.array(image).astype(np.float32) / 255.0

    # ImageNet normalization
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    pixels = (pixels - mean) / std

    # To PyTorch tensor (H,W,C) -> (C,H,W)
    tensor = torch.from_numpy(pixels.transpose(2, 0, 1)).float()
    return tensor

# === OpenCV Pipeline ===
def preprocess_opencv(path):
    # Load (BGR!)
    image = cv2.imread(path)

    # Convert BGR to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Resize
    image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_LINEAR)

    # To float and normalize
    pixels = image.astype(np.float32) / 255.0

    # ImageNet normalization
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    pixels = (pixels - mean) / std

    # To PyTorch tensor (H,W,C) -> (C,H,W)
    tensor = torch.from_numpy(pixels.transpose(2, 0, 1)).float()
    return tensor

# Both produce the same result
tensor_pil = preprocess_pil("cat.jpg")
tensor_cv = preprocess_opencv("cat.jpg")
print(f"PIL output shape: {tensor_pil.shape}")
print(f"OpenCV output shape: {tensor_cv.shape}")
# Output: PIL output shape: torch.Size([3, 224, 224])
# Output: OpenCV output shape: torch.Size([3, 224, 224])
```

**Recommendation:** Use **PIL with torchvision transforms** for deep learning projects. It integrates seamlessly with PyTorch's data loading utilities and is less error-prone (no BGR/RGB confusion).

---

## 17.7 Building Preprocessing Pipelines

### A Reusable Preprocessing Class

```python
from torchvision import transforms
from PIL import Image
import torch

class ImagePreprocessor:
    """Reusable image preprocessing for different model architectures."""

    # Presets for common models
    PRESETS = {
        "resnet": {"size": 224, "resize": 256},
        "inception": {"size": 299, "resize": 342},
        "efficientnet_b0": {"size": 224, "resize": 256},
        "efficientnet_b7": {"size": 600, "resize": 672},
        "vit": {"size": 224, "resize": 256},
    }

    def __init__(self, model_name="resnet", mode="eval"):
        """
        Args:
            model_name: One of the preset model names
            mode: "train" for training (with augmentation)
                  "eval" for inference (no augmentation)
        """
        config = self.PRESETS.get(model_name, self.PRESETS["resnet"])
        target_size = config["size"]
        resize_size = config["resize"]

        if mode == "train":
            self.transform = transforms.Compose([
                transforms.RandomResizedCrop(target_size),
                transforms.RandomHorizontalFlip(),
                transforms.ColorJitter(0.2, 0.2, 0.2, 0.1),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                ),
            ])
        else:
            self.transform = transforms.Compose([
                transforms.Resize(resize_size),
                transforms.CenterCrop(target_size),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                ),
            ])

    def __call__(self, image):
        """Preprocess a single PIL image."""
        if isinstance(image, str):
            image = Image.open(image).convert("RGB")
        return self.transform(image)

# Usage
preprocessor = ImagePreprocessor("resnet", mode="eval")

# Preprocess a single image
tensor = preprocessor("cat.jpg")
print(f"Output: {tensor.shape}")
# Output: Output: torch.Size([3, 224, 224])

# Preprocess for training
train_preprocessor = ImagePreprocessor("resnet", mode="train")
tensor_train = train_preprocessor("cat.jpg")
print(f"Training output: {tensor_train.shape}")
# Output: Training output: torch.Size([3, 224, 224])
```

**Line-by-line explanation:**

- `self.PRESETS`: A dictionary of common model configurations. This avoids hardcoding sizes everywhere.
- `__call__`: Makes the class callable like a function. You can use `preprocessor("cat.jpg")` instead of `preprocessor.process("cat.jpg")`.
- `isinstance(image, str)`: If a file path is passed, load it. If a PIL Image is passed, use it directly.

---

## 17.8 Batch Preprocessing

In real projects, you preprocess thousands of images. Doing this efficiently matters.

### Using PyTorch DataLoader

The standard approach combines a `Dataset` with a `DataLoader`:

```python
from torchvision import transforms
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import os
import torch

class ImageDataset(Dataset):
    """A simple dataset that loads images from a directory."""

    def __init__(self, image_dir, transform=None):
        self.image_dir = image_dir
        self.transform = transform

        # Get all image file paths
        self.image_paths = [
            os.path.join(image_dir, f)
            for f in os.listdir(image_dir)
            if f.endswith((".jpg", ".jpeg", ".png"))
        ]

        print(f"Found {len(self.image_paths)} images")

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        # Load image
        image = Image.open(self.image_paths[idx]).convert("RGB")

        # Apply transforms
        if self.transform:
            image = self.transform(image)

        return image

# Define transforms
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])

# Create dataset and dataloader
dataset = ImageDataset("images/", transform=preprocess)
dataloader = DataLoader(
    dataset,
    batch_size=32,       # Process 32 images at a time
    shuffle=False,       # Keep original order
    num_workers=4,       # Use 4 parallel processes for loading
)

# Iterate through batches
for batch in dataloader:
    print(f"Batch shape: {batch.shape}")
    # Output: Batch shape: torch.Size([32, 3, 224, 224])
    break  # Just show one batch
```

```
Batch Preprocessing Flow:

DataLoader (num_workers=4)
       |
       +-- Worker 1: loads images 0,4,8,...
       +-- Worker 2: loads images 1,5,9,...
       +-- Worker 3: loads images 2,6,10,...
       +-- Worker 4: loads images 3,7,11,...
       |
       v
  Collate function stacks individual
  images into a batch tensor
       |
       v
  Batch: (32, 3, 224, 224)
    32 images, 3 channels, 224x224 pixels
```

**Line-by-line explanation:**

- `__len__`: Returns the total number of images. The DataLoader uses this to know how many batches to create.
- `__getitem__`: Returns one preprocessed image. The DataLoader calls this in parallel using multiple workers.
- `batch_size=32`: Groups 32 images into a single tensor. Larger batches are faster but use more memory.
- `num_workers=4`: Uses 4 separate processes to load and preprocess images in parallel while the GPU trains on the previous batch.

### Preprocessing with Progress Tracking

```python
from torchvision import transforms
from PIL import Image
import os
import time

def batch_preprocess_and_save(input_dir, output_dir, transform):
    """Preprocess all images and save the results."""
    os.makedirs(output_dir, exist_ok=True)

    image_files = [
        f for f in os.listdir(input_dir)
        if f.endswith((".jpg", ".jpeg", ".png"))
    ]

    total = len(image_files)
    start_time = time.time()

    for i, filename in enumerate(image_files):
        # Load and preprocess
        path = os.path.join(input_dir, filename)
        image = Image.open(path).convert("RGB")
        tensor = transform(image)

        # Save preprocessed tensor
        save_path = os.path.join(
            output_dir,
            filename.rsplit(".", 1)[0] + ".pt"
        )
        import torch
        torch.save(tensor, save_path)

        # Progress update
        if (i + 1) % 100 == 0 or (i + 1) == total:
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed
            remaining = (total - i - 1) / rate
            print(f"[{i+1}/{total}] "
                  f"{rate:.1f} images/sec, "
                  f"~{remaining:.0f}s remaining")

    print(f"\nDone! Processed {total} images "
          f"in {time.time() - start_time:.1f} seconds.")

# Usage
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])

# batch_preprocess_and_save("raw_images/", "preprocessed/", preprocess)
# Output:
# [100/5000] 45.2 images/sec, ~108s remaining
# [200/5000] 46.1 images/sec, ~104s remaining
# ...
# Done! Processed 5000 images in 109.3 seconds.
```

---

## 17.9 Undoing Normalization for Display

After normalizing an image for model input, you cannot display it directly (the values are wrong for display). You need to **denormalize** to convert back to viewable values:

```python
import torch
import numpy as np
import matplotlib.pyplot as plt
from torchvision import transforms
from PIL import Image

def denormalize(tensor, mean, std):
    """Convert a normalized tensor back to displayable format."""
    # Clone to avoid modifying the original
    img = tensor.clone()

    # Reverse normalization: value = (normalized * std) + mean
    for channel in range(3):
        img[channel] = img[channel] * std[channel] + mean[channel]

    # Clip to valid range [0, 1]
    img = torch.clamp(img, 0, 1)

    # Convert from (C, H, W) to (H, W, C) for matplotlib
    img = img.permute(1, 2, 0).numpy()

    return img

# Preprocess an image
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])

image = Image.open("cat.jpg")
tensor = preprocess(image)

# Try displaying the normalized tensor (wrong!)
fig, axes = plt.subplots(1, 2, figsize=(10, 5))

# This will look wrong - colors are off
wrong_display = tensor.permute(1, 2, 0).numpy()
wrong_display = np.clip(wrong_display, 0, 1)
axes[0].imshow(wrong_display)
axes[0].set_title("Normalized (Wrong Colors)")
axes[0].axis("off")

# Denormalize first (correct!)
correct_display = denormalize(
    tensor,
    mean=[0.485, 0.456, 0.406],
    std=[0.229, 0.224, 0.225]
)
axes[1].imshow(correct_display)
axes[1].set_title("Denormalized (Correct)")
axes[1].axis("off")

plt.tight_layout()
plt.show()
```

```
Denormalization:

Normalized value: -1.5
   * std (0.229) = -0.3435
   + mean (0.485) = 0.1415
Displayable value: 0.1415  (dark pixel)

Normalized value: 2.0
   * std (0.229) = 0.458
   + mean (0.485) = 0.943
Displayable value: 0.943  (bright pixel)

Formula: display_value = normalized * std + mean
(This is the REVERSE of normalization)
```

---

## Common Mistakes

1. **Forgetting to convert to RGB before preprocessing.** Grayscale or RGBA images will crash your pipeline. Always call `.convert("RGB")` when loading.

2. **Applying `Normalize()` before `ToTensor()`.** `Normalize()` expects values in the 0-1 range (produced by `ToTensor()`). If you apply it to 0-255 values, the results will be wildly wrong.

3. **Using training transforms for validation.** Random augmentations during evaluation make your metrics unreliable. Always use deterministic transforms for validation and testing.

4. **Not matching preprocessing between training and inference.** If you trained with ImageNet normalization, you MUST use the same normalization at inference time. This is the number one cause of "my model works during training but fails in production."

5. **Resizing without considering aspect ratio.** Simple resize distorts objects. Use resize-then-crop or resize with padding to maintain proportions.

6. **Forgetting that `ToTensor()` already scales to 0-1.** If you manually divide by 255 and THEN apply `ToTensor()`, your values will be divided twice, giving you tiny numbers near zero.

---

## Best Practices

1. **Use `torchvision.transforms.Compose`** to define clear, reusable preprocessing pipelines. Keep them as named variables, not inline.

2. **Always use the same normalization** for training and inference. Store the mean and std values as constants.

3. **Use `num_workers > 0` in DataLoader** to parallelize preprocessing. A good starting value is 4, or `os.cpu_count()` minus one.

4. **Validate your preprocessing visually.** Denormalize a few images and display them to make sure they look correct.

5. **Keep preprocessing simple during debugging.** Start with just `Resize`, `ToTensor`, and `Normalize`. Add augmentations only after the basic pipeline works.

---

## Quick Summary

Image preprocessing converts raw images into the standardized format that deep learning models expect. The essential steps are: resize to the model's expected dimensions, convert to the correct color space (RGB), scale pixel values to floats (0-1 via `ToTensor()`), and normalize using dataset statistics (ImageNet mean and std for pretrained models). Torchvision's `transforms.Compose` lets you chain these steps into a clean pipeline. Training pipelines include random augmentations; validation pipelines do not. PyTorch's DataLoader handles batch preprocessing with parallel workers.

---

## Key Points

- Deep learning models require fixed-size input images. Most standard models use 224x224 pixels.
- `ToTensor()` does three things: converts PIL to tensor, changes (H,W,C) to (C,H,W), and scales 0-255 to 0.0-1.0.
- ImageNet normalization (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]) is required for any pretrained model trained on ImageNet.
- Training transforms include random augmentations (flips, crops, color jitter). Validation transforms must be deterministic.
- Always match your inference preprocessing to your training preprocessing exactly.
- Use DataLoader with `num_workers > 0` for efficient batch preprocessing.
- Denormalize tensors before displaying them to get correct colors.

---

## Practice Questions

1. Why do we normalize pixel values before feeding them to a neural network? What would happen if we did not?

2. What three things does `transforms.ToTensor()` do to a PIL image?

3. You trained a model using ImageNet normalization. At inference time, you forgot to normalize your test images. What would happen and why?

4. Why do we use different transforms for training versus validation? Give an example of a transform that should only be used during training.

5. You have images of different sizes: 800x600, 1200x900, and 640x480. Explain two strategies to make them all 224x224 without distortion.

---

## Exercises

### Exercise 1: Complete Preprocessing Pipeline

Write a preprocessing pipeline using `transforms.Compose` that:
1. Resizes the image so the shorter side is 256 pixels
2. Takes a center crop of 224x224
3. Converts to a tensor
4. Normalizes with ImageNet statistics

Apply it to three images of different sizes and verify all outputs have shape `(3, 224, 224)`.

### Exercise 2: Dataset Statistics Calculator

Write a function that takes a directory of images and calculates:
- The mean pixel value for each channel (R, G, B)
- The standard deviation for each channel
- The min and max image dimensions in the dataset

Print the results and compare to ImageNet statistics.

### Exercise 3: Visual Augmentation Explorer

Create a script that takes one image and applies these augmentations 9 times each, displaying results in a 3x3 grid:
1. `RandomResizedCrop(224)`
2. `RandomHorizontalFlip()` combined with `ColorJitter()`
3. `RandomRotation(30)` combined with `RandomGrayscale(p=0.2)`

Show how each augmentation produces different variations of the same image.

---

## What Is Next?

Now that you know how to prepare images for deep learning, the next chapter teaches you how to **classify images using Convolutional Neural Networks (CNNs)**. You will build a complete image classification pipeline from scratch -- loading a dataset, building a CNN model, training it, and evaluating its performance. Everything you learned about preprocessing in this chapter will be put to work.
