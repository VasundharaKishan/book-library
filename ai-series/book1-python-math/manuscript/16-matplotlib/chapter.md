# Chapter 16: Matplotlib — Drawing Charts with Code

## What You Will Learn

In this chapter, you will learn how to:

- Understand what Matplotlib is and why it matters
- Install Matplotlib on your computer
- Create line plots, scatter plots, bar charts, and histograms
- Understand the figure and axes system
- Add titles, labels, and legends to your charts
- Customize colors, line styles, and markers
- Create subplots (multiple charts in one image)
- Save your charts to image files
- Understand what `plt.show()` does

## Why This Chapter Matters

Imagine you have a spreadsheet with 10,000 rows of numbers. Can you spot a trend by staring at the numbers? Probably not. But turn those numbers into a chart, and the pattern jumps out instantly.

In AI and machine learning, you will constantly need to:

- See how your model is improving during training
- Understand the shape of your data before building a model
- Compare results from different experiments
- Communicate your findings to other people

Matplotlib is Python's most popular charting library. It is the foundation that many other visualization tools are built on. Learning Matplotlib is like learning to drive — once you know it, you can go anywhere.

```
Without Charts:              With Charts:

  23, 45, 67, 89, 91          |         *
  12, 34, 56, 78, 95          |       *
  ...10,000 more rows...      |     *
                               |   *
  "I see nothing."             | *
                               +----------
                               "Clear upward trend!"
```

---

## 16.1 What Is Matplotlib?

Matplotlib is a Python library that draws charts and graphs. Think of it as a digital sketchpad for data.

```
+------------------------------------------+
|           What Matplotlib Does            |
+------------------------------------------+
|                                           |
|   Your Data   --->   Matplotlib   --->   Chart
|   [1,2,3,4]          (the artist)        (picture)
|   [10,20,30,40]                           |
|                                           |
+------------------------------------------+
```

The name "Matplotlib" comes from "MATLAB" (a math tool) + "plot" + "library." It was created to bring MATLAB-style plotting to Python.

Key facts:

- **Free and open source** — no cost to use
- **Works everywhere** — Windows, Mac, Linux
- **Huge community** — millions of users, tons of examples online
- **Foundation library** — Seaborn, Pandas plotting, and others are built on top of it

---

## 16.2 Installing Matplotlib

Open your terminal or command prompt and type:

```bash
pip install matplotlib
```

**Expected Output:**

```
Successfully installed matplotlib-3.x.x
```

To verify the installation:

```python
import matplotlib
print(matplotlib.__version__)
```

**Expected Output:**

```
3.8.2
```

(Your version number may be different. That is fine.)

---

## 16.3 Your First Line Plot

A line plot connects data points with a line. It is perfect for showing trends over time.

**Real-life analogy:** Think of a line plot like tracking your daily step count on a fitness app. Each day is a point. The line connecting them shows whether you are walking more or less over time.

```python
import matplotlib.pyplot as plt

# Data: days of the week and steps walked
days = [1, 2, 3, 4, 5, 6, 7]
steps = [3000, 4500, 4000, 7000, 6500, 8000, 5000]

# Create the line plot
plt.plot(days, steps)

# Add labels and title
plt.xlabel("Day of the Week")
plt.ylabel("Steps Walked")
plt.title("My Weekly Step Count")

# Display the chart
plt.show()
```

**Expected Output:**

A window pops up showing a line chart. The x-axis shows days 1 through 7. The y-axis shows step counts. A blue line connects the points.

```
Steps
8000 |          *
7000 |       *     *
6000 |
5000 |    *     *        *
4000 |      *
3000 | *
     +--+--+--+--+--+--+--
       1  2  3  4  5  6  7
              Day
```

**Line-by-line explanation:**

```python
import matplotlib.pyplot as plt
```

We import the `pyplot` module from Matplotlib. We give it the short name `plt`. This is a universal convention — almost every Python programmer uses `plt`.

```python
days = [1, 2, 3, 4, 5, 6, 7]
steps = [3000, 4500, 4000, 7000, 6500, 8000, 5000]
```

We create two lists. `days` is our x-axis data. `steps` is our y-axis data. Both lists must have the same length.

```python
plt.plot(days, steps)
```

