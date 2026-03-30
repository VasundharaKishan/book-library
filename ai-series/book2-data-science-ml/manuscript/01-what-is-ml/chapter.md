# Chapter 1: What Is Machine Learning?

## What You Will Learn

In this chapter, you will learn:

- What machine learning actually means in plain English
- How machine learning differs from regular programming
- The three main types of machine learning
- Real-world examples you already use every day
- The basic workflow every ML project follows
- The difference between classification and regression
- When to use machine learning and when not to

## Why This Chapter Matters

Machine learning is everywhere. Your email filters spam. Netflix suggests movies. Your phone understands your voice. Banks detect fraud on your credit card. Doctors use it to spot diseases in X-rays.

But what IS machine learning? Most explanations use jargon that confuses beginners. This chapter explains it in simple English. No math. No complex theory. Just clear ideas with real examples.

Understanding what ML is (and what it is not) saves you from two common mistakes. First, trying to use ML when a simple `if/else` statement would work. Second, not using ML when it would save you months of work.

By the end of this chapter, you will have a clear mental picture of machine learning. You will know the vocabulary. You will understand the process. And you will be ready to start building.

---

## What Is Machine Learning? The Simple Explanation

Imagine you are teaching a child to recognize dogs.

You do not sit down and write a rule book:
- "A dog has four legs, fur, a tail, and barks."

Why not? Because some dogs have three legs. Some do not bark. Some have very short tails. Writing rules for every possible dog is impossible.

Instead, you show the child hundreds of pictures. Some are dogs. Some are not. The child starts to notice patterns. After enough examples, the child can recognize a dog it has never seen before.

**That is machine learning.**

Machine learning is teaching a computer to learn from examples instead of giving it explicit rules.

Here is the key definition:

> **Machine Learning (ML):** A way to teach computers to make decisions or predictions by showing them many examples, instead of programming every rule by hand.

Let me say that again in an even simpler way:

- **Traditional programming:** You write the rules. The computer follows them.
- **Machine learning:** You give examples. The computer figures out the rules.

### The Key Difference: Rules vs. Learning

```
+-----------------------------------------------+
|         TRADITIONAL PROGRAMMING                |
|                                                 |
|   Rules  +  Data  ------>  Answers              |
|                                                 |
|   You write the rules.                          |
|   The computer applies them to data.            |
|   The computer gives you answers.               |
+-----------------------------------------------+

+-----------------------------------------------+
|         MACHINE LEARNING                        |
|                                                 |
|   Data  +  Answers  ------>  Rules              |
|                                                 |
|   You give examples (data + correct answers).   |
|   The computer figures out the rules.           |
|   The computer can now answer new questions.     |
+-----------------------------------------------+
```

### A Concrete Example: Spam Detection

**Traditional approach:**

You sit down and write rules:
```
if email contains "free money" -> spam
if email contains "you won" -> spam
if email contains "click here now" -> spam
... (hundreds more rules)
```

This is exhausting. Spammers change their words. Your rules break. You spend forever updating them.

**Machine learning approach:**

You collect 10,000 emails. You label each one as "spam" or "not spam." You feed them to an ML algorithm (algorithm = a set of steps, like a recipe). The algorithm learns the patterns. Now it can classify new emails it has never seen.

The ML approach is better because:
1. You do not need to figure out the rules yourself
2. The system can adapt when spammers change tactics
3. It catches patterns you might never think of

---

## Three Types of Machine Learning

There are three main types of machine learning. Think of them as three different ways to teach.

### Type 1: Supervised Learning (Learning with a Teacher)

**Analogy:** A student studies with a teacher. The teacher shows problems AND the correct answers. The student learns the pattern. Then the student can solve new problems alone.

**How it works:**
1. You give the computer labeled data (data with correct answers)
2. The computer finds patterns between input and output
3. The computer predicts answers for new, unseen data

```
+-------------------------------------------------+
|           SUPERVISED LEARNING                    |
|                                                  |
|   Training Data (with labels):                   |
|                                                  |
|   Input              |  Label (Answer)           |
|   -------------------|------------------------   |
|   Sunny, 85F         |  "Go to beach"            |
|   Rainy, 55F         |  "Stay home"              |
|   Cloudy, 70F        |  "Go for walk"             |
|   Snowy, 25F         |  "Stay home"              |
|                                                  |
|   New Input: Sunny, 78F  --->  Prediction: ?     |
|   The model predicts: "Go to beach"              |
+-------------------------------------------------+
```

