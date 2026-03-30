# Chapter 11: How CNNs See Images

## What You Will Learn

In this chapter, you will learn:

- How computers store images as numbers
- What pixels and RGB color channels are
- What a filter (also called a kernel) is and why it matters
- How the convolution operation works, step by step
- How edge detection filters find boundaries in images
- What feature maps are and what they represent
- How stride and padding control the convolution process
- How to perform convolution with real numbers

## Why This Chapter Matters

When you look at a photograph of a cat, you instantly recognize the ears, whiskers, and fur. Your brain processes millions of visual signals without you even thinking about it. But how does a computer "see" the same image?

The answer is Convolutional Neural Networks, or CNNs for short. CNNs are the technology behind self-driving cars that detect pedestrians, phone apps that recognize faces, and medical systems that spot tumors in X-rays. Before we can build a CNN, we need to understand what it actually does under the hood.

This chapter breaks down the most important operation in computer vision: convolution. By the end, you will understand exactly how a CNN looks at raw pixel numbers and finds patterns like edges, textures, and shapes. This foundation is essential for everything that follows in the next chapters.

---

## Images Are Just Numbers

When you take a photo with your phone, the camera captures light and converts it into numbers. Every image on your computer is actually a giant grid of numbers.

### What Is a Pixel?

A pixel is the smallest unit of an image. Think of it like a single tile in a mosaic. Each tile has one color, and when you put thousands of tiles together, you see a picture.

A small 28 by 28 image (like the handwritten digits in the MNIST dataset) has 28 rows and 28 columns, giving us 784 pixels total.

```
Think of a pixel like a single LEGO brick in a LEGO mosaic.
One brick = one color.
Thousands of bricks together = a recognizable image.
```

### Grayscale Images: One Number Per Pixel

In a grayscale image (black and white), each pixel is represented by a single number between 0 and 255:

- **0** means completely black (no light)
- **255** means completely white (maximum light)
- Numbers in between represent shades of gray

```python
import numpy as np

# A tiny 5x5 grayscale image
# Low numbers = dark, high numbers = bright
image = np.array([
    [0,   0,   0,   0,   0  ],
    [0,   200, 200, 200, 0  ],
    [0,   200, 255, 200, 0  ],
    [0,   200, 200, 200, 0  ],
    [0,   0,   0,   0,   0  ]
])

print("Image shape:", image.shape)
print("Image values:")
print(image)
```

**Output:**
```
Image shape: (5, 5)
Image values:
[[  0   0   0   0   0]
 [  0 200 200 200   0]
 [  0 200 255 200   0]
 [  0 200 200 200   0]
 [  0   0   0   0   0]]
```

**Line-by-line explanation:**

- `import numpy as np` imports the NumPy library, which handles arrays of numbers efficiently.
- `image = np.array([...])` creates a 5-by-5 grid of numbers. Each number is one pixel.
- The outer ring of zeros means the border is black. The inner values (200, 255) mean the center is bright. This creates a bright square on a dark background.
- `image.shape` tells us the image has 5 rows and 5 columns.

Here is what this tiny image looks like as a diagram:

```
+-----+-----+-----+-----+-----+
|  0  |  0  |  0  |  0  |  0  |  <- Row 0 (all black)
+-----+-----+-----+-----+-----+
|  0  | 200 | 200 | 200 |  0  |  <- Row 1
+-----+-----+-----+-----+-----+
|  0  | 200 | 255 | 200 |  0  |  <- Row 2 (center is brightest)
+-----+-----+-----+-----+-----+
|  0  | 200 | 200 | 200 |  0  |  <- Row 3
+-----+-----+-----+-----+-----+
|  0  |  0  |  0  |  0  |  0  |  <- Row 4 (all black)
+-----+-----+-----+-----+-----+
```

### Color Images: Three Numbers Per Pixel (RGB)

Color images use three channels:

- **R** = Red (how much red light)
- **G** = Green (how much green light)
- **B** = Blue (how much blue light)

Each channel has values from 0 to 255. By mixing different amounts of red, green, and blue, you can create any color.

```
RGB Color Examples:
  (255,   0,   0) = Pure Red
  (  0, 255,   0) = Pure Green
  (  0,   0, 255) = Pure Blue
  (255, 255,   0) = Yellow (Red + Green)
  (255, 255, 255) = White (all colors at max)
  (  0,   0,   0) = Black (no colors)
  (128, 128, 128) = Gray (equal amounts)
```

Think of RGB like mixing paint, except with light. Every color you see on your screen is a combination of these three primary colors.

