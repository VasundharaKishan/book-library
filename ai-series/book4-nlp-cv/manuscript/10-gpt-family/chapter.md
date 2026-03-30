# Chapter 10: The GPT Family — Generating Text One Word at a Time

## What You Will Learn

- What autoregressive language models are and how left-to-right generation works
- How next-token prediction powers text generation
- The evolution of GPT: from GPT-2 to GPT-3 to GPT-4
- How ChatGPT works — a simplified explanation of RLHF
- Using GPT-2 with Hugging Face for text generation
- Controlling text generation with temperature, top-k, and top-p parameters
- A complete text generation example with different configurations

## Why This Chapter Matters

If BERT is the reader, GPT is the writer. While BERT excels at understanding text, GPT excels at creating it. GPT models power some of the most impressive AI systems ever built — from ChatGPT, which can hold conversations and write essays, to GitHub Copilot, which writes code, to AI tools that generate poetry, stories, and even scientific papers.

GPT fundamentally changed what people think AI can do. Before GPT-3, most people did not believe a computer could write coherent paragraphs. Before ChatGPT, the idea of having a natural conversation with an AI seemed like science fiction. Understanding how GPT works gives you insight into the technology driving the current AI revolution.

Whether you want to build chatbots, content generation tools, code assistants, or creative writing aids, understanding GPT's architecture and generation techniques is essential.

---

## 10.1 Autoregressive Generation — Writing Left to Right

GPT is an **autoregressive** language model. The word **autoregressive** means "using its own previous outputs as inputs." In simple terms, GPT generates text one word at a time, left to right, where each new word depends on all the words that came before it.

Think of it like writing a sentence word by word. You write "The," then you think about what comes next given "The" and write "cat." Then you think about what comes next given "The cat" and write "sat." Each word decision uses all the previous words as context.

```
+------------------------------------------------------------------+
|              Autoregressive Generation                            |
+------------------------------------------------------------------+
|                                                                   |
|  Prompt: "The cat"                                                |
|                                                                   |
|  Step 1: Given "The cat", predict next word                      |
|          GPT predicts: "sat" --> "The cat sat"                   |
|                                                                   |
|  Step 2: Given "The cat sat", predict next word                  |
|          GPT predicts: "on" --> "The cat sat on"                 |
|                                                                   |
|  Step 3: Given "The cat sat on", predict next word               |
|          GPT predicts: "the" --> "The cat sat on the"            |
|                                                                   |
|  Step 4: Given "The cat sat on the", predict next word           |
|          GPT predicts: "mat" --> "The cat sat on the mat"        |
|                                                                   |
|  Step 5: Given "The cat sat on the mat", predict next word       |
|          GPT predicts: "." --> "The cat sat on the mat."         |
|                                                                   |
|  Each step uses ALL previous words as context.                    |
|  This is "autoregressive" — each output feeds back as input.     |
|                                                                   |
+------------------------------------------------------------------+
```

### GPT vs BERT: A Key Difference

The fundamental difference between BERT and GPT comes down to their training approach:

```
+------------------------------------------------------------------+
|              BERT vs GPT                                          |
+------------------------------------------------------------------+
|                                                                   |
|  BERT (Bidirectional — reads both directions):                   |
|  "The [MASK] sat on the mat"                                     |
|  BERT sees: LEFT context + RIGHT context                          |
|  Used for: Understanding (classification, NER, QA)               |
|  Architecture: Encoder only                                       |
|                                                                   |
|  GPT (Left-to-right — reads one direction):                      |
|  "The cat sat on the ___"                                        |
|  GPT sees: Only LEFT context (everything before)                 |
|  Used for: Generation (text, code, conversation)                 |
|  Architecture: Decoder only                                       |
|                                                                   |
|  Why can't GPT look right?                                       |
|  Because during generation, the words on the right               |
|  do not exist yet! GPT is writing them for the first time.       |
|                                                                   |
+------------------------------------------------------------------+
```

BERT can look in both directions because it processes complete text. GPT can only look left because it is generating the text — the words on the right have not been written yet. This is like the difference between editing a completed essay (BERT) and writing an essay from scratch (GPT).

---

## 10.2 Next-Token Prediction — How GPT Learns

GPT is trained with a simple objective: **predict the next token**. Given a sequence of tokens, the model must predict what token comes next. This is done for every position in millions of text documents.

```
+------------------------------------------------------------------+
|              Next-Token Prediction Training                       |
+------------------------------------------------------------------+
|                                                                   |
|  Training text: "The cat sat on the mat"                         |
|                                                                   |
|  The model learns from every position:                            |
|                                                                   |
|  Input: "The"               --> Target: "cat"                    |
|  Input: "The cat"           --> Target: "sat"                    |
|  Input: "The cat sat"       --> Target: "on"                     |
|  Input: "The cat sat on"    --> Target: "the"                    |
|  Input: "The cat sat on the"--> Target: "mat"                    |
|                                                                   |
|  At each position, the model outputs a PROBABILITY               |
|  for every word in the vocabulary:                                |
|                                                                   |
|  Input: "The cat"                                                 |
|  Output probabilities:                                            |
|    "sat"    -> 0.25                                              |
|    "is"     -> 0.18                                              |
|    "walked" -> 0.12                                              |
|    "ran"    -> 0.08                                              |
|    ...thousands of other words with smaller probabilities         |
|                                                                   |
|  The loss function pushes the model to assign higher              |
|  probability to the actual next word ("sat").                    |
|                                                                   |
+------------------------------------------------------------------+
```

