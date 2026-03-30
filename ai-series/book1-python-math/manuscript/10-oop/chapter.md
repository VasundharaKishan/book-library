# Chapter 10: Object-Oriented Programming — Building with Blueprints

## What You Will Learn

- What objects and classes are
- How classes work as blueprints
- How to use the `__init__` method
- What `self` means and why it is needed
- How to create attributes and methods
- How to create objects from classes
- How inheritance works
- What `__str__` and `__repr__` do
- When to use OOP in data science and machine learning

## Why This Chapter Matters

Look around you. Everything is an object. A car, a phone, a book, a cup of coffee. Each object has **properties** (color, size, weight) and **actions** it can perform (drive, ring, open, pour).

Object-Oriented Programming (OOP) brings this idea into code. You create **blueprints** (classes) that describe what an object looks like and what it can do. Then you build **objects** from those blueprints.

Why does this matter for AI?

- Libraries like PyTorch and TensorFlow use classes for models, layers, and datasets.
- When you build a neural network, you create a class.
- Data pipelines use classes to organize data processing steps.

You do not need to be an OOP expert to start with AI. But understanding the basics will help you **read** and **use** AI code much more effectively.

---

## 10.1 Objects Are Everywhere

Think about a dog.

Every dog has **properties** (also called **attributes**):
- Name
- Breed
- Age
- Color

Every dog can perform **actions** (also called **methods**):
- Bark
- Sit
- Fetch
- Eat

```
+-----------------------------------------------+
|              Object: Dog                       |
+-----------------------------------------------+
|  Attributes (data):     |  Methods (actions):  |
|    - name               |    - bark()          |
|    - breed              |    - sit()           |
|    - age                |    - fetch()         |
|    - color              |    - eat()           |
+-----------------------------------------------+
```

In Python, we put attributes and methods together inside a **class**.

---

## 10.2 Classes as Blueprints

A **class** is a blueprint. An **object** is something built from that blueprint.

Think of a cookie cutter (class) and cookies (objects). One cookie cutter can make many cookies. Each cookie is the same shape, but you can decorate them differently.

```
+-----------------------------------------------+
|  Class vs Object                               |
+-----------------------------------------------+
|                                                |
|  Class (Blueprint):                            |
|    "A Dog has a name, breed, and can bark."    |
|                                                |
|  Objects (Instances):                          |
|    Dog 1: name="Buddy", breed="Labrador"       |
|    Dog 2: name="Max", breed="Poodle"           |
|    Dog 3: name="Bella", breed="Beagle"         |
|                                                |
|  Same blueprint, different data.               |
+-----------------------------------------------+
```

### Your First Class

```python
class Dog:
    pass

# Create objects (instances) from the class
dog1 = Dog()
dog2 = Dog()

print(type(dog1))
print(dog1)
print(dog2)
```

**Expected Output:**
```
<class '__main__.Dog'>
<__main__.Dog object at 0x...>
<__main__.Dog object at 0x...>
```

**Line-by-line explanation:**
- **Line 1:** `class Dog:` defines a new class called `Dog`. Class names use CamelCase (capital first letter).
- **Line 2:** `pass` means "do nothing." It is a placeholder for an empty class.
- **Line 5-6:** We create two Dog objects. Each is a separate instance.
- **Line 8:** `type(dog1)` shows that `dog1` is a `Dog` object.

---

## 10.3 The `__init__` Method — Setting Up Objects

The `__init__` method is called automatically when you create an object. It **initializes** the object with data.

Think of it as filling out a form when a new dog arrives at a shelter. You record its name, breed, and age.

```python
class Dog:
    def __init__(self, name, breed, age):
        self.name = name
        self.breed = breed
        self.age = age

# Create a dog
buddy = Dog("Buddy", "Labrador", 3)
print(f"Name: {buddy.name}")
print(f"Breed: {buddy.breed}")
print(f"Age: {buddy.age}")
```

