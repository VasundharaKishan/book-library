# Chapter 25: Building Agents with LangChain

## What You Will Learn

In this chapter, you will learn:

- What LangChain is and why it has become the most popular framework for building LLM applications
- How to create chains that connect prompts, LLMs, and output parsers
- How to define and use tools (search, calculator, code interpreter)
- How to add memory so agents remember previous conversations
- How to build a complete agent that reasons and uses tools
- How to build a research agent that searches the web and summarizes findings

## Why This Chapter Matters

In Chapters 23 and 24, you built agents and function calling from scratch. That was valuable for understanding how things work under the hood. But in practice, building everything from scratch is like making bread by growing your own wheat. It works, but there is a faster way.

LangChain is a framework that provides ready-made building blocks for LLM applications. It handles the messy details -- conversation memory, tool management, error handling, prompt formatting -- so you can focus on what your agent actually does.

Think of LangChain as a Lego set for AI applications. Instead of carving each brick yourself, you snap together pre-built pieces to create powerful systems quickly.

---

## 25.1 What Is LangChain?

### Overview

```
+---------------------------------------------------------------+
|              LANGCHAIN ECOSYSTEM                              |
+---------------------------------------------------------------+
|                                                               |
|  LangChain is a framework with these main components:         |
|                                                               |
|  1. Models       Connect to any LLM (OpenAI, Anthropic, etc.)|
|  2. Prompts      Templates for structuring LLM inputs         |
|  3. Chains       Link multiple steps together                 |
|  4. Memory       Remember conversation history                |
|  5. Tools        Let agents interact with the world           |
|  6. Agents       Autonomous LLM systems with tools            |
|                                                               |
|  Think of it as:                                              |
|  Models  = The engine                                         |
|  Prompts = The steering wheel                                 |
|  Chains  = The transmission (connects parts)                  |
|  Memory  = The dashcam (records history)                      |
|  Tools   = The hands (interact with the world)                |
|  Agents  = The driver (makes decisions)                       |
|                                                               |
+---------------------------------------------------------------+
```

### Installation

```python
# Install LangChain and its dependencies
# pip install langchain langchain-openai langchain-community
# pip install duckduckgo-search   # For web search tool
# pip install numexpr              # For calculator tool

# For this chapter, you also need an API key:
# export OPENAI_API_KEY="your-key-here"
# Or set it in Python:
# import os
# os.environ["OPENAI_API_KEY"] = "your-key-here"
```

### Verifying Installation

```python
import langchain

print(f"LangChain version: {langchain.__version__}")
```

**Expected output:**

```
LangChain version: 0.3.7
```

---

## 25.2 Models: Connecting to LLMs

### Using Chat Models

```python
from langchain_openai import ChatOpenAI

# Create an LLM instance
llm = ChatOpenAI(
    model="gpt-4o-mini",       # Which model to use
    temperature=0,              # 0 = deterministic, 1 = creative
    max_tokens=500,             # Maximum response length
)

# Simple invocation
response = llm.invoke("What is Python in one sentence?")
print(f"Response: {response.content}")
```

**Expected output:**

```
Response: Python is a high-level, interpreted programming language known for its simple syntax and versatility across web development, data science, and automation.
```

**Line-by-line explanation:**

- `ChatOpenAI` -- LangChain's wrapper around the OpenAI chat API. Similar wrappers exist for Anthropic (`ChatAnthropic`), Google (`ChatGoogleGenerativeAI`), and others
- `model="gpt-4o-mini"` -- A fast, affordable model good for most tasks
- `temperature=0` -- Makes output deterministic (same input always gives same output)
- `llm.invoke(...)` -- Sends a message to the LLM and returns the response
- `response.content` -- The text content of the LLM's response

### Using Different Providers

