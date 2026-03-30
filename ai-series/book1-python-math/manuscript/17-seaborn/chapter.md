# Chapter 17: Seaborn — Beautiful Statistical Charts

## What You Will Learn

In this chapter, you will learn how to:

- Understand what Seaborn is and how it relates to Matplotlib
- Install Seaborn on your computer
- Decide when to use Seaborn vs Matplotlib
- Create histograms and KDE plots to see data distributions
- Create box plots and violin plots to compare groups
- Make scatter plots with color-coded categories using `hue`
- Generate pair plots to see relationships between all variables at once
- Build heatmaps to visualize correlation matrices
- Create count plots for categorical data
- Set themes and color palettes to make charts look professional

## Why This Chapter Matters

Matplotlib is powerful, but making beautiful statistical charts can take many lines of code. Seaborn solves this problem.

Think of it this way:

- **Matplotlib** is like cooking from scratch. You control everything, but it takes time.
- **Seaborn** is like a meal kit. The hard work is done for you. You get a great result with less effort.

In machine learning, you need to explore your data before building models. This is called **Exploratory Data Analysis (EDA)**. Seaborn is built specifically for EDA. It creates the kinds of charts data scientists use every day — with just one or two lines of code.

```
Matplotlib:                     Seaborn:
  15 lines of code                2 lines of code
  Manual colors                   Smart defaults
  Plain looking                   Publication-ready
  Full control                    Less control, more beauty
```

---

## 17.1 What Is Seaborn?

Seaborn is a Python library built on top of Matplotlib. It specializes in **statistical visualizations**.

```
+---------------------------------------------+
|  How Seaborn and Matplotlib relate:          |
+---------------------------------------------+
|                                              |
|   Seaborn  (high-level, easy, beautiful)     |
|      |                                       |
|      | built on top of                       |
|      v                                       |
|   Matplotlib  (low-level, powerful, manual)  |
|                                              |
+---------------------------------------------+
```

Key facts about Seaborn:

- **Built on Matplotlib** — every Seaborn chart is actually a Matplotlib chart underneath
- **Designed for statistics** — histograms, distributions, correlations, comparisons
- **Works with Pandas** — pass DataFrames directly, no manual data extraction needed
- **Beautiful defaults** — charts look professional with zero customization
- **Smart features** — automatically adds colors, legends, and labels from your data

---

## 17.2 Installing Seaborn

Open your terminal and type:

```bash
pip install seaborn
```

**Expected Output:**

```
Successfully installed seaborn-0.x.x
```

Verify the installation:

```python
import seaborn as sns
print(sns.__version__)
```

**Expected Output:**

```
0.13.2
```

(Your version may differ. That is fine.)

**Why `sns`?** The convention is to import Seaborn as `sns`. This comes from the name "Samuel Norman Seaborn," a character from a TV show that the library creator liked.

---

## 17.3 When to Use Seaborn vs Matplotlib

Here is a simple decision guide:

```
+-------------------------------+-------------------------------+
|  Use Seaborn when...          |  Use Matplotlib when...       |
+-------------------------------+-------------------------------+
|  Exploring data               |  Full customization needed    |
|  Statistical charts           |  Non-statistical charts       |
|  Working with DataFrames      |  Working with raw arrays      |
|  You want quick, pretty plots |  You need pixel-level control |
|  Comparing groups/categories  |  Custom animations            |
|  Correlation analysis         |  Unusual chart types          |
+-------------------------------+-------------------------------+
```

**The great news:** You can mix them! Start with Seaborn for the chart, then use Matplotlib to fine-tune details.

```python
import seaborn as sns
import matplotlib.pyplot as plt

# Seaborn creates the chart
sns.histplot(data=[1, 2, 2, 3, 3, 3, 4, 4, 5])

# Matplotlib customizes it
plt.title("My Custom Title")    # Matplotlib adds the title
plt.xlabel("Values")            # Matplotlib adds the label

plt.show()
```

---

## 17.4 Setting Up Example Data

