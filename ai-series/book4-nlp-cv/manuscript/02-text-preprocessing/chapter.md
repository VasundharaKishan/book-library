# Chapter 2: Text Preprocessing

## What You Will Learn

- How to split text into words and subwords (tokenization)
- Why and how to lowercase text
- How to remove punctuation and special characters
- What stop words are and when to remove them
- The difference between stemming and lemmatization
- How to use regular expressions (regex) for text cleaning
- How to build a complete preprocessing pipeline with NLTK and spaCy

## Why This Chapter Matters

Raw text is messy. It has capital letters, punctuation marks, emojis, HTML tags, extra spaces, and typos. If you feed this messy text directly into a machine learning model, the model gets confused. It might think "Running," "running," and "RUNNING" are three different words. Preprocessing transforms chaotic raw text into clean, consistent data that models can actually learn from. Data scientists often say they spend 80% of their time on data preparation -- and in NLP, preprocessing is that 80%.

---

## 2.1 Why Do We Need Text Preprocessing?

Let us look at a simple example to understand the problem:

```python
# Without preprocessing, these are all "different" to a computer
words = ["Running", "running", "RUNNING", "running!", "running..."]

# How many unique words does Python see?
print(f"Unique words: {len(set(words))}")
print(f"The set: {set(words)}")
```

**Output:**
```
Unique words: 5
The set: {'running!', 'Running', 'RUNNING', 'running...', 'running'}
```

Python sees five completely different words! But to a human, they are all the same word: "running." This is why we need preprocessing.

> **Analogy:** Imagine you are sorting mail at a post office. Letters arrive with addresses written in all caps, lowercase, with typos, in different handwriting styles. Before you can sort them, you need to standardize every address into a clean, consistent format. Text preprocessing is the same -- standardizing text before processing it.

```
+----------------------------------------------------------+
|          Why Preprocessing Matters                        |
+----------------------------------------------------------+
|                                                           |
|  Raw Text:                                                |
|  "I LOVED this movie!!! It was SO good :) <br>"          |
|                                                           |
|        |                                                  |
|        v                                                  |
|                                                           |
|  Clean Text:                                              |
|  "loved movie good"                                       |
|                                                           |
|  Result: Fewer words, less noise, better model accuracy   |
|                                                           |
+----------------------------------------------------------+
```

---

## 2.2 Tokenization

**Tokenization** is the process of splitting text into smaller pieces called **tokens**. A token is usually a word, but it can also be a subword, a character, or even a sentence.

### 2.2.1 Word Tokenization

The simplest form: split text on spaces.

```python
# Simple word tokenization using Python's split()
text = "Natural language processing is fascinating"
tokens = text.split()

print(tokens)
print(f"Number of tokens: {len(tokens)}")
```

**Output:**
```
['Natural', 'language', 'processing', 'is', 'fascinating']
Number of tokens: 5
```

But `split()` has problems with punctuation:

```python
text = "Hello, world! How's it going?"
tokens = text.split()
print(tokens)
```

**Output:**
```
['Hello,', 'world!', "How's", 'it', 'going?']
```

Notice "Hello," includes the comma and "world!" includes the exclamation mark. We need smarter tokenization.

### 2.2.2 Tokenization with NLTK

**NLTK** (Natural Language Toolkit) is one of the most popular NLP libraries in Python. It handles punctuation properly:

```python
import nltk
# Download required data (only needed once)
nltk.download('punkt_tab', quiet=True)

from nltk.tokenize import word_tokenize

text = "Hello, world! How's it going?"
tokens = word_tokenize(text)

print(tokens)
print(f"Number of tokens: {len(tokens)}")
```

**Output:**
```
['Hello', ',', 'world', '!', 'How', "'s", 'it', 'going', '?']
Number of tokens: 9
```

**Line-by-line explanation:**

1. `import nltk` -- Import the NLTK library.
2. `nltk.download('punkt_tab', quiet=True)` -- Download the tokenizer data. The `punkt_tab` resource contains rules for splitting text. You only need to run this once.
3. `from nltk.tokenize import word_tokenize` -- Import the word tokenizer function.
4. `word_tokenize(text)` -- Split the text into tokens. Notice how it separates "How's" into "How" and "'s", and punctuation marks become their own tokens.

