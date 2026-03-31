# Chapter 11: The Interface Segregation Principle -- Keep Interfaces Focused

---

## What You Will Learn

- What the Interface Segregation Principle (ISP) means and why fat interfaces cause real problems
- The "forced dependency" problem: when classes must implement methods they do not need
- How to split a fat interface into focused, role-based interfaces
- The IWorker problem: before and after refactoring with work(), eat(), and sleep()
- How Python ABCs and Protocols support ISP
- When a single large interface is actually fine and splitting would be over-engineering
- How ISP applies beyond classes to REST APIs and module design

---

## Why This Chapter Matters

Imagine you are building a robot class for a factory simulation. You inherit from an `IWorker` interface that requires you to implement `work()`, `eat()`, and `sleep()`. Your robot works, but it does not eat or sleep. You are forced to write empty method bodies or throw exceptions for methods that have nothing to do with your class.

This is not a minor annoyance. It creates three serious problems:

1. **Misleading API**: Anyone looking at the robot class sees `eat()` and `sleep()` and assumes the robot supports those operations.
2. **Coupling**: If someone adds `dream()` to the `IWorker` interface, your robot class must be updated even though dreaming is irrelevant to robots.
3. **Testing burden**: You must write tests for methods that do nothing, or worse, document why they throw exceptions.

The Interface Segregation Principle eliminates these problems by ensuring no class is forced to depend on methods it does not use.

---

## The Interface Segregation Principle Defined

Robert C. Martin stated the principle as:

> No client should be forced to depend on methods it does not use.

In practical terms: **prefer many small, focused interfaces over one large, general-purpose interface.** Each interface should represent a single role or capability.

```
+-----------------------------------------------------------+
|     THE INTERFACE SEGREGATION PRINCIPLE                     |
+-----------------------------------------------------------+
|                                                            |
|  FAT INTERFACE (BAD):                                      |
|  +------------------------------+                          |
|  |         IWorker              |                          |
|  |------------------------------|                          |
|  |  + work()                    |                          |
|  |  + eat()                     |  <-- Robot must          |
|  |  + sleep()                   |      implement all       |
|  |  + takeBreak()               |      even if irrelevant  |
|  |  + getPaycheck()             |                          |
|  +------------------------------+                          |
|                                                            |
|  SEGREGATED INTERFACES (GOOD):                             |
|  +-----------+  +-----------+  +-----------+               |
|  | IWorkable |  | IFeedable |  | ISleepable|               |
|  |-----------|  |-----------|  |-----------|               |
|  | + work()  |  | + eat()   |  | + sleep() |               |
|  +-----------+  +-----------+  +-----------+               |
|       ^              ^              ^                      |
|       |              |              |                      |
|    Robot         Human          Human                      |
|  (work only)   (all three)    (all three)                  |
|                                                            |
+-----------------------------------------------------------+
```

---

## The IWorker Problem: Before and After

### BEFORE: Fat Interface Forces Unwanted Dependencies (Java)

```java
// Java -- BAD: Fat interface that mixes unrelated responsibilities
public interface IWorker {

    void work();

    void eat();

    void sleep();
}

public class HumanWorker implements IWorker {

    @Override
    public void work() {
        System.out.println("Human working on tasks.");
    }

    @Override
    public void eat() {
        System.out.println("Human eating lunch.");
    }

    @Override
    public void sleep() {
        System.out.println("Human sleeping for 8 hours.");
    }
}

public class RobotWorker implements IWorker {

    @Override
    public void work() {
        System.out.println("Robot performing tasks efficiently.");
    }

    @Override
    public void eat() {
        // Robot does not eat. What do we put here?
        throw new UnsupportedOperationException("Robots don't eat!");
    }

    @Override
    public void sleep() {
        // Robot does not sleep. Same problem.
        throw new UnsupportedOperationException("Robots don't sleep!");
    }
}
```

This is also an LSP violation. If code iterates over a list of `IWorker` instances and calls `eat()`, the robot will throw an exception. The interface promises something the implementation cannot deliver.

### AFTER: Segregated Interfaces (Java)

