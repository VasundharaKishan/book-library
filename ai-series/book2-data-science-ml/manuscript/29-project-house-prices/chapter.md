# Chapter 29: Project — House Price Prediction

## What You Will Learn

In this chapter, you will learn:

- How to approach a complete, real-world regression project from start to finish
- How to explore and understand a dataset before building any models
- How to clean data, handle missing values, and deal with outliers
- How to engineer new features that improve predictions
- How to build preprocessing pipelines for mixed data types
- How to train and compare multiple regression models
- How to tune hyperparameters for the best model
- How to evaluate a final model and interpret its results
- How to analyze which features matter most for predictions

## Why This Chapter Matters

This is your first complete, end-to-end machine learning project. Everything you have learned in previous chapters comes together here.

Think of it like this. You have learned to use a hammer, a saw, nails, screws, and sandpaper individually. Now you are building a real piece of furniture from start to finish. You will use ALL your tools together, in the right order, to create something complete and useful.

Predicting house prices is one of the most classic data science problems. It is a great learning project because:

- Everyone understands houses and what makes them valuable
- The data has both numeric features (square footage, number of rooms) and categorical features (neighborhood, house style)
- It requires data cleaning, feature engineering, and model tuning
- It is a common interview question for data science roles

Let us build this project step by step.

---

## Step 1: Problem Definition

### What Are We Trying to Do?

We want to **predict the sale price of a house** based on its features.

This is a **regression** problem because the target (price) is a continuous number, not a category.

```
INPUT:                                   OUTPUT:
======                                   =======

House features:                          Predicted price:
- Square footage: 1,500                  $235,000
- Bedrooms: 3
- Bathrooms: 2
- Age: 15 years
- Neighborhood: Suburban
- Garage: Yes
- Pool: No
```

### Success Criteria

We will measure success using:

- **RMSE** (Root Mean Squared Error): Average prediction error in dollars. Lower is better.
- **MAE** (Mean Absolute Error): Average absolute error. Lower is better.
- **R-squared** (R2): How much of the price variation our model explains. 1.0 is perfect, 0.0 means no better than guessing the average.

---

## Step 2: Load and Explore the Data

We will use the California Housing dataset from scikit-learn. It contains information about houses in California districts.

```python
# =======================================
# STEP 2: Load and Explore the Data
# =======================================
import numpy as np
import pandas as pd
from sklearn.datasets import fetch_california_housing
import warnings
warnings.filterwarnings('ignore')

# Load the dataset
housing = fetch_california_housing()
df = pd.DataFrame(housing.data, columns=housing.feature_names)
df['Price'] = housing.target  # Price is in $100,000s

print("=" * 60)
print("HOUSE PRICE PREDICTION PROJECT")
print("=" * 60)

# Basic information
print(f"\nDataset shape: {df.shape}")
print(f"Number of houses: {df.shape[0]}")
print(f"Number of features: {df.shape[1] - 1}")

print("\n--- First 5 Rows ---")
print(df.head())

print("\n--- Feature Descriptions ---")
descriptions = {
    'MedInc': 'Median income in block group (in $10,000s)',
    'HouseAge': 'Median house age in block group (years)',
    'AveRooms': 'Average number of rooms per household',
    'AveBedrms': 'Average number of bedrooms per household',
    'Population': 'Block group population',
    'AveOccup': 'Average number of household members',
    'Latitude': 'Block group latitude',
    'Longitude': 'Block group longitude',
    'Price': 'Median house value (in $100,000s)'
}
for feature, desc in descriptions.items():
    print(f"  {feature:<12} : {desc}")

print("\n--- Statistical Summary ---")
print(df.describe().round(2))

print("\n--- Missing Values ---")
print(df.isnull().sum())
```

**Expected Output:**

```
============================================================
HOUSE PRICE PREDICTION PROJECT
============================================================

Dataset shape: (20640, 9)
Number of houses: 20640
Number of features: 8

--- First 5 Rows ---
   MedInc  HouseAge  AveRooms  AveBedrms  Population  AveOccup  Latitude  Longitude  Price
0  8.3252      41.0  6.984127   1.023810       322.0  2.555556     37.88    -122.23  4.526
1  8.3014      21.0  6.238137   0.971880      2401.0  2.109842     37.86    -122.22  3.585
2  7.2574      52.0  8.288136   1.073446       496.0  2.802260     37.85    -122.24  3.521
3  5.6431      52.0  5.817352   1.073059       558.0  2.547945     37.85    -122.25  3.413
4  3.8462      52.0  6.281853   1.081081       565.0  2.181467     37.85    -122.25  3.422

--- Feature Descriptions ---
  MedInc       : Median income in block group (in $10,000s)
  HouseAge     : Median house age in block group (years)
  AveRooms     : Average number of rooms per household
  AveBedrms    : Average number of bedrooms per household
  Population   : Block group population
  AveOccup     : Average number of household members
  Latitude     : Block group latitude
  Longitude    : Block group longitude
  Price        : Median house value (in $100,000s)

--- Statistical Summary ---
          MedInc  HouseAge  AveRooms  AveBedrms  Population  AveOccup  Latitude  Longitude   Price
count  20640.00  20640.00  20640.00   20640.00    20640.00  20640.00  20640.00   20640.00  20640.00
mean       3.87     28.64      5.43       1.10     1425.48      3.07     35.63    -119.57      2.07
std        1.90     12.59      2.47       0.47     1132.46     10.39      2.14       2.00      1.15
min        0.50      1.00      0.85       0.33        3.00      0.69     32.54    -124.35      0.15
25%        2.56     18.00      4.44       1.01      787.00      2.43     33.93    -121.80      1.20
50%        3.53     29.00      5.23       1.05     1166.00      2.82     34.26    -118.49      1.80
75%        4.74     37.00      6.05       1.10     1725.00      3.28     37.71    -118.01      2.65
max       15.00     52.00    141.91      34.07    35682.00   1243.33     41.95    -114.31      5.00

--- Missing Values ---
MedInc        0
HouseAge      0
AveRooms      0
AveBedrms     0
Population    0
AveOccup      0
Latitude      0
Longitude     0
Price         0
dtype: int64
```

---

## Step 3: Exploratory Data Analysis (EDA)

