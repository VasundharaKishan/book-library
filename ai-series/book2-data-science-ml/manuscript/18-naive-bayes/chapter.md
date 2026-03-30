# Chapter 18: Naive Bayes

## What You Will Learn

In this chapter, you will learn:

- A quick recap of Bayes' theorem
- What the "naive" assumption means and why it works anyway
- How to think about Naive Bayes with a detective analogy
- The three types: GaussianNB, MultinomialNB, and BernoulliNB
- Why Naive Bayes is great for text classification
- How to use GaussianNB with the iris dataset
- How to build a spam classifier with MultinomialNB
- The pros and cons of Naive Bayes
- A complete spam detection project with real text data

## Why This Chapter Matters

Sometimes simple beats complex.

Naive Bayes is one of the simplest machine learning algorithms. It is based on basic probability. It makes an assumption that is almost always wrong (features are independent). And yet it works surprisingly well.

Naive Bayes is the go-to algorithm for **text classification**. Spam filters, sentiment analysis, document categorization -- Naive Bayes handles these beautifully. It is also incredibly fast. While SVM might take minutes on a large dataset, Naive Bayes finishes in seconds.

Every data scientist should understand Naive Bayes. It is a perfect example of how a simple model with a "wrong" assumption can outperform complex models in the right situation.

---

## Bayes' Theorem Recap

If you read Book 1, you already know Bayes' theorem. Here is a quick refresher.

**Bayes' theorem** tells us how to update our beliefs when we get new evidence.

```
BAYES' THEOREM:

                    P(B|A) * P(A)
    P(A|B) = -------------------------
                      P(B)

Where:
  P(A|B) = Probability of A given B happened (POSTERIOR)
  P(A)   = Probability of A before evidence  (PRIOR)
  P(B|A) = Probability of B given A is true  (LIKELIHOOD)
  P(B)   = Probability of B overall          (EVIDENCE)
```

### A Simple Example

Suppose you want to know if an email is spam.

```
QUESTION: Is this email spam?

What we know:
  - 30% of all emails are spam         P(Spam) = 0.30
  - 80% of spam emails contain "FREE"  P("FREE"|Spam) = 0.80
  - 10% of normal emails contain "FREE" P("FREE"|Not Spam) = 0.10

The email contains "FREE". Is it spam?

Using Bayes' theorem:

             P("FREE"|Spam) * P(Spam)
P(Spam|"FREE") = ---------------------------------
                         P("FREE")

P("FREE") = P("FREE"|Spam)*P(Spam) + P("FREE"|Not Spam)*P(Not Spam)
          = 0.80 * 0.30 + 0.10 * 0.70
          = 0.24 + 0.07
          = 0.31

             0.80 * 0.30
P(Spam|"FREE") = ----------- = 0.774
                   0.31

Result: 77.4% chance it is spam!
```

The word "FREE" in an email makes it 77.4% likely to be spam. That is Bayes' theorem in action.

---

## The "Naive" Assumption

Naive Bayes is called "naive" because it makes a simplifying assumption:

**All features are independent of each other.**

This means Naive Bayes treats each piece of evidence separately, as if one feature has no connection to any other feature.

### Is This True?

Almost never! In reality, features are usually related:

```
REAL WORLD (features ARE related):

  In an email:
    "FREE" often appears with "CLICK HERE"
    "Meeting" often appears with "agenda"
    Word choices are related to each other

  In medical data:
    High blood pressure relates to age
    Smoking relates to lung disease
    Features are connected
```

### Then Why Does It Work?

Even though the assumption is wrong, Naive Bayes still works well because:

1. **Classification does not need exact probabilities.** It only needs to know which class has the HIGHEST probability. Even if the numbers are wrong, the ranking is often correct.

2. **Errors in assumptions tend to cancel out.** Some probabilities are overestimated, some are underestimated. On average, they balance out.

3. **Simplicity is a strength.** With fewer parameters to estimate, there is less risk of overfitting, especially with small datasets.

```
WHY "NAIVE" STILL WORKS:

Exact probabilities:     Naive estimates:
  Spam:  0.87              Spam:  0.93    <-- Wrong number
  Ham:   0.13              Ham:   0.07    <-- Wrong number

  But both say "SPAM"!     Still says "SPAM"!

  The RANKING is correct even though
  the exact numbers are wrong.
```

---

## The Detective Analogy

Think of Naive Bayes as a detective who considers each clue **independently**.

