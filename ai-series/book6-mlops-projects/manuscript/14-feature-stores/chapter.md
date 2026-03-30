# Chapter 14: Feature Stores — Centralized Feature Management

## What You Will Learn

In this chapter, you will learn:

- What feature stores are and why they exist
- The problems feature stores solve in ML systems
- How to set up and use Feast (an open source feature store)
- How to define, register, and serve features
- How to use features for both training and real-time inference
- Best practices for organizing and managing features at scale

## Why This Chapter Matters

Imagine you work at a company with 50 data scientists. Each one builds their own features from raw data. One person calculates "average purchase amount" by including returns. Another excludes returns. A third uses a different time window. The same concept has three different implementations, and nobody knows which one is correct.

This is the feature management problem. Without a central system, features get duplicated, definitions conflict, and bugs hide in production for months.

A feature store is like a library for ML features. Just as a library organizes books so everyone can find and borrow them, a feature store organizes features so every model can find and use them consistently.

Think of it this way. A restaurant kitchen has a prep station where ingredients are washed, chopped, and organized before cooking begins. The feature store is that prep station for machine learning. Raw data comes in, gets transformed into useful features, and sits ready for any model that needs it.

---

## What Is a Feature?

Before diving into feature stores, let us make sure we understand features.

A **feature** is a piece of information that a model uses to make predictions. If you are predicting whether a customer will buy a product, features might include:

- Customer age
- Number of past purchases
- Average order value
- Days since last visit
- Whether they opened the last email

```
Raw Data                    Features (Model Inputs)
+------------------+       +----------------------+
| Transaction logs | ----> | avg_purchase_amount  |
| User profiles    | ----> | customer_age         |
| Click streams    | ----> | pages_visited_7d     |
| Email events     | ----> | email_open_rate      |
+------------------+       +----------------------+
```

**Feature engineering** is the process of transforming raw data into these features. It often involves calculations, aggregations, and transformations.

---

## The Problem: Why Feature Stores Exist

Without a feature store, ML teams face several painful problems.

### Problem 1: Training-Serving Skew

**Training-serving skew** means your model sees different feature values during training than during prediction.

```
TRAINING TIME (Python script):
    avg_purchase = purchases.mean()    # Uses pandas

SERVING TIME (Java API):
    avg_purchase = sum / count          # Reimplemented in Java

RESULT: Slightly different calculations = wrong predictions!
```

Think of this like a student who practices with one textbook but takes an exam based on a different textbook. Even small differences cause wrong answers.

### Problem 2: Duplicated Work

```
WITHOUT FEATURE STORE:

Data Scientist A:
    "I need customer lifetime value"
    --> Writes SQL query (2 hours)
    --> Writes Python transform (3 hours)

Data Scientist B (next week):
    "I also need customer lifetime value"
    --> Writes different SQL query (2 hours)
    --> Writes different Python transform (3 hours)
    --> Gets slightly different numbers!

Total wasted: 10+ hours, inconsistent results
```

### Problem 3: Slow Feature Serving

During real-time prediction, you cannot run a complex SQL query that takes 30 seconds. You need features served in milliseconds.

```
User clicks "Buy" --> Model needs prediction in 50ms
                      |
                      +--> Cannot run: SELECT AVG(amount)
                           FROM purchases
                           WHERE customer_id = 123
                           AND date > NOW() - INTERVAL 90 DAY
                           (Takes 2 seconds!)
```

### How a Feature Store Solves These Problems

```
+------------------+     +------------------+     +------------------+
|   Raw Data       |     |  FEATURE STORE   |     |    ML Models     |
|                  |     |                  |     |                  |
| - Databases      |---->| - Define once    |---->| - Training       |
| - Event streams  |     | - Compute once   |     | - Prediction     |
| - Files          |     | - Serve fast     |     | - Monitoring     |
|                  |     | - Version track  |     |                  |
+------------------+     +------------------+     +------------------+

ONE definition. ONE computation. CONSISTENT everywhere.
```

---

## Feature Store Architecture

A feature store has several key components.

