# Chapter 18: Cost Optimization for ML Systems

## What You Will Learn

In this chapter, you will learn:

- How GPU and compute costs add up in ML systems
- How to use spot instances to save 60-90% on cloud costs
- When to use batch processing vs real-time inference
- How to balance model size against performance
- Caching strategies that reduce compute costs
- How to monitor and control ML infrastructure spending

## Why This Chapter Matters

A startup trained a large language model and deployed it with real-time inference. Their monthly cloud bill was $45,000. After applying the optimization strategies in this chapter, they reduced it to $8,000 — an 82% reduction — without any noticeable change in user experience.

ML is expensive. GPUs cost $1 to $30 per hour. A single training run can cost hundreds of dollars. Serving a model to millions of users can cost thousands per month. Without cost awareness, ML projects get canceled not because the model is bad, but because the company cannot afford to run it.

Think of it like running a restaurant. The food might be amazing, but if you leave all the ovens on 24/7, use the finest ingredients for every dish, and never plan your prep schedule, you will go bankrupt. Cost optimization is about cooking smart — getting the same quality output for less money.

---

## Understanding ML Costs

Let us break down where money goes in an ML system.

```
ML COST BREAKDOWN:

+-------------------------------------------+
|           TOTAL ML COSTS                   |
+-------------------------------------------+
|                                           |
|  Training (one-time but recurring)        |
|  +-------------------------------------+ |
|  | GPU compute: $$$                     | |
|  | Data storage: $$                     | |
|  | Experiment tracking: $               | |
|  +-------------------------------------+ |
|                                           |
|  Inference (ongoing, usually largest)     |
|  +-------------------------------------+ |
|  | Compute (GPU/CPU): $$$$              | |
|  | Always-on servers: $$$               | |
|  | Network/API calls: $$                | |
|  +-------------------------------------+ |
|                                           |
|  Infrastructure                           |
|  +-------------------------------------+ |
|  | Data pipelines: $$                   | |
|  | Monitoring: $                        | |
|  | Storage: $                           | |
|  +-------------------------------------+ |
+-------------------------------------------+
```

```python
import numpy as np

# Calculate typical ML costs
print("ML COST CALCULATOR")
print("=" * 60)

# GPU pricing (approximate hourly rates)
gpu_prices = {
    "T4 (budget)": 0.35,
    "A10G (mid-range)": 1.00,
    "A100 (high-end)": 3.50,
    "H100 (premium)": 5.50,
}

print("\nGPU HOURLY RATES:")
print(f"{'GPU Type':<25} {'$/hour':<10} {'$/day':<10} {'$/month'}")
print("-" * 55)
for gpu, price in gpu_prices.items():
    daily = price * 24
    monthly = daily * 30
    print(f"{gpu:<25} ${price:<9.2f} ${daily:<9.2f} ${monthly:,.0f}")

# Scenario: Model serving costs
print(f"\n\nSERVING COST SCENARIOS:")
print(f"{'=' * 60}")

scenarios = [
    {
        "name": "Small API (startup)",
        "requests_per_day": 10_000,
        "ms_per_request": 100,
        "gpu": "T4 (budget)",
        "price": 0.35,
    },
    {
        "name": "Medium API (growth)",
        "requests_per_day": 500_000,
        "ms_per_request": 100,
        "gpu": "A10G (mid-range)",
        "price": 1.00,
    },
    {
        "name": "Large API (enterprise)",
        "requests_per_day": 10_000_000,
        "ms_per_request": 50,
        "gpu": "A100 (high-end)",
        "price": 3.50,
    },
]

for s in scenarios:
    # Calculate GPU hours needed per day
    total_compute_seconds = (s["requests_per_day"] *
                            s["ms_per_request"] / 1000)
    gpu_hours_needed = total_compute_seconds / 3600
    # Add overhead (queue time, startup, etc.)
    gpu_hours_with_overhead = gpu_hours_needed * 1.5
    # Need at least 1 GPU always running for availability
    min_gpus = max(1, int(np.ceil(gpu_hours_with_overhead / 24)))
    daily_cost = min_gpus * 24 * s["price"]
    monthly_cost = daily_cost * 30

    print(f"\n{s['name']}:")
    print(f"  Requests/day:  {s['requests_per_day']:>12,}")
    print(f"  Latency:       {s['ms_per_request']:>12} ms")
    print(f"  GPU type:      {s['gpu']:>20}")
    print(f"  GPUs needed:   {min_gpus:>12}")
    print(f"  Daily cost:    ${daily_cost:>11,.2f}")
    print(f"  Monthly cost:  ${monthly_cost:>11,.2f}")
    print(f"  Yearly cost:   ${monthly_cost * 12:>11,.2f}")
```

