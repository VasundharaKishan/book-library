# Chapter 26: Multi-Agent Systems

## What You Will Learn

In this chapter, you will learn:

- Why a single agent is not enough for complex tasks
- How multiple agents can collaborate like a team of specialists
- Common orchestration patterns for multi-agent systems
- How to use CrewAI to define agents with specific roles
- How task delegation works between agents
- How to build a complete multi-agent workflow with a researcher, writer, and editor

## Why This Chapter Matters

Think about how a newspaper works. A single journalist does not do everything. There is a reporter who gathers facts, a writer who drafts the story, an editor who polishes the language, and a fact-checker who verifies claims. Each person is a specialist, and together they produce a high-quality article faster and better than any one person could alone.

Multi-agent systems bring this same idea to AI. Instead of one overloaded agent trying to do everything, you create a team of specialized agents. Each agent has a clear role, specific skills, and a defined scope of responsibility. They pass work between each other, just like a real team.

This is the most advanced and powerful pattern for building AI applications today. It is used in production systems for customer support, content creation, software development, and research.

---

## 26.1 Why Multiple Agents?

### The Limitations of a Single Agent

```
+---------------------------------------------------------------+
|              SINGLE AGENT vs MULTI-AGENT                      |
+---------------------------------------------------------------+
|                                                               |
|  SINGLE AGENT:                                                |
|  +------------------------------------------+                |
|  |  One agent tries to:                     |                |
|  |  - Research the topic                     |                |
|  |  - Write the content                     |                |
|  |  - Check for errors                      |                |
|  |  - Format the output                     |                |
|  |  - Verify facts                          |                |
|  |                                          |                |
|  |  Problems:                               |                |
|  |  - Context window fills up fast          |                |
|  |  - Quality drops as task gets complex    |                |
|  |  - Hard to debug which step failed       |                |
|  +------------------------------------------+                |
|                                                               |
|  MULTI-AGENT TEAM:                                            |
|  +------------+  +------------+  +------------+              |
|  | Researcher |->|   Writer   |->|   Editor   |              |
|  |            |  |            |  |            |              |
|  | Finds      |  | Drafts     |  | Polishes   |              |
|  | facts      |  | content    |  | quality    |              |
|  +------------+  +------------+  +------------+              |
|                                                               |
|  Benefits:                                                    |
|  - Each agent has a focused role                              |
|  - Smaller context per agent                                  |
|  - Easy to debug (check each agent separately)               |
|  - Better quality through specialization                      |
|                                                               |
+---------------------------------------------------------------+
```

```python
# Demonstrating why multi-agent systems are better

def single_agent_approach(topic):
    """Simulate a single agent handling everything."""
    print("=== Single Agent Approach ===")
    print(f"Topic: {topic}\n")

    steps = [
        "Searching for information... (using 2000 tokens)",
        "Processing search results... (using 1500 tokens)",
        "Writing the article... (using 3000 tokens)",
        "Editing for grammar... (using 1000 tokens)",
        "Checking facts... (using 1500 tokens)",
        "Formatting output... (using 500 tokens)",
    ]

    total_tokens = 0
    for step in steps:
        tokens = int(step.split("(using ")[1].split(" ")[0])
        total_tokens += tokens
        print(f"  Step: {step}")

    print(f"\n  Total tokens used: {total_tokens}")
    print(f"  Context window pressure: HIGH")
    print(f"  Risk of forgetting early context: HIGH")


def multi_agent_approach(topic):
    """Simulate a multi-agent team handling the same task."""
    print("\n=== Multi-Agent Approach ===")
    print(f"Topic: {topic}\n")

    agents = {
        "Researcher": ["Search for info (2000 tokens)", "Process results (1500 tokens)"],
        "Writer": ["Draft article from research notes (2000 tokens)"],
        "Editor": ["Polish grammar and style (1000 tokens)", "Verify facts (1000 tokens)"],
    }

    for agent_name, tasks in agents.items():
        agent_tokens = 0
        print(f"  Agent: {agent_name}")
        for task in tasks:
            tokens = int(task.split("(")[1].split(" ")[0])
            agent_tokens += tokens
            print(f"    - {task}")
        print(f"    Total: {agent_tokens} tokens (fresh context)\n")

    print(f"  Each agent gets a FRESH context window")
    print(f"  Risk of forgetting context: LOW")
    print(f"  Easier to debug: YES (check each agent)")


single_agent_approach("The History of Python")
multi_agent_approach("The History of Python")
```

**Expected output:**

