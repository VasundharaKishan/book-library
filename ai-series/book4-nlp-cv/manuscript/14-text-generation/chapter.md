# Chapter 14: Text Generation

## What You Will Learn

In this chapter, you will learn:

- How autoregressive text generation works (predicting one word at a time)
- What temperature is and how it controls the randomness of generated text
- How top-k sampling limits choices to the most likely words
- How top-p (nucleus) sampling works and why it is often preferred
- How to control output length and prevent repetition
- How to use Hugging Face's `generate()` method with all its options
- How to build a complete story generation example
- The basics of prompt engineering for better results

## Why This Chapter Matters

Text generation is the technology behind some of the most impressive AI applications today. When you ask a chatbot a question and it writes a thoughtful response, that is text generation. When a coding tool suggests the next line of code, that is text generation. When an AI writes a product description, a poem, or a news summary -- all text generation.

Understanding how text generation works is not just about using it -- it is about controlling it. Without understanding temperature, sampling strategies, and repetition penalties, your generated text will often be boring, repetitive, or nonsensical. This chapter gives you the knobs and dials to produce exactly the kind of text you want.

Think of a text generation model as a very talented writer who needs clear instructions. Temperature tells the writer how creative to be. Top-k and top-p tell the writer which word choices to consider. This chapter teaches you how to be a good editor for your AI writer.

---

## 14.1 How Autoregressive Generation Works

### The Word-by-Word Process

Text generation models work by predicting one word (actually, one token) at a time. Each prediction depends on all the words that came before it:

```
+--------------------------------------------------------------+
|        AUTOREGRESSIVE GENERATION                              |
+--------------------------------------------------------------+
|                                                                |
|  Prompt: "The cat sat"                                        |
|                                                                |
|  Step 1: What comes after "The cat sat"?                      |
|           Model predicts: "on"                                |
|           Text so far: "The cat sat on"                       |
|                                                                |
|  Step 2: What comes after "The cat sat on"?                   |
|           Model predicts: "the"                               |
|           Text so far: "The cat sat on the"                   |
|                                                                |
|  Step 3: What comes after "The cat sat on the"?               |
|           Model predicts: "mat"                               |
|           Text so far: "The cat sat on the mat"               |
|                                                                |
|  Step 4: What comes after "The cat sat on the mat"?           |
|           Model predicts: "." (end of sentence)               |
|           Text so far: "The cat sat on the mat."              |
|                                                                |
|  This is called "autoregressive" because each prediction      |
|  feeds back into the input for the next prediction.           |
|                                                                |
+--------------------------------------------------------------+
```

The word "autoregressive" comes from two parts:
- **Auto** = self
- **Regressive** = using previous outputs

So autoregressive means "using its own previous outputs as input."

### The Probability Distribution

At each step, the model does not just pick one word. It calculates a probability for every word in its vocabulary:

```
+--------------------------------------------------------------+
|        PROBABILITY DISTRIBUTION AT EACH STEP                 |
+--------------------------------------------------------------+
|                                                                |
|  Input: "The cat sat on the"                                  |
|                                                                |
|  Model calculates probabilities for ALL words:                |
|                                                                |
|  mat     ||||||||||||||||||||||||  0.35  (35%)                |
|  floor   |||||||||||||||           0.20  (20%)                |
|  couch   ||||||||||                0.12  (12%)                |
|  bed     ||||||||                  0.10  (10%)                |
|  table   ||||||                    0.08  (8%)                 |
|  chair   |||||                     0.06  (6%)                 |
|  roof    |||                       0.04  (4%)                 |
|  ...     |                         0.05  (5% total for rest)  |
|                                                                |
|  The question is: HOW do we choose from these probabilities?  |
|  That is what temperature, top-k, and top-p control.          |
|                                                                |
+--------------------------------------------------------------+
```

### Basic Text Generation

```python
from transformers import pipeline

# Create a text generation pipeline
generator = pipeline("text-generation", model="gpt2")

# Generate text from a prompt
prompt = "Once upon a time in a land far away"
result = generator(prompt, max_length=60, num_return_sequences=1)

print("Prompt:", prompt)
print("Generated:", result[0]['generated_text'])
```

**Expected output:**

```
Prompt: Once upon a time in a land far away
Generated: Once upon a time in a land far away, there lived a young
princess who dreamed of exploring the world beyond her castle walls.
She spent her days reading books about distant kingdoms and magical
creatures.
```

**Line-by-line explanation:**
- `pipeline("text-generation", model="gpt2")` -- Creates a text generation pipeline using GPT-2, a popular generation model
- `max_length=60` -- Generate at most 60 tokens total (including the prompt)
- `num_return_sequences=1` -- Generate one version of the text
- The output includes the original prompt followed by the generated continuation

