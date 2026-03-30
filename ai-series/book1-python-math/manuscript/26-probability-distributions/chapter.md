# Chapter 26: Probability Distributions — The Shape of Data

## What You Will Learn

- What a probability distribution is and why it matters
- The uniform distribution (equal chance for everything)
- The normal (Gaussian) distribution (the famous bell curve)
- Mean and standard deviation of the normal distribution
- The 68-95-99.7 rule
- The binomial distribution (coin flips and yes/no outcomes)
- The Poisson distribution (counting rare events)
- How to plot distributions with Matplotlib
- How to generate random samples with NumPy
- Why the normal distribution appears everywhere (Central Limit Theorem)

## Why This Chapter Matters

In the last chapter, you learned what probability is. Now you will learn about **distributions** — the patterns that probabilities follow.

Think of it this way. If probability answers "what are the chances?", then a distribution answers "what does the full picture look like?"

Machine learning is all about data. And data follows patterns. Those patterns are distributions. When you understand distributions, you understand the language that data speaks.

Every ML model makes assumptions about how data is distributed. If you do not understand distributions, you cannot understand why models work or why they fail.

---

## 26.1 What Is a Probability Distribution?

Imagine you roll a die 6000 times. You write down every result. Then you count how many times each number appeared.

You might get something like this:

```
Number:  1     2     3     4     5     6
Count:   980   1020  1010  990   1000  1000
```

If you draw a bar chart of these counts, you get a **histogram**. That histogram shows the **shape** of your data.

A **probability distribution** tells you how likely each possible outcome is. It is the "shape" of all possible results.

```
WHAT IS A DISTRIBUTION?

Think of it like a terrain map for probabilities:

Probability
^
|     ___
|    /   \        <-- Where are values most likely?
|   /     \
|  /       \      <-- Where are values rare?
| /         \
|/___________\__> Values

The SHAPE tells the whole story!
```

There are two types of distributions:

1. **Discrete** — countable outcomes (rolling dice, flipping coins)
2. **Continuous** — any value in a range (height, temperature, weight)

Let us explore the most important ones.

---

## 26.2 The Uniform Distribution — Equal Chance for Everything

The simplest distribution. Every outcome is equally likely.

**Real-life analogy:** Rolling a fair die. Each number (1 through 6) has the same chance: 1/6.

```
UNIFORM DISTRIBUTION (Discrete — Fair Die)

Probability
^
|  ___  ___  ___  ___  ___  ___
| | 1 || 2 || 3 || 4 || 5 || 6 |   Each bar is the same height!
| |___||___||___||___||___||___|
| 1/6  1/6  1/6  1/6  1/6  1/6
+--------------------------------> Outcome
```

There is also a **continuous** uniform distribution. Imagine picking a random number between 0 and 1. Any number is equally likely.

### Computing with Python

```python
import numpy as np
import matplotlib.pyplot as plt

# Generate 10000 random numbers from a uniform distribution (0 to 1)
samples = np.random.uniform(low=0, high=1, size=10000)

# Check the mean — should be close to 0.5 (middle of 0 and 1)
print(f"Mean: {np.mean(samples):.4f}")
print(f"Min:  {np.min(samples):.4f}")
print(f"Max:  {np.max(samples):.4f}")

# Plot the histogram
plt.figure(figsize=(8, 4))
plt.hist(samples, bins=50, edgecolor='black', alpha=0.7, color='skyblue')
plt.title('Uniform Distribution (10,000 samples)')
plt.xlabel('Value')
plt.ylabel('Count')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('uniform_distribution.png', dpi=100)
plt.show()
```

**Expected output:**
```
Mean: 0.4998
Min:  0.0001
Max:  0.9999
```

**Line-by-line explanation:**
- `np.random.uniform(low=0, high=1, size=10000)` — generate 10,000 random numbers between 0 and 1, each equally likely
- `np.mean(samples)` — the average should be near 0.5 (the center of the range)
- `plt.hist(samples, bins=50, ...)` — draw a histogram with 50 bars; they should all be roughly the same height

