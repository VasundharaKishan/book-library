# Chapter 28: The Memoization Pattern

## What You Will Learn

- What memoization is and how it works conceptually
- How `React.memo` prevents unnecessary component re-renders
- When and how to use `useMemo` for expensive calculations
- When and how to use `useCallback` for stable function references
- Why premature memoization can make things worse
- How to profile first and memoize second
- The real cost of memoization

## Why This Chapter Matters

Memoization is one of the most misunderstood concepts in React. Some developers sprinkle `React.memo`, `useMemo`, and `useCallback` everywhere, thinking they are "optimizing" their code. Others avoid them entirely because they heard they are unnecessary.

Both extremes are wrong.

Think of memoization like insulation in a house. In a cold climate, insulation saves you money on heating. In a tropical climate, it is a waste. And even in a cold climate, you insulate the walls, not the mailbox.

The key insight is: **memoization is medicine, not vitamins**. You should not take it preventatively. You should diagnose a performance problem first, then apply memoization where it actually helps.

This chapter teaches you how to diagnose, when to apply, and where each memoization tool fits.

---

## What Is Memoization?

Memoization is caching the result of a function based on its inputs. If the inputs have not changed, return the cached result instead of recalculating.

```
Without Memoization:

  calculate(5, 10) --> runs computation --> returns 50    (100ms)
  calculate(5, 10) --> runs computation --> returns 50    (100ms)
  calculate(5, 10) --> runs computation --> returns 50    (100ms)
  Total: 300ms for the same result three times

With Memoization:

  calculate(5, 10) --> runs computation --> caches (5,10)=50 --> returns 50 (100ms)
  calculate(5, 10) --> cache hit! --> returns 50                            (0.01ms)
  calculate(5, 10) --> cache hit! --> returns 50                            (0.01ms)
  Total: ~100ms. Saved ~200ms.

  calculate(5, 20) --> new inputs --> runs computation --> caches --> returns 100
```

### Pure JavaScript Memoization

```jsx
// A simple memoization function
function memoize(fn) {
  const cache = new Map();

  return function (...args) {
    const key = JSON.stringify(args);

    if (cache.has(key)) {
      console.log('Cache hit!');
      return cache.get(key);
    }

    console.log('Computing...');
    const result = fn(...args);
    cache.set(key, result);
    return result;
  };
}

// Example: Expensive Fibonacci calculation
function fibonacci(n) {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}

const memoizedFib = memoize(fibonacci);

memoizedFib(40); // Computing... (takes ~1 second)
                 // Output: 102334155

memoizedFib(40); // Cache hit! (instant)
                 // Output: 102334155
```

---

## React.memo: Preventing Component Re-Renders

### The Problem

In React, when a parent component re-renders, **all its children re-render too**, even if their props have not changed.

```jsx
function App() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <button onClick={() => setCount(c => c + 1)}>
        Count: {count}
      </button>

      {/* This re-renders EVERY TIME count changes */}
      {/* Even though it receives NO props related to count */}
      <ExpensiveChart data={staticData} />
    </div>
  );
}

function ExpensiveChart({ data }) {
  console.log('ExpensiveChart rendered'); // Logs on EVERY click!
  // Imagine this does complex SVG calculations
  return <svg>{/* complex chart */}</svg>;
}

// Output when clicking the button 3 times:
// "ExpensiveChart rendered"  (initial)
// "ExpensiveChart rendered"  (click 1 - unnecessary!)
// "ExpensiveChart rendered"  (click 2 - unnecessary!)
// "ExpensiveChart rendered"  (click 3 - unnecessary!)
```

### The Solution: React.memo

