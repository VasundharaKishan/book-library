# Chapter 11: Structured Outputs

## What You Will Learn

In this chapter, you will learn:

- Why plain text responses from LLMs are hard to use in real applications
- How to use JSON mode to get structured responses
- How to control the format of LLM outputs
- How to parse and validate responses reliably
- How to use Pydantic models for automatic validation
- How to build reliable data extraction pipelines

## Why This Chapter Matters

Imagine you ask an LLM to extract customer information from an email. The LLM responds with a nice paragraph like "The customer's name is Alice and her email is alice@example.com." That is great for a human to read. But what if your Python code needs to store that name and email in a database?

You would need to somehow find the name and email inside that paragraph. What if the LLM phrases it differently next time? Your parsing code would break.

Structured outputs solve this problem. Instead of getting free-form text, you tell the LLM exactly what format to use. You get back clean JSON that your code can use directly. No guessing. No fragile parsing. Just reliable, predictable data.

This is the difference between a demo and a production application. Real applications need structured data they can depend on.

---

## The Problem with Unstructured Responses

Let us see why plain text responses cause headaches.

```
+------------------------------------------------------------------+
|                    THE PARSING PROBLEM                            |
|                                                                   |
|  Your Prompt:                                                     |
|  "Extract the name and email from this text"                      |
|                                                                   |
|  Response 1: "The name is Alice and email is alice@mail.com"      |
|  Response 2: "Name: Alice, Email: alice@mail.com"                 |
|  Response 3: "I found Alice (alice@mail.com) in the text"         |
|  Response 4: "alice@mail.com belongs to Alice"                    |
|                                                                   |
|  Same information, FOUR different formats!                        |
|  How does your code handle all of them?                           |
|                                                                   |
|  With JSON mode:                                                  |
|  {"name": "Alice", "email": "alice@mail.com"}                    |
|  ALWAYS the same format. Every single time.                       |
+------------------------------------------------------------------+
```

Think of it like ordering food at a restaurant. If you just say "give me something with chicken," you might get a sandwich, a salad, or a curry. But if you fill out an order form with checkboxes, you get exactly what you specified. JSON mode is that order form for LLMs.

---

## What Is JSON?

Before we dive into JSON mode, let us make sure you understand JSON.

> **JSON (JavaScript Object Notation):** A simple text format for storing data as key-value pairs. It uses curly braces `{}` for objects and square brackets `[]` for lists. Despite its name, every programming language can read and write JSON, not just JavaScript.

```python
import json

# A JSON object is like a Python dictionary
person = {
    "name": "Alice",
    "age": 30,
    "email": "alice@example.com",
    "skills": ["Python", "SQL", "ML"]
}

# Convert Python dictionary to JSON string
json_string = json.dumps(person, indent=2)
print(json_string)
```

**Output:**
```
{
  "name": "Alice",
  "age": 30,
  "email": "alice@example.com",
  "skills": [
    "Python",
    "SQL",
    "ML"
  ]
}
```

**Line-by-line explanation:**

- `import json` loads Python's built-in JSON library. No installation needed.
- `person = {...}` creates a Python dictionary. Dictionaries and JSON look almost identical.
- `json.dumps(person, indent=2)` converts the dictionary to a formatted JSON string. The `indent=2` makes it pretty with 2-space indentation.
- `print(json_string)` displays the JSON. Notice the keys are in double quotes. JSON always uses double quotes, never single quotes.

---

## Using JSON Mode with OpenAI

The simplest way to get structured output is to ask the LLM to respond in JSON format.

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant. Always respond in valid JSON format."
        },
        {
            "role": "user",
            "content": """Extract the following from this customer message:
            - customer name
            - product mentioned
            - issue described
            - urgency (low, medium, high)

            Message: "Hi, I'm Sarah Chen. My BlueWave Router keeps
            disconnecting every 10 minutes. This is urgent because I
            work from home and need stable internet for video calls."
            """
        }
    ],
    response_format={"type": "json_object"}
)

import json

