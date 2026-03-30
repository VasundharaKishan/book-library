# Chapter 28: Inferential Statistics — Drawing Conclusions from Data

## What You Will Learn

- The difference between a population and a sample
- How sampling works and why it is powerful
- Confidence intervals (we are 95% sure the true value is between X and Y)
- Hypothesis testing (is this result real or just luck?)
- Null hypothesis and alternative hypothesis
- P-values (the probability of seeing this result by chance)
- Significance level (alpha = 0.05)
- How to run a t-test with `scipy.stats`
- Type I and Type II errors
- A complete A/B testing example

## Why This Chapter Matters

Descriptive statistics tells you about the data you have. But in the real world, you almost never have ALL the data. You have a **sample** — a small piece of the whole picture.

Inferential statistics lets you take that sample and draw conclusions about the entire population. It is how scientists, doctors, and data scientists answer questions like:

- "Does this drug actually work?"
- "Did the new website design improve sales?"
- "Is this difference real, or just random noise?"

In machine learning, you constantly compare models. You need to know: "Is Model A truly better than Model B, or did it just get lucky on this test set?" Inferential statistics gives you the tools to answer that.

---

## 28.1 Population vs Sample

A **population** is the entire group you care about. A **sample** is a smaller group taken from the population.

```
POPULATION vs SAMPLE

POPULATION (all 10 million residents of a city)
+-----------------------------------------------+
|  o o o o o o o o o o o o o o o o o o o o o o  |
|  o o o o o o o o o o o o o o o o o o o o o o  |
|  o o o o o o o o o o o o o o o o o o o o o o  |
|  o o o o o o o o o o o o o o o o o o o o o o  |
|  o o o o o o o o o o o o o o o o o o o o o o  |
+-----------------------------------------------+

SAMPLE (1000 randomly chosen residents)
+-------------+
|  * * * * *  |    We study these 1000 people
|  * * * * *  |    and draw conclusions about
|  * * * * *  |    all 10 million.
+-------------+
```

**Real-life analogy:** You do not need to eat an entire pot of soup to know if it is salty. One spoonful (a sample) tells you about the whole pot (the population). But the spoonful must be well-stirred (random).

### Why Sample?

- You cannot measure every person in a city
- You cannot test every product from a factory
- You cannot observe every customer on a website
- Sampling saves time, money, and effort

### The Key Rule: The Sample Must Be Random

If your sample is not random, your conclusions will be wrong. This is called **sampling bias**.

```
GOOD vs BAD SAMPLING

GOOD: Random sample from the whole population
  Every person has an equal chance of being selected
  --> Conclusions apply to the whole population

BAD: Surveying only people at a gym
  Only active/healthy people are included
  --> Conclusions only apply to gym-goers, not everyone
```

### Demonstrating Sampling with Python

```python
import numpy as np

np.random.seed(42)

# The "population" — all 100,000 adult heights in a city (in cm)
population = np.random.normal(loc=170, scale=10, size=100000)

# Take a random sample of 100 people
sample = np.random.choice(population, size=100, replace=False)

print("=== Population vs Sample ===")
print(f"Population size: {len(population):,}")
print(f"Sample size:     {len(sample)}")
print()
print(f"Population mean: {np.mean(population):.2f} cm")
print(f"Sample mean:     {np.mean(sample):.2f} cm")
print()
print(f"Population std:  {np.std(population):.2f} cm")
print(f"Sample std:      {np.std(sample):.2f} cm")
```

**Expected output:**
```
=== Population vs Sample ===
Population size: 100,000
Sample size:     100

Population mean: 170.03 cm
Population mean: 170.03 cm
Sample mean:     170.41 cm

Population std:  9.98 cm
Sample std:      9.46 cm
```

**Line-by-line explanation:**
- We create a "population" of 100,000 heights (normally distributed, mean=170, std=10)
- We take a random sample of just 100 people
- The sample mean (170.41) is close to the population mean (170.03) but not exact
- This difference is called **sampling error** — it is normal and expected

---

## 28.2 Confidence Intervals

A confidence interval gives you a **range** of values that likely contains the true population value.

Instead of saying "the average height is 170.41 cm," you say "we are 95% confident the true average height is between 168.5 and 172.3 cm."