> **Note:** Your output will differ from this example. Text generation involves randomness, so each run produces different text.

---

## 14.2 Temperature: Controlling Randomness

### What Is Temperature?

Temperature controls how random or predictable the generated text is. Think of it as a "creativity dial":

```
+--------------------------------------------------------------+
|        TEMPERATURE ANALOGY                                    |
+--------------------------------------------------------------+
|                                                                |
|  Temperature = 0.1 (Very Low)                                 |
|    Like a careful student always choosing the "safe" answer   |
|    Output is predictable and repetitive                       |
|    Almost always picks the most likely word                   |
|                                                                |
|  Temperature = 0.7 (Medium)                                   |
|    Like a balanced writer mixing common and creative words    |
|    Output is natural and interesting                          |
|    Good balance of coherence and variety                      |
|                                                                |
|  Temperature = 1.5 (Very High)                                |
|    Like a wild poet throwing words together                   |
|    Output is creative but sometimes nonsensical               |
|    Often picks unexpected, unusual words                      |
|                                                                |
+--------------------------------------------------------------+
```

### How Temperature Works Mathematically

Temperature modifies the probability distribution before a word is chosen:

```
+--------------------------------------------------------------+
|        TEMPERATURE EFFECT ON PROBABILITIES                    |
+--------------------------------------------------------------+
|                                                                |
|  Original probabilities (temperature = 1.0):                  |
|    "mat":   0.35    "floor": 0.20    "couch": 0.12           |
|                                                                |
|  Low temperature (0.2) -- probabilities become more extreme:  |
|    "mat":   0.85    "floor": 0.10    "couch": 0.03           |
|    (The top choice dominates even more)                       |
|                                                                |
|  High temperature (2.0) -- probabilities become more equal:   |
|    "mat":   0.22    "floor": 0.18    "couch": 0.15           |
|    (All choices become more equally likely)                   |
|                                                                |
+--------------------------------------------------------------+
```

### Comparing Different Temperatures

```python
from transformers import pipeline

generator = pipeline("text-generation", model="gpt2")

prompt = "The future of artificial intelligence"

# Generate with different temperatures
temperatures = [0.2, 0.7, 1.0, 1.5]

for temp in temperatures:
    result = generator(
        prompt,
        max_length=50,
        temperature=temp,
        do_sample=True,        # Must be True to use temperature
        num_return_sequences=1
    )
    print(f"Temperature = {temp}:")
    print(f"  {result[0]['generated_text']}")
    print()
```

**Expected output:**

```
Temperature = 0.2:
  The future of artificial intelligence is likely to be shaped by the
  development of more advanced machine learning algorithms and the
  increasing availability of large datasets.

Temperature = 0.7:
  The future of artificial intelligence holds tremendous promise for
  healthcare, education, and scientific discovery, though we must
  carefully consider the ethical implications.

Temperature = 1.0:
  The future of artificial intelligence could reshape everything from
  how we communicate to how cities are designed, creating opportunities
  we haven't yet imagined.

Temperature = 1.5:
  The future of artificial intelligence dances between quantum
  possibilities and crystalline dreams of silicon consciousness
  awakening beneath digital moonlight.
```

**Line-by-line explanation:**
- `temperature=0.2` -- Very low temperature. The model picks the most probable words almost every time. Output is safe but can be boring
- `temperature=0.7` -- A balanced setting. The model mostly picks likely words but occasionally makes creative choices. This is the most commonly used setting
- `temperature=1.0` -- Default temperature. The model uses the original probability distribution
- `temperature=1.5` -- High temperature. The model frequently picks less likely words. Output is creative but may not make sense
- `do_sample=True` -- This is required to use temperature. Without it, the model always picks the most likely word (called "greedy decoding")

---

## 14.3 Top-k Sampling

### What Is Top-k?

Top-k sampling limits the model to choosing from only the k most likely next words. All other words are excluded:

```
+--------------------------------------------------------------+
|        TOP-K SAMPLING (k=3)                                   |
+--------------------------------------------------------------+
|                                                                |
|  Full vocabulary probabilities:                               |
|    mat:   0.35  <-- included (top 3)                          |
|    floor: 0.20  <-- included (top 3)                          |
|    couch: 0.12  <-- included (top 3)                          |
|    bed:   0.10  <-- EXCLUDED                                  |
|    table: 0.08  <-- EXCLUDED                                  |
|    chair: 0.06  <-- EXCLUDED                                  |
|    ...                                                         |
|                                                                |
|  After top-k filtering (k=3):                                 |
|    mat:   0.52  (0.35 / 0.67, renormalized)                   |
|    floor: 0.30  (0.20 / 0.67, renormalized)                   |
|    couch: 0.18  (0.12 / 0.67, renormalized)                   |
|                                                                |
|  The model can only choose from these 3 words.                |
|  This prevents picking very unlikely, weird words.            |
|                                                                |
+--------------------------------------------------------------+
```