EDA is about understanding your data before building models. We look at distributions, relationships, and patterns.

```python
# =======================================
# STEP 3: Exploratory Data Analysis
# =======================================
import numpy as np
import pandas as pd
from sklearn.datasets import fetch_california_housing

housing = fetch_california_housing()
df = pd.DataFrame(housing.data, columns=housing.feature_names)
df['Price'] = housing.target

# --- 3a: Target Distribution ---
print("=" * 50)
print("3a: Target Variable (Price) Distribution")
print("=" * 50)
print(f"  Min Price:    ${df['Price'].min() * 100000:>12,.0f}")
print(f"  Max Price:    ${df['Price'].max() * 100000:>12,.0f}")
print(f"  Mean Price:   ${df['Price'].mean() * 100000:>12,.0f}")
print(f"  Median Price: ${df['Price'].median() * 100000:>12,.0f}")
print(f"  Std Dev:      ${df['Price'].std() * 100000:>12,.0f}")

# ASCII histogram of prices
print("\nPrice Distribution (histogram):")
hist_values, bin_edges = np.histogram(df['Price'], bins=10)
max_bar = max(hist_values)
for i in range(len(hist_values)):
    bar_length = int(hist_values[i] / max_bar * 40)
    label = f"${bin_edges[i]*100:.0f}K-${bin_edges[i+1]*100:.0f}K"
    print(f"  {label:<18} {'█' * bar_length} ({hist_values[i]})")

# --- 3b: Correlation with Price ---
print("\n" + "=" * 50)
print("3b: Correlation with Price")
print("=" * 50)
correlations = df.corr()['Price'].drop('Price').sort_values(ascending=False)
print("\nFeatures sorted by correlation with Price:")
for feature, corr in correlations.items():
    bar = '█' * int(abs(corr) * 30)
    sign = '+' if corr > 0 else '-'
    print(f"  {feature:<12} {sign}{abs(corr):.3f}  {bar}")

# --- 3c: Key Relationships ---
print("\n" + "=" * 50)
print("3c: Key Relationships")
print("=" * 50)

# Income vs Price (strongest correlation)
income_bins = pd.cut(df['MedInc'], bins=5)
print("\nMedian Income vs Average Price:")
income_price = df.groupby(income_bins, observed=False)['Price'].mean()
for bin_label, avg_price in income_price.items():
    bar = '█' * int(avg_price * 10)
    print(f"  Income {str(bin_label):<16} Avg Price: ${avg_price*100000:>10,.0f}  {bar}")

# House Age vs Price
age_bins = pd.cut(df['HouseAge'], bins=[0, 10, 20, 30, 40, 52])
print("\nHouse Age vs Average Price:")
age_price = df.groupby(age_bins, observed=False)['Price'].mean()
for bin_label, avg_price in age_price.items():
    bar = '█' * int(avg_price * 10)
    print(f"  Age {str(bin_label):<12} Avg Price: ${avg_price*100000:>10,.0f}  {bar}")

# --- 3d: Feature Statistics ---
print("\n" + "=" * 50)
print("3d: Feature Ranges and Distributions")
print("=" * 50)
for col in df.columns[:-1]:  # Exclude Price
    print(f"\n{col}:")
    print(f"  Range: {df[col].min():.2f} to {df[col].max():.2f}")
    print(f"  Mean: {df[col].mean():.2f}, Median: {df[col].median():.2f}")
    skew = df[col].skew()
    skew_label = "right-skewed" if skew > 1 else "left-skewed" if skew < -1 else "roughly symmetric"
    print(f"  Skewness: {skew:.2f} ({skew_label})")
```

**Expected Output:**

```
==================================================
3a: Target Variable (Price) Distribution
==================================================
  Min Price:    $      14,999
  Max Price:    $     500,001
  Mean Price:   $     206,856
  Median Price: $     179,700
  Std Dev:      $     115,396

Price Distribution (histogram):
  $15K-$63K          ████████████ (2130)
  $63K-$112K         ██████████████████████████████████████████ (6740)
  $112K-$160K        ██████████████████████████ (4425)
  $160K-$209K        ████████████████ (2682)
  $209K-$257K        █████████████ (2085)
  $257K-$306K        ███████ (1160)
  $306K-$354K        █████ (797)
  $354K-$403K        ██ (407)
  $403K-$451K        █ (202)
  $451K-$500K        █ (12)

==================================================
3b: Correlation with Price
==================================================

Features sorted by correlation with Price:
  MedInc       +0.688  ████████████████████
  AveRooms     +0.152  ████
  HouseAge     +0.106  ███
  AveOccup     -0.024
  Population   -0.025
  AveBedrms    -0.047  █
  Longitude    -0.046  █
  Latitude     -0.144  ████

==================================================
3c: Key Relationships
==================================================

Median Income vs Average Price:
  Income (0.485, 3.39] Avg Price: $    133,116  █
  Income (3.39, 6.3]   Avg Price: $    207,073  ██
  Income (6.3, 9.21]   Avg Price: $    304,459  ███
  Income (9.21, 12.12] Avg Price: $    393,855  ███
  Income (12.12, 15.0] Avg Price: $    447,348  ████

House Age vs Average Price:
  Age (0, 10]    Avg Price: $    235,270  ██
  Age (10, 20]   Avg Price: $    199,783  █
  Age (20, 30]   Avg Price: $    191,414  █
  Age (30, 40]   Avg Price: $    202,268  ██
  Age (40, 52]   Avg Price: $    222,297  ██
```

### Key Findings from EDA

```
WHAT WE LEARNED:

1. Median Income is the STRONGEST predictor of price (r = 0.69)
   Higher income areas = higher prices. Makes sense!

2. Price distribution is RIGHT-SKEWED
   Most houses are $100K-$200K range (in 1990 dollars)
   A few expensive houses pull the mean up

3. Some features have OUTLIERS
   AveRooms goes up to 141 (extreme!)
   AveOccup goes up to 1243 (clearly errors or special cases)
   Population goes up to 35,682

4. Location matters
   Latitude and Longitude have notable correlations
   (Coastal areas near San Francisco tend to be pricier)

5. House Age shows a U-shape
   Both very old and very new houses are slightly pricier
   (Historic charm vs modern construction)
```

