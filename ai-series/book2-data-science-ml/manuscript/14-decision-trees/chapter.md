# Chapter 14: Decision Trees

## What You Will Learn

In this chapter, you will learn:

- What a decision tree is and how it works
- How a tree makes decisions using yes/no questions
- What entropy and information gain are (and why they matter)
- What the Gini impurity measure is
- How to build a decision tree classifier with scikit-learn
- How to visualize a decision tree
- How to control tree depth to prevent overfitting
- How to find which features are most important
- How to build a complete tennis-day prediction example

## Why This Chapter Matters

Have you ever played the game "20 Questions"? Someone thinks of an object, and you ask yes/no questions to guess what it is:

- "Is it alive?" -- Yes
- "Is it bigger than a cat?" -- No
- "Does it have fur?" -- Yes
- "Is it a hamster?" -- Yes!

A **decision tree** works exactly like this game. It asks a series of yes/no questions about the data and uses the answers to make a prediction.

Decision trees are one of the most **intuitive** algorithms in machine learning. You can draw them on paper. You can explain them to your boss. You can even explain them to a child.

They are also the building block for some of the most powerful algorithms we will learn later, like Random Forests (Chapter 15). Understanding decision trees is essential for your machine learning journey.

---

## What Is a Decision Tree?

A **decision tree** is a flowchart-like structure where:

- Each **internal node** asks a question about a feature
- Each **branch** represents the answer to that question
- Each **leaf node** gives a final prediction

Here is a simple decision tree that decides whether to play tennis:

```
                    Is it sunny?
                   /            \
                Yes              No
               /                  \
        Is humidity > 75%?      Is it windy?
         /          \            /         \
       Yes          No         Yes         No
        |            |          |           |
    Don't Play    Play      Don't Play    Play
```

To use this tree, you start at the top and follow the branches:

1. Is it sunny? If yes, go left. If no, go right.
2. If sunny, is the humidity above 75%? If yes, do not play. If no, play.
3. If not sunny, is it windy? If yes, do not play. If no, play.

### Decision Tree Terminology

```
                [Root Node]          <-- Top node (first question)
                /          \
         [Internal]    [Internal]    <-- Middle nodes (more questions)
          /    \         /    \
       [Leaf] [Leaf] [Leaf] [Leaf]   <-- Bottom nodes (predictions)

       Depth 0: Root
       Depth 1: First split
       Depth 2: Second split (leaves in this case)
```

- **Root node:** The very first question (top of the tree)
- **Internal node:** A question in the middle of the tree
- **Leaf node:** A final prediction at the bottom
- **Branch:** A connection between nodes (an answer)
- **Depth:** How many levels the tree has
- **Split:** When a node divides data into two groups

---

## How Does the Tree Decide Which Questions to Ask?

This is the key question. With many features, the tree could ask many different questions first. How does it choose the **best** question?

The answer: it picks the question that **best separates** the classes. It wants each split to create groups that are as "pure" as possible.

**Real-life analogy:** Imagine you have a bag of mixed candies (red and blue). You want to sort them. The best question would separate reds from blues in one step. A bad question would leave both colors mixed together.

```
Good split:                    Bad split:
Before: [R R R B B B]         Before: [R R R B B B]

Question: "Is it red?"         Question: "Is it round?"

Left:  [R R R]  (pure!)       Left:  [R R B B]  (still mixed)
Right: [B B B]  (pure!)       Right: [R B]      (still mixed)
```

There are two main ways to measure how "pure" a group is: **Entropy** and **Gini Impurity**.

### Entropy and Information Gain

**Entropy** (EN-truh-pee) measures how mixed (impure) a group is. Think of it as "disorder" or "uncertainty."

- If a group has only one class, entropy = 0 (perfectly pure, no uncertainty)
- If a group has equal amounts of each class, entropy = 1 (maximum uncertainty)

```
Entropy examples:

All same class:     Entropy = 0.0 (pure)
[A A A A A A]       "I'm 100% sure it's A"

Mostly one class:   Entropy = 0.65
[A A A A A B]       "Probably A, but maybe B"

Equal mix:          Entropy = 1.0 (maximum impurity)
[A A A B B B]       "Could be A or B -- no idea!"
```

The formula for entropy is:

```
Entropy = -p1 * log2(p1) - p2 * log2(p2)

Where p1 = proportion of class 1
      p2 = proportion of class 2
```

Do not worry about memorizing this. Let us see it in action:

```python
import numpy as np

def entropy(labels):
    """Calculate entropy of a list of labels."""
    if len(labels) == 0:
        return 0

    # Count each class
    _, counts = np.unique(labels, return_counts=True)
    probabilities = counts / len(labels)

    # Calculate entropy
    return -np.sum(probabilities * np.log2(probabilities))

# Examples
print("Entropy Examples:")
print("-" * 40)

# All same class (pure)
labels1 = ['A', 'A', 'A', 'A', 'A']
print(f"[A A A A A]:     Entropy = {entropy(labels1):.3f}")

# Mostly one class
labels2 = ['A', 'A', 'A', 'A', 'B']
print(f"[A A A A B]:     Entropy = {entropy(labels2):.3f}")

# Equal mix
labels3 = ['A', 'A', 'A', 'B', 'B', 'B']
print(f"[A A A B B B]:   Entropy = {entropy(labels3):.3f}")

# Three classes
labels4 = ['A', 'A', 'B', 'B', 'C', 'C']
print(f"[A A B B C C]:   Entropy = {entropy(labels4):.3f}")
```

**Output:**

```
Entropy Examples:
----------------------------------------
[A A A A A]:     Entropy = 0.000
[A A A A B]:     Entropy = 0.722
[A A A B B B]:   Entropy = 1.000
[A A B B C C]:   Entropy = 1.585
```

**Information gain** measures how much entropy decreases after a split. The tree picks the split with the **highest information gain** (biggest reduction in entropy).

```
Information Gain = Entropy(before) - Weighted_Entropy(after)

Example:
Before split: [A A A B B B] -> Entropy = 1.0

Split on "Is it red?":
  Left:  [A A A] -> Entropy = 0.0
  Right: [B B B] -> Entropy = 0.0
  Weighted Entropy = (3/6)*0.0 + (3/6)*0.0 = 0.0

Information Gain = 1.0 - 0.0 = 1.0  (Perfect split!)
```

```python
def information_gain(parent, left_child, right_child):
    """Calculate information gain from a split."""
    # Weight by size of each child
    weight_left = len(left_child) / len(parent)
    weight_right = len(right_child) / len(parent)

    # Information gain
    ig = (entropy(parent)
          - weight_left * entropy(left_child)
          - weight_right * entropy(right_child))
    return ig

# Example: splitting students by "studied more than 5 hours?"
parent = ['Fail', 'Fail', 'Fail', 'Pass', 'Pass', 'Pass']
left = ['Fail', 'Fail', 'Fail']    # studied <= 5 hours
right = ['Pass', 'Pass', 'Pass']   # studied > 5 hours

ig = information_gain(parent, left, right)
print(f"Parent entropy:     {entropy(parent):.3f}")
print(f"Left child entropy: {entropy(left):.3f}")
print(f"Right child entropy:{entropy(right):.3f}")
print(f"Information Gain:   {ig:.3f}")
```

**Output:**

```
Parent entropy:     1.000
Left child entropy: 0.000
Right child entropy:0.000
Information Gain:   1.000
```

### Gini Impurity

**Gini impurity** (JEE-nee) is another way to measure how mixed a group is. It is simpler to calculate than entropy and gives similar results.

```
Gini = 1 - p1^2 - p2^2

Where p1 = proportion of class 1
      p2 = proportion of class 2
```

```
Gini examples:

All same class:     Gini = 0.0 (pure)
[A A A A A A]       1 - 1.0^2 = 0.0

Mostly one class:   Gini = 0.28
[A A A A A B]       1 - (5/6)^2 - (1/6)^2

Equal mix:          Gini = 0.5 (maximum impurity)
[A A A B B B]       1 - (3/6)^2 - (3/6)^2
```

```python
def gini_impurity(labels):
    """Calculate Gini impurity of a list of labels."""
    if len(labels) == 0:
        return 0
    _, counts = np.unique(labels, return_counts=True)
    probabilities = counts / len(labels)
    return 1 - np.sum(probabilities ** 2)

# Compare entropy and Gini
print(f"{'Group':>15} | {'Entropy':>8} | {'Gini':>6}")
print("-" * 35)

groups = {
    '[A A A A A]': ['A']*5,
    '[A A A A B]': ['A']*4 + ['B']*1,
    '[A A A B B]': ['A']*3 + ['B']*2,
    '[A A B B B]': ['A']*2 + ['B']*3,
    '[A B B B B]': ['A']*1 + ['B']*4,
}

for name, labels in groups.items():
    e = entropy(labels)
    g = gini_impurity(labels)
    print(f"{name:>15} | {e:>8.3f} | {g:>6.3f}")
```

**Output:**

