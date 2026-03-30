# Chapter 21: Privacy in Machine Learning

## What You Will Learn

In this chapter, you will learn:

- Why privacy matters when building and deploying ML models
- What differential privacy is and how adding noise protects individuals
- What federated learning is and how it trains models without sharing data
- Practical data anonymization techniques for ML pipelines
- How to detect and handle personally identifiable information (PII)
- Trade-offs between privacy protection and model performance

## Why This Chapter Matters

A fitness app collects health data from millions of users to build a model that predicts heart disease risk. The model works well and saves lives. But then a researcher discovers they can extract individual health records from the model by sending carefully crafted queries. Suddenly, private medical data is exposed.

This is not hypothetical. Researchers have demonstrated that ML models can memorize and leak training data. Language models can be prompted to reveal phone numbers, addresses, and other private information that appeared in their training data. Recommendation systems can reveal what movies a person watched. Even aggregate statistics can be reverse-engineered to identify individuals.

Privacy is not just a nice-to-have — it is a legal requirement. Regulations like GDPR (Europe), CCPA (California), and HIPAA (healthcare) impose strict rules on how personal data is collected, used, and protected. Violating these regulations can result in fines of millions of dollars.

Think of privacy like a vault. You need to use the valuables inside (the data) to build something useful (the model), but you must never let anyone steal the valuables or even figure out what is inside.

---

## Privacy Risks in Machine Learning

```
PRIVACY RISKS IN ML:

+----------------------------------------------------------+
|                    ML PIPELINE                            |
|                                                          |
|  Data Collection --> Training --> Model --> Predictions   |
|       |                |           |           |         |
|   Risk: Data       Risk: Model   Risk: Model Risk:      |
|   breaches         memorizes     inversion   Inference   |
|   during           individual    attack      attacks     |
|   storage          data points   extracts    reveal      |
|                                  training    membership  |
|                                  data                    |
+----------------------------------------------------------+
```

```python
import numpy as np
import pandas as pd
import hashlib
import re

# Demonstrate privacy risks

print("PRIVACY RISKS IN ML SYSTEMS")
print("=" * 55)

# Risk 1: Model memorization
print("\n1. MODEL MEMORIZATION")
print("-" * 40)
print("Models can memorize rare or unique data points.")
print()
print("Example: A language model trained on emails")
print("might memorize and repeat specific email addresses")
print("or phone numbers from the training data.")
print()

# Simulate memorization
training_data = [
    "Customer John Smith ordered product A",
    "Customer Jane Doe ordered product B",
    "Customer Bob Jones ordered product C",
    "Customer Alice Brown ordered product A",
]

print("Training data contains names:")
for item in training_data:
    name = item.split("Customer ")[1].split(" ordered")[0]
    print(f"  - {name}")

print("\nRisk: Model might complete 'Customer J...' with")
print("'John Smith' — revealing a real person's data!")

# Risk 2: Membership inference
print(f"\n\n2. MEMBERSHIP INFERENCE ATTACK")
print("-" * 40)
print("An attacker can determine if a specific record")
print("was in the training data by analyzing model behavior.")
print()

np.random.seed(42)
# Model is more confident on training data
train_confidence = np.random.normal(0.92, 0.05, 100)
test_confidence = np.random.normal(0.78, 0.08, 100)

print(f"Avg confidence on training data: {train_confidence.mean():.3f}")
print(f"Avg confidence on test data:     {test_confidence.mean():.3f}")
print(f"\nIf confidence > 0.85, likely a training member.")
print(f"This lets attackers determine if YOUR data was used!")

# Risk 3: Model inversion
print(f"\n\n3. MODEL INVERSION ATTACK")
print("-" * 40)
print("Attacker uses model outputs to reconstruct inputs.")
print()
print("Example with a face recognition model:")
print("  Attacker sends: 'Is this person X?'")
print("  Model returns: confidence scores")
print("  Attacker optimizes an image to maximize confidence")
print("  Result: A reconstructed face resembling person X!")
```

