# Chapter 6: Named Entity Recognition — Finding Names, Places, and Dates in Text

## What You Will Learn

- What Named Entity Recognition (NER) is and why it matters in real applications
- The main entity types: PERSON, ORG, LOC, DATE, and others
- How NER works under the hood with BIO tagging
- Using spaCy for named entity recognition with practical examples
- Using the Hugging Face NER pipeline for transformer-based NER
- Visualizing entities in text with color-coded displays
- An overview of how to train your own custom NER model

## Why This Chapter Matters

Imagine you receive a thousand news articles and need to find every person, company, and location mentioned in them. Reading each article manually would take days. But a computer can do this in seconds using Named Entity Recognition.

NER is everywhere in the real world. When your email app detects a date like "March 15th" and offers to add it to your calendar, that is NER. When a search engine knows that "Apple" in "Apple released a new iPhone" refers to a company and not a fruit, that is NER. When a news aggregator groups articles by the people and organizations they mention, that is NER.

Named Entity Recognition is one of the most practical and widely used NLP tasks. It forms the backbone of information extraction, question answering, and knowledge graph construction. After this chapter, you will be able to automatically extract structured information from unstructured text.

---

## 6.1 What Is Named Entity Recognition?

**Named Entity Recognition** (NER) is the task of finding and classifying important "things" in text. These things are called **named entities** because they have specific names. They are not ordinary words like "run" or "beautiful." They are proper nouns and specific references like "Albert Einstein," "Google," or "January 5, 2024."

Think of NER like a highlighter pen. You read through a document and highlight every person's name in yellow, every organization in green, every location in blue, and every date in orange. NER does exactly this, but automatically.

```
+------------------------------------------------------------------+
|              What NER Does                                        |
+------------------------------------------------------------------+
|                                                                   |
|  Input text:                                                      |
|  "Barack Obama visited Google headquarters in Mountain View       |
|   on January 15, 2023."                                          |
|                                                                   |
|  NER output:                                                      |
|  [Barack Obama]  --> PERSON                                       |
|  [Google]        --> ORGANIZATION                                 |
|  [Mountain View] --> LOCATION                                     |
|  [January 15, 2023] --> DATE                                     |
|                                                                   |
|  NER finds the "named things" and labels their type.             |
|                                                                   |
+------------------------------------------------------------------+
```

The word **entity** means a thing that exists. A **named entity** is a thing that has a specific name. The word **recognition** means identifying or detecting something. So NER means detecting named things in text.

---

## 6.2 Entity Types — What Can NER Find?

NER models are trained to recognize different categories of entities. The most common entity types are:

```
+------------------------------------------------------------------+
|              Common Entity Types                                  |
+------------------------------------------------------------------+
|                                                                   |
|  Type       | Label    | Examples                                 |
|  -----------|----------|----------------------------------------  |
|  Person     | PERSON   | Elon Musk, Marie Curie, LeBron James     |
|  Org        | ORG      | Google, United Nations, MIT              |
|  Location   | LOC      | Paris, Mount Everest, Pacific Ocean      |
|  Geo-Pol    | GPE      | France, New York City, Texas             |
|  Date       | DATE     | January 5, 2024, last Tuesday            |
|  Time       | TIME     | 3:30 PM, noon, midnight                  |
|  Money      | MONEY    | $500, 3.2 million euros                  |
|  Percent    | PERCENT  | 45%, three percent                       |
|  Product    | PRODUCT  | iPhone, Boeing 747                       |
|  Event      | EVENT    | World War II, Olympics                   |
|                                                                   |
+------------------------------------------------------------------+
```

The difference between **LOC** and **GPE** can be confusing. **LOC** (Location) refers to natural geographic features like mountains, rivers, and oceans. **GPE** (Geo-Political Entity) refers to countries, cities, and states — places with governments. Some NER systems combine them into a single LOCATION type.

```python
# Let us see entity types in action with simple examples

entity_examples = {
    "PERSON": ["Albert Einstein", "Serena Williams", "Leonardo da Vinci"],
    "ORG": ["Microsoft", "World Health Organization", "Harvard University"],
    "GPE": ["Japan", "New York City", "California"],
    "LOC": ["Mount Everest", "Nile River", "Pacific Ocean"],
    "DATE": ["January 5, 2024", "last Monday", "the 1990s"],
    "TIME": ["3:30 PM", "noon", "midnight"],
    "MONEY": ["$500", "50 euros", "3.2 million dollars"],
    "PERCENT": ["45%", "three percent", "0.5%"],
}

print("Common Named Entity Types")
print("=" * 55)
for entity_type, examples in entity_examples.items():
    print(f"\n{entity_type}:")
    for example in examples:
        print(f"  - {example}")
```

