# Chapter 7: Text Summarization — Condensing Documents into Key Points

## What You Will Learn

- What text summarization is and the two main approaches: extractive and abstractive
- How extractive summarization works by scoring and selecting important sentences
- How abstractive summarization generates new sentences that capture the original meaning
- Building an extractive summarizer from scratch using sentence scoring
- Using the Hugging Face summarization pipeline for abstractive summaries
- Controlling summary length with min_length and max_length parameters
- Evaluating summaries using ROUGE metrics
- A complete end-to-end summarization example

## Why This Chapter Matters

Imagine you are a busy manager who receives a 50-page report every morning. You do not have time to read the whole thing. You need someone to give you the key points in a few paragraphs. That is exactly what text summarization does — it takes a long piece of text and creates a shorter version that captures the most important information.

Text summarization is everywhere. News apps show you article previews. Email clients display message snippets. Search engines show brief descriptions under each result. Legal professionals need summaries of long contracts. Researchers need summaries of scientific papers. Doctors need summaries of patient records.

As the amount of text data in the world grows exponentially, the ability to automatically summarize information becomes critical. After this chapter, you will be able to build systems that condense long documents into concise summaries using both traditional and modern AI approaches.

---

## 7.1 What Is Text Summarization?

**Text summarization** is the task of creating a shorter version of a text while keeping its most important information. Think of it like writing a book report in school — you read an entire book and then write a one-page summary of what happened.

The word **summarization** means making something shorter while keeping the essential meaning. A **summary** is the shortened version.

```
+------------------------------------------------------------------+
|              What Text Summarization Does                         |
+------------------------------------------------------------------+
|                                                                   |
|  Input (long text):                                               |
|  "The Mars rover Perseverance successfully landed on Mars on      |
|   February 18, 2021. The rover is equipped with advanced          |
|   scientific instruments designed to search for signs of          |
|   ancient microbial life. It also carries a small helicopter      |
|   named Ingenuity, which became the first aircraft to achieve    |
|   powered flight on another planet. The mission is part of       |
|   NASA's Mars Exploration Program and cost approximately          |
|   2.7 billion dollars..."                                         |
|                                                                   |
|  Output (summary):                                                |
|  "NASA's Perseverance rover landed on Mars in February 2021       |
|   to search for ancient life. It carries the Ingenuity            |
|   helicopter, the first to fly on another planet."                |
|                                                                   |
+------------------------------------------------------------------+
```

There are two fundamentally different approaches to summarization:

1. **Extractive Summarization** — Selects the most important sentences directly from the original text
2. **Abstractive Summarization** — Generates new sentences that capture the meaning of the original text

Let us understand each approach in detail.

---

## 7.2 Extractive vs. Abstractive Summarization

### Extractive Summarization

**Extractive summarization** works like using a highlighter pen on a printed article. You read through the text and highlight the most important sentences. The summary is just those highlighted sentences copied out. No new words are created — everything in the summary comes directly from the original text.

The word **extractive** comes from "extract," which means to pull out or remove. So extractive summarization pulls out important sentences from the text.

```
+------------------------------------------------------------------+
|              Extractive Summarization                             |
+------------------------------------------------------------------+
|                                                                   |
|  Original text (5 sentences):                                     |
|  1. "The company reported record profits this quarter."           |
|  2. "Sales increased by 35% compared to last year."              |
|  3. "The CEO attributed growth to new product launches."          |
|  4. "Employee count grew from 500 to 750."                       |
|  5. "The board approved a new dividend policy."                   |
|                                                                   |
|  Step 1: Score each sentence for importance                       |
|  Sentence 1: Score = 0.85  <-- HIGH                              |
|  Sentence 2: Score = 0.92  <-- HIGHEST                           |
|  Sentence 3: Score = 0.78                                         |
|  Sentence 4: Score = 0.45                                         |
|  Sentence 5: Score = 0.60                                         |
|                                                                   |
|  Step 2: Select top sentences                                     |
|  Summary: "Sales increased by 35% compared to last year.          |
|           The company reported record profits this quarter."      |
|                                                                   |
|  Notice: These sentences are copied exactly from the original.    |
|                                                                   |
+------------------------------------------------------------------+
```

**Advantages of extractive summarization:**
- Sentences are grammatically correct (they come from the original)
- No risk of generating incorrect facts
- Simpler to implement
- Faster to compute

**Disadvantages of extractive summarization:**
- Summaries can feel choppy or disconnected
- Cannot combine ideas from multiple sentences
- May include unnecessary details within selected sentences
- Limited to the exact words in the original text

### Abstractive Summarization

**Abstractive summarization** works like asking a person to read an article and then explain it in their own words. The summary may contain words and phrases that never appeared in the original text. The model understands the meaning and generates new text that captures that meaning.

The word **abstractive** comes from "abstract," which means a brief summary of a larger work. Abstractive summarization creates an abstract — a new piece of text that conveys the original meaning.

