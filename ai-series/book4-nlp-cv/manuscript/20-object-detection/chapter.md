# Chapter 20: Object Detection

## What You Will Learn

In this chapter, you will learn:

- What object detection is and how it differs from image classification
- How bounding boxes represent the location of objects
- What IoU (Intersection over Union) is and why it matters
- How YOLO works at a high level (dividing images into a grid)
- How to use YOLOv8 with the ultralytics library for inference
- How to draw bounding boxes on images
- How confidence thresholds filter out weak detections
- What NMS (Non-Maximum Suppression) does and why it is necessary

## Why This Chapter Matters

Image classification answers: "What is in this image?" Object detection answers a harder question: "What objects are in this image, AND where are they?"

This difference is enormous in practice. A self-driving car does not just need to know that there is a pedestrian somewhere in the scene -- it needs to know exactly WHERE the pedestrian is. A security camera does not just need to know that a person entered the frame -- it needs to track their position. A retail system does not just need to know that products are on a shelf -- it needs to know which product is where.

Object detection is one of the most commercially valuable skills in computer vision. It powers autonomous vehicles, medical imaging, warehouse robotics, sports analytics, wildlife monitoring, and hundreds of other applications. Understanding it opens up a whole new class of problems you can solve.

---

## 20.1 Classification vs. Detection vs. Segmentation

Let us clearly distinguish three levels of understanding an image:

```
Image Classification:
+---------------------------+
|                           |
|       "dog"               |    One label for the entire image
|                           |
+---------------------------+

Object Detection:
+---------------------------+
|        +------+           |
|        | dog  |  +-----+  |    Find objects AND their locations
|        +------+  | cat |  |    (bounding boxes)
|                  +-----+  |
+---------------------------+

Instance Segmentation:
+---------------------------+
|       ########            |
|       # dog  #  #####     |    Exact pixel-by-pixel outline
|       ########  # cat#    |    of each object
|                 #####     |
+---------------------------+
```

```
What each task outputs:

Classification:  "dog"  (just a label)

Detection:       [
                   {"label": "dog",  "box": [x1, y1, x2, y2], "conf": 0.95},
                   {"label": "cat",  "box": [x1, y1, x2, y2], "conf": 0.87},
                 ]

Each detection has:
  - A class label (what)
  - A bounding box (where)
  - A confidence score (how sure)
```

---

## 20.2 Bounding Boxes

A **bounding box** is a rectangle that tightly encloses an object in an image. It is the standard way to represent object locations.

### Bounding Box Formats

There are two common formats for specifying a bounding box:

```
Format 1: Corner format (x1, y1, x2, y2)
  (x1, y1) = top-left corner
  (x2, y2) = bottom-right corner

  (x1,y1)
    +------------------+
    |                  |
    |    OBJECT        |
    |                  |
    +------------------+
                    (x2,y2)

Format 2: Center format (cx, cy, w, h)
  (cx, cy) = center point
  w = width
  h = height

         w
    +------------------+
    |                  |
    |    (cx,cy)       | h
    |       *          |
    +------------------+

YOLO uses center format internally.
Most display libraries use corner format.
```

### Converting Between Formats

```python
def corner_to_center(x1, y1, x2, y2):
    """Convert (x1, y1, x2, y2) to (cx, cy, w, h)."""
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    w = x2 - x1
    h = y2 - y1
    return cx, cy, w, h

def center_to_corner(cx, cy, w, h):
    """Convert (cx, cy, w, h) to (x1, y1, x2, y2)."""
    x1 = cx - w / 2
    y1 = cy - h / 2
    x2 = cx + w / 2
    y2 = cy + h / 2
    return x1, y1, x2, y2

# Example
x1, y1, x2, y2 = 100, 50, 300, 250
cx, cy, w, h = corner_to_center(x1, y1, x2, y2)
print(f"Corner: ({x1}, {y1}, {x2}, {y2})")
print(f"Center: (cx={cx}, cy={cy}, w={w}, h={h})")

# Output:
# Corner: (100, 50, 300, 250)
# Center: (cx=200.0, cy=150.0, w=200, h=200)
```

### Drawing Bounding Boxes

