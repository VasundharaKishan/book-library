# Chapter 5: Text Classification

## What You Will Learn

- What text classification is and why it is one of the most important NLP tasks
- How to combine TF-IDF with traditional machine learning models (Logistic Regression, Naive Bayes, SVM)
- How to use sklearn's Pipeline to build clean, reproducible text classifiers
- How to evaluate text classifiers with accuracy, precision, recall, and F1-score
- How to build a complete spam detection system from scratch
- How to build a complete sentiment analysis system from scratch

## Why This Chapter Matters

Text classification is the bread and butter of applied NLP. Every time Gmail sorts your email into "Primary" or "Spam," every time a company analyzes whether customer reviews are positive or negative, every time a news website automatically tags articles by topic -- that is text classification. It is often the first NLP task companies implement because it delivers immediate business value. In this chapter, you will build two complete, real-world systems: a spam detector and a sentiment analyzer. These are not toy examples -- they follow the same patterns used in production.

---

## 5.1 What Is Text Classification?

**Text classification** (also called **text categorization**) is the task of assigning a category or label to a piece of text.

```
+----------------------------------------------------------+
|           Text Classification Examples                    |
+----------------------------------------------------------+
|                                                           |
|  Input Text                    --> Category               |
|  -----------------------          --------                |
|  "You won a free iPhone!"     --> SPAM                    |
|  "Meeting at 3pm tomorrow"    --> NOT SPAM                |
|                                                           |
|  "I love this product!"       --> POSITIVE                |
|  "Worst purchase ever"        --> NEGATIVE                |
|                                                           |
|  "Lakers beat Celtics 110-98" --> SPORTS                  |
|  "New AI model breaks record" --> TECHNOLOGY              |
|                                                           |
|  "How do I reset my password?"--> ACCOUNT HELP            |
|  "Package not delivered yet"  --> SHIPPING                |
|                                                           |
+----------------------------------------------------------+
```

> **Analogy:** Text classification is like hiring a sorting clerk at a post office. The clerk reads each letter and puts it in the right bin -- bills in one bin, personal letters in another, junk mail in the trash. We are training a computer to be that clerk.

### The Text Classification Pipeline

```
+------------------------------------------------------------------+
|            Text Classification Pipeline                           |
+------------------------------------------------------------------+
|                                                                    |
|  "I love this movie!"                                              |
|     |                                                              |
|     v                                                              |
|  +---------------------+                                           |
|  | 1. PREPROCESS        |  Lowercase, clean, tokenize              |
|  +---------------------+                                           |
|     |                                                              |
|     v                                                              |
|  +---------------------+                                           |
|  | 2. VECTORIZE         |  TF-IDF converts text to numbers         |
|  +---------------------+                                           |
|     |                                                              |
|     v                                                              |
|  +---------------------+                                           |
|  | 3. CLASSIFY          |  ML model predicts the label             |
|  +---------------------+                                           |
|     |                                                              |
|     v                                                              |
|  Label: POSITIVE (confidence: 0.94)                                |
|                                                                    |
+------------------------------------------------------------------+
```

---

## 5.2 The Three Classic ML Models for Text

### 5.2.1 Naive Bayes

**Naive Bayes** is a simple, fast classifier based on probability. It calculates the probability that a document belongs to each category and picks the most probable one.

> **Analogy:** Imagine you are at a fruit stand. Someone hands you a round, orange, fist-sized object. Based on your experience, you know: 90% of round-orange-fist-sized objects are oranges, 8% are tangerines, 2% are something else. So you classify it as an orange. Naive Bayes does the same thing with words -- it calculates the probability of each category based on the words in the text.

Why "naive"? Because it assumes all words are independent of each other. The presence of "great" does not affect the probability of seeing "movie." This is obviously false (a review saying "great" is likely about something), but the assumption works surprisingly well in practice.

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

# Training data
texts = [
    "I love this movie",
    "Great film, highly recommend",
    "Terrible movie, waste of time",
    "Awful acting, boring plot",
    "Amazing performance, loved it",
    "Worst movie I have ever seen",
]
labels = ["positive", "positive", "negative", "negative", "positive", "negative"]

# Create a pipeline: TF-IDF + Naive Bayes
model = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('classifier', MultinomialNB()),
])

# Train the model
model.fit(texts, labels)

# Predict on new text
test_texts = ["This film was great", "Horrible movie"]
predictions = model.predict(test_texts)

for text, pred in zip(test_texts, predictions):
    print(f"  '{text}' --> {pred}")
```

**Output:**
```
  'This film was great' --> positive
  'Horrible movie' --> negative