This tells Matplotlib to draw a line plot. The first argument is x-values. The second is y-values.

```python
plt.xlabel("Day of the Week")
plt.ylabel("Steps Walked")
plt.title("My Weekly Step Count")
```

These add text labels. `xlabel` labels the x-axis. `ylabel` labels the y-axis. `title` adds a title at the top.

```python
plt.show()
```

This opens a window and displays the chart. Without this line, nothing appears on screen. More on this later.

---

## 16.4 Scatter Plots

A scatter plot shows individual points without connecting them. It is great for seeing relationships between two things.

**Real-life analogy:** Imagine plotting the height and weight of 50 people. Each person is a dot. The scatter plot reveals whether taller people tend to weigh more.

```python
import matplotlib.pyplot as plt

# Study hours and exam scores for 10 students
hours_studied = [1, 2, 3, 3, 4, 5, 5, 6, 7, 8]
exam_scores =   [40, 50, 55, 60, 65, 70, 75, 80, 85, 95]

# Create scatter plot
plt.scatter(hours_studied, exam_scores)

# Add labels and title
plt.xlabel("Hours Studied")
plt.ylabel("Exam Score")
plt.title("Study Hours vs Exam Scores")

# Display
plt.show()
```

**Expected Output:**

A chart with individual dots. More study hours generally means higher scores.

```
Score
 95 |                         *
 85 |                      *
 80 |                   *
 75 |                *
 70 |             *
 65 |          *
 60 |        *
 55 |      *
 50 |   *
 40 | *
    +--+--+--+--+--+--+--+--+--
      1  2  3  4  5  6  7  8
           Hours Studied
```

**Line-by-line explanation:**

```python
plt.scatter(hours_studied, exam_scores)
```

`plt.scatter()` works like `plt.plot()`, but it draws dots instead of a connected line. Use `scatter` when your data points are independent (not a continuous sequence).

---

## 16.5 Bar Charts

A bar chart uses rectangular bars to compare categories. Each bar's height represents a value.

**Real-life analogy:** Think of a bar chart like a shelf of books lined up by height. You can instantly see which book is tallest.

```python
import matplotlib.pyplot as plt

# Favorite programming languages (survey results)
languages = ["Python", "JavaScript", "Java", "C++", "Go"]
votes = [45, 30, 25, 15, 10]

# Create bar chart
plt.bar(languages, votes)

# Add labels and title
plt.xlabel("Programming Language")
plt.ylabel("Number of Votes")
plt.title("Favorite Programming Languages Survey")

# Display
plt.show()
```

**Expected Output:**

Five vertical bars, with Python being the tallest.

```
Votes
  45 | ####
  30 |      ####
  25 |           ####
  15 |                ####
  10 |                     ####
     +------+------+------+------+------
      Python  JS    Java   C++    Go
```

**Horizontal bar chart:**

You can also make bars go sideways using `plt.barh()`:

```python
import matplotlib.pyplot as plt

languages = ["Python", "JavaScript", "Java", "C++", "Go"]
votes = [45, 30, 25, 15, 10]

# Horizontal bar chart
plt.barh(languages, votes)
plt.xlabel("Number of Votes")
plt.title("Favorite Programming Languages Survey")
plt.show()
```

**Expected Output:**

The same data, but bars go left to right instead of bottom to top.

---

## 16.6 Histograms

A histogram shows the distribution of data — how often each range of values appears.

**Real-life analogy:** Imagine sorting 100 students by their test scores into bins: 0-10, 10-20, 20-30, and so on. A histogram shows how many students fall into each bin.

```
Regular bar chart:             Histogram:
(compares categories)          (shows distribution)

 Python  JS  Java               60-70  70-80  80-90
  ####  ###  ##                  ###   ######  ####

"Which is most popular?"       "Where do most scores fall?"
```

```python
import matplotlib.pyplot as plt
import numpy as np

# Generate 1000 random test scores (normal distribution)
np.random.seed(42)
scores = np.random.normal(loc=75, scale=10, size=1000)

# Create histogram
plt.hist(scores, bins=20, edgecolor="black")

# Add labels and title
plt.xlabel("Test Score")
plt.ylabel("Number of Students")
plt.title("Distribution of Test Scores")

# Display
plt.show()
```

**Expected Output:**

