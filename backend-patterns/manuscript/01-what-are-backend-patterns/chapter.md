# Chapter 1: What Are Backend Design Patterns?

## What You Will Learn

- What design patterns are and where they came from
- The three categories of design patterns: creational, structural, and behavioral
- The difference between architecture patterns and design patterns
- The SOLID principles and how they connect to patterns
- Why patterns matter specifically in backend development
- How to read and use a pattern template
- What anti-patterns are and how to avoid them
- When NOT to use patterns (the over-engineering trap)

## Why This Chapter Matters

Every backend developer eventually faces the same problems: how do I structure this code so it does not turn into a tangled mess? How do I make this system handle more traffic without rewriting everything? How do I explain my design decisions to a new team member?

Design patterns are the answer to all three questions. They are proven solutions to recurring problems, and they give you a shared vocabulary with every other developer who has learned them. Before you write a single line of pattern code, you need to understand what patterns are, where they came from, and when they help versus when they hurt.

This chapter is the foundation. Skip it, and every other chapter will feel like memorizing recipes without understanding cooking.

---

## 1.1 What Is a Design Pattern?

A design pattern is a reusable solution to a commonly occurring problem in software design. It is not a finished piece of code you can copy and paste. It is a template, a blueprint, a description of how to solve a problem that you can adapt to your specific situation.

Think of it like this: if someone tells you to "use a queue to handle background jobs," they are describing a pattern. They are not giving you exact code. They are giving you a proven approach that you adapt to your language, framework, and requirements.

### The Key Characteristics of a Pattern

```
+------------------------------------------------------+
|              DESIGN PATTERN                          |
+------------------------------------------------------+
|                                                      |
|  1. NAME        - A shared vocabulary term           |
|  2. PROBLEM     - When to apply the pattern          |
|  3. SOLUTION    - The arrangement of classes/objects  |
|  4. CONSEQUENCES - Trade-offs and results             |
|                                                      |
+------------------------------------------------------+
```

A pattern is NOT:
- A library or framework
- A specific algorithm (like quicksort)
- A finished piece of code
- A silver bullet that solves everything

A pattern IS:
- A description of a solution to a recurring problem
- Language-independent (though implementations differ)
- A communication tool between developers
- A way to capture expert knowledge

---

## 1.2 The Gang of Four: Where It All Started

In 1994, four authors published a book that changed software engineering forever: *Design Patterns: Elements of Reusable Object-Oriented Software*. The authors were Erich Gamma, Richard Helm, Ralph Johnson, and John Vlissides. Developers quickly started calling them the "Gang of Four" or simply "GoF."

The GoF did not invent these patterns. They observed them. They studied experienced developers, looked at successful software systems, and documented the recurring solutions they found. Their contribution was cataloging and naming these patterns so that every developer could learn and communicate them.

```
+----------------------------------------------------------+
|           THE GANG OF FOUR (GoF) - 1994                  |
+----------------------------------------------------------+
|                                                          |
|  Erich Gamma ----+                                       |
|  Richard Helm ---+---> 23 Design Patterns Cataloged      |
|  Ralph Johnson --+                                       |
|  John Vlissides -+                                       |
|                                                          |
|  Key Insight: "Program to an interface, not an           |
|               implementation."                           |
|                                                          |
|  Key Insight: "Favor object composition over             |
|               class inheritance."                        |
|                                                          |
+----------------------------------------------------------+
```

The GoF cataloged 23 patterns, divided into three categories. These 23 patterns remain relevant today, even though the book was written before Java 1.0 was released. The problems they solve have not changed, even as languages and frameworks have evolved.

---

## 1.3 The Three Categories of Design Patterns

The GoF organized their 23 patterns into three categories based on what kind of problem each pattern solves.

