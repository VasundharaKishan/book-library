# Chapter 8: Sequence-to-Sequence Models — Turning One Sequence into Another

## What You Will Learn

- What sequence-to-sequence (seq2seq) models are and why they matter
- How the encoder-decoder architecture works step by step
- What machine translation is and how seq2seq models handle it
- What teacher forcing is and why it speeds up training
- How the attention mechanism solves the bottleneck problem
- Using the Hugging Face translation pipeline for easy translation
- A complete translation example with multiple language pairs

## Why This Chapter Matters

Imagine you are a translator who speaks both English and French. When someone speaks an English sentence to you, your brain does two things: first, you understand (encode) the full English sentence, then you produce (decode) the French translation word by word. This is exactly how sequence-to-sequence models work.

Seq2seq models are the backbone of modern AI. They power machine translation (Google Translate), text summarization (which you learned in the last chapter), chatbots, speech recognition, and even image captioning. The encoder-decoder architecture is one of the most important ideas in deep learning, and it led directly to the Transformer architecture that drives today's AI revolution.

Understanding seq2seq models gives you the foundation to understand BERT, GPT, and every other modern language model. This chapter is a gateway to the most exciting developments in AI.

---

## 8.1 What Is a Sequence-to-Sequence Task?

A **sequence-to-sequence** (seq2seq) task takes a sequence of items as input and produces a different sequence of items as output. The input and output can have different lengths.

The word **sequence** means an ordered list of items. In NLP, a sequence is usually a series of words forming a sentence. **Seq2seq** is short for "sequence-to-sequence."

```
+------------------------------------------------------------------+
|              Sequence-to-Sequence Tasks                           |
+------------------------------------------------------------------+
|                                                                   |
|  Task                 | Input Sequence     | Output Sequence      |
|  ---------------------|--------------------|--------------------- |
|  Translation          | "I love cats"      | "J'aime les chats"  |
|  Summarization        | Long article       | Short summary        |
|  Question Answering   | Question + Context | Answer               |
|  Chatbot              | User message       | Bot response         |
|  Speech Recognition   | Audio waveform     | Text transcript      |
|  Image Captioning     | Image pixels       | Text description     |
|                                                                   |
|  Key insight: Input and output lengths can be DIFFERENT.          |
|  "I love cats" (3 words) --> "J'aime les chats" (3 words)       |
|  "How are you" (3 words) --> "Comment allez-vous" (2 words)     |
|                                                                   |
+------------------------------------------------------------------+
```

This is different from tasks like text classification, where the input is a sequence but the output is a single label. In seq2seq, both the input AND the output are sequences.

---

## 8.2 The Encoder-Decoder Architecture

The **encoder-decoder** architecture is the core design pattern for seq2seq models. Think of it like a two-step process:

1. **Encoder**: Reads the entire input sequence and compresses it into a fixed-size representation (like reading a book and forming a mental understanding)
2. **Decoder**: Takes that representation and generates the output sequence one element at a time (like writing a summary from your mental understanding)

```
+------------------------------------------------------------------+
|         The Encoder-Decoder Architecture                          |
+------------------------------------------------------------------+
|                                                                   |
|  Input: "The cat sat"                                             |
|                                                                   |
|  ENCODER (reads input left to right):                             |
|                                                                   |
|  "The" --> [h1] --> "cat" --> [h2] --> "sat" --> [h3]            |
|                                                                   |
|  h1, h2, h3 are "hidden states" — the encoder's internal         |
|  understanding at each step.                                      |
|                                                                   |
|  The final hidden state [h3] is called the "context vector."     |
|  It summarizes the ENTIRE input sequence into one vector.         |
|                                                                   |
|                     [h3] = Context Vector                         |
|                          |                                        |
|                          v                                        |
|                                                                   |
|  DECODER (generates output left to right):                        |
|                                                                   |
|  [h3] --> "Le" --> "chat" --> "assis" --> <END>                  |
|                                                                   |
|  The decoder uses the context vector to generate each             |
|  output word, one at a time, until it produces an end token.     |
|                                                                   |
+------------------------------------------------------------------+
```

### Hidden States

A **hidden state** is a vector (a list of numbers) that represents what the model has learned so far. Think of it as the model's "memory" at each time step.

As the encoder reads each input word, it updates its hidden state. After reading "The," the hidden state captures the meaning of "The." After reading "cat," it captures "The cat." After reading "sat," it captures the meaning of the entire sentence "The cat sat." This final hidden state is called the **context vector**.

### The Context Vector

The **context vector** is the final hidden state of the encoder. It is a fixed-size vector (for example, a list of 256 or 512 numbers) that tries to capture the meaning of the entire input sequence.