A bell-shaped chart. Most scores cluster around 75. Fewer students score very high or very low.

```
Students
  120 |           ####
  100 |         ########
   80 |       ############
   60 |     ################
   40 |   ####################
   20 | ########################
      +--+--+--+--+--+--+--+--+--
        45  55  65  75  85  95 105
                Test Score
```

**Line-by-line explanation:**

```python
np.random.seed(42)
```

Sets a random seed so we get the same "random" numbers every time. This makes the example reproducible.

```python
scores = np.random.normal(loc=75, scale=10, size=1000)
```

Generates 1000 random numbers centered around 75 with a spread (standard deviation) of 10. This simulates realistic test scores.

```python
plt.hist(scores, bins=20, edgecolor="black")
```

`plt.hist()` creates the histogram. `bins=20` means divide the data into 20 groups. `edgecolor="black"` adds black borders around each bar so they are easy to see.

---

## 16.7 Figure and Axes — How Matplotlib Really Works

So far we used `plt.plot()`, `plt.scatter()`, and so on. This is the **quick style** (called the "pyplot interface"). But Matplotlib has a deeper structure.

**Real-life analogy:** Think of it like painting:

- **Figure** = the canvas (the whole image)
- **Axes** = one drawing area on the canvas (where you actually paint)

You can have one canvas with multiple drawing areas.

```
+----------------------------------------------+
|  FIGURE (the whole canvas)                    |
|                                               |
|   +------------------+  +------------------+  |
|   |   AXES 1         |  |   AXES 2         |  |
|   |   (one chart)    |  |   (another chart) |  |
|   |                  |  |                   |  |
|   +------------------+  +------------------+  |
|                                               |
+----------------------------------------------+
```

Here is the **explicit** way to create charts:

```python
import matplotlib.pyplot as plt

# Create a figure and one axes
fig, ax = plt.subplots()

# Use the axes to plot
days = [1, 2, 3, 4, 5]
steps = [3000, 5000, 4000, 7000, 6000]

ax.plot(days, steps)
ax.set_xlabel("Day")
ax.set_ylabel("Steps")
ax.set_title("Daily Steps")

plt.show()
```

**Expected Output:**

The same kind of line chart as before. The difference is in how we wrote the code.

**Line-by-line explanation:**

```python
fig, ax = plt.subplots()
```

This creates a Figure (the canvas) and one Axes (the drawing area). We store them in `fig` and `ax`.

```python
ax.plot(days, steps)
```

Instead of `plt.plot()`, we call `ax.plot()`. This tells the specific axes to draw the line.

```python
ax.set_xlabel("Day")
ax.set_ylabel("Steps")
ax.set_title("Daily Steps")
```

Notice the methods start with `set_`. When using axes, it is `set_xlabel()` instead of `plt.xlabel()`.

**When to use which style:**

```
plt.plot() style:          fig, ax style:
- Quick and simple         - More control
- One chart                - Multiple charts (subplots)
- Exploration              - Publication-quality figures
- Notebooks                - Complex layouts
```

Both styles are fine. For beginners, `plt.plot()` is easier. As you grow, you will use the `fig, ax` style more.

---

## 16.8 Adding Titles, Labels, and Legends

Labels tell the reader what they are looking at. Without labels, a chart is just meaningless lines and dots.

**Legends** are important when you have multiple lines or datasets on the same chart.

```python
import matplotlib.pyplot as plt

months = [1, 2, 3, 4, 5, 6]
alice_sales = [20, 35, 30, 50, 45, 60]
bob_sales =   [15, 25, 40, 35, 55, 50]

# Plot two lines with labels
plt.plot(months, alice_sales, label="Alice")
plt.plot(months, bob_sales, label="Bob")

# Add title and axis labels
plt.title("Monthly Sales Comparison")
plt.xlabel("Month")
plt.ylabel("Sales (units)")

# Add the legend
plt.legend()

plt.show()
```

**Expected Output:**

Two lines on the same chart. A small box (the legend) shows which color belongs to Alice and which to Bob.

```
Sales
  60 |                    A
  55 |                 B
  50 |          A         B
  45 |             A
  40 |       B
  35 |    A     B
  30 |      A
  25 |    B
  20 | A
  15 | B
     +--+--+--+--+--+--+
       1  2  3  4  5  6
            Month

     Legend: A = Alice, B = Bob
```

