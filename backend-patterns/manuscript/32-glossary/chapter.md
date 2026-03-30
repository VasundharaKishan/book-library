# Chapter 32: Glossary

A comprehensive reference of design pattern terms and concepts used throughout this
book. Each entry includes a concise definition and the chapter(s) where it is covered
in depth.

---

**Abstract Factory**
A creational pattern that provides an interface for creating families of related objects
without specifying their concrete classes. Produces objects that are designed to work
together. *(Chapter 5)*

**Adapter**
A structural pattern that allows objects with incompatible interfaces to collaborate by
wrapping one object to make it look like another. Also called a Wrapper. *(Chapter 7)*

**Anti-Corruption Layer**
A boundary that translates between two systems or contexts to prevent one system's
design from leaking into another. Often implemented using Adapter or Facade patterns.
*(Chapter 26)*

**API Gateway**
An architectural pattern that provides a single entry point for client requests to a
microservice architecture. Handles routing, authentication, rate limiting, and response
aggregation. *(Chapter 29)*

**Behavioral Pattern**
A category of design patterns concerned with algorithms and the assignment of
responsibilities between objects. Examples include Strategy, Observer, and Command.
*(Chapters 14-22)*

**BFF (Backend for Frontend)**
A variation of the API Gateway pattern where separate gateway instances are created
for different client types (mobile, web, admin), each tailored to that client's data
needs. *(Chapter 29)*

**Bridge**
A structural pattern that separates an abstraction from its implementation so the two
can vary independently. Useful when both the abstraction hierarchy and implementation
hierarchy need to grow. *(Chapter 9)*

**Builder**
A creational pattern that constructs complex objects step by step. Allows producing
different types and representations of an object using the same construction process.
*(Chapter 4)*

**Bulkhead**
A resilience pattern that isolates components so that a failure in one does not cascade
to others. Named after ship compartments that prevent flooding from sinking the entire
vessel. *(Chapter 27)*

**Chain of Responsibility**
A behavioral pattern that passes a request along a chain of handlers. Each handler
decides either to process the request or pass it to the next handler in the chain.
*(Chapter 18)*

**Choreography**
A saga coordination approach where each service listens for events and reacts
independently. No central coordinator. Contrast with Orchestration. *(Chapter 28)*

**Circuit Breaker**
A resilience pattern that prevents an application from repeatedly calling a failing
service. Tracks failures and "opens" the circuit to reject calls, then periodically
allows test calls to check recovery. Three states: Closed, Open, Half-Open. *(Chapter 27)*

**Client-Side Discovery**
A service discovery approach where the client queries the service registry directly
and selects which instance to call, performing its own load balancing. *(Chapter 30)*

**Cloneable**
A Java interface that indicates an object can be cloned using `Object.clone()`. Used
in the Prototype pattern. Python equivalent uses the `copy` module. *(Chapter 6)*

**Command**
A behavioral pattern that encapsulates a request as an object, allowing parameterization
of clients with different requests, queuing of requests, and support for undoable
operations. *(Chapter 17)*

**Compensating Transaction**
A transaction that undoes the effects of a previously completed transaction. Used in the
Saga pattern to maintain consistency when a step in a distributed transaction fails.
*(Chapter 28)*

**Composite**
A structural pattern that composes objects into tree structures to represent part-whole
hierarchies. Lets clients treat individual objects and compositions uniformly through a
shared interface. *(Chapter 12)*

**Concrete Class**
A class that implements all abstract methods and can be instantiated. Contrast with
abstract class or interface. Used throughout all pattern implementations.

**Copy Constructor**
A constructor that creates a new object by copying fields from an existing object of the
same class. An alternative to implementing `Cloneable` in Java for the Prototype pattern.
*(Chapter 6)*

**CQRS (Command Query Responsibility Segregation)**
An architectural pattern that separates the read model (queries) from the write model
(commands). Allows independent optimization and scaling of reads and writes. *(Chapter 25)*

**Creational Pattern**
A category of design patterns that deal with object creation mechanisms, trying to
create objects in a manner suitable to the situation. Examples include Singleton,
Factory Method, and Builder. *(Chapters 1-6)*

**Decorator**
A structural pattern that attaches additional responsibilities to an object dynamically.
Provides a flexible alternative to subclassing for extending functionality. *(Chapter 10)*