### 2.2.3 Tokenization with spaCy

**spaCy** is another popular NLP library, designed for production use. It is faster than NLTK for many tasks:

```python
import spacy

# Load the English language model
# Run this first in your terminal: python -m spacy download en_core_web_sm
nlp = spacy.load("en_core_web_sm")

text = "Hello, world! How's it going?"
doc = nlp(text)

# Extract tokens from the processed document
tokens = [token.text for token in doc]

print(tokens)
print(f"Number of tokens: {len(tokens)}")
```

**Output:**
```
['Hello', ',', 'world', '!', 'How', "'s", 'it', 'going', '?']
Number of tokens: 9
```

**Line-by-line explanation:**

1. `import spacy` -- Import the spaCy library.
2. `nlp = spacy.load("en_core_web_sm")` -- Load a pre-trained English language model. The `"en_core_web_sm"` model is a small, efficient model for English.
3. `doc = nlp(text)` -- Process the text. spaCy creates a `Doc` object that contains all the tokens and their linguistic information.
4. `[token.text for token in doc]` -- Extract the text of each token using a list comprehension.

### 2.2.4 Sentence Tokenization

Sometimes you need to split text into sentences rather than words:

```python
from nltk.tokenize import sent_tokenize

text = "NLP is amazing. It powers many applications. Let's learn more!"
sentences = sent_tokenize(text)

for i, sent in enumerate(sentences, 1):
    print(f"Sentence {i}: {sent}")
```

**Output:**
```
Sentence 1: NLP is amazing.
Sentence 2: It powers many applications.
Sentence 3: Let's learn more!
```

### 2.2.5 Subword Tokenization

Modern models like BERT and GPT use **subword tokenization**. Instead of splitting into whole words, they split into meaningful pieces:

```python
from transformers import AutoTokenizer

# Load the BERT tokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

text = "I love tokenization and preprocessing"
tokens = tokenizer.tokenize(text)

print(f"Tokens: {tokens}")
```

**Output:**
```
Tokens: ['i', 'love', 'token', '##ization', 'and', 'pre', '##processing']
```

Notice how "tokenization" becomes "token" + "##ization" and "preprocessing" becomes "pre" + "##processing." The `##` prefix means "this piece is attached to the previous piece." This approach handles words the model has never seen before by breaking them into known parts.

```
+----------------------------------------------------------+
|           Types of Tokenization                           |
+----------------------------------------------------------+
|                                                           |
|  Word:     ["I", "love", "tokenization"]                  |
|            Simple but fails on unknown words              |
|                                                           |
|  Subword:  ["I", "love", "token", "##ization"]            |
|            Handles unknown words by splitting them         |
|                                                           |
|  Character: ["I", " ", "l", "o", "v", "e", ...]           |
|            Very flexible but loses word meaning            |
|                                                           |
+----------------------------------------------------------+
```

---

## 2.3 Lowercasing

**Lowercasing** means converting all characters to lowercase. This ensures that "Apple," "apple," and "APPLE" are treated as the same word.

```python
texts = ["The Cat sat on the MAT",
         "THE CAT SAT ON THE MAT",
         "the cat sat on the mat"]

# Without lowercasing -- all different
print("Without lowercasing:")
print(f"  All same? {texts[0] == texts[1] == texts[2]}")

# With lowercasing -- all the same
lowered = [t.lower() for t in texts]
print("\nAfter lowercasing:")
for t in lowered:
    print(f"  {t}")
print(f"  All same? {lowered[0] == lowered[1] == lowered[2]}")
```

**Output:**
```
Without lowercasing:
  All same? False

After lowercasing:
  the cat sat on the mat
  the cat sat on the mat
  the cat sat on the mat
  All same? True
```

### When NOT to Lowercase

Lowercasing is not always the right choice:

```
Cases where lowercasing LOSES information:

1. Named Entities:
   "Apple" (the company) vs "apple" (the fruit)

2. Abbreviations:
   "US" (United States) vs "us" (pronoun)

3. Sentiment emphasis:
   "This is AMAZING" (strong positive) vs "this is amazing"
```

