# Chapter 10: useRef and DOM Manipulation

---

## Learning Goals

By the end of this chapter, you will be able to:

- Explain what `useRef` is and how it differs from `useState`
- Access and manipulate DOM elements directly using refs
- Manage focus, scroll position, and text selection programmatically
- Store mutable values that persist across renders without triggering re-renders
- Use refs to track previous state values
- Implement practical patterns like click-outside detection and auto-focus
- Understand when refs are appropriate and when they are a code smell
- Use `forwardRef` to pass refs to child components
- Integrate third-party DOM libraries with React using refs

---

## What Is useRef?

`useRef` is a React hook that returns a mutable object with a single property: `.current`. This object persists for the entire lifetime of the component — it survives re-renders without being reset.

```jsx
import { useRef } from "react";

function MyComponent() {
  const myRef = useRef(initialValue);

  console.log(myRef.current); // Access the value
  myRef.current = newValue;   // Update the value

  return <div>...</div>;
}
```

`useRef` has two primary uses:

1. **Accessing DOM elements** — getting a reference to an actual DOM node so you can call DOM methods on it (like `.focus()`, `.scrollIntoView()`, `.getBoundingClientRect()`).

2. **Storing mutable values** — keeping a value that persists across renders but does NOT trigger a re-render when changed (unlike state).

### useRef vs useState — The Key Difference

| Feature | `useState` | `useRef` |
|---------|-----------|---------|
| Triggers re-render when updated? | Yes | No |
| Value persists across renders? | Yes | Yes |
| Returns | `[value, setValue]` | `{ current: value }` |
| Used for | Data that affects the UI | Data that does NOT affect the UI |
| Update method | `setValue(newValue)` | `ref.current = newValue` |

**The golden rule:** If changing a value should update what the user sees on screen, use `useState`. If changing a value should NOT update the screen, use `useRef`.

Think of it this way:
- **State** is like a whiteboard in a classroom — when you change it, everyone (the UI) sees the update.
- **Ref** is like a note in your pocket — you can read and update it, but nobody else knows it changed.

---

## Accessing DOM Elements

The most common use of `useRef` is to get a reference to a DOM element. You do this by:

1. Creating a ref with `useRef(null)`.
2. Passing it to a JSX element via the `ref` attribute.
3. After the component renders, `ref.current` contains the actual DOM node.

```jsx
import { useRef, useEffect } from "react";

function TextInput() {
  const inputRef = useRef(null);

  useEffect(() => {
    // After the component renders, inputRef.current is the <input> DOM element
    console.log(inputRef.current); // <input type="text" ...>
  }, []);

  return <input type="text" ref={inputRef} />;
}
```

### Why null as the Initial Value?

We pass `null` because the DOM element does not exist yet when `useRef` is called — the component has not rendered. After React renders the component and creates the DOM elements, it sets `ref.current` to the actual DOM node. When the component unmounts, React sets `ref.current` back to `null`.

```
1. useRef(null) called           → ref.current = null
2. Component renders             → React creates <input> in DOM
3. React sets ref.current        → ref.current = <input> element
4. Component unmounts             → ref.current = null
```

---

## Focus Management

One of the most practical uses of refs — controlling which element has focus.

### Auto-Focus on Mount

```jsx
import { useRef, useEffect } from "react";

function SearchBar() {
  const searchRef = useRef(null);

  useEffect(() => {
    searchRef.current.focus();
  }, []);

  return (
    <div>
      <h2>Search</h2>
      <input
        ref={searchRef}
        type="text"
        placeholder="Start typing to search..."
        style={{ padding: "0.75rem", width: "300px", fontSize: "1rem" }}
      />
    </div>
  );
}
```

**What this code does:** When the component mounts, the `useEffect` runs and calls `.focus()` on the input element. The cursor appears in the input, and the user can start typing immediately without clicking the input first.

**Note:** React also provides the `autoFocus` JSX prop, which does the same thing for simple cases:

```jsx
<input autoFocus type="text" placeholder="Auto-focused" />
```

However, `useRef` gives you more control — you can focus conditionally, focus after an action, or focus a different element.

### Moving Focus Between Fields

