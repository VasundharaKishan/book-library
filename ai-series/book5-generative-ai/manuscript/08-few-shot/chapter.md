# Chapter 8: Few-Shot Prompting

## What You Will Learn

In this chapter, you will learn:

- The difference between zero-shot, one-shot, and few-shot prompting
- How providing examples in your prompt teaches the model patterns
- What in-context learning is and why it works
- How to format examples effectively for best results
- When few-shot prompting helps the most and when it is unnecessary
- Practical techniques for selecting and structuring examples

## Why This Chapter Matters

In the previous chapter, you learned how to write clear, specific prompts. But sometimes, no matter how well you describe what you want, the model still does not quite get it. This is where few-shot prompting shines.

Instead of describing the output format in words, you show the model examples. Humans learn this way too. If someone asks you to write a haiku, a description helps. But seeing three example haikus teaches you the pattern instantly.

Few-shot prompting is one of the most practical and powerful techniques in prompt engineering. It works with every LLM, requires no fine-tuning, and can dramatically improve output quality for structured or pattern-based tasks.

---

## Zero-Shot, One-Shot, and Few-Shot

These terms describe how many examples you include in your prompt.

```
+----------------------------------------------------------+
|         The Shot Spectrum                                 |
+----------------------------------------------------------+
|                                                            |
|  ZERO-SHOT (0 examples):                                 |
|    "Classify this review as positive or negative:         |
|     'The food was terrible.' "                            |
|    Just the instruction, no examples.                     |
|                                                            |
|  ONE-SHOT (1 example):                                    |
|    "Classify reviews as positive or negative.             |
|     Example: 'Great service!' -> Positive                 |
|     Now classify: 'The food was terrible.' "              |
|    One example to show the pattern.                       |
|                                                            |
|  FEW-SHOT (2-10 examples):                               |
|    "Classify reviews as positive or negative.             |
|     'Great service!' -> Positive                          |
|     'Awful experience.' -> Negative                       |
|     'Best meal ever!' -> Positive                         |
|     Now classify: 'The food was terrible.' "              |
|    Multiple examples to establish the pattern clearly.    |
|                                                            |
+----------------------------------------------------------+
```

**Analogy:** Think of teaching someone a new game.
- **Zero-shot:** Read them the rulebook (just instructions)
- **One-shot:** Show them one round being played (one example)
- **Few-shot:** Let them watch several rounds before playing (multiple examples)

Most people learn games fastest by watching a few rounds first.

```python
# Comparing zero-shot, one-shot, and few-shot prompts

def compare_shot_types():
    """Show the three types of prompting side by side."""

    task = "Convert informal text to formal business English"
    test_input = "hey can u send me that report asap thx"

    prompts = {
        "Zero-shot": (
            f"Convert this informal text to formal business English:\n"
            f"'{test_input}'"
        ),
        "One-shot": (
            f"Convert informal text to formal business English.\n\n"
            f"Example:\n"
            f"Informal: 'gonna need those numbers by friday'\n"
            f"Formal: 'I will need those numbers by Friday, please.'\n\n"
            f"Now convert:\n"
            f"Informal: '{test_input}'\n"
            f"Formal:"
        ),
        "Few-shot": (
            f"Convert informal text to formal business English.\n\n"
            f"Informal: 'gonna need those numbers by friday'\n"
            f"Formal: 'I will need those numbers by Friday, please.'\n\n"
            f"Informal: 'lmk if u can make it to the meeting tmrw'\n"
            f"Formal: 'Please let me know if you are available to "
            f"attend the meeting tomorrow.'\n\n"
            f"Informal: 'sry for the late reply been super busy'\n"
            f"Formal: 'I apologize for the delayed response. I have "
            f"been quite occupied.'\n\n"
            f"Informal: '{test_input}'\n"
            f"Formal:"
        ),
    }

    print("Zero-Shot vs One-Shot vs Few-Shot")
    print("=" * 60)
    print(f"Task: {task}")
    print(f"Input: '{test_input}'")

    for shot_type, prompt in prompts.items():
        lines = prompt.split('\n')
        num_examples = prompt.count('Informal:') - 1
        print(f"\n{'─' * 55}")
        print(f"  {shot_type} ({num_examples} example(s)):")
        print(f"  Prompt length: {len(prompt)} characters")
        print(f"  Prompt:")
        for line in lines[:4]:
            print(f"    {line}")
        if len(lines) > 4:
            print(f"    ... ({len(lines) - 4} more lines)")

compare_shot_types()
```

