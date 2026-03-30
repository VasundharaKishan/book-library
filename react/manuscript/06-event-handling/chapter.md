# Chapter 6: Event Handling

---

## Learning Goals

By the end of this chapter, you will be able to:

- Handle user events like clicks, keyboard input, and form submissions
- Understand the difference between HTML event handling and React event handling
- Use the synthetic event object to access event details
- Pass arguments to event handlers correctly
- Prevent default browser behavior using `preventDefault()`
- Stop event propagation using `stopPropagation()`
- Handle keyboard, mouse, focus, and form events
- Use event delegation and understand how React handles events internally
- Build interactive components that respond to complex user interactions
- Avoid common event handling mistakes

---

## How Events Work in the Browser

Before we dive into React's event system, let us understand how events work in general.

Every time a user interacts with a web page — clicking a button, typing in a field, moving the mouse, scrolling the page — the browser creates an **event**. An event is an object that contains information about what happened: which element was interacted with, what keys were pressed, where the mouse was, and so on.

To respond to an event, you attach an **event handler** — a function that runs when the event occurs.

### Events in Vanilla JavaScript

In plain JavaScript, you add event listeners like this:

```javascript
// Method 1: addEventListener (recommended in vanilla JS)
const button = document.getElementById("myButton");
button.addEventListener("click", function () {
  alert("Button clicked!");
});

// Method 2: inline HTML attribute (not recommended)
// <button onclick="alert('Clicked!')">Click me</button>

// Method 3: DOM property
button.onclick = function () {
  alert("Button clicked!");
};
```

### Events in React

React handles events differently. Instead of calling `addEventListener` manually, you pass event handlers as props directly in your JSX:

```jsx
function App() {
  function handleClick() {
    alert("Button clicked!");
  }

  return <button onClick={handleClick}>Click me</button>;
}
```

This is one of React's key conveniences — event handlers are declared right alongside the markup, making it easy to see which elements respond to which events.

---

## React vs HTML Event Handling

There are several important differences between how HTML and React handle events:

### 1. Naming Convention

HTML uses lowercase attribute names. React uses camelCase:

| HTML | React |
|------|-------|
| `onclick` | `onClick` |
| `onchange` | `onChange` |
| `onsubmit` | `onSubmit` |
| `onmouseover` | `onMouseOver` |
| `onkeydown` | `onKeyDown` |
| `onfocus` | `onFocus` |
| `onblur` | `onBlur` |

### 2. Passing Functions, Not Strings

In HTML, you pass a string of JavaScript code. In React, you pass a function reference:

```html
<!-- HTML: string of code -->
<button onclick="handleClick()">Click</button>
```

```jsx
{/* React: function reference */}
<button onClick={handleClick}>Click</button>
```

Notice that in React, we write `onClick={handleClick}` — **without parentheses**. We are passing the function itself, not calling it. If you wrote `onClick={handleClick()}`, the function would execute immediately during render, not when the button is clicked.

### 3. Preventing Default Behavior

In HTML, you can return `false` to prevent the default action. In React, you must explicitly call `preventDefault()`:

```html
<!-- HTML: returning false works -->
<a href="https://example.com" onclick="return false;">Click</a>
```

```jsx
{/* React: must use preventDefault() */}
function Link() {
  function handleClick(event) {
    event.preventDefault();
    console.log("Link clicked, but navigation was prevented.");
  }

  return <a href="https://example.com" onClick={handleClick}>Click</a>;
}
```

### 4. Synthetic Events

React does not attach event listeners directly to DOM elements. Instead, React uses a system called **event delegation** — it attaches a single event listener to the root of your application and handles all events from there. When an event occurs, React wraps the native browser event in a **Synthetic Event** object that works identically across all browsers.

You do not need to worry about the implementation details, but it is good to know that:
- The event object you receive in React handlers is a `SyntheticEvent`, not the native DOM event.
- It has the same interface as native events (`target`, `preventDefault()`, `stopPropagation()`, etc.).
- If you ever need the native event, you can access it via `event.nativeEvent`.

---

## Basic Event Handling

### Handling Click Events

The most common event — responding to a button click:

```jsx
import { useState } from "react";

function ClickDemo() {
  const [message, setMessage] = useState("Click a button!");

  function handleHello() {
    setMessage("Hello! You clicked the first button.");
  }

  function handleGoodbye() {
    setMessage("Goodbye! You clicked the second button.");
  }

  return (
    <div>
      <p>{message}</p>
      <button onClick={handleHello}>Say Hello</button>
      <button onClick={handleGoodbye}>Say Goodbye</button>
    </div>
  );
}
```

**What this code does:** Two buttons each have their own click handler. Clicking either button updates the `message` state, which React displays in the paragraph.

### Inline Event Handlers

For simple, one-line handlers, you can define the function inline using an arrow function:

```jsx
function InlineDemo() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Add 1</button>
      <button onClick={() => setCount(0)}>Reset</button>
    </div>
  );
}
```

**When to use inline handlers:**
- The handler is simple (one line).
- The handler does not need to be reused.
- Readability is not sacrificed.

**When to use named functions:**
- The handler has multiple lines of logic.
- The handler is used by multiple elements.
- You want clearer, more readable code.

```jsx
// ✅ Simple enough for inline
<button onClick={() => setIsOpen(true)}>Open</button>

// ✅ Complex enough to deserve a named function
function handleSubmit(event) {
  event.preventDefault();
  if (!validateForm()) return;
  setIsLoading(true);
  submitData(formData);
}
<form onSubmit={handleSubmit}>...</form>
```

### Naming Conventions for Event Handlers

The React community follows a consistent naming pattern:

- Event handler functions start with `handle`: `handleClick`, `handleSubmit`, `handleChange`
- Event handler props start with `on`: `onClick`, `onSubmit`, `onChange`

When you create custom components that accept event handlers as props, follow this convention:

```jsx
// The prop name starts with "on"
<SearchBar onSearch={handleSearch} />

// Inside SearchBar, the handler function starts with "handle"
function SearchBar({ onSearch }) {
  function handleSubmit(event) {
    event.preventDefault();
    onSearch(query);
  }
  // ...
}
```

This makes code predictable — when you see `on` prefix, you know it is an event prop. When you see `handle` prefix, you know it is an event handler function.

---

## The Event Object

Every event handler receives an **event object** as its first argument. This object contains detailed information about the event.

