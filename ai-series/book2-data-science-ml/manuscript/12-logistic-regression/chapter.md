# Chapter 12: Logistic Regression

## What You Will Learn

In this chapter, you will learn:

- Why linear regression fails for classification problems
- What logistic regression is and how it works
- How the sigmoid function turns numbers into probabilities
- What a decision boundary is and how it separates classes
- How to build a logistic regression model with scikit-learn
- How to handle binary classification (two classes)
- How to handle multi-class classification (three or more classes)
- What a confusion matrix is and how to read it
- How to build a complete customer purchase prediction system

## Why This Chapter Matters

Imagine you are a doctor. A patient walks in. You need to answer a simple question: does this patient have the disease or not? Yes or no. Sick or healthy. Positive or negative.

This is a **classification** problem. You are not predicting a number (like "how tall will this person grow?"). You are predicting a **category** (like "will this person buy our product?").

Classification is everywhere:

- Will this email be spam or not spam?
- Will this customer leave or stay?
- Will this loan be approved or denied?
- Will this tumor be benign or malignant?

Logistic regression is the simplest and most popular algorithm for classification. It is often the **first model** data scientists try. It is fast, easy to understand, and works surprisingly well.

If linear regression is the "hello world" of regression, logistic regression is the "hello world" of classification. You need to learn it before anything else.

---

## From Regression to Classification

### The Problem with Linear Regression

In earlier chapters, you learned linear regression. It predicts a continuous number. For example, it might predict that a house costs $250,000.

But what if we want to predict something with only two outcomes?

Let us say we want to predict whether a student will pass an exam based on hours studied.

```
Hours Studied | Pass? (1 = Yes, 0 = No)
--------------|-----------------------
1             | 0
2             | 0
3             | 0
4             | 0
5             | 1
6             | 1
7             | 1
8             | 1
```

If we use linear regression, we get a straight line:

```
Pass?
1.0 |                          xxxxxxx
    |                    xxxxx
    |               xxxx
0.5 |          xxxx
    |     xxxx
    |xxxx
0.0 |xxxx
    +--+--+--+--+--+--+--+--+--
       1  2  3  4  5  6  7  8
                Hours Studied
```

The problem? Linear regression can predict values like 1.5 or -0.3. But a student cannot "half pass" an exam. The answer must be 0 or 1.

We need a way to squeeze any number into the range of 0 to 1. That is where the **sigmoid function** comes in.

### What Is a Sigmoid Function?

A **sigmoid function** (pronounced "SIG-moyd") is a mathematical formula that takes any number and converts it into a value between 0 and 1. Think of it as a squeezing machine.

You put in any number. It gives you back a number between 0 and 1.

Here is what it looks like:

```
Output
1.0 |                          --------
    |                       --
    |                     /
0.5 |                   /
    |                 /
    |              --
0.0 |  ------------
    +--+--+--+--+--+--+--+--+--+--+--
      -5 -4 -3 -2 -1  0  1  2  3  4  5
                    Input
```

Notice the S-shape. That is why it is called "sigmoid" (sigma is an S-shaped Greek letter).

The rules are simple:

- Big positive numbers become close to 1.0
- Big negative numbers become close to 0.0
- Zero becomes exactly 0.5

**Real-life analogy:** Think of a dimmer switch for a light. You can turn the knob from "fully off" (0) to "fully on" (1). The sigmoid function is like that dimmer switch. It smoothly transitions from off to on.

The mathematical formula is:

```
sigmoid(x) = 1 / (1 + e^(-x))
```

Where `e` is Euler's number (approximately 2.718). Do not worry about memorizing this formula. Python will handle it for you.

Let us see it in Python:

```python
import numpy as np
import matplotlib.pyplot as plt

# Create input values from -10 to 10
x = np.linspace(-10, 10, 100)

# Sigmoid function
sigmoid = 1 / (1 + np.exp(-x))

# Print a few values
print("Input -> Sigmoid Output")
print(f"  -10 -> {1 / (1 + np.exp(10)):.4f}")
print(f"   -5 -> {1 / (1 + np.exp(5)):.4f}")
print(f"    0 -> {1 / (1 + np.exp(0)):.4f}")
print(f"    5 -> {1 / (1 + np.exp(-5)):.4f}")
print(f"   10 -> {1 / (1 + np.exp(-10)):.4f}")
```