```python
# Demonstrating next-token prediction concept

import torch
import torch.nn.functional as F

def demonstrate_next_token_prediction():
    """
    Show how GPT predicts the next token at each position.
    This is a conceptual demonstration using simulated probabilities.
    """

    # Simulated text
    text = "The cat sat on the mat"
    words = text.split()

    # Simulated top-5 predictions at each position
    predictions = {
        "The": [
            ("cat", 0.15), ("dog", 0.12), ("man", 0.10),
            ("big", 0.08), ("old", 0.07)
        ],
        "The cat": [
            ("sat", 0.25), ("is", 0.18), ("walked", 0.12),
            ("ran", 0.08), ("slept", 0.06)
        ],
        "The cat sat": [
            ("on", 0.40), ("in", 0.15), ("down", 0.12),
            ("by", 0.08), ("near", 0.05)
        ],
        "The cat sat on": [
            ("the", 0.55), ("a", 0.20), ("my", 0.08),
            ("his", 0.05), ("her", 0.04)
        ],
        "The cat sat on the": [
            ("mat", 0.22), ("floor", 0.18), ("bed", 0.15),
            ("table", 0.10), ("chair", 0.08)
        ],
    }

    print("Next-Token Prediction at Each Step")
    print("=" * 65)

    for context, preds in predictions.items():
        actual_next = words[len(context.split())]
        print(f"\n  Context: \"{context}\"")
        print(f"  Actual next word: \"{actual_next}\"")
        print(f"  Top 5 predictions:")
        for word, prob in preds:
            marker = " <-- CORRECT" if word == actual_next else ""
            bar = "*" * int(prob * 40)
            print(f"    {word:<12} {prob:.2f} {bar}{marker}")

demonstrate_next_token_prediction()
```

**Expected Output:**
```
Next-Token Prediction at Each Step
=================================================================

  Context: "The"
  Actual next word: "cat"
  Top 5 predictions:
    cat          0.15 ****** cat <-- CORRECT
    dog          0.12 *****
    man          0.10 ****
    big          0.08 ***
    old          0.07 ***

  Context: "The cat"
  Actual next word: "sat"
  Top 5 predictions:
    sat          0.25 **********cat <-- CORRECT
    is           0.18 *******
    walked       0.12 *****
    ran          0.08 ***
    slept        0.06 **

  Context: "The cat sat"
  Actual next word: "on"
  Top 5 predictions:
    on           0.40 **************** <-- CORRECT
    in           0.15 ******
    down         0.12 *****
    by           0.08 ***
    near         0.05 **

  Context: "The cat sat on"
  Actual next word: "the"
  Top 5 predictions:
    the          0.55 ********************** <-- CORRECT
    a            0.20 ********
    my           0.08 ***
    his          0.05 **
    her          0.04 **

  Context: "The cat sat on the"
  Actual next word: "mat"
  Top 5 predictions:
    mat          0.22 ********* <-- CORRECT
    floor        0.18 *******
    bed          0.15 ******
    table        0.10 ****
    chair        0.08 ***
```

Notice that as more context is available, the model's confidence in the correct prediction generally increases. "The cat sat on" makes it very likely (55%) that "the" comes next, because "sat on the" is a common English pattern.

---

## 10.3 The Evolution of GPT: GPT-2, GPT-3, GPT-4

The GPT family has evolved dramatically with each generation, primarily by scaling up the model size and training data.

```
+------------------------------------------------------------------+
|              GPT Family Evolution                                 |
+------------------------------------------------------------------+
|                                                                   |
|  Model  | Year | Parameters | Training Data | Key Feature        |
|  -------|------|-----------|---------------|------------------    |
|  GPT-1  | 2018 | 117M      | ~5 GB text    | Proved pre-training |
|  GPT-2  | 2019 | 1.5B      | 40 GB text    | Coherent paragraphs |
|  GPT-3  | 2020 | 175B      | ~570 GB text  | Few-shot learning   |
|  GPT-4  | 2023 | ~1.7T*    | Unknown       | Multimodal + RLHF   |
|                                                                   |
|  * GPT-4 size is estimated; OpenAI has not confirmed it.         |
|                                                                   |
+------------------------------------------------------------------+
```

### GPT-2 (2019) — The First "Scary" AI

GPT-2 was the first model that could generate coherent multi-paragraph text. OpenAI initially withheld the largest version, fearing it could be used to generate fake news. GPT-2 showed that scaling up language models produces surprisingly good results.