The histogram looks nearly flat. That is what "uniform" means — no value is more likely than another.

---

## 26.3 The Normal (Gaussian) Distribution — The Bell Curve

This is the **most important distribution in all of statistics and machine learning**.

**Real-life analogy:** Measure the height of 10,000 adults. Most people are near average height. Very few are extremely tall or extremely short. The data forms a bell shape.

```
THE BELL CURVE (Normal Distribution)

Probability
^
|           *
|          * *
|         *   *
|        *     *
|       *       *
|     *           *
|   *               *
| *                   *
|*_____________________*___> Value
        |     |     |
       -1s   mean  +1s

s = standard deviation

Most data clusters around the mean.
The tails stretch out but never touch zero.
```

The normal distribution is defined by two numbers:

1. **Mean (mu)** — the center of the bell
2. **Standard deviation (sigma)** — how wide the bell is

```
NARROW vs WIDE BELL CURVES

Narrow (small sigma)         Wide (large sigma)

      *                          *
     * *                       *   *
    *   *                    *       *
   *     *                 *           *
 *         *             *               *
*___________*          *___________________*

Data is tightly packed       Data is spread out
around the mean              around the mean
```

### Computing with Python

```python
import numpy as np
import matplotlib.pyplot as plt

# Generate samples from a normal distribution
# mean = 0, standard deviation = 1 (this is the "standard normal")
samples = np.random.normal(loc=0, scale=1, size=10000)

print(f"Mean: {np.mean(samples):.4f}")
print(f"Std Dev: {np.std(samples):.4f}")
print(f"Min: {np.min(samples):.4f}")
print(f"Max: {np.max(samples):.4f}")

# Plot the histogram
plt.figure(figsize=(8, 4))
plt.hist(samples, bins=50, edgecolor='black', alpha=0.7,
         color='salmon', density=True)
plt.title('Normal Distribution (mean=0, std=1)')
plt.xlabel('Value')
plt.ylabel('Probability Density')
plt.axvline(x=0, color='red', linestyle='--', label='Mean')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('normal_distribution.png', dpi=100)
plt.show()
```

**Expected output:**
```
Mean: -0.0012
Std Dev: 0.9987
Min: -3.8521
Max: 3.7645
```

**Line-by-line explanation:**
- `np.random.normal(loc=0, scale=1, size=10000)` — generate 10,000 samples from a normal distribution with mean=0 and standard deviation=1
- `density=True` — normalize the histogram so the y-axis shows probability density, not raw counts
- `plt.axvline(x=0, ...)` — draw a vertical dashed line at the mean

---

## 26.4 The 68-95-99.7 Rule

This is one of the most useful rules in statistics. It tells you how data spreads around the mean in a normal distribution.

```
THE 68-95-99.7 RULE

|<-------------- 99.7% ------------->|
|    |<-------- 95% -------->|       |
|    |   |<--- 68% --->|    |       |
|    |   |              |    |       |
|    |   |     ****     |    |       |
|    |   |   **    **   |    |       |
|    |   |  *        *  |    |       |
|    |   | *          * |    |       |
|    |  *|              |*   |       |
|    |*  |              |  * |       |
|___*|___|______________|____|*______|
   -3s  -2s   -1s  mean +1s  +2s   +3s

s = standard deviation
```

- **68%** of data falls within 1 standard deviation of the mean
- **95%** of data falls within 2 standard deviations of the mean
- **99.7%** of data falls within 3 standard deviations of the mean

**Real-life example:** If average adult male height is 175 cm with a standard deviation of 7 cm:
- 68% of men are between 168 and 182 cm
- 95% of men are between 161 and 189 cm
- 99.7% of men are between 154 and 196 cm

### Verifying with Python

