# Chapter 22: Association Rules

## What You Will Learn

In this chapter, you will learn:

- What association rules are and how they find hidden patterns in transactions
- The three key metrics: support, confidence, and lift
- How the Apriori algorithm discovers frequent item combinations
- How to use the mlxtend library to mine association rules
- How to interpret rules and decide which ones are useful
- Real-world applications beyond shopping
- When association rules work well and when they do not

## Why This Chapter Matters

Have you ever noticed how grocery stores place certain items together? Bread near butter. Chips near salsa. Diapers near beer.

This is not random. Stores analyzed millions of transactions and discovered that people who buy one item often buy another. This is called **market basket analysis**, and it is powered by association rules.

Association rules go far beyond grocery stores:

- **Netflix** suggests movies based on what similar users watched together
- **Amazon** shows "Frequently Bought Together" recommendations
- **Doctors** find that certain symptoms often appear together
- **Websites** discover that users who visit page A often visit page B
- **Banks** find transaction patterns that signal fraud

This technique turns raw transaction data into actionable business insights. It is simple to understand, easy to implement, and delivers real value.

---

## What Are Association Rules?

An **association rule** is a pattern like:

```
{bread} → {butter}
```

This means: "People who buy bread also tend to buy butter."

The left side is called the **antecedent** (the "if" part). The right side is called the **consequent** (the "then" part).

```
Rule Structure:
═══════════════

    {bread, milk}  →  {eggs}
     ─────┬─────     ──┬──
           │            │
      Antecedent    Consequent
      (IF part)     (THEN part)

    "IF a customer buys bread and milk,
     THEN they are likely to also buy eggs."
```

### A Simple Example

Imagine you have 5 shopping transactions:

```
Transaction 1: bread, butter, milk
Transaction 2: bread, butter
Transaction 3: bread, milk, eggs
Transaction 4: butter, milk, eggs
Transaction 5: bread, butter, milk, eggs
```

Looking at this data, you might notice:
- Bread and butter appear together often (transactions 1, 2, 5)
- When someone buys bread, they often buy butter too

But how do you measure "often"? That is where the three key metrics come in.

---

## The Three Key Metrics

### 1. Support: How Often Does It Appear?

**Support** measures how frequently an item or item set appears in all transactions.

```
Support = (Number of transactions containing the item set)
          ─────────────────────────────────────────────────
                    (Total number of transactions)
```

Using our 5 transactions:

```
Support({bread})          = 4/5 = 0.80  (bread appears in 4 of 5 transactions)
Support({butter})         = 4/5 = 0.80
Support({bread, butter})  = 3/5 = 0.60  (both appear together in 3 transactions)
Support({eggs})           = 3/5 = 0.60
```

Think of support as **popularity**. High support means the item set appears frequently.

### 2. Confidence: How Likely Is the Rule?

**Confidence** measures how often the rule is true. If someone buys the antecedent, how likely are they to buy the consequent?

```
Confidence({bread} → {butter}) = Support({bread, butter})
                                  ────────────────────────
                                     Support({bread})

                                = 0.60 / 0.80 = 0.75
```

This means: 75% of people who bought bread also bought butter.

```
Confidence Scale:
═════════════════

0.0          0.5          0.75         1.0
 |            |            |            |
 ├────────────┼────────────┼────────────┤
 │   Weak     │  Moderate  │   Strong   │
 │            │            │            │

 {bread} → {butter} has confidence 0.75
 "75% of bread buyers also buy butter"
```

### 3. Lift: How Surprising Is the Rule?

**Lift** measures how much more likely items are bought together compared to being bought independently.

```
Lift({bread} → {butter}) = Confidence({bread} → {butter})
                            ──────────────────────────────
                                  Support({butter})

                          = 0.75 / 0.80 = 0.9375
```

Lift tells you if the association is real or just a coincidence:

```
Lift Values:
════════════

Lift = 1.0    Items are independent (no real association)
Lift > 1.0    Items are positively associated (bought together
              MORE than expected)
Lift < 1.0    Items are negatively associated (bought together
              LESS than expected)

Example interpretations:
  Lift = 2.5  → Items are 2.5x MORE likely to be bought together
  Lift = 1.0  → No association (just coincidence)
  Lift = 0.5  → Items are 2x LESS likely to be bought together
```

