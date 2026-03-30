# Chapter 20: Preparing Training Data

## What You Will Learn

In this chapter, you will learn:

- What training data formats LLMs use (instruction and chat formats)
- Why quality matters more than quantity for fine-tuning
- How to clean and validate training data
- How to augment limited data to create more examples
- How to create instruction datasets from scratch
- What tools are available for data preparation

## Why This Chapter Matters

Fine-tuning is only as good as the data you train on. You could have the best model architecture, the most expensive hardware, and the most sophisticated training pipeline. If your training data is bad, the result will be bad. Garbage in, garbage out.

Think of training data like the ingredients in a recipe. A master chef cannot make a great meal with rotten ingredients. Similarly, you cannot fine-tune a great model with sloppy, inconsistent, or incorrect training examples.

This chapter is the most important prerequisite for fine-tuning. Skipping data preparation is the number one reason fine-tuning projects fail. Companies spend weeks training models only to discover the training data had errors, inconsistencies, or biases that ruined the result. Investing time in data preparation saves money, time, and frustration.

---

## Training Data Formats

LLMs use specific data formats for fine-tuning. The two most common are instruction format and chat format.

### Instruction Format

> **Instruction Format:** A training example with an instruction (what to do), an optional input (the data to work with), and an output (the expected response). This is the simplest format for fine-tuning.

```python
import json

# Instruction format examples
instruction_examples = [
    {
        "instruction": "Classify the sentiment of the following review.",
        "input": "This product exceeded my expectations! The quality is "
                 "outstanding and the price is very reasonable.",
        "output": "positive"
    },
    {
        "instruction": "Classify the sentiment of the following review.",
        "input": "Terrible purchase. Broke after two days and customer "
                 "service was unhelpful.",
        "output": "negative"
    },
    {
        "instruction": "Summarize the following text in one sentence.",
        "input": "The company announced quarterly earnings that exceeded "
                 "analyst expectations by 15%. Revenue grew to $2.3 billion, "
                 "driven primarily by strong performance in the cloud "
                 "computing division. The stock price rose 8% in after-hours "
                 "trading.",
        "output": "The company reported quarterly earnings 15% above "
                  "expectations with $2.3B revenue, boosted by cloud "
                  "computing, causing an 8% stock price increase."
    },
    {
        "instruction": "Translate the following English text to French.",
        "input": "Good morning, how are you?",
        "output": "Bonjour, comment allez-vous ?"
    },
]

print("INSTRUCTION FORMAT EXAMPLES")
print("=" * 55)
for i, example in enumerate(instruction_examples, 1):
    print(f"\nExample {i}:")
    print(f"  Instruction: {example['instruction']}")
    print(f"  Input:       {example['input'][:60]}...")
    print(f"  Output:      {example['output'][:60]}...")

# Save as JSONL (JSON Lines - one JSON object per line)
output_file = "training_data_instruction.jsonl"
with open(output_file, 'w') as f:
    for example in instruction_examples:
        f.write(json.dumps(example) + '\n')

print(f"\nSaved {len(instruction_examples)} examples to {output_file}")
```

**Output:**
```
INSTRUCTION FORMAT EXAMPLES
=======================================================

Example 1:
  Instruction: Classify the sentiment of the following review.
  Input:       This product exceeded my expectations! The quality is ou...
  Output:      positive...

Example 2:
  Instruction: Classify the sentiment of the following review.
  Input:       Terrible purchase. Broke after two days and customer ser...
  Output:      negative...

Example 3:
  Instruction: Summarize the following text in one sentence.
  Input:       The company announced quarterly earnings that exceeded a...
  Output:      The company reported quarterly earnings 15% above expect...

Example 4:
  Instruction: Translate the following English text to French.
  Input:       Good morning, how are you?...
  Output:      Bonjour, comment allez-vous ?...

Saved 4 examples to training_data_instruction.jsonl
```

**Line-by-line explanation:**

- `instruction` tells the model what task to perform. This stays the same for similar tasks.
- `input` is the data the model should work on. This changes for each example.
- `output` is the correct response the model should learn to produce.
- JSONL format stores one JSON object per line. This is the standard format for training data because it is easy to append, process line by line, and handle large files.

### Chat Format

> **Chat Format:** A training example structured as a conversation between a user and an assistant. This format is used for training chatbots and conversational models. It can include system messages, multi-turn conversations, and function calls.

