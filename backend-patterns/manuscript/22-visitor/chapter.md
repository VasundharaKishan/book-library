# Chapter 22: Visitor Pattern -- Add Operations Without Modifying Classes

## What You Will Learn

- What the Visitor pattern is and the problem it solves
- How double dispatch works and why it matters
- How to implement Visitor in Java with a tax calculation example
- How to implement Visitor in Python with AST (Abstract Syntax Tree) processing
- When the added complexity of Visitor is justified
- The trade-offs between Visitor and other approaches

## Why This Chapter Matters

You have a stable class hierarchy: different types of products, AST nodes, document
elements, or file system entries. Now you need to add new operations: calculate tax,
export to JSON, validate, generate code, pretty-print. Each operation needs different
logic for each type.

Without Visitor, you either add methods to every class (modifying many files) or write
switch/if-else chains on type (violating the Open/Closed Principle). The Visitor pattern
lets you add new operations by creating new classes, without touching existing ones.

---

## The Problem

You are building an e-commerce system with different product types. Each type needs
different tax calculation logic, different discount rules, and different shipping cost
formulas.

**Without Visitor**, you have two bad options:

**Option 1: Methods in each class (violates Open/Closed Principle)**

```java
// Every time you add a new operation, you modify ALL classes
class Electronics {
    double calculateTax() { ... }
    double calculateShipping() { ... }
    String exportToJson() { ... }
    String generateReport() { ... }
    // New operation = modify this class AND Food AND Clothing AND ...
}

class Food {
    double calculateTax() { ... }     // different logic
    double calculateShipping() { ... } // different logic
    String exportToJson() { ... }
    String generateReport() { ... }
}

// Adding "calculateInsurance()" means modifying 5+ classes
```

**Option 2: Type-checking chains (violates Open/Closed Principle differently)**

```java
double calculateTax(Product p) {
    if (p instanceof Electronics) { return p.getPrice() * 0.15; }
    else if (p instanceof Food) { return p.getPrice() * 0.05; }
    else if (p instanceof Clothing) { return p.getPrice() * 0.08; }
    // Adding a new product type means updating ALL these chains
}
```

---

## The Solution: Visitor Pattern

The Visitor pattern separates algorithms from the objects they operate on. Each new
operation is a new Visitor class. Each element accepts a visitor and tells it what type
it is (double dispatch).

```
+----------------------+         +-----------------------+
|   <<interface>>      |         |    <<interface>>      |
|     Element          |         |      Visitor          |
+----------------------+         +-----------------------+
| + accept(Visitor v)  |<------->| + visitElectronics()  |
+----------------------+         | + visitFood()         |
    ^       ^       ^            | + visitClothing()     |
    |       |       |            +-----------------------+
+-----+ +-----+ +------+            ^            ^
|Elec.| |Food | |Cloth.|        +--------+   +--------+
+-----+ +-----+ +------+        |TaxVisit|   |ShipVis.|
                                +--------+   +--------+

  element.accept(visitor)
    -> visitor.visitElectronics(this)   // double dispatch
```

**How double dispatch works:**

1. Client calls `element.accept(visitor)`
2. Element calls `visitor.visitElectronics(this)` (or whichever type it is)
3. The correct method runs based on BOTH the visitor type AND the element type

This is called "double dispatch" because the operation depends on two types: the visitor
(which operation) and the element (which type of data).

```
Single Dispatch (normal method call):
  element.calculateTax()
  Dispatch based on: element type only

Double Dispatch (visitor):
  element.accept(taxVisitor)
    -> taxVisitor.visitElectronics(this)
  Dispatch based on: element type AND visitor type
```

---

## Java Implementation: Tax Calculator

### Define the Element and Visitor Interfaces

```java
// Visitor interface: one method per element type
public interface ProductVisitor<T> {
    T visitElectronics(Electronics electronics);
    T visitFood(Food food);
    T visitClothing(Clothing clothing);
    T visitDigitalService(DigitalService service);
}

// Element interface: accepts a visitor
public interface Product {
    String getName();
    double getPrice();
    <T> T accept(ProductVisitor<T> visitor);
}
```