Seaborn comes with built-in datasets for practice. We will use two of them throughout this chapter.

```python
import seaborn as sns
import pandas as pd

# Load the "tips" dataset
tips = sns.load_dataset("tips")
print(tips.head())
```

**Expected Output:**

```
   total_bill   tip     sex smoker  day    time  size
0       16.99  1.01  Female     No  Sun  Dinner     2
1       10.34  1.66    Male     No  Sun  Dinner     3
2       21.01  3.50    Male     No  Sun  Dinner     3
3       23.68  3.31    Male     No  Sun  Dinner     2
4       24.59  3.61  Female     No  Sun  Dinner     4
```

This dataset contains restaurant bills, tips, and other information. We will use it to practice different chart types.

```python
# Load the "iris" dataset (flower measurements)
iris = sns.load_dataset("iris")
print(iris.head())
```

**Expected Output:**

```
   sepal_length  sepal_width  petal_length  petal_width species
0           5.1          3.5           1.4          0.2  setosa
1           4.9          3.0           1.4          0.2  setosa
2           4.7          3.2           1.3          0.2  setosa
3           4.6          3.1           1.5          0.2  setosa
4           5.0          3.6           1.4          0.2  setosa
```

This dataset contains measurements of three flower species. It is one of the most famous datasets in machine learning.

---

## 17.5 Histograms and KDE Plots — Seeing Distributions

A **histogram** shows how data is distributed across ranges. A **KDE plot** (Kernel Density Estimate) shows the same thing but as a smooth curve instead of bars.

**Real-life analogy:** Imagine measuring the heights of 200 people. A histogram shows how many people are 150-155cm, 155-160cm, and so on. A KDE smooths those bars into a flowing curve.

```
Histogram:                  KDE Plot:
  ##                           __
  ####                       /    \
  ######                    /      \
  ########                 /        \
  ##########             _/          \_
+------------+         +---------------+
  Short  Tall            Short    Tall
```

### histplot — The Modern Way

```python
import seaborn as sns
import matplotlib.pyplot as plt

tips = sns.load_dataset("tips")

# Histogram of total bills
sns.histplot(data=tips, x="total_bill", bins=20)
plt.title("Distribution of Total Bills")
plt.show()
```

**Expected Output:**

A histogram showing that most restaurant bills are between $10 and $25.

**Line-by-line explanation:**

```python
sns.histplot(data=tips, x="total_bill", bins=20)
```

- `data=tips` — pass the entire DataFrame
- `x="total_bill"` — which column to plot
- `bins=20` — divide the data into 20 groups

### Adding a KDE Curve on Top

```python
import seaborn as sns
import matplotlib.pyplot as plt

tips = sns.load_dataset("tips")

sns.histplot(data=tips, x="total_bill", bins=20, kde=True)
plt.title("Total Bills with KDE Curve")
plt.show()
```

**Expected Output:**

The same histogram, but now with a smooth curve drawn on top of the bars.

**Line-by-line explanation:**

```python
sns.histplot(data=tips, x="total_bill", bins=20, kde=True)
```

Adding `kde=True` draws a smooth density curve over the histogram. This helps you see the overall shape of the distribution more clearly.

### KDE Plot Alone

```python
import seaborn as sns
import matplotlib.pyplot as plt

tips = sns.load_dataset("tips")

sns.kdeplot(data=tips, x="total_bill")
plt.title("KDE of Total Bills")
plt.show()
```

**Expected Output:**

A smooth curve without any bars. The peak shows where most values are concentrated.

---

## 17.6 Box Plots — Spotting Outliers and Comparing Groups

A **box plot** shows five key statistics in one compact picture:

1. Minimum (excluding outliers)
2. First quartile (Q1) — 25th percentile
3. Median (Q2) — 50th percentile
4. Third quartile (Q3) — 75th percentile
5. Maximum (excluding outliers)

Dots beyond the "whiskers" are **outliers** — unusual values.

**Real-life analogy:** Imagine you want to compare salaries at three companies. A box plot for each company instantly shows the typical range, the middle salary, and any extremely high or low salaries.