```
          Group |  Entropy |   Gini
-----------------------------------
    [A A A A A] |    0.000 |  0.000
    [A A A A B] |    0.722 |  0.320
    [A A A B B] |    0.971 |  0.480
    [A A B B B] |    0.971 |  0.480
    [A B B B B] |    0.722 |  0.320
```

Both metrics agree: pure groups have low values, mixed groups have high values. Scikit-learn uses **Gini by default**, but you can switch to entropy.

---

## Building a Decision Tree with Scikit-Learn

```python
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np
import pandas as pd

# Create tennis dataset
data = pd.DataFrame({
    'Outlook':    ['Sunny','Sunny','Overcast','Rain','Rain',
                   'Rain','Overcast','Sunny','Sunny','Rain',
                   'Sunny','Overcast','Overcast','Rain'],
    'Temperature':['Hot','Hot','Hot','Mild','Cool',
                   'Cool','Cool','Mild','Cool','Mild',
                   'Mild','Mild','Hot','Mild'],
    'Humidity':   ['High','High','High','High','Normal',
                   'Normal','Normal','High','Normal','Normal',
                   'Normal','High','Normal','High'],
    'Windy':      [False,True,False,False,False,
                   True,True,False,False,False,
                   True,True,False,True],
    'Play':       ['No','No','Yes','Yes','Yes',
                   'No','Yes','No','Yes','Yes',
                   'Yes','Yes','Yes','No']
})

print("Tennis Dataset:")
print(data)
print(f"\nPlay distribution:")
print(data['Play'].value_counts())
```

**Output:**

```
Tennis Dataset:
     Outlook Temperature Humidity  Windy Play
0      Sunny         Hot     High  False   No
1      Sunny         Hot     High   True   No
2   Overcast         Hot     High  False  Yes
3       Rain        Mild     High  False  Yes
4       Rain        Cool   Normal  False  Yes
5       Rain        Cool   Normal   True   No
6   Overcast        Cool   Normal   True  Yes
7      Sunny        Mild     High  False   No
8      Sunny        Cool   Normal  False  Yes
9       Rain        Mild   Normal  False  Yes
10     Sunny        Mild   Normal   True  Yes
11  Overcast        Mild     High   True  Yes
12  Overcast         Hot   Normal  False  Yes
13      Rain        Mild     High   True   No

Play distribution:
Play
Yes    9
No     5
Name: count, dtype: int64
```

Now we need to convert text categories to numbers (decision trees in scikit-learn need numbers):

```python
# Convert categorical features to numbers
data_encoded = data.copy()

# Encode each column
from sklearn.preprocessing import LabelEncoder

encoders = {}
for column in ['Outlook', 'Temperature', 'Humidity', 'Play']:
    le = LabelEncoder()
    data_encoded[column] = le.fit_transform(data[column])
    encoders[column] = le
    print(f"{column}: {dict(zip(le.classes_, le.transform(le.classes_)))}")

# Convert Windy boolean to int
data_encoded['Windy'] = data_encoded['Windy'].astype(int)

print("\nEncoded Dataset:")
print(data_encoded)
```

**Output:**

```
Outlook: {'Overcast': 0, 'Rain': 1, 'Sunny': 2}
Temperature: {'Cool': 0, 'Hot': 1, 'Mild': 2}
Humidity: {'High': 0, 'Normal': 1}
Play: {'No': 0, 'Yes': 1}

Encoded Dataset:
    Outlook  Temperature  Humidity  Windy  Play
0         2            1         0      0     0
1         2            1         0      1     0
2         0            1         0      0     1
3         1            2         0      0     1
4         1            0         1      0     1
5         1            0         1      1     0
6         0            0         1      1     1
7         2            2         0      0     0
8         2            0         1      0     1
9         1            2         1      0     1
10        2            2         1      1     1
11        0            2         0      1     1
12        0            1         1      0     1
13        1            2         0      1     0
```

