# Chapter 3: Key Models

## What You Will Learn

In this chapter, you will learn:

- The major LLM families available today: GPT, Claude, Gemini, Llama, and Mistral
- The key differences between these models in terms of capabilities, pricing, and use cases
- What open-source vs closed-source means for LLMs and why it matters
- How to read a model comparison table and understand what the numbers mean
- When to choose one model over another for different tasks

## Why This Chapter Matters

There are dozens of large language models available today. Choosing the wrong one can cost you money, give you poor results, or lock you into a vendor. Choosing the right one can save you time, produce better output, and give you flexibility.

This chapter is your field guide. Just as a carpenter needs to know the difference between a hammer and a wrench, an AI practitioner needs to know the difference between GPT-4 and Llama 3. Each model has strengths, weaknesses, and ideal use cases.

By the end of this chapter, you will be able to look at any task and say, "For this, I should use this model, and here is why."

---

## The LLM Landscape

```
+------------------------------------------------------------------+
|                   Major LLM Families (2024-2025)                  |
+------------------------------------------------------------------+
|                                                                    |
|  CLOSED SOURCE (API access only):                                 |
|  ┌────────────────────────────────────────────────────────┐       |
|  │  OpenAI GPT Series    - GPT-4o, GPT-4 Turbo, o1       │       |
|  │  Anthropic Claude     - Claude 3.5 Sonnet, Claude 3 Opus│      |
|  │  Google Gemini        - Gemini 1.5 Pro, Gemini Ultra    │       |
|  └────────────────────────────────────────────────────────┘       |
|                                                                    |
|  OPEN SOURCE / OPEN WEIGHTS (downloadable):                       |
|  ┌────────────────────────────────────────────────────────┐       |
|  │  Meta Llama           - Llama 3 8B, 70B, 405B          │       |
|  │  Mistral AI           - Mistral 7B, Mixtral, Mistral Large│    |
|  │  Others               - Qwen, Phi, Gemma, DeepSeek     │       |
|  └────────────────────────────────────────────────────────┘       |
|                                                                    |
+------------------------------------------------------------------+
```

---

## OpenAI GPT Series

### What Is GPT?

**GPT** stands for Generative Pre-trained Transformer. It is a family of LLMs created by OpenAI, the company that launched ChatGPT and brought LLMs into mainstream awareness.

**Analogy:** If the LLM world were the automobile industry, GPT-4 would be like the first widely successful electric car. It was not the first LLM, but it was the one that showed the world what was possible.

### Key GPT Models

```
+----------------------------------------------------------+
|              GPT Model Timeline                           |
+----------------------------------------------------------+
|                                                            |
|  GPT-2 (2019)    | 1.5B params  | Text generation        |
|  GPT-3 (2020)    | 175B params  | Few-shot learning      |
|  GPT-3.5 (2022)  | ~175B params | ChatGPT launched       |
|  GPT-4 (2023)    | ~1.8T params | Multimodal, reasoning  |
|  GPT-4o (2024)   | Optimized    | Faster, cheaper GPT-4  |
|  o1 (2024)       | Reasoning    | Chain-of-thought built in|
|  o3 (2025)       | Advanced     | Enhanced reasoning     |
|                                                            |
+----------------------------------------------------------+
```

### GPT Strengths and Weaknesses

```python
# GPT model characteristics

gpt_profile = {
    "name": "OpenAI GPT-4o",
    "company": "OpenAI",
    "type": "Closed source (API only)",
    "strengths": [
        "Excellent at code generation",
        "Strong general knowledge",
        "Good at following complex instructions",
        "Large ecosystem of tools and integrations",
        "Multimodal (text + images)",
    ],
    "weaknesses": [
        "No access to model weights",
        "Can be expensive at scale",
        "Training data cutoff limits knowledge",
        "Occasional hallucinations on niche topics",
    ],
    "best_for": [
        "Code generation and debugging",
        "General-purpose chat applications",
        "Content creation",
        "Data analysis with Code Interpreter",
    ],
    "pricing_note": "Pay per token via API, or subscription via ChatGPT"
}

print(f"Model: {gpt_profile['name']}")
print(f"Company: {gpt_profile['company']}")
print(f"Type: {gpt_profile['type']}")
print()

print("Strengths:")
for s in gpt_profile['strengths']:
    print(f"  + {s}")

print("\nWeaknesses:")
for w in gpt_profile['weaknesses']:
    print(f"  - {w}")

print("\nBest for:")
for b in gpt_profile['best_for']:
    print(f"  * {b}")

print(f"\nPricing: {gpt_profile['pricing_note']}")
```

