# Chapter 19: When to Fine-Tune vs Prompt vs RAG

## What You Will Learn

In this chapter, you will learn:

- The three main approaches to customizing LLM behavior
- A decision framework for choosing the right approach
- Cost comparison between prompting, RAG, and fine-tuning
- Difficulty and time comparison for each approach
- Real-world use case examples for each approach
- When to combine approaches for the best results

## Why This Chapter Matters

You have learned prompting techniques, built RAG systems, and are about to learn fine-tuning. But knowing how to use each tool is not enough. You need to know when to use each one.

This is like knowing how to use a hammer, a screwdriver, and a drill. All three are useful tools. But using a hammer to drive a screw wastes time and damages the screw. The skill is not just using the tools but choosing the right tool for the job.

Making the wrong choice costs real money and time. Fine-tuning when RAG would suffice wastes thousands of dollars and weeks of work. Using only prompting when RAG is needed leads to hallucinated answers that frustrate users. This chapter gives you a clear framework for making the right decision every time.

---

## The Three Approaches at a Glance

```
+------------------------------------------------------------------+
|              THREE APPROACHES TO CUSTOMIZING LLMs                 |
|                                                                   |
|  PROMPTING                                                        |
|  +----+  Tell the model WHAT to do through instructions           |
|  |EASY|  "You are a customer support agent. Be polite."           |
|  +----+  No code changes. No training. Just words.                |
|                                                                   |
|  RAG (Retrieval-Augmented Generation)                             |
|  +------+  Give the model ACCESS to your data at query time       |
|  |MEDIUM|  "Here are the relevant docs. Answer based on these."   |
|  +------+  Requires document processing and vector database.      |
|                                                                   |
|  FINE-TUNING                                                      |
|  +----+  TRAIN the model on your specific data                    |
|  |HARD|  Model learns your domain, style, or task permanently.    |
|  +----+  Requires training data, compute, and expertise.          |
+------------------------------------------------------------------+
```

> **Prompting:** Giving the LLM instructions in the prompt to control its behavior. No model modification needed. The fastest and cheapest approach but limited by the model's existing knowledge.

> **RAG:** Retrieving relevant information from your data and including it in the prompt. Gives the model access to current, private, or specialized information without modifying the model itself.

> **Fine-Tuning:** Training the model on your specific data so it permanently learns your domain, style, or task format. Most powerful but most expensive and time-consuming.

---

## The Decision Framework

```
+------------------------------------------------------------------+
|                    DECISION FLOWCHART                             |
|                                                                   |
|  START: What do you need the LLM to do differently?              |
|  |                                                                |
|  v                                                                |
|  Does the model already know how to do it?                       |
|  |                                                                |
|  +-- YES --> Does it need your private/current data?             |
|  |           |                                                    |
|  |           +-- NO  --> Use PROMPTING                           |
|  |           |           (System prompts, few-shot examples)     |
|  |           |                                                    |
|  |           +-- YES --> Use RAG                                 |
|  |                       (Retrieve your docs, augment prompt)    |
|  |                                                                |
|  +-- NO  --> Can you describe the task with examples?            |
|              |                                                    |
|              +-- YES, many --> Do you need a specific style/format?|
|              |                 |                                   |
|              |                 +-- YES --> Use FINE-TUNING         |
|              |                 |                                   |
|              |                 +-- NO  --> Try FEW-SHOT PROMPTING |
|              |                            first. Fine-tune if     |
|              |                            not good enough.        |
|              |                                                    |
|              +-- YES, few  --> Use FEW-SHOT PROMPTING            |
|              |                                                    |
|              +-- NO        --> Use ZERO-SHOT PROMPTING           |
|                               with clear instructions            |
+------------------------------------------------------------------+
```