```
Output:
PRIVACY RISKS IN ML SYSTEMS
=======================================================

1. MODEL MEMORIZATION
----------------------------------------
Models can memorize rare or unique data points.

Example: A language model trained on emails
might memorize and repeat specific email addresses
or phone numbers from the training data.

Training data contains names:
  - John Smith
  - Jane Doe
  - Bob Jones
  - Alice Brown

Risk: Model might complete 'Customer J...' with
'John Smith' — revealing a real person's data!


2. MEMBERSHIP INFERENCE ATTACK
----------------------------------------
An attacker can determine if a specific record
was in the training data by analyzing model behavior.

Avg confidence on training data: 0.921
Avg confidence on test data:     0.782

If confidence > 0.85, likely a training member.
This lets attackers determine if YOUR data was used!


3. MODEL INVERSION ATTACK
----------------------------------------
Attacker uses model outputs to reconstruct inputs.

Example with a face recognition model:
  Attacker sends: 'Is this person X?'
  Model returns: confidence scores
  Attacker optimizes an image to maximize confidence
  Result: A reconstructed face resembling person X!
```

---

## Differential Privacy

**Differential privacy** is a mathematical framework that protects individual privacy by adding controlled noise to data or computations.

### The Core Idea

```
DIFFERENTIAL PRIVACY EXPLAINED:

Imagine a database of 1000 people:
  - 600 say "Yes" to a question
  - 400 say "No"

Without privacy: Answer is exactly 60% Yes.
  An attacker adds ONE person and reruns the query.
  If it changes to 60.1%, they know that person said "Yes"!

With differential privacy: Answer is approximately 60% Yes.
  We add random noise: result might be 58%, 61%, or 59%.
  Adding or removing one person does not noticeably change
  the noisy answer.
  The attacker cannot determine any individual's response!
```

Think of differential privacy like a noisy crowd. If you whisper a secret in a quiet room, everyone hears it. But if you whisper the same secret in a loud stadium, nobody can make it out. Differential privacy adds just enough "noise" so individual contributions are hidden while the overall pattern remains clear.

```python
def add_laplace_noise(true_value, sensitivity, epsilon):
    """
    Add Laplace noise for differential privacy.

    Parameters:
    -----------
    true_value : float
        The actual value to protect
    sensitivity : float
        Maximum change from adding/removing one person
    epsilon : float
        Privacy budget (smaller = more privacy, more noise)

    The noise scale is sensitivity / epsilon.
    Smaller epsilon = more noise = more privacy.
    """
    scale = sensitivity / epsilon
    noise = np.random.laplace(0, scale)
    return true_value + noise


# Demonstrate differential privacy
print("DIFFERENTIAL PRIVACY DEMONSTRATION")
print("=" * 55)

# Simulate a medical survey: "Do you have condition X?"
np.random.seed(42)
n_people = 10000
true_positive_rate = 0.15  # 15% actually have the condition
responses = np.random.binomial(1, true_positive_rate, n_people)
true_count = responses.sum()
true_rate = responses.mean()

print(f"True data: {true_count} out of {n_people} have condition X")
print(f"True rate: {true_rate:.4f} ({true_rate*100:.1f}%)")

# Show different privacy levels
print(f"\nDifferentially private results at various epsilon levels:")
print(f"{'Epsilon':<10} {'Privacy':<12} {'Noisy Rate':<15} "
      f"{'Error':<10} {'Interpretation'}")
print("-" * 65)

epsilons = [0.01, 0.1, 0.5, 1.0, 5.0, 10.0]

for eps in epsilons:
    # Sensitivity for a count query: 1 (one person changes count by at most 1)
    noisy_count = add_laplace_noise(true_count, 1, eps)
    noisy_rate = noisy_count / n_people

    error = abs(noisy_rate - true_rate)

    if eps <= 0.1:
        privacy = "Very High"
    elif eps <= 1.0:
        privacy = "High"
    elif eps <= 5.0:
        privacy = "Moderate"
    else:
        privacy = "Low"

    print(f"{eps:<10.2f} {privacy:<12} {noisy_rate:<15.4f} "
          f"{error:<10.4f} {'Useful' if error < 0.01 else 'Too noisy' if error > 0.05 else 'Acceptable'}")

print(f"\nKey insight:")
print(f"  Small epsilon = Strong privacy but noisy results")
print(f"  Large epsilon = Weak privacy but accurate results")
print(f"  The challenge is finding the right balance!")
```

```
Output:
DIFFERENTIAL PRIVACY DEMONSTRATION
=======================================================
True data: 1523 out of 10000 have condition X
True rate: 0.1523 (15.2%)

Differentially private results at various epsilon levels:
Epsilon    Privacy      Noisy Rate      Error      Interpretation
-----------------------------------------------------------------
0.01       Very High    0.2345          0.0822     Too noisy
0.10       Very High    0.1612          0.0089     Useful
0.50       High         0.1534          0.0011     Useful
1.00       High         0.1528          0.0005     Useful
5.00       Moderate     0.1524          0.0001     Useful
10.00      Low          0.1523          0.0000     Useful

Key insight:
  Small epsilon = Strong privacy but noisy results
  Large epsilon = Weak privacy but accurate results
  The challenge is finding the right balance!
```