```python
import numpy as np

# A tiny 3x3 color image with 3 channels (RGB)
# Shape: (height, width, channels) = (3, 3, 3)
color_image = np.zeros((3, 3, 3), dtype=np.uint8)

# Make top-left pixel red
color_image[0, 0] = [255, 0, 0]

# Make center pixel green
color_image[1, 1] = [0, 255, 0]

# Make bottom-right pixel blue
color_image[2, 2] = [0, 0, 255]

print("Color image shape:", color_image.shape)
print("Top-left pixel (Red):", color_image[0, 0])
print("Center pixel (Green):", color_image[1, 1])
print("Bottom-right pixel (Blue):", color_image[2, 2])
```

**Output:**
```
Color image shape: (3, 3, 3)
Top-left pixel (Red): [255   0   0]
Center pixel (Green): [  0 255   0]
Bottom-right pixel (Blue): [  0   0 255]
```

**Line-by-line explanation:**

- `np.zeros((3, 3, 3), dtype=np.uint8)` creates a 3x3 image with 3 color channels, filled with zeros (all black). The `uint8` means unsigned 8-bit integer, which holds values 0-255.
- `color_image[0, 0] = [255, 0, 0]` sets the pixel at row 0, column 0 to pure red (255 red, 0 green, 0 blue).
- The shape `(3, 3, 3)` means 3 rows, 3 columns, and 3 color channels.

```
How a Color Image Is Stored (3 Separate Layers):

    Red Channel         Green Channel        Blue Channel
  +-----+-----+-----+ +-----+-----+-----+ +-----+-----+-----+
  | 255 |  0  |  0  | |  0  |  0  |  0  | |  0  |  0  |  0  |
  +-----+-----+-----+ +-----+-----+-----+ +-----+-----+-----+
  |  0  |  0  |  0  | |  0  | 255 |  0  | |  0  |  0  |  0  |
  +-----+-----+-----+ +-----+-----+-----+ +-----+-----+-----+
  |  0  |  0  |  0  | |  0  |  0  |  0  | |  0  |  0  | 255 |
  +-----+-----+-----+ +-----+-----+-----+ +-----+-----+-----+

  These three layers stack on top of each other to form one color image.
```

### Image Dimensions in Deep Learning

In deep learning frameworks like PyTorch, images are usually stored as tensors (multi-dimensional arrays) with a specific order:

```
PyTorch format:  (Channels, Height, Width)
Example:         (3, 224, 224) = 3 color channels, 224 pixels tall, 224 pixels wide

NumPy/PIL format: (Height, Width, Channels)
Example:          (224, 224, 3) = same image, different order
```

This difference in ordering is important to remember. PyTorch puts the channel dimension first because it makes the convolution operation more efficient.

---

## What Is a Filter (Kernel)?

Now that we know images are grids of numbers, how does a CNN find patterns in those numbers? The answer is filters.

### The Filter Analogy

Imagine you have a magnifying glass that is much smaller than the page you are reading. You slide it across the page, looking at one small area at a time. As you move it, you notice certain patterns: letters, spaces, punctuation marks.

A **filter** (also called a **kernel**) works the same way. It is a small grid of numbers, typically 3x3 or 5x5, that slides across an image looking for specific patterns.

```
The Filter Is Like a Pattern Detector:

  Image (big)              Filter (small)
  +---+---+---+---+---+    +---+---+---+
  |   |   |   |   |   |    | 1 | 0 |-1 |
  +---+---+---+---+---+    +---+---+---+
  |   |   |   |   |   |    | 1 | 0 |-1 |
  +---+---+---+---+---+    +---+---+---+
  |   |   |   |   |   |    | 1 | 0 |-1 |
  +---+---+---+---+---+    +---+---+---+
  |   |   |   |   |   |
  +---+---+---+---+---+    The filter slides over
  |   |   |   |   |   |    the image, one position
  +---+---+---+---+---+    at a time.
```

### What Makes a Filter Special?

Each filter is designed to detect a specific pattern:

- **Edge detection filter:** finds boundaries where light meets dark
- **Blur filter:** smooths out the image
- **Sharpen filter:** makes details more pronounced

The key insight about CNNs is this: **the network learns the best filter values automatically during training.** You do not need to design filters by hand. The CNN figures out what patterns to look for by adjusting the filter numbers through backpropagation.

```python
import numpy as np

# A 3x3 filter for detecting vertical edges
vertical_edge_filter = np.array([
    [ 1,  0, -1],
    [ 1,  0, -1],
    [ 1,  0, -1]
])

# A 3x3 filter for detecting horizontal edges
horizontal_edge_filter = np.array([
    [ 1,  1,  1],
    [ 0,  0,  0],
    [-1, -1, -1]
])

print("Vertical edge filter:")
print(vertical_edge_filter)
print("\nHorizontal edge filter:")
print(horizontal_edge_filter)
```

**Output:**
```
Vertical edge filter:
[[ 1  0 -1]
 [ 1  0 -1]
 [ 1  0 -1]]

Horizontal edge filter:
[[ 1  1  1]
 [ 0  0  0]
 [-1 -1 -1]]
```