### Using Top-k in Practice

```python
from transformers import pipeline

generator = pipeline("text-generation", model="gpt2")

prompt = "The scientist discovered that"

# Compare different k values
k_values = [5, 20, 50, 100]

for k in k_values:
    result = generator(
        prompt,
        max_length=40,
        top_k=k,
        do_sample=True,
        temperature=0.8,
        num_return_sequences=1
    )
    print(f"top_k = {k}:")
    print(f"  {result[0]['generated_text']}")
    print()
```

**Expected output:**

```
top_k = 5:
  The scientist discovered that the new compound could effectively
  reduce inflammation in laboratory tests.

top_k = 20:
  The scientist discovered that ancient bacteria preserved in ice
  could still be revived after thousands of years.

top_k = 50:
  The scientist discovered that gravitational waves from colliding
  neutron stars contained unexpected frequency patterns.

top_k = 100:
  The scientist discovered that bioluminescent algae communicated
  through synchronized light pulses resembling Morse code.
```

**Line-by-line explanation:**
- `top_k=5` -- Only consider the 5 most likely next words at each step. Results are very predictable
- `top_k=20` -- Consider the top 20 words. More variety while staying coherent
- `top_k=50` -- Consider the top 50 words. A common default value
- `top_k=100` -- Consider the top 100 words. More creative but occasionally odd

```
+--------------------------------------------------------------+
|        TOP-K: CHOOSING THE RIGHT VALUE                        |
+--------------------------------------------------------------+
|                                                                |
|  k = 1:   Always picks the most likely word (greedy)          |
|            Very repetitive, but very "safe"                   |
|                                                                |
|  k = 10:  Very conservative, predictable text                |
|                                                                |
|  k = 50:  Good balance (commonly used default)               |
|                                                                |
|  k = 100: More creative, occasionally surprising             |
|                                                                |
|  k = 1000: Almost no filtering, very random                  |
|                                                                |
+--------------------------------------------------------------+
```

---

## 14.4 Top-p (Nucleus) Sampling

### What Is Top-p?

Top-p sampling (also called nucleus sampling) is a smarter alternative to top-k. Instead of always keeping a fixed number of words, it keeps the smallest set of words whose combined probability is at least p:

```
+--------------------------------------------------------------+
|        TOP-P SAMPLING (p=0.9)                                 |
+--------------------------------------------------------------+
|                                                                |
|  Probabilities (sorted highest to lowest):                    |
|    mat:    0.35  cumulative: 0.35  <-- included               |
|    floor:  0.20  cumulative: 0.55  <-- included               |
|    couch:  0.12  cumulative: 0.67  <-- included               |
|    bed:    0.10  cumulative: 0.77  <-- included               |
|    table:  0.08  cumulative: 0.85  <-- included               |
|    chair:  0.06  cumulative: 0.91  <-- included (>= 0.9!)    |
|    roof:   0.04  cumulative: 0.95  <-- EXCLUDED               |
|    ...                                                         |
|                                                                |
|  We keep adding words until cumulative probability >= 0.9     |
|  This gives us 6 words to choose from                        |
|                                                                |
+--------------------------------------------------------------+
```

### Why Top-p Is Better Than Top-k

The advantage of top-p is that it adapts to the situation:

```
+--------------------------------------------------------------+
|        WHY TOP-P ADAPTS BETTER THAN TOP-K                     |
+--------------------------------------------------------------+
|                                                                |
|  Situation 1: Model is very confident                         |
|    "The capital of France is ___"                             |
|    Paris: 0.95, Lyon: 0.03, Marseille: 0.01, ...             |
|    top_p=0.9 --> keeps only "Paris" (1 word)                  |
|    top_k=50 --> keeps 50 words (too many!)                    |
|                                                                |
|  Situation 2: Model is uncertain                              |
|    "For dinner I want to eat ___"                             |
|    pizza: 0.08, pasta: 0.07, sushi: 0.06, ...                |
|    top_p=0.9 --> keeps ~15 words (appropriate variety)        |
|    top_k=50 --> keeps 50 words (still too many)               |
|                                                                |
|  Top-p naturally adjusts the number of choices!               |
|                                                                |
+--------------------------------------------------------------+
```

### Using Top-p in Practice