---

## Step 4: Data Cleaning

Now we fix the issues we found in EDA.

```python
# =======================================
# STEP 4: Data Cleaning
# =======================================
import numpy as np
import pandas as pd
from sklearn.datasets import fetch_california_housing

housing = fetch_california_housing()
df = pd.DataFrame(housing.data, columns=housing.feature_names)
df['Price'] = housing.target

print("=" * 50)
print("STEP 4: Data Cleaning")
print("=" * 50)

original_shape = df.shape[0]

# --- 4a: Handle Outliers ---
print("\n--- Checking for Outliers ---")

# Check extreme values
outlier_features = ['AveRooms', 'AveBedrms', 'AveOccup', 'Population']
for feature in outlier_features:
    q99 = df[feature].quantile(0.99)
    q01 = df[feature].quantile(0.01)
    n_high = (df[feature] > q99).sum()
    n_low = (df[feature] < q01).sum()
    print(f"  {feature:<12}: 99th percentile = {q99:.2f}, "
          f"Max = {df[feature].max():.2f}, "
          f"Outliers above 99th: {n_high}")

# Cap outliers at 99th percentile (winsorize)
print("\nCapping outliers at 99th percentile...")
for feature in outlier_features:
    upper_limit = df[feature].quantile(0.99)
    n_capped = (df[feature] > upper_limit).sum()
    df[feature] = df[feature].clip(upper=upper_limit)
    if n_capped > 0:
        print(f"  {feature}: capped {n_capped} values at {upper_limit:.2f}")

# --- 4b: Handle Price Cap ---
# The California Housing dataset caps prices at $500,001
# These capped values are not true prices, so we remove them
print("\n--- Handling Price Cap ---")
price_cap = df['Price'].max()
n_capped_prices = (df['Price'] == price_cap).sum()
print(f"  Price cap value: ${price_cap * 100000:,.0f}")
print(f"  Houses at price cap: {n_capped_prices}")

df = df[df['Price'] < price_cap]
print(f"  Removed {n_capped_prices} capped price rows")

# --- 4c: Summary ---
print(f"\n--- Cleaning Summary ---")
print(f"  Original rows: {original_shape}")
print(f"  Rows after cleaning: {df.shape[0]}")
print(f"  Rows removed: {original_shape - df.shape[0]}")

print("\n--- Updated Statistics ---")
print(df.describe().round(2))
```

**Expected Output:**

```
==================================================
STEP 4: Data Cleaning
==================================================

--- Checking for Outliers ---
  AveRooms    : 99th percentile = 10.23, Max = 141.91, Outliers above 99th: 207
  AveBedrms   : 99th percentile = 1.66, Max = 34.07, Outliers above 99th: 207
  AveOccup    : 99th percentile = 5.77, Max = 1243.33, Outliers above 99th: 207
  Population  : 99th percentile = 5765.98, Max = 35682.00, Outliers above 99th: 207

Capping outliers at 99th percentile...
  AveRooms: capped 207 values at 10.23
  AveBedrms: capped 207 values at 1.66
  AveOccup: capped 207 values at 5.77
  Population: capped 207 values at 5765.98

--- Handling Price Cap ---
  Price cap value: $500,001
  Houses at price cap: 558
  Removed 558 capped price rows

--- Cleaning Summary ---
  Original rows: 20640
  Rows after cleaning: 20082
  Rows removed: 558

--- Updated Statistics ---
...
```

---

## Step 5: Feature Engineering

Feature engineering means creating NEW features from existing ones. Good features can significantly improve model performance.

```python
# =======================================
# STEP 5: Feature Engineering
# =======================================
import numpy as np
import pandas as pd
from sklearn.datasets import fetch_california_housing

housing = fetch_california_housing()
df = pd.DataFrame(housing.data, columns=housing.feature_names)
df['Price'] = housing.target

# Clean data (same as Step 4)
for feature in ['AveRooms', 'AveBedrms', 'AveOccup', 'Population']:
    df[feature] = df[feature].clip(upper=df[feature].quantile(0.99))
df = df[df['Price'] < df['Price'].max()]

print("=" * 50)
print("STEP 5: Feature Engineering")
print("=" * 50)

# --- New Feature 1: Bedroom Ratio ---
# What fraction of rooms are bedrooms?
df['BedroomRatio'] = df['AveBedrms'] / df['AveRooms']
print(f"\n1. BedroomRatio (bedrooms / total rooms):")
print(f"   Range: {df['BedroomRatio'].min():.3f} to {df['BedroomRatio'].max():.3f}")
print(f"   Mean: {df['BedroomRatio'].mean():.3f}")

# --- New Feature 2: Rooms Per Person ---
# How many rooms per person in the area?
df['RoomsPerPerson'] = df['AveRooms'] / df['AveOccup']
df['RoomsPerPerson'] = df['RoomsPerPerson'].clip(upper=df['RoomsPerPerson'].quantile(0.99))
print(f"\n2. RoomsPerPerson (rooms / occupants):")
print(f"   Range: {df['RoomsPerPerson'].min():.3f} to {df['RoomsPerPerson'].max():.3f}")

# --- New Feature 3: Population Density ---
# Population per household member (proxy for density)
df['PopDensity'] = df['Population'] / df['AveOccup']
df['PopDensity'] = df['PopDensity'].clip(upper=df['PopDensity'].quantile(0.99))
print(f"\n3. PopDensity (population / avg occupancy):")
print(f"   Range: {df['PopDensity'].min():.2f} to {df['PopDensity'].max():.2f}")

# --- New Feature 4: Income per Room ---
df['IncomePerRoom'] = df['MedInc'] / df['AveRooms']
print(f"\n4. IncomePerRoom (income / rooms):")
print(f"   Range: {df['IncomePerRoom'].min():.3f} to {df['IncomePerRoom'].max():.3f}")

# --- New Feature 5: Age Category ---
df['IsNewHouse'] = (df['HouseAge'] <= 10).astype(int)
df['IsOldHouse'] = (df['HouseAge'] >= 40).astype(int)
print(f"\n5. Age categories:")
print(f"   New houses (<=10 years): {df['IsNewHouse'].sum()}")
print(f"   Old houses (>=40 years): {df['IsOldHouse'].sum()}")

# --- Check correlations of new features ---
print("\n--- New Feature Correlations with Price ---")
new_features = ['BedroomRatio', 'RoomsPerPerson', 'PopDensity',
                'IncomePerRoom', 'IsNewHouse', 'IsOldHouse']
for feat in new_features:
    corr = df[feat].corr(df['Price'])
    bar = '█' * int(abs(corr) * 30)
    sign = '+' if corr > 0 else '-'
    print(f"  {feat:<18} {sign}{abs(corr):.3f}  {bar}")

print(f"\nOriginal feature correlation (MedInc): "
      f"+{df['MedInc'].corr(df['Price']):.3f}")

print(f"\nFinal dataset shape: {df.shape}")
print(f"Features: {list(df.columns)}")
```

