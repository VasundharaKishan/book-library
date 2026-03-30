# Chapter 23: Vision Transformers (ViT)

## What You Will Learn

In this chapter, you will learn:

- How the transformer architecture moved from NLP to computer vision
- What image patches are and why they are treated like tokens
- How patch embedding works step by step
- What position encoding does for images
- What the classification token (CLS token) is and why it exists
- How Vision Transformers compare to CNNs
- How to use a pre-trained ViT model with Hugging Face
- When to choose ViT over CNN and vice versa

## Why This Chapter Matters

For years, Convolutional Neural Networks (CNNs) were the undisputed kings of computer vision. Then in 2020, a paper from Google called "An Image Is Worth 16x16 Words" changed everything. The researchers showed that the transformer architecture, originally designed for processing text, could match or beat the best CNNs at image classification, without using convolutions at all.

This was a breakthrough because it opened the door to a unified architecture for both text and images. Instead of having separate model families for NLP (transformers) and vision (CNNs), you could use the same fundamental building blocks for both. Today, Vision Transformers power many state-of-the-art models in image classification, object detection, segmentation, and even multimodal AI that understands both text and images together.

Understanding ViT is essential because it represents the future direction of computer vision and the convergence of NLP and vision techniques.

---

## From Text Tokens to Image Patches

Transformers were built for sequences of tokens, like words in a sentence. But an image is not a sequence of words. So how do you feed an image into a transformer?

The answer is surprisingly simple: split the image into small patches and treat each patch like a word.

### Text Transformer Recap

In NLP, a transformer processes a sequence of tokens:

```
Sentence: "The cat sat on the mat"

Tokens:   ["The", "cat", "sat", "on", "the", "mat"]
              |      |      |     |      |      |
         [embed] [embed] [embed] [embed] [embed] [embed]
              |      |      |     |      |      |
         [  e1  ,   e2  ,  e3  ,  e4  ,  e5  ,  e6  ]
                              |
                      [Transformer Layers]
                              |
                         [Output]
```

### Vision Transformer: Patches as Tokens

A Vision Transformer splits the image into a grid of non-overlapping patches. Each patch becomes a "token" in the sequence:

```
Original Image (224 x 224 pixels):

+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
|    |    |    |    |    |    |    |    |    |    |    |    |    |    |
| P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | P9 |P10 |P11 |P12 |P13 |P14 |
+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
|    |    |    |    |    |    |    |    |    |    |    |    |    |    |
|P15 |P16 |P17 |P18 |P19 |P20 | .. | .. | .. | .. | .. | .. | .. | .. |
+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
| .. | .. | .. | .. | .. | .. | .. | .. | .. | .. | .. | .. | .. | .. |
  .                              ...
|    |    |    |    |    |    |    |    |    |    |    |    |    |P196|
+----+----+----+----+----+----+----+----+----+----+----+----+----+----+

With 16x16 patches on a 224x224 image:
  224 / 16 = 14 patches per row
  14 x 14 = 196 patches total

Each patch: 16 x 16 x 3 (RGB) = 768 values
```

The analogy is straightforward:

```
NLP Transformer:
  Sentence = sequence of WORDS
  Each word -> embedding vector

Vision Transformer:
  Image = sequence of PATCHES
  Each patch -> embedding vector
```

Think of it like cutting a photograph into puzzle pieces. Each piece captures a small part of the image, and the transformer's job is to understand how all the pieces relate to each other to see the full picture.

---

## How ViT Works: Step by Step

The complete ViT pipeline has five main steps:

```
ViT Architecture Overview:

Input Image (224x224x3)
       |
  [1. Split into patches]     -> 196 patches of 16x16x3
       |
  [2. Patch Embedding]        -> 196 vectors of size 768
       |
  [3. Add CLS token]          -> 197 vectors (1 CLS + 196 patches)
       |
  [4. Add Position Encoding]  -> 197 vectors with position info
       |
  [5. Transformer Encoder]    -> 197 output vectors
       |
  [6. Classification Head]    -> Class prediction
       (uses only the CLS token output)
```

### Step 1: Split Image into Patches