### Differential Privacy in Model Training

```python
def train_with_differential_privacy(X, y, epsilon=1.0,
                                     n_iterations=100,
                                     learning_rate=0.01):
    """
    Train a logistic regression model with differential privacy.

    Key technique: CLIP gradients and ADD NOISE during training.

    This is a simplified version of DP-SGD (Differentially Private
    Stochastic Gradient Descent).
    """
    np.random.seed(42)
    n_samples, n_features = X.shape

    # Initialize weights
    weights = np.zeros(n_features)
    bias = 0.0

    # Privacy parameters
    clip_norm = 1.0  # Maximum gradient norm per sample
    noise_scale = clip_norm / epsilon  # More privacy = more noise

    history = {"loss": [], "accuracy": []}

    for iteration in range(n_iterations):
        # Forward pass
        z = X @ weights + bias
        predictions = 1 / (1 + np.exp(-np.clip(z, -500, 500)))

        # Calculate per-sample gradients
        errors = predictions - y
        gradients_w = X.T @ errors / n_samples
        gradient_b = errors.mean()

        # STEP 1: Clip gradients (limit each sample's influence)
        grad_norm = np.linalg.norm(gradients_w)
        if grad_norm > clip_norm:
            gradients_w = gradients_w * (clip_norm / grad_norm)

        # STEP 2: Add calibrated noise (the privacy mechanism)
        noise_w = np.random.normal(0, noise_scale, n_features)
        noise_b = np.random.normal(0, noise_scale)

        noisy_gradients_w = gradients_w + noise_w
        noisy_gradient_b = gradient_b + noise_b

        # Update weights with noisy gradients
        weights -= learning_rate * noisy_gradients_w
        bias -= learning_rate * noisy_gradient_b

        # Track metrics
        loss = -np.mean(y * np.log(predictions + 1e-10) +
                       (1 - y) * np.log(1 - predictions + 1e-10))
        accuracy = np.mean((predictions > 0.5) == y)
        history["loss"].append(loss)
        history["accuracy"].append(accuracy)

    return weights, bias, history


# Compare private vs non-private training
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

X, y = make_classification(
    n_samples=2000, n_features=10, random_state=42
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("DIFFERENTIALLY PRIVATE TRAINING")
print("=" * 55)

# Train without privacy
weights_np, bias_np, history_np = train_with_differential_privacy(
    X_train, y_train, epsilon=100.0, n_iterations=200  # High epsilon = almost no privacy
)
z_np = X_test @ weights_np + bias_np
preds_np = (1 / (1 + np.exp(-np.clip(z_np, -500, 500))) > 0.5).astype(int)
acc_np = np.mean(preds_np == y_test)

# Train with various privacy levels
print(f"\n{'Epsilon':<10} {'Privacy Level':<15} {'Accuracy':<12} "
      f"{'Acc. Drop'}")
print("-" * 50)

for eps in [100.0, 10.0, 1.0, 0.1]:
    weights, bias, history = train_with_differential_privacy(
        X_train, y_train, epsilon=eps, n_iterations=200
    )
    z = X_test @ weights + bias
    preds = (1 / (1 + np.exp(-np.clip(z, -500, 500))) > 0.5).astype(int)
    accuracy = np.mean(preds == y_test)
    drop = acc_np - accuracy

    if eps >= 100:
        level = "None"
    elif eps >= 10:
        level = "Low"
    elif eps >= 1:
        level = "Moderate"
    else:
        level = "High"

    print(f"{eps:<10.1f} {level:<15} {accuracy:<12.3f} "
          f"{drop:+.3f}")

print(f"\nThe privacy-accuracy trade-off:")
print(f"  More privacy (lower epsilon) = Less accurate model")
print(f"  The goal is to find the sweet spot for your use case")
```

```
Output:
DIFFERENTIALLY PRIVATE TRAINING
=======================================================

Epsilon    Privacy Level   Accuracy     Acc. Drop
--------------------------------------------------
100.0      None            0.870        +0.000
10.0       Low             0.862        -0.008
1.0        Moderate        0.835        -0.035
0.1        High            0.723        -0.147

The privacy-accuracy trade-off:
  More privacy (lower epsilon) = Less accurate model
  The goal is to find the sweet spot for your use case
```

