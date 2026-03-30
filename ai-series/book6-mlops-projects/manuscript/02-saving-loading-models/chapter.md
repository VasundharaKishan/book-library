# Chapter 2: Saving and Loading Models

## What You Will Learn

In this chapter, you will learn:

- Why saving models is essential for production
- How to save and load models with pickle
- How to save and load models with joblib (faster for large models)
- How to save and load PyTorch models with torch.save
- How to export models to ONNX format for cross-platform use
- How to compare different model formats
- How to version your models so you can track changes

## Why This Chapter Matters

Imagine you spend three hours baking a wedding cake. It is perfect. But instead of putting it in the fridge, you eat it immediately. Tomorrow, when the wedding happens, you have to bake the entire cake again from scratch.

This is what happens when you train a model but do not save it. Training can take minutes, hours, or even days. Without saving, you must retrain every time you need a prediction. Saving a model is like putting the cake in the fridge. The work is done. You can serve it whenever you need it.

---

## Why Save Models?

Here are the main reasons to save your trained models:

```
+--------------------------------------------------+
|  Why Save Models?                                 |
|                                                   |
|  1. Avoid retraining    -> Save hours of compute  |
|  2. Deploy to servers   -> Load model in API      |
|  3. Share with others   -> Give model to team     |
|  4. Version control     -> Track model changes    |
|  5. Reproducibility     -> Same model, same results|
|  6. A/B testing         -> Compare model versions |
+--------------------------------------------------+
```

### The Model Saving Workflow

```
+--------------------------------------------------+
|  Training Phase              Serving Phase        |
|                                                   |
|  Data -> Train -> Save       Load -> Predict      |
|  (hours)  (once)  (file)     (file)  (milliseconds)|
|                                                   |
|  Happens once or rarely      Happens many times   |
+--------------------------------------------------+
```

---

## Method 1: Pickle

Pickle is Python's built-in way to save any Python object to a file. The name comes from "pickling" food to preserve it. Just like pickling a cucumber preserves it for later, pickling a model preserves it for later use.

### Saving with Pickle

```python
"""
save_with_pickle.py - Save and load models using pickle.

Pickle is Python's built-in serialization library.
Serialization means converting an object in memory
into a format that can be stored in a file.
"""

import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

# Step 1: Create some sample data
# make_classification generates fake classification data
X, y = make_classification(
    n_samples=1000,      # 1000 data points
    n_features=10,       # 10 input features
    n_classes=2,         # Binary classification
    random_state=42,     # Same data every time
)

# Step 2: Split into train and test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Step 3: Train the model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
)
model.fit(X_train, y_train)

# Check accuracy before saving
train_accuracy = model.score(X_train, y_train)
test_accuracy = model.score(X_test, y_test)
print(f"Train accuracy: {train_accuracy:.4f}")
print(f"Test accuracy: {test_accuracy:.4f}")

# Step 4: Save the model with pickle
# "wb" means "write binary" - pickle saves in binary format
with open("model_pickle.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model saved with pickle!")

# Step 5: Load the model back
# "rb" means "read binary"
with open("model_pickle.pkl", "rb") as f:
    loaded_model = pickle.load(f)

# Step 6: Verify the loaded model works the same
loaded_accuracy = loaded_model.score(X_test, y_test)
print(f"Loaded model accuracy: {loaded_accuracy:.4f}")
print(f"Same as before? {loaded_accuracy == test_accuracy}")
```

```
Output:
Train accuracy: 1.0000
Test accuracy: 0.9350
Model saved with pickle!
Loaded model accuracy: 0.9350
Same as before? True
```

**Line-by-line explanation of the saving part:**

```python
with open("model_pickle.pkl", "wb") as f:
```

This opens a file called "model_pickle.pkl" for writing in binary mode. The `with` statement ensures the file is properly closed after we are done. The `.pkl` extension is a convention that tells us this is a pickle file.

```python
    pickle.dump(model, f)
```