```python
import json

# Chat format examples (OpenAI style)
chat_examples = [
    {
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful customer support agent for "
                           "TechCorp. Be polite, concise, and helpful."
            },
            {
                "role": "user",
                "content": "My laptop won't turn on. What should I do?"
            },
            {
                "role": "assistant",
                "content": "I'm sorry to hear your laptop isn't turning on. "
                           "Let's try a few steps:\n\n"
                           "1. Make sure the charger is plugged in and the "
                           "charging light is on.\n"
                           "2. Hold the power button for 15 seconds, then "
                           "release and press it normally.\n"
                           "3. If it still doesn't work, try removing the "
                           "battery (if removable), holding the power button "
                           "for 30 seconds, then reinserting the battery.\n\n"
                           "Did any of these steps help?"
            }
        ]
    },
    {
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful customer support agent for "
                           "TechCorp. Be polite, concise, and helpful."
            },
            {
                "role": "user",
                "content": "How do I cancel my subscription?"
            },
            {
                "role": "assistant",
                "content": "To cancel your subscription, follow these steps:\n\n"
                           "1. Go to Settings > Billing\n"
                           "2. Click 'Cancel Subscription'\n"
                           "3. Select a reason for cancellation\n"
                           "4. Confirm the cancellation\n\n"
                           "Your subscription will remain active until the end "
                           "of your current billing period. Is there anything "
                           "I can help with to improve your experience?"
            }
        ]
    },
    # Multi-turn conversation example
    {
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful customer support agent for "
                           "TechCorp. Be polite, concise, and helpful."
            },
            {
                "role": "user",
                "content": "I need to return a product."
            },
            {
                "role": "assistant",
                "content": "I'd be happy to help with your return. Could you "
                           "please provide your order number?"
            },
            {
                "role": "user",
                "content": "It's ORD-45678."
            },
            {
                "role": "assistant",
                "content": "Thank you! I found order ORD-45678. This order "
                           "is within our 30-day return window. To proceed:\n\n"
                           "1. Go to Orders > ORD-45678 > Request Return\n"
                           "2. Select the items to return\n"
                           "3. Print the prepaid shipping label\n"
                           "4. Drop off at any UPS location\n\n"
                           "Your refund will be processed within 5-7 business "
                           "days after we receive the item."
            }
        ]
    },
]

print("CHAT FORMAT EXAMPLES")
print("=" * 55)
for i, example in enumerate(chat_examples, 1):
    print(f"\nConversation {i} ({len(example['messages'])} messages):")
    for msg in example['messages']:
        role = msg['role'].upper()
        content = msg['content'][:60]
        print(f"  [{role}] {content}...")

# Save as JSONL
with open("training_data_chat.jsonl", 'w') as f:
    for example in chat_examples:
        f.write(json.dumps(example) + '\n')

print(f"\nSaved {len(chat_examples)} conversations")
```

**Output:**
```
CHAT FORMAT EXAMPLES
=======================================================

Conversation 1 (3 messages):
  [SYSTEM] You are a helpful customer support agent for TechCor...
  [USER] My laptop won't turn on. What should I do?...
  [ASSISTANT] I'm sorry to hear your laptop isn't turning on. Let...

Conversation 2 (3 messages):
  [SYSTEM] You are a helpful customer support agent for TechCor...
  [USER] How do I cancel my subscription?...
  [ASSISTANT] To cancel your subscription, follow these steps:

1...

Conversation 3 (5 messages):
  [SYSTEM] You are a helpful customer support agent for TechCor...
  [USER] I need to return a product....
  [ASSISTANT] I'd be happy to help with your return. Could you plea...
  [USER] It's ORD-45678....
  [ASSISTANT] Thank you! I found order ORD-45678. This order is wit...

Saved 3 conversations
```

**Line-by-line explanation:**

- `"role": "system"` sets the assistant's behavior and personality. It is included in every conversation.
- `"role": "user"` is what the customer/user says.
- `"role": "assistant"` is the response you want the model to learn to produce.
- Multi-turn conversations (Conversation 3) teach the model to handle follow-up questions naturally.
- Each JSONL line is one complete conversation, even if it has multiple turns.

---

## Quality Over Quantity

```
+------------------------------------------------------------------+
|              QUALITY vs QUANTITY IN TRAINING DATA                  |
|                                                                   |
|  100 high-quality examples    >    10,000 low-quality examples    |
|                                                                   |
|  HIGH QUALITY means:                                              |
|  +----------------------------------------------------------+   |
|  | [x] Correct answers (verified by a human)                  |   |
|  | [x] Consistent format (same style throughout)              |   |
|  | [x] Clear instructions (unambiguous tasks)                 |   |
|  | [x] Diverse inputs (covers edge cases)                     |   |
|  | [x] Representative (matches real-world distribution)       |   |
|  | [x] No contradictions (examples don't conflict)            |   |
|  +----------------------------------------------------------+   |
|                                                                   |
|  LOW QUALITY means:                                               |
|  +----------------------------------------------------------+   |
|  | [x] Some answers are wrong                                 |   |
|  | [x] Inconsistent formatting                                |   |
|  | [x] Vague or ambiguous instructions                        |   |
|  | [x] All examples are similar (no diversity)                |   |
|  | [x] Does not match real usage patterns                     |   |
|  | [x] Contradictory examples confuse the model               |   |
|  +----------------------------------------------------------+   |
+------------------------------------------------------------------+
```

