# Chapter 3: Building ML APIs with FastAPI

## What You Will Learn

In this chapter, you will learn:

- What an API is and why ML models need one
- How to install and use FastAPI
- How to create prediction endpoints for your ML model
- How to define request and response models with Pydantic
- How to load a model at startup so it is ready for predictions
- How to test your API with curl and httpx
- How to build a complete ML prediction API

## Why This Chapter Matters

Imagine you have built a brilliant weather prediction model. It runs on your laptop and gives amazing forecasts. But your laptop is in your bedroom. How does the weather app on a million phones get your predictions?

The answer is an API (Application Programming Interface). An API is like a restaurant waiter. You (the customer) tell the waiter what you want (your order). The waiter goes to the kitchen (the model), gets your food (the prediction), and brings it back to you. You never need to enter the kitchen, and the chef never needs to meet you.

FastAPI is one of the best tools for building these "waiters" in Python. It is fast, easy to use, and automatically creates documentation for your API.

---

## What Is an API?

API stands for Application Programming Interface. Let us break that down:

```
+--------------------------------------------------+
|  API Analogy: The Restaurant                     |
|                                                   |
|  Customer (Client App)                           |
|       |                                           |
|       | "I want the salmon" (Request)            |
|       v                                           |
|  Waiter (API)                                    |
|       |                                           |
|       | Takes order to kitchen                   |
|       v                                           |
|  Kitchen (ML Model)                              |
|       |                                           |
|       | Prepares food (Makes prediction)         |
|       v                                           |
|  Waiter (API)                                    |
|       |                                           |
|       | "Here is your salmon" (Response)         |
|       v                                           |
|  Customer (Client App)                           |
+--------------------------------------------------+
```

In ML, a typical API flow looks like this:

```
+--------------------------------------------------+
|  ML API Flow                                     |
|                                                   |
|  Phone App sends:  {"age": 25, "income": 50000}  |
|       |                                           |
|       v                                           |
|  API receives the data                           |
|       |                                           |
|       v                                           |
|  Model predicts: "low risk"                      |
|       |                                           |
|       v                                           |
|  API sends back: {"prediction": "low risk",      |
|                    "confidence": 0.92}            |
+--------------------------------------------------+
```

---

## Installing FastAPI

FastAPI requires two packages:

```bash
pip install fastapi uvicorn
```

- **FastAPI** is the framework for building APIs
- **Uvicorn** is the server that runs your API (like how a car engine runs the car)

---

## Your First FastAPI App

Let us start with the simplest possible API:

```python
"""
hello_api.py - Your very first FastAPI application.

Run with: uvicorn hello_api:app --reload

The --reload flag automatically restarts the server
when you change the code. Very handy during development.
"""

from fastapi import FastAPI

# Create the FastAPI application
# This is like opening your restaurant
app = FastAPI(
    title="My First API",
    description="A simple API to learn FastAPI",
    version="1.0.0",
)


# Define an endpoint (a "menu item")
# The @app.get decorator tells FastAPI:
# "When someone visits /hello, run this function"
@app.get("/hello")
def say_hello():
    """Return a friendly greeting."""
    return {"message": "Hello, World!"}


@app.get("/hello/{name}")
def say_hello_to(name: str):
    """
    Greet a specific person.

    The {name} in the URL is a path parameter.
    Whatever the user puts there becomes the 'name' variable.
    """
    return {"message": f"Hello, {name}!"}
```

To run this API:

```bash
uvicorn hello_api:app --reload
```

```
Output:
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Now you can visit:
- `http://127.0.0.1:8000/hello` to see `{"message": "Hello, World!"}`
- `http://127.0.0.1:8000/hello/Alice` to see `{"message": "Hello, Alice!"}`
- `http://127.0.0.1:8000/docs` to see automatic documentation

**Line-by-line explanation:**

```python
app = FastAPI(title="My First API", ...)
```

This creates your API application. Think of it as registering your restaurant business. The title, description, and version appear in the auto-generated documentation.

```python
@app.get("/hello")
```

This is a decorator. It tells FastAPI: "When someone sends a GET request to /hello, run the function below." GET is an HTTP method that means "give me data." There are also POST (send data), PUT (update data), and DELETE (remove data).

```python
def say_hello():
    return {"message": "Hello, World!"}
```

This function handles the request. It returns a Python dictionary, which FastAPI automatically converts to JSON (the standard data format for APIs).

---

## Request and Response Models with Pydantic

When someone sends data to your ML model, you want to make sure the data is correct. Pydantic models are like bouncers at a club. They check if the data meets your requirements before letting it in.

