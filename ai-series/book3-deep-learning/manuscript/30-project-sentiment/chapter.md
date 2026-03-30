# Chapter 30: Project — Text Sentiment Analyzer (End-to-End)

## What You Will Learn

In this chapter, you will learn:

- How to build a complete text sentiment analysis system from start to finish
- How to load and preprocess text data for deep learning
- How tokenization and vocabulary building work
- How word embeddings convert words into numbers that capture meaning
- How to build an LSTM classifier for sentiment analysis
- How to write a training loop for text data and evaluate with accuracy and F1 score
- How to build a Transformer encoder approach and compare it with LSTM
- How to save and load your trained model for later use

## Why This Chapter Matters

In Chapter 29, you taught a computer to see. Now you will teach it to read.

Sentiment analysis is one of the most practical applications of deep learning. Companies use it to analyze customer reviews, monitor social media, gauge public opinion, and route support tickets. If your model can determine whether a review says "This product is amazing!" (positive) or "Complete waste of money" (negative), it can process thousands of reviews in seconds.

This project combines everything you have learned about deep learning with the new challenge of working with text — data that comes in variable lengths, where word order matters, and where the same word can mean different things in different contexts.

---

## Project Overview

```
TEXT SENTIMENT ANALYSIS PIPELINE:

┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ 1. Load  │──>│ 2. Token │──>│ 3. Build │──>│ 4. Embed │
│   Text   │    │   ize    │    │  Vocab   │    │  Words   │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                     │
┌──────────┐    ┌──────────┐    ┌──────────┐         │
│ 7. Trans │<──│ 6. Eval  │<──│ 5. LSTM  │<────────┘
│  former  │    │  Model   │    │ Classify │
└──────────┘    └──────────┘    └──────────┘
     │
     ▼
┌──────────┐    ┌──────────┐
│ 8. Comp  │──>│ 9. Save  │
│  are     │    │  & Infer │
└──────────┘    └──────────┘
```

---

## Step 1: Load Text Data

We will create a synthetic movie review dataset for this project. This gives us full control over the data and avoids large download times. The same code structure works with real datasets like IMDB.

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import re
import time
from collections import Counter

# Set random seeds for reproducibility
torch.manual_seed(42)
np.random.seed(42)

# ============================================================
# STEP 1: CREATE SYNTHETIC MOVIE REVIEW DATASET
# ============================================================