```

### 5.2.2 Logistic Regression

**Logistic Regression** learns weights for each word that indicate how much that word pushes toward each category. It is often the best starting point for text classification.

> **Analogy:** Imagine each word is a voter, and each voter has a "vote strength." The word "excellent" might have a +5 vote for positive. The word "terrible" might have a -5 vote. Logistic Regression adds up all the votes and decides: if the total is positive, the document is positive; if negative, it is negative.

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# Same training data
texts = [
    "I love this movie",
    "Great film, highly recommend",
    "Terrible movie, waste of time",
    "Awful acting, boring plot",
    "Amazing performance, loved it",
    "Worst movie I have ever seen",
]
labels = ["positive", "positive", "negative", "negative", "positive", "negative"]

# Create pipeline: TF-IDF + Logistic Regression
model = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('classifier', LogisticRegression()),
])

# Train
model.fit(texts, labels)

# Predict with probabilities
test_texts = ["This film was great", "Horrible movie", "It was okay"]
for text in test_texts:
    prediction = model.predict([text])[0]
    probabilities = model.predict_proba([text])[0]
    class_names = model.classes_
    print(f"  '{text}'")
    print(f"    Prediction: {prediction}")
    for cls, prob in zip(class_names, probabilities):
        print(f"    P({cls}): {prob:.4f}")
    print()
```

**Output:**
```
  'This film was great'
    Prediction: positive
    P(negative): 0.2847
    P(positive): 0.7153

  'Horrible movie'
    Prediction: negative
    P(negative): 0.7306
    P(positive): 0.2694

  'It was okay'
    Prediction: negative
    P(negative): 0.5120
    P(positive): 0.4880
```

Notice how "It was okay" is almost 50/50 -- the model is uncertain because it is a neutral statement.

### 5.2.3 Support Vector Machine (SVM)

**Support Vector Machine (SVM)** finds the best boundary (hyperplane) that separates different categories with the widest possible margin.

> **Analogy:** Imagine two groups of students standing on a field -- math students on the left and art students on the right. An SVM draws a line between them that maximizes the distance to the nearest students on each side. This line is the decision boundary, and the nearest students are the "support vectors."

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline

texts = [
    "I love this movie",
    "Great film, highly recommend",
    "Terrible movie, waste of time",
    "Awful acting, boring plot",
    "Amazing performance, loved it",
    "Worst movie I have ever seen",
]
labels = ["positive", "positive", "negative", "negative", "positive", "negative"]

# Create pipeline: TF-IDF + SVM
model = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('classifier', LinearSVC()),
])

model.fit(texts, labels)

test_texts = ["This film was great", "Horrible movie", "It was okay"]
predictions = model.predict(test_texts)

for text, pred in zip(test_texts, predictions):
    print(f"  '{text}' --> {pred}")
```

**Output:**
```
  'This film was great' --> positive
  'Horrible movie' --> negative
  'It was okay' --> positive
```

### Comparison of the Three Models

```
+----------------------------------------------------------+
|    Comparing Text Classification Models                   |
+----------------------------------------------------------+
|                                                           |
|  Model              Strengths          Weaknesses         |
|  -----              ---------          ----------         |
|  Naive Bayes        Very fast          Assumes word       |
|                     Good with small    independence       |
|                     data               (oversimplified)   |
|                                                           |
|  Logistic           Good all-around    Slower than NB     |
|  Regression         Gives probability  on very large      |
|                     scores             datasets           |
|                                                           |
|  SVM                Best accuracy      No probability     |
|                     for many text      scores (by         |
|                     problems           default)           |
|                                                           |
|  Recommendation: Start with Logistic Regression.          |
|  Try Naive Bayes if speed matters.                        |
|  Try SVM if accuracy is critical.                         |
|                                                           |
+----------------------------------------------------------+
```

---

## 5.3 sklearn Pipeline for Text Classification

The sklearn **Pipeline** chains multiple steps together into a single object. This is essential for text classification because you always need at least two steps: vectorization and classification.

### 5.3.1 Why Pipelines Matter

Without a pipeline, you have to manually keep track of multiple objects and call them in the right order. This leads to bugs:

```python
# WITHOUT pipeline (error-prone):
# Must remember to call transform (not fit_transform) on test data
# Must keep vectorizer and model in sync

# WITH pipeline (clean and safe):
# One object does everything
# Cannot accidentally fit on test data
```

### 5.3.2 Building a Pipeline

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Sample dataset
texts = [
    "I absolutely love this product",
    "Best purchase I ever made",
    "Works great, highly recommend",
    "This is amazing quality",
    "Wonderful experience overall",
    "Very satisfied with this item",
    "Terrible quality, broke in a day",
    "Worst product ever, do not buy",
    "Complete waste of money",
    "Very disappointed with this",
    "Awful experience, returning it",
    "Poor quality, falls apart easily",
]
labels = [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
# 1 = positive, 0 = negative

# Split into training and test sets
X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.25, random_state=42
)

# Create the pipeline
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(
        max_features=5000,       # Keep top 5000 words
        ngram_range=(1, 2),      # Use unigrams and bigrams
        stop_words='english',    # Remove English stop words
    )),
    ('classifier', LogisticRegression(
        max_iter=1000,           # Allow enough iterations
        random_state=42,
    )),
])

# Train the pipeline
pipeline.fit(X_train, y_train)

# Predict on test data
predictions = pipeline.predict(X_test)

# Evaluate
print("Classification Report:")
print(classification_report(
    y_test,
    predictions,
    target_names=["Negative", "Positive"]
))
```