Think of the context vector like a zip file — it compresses all the information from a long input into a compact representation. The decoder then "unzips" this representation to generate the output.

```
+------------------------------------------------------------------+
|              The Context Vector                                   |
+------------------------------------------------------------------+
|                                                                   |
|  Input sentence: "I love learning about artificial intelligence" |
|  (6 words)                                                        |
|                                                                   |
|        Encoder processes word by word:                            |
|        "I" -> "love" -> "learning" -> "about" -> "artificial"   |
|        -> "intelligence"                                          |
|                                                                   |
|        Final hidden state = Context Vector                        |
|        [0.23, -0.45, 0.89, 0.12, ..., -0.67]                    |
|        (a vector of, say, 512 numbers)                           |
|                                                                   |
|  This single vector must capture the ENTIRE meaning of the       |
|  input sentence. This is hard for very long sentences!            |
|                                                                   |
+------------------------------------------------------------------+
```

### Building a Simple Encoder-Decoder in PyTorch

Let us build a simple seq2seq model to see how the pieces fit together:

```python
# A simple encoder-decoder model in PyTorch

import torch
import torch.nn as nn

class Encoder(nn.Module):
    """
    The encoder reads the input sequence and produces a context vector.
    It uses an RNN (Recurrent Neural Network) to process the sequence.
    """

    def __init__(self, input_size, embedding_size, hidden_size):
        super().__init__()
        # Embedding layer: converts word indices to dense vectors
        # Think of it as a lookup table where each word has a vector
        self.embedding = nn.Embedding(input_size, embedding_size)

        # GRU layer: processes the sequence step by step
        # GRU = Gated Recurrent Unit (a type of RNN)
        self.rnn = nn.GRU(embedding_size, hidden_size, batch_first=True)

    def forward(self, x):
        # x shape: (batch_size, sequence_length)
        # Each element is a word index like 42 meaning "cat"

        # Convert word indices to vectors
        embedded = self.embedding(x)
        # embedded shape: (batch_size, sequence_length, embedding_size)

        # Process through the RNN
        outputs, hidden = self.rnn(embedded)
        # outputs: hidden states for ALL time steps
        # hidden: the FINAL hidden state (this is our context vector)

        return outputs, hidden


class Decoder(nn.Module):
    """
    The decoder takes the context vector and generates the output
    sequence one word at a time.
    """

    def __init__(self, output_size, embedding_size, hidden_size):
        super().__init__()
        self.embedding = nn.Embedding(output_size, embedding_size)
        self.rnn = nn.GRU(embedding_size, hidden_size, batch_first=True)

        # Linear layer: converts hidden state to word probabilities
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x, hidden):
        # x shape: (batch_size, 1) - one word at a time
        # hidden: the context vector from the encoder

        embedded = self.embedding(x)
        output, hidden = self.rnn(embedded, hidden)

        # Convert hidden state to a probability for each possible word
        prediction = self.fc(output)

        return prediction, hidden


class Seq2Seq(nn.Module):
    """
    The complete seq2seq model combining encoder and decoder.
    """

    def __init__(self, encoder, decoder):
        super().__init__()
        self.encoder = encoder
        self.decoder = decoder

    def forward(self, source, target):
        # source: input sequence (e.g., English sentence)
        # target: output sequence (e.g., French sentence)

        batch_size = source.shape[0]
        target_length = target.shape[1]
        target_vocab_size = self.decoder.fc.out_features

        # Store decoder outputs
        outputs = torch.zeros(batch_size, target_length, target_vocab_size)

        # Step 1: Encode the input sequence
        _, hidden = self.encoder(source)
        # hidden is now the context vector

        # Step 2: Decode one word at a time
        # Start with the first target word
        decoder_input = target[:, 0:1]  # First word (usually <START>)

        for t in range(1, target_length):
            # Generate next word prediction
            output, hidden = self.decoder(decoder_input, hidden)
            outputs[:, t:t+1, :] = output

            # Use the actual next target word as input (teacher forcing)
            decoder_input = target[:, t:t+1]

        return outputs


# Create the model
INPUT_VOCAB_SIZE = 5000    # Number of words in source language
OUTPUT_VOCAB_SIZE = 6000   # Number of words in target language
EMBEDDING_SIZE = 256       # Size of word vectors
HIDDEN_SIZE = 512          # Size of hidden states

encoder = Encoder(INPUT_VOCAB_SIZE, EMBEDDING_SIZE, HIDDEN_SIZE)
decoder = Decoder(OUTPUT_VOCAB_SIZE, EMBEDDING_SIZE, HIDDEN_SIZE)
model = Seq2Seq(encoder, decoder)

# Show model summary
total_params = sum(p.numel() for p in model.parameters())
print("Seq2Seq Model Architecture")
print("=" * 50)
print(f"Input vocabulary size:  {INPUT_VOCAB_SIZE}")
print(f"Output vocabulary size: {OUTPUT_VOCAB_SIZE}")
print(f"Embedding size:         {EMBEDDING_SIZE}")
print(f"Hidden size:            {HIDDEN_SIZE}")
print(f"Total parameters:       {total_params:,}")

# Test with dummy data
source = torch.randint(0, INPUT_VOCAB_SIZE, (2, 10))   # batch=2, length=10
target = torch.randint(0, OUTPUT_VOCAB_SIZE, (2, 12))   # batch=2, length=12

output = model(source, target)
print(f"\nInput shape:  {source.shape}  (batch_size=2, source_length=10)")
print(f"Target shape: {target.shape}  (batch_size=2, target_length=12)")
print(f"Output shape: {output.shape}  (batch_size=2, target_length=12, vocab_size={OUTPUT_VOCAB_SIZE})")
```

