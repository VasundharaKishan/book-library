# Chapter 22: Debugging React Applications

## Learning Goals

By the end of this chapter, you will be able to:

- Use React DevTools to inspect component trees, props, state, and hooks
- Profile rendering performance and identify unnecessary re-renders
- Use browser DevTools effectively for React debugging
- Set breakpoints in JSX components and step through code
- Read and interpret common React error messages
- Debug state management issues (stale state, unexpected re-renders)
- Debug useEffect problems (infinite loops, missing dependencies, stale closures)
- Debug network and API integration issues
- Apply a systematic debugging methodology
- Use console methods beyond console.log

---

## The Debugging Mindset

Before diving into tools, understand the approach. Debugging is not about guessing — it is about systematic investigation.

**The debugging process:**

1. **Reproduce** — Make the bug happen consistently. If you cannot reproduce it, you cannot fix it.
2. **Isolate** — Narrow down where the bug originates. Which component? Which function? Which line?
3. **Understand** — Why does the bug happen? What is the code actually doing vs what you expect?
4. **Fix** — Change the code to produce the correct behavior.
5. **Verify** — Confirm the fix works and does not break anything else.

The most common mistake is skipping step 3. Developers often jump from "I found the broken line" to "let me change it" without understanding the root cause. This leads to patches that fix one symptom while creating new bugs.

---

## React DevTools

React DevTools is a browser extension (available for Chrome and Firefox) that adds React-specific inspection capabilities to the browser's developer tools.

### Installation

Install from the Chrome Web Store or Firefox Add-ons — search for "React Developer Tools." After installation, two new tabs appear in your browser's DevTools: **Components** and **Profiler**.

### The Components Tab

The Components tab shows your React component tree, similar to the Elements tab but showing React components instead of DOM elements.

**What you can see:**

- The full component hierarchy (which components are inside which)
- Props passed to each component
- State values (useState, useReducer)
- Hook values (useContext, useRef, useMemo, custom hooks)
- The source file and line number of each component

**What you can do:**

- **Click a component** to see its props, state, and hooks in the right panel
- **Edit state and props** directly to test different scenarios without changing code
- **Search** for components by name using the search bar
- **Filter** components to hide ones you do not care about (like third-party library components)
- **Inspect the DOM element** — click the eye icon to jump to the corresponding DOM node in the Elements tab
- **Log component data** — click the bug icon to log the component's props, state, and hooks to the console

### Inspecting State Changes

One of the most useful features: you can watch state change in real time. Open the Components tab, select a component, and interact with your app. The state values update live in the DevTools panel.

This is invaluable for debugging:

- "Why is this value wrong?" — Select the component and check its state
- "Which prop is causing the issue?" — Compare expected vs actual prop values
- "Is this hook returning the right value?" — Expand the hooks section

### The Profiler Tab

The Profiler records rendering activity and shows you what rendered, when, and why. This is your primary tool for performance debugging.

**How to use it:**

1. Click the record button (blue circle)
2. Interact with your app (click buttons, type in inputs, navigate)
3. Click the record button again to stop
4. Examine the flame chart

**What the Profiler shows:**

- **Flame chart** — Each bar is a component. The width represents render time. The color indicates how long it took (green = fast, yellow = medium, orange = slow)
- **Ranked chart** — Components sorted by render time, most expensive first
- **Why did this render?** — Enable "Record why each component rendered" in settings. For each component, it shows: "Props changed," "State changed," "Parent rendered," or "Hooks changed"

**How to enable "why" information:**

1. Open React DevTools settings (gear icon)
2. Under Profiler, check "Record why each component rendered while profiling"

### Finding Unnecessary Re-Renders

The Profiler's "why did this render" feature is the fastest way to find performance issues:

```
Component: ProductCard
Why did this render?
  → The parent component rendered.
```

If a component re-rendered because its parent rendered, but its own props and state did not change, it is an unnecessary re-render. Consider wrapping it in `React.memo`.

```
Component: ExpensiveList
Why did this render?
  → Props changed: (items)
```

If `items` is a new array reference on every render (even with the same data), the component re-renders unnecessarily. The fix is memoizing the array with `useMemo` in the parent.

### Highlight Updates

React DevTools can visually highlight components as they re-render:

1. Open React DevTools settings (gear icon)
2. Check "Highlight updates when components render"

Now, every time a component re-renders, a colored border flashes around it. This makes it immediately obvious which components re-render when you type in an input, click a button, or interact with the page.

Green borders = fast renders. Yellow/red borders = slow renders.

---

## Browser DevTools for React

### The Console

The console is your first debugging tool. But there is more to it than `console.log`.

**`console.log` — Basic output:**

```jsx
function UserProfile({ user }) {
  console.log("UserProfile render:", user);
  return <h2>{user.name}</h2>;
}
```

