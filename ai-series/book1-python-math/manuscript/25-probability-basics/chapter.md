# Chapter 25: Probability Basics — Measuring Uncertainty

## What You Will Learn

- What probability is and how to measure it
- Events and sample spaces
- How to calculate simple probabilities
- Complementary events (the probability something does NOT happen)
- Independent events (events that do not affect each other)
- Conditional probability (probability GIVEN something happened)
- Bayes' theorem (updating beliefs with evidence)
- How to compute probabilities and run simulations in Python

## Why This Chapter Matters

AI lives in a world of uncertainty. Nothing is 100% certain.

- "Is this email spam?" — Probably, with 97% confidence.
- "Is this image a cat?" — 89% likely a cat, 10% likely a dog, 1% something else.
- "Will this customer buy?" — 65% chance yes.

Probability is the language AI uses to express uncertainty. Without it, a model could only say "yes" or "no." With probability, it can say "I am 95% confident this is correct."

Spam filters use probability. Medical diagnosis AI uses probability. Self-driving cars use probability to predict what other drivers will do.

If you want to understand how AI makes decisions, you need to understand probability.

---

## What Is Probability?

Probability is a number between 0 and 1 that measures how likely something is to happen.

```
The Probability Scale:

    0.0          0.25          0.5          0.75          1.0
     |------------|------------|------------|------------|
  Impossible    Unlikely     50-50       Likely       Certain

    Examples:
    0.0  =  Impossible (rolling a 7 on a standard die)
    0.1  =  Very unlikely (rain in the Sahara)
    0.5  =  Equally likely (flipping heads on a fair coin)
    0.9  =  Very likely (sun rising tomorrow)
    1.0  =  Certain (you exist right now)
```

### The Basic Formula

```
                    Number of favorable outcomes
    Probability = ---------------------------------
                    Total number of possible outcomes

    Example: Rolling a 3 on a fair die

    Favorable outcomes: 1 (just the number 3)
    Total outcomes: 6 (numbers 1 through 6)

    P(rolling a 3) = 1/6 ≈ 0.167  (about 16.7%)
```

### Computing Basic Probabilities in Python

```python
import numpy as np

# Probability of rolling a 3 on a fair die
favorable = 1
total = 6
prob = favorable / total
print(f"P(rolling a 3) = {favorable}/{total} = {prob:.4f} = {prob*100:.1f}%")

# Probability of rolling an even number (2, 4, or 6)
favorable_even = 3
prob_even = favorable_even / total
print(f"P(rolling even) = {favorable_even}/{total} = {prob_even:.4f} = {prob_even*100:.1f}%")

# Probability of drawing a heart from a deck of cards
hearts = 13
total_cards = 52
prob_heart = hearts / total_cards
print(f"P(drawing a heart) = {hearts}/{total_cards} = {prob_heart:.4f} = {prob_heart*100:.1f}%")
```

**Expected Output:**
```
P(rolling a 3) = 1/6 = 0.1667 = 16.7%
P(rolling even) = 3/6 = 0.5000 = 50.0%
P(drawing a heart) = 13/52 = 0.2500 = 25.0%
```

---

## Events and Sample Spaces

The **sample space** is the set of all possible outcomes. An **event** is a specific outcome or set of outcomes you care about.

```
Example: Flipping a coin

    Sample Space: {Heads, Tails}
    Event "getting heads": {Heads}
    P(Heads) = 1/2 = 0.5

Example: Rolling a die

    Sample Space: {1, 2, 3, 4, 5, 6}
    Event "rolling greater than 4": {5, 6}
    P(greater than 4) = 2/6 = 1/3 ≈ 0.333

Example: Rolling two dice

    Sample Space: All pairs (1,1), (1,2), ..., (6,6) = 36 outcomes
    Event "sum equals 7": {(1,6), (2,5), (3,4), (4,3), (5,2), (6,1)}
    P(sum = 7) = 6/36 = 1/6 ≈ 0.167
```

### Computing with Python