**Expected Output:**
```
Seq2Seq Model Architecture
==================================================
Input vocabulary size:  5000
Output vocabulary size: 6000
Embedding size:         256
Hidden size:            512
Total parameters:       7,679,464

Input shape:  torch.Size([2, 10])  (batch_size=2, source_length=10)
Target shape: torch.Size([2, 12])  (batch_size=2, target_length=12)
Output shape: torch.Size([2, 12, 6000])  (batch_size=2, target_length=12, vocab_size=6000)
```

Let us trace through the key parts:

- **Encoder.__init__**: Creates an embedding layer to convert word indices into dense vectors, and a GRU layer to process the sequence. **GRU** (Gated Recurrent Unit) is a type of recurrent neural network that maintains a hidden state as it processes each word
- **Encoder.forward**: Takes word indices, converts them to embeddings, and passes them through the GRU. Returns all hidden states and the final hidden state (context vector)
- **Decoder.__init__**: Similar to encoder, plus a linear layer (`fc`) that converts hidden states to word probabilities
- **Decoder.forward**: Takes one word and the previous hidden state, produces a prediction for the next word and an updated hidden state
- **Seq2Seq.forward**: First encodes the entire input, then decodes one word at a time using the context vector

---

## 8.3 Machine Translation — A Key Seq2Seq Application

**Machine translation** is the task of automatically converting text from one language to another. It is the most well-known application of seq2seq models.

```
+------------------------------------------------------------------+
|              Machine Translation                                  |
+------------------------------------------------------------------+
|                                                                   |
|  English:  "The weather is beautiful today"                      |
|  French:   "Le temps est magnifique aujourd'hui"                 |
|  Spanish:  "El clima es hermoso hoy"                             |
|  German:   "Das Wetter ist heute schoen"                         |
|                                                                   |
|  Challenges:                                                      |
|  1. Word order differs between languages                          |
|     English: "I eat an apple"                                    |
|     Japanese: "I apple eat" (verb at end)                        |
|                                                                   |
|  2. One word may map to multiple words                            |
|     English: "I am" --> Spanish: "Yo soy" (or just "soy")       |
|                                                                   |
|  3. Gender and agreement                                          |
|     English: "The red car" (no gender)                           |
|     French: "La voiture rouge" (feminine)                        |
|     Spanish: "El coche rojo" (masculine)                         |
|                                                                   |
|  4. Idioms don't translate word by word                          |
|     English: "It's raining cats and dogs"                        |
|     French: "Il pleut des cordes" ("It rains ropes")            |
|                                                                   |
+------------------------------------------------------------------+
```

Machine translation is hard because languages have different word orders, grammar rules, and idioms. A seq2seq model handles this by learning the patterns during training, rather than using hand-coded rules.

---

## 8.4 Teacher Forcing — Training the Decoder

When training a seq2seq model, we face a question: when the decoder generates one word, should we use that generated word as input for the next step, or should we use the correct (target) word?

**Teacher forcing** is a training technique where we feed the decoder the correct target word at each step, even if it predicted wrong at the previous step.

```
+------------------------------------------------------------------+
|              Teacher Forcing vs. Free Running                     |
+------------------------------------------------------------------+
|                                                                   |
|  Target translation: "Le chat dort" (The cat sleeps)             |
|                                                                   |
|  WITHOUT Teacher Forcing (Free Running):                          |
|  Step 1: Input=<START>  --> Predicted="Le"    (correct!)         |
|  Step 2: Input="Le"     --> Predicted="chien" (wrong! "dog")     |
|  Step 3: Input="chien"  --> Predicted="mange" (wrong! "eats")    |
|  The error snowballs! One mistake causes more mistakes.           |
|                                                                   |
|  WITH Teacher Forcing:                                            |
|  Step 1: Input=<START>  --> Predicted="Le"    (correct!)         |
|  Step 2: Input="chat"   --> Predicted="dort"  (correct!)         |
|  Step 3: Input="dort"   --> Predicted=<END>   (correct!)         |
|  Even if Step 1 was wrong, Step 2 gets the CORRECT input.        |
|  This prevents error accumulation during training.                |
|                                                                   |
+------------------------------------------------------------------+
```

