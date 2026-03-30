# Chapter 12: Prompt Templates and Evaluation

## What You Will Learn

In this chapter, you will learn:

- How to create reusable prompt templates with variables
- How to use f-strings and Jinja2 for template rendering
- How to measure the quality of your prompts
- How to run A/B tests to compare different prompts
- What evaluation metrics tell you about prompt performance
- How to iterate and improve prompts systematically

## Why This Chapter Matters

Imagine you are a chef. You would not cook a different way every time. You would follow a recipe, taste the result, adjust the seasoning, and try again until it is perfect. Then you would write down the final recipe so you can repeat it.

Prompt engineering works the same way. In the early chapters, you wrote prompts by hand. That works for experiments, but not for production. You need templates that you can reuse with different inputs. And you need a way to measure whether one prompt is better than another.

Without evaluation, you are guessing. "This prompt seems better" is not good enough. You need numbers. How often does the prompt produce the right answer? How fast does it respond? How much does it cost? This chapter gives you the tools to answer these questions.

---

## What Is a Prompt Template?

A prompt template is a reusable prompt with placeholders for variable parts.

```
+------------------------------------------------------------------+
|                    PROMPT TEMPLATE CONCEPT                        |
|                                                                   |
|  Template:                                                        |
|  "Summarize the following {document_type} in {num_sentences}      |
|   sentences. Focus on {focus_area}."                              |
|                                                                   |
|  Variables:                                                       |
|  +----------------+  +----------------+  +----------------+      |
|  | document_type  |  | num_sentences  |  | focus_area     |      |
|  | = "email"      |  | = 3            |  | = "action      |      |
|  |                |  |                |  |   items"       |      |
|  +----------------+  +----------------+  +----------------+      |
|                                                                   |
|  Result:                                                          |
|  "Summarize the following email in 3 sentences. Focus on          |
|   action items."                                                  |
|                                                                   |
|  Same template, different variables = different prompts           |
+------------------------------------------------------------------+
```

Think of a prompt template like a form letter. The letter stays the same, but you change the name and address for each recipient.

> **Prompt Template:** A string with placeholders (variables) that get replaced with actual values before sending to the LLM. Templates let you reuse the same prompt structure with different inputs.

---

## Templates with Python f-strings

The simplest way to create prompt templates in Python is with f-strings.

> **f-string (formatted string literal):** A Python string prefixed with `f` that lets you embed expressions inside curly braces `{}`. The expressions are evaluated and inserted into the string at runtime.

```python
def create_summary_prompt(text, num_sentences=3, style="professional"):
    """Create a summary prompt using f-string template."""
    prompt = f"""Summarize the following text in exactly {num_sentences} sentences.
Use a {style} tone.

Text to summarize:
{text}

Summary:"""
    return prompt


# Use the template with different inputs
email_text = """
Hi team, just wanted to update you on the Q3 results. Revenue
is up 15% compared to last quarter. The new product launch in
September exceeded expectations with 10,000 units sold in the
first week. However, customer support tickets have increased
by 30%, which we need to address. Let's discuss in Friday's
meeting.
"""

# Professional summary
prompt1 = create_summary_prompt(email_text, num_sentences=2, style="professional")
print("=== Professional Prompt ===")
print(prompt1)
print()

# Casual summary
prompt2 = create_summary_prompt(email_text, num_sentences=1, style="casual")
print("=== Casual Prompt ===")
print(prompt2)
```

**Output:**
```
=== Professional Prompt ===
Summarize the following text in exactly 2 sentences.
Use a professional tone.

Text to summarize:

Hi team, just wanted to update you on the Q3 results. Revenue
is up 15% compared to last quarter. The new product launch in
September exceeded expectations with 10,000 units sold in the
first week. However, customer support tickets have increased
by 30%, which we need to address. Let's discuss in Friday's
meeting.


Summary:

=== Casual Prompt ===
Summarize the following text in exactly 1 sentences.
Use a casual tone.

Text to summarize:

Hi team, just wanted to update you on the Q3 results. Revenue
is up 15% compared to last quarter. The new product launch in
September exceeded expectations with 10,000 units sold in the
first week. However, customer support tickets have increased
by 30%, which we need to address. Let's discuss in Friday's
meeting.


Summary:
```

**Line-by-line explanation:**