### Define the Element Classes

```java
public class Electronics implements Product {
    private final String name;
    private final double price;
    private final double weight;  // for shipping
    private final boolean imported;

    public Electronics(String name, double price, double weight,
                       boolean imported) {
        this.name = name;
        this.price = price;
        this.weight = weight;
        this.imported = imported;
    }

    @Override
    public String getName() { return name; }
    @Override
    public double getPrice() { return price; }
    public double getWeight() { return weight; }
    public boolean isImported() { return imported; }

    @Override
    public <T> T accept(ProductVisitor<T> visitor) {
        return visitor.visitElectronics(this);
    }
}

public class Food implements Product {
    private final String name;
    private final double price;
    private final boolean organic;
    private final boolean perishable;

    public Food(String name, double price, boolean organic,
                boolean perishable) {
        this.name = name;
        this.price = price;
        this.organic = organic;
        this.perishable = perishable;
    }

    @Override
    public String getName() { return name; }
    @Override
    public double getPrice() { return price; }
    public boolean isOrganic() { return organic; }
    public boolean isPerishable() { return perishable; }

    @Override
    public <T> T accept(ProductVisitor<T> visitor) {
        return visitor.visitFood(this);
    }
}

public class Clothing implements Product {
    private final String name;
    private final double price;
    private final String size;

    public Clothing(String name, double price, String size) {
        this.name = name;
        this.price = price;
        this.size = size;
    }

    @Override
    public String getName() { return name; }
    @Override
    public double getPrice() { return price; }
    public String getSize() { return size; }

    @Override
    public <T> T accept(ProductVisitor<T> visitor) {
        return visitor.visitClothing(this);
    }
}

public class DigitalService implements Product {
    private final String name;
    private final double price;
    private final String region;

    public DigitalService(String name, double price, String region) {
        this.name = name;
        this.price = price;
        this.region = region;
    }

    @Override
    public String getName() { return name; }
    @Override
    public double getPrice() { return price; }
    public String getRegion() { return region; }

    @Override
    public <T> T accept(ProductVisitor<T> visitor) {
        return visitor.visitDigitalService(this);
    }
}
```

### Visitor 1: Tax Calculator

```java
public class TaxVisitor implements ProductVisitor<Double> {

    @Override
    public Double visitElectronics(Electronics e) {
        double tax = e.getPrice() * 0.15;  // 15% electronics tax
        if (e.isImported()) {
            tax += e.getPrice() * 0.05;    // 5% import duty
        }
        return tax;
    }

    @Override
    public Double visitFood(Food f) {
        if (f.isOrganic()) {
            return 0.0;  // organic food is tax-exempt
        }
        return f.getPrice() * 0.05;  // 5% food tax
    }

    @Override
    public Double visitClothing(Clothing c) {
        if (c.getPrice() < 50.0) {
            return 0.0;  // cheap clothing is tax-exempt
        }
        return c.getPrice() * 0.08;  // 8% clothing tax
    }

    @Override
    public Double visitDigitalService(DigitalService s) {
        // Digital services taxed by region
        return switch (s.getRegion()) {
            case "EU" -> s.getPrice() * 0.20;  // 20% VAT
            case "US" -> s.getPrice() * 0.07;  // 7% sales tax
            default -> s.getPrice() * 0.10;    // 10% default
        };
    }
}
```

### Visitor 2: Shipping Calculator

```java
public class ShippingVisitor implements ProductVisitor<Double> {

    @Override
    public Double visitElectronics(Electronics e) {
        return e.getWeight() * 2.50;  // $2.50 per kg
    }

    @Override
    public Double visitFood(Food f) {
        if (f.isPerishable()) {
            return 15.00;  // flat rate for cold chain
        }
        return 5.00;  // flat rate for non-perishable
    }

    @Override
    public Double visitClothing(Clothing c) {
        return 3.00;  // flat rate for clothing
    }

    @Override
    public Double visitDigitalService(DigitalService s) {
        return 0.0;  // no shipping for digital services
    }
}
```

