# Chapter 9: Chain-of-Thought Prompting

## What You Will Learn

In this chapter, you will learn:

- What chain-of-thought (CoT) prompting is and why it matters
- How the simple phrase "Let's think step by step" improves accuracy
- The difference between zero-shot CoT and few-shot CoT
- How the ReAct pattern combines reasoning with actions
- What self-consistency is and how running multiple reasoning paths improves answers
- An overview of tree of thoughts for exploring multiple solution branches
- Practical examples where step-by-step reasoning dramatically improves results

## Why This Chapter Matters

In the previous chapter, you learned how few-shot prompting teaches models patterns through examples. But what happens when a task requires genuine reasoning, not just pattern matching? Math problems, logic puzzles, and multi-step analysis need the model to think through a problem, not just jump to an answer.

Here is a surprising fact: when you simply ask an LLM "What is 23 times 17?", it often gets the answer wrong. But when you ask "What is 23 times 17? Let's work through this step by step," the accuracy jumps dramatically. The model did not get smarter. You just gave it room to reason.

**Analogy:** Imagine someone asks you "What is 247 plus 389?" If you try to answer instantly, you might get it wrong. But if you grab a piece of scratch paper and work through it digit by digit, you get it right every time. Chain-of-thought prompting is like giving the LLM that scratch paper.

This technique is one of the most impactful discoveries in prompt engineering, and it costs nothing extra to use.

---

## The Problem: LLMs Rush to Answers

LLMs generate text one token at a time, moving left to right. When you ask a question and expect an immediate answer, the model has to produce the correct answer as its very first output token. For simple questions, this works fine. For reasoning tasks, it often fails.

```
+----------------------------------------------------------+
|         Why LLMs Struggle with Direct Answers             |
+----------------------------------------------------------+
|                                                            |
|  Question: "Roger has 5 tennis balls. He buys 2 cans     |
|  of 3. How many does he have now?"                        |
|                                                            |
|  WITHOUT Chain-of-Thought:                                |
|    Model must output answer immediately: "11"             |
|    All reasoning happens in one step.                     |
|    Result: Often wrong (might say "8" or "9")             |
|                                                            |
|  WITH Chain-of-Thought:                                   |
|    Model works through it:                                |
|    "Roger starts with 5 balls.                            |
|     He buys 2 cans of 3 balls each.                      |
|     2 cans x 3 balls = 6 new balls.                      |
|     5 + 6 = 11 total balls."                              |
|    Result: Correct! Step-by-step reasoning works.         |
|                                                            |
+----------------------------------------------------------+
```

**Analogy:** It is like the difference between doing mental math and writing out the calculation. Both use the same brain, but writing it out gives you intermediate checkpoints to avoid mistakes.

```python
# Showing the difference between direct and CoT prompting

def direct_vs_cot():
    """Compare direct answers with chain-of-thought answers."""

    print("Direct Answer vs Chain-of-Thought")
    print("=" * 60)

    # Example 1: Math word problem
    question = (
        "A store has 42 apples. They sell 15 in the morning "
        "and receive a shipment of 28 in the afternoon. "
        "Then they sell 19 more before closing. "
        "How many apples does the store have at closing?"
    )

    print(f"\nQuestion: {question}")

    # Direct approach
    print(f"\n{'─' * 55}")
    print("  DIRECT PROMPT:")
    print(f"  '{question}'")
    print()
    print("  Typical LLM response: '36'")
    print("  (Model jumps to answer, often wrong)")

    # CoT approach
    print(f"\n{'─' * 55}")
    print("  CHAIN-OF-THOUGHT PROMPT:")
    print(f"  '{question}")
    print("   Let's solve this step by step.'")
    print()
    print("  Typical LLM response:")
    print("  'Let me work through this step by step:")
    print("   1. Start with 42 apples")
    print("   2. Sell 15 in the morning: 42 - 15 = 27")
    print("   3. Receive shipment of 28: 27 + 28 = 55")
    print("   4. Sell 19 before closing: 55 - 19 = 36")
    print("   The store has 36 apples at closing.'")
    print()
    print("  The model shows its work and arrives at the")
    print("  correct answer by building on each step.")

direct_vs_cot()
```

**Output:**
```
Direct Answer vs Chain-of-Thought
============================================================

Question: A store has 42 apples. They sell 15 in the morning and receive a shipment of 28 in the afternoon. Then they sell 19 more before closing. How many apples does the store have at closing?

───────────────────────────────────────────────────────
  DIRECT PROMPT:
  'A store has 42 apples. They sell 15 in the morning and receive a shipment of 28 in the afternoon. Then they sell 19 more before closing. How many apples does the store have at closing?'

  Typical LLM response: '36'
  (Model jumps to answer, often wrong)

───────────────────────────────────────────────────────
  CHAIN-OF-THOUGHT PROMPT:
  'A store has 42 apples. They sell 15 in the morning and receive a shipment of 28 in the afternoon. Then they sell 19 more before closing. How many apples does the store have at closing?
   Let's solve this step by step.'

  Typical LLM response:
  'Let me work through this step by step:
   1. Start with 42 apples
   2. Sell 15 in the morning: 42 - 15 = 27
   3. Receive shipment of 28: 27 + 28 = 55
   4. Sell 19 before closing: 55 - 19 = 36
   The store has 36 apples at closing.'

  The model shows its work and arrives at the
  correct answer by building on each step.
```

**Line-by-line explanation:**

- The `direct_vs_cot()` function shows the same math problem solved two ways. The direct approach asks for the answer immediately. The chain-of-thought approach adds "Let's solve this step by step" and the model shows its intermediate calculations.
- With CoT, each step becomes a checkpoint. If the model makes an error at step 2, the remaining steps still follow logically from that point, making errors easier to spot and less likely to compound.

---

## Zero-Shot Chain-of-Thought

Zero-shot CoT is the simplest form: just add a reasoning trigger phrase to your prompt. No examples needed.

```
+----------------------------------------------------------+
|         Zero-Shot CoT Trigger Phrases                     |
+----------------------------------------------------------+
|                                                            |
|  Most effective phrases:                                  |
|                                                            |
|    "Let's think step by step."                            |
|    "Let's work through this step by step."                |
|    "Think about this carefully, step by step."            |
|    "Let's break this down."                               |
|    "Let's solve this one step at a time."                 |
|                                                            |
|  Why they work:                                           |
|    These phrases tell the model to generate               |
|    intermediate reasoning BEFORE the final answer.        |
|    The model literally "thinks out loud" in text.         |
|                                                            |
|  Where to place them:                                     |
|    At the END of your prompt, right before the            |
|    model generates its response.                          |
|                                                            |
+----------------------------------------------------------+
```