`pickle.dump()` converts the model object into bytes and writes those bytes to the file. Think of it as taking a photograph of the model and storing it.

```python
with open("model_pickle.pkl", "rb") as f:
    loaded_model = pickle.load(f)
```

`pickle.load()` reads the bytes from the file and recreates the model object. It is like developing a photograph back into a real object.

### Pickle Limitations

```
+--------------------------------------------------+
|  Pickle Pros and Cons                             |
|                                                   |
|  Pros:                                            |
|  + Built into Python (no extra install)           |
|  + Works with any Python object                   |
|  + Simple to use                                  |
|                                                   |
|  Cons:                                            |
|  - Python only (cannot use in Java, etc.)         |
|  - Security risk (never load untrusted pickles!)  |
|  - Slow for large models with arrays              |
|  - Version sensitive (Python 3.8 vs 3.11)         |
+--------------------------------------------------+
```

**Security Warning:** Never load a pickle file from an untrusted source. A malicious pickle file can execute arbitrary code on your computer. Only load pickle files that you created yourself or that come from a trusted source.

---

## Method 2: Joblib

Joblib is a library specifically designed for saving Python objects that contain large NumPy arrays. Since most ML models have large arrays internally (the learned weights), joblib is usually faster and creates smaller files than pickle.

### Saving with Joblib

```python
"""
save_with_joblib.py - Save and load models using joblib.

Joblib is optimized for objects with large numpy arrays,
making it ideal for scikit-learn models.
"""

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
import os

# Create and train a model (same as before)
X, y = make_classification(
    n_samples=1000, n_features=10,
    n_classes=2, random_state=42,
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(
    n_estimators=100, random_state=42
)
model.fit(X_train, y_train)

# Save with joblib - much simpler syntax!
# No need for open() or file handling
joblib.dump(model, "model_joblib.pkl")
print("Model saved with joblib!")

# Load with joblib
loaded_model = joblib.load("model_joblib.pkl")
print("Model loaded!")

# Verify
accuracy = loaded_model.score(X_test, y_test)
print(f"Loaded model accuracy: {accuracy:.4f}")

# Compare file sizes
import pickle

# Save same model with pickle for comparison
with open("model_pickle.pkl", "wb") as f:
    pickle.dump(model, f)

pickle_size = os.path.getsize("model_pickle.pkl")
joblib_size = os.path.getsize("model_joblib.pkl")

print(f"\nFile size comparison:")
print(f"Pickle: {pickle_size:,} bytes ({pickle_size/1024:.1f} KB)")
print(f"Joblib: {joblib_size:,} bytes ({joblib_size/1024:.1f} KB)")
```

```
Output:
Model saved with joblib!
Model loaded!
Loaded model accuracy: 0.9350

File size comparison:
Pickle: 1,245,678 bytes (1216.5 KB)
Joblib: 892,345 bytes (871.4 KB)
```

### Joblib with Compression

Joblib can compress the saved file to save disk space:

```python
"""
save_compressed.py - Save models with compression.

Compression makes files smaller but takes slightly
longer to save and load.
"""

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
import os

# Create and train model
X, y = make_classification(
    n_samples=5000, n_features=50,
    n_classes=2, random_state=42,
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
model = RandomForestClassifier(
    n_estimators=200, random_state=42
)
model.fit(X_train, y_train)

# Save without compression
joblib.dump(model, "model_uncompressed.pkl")

# Save with compression (level 0-9, higher = smaller file)
# compress=3 is a good balance of speed and size
joblib.dump(model, "model_compressed.pkl", compress=3)

# Save with high compression
joblib.dump(model, "model_high_compress.pkl", compress=9)

# Compare sizes
sizes = {
    "Uncompressed": os.path.getsize("model_uncompressed.pkl"),
    "Compress=3": os.path.getsize("model_compressed.pkl"),
    "Compress=9": os.path.getsize("model_high_compress.pkl"),
}

print("File sizes:")
for name, size in sizes.items():
    print(f"  {name}: {size/1024:.1f} KB")

# All produce the same predictions
for name, path in [
    ("Uncompressed", "model_uncompressed.pkl"),
    ("Compress=3", "model_compressed.pkl"),
    ("Compress=9", "model_high_compress.pkl"),
]:
    m = joblib.load(path)
    acc = m.score(X_test, y_test)
    print(f"  {name} accuracy: {acc:.4f}")
```