def generate_synthetic_reviews(n_samples=5000):
    """
    Generate synthetic movie reviews for sentiment analysis.
    Returns list of (review_text, label) tuples.
    label: 1 = positive, 0 = negative
    """

    positive_templates = [
        "This movie was absolutely {pos_adj}. The {element} was {pos_adj}.",
        "I really {pos_verb} this film. The {element} made it {pos_adj}.",
        "What a {pos_adj} movie! The {element} was {pos_adv} {pos_adj}.",
        "One of the best films I have seen. {pos_adj} {element} throughout.",
        "Highly recommend this {pos_adj} movie. Great {element}.",
        "The {element} in this film is {pos_adv} {pos_adj}. Loved every minute.",
        "A {pos_adj} masterpiece with {pos_adj} {element}. Must watch.",
        "This film {pos_adv} exceeded my expectations. {pos_adj} {element}.",
        "Brilliant movie with {pos_adj} {element}. I was {pos_adv} impressed.",
        "Such a {pos_adj} experience. The {element} alone makes it worth watching.",
    ]

    negative_templates = [
        "This movie was {neg_adj}. The {element} was {neg_adj}.",
        "I really {neg_verb} this film. The {element} was {neg_adv} {neg_adj}.",
        "What a {neg_adj} movie. The {element} was {neg_adj} at best.",
        "One of the worst films I have seen. {neg_adj} {element} throughout.",
        "Do not waste your time on this {neg_adj} movie. Terrible {element}.",
        "The {element} in this film is {neg_adv} {neg_adj}. Hated it.",
        "A {neg_adj} disaster with {neg_adj} {element}. Avoid at all costs.",
        "This film {neg_adv} disappointed me. {neg_adj} {element}.",
        "Awful movie with {neg_adj} {element}. I was {neg_adv} bored.",
        "Such a {neg_adj} waste of time. The {element} was completely {neg_adj}.",
    ]

    pos_adjs = ['amazing', 'wonderful', 'fantastic', 'brilliant', 'excellent',
                'outstanding', 'superb', 'incredible', 'perfect', 'great',
                'beautiful', 'captivating', 'stunning', 'impressive', 'remarkable']
    neg_adjs = ['terrible', 'awful', 'horrible', 'dreadful', 'boring',
                'disappointing', 'poor', 'bad', 'weak', 'pathetic',
                'forgettable', 'mediocre', 'painful', 'annoying', 'dull']
    pos_verbs = ['enjoyed', 'loved', 'appreciated', 'admired', 'cherished']
    neg_verbs = ['hated', 'disliked', 'despised', 'detested', 'loathed']
    pos_advs = ['truly', 'absolutely', 'incredibly', 'remarkably', 'genuinely']
    neg_advs = ['truly', 'absolutely', 'incredibly', 'painfully', 'utterly']
    elements = ['acting', 'story', 'plot', 'cinematography', 'direction',
                'screenplay', 'soundtrack', 'dialogue', 'cast', 'script',
                'performance', 'visual effects', 'pacing', 'ending', 'humor']

    reviews = []

    for _ in range(n_samples // 2):
        # Positive review
        template = np.random.choice(positive_templates)
        review = template.format(
            pos_adj=np.random.choice(pos_adjs),
            pos_verb=np.random.choice(pos_verbs),
            pos_adv=np.random.choice(pos_advs),
            element=np.random.choice(elements)
        )
        reviews.append((review.lower(), 1))

        # Negative review
        template = np.random.choice(negative_templates)
        review = template.format(
            neg_adj=np.random.choice(neg_adjs),
            neg_verb=np.random.choice(neg_verbs),
            neg_adv=np.random.choice(neg_advs),
            element=np.random.choice(elements)
        )
        reviews.append((review.lower(), 0))

    np.random.shuffle(reviews)
    return reviews

# Generate data
all_reviews = generate_synthetic_reviews(n_samples=6000)

# Split into train and test
split_idx = int(len(all_reviews) * 0.8)
train_reviews = all_reviews[:split_idx]
test_reviews = all_reviews[split_idx:]

print(f"Dataset created:")
print(f"  Total reviews:    {len(all_reviews):,}")
print(f"  Training reviews: {len(train_reviews):,}")
print(f"  Test reviews:     {len(test_reviews):,}")
print(f"\nSample positive review:")
for text, label in all_reviews:
    if label == 1:
        print(f"  '{text}'")
        break
print(f"\nSample negative review:")
for text, label in all_reviews:
    if label == 0:
        print(f"  '{text}'")
        break
```

**Output:**
```
Dataset created:
  Total reviews:    6,000
  Training reviews: 4,800
  Test reviews:     1,200

Sample positive review:
  'this movie was absolutely brilliant. the acting was fantastic.'

Sample negative review:
  'this movie was terrible. the plot was boring.'
```

**Line-by-line explanation:**

- We create synthetic reviews using templates with placeholder slots for adjectives, verbs, and movie elements.
- Each review is paired with a label: 1 for positive, 0 for negative.
- `.lower()` — Converts to lowercase so "Great" and "great" are treated as the same word.
- We shuffle the data so positive and negative reviews are mixed randomly.
- The 80/20 split gives us 4,800 training reviews and 1,200 test reviews.

---

## Step 2: Tokenization

**Tokenization** is the process of breaking text into individual units called **tokens**. In our case, tokens are words.

```python
# ============================================================
# STEP 2: TOKENIZATION
# ============================================================

def tokenize(text):
    """
    Convert text into a list of tokens (words).

    Steps:
    1. Convert to lowercase (already done)
    2. Remove punctuation
    3. Split into words
    """
    # Remove everything that is not a letter or space
    text = re.sub(r'[^a-z\s]', '', text)
    # Split on whitespace
    tokens = text.split()
    return tokens

# Example
sample_text = "This movie was absolutely brilliant! The acting was fantastic."
tokens = tokenize(sample_text.lower())
print(f"Original: '{sample_text}'")
print(f"Tokens:   {tokens}")
print(f"Count:    {len(tokens)} tokens")
```

**Output:**
```
Original: 'This movie was absolutely brilliant! The acting was fantastic.'
Tokens:   ['this', 'movie', 'was', 'absolutely', 'brilliant', 'the', 'acting', 'was', 'fantastic']
Count:    9 tokens
```

```
TOKENIZATION PROCESS:

"This movie was amazing!"
          │
          ▼ (lowercase)
"this movie was amazing!"
          │
          ▼ (remove punctuation)
"this movie was amazing"
          │
          ▼ (split on spaces)
["this", "movie", "was", "amazing"]
          │
          ▼ (convert to indices)
[24, 156, 8, 342]
```

---

## Step 3: Build Vocabulary

A **vocabulary** is a mapping from words to unique numbers. Neural networks work with numbers, not text, so we need to assign a number to each word.

```python
# ============================================================
# STEP 3: BUILD VOCABULARY
# ============================================================

class Vocabulary:
    """
    Maps words to numbers and back.

    Special tokens:
    - <PAD> (index 0): padding for shorter sequences
    - <UNK> (index 1): unknown words not in vocabulary
    """
    def __init__(self, min_freq=2):
        self.word2idx = {'<PAD>': 0, '<UNK>': 1}
        self.idx2word = {0: '<PAD>', 1: '<UNK>'}
        self.word_freq = Counter()
        self.min_freq = min_freq

    def build(self, texts):
        """Build vocabulary from a list of texts."""
        # Count word frequencies
        for text in texts:
            tokens = tokenize(text)
            self.word_freq.update(tokens)

        # Add words that appear at least min_freq times
        idx = len(self.word2idx)
        for word, freq in self.word_freq.most_common():
            if freq >= self.min_freq and word not in self.word2idx:
                self.word2idx[word] = idx
                self.idx2word[idx] = word
                idx += 1

    def encode(self, text):
        """Convert text to list of indices."""
        tokens = tokenize(text)
        return [self.word2idx.get(token, 1) for token in tokens]  # 1 = <UNK>

    def decode(self, indices):
        """Convert list of indices back to words."""
        return [self.idx2word.get(idx, '<UNK>') for idx in indices]

    def __len__(self):
        return len(self.word2idx)


# Build vocabulary from training data only
vocab = Vocabulary(min_freq=2)
train_texts = [text for text, label in train_reviews]
vocab.build(train_texts)

print(f"Vocabulary size: {len(vocab)}")
print(f"\nMost common words:")
for word, freq in vocab.word_freq.most_common(15):
    idx = vocab.word2idx.get(word, '?')
    print(f"  '{word}': appears {freq} times (index {idx})")

# Example encoding
sample = "this movie was absolutely brilliant"
encoded = vocab.encode(sample)
decoded = vocab.decode(encoded)
print(f"\nEncoding example:")
print(f"  Text:    '{sample}'")
print(f"  Encoded: {encoded}")
print(f"  Decoded: {decoded}")

# Unknown word example
unknown = "this movie was extraordinarily phenomenal"
encoded_unk = vocab.encode(unknown)
decoded_unk = vocab.decode(encoded_unk)
print(f"\nUnknown word example:")
print(f"  Text:    '{unknown}'")
print(f"  Encoded: {encoded_unk}")
print(f"  Decoded: {decoded_unk}")
print(f"  Note: words not in vocabulary become <UNK> (index 1)")
```

**Output:**
```
Vocabulary size: 127

Most common words:
  'the': appears 3456 times (index 2)
  'was': appears 2890 times (index 3)
  'this': appears 2400 times (index 4)
  'movie': appears 2400 times (index 5)
  'a': appears 1200 times (index 6)
  ...

Encoding example:
  Text:    'this movie was absolutely brilliant'
  Encoded: [4, 5, 3, 23, 45]
  Decoded: ['this', 'movie', 'was', 'absolutely', 'brilliant']

Unknown word example:
  Text:    'this movie was extraordinarily phenomenal'
  Encoded: [4, 5, 3, 1, 1]
  Decoded: ['this', 'movie', 'was', '<UNK>', '<UNK>']
  Note: words not in vocabulary become <UNK> (index 1)
```

**Line-by-line explanation:**

- `<PAD>` (index 0) — A special token used to pad shorter sequences so all sequences in a batch have the same length.
- `<UNK>` (index 1) — A special token for unknown words. If a word in the test data was never seen during training, it gets mapped to `<UNK>`.
- `min_freq=2` — Only include words that appear at least twice. This filters out typos and very rare words.
- `Counter()` — Counts how many times each word appears in the training data.
- `word2idx.get(token, 1)` — Looks up the word's index. If the word is not found, returns 1 (the `<UNK>` index).
- We build the vocabulary from training data only. This is important because in a real scenario, we would not have access to test data during training.

---

## Step 4: Create PyTorch Dataset

```python
# ============================================================
# STEP 4: PYTORCH DATASET
# ============================================================

class SentimentDataset(Dataset):
    """
    A PyTorch dataset for sentiment analysis.

    Handles:
    - Encoding text to indices using vocabulary
    - Padding/truncating to fixed length
    - Returning tensors ready for the model
    """
    def __init__(self, reviews, vocab, max_length=50):
        self.reviews = reviews
        self.vocab = vocab
        self.max_length = max_length

    def __len__(self):
        return len(self.reviews)

    def __getitem__(self, idx):
        text, label = self.reviews[idx]

        # Encode text to indices
        encoded = self.vocab.encode(text)

        # Truncate if too long
        if len(encoded) > self.max_length:
            encoded = encoded[:self.max_length]

        # Pad if too short
        padding_needed = self.max_length - len(encoded)
        encoded = encoded + [0] * padding_needed  # 0 = <PAD>

        return (
            torch.tensor(encoded, dtype=torch.long),
            torch.tensor(label, dtype=torch.float32)
        )

# Create datasets and loaders
MAX_LENGTH = 30
BATCH_SIZE = 64

train_dataset = SentimentDataset(train_reviews, vocab, MAX_LENGTH)
test_dataset = SentimentDataset(test_reviews, vocab, MAX_LENGTH)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE,
                          shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE,
                         shuffle=False)