```python
import numpy as np

# Generate a large sample from a normal distribution
np.random.seed(42)
data = np.random.normal(loc=175, scale=7, size=100000)

mean = np.mean(data)
std = np.std(data)

# Count what percentage falls within 1, 2, and 3 standard deviations
within_1_std = np.sum((data >= mean - std) & (data <= mean + std)) / len(data) * 100
within_2_std = np.sum((data >= mean - 2*std) & (data <= mean + 2*std)) / len(data) * 100
within_3_std = np.sum((data >= mean - 3*std) & (data <= mean + 3*std)) / len(data) * 100

print(f"Mean: {mean:.2f} cm")
print(f"Std Dev: {std:.2f} cm")
print()
print(f"Within 1 std dev ({mean-std:.1f} to {mean+std:.1f}): {within_1_std:.1f}%")
print(f"Within 2 std dev ({mean-2*std:.1f} to {mean+2*std:.1f}): {within_2_std:.1f}%")
print(f"Within 3 std dev ({mean-3*std:.1f} to {mean+3*std:.1f}): {within_3_std:.1f}%")
```

**Expected output:**
```
Mean: 175.02 cm
Std Dev: 7.01 cm

Within 1 std dev (168.0 to 182.0): 68.2%
Within 2 std dev (161.0 to 189.0): 95.5%
Within 3 std dev (154.0 to 196.1): 99.7%
```

**Line-by-line explanation:**
- `np.random.seed(42)` — make the random numbers reproducible
- `np.random.normal(loc=175, scale=7, size=100000)` — generate 100,000 heights with mean 175 and std 7
- The `&` operator combines two conditions (greater than lower bound AND less than upper bound)
- The percentages match the 68-95-99.7 rule almost exactly

---

## 26.5 The Binomial Distribution — Coin Flips

The binomial distribution models situations with exactly **two outcomes**: success or failure.

**Real-life analogies:**
- Flipping a coin (heads or tails)
- An email is spam or not spam
- A patient is sick or healthy
- A customer buys or does not buy

It answers: "If I flip a coin 10 times, how many heads will I get?"

```
BINOMIAL DISTRIBUTION: 10 coin flips

Probability
^
|              *
|            *   *
|          *       *
|        *           *
|      *               *
|    *                   *
|  *                       *
|*___________________________*
  0  1  2  3  4  5  6  7  8  9  10
          Number of heads

Most likely outcome: 5 heads (half of 10 flips)
Getting 0 or 10 heads is very rare!
```

The binomial distribution needs two parameters:
- **n** — number of trials (how many coin flips)
- **p** — probability of success on each trial (0.5 for a fair coin)

### Computing with Python

```python
import numpy as np
import matplotlib.pyplot as plt

# Simulate flipping a coin 10 times, repeated 10000 times
n_flips = 10      # number of flips per experiment
p_heads = 0.5     # probability of heads
n_experiments = 10000

results = np.random.binomial(n=n_flips, p=p_heads, size=n_experiments)

print(f"Average number of heads: {np.mean(results):.2f}")
print(f"Most common result: {np.bincount(results).argmax()} heads")
print(f"Std Dev: {np.std(results):.2f}")

# Plot the distribution
plt.figure(figsize=(8, 4))
plt.hist(results, bins=range(12), edgecolor='black', alpha=0.7,
         color='lightgreen', align='left')
plt.title('Binomial Distribution: 10 Coin Flips (10,000 experiments)')
plt.xlabel('Number of Heads')
plt.ylabel('Count')
plt.xticks(range(11))
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('binomial_distribution.png', dpi=100)
plt.show()
```

**Expected output:**
```
Average number of heads: 5.01
Most common result: 5 heads
Std Dev: 1.58
```

**Line-by-line explanation:**
- `np.random.binomial(n=10, p=0.5, size=10000)` — simulate 10,000 experiments, each flipping a coin 10 times
- `np.bincount(results).argmax()` — count how often each result appears, then find the most common one
- The histogram is bell-shaped and centered at 5 (half of 10 flips)

### Unfair Coins

What if the coin is biased? Say 70% chance of heads.

```python
import numpy as np

# Unfair coin: 70% chance of heads
results_unfair = np.random.binomial(n=10, p=0.7, size=10000)

print(f"Average heads (unfair coin): {np.mean(results_unfair):.2f}")
print(f"Expected: {10 * 0.7:.1f}")
```