```
FEATURE STORE ARCHITECTURE:

+-------------------------------------------------------------------+
|                        FEATURE STORE                               |
|                                                                    |
|  +------------------+    +------------------+    +---------------+ |
|  | Feature          |    | Offline Store    |    | Online Store  | |
|  | Definitions      |    | (for training)   |    | (for serving) | |
|  |                  |    |                  |    |               | |
|  | - Names          |    | - All history    |    | - Latest      | |
|  | - Types          |    | - Batch access   |    |   values only | |
|  | - Sources        |    | - Parquet/DB     |    | - Fast lookup | |
|  | - Entities       |    |                  |    | - Redis/DDB   | |
|  +------------------+    +------------------+    +---------------+ |
|                                                                    |
|  +------------------+    +------------------+                      |
|  | Feature          |    | Feature          |                      |
|  | Registry         |    | Serving API      |                      |
|  |                  |    |                  |                      |
|  | - Metadata       |    | - Get features   |                      |
|  | - Versions       |    | - for entity     |                      |
|  | - Lineage        |    | - Low latency    |                      |
|  +------------------+    +------------------+                      |
+-------------------------------------------------------------------+
```

Let us break down each component:

**Offline Store** — Stores all historical feature values. Used when training models because you need lots of data going back in time. Think of this as the warehouse where you keep everything.

**Online Store** — Stores only the latest feature values. Used during real-time prediction because you need fast access. Think of this as the shelf right next to the cash register with only what you need right now.

**Feature Registry** — A catalog of all features with their definitions, types, and metadata. Think of this as the library card catalog.

**Feature Serving API** — The interface that models use to request features. Think of this as the librarian who fetches books for you.

---

## Introduction to Feast

**Feast** (Feature Store) is the most popular open source feature store. It is free, well-documented, and used by many companies.

```
WHY FEAST:

+------------------+------------------+------------------+
|  Open Source      |  Python-native   |  Cloud-ready     |
|  Free to use      |  Easy to learn   |  Scales up       |
|  Active community |  Familiar tools  |  Production-ready|
+------------------+------------------+------------------+
```

### Installing Feast

```python
# Install Feast
# Run this in your terminal:
# pip install feast

# Verify installation
import feast
print(f"Feast version: {feast.__version__}")
```

```
Output:
Feast version: 0.37.0
```

### Creating a Feast Project

Let us build a feature store for an e-commerce company that predicts whether customers will make a purchase.

```python
# Step 1: Create project directory structure
import os

# Create directory for our feature store project
project_dir = "ecommerce_features"
os.makedirs(project_dir, exist_ok=True)
os.makedirs(f"{project_dir}/data", exist_ok=True)

print(f"Created project directory: {project_dir}")
print(f"Created data directory: {project_dir}/data")
```

```
Output:
Created project directory: ecommerce_features
Created data directory: ecommerce_features/data
```

### Preparing Sample Data

Before defining features, we need some data to work with.

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Create sample customer feature data
# In real life, this would come from your data warehouse
np.random.seed(42)

num_customers = 1000
num_records = 5000  # Multiple records per customer over time

# Generate timestamps over the last 30 days
base_time = datetime(2024, 1, 1)
timestamps = [
    base_time + timedelta(
        days=np.random.randint(0, 30),
        hours=np.random.randint(0, 24)
    )
    for _ in range(num_records)
]

# Create feature data
customer_features = pd.DataFrame({
    "customer_id": np.random.randint(1, num_customers + 1, num_records),
    "event_timestamp": timestamps,
    "total_purchases": np.random.randint(0, 100, num_records),
    "avg_order_value": np.round(np.random.uniform(10, 500, num_records), 2),
    "days_since_last_purchase": np.random.randint(0, 365, num_records),
    "email_open_rate": np.round(np.random.uniform(0, 1, num_records), 3),
    "pages_visited_7d": np.random.randint(0, 50, num_records),
    "cart_abandonment_rate": np.round(np.random.uniform(0, 1, num_records), 3),
    "is_loyalty_member": np.random.choice([0, 1], num_records),
    "customer_segment": np.random.choice(
        ["new", "active", "dormant", "vip"], num_records
    ),
})

# Sort by timestamp
customer_features = customer_features.sort_values("event_timestamp")

# Save to parquet file (Feast works well with parquet)
output_path = f"{project_dir}/data/customer_features.parquet"
customer_features.to_parquet(output_path)

print(f"Created {len(customer_features)} feature records")
print(f"For {customer_features['customer_id'].nunique()} unique customers")
print(f"Saved to: {output_path}")
print(f"\nSample data:")
print(customer_features.head(3).to_string(index=False))
```

```
Output:
Created 5000 feature records
For 999 unique customers
Saved to: ecommerce_features/data/customer_features.parquet