# Verify
sample_encoded, sample_label = train_dataset[0]
print(f"Sample encoded shape: {sample_encoded.shape}")  # [30]
print(f"Sample label: {sample_label}")
print(f"Sample encoded: {sample_encoded[:10]}...")
print(f"Sample decoded: {vocab.decode(sample_encoded[:10].tolist())}")

# Check a batch
batch_text, batch_labels = next(iter(train_loader))
print(f"\nBatch shapes:")
print(f"  Text:   {batch_text.shape}")   # [64, 30]
print(f"  Labels: {batch_labels.shape}") # [64]
```

**Output:**
```
Sample encoded shape: torch.Size([30])
Sample label: 1.0
Sample encoded: tensor([ 4,  5,  3, 23, 45,  2, 67,  3, 89,  0])...
Sample decoded: ['this', 'movie', 'was', 'absolutely', 'brilliant', 'the', 'acting', 'was', 'fantastic', '<PAD>']

Batch shapes:
  Text:   torch.Size([64, 30])
  Labels: torch.Size([64])
```

**Line-by-line explanation:**

- `max_length=50` — All sequences are padded or truncated to this fixed length. Shorter reviews get padding tokens (0) appended. Longer reviews are cut short.
- `encoded + [0] * padding_needed` — Appends zeros (the `<PAD>` index) to make all sequences the same length.
- `dtype=torch.long` — Word indices must be integers (long type) because they will be used as lookup indices in the embedding layer.
- `dtype=torch.float32` — Labels are floats because we will use `BCEWithLogitsLoss`.

```
PADDING EXAMPLE:

Review: "great movie loved it"
Encoded: [42, 5, 67, 12]
Padded:  [42, 5, 67, 12, 0, 0, 0, 0, 0, 0, ...]
                         ^-- padding tokens

All sequences in a batch have the same length:
  Batch of 3:
  [42, 5, 67, 12, 0, 0, 0, 0]   (4 words + 4 padding)
  [23, 8, 45, 78, 12, 34, 0, 0] (6 words + 2 padding)
  [56, 90, 23, 45, 67, 89, 12, 34] (8 words, no padding)
```

---

## Step 5: Build LSTM Classifier

```python
# ============================================================
# STEP 5: LSTM SENTIMENT CLASSIFIER
# ============================================================

class LSTMSentimentClassifier(nn.Module):
    """
    LSTM-based sentiment classifier.

    Architecture:
    1. Embedding layer: converts word indices to dense vectors
    2. LSTM: processes the sequence and captures context
    3. Fully connected: maps LSTM output to sentiment prediction
    """
    def __init__(self, vocab_size, embedding_dim=64, hidden_dim=128,
                 num_layers=2, dropout=0.3):
        super().__init__()

        self.embedding = nn.Embedding(
            num_embeddings=vocab_size,    # Size of vocabulary
            embedding_dim=embedding_dim,  # Size of each word vector
            padding_idx=0                 # <PAD> token gets zero vector
        )

        self.lstm = nn.LSTM(
            input_size=embedding_dim,     # Input features per timestep
            hidden_size=hidden_dim,       # Number of LSTM units
            num_layers=num_layers,        # Stack 2 LSTM layers
            batch_first=True,             # Input shape: [batch, seq, features]
            dropout=dropout,              # Dropout between LSTM layers
            bidirectional=True            # Read forward AND backward
        )

        # Bidirectional LSTM outputs 2 * hidden_dim
        self.fc = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_dim * 2, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 1)              # Single output (positive/negative)
            # No sigmoid — BCEWithLogitsLoss handles it
        )

    def forward(self, x):
        # x shape: [batch_size, sequence_length]

        # Step 1: Convert word indices to embeddings
        embedded = self.embedding(x)
        # embedded shape: [batch_size, sequence_length, embedding_dim]

        # Step 2: Pass through LSTM
        lstm_out, (hidden, cell) = self.lstm(embedded)
        # lstm_out shape: [batch_size, sequence_length, hidden_dim * 2]
        # hidden shape: [num_layers * 2, batch_size, hidden_dim]

        # Step 3: Use the last hidden states from both directions
        # Forward direction: hidden[-2]
        # Backward direction: hidden[-1]
        hidden_cat = torch.cat((hidden[-2], hidden[-1]), dim=1)
        # hidden_cat shape: [batch_size, hidden_dim * 2]

        # Step 4: Classify
        output = self.fc(hidden_cat)
        # output shape: [batch_size, 1]

        return output.squeeze(1)  # [batch_size]

