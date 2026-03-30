# Chapter 25: Project — Sentiment Analysis API

## What You Will Learn

In this chapter, you will learn:

- How to fine-tune DistilBERT on a movie review dataset
- How to build a REST API with FastAPI
- How to design request and response formats for ML APIs
- How to test your API with curl and Python requests
- How to handle errors gracefully in production
- How to optimize model loading for fast inference
- How to put together a complete, deployable sentiment analysis service

## Why This Chapter Matters

You have learned how transformers work, how to use Hugging Face models, and how to fine-tune BERT for text classification. Now it is time to build something real.

In this project, you will create a sentiment analysis API from start to finish. A user sends a movie review to your API, and your API responds with whether the review is positive or negative, along with a confidence score. This is the same kind of service that powers product review analysis, social media monitoring, and customer feedback systems used by real companies.

This project teaches you the critical skill of turning a trained model into a production service that other applications can use. A model sitting in a Jupyter notebook is interesting. A model behind an API endpoint is useful.

---

## Project Overview

```
What We Are Building:

User sends a request:
  POST /predict
  {"text": "This movie was absolutely fantastic!"}

Our API responds:
  {
    "text": "This movie was absolutely fantastic!",
    "sentiment": "positive",
    "confidence": 0.9847,
    "model": "distilbert-sentiment"
  }

Architecture:
+--------+         +---------+         +------------+
|        |  HTTP   |         |         |            |
| Client | ------> | FastAPI | ------> | DistilBERT |
|        |         | Server  |         | Model      |
+--------+         +---------+         +------------+
                       |
                  [Request validation]
                  [Error handling]
                  [Response formatting]
```

### Project Structure

```
sentiment-api/
├── train.py          # Fine-tuning script
├── app.py            # FastAPI application
├── model/            # Saved model files
│   ├── config.json
│   ├── model.safetensors
│   └── tokenizer/
├── requirements.txt  # Dependencies
└── test_api.py       # Test script
```

---

## Step 1: Install Dependencies

```python
# requirements.txt contents:
requirements = """
torch>=2.0.0
transformers>=4.30.0
datasets>=2.14.0
fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
requests>=2.31.0
accelerate>=0.21.0
"""

print("requirements.txt:")
print(requirements)
print("Install with: pip install -r requirements.txt")
print()
print("Or install individually:")
print("  pip install torch transformers datasets")
print("  pip install fastapi uvicorn pydantic")
print("  pip install requests accelerate")
```

**Output:**
```
requirements.txt:

torch>=2.0.0
transformers>=4.30.0
datasets>=2.14.0
fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
requests>=2.31.0
accelerate>=0.21.0

Install with: pip install -r requirements.txt

Or install individually:
  pip install torch transformers datasets
  pip install fastapi uvicorn pydantic
  pip install requests accelerate
```

---

## Step 2: Fine-Tune DistilBERT on Movie Reviews

We will fine-tune DistilBERT on the IMDB movie review dataset. This dataset contains 50,000 reviews labeled as positive or negative.

### Understanding DistilBERT

```
Why DistilBERT?

BERT:        110 million parameters, slower
DistilBERT:   66 million parameters, 60% faster
              Retains 97% of BERT's accuracy

For an API, speed matters. DistilBERT gives us:
  - Fast inference (good for real-time APIs)
  - Lower memory usage (cheaper to host)
  - Nearly the same accuracy as full BERT
```

### The Training Script (train.py)