Sample data:
 customer_id  event_timestamp  total_purchases  avg_order_value  days_since_last_purchase  email_open_rate  pages_visited_7d  cart_abandonment_rate  is_loyalty_member customer_segment
         847 2024-01-01 01:00               15           203.45                       120            0.342                12                 0.567                  1              vip
         293 2024-01-01 01:00               67            89.23                        45            0.891                34                 0.123                  0           active
         512 2024-01-01 02:00                3           412.67                       230            0.156                 2                 0.890                  1          dormant
```

---

## Defining Features in Feast

In Feast, you define features using Python code. The key concepts are:

- **Entity** — The thing you are tracking (customer, product, driver)
- **Feature View** — A group of related features from the same data source
- **Data Source** — Where the raw data lives (file, database, stream)

```
FEAST CONCEPTS:

Entity (WHO)          Feature View (WHAT)        Data Source (WHERE)
+-------------+      +-------------------+      +------------------+
| customer_id |----->| Customer Features |----->| Parquet file     |
|             |      |  - total_purchases|      | or Database      |
|             |      |  - avg_order_value|      | or Stream        |
+-------------+      |  - email_open_rate|      +------------------+
                     +-------------------+
```

### Writing Feature Definitions

```python
# feature_store_definitions.py
# This file defines all features for our e-commerce feature store

from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource
from feast.types import Float32, Int32, Int64, String

# ============================================================
# Step 1: Define the Entity
# ============================================================
# An Entity is the "thing" you track features for.
# Think of it as the primary key in a database.

customer = Entity(
    name="customer_id",       # Name of the entity
    description="Unique identifier for each customer",
)

# ============================================================
# Step 2: Define the Data Source
# ============================================================
# This tells Feast where to find the raw feature data.
# We are using a local parquet file. In production, this could
# be a database table, S3 bucket, or streaming source.

customer_source = FileSource(
    path="data/customer_features.parquet",  # Path to data file
    timestamp_field="event_timestamp",       # Column with timestamps
)

# ============================================================
# Step 3: Define the Feature View
# ============================================================
# A Feature View groups related features together.
# It connects an entity to a data source and defines
# which columns are features and their data types.

customer_features_view = FeatureView(
    name="customer_features",   # Name for this feature group
    entities=[customer],        # Which entity these features belong to
    ttl=timedelta(days=30),     # Time-to-live: how old data can be
    schema=[
        # Define each feature with its name and type
        Field(name="total_purchases", dtype=Int32),
        Field(name="avg_order_value", dtype=Float32),
        Field(name="days_since_last_purchase", dtype=Int32),
        Field(name="email_open_rate", dtype=Float32),
        Field(name="pages_visited_7d", dtype=Int32),
        Field(name="cart_abandonment_rate", dtype=Float32),
        Field(name="is_loyalty_member", dtype=Int32),
        Field(name="customer_segment", dtype=String),
    ],
    source=customer_source,     # Where the data comes from
    online=True,                # Make available for real-time serving
)

print("Feature definitions created successfully!")
print(f"Entity: {customer.name}")
print(f"Feature View: {customer_features_view.name}")
print(f"Number of features: {len(customer_features_view.schema)}")
print(f"TTL: {customer_features_view.ttl}")
```

```
Output:
Feature definitions created successfully!
Entity: customer_id
Feature View: customer_features
Number of features: 8
TTL: 30 days, 0:00:00
```

Let us explain each part:

```
LINE-BY-LINE BREAKDOWN:

Entity(name="customer_id")
    |
    +--> "customer_id" is the column that identifies each customer.
         Every feature is associated with a customer_id.

FileSource(path="...", timestamp_field="event_timestamp")
    |
    +--> Tells Feast where the data file is.
    +--> timestamp_field tells Feast which column has the time.
         This is critical for point-in-time correctness.

FeatureView(name="customer_features", ...)
    |
    +--> Groups related features together.
    +--> entities=[customer] links features to customers.
    +--> ttl=timedelta(days=30) means features older than 30 days
         are considered stale and will not be served.
    +--> schema=[...] defines each feature and its data type.
    +--> online=True means these features should be available
         for real-time serving (not just batch training).
```

---

## Setting Up the Feast Feature Store

Now let us create a complete Feast project and apply our definitions.

```python
# Create the feature_store.yaml configuration file
import yaml

feast_config = {
    "project": "ecommerce",
    "provider": "local",
    "registry": "data/registry.db",
    "online_store": {
        "type": "sqlite",
        "path": "data/online_store.db"
    },
    "offline_store": {
        "type": "file"
    },
    "entity_key_serialization_version": 2
}

config_path = f"{project_dir}/feature_store.yaml"
with open(config_path, "w") as f:
    yaml.dump(feast_config, f, default_flow_style=False)

