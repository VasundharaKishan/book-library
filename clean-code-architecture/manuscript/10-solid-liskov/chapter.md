# Chapter 10: The Liskov Substitution Principle -- Subtypes Must Keep Their Promises

---

## What You Will Learn

- What the Liskov Substitution Principle (LSP) means and why it is essential for reliable inheritance
- The Rectangle/Square problem explained step by step, showing how intuitive inheritance can be wrong
- Behavioral subtyping: what promises a subtype must keep
- Pre-conditions and post-conditions and how they constrain subtype behavior
- How to fix broken inheritance hierarchies using composition
- The Bird/Penguin fly() problem as a practical before-and-after example
- How duck typing in Python relates to LSP
- How to detect LSP violations in your own code

---

## Why This Chapter Matters

Inheritance is one of the most powerful tools in object-oriented programming, and also one of the most misused. Developers create subclasses based on real-world "is-a" relationships (a Square is a Rectangle, a Penguin is a Bird) without checking whether the subclass actually behaves correctly in every place the parent class is used.

When a subclass violates the behavioral contract of its parent, every piece of code that works with the parent type becomes unreliable. Tests that pass with the parent mysteriously fail with the subclass. Functions that work correctly for years suddenly break when someone passes a new subtype. These are some of the hardest bugs to track down because the code looks correct at the local level.

The Liskov Substitution Principle gives you a precise rule for checking whether your inheritance is safe.

---

## The Liskov Substitution Principle Defined

Barbara Liskov defined this principle in 1987:

> If S is a subtype of T, then objects of type T may be replaced with objects of type S without altering any of the desirable properties of the program.

In simpler terms: **if your code works with a parent type, it must also work correctly with any subtype of that parent, without the code knowing or caring which subtype it received.**

```
+-----------------------------------------------------------+
|           THE LISKOV SUBSTITUTION PRINCIPLE                 |
+-----------------------------------------------------------+
|                                                            |
|  function doSomething(T parent) {                          |
|      parent.method();   // Works correctly with T          |
|  }                                                         |
|                                                            |
|  If S extends T, then:                                     |
|    doSomething(new S())  // MUST also work correctly       |
|                                                            |
|  "Correctly" means:                                        |
|    - Same behavior the caller expects                      |
|    - No surprising exceptions                              |
|    - No violated invariants                                |
|    - No broken post-conditions                             |
|                                                            |
+-----------------------------------------------------------+
```

---

## The Rectangle/Square Problem: Step by Step

This is the classic example. Mathematically, a square is a rectangle. So it seems natural to make `Square` a subclass of `Rectangle`. But this innocent-looking hierarchy is a trap.

### Step 1: Define Rectangle

```java
// Java -- A simple Rectangle class
public class Rectangle {

    protected int width;
    protected int height;

    public void setWidth(int width) {
        this.width = width;
    }

    public void setHeight(int height) {
        this.height = height;
    }

    public int getWidth() {
        return width;
    }

    public int getHeight() {
        return height;
    }

    public int getArea() {
        return width * height;
    }
}
```

### Step 2: Make Square Extend Rectangle

A square is a rectangle where width equals height. So we override the setters to enforce this constraint:

```java
// Java -- Square as a subtype of Rectangle
public class Square extends Rectangle {

    @Override
    public void setWidth(int width) {
        this.width = width;
        this.height = width;  // Keep width == height
    }

    @Override
    public void setHeight(int height) {
        this.width = height;  // Keep width == height
        this.height = height;
    }
}
```

### Step 3: Write Code That Uses Rectangle

```java
// Java -- This function works with any Rectangle
public void resize(Rectangle rect) {
    rect.setWidth(5);
    rect.setHeight(10);

    // A reasonable expectation for a Rectangle:
    assert rect.getArea() == 50;  // 5 * 10 = 50
}
```

### Step 4: Watch It Break

```java
Rectangle rect = new Rectangle();
resize(rect);  // area = 50. Correct.

Rectangle square = new Square();
resize(square);  // area = 100! setHeight(10) also set width to 10.
                 // The assertion fails.
```

```
+-----------------------------------------------------------+
|     THE RECTANGLE/SQUARE PROBLEM                           |
+-----------------------------------------------------------+
|                                                            |
|  Rectangle:                                                |
|  +----------+                                              |
|  |          |  setWidth(5)  -> width=5, height unchanged   |
|  |   5x10   |  setHeight(10) -> height=10, width unchanged|
|  |          |  area = 5 * 10 = 50  (correct)              |
|  +----------+                                              |
|                                                            |
|  Square (pretending to be Rectangle):                      |
|  +----------+                                              |
|  |          |  setWidth(5)  -> width=5, height=5           |
|  |  10x10   |  setHeight(10) -> width=10, height=10       |
|  |          |  area = 10 * 10 = 100  (WRONG!)             |
|  +----------+                                              |
|                                                            |
|  The caller expected setWidth and setHeight to be          |
|  independent. Square violates that expectation.            |
|                                                            |
+-----------------------------------------------------------+
```