**Output:**
```
Model: OpenAI GPT-4o
Company: OpenAI
Type: Closed source (API only)

Strengths:
  + Excellent at code generation
  + Strong general knowledge
  + Good at following complex instructions
  + Large ecosystem of tools and integrations
  + Multimodal (text + images)

Weaknesses:
  - No access to model weights
  - Can be expensive at scale
  - Training data cutoff limits knowledge
  - Occasional hallucinations on niche topics

Best for:
  * Code generation and debugging
  * General-purpose chat applications
  * Content creation
  * Data analysis with Code Interpreter

Pricing: Pay per token via API, or subscription via ChatGPT
```

---

## Anthropic Claude

### What Is Claude?

Claude is a family of LLMs created by Anthropic, a company founded by former OpenAI researchers. Claude is designed with a strong emphasis on safety, helpfulness, and honesty.

**Analogy:** If GPT is the adventurous all-rounder, Claude is the careful, thoughtful expert. It tends to be more cautious about harmful content and more transparent about its limitations.

### Key Claude Models

```
+----------------------------------------------------------+
|              Claude Model Timeline                        |
+----------------------------------------------------------+
|                                                            |
|  Claude 1 (2023)        | Early release                  |
|  Claude 2 (2023)        | 100K context window            |
|  Claude 3 Haiku (2024)  | Small, fast, cheap             |
|  Claude 3 Sonnet (2024) | Balanced performance           |
|  Claude 3 Opus (2024)   | Most capable                   |
|  Claude 3.5 Sonnet (2024)| Best balance of speed/quality |
|  Claude 3.5 Haiku (2024) | Fast and improved             |
|                                                            |
+----------------------------------------------------------+
```

### Claude Strengths and Weaknesses

```python
# Claude model characteristics

claude_profile = {
    "name": "Anthropic Claude 3.5 Sonnet",
    "company": "Anthropic",
    "type": "Closed source (API only)",
    "strengths": [
        "Very long context window (200K tokens)",
        "Excellent at analysis and writing",
        "Strong safety alignment",
        "Good at following nuanced instructions",
        "Transparent about uncertainty",
        "Strong coding capabilities",
    ],
    "weaknesses": [
        "No access to model weights",
        "Smaller ecosystem than GPT",
        "Sometimes overly cautious (refuses safe requests)",
        "No built-in web browsing or code execution",
    ],
    "best_for": [
        "Long document analysis and summarization",
        "Nuanced writing tasks",
        "Tasks requiring careful reasoning",
        "Code review and generation",
        "Applications needing strong safety guardrails",
    ],
    "context_window": "200,000 tokens (~150,000 words)"
}

print(f"Model: {claude_profile['name']}")
print(f"Company: {claude_profile['company']}")
print(f"Context Window: {claude_profile['context_window']}")
print()

print("Strengths:")
for s in claude_profile['strengths']:
    print(f"  + {s}")

print("\nWeaknesses:")
for w in claude_profile['weaknesses']:
    print(f"  - {w}")

print("\nBest for:")
for b in claude_profile['best_for']:
    print(f"  * {b}")
```

**Output:**
```
Model: Anthropic Claude 3.5 Sonnet
Company: Anthropic
Context Window: 200,000 tokens (~150,000 words)

Strengths:
  + Very long context window (200K tokens)
  + Excellent at analysis and writing
  + Strong safety alignment
  + Good at following nuanced instructions
  + Transparent about uncertainty
  + Strong coding capabilities

Weaknesses:
  - No access to model weights
  - Smaller ecosystem than GPT
  - Sometimes overly cautious (refuses safe requests)
  - No built-in web browsing or code execution

Best for:
  * Long document analysis and summarization
  * Nuanced writing tasks
  * Tasks requiring careful reasoning
  * Code review and generation
  * Applications needing strong safety guardrails
```

---

## Google Gemini

### What Is Gemini?

Gemini is Google's family of LLMs, designed to be natively multimodal, meaning they can process text, images, audio, and video from the ground up, not as an afterthought.

### Key Gemini Models