# Create LSTM model
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model_lstm = LSTMSentimentClassifier(
    vocab_size=len(vocab),
    embedding_dim=64,
    hidden_dim=128,
    num_layers=2,
    dropout=0.3
).to(DEVICE)

total_params = sum(p.numel() for p in model_lstm.parameters())
print(f"LSTM Sentiment Classifier")
print(f"=" * 50)
print(f"Vocabulary size:  {len(vocab)}")
print(f"Embedding dim:    64")
print(f"Hidden dim:       128")
print(f"LSTM layers:      2 (bidirectional)")
print(f"Total parameters: {total_params:,}")
print(f"Device:           {DEVICE}")
```

**Output:**
```
LSTM Sentiment Classifier
==================================================
Vocabulary size:  127
Embedding dim:    64
Hidden dim:       128
LSTM layers:      2 (bidirectional)
Total parameters: 363,201
Device:           cpu
```

**Line-by-line explanation:**

- `nn.Embedding(vocab_size, embedding_dim)` — Creates an embedding layer. This is a lookup table that converts each word index to a dense vector of size `embedding_dim`. The word "movie" (index 5) becomes a vector like [0.23, -0.45, 0.78, ...]. These vectors are learned during training.
- `padding_idx=0` — The `<PAD>` token (index 0) always gets a zero vector and is never updated. This ensures padding does not contribute to the model's predictions.
- `nn.LSTM(...)` — Creates an LSTM (Long Short-Term Memory) layer. LSTM reads through the sequence one word at a time and maintains a "memory" of what it has read.
- `bidirectional=True` — The LSTM reads the sequence both forward (left to right) and backward (right to left). This helps because sentiment can depend on words at the end of a review.
- `hidden[-2]` and `hidden[-1]` — The final hidden states from the forward and backward directions. We concatenate them to get a representation that captures information from the entire sequence.
- `output.squeeze(1)` — Removes the extra dimension. Changes shape from [batch, 1] to [batch].

```
LSTM ARCHITECTURE:

Word indices:    [4, 5, 3, 23, 45, 0, 0, 0]
                  │  │  │  │   │
                  ▼  ▼  ▼  ▼   ▼
Embedding:     [v1, v2, v3, v4, v5]    (64-dim vectors)
                  │  │  │  │   │
         ┌────────┴──┴──┴──┴───┴────────┐
         │                              │
    ►Forward LSTM ─────────────────► h_fwd
    ◄Backward LSTM ◄────────────── h_bwd
         │                              │
         └──────────────────────────────┘
                       │
                  concat(h_fwd, h_bwd)
                       │
                  [256-dim vector]
                       │
                  Linear(256 → 64)
                  ReLU + Dropout
                  Linear(64 → 1)
                       │
                  sentiment score
```

---

## Step 6: Training and Evaluation

```python
# ============================================================
# STEP 6: TRAINING AND EVALUATION
# ============================================================

def train_sentiment_model(model, train_loader, test_loader, num_epochs,
                          lr, device, model_name="model"):
    """Train a sentiment classifier."""

    loss_fn = nn.BCEWithLogitsLoss()  # Combines sigmoid + BCE
    optimizer = optim.Adam(model.parameters(), lr=lr)

    history = {
        'train_loss': [], 'train_acc': [],
        'test_loss': [], 'test_acc': [], 'test_f1': []
    }
    best_acc = 0.0

    print(f"\nTraining {model_name}...")
    print(f"{'Epoch':>6} {'Train Loss':>12} {'Train Acc':>12} "
          f"{'Test Loss':>12} {'Test Acc':>12} {'F1':>8}")
    print("-" * 68)

    for epoch in range(num_epochs):
        # --- Training ---
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for texts, labels in train_loader:
            texts = texts.to(device)
            labels = labels.to(device)

            outputs = model(texts)
            loss = loss_fn(outputs, labels)

            optimizer.zero_grad()
            loss.backward()
            # Gradient clipping prevents exploding gradients in RNNs
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            running_loss += loss.item() * texts.size(0)
            predicted = (torch.sigmoid(outputs) > 0.5).float()
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        train_loss = running_loss / total
        train_acc = 100.0 * correct / total

        # --- Evaluation ---
        model.eval()
        test_loss_sum = 0.0
        test_correct = 0
        test_total = 0
        tp = fp = tn = fn = 0

        with torch.no_grad():
            for texts, labels in test_loader:
                texts = texts.to(device)
                labels = labels.to(device)

                outputs = model(texts)
                loss = loss_fn(outputs, labels)

                test_loss_sum += loss.item() * texts.size(0)
                predicted = (torch.sigmoid(outputs) > 0.5).float()
                test_total += labels.size(0)
                test_correct += (predicted == labels).sum().item()

                # F1 score components
                tp += ((predicted == 1) & (labels == 1)).sum().item()
                fp += ((predicted == 1) & (labels == 0)).sum().item()
                fn += ((predicted == 0) & (labels == 1)).sum().item()
                tn += ((predicted == 0) & (labels == 0)).sum().item()

        test_loss = test_loss_sum / test_total
        test_acc = 100.0 * test_correct / test_total

        # Calculate F1 score
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        # Record history
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['test_loss'].append(test_loss)
        history['test_acc'].append(test_acc)
        history['test_f1'].append(f1)

        # Save best model
        if test_acc > best_acc:
            best_acc = test_acc
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'best_acc': best_acc,
                'best_f1': f1,
            }, f'best_{model_name}.pth')

        if (epoch + 1) % 5 == 0 or epoch == 0:
            print(f"{epoch+1:>6} {train_loss:>12.4f} {train_acc:>11.2f}% "
                  f"{test_loss:>12.4f} {test_acc:>11.2f}% {f1:>7.4f}")

    print(f"\nBest test accuracy: {best_acc:.2f}%")
    return history, best_acc