**Line-by-line explanation:**

- The vertical edge filter has positive numbers on the left and negative numbers on the right. When this slides over a place where the image goes from bright (left) to dark (right), it produces a large positive number. This is how it "detects" a vertical edge.
- The horizontal edge filter works the same way but rotated: positive on top, negative on bottom. It detects horizontal edges.
- The zeros in the middle mean the filter ignores the center column (or row).

---

## The Convolution Operation

Convolution is the core mathematical operation that gives CNNs their name. It sounds complicated, but it is actually just multiplication and addition.

### How Convolution Works Step by Step

Here is the process:

1. Place the filter on the top-left corner of the image
2. Multiply each filter value by the corresponding image value
3. Add up all the products to get one single number
4. Write that number in the output (called the feature map)
5. Slide the filter one position to the right
6. Repeat steps 2-5 until you reach the end of the row
7. Move down one row and start again from the left

```
Step-by-Step Convolution:

Step 1: Place filter on top-left corner

  Image:                    Filter:
  +---+---+---+---+---+    +---+---+---+
  | 1 | 2 | 3 | 0 | 1 |    | 1 | 0 |-1 |
  +---+---+---+---+---+    +---+---+---+
  | 4 | 5 | 6 | 1 | 2 |    | 1 | 0 |-1 |
  +---+---+---+---+---+    +---+---+---+
  | 7 | 8 | 9 | 2 | 0 |    | 1 | 0 |-1 |
  +---+---+---+---+---+    +---+---+---+
  | 2 | 3 | 1 | 5 | 4 |
  +---+---+---+---+---+
  | 1 | 0 | 2 | 3 | 6 |
  +---+---+---+---+---+

Step 2: Multiply and add (element-wise)

  Covered region:           Filter:
  | 1 | 2 | 3 |            | 1 | 0 |-1 |
  | 4 | 5 | 6 |     x      | 1 | 0 |-1 |
  | 7 | 8 | 9 |            | 1 | 0 |-1 |

  = (1x1) + (2x0) + (3x-1)
  + (4x1) + (5x0) + (6x-1)
  + (7x1) + (8x0) + (9x-1)

  = 1 + 0 + (-3)
  + 4 + 0 + (-6)
  + 7 + 0 + (-9)

  = 1 - 3 + 4 - 6 + 7 - 9
  = -6

Step 3: Write -6 in the output feature map

  Output (so far):
  +----+
  | -6 |
  +----+
```

### Complete Convolution Example with Code

Let us perform a full convolution operation in Python:

```python
import numpy as np

# Our 5x5 input image
image = np.array([
    [1, 2, 3, 0, 1],
    [4, 5, 6, 1, 2],
    [7, 8, 9, 2, 0],
    [2, 3, 1, 5, 4],
    [1, 0, 2, 3, 6]
])

# Our 3x3 filter (vertical edge detector)
kernel = np.array([
    [ 1,  0, -1],
    [ 1,  0, -1],
    [ 1,  0, -1]
])

# Perform convolution manually
# Output size = (image_size - filter_size) + 1 = (5 - 3) + 1 = 3
output_size = image.shape[0] - kernel.shape[0] + 1
output = np.zeros((output_size, output_size))

for i in range(output_size):
    for j in range(output_size):
        # Extract the region of the image covered by the filter
        region = image[i:i+3, j:j+3]

        # Element-wise multiply and sum
        output[i, j] = np.sum(region * kernel)

print("Input image:")
print(image)
print("\nFilter (kernel):")
print(kernel)
print("\nOutput (feature map):")
print(output)
```

**Output:**
```
Input image:
[[1 2 3 0 1]
 [4 5 6 1 2]
 [7 8 9 2 0]
 [2 3 1 5 4]
 [1 0 2 3 6]]

Filter (kernel):
[[ 1  0 -1]
 [ 1  0 -1]
 [ 1  0 -1]]

Output (feature map):
[[ -6.  -2.   2.]
 [ -3.   3.   3.]
 [  6.  -2. -12.]]
```

**Line-by-line explanation:**

- `output_size = image.shape[0] - kernel.shape[0] + 1` calculates the output dimension. A 5x5 image with a 3x3 filter produces a 3x3 output (5 - 3 + 1 = 3). The output is smaller because the filter cannot go beyond the edges.
- `for i in range(output_size)` loops over each row of the output.
- `for j in range(output_size)` loops over each column of the output.
- `region = image[i:i+3, j:j+3]` extracts the 3x3 patch of the image that the filter currently covers.
- `np.sum(region * kernel)` multiplies each element of the region by the corresponding element of the filter and adds them all up. This single number goes into the output.