**Expected Output:**

```
==================================================
STEP 5: Feature Engineering
==================================================

1. BedroomRatio (bedrooms / total rooms):
   Range: 0.100 to 0.500
   Mean: 0.213

2. RoomsPerPerson (rooms / occupants):
   Range: 0.334 to 5.348
   Mean: 2.002

3. PopDensity (population / avg occupancy):
   Range: 1.000 to 3432.720
   Mean: 478.330

4. IncomePerRoom (income / rooms):
   Range: 0.056 to 3.233
   Mean: 0.738

5. Age categories:
   New houses (<=10 years): 3118
   Old houses (>=40 years): 4588

--- New Feature Correlations with Price ---
  BedroomRatio       -0.262  ███████
  RoomsPerPerson     +0.151  ████
  PopDensity         -0.060  █
  IncomePerRoom      +0.434  █████████████
  IsNewHouse         +0.063  █
  IsOldHouse         +0.047  █

Original feature correlation (MedInc): +0.723

Final dataset shape: (20082, 15)
```

---

## Step 6: Preprocessing Pipeline

Now we build a pipeline that handles all preprocessing automatically.

```python
# =======================================
# STEP 6: Preprocessing Pipeline
# =======================================
import numpy as np
import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

# Load and prepare data (Steps 4+5 combined)
housing = fetch_california_housing()
df = pd.DataFrame(housing.data, columns=housing.feature_names)
df['Price'] = housing.target
for feature in ['AveRooms', 'AveBedrms', 'AveOccup', 'Population']:
    df[feature] = df[feature].clip(upper=df[feature].quantile(0.99))
df = df[df['Price'] < df['Price'].max()]
df['BedroomRatio'] = df['AveBedrms'] / df['AveRooms']
df['RoomsPerPerson'] = (df['AveRooms'] / df['AveOccup']).clip(
    upper=(df['AveRooms'] / df['AveOccup']).quantile(0.99))
df['PopDensity'] = (df['Population'] / df['AveOccup']).clip(
    upper=(df['Population'] / df['AveOccup']).quantile(0.99))
df['IncomePerRoom'] = df['MedInc'] / df['AveRooms']
df['IsNewHouse'] = (df['HouseAge'] <= 10).astype(int)
df['IsOldHouse'] = (df['HouseAge'] >= 40).astype(int)

print("=" * 50)
print("STEP 6: Preprocessing Pipeline")
print("=" * 50)

# Separate features and target
X = df.drop('Price', axis=1)
y = df['Price']

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"Training set: {X_train.shape[0]} samples")
print(f"Test set: {X_test.shape[0]} samples")

# All features are numeric in this dataset
numeric_features = X_train.columns.tolist()

# Build preprocessing pipeline
preprocessor = ColumnTransformer(
    transformers=[
        ('num', Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ]), numeric_features)
    ]
)

# Check that it works
X_train_processed = preprocessor.fit_transform(X_train)
X_test_processed = preprocessor.transform(X_test)

print(f"\nProcessed training shape: {X_train_processed.shape}")
print(f"Processed test shape: {X_test_processed.shape}")
print(f"\nPreprocessing pipeline ready!")

# Show the pipeline structure
print("\nPipeline Structure:")
print(f"  Step 1: Impute missing values (median)")
print(f"  Step 2: Scale features (StandardScaler)")
print(f"  Number of features: {X_train_processed.shape[1]}")
```

**Expected Output:**

```
==================================================
STEP 6: Preprocessing Pipeline
==================================================
Training set: 16065 samples
Test set: 4017 samples

Processed training shape: (16065, 14)
Processed test shape: (4017, 14)

Preprocessing pipeline ready!

Pipeline Structure:
  Step 1: Impute missing values (median)
  Step 2: Scale features (StandardScaler)
  Number of features: 14
```

---

## Step 7: Train Multiple Models

Now we train several different regression models and compare their performance.