**`console.table` — Structured data:**

```jsx
console.table(users);
// Displays an interactive table in the console
// Perfect for arrays of objects

console.table(user);
// Displays object properties in a table format
```

**`console.group` / `console.groupEnd` — Grouped output:**

```jsx
function processOrder(order) {
  console.group(`Processing Order #${order.id}`);
  console.log("Items:", order.items);
  console.log("Total:", order.total);
  console.log("Status:", order.status);
  console.groupEnd();
}
```

**`console.count` — Count executions:**

```jsx
function ExpensiveComponent({ data }) {
  console.count("ExpensiveComponent render");
  // Outputs: "ExpensiveComponent render: 1", "ExpensiveComponent render: 2", etc.
  return <div>{/* ... */}</div>;
}
```

This immediately shows how many times a component renders. If you see it climbing rapidly, you have a re-rendering problem.

**`console.time` / `console.timeEnd` — Measure duration:**

```jsx
function processLargeDataset(data) {
  console.time("Data processing");
  const result = data.map(/* expensive operation */);
  console.timeEnd("Data processing");
  // Outputs: "Data processing: 142.5ms"
  return result;
}
```

**`console.trace` — Stack trace:**

```jsx
function updateUser(user) {
  console.trace("updateUser called");
  // Shows the complete call stack — who called this function?
}
```

**`console.warn` and `console.error` — Severity levels:**

```jsx
if (items.length > 1000) {
  console.warn("Large item list may cause performance issues:", items.length);
}

if (!user) {
  console.error("User is null — this should not happen");
}
```

### Breakpoints

Breakpoints pause code execution at a specific line, letting you inspect variables, step through code line by line, and see the call stack.

**Setting breakpoints in the Sources tab:**

1. Open DevTools → Sources tab
2. Find your file in the file tree (under `src/`)
3. Click the line number where you want to pause
4. A blue marker appears — the breakpoint is set
5. Interact with your app — execution pauses at the breakpoint

**The `debugger` statement:**

You can also set breakpoints directly in code:

```jsx
function handleSubmit(formData) {
  debugger; // Execution pauses here when DevTools is open
  validateForm(formData);
  submitToAPI(formData);
}
```

Remove `debugger` statements before committing. They are for local debugging only.

**Stepping through code:**

When paused at a breakpoint, use the control buttons:

- **Step Over (F10)** — Execute the current line and move to the next
- **Step Into (F11)** — Enter the function called on the current line
- **Step Out (Shift+F11)** — Finish the current function and return to the caller
- **Resume (F8)** — Continue execution until the next breakpoint

**Conditional breakpoints:**

Right-click a line number → "Add conditional breakpoint" → enter a condition:

```
userId === 42
```

The breakpoint only triggers when the condition is true. This is useful for debugging a specific item in a loop or a specific user's data.

### The Network Tab

The Network tab shows every HTTP request your application makes. This is essential for debugging API issues.

**What to check:**

- **Status codes** — 200 (success), 404 (not found), 500 (server error), 401 (unauthorized)
- **Request payload** — Is the correct data being sent?
- **Response body** — Is the server returning what you expect?
- **Timing** — How long do requests take?
- **Headers** — Is the Authorization header present? Is Content-Type correct?

**Filtering:**

- Click "Fetch/XHR" to show only API calls (hide CSS, JS, images)
- Use the search bar to filter by URL

**Common API bugs found in the Network tab:**

- Wrong URL (typo in the endpoint)
- Missing or wrong Authorization header
- Request payload has wrong field names
- Server returns different data structure than expected
- CORS errors (check the Console for these)

---

## Debugging Common React Problems

### Problem 1: Component Re-Renders Too Many Times

**Symptom:** The UI is slow, `console.count` shows dozens of renders, or the React Profiler shows unnecessary renders.

**Common causes and fixes:**

**Cause: Creating new objects/arrays/functions in render**

```jsx
// PROBLEM — new object on every render
function Parent() {
  return <Child style={{ color: "red" }} />;
  //                    ^^^^^^^^^^^^^^^^ new object every render
}

// FIX — define outside or memoize
const style = { color: "red" };
function Parent() {
  return <Child style={style} />;
}
```

```jsx
// PROBLEM — new function on every render
function Parent() {
  return <Child onClick={() => console.log("clicked")} />;
  //                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ new function every render
}

// FIX — useCallback
function Parent() {
  const handleClick = useCallback(() => console.log("clicked"), []);
  return <Child onClick={handleClick} />;
}
```

**Cause: State update in parent re-renders all children**

```jsx
// PROBLEM — typing in search re-renders every ProductCard
function ProductPage() {
  const [search, setSearch] = useState("");
  const [products, setProducts] = useState(largeProductList);

  return (
    <div>
      <input value={search} onChange={(e) => setSearch(e.target.value)} />
      {products.map((p) => (
        <ProductCard key={p.id} product={p} /> // Re-renders on every keystroke
      ))}
    </div>
  );
}