> **Rule of thumb:** Lowercase for most classification tasks. Keep original casing if you need to detect named entities or if capitalization carries meaning.

---

## 2.4 Removing Punctuation

Punctuation marks like commas, periods, and exclamation marks usually do not help with tasks like classification. We remove them to reduce noise.

```python
import string

text = "Hello, world! How are you doing today???"

# Method 1: Using str.translate (fastest)
# string.punctuation contains: !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
translator = str.maketrans('', '', string.punctuation)
clean_text = text.translate(translator)

print(f"Original:  {text}")
print(f"Cleaned:   {clean_text}")
print(f"Punctuation chars: {string.punctuation}")
```

**Output:**
```
Original:  Hello, world! How are you doing today???
Cleaned:   Hello world How are you doing today
Punctuation chars: !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
```

**Line-by-line explanation:**

1. `import string` -- Import Python's `string` module, which contains useful constants like `string.punctuation`.
2. `str.maketrans('', '', string.punctuation)` -- Create a translation table that maps every punctuation character to `None` (meaning "delete it").
3. `text.translate(translator)` -- Apply the translation table to remove all punctuation characters.

### When NOT to Remove Punctuation

```
Cases where punctuation carries meaning:

1. Contractions:
   "don't" --> removing ' gives "dont" (not a real word)

2. Emoticons:
   ":)" and ":(" carry sentiment information

3. Domain-specific:
   "$100", "C++", "Dr.", "U.S.A."
```

---

## 2.5 Stop Words

**Stop words** are common words that appear frequently but carry little meaning on their own. Words like "the," "is," "at," "which," and "on" are stop words.

> **Analogy:** In a recipe, the important words are "chicken," "garlic," and "roast." Words like "the," "a," and "of" are just glue holding the sentence together. Stop words are the glue -- useful for grammar but not for understanding meaning.

### 2.5.1 Stop Words with NLTK

```python
import nltk
nltk.download('stopwords', quiet=True)

from nltk.corpus import stopwords

# Get English stop words
stop_words = set(stopwords.words('english'))

print(f"Number of stop words: {len(stop_words)}")
print(f"First 20: {sorted(list(stop_words))[:20]}")
```

**Output:**
```
Number of stop words: 179
First 20: ["a", "about", "above", "after", "again", "against", "ain", "all", "am", "an", "and", "any", "are", "aren", "aren't", "as", "at", "be", "because", "been"]
```

### 2.5.2 Removing Stop Words

```python
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

stop_words = set(stopwords.words('english'))

text = "This is a sample sentence showing stop word removal"
tokens = word_tokenize(text.lower())

# Keep only words that are NOT stop words
filtered = [word for word in tokens if word not in stop_words]

print(f"Original tokens:  {tokens}")
print(f"After filtering:  {filtered}")
print(f"Removed {len(tokens) - len(filtered)} stop words")
```

**Output:**
```
Original tokens:  ['this', 'is', 'a', 'sample', 'sentence', 'showing', 'stop', 'word', 'removal']
After filtering:  ['sample', 'sentence', 'showing', 'stop', 'word', 'removal']
Removed 3 stop words
```

### 2.5.3 Stop Words with spaCy

```python
import spacy

nlp = spacy.load("en_core_web_sm")

text = "This is a sample sentence showing stop word removal"
doc = nlp(text)

# spaCy marks each token as a stop word or not
for token in doc:
    print(f"  {token.text:12s} --> is_stop = {token.is_stop}")
```

**Output:**
```
  This         --> is_stop = True
  is           --> is_stop = True
  a            --> is_stop = True
  sample       --> is_stop = False
  sentence     --> is_stop = False
  showing      --> is_stop = False
  stop         --> is_stop = False
  word         --> is_stop = False
  removal      --> is_stop = False
```

### When NOT to Remove Stop Words

```
Cases where stop words matter:

1. Sentiment:
   "not good" --> removing "not" changes meaning to "good"

2. Phrases:
   "to be or not to be" --> all stop words, but meaningful

3. Question answering:
   "What is the capital of France?"
   --> "what" and "is" help identify this as a question
```

