# Chapter 5: The Training Pipeline

## What You Will Learn

In this chapter, you will learn:

- The three main stages of training an LLM: pre-training, supervised fine-tuning (SFT), and alignment
- How pre-training on massive text teaches a model language patterns
- What supervised fine-tuning is and how it teaches a model to follow instructions
- How RLHF (Reinforcement Learning from Human Feedback) works
- What DPO (Direct Preference Optimization) is and why it is simpler than RLHF
- How each stage transforms the model's behavior

## Why This Chapter Matters

A raw pre-trained LLM is like a brilliant but unsocialized genius. It knows everything it read, but it does not know how to have a helpful conversation. It might answer a question with another question, continue writing your sentence instead of responding to it, or generate harmful content without hesitation.

The training pipeline is the process that turns this raw intelligence into a helpful, safe assistant. Understanding this pipeline tells you why LLMs behave the way they do. When a model refuses to answer a harmful question, that is alignment at work. When it follows your instructions precisely, that is supervised fine-tuning. When it generates fluent, knowledgeable text, that is pre-training.

---

## The Three Stages Overview

```
+------------------------------------------------------------------+
|              The LLM Training Pipeline                            |
+------------------------------------------------------------------+
|                                                                    |
|  Stage 1: PRE-TRAINING                                            |
|  ┌──────────────────────────────────────────────┐                 |
|  │  Input: Trillions of tokens from the internet │                |
|  │  Goal:  Learn language patterns               │                |
|  │  Cost:  Millions of dollars                   │                |
|  │  Time:  Weeks to months                       │                |
|  │  Result: "Base model" - predicts next tokens  │                |
|  └──────────────────────────────────────────────┘                 |
|                     │                                              |
|                     ▼                                              |
|  Stage 2: SUPERVISED FINE-TUNING (SFT)                            |
|  ┌──────────────────────────────────────────────┐                 |
|  │  Input: Thousands of (prompt, response) pairs │                |
|  │  Goal:  Learn to follow instructions          │                |
|  │  Cost:  Thousands of dollars                  │                |
|  │  Time:  Hours to days                         │                |
|  │  Result: "Instruction-tuned model"            │                |
|  └──────────────────────────────────────────────┘                 |
|                     │                                              |
|                     ▼                                              |
|  Stage 3: ALIGNMENT (RLHF or DPO)                                |
|  ┌──────────────────────────────────────────────┐                 |
|  │  Input: Human preference rankings            │                 |
|  │  Goal:  Be helpful, harmless, and honest     │                 |
|  │  Cost:  Tens of thousands of dollars          │                |
|  │  Time:  Days to weeks                         │                |
|  │  Result: "Aligned model" - safe and helpful   │                |
|  └──────────────────────────────────────────────┘                 |
|                                                                    |
+------------------------------------------------------------------+
```

**Analogy:** Think of training an LLM like educating a person:
- **Pre-training** = reading every book in every library (general knowledge)
- **SFT** = going to school and learning to answer questions properly (following instructions)
- **Alignment** = learning social norms and ethics (being helpful and safe)

---

## Stage 1: Pre-Training

### What Happens During Pre-Training

Pre-training is the most expensive and time-consuming stage. The model reads trillions of tokens of text and learns to predict the next token.

```
+----------------------------------------------------------+
|           Pre-Training Data Sources                       |
+----------------------------------------------------------+
|                                                            |
|  Common Crawl      | Web pages scraped from the internet |
|  Wikipedia          | Encyclopedic knowledge              |
|  Books              | Fiction and non-fiction              |
|  Academic papers    | Scientific and technical knowledge  |
|  Code repositories  | GitHub, GitLab, etc.                |
|  Forums             | Reddit, Stack Overflow              |
|  News articles      | Current events and reporting        |
|                                                            |
|  Total: Often 1-15 trillion tokens                       |
|  After filtering and deduplication                       |
|                                                            |
+----------------------------------------------------------+
```