```python
# Example: Good vs bad training data

good_examples = [
    # Clear, consistent, correct
    {
        "instruction": "Extract the company name and revenue from the text.",
        "input": "Apple Inc. reported revenue of $94.8 billion for Q1 2024.",
        "output": '{"company": "Apple Inc.", "revenue": "$94.8 billion"}'
    },
    {
        "instruction": "Extract the company name and revenue from the text.",
        "input": "Microsoft's quarterly revenue reached $62.0 billion.",
        "output": '{"company": "Microsoft", "revenue": "$62.0 billion"}'
    },
    {
        "instruction": "Extract the company name and revenue from the text.",
        "input": "No financial data was mentioned in the press release.",
        "output": '{"company": null, "revenue": null}'
    },
]

bad_examples = [
    # Inconsistent format
    {
        "instruction": "Get company and revenue",
        "input": "Apple Inc. reported revenue of $94.8 billion for Q1 2024.",
        "output": "Company: Apple, Revenue: 94.8B"  # Different format!
    },
    {
        "instruction": "Extract the company name and revenue from the text.",
        "input": "Microsoft's quarterly revenue reached $62.0 billion.",
        "output": '{"name": "MSFT", "rev": "62B"}'  # Different keys!
    },
    {
        "instruction": "find revenue",  # Vague, lowercase
        "input": "No financial data was mentioned.",
        "output": "I couldn't find any revenue."  # Not JSON!
    },
]

print("GOOD Training Data (consistent format):")
for ex in good_examples:
    print(f"  Output: {ex['output']}")

print("\nBAD Training Data (inconsistent format):")
for ex in bad_examples:
    print(f"  Output: {ex['output']}")

print("\nThe bad examples use different formats, different keys,")
print("different styles. This confuses the model during training.")
```

**Output:**
```
GOOD Training Data (consistent format):
  Output: {"company": "Apple Inc.", "revenue": "$94.8 billion"}
  Output: {"company": "Microsoft", "revenue": "$62.0 billion"}
  Output: {"company": null, "revenue": null}

BAD Training Data (inconsistent format):
  Output: Company: Apple, Revenue: 94.8B
  Output: {"name": "MSFT", "rev": "62B"}
  Output: I couldn't find any revenue.

The bad examples use different formats, different keys,
different styles. This confuses the model during training.
```

---

## Data Cleaning Pipeline

```python
import json
import re
from typing import List, Dict, Tuple

class TrainingDataCleaner:
    """Clean and validate training data for fine-tuning."""

    def __init__(self):
        self.issues = []

    def clean(self, examples: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Clean training data and separate good from problematic examples.

        Returns:
            Tuple of (clean_examples, problematic_examples)
        """
        clean = []
        problematic = []

        for i, example in enumerate(examples):
            issues = self._validate_example(example, i)

            if issues:
                problematic.append({
                    "index": i,
                    "example": example,
                    "issues": issues,
                })
            else:
                cleaned = self._clean_example(example)
                clean.append(cleaned)

        return clean, problematic

    def _validate_example(self, example: Dict, index: int) -> List[str]:
        """Check for common issues in a training example."""
        issues = []

        # Check required fields
        if "instruction" in example:
            # Instruction format
            if not example.get("instruction", "").strip():
                issues.append("Empty instruction")
            if not example.get("output", "").strip():
                issues.append("Empty output")
        elif "messages" in example:
            # Chat format
            messages = example.get("messages", [])
            if len(messages) < 2:
                issues.append("Chat needs at least 2 messages")

            roles = [m.get("role") for m in messages]
            if "assistant" not in roles:
                issues.append("No assistant message in chat")

            for j, msg in enumerate(messages):
                if not msg.get("content", "").strip():
                    issues.append(f"Empty content in message {j}")
        else:
            issues.append("Unknown format (no 'instruction' or 'messages' key)")

        # Check for overly short outputs
        output = example.get("output", "")
        if output and len(output) < 3:
            issues.append(f"Output too short: '{output}'")

        # Check for potential PII
        pii_patterns = [
            (r'\b\d{3}-\d{2}-\d{4}\b', "Possible SSN"),
            (r'\b\d{16}\b', "Possible credit card number"),
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
             "Email address found"),
        ]

        text = json.dumps(example)
        for pattern, label in pii_patterns:
            if re.search(pattern, text):
                issues.append(label)

        return issues

    def _clean_example(self, example: Dict) -> Dict:
        """Clean a single training example."""
        cleaned = {}

        if "instruction" in example:
            cleaned["instruction"] = example["instruction"].strip()
            cleaned["input"] = example.get("input", "").strip()
            cleaned["output"] = example["output"].strip()
        elif "messages" in example:
            cleaned["messages"] = []
            for msg in example["messages"]:
                cleaned["messages"].append({
                    "role": msg["role"],
                    "content": msg["content"].strip(),
                })

        return cleaned

    def report(self, clean: List, problematic: List):
        """Print a cleaning report."""
        total = len(clean) + len(problematic)
        print("DATA CLEANING REPORT")
        print("=" * 50)
        print(f"Total examples:       {total}")
        print(f"Clean examples:       {len(clean)} ({len(clean)/total:.0%})")
        print(f"Problematic examples: {len(problematic)} "
              f"({len(problematic)/total:.0%})")

        if problematic:
            print(f"\nIssues found:")
            all_issues = [
                issue
                for p in problematic
                for issue in p["issues"]
            ]
            from collections import Counter
            issue_counts = Counter(all_issues)
            for issue, count in issue_counts.most_common():
                print(f"  [{count}x] {issue}")


# Example usage
test_data = [
    # Good examples
    {
        "instruction": "Classify the sentiment.",
        "input": "Great product, love it!",
        "output": "positive"
    },
    {
        "instruction": "Classify the sentiment.",
        "input": "Terrible experience.",
        "output": "negative"
    },
    # Problematic examples
    {
        "instruction": "",  # Empty instruction
        "input": "Some text",
        "output": "result"
    },
    {
        "instruction": "Extract info.",
        "input": "Contact john.doe@email.com for details.",  # PII
        "output": "email found"
    },
    {
        "instruction": "Summarize.",
        "input": "Long text here...",
        "output": "ok"  # Too short
    },
    {
        "instruction": "Classify.",
        "input": "Text",
        "output": ""  # Empty output
    },
]

cleaner = TrainingDataCleaner()
clean, problematic = cleaner.clean(test_data)
cleaner.report(clean, problematic)

print("\nClean examples:")
for ex in clean:
    print(f"  {ex['instruction']}: {ex['input'][:30]}... -> {ex['output']}")

print("\nProblematic examples:")
for p in problematic:
    print(f"  Index {p['index']}: {p['issues']}")
```