```java
// Java -- GOOD: Small, focused interfaces

public interface Workable {
    void work();
}

public interface Feedable {
    void eat();
}

public interface Sleepable {
    void sleep();
}

public class HumanWorker implements Workable, Feedable, Sleepable {

    @Override
    public void work() {
        System.out.println("Human working on tasks.");
    }

    @Override
    public void eat() {
        System.out.println("Human eating lunch.");
    }

    @Override
    public void sleep() {
        System.out.println("Human sleeping for 8 hours.");
    }
}

public class RobotWorker implements Workable {

    @Override
    public void work() {
        System.out.println("Robot performing tasks efficiently.");
    }

    // No eat(). No sleep(). Clean and honest.
}
```

Now the code that manages work schedules takes `Workable`:

```java
// Java -- Clean: each function depends only on what it needs
public class WorkScheduler {

    public void assignTasks(List<Workable> workers) {
        for (Workable worker : workers) {
            worker.work();  // Safe for both humans and robots
        }
    }
}

public class CafeteriaManager {

    public void serveLunch(List<Feedable> hungryWorkers) {
        for (Feedable worker : hungryWorkers) {
            worker.eat();  // Only gets workers that actually eat
        }
    }
}
```

### BEFORE: Fat Interface in Python

```python
# Python -- BAD: Fat interface
from abc import ABC, abstractmethod


class IWorker(ABC):

    @abstractmethod
    def work(self) -> None:
        pass

    @abstractmethod
    def eat(self) -> None:
        pass

    @abstractmethod
    def sleep(self) -> None:
        pass


class HumanWorker(IWorker):

    def work(self) -> None:
        print("Human working on tasks.")

    def eat(self) -> None:
        print("Human eating lunch.")

    def sleep(self) -> None:
        print("Human sleeping for 8 hours.")


class RobotWorker(IWorker):

    def work(self) -> None:
        print("Robot performing tasks efficiently.")

    def eat(self) -> None:
        pass  # Empty implementation -- dishonest

    def sleep(self) -> None:
        pass  # Empty implementation -- dishonest
```

### AFTER: Segregated Interfaces in Python

```python
# Python -- GOOD: Segregated ABCs
from abc import ABC, abstractmethod


class Workable(ABC):
    @abstractmethod
    def work(self) -> None:
        pass


class Feedable(ABC):
    @abstractmethod
    def eat(self) -> None:
        pass


class Sleepable(ABC):
    @abstractmethod
    def sleep(self) -> None:
        pass


class HumanWorker(Workable, Feedable, Sleepable):

    def work(self) -> None:
        print("Human working on tasks.")

    def eat(self) -> None:
        print("Human eating lunch.")

    def sleep(self) -> None:
        print("Human sleeping for 8 hours.")


class RobotWorker(Workable):

    def work(self) -> None:
        print("Robot performing tasks efficiently.")
```

---

## Python ABCs vs. Protocols for ISP

Python gives you two tools for defining interfaces: Abstract Base Classes (ABCs) and Protocols. Both work well for ISP, but they serve different purposes.

### ABCs: Explicit, Enforced at Instantiation

```python
# Python -- ABCs enforce implementation at instantiation time
from abc import ABC, abstractmethod


class Printable(ABC):
    @abstractmethod
    def to_string(self) -> str:
        pass


class Invoice(Printable):
    def to_string(self) -> str:
        return "Invoice #12345"


class BadInvoice(Printable):
    pass  # TypeError raised when you try to instantiate this
```

### Protocols: Structural, No Inheritance Required

```python
# Python -- Protocols use structural typing (duck typing with type hints)
from typing import Protocol


class Printable(Protocol):
    def to_string(self) -> str: ...


class Invoice:
    """Does NOT inherit from Printable, but satisfies its contract."""

    def to_string(self) -> str:
        return "Invoice #12345"


def print_document(doc: Printable) -> None:
    print(doc.to_string())


# This works because Invoice has a to_string() method
print_document(Invoice())  # No inheritance needed
```

**When to use which:**

```
+-----------------------------------------------------------+
|     ABCs vs PROTOCOLS FOR ISP                              |
+-----------------------------------------------------------+
|                                                            |
|  Use ABCs when:                                            |
|    - You want instantiation-time enforcement               |
|    - You have shared default implementations               |
|    - Your team prefers explicit "implements" relationships  |
|                                                            |
|  Use Protocols when:                                       |
|    - You want duck typing with type checker support        |
|    - You are working with third-party classes you cannot   |
|      modify                                                |
|    - You prefer minimal coupling (no inheritance needed)   |
|                                                            |
+-----------------------------------------------------------+
```

---

## Role Interfaces

The segregated interfaces in the IWorker example are called **role interfaces**. Each interface represents a specific role an object can play, rather than defining everything the object is.