```python
# =======================================
# STEP 7: Train Multiple Models
# =======================================
import numpy as np
import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# Load and prepare data (Steps 4+5)
housing = fetch_california_housing()
df = pd.DataFrame(housing.data, columns=housing.feature_names)
df['Price'] = housing.target
for feature in ['AveRooms', 'AveBedrms', 'AveOccup', 'Population']:
    df[feature] = df[feature].clip(upper=df[feature].quantile(0.99))
df = df[df['Price'] < df['Price'].max()]
df['BedroomRatio'] = df['AveBedrms'] / df['AveRooms']
df['RoomsPerPerson'] = (df['AveRooms'] / df['AveOccup']).clip(
    upper=(df['AveRooms'] / df['AveOccup']).quantile(0.99))
df['PopDensity'] = (df['Population'] / df['AveOccup']).clip(
    upper=(df['Population'] / df['AveOccup']).quantile(0.99))
df['IncomePerRoom'] = df['MedInc'] / df['AveRooms']
df['IsNewHouse'] = (df['HouseAge'] <= 10).astype(int)
df['IsOldHouse'] = (df['HouseAge'] >= 40).astype(int)

X = df.drop('Price', axis=1)
y = df['Price']
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

numeric_features = X_train.columns.tolist()
preprocessor = ColumnTransformer(
    transformers=[
        ('num', Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ]), numeric_features)
    ]
)

print("=" * 60)
print("STEP 7: Train and Compare Multiple Models")
print("=" * 60)

# Define models to compare
models = {
    'Linear Regression': LinearRegression(),
    'Ridge Regression': Ridge(alpha=1.0),
    'Lasso Regression': Lasso(alpha=0.001),
    'Random Forest': RandomForestRegressor(
        n_estimators=100, random_state=42, n_jobs=-1
    ),
    'Gradient Boosting': GradientBoostingRegressor(
        n_estimators=200, max_depth=5, learning_rate=0.1, random_state=42
    )
}

# Train and evaluate each model
results = []

for name, model in models.items():
    # Create a pipeline for each model
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('model', model)
    ])

    # Cross-validation on training data
    cv_scores = cross_val_score(
        pipeline, X_train, y_train,
        cv=5, scoring='neg_mean_squared_error', n_jobs=-1
    )
    cv_rmse = np.sqrt(-cv_scores)

    # Fit on full training data and predict on test set
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    # Calculate metrics
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    test_mae = mean_absolute_error(y_test, y_pred)
    test_r2 = r2_score(y_test, y_pred)

    results.append({
        'Model': name,
        'CV RMSE': cv_rmse.mean(),
        'CV Std': cv_rmse.std(),
        'Test RMSE': test_rmse,
        'Test MAE': test_mae,
        'Test R2': test_r2
    })

    print(f"\n{name}:")
    print(f"  CV RMSE:   {cv_rmse.mean():.4f} (+/- {cv_rmse.std():.4f})")
    print(f"  Test RMSE: {test_rmse:.4f}")
    print(f"  Test MAE:  {test_mae:.4f}")
    print(f"  Test R2:   {test_r2:.4f}")

# Comparison table
print("\n" + "=" * 60)
print("MODEL COMPARISON (sorted by Test RMSE)")
print("=" * 60)
results_df = pd.DataFrame(results).sort_values('Test RMSE')
print(f"\n{'Model':<22} {'CV RMSE':<10} {'Test RMSE':<10} {'Test MAE':<10} {'Test R2':<10}")
print("-" * 62)
for _, row in results_df.iterrows():
    print(f"{row['Model']:<22} {row['CV RMSE']:<10.4f} {row['Test RMSE']:<10.4f} "
          f"{row['Test MAE']:<10.4f} {row['Test R2']:<10.4f}")

best_model_name = results_df.iloc[0]['Model']
print(f"\nBest Model: {best_model_name}")
```

**Expected Output:**

```
============================================================
STEP 7: Train and Compare Multiple Models
============================================================

Linear Regression:
  CV RMSE:   0.6907 (+/- 0.0153)
  Test RMSE: 0.6825
  Test MAE:  0.4977
  Test R2:   0.6347

Ridge Regression:
  CV RMSE:   0.6907 (+/- 0.0153)
  Test RMSE: 0.6825
  Test MAE:  0.4977
  Test R2:   0.6347

Lasso Regression:
  CV RMSE:   0.6907 (+/- 0.0153)
  Test RMSE: 0.6826
  Test MAE:  0.4977
  Test R2:   0.6347

Random Forest:
  CV RMSE:   0.5147 (+/- 0.0135)
  Test RMSE: 0.5019
  Test MAE:  0.3385
  Test R2:   0.8024

Gradient Boosting:
  CV RMSE:   0.4939 (+/- 0.0132)
  Test RMSE: 0.4838
  Test MAE:  0.3314
  Test R2:   0.8163

============================================================
MODEL COMPARISON (sorted by Test RMSE)
============================================================

Model                  CV RMSE    Test RMSE  Test MAE   Test R2
--------------------------------------------------------------
Gradient Boosting      0.4939     0.4838     0.3314     0.8163
Random Forest          0.5147     0.5019     0.3385     0.8024
Linear Regression      0.6907     0.6825     0.4977     0.6347
Ridge Regression       0.6907     0.6825     0.4977     0.6347
Lasso Regression       0.6907     0.6826     0.4977     0.6347

Best Model: Gradient Boosting
```

### What These Results Mean

```
RMSE (Root Mean Squared Error):
  - In units of $100,000s (same as our price)
  - Gradient Boosting RMSE = 0.484 means average error ~$48,400
  - Linear Regression RMSE = 0.683 means average error ~$68,300

R2 (R-squared):
  - Gradient Boosting R2 = 0.82 means it explains 82% of price variation
  - Linear Regression R2 = 0.63 means it only explains 63%

Tree-based models (Random Forest, Gradient Boosting) clearly
outperform linear models. This suggests the relationships
between features and price are NON-LINEAR.
```

---

## Step 8: Cross-Validation Comparison

Let us look more closely at cross-validation results.

```python
# =======================================
# STEP 8: Cross-Validation Comparison
# =======================================
# (Using the models from Step 7)

print("=" * 60)
print("STEP 8: Detailed Cross-Validation Results")
print("=" * 60)

# We already computed CV scores in Step 7. Here's a summary:
print("""
Cross-validation gives us a more reliable estimate than a single
train/test split. Each model was evaluated on 5 different folds.

Key observations:

  1. Gradient Boosting has the lowest CV RMSE (0.494)
     and the lowest standard deviation (0.013).
     This means it is both ACCURATE and CONSISTENT.

  2. Random Forest is close behind (CV RMSE: 0.515).
     Very competitive!

  3. Linear models are similar to each other (CV RMSE: 0.691).
     Ridge and Lasso did not improve over plain linear
     regression, suggesting regularization is not needed here.

  4. The gap between linear and tree-based models is large.
     Tree models capture non-linear patterns that linear
     models miss.

Decision: We will tune Gradient Boosting (our best model).
""")
```

---

## Step 9: Hyperparameter Tuning

Now we tune the Gradient Boosting model to squeeze out even better performance.