**Line-by-line explanation:**

```python
plt.plot(months, alice_sales, label="Alice")
```

The `label="Alice"` parameter gives this line a name. The name appears in the legend.

```python
plt.legend()
```

This tells Matplotlib to display the legend box. Without calling `plt.legend()`, the labels you set with `label=` will not appear.

**Legend placement:**

You can control where the legend appears:

```python
plt.legend(loc="upper left")    # top-left corner
plt.legend(loc="lower right")   # bottom-right corner
plt.legend(loc="best")          # Matplotlib picks the best spot (default)
```

---

## 16.9 Customizing Colors and Styles

You can change colors, line styles, marker shapes, and line widths.

### Colors

```python
import matplotlib.pyplot as plt

x = [1, 2, 3, 4, 5]
y = [10, 20, 15, 25, 30]

# Different ways to set colors
plt.plot(x, y, color="red")           # Color name
plt.plot(x, y, color="#FF5733")       # Hex code
plt.plot(x, y, color="green")        # Another color name
```

Common color names: `"red"`, `"blue"`, `"green"`, `"orange"`, `"purple"`, `"black"`, `"gray"`.

### Line Styles

```python
import matplotlib.pyplot as plt

x = [1, 2, 3, 4, 5]

plt.plot(x, [10, 20, 15, 25, 30], linestyle="-",  label="Solid")
plt.plot(x, [8, 18, 13, 23, 28],  linestyle="--", label="Dashed")
plt.plot(x, [6, 16, 11, 21, 26],  linestyle="-.", label="Dash-dot")
plt.plot(x, [4, 14, 9, 19, 24],   linestyle=":",  label="Dotted")

plt.legend()
plt.title("Line Styles")
plt.show()
```

**Expected Output:**

Four lines, each with a different line style.

```
Line styles available:
  "-"   ________________   solid (default)
  "--"  _ _ _ _ _ _ _ _    dashed
  "-."  _._._._._._._     dash-dot
  ":"   ................   dotted
```

### Markers

Markers are shapes at each data point.

```python
import matplotlib.pyplot as plt

x = [1, 2, 3, 4, 5]
y = [10, 20, 15, 25, 30]

plt.plot(x, y, marker="o", color="blue")     # circles
plt.show()
```

Common markers:

```
"o"   circle        "s"   square
"^"   triangle up   "v"   triangle down
"*"   star          "+"   plus sign
"x"   x mark        "D"   diamond
```

### Combining Everything

You can use a **format string** shortcut:

```python
import matplotlib.pyplot as plt

x = [1, 2, 3, 4, 5]
y = [10, 20, 15, 25, 30]

# "r--o" means: red, dashed line, circle markers
plt.plot(x, y, "r--o")
plt.title("Red Dashed Line with Circle Markers")
plt.show()
```

The format string pattern is: `"[color][linestyle][marker]"`.

- `"r--o"` = red + dashed + circles
- `"g-s"` = green + solid + squares
- `"b:^"` = blue + dotted + triangles

### Line Width and Marker Size

```python
import matplotlib.pyplot as plt

x = [1, 2, 3, 4, 5]
y = [10, 20, 15, 25, 30]

plt.plot(x, y, color="blue", linewidth=3, marker="o", markersize=10)
plt.title("Thick Line with Large Markers")
plt.show()
```

---

## 16.10 Subplots — Multiple Charts in One Image

Sometimes you want to show several charts side by side.

**Real-life analogy:** Think of a dashboard in a car. You see speed, fuel level, and engine temperature all at once. Each gauge is a separate "subplot."

```python
import matplotlib.pyplot as plt

# Create a figure with 2 charts side by side (1 row, 2 columns)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

# Left chart: Line plot
days = [1, 2, 3, 4, 5]
steps = [3000, 5000, 4000, 7000, 6000]
ax1.plot(days, steps, color="blue", marker="o")
ax1.set_title("Daily Steps")
ax1.set_xlabel("Day")
ax1.set_ylabel("Steps")

# Right chart: Bar chart
fruits = ["Apple", "Banana", "Cherry"]
counts = [30, 45, 20]
ax2.bar(fruits, counts, color="orange")
ax2.set_title("Fruit Sales")
ax2.set_xlabel("Fruit")
ax2.set_ylabel("Count")

# Adjust spacing so titles do not overlap
plt.tight_layout()
plt.show()
```