**Expected Output:**
```
Common Named Entity Types
=======================================================

PERSON:
  - Albert Einstein
  - Serena Williams
  - Leonardo da Vinci

ORG:
  - Microsoft
  - World Health Organization
  - Harvard University

GPE:
  - Japan
  - New York City
  - California

LOC:
  - Mount Everest
  - Nile River
  - Pacific Ocean

DATE:
  - January 5, 2024
  - last Monday
  - the 1990s

TIME:
  - 3:30 PM
  - noon
  - midnight

MONEY:
  - $500
  - 50 euros
  - 3.2 million dollars

PERCENT:
  - 45%
  - three percent
  - 0.5%
```

---

## 6.3 How NER Works: BIO Tagging

Under the hood, NER is a **token classification** task. The model looks at each word (token) in the sentence and assigns it a label. But there is a problem: some entities span multiple words. "New York City" is one entity (a GPE), but it has three words.

To handle multi-word entities, NER uses a tagging scheme called **BIO tagging**:

- **B** = Beginning of an entity (the first word)
- **I** = Inside an entity (continuation words)
- **O** = Outside any entity (not part of an entity)

The word **BIO** comes from the first letters of Beginning, Inside, and Outside.

```
+------------------------------------------------------------------+
|              BIO Tagging Explained                                |
+------------------------------------------------------------------+
|                                                                   |
|  Sentence: "Barack Obama visited New York City"                   |
|                                                                   |
|  Word     | BIO Tag       | Meaning                              |
|  ---------|---------------|------------------------------------  |
|  Barack   | B-PERSON      | Beginning of a PERSON entity         |
|  Obama    | I-PERSON      | Inside (continuation of) PERSON      |
|  visited  | O             | Outside — not an entity              |
|  New      | B-GPE         | Beginning of a GPE entity            |
|  York     | I-GPE         | Inside GPE                           |
|  City     | I-GPE         | Inside GPE                           |
|                                                                   |
+------------------------------------------------------------------+
```

```python
# Demonstrating BIO tagging

sentence = "Barack Obama visited New York City on January 15".split()

# BIO tags for each word
bio_tags = [
    "B-PERSON",   # Barack — beginning of person name
    "I-PERSON",   # Obama — continuation of person name
    "O",          # visited — not an entity
    "B-GPE",      # New — beginning of geo-political entity
    "I-GPE",      # York — continuation
    "I-GPE",      # City — continuation
    "O",          # on — not an entity
    "B-DATE",     # January — beginning of date
    "I-DATE",     # 15 — continuation of date
]

print("BIO Tagging Example")
print("=" * 45)
print(f"{'Word':<12} {'BIO Tag':<14} {'Meaning'}")
print("-" * 45)

for word, tag in zip(sentence, bio_tags):
    if tag == "O":
        meaning = "Not an entity"
    elif tag.startswith("B-"):
        meaning = f"Start of {tag[2:]}"
    else:
        meaning = f"Continues {tag[2:]}"
    print(f"{word:<12} {tag:<14} {meaning}")

# Reconstruct entities from BIO tags
print("\nReconstructed Entities:")
print("-" * 45)

current_entity = []
current_type = None

for word, tag in zip(sentence + [""], bio_tags + ["O"]):
    if tag.startswith("B-"):
        # Save previous entity if exists
        if current_entity:
            print(f"  {' '.join(current_entity)} --> {current_type}")
        current_entity = [word]
        current_type = tag[2:]
    elif tag.startswith("I-"):
        current_entity.append(word)
    else:
        if current_entity:
            print(f"  {' '.join(current_entity)} --> {current_type}")
        current_entity = []
        current_type = None
```

**Expected Output:**
```
BIO Tagging Example
=============================================
Word         BIO Tag        Meaning
---------------------------------------------
Barack       B-PERSON       Start of PERSON
Obama        I-PERSON       Continues PERSON
visited      O              Not an entity
New          B-GPE          Start of GPE
York         I-GPE          Continues GPE
City         I-GPE          Continues GPE
on           O              Not an entity
January      B-DATE         Start of DATE
15           I-DATE         Continues DATE

Reconstructed Entities:
---------------------------------------------
  Barack Obama --> PERSON
  New York City --> GPE
  January 15 --> DATE
```