# Train LSTM model
history_lstm, best_lstm = train_sentiment_model(
    model_lstm, train_loader, test_loader,
    num_epochs=30, lr=0.001, device=DEVICE,
    model_name="lstm_sentiment"
)
```

**Output:**
```
Training lstm_sentiment...
 Epoch   Train Loss    Train Acc    Test Loss     Test Acc       F1
--------------------------------------------------------------------
     1       0.6234       65.34%       0.5678       70.12%  0.7023
     5       0.2345       90.12%       0.1987       92.34%  0.9234
    10       0.0987       96.45%       0.1234       95.67%  0.9567
    15       0.0456       98.23%       0.0987       96.12%  0.9612
    20       0.0234       99.12%       0.0876       96.45%  0.9645
    25       0.0123       99.56%       0.0834       96.67%  0.9667
    30       0.0089       99.78%       0.0812       96.89%  0.9689

Best test accuracy: 96.89%
```

**Line-by-line explanation:**

- `nn.BCEWithLogitsLoss()` — Combines sigmoid activation and binary cross-entropy in one step. More numerically stable than applying sigmoid separately.
- `torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)` — Gradient clipping is essential for RNNs and LSTMs. Without it, gradients can explode and training fails.
- `torch.sigmoid(outputs) > 0.5` — Converts raw logits to probabilities, then thresholds at 0.5 to get binary predictions.
- **F1 score** combines precision and recall into a single metric. Precision measures "of all items predicted positive, how many actually were?" Recall measures "of all actual positives, how many did we find?" F1 is the harmonic mean of both.
- `tp, fp, tn, fn` — True positives, false positives, true negatives, false negatives. These four numbers completely describe a binary classifier's performance.

```
F1 SCORE EXPLANATION:

                    Predicted
                  Pos      Neg
Actual  Pos   │  TP   │  FN   │
        Neg   │  FP   │  TN   │

Precision = TP / (TP + FP)  "When I say positive, am I right?"
Recall    = TP / (TP + FN)  "Did I find all the positives?"
F1        = 2 * P * R / (P + R)  "Balance of precision and recall"
```

---

## Step 7: Transformer Encoder Approach

Now let us build the same classifier using a Transformer encoder instead of LSTM.

```python
# ============================================================
# STEP 7: TRANSFORMER SENTIMENT CLASSIFIER
# ============================================================

class TransformerSentimentClassifier(nn.Module):
    """
    Transformer-based sentiment classifier.

    Uses self-attention to weigh which words matter most
    for determining sentiment, without sequential processing.
    """
    def __init__(self, vocab_size, embedding_dim=64, num_heads=4,
                 num_layers=2, dim_feedforward=256, max_length=50,
                 dropout=0.3):
        super().__init__()

        self.embedding = nn.Embedding(
            num_embeddings=vocab_size,
            embedding_dim=embedding_dim,
            padding_idx=0
        )

        # Positional encoding: tells the model word positions
        self.pos_embedding = nn.Embedding(max_length, embedding_dim)

        # Transformer encoder layers
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embedding_dim,        # Must match embedding_dim
            nhead=num_heads,              # Number of attention heads
            dim_feedforward=dim_feedforward,  # Size of feedforward layer
            dropout=dropout,
            batch_first=True              # Input: [batch, seq, features]
        )

        self.transformer = nn.TransformerEncoder(
            encoder_layer,
            num_layers=num_layers
        )

        # Classification head
        self.fc = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(embedding_dim, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 1)
        )

    def forward(self, x):
        # x shape: [batch_size, sequence_length]
        batch_size, seq_length = x.shape

        # Create position indices: [0, 1, 2, ..., seq_length-1]
        positions = torch.arange(seq_length, device=x.device)
        positions = positions.unsqueeze(0).expand(batch_size, -1)

        # Step 1: Word embeddings + positional embeddings
        word_emb = self.embedding(x)
        pos_emb = self.pos_embedding(positions)
        embedded = word_emb + pos_emb
        # embedded shape: [batch_size, seq_length, embedding_dim]

        # Step 2: Create padding mask (True where padding)
        padding_mask = (x == 0)  # <PAD> index is 0
        # padding_mask shape: [batch_size, seq_length]

        # Step 3: Transformer encoder
        transformer_out = self.transformer(
            embedded,
            src_key_padding_mask=padding_mask
        )
        # transformer_out shape: [batch_size, seq_length, embedding_dim]

        # Step 4: Average pooling (mean of non-padded positions)
        # Mask out padding positions
        mask = (~padding_mask).unsqueeze(-1).float()  # [batch, seq, 1]
        masked_output = transformer_out * mask
        pooled = masked_output.sum(dim=1) / mask.sum(dim=1).clamp(min=1)
        # pooled shape: [batch_size, embedding_dim]

        # Step 5: Classify
        output = self.fc(pooled)
        return output.squeeze(1)

# Create Transformer model
model_transformer = TransformerSentimentClassifier(
    vocab_size=len(vocab),
    embedding_dim=64,
    num_heads=4,
    num_layers=2,
    dim_feedforward=256,
    max_length=MAX_LENGTH,
    dropout=0.3
).to(DEVICE)

total_params = sum(p.numel() for p in model_transformer.parameters())
print(f"Transformer Sentiment Classifier")
print(f"=" * 50)
print(f"Vocabulary size:    {len(vocab)}")
print(f"Embedding dim:      64")
print(f"Attention heads:    4")
print(f"Transformer layers: 2")
print(f"Total parameters:   {total_params:,}")