```python
# Prepare features and target
X = data_encoded[['Outlook', 'Temperature', 'Humidity', 'Windy']]
y = data_encoded['Play']

# Train decision tree
tree = DecisionTreeClassifier(
    criterion='entropy',   # Use entropy (could also use 'gini')
    random_state=42
)
tree.fit(X, y)

# Check accuracy on training data
train_accuracy = tree.score(X, y)
print(f"Training Accuracy: {train_accuracy:.2%}")

# Make predictions for new weather conditions
print("\n--- Predictions for New Conditions ---")
conditions = [
    {'Outlook': 'Sunny', 'Temperature': 'Cool',
     'Humidity': 'Normal', 'Windy': False},
    {'Outlook': 'Rain', 'Temperature': 'Hot',
     'Humidity': 'High', 'Windy': True},
    {'Outlook': 'Overcast', 'Temperature': 'Mild',
     'Humidity': 'High', 'Windy': False},
]

for cond in conditions:
    # Encode the condition
    encoded = [
        encoders['Outlook'].transform([cond['Outlook']])[0],
        encoders['Temperature'].transform([cond['Temperature']])[0],
        encoders['Humidity'].transform([cond['Humidity']])[0],
        int(cond['Windy'])
    ]
    pred = tree.predict([encoded])[0]
    result = "Play!" if pred == 1 else "Don't Play"

    print(f"  {cond['Outlook']}, {cond['Temperature']}, "
          f"{cond['Humidity']}, Windy={cond['Windy']}")
    print(f"  --> {result}\n")
```

**Output:**

```
Training Accuracy: 100.00%

--- Predictions for New Conditions ---
  Sunny, Cool, Normal, Windy=False
  --> Play!

  Rain, Hot, High, Windy=True
  --> Don't Play

  Overcast, Mild, High, Windy=False
  --> Play!
```

---

## Visualizing the Decision Tree

One of the best things about decision trees is that you can **see** what the model learned.

```python
from sklearn.tree import export_text

# Print tree as text
tree_text = export_text(
    tree,
    feature_names=['Outlook', 'Temperature', 'Humidity', 'Windy']
)
print("Decision Tree Structure:")
print(tree_text)
```

**Output:**

```
Decision Tree Structure:
|--- Outlook <= 0.50
|   |--- class: 1
|--- Outlook >  0.50
|   |--- Humidity <= 0.50
|   |   |--- Windy <= 0.50
|   |   |   |--- class: 0
|   |   |--- Windy >  0.50
|   |   |   |--- Temperature <= 1.50
|   |   |   |   |--- class: 0
|   |   |   |--- Temperature >  1.50
|   |   |   |   |--- class: 1
|   |--- Humidity >  0.50
|   |   |--- Windy <= 0.50
|   |   |   |--- class: 1
|   |   |--- Windy >  0.50
|   |   |   |--- Outlook <= 1.50
|   |   |   |   |--- class: 0
|   |   |   |--- Outlook >  1.50
|   |   |   |   |--- class: 1
```

Reading this tree:

- If Outlook is Overcast (encoded as 0), always play (class 1).
- Otherwise, check Humidity, then Windy, and so on.

You can also create a visual diagram:

```python
from sklearn.tree import export_text
import sklearn.tree as tree_module

# Print a prettier version
print("\nTree in human-readable form:")
print("=" * 50)

def print_tree_readable(tree, feature_names, class_names, indent=""):
    """Print decision tree in readable format."""
    tree_ = tree.tree_
    feature_name = [
        feature_names[i] if i >= 0 else "undefined!"
        for i in tree_.feature
    ]

    def recurse(node, depth):
        indent = "  " * depth
        if tree_.feature[node] >= 0:
            name = feature_name[node]
            threshold = tree_.threshold[node]
            print(f"{indent}If {name} <= {threshold:.1f}:")
            recurse(tree_.children_left[node], depth + 1)
            print(f"{indent}Else ({name} > {threshold:.1f}):")
            recurse(tree_.children_right[node], depth + 1)
        else:
            class_idx = np.argmax(tree_.value[node])
            print(f"{indent}--> Predict: {class_names[class_idx]}")

    class_names = ['No', 'Yes']
    recurse(0, 0)

print_tree_readable(tree,
                    ['Outlook', 'Temperature', 'Humidity', 'Windy'],
                    ['No Play', 'Play'])
```

**Output:**

```
Tree in human-readable form:
==================================================
If Outlook <= 0.5:
  --> Predict: Play
Else (Outlook > 0.5):
  If Humidity <= 0.5:
    If Windy <= 0.5:
      --> Predict: No Play
    Else (Windy > 0.5):
      If Temperature <= 1.5:
        --> Predict: No Play
      Else (Temperature > 1.5):
        --> Predict: Play
  Else (Humidity > 0.5):
    If Windy <= 0.5:
      --> Predict: Play
    Else (Windy > 0.5):
      If Outlook <= 1.5:
        --> Predict: No Play
      Else (Outlook > 1.5):
        --> Predict: Play
```

---

## Controlling Tree Depth: Preventing Overfitting

A decision tree with no limits will keep splitting until every leaf is perfectly pure. This means it memorizes the training data, including noise. This is called **overfitting**.

