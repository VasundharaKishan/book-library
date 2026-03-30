# Chapter 8: useEffect and the Component Lifecycle

---

## Learning Goals

By the end of this chapter, you will be able to:

- Explain what side effects are and why they need special handling in React
- Use `useEffect` to run code after a component renders
- Control when effects run using the dependency array
- Clean up effects to prevent memory leaks and stale behavior
- Fetch data from APIs using `useEffect`
- Set up and tear down timers, intervals, and event listeners
- Understand the component lifecycle in functional components
- Compare class component lifecycle methods with hooks
- Avoid infinite loops and other common `useEffect` pitfalls
- Implement practical patterns like debouncing, polling, and window resize listeners

---

## What Are Side Effects?

In React, a component's main job is to take data (props and state) and return JSX. This is called **rendering** — it is a pure calculation. You give the component inputs, and it returns a predictable output.

But applications need to do more than just display things. They need to:

- Fetch data from a server
- Update the page title
- Start a timer or interval
- Listen for window resize or scroll events
- Write to local storage
- Connect to a WebSocket
- Track analytics
- Log information

These actions are called **side effects** (or just "effects") because they are operations that reach outside the component and interact with the outside world. They are "side" effects because they happen on the side — they are not part of the rendering itself.

### Why Side Effects Need Special Handling

Consider this problematic example:

```jsx
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);

  // ❌ WRONG: Fetching data directly during render
  fetch(`https://api.example.com/users/${userId}`)
    .then((response) => response.json())
    .then((data) => setUser(data));

  return <div>{user ? user.name : "Loading..."}</div>;
}
```

**Why this is broken:**

1. `fetch` runs every time the component renders.
2. When the data arrives, `setUser(data)` updates state.
3. The state update triggers a re-render.
4. The re-render calls `fetch` again.
5. Steps 2-4 repeat forever — **infinite loop**.

Even without the infinite loop problem, side effects during rendering can:
- Slow down rendering (the browser waits for the effect instead of painting)
- Run at the wrong time (before the DOM is ready)
- Run more often than intended (on every render)

**The solution:** React provides `useEffect` — a hook that lets you run side effects *after* the component has rendered and the DOM has been updated. This keeps rendering fast and predictable, while giving you a controlled place to perform side effects.

---

## The useEffect Hook

### Basic Syntax

```jsx
import { useEffect } from "react";

useEffect(() => {
  // This code runs after the component renders
  console.log("Component rendered!");
});
```

`useEffect` takes a function (called the "effect function") as its first argument. React calls this function after the component's output has been committed to the DOM.

### When Does useEffect Run?

By default (without a dependency array), `useEffect` runs after **every render** — including the first render and every re-render caused by state or prop changes.

```jsx
import { useState, useEffect } from "react";

function Counter() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    console.log(`Effect ran! Count is ${count}`);
  });

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
}

// Console output:
// (initial render) Effect ran! Count is 0
// (click button)   Effect ran! Count is 1
// (click button)   Effect ran! Count is 2
```

### The Timeline of a Render with useEffect

```
1. State changes (e.g., setCount(1))
      │
      ▼
2. React calls the component function
   → computes the new JSX
      │
      ▼
3. React updates the DOM
   → the screen shows the new content
      │
      ▼
4. React runs the useEffect callback
   → side effects happen AFTER the screen updates
```

This ordering is important: effects run **after** the browser has painted. The user sees the updated UI immediately — the effect does not block the screen update.

---

## The Dependency Array

The second argument to `useEffect` is the **dependency array** — it controls when the effect runs.

### Three Variations

```jsx
// 1. No dependency array: runs after EVERY render
useEffect(() => {
  console.log("Runs after every render");
});

// 2. Empty dependency array: runs only ONCE (after first render)
useEffect(() => {
  console.log("Runs once, after initial render");
}, []);

// 3. With dependencies: runs when any dependency changes
useEffect(() => {
  console.log(`Runs when count or name changes`);
}, [count, name]);
```

Let us examine each in detail.

### Variation 1: No Dependency Array — Run After Every Render

```jsx
useEffect(() => {
  document.title = `Count: ${count}`;
});
```

This updates the page title on every render. It is rarely the best choice because most effects do not need to run on every single render.

**When to use:** Almost never. If you find yourself omitting the dependency array, think about whether you actually need the effect to run on every render.

### Variation 2: Empty Array `[]` — Run Once on Mount

```jsx
useEffect(() => {
  console.log("Component mounted!");
  fetchInitialData();
}, []);
```

The empty array `[]` means "this effect has no dependencies — it never needs to re-run." React runs it once after the first render (when the component "mounts"), and never again.

**When to use:**
- Fetching initial data from an API
- Setting up a one-time event listener
- Initializing a third-party library
- Running setup code that should happen once

### Variation 3: Specific Dependencies — Run When Dependencies Change

```jsx
useEffect(() => {
  console.log(`Fetching data for user ${userId}`);
  fetchUser(userId);
}, [userId]);
```

The effect runs after the first render AND whenever `userId` changes. If `userId` stays the same between renders, the effect does not run.

**How React decides whether to re-run:**

```
Render 1: userId = 5  → Effect runs (first render always runs)
Render 2: userId = 5  → Effect SKIPPED (5 === 5, no change)
Render 3: userId = 8  → Effect runs (5 !== 8, dependency changed)
Render 4: userId = 8  → Effect SKIPPED (8 === 8, no change)
```

React uses `Object.is()` comparison (essentially `===` for primitives) to check if dependencies have changed.

**When to use:**
- Fetching data when a specific prop or state changes
- Recalculating something when inputs change
- Subscribing to a different data source when a parameter changes

---

## Practical Example: Document Title

A simple but useful effect — updating the browser tab title:

```jsx
import { useState, useEffect } from "react";

