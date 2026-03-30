# Chapter 28: Project — Object Detection System

## What You Will Learn

- How to use YOLOv8 for object detection inference on images
- How to draw custom bounding boxes and labels on detected objects
- How to filter detections by confidence score and class
- How to save annotated images with detection results
- How to build a complete Gradio web app for object detection
- How to put together a deployable detection system

## Why This Chapter Matters

Image classification tells you WHAT is in an image. Object detection tells you WHAT is in an image AND WHERE it is. This is a much harder and more useful task. Self-driving cars use object detection to find pedestrians, traffic lights, and other cars. Security cameras use it to detect people in restricted areas. Retail stores use it to count products on shelves. Medical imaging uses it to locate tumors in X-rays.

In this final project chapter, you will build a complete object detection system that takes any image, finds all objects in it, draws labeled boxes around them, and presents the results through a clean web interface. This is the capstone of your NLP and Computer Vision journey.

---

## 28.1 Project Overview

```
+------------------------------------------------------------------+
|              Object Detection System Architecture                 |
+------------------------------------------------------------------+
|                                                                   |
|  PART 1: YOLOv8 Inference                                        |
|  +-----------------------------+                                  |
|  | Load pre-trained YOLOv8     |                                 |
|  | Run detection on images     |                                 |
|  | Parse detection results     |                                 |
|  +-----------------------------+                                  |
|                |                                                   |
|                v                                                   |
|  PART 2: Custom Visualization                                    |
|  +-----------------------------+                                  |
|  | Draw bounding boxes         |                                 |
|  | Add class labels and scores |                                 |
|  | Color-code by class         |                                 |
|  +-----------------------------+                                  |
|                |                                                   |
|                v                                                   |
|  PART 3: Filtering and Control                                   |
|  +-----------------------------+                                  |
|  | Filter by confidence score  |                                 |
|  | Filter by object class      |                                 |
|  | Save annotated results      |                                 |
|  +-----------------------------+                                  |
|                |                                                   |
|                v                                                   |
|  PART 4: Gradio Detection App                                    |
|  +-----------------------------+                                  |
|  | Upload images               |                                 |
|  | Adjust settings             |                                 |
|  | View annotated results      |                                 |
|  +-----------------------------+                                  |
|                                                                   |
+------------------------------------------------------------------+
```

### What Is YOLO?

**YOLO** stands for **You Only Look Once**. It is one of the fastest and most popular object detection models. Unlike older detection methods that scan an image multiple times at different locations, YOLO processes the entire image in a single pass — hence "you only look once."

```
+------------------------------------------------------------------+
|              How YOLO Works (Simplified)                          |
+------------------------------------------------------------------+
|                                                                   |
|  Input Image                                                      |
|  +-------------------+                                            |
|  |  +---+            |                                            |
|  |  |cat|   +-----+  |                                            |
|  |  +---+   | dog |  |                                            |
|  |          +-----+  |                                            |
|  +-------------------+                                            |
|           |                                                       |
|           v                                                       |
|  YOLO divides the image into a grid:                              |
|  +-----+-----+-----+                                             |
|  |  .  |  .  |  .  |                                             |
|  +-----+-----+-----+                                             |
|  |  .  |  .  |  .  |                                             |
|  +-----+-----+-----+                                             |
|  |  .  |  .  |  .  |                                             |
|  +-----+-----+-----+                                             |
|                                                                   |
|  Each grid cell predicts:                                         |
|  - Bounding boxes (x, y, width, height)                          |
|  - Confidence scores (how sure it is)                            |
|  - Class probabilities (what object it is)                       |
|                                                                   |
|  All predictions happen in ONE forward pass!                     |
|  That is why YOLO is so fast.                                    |
|                                                                   |
+------------------------------------------------------------------+
```

YOLOv8 is the latest version, released by Ultralytics. It is faster, more accurate, and easier to use than previous versions.

---

## 28.2 Part 1 — YOLOv8 Inference on Images

First, install the Ultralytics library:

```bash
pip install ultralytics
```

### Running Detection on an Image

```python
# Part 1: YOLOv8 inference on images

from ultralytics import YOLO
from PIL import Image
import os

# Load YOLOv8 pre-trained model
# 'yolov8n' is the nano (smallest, fastest) version
# Other options: yolov8s (small), yolov8m (medium),
#                yolov8l (large), yolov8x (extra large)
model = YOLO('yolov8n.pt')

print("YOLOv8 Model Loaded")
print("=" * 55)
print(f"Model: YOLOv8n (nano)")
print(f"Number of classes: {len(model.names)}")
print(f"\nFirst 20 classes:")
for i in range(20):
    print(f"  {i:3d}: {model.names[i]}")

print(f"\nSome other classes:")
for i in [24, 39, 56, 62, 67, 73]:
    print(f"  {i:3d}: {model.names[i]}")
```