### Visitor 3: Summary Report

```java
public class SummaryVisitor implements ProductVisitor<String> {

    @Override
    public String visitElectronics(Electronics e) {
        return String.format("ELECTRONICS: %s ($%.2f, %.1fkg%s)",
                e.getName(), e.getPrice(), e.getWeight(),
                e.isImported() ? ", imported" : "");
    }

    @Override
    public String visitFood(Food f) {
        return String.format("FOOD: %s ($%.2f%s%s)",
                f.getName(), f.getPrice(),
                f.isOrganic() ? ", organic" : "",
                f.isPerishable() ? ", perishable" : "");
    }

    @Override
    public String visitClothing(Clothing c) {
        return String.format("CLOTHING: %s ($%.2f, size %s)",
                c.getName(), c.getPrice(), c.getSize());
    }

    @Override
    public String visitDigitalService(DigitalService s) {
        return String.format("DIGITAL: %s ($%.2f, region: %s)",
                s.getName(), s.getPrice(), s.getRegion());
    }
}
```

### Using the Visitors

```java
import java.util.List;

public class VisitorDemo {
    public static void main(String[] args) {
        List<Product> cart = List.of(
            new Electronics("Laptop", 999.99, 2.5, true),
            new Food("Organic Apples", 6.99, true, true),
            new Food("Rice (5kg)", 12.50, false, false),
            new Clothing("T-Shirt", 29.99, "M"),
            new Clothing("Winter Jacket", 189.99, "L"),
            new DigitalService("Cloud Storage", 9.99, "EU")
        );

        TaxVisitor taxCalc = new TaxVisitor();
        ShippingVisitor shipCalc = new ShippingVisitor();
        SummaryVisitor summary = new SummaryVisitor();

        double totalTax = 0;
        double totalShipping = 0;
        double totalPrice = 0;

        System.out.println("=== Shopping Cart ===");
        for (Product product : cart) {
            String desc = product.accept(summary);
            double tax = product.accept(taxCalc);
            double shipping = product.accept(shipCalc);

            System.out.printf("  %s%n", desc);
            System.out.printf("    Tax: $%.2f | Shipping: $%.2f%n",
                    tax, shipping);

            totalPrice += product.getPrice();
            totalTax += tax;
            totalShipping += shipping;
        }

        System.out.println("\n=== Totals ===");
        System.out.printf("  Subtotal:  $%.2f%n", totalPrice);
        System.out.printf("  Tax:       $%.2f%n", totalTax);
        System.out.printf("  Shipping:  $%.2f%n", totalShipping);
        System.out.printf("  Total:     $%.2f%n",
                totalPrice + totalTax + totalShipping);
    }
}
```

**Output:**
```
=== Shopping Cart ===
  ELECTRONICS: Laptop ($999.99, 2.5kg, imported)
    Tax: $200.00 | Shipping: $6.25
  FOOD: Organic Apples ($6.99, organic, perishable)
    Tax: $0.00 | Shipping: $15.00
  FOOD: Rice (5kg) ($12.50)
    Tax: $0.63 | Shipping: $5.00
  CLOTHING: T-Shirt ($29.99, size M)
    Tax: $0.00 | Shipping: $3.00
  CLOTHING: Winter Jacket ($189.99, size L)
    Tax: $15.20 | Shipping: $3.00
  DIGITAL: Cloud Storage ($9.99, region: EU)
    Tax: $2.00 | Shipping: $0.00

=== Totals ===
  Subtotal:  $1249.45
  Tax:       $217.83
  Shipping:  $32.25
  Total:     $1499.53
```

Adding a new operation (like insurance calculation) means creating a new
`InsuranceVisitor` class. No existing product classes change. That is the power of
Visitor.

---

## Python Implementation: AST Visitor

### Abstract Syntax Tree Processing

Compilers and interpreters are the classic use case for Visitor. An AST represents
parsed code, and you need many operations: evaluate, type-check, optimize, pretty-print,
compile.