```
+----------------------------------------------------------+
|              Gemini Model Lineup                          |
+----------------------------------------------------------+
|                                                            |
|  Gemini Nano      | On-device (phones)                    |
|  Gemini Flash     | Fast, lightweight                     |
|  Gemini Pro       | Balanced performance                  |
|  Gemini Ultra     | Most capable                          |
|  Gemini 1.5 Pro   | 1M token context window!              |
|                                                            |
+----------------------------------------------------------+
```

```python
# Gemini model characteristics

gemini_profile = {
    "name": "Google Gemini 1.5 Pro",
    "company": "Google DeepMind",
    "type": "Closed source (API via Google AI Studio / Vertex AI)",
    "strengths": [
        "Massive context window (1M tokens = ~700K words)",
        "Natively multimodal (text, images, audio, video)",
        "Strong integration with Google ecosystem",
        "Competitive reasoning capabilities",
        "Multiple size variants for different needs",
    ],
    "weaknesses": [
        "API can be complex to set up",
        "Less mature third-party ecosystem",
        "Availability varies by region",
        "Rapid model changes can break workflows",
    ],
    "best_for": [
        "Processing very long documents or codebases",
        "Multimodal tasks (analyzing images and video)",
        "Google Workspace integrations",
        "Applications needing massive context",
    ],
    "standout_feature": "1,000,000 token context window"
}

print(f"Model: {gemini_profile['name']}")
print(f"Company: {gemini_profile['company']}")
print(f"Standout: {gemini_profile['standout_feature']}")
print()

# Context window comparison
print("Context Window Comparison:")
print("=" * 50)
windows = [
    ("GPT-4 Turbo",    128_000),
    ("Claude 3.5",     200_000),
    ("Gemini 1.5 Pro", 1_000_000),
]

max_window = max(w for _, w in windows)
for name, size in windows:
    bar_length = int((size / max_window) * 40)
    bar = "█" * bar_length
    print(f"  {name:18s}: {size:>10,} tokens {bar}")
```

**Output:**
```
Model: Google Gemini 1.5 Pro
Company: Google DeepMind
Standout: 1,000,000 token context window

Context Window Comparison:
==================================================
  GPT-4 Turbo       :    128,000 tokens █████
  Claude 3.5        :    200,000 tokens ████████
  Gemini 1.5 Pro    :  1,000,000 tokens ████████████████████████████████████████
```

---

## Meta Llama

### What Is Llama?

**Llama** (Large Language Model Meta AI) is Meta's family of open-weight LLMs. "Open weights" means you can download the model and run it on your own hardware.

**Analogy:** If closed-source models are like renting a car (you use it but do not own it), Llama is like buying a car. You own it, can modify it, and do not pay per mile.

### Key Llama Models

```
+----------------------------------------------------------+
|              Llama Model Progression                      |
+----------------------------------------------------------+
|                                                            |
|  Llama 1 (2023)    | 7B, 13B, 33B, 65B  | Research only  |
|  Llama 2 (2023)    | 7B, 13B, 70B       | Commercial use  |
|  Llama 3 (2024)    | 8B, 70B            | Much improved   |
|  Llama 3.1 (2024)  | 8B, 70B, 405B      | Largest open    |
|  Llama 3.2 (2024)  | 1B, 3B, 11B, 90B   | Multimodal      |
|                                                            |
|  B = Billion parameters                                   |
|  405B = 405 billion parameters                            |
|                                                            |
+----------------------------------------------------------+
```

```python
# Llama model characteristics

llama_profile = {
    "name": "Meta Llama 3.1",
    "company": "Meta (Facebook)",
    "type": "Open weights (downloadable, free to use)",
    "sizes": ["8B", "70B", "405B"],
    "strengths": [
        "Free to download and use",
        "Can run on your own hardware",
        "Full control over the model",
        "Active open-source community",
        "No per-token API costs",
        "Can be fine-tuned for specific tasks",
        "Privacy: your data never leaves your servers",
    ],
    "weaknesses": [
        "Requires powerful hardware (especially 70B and 405B)",
        "You manage infrastructure yourself",
        "No built-in safety features (you must add your own)",
        "Smaller models less capable than top closed models",
    ],
    "best_for": [
        "Privacy-sensitive applications",
        "Custom fine-tuning for specific domains",
        "Cost-effective high-volume usage",
        "Research and experimentation",
        "On-premise deployments",
    ],
}

print(f"Model: {llama_profile['name']}")
print(f"Company: {llama_profile['company']}")
print(f"Type: {llama_profile['type']}")
print(f"Available sizes: {', '.join(llama_profile['sizes'])}")
print()

# Show hardware requirements for each size
print("Hardware Requirements by Size:")
print("-" * 50)
requirements = [
    ("8B",   "16 GB RAM",    "Consumer GPU (RTX 3090)"),
    ("70B",  "140 GB RAM",   "Multiple GPUs or quantized"),
    ("405B", "800+ GB RAM",  "Server cluster required"),
]

for size, ram, hardware in requirements:
    print(f"  Llama 3 {size:4s}: {ram:15s} | {hardware}")
```