```
THE NAIVE DETECTIVE:

Crime Scene Evidence:
  Clue 1: Muddy footprints (size 10)
  Clue 2: Red hair found
  Clue 3: Left-handed tool marks

The Naive Detective thinks:

  "What is the chance EACH suspect left each clue,
   independently?"

  Suspect A:
    P(size 10 shoes | A) = 0.8   (A wears size 10)
    P(red hair | A)      = 0.9   (A has red hair)
    P(left-handed | A)   = 0.1   (A is right-handed)

    Combined: 0.8 * 0.9 * 0.1 = 0.072

  Suspect B:
    P(size 10 shoes | B) = 0.3   (B wears size 9)
    P(red hair | B)      = 0.1   (B has brown hair)
    P(left-handed | B)   = 0.9   (B is left-handed)

    Combined: 0.3 * 0.1 * 0.9 = 0.027

  Verdict: Suspect A is more likely! (0.072 > 0.027)
```

A real detective would consider connections between clues. The naive detective treats each clue separately. But the naive detective often gets the right suspect anyway!

### The Math

For classification, Naive Bayes calculates:

```
P(class | feature1, feature2, ..., featureN)

  is proportional to:

P(class) * P(feature1|class) * P(feature2|class) * ... * P(featureN|class)

We pick the class with the HIGHEST result.
```

The key simplification: instead of calculating the complex joint probability of all features together, we just **multiply** the individual probabilities. This is what makes it "naive" -- and fast.

---

## Three Types of Naive Bayes

Different types of Naive Bayes handle different types of data.

### 1. GaussianNB (For Continuous Numbers)

Use when your features are continuous numbers (like height, weight, temperature).

It assumes each feature follows a **Gaussian (normal) distribution** -- the bell curve.

```
GAUSSIAN DISTRIBUTION (Bell Curve):

         *****
       **     **
      *         *
     *           *
    *             *
   *               *
  *                 *
  |       mean      |

  GaussianNB fits a bell curve to each feature
  for each class, then uses the curves to
  calculate probabilities.
```

**Best for:** Numerical measurements, scientific data.

### 2. MultinomialNB (For Counts)

Use when your features are **counts** or **frequencies**. Most commonly used for text data, where features are word counts.

```
MULTINOMIAL DATA (Word Counts):

Email: "Free money free offer click now free"

Word counts:
  free:  3
  money: 1
  offer: 1
  click: 1
  now:   1

MultinomialNB works with these counts.
```

**Best for:** Text classification, document categorization, any count-based features.

### 3. BernoulliNB (For Binary Yes/No)

Use when your features are **binary** (0 or 1, yes or no, true or false).

```
BERNOULLI DATA (Yes/No):

Email features:
  contains "free":    Yes (1)
  contains "money":   Yes (1)
  contains "meeting": No  (0)
  contains "agenda":  No  (0)
  has attachment:     No  (0)
  has link:           Yes (1)

BernoulliNB works with these binary features.
```

**Best for:** Binary feature data, short text documents.

### Comparison Table

```
+-------------------+------------------+--------------------+
| Type              | Data Type        | Example Use        |
+-------------------+------------------+--------------------+
| GaussianNB        | Continuous       | Iris flowers,      |
|                   | numbers          | medical data       |
+-------------------+------------------+--------------------+
| MultinomialNB     | Counts /         | Spam detection,    |
|                   | frequencies      | topic classif.     |
+-------------------+------------------+--------------------+
| BernoulliNB       | Binary           | Feature presence,  |
|                   | (yes/no)         | short texts        |
+-------------------+------------------+--------------------+
```

---

## Why Naive Bayes Is Great for Text Classification

Text classification is the "sweet spot" for Naive Bayes. Here is why:

```
WHY NAIVE BAYES LOVES TEXT:

1. HIGH-DIMENSIONAL DATA
   Vocabulary can have 50,000+ words (features).
   Many algorithms struggle. Naive Bayes thrives.

2. INDEPENDENCE ASSUMPTION IS "OKAY" FOR WORDS
   While words ARE related, treating them independently
   still captures useful patterns.
   "free" + "money" + "click" = probably spam
   (even without knowing they appear together)

3. SPEED
   With 50,000 features, SVM takes hours.
   Naive Bayes takes seconds.

4. SMALL DATA IS FINE
   Text datasets are often small (hundreds of emails).
   Naive Bayes works well with limited training data.

5. HANDLES NEW WORDS
   With Laplace smoothing, it handles words
   it has never seen before.
```

**Laplace smoothing** (also called add-one smoothing) is a technique that adds a small count (usually 1) to every word count. This prevents a probability of zero when a word appears in test data but was not in training data.

---

## GaussianNB Example with Iris

Let us use GaussianNB on the classic iris dataset (numerical features).

