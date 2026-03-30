# Chapter 5: State and the useState Hook

---

## Learning Goals

By the end of this chapter, you will be able to:

- Explain what state is and why it is needed
- Understand the difference between props and state
- Use the `useState` hook to add state to functional components
- Update state correctly using direct values and updater functions
- Manage different types of state: strings, numbers, booleans, arrays, and objects
- Avoid common state mutation mistakes
- Handle multiple state variables in a single component
- Understand why state updates are asynchronous (batched)
- Build interactive components that respond to user actions
- Apply best practices for organizing and managing state

---

## What Is State?

In previous chapters, we built components that display data. That data was either hardcoded inside the component or passed in as props. But in both cases, the data never changed — it was static. Real applications are not static. Users click buttons, type into forms, toggle settings, add items to carts, and navigate between pages. The data on screen needs to change in response to these actions.

**State** is data that belongs to a component and can change over time. When state changes, React automatically re-renders the component to reflect the new data on screen.

Think of it like this:

- **Props** are like the arguments you pass to a function — the caller decides them, and the function cannot change them.
- **State** is like a local variable inside a function — the function owns it and can change it.

### A Real-Life Analogy

Imagine a light switch on your wall. The switch has state — it is either **on** or **off**. When you flip the switch, the state changes. When the state changes, the light responds by turning on or off. You do not need to manually tell the light bulb to change — it reacts to the state change automatically.

React works the same way. When you update state, React automatically re-renders the component to show the new state. You never have to manually update the DOM — React handles it for you.

```
User Action  →  State Change  →  Re-render  →  Updated UI

[Click]      →  count: 0→1   →  React runs  →  Screen shows
                                 component      new count
                                 function
                                 again
```

### Why Not Just Use Regular Variables?

You might wonder why we need a special mechanism for state. Why not just use a regular JavaScript variable?

```jsx
// ❌ This does NOT work
function Counter() {
  let count = 0;

  function handleClick() {
    count = count + 1;
    console.log(count); // This increases, but...
  }

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={handleClick}>Add 1</button>
    </div>
  );
}
```

If you run this code, clicking the button does nothing on screen. The console shows the count increasing, but the displayed number stays at 0. Why?

Two reasons:

1. **React does not know the variable changed.** Regular variables do not trigger a re-render. React has no way to detect that `count` was updated, so it does not update the screen.

2. **The variable resets on every render.** Even if React did re-render, the function runs from top to bottom again, and `let count = 0` would reset the count back to 0.

This is the problem that `useState` solves. It gives you:
- A value that **persists** between renders (does not reset).
- A function that **tells React** to re-render when the value changes.

---

## The useState Hook

`useState` is a function provided by React that lets you add state to a component. It is called a **hook** — a special function that "hooks into" React's internal features. We will learn about more hooks in later chapters, but `useState` is the most fundamental one.

### Basic Syntax

```jsx
import { useState } from "react";

function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Add 1</button>
    </div>
  );
}
```

Let us break this down piece by piece.

### Step 1: Import useState

```jsx
import { useState } from "react";
```

`useState` is a named export from the `react` package. You must import it before using it.

### Step 2: Call useState

```jsx
const [count, setCount] = useState(0);
```

This single line does several things:

1. **`useState(0)`** — Calls the `useState` function with an initial value of `0`. This initial value is only used during the first render. On subsequent renders, React uses the current state value instead.

2. **Returns an array** — `useState` returns an array with exactly two items:
   - The **current state value** (what the state is right now)
   - A **setter function** (a function to update the state)

3. **Array destructuring** — We use JavaScript array destructuring to assign names to these two items:
   - `count` — the current value (starts at `0`)
   - `setCount` — the function to update it

### Understanding Array Destructuring

If you are not familiar with array destructuring, here is what is happening:

```javascript
// Without destructuring:
const stateArray = useState(0);
const count = stateArray[0];      // the current value
const setCount = stateArray[1];   // the setter function

// With destructuring (same thing, cleaner):
const [count, setCount] = useState(0);
```

You can name these variables anything you want, but the convention is:

```
const [thing, setThing] = useState(initialValue);
```

Examples:
```jsx
const [name, setName] = useState("");
const [isVisible, setIsVisible] = useState(false);
const [items, setItems] = useState([]);
const [user, setUser] = useState(null);
const [selectedColor, setSelectedColor] = useState("blue");
```

### Step 3: Use the State Value

```jsx
<p>Count: {count}</p>
```

Use the state variable just like any other variable in your JSX. When the state changes, React re-renders the component, and `count` will have the new value.

### Step 4: Update the State

```jsx
<button onClick={() => setCount(count + 1)}>Add 1</button>
```

When the button is clicked, `setCount(count + 1)` is called. This does two things:
1. Updates the state value to `count + 1`.
2. Tells React to re-render the component.

On the next render, `count` will have the new value, and the UI will update to show it.

### The Full Flow

Let us trace exactly what happens when a user clicks the button:

```
Initial render:
1. React calls Counter()
2. useState(0) returns [0, setCount]
3. count = 0
4. React renders: <p>Count: 0</p> <button>Add 1</button>

User clicks the button:
5. onClick fires → setCount(0 + 1) is called
6. React schedules a re-render

Re-render:
7. React calls Counter() again
8. useState(0) → React ignores the 0, returns [1, setCount]
9. count = 1
10. React renders: <p>Count: 1</p> <button>Add 1</button>
11. React compares old and new output, updates only what changed
    (the text inside <p> changes from "0" to "1")

User clicks again:
12. onClick fires → setCount(1 + 1) is called
13. React schedules a re-render

Re-render:
14. React calls Counter() again
15. useState(0) → React ignores the 0, returns [2, setCount]
16. count = 2
17. React renders: <p>Count: 2</p> <button>Add 1</button>
```

**Key insight:** The entire function body runs again on every render. But `useState` remembers the current state value between renders. The initial value (`0` in this case) is only used on the very first render.

---

## Building a Complete Counter

Let us build a more feature-rich counter to practice:

```jsx
import { useState } from "react";

function Counter() {
  const [count, setCount] = useState(0);

  function increment() {
    setCount(count + 1);
  }

  function decrement() {
    setCount(count - 1);
  }

  function reset() {
    setCount(0);
  }

  return (
    <div style={{ textAlign: "center", padding: "2rem" }}>
      <h1>Counter</h1>
      <p style={{ fontSize: "3rem", margin: "1rem 0" }}>{count}</p>
      <div style={{ display: "flex", gap: "0.5rem", justifyContent: "center" }}>
        <button onClick={decrement}>- 1</button>
        <button onClick={reset}>Reset</button>
        <button onClick={increment}>+ 1</button>
      </div>
      {count < 0 && (
        <p style={{ color: "red", marginTop: "1rem" }}>
          Count is negative!
        </p>
      )}
    </div>
  );
}

export default Counter;
```

**What this code does:**

1. `count` starts at `0`.
2. Three functions update the state: `increment` adds 1, `decrement` subtracts 1, `reset` sets it back to 0.
3. The count is displayed in large text.
4. Three buttons trigger the respective functions.
5. A warning message appears when the count goes below zero, using conditional rendering with `&&`.

**Why the handler functions are defined separately:** Instead of writing `onClick={() => setCount(count + 1)}` inline, we defined named functions (`increment`, `decrement`, `reset`). This is a matter of readability — named functions make it clear what each button does. Both approaches work; use whichever is clearer for your situation.

---

## State with Different Data Types

State can hold any JavaScript value — numbers, strings, booleans, arrays, objects, or `null`. Let us look at each type.

### String State

```jsx
import { useState } from "react";

function NameInput() {
  const [name, setName] = useState("");

  return (
    <div>
      <label htmlFor="name">Your name: </label>
      <input
        id="name"
        type="text"
        value={name}
        onChange={(event) => setName(event.target.value)}
      />
      <p>Hello, {name || "stranger"}!</p>
      <p>Name length: {name.length} characters</p>
    </div>
  );
}
```

**What this code does:**

1. `name` starts as an empty string `""`.
2. The `<input>` element has two important attributes:
   - `value={name}` — the input displays whatever is in the `name` state (this is called a **controlled input**, which we will cover in Chapter 8).
   - `onChange={(event) => setName(event.target.value)}` — when the user types, the `onChange` event fires. `event.target.value` is the current text in the input. We update the state to match.
3. The greeting uses `name || "stranger"` — if `name` is empty (falsy), it shows "stranger" instead.
4. `name.length` shows the character count, updating in real time as the user types.

### Boolean State

```jsx
import { useState } from "react";

function ToggleSwitch() {
  const [isOn, setIsOn] = useState(false);

  function toggle() {
    setIsOn(!isOn);
  }

  return (
    <div>
      <p>The switch is {isOn ? "ON" : "OFF"}</p>
      <button
        onClick={toggle}
        style={{
          backgroundColor: isOn ? "#38a169" : "#e53e3e",
          color: "white",
          border: "none",
          padding: "0.5rem 1rem",
          borderRadius: "4px",
          cursor: "pointer",
        }}
      >
        {isOn ? "Turn OFF" : "Turn ON"}
      </button>
    </div>
  );
}
```

**What this code does:**

1. `isOn` starts as `false`.
2. `toggle` flips the value: `!isOn` turns `true` to `false` and `false` to `true`.
3. The button text, color, and status text all change based on the current state.

**Why use `!isOn` instead of setting a specific value:** Using the logical NOT operator (`!`) is the standard way to toggle a boolean. It always flips the current value, regardless of what it is. You could also write `setIsOn(false)` or `setIsOn(true)` if you need to set a specific value rather than toggle.

### Number State (Temperature Converter)

```jsx
import { useState } from "react";

function TemperatureConverter() {
  const [celsius, setCelsius] = useState(0);

  const fahrenheit = (celsius * 9) / 5 + 32;
  const kelvin = celsius + 273.15;

  return (
    <div>
      <h2>Temperature Converter</h2>
      <div>
        <label htmlFor="celsius">Celsius: </label>
        <input
          id="celsius"
          type="number"
          value={celsius}
          onChange={(event) => setCelsius(Number(event.target.value))}
        />
      </div>
      <p>Fahrenheit: {fahrenheit.toFixed(1)}°F</p>
      <p>Kelvin: {kelvin.toFixed(1)}K</p>
      <p>
        {celsius > 30
          ? "It's hot! 🔥"
          : celsius < 0
          ? "It's freezing! 🥶"
          : "Nice weather! 😊"}
      </p>
    </div>
  );
}
```

**What this code does:**

1. `celsius` holds a number, starting at `0`.
2. `Number(event.target.value)` converts the input string to a number. Input values are always strings in JavaScript, so we convert explicitly.
3. `fahrenheit` and `kelvin` are **derived values** — they are calculated from the state, not stored as separate state. This is an important principle: **do not store values in state that can be computed from other state**.
4. `.toFixed(1)` formats the number to one decimal place.

**Why we do not store `fahrenheit` and `kelvin` as state:** If we used `useState` for all three, we would need to keep them in sync manually — every time celsius changes, we would also need to update fahrenheit and kelvin. That is error-prone. Instead, we compute them from the single source of truth (`celsius`). This principle is called **derived state** and is a key best practice.

---

## Updating State Based on Previous State

There is a subtle but critical issue with how we have been updating state. Consider this code:

```jsx
function Counter() {
  const [count, setCount] = useState(0);

  function addThree() {
    setCount(count + 1);
    setCount(count + 1);
    setCount(count + 1);
  }

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={addThree}>Add 3</button>
    </div>
  );
}
```

You might expect clicking "Add 3" to increase the count by 3. But it only increases by 1. Why?

### The Problem: State Updates Are Batched

When you call `setCount(count + 1)` three times in a row, here is what happens:

```
count is currently 0

setCount(count + 1)  →  setCount(0 + 1)  →  setCount(1)
setCount(count + 1)  →  setCount(0 + 1)  →  setCount(1)
setCount(count + 1)  →  setCount(0 + 1)  →  setCount(1)
```

All three calls use the same `count` value (`0`) because the component has not re-rendered yet. React batches state updates for performance — it does not re-render after each `setCount` call. All three updates happen in the same render cycle, so `count` is `0` for all three.