function NotificationPage() {
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    const count = notifications.length;
    if (count > 0) {
      document.title = `(${count}) New Notifications`;
    } else {
      document.title = "My App";
    }
  }, [notifications]);

  function addNotification() {
    setNotifications((prev) => [
      ...prev,
      { id: Date.now(), text: `Notification ${prev.length + 1}` },
    ]);
  }

  function clearNotifications() {
    setNotifications([]);
  }

  return (
    <div>
      <h1>Notifications</h1>
      <button onClick={addNotification}>Add Notification</button>
      <button onClick={clearNotifications}>Clear All</button>
      <p>{notifications.length} notifications</p>
      <ul>
        {notifications.map((n) => (
          <li key={n.id}>{n.text}</li>
        ))}
      </ul>
    </div>
  );
}
```

**What this code does:** The effect runs whenever the `notifications` array changes. It updates the browser tab title to show the count. When notifications are cleared, the title goes back to "My App".

**Why `[notifications]` as the dependency:** We want the title to update only when the notifications change. If we used `[]`, the title would only be set once. If we omitted the array, the title would update on every render (wasteful).

---

## Cleanup Functions

Some effects create something that needs to be cleaned up — a timer, an event listener, a subscription. If you do not clean these up, they keep running even after the component is removed from the screen, causing **memory leaks** and unexpected behavior.

### How Cleanup Works

The effect function can return another function — the **cleanup function**. React calls this cleanup function:

1. **Before running the effect again** (if dependencies changed)
2. **When the component unmounts** (is removed from the DOM)

```jsx
useEffect(() => {
  // SETUP: runs after render
  console.log("Setting up");

  return () => {
    // CLEANUP: runs before next effect or on unmount
    console.log("Cleaning up");
  };
}, [dependency]);
```

### Cleanup Timeline

```
Render 1 (mount):
  → Setup runs: "Setting up" (with dependency = A)

Render 2 (dependency changes to B):
  → Cleanup runs: "Cleaning up" (for the previous effect with A)
  → Setup runs: "Setting up" (with dependency = B)

Render 3 (dependency stays B):
  → Nothing happens (dependency did not change)

Component unmounts:
  → Cleanup runs: "Cleaning up" (for the last effect with B)
```

### Example: Timer with Cleanup

```jsx
import { useState, useEffect } from "react";

function Stopwatch() {
  const [seconds, setSeconds] = useState(0);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    if (!isRunning) return; // No setup needed if not running

    const intervalId = setInterval(() => {
      setSeconds((prev) => prev + 1);
    }, 1000);

    // Cleanup: clear the interval
    return () => {
      clearInterval(intervalId);
    };
  }, [isRunning]);

  function handleReset() {
    setIsRunning(false);
    setSeconds(0);
  }

  function formatTime(totalSeconds) {
    const minutes = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${String(minutes).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
  }

  return (
    <div style={{ textAlign: "center", padding: "2rem" }}>
      <p style={{ fontSize: "3rem", fontFamily: "monospace" }}>
        {formatTime(seconds)}
      </p>
      <div style={{ display: "flex", gap: "0.5rem", justifyContent: "center" }}>
        <button onClick={() => setIsRunning(!isRunning)}>
          {isRunning ? "Pause" : "Start"}
        </button>
        <button onClick={handleReset}>Reset</button>
      </div>
    </div>
  );
}
```

**What this code does:**

1. When `isRunning` becomes `true`, the effect starts an interval that increments `seconds` every second.
2. The cleanup function returns `clearInterval(intervalId)` — this stops the interval.
3. When `isRunning` changes to `false`, React cleans up the previous interval (stopping the timer).
4. When `isRunning` is `false`, the effect returns early without setting up an interval.

**What would happen without cleanup:** If you did not clear the interval, every time `isRunning` toggled to `true`, a new interval would start without stopping the old one. After a few toggles, you would have multiple intervals running simultaneously, each incrementing the counter — the stopwatch would speed up each time you restart it.

### Example: Window Event Listener with Cleanup

```jsx
import { useState, useEffect } from "react";

function WindowSize() {
  const [windowSize, setWindowSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  });

  useEffect(() => {
    function handleResize() {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    }

    window.addEventListener("resize", handleResize);

    // Cleanup: remove the event listener
    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []); // Empty array: set up once, clean up on unmount

  return (
    <div>
      <h2>Window Size</h2>
      <p>
        Width: {windowSize.width}px | Height: {windowSize.height}px
      </p>
      <p>
        {windowSize.width < 768 ? "Mobile" : windowSize.width < 1024 ? "Tablet" : "Desktop"}
      </p>
    </div>
  );
}
```

**Why `[]` dependency:** We only need to add the event listener once. The `handleResize` function uses `setWindowSize` (which is stable and does not change), so we do not need to list any dependencies. When the component unmounts, the cleanup removes the listener.

**What would happen without cleanup:** The event listener would remain attached to the window even after the component is removed. If the component mounts and unmounts repeatedly (e.g., when navigating between pages), you would accumulate orphaned listeners that run their handlers for nothing — a classic memory leak.

### Example: Keyboard Shortcut Listener

```jsx
import { useEffect } from "react";

function KeyboardShortcuts({ onSave, onUndo, onRedo }) {
  useEffect(() => {
    function handleKeyDown(event) {
      // Ctrl+S or Cmd+S: Save
      if ((event.ctrlKey || event.metaKey) && event.key === "s") {
        event.preventDefault();
        onSave();
      }

      // Ctrl+Z or Cmd+Z: Undo
      if ((event.ctrlKey || event.metaKey) && event.key === "z" && !event.shiftKey) {
        event.preventDefault();
        onUndo();
      }

      // Ctrl+Shift+Z or Cmd+Shift+Z: Redo
      if ((event.ctrlKey || event.metaKey) && event.key === "z" && event.shiftKey) {
        event.preventDefault();
        onRedo();
      }
    }

    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [onSave, onUndo, onRedo]);

  return null; // This component renders nothing — it just sets up listeners
}
```

**A component that renders nothing:** This is a valid pattern. `KeyboardShortcuts` exists only to attach keyboard listeners. It renders `null` (nothing visible). The parent uses it like:

```jsx
<KeyboardShortcuts
  onSave={() => console.log("Saving...")}
  onUndo={() => console.log("Undoing...")}
  onRedo={() => console.log("Redoing...")}
/>
```

---

## Data Fetching with useEffect

Fetching data from an API is the most common use of `useEffect`. Let us build this up step by step.

### Basic Data Fetching

```jsx
import { useState, useEffect } from "react";

function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchUser() {
      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch(
          `https://jsonplaceholder.typicode.com/users/${userId}`
        );

        if (!response.ok) {
          throw new Error(`HTTP error: ${response.status}`);
        }

        const data = await response.json();
        setUser(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    }

    fetchUser();
  }, [userId]); // Re-fetch when userId changes

  if (isLoading) return <p>Loading user...</p>;
  if (error) return <p style={{ color: "red" }}>Error: {error}</p>;
  if (!user) return null;

  return (
    <div>
      <h2>{user.name}</h2>
      <p>Email: {user.email}</p>
      <p>Phone: {user.phone}</p>
      <p>Website: {user.website}</p>
    </div>
  );
}
```

**Important: Why the async function is defined inside useEffect.**

You might wonder why we cannot just make the effect function itself async:

```jsx
// ❌ WRONG: useEffect callback must not be async
useEffect(async () => {
  const response = await fetch(url);
  // ...
}, []);
```

This does not work because an `async` function returns a Promise, but `useEffect` expects the return value to be either nothing or a cleanup function. Instead, define the async function inside and call it immediately:

```jsx
// ✅ CORRECT: Define async function inside, then call it
useEffect(() => {
  async function fetchData() {
    const response = await fetch(url);
    // ...
  }

  fetchData();
}, []);
```

### Handling Race Conditions

When `userId` changes rapidly (e.g., the user clicks through a list quickly), multiple fetch requests fire in sequence. The responses might arrive out of order — an earlier request might resolve after a later one, overwriting fresh data with stale data.

```
userId changes: 1 → 2 → 3