```python
"""
pydantic_models.py - Define what data your API accepts and returns.

Pydantic models validate incoming data automatically.
If someone sends the wrong type of data, they get a
clear error message.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class PredictionRequest(BaseModel):
    """
    What the client sends to get a prediction.

    Each field has a type and an optional description.
    Pydantic will automatically reject data that does
    not match these types.
    """

    # Field() lets you add descriptions and constraints
    age: int = Field(
        ...,  # ... means this field is required
        description="Age of the person in years",
        ge=0,   # ge = greater than or equal to
        le=150,  # le = less than or equal to
    )

    income: float = Field(
        ...,
        description="Annual income in dollars",
        ge=0,
    )

    credit_score: int = Field(
        ...,
        description="Credit score (300-850)",
        ge=300,
        le=850,
    )

    # Optional field with a default value
    employment_years: Optional[float] = Field(
        default=0.0,
        description="Years of employment",
        ge=0,
    )


class PredictionResponse(BaseModel):
    """
    What the API sends back after making a prediction.
    """

    prediction: str = Field(
        description="The prediction result"
    )

    confidence: float = Field(
        description="How confident the model is (0 to 1)"
    )

    risk_level: str = Field(
        description="Risk category: low, medium, or high"
    )


class BatchPredictionRequest(BaseModel):
    """
    For predicting multiple items at once.
    """

    items: List[PredictionRequest] = Field(
        description="List of items to predict"
    )


# Example: Create an instance to see how it works
request = PredictionRequest(
    age=30,
    income=65000.0,
    credit_score=720,
    employment_years=5.0,
)
print(f"Valid request: {request}")
print(f"As dictionary: {request.model_dump()}")

# This would raise an error:
# invalid = PredictionRequest(age=-5, income=50000, credit_score=200)
# ValueError: age must be >= 0, credit_score must be >= 300
```

```
Output:
Valid request: age=30 income=65000.0 credit_score=720 employment_years=5.0
As dictionary: {'age': 30, 'income': 65000.0, 'credit_score': 720, 'employment_years': 5.0}
```

---

## Loading Your Model at Startup

You do not want to load your model every time someone makes a request. That would be like starting your car engine every time you need to check the speedometer. Instead, load the model once when the API starts, and keep it in memory.

```python
"""
model_loading.py - Load model once at API startup.

The @app.on_event("startup") decorator runs a function
once when the API starts. This is where we load our model.
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
import joblib
import logging

logger = logging.getLogger(__name__)

# Global variable to hold the model
# We load it once and reuse it for every request
ml_model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage the lifecycle of the application.

    Code before 'yield' runs at startup.
    Code after 'yield' runs at shutdown.

    This is the modern way to handle startup/shutdown
    events in FastAPI.
    """
    global ml_model

    # Startup: Load the model
    logger.info("Loading ML model...")
    try:
        ml_model = joblib.load("models/trained_model.pkl")
        logger.info("Model loaded successfully!")
    except FileNotFoundError:
        logger.error("Model file not found!")
        raise

    yield  # The API runs here

    # Shutdown: Clean up
    logger.info("Shutting down, cleaning up...")
    ml_model = None


app = FastAPI(
    title="ML Prediction API",
    lifespan=lifespan,
)


@app.get("/health")
def health_check():
    """
    Health check endpoint.

    Other services use this to check if our API is running.
    It is like asking "Are you still there?"
    """
    return {
        "status": "healthy",
        "model_loaded": ml_model is not None,
    }
```

---

## Complete ML Prediction API

Now let us put everything together into a complete, production-ready API:

```python
"""
main.py - Complete ML Prediction API with FastAPI.

This API loads a trained model and serves predictions
through HTTP endpoints.

Run with: uvicorn main:app --reload --host 0.0.0.0 --port 8000

Structure:
  POST /predict         -> Single prediction
  POST /predict/batch   -> Multiple predictions
  GET  /health          -> Health check
  GET  /model/info      -> Model information
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
from typing import List, Optional
import joblib
import numpy as np
import logging
import time
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================
# Pydantic Models (Data Validation)
# ============================================================

class PredictionRequest(BaseModel):
    """Input data for a single prediction."""

    age: int = Field(..., ge=0, le=150, description="Age in years")
    income: float = Field(..., ge=0, description="Annual income")
    credit_score: int = Field(..., ge=300, le=850, description="Credit score")
    employment_years: float = Field(default=0.0, ge=0, description="Years employed")

    # model_config replaces the old Config inner class
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "age": 30,
                    "income": 65000.0,
                    "credit_score": 720,
                    "employment_years": 5.0,
                }
            ]
        }
    }


class PredictionResponse(BaseModel):
    """Output from a single prediction."""

    prediction: int = Field(description="0 = low risk, 1 = high risk")
    probability: float = Field(description="Probability of high risk")
    risk_label: str = Field(description="Human-readable risk level")
    processing_time_ms: float = Field(description="Time to make prediction")


class BatchRequest(BaseModel):
    """Input for multiple predictions."""

    items: List[PredictionRequest] = Field(
        description="List of prediction requests"
    )


class BatchResponse(BaseModel):
    """Output for multiple predictions."""

    predictions: List[PredictionResponse]
    total_items: int
    total_processing_time_ms: float


class ModelInfo(BaseModel):
    """Information about the loaded model."""

    model_type: str
    n_features: int
    model_version: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    model_loaded: bool
    uptime_seconds: float


# ============================================================
# Application Setup
# ============================================================

# Global state
ml_model = None
model_info = {}
start_time = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model at startup, clean up at shutdown."""
    global ml_model, model_info, start_time

    start_time = time.time()

    # Load model
    model_path = os.getenv("MODEL_PATH", "models/trained_model.pkl")
    logger.info(f"Loading model from: {model_path}")

    try:
        ml_model = joblib.load(model_path)
        model_info = {
            "model_type": type(ml_model).__name__,
            "n_features": getattr(ml_model, "n_features_in_", 4),
            "model_version": os.getenv("MODEL_VERSION", "1.0.0"),
        }
        logger.info(f"Model loaded: {model_info['model_type']}")
    except FileNotFoundError:
        logger.warning(f"Model not found at {model_path}, running without model")
        ml_model = None

    yield

    logger.info("Shutting down...")
    ml_model = None


app = FastAPI(
    title="ML Prediction API",
    description="A complete API for serving ML predictions",
    version="1.0.0",
    lifespan=lifespan,
)


# ============================================================
# Helper Functions
# ============================================================

def prepare_features(request: PredictionRequest) -> np.ndarray:
    """
    Convert a request into a feature array for the model.

    The model expects features in a specific order as a
    numpy array. This function ensures the conversion is
    consistent.
    """
    features = np.array([[
        request.age,
        request.income,
        request.credit_score,
        request.employment_years,
    ]])
    return features


def get_risk_label(probability: float) -> str:
    """
    Convert probability to a human-readable label.

    Parameters
    ----------
    probability : float
        Probability of high risk (0.0 to 1.0).

    Returns
    -------
    str
        "low", "medium", or "high"
    """
    if probability < 0.3:
        return "low"
    elif probability < 0.7:
        return "medium"
    else:
        return "high"


# ============================================================
# API Endpoints
# ============================================================

@app.get("/health", response_model=HealthResponse)
def health_check():
    """
    Check if the API is running and the model is loaded.

    This endpoint is used by monitoring tools and load
    balancers to verify the service is healthy.
    """
    return HealthResponse(
        status="healthy" if ml_model is not None else "degraded",
        model_loaded=ml_model is not None,
        uptime_seconds=time.time() - start_time if start_time else 0,
    )


@app.get("/model/info", response_model=ModelInfo)
def get_model_info():
    """
    Get information about the loaded model.

    Useful for debugging and knowing which model version
    is currently serving predictions.
    """
    if ml_model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded",
        )
    return ModelInfo(**model_info)


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    """
    Make a single prediction.

    Send the input features and get back a prediction
    with probability and risk label.
    """
    if ml_model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please check the model path.",
        )

    start = time.time()

    # Prepare features
    features = prepare_features(request)

    # Make prediction
    prediction = int(ml_model.predict(features)[0])

    # Get probability (if model supports it)
    try:
        probability = float(
            ml_model.predict_proba(features)[0][1]
        )
    except AttributeError:
        # Some models do not have predict_proba
        probability = float(prediction)

    processing_time = (time.time() - start) * 1000

    return PredictionResponse(
        prediction=prediction,
        probability=round(probability, 4),
        risk_label=get_risk_label(probability),
        processing_time_ms=round(processing_time, 2),
    )


@app.post("/predict/batch", response_model=BatchResponse)
def predict_batch(request: BatchRequest):
    """
    Make predictions for multiple items at once.

    Batch prediction is more efficient than making
    many individual requests.
    """
    if ml_model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded",
        )

    start = time.time()
    predictions = []

    # Process all items
    # In production, you would vectorize this for speed
    for item in request.items:
        features = prepare_features(item)
        pred = int(ml_model.predict(features)[0])

        try:
            prob = float(ml_model.predict_proba(features)[0][1])
        except AttributeError:
            prob = float(pred)

        predictions.append(
            PredictionResponse(
                prediction=pred,
                probability=round(prob, 4),
                risk_label=get_risk_label(prob),
                processing_time_ms=0,  # Individual time not tracked in batch
            )
        )

    total_time = (time.time() - start) * 1000

    return BatchResponse(
        predictions=predictions,
        total_items=len(predictions),
        total_processing_time_ms=round(total_time, 2),
    )


# ============================================================
# Run directly (alternative to uvicorn command)
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
```