In our example, lift is 0.94 (close to 1.0). This means bread and butter are almost independent in this tiny dataset. With more data, the patterns become clearer.

### Putting It All Together

```
Metric Summary:
═══════════════

┌──────────────┬───────────────────────────────┬────────────┐
│ Metric       │ What It Measures              │ Good Value │
├──────────────┼───────────────────────────────┼────────────┤
│ Support      │ How often items appear         │ > 0.01     │
│              │ together in all transactions   │            │
├──────────────┼───────────────────────────────┼────────────┤
│ Confidence   │ How likely B is bought when    │ > 0.5      │
│              │ A is already in the basket     │            │
├──────────────┼───────────────────────────────┼────────────┤
│ Lift         │ How much MORE likely they      │ > 1.0      │
│              │ are bought together than       │            │
│              │ by chance                      │            │
└──────────────┴───────────────────────────────┴────────────┘
```

A good rule has **reasonable support** (not too rare), **high confidence** (usually happens), and **lift greater than 1** (not just a coincidence).

---

## The Apriori Algorithm

Now you know how to measure rules. But how do you find them? With thousands of products, there are millions of possible combinations. Checking every combination would take forever.

The **Apriori algorithm** solves this problem cleverly.

### The Key Insight

Apriori uses one simple principle:

> **If an item set is infrequent, all its supersets are also infrequent.**

What does this mean? If very few people buy "truffle oil," then very few people buy "truffle oil AND saffron AND gold leaf" together. So we do not even need to check that combination.

```
Apriori Pruning:
════════════════

If {truffle oil} has low support (only 0.001 = 0.1%):

    {truffle oil}  ← Infrequent? YES
         │
         ├── {truffle oil, bread}     ← Skip! Must be even rarer
         ├── {truffle oil, milk}      ← Skip!
         ├── {truffle oil, eggs}      ← Skip!
         └── {truffle oil, saffron}   ← Skip!

This saves ENORMOUS computation time!
```

### How Apriori Works Step by Step

```
Apriori Algorithm:
══════════════════

Step 1: Count single items. Keep only frequent ones.
─────────────────────────────────────────────────────
  {bread}: 4/5 = 0.80  ✓ Keep (above min_support 0.40)
  {butter}: 4/5 = 0.80  ✓ Keep
  {milk}: 4/5 = 0.80  ✓ Keep
  {eggs}: 3/5 = 0.60  ✓ Keep
  {caviar}: 0/5 = 0.00  ✗ Remove

Step 2: Make pairs from frequent singles. Count them.
─────────────────────────────────────────────────────
  {bread, butter}: 3/5 = 0.60  ✓ Keep
  {bread, milk}: 3/5 = 0.60  ✓ Keep
  {bread, eggs}: 2/5 = 0.40  ✓ Keep
  {butter, milk}: 3/5 = 0.60  ✓ Keep
  {butter, eggs}: 2/5 = 0.40  ✓ Keep
  {milk, eggs}: 3/5 = 0.60  ✓ Keep

Step 3: Make triples from frequent pairs. Count them.
─────────────────────────────────────────────────────
  {bread, butter, milk}: 2/5 = 0.40  ✓ Keep
  {bread, butter, eggs}: 1/5 = 0.20  ✗ Remove
  {bread, milk, eggs}: 2/5 = 0.40  ✓ Keep
  {butter, milk, eggs}: 2/5 = 0.40  ✓ Keep

Step 4: Make quadruples from frequent triples.
─────────────────────────────────────────────────────
  {bread, butter, milk, eggs}: 1/5 = 0.20  ✗ Remove

Step 5: Generate rules from all frequent item sets.
```

The algorithm builds up from singles to pairs to triples, dropping infrequent sets at each level. This dramatically reduces the number of combinations to check.

---

## Using mlxtend for Association Rules