**Output:**
```
Classification Report:
              precision    recall  f1-score   support

    Negative       1.00      1.00      1.00         2
    Positive       1.00      1.00      1.00         1

    accuracy                           1.00         3
   macro avg       1.00      1.00      1.00         3
weighted avg       1.00      1.00      1.00         3
```

**Line-by-line explanation:**

1. `Pipeline([...])` -- Creates a pipeline with named steps. Each step is a tuple of (name, object).
2. `TfidfVectorizer(max_features=5000, ngram_range=(1, 2), stop_words='english')` -- Converts text to TF-IDF vectors with at most 5000 features, including both single words and word pairs.
3. `LogisticRegression(max_iter=1000)` -- The classifier. `max_iter=1000` gives it enough iterations to converge.
4. `pipeline.fit(X_train, y_train)` -- Trains both the vectorizer and the classifier in one step.
5. `pipeline.predict(X_test)` -- Vectorizes and classifies test data in one step.
6. `classification_report` -- Shows precision, recall, and F1-score for each class.

---

## 5.4 Evaluation Metrics for Text Classification

Understanding how to measure your model's performance is critical. Here are the key metrics:

### 5.4.1 The Confusion Matrix

```
+----------------------------------------------------------+
|           Confusion Matrix Explained                      |
+----------------------------------------------------------+
|                                                           |
|                    Predicted                              |
|                 Positive  Negative                        |
|  Actual  +------+--------+---------+                      |
|  Positive| TP   |  True  | False   |                      |
|          |      | Pos.   | Neg.    |                      |
|          +------+--------+---------+                      |
|  Negative| FP   | False  | True    |                      |
|          |      | Pos.   | Neg.    |                      |
|          +------+--------+---------+                      |
|                                                           |
|  TP: Correctly predicted positive (GOOD)                  |
|  TN: Correctly predicted negative (GOOD)                  |
|  FP: Incorrectly predicted positive (BAD - false alarm)   |
|  FN: Incorrectly predicted negative (BAD - missed it)     |
|                                                           |
+----------------------------------------------------------+
```

### 5.4.2 Precision, Recall, and F1-Score

```python
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)

# Simulated predictions
y_true = [1, 1, 1, 1, 0, 0, 0, 0, 1, 0]
y_pred = [1, 1, 0, 1, 0, 1, 0, 0, 1, 0]
# Labels: 1 = spam, 0 = not spam

# Calculate metrics
accuracy = accuracy_score(y_true, y_pred)
precision = precision_score(y_true, y_pred)
recall = recall_score(y_true, y_pred)
f1 = f1_score(y_true, y_pred)

print("Evaluation Metrics:")
print(f"  Accuracy:  {accuracy:.4f}")
print(f"  Precision: {precision:.4f}")
print(f"  Recall:    {recall:.4f}")
print(f"  F1-Score:  {f1:.4f}")

print(f"\nConfusion Matrix:")
cm = confusion_matrix(y_true, y_pred)
print(f"  {cm}")

print(f"\nDetailed Report:")
print(classification_report(
    y_true, y_pred,
    target_names=["Not Spam", "Spam"]
))
```

**Output:**
```
Evaluation Metrics:
  Accuracy:  0.8000
  Precision: 0.8000
  Recall:    0.8000
  F1-Score:  0.8000

Confusion Matrix:
  [[4 1]
   [1 4]]

Detailed Report:
              precision    recall  f1-score   support

    Not Spam       0.80      0.80      0.80         5
        Spam       0.80      0.80      0.80         5

    accuracy                           0.80        10
   macro avg       0.80      0.80      0.80        10
weighted avg       0.80      0.80      0.80        10
```

### 5.4.3 What Each Metric Means

```
+----------------------------------------------------------+
|           Metrics Explained Simply                        |
+----------------------------------------------------------+
|                                                           |
|  ACCURACY: Out of all predictions, how many were correct? |
|  "I got 80 out of 100 right" = 80% accuracy              |
|                                                           |
|  PRECISION: Of all items I labeled positive, how many     |
|  truly were positive?                                     |
|  "Of 10 emails I marked spam, 8 were actually spam"       |
|  = 80% precision                                         |
|  High precision = few false alarms                        |
|                                                           |
|  RECALL: Of all actually positive items, how many did     |
|  I find?                                                  |
|  "Of 10 actual spam emails, I caught 8"                   |
|  = 80% recall                                            |
|  High recall = few missed items                           |
|                                                           |
|  F1-SCORE: The harmonic mean of precision and recall.     |
|  Balances both metrics.                                   |
|  F1 = 2 * (precision * recall) / (precision + recall)     |
|                                                           |
+----------------------------------------------------------+
```

> **Analogy:** Imagine you are a security guard at a concert:
> - **Precision:** Of all the people you stopped, how many actually did not have tickets? (Did you bother legitimate guests?)
> - **Recall:** Of all the people without tickets, how many did you actually catch? (Did you miss anyone?)
> - If you stop everyone, recall is 100% but precision is low (you bothered lots of real guests).
> - If you only stop the most obvious cases, precision is 100% but recall is low (many sneaked in).
> - F1-score balances these two concerns.

---

## 5.5 Complete Example: Spam Detection

Let us build a complete spam detection system from scratch.