// FIX — memoize the child component
const ProductCard = React.memo(function ProductCard({ product }) {
  return <div>{product.name}</div>;
});
```

**Debugging approach:**

1. Add `console.count("ComponentName render")` to the suspected component
2. Open React DevTools Profiler with "why did this render" enabled
3. Record while reproducing the slow interaction
4. Check which components re-render and why
5. Apply the appropriate fix (memo, useMemo, useCallback, state restructuring)

### Problem 2: useEffect Infinite Loop

**Symptom:** The browser freezes or crashes, the console shows rapid-fire state updates, or the Network tab shows hundreds of API calls.

**Common causes:**

```jsx
// PROBLEM 1 — missing dependency array
useEffect(() => {
  fetchData(); // Runs on EVERY render, which triggers a state update, which triggers a re-render, which runs the effect again...
});

// FIX — add dependency array
useEffect(() => {
  fetchData();
}, []); // Runs once on mount
```

```jsx
// PROBLEM 2 — object/array in dependency array
useEffect(() => {
  fetchData(filters);
}, [filters]); // If filters is { status: "active" } created in render, it is a new object every time

// FIX — use specific values, not the object
useEffect(() => {
  fetchData(filters);
}, [filters.status, filters.sort]); // Compare primitives, not objects
```

```jsx
// PROBLEM 3 — setting state that triggers re-render, which triggers the effect
function Component({ userId }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const fetchedUser = getUser(userId);
    setUser(fetchedUser); // State update → re-render → effect runs again?
  }, [user]); // user is in the dependency array!

  // FIX — depend on userId, not user
  useEffect(() => {
    const fetchedUser = getUser(userId);
    setUser(fetchedUser);
  }, [userId]);
}
```

**Debugging approach:**

1. Check the dependency array — is it missing? Does it contain objects or arrays?
2. Add `console.log("Effect running")` inside the effect
3. Check if the effect sets state that causes a re-render that triggers the same effect
4. Use the React DevTools Components tab to watch state cycling

### Problem 3: Stale Closures

**Symptom:** A function uses an old value of state or props instead of the current one.

```jsx
// PROBLEM — stale closure in setTimeout
function Counter() {
  const [count, setCount] = useState(0);

  function handleClick() {
    setTimeout(() => {
      // This captures the count value at the time handleClick was called
      alert(`Count is: ${count}`); // Always shows the old value
    }, 3000);
  }

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount((c) => c + 1)}>Increment</button>
      <button onClick={handleClick}>Show count in 3s</button>
    </div>
  );
}
```

If you click increment three times then click "Show count in 3s," the alert shows 0, not 3. The `handleClick` function closed over the `count` value at the time it was created.

**Fix 1 — Use a ref for the current value:**

```jsx
function Counter() {
  const [count, setCount] = useState(0);
  const countRef = useRef(count);
  countRef.current = count; // Always up to date

  function handleClick() {
    setTimeout(() => {
      alert(`Count is: ${countRef.current}`); // Reads the latest value
    }, 3000);
  }
  // ...
}
```

**Fix 2 — Use the functional updater to read current state:**

```jsx
function handleClick() {
  setTimeout(() => {
    setCount((currentCount) => {
      alert(`Count is: ${currentCount}`);
      return currentCount; // Do not change state
    });
  }, 3000);
}
```

**Debugging approach:**

1. If a value seems "stuck" at an old value, suspect a stale closure
2. Check if the function using the value is created inside a callback, setTimeout, or event handler
3. Check if the function is memoized with useCallback but the dependencies are missing
4. Use a ref to verify what the current value actually is

### Problem 4: State Updates Not Appearing

**Symptom:** You call `setState` but the UI does not update.

**Cause 1: Mutating state instead of creating a new value**

```jsx
// PROBLEM — mutation, not an update
function addItem(item) {
  items.push(item); // Mutates the existing array
  setItems(items);  // Same reference — React sees no change
}

// FIX — create a new array
function addItem(item) {
  setItems((prev) => [...prev, item]);
}
```

```jsx
// PROBLEM — mutating nested object
function updateAddress(newCity) {
  user.address.city = newCity; // Mutates the existing object
  setUser(user);              // Same reference — React sees no change
}

// FIX — create new objects at every level
function updateAddress(newCity) {
  setUser((prev) => ({
    ...prev,
    address: { ...prev.address, city: newCity },
  }));
}
```

**Cause 2: Setting state to the same value**

```jsx
// React skips re-render if the new value === the old value
setCount(5); // If count is already 5, nothing happens
setName("Alice"); // If name is already "Alice", nothing happens
```

**Cause 3: State update in wrong scope**

```jsx
// PROBLEM — local variable, not state
function handleClick() {
  let count = 0; // This is a local variable, not React state
  count += 1;    // Changes the local variable — React does not know
}