**Expected Output:**
```
Name: Buddy
Breed: Labrador
Age: 3
```

**Line-by-line explanation:**
- **Line 2:** `__init__` is a special method (notice the double underscores). It runs when you create a new object. `self` refers to the object being created.
- **Line 3:** `self.name = name` stores the `name` argument as an attribute of the object. Now the object "remembers" its name.
- **Line 4-5:** Same for breed and age.
- **Line 8:** `Dog("Buddy", "Labrador", 3)` creates a new Dog and calls `__init__` automatically. You do NOT pass `self` — Python does that for you.

```
+-----------------------------------------------+
|  How __init__ Works                            |
+-----------------------------------------------+
|                                                |
|  buddy = Dog("Buddy", "Labrador", 3)           |
|                                                |
|  Python does this behind the scenes:           |
|                                                |
|  1. Creates a new empty Dog object             |
|  2. Calls __init__(self, "Buddy", "Lab", 3)    |
|     - self.name = "Buddy"                      |
|     - self.breed = "Labrador"                  |
|     - self.age = 3                             |
|  3. Returns the finished object                |
+-----------------------------------------------+
```

---

## 10.4 The `self` Parameter

`self` is the object itself. Every method in a class needs `self` as its first parameter.

Think of `self` as "me." When a dog says "my name is Buddy," it is referring to itself.

```python
class Dog:
    def __init__(self, name, breed):
        self.name = name
        self.breed = breed

    def introduce(self):
        print(f"Hi! I am {self.name}, a {self.breed}.")

# Create two dogs
buddy = Dog("Buddy", "Labrador")
max_dog = Dog("Max", "Poodle")

# Each dog introduces itself
buddy.introduce()
max_dog.introduce()
```

**Expected Output:**
```
Hi! I am Buddy, a Labrador.
Hi! I am Max, a Poodle.
```

**Line-by-line explanation:**
- **Line 6:** `def introduce(self):` — Every method needs `self`. It gives the method access to the object's data.
- **Line 7:** `self.name` means "MY name." When `buddy` calls this, `self` is `buddy`. When `max_dog` calls this, `self` is `max_dog`.
- **Line 14:** `buddy.introduce()` — We do NOT pass `self`. Python fills it in automatically.

```
+-----------------------------------------------+
|  Understanding self                            |
+-----------------------------------------------+
|                                                |
|  buddy.introduce()                             |
|                                                |
|  Python translates this to:                    |
|  Dog.introduce(buddy)                          |
|                                                |
|  So 'self' = buddy in this call.               |
|  self.name = buddy.name = "Buddy"              |
+-----------------------------------------------+
```

---

## 10.5 Attributes and Methods

**Attributes** are data stored in an object. **Methods** are functions that belong to an object.

```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
        print(f"Deposited ${amount}. New balance: ${self.balance}")

    def withdraw(self, amount):
        if amount > self.balance:
            print(f"Cannot withdraw ${amount}. Balance is only ${self.balance}.")
        else:
            self.balance -= amount
            print(f"Withdrew ${amount}. New balance: ${self.balance}")

    def get_balance(self):
        return self.balance

# Create an account
account = BankAccount("Alice", 100)
print(f"Owner: {account.owner}")
print(f"Balance: ${account.get_balance()}")

# Use the methods
account.deposit(50)
account.withdraw(30)
account.withdraw(200)
```

**Expected Output:**
```
Owner: Alice
Balance: $100
Deposited $50. New balance: $150
Withdrew $30. New balance: $120
Cannot withdraw $200. Balance is only $120.
```

**Line-by-line explanation:**
- **Line 2-4:** `__init__` sets up the owner and balance. `balance=0` is a default.
- **Line 6-8:** `deposit()` adds money to the balance.
- **Line 10-15:** `withdraw()` checks if there is enough money first. This is a real-world rule built into the code.
- **Line 17-18:** `get_balance()` returns the current balance.
- **Line 28:** Trying to withdraw more than the balance gives a warning.