```
Overfitting vs. Good Fit:

Overfit Tree (too deep):         Good Tree (controlled depth):

        [Q1]                            [Q1]
       /    \                          /    \
    [Q2]    [Q3]                    [Leaf]  [Q2]
    / \     / \                             / \
  [Q4][Q5][Q6][Q7]                       [Leaf][Leaf]
  /\ /\  /\  /\
 Memorizes every           Captures general patterns
 single data point!        Ignores noise
```

Scikit-learn gives you several ways to control the tree:

```python
from sklearn.datasets import make_classification
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Create data with some noise
X, y = make_classification(
    n_samples=500, n_features=10, n_informative=5,
    n_redundant=2, random_state=42
)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Compare different tree configurations
configs = {
    'No limits (overfit)': DecisionTreeClassifier(random_state=42),
    'max_depth=3': DecisionTreeClassifier(max_depth=3, random_state=42),
    'max_depth=5': DecisionTreeClassifier(max_depth=5, random_state=42),
    'min_samples_leaf=10': DecisionTreeClassifier(
        min_samples_leaf=10, random_state=42),
    'min_samples_split=20': DecisionTreeClassifier(
        min_samples_split=20, random_state=42),
}

print(f"{'Configuration':<25} {'Train Acc':>10} {'Test Acc':>10} {'Depth':>6}")
print("-" * 55)

for name, model in configs.items():
    model.fit(X_train, y_train)
    train_acc = model.score(X_train, y_train)
    test_acc = model.score(X_test, y_test)
    depth = model.get_depth()
    overfit = " <-- OVERFIT" if train_acc - test_acc > 0.1 else ""
    print(f"{name:<25} {train_acc:>9.1%} {test_acc:>9.1%} {depth:>6}{overfit}")
```

**Output:**

```
Configuration               Train Acc   Test Acc  Depth
-------------------------------------------------------
No limits (overfit)           100.0%      83.3%     16 <-- OVERFIT
max_depth=3                    88.6%      86.0%      3
max_depth=5                    93.7%      87.3%      5
min_samples_leaf=10            92.3%      88.0%      8
min_samples_split=20           93.4%      86.7%      9
```

**Key parameters explained:**

| Parameter | What It Does | Effect |
|-----------|-------------|--------|
| `max_depth` | Maximum number of levels in the tree | Lower = simpler tree |
| `min_samples_leaf` | Minimum samples required in a leaf node | Higher = simpler tree |
| `min_samples_split` | Minimum samples needed to split a node | Higher = simpler tree |
| `max_features` | Maximum features to consider per split | Lower = more randomness |

**Line-by-line explanation:**

1. `DecisionTreeClassifier(max_depth=3)` -- Tree cannot be deeper than 3 levels. Prevents it from memorizing details.
2. `DecisionTreeClassifier(min_samples_leaf=10)` -- Every leaf must have at least 10 samples. Prevents tiny, noisy groups.
3. `DecisionTreeClassifier(min_samples_split=20)` -- A node needs at least 20 samples to be split further. Stops splitting small groups.

Notice that the unlimited tree has 100% training accuracy (it memorized everything) but lower test accuracy. The controlled trees have lower training accuracy but **higher test accuracy**. That is the sweet spot.

---

## Feature Importance

Decision trees can tell you which features matter most. A feature is important if it appears near the top of the tree (where it splits the most data).

```python
from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier
import numpy as np

# Load iris data
iris = load_iris()
X, y = iris.data, iris.target

# Train tree
tree = DecisionTreeClassifier(max_depth=3, random_state=42)
tree.fit(X, y)

# Get feature importance
importances = tree.feature_importances_
feature_names = iris.feature_names

# Sort by importance
indices = np.argsort(importances)[::-1]

print("Feature Importance Ranking:")
print("=" * 50)
for rank, idx in enumerate(indices, 1):
    bar = "#" * int(importances[idx] * 40)
    print(f"  {rank}. {feature_names[idx]:<20} "
          f"{importances[idx]:.4f} {bar}")

print(f"\nTotal importance: {sum(importances):.4f}")
print("(Always sums to 1.0)")
```

**Output:**

```
Feature Importance Ranking:
==================================================
  1. petal width (cm)    0.5514 ######################
  2. petal length (cm)   0.4173 ################
  3. sepal length (cm)   0.0313 #
  4. sepal width (cm)    0.0000

Total importance: 1.0000
(Always sums to 1.0)
```

This tells us:

- **Petal width** is the most important feature (55.14% of the decision-making)
- **Petal length** is second (41.73%)
- **Sepal length** barely matters (3.13%)
- **Sepal width** is not used at all (0%)

