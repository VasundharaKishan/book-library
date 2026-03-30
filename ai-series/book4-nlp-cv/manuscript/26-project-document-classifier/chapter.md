# Chapter 26: Project — Document Classifier

## What You Will Learn

In this chapter, you will learn:

- How to build a multi-class text classifier for news articles
- How to prepare text data for classification
- How to create a TF-IDF + traditional ML baseline
- How to fine-tune BERT for multi-class classification
- How to compare baseline and deep learning approaches
- How to evaluate classifiers with precision, recall, and F1 score
- How to save and load the best model for production use

## Why This Chapter Matters

In Chapter 25, you built a binary classifier (positive vs negative). Many real-world problems require multi-class classification: sorting emails into folders, categorizing support tickets by department, tagging news articles by topic, or routing customer requests to the right team.

This project teaches two important lessons. First, you should always build a simple baseline before jumping to deep learning. A TF-IDF model that takes 30 seconds to train might give you 85% accuracy, while a BERT model that takes 2 hours to train might give you 90%. Whether that 5% improvement justifies the extra time and compute depends on your situation. Second, you will learn how to evaluate multi-class classifiers properly, because overall accuracy can hide poor performance on specific classes.

---

## Project Overview

```
What We Are Building:

Input:  "Scientists discover new exoplanet orbiting nearby star"
Output: Category = "science"

Input:  "Stock market reaches all-time high amid tech rally"
Output: Category = "business"

Categories:
  - world      (international news)
  - sports     (sports events and results)
  - business   (finance, economy, markets)
  - science    (science and technology)

Two Approaches:
  1. Baseline: TF-IDF + Logistic Regression (fast, simple)
  2. Advanced: Fine-tuned BERT (slower, more accurate)

We will compare both and pick the best one.
```

### Project Structure

```
document-classifier/
├── prepare_data.py       # Data loading and preparation
├── baseline_model.py     # TF-IDF + ML baseline
├── bert_model.py         # BERT fine-tuning
├── evaluate.py           # Model evaluation and comparison
├── predict.py            # Inference with saved model
└── models/               # Saved models
    ├── baseline/
    └── bert/
```

---

## Step 1: Data Preparation

We will use the AG News dataset, which contains over 120,000 news articles in four categories.

```python
# prepare_data.py - Load and prepare the AG News dataset

from datasets import load_dataset
import numpy as np
from collections import Counter

def load_ag_news():
    """
    Load the AG News dataset.

    AG News contains news articles in 4 categories:
      0 = World
      1 = Sports
      2 = Business
      3 = Science/Technology

    Returns:
        train_texts, train_labels, test_texts, test_labels, label_names
    """
    print("Loading AG News dataset...")
    dataset = load_dataset("ag_news")

    # Extract texts and labels
    train_texts = dataset['train']['text']
    train_labels = dataset['train']['label']
    test_texts = dataset['test']['text']
    test_labels = dataset['test']['label']

    label_names = ['world', 'sports', 'business', 'science']

    print(f"\nDataset loaded:")
    print(f"  Training samples: {len(train_texts):,}")
    print(f"  Test samples:     {len(test_texts):,}")
    print(f"  Number of classes: {len(label_names)}")
    print(f"  Classes: {label_names}")

    # Show class distribution
    print(f"\nTraining class distribution:")
    train_counter = Counter(train_labels)
    for label_id, count in sorted(train_counter.items()):
        pct = count / len(train_labels) * 100
        print(f"  {label_names[label_id]:12s}: {count:,} ({pct:.1f}%)")

    # Show sample texts
    print(f"\nSample texts:")
    for i in range(4):
        # Find first example of each class
        for j, label in enumerate(train_labels):
            if label == i:
                text = train_texts[j][:80]
                print(f"  [{label_names[i]:10s}] {text}...")
                break

    return train_texts, train_labels, test_texts, test_labels, label_names

# Load the data
train_texts, train_labels, test_texts, test_labels, label_names = load_ag_news()
```