```jsx
// Wrap the component with React.memo
const ExpensiveChart = React.memo(function ExpensiveChart({ data }) {
  console.log('ExpensiveChart rendered');
  return <svg>{/* complex chart */}</svg>;
});

function App() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <button onClick={() => setCount(c => c + 1)}>
        Count: {count}
      </button>

      {/* Now this only re-renders when `data` actually changes */}
      <ExpensiveChart data={staticData} />
    </div>
  );
}

// Output when clicking the button 3 times:
// "ExpensiveChart rendered"  (initial render only!)
// (no more logs - React.memo prevents re-renders)
```

### How React.memo Works

```
Without React.memo:
  Parent renders --> React renders ALL children
  Parent renders --> React renders ALL children (again)

With React.memo:
  Parent renders --> React checks: did props change?
                     YES --> render child
                     NO  --> skip child, reuse last result

  React.memo does a SHALLOW comparison of props:
    { data: [1,2,3] } === { data: [1,2,3] }  --> FALSE (different reference)
    { data: sameArray } === { data: sameArray } --> TRUE (same reference)
    { name: "Alice" } === { name: "Alice" } --> TRUE (same primitive value)
```

### Custom Comparison Function

```jsx
// Default: React.memo uses shallow equality (Object.is for each prop)
const MemoizedComponent = React.memo(MyComponent);

// Custom: You can provide your own comparison function
const MemoizedComponent = React.memo(MyComponent, (prevProps, nextProps) => {
  // Return TRUE if props are EQUAL (skip re-render)
  // Return FALSE if props are DIFFERENT (re-render)

  // Only re-render if the `id` or `name` changed
  // Ignore changes to `lastUpdated` timestamp
  return (
    prevProps.id === nextProps.id &&
    prevProps.name === nextProps.name
  );
});

// Usage example:
function UserCard({ id, name, lastUpdated, onlineStatus }) {
  console.log(`UserCard ${name} rendered`);
  return (
    <div>
      <h3>{name}</h3>
      <span>{onlineStatus}</span>
    </div>
  );
}

const MemoizedUserCard = React.memo(UserCard, (prev, next) => {
  // Only re-render when name or onlineStatus changes
  // Skip re-render for lastUpdated changes (cosmetic, not visual)
  return (
    prev.name === next.name &&
    prev.onlineStatus === next.onlineStatus
  );
});
```

---

## useMemo: Caching Expensive Calculations

### The Problem

Some calculations are expensive. If their inputs have not changed, running them again is wasted work.

```jsx
function ProductList({ products, filterText }) {
  // This runs on EVERY render, even if products and filterText
  // have not changed (e.g., parent re-rendered for unrelated reason)
  const filteredProducts = products
    .filter(p => p.name.toLowerCase().includes(filterText.toLowerCase()))
    .sort((a, b) => a.price - b.price)
    .map(p => ({
      ...p,
      discountedPrice: calculateComplexDiscount(p),
    }));

  return (
    <ul>
      {filteredProducts.map(p => (
        <li key={p.id}>{p.name} - ${p.discountedPrice}</li>
      ))}
    </ul>
  );
}
// With 10,000 products, this filtering + sorting + discount calculation
// might take 50-100ms. Running it 60 times per second is a problem.
```

### The Solution: useMemo

```jsx
function ProductList({ products, filterText }) {
  // Only recalculates when products OR filterText changes
  const filteredProducts = useMemo(() => {
    console.log('Recalculating filtered products...');
    return products
      .filter(p =>
        p.name.toLowerCase().includes(filterText.toLowerCase())
      )
      .sort((a, b) => a.price - b.price)
      .map(p => ({
        ...p,
        discountedPrice: calculateComplexDiscount(p),
      }));
  }, [products, filterText]); // Dependency array

  return (
    <ul>
      {filteredProducts.map(p => (
        <li key={p.id}>{p.name} - ${p.discountedPrice}</li>
      ))}
    </ul>
  );
}

// Output:
// First render: "Recalculating filtered products..."
// Parent re-renders (unrelated state change): (no log - cached!)
// filterText changes: "Recalculating filtered products..."
// products array changes: "Recalculating filtered products..."
```

