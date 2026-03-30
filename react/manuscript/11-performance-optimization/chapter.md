# Chapter 11: useMemo, useCallback, and Performance Optimization

---

## Learning Goals

By the end of this chapter, you will be able to:

- Understand how React's re-rendering works and when it causes performance issues
- Use `React.memo` to prevent unnecessary re-renders of child components
- Use `useMemo` to cache expensive calculations
- Use `useCallback` to stabilize function references for child components
- Profile React applications to identify performance bottlenecks
- Distinguish between real performance problems and premature optimization
- Apply optimization strategies in the right situations
- Understand referential equality and why it matters for React
- Build performant lists, search interfaces, and data-heavy components

---

## How React Re-Rendering Works

Before learning optimization tools, you need to understand what happens when React re-renders.

### What Triggers a Re-Render?

A component re-renders when:

1. **Its state changes** — calling `setState` triggers a re-render of that component.
2. **Its parent re-renders** — when a parent component re-renders, all of its children re-render too, regardless of whether their props changed.
3. **Its context value changes** — components consuming a context re-render when the context value updates.

**The critical insight is #2**: when a parent re-renders, every child component re-renders — even if the child received the exact same props.

```jsx
function Parent() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
      <ExpensiveChild name="Alice" />  {/* Re-renders on EVERY count change! */}
    </div>
  );
}

function ExpensiveChild({ name }) {
  console.log("ExpensiveChild rendered");
  // Imagine this component does heavy work...
  return <p>Hello, {name}</p>;
}
```

Every time the user clicks "Increment," `Parent` re-renders (because `count` changed), and `ExpensiveChild` also re-renders — even though its `name` prop never changed. For most components, this is fine because re-renders are fast. But for expensive components, it can cause noticeable lag.

### What Happens During a Re-Render?

```
State changes (setCount(1))
    │
    ▼
React calls the component function
    │
    ├── All code inside the function runs
    ├── All hooks are called
    ├── A new JSX tree is created
    │
    ▼
React compares new JSX tree with previous one (reconciliation)
    │
    ├── If something changed → update the DOM
    └── If nothing changed → skip DOM updates
```

**Important:** Re-rendering does NOT mean the DOM is updated. React re-renders (calls the component function and creates a virtual DOM) and then compares the result with the previous render. Only actual DOM differences are applied to the real DOM.

This means re-renders are usually cheap — React is optimized for this. But when a component has expensive calculations, many children, or complex rendering logic, unnecessary re-renders can add up.

---

## React.memo — Preventing Unnecessary Child Re-Renders

`React.memo` is a higher-order component that wraps a child component and tells React: "Only re-render this component if its props actually changed."

### Basic Usage

```jsx
import { useState, memo } from "react";

const ExpensiveChild = memo(function ExpensiveChild({ name }) {
  console.log("ExpensiveChild rendered");
  // Simulate expensive work
  let total = 0;
  for (let i = 0; i < 10000000; i++) {
    total += i;
  }
  return <p>Hello, {name} (computed: {total})</p>;
});

function Parent() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
      <ExpensiveChild name="Alice" />
    </div>
  );
}
```

Now when the user clicks "Increment":
- `Parent` re-renders (because `count` changed).
- React checks if `ExpensiveChild`'s props changed: `name` was `"Alice"` before and is still `"Alice"` — **no change**.
- React skips re-rendering `ExpensiveChild`.

Without `memo`, clicking Increment would re-render `ExpensiveChild` every time (running that 10-million-iteration loop). With `memo`, it only re-renders when `name` actually changes.

### How memo Compares Props

By default, `React.memo` uses a **shallow comparison** of props:

```javascript
// Shallow comparison: checks each prop with Object.is (≈ ===)
// Re-renders only if at least one prop changed

// Primitive values: compared by value
"Alice" === "Alice"     // true → skip re-render
42 === 42               // true → skip re-render
"Alice" === "Bob"       // false → re-render

// Objects/arrays: compared by reference
{ a: 1 } === { a: 1 }  // false → re-render (different references!)
[1, 2] === [1, 2]       // false → re-render (different references!)
```

This is the key trap: even if an object or array has the same content, a new instance is a different reference — and `memo` sees it as a prop change.

```jsx
function Parent() {
  const [count, setCount] = useState(0);

  // ❌ New object on every render → memo is useless
  const style = { color: "blue" };

  // ❌ New array on every render → memo is useless
  const items = ["apple", "banana"];

  // ❌ New function on every render → memo is useless
  function handleClick() {
    console.log("clicked");
  }

  return (
    <div>
      <button onClick={() => setCount(count + 1)}>Count: {count}</button>
      <MemoizedChild style={style} items={items} onClick={handleClick} />
    </div>
  );
}

const MemoizedChild = memo(function MemoizedChild({ style, items, onClick }) {
  console.log("Child rendered"); // Still logs every time!
  return <div style={style}>{items.join(", ")}</div>;
});
```