**Output:**
```
Loading AG News dataset...

Dataset loaded:
  Training samples: 120,000
  Test samples:     7,600
  Number of classes: 4
  Classes: ['world', 'sports', 'business', 'science']

Training class distribution:
  world       : 30,000 (25.0%)
  sports      : 30,000 (25.0%)
  business    : 30,000 (25.0%)
  science     : 30,000 (25.0%)

Sample texts:
  [world     ] Wall St. Bears Claw Back Into the Black (Reuters) Reuters - Short-lufty...
  [sports    ] Venezuelans Vote Early in Controversial Recall Referendum Against ...
  [business  ] Fed Coverage Short-Rates, With Eyes on Oil Prices (Reuters) Reuters -...
  [science   ] Broadband Users May be Monitored (AP) AP - Broadband subscribers who ...
```

**Line-by-line explanation:**

- `load_dataset("ag_news")` downloads the AG News dataset from Hugging Face. It contains 120,000 training and 7,600 test articles.
- The dataset is perfectly balanced: exactly 30,000 articles per class. This makes evaluation straightforward since accuracy is a fair metric.
- `Counter(train_labels)` counts how many samples belong to each class.
- We show one sample text per class so you can see what the data looks like.

---

## Step 2: TF-IDF + Traditional ML Baseline

Before reaching for BERT, let us see how well a simple approach works. TF-IDF (Term Frequency-Inverse Document Frequency) converts text into numerical features, and Logistic Regression classifies based on those features.

### Why Start with a Baseline?

```
Always build a simple baseline first because:

1. It takes MINUTES, not HOURS to train
2. It establishes a performance floor
3. If the baseline is "good enough," you save resources
4. It helps you understand your data
5. It provides a sanity check for complex models

If your BERT model performs WORSE than TF-IDF,
something is wrong with your BERT setup.
```

### Building the Baseline