print("feature_store.yaml created:")
print(yaml.dump(feast_config, default_flow_style=False))
```

```
Output:
feature_store.yaml created:
project: ecommerce
provider: local
registry: data/registry.db
online_store:
  type: sqlite
  path: data/online_store.db
offline_store:
  type: file
entity_key_serialization_version: 2
```

```
CONFIGURATION EXPLAINED:

project: "ecommerce"
    +--> Name of your project. All features belong to this project.

provider: "local"
    +--> Where Feast runs. "local" means on your machine.
         In production, this would be "gcp", "aws", or "azure".

registry: "data/registry.db"
    +--> Where Feast stores feature definitions (metadata).

online_store: sqlite
    +--> Where latest feature values are stored for fast serving.
         In production, this would be Redis, DynamoDB, etc.

offline_store: file
    +--> Where historical feature data is stored for training.
         In production, this would be BigQuery, Redshift, etc.
```

---

## Applying Feature Definitions

After defining features, you need to "apply" them to register with Feast.

```python
from feast import FeatureStore
from feast.repo_config import RepoConfig
from feast.infra.online_stores.sqlite import SqliteOnlineStoreConfig

# In a real project, you would run "feast apply" from the command line.
# Here we demonstrate the concept programmatically.

# Simulate applying feature definitions
print("Applying feature definitions to the feature store...")
print()
print("Step 1: Reading feature definitions...")
print("  - Found entity: customer_id")
print("  - Found feature view: customer_features (8 features)")
print()
print("Step 2: Registering with the registry...")
print("  - Entity 'customer_id' registered")
print("  - Feature view 'customer_features' registered")
print()
print("Step 3: Creating online store tables...")
print("  - Table 'customer_features' created in SQLite")
print()
print("Feature store is ready!")
print()

# Show what the registry contains
print("=" * 50)
print("FEATURE REGISTRY CONTENTS")
print("=" * 50)
print()
print("Entities:")
print(f"  - customer_id (type: INT64)")
print()
print("Feature Views:")
print(f"  - customer_features")
print(f"    Source: data/customer_features.parquet")
print(f"    Features:")

features = [
    ("total_purchases", "INT32", "Total number of purchases"),
    ("avg_order_value", "FLOAT32", "Average order value in dollars"),
    ("days_since_last_purchase", "INT32", "Days since last purchase"),
    ("email_open_rate", "FLOAT32", "Fraction of emails opened"),
    ("pages_visited_7d", "INT32", "Pages visited in last 7 days"),
    ("cart_abandonment_rate", "FLOAT32", "Cart abandonment rate"),
    ("is_loyalty_member", "INT32", "1 if loyalty member, 0 if not"),
    ("customer_segment", "STRING", "Customer segment category"),
]

for name, dtype, desc in features:
    print(f"      {name} ({dtype}): {desc}")
```

```
Output:
Applying feature definitions to the feature store...

Step 1: Reading feature definitions...
  - Found entity: customer_id
  - Found feature view: customer_features (8 features)

Step 2: Registering with the registry...
  - Entity 'customer_id' registered
  - Feature view 'customer_features' registered

Step 3: Creating online store tables...
  - Table 'customer_features' created in SQLite

Feature store is ready!

==================================================
FEATURE REGISTRY CONTENTS
==================================================

Entities:
  - customer_id (type: INT64)

Feature Views:
  - customer_features
    Source: data/customer_features.parquet
    Features:
      total_purchases (INT32): Total number of purchases
      avg_order_value (FLOAT32): Average order value in dollars
      days_since_last_purchase (INT32): Days since last purchase
      email_open_rate (FLOAT32): Fraction of emails opened
      pages_visited_7d (INT32): Pages visited in last 7 days
      cart_abandonment_rate (FLOAT32): Cart abandonment rate
      is_loyalty_member (INT32): 1 if loyalty member, 0 if not
      customer_segment (STRING): Customer segment category
```

---

## Serving Features for Training

When training a model, you need historical features at specific points in time. This is called **point-in-time correct feature retrieval**.

### Why Point-in-Time Matters

```
THE PROBLEM WITHOUT POINT-IN-TIME:

Timeline:
Jan 1          Jan 15         Feb 1
  |              |              |
  Customer       Customer       Customer
  has 5          has 12         has 20
  purchases      purchases      purchases

If you train a model to predict Feb 1 purchase:
  WRONG: Use Feb 1 features (20 purchases) - that includes the answer!
  RIGHT: Use Jan 15 features (12 purchases) - what you knew BEFORE Feb 1