```
+-----------------------------------------------------------+
|     ROLE INTERFACES                                        |
+-----------------------------------------------------------+
|                                                            |
|  Instead of one big "I am everything" interface:           |
|                                                            |
|    IEmployee: work(), eat(), sleep(), getPaycheck(),       |
|               requestVacation(), attendMeeting(),          |
|               submitTimesheet()                            |
|                                                            |
|  Define focused roles:                                     |
|                                                            |
|    Workable:     work()                                    |
|    Feedable:     eat()                                     |
|    Payable:      getPaycheck()                             |
|    Schedulable:  attendMeeting(), requestVacation()        |
|    Trackable:    submitTimesheet()                         |
|                                                            |
|  Each client depends only on the roles it cares about.     |
|                                                            |
+-----------------------------------------------------------+
```

A more realistic example:

```java
// Java -- Role interfaces for a document management system

public interface Readable {
    String getContent();
}

public interface Writable {
    void setContent(String content);
}

public interface Printable {
    void print();
}

public interface Versionable {
    int getVersion();
    void incrementVersion();
    List<String> getHistory();
}

// A full document supports all roles
public class Document implements Readable, Writable, Printable, Versionable {
    // Implements all four interfaces
}

// A read-only view supports only reading
public class ReadOnlyDocument implements Readable {
    // Only implements getContent()
}

// A printer service only needs Printable
public class PrintService {
    public void printAll(List<Printable> documents) {
        for (Printable doc : documents) {
            doc.print();
        }
    }
}

// A version control service only needs Versionable
public class VersionControl {
    public void commit(Versionable document) {
        document.incrementVersion();
    }
}
```

---

## When One Big Interface Is Actually Fine

ISP does not mean you should always split every interface into single-method fragments. Sometimes a larger interface is the right choice:

### 1. Cohesive Operations That Always Go Together

```java
// Java -- This is fine as one interface
public interface Iterator<T> {
    boolean hasNext();
    T next();
}

// These two methods are inseparable.
// You will never need hasNext() without next().
// Splitting them would be pointless.
```

### 2. Standard Library Interfaces

The `List` interface in Java has dozens of methods (`add`, `remove`, `get`, `size`, `contains`, etc.). This is fine because all implementations genuinely support all operations. If they do not (like `Collections.unmodifiableList()`), that is an LSP problem, not an ISP problem.

### 3. Small Teams with Simple Domains

If you have three classes that all implement the exact same five methods, and you do not anticipate adding a class that would only need some of them, keeping one five-method interface is simpler than creating five single-method interfaces.

**The test**: Would splitting the interface result in some implementors implementing fewer interfaces? If yes, split it. If every implementor would implement all the sub-interfaces anyway, a single interface is fine.

---

## ISP in REST APIs

ISP applies beyond class interfaces. In REST API design, the same principle says: do not force clients to receive data they do not need.

### BEFORE: Fat API Response

```json
// BAD: Client only needs name and email, gets everything
GET /api/users/123

{
    "id": 123,
    "name": "Jane Smith",
    "email": "jane@example.com",
    "passwordHash": "bcrypt$...",
    "socialSecurityNumber": "123-45-6789",
    "internalNotes": "Flagged for review",
    "loginHistory": [...2000 entries...],
    "fullOrderHistory": [...500 entries...],
    "paymentMethods": [...],
    "adminFlags": {...}
}
```

### AFTER: Focused API Responses

```json
// GOOD: Separate endpoints or field selection

// Public profile (what most clients need)
GET /api/users/123/profile
{
    "id": 123,
    "name": "Jane Smith",
    "email": "jane@example.com"
}

// Order history (only for order-related features)
GET /api/users/123/orders
{
    "orders": [...]
}

// Admin view (only for admin dashboards)
GET /api/admin/users/123
{
    "id": 123,
    "internalNotes": "...",
    "adminFlags": {...}
}
```

Or use field selection (GraphQL-style):

```
GET /api/users/123?fields=name,email
```

