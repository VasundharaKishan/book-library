# Chapter 7: Writing Effective Prompts

## What You Will Learn

In this chapter, you will learn:

- Why prompt quality dramatically affects output quality
- How clarity, specificity, and context improve LLM responses
- How to use constraints and output format instructions
- How role assignment changes the model's behavior
- The iterative process of improving prompts
- Concrete examples of bad prompts transformed into good ones

## Why This Chapter Matters

The prompt is your only way to communicate with an LLM. A great model with a bad prompt gives bad results. A decent model with a great prompt gives surprisingly good results. Prompt engineering is not a gimmick; it is the most important practical skill for working with LLMs.

**Analogy:** Think of prompting like giving directions to a taxi driver. "Take me somewhere nice" will get you to a random destination. "Take me to the Italian restaurant on 5th Street, the one with outdoor seating" gets you exactly where you want to go. The taxi driver's skill (the model) matters, but your directions (the prompt) matter just as much.

---

## The Five Principles of Effective Prompts

```
+----------------------------------------------------------+
|         The Five Principles                               |
+----------------------------------------------------------+
|                                                            |
|  1. CLARITY     - Say exactly what you mean               |
|  2. SPECIFICITY - Include precise details                 |
|  3. CONTEXT     - Provide relevant background             |
|  4. CONSTRAINTS - Set boundaries and limits               |
|  5. FORMAT      - Describe the desired output structure   |
|                                                            |
+----------------------------------------------------------+
```

---

## Principle 1: Clarity

**Clarity** means making your prompt unambiguous. Every word should have one obvious interpretation.

```python
# Demonstrating the impact of clarity

examples = [
    {
        "label": "Ambiguous prompt",
        "prompt": "Tell me about Python.",
        "problems": [
            "Python the programming language or python the snake?",
            "Tell you what exactly? History? Syntax? Use cases?",
            "How much detail? A sentence or an essay?",
        ],
        "improved": "Explain what the Python programming language is "
                   "used for, in 3 bullet points.",
        "why_better": "Specifies the topic, format, and scope"
    },
    {
        "label": "Vague request",
        "prompt": "Fix this code.",
        "problems": [
            "What code? No code was provided.",
            "What is wrong with it? Syntax error? Logic error?",
            "What should the fixed version do?",
        ],
        "improved": "This Python function should return the sum of "
                   "all even numbers in a list, but it returns 0 for "
                   "every input. Find and fix the bug:\n"
                   "def sum_evens(nums): ...",
        "why_better": "Describes expected behavior, actual behavior, and provides the code"
    },
    {
        "label": "Multiple interpretations",
        "prompt": "Make it better.",
        "problems": [
            "Make what better?",
            "Better in what way? Faster? More readable? More accurate?",
            "What is the current quality level?",
        ],
        "improved": "Rewrite this paragraph to be more concise. Reduce "
                   "it from 150 words to under 75 words while keeping "
                   "all key points.",
        "why_better": "Defines what 'better' means with measurable criteria"
    },
]

print("Principle 1: CLARITY")
print("=" * 60)

for ex in examples:
    print(f"\n  {ex['label']}:")
    print(f"  Bad:  '{ex['prompt']}'")
    print(f"  Problems:")
    for p in ex['problems']:
        print(f"    ? {p}")
    print(f"  Good: '{ex['improved'][:70]}...'")
    print(f"  Why:  {ex['why_better']}")
```

**Output:**
```
Principle 1: CLARITY
============================================================

  Ambiguous prompt:
  Bad:  'Tell me about Python.'
  Problems:
    ? Python the programming language or python the snake?
    ? Tell you what exactly? History? Syntax? Use cases?
    ? How much detail? A sentence or an essay?
  Good: 'Explain what the Python programming language is used for, in 3 bulle...'
  Why:  Specifies the topic, format, and scope

  Vague request:
  Bad:  'Fix this code.'
  Problems:
    ? What code? No code was provided.
    ? What is wrong with it? Syntax error? Logic error?
    ? What should the fixed version do?
  Good: 'This Python function should return the sum of all even numbers in a ...'
  Why:  Describes expected behavior, actual behavior, and provides the code

  Multiple interpretations:
  Bad:  'Make it better.'
  Problems:
    ? Make what better?
    ? Better in what way? Faster? More readable? More accurate?
    ? What is the current quality level?
  Good: 'Rewrite this paragraph to be more concise. Reduce it from 150 words ...'
  Why:  Defines what 'better' means with measurable criteria
```