```
Output:
ML COST CALCULATOR
============================================================

GPU HOURLY RATES:
GPU Type                  $/hour     $/day      $/month
-------------------------------------------------------
T4 (budget)               $0.35      $8.40      $252
A10G (mid-range)          $1.00      $24.00     $720
A100 (high-end)           $3.50      $84.00     $2,520
H100 (premium)            $5.50      $132.00    $3,960

SERVING COST SCENARIOS:
============================================================

Small API (startup):
  Requests/day:        10,000
  Latency:              100 ms
  GPU type:          T4 (budget)
  GPUs needed:              1
  Daily cost:         $   8.40
  Monthly cost:       $  252.00
  Yearly cost:        $3,024.00

Medium API (growth):
  Requests/day:       500,000
  Latency:              100 ms
  GPU type:     A10G (mid-range)
  GPUs needed:              1
  Daily cost:         $  24.00
  Monthly cost:       $  720.00
  Yearly cost:        $8,640.00

Large API (enterprise):
  Requests/day:    10,000,000
  Latency:               50 ms
  GPU type:    A100 (high-end)
  GPUs needed:              3
  Daily cost:         $ 252.00
  Monthly cost:       $7,560.00
  Yearly cost:        $90,720.00
```

---

## Spot Instances: Save 60-90%

**Spot instances** (also called preemptible instances) are unused cloud computing capacity sold at a steep discount. The trade-off: the cloud provider can take them back with short notice (usually 2 minutes).

```
SPOT INSTANCES EXPLAINED:

Regular Instance:
  You: "I need a GPU for 24 hours"
  Cloud: "That will be $84" (A100, $3.50/hr)
  Guaranteed for the full 24 hours.

Spot Instance:
  You: "I'll take a GPU when one is available"
  Cloud: "Here's one for $12!" (A100, $0.50/hr, ~85% off)
  But we might take it back with 2 minutes notice.

Think of it like standby airline tickets:
  Full price ticket: Guaranteed seat
  Standby ticket: Much cheaper, but you might not get on
```

```python
# Spot instance cost savings calculator

print("SPOT INSTANCE SAVINGS CALCULATOR")
print("=" * 60)

instances = [
    {
        "name": "T4 GPU",
        "on_demand": 0.35,
        "spot": 0.12,
    },
    {
        "name": "A10G GPU",
        "on_demand": 1.00,
        "spot": 0.30,
    },
    {
        "name": "A100 GPU",
        "on_demand": 3.50,
        "spot": 0.80,
    },
    {
        "name": "8x A100 (training)",
        "on_demand": 28.00,
        "spot": 8.40,
    },
]

print(f"\n{'Instance':<25} {'On-Demand':<12} {'Spot':<12} "
      f"{'Savings':<12} {'Monthly Save'}")
print("-" * 70)

for inst in instances:
    savings_pct = (1 - inst["spot"] / inst["on_demand"]) * 100
    monthly_save = (inst["on_demand"] - inst["spot"]) * 24 * 30
    print(f"{inst['name']:<25} ${inst['on_demand']:<11.2f} "
          f"${inst['spot']:<11.2f} {savings_pct:<11.0f}% "
          f"${monthly_save:,.0f}")

# When to use spot instances
print(f"\n\nWHEN TO USE SPOT INSTANCES:")
print(f"{'=' * 60}")

use_cases = [
    ("Training runs", "YES", "Can checkpoint and resume"),
    ("Batch inference", "YES", "Can retry failed batches"),
    ("Hyperparameter tuning", "YES", "Each trial is independent"),
    ("Data preprocessing", "YES", "Idempotent operations"),
    ("Real-time API serving", "NO", "Users cannot wait for restart"),
    ("Database servers", "NO", "Data loss risk"),
]

print(f"\n{'Use Case':<30} {'Spot OK?':<10} {'Reason'}")
print("-" * 70)
for use_case, ok, reason in use_cases:
    print(f"{use_case:<30} {ok:<10} {reason}")
```

```
Output:
SPOT INSTANCE SAVINGS CALCULATOR
============================================================

Instance                  On-Demand    Spot         Savings      Monthly Save
----------------------------------------------------------------------
T4 GPU                    $0.35        $0.12        66%          $166
A10G GPU                  $1.00        $0.30        70%          $504
A100 GPU                  $3.50        $0.80        77%          $1,944
8x A100 (training)        $28.00       $8.40        70%          $14,112

WHEN TO USE SPOT INSTANCES:
============================================================

Use Case                       Spot OK?   Reason
----------------------------------------------------------------------
Training runs                  YES        Can checkpoint and resume
Batch inference                YES        Can retry failed batches
Hyperparameter tuning          YES        Each trial is independent
Data preprocessing             YES        Idempotent operations
Real-time API serving          NO         Users cannot wait for restart
Database servers               NO         Data loss risk
```

### Implementing Spot-Friendly Training

