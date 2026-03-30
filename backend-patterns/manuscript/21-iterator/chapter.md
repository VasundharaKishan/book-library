# Chapter 21: Iterator Pattern -- Sequential Access Without Exposing Internals

## What You Will Learn

- What the Iterator pattern is and why it matters for clean collection traversal
- How to implement custom iterators in Java with `Iterable` and `Iterator`
- How to leverage Java's Stream API for modern iteration
- How to implement Python's `__iter__` and `__next__` protocols
- How to use Python generators for elegant, memory-efficient iteration
- Real-world use case: paginated database results

## Why This Chapter Matters

Every backend system processes collections of data: users from a database, messages
from a queue, files from a directory, events from a log. The Iterator pattern defines
how to traverse these collections without exposing their internal structure.

You use iterators every day. Every `for` loop in Java and Python relies on the Iterator
pattern under the hood. Understanding how iterators work lets you build custom
collections that integrate seamlessly with language features, handle datasets too large
for memory, and create lazy evaluation pipelines.

---

## The Problem

You have a `UserRepository` backed by a database. You need to process all 100,000
users, but loading them all into a list at once consumes too much memory.

**Without Iterator**, your options are ugly:

```java
// Option 1: Load everything into memory (dangerous for large datasets)
List<User> allUsers = repo.findAll(); // 100,000 users in memory!
for (User user : allUsers) {
    process(user);
}

// Option 2: Manual pagination (exposes internals)
int page = 0;
int pageSize = 100;
while (true) {
    List<User> batch = repo.findPage(page, pageSize);
    if (batch.isEmpty()) break;
    for (User user : batch) {
        process(user);
    }
    page++;
}
// Every consumer must know about pagination!
```

Option 1 can crash with OutOfMemoryError. Option 2 forces every caller to handle
pagination logic. The caller needs to know about pages, sizes, and when to stop.

**With Iterator**, the caller just writes:

```java
for (User user : repo) {
    process(user);
}
// Pagination is hidden inside the iterator.
```

---

## The Solution: Iterator Pattern

```
+-------------------+          +-------------------+
|   <<interface>>   |          |   <<interface>>   |
|    Iterable<T>    |          |    Iterator<T>    |
+-------------------+          +-------------------+
| + iterator():     |--------->| + hasNext(): bool |
|   Iterator<T>     |          | + next(): T       |
+-------------------+          +-------------------+
        ^                              ^
        |                              |
+-------------------+          +-------------------+
| ConcreteCollection|          | ConcreteIterator  |
+-------------------+          +-------------------+
| - elements[]      |          | - position: int   |
| + iterator()      |          | - collection      |
+-------------------+          | + hasNext()       |
                               | + next()          |
                               +-------------------+
```

**Key participants:**

- **Iterator**: interface with `hasNext()` and `next()` methods
- **Iterable**: interface that returns an Iterator (enables for-each loops)
- **ConcreteIterator**: implements traversal logic for a specific collection
- **ConcreteCollection**: stores elements and creates iterators

---

## Java Implementation: Custom Collection

### A Filtered, Sorted Task List

```java
import java.util.Iterator;
import java.util.List;
import java.util.ArrayList;
import java.util.NoSuchElementException;

public class Task {
    private final String name;
    private final String priority;  // "high", "medium", "low"
    private final boolean completed;

    public Task(String name, String priority, boolean completed) {
        this.name = name;
        this.priority = priority;
        this.completed = completed;
    }

    public String getName() { return name; }
    public String getPriority() { return priority; }
    public boolean isCompleted() { return completed; }

    @Override
    public String toString() {
        String status = completed ? "done" : "todo";
        return String.format("[%s] %s (%s)", priority.toUpperCase(),
                name, status);
    }
}
```

### The Custom Iterator