**Output:**
```
Zero-Shot vs One-Shot vs Few-Shot
============================================================
Task: Convert informal text to formal business English
Input: 'hey can u send me that report asap thx'

───────────────────────────────────────────────────────
  Zero-shot (0 example(s)):
  Prompt length: 79 characters
  Prompt:
    Convert this informal text to formal business English:
    'hey can u send me that report asap thx'

───────────────────────────────────────────────────────
  One-shot (1 example(s)):
  Prompt length: 241 characters
  Prompt:
    Convert informal text to formal business English.

    Example:
    ... (5 more lines)

───────────────────────────────────────────────────────
  Few-shot (3 example(s)):
  Prompt length: 543 characters
  Prompt:
    Convert informal text to formal business English.

    Informal: 'gonna need those numbers by friday'
    ... (12 more lines)
```

---

## In-Context Learning: Why Few-Shot Works

**In-context learning** is the ability of LLMs to learn patterns from examples provided in the prompt, without any changes to the model's parameters. The model is not being trained; it is recognizing patterns in real time.

```
+----------------------------------------------------------+
|         In-Context Learning Explained                     |
+----------------------------------------------------------+
|                                                            |
|  Traditional Machine Learning:                            |
|    1. Collect training data                               |
|    2. Train model (adjust parameters)                     |
|    3. Model learns the pattern                            |
|    Time: Hours to days                                    |
|                                                            |
|  In-Context Learning (few-shot):                          |
|    1. Put examples in the prompt                          |
|    2. Model recognizes the pattern                        |
|    3. Model applies the pattern to new input              |
|    Time: Instant (no training!)                           |
|                                                            |
|  Key insight:                                             |
|    The model's parameters do NOT change.                  |
|    It uses its existing knowledge to                      |
|    recognize and follow the pattern                       |
|    in the examples.                                       |
|                                                            |
+----------------------------------------------------------+
```

```python
# Demonstrating in-context learning

def in_context_learning_demo():
    """
    Show how few-shot examples teach the model a new pattern
    without any training.
    """

    print("In-Context Learning: Teaching Without Training")
    print("=" * 60)

    # Example: Teaching a custom format the model hasn't seen
    print("\nScenario: You have a custom data format your company uses.")
    print("No model was trained on it, but few-shot teaches it instantly.")
    print()

    prompt = """Convert product data to our internal format.

Product: iPhone 15 Pro | Category: Electronics | Price: $999 | Stock: 150
Output: [PROD] iPhone 15 Pro {cat:Electronics} {price:999} {qty:150}

Product: Nike Air Max | Category: Footwear | Price: $120 | Stock: 500
Output: [PROD] Nike Air Max {cat:Footwear} {price:120} {qty:500}

Product: Python Cookbook | Category: Books | Price: $45 | Stock: 80
Output: [PROD] Python Cookbook {cat:Books} {price:45} {qty:80}

Product: Standing Desk | Category: Furniture | Price: $350 | Stock: 25
Output:"""

    expected = "[PROD] Standing Desk {cat:Furniture} {price:350} {qty:25}"

    print("Prompt (with 3 examples):")
    for line in prompt.split('\n'):
        print(f"  {line}")
    print()
    print(f"Expected model output:")
    print(f"  {expected}")
    print()
    print("The model learned your custom format from just 3 examples!")
    print("No fine-tuning, no training, no code changes.")

in_context_learning_demo()
```

**Output:**
```
In-Context Learning: Teaching Without Training
============================================================

Scenario: You have a custom data format your company uses.
No model was trained on it, but few-shot teaches it instantly.

Prompt (with 3 examples):
  Convert product data to our internal format.

  Product: iPhone 15 Pro | Category: Electronics | Price: $999 | Stock: 150
  Output: [PROD] iPhone 15 Pro {cat:Electronics} {price:999} {qty:150}

  Product: Nike Air Max | Category: Footwear | Price: $120 | Stock: 500
  Output: [PROD] Nike Air Max {cat:Footwear} {price:120} {qty:500}

  Product: Python Cookbook | Category: Books | Price: $45 | Stock: 80
  Output: [PROD] Python Cookbook {cat:Books} {price:45} {qty:80}

  Product: Standing Desk | Category: Furniture | Price: $350 | Stock: 25
  Output:

Expected model output:
  [PROD] Standing Desk {cat:Furniture} {price:350} {qty:25}

The model learned your custom format from just 3 examples!
No fine-tuning, no training, no code changes.
```