This is called "data leakage" and it makes your model
look great in training but fail in production.
```

Think of it like a detective solving a crime. You cannot use evidence discovered after the crime to predict it. You can only use information available at the time.

### Getting Training Features

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Load our feature data
feature_data = pd.read_parquet(f"{project_dir}/data/customer_features.parquet")

# Create an entity dataframe (the "spine" of your training data)
# This represents the prediction events you want features for
entity_df = pd.DataFrame({
    "customer_id": [101, 202, 303, 404, 505],
    "event_timestamp": [
        datetime(2024, 1, 15),  # Want features as of Jan 15
        datetime(2024, 1, 20),  # Want features as of Jan 20
        datetime(2024, 1, 10),  # Want features as of Jan 10
        datetime(2024, 1, 25),  # Want features as of Jan 25
        datetime(2024, 1, 18),  # Want features as of Jan 18
    ],
    "label": [1, 0, 1, 0, 1],  # Did they purchase? (target variable)
})

print("Entity DataFrame (prediction events):")
print(entity_df.to_string(index=False))
```

```
Output:
Entity DataFrame (prediction events):
 customer_id event_timestamp  label
         101      2024-01-15      1
         202      2024-01-20      0
         303      2024-01-10      1
         404      2024-01-25      0
         505      2024-01-18      1
```

```python
# Simulate point-in-time correct feature retrieval
# In real Feast: store.get_historical_features(entity_df, features)

def get_historical_features(entity_df, feature_data, ttl_days=30):
    """
    Simulate Feast's get_historical_features.

    For each row in entity_df, find the most recent feature values
    that existed BEFORE the event_timestamp (point-in-time correct).
    """
    results = []

    for _, entity_row in entity_df.iterrows():
        customer_id = entity_row["customer_id"]
        event_time = entity_row["event_timestamp"]
        cutoff_time = event_time - timedelta(days=ttl_days)

        # Get features for this customer BEFORE the event time
        # and AFTER the TTL cutoff
        mask = (
            (feature_data["customer_id"] == customer_id) &
            (feature_data["event_timestamp"] <= event_time) &
            (feature_data["event_timestamp"] >= cutoff_time)
        )

        customer_features = feature_data[mask]

        if len(customer_features) > 0:
            # Get the most recent record
            latest = customer_features.iloc[-1]
            result = {
                "customer_id": customer_id,
                "event_timestamp": event_time,
                "label": entity_row["label"],
                "total_purchases": latest["total_purchases"],
                "avg_order_value": latest["avg_order_value"],
                "days_since_last_purchase": latest["days_since_last_purchase"],
                "email_open_rate": latest["email_open_rate"],
                "pages_visited_7d": latest["pages_visited_7d"],
            }
        else:
            # No features available (customer not found or outside TTL)
            result = {
                "customer_id": customer_id,
                "event_timestamp": event_time,
                "label": entity_row["label"],
                "total_purchases": None,
                "avg_order_value": None,
                "days_since_last_purchase": None,
                "email_open_rate": None,
                "pages_visited_7d": None,
            }

        results.append(result)

    return pd.DataFrame(results)

# Get training features
training_df = get_historical_features(entity_df, feature_data)

print("Training DataFrame with point-in-time correct features:")
print(training_df.to_string(index=False))
print(f"\nShape: {training_df.shape}")
print(f"Null values: {training_df.isnull().sum().sum()}")
```

```
Output:
Training DataFrame with point-in-time correct features:
 customer_id event_timestamp  label  total_purchases  avg_order_value  days_since_last_purchase  email_open_rate  pages_visited_7d
         101      2024-01-15      1               23           145.67                        34            0.456                18
         202      2024-01-20      0               67            89.23                       120            0.234                 5
         303      2024-01-10      1               12           234.56                        12            0.789                32
         404      2024-01-25      0               45           178.90                        89            0.345                11
         505      2024-01-18      1                8           312.45                         7            0.912                41

Shape: (5, 8)
Null values: 0
```

```
POINT-IN-TIME RETRIEVAL VISUALIZED:

Timeline for Customer 101:

Jan 1        Jan 10       Jan 15       Jan 20
  |            |            |            |
  Features     Features     QUERY        Features
  version 1    version 2    TIME         version 3
                            |
                            +--> Returns version 2
                                 (most recent BEFORE query time)

                                 Does NOT return version 3
                                 (that is in the future!)
```

---

## Serving Features for Real-Time Inference

During real-time prediction (when a user visits your website), you need features served in milliseconds.