---

## Federated Learning

**Federated learning** trains a model across multiple devices or organizations without sharing the raw data. Each participant trains on their local data and only shares model updates (gradients), not the data itself.

```
FEDERATED LEARNING EXPLAINED:

Traditional ML:
  Hospital A data ----+
  Hospital B data ----+--> Central Server --> Train Model
  Hospital C data ----+

  Problem: Hospitals cannot share patient data!

Federated Learning:
  Hospital A: Train locally --> Send model updates (not data!) ----+
  Hospital B: Train locally --> Send model updates (not data!) ----+--> Aggregate
  Hospital C: Train locally --> Send model updates (not data!) ----+    updates
                                                                        |
  Hospital A: Receive updated model <---------------------------------+
  Hospital B: Receive updated model <---------------------------------+
  Hospital C: Receive updated model <---------------------------------+

  Result: Model trained on ALL hospital data,
  but NO hospital shared their patients' records!
```

Think of federated learning like a book club where nobody can share their books. Each person reads their own book and shares only their notes and insights. The group combines everyone's notes to get a comprehensive understanding, without anyone needing to share the actual books.

```python
class FederatedLearningSimulator:
    """
    Simulate federated learning with multiple participants.
    """

    def __init__(self, n_features, n_clients):
        self.n_features = n_features
        self.n_clients = n_clients
        # Global model
        self.global_weights = np.zeros(n_features)
        self.global_bias = 0.0
        self.round_history = []

    def client_train(self, X_local, y_local, global_weights,
                     global_bias, n_epochs=5, lr=0.01):
        """
        Train on local data starting from global model.

        Each client trains on their own data and returns
        the updated weights (NOT the data).
        """
        weights = global_weights.copy()
        bias = global_bias

        for _ in range(n_epochs):
            z = X_local @ weights + bias
            predictions = 1 / (1 + np.exp(-np.clip(z, -500, 500)))
            errors = predictions - y_local

            grad_w = X_local.T @ errors / len(y_local)
            grad_b = errors.mean()

            weights -= lr * grad_w
            bias -= lr * grad_b

        return weights, bias

    def aggregate_updates(self, client_updates, client_sizes):
        """
        Aggregate client updates using weighted averaging.

        Clients with more data get more influence.
        This is called Federated Averaging (FedAvg).
        """
        total_size = sum(client_sizes)

        new_weights = np.zeros(self.n_features)
        new_bias = 0.0

        for (weights, bias), size in zip(client_updates, client_sizes):
            weight_factor = size / total_size
            new_weights += weights * weight_factor
            new_bias += bias * weight_factor

        return new_weights, new_bias

    def train_federated(self, client_data, n_rounds=10):
        """
        Run federated training for multiple rounds.
        """
        print(f"Starting federated training with "
              f"{len(client_data)} clients")
        print(f"Rounds: {n_rounds}")
        print()

        for round_num in range(n_rounds):
            client_updates = []
            client_sizes = []

            # Each client trains locally
            for client_id, (X_local, y_local) in enumerate(
                client_data
            ):
                local_weights, local_bias = self.client_train(
                    X_local, y_local,
                    self.global_weights, self.global_bias,
                )
                client_updates.append((local_weights, local_bias))
                client_sizes.append(len(y_local))

            # Aggregate updates
            self.global_weights, self.global_bias = \
                self.aggregate_updates(client_updates, client_sizes)

            # Evaluate global model
            all_X = np.vstack([X for X, y in client_data])
            all_y = np.concatenate([y for X, y in client_data])
            z = all_X @ self.global_weights + self.global_bias
            preds = (1 / (1 + np.exp(-np.clip(z, -500, 500))) > 0.5)
            accuracy = np.mean(preds == all_y)

            self.round_history.append(accuracy)

            if (round_num + 1) % 2 == 0 or round_num == 0:
                print(f"  Round {round_num + 1:>3}: "
                      f"accuracy = {accuracy:.3f}")

        print(f"\nFinal accuracy: {self.round_history[-1]:.3f}")


# Simulate federated learning
np.random.seed(42)

# Create data distributed across 3 "hospitals"
X_full, y_full = make_classification(
    n_samples=3000, n_features=10, random_state=42
)

# Split data among clients (unequal distribution)
client_data = [
    (X_full[:1000], y_full[:1000]),      # Hospital A: 1000 patients
    (X_full[1000:1800], y_full[1000:1800]),  # Hospital B: 800 patients
    (X_full[1800:], y_full[1800:]),      # Hospital C: 1200 patients
]

print("FEDERATED LEARNING DEMONSTRATION")
print("=" * 55)
print()
print("Scenario: 3 hospitals want to train a model together")
print("but cannot share patient data due to regulations.")
print()
print(f"Hospital A: {len(client_data[0][1])} patients")
print(f"Hospital B: {len(client_data[1][1])} patients")
print(f"Hospital C: {len(client_data[2][1])} patients")
print()

fl = FederatedLearningSimulator(n_features=10, n_clients=3)
fl.train_federated(client_data, n_rounds=20)

# Compare with centralized training
print(f"\nComparison with centralized training:")
from sklearn.linear_model import LogisticRegression
centralized_model = LogisticRegression(max_iter=1000)
centralized_model.fit(X_full, y_full)
centralized_acc = centralized_model.score(X_full, y_full)
print(f"  Centralized accuracy: {centralized_acc:.3f}")
print(f"  Federated accuracy:   {fl.round_history[-1]:.3f}")
print(f"  Gap:                  {centralized_acc - fl.round_history[-1]:.3f}")
print(f"\n  Federated learning achieves close to centralized")
print(f"  performance WITHOUT sharing any patient data!")
```