---

## Principle 2: Specificity

**Specificity** means including precise details about what you want. The more specific you are, the less the model has to guess.

```python
# Demonstrating specificity

def specificity_comparison():
    """Show how adding specific details improves prompts."""

    comparisons = [
        {
            "task": "Writing a product description",
            "vague": "Write a product description for shoes.",
            "specific": (
                "Write a product description for the Nike Air Max 90 "
                "running shoes. Target audience: casual runners aged "
                "25-40. Tone: energetic but not pushy. Length: 100-150 "
                "words. Include: comfort features, available colors, "
                "and a call to action."
            ),
            "added_details": [
                "Product name", "Target audience", "Tone",
                "Length", "Required content", "Call to action"
            ]
        },
        {
            "task": "Code generation",
            "vague": "Write a function to sort data.",
            "specific": (
                "Write a Python function called sort_employees that "
                "takes a list of dictionaries (each with 'name', "
                "'department', and 'salary' keys) and returns the list "
                "sorted by salary in descending order. Include type "
                "hints and a docstring."
            ),
            "added_details": [
                "Language", "Function name", "Input type",
                "Data structure", "Sort field", "Sort order",
                "Code style requirements"
            ]
        },
        {
            "task": "Summarization",
            "vague": "Summarize this article.",
            "specific": (
                "Summarize this article in exactly 3 bullet points. "
                "Each bullet should be one sentence. Focus on the "
                "main findings, not the methodology. Write for a "
                "non-technical audience."
            ),
            "added_details": [
                "Format (bullet points)", "Count (3)",
                "Length per point (1 sentence)", "Focus area",
                "Audience level"
            ]
        },
    ]

    print("Principle 2: SPECIFICITY")
    print("=" * 60)

    for comp in comparisons:
        print(f"\n  Task: {comp['task']}")
        print(f"  Vague:    '{comp['vague']}'")
        print(f"  Specific: '{comp['specific'][:65]}...'")
        print(f"  Details added:")
        for detail in comp['added_details']:
            print(f"    + {detail}")

specificity_comparison()
```

**Output:**
```
Principle 2: SPECIFICITY
============================================================

  Task: Writing a product description
  Vague:    'Write a product description for shoes.'
  Specific: 'Write a product description for the Nike Air Max 90 running sho...'
  Details added:
    + Product name
    + Target audience
    + Tone
    + Length
    + Required content
    + Call to action

  Task: Code generation
  Vague:    'Write a function to sort data.'
  Specific: 'Write a Python function called sort_employees that takes a list ...'
  Details added:
    + Language
    + Function name
    + Input type
    + Data structure
    + Sort field
    + Sort order
    + Code style requirements

  Task: Summarization
  Vague:    'Summarize this article.'
  Specific: 'Summarize this article in exactly 3 bullet points. Each bullet ...'
  Details added:
    + Format (bullet points)
    + Count (3)
    + Length per point (1 sentence)
    + Focus area
    + Audience level
```

---

## Principle 3: Context

**Context** gives the model background information that shapes its response. Without context, the model guesses. With context, it can be precise.

