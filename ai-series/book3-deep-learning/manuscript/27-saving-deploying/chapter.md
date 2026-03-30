# Chapter 27: Saving, Loading, and Deploying Models

## What You Will Learn

In this chapter, you will learn:

- How to save and load PyTorch models using `torch.save` and `torch.load`
- The difference between saving the `state_dict` and saving the entire model
- How to create checkpoints during training so you never lose progress
- How to export models to ONNX format for cross-platform deployment
- How to use TorchScript to optimize models for production
- How to load a saved model and run inference
- Model size considerations and how to reduce them
- How to serve your model through a simple Flask or FastAPI web API

## Why This Chapter Matters

Training a deep learning model can take hours, days, or even weeks. Imagine spending three days training a model, only to lose everything because your computer restarted and you forgot to save. Or imagine training a fantastic image classifier but having no way to let other people use it.

Saving and deploying models is the bridge between research and real-world impact. A model sitting in a Jupyter notebook helps no one. A model deployed as a web service can serve millions of users. This chapter teaches you the practical skills that turn your trained models into usable products.

Think of it like writing a book. Training the model is like writing the manuscript. Saving the model is like printing the book. Deploying the model is like putting the book in libraries and bookstores where people can actually read it.

---

## 27.1 Saving Models with `torch.save`

PyTorch provides two main approaches to save a model:

### Approach 1: Saving the `state_dict` (Recommended)

The `state_dict` is a Python dictionary that maps each layer name to its parameter tensor (weights and biases). This is the recommended approach.

```python
import torch
import torch.nn as nn

# Define a simple model for demonstration
class SimpleClassifier(nn.Module):
    def __init__(self, input_size=784, hidden_size=256, num_classes=10):
        super(SimpleClassifier, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        x = x.view(x.size(0), -1)
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Create and train a model (assuming it has been trained)
model = SimpleClassifier()

# Save only the state_dict
torch.save(model.state_dict(), 'model_weights.pth')
print("Model weights saved!")

# Check what is inside the state_dict
for name, param in model.state_dict().items():
    print(f"  {name}: shape={param.shape}")
```

**Expected output:**
```
Model weights saved!
  fc1.weight: shape=torch.Size([256, 784])
  fc1.bias: shape=torch.Size([256])
  fc2.weight: shape=torch.Size([10, 256])
  fc2.bias: shape=torch.Size([10])
```

**Line-by-line explanation:**

- `model.state_dict()`: Returns a dictionary containing all the learned parameters. Each key is the layer name (like `fc1.weight`) and each value is the tensor of weights.

- `torch.save(model.state_dict(), 'model_weights.pth')`: Saves the dictionary to a file. The `.pth` extension is a convention for PyTorch files (it stands for "PyTorch"). You could also use `.pt`.

### Loading the state_dict

To load the weights, you first create the model architecture, then load the weights into it:

```python
# Create a new model with the same architecture
loaded_model = SimpleClassifier()

# Load the saved weights
loaded_model.load_state_dict(torch.load('model_weights.pth'))

# Set to evaluation mode for inference
loaded_model.eval()

print("Model loaded successfully!")
```

**Expected output:**
```
Model loaded successfully!
```

**Line-by-line explanation:**

- `SimpleClassifier()`: You must recreate the exact same model architecture. The code for the model class must be available.

- `torch.load('model_weights.pth')`: Loads the saved dictionary from disk.

- `loaded_model.load_state_dict(...)`: Copies all the parameters from the dictionary into the model's layers.

- `loaded_model.eval()`: Switches to evaluation mode. This is important because some layers (like BatchNorm and Dropout) behave differently during training and evaluation.

### Approach 2: Saving the Entire Model

You can save the entire model object, including its architecture:

```python
# Save entire model
torch.save(model, 'model_complete.pth')
print("Complete model saved!")

# Load entire model
loaded_model_complete = torch.load('model_complete.pth')
loaded_model_complete.eval()
print("Complete model loaded!")
```

**Expected output:**
```
Complete model saved!
Complete model loaded!
```

### Which Approach Should You Use?

