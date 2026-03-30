# Chapter 1: From Notebook to Production

## What You Will Learn

In this chapter, you will learn:

- Why moving code from notebooks to production matters
- The key differences between notebook code and production code
- How to refactor messy notebook code into clean Python scripts
- How to organize an ML project with a proper folder structure
- How to use configuration files to manage settings
- How to add logging so you can track what your code does

## Why This Chapter Matters

Imagine you are a chef. You have been experimenting with recipes in your home kitchen. You try a little of this, a little of that. You taste as you go. Your kitchen is messy, but the food tastes great.

Now imagine someone says, "That dish is amazing! Can you make it for 500 people every day?" Suddenly, your messy home kitchen approach will not work. You need a commercial kitchen, standardized recipes, proper equipment, and a team that can follow your process.

This is exactly what happens in machine learning. You build a great model in a Jupyter notebook. It works! But then someone asks, "Can we use this in our app?" or "Can this run automatically every day?" That is when you need to move from notebook to production.

This chapter is the bridge between "it works on my laptop" and "it works for real users."

---

## The Problem with Notebooks

Jupyter notebooks are wonderful for exploration and learning. They let you run code cell by cell, see results immediately, and mix code with explanations. But they have serious problems when you try to use them in the real world.

### What Makes Notebooks Great for Learning

```
+------------------------------------------+
|  Jupyter Notebook                        |
|                                          |
|  [Cell 1] Load data         -> Output    |
|  [Cell 2] Explore data      -> Charts    |
|  [Cell 3] Clean data        -> Output    |
|  [Cell 4] Train model       -> Metrics   |
|  [Cell 5] Evaluate          -> Results   |
|                                          |
|  Interactive! Visual! Easy to change!    |
+------------------------------------------+
```

### What Makes Notebooks Bad for Production

Here are the main problems:

**Problem 1: Cells can run out of order.**

In a notebook, you might run Cell 5, then go back and change Cell 2, then run Cell 4. The notebook remembers the old Cell 2 results. This creates hidden bugs that are hard to find.

**Problem 2: Hidden state.**

Variables from deleted cells might still be in memory. Your code works now, but if you restart the notebook and run everything from the top, it might break.

**Problem 3: No error handling.**

When you explore data, you do not think about what happens when the data file is missing, or the data has unexpected values. Production code must handle these situations.

**Problem 4: Hard to test.**

You cannot easily write automated tests for notebook code. Tests are essential in production.

**Problem 5: Hard to version control.**

Notebooks are stored as JSON files. When two people edit the same notebook, merging changes is a nightmare.

**Problem 6: Cannot be imported.**

You cannot import functions from a notebook into another Python file. In production, you want reusable code.

---

## Notebook Code vs Production Code

Let us look at a concrete example. Here is typical notebook code for training a simple model:

### The Notebook Way (Messy but Common)

```python
# Cell 1
import pandas as pd
df = pd.read_csv("data.csv")
df.head()

# Cell 2
df.shape

# Cell 3
df.isnull().sum()

# Cell 4
df = df.dropna()

# Cell 5
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

X = df.drop("target", axis=1)
y = df["target"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Cell 6
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Cell 7
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(f"Accuracy: {accuracy}")
```

```
Output:
Accuracy: 0.92
```

This code works, but it has many problems:

- File path is hardcoded ("data.csv")
- No error handling (what if the file does not exist?)
- No logging (how do we know what happened when it ran?)
- Everything is in one place (cannot reuse parts)
- Magic numbers everywhere (100 trees, 0.2 test size, 42 random state)

### The Production Way (Clean and Reliable)

Now let us see what production code looks like. We will break it into multiple files:

**File: config.yaml**

```yaml
# Configuration file for our ML project
# Change settings here without touching code

data:
  input_path: "data/raw/dataset.csv"
  test_size: 0.2
  random_state: 42

model:
  type: "random_forest"
  n_estimators: 100
  random_state: 42

output:
  model_path: "models/trained_model.pkl"
  log_file: "logs/training.log"
```

**File: src/data_loader.py**