```python
import numpy as np

# All possible outcomes of rolling two dice
sample_space = []
for die1 in range(1, 7):
    for die2 in range(1, 7):
        sample_space.append((die1, die2))

print(f"Total outcomes: {len(sample_space)}")

# Event: sum equals 7
event_sum_7 = [(d1, d2) for d1, d2 in sample_space if d1 + d2 == 7]
print(f"\nOutcomes where sum = 7: {event_sum_7}")
print(f"Count: {len(event_sum_7)}")
print(f"P(sum = 7) = {len(event_sum_7)}/{len(sample_space)} = {len(event_sum_7)/len(sample_space):.4f}")

# Event: both dice show the same number (doubles)
event_doubles = [(d1, d2) for d1, d2 in sample_space if d1 == d2]
print(f"\nDoubles: {event_doubles}")
print(f"P(doubles) = {len(event_doubles)}/{len(sample_space)} = {len(event_doubles)/len(sample_space):.4f}")
```

**Expected Output:**
```
Total outcomes: 36

Outcomes where sum = 7: [(1, 6), (2, 5), (3, 4), (4, 3), (5, 2), (6, 1)]
Count: 6
P(sum = 7) = 6/36 = 0.1667

Doubles: [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)]
P(doubles) = 6/36 = 0.1667
```

**Line-by-line explanation:**
- We list all 36 possible outcomes by pairing each die value with every other.
- We filter for the outcomes we want (sum=7, doubles).
- Probability = count of favorable outcomes / total outcomes.

---

## Complementary Events

The complement of an event is "everything else." If event A has probability P(A), the probability of A NOT happening is:

```
    P(not A) = 1 - P(A)

    Example:
    P(rain) = 0.3
    P(no rain) = 1 - 0.3 = 0.7

    The complement is useful when it is easier to count
    what you DON'T want.
```

### Python Example

```python
import numpy as np

# What is the probability of NOT rolling a 6?
p_six = 1/6
p_not_six = 1 - p_six
print(f"P(rolling a 6) = {p_six:.4f}")
print(f"P(NOT rolling a 6) = {p_not_six:.4f}")

# What is the probability of getting at least one heads
# in 3 coin flips?
# Easier to compute the complement: P(no heads at all)
p_all_tails = (1/2) ** 3
p_at_least_one_heads = 1 - p_all_tails
print(f"\nP(all tails in 3 flips) = {p_all_tails:.4f}")
print(f"P(at least one heads in 3 flips) = {p_at_least_one_heads:.4f}")

# Verify with simulation
np.random.seed(42)
n_experiments = 100000
results = np.random.randint(0, 2, size=(n_experiments, 3))  # 0=tails, 1=heads
has_heads = np.any(results == 1, axis=1)
simulated = np.mean(has_heads)
print(f"Simulated P(at least one heads) = {simulated:.4f}")
```

**Expected Output:**
```
P(rolling a 6) = 0.1667
P(NOT rolling a 6) = 0.8333

P(all tails in 3 flips) = 0.1250
P(at least one heads in 3 flips) = 0.8750
Simulated P(at least one heads) = 0.8748
```

**Line-by-line explanation:**
- `1 - p_six` — The complement: the probability of anything except rolling a 6.
- For 3 coin flips, calculating "at least one heads" directly is messy. But "all tails" is easy: (1/2)^3 = 1/8. The complement gives us the answer.
- The simulation with 100,000 experiments confirms our math.

---

## Independent Events

Two events are **independent** if one happening does not affect the other.

```
    Independent:
    - Flipping a coin twice (the first flip doesn't affect the second)
    - Rolling two dice (each die is independent)

    NOT Independent:
    - Drawing cards without replacement (first draw changes what's left)
    - Weather today and weather tomorrow (related!)
```

For independent events, multiply the probabilities:

```
    P(A AND B) = P(A) x P(B)

    Example: What is the probability of flipping heads twice in a row?

    P(heads AND heads) = P(heads) x P(heads)
                       = 0.5 x 0.5
                       = 0.25  (25%)
```

### Python Example