```
ASCII Diagram: Comparing the Two Approaches

    +--------------------+------------------+---------------------+
    |                    | state_dict       | Entire Model        |
    +--------------------+------------------+---------------------+
    | What is saved      | Just weights     | Weights + structure |
    +--------------------+------------------+---------------------+
    | File size          | Smaller          | Larger              |
    +--------------------+------------------+---------------------+
    | Flexibility        | High (can modify | Low (tied to exact  |
    |                    | architecture)    | code version)       |
    +--------------------+------------------+---------------------+
    | Portability        | Need model class | More self-contained |
    |                    | code to load     | but fragile         |
    +--------------------+------------------+---------------------+
    | Recommended?       | YES              | Only for quick      |
    |                    |                  | prototyping         |
    +--------------------+------------------+---------------------+
```

**Use `state_dict` (Approach 1)** in almost all cases. It is more flexible, more portable, and less likely to break when you update your code.

**Avoid Approach 2** for production. It uses Python's `pickle` module internally, which ties the saved file to the exact Python class structure and file paths. If you rename a file or move code, loading can break.

---

## 27.2 Checkpointing During Training

Training can take a long time. Checkpointing saves your progress periodically so you can resume if something goes wrong.

A good checkpoint saves everything needed to resume training:

```python
def save_checkpoint(model, optimizer, epoch, loss, filepath):
    """Save a complete training checkpoint."""
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': loss,
    }
    torch.save(checkpoint, filepath)
    print(f"Checkpoint saved at epoch {epoch}")

def load_checkpoint(filepath, model, optimizer=None):
    """Load a training checkpoint."""
    checkpoint = torch.load(filepath)

    model.load_state_dict(checkpoint['model_state_dict'])
    start_epoch = checkpoint['epoch']
    loss = checkpoint['loss']

    if optimizer is not None:
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

    print(f"Checkpoint loaded from epoch {start_epoch}, loss: {loss:.4f}")
    return start_epoch, loss
```

**Line-by-line explanation:**

- `checkpoint = {...}`: We create a dictionary containing everything needed to resume training. This includes the model weights, optimizer state (which tracks momentum and learning rate schedules), the current epoch number, and the current loss.

- `optimizer.state_dict()`: The optimizer has its own state (like running averages for Adam). Saving this ensures training resumes exactly where it left off.

### Using Checkpoints in a Training Loop

```python
import torch.optim as optim

# Setup
model = SimpleClassifier()
optimizer = optim.Adam(model.parameters(), lr=0.001)
criterion = nn.CrossEntropyLoss()

# Simulated training loop with checkpointing
num_epochs = 50
checkpoint_every = 10  # Save every 10 epochs

# Check if a checkpoint exists to resume from
import os
start_epoch = 0
if os.path.exists('checkpoint_latest.pth'):
    start_epoch, _ = load_checkpoint(
        'checkpoint_latest.pth', model, optimizer
    )
    start_epoch += 1  # Start from the next epoch
    print(f"Resuming from epoch {start_epoch}")

for epoch in range(start_epoch, num_epochs):
    # ... training code here ...
    train_loss = 0.1  # Placeholder for actual training loss

    # Save checkpoint periodically
    if (epoch + 1) % checkpoint_every == 0:
        save_checkpoint(model, optimizer, epoch, train_loss,
                       f'checkpoint_epoch_{epoch+1}.pth')

    # Always save the latest checkpoint (overwrite)
    save_checkpoint(model, optimizer, epoch, train_loss,
                   'checkpoint_latest.pth')

print("Training complete!")
```

**Expected output:**
```
Checkpoint saved at epoch 0
Checkpoint saved at epoch 1
...
Checkpoint saved at epoch 9
Checkpoint saved at epoch 9
Checkpoint saved at epoch 10
...
Training complete!
```

### Saving the Best Model

Often you want to save the model that performed best on the validation set, not just the latest one:

```python
best_val_loss = float('inf')

for epoch in range(num_epochs):
    # Training phase
    train_loss = 0.1  # Placeholder

    # Validation phase
    val_loss = 0.08  # Placeholder

    # Save if this is the best model so far
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        torch.save(model.state_dict(), 'best_model.pth')
        print(f"  New best model saved! Val loss: {val_loss:.4f}")
```