```jsx
function EventDetails() {
  function handleClick(event) {
    console.log("Event type:", event.type);           // "click"
    console.log("Target element:", event.target);      // the clicked element
    console.log("Current target:", event.currentTarget); // element with the handler
    console.log("Timestamp:", event.timeStamp);        // when the event occurred
    console.log("Mouse X:", event.clientX);            // mouse position X
    console.log("Mouse Y:", event.clientY);            // mouse position Y
  }

  return (
    <button onClick={handleClick}>
      Click me and check the console
    </button>
  );
}
```

### Important Event Properties

| Property | Description |
|----------|-------------|
| `event.type` | The type of event: `"click"`, `"change"`, `"submit"`, etc. |
| `event.target` | The DOM element that triggered the event (the element the user actually interacted with) |
| `event.currentTarget` | The DOM element that the event handler is attached to |
| `event.preventDefault()` | Prevents the browser's default action for this event |
| `event.stopPropagation()` | Stops the event from bubbling up to parent elements |
| `event.clientX` / `event.clientY` | Mouse coordinates relative to the viewport |
| `event.key` | The key that was pressed (for keyboard events) |
| `event.shiftKey` / `event.ctrlKey` / `event.altKey` | Whether modifier keys were held |

### event.target vs event.currentTarget

This distinction is important and often confuses beginners:

```jsx
function TargetDemo() {
  function handleClick(event) {
    console.log("target:", event.target.tagName);        // What was clicked
    console.log("currentTarget:", event.currentTarget.tagName); // Where the handler is
  }

  return (
    <div onClick={handleClick} style={{ padding: "1rem", border: "1px solid #ccc" }}>
      <button>Click this button</button>
      <p>Or click this text</p>
    </div>
  );
}
```

If you click the button:
- `event.target` → `BUTTON` (the element you actually clicked)
- `event.currentTarget` → `DIV` (the element that has the `onClick` handler)

If you click the paragraph:
- `event.target` → `P`
- `event.currentTarget` → `DIV`

**Rule of thumb:**
- Use `event.target` when you need to know exactly which element was clicked.
- Use `event.currentTarget` when you need to reference the element that has the event handler.

---

## Passing Arguments to Event Handlers

Often you need to pass additional information to an event handler — like the ID of an item to delete or the value to set.

### Method 1: Arrow Function Wrapper

The most common approach — wrap the handler call in an arrow function:

```jsx
function ItemList() {
  const [items, setItems] = useState(["Apple", "Banana", "Cherry"]);

  function handleDelete(index) {
    setItems(items.filter((_, i) => i !== index));
  }

  return (
    <ul>
      {items.map((item, index) => (
        <li key={item}>
          {item}
          <button onClick={() => handleDelete(index)}>Delete</button>
        </li>
      ))}
    </ul>
  );
}
```

**What `onClick={() => handleDelete(index)}` does:** It creates a new arrow function that, when called (on click), invokes `handleDelete` with the specific `index` value. Each button gets its own arrow function with its own `index` captured via closure.

### Method 2: Return a Function from a Function

An alternative pattern — the handler function returns another function:

```jsx
function ItemList() {
  const [items, setItems] = useState(["Apple", "Banana", "Cherry"]);

  function handleDelete(index) {
    return function () {
      setItems(items.filter((_, i) => i !== index));
    };
  }

  return (
    <ul>
      {items.map((item, index) => (
        <li key={item}>
          {item}
          <button onClick={handleDelete(index)}>Delete</button>
        </li>
      ))}
    </ul>
  );
}
```

Here, `handleDelete(index)` is called during render and returns a function. That returned function is what gets called on click. This pattern is less common but useful in some situations.

### Getting Both the Event and Custom Arguments

When you use an arrow function wrapper, you can still access the event:

```jsx
function UserList() {
  const users = [
    { id: 1, name: "Alice" },
    { id: 2, name: "Bob" },
    { id: 3, name: "Charlie" },
  ];

  function handleAction(userId, action, event) {
    console.log(`User ${userId}: ${action}`);
    console.log("Clicked element:", event.target);
  }

  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>
          {user.name}
          <button onClick={(event) => handleAction(user.id, "edit", event)}>
            Edit
          </button>
          <button onClick={(event) => handleAction(user.id, "delete", event)}>
            Delete
          </button>
        </li>
      ))}
    </ul>
  );
}
```

The arrow function receives the event from React, and you forward it to your handler along with any other arguments.

---

## Common Mistake: Calling the Function Instead of Passing It

This is the most frequent event handling mistake:

```jsx
// ❌ WRONG: Calls the function immediately during render
<button onClick={handleClick()}>Click me</button>

// ❌ WRONG: Also calls immediately
<button onClick={setCount(count + 1)}>Add</button>
```

When you write `handleClick()` with parentheses, JavaScript executes the function right away — during the render — rather than waiting for a click. If the function updates state, you get an infinite loop: the state update triggers a re-render, which calls the function again, which triggers another re-render...

**Correct approaches:**

```jsx
// ✅ Pass a reference (no parentheses)
<button onClick={handleClick}>Click me</button>

// ✅ Wrap in an arrow function (for arguments or inline logic)
<button onClick={() => handleClick()}>Click me</button>
<button onClick={() => setCount(count + 1)}>Add</button>
<button onClick={() => handleDelete(item.id)}>Delete</button>
```

**The difference visualized:**

```
onClick={handleClick}      → "When clicked, run handleClick"
onClick={handleClick()}    → "Run handleClick RIGHT NOW and pass its
                              return value as the click handler"
onClick={() => handleClick()} → "When clicked, run a function that
                                  calls handleClick"
```

---

## Preventing Default Behavior

Some HTML elements have default behaviors. For example:
- A `<form>` submits and reloads the page when the submit button is clicked.
- An `<a>` tag navigates to its `href` URL.
- A right-click opens the context menu.

To prevent these defaults in React, call `event.preventDefault()`:

### Preventing Form Submission

```jsx
import { useState } from "react";

function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  function handleSubmit(event) {
    event.preventDefault(); // Prevents page reload

    console.log("Submitting:", { email, password });
    // In a real app, you would send this data to a server
  }

  return (
    <form onSubmit={handleSubmit}>
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
        <label htmlFor="password">Password: </label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />
      </div>
      <button type="submit">Log In</button>
    </form>
  );
}
```

**Why `event.preventDefault()` is critical here:** Without it, the browser would submit the form the traditional way — creating an HTTP request and reloading the page. In a single-page React application, you want to handle the submission with JavaScript instead, so you prevent the default and handle it yourself.