**Deep Copy**
A copy operation that duplicates an object and all objects it references, recursively.
The result is fully independent of the original. Contrast with Shallow Copy.
*(Chapter 6)*

**Dependency Injection**
A technique where an object receives its dependencies from external code rather than
creating them internally. Not a GoF pattern but widely used in modern backend development.
*(Chapter 23)*

**Design Pattern**
A general, reusable solution to a commonly occurring problem within a given context in
software design. Not finished code but a template for solving problems.

**Double Dispatch**
A technique where the operation performed depends on the runtime types of two objects.
Used in the Visitor pattern: the element calls a type-specific method on the visitor.
*(Chapter 22)*

**Eager Initialization**
Creating a Singleton instance when the class is loaded, rather than waiting until first
use. Simple and thread-safe but wastes resources if the instance is never used.
*(Chapter 1)*

**Event Bus**
A communication mechanism where components publish events and subscribe to events
without knowing about each other. An implementation of the Observer pattern for
decoupled communication. *(Chapters 20, 31)*

**Event Sourcing**
An architectural pattern that stores the full history of changes to application state as
a sequence of events, rather than storing just the current state. Often used with CQRS.
*(Chapter 25)*

**Extrinsic State**
In the Flyweight pattern, data that varies between instances and is stored externally
(by the client or context object). Examples: position, size, user-specific data.
Contrast with Intrinsic State. *(Chapter 13)*

**Facade**
A structural pattern that provides a simplified interface to a complex subsystem. Hides
the complexity of interacting with multiple classes behind a single, easy-to-use class.
*(Chapter 8)*

**Factory Method**
A creational pattern that defines an interface for creating objects but lets subclasses
decide which class to instantiate. Defers instantiation to subclasses. *(Chapter 3)*

**Flyweight**
A structural pattern that uses sharing to support large numbers of fine-grained objects
efficiently. Splits object state into shared (intrinsic) and unique (extrinsic) parts.
*(Chapter 13)*

**Flyweight Factory**
A factory that manages the creation and caching of Flyweight objects. Ensures that
shared instances are reused rather than duplicated. *(Chapter 13)*

**Gang of Four (GoF)**
The four authors of the seminal book "Design Patterns: Elements of Reusable
Object-Oriented Software" (1994): Erich Gamma, Richard Helm, Ralph Johnson, and
John Vlissides. The book defined 23 classic design patterns.

**Generator (Python)**
A function that uses the `yield` keyword to produce a sequence of values lazily. Each
call to `next()` resumes execution until the next `yield`. A natural implementation of
the Iterator pattern in Python. *(Chapter 21)*

**God Object**
An anti-pattern where one class does too much, accumulating too many responsibilities.
The Mediator pattern can degrade into a God Object if too much logic is placed in the
mediator. *(Chapter 20)*

**Half-Open State**
In the Circuit Breaker pattern, a state where the breaker allows a limited number of
test requests to check if the failing service has recovered. *(Chapter 27)*

**Handler**
In the Chain of Responsibility pattern, an object that processes a request or passes
it to the next handler. Each handler in the chain has a single responsibility.
*(Chapter 18)*

**Health Check**
A mechanism where services report their operational status (healthy/unhealthy) to a
service registry or monitoring system. Used in Service Discovery to route traffic only
to healthy instances. *(Chapter 30)*

**Heartbeat**
A periodic signal sent by a service instance to the service registry to indicate it is
still alive. If heartbeats stop, the registry removes the instance. *(Chapter 30)*

**Idempotent**
An operation that produces the same result whether executed once or multiple times.
Critical for compensating transactions in the Saga pattern and for retry mechanisms.
*(Chapter 28)*

**Intrinsic State**
In the Flyweight pattern, data that is shared across many instances and stored inside
the flyweight object. Must be immutable. Examples: texture data, font definition, icon
SVG. Contrast with Extrinsic State. *(Chapter 13)*

**Iterable**
An object that can produce an Iterator. In Java, implements `Iterable<T>`. In Python,
implements `__iter__()`. Enables use in for-each loops. *(Chapter 21)*

**Iterator**
A behavioral pattern that provides a way to access elements of a collection sequentially
without exposing its underlying representation. In Java: `Iterator<T>`. In Python:
`__iter__()` and `__next__()`. *(Chapter 21)*