---

## 6.4 NER with spaCy

**spaCy** is a popular Python library for NLP. It comes with pre-trained NER models that work out of the box. The word "spaCy" is just the library's name (pronounced "spay-see").

First, install spaCy and download a pre-trained English model:

```bash
pip install spacy
python -m spacy download en_core_web_sm
```

The model name `en_core_web_sm` means: English (`en`), core features (`core`), trained on web text (`web`), small size (`sm`). Larger models like `en_core_web_lg` are more accurate but require more memory.

```python
import spacy

# Load the pre-trained English model
nlp = spacy.load("en_core_web_sm")

# Process a sentence
text = "Apple CEO Tim Cook announced new products in San Francisco on Tuesday."
doc = nlp(text)

# Extract named entities
print("Named Entities Found:")
print("=" * 55)
print(f"{'Entity':<25} {'Label':<10} {'Description'}")
print("-" * 55)

for ent in doc.ents:
    print(f"{ent.text:<25} {ent.label_:<10} {spacy.explain(ent.label_)}")
```

**Expected Output:**
```
Named Entities Found:
=======================================================
Entity                    Label      Description
-------------------------------------------------------
Apple                     ORG        Companies, agencies, institutions, etc.
Tim Cook                  PERSON     People, including fictional
San Francisco             GPE        Countries, cities, states
Tuesday                   DATE       Absolute or relative dates or periods
```

Let us break down this code line by line:

- `spacy.load("en_core_web_sm")` loads the pre-trained model into memory. This model already knows how to recognize entities.
- `nlp(text)` processes the text through the entire spaCy pipeline (tokenization, part-of-speech tagging, NER, and more). It returns a `Doc` object.
- `doc.ents` is a list of all entities found in the text. Each entity has `.text` (the actual text), `.label_` (the entity type), and other attributes.
- `spacy.explain(ent.label_)` gives a human-readable description of what each label means.

```python
import spacy

nlp = spacy.load("en_core_web_sm")

# Try with a longer, more complex text
text = """
Elon Musk, the CEO of Tesla and SpaceX, met with President Biden
at the White House on December 3, 2023. They discussed a $2 billion
investment plan that could create 50,000 jobs across the United States.
The meeting lasted about three hours.
"""

doc = nlp(text)

print("Entities in a Complex Text:")
print("=" * 60)

# Group entities by type
from collections import defaultdict
entities_by_type = defaultdict(list)

for ent in doc.ents:
    entities_by_type[ent.label_].append(ent.text)

for label, entities in sorted(entities_by_type.items()):
    print(f"\n{label} ({spacy.explain(label)}):")
    for entity in entities:
        print(f"  - {entity}")
```

**Expected Output:**
```
Entities in a Complex Text:
============================================================

CARDINAL (Numerals that do not fall under another type):
  - 50,000

DATE (Absolute or relative dates or periods):
  - December 3, 2023
  - about three hours

GPE (Countries, cities, states):
  - the United States

MONEY (Monetary values, including unit):
  - $2 billion

ORG (Companies, agencies, institutions, etc.):
  - Tesla
  - SpaceX

PERSON (People, including fictional):
  - Elon Musk
  - Biden

FAC (Buildings, airports, highways, bridges, etc.):
  - the White House
```

---

## 6.5 Understanding Entity Positions

Each entity also tells you exactly where in the text it appears. This is useful when you need to know the character positions for highlighting or further processing.

```python
import spacy

nlp = spacy.load("en_core_web_sm")

text = "Marie Curie won the Nobel Prize in Paris in 1903."
doc = nlp(text)

print("Entity Positions:")
print("=" * 65)
print(f"{'Entity':<18} {'Label':<10} {'Start':<8} {'End':<8} {'Char Span'}")
print("-" * 65)

for ent in doc.ents:
    print(f"{ent.text:<18} {ent.label_:<10} {ent.start_char:<8} {ent.end_char:<8} "
          f"text[{ent.start_char}:{ent.end_char}]")

# Verify the positions
print("\nVerification:")
for ent in doc.ents:
    extracted = text[ent.start_char:ent.end_char]
    print(f"  text[{ent.start_char}:{ent.end_char}] = '{extracted}'")
```