The problem is not mathematical. Mathematically, a square is a rectangle. The problem is behavioral. `Rectangle` has an implicit contract: `setWidth` changes only the width, and `setHeight` changes only the height. `Square` violates this contract.

### The Fix: Separate Types

```java
// Java -- GOOD: Rectangle and Square are independent shapes
public interface Shape {
    int getArea();
}

public class Rectangle implements Shape {
    private final int width;
    private final int height;

    public Rectangle(int width, int height) {
        this.width = width;
        this.height = height;
    }

    public int getArea() {
        return width * height;
    }
}

public class Square implements Shape {
    private final int side;

    public Square(int side) {
        this.side = side;
    }

    public int getArea() {
        return side * side;
    }
}
```

Now there is no inheritance relationship. Both implement `Shape`, and neither violates any behavioral contract.

---

## The Bird/Penguin Problem: Before and After

Here is a more practical example. You have a `Bird` class with a `fly()` method. Then you add `Penguin`, which is a bird -- but penguins cannot fly.

### BEFORE: Broken Inheritance

```java
// Java -- BAD: Penguin violates Bird's behavioral contract
public class Bird {

    private String name;

    public Bird(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    public void fly() {
        System.out.println(name + " is flying!");
    }

    public void eat() {
        System.out.println(name + " is eating.");
    }
}

public class Penguin extends Bird {

    public Penguin(String name) {
        super(name);
    }

    @Override
    public void fly() {
        throw new UnsupportedOperationException(
            "Penguins cannot fly!"
        );
    }
}
```

```
+-----------------------------------------------------------+
|     THE BIRD/PENGUIN PROBLEM                               |
+-----------------------------------------------------------+
|                                                            |
|         Bird                                               |
|        /    \                                              |
|    Eagle    Penguin                                        |
|                                                            |
|  Code that uses Bird:                                      |
|                                                            |
|  void migrateFlock(List<Bird> birds) {                     |
|      for (Bird bird : birds) {                             |
|          bird.fly();  // BOOM! Penguin throws exception    |
|      }                                                     |
|  }                                                         |
|                                                            |
|  The caller has every right to expect that Bird.fly()      |
|  works. Penguin breaks that expectation.                   |
|                                                            |
+-----------------------------------------------------------+
```

### The Problem in Python

```python
# Python -- BAD: Same LSP violation
class Bird:

    def __init__(self, name: str):
        self.name = name

    def fly(self) -> None:
        print(f"{self.name} is flying!")

    def eat(self) -> None:
        print(f"{self.name} is eating.")


class Penguin(Bird):

    def fly(self) -> None:
        raise NotImplementedError("Penguins cannot fly!")


# This function expects all birds to fly
def migrate_flock(birds: list[Bird]) -> None:
    for bird in birds:
        bird.fly()  # Crashes on Penguin
```

### AFTER: Fixed with Composition and Proper Abstractions

The fix is to recognize that not all birds can fly. Separate the concept of "bird" from the ability "can fly."

```java
// Java -- GOOD: Separate the ability to fly from being a bird

public abstract class Bird {

    private final String name;

    protected Bird(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    public abstract void eat();
}

// Interface for birds that can fly
public interface Flyable {
    void fly();
}

// Interface for birds that can swim
public interface Swimmable {
    void swim();
}

public class Eagle extends Bird implements Flyable {

    public Eagle(String name) {
        super(name);
    }

    @Override
    public void eat() {
        System.out.println(getName() + " hunts fish.");
    }

    @Override
    public void fly() {
        System.out.println(getName() + " soars through the sky!");
    }
}

public class Penguin extends Bird implements Swimmable {

    public Penguin(String name) {
        super(name);
    }

    @Override
    public void eat() {
        System.out.println(getName() + " eats fish from the sea.");
    }

    @Override
    public void swim() {
        System.out.println(getName() + " swims gracefully!");
    }
}

public class Duck extends Bird implements Flyable, Swimmable {

    public Duck(String name) {
        super(name);
    }

    @Override
    public void eat() {
        System.out.println(getName() + " eats bread.");
    }

    @Override
    public void fly() {
        System.out.println(getName() + " flies over the pond.");
    }

    @Override
    public void swim() {
        System.out.println(getName() + " paddles on the lake.");
    }
}
```