```python
# Demonstrating the power of context

def context_examples():
    """Show how context transforms responses."""

    examples = [
        {
            "without_context": "How should I handle this error?",
            "with_context": (
                "I am building a REST API in Python using FastAPI. "
                "When I send a POST request with JSON data, I get a "
                "422 Unprocessable Entity error. Here is my endpoint:\n"
                "\n"
                "@app.post('/users')\n"
                "def create_user(name: str, age: int):\n"
                "    return {'name': name, 'age': age}\n"
                "\n"
                "I am sending: {'name': 'Alice', 'age': 30}\n"
                "How should I handle this error?"
            ),
            "context_adds": "Framework, error type, code, request data"
        },
        {
            "without_context": "What is the best database?",
            "with_context": (
                "I am building a real-time chat application that needs "
                "to handle 10,000 concurrent users. Messages need to be "
                "stored and retrieved quickly. I am using Node.js on the "
                "backend. My team has experience with SQL but not NoSQL. "
                "What is the best database for this use case?"
            ),
            "context_adds": "Use case, scale, tech stack, team skills"
        },
    ]

    print("Principle 3: CONTEXT")
    print("=" * 60)

    for ex in examples:
        print(f"\n  Without context:")
        print(f"    '{ex['without_context']}'")
        print(f"    Problem: Model must guess everything")
        print(f"\n  With context:")
        lines = ex['with_context'].split('\n')
        for line in lines[:3]:
            print(f"    '{line}'")
        print(f"    ... (full context provided)")
        print(f"    Added: {ex['context_adds']}")

context_examples()
```

**Output:**
```
Principle 3: CONTEXT
============================================================

  Without context:
    'How should I handle this error?'
    Problem: Model must guess everything

  With context:
    'I am building a REST API in Python using FastAPI. '
    'When I send a POST request with JSON data, I get a '
    '422 Unprocessable Entity error. Here is my endpoint:'
    ... (full context provided)
    Added: Framework, error type, code, request data

  Without context:
    'What is the best database?'
    Problem: Model must guess everything

  With context:
    'I am building a real-time chat application that needs '
    'to handle 10,000 concurrent users. Messages need to be '
    'stored and retrieved quickly. I am using Node.js on the '
    ... (full context provided)
    Added: Use case, scale, tech stack, team skills
```

---

## Principle 4: Constraints

**Constraints** set boundaries on the response. They tell the model what it should NOT do, how long the response should be, and what format to follow.

```python
# Demonstrating constraints

def constraint_examples():
    """Show how constraints shape output."""

    constraints = [
        {
            "type": "Length constraint",
            "without": "Explain machine learning.",
            "with": "Explain machine learning in exactly 3 sentences.",
            "effect": "Controls verbosity; prevents 5-paragraph essays"
        },
        {
            "type": "Format constraint",
            "without": "List the benefits of exercise.",
            "with": "List the benefits of exercise as a numbered list. "
                    "Each item should be one sentence starting with a verb.",
            "effect": "Ensures structured, consistent output"
        },
        {
            "type": "Scope constraint",
            "without": "Tell me about world history.",
            "with": "Explain the causes of World War I. "
                    "Focus only on political alliances, not economic factors.",
            "effect": "Narrows topic to prevent overwhelming responses"
        },
        {
            "type": "Style constraint",
            "without": "Explain how a computer works.",
            "with": "Explain how a computer works to a 10-year-old. "
                    "Use simple words, no jargon, and include a fun analogy.",
            "effect": "Controls complexity and tone"
        },
        {
            "type": "Exclusion constraint",
            "without": "Recommend programming languages to learn.",
            "with": "Recommend 3 programming languages for data science. "
                    "Do NOT include Python (I already know it). "
                    "For each, give one reason to learn it.",
            "effect": "Prevents unwanted or redundant content"
        },
    ]

    print("Principle 4: CONSTRAINTS")
    print("=" * 60)

    for c in constraints:
        print(f"\n  {c['type']}:")
        print(f"    Without: '{c['without']}'")
        print(f"    With:    '{c['with'][:65]}...'")
        print(f"    Effect:  {c['effect']}")

constraint_examples()
```