**Analogy:** Zero-shot CoT is like telling a student "show your work" on a math test. You do not need to show them an example of showing their work. The instruction alone changes how they approach the problem.

```python
# Zero-shot chain-of-thought examples

def zero_shot_cot_examples():
    """Show how adding a simple phrase triggers reasoning."""

    print("Zero-Shot Chain-of-Thought Examples")
    print("=" * 60)

    examples = [
        {
            "category": "Math",
            "question": (
                "If a shirt costs $25 and is on sale for 20% off, "
                "and you also have a $5 coupon, how much do you pay?"
            ),
            "direct_answer": "$15",
            "cot_reasoning": [
                "Original price: $25",
                "20% discount: $25 x 0.20 = $5 off",
                "Price after discount: $25 - $5 = $20",
                "Apply $5 coupon: $20 - $5 = $15",
                "Final price: $15"
            ],
        },
        {
            "category": "Logic",
            "question": (
                "Tom is taller than Sam. Sam is taller than Jim. "
                "Jim is taller than Bob. Is Tom taller than Bob?"
            ),
            "direct_answer": "Yes",
            "cot_reasoning": [
                "Tom is taller than Sam (given)",
                "Sam is taller than Jim (given)",
                "So Tom is taller than Jim (transitive)",
                "Jim is taller than Bob (given)",
                "So Tom is taller than Bob (transitive)",
                "Answer: Yes"
            ],
        },
        {
            "category": "Word Problem",
            "question": (
                "A farmer has chickens and cows. He counts 20 heads "
                "and 56 legs total. How many chickens does he have?"
            ),
            "direct_answer": "Often wrong without reasoning",
            "cot_reasoning": [
                "Each animal has 1 head",
                "20 heads means 20 animals total",
                "Chickens have 2 legs, cows have 4 legs",
                "Let c = chickens, w = cows",
                "c + w = 20 (heads)",
                "2c + 4w = 56 (legs)",
                "From first equation: c = 20 - w",
                "Substitute: 2(20 - w) + 4w = 56",
                "40 - 2w + 4w = 56",
                "2w = 16, so w = 8 cows",
                "c = 20 - 8 = 12 chickens",
                "Answer: 12 chickens"
            ],
        },
    ]

    for ex in examples:
        print(f"\n{'─' * 55}")
        print(f"  Category: {ex['category']}")
        print(f"  Question: {ex['question']}")
        print(f"\n  Without CoT: {ex['direct_answer']}")
        print(f"\n  With CoT ('Let's think step by step'):")
        for step in ex['cot_reasoning']:
            print(f"    {step}")

zero_shot_cot_examples()
```

**Output:**
```
Zero-Shot Chain-of-Thought Examples
============================================================

───────────────────────────────────────────────────────
  Category: Math
  Question: If a shirt costs $25 and is on sale for 20% off, and you also have a $5 coupon, how much do you pay?

  Without CoT: $15

  With CoT ('Let's think step by step'):
    Original price: $25
    20% discount: $25 x 0.20 = $5 off
    Price after discount: $25 - $5 = $20
    Apply $5 coupon: $20 - $5 = $15
    Final price: $15

───────────────────────────────────────────────────────
  Category: Logic
  Question: Tom is taller than Sam. Sam is taller than Jim. Jim is taller than Bob. Is Tom taller than Bob?

  Without CoT: Yes

  With CoT ('Let's think step by step'):
    Tom is taller than Sam (given)
    Sam is taller than Jim (given)
    So Tom is taller than Jim (transitive)
    Jim is taller than Bob (given)
    So Tom is taller than Bob (transitive)
    Answer: Yes

───────────────────────────────────────────────────────
  Category: Word Problem
  Question: A farmer has chickens and cows. He counts 20 heads and 56 legs total. How many chickens does he have?

  Without CoT: Often wrong without reasoning

  With CoT ('Let's think step by step'):
    Each animal has 1 head
    20 heads means 20 animals total
    Chickens have 2 legs, cows have 4 legs
    Let c = chickens, w = cows
    c + w = 20 (heads)
    2c + 4w = 56 (legs)
    From first equation: c = 20 - w
    Substitute: 2(20 - w) + 4w = 56
    40 - 2w + 4w = 56
    2w = 16, so w = 8 cows
    c = 20 - 8 = 12 chickens
    Answer: 12 chickens
```

**Line-by-line explanation:**

- Each example shows a question, the direct answer (which might be wrong), and the step-by-step CoT reasoning.
- For the math problem, CoT prevents the model from confusing the order of operations (discount first, then coupon).
- For the logic problem, CoT forces the model to trace through the transitive relationships explicitly rather than guessing.
- The farmer problem requires algebra. Without CoT, models often guess. With CoT, they can set up and solve equations correctly.

---

## Few-Shot Chain-of-Thought

Few-shot CoT goes further: you show the model examples of step-by-step reasoning. This teaches the model both the format and the depth of reasoning you expect.

```
+----------------------------------------------------------+
|         Zero-Shot CoT vs Few-Shot CoT                     |
+----------------------------------------------------------+
|                                                            |
|  ZERO-SHOT CoT:                                          |
|    [Question]                                             |
|    "Let's think step by step."                            |
|                                                            |
|    Pros: Simple, no examples needed                       |
|    Cons: Reasoning depth is unpredictable                 |
|                                                            |
|  FEW-SHOT CoT:                                           |
|    [Example question 1]                                   |
|    [Step-by-step reasoning 1]                             |
|    [Answer 1]                                             |
|                                                            |
|    [Example question 2]                                   |
|    [Step-by-step reasoning 2]                             |
|    [Answer 2]                                             |
|                                                            |
|    [New question]                                         |
|                                                            |
|    Pros: Controls reasoning format and depth              |
|    Cons: Uses more tokens, requires crafting examples     |
|                                                            |
+----------------------------------------------------------+
```

