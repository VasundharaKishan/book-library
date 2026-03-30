# Chapter 17: Template Method Pattern -- Define Algorithm Skeleton, Let Subclasses Fill in Steps

## What You Will Learn

- How to define a fixed algorithm structure while allowing steps to vary
- Implementing Template Method in Java with an `AbstractDataProcessor` for ETL
- Building a Python `ReportGenerator` with customizable steps
- Understanding hook methods and when to use them
- Real-world applications: ETL pipelines, document generators, test frameworks
- Template Method vs Strategy: when to use each

## Why This Chapter Matters

Many backend processes follow the same overall structure but differ in the details. Every ETL pipeline extracts data, transforms it, and loads it. Every report generator fetches data, formats it, and outputs it. Every test runs setup, the test itself, and teardown. The structure is identical -- only the individual steps change.

If you copy-paste the structure and modify the details each time, you end up with duplicated code that drifts apart over time. The Template Method pattern solves this by putting the algorithm skeleton in a base class and letting subclasses fill in the specific steps. The structure stays consistent, and new variants only need to implement what is different.

---

## The Problem: Duplicated Algorithm Structure

```java
// CSVDataProcessor.java
public class CSVDataProcessor {
    public void process() {
        System.out.println("Opening CSV file...");
        System.out.println("Reading CSV rows...");        // Step 1: Extract
        System.out.println("Converting strings to ints..."); // Step 2: Transform
        System.out.println("Validating data...");           // Shared step
        System.out.println("Inserting into MySQL...");      // Step 3: Load
        System.out.println("Closing connections...");       // Shared step
    }
}

// JSONDataProcessor.java
public class JSONDataProcessor {
    public void process() {
        System.out.println("Opening JSON file...");
        System.out.println("Parsing JSON objects...");     // Step 1: Extract
        System.out.println("Flattening nested objects..."); // Step 2: Transform
        System.out.println("Validating data...");           // Shared step (DUPLICATED)
        System.out.println("Inserting into MySQL...");      // Step 3: Load (DUPLICATED)
        System.out.println("Closing connections...");       // Shared step (DUPLICATED)
    }
}

// The shared steps are copy-pasted. If validation logic changes,
// you must update EVERY processor. This does not scale.
```

```
The Duplication Problem:

  CSVProcessor       JSONProcessor      XMLProcessor
  +------------+     +------------+     +------------+
  | extract()  |     | extract()  |     | extract()  |
  | transform()|     | transform()|     | transform()|
  | validate() |     | validate() |     | validate() |  <-- Same in all three
  | load()     |     | load()     |     | load()     |  <-- Same in all three
  | cleanup()  |     | cleanup()  |     | cleanup()  |  <-- Same in all three
  +------------+     +------------+     +------------+

  3 classes x 3 duplicated methods = maintenance nightmare
```

---

## The Solution: Template Method Pattern

```
Template Method Structure:

  +------------------------------------------+
  |       AbstractDataProcessor              |
  |                                          |
  |  process()  <-- TEMPLATE METHOD (final)  |
  |  {                                       |
  |      extract();     // abstract          |
  |      transform();   // abstract          |
  |      validate();    // concrete (shared)  |
  |      load();        // abstract          |
  |      cleanup();     // concrete (shared)  |
  |  }                                       |
  |                                          |
  |  abstract extract();                     |
  |  abstract transform();                   |
  |  abstract load();                        |
  |  validate() { ... }  // shared logic     |
  |  cleanup()  { ... }  // shared logic     |
  +------------------------------------------+
           ^                ^
           |                |
  +----------------+ +----------------+
  | CSVProcessor   | | JSONProcessor  |
  |                | |                |
  | extract() {...}| | extract() {...}|
  | transform(){..}| | transform(){..}|
  | load() {...}   | | load() {...}   |
  +----------------+ +----------------+

  Subclasses ONLY implement what differs.
  The algorithm structure is defined ONCE.
```

---

## Java Implementation: AbstractDataProcessor (ETL)