```
+-----------------------------------------------+
|  BankAccount Object                            |
+-----------------------------------------------+
|  Attributes:            Methods:               |
|    - owner = "Alice"    - deposit(amount)       |
|    - balance = 100      - withdraw(amount)      |
|                         - get_balance()         |
+-----------------------------------------------+
```

---

## 10.6 Creating Multiple Objects

Each object has its own data. Changing one does not affect others.

```python
class Student:
    def __init__(self, name, grade):
        self.name = name
        self.grade = grade
        self.courses = []

    def enroll(self, course):
        self.courses.append(course)
        print(f"{self.name} enrolled in {course}.")

    def show_info(self):
        print(f"\nStudent: {self.name}")
        print(f"Grade: {self.grade}")
        print(f"Courses: {self.courses}")

# Create different students
alice = Student("Alice", "A")
bob = Student("Bob", "B")

# Each student has their own data
alice.enroll("Math")
alice.enroll("Physics")

bob.enroll("History")
bob.enroll("English")
bob.enroll("Art")

# Show each student's info
alice.show_info()
bob.show_info()
```

**Expected Output:**
```
Alice enrolled in Math.
Alice enrolled in Physics.
Bob enrolled in History.
Bob enrolled in English.
Bob enrolled in Art.

Student: Alice
Grade: A
Courses: ['Math', 'Physics']

Student: Bob
Grade: B
Courses: ['History', 'English', 'Art']
```

**Line-by-line explanation:**
- **Line 5:** `self.courses = []` creates an empty list for each student. Each student gets their OWN list.
- **Lines 22-26:** Alice and Bob enroll in different courses. Their course lists are separate.

---

## 10.7 Inheritance — Building on Existing Blueprints

**Inheritance** lets you create a new class based on an existing class. The new class gets all the attributes and methods of the parent class.

Think of it like a family. A child inherits traits from their parents. They share some features but also have their own unique traits.

```
+-----------------------------------------------+
|  Inheritance                                   |
+-----------------------------------------------+
|                                                |
|  Parent Class: Animal                          |
|    - name, species                             |
|    - speak() -> "..."                          |
|                                                |
|      |--- Child Class: Dog                     |
|      |      speak() -> "Woof!"                 |
|      |                                         |
|      |--- Child Class: Cat                     |
|             speak() -> "Meow!"                 |
+-----------------------------------------------+
```

```python
class Animal:
    def __init__(self, name, species):
        self.name = name
        self.species = species

    def speak(self):
        print(f"{self.name} makes a sound.")

    def info(self):
        print(f"{self.name} is a {self.species}.")

# Dog INHERITS from Animal
class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name, "Dog")  # Call parent's __init__
        self.breed = breed

    def speak(self):  # Override the parent method
        print(f"{self.name} says: Woof!")

    def fetch(self):  # New method, only for dogs
        print(f"{self.name} fetches the ball!")

# Cat INHERITS from Animal
class Cat(Animal):
    def __init__(self, name, color):
        super().__init__(name, "Cat")
        self.color = color

    def speak(self):
        print(f"{self.name} says: Meow!")

    def purr(self):
        print(f"{self.name} purrs...")

# Create objects
buddy = Dog("Buddy", "Labrador")
whiskers = Cat("Whiskers", "orange")

# info() is inherited from Animal
buddy.info()
whiskers.info()

# speak() is overridden in each child class
buddy.speak()
whiskers.speak()

# Unique methods
buddy.fetch()
whiskers.purr()
```

**Expected Output:**
```
Buddy is a Dog.
Whiskers is a Cat.
Buddy says: Woof!
Whiskers says: Meow!
Buddy fetches the ball!
Whiskers purrs...
```