// FIX — use state
const [count, setCount] = useState(0);
function handleClick() {
  setCount((c) => c + 1);
}
```

**Debugging approach:**

1. Add `console.log` before and after the `setState` call
2. Log the value you are setting — is it different from the current value?
3. Check if you are mutating instead of creating new objects
4. Use React DevTools to verify the component's state value

### Problem 5: Event Handler Not Firing

**Symptom:** Clicking a button or submitting a form does nothing.

**Common causes:**

```jsx
// PROBLEM 1 — calling the function instead of passing it
<button onClick={handleClick()}>Click</button>
//                            ^^ This CALLS the function during render

// FIX — pass the function reference
<button onClick={handleClick}>Click</button>
```

```jsx
// PROBLEM 2 — event propagation stopped by a parent
<div onClick={parentHandler}>
  <button onClick={(e) => {
    e.stopPropagation(); // This prevents parentHandler from firing
    childHandler();
  }}>Click</button>
</div>
```

```jsx
// PROBLEM 3 — form default behavior
<form onSubmit={handleSubmit}> // Page refreshes before handleSubmit runs
  <button type="submit">Submit</button>
</form>

// FIX — prevent default
function handleSubmit(e) {
  e.preventDefault();
  // ...
}
```

```jsx
// PROBLEM 4 — disabled element
<button onClick={handleClick} disabled>Click</button>
// disabled elements do not fire click events
```

### Problem 6: Data Not Displaying After API Call

**Symptom:** The API call succeeds (visible in Network tab) but the data does not appear.

**Debugging checklist:**

```jsx
useEffect(() => {
  async function fetchData() {
    const response = await fetch("/api/data");
    const data = await response.json();

    console.log("API response:", data); // Step 1: Is data what you expect?
    console.log("Type:", typeof data);  // Step 2: Is it the right type?
    console.log("Is array?", Array.isArray(data)); // Step 3: Is it an array?

    setItems(data); // Step 4: Are you setting state correctly?
    // Maybe the API returns { results: [...] } and you need setItems(data.results)
  }

  fetchData();
}, []);
```

**Common API response structure mismatches:**

```jsx
// API returns: { data: { users: [...] } }
// You expect: [...]

// WRONG
const response = await fetch("/api/users");
const users = await response.json();
setUsers(users); // users is { data: { users: [...] } }, not an array

// CORRECT
const response = await fetch("/api/users");
const json = await response.json();
setUsers(json.data.users); // Extract the array
```

---

## Reading React Error Messages

React provides detailed error messages in development. Learning to read them speeds up debugging significantly.

### "Cannot read properties of undefined/null"

```
TypeError: Cannot read properties of undefined (reading 'name')
```

**What it means:** You are trying to access `.name` on a value that is `undefined` or `null`.

**Common scenarios:**

```jsx
// user is null before the API call completes
return <h2>{user.name}</h2>;

// FIX — guard against null
if (!user) return <p>Loading...</p>;
return <h2>{user.name}</h2>;

// Or use optional chaining
return <h2>{user?.name}</h2>;
```

### "Too many re-renders"

```
Error: Too many re-renders. React limits the number of renders to prevent an infinite loop.
```

**What it means:** Something is causing an infinite render loop — usually setting state during render.

```jsx
// PROBLEM — calling setState during render
function Component() {
  const [count, setCount] = useState(0);
  setCount(count + 1); // This triggers a re-render, which calls setCount again

  // FIX — move state updates to effects or event handlers
  useEffect(() => {
    setCount((c) => c + 1);
  }, []); // Runs once, not on every render
}
```

```jsx
// PROBLEM — calling function instead of passing reference
<button onClick={handleClick()}>Click</button>
//                            ^^ Calls immediately, sets state, triggers re-render

// FIX
<button onClick={handleClick}>Click</button>
```

### "Each child in a list should have a unique key prop"

```
Warning: Each child in a list should have a unique "key" prop.
```

**What it means:** You are rendering a list without providing `key` props, or the keys are not unique.

```jsx
// PROBLEM — no keys
{items.map((item) => <li>{item.name}</li>)}

// FIX — add unique keys
{items.map((item) => <li key={item.id}>{item.name}</li>)}

// PROBLEM — using index as key (bad for dynamic lists)
{items.map((item, index) => <li key={index}>{item.name}</li>)}
// Use index only when: the list is static, never reordered, and items are never added/removed
```

### "Cannot update a component while rendering a different component"

```
Warning: Cannot update a component (`Parent`) while rendering a different component (`Child`).
```

**What it means:** A child component is calling the parent's setState during its render.

```jsx
// PROBLEM
function Child({ onReady }) {
  onReady(); // This calls parent's setState during Child's render
  return <div>Ready</div>;
}