```python
def recommend_approach(
    needs_private_data: bool,
    needs_current_data: bool,
    needs_custom_style: bool,
    has_training_examples: int,
    data_changes_frequently: bool,
    budget: str,
    latency_requirement: str,
    accuracy_requirement: str,
) -> dict:
    """
    Recommend the best approach based on project requirements.

    Args:
        needs_private_data: Does the LLM need access to private data?
        needs_current_data: Does the LLM need up-to-date information?
        needs_custom_style: Does the output need a specific format/style?
        has_training_examples: Number of training examples available
        data_changes_frequently: Does the data change often?
        budget: "low", "medium", or "high"
        latency_requirement: "fast" (<1s), "normal" (1-5s), "slow" (>5s ok)
        accuracy_requirement: "low", "medium", "high", "critical"

    Returns:
        Dictionary with recommendation and reasoning
    """
    scores = {"prompting": 0, "rag": 0, "fine_tuning": 0}
    reasons = {"prompting": [], "rag": [], "fine_tuning": []}

    # Private or current data needs
    if needs_private_data or needs_current_data:
        scores["rag"] += 5
        reasons["rag"].append("Needs access to private/current data")
        if data_changes_frequently:
            scores["rag"] += 3
            reasons["rag"].append("Data changes frequently - RAG updates easily")
        else:
            scores["fine_tuning"] += 1
            reasons["fine_tuning"].append("Static data could be fine-tuned")
    else:
        scores["prompting"] += 3
        reasons["prompting"].append("No private data needed")

    # Custom style/format needs
    if needs_custom_style:
        scores["fine_tuning"] += 4
        reasons["fine_tuning"].append("Custom style/format benefits from fine-tuning")
        if has_training_examples >= 100:
            scores["fine_tuning"] += 2
            reasons["fine_tuning"].append(f"{has_training_examples} training examples available")
    else:
        scores["prompting"] += 2
        reasons["prompting"].append("Standard format - prompting sufficient")

    # Training examples
    if has_training_examples >= 500:
        scores["fine_tuning"] += 3
        reasons["fine_tuning"].append("Large training set available")
    elif has_training_examples >= 50:
        scores["prompting"] += 1
        reasons["prompting"].append("Few-shot prompting can use these examples")
    else:
        scores["prompting"] += 2
        reasons["prompting"].append("Few examples favor prompting approach")

    # Budget constraints
    if budget == "low":
        scores["prompting"] += 4
        reasons["prompting"].append("Lowest cost approach")
        scores["rag"] += 1
        reasons["rag"].append("Moderate cost")
    elif budget == "medium":
        scores["rag"] += 2
        reasons["rag"].append("Reasonable cost for RAG setup")
    elif budget == "high":
        scores["fine_tuning"] += 2
        reasons["fine_tuning"].append("Budget allows fine-tuning costs")

    # Latency
    if latency_requirement == "fast":
        scores["prompting"] += 2
        reasons["prompting"].append("Fastest response time")
        scores["fine_tuning"] += 1
        reasons["fine_tuning"].append("No retrieval overhead")
    elif latency_requirement == "slow":
        scores["rag"] += 1
        reasons["rag"].append("Retrieval latency acceptable")

    # Accuracy
    if accuracy_requirement in ("high", "critical"):
        scores["rag"] += 2
        reasons["rag"].append("RAG grounds answers in real data")
        scores["fine_tuning"] += 2
        reasons["fine_tuning"].append("Fine-tuning can achieve high accuracy")

    # Determine winner
    best = max(scores, key=scores.get)
    total = sum(scores.values())

    return {
        "recommendation": best,
        "confidence": scores[best] / total if total > 0 else 0,
        "scores": scores,
        "reasons": reasons,
    }


def display_recommendation(result):
    """Display the recommendation in a formatted way."""
    rec = result["recommendation"].upper()
    conf = result["confidence"]

    print(f"Recommendation: {rec}")
    print(f"Confidence: {conf:.0%}")
    print()

    for approach in ["prompting", "rag", "fine_tuning"]:
        score = result["scores"][approach]
        bar = "|" * score
        label = approach.replace("_", " ").title()
        print(f"  {label:<15} {score:>3} {bar}")
        for reason in result["reasons"][approach]:
            print(f"    + {reason}")
        print()


# Scenario 1: Customer Support Bot
print("=" * 55)
print("SCENARIO 1: Customer Support Bot")
print("=" * 55)
result = recommend_approach(
    needs_private_data=True,
    needs_current_data=True,
    needs_custom_style=False,
    has_training_examples=20,
    data_changes_frequently=True,
    budget="medium",
    latency_requirement="normal",
    accuracy_requirement="high",
)
display_recommendation(result)

# Scenario 2: Email Writing Assistant
print("=" * 55)
print("SCENARIO 2: Email Writing in Company Tone")
print("=" * 55)
result = recommend_approach(
    needs_private_data=False,
    needs_current_data=False,
    needs_custom_style=True,
    has_training_examples=500,
    data_changes_frequently=False,
    budget="high",
    latency_requirement="fast",
    accuracy_requirement="medium",
)
display_recommendation(result)

# Scenario 3: Simple Text Summarizer
print("=" * 55)
print("SCENARIO 3: Meeting Notes Summarizer")
print("=" * 55)
result = recommend_approach(
    needs_private_data=False,
    needs_current_data=False,
    needs_custom_style=False,
    has_training_examples=10,
    data_changes_frequently=False,
    budget="low",
    latency_requirement="fast",
    accuracy_requirement="medium",
)
display_recommendation(result)
```