```python
from transformers import pipeline

generator = pipeline("text-generation", model="gpt2")

prompt = "In a world where robots"

# Compare different p values
p_values = [0.5, 0.7, 0.9, 0.95]

for p in p_values:
    result = generator(
        prompt,
        max_length=40,
        top_p=p,
        do_sample=True,
        temperature=0.8,
        num_return_sequences=1
    )
    print(f"top_p = {p}:")
    print(f"  {result[0]['generated_text']}")
    print()
```

**Expected output:**

```
top_p = 0.5:
  In a world where robots have become an essential part of daily life,
  humans must learn to work alongside their mechanical counterparts.

top_p = 0.7:
  In a world where robots can think and feel, a young engineer builds
  the first machine capable of genuine empathy.

top_p = 0.9:
  In a world where robots govern the ancient forests, one small bird
  discovers a secret that could change everything.

top_p = 0.95:
  In a world where robots dream in watercolors, a forgotten clockwork
  sparrow awakens to find the last human library.
```

### Combining Temperature, Top-k, and Top-p

You can use these parameters together for fine-grained control:

```python
from transformers import pipeline

generator = pipeline("text-generation", model="gpt2")

prompt = "The old library held a secret"

# Combination 1: Conservative (factual, predictable)
result1 = generator(
    prompt, max_length=50,
    temperature=0.3, top_k=10, top_p=0.85,
    do_sample=True, num_return_sequences=1
)

# Combination 2: Balanced (natural, interesting)
result2 = generator(
    prompt, max_length=50,
    temperature=0.7, top_k=50, top_p=0.9,
    do_sample=True, num_return_sequences=1
)

# Combination 3: Creative (surprising, imaginative)
result3 = generator(
    prompt, max_length=50,
    temperature=1.2, top_k=100, top_p=0.95,
    do_sample=True, num_return_sequences=1
)

print("Conservative:")
print(f"  {result1[0]['generated_text']}\n")

print("Balanced:")
print(f"  {result2[0]['generated_text']}\n")

print("Creative:")
print(f"  {result3[0]['generated_text']}\n")
```

```
+--------------------------------------------------------------+
|        RECOMMENDED PARAMETER COMBINATIONS                     |
+--------------------------------------------------------------+
|                                                                |
|  Use Case          | Temp | top_k | top_p | Notes            |
|  ------------------|------|-------|-------|------------------ |
|  Factual writing   | 0.3  |  10   | 0.85  | Safe, accurate   |
|  General text      | 0.7  |  50   | 0.90  | Natural feel     |
|  Creative writing  | 1.0  |  100  | 0.95  | Interesting      |
|  Poetry/fiction    | 1.2  |  150  | 0.95  | Wild, creative   |
|  Code generation   | 0.2  |   5   | 0.80  | Precise, correct |
|                                                                |
+--------------------------------------------------------------+
```

---

## 14.5 Controlling Output Length

### Max Length and Max New Tokens

There are two ways to control how much text is generated:

```python
from transformers import pipeline

generator = pipeline("text-generation", model="gpt2")

prompt = "The weather today"

# Method 1: max_length (total length including prompt)
result1 = generator(prompt, max_length=30, do_sample=True)
print("max_length=30 (total tokens):")
print(f"  {result1[0]['generated_text']}\n")

# Method 2: max_new_tokens (only new tokens, not counting prompt)
result2 = generator(prompt, max_new_tokens=20, do_sample=True)
print("max_new_tokens=20 (new tokens only):")
print(f"  {result2[0]['generated_text']}\n")
```

**Expected output:**

```
max_length=30 (total tokens):
  The weather today is expected to be partly cloudy with temperatures
  reaching the mid-70s in most areas.

max_new_tokens=20 (new tokens only):
  The weather today looks beautiful with clear skies and a gentle
  breeze coming from the west.
```

**Line-by-line explanation:**
- `max_length=30` -- The total output (prompt + generated text) will be at most 30 tokens. If your prompt is 5 tokens, you get at most 25 new tokens
- `max_new_tokens=20` -- Exactly 20 new tokens will be generated, regardless of prompt length. This is often more intuitive to use

### Using Min Length

```python
from transformers import pipeline

generator = pipeline("text-generation", model="gpt2")

prompt = "The meaning of life is"

# Without min_length (model might stop early)
result1 = generator(prompt, max_length=50, do_sample=True)

# With min_length (force the model to write more)
result2 = generator(prompt, max_length=50, min_length=30, do_sample=True)

print("Without min_length:")
print(f"  {result1[0]['generated_text']}\n")

print("With min_length=30:")
print(f"  {result2[0]['generated_text']}\n")
```

---