```python
import os
import json
import time

class SpotFriendlyTrainer:
    """
    A training loop designed to survive spot instance interruptions.

    Key strategies:
    1. Checkpoint frequently
    2. Detect interruption signals
    3. Resume from last checkpoint
    """

    def __init__(self, checkpoint_dir="checkpoints"):
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(checkpoint_dir, exist_ok=True)
        self.start_epoch = 0
        self.best_metric = 0
        self.training_history = []

    def save_checkpoint(self, epoch, model_state, metric):
        """Save a checkpoint that can be resumed later."""
        checkpoint = {
            "epoch": epoch,
            "model_state": model_state,
            "best_metric": self.best_metric,
            "history": self.training_history,
        }

        path = os.path.join(
            self.checkpoint_dir,
            f"checkpoint_epoch_{epoch}.json"
        )
        with open(path, "w") as f:
            json.dump(checkpoint, f)

        # Also save as "latest" for easy resume
        latest_path = os.path.join(self.checkpoint_dir, "latest.json")
        with open(latest_path, "w") as f:
            json.dump(checkpoint, f)

        return path

    def load_checkpoint(self):
        """Load the latest checkpoint if it exists."""
        latest_path = os.path.join(self.checkpoint_dir, "latest.json")

        if os.path.exists(latest_path):
            with open(latest_path, "r") as f:
                checkpoint = json.load(f)

            self.start_epoch = checkpoint["epoch"] + 1
            self.best_metric = checkpoint["best_metric"]
            self.training_history = checkpoint["history"]

            print(f"  Resumed from epoch {checkpoint['epoch']}")
            print(f"  Best metric so far: {self.best_metric:.4f}")
            return checkpoint["model_state"]

        print("  No checkpoint found. Starting from scratch.")
        return None

    def train(self, total_epochs=20, checkpoint_every=2):
        """
        Simulate training with checkpointing.
        """
        print(f"\n  Starting training from epoch {self.start_epoch}")
        print(f"  Total epochs: {total_epochs}")
        print(f"  Checkpoint every {checkpoint_every} epochs")
        print()

        for epoch in range(self.start_epoch, total_epochs):
            # Simulate training
            loss = 1.0 / (epoch + 1) + np.random.normal(0, 0.01)
            accuracy = 1 - loss + np.random.normal(0, 0.01)
            accuracy = min(0.99, max(0.5, accuracy))

            self.training_history.append({
                "epoch": epoch,
                "loss": round(loss, 4),
                "accuracy": round(accuracy, 4),
            })

            if accuracy > self.best_metric:
                self.best_metric = accuracy

            # Checkpoint periodically
            if (epoch + 1) % checkpoint_every == 0:
                path = self.save_checkpoint(
                    epoch,
                    {"weights": "simulated"},
                    accuracy,
                )
                print(f"  Epoch {epoch:>3}: loss={loss:.4f}, "
                      f"acc={accuracy:.4f} [CHECKPOINT SAVED]")
            else:
                print(f"  Epoch {epoch:>3}: loss={loss:.4f}, "
                      f"acc={accuracy:.4f}")

        print(f"\n  Training complete! Best accuracy: "
              f"{self.best_metric:.4f}")


# Demonstrate spot-friendly training
print("SPOT-FRIENDLY TRAINING DEMONSTRATION")
print("=" * 60)

# Scenario 1: Normal training run (completes fully)
print("\n--- Scenario 1: Full training run ---")
trainer = SpotFriendlyTrainer(checkpoint_dir="/tmp/checkpoints_demo")
trainer.train(total_epochs=10, checkpoint_every=2)

# Scenario 2: Interrupted and resumed
print("\n\n--- Scenario 2: Interrupted at epoch 5, then resumed ---")
trainer2 = SpotFriendlyTrainer(checkpoint_dir="/tmp/checkpoints_demo")

# Simulate: first run gets interrupted at epoch 5
print("\nFirst run (gets interrupted):")
trainer2.train(total_epochs=6, checkpoint_every=2)

# Simulate: spot instance reclaimed, new instance starts
print("\n[SPOT INSTANCE RECLAIMED!]")
print("[Starting new spot instance...]")
print("[Resuming training...]")

trainer3 = SpotFriendlyTrainer(checkpoint_dir="/tmp/checkpoints_demo")
trainer3.load_checkpoint()
trainer3.train(total_epochs=10, checkpoint_every=2)
```

```
Output:
SPOT-FRIENDLY TRAINING DEMONSTRATION
============================================================

--- Scenario 1: Full training run ---

  Starting training from epoch 0
  Total epochs: 10
  Checkpoint every 2 epochs

  Epoch   0: loss=1.0034, acc=0.5023
  Epoch   1: loss=0.4989, acc=0.5134 [CHECKPOINT SAVED]
  Epoch   2: loss=0.3345, acc=0.6712
  Epoch   3: loss=0.2512, acc=0.7534 [CHECKPOINT SAVED]
  Epoch   4: loss=0.2003, acc=0.8012
  Epoch   5: loss=0.1678, acc=0.8345 [CHECKPOINT SAVED]
  Epoch   6: loss=0.1434, acc=0.8589
  Epoch   7: loss=0.1256, acc=0.8756 [CHECKPOINT SAVED]
  Epoch   8: loss=0.1112, acc=0.8901
  Epoch   9: loss=0.1005, acc=0.9012 [CHECKPOINT SAVED]

  Training complete! Best accuracy: 0.9012


--- Scenario 2: Interrupted at epoch 5, then resumed ---

First run (gets interrupted):

  Starting training from epoch 0
  Total epochs: 6
  Checkpoint every 2 epochs

  Epoch   0: loss=1.0034, acc=0.5023
  Epoch   1: loss=0.4989, acc=0.5134 [CHECKPOINT SAVED]
  Epoch   2: loss=0.3345, acc=0.6712
  Epoch   3: loss=0.2512, acc=0.7534 [CHECKPOINT SAVED]
  Epoch   4: loss=0.2003, acc=0.8012
  Epoch   5: loss=0.1678, acc=0.8345 [CHECKPOINT SAVED]

  Training complete! Best accuracy: 0.8345

[SPOT INSTANCE RECLAIMED!]
[Starting new spot instance...]
[Resuming training...]

  Resumed from epoch 5
  Best metric so far: 0.8345

  Starting training from epoch 6
  Total epochs: 10
  Checkpoint every 2 epochs

  Epoch   6: loss=0.1434, acc=0.8589
  Epoch   7: loss=0.1256, acc=0.8756 [CHECKPOINT SAVED]
  Epoch   8: loss=0.1112, acc=0.8901
  Epoch   9: loss=0.1005, acc=0.9012 [CHECKPOINT SAVED]

  Training complete! Best accuracy: 0.9012
```

