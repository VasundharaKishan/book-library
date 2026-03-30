# Chapter 23: What Are AI Agents?

## What You Will Learn

In this chapter, you will learn:

- What an AI agent is and how it differs from a regular chatbot
- The three core components of an agent: tools, reasoning, and autonomy
- How the agent loop works (observe, think, act)
- Real-world examples of AI agents in action
- Different types of agents: ReAct, plan-and-execute, and conversational
- When to use an agent vs a simple prompt

## Why This Chapter Matters

Imagine you ask a friend to plan a weekend trip for you. A chatbot would give you a list of suggestions and stop there. An agent would actually search for flights, compare hotel prices, check the weather forecast, book reservations, and send you the itinerary -- all on its own.

AI agents are the next leap beyond chatbots. While a chatbot can only generate text, an agent can **take actions** in the real world. It can search the web, run code, query databases, send emails, and make API calls. The agent decides which actions to take, observes the results, and adjusts its plan accordingly.

This is where AI moves from "answering questions" to "getting things done." Understanding agents is essential because they are rapidly becoming the standard way to build useful AI applications.

---

## 23.1 Chatbot vs Agent: What Is the Difference?

### A Simple Comparison

```
+---------------------------------------------------------------+
|              CHATBOT vs AGENT                                 |
+---------------------------------------------------------------+
|                                                               |
|  CHATBOT:                                                     |
|  - Receives a question                                        |
|  - Generates a text answer                                    |
|  - Done                                                       |
|                                                               |
|  Like a librarian who can answer questions                    |
|  but cannot leave the library                                 |
|                                                               |
|  AGENT:                                                       |
|  - Receives a goal                                            |
|  - Breaks it into steps                                       |
|  - Uses tools to complete each step                           |
|  - Checks results and adjusts                                 |
|  - Repeats until the goal is achieved                         |
|                                                               |
|  Like a personal assistant who can make calls,                |
|  search the internet, write documents, and                    |
|  keep working until the job is done                           |
|                                                               |
+---------------------------------------------------------------+
```

```python
# Simulating the difference between a chatbot and an agent

def chatbot(question):
    """A chatbot just generates text."""
    # In reality, this would call an LLM
    responses = {
        "What is the weather?": "I don't have access to real-time weather data, "
                                "but you can check weather.com.",
        "Book me a flight": "I can't book flights, but you can try expedia.com.",
    }
    return responses.get(question, "I don't know.")


def agent(goal):
    """An agent uses tools and reasoning to achieve a goal."""
    steps = []

    # Step 1: Think about what to do
    steps.append("THINK: I need to find the current weather. Let me use the weather tool.")

    # Step 2: Use a tool
    steps.append("ACT: Calling weather_api('New York')")
    steps.append("OBSERVE: Temperature: 72F, Sunny, Humidity: 45%")

    # Step 3: Think about the result
    steps.append("THINK: I have the weather data. Let me format a nice response.")

    # Step 4: Respond
    steps.append("RESPOND: It is currently 72F and sunny in New York with 45% humidity.")

    return steps


# Compare
print("=== CHATBOT ===")
print(chatbot("What is the weather?"))

print("\n=== AGENT ===")
for step in agent("What is the weather in New York?"):
    print(f"  {step}")
```

**Expected output:**

```
=== CHATBOT ===
I don't have access to real-time weather data, but you can check weather.com.

=== AGENT ===
  THINK: I need to find the current weather. Let me use the weather tool.
  ACT: Calling weather_api('New York')
  OBSERVE: Temperature: 72F, Sunny, Humidity: 45%
  THINK: I have the weather data. Let me format a nice response.
  RESPOND: It is currently 72F and sunny in New York with 45% humidity.
```

**Line-by-line explanation:**

- The chatbot receives a question and returns a static text response. It cannot access real data
- The agent follows a loop: it thinks about what to do, takes an action (calls a tool), observes the result, thinks again, and then responds with real information
- The key difference is that the agent can **use tools** and **reason about results**

---

## 23.2 The Three Pillars of an AI Agent

Every AI agent is built on three core components:

```
+---------------------------------------------------------------+
|              THE THREE PILLARS                                |
+---------------------------------------------------------------+
|                                                               |
|           +----------+                                        |
|           |  TOOLS   |   What the agent CAN DO                |
|           +----------+   (search, calculate, browse, etc.)    |
|                |                                              |
|           +----------+                                        |
|           |REASONING |   How the agent THINKS                 |
|           +----------+   (plan, decide, reflect)              |
|                |                                              |
|           +----------+                                        |
|           |AUTONOMY  |   How INDEPENDENTLY it works            |
|           +----------+   (with or without human approval)     |
|                                                               |
+---------------------------------------------------------------+
```

