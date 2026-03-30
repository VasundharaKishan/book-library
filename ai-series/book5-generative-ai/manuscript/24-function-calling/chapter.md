# Chapter 24: Function Calling and Tool Use

## What You Will Learn

In this chapter, you will learn:

- How LLMs use external tools through function calling
- How to define tools using JSON schema descriptions
- How the function calling flow works from request to response
- How to parse LLM tool calls and execute the corresponding functions
- How to return tool results back to the LLM for final answers
- How to build a complete tool-use system with a calculator and weather tool

## Why This Chapter Matters

In Chapter 23, you learned that agents use tools to interact with the real world. But how does an LLM -- which only generates text -- actually "call" a function? The LLM cannot run Python code or make API calls by itself. It can only output text.

The trick is elegant: the LLM outputs structured text (JSON) that describes which function to call and with what arguments. Your code then parses this JSON, calls the actual function, and feeds the result back to the LLM.

Think of it like a drive-through restaurant. You (the code) are the driver. The LLM is a passenger who cannot drive. The passenger tells you what to order (generates a tool call), you place the order at the window (execute the function), and you hand the food back to the passenger (return the result). The passenger never touches the window directly.

Understanding function calling is the foundation for building every AI agent, from simple chatbots with tools to complex autonomous systems.

---

## 24.1 How Function Calling Works

### The Big Picture

```
+---------------------------------------------------------------+
|              FUNCTION CALLING FLOW                            |
+---------------------------------------------------------------+
|                                                               |
|  Step 1: You send a message + tool definitions to the LLM    |
|                                                               |
|  User: "What is the weather in London?"                       |
|  Tools: [get_weather(city: str) -> str]                       |
|         |                                                     |
|         v                                                     |
|  Step 2: LLM generates a tool call (NOT the answer)          |
|                                                               |
|  LLM Response: {                                              |
|    "tool": "get_weather",                                     |
|    "arguments": {"city": "London"}                            |
|  }                                                            |
|         |                                                     |
|         v                                                     |
|  Step 3: Your code executes the function                      |
|                                                               |
|  result = get_weather("London")                               |
|  result = "London: 58F, Rainy"                                |
|         |                                                     |
|         v                                                     |
|  Step 4: You send the result back to the LLM                 |
|                                                               |
|  Tool Result: "London: 58F, Rainy"                            |
|         |                                                     |
|         v                                                     |
|  Step 5: LLM generates the final answer using the result     |
|                                                               |
|  LLM: "The weather in London is currently 58F and rainy."    |
|                                                               |
+---------------------------------------------------------------+
```

```python
# Demonstrating the function calling flow step by step

import json

# Step 1: Define the available tools
tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a city",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The name of the city"
                }
            },
            "required": ["city"]
        }
    }
]

# Step 2: The LLM generates a tool call (simulated)
llm_response = {
    "tool_call": {
        "name": "get_weather",
        "arguments": {"city": "London"}
    }
}

# Step 3: Parse and execute the tool call
tool_name = llm_response["tool_call"]["name"]
tool_args = llm_response["tool_call"]["arguments"]
print(f"Step 2 - LLM wants to call: {tool_name}({tool_args})")

# The actual function
def get_weather(city):
    """Simulated weather API."""
    weather_data = {
        "London": "58F, Rainy",
        "New York": "72F, Sunny",
        "Tokyo": "68F, Cloudy",
    }
    return weather_data.get(city, "Weather data not available")

# Execute the function
result = get_weather(**tool_args)
print(f"Step 3 - Function result: {result}")

# Step 4: Send result back to LLM (simulated)
print(f"Step 4 - Sending result back to LLM")

# Step 5: LLM generates final answer (simulated)
final_answer = f"The weather in {tool_args['city']} is currently {result}."
print(f"Step 5 - Final answer: {final_answer}")
```

**Expected output:**

```
Step 2 - LLM wants to call: get_weather({'city': 'London'})
Step 3 - Function result: 58F, Rainy
Step 4 - Sending result back to LLM
Step 5 - Final answer: The weather in London is currently 58F, Rainy.
```

**Line-by-line explanation:**

- `tools` -- A list of tool definitions in JSON format. Each tool has a name, description, and parameter schema
- `llm_response` -- What the LLM returns when it decides to use a tool. Instead of generating a text answer, it generates a structured tool call
- `tool_name` and `tool_args` -- We parse the LLM's response to extract which function to call and with what arguments
- `get_weather(**tool_args)` -- The `**` operator unpacks the dictionary into keyword arguments. So `get_weather(**{"city": "London"})` becomes `get_weather(city="London")`
- The final answer is what the LLM generates after seeing the tool result

---

