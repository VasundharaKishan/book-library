# Chapter 1: Welcome to Python

## What You Will Learn

- What Python is and where it came from
- Why Python is the top language for AI and machine learning
- How to install Python on Windows, Mac, and Linux
- How to verify your installation works
- How to write and run your very first Python program
- The difference between the Python shell and script mode
- What makes Python so beginner-friendly

## Why This Chapter Matters

Every AI journey starts with a single line of code. Python is the language that powers most of the AI world today. Before you can build smart programs, train models, or analyze data, you need Python on your computer and a basic understanding of how to use it. This chapter gets you from zero to your first working program. It is the foundation for everything that follows in this book.

---

## What Is Python?

Python is a programming language. A programming language is how you talk to a computer. You write instructions. The computer follows them.

Python was created by Guido van Rossum in 1991. He named it after the comedy group Monty Python, not the snake.

Think of Python like a universal remote control. A universal remote can talk to your TV, your sound system, and your streaming box. Python can talk to websites, databases, robots, and AI models. One language, many uses.

```
+---------------------------------------------+
|              PYTHON CAN DO                  |
+---------------------------------------------+
|                                             |
|   +--------+  +---------+  +----------+    |
|   |  Web   |  |  Data   |  |    AI    |    |
|   |  Apps   |  | Science |  | Machine  |    |
|   |        |  |         |  | Learning |    |
|   +--------+  +---------+  +----------+    |
|                                             |
|   +--------+  +---------+  +----------+    |
|   | Games  |  | Scripts |  | Robotics |    |
|   |        |  |  and    |  |          |    |
|   |        |  | Tools   |  |          |    |
|   +--------+  +---------+  +----------+    |
|                                             |
+---------------------------------------------+
```

---

## Why Does AI Use Python?

You might wonder: there are hundreds of programming languages. Why does almost everyone in AI use Python?

Here are the main reasons:

**1. Easy to Read**

Python code looks almost like English. Compare these two examples that both print a message:

Python:
```
print("Hello, AI World!")
```

Java:
```
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, AI World!");
    }
}
```

Python does the same thing in one line. Java needs five lines. When you are building complex AI systems, this simplicity saves you hours.

**2. Massive AI Libraries**

A library is a collection of pre-written code. Someone already solved common problems for you. Python has the best AI libraries in the world:

```
+--------------------------------------------------+
|          POPULAR PYTHON AI LIBRARIES             |
+--------------------------------------------------+
|                                                  |
|  NumPy        -> Math and numbers                |
|  Pandas       -> Data tables and analysis        |
|  Matplotlib   -> Charts and graphs               |
|  Scikit-learn -> Machine learning models          |
|  TensorFlow   -> Deep learning (by Google)        |
|  PyTorch      -> Deep learning (by Meta)          |
|  OpenAI API   -> Connect to GPT models            |
|                                                  |
+--------------------------------------------------+
```

You do not need to understand these yet. Just know they exist and they are waiting for you.

**3. Huge Community**

Millions of people use Python. When you get stuck, someone has already asked your question online. When you need help, thousands of tutorials exist. You are never alone.

**4. Free and Open Source**

Python costs nothing. You can download it, use it, and share your programs without paying a cent.

---

## Installing Python

Let us get Python on your computer. Follow the instructions for your operating system.

### Installing on Windows

**Step 1:** Open your web browser. Go to https://www.python.org/downloads/