- `def create_summary_prompt(text, num_sentences=3, style="professional")` defines a function that creates prompts. Default values make it easy to use.
- `f"""..."""` is a multi-line f-string. Triple quotes allow the string to span multiple lines.
- `{num_sentences}`, `{style}`, and `{text}` are placeholders that get replaced with the actual values when the function is called.
- The same template generates different prompts by passing different arguments. This is reuse.

---

## Templates with Jinja2

For more complex templates, Jinja2 is the industry standard. It supports conditionals, loops, and filters.

> **Jinja2:** A popular Python templating engine. It lets you create templates with variables, if-else conditions, for loops, and filters. It is widely used in web development and increasingly in prompt engineering.

```python
# Install: pip install jinja2
from jinja2 import Template

# Basic template with variables
basic_template = Template("""
You are a {{ role }} assistant.
Analyze the following {{ document_type }} and provide:
{% for task in tasks %}
- {{ task }}
{% endfor %}

Document:
{{ document }}
""")

# Render the template
prompt = basic_template.render(
    role="financial",
    document_type="quarterly report",
    tasks=[
        "Key revenue figures",
        "Year-over-year growth",
        "Areas of concern",
        "Recommendations"
    ],
    document="Q3 revenue was $2.5M, up from $2.1M in Q3 last year..."
)

print(prompt)
```

**Output:**
```

You are a financial assistant.
Analyze the following quarterly report and provide:

- Key revenue figures

- Year-over-year growth

- Areas of concern

- Recommendations


Document:
Q3 revenue was $2.5M, up from $2.1M in Q3 last year...
```

**Line-by-line explanation:**

- `Template("""...""")` creates a Jinja2 template object from a string.
- `{{ role }}` is a Jinja2 variable placeholder. Double curly braces mark variables (unlike f-strings which use single curly braces).
- `{% for task in tasks %}` starts a for loop. Jinja2 uses `{% %}` for logic blocks.
- `{{ task }}` prints the current item in the loop.
- `{% endfor %}` ends the for loop. Unlike Python, Jinja2 needs explicit end tags.
- `basic_template.render(...)` fills in all the variables and returns the final string.

---

## Jinja2 Templates with Conditionals

Jinja2 lets you include or exclude parts of the prompt based on conditions.

```python
from jinja2 import Template

analysis_template = Template("""
Analyze this customer review for the product "{{ product_name }}".

{% if include_sentiment %}
1. Determine the overall sentiment (positive, negative, or mixed).
{% endif %}

{% if include_key_points %}
2. List the key points mentioned by the customer.
{% endif %}

{% if language != "english" %}
Note: The review is in {{ language }}. Provide your analysis in English.
{% endif %}

{% if word_limit %}
Keep your analysis under {{ word_limit }} words.
{% endif %}

Review:
{{ review_text }}
""")

# Render with different options
prompt = analysis_template.render(
    product_name="CloudSync Pro",
    include_sentiment=True,
    include_key_points=True,
    language="english",
    word_limit=100,
    review_text="Great software but the sync takes too long on large files."
)

print(prompt)
```

**Output:**
```

Analyze this customer review for the product "CloudSync Pro".


1. Determine the overall sentiment (positive, negative, or mixed).



2. List the key points mentioned by the customer.




Keep your analysis under 100 words.


Review:
Great software but the sync takes too long on large files.
```

**Line-by-line explanation:**

- `{% if include_sentiment %}` only includes the sentiment instruction when `include_sentiment` is `True`. This lets you build modular prompts.
- `{% if language != "english" %}` adds a translation note only for non-English reviews.
- `{% if word_limit %}` adds a word limit only when one is specified. If `word_limit` is `None` or `0`, this block is skipped.
- This is powerful because the same template can generate simple or complex prompts depending on the options.

---

## Building a Prompt Template Library

For real projects, organize your templates in a structured way.