```python
from sklearn.naive_bayes import GaussianNB
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report

# Load data
iris = load_iris()
X = iris.data       # 4 numerical features
y = iris.target     # 3 classes

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Create and train GaussianNB
# Note: NO parameters to tune! Very simple.
gnb = GaussianNB()
gnb.fit(X_train, y_train)

# Predict
y_pred = gnb.predict(X_test)

# Evaluate
accuracy = accuracy_score(y_test, y_pred)
print(f"GaussianNB Accuracy: {accuracy:.4f}")
print(f"\nClassification Report:")
print(classification_report(y_test, y_pred,
                            target_names=iris.target_names))

# Cross-validation
cv_scores = cross_val_score(gnb, X, y, cv=5)
print(f"Cross-validation: {cv_scores.mean():.4f} "
      f"(+/- {cv_scores.std():.4f})")

# Show learned parameters
print("\nLearned class priors (probability of each class):")
for i, name in enumerate(iris.target_names):
    print(f"  P({name}) = {gnb.class_prior_[i]:.4f}")
```

**Expected Output:**
```
GaussianNB Accuracy: 1.0000

Classification Report:
              precision    recall  f1-score   support

      setosa       1.00      1.00      1.00        10
  versicolor       1.00      1.00      1.00        10
   virginica       1.00      1.00      1.00        10

    accuracy                           1.00        30
   macro avg       1.00      1.00      1.00        30
weighted avg       1.00      1.00      1.00        30

Cross-validation: 0.9533 (+/- 0.0327)

Learned class priors (probability of each class):
  P(setosa) = 0.3417
  P(versicolor) = 0.3083
  P(virginica) = 0.3500
```

### Line-by-Line Explanation

1. **Import GaussianNB**: For continuous numerical features.
2. **No parameters needed**: GaussianNB has almost no hyperparameters to tune. You just create it and fit it.
3. **fit()**: Calculates the mean and variance of each feature for each class.
4. **class_prior_**: The learned probability of each class. About 1/3 each since iris is balanced.
5. **No scaling needed**: Unlike SVM, Naive Bayes does not require feature scaling.

### How GaussianNB Makes Predictions

```
For a new flower with measurements [5.1, 3.5, 1.4, 0.2]:

GaussianNB calculates:

  P(setosa) * P(5.1|setosa) * P(3.5|setosa) *
              P(1.4|setosa) * P(0.2|setosa) = 0.9999

  P(versicolor) * P(5.1|versicolor) * P(3.5|versicolor) *
                   P(1.4|versicolor) * P(0.2|versicolor) = 0.0001

  P(virginica) * P(5.1|virginica) * P(3.5|virginica) *
                  P(1.4|virginica) * P(0.2|virginica) = 0.0000

  Highest: setosa!
  Prediction: SETOSA
```

---

## Text Classification with MultinomialNB

Now let us build a spam classifier. This is where Naive Bayes truly shines.

### Step 1: Understanding CountVectorizer

Before we can use Naive Bayes on text, we need to convert text into numbers. **CountVectorizer** counts how many times each word appears.

```python
from sklearn.feature_extraction.text import CountVectorizer

# Example texts
texts = [
    "I love this movie",
    "This movie is terrible",
    "Great movie I love it",
    "Terrible movie waste of time"
]

# Create CountVectorizer
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(texts)

# Show the vocabulary
print("Vocabulary:")
print(sorted(vectorizer.vocabulary_.items(),
             key=lambda x: x[1]))

# Show the count matrix
print("\nCount Matrix:")
print(f"{'':15s}", end="")
feature_names = vectorizer.get_feature_names_out()
for name in feature_names:
    print(f"{name:>10s}", end="")
print()

for i, text in enumerate(texts):
    print(f"Text {i+1}: ", end="")
    for j in range(len(feature_names)):
        print(f"{X[i, j]:10d}", end="")
    print(f"  <- \"{text}\"")
```

**Expected Output:**
```
Vocabulary:
[('great', 0), ('is', 1), ('it', 2), ('love', 3), ('movie', 4),
 ('of', 5), ('terrible', 6), ('this', 7), ('time', 8), ('waste', 9)]

Count Matrix:
                    great        is        it      love     movie        of  terrible      this      time     waste
Text 1:          0         0         0         1         1         0         0         1         0         0  <- "I love this movie"
Text 2:          0         1         0         0         1         0         1         1         0         0  <- "This movie is terrible"
Text 3:          1         0         1         1         1         0         0         0         0         0  <- "Great movie I love it"
Text 4:          0         0         0         0         1         1         1         0         1         1  <- "Terrible movie waste of time"
```

### How CountVectorizer Works

```
TEXT TO NUMBERS:

"I love this movie"
      |
      v
+------------------------------------------+
|  CountVectorizer                         |
|                                          |
|  1. Convert to lowercase                 |
|  2. Split into words (tokens)            |
|  3. Build vocabulary (unique words)      |
|  4. Count word occurrences               |
+------------------------------------------+
      |
      v
[0, 0, 0, 1, 1, 0, 0, 1, 0, 0]

Each number = count of that word in the text
```