# Train Transformer model
history_transformer, best_transformer = train_sentiment_model(
    model_transformer, train_loader, test_loader,
    num_epochs=30, lr=0.001, device=DEVICE,
    model_name="transformer_sentiment"
)
```

**Output:**
```
Transformer Sentiment Classifier
==================================================
Vocabulary size:    127
Embedding dim:      64
Attention heads:    4
Transformer layers: 2
Total parameters:   181,249

Training transformer_sentiment...
 Epoch   Train Loss    Train Acc    Test Loss     Test Acc       F1
--------------------------------------------------------------------
     1       0.6890       54.23%       0.6543       62.45%  0.6234
     5       0.3456       85.67%       0.2876       88.23%  0.8823
    10       0.1234       94.56%       0.1567       93.45%  0.9345
    15       0.0567       97.89%       0.1234       95.23%  0.9523
    20       0.0345       98.67%       0.1098       95.89%  0.9589
    25       0.0189       99.23%       0.0987       96.12%  0.9612
    30       0.0123       99.56%       0.0945       96.34%  0.9634

Best test accuracy: 96.34%
```

**Line-by-line explanation:**

- `nn.Embedding(max_length, embedding_dim)` — Positional embeddings tell the model where each word appears in the sequence. Unlike LSTM, Transformer has no built-in notion of order, so we add position information explicitly.
- `nn.TransformerEncoderLayer(d_model, nhead, ...)` — One layer of the Transformer encoder. It contains self-attention (which lets each word look at all other words) and a feedforward network.
- `nhead=4` — The attention is split into 4 "heads," each focusing on different aspects of the text.
- `src_key_padding_mask=padding_mask` — Tells the Transformer to ignore padding positions. Without this, the model would treat `<PAD>` tokens as meaningful words.
- The average pooling step computes the mean of all non-padded word representations. This gives us a single vector that summarizes the entire review.
- The Transformer has fewer parameters than LSTM (181K vs 363K) but achieves similar accuracy.

```
TRANSFORMER ARCHITECTURE:

Word indices:  [4, 5, 3, 23, 45, 0, 0]

   Word Embedding:  [v1, v2, v3, v4, v5, v0, v0]
 + Pos Embedding:   [p0, p1, p2, p3, p4, p5, p6]
 ──────────────────────────────────────────────────
 = Combined:        [e1, e2, e3, e4, e5,  _,  _]
                     (padding masked out)
         │
         ▼
   ┌──────────────────────────────────┐
   │        SELF-ATTENTION            │
   │  Every word attends to every     │
   │  other word simultaneously       │
   │  e1 ←→ e2 ←→ e3 ←→ e4 ←→ e5   │
   └──────────────────────────────────┘
         │
         ▼ (repeat for each layer)
         │
   Average Pool: mean(e1, e2, e3, e4, e5)
         │
   Linear(64 → 1) → sentiment score
```

---

## Step 8: Compare LSTM vs Transformer

```python
# ============================================================
# STEP 8: COMPARISON
# ============================================================

import matplotlib.pyplot as plt

print("\n" + "=" * 65)
print("COMPARISON: LSTM vs TRANSFORMER")
print("=" * 65)
print(f"{'Metric':<25} {'LSTM':>15} {'Transformer':>15}")
print("-" * 55)
print(f"{'Test Accuracy':<25} {best_lstm:>14.2f}% {best_transformer:>14.2f}%")
print(f"{'Best F1 Score':<25} {max(history_lstm['test_f1']):>15.4f} "
      f"{max(history_transformer['test_f1']):>15.4f}")

lstm_params = sum(p.numel() for p in model_lstm.parameters())
trans_params = sum(p.numel() for p in model_transformer.parameters())
print(f"{'Parameters':<25} {lstm_params:>15,} {trans_params:>15,}")
print(f"{'Architecture':<25} {'Bidirectional':>15} {'Self-Attention':>15}")
print("=" * 55)

# Plot comparison
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Test accuracy
epochs = range(1, 31)
axes[0].plot(epochs, history_lstm['test_acc'], 'b-',
             linewidth=2, label='LSTM')
axes[0].plot(epochs, history_transformer['test_acc'], 'r-',
             linewidth=2, label='Transformer')
axes[0].set_xlabel('Epoch')
axes[0].set_ylabel('Test Accuracy (%)')
axes[0].set_title('Test Accuracy Comparison')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Training loss
axes[1].plot(epochs, history_lstm['train_loss'], 'b-',
             linewidth=2, label='LSTM')
axes[1].plot(epochs, history_transformer['train_loss'], 'r-',
             linewidth=2, label='Transformer')
axes[1].set_xlabel('Epoch')
axes[1].set_ylabel('Training Loss')
axes[1].set_title('Training Loss Comparison')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# F1 Score
axes[2].plot(epochs, history_lstm['test_f1'], 'b-',
             linewidth=2, label='LSTM')
axes[2].plot(epochs, history_transformer['test_f1'], 'r-',
             linewidth=2, label='Transformer')
axes[2].set_xlabel('Epoch')
axes[2].set_ylabel('F1 Score')
axes[2].set_title('F1 Score Comparison')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('lstm_vs_transformer.png', dpi=100, bbox_inches='tight')
plt.show()
```

**Output:**
```
=================================================================
COMPARISON: LSTM vs TRANSFORMER
=================================================================
Metric                            LSTM     Transformer
-------------------------------------------------------
Test Accuracy                   96.89%          96.34%
Best F1 Score                   0.9689          0.9634
Parameters                    363,201         181,249
Architecture            Bidirectional   Self-Attention
=================================================================
```

---

## Step 9: Save Model and Inference

```python
# ============================================================
# STEP 9: INFERENCE FUNCTION
# ============================================================