```python
# Few-shot chain-of-thought prompting

def few_shot_cot_prompt():
    """Build a few-shot CoT prompt for math word problems."""

    print("Few-Shot Chain-of-Thought Prompt")
    print("=" * 60)

    prompt = """Solve each math problem step by step.

Question: There are 15 trees in a park. Park workers plant 6 trees today and 4 trees tomorrow. How many trees will be in the park?
Reasoning:
- Start with 15 trees
- Workers plant 6 today: 15 + 6 = 21
- Workers plant 4 tomorrow: 21 + 4 = 25
Answer: 25

Question: If there are 3 cars in a parking lot and 2 more arrive, then 1 leaves, how many cars are there?
Reasoning:
- Start with 3 cars
- 2 more arrive: 3 + 2 = 5
- 1 leaves: 5 - 1 = 4
Answer: 4

Question: A library has 120 books. They donate 35 to a school, buy 50 new books, then lose 12 to water damage. How many books does the library have?
Reasoning:"""

    print("\nPrompt sent to the model:")
    print("-" * 55)
    for line in prompt.split('\n'):
        print(f"  {line}")

    print("\n" + "-" * 55)
    print("\nExpected model completion:")
    completion = """- Start with 120 books
- Donate 35 to school: 120 - 35 = 85
- Buy 50 new books: 85 + 50 = 135
- Lose 12 to water damage: 135 - 12 = 123
Answer: 123"""
    for line in completion.split('\n'):
        print(f"  {line}")
    print()
    print("The model follows the exact reasoning format from the")
    print("examples: bullet points with intermediate calculations.")

few_shot_cot_prompt()
```

**Output:**
```
Few-Shot Chain-of-Thought Prompt
============================================================

Prompt sent to the model:
-------------------------------------------------------
  Solve each math problem step by step.

  Question: There are 15 trees in a park. Park workers plant 6 trees today and 4 trees tomorrow. How many trees will be in the park?
  Reasoning:
  - Start with 15 trees
  - Workers plant 6 today: 15 + 6 = 21
  - Workers plant 4 tomorrow: 21 + 4 = 25
  Answer: 25

  Question: If there are 3 cars in a parking lot and 2 more arrive, then 1 leaves, how many cars are there?
  Reasoning:
  - Start with 3 cars
  - 2 more arrive: 3 + 2 = 5
  - 1 leaves: 5 - 1 = 4
  Answer: 4

  Question: A library has 120 books. They donate 35 to a school, buy 50 new books, then lose 12 to water damage. How many books does the library have?
  Reasoning:

-------------------------------------------------------

Expected model completion:
  - Start with 120 books
  - Donate 35 to school: 120 - 35 = 85
  - Buy 50 new books: 85 + 50 = 135
  - Lose 12 to water damage: 135 - 12 = 123
  Answer: 123

The model follows the exact reasoning format from the
examples: bullet points with intermediate calculations.
```

**Line-by-line explanation:**

- The prompt includes two complete solved examples with "Reasoning:" and "Answer:" sections. This teaches the model both the depth and format of reasoning expected.
- The third question provides only the "Reasoning:" label, cueing the model to fill in the steps and answer.
- Few-shot CoT gives you more control over reasoning format than zero-shot CoT. The model mirrors the bullet-point style with intermediate calculations.

---

## When CoT Helps the Most

Chain-of-thought does not help equally on all tasks. Here is a guide to when it shines and when it is unnecessary.

```python
# When to use chain-of-thought prompting

def cot_decision_guide():
    """Show when CoT helps and when it does not."""

    print("When to Use Chain-of-Thought Prompting")
    print("=" * 60)

    helps = [
        {
            "task": "Multi-step math problems",
            "why": "Each step builds on the previous one",
            "improvement": "Large (30-50% accuracy gain)",
        },
        {
            "task": "Logic and reasoning puzzles",
            "why": "Forces explicit tracking of relationships",
            "improvement": "Large (20-40% accuracy gain)",
        },
        {
            "task": "Code debugging",
            "why": "Traces through execution step by step",
            "improvement": "Moderate to large",
        },
        {
            "task": "Complex decision making",
            "why": "Weighs multiple factors systematically",
            "improvement": "Moderate",
        },
        {
            "task": "Reading comprehension with inference",
            "why": "Connects multiple pieces of information",
            "improvement": "Moderate",
        },
    ]

    does_not_help = [
        {
            "task": "Simple factual questions",
            "why": "No reasoning needed, just recall",
            "example": "'What is the capital of France?'",
        },
        {
            "task": "Text classification",
            "why": "Pattern matching, not reasoning",
            "example": "'Is this email spam or not?'",
        },
        {
            "task": "Translation",
            "why": "Direct mapping, no multi-step logic",
            "example": "'Translate hello to Spanish'",
        },
        {
            "task": "Simple formatting",
            "why": "Transformation, not reasoning",
            "example": "'Convert this to uppercase'",
        },
    ]

    print("\n  CoT HELPS (use it!):")
    for item in helps:
        print(f"\n    Task: {item['task']}")
        print(f"    Why:  {item['why']}")
        print(f"    Gain: {item['improvement']}")

    print(f"\n{'─' * 55}")
    print("\n  CoT NOT NEEDED (skip it):")
    for item in does_not_help:
        print(f"\n    Task: {item['task']}")
        print(f"    Why:  {item['why']}")
        print(f"    Example: {item['example']}")

cot_decision_guide()
```

**Output:**
```
When to Use Chain-of-Thought Prompting
============================================================

  CoT HELPS (use it!):

    Task: Multi-step math problems
    Why:  Each step builds on the previous one
    Gain: Large (30-50% accuracy gain)

    Task: Logic and reasoning puzzles
    Why:  Forces explicit tracking of relationships
    Gain: Large (20-40% accuracy gain)

    Task: Code debugging
    Why:  Traces through execution step by step
    Gain: Moderate to large

    Task: Complex decision making
    Why:  Weighs multiple factors systematically
    Gain: Moderate

    Task: Reading comprehension with inference
    Why:  Connects multiple pieces of information
    Gain: Moderate

───────────────────────────────────────────────────────

  CoT NOT NEEDED (skip it):

    Task: Simple factual questions
    Why:  No reasoning needed, just recall
    Example: 'What is the capital of France?'

    Task: Text classification
    Why:  Pattern matching, not reasoning
    Example: 'Is this email spam or not?'

    Task: Translation
    Why:  Direct mapping, no multi-step logic
    Example: 'Translate hello to Spanish'

    Task: Simple formatting
    Why:  Transformation, not reasoning
    Example: 'Convert this to uppercase'
```