```java
public class PriorityTaskIterator implements Iterator<Task> {
    private final List<Task> tasks;
    private final String priorityFilter;
    private final boolean skipCompleted;
    private int position;

    public PriorityTaskIterator(List<Task> tasks, String priorityFilter,
                                 boolean skipCompleted) {
        this.tasks = tasks;
        this.priorityFilter = priorityFilter;
        this.skipCompleted = skipCompleted;
        this.position = 0;
        advanceToNext(); // position at first valid element
    }

    @Override
    public boolean hasNext() {
        return position < tasks.size();
    }

    @Override
    public Task next() {
        if (!hasNext()) {
            throw new NoSuchElementException();
        }
        Task task = tasks.get(position);
        position++;
        advanceToNext(); // move to next valid element
        return task;
    }

    private void advanceToNext() {
        while (position < tasks.size()) {
            Task task = tasks.get(position);
            boolean matchesPriority = priorityFilter == null ||
                    task.getPriority().equals(priorityFilter);
            boolean matchesCompleted = !skipCompleted ||
                    !task.isCompleted();

            if (matchesPriority && matchesCompleted) {
                return; // found a valid element
            }
            position++;
        }
    }
}
```

### The Iterable Collection

```java
public class TaskList implements Iterable<Task> {
    private final List<Task> tasks = new ArrayList<>();

    public void add(Task task) {
        tasks.add(task);
    }

    // Default iterator: all tasks
    @Override
    public Iterator<Task> iterator() {
        return tasks.iterator();
    }

    // Custom iterator: filter by priority
    public Iterable<Task> byPriority(String priority) {
        return () -> new PriorityTaskIterator(tasks, priority, false);
    }

    // Custom iterator: only pending tasks
    public Iterable<Task> pending() {
        return () -> new PriorityTaskIterator(tasks, null, true);
    }

    // Custom iterator: pending tasks of a specific priority
    public Iterable<Task> pendingByPriority(String priority) {
        return () -> new PriorityTaskIterator(tasks, priority, true);
    }

    public int size() {
        return tasks.size();
    }
}
```

### Demo

```java
public class IteratorDemo {
    public static void main(String[] args) {
        TaskList tasks = new TaskList();
        tasks.add(new Task("Deploy to production", "high", false));
        tasks.add(new Task("Write unit tests", "high", true));
        tasks.add(new Task("Update documentation", "medium", false));
        tasks.add(new Task("Fix login bug", "high", false));
        tasks.add(new Task("Refactor database layer", "low", false));
        tasks.add(new Task("Code review PR #42", "medium", true));
        tasks.add(new Task("Setup CI pipeline", "medium", false));

        // Default: iterate all tasks
        System.out.println("=== All Tasks ===");
        for (Task task : tasks) {
            System.out.println("  " + task);
        }

        // Filter: high priority only
        System.out.println("\n=== High Priority ===");
        for (Task task : tasks.byPriority("high")) {
            System.out.println("  " + task);
        }

        // Filter: pending tasks only
        System.out.println("\n=== Pending Only ===");
        for (Task task : tasks.pending()) {
            System.out.println("  " + task);
        }

        // Filter: pending high priority
        System.out.println("\n=== Pending High Priority ===");
        for (Task task : tasks.pendingByPriority("high")) {
            System.out.println("  " + task);
        }
    }
}
```

**Output:**
```
=== All Tasks ===
  [HIGH] Deploy to production (todo)
  [HIGH] Write unit tests (done)
  [MEDIUM] Update documentation (todo)
  [HIGH] Fix login bug (todo)
  [LOW] Refactor database layer (todo)
  [MEDIUM] Code review PR #42 (done)
  [MEDIUM] Setup CI pipeline (todo)

=== High Priority ===
  [HIGH] Deploy to production (todo)
  [HIGH] Write unit tests (done)
  [HIGH] Fix login bug (todo)

=== Pending Only ===
  [HIGH] Deploy to production (todo)
  [MEDIUM] Update documentation (todo)
  [HIGH] Fix login bug (todo)
  [LOW] Refactor database layer (todo)
  [MEDIUM] Setup CI pipeline (todo)

=== Pending High Priority ===
  [HIGH] Deploy to production (todo)
  [HIGH] Fix login bug (todo)
```

Notice that the for-each loop works with every custom iterator because they implement
`Iterable`. The caller does not know or care about the filtering logic.

---

## Java Stream API: Modern Iteration

Java 8+ Streams provide a functional approach to iteration with built-in filtering,
mapping, and reducing.