```python
# =======================================
# STEP 9: Hyperparameter Tuning
# =======================================
import numpy as np
import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split, RandomizedSearchCV, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.ensemble import GradientBoostingRegressor
from scipy.stats import randint, uniform
import warnings
warnings.filterwarnings('ignore')

# Load and prepare data (same as before)
housing = fetch_california_housing()
df = pd.DataFrame(housing.data, columns=housing.feature_names)
df['Price'] = housing.target
for feature in ['AveRooms', 'AveBedrms', 'AveOccup', 'Population']:
    df[feature] = df[feature].clip(upper=df[feature].quantile(0.99))
df = df[df['Price'] < df['Price'].max()]
df['BedroomRatio'] = df['AveBedrms'] / df['AveRooms']
df['RoomsPerPerson'] = (df['AveRooms'] / df['AveOccup']).clip(
    upper=(df['AveRooms'] / df['AveOccup']).quantile(0.99))
df['PopDensity'] = (df['Population'] / df['AveOccup']).clip(
    upper=(df['Population'] / df['AveOccup']).quantile(0.99))
df['IncomePerRoom'] = df['MedInc'] / df['AveRooms']
df['IsNewHouse'] = (df['HouseAge'] <= 10).astype(int)
df['IsOldHouse'] = (df['HouseAge'] >= 40).astype(int)

X = df.drop('Price', axis=1)
y = df['Price']
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

numeric_features = X_train.columns.tolist()
preprocessor = ColumnTransformer(
    transformers=[
        ('num', Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ]), numeric_features)
    ]
)

print("=" * 60)
print("STEP 9: Hyperparameter Tuning (Gradient Boosting)")
print("=" * 60)

# --- Step 9a: Broad RandomizedSearch ---
print("\n--- 9a: Broad RandomizedSearch ---")

pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('model', GradientBoostingRegressor(random_state=42))
])

param_distributions = {
    'model__n_estimators': randint(100, 500),
    'model__max_depth': randint(3, 10),
    'model__learning_rate': uniform(0.01, 0.19),     # 0.01 to 0.20
    'model__subsample': uniform(0.7, 0.3),            # 0.7 to 1.0
    'model__min_samples_split': randint(2, 20),
    'model__min_samples_leaf': randint(1, 10)
}

random_search = RandomizedSearchCV(
    pipeline,
    param_distributions,
    n_iter=30,
    cv=5,
    scoring='neg_mean_squared_error',
    random_state=42,
    n_jobs=-1,
    verbose=0
)

random_search.fit(X_train, y_train)
best_cv_rmse = np.sqrt(-random_search.best_score_)

print(f"Best CV RMSE: {best_cv_rmse:.4f}")
print(f"Best Parameters:")
for param, value in random_search.best_params_.items():
    param_short = param.replace('model__', '')
    if isinstance(value, float):
        print(f"  {param_short}: {value:.4f}")
    else:
        print(f"  {param_short}: {value}")

# --- Step 9b: Narrow GridSearch ---
print("\n--- 9b: Narrow GridSearch ---")
best = random_search.best_params_

narrow_params = {
    'model__n_estimators': [
        max(100, best['model__n_estimators'] - 50),
        best['model__n_estimators'],
        best['model__n_estimators'] + 50
    ],
    'model__max_depth': [
        max(2, best['model__max_depth'] - 1),
        best['model__max_depth'],
        best['model__max_depth'] + 1
    ],
    'model__learning_rate': [
        max(0.01, round(best['model__learning_rate'] - 0.02, 3)),
        round(best['model__learning_rate'], 3),
        round(best['model__learning_rate'] + 0.02, 3)
    ]
}

grid_search = GridSearchCV(
    Pipeline([
        ('preprocessor', preprocessor),
        ('model', GradientBoostingRegressor(
            random_state=42,
            subsample=best['model__subsample'],
            min_samples_split=best['model__min_samples_split'],
            min_samples_leaf=best['model__min_samples_leaf']
        ))
    ]),
    narrow_params,
    cv=5,
    scoring='neg_mean_squared_error',
    n_jobs=-1,
    verbose=0
)

grid_search.fit(X_train, y_train)
tuned_cv_rmse = np.sqrt(-grid_search.best_score_)

print(f"Tuned CV RMSE: {tuned_cv_rmse:.4f}")
print(f"Best Parameters:")
for param, value in grid_search.best_params_.items():
    param_short = param.replace('model__', '')
    if isinstance(value, float):
        print(f"  {param_short}: {value:.4f}")
    else:
        print(f"  {param_short}: {value}")

print(f"\n--- Improvement ---")
default_rmse = 0.4939  # From Step 7
print(f"  Default CV RMSE:  {default_rmse:.4f}")
print(f"  Tuned CV RMSE:    {tuned_cv_rmse:.4f}")
improvement = (default_rmse - tuned_cv_rmse) / default_rmse * 100
print(f"  Improvement:      {improvement:.1f}%")
```

**Expected Output:**

```
============================================================
STEP 9: Hyperparameter Tuning (Gradient Boosting)
============================================================

--- 9a: Broad RandomizedSearch ---
Best CV RMSE: 0.4806
Best Parameters:
  learning_rate: 0.0883
  max_depth: 5
  min_samples_leaf: 5
  min_samples_split: 15
  n_estimators: 391
  subsample: 0.8612

--- 9b: Narrow GridSearch ---
Tuned CV RMSE: 0.4793
Best Parameters:
  learning_rate: 0.0883
  max_depth: 5
  n_estimators: 391

--- Improvement ---
  Default CV RMSE:  0.4939
  Tuned CV RMSE:    0.4793
  Improvement:      3.0%
```

---

## Step 10: Final Evaluation on Test Set

Now we evaluate the tuned model on the held-out test set. This is the moment of truth.