```
+------------------------------------------------------------------+
|              Abstractive Summarization                            |
+------------------------------------------------------------------+
|                                                                   |
|  Original text:                                                   |
|  "The company reported record profits this quarter. Sales         |
|   increased by 35% compared to last year. The CEO attributed     |
|   growth to new product launches."                                |
|                                                                   |
|  Abstractive Summary:                                             |
|  "The company achieved unprecedented financial success with       |
|   a 35% sales surge, driven by new product introductions."       |
|                                                                   |
|  Notice: "unprecedented financial success" and "sales surge"      |
|  are NEW phrases not in the original text. The model              |
|  understood the meaning and expressed it differently.             |
|                                                                   |
+------------------------------------------------------------------+
```

**Advantages of abstractive summarization:**
- More natural and fluent summaries
- Can combine ideas from multiple sentences
- Can rephrase for clarity
- More like how humans summarize

**Disadvantages of abstractive summarization:**
- May generate incorrect facts (called **hallucination**)
- Requires more complex models (usually deep learning)
- Slower to compute
- Harder to verify accuracy

```
+------------------------------------------------------------------+
|         Extractive vs Abstractive: Side by Side                   |
+------------------------------------------------------------------+
|                                                                   |
|  Feature          | Extractive        | Abstractive              |
|  -----------------|-------------------|------------------------  |
|  Method           | Select sentences  | Generate new text        |
|  Output words     | From original     | May be new words         |
|  Grammar          | Always correct    | Usually correct          |
|  Fluency          | Can be choppy     | More natural             |
|  Factual accuracy | High              | Risk of hallucination    |
|  Complexity       | Simpler           | More complex             |
|  Speed            | Faster            | Slower                   |
|  Models used      | Scoring methods   | Seq2seq, Transformers    |
|                                                                   |
+------------------------------------------------------------------+
```

---

## 7.3 Extractive Summarization with Sentence Scoring

Let us build an extractive summarizer from scratch. The idea is simple: we score each sentence based on how important it is, then select the top-scoring sentences.

### How Sentence Scoring Works

The most basic approach scores sentences based on **word frequency**. The idea is that important words appear more often in the text. Sentences that contain many important (frequent) words are likely important sentences.

```
+------------------------------------------------------------------+
|              Sentence Scoring Process                             |
+------------------------------------------------------------------+
|                                                                   |
|  Step 1: Count word frequencies in the entire text                |
|    "profits" -> 5 times                                           |
|    "revenue" -> 4 times                                           |
|    "the"     -> 20 times (stop word, ignore)                     |
|    "growth"  -> 3 times                                           |
|                                                                   |
|  Step 2: Score each sentence                                      |
|    Sentence score = sum of word frequencies in that sentence      |
|                     divided by number of words in the sentence    |
|                                                                   |
|  Step 3: Rank sentences by score                                  |
|                                                                   |
|  Step 4: Select top N sentences for the summary                   |
|                                                                   |
+------------------------------------------------------------------+
```

### Building an Extractive Summarizer

```python
# Extractive summarization using word frequency scoring

import re
from collections import Counter

def extractive_summarize(text, num_sentences=3):
    """
    Summarize text by selecting the most important sentences.

    Parameters:
        text: The input text to summarize
        num_sentences: How many sentences to include in the summary

    Returns:
        A string containing the summary
    """

    # Step 1: Split text into sentences
    # We use a simple regex pattern that splits on periods,
    # exclamation marks, or question marks followed by a space
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    # Remove very short sentences (likely not meaningful)
    sentences = [s for s in sentences if len(s.split()) > 3]

    # Step 2: Define stop words (common words that are not important)
    stop_words = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
        'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'could', 'should', 'may', 'might', 'shall', 'can',
        'of', 'in', 'to', 'for', 'with', 'on', 'at', 'by', 'from',
        'as', 'into', 'through', 'during', 'before', 'after', 'and',
        'but', 'or', 'nor', 'not', 'so', 'yet', 'both', 'either',
        'neither', 'each', 'every', 'all', 'any', 'few', 'more',
        'most', 'other', 'some', 'such', 'no', 'only', 'own', 'same',
        'than', 'too', 'very', 'just', 'because', 'if', 'when',
        'that', 'this', 'these', 'those', 'it', 'its', 'he', 'she',
        'they', 'them', 'their', 'we', 'our', 'you', 'your', 'also'
    }

    # Step 3: Count word frequencies (excluding stop words)
    # We combine all sentences into one big list of words
    all_words = []
    for sentence in sentences:
        words = re.findall(r'\b[a-z]+\b', sentence.lower())
        meaningful_words = [w for w in words if w not in stop_words]
        all_words.extend(meaningful_words)

    # Count how often each word appears
    word_freq = Counter(all_words)

    # Step 4: Score each sentence
    sentence_scores = []
    for i, sentence in enumerate(sentences):
        words = re.findall(r'\b[a-z]+\b', sentence.lower())
        meaningful_words = [w for w in words if w not in stop_words]

        if len(meaningful_words) == 0:
            score = 0
        else:
            # Sum the frequency of each meaningful word in the sentence
            # Divide by total words to avoid bias toward long sentences
            score = sum(word_freq[w] for w in meaningful_words)
            score = score / len(meaningful_words)

        sentence_scores.append((score, i, sentence))

    # Step 5: Select top sentences
    # Sort by score (highest first)
    sentence_scores.sort(key=lambda x: x[0], reverse=True)

    # Take top N sentences
    selected = sentence_scores[:num_sentences]

    # Sort selected sentences by their original position
    # This keeps the summary in the same order as the original text
    selected.sort(key=lambda x: x[1])

    # Step 6: Combine selected sentences into the summary
    summary = ' '.join([s[2] for s in selected])

    return summary


# Let us test our summarizer
article = """
Artificial intelligence is transforming the healthcare industry in remarkable ways.
Doctors are using AI systems to diagnose diseases more accurately and quickly.
Machine learning algorithms can analyze medical images like X-rays and MRIs to
detect cancer at early stages. Natural language processing helps extract important
information from patient records automatically. AI-powered drug discovery is
reducing the time needed to develop new medications from years to months.
Robotic surgery systems guided by AI are making complex procedures safer and
more precise. Wearable devices with AI capabilities can monitor patient health
in real time and alert doctors to potential problems. Despite these advances,
experts emphasize that AI should assist doctors rather than replace them. The
human element in healthcare, including empathy and complex decision making,
remains irreplaceable. The future of healthcare lies in the collaboration
between human doctors and AI systems.
"""

print("Original text length:", len(article.split()), "words")
print()

summary = extractive_summarize(article, num_sentences=3)
print("Summary (3 sentences):")
print(summary)
print()
print("Summary length:", len(summary.split()), "words")
```