```jsx
import { useRef } from "react";

function PinInput() {
  const inputRefs = [useRef(null), useRef(null), useRef(null), useRef(null)];

  function handleChange(index, event) {
    const value = event.target.value;

    // Only allow single digits
    if (value.length > 1) return;

    // Move focus to next input when a digit is entered
    if (value && index < inputRefs.length - 1) {
      inputRefs[index + 1].current.focus();
    }
  }

  function handleKeyDown(index, event) {
    // Move focus to previous input on Backspace if current input is empty
    if (event.key === "Backspace" && !event.target.value && index > 0) {
      inputRefs[index - 1].current.focus();
    }
  }

  return (
    <div>
      <h2>Enter PIN</h2>
      <div style={{ display: "flex", gap: "0.5rem" }}>
        {inputRefs.map((ref, index) => (
          <input
            key={index}
            ref={ref}
            type="text"
            maxLength={1}
            onChange={(e) => handleChange(index, e)}
            onKeyDown={(e) => handleKeyDown(index, e)}
            style={{
              width: "50px",
              height: "50px",
              textAlign: "center",
              fontSize: "1.5rem",
              border: "2px solid #e2e8f0",
              borderRadius: "8px",
            }}
          />
        ))}
      </div>
    </div>
  );
}
```

**What this code does:**

1. Four input refs — one for each PIN digit.
2. When the user types a digit, focus automatically moves to the next input.
3. When the user presses Backspace on an empty input, focus moves back to the previous input.
4. This creates a smooth PIN entry experience without the user needing to click between fields.

### Focus on Validation Error

```jsx
import { useRef, useState } from "react";

function LoginForm() {
  const emailRef = useRef(null);
  const passwordRef = useRef(null);
  const [errors, setErrors] = useState({});

  function handleSubmit(event) {
    event.preventDefault();

    const email = emailRef.current.value;
    const password = passwordRef.current.value;
    const newErrors = {};

    if (!email.trim()) {
      newErrors.email = "Email is required.";
    }
    if (!password) {
      newErrors.password = "Password is required.";
    }

    setErrors(newErrors);

    // Focus the first field with an error
    if (newErrors.email) {
      emailRef.current.focus();
    } else if (newErrors.password) {
      passwordRef.current.focus();
    } else {
      console.log("Login:", { email, password });
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: "400px", margin: "0 auto" }}>
      <h2>Login</h2>

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="email">Email:</label>
        <input
          id="email"
          ref={emailRef}
          type="email"
          style={{
            width: "100%",
            padding: "0.5rem",
            boxSizing: "border-box",
            border: `1px solid ${errors.email ? "#e53e3e" : "#e2e8f0"}`,
            borderRadius: "4px",
          }}
        />
        {errors.email && (
          <p style={{ color: "#e53e3e", fontSize: "0.875rem", margin: "0.25rem 0 0" }}>
            {errors.email}
          </p>
        )}
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="password">Password:</label>
        <input
          id="password"
          ref={passwordRef}
          type="password"
          style={{
            width: "100%",
            padding: "0.5rem",
            boxSizing: "border-box",
            border: `1px solid ${errors.password ? "#e53e3e" : "#e2e8f0"}`,
            borderRadius: "4px",
          }}
        />
        {errors.password && (
          <p style={{ color: "#e53e3e", fontSize: "0.875rem", margin: "0.25rem 0 0" }}>
            {errors.password}
          </p>
        )}
      </div>

      <button type="submit" style={{ padding: "0.75rem 1.5rem", width: "100%" }}>
        Log In
      </button>
    </form>
  );
}
```

**UX improvement:** When validation fails, the cursor jumps to the first invalid field. This is especially helpful on long forms — the user immediately knows where to fix the problem.

---

## Scrolling

### Scroll an Element into View

```jsx
import { useRef } from "react";

function ScrollDemo() {
  const topRef = useRef(null);
  const middleRef = useRef(null);
  const bottomRef = useRef(null);

  function scrollTo(ref) {
    ref.current.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }

  return (
    <div>
      <nav style={{
        position: "sticky",
        top: 0,
        backgroundColor: "white",
        padding: "0.75rem",
        borderBottom: "1px solid #e2e8f0",
        display: "flex",
        gap: "0.5rem",
        zIndex: 10,
      }}>
        <button onClick={() => scrollTo(topRef)}>Go to Top</button>
        <button onClick={() => scrollTo(middleRef)}>Go to Middle</button>
        <button onClick={() => scrollTo(bottomRef)}>Go to Bottom</button>
      </nav>

      <div ref={topRef} style={{ padding: "2rem", minHeight: "500px", backgroundColor: "#ebf8ff" }}>
        <h2>Top Section</h2>
        <p>This is the beginning of the page.</p>
      </div>

      <div ref={middleRef} style={{ padding: "2rem", minHeight: "500px", backgroundColor: "#f0fff4" }}>
        <h2>Middle Section</h2>
        <p>This is the middle of the page.</p>
      </div>

      <div ref={bottomRef} style={{ padding: "2rem", minHeight: "500px", backgroundColor: "#fff5f5" }}>
        <h2>Bottom Section</h2>
        <p>This is the end of the page.</p>
      </div>
    </div>
  );
}
```