**Expected Output:**
```
Entity Positions:
=================================================================
Entity             Label      Start    End      Char Span
-----------------------------------------------------------------
Marie Curie        PERSON     0        11       text[0:11]
the Nobel Prize    WORK_OF_ART 16      31       text[16:31]
Paris              GPE        35       40       text[35:40]
1903               DATE       44       48       text[44:48]

Verification:
  text[0:11] = 'Marie Curie'
  text[16:31] = 'the Nobel Prize'
  text[35:40] = 'Paris'
  text[44:48] = '1903'
```

---

## 6.6 Hugging Face NER Pipeline

While spaCy is excellent, Hugging Face transformers can be even more accurate because they use large pre-trained models like BERT. The **Hugging Face NER pipeline** makes it simple to use transformer-based NER.

```bash
pip install transformers torch
```

```python
from transformers import pipeline

# Create a NER pipeline
# This downloads a pre-trained BERT model fine-tuned for NER
ner_pipeline = pipeline(
    "ner",
    model="dslim/bert-base-NER",
    aggregation_strategy="simple"
)

text = "Elon Musk founded SpaceX in Hawthorne, California in 2002."

# Run NER
results = ner_pipeline(text)

print("Hugging Face NER Results:")
print("=" * 65)
print(f"{'Entity':<22} {'Type':<10} {'Score':<8} {'Position'}")
print("-" * 65)

for entity in results:
    print(f"{entity['word']:<22} {entity['entity_group']:<10} "
          f"{entity['score']:.4f}  chars {entity['start']}-{entity['end']}")
```

**Expected Output:**
```
Hugging Face NER Results:
=================================================================
Entity                 Type       Score    Position
-----------------------------------------------------------------
Elon Musk              PER        0.9987  chars 0-9
SpaceX                 ORG        0.9993  chars 18-24
Hawthorne              LOC        0.9976  chars 28-37
California             LOC        0.9991  chars 39-49
```

Let us break down the key parts:

- `pipeline("ner", ...)` creates a NER pipeline. The word **pipeline** means a sequence of processing steps packaged together.
- `model="dslim/bert-base-NER"` specifies a BERT model that has been fine-tuned (additionally trained) specifically for NER.
- `aggregation_strategy="simple"` tells the pipeline to group sub-word tokens back into complete words. Without this, "Elon" might appear as "El" and "##on" separately.
- Each result includes a **confidence score** between 0 and 1. Higher scores mean the model is more confident about its prediction.

```
+------------------------------------------------------------------+
|              spaCy vs Hugging Face NER                            |
+------------------------------------------------------------------+
|                                                                   |
|  spaCy:                                                           |
|  + Fast and lightweight                                           |
|  + Easy to use                                                    |
|  + Good for most applications                                     |
|  + Built-in visualization                                         |
|  - Less accurate on complex text                                  |
|                                                                   |
|  Hugging Face Transformers:                                       |
|  + More accurate (uses BERT/RoBERTa)                              |
|  + State-of-the-art results                                       |
|  + Many specialized models available                              |
|  - Slower (larger models)                                         |
|  - Requires more memory                                           |
|                                                                   |
+------------------------------------------------------------------+
```

```python
from transformers import pipeline

# Compare results on a tricky sentence
ner_pipeline = pipeline(
    "ner",
    model="dslim/bert-base-NER",
    aggregation_strategy="simple"
)

# Sentences that are harder for NER
tricky_texts = [
    "Jordan played basketball in Jordan.",
    "Apple stock rose after Apple released the Apple Watch.",
    "Dr. Martin Luther King Jr. spoke in Washington D.C.",
]

for text in tricky_texts:
    print(f"\nText: '{text}'")
    results = ner_pipeline(text)
    if results:
        for r in results:
            print(f"  [{r['word']}] -> {r['entity_group']} "
                  f"(confidence: {r['score']:.2%})")
    else:
        print("  No entities found")
    print()
```

**Expected Output:**
```
Text: 'Jordan played basketball in Jordan.'
  [Jordan] -> PER (confidence: 98.43%)
  [Jordan] -> LOC (confidence: 95.67%)

Text: 'Apple stock rose after Apple released the Apple Watch.'
  [Apple] -> ORG (confidence: 99.12%)
  [Apple] -> ORG (confidence: 99.34%)
  [Apple Watch] -> MISC (confidence: 78.21%)

Text: 'Dr. Martin Luther King Jr. spoke in Washington D.C.'
  [Martin Luther King Jr.] -> PER (confidence: 99.87%)
  [Washington D.C.] -> LOC (confidence: 99.45%)
```