// FIX — move to an effect
function Child({ onReady }) {
  useEffect(() => {
    onReady();
  }, [onReady]);
  return <div>Ready</div>;
}
```

### "React Hook useEffect has a missing dependency"

```
React Hook useEffect has a missing dependency: 'fetchData'. Either include it or remove the dependency array.
```

**What it means:** The effect uses a variable that is not in its dependency array. If the variable changes, the effect will not re-run with the new value.

```jsx
// WARNING
useEffect(() => {
  fetchData(userId); // userId is used but not in deps
}, []); // Missing userId

// FIX — include the dependency
useEffect(() => {
  fetchData(userId);
}, [userId]);
```

This warning is almost always correct. Do not suppress it with `// eslint-disable-next-line` unless you have a very specific reason and understand the consequences.

---

## Systematic Debugging Strategy

When you encounter a bug, follow this systematic approach:

### Step 1: Reproduce the Bug

Make the bug happen consistently. Note the exact steps:

1. What page are you on?
2. What did you click/type?
3. What data was on screen?
4. What happened vs what should have happened?

### Step 2: Check the Console

Open the browser console and look for:

- Red error messages (JavaScript errors)
- Yellow warnings (React warnings)
- Network errors (failed API calls)

### Step 3: Isolate the Component

Use React DevTools to find the component where the bug occurs:

- Is the component receiving the right props?
- Is the component's state what you expect?
- Are the hook values correct?

### Step 4: Add Strategic Logging

Add `console.log` at key points to trace execution:

```jsx
function BuggyComponent({ userId }) {
  console.log("1. Render with userId:", userId);

  const [user, setUser] = useState(null);
  console.log("2. Current user state:", user);

  useEffect(() => {
    console.log("3. Effect running for userId:", userId);

    async function load() {
      const data = await fetchUser(userId);
      console.log("4. API returned:", data);
      setUser(data);
    }

    load();
  }, [userId]);

  console.log("5. About to render, user:", user);

  if (!user) return <p>Loading...</p>;
  return <h2>{user.name}</h2>;
}
```

Read the numbered logs in order. At which point does the actual behavior diverge from what you expect?

### Step 5: Use Breakpoints for Complex Issues

For issues where logging is not enough:

1. Set a breakpoint at the suspicious line
2. Inspect all variables in the Scope panel
3. Step through line by line
4. Watch how values change at each step

### Step 6: Check the Network Tab

For data-related bugs:

1. Is the request being made?
2. Is the URL correct?
3. Is the request payload correct?
4. What is the response status?
5. What data does the response contain?
6. Does the response structure match what the code expects?

### Step 7: Test Your Fix

After fixing the bug:

1. Verify the fix resolves the original issue
2. Test related functionality — did the fix break anything?
3. Test edge cases — empty data, errors, rapid clicks
4. Remove all debugging console.log statements
5. Write a test that catches this bug so it does not happen again

---

## Debugging Performance Issues

### Identifying Slow Renders

```jsx
// Quick way to measure render time
function ExpensiveComponent({ data }) {
  console.time("ExpensiveComponent render");

  // ... rendering logic

  const result = <div>{/* ... */}</div>;

  console.timeEnd("ExpensiveComponent render");
  return result;
}
```

### React Profiler API

For more detailed performance data, use the built-in `<Profiler>` component:

```jsx
import { Profiler } from "react";

function onRenderCallback(id, phase, actualDuration, baseDuration, startTime, commitTime) {
  console.log(`${id} [${phase}]: ${actualDuration.toFixed(2)}ms`);
}

function App() {
  return (
    <Profiler id="Dashboard" onRender={onRenderCallback}>
      <Dashboard />
    </Profiler>
  );
}
```

The callback provides:

- `id` — The Profiler's identifier
- `phase` — "mount" or "update"
- `actualDuration` — Time spent rendering (in ms)
- `baseDuration` — Estimated time to render the entire subtree without memoization
- `startTime` and `commitTime` — Timestamps

### Common Performance Fixes

| Problem | Detection | Fix |
|---------|-----------|-----|
| Component re-renders unnecessarily | Profiler shows "parent rendered" | `React.memo` |
| Expensive calculation runs on every render | `console.time` shows slow renders | `useMemo` |
| New callback function triggers child re-render | Profiler shows "props changed" | `useCallback` |
| Huge list renders all items | Scroll is janky | Virtualization (react-window) |
| Large bundle, slow initial load | Network tab shows large JS files | `React.lazy` + code splitting |

---

## Debugging Tools Summary