```
=== Single Agent Approach ===
Topic: The History of Python

  Step: Searching for information... (using 2000 tokens)
  Step: Processing search results... (using 1500 tokens)
  Step: Writing the article... (using 3000 tokens)
  Step: Editing for grammar... (using 1000 tokens)
  Step: Checking facts... (using 1500 tokens)
  Step: Formatting output... (using 500 tokens)

  Total tokens used: 9500
  Context window pressure: HIGH
  Risk of forgetting early context: HIGH

=== Multi-Agent Approach ===
Topic: The History of Python

  Agent: Researcher
    - Search for info (2000 tokens)
    - Process results (1500 tokens)
    Total: 3500 tokens (fresh context)

  Agent: Writer
    - Draft article from research notes (2000 tokens)
    Total: 2000 tokens (fresh context)

  Agent: Editor
    - Polish grammar and style (1000 tokens)
    - Verify facts (1000 tokens)
    Total: 2000 tokens (fresh context)

  Each agent gets a FRESH context window
  Risk of forgetting context: LOW
  Easier to debug: YES (check each agent)
```

---

## 26.2 Orchestration Patterns

### How Agents Work Together

There are several ways to organize multiple agents:

```
+---------------------------------------------------------------+
|              ORCHESTRATION PATTERNS                            |
+---------------------------------------------------------------+
|                                                               |
|  Pattern 1: SEQUENTIAL (Pipeline)                             |
|  Agent A --> Agent B --> Agent C --> Result                    |
|  Each agent processes the output of the previous one          |
|  Best for: Content creation, data processing pipelines        |
|                                                               |
|  Pattern 2: HIERARCHICAL (Manager + Workers)                  |
|       +--------+                                              |
|       | Manager|                                              |
|       +---+----+                                              |
|           |                                                   |
|     +-----+-----+                                             |
|     |     |     |                                             |
|  Agent  Agent  Agent                                          |
|    A      B      C                                            |
|  Manager delegates tasks and combines results                 |
|  Best for: Complex projects, research tasks                   |
|                                                               |
|  Pattern 3: COLLABORATIVE (Peer-to-Peer)                      |
|  Agent A <--> Agent B                                         |
|     ^            ^                                            |
|     |            |                                            |
|     +---> Agent C                                             |
|  Agents discuss and iterate on results                        |
|  Best for: Brainstorming, problem-solving, debugging          |
|                                                               |
+---------------------------------------------------------------+
```

```python
# Demonstrating the three orchestration patterns

class SimpleAgent:
    def __init__(self, name, role):
        self.name = name
        self.role = role

    def process(self, input_text):
        """Simulate agent processing."""
        return f"[{self.name}] Processed: {input_text[:50]}..."


# Pattern 1: Sequential
def sequential_pipeline(task):
    """Agents process one after another like an assembly line."""
    print("=== SEQUENTIAL PIPELINE ===\n")

    researcher = SimpleAgent("Researcher", "Gather information")
    writer = SimpleAgent("Writer", "Draft content")
    editor = SimpleAgent("Editor", "Polish and verify")

    # Each agent takes the previous agent's output
    step1 = f"Research findings about: {task}"
    print(f"  Step 1: Researcher -> {step1}")

    step2 = f"Draft article based on: {step1}"
    print(f"  Step 2: Writer -> {step2[:60]}...")

    step3 = f"Polished version of: {step2[:30]}..."
    print(f"  Step 3: Editor -> {step3}")

    return step3


# Pattern 2: Hierarchical
def hierarchical_system(task):
    """A manager agent delegates to worker agents."""
    print("\n=== HIERARCHICAL SYSTEM ===\n")

    subtasks = {
        "Researcher": "Find key facts and statistics",
        "Writer": "Write introduction and body paragraphs",
        "Fact Checker": "Verify all claims against sources",
    }

    print(f"  Manager receives task: {task}")
    print(f"  Manager breaks it into subtasks:\n")

    results = {}
    for agent_name, subtask in subtasks.items():
        print(f"    Delegating to {agent_name}: {subtask}")
        results[agent_name] = f"Completed: {subtask}"

    print(f"\n  Manager combines all results into final output")
    return results


# Pattern 3: Collaborative
def collaborative_system(task):
    """Agents discuss and iterate together."""
    print("\n=== COLLABORATIVE SYSTEM ===\n")

    rounds = [
        ("Agent A", "Here is my initial idea for the solution..."),
        ("Agent B", "I agree with part of it, but I think we should also consider..."),
        ("Agent A", "Good point. Let me revise my approach..."),
        ("Agent B", "That looks better. One more suggestion..."),
        ("Agent A", "Perfect. Here is the final version incorporating all feedback."),
    ]

    print(f"  Task: {task}\n")
    for agent, message in rounds:
        print(f"  {agent}: {message}")

    print(f"\n  Consensus reached after {len(rounds)} exchanges")


# Run all patterns
sequential_pipeline("History of Python")
hierarchical_system("Write a research report on AI safety")
collaborative_system("Debug a complex algorithm")
```

**Expected output:**