### useMemo for Stable Object References

```jsx
// PROBLEM: New object created every render, breaks React.memo on child
function Parent() {
  const [count, setCount] = useState(0);

  // New object on EVERY render, even though values are the same
  const style = { color: 'blue', fontSize: 16 };

  return (
    <div>
      <button onClick={() => setCount(c => c + 1)}>
        Count: {count}
      </button>
      {/* MemoizedChild re-renders because style is new object */}
      <MemoizedChild style={style} />
    </div>
  );
}

// FIX: Memoize the object
function Parent() {
  const [count, setCount] = useState(0);

  // Same object reference unless values change
  const style = useMemo(
    () => ({ color: 'blue', fontSize: 16 }),
    [] // No dependencies = never recalculated
  );

  return (
    <div>
      <button onClick={() => setCount(c => c + 1)}>
        Count: {count}
      </button>
      {/* MemoizedChild skips re-render because style reference is stable */}
      <MemoizedChild style={style} />
    </div>
  );
}
```

---

## useCallback: Stable Function References

### The Problem

Functions defined inside a component are recreated on every render. This breaks `React.memo` on children that receive those functions as props.

```jsx
function TodoList() {
  const [todos, setTodos] = useState([]);
  const [input, setInput] = useState('');

  // NEW function created on every render
  const handleDelete = (id) => {
    setTodos(prev => prev.filter(t => t.id !== id));
  };

  // NEW function created on every render
  const handleToggle = (id) => {
    setTodos(prev =>
      prev.map(t => (t.id === id ? { ...t, done: !t.done } : t))
    );
  };

  return (
    <div>
      <input value={input} onChange={e => setInput(e.target.value)} />
      {todos.map(todo => (
        // Even with React.memo on TodoItem, it re-renders
        // because handleDelete and handleToggle are new functions
        <TodoItem
          key={todo.id}
          todo={todo}
          onDelete={handleDelete}
          onToggle={handleToggle}
        />
      ))}
    </div>
  );
}

const TodoItem = React.memo(function TodoItem({ todo, onDelete, onToggle }) {
  console.log(`Rendering todo: ${todo.text}`);
  return (
    <div>
      <input
        type="checkbox"
        checked={todo.done}
        onChange={() => onToggle(todo.id)}
      />
      <span>{todo.text}</span>
      <button onClick={() => onDelete(todo.id)}>Delete</button>
    </div>
  );
});

// Output when typing in input (which changes `input` state):
// "Rendering todo: Buy groceries"    <-- unnecessary!
// "Rendering todo: Walk the dog"     <-- unnecessary!
// "Rendering todo: Read book"        <-- unnecessary!
// All todos re-render because function props are new references
```

### The Solution: useCallback

```jsx
function TodoList() {
  const [todos, setTodos] = useState([]);
  const [input, setInput] = useState('');

  // Stable function reference - only changes when dependencies change
  const handleDelete = useCallback((id) => {
    setTodos(prev => prev.filter(t => t.id !== id));
  }, []); // No dependencies needed - uses functional updater

  const handleToggle = useCallback((id) => {
    setTodos(prev =>
      prev.map(t => (t.id === id ? { ...t, done: !t.done } : t))
    );
  }, []); // No dependencies needed - uses functional updater

  return (
    <div>
      <input value={input} onChange={e => setInput(e.target.value)} />
      {todos.map(todo => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onDelete={handleDelete}   // Same reference every render!
          onToggle={handleToggle}   // Same reference every render!
        />
      ))}
    </div>
  );
}

// Output when typing in input:
// (nothing logged - React.memo works because function refs are stable!)
```

---

## When Memoization Helps vs. When It Hurts

### Profile First, Memoize Second