**Output:**
```
Principle 4: CONSTRAINTS
============================================================

  Length constraint:
    Without: 'Explain machine learning.'
    With:    'Explain machine learning in exactly 3 sentences.'
    Effect:  Controls verbosity; prevents 5-paragraph essays

  Format constraint:
    Without: 'List the benefits of exercise.'
    With:    'List the benefits of exercise as a numbered list. Each item sho...'
    Effect:  Ensures structured, consistent output

  Scope constraint:
    Without: 'Tell me about world history.'
    With:    'Explain the causes of World War I. Focus only on political alli...'
    Effect:  Narrows topic to prevent overwhelming responses

  Style constraint:
    Without: 'Explain how a computer works.'
    With:    'Explain how a computer works to a 10-year-old. Use simple words...'
    Effect:  Controls complexity and tone

  Exclusion constraint:
    Without: 'Recommend programming languages to learn.'
    With:    'Recommend 3 programming languages for data science. Do NOT incl...'
    Effect:  Prevents unwanted or redundant content
```

---

## Principle 5: Output Format

**Output format** instructions tell the model exactly how to structure its response.

```python
# Demonstrating output format instructions

def format_examples():
    """Show how format instructions produce structured output."""

    formats = [
        {
            "name": "JSON output",
            "prompt": (
                "Extract the following information from this text and "
                "return it as JSON:\n"
                "- person_name\n"
                "- age\n"
                "- city\n\n"
                'Text: "Alice is a 30-year-old engineer living in Boston."'
            ),
            "expected_output": '{"person_name": "Alice", "age": 30, "city": "Boston"}'
        },
        {
            "name": "Markdown table",
            "prompt": (
                "Compare Python and JavaScript. Create a markdown table "
                "with columns: Feature, Python, JavaScript. "
                "Include rows for: Typing, Speed, Main Use, Learning Curve."
            ),
            "expected_output": (
                "| Feature | Python | JavaScript |\n"
                "|---------|--------|------------|\n"
                "| Typing  | Dynamic| Dynamic    |"
            )
        },
        {
            "name": "Step-by-step with numbering",
            "prompt": (
                "Explain how to make a peanut butter sandwich. "
                "Use numbered steps. Each step should be one sentence. "
                "Maximum 6 steps."
            ),
            "expected_output": (
                "1. Get two slices of bread.\n"
                "2. Open the peanut butter jar.\n"
                "3. Spread peanut butter on one slice.\n"
                "..."
            )
        },
    ]

    print("Principle 5: OUTPUT FORMAT")
    print("=" * 60)

    for fmt in formats:
        print(f"\n  {fmt['name']}:")
        print(f"  Prompt:")
        for line in fmt['prompt'].split('\n')[:3]:
            print(f"    {line}")
        print(f"    ...")
        print(f"  Expected output format:")
        for line in fmt['expected_output'].split('\n')[:3]:
            print(f"    {line}")

format_examples()
```

**Output:**
```
Principle 5: OUTPUT FORMAT
============================================================

  JSON output:
  Prompt:
    Extract the following information from this text and
    return it as JSON:
    - person_name
    ...
  Expected output format:
    {"person_name": "Alice", "age": 30, "city": "Boston"}

  Markdown table:
  Prompt:
    Compare Python and JavaScript. Create a markdown table
    with columns: Feature, Python, JavaScript.
    Include rows for: Typing, Speed, Main Use, Learning Curve.
    ...
  Expected output format:
    | Feature | Python | JavaScript |
    |---------|--------|------------|
    | Typing  | Dynamic| Dynamic    |

  Step-by-step with numbering:
  Prompt:
    Explain how to make a peanut butter sandwich.
    Use numbered steps. Each step should be one sentence.
    Maximum 6 steps.
    ...
  Expected output format:
    1. Get two slices of bread.
    2. Open the peanut butter jar.
    3. Spread peanut butter on one slice.
```

---

## Role Assignment

**Role assignment** tells the model to behave as a specific type of expert. This can significantly improve the quality and style of responses.

