# Chapter 16: Image Fundamentals

## What You Will Learn

In this chapter, you will learn:

- How computers see images as grids of numbers
- The difference between grayscale and color (RGB) images
- How to load images using PIL and OpenCV
- What image shapes and channels mean
- How to display images with matplotlib
- The most common color spaces: RGB, BGR, grayscale, and HSV
- Basic image operations: cropping, resizing, and rotating

## Why This Chapter Matters

Every time you unlock your phone with your face, use a photo filter, or let Google Photos search for "beach," a computer is working with images. But here is the thing: computers do not see pictures the way you do. They see numbers. Lots and lots of numbers.

Before you can build any computer vision model -- whether it classifies cats versus dogs, detects pedestrians, or reads license plates -- you need to understand what an image actually is to a computer. This chapter gives you that foundation.

Think of it like learning to read sheet music before playing piano. You could memorize a few songs without it, but you would never truly understand what you are playing. Understanding image fundamentals is the "sheet music" of computer vision.

---

## 16.1 What Is an Image to a Computer?

When you look at a photograph, you see faces, trees, and sky. When a computer looks at the same photograph, it sees a giant grid of numbers. Each number represents the brightness or color at one tiny point in the image.

### Pixels: The Building Blocks

A **pixel** (short for "picture element") is the smallest unit of an image. It is a single dot of color. If you zoom in very close on any digital image, you will see these tiny squares:

```
+-----+-----+-----+-----+-----+
| 200 | 180 | 170 | 160 | 150 |
+-----+-----+-----+-----+-----+
| 190 | 175 | 165 | 155 | 140 |
+-----+-----+-----+-----+-----+
| 180 | 170 | 160 | 150 | 130 |
+-----+-----+-----+-----+-----+
| 170 | 165 | 155 | 145 | 120 |
+-----+-----+-----+-----+-----+

Each box is one pixel.
Each number is the brightness (0 = black, 255 = white).
```

**Why 0 to 255?** Computers store pixel values using 8 bits (binary digits). With 8 bits, you can represent 2^8 = 256 different values, giving us the range 0 through 255.

### A Real-World Analogy

Imagine a mosaic on a wall. From far away, you see a beautiful picture. But walk up close, and you see it is made of thousands of tiny colored tiles. Each tile is like a pixel. The more tiles you use (higher resolution), the more detailed the picture looks.

---

## 16.2 Grayscale vs. RGB Images

### Grayscale: One Number Per Pixel

A **grayscale** image uses a single number for each pixel. That number represents brightness:

- **0** means completely black
- **255** means completely white
- Values in between are shades of gray

```
Grayscale Image (5x5 pixels):

  0   50  100  150  200      <- Row 0
 25   75  125  175  225      <- Row 1
 50  100  150  200  250      <- Row 2
 75  125  175  225  255      <- Row 3
100  150  200  250  255      <- Row 4

Think of it as a spreadsheet where each cell
holds one number (brightness).
```

### RGB: Three Numbers Per Pixel

A **color image** uses three numbers for each pixel, one for each color channel:

- **R** (Red): How much red light (0-255)
- **G** (Green): How much green light (0-255)
- **B** (Blue): How much blue light (0-255)

```
One Pixel in an RGB Image:

    +-------+-------+-------+
    | R=255 | G=0   | B=0   |  -> Pure Red
    +-------+-------+-------+

    +-------+-------+-------+
    | R=0   | G=255 | B=0   |  -> Pure Green
    +-------+-------+-------+

    +-------+-------+-------+
    | R=0   | G=0   | B=255 |  -> Pure Blue
    +-------+-------+-------+

    +-------+-------+-------+
    | R=255 | G=255 | B=0   |  -> Yellow (Red + Green)
    +-------+-------+-------+

    +-------+-------+-------+
    | R=255 | G=255 | B=255 |  -> White (all colors)
    +-------+-------+-------+

    +-------+-------+-------+
    | R=0   | G=0   | B=0   |  -> Black (no color)
    +-------+-------+-------+
```

### How RGB Channels Stack Up

Think of an RGB image as three transparent sheets stacked on top of each other:

```
RGB Image Structure:

         Width
    +------------------+
    |                  |  <- Red Channel (one layer of numbers)
    |   Red Layer      |
    |                  |
    +------------------+
    |                  |  <- Green Channel
    |   Green Layer    |
    |                  |
    +------------------+
    |                  |  <- Blue Channel
    |   Blue Layer     |
    |                  |
    +------------------+
         Height

Shape: (Height, Width, 3)
         ^       ^     ^
         |       |     |
       rows   columns  channels (R, G, B)
```