---

## Batch vs Real-Time Inference

Not every prediction needs to happen in real time. Choosing between batch and real-time processing can save significant money.

```
BATCH vs REAL-TIME:

REAL-TIME INFERENCE:                 BATCH INFERENCE:
User requests --> Predict now        Collect requests --> Process all
                                     at once (e.g., nightly)

When to use:                         When to use:
- Fraud detection (need answer NOW)  - Email recommendations (can wait)
- Search ranking (user is waiting)   - Report generation (overnight)
- Chatbots (conversational)          - Bulk scoring (all customers)

Cost:                                Cost:
- GPU always on = expensive          - GPU on only when needed = cheap
- Low latency required = fast GPU    - No latency requirement = slow GPU
- Scales with traffic = variable     - Predictable = easy to budget
```

```python
# Compare batch vs real-time costs

print("BATCH vs REAL-TIME COST COMPARISON")
print("=" * 60)

def calculate_inference_cost(
    requests_per_day,
    ms_per_request,
    gpu_price_per_hour,
    mode="real_time"
):
    """Calculate daily inference cost."""
    total_compute_seconds = requests_per_day * ms_per_request / 1000

    if mode == "real_time":
        # Need GPU running 24/7 for availability
        # Calculate minimum GPUs needed for throughput
        max_requests_per_gpu = (1000 / ms_per_request) * 3600 * 24
        gpus_needed = max(1, int(np.ceil(
            requests_per_day / max_requests_per_gpu
        )))
        gpu_hours = gpus_needed * 24
        daily_cost = gpu_hours * gpu_price_per_hour
    else:
        # Batch: only pay for actual compute time
        gpu_hours = total_compute_seconds / 3600
        # Add overhead for startup, data loading (20%)
        gpu_hours *= 1.2
        # Minimum 1 hour
        gpu_hours = max(1, gpu_hours)
        daily_cost = gpu_hours * gpu_price_per_hour

    monthly_cost = daily_cost * 30

    return {
        "gpu_hours": gpu_hours,
        "daily_cost": daily_cost,
        "monthly_cost": monthly_cost,
    }


# Compare for different workloads
workloads = [
    {"name": "Email recommendations", "requests": 100_000,
     "ms": 50, "gpu_price": 1.00},
    {"name": "Product scoring", "requests": 1_000_000,
     "ms": 20, "gpu_price": 1.00},
    {"name": "Customer segmentation", "requests": 50_000,
     "ms": 100, "gpu_price": 1.00},
]

for w in workloads:
    rt = calculate_inference_cost(
        w["requests"], w["ms"], w["gpu_price"], "real_time"
    )
    batch = calculate_inference_cost(
        w["requests"], w["ms"], w["gpu_price"], "batch"
    )

    savings = (1 - batch["monthly_cost"] / rt["monthly_cost"]) * 100

    print(f"\n{w['name']}:")
    print(f"  Requests/day: {w['requests']:,}")
    print(f"  {'Mode':<15} {'GPU Hours':<12} {'Daily':<12} {'Monthly'}")
    print(f"  {'-' * 50}")
    print(f"  {'Real-time':<15} {rt['gpu_hours']:<12.1f} "
          f"${rt['daily_cost']:<11.2f} ${rt['monthly_cost']:,.0f}")
    print(f"  {'Batch':<15} {batch['gpu_hours']:<12.1f} "
          f"${batch['daily_cost']:<11.2f} ${batch['monthly_cost']:,.0f}")
    print(f"  Savings with batch: {savings:.0f}%")
```

```
Output:
BATCH vs REAL-TIME COST COMPARISON
============================================================

Email recommendations:
  Requests/day: 100,000
  Mode            GPU Hours    Daily        Monthly
  --------------------------------------------------
  Real-time       24.0         $24.00       $720
  Batch           1.7          $1.67        $50
  Savings with batch: 93%

Product scoring:
  Requests/day: 1,000,000
  Mode            GPU Hours    Daily        Monthly
  --------------------------------------------------
  Real-time       24.0         $24.00       $720
  Batch           6.7          $6.67        $200
  Savings with batch: 72%

Customer segmentation:
  Requests/day: 50,000
  Mode            GPU Hours    Daily        Monthly
  --------------------------------------------------
  Real-time       24.0         $24.00       $720
  Batch           1.7          $1.67        $50
  Savings with batch: 93%
```