**Expected output:**
```
Average heads (unfair coin): 7.00
Expected: 7.0
```

The average shifts. With p=0.7, you expect 7 heads out of 10 flips.

---

## 26.6 The Poisson Distribution — Counting Events

The Poisson distribution counts how many times something happens in a fixed period when events are rare and random.

**Real-life analogies:**
- How many customers arrive at a store per hour?
- How many emails do you receive per day?
- How many typos are on a page?
- How many server crashes happen per month?

It has one parameter:
- **lambda** — the average number of events per time period

```
POISSON DISTRIBUTION (lambda = 3)

Probability
^
|      *
|    *   *
|   *     *
|  *       *
| *         *
|*           *  *
|              *  *
|                  *  *  *
+----------------------------> Events
  0  1  2  3  4  5  6  7  8

Peak is at lambda = 3
Skewed to the right (long tail)
```

### Computing with Python

```python
import numpy as np
import matplotlib.pyplot as plt

# A store gets an average of 4 customers per hour
# Simulate 10000 hours
lam = 4  # lambda (average events per hour)
samples = np.random.poisson(lam=lam, size=10000)

print(f"Average customers per hour: {np.mean(samples):.2f}")
print(f"Max in one hour: {np.max(samples)}")
print(f"Min in one hour: {np.min(samples)}")

# What fraction of hours had zero customers?
zero_hours = np.sum(samples == 0) / len(samples) * 100
print(f"Hours with zero customers: {zero_hours:.1f}%")

# Plot
plt.figure(figsize=(8, 4))
plt.hist(samples, bins=range(max(samples)+2), edgecolor='black',
         alpha=0.7, color='plum', align='left')
plt.title('Poisson Distribution (lambda=4): Customers per Hour')
plt.xlabel('Number of Customers')
plt.ylabel('Count')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('poisson_distribution.png', dpi=100)
plt.show()
```

**Expected output:**
```
Average customers per hour: 4.01
Max in one hour: 14
Min in one hour: 0
Hours with zero customers: 1.8%
```

**Line-by-line explanation:**
- `np.random.poisson(lam=4, size=10000)` — simulate 10,000 hours where the average is 4 customers per hour
- Some hours have 0 customers, some have 10+, but most have around 3-5
- The distribution is not symmetric — it has a long tail to the right

---

## 26.7 Plotting Multiple Distributions Together

Let us compare all four distributions side by side.

```python
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)
fig, axes = plt.subplots(2, 2, figsize=(12, 8))

# 1. Uniform
uniform_data = np.random.uniform(0, 10, size=10000)
axes[0, 0].hist(uniform_data, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
axes[0, 0].set_title('Uniform Distribution')
axes[0, 0].set_xlabel('Value')

# 2. Normal
normal_data = np.random.normal(loc=5, scale=1.5, size=10000)
axes[0, 1].hist(normal_data, bins=50, color='salmon', edgecolor='black', alpha=0.7)
axes[0, 1].set_title('Normal Distribution')
axes[0, 1].set_xlabel('Value')

# 3. Binomial
binomial_data = np.random.binomial(n=20, p=0.5, size=10000)
axes[1, 0].hist(binomial_data, bins=range(22), color='lightgreen',
                edgecolor='black', alpha=0.7, align='left')
axes[1, 0].set_title('Binomial Distribution (n=20, p=0.5)')
axes[1, 0].set_xlabel('Successes')

# 4. Poisson
poisson_data = np.random.poisson(lam=5, size=10000)
axes[1, 1].hist(poisson_data, bins=range(max(poisson_data)+2), color='plum',
                edgecolor='black', alpha=0.7, align='left')
axes[1, 1].set_title('Poisson Distribution (lambda=5)')
axes[1, 1].set_xlabel('Events')

for ax in axes.flat:
    ax.set_ylabel('Count')
    ax.grid(True, alpha=0.3)

plt.suptitle('Four Common Probability Distributions', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('four_distributions.png', dpi=100)
plt.show()
```