**Output:**

```
Input -> Sigmoid Output
  -10 -> 0.0000
   -5 -> 0.0067
    0 -> 0.5000
    5 -> 0.9933
   10 -> 0.9999
```

**Line-by-line explanation:**

1. `x = np.linspace(-10, 10, 100)` -- Create 100 evenly spaced numbers from -10 to 10
2. `sigmoid = 1 / (1 + np.exp(-x))` -- Apply the sigmoid formula to every number
3. The print statements show how different inputs map to outputs between 0 and 1

---

## How Logistic Regression Works

Logistic regression works in two steps:

**Step 1:** It calculates a weighted sum (just like linear regression).

```
z = w1*x1 + w2*x2 + ... + b
```

Where `w` values are weights, `x` values are features, and `b` is the bias (intercept). This is the same as linear regression.

**Step 2:** It passes that sum through the sigmoid function.

```
probability = sigmoid(z) = 1 / (1 + e^(-z))
```

This converts the raw number into a probability between 0 and 1.

Here is the full picture:

```
                    Logistic Regression Pipeline

    Features          Weighted Sum         Sigmoid          Prediction
    --------          ------------         -------          ----------

    x1 --w1--\
              \
    x2 --w2---+--->  z = w1*x1 +  ---->  sigmoid(z)  ---->  0 or 1
              /       w2*x2 + b           = p
    bias --b-/

                                     if p >= 0.5 --> 1 (Yes)
                                     if p <  0.5 --> 0 (No)
```

**Real-life analogy:** Imagine you are deciding whether to go to a picnic. You consider several factors:

- Weather forecast (sunny = +3, rainy = -3)
- Friend coming (yes = +2, no = -1)
- Distance (close = +1, far = -2)

You add up all the scores. If the total is positive, you are probably going. If negative, probably not. The sigmoid function converts your total score into a probability (like "75% chance I will go").

### What Is a Decision Boundary?

The **decision boundary** is the line (or surface) that separates the two classes. It is where the model says "above this line, I predict class 1. Below this line, I predict class 0."

```
    Feature 2
    ^
    |   0  0  0  |  1  1  1
    |   0  0  0  |  1  1  1
    |   0  0  0  |  1  1  1
    |   0  0  0  |  1  1  1
    |   0  0  0  |  1  1  1
    +---------------------> Feature 1
                 ^
                 |
          Decision Boundary
          (where probability = 0.5)
```

At the decision boundary, the sigmoid output is exactly 0.5. The model is equally unsure about both classes.

- To the right of the boundary: probability > 0.5, so predict class 1
- To the left of the boundary: probability < 0.5, so predict class 0

---

## Your First Logistic Regression with Scikit-Learn

Let us build a model that predicts whether a student passes an exam based on hours studied.

```python
import numpy as np
from sklearn.linear_model import LogisticRegression

# Training data
# Hours studied
X_train = np.array([1, 2, 3, 4, 5, 6, 7, 8]).reshape(-1, 1)

# Pass (1) or Fail (0)
y_train = np.array([0, 0, 0, 0, 1, 1, 1, 1])

# Create and train the model
model = LogisticRegression()
model.fit(X_train, y_train)

# Predict for new students
new_students = np.array([2.5, 4.5, 6.5]).reshape(-1, 1)
predictions = model.predict(new_students)
probabilities = model.predict_proba(new_students)

# Show results
for hours, pred, prob in zip([2.5, 4.5, 6.5], predictions, probabilities):
    status = "PASS" if pred == 1 else "FAIL"
    print(f"Hours: {hours} -> Prediction: {status}")
    print(f"  Probability of failing: {prob[0]:.2%}")
    print(f"  Probability of passing: {prob[1]:.2%}")
    print()
```

**Output:**

```
Hours: 2.5 -> Prediction: FAIL
  Probability of failing: 93.47%
  Probability of passing: 6.53%

Hours: 4.5 -> Prediction: PASS
  Probability of failing: 49.64%
  Probability of passing: 50.36%

Hours: 6.5 -> Prediction: PASS
  Probability of failing: 6.53%
  Probability of passing: 93.47%
```

**Line-by-line explanation:**