result = json.loads(response.choices[0].message.content)
print(json.dumps(result, indent=2))
```

**Output:**
```json
{
  "customer_name": "Sarah Chen",
  "product": "BlueWave Router",
  "issue": "Router keeps disconnecting every 10 minutes",
  "urgency": "high"
}
```

**Line-by-line explanation:**

- `from openai import OpenAI` imports the OpenAI client library.
- `client = OpenAI()` creates a client. It reads your API key from the `OPENAI_API_KEY` environment variable automatically.
- `model="gpt-4o-mini"` selects a fast, affordable model.
- The system message tells the LLM to always respond in JSON.
- The user message describes exactly what fields to extract and provides the text to analyze.
- `response_format={"type": "json_object"}` is the key setting. This tells the API to force JSON output. Without this, the model might still include extra text around the JSON.
- `json.loads(...)` converts the JSON string back into a Python dictionary so you can use the data in your code.

> **response_format:** A parameter in the OpenAI API that forces the model to output valid JSON. When set to `{"type": "json_object"}`, the model guarantees its response is parseable JSON. You must also mention JSON in your prompt for this to work.

---

## Defining the Exact Schema You Want

JSON mode guarantees valid JSON but does not guarantee the exact fields you want. The model might use different key names than you expect. To solve this, you specify the exact schema.

> **Schema:** A blueprint that defines the structure of your data. It specifies what fields exist, what types they are (string, number, list), and which ones are required. Think of it as a template that your data must follow.

```python
from openai import OpenAI
import json

client = OpenAI()