**Line-by-line explanation:**
- **Line 13:** `class Dog(Animal):` means Dog inherits from Animal. Dog is the **child** class. Animal is the **parent** class.
- **Line 15:** `super().__init__(name, "Dog")` calls the parent's `__init__`. This sets up `self.name` and `self.species`.
- **Line 18:** Dog **overrides** the `speak()` method. It replaces the parent's version with its own.
- **Line 21:** `fetch()` is a new method that only Dog has. Cat does not have it.
- **Line 41:** `buddy.info()` works even though Dog did not define `info()`. It **inherited** it from Animal.

```
+-----------------------------------------------+
|  What Dog inherits from Animal:                |
+-----------------------------------------------+
|                                                |
|  Inherited:    info()                          |
|  Overridden:   speak() (Dog version)           |
|  New:          fetch() (Dog only)              |
|  From super(): name, species                   |
|  Own:          breed                           |
+-----------------------------------------------+
```

---

## 10.8 `__str__` and `__repr__` — String Representations

When you print an object, Python shows something like `<__main__.Dog object at 0x...>`. That is not helpful. You can fix this with `__str__` and `__repr__`.

```python
class Book:
    def __init__(self, title, author, pages):
        self.title = title
        self.author = author
        self.pages = pages

    def __str__(self):
        return f"'{self.title}' by {self.author}"

    def __repr__(self):
        return f"Book('{self.title}', '{self.author}', {self.pages})"

# Create a book
book = Book("Python Basics", "John Doe", 350)

# __str__ is used by print()
print(book)

# __repr__ is used in the console and by repr()
print(repr(book))

# __str__ is also used in f-strings
print(f"I am reading {book}.")
```

**Expected Output:**
```
'Python Basics' by John Doe
Book('Python Basics', 'John Doe', 350)
I am reading 'Python Basics' by John Doe.
```

**Line-by-line explanation:**
- **Line 7-8:** `__str__` returns a human-friendly string. Used by `print()` and `str()`.
- **Line 10-11:** `__repr__` returns a developer-friendly string. It should look like the code to recreate the object.
- **Line 18:** `print(book)` calls `__str__` behind the scenes.
- **Line 21:** `repr(book)` calls `__repr__`.

```
+-----------------------------------------------+
|  __str__ vs __repr__                           |
+-----------------------------------------------+
|                                                |
|  __str__:  For humans. Readable and pretty.    |
|            "Python Basics by John Doe"         |
|                                                |
|  __repr__: For developers. Detailed and exact. |
|            "Book('Python Basics', 'John', 350)"|
|                                                |
|  If only one is defined, define __repr__.      |
|  Python will use __repr__ as a fallback.       |
+-----------------------------------------------+
```

---

## 10.9 When to Use OOP in Data Science and ML

You do not need to use OOP for everything. But here are common situations where classes help.

### Example 1: A Simple Data Preprocessor

```python
class DataPreprocessor:
    def __init__(self, data):
        self.original_data = data
        self.cleaned_data = None

    def remove_negatives(self):
        """Remove negative values from the data."""
        self.cleaned_data = [x for x in self.original_data if x >= 0]
        print(f"Removed negatives: {len(self.original_data) - len(self.cleaned_data)} items removed")
        return self

    def normalize(self):
        """Scale data to range 0-1."""
        data = self.cleaned_data if self.cleaned_data else self.original_data
        min_val = min(data)
        max_val = max(data)
        self.cleaned_data = [(x - min_val) / (max_val - min_val) for x in data]
        print("Data normalized to 0-1 range")
        return self

    def summary(self):
        """Print a summary of the data."""
        data = self.cleaned_data if self.cleaned_data else self.original_data
        print(f"\nData Summary:")
        print(f"  Count: {len(data)}")
        print(f"  Min: {min(data):.4f}")
        print(f"  Max: {max(data):.4f}")
        print(f"  Mean: {sum(data)/len(data):.4f}")

# Use it
raw = [45, -3, 82, 67, -1, 91, 23, -8, 55, 73]
print("Original:", raw)

processor = DataPreprocessor(raw)
processor.remove_negatives()
processor.normalize()
processor.summary()

print(f"\nCleaned data: {[round(x, 4) for x in processor.cleaned_data]}")
```