## 14.6 Repetition Penalty

### The Problem of Repetition

Without a repetition penalty, generation models often get stuck in loops:

```
Without penalty:
"The cat sat on the mat. The cat sat on the mat. The cat sat
 on the mat. The cat sat on the mat."

With penalty:
"The cat sat on the mat. It purred contentedly while watching
 the birds outside the window."
```

### Using Repetition Penalty

```python
from transformers import pipeline

generator = pipeline("text-generation", model="gpt2")

prompt = "Artificial intelligence is"

# Without repetition penalty
result1 = generator(
    prompt, max_length=80,
    do_sample=True, temperature=0.7,
    repetition_penalty=1.0   # 1.0 means no penalty (default)
)

# With repetition penalty
result2 = generator(
    prompt, max_length=80,
    do_sample=True, temperature=0.7,
    repetition_penalty=1.3   # Penalize repeated words/phrases
)

print("No penalty (repetition_penalty=1.0):")
print(f"  {result1[0]['generated_text']}\n")

print("With penalty (repetition_penalty=1.3):")
print(f"  {result2[0]['generated_text']}\n")
```

**Expected output:**

```
No penalty (repetition_penalty=1.0):
  Artificial intelligence is a field of computer science that focuses
  on creating systems that can perform tasks that require human
  intelligence. Artificial intelligence is used in many applications
  that require human intelligence and artificial intelligence is
  becoming more and more important.

With penalty (repetition_penalty=1.3):
  Artificial intelligence is a rapidly evolving field that combines
  computer science with cognitive psychology. Modern applications range
  from medical diagnosis to autonomous vehicles, transforming industries
  and creating new possibilities for human-machine collaboration.
```

**Line-by-line explanation:**
- `repetition_penalty=1.0` -- No penalty. The model can repeat words and phrases freely. This often leads to repetitive, looping text
- `repetition_penalty=1.3` -- Each time a word is generated, its probability of being generated again is divided by 1.3. Higher values mean stronger penalties
- Values between 1.1 and 1.5 work well. Going above 2.0 can make the text incoherent as the model avoids too many common words

```
+--------------------------------------------------------------+
|        REPETITION PENALTY VALUES                              |
+--------------------------------------------------------------+
|                                                                |
|  1.0 = No penalty (default, may cause repetition)             |
|  1.1 = Light penalty (reduces obvious repetition)             |
|  1.3 = Moderate penalty (good default for most tasks)         |
|  1.5 = Strong penalty (good for creative writing)             |
|  2.0 = Very strong (may cause incoherent text)                |
|                                                                |
+--------------------------------------------------------------+
```

---

## 14.7 The generate() Method

### Using generate() Directly

The pipeline wraps the `generate()` method for convenience, but you can use `generate()` directly for maximum control:

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Load model and tokenizer
model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Set the padding token (GPT-2 does not have one by default)
tokenizer.pad_token = tokenizer.eos_token

# Encode the prompt
prompt = "In the year 2050, technology"
inputs = tokenizer(prompt, return_tensors="pt")

# Generate text using the generate() method
with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=50,
        temperature=0.8,
        top_k=50,
        top_p=0.9,
        repetition_penalty=1.2,
        do_sample=True,
        num_return_sequences=3,   # Generate 3 different versions
    )

# Decode and print each generated sequence
print(f"Prompt: {prompt}\n")
for i, output in enumerate(outputs):
    text = tokenizer.decode(output, skip_special_tokens=True)
    # Remove the prompt from the output for clarity
    generated_part = text[len(prompt):]
    print(f"Version {i+1}: {generated_part.strip()}")
    print()
```

**Expected output:**

```
Prompt: In the year 2050, technology

Version 1: will have transformed every aspect of daily life.
Self-driving vehicles will dominate the roads, while AI assistants
manage our homes and personal schedules with remarkable efficiency.

Version 2: has advanced to the point where humans can upload their
consciousness into digital spaces. Virtual reality is indistinguishable
from the physical world, raising profound philosophical questions.

Version 3: enables cities to run entirely on renewable energy. Smart
grids powered by quantum computers optimize power distribution in real
time, eliminating waste and reducing costs dramatically.
```

**Line-by-line explanation:**
- `AutoModelForCausalLM` -- "Causal Language Model" is the technical name for autoregressive text generation models. "Causal" means each token can only see the tokens before it, not after
- `tokenizer.pad_token = tokenizer.eos_token` -- GPT-2 was not trained with a padding token, so we assign the end-of-sequence token as the pad token
- `model.generate(**inputs, ...)` -- The main generation method with full control
- `num_return_sequences=3` -- Generate 3 different versions from the same prompt
- `tokenizer.decode(output, skip_special_tokens=True)` -- Converts the generated token IDs back to readable text, removing special tokens like `<|endoftext|>`

### Generating Multiple Sequences

```python
from transformers import pipeline