### Pillar 1: Tools

Tools are functions that an agent can call to interact with the outside world:

```python
# Examples of agent tools

tools = {
    "web_search": {
        "description": "Search the internet for information",
        "example": "web_search('latest Python version')",
        "returns": "Search results with titles, URLs, and snippets",
    },
    "calculator": {
        "description": "Perform mathematical calculations",
        "example": "calculator('15% of 234.50')",
        "returns": "The numerical result",
    },
    "code_executor": {
        "description": "Write and run Python code",
        "example": "code_executor('import pandas as pd; print(pd.__version__)')",
        "returns": "The output of the code",
    },
    "email_sender": {
        "description": "Send an email to someone",
        "example": "email_sender(to='bob@email.com', subject='Meeting', body='...')",
        "returns": "Confirmation that email was sent",
    },
    "database_query": {
        "description": "Query a SQL database",
        "example": "database_query('SELECT COUNT(*) FROM users')",
        "returns": "Query results",
    },
}

print("Available Agent Tools:")
print("=" * 60)
for name, info in tools.items():
    print(f"\n  Tool: {name}")
    print(f"  Description: {info['description']}")
    print(f"  Example: {info['example']}")
    print(f"  Returns: {info['returns']}")
```

**Expected output:**

```
Available Agent Tools:
============================================================

  Tool: web_search
  Description: Search the internet for information
  Example: web_search('latest Python version')
  Returns: Search results with titles, URLs, and snippets

  Tool: calculator
  Description: Perform mathematical calculations
  Example: calculator('15% of 234.50')
  Returns: The numerical result

  Tool: code_executor
  Description: Write and run Python code
  Example: code_executor('import pandas as pd; print(pd.__version__)')
  Returns: The output of the code

  Tool: email_sender
  Description: Send an email to someone
  Example: email_sender(to='bob@email.com', subject='Meeting', body='...')
  Returns: Confirmation that email was sent

  Tool: database_query
  Description: Query a SQL database
  Example: database_query('SELECT COUNT(*) FROM users')
  Returns: Query results
```

### Pillar 2: Reasoning

The LLM at the heart of the agent provides reasoning ability. It decides:

- **What** tool to use
- **When** to use it
- **How** to interpret results
- **Whether** to try a different approach if something fails

```python
# Simulating agent reasoning

def agent_reasoning(goal, available_tools, context=""):
    """Simulate how an agent reasons about a goal."""

    print(f"GOAL: {goal}")
    print(f"AVAILABLE TOOLS: {', '.join(available_tools)}")
    if context:
        print(f"CONTEXT: {context}")
    print()

    # The LLM generates reasoning like this:
    reasoning_steps = [
        "1. ANALYZE: What does the user want?",
        f"   -> The user wants to: {goal}",
        "",
        "2. PLAN: What steps are needed?",
        "   -> Step 1: Search for the information",
        "   -> Step 2: Process the results",
        "   -> Step 3: Format and present the answer",
        "",
        "3. DECIDE: Which tool should I use first?",
        f"   -> I should use: {available_tools[0]}",
        "   -> Because: It will give me the information I need",
        "",
        "4. EXECUTE: Call the selected tool",
    ]

    for step in reasoning_steps:
        print(f"  {step}")

# Example
agent_reasoning(
    goal="Find the population of Tokyo and compare it to New York",
    available_tools=["web_search", "calculator", "code_executor"],
)
```

**Expected output:**

```
GOAL: Find the population of Tokyo and compare it to New York
AVAILABLE TOOLS: web_search, calculator, code_executor

  1. ANALYZE: What does the user want?
     -> The user wants to: Find the population of Tokyo and compare it to New York

  2. PLAN: What steps are needed?
     -> Step 1: Search for the information
     -> Step 2: Process the results
     -> Step 3: Format and present the answer

  3. DECIDE: Which tool should I use first?
     -> I should use: web_search
     -> Because: It will give me the information I need

  4. EXECUTE: Call the selected tool
```

### Pillar 3: Autonomy

Autonomy refers to how much the agent can do without human intervention:

```
+---------------------------------------------------------------+
|              LEVELS OF AUTONOMY                               |
+---------------------------------------------------------------+
|                                                               |
|  Level 1: Human-in-the-loop                                   |
|  Agent suggests actions, human approves each one              |
|  Example: "I want to search for X. OK?"                       |
|  Best for: High-stakes tasks (financial, medical)             |
|                                                               |
|  Level 2: Semi-autonomous                                     |
|  Agent acts freely for safe tasks, asks for risky ones        |
|  Example: Searches freely, asks before sending emails         |
|  Best for: General business tasks                             |
|                                                               |
|  Level 3: Fully autonomous                                    |
|  Agent acts without any human approval                        |
|  Example: Monitors systems and fixes issues automatically     |
|  Best for: Well-defined, low-risk, repetitive tasks           |
|                                                               |
+---------------------------------------------------------------+
```