```
+-------------------+--------------------+--------------------+
|    CREATIONAL     |    STRUCTURAL      |    BEHAVIORAL      |
|    (5 patterns)   |    (7 patterns)    |    (11 patterns)   |
+-------------------+--------------------+--------------------+
|                   |                    |                    |
| HOW objects       | HOW objects        | HOW objects        |
| are CREATED       | are COMPOSED       | COMMUNICATE        |
|                   |                    |                    |
+-------------------+--------------------+--------------------+
| - Singleton       | - Adapter          | - Observer         |
| - Factory Method  | - Bridge           | - Strategy         |
| - Abstract Factory| - Composite        | - Command          |
| - Builder         | - Decorator        | - Iterator         |
| - Prototype       | - Facade           | - State            |
|                   | - Flyweight        | - Template Method  |
|                   | - Proxy            | - Chain of Resp.   |
|                   |                    | - Mediator         |
|                   |                    | - Memento          |
|                   |                    | - Visitor          |
|                   |                    | - Interpreter      |
+-------------------+--------------------+--------------------+
```

### Creational Patterns

Creational patterns deal with object creation mechanisms. Instead of creating objects directly with `new`, these patterns provide ways to create objects that increase flexibility and reuse.

**Backend relevance:** Every backend system creates objects constantly: database connections, request handlers, configuration objects, service instances. Creational patterns help you control how, when, and how many of these objects get created.

### Structural Patterns

Structural patterns deal with how classes and objects are composed to form larger structures. They help you build flexible and efficient class hierarchies.

**Backend relevance:** Backend systems are built from many components: caches, databases, APIs, message queues. Structural patterns help you combine these components cleanly, add new capabilities without modifying existing code, and simplify complex subsystems.

### Behavioral Patterns

Behavioral patterns deal with how objects communicate and distribute responsibility. They help you define clear protocols for object interaction.

**Backend relevance:** Request processing, event handling, workflow orchestration, and state management are all communication problems. Behavioral patterns give you proven ways to handle them.

---

## 1.4 Architecture Patterns vs. Design Patterns

This is a distinction that confuses many developers. Architecture patterns and design patterns solve problems at different scales.

```
+----------------------------------------------------------------+
|                    SCALE OF PATTERNS                           |
+----------------------------------------------------------------+
|                                                                |
|  ARCHITECTURE PATTERNS (System-level)                          |
|  +----------------------------------------------------------+ |
|  | - Microservices     - Event-Driven Architecture           | |
|  | - Layered (N-Tier)  - CQRS                                | |
|  | - Hexagonal         - Serverless                          | |
|  | - MVC               - Pipe and Filter                     | |
|  +----------------------------------------------------------+ |
|  | Scope: Entire application or system                       | |
|  | Decided by: Architects, tech leads                        | |
|  | Changed: Rarely (expensive to change)                     | |
|  +----------------------------------------------------------+ |
|                                                                |
|  DESIGN PATTERNS (Class/Object-level)                          |
|  +----------------------------------------------------------+ |
|  | - Singleton          - Factory Method                     | |
|  | - Observer           - Strategy                           | |
|  | - Builder            - Decorator                          | |
|  +----------------------------------------------------------+ |
|  | Scope: A few classes or objects                            | |
|  | Decided by: Individual developers                         | |
|  | Changed: Frequently (low cost to change)                  | |
|  +----------------------------------------------------------+ |
|                                                                |
+----------------------------------------------------------------+
```

**Architecture patterns** answer questions like:
- How do we structure the entire application?
- How do services communicate?
- How do we handle data flow across the system?

**Design patterns** answer questions like:
- How do I create this object flexibly?
- How do I add behavior to this class without modifying it?
- How do I decouple these two classes?

They work together. Inside a microservices architecture, each service uses design patterns internally. A layered architecture uses the Facade pattern at layer boundaries. An event-driven architecture uses the Observer pattern at its core.

### A Concrete Example

Imagine you are building an e-commerce backend:

```
ARCHITECTURE DECISION:
  "We will use a microservices architecture
   with an API Gateway."

                +-------------+
                | API Gateway |
                +------+------+
                       |
          +------------+------------+
          |            |            |
     +----+----+  +----+----+  +---+-----+
     |  Order  |  | Payment |  | Inventory|
     | Service |  | Service |  | Service  |
     +---------+  +---------+  +----------+

DESIGN DECISIONS (inside each service):
  - Singleton for database connection pool
  - Factory Method for creating payment processors
  - Builder for constructing complex order objects
  - Observer for inventory change notifications
```