**Expected Output:**
```
YOLOv8 Model Loaded
=======================================================
Model: YOLOv8n (nano)
Number of classes: 80

First 20 classes:
    0: person
    1: bicycle
    2: car
    3: motorcycle
    4: airplane
    5: bus
    6: train
    7: truck
    8: boat
    9: traffic light
   10: fire hydrant
   11: stop sign
   12: parking meter
   13: bench
   14: bird
   15: cat
   16: dog
   17: horse
   18: sheep
   19: cow

Some other classes:
   24: backpack
   39: bottle
   56: chair
   62: tv
   67: cell phone
   73: book
```

YOLOv8 is trained on the COCO dataset, which contains 80 common object classes including people, vehicles, animals, furniture, and everyday items.

### Running Detection and Parsing Results

```python
# Running detection on an image

from ultralytics import YOLO
from PIL import Image

model = YOLO('yolov8n.pt')

# Run detection on an image
# You can use any image file path or URL
results = model('https://ultralytics.com/images/bus.jpg')

# Parse the results
result = results[0]  # First image's results

print("Detection Results")
print("=" * 55)
print(f"Image size: {result.orig_shape}")
print(f"Number of detections: {len(result.boxes)}")
print()

# Extract detection details
print(f"{'#':<4} {'Class':<15} {'Confidence':<12} {'Bounding Box (x1,y1,x2,y2)'}")
print("-" * 65)

for i, box in enumerate(result.boxes):
    # Get class ID and name
    class_id = int(box.cls[0])
    class_name = model.names[class_id]

    # Get confidence score
    confidence = float(box.conf[0])

    # Get bounding box coordinates
    # xyxy format: (x1, y1, x2, y2) = (left, top, right, bottom)
    x1, y1, x2, y2 = box.xyxy[0].tolist()

    print(f"{i+1:<4} {class_name:<15} {confidence:<12.4f} "
          f"({x1:.0f}, {y1:.0f}, {x2:.0f}, {y2:.0f})")

# Summary by class
print(f"\nDetection Summary:")
class_counts = {}
for box in result.boxes:
    class_name = model.names[int(box.cls[0])]
    class_counts[class_name] = class_counts.get(class_name, 0) + 1

for class_name, count in sorted(class_counts.items()):
    print(f"  {class_name}: {count}")
```

**Expected Output:**
```
Detection Results
=======================================================
Image size: (1080, 810)
Number of detections: 5

#    Class           Confidence   Bounding Box (x1,y1,x2,y2)
-----------------------------------------------------------------
1    person          0.8845       (670, 377, 809, 878)
2    person          0.8714       (48, 398, 245, 903)
3    bus             0.8675       (17, 231, 801, 768)
4    person          0.8423       (222, 407, 343, 859)
5    person          0.5987       (0, 551, 63, 872)

Detection Summary:
  bus: 1
  person: 4
```

Let us explain the key detection fields:

- **class_id / class_name**: Which object class was detected (person, car, dog, etc.)
- **confidence**: How confident the model is in this detection (0.0 to 1.0). Higher is more confident
- **bounding box (x1, y1, x2, y2)**: The coordinates of the rectangle around the detected object. (x1, y1) is the top-left corner and (x2, y2) is the bottom-right corner

```
+------------------------------------------------------------------+
|              Bounding Box Coordinates                             |
+------------------------------------------------------------------+
|                                                                   |
|  (x1, y1) +-----------+                                         |
|            |           |                                          |
|            |   OBJECT  |    Bounding box format: xyxy             |
|            |           |    (x1, y1) = top-left corner            |
|            +-----------+ (x2, y2)   (x2, y2) = bottom-right corner|
|                                                                   |
|  Width  = x2 - x1                                                |
|  Height = y2 - y1                                                |
|                                                                   |
+------------------------------------------------------------------+
```

---

## 28.3 Part 2 — Custom Visualization with Bounding Boxes

While YOLOv8 has built-in plotting, let us build our own visualization to learn how it works and have full control over the appearance.