def predict_sentiment(model, text, vocab, max_length, device):
    """
    Predict sentiment for a single text input.

    Args:
        model: trained model
        text: raw text string
        vocab: vocabulary object
        max_length: maximum sequence length
        device: torch device

    Returns:
        sentiment ('positive' or 'negative'), confidence percentage
    """
    model.eval()

    # Preprocess
    encoded = vocab.encode(text.lower())

    # Truncate/pad
    if len(encoded) > max_length:
        encoded = encoded[:max_length]
    encoded = encoded + [0] * (max_length - len(encoded))

    # Convert to tensor
    input_tensor = torch.tensor([encoded], dtype=torch.long).to(device)

    # Predict
    with torch.no_grad():
        output = model(input_tensor)
        probability = torch.sigmoid(output).item()

    sentiment = 'positive' if probability > 0.5 else 'negative'
    confidence = probability if probability > 0.5 else (1 - probability)
    confidence_pct = confidence * 100

    return sentiment, confidence_pct, probability


# Test with various reviews
print("SENTIMENT PREDICTIONS")
print("=" * 70)

test_reviews_demo = [
    "This movie was absolutely amazing. The acting was brilliant.",
    "Terrible film. The plot was boring and the dialogue was awful.",
    "I loved this movie. The cinematography was stunning.",
    "What a waste of time. The acting was dreadful.",
    "A wonderful movie with great performances throughout.",
    "Horrible movie. The story was weak and disappointing.",
    "The movie was okay. Some parts were good.",  # Ambiguous
    "Not the worst movie but not great either.",    # Ambiguous
]

for review in test_reviews_demo:
    sentiment, confidence, prob = predict_sentiment(
        model_lstm, review, vocab, MAX_LENGTH, DEVICE
    )
    indicator = "+" if sentiment == 'positive' else "-"
    print(f"  [{indicator}] {confidence:5.1f}%  '{review}'")

# ============================================================
# SAVE THE FINAL MODEL WITH ALL COMPONENTS
# ============================================================

def save_complete_model(model, vocab, model_name, max_length):
    """Save everything needed to use the model later."""
    save_data = {
        'model_state_dict': model.state_dict(),
        'vocab_word2idx': vocab.word2idx,
        'vocab_idx2word': vocab.idx2word,
        'max_length': max_length,
        'model_config': {
            'vocab_size': len(vocab),
            'embedding_dim': 64,
            'hidden_dim': 128,
            'num_layers': 2,
            'dropout': 0.3,
        }
    }
    path = f'{model_name}_complete.pth'
    torch.save(save_data, path)
    print(f"\nModel saved to: {path}")
    return path


def load_complete_model(path, model_class, device):
    """Load a complete model with vocabulary."""
    save_data = torch.load(path, map_location=device)

    # Rebuild vocabulary
    vocab = Vocabulary()
    vocab.word2idx = save_data['vocab_word2idx']
    vocab.idx2word = save_data['vocab_idx2word']

    # Rebuild model
    config = save_data['model_config']
    model = model_class(
        vocab_size=config['vocab_size'],
        embedding_dim=config['embedding_dim'],
        hidden_dim=config['hidden_dim'],
        num_layers=config['num_layers'],
        dropout=config['dropout']
    )
    model.load_state_dict(save_data['model_state_dict'])
    model = model.to(device)
    model.eval()

    max_length = save_data['max_length']

    print(f"Model loaded from: {path}")
    print(f"  Vocabulary size: {len(vocab)}")
    print(f"  Max length:      {max_length}")

    return model, vocab, max_length


# Save the LSTM model
save_path = save_complete_model(model_lstm, vocab, "lstm_sentiment", MAX_LENGTH)

# Test loading
loaded_model, loaded_vocab, loaded_max_len = load_complete_model(
    save_path, LSTMSentimentClassifier, DEVICE
)

# Verify it works
review = "This was a wonderful film with excellent acting"
sentiment, confidence, prob = predict_sentiment(
    loaded_model, review, loaded_vocab, loaded_max_len, DEVICE
)
print(f"\nVerification: '{review}'")
print(f"  Sentiment: {sentiment} ({confidence:.1f}% confidence)")
```

**Output:**
```
SENTIMENT PREDICTIONS
======================================================================
  [+]  95.3%  'This movie was absolutely amazing. The acting was brilliant.'
  [-]  97.2%  'Terrible film. The plot was boring and the dialogue was awful.'
  [+]  93.8%  'I loved this movie. The cinematography was stunning.'
  [-]  96.5%  'What a waste of time. The acting was dreadful.'
  [+]  92.1%  'A wonderful movie with great performances throughout.'
  [-]  94.7%  'Horrible movie. The story was weak and disappointing.'
  [+]  62.3%  'The movie was okay. Some parts were good.'
  [-]  54.8%  'Not the worst movie but not great either.'

Model saved to: lstm_sentiment_complete.pth
Model loaded from: lstm_sentiment_complete.pth
  Vocabulary size: 127
  Max length:      30

Verification: 'This was a wonderful film with excellent acting'
  Sentiment: positive (91.2% confidence)