Request for user 1 starts ──────────────────────── Arrives 3rd ← STALE!
Request for user 2 starts ──────────── Arrives 2nd ← STALE!
Request for user 3 starts ── Arrives 1st

Without handling: user 1's data overwrites user 3's data
```

**The solution — use a cleanup flag:**

```jsx
import { useState, useEffect } from "react";

function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isCancelled = false; // Flag to track if this effect is still current

    async function fetchUser() {
      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch(
          `https://jsonplaceholder.typicode.com/users/${userId}`
        );

        if (!response.ok) {
          throw new Error(`HTTP error: ${response.status}`);
        }

        const data = await response.json();

        // Only update state if this effect has not been cleaned up
        if (!isCancelled) {
          setUser(data);
        }
      } catch (err) {
        if (!isCancelled) {
          setError(err.message);
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    }

    fetchUser();

    // Cleanup: mark this effect as cancelled
    return () => {
      isCancelled = true;
    };
  }, [userId]);

  if (isLoading) return <p>Loading user...</p>;
  if (error) return <p style={{ color: "red" }}>Error: {error}</p>;
  if (!user) return null;

  return (
    <div>
      <h2>{user.name}</h2>
      <p>Email: {user.email}</p>
    </div>
  );
}
```

**How this works:**

1. When `userId` changes, React runs the cleanup of the previous effect, setting `isCancelled = true`.
2. Then React runs the new effect with the new `userId`.
3. If the old fetch resolves after the new one started, the `if (!isCancelled)` check prevents it from updating state.

This is the standard pattern for preventing race conditions in data fetching with `useEffect`.

### Using AbortController for True Cancellation

The `isCancelled` flag prevents state updates but does not actually cancel the network request. For true cancellation, use `AbortController`:

```jsx
useEffect(() => {
  const controller = new AbortController();

  async function fetchUser() {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `https://jsonplaceholder.typicode.com/users/${userId}`,
        { signal: controller.signal } // Pass the abort signal
      );

      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }

      const data = await response.json();
      setUser(data);
    } catch (err) {
      // AbortError is expected when we cancel — do not treat it as an error
      if (err.name !== "AbortError") {
        setError(err.message);
      }
    } finally {
      if (!controller.signal.aborted) {
        setIsLoading(false);
      }
    }
  }

  fetchUser();

  return () => {
    controller.abort(); // Actually cancels the HTTP request
  };
}, [userId]);
```

**Difference between `isCancelled` flag and `AbortController`:**

| Approach | Network Request | State Updates |
|----------|----------------|---------------|
| `isCancelled` flag | Still completes in background | Prevented |
| `AbortController` | Actually cancelled | Prevented |

`AbortController` is better because it saves bandwidth and server resources by stopping the request entirely.

---

## The Component Lifecycle

In class components (the old way), React had explicit lifecycle methods like `componentDidMount`, `componentDidUpdate`, and `componentWillUnmount`. With hooks, `useEffect` handles all of these.

### Lifecycle Comparison

```
CLASS COMPONENTS                    FUNCTIONAL COMPONENTS (HOOKS)
═══════════════                     ═══════════════════════════

componentDidMount()          →      useEffect(() => { ... }, [])
  Runs once after first render        Runs once after first render

componentDidUpdate()         →      useEffect(() => { ... }, [deps])
  Runs after every update             Runs when dependencies change

componentWillUnmount()       →      useEffect(() => {
  Cleanup before removal                return () => { ... }
                                      }, [])
                                      Cleanup function runs on unmount

componentDidMount() +        →      useEffect(() => {
componentDidUpdate()                   ...
  Combined mount + update              return () => { ... }
                                      }, [dep])
                                      Effect runs on mount + when dep changes
                                      Cleanup runs before each re-run + on unmount
```

### The Three Lifecycle Phases

```
┌──────────────────────────────────────────────────────────┐
│                    COMPONENT LIFECYCLE                    │
│                                                          │
│  MOUNTING                                                │
│  ────────                                                │
│  Component is created and inserted into the DOM          │
│  → Initial render                                        │
│  → useEffect(() => { ... }, []) runs                    │
│                                                          │
│  UPDATING                                                │
│  ────────                                                │
│  Component re-renders due to state or prop changes       │
│  → Re-render with new data                              │
│  → Previous effect cleanup runs (if dependencies changed)│
│  → New useEffect callback runs (if dependencies changed) │
│                                                          │
│  UNMOUNTING                                              │
│  ──────────                                              │
│  Component is removed from the DOM                       │
│  → Final cleanup function runs                          │
│  → Component is gone                                     │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Demonstrating the Lifecycle