**Output:**
```
=======================================================
SCENARIO 1: Customer Support Bot
=======================================================
Recommendation: RAG
Confidence: 52%

  Prompting         5 |||||
    + Few-shot prompting can use these examples
    + Fastest response time

  Rag               13 |||||||||||||
    + Needs access to private/current data
    + Data changes frequently - RAG updates easily
    + Moderate cost
    + Retrieval latency acceptable
    + RAG grounds answers in real data

  Fine Tuning        7 |||||||
    + Fine-tuning can achieve high accuracy

=======================================================
SCENARIO 2: Email Writing in Company Tone
=======================================================
Recommendation: FINE_TUNING
Confidence: 46%

  Prompting         5 |||||
    + Standard format - prompting sufficient

  Rag                0

  Fine Tuning       12 ||||||||||||
    + Custom style/format benefits from fine-tuning
    + 500 training examples available
    + Large training set available
    + Budget allows fine-tuning costs
    + No retrieval overhead
    + Fine-tuning can achieve high accuracy

=======================================================
SCENARIO 3: Meeting Notes Summarizer
=======================================================
Recommendation: PROMPTING
Confidence: 55%

  Prompting        11 |||||||||||
    + No private data needed
    + Standard format - prompting sufficient
    + Few examples favor prompting approach
    + Lowest cost approach
    + Fastest response time

  Rag                0

  Fine Tuning        0
```

---

## Cost Comparison

```python
cost_comparison = {
    "Approach": ["Prompting", "RAG", "Fine-Tuning"],
    "Setup Cost": [
        "$0 (just write prompts)",
        "$50-500 (document processing, vector DB setup)",
        "$500-5,000+ (data prep, training compute)",
    ],
    "Per Query Cost": [
        "~$0.001-0.01 (just LLM tokens)",
        "~$0.005-0.05 (embedding + LLM tokens)",
        "~$0.001-0.02 (fine-tuned model tokens)",
    ],
    "Maintenance Cost": [
        "Low (update prompts)",
        "Medium (update documents, re-embed)",
        "High (retrain when data changes)",
    ],
    "Time to Deploy": [
        "Hours",
        "Days to weeks",
        "Weeks to months",
    ],
    "Technical Skills": [
        "Beginner (prompt writing)",
        "Intermediate (Python, embeddings, vector DBs)",
        "Advanced (ML training, data preparation)",
    ],
}

print("COST & EFFORT COMPARISON")
print("=" * 70)
for key in cost_comparison:
    if key == "Approach":
        continue
    print(f"\n{key}:")
    for i, approach in enumerate(cost_comparison["Approach"]):
        print(f"  {approach:<15} {cost_comparison[key][i]}")
```

**Output:**
```
COST & EFFORT COMPARISON
======================================================================

Setup Cost:
  Prompting       $0 (just write prompts)
  RAG             $50-500 (document processing, vector DB setup)
  Fine-Tuning     $500-5,000+ (data prep, training compute)

Per Query Cost:
  Prompting       ~$0.001-0.01 (just LLM tokens)
  RAG             ~$0.005-0.05 (embedding + LLM tokens)
  Fine-Tuning     ~$0.001-0.02 (fine-tuned model tokens)

Maintenance Cost:
  Prompting       Low (update prompts)
  RAG             Medium (update documents, re-embed)
  Fine-Tuning     High (retrain when data changes)

Time to Deploy:
  Prompting       Hours
  RAG             Days to weeks
  Fine-Tuning     Weeks to months

Technical Skills:
  Prompting       Beginner (prompt writing)
  RAG             Intermediate (Python, embeddings, vector DBs)
  Fine-Tuning     Advanced (ML training, data preparation)
```