```python
from abc import ABC, abstractmethod


# --- AST Node Types (Elements) ---

class ASTNode(ABC):
    @abstractmethod
    def accept(self, visitor):
        pass


class NumberNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def accept(self, visitor):
        return visitor.visit_number(self)

    def __repr__(self):
        return f"Number({self.value})"


class BinaryOpNode(ASTNode):
    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right

    def accept(self, visitor):
        return visitor.visit_binary_op(self)

    def __repr__(self):
        return f"BinaryOp({self.operator})"


class UnaryOpNode(ASTNode):
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand

    def accept(self, visitor):
        return visitor.visit_unary_op(self)


class VariableNode(ASTNode):
    def __init__(self, name):
        self.name = name

    def accept(self, visitor):
        return visitor.visit_variable(self)


class AssignmentNode(ASTNode):
    def __init__(self, name, expression):
        self.name = name
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_assignment(self)


class FunctionCallNode(ASTNode):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

    def accept(self, visitor):
        return visitor.visit_function_call(self)


# --- Visitor Interface ---

class ASTVisitor(ABC):
    @abstractmethod
    def visit_number(self, node): pass

    @abstractmethod
    def visit_binary_op(self, node): pass

    @abstractmethod
    def visit_unary_op(self, node): pass

    @abstractmethod
    def visit_variable(self, node): pass

    @abstractmethod
    def visit_assignment(self, node): pass

    @abstractmethod
    def visit_function_call(self, node): pass
```

### Visitor 1: Evaluator

```python
import math


class EvaluatorVisitor(ASTVisitor):
    """Evaluates the AST and returns a numeric result."""

    def __init__(self):
        self.variables = {}
        self.functions = {
            "sqrt": math.sqrt,
            "abs": abs,
            "max": max,
            "min": min,
        }

    def visit_number(self, node):
        return node.value

    def visit_binary_op(self, node):
        left = node.left.accept(self)
        right = node.right.accept(self)

        ops = {
            "+": lambda a, b: a + b,
            "-": lambda a, b: a - b,
            "*": lambda a, b: a * b,
            "/": lambda a, b: a / b,
            "**": lambda a, b: a ** b,
        }

        if node.operator not in ops:
            raise ValueError(f"Unknown operator: {node.operator}")
        return ops[node.operator](left, right)

    def visit_unary_op(self, node):
        value = node.operand.accept(self)
        if node.operator == "-":
            return -value
        if node.operator == "+":
            return value
        raise ValueError(f"Unknown unary operator: {node.operator}")

    def visit_variable(self, node):
        if node.name not in self.variables:
            raise NameError(f"Undefined variable: {node.name}")
        return self.variables[node.name]

    def visit_assignment(self, node):
        value = node.expression.accept(self)
        self.variables[node.name] = value
        return value

    def visit_function_call(self, node):
        if node.name not in self.functions:
            raise NameError(f"Undefined function: {node.name}")
        args = [arg.accept(self) for arg in node.arguments]
        return self.functions[node.name](*args)
```

### Visitor 2: Pretty Printer

```python
class PrettyPrintVisitor(ASTVisitor):
    """Converts AST back to a readable string."""

    def visit_number(self, node):
        return str(node.value)

    def visit_binary_op(self, node):
        left = node.left.accept(self)
        right = node.right.accept(self)
        return f"({left} {node.operator} {right})"

    def visit_unary_op(self, node):
        operand = node.operand.accept(self)
        return f"({node.operator}{operand})"

    def visit_variable(self, node):
        return node.name

    def visit_assignment(self, node):
        expr = node.expression.accept(self)
        return f"{node.name} = {expr}"

    def visit_function_call(self, node):
        args = ", ".join(arg.accept(self) for arg in node.arguments)
        return f"{node.name}({args})"
```

### Visitor 3: Complexity Analyzer