## 24.2 Defining Tools with JSON Schema

### What Is JSON Schema?

JSON Schema is a standard way to describe the structure of data. When we define tools for an LLM, we use JSON Schema to describe what arguments each tool accepts:

```
+---------------------------------------------------------------+
|              JSON SCHEMA BASICS                               |
+---------------------------------------------------------------+
|                                                               |
|  Think of JSON Schema as a form template:                     |
|                                                               |
|  Form: "Pizza Order"                                          |
|  Fields:                                                      |
|    - size (required): small, medium, or large                 |
|    - toppings (optional): list of strings                     |
|    - delivery (required): true or false                       |
|                                                               |
|  JSON Schema:                                                 |
|  {                                                            |
|    "type": "object",                                          |
|    "properties": {                                            |
|      "size": {"type": "string", "enum": ["small","med","lg"]},|
|      "toppings": {"type": "array", "items": {"type":"string"}|
|      "delivery": {"type": "boolean"}                          |
|    },                                                         |
|    "required": ["size", "delivery"]                           |
|  }                                                            |
|                                                               |
+---------------------------------------------------------------+
```

### Defining Multiple Tools

```python
import json

# Define a set of tools using JSON Schema

tools_definition = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a specific city. Returns temperature, conditions, and humidity.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The name of the city (e.g., 'London', 'New York')"
                    },
                    "units": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature units. Defaults to fahrenheit."
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Perform a mathematical calculation. Supports basic arithmetic, percentages, and common math functions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate (e.g., '2 + 2', '15% of 200', 'sqrt(144)')"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for current information. Use this when you need up-to-date information that you do not have in your training data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return (1-10). Defaults to 3."
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# Display the tools
print("Defined Tools:")
print("=" * 60)
for tool in tools_definition:
    func = tool["function"]
    params = func["parameters"]["properties"]
    required = func["parameters"].get("required", [])

    print(f"\n  {func['name']}:")
    print(f"    Description: {func['description'][:60]}...")
    print(f"    Parameters:")
    for param_name, param_info in params.items():
        req = "(required)" if param_name in required else "(optional)"
        print(f"      - {param_name}: {param_info['type']} {req}")
        print(f"        {param_info['description'][:50]}")
```

**Expected output:**

```
Defined Tools:
============================================================

  get_weather:
    Description: Get the current weather for a specific city. Returns te...
    Parameters:
      - city: string (required)
        The name of the city (e.g., 'London', 'New Yo
      - units: string (optional)
        Temperature units. Defaults to fahrenheit.

  calculator:
    Description: Perform a mathematical calculation. Supports basic arit...
    Parameters:
      - expression: string (required)
        The mathematical expression to evaluate (e.g.

  search_web:
    Description: Search the web for current information. Use this when y...
    Parameters:
      - query: string (required)
        The search query
      - num_results: integer (optional)
        Number of results to return (1-10). Defaults
```

### Best Practices for Tool Descriptions

```
+---------------------------------------------------------------+
|              WRITING GOOD TOOL DESCRIPTIONS                   |
+---------------------------------------------------------------+
|                                                               |
|  BAD description:                                             |
|  "Gets weather"                                               |
|                                                               |
|  GOOD description:                                            |
|  "Get the current weather for a specific city.                |
|   Returns temperature in Fahrenheit, weather conditions       |
|   (sunny, cloudy, rainy), and humidity percentage.            |
|   Use this when the user asks about weather or                |
|   temperature in a specific location."                        |
|                                                               |
|  Rules:                                                       |
|  1. Say WHAT the tool does                                    |
|  2. Say WHAT it returns                                       |
|  3. Say WHEN to use it                                        |
|  4. Give examples of input values                             |
|  5. Mention any limitations                                   |
|                                                               |
+---------------------------------------------------------------+
```

---

## 24.3 Implementing the Tool Functions

### Building Real Tool Functions