```jsx
import { useState, useEffect } from "react";

function LifecycleDemo() {
  const [showChild, setShowChild] = useState(true);

  return (
    <div>
      <button onClick={() => setShowChild(!showChild)}>
        {showChild ? "Unmount Child" : "Mount Child"}
      </button>
      {showChild && <Child />}
    </div>
  );
}

function Child() {
  const [count, setCount] = useState(0);

  // Effect 1: Runs once on mount
  useEffect(() => {
    console.log("MOUNT: Component appeared on screen");

    return () => {
      console.log("UNMOUNT: Component is being removed");
    };
  }, []);

  // Effect 2: Runs when count changes
  useEffect(() => {
    console.log(`UPDATE: Count changed to ${count}`);

    return () => {
      console.log(`CLEANUP: Cleaning up for count ${count}`);
    };
  }, [count]);

  return (
    <div style={{ padding: "1rem", border: "1px solid #ccc", margin: "1rem 0" }}>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
}

/*
Console output when component mounts:
  MOUNT: Component appeared on screen
  UPDATE: Count changed to 0

When button is clicked (count: 0 → 1):
  CLEANUP: Cleaning up for count 0
  UPDATE: Count changed to 1

When button is clicked again (count: 1 → 2):
  CLEANUP: Cleaning up for count 1
  UPDATE: Count changed to 2

When "Unmount Child" is clicked:
  CLEANUP: Cleaning up for count 2
  UNMOUNT: Component is being removed
*/
```

**Notice the cleanup order:** When count changes from 0 to 1, the cleanup for count 0 runs first, then the new effect for count 1 runs. This ensures the old effect is fully cleaned up before the new one starts.

---

## Multiple useEffect Calls

A component can have multiple `useEffect` calls. Each one handles a separate concern:

```jsx
import { useState, useEffect } from "react";

function Dashboard({ userId }) {
  const [user, setUser] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);

  // Effect 1: Fetch user data
  useEffect(() => {
    let isCancelled = false;

    async function fetchUser() {
      const response = await fetch(`https://jsonplaceholder.typicode.com/users/${userId}`);
      const data = await response.json();
      if (!isCancelled) setUser(data);
    }

    fetchUser();
    return () => { isCancelled = true; };
  }, [userId]);

  // Effect 2: Set up notification polling
  useEffect(() => {
    const intervalId = setInterval(() => {
      console.log("Checking for new notifications...");
      // In a real app, this would fetch from an API
    }, 30000); // Every 30 seconds

    return () => clearInterval(intervalId);
  }, []);

  // Effect 3: Track window resize
  useEffect(() => {
    function handleResize() {
      setWindowWidth(window.innerWidth);
    }

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  // Effect 4: Update document title based on user
  useEffect(() => {
    if (user) {
      document.title = `Dashboard - ${user.name}`;
    }
    return () => {
      document.title = "My App";
    };
  }, [user]);

  return (
    <div>
      <p>Window width: {windowWidth}px</p>
      {user && <h1>Welcome, {user.name}</h1>}
    </div>
  );
}
```

**Why separate effects?** Each effect handles one concern:
1. Data fetching (depends on `userId`)
2. Notification polling (runs once)
3. Window resize (runs once)
4. Document title (depends on `user`)

If these were all in one `useEffect`, changing `userId` would unnecessarily restart the notification polling and resize listener. Separating them ensures each effect runs only when its specific dependencies change.

**Rule:** Split effects by concern, not by lifecycle phase. Each `useEffect` should do one thing.

---

## Common Patterns

### Pattern 1: Local Storage Sync

Save and load state from local storage:

```jsx
import { useState, useEffect } from "react";

function useLocalStorage(key, initialValue) {
  // Initialize state from local storage (or use initial value)
  const [value, setValue] = useState(() => {
    try {
      const stored = localStorage.getItem(key);
      return stored !== null ? JSON.parse(stored) : initialValue;
    } catch {
      return initialValue;
    }
  });

  // Save to local storage whenever value changes
  useEffect(() => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (err) {
      console.error("Failed to save to localStorage:", err);
    }
  }, [key, value]);

  return [value, setValue];
}

// Usage:
function Settings() {
  const [theme, setTheme] = useLocalStorage("theme", "light");
  const [fontSize, setFontSize] = useLocalStorage("fontSize", 16);

  return (
    <div>
      <h2>Settings</h2>
      <label>
        Theme:
        <select value={theme} onChange={(e) => setTheme(e.target.value)}>
          <option value="light">Light</option>
          <option value="dark">Dark</option>
        </select>
      </label>
      <label>
        Font Size:
        <input
          type="range"
          min="12"
          max="24"
          value={fontSize}
          onChange={(e) => setFontSize(Number(e.target.value))}
        />
        {fontSize}px
      </label>
    </div>
  );
}
```

**What `useLocalStorage` does:** This is a **custom hook** (we will cover custom hooks in depth in Chapter 11). It works like `useState` but automatically persists the value to `localStorage`. When the component mounts, it reads from `localStorage`. When the value changes, it writes to `localStorage`.

### Pattern 2: Debounced Search

Wait for the user to stop typing before searching:

```jsx
import { useState, useEffect } from "react";