1. `X_train = np.array([1, 2, 3, 4, 5, 6, 7, 8]).reshape(-1, 1)` -- Create feature data. The `reshape(-1, 1)` converts a flat list into a column (scikit-learn requires this shape for a single feature).
2. `y_train = np.array([0, 0, 0, 0, 1, 1, 1, 1])` -- Create labels. 0 means fail, 1 means pass.
3. `model = LogisticRegression()` -- Create a logistic regression model object.
4. `model.fit(X_train, y_train)` -- Train the model on our data. The model learns the weights.
5. `new_students = np.array([2.5, 4.5, 6.5]).reshape(-1, 1)` -- Create test data for three new students.
6. `predictions = model.predict(new_students)` -- Get class predictions (0 or 1).
7. `probabilities = model.predict_proba(new_students)` -- Get probability for each class. Returns two columns: [probability of class 0, probability of class 1].

Notice that 4.5 hours is right near the decision boundary. The model is almost 50/50 on whether that student passes.

---

## Binary Classification: Customer Purchase Prediction

Let us build a more realistic example. We will predict whether a customer will buy a product based on their age and estimated salary.

```python
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

# Create sample data
np.random.seed(42)
n_samples = 200

# Generate customer data
ages = np.random.randint(18, 65, n_samples)
salaries = np.random.randint(20000, 120000, n_samples)

# Purchase rule: more likely if older and higher salary
# (with some randomness)
purchase_score = (ages - 30) * 0.05 + (salaries - 50000) * 0.00003
purchase_probability = 1 / (1 + np.exp(-purchase_score))
purchased = (purchase_probability > np.random.random(n_samples)).astype(int)

# Create DataFrame
df = pd.DataFrame({
    'Age': ages,
    'Salary': salaries,
    'Purchased': purchased
})

print("First 10 rows:")
print(df.head(10))
print(f"\nTotal customers: {len(df)}")
print(f"Purchased: {purchased.sum()} ({purchased.mean():.1%})")
print(f"Not Purchased: {(1-purchased).sum()} ({(1-purchased).mean():.1%})")
```

**Output:**

```
First 10 rows:
   Age  Salary  Purchased
0   56   74531          1
1   18   93949          1
2   28   67513          0
3   60   40073          1
4   37   53085          0
5   49   27830          0
6   62   32966          1
7   56   84741          1
8   41   96498          1
9   30   53709          0

Total customers: 200
Purchased: 107 (53.5%)
Not Purchased: 93 (46.5%)
```

Now let us train and evaluate the model:

```python
# Step 1: Separate features and target
X = df[['Age', 'Salary']]
y = df['Purchased']

# Step 2: Split into training and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"Training set size: {len(X_train)}")
print(f"Test set size: {len(X_test)}")

# Step 3: Scale the features
# Age ranges from 18-65, Salary from 20000-120000
# We need to put them on the same scale
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"\nBefore scaling (first row): Age={X_train.iloc[0]['Age']}, "
      f"Salary={X_train.iloc[0]['Salary']}")
print(f"After scaling (first row):  {X_train_scaled[0][0]:.2f}, "
      f"{X_train_scaled[0][1]:.2f}")

# Step 4: Train the model
model = LogisticRegression(random_state=42)
model.fit(X_train_scaled, y_train)

# Step 5: Make predictions
y_pred = model.predict(X_test_scaled)

# Step 6: Check accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"\nModel Accuracy: {accuracy:.2%}")

# Step 7: Look at model coefficients
print(f"\nModel Coefficients:")
print(f"  Age weight:    {model.coef_[0][0]:.4f}")
print(f"  Salary weight: {model.coef_[0][1]:.4f}")
print(f"  Intercept:     {model.intercept_[0]:.4f}")
```

**Output:**

```
Training set size: 160
Test set size: 40

Before scaling (first row): Age=49, Salary=27830
After scaling (first row):  0.65, -1.43

Model Accuracy: 77.50%

Model Coefficients:
  Age weight:    0.6511
  Salary weight: 0.5789
  Intercept:     0.1532
```

**Line-by-line explanation:**

1. `X = df[['Age', 'Salary']]` -- Select the feature columns.
2. `y = df['Purchased']` -- Select the target column.
3. `train_test_split(X, y, test_size=0.2, random_state=42)` -- Split data: 80% for training, 20% for testing.
4. `StandardScaler()` -- Creates a scaler that will normalize features to have mean=0 and standard deviation=1. This is important because Age (18-65) and Salary (20000-120000) are on very different scales.
5. `scaler.fit_transform(X_train)` -- Learn the scaling parameters from training data AND transform it.
6. `scaler.transform(X_test)` -- Transform test data using the SAME parameters. Never fit on test data.
7. `model.coef_` -- Shows how much each feature matters. Both are positive, meaning higher age and higher salary both increase the chance of purchase.