---

## Testing Your API

### Testing with curl

curl is a command-line tool for making HTTP requests. Think of it as a phone that can call your API.

```bash
# Test the health endpoint
curl http://localhost:8000/health
```

```json
{
  "status": "healthy",
  "model_loaded": true,
  "uptime_seconds": 45.23
}
```

```bash
# Make a prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 30, "income": 65000, "credit_score": 720, "employment_years": 5}'
```

```json
{
  "prediction": 0,
  "probability": 0.1532,
  "risk_label": "low",
  "processing_time_ms": 2.45
}
```

```bash
# Batch prediction
curl -X POST http://localhost:8000/predict/batch \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"age": 25, "income": 40000, "credit_score": 650, "employment_years": 2},
      {"age": 55, "income": 120000, "credit_score": 800, "employment_years": 25}
    ]
  }'
```

```json
{
  "predictions": [
    {"prediction": 1, "probability": 0.7234, "risk_label": "high", "processing_time_ms": 0},
    {"prediction": 0, "probability": 0.0845, "risk_label": "low", "processing_time_ms": 0}
  ],
  "total_items": 2,
  "total_processing_time_ms": 3.12
}
```

**Understanding the curl commands:**

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 30, ...}'
```

- `curl` is the command-line HTTP client
- `-X POST` means we are sending data (not just requesting it)
- `http://localhost:8000/predict` is the URL of our endpoint
- `-H "Content-Type: application/json"` tells the API we are sending JSON data
- `-d '{...}'` is the actual data (the JSON body)

### Testing with Python (httpx)

httpx is a Python library for making HTTP requests. It is like curl but in Python:

```python
"""
test_api.py - Test the ML API using httpx.

Install: pip install httpx
Run: python test_api.py

Make sure the API is running first:
    uvicorn main:app --reload
"""

import httpx

# Base URL of our API
BASE_URL = "http://localhost:8000"


def test_health():
    """Test the health check endpoint."""
    response = httpx.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("Health check PASSED\n")


def test_single_prediction():
    """Test a single prediction."""
    data = {
        "age": 30,
        "income": 65000.0,
        "credit_score": 720,
        "employment_years": 5.0,
    }

    response = httpx.post(
        f"{BASE_URL}/predict",
        json=data,  # json= automatically sets Content-Type
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("Single prediction PASSED\n")


def test_batch_prediction():
    """Test batch prediction."""
    data = {
        "items": [
            {"age": 25, "income": 40000, "credit_score": 650, "employment_years": 2},
            {"age": 45, "income": 90000, "credit_score": 780, "employment_years": 15},
            {"age": 60, "income": 150000, "credit_score": 810, "employment_years": 30},
        ]
    }

    response = httpx.post(
        f"{BASE_URL}/predict/batch",
        json=data,
    )

    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Total items: {result['total_items']}")
    for i, pred in enumerate(result["predictions"]):
        print(f"  Item {i+1}: risk={pred['risk_label']}, prob={pred['probability']}")
    assert response.status_code == 200
    print("Batch prediction PASSED\n")


def test_invalid_input():
    """Test that invalid data gets rejected."""
    data = {
        "age": -5,  # Invalid: negative age
        "income": 50000,
        "credit_score": 100,  # Invalid: below 300
    }

    response = httpx.post(
        f"{BASE_URL}/predict",
        json=data,
    )

    print(f"Status Code: {response.status_code}")
    print(f"Error: {response.json()}")
    assert response.status_code == 422  # Validation error
    print("Invalid input test PASSED\n")


def test_model_info():
    """Test the model info endpoint."""
    response = httpx.get(f"{BASE_URL}/model/info")
    print(f"Status Code: {response.status_code}")
    print(f"Model Info: {response.json()}")
    print("Model info PASSED\n")


if __name__ == "__main__":
    print("Testing ML API\n" + "=" * 40)
    test_health()
    test_single_prediction()
    test_batch_prediction()
    test_invalid_input()
    test_model_info()
    print("=" * 40)
    print("All tests passed!")
```