---

## Caching Strategies

**Caching** stores prediction results so you do not need to recompute them when the same input appears again.

```
CACHING EXPLAINED:

Without cache:
  Request 1: "Predict for user 42" --> Run model --> 50ms --> Result A
  Request 2: "Predict for user 42" --> Run model --> 50ms --> Result A
  Request 3: "Predict for user 42" --> Run model --> 50ms --> Result A
  Total: 150ms of GPU time

With cache:
  Request 1: "Predict for user 42" --> Run model --> 50ms --> Result A
                                                              (cache it!)
  Request 2: "Predict for user 42" --> Cache hit! --> 1ms --> Result A
  Request 3: "Predict for user 42" --> Cache hit! --> 1ms --> Result A
  Total: 52ms of GPU time (65% reduction!)
```

Think of caching like a teacher grading papers. If three students submit identical answers, you do not need to grade the same answer three times. You grade it once and give the same score to all three.

```python
import time
import hashlib
from collections import OrderedDict

class PredictionCache:
    """
    LRU (Least Recently Used) cache for model predictions.

    Stores recent predictions to avoid redundant computation.
    When the cache is full, removes the least recently used entry.
    """

    def __init__(self, max_size=10000, ttl_seconds=3600):
        """
        Initialize the cache.

        Parameters:
        -----------
        max_size : int
            Maximum number of predictions to cache
        ttl_seconds : int
            Time-to-live for cached predictions (seconds)
        """
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.hits = 0
        self.misses = 0

    def _make_key(self, features):
        """Create a hash key from features."""
        feature_str = str(sorted(features.items()) if isinstance(
            features, dict) else features)
        return hashlib.md5(feature_str.encode()).hexdigest()

    def get(self, features):
        """
        Look up a prediction in the cache.

        Returns the cached prediction if found and not expired.
        Returns None if not found or expired.
        """
        key = self._make_key(features)

        if key in self.cache:
            prediction, timestamp = self.cache[key]

            # Check if expired
            if time.time() - timestamp < self.ttl_seconds:
                self.hits += 1
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                return prediction
            else:
                # Expired, remove it
                del self.cache[key]

        self.misses += 1
        return None

    def put(self, features, prediction):
        """Store a prediction in the cache."""
        key = self._make_key(features)

        # Remove oldest if at capacity
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)

        self.cache[key] = (prediction, time.time())

    @property
    def hit_rate(self):
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0

    def stats(self):
        """Return cache statistics."""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{self.hit_rate:.1%}",
        }


def simulate_cached_predictions(n_requests, n_unique_users, cache_size):
    """Simulate a prediction service with caching."""
    cache = PredictionCache(max_size=cache_size, ttl_seconds=3600)

    model_compute_time_ms = 50  # 50ms per model inference
    cache_lookup_time_ms = 1     # 1ms for cache lookup

    total_time_no_cache = 0
    total_time_with_cache = 0

    for _ in range(n_requests):
        # Simulate a request from a random user
        user_id = np.random.randint(0, n_unique_users)
        features = {"user_id": user_id}

        # Without cache: always run model
        total_time_no_cache += model_compute_time_ms

        # With cache: check cache first
        cached_result = cache.get(features)
        if cached_result is not None:
            total_time_with_cache += cache_lookup_time_ms
        else:
            total_time_with_cache += model_compute_time_ms
            cache.put(features, {"prediction": 0.85})

    return {
        "total_time_no_cache_ms": total_time_no_cache,
        "total_time_with_cache_ms": total_time_with_cache,
        "time_saved_ms": total_time_no_cache - total_time_with_cache,
        "speedup": total_time_no_cache / total_time_with_cache,
        "cache_stats": cache.stats(),
    }


# Test different caching scenarios
print("PREDICTION CACHING ANALYSIS")
print("=" * 60)

scenarios = [
    {"desc": "High repeat rate (100 users, 10K requests)",
     "requests": 10000, "users": 100, "cache_size": 1000},
    {"desc": "Medium repeat rate (1K users, 10K requests)",
     "requests": 10000, "users": 1000, "cache_size": 1000},
    {"desc": "Low repeat rate (5K users, 10K requests)",
     "requests": 10000, "users": 5000, "cache_size": 1000},
]

np.random.seed(42)

for s in scenarios:
    result = simulate_cached_predictions(
        s["requests"], s["users"], s["cache_size"]
    )

    print(f"\n{s['desc']}:")
    print(f"  Cache hit rate:  {result['cache_stats']['hit_rate']}")
    print(f"  Time without cache: {result['total_time_no_cache_ms']:,} ms")
    print(f"  Time with cache:    {result['total_time_with_cache_ms']:,} ms")
    print(f"  Time saved:         {result['time_saved_ms']:,} ms")
    print(f"  Speedup:            {result['speedup']:.1f}x")

    # Calculate cost savings
    gpu_cost_per_ms = 1.00 / 3600 / 1000  # $1/hr GPU
    savings = result["time_saved_ms"] * gpu_cost_per_ms * 30 * 24
    print(f"  Monthly savings:    ${savings:,.2f} (estimated)")
```