### Preventing Link Navigation

```jsx
function CustomLink() {
  function handleClick(event) {
    event.preventDefault();
    console.log("Navigation prevented. We can use React Router instead.");
  }

  return (
    <a href="https://example.com" onClick={handleClick}>
      Click me (will not navigate)
    </a>
  );
}
```

---

## Event Propagation (Bubbling)

When an event occurs on an element, it does not just fire on that element. The event **bubbles up** through the DOM tree, triggering event handlers on each parent element along the way.

```jsx
function BubblingDemo() {
  function handleOuterClick() {
    console.log("Outer div clicked");
  }

  function handleMiddleClick() {
    console.log("Middle div clicked");
  }

  function handleInnerClick() {
    console.log("Inner button clicked");
  }

  return (
    <div onClick={handleOuterClick} style={{ padding: "2rem", backgroundColor: "#fee" }}>
      Outer
      <div onClick={handleMiddleClick} style={{ padding: "2rem", backgroundColor: "#efe" }}>
        Middle
        <button onClick={handleInnerClick}>
          Inner Button
        </button>
      </div>
    </div>
  );
}
```

When you click the inner button, the console shows:

```
Inner button clicked
Middle div clicked
Outer div clicked
```

The event starts at the button (innermost), then bubbles up to the middle div, then to the outer div. All three handlers fire.

### Stopping Propagation

Use `event.stopPropagation()` to prevent the event from bubbling up:

```jsx
function StopPropagationDemo() {
  function handleOuterClick() {
    console.log("Outer div clicked");
  }

  function handleButtonClick(event) {
    event.stopPropagation(); // Stops bubbling
    console.log("Button clicked — event does NOT reach the outer div");
  }

  return (
    <div onClick={handleOuterClick} style={{ padding: "2rem", backgroundColor: "#fee" }}>
      <p>Click the outer area to trigger the outer handler.</p>
      <button onClick={handleButtonClick}>
        Click me (stops propagation)
      </button>
    </div>
  );
}
```

Now, clicking the button only logs "Button clicked" — the outer handler does not fire.

### Practical Use Case: Modal Backdrop

A common use case for `stopPropagation` is a modal dialog with a backdrop. You want clicking the backdrop to close the modal, but clicking inside the modal should not close it:

```jsx
import { useState } from "react";

function ModalDemo() {
  const [isOpen, setIsOpen] = useState(false);

  function handleBackdropClick() {
    setIsOpen(false);
  }

  function handleModalClick(event) {
    event.stopPropagation(); // Clicking inside modal does not close it
  }

  return (
    <div>
      <button onClick={() => setIsOpen(true)}>Open Modal</button>

      {isOpen && (
        <div
          onClick={handleBackdropClick}
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0, 0, 0, 0.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <div
            onClick={handleModalClick}
            style={{
              backgroundColor: "white",
              padding: "2rem",
              borderRadius: "8px",
              minWidth: "300px",
            }}
          >
            <h2>Modal Title</h2>
            <p>Click outside this box to close the modal.</p>
            <p>Clicking inside this box does nothing because propagation is stopped.</p>
            <button onClick={() => setIsOpen(false)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
}
```

**How this works:**

1. The backdrop (dark overlay) has an `onClick` that closes the modal.
2. The modal content has an `onClick` with `stopPropagation()`.
3. When the user clicks inside the modal, the click event fires on the modal content but does NOT bubble up to the backdrop — so the modal stays open.
4. When the user clicks the backdrop (outside the modal content), the backdrop's `onClick` fires and closes the modal.

---

## Keyboard Events

React provides three keyboard events:

| Event | When It Fires |
|-------|---------------|
| `onKeyDown` | When a key is pressed down |
| `onKeyUp` | When a key is released |
| `onKeyPress` | **Deprecated** — do not use |

### Basic Keyboard Handling

```jsx
import { useState } from "react";

function KeyboardDemo() {
  const [lastKey, setLastKey] = useState("None");
  const [keys, setKeys] = useState([]);

  function handleKeyDown(event) {
    setLastKey(event.key);

    if (event.key === "Enter") {
      console.log("Enter pressed!");
    }

    if (event.key === "Escape") {
      console.log("Escape pressed!");
    }

    // Detect keyboard shortcuts
    if (event.ctrlKey && event.key === "s") {
      event.preventDefault(); // Prevent browser save dialog
      console.log("Ctrl+S: Save triggered!");
    }
  }

  return (
    <div>
      <h2>Keyboard Events</h2>
      <input
        type="text"
        onKeyDown={handleKeyDown}
        placeholder="Type here and watch the console..."
        style={{ padding: "0.5rem", width: "300px" }}
      />
      <p>Last key pressed: <strong>{lastKey}</strong></p>
    </div>
  );
}
```

### Common Key Values

| `event.key` Value | Key |
|-------------------|-----|
| `"Enter"` | Enter/Return |
| `"Escape"` | Escape |
| `"Tab"` | Tab |
| `"Backspace"` | Backspace |
| `"Delete"` | Delete |
| `"ArrowUp"` | Up arrow |
| `"ArrowDown"` | Down arrow |
| `"ArrowLeft"` | Left arrow |
| `"ArrowRight"` | Right arrow |
| `" "` | Space (a space character) |
| `"a"` through `"z"` | Letter keys (lowercase) |
| `"A"` through `"Z"` | Letter keys with Shift (uppercase) |
| `"1"` through `"9"` | Number keys |
| `"F1"` through `"F12"` | Function keys |

### Modifier Keys

Check if modifier keys are held using boolean properties:

```jsx
function handleKeyDown(event) {
  if (event.ctrlKey) console.log("Ctrl is held");
  if (event.shiftKey) console.log("Shift is held");
  if (event.altKey) console.log("Alt is held");
  if (event.metaKey) console.log("Meta (Cmd/Win) is held");

  // Common shortcuts
  if (event.ctrlKey && event.key === "z") {
    event.preventDefault();
    console.log("Undo!");
  }

  if (event.ctrlKey && event.shiftKey && event.key === "Z") {
    event.preventDefault();
    console.log("Redo!");
  }
}
```

### Practical Example: Search with Enter Key