**Output:**
```
Model: Meta Llama 3.1
Company: Meta (Facebook)
Type: Open weights (downloadable, free to use)
Available sizes: 8B, 70B, 405B

Hardware Requirements by Size:
--------------------------------------------------
  Llama 3 8B  : 16 GB RAM       | Consumer GPU (RTX 3090)
  Llama 3 70B : 140 GB RAM      | Multiple GPUs or quantized
  Llama 3 405B: 800+ GB RAM     | Server cluster required
```

---

## Mistral AI

### What Is Mistral?

Mistral AI is a French AI company that has rapidly become known for producing highly efficient models that punch above their weight class.

**Analogy:** If LLMs were athletes, Mistral models would be the lightweight boxer who knocks out heavyweights. Their smaller models often match or beat much larger competitors.

### Key Mistral Models

```
+----------------------------------------------------------+
|              Mistral Model Lineup                         |
+----------------------------------------------------------+
|                                                            |
|  Mistral 7B (2023)      | 7B params    | Open weights   |
|  Mixtral 8x7B (2024)    | 46B params   | Mixture of     |
|                          | (12B active) | Experts (MoE)  |
|  Mistral Small (2024)   | ~22B params  | API only       |
|  Mistral Medium (2024)  | ~70B params  | API only       |
|  Mistral Large (2024)   | ~120B params | API only       |
|                                                            |
+----------------------------------------------------------+
```

### What Is Mixture of Experts (MoE)?

Mixtral uses a technique called **Mixture of Experts (MoE)**. Instead of using all parameters for every token, it activates only a subset of "expert" sub-networks.

```
+----------------------------------------------------------+
|         Mixture of Experts (MoE) Explained                |
+----------------------------------------------------------+
|                                                            |
|  Traditional model (dense):                               |
|    Every token uses ALL 70B parameters                    |
|    Slow but thorough                                      |
|                                                            |
|  MoE model (Mixtral 8x7B):                               |
|    Has 8 "expert" sub-networks of 7B each                |
|    For each token, a router picks 2 experts               |
|    Only 12B parameters are active per token               |
|    Fast like a 12B model, smart like a 46B model          |
|                                                            |
|  ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐                  |
|  │Exp 1│   │Exp 2│   │Exp 3│   │Exp 4│                   |
|  └──┬──┘   └──┬──┘   └──┬──┘   └──┬──┘                   |
|     │         │         │         │                        |
|  ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐                  |
|  │Exp 5│   │Exp 6│   │Exp 7│   │Exp 8│                   |
|  └──┬──┘   └──┬──┘   └──┬──┘   └──┬──┘                   |
|     │         │         │         │                        |
|     └─────────┴────┬────┴─────────┘                       |
|                    │                                       |
|              ┌─────┴─────┐                                 |
|              │  Router   │  Picks 2 experts per token     |
|              └───────────┘                                 |
|                                                            |
+----------------------------------------------------------+
```