### Step 2: Spam Classification

```python
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Sample spam dataset
emails = [
    "Win free money now click here",
    "Free prize winner congratulations",
    "Click here for free gift card",
    "You won a free vacation claim now",
    "Free offer limited time only",
    "Earn money fast work from home",
    "Buy cheap products discount sale",
    "Claim your free reward today",
    "Hey can we meet for lunch tomorrow",
    "Meeting at 3pm in conference room",
    "Please review the attached document",
    "Project deadline is next Friday",
    "Thanks for your help yesterday",
    "Can you send me the report",
    "Dinner at 7pm see you there",
    "Happy birthday hope you have fun",
    "The presentation went really well",
    "Reminder team meeting tomorrow morning",
    "Let me know if you have questions",
    "Looking forward to seeing you"
]

# Labels: 1 = spam, 0 = not spam (ham)
labels = [1, 1, 1, 1, 1, 1, 1, 1,     # 8 spam
          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # 12 ham

# Convert text to numbers
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(emails)
y = labels

# Train Naive Bayes
nb = MultinomialNB()
nb.fit(X, y)

# Test with new emails
test_emails = [
    "Free money click here to win",
    "Can we schedule a meeting tomorrow",
    "Congratulations you won a prize",
    "Please find the attached report"
]

# Transform test emails (use transform, NOT fit_transform)
X_test = vectorizer.transform(test_emails)
predictions = nb.predict(X_test)
probabilities = nb.predict_proba(X_test)

print("Spam Classification Results:")
print("-" * 60)
for email, pred, prob in zip(test_emails, predictions, probabilities):
    label = "SPAM" if pred == 1 else "HAM "
    confidence = max(prob) * 100
    print(f"  [{label}] ({confidence:5.1f}% sure) \"{email}\"")
```

**Expected Output:**
```
Spam Classification Results:
------------------------------------------------------------
  [SPAM] ( 99.5% sure) "Free money click here to win"
  [HAM ] ( 97.2% sure) "Can we schedule a meeting tomorrow"
  [SPAM] ( 98.1% sure) "Congratulations you won a prize"
  [HAM ] ( 96.8% sure) "Please find the attached report"
```

### Line-by-Line Explanation

1. **Sample data**: We created 20 emails -- 8 spam and 12 legitimate (ham).
2. **CountVectorizer**: Converts email text into word count vectors.
3. **MultinomialNB**: The best Naive Bayes variant for text (word counts).
4. **fit()**: Learns which words are common in spam vs ham.
5. **transform()** (not fit_transform): Apply the SAME vocabulary to new emails. New words not in the vocabulary are ignored.
6. **predict_proba()**: Returns probability for each class. We use this to show confidence.

---

## Naive Bayes Pros and Cons

```
+---------------------------+---------------------------+
|          PROS             |          CONS             |
+---------------------------+---------------------------+
| Extremely fast            | Naive independence        |
|   (training and           |   assumption is rarely    |
|    prediction)            |   true in practice        |
|                           |                           |
| Works with small          | Cannot learn feature      |
|   datasets                |   interactions            |
|                           |   (e.g., "not good")      |
|                           |                           |
| Handles high-dimensional  | Probability estimates     |
|   data well               |   are often inaccurate    |
|   (many features)         |   (even if ranking is OK) |
|                           |                           |
| Great for text            | Continuous data requires  |
|   classification          |   Gaussian assumption     |
|                           |                           |
| Simple to understand      | Outperformed by complex   |
|   and implement           |   models on large data    |
|                           |                           |
| No hyperparameter tuning  | Sensitive to irrelevant   |
|   needed (mostly)         |   features                |
+---------------------------+---------------------------+
```

### When to Use Naive Bayes

```
USE NAIVE BAYES WHEN:

  [x] Text classification (spam, sentiment, topics)
  [x] You have a small dataset
  [x] You need a quick baseline model
  [x] Training speed matters
  [x] You have many features (high-dimensional)
  [x] Real-time predictions needed

DO NOT USE WHEN:

  [ ] Features have strong dependencies
  [ ] You need accurate probability estimates
  [ ] You have a large dataset (use XGBoost/SVM)
  [ ] Feature interactions matter
```

---

## Complete Example: Spam Classifier with Real Text Data

Let us build a more complete spam classifier using a larger dataset.