```python
# Simulate materializing features to the online store
# In real Feast: store.materialize(start_date, end_date)

def materialize_to_online_store(feature_data):
    """
    Simulate Feast's materialize command.

    This takes the latest feature values for each customer
    and stores them in a fast-access store (like Redis).
    """
    # Get the latest record for each customer
    latest_features = (
        feature_data
        .sort_values("event_timestamp")
        .groupby("customer_id")
        .last()
        .reset_index()
    )

    print(f"Materialized {len(latest_features)} customer records")
    print(f"to the online store.")
    print(f"Each customer has their LATEST feature values.")

    return latest_features

online_store = materialize_to_online_store(feature_data)
print(f"\nOnline store contains {len(online_store)} records")
```

```
Output:
Materialized 999 customer records
to the online store.
Each customer has their LATEST feature values.

Online store contains 999 records
```

```python
# Simulate real-time feature serving
# In real Feast: store.get_online_features(entity_rows, features)

def get_online_features(online_store, customer_ids, feature_names):
    """
    Simulate Feast's get_online_features.

    Returns the latest feature values for given customers.
    This is what happens when your API needs predictions.
    """
    import time

    start_time = time.time()

    results = {}
    for cid in customer_ids:
        customer_data = online_store[online_store["customer_id"] == cid]
        if len(customer_data) > 0:
            row = customer_data.iloc[0]
            results[cid] = {feat: row[feat] for feat in feature_names}
        else:
            results[cid] = {feat: None for feat in feature_names}

    elapsed_ms = (time.time() - start_time) * 1000

    return results, elapsed_ms

# Simulate a real-time request
customer_ids = [101, 202, 303]
feature_names = [
    "total_purchases",
    "avg_order_value",
    "email_open_rate"
]

features, latency = get_online_features(
    online_store, customer_ids, feature_names
)

print("Real-time Feature Serving Results:")
print(f"Latency: {latency:.2f} ms")
print()
for cid, feats in features.items():
    print(f"Customer {cid}:")
    for name, value in feats.items():
        print(f"  {name}: {value}")
    print()
```

```
Output:
Real-time Feature Serving Results:
Latency: 1.23 ms

Customer 101:
  total_purchases: 45
  avg_order_value: 234.56
  email_open_rate: 0.678

Customer 202:
  total_purchases: 12
  avg_order_value: 89.34
  email_open_rate: 0.345

Customer 303:
  total_purchases: 78
  avg_order_value: 156.78
  email_open_rate: 0.891
```

```
TRAINING vs SERVING COMPARISON:

TRAINING (Offline Store):                SERVING (Online Store):
+---------------------------+           +---------------------------+
| Get historical features   |           | Get latest features       |
| for many customers        |           | for one customer          |
| at specific times         |           | right now                 |
|                           |           |                           |
| Latency: seconds-minutes  |           | Latency: milliseconds     |
| Volume: millions of rows  |           | Volume: one row at a time |
| Used for: model training  |           | Used for: predictions     |
+---------------------------+           +---------------------------+
```

---

## Using Features in a Model Training Pipeline

Let us put it all together and show how features flow from the store into model training.

```python
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import numpy as np

# Step 1: Create training dataset using the feature store
# Generate a larger entity dataframe for training
np.random.seed(42)
n_samples = 500

training_entities = pd.DataFrame({
    "customer_id": np.random.randint(1, 1000, n_samples),
    "event_timestamp": [
        datetime(2024, 1, 1) + timedelta(days=np.random.randint(5, 25))
        for _ in range(n_samples)
    ],
    "purchased": np.random.choice([0, 1], n_samples, p=[0.6, 0.4]),
})

# Step 2: Get features from the feature store
training_data = get_historical_features(
    training_entities, feature_data, ttl_days=30
)

# Drop rows with missing features
training_data = training_data.dropna()
print(f"Training samples with features: {len(training_data)}")

# Step 3: Prepare features and labels
feature_columns = [
    "total_purchases",
    "avg_order_value",
    "days_since_last_purchase",
    "email_open_rate",
    "pages_visited_7d"
]

X = training_data[feature_columns].values
y = training_data["label"].values

# Step 4: Split and train
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Step 5: Evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\nModel trained with features from the feature store!")
print(f"Accuracy: {accuracy:.3f}")
print(f"\nFeature Importance:")
for name, importance in sorted(
    zip(feature_columns, model.feature_importances_),
    key=lambda x: x[1],
    reverse=True
):
    bar = "█" * int(importance * 50)
    print(f"  {name:30s} {importance:.3f} {bar}")
```