**Expected Output:**
```
Original: [45, -3, 82, 67, -1, 91, 23, -8, 55, 73]
Removed negatives: 3 items removed
Data normalized to 0-1 range

Data Summary:
  Count: 7
  Min: 0.0000
  Max: 1.0000
  Mean: 0.5714

Cleaned data: [0.3235, 0.8676, 0.6471, 1.0, 0.0, 0.4706, 0.7353]
```

### Example 2: A Simple Model Tracker

```python
class ModelTracker:
    def __init__(self, model_name):
        self.model_name = model_name
        self.history = []

    def log_epoch(self, epoch, loss, accuracy):
        """Log the results of one training epoch."""
        entry = {
            "epoch": epoch,
            "loss": round(loss, 4),
            "accuracy": round(accuracy, 4)
        }
        self.history.append(entry)

    def best_epoch(self):
        """Find the epoch with the best accuracy."""
        best = max(self.history, key=lambda x: x["accuracy"])
        return best

    def show_history(self):
        """Display the training history."""
        print(f"\n{self.model_name} - Training History")
        print(f"{'Epoch':<8}{'Loss':<10}{'Accuracy':<10}")
        print("-" * 28)
        for entry in self.history:
            print(f"{entry['epoch']:<8}{entry['loss']:<10}{entry['accuracy']:<10}")

    def __str__(self):
        return f"ModelTracker('{self.model_name}', epochs={len(self.history)})"

# Simulate training
tracker = ModelTracker("MyFirstModel")

# Log some training epochs (simulated)
for i in range(1, 6):
    loss = 1.0 / i
    accuracy = 1 - (1.0 / (i + 1))
    tracker.log_epoch(i, loss, accuracy)

# Show results
tracker.show_history()

best = tracker.best_epoch()
print(f"\nBest epoch: {best['epoch']} (accuracy: {best['accuracy']})")
print(f"\nTracker: {tracker}")
```

**Expected Output:**
```
MyFirstModel - Training History
Epoch   Loss      Accuracy
----------------------------
1       1.0       0.5
2       0.5       0.6667
3       0.3333    0.75
4       0.25      0.8
5       0.2       0.8333

Best epoch: 5 (accuracy: 0.8333)

Tracker: ModelTracker('MyFirstModel', epochs=5)
```

### Example 3: A Dataset Container

```python
class Dataset:
    def __init__(self, name):
        self.name = name
        self.features = []
        self.labels = []

    def add_sample(self, feature, label):
        """Add a data sample."""
        self.features.append(feature)
        self.labels.append(label)

    def size(self):
        """Return the number of samples."""
        return len(self.features)

    def get_sample(self, index):
        """Get a specific sample."""
        return self.features[index], self.labels[index]

    def label_counts(self):
        """Count occurrences of each label."""
        counts = {}
        for label in self.labels:
            counts[label] = counts.get(label, 0) + 1
        return counts

    def __str__(self):
        return f"Dataset('{self.name}', samples={self.size()})"

    def __repr__(self):
        return self.__str__()

# Build a dataset
iris = Dataset("Iris Sample")
iris.add_sample([5.1, 3.5, 1.4, 0.2], "setosa")
iris.add_sample([4.9, 3.0, 1.4, 0.2], "setosa")
iris.add_sample([7.0, 3.2, 4.7, 1.4], "versicolor")
iris.add_sample([6.4, 3.2, 4.5, 1.5], "versicolor")
iris.add_sample([6.3, 3.3, 6.0, 2.5], "virginica")

print(iris)
print(f"Dataset size: {iris.size()}")
print(f"Label distribution: {iris.label_counts()}")

# Get a specific sample
features, label = iris.get_sample(0)
print(f"\nFirst sample: features={features}, label={label}")
```

