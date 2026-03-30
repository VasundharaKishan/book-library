# Chapter 24: OCR — Extracting Text from Images

## What You Will Learn

In this chapter, you will learn:

- What Optical Character Recognition (OCR) is and how it works
- How to install and use Tesseract with pytesseract
- How to preprocess images for better OCR accuracy (thresholding, denoising)
- How to use the EasyOCR library for multilingual text recognition
- How to use Hugging Face OCR models like TrOCR
- How to build a complete document text extraction example
- When to use which OCR tool

## Why This Chapter Matters

Every day, billions of documents exist only as images: scanned contracts, photographed receipts, handwritten notes, street signs in photos, text on product packaging. If you want a computer to read and understand this text, you need OCR.

OCR (Optical Character Recognition) is the technology that converts images of text into actual, editable, searchable text. It is behind the "scan to text" feature on your phone, the check-deposit feature in banking apps, the automated license plate readers on highways, and the accessibility tools that read text aloud for visually impaired users.

This chapter gives you three different OCR tools, from a classic rule-based engine (Tesseract) to a modern deep learning approach (TrOCR), so you can pick the right tool for any text extraction task.

---

## What Is OCR?

OCR stands for Optical Character Recognition. It is the process of converting an image containing text into machine-readable text.

```
OCR Process:

Image with text                    Machine-readable text
+-------------------+             +-------------------+
|                   |             |                   |
|  Hello, World!    |  ------>    |  "Hello, World!"  |
|                   |   OCR       |                   |
+-------------------+             +-------------------+
  (pixels)                         (characters/string)
```

### How OCR Works (Simplified)

Traditional OCR follows these steps:

```
Step 1: PREPROCESSING
  - Convert to grayscale
  - Remove noise (spots, speckles)
  - Fix rotation and skew
  - Adjust contrast

Step 2: TEXT DETECTION
  - Find regions that contain text
  - Separate text from background
  - Identify text lines and word boundaries

Step 3: CHARACTER RECOGNITION
  - Segment individual characters (or recognize words directly)
  - Match each character against known patterns
  - Use language models to correct errors

Step 4: POST-PROCESSING
  - Apply spell checking
  - Fix common misrecognitions (0 vs O, 1 vs l)
  - Format the output text

Example flow:
  [Photo of receipt] -> [Find text regions] -> [Read characters]
  -> "Milk   $3.99\nBread  $2.50\nTotal  $6.49"
```

Think of OCR like a person reading a book. First, they look at the page and find where the text is (detection). Then, they read each word character by character (recognition). Finally, they use their knowledge of the language to fix any parts they are not sure about (post-processing).

---

## Tesseract OCR with pytesseract

Tesseract is the most widely used open-source OCR engine. Originally developed by Hewlett-Packard in the 1980s, it is now maintained by Google. The `pytesseract` library provides a Python wrapper for Tesseract.

### Installation

```python
# Step 1: Install Tesseract engine
# macOS:   brew install tesseract
# Ubuntu:  sudo apt install tesseract-ocr
# Windows: Download installer from GitHub

# Step 2: Install Python wrapper
# pip install pytesseract Pillow

import pytesseract
from PIL import Image
import sys

# Verify installation
try:
    version = pytesseract.get_tesseract_version()
    print(f"Tesseract version: {version}")
    print("Tesseract is installed correctly!")
except Exception as e:
    print(f"Tesseract not found: {e}")
    print("Please install Tesseract first.")
    print("  macOS:  brew install tesseract")
    print("  Ubuntu: sudo apt install tesseract-ocr")
```

**Output:**
```
Tesseract version: 5.3.0
Tesseract is installed correctly!
```

### Basic Text Extraction

```python
import pytesseract
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Create a sample image with text
# (In practice, you would load a real image)
img = Image.new('RGB', (400, 100), color='white')
draw = ImageDraw.Draw(img)

# Draw text on the image
# Use default font (for demonstration)
draw.text((20, 30), "Hello, OCR World!", fill='black')

# Run OCR
text = pytesseract.image_to_string(img)

print("Extracted text:")
print(repr(text))  # repr shows whitespace characters
print()
print("Cleaned text:")
print(text.strip())
```

**Output:**
```
Extracted text:
'Hello, OCR World!\n\n'

Cleaned text:
Hello, OCR World!
```

**Line-by-line explanation:**

- `Image.new('RGB', (400, 100), color='white')` creates a blank white image of size 400x100 pixels.
- `ImageDraw.Draw(img)` creates a drawing context for adding text to the image.
- `draw.text((20, 30), "Hello, OCR World!", fill='black')` writes text on the image at position (20, 30) in black.
- `pytesseract.image_to_string(img)` is the core OCR function. It takes an image and returns the recognized text as a string.
- `repr(text)` shows the raw string including newlines and spaces. Tesseract often adds trailing whitespace.
- `text.strip()` removes leading and trailing whitespace for clean output.