Every time `Parent` re-renders, `style`, `items`, and `handleClick` are new objects/functions. `memo` sees new references and re-renders the child anyway.

**This is why we need `useMemo` and `useCallback`.**

---

## useMemo — Caching Expensive Calculations

`useMemo` caches (memoizes) the result of a calculation and only recalculates when its dependencies change.

### Syntax

```jsx
const memoizedValue = useMemo(() => {
  return expensiveCalculation(a, b);
}, [a, b]); // Only recalculates when a or b changes
```

- **First argument:** A function that returns the computed value.
- **Second argument:** A dependency array — the value is recalculated only when these dependencies change.

### Example: Expensive Filtering

```jsx
import { useState, useMemo } from "react";

function ProductList() {
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState("name");
  const [showCount, setShowCount] = useState(true);

  // Imagine this list comes from an API and has thousands of items
  const products = useMemo(() => generateProducts(5000), []);

  // Without useMemo: this runs on EVERY render, including when showCount toggles
  // With useMemo: this only runs when products, searchTerm, or sortBy changes
  const filteredAndSorted = useMemo(() => {
    console.log("Filtering and sorting...");

    let result = products;

    // Filter
    if (searchTerm) {
      result = result.filter((p) =>
        p.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Sort
    result = [...result].sort((a, b) => {
      if (sortBy === "name") return a.name.localeCompare(b.name);
      if (sortBy === "price") return a.price - b.price;
      return 0;
    });

    return result;
  }, [products, searchTerm, sortBy]);

  return (
    <div>
      <input
        type="text"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        placeholder="Search products..."
      />
      <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
        <option value="name">Sort by Name</option>
        <option value="price">Sort by Price</option>
      </select>
      <label>
        <input
          type="checkbox"
          checked={showCount}
          onChange={(e) => setShowCount(e.target.checked)}
        />
        Show count
      </label>

      {showCount && <p>{filteredAndSorted.length} products</p>}

      <ul>
        {filteredAndSorted.slice(0, 50).map((product) => (
          <li key={product.id}>
            {product.name} — ${product.price.toFixed(2)}
          </li>
        ))}
      </ul>
    </div>
  );
}

function generateProducts(count) {
  const names = ["Widget", "Gadget", "Device", "Tool", "Gizmo", "Apparatus"];
  return Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    name: `${names[i % names.length]} ${i + 1}`,
    price: Math.round(Math.random() * 200 * 100) / 100,
  }));
}
```

**Why `useMemo` helps here:**

Without `useMemo`, toggling the "Show count" checkbox would re-run the filtering and sorting of 5,000 products — because the component re-renders and the calculation runs again. With `useMemo`, toggling the checkbox still re-renders the component, but the memoized value is reused because `searchTerm` and `sortBy` have not changed. The expensive calculation is skipped.

### When useMemo Makes a Real Difference

```
Without useMemo:
  Component renders → expensive calculation runs → result displayed
  showCount toggles → component re-renders → expensive calculation runs AGAIN
  Every render: calculation runs (even when inputs haven't changed)

With useMemo:
  Component renders → expensive calculation runs → result cached
  showCount toggles → component re-renders → cached result reused (fast!)
  Only when searchTerm or sortBy changes: calculation re-runs
```

### Stabilizing Object and Array References

`useMemo` also solves the `React.memo` reference problem we saw earlier:

```jsx
function Parent() {
  const [count, setCount] = useState(0);

  // ✅ Same reference unless actual values change
  const style = useMemo(() => ({ color: "blue", fontSize: "16px" }), []);

  // ✅ Same reference unless items data changes
  const processedItems = useMemo(() => {
    return rawItems.map((item) => ({
      ...item,
      displayName: item.name.toUpperCase(),
    }));
  }, [rawItems]);

  return (
    <div>
      <button onClick={() => setCount(count + 1)}>Count: {count}</button>
      <MemoizedChild style={style} items={processedItems} />
    </div>
  );
}
```

Now `MemoizedChild` will not re-render when `count` changes because `style` and `processedItems` have stable references.

---

## useCallback — Stabilizing Function References

`useCallback` is similar to `useMemo`, but specifically for functions. It returns the same function reference between renders unless its dependencies change.

### Syntax

```jsx
const memoizedFunction = useCallback(
  (args) => {
    // function body
    doSomething(a, b, args);
  },
  [a, b] // Only creates a new function when a or b changes
);
```

`useCallback(fn, deps)` is equivalent to `useMemo(() => fn, deps)`.

### The Problem useCallback Solves