---

## 2.6 Stemming vs Lemmatization

Both stemming and lemmatization reduce words to their base form. But they do it differently.

### 2.6.1 Stemming

**Stemming** chops off the end of words using simple rules. It is fast but sometimes produces words that are not real English words.

```python
from nltk.stem import PorterStemmer

stemmer = PorterStemmer()

words = ["running", "runs", "ran", "runner", "easily",
         "fairly", "studies", "studying", "studied"]

for word in words:
    stem = stemmer.stem(word)
    print(f"  {word:12s} --> {stem}")
```

**Output:**
```
  running      --> run
  runs         --> run
  ran          --> ran
  runner       --> runner
  easily       --> easili
  fairly       --> fairli
  studies      --> studi
  studying     --> studi
  studied      --> studi
```

Notice "easily" becomes "easili" and "studies" becomes "studi" -- these are not real words! The stemmer just blindly chops endings.

> **Analogy:** Stemming is like cutting the branches of a tree with a chainsaw. It is fast, but the cuts are rough and imprecise.

### 2.6.2 Lemmatization

**Lemmatization** uses a dictionary to find the proper base form (**lemma**) of a word. It is slower but produces real words.

```python
import nltk
nltk.download('wordnet', quiet=True)

from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()

words = ["running", "runs", "ran", "runner", "easily",
         "fairly", "studies", "studying", "studied"]

for word in words:
    # pos='v' tells the lemmatizer to treat the word as a verb
    lemma_v = lemmatizer.lemmatize(word, pos='v')
    lemma_n = lemmatizer.lemmatize(word, pos='n')
    print(f"  {word:12s} --> verb: {lemma_v:10s}  noun: {lemma_n}")
```

**Output:**
```
  running      --> verb: run         noun: running
  runs         --> verb: run         noun: run
  ran          --> verb: run         noun: ran
  runner       --> verb: runner      noun: runner
  easily       --> verb: easily      noun: easily
  fairly       --> verb: fairly      noun: fairly
  studies      --> verb: study       noun: study
  studying     --> verb: study       noun: studying
  studied      --> verb: study       noun: studied
```

**Line-by-line explanation:**

1. `WordNetLemmatizer()` -- Creates a lemmatizer that uses WordNet, a large English dictionary database.
2. `lemmatizer.lemmatize(word, pos='v')` -- Find the base form of the word, assuming it is a verb. The `pos` parameter stands for **part of speech** (noun, verb, adjective, etc.).
3. Notice that the results depend on the part of speech. "running" as a verb becomes "run," but as a noun it stays "running."

> **Analogy:** Lemmatization is like pruning a tree with garden shears and a guidebook. It is slower, but every cut is precise and intentional.

### 2.6.3 Lemmatization with spaCy

spaCy performs lemmatization automatically when you process text:

```python
import spacy

nlp = spacy.load("en_core_web_sm")

text = "The children were running and playing in the studies"
doc = nlp(text)

for token in doc:
    print(f"  {token.text:12s} --> lemma: {token.lemma_:12s}  POS: {token.pos_}")
```

**Output:**
```
  The          --> lemma: the           POS: DET
  children     --> lemma: child         POS: NOUN
  were         --> lemma: be            POS: AUX
  running      --> lemma: run           POS: VERB
  and          --> lemma: and           POS: CCONJ
  playing      --> lemma: play          POS: VERB
  in           --> lemma: in            POS: ADP
  the          --> lemma: the           POS: DET
  studies      --> lemma: study         POS: NOUN
```

spaCy automatically detects the part of speech and applies the correct lemmatization. "children" becomes "child," "were" becomes "be," and "running" becomes "run."

### Comparison Table

```
+----------------------------------------------------------+
|         Stemming vs Lemmatization                         |
+----------------------------------------------------------+
|                                                           |
|  Feature        Stemming          Lemmatization           |
|  ---------      --------          -------------           |
|  Speed           Fast              Slower                 |
|  Accuracy        Rough             Precise                |
|  Real words?     Not always        Always                 |
|  Needs POS?      No                Yes (for best results) |
|  Example:                                                 |
|  "studies"       "studi"           "study"                |
|  "better"        "better"          "good"                 |
|                                                           |
|  Use stemming when: speed matters, search engines         |
|  Use lemmatization when: accuracy matters, chatbots       |
|                                                           |
+----------------------------------------------------------+
```