```python
"""
data_loader.py - Functions for loading and preparing data.

This module handles all data-related operations:
reading files, cleaning data, and splitting into
training and test sets.
"""

import pandas as pd
from sklearn.model_selection import train_test_split
import logging

# Create a logger for this module
# A logger is like a diary that records what your code does
logger = logging.getLogger(__name__)


def load_data(file_path):
    """
    Load data from a CSV file.

    Parameters
    ----------
    file_path : str
        Path to the CSV file.

    Returns
    -------
    pd.DataFrame
        The loaded data.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    """
    logger.info(f"Loading data from {file_path}")

    try:
        df = pd.read_csv(file_path)
        logger.info(f"Loaded {len(df)} rows and {len(df.columns)} columns")
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise


def clean_data(df):
    """
    Clean the data by removing rows with missing values.

    Parameters
    ----------
    df : pd.DataFrame
        The raw data.

    Returns
    -------
    pd.DataFrame
        The cleaned data.
    """
    original_rows = len(df)
    df_clean = df.dropna()
    removed_rows = original_rows - len(df_clean)

    logger.info(f"Removed {removed_rows} rows with missing values")
    logger.info(f"Clean data has {len(df_clean)} rows")

    return df_clean


def split_data(df, target_column, test_size=0.2, random_state=42):
    """
    Split data into training and test sets.

    Parameters
    ----------
    df : pd.DataFrame
        The cleaned data.
    target_column : str
        Name of the column to predict.
    test_size : float
        Fraction of data to use for testing (0.0 to 1.0).
    random_state : int
        Random seed for reproducibility.

    Returns
    -------
    tuple
        (X_train, X_test, y_train, y_test)
    """
    X = df.drop(target_column, axis=1)
    y = df[target_column]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    logger.info(f"Training set: {len(X_train)} samples")
    logger.info(f"Test set: {len(X_test)} samples")

    return X_train, X_test, y_train, y_test
```

```
Output (when used):
INFO - Loading data from data/raw/dataset.csv
INFO - Loaded 1000 rows and 11 columns
INFO - Removed 15 rows with missing values
INFO - Clean data has 985 rows
INFO - Training set: 788 samples
INFO - Test set: 197 samples
```

Let us break down what makes this better:

**Line-by-line explanation of key parts:**

```python
logger = logging.getLogger(__name__)
```

This creates a logger. Think of it as a diary for your code. `__name__` is a special Python variable that holds the name of the current file. This way, when you read the logs, you know which file wrote each message.

```python
def load_data(file_path):
```

Instead of hardcoding "data.csv", we accept the file path as a parameter. This makes the function flexible and reusable.

```python
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
```

The `try/except` block catches errors gracefully. If the file does not exist, we log a helpful error message before raising the error. In a notebook, the error would just crash. In production, we want to know exactly what went wrong.

```python
    """
    Load data from a CSV file.

    Parameters
    ----------
    ...
    """
```

This is a docstring. It explains what the function does, what it needs, and what it returns. Other developers (and future you) will thank you for writing these.

---

## Project Structure

A well-organized project is like a well-organized house. Everything has its place, and anyone can find what they need.

Here is a recommended structure for an ML project:

```
my-ml-project/
│
├── README.md              # What this project does
├── requirements.txt       # Python packages needed
├── config.yaml            # Settings and parameters
├── setup.py               # Package installation file
│
├── data/
│   ├── raw/               # Original, unchanged data
│   ├── processed/         # Cleaned, ready-to-use data
│   └── external/          # Data from outside sources
│
├── notebooks/
│   ├── 01-exploration.ipynb    # Data exploration
│   └── 02-experiments.ipynb    # Model experiments
│
├── src/
│   ├── __init__.py        # Makes src a Python package
│   ├── data_loader.py     # Data loading functions
│   ├── features.py        # Feature engineering
│   ├── model.py           # Model training and prediction
│   └── evaluate.py        # Model evaluation
│
├── tests/
│   ├── __init__.py
│   ├── test_data_loader.py
│   └── test_model.py
│
├── models/
│   └── trained_model.pkl  # Saved model files
│
├── logs/
│   └── training.log       # Log files
│
└── scripts/
    ├── train.py           # Script to train model
    └── predict.py         # Script to make predictions
```

Let us understand each folder:

```
+---------------------------------------------------+
|  Project Structure Explained                       |
|                                                    |
|  data/       -> Where your data lives              |
|  notebooks/  -> For exploration only               |
|  src/        -> Your production code               |
|  tests/      -> Automated tests                    |
|  models/     -> Saved trained models               |
|  logs/       -> What happened when code ran         |
|  scripts/    -> Entry points to run things          |
+---------------------------------------------------+
```

### Creating the Project Structure

Here is a Python script that creates this structure for you:

```python
"""
create_project.py - Create an ML project structure.

Run this script to set up a new ML project with
all the necessary folders and files.
"""

import os


def create_project(project_name):
    """
    Create a standard ML project structure.

    Parameters
    ----------
    project_name : str
        Name of the project (used as the root folder name).
    """
    # Define all the folders we need
    folders = [
        "data/raw",
        "data/processed",
        "data/external",
        "notebooks",
        "src",
        "tests",
        "models",
        "logs",
        "scripts",
    ]

    # Create each folder
    for folder in folders:
        path = os.path.join(project_name, folder)
        os.makedirs(path, exist_ok=True)
        print(f"Created: {path}")

        # Add __init__.py to Python package folders
        # __init__.py tells Python "this folder is a package"
        if folder in ["src", "tests"]:
            init_file = os.path.join(path, "__init__.py")
            with open(init_file, "w") as f:
                f.write("")
            print(f"Created: {init_file}")

    # Create essential files
    essential_files = {
        "README.md": f"# {project_name}\n\nDescribe your project here.\n",
        "requirements.txt": "pandas\nscikit-learn\npyyaml\n",
        "config.yaml": "# Project configuration\n",
        ".gitignore": "data/\nmodels/\nlogs/\n__pycache__/\n*.pyc\n",
    }

    for filename, content in essential_files.items():
        filepath = os.path.join(project_name, filename)
        with open(filepath, "w") as f:
            f.write(content)
        print(f"Created: {filepath}")

    print(f"\nProject '{project_name}' created successfully!")


# Run it
create_project("my-ml-project")
```

```
Output:
Created: my-ml-project/data/raw
Created: my-ml-project/data/processed
Created: my-ml-project/data/external
Created: my-ml-project/notebooks
Created: my-ml-project/src
Created: my-ml-project/src/__init__.py
Created: my-ml-project/tests
Created: my-ml-project/tests/__init__.py
Created: my-ml-project/models
Created: my-ml-project/logs
Created: my-ml-project/scripts
Created: my-ml-project/README.md
Created: my-ml-project/requirements.txt
Created: my-ml-project/config.yaml
Created: my-ml-project/.gitignore

Project 'my-ml-project' created successfully!
```

---

## Refactoring a Notebook into Scripts

Refactoring means reorganizing code without changing what it does. Think of it like reorganizing a messy closet. The same clothes are there, but now you can find what you need.

Let us refactor our earlier notebook code step by step.

### Step 1: Identify Logical Groups

Look at your notebook and group cells by what they do:

```
+--------------------------------------------------+
|  Notebook Cell Groups                             |
|                                                   |
|  Group 1: Data Loading     -> data_loader.py      |
|  Group 2: Data Cleaning    -> data_loader.py      |
|  Group 3: Feature Work     -> features.py         |
|  Group 4: Model Training   -> model.py            |
|  Group 5: Evaluation       -> evaluate.py         |
|  Group 6: Run Everything   -> scripts/train.py    |
+--------------------------------------------------+
```

### Step 2: Create the Model Module

**File: src/model.py**

