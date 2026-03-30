# Chapter 7: Model Serving Patterns

## What You Will Learn

In this chapter, you will learn:

- The difference between batch and real-time inference
- Common model serving patterns used in production
- How to think about scaling your model serving
- How to cache predictions to improve speed and reduce cost

## Why This Chapter Matters

Imagine a restaurant. Some dishes are made fresh when you order them (real-time). Others, like soup, are made in large batches in the morning and served throughout the day (batch). Each approach has its strengths.

ML model serving works the same way. Sometimes you need predictions instantly (a fraud detection system checking each credit card swipe). Sometimes you can wait and process everything at once (generating product recommendations overnight for all users). Choosing the right pattern affects speed, cost, and complexity.

---

## Batch vs Real-Time Inference

These are the two fundamental ways to serve predictions:

```
+--------------------------------------------------+
|  Batch Inference                                  |
|                                                   |
|  "Make all the soup in the morning"              |
|                                                   |
|  [Data] --> [Model] --> [Store Results]           |
|  (1000 items at once)   (Database/File)          |
|                                                   |
|  When to use:                                    |
|  - Results not needed immediately                |
|  - Large volume of predictions                   |
|  - Scheduled processing (daily, hourly)          |
|  - Cost-sensitive (cheaper to run in bulk)       |
|                                                   |
|  Examples:                                       |
|  - Nightly product recommendations               |
|  - Monthly churn risk scores                     |
|  - Weekly email targeting                        |
+--------------------------------------------------+

+--------------------------------------------------+
|  Real-Time Inference                              |
|                                                   |
|  "Cook each dish when ordered"                   |
|                                                   |
|  [Request] --> [Model] --> [Response]            |
|  (1 item)     (instant)   (milliseconds)         |
|                                                   |
|  When to use:                                    |
|  - Results needed immediately                    |
|  - User is waiting for a response               |
|  - Input data is not known in advance            |
|                                                   |
|  Examples:                                       |
|  - Fraud detection on card swipe                 |
|  - Autocomplete suggestions while typing         |
|  - Image classification on upload                |
+--------------------------------------------------+
```

### Batch Inference Implementation

```python
"""
batch_inference.py - Process predictions in bulk.

Batch inference is efficient because:
1. The model is loaded once
2. Data can be processed in optimized chunks
3. Results are stored for later use
4. It can run during off-peak hours
"""

import joblib
import pandas as pd
import numpy as np
import json
import time
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_batch_inference(
    model_path,
    input_path,
    output_path,
    batch_size=1000,
):
    """
    Run predictions on a large dataset in batches.

    Parameters
    ----------
    model_path : str
        Path to the saved model file.
    input_path : str
        Path to the input CSV file.
    output_path : str
        Path to save predictions.
    batch_size : int
        Number of rows to process at once.
        Larger batches are faster but use more memory.
    """
    start_time = time.time()
    logger.info(f"Starting batch inference at {datetime.now()}")

    # Load model once
    logger.info(f"Loading model from {model_path}")
    model = joblib.load(model_path)

    # Load data
    logger.info(f"Loading data from {input_path}")
    df = pd.read_csv(input_path)
    total_rows = len(df)
    logger.info(f"Total rows to process: {total_rows}")

    # Process in batches
    all_predictions = []
    all_probabilities = []

    for i in range(0, total_rows, batch_size):
        batch = df.iloc[i : i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (total_rows + batch_size - 1) // batch_size

        logger.info(
            f"Processing batch {batch_num}/{total_batches} "
            f"({len(batch)} rows)"
        )

        # Make predictions for this batch
        features = batch.values
        predictions = model.predict(features)
        all_predictions.extend(predictions)

        # Get probabilities if available
        try:
            probabilities = model.predict_proba(features)[:, 1]
            all_probabilities.extend(probabilities)
        except AttributeError:
            all_probabilities.extend(predictions.astype(float))

    # Add predictions to the dataframe
    df["prediction"] = all_predictions
    df["probability"] = all_probabilities
    df["predicted_at"] = datetime.now().isoformat()

    # Save results
    df.to_csv(output_path, index=False)

    elapsed = time.time() - start_time
    logger.info(f"Batch inference complete!")
    logger.info(f"Processed {total_rows} rows in {elapsed:.1f} seconds")
    logger.info(f"Speed: {total_rows / elapsed:.0f} rows/second")
    logger.info(f"Results saved to {output_path}")

    return df


# Run batch inference
results = run_batch_inference(
    model_path="models/trained_model.pkl",
    input_path="data/customers_to_predict.csv",
    output_path="data/predictions_output.csv",
    batch_size=500,
)
```