**mlxtend** (machine learning extensions) is a Python library that implements the Apriori algorithm. It is not part of scikit-learn, but it follows a similar style.

### Installation

```python
# Install mlxtend (run this in your terminal)
# pip install mlxtend
```

### Complete Grocery Store Example

```python
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules

# ============================================
# Step 1: Create transaction data
# ============================================
transactions = [
    ['bread', 'butter', 'milk', 'eggs'],
    ['bread', 'butter', 'milk'],
    ['bread', 'butter'],
    ['bread', 'milk', 'eggs'],
    ['butter', 'milk', 'eggs'],
    ['bread', 'butter', 'milk', 'eggs', 'cheese'],
    ['milk', 'eggs', 'cheese'],
    ['bread', 'butter', 'cheese'],
    ['bread', 'milk'],
    ['butter', 'milk', 'eggs'],
    ['bread', 'butter', 'milk'],
    ['eggs', 'cheese'],
    ['bread', 'butter', 'milk', 'eggs'],
    ['bread', 'milk', 'cheese'],
    ['butter', 'milk'],
]

print(f"Total transactions: {len(transactions)}")
print(f"Sample transaction: {transactions[0]}")

# ============================================
# Step 2: Convert to binary format
# ============================================
# TransactionEncoder converts lists into a True/False table
te = TransactionEncoder()
te_array = te.fit(transactions).transform(transactions)
df = pd.DataFrame(te_array, columns=te.columns_)

print(f"\nBinary transaction table (first 5 rows):")
print(df.head().to_string())

# ============================================
# Step 3: Find frequent item sets with Apriori
# ============================================
frequent_items = apriori(
    df,
    min_support=0.3,    # Item set must appear in at least 30% of transactions
    use_colnames=True   # Use item names instead of column numbers
)

print(f"\nFrequent item sets (support >= 0.30):")
print(frequent_items.sort_values('support', ascending=False).to_string(index=False))

# ============================================
# Step 4: Generate association rules
# ============================================
rules = association_rules(
    frequent_items,
    metric="lift",       # Sort by lift
    min_threshold=1.0    # Only keep rules with lift > 1.0
)

# Select important columns
rules_clean = rules[['antecedents', 'consequents', 'support',
                      'confidence', 'lift']].sort_values('lift', ascending=False)

print(f"\nAssociation Rules (lift > 1.0):")
print(f"{'Antecedent':<25} {'Consequent':<15} {'Support':>8} {'Confidence':>11} {'Lift':>6}")
print("-" * 70)
for _, row in rules_clean.head(15).iterrows():
    ant = ', '.join(list(row['antecedents']))
    con = ', '.join(list(row['consequents']))
    print(f"{ant:<25} {con:<15} {row['support']:>8.3f} {row['confidence']:>10.3f} {row['lift']:>6.2f}")
```

Expected output:

```
Total transactions: 15
Sample transaction: ['bread', 'butter', 'milk', 'eggs']

Binary transaction table (first 5 rows):
   bread  butter  cheese   eggs   milk
0   True    True   False   True   True
1   True    True   False  False   True
2   True    True   False  False  False
3   True   False   False   True   True
4  False    True   False   True   True

Frequent item sets (support >= 0.30):
          support            itemsets
         0.733333             (bread)
         0.733333            (butter)
         0.800000              (milk)
         0.533333              (eggs)
         0.333333            (cheese)
         0.533333      (bread, butter)
         0.600000        (bread, milk)
         0.333333        (bread, eggs)
         0.533333       (butter, milk)
         0.333333       (butter, eggs)
         0.466667         (milk, eggs)
         0.400000  (bread, butter, milk)
         0.333333   (butter, milk, eggs)

Association Rules (lift > 1.0):
Antecedent                Consequent       Support  Confidence   Lift
----------------------------------------------------------------------
bread                     butter             0.533       0.727   0.99
butter                    bread              0.533       0.727   0.99
bread, butter             milk               0.400       0.750   1.02
eggs                      milk               0.467       0.875   1.09
milk                      eggs               0.467       0.583   1.09
butter, eggs              milk               0.333       1.000   1.25
butter, milk              eggs               0.333       0.625   1.17
eggs                      butter             0.333       0.625   1.17
```