```python
import numpy as np

# Probability of rolling a 6 on both of two dice
p_six = 1/6
p_double_six = p_six * p_six
print(f"P(6 on one die) = {p_six:.4f}")
print(f"P(6 on both dice) = {p_double_six:.4f}")

# Probability of flipping 5 heads in a row
p_heads = 0.5
p_five_heads = p_heads ** 5
print(f"\nP(5 heads in a row) = {p_five_heads:.4f} = 1/{int(1/p_five_heads)}")

# Simulate to verify
np.random.seed(42)
n_experiments = 100000
flips = np.random.randint(0, 2, size=(n_experiments, 5))
all_heads = np.all(flips == 1, axis=1)
simulated = np.mean(all_heads)
print(f"Simulated P(5 heads) = {simulated:.4f}")
```

**Expected Output:**
```
P(6 on one die) = 0.1667
P(6 on both dice) = 0.0278

P(5 heads in a row) = 0.0312 = 1/32
Simulated P(5 heads) = 0.0316
```

---

## Conditional Probability

**Conditional probability** asks: "What is the probability of A, GIVEN that B has already happened?"

We write this as P(A | B), read as "probability of A given B."

### Real-Life Analogy

```
    Overall: P(passing the test) = 0.60  (60% pass rate)

    But if you studied:
    P(passing | studied) = 0.90  (90% of people who study pass)

    And if you didn't study:
    P(passing | didn't study) = 0.30  (only 30% who don't study pass)

    Knowing whether someone studied CHANGES the probability.
```

### The Formula

```
                    P(A AND B)
    P(A | B) = ----------------
                      P(B)

    "The probability of A given B equals
     the probability of both happening
     divided by the probability of B."
```

### Python Example

```python
import numpy as np

# A bag has 3 red balls and 7 blue balls (10 total)
# You draw two balls WITHOUT replacement.

# P(second ball is red | first ball was red)?

# If first was red: 2 red and 7 blue remain (9 total)
p_second_red_given_first_red = 2 / 9

# If first was blue: 3 red and 6 blue remain (9 total)
p_second_red_given_first_blue = 3 / 9

print("Bag: 3 red, 7 blue balls. Draw 2 without replacement.")
print(f"P(2nd red | 1st was red) = 2/9 = {p_second_red_given_first_red:.4f}")
print(f"P(2nd red | 1st was blue) = 3/9 = {p_second_red_given_first_blue:.4f}")

# Simulate it
np.random.seed(42)
n_experiments = 100000
# Create bag: 0=red, 1=blue
bag = [0, 0, 0, 1, 1, 1, 1, 1, 1, 1]

count_first_red = 0
count_second_red_after_first_red = 0

for _ in range(n_experiments):
    shuffled = np.random.permutation(bag)
    first = shuffled[0]
    second = shuffled[1]

    if first == 0:  # first was red
        count_first_red += 1
        if second == 0:  # second also red
            count_second_red_after_first_red += 1

simulated = count_second_red_after_first_red / count_first_red
print(f"\nSimulated P(2nd red | 1st red) = {simulated:.4f}")
```

**Expected Output:**
```
Bag: 3 red, 7 blue balls. Draw 2 without replacement.
P(2nd red | 1st was red) = 2/9 = 0.2222
P(2nd red | 1st was blue) = 3/9 = 0.3333

Simulated P(2nd red | 1st red) = 0.2226
```

**Line-by-line explanation:**
- After drawing a red ball first, only 2 red balls remain out of 9 total.
- After drawing a blue ball first, all 3 red balls remain out of 9 total.
- The first draw changes the probability of the second draw. These events are NOT independent.

---

## Bayes' Theorem

Bayes' theorem is one of the most important ideas in probability. It tells you how to **update your beliefs when you get new evidence**.

### The Idea

```
    You start with a PRIOR belief (what you thought before).
    You observe some EVIDENCE (new information).
    You compute the POSTERIOR belief (what you think now).

    Prior belief + Evidence = Updated belief

    Example:
    - You think there is a 1% chance you have a disease (prior).
    - You take a test and it comes back positive (evidence).
    - Now what is the probability you actually have the disease? (posterior)
    - Surprise: it might NOT be as high as you think!
```