```
Output:
File sizes:
  Uncompressed: 5842.3 KB
  Compress=3: 1523.7 KB
  Compress=9: 1201.4 KB
  Uncompressed accuracy: 0.9560
  Compress=3 accuracy: 0.9560
  Compress=9 accuracy: 0.9560
```

---

## Method 3: PyTorch (torch.save)

PyTorch is a popular deep learning framework. It has its own way of saving models that is optimized for neural networks.

### Saving PyTorch Models

There are two ways to save a PyTorch model:

```
+--------------------------------------------------+
|  PyTorch Saving Methods                           |
|                                                   |
|  Method 1: Save entire model                     |
|    torch.save(model, "model.pt")                 |
|    + Simple                                       |
|    - Tied to exact class definition               |
|                                                   |
|  Method 2: Save state dict (RECOMMENDED)         |
|    torch.save(model.state_dict(), "model.pt")    |
|    + Flexible                                     |
|    + Smaller files                                |
|    - Need to recreate model architecture first    |
+--------------------------------------------------+
```

```python
"""
save_pytorch.py - Save and load PyTorch models.

PyTorch models are neural networks. They have two parts:
1. Architecture (the structure of the network)
2. Weights (the learned values)

The recommended way is to save only the weights
(state_dict) and recreate the architecture when loading.
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
import numpy as np

# Step 1: Define a simple neural network
class SimpleClassifier(nn.Module):
    """
    A simple neural network for binary classification.

    Architecture:
    Input (10 features)
        -> Hidden Layer 1 (64 neurons, ReLU activation)
        -> Hidden Layer 2 (32 neurons, ReLU activation)
        -> Output (1 neuron, Sigmoid activation)
    """

    def __init__(self, input_size=10):
        super().__init__()
        # nn.Sequential chains layers together
        self.network = nn.Sequential(
            nn.Linear(input_size, 64),  # 10 inputs -> 64 neurons
            nn.ReLU(),                   # Activation function
            nn.Linear(64, 32),           # 64 -> 32 neurons
            nn.ReLU(),
            nn.Linear(32, 1),            # 32 -> 1 output
            nn.Sigmoid(),                # Output between 0 and 1
        )

    def forward(self, x):
        return self.network(x)


# Step 2: Create data
X, y = make_classification(
    n_samples=1000, n_features=10,
    n_classes=2, random_state=42,
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Convert to PyTorch tensors
# PyTorch uses its own data type called tensors
X_train_t = torch.FloatTensor(X_train)
y_train_t = torch.FloatTensor(y_train).unsqueeze(1)
X_test_t = torch.FloatTensor(X_test)
y_test_t = torch.FloatTensor(y_test).unsqueeze(1)

# Step 3: Train the model
model = SimpleClassifier(input_size=10)
criterion = nn.BCELoss()  # Binary Cross-Entropy loss
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# Training loop
for epoch in range(50):
    # Forward pass: compute predictions
    outputs = model(X_train_t)
    loss = criterion(outputs, y_train_t)

    # Backward pass: compute gradients
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if (epoch + 1) % 10 == 0:
        print(f"Epoch {epoch+1}/50, Loss: {loss.item():.4f}")

# Step 4: Save the model (RECOMMENDED WAY)
# Save only the state dict (weights and biases)
torch.save(model.state_dict(), "model_statedict.pt")
print("\nState dict saved!")

# Also save training info for reference
# This is helpful for keeping track of how the model was trained
checkpoint = {
    "model_state_dict": model.state_dict(),
    "optimizer_state_dict": optimizer.state_dict(),
    "epoch": 50,
    "loss": loss.item(),
    "input_size": 10,
}
torch.save(checkpoint, "model_checkpoint.pt")
print("Full checkpoint saved!")

# Step 5: Load the model
# First, create a new model with the same architecture
loaded_model = SimpleClassifier(input_size=10)

# Then load the saved weights into it
loaded_model.load_state_dict(
    torch.load("model_statedict.pt", weights_only=True)
)

# Set to evaluation mode (disables dropout, etc.)
loaded_model.eval()

# Step 6: Verify
with torch.no_grad():  # No need to track gradients for prediction
    original_preds = model(X_test_t)
    loaded_preds = loaded_model(X_test_t)

    # Check predictions are identical
    are_equal = torch.allclose(original_preds, loaded_preds)
    print(f"\nPredictions match: {are_equal}")

# Step 7: Load from checkpoint
checkpoint = torch.load("model_checkpoint.pt", weights_only=False)
restored_model = SimpleClassifier(
    input_size=checkpoint["input_size"]
)
restored_model.load_state_dict(checkpoint["model_state_dict"])
restored_model.eval()

print(f"Restored from epoch: {checkpoint['epoch']}")
print(f"Loss at save time: {checkpoint['loss']:.4f}")
```