**Expected Output:**
```
Dataset('Iris Sample', samples=5)
Dataset size: 5
Label distribution: {'setosa': 2, 'versicolor': 2, 'virginica': 1}

First sample: features=[5.1, 3.5, 1.4, 0.2], label=setosa
```

---

## 10.10 When to Use OOP and When Not To

```
+-----------------------------------------------+
|  When to Use OOP                               |
+-----------------------------------------------+
|                                                |
|  USE classes when:                             |
|  - You have data + actions that go together    |
|  - You need multiple similar objects           |
|  - You are building reusable components        |
|  - The library you are using requires it       |
|    (PyTorch models, Flask views, etc.)         |
|                                                |
|  DON'T use classes when:                       |
|  - A simple function would work                |
|  - You only need the class once                |
|  - You are writing a quick script              |
|  - The class has only data and no methods      |
|    (use a dictionary or dataclass instead)     |
+-----------------------------------------------+
```

---

## Common Mistakes

### Mistake 1: Forgetting `self`

```python
class Dog:
    def __init__(self, name):
        self.name = name

    # WRONG - forgot self
    # def bark():
    #     print(f"{name} says Woof!")  # Error!

    # RIGHT
    def bark(self):
        print(f"{self.name} says Woof!")

dog = Dog("Buddy")
dog.bark()
```

**Expected Output:**
```
Buddy says Woof!
```

### Mistake 2: Forgetting to Call `super().__init__()` in Child Classes

```python
class Animal:
    def __init__(self, name):
        self.name = name

# WRONG - forgot to call super().__init__()
class BadDog(Animal):
    def __init__(self, name, breed):
        # Missing: super().__init__(name)
        self.breed = breed

# RIGHT
class GoodDog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)  # Set up parent attributes
        self.breed = breed

try:
    bad = BadDog("Buddy", "Lab")
    print(bad.name)  # Error! name was never set
except AttributeError as e:
    print("Error:", e)

good = GoodDog("Buddy", "Lab")
print(f"Good: {good.name}, {good.breed}")
```

**Expected Output:**
```
Error: 'BadDog' object has no attribute 'name'
Good: Buddy, Lab
```

### Mistake 3: Confusing Class Variables and Instance Variables

```python
class Counter:
    # Class variable - shared by ALL instances
    total_count = 0

    def __init__(self, name):
        # Instance variable - unique to each instance
        self.name = name
        self.count = 0
        Counter.total_count += 1

    def increment(self):
        self.count += 1

a = Counter("A")
b = Counter("B")

a.increment()
a.increment()
b.increment()

print(f"A count: {a.count}")         # Instance variable
print(f"B count: {b.count}")         # Instance variable
print(f"Total created: {Counter.total_count}")  # Class variable
```

**Expected Output:**
```
A count: 2
B count: 1
Total created: 2
```

### Mistake 4: Thinking __init__ Is a Constructor That Returns Something

```python
class Calculator:
    def __init__(self, value):
        self.value = value
        # DON'T return anything from __init__!
        # return self.value  <-- This would cause an error

    def double(self):
        return self.value * 2

calc = Calculator(5)
print(calc.double())
```

**Expected Output:**
```
10
```

---

## Best Practices

1. **Use CamelCase for class names.** `BankAccount`, not `bank_account`.
2. **Use lowercase for method names.** `get_balance()`, not `GetBalance()`.
3. **Always include `self` as the first parameter** in instance methods.
4. **Write `__str__` for every class.** It makes debugging much easier.
5. **Keep classes focused.** A class should represent one thing.
6. **Use inheritance sparingly.** Only inherit when there is a true "is-a" relationship (a Dog IS an Animal).
7. **Write docstrings for classes and methods.** Describe what they do.