---

## The ReAct Pattern: Reason + Act

ReAct (Reasoning + Acting) extends chain-of-thought by alternating between thinking and doing. The model reasons about what it needs, takes an action (like searching or calculating), observes the result, and reasons again.

```
+----------------------------------------------------------+
|         The ReAct Loop                                    |
+----------------------------------------------------------+
|                                                            |
|     Question                                              |
|        |                                                   |
|        v                                                   |
|   +----------+                                            |
|   | THOUGHT  |  "I need to find out X first"              |
|   +----------+                                            |
|        |                                                   |
|        v                                                   |
|   +----------+                                            |
|   |  ACTION  |  Search/Calculate/Look up                  |
|   +----------+                                            |
|        |                                                   |
|        v                                                   |
|   +----------+                                            |
|   |OBSERVATION|  "The result is Y"                        |
|   +----------+                                            |
|        |                                                   |
|        v                                                   |
|   +----------+                                            |
|   | THOUGHT  |  "Now I know X, I need Z"                  |
|   +----------+                                            |
|        |                                                   |
|        v                                                   |
|      (repeat until answer is found)                       |
|        |                                                   |
|        v                                                   |
|   +----------+                                            |
|   |  ANSWER  |  Final response                            |
|   +----------+                                            |
|                                                            |
+----------------------------------------------------------+
```

**Analogy:** Imagine a detective solving a case. They do not just guess the answer. They think about what clue to look for next (Thought), go examine the evidence (Action), note what they find (Observation), then think about what it means and what to do next (Thought). ReAct works the same way.

```python
# Demonstrating the ReAct pattern

def react_pattern_demo():
    """Show how the ReAct pattern works step by step."""

    print("ReAct Pattern: Reason + Act")
    print("=" * 60)

    question = (
        "What is the population of the country where the "
        "Eiffel Tower is located, divided by 1000?"
    )

    print(f"\nQuestion: {question}")
    print()

    steps = [
        {
            "thought": (
                "I need to find which country the Eiffel Tower is in."
            ),
            "action": "Search: 'Where is the Eiffel Tower located?'",
            "observation": (
                "The Eiffel Tower is located in Paris, France."
            ),
        },
        {
            "thought": (
                "The Eiffel Tower is in France. Now I need the "
                "population of France."
            ),
            "action": "Search: 'Population of France'",
            "observation": (
                "The population of France is approximately "
                "68 million (68,000,000)."
            ),
        },
        {
            "thought": (
                "France has a population of 68,000,000. "
                "I need to divide this by 1000."
            ),
            "action": "Calculate: 68,000,000 / 1000",
            "observation": "68,000",
        },
        {
            "thought": (
                "I have the answer. The population of France "
                "divided by 1000 is 68,000."
            ),
            "action": None,
            "observation": None,
        },
    ]

    for i, step in enumerate(steps, 1):
        print(f"  Step {i}:")
        print(f"    Thought:     {step['thought']}")
        if step['action']:
            print(f"    Action:      {step['action']}")
        if step['observation']:
            print(f"    Observation: {step['observation']}")
        print()

    print("  Final Answer: 68,000")
    print()
    print("Each step decomposes a complex question into simpler")
    print("sub-tasks that can be solved one at a time.")

react_pattern_demo()
```

**Output:**
```
ReAct Pattern: Reason + Act
============================================================

Question: What is the population of the country where the Eiffel Tower is located, divided by 1000?

  Step 1:
    Thought:     I need to find which country the Eiffel Tower is in.
    Action:      Search: 'Where is the Eiffel Tower located?'
    Observation: The Eiffel Tower is located in Paris, France.

  Step 2:
    Thought:     The Eiffel Tower is in France. Now I need the population of France.
    Action:      Search: 'Population of France'
    Observation: The population of France is approximately 68 million (68,000,000).

  Step 3:
    Thought:     France has a population of 68,000,000. I need to divide this by 1000.
    Action:      Calculate: 68,000,000 / 1000
    Observation: 68,000

  Step 4:
    Thought:     I have the answer. The population of France divided by 1000 is 68,000.

  Final Answer: 68,000

Each step decomposes a complex question into simpler
sub-tasks that can be solved one at a time.
```

**Line-by-line explanation:**

- Each ReAct step has three parts: Thought (reasoning about what to do), Action (actually doing something like searching or calculating), and Observation (noting the result).
- The model decides what action to take based on its reasoning, not a fixed sequence. This makes ReAct flexible for open-ended tasks.
- In real implementations, the "Action" step can call actual tools like web search APIs, calculators, or databases. We will explore this in depth in the chapters on agents and function calling.

```python
# Building a ReAct prompt template

def build_react_prompt(question, available_actions):
    """
    Build a ReAct-style prompt that instructs the model
    to alternate between thinking and acting.

    Args:
        question: The question to answer
        available_actions: List of actions the model can take

    Returns:
        A formatted ReAct prompt string
    """

    actions_list = "\n".join(
        f"  - {action}" for action in available_actions
    )

    prompt = f"""Answer the following question by reasoning step by step.
You can use the following actions:
{actions_list}

Use this format:

Thought: [your reasoning about what to do next]
Action: [the action you want to take]
Observation: [the result of the action]
... (repeat Thought/Action/Observation as needed)
Thought: [final reasoning]
Answer: [your final answer]

Question: {question}

Thought:"""

    return prompt

# Example usage
question = "How many seconds are in the month of February 2024?"
actions = [
    "Calculate: [math expression]",
    "Search: [query]",
    "Lookup: [term or fact]"
]

prompt = build_react_prompt(question, actions)

print("ReAct Prompt Template")
print("=" * 60)
print()
print(prompt)
print()
print("The model will fill in its reasoning after 'Thought:'")
print("and alternate between thinking and acting until done.")
```

**Output:**
```
ReAct Prompt Template
============================================================

Answer the following question by reasoning step by step.
You can use the following actions:
  - Calculate: [math expression]
  - Search: [query]
  - Lookup: [term or fact]

Use this format:

Thought: [your reasoning about what to do next]
Action: [the action you want to take]
Observation: [the result of the action]
... (repeat Thought/Action/Observation as needed)
Thought: [final reasoning]
Answer: [your final answer]

Question: How many seconds are in the month of February 2024?

Thought:

The model will fill in its reasoning after 'Thought:'
and alternate between thinking and acting until done.
```