```
CONFIDENCE INTERVAL

Point estimate (sample mean)
           |
           v
  [--------*--------]
  168.5   170.4   172.3

  "We are 95% confident the true population
   mean is somewhere in this range."

Wider interval = more confident, less precise
Narrow interval = less confident, more precise
```

**Real-life analogy:** If someone asks "How long is your commute?", you could say "30 minutes" (a point estimate). Or you could say "between 25 and 40 minutes" (a confidence interval). The range is less precise but more honest.

### Computing a Confidence Interval with Python

```python
import numpy as np
from scipy import stats

np.random.seed(42)

# Population (unknown in real life — we use it here for comparison)
population = np.random.normal(loc=170, scale=10, size=100000)

# Take a sample
sample = np.random.choice(population, size=100, replace=False)

# Compute the 95% confidence interval
sample_mean = np.mean(sample)
sample_std = np.std(sample, ddof=1)  # ddof=1 for sample std
n = len(sample)

# Standard error = std / sqrt(n)
standard_error = sample_std / np.sqrt(n)

# For 95% confidence, we use the t-distribution
confidence_level = 0.95
degrees_of_freedom = n - 1
t_critical = stats.t.ppf((1 + confidence_level) / 2, degrees_of_freedom)

margin_of_error = t_critical * standard_error
ci_lower = sample_mean - margin_of_error
ci_upper = sample_mean + margin_of_error

print(f"Sample mean: {sample_mean:.2f} cm")
print(f"Standard error: {standard_error:.2f} cm")
print(f"Margin of error: {margin_of_error:.2f} cm")
print(f"\n95% Confidence Interval: ({ci_lower:.2f}, {ci_upper:.2f}) cm")
print(f"\nTrue population mean: {np.mean(population):.2f} cm")
print(f"Is the true mean inside our CI? {ci_lower <= np.mean(population) <= ci_upper}")
```

**Expected output:**
```
Sample mean: 170.41 cm
Standard error: 0.95 cm
Margin of error: 1.89 cm

95% Confidence Interval: (168.52, 172.30) cm

True population mean: 170.03 cm
Is the true mean inside our CI? True
```

**Line-by-line explanation:**
- `ddof=1` — use sample standard deviation (divides by n-1, not n)
- `standard_error = sample_std / np.sqrt(n)` — how much the sample mean varies from sample to sample
- `stats.t.ppf(...)` — get the critical t-value for 95% confidence
- `margin_of_error` — how far the CI extends on each side of the mean
- The true mean (170.03) falls inside our interval (168.52 to 172.30)

### Using SciPy's Built-in Method

```python
from scipy import stats
import numpy as np

np.random.seed(42)
population = np.random.normal(loc=170, scale=10, size=100000)
sample = np.random.choice(population, size=100, replace=False)

# Quick way using scipy
ci = stats.t.interval(
    confidence=0.95,
    df=len(sample) - 1,
    loc=np.mean(sample),
    scale=stats.sem(sample)  # standard error of the mean
)

print(f"95% CI: ({ci[0]:.2f}, {ci[1]:.2f}) cm")
```

**Expected output:**
```
95% CI: (168.52, 172.30) cm
```

```
HOW SAMPLE SIZE AFFECTS CONFIDENCE INTERVALS

Small sample (n=25):    [---------|----------]  Wide — less precise
Medium sample (n=100):  [----|----|]             Narrower
Large sample (n=1000):  [-|--]                   Very narrow — very precise

More data = narrower interval = more precise estimate
```

---

## 28.3 Hypothesis Testing

Hypothesis testing is a formal way to answer: "Is this result real, or could it have happened by chance?"

**Real-life analogy:** A friend claims they can predict coin flips. They get 7 out of 10 right. Is your friend psychic, or did they just get lucky? Hypothesis testing helps you decide.

### The Steps of Hypothesis Testing

```
HYPOTHESIS TESTING — THE FIVE STEPS

Step 1: State the null hypothesis (H0)
        "Nothing special is happening"
        Example: "The coin is fair (p = 0.5)"

Step 2: State the alternative hypothesis (H1)
        "Something IS happening"
        Example: "The coin is NOT fair (p != 0.5)"

Step 3: Collect data and compute a test statistic
        Run the experiment, measure the result

Step 4: Compute the p-value
        "What is the probability of seeing this result
         IF the null hypothesis is true?"

Step 5: Make a decision
        If p-value < alpha (0.05): REJECT H0 --> result is significant!
        If p-value >= alpha (0.05): FAIL TO REJECT H0 --> not enough evidence
```