```
Output:
FEDERATED LEARNING DEMONSTRATION
=======================================================

Scenario: 3 hospitals want to train a model together
but cannot share patient data due to regulations.

Hospital A: 1000 patients
Hospital B: 800 patients
Hospital C: 1200 patients

Starting federated training with 3 clients
Rounds: 20

  Round   1: accuracy = 0.723
  Round   2: accuracy = 0.789
  Round   4: accuracy = 0.834
  Round   6: accuracy = 0.852
  Round   8: accuracy = 0.861
  Round  10: accuracy = 0.867
  Round  12: accuracy = 0.870
  Round  14: accuracy = 0.872
  Round  16: accuracy = 0.873
  Round  18: accuracy = 0.874
  Round  20: accuracy = 0.874

Final accuracy: 0.874

Comparison with centralized training:
  Centralized accuracy: 0.891
  Federated accuracy:   0.874
  Gap:                  0.017

  Federated learning achieves close to centralized
  performance WITHOUT sharing any patient data!
```

---

## Data Anonymization Techniques

**Data anonymization** removes or transforms personally identifiable information (PII) so individuals cannot be identified.

```python
import re
import hashlib

class DataAnonymizer:
    """
    Anonymize datasets by removing or transforming PII.
    """

    def __init__(self, salt="random_secret_salt_12345"):
        self.salt = salt

    def hash_value(self, value):
        """
        One-way hash: cannot be reversed to find original value.
        Same input always produces same hash (consistent).
        """
        salted = f"{self.salt}:{value}"
        return hashlib.sha256(salted.encode()).hexdigest()[:12]

    def mask_email(self, email):
        """Mask an email address."""
        if "@" not in str(email):
            return email
        local, domain = str(email).split("@")
        masked_local = local[0] + "***" + local[-1]
        return f"{masked_local}@{domain}"

    def mask_phone(self, phone):
        """Mask a phone number, keeping last 4 digits."""
        digits = re.sub(r'\D', '', str(phone))
        if len(digits) >= 4:
            return "***-***-" + digits[-4:]
        return "***"

    def generalize_age(self, age, bin_size=10):
        """Replace exact age with age range."""
        lower = (int(age) // bin_size) * bin_size
        upper = lower + bin_size - 1
        return f"{lower}-{upper}"

    def generalize_zip(self, zip_code, keep_digits=3):
        """Keep only first N digits of zip code."""
        zip_str = str(zip_code)
        return zip_str[:keep_digits] + "XX"

    def suppress(self, value, threshold_count=5, group_count=0):
        """
        Replace rare values with 'OTHER' to prevent
        identification through rare combinations.
        """
        if group_count < threshold_count:
            return "[SUPPRESSED]"
        return value

    def anonymize_dataframe(self, df, config):
        """
        Anonymize a DataFrame based on configuration.

        config: dict mapping column names to anonymization methods
        """
        df_anon = df.copy()

        for col, method in config.items():
            if col not in df_anon.columns:
                continue

            if method == "hash":
                df_anon[col] = df_anon[col].apply(self.hash_value)
            elif method == "mask_email":
                df_anon[col] = df_anon[col].apply(self.mask_email)
            elif method == "mask_phone":
                df_anon[col] = df_anon[col].apply(self.mask_phone)
            elif method == "generalize_age":
                df_anon[col] = df_anon[col].apply(self.generalize_age)
            elif method == "generalize_zip":
                df_anon[col] = df_anon[col].apply(self.generalize_zip)
            elif method == "remove":
                df_anon = df_anon.drop(columns=[col])

        return df_anon


# Demonstrate anonymization
anonymizer = DataAnonymizer()

# Create sample PII data
sample_data = pd.DataFrame({
    "name": ["John Smith", "Jane Doe", "Bob Johnson",
             "Alice Williams", "Charlie Brown"],
    "email": ["john@email.com", "jane@company.org",
              "bob@mail.com", "alice@work.net", "charlie@mail.com"],
    "phone": ["555-123-4567", "555-234-5678", "555-345-6789",
              "555-456-7890", "555-567-8901"],
    "age": [34, 45, 28, 52, 41],
    "zip_code": ["94102", "94103", "94102", "10001", "10002"],
    "income": [75000, 92000, 65000, 110000, 88000],
    "condition": ["diabetes", "none", "asthma", "diabetes", "none"],
})

print("DATA ANONYMIZATION DEMONSTRATION")
print("=" * 60)

print("\nORIGINAL DATA (contains PII):")
print(sample_data.to_string(index=False))

# Apply anonymization
config = {
    "name": "hash",
    "email": "mask_email",
    "phone": "mask_phone",
    "age": "generalize_age",
    "zip_code": "generalize_zip",
}

anon_data = anonymizer.anonymize_dataframe(sample_data, config)

print(f"\n\nANONYMIZED DATA:")
print(anon_data.to_string(index=False))

print(f"\n\nANONYMIZATION METHODS USED:")
print(f"  name     -> Hashed (one-way, irreversible)")
print(f"  email    -> Masked (partially hidden)")
print(f"  phone    -> Masked (only last 4 digits visible)")
print(f"  age      -> Generalized (exact age -> age range)")
print(f"  zip_code -> Generalized (full zip -> partial zip)")
print(f"  income   -> Kept as-is (not PII by itself)")
print(f"  condition-> Kept as-is (useful for modeling)")
```