```python
# Part 2: Custom visualization with bounding boxes

from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO
import random

def get_class_colors(num_classes):
    """Generate distinct colors for each class."""
    random.seed(42)  # Fixed seed for consistent colors
    colors = {}
    for i in range(num_classes):
        colors[i] = (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255)
        )
    return colors


def draw_detections(image, detections, class_names, min_confidence=0.5):
    """
    Draw bounding boxes and labels on an image.

    Parameters:
        image: PIL Image to annotate
        detections: YOLO detection results (result.boxes)
        class_names: Dictionary mapping class IDs to names
        min_confidence: Minimum confidence to display a detection

    Returns:
        Annotated PIL Image
    """

    # Create a copy to avoid modifying the original
    annotated = image.copy()
    draw = ImageDraw.Draw(annotated)

    # Generate colors for each class
    colors = get_class_colors(len(class_names))

    # Try to load a nice font, fall back to default
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except (IOError, OSError):
        font = ImageFont.load_default()
        small_font = font

    # Track detection count
    detection_count = 0

    for box in detections:
        # Get detection info
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        x1, y1, x2, y2 = box.xyxy[0].tolist()

        # Skip low-confidence detections
        if confidence < min_confidence:
            continue

        detection_count += 1
        class_name = class_names[class_id]
        color = colors[class_id]

        # Draw the bounding box (rectangle)
        box_width = 3
        draw.rectangle(
            [x1, y1, x2, y2],
            outline=color,
            width=box_width
        )

        # Create label text
        label = f"{class_name} {confidence:.0%}"

        # Calculate label background size
        bbox = draw.textbbox((0, 0), label, font=font)
        label_width = bbox[2] - bbox[0]
        label_height = bbox[3] - bbox[1]

        # Draw label background
        label_y = max(y1 - label_height - 6, 0)
        draw.rectangle(
            [x1, label_y, x1 + label_width + 8, label_y + label_height + 6],
            fill=color
        )

        # Draw label text (white on colored background)
        draw.text(
            (x1 + 4, label_y + 2),
            label,
            fill=(255, 255, 255),
            font=font
        )

    # Add detection summary at the top
    summary = f"Detected: {detection_count} objects (min confidence: {min_confidence:.0%})"
    draw.rectangle([0, 0, len(summary) * 8 + 10, 22], fill=(0, 0, 0, 180))
    draw.text((5, 3), summary, fill=(255, 255, 255), font=small_font)

    return annotated, detection_count


# Run detection and visualize
model = YOLO('yolov8n.pt')
image = Image.open('bus.jpg')  # Use any image

results = model(image)
result = results[0]

# Draw detections
annotated_image, count = draw_detections(
    image, result.boxes, model.names, min_confidence=0.5
)

# Save the result
annotated_image.save('detected_bus.jpg')

print("Custom Visualization Complete")
print("=" * 55)
print(f"Objects detected: {count}")
print(f"Annotated image saved: detected_bus.jpg")
```

**Expected Output:**
```
Custom Visualization Complete
=======================================================
Objects detected: 5
Annotated image saved: detected_bus.jpg
```

Let us trace through the `draw_detections` function:

- **Lines 8-16**: We create a copy of the image and an `ImageDraw` object. The draw object lets us draw shapes and text on the image
- **Lines 19**: We generate a unique color for each object class so different classes are easy to distinguish
- **Lines 22-26**: We try to load a TrueType font for nice-looking labels. If the font file is not available, we fall back to a basic default font
- **Lines 33-37**: For each detection, we extract the class ID, confidence, and bounding box coordinates
- **Lines 40-41**: We skip detections with confidence below our threshold
- **Lines 47-52**: We draw the bounding box as a colored rectangle using `draw.rectangle`
- **Lines 55-74**: We draw a label showing the class name and confidence percentage. The label has a colored background for readability

---

## 28.4 Part 3 — Confidence Filtering and Class Filtering

In real applications, you often want to filter detections. For example, a security system might only care about "person" detections, or a wildlife camera might only want animals.