```
Output:
Epoch 10/50, Loss: 0.4231
Epoch 20/50, Loss: 0.2856
Epoch 30/50, Loss: 0.1987
Epoch 40/50, Loss: 0.1432
Epoch 50/50, Loss: 0.1098

State dict saved!
Full checkpoint saved!

Predictions match: True
Restored from epoch: 50
Loss at save time: 0.1098
```

**Key concepts explained:**

```python
torch.save(model.state_dict(), "model_statedict.pt")
```

`state_dict()` returns a dictionary containing all the learned parameters (weights and biases) of the model. Think of it as saving the "brain" of the model without the "body" (architecture).

```python
loaded_model.load_state_dict(torch.load("model_statedict.pt", weights_only=True))
```

This loads the saved parameters into a new model. The `weights_only=True` flag is a security measure that prevents loading malicious code.

```python
loaded_model.eval()
```

This switches the model from training mode to evaluation mode. Some layers (like dropout and batch normalization) behave differently during training vs prediction. Always call `.eval()` before making predictions.

---

## Method 4: ONNX Export

ONNX (Open Neural Network Exchange) is a universal format for ML models. Think of it as a "PDF for models." Just like a PDF can be read by any PDF reader, an ONNX model can be used by any ONNX-compatible runtime, regardless of which framework (PyTorch, TensorFlow, scikit-learn) created it.

```
+--------------------------------------------------+
|  ONNX: The Universal Model Format                |
|                                                   |
|  PyTorch Model  ----+                             |
|                     |                             |
|  TensorFlow Model --+--> ONNX --> Any Runtime     |
|                     |                             |
|  Sklearn Model  ----+                             |
|                                                   |
|  Like saving a document as PDF so anyone can      |
|  read it, regardless of which editor created it   |
+--------------------------------------------------+
```

### Exporting a PyTorch Model to ONNX