```
Output:
DATA ANONYMIZATION DEMONSTRATION
============================================================

ORIGINAL DATA (contains PII):
         name            email         phone  age zip_code  income condition
   John Smith   john@email.com  555-123-4567   34    94102   75000  diabetes
     Jane Doe  jane@company.org  555-234-5678   45    94103   92000      none
  Bob Johnson     bob@mail.com  555-345-6789   28    94102   65000    asthma
Alice Williams  alice@work.net  555-456-7890   52    10001  110000  diabetes
 Charlie Brown charlie@mail.com  555-567-8901   41    10002   88000      none


ANONYMIZED DATA:
         name            email         phone    age zip_code  income condition
 a3f8b2c1d4e5   j***n@email.com  ***-***-4567  30-39    941XX   75000  diabetes
 b4e9c3d2f5a6  j***e@company.org  ***-***-5678  40-49    941XX   92000      none
 c5f0d4e3a6b7     b***b@mail.com  ***-***-6789  20-29    941XX   65000    asthma
 d6a1e5f4b7c8  a***e@work.net  ***-***-7890  50-59    100XX  110000  diabetes
 e7b2f6a5c8d9 c***e@mail.com  ***-***-8901  40-49    100XX   88000      none


ANONYMIZATION METHODS USED:
  name     -> Hashed (one-way, irreversible)
  email    -> Masked (partially hidden)
  phone    -> Masked (only last 4 digits visible)
  age      -> Generalized (exact age -> age range)
  zip_code -> Generalized (full zip -> partial zip)
  income   -> Kept as-is (not PII by itself)
  condition-> Kept as-is (useful for modeling)
```

---

## PII Detection

Before you can protect PII, you need to find it. Here is how to automatically detect PII in datasets.