Notice how the model correctly distinguishes "Jordan" (the person) from "Jordan" (the country) based on context. This is the power of transformer-based models.

---

## 6.7 Visualizing Named Entities

spaCy provides built-in visualization tools that display entities with color-coded highlights. This is extremely useful for debugging and understanding what the model finds.

```python
import spacy
from spacy import displacy

nlp = spacy.load("en_core_web_sm")

text = """NASA astronaut Jessica Watkins made history at the
International Space Station on April 27, 2022. The SpaceX Crew
Dragon spacecraft launched from Kennedy Space Center in Florida."""

doc = nlp(text)

# Generate HTML visualization (for Jupyter notebooks)
# displacy.render(doc, style="ent", jupyter=True)

# For scripts, save as HTML file
html = displacy.render(doc, style="ent", page=True)
with open("ner_visualization.html", "w") as f:
    f.write(html)
print("Visualization saved to ner_visualization.html")

# Text-based visualization for the terminal
print("\nText-Based Entity Visualization:")
print("=" * 60)

# Build a simple text visualization
result = ""
last_end = 0
for ent in doc.ents:
    # Add text before the entity
    result += text[last_end:ent.start_char]
    # Add the entity with markers
    result += f"[{ent.text}]({ent.label_})"
    last_end = ent.end_char
result += text[last_end:]

print(result)
```

**Expected Output:**
```
Visualization saved to ner_visualization.html

Text-Based Entity Visualization:
============================================================
[NASA](ORG) astronaut [Jessica Watkins](PERSON) made history at the
[International Space Station](FAC) on [April 27, 2022](DATE). The [SpaceX](ORG) Crew
Dragon spacecraft launched from [Kennedy Space Center](FAC) in [Florida](GPE).
```

```python
import spacy

nlp = spacy.load("en_core_web_sm")

# Create a colored terminal visualization
def visualize_entities_terminal(text, nlp):
    """Display entities with ASCII markers in the terminal."""
    doc = nlp(text)

    if not doc.ents:
        print("No entities found.")
        return

    # Print the original text
    print(f"\nOriginal: {text}\n")

    # Print entity annotations
    print("Entities found:")
    print("-" * 50)

    for ent in doc.ents:
        # Create a pointer showing where the entity is
        pointer = " " * ent.start_char + "^" * len(ent.text)
        label_line = " " * ent.start_char + ent.label_
        print(f"  Text:  '{ent.text}'")
        print(f"  Type:  {ent.label_} ({spacy.explain(ent.label_)})")
        print(f"  Pos:   characters {ent.start_char} to {ent.end_char}")
        print()

# Test with different sentences
sentences = [
    "Jeff Bezos started Amazon in his garage in Seattle in 1994.",
    "The European Union signed a trade deal worth 50 billion euros.",
    "Taylor Swift performed at Madison Square Garden last Friday.",
]

for sentence in sentences:
    visualize_entities_terminal(sentence, nlp)
    print("=" * 60)
```

**Expected Output:**
```
Original: Jeff Bezos started Amazon in his garage in Seattle in 1994.

Entities found:
--------------------------------------------------
  Text:  'Jeff Bezos'
  Type:  PERSON (People, including fictional)
  Pos:   characters 0 to 10

  Text:  'Amazon'
  Type:  ORG (Companies, agencies, institutions, etc.)
  Pos:   characters 19 to 25

  Text:  'Seattle'
  Type:  GPE (Countries, cities, states)
  Pos:   characters 43 to 50

  Text:  '1994'
  Type:  DATE (Absolute or relative dates or periods)
  Pos:   characters 54 to 58

============================================================

Original: The European Union signed a trade deal worth 50 billion euros.

Entities found:
--------------------------------------------------
  Text:  'The European Union'
  Type:  ORG (Companies, agencies, institutions, etc.)
  Pos:   characters 0 to 18

  Text:  '50 billion euros'
  Type:  MONEY (Monetary values, including unit)
  Pos:   characters 45 to 61

============================================================

Original: Taylor Swift performed at Madison Square Garden last Friday.

Entities found:
--------------------------------------------------
  Text:  'Taylor Swift'
  Type:  PERSON (People, including fictional)
  Pos:   characters 0 to 12

  Text:  'Madison Square Garden'
  Type:  FAC (Buildings, airports, highways, bridges, etc.)
  Pos:   characters 27 to 48

  Text:  'last Friday'
  Type:  DATE (Absolute or relative dates or periods)
  Pos:   characters 49 to 60

============================================================
```