```jsx
function Parent() {
  const [count, setCount] = useState(0);
  const [query, setQuery] = useState("");

  // ❌ New function on every render
  function handleSearch(term) {
    console.log("Searching:", term);
    setQuery(term);
  }

  return (
    <div>
      <button onClick={() => setCount(count + 1)}>Count: {count}</button>
      <MemoizedSearchBar onSearch={handleSearch} />
    </div>
  );
}

const MemoizedSearchBar = memo(function SearchBar({ onSearch }) {
  console.log("SearchBar rendered");
  return (
    <input
      type="text"
      onChange={(e) => onSearch(e.target.value)}
      placeholder="Search..."
    />
  );
});
```

Even though `SearchBar` is wrapped in `memo`, it re-renders on every count change because `handleSearch` is a new function each time. `memo` sees a different function reference and thinks the prop changed.

### The Fix with useCallback

```jsx
function Parent() {
  const [count, setCount] = useState(0);
  const [query, setQuery] = useState("");

  // ✅ Same function reference between renders
  const handleSearch = useCallback((term) => {
    console.log("Searching:", term);
    setQuery(term);
  }, []); // setQuery is stable, so no dependencies needed

  return (
    <div>
      <button onClick={() => setCount(count + 1)}>Count: {count}</button>
      <MemoizedSearchBar onSearch={handleSearch} />
    </div>
  );
}
```

Now `handleSearch` has a stable reference. When `count` changes and `Parent` re-renders, `MemoizedSearchBar` receives the same `onSearch` function and skips its re-render.

### useCallback with Dependencies

When the function uses values that change, include them in the dependency array:

```jsx
function TodoList() {
  const [filter, setFilter] = useState("all");

  // This function depends on `filter` — include it in dependencies
  const handleToggle = useCallback(
    (todoId) => {
      console.log(`Toggling ${todoId} with filter: ${filter}`);
    },
    [filter] // New function when filter changes
  );

  return (
    <div>
      <select value={filter} onChange={(e) => setFilter(e.target.value)}>
        <option value="all">All</option>
        <option value="active">Active</option>
        <option value="completed">Completed</option>
      </select>
      <MemoizedTodoItem onToggle={handleToggle} />
    </div>
  );
}
```

When `filter` changes, `useCallback` returns a new function (because it needs the updated `filter` value). This is correct — the memoized child should re-render when the callback's behavior changes.

---

## The Complete Picture: memo + useMemo + useCallback

These three tools work together:

```
React.memo     → Prevents child re-renders when props haven't changed
useMemo        → Stabilizes object/array references and caches calculations
useCallback    → Stabilizes function references

Without all three, memo alone is often defeated by new object/function references.
```

### A Complete Example

```jsx
import { useState, useMemo, useCallback, memo } from "react";

function App() {
  const [items, setItems] = useState([
    { id: 1, name: "Learn React", done: false },
    { id: 2, name: "Build a project", done: false },
    { id: 3, name: "Get a job", done: false },
  ]);
  const [newItem, setNewItem] = useState("");
  const [filter, setFilter] = useState("all");

  // useMemo: cache the filtered list
  const filteredItems = useMemo(() => {
    console.log("Filtering items...");
    if (filter === "all") return items;
    if (filter === "active") return items.filter((i) => !i.done);
    return items.filter((i) => i.done);
  }, [items, filter]);

  // useMemo: cache statistics
  const stats = useMemo(() => ({
    total: items.length,
    done: items.filter((i) => i.done).length,
    active: items.filter((i) => !i.done).length,
  }), [items]);

  // useCallback: stable function for toggling items
  const handleToggle = useCallback((id) => {
    setItems((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, done: !item.done } : item
      )
    );
  }, []);

  // useCallback: stable function for deleting items
  const handleDelete = useCallback((id) => {
    setItems((prev) => prev.filter((item) => item.id !== id));
  }, []);

  function handleAdd(event) {
    event.preventDefault();
    if (!newItem.trim()) return;
    setItems((prev) => [
      ...prev,
      { id: Date.now(), name: newItem.trim(), done: false },
    ]);
    setNewItem("");
  }

  return (
    <div style={{ maxWidth: "500px", margin: "0 auto", padding: "1rem" }}>
      <h1>Todo List</h1>

      {/* Stats — memo'd component */}
      <Stats stats={stats} />

      {/* Add form — typing here re-renders Parent but NOT the list items */}
      <form onSubmit={handleAdd} style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
        <input
          type="text"
          value={newItem}
          onChange={(e) => setNewItem(e.target.value)}
          placeholder="Add a todo..."
          style={{ flex: 1, padding: "0.5rem" }}
        />
        <button type="submit">Add</button>
      </form>

      {/* Filter */}
      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
        {["all", "active", "done"].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            style={{
              padding: "0.25rem 0.75rem",
              backgroundColor: filter === f ? "#3182ce" : "transparent",
              color: filter === f ? "white" : "#4a5568",
              border: "1px solid #e2e8f0",
              borderRadius: "4px",
              cursor: "pointer",
            }}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {/* List — each item is memo'd */}
      {filteredItems.map((item) => (
        <TodoItem
          key={item.id}
          item={item}
          onToggle={handleToggle}
          onDelete={handleDelete}
        />
      ))}
    </div>
  );
}

// memo: only re-renders when its specific item, onToggle, or onDelete changes
const TodoItem = memo(function TodoItem({ item, onToggle, onDelete }) {
  console.log(`TodoItem rendered: ${item.name}`);

  return (
    <div style={{
      display: "flex",
      alignItems: "center",
      gap: "0.5rem",
      padding: "0.5rem",
      borderBottom: "1px solid #edf2f7",
    }}>
      <input
        type="checkbox"
        checked={item.done}
        onChange={() => onToggle(item.id)}
      />
      <span style={{
        flex: 1,
        textDecoration: item.done ? "line-through" : "none",
        color: item.done ? "#a0aec0" : "#2d3748",
      }}>
        {item.name}
      </span>
      <button
        onClick={() => onDelete(item.id)}
        style={{
          padding: "0.125rem 0.5rem",
          backgroundColor: "transparent",
          border: "1px solid #e53e3e",
          color: "#e53e3e",
          borderRadius: "4px",
          cursor: "pointer",
          fontSize: "0.75rem",
        }}
      >
        Delete
      </button>
    </div>
  );
});

// memo: only re-renders when stats object changes
const Stats = memo(function Stats({ stats }) {
  console.log("Stats rendered");

  return (
    <div style={{
      display: "flex",
      gap: "1rem",
      marginBottom: "1rem",
      padding: "0.75rem",
      backgroundColor: "#f7fafc",
      borderRadius: "8px",
    }}>
      <span>Total: {stats.total}</span>
      <span>Active: {stats.active}</span>
      <span>Done: {stats.done}</span>
    </div>
  );
});

export default App;
```