```
=== SEQUENTIAL PIPELINE ===

  Step 1: Researcher -> Research findings about: History of Python
  Step 2: Writer -> Draft article based on: Research findings about: History...
  Step 3: Editor -> Polished version of: Draft article based on: R...

=== HIERARCHICAL SYSTEM ===

  Manager receives task: Write a research report on AI safety
  Manager breaks it into subtasks:

    Delegating to Researcher: Find key facts and statistics
    Delegating to Writer: Write introduction and body paragraphs
    Delegating to Fact Checker: Verify all claims against sources

  Manager combines all results into final output

=== COLLABORATIVE SYSTEM ===

  Task: Debug a complex algorithm

  Agent A: Here is my initial idea for the solution...
  Agent B: I agree with part of it, but I think we should also consider...
  Agent A: Good point. Let me revise my approach...
  Agent B: That looks better. One more suggestion...
  Agent A: Perfect. Here is the final version incorporating all feedback.

  Consensus reached after 5 exchanges
```

---

## 26.3 Introduction to CrewAI

### What Is CrewAI?

CrewAI is a framework designed specifically for building multi-agent systems. It uses intuitive concepts:

```
+---------------------------------------------------------------+
|              CrewAI CONCEPTS                                  |
+---------------------------------------------------------------+
|                                                               |
|  AGENT = A team member with a specific role and skills        |
|    - Has a role (e.g., "Senior Researcher")                   |
|    - Has a goal (e.g., "Find accurate information")           |
|    - Has a backstory (personality and expertise)              |
|    - Has tools it can use                                     |
|                                                               |
|  TASK = A specific piece of work to be done                   |
|    - Has a description (what to do)                           |
|    - Has an expected output (what to produce)                 |
|    - Is assigned to an agent                                  |
|                                                               |
|  CREW = A team of agents working on tasks                     |
|    - Contains agents and tasks                                |
|    - Defines the execution order (sequential or hierarchical) |
|    - Manages communication between agents                     |
|                                                               |
|  Analogy:                                                     |
|  Agent = Employee     (has a job title and skills)            |
|  Task  = Work order   (describes what needs to be done)       |
|  Crew  = Team         (group of employees working together)   |
|                                                               |
+---------------------------------------------------------------+
```

### Installation

```python
# Install CrewAI
# pip install crewai crewai-tools

# You also need an LLM API key
# export OPENAI_API_KEY="your-key-here"
```

---

## 26.4 Defining Agents with Roles

### Creating Specialized Agents

```python
from crewai import Agent

# Agent 1: The Researcher
researcher = Agent(
    role="Senior Research Analyst",
    goal="Find accurate, comprehensive information on the given topic",
    backstory="""You are an experienced research analyst with 15 years
    of experience. You are known for your thorough research, attention
    to detail, and ability to find information from multiple sources.
    You always verify facts from at least two sources before reporting them.""",
    verbose=True,        # Print the agent's reasoning
    allow_delegation=False,  # This agent works alone
)

# Agent 2: The Writer
writer = Agent(
    role="Content Writer",
    goal="Write clear, engaging, and informative articles based on research",
    backstory="""You are a skilled content writer who specializes in
    making complex topics accessible to a general audience. You use
    analogies, examples, and clear structure to explain difficult concepts.
    You always write in an engaging, conversational tone.""",
    verbose=True,
    allow_delegation=False,
)

# Agent 3: The Editor
editor = Agent(
    role="Senior Editor",
    goal="Ensure content is accurate, well-structured, and error-free",
    backstory="""You are a meticulous editor with expertise in technical
    content. You check for factual accuracy, grammatical errors, unclear
    passages, and logical flow. You provide specific, actionable feedback
    and always improve the content you review.""",
    verbose=True,
    allow_delegation=False,
)

# Display agent information
agents = [researcher, writer, editor]
print("Team Members:")
print("=" * 60)
for agent in agents:
    print(f"\n  Role: {agent.role}")
    print(f"  Goal: {agent.goal}")
    print(f"  Backstory: {agent.backstory[:80]}...")
```

**Expected output:**

```
Team Members:
============================================================

  Role: Senior Research Analyst
  Goal: Find accurate, comprehensive information on the given topic
  Backstory: You are an experienced research analyst with 15 years
    of experience. You a...

  Role: Content Writer
  Goal: Write clear, engaging, and informative articles based on research
  Backstory: You are a skilled content writer who specializes in
    making complex topics ...

  Role: Senior Editor
  Goal: Ensure content is accurate, well-structured, and error-free
  Backstory: You are a meticulous editor with expertise in technical
    content. You check...
```

**Line-by-line explanation:**

- `role` -- The agent's job title. This tells the LLM what kind of specialist it is
- `goal` -- What the agent is trying to achieve. This guides the LLM's decision-making
- `backstory` -- A personality and expertise description. The more detailed the backstory, the more consistent and specialized the agent's behavior
- `verbose=True` -- Prints the agent's internal reasoning during execution
- `allow_delegation=False` -- When True, the agent can ask other agents for help. When False, it must complete tasks on its own

---

## 26.5 Defining Tasks

### Creating Tasks for Each Agent