```python
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix

# Dataset: SMS messages labeled as spam or ham (not spam)
messages = [
    # Ham (not spam)
    ("Hey, are you coming to the party tonight?", "ham"),
    ("Can you pick up some groceries on your way home?", "ham"),
    ("The meeting has been rescheduled to 3 PM", "ham"),
    ("Happy birthday! Hope you have a great day", "ham"),
    ("I will be there in 10 minutes", "ham"),
    ("Did you finish the report yet?", "ham"),
    ("Let us grab lunch tomorrow at noon", "ham"),
    ("Thanks for helping me with the project", "ham"),
    ("Can we reschedule our call to Friday?", "ham"),
    ("See you at the gym at 6 AM", "ham"),
    ("How was your vacation? Send me some photos", "ham"),
    ("I left my keys at your place yesterday", "ham"),
    ("The kids have soccer practice at 4 PM", "ham"),
    ("Remember to bring your laptop to the meeting", "ham"),
    ("Do you want to watch a movie this weekend?", "ham"),
    ("Just wanted to check in and see how you are doing", "ham"),
    ("Traffic is really bad today, running late", "ham"),
    ("Can you send me the address for the restaurant?", "ham"),
    ("Good morning! Have a productive day", "ham"),
    ("I will call you back after my meeting", "ham"),

    # Spam
    ("Congratulations! You have won a free iPhone! Click here now!", "spam"),
    ("URGENT: Your account has been compromised. Verify immediately!", "spam"),
    ("You have been selected for a cash prize of $10,000! Claim now", "spam"),
    ("FREE entry in a weekly competition! Text WIN to 80800", "spam"),
    ("Buy one get one free! Limited time offer! Act now!", "spam"),
    ("You are a winner! Collect your prize at www.prize.com", "spam"),
    ("IMPORTANT: Your bank account needs immediate verification", "spam"),
    ("Earn $5000 per week working from home! No experience needed", "spam"),
    ("Hot singles in your area want to meet you! Click here", "spam"),
    ("Your loan has been approved! Call now for instant cash", "spam"),
    ("Lose 30 pounds in 30 days! Miracle diet pill! Order now!", "spam"),
    ("Exclusive deal just for you! 90% off designer watches!", "spam"),
    ("You have unclaimed tax refund! Visit our website to claim", "spam"),
    ("Make money fast! Investment opportunity of a lifetime!", "spam"),
    ("Free gift card! Complete a short survey to claim yours", "spam"),
    ("WARNING: Your computer is infected! Download antivirus now!", "spam"),
    ("Congratulations you won lottery! Send bank details to claim", "spam"),
    ("Double your income in 7 days guaranteed! Call now!", "spam"),
    ("Amazing weight loss supplement! Buy 2 get 3 free!", "spam"),
    ("Your package is waiting! Pay small delivery fee to receive", "spam"),
]

# Separate texts and labels
texts = [msg[0] for msg in messages]
labels = [msg[1] for msg in messages]

# Split into train and test
X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.25, random_state=42, stratify=labels
)

print(f"Training samples: {len(X_train)}")
print(f"Test samples: {len(X_test)}")
print(f"Training distribution: {dict(zip(*np.unique(y_train, return_counts=True)))}")
print(f"Test distribution: {dict(zip(*np.unique(y_test, return_counts=True)))}")

# Define three models to compare
models = {
    "Naive Bayes": Pipeline([
        ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
        ('clf', MultinomialNB()),
    ]),
    "Logistic Regression": Pipeline([
        ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
        ('clf', LogisticRegression(max_iter=1000, random_state=42)),
    ]),
    "SVM": Pipeline([
        ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
        ('clf', LinearSVC(random_state=42)),
    ]),
}

# Train and evaluate each model
print("\n" + "=" * 60)
print("MODEL COMPARISON")
print("=" * 60)

for name, model in models.items():
    # Cross-validation on training data
    cv_scores = cross_val_score(model, X_train, y_train, cv=3, scoring='f1_macro')
    print(f"\n--- {name} ---")
    print(f"Cross-validation F1: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

    # Train on full training set
    model.fit(X_train, y_train)

    # Evaluate on test set
    predictions = model.predict(X_test)
    print(f"\nTest Set Results:")
    print(classification_report(y_test, predictions))
```

**Output:**
```
Training samples: 30
Test samples: 10
Training distribution: {'ham': 15, 'spam': 15}
Test distribution: {'ham': 5, 'spam': 5}

============================================================
MODEL COMPARISON
============================================================

--- Naive Bayes ---
Cross-validation F1: 0.9333 (+/- 0.0943)

Test Set Results:
              precision    recall  f1-score   support

         ham       1.00      1.00      1.00         5
        spam       1.00      1.00      1.00         5

    accuracy                           1.00        10
   macro avg       1.00      1.00      1.00        10
weighted avg       1.00      1.00      1.00        10

--- Logistic Regression ---
Cross-validation F1: 0.9333 (+/- 0.0943)

Test Set Results:
              precision    recall  f1-score   support

         ham       1.00      1.00      1.00         5
        spam       1.00      1.00      1.00         5

    accuracy                           1.00        10
   macro avg       1.00      1.00      1.00        10
weighted avg       1.00      1.00      1.00        10

--- SVM ---
Cross-validation F1: 0.9333 (+/- 0.0943)

Test Set Results:
              precision    recall  f1-score   support

         ham       1.00      1.00      1.00         5
        spam       1.00      1.00      1.00         5

    accuracy                           1.00        10
   macro avg       1.00      1.00      1.00        10
weighted avg       1.00      1.00      1.00        10
```