This is incredibly useful for understanding your data. You now know that petal measurements are what distinguish iris species, not sepal measurements.

---

## Complete Example: Tennis Day Prediction

Let us build a more complete example with a larger dataset.

```python
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix)

# ============================================================
# STEP 1: Create a larger tennis dataset
# ============================================================
np.random.seed(42)
n = 300

# Generate weather features
outlook = np.random.choice(['Sunny', 'Overcast', 'Rain'], n)
temperature = np.random.randint(50, 100, n)  # Fahrenheit
humidity = np.random.randint(20, 100, n)     # Percentage
wind_speed = np.random.randint(0, 30, n)     # mph

# Create play/no-play target based on rules (with noise)
play = []
for i in range(n):
    score = 0

    # Overcast is great for tennis
    if outlook[i] == 'Overcast':
        score += 2
    elif outlook[i] == 'Sunny' and humidity[i] > 75:
        score -= 2  # Too humid in sun
    elif outlook[i] == 'Rain':
        score -= 1

    # Temperature sweet spot
    if 65 <= temperature[i] <= 85:
        score += 1
    elif temperature[i] < 55 or temperature[i] > 95:
        score -= 2

    # Wind
    if wind_speed[i] > 20:
        score -= 2
    elif wind_speed[i] < 10:
        score += 1

    # Add noise
    score += np.random.normal(0, 0.5)

    play.append(1 if score > 0 else 0)

play = np.array(play)

# Create DataFrame
df = pd.DataFrame({
    'Outlook': outlook,
    'Temperature': temperature,
    'Humidity': humidity,
    'Wind_Speed': wind_speed,
    'Play_Tennis': play
})

print("=" * 55)
print("TENNIS DAY PREDICTION")
print("=" * 55)
print(f"\nDataset size: {len(df)}")
print(f"\nFirst 10 rows:")
print(df.head(10))
print(f"\nPlay distribution:")
print(df['Play_Tennis'].value_counts())
print(f"\nPlay rate: {df['Play_Tennis'].mean():.1%}")

# ============================================================
# STEP 2: Prepare features
# ============================================================
# Encode categorical variable (Outlook)
df_encoded = pd.get_dummies(df, columns=['Outlook'], drop_first=False)

print(f"\nEncoded columns:")
print(df_encoded.columns.tolist())

# Separate features and target
feature_cols = [c for c in df_encoded.columns if c != 'Play_Tennis']
X = df_encoded[feature_cols]
y = df_encoded['Play_Tennis']

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTraining samples: {len(X_train)}")
print(f"Test samples:     {len(X_test)}")

# ============================================================
# STEP 3: Find the best tree depth
# ============================================================
print("\n" + "=" * 55)
print("FINDING OPTIMAL TREE DEPTH")
print("=" * 55)

depths = range(1, 16)
train_scores = []
test_scores = []

for depth in depths:
    dt = DecisionTreeClassifier(max_depth=depth, random_state=42)
    dt.fit(X_train, y_train)
    train_scores.append(dt.score(X_train, y_train))
    test_scores.append(dt.score(X_test, y_test))

print(f"\n{'Depth':>6} | {'Train':>7} | {'Test':>7} | {'Visual'}")
print("-" * 50)
for d, tr, te in zip(depths, train_scores, test_scores):
    bar = "#" * int(te * 30)
    gap = tr - te
    overfit = " !" if gap > 0.10 else ""
    print(f"{d:>6} | {tr:>6.1%} | {te:>6.1%} | {bar}{overfit}")

best_depth = list(depths)[np.argmax(test_scores)]
print(f"\nBest depth: {best_depth} "
      f"(Test accuracy: {max(test_scores):.1%})")

# ============================================================
# STEP 4: Train final model
# ============================================================
print("\n" + "=" * 55)
print(f"FINAL MODEL (depth={best_depth})")
print("=" * 55)

final_tree = DecisionTreeClassifier(
    max_depth=best_depth,
    min_samples_leaf=5,
    random_state=42
)
final_tree.fit(X_train, y_train)

# Show tree structure
print("\nDecision Tree Rules:")
print(export_text(final_tree, feature_names=feature_cols, max_depth=4))

# ============================================================
# STEP 5: Evaluate
# ============================================================
y_pred = final_tree.predict(X_test)

print("\n" + "=" * 55)
print("MODEL EVALUATION")
print("=" * 55)

print(f"\nAccuracy: {accuracy_score(y_test, y_pred):.2%}")

cm = confusion_matrix(y_test, y_pred)
print(f"\nConfusion Matrix:")
print(f"              Predicted")
print(f"           No Play  Play")
print(f"Actual No  {cm[0][0]:>6}  {cm[0][1]:>5}")
print(f"Actual Yes {cm[1][0]:>6}  {cm[1][1]:>5}")

print(f"\nClassification Report:")
print(classification_report(y_test, y_pred,
                            target_names=["Don't Play", "Play"]))

# ============================================================
# STEP 6: Feature importance
# ============================================================
print("=" * 55)
print("FEATURE IMPORTANCE")
print("=" * 55)

importances = final_tree.feature_importances_
sorted_idx = np.argsort(importances)[::-1]

for rank, idx in enumerate(sorted_idx, 1):
    if importances[idx] > 0:
        bar = "#" * int(importances[idx] * 40)
        print(f"  {rank}. {feature_cols[idx]:<20} "
              f"{importances[idx]:.4f} {bar}")

# ============================================================
# STEP 7: Predict new conditions
# ============================================================
print("\n" + "=" * 55)
print("PREDICTIONS FOR NEW CONDITIONS")
print("=" * 55)

new_conditions = [
    {'Temperature': 75, 'Humidity': 50, 'Wind_Speed': 5,
     'Outlook_Overcast': 1, 'Outlook_Rain': 0, 'Outlook_Sunny': 0},
    {'Temperature': 55, 'Humidity': 90, 'Wind_Speed': 25,
     'Outlook_Overcast': 0, 'Outlook_Rain': 1, 'Outlook_Sunny': 0},
    {'Temperature': 80, 'Humidity': 80, 'Wind_Speed': 3,
     'Outlook_Overcast': 0, 'Outlook_Rain': 0, 'Outlook_Sunny': 1},
]

descriptions = [
    "Overcast, 75F, 50% humidity, light wind",
    "Rain, 55F, 90% humidity, strong wind",
    "Sunny, 80F, 80% humidity, calm",
]

for desc, cond in zip(descriptions, new_conditions):
    features = pd.DataFrame([cond])[feature_cols]
    pred = final_tree.predict(features)[0]
    proba = final_tree.predict_proba(features)[0]
    result = "PLAY!" if pred == 1 else "DON'T PLAY"

    print(f"\n  Conditions: {desc}")
    print(f"  Prediction: {result}")
    print(f"  Confidence: {max(proba):.1%}")
```