```python
# Demonstrating role assignment

def role_assignment_demo():
    """Show how role assignment changes model behavior."""

    question = "How should I structure my database?"

    roles = [
        {
            "role": "No role (default)",
            "prompt": question,
            "expected_style": "Generic advice, surface-level"
        },
        {
            "role": "Senior database architect",
            "prompt": (
                "You are a senior database architect with 15 years "
                "of experience. I am building a social media platform "
                "that needs to handle 1 million users. " + question
            ),
            "expected_style": "Technical, detailed, covers scalability"
        },
        {
            "role": "Patient teacher",
            "prompt": (
                "You are a patient computer science teacher explaining "
                "concepts to a beginner who has never used a database. "
                "Use simple language and real-world analogies. " + question
            ),
            "expected_style": "Simple, analogy-rich, encouraging"
        },
        {
            "role": "Code reviewer",
            "prompt": (
                "You are a strict code reviewer at a Fortune 500 company. "
                "Review database design decisions critically. Point out "
                "potential issues and anti-patterns. " + question
            ),
            "expected_style": "Critical, thorough, warns about pitfalls"
        },
    ]

    print("Role Assignment: Same Question, Different Perspectives")
    print("=" * 60)

    for r in roles:
        print(f"\n  Role: {r['role']}")
        print(f"  Prompt: '{r['prompt'][:60]}...'")
        print(f"  Expected response style: {r['expected_style']}")

role_assignment_demo()
```

**Output:**
```
Role Assignment: Same Question, Different Perspectives
============================================================

  Role: No role (default)
  Prompt: 'How should I structure my database?...'
  Expected response style: Generic advice, surface-level

  Role: Senior database architect
  Prompt: 'You are a senior database architect with 15 years of experi...'
  Expected response style: Technical, detailed, covers scalability

  Role: Patient teacher
  Prompt: 'You are a patient computer science teacher explaining conce...'
  Expected response style: Simple, analogy-rich, encouraging

  Role: Code reviewer
  Prompt: 'You are a strict code reviewer at a Fortune 500 company. Re...'
  Expected response style: Critical, thorough, warns about pitfalls
```

---

## The Iterative Process

Good prompts are rarely written on the first try. Prompt engineering is an iterative process.

```python
# Demonstrating iterative prompt improvement

def iterative_improvement():
    """Show how to iteratively improve a prompt."""

    iterations = [
        {
            "version": "v1 (first attempt)",
            "prompt": "Write a function to process data.",
            "problem": "Too vague. What language? What data? What processing?",
            "quality": 2,
        },
        {
            "version": "v2 (add specifics)",
            "prompt": ("Write a Python function that takes a list of "
                      "dictionaries containing student grades and "
                      "returns the average grade."),
            "problem": "Better, but no details about error handling or format.",
            "quality": 5,
        },
        {
            "version": "v3 (add constraints)",
            "prompt": ("Write a Python function called calculate_average "
                      "that takes a list of dicts with 'name' (str) and "
                      "'grade' (float) keys. Return the average grade "
                      "rounded to 2 decimal places. Handle empty lists "
                      "by returning 0.0. Include type hints."),
            "problem": "Good, but could use an example for clarity.",
            "quality": 8,
        },
        {
            "version": "v4 (add example)",
            "prompt": ("Write a Python function called calculate_average "
                      "that takes a list of dicts with 'name' (str) and "
                      "'grade' (float) keys. Return the average grade "
                      "rounded to 2 decimal places. Handle empty lists "
                      "by returning 0.0. Include type hints and docstring.\n\n"
                      "Example:\n"
                      "  Input:  [{'name': 'Alice', 'grade': 85.5}, "
                      "{'name': 'Bob', 'grade': 92.0}]\n"
                      "  Output: 88.75"),
            "problem": "Excellent prompt. Clear, specific, constrained, with example.",
            "quality": 10,
        },
    ]

    print("Iterative Prompt Improvement")
    print("=" * 60)

    for it in iterations:
        quality_bar = "█" * it['quality'] + "░" * (10 - it['quality'])
        print(f"\n  {it['version']}:")
        print(f"    Prompt: '{it['prompt'][:65]}...'")
        print(f"    Issue:  {it['problem']}")
        print(f"    Quality: [{quality_bar}] {it['quality']}/10")

    print(f"\n{'=' * 60}")
    print("Key takeaway: Each iteration adds specificity and context.")
    print("Version 4 is 5x better than version 1!")

iterative_improvement()
```