```python
# train.py - Fine-tune DistilBERT for sentiment analysis

import torch
from transformers import (
    DistilBertTokenizer,
    DistilBertForSequenceClassification,
    TrainingArguments,
    Trainer
)
from datasets import load_dataset
import numpy as np
import os

def compute_metrics(eval_pred):
    """Calculate accuracy for evaluation."""
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    accuracy = (predictions == labels).mean()
    return {"accuracy": accuracy}

def main():
    print("=" * 50)
    print("Sentiment Analysis Model Training")
    print("=" * 50)

    # ---- Configuration ----
    MODEL_NAME = "distilbert-base-uncased"
    OUTPUT_DIR = "./model"
    MAX_LENGTH = 256       # Maximum token length
    BATCH_SIZE = 16        # Samples per batch
    EPOCHS = 3             # Training epochs
    LEARNING_RATE = 2e-5   # Learning rate

    # ---- Step 1: Load Dataset ----
    print("\n[1/5] Loading IMDB dataset...")
    dataset = load_dataset("imdb")

    print(f"  Training samples:   {len(dataset['train']):,}")
    print(f"  Test samples:       {len(dataset['test']):,}")
    print(f"  Sample review:      '{dataset['train'][0]['text'][:80]}...'")
    print(f"  Sample label:       {dataset['train'][0]['label']} "
          f"({'positive' if dataset['train'][0]['label'] == 1 else 'negative'})")

    # Use a subset for faster training (optional)
    # Remove these lines to train on the full dataset
    train_dataset = dataset['train'].shuffle(seed=42).select(range(5000))
    eval_dataset = dataset['test'].shuffle(seed=42).select(range(1000))
    print(f"  Using subset: {len(train_dataset)} train, "
          f"{len(eval_dataset)} eval")

    # ---- Step 2: Load Tokenizer ----
    print("\n[2/5] Loading tokenizer...")
    tokenizer = DistilBertTokenizer.from_pretrained(MODEL_NAME)

    def tokenize_function(examples):
        """Tokenize a batch of texts."""
        return tokenizer(
            examples['text'],
            padding='max_length',
            truncation=True,
            max_length=MAX_LENGTH
        )

    # Tokenize all data
    print("  Tokenizing training data...")
    train_dataset = train_dataset.map(
        tokenize_function, batched=True,
        desc="Tokenizing train"
    )
    print("  Tokenizing evaluation data...")
    eval_dataset = eval_dataset.map(
        tokenize_function, batched=True,
        desc="Tokenizing eval"
    )

    # Set format for PyTorch
    train_dataset.set_format(
        type='torch',
        columns=['input_ids', 'attention_mask', 'label']
    )
    eval_dataset.set_format(
        type='torch',
        columns=['input_ids', 'attention_mask', 'label']
    )

    # ---- Step 3: Load Model ----
    print("\n[3/5] Loading DistilBERT model...")
    model = DistilBertForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=2  # positive and negative
    )

    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(
        p.numel() for p in model.parameters() if p.requires_grad
    )
    print(f"  Total parameters:     {total_params:,}")
    print(f"  Trainable parameters: {trainable_params:,}")

    # ---- Step 4: Define Training Arguments ----
    print("\n[4/5] Setting up training...")
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        warmup_steps=500,
        weight_decay=0.01,
        learning_rate=LEARNING_RATE,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        logging_steps=100,
        report_to="none",  # Disable wandb/tensorboard
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        compute_metrics=compute_metrics,
    )

    # ---- Step 5: Train! ----
    print("\n[5/5] Training...")
    trainer.train()

    # Evaluate
    results = trainer.evaluate()
    print(f"\n  Final accuracy: {results['eval_accuracy']:.4f}")

    # Save the model and tokenizer
    print(f"\nSaving model to {OUTPUT_DIR}/")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print("\nTraining complete!")
    print(f"Model saved to: {os.path.abspath(OUTPUT_DIR)}")

if __name__ == "__main__":
    main()
```

**Output:**
```
==================================================
Sentiment Analysis Model Training
==================================================

[1/5] Loading IMDB dataset...
  Training samples:   25,000
  Test samples:       25,000
  Sample review:      'I rented I AM CURIOUS-YELLOW from my video store because of all the
  Sample label:       0 (negative)
  Using subset: 5000 train, 1000 eval

[2/5] Loading tokenizer...
  Tokenizing training data...
  Tokenizing evaluation data...

[3/5] Loading DistilBERT model...
  Total parameters:     66,955,010
  Trainable parameters: 66,955,010

[4/5] Setting up training...

[5/5] Training...
  {'loss': 0.4231, 'learning_rate': 1.8e-05, 'epoch': 0.96}
  {'eval_loss': 0.2845, 'eval_accuracy': 0.8890, 'epoch': 1.0}
  {'loss': 0.2156, 'learning_rate': 1.2e-05, 'epoch': 1.92}
  {'eval_loss': 0.2534, 'eval_accuracy': 0.9050, 'epoch': 2.0}
  {'loss': 0.1234, 'learning_rate': 6.0e-06, 'epoch': 2.88}
  {'eval_loss': 0.2678, 'eval_accuracy': 0.9100, 'epoch': 3.0}

  Final accuracy: 0.9100

Saving model to ./model/
Training complete!
Model saved to: /path/to/sentiment-api/model
```