```python
# LangChain supports many LLM providers:

# OpenAI
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4o-mini")

# Anthropic
# from langchain_anthropic import ChatAnthropic
# llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")

# Google
# from langchain_google_genai import ChatGoogleGenerativeAI
# llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")

# Local models via Ollama
# from langchain_ollama import ChatOllama
# llm = ChatOllama(model="llama3.1")

print("LangChain supports OpenAI, Anthropic, Google, Ollama, and many more.")
print("You can swap LLM providers by changing one line of code.")
```

---

## 25.3 Prompts: Structuring Your Inputs

### Prompt Templates

Prompt templates let you create reusable prompts with variables:

```python
from langchain_core.prompts import ChatPromptTemplate

# Create a prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that explains {topic} concepts in simple terms."),
    ("user", "{question}")
])

# Fill in the template
formatted = prompt.format_messages(
    topic="Python programming",
    question="What is a list comprehension?"
)

# Show the formatted messages
for msg in formatted:
    print(f"[{msg.type}]: {msg.content}")
```

**Expected output:**

```
[system]: You are a helpful assistant that explains Python programming concepts in simple terms.
[human]: What is a list comprehension?
```

**Line-by-line explanation:**

- `ChatPromptTemplate.from_messages(...)` -- Creates a template from a list of (role, content) pairs
- `("system", "...")` -- The system message sets the LLM's behavior
- `{topic}` and `{question}` -- Variables that get filled in when the template is used
- `prompt.format_messages(...)` -- Replaces the variables with actual values
- This approach lets you reuse the same prompt structure with different inputs

### Using Templates with Models

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Create the prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a {role}. Answer questions in {style} style."),
    ("user", "{question}")
])

# Create the model
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Create a chain: prompt -> model
chain = prompt | llm

# Run the chain
response = chain.invoke({
    "role": "pirate",
    "style": "pirate",
    "question": "What is recursion in programming?"
})

print(response.content)
```

**Expected output:**

```
Arrr, ye landlubber! Recursion be like a pirate lookin' into two mirrors facin' each other -- ye see yerself repeated endlessly! In programming, 'tis when a function calls itself to solve a smaller piece of the same problem, until it hits the base case and stops. Like a treasure map that says "dig here, but first follow THIS treasure map," until ye finally find the gold!
```

---

## 25.4 Chains: Connecting Steps Together

### What Is a Chain?

A chain connects multiple processing steps. The output of one step becomes the input to the next:

```
+---------------------------------------------------------------+
|              LANGCHAIN CHAIN                                  |
+---------------------------------------------------------------+
|                                                               |
|  Input --> [Prompt Template] --> [LLM] --> [Output Parser]    |
|                                                               |
|  Like an assembly line:                                       |
|  Raw materials --> Shaping --> Painting --> Packaging          |
|                                                               |
+---------------------------------------------------------------+
```

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Step 1: Prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("user", "Explain {concept} in exactly 3 bullet points.")
])

# Step 2: LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Step 3: Output parser (extracts the text from the response)
parser = StrOutputParser()

# Create the chain using the pipe operator |
chain = prompt | llm | parser

# Run the chain
result = chain.invoke({"concept": "machine learning"})
print(result)
```

**Expected output:**

```
- Machine learning is a type of AI where computers learn patterns from data rather than being explicitly programmed with rules.
- It works by training algorithms on large datasets, allowing models to make predictions or decisions based on new, unseen data.
- Common applications include email spam filtering, recommendation systems (Netflix, Spotify), and image recognition (facial recognition, medical imaging).
```

**Line-by-line explanation:**

- `prompt | llm | parser` -- The pipe operator `|` creates a chain. Data flows left to right
- `StrOutputParser()` -- Extracts the plain text string from the LLM's response object
- `chain.invoke({"concept": "machine learning"})` -- Runs the entire chain: fills the template, sends to LLM, parses the output

### Sequential Chains

You can chain multiple LLM calls together:

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
parser = StrOutputParser()

# Chain 1: Generate a topic
topic_prompt = ChatPromptTemplate.from_messages([
    ("user", "Give me one interesting fact about {subject}. Just the fact, nothing else.")
])
topic_chain = topic_prompt | llm | parser