```python
from jinja2 import Template
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class PromptTemplate:
    """A reusable prompt template with metadata."""
    name: str
    description: str
    template: str
    version: str = "1.0"
    default_vars: Optional[Dict[str, Any]] = None

    def render(self, **kwargs) -> str:
        """Render the template with given variables."""
        variables = {}
        if self.default_vars:
            variables.update(self.default_vars)
        variables.update(kwargs)

        jinja_template = Template(self.template)
        return jinja_template.render(**variables)


# Create a library of templates
TEMPLATES = {
    "summarize": PromptTemplate(
        name="summarize",
        description="Summarize text with configurable length and style",
        template="""Summarize the following text in {{ num_sentences }} sentences.
Style: {{ style }}
Audience: {{ audience }}

Text:
{{ text }}

Summary:""",
        default_vars={
            "num_sentences": 3,
            "style": "professional",
            "audience": "general"
        }
    ),
    "classify": PromptTemplate(
        name="classify",
        description="Classify text into predefined categories",
        template="""Classify the following text into one of these categories:
{% for category in categories %}
- {{ category }}
{% endfor %}

Respond with ONLY the category name, nothing else.

Text: {{ text }}

Category:""",
        default_vars={
            "categories": ["positive", "negative", "neutral"]
        }
    ),
    "extract": PromptTemplate(
        name="extract",
        description="Extract specific information from text",
        template="""Extract the following information from the text:
{% for field in fields %}
- {{ field }}
{% endfor %}

Format your response as JSON.

Text:
{{ text }}""",
        default_vars={"fields": ["name", "date", "location"]}
    ),
}


# Use the templates
print("=== Summarize Template ===")
prompt1 = TEMPLATES["summarize"].render(
    text="The stock market rose 2% today...",
    num_sentences=2
)
print(prompt1)
print()

print("=== Classify Template ===")
prompt2 = TEMPLATES["classify"].render(
    text="This product is absolutely terrible!",
    categories=["positive", "negative", "neutral", "mixed"]
)
print(prompt2)
print()

print("=== Extract Template ===")
prompt3 = TEMPLATES["extract"].render(
    text="Meeting with Sarah on March 15 at the NYC office",
    fields=["person name", "date", "location"]
)
print(prompt3)
```

**Output:**
```
=== Summarize Template ===
Summarize the following text in 2 sentences.
Style: professional
Audience: general

Text:
The stock market rose 2% today...

Summary:

=== Classify Template ===
Classify the following text into one of these categories:

- positive

- negative

- neutral

- mixed


Respond with ONLY the category name, nothing else.

Text: This product is absolutely terrible!

Category:

=== Extract Template ===
Extract the following information from the text:

- person name

- date

- location


Format your response as JSON.

Text:
Meeting with Sarah on March 15 at the NYC office
```

**Line-by-line explanation:**

- `@dataclass` creates a class that automatically generates `__init__` and other methods. It is a clean way to define data containers.
- `PromptTemplate` stores the template string, a description, a version, and default variable values.
- `render()` merges default variables with provided variables. Provided values override defaults. So if the default `num_sentences` is 3 but you pass 2, it uses 2.
- `TEMPLATES` is a dictionary that acts as a template library. You look up templates by name.
- This pattern is used in production systems. Templates are versioned so you can track changes over time.

---

## Measuring Prompt Quality

How do you know if your prompt is good? You measure it. Here are the key metrics.

```
+------------------------------------------------------------------+
|                 PROMPT EVALUATION METRICS                         |
|                                                                   |
|  +------------------+  +------------------+  +------------------+|
|  |   Accuracy       |  |  Consistency     |  |  Relevance       ||
|  |  Is the answer   |  |  Does it give    |  |  Is the answer   ||
|  |  correct?        |  |  the same answer |  |  on topic?       ||
|  |                  |  |  every time?     |  |                  ||
|  +------------------+  +------------------+  +------------------+|
|                                                                   |
|  +------------------+  +------------------+  +------------------+|
|  |   Completeness   |  |  Format          |  |  Cost            ||
|  |  Does it cover   |  |  Compliance      |  |  Efficiency      ||
|  |  all required    |  |  Does it follow  |  |  Tokens used,    ||
|  |  points?         |  |  the format?     |  |  API cost        ||
|  +------------------+  +------------------+  +------------------+|
+------------------------------------------------------------------+
```

> **Evaluation Metric:** A number that measures how well your prompt performs on a specific quality. For example, accuracy might be 85%, meaning the prompt gives the correct answer 85 out of 100 times.

---

## Building a Simple Evaluation Framework