function SearchWithDebounce() {
  const [searchTerm, setSearchTerm] = useState("");
  const [debouncedTerm, setDebouncedTerm] = useState("");
  const [results, setResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

  // Debounce: update debouncedTerm 500ms after searchTerm stops changing
  useEffect(() => {
    const timerId = setTimeout(() => {
      setDebouncedTerm(searchTerm);
    }, 500);

    // Cleanup: cancel the timer if searchTerm changes again before 500ms
    return () => {
      clearTimeout(timerId);
    };
  }, [searchTerm]);

  // Fetch results when debouncedTerm changes
  useEffect(() => {
    if (!debouncedTerm.trim()) {
      setResults([]);
      return;
    }

    let isCancelled = false;
    setIsSearching(true);

    async function search() {
      try {
        // Using a real API for demonstration
        const response = await fetch(
          `https://jsonplaceholder.typicode.com/users?q=${debouncedTerm}`
        );
        const data = await response.json();

        if (!isCancelled) {
          // Filter client-side for demo
          const filtered = data.filter((user) =>
            user.name.toLowerCase().includes(debouncedTerm.toLowerCase())
          );
          setResults(filtered);
        }
      } catch (err) {
        if (!isCancelled) {
          console.error("Search failed:", err);
        }
      } finally {
        if (!isCancelled) {
          setIsSearching(false);
        }
      }
    }

    search();
    return () => { isCancelled = true; };
  }, [debouncedTerm]);

  return (
    <div style={{ maxWidth: "500px", margin: "0 auto" }}>
      <h2>Search Users</h2>
      <input
        type="text"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        placeholder="Type to search..."
        style={{ width: "100%", padding: "0.75rem", fontSize: "1rem", boxSizing: "border-box" }}
      />

      {isSearching && <p style={{ color: "#718096" }}>Searching...</p>}

      {!isSearching && debouncedTerm && results.length === 0 && (
        <p style={{ color: "#718096" }}>No results found.</p>
      )}

      <ul style={{ listStyle: "none", padding: 0 }}>
        {results.map((user) => (
          <li key={user.id} style={{ padding: "0.5rem 0", borderBottom: "1px solid #eee" }}>
            <strong>{user.name}</strong> — {user.email}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

**How debouncing works:**

```
User types: R → Re → Rea → Reac → React

Without debounce:
  API call for "R"
  API call for "Re"
  API call for "Rea"
  API call for "Reac"
  API call for "React"
  → 5 API calls!

With 500ms debounce:
  Timer set for "R"
  Timer cancelled, new timer for "Re"     (typed within 500ms)
  Timer cancelled, new timer for "Rea"    (typed within 500ms)
  Timer cancelled, new timer for "Reac"   (typed within 500ms)
  Timer cancelled, new timer for "React"  (typed within 500ms)
  ... 500ms of silence ...
  API call for "React"
  → 1 API call!
```

The cleanup function (`clearTimeout`) is the key — it cancels the pending timer whenever `searchTerm` changes, effectively resetting the 500ms countdown.

### Pattern 3: Polling (Periodic Data Refresh)

Regularly check for updates:

```jsx
import { useState, useEffect } from "react";

function LiveStatus() {
  const [status, setStatus] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [isPolling, setIsPolling] = useState(true);

  useEffect(() => {
    if (!isPolling) return;

    async function checkStatus() {
      try {
        const response = await fetch("https://jsonplaceholder.typicode.com/posts/1");
        const data = await response.json();
        setStatus(data);
        setLastUpdated(new Date().toLocaleTimeString());
      } catch (err) {
        console.error("Poll failed:", err);
      }
    }

    // Fetch immediately on mount
    checkStatus();

    // Then poll every 10 seconds
    const intervalId = setInterval(checkStatus, 10000);

    return () => clearInterval(intervalId);
  }, [isPolling]);

  return (
    <div>
      <h2>Live Status</h2>
      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1rem" }}>
        <span
          style={{
            width: "10px",
            height: "10px",
            borderRadius: "50%",
            backgroundColor: isPolling ? "#38a169" : "#a0aec0",
            display: "inline-block",
          }}
        />
        <span>{isPolling ? "Live" : "Paused"}</span>
        <button onClick={() => setIsPolling(!isPolling)} style={{ marginLeft: "auto" }}>
          {isPolling ? "Pause" : "Resume"}
        </button>
      </div>

      {status && (
        <div>
          <p><strong>Title:</strong> {status.title}</p>
          <p style={{ color: "#718096", fontSize: "0.875rem" }}>
            Last updated: {lastUpdated}
          </p>
        </div>
      )}
    </div>
  );
}
```

### Pattern 4: Online/Offline Detection

```jsx
import { useState, useEffect } from "react";

function OnlineStatus() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    function handleOnline() {
      setIsOnline(true);
    }

    function handleOffline() {
      setIsOnline(false);
    }

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  return (
    <div
      style={{
        padding: "0.5rem 1rem",
        backgroundColor: isOnline ? "#c6f6d5" : "#fed7d7",
        color: isOnline ? "#22543d" : "#742a2a",
        borderRadius: "6px",
        display: "inline-flex",
        alignItems: "center",
        gap: "0.5rem",
      }}
    >
      <span
        style={{
          width: "8px",
          height: "8px",
          borderRadius: "50%",
          backgroundColor: isOnline ? "#38a169" : "#e53e3e",
        }}
      />
      {isOnline ? "You are online" : "You are offline"}
    </div>
  );
}
```

---

## useEffect and Strict Mode

If you are using React 18+ with `StrictMode` (which Vite enables by default), you will notice that effects run **twice** in development:

```jsx
useEffect(() => {
  console.log("Effect ran"); // This logs TWICE in development!
}, []);
```

**Why?** React intentionally mounts, unmounts, and remounts your component in development to help you find bugs. If your effect does not clean up properly, this double-run reveals the problem.

```
Development (Strict Mode):
  1. Component mounts → effect runs
  2. Component unmounts → cleanup runs
  3. Component remounts → effect runs again

Production:
  1. Component mounts → effect runs (once)
```

**This only happens in development.** Production builds run effects once as expected.

**What this means for you:** If your effect works correctly with double-invocation, it will work correctly in production. If it breaks (e.g., duplicate API calls, duplicate event listeners), your cleanup is not working properly — fix it.

---

## Effects Are Not Lifecycle Methods

A common mistake when learning hooks is to think about `useEffect` as a replacement for lifecycle methods. While there is overlap, the mental model is different:

**Lifecycle thinking (class components):**
- "What should happen when the component mounts?"
- "What should happen when it updates?"
- "What should happen when it unmounts?"

**Effect thinking (hooks):**
- "What external thing needs to stay synchronized with this component's state?"

```jsx
// ❌ Lifecycle thinking: "On mount, set up. On unmount, clean up."
useEffect(() => {
  subscribeToChat(roomId);
  return () => unsubscribeFromChat(roomId);
}, []); // Bug! roomId might change

// ✅ Synchronization thinking: "Stay connected to the current room."
useEffect(() => {
  subscribeToChat(roomId);
  return () => unsubscribeFromChat(roomId);
}, [roomId]); // Reconnects when room changes
```

The correct mental model: "My component needs to be synchronized with the chat room specified by `roomId`. Whenever `roomId` changes, disconnect from the old room and connect to the new one."

---

## Mini Project: Real-Time Dashboard

Let us build a dashboard that combines multiple effects:

```jsx
import { useState, useEffect } from "react";

function RealTimeDashboard() {
  const [posts, setPosts] = useState([]);
  const [selectedPost, setSelectedPost] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState("");
  const [currentTime, setCurrentTime] = useState(new Date());
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  // Effect 1: Fetch posts on mount
  useEffect(() => {
    const controller = new AbortController();

    async function fetchPosts() {
      try {
        setStatus("loading");
        const response = await fetch(
          "https://jsonplaceholder.typicode.com/posts",
          { signal: controller.signal }
        );

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        setPosts(data.slice(0, 20)); // Take first 20
        setStatus("success");
      } catch (err) {
        if (err.name !== "AbortError") {
          setError(err.message);
          setStatus("error");
        }
      }
    }

    fetchPosts();
    return () => controller.abort();
  }, []);

  // Effect 2: Live clock
  useEffect(() => {
    const timerId = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timerId);
  }, []);

  // Effect 3: Online/offline detection
  useEffect(() => {
    function goOnline() { setIsOnline(true); }
    function goOffline() { setIsOnline(false); }

    window.addEventListener("online", goOnline);
    window.addEventListener("offline", goOffline);

    return () => {
      window.removeEventListener("online", goOnline);
      window.removeEventListener("offline", goOffline);
    };
  }, []);

  // Effect 4: Debounce search
  useEffect(() => {
    const timerId = setTimeout(() => {
      setDebouncedSearch(searchTerm);
    }, 300);

    return () => clearTimeout(timerId);
  }, [searchTerm]);

  // Effect 5: Update document title with selected post
  useEffect(() => {
    if (selectedPost) {
      document.title = `Reading: ${selectedPost.title.substring(0, 30)}...`;
    } else {
      document.title = "Real-Time Dashboard";
    }

    return () => {
      document.title = "Real-Time Dashboard";
    };
  }, [selectedPost]);

  // Effect 6: Keyboard shortcut to close post detail
  useEffect(() => {
    function handleKeyDown(event) {
      if (event.key === "Escape" && selectedPost) {
        setSelectedPost(null);
      }
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [selectedPost]);

  // Derived data
  const filteredPosts = debouncedSearch
    ? posts.filter(
        (post) =>
          post.title.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
          post.body.toLowerCase().includes(debouncedSearch.toLowerCase())
      )
    : posts;

  // ── Render ──────────────────────────────────

  return (
    <div style={{ maxWidth: "800px", margin: "0 auto", padding: "1rem" }}>
      {/* Header */}
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: "1.5rem",
        paddingBottom: "1rem",
        borderBottom: "1px solid #e2e8f0",
      }}>
        <h1 style={{ margin: 0 }}>Dashboard</h1>
        <div style={{ textAlign: "right" }}>
          <p style={{ margin: 0, fontFamily: "monospace", fontSize: "1.125rem" }}>
            {currentTime.toLocaleTimeString()}
          </p>
          <div style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "0.25rem",
            fontSize: "0.75rem",
            color: isOnline ? "#38a169" : "#e53e3e",
          }}>
            <span style={{
              width: "6px",
              height: "6px",
              borderRadius: "50%",
              backgroundColor: isOnline ? "#38a169" : "#e53e3e",
            }} />
            {isOnline ? "Online" : "Offline"}
          </div>
        </div>
      </div>

      {/* Search */}
      <input
        type="text"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        placeholder="Search posts..."
        style={{
          width: "100%",
          padding: "0.75rem",
          border: "1px solid #e2e8f0",
          borderRadius: "8px",
          marginBottom: "1rem",
          fontSize: "1rem",
          boxSizing: "border-box",
        }}
      />

      {/* Status handling */}
      {status === "loading" && (
        <div style={{ textAlign: "center", padding: "3rem" }}>
          <p style={{ color: "#718096" }}>Loading posts...</p>
        </div>
      )}

      {status === "error" && (
        <div style={{
          backgroundColor: "#fff5f5",
          border: "1px solid #fc8181",
          borderRadius: "8px",
          padding: "1.5rem",
          textAlign: "center",
        }}>
          <p style={{ color: "#e53e3e" }}>Error: {error}</p>
        </div>
      )}

      {status === "success" && (
        <>
          <p style={{ color: "#718096", fontSize: "0.875rem", marginBottom: "0.75rem" }}>
            {debouncedSearch
              ? `${filteredPosts.length} results for "${debouncedSearch}"`
              : `${posts.length} posts`}
          </p>

          {/* Post detail overlay */}
          {selectedPost && (
            <div style={{
              backgroundColor: "#f7fafc",
              border: "1px solid #e2e8f0",
              borderRadius: "8px",
              padding: "1.5rem",
              marginBottom: "1rem",
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <h2 style={{ margin: "0 0 0.5rem 0", fontSize: "1.25rem" }}>
                  {selectedPost.title}
                </h2>
                <button
                  onClick={() => setSelectedPost(null)}
                  style={{
                    backgroundColor: "transparent",
                    border: "none",
                    fontSize: "1.25rem",
                    cursor: "pointer",
                    color: "#718096",
                  }}
                >
                  x
                </button>
              </div>
              <p style={{ color: "#4a5568", lineHeight: "1.6" }}>{selectedPost.body}</p>
              <p style={{ color: "#a0aec0", fontSize: "0.75rem" }}>Press Escape to close</p>
            </div>
          )}

          {/* Post list */}
          {filteredPosts.length === 0 ? (
            <p style={{ textAlign: "center", color: "#a0aec0", padding: "2rem" }}>
              No posts match your search.
            </p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              {filteredPosts.map((post) => (
                <div
                  key={post.id}
                  onClick={() => setSelectedPost(post)}
                  style={{
                    padding: "0.75rem 1rem",
                    border: "1px solid #e2e8f0",
                    borderRadius: "8px",
                    cursor: "pointer",
                    backgroundColor: selectedPost?.id === post.id ? "#ebf8ff" : "white",
                    transition: "background-color 0.15s",
                  }}
                >
                  <h3 style={{ margin: "0 0 0.25rem 0", fontSize: "0.9375rem" }}>
                    {post.title}
                  </h3>
                  <p style={{
                    margin: 0,
                    color: "#718096",
                    fontSize: "0.8125rem",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}>
                    {post.body}
                  </p>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default RealTimeDashboard;
```

**Six independent effects in one component:**

| # | Effect | Dependencies | Cleanup |
|---|--------|-------------|---------|
| 1 | Fetch posts | `[]` (once) | AbortController |
| 2 | Live clock | `[]` (once) | clearInterval |
| 3 | Online/offline | `[]` (once) | removeEventListener |
| 4 | Debounce search | `[searchTerm]` | clearTimeout |
| 5 | Document title | `[selectedPost]` | Reset title |
| 6 | Escape shortcut | `[selectedPost]` | removeEventListener |

Each effect is independent, has proper cleanup, and runs only when its specific dependencies change.

---

## Common Mistakes

1. **Missing dependencies — causing stale closures.**

   ```jsx
   // ❌ Bug: count is always 0 inside the interval
   useEffect(() => {
     const id = setInterval(() => {
       setCount(count + 1); // count is captured as 0 and never updates
     }, 1000);
     return () => clearInterval(id);
   }, []); // count is missing from dependencies

   // ✅ Fix: use the functional updater form
   useEffect(() => {
     const id = setInterval(() => {
       setCount((prev) => prev + 1); // Does not depend on count
     }, 1000);
     return () => clearInterval(id);
   }, []); // No dependency needed
   ```

   When you use `count` inside an effect but do not include it in the dependency array, the effect captures the initial value of `count` (0) and never sees updates. Using the functional updater `(prev) => prev + 1` avoids this because it does not reference the outer `count`.

2. **Infinite loops — updating state that is also a dependency.**

   ```jsx
   // ❌ Infinite loop: fetch updates data, data triggers re-fetch
   useEffect(() => {
     fetch(url)
       .then((res) => res.json())
       .then((data) => setData(data));
   }, [data]); // data changes → effect re-runs → data changes → ...

   // ✅ Fix: depend on what triggers the fetch, not the result
   useEffect(() => {
     fetch(url)
       .then((res) => res.json())
       .then((data) => setData(data));
   }, [url]); // Only re-fetch when URL changes
   ```

3. **Object/array dependencies causing infinite re-runs.**

   ```jsx
   // ❌ New object on every render → effect runs every time
   useEffect(() => {
     fetchData(options);
   }, [{ page: 1, limit: 10 }]); // New object every render!

   // ✅ Fix: use primitive values or memoize
   useEffect(() => {
     fetchData({ page, limit });
   }, [page, limit]); // Primitives are compared by value
   ```

   Objects and arrays are compared by reference (`===`), not by value. A new object `{ page: 1 }` is not equal to another `{ page: 1 }` — they are different objects in memory.

4. **Making the effect callback async.**

   ```jsx
   // ❌ Wrong: async function returns a Promise, not a cleanup function
   useEffect(async () => {
     const data = await fetchData();
     setData(data);
   }, []);

   // ✅ Correct: define async function inside, then call it
   useEffect(() => {
     async function loadData() {
       const data = await fetchData();
       setData(data);
     }
     loadData();
   }, []);
   ```

5. **Not cleaning up subscriptions, timers, or listeners.**

   ```jsx
   // ❌ Memory leak: listener accumulates on every render
   useEffect(() => {
     window.addEventListener("resize", handleResize);
     // Missing cleanup!
   });

   // ✅ Always clean up
   useEffect(() => {
     window.addEventListener("resize", handleResize);
     return () => window.removeEventListener("resize", handleResize);
   }, []);
   ```

6. **Using `useEffect` for things that do not need it.**

   ```jsx
   // ❌ Unnecessary effect: derived data should be computed during render
   const [firstName, setFirstName] = useState("Alice");
   const [lastName, setLastName] = useState("Smith");
   const [fullName, setFullName] = useState("");

   useEffect(() => {
     setFullName(`${firstName} ${lastName}`);
   }, [firstName, lastName]);

   // ✅ Just compute it during render — no effect needed
   const fullName = `${firstName} ${lastName}`;
   ```

   If a value can be calculated from existing state and props, calculate it during render. Do not use `useEffect` to "sync" derived state — it causes an unnecessary extra render.

---

## Best Practices

1. **Each effect should do one thing.** If you need to fetch data AND set up a timer, use two separate `useEffect` calls.

2. **Always include all values from the component scope that change over time and are used by the effect in the dependency array.** If the linter warns about a missing dependency, it is almost always right.

3. **Use the functional updater for state updates inside effects** (`setCount(prev => prev + 1)`) to avoid stale closure issues and unnecessary dependencies.

4. **Always clean up:** timers (`clearTimeout`, `clearInterval`), event listeners (`removeEventListener`), abort controllers (`controller.abort()`), subscriptions (`.unsubscribe()`).

5. **Handle race conditions** with `isCancelled` flags or `AbortController` when fetching data that depends on changing values.

6. **Do not use `useEffect` for derived data.** If you can compute a value from state/props, compute it during render. `useEffect` is for synchronizing with external systems, not for internal state derivation.

7. **Use `[]` for effects that truly run once** (setup-only effects). But question whether your effect truly has no dependencies — the linter will help.

8. **Do not suppress the exhaustive-deps linter warning** without understanding why. The warning exists to prevent subtle bugs. If you think you need to suppress it, you probably need to restructure your code.

---

## Summary

In this chapter, you learned:

- **Side effects** are operations that interact with the outside world — data fetching, timers, event listeners, DOM updates, local storage.
- **`useEffect`** runs side effect code after the component renders, keeping rendering fast and predictable.
- The **dependency array** controls when the effect runs: `[]` for once on mount, `[dep]` for when `dep` changes, or omitted for every render.
- **Cleanup functions** prevent memory leaks by removing event listeners, clearing timers, and cancelling requests when the component unmounts or before the effect re-runs.
- **Data fetching** uses `useEffect` with async functions defined inside, plus `isCancelled` flags or `AbortController` for race conditions.
- The **component lifecycle** (mount, update, unmount) maps to `useEffect` patterns, but the correct mental model is **synchronization**, not lifecycle phases.
- **Multiple `useEffect` calls** in one component separate concerns — each effect handles one thing with its own dependencies and cleanup.
- **Strict Mode** double-invokes effects in development to help find cleanup bugs.
- Common patterns include **local storage sync**, **debounced search**, **polling**, and **online/offline detection**.
- **Derived data** should be computed during render, not synchronized via `useEffect`.

---

## Interview Questions

**Q1: What is `useEffect`, and why is it needed?**

`useEffect` is a React hook for performing side effects in functional components. Side effects are operations that interact with the outside world — fetching data, subscribing to events, manipulating the DOM, setting timers. These operations cannot happen during rendering because they may be slow, have unpredictable timing, or need to happen after the DOM is ready. `useEffect` provides a controlled place to run these operations after React has committed the component's output to the DOM.

**Q2: Explain the three variations of the `useEffect` dependency array.**

Without a dependency array, the effect runs after every render. With an empty array `[]`, the effect runs only once after the initial render (mount) — it tells React the effect has no dependencies that could change. With specific dependencies `[a, b]`, the effect runs after the initial render and then again whenever any listed dependency changes value. React uses `Object.is()` (essentially `===`) to compare current and previous dependency values.

**Q3: What is a cleanup function in `useEffect`, and when does it run?**

A cleanup function is the function returned from the `useEffect` callback. It runs in two scenarios: (1) before the effect re-runs due to changed dependencies, to clean up the previous effect's resources, and (2) when the component unmounts, to clean up the final effect. Common cleanup operations include clearing timers (`clearInterval`, `clearTimeout`), removing event listeners (`removeEventListener`), aborting fetch requests (`controller.abort()`), and unsubscribing from data sources.

**Q4: How do you prevent race conditions when fetching data in `useEffect`?**

Use either an `isCancelled` boolean flag or an `AbortController`. With the flag approach, declare `let isCancelled = false` at the start of the effect, check `if (!isCancelled)` before updating state, and set `isCancelled = true` in the cleanup function. With `AbortController`, create a controller, pass its signal to `fetch`, and call `controller.abort()` in cleanup. `AbortController` is preferred because it actually cancels the network request, saving bandwidth.

**Q5: Why can't the `useEffect` callback be an `async` function?**

Because `useEffect` expects the callback to return either nothing (`undefined`) or a cleanup function. An `async` function always returns a Promise, which React cannot use as a cleanup function. The solution is to define the async function inside the effect and call it immediately: `useEffect(() => { async function fetchData() { ... } fetchData(); }, [])`.

**Q6: What is a stale closure in the context of `useEffect`, and how do you avoid it?**

A stale closure occurs when an effect captures a state or prop value at the time it was created, and that value becomes outdated. For example, an interval callback that references `count` captures the value of `count` from when the effect ran — it never sees future updates. Solutions: (1) Add the variable to the dependency array so the effect re-runs with the latest value, (2) Use the functional updater form (`setCount(prev => prev + 1)`) which does not reference the outer variable, or (3) Use `useRef` to hold a mutable reference to the latest value.

**Q7: When should you NOT use `useEffect`?**

Do not use `useEffect` for computing derived data from state or props — calculate it directly during render. Do not use it for handling user events — use event handlers instead. Do not use it to "initialize" state that can be set with the initializer function of `useState`. In general, avoid `useEffect` when the operation is part of the rendering logic itself. `useEffect` is specifically for synchronizing with external systems (APIs, DOM, timers, storage).

**Q8: Why does React's Strict Mode run effects twice in development?**

Strict Mode intentionally mounts, unmounts, and remounts every component in development to surface bugs in effect cleanup. If an effect works correctly when run twice (setup → cleanup → setup), it has proper cleanup logic. If it breaks (duplicate subscriptions, orphaned listeners, inconsistent state), the cleanup function is missing or incomplete. This double-invocation only happens in development — production builds run effects once.

---

## Practice Exercises

**Exercise 1: Auto-Saving Notes**

Create a notes component that:
- Has a text area for writing notes
- Auto-saves to `localStorage` every 3 seconds after the user stops typing (debounced)
- Shows "Saved" or "Unsaved changes" indicator
- Loads saved notes from `localStorage` on mount
- Shows the last saved timestamp

**Exercise 2: Countdown Timer**

Build a countdown timer that:
- Lets the user input minutes and seconds
- Has Start, Pause, Resume, and Reset buttons
- Updates every second when running
- Shows a visual progress bar
- Changes the document title to show remaining time
- Plays an alert (or changes background color) when the timer reaches 0
- Properly cleans up the interval

**Exercise 3: Window Scroll Tracker**

Create a component that:
- Shows a "Back to top" button only when scrolled past 300px
- Shows a scroll progress bar at the top of the page
- Displays the current scroll percentage
- Smoothly scrolls to top when the button is clicked
- Uses a single `useEffect` with scroll event listener and cleanup

**Exercise 4: API Data with Polling and Manual Refresh**

Build a component that:
- Fetches data from an API on mount
- Polls for updates every 30 seconds
- Has a "Refresh Now" button for manual refresh
- Shows "Last updated: X seconds ago" with live counter
- Has a toggle to enable/disable auto-polling
- Handles loading, error, and empty states
- Cancels pending requests on unmount (AbortController)

**Exercise 5: Multi-Effect Component**

Create a "Focus Timer" (Pomodoro-style) component with these separate effects:
- Effect 1: A 25-minute countdown timer
- Effect 2: Updates document title with remaining time
- Effect 3: Listens for Space key to pause/resume
- Effect 4: Saves session history to localStorage
- Effect 5: Shows a browser notification when the timer ends (using the Notification API)
- Each effect should have proper cleanup

**Exercise 6: Real-Time Search with Loading States**

Create a GitHub user search component:
- Text input for username search
- Debounced API call (500ms) to `https://api.github.com/search/users?q={query}`
- Show loading spinner while searching
- Display results as a list with avatar, username, and profile link
- Handle errors (API rate limiting)
- Cancel previous requests when a new search starts (AbortController)
- Show "Type to search" when input is empty

---

## What Is Next?

You now understand how React components interact with the outside world through `useEffect`. You can fetch data, set up timers, listen for events, and clean everything up properly.

In Chapter 9, we will explore **Forms in React — Controlled and Uncontrolled Components**. You will learn the standard patterns for handling form input, validation, and submission in React applications, building on the event handling and state management you already know.