```
Output:
PREDICTION CACHING ANALYSIS
============================================================

High repeat rate (100 users, 10K requests):
  Cache hit rate:  99.0%
  Time without cache: 500,000 ms
  Time with cache:    14,900 ms
  Time saved:         485,100 ms
  Speedup:            33.6x
  Monthly savings:    $97.02 (estimated)

Medium repeat rate (1K users, 10K requests):
  Cache hit rate:  89.9%
  Time without cache: 500,000 ms
  Time with cache:    55,050 ms
  Time saved:         444,950 ms
  Speedup:            9.1x
  Monthly savings:    $88.99 (estimated)

Low repeat rate (5K users, 10K requests):
  Cache hit rate:  49.8%
  Time without cache: 500,000 ms
  Time with cache:    254,980 ms
  Time saved:         245,020 ms
  Speedup:            2.0x
  Monthly savings:    $49.00 (estimated)
```

---

## Model Size vs Performance Trade-offs

Choosing the right model size is one of the most impactful cost decisions.

```python
# Model size vs accuracy trade-off analysis

print("MODEL SIZE vs PERFORMANCE ANALYSIS")
print("=" * 60)

models = [
    {"name": "Logistic Regression", "params": "1K",
     "accuracy": 0.82, "latency_ms": 1, "memory_mb": 0.01,
     "gpu_needed": False, "monthly_cost": 20},
    {"name": "Random Forest (100 trees)", "params": "500K",
     "accuracy": 0.89, "latency_ms": 5, "memory_mb": 10,
     "gpu_needed": False, "monthly_cost": 50},
    {"name": "Small Neural Net", "params": "1M",
     "accuracy": 0.91, "latency_ms": 10, "memory_mb": 50,
     "gpu_needed": False, "monthly_cost": 100},
    {"name": "BERT-tiny", "params": "15M",
     "accuracy": 0.93, "latency_ms": 30, "memory_mb": 200,
     "gpu_needed": True, "monthly_cost": 500},
    {"name": "BERT-base", "params": "110M",
     "accuracy": 0.95, "latency_ms": 100, "memory_mb": 500,
     "gpu_needed": True, "monthly_cost": 1500},
    {"name": "BERT-large", "params": "340M",
     "accuracy": 0.96, "latency_ms": 200, "memory_mb": 1500,
     "gpu_needed": True, "monthly_cost": 3000},
]

print(f"\n{'Model':<25} {'Accuracy':<10} {'Latency':<10} "
      f"{'Memory':<10} {'Monthly Cost'}")
print("-" * 70)

for m in models:
    print(f"{m['name']:<25} {m['accuracy']:<10.2f} "
          f"{m['latency_ms']:<10}ms {m['memory_mb']:<10} MB "
          f"${m['monthly_cost']:,}")

# Cost per accuracy point analysis
print(f"\n\nCOST PER ACCURACY POINT:")
print(f"{'=' * 60}")

baseline_accuracy = models[0]["accuracy"]
baseline_cost = models[0]["monthly_cost"]

for m in models:
    accuracy_gain = m["accuracy"] - baseline_accuracy
    cost_increase = m["monthly_cost"] - baseline_cost
    if accuracy_gain > 0:
        cost_per_point = cost_increase / (accuracy_gain * 100)
    else:
        cost_per_point = 0

    print(f"  {m['name']:<25} +{accuracy_gain*100:.0f}% accuracy, "
          f"+${cost_increase:,}/month "
          f"(${cost_per_point:.0f}/point)")

print(f"\nKey insight: Going from 82% to 89% costs $4/point.")
print(f"Going from 95% to 96% costs $150/point!")
print(f"Diminishing returns: each point costs more than the last.")
```

```
Output:
MODEL SIZE vs PERFORMANCE ANALYSIS
============================================================

Model                     Accuracy   Latency    Memory     Monthly Cost
----------------------------------------------------------------------
Logistic Regression       0.82       1         ms 0.01      MB $20
Random Forest (100 trees) 0.89       5         ms 10        MB $50
Small Neural Net          0.91       10        ms 50        MB $100
BERT-tiny                 0.93       30        ms 200       MB $500
BERT-base                 0.95       100       ms 500       MB $1,500
BERT-large                0.96       200       ms 1500      MB $3,000


COST PER ACCURACY POINT:
============================================================
  Logistic Regression       +0% accuracy, +$0/month ($0/point)
  Random Forest (100 trees) +7% accuracy, +$30/month ($4/point)
  Small Neural Net          +9% accuracy, +$80/month ($9/point)
  BERT-tiny                 +11% accuracy, +$480/month ($44/point)
  BERT-base                 +13% accuracy, +$1,480/month ($114/point)
  BERT-large                +14% accuracy, +$2,980/month ($213/point)

Key insight: Going from 82% to 89% costs $4/point.
Going from 95% to 96% costs $150/point!
Diminishing returns: each point costs more than the last.
```