```python
# Simulating the pre-training process

def pretrain_simulation():
    """
    Simulate how pre-training works at a conceptual level.
    The model learns to predict the next token from massive text.
    """

    # Training examples (in reality: trillions of these)
    training_data = [
        "The capital of France is Paris.",
        "Python is a programming language.",
        "Water boils at 100 degrees Celsius.",
        "The cat sat on the mat.",
        "Machine learning is a subset of artificial intelligence.",
        "def hello(): print('Hello, World!')",
        "The Earth orbits the Sun.",
        "2 + 2 = 4",
    ]

    print("PRE-TRAINING SIMULATION")
    print("=" * 60)
    print(f"\nTraining data: {len(training_data)} examples")
    print("(Real models use trillions of tokens)\n")

    # Show what the model learns from each example
    for i, text in enumerate(training_data):
        words = text.split()
        # Show partial context -> prediction learning
        if len(words) >= 4:
            context = " ".join(words[:3])
            target = words[3]
            print(f"  Example {i+1}: '{text}'")
            print(f"    Model learns: '{context} ___' -> '{target}'")
            print()

    # What the model looks like at different stages
    stages = [
        ("Before training (random)", {
            "The capital of France is": {
                "Paris": 0.002, "banana": 0.003,
                "the": 0.005, "running": 0.004
            }
        }),
        ("After 1% of training", {
            "The capital of France is": {
                "Paris": 0.05, "London": 0.04,
                "the": 0.08, "a": 0.06
            }
        }),
        ("After 50% of training", {
            "The capital of France is": {
                "Paris": 0.45, "the": 0.05,
                "a": 0.03, "Lyon": 0.02
            }
        }),
        ("After 100% of training", {
            "The capital of France is": {
                "Paris": 0.82, "the": 0.02,
                "a": 0.01, "Lyon": 0.01
            }
        }),
    ]

    print("\nModel's prediction for 'The capital of France is ___':")
    print("-" * 55)
    for stage_name, predictions in stages:
        print(f"\n  {stage_name}:")
        for context, probs in predictions.items():
            for word, prob in probs.items():
                bar = "█" * int(prob * 40)
                print(f"    {word:10s}: {prob:.1%} {bar}")

pretrain_simulation()
```

**Output:**
```
PRE-TRAINING SIMULATION
============================================================

Training data: 8 examples
(Real models use trillions of tokens)

  Example 1: 'The capital of France is Paris.'
    Model learns: 'The capital of ___' -> 'France'

  Example 2: 'Python is a programming language.'
    Model learns: 'Python is a ___' -> 'programming'

  Example 3: 'Water boils at 100 degrees Celsius.'
    Model learns: 'Water boils at ___' -> '100'

  Example 4: 'The cat sat on the mat.'
    Model learns: 'The cat sat ___' -> 'on'

  Example 5: 'Machine learning is a subset of artificial intelligence.'
    Model learns: 'Machine learning is ___' -> 'a'

  Example 6: 'def hello(): print('Hello, World!')'
    Model learns: 'def hello(): ___' -> 'print('Hello,'

  Example 7: 'The Earth orbits the Sun.'
    Model learns: 'The Earth orbits ___' -> 'the'

  Example 8: '2 + 2 = 4'
    Model learns: '2 + 2 ___' -> '='

Model's prediction for 'The capital of France is ___':
-------------------------------------------------------

  Before training (random):
    Paris     : 0.2%
    banana    : 0.3%
    the       : 0.5%
    running   : 0.4%

  After 1% of training:
    Paris     : 5.0% ██
    London    : 4.0% █
    the       : 8.0% ███
    a         : 6.0% ██

  After 50% of training:
    Paris     : 45.0% ██████████████████
    the       : 5.0% ██
    a         : 3.0% █
    Lyon      : 2.0%

  After 100% of training:
    Paris     : 82.0% ████████████████████████████████
    the       : 2.0%
    a         : 1.0%
    Lyon      : 1.0%
```

### What a Base Model Can and Cannot Do

```
+----------------------------------------------------------+
|     Base Model Behavior (After Pre-Training Only)         |
+----------------------------------------------------------+
|                                                            |
|  CAN DO:                                                  |
|    + Complete text naturally                               |
|    + Generate coherent paragraphs                         |
|    + Write code (if it saw code in training)              |
|    + Translate (if it saw parallel text)                  |
|    + Answer questions (sometimes, inconsistently)         |
|                                                            |
|  CANNOT DO WELL:                                          |
|    - Follow specific instructions reliably                |
|    - Have a back-and-forth conversation                   |
|    - Refuse harmful requests                              |
|    - Stay on topic when asked a question                  |
|    - Format output in a requested way                     |
|                                                            |
|  Example of base model behavior:                         |
|    You: "What is the capital of France?"                  |
|    Base model: "What is the capital of Germany?            |
|    What is the capital of Spain? What is the..."          |
|    (It continues the pattern instead of answering!)       |
|                                                            |
+----------------------------------------------------------+
```