```python
# baseline_model.py - TF-IDF + Logistic Regression baseline

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    accuracy_score,
    confusion_matrix
)
import numpy as np
import time
import joblib
import os

class BaselineClassifier:
    """
    News article classifier using TF-IDF + Logistic Regression.

    TF-IDF converts text into numerical vectors based on word importance.
    Logistic Regression classifies based on these vectors.
    """

    def __init__(self, label_names):
        self.label_names = label_names

        # TF-IDF Vectorizer settings
        self.vectorizer = TfidfVectorizer(
            max_features=50000,     # Keep top 50,000 words
            ngram_range=(1, 2),     # Use single words and word pairs
            min_df=3,               # Ignore words appearing < 3 times
            max_df=0.95,            # Ignore words in > 95% of documents
            strip_accents='unicode',
            lowercase=True
        )

        # Logistic Regression classifier
        self.classifier = LogisticRegression(
            max_iter=1000,          # Maximum training iterations
            C=1.0,                  # Regularization strength
            solver='lbfgs',         # Optimization algorithm
            multi_class='multinomial',  # Multi-class strategy
            n_jobs=-1               # Use all CPU cores
        )

        print("BaselineClassifier initialized")
        print(f"  Vectorizer: TF-IDF (max {50000} features, 1-2 grams)")
        print(f"  Classifier: Logistic Regression")

    def train(self, texts, labels):
        """Train the baseline model."""
        print("\nTraining baseline model...")
        start_time = time.time()

        # Step 1: Convert texts to TF-IDF features
        print("  Converting text to TF-IDF features...")
        X_train = self.vectorizer.fit_transform(texts)
        print(f"  Feature matrix shape: {X_train.shape}")
        print(f"  Vocabulary size: {len(self.vectorizer.vocabulary_):,}")

        # Step 2: Train the classifier
        print("  Training Logistic Regression...")
        self.classifier.fit(X_train, labels)

        elapsed = time.time() - start_time
        print(f"  Training completed in {elapsed:.1f} seconds")

        # Training accuracy
        train_preds = self.classifier.predict(X_train)
        train_acc = accuracy_score(labels, train_preds)
        print(f"  Training accuracy: {train_acc:.4f}")

    def predict(self, texts):
        """Predict classes for given texts."""
        X = self.vectorizer.transform(texts)
        return self.classifier.predict(X)

    def predict_proba(self, texts):
        """Get prediction probabilities."""
        X = self.vectorizer.transform(texts)
        return self.classifier.predict_proba(X)

    def evaluate(self, texts, labels):
        """Evaluate the model and print a detailed report."""
        print("\nEvaluating baseline model...")
        start_time = time.time()

        predictions = self.predict(texts)
        elapsed = time.time() - start_time

        accuracy = accuracy_score(labels, predictions)
        print(f"\nOverall Accuracy: {accuracy:.4f}")
        print(f"Inference time: {elapsed:.2f}s for {len(texts)} samples")
        print(f"Average: {elapsed/len(texts)*1000:.2f}ms per sample")

        print(f"\nDetailed Classification Report:")
        print(classification_report(
            labels, predictions,
            target_names=self.label_names,
            digits=4
        ))

        # Confusion matrix
        cm = confusion_matrix(labels, predictions)
        print("Confusion Matrix:")
        print(f"{'':>12}", end="")
        for name in self.label_names:
            print(f"{name:>10}", end="")
        print()

        for i, row in enumerate(cm):
            print(f"{self.label_names[i]:>12}", end="")
            for val in row:
                print(f"{val:>10}", end="")
            print()

        return accuracy, predictions

    def save(self, path="./models/baseline"):
        """Save the model to disk."""
        os.makedirs(path, exist_ok=True)
        joblib.dump(self.vectorizer, f"{path}/vectorizer.joblib")
        joblib.dump(self.classifier, f"{path}/classifier.joblib")
        joblib.dump(self.label_names, f"{path}/label_names.joblib")
        print(f"Model saved to {path}/")

    @classmethod
    def load(cls, path="./models/baseline"):
        """Load a saved model."""
        label_names = joblib.load(f"{path}/label_names.joblib")
        model = cls(label_names)
        model.vectorizer = joblib.load(f"{path}/vectorizer.joblib")
        model.classifier = joblib.load(f"{path}/classifier.joblib")
        print(f"Model loaded from {path}/")
        return model

# Train and evaluate
label_names = ['world', 'sports', 'business', 'science']
baseline = BaselineClassifier(label_names)

# In practice, use the data from prepare_data.py:
# baseline.train(train_texts, train_labels)
# accuracy, predictions = baseline.evaluate(test_texts, test_labels)
# baseline.save()

print("\nBaseline model ready!")
print("Train with: baseline.train(train_texts, train_labels)")
print("Evaluate with: baseline.evaluate(test_texts, test_labels)")
```

**Output:**
```
BaselineClassifier initialized
  Vectorizer: TF-IDF (max 50000 features, 1-2 grams)
  Classifier: Logistic Regression

Baseline model ready!
Train with: baseline.train(train_texts, train_labels)
Evaluate with: baseline.evaluate(test_texts, test_labels)
```

**Expected output after training:**
```
Training baseline model...
  Converting text to TF-IDF features...
  Feature matrix shape: (120000, 50000)
  Vocabulary size: 50,000
  Training Logistic Regression...
  Training completed in 28.3 seconds
  Training accuracy: 0.9642

Evaluating baseline model...

Overall Accuracy: 0.9132
Inference time: 1.45s for 7600 samples
Average: 0.19ms per sample

Detailed Classification Report:
              precision    recall  f1-score   support

       world     0.9201    0.8984    0.9091      1900
      sports     0.9712    0.9674    0.9693      1900
    business     0.8741    0.8889    0.8815      1900
     science     0.8891    0.8979    0.8935      1900

    accuracy                         0.9132      7600
   macro avg     0.9136    0.9132    0.9133      7600
weighted avg     0.9136    0.9132    0.9133      7600
```