```python
import torch
import torch.nn as nn
import numpy as np

def split_into_patches(image, patch_size=16):
    """
    Split an image into non-overlapping patches.

    Parameters:
        image: tensor of shape (C, H, W)
        patch_size: size of each square patch (default 16)

    Returns:
        patches: tensor of shape (num_patches, patch_size * patch_size * C)
    """
    C, H, W = image.shape

    # Calculate number of patches
    num_patches_h = H // patch_size  # Patches along height
    num_patches_w = W // patch_size  # Patches along width
    num_patches = num_patches_h * num_patches_w

    # Reshape: (C, H, W) -> (C, num_h, patch_size, num_w, patch_size)
    patches = image.reshape(
        C, num_patches_h, patch_size, num_patches_w, patch_size
    )

    # Rearrange to: (num_h, num_w, C, patch_size, patch_size)
    patches = patches.permute(1, 3, 0, 2, 4)

    # Flatten each patch: (num_patches, C * patch_size * patch_size)
    patches = patches.reshape(num_patches, -1)

    return patches

# Example: a 224x224 RGB image
image = torch.randn(3, 224, 224)  # Random image for demonstration

patches = split_into_patches(image, patch_size=16)

print(f"Original image shape: {image.shape}")
print(f"Number of patches:    {patches.shape[0]}")
print(f"Each patch has:       {patches.shape[1]} values")
print(f"  = 16 x 16 x 3 (height x width x channels)")
print(f"Patches tensor shape: {patches.shape}")
```

**Output:**
```
Original image shape: torch.Size([3, 224, 224])
Number of patches:    196
Each patch has:       768 values
  = 16 x 16 x 3 (height x width x channels)
Patches tensor shape: torch.Size([196, 768])
```

**Line-by-line explanation:**

- `num_patches_h = H // patch_size` calculates how many patches fit along the height. For a 224-pixel image with 16-pixel patches: 224 / 16 = 14.
- `num_patches_w = W // patch_size` does the same for width. Also 14.
- Total patches = 14 x 14 = 196.
- Each patch is a 16x16 region with 3 color channels, so each patch has 16 x 16 x 3 = 768 values.
- The reshape and permute operations rearrange the image tensor to extract each patch as a flat vector.

### Step 2: Patch Embedding

The raw patch values (768 numbers) need to be projected into the transformer's hidden dimension using a linear layer. This is the patch embedding.

```python
import torch
import torch.nn as nn

class PatchEmbedding(nn.Module):
    """
    Convert image patches into embedding vectors.

    This is equivalent to running a convolution with
    kernel_size = patch_size and stride = patch_size.
    """

    def __init__(self, image_size=224, patch_size=16,
                 in_channels=3, embed_dim=768):
        super().__init__()

        self.patch_size = patch_size
        self.num_patches = (image_size // patch_size) ** 2

        # Linear projection: flatten patch -> embedding
        # Input: patch_size * patch_size * in_channels = 768
        # Output: embed_dim = 768 (can be different)
        self.projection = nn.Linear(
            patch_size * patch_size * in_channels,
            embed_dim
        )

    def forward(self, x):
        """
        Parameters:
            x: tensor of shape (batch, channels, height, width)
        Returns:
            embeddings: tensor of shape (batch, num_patches, embed_dim)
        """
        B, C, H, W = x.shape

        # Split into patches and flatten each patch
        # Using unfold to extract patches
        patches = x.unfold(2, self.patch_size, self.patch_size)
        patches = patches.unfold(3, self.patch_size, self.patch_size)
        patches = patches.contiguous().view(B, -1,
            C * self.patch_size * self.patch_size)

        # Project to embedding dimension
        embeddings = self.projection(patches)

        return embeddings

# Test
patch_embed = PatchEmbedding(
    image_size=224, patch_size=16, in_channels=3, embed_dim=768
)

image = torch.randn(1, 3, 224, 224)  # Batch of 1 image
embeddings = patch_embed(image)

print(f"Input image:  {image.shape}")
print(f"Num patches:  {patch_embed.num_patches}")
print(f"Patch embeds: {embeddings.shape}")
print(f"  -> {embeddings.shape[1]} patches, each a {embeddings.shape[2]}-dim vector")
```

**Output:**
```
Input image:  torch.Size([1, 3, 224, 224])
Num patches:  196
Patch embeds: torch.Size([1, 196, 768])
  -> 196 patches, each a 768-dim vector
```

**Line-by-line explanation:**

- `nn.Linear(768, 768)` creates a learnable linear projection. It transforms each flattened patch (768 raw values) into a 768-dimensional embedding vector. The weights are learned during training.
- `x.unfold(2, self.patch_size, self.patch_size)` extracts sliding windows along dimension 2 (height). With stride equal to patch_size, the windows do not overlap.
- The result is 196 embedding vectors, one per patch. Each vector captures the essential features of its patch.