```
DISTRIBUTION COMPARISON

Uniform:    [____________]     Flat — all values equally likely
Normal:     [____/\____]       Bell-shaped — most values near center
Binomial:   [___/\___]         Bell-shaped (discrete) — counting successes
Poisson:    [__/\____]         Skewed right — counting rare events
```

---

## 26.8 Generating Random Samples with NumPy

NumPy makes it easy to generate random data from any distribution. Here is a quick reference.

```python
import numpy as np

np.random.seed(0)

# Uniform: random numbers between a and b
uniform = np.random.uniform(low=0, high=100, size=5)
print(f"Uniform (0 to 100):    {uniform.round(1)}")

# Normal: bell curve with given mean and std
normal = np.random.normal(loc=50, scale=10, size=5)
print(f"Normal (mean=50, std=10): {normal.round(1)}")

# Binomial: number of successes in n trials
binomial = np.random.binomial(n=10, p=0.3, size=5)
print(f"Binomial (n=10, p=0.3): {binomial}")

# Poisson: number of events with average rate lambda
poisson = np.random.poisson(lam=5, size=5)
print(f"Poisson (lambda=5):     {poisson}")

# Random integers
integers = np.random.randint(low=1, high=7, size=5)  # like rolling dice
print(f"Random integers (1-6):  {integers}")
```

**Expected output:**
```
Uniform (0 to 100):    [54.9 71.5 60.3 54.5 42.4]
Normal (mean=50, std=10): [67.6 54.  59.8 62.2 41.1]
Binomial (n=10, p=0.3): [3 3 2 4 4]
Poisson (lambda=5):     [5 8 4 7 2]
Random integers (1-6):  [5 3 5 2 4]
```

```
NUMPY RANDOM CHEAT SHEET

+----------------------------------+---------------------------+
| Function                         | What It Generates         |
+----------------------------------+---------------------------+
| np.random.uniform(a, b, n)       | n numbers between a and b |
| np.random.normal(mean, std, n)   | n numbers from bell curve |
| np.random.binomial(trials, p, n) | n success counts          |
| np.random.poisson(rate, n)       | n event counts            |
| np.random.randint(a, b, n)       | n integers from a to b-1  |
| np.random.seed(number)           | Make results reproducible |
+----------------------------------+---------------------------+
```

---

## 26.9 Why the Normal Distribution Appears Everywhere

Here is one of the most amazing facts in statistics: **the Central Limit Theorem (CLT)**.

It says:

> If you take the average of many random numbers, the result will follow a normal distribution — **no matter what distribution the original numbers came from**.

This is why the bell curve appears everywhere in nature and in data.

**Real-life analogy:** Imagine you roll a single die. The result is uniform (1-6, each equally likely). But if you roll 30 dice and take the average, that average will be close to 3.5 almost every time. Repeat this experiment thousands of times, and the averages form a perfect bell curve.

### Seeing the CLT in Action

```python
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

# Step 1: Roll a single die many times — uniform, NOT bell-shaped
single_rolls = np.random.randint(1, 7, size=10000)

# Step 2: Roll 30 dice and take the average — repeat 10000 times
averages_of_30 = [np.mean(np.random.randint(1, 7, size=30)) for _ in range(10000)]

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# Left plot: single die rolls (uniform)
axes[0].hist(single_rolls, bins=range(1, 8), edgecolor='black',
             alpha=0.7, color='skyblue', align='left')
axes[0].set_title('Single Die Rolls (Uniform)')
axes[0].set_xlabel('Value')
axes[0].set_ylabel('Count')

# Right plot: averages of 30 dice (bell curve!)
axes[1].hist(averages_of_30, bins=50, edgecolor='black',
             alpha=0.7, color='salmon')
axes[1].set_title('Average of 30 Dice Rolls (Normal!)')
axes[1].set_xlabel('Average Value')
axes[1].set_ylabel('Count')

for ax in axes:
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('central_limit_theorem.png', dpi=100)
plt.show()

print(f"Mean of single rolls: {np.mean(single_rolls):.2f}")
print(f"Mean of averages: {np.mean(averages_of_30):.4f}")
print(f"Std of averages: {np.std(averages_of_30):.4f}")
```