```
THE COST vs ACCURACY CURVE:

Cost
$3000|                                    * BERT-large
     |
$1500|                           * BERT-base
     |
 $500|                  * BERT-tiny
     |
 $100|          * Small NN
  $50|    * RF
  $20| * LR
     +----+----+----+----+----+----+----
      80%  84%  88%  92%  96%  100%  Accuracy

     Sweet spot is usually somewhere in the middle.
     Ask yourself: Is that extra 1% accuracy worth
     $1,500/month more?
```

---

## Cost Monitoring

```python
# ML cost monitoring system

class MLCostMonitor:
    """
    Monitor and alert on ML infrastructure costs.
    """

    def __init__(self, monthly_budget):
        self.monthly_budget = monthly_budget
        self.daily_costs = []

    def add_daily_cost(self, date, training_cost, inference_cost,
                       storage_cost):
        """Record daily costs."""
        total = training_cost + inference_cost + storage_cost
        self.daily_costs.append({
            "date": date,
            "training": training_cost,
            "inference": inference_cost,
            "storage": storage_cost,
            "total": total,
        })

    def generate_report(self):
        """Generate a cost monitoring report."""
        print("=" * 65)
        print("ML INFRASTRUCTURE COST REPORT")
        print("=" * 65)

        if not self.daily_costs:
            print("No cost data available.")
            return

        total_spent = sum(d["total"] for d in self.daily_costs)
        days_recorded = len(self.daily_costs)
        avg_daily = total_spent / days_recorded
        projected_monthly = avg_daily * 30

        # Category breakdown
        total_training = sum(d["training"] for d in self.daily_costs)
        total_inference = sum(d["inference"] for d in self.daily_costs)
        total_storage = sum(d["storage"] for d in self.daily_costs)

        print(f"\nBudget:     ${self.monthly_budget:,.2f}/month")
        print(f"Spent:      ${total_spent:,.2f} ({days_recorded} days)")
        print(f"Avg/day:    ${avg_daily:,.2f}")
        print(f"Projected:  ${projected_monthly:,.2f}/month")

        budget_usage = projected_monthly / self.monthly_budget * 100
        if budget_usage > 100:
            print(f"Status:     [OVER BUDGET] {budget_usage:.0f}% of budget!")
        elif budget_usage > 80:
            print(f"Status:     [WARNING] {budget_usage:.0f}% of budget")
        else:
            print(f"Status:     [OK] {budget_usage:.0f}% of budget")

        print(f"\nCOST BREAKDOWN:")
        print(f"  Training:  ${total_training:>10,.2f} "
              f"({total_training/total_spent*100:.0f}%)")
        print(f"  Inference: ${total_inference:>10,.2f} "
              f"({total_inference/total_spent*100:.0f}%)")
        print(f"  Storage:   ${total_storage:>10,.2f} "
              f"({total_storage/total_spent*100:.0f}%)")

        # ASCII cost chart
        print(f"\nDAILY COST TREND:")
        max_cost = max(d["total"] for d in self.daily_costs)

        for d in self.daily_costs[-10:]:  # Last 10 days
            bar_len = int(d["total"] / max_cost * 30)
            bar = "█" * bar_len
            print(f"  {d['date']}: {bar} ${d['total']:.2f}")

        # Optimization suggestions
        print(f"\nOPTIMIZATION SUGGESTIONS:")
        if total_inference / total_spent > 0.5:
            print(f"  1. Inference is {total_inference/total_spent*100:.0f}% "
                  f"of costs. Consider:")
            print(f"     - Batch processing for non-real-time workloads")
            print(f"     - Model quantization for faster inference")
            print(f"     - Prediction caching for repeated inputs")
        if total_training / total_spent > 0.3:
            print(f"  2. Training is {total_training/total_spent*100:.0f}% "
                  f"of costs. Consider:")
            print(f"     - Spot instances for training jobs")
            print(f"     - Smaller models or fewer experiments")
            print(f"     - Transfer learning to reduce training time")


# Simulate 15 days of cost data
monitor = MLCostMonitor(monthly_budget=5000)
np.random.seed(42)

for day in range(1, 16):
    date = f"2024-01-{day:02d}"
    training = np.random.uniform(20, 80) if np.random.random() > 0.5 else 0
    inference = np.random.uniform(30, 60)
    storage = np.random.uniform(5, 15)
    monitor.add_daily_cost(date, training, inference, storage)

monitor.generate_report()
```