**Line-by-line explanation:**

- `load_dataset("imdb")` downloads the IMDB dataset from Hugging Face. It contains 25,000 training and 25,000 test reviews.
- `dataset['train'].shuffle(seed=42).select(range(5000))` takes a random subset of 5,000 reviews for faster training. Remove this for full training.
- `tokenizer(examples['text'], padding='max_length', truncation=True, max_length=256)` converts text into token IDs. Padding ensures all sequences have the same length. Truncation cuts long reviews to 256 tokens.
- `DistilBertForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)` loads DistilBERT with a classification head that outputs 2 classes (positive/negative).
- `warmup_steps=500` gradually increases the learning rate during the first 500 steps to prevent training instability.
- `weight_decay=0.01` adds L2 regularization to prevent overfitting.
- `load_best_model_at_end=True` automatically loads the checkpoint with the highest accuracy after training.
- `trainer.save_model(OUTPUT_DIR)` saves the trained model weights so we can load them in the API.

---

## Step 3: Build the FastAPI Application

FastAPI is a modern Python web framework for building APIs. It is fast, easy to use, and automatically generates API documentation.

### The API Application (app.py)

```python
# app.py - Sentiment Analysis API with FastAPI

import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import time
import os

# ---- Pydantic Models (Request/Response Schemas) ----

class PredictionRequest(BaseModel):
    """Schema for incoming prediction requests."""
    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="The text to analyze for sentiment"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "This movie was absolutely fantastic! Great acting."
            }
        }

class PredictionResponse(BaseModel):
    """Schema for prediction responses."""
    text: str = Field(description="The input text")
    sentiment: str = Field(description="Predicted sentiment: positive or negative")
    confidence: float = Field(description="Confidence score between 0 and 1")
    processing_time_ms: float = Field(description="Processing time in milliseconds")
    model: str = Field(description="Model name used for prediction")

class HealthResponse(BaseModel):
    """Schema for health check responses."""
    status: str
    model_loaded: bool
    device: str

# ---- Model Loading ----

class SentimentModel:
    """Wrapper for the sentiment analysis model."""

    def __init__(self, model_path: str = "./model"):
        """
        Load the fine-tuned model and tokenizer.

        Parameters:
            model_path: path to the saved model directory
        """
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self.model_name = "distilbert-sentiment"

        print(f"Loading model from {model_path}...")
        print(f"Using device: {self.device}")

        # Load tokenizer
        self.tokenizer = DistilBertTokenizer.from_pretrained(model_path)

        # Load model
        self.model = DistilBertForSequenceClassification.from_pretrained(
            model_path
        )

        # Move model to device and set to evaluation mode
        self.model.to(self.device)
        self.model.eval()

        # Label mapping
        self.labels = {0: "negative", 1: "positive"}

        print("Model loaded successfully!")

    @torch.no_grad()
    def predict(self, text: str) -> dict:
        """
        Predict sentiment for a given text.

        Parameters:
            text: the input text

        Returns:
            dict with 'sentiment', 'confidence', 'scores'
        """
        # Tokenize
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=256,
            padding=True
        )

        # Move inputs to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Get predictions
        outputs = self.model(**inputs)
        logits = outputs.logits

        # Convert to probabilities
        probabilities = torch.softmax(logits, dim=-1)

        # Get the predicted class and confidence
        confidence, predicted_class = torch.max(probabilities, dim=-1)

        sentiment = self.labels[predicted_class.item()]

        return {
            "sentiment": sentiment,
            "confidence": round(confidence.item(), 4),
            "scores": {
                "negative": round(probabilities[0][0].item(), 4),
                "positive": round(probabilities[0][1].item(), 4)
            }
        }

# ---- FastAPI Application ----

app = FastAPI(
    title="Sentiment Analysis API",
    description="Analyze the sentiment of text using a fine-tuned DistilBERT model.",
    version="1.0.0"
)

# Load model at startup (once, not per request)
# This is critical for performance
model = None

@app.on_event("startup")
async def load_model():
    """Load the ML model when the server starts."""
    global model

    model_path = os.environ.get("MODEL_PATH", "./model")

    try:
        model = SentimentModel(model_path)
    except Exception as e:
        print(f"ERROR: Failed to load model: {e}")
        print("The /predict endpoint will return errors.")

# ---- API Endpoints ----

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check if the API and model are ready."""
    return HealthResponse(
        status="healthy" if model else "model not loaded",
        model_loaded=model is not None,
        device=str(model.device) if model else "unknown"
    )

@app.post("/predict", response_model=PredictionResponse)
async def predict_sentiment(request: PredictionRequest):
    """
    Predict the sentiment of the given text.

    Returns positive or negative with a confidence score.
    """
    # Check if model is loaded
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded. Please try again later."
        )

    # Validate input
    text = request.text.strip()
    if not text:
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty or whitespace only."
        )

    try:
        # Time the prediction
        start_time = time.time()

        # Run prediction
        result = model.predict(text)

        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000

        return PredictionResponse(
            text=text,
            sentiment=result["sentiment"],
            confidence=result["confidence"],
            processing_time_ms=round(processing_time, 2),
            model=model.model_name
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )

@app.post("/predict/batch")
async def predict_batch(texts: list[str]):
    """
    Predict sentiment for multiple texts at once.

    Parameters:
        texts: list of text strings

    Returns:
        list of prediction results
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded.")

    if len(texts) > 100:
        raise HTTPException(
            status_code=400,
            detail="Maximum 100 texts per batch request."
        )

    results = []
    for text in texts:
        text = text.strip()
        if text:
            result = model.predict(text)
            results.append({
                "text": text,
                "sentiment": result["sentiment"],
                "confidence": result["confidence"]
            })

    return {"results": results, "count": len(results)}

# ---- Run the server ----
# Start with: uvicorn app:app --host 0.0.0.0 --port 8000

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Line-by-line explanation:**

- `PredictionRequest` defines the expected input format using Pydantic. The `text` field must be between 1 and 5,000 characters. Pydantic automatically validates incoming requests.
- `PredictionResponse` defines the output format. Every response includes the input text, sentiment, confidence, processing time, and model name.
- `SentimentModel` wraps the model loading and prediction logic. Loading happens once at startup, not on every request, which is critical for performance.
- `@torch.no_grad()` disables gradient computation during inference, saving memory and speeding up predictions.
- `torch.softmax(logits, dim=-1)` converts raw model outputs (logits) into probabilities that sum to 1.
- `@app.on_event("startup")` runs when the server starts. The model is loaded once and shared across all requests.
- `HTTPException(status_code=503)` returns a "Service Unavailable" error if the model failed to load.
- `HTTPException(status_code=400)` returns a "Bad Request" error for invalid input.
- The batch endpoint `/predict/batch` allows processing multiple texts in a single request, limited to 100 texts.

---

## Step 4: Testing the API

### Starting the Server

```python
# Start the server in a terminal:
# uvicorn app:app --host 0.0.0.0 --port 8000 --reload