```python
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# === Method 1: Drawing with OpenCV ===
def draw_boxes_opencv(image_path, detections):
    """Draw bounding boxes using OpenCV."""
    image = cv2.imread(image_path)

    for det in detections:
        x1, y1, x2, y2 = det["box"]
        label = det["label"]
        conf = det["confidence"]

        # Draw rectangle
        color = (0, 255, 0)   # Green in BGR
        thickness = 2
        cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)

        # Draw label background
        text = f"{label} {conf:.2f}"
        (text_w, text_h), _ = cv2.getTextSize(
            text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1
        )
        cv2.rectangle(image, (x1, y1 - text_h - 8),
                       (x1 + text_w, y1), color, -1)  # Filled

        # Draw label text
        cv2.putText(image, text, (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (0, 0, 0), 1)  # Black text

    return image

# === Method 2: Drawing with PIL ===
def draw_boxes_pil(image_path, detections):
    """Draw bounding boxes using PIL."""
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    for det in detections:
        x1, y1, x2, y2 = det["box"]
        label = det["label"]
        conf = det["confidence"]

        # Draw rectangle
        draw.rectangle([x1, y1, x2, y2], outline="green", width=3)

        # Draw label
        text = f"{label} {conf:.2f}"
        draw.text((x1, y1 - 15), text, fill="green")

    return image

# Example usage
detections = [
    {"label": "dog", "box": [100, 50, 300, 250], "confidence": 0.95},
    {"label": "cat", "box": [350, 100, 500, 280], "confidence": 0.87},
]

# result = draw_boxes_pil("photo.jpg", detections)
# result.show()
```

---

## 20.3 IoU (Intersection over Union)

**IoU** (Intersection over Union) measures how much two bounding boxes overlap. It is the standard metric for evaluating object detection.

```
IoU = Area of Overlap / Area of Union

Box A:         Box B:         Overlap:       Union:
+--------+                   +----+         +--------+---+
|        |   +--------+      |    |         |        |   |
|   A    |   |        |      |    |         |   A    | B |
|     +--+---+--+     |      +----+         |     +--+---+--+
|     |  |   |  |     |   (intersection)    |     |        |
+-----+--+   |  B     |                     +-----+--------+
      |      |        |                          (union)
      +------+--------+

IoU = intersection area / union area
```

### Computing IoU

```python
def compute_iou(box1, box2):
    """
    Compute IoU between two boxes.
    Each box is [x1, y1, x2, y2].
    """
    # Find the intersection rectangle
    x1 = max(box1[0], box2[0])  # Left edge of intersection
    y1 = max(box1[1], box2[1])  # Top edge of intersection
    x2 = min(box1[2], box2[2])  # Right edge of intersection
    y2 = min(box1[3], box2[3])  # Bottom edge of intersection

    # Calculate intersection area
    intersection = max(0, x2 - x1) * max(0, y2 - y1)

    # Calculate union area
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = area1 + area2 - intersection

    # Compute IoU
    iou = intersection / union if union > 0 else 0
    return iou

# Example 1: Boxes overlap significantly
box1 = [100, 100, 300, 300]   # 200x200 = 40000 pixels
box2 = [150, 150, 350, 350]   # 200x200 = 40000 pixels
print(f"IoU: {compute_iou(box1, box2):.4f}")
# Output: IoU: 0.3913

# Example 2: Boxes are identical (perfect match)
box3 = [100, 100, 300, 300]
box4 = [100, 100, 300, 300]
print(f"IoU (identical): {compute_iou(box3, box4):.4f}")
# Output: IoU (identical): 1.0000

# Example 3: Boxes do not overlap at all
box5 = [0, 0, 100, 100]
box6 = [200, 200, 300, 300]
print(f"IoU (no overlap): {compute_iou(box5, box6):.4f}")
# Output: IoU (no overlap): 0.0000
```

**Line-by-line explanation:**

- `max(box1[0], box2[0])`: The left edge of the intersection is the rightmost left edge of the two boxes.
- `min(box1[2], box2[2])`: The right edge of the intersection is the leftmost right edge.
- `max(0, x2 - x1)`: If the boxes do not overlap, x2 - x1 will be negative. `max(0, ...)` ensures we get 0 instead of a negative area.
- `area1 + area2 - intersection`: The union is both areas combined, minus the intersection (which was counted twice).

### IoU Thresholds in Practice

```
IoU Value    Interpretation
---------------------------------
0.0          No overlap at all
0.1 - 0.3    Slight overlap, poor match
0.3 - 0.5    Moderate overlap
0.5+         Good match (common threshold for "correct")
0.75+        Very good match (stricter evaluation)
1.0          Perfect overlap (identical boxes)

Standard COCO evaluation uses IoU = 0.5
(a detection with IoU >= 0.5 with ground truth
is considered "correct")
```

---

## 20.4 How YOLO Works

**YOLO** stands for **You Only Look Once**. It is one of the most popular object detection algorithms because it is fast and accurate.

### The Key Idea: Grid-Based Detection

Instead of scanning every possible location (which is slow), YOLO divides the image into a grid and predicts objects for each grid cell simultaneously:

```
YOLO Grid Approach:

Original Image:              YOLO Grid (e.g., 7x7):
+------------------------+   +--+--+--+--+--+--+--+
|                        |   |  |  |  |  |  |  |  |
|      +------+          |   +--+--+--+--+--+--+--+
|      | dog  |          |   |  |  |##|##|  |  |  |
|      +------+          |   +--+--+--+--+--+--+--+
|                        |   |  |  |##|##|  |  |  |
|             +-----+    |   +--+--+--+--+--+--+--+
|             | cat |    |   |  |  |  |  |  |  |  |
|             +-----+    |   +--+--+--+--+--+--+--+
+------------------------+   |  |  |  |  |##|##|  |
                              +--+--+--+--+--+--+--+
                              |  |  |  |  |##|##|  |
                              +--+--+--+--+--+--+--+
                              |  |  |  |  |  |  |  |
                              +--+--+--+--+--+--+--+

## = Grid cells responsible for detecting objects
     (the cell containing the object's center)
```

### What Each Grid Cell Predicts

Each grid cell predicts:
1. **Bounding boxes** (position and size)
2. **Confidence scores** (is there an object here?)
3. **Class probabilities** (if there is an object, what class is it?)

```
One Grid Cell Predicts:

+----------------------------------+
| Bounding Box 1:                  |
|   (cx, cy, w, h, confidence)    |
|                                  |
| Bounding Box 2:                  |
|   (cx, cy, w, h, confidence)    |
|                                  |
| Class Probabilities:             |
|   P(dog)=0.8, P(cat)=0.1, ...  |
+----------------------------------+

Total output per cell:
  B boxes * 5 values + C classes
  where B = number of boxes per cell
        C = number of classes
```

### Why "You Only Look Once"?

```
Traditional Detection (R-CNN):
  1. Propose ~2000 regions
  2. Classify each region individually
  3. Very slow (seconds per image)

  Image -> [Region 1] -> CNN -> "dog"
        -> [Region 2] -> CNN -> "background"
        -> [Region 3] -> CNN -> "cat"
        -> ...2000 times...

YOLO:
  1. Pass the ENTIRE image through the network ONCE
  2. Get ALL detections simultaneously
  3. Very fast (milliseconds per image)

  Image -> CNN -> Grid of predictions -> All detections at once!

YOLO is 100-1000x faster than R-CNN approaches.
```

### YOLO Evolution

```
Version    Year    Key Innovation
------------------------------------------
YOLOv1     2016    Original grid-based approach
YOLOv2     2017    Anchor boxes, batch norm
YOLOv3     2018    Multi-scale detection
YOLOv4     2020    Bag of freebies, CSP backbone
YOLOv5     2020    PyTorch implementation, easy to use
YOLOv8     2023    State-of-the-art, anchor-free
YOLOv11    2024    Latest, improved performance

We will use YOLOv8 (via the ultralytics library)
because it is modern, fast, and very easy to use.
```

---

## 20.5 Using YOLOv8 with Ultralytics

The **ultralytics** library makes using YOLO incredibly easy -- just a few lines of code.

### Installation

```python
# Install ultralytics
# Run in your terminal:
# pip install ultralytics
```

### Basic Inference

```python
from ultralytics import YOLO

# Load a pretrained YOLOv8 model
# 'yolov8n' = nano (smallest, fastest)
# 'yolov8s' = small
# 'yolov8m' = medium
# 'yolov8l' = large
# 'yolov8x' = extra large (most accurate, slowest)
model = YOLO("yolov8n.pt")

# Run inference on an image
results = model("street_scene.jpg")

# Print results
for result in results:
    print(f"Found {len(result.boxes)} objects")
    print(f"Image shape: {result.orig_shape}")

# Output:
# Found 8 objects
# Image shape: (720, 1280)
```

**Line-by-line explanation:**

- `YOLO("yolov8n.pt")`: Downloads and loads the YOLOv8 nano model. On the first run, it downloads the model weights (~6MB). The "n" suffix means nano -- the smallest and fastest variant.
- `model("street_scene.jpg")`: Runs detection on the image. It handles all preprocessing internally (resize, normalize, etc.).
- `result.boxes`: Contains all detected bounding boxes with their class labels and confidence scores.

### Exploring Detection Results