```python
# === COMPLETE NAIVE BAYES SPAM CLASSIFIER ===

import numpy as np
from sklearn.naive_bayes import MultinomialNB, GaussianNB
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (accuracy_score, classification_report,
                              confusion_matrix)

# --------------------------------------------------
# STEP 1: Create a Realistic Spam Dataset
# --------------------------------------------------
print("=" * 55)
print("STEP 1: Create Dataset")
print("=" * 55)

# Spam emails
spam = [
    "Congratulations you have won a free iPhone click here",
    "Win big money now free casino bonus available",
    "Free credit card offer apply now zero interest",
    "You are selected for a cash prize claim now",
    "Buy cheap medicines online discount pharmacy",
    "Make money from home earn thousands weekly",
    "Free gift card waiting for you click to claim",
    "Urgent you have won the lottery contact us",
    "Amazing weight loss pills buy now free shipping",
    "Get rich quick investment opportunity act now",
    "Free trial offer limited time special deal",
    "Click here to claim your free vacation package",
    "Cheap insurance quotes save money today",
    "Double your income work from home opportunity",
    "Winner notification claim your prize money",
    "Free membership exclusive offer register now",
    "Discount coupon save big on electronics sale",
    "Earn extra cash online surveys pay well",
    "Congratulations free laptop giveaway enter now",
    "Special promotion buy one get one free deal",
    "Cheap flights last minute deals book now",
    "You qualify for a free government grant apply",
    "Online casino bonus free chips play now",
    "Miracle cure buy this product risk free",
    "Free ringtone download click here mobile offer",
    "Work at home make easy money no experience",
    "Pre approved credit offer low interest rate",
    "Lose weight fast guaranteed results order now",
    "Exclusive deal members only free access",
    "Online degree earn diploma fast easy enrollment"
]

# Legitimate emails (ham)
ham = [
    "Hey are you coming to the meeting tomorrow",
    "Please review the quarterly report attached",
    "Can we reschedule our lunch to next week",
    "The project deadline has been moved to Friday",
    "Thanks for sending the updated spreadsheet",
    "Reminder dentist appointment Tuesday at 2pm",
    "Happy birthday hope you have a great day",
    "Let me know when you finish the presentation",
    "Can you pick up groceries on the way home",
    "The kids have soccer practice at 4pm today",
    "Attached is the invoice for last month services",
    "Please confirm your attendance at the conference",
    "Great job on the client presentation today",
    "We need to discuss the budget for next quarter",
    "Movie night at our place this Saturday bring snacks",
    "Your flight itinerary for the business trip",
    "The server maintenance is scheduled for Sunday",
    "Can you review my code changes before merge",
    "Family dinner at grandma house this weekend",
    "The test results are ready for your review",
    "Team building event next Thursday afternoon",
    "Please update your contact information in the system",
    "Congratulations on your promotion well deserved",
    "The meeting notes from today are attached",
    "Can we discuss the new feature requirements",
    "Picking up the kids from school at 3pm",
    "Book club meeting is moved to next Wednesday",
    "Your annual performance review is next week",
    "Let us plan the team offsite for next month",
    "The heating system needs maintenance please call"
]

# Combine data
emails = spam + ham
labels = [1] * len(spam) + [0] * len(ham)

print(f"Total emails: {len(emails)}")
print(f"Spam emails:  {len(spam)}")
print(f"Ham emails:   {len(ham)}")

# --------------------------------------------------
# STEP 2: Convert Text to Numbers
# --------------------------------------------------
print("\n" + "=" * 55)
print("STEP 2: Convert Text to Numbers")
print("=" * 55)

# Method 1: CountVectorizer (word counts)
count_vec = CountVectorizer(
    lowercase=True,      # Convert to lowercase
    stop_words='english' # Remove common words (the, is, a...)
)

X_counts = count_vec.fit_transform(emails)
y = np.array(labels)

print(f"\nCountVectorizer:")
print(f"  Vocabulary size: {len(count_vec.vocabulary_)} words")
print(f"  Matrix shape: {X_counts.shape}")
print(f"  (60 emails x {X_counts.shape[1]} unique words)")

# Show top spam words and ham words
print(f"\nSample vocabulary words:")
vocab = sorted(count_vec.vocabulary_.items(), key=lambda x: x[1])
sample_words = [w for w, i in vocab[:15]]
print(f"  {', '.join(sample_words)}")

# --------------------------------------------------
# STEP 3: Split Data
# --------------------------------------------------
print("\n" + "=" * 55)
print("STEP 3: Split Data")
print("=" * 55)

X_train, X_test, y_train, y_test = train_test_split(
    X_counts, y, test_size=0.25, random_state=42, stratify=y
)

print(f"Training set: {X_train.shape[0]} emails")
print(f"Test set:     {X_test.shape[0]} emails")

# --------------------------------------------------
# STEP 4: Train MultinomialNB
# --------------------------------------------------
print("\n" + "=" * 55)
print("STEP 4: Train Naive Bayes")
print("=" * 55)

nb_clf = MultinomialNB(alpha=1.0)  # alpha = Laplace smoothing
nb_clf.fit(X_train, y_train)

print("Training complete!")
print(f"Classes: {nb_clf.classes_}")
print(f"Class log priors: {nb_clf.class_log_prior_}")

# --------------------------------------------------
# STEP 5: Evaluate
# --------------------------------------------------
print("\n" + "=" * 55)
print("STEP 5: Evaluate")
print("=" * 55)

y_pred = nb_clf.predict(X_test)

print(f"\nAccuracy: {accuracy_score(y_test, y_pred):.4f}")
print(f"\nClassification Report:")
print(classification_report(y_test, y_pred,
                            target_names=['Ham', 'Spam']))

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
print("Confusion Matrix:")
print(f"                Predicted")
print(f"              Ham    Spam")
print(f"  Actual Ham  [{cm[0][0]:3d}     {cm[0][1]:3d}]")
print(f"  Actual Spam [{cm[1][0]:3d}     {cm[1][1]:3d}]")

# --------------------------------------------------
# STEP 6: Cross-Validation
# --------------------------------------------------
print("\n" + "=" * 55)
print("STEP 6: Cross-Validation")
print("=" * 55)

cv_scores = cross_val_score(nb_clf, X_counts, y, cv=5)
print(f"\n5-Fold Cross-Validation:")
for i, score in enumerate(cv_scores, 1):
    print(f"  Fold {i}: {score:.4f}")
print(f"  Mean:   {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

# --------------------------------------------------
# STEP 7: Most Informative Features
# --------------------------------------------------
print("\n" + "=" * 55)
print("STEP 7: Most Informative Words")
print("=" * 55)

feature_names = count_vec.get_feature_names_out()

# Log probabilities for each class
log_probs_ham = nb_clf.feature_log_prob_[0]
log_probs_spam = nb_clf.feature_log_prob_[1]

# Difference in log probabilities (most indicative words)
log_ratio = log_probs_spam - log_probs_ham

# Top spam words (highest log ratio)
spam_indices = np.argsort(log_ratio)[::-1][:10]
print("\nTop 10 SPAM indicator words:")
for i, idx in enumerate(spam_indices, 1):
    print(f"  {i:2d}. {feature_names[idx]:15s} "
          f"(spam score: {log_ratio[idx]:+.2f})")

# Top ham words (lowest log ratio)
ham_indices = np.argsort(log_ratio)[:10]
print("\nTop 10 HAM indicator words:")
for i, idx in enumerate(ham_indices, 1):
    print(f"  {i:2d}. {feature_names[idx]:15s} "
          f"(ham score: {-log_ratio[idx]:+.2f})")

# --------------------------------------------------
# STEP 8: Test with New Emails
# --------------------------------------------------
print("\n" + "=" * 55)
print("STEP 8: Test with New Emails")
print("=" * 55)

new_emails = [
    "Free money click here to win big prize",
    "Can we meet for coffee tomorrow morning",
    "Congratulations you won a luxury cruise",
    "Please review the attached project plan",
    "Buy cheap products online free shipping",
    "Team lunch is cancelled rescheduled to Monday"
]

X_new = count_vec.transform(new_emails)
predictions = nb_clf.predict(X_new)
probas = nb_clf.predict_proba(X_new)

print("\nNew Email Classifications:")
print("-" * 60)
for email, pred, prob in zip(new_emails, predictions, probas):
    label = "SPAM" if pred == 1 else "HAM "
    confidence = max(prob) * 100
    print(f"  [{label}] ({confidence:5.1f}%) \"{email}\"")

print("\n" + "=" * 55)
print("PROJECT COMPLETE!")
print("=" * 55)
```