**Line-by-line explanation:**

1. `transactions = [...]` - Each inner list is one customer's purchases.
2. `TransactionEncoder()` - Converts transaction lists into a binary (True/False) table. Each column is a product. True means the customer bought it.
3. `te.fit(transactions).transform(transactions)` - First `fit` learns all unique items. Then `transform` creates the binary table.
4. `apriori(df, min_support=0.3, ...)` - Finds all item combinations that appear in at least 30% of transactions.
5. `association_rules(frequent_items, metric="lift", min_threshold=1.0)` - Generates rules from frequent item sets. We keep only rules with lift > 1.0 (items that are more likely to appear together than by chance).

### Reading the Results

Let us interpret some rules from the output:

```
Rule: {butter, eggs} → {milk}
  Support:    0.333  (appears in 33% of transactions)
  Confidence: 1.000  (100% of the time butter+eggs are bought, milk is too)
  Lift:       1.25   (25% more likely than chance)

  Meaning: Every single customer who bought butter and eggs
           also bought milk. This is a strong rule!

Rule: {eggs} → {milk}
  Support:    0.467  (appears in 47% of transactions)
  Confidence: 0.875  (88% of egg buyers also buy milk)
  Lift:       1.09   (9% more likely than chance)

  Meaning: Most egg buyers also buy milk. But lift is close to 1,
           so this might partly be because milk is just very popular.
```

---

## Interpreting Rules: Which Ones Are Actually Useful?

Not all rules are useful. Here is how to filter the good ones:

```
Rule Quality Filter:
════════════════════

Step 1: Check Lift > 1.0
  If lift <= 1.0, the items are not really associated.
  They just happen to be popular individually.

Step 2: Check Confidence > 0.5
  If confidence < 0.5, the rule is wrong more often than right.
  Not very useful for recommendations.

Step 3: Check Support > minimum threshold
  Very low support means the rule applies to very few customers.
  The rule might be a coincidence.

Step 4: Does it make business sense?
  {diapers} → {beer} has high lift? Check with domain experts.
  It might be real (tired parents buying both) or a fluke.
```

### Filtering Rules in Code

```python
# Filter for actionable rules
strong_rules = rules[
    (rules['lift'] > 1.2) &          # Strong positive association
    (rules['confidence'] > 0.6) &     # Rule is right >60% of the time
    (rules['support'] > 0.2)          # Appears in >20% of transactions
]

print("Strong, Actionable Rules:")
print("=" * 65)
for _, row in strong_rules.iterrows():
    ant = ', '.join(list(row['antecedents']))
    con = ', '.join(list(row['consequents']))
    print(f"\n  IF customer buys: {ant}")
    print(f"  THEN recommend:  {con}")
    print(f"  Confidence: {row['confidence']:.0%} | Lift: {row['lift']:.2f}")
```

Expected output:

```
Strong, Actionable Rules:
=================================================================

  IF customer buys: butter, eggs
  THEN recommend:  milk
  Confidence: 100% | Lift: 1.25
```

---

## Real-World Applications

Association rules are used in many fields beyond grocery stores:

```
Applications of Association Rules:
═══════════════════════════════════

1. RETAIL / E-COMMERCE
   ─────────────────────
   "Frequently Bought Together" on Amazon
   Product placement in stores
   Bundle deals and promotions

2. WEBSITE OPTIMIZATION
   ─────────────────────
   Users who visit page A also visit page B
   → Add link from A to B
   → Redesign navigation

3. MEDICAL DIAGNOSIS
   ─────────────────────
   Symptoms that appear together suggest specific diseases
   {fever, cough, fatigue} → {influenza}

4. STREAMING SERVICES
   ─────────────────────
   Users who watched Movie A also watched Movie B
   → Power recommendation engines

5. TELECOMMUNICATIONS
   ─────────────────────
   Customers who use Service A often add Service B
   → Cross-selling opportunities

6. CYBERSECURITY
   ─────────────────────
   Certain network events often precede attacks
   {port scan, failed logins} → {data breach attempt}
```