---

## 6.8 Custom NER Training Overview

Pre-trained models work well for common entity types like PERSON, ORG, and DATE. But what if you need to recognize custom entities? For example, a medical system might need to find DRUG names and SYMPTOM descriptions. A legal system might need to find CASE_NUMBER and STATUTE entities.

This is where **custom NER training** comes in. You train a model on your own labeled data to recognize your specific entity types.

```
+------------------------------------------------------------------+
|              Custom NER Training Process                          |
+------------------------------------------------------------------+
|                                                                   |
|  Step 1: Define your entity types                                |
|  +-----------------------+                                        |
|  | DRUG, SYMPTOM, DOSAGE |                                        |
|  +-----------------------+                                        |
|          |                                                        |
|          v                                                        |
|  Step 2: Label training data                                     |
|  +-----------------------------------------------+               |
|  | "Take [Aspirin](DRUG) for [headache](SYMPTOM) |               |
|  |  at a dose of [500mg](DOSAGE)"                |               |
|  +-----------------------------------------------+               |
|          |                                                        |
|          v                                                        |
|  Step 3: Train the model                                         |
|  +-----------------------------+                                  |
|  | Feed labeled data to model  |                                  |
|  | Model learns patterns       |                                  |
|  +-----------------------------+                                  |
|          |                                                        |
|          v                                                        |
|  Step 4: Evaluate and use                                        |
|  +-----------------------------+                                  |
|  | Test on new, unseen text    |                                  |
|  | Deploy in your application  |                                  |
|  +-----------------------------+                                  |
|                                                                   |
+------------------------------------------------------------------+
```

Here is a simplified example of preparing training data and training a spaCy NER model:

```python
import spacy
from spacy.training import Example

# Step 1: Prepare training data
# Format: (text, {"entities": [(start, end, label)]})
TRAIN_DATA = [
    ("Take Aspirin for headaches", {
        "entities": [(5, 12, "DRUG"), (17, 26, "SYMPTOM")]
    }),
    ("Ibuprofen helps with joint pain", {
        "entities": [(0, 9, "DRUG"), (21, 31, "SYMPTOM")]
    }),
    ("Prescribe Metformin for diabetes", {
        "entities": [(10, 19, "DRUG"), (24, 32, "SYMPTOM")]
    }),
    ("Amoxicillin treats bacterial infections", {
        "entities": [(0, 11, "DRUG"), (19, 39, "SYMPTOM")]
    }),
]

print("Training Data Format:")
print("=" * 55)
for text, annotations in TRAIN_DATA:
    print(f"\n  Text: '{text}'")
    for start, end, label in annotations["entities"]:
        print(f"    [{text[start:end]}] -> {label}")

# Step 2: Create a blank model and add NER
nlp = spacy.blank("en")
ner = nlp.add_pipe("ner")

# Add custom entity labels
for _, annotations in TRAIN_DATA:
    for start, end, label in annotations["entities"]:
        ner.add_label(label)

print("\n\nCustom Entity Labels Added:")
print(f"  {ner.labels}")

# Step 3: Training loop (simplified)
print("\n\nTraining (simplified demo):")
print("-" * 40)

# Initialize the model
nlp.initialize()

import random

for epoch in range(10):
    random.shuffle(TRAIN_DATA)
    losses = {}

    for text, annotations in TRAIN_DATA:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        losses = nlp.update([example])

    if epoch % 3 == 0:
        print(f"  Epoch {epoch + 1:>2}: loss = {losses['ner']:.4f}")

print(f"  Epoch 10: loss = {losses['ner']:.4f}")

# Step 4: Test the trained model
print("\n\nTesting Custom NER Model:")
print("-" * 40)
test_texts = [
    "Prescribe Aspirin for chest pain",
    "Use Ibuprofen to treat fever",
]

for text in test_texts:
    doc = nlp(text)
    print(f"\n  Text: '{text}'")
    for ent in doc.ents:
        print(f"    [{ent.text}] -> {ent.label_}")
```

