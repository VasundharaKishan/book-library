# Chapter 28: Refs — Remembering Without Re-rendering

---

## What You Will Learn

- What `useRef` is and how it works
- The key difference between state and refs
- When to use refs instead of state
- How to access DOM elements (like input fields) using refs
- Practical examples: auto-focusing an input and building a stopwatch
- The rules for using refs safely

## Why This Chapter Matters

In the last chapter, you learned that every time state changes, React re-renders your component. That is usually what you want. You change data, and the screen updates.

But sometimes you need to remember a value **without** updating the screen. For example:

- You start a timer and need to remember its ID so you can stop it later.
- You want to focus an input field when the page loads.
- You want to track how many times a component rendered, without causing extra renders.

Using state for these would cause unnecessary re-renders. That is where **refs** come in. A ref is like a sticky note your component keeps in its pocket. It can read and update the note anytime, but changing the note does not cause the screen to re-render.

---

## What Is useRef?

`useRef` is a React Hook that gives you a box to store a value. This box has one special property: changing what is inside the box does **not** cause a re-render.

### The Sticky Note Analogy

Imagine two ways to write something down:

1. **A whiteboard in a classroom** (this is state). When you change what is on the whiteboard, everyone looks up and reads the new content. The "screen" updates.

2. **A sticky note in your pocket** (this is a ref). You can write anything on it, change it, erase it, and write again. Nobody else notices because it is in your pocket. No "screen update."

### Creating a Ref

```jsx
import { useRef } from "react";

function MyComponent() {
  const myRef = useRef(0);

  console.log(myRef.current); // 0
}
```

**Line-by-line explanation:**

- **Line 1:** We import `useRef` from React.
- **Line 4:** We create a ref with an initial value of 0. The ref is an object that looks like this: `{ current: 0 }`.
- **Line 6:** To read the value, you use `myRef.current`.

The ref is an object with a single property called `current`. You read and write using `.current`:

```
+-------------------------------+
|  What a ref looks like:       |
|                                |
|  myRef = {                    |
|    current: 0    <-- your value|
|  }                             |
|                                |
|  Read:  myRef.current          |
|  Write: myRef.current = 5     |
+-------------------------------+
```

---

## Ref vs State: A Side-by-Side Comparison

Here is the most important difference:

| Feature | State (`useState`) | Ref (`useRef`) |
|---------|-------------------|----------------|
| Causes re-render when changed? | **Yes** | **No** |
| Returns | `[value, setValue]` | `{ current: value }` |
| How to read | `value` | `ref.current` |
| How to update | `setValue(newValue)` | `ref.current = newValue` |
| When to use | Data that should be displayed on screen | Data you need to remember but not display |

### Seeing the Difference in Action

Here is a component that uses **state** to count clicks:

```jsx
import { useState } from "react";

function StateCounter() {
  const [count, setCount] = useState(0);

  function handleClick() {
    setCount(count + 1);
  }

  return (
    <div>
      <p>You clicked {count} times</p>
      <button onClick={handleClick}>Click me</button>
    </div>
  );
}
```

**Expected output (after 3 clicks):**

```
You clicked 3 times
[Click me]
```

Every click updates the screen. The number changes visibly.

Now here is a component that uses a **ref** to count clicks:

```jsx
import { useRef } from "react";

function RefCounter() {
  const countRef = useRef(0);

  function handleClick() {
    countRef.current = countRef.current + 1;
    alert("You clicked " + countRef.current + " times");
  }

  return (
    <div>
      <p>Check the alert for the count</p>
      <button onClick={handleClick}>Click me</button>
    </div>
  );
}
```

**Line-by-line explanation:**

- **Line 4:** We create a ref starting at 0.
- **Line 7:** We update the ref directly. No setter function needed. Just assign to `.current`.
- **Line 8:** We show the count in an alert. The ref has the latest value.

**Expected output (after 3 clicks):**

The screen always says "Check the alert for the count." It never changes. But each alert shows the updated count: 1, then 2, then 3.

The ref remembers the value. But the screen does not update because refs do not trigger re-renders.

---

## When to Use Refs

Use refs when you need to remember something but do not need to show it on the screen. Common situations:

```
+---------------------------------------------------+
|  Good reasons to use a ref:                       |
|                                                    |
|  1. Storing a timer ID (setTimeout, setInterval)  |
|  2. Accessing a DOM element (input, div, etc.)    |
|  3. Storing a value from the previous render      |
|  4. Storing values that do not affect the display |
+---------------------------------------------------+
```

If the value should appear on the screen, use state. If it is behind-the-scenes bookkeeping, use a ref.

---

## Accessing DOM Elements with Refs

One of the most common uses of refs is to access an actual HTML element on the page. For example, you might want to focus an input field, scroll to an element, or measure an element's size.

### How It Works