**Real-world analogy:** Think of RGB like mixing paint on a palette. Red, green, and blue are your three primary colors. By mixing different amounts of each, you can create any color. A pixel with (255, 165, 0) is orange -- lots of red, some green, no blue.

---

## 16.3 Loading Images with PIL

**PIL** (Python Imaging Library), now maintained as **Pillow**, is one of the most popular Python libraries for working with images. It is simple, intuitive, and works great for basic image tasks.

### Installing Pillow

```python
# Install Pillow (the maintained fork of PIL)
# Run this in your terminal:
# pip install Pillow
```

### Loading and Inspecting an Image

```python
from PIL import Image

# Load an image from disk
# Replace with your own image path
image = Image.open("cat.jpg")

# Check basic properties
print(f"Format: {image.format}")        # Output: Format: JPEG
print(f"Mode: {image.mode}")            # Output: Mode: RGB
print(f"Size: {image.size}")            # Output: Size: (640, 480)
print(f"Width: {image.width}")          # Output: Width: 640
print(f"Height: {image.height}")        # Output: Height: 480
```

**Line-by-line explanation:**

- `Image.open("cat.jpg")`: Opens the image file. It does NOT load all pixel data into memory right away -- PIL uses "lazy loading" to be efficient.
- `image.format`: The file format (JPEG, PNG, BMP, etc.).
- `image.mode`: The color mode. "RGB" means a color image with three channels. "L" means grayscale.
- `image.size`: Returns (width, height) as a tuple. Notice: width comes first in PIL.

### Converting PIL Image to NumPy Array

To do math with images (which is what machine learning does), we need to convert them to NumPy arrays:

```python
from PIL import Image
import numpy as np

# Load image
image = Image.open("cat.jpg")

# Convert to NumPy array
pixel_array = np.array(image)

# Check the array
print(f"Type: {type(pixel_array)}")       # Output: Type: <class 'numpy.ndarray'>
print(f"Shape: {pixel_array.shape}")       # Output: Shape: (480, 640, 3)
print(f"Data type: {pixel_array.dtype}")   # Output: Data type: uint8
print(f"Min value: {pixel_array.min()}")   # Output: Min value: 0
print(f"Max value: {pixel_array.max()}")   # Output: Max value: 255
```

**Line-by-line explanation:**

- `np.array(image)`: Converts the PIL image into a NumPy array of numbers.
- `pixel_array.shape`: Returns (height, width, channels). **Important:** In NumPy, height comes first! This is (480, 640, 3) meaning 480 rows, 640 columns, 3 color channels.
- `pixel_array.dtype`: The data type is `uint8` (unsigned 8-bit integer), meaning values from 0 to 255.

### Accessing Individual Pixels

```python
from PIL import Image
import numpy as np

image = Image.open("cat.jpg")
pixels = np.array(image)

# Get the pixel at row 100, column 200
pixel = pixels[100, 200]
print(f"Pixel at (100, 200): {pixel}")
# Output: Pixel at (100, 200): [142  98  67]
#          This means R=142, G=98, B=67 (a brownish color)

# Get just the red channel value at that pixel
red_value = pixels[100, 200, 0]    # Channel 0 = Red
green_value = pixels[100, 200, 1]  # Channel 1 = Green
blue_value = pixels[100, 200, 2]   # Channel 2 = Blue

print(f"Red: {red_value}")    # Output: Red: 142
print(f"Green: {green_value}")  # Output: Green: 98
print(f"Blue: {blue_value}")   # Output: Blue: 67
```

```
How pixel indexing works:

pixels[row, column, channel]
         |      |       |
         |      |       +-- 0=Red, 1=Green, 2=Blue
         |      +---------- Which column (left to right)
         +----------------- Which row (top to bottom)

        Column 0  Column 1  Column 2  ...
Row 0:  [R,G,B]   [R,G,B]   [R,G,B]
Row 1:  [R,G,B]   [R,G,B]   [R,G,B]
Row 2:  [R,G,B]   [R,G,B]   [R,G,B]
...
```

---

## 16.4 Loading Images with OpenCV

**OpenCV** (Open Source Computer Vision Library) is the most widely used computer vision library in the world. It is faster than PIL for many operations and has hundreds of image processing functions.

### Installing OpenCV

```python
# Install OpenCV for Python
# Run this in your terminal:
# pip install opencv-python
```

### Loading and Inspecting an Image