```
+-----------------------------------------------------------+
|     FIXED BIRD HIERARCHY                                   |
+-----------------------------------------------------------+
|                                                            |
|           Bird (abstract)                                  |
|          /      |      \                                   |
|      Eagle    Duck    Penguin                               |
|        |       |  |      |                                 |
|     Flyable  Flyable Swimmable                             |
|             Swimmable                                      |
|                                                            |
|  void migrateFlock(List<Flyable> flyers) {                 |
|      for (Flyable f : flyers) {                            |
|          f.fly();  // SAFE: only Flyable birds are here    |
|      }                                                     |
|  }                                                         |
|                                                            |
|  Eagle and Duck go in. Penguin does not.                   |
|  No exceptions. No surprises.                              |
|                                                            |
+-----------------------------------------------------------+
```

Now the `migrateFlock` function takes `List<Flyable>` instead of `List<Bird>`. Penguins simply are not passed to it. The type system prevents the mistake.

### Python Version: Fixed

```python
# Python -- GOOD: Composition-based design
from abc import ABC, abstractmethod
from typing import Protocol


class Bird(ABC):

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def eat(self) -> None:
        pass


class Flyable(Protocol):
    name: str
    def fly(self) -> None: ...


class Swimmable(Protocol):
    name: str
    def swim(self) -> None: ...


class Eagle(Bird):

    def eat(self) -> None:
        print(f"{self.name} hunts fish.")

    def fly(self) -> None:
        print(f"{self.name} soars through the sky!")


class Penguin(Bird):

    def eat(self) -> None:
        print(f"{self.name} eats fish from the sea.")

    def swim(self) -> None:
        print(f"{self.name} swims gracefully!")


class Duck(Bird):

    def eat(self) -> None:
        print(f"{self.name} eats bread.")

    def fly(self) -> None:
        print(f"{self.name} flies over the pond.")

    def swim(self) -> None:
        print(f"{self.name} paddles on the lake.")


def migrate_flock(flyers: list[Flyable]) -> None:
    for flyer in flyers:
        flyer.fly()  # Safe: only objects with fly() are accepted
```

---

## Pre-Conditions and Post-Conditions

The Liskov Substitution Principle can be stated precisely in terms of conditions:

- **Pre-conditions**: What must be true before a method is called
- **Post-conditions**: What is guaranteed to be true after a method returns
- **Invariants**: What is always true about the object's state

The rule is:

```
+-----------------------------------------------------------+
|     LSP CONDITIONS RULE                                    |
+-----------------------------------------------------------+
|                                                            |
|  A subtype may:                                            |
|    - WEAKEN pre-conditions (accept more inputs)            |
|    - STRENGTHEN post-conditions (guarantee more outputs)   |
|                                                            |
|  A subtype must NOT:                                       |
|    - STRENGTHEN pre-conditions (reject valid inputs)       |
|    - WEAKEN post-conditions (guarantee less)               |
|                                                            |
+-----------------------------------------------------------+
```

### Example: Weakening Pre-Conditions Is Safe

```java
// Java -- Base class: accepts positive integers only
public class Validator {
    public boolean validate(int value) {
        if (value <= 0) {
            throw new IllegalArgumentException("Must be positive");
        }
        return value < 1000;
    }
}

// Subclass: accepts all integers (WEAKER pre-condition = OK)
public class LenientValidator extends Validator {
    @Override
    public boolean validate(int value) {
        // Accepts zero and negative values too -- this is safe
        // because any code that passed positive values still works
        return Math.abs(value) < 1000;
    }
}
```

### Example: Strengthening Pre-Conditions Breaks LSP

```java
// Java -- BAD: Subclass rejects inputs the parent accepts
public class StrictValidator extends Validator {
    @Override
    public boolean validate(int value) {
        if (value <= 0 || value > 500) {  // STRICTER than parent!
            throw new IllegalArgumentException("Must be between 1 and 500");
        }
        return true;
    }
}

// Code that works with Validator (values up to 999) breaks with StrictValidator
Validator v = new StrictValidator();
v.validate(750);  // BOOM! Parent would accept this, subclass rejects it
```

---

## LSP Violations in the Wild

Here are common real-world LSP violations to watch for:

### 1. Throwing Exceptions the Parent Does Not

```python
# Python -- BAD: Subclass throws where parent does not
class FileStorage:
    def save(self, key: str, data: bytes) -> None:
        with open(f"/data/{key}", "wb") as f:
            f.write(data)


class ReadOnlyStorage(FileStorage):
    def save(self, key: str, data: bytes) -> None:
        raise PermissionError("Storage is read-only!")  # LSP violation
```