### Step 1: Define the Abstract Base Class

```java
// AbstractDataProcessor.java
public abstract class AbstractDataProcessor {

    // The TEMPLATE METHOD -- defines the algorithm skeleton
    // 'final' prevents subclasses from changing the structure
    public final void process() {
        System.out.println("=== Starting " + getProcessorName() + " ===");

        List<Map<String, Object>> rawData = extract();
        System.out.println("  Extracted " + rawData.size() + " records");

        List<Map<String, Object>> transformedData = transform(rawData);
        System.out.println("  Transformed " + transformedData.size() + " records");

        // Hook method -- subclasses CAN override, but do not have to
        if (shouldValidate()) {
            validate(transformedData);
            System.out.println("  Validation passed");
        }

        int loaded = load(transformedData);
        System.out.println("  Loaded " + loaded + " records");

        cleanup();
        System.out.println("=== Completed " + getProcessorName() + " ===\n");
    }

    // Abstract methods -- subclasses MUST implement these
    protected abstract List<Map<String, Object>> extract();
    protected abstract List<Map<String, Object>> transform(
        List<Map<String, Object>> data);
    protected abstract int load(List<Map<String, Object>> data);
    protected abstract String getProcessorName();

    // Hook method -- default behavior that subclasses CAN override
    protected boolean shouldValidate() {
        return true;  // Validate by default
    }

    // Concrete methods -- shared logic, same for all subclasses
    protected void validate(List<Map<String, Object>> data) {
        for (Map<String, Object> record : data) {
            if (record.isEmpty()) {
                throw new IllegalStateException("Empty record found");
            }
        }
    }

    protected void cleanup() {
        System.out.println("  Releasing resources...");
    }
}
```

### Step 2: Implement Concrete Processors

```java
// CSVDataProcessor.java
public class CSVDataProcessor extends AbstractDataProcessor {

    @Override
    protected List<Map<String, Object>> extract() {
        System.out.println("  Reading CSV file: data.csv");
        // Simulate CSV parsing
        return List.of(
            Map.of("name", "Alice", "age", "30", "city", "NYC"),
            Map.of("name", "Bob", "age", "25", "city", "LA"),
            Map.of("name", "Charlie", "age", "35", "city", "Chicago")
        );
    }

    @Override
    protected List<Map<String, Object>> transform(
            List<Map<String, Object>> data) {
        System.out.println("  Converting string ages to integers");
        List<Map<String, Object>> result = new ArrayList<>();
        for (Map<String, Object> record : data) {
            Map<String, Object> transformed = new HashMap<>(record);
            transformed.put("age", Integer.parseInt((String) record.get("age")));
            result.add(transformed);
        }
        return result;
    }

    @Override
    protected int load(List<Map<String, Object>> data) {
        System.out.println("  Inserting into 'users' table");
        // Simulate database insert
        return data.size();
    }

    @Override
    protected String getProcessorName() {
        return "CSV Data Processor";
    }
}

// JSONDataProcessor.java
public class JSONDataProcessor extends AbstractDataProcessor {

    @Override
    protected List<Map<String, Object>> extract() {
        System.out.println("  Parsing JSON file: data.json");
        return List.of(
            Map.of("product", "Laptop", "price", 999.99,
                   "specs", Map.of("ram", "16GB", "storage", "512GB")),
            Map.of("product", "Phone", "price", 699.99,
                   "specs", Map.of("ram", "8GB", "storage", "256GB"))
        );
    }

    @Override
    protected List<Map<String, Object>> transform(
            List<Map<String, Object>> data) {
        System.out.println("  Flattening nested JSON objects");
        List<Map<String, Object>> result = new ArrayList<>();
        for (Map<String, Object> record : data) {
            Map<String, Object> flat = new HashMap<>();
            flat.put("product", record.get("product"));
            flat.put("price", record.get("price"));
            @SuppressWarnings("unchecked")
            Map<String, String> specs = (Map<String, String>) record.get("specs");
            flat.put("ram", specs.get("ram"));
            flat.put("storage", specs.get("storage"));
            result.add(flat);
        }
        return result;
    }

    @Override
    protected int load(List<Map<String, Object>> data) {
        System.out.println("  Inserting into 'products' table");
        return data.size();
    }

    @Override
    protected String getProcessorName() {
        return "JSON Data Processor";
    }

    // Override hook -- skip validation for trusted JSON sources
    @Override
    protected boolean shouldValidate() {
        return false;
    }
}
```