generator = pipeline("text-generation", model="gpt2")

prompt = "Three reasons to learn programming:"

# Generate 5 different completions
results = generator(
    prompt,
    max_new_tokens=60,
    num_return_sequences=5,
    do_sample=True,
    temperature=0.8,
    top_p=0.9
)

print(f"Prompt: {prompt}\n")
for i, result in enumerate(results):
    generated = result['generated_text'][len(prompt):].strip()
    print(f"Version {i+1}:")
    print(f"  {generated}")
    print()
```

---

## 14.8 Complete Story Generation Example

### Building a Story Generator

```python
from transformers import pipeline

def generate_story(opening, genre="fantasy", length="medium",
                   creativity=0.7):
    """
    Generate a short story from an opening sentence.

    Parameters:
        opening: The first sentence of the story
        genre: The story genre (used in the prompt)
        length: "short" (50 tokens), "medium" (100), "long" (200)
        creativity: How creative (0.1 = conservative, 1.5 = wild)

    Returns:
        The generated story as a string
    """

    # Map length to max_new_tokens
    length_map = {
        "short": 50,
        "medium": 100,
        "long": 200
    }
    max_tokens = length_map.get(length, 100)

    # Create the prompt with genre context
    prompt = f"[Genre: {genre}]\n\n{opening}"

    # Create the generator
    generator = pipeline("text-generation", model="gpt2")

    # Generate the story
    result = generator(
        prompt,
        max_new_tokens=max_tokens,
        temperature=creativity,
        top_p=0.9,
        top_k=50,
        repetition_penalty=1.3,
        do_sample=True,
        num_return_sequences=1
    )

    # Clean up: remove the genre tag from the output
    story = result[0]['generated_text']
    if story.startswith(f"[Genre: {genre}]\n\n"):
        story = story[len(f"[Genre: {genre}]\n\n"):]

    return story


# Generate stories with different settings
print("=" * 60)
print("STORY 1: Fantasy (Medium creativity)")
print("=" * 60)
story1 = generate_story(
    "The ancient dragon opened one eye as the young knight entered the cave.",
    genre="fantasy",
    length="medium",
    creativity=0.7
)
print(story1)
print()

print("=" * 60)
print("STORY 2: Science Fiction (High creativity)")
print("=" * 60)
story2 = generate_story(
    "The last human on Mars stared at the incoming transmission.",
    genre="science fiction",
    length="medium",
    creativity=1.0
)
print(story2)
print()

print("=" * 60)
print("STORY 3: Mystery (Low creativity, more structured)")
print("=" * 60)
story3 = generate_story(
    "Detective Chen found the missing painting exactly where nobody expected.",
    genre="mystery",
    length="medium",
    creativity=0.4
)
print(story3)
```

**Expected output:**

```
============================================================
STORY 1: Fantasy (Medium creativity)
============================================================
The ancient dragon opened one eye as the young knight entered
the cave. Its scales gleamed like molten gold in the dim light
of the cavern. "You are brave," the dragon rumbled, smoke
curling from its nostrils. "Or perhaps merely foolish." The
knight gripped the hilt of her sword but did not draw it.
"I did not come to fight," she said quietly. "I came to ask
for your help."

============================================================
STORY 2: Science Fiction (High creativity)
============================================================
The last human on Mars stared at the incoming transmission.
The signal pulsed with frequencies that shouldn't exist,
carrying fragments of music from Earth's forgotten symphonies.
She adjusted the antenna array, hands trembling as the message
decoded itself into coordinates pointing beyond the solar
system. Something out there knew she was alive. Something
wanted her to come home -- but not to Earth.

============================================================
STORY 3: Mystery (Low creativity, more structured)
============================================================
Detective Chen found the missing painting exactly where nobody
expected. It was hanging in plain sight in the museum lobby,
hidden behind a reproduction that had been placed over it.
"The thief never took it out of the building," Chen said,
examining the frame. "They simply covered it up and waited for
everyone to stop looking."
```

### A More Advanced Generator with Multiple Options

```python
from transformers import pipeline