# Chain 2: Explain the fact for a child
explain_prompt = ChatPromptTemplate.from_messages([
    ("user", "Explain this fact to a 5-year-old: {fact}")
])
explain_chain = explain_prompt | llm | parser

# Run them sequentially
fact = topic_chain.invoke({"subject": "octopuses"})
print(f"Fact: {fact}\n")

explanation = explain_chain.invoke({"fact": fact})
print(f"Child-friendly explanation: {explanation}")
```

**Expected output:**

```
Fact: Octopuses have three hearts — two pump blood to the gills, and one pumps it to the rest of the body.

Child-friendly explanation: Did you know that an octopus has THREE hearts? That is two more than you! Two of the hearts help push blood to its special breathing parts (kind of like your lungs but underwater). And the third heart pushes blood all around its body, just like your one heart does. Pretty cool, right?
```

---

## 25.5 Tools: Giving Agents Superpowers

### Built-in Tools

LangChain comes with many pre-built tools:

```python
# LangChain provides many built-in tools

# Web Search (DuckDuckGo -- no API key needed)
from langchain_community.tools import DuckDuckGoSearchRun
search_tool = DuckDuckGoSearchRun()

# Run a search
result = search_tool.invoke("What is the latest version of Python?")
print(f"Search result: {result[:200]}...")
```

**Expected output:**

```
Search result: Python 3.13 is the latest stable release of the Python programming language. It was released in October 2024 and includes several performance improvements and new features...
```

### Creating Custom Tools

```python
from langchain_core.tools import tool

@tool
def calculator(expression: str) -> str:
    """Calculate a mathematical expression.

    Args:
        expression: A math expression like '2 + 2' or 'sqrt(144)'
    """
    import math
    safe_dict = {
        "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
        "pi": math.pi, "e": math.e, "abs": abs, "round": round,
    }
    try:
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def get_current_time() -> str:
    """Get the current date and time."""
    from datetime import datetime
    now = datetime.now()
    return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"


@tool
def word_count(text: str) -> str:
    """Count the number of words in a text.

    Args:
        text: The text to count words in
    """
    count = len(text.split())
    return f"Word count: {count}"


# Test the custom tools
print(calculator.invoke("2 ** 10"))
print(get_current_time.invoke(""))
print(word_count.invoke("The quick brown fox jumps over the lazy dog"))
```

**Expected output:**

```
Result: 1024
Current time: 2024-11-15 14:30:22
Word count: 9
```

**Line-by-line explanation:**

- `@tool` -- This decorator converts a regular Python function into a LangChain tool. It automatically extracts the function name, description (from the docstring), and parameter types
- The docstring is critical -- it tells the LLM what the tool does and when to use it
- Type hints (`expression: str -> str`) tell the LLM the expected input and output types
- `tool.invoke(...)` -- Calls the tool with the given input

### Viewing Tool Information

```python
# See what the LLM knows about our tools

tools = [calculator, get_current_time, word_count]

print("Tools available to the agent:")
print("=" * 60)
for t in tools:
    print(f"\n  Name: {t.name}")
    print(f"  Description: {t.description}")
    print(f"  Args: {t.args}")
```

**Expected output:**

```
Tools available to the agent:
============================================================

  Name: calculator
  Description: Calculate a mathematical expression.
  Args: {'expression': {'title': 'Expression', 'type': 'string'}}

  Name: get_current_time
  Description: Get the current date and time.
  Args: {}

  Name: word_count
  Description: Count the number of words in a text.
  Args: {'text': {'title': 'Text', 'type': 'string'}}