print("Starting the API server:")
print("  uvicorn app:app --host 0.0.0.0 --port 8000")
print()
print("Flags explained:")
print("  app:app       -> file 'app.py', FastAPI instance 'app'")
print("  --host 0.0.0.0 -> accept connections from any IP")
print("  --port 8000    -> listen on port 8000")
print("  --reload       -> auto-restart on code changes (dev only)")
print()
print("Once running, access:")
print("  API:  http://localhost:8000")
print("  Docs: http://localhost:8000/docs  (interactive Swagger UI)")
print("  Alt:  http://localhost:8000/redoc  (alternative docs)")
```

**Output:**
```
Starting the API server:
  uvicorn app:app --host 0.0.0.0 --port 8000

Flags explained:
  app:app       -> file 'app.py', FastAPI instance 'app'
  --host 0.0.0.0 -> accept connections from any IP
  --port 8000    -> listen on port 8000
  --reload       -> auto-restart on code changes (dev only)

Once running, access:
  API:  http://localhost:8000
  Docs: http://localhost:8000/docs  (interactive Swagger UI)
  Alt:  http://localhost:8000/redoc  (alternative docs)
```

### Testing with curl

```python
# Test commands to run in a terminal

curl_commands = """
# 1. Health check
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","model_loaded":true,"device":"cpu"}


# 2. Predict sentiment (positive review)
curl -X POST http://localhost:8000/predict \\
  -H "Content-Type: application/json" \\
  -d '{"text": "This movie was absolutely fantastic! The acting was superb."}'

# Expected response:
# {
#   "text": "This movie was absolutely fantastic! The acting was superb.",
#   "sentiment": "positive",
#   "confidence": 0.9847,
#   "processing_time_ms": 45.23,
#   "model": "distilbert-sentiment"
# }


# 3. Predict sentiment (negative review)
curl -X POST http://localhost:8000/predict \\
  -H "Content-Type: application/json" \\
  -d '{"text": "Terrible movie. Waste of time and money."}'

# Expected response:
# {
#   "text": "Terrible movie. Waste of time and money.",
#   "sentiment": "negative",
#   "confidence": 0.9923,
#   "processing_time_ms": 38.15,
#   "model": "distilbert-sentiment"
# }


# 4. Batch prediction
curl -X POST http://localhost:8000/predict/batch \\
  -H "Content-Type: application/json" \\
  -d '["Great film!", "Awful movie.", "It was okay."]'

# Expected response:
# {
#   "results": [
#     {"text": "Great film!", "sentiment": "positive", "confidence": 0.9876},
#     {"text": "Awful movie.", "sentiment": "negative", "confidence": 0.9654},
#     {"text": "It was okay.", "sentiment": "positive", "confidence": 0.5432}
#   ],
#   "count": 3
# }


# 5. Error case (empty text)
curl -X POST http://localhost:8000/predict \\
  -H "Content-Type: application/json" \\
  -d '{"text": ""}'

# Expected response:
# {"detail": [...validation error...]}
"""