def creative_writing_assistant():
    """
    An interactive creative writing assistant that generates text
    with user-specified parameters.
    """
    generator = pipeline("text-generation", model="gpt2")

    # Define preset configurations
    presets = {
        "formal": {
            "temperature": 0.3,
            "top_p": 0.85,
            "top_k": 20,
            "repetition_penalty": 1.2,
            "description": "Professional, structured, predictable"
        },
        "casual": {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 50,
            "repetition_penalty": 1.2,
            "description": "Natural, conversational, balanced"
        },
        "creative": {
            "temperature": 1.0,
            "top_p": 0.95,
            "top_k": 100,
            "repetition_penalty": 1.3,
            "description": "Imaginative, surprising, artistic"
        },
        "wild": {
            "temperature": 1.5,
            "top_p": 0.95,
            "top_k": 200,
            "repetition_penalty": 1.5,
            "description": "Experimental, unpredictable, avant-garde"
        }
    }

    # Generate with all presets for comparison
    prompt = "The old bookshop on the corner"

    print("=== Creative Writing Presets Comparison ===\n")
    print(f"Prompt: \"{prompt}\"\n")

    for name, config in presets.items():
        result = generator(
            prompt,
            max_new_tokens=40,
            temperature=config["temperature"],
            top_p=config["top_p"],
            top_k=config["top_k"],
            repetition_penalty=config["repetition_penalty"],
            do_sample=True,
            num_return_sequences=1
        )

        generated = result[0]['generated_text'][len(prompt):].strip()
        print(f"[{name.upper()}] ({config['description']})")
        print(f"  {prompt} {generated}")
        print()


# Run the comparison
creative_writing_assistant()
```

---

## 14.9 Prompt Engineering Basics

### What Is Prompt Engineering?

Prompt engineering is the art of crafting your input text to get better results from a generation model. The prompt is your instruction to the model -- and how you phrase it matters enormously:

```
+--------------------------------------------------------------+
|        PROMPT ENGINEERING PRINCIPLES                          |
+--------------------------------------------------------------+
|                                                                |
|  1. BE SPECIFIC                                               |
|     Bad:  "Write something about dogs"                        |
|     Good: "Write a paragraph describing a golden retriever    |
|            playing fetch in a park on a sunny afternoon"       |
|                                                                |
|  2. PROVIDE CONTEXT                                           |
|     Bad:  "Continue this story"                               |
|     Good: "Continue this fantasy story about a wizard:        |
|            [your story beginning]"                             |
|                                                                |
|  3. USE EXAMPLES (FEW-SHOT)                                   |
|     "Translate English to French:                              |
|      Hello -> Bonjour                                         |
|      Goodbye -> Au revoir                                     |
|      Thank you ->"                                            |
|                                                                |
|  4. SET THE TONE                                              |
|     "Write in a formal, academic style:"                      |
|     "Write in a casual, friendly tone:"                       |
|                                                                |
+--------------------------------------------------------------+
```

### Prompt Examples

```python
from transformers import pipeline

generator = pipeline("text-generation", model="gpt2")

# Example 1: Few-shot learning through prompts
prompt_fewshot = """Convert the following movie reviews to one-word sentiment:

Review: "This movie was absolutely wonderful!"
Sentiment: Positive

Review: "Terrible acting and boring plot."
Sentiment: Negative

Review: "A masterpiece of modern cinema."
Sentiment:"""

result = generator(prompt_fewshot, max_new_tokens=5, do_sample=False)
print("Few-shot example:")
print(result[0]['generated_text'])
print()

# Example 2: Structured output through prompts
prompt_structured = """Product: Wireless Bluetooth Headphones
Price: $49.99
Rating: 4.5/5 stars

Write a short product description:
These premium wireless Bluetooth headphones offer"""

result = generator(prompt_structured, max_new_tokens=40,
                   temperature=0.7, do_sample=True)
print("Structured prompt:")
print(result[0]['generated_text'])
print()

# Example 3: Style-specific prompt
prompt_style = """Write in the style of a nature documentary narrator:

The camera slowly pans across the African savanna at dawn."""

result = generator(prompt_style, max_new_tokens=50,
                   temperature=0.8, do_sample=True)