```java
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

public class StreamDemo {
    public static void main(String[] args) {
        List<Task> tasks = Arrays.asList(
            new Task("Deploy to production", "high", false),
            new Task("Write unit tests", "high", true),
            new Task("Update documentation", "medium", false),
            new Task("Fix login bug", "high", false),
            new Task("Refactor database layer", "low", false),
            new Task("Code review PR #42", "medium", true),
            new Task("Setup CI pipeline", "medium", false)
        );

        // Filter and collect
        System.out.println("=== Pending High Priority (Stream) ===");
        List<Task> urgent = tasks.stream()
                .filter(t -> !t.isCompleted())
                .filter(t -> t.getPriority().equals("high"))
                .collect(Collectors.toList());

        urgent.forEach(t -> System.out.println("  " + t));

        // Count by priority
        System.out.println("\n=== Task Counts ===");
        tasks.stream()
                .collect(Collectors.groupingBy(
                        Task::getPriority, Collectors.counting()))
                .forEach((priority, count) ->
                        System.out.printf("  %s: %d%n", priority, count));

        // Map to names
        System.out.println("\n=== Pending Task Names ===");
        String names = tasks.stream()
                .filter(t -> !t.isCompleted())
                .map(Task::getName)
                .collect(Collectors.joining(", "));
        System.out.println("  " + names);

        // Find first urgent task
        tasks.stream()
                .filter(t -> !t.isCompleted())
                .filter(t -> t.getPriority().equals("high"))
                .findFirst()
                .ifPresent(t -> System.out.println(
                        "\nFirst urgent: " + t.getName()));
    }
}
```

**Output:**
```
=== Pending High Priority (Stream) ===
  [HIGH] Deploy to production (todo)
  [HIGH] Fix login bug (todo)

=== Task Counts ===
  high: 3
  medium: 3
  low: 1

=== Pending Task Names ===
  Deploy to production, Update documentation, Fix login bug, Refactor database layer, Setup CI pipeline

First urgent: Deploy to production
```

Streams are lazy: they do not process elements until a terminal operation (like
`collect` or `forEach`) is called. This makes them efficient for large datasets.

---

## Python Implementation: __iter__ and __next__

### Custom Iterator Protocol

```python
class Task:
    def __init__(self, name, priority, completed=False):
        self.name = name
        self.priority = priority
        self.completed = completed

    def __repr__(self):
        status = "done" if self.completed else "todo"
        return f"[{self.priority.upper()}] {self.name} ({status})"


class TaskIterator:
    """Custom iterator with filtering support."""

    def __init__(self, tasks, priority_filter=None, skip_completed=False):
        self._tasks = tasks
        self._priority_filter = priority_filter
        self._skip_completed = skip_completed
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        while self._index < len(self._tasks):
            task = self._tasks[self._index]
            self._index += 1

            # Apply filters
            if self._priority_filter and \
               task.priority != self._priority_filter:
                continue
            if self._skip_completed and task.completed:
                continue

            return task

        raise StopIteration


class TaskList:
    """Collection that provides multiple iteration strategies."""

    def __init__(self):
        self._tasks = []

    def add(self, task):
        self._tasks.append(task)

    def __iter__(self):
        return iter(self._tasks)

    def __len__(self):
        return len(self._tasks)

    def by_priority(self, priority):
        return IterableView(self._tasks, priority_filter=priority)

    def pending(self):
        return IterableView(self._tasks, skip_completed=True)

    def pending_by_priority(self, priority):
        return IterableView(self._tasks, priority_filter=priority,
                            skip_completed=True)


class IterableView:
    """A filtered view of a task list that is itself iterable."""

    def __init__(self, tasks, priority_filter=None, skip_completed=False):
        self._tasks = tasks
        self._priority_filter = priority_filter
        self._skip_completed = skip_completed

    def __iter__(self):
        return TaskIterator(self._tasks, self._priority_filter,
                            self._skip_completed)


# Usage
tasks = TaskList()
tasks.add(Task("Deploy to production", "high"))
tasks.add(Task("Write unit tests", "high", completed=True))
tasks.add(Task("Update documentation", "medium"))
tasks.add(Task("Fix login bug", "high"))
tasks.add(Task("Refactor database layer", "low"))
tasks.add(Task("Code review PR #42", "medium", completed=True))

print("=== All Tasks ===")
for task in tasks:
    print(f"  {task}")

print("\n=== High Priority ===")
for task in tasks.by_priority("high"):
    print(f"  {task}")

print("\n=== Pending High Priority ===")
for task in tasks.pending_by_priority("high"):
    print(f"  {task}")
```