---

## Self-Consistency: Multiple Paths to Better Answers

Self-consistency is a technique where you run the same question through the model multiple times, let it reason differently each time, and then take the most common answer. This works because different reasoning paths might make different errors, but the correct answer tends to appear most often.

```
+----------------------------------------------------------+
|         Self-Consistency: Vote Among Reasoning Paths      |
+----------------------------------------------------------+
|                                                            |
|   Same question asked 5 times with CoT:                  |
|                                                            |
|   Path 1: ... reasoning ... -> Answer: 42                |
|   Path 2: ... reasoning ... -> Answer: 42                |
|   Path 3: ... reasoning ... -> Answer: 38  (error!)      |
|   Path 4: ... reasoning ... -> Answer: 42                |
|   Path 5: ... reasoning ... -> Answer: 42                |
|                                                            |
|   Majority vote: 42 (4 out of 5)                          |
|   Confidence: 80%                                         |
|                                                            |
|   This is MORE reliable than a single CoT response!      |
|                                                            |
+----------------------------------------------------------+
```

**Analogy:** Imagine asking five friends to solve the same math problem independently. If four of them get 42 and one gets 38, you would trust 42. That one friend probably made an arithmetic mistake. Self-consistency works the same way with LLM reasoning paths.

```python
# Demonstrating the self-consistency technique

import random

def self_consistency_demo():
    """
    Simulate self-consistency by running multiple
    reasoning paths and taking the majority answer.
    """

    print("Self-Consistency: Multiple Reasoning Paths")
    print("=" * 60)

    question = (
        "A bus has 25 passengers. At the first stop, 8 get off "
        "and 5 get on. At the second stop, 3 get off and 9 get on. "
        "How many passengers are on the bus?"
    )

    print(f"\nQuestion: {question}")
    print(f"\nCorrect answer: 28")

    # Simulate 5 reasoning paths (as if we called the model 5 times)
    # In practice, you would set temperature > 0 to get variation
    reasoning_paths = [
        {
            "steps": "25 - 8 = 17, 17 + 5 = 22, 22 - 3 = 19, 19 + 9 = 28",
            "answer": 28
        },
        {
            "steps": "25 - 8 + 5 = 22, 22 - 3 + 9 = 28",
            "answer": 28
        },
        {
            "steps": "25 - 8 = 17, 17 + 5 = 22, 22 - 3 = 19, 19 + 9 = 27",
            "answer": 27  # arithmetic error
        },
        {
            "steps": "Start: 25. Stop 1: -8+5 = -3, so 22. Stop 2: -3+9 = +6, so 28",
            "answer": 28
        },
        {
            "steps": "25 - 8 + 5 - 3 + 9 = 28",
            "answer": 28
        },
    ]

    print(f"\nRunning {len(reasoning_paths)} reasoning paths:")
    print("-" * 55)

    answers = []
    for i, path in enumerate(reasoning_paths, 1):
        print(f"\n  Path {i}:")
        print(f"    Reasoning: {path['steps']}")
        print(f"    Answer:    {path['answer']}")
        answers.append(path['answer'])

    # Count votes
    print(f"\n{'─' * 55}")
    print("\nMajority Vote:")
    from collections import Counter
    vote_counts = Counter(answers)
    for answer, count in vote_counts.most_common():
        pct = count / len(answers) * 100
        bar = "#" * (count * 8)
        print(f"  Answer {answer}: {count} votes ({pct:.0f}%) {bar}")

    majority = vote_counts.most_common(1)[0]
    print(f"\n  Final answer: {majority[0]} (confidence: "
          f"{majority[1]}/{len(answers)})")
    print(f"  Correct: {'Yes' if majority[0] == 28 else 'No'}")

self_consistency_demo()
```

**Output:**
```
Self-Consistency: Multiple Reasoning Paths
============================================================

Question: A bus has 25 passengers. At the first stop, 8 get off and 5 get on. At the second stop, 3 get off and 9 get on. How many passengers are on the bus?

Correct answer: 28

Running 5 reasoning paths:
-------------------------------------------------------

  Path 1:
    Reasoning: 25 - 8 = 17, 17 + 5 = 22, 22 - 3 = 19, 19 + 9 = 28
    Answer:    28

  Path 2:
    Reasoning: 25 - 8 + 5 = 22, 22 - 3 + 9 = 28
    Answer:    28

  Path 3:
    Reasoning: 25 - 8 = 17, 17 + 5 = 22, 22 - 3 = 19, 19 + 9 = 27
    Answer:    27

  Path 4:
    Reasoning: Start: 25. Stop 1: -8+5 = -3, so 22. Stop 2: -3+9 = +6, so 28
    Answer:    28

  Path 5:
    Reasoning: 25 - 8 + 5 - 3 + 9 = 28
    Answer:    28

───────────────────────────────────────────────────────

Majority Vote:
  Answer 28: 4 votes (80%) ################################
  Answer 27: 1 votes (20%) ########

  Final answer: 28 (confidence: 4/5)
  Correct: Yes
```

**Line-by-line explanation:**

- We simulate calling the model five times with the same question but slightly different reasoning paths (in practice, use `temperature > 0` to get variation).
- Path 3 has an arithmetic error (19 + 9 = 27 instead of 28), but the majority vote still arrives at the correct answer.
- The `Counter` class counts how many times each answer appears. The most common answer wins.
- Confidence is measured as the fraction of paths that agree. Higher agreement means more reliable answers.