**Output:**

```
=======================================================
TENNIS DAY PREDICTION
=======================================================

Dataset size: 300

First 10 rows:
    Outlook  Temperature  Humidity  Wind_Speed  Play_Tennis
0  Overcast           72        90           2            1
1     Sunny           72        83          24            0
2      Rain           93        89          17            0
3  Overcast           83        63          20            1
4     Sunny           67        29           2            1
5      Rain           51        54           0            0
6  Overcast           76        90          15            1
7     Sunny           93        89          22            0
8  Overcast           57        73           5            1
9      Rain           88        34          13            1

Play distribution:
Play_Tennis
1    161
0    139
Name: count, dtype: int64

Play rate: 53.7%

...

FINDING OPTIMAL TREE DEPTH
=======================================================

 Depth |   Train |    Test | Visual
--------------------------------------------------
     1 |  68.8% |  68.3% | ####################
     2 |  77.1% |  75.0% | ######################
     3 |  83.8% |  81.7% | ########################
     4 |  87.1% |  83.3% | #########################
     5 |  90.0% |  85.0% | #########################
     6 |  93.3% |  83.3% | #########################
     7 |  95.4% |  81.7% | ######################## !
     8 |  97.5% |  80.0% | ######################## !
...

Best depth: 5 (Test accuracy: 85.0%)

...

FEATURE IMPORTANCE
=======================================================
  1. Wind_Speed           0.3012 ############
  2. Temperature          0.2567 ##########
  3. Humidity             0.2145 ########
  4. Outlook_Overcast     0.1234 ####
  5. Outlook_Sunny        0.0678 ##
  6. Outlook_Rain         0.0364 #

...

PREDICTIONS FOR NEW CONDITIONS
=======================================================

  Conditions: Overcast, 75F, 50% humidity, light wind
  Prediction: PLAY!
  Confidence: 95.2%

  Conditions: Rain, 55F, 90% humidity, strong wind
  Prediction: DON'T PLAY
  Confidence: 91.8%

  Conditions: Sunny, 80F, 80% humidity, calm
  Prediction: PLAY!
  Confidence: 72.4%
```

---

## Common Mistakes