```
Output:
INFO - Starting batch inference at 2024-01-15 10:00:00
INFO - Loading model from models/trained_model.pkl
INFO - Loading data from data/customers_to_predict.csv
INFO - Total rows to process: 10000
INFO - Processing batch 1/20 (500 rows)
INFO - Processing batch 2/20 (500 rows)
...
INFO - Processing batch 20/20 (500 rows)
INFO - Batch inference complete!
INFO - Processed 10000 rows in 4.2 seconds
INFO - Speed: 2381 rows/second
INFO - Results saved to data/predictions_output.csv
```

### Real-Time Inference Implementation

```python
"""
realtime_inference.py - Serve predictions one at a time.

Real-time inference focuses on low latency.
Each request must be fast (typically under 100ms).
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import time
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

# Global model reference
model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model at startup."""
    global model
    logger.info("Loading model for real-time serving...")
    model = joblib.load("models/trained_model.pkl")
    logger.info("Model loaded and ready!")
    yield
    model = None


app = FastAPI(title="Real-Time ML API", lifespan=lifespan)


class PredictRequest(BaseModel):
    features: list[float]


class PredictResponse(BaseModel):
    prediction: int
    probability: float
    latency_ms: float


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    """
    Make a single prediction with minimal latency.

    The focus here is speed. Every millisecond counts
    in real-time serving.
    """
    if model is None:
        raise HTTPException(503, "Model not loaded")

    start = time.time()

    # Convert to numpy array (fast)
    features = np.array([request.features])

    # Predict (this is the main bottleneck)
    prediction = int(model.predict(features)[0])

    try:
        probability = float(model.predict_proba(features)[0][1])
    except AttributeError:
        probability = float(prediction)

    latency = (time.time() - start) * 1000

    return PredictResponse(
        prediction=prediction,
        probability=round(probability, 4),
        latency_ms=round(latency, 2),
    )
```

---

## Model Serving Patterns

There are several patterns for how to organize model serving in a larger system:

```
+--------------------------------------------------+
|  Pattern 1: Embedded Model                       |
|                                                   |
|  The model lives inside the application.         |
|  Simple but tightly coupled.                     |
|                                                   |
|  +-------------------------------+               |
|  |  Web Application              |               |
|  |  +----------+                 |               |
|  |  |  Model   |                 |               |
|  |  +----------+                 |               |
|  +-------------------------------+               |
|                                                   |
|  Good for: Simple apps, prototypes               |
|  Bad for: Multiple apps sharing a model          |
+--------------------------------------------------+

+--------------------------------------------------+
|  Pattern 2: Model as a Service                   |
|                                                   |
|  The model runs in its own API.                  |
|  Applications call it over the network.          |
|                                                   |
|  +----------+      +----------+                  |
|  | App 1    |----->|          |                  |
|  +----------+      | Model    |                  |
|  +----------+      | Service  |                  |
|  | App 2    |----->|          |                  |
|  +----------+      +----------+                  |
|                                                   |
|  Good for: Multiple apps, independent scaling    |
|  Bad for: Extra network latency                  |
+--------------------------------------------------+

+--------------------------------------------------+
|  Pattern 3: Model Gateway                        |
|                                                   |
|  A gateway routes requests to different models.  |
|  Useful for A/B testing and canary deployments.  |
|                                                   |
|  +----------+      +---------+      +---------+ |
|  |          |----->| Model   |  80% | Model A | |
|  | Gateway  |      | Router  |----->| (v1.0)  | |
|  |          |      |         |  20% +---------+ |
|  +----------+      |         |----->| Model B | |
|                     +---------+      | (v2.0)  | |
|                                      +---------+ |
|  Good for: A/B testing, gradual rollouts        |
+--------------------------------------------------+
```

### Implementing Model as a Service