**Expected Output:**

Two charts appear side by side in one window. The left shows a line chart. The right shows a bar chart.

```
+-----------------------------+-----------------------------+
|   Daily Steps               |   Fruit Sales               |
|                             |                             |
|   Steps                     |   Count                     |
|   7000|       *             |   45|      ####             |
|   5000|  *       *          |   30| ####                  |
|   4000|     *               |   20|           ####        |
|   3000|*                    |     +------+------+------   |
|       +--+--+--+--+--      |      Apple Banana Cherry    |
|        1  2  3  4  5        |                             |
+-----------------------------+-----------------------------+
```

**Line-by-line explanation:**

```python
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
```

`plt.subplots(1, 2)` means 1 row, 2 columns. This creates two axes objects: `ax1` (left) and `ax2` (right). `figsize=(10, 4)` sets the total image size in inches (width, height).

```python
plt.tight_layout()
```

This automatically adjusts spacing between subplots so nothing overlaps. Always include this when using subplots.

### Grid of Subplots

For a 2x2 grid:

```python
import matplotlib.pyplot as plt
import numpy as np

fig, axes = plt.subplots(2, 2, figsize=(10, 8))

# Top-left
axes[0, 0].plot([1, 2, 3], [1, 4, 9])
axes[0, 0].set_title("Line Plot")

# Top-right
axes[0, 1].scatter([1, 2, 3, 4], [10, 20, 15, 25])
axes[0, 1].set_title("Scatter Plot")

# Bottom-left
axes[1, 0].bar(["A", "B", "C"], [5, 7, 3])
axes[1, 0].set_title("Bar Chart")

# Bottom-right
data = np.random.normal(0, 1, 500)
axes[1, 1].hist(data, bins=15, edgecolor="black")
axes[1, 1].set_title("Histogram")

plt.tight_layout()
plt.show()
```

**Expected Output:**

A 2x2 grid with four different chart types.

```
+-------------------+-------------------+
|   Line Plot       |   Scatter Plot    |
|      /            |     *      *      |
|    /              |   *    *          |
|  /                |                   |
+-------------------+-------------------+
|   Bar Chart       |   Histogram       |
|  ### ### ###      |      ####         |
|  ### ###          |    ########       |
|  ###              |  ############     |
+-------------------+-------------------+
```

**Line-by-line explanation:**

```python
fig, axes = plt.subplots(2, 2, figsize=(10, 8))
```

With a grid, `axes` becomes a 2D array. Access individual axes with `axes[row, col]`.

```python
axes[0, 0]   # top-left
axes[0, 1]   # top-right
axes[1, 0]   # bottom-left
axes[1, 1]   # bottom-right
```

---

## 16.11 Saving Plots to Files

You can save your charts as image files instead of (or in addition to) displaying them on screen.

```python
import matplotlib.pyplot as plt

x = [1, 2, 3, 4, 5]
y = [10, 20, 15, 25, 30]

plt.plot(x, y, color="green", marker="s")
plt.title("Saved Chart Example")
plt.xlabel("X values")
plt.ylabel("Y values")

# Save to a file
plt.savefig("my_chart.png")

print("Chart saved!")
```

**Expected Output:**

```
Chart saved!
```

A file called `my_chart.png` appears in your current folder.

**Important:** Call `plt.savefig()` BEFORE `plt.show()`. If you call `plt.show()` first, it clears the figure, and `plt.savefig()` saves a blank image.

```
CORRECT order:                WRONG order:

plt.plot(x, y)                plt.plot(x, y)
plt.savefig("chart.png")      plt.show()        # clears figure!
plt.show()                    plt.savefig("chart.png")  # saves blank!
```

### Supported File Formats

```python
plt.savefig("chart.png")     # PNG  (good for web)
plt.savefig("chart.jpg")     # JPEG (good for photos)
plt.savefig("chart.pdf")     # PDF  (good for papers)
plt.savefig("chart.svg")     # SVG  (good for web, scalable)
```

### Controlling Quality