```python
"""
model.py - Model training and prediction functions.

This module handles creating, training, and using
machine learning models.
"""

from sklearn.ensemble import RandomForestClassifier
import logging
import joblib

logger = logging.getLogger(__name__)


def create_model(model_type="random_forest", **kwargs):
    """
    Create a machine learning model.

    Parameters
    ----------
    model_type : str
        Type of model to create. Currently supports
        "random_forest".
    **kwargs : dict
        Additional parameters passed to the model.
        For example: n_estimators=100, random_state=42

    Returns
    -------
    model
        An untrained model object.
    """
    if model_type == "random_forest":
        model = RandomForestClassifier(**kwargs)
        logger.info(
            f"Created RandomForest with params: {kwargs}"
        )
    else:
        raise ValueError(f"Unknown model type: {model_type}")

    return model


def train_model(model, X_train, y_train):
    """
    Train a model on the training data.

    Parameters
    ----------
    model : sklearn model
        The model to train.
    X_train : pd.DataFrame
        Training features.
    y_train : pd.Series
        Training labels.

    Returns
    -------
    model
        The trained model.
    """
    logger.info("Starting model training...")
    model.fit(X_train, y_train)
    logger.info("Model training complete")
    return model


def save_model(model, file_path):
    """
    Save a trained model to a file.

    Parameters
    ----------
    model : sklearn model
        The trained model to save.
    file_path : str
        Where to save the model.
    """
    joblib.dump(model, file_path)
    logger.info(f"Model saved to {file_path}")


def load_model(file_path):
    """
    Load a trained model from a file.

    Parameters
    ----------
    file_path : str
        Path to the saved model file.

    Returns
    -------
    model
        The loaded model.
    """
    model = joblib.load(file_path)
    logger.info(f"Model loaded from {file_path}")
    return model
```

### Step 3: Create the Evaluation Module

**File: src/evaluate.py**

```python
"""
evaluate.py - Model evaluation functions.

This module provides functions to measure how well
a model performs.
"""

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
)
import logging

logger = logging.getLogger(__name__)


def evaluate_model(model, X_test, y_test):
    """
    Evaluate a trained model on test data.

    Parameters
    ----------
    model : sklearn model
        The trained model.
    X_test : pd.DataFrame
        Test features.
    y_test : pd.Series
        True test labels.

    Returns
    -------
    dict
        Dictionary with evaluation metrics.
    """
    # Make predictions on test data
    predictions = model.predict(X_test)

    # Calculate multiple metrics
    # Accuracy: what fraction of predictions are correct
    # Precision: of positive predictions, how many are right
    # Recall: of actual positives, how many did we find
    # F1: balance between precision and recall
    metrics = {
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(
            y_test, predictions, average="weighted"
        ),
        "recall": recall_score(
            y_test, predictions, average="weighted"
        ),
        "f1": f1_score(
            y_test, predictions, average="weighted"
        ),
    }

    # Log each metric
    for name, value in metrics.items():
        logger.info(f"{name}: {value:.4f}")

    return metrics


def print_report(model, X_test, y_test):
    """
    Print a detailed classification report.

    Parameters
    ----------
    model : sklearn model
        The trained model.
    X_test : pd.DataFrame
        Test features.
    y_test : pd.Series
        True test labels.
    """
    predictions = model.predict(X_test)
    report = classification_report(y_test, predictions)
    print("\nClassification Report:")
    print(report)
    logger.info("Classification report printed")
```

### Step 4: Create the Training Script

**File: scripts/train.py**

```python
"""
train.py - Main training script.

This script ties everything together. It reads the
configuration, loads data, trains a model, evaluates
it, and saves it.

Usage:
    python scripts/train.py
    python scripts/train.py --config custom_config.yaml
"""

import sys
import os
import yaml
import logging
import argparse
from datetime import datetime

# Add the project root to Python's path
# This lets us import from the src folder
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.data_loader import load_data, clean_data, split_data
from src.model import create_model, train_model, save_model
from src.evaluate import evaluate_model, print_report


def setup_logging(log_file=None):
    """
    Set up logging to both console and file.

    Parameters
    ----------
    log_file : str, optional
        Path to log file. If None, logs only to console.
    """
    # Create a formatter that adds timestamp and level
    # Format: 2024-01-15 10:30:45 - INFO - Message here
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Set up the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Always log to console (so you can see what is happening)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Optionally also log to a file (for later review)
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def load_config(config_path="config.yaml"):
    """
    Load configuration from a YAML file.

    Parameters
    ----------
    config_path : str
        Path to the configuration file.

    Returns
    -------
    dict
        Configuration dictionary.
    """
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config


def main():
    """Main training pipeline."""
    # Parse command line arguments
    # argparse lets users pass options when running the script
    parser = argparse.ArgumentParser(
        description="Train an ML model"
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to config file (default: config.yaml)",
    )
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Set up logging
    log_file = config.get("output", {}).get("log_file")
    setup_logging(log_file)

    logger = logging.getLogger(__name__)
    logger.info("=" * 50)
    logger.info("Starting training pipeline")
    logger.info(f"Time: {datetime.now()}")
    logger.info("=" * 50)

    # Step 1: Load data
    data_config = config["data"]
    df = load_data(data_config["input_path"])

    # Step 2: Clean data
    df = clean_data(df)

    # Step 3: Split data
    X_train, X_test, y_train, y_test = split_data(
        df,
        target_column="target",
        test_size=data_config.get("test_size", 0.2),
        random_state=data_config.get("random_state", 42),
    )

    # Step 4: Create and train model
    model_config = config["model"]
    model = create_model(
        model_type=model_config["type"],
        n_estimators=model_config.get("n_estimators", 100),
        random_state=model_config.get("random_state", 42),
    )
    model = train_model(model, X_train, y_train)

    # Step 5: Evaluate model
    metrics = evaluate_model(model, X_test, y_test)
    print_report(model, X_test, y_test)

    # Step 6: Save model
    model_path = config["output"]["model_path"]
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    save_model(model, model_path)

    logger.info("=" * 50)
    logger.info("Training pipeline complete!")
    logger.info(f"Model saved to: {model_path}")
    logger.info(f"Accuracy: {metrics['accuracy']:.4f}")
    logger.info("=" * 50)


# This block runs only when you execute the script directly
# It does NOT run when you import this file
if __name__ == "__main__":
    main()
```