```

---

## 25.6 Memory: Remembering Conversations

### Why Memory Matters

Without memory, every message to the LLM is treated as a brand-new conversation:

```
+---------------------------------------------------------------+
|              WITHOUT MEMORY                                   |
+---------------------------------------------------------------+
|                                                               |
|  User: "My name is Alice."                                    |
|  LLM:  "Nice to meet you, Alice!"                            |
|                                                               |
|  User: "What is my name?"                                     |
|  LLM:  "I don't know your name."  <-- Forgot!                |
|                                                               |
+---------------------------------------------------------------+
|              WITH MEMORY                                      |
+---------------------------------------------------------------+
|                                                               |
|  User: "My name is Alice."                                    |
|  LLM:  "Nice to meet you, Alice!"                            |
|                                                               |
|  User: "What is my name?"                                     |
|  LLM:  "Your name is Alice."  <-- Remembers!                 |
|                                                               |
+---------------------------------------------------------------+
```

### Conversation Buffer Memory

```python
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

# Create a message history store
message_history = InMemoryChatMessageHistory()

# Add messages to history
message_history.add_user_message("My name is Alice and I work at Acme Corp.")
message_history.add_ai_message("Nice to meet you, Alice! How can I help you today?")
message_history.add_user_message("What is 2 + 2?")
message_history.add_ai_message("2 + 2 equals 4.")

# View the conversation history
print("Conversation History:")
print("=" * 50)
for msg in message_history.messages:
    role = "User" if isinstance(msg, HumanMessage) else "AI"
    print(f"  [{role}]: {msg.content}")

print(f"\nTotal messages: {len(message_history.messages)}")
```

**Expected output:**

```
Conversation History:
==================================================
  [User]: My name is Alice and I work at Acme Corp.
  [AI]: Nice to meet you, Alice! How can I help you today?
  [User]: What is 2 + 2?
  [AI]: 2 + 2 equals 4.

Total messages: 4
```

### Using Memory with a Chain

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

# Create prompt with a placeholder for conversation history
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Use the conversation history to answer questions."),
    MessagesPlaceholder(variable_name="history"),
    ("user", "{input}")
])

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
chain = prompt | llm

# Maintain conversation history manually
history = []

# First message
response = chain.invoke({"input": "My name is Alice.", "history": history})
print(f"User: My name is Alice.")
print(f"AI: {response.content}\n")

# Update history
history.append(HumanMessage(content="My name is Alice."))
history.append(AIMessage(content=response.content))

# Second message -- the model should remember the name
response = chain.invoke({"input": "What is my name?", "history": history})
print(f"User: What is my name?")
print(f"AI: {response.content}")
```

**Expected output:**

```
User: My name is Alice.
AI: Nice to meet you, Alice! How can I help you today?

User: What is my name?
AI: Your name is Alice!
```

---

## 25.7 Agents: Putting It All Together

### Creating an Agent

An agent combines an LLM, tools, and memory into a system that can reason and take actions:

```python
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Step 1: Define tools
@tool
def search_web(query: str) -> str:
    """Search the web for current information about a topic.

    Args:
        query: What to search for
    """
    # Simulated search results
    results = {
        "python latest version": "Python 3.13.0 was released in October 2024.",
        "langchain": "LangChain is a framework for building LLM applications.",
    }
    query_lower = query.lower()
    for key, value in results.items():
        if key in query_lower:
            return value
    return f"Search results for '{query}': Various articles found about this topic."


@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression.

    Args:
        expression: Math expression like '2 + 2' or '15 * 3.14'
    """
    import math
    safe_dict = {"sqrt": math.sqrt, "pi": math.pi, "abs": abs}
    try:
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        return f"The result is: {result}"
    except Exception as e:
        return f"Error calculating: {str(e)}"


tools = [search_web, calculator]

# Step 2: Create the LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Step 3: Create the prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful research assistant. Use the available tools when needed to answer questions accurately."),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Step 4: Create the agent
agent = create_tool_calling_agent(llm, tools, prompt)

# Step 5: Create the agent executor (runs the agent loop)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,       # Print the agent's reasoning
    max_iterations=5,   # Safety limit
)

# Step 6: Run the agent
result = agent_executor.invoke({"input": "What is the latest version of Python?"})
print(f"\nFinal Answer: {result['output']}")
```

**Expected output:**