### Why Feature Scaling Matters

```
Without Scaling:                 With Scaling:

Age: 18-65 (range = 47)         Age: -2 to +2
Salary: 20K-120K (range = 100K) Salary: -2 to +2

The model thinks Salary is       Both features are treated
2000x more important than Age!   fairly and equally.
```

**StandardScaler** (standard scaler) transforms each feature so that it has a mean of 0 and a standard deviation of 1. This puts all features on the same playing field.

---

## Understanding Predictions with Probabilities

One of the best features of logistic regression is that it gives you **probabilities**, not just yes/no answers.

```python
# Get probabilities for test data
y_proba = model.predict_proba(X_test_scaled)

# Show predictions with probabilities
print("Customer Predictions with Confidence:")
print("-" * 55)
print(f"{'Age':>5} {'Salary':>8} {'Actual':>8} {'Predicted':>10} {'Confidence':>12}")
print("-" * 55)

for i in range(10):
    age = X_test.iloc[i]['Age']
    salary = X_test.iloc[i]['Salary']
    actual = "Buy" if y_test.iloc[i] == 1 else "No Buy"
    predicted = "Buy" if y_pred[i] == 1 else "No Buy"
    confidence = max(y_proba[i]) * 100

    # Mark incorrect predictions
    marker = " " if y_test.iloc[i] == y_pred[i] else " <-- WRONG"

    print(f"{age:>5} {salary:>8} {actual:>8} {predicted:>10} "
          f"{confidence:>10.1f}%{marker}")
```

**Output:**

```
Customer Predictions with Confidence:
-------------------------------------------------------
  Age   Salary   Actual  Predicted   Confidence
-------------------------------------------------------
   26    57145   No Buy     No Buy       60.2%
   44   108498      Buy        Buy       83.1%
   31    26849   No Buy     No Buy       79.5%
   54    98641      Buy        Buy       90.7%
   19    54930   No Buy     No Buy       71.3%
   62    43000      Buy        Buy       67.4%
   38    71209      Buy     No Buy       51.2% <-- WRONG
   55    89100      Buy        Buy       87.6%
   23    35000   No Buy     No Buy       82.9%
   47    62000      Buy        Buy       63.8%
```

Notice that wrong predictions often have low confidence (close to 50%). This tells us the model was unsure about those cases.

---

## The Confusion Matrix

A **confusion matrix** is a table that shows how well your classification model performed. It counts four things:

```
                        Predicted
                    No (0)     Yes (1)
                 +----------+----------+
    Actual No  0 |    TN    |    FP    |
                 +----------+----------+
    Actual Yes 1 |    FN    |    TP    |
                 +----------+----------+

TN = True Negative  -- Correctly predicted No
FP = False Positive -- Incorrectly predicted Yes (Type I Error)
FN = False Negative -- Incorrectly predicted No (Type II Error)
TP = True Positive  -- Correctly predicted Yes
```

**Real-life analogy:** Think of a fire alarm:

- **True Positive (TP):** There is a fire, and the alarm goes off. Correct!
- **True Negative (TN):** There is no fire, and the alarm stays quiet. Correct!
- **False Positive (FP):** There is no fire, but the alarm goes off. Annoying!
- **False Negative (FN):** There is a fire, but the alarm stays quiet. Dangerous!

Let us see the confusion matrix for our customer model:

```python
from sklearn.metrics import confusion_matrix, classification_report

# Create confusion matrix
cm = confusion_matrix(y_test, y_pred)
print("Confusion Matrix:")
print(cm)

# Make it more readable
print("\n--- Confusion Matrix (Readable) ---")
print(f"                    Predicted")
print(f"                 No Buy    Buy")
print(f"Actual No Buy    {cm[0][0]:>5}    {cm[0][1]:>5}")
print(f"Actual Buy       {cm[1][0]:>5}    {cm[1][1]:>5}")

# Key metrics
tn, fp, fn, tp = cm.ravel()
print(f"\nTrue Negatives:  {tn} (correctly predicted No Buy)")
print(f"False Positives: {fp} (incorrectly predicted Buy)")
print(f"False Negatives: {fn} (incorrectly predicted No Buy)")
print(f"True Positives:  {tp} (correctly predicted Buy)")

# Classification report
print("\n--- Classification Report ---")
print(classification_report(y_test, y_pred,
                            target_names=['No Buy', 'Buy']))
```