**Real-world examples:**
- **Email spam filter:** Learns from emails labeled "spam" or "not spam"
- **House price prediction:** Learns from houses with known prices
- **Medical diagnosis:** Learns from X-rays labeled "healthy" or "disease"
- **Credit card fraud:** Learns from transactions labeled "fraud" or "legitimate"

Supervised learning is the most common type. About 80% of real-world ML uses supervised learning.

### Type 2: Unsupervised Learning (Learning without a Teacher)

**Analogy:** You give a child a box of mixed Lego bricks. No instructions. The child groups them by color, size, or shape on their own. Nobody told the child how to group them.

**How it works:**
1. You give the computer data WITHOUT labels (no correct answers)
2. The computer finds hidden patterns or groups on its own
3. You interpret what the computer found

```
+-------------------------------------------------+
|           UNSUPERVISED LEARNING                  |
|                                                  |
|   Data (no labels):                              |
|                                                  |
|   Customer A: age 22, spends $50/month           |
|   Customer B: age 45, spends $500/month          |
|   Customer C: age 23, spends $45/month           |
|   Customer D: age 47, spends $480/month          |
|                                                  |
|   The model finds groups:                        |
|   Group 1: A, C (young, low spenders)            |
|   Group 2: B, D (older, high spenders)           |
+-------------------------------------------------+
```

**Real-world examples:**
- **Customer segmentation:** Group customers by buying behavior
- **Netflix categories:** Group movies by viewing patterns
- **Anomaly detection:** Find unusual credit card transactions
- **News grouping:** Group similar news articles together

### Type 3: Reinforcement Learning (Learning by Trial and Error)

**Analogy:** Teaching a dog a trick. The dog tries something. If it works, it gets a treat (reward). If not, no treat (penalty). Over time, the dog learns what to do.

**How it works:**
1. An agent (the learner) interacts with an environment
2. It takes actions and receives rewards or penalties
3. It learns which actions give the best rewards over time

```
+-------------------------------------------------+
|           REINFORCEMENT LEARNING                 |
|                                                  |
|   +-------+         +-------------+              |
|   | Agent | ------> | Environment |              |
|   |       | Action  |             |              |
|   |       | <------ |             |              |
|   |       | Reward  |             |              |
|   +-------+  or     +-------------+              |
|              Penalty                             |
|                                                  |
|   The agent learns to maximize rewards           |
|   through trial and error.                       |
+-------------------------------------------------+
```

**Real-world examples:**
- **Self-driving cars:** Learn to navigate roads safely
- **Game AI:** AlphaGo learned to beat the world champion at Go
- **Robots:** Learn to walk, pick up objects, or navigate mazes
- **Ad placement:** Learn which ads get the most clicks

### Quick Comparison

```
+-------------------+------------------+--------------------+
| Type              | Has Labels?      | Example            |
+-------------------+------------------+--------------------+
| Supervised        | Yes              | Predict house      |
|                   | (answers given)  | prices             |
+-------------------+------------------+--------------------+
| Unsupervised      | No               | Group customers    |
|                   | (find patterns)  | by behavior        |
+-------------------+------------------+--------------------+
| Reinforcement     | No               | Teach a robot      |
|                   | (rewards given)  | to walk            |
+-------------------+------------------+--------------------+
```

---

## Real-World ML Examples You Use Every Day

You already interact with machine learning many times a day. Here are examples:

### 1. Spam Filter (Supervised Learning)
Every time Gmail moves a junk email to your spam folder, that is ML. It learned from billions of emails labeled "spam" or "not spam."

### 2. Netflix Recommendations (Unsupervised + Supervised)
"Because you watched..." suggestions use ML. Netflix groups similar users and similar movies. Then it predicts what you will enjoy next.

### 3. Voice Assistants (Supervised Learning)
Siri, Alexa, and Google Assistant use ML to understand your voice. They learned from millions of voice recordings matched to text.

### 4. Self-Driving Cars (Reinforcement Learning)
Self-driving cars use ML to recognize stop signs, pedestrians, and other cars. They learn from millions of miles of driving data.

### 5. Social Media Feeds (Supervised Learning)
Instagram, TikTok, and Twitter use ML to decide which posts to show you. They predict what you will like, comment on, or share.

### 6. Online Shopping (Supervised + Unsupervised)
"Customers who bought this also bought..." is ML. Amazon predicts what you might want based on your browsing and purchase history.