```python
class ComplexityVisitor(ASTVisitor):
    """Counts the number of operations in an expression."""

    def visit_number(self, node):
        return 0  # no operation

    def visit_binary_op(self, node):
        left_ops = node.left.accept(self)
        right_ops = node.right.accept(self)
        return 1 + left_ops + right_ops

    def visit_unary_op(self, node):
        return 1 + node.operand.accept(self)

    def visit_variable(self, node):
        return 0  # lookup, not computation

    def visit_assignment(self, node):
        return node.expression.accept(self)

    def visit_function_call(self, node):
        arg_ops = sum(arg.accept(self) for arg in node.arguments)
        return 1 + arg_ops  # function call is one operation
```

### Using the Visitors

```python
# Build AST for: x = (3 + 5) * sqrt(16) - 2
ast = AssignmentNode("x",
    BinaryOpNode("-",
        BinaryOpNode("*",
            BinaryOpNode("+",
                NumberNode(3),
                NumberNode(5)
            ),
            FunctionCallNode("sqrt", [NumberNode(16)])
        ),
        NumberNode(2)
    )
)

evaluator = EvaluatorVisitor()
printer = PrettyPrintVisitor()
complexity = ComplexityVisitor()

print("=== AST Processing ===")
print(f"Expression: {ast.accept(printer)}")
print(f"Result:     {ast.accept(evaluator)}")
print(f"Operations: {ast.accept(complexity)}")

# Process more expressions
exprs = [
    ("Simple add", BinaryOpNode("+", NumberNode(2), NumberNode(3))),
    ("Nested", BinaryOpNode("*",
        BinaryOpNode("+", NumberNode(1), NumberNode(2)),
        BinaryOpNode("-", NumberNode(10), NumberNode(4))
    )),
    ("With negation", UnaryOpNode("-", NumberNode(42))),
    ("Function", FunctionCallNode("max",
        [NumberNode(10), NumberNode(20), NumberNode(15)])),
]

print("\n=== Multiple Expressions ===")
for label, expr in exprs:
    result = expr.accept(evaluator)
    pretty = expr.accept(printer)
    ops = expr.accept(complexity)
    print(f"  {label}: {pretty} = {result} ({ops} operations)")

# Variable usage
print("\n=== Variables ===")
assign = AssignmentNode("y", BinaryOpNode("+", NumberNode(10), NumberNode(20)))
print(f"  {assign.accept(printer)}")
assign.accept(evaluator)  # sets y = 30

use_var = BinaryOpNode("*", VariableNode("y"), NumberNode(2))
print(f"  {use_var.accept(printer)} = {use_var.accept(evaluator)}")
```

**Output:**
```
=== AST Processing ===
Expression: x = (((3 + 5) * sqrt(16)) - 2)
Result:     30.0
Operations: 4

=== Multiple Expressions ===
  Simple add: (2 + 3) = 5 (1 operations)
  Nested: ((1 + 2) * (10 - 4)) = 18 (3 operations)
  With negation: (-42) = -42 (1 operations)
  Function: max(10, 20, 15) = 20 (1 operations)

=== Variables ===
  y = (10 + 20)
  (y * 2) = 60
```

Three completely different operations (evaluate, print, count) work on the same AST
without any AST node class being modified. Each operation is a separate Visitor class.

---

## Before vs After Comparison

### Before: Operations Embedded in Classes

```python
class NumberNode:
    def evaluate(self): return self.value
    def pretty_print(self): return str(self.value)
    def count_ops(self): return 0
    def type_check(self): return "number"
    def compile(self): return f"PUSH {self.value}"
    # Adding a new operation means modifying this class
    # AND BinaryOpNode AND UnaryOpNode AND ...

class BinaryOpNode:
    def evaluate(self): ...     # different logic
    def pretty_print(self): ... # different logic
    def count_ops(self): ...    # different logic
    def type_check(self): ...   # different logic
    def compile(self): ...      # different logic
    # Same problem: modifying every node class
```

### After: Operations as Visitors