```python
from crewai import Task

# Task 1: Research
research_task = Task(
    description="""Research the topic: 'The Impact of AI on Healthcare in 2024'.

    Find and compile:
    1. At least 3 key applications of AI in healthcare
    2. Recent statistics on AI adoption in hospitals
    3. Benefits and challenges of AI in healthcare
    4. Notable examples of AI healthcare products

    Your research should be thorough and include specific facts and figures.""",
    expected_output="""A comprehensive research report with:
    - Key applications of AI in healthcare
    - Statistics on adoption
    - Benefits and challenges
    - Specific examples and case studies""",
    agent=researcher,
)

# Task 2: Write
writing_task = Task(
    description="""Using the research provided, write an engaging article about
    'The Impact of AI on Healthcare in 2024'.

    The article should:
    1. Start with a compelling introduction
    2. Cover all key points from the research
    3. Use analogies to explain technical concepts
    4. Include specific examples and statistics
    5. End with a forward-looking conclusion

    Target audience: General public with no technical background.
    Length: 500-800 words.""",
    expected_output="""A well-written article of 500-800 words that is:
    - Engaging and accessible
    - Factually accurate
    - Well-structured with clear sections
    - Written for a non-technical audience""",
    agent=writer,
)

# Task 3: Edit
editing_task = Task(
    description="""Review and edit the article about AI in Healthcare.

    Check for:
    1. Factual accuracy (flag any unsupported claims)
    2. Grammar and spelling errors
    3. Clarity and readability
    4. Logical flow between sections
    5. Appropriate tone for general audience

    Make corrections directly and provide a final polished version.""",
    expected_output="""The final, polished article with:
    - All errors corrected
    - Improved clarity where needed
    - Verified facts
    - Professional quality ready for publication""",
    agent=editor,
)

# Display tasks
tasks = [research_task, writing_task, editing_task]
print("Tasks:")
print("=" * 60)
for i, task in enumerate(tasks, 1):
    print(f"\n  Task {i}:")
    print(f"  Assigned to: {task.agent.role}")
    print(f"  Description: {task.description[:80]}...")
    print(f"  Expected output: {task.expected_output[:60]}...")
```

**Expected output:**

```
Tasks:
============================================================

  Task 1:
  Assigned to: Senior Research Analyst
  Description: Research the topic: 'The Impact of AI on Healthcare in 2024'.

    Find and com...
  Expected output: A comprehensive research report with:
    - Key applications of ...

  Task 2:
  Assigned to: Content Writer
  Description: Using the research provided, write an engaging article about
    'The Impact of...
  Expected output: A well-written article of 500-800 words that is:
    - Engagi...

  Task 3:
  Assigned to: Senior Editor
  Description: Review and edit the article about AI in Healthcare.

    Check for:
    1. Fac...
  Expected output: The final, polished article with:
    - All errors corrected
...
```

---

## 26.6 Creating and Running a Crew

### Assembling the Team

```python
from crewai import Crew, Process

# Create the crew
crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[research_task, writing_task, editing_task],
    process=Process.sequential,  # Execute tasks one after another
    verbose=True,                # Print detailed execution logs
)

print("Crew assembled:")
print(f"  Agents: {len(crew.agents)}")
print(f"  Tasks: {len(crew.tasks)}")
print(f"  Process: {crew.process}")
print(f"\nExecution order:")
for i, task in enumerate(crew.tasks, 1):
    print(f"  {i}. {task.agent.role}: {task.description[:50]}...")
```

**Expected output:**

```
Crew assembled:
  Agents: 3
  Tasks: 3
  Process: sequential

Execution order:
  1. Senior Research Analyst: Research the topic: 'The Impact of AI on Healthc...
  2. Content Writer: Using the research provided, write an engaging a...
  3. Senior Editor: Review and edit the article about AI in Healthcar...
```

### Running the Crew

```python
# Kick off the crew's work
# result = crew.kickoff()

# In production, this would actually call the LLM for each agent
# Here is what the output would look like:

print("=" * 60)
print("CREW EXECUTION")
print("=" * 60)

execution_log = [
    {
        "agent": "Senior Research Analyst",
        "action": "Searching for AI healthcare applications 2024",
        "result": "Found: AI diagnostics, drug discovery, personalized medicine...",
    },
    {
        "agent": "Senior Research Analyst",
        "action": "Compiling statistics on AI adoption",
        "result": "Found: 67% of hospitals now use some form of AI...",
    },
    {
        "agent": "Senior Research Analyst",
        "action": "Finalizing research report",
        "result": "Complete research report with 4 sections, 12 data points",
    },
    {
        "agent": "Content Writer",
        "action": "Reading research report",
        "result": "Understood. Starting to write the article...",
    },
    {
        "agent": "Content Writer",
        "action": "Writing article",
        "result": "Draft complete: 650 words, 5 sections",
    },
    {
        "agent": "Senior Editor",
        "action": "Reviewing article",
        "result": "Found 3 areas for improvement, 1 factual correction needed",
    },
    {
        "agent": "Senior Editor",
        "action": "Finalizing article",
        "result": "Article polished and ready for publication",
    },
]

for entry in execution_log:
    print(f"\n  [{entry['agent']}]")
    print(f"  Action: {entry['action']}")
    print(f"  Result: {entry['result']}")

print(f"\n{'='*60}")
print("CREW EXECUTION COMPLETE")
print(f"{'='*60}")
```