```python
"""
model_service.py - Model serving as an independent service.

This pattern separates the model from the application.
The application sends data to this service and gets
predictions back.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
import joblib
import numpy as np
import time
import os
import logging

logger = logging.getLogger(__name__)


class ModelService:
    """
    A service that manages model loading and prediction.

    This class encapsulates all model-related logic,
    making it easy to swap models or add features
    like caching.
    """

    def __init__(self):
        self.model = None
        self.model_version = None
        self.model_loaded_at = None

    def load(self, model_path, version="unknown"):
        """Load a model from disk."""
        self.model = joblib.load(model_path)
        self.model_version = version
        self.model_loaded_at = time.time()
        logger.info(
            f"Model v{version} loaded from {model_path}"
        )

    def predict(self, features):
        """Make a prediction."""
        if self.model is None:
            raise RuntimeError("Model not loaded")

        features_array = np.array([features])
        prediction = int(self.model.predict(features_array)[0])

        try:
            probability = float(
                self.model.predict_proba(features_array)[0][1]
            )
        except AttributeError:
            probability = float(prediction)

        return {
            "prediction": prediction,
            "probability": probability,
            "model_version": self.model_version,
        }

    def get_info(self):
        """Get information about the loaded model."""
        return {
            "model_version": self.model_version,
            "model_type": type(self.model).__name__ if self.model else None,
            "loaded": self.model is not None,
            "uptime_seconds": (
                time.time() - self.model_loaded_at
                if self.model_loaded_at
                else 0
            ),
        }


# Create the service instance
service = ModelService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_path = os.getenv("MODEL_PATH", "models/trained_model.pkl")
    model_version = os.getenv("MODEL_VERSION", "1.0.0")
    service.load(model_path, model_version)
    yield


app = FastAPI(
    title="Model Serving Service",
    lifespan=lifespan,
)


class Features(BaseModel):
    values: list[float]


@app.post("/predict")
def predict(features: Features):
    start = time.time()
    result = service.predict(features.values)
    result["latency_ms"] = round((time.time() - start) * 1000, 2)
    return result


@app.get("/info")
def model_info():
    return service.get_info()


@app.get("/health")
def health():
    info = service.get_info()
    return {
        "status": "healthy" if info["loaded"] else "unhealthy",
        "model_loaded": info["loaded"],
    }
```

---

## Scaling Considerations

```
+--------------------------------------------------+
|  Scaling Decision Tree                            |
|                                                   |
|  How many requests per second?                   |
|       |                                           |
|       +-- < 10 RPS   -> Single server, 1 worker  |
|       |                                           |
|       +-- 10-100 RPS -> Single server, 4 workers |
|       |                                           |
|       +-- 100-1000   -> Multiple servers          |
|       |                  + load balancer           |
|       |                                           |
|       +-- > 1000 RPS -> Specialized serving       |
|                          (TF Serving, Triton)     |
+--------------------------------------------------+
```

### Memory Considerations

```python
"""
memory_check.py - Check model memory usage.

Before scaling, know how much memory your model needs.
Each worker loads a separate copy of the model.
"""

import joblib
import sys
import os


def get_model_memory(model_path):
    """
    Estimate how much memory a model uses.

    Parameters
    ----------
    model_path : str
        Path to the model file.

    Returns
    -------
    dict
        Memory usage information.
    """
    # File size on disk
    file_size = os.path.getsize(model_path)

    # Load model and check memory
    model = joblib.load(model_path)
    # sys.getsizeof gives a rough estimate
    # The actual memory usage is usually higher
    memory_estimate = sys.getsizeof(model)

    # Rule of thumb: in-memory size is roughly
    # 1.5x to 3x the file size for sklearn models
    estimated_memory = file_size * 2

    return {
        "file_size_mb": file_size / (1024 * 1024),
        "estimated_memory_mb": estimated_memory / (1024 * 1024),
    }


info = get_model_memory("models/trained_model.pkl")
print(f"File size: {info['file_size_mb']:.1f} MB")
print(f"Estimated memory: {info['estimated_memory_mb']:.1f} MB")

# Planning for scaling
workers = 4
instances = 3
total_model_copies = workers * instances
total_memory = info["estimated_memory_mb"] * total_model_copies

print(f"\nScaling plan:")
print(f"  Workers per instance: {workers}")
print(f"  Number of instances: {instances}")
print(f"  Total model copies: {total_model_copies}")
print(f"  Total memory for models: {total_memory:.0f} MB")
```

```
Output:
File size: 12.5 MB
Estimated memory: 25.0 MB

Scaling plan:
  Workers per instance: 4
  Number of instances: 3
  Total model copies: 12
  Total memory for models: 300 MB
```