---

## 23.3 The Agent Loop: Observe, Think, Act

### The Core Loop

Every agent follows the same fundamental loop:

```
+---------------------------------------------------------------+
|              THE AGENT LOOP                                   |
+---------------------------------------------------------------+
|                                                               |
|                  +----------+                                 |
|                  |  START   |                                 |
|                  +----+-----+                                 |
|                       |                                       |
|                       v                                       |
|              +--------+--------+                              |
|              |    OBSERVE      |  <-- Look at the current     |
|              |                 |      situation (user input,   |
|              +---------+-------+      tool results, etc.)     |
|                        |                                      |
|                        v                                      |
|              +---------+-------+                              |
|              |     THINK       |  <-- Reason about what to    |
|              |                 |      do next                  |
|              +---------+-------+                              |
|                        |                                      |
|                        v                                      |
|              +---------+-------+                              |
|         +--->|      ACT        |  <-- Take an action (call    |
|         |    |                 |      a tool or respond)       |
|         |    +---------+-------+                              |
|         |              |                                      |
|         |              v                                      |
|         |    +---------+-------+                              |
|         |    |  GOAL REACHED?  |                              |
|         |    +---+----------+--+                              |
|         |        |          |                                 |
|         |       NO         YES                                |
|         |        |          |                                 |
|         +--------+          v                                 |
|                        +----+-----+                           |
|                        |   DONE   |                           |
|                        +----------+                           |
|                                                               |
+---------------------------------------------------------------+
```

```python
# Implementing a simple agent loop

class SimpleAgent:
    """A minimal agent that demonstrates the observe-think-act loop."""

    def __init__(self, tools):
        self.tools = tools
        self.history = []
        self.max_steps = 5  # Safety limit

    def observe(self, observation):
        """Record an observation."""
        self.history.append({"type": "observation", "content": observation})
        print(f"  OBSERVE: {observation}")

    def think(self, observation):
        """Decide what to do next based on the observation."""
        # In a real agent, this would call an LLM
        # Here we use simple rules for demonstration

        if "weather" in observation.lower() and "result:" not in observation.lower():
            thought = "I need to check the weather. Let me use the weather_tool."
            action = ("weather_tool", {"city": "New York"})
        elif "result:" in observation.lower():
            thought = "I have the result. Let me formulate my response."
            action = ("respond", {"text": f"Based on my research: {observation}"})
        else:
            thought = "I have enough information to respond."
            action = ("respond", {"text": "I can help with that!"})

        self.history.append({"type": "thought", "content": thought})
        print(f"  THINK:   {thought}")
        return action

    def act(self, action_name, action_params):
        """Execute an action."""
        if action_name == "respond":
            print(f"  ACT:     Responding to user")
            print(f"  RESULT:  {action_params['text']}")
            return action_params["text"], True  # True means done

        elif action_name in self.tools:
            print(f"  ACT:     Calling {action_name}({action_params})")
            result = self.tools[action_name](**action_params)
            print(f"  RESULT:  {result}")
            return result, False  # False means not done yet

        else:
            print(f"  ACT:     Unknown tool: {action_name}")
            return "Error: tool not found", False

    def run(self, user_input):
        """Run the agent loop until the goal is reached."""
        print(f"\nUSER: {user_input}")
        print("-" * 50)

        observation = user_input
        for step in range(self.max_steps):
            print(f"\n--- Step {step + 1} ---")
            self.observe(observation)
            action_name, action_params = self.think(observation)
            result, done = self.act(action_name, action_params)

            if done:
                print("\n--- Agent finished ---")
                return result

            observation = f"Result: {result}"

        print("\n--- Max steps reached ---")
        return "Could not complete the task in time."


# Define a simple tool
def weather_tool(city):
    """Simulated weather lookup."""
    weather_data = {
        "New York": "72F, Sunny",
        "London": "58F, Cloudy",
        "Tokyo": "68F, Partly Cloudy",
    }
    return weather_data.get(city, "Weather data not available")

# Create and run the agent
agent = SimpleAgent(tools={"weather_tool": weather_tool})
agent.run("What is the weather in New York?")
```

**Expected output:**

```
USER: What is the weather in New York?
--------------------------------------------------

--- Step 1 ---
  OBSERVE: What is the weather in New York?
  THINK:   I need to check the weather. Let me use the weather_tool.
  ACT:     Calling weather_tool({'city': 'New York'})
  RESULT:  72F, Sunny

--- Step 2 ---
  OBSERVE: Result: 72F, Sunny
  THINK:   I have the result. Let me formulate my response.
  ACT:     Responding to user
  RESULT:  Based on my research: Result: 72F, Sunny

--- Agent finished ---
```