### Scroll to Bottom (Chat Pattern)

A common pattern for chat interfaces — automatically scroll to the latest message:

```jsx
import { useState, useRef, useEffect } from "react";

function ChatWindow() {
  const [messages, setMessages] = useState([
    { id: 1, text: "Hey! How are you?", sender: "other" },
    { id: 2, text: "I'm good, thanks! Working on React.", sender: "me" },
    { id: 3, text: "Nice! What chapter are you on?", sender: "other" },
  ]);
  const [newMessage, setNewMessage] = useState("");
  const messagesEndRef = useRef(null);

  // Scroll to bottom whenever messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function handleSend(event) {
    event.preventDefault();
    if (!newMessage.trim()) return;

    setMessages((prev) => [
      ...prev,
      { id: Date.now(), text: newMessage.trim(), sender: "me" },
    ]);
    setNewMessage("");
  }

  return (
    <div style={{ maxWidth: "400px", margin: "0 auto", border: "1px solid #e2e8f0", borderRadius: "8px", overflow: "hidden" }}>
      <div style={{ backgroundColor: "#3182ce", color: "white", padding: "0.75rem 1rem" }}>
        <strong>Chat</strong>
      </div>

      <div style={{ height: "300px", overflowY: "auto", padding: "1rem" }}>
        {messages.map((msg) => (
          <div
            key={msg.id}
            style={{
              display: "flex",
              justifyContent: msg.sender === "me" ? "flex-end" : "flex-start",
              marginBottom: "0.5rem",
            }}
          >
            <div
              style={{
                backgroundColor: msg.sender === "me" ? "#3182ce" : "#e2e8f0",
                color: msg.sender === "me" ? "white" : "#2d3748",
                padding: "0.5rem 0.75rem",
                borderRadius: "12px",
                maxWidth: "75%",
              }}
            >
              {msg.text}
            </div>
          </div>
        ))}
        {/* Invisible element at the bottom — scroll target */}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSend} style={{ display: "flex", borderTop: "1px solid #e2e8f0" }}>
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder="Type a message..."
          style={{ flex: 1, padding: "0.75rem", border: "none", outline: "none" }}
        />
        <button
          type="submit"
          style={{
            padding: "0.75rem 1rem",
            backgroundColor: "#3182ce",
            color: "white",
            border: "none",
            cursor: "pointer",
          }}
        >
          Send
        </button>
      </form>
    </div>
  );
}
```

**How auto-scroll works:**

1. An invisible `<div>` sits at the bottom of the messages list with a ref attached.
2. Whenever the `messages` array changes, the `useEffect` scrolls that invisible div into view.
3. `?.` (optional chaining) prevents errors if the ref is not yet attached.

---

## Measuring DOM Elements

Use refs to get an element's dimensions and position:

```jsx
import { useRef, useState, useEffect } from "react";

function MeasureDemo() {
  const boxRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const [content, setContent] = useState("Hello, World!");

  useEffect(() => {
    if (boxRef.current) {
      const rect = boxRef.current.getBoundingClientRect();
      setDimensions({
        width: Math.round(rect.width),
        height: Math.round(rect.height),
      });
    }
  }, [content]); // Re-measure when content changes

  return (
    <div>
      <h2>Element Measurements</h2>

      <div
        ref={boxRef}
        style={{
          padding: "1rem",
          border: "2px solid #3182ce",
          borderRadius: "8px",
          display: "inline-block",
          marginBottom: "1rem",
        }}
      >
        {content}
      </div>

      <p>
        Width: {dimensions.width}px | Height: {dimensions.height}px
      </p>

      <div style={{ display: "flex", gap: "0.5rem" }}>
        <button onClick={() => setContent("Hello, World!")}>Short</button>
        <button onClick={() => setContent("This is a much longer piece of text that will make the box wider.")}>
          Long
        </button>
        <button onClick={() => setContent("Line 1\nLine 2\nLine 3")}>Multiline</button>
      </div>
    </div>
  );
}
```

**`getBoundingClientRect()`** returns an object with:
- `width`, `height` — element dimensions
- `top`, `right`, `bottom`, `left` — position relative to the viewport
- `x`, `y` — same as `left` and `top`

---

## Storing Mutable Values (Non-DOM Use)

The second major use of `useRef` — storing values that need to persist across renders but should NOT trigger re-renders when changed.

### Tracking Previous Values