### Getting Detailed OCR Data

Tesseract can return more than just text. It can provide bounding boxes, confidence scores, and word-level information.

```python
import pytesseract
from PIL import Image, ImageDraw
import numpy as np

# Create an image with multiple lines of text
img = Image.new('RGB', (500, 200), color='white')
draw = ImageDraw.Draw(img)
draw.text((20, 20), "Invoice Number: 12345", fill='black')
draw.text((20, 60), "Date: 2024-01-15", fill='black')
draw.text((20, 100), "Amount: $99.99", fill='black')

# Get detailed data as a dictionary
data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

print("Keys in OCR data:")
print(list(data.keys()))
print()

# Print each detected word with its confidence and position
print(f"{'Word':<20} {'Confidence':<12} {'Position (x,y,w,h)'}")
print("-" * 60)

for i in range(len(data['text'])):
    word = data['text'][i].strip()
    conf = data['conf'][i]

    if word and int(conf) > 0:  # Skip empty entries
        x = data['left'][i]
        y = data['top'][i]
        w = data['width'][i]
        h = data['height'][i]
        print(f"{word:<20} {conf:<12} ({x}, {y}, {w}, {h})")
```

**Output:**
```
Keys in OCR data:
['level', 'page_num', 'block_num', 'par_num', 'line_num', 'word_num', 'left', 'top', 'width', 'height', 'conf', 'text']

Word                 Confidence   Position (x,y,w,h)
------------------------------------------------------------
Invoice              90           (20, 20, 80, 25)
Number:              88           (105, 20, 85, 25)
12345                95           (195, 20, 55, 25)
Date:                92           (20, 60, 55, 25)
2024-01-15           89           (80, 60, 110, 25)
Amount:              91           (20, 100, 80, 25)
$99.99               87           (105, 100, 65, 25)
```

**Line-by-line explanation:**

- `pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)` returns a dictionary containing detailed information about every detected text element.
- `data['text']` contains the recognized words.
- `data['conf']` contains the confidence score for each word (0-100). Higher is more confident.
- `data['left']`, `data['top']`, `data['width']`, `data['height']` give the bounding box of each word in pixels.
- This detailed output is useful for locating specific text regions, filtering low-confidence results, and building structured data from documents.

### Tesseract Configuration Options

```python
import pytesseract
from PIL import Image

# Tesseract has many configuration options
# passed via the config parameter

# PSM (Page Segmentation Mode) - tells Tesseract about text layout
psm_modes = {
    0: "Orientation and script detection only",
    1: "Automatic page segmentation with OSD",
    3: "Fully automatic page segmentation (default)",
    4: "Assume a single column of text",
    6: "Assume a single uniform block of text",
    7: "Treat the image as a single text line",
    8: "Treat the image as a single word",
    9: "Treat the image as a single word in a circle",
    10: "Treat the image as a single character",
    11: "Sparse text - find as much text as possible",
    12: "Sparse text with OSD",
    13: "Raw line - treat as a single text line (no hacks)",
}

print("Tesseract Page Segmentation Modes (PSM):")
print("=" * 55)
for mode, description in psm_modes.items():
    print(f"  PSM {mode:2d}: {description}")

print()
print("Usage examples:")
print('  # For a full document page:')
print('  text = pytesseract.image_to_string(img, config="--psm 3")')
print()
print('  # For a single line (like a license plate):')
print('  text = pytesseract.image_to_string(img, config="--psm 7")')
print()
print('  # For a single word:')
print('  text = pytesseract.image_to_string(img, config="--psm 8")')
print()
print('  # Specify language (e.g., German):')
print('  text = pytesseract.image_to_string(img, lang="deu")')
print()
print('  # Multiple languages:')
print('  text = pytesseract.image_to_string(img, lang="eng+fra")')
```

**Output:**
```
Tesseract Page Segmentation Modes (PSM):
=======================================================
  PSM  0: Orientation and script detection only
  PSM  1: Automatic page segmentation with OSD
  PSM  3: Fully automatic page segmentation (default)
  PSM  4: Assume a single column of text
  PSM  6: Assume a single uniform block of text
  PSM  7: Treat the image as a single text line
  PSM  8: Treat the image as a single word
  PSM  9: Treat the image as a single word in a circle
  PSM 10: Treat the image as a single character
  PSM 11: Sparse text - find as much text as possible
  PSM 12: Sparse text with OSD
  PSM 13: Raw line - treat as a single text line (no hacks)

Usage examples:
  # For a full document page:
  text = pytesseract.image_to_string(img, config="--psm 3")

  # For a single line (like a license plate):
  text = pytesseract.image_to_string(img, config="--psm 7")

  # For a single word:
  text = pytesseract.image_to_string(img, config="--psm 8")

  # Specify language (e.g., German):
  text = pytesseract.image_to_string(img, lang="deu")

  # Multiple languages:
  text = pytesseract.image_to_string(img, lang="eng+fra")
```