```python
from openai import OpenAI
import json
import time

client = OpenAI()

def evaluate_prompt(prompt_template, test_cases, model="gpt-4o-mini"):
    """
    Evaluate a prompt template against test cases.

    Args:
        prompt_template: A string with {input} placeholder
        test_cases: List of dicts with 'input' and 'expected' keys
        model: Which model to use

    Returns:
        Dictionary with evaluation results
    """
    results = {
        "total": len(test_cases),
        "correct": 0,
        "incorrect": 0,
        "errors": 0,
        "total_tokens": 0,
        "responses": []
    }

    for i, test in enumerate(test_cases):
        try:
            prompt = prompt_template.format(input=test["input"])

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )

            answer = response.choices[0].message.content.strip().lower()
            expected = test["expected"].lower()
            is_correct = expected in answer

            tokens_used = response.usage.total_tokens
            results["total_tokens"] += tokens_used

            if is_correct:
                results["correct"] += 1
            else:
                results["incorrect"] += 1

            results["responses"].append({
                "input": test["input"],
                "expected": expected,
                "actual": answer,
                "correct": is_correct,
                "tokens": tokens_used
            })

        except Exception as e:
            results["errors"] += 1
            results["responses"].append({
                "input": test["input"],
                "expected": test["expected"],
                "error": str(e)
            })

    # Calculate metrics
    results["accuracy"] = results["correct"] / results["total"]
    results["avg_tokens"] = results["total_tokens"] / max(results["total"] - results["errors"], 1)

    return results

# Define test cases for sentiment classification
sentiment_tests = [
    {"input": "This product is amazing! Best purchase ever!", "expected": "positive"},
    {"input": "Terrible quality. Broke after one day.", "expected": "negative"},
    {"input": "It works fine. Nothing special.", "expected": "neutral"},
    {"input": "Love the design but the battery is awful.", "expected": "mixed"},
    {"input": "Absolutely wonderful experience!", "expected": "positive"},
    {"input": "Worst customer service I have ever seen.", "expected": "negative"},
    {"input": "The product arrived on time.", "expected": "neutral"},
    {"input": "Great features but too expensive.", "expected": "mixed"},
]

# Test a prompt
prompt_v1 = """Classify the sentiment of this text as positive, negative, neutral, or mixed.
Respond with ONLY one word.

Text: {input}

Sentiment:"""

print("Evaluating prompt v1...")
results = evaluate_prompt(prompt_v1, sentiment_tests)

print(f"\nResults:")
print(f"  Accuracy:    {results['accuracy']:.1%}")
print(f"  Correct:     {results['correct']}/{results['total']}")
print(f"  Avg tokens:  {results['avg_tokens']:.0f}")
print(f"\nDetailed results:")
for r in results["responses"]:
    if "error" not in r:
        status = "PASS" if r["correct"] else "FAIL"
        print(f"  [{status}] Expected: {r['expected']:8s} | Got: {r['actual']}")
```

**Output:**
```
Evaluating prompt v1...

Results:
  Accuracy:    87.5%
  Correct:     7/8
  Avg tokens:  38

Detailed results:
  [PASS] Expected: positive | Got: positive
  [PASS] Expected: negative | Got: negative
  [PASS] Expected: neutral  | Got: neutral
  [PASS] Expected: mixed    | Got: mixed
  [PASS] Expected: positive | Got: positive
  [PASS] Expected: negative | Got: negative
  [FAIL] Expected: neutral  | Got: positive
  [PASS] Expected: mixed    | Got: mixed
```

**Line-by-line explanation:**

- `evaluate_prompt()` takes a template, a list of test cases, and runs each test case through the LLM.
- `prompt_template.format(input=test["input"])` fills the `{input}` placeholder with the actual text.
- `temperature=0` makes the model deterministic (less random). This is important for evaluation because you want reproducible results.
- `expected in answer` checks if the expected label appears in the model's response. Using `in` instead of `==` handles cases where the model adds extra text.
- `results["accuracy"]` is the percentage of correct answers. This single number tells you how good the prompt is.
- `results["avg_tokens"]` tracks efficiency. Fewer tokens means lower cost.

---

## A/B Testing Prompts

A/B testing means comparing two versions of a prompt to see which one performs better.