**Line-by-line explanation:**

- `SimpleAgent.__init__` -- The agent stores available tools and keeps a history of observations, thoughts, and actions
- `observe()` -- Records what the agent sees (user input or tool results)
- `think()` -- Decides what to do next. In a real agent, this calls an LLM. Here we use simple if-else rules
- `act()` -- Executes the chosen action. Either calls a tool or generates a response
- `run()` -- The main loop. It keeps going until the agent decides it is done or hits the maximum number of steps
- The safety limit (`max_steps=5`) prevents infinite loops

---

## 23.4 Real-World Agent Examples

### Example 1: Research Agent

```
+---------------------------------------------------------------+
|              RESEARCH AGENT                                   |
+---------------------------------------------------------------+
|                                                               |
|  User: "Write a summary of the latest AI safety research"    |
|                                                               |
|  Step 1: THINK - I need to find recent papers on AI safety    |
|  Step 2: ACT   - web_search("AI safety research 2024")       |
|  Step 3: OBSERVE - Found 10 relevant papers                   |
|  Step 4: THINK - Let me read the top 3 papers                |
|  Step 5: ACT   - read_webpage(paper_1_url)                   |
|  Step 6: ACT   - read_webpage(paper_2_url)                   |
|  Step 7: ACT   - read_webpage(paper_3_url)                   |
|  Step 8: THINK - I have enough info to write a summary       |
|  Step 9: ACT   - Generate summary                             |
|  Step 10: RESPOND - Here is your summary...                   |
|                                                               |
+---------------------------------------------------------------+
```

### Example 2: Data Analysis Agent

```
+---------------------------------------------------------------+
|              DATA ANALYSIS AGENT                              |
+---------------------------------------------------------------+
|                                                               |
|  User: "Analyze our Q3 sales data and create a report"       |
|                                                               |
|  Step 1: ACT   - database_query("SELECT * FROM sales         |
|                                  WHERE quarter='Q3'")         |
|  Step 2: OBSERVE - Got 15,000 rows of sales data              |
|  Step 3: ACT   - code_executor(pandas analysis code)         |
|  Step 4: OBSERVE - Key metrics calculated                     |
|  Step 5: ACT   - code_executor(matplotlib chart code)        |
|  Step 6: OBSERVE - Charts generated                           |
|  Step 7: ACT   - Generate report text                         |
|  Step 8: RESPOND - Report with charts and insights            |
|                                                               |
+---------------------------------------------------------------+
```

### Example 3: Customer Support Agent

```python
# Simulating a customer support agent workflow

def simulate_support_agent():
    """Demonstrate how a customer support agent would handle a request."""

    print("=" * 60)
    print("CUSTOMER SUPPORT AGENT SIMULATION")
    print("=" * 60)

    user_message = "I ordered product #12345 last week and it hasn't arrived yet."

    steps = [
        {
            "phase": "OBSERVE",
            "detail": f"Customer says: {user_message}",
        },
        {
            "phase": "THINK",
            "detail": "Customer is asking about order #12345. I need to look up the order status.",
        },
        {
            "phase": "ACT",
            "detail": "Calling order_lookup(order_id='12345')",
        },
        {
            "phase": "OBSERVE",
            "detail": "Order #12345: Shipped on March 18, tracking #TR789, currently in transit, expected delivery March 21",
        },
        {
            "phase": "THINK",
            "detail": "The order is in transit. Today is March 20, so it should arrive tomorrow. Let me check if there are any delays.",
        },
        {
            "phase": "ACT",
            "detail": "Calling shipping_tracker(tracking='TR789')",
        },
        {
            "phase": "OBSERVE",
            "detail": "Package is at local distribution center, no delays reported",
        },
        {
            "phase": "THINK",
            "detail": "Good news -- the package is on track. I can reassure the customer.",
        },
        {
            "phase": "ACT",
            "detail": "Generating response to customer",
        },
        {
            "phase": "RESPOND",
            "detail": "Your order #12345 was shipped on March 18 and is currently at your local distribution center. It is expected to arrive tomorrow, March 21. Tracking number: TR789.",
        },
    ]

    for i, step in enumerate(steps, 1):
        print(f"\n  Step {i} [{step['phase']}]:")
        print(f"    {step['detail']}")

simulate_support_agent()
```

**Expected output:**