```
> Entering new AgentExecutor chain...

Invoking: `search_web` with `{'query': 'Python latest version'}`

Python 3.13.0 was released in October 2024.

The latest version of Python is Python 3.13.0, which was released in October 2024.

> Finished chain.

Final Answer: The latest version of Python is Python 3.13.0, which was released in October 2024.
```

**Line-by-line explanation:**

- `create_tool_calling_agent(llm, tools, prompt)` -- Creates an agent that can use the LLM's native function calling capability
- `AgentExecutor` -- Runs the agent loop: sends the user's message to the LLM, executes any tool calls, sends results back, and repeats until the agent has a final answer
- `verbose=True` -- Prints each step of the agent's reasoning, showing which tools it uses and why
- `max_iterations=5` -- Prevents infinite loops by limiting the number of think-act cycles
- `agent_scratchpad` -- A special placeholder where the agent's intermediate work (tool calls and results) is stored

---

## 25.8 Complete Research Agent Example

### Building a Research Agent

Here is a complete, practical agent that can research topics by searching the web and performing calculations:

```python
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from datetime import datetime

# ============================================
# Define Tools
# ============================================

@tool
def web_search(query: str) -> str:
    """Search the web for information about any topic. Use this when you need current or factual information.

    Args:
        query: The search query
    """
    # In production, use DuckDuckGoSearchRun or SerpAPI
    mock_data = {
        "python popularity 2024": "Python remains the #1 programming language in 2024 according to the TIOBE Index, with a rating of 18.67%.",
        "javascript popularity 2024": "JavaScript is the #6 programming language in 2024 with a TIOBE rating of 3.17%.",
        "python vs javascript": "Python is preferred for data science and AI, while JavaScript dominates web development.",
        "world population 2024": "The world population reached 8.1 billion in 2024.",
    }
    for key, value in mock_data.items():
        if any(word in query.lower() for word in key.split()):
            return value
    return f"Found information about: {query}"


@tool
def calculate(expression: str) -> str:
    """Perform mathematical calculations. Supports basic math, percentages, and common functions.

    Args:
        expression: Math expression (e.g., '2 + 2', '100 * 0.15', 'sqrt(144)')
    """
    import math
    safe_dict = {
        "sqrt": math.sqrt, "log": math.log, "sin": math.sin,
        "cos": math.cos, "pi": math.pi, "e": math.e,
        "abs": abs, "round": round, "pow": pow,
    }
    try:
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def get_date() -> str:
    """Get today's date. Use this when the user asks about today or the current date."""
    return f"Today is {datetime.now().strftime('%B %d, %Y')}"


# ============================================
# Create the Agent
# ============================================

# LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Tools
tools = [web_search, calculate, get_date]

# Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a thorough research assistant. When answering questions:
1. Search for relevant information using web_search
2. Use calculate for any math operations
3. Always cite your sources
4. If you need multiple pieces of information, search for each one separately
5. Provide clear, well-organized answers"""),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Agent
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=10,
    handle_parsing_errors=True,
)

# ============================================
# Use the Agent
# ============================================

# Maintain conversation history
chat_history = []

def ask(question):
    """Ask the research agent a question."""
    print(f"\n{'='*60}")
    print(f"Question: {question}")
    print(f"{'='*60}\n")

    result = agent_executor.invoke({
        "input": question,
        "chat_history": chat_history,
    })

    # Update history
    chat_history.append(HumanMessage(content=question))
    chat_history.append(AIMessage(content=result["output"]))

    print(f"\nFinal Answer: {result['output']}")
    return result["output"]

# Ask a research question
ask("Compare the popularity of Python and JavaScript in 2024. Which is more popular and by how much?")
```

**Expected output:**