---

## How to Format Examples

The way you format your examples matters. Consistent formatting helps the model recognize the pattern.

```python
# Best practices for formatting few-shot examples

def formatting_best_practices():
    """Show good and bad formatting for few-shot examples."""

    print("Formatting Few-Shot Examples")
    print("=" * 60)

    # Bad formatting: inconsistent
    print("\n  BAD: Inconsistent formatting")
    print("  " + "-" * 50)
    bad_format = """
    happy -> Positive
    This movie was awful - it's Negative
    Love it! => positive
    Boring movie. Classify: neg
    """
    for line in bad_format.strip().split('\n'):
        print(f"  {line.strip()}")
    print("  Problems: Different separators, inconsistent labels,")
    print("  no clear pattern for the model to follow.")

    # Good formatting: consistent
    print("\n  GOOD: Consistent formatting")
    print("  " + "-" * 50)
    good_format = """
    Review: "The movie was fantastic and entertaining."
    Sentiment: Positive

    Review: "This was the worst film I have ever seen."
    Sentiment: Negative

    Review: "A decent movie with some good moments."
    Sentiment: Positive

    Review: "Completely boring from start to finish."
    Sentiment: Negative
    """
    for line in good_format.strip().split('\n'):
        print(f"  {line.strip()}")
    print("  Strengths: Same labels, same separators, same structure,")
    print("  clear visual pattern.")

    # Guidelines
    print(f"\n{'=' * 60}")
    print("\nFormatting Guidelines:")
    guidelines = [
        "Use the SAME separator in every example (e.g., ' -> ')",
        "Use the SAME label format (e.g., always 'Positive', never 'pos')",
        "Keep example structure IDENTICAL across all examples",
        "Add blank lines between examples for readability",
        "Put the input and output on clearly labeled lines",
        "Use delimiters (quotes, brackets) around inputs consistently",
    ]
    for i, g in enumerate(guidelines, 1):
        print(f"  {i}. {g}")

formatting_best_practices()
```

**Output:**
```
Formatting Few-Shot Examples
============================================================

  BAD: Inconsistent formatting
  --------------------------------------------------
  happy -> Positive
  This movie was awful - it's Negative
  Love it! => positive
  Boring movie. Classify: neg
  Problems: Different separators, inconsistent labels,
  no clear pattern for the model to follow.

  GOOD: Consistent formatting
  --------------------------------------------------
  Review: "The movie was fantastic and entertaining."
  Sentiment: Positive

  Review: "This was the worst film I have ever seen."
  Sentiment: Negative

  Review: "A decent movie with some good moments."
  Sentiment: Positive

  Review: "Completely boring from start to finish."
  Sentiment: Negative
  Strengths: Same labels, same separators, same structure,
  clear visual pattern.

============================================================

Formatting Guidelines:
  1. Use the SAME separator in every example (e.g., ' -> ')
  2. Use the SAME label format (e.g., always 'Positive', never 'pos')
  3. Keep example structure IDENTICAL across all examples
  4. Add blank lines between examples for readability
  5. Put the input and output on clearly labeled lines
  6. Use delimiters (quotes, brackets) around inputs consistently
```

---

## Practical Few-Shot Examples

### Example 1: Classification

```python
# Few-shot classification prompt

def classification_example():
    """Demonstrate few-shot for text classification."""

    prompt = """Classify each customer message into one of these categories:
- Billing
- Technical Support
- Feature Request
- Complaint

Message: "I was charged twice for my subscription this month."
Category: Billing

Message: "The app keeps crashing when I try to upload photos."
Category: Technical Support

Message: "It would be great if you could add dark mode."
Category: Feature Request

Message: "Your service has been terrible lately. I want a refund."
Category: Complaint

Message: "Can you add support for exporting to PDF format?"
Category: Feature Request

Message: "I cannot log in to my account since the last update."
Category:"""

    print("Few-Shot Classification")
    print("=" * 60)
    print()
    print("Prompt:")
    for line in prompt.split('\n'):
        print(f"  {line}")
    print()
    print("Expected output: Technical Support")
    print()
    print("Why this works:")
    print("  - 5 examples cover all 4 categories")
    print("  - Consistent format (Message: ... / Category: ...)")
    print("  - Examples show a variety of phrasing styles")
    print("  - The last line ends with 'Category:' cueing the model")

classification_example()
```