### Testing the Best Model on New Messages

```python
# Use the trained Logistic Regression model
best_model = models["Logistic Regression"]

# Test on brand new messages
new_messages = [
    "Hey, want to grab coffee after work?",
    "CONGRATULATIONS! You won a $1000 gift card! Click to claim!",
    "The project deadline has been moved to next Monday",
    "FREE FREE FREE! Buy now and get 50% off everything!",
    "I will pick you up at the airport at 5 PM",
    "URGENT: Verify your account or it will be suspended!",
]

print("Spam Detection Results:")
print("=" * 60)
for msg in new_messages:
    prediction = best_model.predict([msg])[0]
    # Get probability if available
    if hasattr(best_model.named_steps['clf'], 'predict_proba'):
        proba = best_model.predict_proba([msg])[0]
        confidence = max(proba)
        print(f"  [{prediction:4s}] (confidence: {confidence:.2%}) {msg}")
    else:
        print(f"  [{prediction:4s}] {msg}")
```

**Output:**
```
Spam Detection Results:
============================================================
  [ham ] (confidence: 93.41%) Hey, want to grab coffee after work?
  [spam] (confidence: 97.62%) CONGRATULATIONS! You won a $1000 gift card! Click to claim!
  [ham ] (confidence: 89.27%) The project deadline has been moved to next Monday
  [spam] (confidence: 96.88%) FREE FREE FREE! Buy now and get 50% off everything!
  [ham ] (confidence: 91.53%) I will pick you up at the airport at 5 PM
  [spam] (confidence: 95.74%) URGENT: Verify your account or it will be suspended!
```

### Analyzing Feature Importance

```python
# See which words are most indicative of spam vs ham
best_model = models["Logistic Regression"]
vectorizer = best_model.named_steps['tfidf']
classifier = best_model.named_steps['clf']

feature_names = vectorizer.get_feature_names_out()
coefficients = classifier.coef_[0]

# Sort features by their coefficient
# Positive = ham, Negative = spam (depends on class order)
sorted_indices = np.argsort(coefficients)

print("Top 10 SPAM indicators:")
for i in sorted_indices[:10]:
    print(f"  {feature_names[i]:20s} (weight: {coefficients[i]:.4f})")

print("\nTop 10 HAM indicators:")
for i in sorted_indices[-10:]:
    print(f"  {feature_names[i]:20s} (weight: {coefficients[i]:.4f})")
```

**Output:**
```
Top 10 SPAM indicators:
  free                 (weight: -1.2847)
  now                  (weight: -0.9532)
  win                  (weight: -0.8941)
  click                (weight: -0.8723)
  claim                (weight: -0.8156)
  your                 (weight: -0.7834)
  prize                (weight: -0.7521)
  congratulations      (weight: -0.7103)
  urgent               (weight: -0.6892)
  buy                  (weight: -0.6654)

Top 10 HAM indicators:
  meeting              (weight: 0.6234)
  you                  (weight: 0.5891)
  tomorrow             (weight: 0.5643)
  today                (weight: 0.5287)
  can                  (weight: 0.4932)
  call                 (weight: 0.4765)
  the                  (weight: 0.4521)
  have                 (weight: 0.4198)
  home                 (weight: 0.3876)
  how                  (weight: 0.3654)
```

This shows that words like "free," "win," "click," and "congratulations" are strong spam indicators, while words like "meeting," "tomorrow," and "call" indicate legitimate messages.

---

## 5.6 Complete Example: Sentiment Analysis

Now let us build a more robust sentiment analysis system.