**Lazy Initialization**
Creating a Singleton instance only when first requested, rather than at class load time.
Saves resources but requires thread-safety handling. *(Chapter 1)*

**Lazy Evaluation**
Computing values only when they are needed, not in advance. Generators and iterators
use lazy evaluation to handle datasets larger than memory. *(Chapter 21)*

**Leaf**
In the Composite pattern, an object that has no children. Represents the end of a
branch in the tree structure. Performs operations directly rather than delegating.
*(Chapter 12)*

**Load Balancer**
A component that distributes incoming requests across multiple service instances.
Strategies include round-robin, random, least connections, and weighted distribution.
*(Chapters 29, 30)*

**Mediator**
A behavioral pattern that reduces chaotic dependencies between objects by restricting
direct communications and forcing them to collaborate through a mediator object.
*(Chapter 20)*

**Memento**
A behavioral pattern that captures an object's internal state so it can be restored
later without violating encapsulation. Used for undo/redo functionality. *(Chapter 19)*

**Null Object**
A behavioral pattern that provides an object with a defined neutral ("null") behavior.
Eliminates the need for null checks by providing a do-nothing implementation of an
interface.

**Observer**
A behavioral pattern that defines a one-to-many dependency between objects so that when
one object changes state, all dependents are notified and updated automatically. Also
known as Publish-Subscribe. *(Chapter 15)*

**Open/Closed Principle**
A SOLID principle stating that software entities should be open for extension but closed
for modification. The Strategy, Observer, and Visitor patterns embody this principle.

**Orchestration**
A saga coordination approach where a central orchestrator directs each service when to
execute its step. The orchestrator contains the workflow logic. Contrast with
Choreography. *(Chapter 28)*

**Polymorphism**
The ability of different classes to respond to the same method call in their own way.
Fundamental to nearly every design pattern, enabling interface-based programming.

**Prototype**
A creational pattern that creates new objects by cloning existing ones. Useful when
object creation is expensive or when many objects share similar configurations.
*(Chapter 6)*

**Prototype Registry**
A catalog of pre-configured prototype objects stored by name. Clients look up a
prototype by name and clone it, rather than configuring objects from scratch.
*(Chapter 6)*

**Proxy**
A structural pattern that provides a surrogate or placeholder for another object to
control access to it. Types include virtual proxy, protection proxy, and remote proxy.
*(Chapter 11)*

**Rate Limiting**
Controlling the number of requests a client can make within a time period. Common
algorithms include token bucket and sliding window. Typically enforced at the API
Gateway. *(Chapter 29)*

**Repository**
An architectural pattern that mediates between the domain and data mapping layers using
a collection-like interface for accessing domain objects. Abstracts data storage
details from business logic. *(Chapter 23)*

**Saga**
A distributed transaction pattern that breaks a long-lived transaction into a sequence
of local transactions. Each local transaction has a compensating transaction to undo its
effects on failure. *(Chapter 28)*

**Server-Side Discovery**
A service discovery approach where the client sends requests to a load balancer or
router, which queries the registry and forwards the request to an available instance.
*(Chapter 30)*

**Service Discovery**
An architectural pattern where services dynamically register themselves with a central
registry, and clients look up service locations at runtime. Enables dynamic scaling and
deployment. *(Chapter 30)*

**Service Mesh**
An infrastructure layer that handles service-to-service communication, providing
features like service discovery, load balancing, encryption, and observability without
changes to application code. Examples: Istio, Linkerd.

**Service Registry**
A database of available service instances with their network locations. Services
register on startup and deregister on shutdown. The registry removes instances that
fail health checks. *(Chapter 30)*

**Shallow Copy**
A copy operation that duplicates an object but shares references to nested objects. The
copy and original point to the same nested data. Contrast with Deep Copy. *(Chapter 6)*

**Simple Factory**
Not a formal GoF pattern but a commonly used technique where a single method creates
objects based on a parameter. Simpler than Factory Method but less flexible. *(Chapter 2)*

**Singleton**
A creational pattern that ensures a class has only one instance and provides a global
point of access to it. Thread-safe implementations use double-checked locking or eager
initialization. *(Chapter 1)*

**SOLID Principles**
Five principles of object-oriented design: Single Responsibility, Open/Closed, Liskov
Substitution, Interface Segregation, and Dependency Inversion. Design patterns often
embody one or more of these principles.