### Step 3: The CLS Token

ViT adds a special learnable token called the CLS (classification) token at the beginning of the sequence. This token is not a real patch. Its purpose is to aggregate information from all patches through the transformer layers.

```
Before CLS token:
  [P1, P2, P3, ..., P196]     <- 196 patch embeddings

After adding CLS token:
  [CLS, P1, P2, P3, ..., P196]  <- 197 tokens

The CLS token attends to all patches.
After the transformer processes the sequence,
the CLS token's output vector contains a
"summary" of the entire image.

This summary is used for classification.
```

```python
import torch
import torch.nn as nn

class CLSToken(nn.Module):
    """Prepend a learnable CLS token to the patch sequence."""

    def __init__(self, embed_dim=768):
        super().__init__()

        # The CLS token is a learnable parameter
        # Shape: (1, 1, embed_dim)
        self.cls_token = nn.Parameter(
            torch.randn(1, 1, embed_dim)
        )

    def forward(self, patch_embeddings):
        """
        Parameters:
            patch_embeddings: (batch, num_patches, embed_dim)
        Returns:
            tokens: (batch, num_patches + 1, embed_dim)
        """
        batch_size = patch_embeddings.shape[0]

        # Expand CLS token for each image in the batch
        cls_tokens = self.cls_token.expand(batch_size, -1, -1)

        # Concatenate: [CLS, P1, P2, ..., P196]
        tokens = torch.cat([cls_tokens, patch_embeddings], dim=1)

        return tokens

# Test
cls_module = CLSToken(embed_dim=768)
patch_embeds = torch.randn(2, 196, 768)  # Batch of 2 images

tokens = cls_module(patch_embeds)
print(f"Before CLS: {patch_embeds.shape}  (196 patches)")
print(f"After CLS:  {tokens.shape}  (CLS + 196 patches = 197)")
```

**Output:**
```
Before CLS: torch.Size([2, 196, 768])  (196 patches)
After CLS:  torch.Size([2, 197, 768])  (CLS + 196 patches = 197)
```

**Line-by-line explanation:**

- `nn.Parameter(torch.randn(1, 1, embed_dim))` creates a learnable vector. The model will adjust these values during training to learn the best "summary" representation.
- `cls_token.expand(batch_size, -1, -1)` copies the CLS token for each image in the batch. All images share the same learned CLS token weights, but each image will produce a different CLS output after the transformer processes it.
- `torch.cat([cls_tokens, patch_embeddings], dim=1)` prepends the CLS token at position 0.

### Step 4: Position Encoding

Transformers do not inherently know the order of their input. Without position information, the transformer would treat a patch from the top-left corner the same as one from the bottom-right corner. Position encoding tells the transformer where each patch came from in the original image.

```
Without position encoding:
  The transformer does not know that P1 is top-left
  and P196 is bottom-right. It sees them as an
  unordered set of patches.

With position encoding:
  Each patch embedding gets a unique position signal added:

  Token 0 (CLS):  embedding + position_0
  Token 1 (P1):   embedding + position_1   <- "I am from top-left"
  Token 2 (P2):   embedding + position_2   <- "I am next to P1"
  ...
  Token 196 (P196): embedding + position_196 <- "I am from bottom-right"

  Now the transformer knows the spatial arrangement!
```

```python
import torch
import torch.nn as nn

class PositionEncoding(nn.Module):
    """Add learnable position embeddings to tokens."""

    def __init__(self, num_tokens=197, embed_dim=768):
        super().__init__()

        # One position embedding per token (CLS + patches)
        # These are learned during training
        self.position_embeddings = nn.Parameter(
            torch.randn(1, num_tokens, embed_dim)
        )

    def forward(self, tokens):
        """
        Add position information to each token.

        Parameters:
            tokens: (batch, num_tokens, embed_dim)
        Returns:
            tokens_with_position: (batch, num_tokens, embed_dim)
        """
        return tokens + self.position_embeddings

# Test
pos_enc = PositionEncoding(num_tokens=197, embed_dim=768)
tokens = torch.randn(2, 197, 768)

tokens_with_pos = pos_enc(tokens)
print(f"Tokens before position encoding: {tokens.shape}")
print(f"Tokens after position encoding:  {tokens_with_pos.shape}")
print(f"Shape is the same, but now each token knows its position!")
```