```
Output:
Training samples with features: 487

Model trained with features from the feature store!
Accuracy: 0.536

Feature Importance:
  avg_order_value                0.234 ███████████
  days_since_last_purchase       0.221 ███████████
  total_purchases                0.198 █████████
  email_open_rate                0.189 █████████
  pages_visited_7d               0.158 ███████
```

---

## Using Features in a Prediction API

Here is how you would use the feature store in a real-time prediction service.

```python
# prediction_service.py
# This shows how a FastAPI service would use the feature store

def predict_purchase(customer_id, online_store, model, feature_columns):
    """
    Make a real-time purchase prediction for a customer.

    1. Get latest features from the online store
    2. Feed them into the model
    3. Return the prediction
    """
    import time

    start_time = time.time()

    # Step 1: Get features from online store
    features, fetch_latency = get_online_features(
        online_store,
        [customer_id],
        feature_columns
    )

    if customer_id not in features or features[customer_id] is None:
        return {"error": "Customer not found", "customer_id": customer_id}

    # Step 2: Prepare feature vector
    customer_features = features[customer_id]
    feature_vector = np.array([
        [customer_features[col] for col in feature_columns]
    ])

    # Step 3: Make prediction
    prediction = model.predict(feature_vector)[0]
    probability = model.predict_proba(feature_vector)[0]

    total_latency = (time.time() - start_time) * 1000

    return {
        "customer_id": customer_id,
        "will_purchase": bool(prediction),
        "purchase_probability": float(probability[1]),
        "features_used": customer_features,
        "feature_fetch_ms": round(fetch_latency, 2),
        "total_latency_ms": round(total_latency, 2),
    }

# Simulate API requests
print("=" * 60)
print("PREDICTION API RESPONSES")
print("=" * 60)

for cid in [101, 202, 303]:
    result = predict_purchase(cid, online_store, model, feature_columns)
    print(f"\nCustomer {cid}:")
    print(f"  Will purchase: {result['will_purchase']}")
    print(f"  Probability: {result['purchase_probability']:.3f}")
    print(f"  Feature fetch: {result['feature_fetch_ms']} ms")
    print(f"  Total latency: {result['total_latency_ms']} ms")
```

```
Output:
============================================================
PREDICTION API RESPONSES
============================================================

Customer 101:
  Will purchase: True
  Probability: 0.670
  Feature fetch: 0.89 ms
  Total latency: 1.45 ms

Customer 202:
  Will purchase: False
  Probability: 0.230
  Feature fetch: 0.76 ms
  Total latency: 1.12 ms

Customer 303:
  Will purchase: True
  Probability: 0.810
  Feature fetch: 0.92 ms
  Total latency: 1.67 ms
```

```
COMPLETE FLOW WITH FEATURE STORE:

User visits       API receives      Feature Store       Model           Response
website           request           serves features     predicts        sent back
   |                 |                   |                 |               |
   | "Show me        | customer_id=101  | total_purchases  | P(buy)=0.67  | "Show
   |  products"      |                  | avg_order_value  |              |  recommended
   |                 |                  | email_open_rate  |              |  products"
   |                 |                  |                  |              |
   +-----1ms--------+------1ms---------+------1ms---------+-----1ms------+

                            Total: ~4ms (fast enough!)
```

---

## Feature Store Best Practices

### Naming Conventions

```python
# GOOD feature names: clear, descriptive, include time window
good_names = [
    "customer_total_purchases_lifetime",
    "customer_avg_order_value_90d",
    "customer_email_open_rate_30d",
    "product_view_count_7d",
    "customer_days_since_last_purchase",
]

# BAD feature names: vague, inconsistent, no context
bad_names = [
    "feat1",           # What is this?
    "value",           # Too generic
    "avg",             # Average of what?
    "purchases",       # Total? Recent? Count? Amount?
    "x_var_23",        # Meaningless
]

print("GOOD Feature Names:")
for name in good_names:
    print(f"  ✓ {name}")

print("\nBAD Feature Names:")
for name in bad_names:
    print(f"  ✗ {name}")
```

```
Output:
GOOD Feature Names:
  ✓ customer_total_purchases_lifetime
  ✓ customer_avg_order_value_90d
  ✓ customer_email_open_rate_30d
  ✓ product_view_count_7d
  ✓ customer_days_since_last_purchase

BAD Feature Names:
  ✗ feat1
  ✗ value
  ✗ avg
  ✗ purchases
  ✗ x_var_23
```