```
============================================================
Question: Compare the popularity of Python and JavaScript in 2024. Which is more popular and by how much?
============================================================

> Entering new AgentExecutor chain...

Invoking: `web_search` with `{'query': 'python popularity 2024'}`
Python remains the #1 programming language in 2024 according to the TIOBE Index, with a rating of 18.67%.

Invoking: `web_search` with `{'query': 'javascript popularity 2024'}`
JavaScript is the #6 programming language in 2024 with a TIOBE rating of 3.17%.

Invoking: `calculate` with `{'expression': '18.67 - 3.17'}`
18.67 - 3.17 = 15.5

Invoking: `calculate` with `{'expression': '18.67 / 3.17'}`
18.67 / 3.17 = 5.89

According to the TIOBE Index for 2024:
- **Python** is #1 with a rating of 18.67%
- **JavaScript** is #6 with a rating of 3.17%

Python is more popular by 15.5 percentage points, making it about 5.89 times more popular than JavaScript by this metric.

> Finished chain.

Final Answer: According to the TIOBE Index for 2024...
```

---

## 25.9 Agent with Conversation Memory

### Building a Stateful Agent

```python
# Agent that remembers the entire conversation

def create_conversational_agent():
    """Create an agent that maintains conversation history."""

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    tools = [web_search, calculate, get_date]

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that remembers our conversation. Use tools when needed."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

    history = []

    def chat(message):
        """Send a message and get a response."""
        result = executor.invoke({
            "input": message,
            "chat_history": history,
        })
        history.append(HumanMessage(content=message))
        history.append(AIMessage(content=result["output"]))
        return result["output"]

    return chat


# Create and use the conversational agent
chat = create_conversational_agent()

# Multi-turn conversation
print("User: My favorite programming language is Python.")
print(f"Agent: {chat('My favorite programming language is Python.')}\n")

print("User: What did I just tell you about my preferences?")
print(f"Agent: {chat('What did I just tell you about my preferences?')}\n")

print("User: Search for the latest news about it.")
print(f"Agent: {chat('Search for the latest news about it.')}")
```

**Expected output:**

```
User: My favorite programming language is Python.
Agent: That's great! Python is an excellent choice — it's versatile, beginner-friendly, and widely used in data science, web development, and AI. What would you like to know about Python?

User: What did I just tell you about my preferences?
Agent: You told me that your favorite programming language is Python!

User: Search for the latest news about it.
Agent: According to the TIOBE Index, Python remains the #1 programming language in 2024 with a rating of 18.67%. It continues to dominate in areas like data science and artificial intelligence.
```

---

## 25.10 Error Handling and Debugging

### Handling Agent Errors

```python
# Setting up error handling for agents

from langchain.agents import AgentExecutor

def create_robust_agent():
    """Create an agent with proper error handling."""

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    tools = [web_search, calculate]

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. If a tool fails, try a different approach."),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5,           # Prevent infinite loops
        handle_parsing_errors=True,  # Handle LLM output parsing errors
        return_intermediate_steps=True,  # Return tool call details
    )

    return executor


agent = create_robust_agent()

# Run with error handling
try:
    result = agent.invoke({"input": "Calculate sqrt(144) + 10"})
    print(f"\nAnswer: {result['output']}")

    # Show intermediate steps
    if result.get('intermediate_steps'):
        print(f"\nIntermediate steps:")
        for step in result['intermediate_steps']:
            action, observation = step
            print(f"  Tool: {action.tool}")
            print(f"  Input: {action.tool_input}")
            print(f"  Output: {observation}")
except Exception as e:
    print(f"Agent failed: {str(e)}")
```

**Expected output:**

```
> Entering new AgentExecutor chain...

Invoking: `calculate` with `{'expression': 'sqrt(144) + 10'}`
sqrt(144) + 10 = 22.0

The result of sqrt(144) + 10 is 22.0

> Finished chain.

Answer: The result of sqrt(144) + 10 is 22.0

Intermediate steps:
  Tool: calculate
  Input: {'expression': 'sqrt(144) + 10'}
  Output: sqrt(144) + 10 = 22.0
```

---

## Common Mistakes

1. **Not setting max_iterations** -- Without a limit, agents can loop forever, consuming tokens and money. Always set `max_iterations`.