# Define the exact schema you want
schema_description = """
Respond with a JSON object using EXACTLY these fields:
{
    "customer_name": string,
    "product_name": string,
    "issue_summary": string (one sentence),
    "urgency_level": string (must be "low", "medium", or "high"),
    "requires_callback": boolean,
    "estimated_category": string (must be one of: "billing", "technical", "shipping", "general")
}
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": f"You extract customer support tickets. {schema_description}"
        },
        {
            "role": "user",
            "content": """Process this message:
            "My name is James Wilson. I was charged twice for my
            CloudSync Pro subscription last month. I need a refund
            as soon as possible. Please call me back at 555-0142."
            """
        }
    ],
    response_format={"type": "json_object"}
)

ticket = json.loads(response.choices[0].message.content)

# Now you can use the data reliably
print(f"Customer: {ticket['customer_name']}")
print(f"Product:  {ticket['product_name']}")
print(f"Issue:    {ticket['issue_summary']}")
print(f"Urgency:  {ticket['urgency_level']}")
print(f"Callback: {ticket['requires_callback']}")
print(f"Category: {ticket['estimated_category']}")
```

**Output:**
```
Customer: James Wilson
Product:  CloudSync Pro
Issue:    Customer was charged twice for their subscription last month and needs a refund.
Urgency:  high
Callback: True
Category: billing
```

**Line-by-line explanation:**

- `schema_description` defines the exact JSON structure you want. You list every field name, its type, and any constraints (like allowed values for urgency_level).
- The system message combines the assistant's role with the schema description.
- After getting the response, `json.loads()` converts it to a Python dictionary.
- You access individual fields using dictionary keys like `ticket['customer_name']`. This works reliably because the schema told the model exactly what keys to use.

---

## Parsing JSON Responses Safely

LLMs are not perfect. Sometimes they produce invalid JSON, especially with complex schemas. You need error handling.

```python
import json

def parse_llm_response(response_text):
    """
    Safely parse JSON from an LLM response.
    Handles common issues like extra text around JSON.
    """
    # Try direct parsing first
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON within the text
    # Sometimes models wrap JSON in markdown code blocks
    import re
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try to find JSON object pattern
    json_match = re.search(r'\{[\s\S]*\}', response_text)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass

    # Nothing worked
    raise ValueError(f"Could not parse JSON from response: {response_text[:200]}")


# Test with various response formats
test_responses = [
    '{"name": "Alice", "age": 30}',
    'Here is the result: {"name": "Bob", "age": 25}',
    '```json\n{"name": "Carol", "age": 35}\n```',
]

for response in test_responses:
    result = parse_llm_response(response)
    print(f"Parsed: {result}")
```

**Output:**
```
Parsed: {'name': 'Alice', 'age': 30}
Parsed: {'name': 'Bob', 'age': 25}
Parsed: {'name': 'Carol', 'age': 35}
```

**Line-by-line explanation:**

- The function tries three strategies to extract JSON from LLM text.
- `json.loads(response_text)` tries parsing the entire text as JSON. This works when the response is pure JSON.
- `re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', ...)` looks for JSON inside markdown code blocks. Some models wrap their JSON in triple backticks.
- `re.search(r'\{[\s\S]*\}', ...)` looks for anything that looks like a JSON object (starts with `{` and ends with `}`).
- If all three strategies fail, the function raises a clear error with the first 200 characters of the response for debugging.

---

## Introduction to Pydantic

Pydantic is a Python library that lets you define data models with automatic validation. It is the best way to ensure LLM responses have the right structure and types.

> **Pydantic:** A Python library for data validation. You define a model class with field names and types. Pydantic automatically checks that data matches your model and converts types when possible. If the data does not match, it raises a clear error.

```python
# Install: pip install pydantic
from pydantic import BaseModel, Field
from typing import List, Optional

# Define a data model
class CustomerTicket(BaseModel):
    customer_name: str = Field(description="Full name of the customer")
    email: str = Field(description="Customer email address")
    product: str = Field(description="Product name mentioned")
    issue: str = Field(description="Brief description of the issue")
    urgency: str = Field(description="low, medium, or high")
    tags: List[str] = Field(description="Relevant tags for categorization")
    order_id: Optional[str] = Field(
        default=None,
        description="Order ID if mentioned"
    )


# Pydantic validates the data automatically
valid_data = {
    "customer_name": "Alice Smith",
    "email": "alice@example.com",
    "product": "SmartWatch Pro",
    "issue": "Screen flickering after update",
    "urgency": "medium",
    "tags": ["hardware", "display", "post-update"],
    "order_id": "ORD-12345"
}

ticket = CustomerTicket(**valid_data)
print(f"Name:    {ticket.customer_name}")
print(f"Email:   {ticket.email}")
print(f"Product: {ticket.product}")
print(f"Urgency: {ticket.urgency}")
print(f"Tags:    {ticket.tags}")
print(f"Order:   {ticket.order_id}")
```

**Output:**
```
Name:    Alice Smith
Email:   alice@example.com
Product: SmartWatch Pro
Urgency: medium
Tags:    ['hardware', 'display', 'post-update']
Order:   ORD-12345
```

**Line-by-line explanation:**

- `from pydantic import BaseModel, Field` imports the base class and field descriptor.
- `class CustomerTicket(BaseModel)` defines your data model by inheriting from `BaseModel`.
- `customer_name: str` says this field must be a string. If you pass a number, Pydantic converts it to a string.
- `Field(description="...")` adds a description. This is useful for documentation and for telling LLMs what each field means.
- `List[str]` means a list of strings. Pydantic checks that every item in the list is a string.
- `Optional[str]` means the field can be a string or `None`. The `default=None` means it is not required.
- `CustomerTicket(**valid_data)` creates an instance and validates all fields. The `**` unpacks the dictionary as keyword arguments.

---

## Pydantic Validation in Action

Let us see what happens when data does not match the model.

```python
from pydantic import BaseModel, Field, ValidationError
from typing import List

class Product(BaseModel):
    name: str = Field(min_length=1)
    price: float = Field(gt=0)
    quantity: int = Field(ge=0)
    categories: List[str] = Field(min_length=1)

# Valid data works fine
try:
    product = Product(
        name="Laptop",
        price=999.99,
        quantity=50,
        categories=["electronics", "computers"]
    )
    print(f"Valid product: {product.name} - ${product.price}")
except ValidationError as e:
    print(f"Error: {e}")

print()

# Invalid data gets caught
invalid_examples = [
    {"name": "", "price": 100, "quantity": 5, "categories": ["tech"]},
    {"name": "Phone", "price": -50, "quantity": 5, "categories": ["tech"]},
    {"name": "Tablet", "price": 299, "quantity": -1, "categories": ["tech"]},
    {"name": "Mouse", "price": 25, "quantity": 10, "categories": []},
]

for i, data in enumerate(invalid_examples, 1):
    try:
        product = Product(**data)
        print(f"Example {i}: Valid")
    except ValidationError as e:
        error_msg = e.errors()[0]['msg']
        field = e.errors()[0]['loc'][0]
        print(f"Example {i}: Field '{field}' - {error_msg}")
```

**Output:**
```
Valid product: Laptop - $999.99

Example 1: Field 'name' - String should have at least 1 character
Example 2: Field 'price' - Input should be greater than 0
Example 3: Field 'quantity' - Input should be greater than or equal to 0
Example 4: Field 'categories' - List should have at least 1 item
```

**Line-by-line explanation:**

- `min_length=1` on the name field ensures the name is not empty.
- `gt=0` on price means "greater than 0." No free or negative-price products allowed.
- `ge=0` on quantity means "greater than or equal to 0." You can have zero stock but not negative.
- `min_length=1` on categories means the list must have at least one category.
- `ValidationError` is raised when data does not match. It tells you exactly which field failed and why.
- `e.errors()` returns a list of all validation errors. Each error has the field location (`loc`) and a message (`msg`).

---

## Using Pydantic with OpenAI Structured Outputs

OpenAI supports Pydantic models directly for structured outputs. This is the most reliable approach.

```python
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Optional

client = OpenAI()

# Define your output model
class MovieReview(BaseModel):
    title: str = Field(description="Movie title")
    year: int = Field(description="Release year")
    rating: float = Field(description="Rating from 0 to 10")
    genre: str = Field(description="Primary genre")
    pros: List[str] = Field(description="Positive aspects")
    cons: List[str] = Field(description="Negative aspects")
    recommended: bool = Field(description="Whether to recommend")
    summary: str = Field(description="One-sentence summary")

response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": "You analyze movie reviews and extract structured information."
        },
        {
            "role": "user",
            "content": """Analyze this review:
            "Just watched Inception again. This 2010 Nolan masterpiece
            never gets old. The visual effects are stunning and the plot
            keeps you guessing. Hans Zimmer's score is incredible. My only
            complaints are that the ending is a bit ambiguous and some
            dialogue gets drowned out by the music. Still, it's a solid
            9 out of 10. Highly recommended for any sci-fi fan!"
            """
        }
    ],
    response_format=MovieReview
)

review = response.choices[0].message.parsed
print(f"Title:       {review.title}")
print(f"Year:        {review.year}")
print(f"Rating:      {review.rating}/10")
print(f"Genre:       {review.genre}")
print(f"Pros:        {', '.join(review.pros)}")
print(f"Cons:        {', '.join(review.cons)}")
print(f"Recommended: {'Yes' if review.recommended else 'No'}")
print(f"Summary:     {review.summary}")
```

**Output:**
```
Title:       Inception
Year:        2010
Rating:      9.0/10
Genre:       Sci-Fi
Pros:        Stunning visual effects, Engaging and complex plot, Incredible Hans Zimmer score
Cons:        Ambiguous ending, Dialogue sometimes drowned out by music
Recommended: Yes
Summary:     A visually stunning sci-fi masterpiece with a complex plot and incredible score that remains highly rewatchable.
```

**Line-by-line explanation:**

- `client.beta.chat.completions.parse()` is a special method that understands Pydantic models. It is in `beta` because it is a newer feature.
- `response_format=MovieReview` passes your Pydantic model directly. The API converts it to a JSON schema automatically and forces the model to follow it exactly.
- `response.choices[0].message.parsed` returns a Pydantic `MovieReview` object, not raw JSON text. You access fields as attributes like `review.title` instead of dictionary keys.
- The model is guaranteed to produce all required fields with the correct types. No parsing or validation needed on your side.

```
+------------------------------------------------------------------+
|              HOW PYDANTIC + OPENAI WORKS                          |
|                                                                   |
|  1. You define:     class MovieReview(BaseModel):                 |
|                         title: str                                |
|                         year: int                                 |
|                         ...                                       |
|                                                                   |
|  2. API converts:   Pydantic model -> JSON Schema                 |
|                     { "type": "object",                           |
|                       "properties": { "title": {...} } }          |
|                                                                   |
|  3. LLM follows:    Schema constrains token generation            |
|                     Model MUST produce valid JSON                 |
|                                                                   |
|  4. API returns:    JSON -> Pydantic object                       |
|                     review.title, review.year, etc.               |
|                                                                   |
|  Result: Type-safe, validated data. Every time.                   |
+------------------------------------------------------------------+
```

---

## Extracting Multiple Items

Often you need to extract a list of items from text, not just a single object.

```python
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List

client = OpenAI()

class Person(BaseModel):
    name: str = Field(description="Person's full name")
    role: str = Field(description="Their role or title")
    company: str = Field(description="Company they work for")

class ExtractionResult(BaseModel):
    people: List[Person] = Field(description="All people mentioned")
    companies: List[str] = Field(description="All companies mentioned")
    key_topic: str = Field(description="Main topic of the text")

response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": "Extract structured information from business text."
        },
        {
            "role": "user",
            "content": """Extract information from this article:
            "At yesterday's tech summit, Maria Garcia, CTO of DataFlow Inc.,
            announced a partnership with NeuralTech. James Park, CEO of
            NeuralTech, said the deal would combine DataFlow's data pipeline
            technology with NeuralTech's AI models. The partnership was
            also praised by Lisa Wang, VP of Engineering at CloudBase,
            who plans to integrate both platforms."
            """
        }
    ],
    response_format=ExtractionResult
)

result = response.choices[0].message.parsed

print(f"Topic: {result.key_topic}\n")

print("People mentioned:")
for person in result.people:
    print(f"  - {person.name}, {person.role} at {person.company}")

print(f"\nCompanies: {', '.join(result.companies)}")
```

**Output:**
```
Topic: Tech partnership announcement between DataFlow Inc. and NeuralTech

People mentioned:
  - Maria Garcia, CTO at DataFlow Inc.
  - James Park, CEO at NeuralTech
  - Lisa Wang, VP of Engineering at CloudBase

Companies: DataFlow Inc., NeuralTech, CloudBase
```

**Line-by-line explanation:**

- `class Person(BaseModel)` defines a model for a single person with name, role, and company.
- `class ExtractionResult(BaseModel)` defines the overall result, which contains a list of `Person` objects, a list of company names, and a key topic.
- `List[Person]` tells Pydantic to expect a list where every item is a valid `Person` object. This is called nesting models.
- The LLM extracts all people and companies from the text and formats them according to your exact schema.
- You iterate over `result.people` just like any Python list, and each item is a `Person` object with `.name`, `.role`, and `.company` attributes.

---

## Building a Reliable Extraction Pipeline

Let us put everything together into a reusable extraction pipeline.

```python
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional
import json

client = OpenAI()

# Step 1: Define your data model
class InvoiceItem(BaseModel):
    description: str = Field(description="Item description")
    quantity: int = Field(ge=1, description="Number of items")
    unit_price: float = Field(gt=0, description="Price per unit")
    total: float = Field(gt=0, description="Line total")

class Invoice(BaseModel):
    invoice_number: str = Field(description="Invoice ID or number")
    vendor_name: str = Field(description="Company that sent the invoice")
    date: str = Field(description="Invoice date in YYYY-MM-DD format")
    items: List[InvoiceItem] = Field(description="Line items on the invoice")
    subtotal: float = Field(ge=0, description="Sum before tax")
    tax: float = Field(ge=0, description="Tax amount")
    total: float = Field(gt=0, description="Final total amount")
    currency: str = Field(description="Currency code like USD, EUR")

# Step 2: Create the extraction function
def extract_invoice(text: str, max_retries: int = 3) -> Optional[Invoice]:
    """
    Extract invoice data from text with retries.
    Returns an Invoice object or None if extraction fails.
    """
    for attempt in range(max_retries):
        try:
            response = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You extract invoice information from text. "
                                   "Be precise with numbers and dates."
                    },
                    {
                        "role": "user",
                        "content": f"Extract the invoice data:\n\n{text}"
                    }
                ],
                response_format=Invoice
            )

            invoice = response.choices[0].message.parsed

            # Additional business logic validation
            calculated_subtotal = sum(
                item.total for item in invoice.items
            )
            if abs(calculated_subtotal - invoice.subtotal) > 0.01:
                print(f"Warning: Subtotal mismatch. "
                      f"Items sum to {calculated_subtotal}, "
                      f"but subtotal says {invoice.subtotal}")

            return invoice

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                print("All retries exhausted")
                return None

    return None

# Step 3: Use it
invoice_text = """
INVOICE #INV-2024-0892