### The Null and Alternative Hypothesis

```
NULL HYPOTHESIS (H0):
  "There is no effect. No difference. Nothing interesting."
  It is the boring, default assumption.

  Examples:
  - The drug has no effect
  - The new design does not change clicks
  - There is no difference between Group A and Group B

ALTERNATIVE HYPOTHESIS (H1):
  "There IS an effect. There IS a difference."
  It is what you are trying to prove.

  Examples:
  - The drug works
  - The new design increases clicks
  - Group A and Group B are different
```

---

## 28.4 P-Values — The Probability of Luck

The **p-value** answers this question: "If nothing special is happening (H0 is true), what is the probability of seeing a result this extreme?"

```
UNDERSTANDING P-VALUES

p-value = 0.03 means:
  "There is only a 3% chance of seeing this result
   if the null hypothesis is true."

  3% is pretty unlikely --> probably not luck
  --> REJECT the null hypothesis

p-value = 0.42 means:
  "There is a 42% chance of seeing this result
   if the null hypothesis is true."

  42% is very plausible --> could easily be luck
  --> FAIL TO REJECT the null hypothesis
```

```
THE SIGNIFICANCE LEVEL (alpha)

alpha = 0.05 is the standard threshold.

  p-value < 0.05  -->  "Statistically significant"
                       (unlikely to be luck)

  p-value >= 0.05 -->  "Not statistically significant"
                       (could be luck)

  Think of alpha as your "suspicion threshold."
  How unlikely does something have to be before
  you stop believing it is just random chance?
```

### A Simple Example: Is This Coin Fair?

```python
import numpy as np
from scipy import stats

np.random.seed(42)

# Flip a coin 100 times — we observe 60 heads
n_flips = 100
n_heads = 60

# Null hypothesis: the coin is fair (p = 0.5)
# Alternative: the coin is NOT fair (p != 0.5)

# Use a binomial test
p_value = stats.binomtest(n_heads, n_flips, p=0.5).pvalue

print(f"Observed: {n_heads} heads out of {n_flips} flips")
print(f"Expected if fair: {n_flips * 0.5:.0f} heads")
print(f"P-value: {p_value:.4f}")
print()

alpha = 0.05
if p_value < alpha:
    print(f"p-value ({p_value:.4f}) < alpha ({alpha})")
    print("REJECT the null hypothesis.")
    print("Conclusion: The coin is likely NOT fair.")
else:
    print(f"p-value ({p_value:.4f}) >= alpha ({alpha})")
    print("FAIL TO REJECT the null hypothesis.")
    print("Conclusion: Not enough evidence to say the coin is unfair.")
```

**Expected output:**
```
Observed: 60 heads out of 100 flips
Expected if fair: 50 heads
P-value: 0.0569

p-value (0.0569) >= alpha (0.05)
FAIL TO REJECT the null hypothesis.
Conclusion: Not enough evidence to say the coin is unfair.
```

**Line-by-line explanation:**
- `stats.binomtest(60, 100, p=0.5)` — tests whether 60 heads out of 100 flips is significantly different from a fair coin (50%)
- The p-value is 0.057, which is just barely above 0.05
- So we cannot conclude the coin is unfair — 60/100 could happen by chance with a fair coin

---

## 28.5 The T-Test — Comparing Two Groups

The **t-test** checks if the means of two groups are significantly different.

**Real-life analogy:** Two classes take the same exam. Class A averages 78 and Class B averages 82. Is Class B actually better, or is the 4-point difference just random variation?

```
T-TEST: ARE THESE TWO GROUPS DIFFERENT?

Group A: mean = 78        Group B: mean = 82

  Group A           Group B
    ___                ___
   / A \              / B \
  / 78  \            / 82  \
 /       \          /       \
/         \        /         \

Question: Is the gap between 78 and 82 real?
Or could random chance produce this difference?

t-test gives you a p-value to decide!
```

### Running a T-Test with Python