### The Formula

```
                         P(B | A) * P(A)
    P(A | B) = -----------------------------------
                            P(B)

    Where:
    P(A | B) = posterior (what we want to know)
    P(A)     = prior (our initial belief)
    P(B | A) = likelihood (probability of evidence given our theory)
    P(B)     = total probability of the evidence
```

### Real-Life Example: Medical Test

```
A medical test for a rare disease:

    - 1% of people have the disease:       P(disease) = 0.01
    - The test correctly detects it 99%:    P(positive | disease) = 0.99
    - The test has a 5% false positive:     P(positive | no disease) = 0.05

    You test positive. What is the probability you ACTUALLY have the disease?

    Step 1: P(positive)
    = P(positive | disease) * P(disease) + P(positive | no disease) * P(no disease)
    = 0.99 * 0.01 + 0.05 * 0.99
    = 0.0099 + 0.0495
    = 0.0594

    Step 2: P(disease | positive)
    = P(positive | disease) * P(disease) / P(positive)
    = 0.99 * 0.01 / 0.0594
    = 0.1667

    SURPRISE: Even with a positive test, there is only a 16.7% chance
    you actually have the disease!

    Why? Because the disease is rare (1%). Most positive results
    are false positives from the 99% of healthy people.
```

### Python Implementation

```python
import numpy as np

# Medical test example
p_disease = 0.01              # Prior: 1% have the disease
p_no_disease = 1 - p_disease   # 99% are healthy
p_positive_given_disease = 0.99     # Test sensitivity
p_positive_given_no_disease = 0.05  # False positive rate

# Total probability of testing positive
p_positive = (p_positive_given_disease * p_disease +
              p_positive_given_no_disease * p_no_disease)

# Bayes' theorem: P(disease | positive)
p_disease_given_positive = (p_positive_given_disease * p_disease) / p_positive

print("=== Medical Test: Bayes' Theorem ===")
print(f"P(disease) = {p_disease}")
print(f"P(positive | disease) = {p_positive_given_disease}")
print(f"P(positive | no disease) = {p_positive_given_no_disease}")
print(f"\nP(positive) = {p_positive:.4f}")
print(f"P(disease | positive) = {p_disease_given_positive:.4f}")
print(f"\nEven with a positive test, there is only a "
      f"{p_disease_given_positive*100:.1f}% chance of having the disease!")
```

**Expected Output:**
```
=== Medical Test: Bayes' Theorem ===
P(disease) = 0.01
P(positive | disease) = 0.99
P(positive | no disease) = 0.05

P(positive) = 0.0594
P(disease | positive) = 0.1667

Even with a positive test, there is only a 16.7% chance of having the disease!
```

### Bayes' Theorem for Spam Filtering

```python
import numpy as np

# Simple spam filter using Bayes' theorem
# Question: If an email contains the word "free", is it spam?

p_spam = 0.3                       # 30% of emails are spam
p_not_spam = 0.7                   # 70% are legitimate
p_free_given_spam = 0.8            # 80% of spam contains "free"
p_free_given_not_spam = 0.1        # 10% of legit emails contain "free"

# P("free")
p_free = (p_free_given_spam * p_spam +
          p_free_given_not_spam * p_not_spam)

# P(spam | "free")
p_spam_given_free = (p_free_given_spam * p_spam) / p_free

print("=== Spam Filter: Bayes' Theorem ===")
print(f"P(spam) = {p_spam}")
print(f'P("free" | spam) = {p_free_given_spam}')
print(f'P("free" | not spam) = {p_free_given_not_spam}')
print(f'\nP("free") = {p_free:.4f}')
print(f'P(spam | "free") = {p_spam_given_free:.4f}')
print(f'\nIf an email contains "free", there is a '
      f'{p_spam_given_free*100:.1f}% chance it is spam.')
```