---

## Stage 2: Supervised Fine-Tuning (SFT)

### What Is Supervised Fine-Tuning?

**Supervised Fine-Tuning (SFT)** teaches the pre-trained model to follow instructions by showing it thousands of examples of good (prompt, response) pairs.

**Analogy:** Pre-training is like giving someone a library card. SFT is like hiring a tutor to show them how to use that knowledge to answer questions properly.

```
+----------------------------------------------------------+
|         Supervised Fine-Tuning (SFT)                      |
+----------------------------------------------------------+
|                                                            |
|  Training data format:                                    |
|                                                            |
|  Prompt: "Explain photosynthesis in simple terms."        |
|  Response: "Photosynthesis is the process by which        |
|  plants convert sunlight into food. Plants absorb         |
|  light through their leaves and use it to turn            |
|  carbon dioxide and water into glucose and oxygen."       |
|                                                            |
|  Prompt: "Write a Python function to add two numbers."    |
|  Response: "def add(a, b):                                |
|      return a + b"                                        |
|                                                            |
|  Prompt: "Summarize this text: [long text]"               |
|  Response: "[concise summary]"                            |
|                                                            |
|  Thousands of such examples are used.                     |
|  Often created by human annotators or other LLMs.         |
|                                                            |
+----------------------------------------------------------+
```

```python
# Simulating the SFT process

def sft_simulation():
    """
    Show how SFT transforms a base model into an
    instruction-following model.
    """

    # SFT training examples
    sft_data = [
        {
            "prompt": "What is the capital of France?",
            "response": "The capital of France is Paris.",
            "type": "factual question"
        },
        {
            "prompt": "Explain gravity to a 5-year-old.",
            "response": "Gravity is like an invisible force that "
                       "pulls things down. It is why when you throw "
                       "a ball up, it comes back down!",
            "type": "simplified explanation"
        },
        {
            "prompt": "Write a haiku about the ocean.",
            "response": "Waves crash on the shore\n"
                       "Salt and sand beneath my feet\n"
                       "Peace in every breeze",
            "type": "creative writing"
        },
        {
            "prompt": "Convert 100 Fahrenheit to Celsius.",
            "response": "100°F = 37.78°C\n\n"
                       "Formula: (100 - 32) × 5/9 = 37.78",
            "type": "calculation"
        },
    ]

    print("SUPERVISED FINE-TUNING (SFT) SIMULATION")
    print("=" * 60)
    print(f"\nSFT training examples: {len(sft_data)}")
    print("(Real SFT uses 10,000-100,000+ examples)\n")

    for i, example in enumerate(sft_data, 1):
        print(f"  Example {i} ({example['type']}):")
        print(f"    Prompt:   '{example['prompt']}'")
        print(f"    Response: '{example['response'][:60]}...'")
        print()

    # Show the transformation
    print("=" * 60)
    print("\nBehavior Change: Before vs After SFT")
    print("-" * 55)

    comparisons = [
        {
            "input": "What is Python?",
            "before": "What is Java? What is C++? What is...",
            "after":  "Python is a high-level programming language...",
            "note":   "Before: continues the pattern. After: answers the question."
        },
        {
            "input": "List 3 fruits.",
            "before": "List 3 vegetables. List 3 colors. List...",
            "after":  "1. Apple\n2. Banana\n3. Orange",
            "note":   "Before: generates similar prompts. After: follows instructions."
        },
    ]

    for comp in comparisons:
        print(f"\n  Input: '{comp['input']}'")
        print(f"  Before SFT: '{comp['before']}'")
        print(f"  After SFT:  '{comp['after']}'")
        print(f"  Note: {comp['note']}")

sft_simulation()
```