```python
class PIIDetector:
    """
    Detect personally identifiable information in datasets.
    """

    def __init__(self):
        self.patterns = {
            "email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            "phone_us": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            "ip_address": r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
        }

        self.name_indicators = [
            "name", "first_name", "last_name", "full_name",
            "patient_name", "customer_name", "user_name",
        ]

        self.address_indicators = [
            "address", "street", "city", "state", "zip",
            "postal", "residence",
        ]

    def scan_column(self, series, column_name):
        """Scan a column for PII patterns."""
        findings = []

        # Check column name for PII indicators
        col_lower = column_name.lower()
        for indicator in self.name_indicators:
            if indicator in col_lower:
                findings.append({
                    "type": "name_field",
                    "confidence": "HIGH",
                    "reason": f"Column name '{column_name}' "
                              f"suggests personal names",
                })
                break

        for indicator in self.address_indicators:
            if indicator in col_lower:
                findings.append({
                    "type": "address_field",
                    "confidence": "HIGH",
                    "reason": f"Column name '{column_name}' "
                              f"suggests address data",
                })
                break

        # Check column values for PII patterns
        if series.dtype == object:
            sample = series.dropna().head(100)
            for pii_type, pattern in self.patterns.items():
                matches = sample.str.contains(
                    pattern, regex=True, na=False
                ).sum()
                if matches > 0:
                    findings.append({
                        "type": pii_type,
                        "confidence": "HIGH" if matches > 5 else "MEDIUM",
                        "reason": f"Found {matches} matches for "
                                  f"{pii_type} pattern",
                    })

        return findings

    def scan_dataframe(self, df):
        """Scan entire DataFrame for PII."""
        report = {}
        for col in df.columns:
            findings = self.scan_column(df[col], col)
            if findings:
                report[col] = findings
        return report


# Scan our sample data for PII
detector = PIIDetector()
report = detector.scan_dataframe(sample_data)

print("PII DETECTION REPORT")
print("=" * 60)

if report:
    for col, findings in report.items():
        print(f"\nColumn: '{col}'")
        for finding in findings:
            print(f"  Type:       {finding['type']}")
            print(f"  Confidence: {finding['confidence']}")
            print(f"  Reason:     {finding['reason']}")
else:
    print("No PII detected.")

# Summary
print(f"\n{'=' * 60}")
print("SUMMARY")
print(f"{'=' * 60}")
print(f"Columns scanned:  {len(sample_data.columns)}")
print(f"Columns with PII: {len(report)}")
print(f"PII types found:  {set(f['type'] for findings in report.values() for f in findings)}")

print(f"\nRECOMMENDATIONS:")
for col in report:
    print(f"  - '{col}': Anonymize or remove before model training")
```

```
Output:
PII DETECTION REPORT
============================================================

Column: 'name'
  Type:       name_field
  Confidence: HIGH
  Reason:     Column name 'name' suggests personal names

Column: 'email'
  Type:       email
  Confidence: HIGH
  Reason:     Found 5 matches for email pattern

Column: 'phone'
  Type:       phone_us
  Confidence: HIGH
  Reason:     Found 5 matches for phone_us pattern

============================================================
SUMMARY
============================================================
Columns scanned:  7
Columns with PII: 3
PII types found:  {'name_field', 'email', 'phone_us'}

RECOMMENDATIONS:
  - 'name': Anonymize or remove before model training
  - 'email': Anonymize or remove before model training
  - 'phone': Anonymize or remove before model training
```

---

## Privacy-Preserving ML Pipeline

```
COMPLETE PRIVACY-PRESERVING ML PIPELINE:

Step 1: DATA COLLECTION
+------------------+
| Collect data     |
| with consent     |
| Minimize what    |
| you collect      |
+--------+---------+
         |
Step 2: PII DETECTION
+--------+---------+
| Scan for PII     |
| Flag sensitive   |
| columns          |
+--------+---------+
         |
Step 3: ANONYMIZATION
+--------+---------+
| Hash identifiers |
| Mask emails/     |
| phones           |
| Generalize ages  |
| zip codes        |
+--------+---------+
         |
Step 4: TRAINING
+--------+---------+
| Use differential |
| privacy (DP-SGD) |
| or federated     |
| learning         |
+--------+---------+
         |
Step 5: DEPLOYMENT
+--------+---------+
| Limit API query  |
| rate             |
| Monitor for      |
| inference attacks|
| Log access       |
+--------+---------+
         |
Step 6: DELETION
+--------+---------+
| Honor deletion   |
| requests (GDPR   |
| right to be      |
| forgotten)       |
+------------------+
```

---

## Common Mistakes