---

## 26.7 Adding Tools to Agents

### Giving Agents Specialized Tools

```python
from crewai import Agent
from crewai_tools import SerperDevTool, WebsiteSearchTool

# Create tools
# search_tool = SerperDevTool()  # Web search (requires SERPER_API_KEY)
# website_tool = WebsiteSearchTool()  # Search within a specific website

# For demonstration, we create custom tools
from langchain_core.tools import tool

@tool
def search_papers(query: str) -> str:
    """Search for academic papers and research articles on a topic.

    Args:
        query: The research topic to search for
    """
    # Simulated academic search
    papers = {
        "AI healthcare": [
            "Smith et al. (2024): AI-Powered Diagnostics Reduce Error Rates by 40%",
            "Chen et al. (2024): Machine Learning in Drug Discovery: A Review",
            "Johnson et al. (2024): Patient Outcomes with AI-Assisted Surgery",
        ],
    }
    for key, results in papers.items():
        if any(word in query.lower() for word in key.split()):
            return "\n".join(results)
    return f"No papers found for: {query}"


@tool
def check_facts(claim: str) -> str:
    """Verify a factual claim by checking against reliable sources.

    Args:
        claim: The claim to verify
    """
    # Simulated fact checking
    return f"VERIFIED: The claim '{claim[:50]}...' is supported by multiple sources."


# Create agents with tools
researcher_with_tools = Agent(
    role="Senior Research Analyst",
    goal="Find accurate information using academic papers and web search",
    backstory="You are an expert researcher who always uses search tools to find the latest information.",
    tools=[search_papers],  # Give the researcher search capabilities
    verbose=True,
)

editor_with_tools = Agent(
    role="Senior Editor and Fact Checker",
    goal="Verify all claims in the article are factually accurate",
    backstory="You are a meticulous editor who verifies every claim using the fact-checking tool.",
    tools=[check_facts],  # Give the editor fact-checking capabilities
    verbose=True,
)

print("Agents with tools:")
print(f"  Researcher tools: {[t.name for t in researcher_with_tools.tools]}")
print(f"  Editor tools: {[t.name for t in editor_with_tools.tools]}")
```

**Expected output:**

```
Agents with tools:
  Researcher tools: ['search_papers']
  Editor tools: ['check_facts']
```

---

## 26.8 Complete Multi-Agent Workflow

### Full Example: Content Creation Pipeline