```python
def ab_test_prompts(prompt_a, prompt_b, test_cases, model="gpt-4o-mini"):
    """
    Compare two prompts head-to-head.

    Returns comparison results with a winner.
    """
    print("Testing Prompt A...")
    results_a = evaluate_prompt(prompt_a, test_cases, model)

    print("Testing Prompt B...")
    results_b = evaluate_prompt(prompt_b, test_cases, model)

    print("\n" + "=" * 50)
    print("A/B TEST RESULTS")
    print("=" * 50)

    metrics = [
        ("Accuracy", f"{results_a['accuracy']:.1%}", f"{results_b['accuracy']:.1%}"),
        ("Correct", f"{results_a['correct']}/{results_a['total']}", f"{results_b['correct']}/{results_b['total']}"),
        ("Avg Tokens", f"{results_a['avg_tokens']:.0f}", f"{results_b['avg_tokens']:.0f}"),
        ("Total Tokens", f"{results_a['total_tokens']}", f"{results_b['total_tokens']}"),
    ]

    print(f"\n{'Metric':<15} {'Prompt A':<15} {'Prompt B':<15}")
    print("-" * 45)
    for name, val_a, val_b in metrics:
        print(f"{name:<15} {val_a:<15} {val_b:<15}")

    # Determine winner
    if results_a["accuracy"] > results_b["accuracy"]:
        winner = "Prompt A"
    elif results_b["accuracy"] > results_a["accuracy"]:
        winner = "Prompt B"
    else:
        # Same accuracy, prefer fewer tokens
        if results_a["total_tokens"] < results_b["total_tokens"]:
            winner = "Prompt A (same accuracy, fewer tokens)"
        elif results_b["total_tokens"] < results_a["total_tokens"]:
            winner = "Prompt B (same accuracy, fewer tokens)"
        else:
            winner = "Tie"

    print(f"\nWinner: {winner}")

    return results_a, results_b

# Define two prompt versions
prompt_a = """Classify the sentiment: positive, negative, neutral, or mixed.
One word only.

Text: {input}"""

prompt_b = """You are a sentiment analysis expert. Analyze the emotional tone
of the following text and classify it into exactly one category:
- positive: The text expresses satisfaction, happiness, or approval
- negative: The text expresses dissatisfaction, frustration, or disapproval
- neutral: The text is factual with no strong emotion
- mixed: The text contains both positive and negative sentiments

Respond with ONLY the category name.

Text: {input}

Category:"""

# Run the A/B test
results_a, results_b = ab_test_prompts(prompt_a, prompt_b, sentiment_tests)
```

**Output:**
```
Testing Prompt A...
Testing Prompt B...

==================================================
A/B TEST RESULTS
==================================================

Metric          Prompt A        Prompt B
---------------------------------------------
Accuracy        75.0%           87.5%
Correct         6/8             7/8
Avg Tokens      32              45
Total Tokens    256             360

Winner: Prompt B
```

**Line-by-line explanation:**

- `ab_test_prompts()` runs both prompts against the same test cases and compares results.
- Prompt A is short and simple. Prompt B is longer with detailed category definitions.
- The function compares accuracy first. If accuracy is the same, it prefers the prompt that uses fewer tokens (cheaper).
- In this example, Prompt B wins because it is more accurate even though it uses more tokens. The detailed definitions help the model understand exactly what each category means.

---

## Evaluation Metrics in Depth

Let us build a more complete evaluation system.

```python
from typing import List, Dict
import statistics

def comprehensive_evaluation(
    prompt_template: str,
    test_cases: List[Dict],
    num_runs: int = 3,
    model: str = "gpt-4o-mini"
) -> Dict:
    """
    Run multiple evaluation rounds and compute comprehensive metrics.

    Multiple runs help measure consistency - does the model give
    the same answer every time?
    """
    all_runs = []

    for run in range(num_runs):
        results = evaluate_prompt(prompt_template, test_cases, model)
        all_runs.append(results)

    # Compute aggregate metrics
    accuracies = [r["accuracy"] for r in all_runs]
    token_counts = [r["avg_tokens"] for r in all_runs]

    # Check consistency: for each test case, how often do all runs agree?
    consistency_scores = []
    for i in range(len(test_cases)):
        answers = []
        for run in all_runs:
            if i < len(run["responses"]) and "actual" in run["responses"][i]:
                answers.append(run["responses"][i]["actual"])
        if answers:
            most_common = max(set(answers), key=answers.count)
            agreement = answers.count(most_common) / len(answers)
            consistency_scores.append(agreement)

    report = {
        "mean_accuracy": statistics.mean(accuracies),
        "std_accuracy": statistics.stdev(accuracies) if len(accuracies) > 1 else 0,
        "min_accuracy": min(accuracies),
        "max_accuracy": max(accuracies),
        "mean_tokens": statistics.mean(token_counts),
        "consistency": statistics.mean(consistency_scores) if consistency_scores else 0,
        "num_runs": num_runs,
        "num_test_cases": len(test_cases),
    }

    return report


def print_evaluation_report(report: Dict):
    """Print a formatted evaluation report."""
    print("=" * 50)
    print("COMPREHENSIVE EVALUATION REPORT")
    print("=" * 50)
    print(f"Test cases:     {report['num_test_cases']}")
    print(f"Runs:           {report['num_runs']}")
    print(f"")
    print(f"Accuracy:")
    print(f"  Mean:         {report['mean_accuracy']:.1%}")
    print(f"  Std Dev:      {report['std_accuracy']:.1%}")
    print(f"  Range:        {report['min_accuracy']:.1%} - {report['max_accuracy']:.1%}")
    print(f"")
    print(f"Consistency:    {report['consistency']:.1%}")
    print(f"Avg Tokens:     {report['mean_tokens']:.0f}")
    print("=" * 50)


# Example usage
report = comprehensive_evaluation(
    prompt_template=prompt_b,
    test_cases=sentiment_tests,
    num_runs=3
)

print_evaluation_report(report)
```