**How optimization works in this example:**

| Action | What Re-Renders | What Is Skipped |
|--------|----------------|-----------------|
| Typing in "Add" input | Parent only | Stats, all TodoItems |
| Adding a new item | Parent, Stats, new TodoItem | Existing TodoItems |
| Toggling an item | Parent, Stats, toggled TodoItem | Other TodoItems |
| Changing filter | Parent | Stats (same items), unaffected TodoItems |

Without optimization, every action would re-render every component. With optimization, only the affected components re-render.

---

## When to Optimize (and When NOT To)

### The Most Important Rule

**Do not optimize prematurely.** React is fast by default. Most components render in less than a millisecond. Adding `memo`, `useMemo`, and `useCallback` everywhere adds complexity without benefit.

### When Optimization Matters

Optimization is worth considering when:

1. **You can measure a performance problem.** The UI stutters, animations jank, or interactions feel slow.
2. **A component is expensive to render** — complex calculations, many DOM elements, or large lists.
3. **A component re-renders frequently** due to parent state changes that do not affect it.
4. **A list has hundreds or thousands of items** and re-renders on every keystroke (like search filtering).

### When Optimization Is Unnecessary

Do not bother optimizing when:

1. **The component is cheap to render** — simple JSX with a few elements.
2. **The component rarely re-renders** — adding `memo` saves nothing if it only renders twice.
3. **The optimization adds significant complexity** — if the code becomes harder to read for minimal gain.
4. **You have not measured a problem** — guessing at performance issues leads to wasted effort.

### The Cost of Over-Optimization

`memo`, `useMemo`, and `useCallback` are not free:

```jsx
// Without optimization: simple, readable
function Parent() {
  const items = data.filter(item => item.active);
  return <List items={items} />;
}

// With unnecessary optimization: more complex, same performance
function Parent() {
  const items = useMemo(() => data.filter(item => item.active), [data]);
  return <List items={items} />;
}
```

If `data.filter()` takes 0.1ms and the component renders 5 times per second, you are "saving" 0.5ms per second — imperceptible to the user. But the code is now harder to read, has a dependency array to maintain, and uses slightly more memory for caching.

### The Decision Framework

```
Is the component noticeably slow?
├── No → Do not optimize. React is fast enough.
│
├── Yes → Measure first (React DevTools Profiler)
│   │
│   ├── Is an expensive calculation running on every render?
│   │   └── Use useMemo to cache the calculation
│   │
│   ├── Is a child component re-rendering unnecessarily?
│   │   └── Wrap it with React.memo
│   │       └── Is memo defeated by object/function props?
│   │           ├── Object props → useMemo
│   │           └── Function props → useCallback
│   │
│   └── Is the list too large to render efficiently?
│       └── Consider virtualization (covered later)
```

---

## Profiling with React DevTools

Before optimizing, measure. React DevTools has a Profiler that shows exactly which components render and how long they take.

### How to Use the Profiler

1. Install the **React Developer Tools** browser extension (Chrome or Firefox).
2. Open your app and go to the **Profiler** tab in DevTools.
3. Click the **Record** button (circle icon).
4. Interact with your app (click buttons, type in inputs, etc.).
5. Click **Stop** to end recording.
6. Review the flame chart — it shows which components rendered and how long each took.