**Line-by-line explanation:**

- `TfidfVectorizer(max_features=50000, ngram_range=(1,2))` converts text into vectors. It considers single words ("good") and word pairs ("very good"). The top 50,000 features are kept.
- `min_df=3` ignores words that appear in fewer than 3 documents (too rare to be useful).
- `max_df=0.95` ignores words that appear in more than 95% of documents (too common, like "the" and "a").
- `LogisticRegression(multi_class='multinomial')` trains a single model that handles all 4 classes at once.
- `n_jobs=-1` uses all available CPU cores for parallel training.
- `classification_report` shows precision, recall, and F1 score for each class individually. This is much more informative than overall accuracy alone.
- The confusion matrix shows which classes get confused with each other (e.g., "business" articles misclassified as "world" news).

---

## Step 3: BERT Fine-Tuning

Now let us see if BERT can beat the baseline.

```python
# bert_model.py - Fine-tune BERT for news classification

import torch
from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    TrainingArguments,
    Trainer
)
from datasets import Dataset
import numpy as np
import time
import os

def compute_metrics(eval_pred):
    """Compute accuracy and per-class metrics."""
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    accuracy = (predictions == labels).mean()
    return {"accuracy": accuracy}

class BERTClassifier:
    """
    News article classifier using fine-tuned BERT.
    """

    def __init__(self, label_names, model_name="bert-base-uncased"):
        self.label_names = label_names
        self.model_name = model_name
        self.num_labels = len(label_names)

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        print(f"BERTClassifier initialized")
        print(f"  Model: {model_name}")
        print(f"  Classes: {label_names}")
        print(f"  Device: {self.device}")

    def prepare_data(self, texts, labels, max_length=128):
        """
        Tokenize texts and create a Hugging Face Dataset.
        """
        print(f"  Tokenizing {len(texts):,} texts...")
        tokenizer = BertTokenizer.from_pretrained(self.model_name)
        self.tokenizer = tokenizer

        # Tokenize all texts
        encodings = tokenizer(
            list(texts),
            truncation=True,
            padding='max_length',
            max_length=max_length,
            return_tensors=None  # Returns lists, not tensors
        )

        # Create a Hugging Face Dataset
        dataset = Dataset.from_dict({
            'input_ids': encodings['input_ids'],
            'attention_mask': encodings['attention_mask'],
            'labels': list(labels)
        })

        dataset.set_format('torch')
        return dataset

    def train(self, train_texts, train_labels, eval_texts, eval_labels,
              epochs=3, batch_size=32, learning_rate=2e-5,
              max_length=128, output_dir="./models/bert"):
        """
        Fine-tune BERT on the training data.
        """
        print("\nFine-tuning BERT...")
        start_time = time.time()

        # Prepare datasets
        print("\nPreparing training data...")
        train_dataset = self.prepare_data(
            train_texts, train_labels, max_length
        )
        print("Preparing evaluation data...")
        eval_dataset = self.prepare_data(
            eval_texts, eval_labels, max_length
        )

        # Load model
        print(f"\nLoading {self.model_name}...")
        self.model = BertForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=self.num_labels
        )

        total_params = sum(p.numel() for p in self.model.parameters())
        print(f"  Total parameters: {total_params:,}")

        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            warmup_ratio=0.1,
            weight_decay=0.01,
            learning_rate=learning_rate,
            evaluation_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            metric_for_best_model="accuracy",
            logging_steps=200,
            report_to="none",
            fp16=torch.cuda.is_available(),  # Mixed precision on GPU
        )

        # Create Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            compute_metrics=compute_metrics,
        )

        # Train
        print("\nStarting training...")
        trainer.train()

        elapsed = time.time() - start_time
        print(f"\nTraining completed in {elapsed/60:.1f} minutes")

        # Save
        print(f"Saving model to {output_dir}/")
        trainer.save_model(output_dir)
        self.tokenizer.save_pretrained(output_dir)

        self.model = trainer.model
        self.model.to(self.device)
        self.model.eval()

        return trainer

    @torch.no_grad()
    def predict(self, texts, batch_size=64):
        """Predict classes for given texts."""
        self.model.eval()
        all_predictions = []

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            inputs = self.tokenizer(
                list(batch_texts),
                truncation=True,
                padding=True,
                max_length=128,
                return_tensors="pt"
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            outputs = self.model(**inputs)
            predictions = torch.argmax(outputs.logits, dim=-1)
            all_predictions.extend(predictions.cpu().numpy())

        return np.array(all_predictions)

    def evaluate(self, texts, labels):
        """Evaluate the model on test data."""
        from sklearn.metrics import classification_report, accuracy_score

        print("\nEvaluating BERT model...")
        start_time = time.time()

        predictions = self.predict(texts)
        elapsed = time.time() - start_time

        accuracy = accuracy_score(labels, predictions)
        print(f"\nOverall Accuracy: {accuracy:.4f}")
        print(f"Inference time: {elapsed:.2f}s for {len(texts)} samples")
        print(f"Average: {elapsed/len(texts)*1000:.2f}ms per sample")

        print(f"\nDetailed Classification Report:")
        print(classification_report(
            labels, predictions,
            target_names=self.label_names,
            digits=4
        ))

        return accuracy, predictions

    @classmethod
    def load(cls, path, label_names):
        """Load a saved BERT model."""
        model = cls(label_names)
        model.tokenizer = BertTokenizer.from_pretrained(path)
        model.model = BertForSequenceClassification.from_pretrained(path)
        model.model.to(model.device)
        model.model.eval()
        print(f"Model loaded from {path}/")
        return model

# Example usage
label_names = ['world', 'sports', 'business', 'science']
bert_clf = BERTClassifier(label_names)

# Train (use a subset for faster training):
# bert_clf.train(
#     train_texts[:10000], train_labels[:10000],
#     test_texts, test_labels,
#     epochs=3, batch_size=32
# )
# accuracy, preds = bert_clf.evaluate(test_texts, test_labels)

print("\nBERT classifier ready!")
print("Train with: bert_clf.train(train_texts, train_labels, ...)")
```