### Step 3: Run the Processors

```java
// Main.java
public class Main {
    public static void main(String[] args) {
        AbstractDataProcessor csvProcessor = new CSVDataProcessor();
        csvProcessor.process();

        AbstractDataProcessor jsonProcessor = new JSONDataProcessor();
        jsonProcessor.process();
    }
}
```

**Output:**
```
=== Starting CSV Data Processor ===
  Reading CSV file: data.csv
  Extracted 3 records
  Converting string ages to integers
  Transformed 3 records
  Validation passed
  Inserting into 'users' table
  Loaded 3 records
  Releasing resources...
=== Completed CSV Data Processor ===

=== Starting JSON Data Processor ===
  Parsing JSON file: data.json
  Extracted 2 records
  Flattening nested JSON objects
  Transformed 2 records
  Inserting into 'products' table
  Loaded 2 records
  Releasing resources...
=== Completed JSON Data Processor ===
```

Notice how the JSON processor skipped validation because it overrode the `shouldValidate()` hook.

---

## Hook Methods Explained

```
Types of Methods in Template Method:

  +------------------------------------------------------------+
  | Abstract Methods (MUST override)                            |
  |   extract(), transform(), load()                            |
  |   Subclass MUST provide implementation.                     |
  +------------------------------------------------------------+
  | Hook Methods (CAN override)                                 |
  |   shouldValidate(), beforeLoad(), afterExtract()            |
  |   Have a default implementation. Override only if needed.   |
  +------------------------------------------------------------+
  | Concrete Methods (SHOULD NOT override)                      |
  |   validate(), cleanup()                                     |
  |   Shared logic. Same for all subclasses.                    |
  +------------------------------------------------------------+
  | Template Method (CANNOT override)                           |
  |   process()  -- marked 'final'                              |
  |   Defines the algorithm structure. Never changed.           |
  +------------------------------------------------------------+

  Hook methods give subclasses OPTIONAL control points
  without forcing them to implement anything.
```

---

## Python Implementation: ReportGenerator