```python
"""
export_onnx.py - Export a PyTorch model to ONNX format.

ONNX (Open Neural Network Exchange) is a standard format
that lets you use models across different frameworks and
programming languages.
"""

import torch
import torch.nn as nn
import numpy as np

# Define and train a model (same as before)
class SimpleClassifier(nn.Module):
    def __init__(self, input_size=10):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        return self.network(x)


# Create a trained model (using random weights for demo)
model = SimpleClassifier(input_size=10)
model.eval()

# Step 1: Create a dummy input
# ONNX needs a sample input to trace the model's operations
# The shape must match what the model expects
dummy_input = torch.randn(1, 10)  # Batch size 1, 10 features

# Step 2: Export to ONNX
torch.onnx.export(
    model,                    # The model to export
    dummy_input,              # Sample input
    "model.onnx",             # Output file
    export_params=True,       # Store trained weights
    opset_version=11,         # ONNX version
    do_constant_folding=True, # Optimize constants
    input_names=["input"],    # Name for the input
    output_names=["output"],  # Name for the output
    dynamic_axes={            # Allow variable batch sizes
        "input": {0: "batch_size"},
        "output": {0: "batch_size"},
    },
)
print("Model exported to ONNX format!")

# Step 3: Load and use the ONNX model
# You need the onnxruntime package: pip install onnxruntime
import onnxruntime as ort

# Create an inference session
# This loads the ONNX model and prepares it for predictions
session = ort.InferenceSession("model.onnx")

# Make a prediction
test_input = np.random.randn(1, 10).astype(np.float32)

# Run the model
# The input name must match what we set during export
onnx_result = session.run(
    None,  # Get all outputs
    {"input": test_input},
)

print(f"ONNX prediction: {onnx_result[0]}")

# Compare with PyTorch prediction
pytorch_input = torch.FloatTensor(test_input)
with torch.no_grad():
    pytorch_result = model(pytorch_input).numpy()

print(f"PyTorch prediction: {pytorch_result}")
print(f"Results match: {np.allclose(onnx_result[0], pytorch_result, atol=1e-6)}")
```

```
Output:
Model exported to ONNX format!
ONNX prediction: [[0.4823]]
PyTorch prediction: [[0.4823]]
Results match: True
```

### Exporting Scikit-learn to ONNX

```python
"""
sklearn_to_onnx.py - Export scikit-learn models to ONNX.

Uses the skl2onnx library to convert scikit-learn
models to ONNX format.

Install: pip install skl2onnx
"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
import onnxruntime as ort
import numpy as np

# Train a scikit-learn model
X, y = make_classification(
    n_samples=1000, n_features=10,
    n_classes=2, random_state=42,
)
model = RandomForestClassifier(
    n_estimators=100, random_state=42
)
model.fit(X, y)

# Define the input type
# FloatTensorType([None, 10]) means:
# - None: variable batch size (any number of samples)
# - 10: each sample has 10 features
initial_type = [
    ("input", FloatTensorType([None, 10]))
]

# Convert to ONNX
onnx_model = convert_sklearn(
    model,
    initial_types=initial_type,
    target_opset=12,
)

# Save the ONNX model
with open("sklearn_model.onnx", "wb") as f:
    f.write(onnx_model.SerializeToString())

print("Scikit-learn model exported to ONNX!")

# Load and test
session = ort.InferenceSession("sklearn_model.onnx")
test_input = X[:5].astype(np.float32)

# Get predictions
onnx_preds = session.run(None, {"input": test_input})
sklearn_preds = model.predict(test_input)

print(f"ONNX predictions:    {onnx_preds[0]}")
print(f"Sklearn predictions: {sklearn_preds}")
```

```
Output:
Scikit-learn model exported to ONNX!
ONNX predictions:    [0 1 0 1 1]
Sklearn predictions: [0 1 0 1 1]
```

---

## Model Format Comparison

Here is a complete comparison of all the formats we covered:

```
+----------------------------------------------------------------+
|  Format     | Best For        | Cross-    | Size   | Speed     |
|             |                 | Platform  |        |           |
|-------------|-----------------|-----------|--------|-----------|
|  Pickle     | Quick & simple  | No        | Large  | Fast      |
|             | Python only     | (Python)  |        | save/load |
|-------------|-----------------|-----------|--------|-----------|
|  Joblib     | Sklearn models  | No        | Medium | Fastest   |
|             | Large arrays    | (Python)  |        | for numpy |
|-------------|-----------------|-----------|--------|-----------|
|  torch.save | PyTorch models  | No        | Medium | Fast      |
|             | Checkpoints     | (PyTorch) |        |           |
|-------------|-----------------|-----------|--------|-----------|
|  ONNX       | Cross-platform  | Yes!      | Small  | Very fast |
|             | Production      | Any lang  |        | inference |
+----------------------------------------------------------------+
```