```python
# Practical self-consistency implementation

def self_consistency_evaluate(question, num_paths=5):
    """
    A practical template for implementing self-consistency.

    In a real application, you would call the LLM API
    num_paths times with temperature > 0 and collect answers.

    Args:
        question: The question to answer
        num_paths: How many reasoning paths to generate

    Returns:
        Dictionary with the majority answer and confidence
    """

    print("Self-Consistency Implementation Template")
    print("=" * 60)

    print(f"""
    # Pseudocode for real implementation:

    from openai import OpenAI
    from collections import Counter

    client = OpenAI()
    answers = []

    for i in range({num_paths}):
        response = client.chat.completions.create(
            model="gpt-4",
            temperature=0.7,        # Allow variation
            messages=[
                {{
                    "role": "user",
                    "content": (
                        "{question}\\n"
                        "Let's think step by step. "
                        "Show your reasoning, then give "
                        "your final answer on the last line "
                        "as 'Answer: [number]'."
                    )
                }}
            ]
        )

        # Extract the answer from the response
        text = response.choices[0].message.content
        # Parse the 'Answer: X' line
        answer = extract_answer(text)
        answers.append(answer)

    # Take majority vote
    vote = Counter(answers)
    best_answer, count = vote.most_common(1)[0]
    confidence = count / {num_paths}

    return {{
        "answer": best_answer,
        "confidence": confidence,
        "all_answers": answers,
        "vote_distribution": dict(vote)
    }}
    """)

    print("Key implementation details:")
    print("  1. Use temperature > 0 (0.5-0.7 works well)")
    print("  2. Ask for 'Answer: X' format to make parsing easy")
    print("  3. Run 3-5 paths (diminishing returns after that)")
    print("  4. Higher confidence = more reliable answer")
    print("  5. If confidence is low, the question may be ambiguous")

self_consistency_evaluate(
    "What is 15% of the sum of 234 and 178?"
)
```

**Output:**
```
Self-Consistency Implementation Template
============================================================

    # Pseudocode for real implementation:

    from openai import OpenAI
    from collections import Counter

    client = OpenAI()
    answers = []

    for i in range(5):
        response = client.chat.completions.create(
            model="gpt-4",
            temperature=0.7,        # Allow variation
            messages=[
                {
                    "role": "user",
                    "content": (
                        "What is 15% of the sum of 234 and 178?\n"
                        "Let's think step by step. "
                        "Show your reasoning, then give "
                        "your final answer on the last line "
                        "as 'Answer: [number]'."
                    )
                }
            ]
        )

        # Extract the answer from the response
        text = response.choices[0].message.content
        # Parse the 'Answer: X' line
        answer = extract_answer(text)
        answers.append(answer)

    # Take majority vote
    vote = Counter(answers)
    best_answer, count = vote.most_common(1)[0]
    confidence = count / 5

    return {
        "answer": best_answer,
        "confidence": confidence,
        "all_answers": answers,
        "vote_distribution": dict(vote)
    }

Key implementation details:
  1. Use temperature > 0 (0.5-0.7 works well)
  2. Ask for 'Answer: X' format to make parsing easy
  3. Run 3-5 paths (diminishing returns after that)
  4. Higher confidence = more reliable answer
  5. If confidence is low, the question may be ambiguous
```

---

## Tree of Thoughts: Exploring Multiple Branches

Tree of Thoughts (ToT) takes self-consistency further. Instead of generating complete reasoning paths independently, the model explores multiple branches at each step and evaluates which branches are most promising before continuing.

```
+----------------------------------------------------------+
|         Tree of Thoughts Overview                         |
+----------------------------------------------------------+
|                                                            |
|  Chain-of-Thought:     One path, straight line            |
|    Step 1 -> Step 2 -> Step 3 -> Answer                   |
|                                                            |
|  Self-Consistency:     Multiple independent paths         |
|    Path A: Step 1 -> Step 2 -> Step 3 -> Answer A        |
|    Path B: Step 1 -> Step 2 -> Step 3 -> Answer B        |
|    Path C: Step 1 -> Step 2 -> Step 3 -> Answer C        |
|    (Vote on final answers)                                |
|                                                            |
|  Tree of Thoughts:     Branching with evaluation          |
|                                                            |
|                    Problem                                 |
|                   /   |   \                                |
|               Idea1 Idea2 Idea3                           |
|               /  \    |    \                               |
|             2a  2b   2c   2d                               |
|              |   X    |    X     <- prune bad branches    |
|             3a       3c                                    |
|              |        |                                    |
|           Answer1  Answer2      <- evaluate both          |
|                                                            |
|  Key difference: ToT evaluates and PRUNES at each step,  |
|  focusing effort on promising branches only.              |
|                                                            |
+----------------------------------------------------------+
```

**Analogy:** Think of planning a road trip. Chain-of-thought picks one route and follows it. Self-consistency plans five complete trips and picks the best one. Tree of thoughts starts driving, and at each intersection, considers all options, eliminates dead ends, and only continues down roads that look promising. It is more efficient because it does not waste time on paths that are clearly wrong.

```python
# Tree of Thoughts overview

def tree_of_thoughts_overview():
    """Explain Tree of Thoughts with a practical example."""

    print("Tree of Thoughts: Step-by-Step Exploration")
    print("=" * 60)

    print("""
    Problem: "Write a creative story opening that is
    suspenseful, set in winter, and involves a mystery."

    STEP 1: Generate multiple initial ideas
    ─────────────────────────────────────────

    Idea A: "A detective finds footprints in fresh snow
             that lead to a locked cabin..."

    Idea B: "During a blizzard, a radio tower picks up
             a message from someone who died last year..."

    Idea C: "A child builds a snowman that appears to
             move when no one is watching..."

    STEP 2: Evaluate each idea (score 1-10)
    ─────────────────────────────────────────

    Idea A: Suspense=7, Winter=9, Mystery=8  -> Score: 8.0
    Idea B: Suspense=9, Winter=8, Mystery=9  -> Score: 8.7
    Idea C: Suspense=6, Winter=8, Mystery=7  -> Score: 7.0

    PRUNE: Drop Idea C (lowest score)

    STEP 3: Expand top ideas further
    ─────────────────────────────────────────

    Idea A expanded:
      A1: "... inside, they find a warm cup of coffee"
      A2: "... the footprints suddenly stop mid-field"

    Idea B expanded:
      B1: "... the message contains coordinates nearby"
      B2: "... the voice is recognized as the listener's own"

    STEP 4: Evaluate expansions and select best
    ─────────────────────────────────────────

    B2 wins: Highest suspense and mystery scores.

    Final opening uses the "radio message in own voice"
    branch as the most compelling combination.
    """)

    print("Key Takeaway:")
    print("  ToT is powerful but expensive (many LLM calls).")
    print("  Use it for high-value creative or analytical tasks")
    print("  where exploring multiple approaches matters.")
    print()
    print("  For most everyday tasks, zero-shot or few-shot CoT")
    print("  is sufficient and far more cost-effective.")

tree_of_thoughts_overview()
```