```python
# High resolution (300 dots per inch)
plt.savefig("chart.png", dpi=300)

# Tight bounding box (removes extra whitespace)
plt.savefig("chart.png", dpi=300, bbox_inches="tight")

# Transparent background
plt.savefig("chart.png", transparent=True)
```

---

## 16.12 Understanding plt.show()

`plt.show()` does two things:

1. **Displays** the chart in a window
2. **Blocks** the program until you close the window

```
Your Code                    Screen
---------                    ------
plt.plot(...)
plt.title(...)
plt.show()  ------->  [Chart window opens]
                      [Program PAUSES here]
                      [You close the window]
            <-------  [Program continues]
print("Done!")  -----> "Done!"
```

**In Jupyter Notebooks**, `plt.show()` works differently. The chart appears inline (inside the notebook) and does not block. You can even skip `plt.show()` in Jupyter because it displays plots automatically.

**Tips about plt.show():**

```python
# In a script (.py file): ALWAYS call plt.show() at the end
plt.plot(x, y)
plt.show()        # Required to see the chart

# In Jupyter Notebook: optional but good practice
plt.plot(x, y)
plt.show()        # Shows chart and clears the figure

# Multiple charts in a script:
plt.plot(x, y1)
plt.show()        # Shows first chart, then clears

plt.plot(x, y2)
plt.show()        # Shows second chart
```

**Using `%matplotlib inline` in Jupyter:**

```python
%matplotlib inline    # Put this at the top of your notebook

# Now charts appear automatically without plt.show()
plt.plot(x, y)
# Chart appears here!
```

---

## Common Mistakes

**Mistake 1: x and y lists have different lengths.**

```python
x = [1, 2, 3]
y = [10, 20]       # Only 2 values!
plt.plot(x, y)      # ERROR!
```

**Fix:** Make sure both lists have the same number of elements.

---

**Mistake 2: Calling `plt.show()` before `plt.savefig()`.**

```python
plt.plot(x, y)
plt.show()                    # This clears the figure
plt.savefig("chart.png")     # Saves a blank image!
```

**Fix:** Call `plt.savefig()` before `plt.show()`.

---

**Mistake 3: Forgetting `plt.legend()` after setting labels.**

```python
plt.plot(x, y1, label="Data A")
plt.plot(x, y2, label="Data B")
# No plt.legend() call!       # Labels will NOT appear
plt.show()
```

**Fix:** Always call `plt.legend()` after setting `label=` parameters.

---

**Mistake 4: All plots end up on the same chart.**

```python
plt.plot(x, y1)
# Forgot plt.show() or plt.figure()!
plt.plot(x, y2)    # This goes on the SAME chart
plt.show()
```

**Fix:** Call `plt.show()` between plots, or call `plt.figure()` to start a new figure.

---

**Mistake 5: Using `ax.xlabel()` instead of `ax.set_xlabel()`.**

```python
fig, ax = plt.subplots()
ax.plot(x, y)
ax.xlabel("X")     # ERROR! No such method
```

**Fix:** When using the axes style, use `set_xlabel()`, `set_ylabel()`, `set_title()`.

---

## Best Practices

1. **Always label your axes.** A chart without labels is like a map without street names.

2. **Use descriptive titles.** "Chart 1" tells the reader nothing. "Monthly Revenue 2024" tells them everything.

3. **Choose the right chart type:**
   - Line plot: trends over time
   - Scatter plot: relationship between two variables
   - Bar chart: comparing categories
   - Histogram: distribution of one variable

4. **Use `tight_layout()` with subplots.** It prevents text from overlapping.

5. **Use the `fig, ax` style for anything complex.** It gives you more control.

6. **Save figures with `dpi=300`** for print quality.

7. **Keep it simple.** Do not add too many colors, labels, or decorations. Clean charts communicate better.

---

## Quick Summary

```
+----------------------------------------------------------+
|  Matplotlib Quick Reference                               |
+----------------------------------------------------------+
|  Import:        import matplotlib.pyplot as plt           |
|                                                           |
|  Line plot:     plt.plot(x, y)                            |
|  Scatter:       plt.scatter(x, y)                         |
|  Bar chart:     plt.bar(categories, values)               |
|  Histogram:     plt.hist(data, bins=20)                   |
|                                                           |
|  Labels:        plt.xlabel(), plt.ylabel(), plt.title()   |
|  Legend:        plt.legend()                               |
|  Save:          plt.savefig("file.png")                   |
|  Show:          plt.show()                                 |
|                                                           |
|  Subplots:      fig, axes = plt.subplots(rows, cols)      |
|  Spacing:       plt.tight_layout()                        |
+----------------------------------------------------------+
```