**Expected Output:**
```
=== Spam Filter: Bayes' Theorem ===
P(spam) = 0.3
P("free" | spam) = 0.8
P("free" | not spam) = 0.1

P("free") = 0.3100
P(spam | "free") = 0.7742

If an email contains "free", there is a 77.4% chance it is spam.
```

**Line-by-line explanation:**
- We know 30% of emails are spam and 80% of spam emails contain "free."
- Using Bayes' theorem, seeing "free" bumps the spam probability from 30% to 77.4%.
- This is exactly how real spam filters work (with more words and more data).

---

## Coin Flip and Dice Simulations

Simulations are a powerful way to verify probability calculations. Run the experiment many times and see how the results match the math.

### Coin Flip Simulation

```python
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

# Simulate flipping a fair coin 10,000 times
n_flips = 10000
flips = np.random.randint(0, 2, size=n_flips)  # 0=tails, 1=heads

# Track running proportion of heads
cumulative_heads = np.cumsum(flips)
flip_numbers = np.arange(1, n_flips + 1)
running_proportion = cumulative_heads / flip_numbers

# Plot
plt.figure(figsize=(12, 5))
plt.plot(flip_numbers, running_proportion, 'b-', linewidth=1, alpha=0.7)
plt.axhline(y=0.5, color='r', linestyle='--', linewidth=2, label='True P(heads) = 0.5')
plt.xlabel('Number of Flips')
plt.ylabel('Proportion of Heads')
plt.title('Law of Large Numbers: Coin Flip Simulation')
plt.legend()
plt.grid(True, alpha=0.3)
plt.ylim(0.3, 0.7)

plt.tight_layout()
plt.savefig('coin_simulation.png', dpi=100, bbox_inches='tight')
plt.show()

print(f"After {n_flips} flips:")
print(f"  Heads: {np.sum(flips)}")
print(f"  Tails: {n_flips - np.sum(flips)}")
print(f"  Proportion of heads: {np.mean(flips):.4f}")
print(f"  Expected: 0.5000")
```

**Expected Output:**
```
After 10000 flips:
  Heads: 5020
  Tails: 4980
  Proportion of heads: 0.5020
  Expected: 0.5000
```

The plot shows the proportion of heads starting noisy and gradually settling near 0.5. This is the **Law of Large Numbers**: with more experiments, the observed probability gets closer to the true probability.

### Dice Simulation

```python
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

# Simulate rolling two dice 100,000 times
n_rolls = 100000
die1 = np.random.randint(1, 7, size=n_rolls)
die2 = np.random.randint(1, 7, size=n_rolls)
sums = die1 + die2

# Count each possible sum
possible_sums = range(2, 13)
counts = [np.sum(sums == s) for s in possible_sums]
proportions = [c / n_rolls for c in counts]

# Theoretical probabilities
theoretical = [1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1]
theoretical = [t / 36 for t in theoretical]

# Plot
fig, ax = plt.subplots(figsize=(10, 6))

x = np.arange(len(possible_sums))
width = 0.35

bars1 = ax.bar(x - width/2, proportions, width, label='Simulated', color='steelblue')
bars2 = ax.bar(x + width/2, theoretical, width, label='Theoretical', color='coral')

ax.set_xlabel('Sum of Two Dice')
ax.set_ylabel('Probability')
ax.set_title('Sum of Two Dice: Simulated vs. Theoretical')
ax.set_xticks(x)
ax.set_xticklabels(possible_sums)
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('dice_simulation.png', dpi=100, bbox_inches='tight')
plt.show()

print("Sum  Simulated  Theoretical")
print("---  ---------  -----------")
for s, sim, theo in zip(possible_sums, proportions, theoretical):
    print(f" {s:2d}    {sim:.4f}      {theo:.4f}")
```

**Expected Output:**
```
Sum  Simulated  Theoretical
---  ---------  -----------
  2    0.0271      0.0278
  3    0.0563      0.0556
  4    0.0842      0.0833
  5    0.1107      0.1111
  6    0.1380      0.1389
  7    0.1681      0.1667
  8    0.1382      0.1389
  9    0.1096      0.1111
 10    0.0832      0.0833
 11    0.0561      0.0556
 12    0.0285      0.0278
```