```python
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
results = model("street_scene.jpg")

# Get the first result (one per image)
result = results[0]

# Access bounding boxes
boxes = result.boxes

print(f"Number of detections: {len(boxes)}")
print(f"Box coordinates (xyxy format):\n{boxes.xyxy}")
print(f"Confidence scores:\n{boxes.conf}")
print(f"Class indices:\n{boxes.cls}")

# Output:
# Number of detections: 8
# Box coordinates (xyxy format):
# tensor([[ 218.2,  267.8,  428.5,  525.3],
#         [ 612.4,  281.1,  785.2,  518.7],
#         ...])
# Confidence scores:
# tensor([0.9234, 0.8876, 0.8543, ...])
# Class indices:
# tensor([0., 0., 2., ...])

# Get class names
print(f"\nDetailed results:")
for i in range(len(boxes)):
    x1, y1, x2, y2 = boxes.xyxy[i].tolist()
    confidence = boxes.conf[i].item()
    class_id = int(boxes.cls[i].item())
    class_name = model.names[class_id]

    print(f"  {class_name:12s} conf={confidence:.3f} "
          f"box=({x1:.0f}, {y1:.0f}, {x2:.0f}, {y2:.0f})")

# Output:
# Detailed results:
#   person       conf=0.923 box=(218, 268, 429, 525)
#   person       conf=0.888 box=(612, 281, 785, 519)
#   car          conf=0.854 box=(0, 320, 215, 520)
#   ...
```

**Line-by-line explanation:**

- `boxes.xyxy`: Bounding boxes in (x1, y1, x2, y2) corner format. Each row is one detection.
- `boxes.conf`: Confidence score for each detection (0 to 1). Higher means the model is more certain.
- `boxes.cls`: Class index for each detection. Use `model.names[class_id]` to get the human-readable name.
- `model.names`: A dictionary mapping class indices to class names. YOLOv8 trained on COCO has 80 classes (person, car, dog, etc.).

### COCO Class Names

YOLOv8 pretrained models are trained on the COCO dataset which has 80 object classes:

```python
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

# Print all 80 class names
for idx, name in model.names.items():
    print(f"  {idx:3d}: {name}")

# Output (abbreviated):
#   0: person
#   1: bicycle
#   2: car
#   3: motorcycle
#   ...
#  14: bird
#  15: cat
#  16: dog
#   ...
#  79: toothbrush
```

---

## 20.6 Running Inference on Images

### Single Image Inference

```python
from ultralytics import YOLO
from PIL import Image
import matplotlib.pyplot as plt

model = YOLO("yolov8n.pt")

# Run detection
results = model("photo.jpg")

# Method 1: Use built-in visualization
result = results[0]
annotated_image = result.plot()   # Returns BGR NumPy array with boxes drawn

# Convert BGR to RGB for matplotlib
import cv2
annotated_rgb = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)

plt.figure(figsize=(12, 8))
plt.imshow(annotated_rgb)
plt.title(f"YOLOv8 Detection: {len(result.boxes)} objects found")
plt.axis("off")
plt.show()
```

**Line-by-line explanation:**

- `result.plot()`: Automatically draws all bounding boxes, labels, and confidence scores on the image. Returns a BGR NumPy array.
- We convert to RGB for matplotlib display (same BGR/RGB issue from Chapter 16).

### Batch Inference on Multiple Images

```python
from ultralytics import YOLO
import os

model = YOLO("yolov8n.pt")

# Process multiple images at once
image_paths = ["photo1.jpg", "photo2.jpg", "photo3.jpg"]
results = model(image_paths)

# Process each result
for i, result in enumerate(results):
    print(f"\nImage: {image_paths[i]}")
    print(f"  Objects found: {len(result.boxes)}")

    for box in result.boxes:
        class_name = model.names[int(box.cls)]
        conf = box.conf.item()
        coords = box.xyxy[0].tolist()
        print(f"  {class_name}: {conf:.3f} at "
              f"({coords[0]:.0f},{coords[1]:.0f},"
              f"{coords[2]:.0f},{coords[3]:.0f})")

# Output:
# Image: photo1.jpg
#   Objects found: 3
#   person: 0.923 at (218,268,429,525)
#   car: 0.854 at (0,320,215,520)
#   dog: 0.712 at (500,400,650,550)
#
# Image: photo2.jpg
#   Objects found: 5
#   ...
```

### Inference on a Video (Frame by Frame)

```python
from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")

# Open video
cap = cv2.VideoCapture("video.mp4")

frame_count = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Run detection on each frame
    results = model(frame, verbose=False)
    result = results[0]

    # Draw results
    annotated = result.plot()

    # Count objects in this frame
    num_objects = len(result.boxes)

    frame_count += 1
    if frame_count % 30 == 0:  # Print every 30 frames
        print(f"Frame {frame_count}: {num_objects} objects detected")

    # Display (in a GUI environment)
    # cv2.imshow("Detection", annotated)
    # if cv2.waitKey(1) & 0xFF == ord("q"):
    #     break

cap.release()
print(f"Processed {frame_count} frames")
```

---

## 20.7 Confidence Thresholds