```python
import math
import json

# Tool 1: Weather lookup
def get_weather(city, units="fahrenheit"):
    """
    Get the current weather for a city.
    In production, this would call a real weather API.
    """
    # Simulated weather database
    weather_db = {
        "London": {"temp_f": 58, "condition": "Rainy", "humidity": 82},
        "New York": {"temp_f": 72, "condition": "Sunny", "humidity": 45},
        "Tokyo": {"temp_f": 68, "condition": "Cloudy", "humidity": 65},
        "Sydney": {"temp_f": 77, "condition": "Sunny", "humidity": 55},
        "Paris": {"temp_f": 63, "condition": "Partly Cloudy", "humidity": 60},
    }

    data = weather_db.get(city)
    if not data:
        return json.dumps({"error": f"Weather data not available for {city}"})

    temp = data["temp_f"]
    if units == "celsius":
        temp = round((temp - 32) * 5 / 9, 1)
        unit_label = "C"
    else:
        unit_label = "F"

    result = {
        "city": city,
        "temperature": f"{temp}{unit_label}",
        "condition": data["condition"],
        "humidity": f"{data['humidity']}%"
    }
    return json.dumps(result)


# Tool 2: Calculator
def calculator(expression):
    """
    Evaluate a mathematical expression safely.
    Supports: +, -, *, /, **, sqrt, sin, cos, tan, log, pi, e
    """
    # Define safe functions and constants
    safe_dict = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log10": math.log10,
        "pi": math.pi,
        "e": math.e,
        "abs": abs,
        "round": round,
    }

    try:
        # Replace common words with math operations
        expr = expression.replace("^", "**")
        result = eval(expr, {"__builtins__": {}}, safe_dict)
        return json.dumps({"expression": expression, "result": result})
    except Exception as e:
        return json.dumps({"error": f"Could not evaluate: {expression}. Error: {str(e)}"})


# Tool 3: Web search (simulated)
def search_web(query, num_results=3):
    """
    Search the web for information.
    In production, this would call a real search API.
    """
    # Simulated search results
    mock_results = {
        "Python latest version": [
            {"title": "Python 3.13 Released", "snippet": "Python 3.13 was released in October 2024 with performance improvements."},
            {"title": "Download Python", "snippet": "The latest stable version is Python 3.13.0."},
        ],
        "default": [
            {"title": f"Search result for: {query}", "snippet": f"Information about {query}."},
        ]
    }

    results = mock_results.get(query, mock_results["default"])[:num_results]
    return json.dumps({"query": query, "results": results})


# Test each tool
print("=== Testing get_weather ===")
print(get_weather("London"))
print(get_weather("Tokyo", units="celsius"))

print("\n=== Testing calculator ===")
print(calculator("2 + 2"))
print(calculator("sqrt(144)"))
print(calculator("15 * 234.50 / 100"))

print("\n=== Testing search_web ===")
print(search_web("Python latest version"))
```

**Expected output:**

```
=== Testing get_weather ===
{"city": "London", "temperature": "58F", "condition": "Rainy", "humidity": "82%"}
{"city": "Tokyo", "temperature": "20.0C", "condition": "Cloudy", "humidity": "65%"}

=== Testing calculator ===
{"expression": "2 + 2", "result": 4}
{"expression": "sqrt(144)", "result": 12.0}
{"expression": "15 * 234.50 / 100", "result": 35.175}

=== Testing search_web ===
{"query": "Python latest version", "results": [{"title": "Python 3.13 Released", "snippet": "Python 3.13 was released in October 2024 with performance improvements."}, {"title": "Download Python", "snippet": "The latest stable version is Python 3.13.0."}]}
```

---

## 24.4 Parsing LLM Tool Calls

### Extracting Tool Calls from LLM Output

When an LLM decides to use a tool, it returns a structured response. You need to parse this response and execute the right function:

```python
import json

# Registry of available tools
TOOL_REGISTRY = {
    "get_weather": get_weather,
    "calculator": calculator,
    "search_web": search_web,
}

def parse_and_execute_tool_call(tool_call):
    """
    Parse a tool call from the LLM and execute the corresponding function.

    Args:
        tool_call: A dictionary with 'name' and 'arguments' keys

    Returns:
        The result of the tool execution
    """
    tool_name = tool_call["name"]
    tool_args = tool_call["arguments"]

    # Validate tool exists
    if tool_name not in TOOL_REGISTRY:
        return json.dumps({
            "error": f"Unknown tool: {tool_name}. Available tools: {list(TOOL_REGISTRY.keys())}"
        })

    # Parse arguments if they are a string
    if isinstance(tool_args, str):
        try:
            tool_args = json.loads(tool_args)
        except json.JSONDecodeError:
            return json.dumps({"error": f"Invalid arguments format: {tool_args}"})

    # Execute the tool
    try:
        func = TOOL_REGISTRY[tool_name]
        result = func(**tool_args)
        return result
    except TypeError as e:
        return json.dumps({"error": f"Wrong arguments for {tool_name}: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"Tool execution failed: {str(e)}"})


# Test with different tool calls
test_calls = [
    {"name": "get_weather", "arguments": {"city": "Paris"}},
    {"name": "calculator", "arguments": {"expression": "25 * 4 + 10"}},
    {"name": "search_web", "arguments": {"query": "Python latest version", "num_results": 2}},
    {"name": "unknown_tool", "arguments": {}},  # This should return an error
]

print("Executing tool calls:")
print("=" * 60)
for call in test_calls:
    print(f"\nTool: {call['name']}")
    print(f"Args: {call['arguments']}")
    result = parse_and_execute_tool_call(call)
    print(f"Result: {result}")
```