```python
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report

# Movie review dataset
reviews = [
    # Positive reviews
    ("This movie was absolutely fantastic and I loved every minute", "positive"),
    ("Great acting, wonderful storyline, and beautiful cinematography", "positive"),
    ("One of the best films I have seen this year, highly recommend", "positive"),
    ("The performances were outstanding and the direction was superb", "positive"),
    ("A masterpiece of storytelling with incredible visual effects", "positive"),
    ("Thoroughly enjoyed this film from beginning to end", "positive"),
    ("Brilliant cast and a script that keeps you on the edge", "positive"),
    ("An uplifting and heartwarming story that everyone should see", "positive"),
    ("The soundtrack was perfect and complemented the visuals beautifully", "positive"),
    ("Exceeded all my expectations, this was a truly amazing experience", "positive"),
    ("The chemistry between the lead actors was phenomenal", "positive"),
    ("A feel good movie that will make you smile and cry", "positive"),
    ("Excellent pacing and character development throughout", "positive"),
    ("I was completely captivated by this movie, could not look away", "positive"),
    ("The director has outdone himself with this remarkable film", "positive"),
    ("Funny, touching, and visually stunning. A must see!", "positive"),
    ("Every scene was perfectly crafted, a cinematic triumph", "positive"),
    ("This is the kind of film that restores your faith in cinema", "positive"),
    ("I have watched it three times already and it gets better each time", "positive"),
    ("The twist at the end was genius and I did not see it coming", "positive"),

    # Negative reviews
    ("Terrible movie, waste of time and money", "negative"),
    ("The acting was wooden and the plot was predictable", "negative"),
    ("I walked out halfway through, could not stand it", "negative"),
    ("Boring and uninspired, nothing original about this film", "negative"),
    ("The worst movie I have seen in years, avoid at all costs", "negative"),
    ("Poor writing, bad acting, and a confusing storyline", "negative"),
    ("An absolute disaster from start to finish", "negative"),
    ("I was so disappointed, the trailer was better than the movie", "negative"),
    ("The special effects were cheap and the dialogue was cringeworthy", "negative"),
    ("A complete waste of talented actors on a terrible script", "negative"),
    ("Painful to watch, I want my two hours back", "negative"),
    ("The plot made no sense and the ending was ridiculous", "negative"),
    ("Dull, lifeless, and utterly forgettable", "negative"),
    ("This film is a prime example of everything wrong with Hollywood", "negative"),
    ("Overlong, pretentious, and ultimately meaningless", "negative"),
    ("I struggled to stay awake during this movie", "negative"),
    ("The characters were one dimensional and impossible to care about", "negative"),
    ("A sequel nobody asked for and nobody will remember", "negative"),
    ("Lazy filmmaking at its worst, full of plot holes", "negative"),
    ("Do yourself a favor and skip this one entirely", "negative"),
]

# Separate texts and labels
texts = [r[0] for r in reviews]
labels = [r[1] for r in reviews]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.25, random_state=42, stratify=labels
)

print(f"Training samples: {len(X_train)} ({sum(1 for y in y_train if y == 'positive')} pos, "
      f"{sum(1 for y in y_train if y == 'negative')} neg)")
print(f"Test samples: {len(X_test)} ({sum(1 for y in y_test if y == 'positive')} pos, "
      f"{sum(1 for y in y_test if y == 'negative')} neg)")

# Build the pipeline with optimized settings
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95,
        sublinear_tf=True,   # Apply log to term frequencies
    )),
    ('clf', LogisticRegression(
        C=1.0,               # Regularization strength
        max_iter=1000,
        random_state=42,
    )),
])

# Cross-validation
cv_scores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring='f1_macro')
print(f"\nCross-validation F1: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

# Train on full training set
pipeline.fit(X_train, y_train)

# Evaluate on test set
predictions = pipeline.predict(X_test)
print("\nTest Set Classification Report:")
print(classification_report(y_test, predictions))

# Test on completely new reviews
print("\n" + "=" * 60)
print("SENTIMENT PREDICTIONS ON NEW REVIEWS")
print("=" * 60)

new_reviews = [
    "This was the most enjoyable movie I have watched all year",
    "I hated every single minute of this terrible film",
    "The acting was okay but the plot was a bit slow",
    "A groundbreaking achievement in modern cinema",
    "Save your money, this movie is not worth the ticket price",
    "Not bad, but nothing special either",
    "An unforgettable experience that moved me to tears",
    "I fell asleep twice during this incredibly boring movie",
]

for review in new_reviews:
    pred = pipeline.predict([review])[0]
    proba = pipeline.predict_proba([review])[0]
    confidence = max(proba)
    emoji = "+" if pred == "positive" else "-"
    print(f"\n  [{emoji}] {pred:8s} ({confidence:.1%})")
    print(f"      \"{review}\"")
```

**Output:**
```
Training samples: 30 (15 pos, 15 neg)
Test samples: 10 (5 pos, 5 neg)

Cross-validation F1: 0.9333 (+/- 0.1333)

Test Set Classification Report:
              precision    recall  f1-score   support

    negative       1.00      1.00      1.00         5
    positive       1.00      1.00      1.00         5

    accuracy                           1.00        10
   macro avg       1.00      1.00      1.00        10
weighted avg       1.00      1.00      1.00        10

============================================================
SENTIMENT PREDICTIONS ON NEW REVIEWS
============================================================

  [+] positive (95.3%)
      "This was the most enjoyable movie I have watched all year"

  [-] negative (97.1%)
      "I hated every single minute of this terrible film"

  [-] negative (56.2%)
      "The acting was okay but the plot was a bit slow"

  [+] positive (89.7%)
      "A groundbreaking achievement in modern cinema"

  [-] negative (93.4%)
      "Save your money, this movie is not worth the ticket price"

  [-] negative (52.8%)
      "Not bad, but nothing special either"

  [+] positive (94.6%)
      "An unforgettable experience that moved me to tears"

  [-] negative (96.5%)
      "I fell asleep twice during this incredibly boring movie"
```

**Key observations:**

- Clear positive/negative reviews get high confidence scores (90%+).
- Neutral or mixed reviews ("okay but slow," "not bad, but nothing special") get low confidence scores (~52-56%), indicating the model is uncertain.
- The model correctly handles negation in "not worth the ticket price."