```
  Anatomy of a Box Plot:

       o           <-- outlier (unusually high)
       |
    +--+--+
    |     |        <-- Q3 (75th percentile)
    |-----|        <-- Median (50th percentile)
    |     |        <-- Q1 (25th percentile)
    +--+--+
       |
       o           <-- outlier (unusually low)

    The box = middle 50% of data
    The line inside = median
    Whiskers = typical range
    Dots outside = outliers
```

```python
import seaborn as sns
import matplotlib.pyplot as plt

tips = sns.load_dataset("tips")

# Box plot: compare total bills by day of the week
sns.boxplot(data=tips, x="day", y="total_bill")
plt.title("Total Bills by Day")
plt.show()
```

**Expected Output:**

Four box plots side by side, one for each day (Thur, Fri, Sat, Sun). You can compare the median bill and spread across days.

**Line-by-line explanation:**

```python
sns.boxplot(data=tips, x="day", y="total_bill")
```

- `x="day"` — the category to split by (one box per day)
- `y="total_bill"` — the values to plot vertically

### Adding Hue for More Detail

```python
import seaborn as sns
import matplotlib.pyplot as plt

tips = sns.load_dataset("tips")

sns.boxplot(data=tips, x="day", y="total_bill", hue="sex")
plt.title("Total Bills by Day and Gender")
plt.show()
```

**Expected Output:**

Two boxes per day — one for male, one for female — color-coded with a legend.

```python
sns.boxplot(data=tips, x="day", y="total_bill", hue="sex")
```

`hue="sex"` splits each day's box into subgroups by gender. Seaborn automatically assigns different colors and adds a legend.

---

## 17.7 Violin Plots — Box Plot + Distribution Shape

A **violin plot** combines a box plot with a KDE plot. It shows the same summary statistics as a box plot, but also reveals the shape of the distribution.

**Real-life analogy:** If a box plot is a summary report, a violin plot is the same report with a picture attached. The wider the "violin," the more data points exist at that value.

```
Box Plot:          Violin Plot:

  +--+--+              /\
  |     |             /  \
  |-----|            |    |
  |     |            |    |
  +--+--+             \  /
                        \/

  Same stats,         Shows the SHAPE
  compact view        of the data too
```

```python
import seaborn as sns
import matplotlib.pyplot as plt

tips = sns.load_dataset("tips")

sns.violinplot(data=tips, x="day", y="total_bill")
plt.title("Total Bill Distribution by Day")
plt.show()
```

**Expected Output:**

Four violin shapes, one for each day. The width at any point shows how many bills were near that amount.

### Comparing Violin Plot with Hue

```python
import seaborn as sns
import matplotlib.pyplot as plt

tips = sns.load_dataset("tips")

sns.violinplot(data=tips, x="day", y="total_bill", hue="sex", split=True)
plt.title("Bills by Day and Gender (Split Violin)")
plt.show()
```

**Expected Output:**

Split violins where each side represents a different gender. This makes comparison very easy.

**Line-by-line explanation:**

```python
sns.violinplot(data=tips, x="day", y="total_bill", hue="sex", split=True)
```

`split=True` puts both groups in the same violin — one on the left half, one on the right half. This saves space and makes comparisons clearer.

---

## 17.8 Scatter Plots with Hue — Color-Coded Categories

Seaborn's scatter plot can automatically color-code points by category. This is incredibly powerful for spotting patterns.

**Real-life analogy:** Imagine plotting house prices vs. house size. Now color each dot by neighborhood. Suddenly you can see that the same-size house costs more in some neighborhoods than others.

```python
import seaborn as sns
import matplotlib.pyplot as plt

tips = sns.load_dataset("tips")

sns.scatterplot(data=tips, x="total_bill", y="tip", hue="time")
plt.title("Tips vs Total Bill (Lunch vs Dinner)")
plt.show()
```

**Expected Output:**

A scatter plot with dots in two colors — one for Lunch, one for Dinner. A legend appears automatically.

