# Chapter 18: Jupyter Notebooks and Google Colab

## What You Will Learn

In this chapter, you will learn how to:

- Understand what Jupyter Notebook is and why data scientists love it
- Install Jupyter Notebook on your computer
- Create and manage notebooks
- Use different cell types (code and markdown)
- Run cells and understand execution order
- Use keyboard shortcuts to work faster
- Use magic commands like `%timeit`, `%%time`, and `!pip`
- Display plots inline (inside the notebook)
- Use Google Colab — free cloud notebooks with GPU access
- Upload files to Colab and mount Google Drive
- Decide when to use notebooks vs regular Python scripts

## Why This Chapter Matters

So far, you have been writing Python code in `.py` files and running them in the terminal. That works, but it has limitations:

- You cannot see a chart next to the code that created it
- You cannot add notes and explanations between code blocks
- You have to re-run the entire file to test one small change
- You cannot easily share your work with non-programmers

Jupyter Notebooks solve all of these problems. They let you mix code, output, charts, and text in one interactive document.

```
Regular Python Script (.py):      Jupyter Notebook (.ipynb):

+---------------------------+     +---------------------------+
|  import pandas as pd      |     |  # Data Analysis Report   |
|  df = pd.read_csv(...)    |     |  Written by: Alice        |
|  print(df.head())         |     +---------------------------+
|  ...                      |     |  import pandas as pd      |
|  plt.show()               |     |  df = pd.read_csv(...)    |
|  ...                      |     |  df.head()                |
+---------------------------+     +---------------------------+
                                  |  Output:                  |
  Run whole file at once.         |  [table appears here]     |
  Output only in terminal.       +---------------------------+
                                  |  ## Key Findings          |
                                  |  Sales grew by 25%...     |
                                  +---------------------------+
                                  |  plt.plot(...)            |
                                  +---------------------------+
                                  |  [chart appears here]     |
                                  +---------------------------+

                                  Run cells one at a time.
                                  Output appears inline.
                                  Notes between code blocks.
```

Almost every data scientist and ML engineer uses Jupyter Notebooks daily. Learning this tool is essential.

---

## 18.1 What Is Jupyter Notebook?

Jupyter Notebook is a web-based application that lets you create documents containing:

- **Live code** — write and run Python right in the browser
- **Output** — results appear directly below the code
- **Charts** — plots display inline
- **Text** — add explanations, headers, and formatting with Markdown
- **Math equations** — write formulas with LaTeX

The name "Jupyter" comes from three programming languages: **Ju**lia, **Py**thon, and **R**. But today, Python is by far the most popular language used with Jupyter.

```
+--------------------------------------------------+
|  How Jupyter Works                                |
+--------------------------------------------------+
|                                                   |
|  Browser (what you see)                           |
|     |                                             |
|     | sends code                                  |
|     v                                             |
|  Jupyter Server (runs on your computer)           |
|     |                                             |
|     | executes code                               |
|     v                                             |
|  Python Kernel (the engine)                       |
|     |                                             |
|     | returns results                             |
|     v                                             |
|  Browser (shows output)                           |
|                                                   |
+--------------------------------------------------+
```

A **kernel** is the engine that runs your code. When you open a notebook, a Python kernel starts in the background. You send code to the kernel, and it sends results back.

---

## 18.2 Installing Jupyter Notebook

### Option 1: Install with pip

```bash
pip install notebook
```

**Expected Output:**

```
Successfully installed notebook-7.x.x
```

### Option 2: Install with Anaconda

If you installed Anaconda (a Python distribution for data science), Jupyter is already included. No extra installation needed.

### Starting Jupyter Notebook

Open your terminal and type:

```bash
jupyter notebook
```

**Expected Output:**

```
[I 2024-01-15 10:30:00] Serving notebooks from local directory: /home/user
[I 2024-01-15 10:30:00] Jupyter Notebook is running at:
[I 2024-01-15 10:30:00] http://localhost:8888/
```

Your web browser opens automatically and shows the Jupyter dashboard — a file browser where you can create and open notebooks.

```
+--------------------------------------------------+
|  Jupyter Dashboard                                |
|                                                   |
|  Files    Running    Clusters                     |
|  -----------------------------------------------  |
|  [ ] Documents/                                   |
|  [ ] my_project/                                  |
|  [ ] analysis.ipynb                               |
|  [ ] data.csv                                     |
|                                                   |
|  [New v]   (click to create a new notebook)       |
+--------------------------------------------------+
```