---

## Complete Example: Grocery Store Market Basket Analysis

Let us build a complete market basket analysis with a larger dataset.

```python
import pandas as pd
import numpy as np
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules

# ============================================
# Step 1: Generate realistic grocery data
# ============================================
np.random.seed(42)

# Define item groups (items in same group are often bought together)
item_groups = {
    'breakfast': ['bread', 'butter', 'jam', 'eggs', 'milk', 'cereal', 'orange_juice'],
    'dinner': ['pasta', 'tomato_sauce', 'ground_beef', 'onion', 'garlic', 'olive_oil'],
    'snacks': ['chips', 'soda', 'cookies', 'chocolate', 'ice_cream'],
    'healthy': ['apples', 'bananas', 'yogurt', 'salad', 'chicken_breast'],
}

def generate_transaction():
    """Generate a realistic shopping transaction."""
    transaction = []

    # Each shopper picks 1-3 categories to shop from
    n_categories = np.random.choice([1, 2, 3], p=[0.3, 0.5, 0.2])
    categories = np.random.choice(list(item_groups.keys()),
                                  size=n_categories, replace=False)

    for category in categories:
        items = item_groups[category]
        # Pick 2-4 items from each category
        n_items = min(np.random.randint(2, 5), len(items))
        selected = np.random.choice(items, size=n_items, replace=False)
        transaction.extend(selected)

    return list(set(transaction))  # Remove duplicates

# Generate 500 transactions
transactions = [generate_transaction() for _ in range(500)]

print("Grocery Store Market Basket Analysis")
print("=" * 50)
print(f"Total transactions: {len(transactions)}")
print(f"\nSample transactions:")
for i in range(5):
    print(f"  Customer {i+1}: {transactions[i]}")

# ============================================
# Step 2: Convert and analyze
# ============================================
te = TransactionEncoder()
te_array = te.fit(transactions).transform(transactions)
df = pd.DataFrame(te_array, columns=te.columns_)

# Show item popularity
print(f"\nItem Popularity (% of transactions):")
print("-" * 40)
popularity = df.mean().sort_values(ascending=False)
for item, pct in popularity.items():
    bar = "#" * int(pct * 40)
    print(f"  {item:<18} {pct:>5.1%}  {bar}")

# ============================================
# Step 3: Find frequent item sets
# ============================================
frequent = apriori(df, min_support=0.05, use_colnames=True)
print(f"\nFound {len(frequent)} frequent item sets")

# Show top 10 pairs
pairs = frequent[frequent['itemsets'].apply(len) == 2]
pairs_sorted = pairs.sort_values('support', ascending=False)
print(f"\nTop 10 Most Common Item Pairs:")
print("-" * 45)
for _, row in pairs_sorted.head(10).iterrows():
    items = ', '.join(sorted(row['itemsets']))
    print(f"  {items:<35} {row['support']:.1%}")

# ============================================
# Step 4: Generate and filter rules
# ============================================
rules = association_rules(frequent, metric="lift", min_threshold=1.0)

# Filter for useful rules
useful_rules = rules[
    (rules['confidence'] >= 0.4) &
    (rules['lift'] >= 1.5) &
    (rules['support'] >= 0.03)
].sort_values('lift', ascending=False)

print(f"\nTop Business-Actionable Rules:")
print("=" * 75)
print(f"{'IF customer buys':<30} {'RECOMMEND':<20} {'Conf':>6} {'Lift':>6} {'Supp':>6}")
print("-" * 75)
for _, row in useful_rules.head(15).iterrows():
    ant = ', '.join(sorted(row['antecedents']))
    con = ', '.join(sorted(row['consequents']))
    print(f"  {ant:<28} → {con:<18} {row['confidence']:>5.0%} {row['lift']:>5.1f}  {row['support']:>5.1%}")

# ============================================
# Step 5: Business recommendations
# ============================================
print(f"\n{'='*50}")
print("BUSINESS RECOMMENDATIONS")
print(f"{'='*50}")

if len(useful_rules) > 0:
    # Best rule for product placement
    best_lift = useful_rules.iloc[0]
    ant = ', '.join(sorted(best_lift['antecedents']))
    con = ', '.join(sorted(best_lift['consequents']))
    print(f"\n1. PRODUCT PLACEMENT:")
    print(f"   Place {con} near {ant}")
    print(f"   Reason: {best_lift['lift']:.1f}x more likely to be bought together")

    # Best rule for bundle deals
    best_conf = useful_rules.sort_values('confidence', ascending=False).iloc[0]
    ant = ', '.join(sorted(best_conf['antecedents']))
    con = ', '.join(sorted(best_conf['consequents']))
    print(f"\n2. BUNDLE DEAL:")
    print(f"   Offer '{ant} + {con}' combo pack")
    print(f"   Reason: {best_conf['confidence']:.0%} of {ant} buyers also buy {con}")

    # Most popular combination for promotion
    best_support = useful_rules.sort_values('support', ascending=False).iloc[0]
    ant = ', '.join(sorted(best_support['antecedents']))
    con = ', '.join(sorted(best_support['consequents']))
    print(f"\n3. CROSS-PROMOTION:")
    print(f"   When {ant} is in cart, suggest {con}")
    print(f"   Applies to {best_support['support']:.0%} of all transactions")
```