**Output:**
```
Tree of Thoughts: Step-by-Step Exploration
============================================================

    Problem: "Write a creative story opening that is
    suspenseful, set in winter, and involves a mystery."

    STEP 1: Generate multiple initial ideas
    ─────────────────────────────────────────

    Idea A: "A detective finds footprints in fresh snow
             that lead to a locked cabin..."

    Idea B: "During a blizzard, a radio tower picks up
             a message from someone who died last year..."

    Idea C: "A child builds a snowman that appears to
             move when no one is watching..."

    STEP 2: Evaluate each idea (score 1-10)
    ─────────────────────────────────────────

    Idea A: Suspense=7, Winter=9, Mystery=8  -> Score: 8.0
    Idea B: Suspense=9, Winter=8, Mystery=9  -> Score: 8.7
    Idea C: Suspense=6, Winter=8, Mystery=7  -> Score: 7.0

    PRUNE: Drop Idea C (lowest score)

    STEP 3: Expand top ideas further
    ─────────────────────────────────────────

    Idea A expanded:
      A1: "... inside, they find a warm cup of coffee"
      A2: "... the footprints suddenly stop mid-field"

    Idea B expanded:
      B1: "... the message contains coordinates nearby"
      B2: "... the voice is recognized as the listener's own"

    STEP 4: Evaluate expansions and select best
    ─────────────────────────────────────────

    B2 wins: Highest suspense and mystery scores.

    Final opening uses the "radio message in own voice"
    branch as the most compelling combination.

Key Takeaway:
  ToT is powerful but expensive (many LLM calls).
  Use it for high-value creative or analytical tasks
  where exploring multiple approaches matters.

  For most everyday tasks, zero-shot or few-shot CoT
  is sufficient and far more cost-effective.
```

---

## Putting It All Together: A Complete CoT Example

Let us build a complete example that combines chain-of-thought with a practical debugging scenario.

```python
# Complete CoT example: Debugging code step by step

def cot_debugging_example():
    """
    Show how CoT helps debug code by tracing execution
    step by step.
    """

    print("Chain-of-Thought for Code Debugging")
    print("=" * 60)

    buggy_code = '''
def calculate_average(numbers):
    total = 0
    for i in range(len(numbers)):
        total += numbers[i]
    average = total / len(numbers)
    return average

result = calculate_average([])
print(result)
'''

    print("\nBuggy code:")
    for line in buggy_code.strip().split('\n'):
        print(f"  {line}")

    print("\n" + "─" * 55)

    prompt_without_cot = (
        "What is wrong with this code?\n"
        f"{buggy_code}"
    )

    prompt_with_cot = (
        "What is wrong with this code? Let's trace through "
        "the execution step by step.\n"
        f"{buggy_code}"
    )

    print("\nWithout CoT, model might say:")
    print('  "The code has a division by zero error."')
    print("  (Correct but not very helpful)")

    print("\nWith CoT, model traces execution:")
    steps = [
        "1. calculate_average is called with an empty list []",
        "2. total = 0 (initialized)",
        "3. range(len([])) = range(0), so the loop body "
        "never executes",
        "4. total remains 0",
        "5. average = total / len([]) = 0 / 0",
        "6. ZeroDivisionError! Cannot divide by zero",
        "",
        "Root cause: No check for empty list",
        "",
        "Fix: Add a guard clause at the start:",
        "  if not numbers:",
        '      return 0  # or raise ValueError("Empty list")',
    ]
    for step in steps:
        print(f"  {step}")

    print("\nThe CoT response is more thorough and provides")
    print("both the root cause and a concrete fix.")

cot_debugging_example()
```

**Output:**
```
Chain-of-Thought for Code Debugging
============================================================

Buggy code:
  def calculate_average(numbers):
      total = 0
      for i in range(len(numbers)):
          total += numbers[i]
      average = total / len(numbers)
      return average

  result = calculate_average([])
  print(result)

───────────────────────────────────────────────────────

Without CoT, model might say:
  "The code has a division by zero error."
  (Correct but not very helpful)

With CoT, model traces execution:
  1. calculate_average is called with an empty list []
  2. total = 0 (initialized)
  3. range(len([])) = range(0), so the loop body never executes
  4. total remains 0
  5. average = total / len([]) = 0 / 0
  6. ZeroDivisionError! Cannot divide by zero

  Root cause: No check for empty list

  Fix: Add a guard clause at the start:
    if not numbers:
        return 0  # or raise ValueError("Empty list")

The CoT response is more thorough and provides
both the root cause and a concrete fix.
```

---

## Comparing All Reasoning Techniques

```python
# Summary comparison of all reasoning techniques

def compare_reasoning_techniques():
    """Compare CoT, ReAct, self-consistency, and ToT."""

    print("Comparing Reasoning Techniques")
    print("=" * 60)

    techniques = [
        {
            "name": "Zero-Shot CoT",
            "how": "Add 'Let's think step by step'",
            "cost": "Low (1 API call)",
            "best_for": "Quick reasoning boost",
            "accuracy": "Good",
        },
        {
            "name": "Few-Shot CoT",
            "how": "Provide solved examples with reasoning",
            "cost": "Low (1 API call, more tokens)",
            "best_for": "Controlled reasoning format",
            "accuracy": "Better",
        },
        {
            "name": "ReAct",
            "how": "Alternate Thought/Action/Observation",
            "cost": "Medium (multiple steps per query)",
            "best_for": "Tasks needing external tools",
            "accuracy": "Good (with tool access)",
        },
        {
            "name": "Self-Consistency",
            "how": "Run CoT multiple times, majority vote",
            "cost": "High (N API calls per query)",
            "best_for": "High-stakes reasoning tasks",
            "accuracy": "Best for math/logic",
        },
        {
            "name": "Tree of Thoughts",
            "how": "Branch, evaluate, prune at each step",
            "cost": "Very high (many API calls)",
            "best_for": "Complex creative/analytical tasks",
            "accuracy": "Highest (but expensive)",
        },
    ]

    for tech in techniques:
        print(f"\n  {tech['name']}")
        print(f"    How:      {tech['how']}")
        print(f"    Cost:     {tech['cost']}")
        print(f"    Best for: {tech['best_for']}")
        print(f"    Accuracy: {tech['accuracy']}")

    print(f"\n{'─' * 55}")
    print("\nRecommendation:")
    print("  Start with zero-shot CoT (it is free and easy).")
    print("  Move to few-shot CoT if you need more control.")
    print("  Use self-consistency for high-stakes decisions.")
    print("  Reserve ToT for complex problems worth the cost.")

compare_reasoning_techniques()
```