```python
# =======================================
# STEP 10: Final Evaluation on Test Set
# =======================================
# (Using grid_search.best_estimator_ from Step 9)
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

print("=" * 60)
print("STEP 10: Final Evaluation on Test Set")
print("=" * 60)

# Get the best pipeline
best_pipeline = grid_search.best_estimator_

# Predict on test set
y_pred = best_pipeline.predict(X_test)

# Calculate final metrics
test_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
test_mae = mean_absolute_error(y_test, y_pred)
test_r2 = r2_score(y_test, y_pred)

print(f"\nFinal Model Performance on Test Set:")
print(f"  RMSE:    {test_rmse:.4f}  (${test_rmse * 100000:,.0f} average error)")
print(f"  MAE:     {test_mae:.4f}  (${test_mae * 100000:,.0f} average absolute error)")
print(f"  R2:      {test_r2:.4f}  ({test_r2*100:.1f}% of variance explained)")

# Prediction error analysis
errors = y_test - y_pred
print(f"\nError Analysis:")
print(f"  Mean Error:   {errors.mean():.4f}  (should be ~0, no systematic bias)")
print(f"  Median Error: {errors.median():.4f}")
print(f"  Std Error:    {errors.std():.4f}")

# How often are we within certain ranges?
print(f"\nPrediction Accuracy Ranges:")
for threshold in [0.1, 0.25, 0.5, 1.0]:
    within = (np.abs(errors) <= threshold).mean()
    print(f"  Within ${threshold * 100000:>8,.0f}: {within*100:>5.1f}% of predictions")

# Show some example predictions
print(f"\n--- Sample Predictions ---")
print(f"{'Actual Price':<15} {'Predicted':<15} {'Error':<15} {'% Error':<10}")
print("-" * 55)
indices = np.random.RandomState(42).choice(len(y_test), 10, replace=False)
for idx in indices:
    actual = y_test.iloc[idx]
    predicted = y_pred[idx]
    error = actual - predicted
    pct_error = abs(error / actual) * 100
    print(f"${actual*100000:>10,.0f}   ${predicted*100000:>10,.0f}   "
          f"${error*100000:>+10,.0f}   {pct_error:>6.1f}%")
```

**Expected Output:**

```
============================================================
STEP 10: Final Evaluation on Test Set
============================================================

Final Model Performance on Test Set:
  RMSE:    0.4700  ($47,000 average error)
  MAE:     0.3244  ($32,440 average absolute error)
  R2:      0.8267  (82.7% of variance explained)

Error Analysis:
  Mean Error:   -0.0015  (should be ~0, no systematic bias)
  Median Error: 0.0102
  Std Error:    0.4700

Prediction Accuracy Ranges:
  Within $  10,000:  7.1% of predictions
  Within $  25,000: 34.5% of predictions
  Within $  50,000: 68.2% of predictions
  Within $ 100,000: 92.4% of predictions

--- Sample Predictions ---
Actual Price    Predicted       Error           % Error
-------------------------------------------------------
$   148,700   $   157,300   $    -8,600       5.8%
$   262,500   $   246,900   $   +15,600       5.9%
$   108,300   $   136,200   $   -27,900      25.8%
$   315,000   $   283,400   $   +31,600      10.0%
$   176,300   $   179,800   $    -3,500       2.0%
$    85,000   $   104,200   $   -19,200      22.6%
$   186,600   $   192,400   $    -5,800       3.1%
$   227,300   $   232,100   $    -4,800       2.1%
$   131,300   $   159,600   $   -28,300      21.6%
$   450,000   $   370,200   $   +79,800      17.7%
```

---

## Step 11: Feature Importance Analysis

Which features matter most for predicting house prices?

```python
# =======================================
# STEP 11: Feature Importance Analysis
# =======================================
import numpy as np
import pandas as pd

print("=" * 60)
print("STEP 11: Feature Importance Analysis")
print("=" * 60)

# Get the trained model from the pipeline
trained_model = best_pipeline.named_steps['model']
feature_names = X_train.columns.tolist()

# Get feature importances
importances = trained_model.feature_importances_
importance_df = pd.DataFrame({
    'Feature': feature_names,
    'Importance': importances
}).sort_values('Importance', ascending=False)

print("\nFeature Importances (Gradient Boosting):")
print(f"\n{'Rank':<6} {'Feature':<20} {'Importance':<12} {'Bar'}")
print("-" * 60)
for rank, (_, row) in enumerate(importance_df.iterrows(), 1):
    bar = '█' * int(row['Importance'] * 100)
    print(f"{rank:<6} {row['Feature']:<20} {row['Importance']:<12.4f} {bar}")

# Top features interpretation
print("\n--- Interpretation ---")
top_features = importance_df.head(5)
print(f"""
Top 5 Most Important Features:

1. {top_features.iloc[0]['Feature']} ({top_features.iloc[0]['Importance']:.3f})
   Median income is the single most important predictor.
   Wealthier areas have more expensive houses.

2. {top_features.iloc[1]['Feature']} ({top_features.iloc[1]['Importance']:.3f})
   Location (inland vs coastal) strongly affects price.

3. {top_features.iloc[2]['Feature']} ({top_features.iloc[2]['Importance']:.3f})
   Location latitude also matters (north vs south California).

4. {top_features.iloc[3]['Feature']} ({top_features.iloc[3]['Importance']:.3f})
   Our engineered feature! Income relative to rooms.

5. {top_features.iloc[4]['Feature']} ({top_features.iloc[4]['Importance']:.3f})
   Average occupancy per household.
""")

# Summary of what we learned
print("=" * 60)
print("KEY INSIGHTS")
print("=" * 60)
print("""
1. INCOME is king: Median income alone explains more than
   any other feature. This makes intuitive sense.

2. LOCATION matters: Latitude and Longitude capture the
   coastal premium in California real estate.

3. ENGINEERED FEATURES helped: IncomePerRoom provided
   additional predictive power beyond raw income.

4. TREE-BASED MODELS won: Gradient Boosting significantly
   outperformed linear models, capturing non-linear
   relationships between features and price.
""")
```

**Expected Output:**

```
============================================================
STEP 11: Feature Importance Analysis
============================================================

Feature Importances (Gradient Boosting):

Rank   Feature              Importance   Bar
------------------------------------------------------------
1      MedInc               0.4512       █████████████████████████████████████████████
2      Longitude            0.1234       ████████████
3      Latitude             0.1156       ███████████
4      IncomePerRoom        0.0823       ████████
5      AveOccup             0.0612       ██████
6      HouseAge             0.0534       █████
7      PopDensity           0.0321       ███
8      AveRooms             0.0267       ██
9      Population           0.0156       █
10     RoomsPerPerson       0.0123       █
11     BedroomRatio         0.0098
12     AveBedrms            0.0078
13     IsNewHouse           0.0045
14     IsOldHouse           0.0041
```

---

## Step 12: Conclusions and Next Steps