**Line-by-line explanation:**

```python
sns.scatterplot(data=tips, x="total_bill", y="tip", hue="time")
```

- `x="total_bill"` — horizontal position of each dot
- `y="tip"` — vertical position
- `hue="time"` — color of each dot based on Lunch or Dinner

### Adding More Dimensions

You can map even more information:

```python
import seaborn as sns
import matplotlib.pyplot as plt

tips = sns.load_dataset("tips")

sns.scatterplot(
    data=tips,
    x="total_bill",
    y="tip",
    hue="time",      # color = meal time
    size="size",      # dot size = party size
    style="sex"       # dot shape = gender
)
plt.title("Tips Analysis")
plt.show()
```

**Expected Output:**

Each dot now conveys four pieces of information: x-position (bill), y-position (tip), color (time), size (party), and shape (gender).

---

## 17.9 Pair Plots — See Everything at Once

A **pair plot** creates scatter plots for every pair of numeric columns in your data. It is the ultimate exploration tool.

**Real-life analogy:** Imagine you have 4 measurements for each flower (length, width, etc.). A pair plot creates 4 x 4 = 16 mini-charts showing every possible relationship between those measurements.

```python
import seaborn as sns
import matplotlib.pyplot as plt

iris = sns.load_dataset("iris")

sns.pairplot(iris, hue="species")
plt.show()
```

**Expected Output:**