**Expected Output:**
```
Original text length: 127 words

Summary (3 sentences):
Machine learning algorithms can analyze medical images like X-rays and MRIs to
detect cancer at early stages. Natural language processing helps extract important
information from patient records automatically. AI-powered drug discovery is
reducing the time needed to develop new medications from years to months.

Summary length: 41 words
```

Let us trace through the code line by line:

- **Lines 3-4:** We import `re` for regular expressions (text pattern matching) and `Counter` for counting word occurrences
- **Lines 6-17:** We define our function with `text` (the input) and `num_sentences` (how many sentences to keep, default 3)
- **Lines 21-22:** We split the text into individual sentences using a regex pattern. The pattern `(?<=[.!?])\s+` looks for a period, exclamation mark, or question mark followed by one or more spaces
- **Lines 25:** We filter out very short sentences (3 words or fewer) because they rarely contain useful information
- **Lines 28-37:** We define **stop words** — common English words like "the," "is," and "of" that appear frequently but carry little meaning. We exclude these from our scoring
- **Lines 40-45:** We loop through all sentences, extract words (lowercase), remove stop words, and collect all meaningful words into one list
- **Lines 48:** We use `Counter` to count how often each meaningful word appears across the entire text
- **Lines 51-63:** For each sentence, we calculate its score. The score is the sum of word frequencies for each meaningful word in the sentence, divided by the number of meaningful words. Dividing prevents long sentences from having an unfair advantage
- **Lines 67-68:** We sort sentences by score from highest to lowest
- **Lines 71:** We take the top N sentences
- **Lines 75-76:** We re-sort the selected sentences by their original position in the text, so the summary reads in a natural order
- **Lines 79:** We join the selected sentences into one string

---

## 7.4 Abstractive Summarization with Hugging Face

While our extractive summarizer works, modern AI can do something much more impressive: read the text, understand it, and write a new summary in its own words. This is **abstractive summarization**, and the Hugging Face `transformers` library makes it easy.

### The Summarization Pipeline

Hugging Face provides a **pipeline** — a pre-built tool that handles all the complex steps automatically. You just give it text and get back a summary.

```python
# Abstractive summarization with Hugging Face

from transformers import pipeline

# Create a summarization pipeline
# This downloads a pre-trained model the first time you run it
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# The text we want to summarize
article = """
The Amazon rainforest, often referred to as the lungs of the Earth, produces
approximately 20 percent of the world's oxygen. Spanning across nine countries
in South America, it covers an area of about 5.5 million square kilometers.
The rainforest is home to an estimated 10 percent of all species on Earth,
including over 40,000 plant species, 1,300 bird species, and 3,000 types of
fish. However, deforestation has been a growing concern, with approximately
17 percent of the forest lost in the last 50 years. Scientists warn that
continued destruction could push the ecosystem past a tipping point,
transforming large portions of the rainforest into savanna. Conservation
efforts have increased in recent years, with governments and organizations
working to protect remaining forest areas and restore degraded land.
Indigenous communities play a crucial role in forest conservation, as their
traditional land management practices have proven effective at maintaining
biodiversity and preventing deforestation.
"""

# Generate the summary
summary = summarizer(article, max_length=80, min_length=30, do_sample=False)

# The pipeline returns a list of dictionaries
# Each dictionary has a 'summary_text' key
print("Summary:")
print(summary[0]['summary_text'])
```

**Expected Output:**
```
Summary:
The Amazon rainforest produces approximately 20 percent of the world's oxygen.
It is home to an estimated 10 percent of all species on Earth. About 17 percent
of the forest has been lost in the last 50 years. Conservation efforts have
increased in recent years.
```

Let us trace through each line:

- **Line 3:** We import `pipeline` from the `transformers` library. A pipeline wraps a model, tokenizer, and post-processing into one simple function
- **Line 7:** We create a summarization pipeline. `"summarization"` tells Hugging Face what task we want. `model="facebook/bart-large-cnn"` specifies the BART model fine-tuned on CNN/Daily Mail news articles. BART stands for **Bidirectional and Auto-Regressive Transformers**. The first time you run this, it downloads the model (about 1.6 GB)
- **Line 27:** We call the summarizer with three parameters:
  - `article` — the text to summarize
  - `max_length=80` — the summary should be at most 80 tokens long
  - `min_length=30` — the summary should be at least 30 tokens long
  - `do_sample=False` — use deterministic generation (always produces the same output)
- **Line 31:** The pipeline returns a list. Each element is a dictionary with a `'summary_text'` key containing the generated summary

### How the Model Works Inside

The BART model used here follows an **encoder-decoder** architecture:

```
+------------------------------------------------------------------+
|          How Abstractive Summarization Works                      |
+------------------------------------------------------------------+
|                                                                   |
|  Input Text                                                       |
|  "The Amazon rainforest produces 20% of the world's oxygen..."   |
|       |                                                           |
|       v                                                           |
|  +----------+                                                     |
|  | Tokenizer|  Converts text into numbers the model understands   |
|  +----------+                                                     |
|       |                                                           |
|       v                                                           |
|  +---------+                                                      |
|  | Encoder |  Reads and understands the full input text            |
|  |         |  Creates a "meaning representation"                  |
|  +---------+                                                      |
|       |                                                           |
|       v                                                           |
|  +---------+                                                      |
|  | Decoder |  Generates the summary word by word                  |
|  |         |  Uses the meaning from the encoder                   |
|  +---------+                                                      |
|       |                                                           |
|       v                                                           |
|  Summary Text                                                     |
|  "The Amazon rainforest produces approximately 20 percent..."    |
|                                                                   |
+------------------------------------------------------------------+
```

The **encoder** reads the entire input text and creates an internal representation of its meaning. The **decoder** then generates the summary one word at a time, using the encoder's understanding to decide what words to write. This is similar to how a human reads an article first (encoding) and then writes a summary from memory (decoding).

---

## 7.5 Controlling Summary Length

One of the most useful features of abstractive summarization is controlling how long or short the summary should be. You can adjust this with `min_length` and `max_length` parameters.

```python
# Controlling summary length

from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

text = """
Climate change is one of the most pressing challenges facing humanity today.
Rising global temperatures are causing more frequent and severe weather events,
including hurricanes, droughts, and wildfires. Sea levels are rising due to
melting ice caps, threatening coastal communities around the world. The burning
of fossil fuels like coal, oil, and natural gas releases greenhouse gases into
the atmosphere, trapping heat and warming the planet. Scientists have reached a
strong consensus that human activities are the primary driver of climate change.
To address this crisis, many countries have committed to reducing carbon emissions
through the Paris Agreement. Renewable energy sources such as solar and wind power
are becoming increasingly affordable and widespread. Electric vehicles are replacing
gas-powered cars at an accelerating rate. However, experts warn that current efforts
are not sufficient to limit warming to 1.5 degrees Celsius above pre-industrial
levels, and more aggressive action is needed.
"""

# Short summary (1-2 sentences)
short_summary = summarizer(text, max_length=40, min_length=10, do_sample=False)
print("SHORT SUMMARY:")
print(short_summary[0]['summary_text'])
print(f"Length: {len(short_summary[0]['summary_text'].split())} words")
print()

# Medium summary (3-4 sentences)
medium_summary = summarizer(text, max_length=80, min_length=30, do_sample=False)
print("MEDIUM SUMMARY:")
print(medium_summary[0]['summary_text'])
print(f"Length: {len(medium_summary[0]['summary_text'].split())} words")
print()

# Long summary (5+ sentences)
long_summary = summarizer(text, max_length=150, min_length=60, do_sample=False)
print("LONG SUMMARY:")
print(long_summary[0]['summary_text'])
print(f"Length: {len(long_summary[0]['summary_text'].split())} words")
```

**Expected Output:**
```
SHORT SUMMARY:
Climate change is one of the most pressing challenges facing humanity today.
Rising global temperatures are causing more frequent and severe weather events.
Length: 23 words

MEDIUM SUMMARY:
Climate change is one of the most pressing challenges facing humanity today.
The burning of fossil fuels releases greenhouse gases into the atmosphere.
Many countries have committed to reducing carbon emissions through the Paris
Agreement. Renewable energy sources are becoming increasingly affordable.
Length: 41 words

LONG SUMMARY:
Climate change is one of the most pressing challenges facing humanity today.
Rising global temperatures are causing more frequent and severe weather events.
The burning of fossil fuels releases greenhouse gases, trapping heat and warming
the planet. Scientists agree that human activities are the primary driver. Many
countries have committed to reducing emissions through the Paris Agreement.
Renewable energy and electric vehicles are helping, but experts warn current
efforts are not sufficient.
Length: 65 words
```