**Output:**
```
Comparing Reasoning Techniques
============================================================

  Zero-Shot CoT
    How:      Add 'Let's think step by step'
    Cost:     Low (1 API call)
    Best for: Quick reasoning boost
    Accuracy: Good

  Few-Shot CoT
    How:      Provide solved examples with reasoning
    Cost:     Low (1 API call, more tokens)
    Best for: Controlled reasoning format
    Accuracy: Better

  ReAct
    How:      Alternate Thought/Action/Observation
    Cost:     Medium (multiple steps per query)
    Best for: Tasks needing external tools
    Accuracy: Good (with tool access)

  Self-Consistency
    How:      Run CoT multiple times, majority vote
    Cost:     High (N API calls per query)
    Best for: High-stakes reasoning tasks
    Accuracy: Best for math/logic

  Tree of Thoughts
    How:      Branch, evaluate, prune at each step
    Cost:     Very high (many API calls)
    Best for: Complex creative/analytical tasks
    Accuracy: Highest (but expensive)

───────────────────────────────────────────────────────

Recommendation:
  Start with zero-shot CoT (it is free and easy).
  Move to few-shot CoT if you need more control.
  Use self-consistency for high-stakes decisions.
  Reserve ToT for complex problems worth the cost.
```

---

## Common Mistakes

| Mistake | Why It Is Wrong | What to Do Instead |
|---------|----------------|-------------------|
| Using CoT for simple factual questions | Adds unnecessary tokens without improving accuracy | Use CoT only for reasoning tasks (math, logic, analysis) |
| Not extracting the final answer | The model buries the answer inside its reasoning | Ask the model to state the final answer clearly at the end |
| Using temperature=0 for self-consistency | All paths produce identical reasoning | Use temperature 0.5-0.7 to get diverse reasoning paths |
| Overly complex CoT instructions | The model gets confused by too many meta-instructions | Keep it simple: "Let's think step by step" often suffices |
| Ignoring CoT for code debugging | Models give shallow answers without step-by-step tracing | Ask the model to trace through execution line by line |

---

## Best Practices

1. **Start with zero-shot CoT before trying anything fancier.** Simply adding "Let's think step by step" to the end of your prompt is free and often sufficient. Only escalate to few-shot CoT or self-consistency if needed.

2. **Ask the model to state the final answer separately.** After reasoning, have it write "Final Answer: X" on its own line. This makes it easy to extract the answer programmatically.

3. **Use few-shot CoT when you need consistent reasoning format.** If your application parses the reasoning steps, provide examples that demonstrate exactly the format you need.

4. **Apply self-consistency for critical decisions.** When accuracy matters more than cost (medical reasoning, financial calculations), run 3-5 paths and take the majority vote.

5. **Match the technique to the task complexity.** Use zero-shot CoT for everyday reasoning, few-shot CoT for structured problems, self-consistency for high stakes, and Tree of Thoughts only for complex multi-branch exploration.

---

## Quick Summary

Chain-of-thought prompting asks the model to show its reasoning step by step before giving a final answer. Zero-shot CoT requires only adding a phrase like "Let's think step by step" to trigger reasoning. Few-shot CoT provides solved examples with explicit reasoning steps. The ReAct pattern extends CoT by alternating between thinking and taking actions like searching or calculating. Self-consistency runs multiple reasoning paths and takes the majority vote, improving accuracy on math and logic tasks. Tree of Thoughts explores multiple branches at each reasoning step, pruning unpromising paths early. Start with zero-shot CoT for most tasks and escalate to more expensive techniques only when accuracy demands it.

---

## Key Points

- Chain-of-thought prompting dramatically improves accuracy on math, logic, and multi-step reasoning tasks
- Zero-shot CoT requires only adding "Let's think step by step" to your prompt
- Few-shot CoT provides solved examples with reasoning to control the format and depth of the model's thinking
- The ReAct pattern (Reason + Act) alternates between thinking, taking actions, and observing results
- Self-consistency runs multiple reasoning paths and takes the majority vote for more reliable answers
- Tree of Thoughts explores and evaluates multiple branches at each step, pruning bad paths early
- CoT is most valuable for math, logic, and analysis; it is unnecessary for simple recall or classification
- Always ask the model to state the final answer clearly after its reasoning

---

## Practice Questions

1. Explain the difference between zero-shot CoT and few-shot CoT. When would you choose one over the other?

2. You are building a system that answers customer billing questions involving calculations. Which reasoning technique would you use and why? How would you handle cases where accuracy is critical?

3. Describe the ReAct pattern in your own words. What types of tasks benefit most from the Thought/Action/Observation cycle?

4. A colleague says "I just ask the model to think step by step and it works great." What additional techniques could they use to further improve accuracy? When would those be worth the extra cost?

5. Why does self-consistency work better with temperature > 0? What would happen if you used temperature = 0 for all reasoning paths?

---

## Exercises

### Exercise 1: CoT Accuracy Test

Create a set of 10 math word problems of increasing difficulty. Test each one with:
1. A direct prompt (no CoT)
2. Zero-shot CoT ("Let's think step by step")
3. Few-shot CoT (provide 2 solved examples first)

Track the accuracy of each approach and note at what difficulty level CoT starts making a significant difference.

### Exercise 2: Build a Self-Consistency Checker

Write a Python function that:
1. Takes a question and calls an LLM API 5 times with temperature=0.7
2. Extracts the final answer from each response
3. Returns the majority vote answer and confidence percentage
4. Prints a summary showing all reasoning paths and the vote distribution

### Exercise 3: ReAct Prompt Builder

Create a ReAct prompt template for a "research assistant" that can:
- Search the web for information
- Calculate mathematical expressions
- Compare two pieces of information

Test it with the question: "Which planet has more moons, Jupiter or Saturn, and what is the difference?" Trace through the expected Thought/Action/Observation steps.

---

## What Is Next?

Chain-of-thought prompting teaches the model how to reason. But where does the model's reasoning happen? In the next chapter, "System Prompts and Roles", you will learn how to control the model's behavior at a deeper level. You will discover how system prompts set the personality, tone, guardrails, and output format for an entire conversation. You will build complete chatbot setups with different personas like a customer support agent, a code reviewer, and a tutor, each behaving consistently because of well-crafted system prompts.