```
Complete Convolution Walkthrough:

  Position (0,0): region [1,2,3; 4,5,6; 7,8,9]   -> output = -6
  Position (0,1): region [2,3,0; 5,6,1; 8,9,2]   -> output = -2
  Position (0,2): region [3,0,1; 6,1,2; 9,2,0]   -> output =  2
  Position (1,0): region [4,5,6; 7,8,9; 2,3,1]   -> output = -3
  Position (1,1): region [5,6,1; 8,9,2; 3,1,5]   -> output =  3
  Position (1,2): region [6,1,2; 9,2,0; 1,5,4]   -> output =  3
  Position (2,0): region [7,8,9; 2,3,1; 1,0,2]   -> output =  6
  Position (2,1): region [8,9,2; 3,1,5; 0,2,3]   -> output = -2
  Position (2,2): region [9,2,0; 1,5,4; 2,3,6]   -> output = -12

  Final output (feature map):
  +-----+-----+-----+
  |  -6 |  -2 |   2 |
  +-----+-----+-----+
  |  -3 |   3 |   3 |
  +-----+-----+-----+
  |   6 |  -2 | -12 |
  +-----+-----+-----+
```

---

## Edge Detection Filter Example

Edge detection is one of the most intuitive examples of what a filter does. An edge in an image is a place where pixel values change sharply, like the boundary between a dark object and a bright background.

```python
import numpy as np

# Create a simple image with a clear vertical edge
# Left side is bright (200), right side is dark (50)
image_with_edge = np.array([
    [200, 200, 200, 50, 50, 50],
    [200, 200, 200, 50, 50, 50],
    [200, 200, 200, 50, 50, 50],
    [200, 200, 200, 50, 50, 50],
    [200, 200, 200, 50, 50, 50],
    [200, 200, 200, 50, 50, 50]
])

# Vertical edge detection filter
vertical_filter = np.array([
    [ 1,  0, -1],
    [ 1,  0, -1],
    [ 1,  0, -1]
])

# Perform convolution
output_rows = image_with_edge.shape[0] - vertical_filter.shape[0] + 1
output_cols = image_with_edge.shape[1] - vertical_filter.shape[1] + 1
edge_output = np.zeros((output_rows, output_cols))

for i in range(output_rows):
    for j in range(output_cols):
        region = image_with_edge[i:i+3, j:j+3]
        edge_output[i, j] = np.sum(region * vertical_filter)

print("Image with vertical edge:")
print(image_with_edge)
print("\nEdge detection output:")
print(edge_output)
```

**Output:**
```
Image with vertical edge:
[[200 200 200  50  50  50]
 [200 200 200  50  50  50]
 [200 200 200  50  50  50]
 [200 200 200  50  50  50]
 [200 200 200  50  50  50]
 [200 200 200  50  50  50]]

Edge detection output:
[[   0.  450.  450.    0.]
 [   0.  450.  450.    0.]
 [   0.  450.  450.    0.]
 [   0.  450.  450.    0.]]
```

**Line-by-line explanation:**

- The image has a clear vertical edge: bright values (200) on the left and dark values (50) on the right.
- After applying the vertical edge filter, the output shows **large values (450) exactly where the edge is** and zeros where the image is uniform.
- Where the filter sees the same values on left and right (all 200s or all 50s), the result is zero because positive and negative values cancel out.
- Where the filter sits right on the edge (200 on left, 50 on right), the result is large because the filter amplifies the difference.

```
Why the Edge Shows Up:

  When filter is on uniform area (all 200s):
    (200x1) + (200x0) + (200x-1) = 200 - 200 = 0  (per row)
    Total = 0 + 0 + 0 = 0    <- No edge detected

  When filter straddles the edge (200 on left, 50 on right):
    (200x1) + (200x0) + (50x-1) = 200 - 50 = 150  (per row)
    Total = 150 + 150 + 150 = 450    <- Edge detected!

  The filter acts like a "difference detector."
  Big output = big difference = edge found.
```

---

## Feature Maps

The output of a convolution operation is called a **feature map** (also known as an activation map). It shows where a particular pattern was found in the image.

### Understanding Feature Maps

Think of a feature map like a heat map. Bright spots (high values) mean "I found the pattern here!" Dark spots (low or zero values) mean "No pattern here."

```
Input Image           Vertical Edge Filter        Feature Map
+----------+         +---+---+---+               +--------+
|          |         | 1 | 0 |-1 |               |        |
|  Bright  | Dark    | 1 | 0 |-1 |    ------>    | Bright |
|  side    | side    | 1 | 0 |-1 |               | stripe |
|          |         +---+---+---+               | where  |
+----------+                                      | edge   |
                                                   | is     |
An image with a      A filter that detects         +--------+
vertical boundary    vertical edges               High values mark
                                                   the edge location
```

### Multiple Filters Mean Multiple Feature Maps