**Output:**
```
SUPERVISED FINE-TUNING (SFT) SIMULATION
============================================================

SFT training examples: 4
(Real SFT uses 10,000-100,000+ examples)

  Example 1 (factual question):
    Prompt:   'What is the capital of France?'
    Response: 'The capital of France is Paris....'

  Example 2 (simplified explanation):
    Prompt:   'Explain gravity to a 5-year-old.'
    Response: 'Gravity is like an invisible force that pulls things dow...'

  Example 3 (creative writing):
    Prompt:   'Write a haiku about the ocean.'
    Response: 'Waves crash on the shore
Salt and sand beneath my fee...'

  Example 4 (calculation):
    Prompt:   'Convert 100 Fahrenheit to Celsius.'
    Response: '100°F = 37.78°C

Formula: (100 - 32) × 5/9 = 37.78...'

============================================================

Behavior Change: Before vs After SFT
-------------------------------------------------------

  Input: 'What is Python?'
  Before SFT: 'What is Java? What is C++? What is...'
  After SFT:  'Python is a high-level programming language...'
  Note: Before: continues the pattern. After: answers the question.

  Input: 'List 3 fruits.'
  Before SFT: 'List 3 vegetables. List 3 colors. List...'
  After SFT:  '1. Apple
2. Banana
3. Orange'
  Note: Before: generates similar prompts. After: follows instructions.
```

---

## Stage 3: Alignment

### Why Alignment Is Needed

After SFT, the model follows instructions, but it might still follow harmful instructions. It might help someone write malware, generate hateful content, or produce dangerous misinformation. Alignment teaches the model to be helpful while being safe.

```
+----------------------------------------------------------+
|     Why We Need Alignment After SFT                       |
+----------------------------------------------------------+
|                                                            |
|  After SFT, the model follows ALL instructions:          |
|                                                            |
|  User: "How do I bake a cake?"                            |
|  Model: "Here are the steps to bake a cake..."  (Good!)  |
|                                                            |
|  User: "How do I pick a lock?"                            |
|  Model: "Here are the steps to pick a lock..."  (Bad!)   |
|                                                            |
|  User: "Write a phishing email."                          |
|  Model: "Subject: Urgent! Click here..."  (Dangerous!)   |
|                                                            |
|  Alignment adds the ability to:                           |
|    + Refuse harmful requests                              |
|    + Explain why something is inappropriate               |
|    + Suggest safe alternatives                            |
|    + Be honest about limitations                          |
|                                                            |
+----------------------------------------------------------+
```

### RLHF: Reinforcement Learning from Human Feedback

**RLHF** is a training technique where humans rank model outputs, and a reward model is trained to predict human preferences. The LLM is then optimized to produce outputs that the reward model scores highly.

```
+----------------------------------------------------------+
|         RLHF: Step by Step                                |
+----------------------------------------------------------+
|                                                            |
|  Step 1: Generate multiple responses                      |
|    Prompt: "Explain quantum computing"                    |
|    Response A: [detailed, accurate explanation]           |
|    Response B: [vague, contains errors]                   |
|    Response C: [too technical, hard to read]              |
|                                                            |
|  Step 2: Humans rank the responses                        |
|    Human says: A > C > B                                  |
|    (A is best, then C, then B)                            |
|                                                            |
|  Step 3: Train a Reward Model                             |
|    Reward Model learns to predict human preferences       |
|    Input: (prompt, response) -> Output: score             |
|    It learns: clear + accurate = high score               |
|                                                            |
|  Step 4: Optimize the LLM using the Reward Model         |
|    LLM generates response                                 |
|    Reward Model scores it                                 |
|    LLM adjusts to get higher scores                      |
|    (Using PPO - Proximal Policy Optimization)             |
|                                                            |
+----------------------------------------------------------+
```

```python
# Simulating the RLHF process

def rlhf_simulation():
    """
    Simulate how RLHF improves model responses.
    """

    print("RLHF SIMULATION")
    print("=" * 60)

    # Step 1: Multiple responses to a prompt
    prompt = "Explain what a black hole is."

    responses = {
        "A": {
            "text": "A black hole is a region in space where gravity "
                    "is so strong that nothing, not even light, can "
                    "escape. They form when massive stars collapse.",
            "qualities": ["Clear", "Accurate", "Concise"]
        },
        "B": {
            "text": "Black holes are these crazy things in space, "
                    "super wild. They suck up everything! Like a "
                    "giant vacuum cleaner in the sky!",
            "qualities": ["Informal", "Inaccurate analogy", "Vague"]
        },
        "C": {
            "text": "A black hole is characterized by a gravitational "
                    "singularity enclosed by an event horizon defined "
                    "by the Schwarzschild radius r_s = 2GM/c^2.",
            "qualities": ["Technical", "Accurate", "Hard to understand"]
        },
    }

    print(f"\nPrompt: '{prompt}'")
    print(f"\nStep 1: Model generates {len(responses)} responses:\n")

    for label, resp in responses.items():
        print(f"  Response {label}: '{resp['text'][:55]}...'")
        print(f"    Qualities: {', '.join(resp['qualities'])}")
        print()

    # Step 2: Human ranking
    print("Step 2: Humans rank the responses:")
    print("  A (clear, accurate) > C (accurate, hard) > B (vague)")
    ranking = {"A": 3, "C": 2, "B": 1}

    # Step 3: Reward model scores
    print("\nStep 3: Reward model learns to score responses:")
    print("-" * 50)

    reward_scores = {"A": 0.92, "B": 0.31, "C": 0.65}
    for label in ["A", "B", "C"]:
        score = reward_scores[label]
        bar = "█" * int(score * 30)
        print(f"  Response {label}: {score:.2f} {bar}")

    # Step 4: LLM optimization
    print("\nStep 4: LLM adjusts to maximize reward scores")
    print("-" * 50)

    improvements = [
        ("Be clear and accessible", "+0.15"),
        ("Be factually accurate",   "+0.20"),
        ("Avoid excessive jargon",  "+0.10"),
        ("Refuse harmful requests", "+0.25"),
    ]

    for behavior, impact in improvements:
        print(f"  Learn: {behavior:30s} Impact: {impact}")

    print("\nResult: Model produces responses more like Response A!")

rlhf_simulation()
```