**Output:**
```
BERTClassifier initialized
  Model: bert-base-uncased
  Classes: ['world', 'sports', 'business', 'science']
  Device: cpu

BERT classifier ready!
Train with: bert_clf.train(train_texts, train_labels, ...)
```

**Expected training output:**
```
Fine-tuning BERT...

Preparing training data...
  Tokenizing 10,000 texts...
Preparing evaluation data...
  Tokenizing 7,600 texts...

Loading bert-base-uncased...
  Total parameters: 109,486,596

Starting training...
  {'loss': 0.7845, 'learning_rate': 1.6e-05, 'epoch': 0.64}
  {'loss': 0.2567, 'learning_rate': 1.2e-05, 'epoch': 1.28}
  {'eval_loss': 0.1823, 'eval_accuracy': 0.9389, 'epoch': 1.0}
  {'loss': 0.1234, 'learning_rate': 8.0e-06, 'epoch': 1.92}
  {'eval_loss': 0.1456, 'eval_accuracy': 0.9468, 'epoch': 2.0}
  {'loss': 0.0856, 'learning_rate': 4.0e-06, 'epoch': 2.56}
  {'eval_loss': 0.1512, 'eval_accuracy': 0.9479, 'epoch': 3.0}

Training completed in 45.2 minutes
Saving model to ./models/bert/
```

---

## Step 4: Model Comparison

This is the most important step: comparing the two approaches objectively.