```
ASCII Diagram: Checkpoint Strategy

    Training Progress:
    Epoch: 0    10    20    30    40    50
           |     |     |     |     |     |
           +     C     C     C     C     C    C = periodic checkpoint
           B           B                B     B = best model (saved when
                                                   val_loss improves)
           L     L     L     L     L     L    L = latest checkpoint
                                                   (always overwritten)
```

---

## 27.3 Loading Models for Inference

Once you have a trained model, here is how to use it for predictions:

```python
def run_inference(model_path, input_data, device='cpu'):
    """Load a model and make predictions."""
    # 1. Create the model architecture
    model = SimpleClassifier()

    # 2. Load trained weights
    model.load_state_dict(torch.load(model_path, map_location=device))

    # 3. Set to evaluation mode
    model.eval()

    # 4. Move to correct device
    model = model.to(device)

    # 5. Run inference with no gradient computation
    with torch.no_grad():
        input_tensor = input_data.to(device)
        output = model(input_tensor)

        # Get predicted class
        probabilities = torch.softmax(output, dim=1)
        predicted_class = torch.argmax(probabilities, dim=1)

    return predicted_class, probabilities

# Example usage
dummy_input = torch.randn(1, 1, 28, 28)  # One 28x28 image
predicted, probs = run_inference('model_weights.pth', dummy_input)
print(f"Predicted class: {predicted.item()}")
print(f"Confidence: {probs.max().item():.2%}")
```

**Expected output:**
```
Predicted class: 3
Confidence: 24.56%
```

**Line-by-line explanation:**

- `map_location=device`: Tells PyTorch where to load the tensors. If you trained on a GPU but are loading on a CPU, use `map_location='cpu'`. This prevents errors when the loading environment is different from the saving environment.

- `model.eval()`: Disables dropout and sets batch normalization to use running statistics instead of batch statistics. Always call this before inference.

- `with torch.no_grad()`: Disables gradient computation. During inference, we do not need gradients, so this saves memory and speeds things up.

- `torch.softmax(output, dim=1)`: Converts the model's raw output (logits) into probabilities that sum to 1. The digit with the highest probability is the prediction.

---

## 27.4 Exporting to ONNX

**ONNX** (Open Neural Network Exchange) is an open format that lets you use your trained model in environments outside PyTorch. You can run ONNX models in TensorFlow, mobile apps, web browsers, and many other platforms.

```python
def export_to_onnx(model, filepath, input_shape=(1, 1, 28, 28)):
    """Export a PyTorch model to ONNX format."""
    model.eval()

    # Create a dummy input with the expected shape
    dummy_input = torch.randn(input_shape)

    # Export to ONNX
    torch.onnx.export(
        model,                     # The model to export
        dummy_input,               # Example input
        filepath,                  # Output file path
        export_params=True,        # Include trained weights
        opset_version=11,          # ONNX version
        do_constant_folding=True,  # Optimize constants
        input_names=['input'],     # Name for the input
        output_names=['output'],   # Name for the output
        dynamic_axes={             # Allow variable batch size
            'input': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        }
    )
    print(f"Model exported to {filepath}")

    # Verify the file size
    file_size = os.path.getsize(filepath) / (1024 * 1024)
    print(f"ONNX model size: {file_size:.2f} MB")

# Export the model
model = SimpleClassifier()
export_to_onnx(model, 'model.onnx')
```

**Expected output:**
```
Model exported to model.onnx
ONNX model size: 0.78 MB
```

**Line-by-line explanation:**

- `dummy_input = torch.randn(input_shape)`: ONNX needs to trace through the model with a real input to understand the computation graph. The values do not matter, only the shape.

- `opset_version=11`: The ONNX operator set version. Higher versions support more operations. Version 11 is widely compatible.

- `do_constant_folding=True`: An optimization that pre-computes operations on constant values, making the model smaller and faster.

- `dynamic_axes={'input': {0: 'batch_size'}, ...}`: Allows the batch size to vary at runtime. Without this, the model would be fixed to the batch size of the dummy input.

### Running an ONNX Model