It is like telling React: "Set count to 1. Set count to 1. Set count to 1." The final result is `1`, not `3`.

### The Solution: Updater Functions

To update state based on the previous state, pass a **function** to the setter instead of a value:

```jsx
function Counter() {
  const [count, setCount] = useState(0);

  function addThree() {
    setCount((prevCount) => prevCount + 1);
    setCount((prevCount) => prevCount + 1);
    setCount((prevCount) => prevCount + 1);
  }

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={addThree}>Add 3</button>
    </div>
  );
}
```

Now it works correctly. Here is what happens:

```
count is currently 0

setCount((prevCount) => prevCount + 1)  →  0 + 1 = 1
setCount((prevCount) => prevCount + 1)  →  1 + 1 = 2
setCount((prevCount) => prevCount + 1)  →  2 + 1 = 3
```

When you pass a function (called an **updater function**), React calls it with the most recent state value as its argument. Each updater function receives the result of the previous one, forming a chain.

### When to Use Updater Functions

The rule is straightforward:

- **Use a direct value** when the new state does NOT depend on the old state:
  ```jsx
  setName("Alice");        // Setting to a specific value
  setIsOpen(false);        // Setting to a specific value
  setCount(0);             // Resetting to initial value
  ```

- **Use an updater function** when the new state IS based on the old state:
  ```jsx
  setCount((prev) => prev + 1);        // Incrementing
  setIsOpen((prev) => !prev);          // Toggling
  setItems((prev) => [...prev, item]); // Adding to array
  ```

Many experienced React developers use updater functions whenever updating based on previous state, even in simple cases, as a defensive coding habit. It is never wrong to use an updater function, but it is sometimes wrong not to.

---

## State with Arrays

Arrays are one of the most common state types. You use them for lists of items: to-do lists, shopping cart items, messages, search results, and more.

The most important rule with array state is: **never mutate the array directly**. Always create a new array.

### Why You Cannot Mutate State

```jsx
// ❌ WRONG: Mutating state directly
function TodoList() {
  const [todos, setTodos] = useState(["Buy milk", "Walk dog"]);

  function addTodo() {
    todos.push("New todo");  // This mutates the existing array
    setTodos(todos);         // React sees the SAME array reference
                             // and may skip the re-render
  }

  return <div>...</div>;
}
```

When you call `todos.push("New todo")`, you modify the existing array. Then when you call `setTodos(todos)`, you pass the same array reference to React. React uses **referential equality** (`===`) to compare the old and new state. Since the reference is the same object, React may think nothing changed and skip the re-render.

**The fix:** Always create a **new** array:

```jsx
// ✅ CORRECT: Creating a new array
function TodoList() {
  const [todos, setTodos] = useState(["Buy milk", "Walk dog"]);

  function addTodo() {
    setTodos([...todos, "New todo"]); // Spread into a new array
  }

  return <div>...</div>;
}
```

The spread operator `...todos` copies all items from the existing array into a new one, and `"New todo"` is added at the end. React sees a new array reference and re-renders.

### Common Array Operations

Here is a reference for all common array operations, showing the immutable approach:

#### Adding Items

```jsx
const [items, setItems] = useState(["A", "B", "C"]);

// Add to the end
setItems([...items, "D"]);
// Result: ["A", "B", "C", "D"]

// Add to the beginning
setItems(["D", ...items]);
// Result: ["D", "A", "B", "C"]

// Add at a specific position (insert "D" at index 2)
setItems([...items.slice(0, 2), "D", ...items.slice(2)]);
// Result: ["A", "B", "D", "C"]
```

#### Removing Items

```jsx
const [items, setItems] = useState(["A", "B", "C", "D"]);

// Remove by index (remove index 1)
setItems(items.filter((_, index) => index !== 1));
// Result: ["A", "C", "D"]

// Remove by value
setItems(items.filter((item) => item !== "B"));
// Result: ["A", "C", "D"]

// Remove by ID (common with objects)
const [users, setUsers] = useState([
  { id: 1, name: "Alice" },
  { id: 2, name: "Bob" },
  { id: 3, name: "Charlie" },
]);
setUsers(users.filter((user) => user.id !== 2));
// Result: [{ id: 1, name: "Alice" }, { id: 3, name: "Charlie" }]
```

#### Updating Items

```jsx
const [items, setItems] = useState(["A", "B", "C"]);

// Update by index (change index 1 to "X")
setItems(items.map((item, index) => (index === 1 ? "X" : item)));
// Result: ["A", "X", "C"]

// Update by ID (common with objects)
const [users, setUsers] = useState([
  { id: 1, name: "Alice", active: true },
  { id: 2, name: "Bob", active: false },
]);
setUsers(
  users.map((user) =>
    user.id === 2 ? { ...user, active: true } : user
  )
);
// Result: [{ id: 1, ..., active: true }, { id: 2, ..., active: true }]
```

#### Sorting and Reversing

```jsx
const [numbers, setNumbers] = useState([3, 1, 4, 1, 5]);

// Sort (create a copy first!)
setNumbers([...numbers].sort((a, b) => a - b));
// Result: [1, 1, 3, 4, 5]

// Reverse (create a copy first!)
setNumbers([...numbers].reverse());
// Result: [5, 1, 4, 1, 3]
```

**Why we spread before sorting:** `Array.sort()` and `Array.reverse()` mutate the original array. By spreading into a new array first (`[...numbers]`), we sort/reverse the copy, leaving the original unchanged.

### Practical Example: Todo List

Let us build a real todo list that uses array state:

```jsx
import { useState } from "react";

function TodoApp() {
  const [todos, setTodos] = useState([
    { id: 1, text: "Learn React", completed: false },
    { id: 2, text: "Build a project", completed: false },
  ]);
  const [inputValue, setInputValue] = useState("");

  function addTodo() {
    if (inputValue.trim() === "") return;

    const newTodo = {
      id: Date.now(),
      text: inputValue.trim(),
      completed: false,
    };

    setTodos([...todos, newTodo]);
    setInputValue("");
  }

  function toggleTodo(id) {
    setTodos(
      todos.map((todo) =>
        todo.id === id ? { ...todo, completed: !todo.completed } : todo
      )
    );
  }

  function deleteTodo(id) {
    setTodos(todos.filter((todo) => todo.id !== id));
  }

  const remainingCount = todos.filter((todo) => !todo.completed).length;

  return (
    <div style={{ maxWidth: "400px", margin: "2rem auto" }}>
      <h1>Todo List</h1>

      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
        <input
          type="text"
          value={inputValue}
          onChange={(event) => setInputValue(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") addTodo();
          }}
          placeholder="Add a new todo..."
          style={{ flex: 1, padding: "0.5rem" }}
        />
        <button onClick={addTodo}>Add</button>
      </div>

      <ul style={{ listStyle: "none", padding: 0 }}>
        {todos.map((todo) => (
          <li
            key={todo.id}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
              padding: "0.5rem",
              borderBottom: "1px solid #eee",
            }}
          >
            <input
              type="checkbox"
              checked={todo.completed}
              onChange={() => toggleTodo(todo.id)}
            />
            <span
              style={{
                flex: 1,
                textDecoration: todo.completed ? "line-through" : "none",
                color: todo.completed ? "#999" : "inherit",
              }}
            >
              {todo.text}
            </span>
            <button
              onClick={() => deleteTodo(todo.id)}
              style={{
                backgroundColor: "#e53e3e",
                color: "white",
                border: "none",
                borderRadius: "4px",
                padding: "0.25rem 0.5rem",
                cursor: "pointer",
              }}
            >
              Delete
            </button>
          </li>
        ))}
      </ul>

      <p style={{ color: "#666", marginTop: "1rem" }}>
        {remainingCount} {remainingCount === 1 ? "task" : "tasks"} remaining
      </p>
    </div>
  );
}

export default TodoApp;
```

**What this code does:**