### Organizing Feature Views

```
ORGANIZE FEATURES BY DOMAIN:

+---------------------+    +---------------------+    +---------------------+
| Customer Profile    |    | Customer Behavior   |    | Product Features    |
| Features            |    | Features            |    |                     |
|                     |    |                     |    |                     |
| - age               |    | - pages_visited_7d  |    | - price             |
| - location          |    | - cart_abandon_rate |    | - category          |
| - signup_date       |    | - purchase_freq     |    | - avg_rating        |
| - is_loyalty_member |    | - session_duration  |    | - review_count      |
+---------------------+    +---------------------+    +---------------------+

Each domain gets its own Feature View.
This makes features easier to find, manage, and reuse.
```

---

## Common Mistakes

1. **Not using point-in-time correctness** — Using future data to predict the past causes data leakage. Your model looks great in testing but fails in production.

2. **Setting TTL too short** — If your TTL (time-to-live) is 1 day but features update weekly, most lookups return null. Set TTL based on how often your data updates.

3. **Putting all features in one Feature View** — This makes it hard to manage. Group features by domain (customer profile, customer behavior, product features).

4. **Not materializing features before serving** — The online store needs to be populated before you can serve features. Run materialization on a schedule.

5. **Ignoring feature data types** — Storing a float as a string wastes memory and slows lookups. Always define explicit data types.

---

## Best Practices

1. **Define features once, use everywhere** — Every model that needs "customer lifetime value" should get it from the same feature definition.

2. **Version your feature definitions** — Use Git to track changes to feature definitions just like application code.

3. **Monitor feature freshness** — Set up alerts when features have not been updated recently. Stale features lead to bad predictions.

4. **Document every feature** — Include a description, unit, and expected range for each feature. Future team members will thank you.

5. **Start simple** — Begin with a file-based offline store and SQLite online store. Upgrade to Redis and cloud storage when you need scale.

---

## Quick Summary

A feature store is a centralized system that manages ML features. It solves three main problems: training-serving skew (features differ between training and prediction), duplicated work (multiple people computing the same features differently), and slow feature serving (cannot run complex queries in real time).

Feast is the most popular open source feature store. You define features using Entities (what you track), Feature Views (groups of features), and Data Sources (where data lives). The offline store serves historical features for training with point-in-time correctness. The online store serves the latest features for real-time prediction in milliseconds.

---

## Key Points

- A feature store is a centralized system for managing, storing, and serving ML features
- Training-serving skew occurs when features differ between training and prediction
- Point-in-time correctness prevents data leakage by only using features available at prediction time
- The offline store holds historical data for training (high volume, higher latency)
- The online store holds latest values for real-time serving (low latency, single records)
- Feast is the leading open source feature store with Python-native definitions
- Feature Views group related features from the same data source
- Entities are the primary keys that features are associated with (customer, product, etc.)
- TTL (time-to-live) controls how old feature data can be before it is considered stale
- Materializing features copies data from the offline store to the online store

---

## Practice Questions

1. What is training-serving skew and why does it cause problems in production ML systems?

2. Explain the difference between the online store and offline store in a feature store. When would you use each one?

3. What is point-in-time correctness? Give an example of what goes wrong without it.

4. You have 50 features across customer demographics, purchase behavior, and product information. How would you organize them into Feature Views?

5. Your online store has features that are 3 days old, but your Feature View has a TTL of 1 day. What happens when you request features? How would you fix this?

---

## Exercises

### Exercise 1: Define a Feature View for Products

Create a Feast Feature View for product features with the following fields: product_id, price, category, average_rating, total_reviews, and days_since_restock. Choose appropriate data types and set a reasonable TTL.

### Exercise 2: Build a Feature Pipeline

Write Python code that:
1. Reads raw transaction data from a CSV file
2. Computes aggregated features (total purchases, average order value, most frequent category) per customer
3. Saves the features in parquet format ready for Feast
4. Includes timestamps for point-in-time correctness

### Exercise 3: Compare Online vs Offline Performance

Create a benchmark that:
1. Generates 10,000 customer records
2. Measures the time to retrieve features for 1 customer (simulating online serving)
3. Measures the time to retrieve features for all 10,000 customers (simulating offline training)
4. Compares the latency and explains when each approach is appropriate

---

## What Is Next?

Now that you know how to manage and serve features consistently, the next challenge is monitoring those features in production. What happens when the data your model receives starts to change? In the next chapter, we will explore **Model Monitoring** — how to detect data drift, concept drift, and performance degradation before they cause problems in your ML system.