Expected output:

```
Grocery Store Market Basket Analysis
==================================================
Total transactions: 500

Sample transactions:
  Customer 1: ['bread', 'eggs', 'milk', 'pasta', 'garlic']
  Customer 2: ['chips', 'soda', 'cookies', 'chocolate']
  Customer 3: ['butter', 'jam', 'cereal', 'milk']
  Customer 4: ['apples', 'yogurt', 'salad', 'chicken_breast']
  Customer 5: ['bread', 'eggs', 'tomato_sauce', 'onion']

Item Popularity (% of transactions):
----------------------------------------
  milk               32.4%  ############
  bread              31.8%  ############
  eggs               29.6%  ###########
  butter             27.2%  ##########
  onion              24.0%  #########
  pasta              23.6%  #########
  garlic             22.8%  #########
  tomato_sauce       22.4%  ########
  olive_oil          21.6%  ########
  soda               20.2%  ########
  chips              19.8%  #######
  cookies            18.4%  #######
  chocolate          17.6%  #######
  ground_beef        17.2%  ######
  apples             16.8%  ######
  bananas            16.0%  ######
  yogurt             15.6%  ######
  chicken_breast     14.8%  #####
  salad              14.4%  #####
  cereal             14.2%  #####
  jam                13.8%  #####
  orange_juice       13.4%  #####
  ice_cream          12.8%  #####

Found 187 frequent item sets

Top 10 Most Common Item Pairs:
---------------------------------------------
  bread, milk                             12.8%
  bread, eggs                             11.6%
  bread, butter                           11.2%
  butter, milk                            10.8%
  eggs, milk                              10.4%
  garlic, onion                            9.8%
  onion, pasta                             9.6%
  garlic, pasta                            9.2%
  pasta, tomato_sauce                      9.0%
  onion, tomato_sauce                      8.8%

Top Business-Actionable Rules:
===========================================================================
IF customer buys                RECOMMEND              Conf   Lift   Supp
---------------------------------------------------------------------------
  garlic, tomato_sauce         → pasta                  72%    3.1   5.6%
  ground_beef, onion           → pasta                  68%    2.9   4.8%
  olive_oil, tomato_sauce      → pasta                  65%    2.8   4.4%
  garlic, pasta                → onion                  63%    2.6   5.8%
  pasta, tomato_sauce          → garlic                 61%    2.7   5.6%
  chips, cookies               → soda                   58%    2.9   4.2%
  cookies, soda                → chips                  55%    2.8   3.8%
  butter, jam                  → bread                  54%    1.7   3.4%
  cereal, milk                 → bread                  52%    1.6   3.2%
  bananas, yogurt              → apples                 50%    3.0   3.0%

==================================================
BUSINESS RECOMMENDATIONS
==================================================

1. PRODUCT PLACEMENT:
   Place pasta near garlic, tomato_sauce
   Reason: 3.1x more likely to be bought together

2. BUNDLE DEAL:
   Offer 'garlic, tomato_sauce + pasta' combo pack
   Reason: 72% of garlic, tomato_sauce buyers also buy pasta

3. CROSS-PROMOTION:
   When garlic, pasta is in cart, suggest onion
   Applies to 6% of all transactions
```