---

## 1.5 SOLID Principles Overview

Before diving into patterns, you need to understand SOLID. These five principles guide good object-oriented design, and almost every design pattern embodies one or more of them.

```
+---+----------------------------------+----------------------------+
| # | PRINCIPLE                        | ONE-LINE SUMMARY           |
+---+----------------------------------+----------------------------+
| S | Single Responsibility Principle  | One class, one reason to   |
|   |                                  | change.                    |
+---+----------------------------------+----------------------------+
| O | Open/Closed Principle            | Open for extension, closed |
|   |                                  | for modification.          |
+---+----------------------------------+----------------------------+
| L | Liskov Substitution Principle    | Subtypes must be           |
|   |                                  | substitutable for their    |
|   |                                  | base types.                |
+---+----------------------------------+----------------------------+
| I | Interface Segregation Principle  | Many small interfaces beat |
|   |                                  | one fat interface.         |
+---+----------------------------------+----------------------------+
| D | Dependency Inversion Principle   | Depend on abstractions,    |
|   |                                  | not concretions.           |
+---+----------------------------------+----------------------------+
```

Let us look at each one with backend-relevant examples.

### S - Single Responsibility Principle (SRP)

A class should have only one reason to change.

**Java - Before (violates SRP):**

```java
// BAD: This class does three things
public class UserService {

    public void createUser(String name, String email) {
        // 1. Validates input
        if (name == null || email == null) {
            throw new IllegalArgumentException("Name and email required");
        }

        // 2. Saves to database
        String sql = "INSERT INTO users (name, email) VALUES (?, ?)";
        jdbcTemplate.update(sql, name, email);

        // 3. Sends welcome email
        String subject = "Welcome!";
        String body = "Hello " + name + ", welcome to our platform!";
        emailClient.send(email, subject, body);
    }
}
```

**Java - After (follows SRP):**

```java
// GOOD: Each class has one responsibility

public class UserValidator {
    public void validate(String name, String email) {
        if (name == null || email == null) {
            throw new IllegalArgumentException("Name and email required");
        }
    }
}

public class UserRepository {
    public void save(String name, String email) {
        String sql = "INSERT INTO users (name, email) VALUES (?, ?)";
        jdbcTemplate.update(sql, name, email);
    }
}

public class WelcomeEmailSender {
    public void send(String name, String email) {
        String subject = "Welcome!";
        String body = "Hello " + name + ", welcome to our platform!";
        emailClient.send(email, subject, body);
    }
}

public class UserService {
    private final UserValidator validator;
    private final UserRepository repository;
    private final WelcomeEmailSender emailSender;

    public void createUser(String name, String email) {
        validator.validate(name, email);
        repository.save(name, email);
        emailSender.send(name, email);
    }
}
```

**Python - Before (violates SRP):**

```python
# BAD: This class does three things
class UserService:
    def create_user(self, name: str, email: str):
        # 1. Validates input
        if not name or not email:
            raise ValueError("Name and email required")

        # 2. Saves to database
        cursor = self.db.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (name, email)
        )

        # 3. Sends welcome email
        self.email_client.send(
            to=email,
            subject="Welcome!",
            body=f"Hello {name}, welcome to our platform!"
        )
```

**Python - After (follows SRP):**

```python
# GOOD: Each class has one responsibility

class UserValidator:
    def validate(self, name: str, email: str):
        if not name or not email:
            raise ValueError("Name and email required")

class UserRepository:
    def __init__(self, db):
        self.db = db

    def save(self, name: str, email: str):
        self.db.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (name, email)
        )

class WelcomeEmailSender:
    def __init__(self, email_client):
        self.email_client = email_client

    def send(self, name: str, email: str):
        self.email_client.send(
            to=email,
            subject="Welcome!",
            body=f"Hello {name}, welcome to our platform!"
        )

class UserService:
    def __init__(self, validator, repository, email_sender):
        self.validator = validator
        self.repository = repository
        self.email_sender = email_sender

    def create_user(self, name: str, email: str):
        self.validator.validate(name, email)
        self.repository.save(name, email)
        self.email_sender.send(name, email)
```