```python
# Demonstrating the MoE concept

def moe_demo():
    """Show how Mixture of Experts works."""

    experts = {
        "Expert 1": "Mathematics and logic",
        "Expert 2": "Code and programming",
        "Expert 3": "Creative writing",
        "Expert 4": "Science and facts",
        "Expert 5": "Languages and translation",
        "Expert 6": "Conversation and chat",
        "Expert 7": "Analysis and reasoning",
        "Expert 8": "Instructions and tasks",
    }

    # Simulated routing for different inputs
    routing = {
        "Write a Python function": ["Expert 2", "Expert 7"],
        "Translate to French":     ["Expert 5", "Expert 6"],
        "What is gravity?":        ["Expert 4", "Expert 7"],
        "Write a poem about cats": ["Expert 3", "Expert 6"],
    }

    print("Mixture of Experts (MoE) Routing")
    print("=" * 55)
    print(f"\nTotal experts: {len(experts)}")
    print(f"Experts used per token: 2 (out of 8)")
    print(f"Total parameters: 8 x 7B = 56B")
    print(f"Active parameters: 2 x 7B = 14B per token")
    print()

    for prompt, selected in routing.items():
        print(f"  Input: '{prompt}'")
        print(f"  Router selects:")
        for exp in selected:
            print(f"    -> {exp}: {experts[exp]}")
        print()

    print("Benefit: Speed of a 14B model, knowledge of a 56B model!")

moe_demo()
```

**Output:**
```
Mixture of Experts (MoE) Routing
=======================================================

Total experts: 8
Experts used per token: 2 (out of 8)
Total parameters: 8 x 7B = 56B
Active parameters: 2 x 7B = 14B per token

  Input: 'Write a Python function'
  Router selects:
    -> Expert 2: Code and programming
    -> Expert 7: Analysis and reasoning

  Input: 'Translate to French'
  Router selects:
    -> Expert 5: Languages and translation
    -> Expert 6: Conversation and chat

  Input: 'What is gravity?'
  Router selects:
    -> Expert 4: Science and facts
    -> Expert 7: Analysis and reasoning

  Input: 'Write a poem about cats'
  Router selects:
    -> Expert 3: Creative writing
    -> Expert 6: Conversation and chat

Benefit: Speed of a 14B model, knowledge of a 56B model!
```

---

## Open Source vs Closed Source

This is one of the most important distinctions in the LLM world.

```
+------------------------------------------------------------------+
|           Open Source vs Closed Source LLMs                        |
+------------------------------------------------------------------+
|                                                                    |
|  CLOSED SOURCE              |  OPEN SOURCE / OPEN WEIGHTS        |
|  (GPT-4, Claude, Gemini)    |  (Llama, Mistral, Qwen)            |
|  ─────────────────────────  |  ──────────────────────────         |
|  Access via API only        |  Download and run locally           |
|  Pay per token              |  Free (you pay for hardware)       |
|  Cannot see model weights   |  Full access to weights            |
|  Cannot fine-tune (usually) |  Can fine-tune freely              |
|  Data goes to provider      |  Data stays on your servers        |
|  Provider handles updates   |  You manage updates                |
|  Usually more capable       |  Catching up rapidly               |
|  Built-in safety features   |  You add safety yourself           |
|  Easy to start              |  More setup required               |
|                                                                    |
+------------------------------------------------------------------+
```

```python
# Decision helper: Open source vs Closed source

def recommend_model_type(requirements):
    """
    Help decide between open and closed source based on needs.
    """
    scores = {"open_source": 0, "closed_source": 0}
    reasons = {"open_source": [], "closed_source": []}

    checks = {
        "data_privacy": {
            True:  ("open_source",  "Data stays on your servers"),
            False: ("closed_source", "Provider handles security"),
        },
        "budget_limited": {
            True:  ("open_source",  "No per-token API costs"),
            False: ("closed_source", "Pay for quality, not hardware"),
        },
        "need_fine_tuning": {
            True:  ("open_source",  "Full control over model weights"),
            False: ("closed_source", "Works well out of the box"),
        },
        "high_volume": {
            True:  ("open_source",  "Fixed hardware cost vs per-token"),
            False: ("closed_source", "Pay only for what you use"),
        },
        "maximum_quality": {
            True:  ("closed_source", "Top closed models still lead"),
            False: ("open_source",  "Open models are good enough"),
        },
        "easy_setup": {
            True:  ("closed_source", "API key and you are done"),
            False: ("open_source",  "More setup but more control"),
        },
    }

    print("Model Type Recommendation")
    print("=" * 55)
    print()

    for requirement, value in requirements.items():
        if requirement in checks:
            choice, reason = checks[requirement][value]
            scores[choice] += 1
            reasons[choice].append(reason)
            status = "Yes" if value else "No"
            print(f"  {requirement:20s}: {status:4s} -> {choice}")

    print()
    print("Scores:")
    print(f"  Open Source:   {scores['open_source']}")
    print(f"  Closed Source: {scores['closed_source']}")

    winner = max(scores, key=scores.get)
    print(f"\nRecommendation: {winner.replace('_', ' ').title()}")
    print(f"\nReasons:")
    for r in reasons[winner]:
        print(f"  + {r}")

# Example: A healthcare startup
recommend_model_type({
    "data_privacy": True,
    "budget_limited": True,
    "need_fine_tuning": True,
    "high_volume": True,
    "maximum_quality": False,
    "easy_setup": False,
})
```