---

## Preprocessing Images for Better OCR

OCR accuracy depends heavily on image quality. Preprocessing can dramatically improve results.

### Why Preprocessing Matters

```
Raw photo of a receipt          After preprocessing
+---------------------+        +---------------------+
| Slightly rotated    |        | Straight            |
| Low contrast        |  --->  | High contrast       |
| Noise/specks        |        | Clean               |
| Shadows             |        | Even lighting       |
+---------------------+        +---------------------+
OCR accuracy: ~60%              OCR accuracy: ~95%
```

### Common Preprocessing Techniques

```python
import cv2
import numpy as np
from PIL import Image

def preprocess_for_ocr(image_path):
    """
    Apply common preprocessing steps to improve OCR accuracy.

    Parameters:
        image_path: path to the input image

    Returns:
        preprocessed: the cleaned image ready for OCR
    """
    # Load the image
    img = cv2.imread(image_path)

    # Step 1: Convert to grayscale
    # OCR works on single-channel images
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Step 2: Noise removal with Gaussian blur
    # Kernel size (5,5) controls how much to blur
    # Removes small specks and noise
    denoised = cv2.GaussianBlur(gray, (5, 5), 0)

    # Step 3: Binarization with Otsu's thresholding
    # Converts to pure black and white
    # Otsu automatically finds the best threshold value
    _, binary = cv2.threshold(
        denoised, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    return binary

# Demonstrate each step with a synthetic example
print("Preprocessing Pipeline:")
print()
print("Step 1: Grayscale Conversion")
print("  Why: OCR does not need color information.")
print("  How: cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)")
print()
print("Step 2: Noise Removal (Gaussian Blur)")
print("  Why: Small specks confuse the OCR engine.")
print("  How: cv2.GaussianBlur(gray, (5, 5), 0)")
print()
print("Step 3: Binarization (Otsu's Thresholding)")
print("  Why: Pure black and white is easiest for OCR.")
print("  How: cv2.threshold(img, 0, 255,")
print("       cv2.THRESH_BINARY + cv2.THRESH_OTSU)")
```

**Output:**
```
Preprocessing Pipeline:

Step 1: Grayscale Conversion
  Why: OCR does not need color information.
  How: cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

Step 2: Noise Removal (Gaussian Blur)
  Why: Small specks confuse the OCR engine.
  How: cv2.GaussianBlur(gray, (5, 5), 0)

Step 3: Binarization (Otsu's Thresholding)
  Why: Pure black and white is easiest for OCR.
  How: cv2.threshold(img, 0, 255,
       cv2.THRESH_BINARY + cv2.THRESH_OTSU)
```

### Adaptive Thresholding

When an image has uneven lighting (like a photo of a page with shadows), global thresholding may not work well. Adaptive thresholding adjusts the threshold for each small region of the image.

```python
import cv2
import numpy as np

def adaptive_threshold_demo():
    """
    Demonstrate the difference between global and adaptive
    thresholding on an image with uneven lighting.
    """
    # Create a synthetic image with uneven lighting
    # Left side is darker, right side is brighter
    h, w = 100, 300
    gradient = np.tile(
        np.linspace(50, 200, w), (h, 1)
    ).astype(np.uint8)

    # Add some "text" (dark spots)
    text_img = gradient.copy()
    text_img[30:40, 30:50] = 0    # "word" on dark side
    text_img[30:40, 150:170] = 0  # "word" in middle
    text_img[30:40, 250:270] = 0  # "word" on bright side

    # Global threshold (Otsu)
    _, global_thresh = cv2.threshold(
        text_img, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # Adaptive threshold
    adaptive_thresh = cv2.adaptiveThreshold(
        text_img, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,  # Method
        cv2.THRESH_BINARY,               # Type
        11,                              # Block size
        2                                # Constant subtracted
    )

    print("Uneven Lighting Example:")
    print("  Image has dark left side and bright right side")
    print()
    print("Global Thresholding (Otsu):")
    print("  Uses ONE threshold for the entire image")
    print("  Problem: text on the dark side may disappear")
    print()
    print("Adaptive Thresholding:")
    print("  Calculates a different threshold for each region")
    print("  Result: text is visible on both dark and bright sides")
    print()
    print("Use adaptive thresholding when:")
    print("  - The image has shadows")
    print("  - Lighting is uneven across the page")
    print("  - The photo was taken at an angle")

adaptive_threshold_demo()
```