**Output:**
```
Few-Shot Classification
============================================================

Prompt:
  Classify each customer message into one of these categories:
  - Billing
  - Technical Support
  - Feature Request
  - Complaint

  Message: "I was charged twice for my subscription this month."
  Category: Billing

  Message: "The app keeps crashing when I try to upload photos."
  Category: Technical Support

  Message: "It would be great if you could add dark mode."
  Category: Feature Request

  Message: "Your service has been terrible lately. I want a refund."
  Category: Complaint

  Message: "Can you add support for exporting to PDF format?"
  Category: Feature Request

  Message: "I cannot log in to my account since the last update."
  Category:

Expected output: Technical Support

Why this works:
  - 5 examples cover all 4 categories
  - Consistent format (Message: ... / Category: ...)
  - Examples show a variety of phrasing styles
  - The last line ends with 'Category:' cueing the model
```

### Example 2: Data Extraction

```python
# Few-shot data extraction

def extraction_example():
    """Demonstrate few-shot for structured data extraction."""

    prompt = """Extract person information from text and format as JSON.

Text: "Dr. Sarah Johnson is a 42-year-old cardiologist based in Chicago."
JSON: {"name": "Sarah Johnson", "title": "Dr.", "age": 42, "occupation": "cardiologist", "city": "Chicago"}

Text: "Meet Bob Smith, a 35-year-old software engineer from Seattle."
JSON: {"name": "Bob Smith", "title": null, "age": 35, "occupation": "software engineer", "city": "Seattle"}

Text: "Professor Maria Garcia, age 58, teaches physics at MIT in Boston."
JSON: {"name": "Maria Garcia", "title": "Professor", "age": 58, "occupation": "physics teacher", "city": "Boston"}

Text: "Mr. James Lee is a 29-year-old architect working in Denver."
JSON:"""

    expected = '{"name": "James Lee", "title": "Mr.", "age": 29, "occupation": "architect", "city": "Denver"}'

    print("Few-Shot Data Extraction")
    print("=" * 60)
    print()
    print("Prompt (3 examples):")
    for line in prompt.split('\n')[:8]:
        print(f"  {line}")
    print("  ... (more examples)")
    print()
    print("Expected output:")
    print(f"  {expected}")
    print()
    print("Key design choices:")
    print("  - Examples show exact JSON structure expected")
    print("  - 'null' example teaches handling of missing data")
    print("  - Variety in titles (Dr., Professor, none)")
    print("  - Consistent field ordering in JSON output")

extraction_example()
```

**Output:**
```
Few-Shot Data Extraction
============================================================

Prompt (3 examples):
  Extract person information from text and format as JSON.

  Text: "Dr. Sarah Johnson is a 42-year-old cardiologist based in Chicago."
  JSON: {"name": "Sarah Johnson", "title": "Dr.", "age": 42, "occupation": "cardiologist", "city": "Chicago"}

  Text: "Meet Bob Smith, a 35-year-old software engineer from Seattle."
  JSON: {"name": "Bob Smith", "title": null, "age": 35, "occupation": "software engineer", "city": "Seattle"}
  ... (more examples)

Expected output:
  {"name": "James Lee", "title": "Mr.", "age": 29, "occupation": "architect", "city": "Denver"}

Key design choices:
  - Examples show exact JSON structure expected
  - 'null' example teaches handling of missing data
  - Variety in titles (Dr., Professor, none)
  - Consistent field ordering in JSON output
```

### Example 3: Code Transformation

```python
# Few-shot code transformation

def code_transformation_example():
    """Demonstrate few-shot for converting code patterns."""

    prompt = """Convert Python for-loops to list comprehensions.

# Input:
result = []
for x in numbers:
    if x > 0:
        result.append(x * 2)
# Output:
result = [x * 2 for x in numbers if x > 0]

# Input:
names = []
for person in people:
    names.append(person['name'].upper())
# Output:
names = [person['name'].upper() for person in people]

# Input:
squares = []
for i in range(10):
    squares.append(i ** 2)
# Output:
squares = [i ** 2 for i in range(10)]

# Input:
evens = []
for num in data:
    if num % 2 == 0:
        evens.append(num)
# Output:"""

    expected = "evens = [num for num in data if num % 2 == 0]"

    print("Few-Shot Code Transformation")
    print("=" * 60)
    print()
    print("Task: Convert for-loops to list comprehensions")
    print()
    print("3 examples teach the pattern, then model applies it.")
    print(f"\nExpected output: {expected}")
    print()
    print("This works because:")
    print("  - Examples show progressively simpler cases")
    print("  - Pattern: for-loop with append -> list comprehension")
    print("  - Includes cases with and without if-conditions")
    print("  - Uses # Input: / # Output: as clear delimiters")

code_transformation_example()
```