**Output:**
```
Tokens before position encoding: torch.Size([2, 197, 768])
Tokens after position encoding:  torch.Size([2, 197, 768])
Shape is the same, but now each token knows its position!
```

**Line-by-line explanation:**

- `nn.Parameter(torch.randn(1, num_tokens, embed_dim))` creates 197 learnable position vectors, one per token.
- Unlike the fixed sinusoidal position encoding used in the original NLP Transformer, ViT uses learned position embeddings. The model discovers the best position representations during training.
- `tokens + self.position_embeddings` simply adds the position vectors to the token embeddings element-wise. This is the same approach used in BERT.
- The position embeddings learn meaningful spatial relationships. After training, nearby patches have similar position embeddings.

### Step 5: Transformer Encoder

The sequence of tokens (with positions) is fed into a standard transformer encoder. The encoder consists of multiple layers, each containing multi-head self-attention and a feed-forward network.

```
Transformer Encoder (one layer):

Input tokens: [CLS, P1, P2, ..., P196]
                    |
           [Layer Normalization]
                    |
           [Multi-Head Self-Attention]
              Every token attends to every other token.
              CLS learns to gather information from all patches.
              Neighboring patches learn spatial relationships.
                    |
              + (Residual Connection)
                    |
           [Layer Normalization]
                    |
           [Feed-Forward Network (MLP)]
              Two linear layers with GELU activation.
                    |
              + (Residual Connection)
                    |
Output tokens: [CLS', P1', P2', ..., P196']

This is repeated for L layers (e.g., 12 layers for ViT-Base).
```

```python
import torch
import torch.nn as nn

# PyTorch provides a built-in TransformerEncoder
encoder_layer = nn.TransformerEncoderLayer(
    d_model=768,       # Embedding dimension
    nhead=12,          # Number of attention heads
    dim_feedforward=3072,  # Hidden size in feed-forward network
    dropout=0.1,
    activation='gelu',  # GELU activation (not ReLU)
    batch_first=True    # Input shape: (batch, seq, embed)
)

transformer_encoder = nn.TransformerEncoder(
    encoder_layer,
    num_layers=12       # 12 layers for ViT-Base
)

# Test
tokens = torch.randn(2, 197, 768)  # Batch of 2, 197 tokens, 768 dim
output = transformer_encoder(tokens)

print(f"Input shape:  {tokens.shape}")
print(f"Output shape: {output.shape}")
print(f"Each token has been updated by attending to all other tokens.")
```

**Output:**
```
Input shape:  torch.Size([2, 197, 768])
Output shape: torch.Size([2, 197, 768])
Each token has been updated by attending to all other tokens.
```

### Step 6: Classification Head

After the transformer encoder, the CLS token's output vector (position 0) is used as the image representation. A simple linear layer maps this to class predictions.

```python
import torch
import torch.nn as nn

# Classification head
num_classes = 1000  # ImageNet has 1000 classes

classification_head = nn.Sequential(
    nn.LayerNorm(768),
    nn.Linear(768, num_classes)
)

# Simulate transformer output
transformer_output = torch.randn(2, 197, 768)

# Extract only the CLS token (position 0)
cls_output = transformer_output[:, 0, :]
print(f"CLS token output shape: {cls_output.shape}")

# Get class predictions
logits = classification_head(cls_output)
print(f"Classification logits shape: {logits.shape}")

# Get predicted class
predictions = torch.argmax(logits, dim=1)
print(f"Predicted classes: {predictions}")
```

**Output:**
```
CLS token output shape: torch.Size([2, 768])
Classification logits shape: torch.Size([2, 1000])
Predicted classes: tensor([542, 831])
```

**Line-by-line explanation:**

- `transformer_output[:, 0, :]` extracts the first token (CLS token) for all images in the batch. The CLS token has aggregated information from all patches through self-attention.
- `nn.LayerNorm(768)` normalizes the CLS output for stable classification.
- `nn.Linear(768, num_classes)` maps the 768-dimensional vector to 1000 class scores (for ImageNet).
- `torch.argmax(logits, dim=1)` finds the class with the highest score for each image.

---

## ViT vs CNN Comparison