**Output:**
```
Model Type Recommendation
=======================================================

  data_privacy        : Yes  -> open_source
  budget_limited      : Yes  -> open_source
  need_fine_tuning    : Yes  -> open_source
  high_volume         : Yes  -> open_source
  maximum_quality     : No   -> open_source
  easy_setup          : No   -> open_source

Scores:
  Open Source:   6
  Closed Source: 0

Recommendation: Open Source

Reasons:
  + Data stays on your servers
  + No per-token API costs
  + Full control over model weights
  + Fixed hardware cost vs per-token
  + Open models are good enough
  + More setup but more control
```

---

## Model Comparison Table

```python
# Comprehensive model comparison

models = [
    {
        "name": "GPT-4o",
        "company": "OpenAI",
        "params": "~1.8T (est.)",
        "context": "128K",
        "open": "No",
        "multimodal": "Yes",
        "code": "Excellent",
        "reasoning": "Excellent",
        "speed": "Fast",
        "cost": "$$$",
    },
    {
        "name": "Claude 3.5 Sonnet",
        "company": "Anthropic",
        "params": "Unknown",
        "context": "200K",
        "open": "No",
        "multimodal": "Yes",
        "code": "Excellent",
        "reasoning": "Excellent",
        "speed": "Fast",
        "cost": "$$",
    },
    {
        "name": "Gemini 1.5 Pro",
        "company": "Google",
        "params": "Unknown",
        "context": "1M",
        "open": "No",
        "multimodal": "Yes",
        "code": "Good",
        "reasoning": "Good",
        "speed": "Medium",
        "cost": "$$",
    },
    {
        "name": "Llama 3.1 70B",
        "company": "Meta",
        "params": "70B",
        "context": "128K",
        "open": "Yes",
        "multimodal": "No",
        "code": "Good",
        "reasoning": "Good",
        "speed": "Varies",
        "cost": "Free*",
    },
    {
        "name": "Mixtral 8x7B",
        "company": "Mistral",
        "params": "46B (12B active)",
        "context": "32K",
        "open": "Yes",
        "multimodal": "No",
        "code": "Good",
        "reasoning": "Good",
        "speed": "Fast",
        "cost": "Free*",
    },
]

# Print comparison table
print("Model Comparison Table")
print("=" * 80)
header = (f"{'Model':<20} {'Context':<8} {'Open':<5} "
          f"{'Code':<10} {'Reasoning':<10} {'Cost':<6}")
print(header)
print("-" * 80)

for m in models:
    row = (f"{m['name']:<20} {m['context']:<8} {m['open']:<5} "
           f"{m['code']:<10} {m['reasoning']:<10} {m['cost']:<6}")
    print(row)

print("-" * 80)
print("* Free to download; hardware costs apply")
print()

# When to use which
print("When to Use Which Model:")
print("=" * 55)
use_cases = [
    ("General chat/assistant",   "GPT-4o or Claude 3.5 Sonnet"),
    ("Long document analysis",   "Claude 3.5 (200K) or Gemini 1.5 (1M)"),
    ("Code generation",          "GPT-4o or Claude 3.5 Sonnet"),
    ("Privacy-critical apps",    "Llama 3.1 70B (self-hosted)"),
    ("Budget-friendly at scale", "Mixtral 8x7B or Llama 3.1 8B"),
    ("Multimodal (images+text)", "GPT-4o or Gemini 1.5 Pro"),
    ("Research/experimentation", "Llama 3.1 or Mistral (open weights)"),
    ("Complex reasoning",        "o1 / o3 or Claude 3 Opus"),
]

for task, model in use_cases:
    print(f"  {task:<30s} -> {model}")
```