### O - Open/Closed Principle (OCP)

Software entities should be open for extension but closed for modification.

This means you should be able to add new behavior without changing existing code. The Factory Method and Strategy patterns are direct applications of this principle.

### L - Liskov Substitution Principle (LSP)

Objects of a superclass should be replaceable with objects of a subclass without breaking the application.

If your code works with a `PaymentProcessor` interface, it should work with `StripeProcessor`, `PayPalProcessor`, or any other implementation without surprises.

### I - Interface Segregation Principle (ISP)

Clients should not be forced to depend on interfaces they do not use.

Instead of one giant `DatabaseOperations` interface with 50 methods, create smaller interfaces like `Readable`, `Writable`, and `Deletable`.

### D - Dependency Inversion Principle (DIP)

High-level modules should not depend on low-level modules. Both should depend on abstractions.

Instead of `OrderService` depending directly on `MySQLDatabase`, both should depend on a `Database` interface.

```
BEFORE (Dependency Inversion violated):

  +---------------+         +------------------+
  | OrderService  |-------->| MySQLDatabase    |
  +---------------+         +------------------+
  High-level module         Low-level module
  depends on                (concrete class)
  concrete class

AFTER (Dependency Inversion applied):

  +---------------+         +------------------+
  | OrderService  |-------->|  <<interface>>   |
  +---------------+         |    Database      |
                            +------------------+
                                    ^
                                    |
                            +------------------+
                            | MySQLDatabase    |
                            +------------------+

  Both depend on the abstraction (Database interface).
  OrderService is easy to test with a mock database.
```

---

## 1.6 Why Patterns Matter in Backend Development

Backend development has unique challenges that patterns address directly.

### 1. Scalability

Backend systems must handle growing load. Patterns like Singleton (connection pools), Flyweight (shared objects), and Proxy (lazy loading) help you manage resources efficiently.

```
Without patterns:
  Request 1 --> new DBConnection()  --> DB
  Request 2 --> new DBConnection()  --> DB
  Request 3 --> new DBConnection()  --> DB
  ...
  Request 10000 --> new DBConnection() --> DB OVERWHELMED!

With Singleton + Object Pool:
  Request 1 ----+
  Request 2 ----+--> ConnectionPool (Singleton)
  Request 3 ----+       |
  ...           |       +--> Connection 1 --> DB
  Request 10000-+       +--> Connection 2 --> DB
                        +--> Connection 3 --> DB
                        (reuses connections)
```

### 2. Maintainability

Backend code lives for years. Patterns make code easier to understand and modify because every developer recognizes them.

```
WITHOUT patterns (in a code review):
  Developer A: "Why is there a private constructor here?"
  Developer B: "Oh, I wanted only one instance."
  Developer A: "But what about thread safety?"
  Developer B: "Uh..."

WITH patterns (in a code review):
  Developer A: "I see you used the Singleton pattern."
  Developer B: "Yes, with double-checked locking for thread safety."
  Developer A: "Got it. Looks good."
```

### 3. Team Communication

Patterns are a shared vocabulary. Saying "use a Builder for the query object" communicates more information in fewer words than describing the entire approach from scratch.

### 4. Testability

Many patterns naturally lead to testable code. Factory patterns let you inject mock objects. Strategy patterns let you swap algorithms in tests. Observer patterns let you verify events were fired.

### 5. Framework Integration

Modern frameworks are built on patterns. Spring uses Singleton, Factory, Proxy, and Template Method extensively. Django uses Template Method, Observer, and Strategy. Understanding patterns helps you understand your framework.