**Output:**

```
Confusion Matrix:
[[14  3]
 [ 6 17]]

--- Confusion Matrix (Readable) ---
                    Predicted
                 No Buy    Buy
Actual No Buy       14      3
Actual Buy           6     17

True Negatives:  14 (correctly predicted No Buy)
False Positives: 3 (incorrectly predicted Buy)
False Negatives: 6 (incorrectly predicted No Buy)
True Positives:  17 (correctly predicted Buy)

--- Classification Report ---
              precision    recall  f1-score   support

      No Buy       0.70      0.82      0.76        17
         Buy       0.85      0.74      0.79        23

    accuracy                           0.78        40
   macro avg       0.78      0.78      0.77        40
weighted avg       0.79      0.78      0.78        40
```

**Understanding the classification report:**

- **Precision** (pre-SIH-zhun): Of all the times the model predicted "Buy", how many were actually "Buy"? High precision means few false alarms.
- **Recall** (re-CALL): Of all the actual "Buy" customers, how many did the model catch? High recall means few missed cases.
- **F1-score**: The balance between precision and recall. It is the harmonic mean (a special kind of average) of both.
- **Support**: How many actual instances of each class exist in the test set.

---

## Multi-Class Classification

So far, we have predicted two classes (buy or not buy). But logistic regression can also handle **multi-class** problems -- problems with three or more classes.

**Examples of multi-class problems:**

- Predicting the type of flower (setosa, versicolor, virginica)
- Classifying an image as a cat, dog, or bird
- Rating a review as positive, neutral, or negative

```python
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Load the famous Iris dataset
iris = load_iris()
X = iris.data       # 4 features: sepal length/width, petal length/width
y = iris.target     # 3 classes: 0=setosa, 1=versicolor, 2=virginica

print("Feature names:", iris.feature_names)
print("Target names:", iris.target_names)
print(f"Number of samples: {len(X)}")
print(f"Number of features: {X.shape[1]}")
print(f"Number of classes: {len(iris.target_names)}")

# Split the data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Train multi-class logistic regression
model = LogisticRegression(max_iter=200, random_state=42)
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)

# Accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"\nAccuracy: {accuracy:.2%}")

# Detailed report
print("\n--- Classification Report ---")
print(classification_report(y_test, y_pred,
                            target_names=iris.target_names))
```

**Output:**

```
Feature names: ['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']
Target names: ['setosa' 'versicolor' 'virginica']
Number of samples: 150
Number of features: 4
Number of classes: 3

Accuracy: 97.78%

--- Classification Report ---
              precision    recall  f1-score   support

      setosa       1.00      1.00      1.00        19
  versicolor       1.00      0.92      0.96        13
   virginica       0.93      1.00      0.96        13

    accuracy                           0.98        45
   macro avg       0.98      0.97      0.97        45
weighted avg       0.98      0.98      0.98        45
```

The model is 97.78% accurate on the Iris dataset. Logistic regression works very well for this classic problem.

**How does multi-class work?** Scikit-learn uses a strategy called **One-vs-Rest** (also called One-vs-All). For 3 classes, it builds 3 separate binary classifiers:

```
Classifier 1: Is it setosa?     (setosa vs. everything else)
Classifier 2: Is it versicolor? (versicolor vs. everything else)
Classifier 3: Is it virginica?  (virginica vs. everything else)

Final prediction: Pick the class with the highest probability.
```

```python
# Show probabilities for a few test samples
print("Multi-Class Probabilities:")
print("-" * 60)
y_proba = model.predict_proba(X_test)

for i in range(5):
    print(f"\nSample {i+1}:")
    print(f"  Actual class: {iris.target_names[y_test[i]]}")
    print(f"  Predicted:    {iris.target_names[y_pred[i]]}")
    for j, name in enumerate(iris.target_names):
        bar = "#" * int(y_proba[i][j] * 30)
        print(f"  P({name:>10}): {y_proba[i][j]:.4f} {bar}")
```