The **confidence threshold** controls which detections are kept. Detections with confidence below the threshold are discarded.

```
Confidence Threshold:

All detections (no threshold):
  person  0.95  <- Keep
  car     0.82  <- Keep
  dog     0.45  <- Maybe?
  cat     0.12  <- Probably wrong
  chair   0.03  <- Almost certainly wrong

With threshold = 0.5:
  person  0.95  <- KEEP (above 0.5)
  car     0.82  <- KEEP (above 0.5)
  dog     0.45  <- DISCARD (below 0.5)
  cat     0.12  <- DISCARD (below 0.5)
  chair   0.03  <- DISCARD (below 0.5)
```

### Setting the Confidence Threshold

```python
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

# Default threshold (usually 0.25)
results_default = model("photo.jpg")
print(f"Default: {len(results_default[0].boxes)} detections")

# Higher threshold = fewer but more confident detections
results_high = model("photo.jpg", conf=0.7)
print(f"conf=0.7: {len(results_high[0].boxes)} detections")

# Lower threshold = more detections, but some might be wrong
results_low = model("photo.jpg", conf=0.1)
print(f"conf=0.1: {len(results_low[0].boxes)} detections")

# Output:
# Default: 8 detections
# conf=0.7: 4 detections
# conf=0.1: 15 detections
```

### Choosing the Right Threshold

```
Threshold Too Low (e.g., 0.1):
  + Catches everything, even hard-to-see objects
  - Lots of false detections (seeing things that are not there)
  Use for: Safety-critical applications (do not miss anything)

Threshold Too High (e.g., 0.9):
  + Very few false detections
  - Misses objects that are partially hidden or far away
  Use for: Applications where false alarms are costly

Good Default (0.25 - 0.5):
  Balanced trade-off between catching objects and avoiding false alarms
  Use for: Most applications

The "right" threshold depends on your specific use case.
There is no universally correct value.
```

### Visualizing Different Thresholds

```python
from ultralytics import YOLO
import matplotlib.pyplot as plt
import cv2

model = YOLO("yolov8n.pt")

thresholds = [0.1, 0.3, 0.5, 0.7]
fig, axes = plt.subplots(1, 4, figsize=(20, 5))

for ax, thresh in zip(axes, thresholds):
    results = model("street_scene.jpg", conf=thresh, verbose=False)
    result = results[0]

    annotated = result.plot()
    annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)

    ax.imshow(annotated_rgb)
    ax.set_title(f"conf={thresh}\n{len(result.boxes)} detections")
    ax.axis("off")

plt.suptitle("Effect of Confidence Threshold", fontsize=14)
plt.tight_layout()
plt.show()
```

**Output:** Four versions of the same image with different numbers of bounding boxes. Lower thresholds show more boxes (including false positives); higher thresholds show fewer, more confident boxes.

---

## 20.8 NMS (Non-Maximum Suppression)

**Non-Maximum Suppression (NMS)** solves a common problem: the model detects the same object multiple times with slightly different bounding boxes.

### The Problem: Duplicate Detections

```
Without NMS:

  +--------+
  | +------+-+
  | | +----+-+-+
  | | |    | | |    Three overlapping boxes
  | | | dog| | |    all detecting the SAME dog
  | | |    | | |
  | | +----+ | |
  | +--------+ |
  +------------+

The model is not wrong -- it detected the dog
from three slightly different positions.
But we want ONE box per dog, not three.
```

### How NMS Works

```
NMS Algorithm:

1. Sort all boxes by confidence score (highest first)
   Box A: dog, conf=0.95
   Box B: dog, conf=0.88
   Box C: dog, conf=0.82
   Box D: cat, conf=0.90

2. Start with the highest confidence box (A)
   Keep Box A.

3. Compare A with every remaining box of the SAME class:
   IoU(A, B) = 0.85 > threshold(0.45) -> REMOVE B (too similar to A)
   IoU(A, C) = 0.78 > threshold(0.45) -> REMOVE C (too similar to A)

4. Move to next remaining box (D is a different class)
   Keep Box D.

5. Result: Box A (dog) and Box D (cat)
   Two clean detections, no duplicates!
```

```
NMS Step by Step:

Step 1: All detections         Step 2: After NMS
+--------+                     +--------+
| +------+-+                   |        |
| | +----+-+-+                 |  dog   |     Only the best
| | |    | | |    --------->   |  0.95  |     box survives
| | | dog| | |                 |        |
| | |    | | |                 +--------+
| | +----+ | |
| +--------+ |                 +------+
+------------+                 | cat  |
     +------+                  | 0.90 |
     | cat  |                  +------+
     +------+
```

### NMS in YOLOv8