| Tool | Best For |
|------|----------|
| **React DevTools — Components** | Inspecting props, state, hooks, component tree |
| **React DevTools — Profiler** | Finding unnecessary re-renders, measuring render times |
| **Console** | Quick logging, counting renders, timing operations |
| **Sources tab (breakpoints)** | Stepping through code, inspecting variables |
| **Network tab** | Debugging API calls, checking request/response data |
| **Elements tab** | Inspecting the actual DOM output, CSS issues |
| **`console.count`** | Counting how many times something executes |
| **`console.table`** | Viewing arrays/objects in a readable format |
| **`console.trace`** | Finding who called a function |
| **`debugger`** | Quick breakpoint without opening Sources tab |

---

## Mini Project: Debugging Challenge

Here is a component with several bugs. Let us walk through finding and fixing each one.

```jsx
// BuggyTodoApp.jsx — BEFORE (contains bugs)
import { useState, useEffect } from "react";

function BuggyTodoApp() {
  const [todos, setTodos] = useState([]);
  const [input, setInput] = useState("");
  const [filter, setFilter] = useState("all");
  const [editingId, setEditingId] = useState(null);
  const [editText, setEditText] = useState("");

  // BUG 1: Infinite loop — no dependency array
  useEffect(() => {
    const saved = localStorage.getItem("todos");
    if (saved) {
      setTodos(JSON.parse(saved));
    }
  });

  // BUG 2: Saves to localStorage on every render, not when todos change
  localStorage.setItem("todos", JSON.stringify(todos));

  function addTodo() {
    // BUG 3: No input validation — empty todos can be added
    const newTodo = {
      id: Date.now(),
      text: input,
      completed: false,
    };
    // BUG 4: Mutation — pushing to existing array
    todos.push(newTodo);
    setTodos(todos);
    setInput("");
  }

  function toggleTodo(id) {
    // BUG 5: Mutation — modifying the todo object directly
    const todo = todos.find((t) => t.id === id);
    todo.completed = !todo.completed;
    setTodos(todos);
  }

  function deleteTodo(id) {
    setTodos(todos.filter((t) => t.id !== id));
  }

  function startEdit(todo) {
    setEditingId(todo.id);
    setEditText(todo.text);
  }

  function saveEdit(id) {
    // BUG 6: Mutation — modifying todo directly
    const todo = todos.find((t) => t.id === id);
    todo.text = editText;
    setTodos(todos);
    setEditingId(null);
  }

  // BUG 7: Filter creates new array on every render (minor perf issue)
  const filteredTodos = todos.filter((todo) => {
    if (filter === "active") return !todo.completed;
    if (filter === "completed") return todo.completed;
    return true;
  });

  return (
    <div>
      <h1>Todo App</h1>

      <form
        onSubmit={(e) => {
          // BUG 8: Missing preventDefault — page refreshes
          addTodo();
        }}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Add a todo..."
        />
        <button type="submit">Add</button>
      </form>

      <div>
        {/* BUG 9: onClick calls function instead of passing reference */}
        <button onClick={setFilter("all")}>All</button>
        <button onClick={setFilter("active")}>Active</button>
        <button onClick={setFilter("completed")}>Completed</button>
      </div>

      <ul>
        {filteredTodos.map((todo) => (
          <li key={todo.id}>
            {editingId === todo.id ? (
              <span>
                <input
                  value={editText}
                  onChange={(e) => setEditText(e.target.value)}
                />
                <button onClick={() => saveEdit(todo.id)}>Save</button>
              </span>
            ) : (
              <span>
                <input
                  type="checkbox"
                  checked={todo.completed}
                  onChange={() => toggleTodo(todo.id)}
                />
                <span>{todo.text}</span>
                <button onClick={() => startEdit(todo)}>Edit</button>
                <button onClick={() => deleteTodo(todo.id)}>Delete</button>
              </span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### The Fixes

```jsx
// FixedTodoApp.jsx — AFTER (all bugs fixed)
import { useState, useEffect, useMemo } from "react";