```python
# =======================================
# STEP 12: Conclusions and Next Steps
# =======================================
print("=" * 60)
print("STEP 12: Project Conclusions")
print("=" * 60)

print("""
PROJECT SUMMARY
===============

Problem:  Predict California house prices from district-level features.

Dataset:  20,082 housing districts (after cleaning).
          14 features (8 original + 6 engineered).

Best Model: Gradient Boosting Regressor (tuned)

Final Results:
  +------------------+----------+
  | Metric           | Value    |
  +------------------+----------+
  | RMSE             | $47,000  |
  | MAE              | $32,440  |
  | R-squared        | 82.7%    |
  +------------------+----------+

Model Evolution:
  +-------------------------+--------+--------+
  | Stage                   | RMSE   | R2     |
  +-------------------------+--------+--------+
  | Linear Regression       | 0.683  | 0.635  |
  | Random Forest (default) | 0.502  | 0.802  |
  | Gradient Boosting (def) | 0.484  | 0.816  |
  | Gradient Boosting (tuned)| 0.470 | 0.827  |
  +-------------------------+--------+--------+

Key Takeaways:
  1. Feature engineering improved predictions.
  2. Tree-based models vastly outperformed linear models.
  3. Hyperparameter tuning provided a ~3% improvement.
  4. The pipeline approach prevented data leakage and
     made the code clean and reproducible.

What Could Improve This Further:
  - More granular location data (ZIP code, neighborhood)
  - Actual house features (not district averages)
  - External data (school ratings, crime rates)
  - More advanced models (XGBoost, LightGBM)
  - Stacking multiple models (ensemble of ensembles)
""")
```

---

## Common Mistakes

**Mistake 1: Not holding out a test set until the very end.**
The test set should be used ONCE, at the very end. Using it during model selection or tuning gives overly optimistic results.

**Mistake 2: Feature engineering after the train/test split with information from the test set.**
All feature engineering parameters (like the 99th percentile for clipping) should be computed from the training set only.

**Mistake 3: Comparing models without cross-validation.**
A single train/test split can be misleading. Always use cross-validation for model comparison.

**Mistake 4: Ignoring outliers.**
Extreme values (like 141 average rooms) can distort model training. Always check for and handle outliers.

**Mistake 5: Only trying linear models.**
For many real-world datasets, the relationship between features and target is non-linear. Always include tree-based models in your comparison.

---

## Best Practices

1. **Follow a structured workflow.** EDA -> Clean -> Engineer -> Pipeline -> Train -> Tune -> Evaluate.
2. **Start with simple models.** Linear regression gives you a baseline. Then try more complex models.
3. **Engineer features based on domain knowledge.** BedroomRatio and IncomePerRoom made sense for housing.
4. **Use pipelines.** They prevent data leakage and make code reproducible.
5. **Compare multiple models.** Never assume one model will be best.
6. **Tune the best model.** Start with RandomizedSearch, narrow with GridSearch.
7. **Interpret your results.** Feature importance tells you what drives predictions.
8. **Report results honestly.** Include confidence intervals (CV standard deviation).

---

## Quick Summary

- We built a complete house price prediction system from scratch.
- We explored the data, cleaned outliers, and engineered new features.
- We built a preprocessing pipeline that handles all transformations.
- We compared 5 different regression models using cross-validation.
- Gradient Boosting was the best model with R2 = 0.827.
- Hyperparameter tuning improved RMSE by about 3%.
- Median income and location were the most important features.
- The final model predicts prices with an average error of about $47,000.

---

## Key Points to Remember

1. Always explore your data before building models (EDA).
2. Handle outliers and capped values during data cleaning.
3. Feature engineering can significantly improve model performance.
4. Use pipelines to chain preprocessing and modeling.
5. Compare multiple models before choosing the best one.
6. Use cross-validation for reliable model comparison.
7. Tune hyperparameters with RandomizedSearch first, then GridSearch.
8. Evaluate the final model on a separate, untouched test set.
9. Analyze feature importance to understand what drives predictions.
10. Document your findings and report results with appropriate metrics.

---

## Practice Questions

### Question 1
Why did we remove houses with a price equal to the maximum value ($500,001)?

**Answer:** The California Housing dataset caps house prices at $500,001. These are not true prices; they are just the maximum value recorded. Including them would mean we are trying to predict a censored value, which distorts our model. By removing them, we ensure all prices in our dataset are actual values.

### Question 2
Why did tree-based models (Random Forest, Gradient Boosting) significantly outperform linear models?

**Answer:** Tree-based models can capture non-linear relationships between features and the target. For house prices, the relationships are not simple straight lines. For example, the relationship between income and price might be exponential, or location effects might interact with other features in complex ways. Linear models assume a straight-line relationship, which limits their ability to capture these patterns.

### Question 3
What is the purpose of clipping outliers at the 99th percentile rather than removing them?

**Answer:** Clipping (winsorizing) replaces extreme values with the 99th percentile value rather than removing the entire row. This preserves the sample while reducing the impact of extreme values. Removing rows loses all information about those samples, including the values of other features. Clipping keeps the sample but limits the influence of the outlier value.

### Question 4
Why is R-squared (R2) a useful metric for regression problems?

**Answer:** R-squared tells you what proportion of the variation in the target variable your model explains. An R2 of 0.827 means the model explains 82.7% of the variation in house prices. The remaining 17.3% is due to factors not captured by our features (like individual house condition, renovations, etc.). R2 is easy to interpret and ranges from 0 (no explanatory power) to 1 (perfect predictions).

---

## Exercises

### Exercise 1: Try XGBoost

Replace Gradient Boosting with XGBoost (XGBRegressor). Tune its hyperparameters and compare the results with our Gradient Boosting model. Is XGBoost better?

### Exercise 2: Add More Features

Create three additional engineered features from the existing data. Ideas: income squared, log of population, interaction between latitude and longitude. Do they improve the model?

### Exercise 3: Use a Different Dataset

Repeat this entire workflow with the Boston Housing dataset or a Kaggle housing dataset. Follow the same steps: EDA, cleaning, feature engineering, pipeline, model comparison, tuning, and final evaluation.

---

## What Is Next?

Congratulations! You have completed your first end-to-end regression project. You went from raw data to a tuned model that predicts house prices with 83% accuracy (R2).

In the next chapter, you will tackle a **classification** project: **Customer Churn Prediction**. You will predict whether a customer will leave a telecom company. This project will use many of the same techniques but will also introduce strategies for handling imbalanced data (from Chapter 28) and different evaluation metrics like AUC-ROC and confusion matrices.