```python
# Part 3: Filtering detections by confidence and class

from ultralytics import YOLO
from PIL import Image

model = YOLO('yolov8n.pt')


def detect_and_filter(image_path, confidence_threshold=0.5,
                       target_classes=None):
    """
    Detect objects with filtering options.

    Parameters:
        image_path: Path to the image file
        confidence_threshold: Minimum confidence score (0.0 to 1.0)
        target_classes: List of class names to detect, or None for all

    Returns:
        List of detection dictionaries
    """

    # Run detection
    results = model(image_path, verbose=False)
    result = results[0]

    # Parse and filter detections
    detections = []

    for box in result.boxes:
        class_id = int(box.cls[0])
        class_name = model.names[class_id]
        confidence = float(box.conf[0])
        x1, y1, x2, y2 = box.xyxy[0].tolist()

        # Filter by confidence
        if confidence < confidence_threshold:
            continue

        # Filter by class (if specified)
        if target_classes and class_name not in target_classes:
            continue

        detections.append({
            'class_name': class_name,
            'class_id': class_id,
            'confidence': confidence,
            'bbox': {
                'x1': int(x1), 'y1': int(y1),
                'x2': int(x2), 'y2': int(y2)
            },
            'width': int(x2 - x1),
            'height': int(y2 - y1),
            'area': int((x2 - x1) * (y2 - y1))
        })

    # Sort by confidence (highest first)
    detections.sort(key=lambda d: d['confidence'], reverse=True)

    return detections


# Example 1: All detections above 50% confidence
print("Example 1: All objects (confidence > 50%)")
print("=" * 55)

detections = detect_and_filter('bus.jpg', confidence_threshold=0.5)

for det in detections:
    print(f"  {det['class_name']:<15} "
          f"conf={det['confidence']:.2f}  "
          f"size={det['width']}x{det['height']}  "
          f"area={det['area']} px")

print(f"\n  Total: {len(detections)} objects")


# Example 2: Only persons with high confidence
print(f"\nExample 2: Only persons (confidence > 70%)")
print("=" * 55)

person_detections = detect_and_filter(
    'bus.jpg',
    confidence_threshold=0.7,
    target_classes=['person']
)

for det in person_detections:
    print(f"  {det['class_name']:<15} "
          f"conf={det['confidence']:.2f}  "
          f"bbox=({det['bbox']['x1']},{det['bbox']['y1']},"
          f"{det['bbox']['x2']},{det['bbox']['y2']})")

print(f"\n  Total persons found: {len(person_detections)}")


# Example 3: Only vehicles
print(f"\nExample 3: Only vehicles (confidence > 50%)")
print("=" * 55)

vehicle_classes = ['car', 'bus', 'truck', 'motorcycle', 'bicycle']
vehicle_detections = detect_and_filter(
    'bus.jpg',
    confidence_threshold=0.5,
    target_classes=vehicle_classes
)

for det in vehicle_detections:
    print(f"  {det['class_name']:<15} conf={det['confidence']:.2f}")

print(f"\n  Total vehicles found: {len(vehicle_detections)}")
```

**Expected Output:**
```
Example 1: All objects (confidence > 50%)
=======================================================
  person          conf=0.88  size=139x501  area=69639 px
  person          conf=0.87  size=197x505  area=99485 px
  bus             conf=0.87  size=784x537  area=421008 px
  person          conf=0.84  size=121x452  area=54692 px
  person          conf=0.60  size=63x321   area=20223 px

  Total: 5 objects

Example 2: Only persons (confidence > 70%)
=======================================================
  person          conf=0.88  bbox=(670,377,809,878)
  person          conf=0.87  bbox=(48,398,245,903)
  person          conf=0.84  bbox=(222,407,343,859)

  Total persons found: 3

Example 3: Only vehicles (confidence > 50%)
=======================================================
  bus             conf=0.87

  Total vehicles found: 1
```

### Saving Annotated Results

```python
# Saving annotated images with detection results

import json
from datetime import datetime

def save_detection_results(image_path, output_dir='detection_results'):
    """
    Run detection and save annotated image + JSON results.
    """

    os.makedirs(output_dir, exist_ok=True)

    # Load image
    image = Image.open(image_path)

    # Run detection
    results = model(image_path, verbose=False)
    result = results[0]

    # Draw annotations
    annotated_image, count = draw_detections(
        image, result.boxes, model.names, min_confidence=0.5
    )

    # Generate filenames
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    img_output = os.path.join(output_dir, f'{base_name}_detected_{timestamp}.jpg')
    json_output = os.path.join(output_dir, f'{base_name}_results_{timestamp}.json')

    # Save annotated image
    annotated_image.save(img_output, quality=95)

    # Save detection data as JSON
    detection_data = {
        'source_image': image_path,
        'timestamp': timestamp,
        'image_size': {'width': image.width, 'height': image.height},
        'total_detections': count,
        'detections': []
    }

    for box in result.boxes:
        confidence = float(box.conf[0])
        if confidence < 0.5:
            continue

        class_id = int(box.cls[0])
        x1, y1, x2, y2 = box.xyxy[0].tolist()

        detection_data['detections'].append({
            'class': model.names[class_id],
            'confidence': round(confidence, 4),
            'bbox': {
                'x1': int(x1), 'y1': int(y1),
                'x2': int(x2), 'y2': int(y2)
            }
        })

    with open(json_output, 'w') as f:
        json.dump(detection_data, f, indent=2)

    print(f"Results saved:")
    print(f"  Annotated image: {img_output}")
    print(f"  Detection data:  {json_output}")
    print(f"  Objects found:   {count}")

    return img_output, json_output


# Save results
save_detection_results('bus.jpg')
```