```python
import cv2

# Load an image
image = cv2.imread("cat.jpg")

# Check properties
print(f"Type: {type(image)}")          # Output: Type: <class 'numpy.ndarray'>
print(f"Shape: {image.shape}")          # Output: Shape: (480, 640, 3)
print(f"Data type: {image.dtype}")      # Output: Data type: uint8
print(f"Height: {image.shape[0]}")      # Output: Height: 480
print(f"Width: {image.shape[1]}")       # Output: Width: 640
print(f"Channels: {image.shape[2]}")    # Output: Channels: 3
```

**Line-by-line explanation:**

- `cv2.imread("cat.jpg")`: Loads the image directly as a NumPy array. Unlike PIL, OpenCV gives you a NumPy array immediately.
- `image.shape`: Same as PIL's NumPy array -- (height, width, channels).

### CRITICAL WARNING: OpenCV Uses BGR, Not RGB!

This is the single most common source of bugs when working with images in Python:

```
PIL loads images as:    R, G, B  (Red, Green, Blue)
OpenCV loads images as: B, G, R  (Blue, Green, Red)

Same image, different channel order!

PIL pixel:    [255,   0,   0] = RED
OpenCV pixel: [255,   0,   0] = BLUE   <-- Surprise!
```

If you load an image with OpenCV and display it with matplotlib (which expects RGB), the colors will look wrong -- reds become blue and blues become red:

```python
import cv2

# Load with OpenCV (BGR order)
bgr_image = cv2.imread("cat.jpg")

# Convert BGR to RGB
rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)

# Now rgb_image has correct colors for matplotlib
```

**Line-by-line explanation:**

- `cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)`: Converts from BGR color order to RGB color order. The function name `cvtColor` stands for "convert color."
- `cv2.COLOR_BGR2RGB`: A constant that tells OpenCV which conversion to perform. Read it as "BGR to RGB."

### Loading Grayscale Images

```python
import cv2

# Method 1: Load directly as grayscale
gray_image = cv2.imread("cat.jpg", cv2.IMREAD_GRAYSCALE)
print(f"Shape: {gray_image.shape}")  # Output: Shape: (480, 640)
# Notice: only 2 dimensions! No channel dimension.

# Method 2: Convert a color image to grayscale
color_image = cv2.imread("cat.jpg")
gray_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
print(f"Shape: {gray_image.shape}")  # Output: Shape: (480, 640)
```

**Key observation:** Grayscale images have shape (height, width) with no third dimension, because there is only one value per pixel (brightness), not three.

---

## 16.5 Image Shapes and Channels

Understanding image shapes is critical because deep learning models are very particular about the shape of their input data.

### Shape Summary

```
Image Type          Shape                Example
---------------------------------------------------------
Grayscale           (H, W)              (480, 640)
RGB (PIL/NumPy)     (H, W, 3)           (480, 640, 3)
BGR (OpenCV)        (H, W, 3)           (480, 640, 3)
RGBA (with alpha)   (H, W, 4)           (480, 640, 4)

Where:
  H = Height (number of rows)
  W = Width (number of columns)
  3 = Three color channels (R, G, B)
  4 = Four channels (R, G, B, A) where A = transparency
```

### Working with Channels

```python
from PIL import Image
import numpy as np

image = Image.open("cat.jpg")
pixels = np.array(image)

print(f"Full image shape: {pixels.shape}")
# Output: Full image shape: (480, 640, 3)

# Extract individual channels
red_channel = pixels[:, :, 0]     # All rows, all columns, channel 0
green_channel = pixels[:, :, 1]   # All rows, all columns, channel 1
blue_channel = pixels[:, :, 2]    # All rows, all columns, channel 2

print(f"Red channel shape: {red_channel.shape}")
# Output: Red channel shape: (480, 640)

print(f"Red channel sample values:")
print(red_channel[:3, :5])
# Output: (first 3 rows, first 5 columns of red values)
# [[142 145 148 150 152]
#  [140 143 146 149 151]
#  [138 141 144 147 150]]
```

**Line-by-line explanation:**

- `pixels[:, :, 0]`: NumPy slicing. The colons (`:`) mean "take everything." So this says "all rows, all columns, channel index 0 (red)."
- Each channel is a 2D array (height x width) containing just that color's intensity values.