```jsx
import { useState } from "react";

function SearchBar() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);

  function performSearch() {
    if (query.trim() === "") return;

    // Simulate search results
    const allItems = [
      "React", "Redux", "Router", "Relay",
      "JavaScript", "Java", "Jest",
      "TypeScript", "Tailwind", "Testing Library",
    ];
    const filtered = allItems.filter((item) =>
      item.toLowerCase().includes(query.toLowerCase())
    );
    setResults(filtered);
  }

  function handleKeyDown(event) {
    if (event.key === "Enter") {
      performSearch();
    }
    if (event.key === "Escape") {
      setQuery("");
      setResults([]);
    }
  }

  return (
    <div>
      <h2>Search</h2>
      <div style={{ display: "flex", gap: "0.5rem" }}>
        <input
          type="text"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Search... (Enter to search, Esc to clear)"
          style={{ flex: 1, padding: "0.5rem" }}
        />
        <button onClick={performSearch}>Search</button>
      </div>
      {results.length > 0 && (
        <ul>
          {results.map((result) => (
            <li key={result}>{result}</li>
          ))}
        </ul>
      )}
      {results.length === 0 && query && (
        <p style={{ color: "#999" }}>No results found.</p>
      )}
    </div>
  );
}
```

---

## Mouse Events

React provides several mouse events:

| Event | When It Fires |
|-------|---------------|
| `onClick` | When the element is clicked |
| `onDoubleClick` | When the element is double-clicked |
| `onMouseDown` | When a mouse button is pressed |
| `onMouseUp` | When a mouse button is released |
| `onMouseEnter` | When the mouse enters an element (does not bubble) |
| `onMouseLeave` | When the mouse leaves an element (does not bubble) |
| `onMouseOver` | When the mouse moves over an element (bubbles) |
| `onMouseOut` | When the mouse moves out of an element (bubbles) |
| `onMouseMove` | When the mouse moves within an element |
| `onContextMenu` | When right-click context menu is triggered |

### Hover Effects with State

While CSS `:hover` handles most hover styling, sometimes you need hover state in JavaScript:

```jsx
import { useState } from "react";

function HoverCard() {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        padding: "1.5rem",
        border: "2px solid",
        borderColor: isHovered ? "#3182ce" : "#e2e8f0",
        borderRadius: "8px",
        backgroundColor: isHovered ? "#ebf8ff" : "white",
        transform: isHovered ? "scale(1.02)" : "scale(1)",
        transition: "all 0.2s ease",
        cursor: "pointer",
      }}
    >
      <h3>Hover over me!</h3>
      <p>
        {isHovered
          ? "You are hovering! The card is highlighted."
          : "Move your mouse over this card to see the effect."}
      </p>
    </div>
  );
}
```

**When to use JavaScript hover vs CSS hover:**
- Use **CSS `:hover`** for simple visual changes (color, background, shadow). It is more performant.
- Use **JavaScript hover state** when you need to change content, show/hide elements, trigger side effects, or coordinate hover state with other logic.

### Mouse Position Tracking

```jsx
import { useState } from "react";

function MouseTracker() {
  const [position, setPosition] = useState({ x: 0, y: 0 });

  function handleMouseMove(event) {
    setPosition({
      x: event.clientX,
      y: event.clientY,
    });
  }

  return (
    <div
      onMouseMove={handleMouseMove}
      style={{
        height: "300px",
        border: "2px solid #ccc",
        borderRadius: "8px",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        position: "relative",
        cursor: "crosshair",
      }}
    >
      <p>
        Mouse position: ({position.x}, {position.y})
      </p>
      <div
        style={{
          position: "fixed",
          left: position.x + 10,
          top: position.y + 10,
          backgroundColor: "#3182ce",
          color: "white",
          padding: "0.25rem 0.5rem",
          borderRadius: "4px",
          fontSize: "0.75rem",
          pointerEvents: "none",
        }}
      >
        {position.x}, {position.y}
      </div>
    </div>
  );
}
```

**What this code does:** As the mouse moves over the div, `onMouseMove` fires continuously, updating the position state. A small tooltip follows the mouse cursor showing the coordinates. The `pointerEvents: "none"` style on the tooltip prevents it from interfering with mouse events.

---

## Focus and Blur Events

Focus events fire when an element gains or loses focus (typically input fields):

| Event | When It Fires |
|-------|---------------|
| `onFocus` | When the element receives focus |
| `onBlur` | When the element loses focus |

### Input Validation on Blur

A common pattern — validate input when the user leaves the field:

```jsx
import { useState } from "react";

function EmailInput() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [isFocused, setIsFocused] = useState(false);

  function handleBlur() {
    setIsFocused(false);

    if (email === "") {
      setError("Email is required.");
    } else if (!email.includes("@")) {
      setError("Please enter a valid email address.");
    } else {
      setError("");
    }
  }

  function handleFocus() {
    setIsFocused(true);
    setError(""); // Clear error when user starts editing again
  }

  return (
    <div>
      <label htmlFor="email">Email: </label>
      <input
        id="email"
        type="email"
        value={email}
        onChange={(event) => setEmail(event.target.value)}
        onFocus={handleFocus}
        onBlur={handleBlur}
        style={{
          padding: "0.5rem",
          border: `2px solid ${error ? "#e53e3e" : isFocused ? "#3182ce" : "#ccc"}`,
          borderRadius: "4px",
          outline: "none",
        }}
      />
      {error && (
        <p style={{ color: "#e53e3e", fontSize: "0.875rem", marginTop: "0.25rem" }}>
          {error}
        </p>
      )}
    </div>
  );
}
```

**What this code does:**

1. When the input gains focus (`onFocus`), we set `isFocused` to true and clear any existing error.
2. When the input loses focus (`onBlur`), we validate the email and show an error if invalid.
3. The border color changes based on state: red for error, blue for focused, gray for default.

This is called **blur validation** and is a common UX pattern — it is less aggressive than validating on every keystroke, giving the user a chance to finish typing before showing errors.

---

## Form Events

### onChange

The `onChange` event fires whenever the value of a form element changes. In React, it fires on every keystroke for text inputs — which is different from HTML's `change` event that fires only when the input loses focus.