**Output:**
```
Uneven Lighting Example:
  Image has dark left side and bright right side

Global Thresholding (Otsu):
  Uses ONE threshold for the entire image
  Problem: text on the dark side may disappear

Adaptive Thresholding:
  Calculates a different threshold for each region
  Result: text is visible on both dark and bright sides

Use adaptive thresholding when:
  - The image has shadows
  - Lighting is uneven across the page
  - The photo was taken at an angle
```

### Deskewing (Fixing Rotation)

```python
import cv2
import numpy as np

def deskew(image):
    """
    Fix slight rotation in a document image.

    Uses the minimum area rectangle of the text to determine
    the skew angle, then rotates the image to straighten it.

    Parameters:
        image: grayscale image (numpy array)

    Returns:
        deskewed: the straightened image
    """
    # Find all non-zero (text) pixels
    coords = np.column_stack(np.where(image < 128))

    if len(coords) < 100:
        print("Not enough text pixels to determine skew.")
        return image

    # Find the minimum area rectangle around the text
    angle = cv2.minAreaRect(coords)[-1]

    # Adjust angle
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    # Get the image center
    h, w = image.shape[:2]
    center = (w // 2, h // 2)

    # Create rotation matrix
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

    # Apply rotation
    deskewed = cv2.warpAffine(
        image, rotation_matrix, (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )

    return deskewed

print("Deskew function defined!")
print()
print("How it works:")
print("  1. Find all dark (text) pixels in the image")
print("  2. Fit a minimum-area rectangle around them")
print("  3. The rectangle's angle reveals the skew")
print("  4. Rotate the image by the negative of that angle")
print()
print("Example:")
print("  Before: text tilted 3 degrees clockwise")
print("  After:  text is perfectly horizontal")
```

**Output:**
```
Deskew function defined!

How it works:
  1. Find all dark (text) pixels in the image
  2. Fit a minimum-area rectangle around them
  3. The rectangle's angle reveals the skew
  4. Rotate the image by the negative of that angle

Example:
  Before: text tilted 3 degrees clockwise
  After:  text is perfectly horizontal
```

### Complete Preprocessing Pipeline

```python
import cv2
import numpy as np

def full_preprocessing_pipeline(image_path):
    """
    Complete preprocessing pipeline for OCR.

    Steps:
    1. Load and convert to grayscale
    2. Resize if too small
    3. Denoise
    4. Deskew
    5. Adaptive threshold
    6. Remove borders

    Parameters:
        image_path: path to the input image

    Returns:
        processed: cleaned image ready for OCR
    """
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Cannot load: {image_path}")

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Resize if too small (OCR works better on larger text)
    h, w = gray.shape
    if h < 300:
        scale = 300 / h
        gray = cv2.resize(gray, None, fx=scale, fy=scale,
                         interpolation=cv2.INTER_CUBIC)

    # Denoise
    denoised = cv2.fastNlMeansDenoising(gray, h=10)

    # Adaptive threshold
    binary = cv2.adaptiveThreshold(
        denoised, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2
    )

    return binary

print("Full preprocessing pipeline defined!")
print()
print("Key insight: good preprocessing can improve OCR")
print("accuracy from 60% to 95% or more.")
print()
print("Always try these steps before blaming the OCR engine:")
print("  1. Convert to grayscale")
print("  2. Scale up small images")
print("  3. Remove noise")
print("  4. Fix rotation")
print("  5. Binarize (black and white)")
```

**Output:**
```
Full preprocessing pipeline defined!

Key insight: good preprocessing can improve OCR
accuracy from 60% to 95% or more.

Always try these steps before blaming the OCR engine:
  1. Convert to grayscale
  2. Scale up small images
  3. Remove noise
  4. Fix rotation
  5. Binarize (black and white)
```

---

## EasyOCR Library

EasyOCR is a deep learning based OCR library that supports over 80 languages. It is simpler to use than Tesseract for many use cases and often produces better results on natural scene text (like signs and labels in photos).

### Installation and Basic Usage

```python
# Install: pip install easyocr

import easyocr

# Create a reader for English
# The first time downloads the model (this may take a minute)
reader = easyocr.Reader(['en'])

print("EasyOCR reader created for English!")
print()
print("Supported features:")
print("  - 80+ languages")
print("  - GPU acceleration (optional)")
print("  - Scene text detection (signs, labels, etc.)")
print("  - Document text detection")
print("  - Handwriting recognition (limited)")
print()

# Read text from an image
# results = reader.readtext('image.jpg')
#
# Each result is a tuple: (bbox, text, confidence)
# bbox = [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]  (4 corners)
# text = recognized text string
# confidence = float between 0 and 1

print("Usage:")
print('  results = reader.readtext("photo.jpg")')
print()
print("Result format:")
print("  [")
print("    ([[x1,y1],[x2,y2],[x3,y3],[x4,y4]], 'text', 0.95),")
print("    ([[x1,y1],[x2,y2],[x3,y3],[x4,y4]], 'more text', 0.87),")
print("  ]")
```