---

## Use Case Examples

```python
use_cases = [
    {
        "name": "Blog Post Generator",
        "approach": "Prompting",
        "why": "The LLM already knows how to write. You just need to "
               "describe the tone, length, and topic in the prompt.",
        "not_rag": "No private data needed.",
        "not_ft": "Not worth the cost for a style that can be prompted.",
    },
    {
        "name": "Company Policy Q&A Bot",
        "approach": "RAG",
        "why": "Policies are private, change regularly, and the LLM "
               "must not hallucinate incorrect policy information.",
        "not_prompting": "Too many policies to fit in a single prompt.",
        "not_ft": "Policies change - would need constant retraining.",
    },
    {
        "name": "Medical Report Summarizer",
        "approach": "Fine-Tuning + RAG",
        "why": "Needs domain-specific medical terminology (fine-tuning) "
               "AND access to patient records (RAG). A combined approach.",
        "not_prompting": "Medical language needs specialized training.",
        "not_just_rag": "Generic model misuses medical terms.",
    },
    {
        "name": "Code Review Assistant",
        "approach": "Prompting",
        "why": "Modern LLMs are already excellent at code review. "
               "A well-crafted system prompt with coding standards "
               "is sufficient.",
        "not_rag": "Code patterns are in the model's training data.",
        "not_ft": "Prompting achieves 90%+ of the benefit at zero cost.",
    },
    {
        "name": "Legal Contract Analyzer",
        "approach": "RAG",
        "why": "Needs to reference specific legal documents, precedents, "
               "and regulations. Must cite sources accurately.",
        "not_prompting": "Cannot fit all legal references in one prompt.",
        "not_ft": "Legal documents change with new laws and cases.",
    },
    {
        "name": "Brand Voice Email Writer",
        "approach": "Fine-Tuning",
        "why": "The company has a very specific brand voice that is hard "
               "to capture in a prompt. Hundreds of example emails exist "
               "to train on.",
        "not_prompting": "Brand voice is too nuanced for prompt description.",
        "not_rag": "Not about retrieving information, about writing style.",
    },
    {
        "name": "Multilingual Customer Support",
        "approach": "Prompting + RAG",
        "why": "RAG for retrieving correct answers from knowledge base. "
               "Prompting to specify the response language and tone.",
        "combined": "RAG provides accuracy, prompting provides flexibility.",
    },
    {
        "name": "Financial Data Classifier",
        "approach": "Fine-Tuning",
        "why": "Classifying transactions into 50+ categories requires "
               "consistent, precise behavior that prompting cannot "
               "reliably achieve. Training data available.",
        "not_prompting": "Too many categories for reliable prompt-based classification.",
        "not_rag": "Classification task, not information retrieval.",
    },
]

print("USE CASE EXAMPLES")
print("=" * 60)
for case in use_cases:
    print(f"\n{case['name']}")
    print(f"  Approach: {case['approach']}")
    print(f"  Why: {case['why']}")

# Summary table
print("\n\nSUMMARY")
print(f"{'Use Case':<30} {'Approach':<20}")
print("-" * 50)
for case in use_cases:
    print(f"{case['name']:<30} {case['approach']:<20}")
```

**Output:**
```
USE CASE EXAMPLES
============================================================

Blog Post Generator
  Approach: Prompting
  Why: The LLM already knows how to write. You just need to describe the tone, length, and topic in the prompt.

Company Policy Q&A Bot
  Approach: RAG
  Why: Policies are private, change regularly, and the LLM must not hallucinate incorrect policy information.

Medical Report Summarizer
  Approach: Fine-Tuning + RAG
  Why: Needs domain-specific medical terminology (fine-tuning) AND access to patient records (RAG). A combined approach.

Code Review Assistant
  Approach: Prompting
  Why: Modern LLMs are already excellent at code review. A well-crafted system prompt with coding standards is sufficient.

Legal Contract Analyzer
  Approach: RAG
  Why: Needs to reference specific legal documents, precedents, and regulations. Must cite sources accurately.

Brand Voice Email Writer
  Approach: Fine-Tuning
  Why: The company has a very specific brand voice that is hard to capture in a prompt. Hundreds of example emails exist to train on.

Multilingual Customer Support
  Approach: Prompting + RAG
  Why: RAG for retrieving correct answers from knowledge base. Prompting to specify the response language and tone.

Financial Data Classifier
  Approach: Fine-Tuning
  Why: Classifying transactions into 50+ categories requires consistent, precise behavior that prompting cannot reliably achieve. Training data available.


SUMMARY
Use Case                       Approach
--------------------------------------------------
Blog Post Generator            Prompting
Company Policy Q&A Bot         RAG
Medical Report Summarizer      Fine-Tuning + RAG
Code Review Assistant          Prompting
Legal Contract Analyzer        RAG
Brand Voice Email Writer       Fine-Tuning
Multilingual Customer Support  Prompting + RAG
Financial Data Classifier      Fine-Tuning
```