**Output:**
```
=== All Tasks ===
  [HIGH] Deploy to production (todo)
  [HIGH] Write unit tests (done)
  [MEDIUM] Update documentation (todo)
  [HIGH] Fix login bug (todo)
  [LOW] Refactor database layer (todo)
  [MEDIUM] Code review PR #42 (done)

=== High Priority ===
  [HIGH] Deploy to production (todo)
  [HIGH] Write unit tests (done)
  [HIGH] Fix login bug (todo)

=== Pending High Priority ===
  [HIGH] Deploy to production (todo)
  [HIGH] Fix login bug (todo)
```

---

## Python Generators: Elegant Iteration

Generators are Python's most powerful iteration feature. A generator function uses
`yield` instead of `return`. It pauses execution after each yield and resumes when the
next value is requested.

```python
def fibonacci(limit):
    """Generate Fibonacci numbers up to limit."""
    a, b = 0, 1
    while a < limit:
        yield a
        a, b = b, a + b

# Use in a for loop
print("Fibonacci up to 100:")
for num in fibonacci(100):
    print(f"  {num}", end="")
print()

# Use with list comprehension
fibs = [n for n in fibonacci(50)]
print(f"As list: {fibs}")
```

**Output:**
```
Fibonacci up to 100:
  0  1  1  2  3  5  8  13  21  34  55  89
As list: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

### Generator-Based Task Filtering

```python
class TaskList:
    def __init__(self):
        self._tasks = []

    def add(self, task):
        self._tasks.append(task)

    def __iter__(self):
        return iter(self._tasks)

    def by_priority(self, priority):
        """Generator that yields tasks matching the priority."""
        for task in self._tasks:
            if task.priority == priority:
                yield task

    def pending(self):
        """Generator that yields only incomplete tasks."""
        for task in self._tasks:
            if not task.completed:
                yield task

    def pending_by_priority(self, priority):
        """Compose generators: pending AND matching priority."""
        for task in self.pending():
            if task.priority == priority:
                yield task

    def summary(self):
        """Generator that yields summary strings."""
        from collections import Counter
        counts = Counter(t.priority for t in self._tasks if not t.completed)
        for priority, count in counts.most_common():
            yield f"{priority}: {count} pending"


tasks = TaskList()
tasks.add(Task("Deploy", "high"))
tasks.add(Task("Tests", "high", completed=True))
tasks.add(Task("Docs", "medium"))
tasks.add(Task("Bug fix", "high"))
tasks.add(Task("Refactor", "low"))

print("=== Summary ===")
for line in tasks.summary():
    print(f"  {line}")

print("\n=== Pending (generator) ===")
pending = tasks.pending()  # no work done yet
print(f"  Type: {type(pending)}")
print(f"  First: {next(pending)}")
print(f"  Second: {next(pending)}")
# Remaining items are never generated -- lazy!
```

**Output:**
```
=== Summary ===
  high: 1 pending
  medium: 1 pending
  low: 1 pending

=== Pending (generator) ===
  Type: <class 'generator'>
  First: [HIGH] Deploy (todo)
  Second: [MEDIUM] Docs (todo)
```

Generators are lazy: they compute values on demand. This is critical for large datasets.

---

## Real-World Use Case: Paginated Database Results

This is the most practical application of iterators in backend development.

### Java: Paginated Iterator

```java
import java.util.*;

// Simulated database
class UserDatabase {
    private final List<String> users = new ArrayList<>();

    public UserDatabase() {
        for (int i = 1; i <= 47; i++) {
            users.add("User-" + i);
        }
    }

    public List<String> fetchPage(int offset, int limit) {
        int start = Math.min(offset, users.size());
        int end = Math.min(offset + limit, users.size());
        System.out.printf("    [DB] Fetching offset=%d limit=%d "
                + "(returned %d rows)%n", offset, limit, end - start);
        return users.subList(start, end);
    }