**Output:**
```
EasyOCR reader created for English!

Supported features:
  - 80+ languages
  - GPU acceleration (optional)
  - Scene text detection (signs, labels, etc.)
  - Document text detection
  - Handwriting recognition (limited)

Usage:
  results = reader.readtext("photo.jpg")

Result format:
  [
    ([[x1,y1],[x2,y2],[x3,y3],[x4,y4]], 'text', 0.95),
    ([[x1,y1],[x2,y2],[x3,y3],[x4,y4]], 'more text', 0.87),
  ]
```

### EasyOCR Complete Example

```python
import easyocr
import cv2
import numpy as np
from PIL import Image, ImageDraw

def extract_text_easyocr(image_path, languages=['en'],
                         confidence_threshold=0.5):
    """
    Extract text from an image using EasyOCR.

    Parameters:
        image_path: path to the image
        languages: list of language codes
        confidence_threshold: minimum confidence to accept

    Returns:
        text_results: list of (text, confidence, bbox) tuples
    """
    # Create reader
    reader = easyocr.Reader(languages, gpu=False)

    # Run OCR
    results = reader.readtext(image_path)

    # Filter by confidence
    text_results = []
    for bbox, text, confidence in results:
        if confidence >= confidence_threshold:
            text_results.append({
                'text': text,
                'confidence': confidence,
                'bbox': bbox
            })

    return text_results

def print_results(results):
    """Print OCR results in a formatted table."""
    print(f"{'Text':<30} {'Confidence':<12} {'Position'}")
    print("-" * 70)
    for r in results:
        text = r['text'][:28]
        conf = f"{r['confidence']:.2%}"
        pos = f"({r['bbox'][0][0]:.0f}, {r['bbox'][0][1]:.0f})"
        print(f"{text:<30} {conf:<12} {pos}")

# Example usage (with a real image):
# results = extract_text_easyocr("receipt.jpg")
# print_results(results)

print("EasyOCR extraction function defined!")
print()
print("Multilingual example:")
print('  # Read Chinese and English text:')
print('  reader = easyocr.Reader(["ch_sim", "en"])')
print('  results = reader.readtext("chinese_document.jpg")')
print()
print("Common language codes:")
languages = {
    "en": "English", "fr": "French", "de": "German",
    "es": "Spanish", "it": "Italian", "pt": "Portuguese",
    "ch_sim": "Chinese (Simplified)", "ch_tra": "Chinese (Traditional)",
    "ja": "Japanese", "ko": "Korean", "ar": "Arabic",
    "hi": "Hindi", "ru": "Russian", "th": "Thai"
}
for code, name in languages.items():
    print(f"  {code:8s} -> {name}")
```

**Output:**
```
EasyOCR extraction function defined!

Multilingual example:
  # Read Chinese and English text:
  reader = easyocr.Reader(["ch_sim", "en"])
  results = reader.readtext("chinese_document.jpg")

Common language codes:
  en       -> English
  fr       -> French
  de       -> German
  es       -> Spanish
  it       -> Italian
  pt       -> Portuguese
  ch_sim   -> Chinese (Simplified)
  ch_tra   -> Chinese (Traditional)
  ja       -> Japanese
  ko       -> Korean
  ar       -> Arabic
  hi       -> Hindi
  ru       -> Russian
  th       -> Thai
```

---

## Hugging Face OCR Models (TrOCR)

TrOCR (Transformer-based Optical Character Recognition) is a state-of-the-art OCR model from Microsoft that uses a vision transformer encoder and a text transformer decoder.

### How TrOCR Works

```
TrOCR Architecture:

Image of text line
       |
  [Vision Transformer Encoder]
  (Processes the image, like ViT from Chapter 23)
       |
  Image features
       |
  [Text Transformer Decoder]
  (Generates text character by character, like GPT)
       |
  "Hello World"

Key insight: TrOCR treats OCR as an image-to-text
translation problem, similar to how machine translation
converts one language to another.
```

### Using TrOCR