**Output:**
```
DATA CLEANING REPORT
==================================================
Total examples:       6
Clean examples:       2 (33%)
Problematic examples: 4 (67%)

Issues found:
  [1x] Empty instruction
  [1x] Email address found
  [1x] Output too short: 'ok'
  [1x] Empty output

Clean examples:
  Classify the sentiment.: Great product, love it!... -> positive
  Classify the sentiment.: Terrible experience.... -> negative

Problematic examples:
  Index 2: ['Empty instruction']
  Index 3: ['Email address found']
  Index 4: ["Output too short: 'ok'"]
  Index 5: ['Empty output']
```

---

## Data Augmentation

When you have limited training data, augmentation creates additional examples from your existing ones.

> **Data Augmentation:** Creating new training examples by modifying existing ones. Techniques include paraphrasing, changing the order of information, adding noise, or generating variations with an LLM.

```python
from openai import OpenAI
import json

client = OpenAI()

def augment_instruction_data(
    examples: list,
    augmentations_per_example: int = 3,
    model: str = "gpt-4o-mini"
) -> list:
    """
    Generate additional training examples by paraphrasing existing ones.

    Uses an LLM to create variations that preserve the meaning
    but use different wording.
    """
    augmented = []

    for example in examples:
        # Keep the original
        augmented.append(example)

        # Generate variations of the input
        prompt = f"""Generate {augmentations_per_example} different ways to
express the same input text. Each variation should:
1. Preserve the core meaning
2. Use different words and sentence structure
3. Be roughly the same length

Original input: {example['input']}

Return ONLY the variations, one per line, no numbering."""

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
        )

        variations = response.choices[0].message.content.strip().split('\n')
        variations = [v.strip() for v in variations if v.strip()]

        for var in variations[:augmentations_per_example]:
            augmented.append({
                "instruction": example["instruction"],
                "input": var,
                "output": example["output"],
            })

    return augmented


# Example: augmenting sentiment classification data
original_data = [
    {
        "instruction": "Classify the sentiment as positive, negative, or neutral.",
        "input": "This product is amazing! Best purchase I've ever made.",
        "output": "positive"
    },
    {
        "instruction": "Classify the sentiment as positive, negative, or neutral.",
        "input": "Terrible quality. It broke on the first day.",
        "output": "negative"
    },
]

print(f"Original examples: {len(original_data)}")

augmented_data = augment_instruction_data(original_data, augmentations_per_example=2)

print(f"After augmentation: {len(augmented_data)}")
print()

for i, example in enumerate(augmented_data):
    marker = "[ORIGINAL]" if i % 3 == 0 else "[AUGMENTED]"
    print(f"  {marker} Input: {example['input'][:55]}...")
    print(f"           Output: {example['output']}")
    print()
```