**Output:**
```
RLHF SIMULATION
============================================================

Prompt: 'Explain what a black hole is.'

Step 1: Model generates 3 responses:

  Response A: 'A black hole is a region in space where gravity is so...'
    Qualities: Clear, Accurate, Concise

  Response B: 'Black holes are these crazy things in space, super wi...'
    Qualities: Informal, Inaccurate analogy, Vague

  Response C: 'A black hole is characterized by a gravitational sin...'
    Qualities: Technical, Accurate, Hard to understand

Step 2: Humans rank the responses:
  A (clear, accurate) > C (accurate, hard) > B (vague)

Step 3: Reward model learns to score responses:
--------------------------------------------------
  Response A: 0.92 ███████████████████████████
  Response B: 0.31 █████████
  Response C: 0.65 ███████████████████

Step 4: LLM adjusts to maximize reward scores
--------------------------------------------------
  Learn: Be clear and accessible        Impact: +0.15
  Learn: Be factually accurate           Impact: +0.20
  Learn: Avoid excessive jargon          Impact: +0.10
  Learn: Refuse harmful requests         Impact: +0.25

Result: Model produces responses more like Response A!
```

### The RLHF Pipeline Diagram

```
+------------------------------------------------------------------+
|                    RLHF Pipeline                                  |
+------------------------------------------------------------------+
|                                                                    |
|  ┌─────────────┐     ┌──────────────┐     ┌─────────────────┐    |
|  │   SFT Model │────>│ Generate     │────>│ Human Rankers   │    |
|  │  (from      │     │ multiple     │     │ rank responses  │    |
|  │   Stage 2)  │     │ responses    │     │ A > B > C       │    |
|  └─────────────┘     └──────────────┘     └────────┬────────┘    |
|                                                      │             |
|                                                      ▼             |
|                                            ┌─────────────────┐    |
|                                            │  Train Reward   │    |
|                                            │  Model (RM)     │    |
|                                            │  Learns human   │    |
|                                            │  preferences    │    |
|                                            └────────┬────────┘    |
|                                                      │             |
|                                                      ▼             |
|  ┌─────────────┐     ┌──────────────┐     ┌─────────────────┐    |
|  │  Aligned    │<────│ PPO Training │<────│ Reward Model    │    |
|  │  Model      │     │ (optimize    │     │ scores new      │    |
|  │  (Final!)   │     │  LLM policy) │     │ LLM outputs     │    |
|  └─────────────┘     └──────────────┘     └─────────────────┘    |
|                                                                    |
+------------------------------------------------------------------+
```

---

## DPO: A Simpler Alternative to RLHF

**Direct Preference Optimization (DPO)** achieves similar results to RLHF but without needing to train a separate reward model. It directly optimizes the LLM using human preference data.

```
+----------------------------------------------------------+
|         RLHF vs DPO Comparison                            |
+----------------------------------------------------------+
|                                                            |
|  RLHF (Complex, 3 models):                               |
|    1. SFT Model (starting point)                         |
|    2. Reward Model (learns preferences)                   |
|    3. PPO-trained Model (optimized with RM)              |
|    Pro: Well-established, proven at scale                 |
|    Con: Complex, unstable training, expensive             |
|                                                            |
|  DPO (Simpler, 1 model):                                 |
|    1. SFT Model (starting point)                         |
|    2. Directly optimize using preference pairs            |
|    No reward model needed!                                |
|    Pro: Simpler, more stable, cheaper                     |
|    Con: Newer, less proven at large scale                 |
|                                                            |
+----------------------------------------------------------+
```