The word "teacher" in teacher forcing refers to the training data acting like a teacher who corrects the student at each step. Instead of letting the student's mistakes pile up, the teacher provides the right answer so the student can learn the correct pattern.

```python
# Demonstrating teacher forcing concept

import torch

def demonstrate_teacher_forcing():
    """
    Show the difference between teacher forcing and free running.
    This is a conceptual demonstration, not a real model.
    """

    # Pretend these are our target words (what we want the model to output)
    target_words = ["<START>", "Le", "chat", "dort", "<END>"]

    # Pretend predictions (some correct, some wrong)
    model_predictions = ["Le", "chien", "mange", "vite", "<END>"]

    print("Teacher Forcing (uses correct target at each step):")
    print("=" * 55)
    for step in range(len(target_words) - 1):
        input_word = target_words[step]      # Always use correct word
        target_word = target_words[step + 1]  # What we want
        predicted = model_predictions[step]    # What model says
        correct = "YES" if predicted == target_word else "NO"
        print(f"  Step {step + 1}: Input='{input_word}' "
              f"--> Target='{target_word}', "
              f"Predicted='{predicted}' "
              f"(Correct: {correct})")

    print()
    print("Free Running (uses model's own prediction at each step):")
    print("=" * 55)
    current_input = "<START>"
    for step in range(len(target_words) - 1):
        target_word = target_words[step + 1]
        predicted = model_predictions[step]
        correct = "YES" if predicted == target_word else "NO"
        print(f"  Step {step + 1}: Input='{current_input}' "
              f"--> Target='{target_word}', "
              f"Predicted='{predicted}' "
              f"(Correct: {correct})")
        current_input = predicted  # Use the prediction as next input

demonstrate_teacher_forcing()
```

**Expected Output:**
```
Teacher Forcing (uses correct target at each step):
=======================================================
  Step 1: Input='<START>' --> Target='Le', Predicted='Le' (Correct: YES)
  Step 2: Input='Le' --> Target='chat', Predicted='chien' (Correct: NO)
  Step 3: Input='chat' --> Target='dort', Predicted='mange' (Correct: NO)
  Step 4: Input='dort' --> Target='<END>', Predicted='vite' (Correct: NO)

Free Running (uses model's own prediction at each step):
=======================================================
  Step 1: Input='<START>' --> Target='Le', Predicted='Le' (Correct: YES)
  Step 2: Input='Le' --> Target='chat', Predicted='chien' (Correct: NO)
  Step 3: Input='chien' --> Target='dort', Predicted='mange' (Correct: NO)
  Step 4: Input='mange' --> Target='<END>', Predicted='vite' (Correct: NO)
```

### Teacher Forcing Ratio

In practice, we use a **teacher forcing ratio** — a probability that determines whether to use teacher forcing at each step. A ratio of 1.0 means always use teacher forcing. A ratio of 0.0 means never use it. A common strategy is to start with a high ratio (0.9) and gradually decrease it during training.

```
+------------------------------------------------------------------+
|              Teacher Forcing Ratio                                |
+------------------------------------------------------------------+
|                                                                   |
|  Ratio = 1.0: Always use correct target (pure teacher forcing)   |
|  Ratio = 0.5: 50% chance of using target, 50% using prediction  |
|  Ratio = 0.0: Always use model's prediction (free running)       |
|                                                                   |
|  Training Strategy:                                               |
|  Epoch 1-5:   ratio = 1.0 (learn basic patterns)                |
|  Epoch 5-10:  ratio = 0.7 (start using own predictions)         |
|  Epoch 10-15: ratio = 0.5 (balanced)                             |
|  Epoch 15-20: ratio = 0.3 (mostly self-reliant)                 |
|                                                                   |
|  This gradual reduction is called "scheduled sampling."          |
|                                                                   |
+------------------------------------------------------------------+
```

---

## 8.5 The Attention Mechanism — Solving the Bottleneck

The basic encoder-decoder model has a serious problem: the **context vector bottleneck**. The entire input sequence must be compressed into a single fixed-size vector. For short sentences, this works fine. For long sentences or paragraphs, too much information is lost.