**Output:**
```
==================================================
COMPREHENSIVE EVALUATION REPORT
==================================================
Test cases:     8
Runs:           3

Accuracy:
  Mean:         87.5%
  Std Dev:      0.0%
  Range:        87.5% - 87.5%

Consistency:    100.0%
Avg Tokens:     45
==================================================
```

**Line-by-line explanation:**

- `num_runs=3` means we run the evaluation 3 times. Running multiple times reveals inconsistency. If a prompt gets different answers each time, it is unreliable.
- `statistics.mean(accuracies)` calculates the average accuracy across all runs.
- `statistics.stdev(accuracies)` calculates the standard deviation. A low standard deviation means consistent results. A high one means the prompt is unreliable.
- `consistency` measures how often all runs agree on the same answer for each test case. 100% means the model always gives the same answer.
- This matters because a prompt with 90% accuracy but 50% consistency is worse than a prompt with 85% accuracy and 95% consistency. The first one is unpredictable.

---

## The Prompt Iteration Workflow

Improving prompts is a systematic process.

```
+------------------------------------------------------------------+
|              PROMPT ITERATION WORKFLOW                            |
|                                                                   |
|  +----------+     +-----------+     +----------+                 |
|  | 1. Write |---->| 2. Test   |---->| 3. Measure|                |
|  |  Initial |     |  Against  |     |  Metrics  |                |
|  |  Prompt  |     |  Examples  |     |           |                |
|  +----------+     +-----------+     +----------+                 |
|       ^                                   |                       |
|       |                                   v                       |
|  +----------+     +-----------+     +----------+                 |
|  | 6. Repeat|<----| 5. Create |<----| 4. Analyze|                |
|  |  Until   |     |  Improved |     |  Failures |                |
|  |  Good    |     |  Version  |     |           |                |
|  +----------+     +-----------+     +----------+                 |
|                                                                   |
|  Each cycle should improve at least one metric                    |
+------------------------------------------------------------------+
```

```python
class PromptIterator:
    """Track prompt versions and their performance over time."""

    def __init__(self):
        self.versions = []

    def add_version(self, name, prompt, accuracy, consistency,
                    avg_tokens, notes=""):
        """Record a prompt version and its metrics."""
        self.versions.append({
            "name": name,
            "prompt": prompt,
            "accuracy": accuracy,
            "consistency": consistency,
            "avg_tokens": avg_tokens,
            "notes": notes
        })

    def show_history(self):
        """Display the evolution of prompt versions."""
        print(f"\n{'Version':<12} {'Accuracy':<10} {'Consistency':<13} "
              f"{'Tokens':<8} {'Notes'}")
        print("-" * 70)

        for v in self.versions:
            print(f"{v['name']:<12} {v['accuracy']:<10.1%} "
                  f"{v['consistency']:<13.1%} {v['avg_tokens']:<8.0f} "
                  f"{v['notes']}")

    def best_version(self):
        """Return the version with the highest accuracy."""
        return max(self.versions, key=lambda v: v["accuracy"])


# Track prompt evolution
tracker = PromptIterator()

tracker.add_version(
    name="v1.0",
    prompt="Classify the sentiment: {input}",
    accuracy=0.625,
    consistency=0.75,
    avg_tokens=30,
    notes="Too vague, no categories listed"
)

tracker.add_version(
    name="v1.1",
    prompt="Classify as positive/negative/neutral/mixed: {input}",
    accuracy=0.75,
    consistency=0.875,
    avg_tokens=32,
    notes="Added categories, still brief"
)

tracker.add_version(
    name="v2.0",
    prompt="You are a sentiment expert. Classify... [detailed]: {input}",
    accuracy=0.875,
    consistency=1.0,
    avg_tokens=45,
    notes="Added definitions, much better"
)

tracker.add_version(
    name="v2.1",
    prompt="Expert classifier with examples... [few-shot]: {input}",
    accuracy=0.95,
    consistency=1.0,
    avg_tokens=85,
    notes="Added few-shot examples"
)

tracker.show_history()

best = tracker.best_version()
print(f"\nBest version: {best['name']} with {best['accuracy']:.1%} accuracy")
```