```python
# Demonstrating DPO vs RLHF conceptually

def dpo_vs_rlhf():
    """
    Show the difference between RLHF and DPO approaches.
    """

    print("DPO vs RLHF: Training Approach Comparison")
    print("=" * 60)

    # Preference data (same for both methods)
    preferences = [
        {
            "prompt": "Is it okay to lie to my friend?",
            "chosen": "It is generally better to be honest with friends. "
                     "Lying can damage trust and harm relationships.",
            "rejected": "Sure, sometimes lying is fine. Here are some "
                       "good lies you could tell...",
        },
        {
            "prompt": "How do I lose weight?",
            "chosen": "Safe weight loss involves balanced nutrition and "
                     "regular exercise. Consult a doctor for personalized advice.",
            "rejected": "Just stop eating! Extreme fasting is the fastest "
                       "way to lose weight.",
        },
    ]

    print("\nPreference Data (used by both methods):")
    print("-" * 55)
    for i, pref in enumerate(preferences, 1):
        print(f"\n  Pair {i}:")
        print(f"    Prompt:   '{pref['prompt']}'")
        print(f"    Chosen:   '{pref['chosen'][:50]}...'")
        print(f"    Rejected: '{pref['rejected'][:50]}...'")

    # RLHF approach
    print("\n\nRLHF Approach:")
    print("-" * 55)
    rlhf_steps = [
        "1. Train a Reward Model on preference data",
        "2. Reward Model scores: chosen=0.9, rejected=0.2",
        "3. Use PPO to optimize LLM to get high reward scores",
        "4. Balance: high reward vs staying close to SFT model",
        "5. Iterate for thousands of steps",
    ]
    for step in rlhf_steps:
        print(f"  {step}")

    # DPO approach
    print("\nDPO Approach:")
    print("-" * 55)
    dpo_steps = [
        "1. Take preference pairs directly",
        "2. Increase probability of chosen response",
        "3. Decrease probability of rejected response",
        "4. No reward model needed!",
        "5. Single training stage, much simpler",
    ]
    for step in dpo_steps:
        print(f"  {step}")

    # Summary comparison
    print("\n\nSummary:")
    print("-" * 55)
    comparisons = [
        ("Models needed",  "3 (SFT + RM + Policy)", "1 (SFT + DPO)"),
        ("Complexity",     "High",                    "Low"),
        ("Training cost",  "$$$",                     "$$"),
        ("Stability",      "Can be unstable",        "More stable"),
        ("Track record",   "Proven (GPT-4, etc.)",   "Newer but growing"),
    ]

    print(f"  {'Aspect':<20} {'RLHF':<25} {'DPO':<25}")
    for aspect, rlhf, dpo in comparisons:
        print(f"  {aspect:<20} {rlhf:<25} {dpo:<25}")

dpo_vs_rlhf()
```

**Output:**
```
DPO vs RLHF: Training Approach Comparison
============================================================

Preference Data (used by both methods):
-------------------------------------------------------

  Pair 1:
    Prompt:   'Is it okay to lie to my friend?'
    Chosen:   'It is generally better to be honest with frien...'
    Rejected: 'Sure, sometimes lying is fine. Here are some g...'

  Pair 2:
    Prompt:   'How do I lose weight?'
    Chosen:   'Safe weight loss involves balanced nutrition an...'
    Rejected: 'Just stop eating! Extreme fasting is the faste...'


RLHF Approach:
-------------------------------------------------------
  1. Train a Reward Model on preference data
  2. Reward Model scores: chosen=0.9, rejected=0.2
  3. Use PPO to optimize LLM to get high reward scores
  4. Balance: high reward vs staying close to SFT model
  5. Iterate for thousands of steps

DPO Approach:
-------------------------------------------------------
  1. Take preference pairs directly
  2. Increase probability of chosen response
  3. Decrease probability of rejected response
  4. No reward model needed!
  5. Single training stage, much simpler


Summary:
-------------------------------------------------------
  Aspect               RLHF                      DPO
  Models needed        3 (SFT + RM + Policy)     1 (SFT + DPO)
  Complexity           High                       Low
  Training cost        $$$                        $$
  Stability            Can be unstable            More stable
  Track record         Proven (GPT-4, etc.)       Newer but growing
```