```
Output:
Testing ML API
========================================
Status Code: 200
Response: {'status': 'healthy', 'model_loaded': True, 'uptime_seconds': 12.5}
Health check PASSED

Status Code: 200
Response: {'prediction': 0, 'probability': 0.1532, 'risk_label': 'low', 'processing_time_ms': 2.45}
Single prediction PASSED

Status Code: 200
Total items: 3
  Item 1: risk=high, prob=0.7234
  Item 2: risk=low, prob=0.2156
  Item 3: risk=low, prob=0.0845
Batch prediction PASSED

Status Code: 422
Error: {'detail': [{'msg': 'ensure this value is greater than or equal to 0', ...}]}
Invalid input test PASSED

Status Code: 200
Model Info: {'model_type': 'RandomForestClassifier', 'n_features': 4, 'model_version': '1.0.0'}
Model info PASSED

========================================
All tests passed!
```

---

## Automatic API Documentation

One of FastAPI's best features is automatic documentation. When you run your API, visit `http://localhost:8000/docs` to see an interactive documentation page.

```
+--------------------------------------------------+
|  FastAPI Auto-Generated Documentation            |
|  http://localhost:8000/docs                      |
|                                                   |
|  GET  /health        -> Health check              |
|  GET  /model/info    -> Model information         |
|  POST /predict       -> Single prediction         |
|  POST /predict/batch -> Batch prediction          |
|                                                   |
|  Each endpoint shows:                            |
|  - Expected input format                         |
|  - Example values                                |
|  - Response format                               |
|  - "Try it out" button to test live!             |
+--------------------------------------------------+
```

---

## Common Mistakes

1. **Loading the model inside the endpoint function.** This loads the model on every request, making the API slow. Load it once at startup.

2. **Not validating input data.** Without Pydantic models, bad data can crash your model. Always validate inputs.

3. **Returning raw numpy types.** FastAPI cannot serialize numpy int64 or float64 directly. Convert to Python int() or float() first.

4. **No health check endpoint.** Load balancers and monitoring tools need a way to check if your API is alive.

5. **Hardcoding the model path.** Use environment variables so you can change the path without modifying code.

---

## Best Practices

1. **Use Pydantic models for all inputs and outputs.** They validate data and generate documentation automatically.

2. **Load models at startup using the lifespan context manager.** This is the modern, recommended approach in FastAPI.

3. **Add a health check endpoint.** It should verify the model is loaded and the API is functioning.

4. **Include processing time in responses.** This helps monitor API performance.

5. **Use environment variables for configuration.** This makes your API easy to deploy in different environments.

6. **Write tests.** Test every endpoint with valid and invalid data.

---

## Quick Summary

FastAPI makes it easy to serve ML models as web APIs. You define input and output schemas with Pydantic, load your model at startup, and create endpoints that accept data and return predictions. FastAPI automatically validates inputs, generates documentation, and handles errors gracefully.

---

## Key Points

- An API lets other applications use your ML model over the network
- FastAPI is a modern, fast Python framework for building APIs
- Pydantic models validate input data automatically
- Load models once at startup, not on every request
- Always include health check and model info endpoints
- Test with curl (command line) or httpx (Python)
- FastAPI generates interactive documentation at /docs

---

## Practice Questions

1. What is the difference between a GET and a POST request? When would you use each one?

2. Why should you load your ML model at startup rather than inside the prediction endpoint?

3. What does Pydantic do, and why is it important for an ML API?

4. What HTTP status code does FastAPI return when input validation fails? What does this code mean?

5. How would you make your API accept an optional parameter, like a confidence threshold?

---

## Exercises

### Exercise 1: Build a Sentiment API

Create a FastAPI application that:
- Accepts a text string as input
- Returns a sentiment prediction (positive/negative) with confidence
- Includes a health check endpoint
- Validates that the text is not empty

### Exercise 2: Add Error Handling

Extend the prediction API to handle these edge cases:
- Model file not found at startup
- Input features with extreme values (age = 999)
- Request with missing required fields

### Exercise 3: Add Request Logging

Add middleware that logs every request including:
- The endpoint that was called
- The time the request was received
- How long the request took to process
- Whether it succeeded or failed

---

## What Is Next?

Your API works great on your laptop. But how do you run it on a server where everyone can access it? In Chapter 4, we will learn about Docker, which packages your API and all its dependencies into a container that can run anywhere. Think of it as putting your API in a shipping container that can be delivered to any server in the world.