```jsx
import { useState } from "react";

function FormDemo() {
  const [text, setText] = useState("");
  const [select, setSelect] = useState("option1");
  const [isChecked, setIsChecked] = useState(false);

  return (
    <div>
      {/* Text input: event.target.value */}
      <div style={{ marginBottom: "1rem" }}>
        <label>Text: </label>
        <input
          type="text"
          value={text}
          onChange={(event) => setText(event.target.value)}
        />
        <p>You typed: {text}</p>
      </div>

      {/* Select: event.target.value */}
      <div style={{ marginBottom: "1rem" }}>
        <label>Select: </label>
        <select value={select} onChange={(event) => setSelect(event.target.value)}>
          <option value="option1">Option 1</option>
          <option value="option2">Option 2</option>
          <option value="option3">Option 3</option>
        </select>
        <p>Selected: {select}</p>
      </div>

      {/* Checkbox: event.target.checked */}
      <div style={{ marginBottom: "1rem" }}>
        <label>
          <input
            type="checkbox"
            checked={isChecked}
            onChange={(event) => setIsChecked(event.target.checked)}
          />
          I agree to the terms
        </label>
        <p>Agreed: {isChecked ? "Yes" : "No"}</p>
      </div>
    </div>
  );
}
```

**Key difference for checkboxes:** For text inputs and selects, you use `event.target.value`. For checkboxes, you use `event.target.checked` (a boolean). This is a common source of bugs.

### onSubmit

The `onSubmit` event fires when a form is submitted — either by clicking a submit button or pressing Enter in a text input:

```jsx
import { useState } from "react";

function FeedbackForm() {
  const [name, setName] = useState("");
  const [rating, setRating] = useState("5");
  const [comment, setComment] = useState("");
  const [submitted, setSubmitted] = useState(false);

  function handleSubmit(event) {
    event.preventDefault();

    if (!name.trim()) {
      alert("Please enter your name.");
      return;
    }

    console.log("Feedback submitted:", {
      name: name.trim(),
      rating: Number(rating),
      comment: comment.trim(),
    });

    setSubmitted(true);
  }

  if (submitted) {
    return (
      <div style={{ textAlign: "center", padding: "2rem" }}>
        <h2>Thank you, {name}!</h2>
        <p>Your feedback has been submitted.</p>
        <button onClick={() => {
          setName("");
          setRating("5");
          setComment("");
          setSubmitted(false);
        }}>
          Submit another
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: "400px" }}>
      <h2>Feedback Form</h2>

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="name">Name: </label>
        <input
          id="name"
          type="text"
          value={name}
          onChange={(event) => setName(event.target.value)}
          style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
        />
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="rating">Rating: </label>
        <select
          id="rating"
          value={rating}
          onChange={(event) => setRating(event.target.value)}
          style={{ padding: "0.5rem" }}
        >
          <option value="5">5 - Excellent</option>
          <option value="4">4 - Good</option>
          <option value="3">3 - Average</option>
          <option value="2">2 - Poor</option>
          <option value="1">1 - Terrible</option>
        </select>
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="comment">Comment: </label>
        <textarea
          id="comment"
          value={comment}
          onChange={(event) => setComment(event.target.value)}
          rows={4}
          style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
        />
      </div>

      <button type="submit" style={{ padding: "0.5rem 1rem" }}>
        Submit Feedback
      </button>
    </form>
  );
}
```

**Design pattern:** After successful submission, the component renders a "thank you" message instead of the form. The "Submit another" button resets all state to show the form again.

---

## Handling Multiple Inputs with One Handler

When a form has many fields, writing a separate handler for each is tedious. You can use a single handler by leveraging the `name` attribute:

```jsx
import { useState } from "react";

function RegistrationForm() {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
    agreeToTerms: false,
    role: "user",
  });

  function handleChange(event) {
    const { name, value, type, checked } = event.target;

    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  }

  function handleSubmit(event) {
    event.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      alert("Passwords do not match!");
      return;
    }

    if (!formData.agreeToTerms) {
      alert("You must agree to the terms.");
      return;
    }

    console.log("Form submitted:", formData);
  }

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: "400px" }}>
      <h2>Register</h2>

      <div style={{ marginBottom: "0.75rem" }}>
        <label htmlFor="username">Username:</label>
        <input
          id="username"
          name="username"
          type="text"
          value={formData.username}
          onChange={handleChange}
          style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
        />
      </div>

      <div style={{ marginBottom: "0.75rem" }}>
        <label htmlFor="email">Email:</label>
        <input
          id="email"
          name="email"
          type="email"
          value={formData.email}
          onChange={handleChange}
          style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
        />
      </div>

      <div style={{ marginBottom: "0.75rem" }}>
        <label htmlFor="password">Password:</label>
        <input
          id="password"
          name="password"
          type="password"
          value={formData.password}
          onChange={handleChange}
          style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
        />
      </div>

      <div style={{ marginBottom: "0.75rem" }}>
        <label htmlFor="confirmPassword">Confirm Password:</label>
        <input
          id="confirmPassword"
          name="confirmPassword"
          type="password"
          value={formData.confirmPassword}
          onChange={handleChange}
          style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
        />
      </div>

      <div style={{ marginBottom: "0.75rem" }}>
        <label htmlFor="role">Role:</label>
        <select
          id="role"
          name="role"
          value={formData.role}
          onChange={handleChange}
          style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
        >
          <option value="user">User</option>
          <option value="editor">Editor</option>
          <option value="admin">Admin</option>
        </select>
      </div>

      <div style={{ marginBottom: "0.75rem" }}>
        <label>
          <input
            name="agreeToTerms"
            type="checkbox"
            checked={formData.agreeToTerms}
            onChange={handleChange}
          />
          I agree to the terms and conditions
        </label>
      </div>

      <button type="submit" style={{ padding: "0.5rem 1rem" }}>
        Register
      </button>
    </form>
  );
}
```

**How the unified handler works:**

```javascript
function handleChange(event) {
  const { name, value, type, checked } = event.target;

  setFormData((prev) => ({
    ...prev,
    [name]: type === "checkbox" ? checked : value,
  }));
}
```

1. **`event.target.name`** — the `name` attribute of the input that changed (e.g., `"username"`, `"email"`).
2. **`event.target.value`** — the new value of the input.
3. **`event.target.type`** — the type of input (e.g., `"text"`, `"checkbox"`).
4. **`event.target.checked`** — for checkboxes, whether it is checked.
5. **`[name]: value`** — JavaScript's computed property name sets the right property.
6. **`type === "checkbox" ? checked : value`** — uses `checked` for checkboxes, `value` for everything else.

This single handler works for text inputs, email inputs, password inputs, selects, and checkboxes — all because each input has a unique `name` attribute that matches a property in the state object.

---

## Event Handler Patterns in Parent-Child Components

When a child component needs to communicate with its parent, the parent passes a callback function as a prop. This is a fundamental React pattern:

```jsx
import { useState } from "react";

function SearchInput({ onSearch }) {
  const [query, setQuery] = useState("");

  function handleSubmit(event) {
    event.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  }

  function handleKeyDown(event) {
    if (event.key === "Escape") {
      setQuery("");
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Search..."
        style={{ padding: "0.5rem", marginRight: "0.5rem" }}
      />
      <button type="submit">Search</button>
    </form>
  );
}

function SearchResults({ results }) {
  if (results.length === 0) {
    return <p style={{ color: "#999" }}>No results to display.</p>;
  }

  return (
    <ul>
      {results.map((result, index) => (
        <li key={index}>{result}</li>
      ))}
    </ul>
  );
}

function SearchPage() {
  const [results, setResults] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");

  function handleSearch(query) {
    setSearchTerm(query);

    // Simulate searching
    const allItems = [
      "Learn React basics",
      "React hooks tutorial",
      "Building a React app",
      "React testing guide",
      "JavaScript fundamentals",
      "CSS Grid layout",
      "Node.js introduction",
    ];

    const filtered = allItems.filter((item) =>
      item.toLowerCase().includes(query.toLowerCase())
    );
    setResults(filtered);
  }

  return (
    <div style={{ maxWidth: "500px", margin: "2rem auto" }}>
      <h1>Search</h1>
      <SearchInput onSearch={handleSearch} />
      {searchTerm && (
        <p style={{ margin: "1rem 0", color: "#666" }}>
          Results for: "{searchTerm}"
        </p>
      )}
      <SearchResults results={results} />
    </div>
  );
}

export default SearchPage;
```

**The data flow:**

```
SearchPage (parent)
  ├── handleSearch function defined here
  ├── state: results, searchTerm
  │
  ├── SearchInput (child)
  │     ├── receives onSearch prop (which is handleSearch)
  │     ├── user types and presses Enter or clicks Search
  │     └── calls onSearch(query) → triggers handleSearch in parent
  │
  └── SearchResults (child)
        ├── receives results prop
        └── displays the filtered results
```

This pattern — **data flows down (props), events flow up (callbacks)** — is the core communication model in React. The parent controls the state, and children notify the parent of events through callback props.

---

## Building a Mini Project: Interactive Quiz

Let us build a quiz component that uses many event handling concepts:

```jsx
import { useState } from "react";

function Quiz() {
  const questions = [
    {
      id: 1,
      question: "What does JSX stand for?",
      options: [
        "JavaScript XML",
        "JavaScript Extension",
        "Java Syntax Extension",
        "JSON XML",
      ],
      correctAnswer: 0,
    },
    {
      id: 2,
      question: "Which hook is used to manage state in functional components?",
      options: ["useEffect", "useRef", "useState", "useReducer"],
      correctAnswer: 2,
    },
    {
      id: 3,
      question: "What method is used to prevent a form from reloading the page?",
      options: [
        "event.stopPropagation()",
        "event.preventDefault()",
        "event.cancelBubble()",
        "return false",
      ],
      correctAnswer: 1,
    },
    {
      id: 4,
      question: "How do you pass data from a parent to a child component?",
      options: ["State", "Props", "Context", "Refs"],
      correctAnswer: 1,
    },
    {
      id: 5,
      question: "What renders nothing in JSX?",
      options: ["0", "\"\"", "false", "[]"],
      correctAnswer: 2,
    },
  ];

  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [score, setScore] = useState(0);
  const [showResult, setShowResult] = useState(false);
  const [answered, setAnswered] = useState(false);

  const question = questions[currentQuestion];
  const isLastQuestion = currentQuestion === questions.length - 1;

  function handleOptionClick(optionIndex) {
    if (answered) return; // Prevent changing answer

    setSelectedAnswer(optionIndex);
    setAnswered(true);

    if (optionIndex === question.correctAnswer) {
      setScore((prev) => prev + 1);
    }
  }

  function handleNext() {
    if (isLastQuestion) {
      setShowResult(true);
    } else {
      setCurrentQuestion((prev) => prev + 1);
      setSelectedAnswer(null);
      setAnswered(false);
    }
  }

  function handleRestart() {
    setCurrentQuestion(0);
    setSelectedAnswer(null);
    setScore(0);
    setShowResult(false);
    setAnswered(false);
  }

  function handleKeyDown(event) {
    if (!answered) {
      const keyNum = parseInt(event.key);
      if (keyNum >= 1 && keyNum <= question.options.length) {
        handleOptionClick(keyNum - 1);
      }
    }

    if (answered && event.key === "Enter") {
      handleNext();
    }
  }

  if (showResult) {
    const percentage = Math.round((score / questions.length) * 100);

    return (
      <div style={{ textAlign: "center", padding: "2rem", maxWidth: "500px", margin: "0 auto" }}>
        <h1>Quiz Complete!</h1>
        <p style={{ fontSize: "3rem", margin: "1rem 0" }}>
          {percentage >= 80 ? "🎉" : percentage >= 50 ? "👍" : "📚"}
        </p>
        <p style={{ fontSize: "1.5rem" }}>
          You scored {score} out of {questions.length} ({percentage}%)
        </p>
        <p style={{ color: "#666" }}>
          {percentage >= 80
            ? "Excellent! You know your React well!"
            : percentage >= 50
            ? "Good job! Keep practicing."
            : "Keep studying — you will get there!"}
        </p>
        <button
          onClick={handleRestart}
          style={{
            padding: "0.75rem 1.5rem",
            fontSize: "1rem",
            backgroundColor: "#3182ce",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            marginTop: "1rem",
          }}
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div
      onKeyDown={handleKeyDown}
      tabIndex={0}
      style={{ maxWidth: "500px", margin: "2rem auto", outline: "none" }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
        <span>
          Question {currentQuestion + 1} of {questions.length}
        </span>
        <span>Score: {score}</span>
      </div>

      {/* Progress bar */}
      <div style={{ backgroundColor: "#e2e8f0", borderRadius: "4px", height: "8px", marginBottom: "1.5rem" }}>
        <div
          style={{
            backgroundColor: "#3182ce",
            height: "100%",
            borderRadius: "4px",
            width: `${((currentQuestion + 1) / questions.length) * 100}%`,
            transition: "width 0.3s ease",
          }}
        />
      </div>

      <h2 style={{ marginBottom: "1rem" }}>{question.question}</h2>

      <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
        {question.options.map((option, index) => {
          let backgroundColor = "white";
          let borderColor = "#e2e8f0";
          let color = "inherit";

          if (answered) {
            if (index === question.correctAnswer) {
              backgroundColor = "#c6f6d5";
              borderColor = "#38a169";
            } else if (index === selectedAnswer && index !== question.correctAnswer) {
              backgroundColor = "#fed7d7";
              borderColor = "#e53e3e";
            }
          } else if (index === selectedAnswer) {
            backgroundColor = "#ebf8ff";
            borderColor = "#3182ce";
          }

          return (
            <button
              key={index}
              onClick={() => handleOptionClick(index)}
              style={{
                padding: "0.75rem 1rem",
                border: `2px solid ${borderColor}`,
                borderRadius: "8px",
                backgroundColor: backgroundColor,
                color: color,
                cursor: answered ? "default" : "pointer",
                textAlign: "left",
                fontSize: "1rem",
                transition: "all 0.2s ease",
              }}
            >
              <strong>{index + 1}.</strong> {option}
            </button>
          );
        })}
      </div>

      {answered && (
        <div style={{ marginTop: "1rem" }}>
          <p style={{ color: selectedAnswer === question.correctAnswer ? "#38a169" : "#e53e3e" }}>
            {selectedAnswer === question.correctAnswer
              ? "Correct! Well done."
              : `Incorrect. The correct answer is: ${question.options[question.correctAnswer]}`}
          </p>
          <button
            onClick={handleNext}
            style={{
              padding: "0.5rem 1rem",
              backgroundColor: "#3182ce",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
              marginTop: "0.5rem",
            }}
          >
            {isLastQuestion ? "See Results" : "Next Question"}
          </button>
          <p style={{ fontSize: "0.75rem", color: "#999", marginTop: "0.25rem" }}>
            Press Enter to continue
          </p>
        </div>
      )}
    </div>
  );
}

export default Quiz;
```