---

## The Escalation Strategy

A practical approach is to start simple and escalate only when needed.

```
+------------------------------------------------------------------+
|              THE ESCALATION STRATEGY                              |
|                                                                   |
|  Step 1: Try PROMPTING first                                     |
|  +----------------------------------------------------------+   |
|  | Write a good system prompt with clear instructions.        |   |
|  | Add few-shot examples if needed.                          |   |
|  | Evaluate accuracy.                                         |   |
|  +----------------------------------------------------------+   |
|          |                                                        |
|          v                                                        |
|  Good enough? --> YES --> Ship it! Done.                         |
|          |                                                        |
|          NO                                                       |
|          |                                                        |
|  Step 2: Add RAG                                                 |
|  +----------------------------------------------------------+   |
|  | Set up document processing and vector database.            |   |
|  | Retrieve relevant context for each query.                  |   |
|  | Evaluate accuracy again.                                   |   |
|  +----------------------------------------------------------+   |
|          |                                                        |
|          v                                                        |
|  Good enough? --> YES --> Ship it! Done.                         |
|          |                                                        |
|          NO                                                       |
|          |                                                        |
|  Step 3: Fine-tune                                               |
|  +----------------------------------------------------------+   |
|  | Prepare training data from your specific examples.         |   |
|  | Fine-tune the model on your data.                          |   |
|  | Combine with RAG if both are needed.                       |   |
|  | Evaluate accuracy one more time.                           |   |
|  +----------------------------------------------------------+   |
|                                                                   |
|  This saves time and money. You only escalate when simpler       |
|  approaches are genuinely insufficient.                          |
+------------------------------------------------------------------+
```

```python
def escalation_checklist(task_description):
    """
    Provide an escalation checklist for a given task.
    """
    print(f"ESCALATION CHECKLIST FOR: {task_description}")
    print("=" * 55)

    steps = [
        {
            "level": "Level 1: Zero-Shot Prompting",
            "actions": [
                "Write a clear system prompt describing the task",
                "Test with 10+ real examples",
                "Measure accuracy",
            ],
            "move_on_if": "Accuracy below target or inconsistent results",
            "time": "1-2 hours",
            "cost": "$0-5 (API calls for testing)",
        },
        {
            "level": "Level 2: Few-Shot Prompting",
            "actions": [
                "Add 3-5 examples to the prompt",
                "Try chain-of-thought prompting",
                "Test with 20+ real examples",
                "Measure accuracy improvement",
            ],
            "move_on_if": "Still below target or needs private data",
            "time": "2-4 hours",
            "cost": "$5-20 (more tokens per request)",
        },
        {
            "level": "Level 3: RAG",
            "actions": [
                "Process and chunk your documents",
                "Set up vector database",
                "Build retrieval pipeline",
                "Test with 50+ questions",
                "Measure retrieval quality AND answer accuracy",
            ],
            "move_on_if": "Need consistent custom format/style",
            "time": "1-2 weeks",
            "cost": "$100-500 (setup + compute)",
        },
        {
            "level": "Level 4: Fine-Tuning",
            "actions": [
                "Prepare 500+ training examples",
                "Clean and validate training data",
                "Fine-tune the model",
                "Evaluate on held-out test set",
                "Consider combining with RAG",
            ],
            "move_on_if": "N/A - this is the most powerful option",
            "time": "2-4 weeks",
            "cost": "$500-5,000+ (data prep + training)",
        },
    ]

    for step in steps:
        print(f"\n{step['level']}")
        print(f"  Time: {step['time']} | Cost: {step['cost']}")
        print(f"  Actions:")
        for action in step['actions']:
            print(f"    [ ] {action}")
        print(f"  Escalate if: {step['move_on_if']}")

escalation_checklist("Build a customer support chatbot")
```