**Expected Output:**
```
Training Data Format:
=======================================================

  Text: 'Take Aspirin for headaches'
    [Aspirin] -> DRUG
    [headaches] -> SYMPTOM

  Text: 'Ibuprofen helps with joint pain'
    [Ibuprofen] -> DRUG
    [joint pain] -> SYMPTOM

  Text: 'Prescribe Metformin for diabetes'
    [Metformin] -> DRUG
    [diabetes] -> SYMPTOM

  Text: 'Amoxicillin treats bacterial infections'
    [Amoxicillin] -> DRUG
    [bacterial infections] -> SYMPTOM


Custom Entity Labels Added:
  ('DRUG', 'SYMPTOM')


Training (simplified demo):
----------------------------------------
  Epoch  1: loss = 8.3421
  Epoch  4: loss = 2.1056
  Epoch  7: loss = 0.4523
  Epoch 10: loss = 0.0891


Testing Custom NER Model:
----------------------------------------

  Text: 'Prescribe Aspirin for chest pain'
    [Aspirin] -> DRUG
    [chest pain] -> SYMPTOM

  Text: 'Use Ibuprofen to treat fever'
    [Ibuprofen] -> DRUG
    [fever] -> SYMPTOM
```

> **Important Note:** This is a simplified demo with very little training data. In a real project, you would need hundreds or thousands of labeled examples for good results. The training data shown here is just to illustrate the process.

---

## 6.9 Practical NER: Extracting Information from News

Let us build a practical example that extracts structured information from news-style text.

```python
import spacy
from collections import defaultdict

nlp = spacy.load("en_core_web_sm")

# Simulate processing multiple news snippets
news_texts = [
    "Microsoft announced a $69 billion deal to acquire Activision Blizzard "
    "on January 18, 2022.",

    "Tesla CEO Elon Musk opened a new Gigafactory in Austin, Texas, "
    "creating over 10,000 new jobs.",

    "The United Nations held a climate summit in Geneva, Switzerland, "
    "where leaders from 195 countries gathered on November 30, 2023.",
]

print("News Entity Extraction Report")
print("=" * 60)

all_people = []
all_orgs = []
all_locations = []
all_dates = []
all_money = []

for i, text in enumerate(news_texts, 1):
    doc = nlp(text)
    print(f"\n--- Article {i} ---")
    print(f"Text: {text[:80]}...")

    entities_found = defaultdict(list)
    for ent in doc.ents:
        entities_found[ent.label_].append(ent.text)

        # Collect for summary
        if ent.label_ == "PERSON":
            all_people.append(ent.text)
        elif ent.label_ == "ORG":
            all_orgs.append(ent.text)
        elif ent.label_ in ("GPE", "LOC"):
            all_locations.append(ent.text)
        elif ent.label_ == "DATE":
            all_dates.append(ent.text)
        elif ent.label_ == "MONEY":
            all_money.append(ent.text)

    for label, entities in sorted(entities_found.items()):
        print(f"  {label}: {', '.join(entities)}")

# Summary across all articles
print("\n" + "=" * 60)
print("SUMMARY ACROSS ALL ARTICLES")
print("=" * 60)
print(f"  People mentioned:    {', '.join(set(all_people)) or 'None'}")
print(f"  Organizations:       {', '.join(set(all_orgs))}")
print(f"  Locations:           {', '.join(set(all_locations))}")
print(f"  Dates:               {', '.join(set(all_dates))}")
print(f"  Money:               {', '.join(set(all_money)) or 'None'}")
```

**Expected Output:**
```
News Entity Extraction Report
============================================================

--- Article 1 ---
Text: Microsoft announced a $69 billion deal to acquire Activision Blizzard on Jan...
  DATE: January 18, 2022
  MONEY: $69 billion
  ORG: Microsoft, Activision Blizzard

--- Article 2 ---
Text: Tesla CEO Elon Musk opened a new Gigafactory in Austin, Texas, creating over...
  CARDINAL: over 10,000
  GPE: Austin, Texas
  ORG: Tesla
  PERSON: Elon Musk

--- Article 3 ---
Text: The United Nations held a climate summit in Geneva, Switzerland, where leader...
  CARDINAL: 195
  DATE: November 30, 2023
  GPE: Geneva, Switzerland
  ORG: The United Nations

============================================================
SUMMARY ACROSS ALL ARTICLES
============================================================
  People mentioned:    Elon Musk
  Organizations:       Tesla, Microsoft, Activision Blizzard, The United Nations
  Locations:           Austin, Texas, Geneva, Switzerland
  Dates:               January 18, 2022, November 30, 2023
  Money:               $69 billion
```