```
============================================================
CUSTOMER SUPPORT AGENT SIMULATION
============================================================

  Step 1 [OBSERVE]:
    Customer says: I ordered product #12345 last week and it hasn't arrived yet.

  Step 2 [THINK]:
    Customer is asking about order #12345. I need to look up the order status.

  Step 3 [ACT]:
    Calling order_lookup(order_id='12345')

  Step 4 [OBSERVE]:
    Order #12345: Shipped on March 18, tracking #TR789, currently in transit, expected delivery March 21

  Step 5 [THINK]:
    The order is in transit. Today is March 20, so it should arrive tomorrow. Let me check if there are any delays.

  Step 6 [ACT]:
    Calling shipping_tracker(tracking='TR789')

  Step 7 [OBSERVE]:
    Package is at local distribution center, no delays reported

  Step 8 [THINK]:
    Good news -- the package is on track. I can reassure the customer.

  Step 9 [ACT]:
    Generating response to customer

  Step 10 [RESPOND]:
    Your order #12345 was shipped on March 18 and is currently at your local distribution center. It is expected to arrive tomorrow, March 21. Tracking number: TR789.
```

---

## 23.5 Types of Agents

### Type 1: ReAct Agents (Reasoning + Acting)

ReAct is the most popular agent pattern. The name comes from combining "Reasoning" and "Acting." The agent alternates between reasoning about the problem and taking actions:

```
+---------------------------------------------------------------+
|              ReAct PATTERN                                    |
+---------------------------------------------------------------+
|                                                               |
|  Question: What is the population of the capital of France?   |
|                                                               |
|  Thought 1: I need to find the capital of France first.       |
|  Action 1:  search("capital of France")                       |
|  Result 1:  The capital of France is Paris.                    |
|                                                               |
|  Thought 2: Now I need to find the population of Paris.       |
|  Action 2:  search("population of Paris")                     |
|  Result 2:  The population of Paris is about 2.1 million.     |
|                                                               |
|  Thought 3: I have the answer now.                            |
|  Answer:    The capital of France is Paris, with a             |
|             population of about 2.1 million people.           |
|                                                               |
+---------------------------------------------------------------+
```

```python
# Simulating a ReAct agent

class ReActAgent:
    """Agent that follows the ReAct (Reasoning + Acting) pattern."""

    def __init__(self, tools):
        self.tools = tools
        self.trace = []

    def run(self, question):
        """Process a question using the ReAct loop."""
        print(f"Question: {question}\n")

        # In a real agent, an LLM generates these steps
        # Here we simulate the process

        # Step 1: Reason and act
        thought1 = "I need to find the capital of France."
        action1 = "search"
        action_input1 = "capital of France"

        self.trace.append(f"Thought: {thought1}")
        self.trace.append(f"Action: {action1}({action_input1})")

        result1 = self.tools[action1](action_input1)
        self.trace.append(f"Observation: {result1}")

        # Step 2: Reason and act again
        thought2 = "The capital is Paris. Now I need its population."
        action2 = "search"
        action_input2 = "population of Paris"

        self.trace.append(f"Thought: {thought2}")
        self.trace.append(f"Action: {action2}({action_input2})")

        result2 = self.tools[action2](action_input2)
        self.trace.append(f"Observation: {result2}")

        # Step 3: Final reasoning
        thought3 = "I now have all the information I need."
        answer = "The capital of France is Paris, with a population of about 2.1 million."
        self.trace.append(f"Thought: {thought3}")
        self.trace.append(f"Answer: {answer}")

        # Print the full trace
        for entry in self.trace:
            print(f"  {entry}")

        return answer


# Simulated search tool
def mock_search(query):
    results = {
        "capital of France": "Paris is the capital of France.",
        "population of Paris": "The population of Paris is approximately 2.1 million (city proper).",
    }
    return results.get(query, "No results found.")


agent = ReActAgent(tools={"search": mock_search})
agent.run("What is the population of the capital of France?")
```

**Expected output:**

```
Question: What is the population of the capital of France?

  Thought: I need to find the capital of France.
  Action: search(capital of France)
  Observation: Paris is the capital of France.
  Thought: The capital is Paris. Now I need its population.
  Action: search(population of Paris)
  Observation: The population of Paris is approximately 2.1 million (city proper).
  Thought: I now have all the information I need.
  Answer: The capital of France is Paris, with a population of about 2.1 million.
```

### Type 2: Plan-and-Execute Agents

This type creates a complete plan first, then executes each step:

```
+---------------------------------------------------------------+
|              PLAN-AND-EXECUTE PATTERN                         |
+---------------------------------------------------------------+
|                                                               |
|  Goal: "Compare Python and JavaScript for web development"    |
|                                                               |
|  PLANNING PHASE:                                              |
|  Plan:                                                        |
|    1. Research Python's web development capabilities           |
|    2. Research JavaScript's web development capabilities       |
|    3. Compare performance benchmarks                           |
|    4. List pros and cons of each                               |
|    5. Write a summary comparison                               |
|                                                               |
|  EXECUTION PHASE:                                             |
|    Execute step 1 --> Results                                  |
|    Execute step 2 --> Results                                  |
|    Execute step 3 --> Results                                  |
|    Execute step 4 --> Results                                  |
|    Execute step 5 --> Final comparison document                |
|                                                               |
+---------------------------------------------------------------+
```

```python
# Simulating a plan-and-execute agent

class PlanAndExecuteAgent:
    """Agent that plans first, then executes each step."""

    def __init__(self, tools):
        self.tools = tools

    def plan(self, goal):
        """Create a plan to achieve the goal."""
        # In a real agent, an LLM generates this plan
        plan = [
            "Search for Python web frameworks",
            "Search for JavaScript web frameworks",
            "Compare the two languages",
            "Write a summary",
        ]
        return plan

    def execute_step(self, step, context):
        """Execute a single step of the plan."""
        # In a real agent, an LLM decides which tool to use
        if "Search" in step:
            query = step.replace("Search for ", "")
            result = self.tools["search"](query)
            return result
        elif "Compare" in step:
            return "Python: Better for data/AI. JavaScript: Better for full-stack web."
        elif "Write" in step:
            return "Both languages are excellent for web development with different strengths."
        return "Step completed."

    def run(self, goal):
        """Plan and execute."""
        print(f"GOAL: {goal}\n")

        # Phase 1: Planning
        print("PLANNING PHASE:")
        plan = self.plan(goal)
        for i, step in enumerate(plan, 1):
            print(f"  Step {i}: {step}")

        # Phase 2: Execution
        print("\nEXECUTION PHASE:")
        context = []
        for i, step in enumerate(plan, 1):
            result = self.execute_step(step, context)
            context.append(result)
            print(f"  Step {i}: {step}")
            print(f"  Result: {result}\n")

        return context[-1]


def mock_search(query):
    return f"Found information about: {query}"

agent = PlanAndExecuteAgent(tools={"search": mock_search})
agent.run("Compare Python and JavaScript for web development")
```

**Expected output:**

```
GOAL: Compare Python and JavaScript for web development

PLANNING PHASE:
  Step 1: Search for Python web frameworks
  Step 2: Search for JavaScript web frameworks
  Step 3: Compare the two languages
  Step 4: Write a summary

EXECUTION PHASE:
  Step 1: Search for Python web frameworks
  Result: Found information about: Python web frameworks

  Step 2: Search for JavaScript web frameworks
  Result: Found information about: JavaScript web frameworks

  Step 3: Compare the two languages
  Result: Python: Better for data/AI. JavaScript: Better for full-stack web.

  Step 4: Write a summary
  Result: Both languages are excellent for web development with different strengths.
```

### Comparing Agent Types

```
+---------------------------------------------------------------+
|              AGENT TYPE COMPARISON                            |
+---------------------------------------------------------------+
|                                                               |
|  ReAct:                                                       |
|  + Flexible, adapts on the fly                                |
|  + Good for exploratory tasks                                 |
|  + Simple to implement                                        |
|  - Can get stuck in loops                                     |
|  - May take unnecessary steps                                 |
|                                                               |
|  Plan-and-Execute:                                            |
|  + More structured and predictable                            |
|  + Better for complex, multi-step tasks                       |
|  + Easier to debug                                            |
|  - Less flexible (plan may become outdated)                   |
|  - Overhead of planning step                                  |
|                                                               |
|  When to use which:                                           |
|  - Simple questions --> ReAct                                 |
|  - Complex projects --> Plan-and-Execute                      |
|  - Unknown territory --> ReAct (more adaptive)                |
|  - Well-defined tasks --> Plan-and-Execute (more efficient)   |
|                                                               |
+---------------------------------------------------------------+
```

---

## 23.6 The Anatomy of an Agent Prompt

For an LLM to act as an agent, it needs a carefully crafted system prompt:

```python
# Example agent system prompt

agent_system_prompt = """You are a helpful AI assistant with access to the following tools:

1. search(query: str) -> str
   Search the web for information. Returns relevant search results.

2. calculator(expression: str) -> float
   Evaluate a mathematical expression. Returns the result.

3. get_weather(city: str) -> str
   Get the current weather for a city. Returns temperature and conditions.

When answering questions, follow this process:

1. THINK about what information you need
2. Decide which TOOL to use (if any)
3. Call the tool using this format:
   Action: tool_name
   Action Input: the input to the tool
4. OBSERVE the result
5. Repeat steps 1-4 if you need more information
6. When you have enough information, provide your FINAL ANSWER

Always think step by step. If a tool returns an error, try a different approach.

Example:
Question: What is 15% of the current temperature in Paris?

Thought: I need to find the current temperature in Paris first.
Action: get_weather
Action Input: Paris
Observation: 68F, Partly Cloudy

Thought: Now I need to calculate 15% of 68.
Action: calculator
Action Input: 0.15 * 68
Observation: 10.2

Thought: I have my answer.
Final Answer: 15% of the current temperature in Paris (68F) is 10.2F.
"""

print("Agent System Prompt")
print("=" * 60)
print(agent_system_prompt)
```