To run the ONNX model, you use the `onnxruntime` library:

```python
# pip install onnxruntime

import onnxruntime as ort
import numpy as np

def run_onnx_inference(onnx_path, input_data):
    """Run inference using an ONNX model."""
    # Create an inference session
    session = ort.InferenceSession(onnx_path)

    # Get input name
    input_name = session.get_inputs()[0].name

    # Convert input to numpy (ONNX runtime expects numpy arrays)
    if isinstance(input_data, torch.Tensor):
        input_data = input_data.numpy()

    # Run inference
    result = session.run(None, {input_name: input_data})

    return result[0]

# Example
dummy_input = np.random.randn(1, 1, 28, 28).astype(np.float32)
output = run_onnx_inference('model.onnx', dummy_input)
predicted = np.argmax(output, axis=1)
print(f"ONNX prediction: {predicted[0]}")
```

**Expected output:**
```
ONNX prediction: 7
```

```
ASCII Diagram: ONNX Cross-Platform Deployment

    PyTorch Model
         |
    Export to ONNX
         |
    model.onnx (universal format)
         |
    +----+----+----+----+
    |    |    |    |    |
  Python  C++  Java  JS  Mobile
  (ort)  (ort) (ort) (ort) (ort)

    ONNX runs on virtually any platform!
```

---

## 27.5 TorchScript for Production

**TorchScript** is PyTorch's way of converting models into a serialized, optimized format that can run without Python. This is ideal for production deployment.

There are two ways to create TorchScript models:

### Method 1: Tracing

Tracing records the operations as you run a sample input through the model:

```python
model = SimpleClassifier()
model.eval()

# Create a sample input
example_input = torch.randn(1, 1, 28, 28)

# Trace the model
traced_model = torch.jit.trace(model, example_input)

# Save the traced model
traced_model.save('model_traced.pt')
print("Traced model saved!")

# Load and use the traced model (does not need the model class!)
loaded_traced = torch.jit.load('model_traced.pt')
output = loaded_traced(example_input)
print(f"Output shape: {output.shape}")
```

**Expected output:**
```
Traced model saved!
Output shape: torch.Size([1, 10])
```

### Method 2: Scripting

Scripting analyzes the Python code directly and converts it to TorchScript:

```python
# Script the model
scripted_model = torch.jit.script(model)

# Save the scripted model
scripted_model.save('model_scripted.pt')
print("Scripted model saved!")

# Load and use
loaded_scripted = torch.jit.load('model_scripted.pt')
output = loaded_scripted(example_input)
print(f"Output shape: {output.shape}")
```

**Expected output:**
```
Scripted model saved!
Output shape: torch.Size([1, 10])
```

### Tracing vs Scripting

```
ASCII Diagram: Tracing vs Scripting

    Tracing:
    - Records operations from a sample run
    - Works well for models without control flow (if/else, loops)
    - Ignores any control flow (only records what happened)
    - Simpler to use
    - Use for: straightforward models

    Scripting:
    - Analyzes Python code directly
    - Handles control flow (if/else, loops)
    - More complex but more powerful
    - Use for: models with conditional logic

    When in doubt, try tracing first. Use scripting if
    your model has if-statements or variable-length loops.
```

### Key Advantage of TorchScript

The biggest advantage is that TorchScript models do not need the original Python class definition to load. You can deploy them in C++ applications, mobile apps, or any environment where Python is not available.

---

## 27.6 Model Size Considerations

Model size matters for deployment. Large models use more memory, load slower, and cost more to serve. Here are ways to check and reduce model size.

### Checking Model Size

```python
import os

def get_model_size(model, filepath='temp_model.pth'):
    """Calculate the size of a model in megabytes."""
    torch.save(model.state_dict(), filepath)
    size_mb = os.path.getsize(filepath) / (1024 * 1024)
    os.remove(filepath)
    return size_mb

def count_parameters(model):
    """Count total and trainable parameters."""
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters()
                    if p.requires_grad)
    return total, trainable

model = SimpleClassifier()
size = get_model_size(model)
total, trainable = count_parameters(model)

print(f"Model size: {size:.2f} MB")
print(f"Total parameters: {total:,}")
print(f"Trainable parameters: {trainable:,}")
```