---

## Caching Predictions

Caching means storing predictions so you do not have to compute them again. If someone asks for the same prediction twice, why run the model twice?

```
+--------------------------------------------------+
|  Without Cache                                    |
|                                                   |
|  Request 1: age=30, income=50k -> Run model -> 5ms|
|  Request 2: age=30, income=50k -> Run model -> 5ms|
|  Request 3: age=30, income=50k -> Run model -> 5ms|
|  (Same inputs, computed 3 times!)                |
|                                                   |
|  With Cache                                      |
|                                                   |
|  Request 1: age=30, income=50k -> Run model -> 5ms|
|  Request 2: age=30, income=50k -> From cache -> 0.1ms|
|  Request 3: age=30, income=50k -> From cache -> 0.1ms|
|  (Computed once, served from memory!)            |
+--------------------------------------------------+
```

### Simple In-Memory Cache

```python
"""
prediction_cache.py - Cache predictions for speed.

An in-memory cache stores recent predictions so
identical requests get instant responses.
"""

from collections import OrderedDict
import hashlib
import json
import time
import logging

logger = logging.getLogger(__name__)


class PredictionCache:
    """
    A simple LRU (Least Recently Used) cache for predictions.

    LRU means when the cache is full, the oldest unused
    item gets removed to make room for new ones.

    Think of it like a small shelf that holds your most
    recently used books. When the shelf is full and you
    get a new book, you remove the one you have not
    touched in the longest time.
    """

    def __init__(self, max_size=10000, ttl_seconds=3600):
        """
        Initialize the cache.

        Parameters
        ----------
        max_size : int
            Maximum number of predictions to cache.
        ttl_seconds : int
            Time To Live - how long a cached prediction
            stays valid (in seconds). After this time,
            the prediction is recomputed.
        """
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.hits = 0    # Times we found the answer in cache
        self.misses = 0  # Times we had to compute

    def _make_key(self, features):
        """
        Create a unique key from the input features.

        We convert the features to a string and hash it.
        This creates a short, unique identifier for any
        set of input features.
        """
        feature_str = json.dumps(features, sort_keys=True)
        return hashlib.md5(feature_str.encode()).hexdigest()

    def get(self, features):
        """
        Try to get a cached prediction.

        Returns None if not found or expired.
        """
        key = self._make_key(features)

        if key in self.cache:
            entry = self.cache[key]
            age = time.time() - entry["timestamp"]

            # Check if the cached entry has expired
            if age < self.ttl_seconds:
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                self.hits += 1
                logger.debug(f"Cache HIT (age: {age:.1f}s)")
                return entry["prediction"]
            else:
                # Expired, remove it
                del self.cache[key]
                logger.debug(f"Cache EXPIRED (age: {age:.1f}s)")

        self.misses += 1
        logger.debug("Cache MISS")
        return None

    def put(self, features, prediction):
        """Store a prediction in the cache."""
        key = self._make_key(features)

        # Remove oldest if cache is full
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)

        self.cache[key] = {
            "prediction": prediction,
            "timestamp": time.time(),
        }

    def get_stats(self):
        """Get cache performance statistics."""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1%}",
        }


# Usage example
cache = PredictionCache(max_size=1000, ttl_seconds=3600)

# First request: cache miss, must compute
features1 = [30, 50000, 720, 5]
result = cache.get(features1)
print(f"First lookup: {result}")  # None (not cached yet)

# Store the prediction
cache.put(features1, {"prediction": 0, "probability": 0.15})

# Second request: cache hit!
result = cache.get(features1)
print(f"Second lookup: {result}")  # The cached prediction

# Different features: cache miss
features2 = [45, 80000, 780, 15]
result = cache.get(features2)
print(f"Different features: {result}")  # None

# Check statistics
print(f"\nCache stats: {cache.get_stats()}")
```

```
Output:
First lookup: None
Second lookup: {'prediction': 0, 'probability': 0.15}
Different features: None

Cache stats: {'size': 1, 'max_size': 1000, 'hits': 1, 'misses': 2, 'hit_rate': '33.3%'}
```

### Integrating Cache with the API