```python
from crewai import Agent, Task, Crew, Process
from langchain_core.tools import tool

# ============================================
# Step 1: Define Tools
# ============================================

@tool
def web_search(query: str) -> str:
    """Search the web for current information.

    Args:
        query: What to search for
    """
    mock_results = {
        "python trends 2024": "Python continues to dominate AI/ML. Key trends: AI agents, multimodal AI, smaller language models. Python 3.13 released with performance improvements.",
        "python frameworks 2024": "Top frameworks: FastAPI (web), LangChain (AI), Polars (data), PyTorch (deep learning). Django and Flask remain popular for web development.",
        "python community 2024": "PyCon 2024 attracted record attendance. Python has 15M+ active developers. Key focus areas: AI safety, efficient computing, and developer experience.",
    }
    for key, value in mock_results.items():
        if any(word in query.lower() for word in key.split()):
            return value
    return f"Found general information about: {query}"


@tool
def word_counter(text: str) -> str:
    """Count words in a text and check if it meets length requirements.

    Args:
        text: The text to analyze
    """
    words = len(text.split())
    return f"Word count: {words}. {'Meets 500-word minimum.' if words >= 500 else f'Need {500-words} more words to reach 500.'}"


# ============================================
# Step 2: Define Agents
# ============================================

researcher = Agent(
    role="Technology Research Analyst",
    goal="Compile comprehensive research on Python trends in 2024",
    backstory="""You are a senior technology analyst specializing in
    programming languages and developer ecosystems. You search for
    the latest information and compile organized research briefs
    with facts, statistics, and expert opinions.""",
    tools=[web_search],
    verbose=True,
    allow_delegation=False,
)

writer = Agent(
    role="Technical Content Writer",
    goal="Write an engaging article about Python trends for a developer audience",
    backstory="""You are an experienced technical writer who has written
    for major tech publications. You excel at turning research notes
    into compelling articles. You use clear headings, bullet points,
    code examples when relevant, and a conversational tone. Your articles
    are always well-structured with an introduction, body sections,
    and a conclusion.""",
    verbose=True,
    allow_delegation=False,
)

editor = Agent(
    role="Technical Editor",
    goal="Ensure the article is accurate, well-written, and publication-ready",
    backstory="""You are a detail-oriented technical editor with 10 years
    of experience. You check facts, fix grammar, improve clarity, and
    ensure the article flows logically. You provide the final, polished
    version that is ready for publication.""",
    tools=[word_counter],
    verbose=True,
    allow_delegation=False,
)

# ============================================
# Step 3: Define Tasks
# ============================================

research_task = Task(
    description="""Research 'Python Trends in 2024' thoroughly.

    Cover these areas:
    1. Python's current popularity and market position
    2. Key new features in Python 3.13
    3. Most important Python frameworks and libraries in 2024
    4. The Python community and ecosystem developments
    5. How Python is being used in AI/ML

    Use the web_search tool for each area.
    Compile your findings into a structured research brief.""",
    expected_output="""A structured research brief with sections for each area,
    including specific facts, statistics, and notable examples.""",
    agent=researcher,
)

writing_task = Task(
    description="""Write an engaging article titled 'Python in 2024: What Every Developer Should Know'
    based on the research provided.

    Requirements:
    - 500-800 words
    - Clear introduction that hooks the reader
    - 3-4 main sections with headings
    - Use specific facts and statistics from the research
    - Conclude with predictions for 2025
    - Conversational but professional tone
    - Target audience: intermediate developers""",
    expected_output="""A complete, well-structured article of 500-800 words
    ready for technical review.""",
    agent=writer,
)

editing_task = Task(
    description="""Review and edit the article about Python in 2024.

    Check for:
    1. Word count (must be 500-800 words)
    2. Factual accuracy of all claims
    3. Grammar, spelling, and punctuation
    4. Logical flow between sections
    5. Engaging headline and subheadings
    6. Appropriate tone for developer audience

    Provide the final, publication-ready version of the article.""",
    expected_output="""The final polished article, corrected and ready
    for publication. Include the word count at the end.""",
    agent=editor,
)

# ============================================
# Step 4: Assemble and Run the Crew
# ============================================

content_crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[research_task, writing_task, editing_task],
    process=Process.sequential,
    verbose=True,
)

print("Content Creation Crew")
print("=" * 60)
print(f"Agents: {len(content_crew.agents)}")
for agent in content_crew.agents:
    tools_list = [t.name for t in agent.tools] if agent.tools else ["None"]
    print(f"  - {agent.role} (tools: {', '.join(tools_list)})")
print(f"\nTasks: {len(content_crew.tasks)}")
for i, task in enumerate(content_crew.tasks, 1):
    print(f"  {i}. {task.agent.role}: {task.description[:60]}...")
print(f"\nProcess: {content_crew.process}")
print(f"\nReady to run: crew.kickoff()")

# To actually run:
# result = content_crew.kickoff()
# print(result)
```

**Expected output:**

```
Content Creation Crew
============================================================
Agents: 3
  - Technology Research Analyst (tools: web_search)
  - Technical Content Writer (tools: None)
  - Technical Editor (tools: word_counter)

Tasks: 3
  1. Technology Research Analyst: Research 'Python Trends in 2024' thoroughly.

    Cover thes...
  2. Technical Content Writer: Write an engaging article titled 'Python in 2024: What Every...
  3. Technical Editor: Review and edit the article about Python in 2024.

    Chec...

Process: sequential

Ready to run: crew.kickoff()
```

---

## 26.9 Task Delegation and Dependencies

### How Tasks Pass Information

In a sequential crew, each task's output automatically becomes available to the next task:

```
+---------------------------------------------------------------+
|              INFORMATION FLOW BETWEEN TASKS                   |
+---------------------------------------------------------------+
|                                                               |
|  Task 1 (Research)                                            |
|    Output: "Research brief with facts and statistics"         |
|        |                                                      |
|        v (automatically passed as context)                    |
|  Task 2 (Writing)                                             |
|    Receives: Research brief from Task 1                       |
|    Output: "Draft article based on research"                  |
|        |                                                      |
|        v (automatically passed as context)                    |
|  Task 3 (Editing)                                             |
|    Receives: Draft article from Task 2                        |
|    Output: "Final polished article"                           |
|                                                               |
+---------------------------------------------------------------+
```

### Explicit Task Dependencies

You can also specify explicit dependencies:

```python
from crewai import Task

# Task with explicit context from other tasks
editing_task_v2 = Task(
    description="Edit the article and verify facts against the original research.",
    expected_output="Final polished article",
    agent=editor,
    context=[research_task, writing_task],  # Has access to BOTH previous outputs
)

print("Task with explicit dependencies:")
print(f"  Task: {editing_task_v2.description[:50]}...")
print(f"  Agent: {editing_task_v2.agent.role}")
print(f"  Context from: {len(editing_task_v2.context)} previous tasks")
```

**Expected output:**

```
Task with explicit dependencies:
  Task: Edit the article and verify facts against the or...
  Agent: Technical Editor
  Context from: 2 previous tasks
```

---

## 26.10 Hierarchical Process

### Manager-Worker Pattern