```
+------------------------------------------------------------------+
|              The Bottleneck Problem                               |
+------------------------------------------------------------------+
|                                                                   |
|  Short sentence (works well):                                     |
|  "I eat" --> [context vector] --> "Je mange"                     |
|  Only 2 words to compress. Easy!                                 |
|                                                                   |
|  Long sentence (problematic):                                     |
|  "The incredibly talented young musician from the small           |
|   town in southern France played a beautiful melody on            |
|   her antique violin at the prestigious concert last evening"    |
|                                                                   |
|  --> [context vector] (same size as before!)                     |
|                                                                   |
|  25 words squeezed into the SAME size vector.                    |
|  Important details get lost!                                      |
|                                                                   |
+------------------------------------------------------------------+
```

### How Attention Works

**Attention** solves the bottleneck by letting the decoder look back at ALL encoder hidden states, not just the final one. At each decoding step, the decoder decides which parts of the input are most relevant for generating the current output word.

Think of attention like a spotlight. When translating "The cat sat on the mat," and the decoder is generating the French word for "cat" ("chat"), the attention spotlight shines brightest on the encoder's representation of "cat" in the input.

```
+------------------------------------------------------------------+
|              The Attention Mechanism                              |
+------------------------------------------------------------------+
|                                                                   |
|  Input:  "The  cat  sat  on  the  mat"                           |
|  Output: "Le   chat ..."                                         |
|                                                                   |
|  Encoder hidden states: [h1] [h2] [h3] [h4] [h5] [h6]          |
|                          The  cat  sat  on   the  mat             |
|                                                                   |
|  When decoder generates "chat" (cat):                             |
|                                                                   |
|  Attention weights:                                               |
|  [h1] [h2] [h3] [h4] [h5] [h6]                                  |
|  0.05 0.80 0.05 0.02 0.05 0.03   <-- weights sum to 1.0         |
|       ^^^^                                                        |
|       The decoder "pays attention" mostly to h2 ("cat")          |
|                                                                   |
|  Context for "chat" = 0.05*h1 + 0.80*h2 + 0.05*h3 + ...        |
|                                                                   |
|  This weighted sum gives a FOCUSED context vector                |
|  specifically for generating this word.                           |
|                                                                   |
+------------------------------------------------------------------+
```

### Attention Step by Step

```
+------------------------------------------------------------------+
|              Attention Calculation Steps                          |
+------------------------------------------------------------------+
|                                                                   |
|  Step 1: SCORE                                                    |
|  Calculate how relevant each encoder state is to the current      |
|  decoder state.                                                   |
|  score(h_i, s_j) = how related is encoder state i to             |
|                    decoder state j                                |
|                                                                   |
|  Step 2: NORMALIZE (Softmax)                                     |
|  Convert scores to probabilities that sum to 1.                  |
|  attention_weights = softmax(scores)                              |
|                                                                   |
|  Step 3: WEIGHTED SUM                                             |
|  Multiply each encoder state by its attention weight and sum.    |
|  context = sum(weight_i * h_i)                                   |
|                                                                   |
|  Step 4: COMBINE                                                  |
|  Concatenate the context with the decoder state.                 |
|  Use this combined vector to predict the next word.              |
|                                                                   |
+------------------------------------------------------------------+
```

```python
# Demonstrating attention weights conceptually

import torch
import torch.nn.functional as F

def demonstrate_attention():
    """
    Show how attention weights focus on different input words
    when generating different output words.
    """

    # Input words (English)
    input_words = ["The", "black", "cat", "sat", "on", "the", "mat"]

    # Output words (French)
    output_words = ["Le", "chat", "noir", "etait", "assis", "sur", "le", "tapis"]

    # Simulated attention weights for each output word
    # Each row shows where the decoder "looks" when generating that word
    attention_data = {
        "Le":     [0.60, 0.05, 0.05, 0.05, 0.10, 0.10, 0.05],
        "chat":   [0.05, 0.10, 0.70, 0.05, 0.02, 0.03, 0.05],
        "noir":   [0.03, 0.75, 0.10, 0.02, 0.02, 0.03, 0.05],
        "etait":  [0.05, 0.05, 0.10, 0.60, 0.05, 0.05, 0.10],
        "assis":  [0.03, 0.02, 0.05, 0.70, 0.05, 0.05, 0.10],
        "sur":    [0.02, 0.02, 0.03, 0.05, 0.75, 0.08, 0.05],
        "le":     [0.05, 0.03, 0.02, 0.05, 0.10, 0.65, 0.10],
        "tapis":  [0.02, 0.03, 0.02, 0.03, 0.05, 0.05, 0.80],
    }

    print("Attention Weights Visualization")
    print("=" * 65)
    print()
    print(f"{'Output':<10}", end="")
    for word in input_words:
        print(f"{word:<10}", end="")
    print()
    print("-" * 80)

    for out_word, weights in attention_data.items():
        print(f"{out_word:<10}", end="")
        for w in weights:
            # Show high weights with stars for visibility
            bar = "*" * int(w * 20)
            print(f"{bar:<10}", end="")
        print()

    print()
    print("Key insight: When generating 'chat' (cat), the model")
    print("focuses heavily on the input word 'cat' (weight=0.70).")
    print("When generating 'noir' (black), it focuses on 'black' (0.75).")
    print("This is the attention mechanism at work!")

demonstrate_attention()
```