**Line-by-line explanation:**

- The prompt starts by listing available tools with their signatures and descriptions
- It then provides a step-by-step process for the agent to follow
- The format for tool calls (`Action:` and `Action Input:`) gives the LLM a consistent pattern to follow
- An example shows the agent how to chain multiple tool calls together
- This prompt structure is the foundation of how frameworks like LangChain and LlamaIndex build agents

---

## 23.7 Agent Safety and Limitations

### Common Failure Modes

```
+---------------------------------------------------------------+
|              AGENT FAILURE MODES                              |
+---------------------------------------------------------------+
|                                                               |
|  1. Infinite Loops                                            |
|     Agent keeps calling the same tool repeatedly              |
|     Solution: Set a maximum number of steps                   |
|                                                               |
|  2. Wrong Tool Selection                                      |
|     Agent uses calculator when it should search               |
|     Solution: Better tool descriptions, few-shot examples     |
|                                                               |
|  3. Hallucinated Tool Calls                                   |
|     Agent tries to use a tool that does not exist             |
|     Solution: Validate tool names before execution            |
|                                                               |
|  4. Context Window Overflow                                   |
|     Too many steps fill up the context window                 |
|     Solution: Summarize history, limit step count             |
|                                                               |
|  5. Dangerous Actions                                         |
|     Agent deletes files or sends emails it should not         |
|     Solution: Require human approval for risky actions        |
|                                                               |
+---------------------------------------------------------------+
```

```python
# Implementing safety measures for an agent

class SafeAgent:
    """An agent with built-in safety measures."""

    def __init__(self, tools, max_steps=10, dangerous_tools=None):
        self.tools = tools
        self.max_steps = max_steps
        self.dangerous_tools = dangerous_tools or []
        self.steps_taken = 0

    def call_tool(self, tool_name, tool_input):
        """Call a tool with safety checks."""

        # Safety check 1: Does the tool exist?
        if tool_name not in self.tools:
            print(f"  SAFETY: Tool '{tool_name}' does not exist. Skipping.")
            return None

        # Safety check 2: Is this a dangerous tool?
        if tool_name in self.dangerous_tools:
            print(f"  SAFETY: '{tool_name}' requires human approval.")
            approval = input(f"  Allow '{tool_name}({tool_input})'? (yes/no): ")
            if approval.lower() != "yes":
                print(f"  SAFETY: Action denied by user.")
                return None

        # Safety check 3: Have we exceeded the step limit?
        self.steps_taken += 1
        if self.steps_taken > self.max_steps:
            print(f"  SAFETY: Maximum steps ({self.max_steps}) reached. Stopping.")
            return None

        # Execute the tool
        result = self.tools[tool_name](tool_input)
        print(f"  EXECUTED: {tool_name}({tool_input}) -> {result}")
        return result


# Example usage
safe_agent = SafeAgent(
    tools={
        "search": lambda q: f"Results for: {q}",
        "delete_file": lambda f: f"Deleted: {f}",
    },
    max_steps=5,
    dangerous_tools=["delete_file"],
)

print("Safe tool call:")
safe_agent.call_tool("search", "Python tutorials")

print("\nNon-existent tool:")
safe_agent.call_tool("fly_to_moon", "NASA")
```

**Expected output:**

```
Safe tool call:
  EXECUTED: search(Python tutorials) -> Results for: Python tutorials

Non-existent tool:
  SAFETY: Tool 'fly_to_moon' does not exist. Skipping.
```

---

## 23.8 When to Use Agents vs Simple Prompts

```
+---------------------------------------------------------------+
|              AGENTS vs SIMPLE PROMPTS                         |
+---------------------------------------------------------------+
|                                                               |
|  Use a Simple Prompt when:                                    |
|  - The answer is in the LLM's training data                  |
|  - No external data is needed                                 |
|  - The task is straightforward (summarize, translate, etc.)   |
|  - Speed is critical (agents add latency)                     |
|  - Cost must be minimized (agents use more tokens)            |
|                                                               |
|  Use an Agent when:                                           |
|  - Real-time data is needed (weather, stock prices)           |
|  - Multiple steps are required                                |
|  - External tools are needed (search, code, databases)        |
|  - The task requires exploration and adaptation               |
|  - The answer depends on information the LLM does not have    |
|                                                               |
|  Cost comparison:                                             |
|  Simple prompt: 1 LLM call     = ~$0.01                      |
|  Agent:         5-15 LLM calls = ~$0.05-0.15                 |
|                                                               |
+---------------------------------------------------------------+
```