```python
from crewai import Crew, Process

# In hierarchical mode, a manager agent coordinates the workers
hierarchical_crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[research_task, writing_task, editing_task],
    process=Process.hierarchical,  # Manager delegates tasks
    manager_llm="gpt-4o-mini",    # LLM for the manager agent
    verbose=True,
)

print("Hierarchical Crew:")
print(f"  Process: {hierarchical_crew.process}")
print(f"  Manager: Auto-created with GPT-4o-mini")
print(f"  Workers: {[a.role for a in hierarchical_crew.agents]}")
print(f"\n  The manager will:")
print(f"    1. Analyze the overall goal")
print(f"    2. Decide which agent should work on what")
print(f"    3. Review outputs and request revisions if needed")
print(f"    4. Combine results into the final output")
```

**Expected output:**

```
Hierarchical Crew:
  Process: hierarchical
  Manager: Auto-created with GPT-4o-mini
  Workers: ['Technology Research Analyst', 'Technical Content Writer', 'Technical Editor']

  The manager will:
    1. Analyze the overall goal
    2. Decide which agent should work on what
    3. Review outputs and request revisions if needed
    4. Combine results into the final output
```

---

## 26.11 Simulating a Full Run

```python
# Complete simulation of a multi-agent content creation workflow

def simulate_crew_execution():
    """Simulate what happens when a crew runs."""

    print("=" * 60)
    print("  MULTI-AGENT CONTENT CREATION: FULL SIMULATION")
    print("=" * 60)

    # Phase 1: Research
    print("\n--- PHASE 1: RESEARCH ---")
    print("[Research Analyst] Starting research on Python Trends 2024...")
    print("[Research Analyst] Action: web_search('python trends 2024')")
    print("[Research Analyst] Result: Python dominates AI/ML, 3.13 released...")
    print("[Research Analyst] Action: web_search('python frameworks 2024')")
    print("[Research Analyst] Result: FastAPI, LangChain, Polars trending...")
    print("[Research Analyst] Action: web_search('python community 2024')")
    print("[Research Analyst] Result: 15M+ developers, PyCon record attendance...")
    print("[Research Analyst] Compiling research brief...")
    print("[Research Analyst] DONE: Research brief with 5 sections complete.")

    # Phase 2: Writing
    print("\n--- PHASE 2: WRITING ---")
    print("[Content Writer] Received research brief from Research Analyst.")
    print("[Content Writer] Planning article structure...")
    print("[Content Writer]   - Introduction: Hook about Python's dominance")
    print("[Content Writer]   - Section 1: Python 3.13 highlights")
    print("[Content Writer]   - Section 2: Hot frameworks and libraries")
    print("[Content Writer]   - Section 3: AI/ML ecosystem")
    print("[Content Writer]   - Conclusion: Looking ahead to 2025")
    print("[Content Writer] Writing article...")
    print("[Content Writer] DONE: Article draft complete (672 words).")

    # Phase 3: Editing
    print("\n--- PHASE 3: EDITING ---")
    print("[Technical Editor] Received draft from Content Writer.")
    print("[Technical Editor] Action: word_counter(article)")
    print("[Technical Editor] Result: 672 words. Meets 500-word minimum.")
    print("[Technical Editor] Checking grammar... 2 issues found and fixed.")
    print("[Technical Editor] Checking facts... All claims verified.")
    print("[Technical Editor] Improving transitions between sections...")
    print("[Technical Editor] DONE: Final article ready (685 words).")

    print("\n" + "=" * 60)
    print("  ALL PHASES COMPLETE")
    print("=" * 60)
    print(f"\n  Total agents used: 3")
    print(f"  Total tool calls: 4")
    print(f"  Final output: Publication-ready article (685 words)")
    print(f"  Quality: Research-backed, edited, fact-checked")


simulate_crew_execution()
```

**Expected output:**

```
============================================================
  MULTI-AGENT CONTENT CREATION: FULL SIMULATION
============================================================

--- PHASE 1: RESEARCH ---
[Research Analyst] Starting research on Python Trends 2024...
[Research Analyst] Action: web_search('python trends 2024')
[Research Analyst] Result: Python dominates AI/ML, 3.13 released...
[Research Analyst] Action: web_search('python frameworks 2024')
[Research Analyst] Result: FastAPI, LangChain, Polars trending...
[Research Analyst] Action: web_search('python community 2024')
[Research Analyst] Result: 15M+ developers, PyCon record attendance...
[Research Analyst] Compiling research brief...
[Research Analyst] DONE: Research brief with 5 sections complete.

--- PHASE 2: WRITING ---
[Content Writer] Received research brief from Research Analyst.
[Content Writer] Planning article structure...
[Content Writer]   - Introduction: Hook about Python's dominance
[Content Writer]   - Section 1: Python 3.13 highlights
[Content Writer]   - Section 2: Hot frameworks and libraries
[Content Writer]   - Section 3: AI/ML ecosystem
[Content Writer]   - Conclusion: Looking ahead to 2025
[Content Writer] Writing article...
[Content Writer] DONE: Article draft complete (672 words).

--- PHASE 3: EDITING ---
[Technical Editor] Received draft from Content Writer.
[Technical Editor] Action: word_counter(article)
[Technical Editor] Result: 672 words. Meets 500-word minimum.
[Technical Editor] Checking grammar... 2 issues found and fixed.
[Technical Editor] Checking facts... All claims verified.
[Technical Editor] Improving transitions between sections...
[Technical Editor] DONE: Final article ready (685 words).

============================================================
  ALL PHASES COMPLETE
============================================================

  Total agents used: 3
  Total tool calls: 4
  Final output: Publication-ready article (685 words)
  Quality: Research-backed, edited, fact-checked
```