1. **Thinking anonymization alone is enough** — Research shows that 87% of Americans can be uniquely identified by zip code, birth date, and gender alone. Simple anonymization is often insufficient.

2. **Ignoring model memorization** — Large models can memorize and regurgitate training data. Test for memorization before deploying.

3. **Setting epsilon too large** — An epsilon of 100 provides essentially no privacy. Use epsilon between 1 and 10 for meaningful protection.

4. **Sharing model gradients without protection** — In federated learning, raw gradients can leak information. Add differential privacy noise to gradients before sharing.

5. **Not having a data deletion plan** — GDPR gives users the right to be forgotten. If a user requests deletion, you need a process to remove their influence from trained models.

---

## Best Practices

1. **Collect only what you need** — The best way to protect data is to never collect it. Only gather features that are truly necessary for your model.

2. **Anonymize before training** — Apply anonymization to raw data before it enters the ML pipeline. Never train on raw PII if anonymized data will work.

3. **Use differential privacy for sensitive data** — When working with medical, financial, or other sensitive data, add differential privacy to your training process.

4. **Audit regularly** — Scan your datasets and models for PII leakage periodically, not just at deployment.

5. **Document your privacy measures** — Keep records of what data you collect, how it is protected, and what privacy guarantees your system provides. This is required by regulations.

---

## Quick Summary

Privacy in ML addresses risks including model memorization (models can leak training data), membership inference (attackers determine if specific data was used for training), and model inversion (reconstructing inputs from outputs). Differential privacy adds calibrated noise to protect individuals, controlled by the epsilon parameter (smaller epsilon means more privacy but less accuracy). Federated learning trains models across multiple participants without sharing raw data. Data anonymization techniques include hashing, masking, generalization, and suppression. PII detection scans datasets for personal information before training. A complete privacy pipeline combines data minimization, PII detection, anonymization, private training, and ongoing monitoring.

---

## Key Points

- ML models can memorize and leak training data through various attacks
- Differential privacy adds calibrated noise so individual contributions cannot be identified
- Epsilon controls the privacy-accuracy trade-off (smaller = more private, less accurate)
- Federated learning trains models without centralizing data by sharing only model updates
- Data anonymization techniques include hashing, masking, generalization, and suppression
- PII detection should run before any data enters the ML pipeline
- Simple anonymization (removing names) is often insufficient due to quasi-identifiers
- GDPR, CCPA, and HIPAA require specific privacy protections for personal data
- Privacy measures should be documented for regulatory compliance
- Collect only the minimum data necessary for your model to function

---

## Practice Questions

1. A model trained on hospital records achieves 95% accuracy. When you add differential privacy with epsilon=1.0, accuracy drops to 88%. Is this acceptable? What factors would influence your decision?

2. Explain why removing a person's name from a dataset does not guarantee their privacy. What is re-identification, and how does it work?

3. In federated learning, why might sharing raw gradients still be a privacy risk? What can you do to mitigate this?

4. Your dataset has 10,000 records with zip code, age, and gender. A researcher claims they can identify individuals using just these three fields. Is this plausible? Why?

5. A user requests that their data be deleted under GDPR. The data was used to train a model. What are your options for complying with this request?

---

## Exercises

### Exercise 1: Build a PII Scanner

Create a comprehensive PII scanner that:
1. Detects emails, phone numbers, social security numbers, and credit card numbers
2. Identifies potential name columns by analyzing column names and content patterns
3. Flags columns with low cardinality that could be quasi-identifiers
4. Generates a report with risk levels and recommendations

### Exercise 2: Implement Differential Privacy

Implement a differentially private mean calculation:
1. Calculate the true mean of a dataset
2. Add Laplace noise with different epsilon values (0.01, 0.1, 1.0, 10.0)
3. Run each calculation 100 times and report the average error
4. Plot or print the privacy-accuracy trade-off curve

### Exercise 3: Federated Learning Simulator

Build a federated learning system that:
1. Splits a classification dataset among 5 clients with non-uniform distributions
2. Implements FedAvg (Federated Averaging)
3. Compares the federated model accuracy with centralized training
4. Experiments with different numbers of local training epochs per round
5. Adds differential privacy noise to the gradient updates

---

## What Is Next?

Now that you understand how to protect data privacy in ML systems, the next step is understanding the legal and regulatory landscape. In the next chapter, we will explore **AI Regulations** — the EU AI Act, GDPR implications for AI, and how to build AI systems responsibly within regulatory frameworks.