### 7. Banking Fraud Detection (Supervised Learning)
Your bank uses ML to spot unusual transactions. If someone steals your card and buys something in a different country, ML catches it.

### 8. Healthcare (Supervised Learning)
ML helps doctors read X-rays, MRIs, and CT scans. It can spot tumors, fractures, and diseases, sometimes more accurately than humans.

---

## The ML Workflow: From Data to Predictions

Every ML project follows the same basic steps. Here is the workflow:

```
+------------------------------------------------------------------+
|                    THE ML WORKFLOW                                 |
|                                                                   |
|  Step 1        Step 2       Step 3       Step 4       Step 5      |
|                                                                   |
| +--------+   +--------+   +--------+   +--------+   +--------+   |
| |Collect |-->| Clean  |-->| Train  |-->|  Test  |-->|  Use   |   |
| | Data   |   |  Data  |   | Model  |   | Model  |   | Model  |   |
| +--------+   +--------+   +--------+   +--------+   +--------+   |
|                                                                   |
| Get data      Fix errors   Feed data    Check if    Make          |
| from files,   remove       to an        model is    predictions   |
| databases,    missing      algorithm    accurate    on new data   |
| or APIs       values                                              |
+------------------------------------------------------------------+
```

Let me explain each step:

**Step 1: Collect Data**
Gather the data you need. This could be a CSV file, a database, or an API. More data usually means a better model.

**Step 2: Clean Data**
Real data is messy. It has missing values, typos, and errors. You fix these problems before training. (We cover this in Chapter 4.)

**Step 3: Train the Model**
Feed your clean data to an ML algorithm. The algorithm learns patterns from the data. The result is a trained model.

**Step 4: Test the Model**
Check how well your model works on data it has never seen. If it performs poorly, go back and improve it.

**Step 5: Use the Model**
Deploy your model to make predictions on new, real-world data.

### A Simple Example in Python

Let us see the ML workflow in action. We will teach a computer to predict if a fruit is an apple or an orange based on its weight and texture.

```python
# Step 1: Collect Data
# We have measurements of fruits
# Weight (grams) and Texture (0=smooth, 1=bumpy)
# Label: 0=apple, 1=orange

from sklearn.tree import DecisionTreeClassifier

# Step 1: Our training data
# [weight, texture]
features = [
    [140, 1],  # 140g, bumpy -> orange
    [130, 1],  # 130g, bumpy -> orange
    [150, 0],  # 150g, smooth -> apple
    [170, 0],  # 170g, smooth -> apple
]

# The correct answers (labels)
labels = [1, 1, 0, 0]  # 1=orange, 0=apple

# Step 3: Train the model
model = DecisionTreeClassifier()
model.fit(features, labels)

# Step 5: Use the model to predict
# What is a 160g smooth fruit?
new_fruit = [[160, 0]]
prediction = model.predict(new_fruit)

if prediction[0] == 0:
    print("It is an apple!")
else:
    print("It is an orange!")
```

**Expected Output:**
```
It is an apple!
```

**Line-by-line explanation:**

- `from sklearn.tree import DecisionTreeClassifier` - We import a tool (algorithm) called DecisionTreeClassifier from scikit-learn. A decision tree makes decisions by asking yes/no questions, like a flowchart.
- `features = [[140, 1], [130, 1], [150, 0], [170, 0]]` - Our input data. Each fruit has a weight and texture. This is what the model learns FROM.
- `labels = [1, 1, 0, 0]` - The correct answers. The first two fruits are oranges (1). The last two are apples (0). This is what the model learns TO PREDICT.
- `model = DecisionTreeClassifier()` - Create a new, untrained model. It knows nothing yet.
- `model.fit(features, labels)` - Train the model. The `fit` method means "learn from this data." After this line, the model has learned patterns.
- `new_fruit = [[160, 0]]` - A new fruit we want to classify. It weighs 160g and is smooth.
- `prediction = model.predict(new_fruit)` - Ask the model: "What is this fruit?" The model returns its best guess.
- The `if/else` block prints the result in human-readable form.

---

## Classification vs. Regression

In supervised learning, there are two main types of problems:

### Classification: Predicting a Category

Classification means predicting which group something belongs to. The answer is a label or category.

**Examples:**
- Is this email spam or not spam? (two categories)
- Is this tumor malignant or benign? (two categories)
- What digit is in this image? (ten categories: 0-9)
- What breed is this dog? (many categories)