---

## 2.7 Regular Expressions (Regex) for Text Cleaning

**Regular expressions** (regex) are patterns that describe text. They are incredibly powerful for finding and replacing text patterns.

> **Analogy:** A regex is like a search-and-replace feature on steroids. Instead of searching for exact text, you search for patterns. It is like telling someone, "Find me all phone numbers in this document" instead of "Find me 555-1234."

### 2.7.1 Regex Basics

```python
import re

# \d   matches any digit (0-9)
# \w   matches any letter, digit, or underscore
# \s   matches any whitespace (space, tab, newline)
# .    matches any character except newline
# *    means "zero or more of the previous character"
# +    means "one or more of the previous character"
# []   matches any character inside the brackets
# ^    at the start means "beginning of string"
# $    at the end means "end of string"

text = "Call me at 555-1234 or email john@example.com"

# Find all numbers
numbers = re.findall(r'\d+', text)
print(f"Numbers found: {numbers}")

# Find email addresses
emails = re.findall(r'\S+@\S+', text)
print(f"Emails found: {emails}")
```

**Output:**
```
Numbers found: ['555', '1234']
Emails found: ['john@example.com']
```

**Line-by-line explanation:**

1. `import re` -- Import Python's regular expression module.
2. `re.findall(r'\d+', text)` -- Find all sequences of one or more digits. `\d` matches a digit, `+` means "one or more."
3. `re.findall(r'\S+@\S+', text)` -- Find patterns that look like email addresses. `\S` matches any non-whitespace character.

### 2.7.2 Common Text Cleaning with Regex

```python
import re

def clean_text(text):
    """Clean text using regular expressions."""

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)

    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)

    # Remove numbers
    text = re.sub(r'\d+', '', text)

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# Test with messy text
messy = """
<p>Check out https://example.com for details!</p>
Contact us at info@company.com or call 555-1234.
Visit <a href="link">our site</a> for 50% off!!!
"""

cleaned = clean_text(messy)
print(f"Original:\n{messy}")
print(f"Cleaned:\n{cleaned}")
```

**Output:**
```
Original:

<p>Check out https://example.com for details!</p>
Contact us at info@company.com or call 555-1234.
Visit <a href="link">our site</a> for 50% off!!!

Cleaned:
Check out for details! Contact us at or call -. Visit our site for % off!!!
```

**Line-by-line explanation:**

1. `re.sub(r'<[^>]+>', '', text)` -- Find anything between `<` and `>` (HTML tags) and replace with nothing. `[^>]+` means "one or more characters that are not `>`."
2. `re.sub(r'https?://\S+|www\.\S+', '', text)` -- Find URLs starting with "http://" or "https://" or "www." and remove them. The `?` after `s` makes it optional. The `|` means "or."
3. `re.sub(r'\S+@\S+', '', text)` -- Find and remove email addresses.
4. `re.sub(r'\d+', '', text)` -- Find and remove all sequences of digits.
5. `re.sub(r'\s+', ' ', text).strip()` -- Replace multiple whitespace characters with a single space.

### 2.7.3 Regex Quick Reference

```
+----------------------------------------------------------+
|           Regex Quick Reference                           |
+----------------------------------------------------------+
|                                                           |
|  Pattern    Meaning              Example                  |
|  -------    -------              -------                  |
|  \d         Any digit            "3" matches \d           |
|  \D         Any non-digit        "a" matches \D           |
|  \w         Letter/digit/_       "a" matches \w           |
|  \W         Non-word char        "!" matches \W           |
|  \s         Whitespace           " " matches \s           |
|  \S         Non-whitespace       "a" matches \S           |
|  .          Any character        "x" matches .            |
|  *          Zero or more         "ab*" matches "a", "abbb"|
|  +          One or more          "ab+" matches "ab","abbb"|
|  ?          Zero or one          "ab?" matches "a", "ab"  |
|  [abc]      Any of a, b, c      "b" matches [abc]        |
|  [^abc]     Not a, b, or c      "d" matches [^abc]       |
|  ^          Start of string      "^Hello" matches start   |
|  $          End of string        "end$" matches end       |
|                                                           |
+----------------------------------------------------------+
```