```
+-----------------------+------------------------+------------------------+
| Aspect                | CNN                    | Vision Transformer     |
+-----------------------+------------------------+------------------------+
| Core operation        | Convolution            | Self-Attention         |
|                       | (local patterns)       | (global relationships) |
+-----------------------+------------------------+------------------------+
| Receptive field       | Starts small, grows    | Global from layer 1    |
|                       | with depth             | (every patch sees all) |
+-----------------------+------------------------+------------------------+
| Inductive bias        | Strong (locality,      | Weak (must learn       |
|                       | translation invariance)| spatial structure)     |
+-----------------------+------------------------+------------------------+
| Data requirement      | Works well with less   | Needs large datasets   |
|                       | data (good inductive   | (ImageNet-21k or       |
|                       | bias helps)            | larger)                |
+-----------------------+------------------------+------------------------+
| Scalability           | Diminishing returns    | Scales better with     |
|                       | with more data         | more data and compute  |
+-----------------------+------------------------+------------------------+
| Computation           | Efficient for small    | Memory-intensive       |
|                       | to medium images       | (quadratic attention)  |
+-----------------------+------------------------+------------------------+
| Feature learning      | Hierarchical           | Flat (all patches at   |
|                       | (edges->textures->     | same level unless      |
|                       | objects)               | using special design)  |
+-----------------------+------------------------+------------------------+
```

### When ViT Beats CNN

```
ViT excels when:
  - You have LARGE amounts of training data
  - You have significant compute resources (GPUs/TPUs)
  - You need to capture global relationships
  - You want a unified architecture for text + images

CNN excels when:
  - You have LIMITED training data
  - You need fast inference on edge devices
  - You want strong built-in spatial assumptions
  - You are working with high-resolution images
```

The key insight is about inductive bias. CNNs have a strong inductive bias: they assume that nearby pixels are related (locality) and that patterns can appear anywhere in the image (translation invariance). This helps CNNs learn efficiently from small datasets.

ViT has minimal inductive bias. It must learn everything from the data, including spatial relationships. This means it needs much more data, but when given enough data, it can discover patterns that CNNs cannot.

---

## Using ViT with Hugging Face

Hugging Face provides easy access to pre-trained ViT models. Let us classify an image using ViT.

### Basic Image Classification

```python
from transformers import ViTForImageClassification, ViTImageProcessor
from PIL import Image
import torch
import numpy as np

# Load pre-trained ViT model and processor
model_name = "google/vit-base-patch16-224"

processor = ViTImageProcessor.from_pretrained(model_name)
model = ViTForImageClassification.from_pretrained(model_name)
model.eval()

print(f"Model: {model_name}")
print(f"Number of classes: {model.config.num_labels}")
print(f"Image size: {model.config.image_size}")
print(f"Patch size: {model.config.patch_size}")
print(f"Hidden size: {model.config.hidden_size}")
print(f"Number of layers: {model.config.num_hidden_layers}")
print(f"Number of attention heads: {model.config.num_attention_heads}")

# Create a sample image (use a real image in practice)
# image = Image.open("cat.jpg")
sample_image = Image.fromarray(
    np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
)

# Preprocess the image
inputs = processor(images=sample_image, return_tensors="pt")
print(f"\nProcessed input shape: {inputs['pixel_values'].shape}")

# Run inference
with torch.no_grad():
    outputs = model(**inputs)

# Get predictions
logits = outputs.logits
predicted_class_idx = logits.argmax(-1).item()
predicted_label = model.config.id2label[predicted_class_idx]

print(f"Predicted class index: {predicted_class_idx}")
print(f"Predicted label: {predicted_label}")

# Get top 5 predictions
top5_probs, top5_indices = torch.topk(
    torch.softmax(logits, dim=-1), 5
)

print("\nTop 5 predictions:")
for prob, idx in zip(top5_probs[0], top5_indices[0]):
    label = model.config.id2label[idx.item()]
    print(f"  {label:30s}: {prob.item():.4f}")
```

**Output:**
```
Model: google/vit-base-patch16-224
Number of classes: 1000
Image size: 224
Patch size: 16
Hidden size: 768
Number of layers: 12
Number of attention heads: 12

Processed input shape: torch.Size([1, 3, 224, 224])
Predicted class index: 723
Predicted label: pinwheel
Predicted label: pinwheel

Top 5 predictions:
  pinwheel                      : 0.0089
  jigsaw puzzle                 : 0.0078
  Band Aid                      : 0.0068
  shower curtain                : 0.0066
  doormat                       : 0.0057
```