```
+-------------------------------+---------------------------+
| SPRING FRAMEWORK              | PATTERNS USED             |
+-------------------------------+---------------------------+
| @Component, @Service          | Singleton                 |
| @Bean                         | Factory Method            |
| @Autowired                    | Dependency Injection      |
| AOP / @Transactional          | Proxy                     |
| JdbcTemplate                  | Template Method           |
| ApplicationEvent              | Observer                  |
+-------------------------------+---------------------------+

+-------------------------------+---------------------------+
| DJANGO FRAMEWORK              | PATTERNS USED             |
+-------------------------------+---------------------------+
| Views (CBV)                   | Template Method           |
| Signals                       | Observer                  |
| Middleware                     | Chain of Responsibility   |
| QuerySet                      | Builder / Iterator        |
| Settings module               | Singleton (module-level)  |
+-------------------------------+---------------------------+
```

---

## 1.7 The Pattern Template

Throughout this book, every pattern follows a consistent template. Here is how to read it.

```
+---------------------------------------------------------------+
|                    PATTERN TEMPLATE                            |
+---------------------------------------------------------------+
|                                                               |
|  PATTERN NAME                                                 |
|  Also known as: Alternative names                             |
|                                                               |
|  CATEGORY: Creational / Structural / Behavioral               |
|                                                               |
|  INTENT                                                       |
|  One or two sentences describing what the pattern does.       |
|                                                               |
|  PROBLEM                                                      |
|  The specific problem this pattern solves.                    |
|  Includes a "Before" code example showing the pain.           |
|                                                               |
|  SOLUTION                                                     |
|  How the pattern solves the problem.                          |
|  Includes ASCII diagram of the pattern structure.             |
|                                                               |
|  PARTICIPANTS                                                 |
|  The classes/interfaces involved and their roles.             |
|                                                               |
|  CODE EXAMPLES                                                |
|  Java and Python implementations side by side.                |
|  Each with line-by-line explanations.                         |
|  Each with sample output.                                     |
|                                                               |
|  REAL-WORLD BACKEND USE CASE                                  |
|  A concrete backend scenario where this pattern shines.       |
|                                                               |
|  WHEN TO USE / WHEN NOT TO USE                                |
|  Clear guidance on applicability.                             |
|                                                               |
|  COMMON MISTAKES                                              |
|  Pitfalls that developers frequently fall into.               |
|                                                               |
|  BEST PRACTICES                                               |
|  Tips for getting the most out of the pattern.                |
|                                                               |
+---------------------------------------------------------------+
```

---

## 1.8 Anti-Patterns: When Good Intentions Go Wrong

An anti-pattern is a common response to a recurring problem that is usually ineffective and risks being counterproductive. In other words, it is a pattern that looks like a good idea but turns out to be a bad one.

### Common Backend Anti-Patterns

**1. God Object / God Class**

One class that knows everything and does everything.

```
+--------------------------------------------------+
|              GOD CLASS (ANTI-PATTERN)             |
+--------------------------------------------------+
|                                                  |
|  class ApplicationManager:                       |
|      def handle_request()                        |
|      def validate_input()                        |
|      def query_database()                        |
|      def send_email()                            |
|      def generate_report()                       |
|      def process_payment()                       |
|      def manage_cache()                          |
|      def log_activity()                          |
|      def authenticate_user()                     |
|      def ... (200 more methods)                  |
|                                                  |
+--------------------------------------------------+
|  PROBLEM: Impossible to test, maintain, or       |
|  understand. Every change risks breaking         |
|  something unrelated.                            |
+--------------------------------------------------+
```

**2. Spaghetti Code**

Code with no clear structure, where control flow jumps around unpredictably.

**3. Golden Hammer**

Using the same pattern or technology for every problem because you are familiar with it.

```
Developer: "I know Singleton really well!"

  Need a config?      --> Singleton!
  Need a logger?      --> Singleton!
  Need a user object? --> Singleton!  <-- WRONG
  Need a request?     --> Singleton!  <-- VERY WRONG
  Need anything?      --> Singleton!  <-- STOP
```

**4. Premature Optimization**

Applying complex patterns to solve performance problems that do not exist yet.

**5. Copy-Paste Programming**

Duplicating code instead of finding the right abstraction.