**Expected output:**

```
Executing tool calls:
============================================================

Tool: get_weather
Args: {'city': 'Paris'}
Result: {"city": "Paris", "temperature": "63F", "condition": "Partly Cloudy", "humidity": "60%"}

Tool: calculator
Args: {'expression': '25 * 4 + 10'}
Result: {"expression": "25 * 4 + 10", "result": 110}

Tool: search_web
Args: {'query': 'Python latest version', 'num_results': 2}
Result: {"query": "Python latest version", "results": [{"title": "Python 3.13 Released", "snippet": "Python 3.13 was released in October 2024 with performance improvements."}, {"title": "Download Python", "snippet": "The latest stable version is Python 3.13.0."}]}

Tool: unknown_tool
Args: {}
Result: {"error": "Unknown tool: unknown_tool. Available tools: ['get_weather', 'calculator', 'search_web']"}
```

**Line-by-line explanation:**

- `TOOL_REGISTRY` -- A dictionary mapping tool names to their Python functions. This is how we connect the LLM's text output to actual code
- `parse_and_execute_tool_call()` -- The main function that handles the entire tool execution pipeline
- We first validate that the tool exists, then parse the arguments, then call the function
- Error handling is crucial: we catch invalid tool names, bad arguments, and execution errors
- The `**tool_args` syntax unpacks the dictionary into keyword arguments

---

## 24.5 Using OpenAI's Function Calling API

### The Standard Approach

OpenAI (and many other providers) have built function calling directly into their API:

```python
# Using OpenAI's function calling API
# Note: Requires an OpenAI API key

from openai import OpenAI

# Initialize the client
# client = OpenAI(api_key="your-api-key-here")
# For demonstration, we will simulate the API calls

# Define tools in OpenAI's format
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a math expression",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression to evaluate"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]

# The API call would look like this:
"""
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "What is 15% of the temperature in London?"}
    ],
    tools=tools,
    tool_choice="auto",  # Let the model decide when to use tools
)
"""

# Simulated API response when the model wants to use a tool
simulated_response = {
    "choices": [{
        "message": {
            "role": "assistant",
            "content": None,  # No text content when making a tool call
            "tool_calls": [{
                "id": "call_abc123",
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "arguments": '{"city": "London"}'
                }
            }]
        },
        "finish_reason": "tool_calls"
    }]
}

print("Simulated API Response:")
print(json.dumps(simulated_response, indent=2))

# Parse the tool call
tool_call = simulated_response["choices"][0]["message"]["tool_calls"][0]
func_name = tool_call["function"]["name"]
func_args = json.loads(tool_call["function"]["arguments"])
print(f"\nParsed tool call: {func_name}({func_args})")

# Execute the tool
result = TOOL_REGISTRY[func_name](**func_args)
print(f"Tool result: {result}")
```

**Expected output:**

```
Simulated API Response:
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": null,
        "tool_calls": [
          {
            "id": "call_abc123",
            "type": "function",
            "function": {
              "name": "get_weather",
              "arguments": "{\"city\": \"London\"}"
            }
          }
        ]
      },
      "finish_reason": "tool_calls"
    }
  ]
}

Parsed tool call: get_weather({'city': 'London'})
Tool result: {"city": "London", "temperature": "58F", "condition": "Rainy", "humidity": "82%"}
```

---

## 24.6 Complete Tool-Use Pipeline

### Building a Full Conversational Tool-Use System