### What to Look For

```
Component Render Times:
  < 1ms    → Fast, no optimization needed
  1-5ms    → Normal, optimize only if rendering very frequently
  5-16ms   → Slow enough to notice at 60fps (16ms per frame)
  > 16ms   → Definitely needs optimization — will cause visual jank
```

### Adding Console Logs for Manual Profiling

During development, a simple approach:

```jsx
const ExpensiveComponent = memo(function ExpensiveComponent({ data }) {
  console.log("ExpensiveComponent rendered at", performance.now().toFixed(2));

  const start = performance.now();
  const result = expensiveCalculation(data);
  const end = performance.now();
  console.log(`Calculation took ${(end - start).toFixed(2)}ms`);

  return <div>{result}</div>;
});
```

---

## Referential Equality — Why It Matters

Understanding referential equality is crucial for using `memo`, `useMemo`, and `useCallback` correctly.

### Primitive Values vs Reference Values

```javascript
// Primitives: compared by VALUE
"hello" === "hello"     // true
42 === 42               // true
true === true           // true

// References: compared by IDENTITY (memory address)
{} === {}               // false (two different objects)
[] === []               // false (two different arrays)
(() => {}) === (() => {})  // false (two different functions)

// Same reference: true
const obj = { a: 1 };
const ref = obj;
obj === ref             // true (same object in memory)
```

### Why This Matters for React

Every time a component function runs:
- `const obj = { a: 1 }` creates a **new** object.
- `const arr = [1, 2, 3]` creates a **new** array.
- `const fn = () => {}` creates a **new** function.

Even if the content is identical, the reference is different. React's `memo` uses `===` to compare props, so it sees these as "changed."

```jsx
function Parent() {
  const [count, setCount] = useState(0);

  // NEW object every render → memo sees it as a change
  const config = { theme: "dark" };

  return <MemoizedChild config={config} />;
  // Child re-renders every time, despite memo!
}
```

**Fix with `useMemo`:**

```jsx
function Parent() {
  const [count, setCount] = useState(0);

  // SAME object between renders (unless dependencies change)
  const config = useMemo(() => ({ theme: "dark" }), []);

  return <MemoizedChild config={config} />;
  // Child only re-renders when config actually changes!
}
```

---

## Advanced Patterns

### Pattern 1: Expensive List with Stable Callbacks

```jsx
import { useState, useMemo, useCallback, memo } from "react";

function EmployeeDirectory() {
  const [employees] = useState(() => generateEmployees(1000));
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedId, setSelectedId] = useState(null);
  const [sortField, setSortField] = useState("name");

  const filteredEmployees = useMemo(() => {
    const term = searchTerm.toLowerCase();
    let result = employees.filter(
      (emp) =>
        emp.name.toLowerCase().includes(term) ||
        emp.department.toLowerCase().includes(term) ||
        emp.email.toLowerCase().includes(term)
    );

    result.sort((a, b) => {
      if (sortField === "name") return a.name.localeCompare(b.name);
      if (sortField === "department") return a.department.localeCompare(b.department);
      if (sortField === "salary") return a.salary - b.salary;
      return 0;
    });

    return result;
  }, [employees, searchTerm, sortField]);

  const handleSelect = useCallback((id) => {
    setSelectedId(id);
  }, []);

  const handleDelete = useCallback((id) => {
    console.log("Delete employee:", id);
  }, []);

  return (
    <div style={{ maxWidth: "800px", margin: "0 auto" }}>
      <h1>Employee Directory ({filteredEmployees.length})</h1>

      <div style={{ display: "flex", gap: "0.75rem", marginBottom: "1rem" }}>
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search employees..."
          style={{ flex: 1, padding: "0.5rem" }}
        />
        <select value={sortField} onChange={(e) => setSortField(e.target.value)}>
          <option value="name">Sort by Name</option>
          <option value="department">Sort by Department</option>
          <option value="salary">Sort by Salary</option>
        </select>
      </div>

      <div style={{ maxHeight: "500px", overflowY: "auto" }}>
        {filteredEmployees.map((employee) => (
          <EmployeeRow
            key={employee.id}
            employee={employee}
            isSelected={selectedId === employee.id}
            onSelect={handleSelect}
            onDelete={handleDelete}
          />
        ))}
      </div>
    </div>
  );
}

const EmployeeRow = memo(function EmployeeRow({ employee, isSelected, onSelect, onDelete }) {
  return (
    <div
      onClick={() => onSelect(employee.id)}
      style={{
        display: "flex",
        alignItems: "center",
        padding: "0.5rem 0.75rem",
        borderBottom: "1px solid #edf2f7",
        backgroundColor: isSelected ? "#ebf8ff" : "transparent",
        cursor: "pointer",
      }}
    >
      <div style={{ flex: 1 }}>
        <strong>{employee.name}</strong>
        <span style={{ color: "#718096", marginLeft: "0.5rem", fontSize: "0.875rem" }}>
          {employee.department}
        </span>
      </div>
      <span style={{ color: "#4a5568", minWidth: "100px" }}>
        ${employee.salary.toLocaleString()}
      </span>
      <button
        onClick={(e) => {
          e.stopPropagation();
          onDelete(employee.id);
        }}
        style={{
          marginLeft: "0.5rem",
          padding: "0.25rem 0.5rem",
          fontSize: "0.75rem",
          backgroundColor: "transparent",
          border: "1px solid #e53e3e",
          color: "#e53e3e",
          borderRadius: "4px",
          cursor: "pointer",
        }}
      >
        Delete
      </button>
    </div>
  );
});

function generateEmployees(count) {
  const names = ["Alice", "Bob", "Charlie", "Diana", "Edward", "Fiona", "George", "Helen"];
  const surnames = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Davis", "Miller", "Wilson"];
  const departments = ["Engineering", "Design", "Marketing", "Sales", "Support", "Finance"];

  return Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    name: `${names[i % names.length]} ${surnames[i % surnames.length]}`,
    department: departments[i % departments.length],
    email: `employee${i + 1}@company.com`,
    salary: 50000 + Math.floor(Math.random() * 100000),
  }));
}
```