---

## Common Mistakes

1. **Making agents too similar** -- If two agents have overlapping roles, they produce redundant work. Give each agent a clearly distinct role.

2. **Vague task descriptions** -- Tasks like "write something good" are too vague. Be specific about what the agent should produce, how long it should be, and what format to use.

3. **Too many agents** -- More agents does not always mean better results. Start with 2-3 agents and add more only if needed.

4. **Not setting verbose=True during development** -- Without verbose output, you cannot see what each agent is doing. Always enable it until your system is working correctly.

5. **Ignoring task dependencies** -- If a later task needs information from an earlier one, make sure the task execution order is correct and dependencies are specified.

6. **No error handling between agents** -- If the researcher agent produces bad output, the writer agent will produce a bad article. Add validation between agent steps.

---

## Best Practices

1. **Give each agent a detailed backstory** -- The more specific the backstory, the more consistently the agent behaves. Include years of experience, specialization, and working style.

2. **Write specific expected outputs** -- Tell each task exactly what format and content the output should have. This makes the agent's work more predictable.

3. **Start with sequential process** -- Begin with a simple sequential pipeline. Only switch to hierarchical when you need dynamic task routing.

4. **Test agents individually** -- Before assembling a crew, test each agent on sample tasks to make sure it performs well alone.

5. **Keep the team small** -- 2-4 agents is usually optimal. More agents add communication overhead and complexity.

6. **Use tools strategically** -- Give each agent only the tools it needs. A writer does not need a search tool if the researcher already provided the information.

---

## Quick Summary

Multi-agent systems use teams of specialized AI agents to handle complex tasks that would be difficult for a single agent. The three main orchestration patterns are sequential (pipeline), hierarchical (manager-workers), and collaborative (peer-to-peer). CrewAI provides a framework built around three concepts: Agents (team members with roles and skills), Tasks (specific work assignments), and Crews (teams that execute tasks). Each agent gets a role, goal, and backstory that define its behavior. Tasks specify what to do and what output to produce. The crew handles execution order and information passing between agents.

---

## Key Points

- **Multi-agent systems** divide complex tasks among specialized agents
- Each agent has a **role, goal, and backstory** that define its behavior
- **Sequential process** executes tasks one after another (most common)
- **Hierarchical process** uses a manager agent to delegate work
- **CrewAI** provides Agent, Task, and Crew classes for building teams
- **Task outputs** automatically flow to the next task in sequential mode
- Agents can have **tools** that give them specialized capabilities
- Keep teams **small** (2-4 agents) and roles **distinct**
- Always use `verbose=True` during development
- Test agents **individually** before assembling into a crew

---

## Practice Questions

1. You are building a multi-agent system to analyze customer reviews. What agents would you create, what roles would they have, and how would they work together?

2. Compare sequential and hierarchical orchestration patterns. For a task of writing a technical blog post, which would you choose and why?

3. An agent's backstory says "You are a creative writer who loves metaphors." How does this backstory influence the agent's behavior? What would happen if the backstory was empty?

4. You have a three-agent crew where the editor keeps rejecting the writer's output, causing an infinite loop. How would you fix this?

5. When would you use `allow_delegation=True`? Give a specific example where delegation between agents would be helpful.

---

## Exercises

### Exercise 1: Code Review Crew

Build a multi-agent crew for code review with three agents: (1) a Code Reviewer who checks for bugs and best practices, (2) a Security Analyst who checks for security vulnerabilities, and (3) a Performance Expert who suggests optimization improvements. Test with a sample Python function.

### Exercise 2: Customer Support Team

Create a hierarchical crew for customer support with a Manager agent that delegates to: (1) a FAQ Agent for common questions, (2) a Technical Support Agent for complex issues, and (3) an Escalation Agent for problems that need human intervention.

### Exercise 3: Research Report Generator

Build a sequential crew that generates a research report: (1) a Researcher who gathers information from multiple searches, (2) a Data Analyst who identifies key trends and statistics, (3) a Writer who creates the report, and (4) a Reviewer who provides feedback. Run it on the topic "The Future of Remote Work."

---

## What Is Next?

In Chapter 27, you will explore **Multimodal AI** -- models that understand and generate not just text, but also images, audio, and video. You will learn about vision-language models like GPT-4V, text-to-image generation with Stable Diffusion and DALL-E, and speech processing with Whisper. The boundaries between different types of AI are merging, and multimodal AI represents the next frontier.