```python
import numpy as np
from scipy import stats

np.random.seed(42)

# Class A: mean=78, std=10
class_a = np.random.normal(loc=78, scale=10, size=30)

# Class B: mean=82, std=10
class_b = np.random.normal(loc=82, scale=10, size=30)

print(f"Class A mean: {np.mean(class_a):.2f}")
print(f"Class B mean: {np.mean(class_b):.2f}")
print(f"Difference: {np.mean(class_b) - np.mean(class_a):.2f}")
print()

# Run the independent samples t-test
t_statistic, p_value = stats.ttest_ind(class_a, class_b)

print(f"T-statistic: {t_statistic:.4f}")
print(f"P-value: {p_value:.4f}")
print()

alpha = 0.05
if p_value < alpha:
    print(f"p-value ({p_value:.4f}) < alpha ({alpha})")
    print("REJECT the null hypothesis.")
    print("The difference between the classes IS statistically significant.")
else:
    print(f"p-value ({p_value:.4f}) >= alpha ({alpha})")
    print("FAIL TO REJECT the null hypothesis.")
    print("The difference could be due to random chance.")
```

**Expected output:**
```
Class A mean: 79.22
Class B mean: 83.32
Difference: 4.10

T-statistic: -1.5839
P-value: 0.1186

p-value (0.1186) >= alpha (0.05)
FAIL TO REJECT the null hypothesis.
The difference could be due to random chance.
```

**Line-by-line explanation:**
- `stats.ttest_ind(class_a, class_b)` — performs an independent two-sample t-test
- The t-statistic measures how many standard errors apart the means are
- The p-value (0.1186) is greater than 0.05, so the 4-point difference is not statistically significant
- With only 30 students per class and std=10, a 4-point gap can easily happen by chance

### What If We Had More Data?

```python
import numpy as np
from scipy import stats

np.random.seed(42)

# Same means, but 300 students per class instead of 30
class_a_large = np.random.normal(loc=78, scale=10, size=300)
class_b_large = np.random.normal(loc=82, scale=10, size=300)

t_stat, p_val = stats.ttest_ind(class_a_large, class_b_large)

print(f"Class A mean: {np.mean(class_a_large):.2f}")
print(f"Class B mean: {np.mean(class_b_large):.2f}")
print(f"P-value: {p_val:.6f}")
print()

if p_val < 0.05:
    print("With more data, the difference IS significant!")
    print("More data = more statistical power to detect real differences.")
```

**Expected output:**
```
Class A mean: 78.15
Class B mean: 82.42
P-value: 0.000000

With more data, the difference IS significant!
More data = more statistical power to detect real differences.
```

---

## 28.6 Type I and Type II Errors

Even with statistics, you can make mistakes.

```
TWO TYPES OF ERRORS

                        Reality
                  Nothing happening    Something IS happening
                  (H0 is true)         (H0 is false)
                +-------------------+-------------------+
  Your          |                   |                   |
  Decision:     |   CORRECT!        |   TYPE II ERROR   |
  Fail to       |   (True Negative) |   (False Negative)|
  Reject H0     |                   |   "Missed it"     |
                +-------------------+-------------------+
  Your          |                   |                   |
  Decision:     |   TYPE I ERROR    |   CORRECT!        |
  Reject H0     |   (False Positive)|   (True Positive) |
                |   "False alarm"   |                   |
                +-------------------+-------------------+
```

**Type I Error (False Positive):**
- You say there IS an effect, but there is not.
- Like a fire alarm going off when there is no fire.
- Probability = alpha (usually 5%).

**Type II Error (False Negative):**
- You say there is NO effect, but there is one.
- Like a smoke detector that does not go off during a real fire.
- This happens when your sample is too small to detect a real effect.

```
REAL-LIFE EXAMPLES

Type I Error (False Positive):
  - Telling a healthy patient they have a disease
  - Concluding a drug works when it does not
  - Launching a new website design that is not actually better

Type II Error (False Negative):
  - Telling a sick patient they are healthy
  - Concluding a drug does not work when it does
  - Keeping the old website when the new one IS better
```

### Demonstrating Type I Errors with Python