**Expected output:**
```
Model size: 0.78 MB
Total parameters: 203,530
Trainable parameters: 203,530
```

### Reducing Model Size

#### 1. Half-Precision (FP16)

Convert model weights from 32-bit floats to 16-bit floats, cutting size in half:

```python
# Convert to half precision
model_fp16 = model.half()

# Save in half precision
torch.save(model_fp16.state_dict(), 'model_fp16.pth')
size_fp16 = os.path.getsize('model_fp16.pth') / (1024 * 1024)
print(f"FP32 size: {size:.2f} MB")
print(f"FP16 size: {size_fp16:.2f} MB")
print(f"Reduction: {(1 - size_fp16/size)*100:.1f}%")
```

**Expected output:**
```
FP32 size: 0.78 MB
FP16 size: 0.39 MB
Reduction: 50.0%
```

#### 2. Quantization

Quantization converts weights to 8-bit integers, reducing size by 4x:

```python
# Dynamic quantization (simplest form)
model_quantized = torch.quantization.quantize_dynamic(
    model,
    {nn.Linear},  # Quantize Linear layers
    dtype=torch.qint8
)

torch.save(model_quantized.state_dict(), 'model_quantized.pth')
size_quant = os.path.getsize('model_quantized.pth') / (1024 * 1024)
print(f"Original size:   {size:.2f} MB")
print(f"Quantized size:  {size_quant:.2f} MB")
```

**Expected output:**
```
Original size:   0.78 MB
Quantized size:  0.21 MB
```

```
ASCII Diagram: Model Size Reduction

    Original (FP32):  |████████████████████████|  0.78 MB
    Half (FP16):      |████████████|              0.39 MB
    Quantized (INT8): |██████|                    0.21 MB

    FP32: 32 bits per weight (most precise)
    FP16: 16 bits per weight (half size, tiny accuracy loss)
    INT8:  8 bits per weight (quarter size, small accuracy loss)
```

---

## 27.7 Serving Models with Flask

Flask is a lightweight Python web framework. You can use it to create a simple API that serves your model.

```python
# save this as app_flask.py

from flask import Flask, request, jsonify
import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
import io
import base64

# Define the model class (must match training)
class SimpleClassifier(nn.Module):
    def __init__(self, input_size=784, hidden_size=256, num_classes=10):
        super(SimpleClassifier, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        x = x.view(x.size(0), -1)
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Load the model once at startup
model = SimpleClassifier()
model.load_state_dict(torch.load('model_weights.pth', map_location='cpu'))
model.eval()

# Define preprocessing
transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.Resize((28, 28)),
    transforms.ToTensor(),
    transforms.Normalize([0.5], [0.5])
])

# Create Flask app
app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint that accepts an image and returns a prediction."""
    try:
        # Get image from request
        if 'image' in request.files:
            image = Image.open(request.files['image'])
        elif 'image_base64' in request.json:
            image_data = base64.b64decode(request.json['image_base64'])
            image = Image.open(io.BytesIO(image_data))
        else:
            return jsonify({'error': 'No image provided'}), 400

        # Preprocess
        input_tensor = transform(image).unsqueeze(0)

        # Predict
        with torch.no_grad():
            output = model(input_tensor)
            probabilities = torch.softmax(output, dim=1)
            predicted_class = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][predicted_class].item()

        return jsonify({
            'predicted_digit': predicted_class,
            'confidence': round(confidence, 4),
            'all_probabilities': probabilities[0].tolist()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'model': 'SimpleClassifier'})

if __name__ == '__main__':
    print("Starting model server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)
```

**To run this server:**
```bash
pip install flask pillow
python app_flask.py
```

**To test it:**
```bash
# Health check
curl http://localhost:5000/health

# Send an image for prediction
curl -X POST -F "image=@test_digit.png" http://localhost:5000/predict
```

**Expected response:**
```json
{
  "predicted_digit": 7,
  "confidence": 0.9834,
  "all_probabilities": [0.001, 0.002, 0.003, 0.001, 0.002, 0.001, 0.002, 0.983, 0.003, 0.002]
}
```