In a real CNN, we use many filters at the same time. Each filter looks for a different pattern, and each one produces its own feature map.

```python
import numpy as np

# Simple 6x6 image
image = np.array([
    [100, 100, 100, 200, 200, 200],
    [100, 100, 100, 200, 200, 200],
    [100, 100, 100, 200, 200, 200],
    [200, 200, 200, 100, 100, 100],
    [200, 200, 200, 100, 100, 100],
    [200, 200, 200, 100, 100, 100]
])

# Two different filters
vertical_filter = np.array([[ 1, 0, -1],
                             [ 1, 0, -1],
                             [ 1, 0, -1]])

horizontal_filter = np.array([[ 1,  1,  1],
                               [ 0,  0,  0],
                               [-1, -1, -1]])

def convolve(image, kernel):
    """Perform 2D convolution."""
    h = image.shape[0] - kernel.shape[0] + 1
    w = image.shape[1] - kernel.shape[1] + 1
    output = np.zeros((h, w))
    for i in range(h):
        for j in range(w):
            output[i, j] = np.sum(image[i:i+3, j:j+3] * kernel)
    return output

feature_map_1 = convolve(image, vertical_filter)
feature_map_2 = convolve(image, horizontal_filter)

print("Feature map 1 (vertical edges):")
print(feature_map_1)
print("\nFeature map 2 (horizontal edges):")
print(feature_map_2)
```

**Output:**
```
Feature map 1 (vertical edges):
[[-300. -300.    0.  300.]
 [-300. -300.    0.  300.]
 [   0.    0.    0.    0.]
 [ 300.  300.    0. -300.]]

Feature map 2 (horizontal edges):
[[   0.    0.    0.    0.]
 [-300.    0.  300.  300.]
 [-300.    0.  300.  300.]
 [   0.    0.    0.    0.]]
```

**Line-by-line explanation:**

- `def convolve(image, kernel)` defines a reusable function that performs convolution. This saves us from repeating the loop code.
- `feature_map_1` highlights where vertical edges are (columns where brightness changes left-to-right).
- `feature_map_2` highlights where horizontal edges are (rows where brightness changes top-to-bottom).
- Notice how each filter responds to a different pattern. The vertical filter ignores horizontal edges, and vice versa.

---

## Stride: How Far the Filter Moves

By default, the filter slides one pixel at a time. But we can make it skip positions. The number of pixels the filter moves each step is called the **stride**.

### Stride = 1 (Default)

The filter moves one pixel at a time. This produces the most detailed output.

```
Stride = 1: Filter moves 1 pixel each step

  Step 1        Step 2        Step 3
  +--+--+--+    +--+--+--+    +--+--+--+
  |##|##|##|    |  |##|##|##| |  |  |##|##|##|
  +--+--+--+    +--+--+--+    +--+--+--+--+--+
  |##|##|##|    |  |##|##|##|
  +--+--+--+    +--+--+--+
  |##|##|##|    |  |##|##|##|
  +--+--+--+    +--+--+--+

  ## = area covered by filter
  Filter overlaps with previous position
```

### Stride = 2

The filter moves two pixels at a time. This produces a smaller output and is faster to compute.

```
Stride = 2: Filter moves 2 pixels each step

  Step 1            Step 2
  +--+--+--+--+--+  +--+--+--+--+--+
  |##|##|##|  |  |  |  |  |##|##|##|
  +--+--+--+--+--+  +--+--+--+--+--+
  |##|##|##|  |  |  |  |  |##|##|##|
  +--+--+--+--+--+  +--+--+--+--+--+
  |##|##|##|  |  |  |  |  |##|##|##|
  +--+--+--+--+--+  +--+--+--+--+--+
  |  |  |  |  |  |  |  |  |  |  |  |
  +--+--+--+--+--+  +--+--+--+--+--+
  |  |  |  |  |  |  |  |  |  |  |  |
  +--+--+--+--+--+  +--+--+--+--+--+

  Filter skips one position between steps
```

```python
import numpy as np

image = np.array([
    [1, 2, 3, 4, 5],
    [6, 7, 8, 9, 10],
    [11, 12, 13, 14, 15],
    [16, 17, 18, 19, 20],
    [21, 22, 23, 24, 25]
])

kernel = np.array([
    [1, 0, -1],
    [1, 0, -1],
    [1, 0, -1]
])

def convolve_with_stride(image, kernel, stride=1):
    """Perform convolution with a given stride."""
    k_size = kernel.shape[0]
    output_size = (image.shape[0] - k_size) // stride + 1
    output = np.zeros((output_size, output_size))

    for i in range(output_size):
        for j in range(output_size):
            row = i * stride
            col = j * stride
            region = image[row:row+k_size, col:col+k_size]
            output[i, j] = np.sum(region * kernel)

    return output

# Stride 1
output_s1 = convolve_with_stride(image, kernel, stride=1)
print("Stride = 1, output shape:", output_s1.shape)
print(output_s1)

# Stride 2
output_s2 = convolve_with_stride(image, kernel, stride=2)
print("\nStride = 2, output shape:", output_s2.shape)
print(output_s2)
```