    public int count() {
        return users.size();
    }
}

public class PaginatedIterator implements Iterator<String> {
    private final UserDatabase db;
    private final int pageSize;
    private List<String> currentPage;
    private int pageIndex;     // position within current page
    private int globalOffset;  // position in the full dataset
    private boolean exhausted;

    public PaginatedIterator(UserDatabase db, int pageSize) {
        this.db = db;
        this.pageSize = pageSize;
        this.globalOffset = 0;
        this.pageIndex = 0;
        this.exhausted = false;
        fetchNextPage();
    }

    private void fetchNextPage() {
        currentPage = db.fetchPage(globalOffset, pageSize);
        pageIndex = 0;
        if (currentPage.isEmpty()) {
            exhausted = true;
        }
    }

    @Override
    public boolean hasNext() {
        if (exhausted) return false;
        if (pageIndex < currentPage.size()) return true;

        // Current page exhausted, try next page
        globalOffset += pageSize;
        fetchNextPage();
        return !exhausted;
    }

    @Override
    public String next() {
        if (!hasNext()) {
            throw new NoSuchElementException();
        }
        return currentPage.get(pageIndex++);
    }
}

// Iterable wrapper
class PaginatedUsers implements Iterable<String> {
    private final UserDatabase db;
    private final int pageSize;

    public PaginatedUsers(UserDatabase db, int pageSize) {
        this.db = db;
        this.pageSize = pageSize;
    }

    @Override
    public Iterator<String> iterator() {
        return new PaginatedIterator(db, pageSize);
    }
}
```

```java
public class PaginationDemo {
    public static void main(String[] args) {
        UserDatabase db = new UserDatabase();

        System.out.println("=== Paginated Iteration (page size: 10) ===");
        PaginatedUsers users = new PaginatedUsers(db, 10);

        int count = 0;
        for (String user : users) {
            count++;
        }
        System.out.println("Processed " + count + " users");

        System.out.println("\n=== Small pages (page size: 15) ===");
        PaginatedUsers smallPages = new PaginatedUsers(db, 15);
        count = 0;
        for (String user : smallPages) {
            count++;
        }
        System.out.println("Processed " + count + " users");
    }
}
```

**Output:**
```
=== Paginated Iteration (page size: 10) ===
    [DB] Fetching offset=0 limit=10 (returned 10 rows)
    [DB] Fetching offset=10 limit=10 (returned 10 rows)
    [DB] Fetching offset=20 limit=10 (returned 10 rows)
    [DB] Fetching offset=30 limit=10 (returned 10 rows)
    [DB] Fetching offset=40 limit=10 (returned 7 rows)
    [DB] Fetching offset=50 limit=10 (returned 0 rows)
Processed 47 users

=== Small pages (page size: 15) ===
    [DB] Fetching offset=0 limit=15 (returned 15 rows)
    [DB] Fetching offset=15 limit=15 (returned 15 rows)
    [DB] Fetching offset=30 limit=15 (returned 15 rows)
    [DB] Fetching offset=45 limit=15 (returned 2 rows)
    [DB] Fetching offset=60 limit=15 (returned 0 rows)
Processed 47 users
```

The caller just writes `for (String user : users)`. The pagination is completely hidden.

### Python: Generator-Based Pagination

```python
class UserDatabase:
    """Simulated database with 47 users."""

    def __init__(self):
        self._users = [f"User-{i}" for i in range(1, 48)]

    def fetch_page(self, offset, limit):
        page = self._users[offset:offset + limit]
        print(f"    [DB] Fetching offset={offset} limit={limit} "
              f"(returned {len(page)} rows)")
        return page

    def count(self):
        return len(self._users)


def paginated_users(db, page_size=10):
    """Generator that yields users one at a time, fetching in pages."""
    offset = 0
    while True:
        page = db.fetch_page(offset, page_size)
        if not page:
            return  # no more data

        for user in page:
            yield user

        offset += page_size


# Usage -- caller sees a simple loop
db = UserDatabase()