**Step 2:** Click the big yellow button that says "Download Python 3.x.x" (the x's will be version numbers).

**Step 3:** Run the downloaded file.

**Step 4 (IMPORTANT):** On the first screen of the installer, check the box that says "Add Python to PATH". This is critical. Do not skip this step.

```
+--------------------------------------------------+
|         Python 3.x.x Installer                  |
|                                                  |
|    [x]  Add Python 3.x.x to PATH  <-- CHECK!    |
|                                                  |
|    [ Install Now ]                               |
|                                                  |
+--------------------------------------------------+
```

**Step 5:** Click "Install Now" and wait for it to finish.

**Step 6:** Click "Close" when done.

### Installing on Mac

**Option A: Official Installer**

**Step 1:** Go to https://www.python.org/downloads/

**Step 2:** Click "Download Python 3.x.x".

**Step 3:** Open the downloaded .pkg file.

**Step 4:** Follow the installer steps. Click "Continue" and "Agree" through the screens.

**Step 5:** Click "Install". Enter your password if asked.

**Option B: Using Homebrew (if you have it)**

Open the Terminal app and type:

```
brew install python3
```

### Installing on Linux

Most Linux systems already have Python. But you may need to install or update it.

**For Ubuntu or Debian:**

Open a terminal and type:

```
sudo apt update
sudo apt install python3
```

**For Fedora:**

```
sudo dnf install python3
```

---

## Verifying Your Installation

After installing, let us make sure everything works.

**Step 1:** Open a terminal or command prompt.

- **Windows:** Press the Windows key, type `cmd`, press Enter.
- **Mac:** Press Cmd + Space, type `Terminal`, press Enter.
- **Linux:** Press Ctrl + Alt + T.

**Step 2:** Type this command and press Enter:

```
python3 --version
```

**Expected Output:**

```
Python 3.12.4
```

Your version number may be slightly different. That is fine. As long as it starts with "Python 3", you are good.

> **Windows Note:** If `python3` does not work, try `python --version` instead. On Windows, the command is often just `python`.

**Step 3:** Try starting the Python shell. Type:

```
python3
```

**Expected Output:**

```
Python 3.12.4 (main, Jun  8 2024, 18:29:57)
[GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

You see three arrows: `>>>`. This is the Python prompt. Python is ready and waiting for your commands.

Type `exit()` to leave the shell.

---

## Your First Python Program

Let us write the most famous program in the world: Hello World.

### Method 1: Using the Python Shell

Open your terminal. Start Python:

```
python3
```

At the `>>>` prompt, type:

```python
>>> print("Hello, World!")
```

**Expected Output:**

```
Hello, World!
```

**Line-by-Line Explanation:**

- `print` is a built-in function. A function performs an action. The `print` function displays text on the screen.
- The parentheses `()` tell Python what to print.
- The quotes `" "` mark the beginning and end of text. In Python, text inside quotes is called a **string**.
- `Hello, World!` is the string we want to display.

```
+----------------------------------------------+
|            HOW print() WORKS                 |
+----------------------------------------------+
|                                              |
|   print("Hello, World!")                     |
|   -----  ----------------                   |
|     |           |                            |
|  function     string                         |
|  (action)    (the text                       |
|              to show)                        |
|                                              |
|         |                                    |
|         v                                    |
|                                              |
|   Screen shows: Hello, World!                |
|                                              |
+----------------------------------------------+
```

### Method 2: Writing a Script File

The shell is great for quick experiments. But real programs go into files. Let us create a script.

**Step 1:** Open any text editor. Notepad on Windows, TextEdit on Mac (switch to plain text mode), or nano on Linux.

**Step 2:** Type this code:

```python
# My first Python program
print("Hello, World!")
print("I am learning Python for AI!")
print("This is exciting!")
```

**Step 3:** Save the file as `hello.py`. The `.py` extension tells your computer this is a Python file.

> **Important:** Save it somewhere you can find it. Your Desktop or a folder called `python-practice` are good choices.

**Step 4:** Open your terminal. Navigate to the folder where you saved the file. For example:

```
cd Desktop
```

**Step 5:** Run the script:

```
python3 hello.py
```

**Expected Output:**

```
Hello, World!
I am learning Python for AI!
This is exciting!
```

**Line-by-Line Explanation:**

- Line 1: `# My first Python program` is a **comment**. The `#` symbol tells Python to ignore this line. Comments are notes for humans, not for the computer.
- Line 2: `print("Hello, World!")` displays the first message.
- Line 3: `print("I am learning Python for AI!")` displays the second message.
- Line 4: `print("This is exciting!")` displays the third message.
- Python runs each line from top to bottom, one at a time.

```
+----------------------------------------------+
|      HOW PYTHON RUNS YOUR SCRIPT             |
+----------------------------------------------+
|                                              |
|   Line 1: # comment        -> skip          |
|                |                             |
|                v                             |
|   Line 2: print(...)       -> Hello, World!  |
|                |                             |
|                v                             |
|   Line 3: print(...)       -> I am learning..|
|                |                             |
|                v                             |
|   Line 4: print(...)       -> This is...     |
|                |                             |
|                v                             |
|            Program ends                      |
|                                              |
+----------------------------------------------+
```

---

## Python Shell vs Script Mode

Python gives you two ways to run code. Each has its purpose.

### The Python Shell (Interactive Mode)

- You type one line at a time.
- Python runs it immediately.
- Great for testing small ideas.
- Results disappear when you close the shell.

Think of it like a calculator. You type a problem, you get an answer right away.

```
>>> 2 + 3
5
>>> "hello" * 3
'hellohellohello'
>>> len("Python")
6
```

### Script Mode

- You write many lines in a file.
- You save the file.
- You run the entire file at once.
- Your code is saved permanently.

Think of it like writing a recipe. You write all the steps down, then follow them from start to finish.

```
+----------------------------------------------+
|     SHELL MODE vs SCRIPT MODE                |
+----------------------------------------------+
|                                              |
|   Shell (Interactive)    Script (File)       |
|   -------------------    ---------------     |
|   Quick experiments      Real programs       |
|   One line at a time     Many lines           |
|   Results are temporary  Code is saved        |
|   Like a calculator      Like a recipe        |
|   Good for learning      Good for building    |
|                                              |
+----------------------------------------------+
```

### When to Use Which?

- **Use the shell** when you want to try something quickly. "Does this work?" Just type it and see.
- **Use a script** when you are building something real. A program you want to keep and run again.

In this book, we will use both. Short examples will show the `>>>` prompt (shell mode). Longer programs will be scripts.

---

## What Makes Python Beginner-Friendly?

Here are five reasons Python is great for beginners:

### 1. Clean Syntax

Python uses indentation (spaces) to organize code. Other languages use curly braces `{}`. Indentation makes code naturally readable.

```python
# Python - clean and readable
if age >= 18:
    print("You can vote")
else:
    print("Too young to vote")
```

### 2. No Semicolons Needed

Many languages require a semicolon `;` at the end of every line. Python does not. One less thing to worry about.

### 3. English-Like Keywords

Python uses words like `and`, `or`, `not`, `in`, `is`, `True`, `False`. These read like natural English.

### 4. Helpful Error Messages

When you make a mistake, Python tells you what went wrong and where. For example:

```
>>> print("Hello)
  File "<stdin>", line 1
    print("Hello)
                ^
SyntaxError: unterminated string literal
```

Python points to the exact spot where the problem is. It even tells you the type of error: `SyntaxError`.

### 5. No Compilation Step

Some languages require you to "compile" your code before running it. Python runs your code directly. Write it and run it. That simple.

```
+----------------------------------------------+
|      COMPILED vs INTERPRETED                 |
+----------------------------------------------+
|                                              |
|   Compiled Language (like C):                |
|   Write -> Compile -> Run                    |
|   (extra step)                               |
|                                              |
|   Python (Interpreted):                      |
|   Write -> Run                               |
|   (one less step!)                           |
|                                              |
+----------------------------------------------+
```

---

## Common Mistakes

**Mistake 1: Forgetting to add Python to PATH (Windows)**

If you see "python is not recognized" in your command prompt, you did not check the PATH box during installation. Reinstall Python and check that box.

**Mistake 2: Using Python 2 instead of Python 3**

Python 2 is outdated. Always use Python 3. Check with `python3 --version`. If your version starts with "2", you need to install Python 3.

**Mistake 3: Forgetting the quotes in print()**

```python
# Wrong - this will cause an error
print(Hello, World!)

# Right - text must be in quotes
print("Hello, World!")
```

**Mistake 4: Forgetting the parentheses in print()**

```python
# Wrong - missing parentheses
print "Hello"

# Right - always use parentheses
print("Hello")
```

**Mistake 5: Using the wrong file extension**

Save your Python files with `.py`, not `.txt` or anything else.

```
hello.py    <-- Correct
hello.txt   <-- Wrong
hello.python <-- Wrong
```

---

## Best Practices

1. **Always use Python 3.** Python 2 reached end of life in 2020. All new projects should use Python 3.

2. **Add Python to your PATH.** This lets you run Python from any folder in your terminal.

3. **Use a code editor.** Notepad works, but a code editor like VS Code gives you colors, auto-complete, and error highlighting. It makes coding much easier.

4. **Save your work.** Write scripts instead of typing everything in the shell. Scripts let you build on your work over time.

5. **Comment your code.** Use `#` to leave notes for yourself. Future-you will thank present-you.

---

## Quick Summary

Python is a free, powerful, and beginner-friendly programming language. It is the most popular language for AI and machine learning. You installed Python, verified it works, and wrote your first program. You learned the difference between the shell (for quick tests) and scripts (for real programs). You are now ready to start learning Python properly.

---

## Key Points to Remember

- Python is a programming language created in 1991.
- Python is the number one language for AI because it is simple, has great libraries, and has a huge community.
- Always install Python 3, not Python 2.
- On Windows, check "Add Python to PATH" during installation.
- Use `python3 --version` to verify your installation.
- `print()` displays text on the screen.
- Text in quotes is called a string.
- Lines starting with `#` are comments. Python ignores them.
- The Python shell (`>>>`) is for quick experiments.
- Script files (`.py`) are for real programs.

---

## Practice Questions

**Question 1:** What command do you type in the terminal to check which version of Python is installed?

<details>
<summary>Answer</summary>

```
python3 --version
```

</details>

**Question 2:** What is the difference between the Python shell and a Python script?

<details>
<summary>Answer</summary>

The Python shell runs one line at a time and results are temporary. A Python script is a file with many lines that you save and can run again. The shell is for quick experiments. Scripts are for real programs.

</details>

**Question 3:** What does the `#` symbol do in Python?

<details>
<summary>Answer</summary>

The `#` symbol creates a comment. Python ignores everything after `#` on that line. Comments are notes for humans reading the code.

</details>

**Question 4:** Why is Python so popular for AI development?

<details>
<summary>Answer</summary>

Python is popular for AI because: (1) it has simple, readable syntax, (2) it has powerful AI libraries like TensorFlow, PyTorch, and scikit-learn, (3) it has a huge community for support, and (4) it is free and open source.

</details>

**Question 5:** What happens if you forget the quotes inside `print()`?

<details>
<summary>Answer</summary>

Python will give you an error. Without quotes, Python thinks the words are variable names or commands, not text. You must put text inside quotes: `print("Hello")`.

</details>

---

## Exercises

### Exercise 1: Install and Verify

Install Python on your computer. Open a terminal and run `python3 --version`. Write down the version number you see.

Then start the Python shell and type `print("I installed Python!")`. Take a screenshot of your result.

### Exercise 2: Create Your First Script

Create a file called `about_me.py`. In this file, use `print()` to display:
- Your name
- Your age
- Why you want to learn AI

Run the script and verify the output.

**Example solution:**

```python
# about_me.py - My introduction
print("My name is Alex")
print("I am 25 years old")
print("I want to learn AI to build smart apps")
```

**Expected Output:**

```
My name is Alex
I am 25 years old
I want to learn AI to build smart apps
```

### Exercise 3: Experiment with the Shell

Open the Python shell and try these commands one at a time. Write down what each one does:

```python
>>> 10 + 5
>>> "Python" * 3
>>> len("Hello")
>>> type(42)
>>> type("Hello")
```

---

## What Is Next?

You have Python installed and you can print messages to the screen. But programs need to remember things. In the next chapter, you will learn about **variables** -- the way Python stores and remembers information. Variables are the building blocks of every program, and you will use them in every single chapter after this one.