**Output:**
```
Stride = 1, output shape: (3, 3)
[[ -6.  -6.  -6.]
 [ -6.  -6.  -6.]
 [ -6.  -6.  -6.]]

Stride = 2, output shape: (2, 2)
[[ -6.  -6.]
 [ -6.  -6.]]
```

**Line-by-line explanation:**

- `output_size = (image.shape[0] - k_size) // stride + 1` calculates the output size. With stride 2, the output is smaller because the filter takes bigger jumps.
- `row = i * stride` and `col = j * stride` calculate where to place the filter. With stride 2, the filter moves to positions 0, 2, 4, etc. instead of 0, 1, 2, 3, etc.
- Stride 1 gives us a 3x3 output. Stride 2 gives us a 2x2 output. Larger stride means smaller, faster output.

```
Output Size Formula:

  output_size = (input_size - filter_size) / stride + 1

  Examples with a 5x5 image and 3x3 filter:
    Stride 1: (5 - 3) / 1 + 1 = 3   -> 3x3 output
    Stride 2: (5 - 3) / 2 + 1 = 2   -> 2x2 output
```

---

## Padding: Keeping the Edges

You may have noticed that the output of convolution is always smaller than the input. A 5x5 image with a 3x3 filter gives a 3x3 output. We lose 2 pixels from each dimension.

This is a problem because:
1. The output shrinks after each convolution layer
2. Pixels at the edges are used in fewer calculations than center pixels, so we lose edge information

**Padding** solves this by adding extra pixels (usually zeros) around the border of the image before applying the filter.

### Zero Padding

The most common type of padding adds zeros around the image border.

```
Original 5x5 Image:         After Padding = 1 (7x7 Image):

+---+---+---+---+---+       +---+---+---+---+---+---+---+
| 1 | 2 | 3 | 0 | 1 |       | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
+---+---+---+---+---+       +---+---+---+---+---+---+---+
| 4 | 5 | 6 | 1 | 2 |       | 0 | 1 | 2 | 3 | 0 | 1 | 0 |
+---+---+---+---+---+       +---+---+---+---+---+---+---+
| 7 | 8 | 9 | 2 | 0 |       | 0 | 4 | 5 | 6 | 1 | 2 | 0 |
+---+---+---+---+---+       +---+---+---+---+---+---+---+
| 2 | 3 | 1 | 5 | 4 |       | 0 | 7 | 8 | 9 | 2 | 0 | 0 |
+---+---+---+---+---+       +---+---+---+---+---+---+---+
| 1 | 0 | 2 | 3 | 6 |       | 0 | 2 | 3 | 1 | 5 | 4 | 0 |
+---+---+---+---+---+       +---+---+---+---+---+---+---+
                              | 0 | 1 | 0 | 2 | 3 | 6 | 0 |
                              +---+---+---+---+---+---+---+
                              | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
                              +---+---+---+---+---+---+---+

                              Zeros added around all edges
```

### Types of Padding

- **"Valid" padding (padding=0):** No padding. Output is smaller than input. This is the default.
- **"Same" padding (padding=1 for a 3x3 filter):** Enough padding so the output has the same size as the input.

```python
import numpy as np

image = np.array([
    [1, 2, 3, 0, 1],
    [4, 5, 6, 1, 2],
    [7, 8, 9, 2, 0],
    [2, 3, 1, 5, 4],
    [1, 0, 2, 3, 6]
])

kernel = np.array([
    [1, 0, -1],
    [1, 0, -1],
    [1, 0, -1]
])

def convolve_with_padding(image, kernel, padding=0):
    """Perform convolution with zero padding."""
    if padding > 0:
        # Add zeros around the image
        padded = np.pad(image, padding, mode='constant', constant_values=0)
    else:
        padded = image

    k_size = kernel.shape[0]
    output_h = padded.shape[0] - k_size + 1
    output_w = padded.shape[1] - k_size + 1
    output = np.zeros((output_h, output_w))

    for i in range(output_h):
        for j in range(output_w):
            region = padded[i:i+k_size, j:j+k_size]
            output[i, j] = np.sum(region * kernel)

    return output

# No padding (valid)
output_valid = convolve_with_padding(image, kernel, padding=0)
print("No padding - output shape:", output_valid.shape)
print(output_valid)

# Padding = 1 (same)
output_same = convolve_with_padding(image, kernel, padding=1)
print("\nPadding = 1 - output shape:", output_same.shape)
print(output_same)
```