```python
# report_generator.py
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class ReportGenerator(ABC):
    """Template Method pattern for generating reports."""

    def generate(self) -> str:
        """The template method -- defines the report generation algorithm."""
        print(f"=== Generating {self.get_report_name()} ===")

        # Step 1: Fetch data
        data = self.fetch_data()
        print(f"  Fetched {len(data)} records")

        # Step 2: Hook -- filter data (optional)
        data = self.filter_data(data)
        print(f"  After filtering: {len(data)} records")

        # Step 3: Format the report
        formatted = self.format_report(data)

        # Step 4: Hook -- add header/footer (optional)
        header = self.get_header()
        footer = self.get_footer()
        report = f"{header}\n{formatted}\n{footer}"

        # Step 5: Output the report
        output_path = self.output_report(report)
        print(f"  Report saved to: {output_path}")

        print(f"=== Completed {self.get_report_name()} ===\n")
        return report

    # Abstract methods -- MUST implement
    @abstractmethod
    def fetch_data(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def format_report(self, data: list[dict[str, Any]]) -> str:
        pass

    @abstractmethod
    def get_report_name(self) -> str:
        pass

    # Hook methods -- CAN override
    def filter_data(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Override to filter data. Default: no filtering."""
        return data

    def get_header(self) -> str:
        return f"--- {self.get_report_name()} ---"

    def get_footer(self) -> str:
        return f"--- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} ---"

    def output_report(self, report: str) -> str:
        """Override to change output destination."""
        filename = f"{self.get_report_name().lower().replace(' ', '_')}.txt"
        # In a real system, write to file
        return filename


class SalesReport(ReportGenerator):
    """Generates a plain text sales report."""

    def fetch_data(self) -> list[dict[str, Any]]:
        print("  Querying sales database...")
        return [
            {"product": "Laptop", "quantity": 45, "revenue": 44955.00},
            {"product": "Phone", "quantity": 120, "revenue": 83880.00},
            {"product": "Tablet", "quantity": 30, "revenue": 14970.00},
            {"product": "Watch", "quantity": 200, "revenue": 59800.00},
        ]

    def format_report(self, data: list[dict[str, Any]]) -> str:
        lines = ["Product       | Qty  | Revenue"]
        lines.append("-" * 40)
        total_revenue = 0
        for row in data:
            lines.append(
                f"{row['product']:<14}| {row['quantity']:<5}| "
                f"${row['revenue']:>10,.2f}"
            )
            total_revenue += row['revenue']
        lines.append("-" * 40)
        lines.append(f"{'TOTAL':<14}|      | ${total_revenue:>10,.2f}")
        return "\n".join(lines)

    def get_report_name(self) -> str:
        return "Sales Report"


class TopProductsReport(ReportGenerator):
    """Generates a report of top products only."""

    def __init__(self, min_revenue: float = 50000):
        self.min_revenue = min_revenue

    def fetch_data(self) -> list[dict[str, Any]]:
        print("  Querying sales database...")
        return [
            {"product": "Laptop", "quantity": 45, "revenue": 44955.00},
            {"product": "Phone", "quantity": 120, "revenue": 83880.00},
            {"product": "Tablet", "quantity": 30, "revenue": 14970.00},
            {"product": "Watch", "quantity": 200, "revenue": 59800.00},
        ]

    # Override hook to filter data
    def filter_data(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        print(f"  Filtering: revenue >= ${self.min_revenue:,.2f}")
        return [row for row in data if row["revenue"] >= self.min_revenue]

    def format_report(self, data: list[dict[str, Any]]) -> str:
        lines = ["TOP PRODUCTS"]
        for i, row in enumerate(data, 1):
            lines.append(
                f"  {i}. {row['product']}: ${row['revenue']:,.2f} "
                f"({row['quantity']} units)"
            )
        return "\n".join(lines)

    def get_report_name(self) -> str:
        return "Top Products Report"

    # Override hook for custom header
    def get_header(self) -> str:
        return f"*** {self.get_report_name()} (min: ${self.min_revenue:,.2f}) ***"


# --- Usage ---
if __name__ == "__main__":
    sales = SalesReport()
    report1 = sales.generate()
    print(report1)

    top = TopProductsReport(min_revenue=50000)
    report2 = top.generate()
    print(report2)
```

**Output:**
```
=== Generating Sales Report ===
  Querying sales database...
  Fetched 4 records
  After filtering: 4 records
  Report saved to: sales_report.txt
=== Completed Sales Report ===

--- Sales Report ---
Product       | Qty  | Revenue
----------------------------------------
Laptop        | 45   | $ 44,955.00
Phone         | 120  | $ 83,880.00
Tablet        | 30   | $ 14,970.00
Watch         | 200  | $ 59,800.00
----------------------------------------
TOTAL         |      | $203,605.00
--- Generated: 2024-11-15 10:30 ---

=== Generating Top Products Report ===
  Querying sales database...
  Fetched 4 records
  Filtering: revenue >= $50,000.00
  After filtering: 2 records
  Report saved to: top_products_report.txt
=== Completed Top Products Report ===

*** Top Products Report (min: $50,000.00) ***
TOP PRODUCTS
  1. Phone: $83,880.00 (120 units)
  2. Watch: $59,800.00 (200 units)
--- Generated: 2024-11-15 10:30 ---
```

---

## Template Method vs Strategy

These two patterns are often confused. Here is when to use each.