---

## The Complete Pipeline Visualized

```python
# Complete training pipeline summary

def complete_pipeline():
    """
    Summarize the entire training pipeline from raw text
    to aligned model.
    """

    print("THE COMPLETE LLM TRAINING PIPELINE")
    print("=" * 60)

    stages = [
        {
            "name": "Stage 1: Pre-Training",
            "input": "Trillions of tokens (web, books, code)",
            "process": "Next-token prediction on massive text",
            "output": "Base model (good at text, bad at conversation)",
            "cost": "~$10M - $100M+",
            "time": "Weeks to months",
            "data_size": "1-15 trillion tokens",
            "result_behavior": [
                "Completes text naturally",
                "Has broad knowledge",
                "Does NOT follow instructions",
                "May generate harmful content",
            ]
        },
        {
            "name": "Stage 2: Supervised Fine-Tuning (SFT)",
            "input": "10K-100K+ (prompt, response) pairs",
            "process": "Train on instruction-response examples",
            "output": "Instruction-tuned model (follows instructions)",
            "cost": "~$1K - $100K",
            "time": "Hours to days",
            "data_size": "10K-100K examples",
            "result_behavior": [
                "Follows instructions",
                "Answers questions directly",
                "Formats output as requested",
                "Still may follow harmful instructions",
            ]
        },
        {
            "name": "Stage 3: Alignment (RLHF/DPO)",
            "input": "Human preference rankings",
            "process": "Optimize for human preferences",
            "output": "Aligned model (helpful, harmless, honest)",
            "cost": "~$10K - $500K",
            "time": "Days to weeks",
            "data_size": "100K+ comparisons",
            "result_behavior": [
                "Helpful and informative",
                "Refuses harmful requests",
                "Honest about limitations",
                "Balanced and safe responses",
            ]
        },
    ]

    for stage in stages:
        print(f"\n{'─' * 55}")
        print(f"  {stage['name']}")
        print(f"{'─' * 55}")
        print(f"  Input:     {stage['input']}")
        print(f"  Process:   {stage['process']}")
        print(f"  Output:    {stage['output']}")
        print(f"  Cost:      {stage['cost']}")
        print(f"  Time:      {stage['time']}")
        print(f"  Data size: {stage['data_size']}")
        print(f"  Resulting behavior:")
        for behavior in stage['result_behavior']:
            print(f"    {'✓' if 'NOT' not in behavior and 'may' not in behavior else '!'} {behavior}")

    print(f"\n{'=' * 60}")
    print("Each stage builds on the previous one.")
    print("Skip a stage and the model will be missing key capabilities.")

complete_pipeline()
```

**Output:**
```
THE COMPLETE LLM TRAINING PIPELINE
============================================================

───────────────────────────────────────────────────────
  Stage 1: Pre-Training
───────────────────────────────────────────────────────
  Input:     Trillions of tokens (web, books, code)
  Process:   Next-token prediction on massive text
  Output:    Base model (good at text, bad at conversation)
  Cost:      ~$10M - $100M+
  Time:      Weeks to months
  Data size: 1-15 trillion tokens
  Resulting behavior:
    ✓ Completes text naturally
    ✓ Has broad knowledge
    ! Does NOT follow instructions
    ! May generate harmful content

───────────────────────────────────────────────────────
  Stage 2: Supervised Fine-Tuning (SFT)
───────────────────────────────────────────────────────
  Input:     10K-100K+ (prompt, response) pairs
  Process:   Train on instruction-response examples
  Output:    Instruction-tuned model (follows instructions)
  Cost:      ~$1K - $100K
  Time:      Hours to days
  Data size: 10K-100K examples
  Resulting behavior:
    ✓ Follows instructions
    ✓ Answers questions directly
    ✓ Formats output as requested
    ! Still may follow harmful instructions

───────────────────────────────────────────────────────
  Stage 3: Alignment (RLHF/DPO)
───────────────────────────────────────────────────────
  Input:     Human preference rankings
  Process:   Optimize for human preferences
  Output:    Aligned model (helpful, harmless, honest)
  Cost:      ~$10K - $500K
  Time:      Days to weeks
  Data size: 100K+ comparisons
  Resulting behavior:
    ✓ Helpful and informative
    ✓ Refuses harmful requests
    ✓ Honest about limitations
    ✓ Balanced and safe responses

============================================================
Each stage builds on the previous one.
Skip a stage and the model will be missing key capabilities.
```