YOLOv8 applies NMS automatically. You can control the IoU threshold:

```python
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

# Default NMS IoU threshold is 0.7
results = model("photo.jpg")
print(f"Default NMS: {len(results[0].boxes)} detections")

# Stricter NMS (lower IoU threshold = remove more overlapping boxes)
results_strict = model("photo.jpg", iou=0.3)
print(f"Strict NMS (iou=0.3): {len(results_strict[0].boxes)} detections")

# Lenient NMS (higher IoU threshold = keep more overlapping boxes)
results_lenient = model("photo.jpg", iou=0.9)
print(f"Lenient NMS (iou=0.9): {len(results_lenient[0].boxes)} detections")

# Output:
# Default NMS: 8 detections
# Strict NMS (iou=0.3): 5 detections
# Lenient NMS (iou=0.9): 12 detections
```

**Line-by-line explanation:**

- `iou=0.3`: Any two boxes with IoU above 0.3 are considered duplicates. Only the higher-confidence one survives. This is strict -- it removes more boxes.
- `iou=0.9`: Boxes must overlap by 90% to be considered duplicates. This is lenient -- it keeps more boxes, allowing nearby detections.

```
NMS IoU Threshold:

Low (0.3): Aggressive filtering.
  Keeps fewer boxes. Good when objects
  are well-separated.

Default (0.5-0.7): Balanced.
  Works well for most scenarios.

High (0.9): Minimal filtering.
  Keeps many overlapping boxes. Useful
  when objects are densely packed
  (e.g., a crowd of people).
```

### Implementing NMS from Scratch (for Understanding)

```python
import numpy as np

def nms(boxes, scores, iou_threshold=0.5):
    """
    Non-Maximum Suppression.

    Args:
        boxes: array of [x1, y1, x2, y2] shape (N, 4)
        scores: array of confidence scores shape (N,)
        iou_threshold: IoU threshold for suppression

    Returns:
        indices of boxes to keep
    """
    # Sort by confidence (descending)
    order = scores.argsort()[::-1]

    keep = []

    while len(order) > 0:
        # Keep the highest confidence box
        current = order[0]
        keep.append(current)

        if len(order) == 1:
            break

        # Compare with remaining boxes
        remaining = order[1:]
        ious = np.array([
            compute_iou(boxes[current], boxes[r])
            for r in remaining
        ])

        # Keep boxes with low IoU (they detect different objects)
        mask = ious < iou_threshold
        order = remaining[mask]

    return keep

# Example
boxes = np.array([
    [100, 100, 300, 300],  # Box 0
    [110, 110, 310, 310],  # Box 1 (overlaps with 0)
    [105, 105, 305, 305],  # Box 2 (overlaps with 0)
    [400, 400, 550, 550],  # Box 3 (separate object)
])
scores = np.array([0.95, 0.88, 0.82, 0.90])

kept = nms(boxes, scores, iou_threshold=0.5)
print(f"Kept box indices: {kept}")
print(f"Kept {len(kept)} out of {len(boxes)} boxes")
# Output:
# Kept box indices: [0, 3]
# Kept 2 out of 4 boxes
# (Boxes 1 and 2 were suppressed because they
#  overlapped too much with the higher-confidence Box 0)
```

---

## 20.9 Complete Detection Pipeline

Here is a complete, end-to-end object detection script:

```python
from ultralytics import YOLO
import cv2
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

def detect_objects(image_path, model_size="yolov8n.pt",
                   conf_threshold=0.25, iou_threshold=0.7):
    """
    Complete object detection pipeline.

    Args:
        image_path: Path to the image
        model_size: YOLO model variant
        conf_threshold: Minimum confidence to keep a detection
        iou_threshold: IoU threshold for NMS

    Returns:
        List of detections and annotated image
    """
    # Load model
    model = YOLO(model_size)

    # Run detection
    results = model(
        image_path,
        conf=conf_threshold,
        iou=iou_threshold,
        verbose=False
    )

    result = results[0]
    boxes = result.boxes

    # Extract detections
    detections = []
    for i in range(len(boxes)):
        det = {
            "class_id": int(boxes.cls[i].item()),
            "class_name": model.names[int(boxes.cls[i].item())],
            "confidence": boxes.conf[i].item(),
            "bbox": boxes.xyxy[i].tolist(),  # [x1, y1, x2, y2]
        }
        detections.append(det)

    # Sort by confidence
    detections.sort(key=lambda x: x["confidence"], reverse=True)

    # Get annotated image
    annotated = result.plot()
    annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)

    return detections, annotated_rgb

def print_detection_summary(detections):
    """Print a summary of detections."""
    print(f"\n{'='*50}")
    print(f"Detection Summary: {len(detections)} objects found")
    print(f"{'='*50}")

    # Count by class
    class_counts = Counter(d["class_name"] for d in detections)
    print(f"\nObject counts:")
    for name, count in class_counts.most_common():
        print(f"  {name}: {count}")

    # Detailed list
    print(f"\nDetailed detections:")
    for i, det in enumerate(detections):
        x1, y1, x2, y2 = det["bbox"]
        w = x2 - x1
        h = y2 - y1
        print(f"  [{i+1}] {det['class_name']:12s} "
              f"conf={det['confidence']:.3f} "
              f"size={w:.0f}x{h:.0f} "
              f"at ({x1:.0f},{y1:.0f})")

def display_results(image_path, annotated_image, detections):
    """Display original and annotated images side by side."""
    original = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    ax1.imshow(original)
    ax1.set_title("Original Image")
    ax1.axis("off")

    ax2.imshow(annotated_image)
    ax2.set_title(f"Detections ({len(detections)} objects)")
    ax2.axis("off")

    plt.tight_layout()
    plt.show()

# === Run the pipeline ===
detections, annotated = detect_objects(
    "street_scene.jpg",
    conf_threshold=0.3,
    iou_threshold=0.5
)

print_detection_summary(detections)
display_results("street_scene.jpg", annotated, detections)

# Output:
# ==================================================
# Detection Summary: 8 objects found
# ==================================================
#
# Object counts:
#   person: 3
#   car: 2
#   dog: 1
#   bicycle: 1
#   traffic light: 1
#
# Detailed detections:
#   [1] person       conf=0.954 size=211x257 at (218,268)
#   [2] car          conf=0.912 size=215x200 at (0,320)
#   [3] person       conf=0.888 size=173x238 at (612,281)
#   ...
```

---

## 20.10 Filtering Detections by Class

Often you only care about specific object types:

```python
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

# Detect only specific classes
# Use class indices from model.names
# 0 = person, 2 = car, 16 = dog

# Method 1: Filter using the classes parameter
results = model("street_scene.jpg", classes=[0, 2])  # Only people and cars
print(f"People and cars: {len(results[0].boxes)} detections")

# Method 2: Filter after detection
results_all = model("street_scene.jpg")
all_boxes = results_all[0].boxes

# Keep only "person" detections
person_mask = all_boxes.cls == 0
person_boxes = all_boxes[person_mask]
print(f"People only: {len(person_boxes)} detections")

# Keep only detections with confidence > 0.8
high_conf_mask = all_boxes.conf > 0.8
high_conf_boxes = all_boxes[high_conf_mask]
print(f"High confidence: {len(high_conf_boxes)} detections")

# Output:
# People and cars: 5 detections
# People only: 3 detections
# High confidence: 4 detections
```

---

## 20.11 Choosing the Right YOLO Model

```python
from ultralytics import YOLO
import time

# Compare model sizes
model_variants = ["yolov8n.pt", "yolov8s.pt", "yolov8m.pt"]

for variant in model_variants:
    model = YOLO(variant)

    # Warm up
    model("photo.jpg", verbose=False)

    # Time inference
    start = time.time()
    for _ in range(10):
        results = model("photo.jpg", verbose=False)
    avg_time = (time.time() - start) / 10

    num_detections = len(results[0].boxes)
    print(f"{variant:12s}: {avg_time*1000:.1f}ms, "
          f"{num_detections} detections")

# Typical output:
# yolov8n.pt  :  12.3ms, 7 detections
# yolov8s.pt  :  28.5ms, 9 detections
# yolov8m.pt  :  65.2ms, 10 detections
```

```
Model Selection Guide:

Model     Params   Speed      Accuracy    Best For
------------------------------------------------------
yolov8n   3.2M     Fastest    Good        Real-time, mobile
yolov8s   11.2M    Fast       Better      Edge devices, drones
yolov8m   25.9M    Medium     Very Good   Desktop applications
yolov8l   43.7M    Slower     Excellent   Server-side processing
yolov8x   68.2M    Slowest    Best        Maximum accuracy

Rule of thumb:
  - Start with 'n' (nano) for prototyping
  - Use 's' or 'm' for production
  - Use 'l' or 'x' only when accuracy is critical
    and speed does not matter
```

---

## Common Mistakes

1. **Not adjusting confidence thresholds for your use case.** The default threshold works for general use, but safety-critical applications need lower thresholds (catch everything), while precision-critical applications need higher thresholds (only confident detections).

2. **Ignoring NMS settings when objects are densely packed.** If you are detecting people in a crowd, the default NMS might suppress valid detections because they overlap. Increase the IoU threshold.