To stop Jupyter, go back to the terminal and press `Ctrl+C`.

---

## 18.3 Creating Your First Notebook

1. In the Jupyter dashboard, click **New** in the top-right corner
2. Select **Python 3** from the dropdown
3. A new notebook opens with one empty cell

```
+--------------------------------------------------+
|  Untitled  [File] [Edit] [View] [Insert] ...     |
|                                                   |
|  In [  ]: |                                       |
|           |                                       |
|           +---------------------------------------+
|                                                   |
+--------------------------------------------------+
```

Type some code in the cell:

```python
print("Hello, Jupyter!")
```

Press **Shift + Enter** to run the cell.

**Expected Output:**

```
Hello, Jupyter!
```

The output appears directly below the cell. A new empty cell appears below the output.

```
+--------------------------------------------------+
|  In [1]: print("Hello, Jupyter!")                 |
|                                                   |
|  Hello, Jupyter!                                  |
|                                                   |
|  In [  ]: |   (new empty cell)                    |
+--------------------------------------------------+
```

**The number `[1]`** means this was the first cell you ran. The next cell you run will be `[2]`, and so on. These numbers track the execution order.

### Renaming Your Notebook

Click on "Untitled" at the top of the page and type a new name, like "my_first_notebook". The file is saved as `my_first_notebook.ipynb`.

---

## 18.4 Cell Types — Code and Markdown

A notebook has two main cell types:

### Code Cells

Code cells contain Python code. When you run them, the code executes and output appears below.

```python
# This is a code cell
x = 10
y = 20
print(x + y)
```

**Expected Output:**

```
30
```

### Markdown Cells

Markdown cells contain formatted text. They are used for explanations, headings, lists, and notes.

To change a cell to Markdown:

1. Click on the cell
2. In the toolbar dropdown, change "Code" to "Markdown"
3. Or press **Esc** then **M**

Example Markdown:

```markdown
# This is a Heading

This is regular text. You can make text **bold** or *italic*.

## A Subheading

- Bullet point one
- Bullet point two

### Code Example
You can show code in text using backticks: `print("hello")`
```

When you press **Shift + Enter** on a Markdown cell, it renders the formatted text.

```
+--------------------------------------------------+
|  Before running:                                  |
|  # This is a Heading                              |
|  This is regular text with **bold**               |
+--------------------------------------------------+
|  After running (Shift+Enter):                     |
|                                                   |
|  This is a Heading                                |
|  ================                                 |
|  This is regular text with bold                   |
+--------------------------------------------------+
```

### Common Markdown Syntax

```
# Heading 1             (largest)
## Heading 2
### Heading 3           (smallest used often)

**bold text**
*italic text*
`inline code`

- bullet point
1. numbered list

[Link text](http://example.com)

| Column A | Column B |
|----------|----------|
| data 1   | data 2   |
```

---

## 18.5 Running Cells and Execution Order

### Running a Cell

There are three ways to run a cell:

```
Shift + Enter     Run cell and move to next cell
Ctrl + Enter      Run cell and stay on same cell
Alt + Enter       Run cell and insert new cell below
```

### Execution Order Matters

Cells in Jupyter do NOT have to run top to bottom. You can run them in any order. This is powerful but can cause confusion.

```
+--------------------------------------------------+
|  Example of execution order issues:               |
+--------------------------------------------------+
|                                                   |
|  In [1]: x = 10        # You run this first       |
|                                                   |
|  In [3]: print(x)      # You run this third       |
|          Output: 50     # Gets the value from [2]! |
|                                                   |
|  In [2]: x = 50        # You run this second      |
|                                                   |
+--------------------------------------------------+
```

The number in brackets shows the order you ran the cells, NOT the order they appear. This is a common source of bugs.

**Best practice:** Run all cells from top to bottom regularly. Use **Kernel > Restart & Run All** to re-run everything from scratch.

```
+--------------------------------------------------+
|  Execution Order Rules:                           |
|                                                   |
|  1. The kernel remembers ALL variables from       |
|     ALL cells you have run                        |
|                                                   |
|  2. If you change a cell and re-run it,           |
|     cells BELOW are NOT automatically re-run      |
|                                                   |
|  3. Deleting a cell does NOT delete the           |
|     variables it created                          |
|                                                   |
|  4. "Restart & Run All" is your safety net        |
+--------------------------------------------------+
```

---

## 18.6 Keyboard Shortcuts

Jupyter has two modes:

- **Edit mode** (green border) — you are typing inside a cell
- **Command mode** (blue border) — you are navigating between cells

Press **Esc** to enter Command mode. Press **Enter** to enter Edit mode.

### Essential Command Mode Shortcuts

```
+-------------------+--------------------------------------+
|  Shortcut         |  What It Does                        |
+-------------------+--------------------------------------+
|  A                |  Insert cell Above                   |
|  B                |  Insert cell Below                   |
|  DD               |  Delete current cell (press D twice) |
|  M                |  Change cell to Markdown             |
|  Y                |  Change cell to Code                 |
|  C                |  Copy cell                           |
|  V                |  Paste cell below                    |
|  Z                |  Undo cell deletion                  |
|  Shift + M        |  Merge selected cells                |
|  L                |  Toggle line numbers                 |
|  Shift + Enter    |  Run cell, move to next              |
|  Ctrl + Enter     |  Run cell, stay in place             |
+-------------------+--------------------------------------+
```

### Essential Edit Mode Shortcuts

```
+-------------------+--------------------------------------+
|  Shortcut         |  What It Does                        |
+-------------------+--------------------------------------+
|  Tab              |  Code completion / indent             |
|  Shift + Tab      |  Show function documentation          |
|  Ctrl + /         |  Toggle comment on selected lines     |
|  Ctrl + Z         |  Undo                                 |
|  Ctrl + Shift + Z |  Redo                                 |
+-------------------+--------------------------------------+
```

**Tip:** Press **H** in Command mode to see all available shortcuts.

---

## 18.7 Magic Commands

Magic commands are special commands that start with `%` (line magic) or `%%` (cell magic). They are not Python — they are Jupyter-specific.

### %timeit — Measure Execution Speed

```python
%timeit sum(range(10000))
```

**Expected Output:**

```
121 us +/- 1.03 us per loop (mean +/- std. dev. of 7 runs, 10,000 loops each)
```

`%timeit` runs the code many times and gives you the average execution time. This is useful for comparing different approaches.

**Line-by-line explanation:**

```python
%timeit sum(range(10000))
```

The `%` prefix makes this a line magic command. It times just this one line. The result shows microseconds (`us`), meaning it took about 121 millionths of a second.

### %%time — Time an Entire Cell

```python
%%time
total = 0
for i in range(1000000):
    total += i
print(total)
```

**Expected Output:**

```
499999500000
CPU times: user 98.2 ms, sys: 1.02 ms, total: 99.2 ms
Wall time: 99.5 ms
```

**Line-by-line explanation:**

```python
%%time
```

The `%%` prefix means "cell magic" — it applies to the entire cell, not just one line. It runs the code once and reports the time.

```
%timeit vs %%time:

%timeit    Runs code MANY times. More accurate. For one line.
%%time     Runs code ONCE. Quick check. For a whole cell.
```

### !command — Run Terminal Commands

You can run terminal (shell) commands from inside a notebook by adding `!` at the start.

```python
!pip install numpy
```

**Expected Output:**

```
Requirement already satisfied: numpy in /usr/lib/python3/dist-packages
```

```python
!python --version
```

**Expected Output:**

```
Python 3.11.5
```

```python
# List files in the current directory
!ls
```

**Expected Output:**

```
data.csv    my_notebook.ipynb    results/
```

### Other Useful Magic Commands

```python
%who         # List all variables in memory
%whos        # List variables with type and info
%pwd         # Print working directory
%ls          # List files
%reset       # Clear all variables (asks confirmation)
%matplotlib inline    # Show plots inside notebook
```

Example:

```python
x = 10
name = "Alice"
data = [1, 2, 3]
%whos
```

**Expected Output:**

```
Variable   Type    Data/Info
----------------------------
data       list    n=3
name       str     Alice
x          int     10
```

---

## 18.8 Displaying Plots Inline

By default, Matplotlib plots may open in a separate window. In Jupyter, you want them inside the notebook.

### Method 1: %matplotlib inline

```python
%matplotlib inline
```

Put this at the top of your notebook (or in the first cell). After this, all Matplotlib and Seaborn charts appear directly below the cell.

```python
%matplotlib inline
import matplotlib.pyplot as plt

x = [1, 2, 3, 4, 5]
y = [10, 20, 15, 25, 30]

plt.plot(x, y)
plt.title("Inline Plot")
# No need for plt.show()! Chart appears automatically.
```

**Expected Output:**

The chart appears directly in the notebook, below the code cell.

### Method 2: Just call plt.show()