**Expected output:**
```
Mean of single rolls: 3.49
Mean of averages: 3.5012
Std of averages: 0.3114
```

```
THE CENTRAL LIMIT THEOREM

Start with ANY distribution:

Uniform:  [______]    Skewed:  [/____]    Bimodal:  [__/\__/\__]

Take many samples, compute their averages:

               *
              * *
             *   *          ALL become
            *     *         BELL-SHAPED!
          *         *
        *             *
    *                     *

This is why the normal distribution
is the "default" distribution in ML!
```

### Why the CLT Matters for Machine Learning

- When you train a model on batches of data, the batch averages follow a normal distribution
- Many statistical tests assume normality — the CLT is the reason this assumption often works
- Errors in ML models tend to be normally distributed
- The CLT justifies using the normal distribution as a default assumption

---

## Common Mistakes

1. **Confusing a distribution with a single probability.** A distribution describes ALL possible outcomes, not just one.

2. **Thinking normal means "typical."** Normal distribution is a specific mathematical shape. Not all data is normally distributed.

3. **Forgetting to set the random seed.** Without `np.random.seed()`, your results will be different every time you run the code.

4. **Mixing up parameters.** For normal: `loc` is mean, `scale` is std. For uniform: `low` and `high` are the boundaries.

5. **Assuming all data is normally distributed.** Income, house prices, and many real-world datasets are skewed, not normal.

---

## Best Practices

1. **Always visualize your data first.** Plot a histogram before assuming any distribution.

2. **Use `density=True` in histograms** when comparing distributions with different sample sizes.

3. **Set a random seed** for reproducible results: `np.random.seed(42)`.

4. **Start with the normal distribution** — it is the most common in ML, and the CLT tells us why.

5. **Know which distribution fits your problem:**
   - Two outcomes? Use **binomial**.
   - Counting events? Use **Poisson**.
   - Equal chance? Use **uniform**.
   - Everything else? Start with **normal**.

---

## Quick Summary

```
CHAPTER 26 SUMMARY

+-------------------+-------------------+------------------------+
| Distribution      | Use When          | Key Parameters         |
+-------------------+-------------------+------------------------+
| Uniform           | Equal chance for   | low, high              |
|                   | all outcomes       |                        |
+-------------------+-------------------+------------------------+
| Normal (Gaussian) | Data clusters      | mean (loc),            |
|                   | around a center    | std dev (scale)        |
+-------------------+-------------------+------------------------+
| Binomial          | Counting successes | n (trials),            |
|                   | in yes/no trials   | p (probability)        |
+-------------------+-------------------+------------------------+
| Poisson           | Counting rare      | lambda (average rate)  |
|                   | events in time     |                        |
+-------------------+-------------------+------------------------+

The 68-95-99.7 Rule:
  68% of data is within 1 std dev of the mean
  95% of data is within 2 std devs of the mean
  99.7% of data is within 3 std devs of the mean

Central Limit Theorem:
  Averages of ANY distribution become normally distributed!
```

---

## Key Points to Remember

1. A **distribution** is the shape of all possible outcomes and their probabilities.
2. The **uniform** distribution means every outcome is equally likely.
3. The **normal (Gaussian)** distribution is bell-shaped, defined by mean and standard deviation.
4. The **68-95-99.7 rule** tells you how data spreads in a normal distribution.
5. The **binomial** distribution counts successes in a fixed number of yes/no trials.
6. The **Poisson** distribution counts how many events happen in a fixed time period.
7. The **Central Limit Theorem** says averages of any distribution become normal — this is why the bell curve appears everywhere.
8. NumPy's `np.random` module lets you generate samples from any distribution.

---

## Practice Questions

1. You measure the weight of 1000 apples. The mean is 200g and the standard deviation is 15g. Using the 68-95-99.7 rule, what range contains 95% of the apples?

2. A website gets an average of 3 errors per day. Which distribution would you use to model the number of errors on a given day? What is the parameter?