**Performance breakdown:**

- `filteredEmployees` is memoized — filtering and sorting 1,000 employees only happens when `searchTerm`, `sortField`, or `employees` changes.
- `handleSelect` and `handleDelete` are wrapped in `useCallback` — they have stable references.
- Each `EmployeeRow` is wrapped in `memo` — it only re-renders when its specific `employee`, `isSelected`, `onSelect`, or `onDelete` prop changes.
- When the user types in the search box: the parent re-renders, the filtered list is recalculated, but only rows that appear or disappear from the filtered list need to re-render.
- When the user selects a row: only the previously selected and newly selected rows re-render.

### Pattern 2: Debounced Expensive Calculation

```jsx
import { useState, useMemo, useEffect } from "react";

function DataAnalyzer() {
  const [rawData] = useState(() => generateLargeDataset(10000));
  const [searchTerm, setSearchTerm] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");

  // Debounce the search term
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchTerm);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Expensive computation only runs when debounced search changes
  const analysis = useMemo(() => {
    console.log("Running analysis...");
    const filtered = rawData.filter((item) =>
      item.name.toLowerCase().includes(debouncedSearch.toLowerCase())
    );

    return {
      count: filtered.length,
      avgValue: filtered.length > 0
        ? filtered.reduce((sum, i) => sum + i.value, 0) / filtered.length
        : 0,
      maxValue: filtered.length > 0
        ? Math.max(...filtered.map((i) => i.value))
        : 0,
      minValue: filtered.length > 0
        ? Math.min(...filtered.map((i) => i.value))
        : 0,
      topItems: filtered.sort((a, b) => b.value - a.value).slice(0, 5),
    };
  }, [rawData, debouncedSearch]);

  return (
    <div style={{ maxWidth: "600px", margin: "0 auto" }}>
      <h2>Data Analyzer</h2>
      <input
        type="text"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        placeholder="Search 10,000 items..."
        style={{ width: "100%", padding: "0.75rem", marginBottom: "1rem", boxSizing: "border-box" }}
      />

      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "0.75rem", marginBottom: "1rem" }}>
        <StatCard label="Count" value={analysis.count.toLocaleString()} />
        <StatCard label="Average" value={analysis.avgValue.toFixed(2)} />
        <StatCard label="Max" value={analysis.maxValue.toFixed(2)} />
        <StatCard label="Min" value={analysis.minValue.toFixed(2)} />
      </div>

      <h3>Top 5 Items</h3>
      <ul>
        {analysis.topItems.map((item) => (
          <li key={item.id}>{item.name}: {item.value.toFixed(2)}</li>
        ))}
      </ul>
    </div>
  );
}

function StatCard({ label, value }) {
  return (
    <div style={{
      padding: "1rem",
      backgroundColor: "#f7fafc",
      borderRadius: "8px",
      textAlign: "center",
    }}>
      <p style={{ color: "#718096", fontSize: "0.75rem", margin: 0, textTransform: "uppercase" }}>{label}</p>
      <p style={{ fontSize: "1.5rem", fontWeight: "bold", margin: "0.25rem 0 0" }}>{value}</p>
    </div>
  );
}

function generateLargeDataset(count) {
  return Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    name: `Item ${i + 1}`,
    value: Math.random() * 1000,
  }));
}
```

**Double optimization:** Debouncing + memoization. The search term is debounced (300ms delay), so the expensive calculation runs at most once per 300ms. And `useMemo` ensures it only runs when the debounced term actually changes.

---

## React Compiler (React 19+)