1. Create a ref.
2. Attach it to a JSX element using the `ref` attribute.
3. React fills in `ref.current` with the actual DOM element.

```
+---------------------------------------------------+
|  How DOM refs work:                               |
|                                                    |
|  1. const inputRef = useRef(null);                |
|     (Create an empty box)                          |
|                                                    |
|  2. <input ref={inputRef} />                      |
|     (Tell React: "Put the input element           |
|      in this box")                                 |
|                                                    |
|  3. inputRef.current                              |
|     (Now this IS the <input> element.             |
|      You can call .focus(), .scrollIntoView(),     |
|      etc.)                                         |
+---------------------------------------------------+
```

### Example: Auto-Focus an Input Field

When a search page loads, you often want the search box to be focused automatically so the user can start typing right away.

```jsx
import { useRef, useEffect } from "react";

function SearchPage() {
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current.focus();
  }, []);

  return (
    <div>
      <h1>Search</h1>
      <input ref={inputRef} type="text" placeholder="Type to search..." />
    </div>
  );
}
```

**Line-by-line explanation:**

- **Line 4:** We create a ref starting as `null` (empty). We use `null` because the input element does not exist yet when the component first starts running.
- **Lines 6-8:** After the component appears on screen, `useEffect` runs. By this time, React has put the actual input element into `inputRef.current`. We call `.focus()` on it to make the cursor appear in the input.
- **Line 13:** We attach the ref to the input using `ref={inputRef}`. This tells React, "When you create this input element, store it in `inputRef.current`."

**Expected output:**

When the page loads, you see a search box and the cursor is already blinking inside it. You can start typing immediately without clicking on it first.

### Example: Scrolling to an Element

```jsx
import { useRef } from "react";

function LongPage() {
  const bottomRef = useRef(null);

  function scrollToBottom() {
    bottomRef.current.scrollIntoView({ behavior: "smooth" });
  }

  return (
    <div>
      <button onClick={scrollToBottom}>Go to bottom</button>
      <div style={{ height: "2000px", background: "#f0f0f0" }}>
        <p>Lots of content here...</p>
      </div>
      <p ref={bottomRef}>You reached the bottom!</p>
    </div>
  );
}
```

**Line-by-line explanation:**

- **Line 4:** We create a ref for the bottom element.
- **Line 7:** We call `scrollIntoView()` to smoothly scroll to that element.
- **Line 16:** We attach the ref to the paragraph at the bottom.

**Expected output:** When you click the button, the page smoothly scrolls down to the bottom paragraph.

---

## Example: A Stopwatch

This is a classic example that shows why refs are important. A stopwatch needs a timer (using `setInterval`), and you need to remember the timer ID so you can stop it later. But the timer ID should not be shown on screen, so it does not need to be state.

```jsx
import { useState, useRef } from "react";

function Stopwatch() {
  const [seconds, setSeconds] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const intervalRef = useRef(null);

  function handleStart() {
    if (isRunning) return;
    setIsRunning(true);

    intervalRef.current = setInterval(() => {
      setSeconds((prev) => prev + 1);
    }, 1000);
  }

  function handleStop() {
    setIsRunning(false);
    clearInterval(intervalRef.current);
    intervalRef.current = null;
  }

  function handleReset() {
    setIsRunning(false);
    clearInterval(intervalRef.current);
    intervalRef.current = null;
    setSeconds(0);
  }

  return (
    <div>
      <h2>{seconds} seconds</h2>
      <button onClick={handleStart}>Start</button>
      <button onClick={handleStop}>Stop</button>
      <button onClick={handleReset}>Reset</button>
    </div>
  );
}
```

**Line-by-line explanation:**

- **Line 4:** `seconds` is state because it is displayed on screen. When it changes, the screen needs to update.
- **Line 5:** `isRunning` is state because we use it to show/hide buttons or change behavior.
- **Line 6:** `intervalRef` is a ref. It stores the timer ID. The timer ID is never shown on screen. It is just bookkeeping so we can stop the timer later.
- **Lines 8-15:** When the user clicks Start, we begin a timer that adds 1 to `seconds` every 1000 milliseconds (1 second). We store the timer ID in `intervalRef.current`. Notice we use the updater function `(prev) => prev + 1` so each update gets the latest value.
- **Lines 17-21:** When the user clicks Stop, we clear the timer using the ID stored in the ref. We set the ref back to `null` to clean up.
- **Lines 23-28:** Reset stops the timer and sets seconds back to 0.

**Expected output:**

```
0 seconds
[Start] [Stop] [Reset]
```

After clicking Start, the number counts up: 1, 2, 3, 4... Click Stop and it freezes. Click Reset and it goes back to 0.

### Why We Use a Ref for the Timer ID

What if we used state instead?

```jsx
const [intervalId, setIntervalId] = useState(null);
```