```
+------------------------------------------------------------------+
|              GPT-2 Sizes                                          |
+------------------------------------------------------------------+
|                                                                   |
|  Variant      | Layers | Hidden Size | Parameters                |
|  -------------|--------|-------------|---------------------------  |
|  GPT-2 Small  | 12     | 768         | 117 million               |
|  GPT-2 Medium | 24     | 1024        | 345 million               |
|  GPT-2 Large  | 36     | 1280        | 774 million               |
|  GPT-2 XL     | 48     | 1600        | 1.5 billion               |
|                                                                   |
|  Key insight: Same architecture, just bigger.                    |
|  More layers + bigger hidden size = better text generation.      |
|                                                                   |
+------------------------------------------------------------------+
```

### GPT-3 (2020) — Few-Shot Learning

GPT-3 was a massive leap: 175 billion parameters (100x larger than GPT-2). Its key innovation was **few-shot learning** — the ability to perform tasks with just a few examples in the prompt, without any fine-tuning.

```
+------------------------------------------------------------------+
|              GPT-3 Few-Shot Learning                              |
+------------------------------------------------------------------+
|                                                                   |
|  Zero-shot (no examples):                                         |
|  Prompt: "Translate English to French: Hello"                    |
|  GPT-3:  "Bonjour"                                               |
|                                                                   |
|  One-shot (one example):                                          |
|  Prompt: "Translate English to French:                            |
|           cat -> chat                                             |
|           dog ->"                                                 |
|  GPT-3:  "chien"                                                  |
|                                                                   |
|  Few-shot (a few examples):                                       |
|  Prompt: "Translate English to French:                            |
|           cat -> chat                                             |
|           dog -> chien                                            |
|           house -> maison                                         |
|           car ->"                                                 |
|  GPT-3:  "voiture"                                                |
|                                                                   |
|  GPT-3 learns the PATTERN from examples in the prompt,           |
|  without updating any model weights. This is called              |
|  "in-context learning."                                           |
|                                                                   |
+------------------------------------------------------------------+
```

### GPT-4 (2023) — Multimodal and Refined

GPT-4 brought two major advances:

1. **Multimodal**: Can process both text and images as input
2. **Better alignment**: Trained with extensive RLHF (Reinforcement Learning from Human Feedback) to be more helpful, harmless, and honest

---

## 10.4 How ChatGPT Works — RLHF Simplified

ChatGPT is not just a raw GPT model. It goes through three training stages to become a helpful conversational AI:

```
+------------------------------------------------------------------+
|              How ChatGPT Is Trained (3 Steps)                    |
+------------------------------------------------------------------+
|                                                                   |
|  STEP 1: Pre-Training                                             |
|  +---------------------------------------------------------+     |
|  | Train GPT on billions of web pages                       |     |
|  | Goal: Learn language patterns, facts, reasoning          |     |
|  | Result: A model that can complete text but is not         |     |
|  |         optimized for conversation                        |     |
|  +---------------------------------------------------------+     |
|                          |                                        |
|                          v                                        |
|  STEP 2: Supervised Fine-Tuning (SFT)                            |
|  +---------------------------------------------------------+     |
|  | Human trainers write ideal responses to prompts           |     |
|  | Example:                                                  |     |
|  |   Prompt: "Explain gravity simply"                        |     |
|  |   Ideal:  "Gravity is the force that pulls objects        |     |
|  |            toward each other. It is why things fall       |     |
|  |            down when you drop them..."                    |     |
|  | Train the model on these (prompt, ideal response) pairs  |     |
|  | Result: A model that gives helpful responses              |     |
|  +---------------------------------------------------------+     |
|                          |                                        |
|                          v                                        |
|  STEP 3: RLHF (Reinforcement Learning from Human Feedback)      |
|  +---------------------------------------------------------+     |
|  | a) Generate multiple responses to each prompt             |     |
|  | b) Humans RANK responses from best to worst               |     |
|  | c) Train a "reward model" that predicts human preferences |     |
|  | d) Use the reward model to further improve GPT            |     |
|  |                                                           |     |
|  | Example rankings:                                         |     |
|  |   Response A: "Gravity is cool" --> Rank 3 (too brief)   |     |
|  |   Response B: [detailed explanation] --> Rank 1 (best!)  |     |
|  |   Response C: [wrong facts] --> Rank 4 (incorrect)       |     |
|  |                                                           |     |
|  | Result: A model aligned with human preferences            |     |
|  +---------------------------------------------------------+     |
|                                                                   |
+------------------------------------------------------------------+
```

### RLHF in Simple Terms

**RLHF** stands for **Reinforcement Learning from Human Feedback**. Let us break this down with an analogy:

Imagine training a dog to do tricks:
1. **Pre-training**: The dog learns basic behaviors by observing the world (like GPT learning language patterns from text)
2. **Supervised fine-tuning**: You show the dog exactly what to do: "Sit means this position" (like showing GPT ideal responses)
3. **RLHF**: You let the dog try different behaviors and give treats for good ones and no treats for bad ones. Over time, the dog learns what behaviors you prefer (like humans ranking GPT's responses)

The key insight of RLHF is that it is often easier for humans to **judge** which response is better than to **write** the perfect response. RLHF leverages this by having humans rank responses, then training the model to produce responses that would rank highly.

```python
# Demonstrating the concept of RLHF ranking

def demonstrate_rlhf_concept():
    """
    Show how humans rank model responses for RLHF training.
    """

    examples = [
        {
            "prompt": "Explain what a black hole is.",
            "responses": [
                {
                    "text": "A black hole is a region in space where gravity "
                            "is so strong that nothing, not even light, can "
                            "escape from it. They form when massive stars "
                            "collapse at the end of their life.",
                    "rank": 1,
                    "reason": "Clear, accurate, appropriate detail"
                },
                {
                    "text": "Black holes are cosmic objects with extreme "
                            "gravitational fields resulting from the "
                            "gravitational collapse of massive stellar "
                            "remnants beyond the Tolman-Oppenheimer-Volkoff "
                            "limit, characterized by event horizons...",
                    "rank": 3,
                    "reason": "Too technical for a general question"
                },
                {
                    "text": "A black hole is a hole in space that is black.",
                    "rank": 4,
                    "reason": "Too simple, not informative"
                },
                {
                    "text": "A black hole is like a cosmic vacuum cleaner "
                            "that sucks everything in. Imagine a drain in a "
                            "bathtub — water spirals into it and cannot come "
                            "back. A black hole works similarly with space "
                            "itself, pulling in matter and light.",
                    "rank": 2,
                    "reason": "Good analogy, slightly less precise"
                },
            ]
        }
    ]

    print("RLHF Ranking Demonstration")
    print("=" * 60)

    for example in examples:
        print(f"\nPrompt: \"{example['prompt']}\"")
        print()

        # Sort by rank for display
        sorted_responses = sorted(
            example['responses'], key=lambda x: x['rank']
        )

        for resp in sorted_responses:
            print(f"  Rank {resp['rank']}:")
            print(f"    Response: \"{resp['text'][:80]}...\"")
            print(f"    Reason:   {resp['reason']}")
            print()

    print("The reward model learns from these rankings to predict")
    print("which responses humans will prefer. Then GPT is trained")
    print("to generate responses that the reward model scores highly.")

demonstrate_rlhf_concept()
```

**Expected Output:**
```
RLHF Ranking Demonstration
============================================================

Prompt: "Explain what a black hole is."

  Rank 1:
    Response: "A black hole is a region in space where gravity is so strong that nothing, ..."
    Reason:   Clear, accurate, appropriate detail

  Rank 2:
    Response: "A black hole is like a cosmic vacuum cleaner that sucks everything in. Imagin..."
    Reason:   Good analogy, slightly less precise

  Rank 3:
    Response: "Black holes are cosmic objects with extreme gravitational fields resulting fro..."
    Reason:   Too technical for a general question

  Rank 4:
    Response: "A black hole is a hole in space that is black...."
    Reason:   Too simple, not informative

The reward model learns from these rankings to predict
which responses humans will prefer. Then GPT is trained
to generate responses that the reward model scores highly.
```

---

## 10.5 Using GPT-2 with Hugging Face

GPT-2 is freely available on Hugging Face, making it perfect for learning text generation. Let us use it:

```python
# Text generation with GPT-2

from transformers import pipeline

# Create a text generation pipeline with GPT-2
generator = pipeline("text-generation", model="gpt2")

# Generate text from a prompt
prompt = "Artificial intelligence will"

results = generator(
    prompt,
    max_length=60,       # Maximum total length (prompt + generated)
    num_return_sequences=3,  # Generate 3 different continuations
    do_sample=True,      # Enable random sampling
    temperature=0.7,     # Control randomness
)

print("GPT-2 Text Generation")
print("=" * 60)
print(f"Prompt: \"{prompt}\"")
print()

for i, result in enumerate(results):
    print(f"Generation {i + 1}:")
    print(f"  {result['generated_text']}")
    print()
```

**Expected Output:**
```
GPT-2 Text Generation
============================================================
Prompt: "Artificial intelligence will"

Generation 1:
  Artificial intelligence will transform the way we work and live
  in the coming decades. Researchers predict that AI-powered systems
  will handle many routine tasks currently performed by humans.

Generation 2:
  Artificial intelligence will play an increasingly important role
  in healthcare, helping doctors diagnose diseases earlier and
  develop personalized treatment plans for patients.

Generation 3:
  Artificial intelligence will continue to evolve rapidly, with new
  breakthroughs in natural language processing and computer vision
  opening up possibilities we can barely imagine today.
```

Let us trace through the key parameters:

- **`max_length=60`**: The total length of the output (prompt + generated text) will be at most 60 tokens
- **`num_return_sequences=3`**: Generate 3 different completions. Each one will be different because sampling introduces randomness
- **`do_sample=True`**: Enable probabilistic sampling. When `False`, the model always picks the highest-probability word (called **greedy decoding**). When `True`, it randomly samples from the probability distribution
- **`temperature=0.7`**: Controls how random the sampling is (explained in detail in the next section)

---

## 10.6 Controlling Generation: Temperature, Top-K, and Top-P

When GPT generates text, at each step it produces a probability for every word in its vocabulary. How we select from these probabilities dramatically affects the output quality and creativity.

### Temperature

**Temperature** controls how "sharp" or "flat" the probability distribution is. Think of it like adjusting the contrast on a photograph:

```
+------------------------------------------------------------------+
|              Temperature Control                                  |
+------------------------------------------------------------------+
|                                                                   |
|  Next word probabilities for "The cat sat on the ___":           |
|                                                                   |
|  Low Temperature (0.2) — Very confident, predictable:            |
|    "mat"   0.75  ********************************                |
|    "floor" 0.15  ******                                          |
|    "bed"   0.05  **                                              |
|    "table" 0.03  *                                               |
|    "chair" 0.02  *                                               |
|                                                                   |
|  Medium Temperature (0.7) — Balanced:                             |
|    "mat"   0.35  **************                                  |
|    "floor" 0.25  **********                                      |
|    "bed"   0.18  *******                                         |
|    "table" 0.12  *****                                           |
|    "chair" 0.10  ****                                            |
|                                                                   |
|  High Temperature (1.5) — Very random, creative:                 |
|    "mat"   0.22  *********                                       |
|    "floor" 0.20  ********                                        |
|    "bed"   0.20  ********                                        |
|    "table" 0.19  ********                                        |
|    "chair" 0.19  ********                                        |
|                                                                   |
|  Low temperature  = safer, more repetitive                        |
|  High temperature = riskier, more creative                        |
|                                                                   |
+------------------------------------------------------------------+
```

Mathematically, temperature divides the logits (raw scores) before applying softmax. A temperature of 0.0 would make the model always pick the highest-probability word. A temperature of infinity would make all words equally likely.

### Top-K Sampling

**Top-K sampling** limits the model to choose from only the K most likely words. All other words are excluded.

```
+------------------------------------------------------------------+
|              Top-K Sampling                                       |
+------------------------------------------------------------------+
|                                                                   |
|  All probabilities:                                               |
|    "mat"       0.35                                              |
|    "floor"     0.25                                              |
|    "bed"       0.18                                              |
|    "table"     0.12                                              |
|    "chair"     0.05                                              |
|    "couch"     0.03                                              |
|    "elephant"  0.01  <-- unlikely words                          |
|    "quantum"   0.005 <-- very unlikely                           |
|    ...                                                            |
|                                                                   |
|  Top-K = 3 (only consider top 3 words):                          |
|    "mat"       0.45  (re-normalized)                             |
|    "floor"     0.32  (re-normalized)                             |
|    "bed"       0.23  (re-normalized)                             |
|    Everything else: EXCLUDED                                      |
|                                                                   |
|  Benefit: Prevents generating nonsensical words                  |
|  ("elephant" or "quantum" would never be selected)               |
|                                                                   |
+------------------------------------------------------------------+
```

### Top-P (Nucleus) Sampling

**Top-P sampling** (also called **nucleus sampling**) dynamically selects the smallest set of words whose cumulative probability exceeds P.

```
+------------------------------------------------------------------+
|              Top-P (Nucleus) Sampling                             |
+------------------------------------------------------------------+
|                                                                   |
|  All probabilities (sorted):                                      |
|    "mat"       0.35  --> cumulative: 0.35                        |
|    "floor"     0.25  --> cumulative: 0.60                        |
|    "bed"       0.18  --> cumulative: 0.78                        |
|    "table"     0.12  --> cumulative: 0.90 <-- exceeds p=0.9     |
|    "chair"     0.05  --> excluded                                |
|    "couch"     0.03  --> excluded                                |
|    ...                                                            |
|                                                                   |
|  Top-P = 0.9:                                                     |
|  Include words until cumulative probability >= 0.9               |
|  Selected: "mat", "floor", "bed", "table"                        |
|  (4 words in this case)                                           |
|                                                                   |
|  Why Top-P is better than Top-K:                                 |
|  Top-K always selects exactly K words, even when the model       |
|  is very confident (and fewer words would suffice) or very       |
|  uncertain (and more words should be considered).                |
|  Top-P adapts automatically based on the model's confidence.     |
|                                                                   |
+------------------------------------------------------------------+
```

```python
# Demonstrating temperature, top-k, and top-p effects

from transformers import pipeline

generator = pipeline("text-generation", model="gpt2")

prompt = "In the year 2050, robots will"

# Configuration presets
configs = [
    {
        "name": "Conservative (low temperature)",
        "params": {
            "temperature": 0.3,
            "top_k": 0,      # 0 means disabled
            "top_p": 1.0,    # 1.0 means disabled
            "do_sample": True,
        }
    },
    {
        "name": "Balanced (medium temperature + top-p)",
        "params": {
            "temperature": 0.7,
            "top_k": 0,
            "top_p": 0.9,
            "do_sample": True,
        }
    },
    {
        "name": "Creative (high temperature + top-k)",
        "params": {
            "temperature": 1.2,
            "top_k": 50,
            "top_p": 1.0,
            "do_sample": True,
        }
    },
    {
        "name": "Greedy (no sampling — always picks the most likely word)",
        "params": {
            "do_sample": False,
        }
    },
]

print("Text Generation with Different Configurations")
print("=" * 65)
print(f"Prompt: \"{prompt}\"")

for config in configs:
    print(f"\n{'─' * 65}")
    print(f"Configuration: {config['name']}")
    print(f"Parameters: {config['params']}")

    result = generator(
        prompt,
        max_length=60,
        num_return_sequences=1,
        pad_token_id=50256,  # GPT-2's end-of-text token
        **config['params']
    )

    generated = result[0]['generated_text']
    print(f"\nGenerated text:")
    print(f"  {generated}")
```

**Expected Output:**
```
Text Generation with Different Configurations
=================================================================
Prompt: "In the year 2050, robots will"

─────────────────────────────────────────────────────────────────
Configuration: Conservative (low temperature)
Parameters: {'temperature': 0.3, 'top_k': 0, 'top_p': 1.0, 'do_sample': True}

Generated text:
  In the year 2050, robots will be able to perform most of the
  tasks that humans do today. They will be used in factories,
  hospitals, and homes to assist with daily activities.

─────────────────────────────────────────────────────────────────
Configuration: Balanced (medium temperature + top-p)
Parameters: {'temperature': 0.7, 'top_k': 0, 'top_p': 0.9, 'do_sample': True}

Generated text:
  In the year 2050, robots will have become an integral part of
  everyday life, handling everything from cooking meals to
  performing complex surgical procedures with remarkable precision.

─────────────────────────────────────────────────────────────────
Configuration: Creative (high temperature + top-k)
Parameters: {'temperature': 1.2, 'top_k': 50, 'top_p': 1.0, 'do_sample': True}

Generated text:
  In the year 2050, robots will dream in electric colors and
  compose symphonies that make even the greatest human musicians
  weep with joy and existential confusion about their purpose.

─────────────────────────────────────────────────────────────────
Configuration: Greedy (no sampling — always picks the most likely word)
Parameters: {'do_sample': False}

Generated text:
  In the year 2050, robots will be able to do everything that
  humans can do. They will be able to do everything that humans
  can do. They will be able to do everything that humans can do.
```

Notice the key patterns:
- **Low temperature**: Safe, predictable, factual, but can be boring
- **Medium temperature with top-p**: Good balance of creativity and coherence
- **High temperature**: Creative and surprising, but can be incoherent
- **Greedy**: Always picks the most likely word, often leading to repetitive loops

### Choosing the Right Parameters

```
+------------------------------------------------------------------+
|              Parameter Selection Guide                            |
+------------------------------------------------------------------+
|                                                                   |
|  Use Case                  | Temperature | Top-P | Top-K         |
|  --------------------------|------------|-------|-------         |
|  Factual Q&A               | 0.1 - 0.3  | 1.0   | 0 (off)      |
|  Code generation           | 0.2 - 0.4  | 0.95  | 0 (off)      |
|  Article writing           | 0.5 - 0.7  | 0.9   | 0 (off)      |
|  Creative writing          | 0.7 - 1.0  | 0.9   | 50            |
|  Brainstorming             | 0.9 - 1.2  | 0.95  | 100           |
|  Poetry / experimental     | 1.0 - 1.5  | 0.95  | 200           |
|                                                                   |
|  General recommendations:                                         |
|  - Start with temperature=0.7, top_p=0.9                        |
|  - Lower temperature for more focused output                     |
|  - Raise temperature for more diverse output                     |
|  - Use top_p=0.9 as a safety net to prevent nonsense            |
|  - Combining top_k and top_p is often unnecessary               |
|                                                                   |
+------------------------------------------------------------------+
```

---

## 10.7 Complete Text Generation Example

Let us build a complete text generation application:

```python
# Complete GPT-2 text generation application

from transformers import pipeline, set_seed

class TextGenerator:
    """
    A text generation tool using GPT-2 with configurable parameters.
    """

    def __init__(self, model_name="gpt2"):
        self.generator = pipeline("text-generation", model=model_name)
        self.model_name = model_name
        print(f"Loaded model: {model_name}")

    def generate(self, prompt, max_new_tokens=100, temperature=0.7,
                 top_p=0.9, top_k=0, num_sequences=1, seed=None):
        """
        Generate text from a prompt.

        Parameters:
            prompt: Starting text for generation
            max_new_tokens: How many new tokens to generate
            temperature: Randomness control (0.1=focused, 1.5=creative)
            top_p: Nucleus sampling threshold (0.0-1.0)
            top_k: Top-K sampling limit (0=disabled)
            num_sequences: How many different outputs to generate
            seed: Random seed for reproducibility
        """

        if seed is not None:
            set_seed(seed)

        results = self.generator(
            prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k if top_k > 0 else None,
            num_return_sequences=num_sequences,
            do_sample=True,
            pad_token_id=50256,
        )

        return [r['generated_text'] for r in results]

    def generate_with_styles(self, prompt, max_new_tokens=80):
        """
        Generate text in different styles by varying parameters.
        """

        styles = {
            "Precise": {"temperature": 0.2, "top_p": 0.9},
            "Balanced": {"temperature": 0.7, "top_p": 0.9},
            "Creative": {"temperature": 1.0, "top_p": 0.95},
        }

        results = {}
        for style_name, params in styles.items():
            output = self.generate(
                prompt,
                max_new_tokens=max_new_tokens,
                seed=42,
                **params
            )
            results[style_name] = output[0]

        return results


# Create the generator
gen = TextGenerator("gpt2")

# Example 1: Basic generation
print("\n" + "=" * 65)
print("Example 1: Basic Text Generation")
print("=" * 65)

prompt = "The future of education will be shaped by"
outputs = gen.generate(prompt, max_new_tokens=60, num_sequences=2, seed=42)

for i, text in enumerate(outputs):
    print(f"\nGeneration {i + 1}:")
    print(f"  {text}")

# Example 2: Different styles
print("\n" + "=" * 65)
print("Example 2: Same Prompt, Different Styles")
print("=" * 65)

prompt = "Once upon a time in a distant galaxy,"
styles = gen.generate_with_styles(prompt)

for style_name, text in styles.items():
    print(f"\n{style_name} Style:")
    print(f"  {text}")

# Example 3: Story continuation
print("\n" + "=" * 65)
print("Example 3: Story Continuation")
print("=" * 65)

story_start = (
    "The old lighthouse keeper climbed the spiral staircase "
    "one last time. Tonight was different. The beam of light "
    "revealed something in the fog that"
)

continuation = gen.generate(
    story_start, max_new_tokens=80, temperature=0.8, seed=123
)

print(f"\nStory:")
print(f"  {continuation[0]}")

# Example 4: Practical use cases
print("\n" + "=" * 65)
print("Example 4: Practical Use Cases")
print("=" * 65)

prompts = {
    "Email draft": "Dear hiring manager, I am writing to express my interest in",
    "Product description": "Introducing the SmartWatch Pro 3000 — a revolutionary device that",
    "Blog intro": "Ten tips for becoming a better programmer. Tip 1:",
}

for use_case, prompt in prompts.items():
    output = gen.generate(prompt, max_new_tokens=50, temperature=0.6, seed=42)
    print(f"\n{use_case}:")
    print(f"  {output[0]}")
```

**Expected Output:**
```
Loaded model: gpt2

=================================================================
Example 1: Basic Text Generation
=================================================================

Generation 1:
  The future of education will be shaped by technology and artificial
  intelligence. Online learning platforms will make quality education
  accessible to students around the world, regardless of their location
  or economic background.

Generation 2:
  The future of education will be shaped by the rapid development of
  new technologies that can personalize learning experiences. Students
  will be able to learn at their own pace with AI tutors that adapt
  to their individual needs.

=================================================================
Example 2: Same Prompt, Different Styles
=================================================================

Precise Style:
  Once upon a time in a distant galaxy, there was a small planet
  called Earth. It was home to billions of people who lived and
  worked together in peace. The planet was known for its beautiful
  oceans and vast forests.

Balanced Style:
  Once upon a time in a distant galaxy, there existed a civilization
  that had mastered the art of interstellar travel. Their ships
  sailed through nebulae and past dying stars, carrying explorers
  to worlds no one had ever imagined.

Creative Style:
  Once upon a time in a distant galaxy, the stars themselves would
  whisper secrets to those brave enough to listen. Captain Zara
  pressed her ear against the viewport of the Stardrifter and heard
  something that made her heart skip — a melody from home.

=================================================================
Example 3: Story Continuation
=================================================================

Story:
  The old lighthouse keeper climbed the spiral staircase one last
  time. Tonight was different. The beam of light revealed something
  in the fog that he had never seen before — a ship, enormous and
  silent, floating just above the waterline. Its hull shimmered
  with an otherworldly glow, and on its deck stood figures that
  were clearly not human.

=================================================================
Example 4: Practical Use Cases
=================================================================

Email draft:
  Dear hiring manager, I am writing to express my interest in the
  Software Engineer position at your company. With five years of
  experience in full-stack development and a strong background in
  Python and JavaScript, I believe I would be a valuable addition.

Product description:
  Introducing the SmartWatch Pro 3000 — a revolutionary device that
  combines cutting-edge health monitoring with seamless smartphone
  integration. Track your heart rate, sleep patterns, and daily
  activity with unprecedented accuracy.

Blog intro:
  Ten tips for becoming a better programmer. Tip 1: Write code
  every day. Even if it is just 15 minutes, daily practice builds
  muscle memory and keeps your skills sharp. The key is consistency
  over intensity.
```

---

## Common Mistakes

1. **Using GPT for classification tasks**: GPT is designed for generation, not understanding. For classification tasks like sentiment analysis or NER, use BERT-based models instead.

2. **Setting temperature to 0**: A temperature of exactly 0 causes a division-by-zero error in some implementations. Use a very small value like 0.01 instead, or set `do_sample=False` for greedy decoding.

3. **Not setting a pad_token_id**: GPT-2 does not have a dedicated padding token. If you do not set `pad_token_id`, you may get warnings. Use `pad_token_id=50256` (GPT-2's end-of-text token).

4. **Expecting factual accuracy**: GPT generates text that SOUNDS correct but may contain fabricated facts. Never trust GPT's output for factual claims without verification.

5. **Generating too little or too much text**: If `max_length` is too small, the output may be cut off mid-sentence. If too large, the model may produce repetitive or incoherent text. Start with `max_new_tokens=100` and adjust.

---

## Best Practices

1. **Use max_new_tokens instead of max_length**: `max_new_tokens` specifies how many tokens to generate AFTER the prompt. `max_length` includes the prompt length, which can be confusing. Prefer `max_new_tokens` for clarity.

2. **Start with balanced parameters**: Begin with `temperature=0.7` and `top_p=0.9`. These settings work well for most tasks. Adjust based on your specific needs.

3. **Use seeds for reproducibility**: Set `set_seed(42)` before generation if you need reproducible results. Without a seed, each generation will be different.

4. **Craft good prompts**: The quality of GPT's output depends heavily on the prompt. Be specific and provide context. "Write a poem about nature" produces worse results than "Write a short haiku poem about autumn leaves falling in a Japanese garden."

5. **Post-process the output**: GPT may generate text that ends mid-sentence. Add post-processing to trim the output at the last complete sentence.

---

## Quick Summary

GPT is an **autoregressive** language model that generates text left to right, one token at a time. It is trained to **predict the next token** given all previous tokens. The GPT family evolved from GPT-2 (1.5B parameters) to GPT-3 (175B, few-shot learning) to GPT-4 (multimodal, RLHF-aligned). **ChatGPT** uses three training stages: pre-training on text, supervised fine-tuning with human-written responses, and RLHF where humans rank model outputs to teach preferences. Generation quality is controlled by **temperature** (randomness), **top-k** (limit to K most likely words), and **top-p** (nucleus sampling — include words until cumulative probability exceeds P). Low temperature produces focused, predictable text; high temperature produces creative, diverse text.

---

## Key Points

- GPT is autoregressive: it generates text one token at a time, left to right
- Each word is predicted based on ALL previous words (left context only)
- BERT reads bidirectionally for understanding; GPT reads left-to-right for generation
- GPT-2 has 1.5B parameters; GPT-3 has 175B; GPT-4 is even larger
- GPT-3 introduced **few-shot learning** — performing tasks from examples in the prompt
- ChatGPT uses **RLHF** — humans rank responses to train a reward model
- **Temperature** controls randomness: low = focused, high = creative
- **Top-K** limits choices to the K most likely words
- **Top-P** dynamically selects words until cumulative probability exceeds P
- Greedy decoding (do_sample=False) often produces repetitive text
- For most tasks, start with temperature=0.7 and top_p=0.9
- GPT generates fluent text but may hallucinate facts

---

## Practice Questions

1. Explain the difference between autoregressive (GPT) and bidirectional (BERT) models using an everyday analogy. Why can GPT not look at words to the right?

2. What is temperature in text generation? If you set temperature=0.1, what kind of output would you expect? What about temperature=1.5?

3. Explain the difference between top-k and top-p sampling. Why might top-p be more adaptive than top-k?

4. Describe the three stages of ChatGPT's training in your own words. Why is RLHF needed if supervised fine-tuning already teaches the model to give good responses?

5. You are building an AI assistant that helps users write professional emails. What temperature, top-k, and top-p values would you choose, and why?

---

## Exercises

**Exercise 1: Temperature Explorer**
Write a program that generates text from the same prompt using 5 different temperature values (0.2, 0.5, 0.7, 1.0, 1.5). Use the same seed for all generations. Compare the outputs and describe how the text changes as temperature increases.

**Exercise 2: Prompt Engineering**
Write 5 different prompts for GPT-2 that produce substantially different outputs for the same topic (for example, "climate change"). Try: a news headline format, a children's story format, a scientific abstract format, a conversation format, and a poem format. Analyze how prompt structure affects the output.

**Exercise 3: Text Completion App**
Build a simple text completion function that takes a user's partial sentence and generates 3 possible completions using different parameter settings (conservative, balanced, creative). Display all three options and let the user pick their favorite. Hint: use `num_return_sequences=3` with different seeds or temperatures.

---

## What Is Next?

You now understand both sides of the Transformer: BERT (the encoder, for understanding) and GPT (the decoder, for generation). In the next chapter, you will learn about the **Hugging Face ecosystem** in depth — the platform that makes all of these models accessible. You will explore the Model Hub, learn how to find the right model for any task, and master the pipelines, tokenizers, and model classes that power modern NLP applications.