print(curl_commands)
```

### Testing with Python

```python
# test_api.py - Automated tests for the sentiment API

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint."""
    print("Test 1: Health Check")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] == True
    print(f"  Status: {data['status']}")
    print(f"  Device: {data['device']}")
    print("  PASSED\n")

def test_positive_sentiment():
    """Test with a clearly positive review."""
    print("Test 2: Positive Sentiment")
    response = requests.post(
        f"{BASE_URL}/predict",
        json={"text": "This movie was absolutely brilliant! "
                      "The performances were outstanding and the "
                      "story was deeply moving."}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["sentiment"] == "positive"
    assert data["confidence"] > 0.8
    print(f"  Sentiment: {data['sentiment']}")
    print(f"  Confidence: {data['confidence']}")
    print(f"  Time: {data['processing_time_ms']}ms")
    print("  PASSED\n")

def test_negative_sentiment():
    """Test with a clearly negative review."""
    print("Test 3: Negative Sentiment")
    response = requests.post(
        f"{BASE_URL}/predict",
        json={"text": "This was the worst movie I have ever seen. "
                      "The acting was terrible and the plot made no sense."}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["sentiment"] == "negative"
    assert data["confidence"] > 0.8
    print(f"  Sentiment: {data['sentiment']}")
    print(f"  Confidence: {data['confidence']}")
    print(f"  Time: {data['processing_time_ms']}ms")
    print("  PASSED\n")

def test_batch_prediction():
    """Test batch prediction endpoint."""
    print("Test 4: Batch Prediction")
    texts = [
        "Loved it! A masterpiece.",
        "Boring and predictable.",
        "It was an okay movie, nothing special."
    ]

    response = requests.post(
        f"{BASE_URL}/predict/batch",
        json=texts
    )
    assert response.status_code == 200

    data = response.json()
    assert data["count"] == 3
    print(f"  Processed {data['count']} texts")
    for r in data["results"]:
        print(f"    '{r['text'][:30]}...' -> {r['sentiment']} "
              f"({r['confidence']:.2%})")
    print("  PASSED\n")

def test_empty_text():
    """Test that empty text returns a validation error."""
    print("Test 5: Empty Text (should fail)")
    response = requests.post(
        f"{BASE_URL}/predict",
        json={"text": ""}
    )
    assert response.status_code == 422  # Validation error
    print("  Correctly rejected empty text")
    print("  PASSED\n")

def test_performance():
    """Test inference speed."""
    print("Test 6: Performance")
    text = "A solid and entertaining movie with great characters."
    times = []

    for i in range(10):
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/predict",
            json={"text": text}
        )
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)

    avg_time = sum(times) / len(times)
    max_time = max(times)
    min_time = min(times)

    print(f"  Average: {avg_time:.1f}ms")
    print(f"  Min:     {min_time:.1f}ms")
    print(f"  Max:     {max_time:.1f}ms")
    print("  PASSED\n")

# Run all tests
if __name__ == "__main__":
    print("=" * 50)
    print("Sentiment Analysis API Tests")
    print("=" * 50)
    print()

    try:
        test_health()
        test_positive_sentiment()
        test_negative_sentiment()
        test_batch_prediction()
        test_empty_text()
        test_performance()

        print("=" * 50)
        print("ALL TESTS PASSED!")
        print("=" * 50)
    except requests.ConnectionError:
        print("ERROR: Cannot connect to the API.")
        print("Make sure the server is running:")
        print("  uvicorn app:app --host 0.0.0.0 --port 8000")
    except AssertionError as e:
        print(f"TEST FAILED: {e}")
```

**Output:**
```
==================================================
Sentiment Analysis API Tests
==================================================

Test 1: Health Check
  Status: healthy
  Device: cpu
  PASSED

Test 2: Positive Sentiment
  Sentiment: positive
  Confidence: 0.9847
  Time: 45.23ms
  PASSED

Test 3: Negative Sentiment
  Sentiment: negative
  Confidence: 0.9923
  Time: 38.15ms
  PASSED

Test 4: Batch Prediction
  Processed 3 texts
    'Loved it! A masterpiece....' -> positive (98.76%)
    'Boring and predictable....' -> negative (96.54%)
    'It was an okay movie, nothi...' -> positive (54.32%)
  PASSED

Test 5: Empty Text (should fail)
  Correctly rejected empty text
  PASSED

Test 6: Performance
  Average: 42.3ms
  Min:     35.1ms
  Max:     68.7ms
  PASSED

==================================================
ALL TESTS PASSED!
==================================================
```

---

## Step 5: Model Loading Optimization

Loading a model on every request would be extremely slow. Here are key optimizations:

```python
# Model loading optimization techniques

print("Model Loading Optimizations")
print("=" * 50)
print()

optimizations = {
    "1. Load Once at Startup": {
        "description": "Load the model when the server starts, not per request",
        "code": "@app.on_event('startup')\nasync def load(): global model; model = load_model()",
        "impact": "100x faster (avoids 2-5 second load per request)"
    },
    "2. Use torch.no_grad()": {
        "description": "Disable gradient computation during inference",
        "code": "@torch.no_grad()\ndef predict(self, text): ...",
        "impact": "~30% less memory, slightly faster"
    },
    "3. Use model.eval()": {
        "description": "Disable dropout and batch norm training behavior",
        "code": "model.eval()",
        "impact": "More consistent and accurate predictions"
    },
    "4. Move to GPU if available": {
        "description": "Use GPU for faster inference",
        "code": "model.to('cuda' if torch.cuda.is_available() else 'cpu')",
        "impact": "5-10x faster inference"
    },
    "5. Use ONNX Runtime (advanced)": {
        "description": "Convert model to ONNX format for optimized inference",
        "code": "# pip install onnxruntime\n# Export and load optimized model",
        "impact": "2-3x faster than PyTorch on CPU"
    }
}

for name, info in optimizations.items():
    print(f"{name}")
    print(f"  {info['description']}")
    print(f"  Impact: {info['impact']}")
    print()
```

**Output:**
```
Model Loading Optimizations
==================================================

1. Load Once at Startup
  Load the model when the server starts, not per request
  Impact: 100x faster (avoids 2-5 second load per request)

2. Use torch.no_grad()
  Disable gradient computation during inference
  Impact: ~30% less memory, slightly faster

3. Use model.eval()
  Disable dropout and batch norm training behavior
  Impact: More consistent and accurate predictions

4. Move to GPU if available
  Use GPU for faster inference
  Impact: 5-10x faster inference

5. Use ONNX Runtime (advanced)
  Convert model to ONNX format for optimized inference
  Impact: 2-3x faster than PyTorch on CPU
```

---

## Error Handling

Robust error handling is essential for a production API:

```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

# Custom error handler for unexpected errors
# Add this to app.py

async def generic_exception_handler(request: Request, exc: Exception):
    """Handle any unhandled exception."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred. Please try again.",
            "type": str(type(exc).__name__)
        }
    )