---

## 27.8 Serving Models with FastAPI

FastAPI is a modern, fast web framework for building APIs. It is generally preferred over Flask for new projects because it is faster, has built-in validation, and generates automatic documentation.

```python
# save this as app_fastapi.py

from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
import io
from typing import List

# Define the model class
class SimpleClassifier(nn.Module):
    def __init__(self, input_size=784, hidden_size=256, num_classes=10):
        super(SimpleClassifier, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        x = x.view(x.size(0), -1)
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Load model at startup
model = SimpleClassifier()
model.load_state_dict(torch.load('model_weights.pth', map_location='cpu'))
model.eval()

# Preprocessing
transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.Resize((28, 28)),
    transforms.ToTensor(),
    transforms.Normalize([0.5], [0.5])
])

# Response model
class PredictionResponse(BaseModel):
    predicted_digit: int
    confidence: float
    all_probabilities: List[float]

# Create FastAPI app
app = FastAPI(title="Digit Classifier API",
              description="Classifies handwritten digits 0-9")

@app.get("/health")
def health_check():
    """Check if the server is running."""
    return {"status": "healthy", "model": "SimpleClassifier"}

@app.post("/predict", response_model=PredictionResponse)
async def predict(image: UploadFile = File(...)):
    """
    Upload an image of a handwritten digit.
    Returns the predicted digit and confidence.
    """
    # Read the uploaded image
    contents = await image.read()

    try:
        img = Image.open(io.BytesIO(contents))
    except Exception:
        raise HTTPException(status_code=400,
                          detail="Invalid image file")

    # Preprocess and predict
    input_tensor = transform(img).unsqueeze(0)

    with torch.no_grad():
        output = model(input_tensor)
        probabilities = torch.softmax(output, dim=1)
        predicted_class = torch.argmax(probabilities, dim=1).item()
        confidence = probabilities[0][predicted_class].item()

    return PredictionResponse(
        predicted_digit=predicted_class,
        confidence=round(confidence, 4),
        all_probabilities=[round(p, 4) for p in
                          probabilities[0].tolist()]
    )
```

**To run this server:**
```bash
pip install fastapi uvicorn python-multipart pillow
uvicorn app_fastapi:app --host 0.0.0.0 --port 8000
```

FastAPI automatically generates interactive documentation at `http://localhost:8000/docs`.

```
ASCII Diagram: Deployment Architecture

    Client (Browser / App / Script)
         |
    HTTP Request (POST /predict with image)
         |
    +-------------------+
    | Web Server         |
    | (Flask or FastAPI) |
    +-------------------+
         |
    Preprocess Image
         |
    +-------------------+
    | PyTorch Model      |
    | (loaded in memory) |
    +-------------------+
         |
    JSON Response
         |
    Client receives prediction
```

---

## 27.9 Cross-Device Loading

When loading a model that was saved on a different device (e.g., saved on GPU, loading on CPU), use `map_location`:

```python
# Saved on GPU, loading on CPU
model.load_state_dict(
    torch.load('model.pth', map_location=torch.device('cpu'))
)

# Saved on CPU, loading on GPU
model.load_state_dict(
    torch.load('model.pth', map_location=torch.device('cuda'))
)

# Saved on GPU 1, loading on GPU 0
model.load_state_dict(
    torch.load('model.pth', map_location={'cuda:1': 'cuda:0'})
)

# Let PyTorch figure it out (load to CPU first, then move)
model.load_state_dict(torch.load('model.pth', map_location='cpu'))
model = model.to(device)  # Then move to desired device
```

**Key point**: Always use `map_location` when there is any chance the model was saved on a different device. The safest approach is to always load to CPU first, then move to the target device.

---

## Common Mistakes

1. **Forgetting `model.eval()` before inference**: Without this, batch normalization and dropout behave as if you are still training, giving incorrect results.

2. **Not using `torch.no_grad()` during inference**: Without this, PyTorch tracks gradients unnecessarily, wasting memory and slowing things down.

3. **Saving the entire model for production**: Use `state_dict` instead. Entire model saves are fragile and break when code changes.