**Output:**
```
No padding - output shape: (3, 3)
[[ -6.  -2.   2.]
 [ -3.   3.   3.]
 [  6.  -2. -12.]]

Padding = 1 - output shape: (5, 5)
[[  5.   3.  -3.  -1.  -3.]
 [  5.  -6.  -2.   2.  -3.]
 [ 11.  -3.   3.   3.  -2.]
 [  3.   6.  -2. -12.  -8.]
 [  1.   3.  -2.  -9. -10.]]
```

**Line-by-line explanation:**

- `np.pad(image, padding, mode='constant', constant_values=0)` adds a border of zeros around the image. With padding=1, one row/column of zeros is added on each side, turning a 5x5 image into a 7x7 image.
- Without padding, the 5x5 image becomes a 3x3 output (shrinks by 2).
- With padding=1, the 5x5 image becomes a 5x5 output (same size preserved).
- The added zeros do not change the meaningful content of the image, but they allow the filter to be applied at the edges.

```
Output Size Formula with Padding:

  output_size = (input_size + 2 * padding - filter_size) / stride + 1

  For "same" padding (output = input size):
    padding = (filter_size - 1) / 2

  Examples with 5x5 image, 3x3 filter, stride 1:
    padding=0: (5 + 0 - 3)/1 + 1 = 3   (smaller)
    padding=1: (5 + 2 - 3)/1 + 1 = 5   (same size)
```

---

## Putting It All Together with PyTorch

Now let us see how PyTorch handles convolution. PyTorch does all the heavy lifting for us.

```python
import torch
import torch.nn.functional as F

# Create a 5x5 image as a PyTorch tensor
# PyTorch expects shape: (batch, channels, height, width)
image = torch.tensor([
    [1.0, 2.0, 3.0, 0.0, 1.0],
    [4.0, 5.0, 6.0, 1.0, 2.0],
    [7.0, 8.0, 9.0, 2.0, 0.0],
    [2.0, 3.0, 1.0, 5.0, 4.0],
    [1.0, 0.0, 2.0, 3.0, 6.0]
]).unsqueeze(0).unsqueeze(0)  # Add batch and channel dimensions

# Create a vertical edge detection filter
# Shape: (out_channels, in_channels, height, width)
kernel = torch.tensor([
    [1.0, 0.0, -1.0],
    [1.0, 0.0, -1.0],
    [1.0, 0.0, -1.0]
]).unsqueeze(0).unsqueeze(0)

print("Image shape:", image.shape)
print("Kernel shape:", kernel.shape)

# Apply convolution with no padding
output_valid = F.conv2d(image, kernel, padding=0)
print("\nNo padding output:")
print(output_valid)
print("Output shape:", output_valid.shape)

# Apply convolution with padding=1
output_same = F.conv2d(image, kernel, padding=1)
print("\nPadding=1 output:")
print(output_same)
print("Output shape:", output_same.shape)

# Apply convolution with stride=2
output_stride2 = F.conv2d(image, kernel, padding=0, stride=2)
print("\nStride=2 output:")
print(output_stride2)
print("Output shape:", output_stride2.shape)
```

**Output:**
```
Image shape: torch.Size([1, 1, 5, 5])
Kernel shape: torch.Size([1, 1, 3, 3])

No padding output:
tensor([[[[ -6.,  -2.,   2.],
          [ -3.,   3.,   3.],
          [  6.,  -2., -12.]]]])
Output shape: torch.Size([1, 1, 3, 3])

Padding=1 output:
tensor([[[[  5.,   3.,  -3.,  -1.,  -3.],
          [  5.,  -6.,  -2.,   2.,  -3.],
          [ 11.,  -3.,   3.,   3.,  -2.],
          [  3.,   6.,  -2., -12.,  -8.],
          [  1.,   3.,  -2.,  -9., -10.]]]])
Output shape: torch.Size([1, 1, 5, 5])

Stride=2 output:
tensor([[[[-6.,  2.],
          [ 6., -12.]]]])
Output shape: torch.Size([1, 1, 2, 2])
```

**Line-by-line explanation:**

- `.unsqueeze(0).unsqueeze(0)` adds two extra dimensions. PyTorch requires images to have 4 dimensions: (batch_size, channels, height, width). The batch dimension lets us process multiple images at once, and the channel dimension handles color channels.
- `F.conv2d(image, kernel, padding=0)` performs 2D convolution. This is the same operation we did manually, but PyTorch handles it much faster, especially on GPUs.
- The output shape `[1, 1, 3, 3]` means: 1 image in the batch, 1 output channel (one filter), 3x3 spatial dimensions.
- With `padding=1`, the output matches the input size (5x5).
- With `stride=2`, the output is smaller (2x2) because the filter takes bigger steps.

---

## Common Mistakes