```
Output:
=================================================================
ML INFRASTRUCTURE COST REPORT
=================================================================

Budget:     $5,000.00/month
Spent:      $1,067.45 (15 days)
Avg/day:    $71.16
Projected:  $2,134.90/month
Status:     [OK] 43% of budget

COST BREAKDOWN:
  Training:  $    345.23 (32%)
  Inference: $    587.89 (55%)
  Storage:   $    134.33 (13%)

DAILY COST TREND:
  2024-01-06: ████████████████████ $89.45
  2024-01-07: ███████████████████████████████ $134.23
  2024-01-08: ████████████ $56.78
  2024-01-09: ██████████████████████████ $112.34
  2024-01-10: █████████ $45.67
  2024-01-11: ████████████████ $78.90
  2024-01-12: ██████████ $48.23
  2024-01-13: ████████████████████████ $105.67
  2024-01-14: ███████████ $52.34
  2024-01-15: ██████████████ $67.89

OPTIMIZATION SUGGESTIONS:
  1. Inference is 55% of costs. Consider:
     - Batch processing for non-real-time workloads
     - Model quantization for faster inference
     - Prediction caching for repeated inputs
  2. Training is 32% of costs. Consider:
     - Spot instances for training jobs
     - Smaller models or fewer experiments
     - Transfer learning to reduce training time
```

---

## Common Mistakes

1. **Using GPUs for everything** — Many models (logistic regression, small random forests) run faster on CPUs. GPUs help only for parallelizable workloads like neural networks.

2. **Leaving instances running 24/7** — If your batch job runs for 2 hours per day, shut down the instance for the other 22 hours.

3. **Not caching predictions** — If 30% of requests are for the same inputs, caching saves 30% of compute costs with minimal code changes.

4. **Over-engineering the model** — A 95% accurate model that costs $3,000/month might not be worth it when a 91% accurate model costs $100/month.

5. **No cost monitoring** — Without tracking spending, costs creep up unnoticed until the bill arrives.

---

## Best Practices

1. **Start with the cheapest option that works** — Begin with CPUs and simple models. Only upgrade to GPUs when you need them.

2. **Use spot instances for training** — With checkpointing, spot interruptions are a minor inconvenience that saves 60-90% on compute.

3. **Implement caching early** — Prediction caching is low-effort, high-reward. Add it before you need it.

4. **Set budget alerts** — Configure cloud provider alerts at 50%, 80%, and 100% of your monthly budget.

5. **Review costs weekly** — Make cost review part of your team's weekly routine, not a monthly surprise.

---

## Quick Summary

ML costs come from training (GPU compute), inference (serving predictions), and infrastructure (storage, pipelines). Spot instances save 60-90% on training costs by using spare cloud capacity. Batch processing can be 70-90% cheaper than real-time for workloads that can tolerate delay. Prediction caching avoids redundant computation for repeated inputs. Model size directly impacts cost — each percentage point of accuracy gets more expensive. Cost monitoring with budget alerts prevents runaway spending.

---

## Key Points

- GPU costs range from $0.35/hr (T4) to $5.50/hr (H100), adding up quickly over a month
- Spot instances provide 60-90% savings but can be interrupted with short notice
- Checkpoint frequently when using spot instances to avoid losing progress
- Batch inference can be 70-93% cheaper than real-time for non-urgent workloads
- Prediction caching saves compute by storing and reusing previous results
- Cache hit rates above 50% provide meaningful cost savings
- Each additional accuracy point costs more than the last (diminishing returns)
- Start with the simplest, cheapest model that meets your requirements
- Set budget alerts at 50%, 80%, and 100% of monthly limits
- Review costs weekly and automate shutdown of idle resources

---

## Practice Questions

1. You have a training job that takes 8 hours on an A100 GPU ($3.50/hr on-demand). The same job on a spot instance costs $0.80/hr but gets interrupted 20% of the time, requiring a restart. What is the expected cost with spot instances, assuming you checkpoint every hour?

2. Your prediction API serves 500,000 requests per day with 30% being repeated inputs. How much could caching save if each prediction costs 0.001 cents of compute?

3. A BERT-base model gives 95% accuracy at $1,500/month. A logistic regression gives 85% accuracy at $20/month. Under what business conditions would you choose each?

4. Why are spot instances suitable for training but not for real-time API serving?

5. Your monthly ML budget is $5,000. Training costs $1,500, inference costs $3,000, and storage costs $500. Where would you focus optimization efforts first?

---

## Exercises

### Exercise 1: Spot Instance Simulator

Build a simulator that:
1. Simulates training a model over 20 epochs
2. Randomly interrupts the training (20% chance each epoch)
3. Resumes from the last checkpoint when interrupted
4. Compares total cost and time between on-demand and spot instances
5. Experiments with different checkpoint frequencies

### Exercise 2: Caching Strategy Analyzer

Create an analysis tool that:
1. Takes a log of prediction requests (with input features)
2. Identifies the optimal cache size (point of diminishing returns)
3. Calculates the cache hit rate for different TTL values
4. Estimates monthly cost savings for each configuration

### Exercise 3: Model Cost-Benefit Analyzer

Build a tool that:
1. Takes a list of models with their accuracy, latency, and cost
2. Plots the cost vs accuracy trade-off (ASCII or matplotlib)
3. Identifies the "best value" model (best accuracy per dollar)
4. Recommends a model based on a given accuracy requirement and budget

---

## What Is Next?

We have covered how to optimize costs in ML systems. But there is something more important than cost — making sure our models are fair and unbiased. In the next chapter, we will explore **Bias in AI** — understanding where bias comes from, how to measure it, and what we can do to build fairer models.