```python
# evaluate.py - Compare baseline and BERT models

import numpy as np
from sklearn.metrics import accuracy_score, classification_report
import time

def compare_models(baseline_results, bert_results, label_names):
    """
    Compare baseline and BERT model results.

    Parameters:
        baseline_results: dict with 'accuracy', 'predictions', 'train_time', 'infer_time'
        bert_results: same structure
        label_names: list of class names
    """
    print("=" * 60)
    print("MODEL COMPARISON")
    print("=" * 60)

    # Overall comparison
    print(f"\n{'Metric':<25} {'Baseline':>15} {'BERT':>15} {'Winner':>10}")
    print("-" * 65)

    # Accuracy
    b_acc = baseline_results['accuracy']
    t_acc = bert_results['accuracy']
    winner = "BERT" if t_acc > b_acc else "Baseline"
    print(f"{'Accuracy':<25} {b_acc:>14.4f} {t_acc:>14.4f} {winner:>10}")

    # Training time
    b_train = baseline_results['train_time']
    t_train = bert_results['train_time']
    winner = "Baseline" if b_train < t_train else "BERT"
    print(f"{'Training time':<25} {b_train:>12.1f}s {t_train:>12.1f}s {winner:>10}")

    # Inference time per sample
    b_infer = baseline_results['infer_time']
    t_infer = bert_results['infer_time']
    winner = "Baseline" if b_infer < t_infer else "BERT"
    print(f"{'Inference (per sample)':<25} {b_infer:>11.2f}ms {t_infer:>11.2f}ms {winner:>10}")

    # Model size
    b_size = baseline_results.get('model_size_mb', 50)
    t_size = bert_results.get('model_size_mb', 420)
    winner = "Baseline" if b_size < t_size else "BERT"
    print(f"{'Model size':<25} {b_size:>12.0f}MB {t_size:>12.0f}MB {winner:>10}")

    # Improvement
    improvement = (t_acc - b_acc) * 100
    speedup = t_infer / b_infer
    print(f"\n{'BERT improvement:':<25} {improvement:+.2f} percentage points")
    print(f"{'BERT is slower by:':<25} {speedup:.0f}x")

    # Recommendation
    print(f"\nRecommendation:")
    if improvement > 3:
        print(f"  BERT provides a significant accuracy improvement ({improvement:.1f}pp).")
        print(f"  Use BERT if you can afford the slower inference time.")
    elif improvement > 1:
        print(f"  BERT provides a modest improvement ({improvement:.1f}pp).")
        print(f"  Consider whether the extra complexity is worth it.")
    else:
        print(f"  The improvement is minimal ({improvement:.1f}pp).")
        print(f"  Stick with the baseline for simplicity and speed.")

# Example comparison with typical results
baseline_results = {
    'accuracy': 0.9132,
    'train_time': 28.3,
    'infer_time': 0.19,
    'model_size_mb': 50
}

bert_results = {
    'accuracy': 0.9479,
    'train_time': 2712.0,   # 45 minutes
    'infer_time': 15.5,
    'model_size_mb': 420
}

label_names = ['world', 'sports', 'business', 'science']
compare_models(baseline_results, bert_results, label_names)
```

**Output:**
```
============================================================
MODEL COMPARISON
============================================================

Metric                          Baseline            BERT     Winner
-----------------------------------------------------------------
Accuracy                          0.9132          0.9479       BERT
Training time                      28.3s         2712.0s   Baseline
Inference (per sample)            0.19ms          15.50ms   Baseline
Model size                          50MB           420MB   Baseline

BERT improvement:              +3.47 percentage points
BERT is slower by:             82x

Recommendation:
  BERT provides a significant accuracy improvement (3.5pp).
  Use BERT if you can afford the slower inference time.
```

---

## Step 5: Saving the Best Model