**Expected Output:**
```
Results saved:
  Annotated image: detection_results/bus_detected_20240115_143022.jpg
  Detection data:  detection_results/bus_results_20240115_143022.json
  Objects found:   5
```

---

## 28.5 Part 4 — Building the Gradio Detection App

Now let us put everything together into a polished Gradio web application:

```python
# Part 4: Complete Gradio object detection app

from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont
import gradio as gr
import random
import numpy as np

# =============================================================
# Load the model
# =============================================================

model = YOLO('yolov8n.pt')
print(f"YOLOv8 model loaded with {len(model.names)} classes")

# Generate consistent colors for each class
random.seed(42)
CLASS_COLORS = {
    i: (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
    for i in range(len(model.names))
}


# =============================================================
# Detection and visualization function
# =============================================================

def detect_objects(image, confidence_threshold, class_filter):
    """
    Detect objects in an image and return annotated result.

    Parameters:
        image: PIL Image uploaded by the user
        confidence_threshold: Minimum confidence (0.0-1.0)
        class_filter: Comma-separated class names, or "all"

    Returns:
        Annotated image and detection summary text
    """

    if image is None:
        return None, "No image provided."

    # Parse class filter
    target_classes = None
    if class_filter and class_filter.strip().lower() != "all":
        target_classes = [c.strip().lower() for c in class_filter.split(',')]

    # Run YOLOv8 detection
    results = model(image, verbose=False)
    result = results[0]

    # Create annotated image
    annotated = image.copy()
    draw = ImageDraw.Draw(annotated)

    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18
        )
    except (IOError, OSError):
        try:
            font = ImageFont.truetype(
                "/System/Library/Fonts/Helvetica.ttc", 18
            )
        except (IOError, OSError):
            font = ImageFont.load_default()

    # Process detections
    detection_count = 0
    summary_lines = []
    class_counts = {}

    for box in result.boxes:
        class_id = int(box.cls[0])
        class_name = model.names[class_id]
        confidence = float(box.conf[0])

        # Apply confidence filter
        if confidence < confidence_threshold:
            continue

        # Apply class filter
        if target_classes and class_name.lower() not in target_classes:
            continue

        detection_count += 1
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        color = CLASS_COLORS[class_id]

        # Draw bounding box
        draw.rectangle([x1, y1, x2, y2], outline=color, width=3)

        # Draw label
        label = f"{class_name} {confidence:.0%}"
        bbox = draw.textbbox((0, 0), label, font=font)
        lw = bbox[2] - bbox[0]
        lh = bbox[3] - bbox[1]
        ly = max(y1 - lh - 8, 0)

        draw.rectangle(
            [x1, ly, x1 + lw + 10, ly + lh + 8],
            fill=color
        )
        draw.text((x1 + 5, ly + 3), label, fill='white', font=font)

        # Track class counts
        class_counts[class_name] = class_counts.get(class_name, 0) + 1

    # Build summary text
    summary_lines.append(f"Total objects detected: {detection_count}")
    summary_lines.append(f"Confidence threshold: {confidence_threshold:.0%}")

    if class_filter and class_filter.strip().lower() != "all":
        summary_lines.append(f"Class filter: {class_filter}")

    summary_lines.append("")
    summary_lines.append("Detections by class:")

    for class_name, count in sorted(class_counts.items()):
        summary_lines.append(f"  {class_name}: {count}")

    if detection_count == 0:
        summary_lines.append("  No objects detected with current settings.")
        summary_lines.append("  Try lowering the confidence threshold.")

    summary = "\n".join(summary_lines)

    return annotated, summary


# =============================================================
# Build the Gradio interface
# =============================================================

# List some common classes for the description
common_classes = ", ".join(list(model.names.values())[:15]) + ", ..."

demo = gr.Interface(
    fn=detect_objects,
    inputs=[
        gr.Image(type="pil", label="Upload Image"),
        gr.Slider(
            minimum=0.1, maximum=1.0, value=0.5, step=0.05,
            label="Confidence Threshold",
            info="Only show detections above this confidence level"
        ),
        gr.Textbox(
            value="all",
            label="Class Filter",
            info="Enter class names separated by commas (e.g., 'person, car, dog') or 'all'",
            placeholder="all"
        ),
    ],
    outputs=[
        gr.Image(type="pil", label="Detection Results"),
        gr.Textbox(label="Detection Summary", lines=10),
    ],
    title="Object Detection System",
    description=(
        "Upload an image to detect objects using YOLOv8. "
        "Adjust the confidence threshold and filter by class. "
        f"Available classes: {common_classes}"
    ),
    examples=[
        # Add example images if available
        # ["example1.jpg", 0.5, "all"],
        # ["example2.jpg", 0.7, "person, car"],
    ],
    flagging_mode="never",
)


# =============================================================
# Launch the app
# =============================================================

print("\nObject Detection App")
print("=" * 55)
print(f"Model: YOLOv8n ({len(model.names)} classes)")
print(f"Available classes: {len(model.names)}")
print()
print("Starting web app...")

demo.launch(share=False)
```