```
+-----------------------------------------------+
|           CLASSIFICATION                        |
|                                                 |
|   Input ---------> Model ---------> Category    |
|                                                 |
|   Email text       Spam filter      "Spam"      |
|   X-ray image      Medical AI       "Healthy"   |
|   Photo            Dog classifier   "Labrador"  |
+-----------------------------------------------+
```

### Regression: Predicting a Number

Regression means predicting a continuous number. The answer is a value on a scale.

**Examples:**
- What will this house sell for? ($350,000)
- How many inches of rain will fall tomorrow? (2.5 inches)
- What will the temperature be at noon? (72 degrees)
- How many units will we sell next month? (1,500)

```
+-----------------------------------------------+
|           REGRESSION                            |
|                                                 |
|   Input ---------> Model ---------> Number      |
|                                                 |
|   House features   Price model      $350,000    |
|   Weather data     Rain model       2.5 inches  |
|   Sales history    Sales model      1,500 units |
+-----------------------------------------------+
```

### How to Tell Them Apart

Ask yourself: **Is the answer a category or a number?**

- Category (spam/not spam, cat/dog, yes/no) = **Classification**
- Number (price, temperature, count) = **Regression**

```
+-------------------+------------------+--------------------+
| Question          | Answer Type      | Problem Type       |
+-------------------+------------------+--------------------+
| Will it rain?     | Yes or No        | Classification     |
| How much rain?    | 2.5 inches       | Regression         |
| Is this a cat?    | Cat or Dog       | Classification     |
| How old is this   | 7 years          | Regression         |
| cat?              |                  |                    |
| Will customer     | Yes or No        | Classification     |
| leave?            |                  |                    |
| How much will     | $52.30           | Regression         |
| customer spend?   |                  |                    |
+-------------------+------------------+--------------------+
```

---

## When Is ML Useful? When Is It Overkill?

Machine learning is powerful, but it is not always the right tool. Here is a guide:

### Use ML When:

1. **The rules are too complex to write by hand**
   - Recognizing faces in photos
   - Understanding human speech
   - Detecting fraud in millions of transactions

2. **The rules keep changing**
   - Spam detection (spammers change tactics)
   - Stock market predictions (markets evolve)
   - Content recommendations (user tastes change)

3. **You have lots of data and want to find patterns**
   - Customer behavior analysis
   - Medical research with thousands of patient records
   - Weather prediction with years of historical data

4. **You need to make predictions**
   - Will this customer cancel their subscription?
   - What will sales be next quarter?
   - Which products should we recommend?

### Do NOT Use ML When:

1. **Simple rules work fine**
   - Checking if a number is even or odd (just use `%`)
   - Calculating tax (fixed formula)
   - Sorting a list (use a sort algorithm)

2. **You do not have enough data**
   - ML needs examples to learn from. Ten examples is not enough. You typically need hundreds or thousands.

3. **You need 100% accuracy**
   - ML makes predictions. Predictions can be wrong. If you need a guaranteed correct answer every time, use traditional programming.

4. **You cannot explain why a decision was made**
   - In some fields (medicine, law, finance), you must explain your reasoning. Some ML models are "black boxes" that are hard to explain.

5. **A simple lookup table would work**
   - Converting temperatures from Celsius to Fahrenheit
   - Looking up a zip code for a city
   - Mapping country codes to country names

### The Decision Flowchart

```
Do you need to make predictions
from data?
    |
    +-- No --> Use traditional programming
    |
    +-- Yes
         |
         Do you have enough data
         (hundreds+ examples)?
              |
              +-- No --> Collect more data first
              |
              +-- Yes
                   |
                   Can you write simple rules
                   that work well enough?
                        |
                        +-- Yes --> Use simple rules
                        |           (no ML needed)
                        |
                        +-- No --> Use machine learning!
```

---

## Your First ML Program: Iris Flower Classification

Let us build a complete ML program. We will classify iris flowers into three species based on their measurements.

The Iris dataset is the "Hello World" of machine learning. It contains measurements of 150 iris flowers from three species.

```python
# Import the tools we need
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

# Step 1: Load the data
iris = load_iris()
X = iris.data        # Features (measurements)
y = iris.target      # Labels (species)

# Let us see what we have
print("Number of flowers:", len(X))
print("Number of features:", X.shape[1])
print("Feature names:", iris.feature_names)
print("Species names:", list(iris.target_names))
print()

# Step 2: Split data into training and testing sets
# 80% for training, 20% for testing
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))
print()

# Step 3: Create and train the model
model = DecisionTreeClassifier(random_state=42)
model.fit(X_train, y_train)

# Step 4: Test the model
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print("Model accuracy:", round(accuracy * 100, 1), "%")
print()

# Step 5: Use the model on a new flower
# A flower with these measurements:
# sepal length=5.0, sepal width=3.5,
# petal length=1.5, petal width=0.3
new_flower = [[5.0, 3.5, 1.5, 0.3]]
predicted_species = model.predict(new_flower)
species_name = iris.target_names[predicted_species[0]]
print("Predicted species:", species_name)
```