```python
import numpy as np
from scipy import stats

np.random.seed(42)

# Simulate 1000 experiments where H0 IS true
# (both groups have the SAME mean — no real difference)
n_experiments = 1000
false_positives = 0
alpha = 0.05

for i in range(n_experiments):
    # Both groups come from the SAME distribution
    group_a = np.random.normal(loc=50, scale=10, size=30)
    group_b = np.random.normal(loc=50, scale=10, size=30)

    _, p_value = stats.ttest_ind(group_a, group_b)

    if p_value < alpha:
        false_positives += 1

false_positive_rate = false_positives / n_experiments * 100

print(f"Experiments run: {n_experiments}")
print(f"False positives (Type I errors): {false_positives}")
print(f"False positive rate: {false_positive_rate:.1f}%")
print(f"Expected rate (alpha): {alpha * 100:.1f}%")
print()
print("Even when there is NO real difference,")
print(f"about {alpha*100:.0f}% of experiments will wrongly say there IS one!")
```

**Expected output:**
```
Experiments run: 1000
False positives (Type I errors): 52
False positive rate: 5.2%
Expected rate (alpha): 5.0%

Even when there is NO real difference,
about 5% of experiments will wrongly say there IS one!
```

---

## 28.7 A/B Testing Example — Did the New Design Work?

A/B testing is how companies decide if changes to their website actually help. It is hypothesis testing applied to business.

**Scenario:** An e-commerce company redesigns their "Buy Now" button. They show the old design (Group A) to 1000 visitors and the new design (Group B) to 1000 visitors. They measure click-through rates.

```
A/B TESTING SETUP

Group A (Control):  Old "Buy Now" button
  1000 visitors --> 120 clicked (12.0% click rate)

Group B (Treatment): New "Buy Now" button
  1000 visitors --> 145 clicked (14.5% click rate)

Question: Is the 2.5% improvement real?
          Or could it be random noise?

H0: The new design has NO effect (click rates are the same)
H1: The new design DOES have an effect (click rates differ)
```

### Complete A/B Test with Python

```python
import numpy as np
from scipy import stats

# --- THE DATA ---
n_a = 1000        # visitors who saw old design
clicks_a = 120    # clicks on old design

n_b = 1000        # visitors who saw new design
clicks_b = 145    # clicks on new design

rate_a = clicks_a / n_a
rate_b = clicks_b / n_b
improvement = rate_b - rate_a

print("=== A/B TEST: Buy Now Button ===")
print(f"Group A (old design): {clicks_a}/{n_a} = {rate_a:.1%} click rate")
print(f"Group B (new design): {clicks_b}/{n_b} = {rate_b:.1%} click rate")
print(f"Improvement: {improvement:.1%}")
print()

# --- STATISTICAL TEST ---
# Use a two-proportion z-test
# (or we can use chi-squared test)
# Create a contingency table
#                Clicked   Did not click
# Group A:       120       880
# Group B:       145       855

contingency_table = np.array([
    [clicks_a, n_a - clicks_a],   # Group A
    [clicks_b, n_b - clicks_b]    # Group B
])

chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)

print(f"Chi-squared statistic: {chi2:.4f}")
print(f"P-value: {p_value:.4f}")
print()

# --- DECISION ---
alpha = 0.05
if p_value < alpha:
    print(f"p-value ({p_value:.4f}) < alpha ({alpha})")
    print("REJECT the null hypothesis!")
    print(f"The new design's {improvement:.1%} improvement is statistically significant.")
    print("RECOMMENDATION: Launch the new design.")
else:
    print(f"p-value ({p_value:.4f}) >= alpha ({alpha})")
    print("FAIL TO REJECT the null hypothesis.")
    print("The improvement could be due to random chance.")
    print("RECOMMENDATION: Keep testing or stick with the old design.")

# --- CONFIDENCE INTERVAL FOR THE DIFFERENCE ---
# Standard error for difference of proportions
se_diff = np.sqrt(rate_a * (1 - rate_a) / n_a + rate_b * (1 - rate_b) / n_b)
z_critical = stats.norm.ppf(0.975)  # for 95% CI

ci_lower = improvement - z_critical * se_diff
ci_upper = improvement + z_critical * se_diff

print(f"\n95% CI for improvement: ({ci_lower:.1%}, {ci_upper:.1%})")
```