**Output:**
```
Few-Shot Code Transformation
============================================================

Task: Convert for-loops to list comprehensions

3 examples teach the pattern, then model applies it.

Expected output: evens = [num for num in data if num % 2 == 0]

This works because:
  - Examples show progressively simpler cases
  - Pattern: for-loop with append -> list comprehension
  - Includes cases with and without if-conditions
  - Uses # Input: / # Output: as clear delimiters
```

---

## When Few-Shot Helps Most

```python
# Guide for when to use few-shot prompting

def when_to_use_few_shot():
    """Show when few-shot helps and when it doesn't."""

    scenarios = [
        {
            "scenario": "Custom output format",
            "helps": True,
            "reason": "Examples teach exact formatting better than words",
            "example": "Converting data to your company's internal format"
        },
        {
            "scenario": "Classification with specific labels",
            "helps": True,
            "reason": "Shows model exactly which labels to use",
            "example": "Categorizing tickets as P1/P2/P3/P4"
        },
        {
            "scenario": "Pattern-based transformations",
            "helps": True,
            "reason": "Pattern is easier to show than to describe",
            "example": "Rewriting sentences in a specific style"
        },
        {
            "scenario": "Ambiguous tasks",
            "helps": True,
            "reason": "Examples clarify what you actually want",
            "example": "'Summarize this' - examples show desired length/style"
        },
        {
            "scenario": "Simple factual questions",
            "helps": False,
            "reason": "Model already knows how to answer questions",
            "example": "'What is the capital of France?' needs no examples"
        },
        {
            "scenario": "Creative writing with no constraints",
            "helps": False,
            "reason": "Examples can limit creativity rather than help it",
            "example": "Writing a poem - examples might cause imitation"
        },
        {
            "scenario": "Very long outputs",
            "helps": False,
            "reason": "Examples use too many tokens from context window",
            "example": "Writing a full essay - examples waste too much space"
        },
    ]

    print("When to Use Few-Shot Prompting")
    print("=" * 60)

    print("\n  FEW-SHOT HELPS:")
    for s in scenarios:
        if s['helps']:
            print(f"\n    + {s['scenario']}")
            print(f"      Why: {s['reason']}")
            print(f"      Example: {s['example']}")

    print(f"\n  FEW-SHOT NOT NEEDED:")
    for s in scenarios:
        if not s['helps']:
            print(f"\n    - {s['scenario']}")
            print(f"      Why: {s['reason']}")
            print(f"      Example: {s['example']}")

when_to_use_few_shot()
```

**Output:**
```
When to Use Few-Shot Prompting
============================================================

  FEW-SHOT HELPS:

    + Custom output format
      Why: Examples teach exact formatting better than words
      Example: Converting data to your company's internal format

    + Classification with specific labels
      Why: Shows model exactly which labels to use
      Example: Categorizing tickets as P1/P2/P3/P4

    + Pattern-based transformations
      Why: Pattern is easier to show than to describe
      Example: Rewriting sentences in a specific style

    + Ambiguous tasks
      Why: Examples clarify what you actually want
      Example: 'Summarize this' - examples show desired length/style

  FEW-SHOT NOT NEEDED:

    - Simple factual questions
      Why: Model already knows how to answer questions
      Example: 'What is the capital of France?' needs no examples

    - Creative writing with no constraints
      Why: Examples can limit creativity rather than help it
      Example: Writing a poem - examples might cause imitation

    - Very long outputs
      Why: Examples use too many tokens from context window
      Example: Writing a full essay - examples waste too much space
```

---

## Selecting Good Examples