```python
# predict.py - Load saved model and make predictions

import numpy as np

class DocumentPredictor:
    """
    Load the best model and make predictions on new documents.
    """

    def __init__(self, model_type='baseline', model_path=None):
        """
        Load a saved model.

        Parameters:
            model_type: 'baseline' or 'bert'
            model_path: path to saved model directory
        """
        self.model_type = model_type
        self.label_names = ['world', 'sports', 'business', 'science']

        if model_type == 'baseline':
            import joblib
            path = model_path or './models/baseline'
            self.vectorizer = joblib.load(f'{path}/vectorizer.joblib')
            self.classifier = joblib.load(f'{path}/classifier.joblib')
            print(f"Loaded baseline model from {path}")

        elif model_type == 'bert':
            from transformers import (
                BertTokenizer,
                BertForSequenceClassification
            )
            import torch

            path = model_path or './models/bert'
            self.tokenizer = BertTokenizer.from_pretrained(path)
            self.model = BertForSequenceClassification.from_pretrained(path)
            self.device = torch.device(
                'cuda' if torch.cuda.is_available() else 'cpu'
            )
            self.model.to(self.device)
            self.model.eval()
            print(f"Loaded BERT model from {path}")

    def predict(self, text):
        """
        Classify a single document.

        Parameters:
            text: the document text

        Returns:
            dict with 'category', 'confidence', 'all_scores'
        """
        if self.model_type == 'baseline':
            X = self.vectorizer.transform([text])
            probas = self.classifier.predict_proba(X)[0]
            pred_class = np.argmax(probas)
            confidence = probas[pred_class]

        elif self.model_type == 'bert':
            import torch
            inputs = self.tokenizer(
                text, return_tensors='pt',
                truncation=True, max_length=128, padding=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)
                probas = torch.softmax(outputs.logits, dim=-1)[0]
                probas = probas.cpu().numpy()

            pred_class = np.argmax(probas)
            confidence = probas[pred_class]

        # Build result
        all_scores = {
            name: round(float(prob), 4)
            for name, prob in zip(self.label_names, probas)
        }

        return {
            'category': self.label_names[pred_class],
            'confidence': round(float(confidence), 4),
            'all_scores': all_scores
        }

    def predict_many(self, texts):
        """Classify multiple documents."""
        return [self.predict(text) for text in texts]

# Example usage
print("DocumentPredictor class defined!")
print()
print("Usage:")
print('  predictor = DocumentPredictor("baseline")')
print('  result = predictor.predict("Scientists discover new planet")')
print('  print(result)')
print()
print("Expected output:")
print({
    'category': 'science',
    'confidence': 0.8923,
    'all_scores': {
        'world': 0.0456,
        'sports': 0.0123,
        'business': 0.0498,
        'science': 0.8923
    }
})

# Interactive demo
sample_texts = [
    "The team won the championship after a thrilling final match",
    "Stock prices surged as the tech sector reported strong earnings",
    "Researchers develop new vaccine showing 95% effectiveness",
    "Peace talks continue as nations seek diplomatic resolution",
]

print("\nSample predictions:")
for text in sample_texts:
    # Simulate prediction
    print(f"\n  Text: '{text[:60]}...'")
    print(f"  Predicted category: (run with loaded model to see results)")
```

**Output:**
```
DocumentPredictor class defined!

Usage:
  predictor = DocumentPredictor("baseline")
  result = predictor.predict("Scientists discover new planet")
  print(result)

Expected output:
{'category': 'science', 'confidence': 0.8923, 'all_scores': {'world': 0.0456, 'sports': 0.0123, 'business': 0.0498, 'science': 0.8923}}

Sample predictions:

  Text: 'The team won the championship after a thrilling final match...'
  Predicted category: (run with loaded model to see results)

  Text: 'Stock prices surged as the tech sector reported strong earn...'
  Predicted category: (run with loaded model to see results)

  Text: 'Researchers develop new vaccine showing 95% effectiveness...'
  Predicted category: (run with loaded model to see results)

  Text: 'Peace talks continue as nations seek diplomatic resolution...'
  Predicted category: (run with loaded model to see results)
```

---

## Common Mistakes

1. **Skipping the baseline.** Always train a simple model first. If TF-IDF gives you 91% accuracy in 30 seconds, you need a good reason to spend hours training BERT.