**Output:**
```
Original examples: 2
After augmentation: 6

  [ORIGINAL] Input: This product is amazing! Best purchase I've ever ma...
           Output: positive

  [AUGMENTED] Input: What an incredible product! This is hands down the be...
           Output: positive

  [AUGMENTED] Input: I absolutely love this item! It's the greatest thing ...
           Output: positive

  [ORIGINAL] Input: Terrible quality. It broke on the first day....
           Output: negative

  [AUGMENTED] Input: The quality is awful. It stopped working after just o...
           Output: negative

  [AUGMENTED] Input: What poor craftsmanship. It fell apart within 24 hour...
           Output: negative
```

**Line-by-line explanation:**

- `augment_instruction_data()` takes existing examples and generates variations using an LLM.
- The LLM paraphrases the input while keeping the same meaning and the same output label.
- `temperature=0.8` encourages variety in the paraphrases. Lower temperature would produce more conservative variations.
- From 2 original examples, we created 6 total (2 original + 4 augmented). This is a 3x increase with minimal effort.
- Important: Always verify augmented examples. The LLM might occasionally change the meaning enough to warrant a different label.

---

## Creating Instruction Datasets from Scratch

```python
from openai import OpenAI
import json

client = OpenAI()

def generate_instruction_dataset(
    task_description: str,
    num_examples: int = 10,
    model: str = "gpt-4o-mini"
) -> list:
    """
    Generate a training dataset for a specific task using an LLM.

    This is useful when you have no existing data and need to
    bootstrap a training set.
    """
    prompt = f"""Generate {num_examples} training examples for the following task.

Task: {task_description}

For each example, provide:
1. An instruction (what to do)
2. An input (the data to process)
3. An output (the expected result)

Make the examples diverse - cover different scenarios, edge cases,
and difficulty levels. Make the inputs realistic.

Return as a JSON array of objects with "instruction", "input", and "output" keys.
"""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.9,
    )

    result = json.loads(response.choices[0].message.content)

    # Handle different response structures
    if isinstance(result, dict):
        examples = result.get("examples", result.get("data", []))
    elif isinstance(result, list):
        examples = result
    else:
        examples = []

    return examples


# Generate a dataset for email subject line generation
task = """Generate professional email subject lines from email body text.
The subject should be concise (under 10 words), informative, and
appropriate for a business context."""

print("Generating training examples...")
examples = generate_instruction_dataset(task, num_examples=5)

print(f"\nGenerated {len(examples)} examples:\n")
for i, ex in enumerate(examples, 1):
    print(f"Example {i}:")
    print(f"  Instruction: {ex.get('instruction', 'N/A')}")
    print(f"  Input:       {ex.get('input', 'N/A')[:60]}...")
    print(f"  Output:      {ex.get('output', 'N/A')}")
    print()
```

**Output:**
```
Generating training examples...

Generated 5 examples:

Example 1:
  Instruction: Generate a professional email subject line for this email body.
  Input:       Hi team, just wanted to let you know that the Q3 budget rev...
  Output:      Q3 Budget Review Meeting Scheduled

Example 2:
  Instruction: Generate a professional email subject line for this email body.
  Input:       Dear Mr. Johnson, Thank you for your interest in our enterp...
  Output:      Enterprise Plan Proposal Follow-Up

Example 3:
  Instruction: Generate a professional email subject line for this email body.
  Input:       Team, please be aware that the office will be closed next M...
  Output:      Office Closure Notice - Next Monday

Example 4:
  Instruction: Generate a professional email subject line for this email body.
  Input:       Hi Sarah, I reviewed the pull request you submitted yesterda...
  Output:      Pull Request Feedback - Authentication Module

Example 5:
  Instruction: Generate a professional email subject line for this email body.
  Input:       Dear all, we're excited to announce that our new product li...
  Output:      New Product Line Launch Announcement
```

---

## Validating Your Dataset