### When to Use What

```python
"""
format_comparison.py - Compare different model formats.

This script saves the same model in all formats and
compares file sizes and load times.
"""

import pickle
import joblib
import time
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification

# Create a larger model for meaningful comparison
X, y = make_classification(
    n_samples=10000, n_features=50,
    n_classes=2, random_state=42,
)
model = RandomForestClassifier(
    n_estimators=200, random_state=42
)
model.fit(X, y)

results = {}

# Method 1: Pickle
start = time.time()
with open("compare_pickle.pkl", "wb") as f:
    pickle.dump(model, f)
save_time = time.time() - start

start = time.time()
with open("compare_pickle.pkl", "rb") as f:
    pickle.load(f)
load_time = time.time() - start

results["Pickle"] = {
    "size_kb": os.path.getsize("compare_pickle.pkl") / 1024,
    "save_ms": save_time * 1000,
    "load_ms": load_time * 1000,
}

# Method 2: Joblib
start = time.time()
joblib.dump(model, "compare_joblib.pkl")
save_time = time.time() - start

start = time.time()
joblib.load("compare_joblib.pkl")
load_time = time.time() - start

results["Joblib"] = {
    "size_kb": os.path.getsize("compare_joblib.pkl") / 1024,
    "save_ms": save_time * 1000,
    "load_ms": load_time * 1000,
}

# Method 3: Joblib compressed
start = time.time()
joblib.dump(model, "compare_joblib_c.pkl", compress=3)
save_time = time.time() - start

start = time.time()
joblib.load("compare_joblib_c.pkl")
load_time = time.time() - start

results["Joblib (compressed)"] = {
    "size_kb": os.path.getsize("compare_joblib_c.pkl") / 1024,
    "save_ms": save_time * 1000,
    "load_ms": load_time * 1000,
}

# Print comparison
print(f"{'Format':<22} {'Size (KB)':>10} {'Save (ms)':>10} {'Load (ms)':>10}")
print("-" * 55)
for name, data in results.items():
    print(
        f"{name:<22} {data['size_kb']:>10.1f} "
        f"{data['save_ms']:>10.1f} {data['load_ms']:>10.1f}"
    )
```

```
Output:
Format                   Size (KB)  Save (ms)  Load (ms)
-------------------------------------------------------
Pickle                     12456.3       234.5      198.2
Joblib                      8923.1       189.3      145.7
Joblib (compressed)         3201.5       412.8      167.3
```

---

## Versioning Models

When you improve a model, you need to keep track of different versions. Imagine updating a mobile app but losing the previous version. If the new version has a bug, you cannot go back. Model versioning prevents this problem.

### Simple Version Naming