---

## Common Mistakes

1. **Forgetting aggregation_strategy in Hugging Face.** Without `aggregation_strategy="simple"`, the pipeline returns sub-word tokens instead of complete words. "Barack" might appear as "Bar" and "##ack".

2. **Assuming NER is always correct.** NER models make mistakes, especially with ambiguous words. "Apple" can be a company or a fruit. "Jordan" can be a person or a country. Always review results for critical applications.

3. **Using the wrong spaCy model.** The small model (`en_core_web_sm`) is less accurate than the large model (`en_core_web_lg`). For production use, prefer the larger model.

4. **Not handling overlapping entities.** Some models may produce overlapping entity spans. Always check for this in your post-processing code.

5. **Training custom NER with too little data.** A few examples are not enough. You typically need at least 200-500 labeled examples per entity type for reasonable accuracy.

---

## Best Practices

1. **Choose the right tool for your task.** Use spaCy for fast, general-purpose NER. Use Hugging Face transformers when you need maximum accuracy on complex text.

2. **Check confidence scores.** When using Hugging Face, filter results by confidence score. Entities with scores below 0.8 may be unreliable.

3. **Pre-process your text.** Clean up extra whitespace, fix encoding issues, and handle special characters before running NER.

4. **Validate with domain experts.** If building NER for specialized domains (medical, legal, financial), have domain experts review and correct the model's predictions.

5. **Use larger models for production.** Development and testing can use small models for speed, but production deployments benefit from larger, more accurate models.

---

## Quick Summary

Named Entity Recognition (NER) finds and classifies named things in text — people, organizations, locations, dates, and more. It works by assigning a label to each word using the BIO tagging scheme (Beginning, Inside, Outside). spaCy provides fast, easy-to-use NER with built-in visualization. Hugging Face transformers offer more accurate NER using models like BERT. You can also train custom NER models to recognize domain-specific entities like drug names or legal terms.

---

## Key Points

- **NER** identifies named entities (people, organizations, locations, dates) in text.
- **BIO tagging** handles multi-word entities: B = beginning, I = inside, O = outside.
- **spaCy** offers fast, lightweight NER with built-in visualization tools.
- **Hugging Face** provides transformer-based NER with higher accuracy and confidence scores.
- **Custom NER** training requires labeled data and lets you recognize domain-specific entities.
- NER is a **token classification** task — each word gets a label.
- Always check **confidence scores** and be aware that NER models can make mistakes on ambiguous words.

---

## Practice Questions

1. What does NER stand for, and what is its purpose? Explain the difference between PERSON, ORG, and GPE entity types with examples.

2. Explain the BIO tagging scheme. Given the sentence "New York University is in Manhattan," what would the BIO tags be for each word?

3. What is the difference between spaCy NER and Hugging Face NER? When would you choose one over the other?

4. Why does the Hugging Face NER pipeline need `aggregation_strategy="simple"`? What happens if you leave it out?

5. You need to build a NER system that detects product names and prices in e-commerce product descriptions. What steps would you follow?

---

## Exercises

**Exercise 1: Entity Counter**

Write a Python script using spaCy that takes a paragraph of text and produces a summary table showing: (a) how many entities of each type were found, (b) the most frequently mentioned entity, and (c) the percentage of words that are part of an entity.

**Exercise 2: NER Comparison**

Write a script that runs the same text through both spaCy and Hugging Face NER pipelines and compares the results. Create a table showing which entities each system found, which ones they agreed on, and which ones they disagreed on.

**Exercise 3: Custom Entity Extractor**

Create a function that uses NER to extract structured data from job posting text. Given text like "Google is hiring a Senior Python Developer in New York with a salary of $150,000," extract the company name, job title, location, and salary into a dictionary.

---

## What Is Next?

Now that you can extract named entities from text, the next chapter covers **Text Summarization**. You will learn how to automatically condense long documents into short summaries, using both extractive methods (picking important sentences) and abstractive methods (generating new sentences). Text summarization is one of the most popular applications of NLP, used in news aggregation, document processing, and email summarization.