```python
import json

class ToolUseChat:
    """
    A complete tool-use chat system.
    Simulates the LLM with rule-based logic for demonstration.
    In production, replace simulate_llm() with actual API calls.
    """

    def __init__(self):
        self.tools = {
            "get_weather": get_weather,
            "calculator": calculator,
            "search_web": search_web,
        }
        self.conversation_history = []

    def simulate_llm(self, messages):
        """
        Simulate LLM behavior.
        In production, this would be an API call to OpenAI, Anthropic, etc.
        """
        last_message = messages[-1]["content"].lower()

        # Check if this is a tool result being fed back
        if messages[-1]["role"] == "tool":
            # Generate final answer using the tool result
            tool_result = json.loads(messages[-1]["content"])
            if "temperature" in str(tool_result):
                return {
                    "type": "text",
                    "content": f"The weather in {tool_result.get('city', 'the city')} is {tool_result.get('temperature', 'unknown')} and {tool_result.get('condition', 'unknown')} with {tool_result.get('humidity', 'unknown')} humidity."
                }
            elif "result" in tool_result:
                return {
                    "type": "text",
                    "content": f"The answer is {tool_result['result']}."
                }
            else:
                return {
                    "type": "text",
                    "content": f"Here is what I found: {json.dumps(tool_result, indent=2)}"
                }

        # Determine if a tool should be called
        if "weather" in last_message:
            # Extract city name (simplified)
            cities = ["london", "new york", "tokyo", "sydney", "paris"]
            city = next((c.title() for c in cities if c in last_message), "New York")
            return {
                "type": "tool_call",
                "name": "get_weather",
                "arguments": {"city": city}
            }
        elif any(op in last_message for op in ["calculate", "what is", "how much", "+", "-", "*", "/"]):
            # Try to extract a math expression
            import re
            # Simple pattern matching for math expressions
            numbers = re.findall(r'[\d.]+', last_message)
            if len(numbers) >= 2:
                expr = f"{numbers[0]} * {numbers[1]}" if "times" in last_message or "*" in last_message else f"{numbers[0]} + {numbers[1]}"
                return {
                    "type": "tool_call",
                    "name": "calculator",
                    "arguments": {"expression": expr}
                }
            return {"type": "text", "content": "Could you provide a specific math expression?"}
        elif "search" in last_message or "find" in last_message:
            query = last_message.replace("search for", "").replace("find", "").strip()
            return {
                "type": "tool_call",
                "name": "search_web",
                "arguments": {"query": query}
            }
        else:
            return {
                "type": "text",
                "content": "I can help you with weather, calculations, and web searches. What would you like to know?"
            }

    def chat(self, user_message):
        """Process a user message, potentially using tools."""
        print(f"\nUser: {user_message}")
        print("-" * 50)

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Get LLM response
        llm_response = self.simulate_llm(self.conversation_history)

        if llm_response["type"] == "tool_call":
            # LLM wants to use a tool
            tool_name = llm_response["name"]
            tool_args = llm_response["arguments"]
            print(f"  [Tool Call] {tool_name}({json.dumps(tool_args)})")

            # Execute the tool
            tool_result = self.tools[tool_name](**tool_args)
            print(f"  [Tool Result] {tool_result}")

            # Add tool call and result to history
            self.conversation_history.append({
                "role": "assistant",
                "content": None,
                "tool_call": {"name": tool_name, "arguments": tool_args}
            })
            self.conversation_history.append({
                "role": "tool",
                "content": tool_result
            })

            # Get final answer from LLM
            final_response = self.simulate_llm(self.conversation_history)
            answer = final_response["content"]
        else:
            answer = llm_response["content"]

        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": answer
        })

        print(f"  [Answer] {answer}")
        return answer


# Run the complete system
chat = ToolUseChat()

# Test different types of queries
chat.chat("What is the weather in Tokyo?")
chat.chat("What is the weather in London?")
chat.chat("Search for Python latest version")
```

**Expected output:**

```
User: What is the weather in Tokyo?
--------------------------------------------------
  [Tool Call] get_weather({"city": "Tokyo"})
  [Tool Result] {"city": "Tokyo", "temperature": "68F", "condition": "Cloudy", "humidity": "65%"}
  [Answer] The weather in Tokyo is 68F and Cloudy with 65% humidity.

User: What is the weather in London?
--------------------------------------------------
  [Tool Call] get_weather({"city": "London"})
  [Tool Result] {"city": "London", "temperature": "58F", "condition": "Rainy", "humidity": "82%"}
  [Answer] The weather in London is 58F and Rainy with 82% humidity.

User: Search for Python latest version
--------------------------------------------------
  [Tool Call] search_web({"query": " python latest version"})
  [Tool Result] {"query": " python latest version", "results": [{"title": "Search result for:  python latest version", "snippet": "Information about  python latest version."}]}
  [Answer] Here is what I found: ...
```

---

## 24.7 Handling Multiple Tool Calls

### When One Tool Is Not Enough

Sometimes the LLM needs to call multiple tools to answer a question:

```python
# Demonstrating multiple sequential tool calls

def handle_multi_step_query():
    """
    Handle a query that requires multiple tool calls.
    Example: "What is 15% of the temperature in Paris?"
    """
    print("Query: What is 15% of the temperature in Paris?")
    print("=" * 55)

    # Step 1: LLM decides to get the weather first
    print("\n--- Step 1: Get the temperature ---")
    print("  LLM thinks: I need the temperature in Paris first.")
    weather_result = get_weather("Paris")
    weather_data = json.loads(weather_result)
    print(f"  Tool call: get_weather('Paris')")
    print(f"  Result: {weather_result}")

    # Step 2: Extract temperature and calculate
    temp_str = weather_data["temperature"]  # "63F"
    temp_value = int(temp_str.replace("F", "").replace("C", ""))
    print(f"\n--- Step 2: Calculate 15% ---")
    print(f"  LLM thinks: Temperature is {temp_value}F. Now calculate 15% of {temp_value}.")
    calc_result = calculator(f"0.15 * {temp_value}")
    calc_data = json.loads(calc_result)
    print(f"  Tool call: calculator('0.15 * {temp_value}')")
    print(f"  Result: {calc_result}")

    # Step 3: Generate final answer
    answer = f"15% of the temperature in Paris ({temp_value}F) is {calc_data['result']}F."
    print(f"\n--- Step 3: Final Answer ---")
    print(f"  {answer}")

handle_multi_step_query()
```