```
Output:
2024-01-15 10:30:45 - __main__ - INFO - ==================================================
2024-01-15 10:30:45 - __main__ - INFO - Starting training pipeline
2024-01-15 10:30:45 - __main__ - INFO - Time: 2024-01-15 10:30:45.123456
2024-01-15 10:30:45 - __main__ - INFO - ==================================================
2024-01-15 10:30:45 - src.data_loader - INFO - Loading data from data/raw/dataset.csv
2024-01-15 10:30:45 - src.data_loader - INFO - Loaded 1000 rows and 11 columns
2024-01-15 10:30:45 - src.data_loader - INFO - Removed 15 rows with missing values
2024-01-15 10:30:45 - src.data_loader - INFO - Clean data has 985 rows
2024-01-15 10:30:45 - src.data_loader - INFO - Training set: 788 samples
2024-01-15 10:30:45 - src.data_loader - INFO - Test set: 197 samples
2024-01-15 10:30:46 - src.model - INFO - Created RandomForest with params: {'n_estimators': 100, 'random_state': 42}
2024-01-15 10:30:46 - src.model - INFO - Starting model training...
2024-01-15 10:30:47 - src.model - INFO - Model training complete
2024-01-15 10:30:47 - src.evaluate - INFO - accuracy: 0.9200
2024-01-15 10:30:47 - src.evaluate - INFO - precision: 0.9215
2024-01-15 10:30:47 - src.evaluate - INFO - recall: 0.9200
2024-01-15 10:30:47 - src.evaluate - INFO - f1: 0.9195
2024-01-15 10:30:47 - src.model - INFO - Model saved to models/trained_model.pkl
2024-01-15 10:30:47 - __main__ - INFO - ==================================================
2024-01-15 10:30:47 - __main__ - INFO - Training pipeline complete!
2024-01-15 10:30:47 - __main__ - INFO - Model saved to: models/trained_model.pkl
2024-01-15 10:30:47 - __main__ - INFO - Accuracy: 0.9200
2024-01-15 10:30:47 - __main__ - INFO - ==================================================
```

---

## Configuration Files

A configuration file stores settings separately from your code. This is like having a recipe card separate from the cooking instructions. You can change the ingredients without rewriting the instructions.

### Why Use Config Files?

```
+-------------------------------------------------+
|  Without Config Files          With Config Files |
|                                                  |
|  Change code to change      Change config only   |
|  settings                                        |
|                                                  |
|  Risk breaking things       Code stays the same  |
|                                                  |
|  Hard to track changes      Easy to compare      |
|                                                  |
|  Different settings for     One config per        |
|  dev vs prod? Messy!        environment           |
+-------------------------------------------------+
```

### YAML Configuration Example

YAML (Yet Another Markup Language) is a human-friendly format for configuration files. It uses indentation to show structure, like Python.