---

## 2.8 Complete Preprocessing Pipeline

Now let us put everything together into a complete, reusable preprocessing pipeline.

### 2.8.1 Pipeline with NLTK

```python
import re
import nltk
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

def preprocess_nltk(text):
    """Complete text preprocessing pipeline using NLTK."""

    # Step 1: Lowercase
    text = text.lower()

    # Step 2: Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Step 3: Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)

    # Step 4: Remove special characters (keep letters and spaces)
    text = re.sub(r'[^a-z\s]', '', text)

    # Step 5: Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Step 6: Tokenize
    tokens = word_tokenize(text)

    # Step 7: Remove stop words
    stop_words = set(stopwords.words('english'))
    tokens = [t for t in tokens if t not in stop_words]

    # Step 8: Lemmatize
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(t, pos='v') for t in tokens]

    return tokens

# Test the pipeline
texts = [
    "I absolutely LOVED this movie!!! Best film ever <3",
    "The acting was terrible... worst $15 I've ever spent :(",
    "Check out https://example.com for more reviews!!! #movies",
]

for text in texts:
    result = preprocess_nltk(text)
    print(f"Original: {text}")
    print(f"Cleaned:  {result}")
    print()
```

**Output:**
```
Original: I absolutely LOVED this movie!!! Best film ever <3
Cleaned:  ['absolutely', 'love', 'movie', 'best', 'film', 'ever']

Original: The acting was terrible... worst $15 I've ever spent :(
Cleaned:  ['act', 'terrible', 'worst', 'ever', 'spend']

Original: Check out https://example.com for more reviews!!! #movies
Cleaned:  ['check', 'review', 'movie']
```

### 2.8.2 Pipeline with spaCy

```python
import re
import spacy

nlp = spacy.load("en_core_web_sm")

def preprocess_spacy(text):
    """Complete text preprocessing pipeline using spaCy."""

    # Step 1: Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Step 2: Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)

    # Step 3: Process with spaCy
    doc = nlp(text.lower())

    # Step 4: Lemmatize, remove stop words and punctuation
    tokens = [
        token.lemma_           # Use the lemma (base form)
        for token in doc
        if not token.is_stop   # Skip stop words
        and not token.is_punct # Skip punctuation
        and not token.is_space # Skip whitespace
        and len(token.text) > 1 # Skip single characters
    ]

    return tokens

# Test the pipeline
texts = [
    "I absolutely LOVED this movie!!! Best film ever <3",
    "The acting was terrible... worst $15 I've ever spent :(",
    "The children were running and playing happily in the garden",
]

for text in texts:
    result = preprocess_spacy(text)
    print(f"Original: {text}")
    print(f"Cleaned:  {result}")
    print()
```

**Output:**
```
Original: I absolutely LOVED this movie!!! Best film ever <3
Cleaned:  ['absolutely', 'love', 'movie', 'good', 'film']

Original: The acting was terrible... worst $15 I've ever spent :(
Cleaned:  ['acting', 'terrible', 'bad', '15', 'spend']

Original: The children were running and playing happily in the garden
Cleaned:  ['child', 'run', 'play', 'happily', 'garden']
```

Notice how spaCy's lemmatizer correctly converts "children" to "child" and "Best" to "good" -- it understands that "best" is the superlative form of "good."

### 2.8.3 Processing Multiple Documents

In real projects, you often need to preprocess many documents at once:

```python
import re
import spacy

nlp = spacy.load("en_core_web_sm")

def preprocess_batch(texts):
    """Preprocess a batch of texts efficiently with spaCy."""

    # Clean all texts first
    cleaned = []
    for text in texts:
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        cleaned.append(text.lower())

    # Use spaCy's pipe for efficient batch processing
    # pipe() processes multiple texts much faster than one at a time
    results = []
    for doc in nlp.pipe(cleaned, batch_size=50):
        tokens = [
            token.lemma_
            for token in doc
            if not token.is_stop
            and not token.is_punct
            and not token.is_space
            and len(token.text) > 1
        ]
        results.append(tokens)

    return results

# Example with multiple reviews
reviews = [
    "Great product! Works perfectly.",
    "Terrible quality. Very disappointed.",
    "It's okay, nothing special really.",
    "Absolutely amazing! Best purchase ever!",
    "Broke after two days. Want my money back.",
]

processed = preprocess_batch(reviews)
for original, cleaned in zip(reviews, processed):
    print(f"Original: {original}")
    print(f"Cleaned:  {cleaned}")
    print()
```

**Output:**
```
Original: Great product! Works perfectly.
Cleaned:  ['great', 'product', 'work', 'perfectly']

Original: Terrible quality. Very disappointed.
Cleaned:  ['terrible', 'quality', 'disappointed']

Original: It's okay, nothing special really.
Cleaned:  ['okay', 'special', 'really']

Original: Absolutely amazing! Best purchase ever!
Cleaned:  ['absolutely', 'amazing', 'good', 'purchase']

Original: Broke after two days. Want my money back.
Cleaned:  ['break', 'day', 'want', 'money']
```

**Line-by-line explanation:**

1. `nlp.pipe(cleaned, batch_size=50)` -- Process texts in batches of 50 for efficiency. `pipe()` is much faster than calling `nlp()` on each text individually because it processes them in parallel.
2. The rest of the pipeline is the same as before -- lemmatize and filter tokens.

---

## 2.9 The Complete Preprocessing Pipeline Diagram

```
+------------------------------------------------------------------+
|               Complete Text Preprocessing Pipeline                |
+------------------------------------------------------------------+
|                                                                    |
|  Raw Text: "I LOVED this movie!!! <br> Check https://t.co/abc"    |
|     |                                                              |
|     v                                                              |
|  +---------------------+                                           |
|  | 1. Remove HTML Tags  |  "I LOVED this movie!!! Check ..."      |
|  +---------------------+                                           |
|     |                                                              |
|     v                                                              |
|  +---------------------+                                           |
|  | 2. Remove URLs       |  "I LOVED this movie!!!"                |
|  +---------------------+                                           |
|     |                                                              |
|     v                                                              |
|  +---------------------+                                           |
|  | 3. Lowercase         |  "i loved this movie!!!"                |
|  +---------------------+                                           |
|     |                                                              |
|     v                                                              |
|  +---------------------+                                           |
|  | 4. Remove Punctuation|  "i loved this movie"                   |
|  +---------------------+                                           |
|     |                                                              |
|     v                                                              |
|  +---------------------+                                           |
|  | 5. Tokenize          |  ["i", "loved", "this", "movie"]        |
|  +---------------------+                                           |
|     |                                                              |
|     v                                                              |
|  +---------------------+                                           |
|  | 6. Remove Stop Words |  ["loved", "movie"]                     |
|  +---------------------+                                           |
|     |                                                              |
|     v                                                              |
|  +---------------------+                                           |
|  | 7. Lemmatize         |  ["love", "movie"]                      |
|  +---------------------+                                           |
|     |                                                              |
|     v                                                              |
|  Clean Tokens: ["love", "movie"]                                   |
|                                                                    |
+------------------------------------------------------------------+
```

---

## Common Mistakes

1. **Applying preprocessing steps in the wrong order** -- Always remove HTML and URLs before tokenizing. If you tokenize first, HTML tags become garbage tokens.

2. **Removing stop words for every task** -- For sentiment analysis, "not" is critical. For topic modeling, stop words are noise. Think about your task before deciding.

3. **Using stemming when you need real words** -- If you need to show results to users, use lemmatization. Stemmed words like "studi" confuse people.

4. **Forgetting to apply the same preprocessing to test data** -- If you lowercase and lemmatize during training, you must do the exact same steps on new data at prediction time.

5. **Over-preprocessing** -- Removing too much can destroy useful signal. For example, removing all numbers loses information in reviews like "This laptop only lasted 2 days."