**Expected Output:**
```
Attention Weights Visualization
=================================================================

Output    The       black     cat       sat       on        the       mat
--------------------------------------------------------------------------------
Le        ************                            **        **
chat      *         **        **************       *                   *
noir                ***************       **                           *
etait     *         *         **        *************                  **
assis               *         *         **************                 **
sur                           *         *         ***************      *
le        *                             *         **        *************
tapis                                             *         *         ****************

Key insight: When generating 'chat' (cat), the model
focuses heavily on the input word 'cat' (weight=0.70).
When generating 'noir' (black), it focuses on 'black' (0.75).
This is the attention mechanism at work!
```

Notice an interesting pattern: in English, "black cat" is adjective-noun order, but in French it is "chat noir" (noun-adjective). The attention mechanism handles this naturally — when generating "chat," it looks at "cat," and when generating "noir," it looks at "black." The model learns these reordering patterns from data.

---

## 8.6 Using the Hugging Face Translation Pipeline

Just like with summarization, Hugging Face provides an easy-to-use pipeline for translation. You do not need to build models from scratch — pre-trained models handle all the complexity.

```python
# Machine translation with Hugging Face

from transformers import pipeline

# Create a translation pipeline (English to French)
translator_en_fr = pipeline(
    "translation",
    model="Helsinki-NLP/opus-mt-en-fr"
)

# Translate some English sentences to French
sentences = [
    "Hello, how are you today?",
    "The weather is beautiful this morning.",
    "I love learning about artificial intelligence.",
    "Where is the nearest train station?",
    "Thank you for your help."
]

print("English to French Translation")
print("=" * 60)

for sentence in sentences:
    result = translator_en_fr(sentence)
    translation = result[0]['translation_text']
    print(f"\n  English: {sentence}")
    print(f"  French:  {translation}")
```

**Expected Output:**
```
English to French Translation
============================================================

  English: Hello, how are you today?
  French:  Bonjour, comment allez-vous aujourd'hui ?

  English: The weather is beautiful this morning.
  French:  Le temps est magnifique ce matin.

  English: I love learning about artificial intelligence.
  French:  J'adore apprendre l'intelligence artificielle.

  English: Where is the nearest train station?
  French:  Où est la gare la plus proche ?

  English: Thank you for your help.
  French:  Merci de votre aide.
```

Let us trace through the code:

- **Line 3:** Import the `pipeline` function from `transformers`
- **Lines 6-9:** Create a translation pipeline. `"translation"` specifies the task. `model="Helsinki-NLP/opus-mt-en-fr"` specifies the OPUS-MT model for English-to-French translation. OPUS-MT is a collection of translation models trained on the OPUS parallel corpus (millions of translated sentence pairs)
- **Lines 12-18:** Define the English sentences we want to translate
- **Lines 23-26:** For each sentence, we call the translator. It returns a list of dictionaries, each with a `'translation_text'` key

### Translating Between Multiple Languages

```python
# Translating between multiple language pairs

from transformers import pipeline

# Create pipelines for different language pairs
translators = {
    "English -> French": pipeline("translation", model="Helsinki-NLP/opus-mt-en-fr"),
    "English -> German": pipeline("translation", model="Helsinki-NLP/opus-mt-en-de"),
    "English -> Spanish": pipeline("translation", model="Helsinki-NLP/opus-mt-en-es"),
    "French -> English": pipeline("translation", model="Helsinki-NLP/opus-mt-fr-en"),
}

# The sentence to translate
text = "Artificial intelligence is changing the world."

print("Multi-Language Translation")
print("=" * 60)
print(f"\nOriginal (English): {text}\n")

for direction, translator in translators.items():
    result = translator(text)
    print(f"  {direction}:")
    print(f"    {result[0]['translation_text']}")
    print()
```

**Expected Output:**
```
Multi-Language Translation
============================================================

Original (English): Artificial intelligence is changing the world.

  English -> French:
    L'intelligence artificielle change le monde.

  English -> German:
    Kuenstliche Intelligenz veraendert die Welt.

  English -> Spanish:
    La inteligencia artificial esta cambiando el mundo.

  French -> English:
    Artificial intelligence is changing the world.
```

Notice the round-trip: translating to French and then back to English produces the original sentence. This is a good sign that the translation models are accurate.