**Expected output:**
```
=== A/B TEST: Buy Now Button ===
Group A (old design): 120/1000 = 12.0% click rate
Group B (new design): 145/1000 = 14.5% click rate
Improvement: 2.5%

Chi-squared statistic: 2.7442
P-value: 0.0976

p-value (0.0976) >= alpha (0.05)
FAIL TO REJECT the null hypothesis.
The improvement could be due to random chance.
RECOMMENDATION: Keep testing or stick with the old design.

95% CI for improvement: (-0.4%, 5.4%)
```

**Line-by-line explanation:**
- We set up a contingency table: rows are groups (A, B), columns are outcomes (clicked, did not click)
- `stats.chi2_contingency()` runs a chi-squared test to compare the proportions
- The p-value is 0.0976, which is above our threshold of 0.05
- The 2.5% improvement is NOT statistically significant — it could be random noise
- The confidence interval includes 0% (-0.4% to 5.4%), confirming the result is inconclusive
- The company should keep testing with more visitors

### What If We Had More Visitors?

```python
import numpy as np
from scipy import stats

# Same click rates, but 5000 visitors per group
n_a_large = 5000
clicks_a_large = 600   # 12.0%
n_b_large = 5000
clicks_b_large = 725   # 14.5%

contingency_large = np.array([
    [clicks_a_large, n_a_large - clicks_a_large],
    [clicks_b_large, n_b_large - clicks_b_large]
])

chi2, p_value, _, _ = stats.chi2_contingency(contingency_large)

print(f"With 5000 visitors per group:")
print(f"P-value: {p_value:.6f}")
print(f"Result: {'SIGNIFICANT!' if p_value < 0.05 else 'Not significant'}")
print()
print("More data = more power to detect real differences!")
```

**Expected output:**
```
With 5000 visitors per group:
P-value: 0.000303
Result: SIGNIFICANT!

More data = more power to detect real differences!
```

---

## 28.8 Putting It All Together — A Complete Workflow

```
INFERENTIAL STATISTICS WORKFLOW

1. Define your question
   "Does the new drug lower blood pressure?"

2. Set up hypotheses
   H0: New drug = Old drug (no difference)
   H1: New drug != Old drug (there IS a difference)

3. Collect data (random sample!)
   Measure blood pressure for both groups

4. Choose your test
   Comparing two means? --> t-test
   Comparing proportions? --> chi-squared test
   More than two groups? --> ANOVA

5. Compute the p-value
   scipy.stats does the math for you

6. Make a decision
   p < 0.05 --> Statistically significant
   p >= 0.05 --> Not enough evidence

7. Report results with confidence interval
   "The drug reduced blood pressure by 8 mmHg
    (95% CI: 3 to 13 mmHg, p = 0.002)"
```

```python
import numpy as np
from scipy import stats

np.random.seed(42)

# Complete example: Does a new study method improve test scores?
control_group = np.random.normal(loc=72, scale=10, size=50)    # traditional method
treatment_group = np.random.normal(loc=78, scale=10, size=50)  # new method

# Step 1: Descriptive statistics
print("=== STEP 1: Describe the Data ===")
print(f"Control group:   mean={np.mean(control_group):.1f}, std={np.std(control_group):.1f}, n={len(control_group)}")
print(f"Treatment group: mean={np.mean(treatment_group):.1f}, std={np.std(treatment_group):.1f}, n={len(treatment_group)}")

# Step 2: State hypotheses
print("\n=== STEP 2: Hypotheses ===")
print("H0: The new study method has NO effect (means are equal)")
print("H1: The new study method HAS an effect (means are different)")

# Step 3: Run the test
t_stat, p_value = stats.ttest_ind(control_group, treatment_group)

print(f"\n=== STEP 3: T-Test Results ===")
print(f"T-statistic: {t_stat:.4f}")
print(f"P-value: {p_value:.4f}")

# Step 4: Confidence interval for the difference
diff = np.mean(treatment_group) - np.mean(control_group)
se = np.sqrt(np.var(control_group, ddof=1)/len(control_group) +
             np.var(treatment_group, ddof=1)/len(treatment_group))
ci = stats.t.interval(0.95, df=len(control_group)+len(treatment_group)-2,
                       loc=diff, scale=se)

print(f"\n=== STEP 4: Results ===")
print(f"Mean difference: {diff:.2f} points")
print(f"95% CI: ({ci[0]:.2f}, {ci[1]:.2f})")

# Step 5: Decision
alpha = 0.05
print(f"\n=== STEP 5: Decision (alpha={alpha}) ===")
if p_value < alpha:
    print(f"p-value ({p_value:.4f}) < {alpha}")
    print("REJECT the null hypothesis.")
    print(f"The new study method improves scores by {diff:.1f} points (statistically significant).")
else:
    print(f"p-value ({p_value:.4f}) >= {alpha}")
    print("FAIL TO REJECT. Not enough evidence.")
```