```
+------------------------------------------------------------------+
|              Summary Length Control                                |
+------------------------------------------------------------------+
|                                                                   |
|  Parameter     | What It Controls                                 |
|  --------------|------------------------------------------------  |
|  max_length    | Maximum number of tokens in the summary          |
|  min_length    | Minimum number of tokens in the summary          |
|  do_sample     | False = deterministic, True = add randomness     |
|                                                                   |
|  Note: A "token" is roughly 0.75 words.                          |
|  So max_length=80 means roughly 60 words maximum.                |
|                                                                   |
|  Guidelines:                                                      |
|  - Short summary:  max_length=40,  min_length=10                 |
|  - Medium summary: max_length=80,  min_length=30                 |
|  - Long summary:   max_length=150, min_length=60                 |
|  - Very long:      max_length=300, min_length=100                |
|                                                                   |
+------------------------------------------------------------------+
```

A **token** is a piece of text that the model processes. Tokens can be whole words like "cat" or parts of words like "un" and "believable." On average, one word equals about 1.3 tokens, so `max_length=80` tokens is roughly 60 words.

---

## 7.6 Evaluating Summaries with ROUGE Metrics

How do you measure whether a summary is good? You cannot just check if it is short — a single word would be short but useless. You need a way to measure how well the summary captures the content of the original text. This is where **ROUGE** metrics come in.

### What Is ROUGE?

**ROUGE** stands for **Recall-Oriented Understudy for Gisting Evaluation**. Do not worry about the full name — just remember that ROUGE measures how much overlap exists between a generated summary and a reference (human-written) summary.

Think of it like grading a student's book report by comparing it to the teacher's answer key. The more overlap between the student's answer and the teacher's answer, the higher the score.

There are several types of ROUGE:

```
+------------------------------------------------------------------+
|              ROUGE Metrics Explained                              |
+------------------------------------------------------------------+
|                                                                   |
|  ROUGE-1: Overlap of individual words (unigrams)                 |
|                                                                   |
|  Reference: "The cat sat on the mat"                             |
|  Generated: "The cat is on the mat"                              |
|  Shared words: the, cat, on, the, mat = 5 out of 6              |
|  ROUGE-1 Recall = 5/6 = 0.83                                    |
|                                                                   |
|  ---                                                              |
|                                                                   |
|  ROUGE-2: Overlap of word pairs (bigrams)                        |
|                                                                   |
|  Reference pairs: "the cat", "cat sat", "sat on",                |
|                   "on the", "the mat"                             |
|  Generated pairs: "the cat", "cat is", "is on",                  |
|                   "on the", "the mat"                             |
|  Shared pairs: "the cat", "on the", "the mat" = 3 out of 5      |
|  ROUGE-2 Recall = 3/5 = 0.60                                    |
|                                                                   |
|  ---                                                              |
|                                                                   |
|  ROUGE-L: Longest Common Subsequence                             |
|                                                                   |
|  Finds the longest sequence of words that appear in the same     |
|  order in both summaries (words do not need to be consecutive)   |
|  Reference: "The cat sat on the mat"                             |
|  Generated: "The cat is on the mat"                              |
|  LCS: "The cat on the mat" (5 words)                             |
|  ROUGE-L Recall = 5/6 = 0.83                                    |
|                                                                   |
+------------------------------------------------------------------+
```

Each ROUGE type has three sub-scores:
- **Precision**: Of all the words in the generated summary, how many also appear in the reference?
- **Recall**: Of all the words in the reference summary, how many also appear in the generated summary?
- **F1-score**: The balanced average of precision and recall

### Computing ROUGE Scores in Python

```python
# Computing ROUGE scores to evaluate summaries
# First install: pip install rouge-score

from rouge_score import rouge_scorer

# Create a scorer that computes ROUGE-1, ROUGE-2, and ROUGE-L
scorer = rouge_scorer.RougeScorer(
    ['rouge1', 'rouge2', 'rougeL'],
    use_stemmer=True  # "running" and "runs" count as the same word
)

# Our reference summary (what a human wrote)
reference = """
NASA's Perseverance rover landed on Mars in February 2021. The rover
searches for signs of ancient microbial life. It carries the Ingenuity
helicopter, which achieved the first powered flight on another planet.
"""

# Our generated summary (what our model produced)
generated = """
The Perseverance rover successfully landed on Mars on February 18, 2021.
It is designed to search for ancient life. The rover also carries
Ingenuity, the first helicopter to fly on another planet.
"""

# Compute ROUGE scores
scores = scorer.score(reference, generated)

print("ROUGE Evaluation Results")
print("=" * 50)

for metric, score in scores.items():
    print(f"\n{metric.upper()}:")
    print(f"  Precision: {score.precision:.4f}")
    print(f"  Recall:    {score.recall:.4f}")
    print(f"  F1-Score:  {score.fmeasure:.4f}")
```

**Expected Output:**
```
ROUGE Evaluation Results
==================================================

ROUGE1:
  Precision: 0.7647
  Recall:    0.7222
  F1-Score:  0.7429

ROUGE2:
  Precision: 0.4516
  Recall:    0.4242
  F1-Score:  0.4375

ROUGEL:
  Precision: 0.6471
  Recall:    0.6111
  F1-Score:  0.6286
```

Let us trace through the code:

- **Line 4:** We import `rouge_scorer` from the `rouge_score` library. Install it with `pip install rouge-score`
- **Lines 7-10:** We create a `RougeScorer` object. We specify which ROUGE types to compute: `rouge1` (single words), `rouge2` (word pairs), and `rougeL` (longest common subsequence). `use_stemmer=True` means "running" and "runs" are treated as the same word. **Stemming** reduces words to their root form
- **Lines 13-22:** We define a reference summary (what a human would write) and a generated summary (what our model produced)
- **Line 25:** We compute the scores by comparing the reference and generated summaries
- **Lines 27-33:** We print each metric's precision, recall, and F1-score

### Interpreting ROUGE Scores

```
+------------------------------------------------------------------+
|              Understanding ROUGE Scores                           |
+------------------------------------------------------------------+
|                                                                   |
|  Score Range     | Interpretation                                 |
|  ----------------|----------------------------------------------  |
|  0.0 - 0.2      | Poor overlap, summaries are very different     |
|  0.2 - 0.4      | Some overlap, captures some key ideas          |
|  0.4 - 0.6      | Moderate overlap, decent summary               |
|  0.6 - 0.8      | Good overlap, captures most key ideas          |
|  0.8 - 1.0      | Excellent overlap, very similar to reference   |
|                                                                   |
|  Important notes:                                                  |
|  - A perfect score of 1.0 means identical text                   |
|  - ROUGE-2 is usually lower than ROUGE-1 (harder to match pairs) |
|  - ROUGE does not measure factual correctness                     |
|  - A good summary can have moderate ROUGE if it uses different    |
|    words to express the same ideas                                |
|                                                                   |
+------------------------------------------------------------------+
```

---

## 7.7 Complete Summarization Example

Let us put everything together in a complete example that combines both extractive and abstractive summarization, along with evaluation.

```python
# Complete text summarization example

import re
from collections import Counter
from transformers import pipeline
from rouge_score import rouge_scorer


# ============================================================
# PART 1: The article to summarize
# ============================================================

article = """
Electric vehicles are rapidly transforming the global automotive industry.
Sales of electric cars have grown by over 40 percent annually for the past
three years, with China, Europe, and the United States leading adoption.
Battery technology has improved dramatically, with modern lithium-ion batteries
offering ranges of over 300 miles on a single charge. The cost of batteries has
fallen by nearly 90 percent over the past decade, making electric vehicles
increasingly affordable for average consumers. Major automakers including Ford,
General Motors, and Volkswagen have announced plans to phase out internal
combustion engines within the next 10 to 15 years. Charging infrastructure is
expanding rapidly, with governments investing billions of dollars in public
charging networks. However, challenges remain, including long charging times
compared to gasoline refueling, limited charging stations in rural areas, and
concerns about the environmental impact of battery mining and disposal. Despite
these challenges, industry analysts predict that electric vehicles will account
for over 50 percent of new car sales globally by 2030. The transition to
electric vehicles is seen as a critical step in reducing greenhouse gas
emissions from the transportation sector, which currently accounts for
approximately 16 percent of global emissions.
"""

print("ORIGINAL ARTICLE")
print("=" * 60)
print(article.strip())
print(f"\nWord count: {len(article.split())} words")
print()


# ============================================================
# PART 2: Extractive Summary
# ============================================================

def extractive_summarize(text, num_sentences=3):
    """Select the most important sentences from the text."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s for s in sentences if len(s.split()) > 3]

    stop_words = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'of', 'in', 'to', 'for', 'with', 'on', 'at', 'by', 'from',
        'as', 'and', 'but', 'or', 'not', 'that', 'this', 'it', 'its',
        'he', 'she', 'they', 'them', 'their', 'we', 'our', 'you',
        'your', 'also', 'than', 'more', 'over', 'which', 'including'
    }

    all_words = []
    for sentence in sentences:
        words = re.findall(r'\b[a-z]+\b', sentence.lower())
        meaningful_words = [w for w in words if w not in stop_words]
        all_words.extend(meaningful_words)

    word_freq = Counter(all_words)

    sentence_scores = []
    for i, sentence in enumerate(sentences):
        words = re.findall(r'\b[a-z]+\b', sentence.lower())
        meaningful_words = [w for w in words if w not in stop_words]
        if len(meaningful_words) == 0:
            score = 0
        else:
            score = sum(word_freq[w] for w in meaningful_words)
            score = score / len(meaningful_words)
        sentence_scores.append((score, i, sentence))

    sentence_scores.sort(key=lambda x: x[0], reverse=True)
    selected = sentence_scores[:num_sentences]
    selected.sort(key=lambda x: x[1])

    return ' '.join([s[2] for s in selected])

extractive_result = extractive_summarize(article, num_sentences=3)
print("EXTRACTIVE SUMMARY")
print("=" * 60)
print(extractive_result)
print(f"\nWord count: {len(extractive_result.split())} words")
print()


# ============================================================
# PART 3: Abstractive Summary
# ============================================================

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
abstractive_result = summarizer(
    article, max_length=80, min_length=30, do_sample=False
)[0]['summary_text']

print("ABSTRACTIVE SUMMARY")
print("=" * 60)
print(abstractive_result)
print(f"\nWord count: {len(abstractive_result.split())} words")
print()


# ============================================================
# PART 4: Evaluate both summaries
# ============================================================

# A human-written reference summary for comparison
reference_summary = """
Electric vehicle sales are growing rapidly worldwide, driven by improved battery
technology and falling costs. Major automakers plan to end combustion engine
production within 15 years. While challenges like charging infrastructure and
battery environmental concerns persist, EVs are expected to reach 50 percent of
global sales by 2030, helping reduce transportation emissions.
"""

scorer = rouge_scorer.RougeScorer(
    ['rouge1', 'rouge2', 'rougeL'], use_stemmer=True
)

print("EVALUATION (ROUGE Scores)")
print("=" * 60)

# Score extractive summary
ext_scores = scorer.score(reference_summary, extractive_result)
print("\nExtractive Summary Scores:")
for metric, score in ext_scores.items():
    print(f"  {metric}: F1={score.fmeasure:.4f}")

# Score abstractive summary
abs_scores = scorer.score(reference_summary, abstractive_result)
print("\nAbstractive Summary Scores:")
for metric, score in abs_scores.items():
    print(f"  {metric}: F1={score.fmeasure:.4f}")

# Compare
print("\nComparison:")
print(f"  Extractive ROUGE-1 F1:  {ext_scores['rouge1'].fmeasure:.4f}")
print(f"  Abstractive ROUGE-1 F1: {abs_scores['rouge1'].fmeasure:.4f}")

if abs_scores['rouge1'].fmeasure > ext_scores['rouge1'].fmeasure:
    print("  --> Abstractive summary scores higher on ROUGE-1")
else:
    print("  --> Extractive summary scores higher on ROUGE-1")
```