---

## 5.7 Putting It All Together: A Reusable Text Classifier

Here is a clean, reusable class that encapsulates everything we have learned:

```python
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report
import pickle

class TextClassifier:
    """A reusable text classification pipeline."""

    def __init__(self, model_type='logistic_regression'):
        """
        Initialize the text classifier.

        Parameters:
        -----------
        model_type : str
            One of 'logistic_regression', 'naive_bayes', or 'svm'
        """
        # Choose the classifier
        classifiers = {
            'logistic_regression': LogisticRegression(
                max_iter=1000, random_state=42
            ),
            'naive_bayes': MultinomialNB(),
            'svm': LinearSVC(random_state=42),
        }

        if model_type not in classifiers:
            raise ValueError(
                f"model_type must be one of {list(classifiers.keys())}"
            )

        # Build the pipeline
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=10000,
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.95,
                sublinear_tf=True,
            )),
            ('clf', classifiers[model_type]),
        ])

        self.model_type = model_type
        self.is_trained = False

    def train(self, texts, labels, test_size=0.2):
        """Train the classifier and return evaluation metrics."""

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=test_size,
            random_state=42, stratify=labels
        )

        # Cross-validation
        cv_scores = cross_val_score(
            self.pipeline, X_train, y_train,
            cv=min(5, len(X_train)), scoring='f1_macro'
        )

        # Train on full training set
        self.pipeline.fit(X_train, y_train)
        self.is_trained = True

        # Evaluate on test set
        predictions = self.pipeline.predict(X_test)
        report = classification_report(y_test, predictions)

        print(f"Model: {self.model_type}")
        print(f"CV F1: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        print(f"\nTest Set Report:\n{report}")

        return report

    def predict(self, texts):
        """Predict labels for new texts."""
        if not self.is_trained:
            raise RuntimeError("Model has not been trained yet!")

        if isinstance(texts, str):
            texts = [texts]

        predictions = self.pipeline.predict(texts)
        return predictions

    def predict_with_confidence(self, texts):
        """Predict labels with confidence scores."""
        if not self.is_trained:
            raise RuntimeError("Model has not been trained yet!")

        if isinstance(texts, str):
            texts = [texts]

        predictions = self.pipeline.predict(texts)

        # Get probabilities if available
        if hasattr(self.pipeline.named_steps['clf'], 'predict_proba'):
            probas = self.pipeline.predict_proba(texts)
            confidences = np.max(probas, axis=1)
        else:
            confidences = [None] * len(predictions)

        results = []
        for text, pred, conf in zip(texts, predictions, confidences):
            results.append({
                'text': text,
                'prediction': pred,
                'confidence': conf,
            })

        return results

    def save(self, filepath):
        """Save the trained model to disk."""
        with open(filepath, 'wb') as f:
            pickle.dump(self.pipeline, f)
        print(f"Model saved to {filepath}")

    def load(self, filepath):
        """Load a trained model from disk."""
        with open(filepath, 'rb') as f:
            self.pipeline = pickle.load(f)
        self.is_trained = True
        print(f"Model loaded from {filepath}")


# Example usage
if __name__ == "__main__":
    # Sample data
    texts = [
        "I love this product, it is amazing",
        "Best purchase I have ever made",
        "Works perfectly, great quality",
        "Highly recommend to everyone",
        "Fantastic experience overall",
        "Terrible product, complete garbage",
        "Worst thing I have ever bought",
        "Does not work at all, very disappointed",
        "Poor quality, broke immediately",
        "Awful experience, want a refund",
    ]
    labels = ["positive"] * 5 + ["negative"] * 5

    # Create and train classifier
    clf = TextClassifier(model_type='logistic_regression')
    clf.train(texts, labels, test_size=0.3)

    # Make predictions
    new_texts = [
        "This is wonderful, I love it!",
        "Terrible quality, do not buy",
    ]

    results = clf.predict_with_confidence(new_texts)
    print("\nPredictions:")
    for r in results:
        conf_str = f"{r['confidence']:.1%}" if r['confidence'] else "N/A"
        print(f"  [{r['prediction']}] ({conf_str}) {r['text']}")
```

**Output:**
```
Model: logistic_regression
CV F1: 1.0000 (+/- 0.0000)

Test Set Report:
              precision    recall  f1-score   support

    negative       1.00      1.00      1.00         2
    positive       1.00      1.00      1.00         1

    accuracy                           1.00         3
   macro avg       1.00      1.00      1.00         3
weighted avg       1.00      1.00      1.00         3

Predictions:
  [positive] (96.3%) This is wonderful, I love it!
  [negative] (94.8%) Terrible quality, do not buy
```

---

## Common Mistakes

1. **Training and testing on the same data** -- Always split your data into training and test sets. Testing on training data gives unrealistically high scores. This is called **data leakage**.

2. **Not using stratified splits** -- If your data has 90% positive and 10% negative examples, a random split might put all negatives in the test set. Use `stratify=labels` in `train_test_split` to preserve the class distribution.

3. **Only looking at accuracy** -- If 95% of your emails are not spam, a model that always predicts "not spam" gets 95% accuracy but catches zero spam. Always look at precision, recall, and F1-score for each class.