**Output:**
```
Version      Accuracy   Consistency   Tokens   Notes
----------------------------------------------------------------------
v1.0         62.5%      75.0%         30       Too vague, no categories listed
v1.1         75.0%      87.5%         32       Added categories, still brief
v2.0         87.5%      100.0%        45       Added definitions, much better
v2.1         95.0%      100.0%        85       Added few-shot examples

Best version: v2.1 with 95.0% accuracy
```

**Line-by-line explanation:**

- `PromptIterator` keeps a history of all prompt versions and their metrics. This lets you track progress over time.
- Each version records accuracy, consistency, token usage, and notes about what changed.
- `show_history()` prints a table so you can see the evolution at a glance. Notice how each version improves on the previous one.
- `best_version()` returns the version with the highest accuracy.
- The pattern shows a typical progression: start simple, add structure, add definitions, add examples. Each step usually improves accuracy but costs more tokens.

---

## Automated Evaluation with LLM-as-Judge

For tasks where there is no single "correct" answer (like summarization), you can use another LLM to judge the quality.

```python
from openai import OpenAI

client = OpenAI()

def llm_judge(
    prompt: str,
    response: str,
    criteria: list,
    model: str = "gpt-4o-mini"
) -> dict:
    """
    Use an LLM to judge the quality of a response.

    Args:
        prompt: The original prompt that was given
        response: The response to evaluate
        criteria: List of criteria to judge on

    Returns:
        Dictionary with scores for each criterion
    """
    criteria_text = "\n".join(
        f"- {c}: Rate from 1 (poor) to 5 (excellent)"
        for c in criteria
    )

    judge_prompt = f"""You are evaluating the quality of an AI response.

Original prompt: {prompt}

Response to evaluate: {response}

Rate the response on these criteria (1-5 each):
{criteria_text}

Respond in JSON format like:
{{"criteria_name": score, ...}}
Also include "reasoning": "brief explanation"
"""

    judge_response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": judge_prompt}],
        response_format={"type": "json_object"},
        temperature=0
    )

    import json
    return json.loads(judge_response.choices[0].message.content)


# Example: Judge a summary
original_prompt = "Summarize the impact of AI on healthcare in 2 sentences."
ai_response = ("AI is transforming healthcare through improved diagnostics "
               "and personalized treatment plans. Machine learning models can "
               "now detect diseases from medical images with accuracy matching "
               "human specialists.")

scores = llm_judge(
    prompt=original_prompt,
    response=ai_response,
    criteria=["accuracy", "completeness", "conciseness", "clarity"]
)

print("Evaluation scores:")
for key, value in scores.items():
    if key != "reasoning":
        print(f"  {key}: {value}/5")

if "reasoning" in scores:
    print(f"\nReasoning: {scores['reasoning']}")
```

**Output:**
```
Evaluation scores:
  accuracy: 5/5
  completeness: 4/5
  conciseness: 5/5
  clarity: 5/5

Reasoning: The response accurately describes AI's impact on healthcare in exactly 2 clear sentences. It covers diagnostics and treatment but could mention other areas like drug discovery.
```

**Line-by-line explanation:**