```python
import json
from collections import Counter
from typing import List, Dict

def validate_dataset(examples: List[Dict], format_type: str = "instruction"):
    """
    Comprehensive validation of a training dataset.

    Checks for:
    - Required fields
    - Consistency
    - Duplicates
    - Length distribution
    - Label balance (for classification)
    """
    print("DATASET VALIDATION REPORT")
    print("=" * 55)
    print(f"Format: {format_type}")
    print(f"Total examples: {len(examples)}")

    issues = []
    outputs = []
    input_lengths = []
    output_lengths = []
    instructions = set()

    for i, ex in enumerate(examples):
        if format_type == "instruction":
            # Check required fields
            if not ex.get("instruction"):
                issues.append(f"Example {i}: Missing instruction")
            if not ex.get("output"):
                issues.append(f"Example {i}: Missing output")

            instructions.add(ex.get("instruction", ""))
            outputs.append(ex.get("output", ""))
            input_lengths.append(len(ex.get("input", "")))
            output_lengths.append(len(ex.get("output", "")))

        elif format_type == "chat":
            messages = ex.get("messages", [])
            if len(messages) < 2:
                issues.append(f"Example {i}: Too few messages")
            roles = [m["role"] for m in messages]
            if "assistant" not in roles:
                issues.append(f"Example {i}: No assistant message")

    # Check for duplicates
    seen_inputs = set()
    duplicates = 0
    for ex in examples:
        input_text = ex.get("input", str(ex.get("messages", "")))
        if input_text in seen_inputs:
            duplicates += 1
        seen_inputs.add(input_text)

    # Print results
    print(f"\nField Issues: {len(issues)}")
    for issue in issues[:5]:
        print(f"  - {issue}")
    if len(issues) > 5:
        print(f"  ... and {len(issues) - 5} more")

    print(f"\nDuplicates: {duplicates}")
    print(f"Unique instructions: {len(instructions)}")

    if input_lengths:
        print(f"\nInput length (chars):")
        print(f"  Min: {min(input_lengths)}")
        print(f"  Max: {max(input_lengths)}")
        print(f"  Avg: {sum(input_lengths) // len(input_lengths)}")

    if output_lengths:
        print(f"\nOutput length (chars):")
        print(f"  Min: {min(output_lengths)}")
        print(f"  Max: {max(output_lengths)}")
        print(f"  Avg: {sum(output_lengths) // len(output_lengths)}")

    # Check label distribution (for classification tasks)
    if outputs:
        output_counter = Counter(outputs)
        if len(output_counter) <= 20:
            print(f"\nOutput distribution:")
            for label, count in output_counter.most_common():
                pct = count / len(outputs) * 100
                bar = "|" * int(pct / 2)
                print(f"  {label:<20} {count:>4} ({pct:>5.1f}%) {bar}")

    # Overall assessment
    print(f"\nOVERALL ASSESSMENT:")
    if len(issues) == 0 and duplicates == 0:
        print("  PASS - Dataset looks good!")
    elif len(issues) < len(examples) * 0.05:
        print("  WARNING - Minor issues found. Review and fix.")
    else:
        print("  FAIL - Significant issues. Clean before training.")


# Test with a sample dataset
sample_dataset = [
    {"instruction": "Classify sentiment", "input": "Great product!", "output": "positive"},
    {"instruction": "Classify sentiment", "input": "Terrible service.", "output": "negative"},
    {"instruction": "Classify sentiment", "input": "It's okay.", "output": "neutral"},
    {"instruction": "Classify sentiment", "input": "Love it!", "output": "positive"},
    {"instruction": "Classify sentiment", "input": "Waste of money.", "output": "negative"},
    {"instruction": "Classify sentiment", "input": "Not bad.", "output": "neutral"},
    {"instruction": "Classify sentiment", "input": "Highly recommend!", "output": "positive"},
    {"instruction": "Classify sentiment", "input": "Never buying again.", "output": "negative"},
    {"instruction": "Classify sentiment", "input": "Average quality.", "output": "neutral"},
    {"instruction": "Classify sentiment", "input": "Exceeded expectations!", "output": "positive"},
]

validate_dataset(sample_dataset)
```

**Output:**
```
DATASET VALIDATION REPORT
=======================================================
Format: instruction
Total examples: 10

Field Issues: 0

Duplicates: 0
Unique instructions: 1

Input length (chars):
  Min: 9
  Max: 23
  Avg: 15

Output length (chars):
  Min: 7
  Max: 8
  Avg: 7

Output distribution:
  positive             4 ( 40.0%) ||||||||||||||||||||
  negative             3 ( 30.0%) |||||||||||||||
  neutral              3 ( 30.0%) |||||||||||||||

OVERALL ASSESSMENT:
  PASS - Dataset looks good!
```

---

## Tools for Data Preparation

```python
tools = [
    {
        "name": "Argilla",
        "purpose": "Data labeling and annotation",
        "features": "Web-based UI for labeling, team collaboration, "
                    "active learning suggestions",
        "install": "pip install argilla",
        "best_for": "Teams labeling data together",
    },
    {
        "name": "Label Studio",
        "purpose": "Multi-type data annotation",
        "features": "Supports text, images, audio. Templates for NLP tasks. "
                    "Export in multiple formats.",
        "install": "pip install label-studio",
        "best_for": "Complex annotation tasks",
    },
    {
        "name": "Hugging Face Datasets",
        "purpose": "Loading and processing datasets",
        "features": "Access thousands of public datasets. Built-in processing "
                    "functions. Efficient memory usage.",
        "install": "pip install datasets",
        "best_for": "Loading existing datasets for fine-tuning",
    },
    {
        "name": "cleanlab",
        "purpose": "Finding label errors",
        "features": "Automatically detects mislabeled examples in your "
                    "training data using confident learning.",
        "install": "pip install cleanlab",
        "best_for": "Cleaning noisy labeled datasets",
    },
    {
        "name": "Pandas",
        "purpose": "Data manipulation and analysis",
        "features": "Filter, transform, and analyze data. Read CSV, JSON, "
                    "Excel. Statistical summaries.",
        "install": "pip install pandas",
        "best_for": "General data cleaning and transformation",
    },
]

print("TOOLS FOR TRAINING DATA PREPARATION")
print("=" * 55)
for tool in tools:
    print(f"\n{tool['name']}")
    print(f"  Purpose:  {tool['purpose']}")
    print(f"  Features: {tool['features']}")
    print(f"  Install:  {tool['install']}")
    print(f"  Best for: {tool['best_for']}")
```