**Output:**

```
Multi-Class Probabilities:
------------------------------------------------------------

Sample 1:
  Actual class: versicolor
  Predicted:    versicolor
  P(    setosa): 0.0021
  P(versicolor): 0.9124 ###########################
  P( virginica): 0.0855 ##

Sample 2:
  Actual class: setosa
  Predicted:    setosa
  P(    setosa): 0.9783 #############################
  P(versicolor): 0.0213
  P( virginica): 0.0004

Sample 3:
  Actual class: virginica
  Predicted:    virginica
  P(    setosa): 0.0001
  P(versicolor): 0.1245 ###
  P( virginica): 0.8754 ##########################
```

---

## Complete Example: Customer Purchase Prediction

Let us put everything together in a complete, production-style example.

```python
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (accuracy_score, confusion_matrix,
                             classification_report)

# ============================================================
# STEP 1: Create a realistic dataset
# ============================================================
np.random.seed(42)
n = 500

data = pd.DataFrame({
    'Age': np.random.randint(18, 70, n),
    'Annual_Income': np.random.randint(15000, 150000, n),
    'Website_Visits': np.random.randint(1, 50, n),
    'Time_On_Site_Min': np.round(np.random.uniform(0.5, 30, n), 1),
    'Previous_Purchases': np.random.randint(0, 10, n)
})

# Create target: Purchase decision based on features
score = (
    (data['Age'] - 30) * 0.02 +
    (data['Annual_Income'] - 50000) * 0.00002 +
    data['Website_Visits'] * 0.03 +
    data['Time_On_Site_Min'] * 0.05 +
    data['Previous_Purchases'] * 0.15 -
    1.5
)
prob = 1 / (1 + np.exp(-score))
data['Purchased'] = (prob > np.random.random(n)).astype(int)

print("=" * 50)
print("CUSTOMER PURCHASE PREDICTION")
print("=" * 50)
print(f"\nDataset shape: {data.shape}")
print(f"\nFirst 5 rows:")
print(data.head())
print(f"\nPurchase distribution:")
print(data['Purchased'].value_counts())
print(f"\nPurchase rate: {data['Purchased'].mean():.1%}")

# ============================================================
# STEP 2: Prepare the data
# ============================================================
# Features and target
X = data.drop('Purchased', axis=1)
y = data['Purchased']

# Split: 80% train, 20% test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTraining set: {len(X_train)} samples")
print(f"Test set:     {len(X_test)} samples")

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ============================================================
# STEP 3: Train the model
# ============================================================
model = LogisticRegression(random_state=42, max_iter=1000)
model.fit(X_train_scaled, y_train)

# ============================================================
# STEP 4: Evaluate the model
# ============================================================
y_pred = model.predict(X_test_scaled)
y_proba = model.predict_proba(X_test_scaled)

print("\n" + "=" * 50)
print("MODEL EVALUATION")
print("=" * 50)

# Accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"\nAccuracy: {accuracy:.2%}")

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
print(f"\nConfusion Matrix:")
print(f"                  Predicted")
print(f"               No Buy   Buy")
print(f"Actual No Buy  {cm[0][0]:>5}   {cm[0][1]:>5}")
print(f"Actual Buy     {cm[1][0]:>5}   {cm[1][1]:>5}")

# Classification Report
print(f"\nClassification Report:")
print(classification_report(y_test, y_pred,
                            target_names=['No Buy', 'Buy']))

# ============================================================
# STEP 5: Feature importance
# ============================================================
print("=" * 50)
print("FEATURE IMPORTANCE")
print("=" * 50)

feature_names = X.columns
coefficients = model.coef_[0]

# Sort by absolute importance
importance = pd.DataFrame({
    'Feature': feature_names,
    'Coefficient': coefficients,
    'Abs_Coefficient': np.abs(coefficients)
}).sort_values('Abs_Coefficient', ascending=False)

print("\nFeature Coefficients (higher = more influence):")
for _, row in importance.iterrows():
    direction = "+" if row['Coefficient'] > 0 else "-"
    bar = "#" * int(row['Abs_Coefficient'] * 15)
    print(f"  {row['Feature']:>20}: {direction}{row['Abs_Coefficient']:.4f} {bar}")

# ============================================================
# STEP 6: Make predictions for new customers
# ============================================================
print("\n" + "=" * 50)
print("PREDICTIONS FOR NEW CUSTOMERS")
print("=" * 50)

new_customers = pd.DataFrame({
    'Age': [25, 45, 60, 30, 50],
    'Annual_Income': [30000, 80000, 120000, 50000, 95000],
    'Website_Visits': [3, 20, 35, 8, 28],
    'Time_On_Site_Min': [2.0, 15.5, 25.0, 5.0, 20.0],
    'Previous_Purchases': [0, 3, 7, 1, 5]
})

new_scaled = scaler.transform(new_customers)
new_pred = model.predict(new_scaled)
new_proba = model.predict_proba(new_scaled)

for i in range(len(new_customers)):
    customer = new_customers.iloc[i]
    pred = "WILL BUY" if new_pred[i] == 1 else "WON'T BUY"
    conf = new_proba[i][new_pred[i]] * 100

    print(f"\nCustomer {i+1}:")
    print(f"  Age: {customer['Age']}, Income: ${customer['Annual_Income']:,}")
    print(f"  Website Visits: {customer['Website_Visits']}, "
          f"Time on Site: {customer['Time_On_Site_Min']} min")
    print(f"  Previous Purchases: {customer['Previous_Purchases']}")
    print(f"  Prediction: {pred} (Confidence: {conf:.1f}%)")
```