function FixedTodoApp() {
  const [todos, setTodos] = useState(() => {
    // FIX 1: Load from localStorage in initializer (runs once)
    const saved = localStorage.getItem("todos");
    return saved ? JSON.parse(saved) : [];
  });
  const [input, setInput] = useState("");
  const [filter, setFilter] = useState("all");
  const [editingId, setEditingId] = useState(null);
  const [editText, setEditText] = useState("");

  // FIX 2: Save to localStorage in an effect, when todos change
  useEffect(() => {
    localStorage.setItem("todos", JSON.stringify(todos));
  }, [todos]);

  function addTodo() {
    // FIX 3: Validate input
    if (!input.trim()) return;

    const newTodo = {
      id: Date.now(),
      text: input.trim(),
      completed: false,
    };

    // FIX 4: Create new array instead of mutating
    setTodos((prev) => [...prev, newTodo]);
    setInput("");
  }

  function toggleTodo(id) {
    // FIX 5: Create new array and new todo object
    setTodos((prev) =>
      prev.map((t) => (t.id === id ? { ...t, completed: !t.completed } : t))
    );
  }

  function deleteTodo(id) {
    setTodos((prev) => prev.filter((t) => t.id !== id));
  }

  function startEdit(todo) {
    setEditingId(todo.id);
    setEditText(todo.text);
  }

  function saveEdit(id) {
    // FIX 6: Create new array and new todo object
    if (!editText.trim()) return;
    setTodos((prev) =>
      prev.map((t) => (t.id === id ? { ...t, text: editText.trim() } : t))
    );
    setEditingId(null);
  }

  // FIX 7: Memoize filtered todos
  const filteredTodos = useMemo(() => {
    return todos.filter((todo) => {
      if (filter === "active") return !todo.completed;
      if (filter === "completed") return todo.completed;
      return true;
    });
  }, [todos, filter]);

  return (
    <div>
      <h1>Todo App</h1>

      {/* FIX 8: Add preventDefault */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          addTodo();
        }}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Add a todo..."
        />
        <button type="submit">Add</button>
      </form>

      <div>
        {/* FIX 9: Pass function references, not function calls */}
        <button onClick={() => setFilter("all")}>All</button>
        <button onClick={() => setFilter("active")}>Active</button>
        <button onClick={() => setFilter("completed")}>Completed</button>
      </div>

      <ul>
        {filteredTodos.map((todo) => (
          <li key={todo.id}>
            {editingId === todo.id ? (
              <span>
                <input
                  value={editText}
                  onChange={(e) => setEditText(e.target.value)}
                />
                <button onClick={() => saveEdit(todo.id)}>Save</button>
              </span>
            ) : (
              <span>
                <input
                  type="checkbox"
                  checked={todo.completed}
                  onChange={() => toggleTodo(todo.id)}
                />
                <span>{todo.text}</span>
                <button onClick={() => startEdit(todo)}>Edit</button>
                <button onClick={() => deleteTodo(todo.id)}>Delete</button>
              </span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

**Summary of bugs found and fixed:**

| # | Bug | Root Cause | Fix |
|---|-----|-----------|-----|
| 1 | Infinite loop | useEffect without dependency array | Use useState initializer for one-time load |
| 2 | Side effect in render | localStorage.setItem called during render | Move to useEffect with [todos] dependency |
| 3 | Empty todos added | No input validation | Guard with `if (!input.trim()) return` |
| 4 | State not updating | Array mutation with push | Spread into new array: `[...prev, newTodo]` |
| 5 | Toggle not updating | Object mutation | Map to new array with spread: `{ ...t, completed: !t.completed }` |
| 6 | Edit not updating | Object mutation | Map to new array with spread: `{ ...t, text: editText }` |
| 7 | Unnecessary recalculation | Filter runs on every render | Memoize with useMemo |
| 8 | Page refreshes on submit | Missing preventDefault | Add `e.preventDefault()` |
| 9 | Crashes on render | Calling setState directly in onClick | Wrap in arrow function: `() => setFilter("all")` |

---

## Common Mistakes

### Mistake 1: Leaving console.log in Production Code

```jsx
// Development debugging — fine
console.log("User data:", user);

// But remove before committing!
// Use a linter rule: no-console
```

### Mistake 2: Ignoring React Warnings

React warnings (yellow in the console) are almost always real problems:

- Missing keys in lists → bugs when items are reordered
- Missing effect dependencies → stale data
- Updating state during render → infinite loops

Treat warnings as errors. Fix them immediately.

### Mistake 3: Not Checking the Network Tab

Many "bugs" are actually API issues:

- The endpoint URL has a typo
- The server returns an error
- The response structure changed
- The request is missing authentication

Always check the Network tab before debugging component code.

### Mistake 4: Not Reproducing Before Fixing

"I think I know what the problem is" → changes code → creates new bug

Always reproduce the bug first. Understand exactly what is happening before changing code.

---

## Best Practices

1. **Reproduce first, then debug** — If you cannot make the bug happen consistently, you cannot verify your fix works.

2. **Use React DevTools before console.log** — The Components tab shows props, state, and hooks instantly. The Profiler shows render behavior. These are faster than adding and removing log statements.

3. **Read error messages carefully** — React's error messages in development mode are detailed and usually point directly to the problem. Read the full message, including the component stack.

4. **Fix warnings immediately** — React warnings indicate real issues that will cause bugs eventually. Do not accumulate them.

5. **Remove debugging code** — `console.log`, `debugger`, and `console.count` statements should never reach production. Configure your linter to warn about them.

6. **Use the Network tab for data issues** — When data is wrong, check the API response before debugging component logic. The bug might be on the server.

7. **Add a test after fixing** — Every bug you fix is a test you should write. The test ensures the bug does not return.

8. **Check state immutability** — If the UI is not updating after a state change, the most common cause is mutating state instead of creating new objects/arrays.

---

## Summary

In this chapter, you learned:

- **React DevTools Components tab** lets you inspect the component tree, props, state, hooks, and edit values live
- **React DevTools Profiler** records rendering activity, shows render times, and explains why each component rendered
- **Browser Console** goes beyond `console.log` — use `console.table`, `console.count`, `console.time`, `console.trace`, and `console.group` for structured debugging
- **Breakpoints** (in Sources tab or via `debugger`) let you pause execution and step through code line by line
- **Common React bugs** include infinite effect loops (missing deps), stale closures (old values in callbacks), state mutation (push/direct assignment), and calling functions instead of passing references
- **React error messages** are descriptive in development — read them carefully, including the component stack
- **The debugging process** is systematic: reproduce → isolate → understand → fix → verify
- **Performance debugging** uses the Profiler, `console.time`, and the `<Profiler>` component to identify slow renders and unnecessary re-renders

---

## Interview Questions

1. **How would you debug a component that re-renders too many times?**

   First, use `console.count` in the component to confirm the excessive renders. Then use React DevTools Profiler with "Record why each component rendered" enabled. Record while reproducing the issue and examine each render's cause. Common causes: parent rendering (fix with React.memo), new prop references on every render (fix with useMemo/useCallback), or state updates in effects that trigger re-renders. The Highlight Updates feature in React DevTools settings also visually shows which components re-render.

2. **What causes a useEffect infinite loop and how do you fix it?**

   An infinite loop occurs when an effect triggers a state update that causes a re-render that triggers the same effect again. Common causes: missing dependency array (effect runs on every render), setting state that is in the dependency array, or including objects/arrays in the dependency array that are recreated on every render. Fix by adding the correct dependency array, using primitive values instead of objects as dependencies, or restructuring to avoid the cycle.

3. **What is a stale closure in React and how do you identify it?**

   A stale closure occurs when a function captures a variable's value at creation time and does not see subsequent updates. This happens with setTimeout, setInterval, event listeners, and memoized callbacks. Symptoms: a value appears "stuck" at an old value. Identify by logging the value inside the closure vs outside it. Fix with a ref (`useRef` that is updated each render), the functional form of setState, or by adding the value to the callback's dependency array.

4. **How do you debug an API call that appears to succeed but the data does not display?**

   Check the Network tab to verify the request was made, the status is 200, and the response body contains the expected data. Then `console.log` the parsed response in the component to see what JavaScript receives. Common issues: the response structure does not match expectations (e.g., data is nested in a `results` property), the state setter is called with the wrong value, or a race condition overwrites the data. Check that `response.ok` is verified and the correct property is being set in state.

5. **What is the systematic approach to debugging a React application?**

   Follow this process: (1) Reproduce the bug consistently and note the exact steps. (2) Check the browser console for errors and warnings. (3) Use React DevTools to inspect the component's props, state, and hooks. (4) Add strategic logging at key points in the data flow. (5) Use breakpoints for complex logic. (6) Check the Network tab for API-related issues. (7) Once the root cause is understood, fix it. (8) Verify the fix and test edge cases. (9) Write a test to prevent regression.

---

## Practice Exercises

### Exercise 1: Find the Bugs

Create a buggy shopping cart component with at least 5 intentional bugs (state mutation, missing keys, infinite effects, stale closure, missing preventDefault). Give it to a teammate (or revisit it after a day) and practice finding and fixing each bug using React DevTools and the systematic debugging process.

### Exercise 2: Performance Investigation

Build a large list component (1000+ items) with a search filter input. Profile it with React DevTools and identify performance bottlenecks. Apply optimizations (React.memo, useMemo, virtualization) and measure the improvement using the Profiler.

### Exercise 3: API Debugging

Build a component that fetches data from a public API (e.g., JSONPlaceholder). Intentionally introduce API-related bugs: wrong URL, not checking response.ok, accessing the wrong property on the response, and a race condition. Practice using the Network tab and console to find and fix each issue.

### Exercise 4: Debugging Log

For your next real project, keep a debugging log. For each bug you encounter, write down: (1) the symptom, (2) the debugging steps you took, (3) the root cause, (4) the fix. After 10 entries, review the log for patterns — which bugs occur most often? What debugging techniques were most effective?

---

## What Is Next?

In Chapter 23, we will explore **Authentication Flow and Protected Routes** — building a complete authentication system with login, registration, token management, protected routes, and role-based access control in a React application.