```jsx
import { useState, useRef, useEffect } from "react";

function PreviousValue() {
  const [count, setCount] = useState(0);
  const previousCountRef = useRef(0);

  useEffect(() => {
    previousCountRef.current = count;
  }, [count]);

  // During render, previousCountRef.current still holds the OLD value
  // because useEffect runs AFTER render
  return (
    <div>
      <p>Current: {count}</p>
      <p>Previous: {previousCountRef.current}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
}
```

**How this works:**

```
Render 1: count = 0, previousCountRef.current = 0
  → useEffect runs: previousCountRef.current = 0

Click → setCount(1)

Render 2: count = 1, previousCountRef.current = 0 ← still old value during render
  → Display: Current: 1, Previous: 0
  → useEffect runs: previousCountRef.current = 1

Click → setCount(2)

Render 3: count = 2, previousCountRef.current = 1 ← updated by last useEffect
  → Display: Current: 2, Previous: 1
```

The trick: `useEffect` runs after render, so during the current render, the ref still holds the value from the previous render.

### Storing Timer IDs

Refs are perfect for storing timer and interval IDs — they need to persist across renders (for cleanup) but should not trigger re-renders:

```jsx
import { useState, useRef } from "react";

function Stopwatch() {
  const [time, setTime] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const intervalRef = useRef(null);

  function start() {
    if (isRunning) return;
    setIsRunning(true);

    intervalRef.current = setInterval(() => {
      setTime((prev) => prev + 10); // Update every 10ms
    }, 10);
  }

  function stop() {
    setIsRunning(false);
    clearInterval(intervalRef.current);
  }

  function reset() {
    stop();
    setTime(0);
  }

  function formatTime(ms) {
    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    const centiseconds = Math.floor((ms % 1000) / 10);
    return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}.${String(centiseconds).padStart(2, "0")}`;
  }

  return (
    <div style={{ textAlign: "center", padding: "2rem" }}>
      <p style={{ fontSize: "3rem", fontFamily: "monospace" }}>
        {formatTime(time)}
      </p>
      <div style={{ display: "flex", gap: "0.5rem", justifyContent: "center" }}>
        {!isRunning ? (
          <button onClick={start} style={{ padding: "0.5rem 1rem" }}>Start</button>
        ) : (
          <button onClick={stop} style={{ padding: "0.5rem 1rem" }}>Stop</button>
        )}
        <button onClick={reset} style={{ padding: "0.5rem 1rem" }}>Reset</button>
      </div>
    </div>
  );
}
```

**Why `useRef` instead of `useState` for the interval ID?**

The interval ID is not displayed to the user — it is just a handle for `clearInterval`. If we stored it in state, changing it would trigger an unnecessary re-render. With `useRef`, we can update `intervalRef.current` without causing any re-renders.

### Counting Renders

A debugging technique — count how many times a component renders:

```jsx
import { useRef } from "react";

function RenderCounter() {
  const renderCount = useRef(0);
  renderCount.current += 1;

  return (
    <div>
      <p>This component has rendered {renderCount.current} times.</p>
    </div>
  );
}
```

**Why this works:** The ref persists across renders. Each render increments the count by 1. Because updating a ref does not trigger a re-render, this does not cause an infinite loop (unlike `useState` would).

### Tracking if Component Is Mounted

Useful for preventing state updates on unmounted components:

```jsx
import { useRef, useEffect } from "react";

function useIsMounted() {
  const isMounted = useRef(false);

  useEffect(() => {
    isMounted.current = true;

    return () => {
      isMounted.current = false;
    };
  }, []);

  return isMounted;
}

// Usage:
function DataFetcher({ url }) {
  const [data, setData] = useState(null);
  const isMounted = useIsMounted();

  useEffect(() => {
    fetch(url)
      .then((res) => res.json())
      .then((result) => {
        if (isMounted.current) {
          setData(result);
        }
      });
  }, [url, isMounted]);

  return <div>{data ? JSON.stringify(data) : "Loading..."}</div>;
}
```

---

## Click Outside Detection

A very common pattern — closing a dropdown or modal when the user clicks outside of it:

```jsx
import { useState, useRef, useEffect } from "react";