**Expected output:**

```
Query: What is 15% of the temperature in Paris?
=======================================================

--- Step 1: Get the temperature ---
  LLM thinks: I need the temperature in Paris first.
  Tool call: get_weather('Paris')
  Result: {"city": "Paris", "temperature": "63F", "condition": "Partly Cloudy", "humidity": "60%"}

--- Step 2: Calculate 15% ---
  LLM thinks: Temperature is 63F. Now calculate 15% of 63.
  Tool call: calculator('0.15 * 63')
  Result: {"expression": "0.15 * 63", "result": 9.45}

--- Step 3: Final Answer ---
  15% of the temperature in Paris (63F) is 9.45F.
```

### Parallel Tool Calls

Some APIs support calling multiple tools at once:

```python
# Demonstrating parallel tool calls

def handle_parallel_query():
    """
    Handle a query where multiple tools can be called in parallel.
    Example: "Compare the weather in London and Tokyo"
    """
    print("Query: Compare the weather in London and Tokyo")
    print("=" * 55)

    # The LLM generates two tool calls at once
    tool_calls = [
        {"name": "get_weather", "arguments": {"city": "London"}},
        {"name": "get_weather", "arguments": {"city": "Tokyo"}},
    ]

    print("\nParallel tool calls:")
    results = []
    for call in tool_calls:
        result = TOOL_REGISTRY[call["name"]](**call["arguments"])
        results.append(json.loads(result))
        print(f"  {call['name']}({call['arguments']}) -> {result}")

    # Generate comparison
    print(f"\nFinal Answer:")
    print(f"  London: {results[0]['temperature']}, {results[0]['condition']}")
    print(f"  Tokyo:  {results[1]['temperature']}, {results[1]['condition']}")

    london_temp = int(results[0]['temperature'].replace('F', ''))
    tokyo_temp = int(results[1]['temperature'].replace('F', ''))
    diff = abs(london_temp - tokyo_temp)
    warmer = "Tokyo" if tokyo_temp > london_temp else "London"
    print(f"  {warmer} is {diff}F warmer.")

handle_parallel_query()
```

**Expected output:**

```
Query: Compare the weather in London and Tokyo
=======================================================

Parallel tool calls:
  get_weather({'city': 'London'}) -> {"city": "London", "temperature": "58F", "condition": "Rainy", "humidity": "82%"}
  get_weather({'city': 'Tokyo'}) -> {"city": "Tokyo", "temperature": "68F", "condition": "Cloudy", "humidity": "65%"}

Final Answer:
  London: 58F, Rainy
  Tokyo:  68F, Cloudy
  Tokyo is 10F warmer.
```

---

## 24.8 Error Handling and Edge Cases

### Robust Tool Execution