```yaml
# config.yaml - Main configuration file

# Data settings
data:
  input_path: "data/raw/dataset.csv"
  target_column: "target"
  test_size: 0.2
  random_state: 42

# Model settings
model:
  type: "random_forest"
  params:
    n_estimators: 100
    max_depth: 10
    min_samples_split: 5
    random_state: 42

# Training settings
training:
  epochs: 50          # Not used for sklearn, but useful for deep learning
  batch_size: 32
  learning_rate: 0.001

# Output settings
output:
  model_path: "models/trained_model.pkl"
  metrics_path: "models/metrics.json"
  log_file: "logs/training.log"

# Feature settings
features:
  numeric_columns:
    - "age"
    - "income"
    - "score"
  categorical_columns:
    - "city"
    - "category"
```

### Loading Configuration in Python

```python
"""
config_loader.py - Load and validate configuration.
"""

import yaml
import os


def load_config(config_path="config.yaml"):
    """
    Load configuration from a YAML file.

    Parameters
    ----------
    config_path : str
        Path to the YAML configuration file.

    Returns
    -------
    dict
        Configuration as a Python dictionary.

    Raises
    ------
    FileNotFoundError
        If the config file does not exist.
    ValueError
        If the config file is empty or invalid.
    """
    # Check if file exists
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"Config file not found: {config_path}"
        )

    # Read and parse YAML
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Validate that we got something
    if config is None:
        raise ValueError(
            f"Config file is empty: {config_path}"
        )

    return config


def get_nested(config, *keys, default=None):
    """
    Safely get a nested value from the config.

    This is like navigating a folder structure:
    get_nested(config, "model", "params", "n_estimators")
    is like going to config -> model -> params -> n_estimators

    Parameters
    ----------
    config : dict
        The configuration dictionary.
    *keys : str
        The keys to navigate through.
    default : any
        Value to return if the key path does not exist.

    Returns
    -------
    any
        The value at the key path, or default.
    """
    current = config
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


# Usage example
config = load_config("config.yaml")

# Get values safely
data_path = get_nested(config, "data", "input_path")
n_estimators = get_nested(
    config, "model", "params", "n_estimators", default=100
)

print(f"Data path: {data_path}")
print(f"N estimators: {n_estimators}")
```

```
Output:
Data path: data/raw/dataset.csv
N estimators: 100
```

### Environment-Specific Configs

In the real world, you often need different settings for development and production:

```yaml
# config_dev.yaml - Development settings
data:
  input_path: "data/sample/small_dataset.csv"   # Small data for quick testing
model:
  params:
    n_estimators: 10   # Fewer trees = faster training

# config_prod.yaml - Production settings
data:
  input_path: "data/raw/full_dataset.csv"        # Full data
model:
  params:
    n_estimators: 500  # More trees = better accuracy
```

---

## Logging

Logging is like installing security cameras in a building. When something goes wrong, you can review the footage to figure out what happened.

### Logging Levels

Python's logging module has five levels, from least to most severe:

```
+--------------------------------------------------+
|  Logging Levels (least to most severe)           |
|                                                   |
|  DEBUG    -> Detailed info for debugging          |
|              "Processing row 42 of 1000"          |
|                                                   |
|  INFO     -> General progress updates             |
|              "Model training started"             |
|                                                   |
|  WARNING  -> Something unexpected but not fatal   |
|              "Missing values found in column age" |
|                                                   |
|  ERROR    -> Something failed                     |
|              "Could not load data file"           |
|                                                   |
|  CRITICAL -> The program cannot continue          |
|              "Database connection lost"           |
+--------------------------------------------------+
```

### Complete Logging Setup