**Output:**
```
Iterative Prompt Improvement
============================================================

  v1 (first attempt):
    Prompt: 'Write a function to process data....'
    Issue:  Too vague. What language? What data? What processing?
    Quality: [██░░░░░░░░] 2/10

  v2 (add specifics):
    Prompt: 'Write a Python function that takes a list of dictionaries cont...'
    Issue:  Better, but no details about error handling or format.
    Quality: [█████░░░░░] 5/10

  v3 (add constraints):
    Prompt: 'Write a Python function called calculate_average that takes a ...'
    Issue:  Good, but could use an example for clarity.
    Quality: [████████░░] 8/10

  v4 (add example):
    Prompt: 'Write a Python function called calculate_average that takes a ...'
    Issue:  Excellent prompt. Clear, specific, constrained, with example.
    Quality: [██████████] 10/10

============================================================
Key takeaway: Each iteration adds specificity and context.
Version 4 is 5x better than version 1!
```

---

## Bad vs Good Prompts: Complete Examples

```python
# Comprehensive bad vs good prompt comparison

def bad_vs_good():
    """Side-by-side comparison of bad and good prompts."""

    examples = [
        {
            "task": "Email writing",
            "bad": "Write an email about the meeting.",
            "good": (
                "Write a professional email to my team (5 people) "
                "informing them that Friday's 2pm meeting has been "
                "moved to Monday at 10am. Mention that the agenda "
                "remains the same. Keep it under 100 words. "
                "Sign off as 'Sarah'."
            ),
            "improvements": [
                "Specifies audience and size",
                "Includes concrete details (day, time)",
                "Mentions specific content to include",
                "Sets length constraint",
                "Specifies sender name",
            ]
        },
        {
            "task": "Data analysis",
            "bad": "Analyze this data.",
            "good": (
                "Analyze this CSV sales data and provide:\n"
                "1. Total revenue per quarter\n"
                "2. Top 3 products by units sold\n"
                "3. Month-over-month growth rate\n"
                "Present results in a markdown table. "
                "Note any anomalies or significant trends."
            ),
            "improvements": [
                "Specifies data format (CSV)",
                "Lists exact analyses needed",
                "Requests specific metrics",
                "Defines output format",
                "Asks for insights, not just numbers",
            ]
        },
        {
            "task": "Code review",
            "bad": "Review my code.",
            "good": (
                "Review this Python function for:\n"
                "1. Correctness: Does it handle edge cases?\n"
                "2. Performance: Any inefficiencies?\n"
                "3. Readability: Is it clear and well-structured?\n"
                "4. Security: Any vulnerabilities?\n\n"
                "For each issue found, suggest a specific fix. "
                "Rate the overall quality from 1-10."
            ),
            "improvements": [
                "Lists specific review criteria",
                "Asks for actionable fixes",
                "Requests a quality rating",
                "Covers multiple dimensions",
                "Structured review process",
            ]
        },
    ]

    print("Bad vs Good Prompts: Complete Examples")
    print("=" * 60)

    for ex in examples:
        print(f"\n{'─' * 55}")
        print(f"  Task: {ex['task']}")
        print(f"{'─' * 55}")
        print(f"\n  BAD PROMPT:")
        print(f"    '{ex['bad']}'")
        print(f"\n  GOOD PROMPT:")
        lines = ex['good'].split('\n')
        for line in lines:
            print(f"    {line}")
        print(f"\n  What makes it better:")
        for imp in ex['improvements']:
            print(f"    + {imp}")

bad_vs_good()
```