---

## 1.9 When NOT to Use Patterns: The Over-Engineering Trap

This might be the most important section in the entire book.

Patterns are tools. Like any tool, they can be misused. The most common misuse is applying patterns where they are not needed.

### Signs You Are Over-Engineering

```
+----------------------------------------------------------------+
|              OVER-ENGINEERING WARNING SIGNS                     |
+----------------------------------------------------------------+
|                                                                |
|  1. "We might need this someday"                               |
|     --> YAGNI: You Aren't Gonna Need It                        |
|                                                                |
|  2. You have more interfaces than implementations              |
|     --> An interface with one implementation is overhead        |
|                                                                |
|  3. Simple operations require navigating 10+ files             |
|     --> Patterns should simplify, not complicate                |
|                                                                |
|  4. New team members take weeks to understand the code          |
|     --> If patterns make code harder to read, remove them       |
|                                                                |
|  5. You are adding a pattern because the book says so           |
|     --> Only add patterns to solve real problems                |
|                                                                |
+----------------------------------------------------------------+
```

### The Pragmatic Approach

**Java - Over-Engineered (DO NOT do this):**

```java
// A simple greeting... with five files and three interfaces

public interface GreetingStrategy {
    String greet(String name);
}

public class EnglishGreetingStrategy implements GreetingStrategy {
    public String greet(String name) {
        return "Hello, " + name;
    }
}

public interface GreetingFactory {
    GreetingStrategy createStrategy(String language);
}

public class DefaultGreetingFactory implements GreetingFactory {
    public GreetingStrategy createStrategy(String language) {
        if ("en".equals(language)) {
            return new EnglishGreetingStrategy();
        }
        throw new UnsupportedOperationException();
    }
}

public class GreetingService {
    private final GreetingFactory factory;

    public GreetingService(GreetingFactory factory) {
        this.factory = factory;
    }

    public String greet(String name, String language) {
        return factory.createStrategy(language).greet(name);
    }
}

// All of this... to print "Hello, World"
```

**Java - Just Right:**

```java
// Simple and clear. Add patterns WHEN complexity demands it.
public class GreetingService {

    public String greet(String name) {
        return "Hello, " + name;
    }
}

// When you actually need multiple languages,
// THEN add the Strategy pattern.
```

### The Decision Framework

Ask yourself these questions before applying a pattern:

```
+-----------------------------------+
|   Should I Use a Pattern Here?    |
+-----------------------------------+
          |
          v
+-----------------------------------+
| Do I have a real problem that     |
| a pattern solves?                 |
+---+-------------------------------+
    |                   |
   YES                  NO --> STOP. Keep it simple.
    |
    v
+-----------------------------------+
| Will this pattern make the code   |
| easier to understand?             |
+---+-------------------------------+
    |                   |
   YES                  NO --> STOP. Find a simpler solution.
    |
    v
+-----------------------------------+
| Is the added complexity worth     |
| the flexibility I gain?           |
+---+-------------------------------+
    |                   |
   YES                  NO --> STOP. Simpler is better.
    |
    v
+-----------------------------------+
| USE THE PATTERN.                  |
+-----------------------------------+
```

---

## 1.10 Patterns in This Book

This book covers the most important patterns for backend developers. Here is the roadmap:

```
PART I: CREATIONAL PATTERNS
+----------------------------------------------------------+
| Ch 2:  Singleton       - One instance to rule them all   |
| Ch 3:  Factory Method  - Let subclasses decide           |
| Ch 4:  Abstract Factory- Families of related objects     |
| Ch 5:  Builder         - Step-by-step construction       |
| Ch 6:  Prototype       - Clone existing objects          |
+----------------------------------------------------------+

PART II: STRUCTURAL PATTERNS (Future chapters)
+----------------------------------------------------------+
| Adapter, Decorator, Proxy, Facade, Composite             |
+----------------------------------------------------------+

PART III: BEHAVIORAL PATTERNS (Future chapters)
+----------------------------------------------------------+
| Observer, Strategy, Command, Chain of Responsibility,    |
| Template Method, State                                   |
+----------------------------------------------------------+
```