4. **Not handling `map_location` for cross-device loading**: If you train on a GPU and deploy on a CPU, loading will fail without `map_location='cpu'`.

5. **Forgetting to include the model class when loading `state_dict`**: The class definition must be available when you load weights. Share the model code along with the weight file.

6. **Not saving the optimizer state in checkpoints**: Without the optimizer state, training resumes with fresh momentum values, which can cause a temporary performance drop.

---

## Best Practices

1. **Always save `state_dict`, not the full model**: More portable and less prone to breaking.

2. **Include metadata in checkpoints**: Save the epoch, loss, accuracy, hyperparameters, and any other information needed to understand and resume the training run.

3. **Use versioned filenames**: Name files like `model_v1.2_epoch50.pth` so you can track which version is which.

4. **Test loading immediately after saving**: Verify that your saved model loads correctly and produces the same outputs.

5. **Use ONNX or TorchScript for deployment**: These formats are optimized for inference and do not depend on the training code.

6. **Add a health check endpoint**: When serving models, include an endpoint that confirms the server is running and the model is loaded.

7. **Consider quantization for edge deployment**: If deploying to mobile or embedded devices, quantization can reduce model size by 4x with minimal accuracy loss.

---

## Quick Summary

PyTorch models can be saved in two ways: saving the `state_dict` (recommended) or saving the entire model. Checkpoints should include model weights, optimizer state, epoch number, and loss value to enable training resumption. For cross-platform deployment, ONNX provides a universal format that runs on any platform with ONNX Runtime. TorchScript compiles models for production use without requiring Python. Model size can be reduced through half-precision (FP16) or quantization (INT8). For serving models, Flask and FastAPI are popular choices for creating prediction APIs. Always use `model.eval()` and `torch.no_grad()` during inference, and handle `map_location` when loading across different devices.

---

## Key Points

- `torch.save(model.state_dict(), path)` saves only the weights (recommended)
- `model.load_state_dict(torch.load(path))` loads weights into an existing model
- Checkpoints should include model weights, optimizer state, epoch, and loss
- ONNX enables running PyTorch models on any platform (mobile, web, C++)
- TorchScript (trace or script) creates optimized models that run without Python
- Always call `model.eval()` before inference and use `torch.no_grad()`
- Use `map_location` when loading models across different devices (GPU to CPU)
- FP16 halves model size; INT8 quantization reduces it by 4x
- Flask and FastAPI can serve models as HTTP APIs
- Always test saved models by loading and running inference immediately

---

## Practice Questions

1. What is the difference between saving `model.state_dict()` and saving the entire model with `torch.save(model, path)`? Why is the first approach recommended?

2. What information should a training checkpoint include? Why is saving the optimizer state important?

3. Explain what `map_location` does when loading a model. When do you need to use it?

4. What is ONNX and why would you use it instead of deploying a PyTorch model directly?

5. What is the difference between tracing and scripting in TorchScript? When would you use each?

---

## Exercises

### Exercise 1: Complete Checkpoint System
Implement a training loop for a classifier on MNIST with the following features: save a checkpoint every 5 epochs, save the best model based on validation accuracy, and implement a resume function that continues training from the latest checkpoint.

### Exercise 2: Model Compression Comparison
Train a model on MNIST, then compare the accuracy and inference speed of: (1) the original FP32 model, (2) the FP16 model, and (3) the dynamically quantized INT8 model. Create a table showing size, accuracy, and inference time for each.

### Exercise 3: Deploy with FastAPI
Create a FastAPI application that serves a trained MNIST classifier. Include endpoints for: (1) single image prediction, (2) batch prediction (multiple images), and (3) model information (architecture, number of parameters, training accuracy). Test all endpoints with curl or a Python script.

---

## What Is Next?

You now know how to save, load, and deploy your models. But what happens when your model does not work as expected? What if the loss is not decreasing, the model always predicts the same class, or you get NaN values?

In the next chapter, we will tackle **Debugging Deep Learning**. You will learn a systematic approach to diagnosing and fixing the most common deep learning problems. From gradient checking to learning rate finders to the "overfit one batch" sanity check, you will build a debugging toolkit that will save you countless hours of frustration.