```python
import json
import traceback

def safe_tool_executor(tool_name, tool_args, tool_registry, timeout=30):
    """
    Execute a tool with comprehensive error handling.

    Args:
        tool_name: Name of the tool to execute
        tool_args: Arguments for the tool (dict or JSON string)
        tool_registry: Dictionary mapping tool names to functions
        timeout: Maximum execution time in seconds

    Returns:
        JSON string with the result or error
    """
    # 1. Validate tool exists
    if tool_name not in tool_registry:
        return json.dumps({
            "error": "TOOL_NOT_FOUND",
            "message": f"Tool '{tool_name}' not found. Available: {list(tool_registry.keys())}",
        })

    # 2. Parse arguments
    if isinstance(tool_args, str):
        try:
            tool_args = json.loads(tool_args)
        except json.JSONDecodeError as e:
            return json.dumps({
                "error": "INVALID_ARGUMENTS",
                "message": f"Could not parse arguments: {str(e)}",
                "raw_args": tool_args,
            })

    # 3. Validate arguments are a dictionary
    if not isinstance(tool_args, dict):
        return json.dumps({
            "error": "INVALID_ARGUMENTS",
            "message": f"Arguments must be a dictionary, got {type(tool_args).__name__}",
        })

    # 4. Execute the tool with error handling
    try:
        func = tool_registry[tool_name]
        result = func(**tool_args)
        return result
    except TypeError as e:
        return json.dumps({
            "error": "ARGUMENT_ERROR",
            "message": f"Wrong arguments for '{tool_name}': {str(e)}",
        })
    except Exception as e:
        return json.dumps({
            "error": "EXECUTION_ERROR",
            "message": f"Tool '{tool_name}' failed: {str(e)}",
            "error_type": type(e).__name__,
        })


# Test error cases
print("=== Error Handling Tests ===\n")

# Test 1: Unknown tool
result = safe_tool_executor("fly_to_mars", {}, TOOL_REGISTRY)
print(f"Unknown tool: {result}\n")

# Test 2: Invalid JSON arguments
result = safe_tool_executor("calculator", "not json", TOOL_REGISTRY)
print(f"Bad JSON: {result}\n")

# Test 3: Wrong arguments
result = safe_tool_executor("get_weather", {"wrong_param": "test"}, TOOL_REGISTRY)
print(f"Wrong args: {result}\n")

# Test 4: Successful call
result = safe_tool_executor("calculator", {"expression": "2 + 2"}, TOOL_REGISTRY)
print(f"Success: {result}")
```

**Expected output:**

```
=== Error Handling Tests ===

Unknown tool: {"error": "TOOL_NOT_FOUND", "message": "Tool 'fly_to_mars' not found. Available: ['get_weather', 'calculator', 'search_web']"}

Bad JSON: {"error": "INVALID_ARGUMENTS", "message": "Could not parse arguments: Expecting value: line 1 column 1 (char 0)", "raw_args": "not json"}

Wrong args: {"error": "ARGUMENT_ERROR", "message": "Wrong arguments for 'get_weather': get_weather() got an unexpected keyword argument 'wrong_param'"}

Success: {"expression": "2 + 2", "result": 4}
```

---

## 24.9 Building a Complete Example with OpenAI

Here is how a complete function calling application looks with the OpenAI API:

```python
# Complete function calling example using OpenAI API
# Requires: pip install openai
# Requires: OPENAI_API_KEY environment variable

import json
# from openai import OpenAI

def run_function_calling_demo():
    """
    Complete function calling demo.
    This code works with a real OpenAI API key.
    """

    # Initialize client
    # client = OpenAI()

    # Define the tools
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current weather for a city",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string", "description": "City name"},
                        "units": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "Temperature units"
                        }
                    },
                    "required": ["city"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "Evaluate a math expression",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "Math expression"}
                    },
                    "required": ["expression"]
                }
            }
        }
    ]

    # The tool functions
    tool_functions = {
        "get_weather": get_weather,
        "calculator": calculator,
    }

    # Start a conversation
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Use tools when needed."},
        {"role": "user", "content": "What is the temperature in London in celsius?"}
    ]

    print("=== Function Calling Flow ===\n")
    print(f"User: {messages[-1]['content']}\n")

    # Step 1: First API call -- model may request tool use
    # response = client.chat.completions.create(
    #     model="gpt-4",
    #     messages=messages,
    #     tools=tools,
    #     tool_choice="auto",
    # )

    # Simulated response
    print("Step 1: LLM decides to call get_weather")
    tool_call_name = "get_weather"
    tool_call_args = {"city": "London", "units": "celsius"}
    print(f"  Tool: {tool_call_name}({json.dumps(tool_call_args)})")

    # Step 2: Execute the tool
    result = tool_functions[tool_call_name](**tool_call_args)
    print(f"\nStep 2: Execute tool")
    print(f"  Result: {result}")

    # Step 3: Send result back to LLM
    messages.append({
        "role": "assistant",
        "content": None,
        "tool_calls": [{"id": "call_1", "function": {"name": tool_call_name, "arguments": json.dumps(tool_call_args)}}]
    })
    messages.append({
        "role": "tool",
        "tool_call_id": "call_1",
        "content": result
    })

    # Step 4: Get final response
    # final_response = client.chat.completions.create(
    #     model="gpt-4",
    #     messages=messages,
    # )

    # Simulated final response
    weather_data = json.loads(result)
    final_answer = f"The current temperature in London is {weather_data['temperature']}. The weather is {weather_data['condition'].lower()} with {weather_data['humidity']} humidity."

    print(f"\nStep 3: Send result back to LLM")
    print(f"\nStep 4: LLM generates final answer")
    print(f"  Assistant: {final_answer}")

run_function_calling_demo()
```

**Expected output:**