From: TechSupply Corp
Date: March 15, 2024

Items:
- 5x USB-C Cables @ $12.99 each = $64.95
- 2x Wireless Mouse @ $29.99 each = $59.98
- 10x Screen Protectors @ $8.50 each = $85.00

Subtotal: $209.93
Tax (8%): $16.79
Total: $226.72
Currency: USD
"""

invoice = extract_invoice(invoice_text)

if invoice:
    print(f"Invoice:  {invoice.invoice_number}")
    print(f"Vendor:   {invoice.vendor_name}")
    print(f"Date:     {invoice.date}")
    print(f"\nItems:")
    for item in invoice.items:
        print(f"  {item.quantity}x {item.description} "
              f"@ ${item.unit_price:.2f} = ${item.total:.2f}")
    print(f"\nSubtotal: ${invoice.subtotal:.2f}")
    print(f"Tax:      ${invoice.tax:.2f}")
    print(f"Total:    ${invoice.total:.2f} {invoice.currency}")
else:
    print("Failed to extract invoice data")
```

**Output:**
```
Invoice:  INV-2024-0892
Vendor:   TechSupply Corp
Date:     2024-03-15

Items:
  5x USB-C Cables @ $12.99 = $64.95
  2x Wireless Mouse @ $29.99 = $59.98
  10x Screen Protectors @ $8.50 = $85.00

Subtotal: $209.93
Tax:      $16.79
Total:    $226.72 USD
```

**Line-by-line explanation:**

- `InvoiceItem` defines a single line item with quantity, unit price, and total. The `ge=1` ensures quantity is at least 1.
- `Invoice` contains the full invoice data including a list of `InvoiceItem` objects.
- `extract_invoice()` wraps the API call with retry logic. If the first attempt fails (network error, invalid response), it tries again up to `max_retries` times.
- The function includes business logic validation. It checks that the sum of individual items matches the stated subtotal. This catches cases where the LLM makes arithmetic mistakes.
- `abs(calculated_subtotal - invoice.subtotal) > 0.01` uses a small tolerance (0.01) for floating-point comparison. Comparing floats with `==` can fail due to tiny rounding differences.

---

## Using Structured Outputs without OpenAI

If you use other LLM providers or local models, you can still get structured outputs by combining careful prompting with Pydantic validation.

```python
from pydantic import BaseModel, Field, ValidationError
from typing import List
import json

class SentimentResult(BaseModel):
    text: str = Field(description="The analyzed text")
    sentiment: str = Field(description="positive, negative, or neutral")
    confidence: float = Field(ge=0, le=1, description="Confidence 0 to 1")
    key_phrases: List[str] = Field(description="Important phrases")

def get_schema_prompt(model_class):
    """
    Generate a prompt section describing the expected JSON schema.
    Works with any LLM provider.
    """
    schema = model_class.model_json_schema()

    # Build a simple description
    lines = ["Respond with a JSON object with these exact fields:"]

    properties = schema.get("properties", {})
    required = schema.get("required", [])

    for field_name, field_info in properties.items():
        field_type = field_info.get("type", "string")
        description = field_info.get("description", "")
        is_required = field_name in required
        req_label = "required" if is_required else "optional"
        lines.append(f'  - "{field_name}" ({field_type}, {req_label}): {description}')

    return "\n".join(lines)

# Generate the prompt
schema_prompt = get_schema_prompt(SentimentResult)
print("Schema prompt for the LLM:")
print(schema_prompt)
print()

# Simulate an LLM response
simulated_response = '''
{
    "text": "The new update is fantastic! Everything runs smoothly now.",
    "sentiment": "positive",
    "confidence": 0.95,
    "key_phrases": ["fantastic", "runs smoothly"]
}
'''

# Parse and validate
try:
    data = json.loads(simulated_response)
    result = SentimentResult(**data)
    print(f"Sentiment: {result.sentiment}")
    print(f"Confidence: {result.confidence}")
    print(f"Key phrases: {result.key_phrases}")
except json.JSONDecodeError as e:
    print(f"Invalid JSON: {e}")
except ValidationError as e:
    print(f"Validation failed: {e}")
```

**Output:**
```
Schema prompt for the LLM:
Respond with a JSON object with these exact fields:
  - "text" (string, required): The analyzed text
  - "sentiment" (string, required): positive, negative, or neutral
  - "confidence" (number, required): Confidence 0 to 1
  - "key_phrases" (array, required): Important phrases

Sentiment: positive
Confidence: 0.95
Key phrases: ['fantastic', 'runs smoothly']
```

**Line-by-line explanation:**

- `model_class.model_json_schema()` generates a JSON Schema dictionary from your Pydantic model. This is a standard format that describes data structure.
- `get_schema_prompt()` converts the schema into human-readable instructions that any LLM can follow.
- This approach works with any LLM provider (Anthropic, Google, local models). You include the schema instructions in your prompt and then validate the response with Pydantic.
- The two-step validation (first `json.loads()`, then Pydantic) catches both JSON syntax errors and data validation errors separately.

---

## Enum Fields for Controlled Values

When a field should only accept specific values, use Python enums with Pydantic.

> **Enum (Enumeration):** A set of named constants. Instead of accepting any string, an enum field only accepts values from a predefined list. This prevents typos and invalid values.

```python
from pydantic import BaseModel, Field
from enum import Enum
from typing import List

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Category(str, Enum):
    BUG = "bug"
    FEATURE = "feature"
    IMPROVEMENT = "improvement"
    DOCUMENTATION = "documentation"

class BugReport(BaseModel):
    title: str = Field(description="Short description of the issue")
    priority: Priority = Field(description="Issue priority level")
    category: Category = Field(description="Type of issue")
    steps_to_reproduce: List[str] = Field(
        description="Steps to reproduce the issue"
    )
    expected_behavior: str = Field(description="What should happen")
    actual_behavior: str = Field(description="What actually happens")

# Valid data
report = BugReport(
    title="Login button not responding",
    priority="high",
    category="bug",
    steps_to_reproduce=[
        "Open the app",
        "Enter username and password",
        "Click the Login button",
        "Nothing happens"
    ],
    expected_behavior="User should be logged in and redirected to dashboard",
    actual_behavior="Button click has no effect, no error message shown"
)

print(f"Title:    {report.title}")
print(f"Priority: {report.priority.value}")
print(f"Category: {report.category.value}")
print(f"Steps:    {len(report.steps_to_reproduce)} steps listed")

# Invalid priority gets caught
try:
    bad_report = BugReport(
        title="Test",
        priority="super-urgent",
        category="bug",
        steps_to_reproduce=["step 1"],
        expected_behavior="works",
        actual_behavior="broken"
    )
except Exception as e:
    print(f"\nInvalid priority caught: 'super-urgent' is not allowed")
    print(f"Allowed values: {[p.value for p in Priority]}")
```

**Output:**
```
Title:    Login button not responding
Priority: high
Category: bug
Steps:    4 steps listed

Invalid priority caught: 'super-urgent' is not allowed
Allowed values: ['low', 'medium', 'high', 'critical']
```

---

## Common Mistakes

1. **Forgetting to mention JSON in the prompt.** When using `response_format={"type": "json_object"}`, you must also tell the model to respond in JSON within your prompt. The API requires both.

2. **Not handling parsing errors.** Even with JSON mode, network errors or rate limits can cause failures. Always wrap parsing in try-except blocks.

3. **Making schemas too complex.** Very deeply nested schemas with many optional fields confuse the model. Keep schemas flat and simple when possible.

4. **Not validating beyond types.** Pydantic checks types, but you still need business logic validation. A field might be the right type (a number) but the wrong value (negative price).

5. **Using single quotes in JSON.** JSON requires double quotes. Python dictionaries can use either, but JSON strings cannot. If you build JSON manually, use `json.dumps()` instead of string formatting.

---

## Best Practices

1. **Use Pydantic models for all structured outputs.** They provide both documentation and validation in one place.

2. **Add Field descriptions.** Descriptions help the LLM understand what each field should contain. Better descriptions lead to better extraction.

3. **Use enums for categorical fields.** Instead of accepting any string for fields like "status" or "priority," define the allowed values explicitly.

4. **Implement retry logic.** API calls can fail. Always have a retry mechanism for production code.

5. **Validate business logic separately.** After Pydantic validates the structure, add your own checks. Does the total equal the sum of line items? Is the date in the past?

6. **Keep schemas focused.** Extract one type of information per call rather than trying to extract everything at once. Multiple focused calls are more reliable than one complex call.

---

## Quick Summary

Structured outputs transform LLMs from unpredictable text generators into reliable data extraction tools. JSON mode forces the model to produce valid JSON. Pydantic models define the exact schema and validate every field automatically. Together, they let you build production applications that depend on LLM outputs without worrying about format surprises.

---

## Key Points

- **JSON mode** forces the LLM to output valid JSON instead of free-form text
- **Schemas** define the exact fields, types, and constraints you expect
- **Pydantic models** provide automatic validation with clear error messages
- **OpenAI's parse method** accepts Pydantic models directly for the most reliable approach
- **Retry logic** handles transient failures gracefully
- **Enums** restrict fields to predefined values, preventing invalid data
- **Business logic validation** catches errors that type checking misses

---

## Practice Questions

1. What is the difference between `response_format={"type": "json_object"}` and using `client.beta.chat.completions.parse()` with a Pydantic model? When would you use each one?

2. You have a Pydantic model with a field `age: int = Field(ge=0, le=150)`. What does this validate, and what happens if you pass `age=-5`?

3. Why is it important to include field descriptions in your Pydantic models when using them with LLMs?

4. Your extraction pipeline sometimes gets a JSON response wrapped in markdown code blocks (triple backticks). How would you handle this in your parsing code?

5. When would you choose to use enums instead of plain strings for a field in your Pydantic model?

---

## Exercises

**Exercise 1: Recipe Extractor**

Create a Pydantic model for a recipe with fields for name, prep time, cook time, servings, ingredients (list of objects with name, amount, and unit), and steps (list of strings). Write a function that takes recipe text and extracts structured data using the OpenAI API (or simulate the response for practice).

**Exercise 2: Email Classifier**

Build an email classification system using Pydantic models. Define a model with fields for sender, subject, category (use an enum with values like "work," "personal," "spam," "newsletter"), urgency, summary, and action_required (boolean). Process at least 3 sample emails and print the structured results.

**Exercise 3: Error Report Aggregator**

Create a pipeline that takes multiple error log entries as text and extracts a list of structured error reports. Each report should have: timestamp, error type, affected service, error message, and suggested fix. Use Pydantic's list validation to ensure all entries are properly structured.

---

## What Is Next?

Now that you can get structured, reliable outputs from LLMs, the next step is to make your prompts themselves more structured and measurable. In Chapter 12, you will learn how to create reusable prompt templates, measure prompt quality with evaluation metrics, and systematically improve your prompts through A/B testing. This moves you from crafting prompts by intuition to engineering them with data.