**Output:**
```
Model Comparison Table
================================================================================
Model                Context  Open  Code       Reasoning  Cost
--------------------------------------------------------------------------------
GPT-4o               128K     No    Excellent  Excellent  $$$
Claude 3.5 Sonnet    200K     No    Excellent  Excellent  $$
Gemini 1.5 Pro       1M       No    Good       Good       $$
Llama 3.1 70B        128K     Yes   Good       Good       Free*
Mixtral 8x7B         32K      Yes   Good       Good       Free*
--------------------------------------------------------------------------------
* Free to download; hardware costs apply

When to Use Which Model:
=======================================================
  General chat/assistant       -> GPT-4o or Claude 3.5 Sonnet
  Long document analysis       -> Claude 3.5 (200K) or Gemini 1.5 (1M)
  Code generation              -> GPT-4o or Claude 3.5 Sonnet
  Privacy-critical apps        -> Llama 3.1 70B (self-hosted)
  Budget-friendly at scale     -> Mixtral 8x7B or Llama 3.1 8B
  Multimodal (images+text)     -> GPT-4o or Gemini 1.5 Pro
  Research/experimentation     -> Llama 3.1 or Mistral (open weights)
  Complex reasoning            -> o1 / o3 or Claude 3 Opus
```

---

## Choosing the Right Model: A Decision Framework

```python
# Interactive decision framework for choosing a model

def choose_model(scenario):
    """
    Simple decision tree for model selection.
    """
    print(f"Scenario: {scenario['description']}")
    print("-" * 50)

    # Decision factors
    factors = []

    if scenario.get("needs_privacy"):
        factors.append(("Privacy required", "Open source (Llama, Mistral)"))
    else:
        factors.append(("Privacy flexible", "Any model works"))

    if scenario.get("long_context"):
        factors.append(("Long context needed", "Gemini 1.5 or Claude 3.5"))

    if scenario.get("budget_tight"):
        factors.append(("Budget is tight", "Open source or smaller models"))
    else:
        factors.append(("Budget flexible", "Best model for the job"))

    if scenario.get("needs_code"):
        factors.append(("Code generation", "GPT-4o or Claude 3.5"))

    if scenario.get("needs_multimodal"):
        factors.append(("Multimodal needed", "GPT-4o or Gemini"))

    print("\nDecision factors:")
    for factor, implication in factors:
        print(f"  {factor:<25s} -> {implication}")

    print(f"\nRecommendation: {scenario['recommendation']}")
    print(f"Reason: {scenario['reason']}")
    print()

# Example scenarios
scenarios = [
    {
        "description": "Building a customer support chatbot for a bank",
        "needs_privacy": True,
        "budget_tight": False,
        "needs_code": False,
        "long_context": False,
        "needs_multimodal": False,
        "recommendation": "Llama 3.1 70B (self-hosted)",
        "reason": "Banking data must stay on your servers"
    },
    {
        "description": "Analyzing a 500-page legal contract",
        "needs_privacy": False,
        "budget_tight": False,
        "needs_code": False,
        "long_context": True,
        "needs_multimodal": False,
        "recommendation": "Gemini 1.5 Pro (1M context)",
        "reason": "Entire contract fits in one context window"
    },
    {
        "description": "Building a coding assistant for a startup",
        "needs_privacy": False,
        "budget_tight": True,
        "needs_code": True,
        "long_context": False,
        "needs_multimodal": False,
        "recommendation": "Claude 3.5 Sonnet or GPT-4o",
        "reason": "Top code generation with reasonable pricing"
    },
]

print("Model Selection Examples")
print("=" * 55)
print()
for scenario in scenarios:
    choose_model(scenario)
```

**Output:**
```
Model Selection Examples
=======================================================

Scenario: Building a customer support chatbot for a bank
--------------------------------------------------

Decision factors:
  Privacy required          -> Open source (Llama, Mistral)
  Budget flexible           -> Best model for the job

Recommendation: Llama 3.1 70B (self-hosted)
Reason: Banking data must stay on your servers

Scenario: Analyzing a 500-page legal contract
--------------------------------------------------

Decision factors:
  Privacy flexible          -> Any model works
  Long context needed       -> Gemini 1.5 or Claude 3.5
  Budget flexible           -> Best model for the job

Recommendation: Gemini 1.5 Pro (1M context)
Reason: Entire contract fits in one context window

Scenario: Building a coding assistant for a startup
--------------------------------------------------

Decision factors:
  Privacy flexible          -> Any model works
  Budget is tight           -> Open source or smaller models
  Code generation           -> GPT-4o or Claude 3.5

Recommendation: Claude 3.5 Sonnet or GPT-4o
Reason: Top code generation with reasonable pricing
```