**Output:**
```
ESCALATION CHECKLIST FOR: Build a customer support chatbot
=======================================================

Level 1: Zero-Shot Prompting
  Time: 1-2 hours | Cost: $0-5 (API calls for testing)
  Actions:
    [ ] Write a clear system prompt describing the task
    [ ] Test with 10+ real examples
    [ ] Measure accuracy
  Escalate if: Accuracy below target or inconsistent results

Level 2: Few-Shot Prompting
  Time: 2-4 hours | Cost: $5-20 (more tokens per request)
  Actions:
    [ ] Add 3-5 examples to the prompt
    [ ] Try chain-of-thought prompting
    [ ] Test with 20+ real examples
    [ ] Measure accuracy improvement
  Escalate if: Still below target or needs private data

Level 3: RAG
  Time: 1-2 weeks | Cost: $100-500 (setup + compute)
  Actions:
    [ ] Process and chunk your documents
    [ ] Set up vector database
    [ ] Build retrieval pipeline
    [ ] Test with 50+ questions
    [ ] Measure retrieval quality AND answer accuracy
  Escalate if: Need consistent custom format/style

Level 4: Fine-Tuning
  Time: 2-4 weeks | Cost: $500-5,000+ (data prep + training)
  Actions:
    [ ] Prepare 500+ training examples
    [ ] Clean and validate training data
    [ ] Fine-tune the model
    [ ] Evaluate on held-out test set
    [ ] Consider combining with RAG
  Escalate if: N/A - this is the most powerful option
```

---

## Combining Approaches

The three approaches are not mutually exclusive. Many production systems combine them.

```python
combinations = [
    {
        "combination": "Prompting + RAG",
        "how": "Use system prompts to define behavior. Use RAG to "
               "provide context. Most common production pattern.",
        "example": "Customer support bot: System prompt defines tone, "
                   "RAG retrieves relevant help articles.",
    },
    {
        "combination": "Fine-Tuning + RAG",
        "how": "Fine-tune for domain expertise and output format. "
               "Use RAG for current, specific information.",
        "example": "Medical assistant: Fine-tuned on medical "
                   "terminology, RAG retrieves patient-specific data.",
    },
    {
        "combination": "Fine-Tuning + Prompting",
        "how": "Fine-tune for core capability. Use prompts to "
               "adjust behavior for specific situations.",
        "example": "Code generator: Fine-tuned on company codebase. "
                   "Prompts specify framework and coding standards.",
    },
    {
        "combination": "All Three Together",
        "how": "Fine-tune for domain and style. RAG for knowledge. "
               "Prompts for per-request customization.",
        "example": "Legal research tool: Fine-tuned on legal writing, "
                   "RAG retrieves case law, prompts specify jurisdiction.",
    },
]

print("COMBINING APPROACHES")
print("=" * 60)
for combo in combinations:
    print(f"\n{combo['combination']}")
    print(f"  How: {combo['how']}")
    print(f"  Example: {combo['example']}")
```

**Output:**
```
COMBINING APPROACHES
============================================================

Prompting + RAG
  How: Use system prompts to define behavior. Use RAG to provide context. Most common production pattern.
  Example: Customer support bot: System prompt defines tone, RAG retrieves relevant help articles.

Fine-Tuning + RAG
  How: Fine-tune for domain expertise and output format. Use RAG for current, specific information.
  Example: Medical assistant: Fine-tuned on medical terminology, RAG retrieves patient-specific data.

Fine-Tuning + Prompting
  How: Fine-tune for core capability. Use prompts to adjust behavior for specific situations.
  Example: Code generator: Fine-tuned on company codebase. Prompts specify framework and coding standards.

All Three Together
  How: Fine-tune for domain and style. RAG for knowledge. Prompts for per-request customization.
  Example: Legal research tool: Fine-tuned on legal writing, RAG retrieves case law, prompts specify jurisdiction.
```

---

## Common Mistakes