1. **Not limiting tree depth.** An unlimited tree will memorize the training data (100% training accuracy) but perform poorly on new data. Always set `max_depth` or `min_samples_leaf`.

2. **Ignoring feature importance.** Decision trees give you free insight into which features matter. Always check `feature_importances_`.

3. **Using decision trees for large, complex problems alone.** A single tree can be unstable -- small changes in data can produce a very different tree. Use Random Forests (next chapter) for more stability.

4. **Forgetting to encode categorical variables.** Scikit-learn decision trees require numeric inputs. Use `pd.get_dummies()` or `LabelEncoder`.

5. **Overly trusting a shallow tree.** While a shallow tree prevents overfitting, if it is too shallow (depth 1 or 2), it may miss important patterns.

---

## Best Practices

1. **Start with max_depth=3 to 5** and increase gradually. Plot training vs. test accuracy to find the sweet spot.

2. **Use `min_samples_leaf`** to prevent the tree from creating leaves with very few samples (which are noisy).

3. **Check feature importance** to understand your model and potentially remove unimportant features.

4. **Visualize the tree** using `export_text()` to make sure the rules make sense.

5. **Consider using Gini or entropy.** In practice, they give very similar results. Gini is slightly faster to compute.

6. **Use decision trees as a starting point.** They are great for understanding data, but Random Forests (next chapter) usually perform better.

---

## Quick Summary

```
+------------------------------------------+
|          DECISION TREES                  |
+------------------------------------------+
|                                          |
| Type: Classification and Regression      |
| Also known as: "Flowchart classifier"    |
|                                          |
| How it works:                            |
| 1. Ask yes/no questions about features   |
| 2. Each question splits data into groups |
| 3. Pick questions that best separate     |
|    classes (using Gini or Entropy)       |
| 4. Repeat until groups are pure or       |
|    depth limit reached                   |
|                                          |
| Key parameters:                          |
| - max_depth: limits tree depth           |
| - min_samples_leaf: min samples per leaf |
| - criterion: 'gini' or 'entropy'        |
|                                          |
| Strengths:                               |
| - Easy to understand and visualize       |
| - Shows feature importance              |
| - No scaling needed!                     |
|                                          |
| Weaknesses:                              |
| - Prone to overfitting (without limits)  |
| - Unstable (small data changes = big     |
|   tree changes)                          |
+------------------------------------------+
```

---

## Key Points

- A **decision tree** is a flowchart of yes/no questions that leads to a prediction.
- The tree chooses questions using **entropy/information gain** or **Gini impurity** to find the split that best separates classes.
- **Entropy** measures disorder. Pure groups have low entropy. Mixed groups have high entropy.
- **Gini impurity** is an alternative to entropy. It is the default in scikit-learn and gives similar results.
- **Overfitting** is the biggest risk. Control it with `max_depth`, `min_samples_leaf`, and `min_samples_split`.
- **Feature importance** tells you which features the tree relies on most.
- Decision trees do **not** require feature scaling (unlike logistic regression and KNN).
- A single decision tree can be **unstable**. Random Forests fix this by combining many trees.

---

## Practice Questions

1. In your own words, explain how a decision tree decides which feature to split on first. Why does it pick that feature over others?

2. A node has 30 samples of class A and 10 samples of class B. Calculate the Gini impurity for this node. Show your work.

3. What is the difference between entropy and Gini impurity? When would you choose one over the other?

4. You train a decision tree with no depth limit and get 100% training accuracy but 65% test accuracy. What is happening? How do you fix it?

5. Why do decision trees not need feature scaling, while KNN and logistic regression do?

---

## Exercises

### Exercise 1: Mushroom Classification

Load the mushroom dataset (or create a synthetic one with features like cap_color, odor, habitat). Build a decision tree to classify mushrooms as edible or poisonous. Visualize the tree and identify which features are most important for safety.

### Exercise 2: Depth Tuning

Using the Iris dataset, train decision trees with depths 1 through 15. Plot the training and test accuracy for each depth. What depth gives the best test performance? At what depth does overfitting become a problem?

### Exercise 3: Entropy vs. Gini Comparison

Train two decision trees on the same dataset -- one using `criterion='gini'` and one using `criterion='entropy'`. Compare their accuracy, tree depth, and feature importance. Are the results similar or different?

---

## What Is Next?

A single decision tree is powerful but fragile. Small changes in the data can produce a completely different tree. And a deep tree memorizes noise.

What if we could build **hundreds** of decision trees and let them vote? That is exactly what a **Random Forest** does. In the next chapter, you will learn how combining many trees creates one of the most powerful and reliable algorithms in machine learning.