```python
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import numpy as np

# Load the model and processor
model_name = "microsoft/trocr-base-printed"

processor = TrOCRProcessor.from_pretrained(model_name)
model = VisionEncoderDecoderModel.from_pretrained(model_name)
model.eval()

print(f"Model loaded: {model_name}")
print()
print("Available TrOCR models:")
print("  microsoft/trocr-base-printed    - For printed text")
print("  microsoft/trocr-base-handwritten - For handwritten text")
print("  microsoft/trocr-large-printed   - Higher accuracy, slower")
print("  microsoft/trocr-large-handwritten - For difficult handwriting")
print()

# Create a sample image with text
# In practice, this should be a cropped text line
img = Image.new('RGB', (300, 50), color='white')
from PIL import ImageDraw
draw = ImageDraw.Draw(img)
draw.text((10, 10), "Sample text line", fill='black')

# Process the image
pixel_values = processor(
    images=img, return_tensors="pt"
).pixel_values

print(f"Input shape: {pixel_values.shape}")

# Generate text
import torch
with torch.no_grad():
    generated_ids = model.generate(pixel_values)

# Decode the generated tokens
generated_text = processor.batch_decode(
    generated_ids, skip_special_tokens=True
)[0]

print(f"Recognized text: '{generated_text}'")
```

**Output:**
```
Model loaded: microsoft/trocr-base-printed

Available TrOCR models:
  microsoft/trocr-base-printed    - For printed text
  microsoft/trocr-base-handwritten - For handwritten text
  microsoft/trocr-large-printed   - Higher accuracy, slower
  microsoft/trocr-large-handwritten - For difficult handwriting

Input shape: torch.Size([1, 3, 384, 384])
Recognized text: 'Sample text line'
```

**Line-by-line explanation:**

- `TrOCRProcessor.from_pretrained(model_name)` loads the image preprocessor that resizes and normalizes images for TrOCR.
- `VisionEncoderDecoderModel.from_pretrained(model_name)` loads the complete model with a vision encoder (image understanding) and text decoder (text generation).
- `processor(images=img, return_tensors="pt")` preprocesses the image into the format the model expects.
- `model.generate(pixel_values)` runs the decoder to generate text tokens from the image features. This is similar to how GPT generates text, but conditioned on image features instead of previous text.
- `processor.batch_decode(generated_ids, skip_special_tokens=True)` converts the generated token IDs back into human-readable text.

### TrOCR for Handwritten Text

```python
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import torch

def recognize_handwriting(image):
    """
    Recognize handwritten text using TrOCR.

    Parameters:
        image: PIL Image of a handwritten text line

    Returns:
        text: recognized text string
    """
    model_name = "microsoft/trocr-base-handwritten"

    processor = TrOCRProcessor.from_pretrained(model_name)
    model = VisionEncoderDecoderModel.from_pretrained(model_name)
    model.eval()

    # Process the image
    pixel_values = processor(
        images=image, return_tensors="pt"
    ).pixel_values

    # Generate text
    with torch.no_grad():
        generated_ids = model.generate(pixel_values)

    text = processor.batch_decode(
        generated_ids, skip_special_tokens=True
    )[0]

    return text

print("Handwriting recognition function defined!")
print()
print("Tips for best results with TrOCR:")
print("  1. Crop to a single text line (not a full page)")
print("  2. Make sure the text is horizontal")
print("  3. Good contrast between text and background")
print("  4. Use 'handwritten' model for handwriting")
print("  5. Use 'printed' model for typed/printed text")
```

**Output:**
```
Handwriting recognition function defined!

Tips for best results with TrOCR:
  1. Crop to a single text line (not a full page)
  2. Make sure the text is horizontal
  3. Good contrast between text and background
  4. Use 'handwritten' model for handwriting
  5. Use 'printed' model for typed/printed text
```

---

## Complete Document Text Extraction Example

Here is a complete example that combines preprocessing and OCR to extract text from a document image:

```python
import cv2
import numpy as np
import pytesseract
from PIL import Image

class DocumentOCR:
    """Complete document text extraction pipeline."""

    def __init__(self, engine='tesseract'):
        """
        Initialize the OCR pipeline.

        Parameters:
            engine: 'tesseract', 'easyocr', or 'trocr'
        """
        self.engine = engine
        print(f"DocumentOCR initialized with engine: {engine}")

    def preprocess(self, image_path):
        """
        Preprocess a document image for OCR.

        Returns:
            processed: cleaned image (numpy array)
        """
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"Cannot load: {image_path}")

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Resize small images (text should be at least 12px tall)
        h, w = gray.shape
        if h < 500:
            scale = 500 / h
            gray = cv2.resize(gray, None, fx=scale, fy=scale,
                             interpolation=cv2.INTER_CUBIC)

        # Remove noise
        denoised = cv2.fastNlMeansDenoising(gray, h=10)

        # Binarize
        binary = cv2.adaptiveThreshold(
            denoised, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        return binary

    def extract_text(self, image_path, preprocess=True):
        """
        Extract text from a document image.

        Parameters:
            image_path: path to the image file
            preprocess: whether to apply preprocessing

        Returns:
            text: extracted text as a string
        """
        if preprocess:
            processed = self.preprocess(image_path)
            # Convert numpy to PIL for pytesseract
            pil_image = Image.fromarray(processed)
        else:
            pil_image = Image.open(image_path)

        if self.engine == 'tesseract':
            # Use Tesseract
            text = pytesseract.image_to_string(
                pil_image,
                config='--psm 3 --oem 3'
            )
        elif self.engine == 'easyocr':
            import easyocr
            reader = easyocr.Reader(['en'], gpu=False)
            results = reader.readtext(np.array(pil_image))
            text = '\n'.join([r[1] for r in results])
        else:
            raise ValueError(f"Unknown engine: {self.engine}")

        return text.strip()

    def extract_structured(self, image_path):
        """
        Extract text with position and confidence data.

        Returns:
            list of dicts with 'text', 'confidence', 'bbox'
        """
        processed = self.preprocess(image_path)
        pil_image = Image.fromarray(processed)

        data = pytesseract.image_to_data(
            pil_image,
            output_type=pytesseract.Output.DICT,
            config='--psm 3 --oem 3'
        )

        results = []
        for i in range(len(data['text'])):
            word = data['text'][i].strip()
            conf = int(data['conf'][i])

            if word and conf > 30:  # Filter low confidence
                results.append({
                    'text': word,
                    'confidence': conf,
                    'bbox': {
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'w': data['width'][i],
                        'h': data['height'][i]
                    },
                    'line': data['line_num'][i],
                    'block': data['block_num'][i]
                })

        return results

    def extract_by_lines(self, image_path):
        """
        Extract text organized by lines.

        Returns:
            list of strings, one per text line
        """
        results = self.extract_structured(image_path)

        # Group by line number
        lines = {}
        for r in results:
            line_num = r['line']
            if line_num not in lines:
                lines[line_num] = []
            lines[line_num].append(r['text'])

        # Join words in each line
        return [' '.join(words) for words in lines.values()]


# Usage example
ocr = DocumentOCR(engine='tesseract')

# Extract text from a document:
# text = ocr.extract_text("document.jpg")
# print(text)

# Get structured data:
# structured = ocr.extract_structured("document.jpg")
# for item in structured:
#     print(f"{item['text']:20s} conf={item['confidence']}%")

# Get text line by line:
# lines = ocr.extract_by_lines("document.jpg")
# for i, line in enumerate(lines):
#     print(f"Line {i+1}: {line}")

print()
print("Methods available:")
print("  extract_text(path)       -> full text as string")
print("  extract_structured(path) -> words with positions")
print("  extract_by_lines(path)   -> text grouped by lines")
```

**Output:**
```
DocumentOCR initialized with engine: tesseract

Methods available:
  extract_text(path)       -> full text as string
  extract_structured(path) -> words with positions
  extract_by_lines(path)   -> text grouped by lines
```

**Line-by-line explanation:**

- `DocumentOCR` wraps the entire OCR pipeline: preprocessing, extraction, and result formatting.
- `preprocess()` applies grayscale conversion, resizing, denoising, and binarization.
- `extract_text()` returns plain text from the entire document.
- `extract_structured()` returns a list of dictionaries with each word, its confidence score, bounding box, and line/block information.
- `extract_by_lines()` groups words by their line number and joins them, giving you one string per text line in the document.
- `config='--psm 3 --oem 3'` tells Tesseract to use fully automatic page segmentation (PSM 3) and the LSTM-based engine (OEM 3), which is the most accurate.

---

## Choosing the Right OCR Tool

```
+------------------+-------------------+-------------------+-------------------+
| Feature          | Tesseract         | EasyOCR           | TrOCR             |
+------------------+-------------------+-------------------+-------------------+
| Type             | Traditional +     | Deep Learning     | Transformer       |
|                  | LSTM              |                   |                   |
+------------------+-------------------+-------------------+-------------------+
| Speed            | Fast              | Moderate          | Slow              |
+------------------+-------------------+-------------------+-------------------+
| Printed text     | Good              | Good              | Excellent         |
+------------------+-------------------+-------------------+-------------------+
| Handwriting      | Poor              | Fair              | Good              |
+------------------+-------------------+-------------------+-------------------+
| Scene text       | Poor              | Excellent         | Good              |
| (signs, labels)  |                   |                   |                   |
+------------------+-------------------+-------------------+-------------------+
| Languages        | 100+              | 80+               | English mainly    |
+------------------+-------------------+-------------------+-------------------+
| GPU needed       | No                | Optional          | Recommended       |
+------------------+-------------------+-------------------+-------------------+
| Best for         | Documents,        | Photos, signs,    | High-accuracy     |
|                  | scanned pages     | multilingual      | text line reading |
+------------------+-------------------+-------------------+-------------------+
| Installation     | System install    | pip install       | pip install       |
|                  | + pip             |                   | (large download)  |
+------------------+-------------------+-------------------+-------------------+
```