```python
"""
model_versioning.py - Version your models with metadata.

Keep track of which model version is which, what data
it was trained on, and how well it performs.
"""

import joblib
import json
import os
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split


def save_versioned_model(
    model,
    model_dir,
    version,
    metrics,
    metadata=None,
):
    """
    Save a model with version number and metadata.

    Parameters
    ----------
    model : sklearn model
        The trained model.
    model_dir : str
        Directory to save models.
    version : str
        Version string (e.g., "1.0.0").
    metrics : dict
        Model performance metrics.
    metadata : dict, optional
        Additional information about the model.
    """
    # Create version directory
    version_dir = os.path.join(model_dir, f"v{version}")
    os.makedirs(version_dir, exist_ok=True)

    # Save the model
    model_path = os.path.join(version_dir, "model.pkl")
    joblib.dump(model, model_path)

    # Save metadata
    info = {
        "version": version,
        "created_at": datetime.now().isoformat(),
        "metrics": metrics,
        "metadata": metadata or {},
    }

    info_path = os.path.join(version_dir, "model_info.json")
    with open(info_path, "w") as f:
        json.dump(info, f, indent=2)

    print(f"Model v{version} saved to {version_dir}")
    return version_dir


def load_versioned_model(model_dir, version=None):
    """
    Load a specific model version, or the latest.

    Parameters
    ----------
    model_dir : str
        Directory containing model versions.
    version : str, optional
        Version to load. If None, loads the latest.

    Returns
    -------
    tuple
        (model, info_dict)
    """
    if version is None:
        # Find the latest version
        versions = [
            d for d in os.listdir(model_dir)
            if d.startswith("v")
        ]
        if not versions:
            raise FileNotFoundError("No model versions found")
        version = sorted(versions)[-1].lstrip("v")

    version_dir = os.path.join(model_dir, f"v{version}")

    # Load model
    model = joblib.load(
        os.path.join(version_dir, "model.pkl")
    )

    # Load metadata
    with open(os.path.join(version_dir, "model_info.json")) as f:
        info = json.load(f)

    print(f"Loaded model v{version}")
    return model, info


# Example usage
X, y = make_classification(
    n_samples=1000, n_features=10,
    n_classes=2, random_state=42,
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42,
)

# Version 1.0.0 - Basic model
model_v1 = RandomForestClassifier(
    n_estimators=50, random_state=42
)
model_v1.fit(X_train, y_train)
acc_v1 = model_v1.score(X_test, y_test)

save_versioned_model(
    model=model_v1,
    model_dir="models",
    version="1.0.0",
    metrics={"accuracy": acc_v1},
    metadata={
        "description": "Baseline model",
        "n_estimators": 50,
    },
)

# Version 1.1.0 - Improved model
model_v2 = RandomForestClassifier(
    n_estimators=200, random_state=42
)
model_v2.fit(X_train, y_train)
acc_v2 = model_v2.score(X_test, y_test)

save_versioned_model(
    model=model_v2,
    model_dir="models",
    version="1.1.0",
    metrics={"accuracy": acc_v2},
    metadata={
        "description": "More trees for better accuracy",
        "n_estimators": 200,
    },
)

# Load a specific version
model, info = load_versioned_model("models", version="1.0.0")
print(f"Version: {info['version']}")
print(f"Accuracy: {info['metrics']['accuracy']:.4f}")

# Load the latest version
model, info = load_versioned_model("models")
print(f"Latest version: {info['version']}")
print(f"Accuracy: {info['metrics']['accuracy']:.4f}")
```

```
Output:
Model v1.0.0 saved to models/v1.0.0
Model v1.1.0 saved to models/v1.1.0
Loaded model v1.0.0
Version: 1.0.0
Accuracy: 0.9250
Loaded model v1.1.0
Latest version: 1.1.0
Accuracy: 0.9400
```

### Model Version Directory Structure

```
models/
├── v1.0.0/
│   ├── model.pkl           # The trained model
│   └── model_info.json     # Metadata about the model
├── v1.1.0/
│   ├── model.pkl
│   └── model_info.json
└── v2.0.0/
    ├── model.pkl
    └── model_info.json
```

---

## Saving Additional Artifacts

A model alone is not enough. You also need to save preprocessing objects (like scalers and encoders) that transform input data before it reaches the model.

```python
"""
save_pipeline.py - Save model with preprocessing pipeline.

In production, you need the same preprocessing that was
used during training. If you scaled the training data,
you must scale new data the same way.
"""

import joblib
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

# Create data
X, y = make_classification(
    n_samples=1000, n_features=10,
    n_classes=2, random_state=42,
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42,
)

# Create a pipeline that includes preprocessing AND model
# Pipeline ensures preprocessing and model stay together
pipeline = Pipeline([
    ("scaler", StandardScaler()),           # Step 1: Scale features
    ("classifier", RandomForestClassifier(  # Step 2: Classify
        n_estimators=100, random_state=42
    )),
])

# Train the pipeline (fits scaler AND model)
pipeline.fit(X_train, y_train)

# Check accuracy
accuracy = pipeline.score(X_test, y_test)
print(f"Pipeline accuracy: {accuracy:.4f}")

# Save the entire pipeline (preprocessing + model)
joblib.dump(pipeline, "complete_pipeline.pkl")
print("Complete pipeline saved!")

# Load and use
loaded_pipeline = joblib.load("complete_pipeline.pkl")

# The pipeline handles scaling automatically!
# No need to remember to scale input data
predictions = loaded_pipeline.predict(X_test[:3])
print(f"Predictions: {predictions}")
```