**Expected output:**
```
=== STEP 1: Describe the Data ===
Control group:   mean=73.2, std=9.4, n=50
Treatment group: mean=79.3, std=10.0, n=50

=== STEP 2: Hypotheses ===
H0: The new study method has NO effect (means are equal)
H1: The new study method HAS an effect (means are different)

=== STEP 3: T-Test Results ===
T-statistic: -3.1487
P-value: 0.0022

=== STEP 4: Results ===
Mean difference: 6.15 points
95% CI: (2.27, 10.03)

=== STEP 5: Decision (alpha=0.05) ===
p-value (0.0022) < 0.05
REJECT the null hypothesis.
The new study method improves scores by 6.1 points (statistically significant).
```

---

## Common Mistakes

1. **Saying "we accept the null hypothesis."** You never "accept" it — you "fail to reject" it. The absence of evidence is not evidence of absence.

2. **Thinking p-value = probability the hypothesis is true.** The p-value is the probability of seeing your data IF the null hypothesis is true. It is not the probability that the null hypothesis is true.

3. **Ignoring sample size.** Small samples have low statistical power. A real difference might exist but go undetected because your sample was too small.

4. **Using the wrong test.** Comparing means? Use t-test. Comparing proportions? Use chi-squared. Comparing more than two groups? Use ANOVA.

5. **P-hacking.** Running many tests until you find p < 0.05 by chance. If you test 20 things, one will likely be "significant" just by random luck (5% of 20 = 1).

---

## Best Practices

1. **Decide your hypothesis and alpha BEFORE looking at the data.** Changing them after seeing results is cheating.

2. **Always report the confidence interval** along with the p-value. The CI tells you the size of the effect, not just whether it exists.

3. **Use large enough samples.** Small samples lead to unreliable conclusions. A general rule: at least 30 observations per group for a t-test.

4. **Check assumptions.** The t-test assumes roughly normal data and similar variances. Plot your data first.

5. **Remember: statistical significance does not mean practical significance.** A 0.1% improvement might be statistically significant with enough data, but it might not matter in practice.

---

## Quick Summary

```
CHAPTER 28 SUMMARY

POPULATION vs SAMPLE:
  Population = entire group of interest
  Sample = subset used for analysis
  Sample must be RANDOM

CONFIDENCE INTERVAL:
  A range that likely contains the true population value
  95% CI means: if we repeated this 100 times,
  95 of those intervals would contain the true value

HYPOTHESIS TESTING:
  H0 (null):        "Nothing is happening"
  H1 (alternative): "Something IS happening"
  p-value < 0.05:   Reject H0 (significant!)
  p-value >= 0.05:  Fail to reject H0 (not enough evidence)

P-VALUE:
  Probability of seeing your result IF H0 is true
  Small p-value = result is unlikely to be just chance

ERRORS:
  Type I  (false positive): saying there IS an effect when there is not
  Type II (false negative): missing a real effect

PYTHON TOOLS:
  stats.ttest_ind(a, b)        — compare two group means
  stats.chi2_contingency(table) — compare proportions
  stats.t.interval(...)        — confidence interval
  stats.binomtest(...)         — test a proportion
```

---

## Key Points to Remember

1. A **population** is everyone. A **sample** is a subset. Your sample must be random.
2. A **confidence interval** is a range of plausible values for the true population parameter.
3. **Hypothesis testing** formally asks: "Is this result real or just luck?"
4. The **null hypothesis (H0)** says nothing is happening. The **alternative (H1)** says something is.
5. The **p-value** is the probability of seeing your result if H0 is true. Small p-value = surprising result.
6. **Alpha = 0.05** is the standard threshold. If p < alpha, the result is "statistically significant."
7. **Type I error** = false alarm. **Type II error** = missed detection.
8. The **t-test** compares means of two groups. Use `scipy.stats.ttest_ind()`.