1. **Confusing filter size with image size.** The filter is always much smaller than the image. A common filter is 3x3 or 5x5, while images can be 224x224 or larger.

2. **Forgetting that convolution shrinks the output.** Without padding, each convolution layer makes the spatial dimensions smaller. After many layers, the output can become very tiny or even vanish.

3. **Mixing up height-width order.** PyTorch uses (channels, height, width) for images and (out_channels, in_channels, height, width) for filters. Getting these dimensions wrong will cause errors.

4. **Thinking filters are designed by hand.** In early computer vision, researchers hand-designed filters. In CNNs, the filter values are learned automatically through training. You only decide the filter size and number of filters.

5. **Forgetting to normalize pixel values.** Raw pixel values range from 0-255, but neural networks work better with values between 0-1 or -1 and 1. Always normalize your images before feeding them to a CNN.

---

## Best Practices

1. **Use odd-sized filters** (3x3, 5x5, 7x7). Odd sizes have a clear center pixel, which makes padding calculations simpler and symmetric.

2. **Start with 3x3 filters.** Modern architectures like VGG and ResNet show that stacking multiple 3x3 filters is more effective than using one large filter. Two 3x3 filters cover the same area as one 5x5 filter but with fewer parameters.

3. **Use "same" padding** when you want to preserve spatial dimensions. This is especially important in the early layers where you do not want to lose edge information too quickly.

4. **Normalize your images** to have values between 0 and 1 (divide by 255) or use standardization (subtract mean, divide by standard deviation).

5. **Use PyTorch's built-in functions** instead of writing convolution loops manually. PyTorch's implementation is optimized for speed and can run on GPUs.

---

## Quick Summary

Images are stored as grids of numbers called pixels. Grayscale images have one number per pixel (0 to 255), while color images have three numbers per pixel (Red, Green, Blue). A filter (or kernel) is a small grid of numbers that slides across the image to detect patterns. The convolution operation multiplies the filter values by the image values in the covered region and sums them up, producing a single number in the output feature map. Edge detection filters find boundaries by looking for places where pixel values change sharply. Stride controls how far the filter moves each step, and padding adds extra pixels around the image border to control the output size.

---

## Key Points

- A pixel is the smallest unit of an image, represented by numbers (0 to 255).
- RGB images have three channels (Red, Green, Blue), each storing brightness values for that color.
- A filter (kernel) is a small grid of learned numbers, typically 3x3, that detects specific patterns.
- Convolution is element-wise multiplication followed by summation, applied as the filter slides across the image.
- A feature map is the output of convolution, showing where a pattern was found.
- Stride is how many pixels the filter moves each step. Larger stride means smaller output.
- Padding adds zeros around the image border. "Same" padding keeps the output size equal to the input size.
- CNNs learn filter values automatically during training through backpropagation.

---

## Practice Questions

1. A grayscale image is 32x32 pixels. How many numbers are needed to store it? What if it is an RGB color image?

2. You apply a 3x3 filter to a 10x10 image with stride 1 and no padding. What is the size of the output feature map?

3. What does a vertical edge detection filter detect? Why does it have positive values on one side and negative values on the other side?

4. You want the output of a convolution to have the same spatial dimensions as the input. The filter size is 5x5 and the stride is 1. What should the padding be?

5. In the convolution operation, what happens when the filter is placed over a region of the image where all pixel values are the same?

---

## Exercises

### Exercise 1: Build Your Own Blur Filter

Create a 3x3 averaging filter where every value is 1/9. Apply it to the following image and observe how it smooths the values:

```python
image = np.array([
    [0,   0,   0,   0,   0],
    [0,   0,   0,   0,   0],
    [0,   0, 255,   0,   0],
    [0,   0,   0,   0,   0],
    [0,   0,   0,   0,   0]
])
```

What does the output look like? Why does the bright center pixel "spread out" in the output?

### Exercise 2: Horizontal Edge Detection

Create an image with a horizontal edge (top half is bright, bottom half is dark). Apply the horizontal edge detection filter and verify that it correctly identifies the edge location. Compare the result to what happens when you apply the vertical edge detection filter to the same image.

### Exercise 3: Experiment with Stride and Padding

Start with a 7x7 image filled with random values. Apply a 3x3 filter with:
- stride=1, padding=0
- stride=1, padding=1
- stride=2, padding=0
- stride=2, padding=1

Record the output size for each combination. Verify your results match the formula: output_size = (input_size + 2*padding - filter_size) / stride + 1.

---

## What Is Next?

Now that you understand how a single convolution operation works, you are ready to learn how multiple convolution layers are stacked together to build a complete CNN architecture. In the next chapter, we will explore how convolution layers, pooling layers, and fully connected layers work together to go from raw pixels to predictions. You will see how early layers detect simple patterns like edges, middle layers detect shapes, and deep layers recognize complex objects.