A 4x4 grid of charts. The diagonal shows histograms (one variable's distribution). Off-diagonal cells show scatter plots of every pair of variables. Points are color-coded by flower species.

```
              sepal_len  sepal_wid  petal_len  petal_wid
           +----------+----------+----------+----------+
sepal_len  | hist     | scatter  | scatter  | scatter  |
           +----------+----------+----------+----------+
sepal_wid  | scatter  | hist     | scatter  | scatter  |
           +----------+----------+----------+----------+
petal_len  | scatter  | scatter  | hist     | scatter  |
           +----------+----------+----------+----------+
petal_wid  | scatter  | scatter  | scatter  | hist     |
           +----------+----------+----------+----------+

Each scatter is color-coded by species (setosa, versicolor, virginica)
```

**Line-by-line explanation:**

```python
sns.pairplot(iris, hue="species")
```

One line of code creates 16 charts. `hue="species"` colors each point by flower type. The diagonal cells show the distribution of each variable for each species.

**Warning:** Pair plots can be slow with many columns. If your DataFrame has 20 numeric columns, it creates 400 charts. Use `vars=` to select specific columns:

```python
sns.pairplot(iris, hue="species", vars=["sepal_length", "petal_length"])
```

This creates only a 2x2 grid instead of 4x4.

---

## 17.10 Heatmaps — Visualizing Correlation Matrices

A **heatmap** uses color to represent numbers in a table. The most common use in data science is visualizing a **correlation matrix** — a table showing how strongly each pair of variables is related.

**Real-life analogy:** Think of a weather map where red means hot and blue means cold. A heatmap does the same thing but for any numbers in a table.

```
Correlation values:         Heatmap:
                            (darker = stronger relationship)

        A     B     C           A     B     C
  A   1.00  0.85  0.10     A  ████  ███░  ░░░░
  B   0.85  1.00  0.30     B  ███░  ████  ░░▓░
  C   0.10  0.30  1.00     C  ░░░░  ░░▓░  ████

  A and B are strongly related (0.85)
  A and C are barely related (0.10)
```

### Step 1: Calculate the Correlation Matrix

```python
import seaborn as sns
import pandas as pd

iris = sns.load_dataset("iris")

# Select only numeric columns
numeric_iris = iris.select_dtypes(include="number")

# Calculate correlations
correlation = numeric_iris.corr()
print(correlation)
```

**Expected Output:**

```
              sepal_length  sepal_width  petal_length  petal_width
sepal_length      1.000000    -0.117570      0.871754     0.817941
sepal_width      -0.117570     1.000000     -0.428440    -0.366126
petal_length      0.871754    -0.428440      1.000000     0.962865
petal_width       0.817941    -0.366126      0.962865     1.000000
```

### Step 2: Draw the Heatmap

```python
import seaborn as sns
import matplotlib.pyplot as plt

iris = sns.load_dataset("iris")
numeric_iris = iris.select_dtypes(include="number")
correlation = numeric_iris.corr()

# Create the heatmap
sns.heatmap(correlation, annot=True, cmap="coolwarm", center=0)
plt.title("Iris Feature Correlations")
plt.show()
```

**Expected Output:**

A colorful grid where each cell shows a number (the correlation value). Warm colors (red) mean positive correlation. Cool colors (blue) mean negative correlation.

**Line-by-line explanation:**

```python
sns.heatmap(correlation, annot=True, cmap="coolwarm", center=0)
```

- `correlation` — the data to visualize (a table of numbers)
- `annot=True` — show the actual numbers inside each cell
- `cmap="coolwarm"` — color scheme: blue for negative, white for zero, red for positive
- `center=0` — center the color scale at zero

### Common Color Maps

```
"coolwarm"    blue(-) --- white(0) --- red(+)     best for correlations
"viridis"     purple --- green --- yellow           default, good for all
"YlOrRd"      yellow --- orange --- red             good for positive data
"Blues"        light blue --- dark blue              good for counts
```

---

## 17.11 Count Plots — Counting Categories

A **count plot** shows how many items are in each category. It is like a bar chart, but Seaborn counts for you automatically.

**Real-life analogy:** Imagine counting how many red, blue, and green cars are in a parking lot. A count plot does that counting and drawing in one step.

```python
import seaborn as sns
import matplotlib.pyplot as plt

tips = sns.load_dataset("tips")

# Count how many records for each day
sns.countplot(data=tips, x="day")
plt.title("Number of Records per Day")
plt.show()
```

**Expected Output:**

A bar chart showing the count for each day. Saturday has the most records.

### Count Plot with Hue

```python
import seaborn as sns
import matplotlib.pyplot as plt

tips = sns.load_dataset("tips")

sns.countplot(data=tips, x="day", hue="sex")
plt.title("Diners by Day and Gender")
plt.show()
```

**Expected Output:**

Two bars per day, one for male and one for female, showing the count of each.

---

## 17.12 Setting Themes and Color Palettes

Seaborn makes it easy to change the overall look of your charts.

### Themes

```python
import seaborn as sns
import matplotlib.pyplot as plt

tips = sns.load_dataset("tips")

# Set the theme BEFORE creating the plot
sns.set_theme(style="whitegrid")

sns.scatterplot(data=tips, x="total_bill", y="tip")
plt.title("Whitegrid Theme")
plt.show()
```

Available themes:

```
"darkgrid"    Gray background + white gridlines     (default)
"whitegrid"   White background + gray gridlines     (clean)
"dark"        Gray background, no gridlines         (minimal)
"white"       White background, no gridlines        (cleanest)
"ticks"       White background + tick marks          (publication)
```

```python
# Try different themes
sns.set_theme(style="darkgrid")     # default look
sns.set_theme(style="whitegrid")    # clean, professional
sns.set_theme(style="ticks")        # minimal, for papers
```

### Color Palettes

```python
import seaborn as sns
import matplotlib.pyplot as plt

tips = sns.load_dataset("tips")

# Set a color palette
sns.set_palette("pastel")

sns.countplot(data=tips, x="day", hue="sex")
plt.title("Pastel Color Palette")
plt.show()
```

Popular palettes:

```
"deep"        Rich, saturated colors      (default)
"pastel"      Soft, light colors          (gentle)
"bright"      Vivid, bold colors          (attention-grabbing)
"dark"        Deep, dark colors           (serious)
"colorblind"  Colors safe for colorblind  (accessible)
"Set2"        Distinct, pleasant colors   (good for categories)
```

### Combining Theme and Palette

```python
import seaborn as sns
import matplotlib.pyplot as plt

# Set both theme and palette
sns.set_theme(style="whitegrid", palette="colorblind")

tips = sns.load_dataset("tips")
sns.boxplot(data=tips, x="day", y="total_bill", hue="sex")
plt.title("Professional Look")
plt.show()
```

**Line-by-line explanation:**

```python
sns.set_theme(style="whitegrid", palette="colorblind")
```

Sets the background style to white with gridlines, and uses colors that are distinguishable by people with color vision deficiency. This is a best practice for inclusive data visualization.

### Resetting to Defaults

```python
sns.reset_defaults()    # Go back to Seaborn defaults
sns.reset_orig()        # Go back to Matplotlib defaults
```

---

## Common Mistakes

**Mistake 1: Forgetting to import Matplotlib for `plt.show()`.**

```python
import seaborn as sns

sns.histplot(data=tips, x="total_bill")
plt.show()    # ERROR! plt is not defined
```

**Fix:** Always import both:

```python
import seaborn as sns
import matplotlib.pyplot as plt
```

---

**Mistake 2: Passing raw lists when column names are expected.**

```python
sns.boxplot(data=tips, x=[1, 2, 3], y="total_bill")    # ERROR!
```

**Fix:** The `x` and `y` parameters should be column names (strings) when using `data=`:

```python
sns.boxplot(data=tips, x="day", y="total_bill")    # Correct
```

---

**Mistake 3: Using `distplot()` — it is deprecated.**

```python
sns.distplot(tips["total_bill"])    # WARNING! Deprecated
```

**Fix:** Use `histplot()` or `kdeplot()` instead:

```python
sns.histplot(data=tips, x="total_bill", kde=True)    # Modern way
```

---

**Mistake 4: Pair plot on a large dataset takes forever.**

```python
# DataFrame with 50 columns and 100,000 rows
sns.pairplot(huge_dataframe)    # Very slow!
```

**Fix:** Select only the columns you care about:

```python
sns.pairplot(huge_dataframe, vars=["col1", "col2", "col3"])
```

---

**Mistake 5: Heatmap numbers are hard to read.**

```python
sns.heatmap(correlation)    # No numbers shown
```

**Fix:** Add `annot=True` and optionally format the numbers:

```python
sns.heatmap(correlation, annot=True, fmt=".2f")    # Shows 2 decimal places
```

---

## Best Practices

1. **Start with `sns.set_theme()`** at the top of your notebook. Set it once and all charts look consistent.

2. **Use `hue` to add meaning.** Color-coding by category is one of Seaborn's biggest strengths.

3. **Use `colorblind` palette** when sharing charts with others. About 8% of men have some form of color vision deficiency.

4. **Pair plots first, details later.** When exploring a new dataset, `sns.pairplot()` gives you a complete overview in one line.

5. **Always add `annot=True` to heatmaps.** Without the numbers, readers cannot tell the exact correlation values.

6. **Mix Seaborn and Matplotlib.** Use Seaborn for the chart, Matplotlib for titles and labels.

7. **Choose the right chart for the question:**
   - "What is the distribution?" -> histogram, KDE, violin
   - "How do groups compare?" -> box plot, violin plot
   - "Is there a relationship?" -> scatter plot, heatmap
   - "How many of each?" -> count plot

---

## Quick Summary

```
+----------------------------------------------------------+
|  Seaborn Quick Reference                                  |
+----------------------------------------------------------+
|  Import:        import seaborn as sns                     |
|                                                           |
|  Distribution:  sns.histplot()    sns.kdeplot()           |
|  Comparison:    sns.boxplot()     sns.violinplot()        |
|  Relationship:  sns.scatterplot() sns.heatmap()           |
|  Counting:      sns.countplot()                           |
|  Overview:      sns.pairplot()                            |
|                                                           |
|  Themes:        sns.set_theme(style="whitegrid")          |
|  Palettes:      sns.set_palette("colorblind")             |
|  Color-code:    hue="column_name"                         |
|                                                           |
|  Works with:    Pandas DataFrames                         |
|  Built on:      Matplotlib (use plt for customization)    |
+----------------------------------------------------------+
```

---

## Key Points to Remember

1. **Seaborn** is built on Matplotlib. It makes statistical charts easier and more beautiful.

2. **`import seaborn as sns`** is the universal convention.

3. **`hue`** is Seaborn's secret weapon. It color-codes data by category with zero effort.

4. **`sns.pairplot()`** is the fastest way to explore relationships in a dataset.

5. **`sns.heatmap()` with `annot=True`** is the standard way to visualize correlations.

6. **Use `histplot()` instead of `distplot()`** — the old function is deprecated.

7. **Seaborn works best with Pandas DataFrames.** Pass `data=df` and column names as strings.

---

## Practice Questions

**Question 1:** What is the difference between a box plot and a violin plot?

**Answer:** A box plot shows five summary statistics (min, Q1, median, Q3, max) and outliers as a simple box-and-whisker diagram. A violin plot shows the same information plus the full shape of the data distribution. The wider a violin is at any point, the more data exists at that value. Violin plots give more detail but take more space.

---

**Question 2:** What does the `hue` parameter do in Seaborn?

**Answer:** The `hue` parameter color-codes your data points by a categorical variable. For example, `hue="species"` assigns a different color to each species. Seaborn automatically adds a legend. This lets you compare groups within the same chart.

---

**Question 3:** Why is `sns.pairplot()` useful for data exploration?

**Answer:** `sns.pairplot()` creates scatter plots for every pair of numeric columns in your DataFrame, with histograms on the diagonal. This gives you a complete overview of all relationships in your data with just one line of code. It is often the first chart data scientists create when exploring a new dataset.

---

**Question 4:** What is a heatmap most commonly used for in data science?

**Answer:** A heatmap is most commonly used to visualize a correlation matrix. Each cell shows how strongly two variables are related, using color intensity. Values near +1 (strong positive) or -1 (strong negative) have intense colors. Values near 0 (no relationship) have neutral colors. This helps you quickly identify which variables are related.

---

**Question 5:** When should you use Seaborn instead of Matplotlib?

**Answer:** Use Seaborn when you are doing statistical data exploration, working with Pandas DataFrames, need color-coded categories (hue), or want professional-looking charts with minimal code. Use Matplotlib when you need full control over every detail, are making non-statistical charts, or need custom chart types that Seaborn does not support.

---

## Exercises

### Exercise 1: Distribution Explorer

Using the `tips` dataset:

1. Create a histogram of the `tip` column with a KDE curve
2. Create a box plot comparing `tip` by `day`
3. Create a violin plot comparing `tip` by `day`, split by `sex`

Put all three in separate figures. Use the `whitegrid` theme.

**Hint:** Call `sns.set_theme(style="whitegrid")` once at the top. Use `kde=True` for the histogram. Use `split=True` in the violin plot.

---

### Exercise 2: Iris Correlation Analysis

Using the `iris` dataset:

1. Create a pair plot color-coded by `species`
2. Calculate the correlation matrix (numeric columns only)
3. Create a heatmap of the correlations with `annot=True` and the `"coolwarm"` color map

Which two features have the strongest correlation?

**Hint:** Use `iris.select_dtypes(include="number").corr()` for the correlation matrix.

---

### Exercise 3: Tips Deep Dive

Create a figure that tells a story about the `tips` dataset:

1. Scatter plot of `total_bill` vs `tip`, color-coded by `time` (Lunch vs Dinner)
2. Count plot showing how many records exist for each `day`, split by `smoker` status
3. Box plot comparing `total_bill` by `day`

Use the `"colorblind"` palette for accessibility.

**Hint:** Set the palette with `sns.set_palette("colorblind")`. Create separate figures for each chart or use `plt.subplots()` for a dashboard.

---

## What Is Next?

You now know how to create beautiful statistical charts with Seaborn. In the next chapter, you will learn about **Jupyter Notebooks and Google Colab** — interactive environments where you can write code, see charts, and take notes all in one place. These tools are where data scientists spend most of their time.