1. **Two state variables**: `todos` (an array of todo objects) and `inputValue` (the text input's value).

2. **`addTodo`**: Creates a new todo object with `Date.now()` as a unique ID, spreads the existing todos, and appends the new one. Then clears the input.

3. **`toggleTodo`**: Uses `map()` to create a new array. For the matching todo, it creates a new object with the `completed` property flipped. All other todos are unchanged.

4. **`deleteTodo`**: Uses `filter()` to create a new array without the deleted todo.

5. **`remainingCount`**: A derived value (not state!) — calculated by filtering for incomplete todos and counting them.

6. **`onKeyDown`**: Lets the user press Enter to add a todo, in addition to clicking the Add button.

7. **Visual feedback**: Completed todos get a line-through style and gray color.

**Why `Date.now()` for IDs:** In a real application, IDs come from a database. For a simple client-side demo, `Date.now()` returns the current timestamp in milliseconds, which is unique enough for our purposes. Do not use this approach in production — use proper UUID libraries or server-generated IDs.

---

## State with Objects

When state is an object, you must follow the same immutability rule: never modify the object directly. Create a new object with the changes.

### Updating Object State

```jsx
import { useState } from "react";

function UserProfile() {
  const [user, setUser] = useState({
    firstName: "Alice",
    lastName: "Johnson",
    age: 28,
    email: "alice@example.com",
  });

  function updateFirstName(newName) {
    setUser({ ...user, firstName: newName });
  }

  function incrementAge() {
    setUser((prev) => ({ ...prev, age: prev.age + 1 }));
  }

  function updateEmail(newEmail) {
    setUser({ ...user, email: newEmail });
  }

  return (
    <div>
      <h2>User Profile</h2>
      <div style={{ marginBottom: "1rem" }}>
        <label>First Name: </label>
        <input
          value={user.firstName}
          onChange={(event) => updateFirstName(event.target.value)}
        />
      </div>
      <div style={{ marginBottom: "1rem" }}>
        <label>Email: </label>
        <input
          value={user.email}
          onChange={(event) => updateEmail(event.target.value)}
        />
      </div>
      <p>
        {user.firstName} {user.lastName}, Age: {user.age}
      </p>
      <button onClick={incrementAge}>Birthday! 🎂</button>
    </div>
  );
}
```

**How `{ ...user, firstName: newName }` works:**

1. `...user` copies all properties from the current user object.
2. `firstName: newName` overrides the `firstName` property with the new value.
3. The result is a new object with the same properties as before, except `firstName` has changed.

```javascript
// If user is { firstName: "Alice", lastName: "Johnson", age: 28, email: "..." }
// and newName is "Bob"

{ ...user, firstName: "Bob" }
// Result: { firstName: "Bob", lastName: "Johnson", age: 28, email: "..." }
```

**Important**: The property being overridden must come AFTER the spread. If you write `{ firstName: "Bob", ...user }`, the spread will overwrite `firstName` back to "Alice".

### Nested Object State

Updating nested objects requires spreading at each level:

```jsx
import { useState } from "react";

function Settings() {
  const [settings, setSettings] = useState({
    theme: "light",
    notifications: {
      email: true,
      push: false,
      sms: true,
    },
    language: "en",
  });

  function toggleEmailNotification() {
    setSettings({
      ...settings,
      notifications: {
        ...settings.notifications,
        email: !settings.notifications.email,
      },
    });
  }

  function changeTheme(newTheme) {
    setSettings({ ...settings, theme: newTheme });
  }

  return (
    <div>
      <h2>Settings</h2>
      <div>
        <label>Theme: </label>
        <select
          value={settings.theme}
          onChange={(event) => changeTheme(event.target.value)}
        >
          <option value="light">Light</option>
          <option value="dark">Dark</option>
        </select>
      </div>
      <div>
        <label>
          <input
            type="checkbox"
            checked={settings.notifications.email}
            onChange={toggleEmailNotification}
          />
          Email notifications
        </label>
      </div>
      <pre>{JSON.stringify(settings, null, 2)}</pre>
    </div>
  );
}
```

**What `toggleEmailNotification` does step by step:**

```javascript
// Starting state:
{
  theme: "light",
  notifications: { email: true, push: false, sms: true },
  language: "en"
}

// Step 1: Spread top-level
{ ...settings }
// Copies: theme, notifications, language

// Step 2: Override notifications with a new object
{
  ...settings,
  notifications: { ...settings.notifications, email: false }
}

// Result:
{
  theme: "light",
  notifications: { email: false, push: false, sms: true },
  language: "en"
}
```

Each level of nesting requires its own spread. This can get verbose with deeply nested state, which is why:
1. Keep state as flat as possible.
2. Consider splitting deeply nested state into multiple `useState` calls.
3. For truly complex state, `useReducer` (Chapter 13) is a better fit.

---

## Multiple State Variables

A component can have as many `useState` calls as it needs:

```jsx
import { useState } from "react";

function RegistrationForm() {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [age, setAge] = useState("");
  const [agreedToTerms, setAgreedToTerms] = useState(false);

  function handleSubmit(event) {
    event.preventDefault();

    if (!agreedToTerms) {
      alert("You must agree to the terms.");
      return;
    }

    console.log("Submitted:", { firstName, lastName, email, age, agreedToTerms });
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2>Registration</h2>

      <div style={{ marginBottom: "0.75rem" }}>
        <label htmlFor="firstName">First Name: </label>
        <input
          id="firstName"
          value={firstName}
          onChange={(event) => setFirstName(event.target.value)}
        />
      </div>

      <div style={{ marginBottom: "0.75rem" }}>
        <label htmlFor="lastName">Last Name: </label>
        <input
          id="lastName"
          value={lastName}
          onChange={(event) => setLastName(event.target.value)}
        />
      </div>

      <div style={{ marginBottom: "0.75rem" }}>
        <label htmlFor="email">Email: </label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
        />
      </div>

      <div style={{ marginBottom: "0.75rem" }}>
        <label htmlFor="age">Age: </label>
        <input
          id="age"
          type="number"
          value={age}
          onChange={(event) => setAge(event.target.value)}
        />
      </div>

      <div style={{ marginBottom: "0.75rem" }}>
        <label>
          <input
            type="checkbox"
            checked={agreedToTerms}
            onChange={(event) => setAgreedToTerms(event.target.checked)}
          />
          I agree to the terms and conditions
        </label>
      </div>

      <button type="submit">Register</button>
    </form>
  );
}

export default RegistrationForm;
```

### When to Use One Object vs Multiple State Variables

**Use separate state variables when:**
- The values change independently of each other
- You do not always update them together
- You want simpler update logic

**Use a single object when:**
- The values are closely related and always change together
- You are managing form data with many fields
- The data naturally forms a single entity

```jsx
// ✅ Separate: these change independently
const [isLoading, setIsLoading] = useState(false);
const [error, setError] = useState(null);
const [data, setData] = useState(null);

// ✅ Object: these are one entity
const [position, setPosition] = useState({ x: 0, y: 0 });

// ✅ Object: many related fields
const [formData, setFormData] = useState({
  firstName: "",
  lastName: "",
  email: "",
  phone: "",
});
```

When using a form object, you can create a reusable change handler:

```jsx
function ContactForm() {
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    message: "",
  });

  function handleChange(event) {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  }

  return (
    <form>
      <input name="firstName" value={formData.firstName} onChange={handleChange} />
      <input name="lastName" value={formData.lastName} onChange={handleChange} />
      <input name="email" value={formData.email} onChange={handleChange} />
      <textarea name="message" value={formData.message} onChange={handleChange} />
    </form>
  );
}
```

**What `[name]: value` does:** This is JavaScript's computed property name syntax. If `name` is `"firstName"`, then `{ [name]: value }` creates `{ firstName: value }`. This lets one handler function update any field based on the input's `name` attribute.

---

## Lazy Initialization

If your initial state requires an expensive computation, you can pass a **function** to `useState` instead of a value. This function will only run on the first render:

```jsx
// ❌ Runs on EVERY render (wasteful)
const [data, setData] = useState(expensiveCalculation());

// ✅ Runs only on the FIRST render (efficient)
const [data, setData] = useState(() => expensiveCalculation());
```

A practical example:

```jsx
function App() {
  // Read from localStorage only once, on initial render
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem("theme");
    return saved || "light";
  });

  function toggleTheme() {
    setTheme((prev) => {
      const newTheme = prev === "light" ? "dark" : "light";
      localStorage.setItem("theme", newTheme);
      return newTheme;
    });
  }

  return (
    <div style={{
      backgroundColor: theme === "light" ? "#fff" : "#1a1a2e",
      color: theme === "light" ? "#333" : "#eee",
      minHeight: "100vh",
      padding: "2rem",
    }}>
      <h1>Theme: {theme}</h1>
      <button onClick={toggleTheme}>Toggle Theme</button>
    </div>
  );
}
```

**What this code does:** The initial theme is read from `localStorage`. By passing a function to `useState`, the `localStorage.getItem()` call only happens once (on the first render), not on every re-render. When the theme is toggled, we update both the state and `localStorage`.

**When to use lazy initialization:**
- Reading from `localStorage` or `sessionStorage`
- Parsing data (like JSON)
- Computing a value from a large dataset
- Any operation that is slow and only needed once

---

## Understanding Re-renders

A re-render happens when state changes. Let us make this visible:

```jsx
import { useState } from "react";

function RenderCounter() {
  const [count, setCount] = useState(0);
  const [name, setName] = useState("");

  // This log runs on every render
  console.log("Component rendered!");

  return (
    <div>
      <h2>Render Demo</h2>

      <div style={{ marginBottom: "1rem" }}>
        <p>Count: {count}</p>
        <button onClick={() => setCount((prev) => prev + 1)}>
          Increment
        </button>
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label>Name: </label>
        <input
          value={name}
          onChange={(event) => setName(event.target.value)}
        />
        <p>Hello, {name || "World"}!</p>
      </div>
    </div>
  );
}
```

**Open your browser console** and interact with this component. You will see "Component rendered!" logged every time you:
- Click the Increment button (count state changes)
- Type in the input (name state changes)

**Key insight:** When ANY state variable in a component changes, the ENTIRE component function re-runs. React then compares the new output with the previous output and updates only the parts of the DOM that actually changed. This is efficient — even though the function runs again, React only touches the DOM elements that differ.

### State Updates That Do Not Cause Re-renders

If you set state to the same value it already has, React may skip the re-render:

```jsx
const [count, setCount] = useState(0);

// First click: count goes from 0 to 1 → re-render
setCount(1);

// Second click: count is already 1, setting to 1 → no re-render
setCount(1);
```

React uses `Object.is()` comparison to determine if the state actually changed. For primitive values (numbers, strings, booleans), this checks the value. For objects and arrays, this checks the reference — which is why you must always create new objects/arrays when updating.

---

## Building a Mini Project: Interactive Expense Tracker

Let us combine everything from this chapter into a practical project:

```jsx
import { useState } from "react";

function ExpenseTracker() {
  const [expenses, setExpenses] = useState([
    { id: 1, description: "Groceries", amount: 45.5, category: "Food" },
    { id: 2, description: "Bus pass", amount: 80.0, category: "Transport" },
    { id: 3, description: "Netflix", amount: 15.99, category: "Entertainment" },
  ]);
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState("Food");
  const [filterCategory, setFilterCategory] = useState("All");

  function addExpense() {
    if (!description.trim() || !amount) return;

    const newExpense = {
      id: Date.now(),
      description: description.trim(),
      amount: parseFloat(amount),
      category: category,
    };

    setExpenses((prev) => [...prev, newExpense]);
    setDescription("");
    setAmount("");
  }

  function deleteExpense(id) {
    setExpenses((prev) => prev.filter((expense) => expense.id !== id));
  }

  // Derived values — NOT state
  const filteredExpenses =
    filterCategory === "All"
      ? expenses
      : expenses.filter((expense) => expense.category === filterCategory);

  const totalAmount = filteredExpenses.reduce(
    (sum, expense) => sum + expense.amount,
    0
  );

  const categories = ["Food", "Transport", "Entertainment", "Utilities", "Other"];

  return (
    <div style={{ maxWidth: "500px", margin: "2rem auto", fontFamily: "sans-serif" }}>
      <h1>Expense Tracker</h1>

      {/* Add Expense Form */}
      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: "8px",
          padding: "1rem",
          marginBottom: "1.5rem",
        }}
      >
        <h3 style={{ marginTop: 0 }}>Add Expense</h3>
        <div style={{ marginBottom: "0.5rem" }}>
          <input
            type="text"
            placeholder="Description"
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
          />
        </div>
        <div style={{ display: "flex", gap: "0.5rem", marginBottom: "0.5rem" }}>
          <input
            type="number"
            placeholder="Amount"
            value={amount}
            onChange={(event) => setAmount(event.target.value)}
            style={{ flex: 1, padding: "0.5rem" }}
          />
          <select
            value={category}
            onChange={(event) => setCategory(event.target.value)}
            style={{ padding: "0.5rem" }}
          >
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
        </div>
        <button
          onClick={addExpense}
          style={{
            width: "100%",
            padding: "0.5rem",
            backgroundColor: "#3182ce",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
          }}
        >
          Add Expense
        </button>
      </div>

      {/* Filter */}
      <div style={{ marginBottom: "1rem" }}>
        <label>Filter by category: </label>
        <select
          value={filterCategory}
          onChange={(event) => setFilterCategory(event.target.value)}
        >
          <option value="All">All</option>
          {categories.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>
      </div>

      {/* Expense List */}
      {filteredExpenses.length === 0 ? (
        <p style={{ color: "#999", textAlign: "center" }}>
          No expenses found.
        </p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {filteredExpenses.map((expense) => (
            <li
              key={expense.id}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "0.75rem",
                borderBottom: "1px solid #eee",
              }}
            >
              <div>
                <strong>{expense.description}</strong>
                <br />
                <span style={{ fontSize: "0.875rem", color: "#666" }}>
                  {expense.category}
                </span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                <span style={{ fontWeight: "bold" }}>
                  ${expense.amount.toFixed(2)}
                </span>
                <button
                  onClick={() => deleteExpense(expense.id)}
                  style={{
                    backgroundColor: "#e53e3e",
                    color: "white",
                    border: "none",
                    borderRadius: "4px",
                    padding: "0.25rem 0.5rem",
                    cursor: "pointer",
                    fontSize: "0.75rem",
                  }}
                >
                  Delete
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}

      {/* Total */}
      <div
        style={{
          marginTop: "1rem",
          padding: "1rem",
          backgroundColor: "#f7fafc",
          borderRadius: "8px",
          display: "flex",
          justifyContent: "space-between",
          fontWeight: "bold",
          fontSize: "1.125rem",
        }}
      >
        <span>Total ({filterCategory}):</span>
        <span>${totalAmount.toFixed(2)}</span>
      </div>
    </div>
  );
}

export default ExpenseTracker;
```

**Concepts demonstrated in this project:**

| Concept | Where It Is Used |
|---------|-----------------|
| Multiple state variables | 5 separate `useState` calls |
| String state | `description`, `category`, `filterCategory` |
| Number state (as string) | `amount` (stored as string, converted on submit) |
| Array state | `expenses` |
| Adding to array | `[...prev, newExpense]` |
| Removing from array | `prev.filter(...)` |
| Derived values | `filteredExpenses`, `totalAmount` |
| Updater functions | `setExpenses((prev) => ...)` |
| Conditional rendering | Empty state message |
| List rendering | `expenses.map(...)`, `categories.map(...)` |
| Event handling | `onChange`, `onClick` |
| Controlled inputs | All inputs are controlled |

---

## The Rules of Hooks

`useState` is a hook, and all hooks in React follow the same rules. These rules are critical to understand because breaking them causes bugs that are very hard to track down.

### Rule 1: Only Call Hooks at the Top Level

Do not call hooks inside loops, conditions, or nested functions.

```jsx
// ❌ WRONG: Hook inside a condition
function Profile({ isLoggedIn }) {
  if (isLoggedIn) {
    const [name, setName] = useState(""); // BAD!
  }
  const [age, setAge] = useState(0);
  return <div>...</div>;
}

// ❌ WRONG: Hook inside a loop
function ItemList({ items }) {
  for (const item of items) {
    const [selected, setSelected] = useState(false); // BAD!
  }
  return <div>...</div>;
}

// ✅ CORRECT: Hooks at the top level
function Profile({ isLoggedIn }) {
  const [name, setName] = useState("");
  const [age, setAge] = useState(0);

  // Use conditions AFTER the hooks
  if (!isLoggedIn) {
    return <p>Please log in</p>;
  }

  return (
    <div>
      <p>{name}, {age}</p>
    </div>
  );
}
```

**Why this rule exists:** React identifies hooks by the order they are called. On every render, React expects the same hooks to be called in the same order. If a hook is inside a condition, it might be called on some renders but not others, which breaks React's internal tracking.

```
Render 1 (isLoggedIn = true):
  Hook 1: useState("")   ← React associates this with slot 1
  Hook 2: useState(0)    ← React associates this with slot 2

Render 2 (isLoggedIn = false):
  Hook 1: useState(0)    ← React thinks this is still the name hook!
  // The name useState was skipped, so everything shifts.
  // React is now confused about which state belongs to which variable.
```

### Rule 2: Only Call Hooks from React Functions

Hooks can only be used inside:
- React component functions (functions that return JSX)
- Custom hooks (functions that start with `use` — we will learn about these in Chapter 11)

```jsx
// ❌ WRONG: Hook in a regular function
function calculateTotal() {
  const [total, setTotal] = useState(0); // BAD!
  return total;
}

// ✅ CORRECT: Hook in a component function
function TotalDisplay() {
  const [total, setTotal] = useState(0); // Good!
  return <p>Total: {total}</p>;
}
```

---

## Common Mistakes

1. **Mutating state directly.**

   ```jsx
   // ❌ Mutating an array
   const [items, setItems] = useState(["a", "b"]);
   items.push("c");      // Mutates the existing array
   setItems(items);       // Same reference — React may not re-render

   // ✅ Creating a new array
   setItems([...items, "c"]);

   // ❌ Mutating an object
   const [user, setUser] = useState({ name: "Alice", age: 28 });
   user.age = 29;         // Mutates the existing object
   setUser(user);         // Same reference — React may not re-render

   // ✅ Creating a new object
   setUser({ ...user, age: 29 });
   ```

2. **Not using an updater function when depending on previous state.**

   ```jsx
   // ❌ May produce stale results
   setCount(count + 1);
   setCount(count + 1); // Both use the same old `count`

   // ✅ Each update gets the latest value
   setCount((prev) => prev + 1);
   setCount((prev) => prev + 1);
   ```

3. **Storing derived values as state.**

   ```jsx
   // ❌ Redundant state — fullName can be computed
   const [firstName, setFirstName] = useState("Alice");
   const [lastName, setLastName] = useState("Smith");
   const [fullName, setFullName] = useState("Alice Smith"); // Unnecessary!

   // ✅ Compute it instead
   const [firstName, setFirstName] = useState("Alice");
   const [lastName, setLastName] = useState("Smith");
   const fullName = `${firstName} ${lastName}`; // Derived, not state
   ```

4. **Forgetting that `event.target.value` is always a string.**

   ```jsx
   // ❌ age will be a string "28", not a number
   <input
     type="number"
     onChange={(event) => setAge(event.target.value)}
   />

   // ✅ Convert to a number
   <input
     type="number"
     onChange={(event) => setAge(Number(event.target.value))}
   />
   ```

5. **Calling the setter function during render (infinite loop).**

   ```jsx
   // ❌ INFINITE LOOP: setCount runs during render, which causes
   // a re-render, which runs setCount again, forever
   function Bad() {
     const [count, setCount] = useState(0);
     setCount(count + 1); // Runs every render!
     return <p>{count}</p>;
   }

   // ✅ Only update state in event handlers or effects
   function Good() {
     const [count, setCount] = useState(0);
     return (
       <div>
         <p>{count}</p>
         <button onClick={() => setCount(count + 1)}>Add</button>
       </div>
     );
   }
   ```

6. **Calling the setter function instead of passing it as a reference.**

   ```jsx
   // ❌ This CALLS setCount(0) during render, causing an infinite loop
   <button onClick={setCount(0)}>Reset</button>

   // ✅ Pass a function that calls setCount when clicked
   <button onClick={() => setCount(0)}>Reset</button>
   ```

7. **Putting hooks inside conditions.**

   ```jsx
   // ❌ Breaks the rules of hooks
   if (showName) {
     const [name, setName] = useState("");
   }

   // ✅ Always call the hook, conditionally use the value
   const [name, setName] = useState("");
   // Then use `showName` to conditionally render
   ```

---

## Best Practices

1. **Keep state minimal.** Only store values that change AND cannot be computed from other state or props. If you can calculate it, calculate it.

2. **Use updater functions when updating based on previous state.** `setCount((prev) => prev + 1)` is always safer than `setCount(count + 1)`.

3. **Keep state as flat as possible.** Deeply nested state is hard to update immutably. Consider flattening your data structure or splitting into multiple state variables.

4. **Name state variables descriptively.** Use `[isModalOpen, setIsModalOpen]` instead of `[open, setOpen]`. Clear names make code self-documenting.

5. **Initialize state with the correct type.** If a state variable will hold a string, initialize with `""`, not `null` or `undefined`. This avoids type errors and makes your intent clear:

   ```jsx
   const [name, setName] = useState("");       // Will be a string
   const [count, setCount] = useState(0);      // Will be a number
   const [items, setItems] = useState([]);      // Will be an array
   const [user, setUser] = useState(null);      // Will be an object or null
   const [isOpen, setIsOpen] = useState(false); // Will be a boolean
   ```

6. **Group related state together, split unrelated state apart.**

   ```jsx
   // ✅ Related: position is x and y together
   const [position, setPosition] = useState({ x: 0, y: 0 });

   // ✅ Unrelated: loading and error are independent concerns
   const [isLoading, setIsLoading] = useState(false);
   const [error, setError] = useState(null);
   ```

7. **Use lazy initialization for expensive computations.**

   ```jsx
   // ✅ The function only runs on the first render
   const [data, setData] = useState(() => computeExpensiveInitialValue());
   ```

---

## Summary

In this chapter, you learned:

- **State** is data that belongs to a component and can change over time. When state changes, React re-renders the component.
- **`useState`** returns an array with two items: the current state value and a setter function. The setter function updates the state and triggers a re-render.
- Regular variables do not work for state because they do not trigger re-renders and they reset on every render.
- **Updater functions** (`setCount(prev => prev + 1)`) should be used when the new state depends on the previous state.
- State can hold any JavaScript type: strings, numbers, booleans, arrays, objects, or `null`.
- **Never mutate state directly.** Always create new arrays and objects using the spread operator.
- Common array operations: add with `[...arr, item]`, remove with `filter()`, update with `map()`.
- Common object operations: update with `{ ...obj, key: newValue }`.
- **Derived values** should be calculated from state, not stored as separate state.
- **Lazy initialization** (passing a function to `useState`) avoids expensive computations on every render.
- **Rules of hooks**: call hooks at the top level only, and only from React functions.
- State updates are **batched** — multiple `setState` calls in the same event handler result in a single re-render.

---

## Interview Questions

**Q1: What is state in React, and how is it different from props?**

State is data that is owned and managed by a component internally. It can change over time, and when it changes, the component re-renders. Props are data passed to a component from its parent — they are read-only and cannot be modified by the receiving component. State is like a local variable that persists across renders; props are like function arguments that the caller controls.

**Q2: Why can you not use a regular variable instead of `useState`?**

Regular variables have two problems: (1) They do not trigger re-renders — when a regular variable changes, React has no way to know about it and will not update the UI. (2) They reset to their initial value on every render because the component function runs from top to bottom each time. `useState` solves both problems by persisting the value between renders and triggering a re-render when the setter function is called.

**Q3: What happens when you call a state setter function?**

When you call a setter function (like `setCount(5)`), React schedules a re-render of the component. The state update does not happen immediately — React batches state updates for performance. On the next render, the component function runs again, and `useState` returns the new value. React then compares the new JSX output with the previous output and updates only the DOM elements that changed.

**Q4: What are updater functions, and when should you use them?**

An updater function is a function passed to a state setter, like `setCount(prev => prev + 1)`. Instead of passing the new value directly, you pass a function that receives the most recent state as its argument and returns the new state. You should use updater functions whenever the new state depends on the previous state. This is important because state updates are batched — if you call `setCount(count + 1)` multiple times in a row, all calls use the same stale `count` value. Updater functions always receive the latest state, ensuring correct results.

**Q5: Why must state updates be immutable?**

React uses reference comparison (`Object.is()`) to determine if state has changed. If you mutate an object or array in place and then set state with the same reference, React sees the same reference and may skip the re-render. Creating a new object or array gives React a different reference, which it correctly interprets as a change. Immutable updates also make state changes predictable, prevent bugs from shared references, and enable features like time-travel debugging.

**Q6: What are the rules of hooks?**

There are two rules: (1) Only call hooks at the top level of your component function — never inside loops, conditions, or nested functions. This ensures hooks are called in the same order on every render, which React relies on to associate hook calls with their stored values. (2) Only call hooks from React component functions or custom hooks — never from regular JavaScript functions. Breaking these rules causes React's internal hook tracking to break, leading to bugs where state values get mixed up.

**Q7: What is lazy initialization in `useState`?**

Lazy initialization means passing a function to `useState` instead of a value: `useState(() => expensiveComputation())`. The function is called only on the first render to compute the initial state. On subsequent renders, the function is ignored. This is useful when the initial value requires an expensive computation (like reading from localStorage, parsing JSON, or processing a large dataset) — without lazy initialization, that computation would run on every render, wasting resources.

**Q8: How do you update a specific property in an object state variable?**

Use the spread operator to create a new object that copies all existing properties and overrides the one you want to change: `setUser({ ...user, name: "Bob" })`. For nested objects, you need to spread at each level: `setSettings({ ...settings, notifications: { ...settings.notifications, email: false } })`. This ensures immutability — the original object is not modified, and React correctly detects the state change.

---

## Practice Exercises

**Exercise 1: Like Button**

Create a `LikeButton` component with:
- A count that starts at 0
- A "Like" button that increments the count
- An "Unlike" button that decrements the count (but never below 0)
- The count should change color: green when above 10, red when 0

**Exercise 2: Character Counter**

Create a `CharacterCounter` component with:
- A `<textarea>` for user input
- A character count that updates as the user types
- A maximum length of 280 characters
- The counter should turn red when fewer than 20 characters remain
- Disable the textarea when the limit is reached
- A "Clear" button that empties the textarea

**Exercise 3: Color Picker**

Create a `ColorPicker` component with:
- Three range sliders (0-255) for Red, Green, and Blue
- A preview box that shows the current color
- Display the hex color code (hint: use `.toString(16)`)
- A "Random Color" button
- A "Reset" button that sets all values to 0

**Exercise 4: Shopping List**

Create a `ShoppingList` component with:
- An input to add new items
- Each item has a name, quantity (default 1), and a "purchased" boolean
- Buttons to increase/decrease quantity
- A checkbox to mark items as purchased
- A delete button for each item
- Show total items and total purchased count
- Purchased items should appear with a line-through style

**Exercise 5: Accordion**

Create an `Accordion` component with:
- An array of FAQ items (question and answer)
- Clicking a question shows its answer
- Clicking the same question again hides the answer
- Only one answer should be visible at a time (clicking a new question hides the previous answer)
- The active question should be visually highlighted
- Hint: use a state variable that stores the ID or index of the open item, or `null` if none is open

**Exercise 6: Password Strength Checker**

Create a `PasswordChecker` component with:
- A password input field
- A "Show/Hide Password" toggle button
- A strength indicator that checks:
  - Length (at least 8 characters)
  - Contains uppercase letters
  - Contains lowercase letters
  - Contains numbers
  - Contains special characters
- Show which criteria are met and which are not (green/red)
- Show an overall strength label: Weak, Medium, Strong, Very Strong
- Use a strength meter bar that fills based on how many criteria are met

---

## What Is Next?

You now understand state — the mechanism that makes React components interactive and dynamic. You can store data, update it in response to user actions, and React automatically keeps the UI in sync.

In Chapter 6, we will learn about **Event Handling** in depth — how React handles clicks, keyboard input, form submissions, and more. You will learn about event objects, event delegation, synthetic events, and how to prevent default browser behavior.