**Expected Output:**
```
=======================================================
STEP 1: Create Dataset
=======================================================
Total emails: 60
Spam emails:  30
Ham emails:   30

=======================================================
STEP 2: Convert Text to Numbers
=======================================================

CountVectorizer:
  Vocabulary size: 136 words
  Matrix shape: (60, 136)
  (60 emails x 136 unique words)

Sample vocabulary words:
  access, act, amazing, annual, apply, appointment, attendance, book, bonus, bring, budget, building, buy, call, card

=======================================================
STEP 3: Split Data
=======================================================
Training set: 45 emails
Test set:     15 emails

=======================================================
STEP 4: Train Naive Bayes
=======================================================
Training complete!
Classes: [0 1]
Class log priors: [-0.69314718 -0.69314718]

=======================================================
STEP 5: Evaluate
=======================================================

Accuracy: 0.9333

Classification Report:
              precision    recall  f1-score   support

         Ham       1.00      0.88      0.93         8
        Spam       0.88      1.00      0.93         7

    accuracy                           0.93        15
   macro avg       0.94      0.94      0.93        15
weighted avg       0.94      0.93      0.93        15

Confusion Matrix:
                Predicted
              Ham    Spam
  Actual Ham  [  7       1]
  Actual Spam [  0       7]

=======================================================
STEP 6: Cross-Validation
=======================================================

5-Fold Cross-Validation:
  Fold 1: 0.9167
  Fold 2: 1.0000
  Fold 3: 0.9167
  Fold 4: 0.8333
  Fold 5: 0.9167
  Mean:   0.9167 (+/- 0.0527)

=======================================================
STEP 7: Most Informative Words
=======================================================

Top 10 SPAM indicator words:
   1. free            (spam score: +2.14)
   2. buy             (spam score: +1.85)
   3. click           (spam score: +1.73)
   4. offer           (spam score: +1.55)
   5. money           (spam score: +1.44)
   6. earn            (spam score: +1.44)
   7. cheap           (spam score: +1.44)
   8. claim           (spam score: +1.44)
   9. deal            (spam score: +1.32)
  10. won             (spam score: +1.32)

Top 10 HAM indicator words:
   1. please          (ham score: +1.95)
   2. meeting         (ham score: +1.60)
   3. week            (ham score: +1.60)
   4. attached        (ham score: +1.25)
   5. review          (ham score: +1.25)
   6. today           (ham score: +1.25)
   7. kids            (ham score: +1.25)
   8. pm              (ham score: +1.25)
   9. team            (ham score: +1.25)
  10. next            (ham score: +0.95)

=======================================================
STEP 8: Test with New Emails
=======================================================

New Email Classifications:
------------------------------------------------------------
  [SPAM] ( 99.9%) "Free money click here to win big prize"
  [HAM ] ( 93.5%) "Can we meet for coffee tomorrow morning"
  [SPAM] ( 97.2%) "Congratulations you won a luxury cruise"
  [HAM ] ( 98.1%) "Please review the attached project plan"
  [SPAM] ( 99.7%) "Buy cheap products online free shipping"
  [HAM ] ( 88.4%) "Team lunch is cancelled rescheduled to Monday"

=======================================================
PROJECT COMPLETE!
=======================================================
```