```
+-----------------------------------------------------------+
|     ISP IN API DESIGN                                      |
+-----------------------------------------------------------+
|                                                            |
|  FAT ENDPOINT:                                             |
|  GET /api/users/123                                        |
|  Returns: 50 fields, 3 nested objects, 2000-entry array   |
|  Every client gets everything, uses 3 fields               |
|                                                            |
|  SEGREGATED ENDPOINTS:                                     |
|  GET /api/users/123/profile     -> 5 fields                |
|  GET /api/users/123/orders      -> order list only         |
|  GET /api/users/123/preferences -> preferences only        |
|                                                            |
|  Each client requests only what it needs.                  |
|  Less bandwidth. Less coupling. Less risk of leaking       |
|  sensitive data.                                           |
|                                                            |
+-----------------------------------------------------------+
```

---

## A Larger Example: Printer Interface

### BEFORE: Fat Printer Interface

```java
// Java -- BAD: Every printer must implement every feature
public interface IPrinter {
    void print(Document doc);
    void scan(Document doc);
    void fax(Document doc);
    void staple(Document doc);
    void collate(Document doc);
}

public class BasicPrinter implements IPrinter {

    @Override
    public void print(Document doc) {
        System.out.println("Printing document...");
    }

    @Override
    public void scan(Document doc) {
        throw new UnsupportedOperationException("Cannot scan");
    }

    @Override
    public void fax(Document doc) {
        throw new UnsupportedOperationException("Cannot fax");
    }

    @Override
    public void staple(Document doc) {
        throw new UnsupportedOperationException("Cannot staple");
    }

    @Override
    public void collate(Document doc) {
        throw new UnsupportedOperationException("Cannot collate");
    }
}
```

### AFTER: Segregated Printer Interfaces

```java
// Java -- GOOD: Focused interfaces for printer capabilities
public interface Printer {
    void print(Document doc);
}

public interface Scanner {
    void scan(Document doc);
}

public interface Fax {
    void fax(Document doc);
}

public interface Finisher {
    void staple(Document doc);
    void collate(Document doc);
}

// Basic printer: only prints
public class BasicPrinter implements Printer {
    @Override
    public void print(Document doc) {
        System.out.println("Printing document...");
    }
}

// All-in-one: implements all capabilities
public class AllInOnePrinter implements Printer, Scanner, Fax, Finisher {

    @Override
    public void print(Document doc) {
        System.out.println("Printing document...");
    }

    @Override
    public void scan(Document doc) {
        System.out.println("Scanning document...");
    }

    @Override
    public void fax(Document doc) {
        System.out.println("Faxing document...");
    }

    @Override
    public void staple(Document doc) {
        System.out.println("Stapling document...");
    }

    @Override
    public void collate(Document doc) {
        System.out.println("Collating document...");
    }
}
```

```python
# Python -- GOOD: Segregated printer protocols
from typing import Protocol


class Printer(Protocol):
    def print_doc(self, doc: Document) -> None: ...


class Scanner(Protocol):
    def scan(self, doc: Document) -> None: ...


class Fax(Protocol):
    def fax(self, doc: Document) -> None: ...


class BasicPrinter:
    def print_doc(self, doc: Document) -> None:
        print("Printing document...")


class AllInOnePrinter:
    def print_doc(self, doc: Document) -> None:
        print("Printing document...")

    def scan(self, doc: Document) -> None:
        print("Scanning document...")

    def fax(self, doc: Document) -> None:
        print("Faxing document...")


def print_batch(printer: Printer, docs: list[Document]) -> None:
    for doc in docs:
        printer.print_doc(doc)  # Works with BasicPrinter or AllInOnePrinter
```

---

## Common Mistakes

1. **Creating one giant interface and making every class implement it.** This is the core ISP violation. If any implementor has empty methods or throws UnsupportedOperationException, the interface is too fat.

2. **Splitting interfaces too aggressively.** Do not create a separate interface for every single method. Group methods that are genuinely cohesive and always used together.

3. **Ignoring ISP in API design.** Returning 50 fields when the client needs 3 is the API-level equivalent of a fat interface.

4. **Using marker interfaces instead of capability interfaces.** An empty `IAdvancedPrinter` interface that signals capabilities through its name rather than its methods is a code smell.

5. **Confusing ISP with SRP.** SRP is about classes having one reason to change. ISP is about interfaces not forcing clients to depend on methods they do not use. They are related but distinct.

---

## Best Practices

1. **Design interfaces from the client's perspective.** Ask "What does this client need?" not "What can this object do?"

2. **Use role interfaces.** Each interface should represent one role or capability.

3. **Apply the no-empty-methods test.** If an implementor must leave a method body empty or throw an exception, the interface should be split.

4. **Group cohesive operations.** `hasNext()` and `next()` belong together. Do not split things that always go together.