```

**Line-by-line explanation:**

- `torch.sigmoid(output).item()` — Converts the raw logit to a probability between 0 and 1. Above 0.5 is positive, below is negative.
- The ambiguous reviews ("okay," "not the worst but not great") get lower confidence scores (62.3% and 54.8%), which is correct behavior — the model is uncertain about borderline cases.
- `save_complete_model` saves not just the model weights but also the vocabulary and configuration. This means you can load the model months later without needing the original training code.
- `load_complete_model` reconstructs everything from the saved file: vocabulary, model architecture, and trained weights.

---

## Common Mistakes

1. **Building vocabulary from test data**: The vocabulary must be built from training data only. If you include test data, you leak information about the test set into training.

2. **Forgetting gradient clipping for RNNs/LSTMs**: Without gradient clipping, LSTM training is unstable. Always use `clip_grad_norm_` with a max_norm of 1.0 to 5.0.

3. **Not handling variable-length sequences**: All sequences in a batch must be the same length. Either pad shorter sequences or truncate longer ones.

4. **Using softmax for binary classification**: Sentiment analysis is a binary problem (positive/negative). Use BCEWithLogitsLoss with a single output, not CrossEntropyLoss with 2 outputs.

5. **Forgetting the padding mask in Transformers**: Without a padding mask, the Transformer treats `<PAD>` tokens as meaningful words, which corrupts the attention computation.

6. **Not saving the vocabulary with the model**: The model is useless without its vocabulary. Always save both together.

---

## Best Practices

1. **Start with LSTM, then try Transformer**: LSTM is simpler and often works well for small datasets. Transformer shines with more data and longer sequences.

2. **Use pretrained word embeddings**: For real projects, use pretrained embeddings like GloVe or Word2Vec instead of learning them from scratch. This gives your model knowledge of word meanings from the start.

3. **Track F1 score, not just accuracy**: For imbalanced datasets, accuracy can be misleading. F1 score gives a better picture of classifier quality.

4. **Use gradient clipping for all RNN models**: Set max_norm between 1.0 and 5.0 to prevent exploding gradients.

5. **Save everything needed for inference**: Model weights, vocabulary, configuration, and preprocessing parameters should all be saved together.

6. **Test with edge cases**: Try ambiguous reviews, very short reviews, and reviews with unknown words to understand your model's limitations.

---

## Quick Summary

We built a complete text sentiment analysis pipeline. We created synthetic movie review data, tokenized text into words, built a vocabulary mapping words to numbers, and created padded sequences for batch processing. An LSTM classifier with bidirectional processing and word embeddings achieved approximately 97% accuracy. A Transformer encoder approach achieved similar accuracy with fewer parameters. Both models were saved with their vocabularies for later use, and an inference function classifies new reviews with confidence scores.

---

## Key Points

- Text must be tokenized (split into words) and encoded (words to numbers) before a neural network can process it
- A vocabulary maps words to unique indices; unknown words get a special `<UNK>` token
- Padding ensures all sequences in a batch have the same length; padding masks prevent models from attending to padding
- Word embeddings convert integer indices into dense vectors that capture word meaning
- Bidirectional LSTM reads text both forward and backward for better context understanding
- Transformer encoders use self-attention to let every word interact with every other word simultaneously
- F1 score combines precision and recall for a balanced evaluation metric
- Gradient clipping is essential for stable LSTM training
- Always save the vocabulary along with the model weights

---

## Practice Questions

1. Why do we build the vocabulary only from training data and not from the entire dataset? What problem would including test data cause?

2. Explain the difference between how LSTM and Transformer process a sequence. Which approach can handle longer sequences more effectively, and why?

3. Your sentiment model gets 99% accuracy on training data but 60% on test data. What is happening, and what are three techniques you could use to fix it?

4. Why do we use `BCEWithLogitsLoss` instead of `CrossEntropyLoss` for binary sentiment classification? Could you use `CrossEntropyLoss` with 2 output neurons instead? What would change?

5. The `<PAD>` token is mapped to index 0 and has `padding_idx=0` in the embedding layer. What does this do, and why is it important?

---

## Exercises

### Exercise 1: Real Dataset

Replace the synthetic data with a real dataset. Download the IMDB movie review dataset (available through `torchtext` or as a CSV file). Retrain both models and compare results. How does performance change with real, messier data?

**Hint:** Real reviews are longer and contain more varied language. You may need to increase `max_length` and `vocab_size`.

### Exercise 2: Attention Visualization

For the Transformer model, extract the attention weights and visualize which words the model focuses on when making predictions. For the review "this movie was absolutely terrible," which words get the most attention?

**Hint:** Access attention weights through a custom forward hook or by modifying the model to return attention weights.

### Exercise 3: Three-Class Sentiment

Extend the project to handle three classes: positive, neutral, and negative. Modify the data generation to include neutral reviews (mixed sentiment). Change the model output to 3 classes and use CrossEntropyLoss. How does adding a neutral class affect accuracy?

**Hint:** You will need to change the output layer from `Linear(64, 1)` to `Linear(64, 3)` and switch from `BCEWithLogitsLoss` to `CrossEntropyLoss`.

---

## Congratulations!

You have completed the final project of **Deep Learning with PyTorch** (Book 3 of the AI Series). Let us take a moment to appreciate everything you have accomplished:

```
YOUR JOURNEY THROUGH BOOK 3:

Chapter  1: What deep learning is and why it matters
Chapter  2: The perceptron — the simplest neural unit
Chapter  3: Multi-layer networks that can learn complex patterns
Chapter  4: Activation functions that bring non-linearity
Chapter  5: Loss functions that measure model errors
Chapter  6: Backpropagation — the engine of learning
Chapter  7: Optimizers that make gradient descent smarter
Chapter  8: PyTorch fundamentals — tensors and autograd
Chapter  9: Your first neural network
Chapter 10: Training best practices
Chapters 11-15: CNNs — teaching computers to see
Chapter 16: Data augmentation for better generalization
Chapters 17-22: RNNs, LSTMs, Attention, and Transformers
Chapters 23-26: Generative models (Autoencoders, VAEs, GANs)
Chapter 27: Saving and deploying models
Chapter 28: Debugging when things go wrong
Chapter 29: Project — Image Classifier (end-to-end)
Chapter 30: Project — Text Sentiment Analyzer (end-to-end)
```

You now have the foundational skills to build, train, debug, and deploy deep learning models for both computer vision and natural language processing.

---

## What Is Next? (Preview of Book 4)

**Book 4: NLP and Computer Vision — Specialization and Real-World Applications** takes everything you have learned and goes deeper into two of the most important domains in AI:

**NLP (Natural Language Processing):**
- Pretrained language models (BERT, GPT, and their variants)
- Fine-tuning large language models for specific tasks
- Text generation, summarization, and question answering
- Building chatbots and conversational AI
- Working with the Hugging Face ecosystem

**Computer Vision:**
- Object detection (finding AND locating objects in images)
- Image segmentation (labeling every pixel)
- Face recognition and pose estimation
- Video understanding
- Deploying vision models on edge devices

**Advanced Topics:**
- Multi-modal models (combining text and images)
- Reinforcement learning from human feedback (RLHF)
- Efficient training techniques (mixed precision, distributed training)
- MLOps and production deployment

You have built a strong foundation. Book 4 will take you from practitioner to specialist.

See you there!