2. **Poor tool descriptions** -- If your tool's docstring is vague, the LLM will misuse it or ignore it. Write clear, specific descriptions with examples.

3. **Forgetting to handle errors** -- Tools can fail. Set `handle_parsing_errors=True` and wrap agent calls in try/except.

4. **Growing conversation history** -- Every message adds to the history, which counts toward the context window. For long conversations, summarize or trim old messages.

5. **Using the wrong LLM** -- Not all models support function calling. Use models that explicitly support it (GPT-4, GPT-4o-mini, Claude 3, etc.).

6. **Not testing tools individually** -- Always test each tool in isolation before giving it to an agent. A broken tool will cause the entire agent to fail.

---

## Best Practices

1. **Start with verbose=True** -- Always enable verbose logging during development so you can see what the agent is doing.

2. **Keep tools focused** -- Each tool should do one thing well. Instead of one mega-tool, create several small, specific tools.

3. **Set temperature=0 for agents** -- Deterministic outputs make agents more predictable and easier to debug.

4. **Use return_intermediate_steps=True** -- This lets you inspect what tools were called and what results were returned.

5. **Implement tool timeouts** -- Wrap tool calls with timeouts so a slow API call does not hang the entire agent.

6. **Test edge cases** -- What happens when a tool returns an error? What if the search returns no results? Test these scenarios.

---

## Quick Summary

LangChain provides a comprehensive framework for building LLM applications with agents. The key components are: Models (connect to any LLM), Prompts (template your inputs), Chains (connect processing steps), Memory (remember conversations), Tools (interact with the world), and Agents (combine everything). The `create_tool_calling_agent` function and `AgentExecutor` handle the complex agent loop automatically. Custom tools are created with the `@tool` decorator and clear docstrings. Conversation memory is maintained through a list of messages passed to the agent on each turn.

---

## Key Points

- **LangChain** is a framework for building LLM applications with pre-built components
- **Chains** connect processing steps using the pipe operator `|`
- **Tools** are Python functions with `@tool` decorator and descriptive docstrings
- **Memory** is maintained by passing conversation history to the prompt
- **Agents** combine LLMs, tools, and memory to reason and take actions
- `create_tool_calling_agent` creates agents that use native function calling
- `AgentExecutor` runs the agent loop with safety features (max iterations, error handling)
- Always set `max_iterations` and `handle_parsing_errors=True`
- Use `verbose=True` during development to see agent reasoning
- Test tools individually before giving them to an agent

---

## Practice Questions

1. What is the difference between a chain and an agent in LangChain? When would you use each?

2. You want to create a tool that reads a CSV file and returns summary statistics. Write the `@tool`-decorated function with a proper docstring.

3. An agent keeps calling the search tool in a loop without reaching a final answer. What are three possible causes and their fixes?

4. Explain what `MessagesPlaceholder(variable_name="agent_scratchpad")` does in the agent prompt. Why is it necessary?

5. How would you limit conversation memory to the last 10 messages to avoid exceeding the context window?

---

## Exercises

### Exercise 1: Personal Assistant Agent

Build a LangChain agent with tools for: getting the current time, setting reminders (store in a Python list), and doing calculations. Test it with: "Remind me to buy groceries at 5 PM. Also, what is 15% tip on a $47.50 dinner?"

### Exercise 2: Code Analysis Agent

Create an agent with a tool that reads Python files and another that counts lines of code. Give it a directory path and ask it to analyze the codebase (total files, total lines, average lines per file).

### Exercise 3: Multi-Source Research Agent

Build an agent with a web search tool and a Wikipedia tool (simulated). Ask it to research a topic, gather information from both sources, and write a comparison of the different perspectives.

---

## What Is Next?

In Chapter 26, you will go beyond single agents and explore **multi-agent systems**. You will learn how to create teams of specialized agents that collaborate on complex tasks -- like a researcher who gathers information, a writer who drafts content, and an editor who polishes the final product. Using the CrewAI framework, you will build your first multi-agent workflow.