**Output:**

```
==================================================
CUSTOMER PURCHASE PREDICTION
==================================================

Dataset shape: (500, 6)

First 5 rows:
   Age  Annual_Income  Website_Visits  Time_On_Site_Min  Previous_Purchases  Purchased
0   56         101498              38               8.3                   1          1
1   18         131663              19              22.5                   5          1
2   28          67513              42               9.1                   3          1
3   60          75073               7              17.2                   9          1
4   37          83085              12               4.6                   4          0

Purchase distribution:
Purchased
1    276
0    224
Name: count, dtype: int64

Purchase rate: 55.2%

Training set: 400 samples
Test set:     100 samples

==================================================
MODEL EVALUATION
==================================================

Accuracy: 76.00%

Confusion Matrix:
                  Predicted
               No Buy   Buy
Actual No Buy     33    12
Actual Buy        12    43

Classification Report:
              precision    recall  f1-score   support

      No Buy       0.73      0.73      0.73        45
         Buy       0.78      0.78      0.78        55

    accuracy                           0.76       100
   macro avg       0.76      0.76      0.76       100
weighted avg       0.76      0.76      0.76       100

==================================================
FEATURE IMPORTANCE
==================================================

Feature Coefficients (higher = more influence):
  Previous_Purchases: +0.5842 ########
       Website_Visits: +0.3921 #####
     Time_On_Site_Min: +0.3587 #####
        Annual_Income: +0.2814 ####
                  Age: +0.1923 ##

==================================================
PREDICTIONS FOR NEW CUSTOMERS
==================================================

Customer 1:
  Age: 25, Income: $30,000
  Website Visits: 3, Time on Site: 2.0 min
  Previous Purchases: 0
  Prediction: WON'T BUY (Confidence: 90.2%)

Customer 2:
  Age: 45, Income: $80,000
  Website Visits: 20, Time on Site: 15.5 min
  Previous Purchases: 3
  Prediction: WILL BUY (Confidence: 72.8%)

Customer 3:
  Age: 60, Income: $120,000
  Website Visits: 35, Time on Site: 25.0 min
  Previous Purchases: 7
  Prediction: WILL BUY (Confidence: 97.3%)

Customer 4:
  Age: 30, Income: $50,000
  Website Visits: 8, Time on Site: 5.0 min
  Previous Purchases: 1
  Prediction: WON'T BUY (Confidence: 63.5%)

Customer 5:
  Age: 50, Income: $95,000
  Website Visits: 28, Time on Site: 20.0 min
  Previous Purchases: 5
  Prediction: WILL BUY (Confidence: 91.6%)
```

**Key insights from the model:**

- **Previous Purchases** is the strongest predictor. Customers who have bought before are most likely to buy again.
- **Website Visits** and **Time on Site** are the next most important. Engaged customers buy more.
- **Age** has the least influence. Customers of all ages buy.

---

## Common Mistakes

1. **Forgetting to scale features.** Logistic regression is sensitive to feature scales. Always use StandardScaler or MinMaxScaler.