**Expected Output:**
```
Number of flowers: 150
Number of features: 4
Feature names: ['sepal length (cm)', 'sepal width (cm)',
                'petal length (cm)', 'petal width (cm)']
Species names: ['setosa', 'versicolor', 'virginica']

Training samples: 120
Testing samples: 30

Model accuracy: 100.0 %

Predicted species: setosa
```

**Line-by-line explanation:**

- `from sklearn.datasets import load_iris` - Import the iris dataset that comes built into scikit-learn. No file download needed.
- `from sklearn.model_selection import train_test_split` - Import the function that splits data into training and testing portions.
- `from sklearn.tree import DecisionTreeClassifier` - Import the Decision Tree algorithm. It makes decisions like a flowchart.
- `from sklearn.metrics import accuracy_score` - Import a function to measure how accurate our model is.
- `iris = load_iris()` - Load the iris dataset. It contains 150 flower measurements and their species.
- `X = iris.data` - The features (input data). Capital `X` is a convention in ML. Each row is one flower. Each column is one measurement.
- `y = iris.target` - The labels (correct answers). Lowercase `y` is a convention. Each value is 0, 1, or 2 representing a species.
- `train_test_split(X, y, test_size=0.2, random_state=42)` - Split the data. 80% goes to training. 20% goes to testing. `random_state=42` ensures the same split every time you run the code.
- `model = DecisionTreeClassifier(random_state=42)` - Create a blank model.
- `model.fit(X_train, y_train)` - Train the model on the training data.
- `model.predict(X_test)` - Ask the model to predict species for the test flowers.
- `accuracy_score(y_test, predictions)` - Compare predictions to actual answers. Returns a number between 0 and 1. Multiply by 100 to get a percentage.
- `model.predict(new_flower)` - Predict the species of a brand-new flower the model has never seen.

---

## Common Mistakes

1. **Thinking ML is magic.** ML is powerful, but it is just math and statistics under the hood. It cannot learn from zero data. It cannot make perfect predictions. It finds patterns in the data you give it.

2. **Using ML for everything.** If a simple `if/else` statement solves your problem, use it. ML adds complexity. Only use it when the problem is too complex for manual rules.

3. **Not having enough data.** ML needs examples. A model trained on 10 examples will be terrible. You usually need hundreds or thousands of examples for decent results.

4. **Ignoring data quality.** "Garbage in, garbage out." If your data is full of errors, your model will learn the wrong patterns.

5. **Confusing classification and regression.** Classification predicts categories (spam/not spam). Regression predicts numbers (price, temperature). Using the wrong one gives you wrong results.

6. **Testing on training data.** Never test your model on the same data you used to train it. That is like giving a student the exam answers beforehand. Always split your data into training and testing sets.

---

## Best Practices

1. **Start simple.** Use a simple algorithm first. Only add complexity if needed. A simple model that works is better than a complex model you do not understand.

2. **Understand your data first.** Before building a model, look at your data. Check for missing values, outliers, and patterns. We cover this in Chapter 3.

3. **Always split your data.** Keep some data for testing. A common split is 80% training and 20% testing.

4. **Measure your results.** Always check how accurate your model is. If it is only 50% accurate on a yes/no question, it is no better than flipping a coin.

5. **Learn the vocabulary.** Features, labels, training, testing, accuracy. These words come up constantly. Understanding them makes everything else easier.

---

## Quick Summary

Machine learning teaches computers to learn from examples instead of following hand-written rules. There are three types: supervised (learning with labeled data), unsupervised (finding hidden patterns), and reinforcement (learning through rewards). Most real-world ML is supervised learning, which comes in two flavors: classification (predicting categories) and regression (predicting numbers). Every ML project follows the same workflow: collect data, clean it, train a model, test it, and use it.

---

## Key Points to Remember