```
Step 1: Notice a performance issue (laggy typing, janky scrolling)
Step 2: Open React DevTools Profiler
Step 3: Record the interaction
Step 4: Find which components re-render unnecessarily
Step 5: Apply memoization to THOSE specific components
Step 6: Profile again to verify improvement

Do NOT do this:
Step 1: "I heard memoization makes things faster"
Step 2: Add React.memo to every component
Step 3: Add useMemo and useCallback to everything
Step 4: Wonder why the code is harder to read and not faster
```

### The Cost of Memoization

```
React.memo cost:
  + Shallow comparison of all props on every render
  + Memory to store the previous render result
  + Added code complexity

  Worth it when:
    Component is expensive to render (complex DOM, calculations)
    Component renders often with the same props
    Component is deep in the tree with many expensive children

  NOT worth it when:
    Component is simple (a few divs and text)
    Props almost always change (comparison cost wasted)
    Component is at the top of the tree (re-renders are rare)

useMemo cost:
  + Dependency array comparison on every render
  + Memory to store the cached value
  + Added code complexity

  Worth it when:
    Calculation takes measurable time (>1ms)
    Result is passed to React.memo'd children as a prop
    Calculation runs frequently with same inputs

  NOT worth it when:
    Calculation is trivial (simple math, string concat)
    Dependencies change on every render (never hits cache)
    Value is only used in this component (no child optimization)

useCallback cost:
  + Dependency array comparison on every render
  + Memory for the closure
  + Added code complexity

  Worth it when:
    Function is passed to React.memo'd children
    Function is a dependency of useEffect or other hooks
    Function is used in a virtualized list with many items

  NOT worth it when:
    Function is passed to native HTML elements (<button onClick>)
    No child uses React.memo
    Dependencies change every render
```

### Examples of Premature Optimization

```jsx
// BAD: Memoizing trivial values
function UserProfile({ user }) {
  // This addition takes nanoseconds. useMemo overhead > savings.
  const age = useMemo(
    () => new Date().getFullYear() - user.birthYear,
    [user.birthYear]
  );

  // This string concat is instant. useMemo adds overhead.
  const fullName = useMemo(
    () => `${user.firstName} ${user.lastName}`,
    [user.firstName, user.lastName]
  );

  return (
    <div>
      <h1>{fullName}</h1>
      <p>Age: {age}</p>
    </div>
  );
}

// GOOD: Just compute it directly
function UserProfile({ user }) {
  const age = new Date().getFullYear() - user.birthYear;
  const fullName = `${user.firstName} ${user.lastName}`;

  return (
    <div>
      <h1>{fullName}</h1>
      <p>Age: {age}</p>
    </div>
  );
}
```

```jsx
// BAD: useCallback for native element handlers
function SearchBox() {
  const [query, setQuery] = useState('');

  // Wrapping in useCallback is pointless here
  // <input> is a native element, not a React.memo'd component
  const handleChange = useCallback((e) => {
    setQuery(e.target.value);
  }, []);

  return <input value={query} onChange={handleChange} />;
}

// GOOD: Just use a plain function
function SearchBox() {
  const [query, setQuery] = useState('');
  return (
    <input
      value={query}
      onChange={(e) => setQuery(e.target.value)}
    />
  );
}
```

---

## Profiling with React DevTools

### Step-by-Step Profiling

```
1. Install React DevTools browser extension
2. Open your app and go to the "Profiler" tab
3. Click "Start profiling" (record button)
4. Perform the slow interaction (type, scroll, click)
5. Click "Stop profiling"
6. Examine the results

What to look for:
+------------------------------------------------------------------+
| Profiler Results                                                  |
+------------------------------------------------------------------+
| Component          | Renders | Time   | Why                      |
+------------------------------------------------------------------+
| App                | 5       | 2ms    | State changed            |
| Header             | 5       | 0.5ms  | Parent rendered          | <-- candidate
| ProductList        | 5       | 45ms   | Parent rendered          | <-- problem!
|   ProductCard (x50)| 250     | 40ms   | Parent rendered          | <-- problem!
| Footer             | 5       | 0.3ms  | Parent rendered          | <-- candidate
+------------------------------------------------------------------+

Analysis:
- ProductList renders 5 times even though products did not change
- Each render causes 50 ProductCards to re-render
- Total wasted: ~200ms of rendering for nothing

Solution:
1. Wrap ProductList with React.memo
2. Wrap ProductCard with React.memo
3. Use useCallback for onAddToCart passed from App to ProductList
```