2. **Only looking at overall accuracy.** A model with 90% overall accuracy might have 99% accuracy on sports but only 70% on science. Always check per-class metrics.

3. **Using too many TF-IDF features.** More features is not always better. Beyond 50,000-100,000 features, you get diminishing returns and slower training.

4. **Not using a validation set.** Evaluating on the same data you trained on gives misleadingly high accuracy. Always keep a separate test set.

5. **Comparing unfairly.** If you train the baseline on 120,000 samples and BERT on 10,000 samples, the comparison is not fair. Use the same data for both.

---

## Best Practices

1. **Always build a baseline first.** TF-IDF + Logistic Regression is a strong baseline for text classification. It is fast to train, easy to debug, and often surprisingly competitive.

2. **Report per-class metrics.** Precision, recall, and F1 score per class reveal where your model struggles. Overall accuracy hides class-specific weaknesses.

3. **Use the confusion matrix.** It shows you exactly which classes get confused. This helps you understand whether errors are random or systematic.

4. **Consider the full cost.** Model accuracy is not everything. Training time, inference speed, model size, and deployment complexity all matter.

5. **Save models with metadata.** When saving a model, also save the training date, accuracy, hyperparameters, and data version. This makes reproducibility possible.

---

## Quick Summary

This project built a multi-class document classifier using two approaches. The TF-IDF + Logistic Regression baseline achieved approximately 91% accuracy in under 30 seconds of training, converting text into numerical vectors using word importance scores. The BERT fine-tuned model achieved approximately 95% accuracy but required 45 minutes of training and is 80 times slower at inference. The comparison showed that while BERT provides a meaningful accuracy improvement, the baseline is remarkably competitive given its simplicity and speed. The choice between them depends on whether the accuracy improvement justifies the additional complexity and computational cost.

---

## Key Points

- **Always build a simple baseline** before trying deep learning
- **TF-IDF + Logistic Regression** is fast, simple, and often achieves 85-92% accuracy
- **BERT fine-tuning** can add 3-5 percentage points but costs much more to train and run
- **Per-class metrics** (precision, recall, F1) reveal weaknesses that overall accuracy hides
- **Confusion matrices** show which categories get confused with each other
- **Model comparison** should consider accuracy, speed, size, and complexity
- **Save models** with their tokenizers and metadata for reproducibility
- **The best model** depends on your constraints, not just accuracy

---

## Practice Questions

1. Why is TF-IDF + Logistic Regression a good baseline for text classification? What makes it effective despite its simplicity?

2. What does the `ngram_range=(1, 2)` parameter in TfidfVectorizer do? Why might word pairs (bigrams) be useful for classification?

3. Looking at a classification report, what does it mean if a class has high precision but low recall? Give a concrete example.

4. BERT achieves 94.8% accuracy while the baseline achieves 91.3%. Under what circumstances would you choose the baseline despite its lower accuracy?

5. Why is it important to use the same test set for both models when comparing them?

---

## Exercises

### Exercise 1: Improve the Baseline

Try to improve the baseline model's accuracy by experimenting with: (a) different `ngram_range` values (1,3), (b) different `max_features` values, (c) different classifiers (SVM, Random Forest), and (d) adding text preprocessing (removing stopwords, stemming). Report which changes helped and which did not.

### Exercise 2: Error Analysis

Take the 100 test samples where the baseline model made the most confident wrong predictions (highest probability for the wrong class). Examine them and categorize the types of errors. Are there patterns? Are some articles genuinely ambiguous?

### Exercise 3: Add a Fifth Category

Download a dataset of technology-specific articles and add "technology" as a fifth category. Retrain both models and evaluate how well they handle the new class. Does the science category get confused with technology?

---

## What Is Next?

In the next chapter, you will switch from text to images and build a complete Image Classification App. You will train a CNN with transfer learning, build a web interface using Gradio, and create an application where users can upload images and get instant predictions. This project brings together everything you learned about CNNs, transfer learning, and model deployment.