```
=== Function Calling Flow ===

User: What is the temperature in London in celsius?

Step 1: LLM decides to call get_weather
  Tool: get_weather({"city": "London", "units": "celsius"})

Step 2: Execute tool
  Result: {"city": "London", "temperature": "14.4C", "condition": "Rainy", "humidity": "82%"}

Step 3: Send result back to LLM

Step 4: LLM generates final answer
  Assistant: The current temperature in London is 14.4C. The weather is rainy with 82% humidity.
```

---

## Common Mistakes

1. **Not returning JSON from tools** -- LLMs work best when tool results are structured JSON. Returning plain text makes it harder for the LLM to extract information.

2. **Missing error handling** -- Tools can fail (network errors, invalid inputs, etc.). Always wrap tool execution in try/except and return a meaningful error message.

3. **Vague tool descriptions** -- If the description of a tool is too vague, the LLM will not know when to use it. Be specific about what the tool does, what it accepts, and what it returns.

4. **Not validating tool arguments** -- The LLM might generate arguments that do not match the expected schema. Always validate before executing.

5. **Forgetting to send tool results back** -- After executing a tool, you must send the result back to the LLM so it can generate the final answer. Skipping this step means the LLM never sees the result.

6. **Allowing unsafe operations** -- Never let the LLM call tools that can modify or delete data without validation and human approval.

---

## Best Practices

1. **Always return structured JSON from tools** -- This makes it easy for the LLM to parse and use the results.

2. **Use descriptive parameter names** -- `city` is better than `c`. `temperature_units` is better than `u`.

3. **Include examples in tool descriptions** -- Show the LLM example inputs and outputs so it knows the expected format.

4. **Implement retry logic** -- If a tool call fails, give the LLM a chance to try again with different arguments.

5. **Keep tool outputs concise** -- The LLM has a limited context window. Long tool outputs waste tokens. Summarize when possible.

6. **Log all tool calls** -- Record every tool call, its arguments, and its results for debugging and auditing.

---

## Quick Summary

Function calling is the mechanism that lets LLMs use external tools. The LLM does not directly execute functions; instead, it generates structured JSON describing which function to call and with what arguments. Your code parses this JSON, executes the function, and sends the result back to the LLM. Tools are defined using JSON Schema, which describes each tool's name, purpose, and parameters. Error handling is critical -- always validate tool names, parse arguments safely, and handle execution errors gracefully.

---

## Key Points

- LLMs cannot execute functions directly -- they generate **structured tool calls** (JSON)
- **JSON Schema** is used to define what arguments each tool accepts
- The function calling flow: user message -> LLM generates tool call -> code executes function -> result sent back to LLM -> LLM generates final answer
- A **tool registry** maps tool names to their Python functions
- Always **validate tool calls** before executing them (check tool name, parse arguments, handle errors)
- Tools should return **structured JSON** for easy parsing
- **Multiple tool calls** can be sequential (one after another) or parallel (at the same time)
- Good tool **descriptions** are critical for the LLM to choose the right tool
- Always include **error handling** for tool execution failures
- **Log everything** for debugging and auditing

---

## Practice Questions

1. Explain the function calling flow in your own words. Why can the LLM not call functions directly?

2. Write a JSON Schema for a tool called `send_email` that takes three parameters: `to` (required string), `subject` (required string), and `body` (required string).

3. You have a tool that sometimes takes 30 seconds to respond. How would you handle this in your tool execution pipeline? What should you tell the user while waiting?

4. An LLM generates a tool call for a function called `delete_database`. Your tool registry contains this function. Should you execute it? What safety measures should be in place?

5. Explain the difference between sequential and parallel tool calls. When would you use each?

---

## Exercises

### Exercise 1: Build a Unit Converter Tool

Create a `convert_units` tool that converts between different units (kilometers to miles, celsius to fahrenheit, kilograms to pounds, etc.). Define the JSON Schema, implement the function, and write a test that simulates an LLM calling it.

### Exercise 2: Multi-Tool Pipeline

Build a system with three tools: `get_stock_price(symbol)`, `get_company_info(symbol)`, and `calculator(expression)`. Handle the query: "What would my 100 shares of AAPL be worth if the price went up 15%?" This requires calling get_stock_price, then the calculator.

### Exercise 3: Tool Call Validator

Write a function called `validate_tool_call(tool_call, tool_definitions)` that checks: (a) the tool name exists in the definitions, (b) all required parameters are present, (c) parameter types match the schema. Return detailed error messages for any validation failures.

---

## What Is Next?

Now that you understand how function calling works under the hood, Chapter 25 shows you how to build agents using **LangChain** -- a popular framework that handles all the tool management, conversation history, and agent loops for you. Instead of building everything from scratch, you will use LangChain's pre-built components to create powerful agents in just a few lines of code.