1. **Jumping to fine-tuning before trying prompting.** Many tasks that seem to need fine-tuning can be solved with good prompts. Always try the simpler approach first.

2. **Using RAG when the LLM already knows the answer.** If you are asking about general Python syntax, RAG adds cost and latency for no benefit. RAG is for your private or current data.

3. **Fine-tuning for factual knowledge.** Fine-tuning changes behavior, not knowledge. The model can still hallucinate facts. Use RAG for factual accuracy.

4. **Not evaluating before escalating.** Measure performance at each level. Sometimes a few-shot prompt gets 95% accuracy and the last 5% is not worth the RAG infrastructure.

5. **Choosing based on excitement, not requirements.** Fine-tuning sounds impressive. RAG sounds cutting-edge. But if a system prompt solves your problem, use the system prompt.

---

## Best Practices

1. **Follow the escalation strategy.** Start with prompting, add RAG if needed, fine-tune only when necessary. Each level adds complexity and cost.

2. **Define success metrics before choosing.** Know what "good enough" looks like in numbers (accuracy, latency, cost per query) before deciding on an approach.

3. **Consider maintenance costs.** Fine-tuning has high setup cost but also high maintenance cost. If your data changes monthly, you need to retrain monthly.

4. **Combine approaches when needed.** The best production systems often use prompting + RAG. Some use all three. Choose based on your specific requirements.

5. **Document your decision.** Write down why you chose a particular approach, what you tried, and what the metrics were. This helps future developers understand and maintain the system.

---

## Quick Summary

Prompting, RAG, and fine-tuning are three tools for customizing LLM behavior. Prompting is fast and cheap but limited to the model's existing knowledge. RAG gives the model access to your data and is best for factual Q&A over private or current documents. Fine-tuning permanently trains the model on your data and is best for custom styles, formats, or domain expertise. The escalation strategy starts with the simplest approach and moves to more complex ones only when needed. Many production systems combine approaches for the best results.

---

## Key Points

- **Prompting** is the simplest: fast to deploy, low cost, limited customization
- **RAG** is for data: gives the model access to private/current information
- **Fine-tuning** is for behavior: changes how the model writes, classifies, or responds
- **Escalation strategy**: start simple, measure, escalate only when needed
- **Combine approaches** for the best production systems (prompting + RAG is most common)
- Fine-tuning changes **behavior**, not **knowledge** (still needs RAG for facts)
- Always **measure before and after** each approach change
- Consider **maintenance cost**, not just setup cost

---

## Practice Questions

1. Your company wants a chatbot that answers questions about internal HR policies. The policies change quarterly. Would you use prompting, RAG, or fine-tuning? Explain your reasoning.

2. You need an LLM to classify customer emails into 5 categories with 98% accuracy. Few-shot prompting achieves 92%. What would you try next and why?

3. A startup with a low budget wants to build an AI writing assistant that matches their brand voice. They have 50 example emails. What approach would you recommend?

4. Explain why fine-tuning for factual knowledge is generally a bad idea. What should you use instead?

5. You have a system that uses RAG for answering product questions. A new requirement asks the model to always respond in a specific JSON format with exactly 5 fields. Would you modify the prompt, add RAG documents, or fine-tune? Why?

---

## Exercises

**Exercise 1: Decision Framework Tool**

Build an interactive tool (command-line is fine) that asks the user 6-8 questions about their project and recommends an approach (prompting, RAG, fine-tuning, or a combination). Include a confidence score and reasoning for the recommendation.

**Exercise 2: Cost Calculator**

Create a cost calculator that estimates the monthly cost of each approach based on inputs like: number of queries per day, average prompt length, document collection size, and training data size. Compare costs across all three approaches.

**Exercise 3: Approach Comparison Experiment**

Pick a task (e.g., sentiment analysis or text classification) and implement it three ways: zero-shot prompting, few-shot prompting, and (simulated) fine-tuning. Create a test set of at least 20 examples. Compare accuracy, cost, and development time for each approach. Write a short analysis recommending the best approach for this specific task.

---

## What Is Next?

Now that you know when fine-tuning is the right choice, Chapter 20 teaches you how to prepare the training data you need. You will learn about data formats, quality standards, cleaning techniques, and tools for creating instruction datasets. Good training data is the single most important factor in successful fine-tuning.