```
Template Method:                     Strategy:
+----------------------------+       +----------------------------+
| Base class defines          |       | Interface defines          |
| the OVERALL algorithm.      |       | ONE interchangeable step.  |
|                             |       |                            |
| Subclasses fill in steps.   |       | Implementations provide    |
|                             |       | different algorithms.      |
| Uses INHERITANCE.           |       | Uses COMPOSITION.          |
+----------------------------+       +----------------------------+

  Template Method:                   Strategy:

  AbstractProcessor                  Processor
  |                                  |
  +-- process() {                    +-- process(strategy) {
  |     extract();   // abstract     |     strategy.execute();
  |     transform(); // abstract     |   }
  |     load();      // abstract     |
  |   }                              Strategy strategy
  |                                       ^       ^
  CSVProcessor   JSONProcessor       QuickSort  BubbleSort
```

| Aspect | Template Method | Strategy |
|---|---|---|
| Mechanism | Inheritance | Composition |
| What varies | Steps within a fixed algorithm | The entire algorithm |
| When chosen | At compile time (class hierarchy) | At runtime (inject/swap) |
| Flexibility | Less (locked to class hierarchy) | More (swap any time) |
| Use when | Structure is fixed, steps vary | Algorithm changes at runtime |

---

## When to Use / When NOT to Use

### Use Template Method When

| Scenario | Why Template Method Helps |
|---|---|
| Multiple classes share the same algorithm structure | Define it once in the base class |
| Steps differ but order is fixed | Base class controls the order |
| You want to enforce a workflow | `final` template method prevents changes |
| Hook methods add optional customization | Subclasses choose what to customize |

### Do NOT Use Template Method When

| Scenario | Why Not |
|---|---|
| Algorithm structure changes at runtime | Use Strategy instead |
| Too many abstract methods | Subclasses become painful to implement |
| Only one step varies | A simple callback or Strategy is lighter |
| Deep inheritance hierarchies | Leads to fragile base class problem |

---

## Common Mistakes

### Mistake 1: Template Method Not Marked Final

```java
// BAD -- Subclass can override the template method itself
public class AbstractProcessor {
    public void process() {  // NOT final -- can be overridden
        extract();
        transform();
        load();
    }
}

// Subclass breaks the algorithm
public class BadProcessor extends AbstractProcessor {
    @Override
    public void process() {
        load();  // Oops -- loaded before extracting
    }
}

// GOOD -- Template method is final
public abstract class AbstractProcessor {
    public final void process() {  // Cannot be overridden
        extract();
        transform();
        load();
    }
}
```

### Mistake 2: Too Many Abstract Methods

```java
// BAD -- 8 abstract methods, painful to implement
public abstract class AbstractProcessor {
    public final void process() {
        step1(); step2(); step3(); step4();
        step5(); step6(); step7(); step8();
    }
    protected abstract void step1();
    protected abstract void step2();
    // ... Subclasses must implement ALL 8 methods
}

// GOOD -- Few abstract methods, hooks for optional customization
public abstract class AbstractProcessor {
    public final void process() {
        beforeProcess();  // hook (optional)
        extract();        // abstract (required)
        transform();      // abstract (required)
        afterTransform(); // hook (optional)
        load();           // abstract (required)
        afterProcess();   // hook (optional)
    }
    // Only 3 required methods
}
```

### Mistake 3: Calling Super Without Understanding Order

```python
# BAD -- Overriding a hook and forgetting it changes behavior
class MyProcessor(AbstractProcessor):
    def filter_data(self, data):
        # Forgot to call super() -- other filtering logic lost
        return [d for d in data if d["active"]]

# GOOD -- Be explicit about whether you extend or replace
class MyProcessor(AbstractProcessor):
    def filter_data(self, data):
        # First apply base filtering, then add our own
        data = super().filter_data(data)
        return [d for d in data if d["active"]]
```

---

## Best Practices