---

## Practice Questions

1. A company surveys 200 customers and finds that 60% prefer Product A. Calculate the 95% confidence interval for the true proportion. (Hint: use the formula for proportions.)

2. Explain the difference between a Type I error and a Type II error. Give a real-world example of each.

3. A researcher runs a t-test comparing a new fertilizer to the old one. The p-value is 0.03. What does this mean? What should the researcher conclude?

4. An A/B test shows that Design B has a 2% higher click rate than Design A, but the p-value is 0.15. Should the company switch to Design B? Explain.

5. Why is it important that a sample be random? Give an example of a biased sample that would lead to wrong conclusions.

---

## Exercises

### Exercise 1: Confidence Interval for a Mean

Take a random sample of 50 values from a normal distribution (mean=100, std=15). Compute the 95% confidence interval. Then verify that the true mean (100) falls inside the interval.

```python
import numpy as np
from scipy import stats

np.random.seed(42)

# Generate population and sample
population_mean = 100
sample = np.random.normal(loc=population_mean, scale=15, size=50)

# Compute 95% CI
ci = stats.t.interval(
    confidence=0.95,
    df=len(sample) - 1,
    loc=np.mean(sample),
    scale=stats.sem(sample)
)

print(f"Sample mean: {np.mean(sample):.2f}")
print(f"95% CI: ({ci[0]:.2f}, {ci[1]:.2f})")
print(f"True mean: {population_mean}")
print(f"True mean inside CI? {ci[0] <= population_mean <= ci[1]}")
```

### Exercise 2: Run Your Own A/B Test

Simulate an A/B test where the treatment group truly has a 3% higher conversion rate. Run the test with n=500, n=1000, and n=5000 per group. Observe how the p-value changes with sample size.

```python
import numpy as np
from scipy import stats

np.random.seed(42)

base_rate = 0.10  # 10% conversion rate
improvement = 0.03  # 3% improvement

for n in [500, 1000, 5000]:
    # Simulate conversions
    group_a = np.random.binomial(1, base_rate, size=n)
    group_b = np.random.binomial(1, base_rate + improvement, size=n)

    # Run test
    contingency = np.array([
        [group_a.sum(), n - group_a.sum()],
        [group_b.sum(), n - group_b.sum()]
    ])
    chi2, p_value, _, _ = stats.chi2_contingency(contingency)

    print(f"n={n:>5} | Rate A: {group_a.mean():.1%} | Rate B: {group_b.mean():.1%} | "
          f"p-value: {p_value:.4f} | {'Significant!' if p_value < 0.05 else 'Not significant'}")
```

### Exercise 3: Visualize Hypothesis Testing

Create a visualization showing the sampling distribution under H0, the critical region, and where your test statistic falls.

```python
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

np.random.seed(42)

# Our experiment data
control = np.random.normal(50, 10, 40)
treatment = np.random.normal(55, 10, 40)
t_stat, p_value = stats.ttest_ind(control, treatment)

# Plot the t-distribution under H0
x = np.linspace(-4, 4, 1000)
y = stats.t.pdf(x, df=78)  # df = n1 + n2 - 2

plt.figure(figsize=(10, 5))
plt.plot(x, y, 'b-', linewidth=2, label='Distribution under H0')
plt.fill_between(x, y, where=(x <= -1.96) | (x >= 1.96),
                 color='red', alpha=0.3, label='Rejection region (alpha=0.05)')
plt.axvline(x=t_stat, color='green', linestyle='--', linewidth=2,
            label=f'Our t-statistic: {t_stat:.2f}')
plt.title(f'Hypothesis Test Visualization (p-value = {p_value:.4f})')
plt.xlabel('T-statistic')
plt.ylabel('Probability Density')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('hypothesis_test_visual.png', dpi=100)
plt.show()

print(f"T-statistic: {t_stat:.4f}")
print(f"P-value: {p_value:.4f}")
print(f"Conclusion: {'Reject H0' if p_value < 0.05 else 'Fail to reject H0'}")
```

---

## What Is Next?

You now know how to draw conclusions from data. But statistics gets really powerful when you start looking at **relationships** between variables.

In the next chapter, you will learn about **correlation and regression** — how to measure whether two things are related and how to draw the best line through data points. This is where statistics directly connects to machine learning.