5. **Apply ISP to APIs.** Use focused endpoints, field selection, or separate views for different client needs.

6. **In Python, prefer Protocols for ISP.** They provide structural typing without requiring inheritance, which is the cleanest way to implement ISP.

---

## Quick Summary

```
+-----------------------------------------------------------+
|              ISP CHEAT SHEET                               |
+-----------------------------------------------------------+
|                                                            |
|  PRINCIPLE:                                                |
|    No client should be forced to depend on methods         |
|    it does not use                                         |
|                                                            |
|  FAT INTERFACE SIGNS:                                      |
|    - Classes with empty method implementations             |
|    - UnsupportedOperationException in subclasses           |
|    - Clients using only 2 of 10 methods                    |
|                                                            |
|  SOLUTION:                                                 |
|    - Split into role interfaces (Workable, Feedable)       |
|    - Each client depends on only the interfaces it needs   |
|    - Classes implement only the interfaces they support    |
|                                                            |
|  TOOLS:                                                    |
|    - Java: interface keyword                               |
|    - Python: ABC (explicit) or Protocol (structural)       |
|                                                            |
|  ALSO APPLIES TO:                                          |
|    - REST APIs (focused endpoints over fat responses)      |
|    - Module exports (export only what clients need)        |
|    - Configuration objects (focused config over global)    |
|                                                            |
+-----------------------------------------------------------+
```

---

## Key Points

- The Interface Segregation Principle says no class should be forced to implement methods it does not use
- Fat interfaces cause empty implementations, UnsupportedOperationException, misleading APIs, and unnecessary coupling
- Split fat interfaces into focused role interfaces where each interface represents a single capability
- Python offers ABCs (explicit enforcement) and Protocols (structural typing) as two tools for ISP
- Do not over-split: if two methods are always used together, they belong in the same interface
- ISP extends beyond classes to REST API design -- do not return unnecessary fields to clients
- The test for whether to split: would any implementor need only a subset of the methods? If yes, split

---

## Practice Questions

1. Explain the Interface Segregation Principle in your own words. What problem does it solve?

2. What are the concrete problems caused by a fat interface? List at least three.

3. In the IWorker example, why is it wrong for RobotWorker to implement eat() as a no-op? What are the consequences?

4. What is the difference between Python ABCs and Protocols for implementing ISP? When would you choose one over the other?

5. Give an example of when a large interface is acceptable and should NOT be split. What criteria make a large interface cohesive?

---

## Exercises

### Exercise 1: Refactor a Fat Interface

The following interface is too fat. Split it into focused role interfaces and update the implementing classes.

```java
public interface ISmartDevice {
    void makeCall(String number);
    void sendSMS(String number, String message);
    void browseWeb(String url);
    void takePhoto();
    void playMusic(String track);
    void setAlarm(String time);
}

public class Smartphone implements ISmartDevice {
    // Implements everything
}

public class BasicPhone implements ISmartDevice {
    // Can only make calls and send SMS
    // Must throw exceptions for browseWeb, takePhoto, playMusic
}

public class SmartSpeaker implements ISmartDevice {
    // Can only play music and set alarms
    // Must throw exceptions for calls, SMS, web, photos
}
```

### Exercise 2: Apply ISP to an API

You have a user API endpoint that returns the following response for every request. Design segregated endpoints or a field selection mechanism that follows ISP.

```json
{
    "id": 1,
    "username": "jsmith",
    "email": "j@example.com",
    "passwordHash": "...",
    "profile": { "bio": "...", "avatar": "..." },
    "orders": [{ ... }, { ... }],
    "paymentMethods": [{ ... }],
    "loginHistory": [{ ... }, { ... }],
    "preferences": { "theme": "dark", "language": "en" }
}
```

### Exercise 3: ISP in Python with Protocols

Rewrite the printer example from this chapter using Python Protocols instead of ABCs. Create a function that works with any Printer, a function that works with any Scanner, and verify that BasicPrinter can be passed to the print function but not the scan function (use mypy or pyright for type checking).

---

## What Is Next?

The Interface Segregation Principle taught you to keep interfaces focused so that clients only depend on what they actually use. The next chapter covers the final SOLID principle: the Dependency Inversion Principle. It addresses the direction of dependencies -- why high-level business logic should never depend directly on low-level infrastructure, and how inverting that dependency makes your code testable, flexible, and modular.