- **Machine learning** = teaching computers to learn from data, not from explicit rules.
- **Supervised learning** = data comes with correct answers (labels). The model learns to predict those answers.
- **Unsupervised learning** = data has no labels. The model finds hidden patterns or groups.
- **Reinforcement learning** = the model learns by trial and error, receiving rewards or penalties.
- **Classification** = predicting a category (spam or not spam).
- **Regression** = predicting a number (house price).
- **Features** = the input data the model learns from (also called X).
- **Labels** = the correct answers the model learns to predict (also called y).
- **Training** = the process of the model learning from data.
- **Testing** = checking how well the model performs on unseen data.
- Always **split your data** into training and testing sets.
- ML is not magic. It needs good data and the right problem to be useful.

---

## Practice Questions

### Question 1
You want to build a system that predicts whether a customer will buy a product (yes or no). What type of ML problem is this?

**Answer:** This is a **supervised learning classification** problem. It is supervised because you have historical data with labels (customers who did or did not buy). It is classification because the answer is a category (yes or no), not a number.

### Question 2
A streaming service wants to group its users into segments based on their watching habits, but it does not know what the groups should be. What type of ML is this?

**Answer:** This is **unsupervised learning**. There are no predefined labels or categories. The algorithm must discover the groups (clusters) on its own based on patterns in the viewing data.

### Question 3
You want to predict the exact price a used car will sell for. Is this classification or regression?

**Answer:** This is **regression**. The answer is a continuous number (a price like $15,250), not a category.

### Question 4
Your friend wants to build an ML model to check if a number is prime. Is ML the right tool? Why or why not?

**Answer:** **No, ML is not the right tool.** Checking if a number is prime can be done with a simple mathematical algorithm. The rules are clear and well-defined. There is no need for ML. Using ML here would be overkill and likely less accurate than the mathematical approach.

### Question 5
What is the difference between features and labels in supervised learning?

**Answer:** **Features** (X) are the input data, the information the model uses to make predictions. For example, a house's size, number of bedrooms, and location. **Labels** (y) are the correct answers the model learns to predict. For example, the house's price. Features are what you know. Labels are what you want to predict.

---

## Exercises

### Exercise 1: Classify the Problem

For each scenario below, identify: (a) the type of ML (supervised, unsupervised, or reinforcement), and (b) whether it is classification or regression (if supervised).

1. Predicting tomorrow's temperature
2. Grouping news articles by topic
3. Teaching a robot to navigate a maze
4. Detecting whether a credit card transaction is fraudulent
5. Predicting how many units of a product will sell next month

**Expected Answers:**
1. Supervised, Regression (predicting a number)
2. Unsupervised (no labels, finding groups)
3. Reinforcement (trial and error with rewards)
4. Supervised, Classification (fraud or not fraud)
5. Supervised, Regression (predicting a number)

### Exercise 2: Build Your Own Classifier

Modify the fruit classifier example from this chapter. Add more training data (at least 6 more fruits) and add a third fruit type (banana). Hint: bananas are typically longer (heavier) and smooth.

```python
# Starter code - add your data and run it
from sklearn.tree import DecisionTreeClassifier

# Add more fruits: [weight, texture]
# texture: 0=smooth, 1=bumpy
features = [
    [140, 1],  # orange
    [130, 1],  # orange
    [150, 0],  # apple
    [170, 0],  # apple
    # Add 6+ more fruits here, including bananas
]

# Labels: 0=apple, 1=orange, 2=banana
labels = [1, 1, 0, 0]  # Update this list too

model = DecisionTreeClassifier()
model.fit(features, labels)

# Test with new fruits
test_fruits = [[145, 1], [165, 0], [120, 0]]
predictions = model.predict(test_fruits)
fruit_names = {0: "apple", 1: "orange", 2: "banana"}

for fruit, pred in zip(test_fruits, predictions):
    print(f"Fruit {fruit} -> {fruit_names[pred]}")
```

### Exercise 3: Explore the Iris Dataset

Load the Iris dataset and answer these questions by writing Python code:

1. How many features does each flower have?
2. How many flowers are in the dataset?
3. What are the names of the three species?
4. Train a Decision Tree model and check its accuracy. Try different `random_state` values (1, 10, 100). Does the accuracy change?

---

## What Is Next?

Now you know what machine learning is, how it works, and when to use it. But ML runs on data. Without data, there is no machine learning.

In Chapter 2, you will learn how to get data. You will load CSV files, work with JSON data, use free datasets from Kaggle and scikit-learn, and learn the critical skill of splitting data into training and testing sets. Data is the fuel that powers machine learning, and Chapter 2 teaches you how to get it.