React 19 introduces the **React Compiler** (formerly React Forget), which automatically adds memoization to your components. When the compiler is enabled, it analyzes your code and applies `memo`, `useMemo`, and `useCallback` automatically where beneficial.

**What this means for you:**

- In the future, you may not need to manually add these optimizations.
- Understanding the concepts is still essential — the compiler optimizes what it understands, but knowing the principles helps you write code the compiler can optimize effectively.
- The manual hooks remain available and useful for cases the compiler does not cover.

For now, manually applying these optimizations is still the standard approach in most projects.

---

## Common Mistakes

1. **Wrapping everything in memo/useMemo/useCallback.**

   ```jsx
   // ❌ Over-optimization — adds complexity for no benefit
   const greeting = useMemo(() => `Hello, ${name}!`, [name]);
   const handleClick = useCallback(() => setOpen(true), []);
   const style = useMemo(() => ({ color: "blue" }), []);

   // ✅ Only optimize what measurably needs it
   const greeting = `Hello, ${name}!`;  // String concatenation is instant
   function handleClick() { setOpen(true); } // Fine for most cases
   const style = { color: "blue" }; // Fine unless passed to a memo'd child
   ```

2. **Using memo without stabilizing object/function props.**

   ```jsx
   // ❌ memo is defeated — onClick is new on every render
   const Child = memo(function Child({ onClick }) { ... });
   <Child onClick={() => handleAction(id)} />

   // ✅ Stabilize the callback
   const handleAction = useCallback((id) => { ... }, []);
   <Child onClick={handleAction} />
   ```

3. **Wrong dependency arrays.**

   ```jsx
   // ❌ Missing dependency — stale value
   const filtered = useMemo(() => {
     return items.filter(i => i.type === filterType);
   }, [items]); // filterType is missing!

   // ✅ Include all dependencies
   const filtered = useMemo(() => {
     return items.filter(i => i.type === filterType);
   }, [items, filterType]);
   ```

4. **Using useMemo for cheap operations.**

   ```jsx
   // ❌ Filtering 10 items is instant — no need for useMemo
   const filtered = useMemo(() => {
     return shortList.filter(i => i.active);
   }, [shortList]);

   // ✅ Just compute it directly
   const filtered = shortList.filter(i => i.active);
   ```

5. **Forgetting that useCallback still creates a new function when dependencies change.**

   ```jsx
   // If `filter` changes on every render, useCallback provides no benefit
   const handleFilter = useCallback((item) => {
     return item.type === filter;
   }, [filter]); // New function every time filter changes
   ```

---

## Best Practices

1. **Measure before optimizing.** Use React DevTools Profiler or `performance.now()` to identify actual bottlenecks. Do not guess.

2. **Start without optimization.** Write clean, readable code first. Add optimization only when you measure a problem.

3. **Optimize the most impactful spots first.**
   - Large lists (100+ items) with frequent re-renders → `memo` + `useCallback`
   - Expensive calculations (sorting/filtering thousands of items) → `useMemo`
   - Components with many children that do not need to update → `memo`

4. **Use functional state updates inside useCallback** to avoid listing state as a dependency:

   ```jsx
   // ❌ Needs `items` as dependency — new function when items changes
   const handleAdd = useCallback((item) => {
     setItems([...items, item]);
   }, [items]);

   // ✅ No dependency on items — stable reference
   const handleAdd = useCallback((item) => {
     setItems((prev) => [...prev, item]);
   }, []);
   ```

5. **Keep dependency arrays accurate.** Never suppress the exhaustive-deps ESLint warning. If the linter says a dependency is missing, add it or restructure the code.

6. **Consider component structure** before reaching for memo. Sometimes restructuring (moving state closer to where it is used, or splitting a component) eliminates the need for optimization entirely.

7. **`useMemo` and `useCallback` are NOT guarantees.** React may choose to discard cached values under memory pressure. Write code that works correctly without memoization — these hooks should only improve performance, not change behavior.

---

## Summary

In this chapter, you learned:

- **Re-rendering**: when a parent re-renders, all children re-render too — even if their props have not changed.
- **`React.memo`** wraps a component to skip re-renders when props have not changed (using shallow comparison).
- **`useMemo`** caches the result of an expensive calculation and only recalculates when dependencies change. It also stabilizes object/array references for `memo`.
- **`useCallback`** caches a function reference and only creates a new function when dependencies change. It stabilizes function props for `memo`.
- **Referential equality** — objects, arrays, and functions are compared by reference, not by content. New instances on every render defeat `memo`.
- **When to optimize**: only when you can measure a performance problem. Most components are fast enough without optimization.
- **React DevTools Profiler** helps identify which components render and how long they take.
- **The three tools work together**: `memo` prevents re-renders, `useMemo` stabilizes data props, `useCallback` stabilizes function props.
- **React Compiler** may automate these optimizations in future React versions.

---

## Interview Questions

**Q1: What is `React.memo`, and when should you use it?**