**Expected Output:**
```
YOLOv8 model loaded with 80 classes

Object Detection App
=======================================================
Model: YOLOv8n (80 classes)
Available classes: 80

Starting web app...
Running on local URL:  http://127.0.0.1:7860
```

```
+------------------------------------------------------------------+
|              Object Detection Web Interface                       |
+------------------------------------------------------------------+
|                                                                   |
|  +-----------------------------------------------------------+   |
|  |          Object Detection System                           |   |
|  +-----------------------------------------------------------+   |
|  |                                                             |   |
|  | Upload an image to detect objects using YOLOv8.             |   |
|  |                                                             |   |
|  | +---------+  +----------+  +---------------------------+   |   |
|  | | Upload  |  |Confidence|  | Class Filter              |   |   |
|  | | Image   |  | [===|==] |  | [all                   ]  |   |   |
|  | |         |  |   0.50   |  |                           |   |   |
|  | +---------+  +----------+  +---------------------------+   |   |
|  |                                                             |   |
|  | +------------------------+  +---------------------------+  |   |
|  | |                        |  | Detection Summary:        |  |   |
|  | |   [Annotated image     |  |                           |  |   |
|  | |    with boxes and      |  | Total detected: 5         |  |   |
|  | |    labels shown here]  |  | Confidence: 50%           |  |   |
|  | |                        |  |                           |  |   |
|  | |                        |  | Detections by class:      |  |   |
|  | |                        |  |   bus: 1                  |  |   |
|  | +------------------------+  |   person: 4              |  |   |
|  |                              +---------------------------+  |   |
|  |  [Submit]  [Clear]                                          |   |
|  +-----------------------------------------------------------+   |
|                                                                   |
+------------------------------------------------------------------+
```

### Complete Standalone Detection App

Here is the complete, self-contained application file that you can run independently:

```python
# detection_app.py
# Run with: python detection_app.py
# Install dependencies: pip install ultralytics gradio pillow

"""
Complete Object Detection App
Uses YOLOv8 for real-time object detection with a Gradio web interface.
"""

from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont
import gradio as gr
import random

# Load model
print("Loading YOLOv8 model...")
model = YOLO('yolov8n.pt')
print(f"Model ready with {len(model.names)} object classes")

# Class colors
random.seed(42)
COLORS = {i: (random.randint(50, 255), random.randint(50, 255),
              random.randint(50, 255)) for i in range(80)}


def detect(image, conf_thresh=0.5, classes="all"):
    """Detect objects and return annotated image + summary."""
    if image is None:
        return None, "Please upload an image."

    # Parse class filter
    filter_classes = None
    if classes.strip().lower() != "all":
        filter_classes = [c.strip().lower() for c in classes.split(",")]

    # Run YOLO
    results = model(image, verbose=False)
    boxes = results[0].boxes

    # Draw
    img = image.copy()
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 16)
    except IOError:
        font = ImageFont.load_default()

    counts = {}
    n = 0

    for box in boxes:
        cls_id = int(box.cls[0])
        name = model.names[cls_id]
        conf = float(box.conf[0])

        if conf < conf_thresh:
            continue
        if filter_classes and name.lower() not in filter_classes:
            continue

        n += 1
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        color = COLORS[cls_id]

        draw.rectangle([x1, y1, x2, y2], outline=color, width=3)

        label = f"{name} {conf:.0%}"
        tb = draw.textbbox((0, 0), label, font=font)
        lh = tb[3] - tb[1]
        lw = tb[2] - tb[0]
        ly = max(y1 - lh - 6, 0)
        draw.rectangle([x1, ly, x1 + lw + 8, ly + lh + 6], fill=color)
        draw.text((x1 + 4, ly + 2), label, fill="white", font=font)

        counts[name] = counts.get(name, 0) + 1

    # Summary
    lines = [f"Objects found: {n}", f"Threshold: {conf_thresh:.0%}", ""]
    for name, cnt in sorted(counts.items()):
        lines.append(f"  {name}: {cnt}")
    if n == 0:
        lines.append("  None. Try lowering the confidence threshold.")

    return img, "\n".join(lines)


# Build interface
app = gr.Interface(
    fn=detect,
    inputs=[
        gr.Image(type="pil", label="Upload Image"),
        gr.Slider(0.1, 1.0, 0.5, step=0.05, label="Confidence"),
        gr.Textbox(value="all", label="Classes (comma-separated or 'all')"),
    ],
    outputs=[
        gr.Image(type="pil", label="Detections"),
        gr.Textbox(label="Summary", lines=8),
    ],
    title="Object Detection with YOLOv8",
    description="Upload any image to detect and locate objects.",
)

if __name__ == "__main__":
    app.launch()
```