### Highlight Updates in React DevTools

```
In React DevTools Settings:
  Check "Highlight updates when components render"

Now every re-render flashes a colored border:
  Green  = fast render (< 16ms)
  Yellow = moderate render (16-100ms)
  Red    = slow render (> 100ms)

When typing in a search box, you should see:
  - Search input: green flash (expected)
  - Product cards: NO flash (they should not re-render!)

If product cards flash, they are re-rendering unnecessarily.
```

---

## Real-World Use Case: Dashboard with Multiple Widgets

```jsx
import React, { useState, useMemo, useCallback, memo } from 'react';

// Expensive chart component
const SalesChart = memo(function SalesChart({ data, timeRange }) {
  console.log('SalesChart rendered');

  // Expensive: processes thousands of data points
  const chartData = useMemo(() => {
    return data
      .filter(d => d.date >= timeRange.start && d.date <= timeRange.end)
      .reduce((acc, d) => {
        const month = d.date.substring(0, 7);
        acc[month] = (acc[month] || 0) + d.amount;
        return acc;
      }, {});
  }, [data, timeRange]);

  return (
    <div className="chart">
      {Object.entries(chartData).map(([month, total]) => (
        <div key={month} className="bar" style={{ height: total / 100 }}>
          {month}: ${total}
        </div>
      ))}
    </div>
  );
});

// Expensive table component
const TopProducts = memo(function TopProducts({ products, onSelect }) {
  console.log('TopProducts rendered');

  const sortedProducts = useMemo(
    () => [...products].sort((a, b) => b.revenue - a.revenue).slice(0, 10),
    [products]
  );

  return (
    <table>
      <thead>
        <tr><th>Product</th><th>Revenue</th></tr>
      </thead>
      <tbody>
        {sortedProducts.map(p => (
          <tr key={p.id} onClick={() => onSelect(p.id)}>
            <td>{p.name}</td>
            <td>${p.revenue.toLocaleString()}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
});

// Simple stat card - NOT memoized (too cheap to bother)
function StatCard({ label, value }) {
  return (
    <div className="stat-card">
      <h4>{label}</h4>
      <p className="stat-value">{value}</p>
    </div>
  );
}

// Dashboard orchestrator
function Dashboard() {
  const [salesData] = useState(generateSalesData);     // 50K records
  const [products] = useState(generateProductData);     // 1000 products
  const [timeRange, setTimeRange] = useState(defaultRange);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Stable callback for child components
  const handleProductSelect = useCallback((id) => {
    setSelectedProduct(id);
  }, []);

  // Memoize time range to avoid breaking SalesChart memo
  const stableTimeRange = useMemo(
    () => timeRange,
    [timeRange.start, timeRange.end]
  );

  // Cheap calculations - no need for useMemo
  const totalRevenue = salesData.reduce((sum, d) => sum + d.amount, 0);
  const avgOrder = totalRevenue / salesData.length;

  return (
    <div className="dashboard">
      <button onClick={() => setSidebarOpen(s => !s)}>
        Toggle Sidebar
      </button>

      {/* These are cheap - re-render is fine */}
      <StatCard label="Total Revenue" value={`$${totalRevenue}`} />
      <StatCard label="Average Order" value={`$${avgOrder.toFixed(2)}`} />

      {/* These are expensive - memo prevents re-render when sidebar toggles */}
      <SalesChart data={salesData} timeRange={stableTimeRange} />
      <TopProducts products={products} onSelect={handleProductSelect} />
    </div>
  );
}

// Output when toggling sidebar:
// (No "SalesChart rendered" or "TopProducts rendered" logs)
// Only the sidebar and stat cards re-render. Dashboard stays fast.
//
// Output when changing time range:
// "SalesChart rendered" (expected - timeRange changed)
// (No "TopProducts rendered" - products did not change)
```