```
Extracting Channels:

Full Image (H, W, 3):              Red Channel (H, W):
+---+---+---+                      +---+
|R|G|B|  <- pixel (0,0)           | R |  <- just the red value
+---+---+---+                      +---+
|R|G|B|  <- pixel (0,1)           | R |
+---+---+---+                      +---+
|R|G|B|  <- pixel (1,0)           | R |
+---+---+---+                      +---+
  ...                                ...

pixels[:, :, 0] extracts all R values
pixels[:, :, 1] extracts all G values
pixels[:, :, 2] extracts all B values
```

### PyTorch Channel Convention

Deep learning frameworks like PyTorch use a **different** channel order than NumPy and PIL:

```
NumPy/PIL:  (H, W, C)    "channels last"    (480, 640, 3)
PyTorch:    (C, H, W)    "channels first"   (3, 480, 640)

For batches:
NumPy/PIL:  (B, H, W, C)   (32, 480, 640, 3)
PyTorch:    (B, C, H, W)   (32, 3, 480, 640)

Where B = batch size, C = channels, H = height, W = width
```

Converting between them:

```python
import numpy as np

# NumPy image: (H, W, C)
numpy_image = np.random.randint(0, 256, size=(480, 640, 3), dtype=np.uint8)
print(f"NumPy shape: {numpy_image.shape}")
# Output: NumPy shape: (480, 640, 3)

# Convert to PyTorch order: (C, H, W)
pytorch_order = np.transpose(numpy_image, (2, 0, 1))
print(f"PyTorch shape: {pytorch_order.shape}")
# Output: PyTorch shape: (3, 480, 640)

# Convert back to NumPy order: (H, W, C)
back_to_numpy = np.transpose(pytorch_order, (1, 2, 0))
print(f"Back to NumPy: {back_to_numpy.shape}")
# Output: Back to NumPy: (480, 640, 3)
```

**Line-by-line explanation:**

- `np.transpose(image, (2, 0, 1))`: Rearranges the axes. The tuple `(2, 0, 1)` means "put axis 2 first, then axis 0, then axis 1." Since axis 2 is channels, this moves channels to the front.

---

## 16.6 Displaying Images with Matplotlib

**Matplotlib** is the standard Python plotting library. It works perfectly for displaying images in Jupyter notebooks and scripts.

### Basic Display

```python
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

# Load image with PIL
image = Image.open("cat.jpg")

# Display the image
plt.figure(figsize=(8, 6))
plt.imshow(image)
plt.title("A Cat")
plt.axis("off")       # Hide the axis numbers
plt.show()
```

**Output:** A window (or inline image in Jupyter) showing the cat photo with the title "A Cat" and no axis tick marks.

### Displaying Multiple Images Side by Side

```python
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

# Load image
image = Image.open("cat.jpg")
pixels = np.array(image)

# Create a figure with 4 subplots
fig, axes = plt.subplots(1, 4, figsize=(16, 4))

# Original image
axes[0].imshow(pixels)
axes[0].set_title("Original (RGB)")
axes[0].axis("off")

# Red channel only
axes[1].imshow(pixels[:, :, 0], cmap="Reds")
axes[1].set_title("Red Channel")
axes[1].axis("off")

# Green channel only
axes[2].imshow(pixels[:, :, 1], cmap="Greens")
axes[2].set_title("Green Channel")
axes[2].axis("off")

# Blue channel only
axes[3].imshow(pixels[:, :, 2], cmap="Blues")
axes[3].set_title("Blue Channel")
axes[3].axis("off")

plt.tight_layout()
plt.show()
```

**Output:** Four images side by side: the original color image, then the red, green, and blue channels displayed with their respective color maps.

**Line-by-line explanation:**

- `plt.subplots(1, 4, figsize=(16, 4))`: Creates 1 row of 4 subplots, each in a 16x4 inch figure.
- `cmap="Reds"`: A **colormap** that maps single-channel values to shades of red. Without this, matplotlib would show a single channel in weird rainbow colors.
- `plt.tight_layout()`: Adjusts spacing so the subplots do not overlap.

### Displaying Grayscale Images Correctly

```python
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

# Load and convert to grayscale
image = Image.open("cat.jpg").convert("L")
gray_pixels = np.array(image)

# WRONG way - shows weird colors
plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.imshow(gray_pixels)           # No cmap specified!
plt.title("Wrong: Default Colormap")
plt.axis("off")

# RIGHT way - shows proper gray shades
plt.subplot(1, 2, 2)
plt.imshow(gray_pixels, cmap="gray")  # Specify gray colormap
plt.title("Correct: Gray Colormap")
plt.axis("off")

plt.tight_layout()
plt.show()
```