Save this as `detection_app.py` and run it with `python detection_app.py`. Open the URL in your browser, upload any image, and see objects detected with bounding boxes, labels, and confidence scores.

---

## Common Mistakes

1. **Using too low a confidence threshold**: Setting the threshold below 0.3 produces many false positives (detecting objects that are not there). Start with 0.5 and adjust downward only if you are missing important detections.

2. **Not handling missing fonts**: The `ImageFont.truetype()` call fails if the font file does not exist. Always include a try/except fallback to `ImageFont.load_default()`.

3. **Confusing box coordinate formats**: YOLO can output boxes in different formats: `xyxy` (x1, y1, x2, y2), `xywh` (center_x, center_y, width, height), and `xyxyn` (normalized). Always use `box.xyxy` for drawing and make sure you know which format you are working with.

4. **Running YOLO on very large images without resizing**: Very large images (4000x3000 or bigger) use a lot of memory. YOLOv8 handles resizing internally, but if you are processing many images, consider resizing first.

5. **Forgetting verbose=False**: By default, YOLO prints detection info to the console for every image. Use `verbose=False` in production to suppress this output.

---

## Best Practices

1. **Choose the right YOLO model size**: Use `yolov8n` (nano) for speed, `yolov8s` (small) for a good balance, and `yolov8m/l/x` for maximum accuracy. Nano is fast enough for most real-time applications.

2. **Use confidence thresholds appropriate for your use case**: Security applications might use a lower threshold (0.3) to avoid missing threats. Product counting might use a higher threshold (0.7) to avoid false counts.

3. **Filter by relevant classes**: If you only care about people and vehicles, filter out the other 75+ classes. This reduces noise and speeds up post-processing.

4. **Save both images and metadata**: Save the annotated image for visual inspection and the JSON metadata for programmatic analysis. This makes your results easy to review and process.

5. **Test with diverse images**: Test your detection app with images of different sizes, lighting conditions, and object counts to ensure robustness.

---

## Quick Summary

In this project, we built a complete object detection system using **YOLOv8**, one of the fastest and most accurate detection models available. We loaded a pre-trained model that recognizes 80 object classes, ran inference on images, parsed detection results (class names, confidence scores, bounding box coordinates), built custom visualizations with labeled bounding boxes, implemented filtering by confidence and class, saved annotated results with metadata, and created a **Gradio web interface** where users can upload images, adjust detection settings, and see results instantly.

---

## Key Points

- **YOLO** (You Only Look Once) detects all objects in an image in a single forward pass
- YOLOv8 is pre-trained on COCO dataset with 80 common object classes
- Model sizes range from nano (fast) to extra-large (accurate): yolov8n/s/m/l/x
- Each detection includes: class name, confidence score, and bounding box coordinates
- Bounding boxes in xyxy format: (x1, y1) = top-left, (x2, y2) = bottom-right
- **Confidence threshold** filters out uncertain detections (default: 0.5)
- **Class filtering** lets you detect only specific object types
- Custom visualization draws colored boxes and labels using PIL/Pillow
- Gradio creates an interactive web interface with sliders and text inputs
- Save both annotated images and JSON metadata for complete records

---

## Practice Questions

1. What does "You Only Look Once" mean in the context of YOLO? How is this different from older detection methods that scan an image multiple times?

2. Explain the difference between image classification and object detection. Why is object detection a harder problem?

3. If you set the confidence threshold to 0.9, what happens to your detections? What about 0.1? What is the trade-off?