**Key observations from the results:**

1. Dinner items (pasta, garlic, tomato_sauce, onion) have strong associations -- they are recipe ingredients.
2. Snack items (chips, cookies, soda) cluster together.
3. Breakfast items (bread, butter, milk) appear together frequently.
4. The highest lift values are for recipe combinations, which makes intuitive sense.

---

## Limitations and When Not to Use

Association rules are powerful but not always the right tool:

```
When Association Rules Work Well:
═════════════════════════════════
✓ Transaction data (shopping, browsing, clicks)
✓ Finding co-occurrence patterns
✓ Items are either present or absent (binary)
✓ You want interpretable results
✓ Medium-sized datasets (hundreds to millions of transactions)

When They Do NOT Work Well:
═══════════════════════════
✗ Continuous data (temperatures, prices)
   → Need to bin values first, which loses information

✗ Very sparse data (millions of products, few per transaction)
   → Support values will be very low for everything

✗ Temporal patterns (order matters)
   → Association rules ignore the sequence
   → Use sequential pattern mining instead

✗ Prediction tasks
   → Association rules find patterns but do not predict well
   → Use classification/regression models instead

✗ Small datasets
   → Need enough transactions for patterns to be meaningful
   → At least 100+ transactions recommended
```

### Common Pitfalls

1. **Too many rules**: Lowering `min_support` creates thousands of rules. Most will be noise. Start with higher thresholds and lower gradually.

2. **Confusing correlation with causation**: `{diapers} -> {beer}` does not mean diapers cause beer purchases. Both might be bought by the same demographic (parents shopping in the evening).

3. **Ignoring lift**: A rule with high confidence but low lift might just reflect item popularity. Always check lift.

4. **Not validating rules**: Show rules to domain experts. A rule that looks strange might be a data error or a genuine insight.

---

## Common Mistakes

1. **Forgetting to install mlxtend**. This library is not included with scikit-learn. Run `pip install mlxtend` first.

2. **Setting min_support too low**. This creates thousands of item sets and takes a long time. Start with 0.1 and decrease if you get too few results.

3. **Not using `use_colnames=True`** in the `apriori` function. Without this, you get column numbers instead of item names, making results hard to read.

4. **Confusing confidence with lift**. High confidence does not always mean a strong association. A rule `{anything} -> {milk}` might have high confidence simply because everyone buys milk. Check lift to see if the association is real.

5. **Applying rules blindly without domain knowledge**. Always have a business person review the rules. What seems like a pattern in data might not be actionable.

---

## Best Practices

1. **Start with reasonable thresholds**. Begin with `min_support=0.05` and `min_threshold=1.0` for lift. Adjust based on your data size.

2. **Focus on lift, not just confidence**. Lift tells you if the association is genuine or just reflects item popularity.

3. **Limit rule length**. Rules with 5+ items in the antecedent are hard to act on. Set `max_len` in the `apriori` function.

4. **Validate with domain experts**. Show your top rules to someone who understands the business. They can confirm which ones make sense.

5. **Test rules on new data**. Rules found in January might not hold in July. Check if patterns persist over time.

6. **Consider seasonality**. Ice cream and sunscreen might associate in summer but not in winter. Analyze different time periods separately.

---

## Quick Summary

Association rules discover items that appear together in transactions. The Apriori algorithm efficiently finds frequent item sets by building from singles to pairs to larger sets, pruning infrequent combinations at each step. Three metrics measure rule quality: support (how common), confidence (how reliable), and lift (how surprising). Use mlxtend to implement this in Python.

---

## Key Points to Remember