1. **Mark the template method `final`** (Java) or document it as not-to-be-overridden (Python). The whole point is that the structure does not change.

2. **Use hooks sparingly.** Each hook is a decision point a subclass might use. Too many hooks make the base class hard to understand.

3. **Provide sensible defaults in hooks.** Hooks should do something reasonable if not overridden. Do not force subclasses to override hooks.

4. **Keep the number of abstract methods small.** Three to five is typical. More than that, and subclasses become burdensome.

5. **Name abstract methods clearly.** `extract()`, `transform()`, `load()` are much better than `step1()`, `step2()`, `step3()`.

6. **Prefer Strategy when algorithms change at runtime.** Template Method is a compile-time decision; Strategy is a runtime decision.

---

## Quick Summary

```
+---------------------------------------------------------------+
|                 TEMPLATE METHOD PATTERN SUMMARY                |
+---------------------------------------------------------------+
| Intent:     Define the skeleton of an algorithm in a base      |
|             class, deferring some steps to subclasses.         |
+---------------------------------------------------------------+
| Problem:    Same algorithm structure duplicated across classes |
| Solution:   Base class owns the structure, subclasses vary     |
+---------------------------------------------------------------+
| Key parts:                                                     |
|   - Abstract base class (template method + abstract steps)     |
|   - Concrete subclasses (implement abstract steps)             |
|   - Hook methods (optional override points)                    |
+---------------------------------------------------------------+
| Structure: Fixed by base class (marked final)                  |
| Steps:     Vary by subclass                                    |
+---------------------------------------------------------------+
```

---

## Key Points

- Template Method defines an algorithm skeleton in a base class, with abstract steps filled in by subclasses.
- The template method itself should be `final` to prevent subclasses from altering the algorithm structure.
- Hook methods provide optional customization points with sensible defaults.
- This pattern eliminates duplicated algorithm structures across similar classes.
- Template Method uses inheritance; Strategy uses composition. Prefer Strategy when the algorithm needs to change at runtime.
- Keep the number of abstract methods small to avoid burdening subclasses.

---

## Practice Questions

1. In the ETL example, the JSON processor skips validation by overriding `shouldValidate()`. What are the risks of letting subclasses skip safety checks? How would you make validation mandatory for certain data sources?

2. You have a test framework where every test runs `setup()`, `runTest()`, and `teardown()`. This is a classic Template Method. JUnit uses `@Before`, `@Test`, and `@After` instead. What advantage does the annotation-based approach have over Template Method?

3. If the template method calls five abstract methods, and a subclass only needs custom behavior for two of them, what should you do with the other three? How do hooks help here?

4. Can you combine Template Method and Strategy? Give an example where the template method delegates one of its steps to a Strategy object.

5. Why does Template Method violate the "prefer composition over inheritance" principle? When is this trade-off acceptable?

---

## Exercises

### Exercise 1: HTTP Request Handler

Create an `AbstractRequestHandler` with a template method `handleRequest()` that follows this structure: authenticate, validate input, process, format response. Implement `RestHandler` (returns JSON) and `GraphQLHandler` (returns GraphQL response). Add a hook for rate limiting.

### Exercise 2: Notification Pipeline

Build a notification system with `AbstractNotificationSender`. The template method should: build message, validate recipient, send notification, log result. Implement `EmailSender`, `SMSSender`, and `PushNotificationSender`. Each formats the message differently but follows the same pipeline.

### Exercise 3: Data Migration Tool

Create an `AbstractMigrator` that defines: connect to source, extract batch, transform batch, load to destination, verify count, disconnect. Implement `MySQLToPostgresMigrator` and `MongoToElasticMigrator`. Add hooks for `onBatchComplete()` and `onError()`.

---

## What Is Next?

Template Method defines a fixed algorithm with variable steps. But what if a request needs to pass through a series of independent handlers, where each handler decides whether to process it or pass it along? In the next chapter, we explore the **Chain of Responsibility pattern** -- the pattern behind HTTP middleware, validation pipelines, and exception handling chains.