**Output:**
```
Bad vs Good Prompts: Complete Examples
============================================================

───────────────────────────────────────────────────────
  Task: Email writing
───────────────────────────────────────────────────────

  BAD PROMPT:
    'Write an email about the meeting.'

  GOOD PROMPT:
    Write a professional email to my team (5 people)
    informing them that Friday's 2pm meeting has been
    moved to Monday at 10am. Mention that the agenda
    remains the same. Keep it under 100 words.
    Sign off as 'Sarah'.

  What makes it better:
    + Specifies audience and size
    + Includes concrete details (day, time)
    + Mentions specific content to include
    + Sets length constraint
    + Specifies sender name

───────────────────────────────────────────────────────
  Task: Data analysis
───────────────────────────────────────────────────────

  BAD PROMPT:
    'Analyze this data.'

  GOOD PROMPT:
    Analyze this CSV sales data and provide:
    1. Total revenue per quarter
    2. Top 3 products by units sold
    3. Month-over-month growth rate
    Present results in a markdown table.
    Note any anomalies or significant trends.

  What makes it better:
    + Specifies data format (CSV)
    + Lists exact analyses needed
    + Requests specific metrics
    + Defines output format
    + Asks for insights, not just numbers

───────────────────────────────────────────────────────
  Task: Code review
───────────────────────────────────────────────────────

  BAD PROMPT:
    'Review my code.'

  GOOD PROMPT:
    Review this Python function for:
    1. Correctness: Does it handle edge cases?
    2. Performance: Any inefficiencies?
    3. Readability: Is it clear and well-structured?
    4. Security: Any vulnerabilities?

    For each issue found, suggest a specific fix.
    Rate the overall quality from 1-10.

  What makes it better:
    + Lists specific review criteria
    + Asks for actionable fixes
    + Requests a quality rating
    + Covers multiple dimensions
    + Structured review process
```

---

## Prompt Templates

```python
# Reusable prompt templates

templates = {
    "explanation": {
        "template": (
            "Explain {topic} to someone who is {audience_level}. "
            "Use {style}. Keep it to {length}. "
            "{additional_instructions}"
        ),
        "example": (
            "Explain neural networks to someone who is a complete beginner. "
            "Use real-world analogies. Keep it to 3 paragraphs. "
            "Do not use any math notation."
        ),
    },
    "code_generation": {
        "template": (
            "Write a {language} function called {name} that {description}. "
            "Input: {input_spec}. Output: {output_spec}. "
            "Include: {requirements}. "
            "Handle edge cases: {edge_cases}."
        ),
        "example": (
            "Write a Python function called find_duplicates that finds all "
            "duplicate values in a list. Input: list of any hashable type. "
            "Output: list of duplicates (each appearing once). "
            "Include: type hints and docstring. "
            "Handle edge cases: empty list returns empty list."
        ),
    },
    "analysis": {
        "template": (
            "Analyze the following {content_type} and provide:\n"
            "1. {analysis_point_1}\n"
            "2. {analysis_point_2}\n"
            "3. {analysis_point_3}\n"
            "Format: {output_format}. "
            "Focus on: {focus_area}."
        ),
        "example": (
            "Analyze the following error log and provide:\n"
            "1. Root cause of the error\n"
            "2. Impact on the system\n"
            "3. Recommended fix\n"
            "Format: bullet points under each heading. "
            "Focus on: actionable solutions."
        ),
    },
}

print("Reusable Prompt Templates")
print("=" * 60)

for name, template in templates.items():
    print(f"\n  Template: {name}")
    print(f"  Pattern:")
    for line in template['template'].split('. '):
        print(f"    {line.strip()}.")
    print(f"  Example:")
    print(f"    '{template['example'][:70]}...'")
```

**Output:**
```
Reusable Prompt Templates
============================================================

  Template: explanation
  Pattern:
    Explain {topic} to someone who is {audience_level}.
    Use {style}.
    Keep it to {length}.
    {additional_instructions}.
  Example:
    'Explain neural networks to someone who is a complete beginner. Use r...'

  Template: code_generation
  Pattern:
    Write a {language} function called {name} that {description}.
    Input: {input_spec}.
    Output: {output_spec}.
    Include: {requirements}.
    Handle edge cases: {edge_cases}..
  Example:
    'Write a Python function called find_duplicates that finds all duplic...'

  Template: analysis
  Pattern:
    Analyze the following {content_type} and provide:
    1.
    {analysis_point_1}
    2.
    {analysis_point_2}
    3.
    {analysis_point_3}
    Format: {output_format}.
    Focus on: {focus_area}..
  Example:
    'Analyze the following error log and provide:
1. Root cause of the err...'
```