**Expected Output:**
```
ORIGINAL ARTICLE
============================================================
Electric vehicles are rapidly transforming the global automotive industry...
[full article text]

Word count: 168 words

EXTRACTIVE SUMMARY
============================================================
Sales of electric cars have grown by over 40 percent annually for the past
three years, with China, Europe, and the United States leading adoption. The
cost of batteries has fallen by nearly 90 percent over the past decade, making
electric vehicles increasingly affordable for average consumers. Despite these
challenges, industry analysts predict that electric vehicles will account for
over 50 percent of new car sales globally by 2030.

Word count: 62 words

ABSTRACTIVE SUMMARY
============================================================
Electric vehicle sales have grown by over 40 percent annually for the past
three years. Battery costs have fallen by nearly 90 percent over the past
decade. Major automakers have announced plans to phase out internal combustion
engines. Industry analysts predict EVs will account for over 50 percent of new
car sales by 2030.

Word count: 51 words

EVALUATION (ROUGE Scores)
============================================================

Extractive Summary Scores:
  rouge1: F1=0.4800
  rouge2: F1=0.2353
  rougeL: F1=0.3200

Abstractive Summary Scores:
  rouge1: F1=0.5455
  rouge2: F1=0.3125
  rougeL: F1=0.4000

Comparison:
  Extractive ROUGE-1 F1:  0.4800
  Abstractive ROUGE-1 F1: 0.5455
  --> Abstractive summary scores higher on ROUGE-1
```

---

## 7.8 Summarizing Multiple Documents

In real applications, you often need to summarize multiple related documents. Here is how to handle that:

```python
# Summarizing multiple documents

from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Multiple related articles
documents = [
    """
    Tesla reported record quarterly revenue of 25.2 billion dollars. The company
    delivered over 466,000 vehicles in the quarter, a 20 percent increase from
    the previous year. CEO Elon Musk highlighted the growing demand for the
    Model Y, which became the best-selling car globally.
    """,
    """
    Ford announced a 2 billion dollar investment in electric vehicle manufacturing.
    The company plans to produce 600,000 EVs annually by the end of next year.
    Ford's F-150 Lightning electric pickup truck has received over 200,000
    reservations from customers.
    """,
    """
    General Motors revealed plans to launch 30 new electric vehicle models by 2025.
    The company is investing 35 billion dollars in EV and autonomous vehicle
    development. GM aims to have an all-electric lineup by 2035 and achieve
    carbon neutrality by 2040.
    """
]

print("Individual Document Summaries:")
print("=" * 60)

all_summaries = []
for i, doc in enumerate(documents):
    summary = summarizer(doc, max_length=40, min_length=15, do_sample=False)
    summary_text = summary[0]['summary_text']
    all_summaries.append(summary_text)
    print(f"\nDocument {i + 1} Summary:")
    print(f"  {summary_text}")

# Combine individual summaries into one text
combined = ' '.join(all_summaries)

# Summarize the combined summaries for a mega-summary
print("\n\nCombined Summary of All Documents:")
print("=" * 60)
mega_summary = summarizer(combined, max_length=60, min_length=20, do_sample=False)
print(mega_summary[0]['summary_text'])
```