**Output:**
```
TOOLS FOR TRAINING DATA PREPARATION
=======================================================

Argilla
  Purpose:  Data labeling and annotation
  Features: Web-based UI for labeling, team collaboration, active learning suggestions
  Install:  pip install argilla
  Best for: Teams labeling data together

Label Studio
  Purpose:  Multi-type data annotation
  Features: Supports text, images, audio. Templates for NLP tasks. Export in multiple formats.
  Install:  pip install label-studio
  Best for: Complex annotation tasks

Hugging Face Datasets
  Purpose:  Loading and processing datasets
  Features: Access thousands of public datasets. Built-in processing functions. Efficient memory usage.
  Install:  pip install datasets
  Best for: Loading existing datasets for fine-tuning

cleanlab
  Purpose:  Finding label errors
  Features: Automatically detects mislabeled examples in your training data using confident learning.
  Install:  pip install cleanlab
  Best for: Cleaning noisy labeled datasets

Pandas
  Purpose:  Data manipulation and analysis
  Features: Filter, transform, and analyze data. Read CSV, JSON, Excel. Statistical summaries.
  Install:  pip install pandas
  Best for: General data cleaning and transformation
```

---

## Complete Data Preparation Workflow

```python
def data_preparation_workflow():
    """Print the recommended workflow for preparing training data."""
    workflow = """
DATA PREPARATION WORKFLOW
============================================================

Step 1: Define Your Task
   [ ] Write a clear description of what the model should do
   [ ] List the input types and expected output format
   [ ] Define success criteria (accuracy, format compliance)

Step 2: Collect Seed Data
   [ ] Gather 20-50 high-quality examples
   [ ] Include diverse inputs (easy, hard, edge cases)
   [ ] Verify every output is correct
   [ ] Ensure consistent formatting across all examples

Step 3: Augment Data
   [ ] Use LLM to generate paraphrased inputs
   [ ] Add edge cases and unusual scenarios
   [ ] Target 200-500 examples minimum
   [ ] More is better IF quality is maintained

Step 4: Clean Data
   [ ] Remove duplicates
   [ ] Check for PII (emails, phone numbers, etc.)
   [ ] Validate all required fields are present
   [ ] Ensure output format is consistent
   [ ] Check for contradictory examples

Step 5: Validate Data
   [ ] Run automated validation checks
   [ ] Check label distribution (balance classes)
   [ ] Review a random 10% sample manually
   [ ] Measure inter-annotator agreement if multiple labelers

Step 6: Split Data
   [ ] Training set: 80% of data
   [ ] Validation set: 10% of data
   [ ] Test set: 10% of data (DO NOT use for training)
   [ ] Ensure all splits have similar distributions

Step 7: Format for Training
   [ ] Convert to JSONL format
   [ ] Verify file is valid (each line is valid JSON)
   [ ] Check token counts (stay within model limits)
   [ ] Confirm format matches your training framework
"""
    print(workflow)

data_preparation_workflow()
```

```python
import json
import random

def split_dataset(examples, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1,
                  seed=42):
    """
    Split dataset into train, validation, and test sets.
    """
    random.seed(seed)
    shuffled = examples.copy()
    random.shuffle(shuffled)

    total = len(shuffled)
    train_end = int(total * train_ratio)
    val_end = train_end + int(total * val_ratio)

    train = shuffled[:train_end]
    val = shuffled[train_end:val_end]
    test = shuffled[val_end:]

    print(f"Dataset split:")
    print(f"  Training:   {len(train)} ({len(train)/total:.0%})")
    print(f"  Validation: {len(val)} ({len(val)/total:.0%})")
    print(f"  Test:       {len(test)} ({len(test)/total:.0%})")
    print(f"  Total:      {total}")

    return train, val, test

def save_jsonl(examples, filepath):
    """Save examples to a JSONL file."""
    with open(filepath, 'w') as f:
        for ex in examples:
            f.write(json.dumps(ex) + '\n')
    print(f"Saved {len(examples)} examples to {filepath}")


# Example: complete workflow
dataset = [
    {"instruction": "Classify", "input": f"Text {i}", "output": random.choice(["pos", "neg", "neu"])}
    for i in range(100)
]

train, val, test = split_dataset(dataset)

save_jsonl(train, "train.jsonl")
save_jsonl(val, "val.jsonl")
save_jsonl(test, "test.jsonl")
```