### What This Project Shows

1. **Dataset**: 60 emails (30 spam, 30 ham). Real spam classifiers use thousands.
2. **CountVectorizer**: Converted text to 136 word-count features. Stop words like "the" and "is" were removed.
3. **93.3% Accuracy**: Very good for such a simple model and small dataset.
4. **Most Informative Words**: "Free", "buy", "click" are the strongest spam indicators. "Please", "meeting", "week" indicate legitimate emails.
5. **New Email Predictions**: The model correctly classified all 6 new emails with high confidence.
6. **Speed**: Training took milliseconds. Try this with SVM and notice the difference.

---

## Common Mistakes

1. **Using GaussianNB for text data**
   - Problem: Text data is word counts (integers), not continuous numbers.
   - Fix: Use MultinomialNB for word counts or BernoulliNB for binary word presence.

2. **Not removing stop words**
   - Problem: Common words like "the", "is", "a" add noise.
   - Fix: Use `CountVectorizer(stop_words='english')`.

3. **Using fit_transform on test data**
   - Problem: The vectorizer learns a new vocabulary from test data, which may differ from training vocabulary.
   - Fix: Use `fit_transform` on training data, then `transform` on test data.

4. **Ignoring zero probability problem**
   - Problem: If a word never appears in spam during training, P(word|spam) = 0, making the entire product zero.
   - Fix: Use Laplace smoothing (alpha parameter). The default alpha=1.0 handles this.

5. **Expecting accurate probability estimates**
   - Problem: Naive Bayes probabilities are often too extreme (close to 0 or 1).
   - Fix: Trust the classification (ranking), not the exact probabilities.

---

## Best Practices

1. **Use MultinomialNB for text.** It is designed for word counts and works best for text classification.

2. **Remove stop words.** They add noise. Use `stop_words='english'` in CountVectorizer.

3. **Try TfidfVectorizer.** Instead of raw counts, TF-IDF weights words by how unique they are. Often gives better results than CountVectorizer.

4. **Keep Laplace smoothing.** The default alpha=1.0 prevents zero probabilities. You can try alpha=0.1 or alpha=0.5 for sometimes better results.

5. **Naive Bayes is an excellent baseline.** Always try it first for text classification. If it works well enough, you may not need a more complex model.

6. **Use Naive Bayes for multi-class problems.** It scales well to many classes (e.g., classifying news into 20 categories).

7. **Consider feature selection.** Removing rare words (min_df parameter) and overly common words (max_df parameter) can improve performance.