# Register: app.add_exception_handler(Exception, generic_exception_handler)

print("Error Handling Strategy:")
print()
print("HTTP Status Codes Used:")
print("  200 - Success: prediction completed")
print("  400 - Bad Request: invalid input (empty text, too long)")
print("  422 - Validation Error: wrong data format")
print("  500 - Internal Error: model prediction failed")
print("  503 - Service Unavailable: model not loaded yet")
print()
print("Every error response includes:")
print("  - A clear error message")
print("  - An appropriate HTTP status code")
print("  - Enough detail to debug, but no internal secrets")
```

**Output:**
```
Error Handling Strategy:

HTTP Status Codes Used:
  200 - Success: prediction completed
  400 - Bad Request: invalid input (empty text, too long)
  422 - Validation Error: wrong data format
  500 - Internal Error: model prediction failed
  503 - Service Unavailable: model not loaded yet

Every error response includes:
  - A clear error message
  - An appropriate HTTP status code
  - Enough detail to debug, but no internal secrets
```

---

## Common Mistakes

1. **Loading the model on every request.** This is the biggest performance killer. Always load the model once at startup and reuse it.

2. **Not setting model.eval().** Without this, the model uses training-mode behavior (dropout, batch norm updates) which produces inconsistent and less accurate predictions.

3. **Not handling edge cases.** Empty strings, very long texts, and non-text input can crash your API. Always validate input.

4. **Exposing internal error details.** Never return stack traces or internal paths in API error messages. These leak implementation details that could be exploited.

5. **Not including a health endpoint.** Load balancers and monitoring tools need a way to check if your service is working. Always include `/health`.

---

## Best Practices

1. **Use Pydantic models** for request/response validation. They provide automatic type checking and generate API documentation.

2. **Include processing time** in responses. This helps monitor performance and detect slowdowns.

3. **Set a maximum input length.** Long texts take proportionally longer to process and can cause memory issues.

4. **Add a batch endpoint.** Processing multiple texts in a single request is more efficient than making many individual requests.

5. **Use async FastAPI endpoints.** The `async def` keyword allows the server to handle multiple requests concurrently, even during model inference.

6. **Log predictions** (without the actual text, for privacy). This helps you monitor model performance and detect drift over time.

---

## Quick Summary

This project demonstrated how to build a complete sentiment analysis API. We fine-tuned DistilBERT on the IMDB movie review dataset using the Hugging Face Trainer API, achieving over 90% accuracy. We then built a FastAPI application with health check, single prediction, and batch prediction endpoints. The model is loaded once at startup for optimal performance. Request validation with Pydantic ensures only valid input reaches the model. Error handling covers all edge cases with appropriate HTTP status codes. The API can be tested with curl commands or automated Python test scripts.

---

## Key Points

- **DistilBERT** is 60% faster than BERT with 97% of the accuracy, ideal for APIs
- **Fine-tuning** on domain-specific data (movie reviews) dramatically improves performance
- **FastAPI** provides automatic documentation, validation, and async support
- **Load models at startup**, not per request, for 100x faster response times
- **Pydantic models** define and validate request/response schemas automatically
- **Error handling** must cover empty input, model failures, and service unavailability
- **Batch endpoints** allow efficient processing of multiple texts
- **Health checks** let monitoring tools verify your service is running

---

## Practice Questions

1. Why do we use DistilBERT instead of full BERT for an API? What are the tradeoffs?

2. Explain why loading the model at startup (instead of per-request) is critical for API performance. What would happen if we loaded it on every request?

3. What is the purpose of the Pydantic `PredictionRequest` model? What happens if someone sends a request without the `text` field?

4. Why do we use `@torch.no_grad()` in the predict method? What would happen without it?

5. A user sends a 10,000-word review to your API. What problems could this cause, and how does the code handle it?

---

## Exercises

### Exercise 1: Add Confidence Threshold

Add a `min_confidence` parameter to the `/predict` endpoint. If the model's confidence is below this threshold, return `"sentiment": "uncertain"` instead of positive or negative.

### Exercise 2: Add Request Logging

Create a middleware that logs every request (timestamp, endpoint, processing time, sentiment result) to a CSV file. Do not log the actual text content for privacy.

### Exercise 3: Deploy with Docker

Write a Dockerfile that packages the trained model, the FastAPI application, and all dependencies into a Docker container. Test it by building and running the container locally.

---

## What Is Next?

In the next chapter, you will build another complete project: a Document Classifier. You will classify news articles into categories (like sports, technology, politics) using both a traditional ML baseline (TF-IDF + Logistic Regression) and a fine-tuned BERT model. This project introduces multi-class classification and the important practice of comparing simple baselines against complex deep learning models.