**Output:** Two images. The left one shows the grayscale image with strange false colors (matplotlib's default "viridis" colormap). The right one shows it correctly in shades of gray.

**Key lesson:** Always use `cmap="gray"` when displaying grayscale images with matplotlib, or they will look wrong.

---

## 16.7 Color Spaces

A **color space** is a way of representing colors with numbers. Different color spaces are useful for different tasks. Think of it like measuring temperature -- you can use Fahrenheit, Celsius, or Kelvin. They all describe the same thing (temperature) but in different ways.

### RGB Color Space

The most common color space. Every pixel has three values: Red, Green, Blue.

```
RGB Color Space:

        Green (0-255)
          |
          |
          +-------> Red (0-255)
         /
        /
       Blue (0-255)

Common RGB values:
  (255,   0,   0) = Red
  (  0, 255,   0) = Green
  (  0,   0, 255) = Blue
  (255, 255,   0) = Yellow
  (255, 165,   0) = Orange
  (128,   0, 128) = Purple
  (255, 255, 255) = White
  (  0,   0,   0) = Black
  (128, 128, 128) = Gray
```

**Used by:** PIL, matplotlib, most image formats, web colors, and most deep learning models.

### BGR Color Space

Same channels as RGB, but in reverse order: Blue, Green, Red.

```
RGB pixel: [Red, Green, Blue]  = [255,   0,   0] = RED
BGR pixel: [Blue, Green, Red]  = [255,   0,   0] = BLUE

Same numbers, different meaning!
```

**Used by:** OpenCV. This exists for historical reasons (early camera hardware used BGR order).

### Grayscale

A single brightness value per pixel. Converting from RGB to grayscale uses a weighted formula:

```
Gray = 0.299 * R + 0.587 * G + 0.114 * B

Why not equal weights?
Human eyes are most sensitive to green,
then red, then blue. The weights reflect
how our eyes perceive brightness.

Example:
  RGB = (200, 100, 50)
  Gray = 0.299 * 200 + 0.587 * 100 + 0.114 * 50
       = 59.8 + 58.7 + 5.7
       = 124.2 (rounds to 124)
```

### HSV Color Space

**HSV** stands for Hue, Saturation, Value. It describes color the way humans think about it:

- **Hue (H):** The color itself (red, blue, green, etc.) -- represented as an angle from 0 to 360 degrees (or 0-180 in OpenCV)
- **Saturation (S):** How vivid or pure the color is (0 = gray, 255 = full color)
- **Value (V):** How bright the color is (0 = dark, 255 = bright)

```
HSV Color Space:

        Value (Brightness)
          |
          |  Saturation
          |  /
          | /
          +-------> Hue (Color wheel)

Hue values (in OpenCV, 0-180):
  0   = Red
  30  = Orange/Yellow
  60  = Yellow/Green
  90  = Green/Cyan
  120 = Blue
  150 = Purple/Pink
  180 = Red (wraps around)

Real-world analogy:
  Hue = Which paint color you pick
  Saturation = How much water you add (diluted vs pure)
  Value = How much light shines on it (dark room vs bright room)
```

**Why use HSV?** It is much easier to select a color range in HSV. For example, to find all "red" objects, you just check if Hue is near 0 (or near 180). In RGB, "red" is spread across all three channels, making it harder to isolate.

### Converting Between Color Spaces

```python
import cv2
import numpy as np
from PIL import Image

# Load image with OpenCV (BGR)
bgr_image = cv2.imread("cat.jpg")

# BGR to RGB
rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)

# BGR to Grayscale
gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)

# BGR to HSV
hsv_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)

# Print shapes
print(f"BGR shape: {bgr_image.shape}")    # Output: BGR shape: (480, 640, 3)
print(f"RGB shape: {rgb_image.shape}")    # Output: RGB shape: (480, 640, 3)
print(f"Gray shape: {gray_image.shape}")  # Output: Gray shape: (480, 640)
print(f"HSV shape: {hsv_image.shape}")    # Output: HSV shape: (480, 640, 3)

# Inspect HSV values at one pixel
h, s, v = hsv_image[100, 200]
print(f"Hue: {h}, Saturation: {s}, Value: {v}")
# Output: Hue: 15, Saturation: 140, Value: 180
# This means: orangish color, moderately vivid, fairly bright
```

### Using PIL for Color Space Conversion

```python
from PIL import Image
import numpy as np

# Load image
image = Image.open("cat.jpg")   # RGB by default

# Convert to grayscale
gray = image.convert("L")
print(f"Mode: {gray.mode}")              # Output: Mode: L
print(f"Shape: {np.array(gray).shape}")   # Output: Shape: (480, 640)

# Convert to RGBA (with transparency channel)
rgba = image.convert("RGBA")
print(f"Mode: {rgba.mode}")               # Output: Mode: RGBA
print(f"Shape: {np.array(rgba).shape}")    # Output: Shape: (480, 640, 4)
```

---

## 16.8 Basic Image Operations

### Cropping

**Cropping** means cutting out a rectangular region of an image. Think of it like using scissors to cut a photo.

```python
from PIL import Image
import numpy as np

# Load image
image = Image.open("cat.jpg")
pixels = np.array(image)

print(f"Original size: {image.size}")  # Output: Original size: (640, 480)

# --- Method 1: Crop with PIL ---
# PIL uses (left, upper, right, lower) coordinates
# Crop a 200x200 region starting at (100, 50)
cropped_pil = image.crop((100, 50, 300, 250))
print(f"Cropped PIL size: {cropped_pil.size}")
# Output: Cropped PIL size: (200, 200)

# --- Method 2: Crop with NumPy slicing ---
# NumPy uses [row_start:row_end, col_start:col_end]
cropped_np = pixels[50:250, 100:300]
print(f"Cropped NumPy shape: {cropped_np.shape}")
# Output: Cropped NumPy shape: (200, 200, 3)
```

```
Cropping Coordinates:

PIL:  image.crop((left, top, right, bottom))

    (0,0)_________________(W,0)
      |                    |
      |   (left,top)       |
      |      +--------+   |
      |      | CROPPED|   |
      |      | REGION |   |
      |      +--------+   |
      |         (right,bottom)
      |____________________|
    (0,H)              (W,H)

NumPy: pixels[top:bottom, left:right]

    Same region, but rows come before columns.
```

### Resizing

**Resizing** changes the dimensions of an image. This is essential for deep learning because models expect a fixed input size.

```python
from PIL import Image
import cv2
import numpy as np

# --- Method 1: Resize with PIL ---
image = Image.open("cat.jpg")
print(f"Original: {image.size}")  # Output: Original: (640, 480)

# Resize to exact dimensions
resized = image.resize((224, 224))
print(f"Resized: {resized.size}")  # Output: Resized: (224, 224)

# Resize with high-quality resampling
resized_hq = image.resize((224, 224), resample=Image.LANCZOS)
print(f"Resized HQ: {resized_hq.size}")  # Output: Resized HQ: (224, 224)

# --- Method 2: Resize with OpenCV ---
cv_image = cv2.imread("cat.jpg")
print(f"Original: {cv_image.shape[:2]}")  # Output: Original: (480, 640)

# OpenCV resize takes (width, height) -- same order as PIL
resized_cv = cv2.resize(cv_image, (224, 224))
print(f"Resized: {resized_cv.shape[:2]}")  # Output: Resized: (224, 224)

# With interpolation method
resized_cv_hq = cv2.resize(cv_image, (224, 224),
                            interpolation=cv2.INTER_LANCZOS4)
print(f"Resized HQ: {resized_cv_hq.shape[:2]}")
# Output: Resized HQ: (224, 224)
```

**Line-by-line explanation:**

- `image.resize((224, 224))`: Resizes to 224x224 pixels. The number 224 is very common in deep learning (used by ResNet, VGG, and many other models).
- `Image.LANCZOS`: A high-quality resampling filter. When shrinking images, LANCZOS gives sharper results. When enlarging, it gives smoother results.
- `cv2.INTER_LANCZOS4`: OpenCV's equivalent of the LANCZOS filter.

```
Resizing Methods (Interpolation):

NEAREST:   Fastest, but blocky (picks nearest pixel)
BILINEAR:  Good balance of speed and quality
BICUBIC:   Higher quality, slightly slower
LANCZOS:   Best quality, slowest

For deep learning preprocessing, BILINEAR is usually
good enough. For final display, use LANCZOS.
```

### Rotating

**Rotating** turns an image by a specified angle.

```python
from PIL import Image
import cv2
import numpy as np

# --- Method 1: Rotate with PIL ---
image = Image.open("cat.jpg")

# Rotate 45 degrees counterclockwise
rotated = image.rotate(45)
print(f"Rotated size: {rotated.size}")
# Output: Rotated size: (640, 480)
# Note: Same size, corners are cut off and filled with black

# Rotate and expand to fit the whole image
rotated_expand = image.rotate(45, expand=True)
print(f"Rotated expanded size: {rotated_expand.size}")
# Output: Rotated expanded size: (791, 791)
# Note: Image is larger to fit the rotated content

# --- Method 2: Rotate with OpenCV ---
cv_image = cv2.imread("cat.jpg")
height, width = cv_image.shape[:2]

# Create rotation matrix (center, angle, scale)
center = (width // 2, height // 2)
rotation_matrix = cv2.getRotationMatrix2D(center, 45, 1.0)

# Apply rotation
rotated_cv = cv2.warpAffine(cv_image, rotation_matrix, (width, height))
print(f"Rotated shape: {rotated_cv.shape[:2]}")
# Output: Rotated shape: (480, 640)
```

**Line-by-line explanation:**

- `image.rotate(45)`: Rotates 45 degrees counterclockwise. Positive angles go counterclockwise.
- `expand=True`: Makes the output image larger so nothing gets cut off.
- `cv2.getRotationMatrix2D(center, 45, 1.0)`: Creates a 2x3 transformation matrix. Parameters are: center point, angle, scale (1.0 means no scaling).
- `cv2.warpAffine(...)`: Applies the transformation to the image.

### Flipping

```python
from PIL import Image
import numpy as np

image = Image.open("cat.jpg")

# Flip horizontally (mirror)
flipped_h = image.transpose(Image.FLIP_LEFT_RIGHT)

# Flip vertically (upside down)
flipped_v = image.transpose(Image.FLIP_TOP_BOTTOM)

print(f"Original size: {image.size}")      # Output: Original size: (640, 480)
print(f"H-flipped size: {flipped_h.size}") # Output: H-flipped size: (640, 480)
print(f"V-flipped size: {flipped_v.size}") # Output: V-flipped size: (640, 480)
# Flipping does not change the image size
```

---

## 16.9 Putting It All Together

Here is a complete example that loads an image, explores its properties, converts between color spaces, and performs basic operations:

```python
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

# Step 1: Load the image
image = Image.open("cat.jpg")
print("=== Image Properties ===")
print(f"Format: {image.format}")
print(f"Mode: {image.mode}")
print(f"Size (W x H): {image.size}")

# Step 2: Convert to NumPy array
pixels = np.array(image)
print(f"\n=== NumPy Array ===")
print(f"Shape (H, W, C): {pixels.shape}")
print(f"Data type: {pixels.dtype}")
print(f"Value range: [{pixels.min()}, {pixels.max()}]")

# Step 3: Create grayscale version
gray = image.convert("L")
gray_pixels = np.array(gray)
print(f"\n=== Grayscale ===")
print(f"Shape: {gray_pixels.shape}")

# Step 4: Crop, resize, and rotate
cropped = image.crop((100, 50, 400, 350))
resized = image.resize((224, 224), resample=Image.LANCZOS)
rotated = image.rotate(30, expand=True)

# Step 5: Display everything
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

axes[0, 0].imshow(pixels)
axes[0, 0].set_title(f"Original {image.size}")
axes[0, 0].axis("off")

axes[0, 1].imshow(gray_pixels, cmap="gray")
axes[0, 1].set_title(f"Grayscale {gray_pixels.shape}")
axes[0, 1].axis("off")

axes[0, 2].imshow(np.array(cropped))
axes[0, 2].set_title(f"Cropped {cropped.size}")
axes[0, 2].axis("off")

axes[1, 0].imshow(np.array(resized))
axes[1, 0].set_title(f"Resized {resized.size}")
axes[1, 0].axis("off")

axes[1, 1].imshow(np.array(rotated))
axes[1, 1].set_title(f"Rotated {rotated.size}")
axes[1, 1].axis("off")

# Show color channels
axes[1, 2].imshow(pixels[:, :, 0], cmap="gray")
axes[1, 2].set_title("Red Channel")
axes[1, 2].axis("off")

plt.suptitle("Image Fundamentals Overview", fontsize=16)
plt.tight_layout()
plt.show()
```

**Output:** A 2x3 grid of images showing the original, grayscale, cropped, resized, rotated, and red channel versions of the cat image.

---

## Common Mistakes

1. **Confusing RGB and BGR.** If your image looks like it has swapped red and blue colors, you probably loaded it with OpenCV (BGR) and displayed it with matplotlib (expects RGB). Always convert with `cv2.cvtColor(image, cv2.COLOR_BGR2RGB)`.

2. **Confusing width/height order.** PIL's `.size` returns `(width, height)`, but NumPy's `.shape` returns `(height, width, channels)`. This inconsistency trips up many beginners.

3. **Forgetting `cmap="gray"` for grayscale images.** Without it, matplotlib uses a rainbow colormap that makes grayscale images look like heat maps.

4. **Not checking if the image loaded.** `cv2.imread()` returns `None` if the file is not found instead of raising an error. Always check: `if image is None: print("Failed to load image!")`.

5. **Mixing up PIL Image and NumPy array.** PIL Images have methods like `.resize()` and `.crop()`. NumPy arrays have slicing and mathematical operations. Convert with `np.array(pil_image)` or `Image.fromarray(numpy_array)`.

---

## Best Practices

1. **Always verify your image loaded correctly.** Print the shape, dtype, and a few pixel values before proceeding.

2. **Stick to one library when possible.** Mixing PIL and OpenCV in the same pipeline introduces BGR/RGB conversion bugs. Pick one and use it consistently.

3. **Use RGB for deep learning pipelines.** Most pretrained models expect RGB input. Convert early in your pipeline.

4. **Keep original images unchanged.** Always work on copies. Use `image.copy()` or `pixels.copy()` before modifying.

5. **Use `Image.LANCZOS` for resizing** when quality matters (preprocessing for models). It produces the sharpest results.

---

## Quick Summary

An image is a grid of numbers. Grayscale images use one number per pixel (brightness). Color images use three numbers per pixel (Red, Green, Blue). PIL and OpenCV are the two main Python libraries for loading and manipulating images. PIL uses RGB order; OpenCV uses BGR order -- this is the most common source of bugs. NumPy represents images as arrays with shape (height, width, channels). Deep learning models (PyTorch) expect channels first: (channels, height, width). Matplotlib is the standard tool for displaying images in Python. Color spaces like HSV can be more useful than RGB for certain tasks like color detection.

---

## Key Points

- A pixel is the smallest unit of a digital image, represented as a number (grayscale) or a group of numbers (color).
- Grayscale images have shape (H, W); RGB images have shape (H, W, 3).
- PIL loads images in RGB order. OpenCV loads images in BGR order. Always convert when switching between them.
- PIL `.size` returns (width, height). NumPy `.shape` returns (height, width, channels). The order is different!
- PyTorch expects images in (C, H, W) format, while NumPy uses (H, W, C). Use `np.transpose()` to convert.
- Always use `cmap="gray"` when displaying grayscale images with matplotlib.
- HSV color space separates color (Hue) from intensity (Value), making it easier to detect specific colors.

---

## Practice Questions

1. You have a NumPy array with shape `(720, 1280, 3)`. What are the height, width, and number of channels of this image?

2. You load an image with OpenCV and display it with matplotlib. The sky looks orange instead of blue. What went wrong, and how do you fix it?

3. What is the difference between `image.size` in PIL and `pixels.shape` in NumPy? If PIL reports `(640, 480)`, what will NumPy report?

4. Why does the grayscale conversion formula use different weights for R, G, and B (`0.299, 0.587, 0.114`) instead of equal weights?

5. You want to convert a NumPy image from shape `(480, 640, 3)` to PyTorch format. What function do you use, and what will the resulting shape be?

---

## Exercises

### Exercise 1: Image Explorer

Write a function `explore_image(path)` that takes a file path, loads the image with PIL, and prints:
- File format
- Color mode
- Size (width x height)
- NumPy shape
- Data type
- Min, max, and mean pixel values
- Whether it is grayscale or color

Test it on at least two different images.

### Exercise 2: Channel Visualizer

Load a color image and create a matplotlib figure with 5 subplots showing:
1. The original RGB image
2. The Red channel (using the "Reds" colormap)
3. The Green channel (using the "Greens" colormap)
4. The Blue channel (using the "Blues" colormap)
5. The grayscale version

Add appropriate titles to each subplot.

### Exercise 3: Image Operations Pipeline

Write a script that:
1. Loads an image
2. Crops the center 50% of the image (remove the outer 25% on each side)
3. Resizes the crop to exactly 256x256 pixels
4. Rotates the resized image by 90 degrees
5. Flips it horizontally
6. Saves the final result as "processed.png"
7. Displays the original and final images side by side

---

## What Is Next?

Now that you understand what images are and how to work with them in Python, the next chapter covers **Image Preprocessing** -- the essential step of preparing images for deep learning models. You will learn how to normalize pixel values, apply transformations, and build efficient preprocessing pipelines using torchvision. These skills are what bridge the gap between raw images and model-ready data.