print("=== Paginated Iteration (page size: 10) ===")
count = 0
for user in paginated_users(db, page_size=10):
    count += 1
print(f"Processed {count} users")

print("\n=== Early termination (stop after 25) ===")
count = 0
for user in paginated_users(db, page_size=10):
    count += 1
    if count >= 25:
        break  # generator stops fetching pages!
print(f"Processed {count} users (remaining pages never fetched)")
```

**Output:**
```
=== Paginated Iteration (page size: 10) ===
    [DB] Fetching offset=0 limit=10 (returned 10 rows)
    [DB] Fetching offset=10 limit=10 (returned 10 rows)
    [DB] Fetching offset=20 limit=10 (returned 10 rows)
    [DB] Fetching offset=30 limit=10 (returned 10 rows)
    [DB] Fetching offset=40 limit=10 (returned 7 rows)
    [DB] Fetching offset=50 limit=10 (returned 0 rows)
Processed 47 users

=== Early termination (stop after 25) ===
    [DB] Fetching offset=0 limit=10 (returned 10 rows)
    [DB] Fetching offset=10 limit=10 (returned 10 rows)
    [DB] Fetching offset=20 limit=10 (returned 10 rows)
Processed 25 users (remaining pages never fetched)
```

Notice in the early termination case: the generator only fetched 3 pages (30 rows).
It never fetched the remaining 17 users. Lazy evaluation means no wasted work.

---

## Before vs After Comparison

### Before: Client Handles Pagination

```python
# Every caller must implement pagination
offset = 0
page_size = 100
while True:
    page = db.fetch_page(offset, page_size)
    if not page:
        break
    for user in page:
        send_email(user)
    offset += page_size

# Duplicated everywhere users are processed
offset = 0
while True:
    page = db.fetch_page(offset, page_size)
    if not page:
        break
    for user in page:
        generate_report(user)
    offset += page_size
```

### After: Iterator Hides Pagination

```python
# Simple and reusable
for user in paginated_users(db):
    send_email(user)

for user in paginated_users(db):
    generate_report(user)
```

---

## When to Use / When NOT to Use

### Use Iterator When

- You need to traverse a collection without exposing its internal structure
- The collection is too large to load entirely into memory
- You want multiple traversal strategies over the same collection
- You need lazy evaluation (compute values only when requested)
- You want to integrate custom collections with language for-each loops
- Paginated API or database access should be transparent to callers

### Do NOT Use Iterator When

- A simple list or array suffices (do not over-engineer)
- You need random access by index (iterators are sequential)
- The collection is small and fits in memory easily
- You need to traverse backwards frequently (most iterators are forward-only)
- The overhead of iterator objects exceeds the benefit (very tight inner loops)

---

## Common Mistakes

### Mistake 1: Modifying Collection During Iteration

```java
// WRONG: ConcurrentModificationException
for (Task task : tasks) {
    if (task.isCompleted()) {
        tasks.remove(task); // modifying during iteration!
    }
}

// RIGHT: use Iterator.remove() or collect then remove
Iterator<Task> it = tasks.iterator();
while (it.hasNext()) {
    if (it.next().isCompleted()) {
        it.remove(); // safe removal through iterator
    }
}
```

### Mistake 2: Exhausted Iterator Reuse

```python
# WRONG: generators are single-use
gen = paginated_users(db)
list1 = list(gen)  # consumes the generator
list2 = list(gen)  # empty! generator is exhausted

# RIGHT: create a new generator each time
list1 = list(paginated_users(db))
list2 = list(paginated_users(db))

# OR: make the container iterable (creates new iterator each time)
class Users:
    def __iter__(self):
        return paginated_users(db)  # fresh generator each time
```

### Mistake 3: Not Handling StopIteration

```python
# WRONG: calling next() without checking
it = iter([1, 2])
print(next(it))  # 1
print(next(it))  # 2
print(next(it))  # StopIteration exception!

# RIGHT: use default value
print(next(it, None))  # None instead of exception

# Or use a for loop (handles StopIteration automatically)
for item in iter([1, 2]):
    print(item)