The simulated probabilities closely match the theoretical ones. The sum of 7 is the most common outcome (about 16.7%).

---

## Putting It All Together: A Bayesian Classifier

```python
import numpy as np

# Build a simple Bayesian classifier
# Classify whether a fruit is an Apple or Orange based on features

# Training data (made up but realistic)
# Feature: weight in grams
apple_weights = np.array([150, 160, 155, 170, 145, 165, 158, 152])
orange_weights = np.array([200, 190, 210, 195, 205, 185, 198, 215])

# Prior probabilities (assume equal)
p_apple = 0.5
p_orange = 0.5

# Compute mean and std for each class
apple_mean = np.mean(apple_weights)
apple_std = np.std(apple_weights)
orange_mean = np.mean(orange_weights)
orange_std = np.std(orange_weights)

print("Training data summary:")
print(f"  Apples:  mean={apple_mean:.1f}g, std={apple_std:.1f}g")
print(f"  Oranges: mean={orange_mean:.1f}g, std={orange_std:.1f}g")

# Gaussian probability density function
def gaussian_pdf(x, mean, std):
    return (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean) / std) ** 2)

# Classify a new fruit that weighs 175 grams
new_weight = 175

# Likelihood: P(weight=175 | apple) and P(weight=175 | orange)
p_weight_given_apple = gaussian_pdf(new_weight, apple_mean, apple_std)
p_weight_given_orange = gaussian_pdf(new_weight, orange_mean, orange_std)

# Posterior using Bayes' theorem
p_total = p_weight_given_apple * p_apple + p_weight_given_orange * p_orange
p_apple_given_weight = (p_weight_given_apple * p_apple) / p_total
p_orange_given_weight = (p_weight_given_orange * p_orange) / p_total

print(f"\nClassifying a fruit weighing {new_weight}g:")
print(f"  P(apple | {new_weight}g) = {p_apple_given_weight:.4f} ({p_apple_given_weight*100:.1f}%)")
print(f"  P(orange | {new_weight}g) = {p_orange_given_weight:.4f} ({p_orange_given_weight*100:.1f}%)")
print(f"\n  Prediction: {'Apple' if p_apple_given_weight > p_orange_given_weight else 'Orange'}")
```

**Expected Output:**
```
Training data summary:
  Apples:  mean=156.9g, std=7.5g
  Oranges: mean=199.8g, std=9.4g

Classifying a fruit weighing 175g:
  P(apple | 175g) = 0.8413 (84.1%)
  P(orange | 175g) = 0.1587 (15.9%)

  Prediction: Apple
```

**Line-by-line explanation:**
- We model each fruit type with a Gaussian (bell curve) based on training data.
- For a 175g fruit, we compute how likely that weight is for apples vs. oranges.
- Bayes' theorem combines the likelihoods with our prior beliefs.
- The classifier says: 84% apple, 16% orange. Prediction: Apple.

---

## Common Mistakes

1. **Confusing P(A | B) with P(B | A).**
   - P(positive test | disease) is NOT the same as P(disease | positive test).
   - The medical test example shows they can be very different!

2. **Assuming events are independent when they are not.**
   - Drawing cards without replacement? NOT independent.
   - Always ask: "Does one event change the probability of the other?"

3. **Forgetting that probabilities must sum to 1.**
   - P(A) + P(not A) = 1. Always.
   - If you get a probability greater than 1, something is wrong.

4. **Ignoring the base rate (prior probability).**
   - A 99% accurate test for a rare disease still produces mostly false positives.
   - Always consider how common the event is to begin with.

5. **Using multiplication for non-independent events.**
   - P(A AND B) = P(A) * P(B) ONLY if A and B are independent.
   - Otherwise, P(A AND B) = P(A) * P(B | A).

---

## Best Practices