- `llm_judge()` uses one LLM to evaluate the output of another LLM. This is called "LLM-as-Judge."
- The judge receives the original prompt, the response, and specific criteria to evaluate.
- Each criterion gets a score from 1 to 5 so you can compare responses numerically.
- `temperature=0` makes the judge consistent. You want the same response judged the same way every time.
- This approach is useful for open-ended tasks where there is no single correct answer, like summarization, creative writing, or explanation quality.

---

## Common Mistakes

1. **Testing with too few examples.** Three test cases are not enough. Use at least 20 to get meaningful statistics.

2. **Not setting temperature to 0 for evaluation.** Higher temperatures add randomness, making evaluation unreliable. Always use `temperature=0` when comparing prompts.

3. **Changing multiple things at once.** When you modify a prompt, change one thing at a time. Otherwise, you cannot tell which change helped or hurt.

4. **Ignoring cost in evaluation.** A prompt that is 2% more accurate but costs 5 times more tokens might not be worth it. Always consider the accuracy-cost tradeoff.

5. **Using biased test cases.** If 80% of your test cases are "positive" sentiment, a prompt that always says "positive" will score 80% accuracy. Balance your test set across all categories.

---

## Best Practices

1. **Version your prompts.** Keep a history of every prompt version and its metrics. You will want to go back to a previous version sometimes.

2. **Use representative test cases.** Your test cases should reflect real-world usage. Include edge cases and difficult examples.

3. **Measure multiple metrics.** Accuracy alone is not enough. Track consistency, token usage, latency, and format compliance.

4. **Automate evaluation.** Run evaluations automatically whenever you change a prompt. This prevents regressions.

5. **Use LLM-as-Judge for subjective tasks.** When there is no single correct answer, use a separate LLM to score quality on specific criteria.

6. **Document your iterations.** Write notes about what you changed and why. Future you will thank present you.

---

## Quick Summary

Prompt templates separate the structure of your prompts from the variable content, making prompts reusable and maintainable. Jinja2 adds conditionals and loops for complex templates. Evaluation frameworks measure prompt quality with metrics like accuracy, consistency, and token efficiency. A/B testing compares prompts head-to-head, and the iteration workflow ensures systematic improvement. Together, these tools transform prompt engineering from guesswork into a data-driven process.

---

## Key Points

- **f-strings** work for simple templates with straightforward variable substitution
- **Jinja2** adds conditionals, loops, and filters for complex templates
- **Prompt template libraries** organize reusable templates with metadata and versioning
- **Evaluation metrics** include accuracy, consistency, token efficiency, and format compliance
- **A/B testing** compares two prompts against the same test cases
- **Multiple evaluation runs** reveal consistency problems
- **LLM-as-Judge** evaluates open-ended responses using another LLM
- **Iteration workflow** systematically improves prompts through measure-analyze-improve cycles

---

## Practice Questions

1. What is the advantage of using Jinja2 templates over simple f-strings for prompt engineering?

2. You have a prompt with 90% accuracy and 60% consistency. Another prompt has 85% accuracy and 95% consistency. Which would you choose for a production application and why?

3. When evaluating a prompt, why is it important to run multiple evaluation rounds instead of just one?

4. What is the "LLM-as-Judge" approach, and when would you use it instead of exact-match evaluation?

5. You changed three things in a prompt at once: added a system role, included examples, and changed the output format. The accuracy improved by 10%. What is the problem with this approach?

---

## Exercises

**Exercise 1: Template Library**

Create a Jinja2 prompt template library with at least 4 templates: one for summarization, one for classification, one for translation, and one for question answering. Each template should have configurable parameters. Test each template by rendering it with at least 2 different sets of variables.

**Exercise 2: Prompt A/B Test**

Pick a text classification task (spam detection, topic classification, or intent detection). Write 3 different prompt versions, from simple to detailed. Create at least 15 test cases. Run an A/B test comparing all three versions and report which one wins.

**Exercise 3: Evaluation Dashboard**

Build a function that takes a prompt template, a set of test cases, and produces a formatted evaluation report including: accuracy, consistency (across 3 runs), average tokens, cost estimate (at $0.15 per million input tokens), and a list of failed test cases with the model's actual output.

---

## What Is Next?

You now know how to create reliable, measurable prompts. But what happens when the LLM does not know the answer? It makes something up. In Chapter 13, you will learn about Retrieval-Augmented Generation (RAG), a technique that solves this by giving the LLM access to your own documents and data before it generates a response. RAG is one of the most important techniques in modern AI applications.