---

## When to Use / When NOT to Use

### Use React.memo When

- Component re-renders frequently with the same props
- Component is expensive to render (complex DOM, calculations)
- Component has many children that also re-render
- Component is in a list rendered by a virtualized container

### Do NOT Use React.memo When

- Component is simple and renders fast anyway
- Props change on almost every render (comparison cost is wasted)
- Component is the root or near-root (re-renders are infrequent)

### Use useMemo When

- Calculation takes measurable time (filter/sort/transform large arrays)
- Result is used as a prop for a memoized child component
- Result is used as a dependency in another hook
- Creating a new object/array that breaks child memoization

### Do NOT Use useMemo When

- Calculation is trivial (basic math, simple string operations)
- Dependencies change on every render (cache never hits)
- Value is only used locally in simple rendering

### Use useCallback When

- Function is passed to a React.memo'd child component
- Function is in a dependency array of useEffect/useMemo
- Function is passed to many items in a virtualized list

### Do NOT Use useCallback When

- Function is passed only to native HTML elements
- No child component uses React.memo
- Function dependencies change every render

---

## Common Mistakes

### Mistake 1: Memoizing Everything

```jsx
// WRONG: Memoizing trivial values and simple components
const Title = React.memo(({ text }) => <h1>{text}</h1>);

function App() {
  const title = useMemo(() => 'Hello World', []);
  const handleClick = useCallback(() => console.log('click'), []);

  return (
    <div>
      <Title text={title} />
      <button onClick={handleClick}>Click</button>
    </div>
  );
}
// All this memoization adds complexity for ZERO performance gain.
// <h1> rendering is essentially free.
```

### Mistake 2: Missing Dependencies

```jsx
// WRONG: Stale closure - count will always be 0
const handleClick = useCallback(() => {
  console.log(count); // Always logs 0!
  setCount(count + 1); // Always sets to 1!
}, []); // Missing 'count' in dependencies

// RIGHT: Use functional updater to avoid dependency
const handleClick = useCallback(() => {
  setCount(prev => prev + 1); // Always correct!
}, []); // No dependencies needed with functional updater

// OR include the dependency
const handleClick = useCallback(() => {
  console.log(count);
  setCount(count + 1);
}, [count]); // But this changes on every count update
```

### Mistake 3: React.memo with Inline Objects/Functions

```jsx
// WRONG: React.memo is useless here because props are new every render
const MemoizedChild = React.memo(ChildComponent);

function Parent() {
  return (
    <MemoizedChild
      style={{ color: 'red' }}          // New object every render!
      onClick={() => console.log('hi')} // New function every render!
      config={{ theme: 'dark' }}        // New object every render!
    />
  );
  // React.memo compares props, but EVERY prop is a new reference.
  // The memo wrapper does comparison work + renders anyway. Worse than no memo!
}

// RIGHT: Stabilize the props
function Parent() {
  const style = useMemo(() => ({ color: 'red' }), []);
  const handleClick = useCallback(() => console.log('hi'), []);
  const config = useMemo(() => ({ theme: 'dark' }), []);

  return (
    <MemoizedChild
      style={style}
      onClick={handleClick}
      config={config}
    />
  );
}
```

---

## Best Practices

1. **Profile before memoizing** -- Use React DevTools Profiler to find actual bottlenecks. Do not guess.

2. **Start without memoization** -- Write your components normally first. Add memoization only when profiling shows a problem.