Each pattern chapter follows the same structure, so you always know where to find the information you need.

---

## Quick Summary

| Concept | Key Takeaway |
|---------|-------------|
| Design patterns | Reusable solutions to recurring problems, not copy-paste code |
| Gang of Four | Four authors who cataloged 23 patterns in 1994 |
| Three categories | Creational (object creation), Structural (composition), Behavioral (communication) |
| Architecture vs. design patterns | Architecture = system-level, Design = class/object-level |
| SOLID principles | Five principles that guide good OO design; patterns embody them |
| Anti-patterns | Common "solutions" that cause more problems than they solve |
| Over-engineering | The biggest risk of learning patterns; apply them only when needed |

---

## Key Points

1. Design patterns are proven solutions, not invented solutions. They are discovered by observing what works in practice.

2. The Gang of Four cataloged 23 patterns in three categories. Every pattern in this book traces back to their work.

3. SOLID principles are the foundation. If you understand SOLID, patterns will make intuitive sense.

4. Patterns are a communication tool. Saying "Singleton" is faster and more precise than explaining the entire concept from scratch.

5. The biggest danger of learning patterns is over-engineering. Apply a pattern only when it solves a real problem and makes the code simpler to understand.

6. Architecture patterns and design patterns work at different scales. You will use both, but this book focuses on design patterns.

7. Anti-patterns are just as important to recognize as patterns. Knowing what NOT to do saves you from expensive mistakes.

---

## Practice Questions

1. What are the three categories of design patterns defined by the Gang of Four? Give one example pattern from each category and explain what kind of problem it addresses.

2. Explain the difference between an architecture pattern and a design pattern. Give a scenario where you would use both together in a backend system.

3. You join a team where a single `ApplicationManager` class has 3,000 lines of code and handles user authentication, payment processing, email sending, and report generation. Which SOLID principle does this violate? What would you do to fix it?

4. A junior developer on your team wants to implement the Abstract Factory pattern for a service that currently has only one type of database and no plans to add another. Is this a good idea? Explain your reasoning.

5. Name three backend-specific reasons why design patterns are important. For each reason, give a concrete example.

---

## Exercises

### Exercise 1: Identify the Principle

Look at the following code and identify which SOLID principle(s) it violates. Rewrite it to follow the principles.

```python
class ReportService:
    def generate_pdf_report(self, data):
        # Validate data
        if not data:
            raise ValueError("No data")

        # Query database for additional info
        extra = self.db.query("SELECT * FROM metadata")

        # Generate PDF
        pdf = PDFLibrary.create(data, extra)

        # Send email with attachment
        self.email.send("admin@company.com", "Report", attachment=pdf)

        # Log to file
        with open("report.log", "a") as f:
            f.write(f"Report generated at {datetime.now()}\n")

        return pdf
```

### Exercise 2: Pattern or Over-Engineering?

For each scenario below, decide whether applying a design pattern is appropriate or over-engineering. Justify your answer.

1. A REST API endpoint that returns a hardcoded "OK" health check response. A colleague suggests using the Strategy pattern so you can swap health check implementations.

2. A payment service that currently supports Stripe. The product roadmap shows PayPal and Square integrations coming in the next quarter. A colleague suggests using the Factory Method pattern.

3. A configuration loader that reads from a YAML file at startup. A colleague suggests using the Singleton pattern to ensure only one config object exists.

### Exercise 3: Map the Framework

Pick a backend framework you use (Spring, Django, Flask, Express, etc.). Find three places where the framework uses design patterns. For each one, name the pattern and explain what problem it solves in the framework.

---

## What Is Next?

In the next chapter, we dive into our first design pattern: the Singleton. It is the simplest creational pattern, the most debated, and the most frequently misused. You will learn when it genuinely helps (database connection pools, configuration managers) and when it causes more harm than good (hidden dependencies, testing nightmares). We will implement it in both Java and Python, handle thread safety, and see how modern frameworks like Spring handle singletons for you.