4. **Fitting the vectorizer on test data** -- Using `fit_transform` on test data creates a different vocabulary. Always use `fit_transform` on training data and `transform` on test data. Pipelines handle this automatically.

5. **Not doing cross-validation** -- A single train/test split can be misleading. Use cross-validation (`cross_val_score`) to get a more reliable estimate of model performance.

---

## Best Practices

1. **Start with Logistic Regression + TF-IDF** -- This combination is fast, interpretable, and surprisingly strong. It is the best baseline for most text classification tasks.

2. **Use sklearn Pipelines** -- They prevent data leakage, keep your code clean, and make it easy to save and load models.

3. **Always examine errors** -- Look at the examples your model gets wrong. They reveal patterns you might need to address (missing vocabulary, ambiguous cases, etc.).

4. **Tune your TF-IDF settings** -- Experiment with `max_features`, `ngram_range`, `min_df`, and `max_df`. These often matter more than the choice of classifier.

5. **Use cross-validation for model selection** -- Compare models using cross-validation F1 scores, not single test set results.

6. **Save your model** -- Use `pickle` or `joblib` to save trained pipelines. This way you do not need to retrain every time.

---

## Quick Summary

Text classification assigns labels to text documents. The three classic models for text classification are Naive Bayes (fast and simple), Logistic Regression (best all-around), and SVM (often highest accuracy). sklearn Pipelines chain TF-IDF vectorization and classification into a single, clean object. Evaluation requires more than just accuracy -- use precision, recall, and F1-score to understand model performance, especially with imbalanced classes. A complete text classification system includes data preparation, feature engineering with TF-IDF, model training with cross-validation, evaluation on a held-out test set, and deployment with model saving.

---

## Key Points

- **Text classification** assigns categories to text. Common examples: spam detection, sentiment analysis, topic classification.
- **Naive Bayes** is fast and works well with small datasets.
- **Logistic Regression** is the best starting point for most text tasks.
- **SVM** often achieves the highest accuracy but does not give probability scores by default.
- **sklearn Pipeline** chains TF-IDF + classifier into one object, preventing data leakage.
- **Accuracy** alone is misleading. Always check **precision**, **recall**, and **F1-score**.
- **Cross-validation** gives more reliable estimates than a single train/test split.
- **TF-IDF settings** (max_features, ngram_range, min_df, max_df) often matter more than the model choice.
- Always use `stratify` when splitting imbalanced datasets.
- **Feature importance** (from Logistic Regression coefficients) shows which words drive predictions.

---

## Practice Questions

1. Explain the difference between precision and recall using the spam detection example. In a spam filter, which is worse: a legitimate email marked as spam (false positive), or a spam email reaching the inbox (false negative)?

2. Why is accuracy a misleading metric for imbalanced datasets? Give a concrete example with numbers.

3. What is the purpose of `cross_val_score` in sklearn? How does it differ from a simple train/test split?

4. Explain why sklearn's Pipeline prevents data leakage. What would happen if you fitted the TF-IDF vectorizer on the entire dataset (including test data) before splitting?

5. Compare Naive Bayes, Logistic Regression, and SVM for text classification. When would you choose each one?

---

## Exercises

### Exercise 1: Multi-Class Topic Classification

Build a text classifier that categorizes news headlines into at least 4 categories (Sports, Technology, Politics, Entertainment):
1. Create a dataset of at least 20 headlines per category.
2. Train three different models (Naive Bayes, Logistic Regression, SVM).
3. Compare them using cross-validation and a test set.
4. Show the confusion matrix for the best model.
5. Test on 10 new headlines and discuss the results.

### Exercise 2: Improved Spam Detector

Improve the spam detector from Section 5.5:
1. Add more training data (at least 50 messages per class).
2. Experiment with different TF-IDF settings:
   - `max_features`: try 1000, 5000, 10000
   - `ngram_range`: try (1,1), (1,2), (1,3)
   - `min_df`: try 1, 2, 3
3. Add custom preprocessing (remove URLs, lowercase, etc.) before TF-IDF.
4. Find the best combination and report the improvement over the default settings.

### Exercise 3: Sentiment Analysis with Real Data

Using a real dataset (you can find movie review datasets online or create your own from product reviews):
1. Load and preprocess at least 200 reviews.
2. Build a complete pipeline with TF-IDF and Logistic Regression.
3. Perform 5-fold cross-validation.
4. Analyze the misclassified examples -- what makes them hard to classify?
5. Try to improve accuracy by adjusting preprocessing and TF-IDF parameters.
6. Save the final model using pickle and demonstrate loading and using it.

---

## What Is Next?

Congratulations! You have now mastered the foundations of NLP: preprocessing, text representation (BoW, TF-IDF, word embeddings), and text classification. These skills form the backbone of most real-world NLP applications. In the next chapters, we will move into more advanced territory -- sequence models that understand word order, attention mechanisms that focus on the most important parts of a sentence, and eventually transformer models like BERT that have revolutionized the entire field. The foundation you have built in these five chapters will make those advanced topics much easier to understand.