```python
class NumberNode:
    def accept(self, visitor):
        return visitor.visit_number(self)
    # Never changes again!

# New operations = new classes, no existing code modified
class EvaluatorVisitor: ...
class PrettyPrintVisitor: ...
class ComplexityVisitor: ...
class TypeCheckVisitor: ...      # new, no changes to nodes
class CompilerVisitor: ...       # new, no changes to nodes
```

---

## When Is Visitor Worth the Complexity?

Visitor adds significant complexity. It is justified only in specific situations.

```
+----------------------------------------------------+
| Visitor is WORTH IT when:                          |
+----------------------------------------------------+
| - Element hierarchy is stable (rarely add types)   |
| - Operations change frequently (add new visitors)  |
| - Many operations across many element types        |
| - Operations need access to element-specific data   |
| - You want to keep element classes clean            |
+----------------------------------------------------+

+----------------------------------------------------+
| Visitor is NOT WORTH IT when:                      |
+----------------------------------------------------+
| - Element types change frequently (add new nodes)  |
| - Few operations (1-2 operations, just use methods)|
| - Simple operations (instanceof checks are simpler)|
| - Elements have no type-specific data to access    |
+----------------------------------------------------+
```

The key trade-off: **Visitor makes adding operations easy but adding element types
hard.** Every new element type requires updating every Visitor. Every new Visitor
requires implementing a method for every element type.

---

## When to Use / When NOT to Use

### Use Visitor When

- The class hierarchy is stable but operations change frequently
- You need many different operations across a hierarchy of types
- Operations need access to type-specific data (not just the common interface)
- You want to keep data classes clean and focused on data
- You are building compilers, interpreters, or document processors
- You need to perform operations on a Composite structure (Visitor + Composite)

### Do NOT Use Visitor When

- New element types are added frequently (every visitor must be updated)
- You have only 1-2 operations (direct methods are simpler)
- The element hierarchy is small (2-3 types, not worth the overhead)
- Operations only use the common interface (no need for type-specific dispatch)
- The team is unfamiliar with the pattern (readability trumps elegance)

---

## Common Mistakes

### Mistake 1: Forgetting to Implement All Visit Methods

```java
// WRONG: missing visitDigitalService
public class DiscountVisitor implements ProductVisitor<Double> {
    public Double visitElectronics(Electronics e) { return 0.1; }
    public Double visitFood(Food f) { return 0.05; }
    public Double visitClothing(Clothing c) { return 0.15; }
    // compile error: visitDigitalService not implemented!
}
```

The compiler catches this in Java. In Python, use `@abstractmethod` to get runtime
errors instead of silent bugs.

### Mistake 2: Putting Logic in accept()

```java
// WRONG: logic in the element, not the visitor
public <T> T accept(ProductVisitor<T> visitor) {
    if (this.isOnSale()) {
        return visitor.visitElectronics(this);
    }
    return null;  // skipping visit -- BAD
}

// RIGHT: accept just dispatches, visitor decides
public <T> T accept(ProductVisitor<T> visitor) {
    return visitor.visitElectronics(this);
}
```

### Mistake 3: Using Visitor When Types Change Often

```python
# If you add ProductType every month, Visitor is wrong:
class NewProductType(Product):
    def accept(self, visitor):
        return visitor.visit_new_product(self)  # added

# Now you must update EVERY visitor:
class TaxVisitor:
    def visit_new_product(self, p): ...  # must add

class ShippingVisitor:
    def visit_new_product(self, p): ...  # must add

class SummaryVisitor:
    def visit_new_product(self, p): ...  # must add
# 10 visitors * 1 new type = 10 methods to write!
```

---

## Best Practices

1. **Use Visitor when operations change more than types.** If you add new product types
   monthly but new operations yearly, Visitor is wrong. If types are stable but
   operations grow, Visitor is right.

2. **Use generics for return types.** Java's `ProductVisitor<T>` lets each visitor
   return a different type (Double for tax, String for reports). This is much better
   than Object.

3. **Provide a default visitor.** Create a base visitor class with default implementations
   so that new visitors only override the methods they care about.