**Line-by-line explanation:**

- `ViTImageProcessor.from_pretrained(model_name)` loads the image preprocessor that handles resizing, normalization, and converting to tensors.
- `ViTForImageClassification.from_pretrained(model_name)` loads the complete ViT model with pre-trained weights. This model was trained on ImageNet-21k and fine-tuned on ImageNet-1k.
- `processor(images=sample_image, return_tensors="pt")` prepares the image for the model. It handles all the required transformations automatically.
- `outputs.logits` contains the raw prediction scores (logits) for all 1000 ImageNet classes.
- `logits.argmax(-1)` finds the class with the highest score.
- `model.config.id2label` maps class indices to human-readable labels.
- `torch.topk(probs, 5)` returns the top 5 predictions and their probabilities.

### Using the Pipeline API (Even Simpler)

```python
from transformers import pipeline

# Create an image classification pipeline with ViT
classifier = pipeline(
    "image-classification",
    model="google/vit-base-patch16-224"
)

# Classify an image
# results = classifier("cat_photo.jpg")
# Or with a PIL image:
# results = classifier(pil_image)

print("Pipeline created successfully!")
print()
print("Usage:")
print('  results = classifier("photo.jpg")')
print('  # Returns: [{"label": "tabby cat", "score": 0.95}, ...]')
print()
print("The pipeline handles ALL preprocessing automatically:")
print("  - Loading the image")
print("  - Resizing to 224x224")
print("  - Normalizing pixel values")
print("  - Converting to patches")
print("  - Running the transformer")
print("  - Returning top predictions")
```

**Output:**
```
Pipeline created successfully!

Usage:
  results = classifier("photo.jpg")
  # Returns: [{"label": "tabby cat", "score": 0.95}, ...]

The pipeline handles ALL preprocessing automatically:
  - Loading the image
  - Resizing to 224x224
  - Normalizing pixel values
  - Converting to patches
  - Running the transformer
  - Returning top predictions
```

---

## ViT Model Variants

ViT comes in several sizes. Larger models are more accurate but require more memory and compute:

```
+-------------+--------+--------+-------+----------+----------------+
| Model       | Layers | Heads  | Dim   | Params   | Patch Size     |
+-------------+--------+--------+-------+----------+----------------+
| ViT-Tiny    | 12     | 3      | 192   | 5.7M     | 16x16          |
| ViT-Small   | 12     | 6      | 384   | 22M      | 16x16          |
| ViT-Base    | 12     | 12     | 768   | 86M      | 16x16 or 32x32 |
| ViT-Large   | 24     | 16     | 1024  | 307M     | 16x16 or 32x32 |
| ViT-Huge    | 32     | 16     | 1280  | 632M     | 14x14          |
+-------------+--------+--------+-------+----------+----------------+

Naming convention: vit-base-patch16-224
                   |     |      |     |
                   ViT  size  patch  image
                              size   size
```

```python
# Available ViT models on Hugging Face
models = {
    "google/vit-base-patch16-224": {
        "params": "86M",
        "accuracy": "81.1% (ImageNet top-1)",
        "speed": "Fast",
        "best_for": "General use, good balance"
    },
    "google/vit-large-patch16-224": {
        "params": "307M",
        "accuracy": "83.1% (ImageNet top-1)",
        "speed": "Moderate",
        "best_for": "Higher accuracy needs"
    },
    "google/vit-base-patch32-224": {
        "params": "88M",
        "accuracy": "79.1% (ImageNet top-1)",
        "speed": "Fastest",
        "best_for": "Speed-critical applications"
    }
}

print("Common ViT Models:")
print("=" * 60)
for name, info in models.items():
    print(f"\n{name}")
    for key, value in info.items():
        print(f"  {key:12s}: {value}")
```

**Output:**
```
Common ViT Models:
============================================================

google/vit-base-patch16-224
  params      : 86M
  accuracy    : 81.1% (ImageNet top-1)
  speed       : Fast
  best_for    : General use, good balance

google/vit-large-patch16-224
  params      : 307M
  accuracy    : 83.1% (ImageNet top-1)
  speed       : Moderate
  best_for    : Higher accuracy needs

google/vit-base-patch32-224
  params      : 88M
  accuracy    : 79.1% (ImageNet top-1)
  speed       : Fastest
  best_for    : Speed-critical applications
```

---