function Dropdown() {
  const [isOpen, setIsOpen] = useState(false);
  const [selected, setSelected] = useState("Select an option");
  const dropdownRef = useRef(null);

  const options = ["Apple", "Banana", "Cherry", "Date", "Elderberry"];

  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  function handleSelect(option) {
    setSelected(option);
    setIsOpen(false);
  }

  return (
    <div ref={dropdownRef} style={{ position: "relative", width: "200px" }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          width: "100%",
          padding: "0.75rem",
          textAlign: "left",
          border: "1px solid #e2e8f0",
          borderRadius: "6px",
          backgroundColor: "white",
          cursor: "pointer",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <span>{selected}</span>
        <span style={{ transform: isOpen ? "rotate(180deg)" : "rotate(0)", transition: "transform 0.2s" }}>
          ▼
        </span>
      </button>

      {isOpen && (
        <ul
          style={{
            position: "absolute",
            top: "100%",
            left: 0,
            right: 0,
            margin: "0.25rem 0 0",
            padding: 0,
            listStyle: "none",
            border: "1px solid #e2e8f0",
            borderRadius: "6px",
            backgroundColor: "white",
            boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
            zIndex: 10,
          }}
        >
          {options.map((option) => (
            <li
              key={option}
              onClick={() => handleSelect(option)}
              style={{
                padding: "0.5rem 0.75rem",
                cursor: "pointer",
                backgroundColor: selected === option ? "#ebf8ff" : "transparent",
              }}
              onMouseEnter={(e) => { e.target.style.backgroundColor = "#f7fafc"; }}
              onMouseLeave={(e) => {
                e.target.style.backgroundColor = selected === option ? "#ebf8ff" : "transparent";
              }}
            >
              {option}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

**How click-outside detection works:**

1. A ref is attached to the dropdown container (button + menu).
2. A `mousedown` event listener is added to the document.
3. When a click occurs anywhere, we check if the click target is inside the dropdown using `dropdownRef.current.contains(event.target)`.
4. If the click is outside, we close the dropdown.
5. The listener is only added when the dropdown is open, and cleaned up when it closes or unmounts.

---

## Text Selection and Clipboard

```jsx
import { useRef, useState } from "react";

function CopyableText() {
  const textRef = useRef(null);
  const [copied, setCopied] = useState(false);

  function handleCopy() {
    // Select all text in the input
    textRef.current.select();

    // Copy to clipboard
    navigator.clipboard.writeText(textRef.current.value).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  return (
    <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
      <input
        ref={textRef}
        type="text"
        readOnly
        value="npm install react"
        style={{ flex: 1, padding: "0.5rem", fontFamily: "monospace" }}
      />
      <button onClick={handleCopy} style={{ padding: "0.5rem 1rem", whiteSpace: "nowrap" }}>
        {copied ? "Copied!" : "Copy"}
      </button>
    </div>
  );
}
```

---

## forwardRef — Passing Refs to Child Components

By default, you cannot attach a `ref` to a custom component — only to DOM elements:

```jsx
// ❌ This does NOT work — CustomInput is not a DOM element
function CustomInput(props) {
  return <input type="text" {...props} />;
}

function Parent() {
  const inputRef = useRef(null);
  return <CustomInput ref={inputRef} />;
  // Warning: Function components cannot be given refs
}
```

To make this work, the child component must use `forwardRef` to "forward" the ref to an inner DOM element:

```jsx
import { forwardRef, useRef } from "react";

const CustomInput = forwardRef(function CustomInput(props, ref) {
  return (
    <div style={{ marginBottom: "1rem" }}>
      <label htmlFor={props.id} style={{ display: "block", marginBottom: "0.25rem" }}>
        {props.label}
      </label>
      <input
        ref={ref}  // Forward the ref to the actual <input> element
        id={props.id}
        type={props.type || "text"}
        style={{
          width: "100%",
          padding: "0.5rem",
          border: "1px solid #e2e8f0",
          borderRadius: "4px",
          boxSizing: "border-box",
        }}
        {...props}
      />
    </div>
  );
});

function LoginForm() {
  const emailRef = useRef(null);
  const passwordRef = useRef(null);

  function handleSubmit(event) {
    event.preventDefault();

    if (!emailRef.current.value) {
      emailRef.current.focus(); // This works because ref is forwarded!
      return;
    }

    console.log("Email:", emailRef.current.value);
    console.log("Password:", passwordRef.current.value);
  }

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: "400px", margin: "0 auto" }}>
      <h2>Login</h2>
      <CustomInput ref={emailRef} id="email" label="Email" type="email" />
      <CustomInput ref={passwordRef} id="password" label="Password" type="password" />
      <button type="submit" style={{ padding: "0.75rem 1.5rem" }}>Log In</button>
    </form>
  );
}
```

**How `forwardRef` works:**

1. `forwardRef` wraps a component function and gives it a second parameter: `ref`.
2. The component passes that `ref` to a DOM element inside it.
3. Now the parent can use `ref.current` to access the inner DOM element directly.

**When you need `forwardRef`:**
- When a parent component needs to focus, scroll to, or measure a DOM element inside a child component.
- When building reusable input components that should support refs.
- When integrating with libraries that need DOM access.

---

## Practical Mini Project: Image Gallery with Scroll Controls

```jsx
import { useRef, useState } from "react";

function ImageGallery() {
  const scrollContainerRef = useRef(null);
  const [showLeftArrow, setShowLeftArrow] = useState(false);
  const [showRightArrow, setShowRightArrow] = useState(true);

  const images = [
    { id: 1, color: "#e53e3e", label: "Red" },
    { id: 2, color: "#dd6b20", label: "Orange" },
    { id: 3, color: "#d69e2e", label: "Yellow" },
    { id: 4, color: "#38a169", label: "Green" },
    { id: 5, color: "#3182ce", label: "Blue" },
    { id: 6, color: "#805ad5", label: "Purple" },
    { id: 7, color: "#d53f8c", label: "Pink" },
    { id: 8, color: "#2d3748", label: "Dark" },
    { id: 9, color: "#718096", label: "Gray" },
    { id: 10, color: "#38b2ac", label: "Teal" },
  ];

  function handleScroll() {
    const container = scrollContainerRef.current;
    if (!container) return;

    setShowLeftArrow(container.scrollLeft > 0);
    setShowRightArrow(
      container.scrollLeft < container.scrollWidth - container.clientWidth - 1
    );
  }

  function scroll(direction) {
    const container = scrollContainerRef.current;
    if (!container) return;

    const scrollAmount = 220; // Slightly more than card width
    container.scrollBy({
      left: direction === "left" ? -scrollAmount : scrollAmount,
      behavior: "smooth",
    });
  }

  return (
    <div style={{ maxWidth: "600px", margin: "0 auto", position: "relative" }}>
      <h2>Gallery</h2>

      {/* Left arrow */}
      {showLeftArrow && (
        <button
          onClick={() => scroll("left")}
          style={{
            position: "absolute",
            left: "-20px",
            top: "50%",
            transform: "translateY(-50%)",
            width: "40px",
            height: "40px",
            borderRadius: "50%",
            border: "1px solid #e2e8f0",
            backgroundColor: "white",
            cursor: "pointer",
            fontSize: "1.25rem",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
            zIndex: 2,
          }}
        >
          ←
        </button>
      )}

      {/* Scrollable container */}
      <div
        ref={scrollContainerRef}
        onScroll={handleScroll}
        style={{
          display: "flex",
          gap: "1rem",
          overflowX: "auto",
          scrollBehavior: "smooth",
          padding: "1rem 0",
          scrollbarWidth: "none", // Firefox
        }}
      >
        {images.map((img) => (
          <div
            key={img.id}
            style={{
              minWidth: "200px",
              height: "150px",
              backgroundColor: img.color,
              borderRadius: "12px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "white",
              fontSize: "1.25rem",
              fontWeight: "bold",
              flexShrink: 0,
            }}
          >
            {img.label}
          </div>
        ))}
      </div>

      {/* Right arrow */}
      {showRightArrow && (
        <button
          onClick={() => scroll("right")}
          style={{
            position: "absolute",
            right: "-20px",
            top: "50%",
            transform: "translateY(-50%)",
            width: "40px",
            height: "40px",
            borderRadius: "50%",
            border: "1px solid #e2e8f0",
            backgroundColor: "white",
            cursor: "pointer",
            fontSize: "1.25rem",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
            zIndex: 2,
          }}
        >
          →
        </button>
      )}
    </div>
  );
}

export default ImageGallery;
```

**Ref concepts demonstrated:**

| Concept | Where Used |
|---------|------------|
| DOM ref | `scrollContainerRef` on the scrollable container |
| Reading DOM properties | `scrollLeft`, `scrollWidth`, `clientWidth` |
| Calling DOM methods | `container.scrollBy()` |
| Conditional arrows | Based on scroll position from ref |

---

## When NOT to Use Refs

Refs give you direct DOM access, but React works best when you let it manage the DOM. Overusing refs is an anti-pattern.

**Do NOT use refs to:**

```jsx
// ❌ Set text content — use state and JSX
myRef.current.textContent = "Hello";

// ❌ Change styles — use state and inline styles or CSS classes
myRef.current.style.color = "red";

// ❌ Add/remove CSS classes — use state and className
myRef.current.classList.add("active");

// ❌ Show/hide elements — use conditional rendering
myRef.current.style.display = "none";

// ❌ Read input values on every change — use controlled components
const value = myRef.current.value; // in onChange handler
```

**DO use refs to:**

```jsx
// ✅ Focus management
inputRef.current.focus();

// ✅ Scroll control
elementRef.current.scrollIntoView();

// ✅ Measurements
const rect = elementRef.current.getBoundingClientRect();

// ✅ Integrating with non-React libraries
const chart = new ChartLibrary(canvasRef.current);

// ✅ Storing values that don't affect rendering
intervalRef.current = setInterval(...);

// ✅ Media playback
videoRef.current.play();
videoRef.current.pause();
```

**The rule of thumb:** If you can do it with state and JSX, do it with state and JSX. Use refs only for things that React's declarative model cannot handle — primarily imperative DOM operations and non-visual mutable data.

---

## Common Mistakes

1. **Reading refs during render (before they are set).**

   ```jsx
   // ❌ ref.current is null during the first render
   function Bad() {
     const ref = useRef(null);
     console.log(ref.current.textContent); // TypeError: null has no property 'textContent'
     return <p ref={ref}>Hello</p>;
   }

   // ✅ Access refs in useEffect or event handlers (after render)
   function Good() {
     const ref = useRef(null);
     useEffect(() => {
       console.log(ref.current.textContent); // "Hello"
     }, []);
     return <p ref={ref}>Hello</p>;
   }
   ```

2. **Using refs when state is the right tool.**

   ```jsx
   // ❌ Updating the DOM directly — React does not know about this change
   function Bad() {
     const ref = useRef(null);
     function handleClick() {
       ref.current.textContent = "Updated!"; // React is bypassed
     }
     return <p ref={ref} onClick={handleClick}>Click me</p>;
   }

   // ✅ Use state — React manages the DOM update
   function Good() {
     const [text, setText] = useState("Click me");
     return <p onClick={() => setText("Updated!")}>{text}</p>;
   }
   ```

3. **Forgetting that ref updates do not trigger re-renders.**

   ```jsx
   // ❌ The display never updates because ref changes are invisible to React
   function Bad() {
     const countRef = useRef(0);
     function handleClick() {
       countRef.current += 1;
       // The UI still shows 0! No re-render happens.
     }
     return <p onClick={handleClick}>Count: {countRef.current}</p>;
   }

   // ✅ Use state for values that should be displayed
   function Good() {
     const [count, setCount] = useState(0);
     return <p onClick={() => setCount(c => c + 1)}>Count: {count}</p>;
   }
   ```

4. **Trying to pass `ref` to a function component without `forwardRef`.**

   ```jsx
   // ❌ Warning: Function components cannot be given refs
   function Child(props) {
     return <input {...props} />;
   }
   <Child ref={myRef} />

   // ✅ Use forwardRef
   const Child = forwardRef(function Child(props, ref) {
     return <input ref={ref} {...props} />;
   });
   ```

5. **Creating refs inside loops or conditions.**

   ```jsx
   // ❌ Hooks cannot be called inside loops
   items.map((item) => {
     const ref = useRef(null); // Hook called in loop — ERROR
     return <div ref={ref}>{item}</div>;
   });

   // ✅ Use a ref that holds an array or map
   const itemRefs = useRef([]);
   items.map((item, index) => (
     <div ref={(el) => { itemRefs.current[index] = el; }}>{item}</div>
   ));
   ```

---

## Best Practices

1. **Use refs sparingly.** If React's declarative model (state + JSX) can handle it, prefer that over direct DOM manipulation.

2. **Always initialize DOM refs with `null`:** `useRef(null)`. This makes it clear that the ref will hold a DOM element.

3. **Access refs in `useEffect` or event handlers** — never during render, because the DOM element might not exist yet.

4. **Use `forwardRef` when building reusable components** that other developers might need to attach refs to. This makes your component API flexible.

5. **Do not store values in refs that should trigger UI updates.** If the user should see a change, use state.

6. **Clean up side effects that use refs.** If you set up an interval and store the ID in a ref, make sure to clear it on unmount.

7. **Use callback refs for dynamic lists** when you need refs for items that are generated by `map()`.

---

## Summary

In this chapter, you learned:

- **`useRef`** creates a mutable object (`{ current: value }`) that persists across renders without triggering re-renders.
- **DOM access** — attach a ref to a JSX element to get the underlying DOM node. Use it for focus management, scrolling, measurements, and media control.
- **Focus management** — `.focus()`, `.select()`, auto-focus on mount, focus on validation error, PIN input navigation.
- **Scrolling** — `.scrollIntoView()`, `.scrollBy()`, auto-scroll to bottom (chat pattern), scroll position tracking.
- **Measuring elements** — `.getBoundingClientRect()` returns width, height, and position.
- **Mutable storage** — store timer IDs, previous values, render counts, and mounted status without re-renders.
- **Click-outside detection** — combine refs with document event listeners to detect clicks outside a component.
- **`forwardRef`** — pass refs through custom components to inner DOM elements.
- **When NOT to use refs** — never for things React's state and JSX can handle (text content, styles, visibility, class names).

---

## Interview Questions

**Q1: What is `useRef` and how does it differ from `useState`?**

`useRef` returns a mutable object `{ current: value }` that persists for the lifetime of the component. Unlike `useState`, updating `ref.current` does not trigger a re-render. Use `useState` for values that affect what the user sees (the UI), and `useRef` for values that need to persist but should not cause re-renders — like DOM references, timer IDs, or previous values.

**Q2: Why do DOM refs start as `null`?**

Because when `useRef(null)` is called during the component function's execution, the DOM does not exist yet — React has not rendered the component. After React creates the DOM elements and paints them to the screen, it sets `ref.current` to the actual DOM node. When the component unmounts, React sets it back to `null`. The initial `null` value reflects the fact that no DOM element is available at creation time.

**Q3: Can you attach a ref to a function component? How?**

Not directly — function components do not have a DOM node to reference. You must use `forwardRef` to wrap the child component and forward the ref to an internal DOM element. The child receives `ref` as a second parameter (after `props`) and passes it to a DOM element via the `ref` prop. This lets the parent access the inner DOM element through its ref.

**Q4: What is a callback ref?**

Instead of passing a ref object to the `ref` prop, you can pass a function. React calls this function with the DOM element when the component mounts and with `null` when it unmounts. This is useful for dynamic lists where you need refs for multiple elements generated in a loop, since hooks cannot be called inside loops: `ref={(el) => { itemRefs.current[index] = el; }}`.

**Q5: When should you use `useRef` instead of `useState`?**

Use `useRef` when: the value does not affect the rendered output (timer IDs, previous values, render counts), you need to access DOM elements (focus, scroll, measure), you need to store a mutable value without causing re-renders, or you need to persist a value across renders for use in closures (like intervals or timeouts). Use `useState` when changing the value should update what the user sees on screen.

**Q6: How do you implement click-outside detection in React?**

Attach a ref to the element you want to monitor. Add a `mousedown` event listener to `document` (inside a `useEffect`). In the listener, check if the click target is inside your element using `ref.current.contains(event.target)`. If it is not inside, perform the desired action (e.g., close a dropdown). Clean up the listener in the `useEffect` return function to prevent memory leaks.

---

## Practice Exercises

**Exercise 1: Auto-Expanding Textarea**

Create a textarea that:
- Automatically grows taller as the user types (no scroll bar)
- Uses a ref to measure and set the textarea's height
- Has a minimum height of 3 rows
- Has a maximum height (after which it scrolls)
- Shows a character count below

**Exercise 2: Tooltip Component**

Build a tooltip that:
- Appears when hovering over a trigger element
- Positions itself above, below, left, or right based on available space
- Uses refs to measure both the trigger and tooltip elements
- Uses `getBoundingClientRect()` to calculate position
- Disappears when the mouse leaves

**Exercise 3: Video Player Controls**

Create a custom video player with:
- Play/Pause button using `videoRef.current.play()` and `.pause()`
- A progress bar showing current time (use ref to read `currentTime` and `duration`)
- Volume control slider
- Fullscreen toggle using `videoRef.current.requestFullscreen()`
- Mute/unmute toggle

**Exercise 4: Infinite Scroll with Intersection Observer**

Build a component that:
- Shows a list of items
- Uses a ref on a sentinel element at the bottom
- Uses `IntersectionObserver` to detect when the sentinel is visible
- Loads more items when the sentinel enters the viewport
- Shows a loading indicator during loading

**Exercise 5: Code Snippet with Copy Button**

Create a code display component that:
- Shows formatted code in a `<pre>` block
- Has a "Copy" button that copies the code to clipboard
- Uses a ref to select the code text
- Shows "Copied!" feedback for 2 seconds
- Supports syntax highlighting (just different colors for keywords)

---

## What Is Next?

You now understand `useRef` and how to interact with the DOM when React's declarative approach is not enough. You can manage focus, scroll elements, measure dimensions, detect clicks outside, and store mutable values efficiently.

In Chapter 11, we will explore **useMemo, useCallback, and Performance Optimization** — learning how to prevent unnecessary re-renders and optimize your components for smooth performance, even with large amounts of data.