```python
"""
logger_setup.py - Set up logging for the project.

This creates a logger that writes to both the console
(so you can see what is happening) and a file (so you
can review later).
"""

import logging
import os
from datetime import datetime


def setup_logger(
    name="ml_project",
    log_dir="logs",
    level=logging.INFO,
):
    """
    Set up a logger with console and file output.

    Parameters
    ----------
    name : str
        Name of the logger.
    log_dir : str
        Directory to store log files.
    level : int
        Minimum logging level (e.g., logging.INFO).

    Returns
    -------
    logging.Logger
        Configured logger.
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding handlers multiple times
    # (this can happen if setup_logger is called twice)
    if logger.handlers:
        return logger

    # Create log directory if it does not exist
    os.makedirs(log_dir, exist_ok=True)

    # Create a timestamp for the log file name
    # This way, each run gets its own log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"{name}_{timestamp}.log")

    # Define the format for log messages
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler - shows logs in the terminal
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # File handler - saves logs to a file
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)  # File gets more detail
    file_handler.setFormatter(formatter)

    # Add both handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.info(f"Logging to file: {log_file}")

    return logger


# Usage example
logger = setup_logger("my_ml_project")

logger.debug("This is a debug message (only in file)")
logger.info("Starting the ML pipeline")
logger.warning("Dataset has 5% missing values")
logger.error("Could not connect to database")
logger.critical("Out of memory!")
```

```
Output (console):
2024-01-15 10:30:45 | my_ml_project | INFO     | Logging to file: logs/my_ml_project_20240115_103045.log
2024-01-15 10:30:45 | my_ml_project | INFO     | Starting the ML pipeline
2024-01-15 10:30:45 | my_ml_project | WARNING  | Dataset has 5% missing values
2024-01-15 10:30:45 | my_ml_project | ERROR    | Could not connect to database
2024-01-15 10:30:45 | my_ml_project | CRITICAL | Out of memory!
```

Notice that the DEBUG message does not appear in the console output. That is because we set the console handler to INFO level. The file will contain all messages including DEBUG.

---

## Putting It All Together: Complete Refactored Project

Let us see the complete flow from notebook to production:

```
+--------------------------------------------------+
|  The Refactoring Journey                         |
|                                                   |
|  Notebook (messy)                                |
|       |                                           |
|       v                                           |
|  Identify logical groups                         |
|       |                                           |
|       v                                           |
|  Create module files (src/)                      |
|       |                                           |
|       v                                           |
|  Add error handling and logging                  |
|       |                                           |
|       v                                           |
|  Create config file                              |
|       |                                           |
|       v                                           |
|  Create main script (scripts/train.py)           |
|       |                                           |
|       v                                           |
|  Add tests (tests/)                              |
|       |                                           |
|       v                                           |
|  Production-ready code!                          |
+--------------------------------------------------+
```

### A Simple Test Example

```python
"""
test_data_loader.py - Tests for the data loader module.

Tests verify that your code works correctly. Think of
them as a safety net that catches bugs before they
reach production.
"""

import pytest
import pandas as pd
import os
import tempfile

# Import the functions we want to test
from src.data_loader import load_data, clean_data, split_data


def test_load_data_success():
    """Test that load_data works with a valid CSV file."""
    # Create a temporary CSV file for testing
    # tempfile creates a file that gets deleted automatically
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False
    ) as f:
        f.write("feature1,feature2,target\n")
        f.write("1,2,0\n")
        f.write("3,4,1\n")
        f.write("5,6,0\n")
        temp_path = f.name

    try:
        # Load the data
        df = load_data(temp_path)

        # Check that we got the right shape
        assert len(df) == 3, "Should have 3 rows"
        assert len(df.columns) == 3, "Should have 3 columns"
    finally:
        # Clean up the temporary file
        os.unlink(temp_path)


def test_load_data_file_not_found():
    """Test that load_data raises error for missing file."""
    with pytest.raises(FileNotFoundError):
        load_data("this_file_does_not_exist.csv")


def test_clean_data():
    """Test that clean_data removes rows with missing values."""
    # Create a DataFrame with some missing values
    df = pd.DataFrame(
        {
            "a": [1, 2, None, 4],
            "b": [5, None, 7, 8],
        }
    )

    # Clean it
    cleaned = clean_data(df)

    # Should have 2 rows (rows 0 and 3 have no missing values)
    assert len(cleaned) == 2


def test_split_data():
    """Test that split_data creates proper train/test split."""
    df = pd.DataFrame(
        {
            "feature1": range(100),
            "feature2": range(100, 200),
            "target": [0, 1] * 50,
        }
    )

    X_train, X_test, y_train, y_test = split_data(
        df, target_column="target", test_size=0.2
    )

    # Check sizes
    assert len(X_train) == 80, "Training set should be 80%"
    assert len(X_test) == 20, "Test set should be 20%"
    assert len(y_train) == 80
    assert len(y_test) == 20
```