### 2. Ignoring Method Parameters

```java
// Java -- BAD: Subclass ignores parameters
public class Cache {
    public void put(String key, Object value, Duration ttl) {
        // Stores with the given TTL
        store.put(key, value, ttl);
    }
}

public class PermanentCache extends Cache {
    @Override
    public void put(String key, Object value, Duration ttl) {
        // Ignores TTL entirely -- values never expire
        // Callers who rely on TTL will be surprised
        store.put(key, value, Duration.ofMillis(Long.MAX_VALUE));
    }
}
```

### 3. Returning Different Types

```python
# Python -- BAD: Subclass returns different type
class UserRepository:
    def find_by_id(self, user_id: int) -> User:
        return self.db.query(User, user_id)


class CachingUserRepository(UserRepository):
    def find_by_id(self, user_id: int) -> dict:  # Returns dict, not User!
        cached = self.cache.get(user_id)
        if cached:
            return cached  # This is a dict, not a User object
        return super().find_by_id(user_id)
```

---

## Duck Typing and LSP in Python

Python's duck typing means LSP is about behavior, not formal inheritance. Two classes that do not share a parent can still satisfy LSP if they implement the same behavioral contract.

```python
# Python -- Duck typing: LSP is about behavior, not hierarchy

class InMemoryStore:
    def __init__(self):
        self._data = {}

    def get(self, key: str) -> str | None:
        return self._data.get(key)

    def put(self, key: str, value: str) -> None:
        self._data[key] = value


class RedisStore:
    def __init__(self, client):
        self._client = client

    def get(self, key: str) -> str | None:
        return self._client.get(key)

    def put(self, key: str, value: str) -> None:
        self._client.set(key, value)


# Both work interchangeably -- LSP is satisfied through duck typing
def cache_user_profile(store, user_id: str, profile: str) -> None:
    store.put(f"user:{user_id}", profile)

def get_user_profile(store, user_id: str) -> str | None:
    return store.get(f"user:{user_id}")
```

Neither class inherits from the other, and neither inherits from a common base class. But both satisfy the same behavioral contract (get and put with the same signatures and semantics), so they are interchangeable. This is LSP through duck typing.

---

## How to Detect LSP Violations

Here is a checklist for spotting LSP problems:

```
+-----------------------------------------------------------+
|     LSP VIOLATION DETECTOR                                 |
+-----------------------------------------------------------+
|                                                            |
|  Check for these red flags:                                |
|                                                            |
|  [ ] Does the subclass throw exceptions the parent        |
|      does not declare?                                     |
|                                                            |
|  [ ] Does the subclass ignore parameters that the         |
|      parent uses?                                          |
|                                                            |
|  [ ] Does the subclass return a different type than        |
|      the parent?                                           |
|                                                            |
|  [ ] Does the subclass have a no-op implementation         |
|      of a parent method?                                   |
|                                                            |
|  [ ] Does code using the parent type need isinstance       |
|      checks to work with the subclass?                     |
|                                                            |
|  [ ] Does the subclass violate the parent's invariants?    |
|      (e.g., Square breaking Rectangle's independent        |
|       width/height)                                        |
|                                                            |
|  If you checked any box, you likely have an LSP violation. |
|                                                            |
+-----------------------------------------------------------+
```

The **instanceof smell**: If you ever find yourself writing `if (obj instanceof SpecificSubclass)` to handle a subtype differently, that subtype is not properly substitutable.

```java
// Java -- BAD: instanceof checks indicate LSP violations
public void feedAnimal(Animal animal) {
    if (animal instanceof Snake) {
        // Snakes eat differently -- this is an LSP smell
        ((Snake) animal).swallowWhole(food);
    } else {
        animal.eat(food);
    }
}
```

---

## Common Mistakes

1. **Inheriting based on "is-a" in the real world.** A square "is a" rectangle mathematically, but it is not a valid subtype behaviorally. Design based on behavioral compatibility, not real-world taxonomy.

2. **Empty or no-op overrides.** Overriding a method to do nothing is almost always an LSP violation. If the subtype cannot fulfill the method's contract, it should not inherit it.

3. **Throwing UnsupportedOperationException.** This is the Penguin.fly() anti-pattern. If a subtype cannot support an operation, it should not inherit the interface that declares it.

4. **Adding pre-conditions in the subtype.** If the parent accepts any positive number, the subtype cannot suddenly require numbers under 100.

5. **Confusing code reuse with subtyping.** Do not use inheritance just to reuse some methods from a parent class. If the subtype is not fully substitutable, use composition instead.