---

## 8.7 Complete Translation Example

Let us build a more complete translation application that handles multiple sentences and provides helpful formatting:

```python
# Complete translation application

from transformers import pipeline

class SimpleTranslator:
    """
    A simple translation tool that supports multiple language pairs.
    """

    # Mapping of language pair names to model names
    MODELS = {
        ("en", "fr"): "Helsinki-NLP/opus-mt-en-fr",
        ("en", "de"): "Helsinki-NLP/opus-mt-en-de",
        ("en", "es"): "Helsinki-NLP/opus-mt-en-es",
        ("en", "it"): "Helsinki-NLP/opus-mt-en-it",
        ("fr", "en"): "Helsinki-NLP/opus-mt-fr-en",
        ("de", "en"): "Helsinki-NLP/opus-mt-de-en",
        ("es", "en"): "Helsinki-NLP/opus-mt-es-en",
    }

    LANGUAGE_NAMES = {
        "en": "English",
        "fr": "French",
        "de": "German",
        "es": "Spanish",
        "it": "Italian",
    }

    def __init__(self):
        # Cache loaded pipelines to avoid reloading
        self._pipelines = {}

    def _get_pipeline(self, source_lang, target_lang):
        """Load or retrieve a cached translation pipeline."""
        key = (source_lang, target_lang)
        if key not in self._pipelines:
            if key not in self.MODELS:
                available = [
                    f"{s} -> {t}" for s, t in self.MODELS.keys()
                ]
                raise ValueError(
                    f"Language pair {source_lang}->{target_lang} "
                    f"not supported. Available: {available}"
                )
            model_name = self.MODELS[key]
            self._pipelines[key] = pipeline(
                "translation", model=model_name
            )
        return self._pipelines[key]

    def translate(self, text, source_lang, target_lang):
        """Translate text from source to target language."""
        translator = self._get_pipeline(source_lang, target_lang)
        result = translator(text)
        return result[0]['translation_text']

    def translate_paragraph(self, text, source_lang, target_lang):
        """Translate a paragraph by translating each sentence."""
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())

        translations = []
        for sentence in sentences:
            if sentence.strip():
                translated = self.translate(
                    sentence, source_lang, target_lang
                )
                translations.append(translated)

        return ' '.join(translations)


# Create translator
translator = SimpleTranslator()

# Example 1: Simple sentence translation
print("Example 1: Simple Sentence Translation")
print("=" * 55)

text = "Machine learning is a subset of artificial intelligence."

for target in ["fr", "de", "es"]:
    result = translator.translate(text, "en", target)
    lang_name = translator.LANGUAGE_NAMES[target]
    print(f"  {lang_name}: {result}")

print()

# Example 2: Paragraph translation
print("Example 2: Paragraph Translation (English to French)")
print("=" * 55)

paragraph = (
    "The sun was setting behind the mountains. "
    "Birds were singing their evening songs. "
    "A gentle breeze carried the scent of flowers."
)

print(f"\n  Original:\n  {paragraph}")

translated_paragraph = translator.translate_paragraph(
    paragraph, "en", "fr"
)
print(f"\n  French:\n  {translated_paragraph}")

print()

# Example 3: Round-trip translation
print("Example 3: Round-Trip Translation")
print("=" * 55)

original = "I enjoy reading books about science."
print(f"\n  Original (EN):  {original}")

# English -> French
french = translator.translate(original, "en", "fr")
print(f"  EN -> FR:       {french}")

# French -> English
back = translator.translate(french, "fr", "en")
print(f"  FR -> EN:       {back}")

match = "YES" if original.lower().rstrip('.') in back.lower() else "SIMILAR"
print(f"  Round-trip match: {match}")
```

**Expected Output:**
```
Example 1: Simple Sentence Translation
=======================================================
  French: L'apprentissage automatique est un sous-ensemble de l'intelligence artificielle.
  German: Maschinelles Lernen ist eine Teilmenge der kuenstlichen Intelligenz.
  Spanish: El aprendizaje automatico es un subconjunto de la inteligencia artificial.

Example 2: Paragraph Translation (English to French)
=======================================================

  Original:
  The sun was setting behind the mountains. Birds were singing their evening songs. A gentle breeze carried the scent of flowers.

  French:
  Le soleil se couchait derriere les montagnes. Les oiseaux chantaient leurs chansons du soir. Une douce brise portait le parfum des fleurs.

Example 3: Round-Trip Translation
=======================================================

  Original (EN):  I enjoy reading books about science.
  EN -> FR:       J'aime lire des livres sur la science.
  FR -> EN:       I like to read books about science.
  Round-trip match: SIMILAR
```

---

## Common Mistakes