---

## Key Points to Remember

1. **Matplotlib** is Python's foundational charting library. Almost everything else is built on it.

2. **`import matplotlib.pyplot as plt`** is the standard import. Everyone uses `plt`.

3. **Line plots** show trends. **Scatter plots** show relationships. **Bar charts** compare categories. **Histograms** show distributions.

4. **Figure** = the whole canvas. **Axes** = one chart area on the canvas.

5. **`plt.savefig()` must come before `plt.show()`**, or you save a blank image.

6. **Always label** your axes and give your chart a title.

7. **`plt.tight_layout()`** prevents overlapping text in subplots.

---

## Practice Questions

**Question 1:** What is the difference between `plt.plot()` and `plt.scatter()`?

**Answer:** `plt.plot()` draws a line connecting the data points. `plt.scatter()` draws individual dots without connecting them. Use `plt.plot()` for continuous data (like time series). Use `plt.scatter()` for unrelated data points where you want to see the relationship.

---

**Question 2:** What does `plt.subplots(2, 3)` create?

**Answer:** It creates a figure with a grid of 6 axes arranged in 2 rows and 3 columns. You access each axes using `axes[row, col]`, like `axes[0, 0]` for the top-left chart.

---

**Question 3:** Why should you call `plt.savefig()` before `plt.show()`?

**Answer:** Because `plt.show()` displays the chart and then clears the figure from memory. If you call `plt.savefig()` after `plt.show()`, you save an empty, blank image.

---

**Question 4:** What is the difference between `plt.xlabel("X")` and `ax.set_xlabel("X")`?

**Answer:** `plt.xlabel("X")` uses the simple pyplot interface and applies to the current active axes. `ax.set_xlabel("X")` uses the object-oriented interface and applies to a specific axes object. They do the same thing, but the `ax` style gives you more control when you have multiple subplots.

---

**Question 5:** What does `plt.hist(data, bins=30)` do?

**Answer:** It creates a histogram of the data with 30 bins. The data is divided into 30 equal-width ranges, and bars show how many data points fall into each range. More bins means finer detail. Fewer bins means a smoother overview.

---

## Exercises

### Exercise 1: Temperature Tracker

Create a line plot showing daily temperatures for one week. Use these values:

- Days: Monday through Sunday
- Temperatures: 22, 25, 19, 28, 30, 27, 23

Add a title "Weekly Temperature", label the x-axis "Day" and y-axis "Temperature (C)". Use red color with circle markers.

**Hint:** Use `plt.plot(days, temps, "r-o")` and `plt.xticks()` if you want text labels on the x-axis.

---

### Exercise 2: Chart Dashboard

Create a figure with 4 subplots in a 2x2 grid. Fill each subplot with a different chart type:

1. Top-left: Line plot of any data
2. Top-right: Scatter plot with at least 10 points
3. Bottom-left: Bar chart with 5 categories
4. Bottom-right: Histogram of 500 random numbers

Make sure each subplot has a title. Use `plt.tight_layout()`.

**Hint:** Use `fig, axes = plt.subplots(2, 2, figsize=(10, 8))` and access each axes with `axes[row, col]`.

---

### Exercise 3: Sales Comparison

Two salespeople tracked their monthly sales for 6 months:

- Maria: 15, 22, 18, 30, 25, 35
- James: 10, 28, 20, 22, 32, 30

Plot both on the same line chart with different colors and markers. Add a legend. Save the chart as "sales_comparison.png" with `dpi=300`.

**Hint:** Call `plt.plot()` twice with `label=` for each person, then call `plt.legend()`.

---

## What Is Next?

You now know how to create charts with Matplotlib. In the next chapter, you will learn **Seaborn** — a library built on top of Matplotlib that makes statistical charts even easier and more beautiful. Think of Matplotlib as your basic toolkit and Seaborn as the deluxe upgrade.