This would work, but every time we set the interval ID, it would cause a re-render. That is wasteful. The interval ID is not shown on screen. Nobody sees it. There is no reason to re-render the component just because we stored a timer ID.

Using a ref is more efficient. We remember the value without causing any extra work for React.

---

## Rules for Using Refs

Refs are powerful, but they come with an important rule:

### Do Not Read or Write Refs During Rendering

```
+---------------------------------------------------+
|  THE REF RULE                                     |
|                                                    |
|  Do NOT read or write ref.current while your      |
|  component is rendering (returning JSX).           |
|                                                    |
|  OK in: event handlers, useEffect                 |
|  NOT OK in: the main body of the component        |
|  that runs during rendering                        |
+---------------------------------------------------+
```

**Bad example (reading ref during render):**

```jsx
function BadComponent() {
  const countRef = useRef(0);
  countRef.current = countRef.current + 1;  // BAD! This runs during render.

  return <p>Rendered {countRef.current} times</p>;  // BAD! Reading ref during render.
}
```

**Why this is bad:** The component is not pure anymore. It changes a value and reads a changing value during rendering. React might call this function multiple times (like in StrictMode), and you would get unexpected results.

**Good example (reading ref in event handler):**

```jsx
function GoodComponent() {
  const countRef = useRef(0);

  function handleClick() {
    countRef.current = countRef.current + 1;  // OK! This is in an event handler.
    alert("Clicks: " + countRef.current);      // OK! Reading ref in event handler.
  }

  return <button onClick={handleClick}>Click me</button>;
}
```

This is fine because the ref is read and written inside an event handler, not during rendering.

**Exception:** It is OK to set a ref during the first render if you only do it once:

```jsx
function MyComponent() {
  const startTime = useRef(null);

  if (startTime.current === null) {
    startTime.current = new Date();  // OK: only happens once
  }

  // ...
}
```

---

## Ref vs State: A Quick Decision Guide

When you need to remember a value in a component, ask yourself:

```
+---------------------------------------------------+
|  "Does this value need to show on the screen?"    |
|                                                    |
|  YES --> Use useState                             |
|          (changes trigger re-renders)              |
|                                                    |
|  NO  --> Use useRef                               |
|          (changes are silent)                      |
+---------------------------------------------------+
```

Some examples:

| What you are storing | Use state or ref? | Why |
|---------------------|-------------------|-----|
| A counter shown on screen | State | It is displayed |
| The text in an input field | State | It is displayed |
| A timer ID from setInterval | Ref | Not displayed |
| A reference to an input element | Ref | Not displayed |
| Whether a form has been submitted | State | Affects what is shown |
| The previous value of a prop | Ref | Not displayed |

---

## Quick Summary

- `useRef` creates a box (`{ current: value }`) that persists across renders but does not cause re-renders when changed.
- State is for data that should appear on screen. Refs are for behind-the-scenes bookkeeping.
- You read and write refs using `.current`. There is no setter function.
- To access a DOM element, create a ref and attach it with `ref={myRef}`. React fills in `.current` with the actual element.
- Common uses: storing timer IDs, focusing input fields, scrolling to elements, and remembering values that do not need to trigger re-renders.
- Do not read or write refs during rendering. Use them in event handlers and `useEffect`.

## Key Points to Remember

1. `useRef` returns `{ current: initialValue }`. Change it with `ref.current = newValue`.
2. Changing a ref does NOT cause a re-render. That is the key difference from state.
3. Use refs for values that do not appear on screen (timer IDs, DOM elements, previous values).
4. Attach a ref to a JSX element with `ref={myRef}` to get the actual DOM element.
5. Do not read or write `ref.current` during rendering. Use event handlers or useEffect instead.

## Practice Questions

1. What is the main difference between `useState` and `useRef`?
2. You need to store a timer ID from `setInterval`. Should you use state or a ref? Why?
3. How do you attach a ref to an HTML element in JSX?
4. Why should you not read or write `ref.current` during rendering?
5. A ref starts as `useRef(null)`. After you attach it to an `<input>` element, what does `ref.current` contain?

## Exercises

1. Create a component with an input field and a button that says "Focus." When the user clicks the button, the cursor should jump into the input field. Use `useRef` to access the input element and call `.focus()` on it.

2. Build a stopwatch component with Start, Stop, and Reset buttons. Display the elapsed time in seconds on the screen. Use state for the displayed time and a ref for the interval ID. Make sure the Reset button stops the timer and sets the time back to 0.

3. Create a component that tracks how many times a button has been clicked, but does NOT show the count on screen. Instead, when the user clicks a separate "Show Count" button, display the count in an alert. Use a ref to store the count silently, without causing re-renders on each click.

---

## What Is Coming Next?

You now know how to remember values with both state and refs. In the next chapter, we will learn about `useReducer`, a different way to manage state that works especially well when your state logic gets more complex. Think of it as upgrading from a simple calculator to a more organized system for handling state changes.