---

## Quick Summary

| Concept | Syntax | Example |
|---------|--------|---------|
| Define a class | `class Name:` | `class Dog:` |
| Constructor | `def __init__(self):` | `def __init__(self, name):` |
| Attribute | `self.name = value` | `self.name = "Buddy"` |
| Method | `def action(self):` | `def bark(self):` |
| Create object | `obj = Class()` | `dog = Dog("Buddy")` |
| Inheritance | `class Child(Parent):` | `class Dog(Animal):` |
| Call parent init | `super().__init__()` | `super().__init__(name)` |
| String output | `def __str__(self):` | `return f"{self.name}"` |
| Dev output | `def __repr__(self):` | `return f"Dog('{self.name}')"` |

---

## Key Points to Remember

1. **A class is a blueprint.** An object is an instance built from that blueprint.
2. **`__init__` runs automatically** when you create an object. Use it to set up attributes.
3. **`self` refers to the current object.** Every method needs it as the first parameter.
4. **Attributes store data.** Methods perform actions.
5. **Inheritance lets child classes** reuse code from parent classes.
6. **`super().__init__()`** calls the parent class's constructor.
7. **`__str__` controls what `print()` shows.** `__repr__` is for developers.
8. **Use OOP when data and actions belong together.** Use simple functions when they do not.

---

## Practice Questions

**Question 1:** What is the difference between a class and an object?

<details>
<summary>Answer</summary>

A **class** is a blueprint that defines what attributes and methods something has. An **object** (or instance) is a specific thing created from that blueprint.

Example: `Dog` is a class. `buddy = Dog("Buddy")` creates an object.
</details>

---

**Question 2:** What does `self` refer to?

<details>
<summary>Answer</summary>

`self` refers to the specific object that is calling the method. It allows the method to access and modify the object's own attributes. When you call `buddy.bark()`, `self` is `buddy` inside the `bark()` method.
</details>

---

**Question 3:** What will this code print?
```python
class Car:
    def __init__(self, brand, speed=0):
        self.brand = brand
        self.speed = speed

    def accelerate(self):
        self.speed += 10

car = Car("Toyota")
car.accelerate()
car.accelerate()
print(car.speed)
```

<details>
<summary>Answer</summary>

```
20
```
The car starts with speed 0 (default). Each call to `accelerate()` adds 10. After two calls: 0 + 10 + 10 = 20.
</details>

---

**Question 4:** What is inheritance and when should you use it?

<details>
<summary>Answer</summary>

Inheritance lets a child class reuse attributes and methods from a parent class. Use it when you have a "is-a" relationship:
- A Dog IS an Animal
- A Car IS a Vehicle
- A Student IS a Person

The child class can add new features or override parent features.
</details>

---

**Question 5:** What is the difference between `__str__` and `__repr__`?

<details>
<summary>Answer</summary>

- `__str__` returns a human-readable string. Used by `print()` and `str()`.
- `__repr__` returns a developer-readable string. Should ideally look like valid Python code to recreate the object.

If only one is defined, define `__repr__`. Python uses it as a fallback for `__str__`.
</details>

---

## Exercises

### Exercise 1: Rectangle Class

Create a `Rectangle` class that:
1. Takes `width` and `height` in `__init__`.
2. Has a method `area()` that returns width * height.
3. Has a method `perimeter()` that returns 2 * (width + height).
4. Has a `__str__` method that shows the rectangle info.

Create two rectangles and print their areas and perimeters.

<details>
<summary>Solution</summary>

```python
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        """Calculate the area of the rectangle."""
        return self.width * self.height

    def perimeter(self):
        """Calculate the perimeter of the rectangle."""
        return 2 * (self.width + self.height)

    def __str__(self):
        return f"Rectangle({self.width}x{self.height})"

# Create rectangles
rect1 = Rectangle(5, 3)
rect2 = Rectangle(10, 7)

print(rect1)
print(f"  Area: {rect1.area()}")
print(f"  Perimeter: {rect1.perimeter()}")

print(rect2)
print(f"  Area: {rect2.area()}")
print(f"  Perimeter: {rect2.perimeter()}")
```