3. You flip a coin 20 times. What distribution describes the number of heads? What are the parameters? What is the expected number of heads?

4. Explain in your own words why the Central Limit Theorem is important for machine learning.

5. You generate 10,000 samples from `np.random.uniform(0, 100, 10000)`. What would the mean be approximately? What would the histogram look like?

---

## Exercises

### Exercise 1: Compare Normal Distributions

Generate and plot three normal distributions on the same chart:
- Mean=0, Std=1 (standard normal)
- Mean=0, Std=2 (wider)
- Mean=3, Std=1 (shifted right)

Use `plt.hist()` with `density=True` and `alpha=0.5` so all three are visible.

```python
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

# Generate three normal distributions
dist1 = np.random.normal(loc=0, scale=1, size=10000)
dist2 = np.random.normal(loc=0, scale=2, size=10000)
dist3 = np.random.normal(loc=3, scale=1, size=10000)

plt.figure(figsize=(10, 5))
plt.hist(dist1, bins=50, density=True, alpha=0.5, label='mean=0, std=1', color='blue')
plt.hist(dist2, bins=50, density=True, alpha=0.5, label='mean=0, std=2', color='red')
plt.hist(dist3, bins=50, density=True, alpha=0.5, label='mean=3, std=1', color='green')
plt.title('Comparing Normal Distributions')
plt.xlabel('Value')
plt.ylabel('Density')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('compare_normals.png', dpi=100)
plt.show()
```

### Exercise 2: Simulate a Real Scenario

A factory produces light bulbs. Each bulb has a 5% chance of being defective. A box contains 100 bulbs. Simulate opening 10,000 boxes and counting the defective bulbs in each.

```python
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

# Each box: 100 bulbs, 5% defective rate
defective_counts = np.random.binomial(n=100, p=0.05, size=10000)

print(f"Average defective per box: {np.mean(defective_counts):.2f}")
print(f"Expected: {100 * 0.05:.1f}")
print(f"Max defective in one box: {np.max(defective_counts)}")
print(f"Boxes with zero defective: {np.sum(defective_counts == 0)}")

plt.figure(figsize=(8, 4))
plt.hist(defective_counts, bins=range(max(defective_counts)+2),
         edgecolor='black', alpha=0.7, color='orange', align='left')
plt.title('Defective Bulbs per Box (n=100, p=0.05)')
plt.xlabel('Number of Defective Bulbs')
plt.ylabel('Count (out of 10,000 boxes)')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('defective_bulbs.png', dpi=100)
plt.show()
```

### Exercise 3: Prove the Central Limit Theorem

Take an exponential distribution (very skewed, not bell-shaped at all). Show that the average of 50 samples becomes normally distributed.

```python
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

# Single samples from exponential distribution (very skewed)
single_samples = np.random.exponential(scale=2.0, size=10000)

# Averages of 50 exponential samples (should become normal!)
averages = [np.mean(np.random.exponential(scale=2.0, size=50)) for _ in range(10000)]

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

axes[0].hist(single_samples, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
axes[0].set_title('Exponential Distribution (Skewed!)')
axes[0].set_xlabel('Value')

axes[1].hist(averages, bins=50, color='salmon', edgecolor='black', alpha=0.7)
axes[1].set_title('Average of 50 Exponential Samples (Normal!)')
axes[1].set_xlabel('Average Value')

for ax in axes:
    ax.set_ylabel('Count')
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('clt_exponential.png', dpi=100)
plt.show()

print(f"Skewness of single samples: {float(np.mean((single_samples - np.mean(single_samples))**3) / np.std(single_samples)**3):.2f}")
print(f"Skewness of averages: {float(np.mean((np.array(averages) - np.mean(averages))**3) / np.std(averages)**3):.2f}")
```

---

## What Is Next?

You now know the shapes that data can take. In the next chapter, you will learn **descriptive statistics** — the tools for summarizing data with numbers. You will learn about mean, median, mode, variance, and how to use Python to compute them all instantly.

Distributions tell you the shape. Descriptive stats give you the numbers. Together, they give you a complete picture of any dataset.