**State**
A behavioral pattern that lets an object alter its behavior when its internal state
changes. The object appears to change its class. *(Chapter 16)*

**StopIteration**
A Python exception raised by `__next__()` to signal that an iterator has no more
elements. For loops handle this automatically. *(Chapter 21)*

**Strategy**
A behavioral pattern that defines a family of algorithms, encapsulates each one, and
makes them interchangeable. Lets the algorithm vary independently from the clients that
use it. *(Chapter 14)*

**Stream API (Java)**
Java 8+ API for functional-style operations on sequences of elements. Provides lazy
evaluation, filtering, mapping, and reducing. Built on the Iterator concept.
*(Chapter 21)*

**Structural Pattern**
A category of design patterns concerned with how classes and objects are composed to
form larger structures. Examples include Adapter, Decorator, and Composite.
*(Chapters 7-13)*

**Template Method**
A behavioral pattern that defines the skeleton of an algorithm in a superclass but lets
subclasses override specific steps without changing the algorithm's structure.
*(Chapter 19)*

**Thread Safety**
The property of code that functions correctly when accessed by multiple threads
simultaneously. Critical for Singleton (double-checked locking), Flyweight (immutable
shared state), and Service Registry implementations. *(Chapters 1, 13, 30)*

**Token Bucket**
A rate limiting algorithm that represents available capacity as tokens. Each request
consumes a token; tokens are replenished at a fixed rate. When no tokens remain,
requests are rejected. *(Chapter 29)*

**Visitor**
A behavioral pattern that lets you add operations to objects without modifying them.
Uses double dispatch to call the right method based on both the visitor type and the
element type. *(Chapter 22)*

---

## Pattern Categories Quick Reference

### Creational Patterns (How objects are created)

| Pattern          | Purpose                                      | Chapter |
|------------------|----------------------------------------------|---------|
| Singleton        | Ensure one instance globally                 | 1       |
| Simple Factory   | Centralize object creation                   | 2       |
| Factory Method   | Defer creation to subclasses                 | 3       |
| Builder          | Construct complex objects step by step        | 4       |
| Abstract Factory | Create families of related objects            | 5       |
| Prototype        | Clone existing objects                       | 6       |

### Structural Patterns (How objects are composed)

| Pattern          | Purpose                                      | Chapter |
|------------------|----------------------------------------------|---------|
| Adapter          | Make incompatible interfaces work together   | 7       |
| Facade           | Simplify complex subsystem interface         | 8       |
| Bridge           | Separate abstraction from implementation     | 9       |
| Decorator        | Add responsibilities dynamically             | 10      |
| Proxy            | Control access to an object                  | 11      |
| Composite        | Tree structures with uniform interface       | 12      |
| Flyweight        | Share state to save memory                   | 13      |

### Behavioral Patterns (How objects interact)

| Pattern                   | Purpose                                 | Chapter |
|---------------------------|-----------------------------------------|---------|
| Strategy                  | Interchangeable algorithms              | 14      |
| Observer                  | Notify dependents of state changes      | 15      |
| State                     | Behavior changes with internal state    | 16      |
| Command                   | Encapsulate requests as objects         | 17      |
| Chain of Responsibility   | Pass requests along a handler chain     | 18      |
| Template Method / Memento | Algorithm skeleton / state capture      | 19      |
| Mediator                  | Centralize complex communications       | 20      |
| Iterator                  | Sequential collection access            | 21      |
| Visitor                   | Add operations without modifying classes | 22      |

### Architectural Patterns (System-level design)

| Pattern            | Purpose                                     | Chapter |
|--------------------|---------------------------------------------|---------|
| Repository         | Abstract data access                        | 23      |
| Dependency Injection| Externalize dependencies                   | 23      |
| MVC/MVVM           | Separate concerns in applications           | 24      |
| CQRS               | Separate read and write models              | 25      |
| Event Sourcing     | Store state as event history                | 25      |
| Anti-Corruption Layer| Translate between bounded contexts        | 26      |
| Circuit Breaker    | Resilient external service calls            | 27      |
| Bulkhead           | Isolate failure domains                     | 27      |
| Saga               | Distributed transaction management          | 28      |
| API Gateway        | Single entry point for microservices        | 29      |
| Service Discovery  | Dynamic service registration and lookup     | 30      |