1. **Forgetting about input length limits**: Most seq2seq models have maximum input lengths. If your text is too long, either truncate it or split it into chunks. The Hugging Face pipeline handles truncation automatically, but you should be aware of it.

2. **Not understanding token vs. word**: Models process tokens, not words. A single word might be multiple tokens. When setting `max_length`, remember that tokens are slightly smaller than words.

3. **Using the wrong model for a language pair**: Each translation model handles a specific language pair. Using `opus-mt-en-fr` to translate German to English will produce garbage. Always check that the model matches your source and target languages.

4. **Ignoring attention**: If you are building a seq2seq model from scratch, always include an attention mechanism. Without attention, performance drops dramatically for longer sequences.

5. **Over-relying on teacher forcing**: Using teacher forcing 100% of the time during training can make the model fragile at inference time (when it must use its own predictions). Gradually reduce the teacher forcing ratio during training.

---

## Best Practices

1. **Use pre-trained models when possible**: Training a translation model from scratch requires millions of sentence pairs and significant compute. Pre-trained models from Hugging Face work well for most use cases.

2. **Keep sentences short for better translation**: Very long sentences are harder to translate accurately. If possible, break long sentences into shorter ones before translating.

3. **Verify translations for critical content**: Machine translation is impressive but not perfect. For important documents (legal, medical), always have a human review the translation.

4. **Cache loaded models**: Loading a model takes time. If you need to translate many sentences, load the pipeline once and reuse it, as shown in our `SimpleTranslator` class.

5. **Consider the domain**: Translation models trained on news articles may perform poorly on medical or legal text. Use domain-specific models when available.

---

## Quick Summary

Sequence-to-sequence (seq2seq) models convert one sequence into another using an **encoder-decoder architecture**. The encoder reads the input and creates a context vector. The decoder uses this context vector to generate the output one word at a time. **Teacher forcing** trains the decoder by feeding it correct target words instead of its own predictions, preventing error accumulation. The basic context vector creates a **bottleneck** for long sequences, which the **attention mechanism** solves by letting the decoder look at all encoder states and focus on the most relevant ones. Hugging Face provides pre-trained translation models that handle all this complexity automatically.

---

## Key Points

- Seq2seq models handle tasks where both input and output are sequences of different lengths
- The **encoder** reads the input and produces hidden states; the **decoder** generates output word by word
- The **context vector** (encoder's final hidden state) summarizes the input but creates a bottleneck
- **Teacher forcing** feeds correct target words during training to prevent error snowballing
- The **attention mechanism** lets the decoder focus on relevant parts of the input at each step
- Attention weights show which input words influence each output word
- Hugging Face provides pre-trained translation models for many language pairs
- The OPUS-MT models (Helsinki-NLP) support dozens of language pairs
- Seq2seq with attention is the foundation for the Transformer architecture (BERT, GPT)

---

## Practice Questions

1. Why does the encoder-decoder architecture have a "bottleneck" problem? How does the attention mechanism solve it?

2. Explain teacher forcing using an everyday analogy (not the book's analogy). Why is it helpful during training but potentially harmful if used too much?

3. In the attention visualization, why does the French word "noir" (black) attend strongly to the English word "black" even though they appear in different positions in the sentence?

4. What would happen if you used a model trained for English-to-French translation to translate German text? Why?

5. Why is round-trip translation (English to French and back to English) not always perfect? Give two reasons.

---

## Exercises

**Exercise 1: Attention Weights Visualizer**
Create a function that takes two lists (input words and output words) and a matrix of attention weights, and prints a formatted table showing where the attention is focused. Use different symbols to represent different attention levels: "." for low (< 0.1), "o" for medium (0.1-0.4), "O" for high (0.4-0.7), and "#" for very high (> 0.7).

**Exercise 2: Multi-Hop Translation**
Write a program that translates a sentence from English to French, then from French to German (using French-to-English and English-to-German since direct French-German might not be available). Compare the result with a direct English-to-German translation. How much quality is lost in the multi-hop approach?

**Exercise 3: Translation Quality Checker**
Build a tool that translates a sentence to another language and back, then uses ROUGE scores (from Chapter 7) to measure how similar the round-trip translation is to the original. Test with 10 different sentences of varying complexity and plot which types of sentences survive round-trip translation best.

---

## What Is Next?

You now understand the encoder-decoder architecture that powers seq2seq models. In the next chapter, you will learn about **BERT** — a model that revolutionized NLP by using only the encoder part of this architecture. BERT reads text bidirectionally (both left-to-right and right-to-left simultaneously), giving it a deep understanding of language. You will see how BERT is pre-trained, how its WordPiece tokenizer works, and how to use it with Hugging Face for tasks like fill-in-the-blank and text classification.