```
Output (running pytest):
==================== test session starts ====================
collected 4 items

tests/test_data_loader.py::test_load_data_success PASSED
tests/test_data_loader.py::test_load_data_file_not_found PASSED
tests/test_data_loader.py::test_clean_data PASSED
tests/test_data_loader.py::test_split_data PASSED

==================== 4 passed in 0.52s ====================
```

---

## Common Mistakes

1. **Not using version control.** Always use git from the start. Even for personal projects.

2. **Hardcoding file paths.** Never write `df = pd.read_csv("/home/user/data.csv")`. Use configuration files or command-line arguments instead.

3. **Forgetting `if __name__ == "__main__"`.** Without this guard, your training code runs when you try to import functions from the file.

4. **Not handling errors.** Production code must anticipate what can go wrong. Files can be missing. Data can be corrupted. Models can fail.

5. **Skipping logging.** When your code runs on a server at 3 AM and fails, logs are your only way to figure out what happened.

6. **Keeping exploration code in production.** Remove `df.head()`, `print(df.shape)`, and other exploration code. Use logging instead.

---

## Best Practices

1. **Start with the end in mind.** Even when exploring in a notebook, think about how you will eventually organize the code.

2. **One function, one job.** Each function should do one thing well. `load_data()` loads data. `clean_data()` cleans data. Do not mix responsibilities.

3. **Write docstrings.** Future you will forget what your functions do. Write docstrings that explain parameters, return values, and examples.

4. **Use type hints.** They help editors catch bugs and make code more readable:

```python
def load_data(file_path: str) -> pd.DataFrame:
    ...
```

5. **Keep notebooks for exploration.** Notebooks are great for trying things out. But when code is ready for production, move it to `.py` files.

6. **Use a requirements.txt file.** List all packages your project needs. This helps others (and future you) set up the project.

---

## Quick Summary

Moving from notebook to production is about making your code reliable, maintainable, and runnable without you watching it. The key steps are:

- Organize your project with a clear folder structure
- Break notebook code into reusable Python modules
- Use configuration files for settings
- Add logging so you can track what happens
- Write tests to catch bugs early
- Handle errors gracefully

---

## Key Points

- Notebooks are great for exploration but poor for production
- Production code needs error handling, logging, and tests
- Configuration files separate settings from code
- Project structure makes code organized and findable
- Logging is your eyes and ears when code runs without you
- The `if __name__ == "__main__"` pattern prevents code from running on import
- Refactoring is about reorganizing, not rewriting

---

## Practice Questions

1. What are three problems with using Jupyter notebooks in production?

2. Why should you use a configuration file instead of hardcoding values like file paths and model parameters directly in your code?

3. What is the difference between `logging.INFO` and `logging.DEBUG`? When would you use each one?

4. Explain what `if __name__ == "__main__"` does and why it is important.

5. What is the purpose of the `__init__.py` file in the `src/` and `tests/` folders?

---

## Exercises

### Exercise 1: Refactor a Notebook

Take this notebook code and refactor it into proper production code with separate modules, a config file, and logging:

```python
# Notebook code
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

df = pd.read_csv("customers.csv")
df = df.dropna()
X = df[["age", "income", "score"]]
y = df["churned"]
model = LogisticRegression()
model.fit(X, y)
print(accuracy_score(y, model.predict(X)))
```

### Exercise 2: Add Error Handling

Write a function called `safe_load_data` that:
- Takes a file path as input
- Returns the loaded DataFrame if successful
- Returns `None` and logs a warning if the file does not exist
- Returns `None` and logs an error if the file is not a valid CSV

### Exercise 3: Create a Logging Dashboard

Write a script that reads a log file and prints a summary showing:
- Total number of log messages
- Count of each log level (INFO, WARNING, ERROR, etc.)
- The last 5 error messages

---

## What Is Next?

Now that you know how to organize code for production, the next step is learning how to save and load your trained models. In Chapter 2, we will explore different ways to save models (pickle, joblib, ONNX) so they can be loaded and used later without retraining. This is essential because training a model can take hours or days, and you do not want to retrain every time you need a prediction.