```python
"""
cached_api.py - ML API with prediction caching.

This combines the FastAPI server with the prediction
cache for maximum performance.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
import joblib
import numpy as np
import time

# Import our cache (from the previous example)
# In practice, this would be in a separate file
from prediction_cache import PredictionCache

model = None
cache = PredictionCache(max_size=10000, ttl_seconds=3600)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    model = joblib.load("models/trained_model.pkl")
    yield
    model = None


app = FastAPI(title="Cached ML API", lifespan=lifespan)


class PredictRequest(BaseModel):
    features: list[float]


@app.post("/predict")
def predict(request: PredictRequest):
    start = time.time()

    # Check cache first
    cached = cache.get(request.features)
    if cached is not None:
        cached["from_cache"] = True
        cached["latency_ms"] = round(
            (time.time() - start) * 1000, 2
        )
        return cached

    # Cache miss: compute prediction
    features = np.array([request.features])
    prediction = int(model.predict(features)[0])

    try:
        probability = float(
            model.predict_proba(features)[0][1]
        )
    except AttributeError:
        probability = float(prediction)

    result = {
        "prediction": prediction,
        "probability": round(probability, 4),
        "from_cache": False,
        "latency_ms": round((time.time() - start) * 1000, 2),
    }

    # Store in cache for next time
    cache.put(request.features, result)

    return result


@app.get("/cache/stats")
def cache_stats():
    """View cache performance statistics."""
    return cache.get_stats()
```

---

## Common Mistakes

1. **Using batch inference when real-time is needed.** If users are waiting for a response, you need real-time serving, not batch.

2. **Caching without expiration.** Cached predictions become stale when you update your model. Always set a TTL (time to live).

3. **Not considering memory when scaling.** Each worker loads a copy of the model. Four workers with a 500MB model need 2GB of RAM just for models.

4. **Over-engineering for low traffic.** If you get 10 requests per day, a simple single-server setup is fine. Do not build for millions of users until you have them.

5. **Ignoring cold start time.** The first prediction after loading a model is often slower because of initialization. Warm up your model with a dummy prediction at startup.

---

## Best Practices

1. **Choose the right serving pattern for your use case.** Batch for scheduled bulk processing, real-time for user-facing applications.

2. **Cache predictions for repeated inputs.** This can reduce latency from milliseconds to microseconds.

3. **Monitor cache hit rates.** A low hit rate means caching is not helping. A high hit rate means you are saving significant compute.

4. **Warm up your model at startup.** Make a dummy prediction during startup to avoid slow first requests.

5. **Use health checks to verify model is loaded.** The API should report "unhealthy" if the model fails to load.

---

## Quick Summary

Model serving is about getting predictions from your model to users. Batch inference processes many items at once and is efficient for bulk operations. Real-time inference handles individual requests instantly. Caching stores repeated predictions for faster responses. Choose your pattern based on your latency requirements and traffic volume.

---

## Key Points

- Batch inference processes data in bulk; real-time serves individual requests
- The "Model as a Service" pattern lets multiple apps share one model
- Each worker loads a separate copy of the model (plan memory accordingly)
- Caching can reduce latency from milliseconds to microseconds
- Always set a TTL on cached predictions
- Warm up models at startup to avoid slow first requests

---

## Practice Questions

1. When would you choose batch inference over real-time inference? Give two specific examples.

2. What is an LRU cache and why is it useful for model serving?

3. If your model file is 200MB and you run 4 workers on 3 instances, how much total memory do you need just for the models?

4. What is the "Model as a Service" pattern and what are its advantages?

5. Why should you warm up your model at startup?

---

## Exercises

### Exercise 1: Batch Pipeline

Write a batch inference script that:
- Loads a model
- Reads a CSV file with 10,000 rows
- Processes it in batches of 500
- Logs progress and timing for each batch
- Saves results to a new CSV

### Exercise 2: Cache Comparison

Implement two versions of an ML API:
- One without caching
- One with caching (TTL = 60 seconds)

Send 1000 requests (50% duplicates) to each and compare average latency.

### Exercise 3: Serving Pattern Design

Design a model serving architecture for a ride-sharing app that needs:
- Real-time price prediction (must respond in under 50ms)
- Batch driver matching (run every 30 seconds)
- A/B testing between two pricing models

Draw the architecture and explain your choices.

---

## What Is Next?

We have covered how to build, deploy, and serve ML models. But the journey does not end at deployment. In Chapter 8, we will zoom out and look at the complete ML lifecycle, from data collection to model monitoring and retraining. Understanding this full picture is essential for building ML systems that stay healthy over time.