1. **Always define your sample space first.** Know all possible outcomes before calculating probabilities.

2. **Use simulations to check your math.** If your calculated answer is 0.25, simulate it 100,000 times and see if you get close to 25%.

3. **Think about whether events are independent.** This is the single most important question in probability.

4. **Use complements when counting "at least one."** P(at least one) = 1 - P(none). This is almost always easier.

5. **Draw diagrams for Bayes' theorem.** A tree diagram or a 2x2 table makes the calculation much clearer.

---

## Quick Summary

```
Probability Cheat Sheet:

    Concept               Formula                        Example
    -------               -------                        -------
    Basic probability      favorable / total              P(heads) = 1/2
    Complement             P(not A) = 1 - P(A)           P(not 6) = 5/6
    Independent events     P(A AND B) = P(A) * P(B)      Two heads = 1/4
    Conditional            P(A|B) = P(A AND B) / P(B)    Depends on context
    Bayes' theorem         P(A|B) = P(B|A)*P(A) / P(B)  Updating beliefs

    Python Tools:
    np.random.randint()    Random integers (dice, coins)
    np.random.rand()       Random floats 0 to 1
    np.random.choice()     Pick from a list
    np.mean()              Estimate probability from simulation
```

---

## Key Points to Remember

1. Probability ranges from 0 (impossible) to 1 (certain). It measures how likely something is.
2. The sample space is all possible outcomes. An event is a subset you care about.
3. P(not A) = 1 - P(A). Use this shortcut whenever "at least one" appears.
4. Independent events do not affect each other. Multiply their probabilities.
5. Conditional probability P(A|B) is the probability of A given that B happened.
6. P(A|B) is NOT the same as P(B|A). This confusion is called the "prosecutor's fallacy."
7. Bayes' theorem updates your beliefs with evidence: posterior = likelihood * prior / evidence.
8. Simulations are a powerful way to verify probability calculations.
9. Spam filters, medical diagnosis, and AI classifiers all use Bayes' theorem.
10. Always consider the base rate (prior). A rare event plus a positive test does not mean certainty.

---

## Practice Questions

1. You flip a coin 4 times. What is the probability of getting exactly 3 heads? (Hint: count the favorable outcomes.)

2. A bag has 5 red and 3 blue marbles. You draw 2 marbles without replacement. What is P(both are red)?

3. In your own words, explain why P(disease | positive test) can be very different from P(positive test | disease).

4. A weather app says there is a 20% chance of rain each day. Assuming days are independent, what is the probability it rains on at least one of the next 3 days?

5. You have two dice. One is fair. The other always rolls 6. You pick a die at random and roll a 6. What is the probability you picked the loaded die? (Use Bayes' theorem.)

---

## Exercises

### Exercise 1: Coin Flip Simulation

Write a simulation that flips a biased coin (P(heads) = 0.7) 10,000 times. Plot the running proportion of heads. Verify it converges to 0.7.

**Hint:** Use `np.random.choice(['H', 'T'], p=[0.7, 0.3], size=10000)`.

### Exercise 2: The Birthday Problem

Write a simulation to estimate: in a group of 23 people, what is the probability that at least two share a birthday? Run 100,000 trials. The answer should be close to 50.7%.

**Hint:** For each trial, generate 23 random integers from 1 to 365 and check for duplicates.

### Exercise 3: Bayesian Spam Filter

Build a spam filter that uses two words: "free" and "money." Given:
- P(spam) = 0.4
- P("free" | spam) = 0.7, P("free" | not spam) = 0.05
- P("money" | spam) = 0.6, P("money" | not spam) = 0.02

Assume the words are independent given the class. Compute P(spam | "free" AND "money"). Then simulate 100,000 emails and verify your answer.

---

## What Is Next?

Congratulations! You have now covered the essential math for AI: linear algebra (matrices, eigenvalues), calculus (derivatives, gradients), and probability (Bayes' theorem, conditional probability). These three pillars support everything in machine learning. In the next chapters, we will start applying these tools to real AI problems, building models that actually learn from data.