3. **Memoize expensive components, not cheap ones** -- A component that renders a complex chart is worth memoizing. A component that renders `<h1>` is not.

4. **Use functional state updaters with useCallback** -- `setCount(prev => prev + 1)` avoids the need to include `count` in dependencies.

5. **Keep dependency arrays accurate** -- Never lie about dependencies. Use the ESLint `exhaustive-deps` rule.

6. **Consider component structure** -- Sometimes restructuring components (lifting state up or pushing it down) eliminates the need for memoization entirely.

7. **Measure the impact** -- After adding memoization, profile again. If there is no measurable improvement, remove it. Simpler code is better code.

8. **Memoize at the right level** -- If a parent passes props to 50 children, memoize the children (not each individual prop calculation).

---

## Quick Summary

Memoization in React comes in three forms: `React.memo` (skip re-rendering a component if props have not changed), `useMemo` (cache an expensive calculation between renders), and `useCallback` (cache a function reference between renders). All three exist to avoid unnecessary work. But they are not free -- they add memory overhead, comparison costs, and code complexity. The correct approach is to profile first, identify actual performance bottlenecks, then apply memoization surgically to the specific components and calculations that benefit from it. Premature memoization makes code harder to read without improving performance.

---

## Key Points

- **React.memo**: Wraps a component to skip re-render when props are unchanged (shallow comparison).
- **useMemo**: Caches a computed value; recalculates only when dependencies change.
- **useCallback**: Caches a function reference; creates a new function only when dependencies change.
- **Profile first**: Use React DevTools Profiler to find real performance problems before optimizing.
- **Premature optimization hurts**: Memoization adds overhead. Only apply it where measured performance gains exist.
- **Shallow comparison**: React.memo and useMemo compare by reference, not deep equality.
- **Stable references matter**: Inline objects and functions break React.memo on children.
- **Functional updaters**: `setState(prev => ...)` avoids stale closures and extra dependencies.

---

## Practice Questions

1. A developer wraps every component in their app with `React.memo`. What are the potential downsides of this approach?

2. You have a component that receives a `user` object as a prop. The parent recreates this object on every render (`{name: 'Alice', age: 30}`), even though the values do not change. How would you fix this to work with `React.memo`?

3. Explain the difference between `useMemo` and `useCallback`. Could you implement `useCallback` using `useMemo`? Show how.

4. A search component filters a list of 100 items on every keystroke. A developer wraps the filter logic in `useMemo`. Is this optimization worth it? Why or why not?

5. Your React DevTools Profiler shows that a `DataTable` component re-renders 20 times in 3 seconds, each taking 50ms. The props do not change between renders. What steps would you take to fix this?

---

## Exercises

### Exercise 1: Find the Bottleneck

Create a dashboard with 4 widgets: a counter button, a list of 1000 items, a chart (simulate with a loop), and a text input. Without any memoization, type in the input and observe the lag. Use React DevTools Profiler to identify which widgets re-render unnecessarily. Then apply targeted memoization and measure the improvement.

### Exercise 2: Memoization Audit

Take an existing React project (yours or open-source). Search for all uses of `React.memo`, `useMemo`, and `useCallback`. For each one, determine whether it is:
- Necessary and effective
- Unnecessary (premature optimization)
- Broken (dependencies are wrong or inline objects break the memo)

### Exercise 3: Refactor vs. Memoize

Build a parent component with a text input and a child that displays an expensive list. First, fix the unnecessary re-renders using memoization. Then, refactor the component structure to achieve the same result WITHOUT any memoization (hint: push the state down to a sibling component). Compare the two approaches.

---

## What Is Next?

Memoization prevents wasted rendering work. But what happens when something goes truly wrong -- a JavaScript error that crashes your component? Without proper handling, one error can take down your entire application. In Chapter 29, we will learn the **Error Boundary Pattern** -- how to catch errors at component boundaries, display graceful fallback UIs, and recover without losing the entire page.