### Decision Guide

```
What kind of image do you have?

Scanned document (clean, printed text)?
  -> Use Tesseract (fast, accurate for documents)

Photo of a sign, label, or scene?
  -> Use EasyOCR (handles perspective and varied fonts)

Need to read handwriting?
  -> Use TrOCR handwritten model

Non-English text?
  -> Use EasyOCR (best multilingual support)

Need maximum accuracy on printed text?
  -> Use TrOCR printed model

Processing thousands of images?
  -> Use Tesseract (fastest) with good preprocessing
```

---

## Common Mistakes

1. **Skipping preprocessing.** Raw photographs often produce terrible OCR results. Always preprocess: convert to grayscale, remove noise, and binarize.

2. **Wrong PSM mode in Tesseract.** Using the default PSM mode on a single text line or a receipt will produce poor results. Match the PSM mode to your document layout.

3. **Not scaling small images.** If text in the image is smaller than about 12 pixels tall, OCR accuracy drops sharply. Scale the image up before running OCR.

4. **Feeding full pages to TrOCR.** TrOCR is designed to process single text lines, not full pages. Crop text lines first, then run TrOCR on each line separately.

5. **Ignoring confidence scores.** Low-confidence results are often wrong. Filter by confidence to avoid garbage output.

---

## Best Practices

1. **Always preprocess images** before running OCR. The preprocessing steps in this chapter can transform OCR accuracy from mediocre to excellent.

2. **Choose the right tool for the job.** Tesseract for documents, EasyOCR for scenes and multilingual text, TrOCR for maximum accuracy on text lines.

3. **Use the correct PSM mode** in Tesseract. PSM 3 for full pages, PSM 6 for uniform text blocks, PSM 7 for single lines, PSM 8 for single words.

4. **Validate OCR output.** Use spell checkers, regular expressions, or domain-specific rules to catch and fix common OCR errors.

5. **Keep original images.** Always store the original image alongside the OCR output. OCR is not perfect, and you may need to re-extract text with better settings later.

---

## Quick Summary

OCR converts images of text into machine-readable strings. Tesseract is the most established OCR engine, working best with preprocessed document images and offering many configuration options including page segmentation modes and language support. Preprocessing is critical: grayscale conversion, noise removal, binarization, and deskewing can dramatically improve accuracy. EasyOCR is a deep learning based alternative that excels at reading text in natural scenes (signs, labels) and supports over 80 languages. TrOCR from Hugging Face uses a transformer architecture to achieve the highest accuracy on text lines, especially for handwriting. Each tool has its strengths, and the right choice depends on your specific use case.

---

## Key Points

- **OCR** converts images of text into editable, searchable text strings
- **Tesseract** is fast and works best on clean, preprocessed documents
- **Preprocessing** (grayscale, denoise, threshold, deskew) dramatically improves accuracy
- **Adaptive thresholding** handles uneven lighting better than global thresholding
- **EasyOCR** uses deep learning and excels at scene text and multilingual OCR
- **TrOCR** uses transformers for state-of-the-art text line recognition
- **PSM modes** in Tesseract must match the document layout for best results
- **Confidence scores** help filter out unreliable recognition results

---

## Practice Questions

1. What are the three main steps of an OCR pipeline? Explain what happens at each step.

2. Why is adaptive thresholding better than global thresholding for photographs of documents? Give a specific scenario.

3. When would you choose EasyOCR over Tesseract? When would Tesseract be the better choice?

4. TrOCR processes single text lines, not full pages. How would you use TrOCR to extract text from a full document page?

5. A user complains that their OCR output contains many errors when processing photos of receipts. What preprocessing steps would you recommend to improve the results?

---

## Exercises

### Exercise 1: Build a Receipt Scanner

Create a Python script that takes a photo of a receipt (you can find sample receipt images online), preprocesses it, extracts the text using Tesseract, and attempts to identify the total amount using string matching or regular expressions.

### Exercise 2: Compare OCR Engines

Take the same image and run OCR using both Tesseract and EasyOCR. Compare the extracted text, measure the time each engine takes, and calculate a simple accuracy metric (number of correctly recognized words divided by total words, checked manually).

### Exercise 3: Multi-Page Document Processor

Write a function that takes a folder of document page images, runs OCR on each page in order, and combines the results into a single text file. Include page numbers and handle errors gracefully (if OCR fails on one page, log the error and continue with the next page).

---

## What Is Next?

Congratulations! You have now covered the fundamental techniques of both NLP and Computer Vision. Starting with the next chapter, you will put everything together in hands-on projects. Chapter 25 walks you through building a complete Sentiment Analysis API: fine-tuning a DistilBERT model on movie reviews and serving predictions through a FastAPI endpoint. This is where theory becomes a real, deployable application.