---

## Common Mistakes

| Mistake | Why It Is Wrong | What to Do Instead |
|---------|----------------|-------------------|
| Using the most expensive model for every task | Small tasks do not need the most powerful model | Match model capability to task complexity |
| Ignoring open-source options | Open models are now very capable and offer more control | Evaluate open-source models for your use case |
| Choosing based on hype alone | The "best" model changes frequently | Test multiple models on your specific task |
| Not considering data privacy | Sending sensitive data to API providers has legal implications | Use self-hosted models for sensitive data |
| Locking into one provider | Vendor lock-in limits your options | Design your code to switch models easily |

---

## Best Practices

1. **Test before committing.** Try at least two or three models on your actual task before choosing one. Benchmarks do not always reflect real-world performance.

2. **Use the smallest model that works.** A 7B model that handles your task is better than a 70B model that is overkill. Save cost, reduce latency, and simplify deployment.

3. **Abstract your model calls.** Write your code so you can swap models by changing one line. Do not hard-code model-specific behaviors.

4. **Stay current.** The LLM landscape changes rapidly. A model that was the best choice six months ago may not be the best choice today.

5. **Consider total cost of ownership.** For open-source models, include hardware, maintenance, and engineering time. For closed-source, include API costs at your expected volume.

---

## Quick Summary

The LLM landscape includes closed-source models (GPT-4o, Claude, Gemini) accessed via APIs and open-weight models (Llama, Mistral) that you can download and run yourself. Each has distinct strengths: GPT-4o excels at code and general tasks, Claude at long documents and careful reasoning, Gemini at massive context and multimodality, Llama at privacy and customization, and Mistral at efficiency. The choice between open and closed source depends on your privacy needs, budget, volume, and technical capabilities.

---

## Key Points

- GPT-4o is a strong all-rounder with excellent code and reasoning, but is closed source and can be expensive
- Claude 3.5 Sonnet offers a large context window and strong safety alignment
- Gemini 1.5 Pro has the largest context window (1M tokens) and native multimodal support
- Llama 3.1 is open-weight, free to use, and ideal for privacy-sensitive and high-volume applications
- Mistral models are highly efficient, with Mixtral's MoE architecture offering speed and quality
- Open-source models give you control and privacy; closed-source models offer convenience and often higher quality
- Always test multiple models on your specific task before committing to one

---

## Practice Questions

1. A company needs to process medical records using an LLM. What type of model (open or closed source) should they likely use, and why?

2. Explain the Mixture of Experts (MoE) architecture in simple terms. Why does Mixtral 8x7B run faster than a traditional 46B parameter model?

3. You need to analyze an entire codebase of 500,000 tokens. Which models could handle this in a single context window? Which could not?

4. What are three factors that should influence your choice between GPT-4o and Llama 3.1 70B for a production application?

5. Why is it important to "abstract your model calls" when building applications? What happens if you do not?

---

## Exercises

### Exercise 1: Model Comparison

Choose a specific task (e.g., writing a product description, summarizing an article, or generating code). Submit the exact same prompt to at least two different models. Compare:
- Quality of output
- Speed of response
- Cost (if applicable)
- Any notable differences in style or approach

### Exercise 2: Open Source Exploration

Visit the Hugging Face model hub (huggingface.co) and browse the top LLMs. Find:
- Three open-source models not mentioned in this chapter
- Their parameter counts and license types
- What tasks they are optimized for

### Exercise 3: Cost Calculator

Build a simple Python script that calculates the monthly API cost for a hypothetical application:
- Input: number of requests per day, average tokens per request, price per 1M tokens
- Output: daily cost, monthly cost, yearly cost
- Compare costs for at least two different API providers

---

## What Is Next?

Now that you know the major models and how to choose between them, it is time to understand a fundamental concept that affects cost, performance, and capability: tokenization. In the next chapter, "Tokens and Tokenization", you will learn exactly how text gets broken into tokens, explore the algorithms behind it (BPE, WordPiece, SentencePiece), and use the tiktoken library to count tokens programmatically. Understanding tokenization is essential for managing costs and context windows effectively.