4. **Combine with Composite.** Visitor is a natural fit for traversing Composite
   structures. The Composite handles traversal; the Visitor handles per-element logic.

5. **Keep visit methods focused.** Each visit method should do one thing. If your
   visitor grows to hundreds of lines, split it into multiple visitors.

6. **In Python, consider simpler alternatives.** Python's dynamic nature means you can
   use `functools.singledispatch` or dictionary-based dispatch instead of the full
   Visitor pattern.

---

## Quick Summary

The Visitor pattern lets you add new operations to a class hierarchy without modifying
existing classes. Each operation is a separate Visitor class with one method per element
type. Elements accept visitors through double dispatch, enabling type-specific behavior
without type-checking chains.

```
Problem:  Adding new operations requires modifying every class in the hierarchy.
Solution: Define operations in separate Visitor classes; elements accept visitors.
Key:      Double dispatch resolves both the operation AND the element type.
Trade-off: Easy to add operations, hard to add new element types.
```

---

## Key Points

- **Visitor** separates algorithms from the objects they operate on
- **Double dispatch** resolves the correct method based on both visitor and element type
- Adding a new operation = adding a new Visitor class (no existing code changes)
- Adding a new element type = updating every existing Visitor (expensive)
- Use Visitor when types are stable but operations change frequently
- Classic use cases: compilers (AST processing), tax calculators, document exporters
- Java generics (`Visitor<T>`) allow type-safe return values per visitor
- Python alternatives: `singledispatch`, dictionary dispatch, or `match` statements
- Visitor pairs well with Composite for tree structure operations

---

## Practice Questions

1. Explain double dispatch in your own words. Why can't single dispatch (normal method
   calls) achieve the same result?

2. You have an AST with 5 node types and 8 visitor operations. You need to add a 6th
   node type. How many methods must you write or modify? What if you need to add a 9th
   visitor instead?

3. Compare Visitor with the Strategy pattern. Both separate algorithms from data. What
   is the key difference?

4. In Python, `functools.singledispatch` can dispatch based on argument type. How does
   this compare to the Visitor pattern? When would you choose one over the other?

5. A developer argues that Visitor violates encapsulation because visitors access
   element internals. Is this a valid concern? How would you address it?

---

## Exercises

### Exercise 1: Document Export System

Build a document model with visitors:

- Element types: Heading, Paragraph, CodeBlock, Image, Table
- Visitor 1: `HtmlExporter` -- converts to HTML tags
- Visitor 2: `MarkdownExporter` -- converts to Markdown syntax
- Visitor 3: `WordCountVisitor` -- counts words across all text elements
- Build a document with at least one of each element type
- Export the same document in both HTML and Markdown formats

### Exercise 2: Shape Area and Perimeter

Create a geometry system:

- Shapes: Circle, Rectangle, Triangle, Polygon
- Visitor 1: `AreaVisitor` -- calculates area for each shape type
- Visitor 2: `PerimeterVisitor` -- calculates perimeter
- Visitor 3: `DrawVisitor` -- generates ASCII art description of each shape
- Create a list of 5 shapes and process them with each visitor
- Demonstrate adding a new `ScaleVisitor` (doubles dimensions) without modifying shapes

### Exercise 3: Permission Audit System

Build a permission auditing system using Visitor:

- Element types: User, Group, Role, Resource
- Visitor 1: `AuditVisitor` -- generates a security audit report showing who has access
  to what
- Visitor 2: `ComplianceVisitor` -- checks for compliance violations (e.g., no user
  should have both "approve" and "execute" permissions)
- Visitor 3: `VisualizationVisitor` -- generates an ASCII tree showing the permission
  hierarchy
- Build a realistic permission structure with 3+ users, 2+ groups, and 5+ resources

---

## What Is Next?

The next chapter moves from object-oriented design patterns to broader architectural
patterns. We begin with the **Repository Pattern**, which abstracts data access behind
a clean interface. Where Visitor adds operations without modifying classes, Repository
hides storage details without modifying business logic. Both patterns keep your code
clean by separating concerns.