**Output:**
```
Dataset split:
  Training:   80 (80%)
  Validation: 10 (10%)
  Test:       10 (10%)
  Total:      100
Saved 80 examples to train.jsonl
Saved 10 examples to val.jsonl
Saved 10 examples to test.jsonl
```

---

## Common Mistakes

1. **Using unverified data.** Never train on data you have not checked. Wrong labels teach the model wrong behavior. Review every example, especially if generated by an LLM.

2. **Inconsistent output formats.** If some examples use JSON and others use plain text, the model learns to produce unpredictable output. Pick one format and stick with it.

3. **Imbalanced classes.** If 90% of your sentiment examples are "positive," the model learns to always say "positive." Balance your classes or use stratified sampling.

4. **Including PII in training data.** Personal information (names, emails, phone numbers) in training data can leak during inference. Always anonymize sensitive data.

5. **Not creating a test set.** If you train on all your data, you cannot evaluate the model fairly. Always hold out at least 10% for testing.

6. **Too little data for fine-tuning.** While quality matters more than quantity, you still need a minimum of 50-100 examples for basic fine-tuning. Aim for 500+ for best results.

---

## Best Practices

1. **Start with 50 hand-crafted examples.** These should be perfect. They set the standard for quality.

2. **Use consistent formatting throughout.** Same instruction phrasing, same output structure, same edge case handling across all examples.

3. **Include edge cases.** Add examples with unusual inputs, empty fields, ambiguous text, and boundary conditions. The model needs to learn how to handle these.

4. **Augment thoughtfully.** Use LLM augmentation to increase dataset size, but always review the generated examples for accuracy.

5. **Version your datasets.** Keep track of which version of the dataset was used for which training run. This lets you reproduce results and understand what changed.

6. **Document your data decisions.** Write down what you included, what you excluded, and why. Future team members will need this context.

---

## Quick Summary

Training data preparation is the foundation of successful fine-tuning. Two main formats exist: instruction format (instruction, input, output) and chat format (system, user, assistant messages). Quality matters far more than quantity: 100 perfect examples beat 10,000 sloppy ones. Clean your data by checking for missing fields, duplicates, PII, and inconsistencies. Augment limited datasets using LLM paraphrasing. Always split into train, validation, and test sets. Tools like Argilla, Label Studio, and Hugging Face Datasets streamline the process.

---

## Key Points

- **Instruction format** has instruction, input, and output fields
- **Chat format** uses messages with system, user, and assistant roles
- **Quality over quantity**: 100 verified examples beat 10,000 unverified ones
- **Consistency** in format, style, and labels is critical
- **Clean data** by removing duplicates, PII, empty fields, and contradictions
- **Augment** by paraphrasing inputs while keeping the same outputs
- **Split** into 80% train, 10% validation, 10% test
- **JSONL** is the standard file format for training data
- Always **version** your datasets and document your decisions

---

## Practice Questions

1. What is the difference between instruction format and chat format? When would you use each one?

2. You have 1,000 training examples for sentiment classification. 850 are labeled "positive" and 150 are labeled "negative." What problems might this cause during training, and how would you fix it?

3. Why is it dangerous to include real email addresses in your training data? What should you do instead?

4. You generated 500 training examples using an LLM. A colleague says you can just use them directly for fine-tuning. What step are they missing?

5. Explain why you need a test set that is separate from the training set. What goes wrong if you evaluate on training data?

---

## Exercises

**Exercise 1: Build a Training Dataset**

Create a training dataset for a task of your choice (customer support responses, text classification, entity extraction). Write 20 examples by hand, augment to 50+ using LLM paraphrasing, validate the dataset, and split into train/val/test sets. Save as JSONL files.

**Exercise 2: Data Quality Audit**

Take an existing dataset (or generate one with intentional errors) and build a quality audit tool. The tool should check for: missing fields, duplicate inputs, output format inconsistency, class imbalance, and outlier lengths. Generate a quality report with pass/fail for each check.

**Exercise 3: Data Augmentation Pipeline**

Build a pipeline that takes 10 seed examples and generates 100 augmented examples using at least 3 augmentation techniques: paraphrasing, synonym replacement, and adding context. Validate that augmented examples maintain the correct labels by having an LLM verify each one.

---

## What Is Next?

You now have clean, validated, properly formatted training data ready for fine-tuning. In Chapter 21, you will learn about LoRA and QLoRA, efficient techniques for fine-tuning LLMs without needing expensive hardware. These methods make fine-tuning accessible on consumer GPUs by training only a small fraction of the model's parameters.