```python
# Guidelines for selecting few-shot examples

def example_selection_guide():
    """Show how to choose the best examples for few-shot."""

    print("How to Select Good Few-Shot Examples")
    print("=" * 60)

    guidelines = [
        {
            "rule": "Cover the variety of inputs",
            "good": "Include examples of different types you expect",
            "bad": "Using all similar examples",
            "detail": "If classifying reviews, include both positive and negative"
        },
        {
            "rule": "Include edge cases",
            "good": "Show tricky or ambiguous inputs in your examples",
            "bad": "Only showing easy, obvious cases",
            "detail": "Include a neutral review if it could be misclassified"
        },
        {
            "rule": "Match your actual data",
            "good": "Examples should look like real inputs you will process",
            "bad": "Using perfect, clean examples for messy real data",
            "detail": "If real data has typos, include typos in examples"
        },
        {
            "rule": "Use 3 to 5 examples",
            "good": "Enough to show the pattern without wasting tokens",
            "bad": "Using 20 examples (wastes context window)",
            "detail": "Studies show diminishing returns after 5-8 examples"
        },
        {
            "rule": "Order matters",
            "good": "Put the most representative examples first",
            "bad": "Random ordering with edge cases first",
            "detail": "Models pay more attention to examples near the end"
        },
    ]

    for i, g in enumerate(guidelines, 1):
        print(f"\n  Rule {i}: {g['rule']}")
        print(f"    Good: {g['good']}")
        print(f"    Bad:  {g['bad']}")
        print(f"    Tip:  {g['detail']}")

example_selection_guide()
```

**Output:**
```
How to Select Good Few-Shot Examples
============================================================

  Rule 1: Cover the variety of inputs
    Good: Include examples of different types you expect
    Bad:  Using all similar examples
    Tip:  If classifying reviews, include both positive and negative

  Rule 2: Include edge cases
    Good: Show tricky or ambiguous inputs in your examples
    Bad:  Only showing easy, obvious cases
    Tip:  Include a neutral review if it could be misclassified

  Rule 3: Match your actual data
    Good: Examples should look like real inputs you will process
    Bad:  Using perfect, clean examples for messy real data
    Tip:  If real data has typos, include typos in examples

  Rule 4: Use 3 to 5 examples
    Good: Enough to show the pattern without wasting tokens
    Bad:  Using 20 examples (wastes context window)
    Tip:  Studies show diminishing returns after 5-8 examples

  Rule 5: Order matters
    Good: Put the most representative examples first
    Bad:  Random ordering with edge cases first
    Tip:  Models pay more attention to examples near the end
```

---

## Building Few-Shot Prompts Programmatically

```python
# Building few-shot prompts in code

def build_few_shot_prompt(task_description, examples, new_input,
                          input_label="Input", output_label="Output"):
    """
    Build a few-shot prompt programmatically.

    Args:
        task_description: What the task is
        examples: List of (input, output) tuples
        new_input: The new input to process
        input_label: Label for input field
        output_label: Label for output field

    Returns:
        Complete few-shot prompt string
    """
    parts = [task_description, ""]

    for inp, out in examples:
        parts.append(f"{input_label}: {inp}")
        parts.append(f"{output_label}: {out}")
        parts.append("")  # Blank line separator

    parts.append(f"{input_label}: {new_input}")
    parts.append(f"{output_label}:")

    prompt = "\n".join(parts)
    return prompt

# Example: Sentiment analysis
examples = [
    ("I love this product! Best purchase ever.", "Positive"),
    ("Terrible quality. Broke after one day.", "Negative"),
    ("It works fine. Nothing special.", "Neutral"),
    ("Absolutely amazing! Highly recommend.", "Positive"),
    ("Would not buy again. Very disappointed.", "Negative"),
]

prompt = build_few_shot_prompt(
    task_description="Classify the sentiment of each product review.",
    examples=examples,
    new_input="The delivery was fast but the item was damaged.",
    input_label="Review",
    output_label="Sentiment"
)

print("Programmatically Built Few-Shot Prompt")
print("=" * 60)
print()
print(prompt)
print()
print(f"Total examples: {len(examples)}")
print(f"Prompt length: {len(prompt)} characters")
```

**Output:**
```
Programmatically Built Few-Shot Prompt
============================================================

Classify the sentiment of each product review.

Review: I love this product! Best purchase ever.
Sentiment: Positive

Review: Terrible quality. Broke after one day.
Sentiment: Negative

Review: It works fine. Nothing special.
Sentiment: Neutral

Review: Absolutely amazing! Highly recommend.
Sentiment: Positive

Review: Would not buy again. Very disappointed.
Sentiment: Negative

Review: The delivery was fast but the item was damaged.
Sentiment:

Total examples: 5
Prompt length: 471 characters
```