2. **Using accuracy alone to evaluate.** If 95% of your data is class 0, a model that always predicts 0 gets 95% accuracy but is useless. Always check the confusion matrix.

3. **Confusing logistic regression with linear regression.** Despite the name, logistic regression is a **classification** algorithm, not a regression algorithm.

4. **Not setting `max_iter` high enough.** If you see a "convergence warning", increase `max_iter` (e.g., `LogisticRegression(max_iter=1000)`).

5. **Fitting the scaler on test data.** Always `fit_transform` on training data and only `transform` on test data. Never let the model "peek" at test data.

---

## Best Practices

1. **Always scale your features** before using logistic regression.

2. **Check the class balance** in your dataset. If one class dominates, consider using `class_weight='balanced'` in LogisticRegression.

3. **Look at probabilities**, not just predictions. A prediction with 51% confidence is very different from one with 99% confidence.

4. **Use the confusion matrix** to understand where your model makes mistakes.

5. **Start with logistic regression** as your baseline model. It is fast and interpretable. Then try more complex models to see if they improve.

6. **Examine feature coefficients** to understand what drives predictions. Positive coefficients increase the probability; negative coefficients decrease it.

---

## Quick Summary

```
+------------------------------------------+
|        LOGISTIC REGRESSION               |
+------------------------------------------+
|                                          |
| Purpose: Classification (not regression!)|
|                                          |
| How it works:                            |
| 1. Calculate weighted sum (like linear)  |
| 2. Pass through sigmoid function         |
| 3. Output probability between 0 and 1   |
| 4. If probability >= 0.5 -> class 1     |
|    If probability <  0.5 -> class 0     |
|                                          |
| Key concepts:                            |
| - Sigmoid: squeezes any number to 0-1   |
| - Decision boundary: where P = 0.5      |
| - Confusion matrix: TP, TN, FP, FN      |
|                                          |
| Remember:                                |
| - Scale features first!                  |
| - Check confusion matrix, not just       |
|   accuracy                               |
| - Works for binary AND multi-class       |
+------------------------------------------+
```

---

## Key Points

- **Logistic regression** is a classification algorithm despite having "regression" in its name.
- The **sigmoid function** converts any number into a probability between 0 and 1.
- The **decision boundary** is where the predicted probability equals 0.5.
- **Feature scaling** is critical for logistic regression to work properly.
- The **confusion matrix** shows True Positives, True Negatives, False Positives, and False Negatives.
- **Precision** measures accuracy of positive predictions. **Recall** measures how many actual positives were caught.
- Logistic regression can handle **multi-class** problems using the One-vs-Rest strategy.
- Always use logistic regression as your **baseline** model for classification.

---

## Practice Questions

1. Why can we not use linear regression for classification problems? What happens when linear regression predicts a value like 1.5 for a binary problem?

2. A model has this confusion matrix:
   ```
   [[90, 10],
    [20, 80]]
   ```
   What is the accuracy? What is the precision for class 1? What is the recall for class 1?

3. You train a logistic regression model and get a "ConvergenceWarning". What does this mean and how do you fix it?

4. Explain the difference between `predict()` and `predict_proba()` in scikit-learn. When would you use one over the other?

5. Your dataset has 950 samples of class 0 and 50 samples of class 1. Why might accuracy be misleading? What should you do?

---

## Exercises

### Exercise 1: Email Spam Classifier

Create a logistic regression model that classifies emails as spam or not spam based on features like word count, number of exclamation marks, and number of links. Generate synthetic data, train the model, and show the confusion matrix.

### Exercise 2: Multi-Class Fruit Classifier

Build a model that classifies fruits into three categories (apple, banana, orange) based on features like weight, color_score, and roundness. Use logistic regression with multi-class support. Show the classification report and probabilities.

### Exercise 3: Threshold Tuning

Using the customer purchase prediction example from this chapter, experiment with different decision thresholds (0.3, 0.5, 0.7). Show how changing the threshold affects precision and recall. When would you lower the threshold? When would you raise it?

---

## What Is Next?

You now know logistic regression, the foundation of classification. But logistic regression draws straight decision boundaries. What if the boundary between classes is curved or complex?

In the next chapter, you will learn about **K-Nearest Neighbors (KNN)**, an algorithm that makes predictions by looking at the closest data points. It is like asking your neighbors for advice -- simple but surprisingly effective.