**Event handling concepts demonstrated:**

| Concept | Where Used |
|---------|------------|
| `onClick` | Option buttons, Next button, Restart button |
| `onKeyDown` | Number keys to select options, Enter to continue |
| Passing arguments | `handleOptionClick(index)` via arrow function |
| `event.key` | Detecting number keys and Enter |
| Preventing re-selection | `if (answered) return` guard |
| State-driven UI | Button colors change based on correct/incorrect |
| Conditional rendering | Result screen vs question screen |
| `tabIndex={0}` | Makes the div focusable for keyboard events |

---

## Common Mistakes

1. **Calling the handler instead of passing it.**

   ```jsx
   // ❌ Executes immediately, probably causes infinite re-renders
   <button onClick={handleClick()}>Click</button>

   // ✅ Passes function reference
   <button onClick={handleClick}>Click</button>
   ```

2. **Forgetting `event.preventDefault()` on forms.**

   ```jsx
   // ❌ Page reloads on submit
   function handleSubmit(event) {
     console.log("Submitted!");
     // Forgot event.preventDefault()!
   }

   // ✅ Prevents page reload
   function handleSubmit(event) {
     event.preventDefault();
     console.log("Submitted!");
   }
   ```

3. **Using `event.target.value` for checkboxes.**

   ```jsx
   // ❌ event.target.value for a checkbox is always "on"
   onChange={(event) => setChecked(event.target.value)}

   // ✅ Use event.target.checked for checkboxes
   onChange={(event) => setChecked(event.target.checked)}
   ```

4. **Forgetting that `onMouseEnter`/`onMouseLeave` do not bubble, but `onMouseOver`/`onMouseOut` do.** Use `onMouseEnter`/`onMouseLeave` when you want hover behavior only on the specific element, not triggered by children.

5. **Not accounting for event bubbling.**

   ```jsx
   // ❌ Clicking the delete button also triggers the card's onClick
   <div onClick={handleCardClick}>
     <button onClick={handleDelete}>Delete</button>
   </div>

   // ✅ Stop propagation on the button
   <div onClick={handleCardClick}>
     <button onClick={(event) => {
       event.stopPropagation();
       handleDelete();
     }}>Delete</button>
   </div>
   ```

6. **Using `onKeyPress` (deprecated).** Use `onKeyDown` instead. `onKeyPress` does not fire for all keys (like Escape, Arrow keys, etc.) and has been deprecated.

7. **Not giving focus to elements that need keyboard events.** Non-input elements like `<div>` need `tabIndex={0}` or `tabIndex={-1}` to be focusable and receive keyboard events.

---

## Best Practices

1. **Use named handler functions for complex logic.** Inline handlers are fine for simple one-liners, but extract named functions when the logic involves multiple steps.

2. **Follow naming conventions.** Handler functions: `handleClick`, `handleSubmit`, `handleChange`. Handler props: `onClick`, `onSubmit`, `onChange`.

3. **Always call `event.preventDefault()` for form submissions** in single-page applications.

4. **Use `event.stopPropagation()` sparingly.** Only stop propagation when you have a specific reason. Overusing it can make event flow confusing and break features that depend on event bubbling.

5. **Keep event handlers close to their UI.** Define handlers in the same component that renders the interactive elements. This makes it easy to understand what each element does.

6. **Use the `name` attribute for multi-field forms** to create a single reusable `handleChange` function instead of writing one handler per field.

7. **Be careful with `onMouseMove`.** This event fires very frequently — potentially dozens of times per second. If the handler updates state, ensure the updates are lightweight. For heavy operations, consider throttling or debouncing (covered in later chapters).

8. **Use `onKeyDown` instead of `onKeyPress`.** `onKeyDown` handles all keys and is the modern standard. `onKeyPress` is deprecated and does not fire for modifier keys, arrows, or Escape.

---

## Summary

In this chapter, you learned:

- React uses **camelCase** event names (`onClick`, `onChange`, `onSubmit`) and passes **function references** as handlers, not strings.
- The **event object** contains details about the event (`target`, `key`, `clientX`, `preventDefault()`, `stopPropagation()`).
- **`event.target`** is what triggered the event; **`event.currentTarget`** is where the handler is attached.
- **`event.preventDefault()`** stops the browser's default behavior (like form submission or link navigation).
- **Event bubbling** means events travel up the DOM tree. Use **`event.stopPropagation()`** to stop this when needed.
- To **pass arguments** to event handlers, wrap them in arrow functions: `onClick={() => handleDelete(id)}`.
- **Keyboard events** use `onKeyDown` with `event.key` to detect specific keys and `event.ctrlKey`/`event.shiftKey` for modifier keys.
- **Mouse events** include `onClick`, `onDoubleClick`, `onMouseEnter`/`onMouseLeave`, and `onMouseMove`.
- **Focus events** (`onFocus`, `onBlur`) are useful for input validation.
- A **single `handleChange` function** can manage multiple form inputs by using the `name` attribute and computed property names.
- Parent-child communication works through **callback props**: the parent passes a function, the child calls it with data.