---

## Common Mistakes

| Mistake | Why It Is Wrong | What to Do Instead |
|---------|----------------|-------------------|
| Thinking pre-training alone creates a chatbot | Pre-trained models complete text, not have conversations | Understand that SFT and alignment are needed for chat |
| Confusing SFT with pre-training | SFT uses thousands of examples; pre-training uses trillions of tokens | Recognize that SFT is a much smaller, targeted training phase |
| Thinking alignment makes models perfect | Alignment reduces but does not eliminate harmful outputs | Always implement additional safety checks in your application |
| Believing RLHF is the only alignment method | DPO and other techniques can achieve similar results | Evaluate both RLHF and DPO for your use case |
| Assuming more training data is always better | Low-quality data can make models worse | Focus on data quality over quantity for SFT and alignment |

---

## Best Practices

1. **Start with a pre-trained model if possible.** Pre-training from scratch costs millions. Use existing base models and fine-tune them for your needs.

2. **Invest in high-quality SFT data.** The quality of your instruction-response pairs directly determines how well the model follows instructions. A small dataset of excellent examples beats a large dataset of mediocre ones.

3. **Consider DPO for alignment.** If you are doing alignment on a smaller scale, DPO is simpler to implement and more stable than full RLHF.

4. **Always add safety layers beyond alignment.** Alignment is not foolproof. Add input filtering, output checking, and content moderation in your application.

5. **Understand which stage affects which behavior.** If the model lacks knowledge, that is a pre-training issue. If it does not follow instructions, that is SFT. If it generates harmful content, that is alignment.

---

## Quick Summary

The LLM training pipeline has three stages. Pre-training exposes the model to trillions of tokens of text, teaching it language patterns and world knowledge. Supervised fine-tuning (SFT) shows the model thousands of instruction-response examples, teaching it to follow instructions and have conversations. Alignment (via RLHF or DPO) uses human preference data to make the model helpful, harmless, and honest. RLHF trains a separate reward model and uses PPO optimization, while DPO directly optimizes using preference pairs without a reward model. Each stage builds on the previous one, and all three are needed for a safe, capable assistant.

---

## Key Points

- Pre-training teaches language patterns from trillions of tokens but does not produce a conversational model
- A base (pre-trained only) model completes text rather than answering questions
- SFT uses curated (prompt, response) pairs to teach instruction following
- RLHF uses human rankings to train a reward model, then optimizes the LLM against it
- DPO skips the reward model and directly optimizes using preference pairs, making it simpler and more stable
- Each training stage costs significantly less than the previous one
- Alignment reduces but does not eliminate harmful outputs
- Data quality matters more than data quantity for SFT and alignment

---

## Practice Questions

1. Explain why a pre-trained base model responds to "What is Python?" by generating more questions instead of answering. What training stage fixes this behavior?

2. In RLHF, what is the role of the reward model? Why is it needed as an intermediate step?

3. Compare RLHF and DPO in terms of complexity, cost, and stability. When might you choose one over the other?

4. A company has a pre-trained model that follows instructions well but sometimes generates biased content. Which training stage should they focus on next, and what data would they need?

5. Why do companies spend millions on pre-training but only thousands on SFT? What does this tell you about the relationship between data scale and model capability?

---

## Exercises

### Exercise 1: Design SFT Data

Create 10 high-quality (prompt, response) pairs that you would use to fine-tune a model for customer support. Include:
- Different types of customer queries (billing, technical, general)
- Proper tone (professional, empathetic)
- Appropriate length responses

### Exercise 2: Preference Ranking

For each prompt below, write two responses (one good, one bad) and explain which you would rank higher and why:
- "How do I improve my resume?"
- "What should I eat for breakfast?"
- "Explain blockchain to me."

### Exercise 3: Pipeline Diagram

Draw your own diagram of the complete training pipeline. Include:
- Data inputs at each stage
- Outputs at each stage
- Approximate costs and timescales
- What behavior each stage teaches

---

## What Is Next?

Now that you understand how LLMs are trained, the next chapter brings things to your local machine. In "Running LLMs Locally", you will learn how to set up Ollama, run models with llama.cpp, understand hardware requirements for different model sizes, and use quantization to run large models on consumer hardware. You will go from theory to practice, running an LLM on your own computer.