**Expected Output:**
```
Individual Document Summaries:
============================================================

Document 1 Summary:
  Tesla reported record quarterly revenue of 25.2 billion dollars. The company
  delivered over 466,000 vehicles in the quarter.

Document 2 Summary:
  Ford announced a 2 billion dollar investment in electric vehicle manufacturing.
  The F-150 Lightning has received over 200,000 reservations.

Document 3 Summary:
  General Motors revealed plans to launch 30 new electric vehicle models by 2025.
  GM aims to have an all-electric lineup by 2035.

Combined Summary of All Documents:
============================================================
Tesla, Ford, and GM are all investing heavily in electric vehicles. Tesla
reported record revenue while Ford and GM announced major EV production plans
and investments totaling billions of dollars.
```

---

## Common Mistakes

1. **Input text too short**: Summarization models work best with text that is at least a few sentences long. Trying to summarize a single sentence often produces strange results or just returns the same sentence.

2. **Input text too long**: Most models have a maximum input length (typically 1024 tokens for BART). If your text exceeds this, you need to truncate it or split it into chunks and summarize each chunk separately.

3. **Setting min_length greater than max_length**: This causes an error. Always ensure `min_length` is less than `max_length`.

4. **Trusting abstractive summaries blindly**: Abstractive models can generate facts that were not in the original text (hallucination). Always verify important facts in the summary against the original text.

5. **Using ROUGE as the only evaluation**: ROUGE measures word overlap, not meaning. A summary could have low ROUGE but still be excellent if it uses different words to express the same ideas. Use ROUGE as one signal among many.

---

## Best Practices

1. **Choose the right approach for your use case**: Use extractive summarization when factual accuracy is critical (legal, medical). Use abstractive when you need fluent, readable summaries.

2. **Preprocess your input**: Remove headers, footers, navigation text, and other noise before summarizing. Clean input produces better summaries.

3. **Experiment with length parameters**: Try different `min_length` and `max_length` values to find the right summary length for your application.

4. **Handle long documents with chunking**: If your document exceeds the model's maximum input length, split it into overlapping chunks, summarize each chunk, and then summarize the summaries.

5. **Combine extractive and abstractive**: First use extractive summarization to reduce a very long document to its key sentences, then use abstractive summarization on those sentences for a fluent final summary.

---

## Quick Summary

Text summarization condenses long text into shorter versions. **Extractive summarization** selects important sentences from the original text using scoring methods like word frequency. **Abstractive summarization** uses deep learning models (like BART) to generate new sentences that capture the original meaning. The Hugging Face `pipeline("summarization")` makes abstractive summarization easy with just a few lines of code. **ROUGE metrics** evaluate summary quality by measuring word overlap between generated and reference summaries. ROUGE-1 measures single-word overlap, ROUGE-2 measures word-pair overlap, and ROUGE-L measures the longest common subsequence.

---

## Key Points

- Text summarization creates shorter versions of text while preserving key information
- **Extractive** summarization selects sentences directly; **abstractive** generates new text
- Extractive is simpler and more factually reliable; abstractive is more fluent and natural
- Sentence scoring based on word frequency is a basic but effective extractive method
- The Hugging Face summarization pipeline uses models like BART for abstractive summarization
- Control summary length with `min_length` and `max_length` parameters
- ROUGE metrics (ROUGE-1, ROUGE-2, ROUGE-L) measure overlap between generated and reference summaries
- Abstractive models may hallucinate facts not present in the original text
- For very long documents, use chunking to stay within the model's input limit

---

## Practice Questions

1. What is the difference between extractive and abstractive summarization? Give a real-world analogy for each approach.

2. In our extractive summarizer, why do we divide the sentence score by the number of meaningful words? What would happen if we did not?

3. What does ROUGE-2 measure, and why is it usually lower than ROUGE-1 for the same pair of summaries?

4. A summary has ROUGE-1 precision of 0.90 but ROUGE-1 recall of 0.30. What does this tell you about the summary?

5. Why might an abstractive summary score lower on ROUGE than an extractive summary, even if the abstractive summary is actually better to a human reader?

---

## Exercises

**Exercise 1: Improve the Extractive Summarizer**
Modify the `extractive_summarize` function to also consider sentence position as a scoring factor. Sentences at the beginning and end of the text are often more important (the "lead bias" in news articles). Add a position weight: multiply the score by 1.5 for the first sentence, 1.2 for the last sentence, and 1.0 for all others.

**Exercise 2: Summary Comparison Tool**
Write a program that takes an article and generates three different summaries: one extractive, one abstractive with `max_length=40`, and one abstractive with `max_length=100`. Compare all three using ROUGE scores against a reference summary you write by hand. Display the results in a formatted table.

**Exercise 3: Long Document Summarizer**
Build a function called `summarize_long_document(text, chunk_size=500)` that handles documents longer than 1024 tokens. The function should split the text into chunks of approximately `chunk_size` words each, summarize each chunk using the Hugging Face pipeline, combine the chunk summaries, and then produce a final summary of the combined summaries.

---

## What Is Next?

In this chapter, you learned how to condense long texts into short summaries using both extractive and abstractive methods. But summarization is just one type of **sequence-to-sequence** task — tasks where you take a sequence of text as input and produce a different sequence as output. In the next chapter, you will learn about the **sequence-to-sequence architecture** that powers not only summarization but also machine translation, question answering, and many other tasks. You will see how the encoder-decoder design works in detail and build a translation system that converts text from one language to another.