```

---

## Best Practices

1. **Implement Iterable, not just Iterator.** In Java, implement `Iterable<T>` on your
   collection so it works with for-each loops. In Python, define `__iter__` on the
   collection and return a fresh iterator each time.

2. **Use generators in Python.** They are simpler than manual `__iter__`/`__next__`
   implementations and handle state management automatically.

3. **Make iterators lazy.** Fetch data only when `next()` is called, not during
   construction. This enables processing of datasets larger than memory.

4. **Support early termination.** Lazy iterators should stop fetching when the consumer
   stops consuming. Generators in Python handle this automatically.

5. **Use Java Streams for functional operations.** When you need filter-map-reduce
   operations, Streams are more readable than manual iterators.

6. **Do not modify collections during iteration.** Use `Iterator.remove()` in Java or
   build a new collection instead.

7. **Document iterator guarantees.** State whether the iterator is lazy or eager,
   single-use or reusable, and whether it supports concurrent modification.

---

## Quick Summary

The Iterator pattern provides a standard way to traverse collections without exposing
their internals. In Java, `Iterable` and `Iterator` interfaces enable for-each loops.
In Python, `__iter__`/`__next__` and generators provide the same capability. The pattern
is essential for paginated data access, lazy evaluation, and clean separation between
collections and their traversal logic.

```
Problem:  Clients need to traverse collections but should not know internals.
Solution: Provide an iterator that yields elements one at a time.
Key:      Lazy evaluation enables processing datasets larger than memory.
```

---

## Key Points

- **Iterator** decouples traversal logic from the collection's internal structure
- Java uses `Iterable<T>` and `Iterator<T>` interfaces (enabling for-each loops)
- Java **Streams** provide functional iteration: filter, map, reduce, collect
- Python uses `__iter__()` and `__next__()` methods (enabling for loops)
- Python **generators** (`yield`) are the most elegant way to implement iterators
- Generators are **lazy**: they compute values on demand, saving memory
- **Paginated database access** is the most common backend use case
- Generators are **single-use**: create a new one each time you need to iterate
- Never modify a collection while iterating over it

---

## Practice Questions

1. What is the difference between `Iterable` and `Iterator` in Java? Why are they
   separate interfaces?

2. Explain why generators in Python are single-use. How would you make a class that
   can be iterated multiple times using a generator internally?

3. How does lazy evaluation in iterators help when processing a 10-million-row database
   table? What would happen without lazy evaluation?

4. Compare Java Streams with Python generators. What are two advantages of each?

5. In the paginated database example, what happens if a new row is inserted into the
   database while pagination is in progress? How would you handle this?

---

## Exercises

### Exercise 1: CSV File Iterator

Build a lazy CSV file reader:

- A `CsvIterator` that reads a CSV file line by line (not loading the entire file)
- Each iteration yields a dictionary mapping column headers to values
- Support filtering rows by a column value
- Support limiting the number of rows returned
- Test with a CSV file of at least 100 rows
- Demonstrate that memory usage stays constant regardless of file size

### Exercise 2: Binary Tree Iterator

Implement three traversal iterators for a binary tree:

- `InOrderIterator`: left, root, right
- `PreOrderIterator`: root, left, right
- `PostOrderIterator`: left, right, root
- The tree should implement `Iterable` with a default order
- Provide methods to get each specific traversal: `tree.in_order()`,
  `tree.pre_order()`, `tree.post_order()`
- Build a tree with at least 7 nodes and show the output of each traversal

### Exercise 3: API Cursor Pagination

Build an iterator for cursor-based API pagination:

- Simulate an API that returns `{"data": [...], "next_cursor": "abc123"}` or
  `{"data": [...], "next_cursor": null}` when done
- The iterator should automatically follow cursors until no more data
- Support a maximum number of API calls (to prevent infinite loops)
- Add a delay parameter between API calls (rate limiting)
- The caller should see a simple `for item in api_results` loop

---

## What Is Next?

The next chapter introduces the **Visitor Pattern**, which lets you add new operations
to existing class hierarchies without modifying them. Where Iterator standardizes how
you traverse a structure, Visitor standardizes what you do with each element during
traversal. The two patterns are natural partners: Iterator tells you what to visit next,
and Visitor tells you what to do when you get there.