---

## Best Practices

1. **Design by contract.** Define clear pre-conditions, post-conditions, and invariants for your base types. Verify that every subtype honors them.

2. **Prefer composition over inheritance.** If you are unsure whether a subtype relationship is valid, use composition. It is always safe.

3. **Use interfaces to define capabilities.** Instead of a deep class hierarchy, use small interfaces (Flyable, Swimmable) that describe what an object can do.

4. **Write tests against the base type.** If your tests pass with the parent class but fail with a subclass, you have an LSP violation. Every subclass should pass every test written for the parent.

5. **Avoid empty overrides.** If a subclass method does nothing, refactor the hierarchy so the method does not exist in that branch.

6. **Use the Liskov test.** For every subclass, ask: "Can I use this subclass everywhere the parent is used without any caller knowing or caring?" If the answer is no, refactor.

---

## Quick Summary

```
+-----------------------------------------------------------+
|              LSP CHEAT SHEET                               |
+-----------------------------------------------------------+
|                                                            |
|  PRINCIPLE:                                                |
|    Subtypes must be substitutable for their base types     |
|    without altering program correctness                    |
|                                                            |
|  KEY RULE:                                                 |
|    - Subtypes may WEAKEN pre-conditions                    |
|    - Subtypes may STRENGTHEN post-conditions               |
|    - Subtypes must NOT do the reverse                      |
|                                                            |
|  RED FLAGS:                                                |
|    - UnsupportedOperationException in a subclass           |
|    - instanceof checks in code using the base type         |
|    - No-op method overrides                                |
|    - Subclass ignoring parent method parameters            |
|                                                            |
|  FIXES:                                                    |
|    - Use composition instead of inheritance                |
|    - Use interfaces for capabilities (Flyable, Swimmable)  |
|    - Make separate types instead of forcing hierarchy      |
|                                                            |
+-----------------------------------------------------------+
```

---

## Key Points

- The Liskov Substitution Principle requires that any subtype can replace its parent type without breaking the program
- The Rectangle/Square problem shows that real-world "is-a" relationships do not always translate into valid inheritance hierarchies
- A subtype violates LSP when it throws unexpected exceptions, ignores parameters, returns different types, or has no-op implementations of parent methods
- Pre-conditions can be weakened (accept more) but not strengthened (reject more) in subtypes; post-conditions can be strengthened but not weakened
- The fix for LSP violations is usually composition over inheritance: separate capabilities into interfaces and let each type implement only what it genuinely supports
- Python's duck typing means LSP is about behavioral compatibility, not formal class hierarchy
- The instanceof check is a code smell that often indicates an LSP violation

---

## Practice Questions

1. Explain the Liskov Substitution Principle in your own words. Why is it important for code that works with polymorphism?

2. Walk through the Rectangle/Square problem step by step. What implicit contract does Rectangle have that Square violates?

3. What is the difference between strengthening and weakening pre-conditions? Which is safe for a subtype to do, and which violates LSP?

4. Why is throwing UnsupportedOperationException in a subclass method an LSP violation? What should you do instead?

5. How does Python's duck typing relate to LSP? Can you have an LSP violation in Python even without formal inheritance?

---

## Exercises

### Exercise 1: Fix the Bird Hierarchy

The following code has an LSP violation. Refactor it using interfaces and composition so that all types are properly substitutable.

```python
class Vehicle:
    def start_engine(self):
        print("Engine started")

    def accelerate(self):
        print("Accelerating")

    def refuel(self):
        print("Refueling with gasoline")

class ElectricCar(Vehicle):
    def refuel(self):
        raise NotImplementedError("Electric cars don't use fuel!")

    def recharge(self):
        print("Charging battery")
```

### Exercise 2: Write Substitutability Tests

Write a set of tests that verify LSP for a `Stack` class. The tests should pass for any valid implementation of `Stack` (array-based, linked-list-based, etc.). Then create a `BoundedStack` subclass with a maximum capacity and check whether it passes all the original tests. If it does not, explain the violation and fix it.

### Exercise 3: Detect LSP Violations in Real Code

Find an open-source Java or Python project and look for classes that use inheritance. Identify at least two potential LSP violations using the checklist from this chapter. Describe what the violation is and how you would fix it.

---

## What Is Next?

The Liskov Substitution Principle ensures your subtypes can safely replace their parents. The next chapter covers the Interface Segregation Principle, which addresses a different problem: what happens when an interface grows too large and forces its implementors to provide methods they do not need. You will learn how to split fat interfaces into focused, role-based interfaces that keep your code flexible and your implementations clean.