`React.memo` is a higher-order component that prevents a component from re-rendering when its props have not changed. It performs a shallow comparison of the current and previous props. Use it when: a component is expensive to render, it re-renders frequently due to parent state changes, and its props rarely change. Do not use it for every component — the overhead of comparison and caching is not worth it for cheap components.

**Q2: What is the difference between `useMemo` and `useCallback`?**

`useMemo` caches a computed value — it runs a function and remembers the return value. `useCallback` caches a function reference — it remembers the function itself. `useCallback(fn, deps)` is equivalent to `useMemo(() => fn, deps)`. Use `useMemo` for expensive calculations and stabilizing object/array props. Use `useCallback` for stabilizing function props passed to memoized children.

**Q3: What is referential equality, and why does it matter for React performance?**

Referential equality means comparing values by their identity in memory (`===`). Primitive values (strings, numbers) are equal if their content matches. Objects, arrays, and functions are only equal if they are the exact same instance in memory — even if their content is identical. This matters because `React.memo` uses referential equality to compare props. If a parent creates new objects or functions on every render, `memo` sees them as changed and re-renders the child, defeating the optimization.

**Q4: When should you NOT use `useMemo` or `useCallback`?**

Do not use them for cheap operations (simple string concatenation, basic math, filtering a short list), for values not passed to memoized children, when the dependencies change on every render (making caching useless), or before measuring an actual performance problem. Over-optimization adds complexity, makes code harder to read, and uses additional memory for caching. The rule is: measure first, optimize second.

**Q5: How does the dependency array work in `useMemo` and `useCallback`?**

The dependency array tells React when to recalculate the memoized value. React compares each dependency with its value from the previous render using `Object.is()`. If any dependency has changed, React runs the function and caches the new result. If no dependencies have changed, React returns the cached value without running the function. An empty array `[]` means the value is calculated once and never recalculated. All values from the component scope that are used inside the memoized function must be included in the array.

**Q6: What happens if you omit a dependency from `useMemo` or `useCallback`?**

The memoized function captures the value of the omitted dependency at the time it was created and never sees updates — a "stale closure." This causes subtle bugs where the function uses outdated values. For example, a memoized filter callback that references `filterType` but does not include it in dependencies will always use the initial `filterType`, ignoring user changes. The `react-hooks/exhaustive-deps` ESLint rule catches this.

**Q7: Can `React.memo` prevent all unnecessary re-renders?**

No. `memo` only prevents re-renders caused by a parent re-rendering with unchanged props. It does NOT prevent re-renders caused by: the component's own state changing, a context value changing (context consumers always re-render on context changes), or a ref callback changing. Also, `memo`'s shallow comparison is defeated by new object/function references — you need `useMemo` and `useCallback` to stabilize those.

**Q8: How would you approach optimizing a React application that feels slow?**

First, identify the bottleneck using React DevTools Profiler — record a session of the slow interaction and examine which components render and how long they take. Common issues: (1) An expensive component re-renders too often — wrap it in `memo` and stabilize its props. (2) An expensive calculation runs on every render — wrap it in `useMemo`. (3) A very long list renders entirely — consider virtualization (rendering only visible items). (4) State is too high in the tree — move it closer to where it is used. Always measure before and after to confirm the optimization helped.

---

## Practice Exercises

**Exercise 1: Memoized Filter Dashboard**

Create a dashboard that:
- Generates 5,000 data items on mount
- Has search, category filter, and sort controls
- Uses `useMemo` to memoize the filtered/sorted results
- Has a "Theme toggle" button that changes background color (should NOT re-trigger the expensive filter)
- Add `console.log` to prove the filter only runs when its dependencies change

**Exercise 2: Optimized Contact List**

Build a contact list where:
- Each contact card is wrapped in `memo`
- Selecting a contact only re-renders the selected and previously selected cards
- A search input filters contacts without re-rendering non-affected cards
- Use `useCallback` for the `onSelect` handler
- Add a render counter to each card to visualize which ones re-render

**Exercise 3: Performance Comparison**

Create a side-by-side comparison component:
- Left side: An unoptimized list (no memo, no useMemo, no useCallback)
- Right side: The same list, fully optimized
- Both have 500 items with a search input
- Show a render count for each side
- Time how long each side takes to filter (display in ms)

**Exercise 4: Lazy Computed Fields**

Create a data table where:
- Each row has raw data and computed fields (e.g., full name from first + last, age from birth date)
- Computed fields are memoized per-row
- Adding a new row does not re-compute existing rows
- Sorting the table does not re-compute any rows
- The computation function includes a visible delay (console.log) to prove it only runs when needed

---

## What Is Next?

You now understand React's performance model and the tools available to optimize it. You can identify real performance problems, measure them, and apply targeted optimizations.

In Chapter 12, we will explore **Custom Hooks** — one of React's most powerful patterns. You will learn how to extract reusable logic from components into custom hooks, creating your own building blocks that can be shared across your application.