**Expected Output:**
```
Rectangle(5x3)
  Area: 15
  Perimeter: 16
Rectangle(10x7)
  Area: 70
  Perimeter: 34
```
</details>

---

### Exercise 2: Student Grade Tracker

Create a `Student` class that:
1. Takes `name` in `__init__` and starts with an empty list of grades.
2. Has `add_grade(grade)` to add a grade.
3. Has `average()` that returns the average grade.
4. Has `highest()` that returns the highest grade.
5. Has `__str__` that shows the student's name and average.

<details>
<summary>Solution</summary>

```python
class Student:
    def __init__(self, name):
        self.name = name
        self.grades = []

    def add_grade(self, grade):
        """Add a grade to the student's record."""
        self.grades.append(grade)

    def average(self):
        """Calculate the average grade."""
        if not self.grades:
            return 0
        return sum(self.grades) / len(self.grades)

    def highest(self):
        """Get the highest grade."""
        if not self.grades:
            return 0
        return max(self.grades)

    def __str__(self):
        return f"Student('{self.name}', avg={self.average():.1f})"

# Test
alice = Student("Alice")
alice.add_grade(90)
alice.add_grade(85)
alice.add_grade(92)
alice.add_grade(88)

print(alice)
print(f"Grades: {alice.grades}")
print(f"Average: {alice.average():.1f}")
print(f"Highest: {alice.highest()}")
```

**Expected Output:**
```
Student('Alice', avg=88.8)
Grades: [90, 85, 92, 88]
Average: 88.8
Highest: 92
```
</details>

---

### Exercise 3: Shape Hierarchy with Inheritance

Create a base class `Shape` with a method `area()` that returns 0. Then create two child classes:
- `Circle` with a `radius` attribute.
- `Square` with a `side` attribute.

Each child class should override `area()` and have a `__str__` method.

<details>
<summary>Solution</summary>

```python
import math

class Shape:
    def __init__(self, name):
        self.name = name

    def area(self):
        """Base area method. Override in child classes."""
        return 0

    def __str__(self):
        return f"{self.name}: area = {self.area():.2f}"

class Circle(Shape):
    def __init__(self, radius):
        super().__init__("Circle")
        self.radius = radius

    def area(self):
        return math.pi * self.radius ** 2

    def __str__(self):
        return f"Circle(radius={self.radius}): area = {self.area():.2f}"

class Square(Shape):
    def __init__(self, side):
        super().__init__("Square")
        self.side = side

    def area(self):
        return self.side ** 2

    def __str__(self):
        return f"Square(side={self.side}): area = {self.area():.2f}"

# Create shapes
circle = Circle(5)
square = Square(4)

print(circle)
print(square)

# Polymorphism: treat different shapes the same way
shapes = [Circle(3), Square(5), Circle(7), Square(2)]
print("\nAll shapes:")
for shape in shapes:
    print(f"  {shape}")

total_area = sum(s.area() for s in shapes)
print(f"\nTotal area: {total_area:.2f}")
```

**Expected Output:**
```
Circle(radius=5): area = 78.54
Square(side=4): area = 16.00

All shapes:
  Circle(radius=3): area = 28.27
  Square(side=5): area = 25.00
  Circle(radius=7): area = 153.94
  Square(side=2): area = 4.00

Total area: 211.21
```
</details>

---

## What Is Next?

Congratulations! You now understand Object-Oriented Programming — one of the most important concepts in software development. In the next chapter, you will learn about **modules and packages**, which let you organize code into separate files and use code written by others. This is how you will access the powerful AI and machine learning libraries that make Python so popular in the field.