---

## Best Practices

1. **Document your preprocessing steps** -- Write down exactly what you do and in what order. This makes your work reproducible.

2. **Use spaCy for production, NLTK for learning** -- spaCy is faster and designed for real applications. NLTK has more educational tools and flexibility.

3. **Keep the original text** -- Always store the raw text alongside your cleaned version. You might need to go back to it later.

4. **Test on edge cases** -- Try your pipeline on emojis, numbers, URLs, HTML, non-English characters, and empty strings. Make sure it handles them without crashing.

5. **Consider your domain** -- Medical text needs different preprocessing than social media text. Customize your pipeline for your specific use case.

---

## Quick Summary

Text preprocessing transforms raw, messy text into clean, consistent data for NLP models. The key steps are: lowercasing (making everything lowercase), removing noise (HTML, URLs, punctuation), tokenization (splitting text into words or subwords), removing stop words (dropping common words like "the" and "is"), and stemming or lemmatization (reducing words to their base forms). Regular expressions are a powerful tool for pattern-based text cleaning. NLTK and spaCy are the two main Python libraries for text preprocessing, each with their own strengths.

---

## Key Points

- **Tokenization** splits text into tokens (words, subwords, or sentences). NLTK, spaCy, and Hugging Face tokenizers each handle this differently.
- **Lowercasing** ensures "Apple" and "apple" are treated as the same word, but loses information about proper nouns.
- **Punctuation removal** reduces noise but should preserve contractions and domain-specific symbols when needed.
- **Stop words** are common words that add little meaning. Remove them for most tasks, but keep them when negation or phrases matter.
- **Stemming** is fast but crude -- it chops word endings and may produce non-words.
- **Lemmatization** is slower but accurate -- it uses a dictionary to find proper base forms.
- **Regular expressions** are pattern-matching tools essential for removing HTML, URLs, emails, and other noise.
- Always apply the same preprocessing steps to both training and test data.

---

## Practice Questions

1. What is the difference between word tokenization and subword tokenization? When would you use each one?

2. Given the sentence "The children are NOT enjoying their studies," walk through each preprocessing step (lowercase, tokenize, remove stop words, lemmatize) and show the output at each stage. What potential problem do you see with removing stop words here?

3. Write a regular expression that matches phone numbers in the format "XXX-XXX-XXXX" where X is a digit.

4. Explain the difference between stemming and lemmatization using the words "better," "running," and "studies" as examples.

5. Why is the order of preprocessing steps important? What would go wrong if you tokenized before removing HTML tags?

---

## Exercises

### Exercise 1: Custom Preprocessing Pipeline

Write a function `custom_preprocess(text, options)` that accepts an `options` dictionary to control which steps are applied:

```python
options = {
    'lowercase': True,
    'remove_html': True,
    'remove_urls': True,
    'remove_numbers': False,
    'remove_punctuation': True,
    'remove_stopwords': True,
    'lemmatize': True
}
```

Test it on five different types of text: a tweet, an email, an HTML snippet, a product review, and a scientific abstract.

### Exercise 2: Compare Preprocessing Methods

Take a set of 10 product reviews and preprocess them three different ways:
1. Only lowercase and tokenize
2. Lowercase, tokenize, and remove stop words
3. Full pipeline (lowercase, remove punctuation, tokenize, remove stop words, lemmatize)

For each method, count the total number of unique tokens. How much does each step reduce the vocabulary?

### Exercise 3: Regex Challenge

Write regular expressions to extract the following from a block of text:
1. All email addresses
2. All dates in the format "MM/DD/YYYY"
3. All prices in the format "$XX.XX"
4. All hashtags (words starting with #)
5. All mentions (words starting with @)

Test your patterns on a paragraph that contains examples of each.

---

## What Is Next?

Now that you know how to clean and prepare text, the next question is: how do we convert words into numbers that a machine learning model can understand? In **Chapter 3: Text Representation -- Bag of Words and TF-IDF**, you will learn two foundational methods for turning text into numerical vectors. These methods are simple, powerful, and still used widely in industry today.