3. **Forgetting BGR to RGB conversion when displaying OpenCV images.** YOLO's `result.plot()` returns BGR. Always convert before displaying with matplotlib.

4. **Using the wrong model size.** Starting with yolov8x for a prototype wastes time. Start with yolov8n, get the pipeline working, then upgrade if needed.

5. **Confusing class indices across different models.** COCO class indices are standard for pretrained YOLO, but custom-trained models will have different class mappings. Always check `model.names`.

6. **Not handling empty detections.** Some images have no objects above the confidence threshold. Always check `if len(result.boxes) > 0` before processing detections.

---

## Best Practices

1. **Start with yolov8n for prototyping.** It is fast enough for interactive development and accurate enough to validate your pipeline.

2. **Tune confidence and NMS thresholds for your specific application.** Test different values on a validation set and pick the ones that give the best trade-off.

3. **Filter by class when you only care about specific objects.** Using the `classes` parameter is faster than detecting everything and filtering afterward.

4. **Save detection results in a structured format** (JSON or CSV) for later analysis. Include image path, class, confidence, and bounding box coordinates.

5. **Always visualize results on sample images** before deploying. Seeing the boxes drawn on images reveals problems that metrics alone cannot show.

---

## Quick Summary

Object detection finds and locates objects in images using bounding boxes. Each detection includes a class label, a bounding box (position and size), and a confidence score. IoU (Intersection over Union) measures how well a predicted box matches the ground truth. YOLO divides the image into a grid and predicts all objects in a single forward pass, making it very fast. YOLOv8 via the ultralytics library provides an easy-to-use interface for detection. Confidence thresholds filter out weak detections, and NMS (Non-Maximum Suppression) removes duplicate detections of the same object.

---

## Key Points

- Object detection answers "what AND where" -- it finds objects and draws bounding boxes around them.
- Bounding boxes can be in corner format (x1, y1, x2, y2) or center format (cx, cy, w, h).
- IoU measures overlap between two boxes: 0 = no overlap, 1 = perfect match. IoU >= 0.5 is typically considered a correct detection.
- YOLO processes the entire image in one pass (hence "You Only Look Once"), making it much faster than region-based methods.
- YOLOv8 via ultralytics requires just two lines: `model = YOLO("yolov8n.pt")` and `results = model("image.jpg")`.
- Confidence threshold controls the precision-recall trade-off. Lower = more detections (including false ones). Higher = fewer but more reliable detections.
- NMS removes duplicate detections of the same object by keeping only the highest-confidence box among overlapping boxes.

---

## Practice Questions

1. What are the three pieces of information that an object detection model outputs for each detected object?

2. Two bounding boxes have an IoU of 0.6. What does this mean visually? Would an NMS algorithm with `iou_threshold=0.5` keep both boxes or remove one?

3. You are building a system to detect pedestrians for a self-driving car. Should you use a high or low confidence threshold? Explain why.

4. Explain in simple terms how YOLO detects objects differently from a sliding-window approach. Why is YOLO faster?

5. You run YOLO on an image and get 15 detections. After increasing the confidence threshold from 0.25 to 0.7, you get 6 detections. What happened to the other 9? Were they necessarily wrong?

---

## Exercises

### Exercise 1: Object Counter

Write a script that:
1. Takes an image path as input
2. Runs YOLOv8 detection
3. Counts the number of each object type detected
4. Prints a table showing object type and count
5. Saves the annotated image to disk

### Exercise 2: IoU Calculator and Visualizer

Write a program that:
1. Takes two bounding boxes as input
2. Calculates their IoU
3. Draws both boxes on a blank image (different colors)
4. Shades the intersection area
5. Displays the IoU value as the title

Test with boxes that have IoU = 0 (no overlap), IoU around 0.5, and IoU = 1.0 (identical boxes).

### Exercise 3: Confidence Threshold Analyzer

Write a script that:
1. Runs YOLOv8 on an image with confidence thresholds from 0.1 to 0.9 (step 0.1)
2. For each threshold, records the number of detections
3. Plots a line graph: x-axis = threshold, y-axis = number of detections
4. Identifies the "elbow point" where increasing the threshold starts to dramatically reduce detections

---

## What Is Next?

Congratulations! You have now covered the core building blocks of computer vision: understanding images (Chapter 16), preprocessing them (Chapter 17), classifying them with CNNs (Chapter 18), leveraging transfer learning (Chapter 19), and detecting objects with YOLO (Chapter 20). These skills form a solid foundation for tackling real-world computer vision problems. From here, you can explore more advanced topics like image segmentation (labeling every pixel), pose estimation (detecting body positions), or training custom YOLO models on your own datasets. The fundamentals you have learned will serve you well in all of these directions.