**Line-by-line explanation:**

- `build_few_shot_prompt(...)`: A reusable function that constructs few-shot prompts from a task description and example pairs. This is useful when you process many items with the same pattern.
- `input_label` and `output_label`: Customizable labels let you use this function for different tasks ("Review/Sentiment", "Question/Answer", "Code/Refactored").
- The function adds a blank line between examples for readability and ends with the output label followed by a colon, cueing the model to complete it.

---

## Common Mistakes

| Mistake | Why It Is Wrong | What to Do Instead |
|---------|----------------|-------------------|
| Using too many examples | Wastes context window tokens; diminishing returns | Use 3-5 well-chosen examples |
| Inconsistent formatting | Model cannot identify the pattern | Use identical structure for every example |
| All examples are the same type | Model overfits to one pattern | Include diverse examples covering different cases |
| Examples do not match real data | Model learns wrong patterns | Use examples that look like actual inputs |
| Ignoring example order | Models are sensitive to order | Put representative examples first; edge cases in middle |

---

## Best Practices

1. **Start with 3 examples and add more only if needed.** Three well-chosen examples often work as well as ten mediocre ones.

2. **Make your examples diverse.** Cover different categories, lengths, styles, and edge cases in your examples.

3. **Keep formatting perfectly consistent.** Use the same labels, separators, and structure in every example. Even small inconsistencies can confuse the model.

4. **Build prompts programmatically for repeated tasks.** If you process many items with the same pattern, write a function that constructs the prompt.

5. **Test with and without examples.** Sometimes zero-shot works just as well. Only add examples when they improve output quality.

---

## Quick Summary

Few-shot prompting provides examples in the prompt to teach the model a pattern through in-context learning. Zero-shot uses no examples (just instructions), one-shot uses one example, and few-shot uses two to ten examples. The model does not retrain on these examples; it recognizes patterns using its existing knowledge. Consistent formatting, diverse examples, and appropriate example count are the keys to effective few-shot prompting. This technique is most valuable for custom formats, classification tasks, and pattern-based transformations.

---

## Key Points

- Zero-shot uses only instructions; few-shot adds examples to teach the pattern
- In-context learning lets models recognize patterns from examples without retraining
- Consistent formatting across all examples is critical for the model to identify the pattern
- 3-5 diverse examples typically give the best results for most tasks
- Few-shot is most helpful for custom formats, classification, and structured extraction
- Few-shot is less helpful for creative writing, simple questions, and tasks needing long outputs
- Build few-shot prompts programmatically when processing many items with the same pattern
- Example selection matters: cover variety, include edge cases, match real data

---

## Practice Questions

1. Explain the difference between zero-shot and few-shot prompting. When would you choose each approach?

2. You are building a system to classify customer emails into five categories. Design a few-shot prompt with examples. How many examples would you include and why?

3. Why does formatting consistency matter in few-shot prompts? What happens if your examples use different separators or label formats?

4. A colleague says "I used 50 examples in my few-shot prompt and it works great." What potential problems might they face? What would you recommend?

5. Explain in-context learning in simple terms. How is it different from fine-tuning a model?

---

## Exercises

### Exercise 1: Build a Classifier

Create a few-shot prompt that classifies programming questions into categories (Syntax, Logic, Performance, Design). Include 4 examples and test it with 5 new questions. Track the accuracy.

### Exercise 2: Format Converter

Create a few-shot prompt that converts natural language dates to ISO format:
- "January 5th, 2024" -> "2024-01-05"
- Include examples for different date formats (US, European, informal)
- Test with 10 different date formats

### Exercise 3: Comparison Study

Choose a task and create three versions of the prompt:
1. Zero-shot (instructions only)
2. One-shot (one example)
3. Few-shot (five examples)

Test all three on 10 inputs and compare accuracy, consistency, and output quality.

---

## What Is Next?

Few-shot prompting teaches the model what format to follow. But what about tasks that require reasoning? In the next chapter, "Chain-of-Thought Prompting", you will learn how to make LLMs think step by step. You will discover that asking a model to show its reasoning dramatically improves accuracy on math, logic, and complex analysis tasks. You will also learn about the ReAct pattern, self-consistency, and the tree of thoughts approach.