print("Style prompt:")
print(result[0]['generated_text'])
```

### Prompt Engineering Tips

```
+--------------------------------------------------------------+
|        PROMPT ENGINEERING TIPS                                |
+--------------------------------------------------------------+
|                                                                |
|  DO:                                                           |
|    + Be specific about what you want                          |
|    + Provide examples of desired output format                |
|    + Set the tone and style explicitly                        |
|    + Include relevant context                                 |
|    + Use clear separators between sections                    |
|                                                                |
|  DO NOT:                                                       |
|    - Use vague instructions ("write something good")          |
|    - Assume the model knows your intent                       |
|    - Use very short prompts for complex tasks                 |
|    - Forget that the model continues YOUR text                |
|    - Expect perfect results on the first try                  |
|                                                                |
+--------------------------------------------------------------+
```

---

## Common Mistakes

1. **Forgetting `do_sample=True`.** Temperature, top-k, and top-p only work when sampling is enabled. Without `do_sample=True`, the model always picks the most likely word regardless of your settings.

2. **Setting temperature to 0.** A temperature of exactly 0 causes division by zero errors in some implementations. Use a very small value like 0.01 instead, or set `do_sample=False` for greedy decoding.

3. **Confusing `max_length` and `max_new_tokens`.** `max_length` includes the prompt in its count; `max_new_tokens` does not. Using `max_length=20` with a 15-token prompt gives you only 5 new tokens.

4. **Using too high a repetition penalty.** Values above 2.0 can make the model avoid common words entirely, producing incoherent text. Stay between 1.1 and 1.5 for most use cases.

5. **Not setting a pad token for GPT-2.** GPT-2 does not have a pad token by default. When generating multiple sequences, you must set `tokenizer.pad_token = tokenizer.eos_token`.

---

## Best Practices

1. **Start with balanced settings.** Begin with temperature=0.7, top_p=0.9, and repetition_penalty=1.2. Adjust from there based on results.

2. **Use `max_new_tokens` instead of `max_length`.** It is more intuitive and avoids confusion about prompt length.

3. **Generate multiple versions.** Use `num_return_sequences=3` or more, then pick the best result. Generation is inherently random, so more attempts give better odds.

4. **Invest time in prompt engineering.** A well-crafted prompt often matters more than parameter tuning. Experiment with different prompt formats.

5. **Use repetition penalty for longer texts.** For outputs longer than 50 tokens, always set `repetition_penalty` between 1.1 and 1.3 to avoid loops.

---

## Quick Summary

Text generation works by predicting one token at a time, with each prediction based on all previous tokens (autoregressive generation). Temperature controls randomness -- low values produce predictable text, high values produce creative text. Top-k sampling limits choices to the k most likely tokens, while top-p (nucleus) sampling adapts the number of choices based on the probability distribution. Repetition penalty prevents the model from getting stuck in loops. The Hugging Face `generate()` method provides full control over all these parameters. Good prompt engineering -- being specific, providing examples, and setting the tone -- is often more important than parameter tuning.

---

## Key Points

- Autoregressive generation predicts one token at a time, feeding each prediction back as input
- Temperature controls randomness: low (0.2) is predictable, high (1.5) is creative, medium (0.7) is balanced
- Top-k sampling keeps only the k most likely tokens at each step
- Top-p (nucleus) sampling adapts the number of choices to the model's confidence -- preferred over top-k
- Always set `do_sample=True` when using temperature, top-k, or top-p
- Use `max_new_tokens` instead of `max_length` for clearer control over output length
- Repetition penalty (1.1-1.5) prevents the model from generating repetitive loops
- Generate multiple sequences and pick the best one
- Prompt engineering (being specific, providing examples) is as important as parameter tuning

---

## Practice Questions

1. Explain the difference between greedy decoding and sampling. When would you use each approach?

2. You want to generate a formal business email. What temperature, top-k, and top-p values would you choose, and why?

3. What is the advantage of top-p sampling over top-k sampling? Give an example where top-k would include too many or too few words.

4. Your text generation model keeps producing the same sentence over and over. What parameter would you adjust, and what value would you set?

5. Explain what `max_length=50` and `max_new_tokens=50` mean. If your prompt is 20 tokens long, how many new tokens would each setting generate?

---

## Exercises

### Exercise 1: Temperature Explorer

Write a program that generates text from the same prompt at 5 different temperatures (0.1, 0.5, 0.7, 1.0, and 1.5). For each temperature, generate 3 sequences. Print all results in a neatly formatted table. Observe how the text changes with temperature.

### Exercise 2: Build a Creative Writing Tool

Create a function called `write_with_style` that takes a prompt and a style parameter (one of: "academic", "poetic", "journalistic", "humorous"). The function should adjust the generation parameters and add style-specific instructions to the prompt to produce text matching the requested style.

### Exercise 3: Story Chain Generator

Build a program that generates a story in 5 paragraphs. Each paragraph uses the last sentence of the previous paragraph as its prompt. Start with a single opening sentence. Use different creativity levels for different paragraphs (lower creativity for the introduction and conclusion, higher for the middle).

---

## What Is Next?

You now know how to generate text in one language. But the world speaks thousands of languages. In the next chapter, we will explore **multilingual NLP** -- how modern models can understand and process text in many languages simultaneously. You will learn about cross-lingual models like mBERT and XLM-RoBERTa, translation pipelines, language detection, and the unique challenges of building NLP systems that work across languages and cultures.