Even without `%matplotlib inline`, calling `plt.show()` usually displays the chart inline in modern Jupyter versions.

```python
import matplotlib.pyplot as plt

plt.plot([1, 2, 3], [4, 5, 6])
plt.show()    # Chart appears inline
```

**Recommendation:** Add `%matplotlib inline` at the top of every notebook. It is a safe habit.

---

## 18.9 Google Colab — Free Cloud Notebooks

Google Colab (short for Colaboratory) is a free online version of Jupyter Notebook hosted by Google. You do not install anything. Everything runs in the cloud.

```
+--------------------------------------------------+
|  Jupyter Notebook         vs    Google Colab      |
+--------------------------------------------------+
|  Runs on YOUR computer         Runs on GOOGLE's  |
|  You must install it            Nothing to install|
|  No GPU (usually)               Free GPU/TPU!     |
|  Your files stay local          Files in cloud    |
|  Always available               Needs internet    |
|  Full control                   Some limitations  |
+--------------------------------------------------+
```

### Getting Started with Colab

1. Go to [colab.research.google.com](https://colab.research.google.com)
2. Sign in with your Google account
3. Click **New Notebook**
4. Start coding!

Colab looks almost identical to Jupyter Notebook. The same cell types, same keyboard shortcuts, same Python code.

### What Comes Pre-installed

Colab already has these libraries installed:

```
numpy, pandas, matplotlib, seaborn, scikit-learn,
tensorflow, keras, pytorch, scipy, and many more
```

You do not need to run `pip install` for common libraries. They are ready to use.

### Free GPU Access

This is Colab's killer feature. You can use a GPU (Graphics Processing Unit) for free. GPUs make deep learning training much faster.

To enable GPU:

1. Click **Runtime** in the menu
2. Click **Change runtime type**
3. Under "Hardware accelerator", select **GPU** (or **T4 GPU**)
4. Click **Save**

```python
# Check if GPU is available
import torch
print(torch.cuda.is_available())
```

**Expected Output (with GPU enabled):**

```
True
```

---

## 18.10 Uploading Files to Colab

Since Colab runs in the cloud, your local files are not available. You need to upload them.

### Method 1: Upload Button

```python
from google.colab import files

uploaded = files.upload()
```

**Expected Output:**

A file picker dialog appears in the browser. Select a file from your computer. After uploading:

```
data.csv (1024 bytes) - uploaded
```

Now you can use the file:

```python
import pandas as pd

df = pd.read_csv("data.csv")
print(df.head())
```

### Method 2: From a URL

```python
import pandas as pd

url = "https://example.com/data.csv"
df = pd.read_csv(url)
print(df.head())
```

This downloads the file directly from the internet. No upload needed.

### Downloading Files from Colab

```python
from google.colab import files

# Save a plot first
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [4, 5, 6])
plt.savefig("my_plot.png")

# Download it to your computer
files.download("my_plot.png")
```

A download dialog appears in your browser.

---

## 18.11 Mounting Google Drive

For larger files or persistent storage, you can connect your Google Drive to Colab.

```python
from google.colab import drive

drive.mount("/content/drive")
```

**Expected Output:**

A popup asks you to sign in to Google and grant permission. After that:

```
Mounted at /content/drive
```

Now your entire Google Drive is accessible as a folder:

```python
import pandas as pd

# Read a file from Google Drive
df = pd.read_csv("/content/drive/MyDrive/my_data.csv")
print(df.head())
```

```
+--------------------------------------------------+
|  Google Drive Structure in Colab:                 |
+--------------------------------------------------+
|                                                   |
|  /content/                                        |
|     |-- drive/                                    |
|     |     |-- MyDrive/           <-- your Drive   |
|     |     |     |-- my_data.csv                   |
|     |     |     |-- projects/                     |
|     |     |     |     |-- model.h5                |
|     |                                             |
|     |-- sample_data/             <-- Colab samples|
|                                                   |
+--------------------------------------------------+
```

### Saving Files to Google Drive

```python
# Save a DataFrame to Google Drive
df.to_csv("/content/drive/MyDrive/results.csv", index=False)
print("Saved to Google Drive!")
```

**Why use Drive?** Colab's local storage is temporary. When your session ends (after inactivity or 12 hours), all local files are deleted. Google Drive files persist.

```
Local Colab storage:           Google Drive:
  Temporary                      Permanent
  Deleted when session ends      Always available
  Fast access                    Slightly slower
  Good for temp files            Good for data & models
```

---

## 18.12 When to Use Notebooks vs Scripts

Both notebooks and scripts have their place. Here is when to use each:

### Use Notebooks (.ipynb) When:

- **Exploring data** — try things, see results immediately
- **Prototyping** — experiment with different approaches
- **Visualizing** — charts appear right next to code
- **Teaching** — mix explanations with code
- **Sharing results** — send a notebook as a report
- **Quick analysis** — one-off data analysis tasks

### Use Scripts (.py) When:

- **Building applications** — web apps, APIs, tools
- **Production code** — code that runs automatically
- **Version control** — scripts work better with Git
- **Testing** — unit tests are easier with scripts
- **Large projects** — multiple files, imports, packages
- **Automation** — scheduled jobs, pipelines

```
+--------------------------------------------------+
|  Decision Guide                                   |
+--------------------------------------------------+
|                                                   |
|  "Am I exploring or building?"                    |
|                                                   |
|  Exploring -----> Notebook (.ipynb)               |
|  Building  -----> Script (.py)                    |
|                                                   |
|  "Will someone else read this?"                   |
|                                                   |
|  Yes, non-coders -----> Notebook                  |
|  Yes, developers -----> Script                    |
|  No, just me     -----> Either works              |
|                                                   |
+--------------------------------------------------+
```

### A Common Workflow

Many data scientists use both:

1. **Start in a notebook** — explore data, try ideas, build charts
2. **Move to scripts** — take the working code and organize it into `.py` files
3. **Use notebooks for reports** — create a clean notebook showing final results

---

## Common Mistakes

**Mistake 1: Running cells out of order causes confusing bugs.**

```
Cell 1 (run first):   x = 10
Cell 2 (run third):   print(x)    # Prints 50, not 10!
Cell 3 (run second):  x = 50
```

**Fix:** Use **Kernel > Restart & Run All** regularly. This runs all cells from top to bottom in order.

---

**Mistake 2: Forgetting that deleted cells still affect memory.**

```
Cell 1:  big_list = list(range(10000000))    # Uses lots of memory
         # You DELETE this cell
         # big_list STILL exists in memory!
```

**Fix:** After deleting a cell, restart the kernel to clear memory. Or manually run `del big_list`.

---

**Mistake 3: Using `!pip install` but the package still does not work.**

```python
!pip install some_package
import some_package    # ERROR: module not found
```

**Fix:** After installing, restart the kernel. The new package is not available until the kernel restarts.

---

**Mistake 4: Plots appearing in a separate window instead of inline.**

```python
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [4, 5, 6])
plt.show()
# Chart opens in a new window!
```

**Fix:** Add `%matplotlib inline` at the top of your notebook, before any plotting code.

---

**Mistake 5: Colab session disconnects and you lose your files.**

**Fix:** Mount Google Drive at the beginning. Save important files there. Local Colab storage is temporary.

---

## Best Practices

1. **Put imports in the first cell.** Everyone expects to find imports at the top.

2. **Add `%matplotlib inline` in the first cell.** This ensures plots display correctly.

3. **Use Markdown cells liberally.** Explain what you are doing and why. Future-you will thank present-you.

4. **Run "Restart & Run All" before sharing.** This ensures the notebook works from top to bottom without errors.

5. **Keep cells short.** Each cell should do one thing. Long cells are hard to debug.

6. **Name your notebooks descriptively.** "Untitled7.ipynb" tells you nothing. "customer_churn_analysis.ipynb" tells you everything.

7. **In Colab, mount Google Drive early.** Save your work to Drive so you do not lose it when the session ends.

8. **Do not put passwords or API keys in notebooks.** Notebooks are often shared. Use environment variables instead.

---

## Quick Summary

```
+----------------------------------------------------------+
|  Jupyter & Colab Quick Reference                          |
+----------------------------------------------------------+
|  Install:       pip install notebook                      |
|  Start:         jupyter notebook                          |
|                                                           |
|  Cell Types:    Code (Y) and Markdown (M)                 |
|  Run cell:      Shift+Enter or Ctrl+Enter                 |
|                                                           |
|  Magic:         %timeit  (time one line)                  |
|                 %%time   (time whole cell)                 |
|                 !command (run terminal command)            |
|                 %matplotlib inline (inline plots)         |
|                                                           |
|  Command mode:  A (add above), B (add below)              |
|                 DD (delete), M (markdown), Y (code)       |
|                                                           |
|  Colab:         colab.research.google.com                 |
|                 Free GPU, nothing to install               |
|                 Mount Drive: drive.mount("/content/drive") |
+----------------------------------------------------------+
```

---

## Key Points to Remember

1. **Jupyter Notebook** lets you mix code, output, charts, and text in one interactive document.

2. **Cells** are the building blocks. Code cells run Python. Markdown cells hold formatted text.

3. **Execution order matters.** Cells run in whatever order you click them, not top to bottom. This can cause bugs.

4. **Magic commands** start with `%` or `%%`. Use `%timeit` to measure speed and `!pip` to install packages.

5. **Google Colab** is a free cloud-based Jupyter Notebook. It comes with GPUs and pre-installed libraries.

6. **Mount Google Drive** in Colab to save files permanently. Local Colab storage is temporary.

7. **Use notebooks for exploration, scripts for production.** Many professionals use both.

---

## Practice Questions

**Question 1:** What is the difference between a code cell and a Markdown cell?

**Answer:** A code cell contains Python code that gets executed when you run it. The output appears below the cell. A Markdown cell contains formatted text (headings, bold, lists, etc.) for documentation. When you run a Markdown cell, it renders the formatted text. Code cells have `In [ ]:` next to them. Markdown cells do not.

---

**Question 2:** What does `%timeit` do, and how is it different from `%%time`?

**Answer:** `%timeit` is a line magic that runs a single line of code many times (thousands or millions of loops) and reports the average execution time. It gives very accurate timing. `%%time` is a cell magic that runs the entire cell once and reports how long it took. Use `%timeit` for precise benchmarking of small operations. Use `%%time` for a quick timing of larger code blocks.

---

**Question 3:** Why should you run "Restart & Run All" before sharing a notebook?

**Answer:** Because cells can be run in any order, the notebook might work on your machine but fail for someone else. "Restart & Run All" clears all variables, restarts the Python kernel, and runs every cell from top to bottom in order. If this succeeds, the notebook is guaranteed to work for anyone who opens it.

---

**Question 4:** What happens to your files in Google Colab when your session ends?

**Answer:** All files stored in Colab's local storage (the `/content/` directory) are deleted when the session ends. Sessions end after about 12 hours of continuous use or after extended inactivity. To keep files permanently, save them to Google Drive by mounting it with `drive.mount("/content/drive")`.

---

**Question 5:** When should you use a Jupyter Notebook instead of a regular Python script?

**Answer:** Use a notebook when you are exploring data, prototyping ideas, creating visualizations, teaching, or preparing a report that mixes code with explanations. Use a script when you are building an application, writing production code, creating reusable packages, or setting up automated pipelines. Many professionals start in a notebook and then move proven code to scripts.

---

## Exercises

### Exercise 1: Your First Complete Notebook

Create a Jupyter Notebook that does the following:

1. A Markdown cell with a title and your name
2. A code cell that imports NumPy and Pandas
3. A code cell that creates a small DataFrame with 5 rows of data
4. A Markdown cell explaining what the data represents
5. A code cell that displays basic statistics using `.describe()`
6. A code cell that creates a simple plot of the data

Make sure `%matplotlib inline` is set at the top.

**Hint:** Start by running `jupyter notebook` in the terminal, then create a new Python 3 notebook.

---

### Exercise 2: Speed Comparison

In a Jupyter Notebook, use `%timeit` to compare these three ways of summing numbers from 0 to 999,999:

1. A Python `for` loop with `+=`
2. The built-in `sum()` function with `range()`
3. NumPy's `np.sum()` with `np.arange()`

Which is fastest? By how much?

**Hint:** Use `%timeit` for each approach in separate cells. Compare the reported times.

---

### Exercise 3: Colab Data Analysis

Open Google Colab and create a notebook that:

1. Loads the Seaborn "tips" dataset
2. Displays the first 10 rows
3. Shows basic statistics
4. Creates a scatter plot of total_bill vs tip
5. Saves the plot to Google Drive (mount Drive first)

**Hint:** Use `sns.load_dataset("tips")` and mount Drive with `from google.colab import drive; drive.mount("/content/drive")`.

---

## What Is Next?

You now have powerful tools for writing code (Jupyter), creating charts (Matplotlib and Seaborn), and working in the cloud (Colab). In the next chapter, we shift gears to **mathematics**. You will start with an algebra refresher — revisiting the math concepts that form the backbone of machine learning. Do not worry if math was not your favorite subject. We will keep it simple, visual, and connected to real AI applications.