---

## Common Mistakes

| Mistake | Why It Is Wrong | What to Do Instead |
|---------|----------------|-------------------|
| Being too vague | Model has to guess what you want | Be specific about topic, format, length, and audience |
| Writing prompts that are too long | Wastes tokens and can confuse the model | Be concise but complete; every word should add value |
| Not specifying output format | Model picks its own format, which may not be what you need | Always state the desired format (JSON, list, table, etc.) |
| Not iterating on prompts | First drafts are rarely optimal | Treat prompts as code: test, evaluate, refine, repeat |
| Assuming the model knows your context | Models have no memory of your project or situation | Always include relevant context, even if it seems obvious |

---

## Best Practices

1. **Start with the end in mind.** Before writing a prompt, decide exactly what the output should look like. Then write the prompt to produce that output.

2. **Use the five principles as a checklist.** For every prompt, ask: Is it clear? Specific? Does it have context? Constraints? Format instructions?

3. **Build a prompt library.** Save your best prompts as templates. Reuse and refine them over time.

4. **Test with edge cases.** Try your prompt with unusual inputs to see if it still works. Robust prompts handle edge cases gracefully.

5. **Keep iterating.** The best prompt engineers spend more time refining prompts than writing them the first time.

---

## Quick Summary

Effective prompts follow five principles: clarity (no ambiguity), specificity (precise details), context (relevant background), constraints (boundaries and limits), and format (output structure). Role assignment can significantly change response quality and style. Prompt engineering is an iterative process where each version improves on the last. Templates and patterns help you write better prompts faster. The difference between a bad prompt and a good prompt can be the difference between useless and excellent output.

---

## Key Points

- Clarity eliminates ambiguity; every word should have one obvious interpretation
- Specificity reduces guessing; include precise details about what you want
- Context provides the background the model needs to give relevant answers
- Constraints set boundaries on length, format, scope, and style
- Output format instructions ensure the response is structured as you need it
- Role assignment changes the model's expertise and communication style
- Prompt engineering is iterative: test, evaluate, refine, repeat
- Templates save time and ensure consistency across similar tasks

---

## Practice Questions

1. Take the vague prompt "Help me with my project" and rewrite it using all five principles. What questions would you need to answer first?

2. Why does role assignment change the quality of LLM responses? What is happening internally when you tell the model "You are a senior software engineer"?

3. You wrote a prompt that works 80% of the time but fails for edge cases. What strategies would you use to make it more robust?

4. Compare these two prompts and explain which is better and why:
   - "Write code to sort a list"
   - "Write a Python function that sorts a list of integers in ascending order using the built-in sorted() function. Return the sorted list."

5. When would you NOT want to use a detailed, specific prompt? Are there cases where a simpler prompt is better?

---

## Exercises

### Exercise 1: Prompt Makeover

Take these five bad prompts and rewrite each one as a good prompt using the five principles:
1. "Explain AI."
2. "Write some code."
3. "Summarize the news."
4. "Help me cook something."
5. "Debug this."

### Exercise 2: Template Creation

Create three reusable prompt templates for tasks you do regularly. Each template should include:
- Placeholder variables (marked with curly braces)
- A filled-in example
- A note about when to use each template

### Exercise 3: Iterative Refinement

Choose one task (e.g., generating a cover letter, writing test cases, or creating a study plan). Write four versions of the prompt, each improving on the previous one. For each version, note what you changed and why. Test each version and compare the outputs.

---

## What Is Next?

Now that you know how to write effective single prompts, the next chapter introduces a powerful technique: few-shot prompting. In "Few-Shot Prompting", you will learn how to include examples in your prompt to teach the model exactly what output format and style you want. Few-shot prompting is one of the most practical ways to get consistent, high-quality results from LLMs.