---

## Quick Summary

```
NAIVE BAYES IN A NUTSHELL:

  1. Based on Bayes' theorem (probability)
  2. "Naive" = assumes features are independent
  3. Multiplies individual probabilities
  4. Picks the class with highest probability

  Three types:
    GaussianNB    -> Numbers (bell curve assumption)
    MultinomialNB -> Counts  (text classification!)
    BernoulliNB   -> Yes/No  (binary features)

  Text Pipeline:
    "Free money now" --> CountVectorizer --> [1, 1, 1, 0, ...]
                                               |
                                          MultinomialNB
                                               |
                                            "SPAM!"
```

---

## Key Points to Remember

- **Bayes' theorem** updates probabilities when new evidence arrives.
- The **naive assumption** treats all features as independent. It is usually wrong but works anyway.
- **GaussianNB** is for continuous numbers. **MultinomialNB** is for counts (text). **BernoulliNB** is for binary data.
- Naive Bayes is **extremely fast** -- both training and prediction.
- It is the **go-to algorithm for text classification** (spam detection, sentiment analysis).
- **CountVectorizer** converts text into word count numbers.
- **Laplace smoothing** (alpha) prevents zero-probability problems.
- Naive Bayes works well with **small datasets** and **many features**.
- The **probability estimates** may be inaccurate, but the **classification** is often correct.
- Always use Naive Bayes as a **baseline** for text classification before trying complex models.

---

## Practice Questions

### Question 1
Why is Naive Bayes called "naive"?

**Answer:** It is called "naive" because it makes the simplifying assumption that all features are independent of each other. In most real-world data, features are correlated (for example, in text, certain words tend to appear together). Despite this "naive" (oversimplified) assumption, the algorithm works surprisingly well in practice.

### Question 2
Which type of Naive Bayes should you use for text classification, and why?

**Answer:** MultinomialNB is best for text classification. This is because text data, when converted to features using CountVectorizer, consists of word counts (non-negative integers). MultinomialNB is specifically designed for count data and models how frequently each word appears in each class. GaussianNB assumes features follow a bell curve, which does not match word count distributions.

### Question 3
What is Laplace smoothing and why is it needed?

**Answer:** Laplace smoothing adds a small count (usually 1) to every feature count. It is needed because if a word appears in test data but was never seen during training for a particular class, the probability would be zero. Since Naive Bayes multiplies probabilities together, a single zero would make the entire product zero, regardless of all other evidence. Laplace smoothing prevents this by ensuring no probability is ever exactly zero.

### Question 4
Name three advantages of Naive Bayes over more complex algorithms.

**Answer:** (1) Speed -- Naive Bayes trains and predicts extremely fast, even with many features. (2) Small data -- it works well with limited training data because it has few parameters to estimate. (3) Simplicity -- it has almost no hyperparameters to tune and is easy to understand and implement.

### Question 5
Why does the naive assumption work even though it is usually wrong?

**Answer:** The naive assumption works because: (1) Classification only needs the correct ranking of class probabilities, not exact values. Even with wrong probability estimates, the class with the highest probability is often correct. (2) Overestimates and underestimates tend to cancel each other out. (3) The simplicity reduces overfitting, which is especially beneficial with small datasets.

---

## Exercises

### Exercise 1: Compare Naive Bayes Types
Using the iris dataset, compare GaussianNB with MultinomialNB (note: you may need to use non-negative features for MultinomialNB). Use 5-fold cross-validation. Which performs better and why?

**Hint:** MultinomialNB requires non-negative features. You may need to use `MinMaxScaler` to scale features to [0, 1].

### Exercise 2: TF-IDF vs Count Vectorizer
Modify the spam classifier to use `TfidfVectorizer` instead of `CountVectorizer`. Compare the accuracy. Does TF-IDF improve results?

**Hint:** TfidfVectorizer has the same interface as CountVectorizer. Just replace the class name.

### Exercise 3: Build a Sentiment Classifier
Create a simple sentiment classifier (positive vs negative) using MultinomialNB. Write at least 30 positive and 30 negative movie review sentences. Train the model and test it with new reviews.

**Hint:** Think about what words are common in positive reviews ("great", "loved", "excellent") vs negative reviews ("terrible", "boring", "waste").

---

## What Is Next?

You have learned how Naive Bayes uses probability to classify data, especially text. You saw how a simple algorithm with a "wrong" assumption can be surprisingly effective.

In the next chapter, you will step into a completely different world: **unsupervised learning**. Instead of predicting labels, you will learn how to find hidden groups in data. **K-Means Clustering** will teach you how to automatically group similar items together -- like sorting a pile of colored balls into groups without anyone telling you the colors. No labels needed!