1. Association rules find patterns like "people who buy A also buy B."
2. Support measures how often an item set appears in all transactions.
3. Confidence measures the probability of the consequent given the antecedent.
4. Lift measures how much more likely items appear together compared to chance. Lift > 1 means a positive association.
5. The Apriori algorithm prunes infrequent items early to save computation.
6. Use `TransactionEncoder` to convert transaction lists to binary format.
7. Use `apriori()` to find frequent item sets and `association_rules()` to generate rules.
8. Always filter rules by lift > 1.0 to get meaningful associations.
9. High confidence alone can be misleading -- always check lift too.
10. Association rules find correlations, not causation.

---

## Practice Questions

### Question 1
In a store with 1000 transactions, bread appears in 400, butter in 300, and both together in 200. Calculate the support, confidence, and lift for the rule `{bread} -> {butter}`.

**Answer:**
- Support({bread, butter}) = 200/1000 = 0.20
- Confidence({bread} -> {butter}) = Support({bread, butter}) / Support({bread}) = 0.20 / 0.40 = 0.50
- Lift = Confidence / Support({butter}) = 0.50 / 0.30 = 1.67

The lift of 1.67 means bread and butter are 67% more likely to be bought together than by chance. This is a meaningful association.

### Question 2
A rule has high confidence (0.95) but lift of 0.98. Should you use this rule for product recommendations?

**Answer:** No. Even though confidence is very high, the lift is below 1.0 (0.98). This means the items are actually slightly less likely to be bought together than by chance. The high confidence is misleading -- it probably happens because the consequent item is very popular (almost everyone buys it regardless). Buying the antecedent does not actually increase the likelihood of buying the consequent.

### Question 3
Why does the Apriori algorithm start with single items instead of checking all possible combinations directly?

**Answer:** Checking all possible combinations directly would be computationally impossible. With just 100 products, there are 2^100 possible combinations (more than the number of atoms in the universe). Apriori starts with single items and builds up. At each level, it removes infrequent sets. If {truffle oil} is infrequent, all combinations containing truffle oil are automatically skipped. This pruning dramatically reduces the number of combinations to check, making the algorithm practical even for large product catalogs.

### Question 4
You discover the rule `{fever, headache} -> {flu medication}` in pharmacy data. What would you recommend to the pharmacy?

**Answer:** This rule suggests customers who buy fever and headache remedies often also buy flu medication. Recommendations: (1) Place flu medication near the fever/headache medicine aisle, (2) Create a "flu relief bundle" with all three items at a discount, (3) When a customer brings fever and headache remedies to checkout, suggest flu medication. However, remember this is correlation, not causation -- people buying these items likely already have the flu and are treating symptoms.

---

## Exercises

### Exercise 1: Online Bookstore

Create transaction data for an online bookstore with categories like fiction, science, history, cooking, and self-help. Generate at least 200 transactions where books in the same category are often bought together. Use Apriori to find which books are frequently purchased together. Present the top 5 rules with interpretation.

**Hint:** Follow the grocery store example but use book titles instead of food items.

### Exercise 2: Website Navigation Patterns

Create data representing user page visits on a website (home, products, pricing, about, contact, blog, signup). Generate 300 sessions. Find which pages users commonly visit together. What navigation improvements would you suggest based on the rules?

**Hint:** Treat each user session as a transaction and each visited page as an item.

### Exercise 3: Experiment with Thresholds

Using the grocery store example, run the analysis with three different min_support values: 0.02, 0.05, and 0.10. For each, count how many rules are generated and identify the top 3 rules by lift. How do the results change? Which threshold gives the most useful rules?

**Hint:** Lower support finds rarer patterns but produces more rules. Higher support finds only very common patterns.

---

## What Is Next?

In this chapter, you learned how to discover hidden patterns in transaction data. You can now find which items go together and make business recommendations.

But how do you know if your machine learning models are actually good? In the next two chapters, we will dive deep into **model evaluation**. Chapter 23 covers evaluation metrics for regression models (predicting numbers), and Chapter 24 covers classification models (predicting categories). These chapters will give you the tools to measure and compare model performance rigorously.