4. Why do we generate different colors for different object classes in our visualization? What would happen if we used the same color for everything?

5. You are building a parking lot monitoring system. Which YOLO model size would you choose, what confidence threshold would you set, and which classes would you filter for? Explain your reasoning.

---

## Exercises

**Exercise 1: Detection Statistics Dashboard**
Extend the Gradio app to include additional statistics: the average confidence score across all detections, the largest and smallest detected objects (by bounding box area), and the percentage of the image covered by detections. Display these in the summary text box.

**Exercise 2: Multi-Image Batch Processing**
Write a function that takes a folder of images, runs YOLOv8 on each one, saves annotated versions, and produces a CSV summary file listing the filename, number of detections, and classes found in each image. Process all images in the folder automatically.

**Exercise 3: Detection Comparison Tool**
Build a Gradio app that lets the user upload one image but run detection with two different YOLO model sizes (e.g., yolov8n and yolov8m). Display both annotated images side by side with their summaries so the user can compare speed vs. accuracy trade-offs.

---

## Congratulations!

You have completed Book 4: NLP and Computer Vision! Let us look at the incredible journey you have been on.

### What You Have Accomplished

```
+------------------------------------------------------------------+
|              Your NLP & Computer Vision Journey                   |
+------------------------------------------------------------------+
|                                                                   |
|  NLP Foundations (Chapters 1-6):                                  |
|  - Text preprocessing, tokenization, stopwords                   |
|  - Bag of Words, TF-IDF, word embeddings                        |
|  - Text classification and named entity recognition              |
|                                                                   |
|  Advanced NLP (Chapters 7-15):                                   |
|  - Text summarization (extractive and abstractive)               |
|  - Sequence-to-sequence models and attention                     |
|  - BERT (bidirectional understanding)                            |
|  - GPT family (text generation and RLHF)                        |
|  - Hugging Face ecosystem and fine-tuning                        |
|  - Question answering, text generation, multilingual NLP         |
|                                                                   |
|  Computer Vision (Chapters 16-24):                               |
|  - Image fundamentals and preprocessing                          |
|  - CNNs and transfer learning                                    |
|  - Object detection and image segmentation                       |
|  - Face detection and Vision Transformers                        |
|  - OCR (optical character recognition)                           |
|                                                                   |
|  Projects (Chapters 25-28):                                      |
|  - Sentiment analysis API                                        |
|  - Document classifier                                           |
|  - Image classification app with Gradio                          |
|  - Object detection system with YOLOv8                           |
|                                                                   |
+------------------------------------------------------------------+
```

You now have the knowledge and skills to:

- Process and analyze text data with modern NLP techniques
- Use pre-trained models like BERT and GPT for real-world tasks
- Build image classification and object detection systems
- Create web interfaces for your AI models
- Deploy complete AI applications

### What Is Next? — Book 5: Generative AI and LLMs

The next book takes you into the most exciting frontier of AI: **Generative AI and Large Language Models (LLMs)**. Here is what awaits you:

```
+------------------------------------------------------------------+
|              Book 5 Preview: Generative AI & LLMs                |
+------------------------------------------------------------------+
|                                                                   |
|  What You Will Learn:                                             |
|                                                                   |
|  - The Transformer architecture in complete detail               |
|  - How Large Language Models (LLMs) are built and trained        |
|  - Prompt engineering techniques for getting the best results    |
|  - Fine-tuning LLMs on your own data (LoRA, QLoRA)             |
|  - Retrieval-Augmented Generation (RAG) for knowledge systems   |
|  - Building AI agents that can use tools and take actions        |
|  - Generative AI for images (Stable Diffusion)                  |
|  - Responsible AI development and safety considerations          |
|  - Building production-ready LLM applications                    |
|                                                                   |
|  Book 5 builds directly on the BERT, GPT, and Transformer       |
|  knowledge from this book. You are perfectly prepared.           |
|                                                                   |
+------------------------------------------------------------------+
```

The skills you have built in this book — understanding tokenization, attention mechanisms, encoder-decoder architectures, BERT, and GPT — are the exact foundation you need for the generative AI revolution. You are no longer a beginner. You are ready to build the next generation of AI applications.

Keep learning. Keep building. The best is yet to come.

---

## What Is Next?

Continue your AI journey with **Book 5: Generative AI and LLMs**, where you will dive deep into the technology powering today's most impressive AI systems. You will learn to build RAG systems, fine-tune LLMs, create AI agents, and develop production-ready generative AI applications. Everything you have learned so far has prepared you for this exciting next step.