---

## Interview Questions

**Q1: How does event handling in React differ from vanilla JavaScript?**

React uses camelCase event names (`onClick` vs `onclick`), passes function references instead of strings, and uses a Synthetic Event system. Instead of attaching event listeners directly to DOM elements with `addEventListener`, React uses event delegation — it attaches a single listener at the root and manages all events internally. React also wraps native browser events in `SyntheticEvent` objects that normalize behavior across browsers. Additionally, you cannot return `false` to prevent default behavior in React; you must explicitly call `event.preventDefault()`.

**Q2: What is a Synthetic Event in React?**

A Synthetic Event is React's cross-browser wrapper around the browser's native event. It has the same interface as native events (properties like `target`, `type`, methods like `preventDefault()`, `stopPropagation()`), but it works consistently across all browsers. React creates Synthetic Events as part of its event delegation system. If you need the original native browser event, you can access it via `event.nativeEvent`.

**Q3: What is the difference between `event.target` and `event.currentTarget`?**

`event.target` is the DOM element that actually triggered the event — the innermost element that was clicked, focused, etc. `event.currentTarget` is the DOM element that the event handler is attached to. They are the same when the handler is on the exact element that was interacted with. They differ when the event has bubbled up — for example, if you click a `<button>` inside a `<div>` that has the click handler, `event.target` is the button but `event.currentTarget` is the div.

**Q4: Why do we use `onClick={handleClick}` instead of `onClick={handleClick()}`?**

`onClick={handleClick}` passes the function as a reference — it tells React "when a click happens, call this function." `onClick={handleClick()}` calls the function immediately during render and passes its return value as the click handler. If the function updates state, calling it during render triggers a re-render, which calls it again, creating an infinite loop. You want to pass the function itself, not call it.

**Q5: How do you handle events for multiple form inputs without writing a separate handler for each?**

Create a single `handleChange` function that uses `event.target.name` to identify which input changed and `event.target.value` (or `event.target.checked` for checkboxes) to get the new value. Store form data as an object in state, and use computed property names to update the right field: `setFormData(prev => ({ ...prev, [name]: value }))`. Each input must have a `name` attribute that matches the corresponding property in the state object.

**Q6: What is event propagation (bubbling) in React, and how do you control it?**

Event propagation (bubbling) means that when an event occurs on an element, it fires the handler on that element first, then bubbles up to trigger handlers on each parent element up the DOM tree. In React, this works the same as in the DOM. You can stop bubbling by calling `event.stopPropagation()` in a handler. A common use case is a clickable card with a delete button — you want clicking the delete button to only trigger the delete, not also the card's click handler, so you stop propagation on the button's handler.

**Q7: Why should you use `onKeyDown` instead of `onKeyPress`?**

`onKeyPress` is deprecated and does not fire for all keys — it misses Escape, Arrow keys, Tab, Delete, Backspace, function keys, and modifier keys. `onKeyDown` fires for every key press and is the recommended modern approach. `onKeyDown` also fires before the character is inserted into the input, allowing you to prevent characters from appearing (useful for input filtering). Use `onKeyUp` only when you specifically need to react after the key is released.

**Q8: How does the parent-child event communication pattern work in React?**

The parent component defines a handler function and passes it as a prop (conventionally prefixed with `on`, like `onSearch` or `onDelete`) to the child component. The child component calls this function when an event occurs, optionally passing data as arguments. This follows React's unidirectional data flow: data flows down through props, and events flow up through callbacks. The parent remains in control of the state, and the child simply notifies the parent of user interactions.

---

## Practice Exercises

**Exercise 1: Click Counter with History**

Create a component that:
- Has an "Increment" button and a "Decrement" button
- Shows the current count
- Maintains a history log of all clicks (e.g., "+1 at 2:30:15 PM", "-1 at 2:30:18 PM")
- Has a "Clear History" button
- Has an "Undo" button that reverts the last action

**Exercise 2: Keyboard Shortcut Handler**

Create a component that:
- Displays a text area
- Shows a list of keyboard shortcuts at the top (Bold: Ctrl+B, Italic: Ctrl+I, Save: Ctrl+S, Clear: Ctrl+K)
- When a shortcut is pressed, show a message like "Bold activated!" instead of performing the actual operation
- Prevent the browser's default behavior for these shortcuts
- Show which modifier keys are currently held down

**Exercise 3: Interactive Card Grid**

Create a grid of cards where:
- Each card shows a title and description
- Hovering over a card highlights it (change border and background)
- Clicking a card selects it (visually distinct from hover)
- Only one card can be selected at a time
- Pressing Escape deselects the current card
- Double-clicking a card opens it in an "expanded" view (show more details)

**Exercise 4: Custom Right-Click Menu**

Create a component with:
- A large content area
- When the user right-clicks inside the area, show a custom context menu at the mouse position
- The context menu has options like "Copy", "Paste", "Delete", "Select All"
- Clicking an option shows an alert with the action name
- Clicking anywhere outside the menu closes it
- The default browser context menu should be prevented

**Exercise 5: Drag and Drop Reorder**

Create a list where:
- Items can be reordered by clicking "Move Up" and "Move Down" buttons
- The currently selected item is highlighted
- Moving up the first item or down the last item does nothing (buttons are disabled)
- Add keyboard support: Arrow Up/Down to select, Shift+Arrow to move
- Show the current order number next to each item

**Exercise 6: Form with Real-Time Validation**

Create a registration form with:
- Username (3-20 characters, alphanumeric only)
- Email (must contain @)
- Password (minimum 8 characters, must include a number)
- Confirm Password (must match password)
- Each field validates on blur AND on change (after first blur)
- Show green check or red X next to each field
- The Submit button is disabled until all fields are valid
- Show a character count for username
- Show password strength indicator

---

## What Is Next?

You now have a solid understanding of event handling in React — from simple clicks to complex keyboard shortcuts, mouse tracking, form handling, and parent-child communication.

In Chapter 7, we will explore **Conditional Rendering and Lists** in more practical depth — building on what you learned in Chapter 3 (JSX) and Chapter 5 (state) to create components that handle loading states, error states, empty states, and dynamic data-driven UIs.