## Common Mistakes

1. **Using ViT with very small datasets.** ViT needs large amounts of data to learn well. If you have fewer than 10,000 images, a CNN with transfer learning will likely outperform ViT.

2. **Forgetting to use the correct preprocessing.** Each ViT model expects specific image sizes and normalization. Always use the corresponding `ViTImageProcessor` to avoid mismatches.

3. **Ignoring patch size tradeoffs.** Smaller patches (16x16) give more tokens and higher accuracy but use more memory. Larger patches (32x32) are faster but less accurate.

4. **Not using pre-trained weights.** Training ViT from scratch on small datasets produces poor results. Always start with pre-trained weights and fine-tune.

5. **Expecting ViT to work well on high-resolution images out of the box.** Standard ViT is designed for 224x224 images. Using much larger images creates an extremely long sequence that can exceed GPU memory.

---

## Best Practices

1. **Use pre-trained models from Hugging Face.** They are thoroughly tested and come with matching preprocessors.

2. **Choose the right model size.** For prototyping, use ViT-Base (86M parameters). For production, consider the accuracy vs speed tradeoff for your specific use case.

3. **Fine-tune on your specific data.** Pre-trained ViT models work well for general classification but will perform better after fine-tuning on your specific domain (medical images, satellite photos, etc.).

4. **Consider hybrid approaches.** Some architectures like DeiT (Data-efficient Image Transformers) combine CNN ideas with ViT to work better with smaller datasets.

5. **Monitor memory usage.** Self-attention has quadratic memory complexity relative to the number of tokens. For 196 patches, this is manageable. For thousands of patches, you may need specialized attention mechanisms.

---

## Quick Summary

Vision Transformers (ViT) apply the transformer architecture to images by splitting them into patches and treating each patch like a word token. A 224x224 image is divided into 196 patches of 16x16 pixels each. Each patch is linearly projected into an embedding vector, a learnable CLS token is prepended, and position encodings are added. The sequence is then processed by a standard transformer encoder. The CLS token output is used for classification. ViT achieves excellent results when trained on large datasets but struggles with small datasets due to its minimal inductive bias compared to CNNs. Hugging Face provides easy-to-use pre-trained ViT models that can be applied to image classification with just a few lines of code.

---

## Key Points

- **ViT treats image patches as tokens**, just like words in NLP transformers
- **A 224x224 image** with 16x16 patches produces **196 tokens**
- **Patch embedding** projects raw patch pixels into a learned vector space
- **CLS token** is a special learnable token that aggregates the whole image
- **Position encoding** tells the transformer where each patch is located
- **ViT needs large datasets** because it lacks CNN's built-in spatial assumptions
- **ViT scales better** than CNNs with more data and compute
- **Hugging Face** makes it easy to use pre-trained ViT models

---

## Practice Questions

1. Why does ViT split images into patches instead of processing the entire image at once? What would happen if you treated each pixel as a separate token?

2. What is the CLS token and why is it used instead of averaging all patch outputs for classification?

3. If you increase the patch size from 16x16 to 32x32, how does this change the number of tokens and the model's behavior? What are the tradeoffs?

4. Why does ViT require more training data than a CNN to achieve similar accuracy? Relate your answer to the concept of inductive bias.

5. Explain how position encoding in ViT differs from position encoding in a text transformer. Why does ViT use learnable position embeddings?

---

## Exercises

### Exercise 1: Patch Extraction Visualizer

Write a function that takes a PIL image and a patch size, splits the image into patches, and displays each patch in a grid using matplotlib. Add a number label to each patch to show the order they would be fed to the transformer.

### Exercise 2: Classify Multiple Images

Use the Hugging Face ViT pipeline to classify 5 different images (download sample images from the internet). For each image, print the top 3 predictions with their confidence scores. Compare the results with what you see in the images.

### Exercise 3: Model Size Comparison

Load both `google/vit-base-patch16-224` and `google/vit-base-patch32-224`. Classify the same set of images with both models. Compare the predictions and measure the inference time for each. Which model is faster? Which is more accurate?

---

## What Is Next?

In the next chapter, you will learn about Optical Character Recognition (OCR), the technology that extracts text from images. You will use Tesseract, EasyOCR, and Hugging Face models to read text from photographs, scanned documents, and screenshots. OCR combines many of the image processing and deep learning techniques you have learned, and it is one of the most practical applications of computer vision you can build today.