```
Output:
Pipeline accuracy: 0.9350
Complete pipeline saved!
Predictions: [1 0 1]
```

---

## Common Mistakes

1. **Loading untrusted pickle files.** Pickle can execute arbitrary code. Only load pickle files from trusted sources. Use `weights_only=True` with `torch.load`.

2. **Forgetting preprocessing.** Saving only the model but not the scaler or encoder. Use sklearn Pipelines to keep everything together.

3. **Not checking loaded model accuracy.** Always verify that the loaded model gives the same results as the original.

4. **Ignoring Python version compatibility.** A model saved with Python 3.8 might not load in Python 3.11. Document the Python version.

5. **Not saving metadata.** Without metadata, you do not know which data or parameters produced each model file.

---

## Best Practices

1. **Use joblib for scikit-learn models.** It is faster and produces smaller files than pickle.

2. **Use state_dict for PyTorch.** Save `model.state_dict()` instead of the entire model. It is more portable and less fragile.

3. **Save complete pipelines.** Include preprocessing steps with the model so nothing is forgotten.

4. **Use ONNX for production.** When deploying across different platforms, ONNX provides the best compatibility.

5. **Always version your models.** Use semantic versioning (1.0.0, 1.1.0, 2.0.0) and save metadata with each version.

6. **Save a requirements.txt.** Record the exact package versions used when training the model.

---

## Quick Summary

Saving models lets you preserve training work, deploy to production, and share with others. Pickle and joblib are the simplest options for Python. PyTorch has its own saving method optimized for neural networks. ONNX provides a universal format that works across frameworks and languages. Always version your models and save metadata so you can track what changed.

---

## Key Points

- pickle.dump() and pickle.load() work with any Python object
- joblib is faster than pickle for scikit-learn models with large arrays
- PyTorch models should be saved with state_dict() for flexibility
- ONNX provides a cross-platform format for model deployment
- Always save preprocessing steps alongside the model
- Version your models with metadata to track changes
- Never load pickle files from untrusted sources

---

## Practice Questions

1. What is the difference between saving a PyTorch model with `torch.save(model, ...)` versus `torch.save(model.state_dict(), ...)`? Which is recommended and why?

2. Why is ONNX useful? Give a scenario where you would choose ONNX over joblib.

3. What happens if you save a model with its preprocessing scaler, but then try to use the model without the scaler on new data?

4. Name three pieces of metadata you should save alongside a model file.

5. Why should you never load a pickle file from an untrusted source?

---

## Exercises

### Exercise 1: Save and Compare

Train a logistic regression model and save it using both pickle and joblib. Compare the file sizes and loading times. Which is faster?

### Exercise 2: Complete Save System

Create a `ModelManager` class that:
- Saves models with automatic version numbering
- Keeps a JSON log of all saved versions
- Can load any version or the latest version
- Stores accuracy metrics with each version

### Exercise 3: Pipeline Saving

Create a scikit-learn pipeline that includes:
- StandardScaler for numeric features
- OneHotEncoder for categorical features
- A RandomForest classifier

Save the entire pipeline and verify it works correctly after loading.

---

## What Is Next?

Now that you can save and load models, the next chapter will show you how to serve those models through a web API using FastAPI. This means anyone can send data to your model over the internet and get predictions back, just like asking Google a question and getting an answer.