---

## Common Mistakes

1. **Making agents too autonomous** -- Giving an agent the ability to delete files, send emails, or make purchases without human approval is dangerous. Always add safety checks for risky actions.

2. **No step limit** -- Without a maximum number of steps, an agent can get stuck in an infinite loop, consuming tokens and money endlessly.

3. **Vague tool descriptions** -- If the tool descriptions in the system prompt are unclear, the LLM will choose the wrong tool or make up tool calls.

4. **Using agents for simple tasks** -- Not every task needs an agent. If you just need to summarize text, a simple prompt is faster, cheaper, and more reliable.

5. **Ignoring context window limits** -- Each step adds to the conversation history. Long agent sessions can exceed the context window, causing the agent to forget earlier steps.

---

## Best Practices

1. **Start with fewer tools** -- Give the agent only the tools it needs. More tools mean more chances for the LLM to pick the wrong one.

2. **Write clear tool descriptions** -- Describe each tool's purpose, input format, and what it returns. Include examples.

3. **Set step limits** -- Always set a maximum number of steps (10-20 is usually enough).

4. **Log everything** -- Record every thought, action, and observation. This makes debugging much easier.

5. **Test with simple tasks first** -- Before giving an agent complex goals, verify it works correctly on simple, predictable tasks.

6. **Require approval for dangerous actions** -- Any action that modifies data, sends messages, or costs money should require human approval.

---

## Quick Summary

AI agents combine an LLM's reasoning ability with external tools and autonomy to accomplish complex tasks. Unlike chatbots that only generate text, agents can search the web, run code, query databases, and take actions in the real world. The core agent loop follows three steps: observe the current situation, think about what to do next, and act by calling a tool or generating a response. The two main agent patterns are ReAct (interleaving reasoning and acting) and plan-and-execute (creating a full plan, then executing it). Safety measures like step limits and human approval for dangerous actions are essential for reliable agent systems.

---

## Key Points

- An **agent** combines an LLM with tools, reasoning, and autonomy
- **Chatbots** only generate text; **agents** can take actions in the world
- The **agent loop** follows observe, think, act steps repeated until the goal is achieved
- **Tools** are functions the agent can call (search, calculate, code, database, etc.)
- **ReAct** agents interleave reasoning and acting -- flexible and adaptive
- **Plan-and-execute** agents create a plan first, then execute steps -- structured and predictable
- **Safety measures** include step limits, tool validation, and human approval for risky actions
- Agents are more expensive and slower than simple prompts but can handle complex, multi-step tasks
- Always **log agent traces** for debugging and transparency
- Start simple: fewer tools, short tasks, human-in-the-loop

---

## Practice Questions

1. Explain the difference between a chatbot and an AI agent using a real-world analogy that was not used in this chapter.

2. You are building an agent for a customer service team. What tools would you give it? Which actions should require human approval?

3. A ReAct agent gets stuck in a loop, alternating between searching for "Python tutorials" and "Python courses" without making progress. What is going wrong and how would you fix it?

4. Compare the ReAct and plan-and-execute patterns. For each of the following tasks, which pattern would you choose and why? (a) Answering a factual question. (b) Writing a 10-page research report. (c) Debugging a piece of code.

5. An agent has access to a tool that can delete database records. What safety measures should be in place before this tool is used?

---

## Exercises

### Exercise 1: Build a ReAct Agent

Extend the `ReActAgent` class from this chapter. Add a `calculator` tool and a `wikipedia` tool (simulated with a dictionary). Test it with the question: "What is the square root of the population of Tokyo?"

### Exercise 2: Safety Audit

Review the `SafeAgent` class. Add three more safety features: (a) rate limiting (no more than 3 tool calls per minute), (b) input validation (reject inputs longer than 1000 characters), (c) output logging (save all actions to a log file).

### Exercise 3: Agent Comparison

Write two agents that answer the same question ("What is the tallest building in the world and how tall is it in meters?") -- one using the ReAct pattern and one using the plan-and-execute pattern. Compare the number of steps, tool calls, and quality of the final answer.

---

## What Is Next?

Now that you understand what agents are and how they think, Chapter 24 dives into the technical mechanism that makes agents possible: **function calling and tool use**. You will learn how LLMs are taught to generate structured tool calls, how to define tools using JSON schemas, and how to build a complete tool-use pipeline from scratch.
