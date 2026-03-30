# Chapter 12: Custom Hooks

---

## Learning Goals

By the end of this chapter, you will be able to:

- Explain what custom hooks are and why they exist
- Extract reusable logic from components into custom hooks
- Follow the naming convention and rules for custom hooks
- Build practical custom hooks for common tasks (data fetching, forms, local storage, timers, media queries)
- Compose hooks together — building complex hooks from simpler ones
- Share state logic across multiple components using custom hooks
- Test and debug custom hooks
- Know when to create a custom hook and when not to

---

## What Is a Custom Hook?

A custom hook is a JavaScript function whose name starts with `use` and that calls other hooks inside it. That is the entire definition — there is no special API, no registration step, no magic. It is just a function.

Custom hooks let you extract stateful logic from a component and share it across multiple components. The key insight is that while React components share **UI**, custom hooks share **behavior**.

### Before and After: Why Custom Hooks Exist

**Before (duplicated logic):**

```jsx
function UserProfile() {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    fetch("/api/user/1")
      .then((res) => res.json())
      .then((data) => { if (!cancelled) { setUser(data); setIsLoading(false); }})
      .catch((err) => { if (!cancelled) { setError(err.message); setIsLoading(false); }});
    return () => { cancelled = true; };
  }, []);

  if (isLoading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;
  return <div>{user.name}</div>;
}

function ProductPage() {
  const [product, setProduct] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Almost identical fetch logic repeated...
  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    fetch("/api/product/42")
      .then((res) => res.json())
      .then((data) => { if (!cancelled) { setProduct(data); setIsLoading(false); }})
      .catch((err) => { if (!cancelled) { setError(err.message); setIsLoading(false); }});
    return () => { cancelled = true; };
  }, []);

  if (isLoading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;
  return <div>{product.title}</div>;
}
```

Both components have the same fetch-with-loading-and-error pattern. The logic is duplicated.

**After (extracted into a custom hook):**

```jsx
function useFetch(url) {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setError(null);

    fetch(url)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => { if (!cancelled) { setData(data); setIsLoading(false); }})
      .catch((err) => { if (!cancelled) { setError(err.message); setIsLoading(false); }});

    return () => { cancelled = true; };
  }, [url]);

  return { data, isLoading, error };
}

// Now both components are simple:
function UserProfile() {
  const { data: user, isLoading, error } = useFetch("/api/user/1");

  if (isLoading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;
  return <div>{user.name}</div>;
}

function ProductPage() {
  const { data: product, isLoading, error } = useFetch("/api/product/42");

  if (isLoading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;
  return <div>{product.title}</div>;
}
```

The fetch logic lives in one place. Every component that needs data can call `useFetch(url)` and get back `{ data, isLoading, error }`.

---

## Rules for Custom Hooks

### Rule 1: Name Must Start with `use`

```jsx
// ✅ Valid custom hook names
function useWindowSize() { ... }
function useLocalStorage(key, initialValue) { ... }
function useDebounce(value, delay) { ... }

// ❌ Not recognized as hooks — React won't enforce hook rules
function getWindowSize() { ... }
function windowSizeHook() { ... }
function fetchData() { ... }
```

The `use` prefix is not just a convention — React's linter uses it to check that you follow the rules of hooks (no conditional calls, no calls inside loops, etc.).

### Rule 2: Custom Hooks Follow the Rules of Hooks

Custom hooks must follow the same rules as built-in hooks:

1. **Only call hooks at the top level** — not inside conditions, loops, or nested functions.
2. **Only call hooks from React functions** — from components or from other custom hooks.

```jsx
// ❌ WRONG: hook called conditionally
function useMaybeTimer(shouldRun) {
  if (shouldRun) {
    const [time, setTime] = useState(0); // Hook inside if — ERROR
  }
}

// ✅ CORRECT: hook called unconditionally, condition inside
function useTimer(shouldRun) {
  const [time, setTime] = useState(0);

  useEffect(() => {
    if (!shouldRun) return;
    const id = setInterval(() => setTime((t) => t + 1), 1000);
    return () => clearInterval(id);
  }, [shouldRun]);

  return time;
}
```

### Rule 3: Each Call Gets Its Own State

When two components call the same custom hook, they do NOT share state. Each call creates independent state:

```jsx
function Counter() {
  const count1 = useCounter(0);  // Independent state
  const count2 = useCounter(10); // Independent state

  return (
    <div>
      <p>Counter 1: {count1.value}</p>
      <p>Counter 2: {count2.value}</p>
      {/* Incrementing one does not affect the other */}
    </div>
  );
}
```

Custom hooks share **logic**, not **state**. Each call creates its own `useState`, `useEffect`, and `useRef` instances.

---

## Building Custom Hooks — From Simple to Complex

### Hook 1: useToggle

The simplest useful custom hook — managing a boolean state:

```jsx
import { useState, useCallback } from "react";

function useToggle(initialValue = false) {
  const [value, setValue] = useState(initialValue);

  const toggle = useCallback(() => {
    setValue((prev) => !prev);
  }, []);

  const setTrue = useCallback(() => setValue(true), []);
  const setFalse = useCallback(() => setValue(false), []);

  return { value, toggle, setTrue, setFalse };
}

// Usage:
function Accordion({ title, children }) {
  const { value: isOpen, toggle } = useToggle(false);

  return (
    <div>
      <button onClick={toggle}>
        {title} {isOpen ? "▲" : "▼"}
      </button>
      {isOpen && <div>{children}</div>}
    </div>
  );
}

function Modal() {
  const { value: isVisible, setTrue: open, setFalse: close } = useToggle(false);

  return (
    <div>
      <button onClick={open}>Open Modal</button>
      {isVisible && (
        <div className="modal-backdrop" onClick={close}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Modal Content</h2>
            <button onClick={close}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
}
```

**Why this is better than raw `useState(false)`:** The returned API (`toggle`, `setTrue`, `setFalse`) is clearer about intent. And `useCallback` ensures stable references for event handlers.

### Hook 2: useLocalStorage

Persist state to local storage — a hook we previewed in Chapter 8:

```jsx
import { useState, useEffect } from "react";

function useLocalStorage(key, initialValue) {
  // Initialize from local storage or use initial value
  const [value, setValue] = useState(() => {
    try {
      const stored = localStorage.getItem(key);
      return stored !== null ? JSON.parse(stored) : initialValue;
    } catch {
      return initialValue;
    }
  });

  // Sync to local storage on changes
  useEffect(() => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (err) {
      console.error(`Failed to save "${key}" to localStorage:`, err);
    }
  }, [key, value]);

  return [value, setValue];
}

// Usage:
function Settings() {
  const [theme, setTheme] = useLocalStorage("theme", "light");
  const [fontSize, setFontSize] = useLocalStorage("fontSize", 16);
  const [favorites, setFavorites] = useLocalStorage("favorites", []);

  return (
    <div>
      <select value={theme} onChange={(e) => setTheme(e.target.value)}>
        <option value="light">Light</option>
        <option value="dark">Dark</option>
      </select>

      <input
        type="range"
        min="12"
        max="24"
        value={fontSize}
        onChange={(e) => setFontSize(Number(e.target.value))}
      />
      <span>{fontSize}px</span>
    </div>
  );
}
```

**The hook API matches `useState` exactly** — it returns `[value, setValue]`. This means switching from `useState` to `useLocalStorage` requires changing one function name.

### Hook 3: useDebounce

Delay a value until the user stops changing it:

```jsx
import { useState, useEffect } from "react";

function useDebounce(value, delay = 300) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

// Usage:
function SearchPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const debouncedSearch = useDebounce(searchTerm, 500);

  useEffect(() => {
    if (debouncedSearch) {
      console.log("Searching for:", debouncedSearch);
      // Fetch search results...
    }
  }, [debouncedSearch]);

  return (
    <input
      type="text"
      value={searchTerm}
      onChange={(e) => setSearchTerm(e.target.value)}
      placeholder="Search..."
    />
  );
}
```

**How it works:** The hook creates a timer whenever `value` changes. If `value` changes again before the timer fires, the old timer is cleared and a new one starts. Only when `value` stays the same for `delay` milliseconds does `debouncedValue` update.

### Hook 4: useWindowSize

Track browser window dimensions:

```jsx
import { useState, useEffect } from "react";

function useWindowSize() {
  const [size, setSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  });

  useEffect(() => {
    function handleResize() {
      setSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    }

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return size;
}

// Usage:
function ResponsiveLayout() {
  const { width } = useWindowSize();

  const layout = width < 768 ? "mobile" : width < 1024 ? "tablet" : "desktop";

  return (
    <div>
      <p>Window width: {width}px ({layout})</p>
      {layout === "mobile" ? (
        <MobileNavigation />
      ) : (
        <DesktopNavigation />
      )}
    </div>
  );
}
```

### Hook 5: useMediaQuery

A more flexible way to respond to screen size:

```jsx
import { useState, useEffect } from "react";

function useMediaQuery(query) {
  const [matches, setMatches] = useState(() => {
    return window.matchMedia(query).matches;
  });

  useEffect(() => {
    const mediaQuery = window.matchMedia(query);

    function handleChange(event) {
      setMatches(event.matches);
    }

    mediaQuery.addEventListener("change", handleChange);
    return () => mediaQuery.removeEventListener("change", handleChange);
  }, [query]);

  return matches;
}

// Usage:
function App() {
  const isMobile = useMediaQuery("(max-width: 767px)");
  const isTablet = useMediaQuery("(min-width: 768px) and (max-width: 1023px)");
  const prefersDark = useMediaQuery("(prefers-color-scheme: dark)");

  return (
    <div style={{ backgroundColor: prefersDark ? "#1a202c" : "white", color: prefersDark ? "white" : "#1a202c" }}>
      {isMobile && <p>You are on a mobile device.</p>}
      {isTablet && <p>You are on a tablet.</p>}
      {!isMobile && !isTablet && <p>You are on a desktop.</p>}
    </div>
  );
}
```

### Hook 6: useFetch (Complete Version)

A production-quality data fetching hook:

```jsx
import { useState, useEffect, useCallback } from "react";

function useFetch(url, options = {}) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [status, setStatus] = useState("idle"); // idle | loading | success | error

  const fetchData = useCallback(async () => {
    if (!url) return;

    const controller = new AbortController();
    setStatus("loading");
    setError(null);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      setData(result);
      setStatus("success");
    } catch (err) {
      if (err.name !== "AbortError") {
        setError(err.message);
        setStatus("error");
      }
    }

    return () => controller.abort();
  }, [url]);

  useEffect(() => {
    const cleanup = fetchData();
    return () => {
      if (cleanup && typeof cleanup === "function") cleanup();
    };
  }, [fetchData]);

  const refetch = useCallback(() => {
    fetchData();
  }, [fetchData]);

  return {
    data,
    error,
    status,
    isLoading: status === "loading",
    isError: status === "error",
    isSuccess: status === "success",
    refetch,
  };
}

// Usage:
function UserList() {
  const {
    data: users,
    isLoading,
    isError,
    error,
    refetch,
  } = useFetch("https://jsonplaceholder.typicode.com/users");

  if (isLoading) return <p>Loading users...</p>;
  if (isError) return (
    <div>
      <p>Error: {error}</p>
      <button onClick={refetch}>Retry</button>
    </div>
  );

  return (
    <ul>
      {users?.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

**Features:**
- AbortController for request cancellation
- Status pattern (idle/loading/success/error)
- Convenience booleans (isLoading, isError, isSuccess)
- `refetch` function for manual retry
- Handles URL changes (re-fetches automatically)

### Hook 7: useForm

A comprehensive form management hook:

```jsx
import { useState, useCallback } from "react";

function useForm(initialValues, validate) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = useCallback((event) => {
    const { name, value, type, checked } = event.target;
    const newValue = type === "checkbox" ? checked : value;

    setValues((prev) => ({ ...prev, [name]: newValue }));

    // If field was touched, validate on change
    if (touched[name] && validate) {
      const fieldError = validate({ ...values, [name]: newValue });
      setErrors((prev) => ({ ...prev, [name]: fieldError[name] || "" }));
    }
  }, [touched, validate, values]);

  const handleBlur = useCallback((event) => {
    const { name } = event.target;
    setTouched((prev) => ({ ...prev, [name]: true }));

    if (validate) {
      const allErrors = validate(values);
      setErrors((prev) => ({ ...prev, [name]: allErrors[name] || "" }));
    }
  }, [validate, values]);

  const handleSubmit = useCallback((onSubmit) => {
    return async (event) => {
      event.preventDefault();

      // Touch all fields
      const allTouched = {};
      Object.keys(values).forEach((key) => { allTouched[key] = true; });
      setTouched(allTouched);

      // Validate all fields
      if (validate) {
        const allErrors = validate(values);
        setErrors(allErrors);

        if (Object.values(allErrors).some((e) => e)) {
          return; // Has errors — do not submit
        }
      }

      setIsSubmitting(true);
      try {
        await onSubmit(values);
      } finally {
        setIsSubmitting(false);
      }
    };
  }, [validate, values]);

  const reset = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
    setIsSubmitting(false);
  }, [initialValues]);

  const getFieldProps = useCallback((name) => ({
    name,
    value: values[name] || "",
    onChange: handleChange,
    onBlur: handleBlur,
  }), [values, handleChange, handleBlur]);

  return {
    values,
    errors,
    touched,
    isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit,
    reset,
    getFieldProps,
    setValues,
  };
}

// Usage:
function ContactForm() {
  const form = useForm(
    { name: "", email: "", message: "" },
    (values) => {
      const errors = {};
      if (!values.name.trim()) errors.name = "Name is required.";
      if (!values.email.trim()) errors.email = "Email is required.";
      else if (!/\S+@\S+\.\S+/.test(values.email)) errors.email = "Invalid email.";
      if (!values.message.trim()) errors.message = "Message is required.";
      return errors;
    }
  );

  async function onSubmit(values) {
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000));
    console.log("Submitted:", values);
    form.reset();
  }

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} style={{ maxWidth: "400px", margin: "0 auto" }}>
      <h2>Contact</h2>

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="name">Name:</label>
        <input
          id="name"
          type="text"
          {...form.getFieldProps("name")}
          style={{
            width: "100%", padding: "0.5rem", boxSizing: "border-box",
            border: `1px solid ${form.touched.name && form.errors.name ? "#e53e3e" : "#e2e8f0"}`,
            borderRadius: "4px",
          }}
        />
        {form.touched.name && form.errors.name && (
          <p style={{ color: "#e53e3e", fontSize: "0.875rem", margin: "0.25rem 0 0" }}>
            {form.errors.name}
          </p>
        )}
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="email">Email:</label>
        <input id="email" type="email" {...form.getFieldProps("email")}
          style={{
            width: "100%", padding: "0.5rem", boxSizing: "border-box",
            border: `1px solid ${form.touched.email && form.errors.email ? "#e53e3e" : "#e2e8f0"}`,
            borderRadius: "4px",
          }}
        />
        {form.touched.email && form.errors.email && (
          <p style={{ color: "#e53e3e", fontSize: "0.875rem", margin: "0.25rem 0 0" }}>
            {form.errors.email}
          </p>
        )}
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="message">Message:</label>
        <textarea id="message" {...form.getFieldProps("message")} rows={4}
          style={{
            width: "100%", padding: "0.5rem", boxSizing: "border-box",
            border: `1px solid ${form.touched.message && form.errors.message ? "#e53e3e" : "#e2e8f0"}`,
            borderRadius: "4px",
          }}
        />
        {form.touched.message && form.errors.message && (
          <p style={{ color: "#e53e3e", fontSize: "0.875rem", margin: "0.25rem 0 0" }}>
            {form.errors.message}
          </p>
        )}
      </div>

      <button
        type="submit"
        disabled={form.isSubmitting}
        style={{ padding: "0.75rem 1.5rem", width: "100%" }}
      >
        {form.isSubmitting ? "Sending..." : "Send Message"}
      </button>
    </form>
  );
}
```

**The `getFieldProps` helper** reduces boilerplate — instead of writing `name`, `value`, `onChange`, and `onBlur` for every input, you spread `{...form.getFieldProps("fieldName")}`.

### Hook 8: useOnlineStatus

```jsx
import { useState, useEffect } from "react";

function useOnlineStatus() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    function handleOnline() { setIsOnline(true); }
    function handleOffline() { setIsOnline(false); }

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  return isOnline;
}

// Usage:
function App() {
  const isOnline = useOnlineStatus();

  return (
    <div>
      {!isOnline && (
        <div style={{
          backgroundColor: "#fed7d7",
          color: "#742a2a",
          padding: "0.5rem 1rem",
          textAlign: "center",
        }}>
          You are offline. Some features may be unavailable.
        </div>
      )}
      {/* Rest of app */}
    </div>
  );
}
```

### Hook 9: useClickOutside

Reusable click-outside detection:

```jsx
import { useEffect, useRef } from "react";

function useClickOutside(handler) {
  const ref = useRef(null);

  useEffect(() => {
    function handleClick(event) {
      if (ref.current && !ref.current.contains(event.target)) {
        handler();
      }
    }

    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [handler]);

  return ref;
}

// Usage:
function Dropdown({ options, onSelect }) {
  const { value: isOpen, toggle, setFalse: close } = useToggle(false);
  const dropdownRef = useClickOutside(close);

  return (
    <div ref={dropdownRef} style={{ position: "relative" }}>
      <button onClick={toggle}>Menu ▼</button>
      {isOpen && (
        <ul style={{ position: "absolute", top: "100%", left: 0 }}>
          {options.map((option) => (
            <li key={option} onClick={() => { onSelect(option); close(); }}>
              {option}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

**Notice how hooks compose:** `Dropdown` uses both `useToggle` (for open/close state) and `useClickOutside` (for closing on outside clicks). Each hook handles one concern.

### Hook 10: useInterval

A declarative interval hook:

```jsx
import { useEffect, useRef } from "react";

function useInterval(callback, delay) {
  const savedCallback = useRef(callback);

  // Update the saved callback when it changes
  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    if (delay === null) return; // Paused

    const id = setInterval(() => {
      savedCallback.current();
    }, delay);

    return () => clearInterval(id);
  }, [delay]);
}

// Usage:
function Clock() {
  const [time, setTime] = useState(new Date());
  const [isPaused, setIsPaused] = useState(false);

  useInterval(
    () => setTime(new Date()),
    isPaused ? null : 1000 // null pauses the interval
  );

  return (
    <div>
      <p style={{ fontSize: "2rem", fontFamily: "monospace" }}>
        {time.toLocaleTimeString()}
      </p>
      <button onClick={() => setIsPaused(!isPaused)}>
        {isPaused ? "Resume" : "Pause"}
      </button>
    </div>
  );
}
```

**Why the ref pattern:** The interval callback might use state or props that change. Without the ref, you would need to restart the interval every time the callback changes. The ref ensures the interval always calls the latest version of the callback without restarting.

---

## Composing Hooks

One of the most powerful aspects of custom hooks is that they can call other custom hooks. This lets you build complex behavior from simple building blocks.

### Example: useSearchWithDebounce

```jsx
function useSearchWithDebounce(items, fields, delay = 300) {
  const [searchTerm, setSearchTerm] = useState("");
  const debouncedTerm = useDebounce(searchTerm, delay); // Uses our useDebounce hook

  const filteredItems = useMemo(() => {
    if (!debouncedTerm.trim()) return items;

    const term = debouncedTerm.toLowerCase();
    return items.filter((item) =>
      fields.some((field) => {
        const value = item[field];
        return value && String(value).toLowerCase().includes(term);
      })
    );
  }, [items, fields, debouncedTerm]);

  return {
    searchTerm,
    setSearchTerm,
    filteredItems,
    isSearching: searchTerm !== debouncedTerm,
    resultCount: filteredItems.length,
    totalCount: items.length,
  };
}

// Usage:
function ContactsPage() {
  const contacts = [/* ... */];

  const search = useSearchWithDebounce(contacts, ["name", "email", "phone"], 500);

  return (
    <div>
      <input
        type="text"
        value={search.searchTerm}
        onChange={(e) => search.setSearchTerm(e.target.value)}
        placeholder="Search contacts..."
      />
      {search.isSearching && <p>Searching...</p>}
      <p>{search.resultCount} of {search.totalCount} contacts</p>
      <ul>
        {search.filteredItems.map((contact) => (
          <li key={contact.id}>{contact.name}</li>
        ))}
      </ul>
    </div>
  );
}
```

**Composition chain:**
```
useSearchWithDebounce
├── useState (searchTerm)
├── useDebounce (debouncedTerm)
│   ├── useState (internal)
│   └── useEffect (timer)
└── useMemo (filtered results)
```

### Example: usePersistedForm

A form hook that saves to local storage:

```jsx
function usePersistedForm(key, initialValues, validate) {
  // Use our useLocalStorage hook instead of useState
  const [values, setValues] = useLocalStorage(key, initialValues);

  // Use our useForm hook for the rest
  const form = useForm(values, validate);

  // Sync form values to local storage
  useEffect(() => {
    setValues(form.values);
  }, [form.values, setValues]);

  // Override reset to also clear local storage
  const reset = useCallback(() => {
    form.reset();
    setValues(initialValues);
  }, [form, initialValues, setValues]);

  return { ...form, reset };
}

// Usage: Form that survives page reloads
function DraftEditor() {
  const form = usePersistedForm(
    "draft-post",
    { title: "", body: "" },
    (values) => {
      const errors = {};
      if (!values.title.trim()) errors.title = "Title required.";
      return errors;
    }
  );

  // User can close the browser and come back — their draft is saved!
  return (
    <form onSubmit={form.handleSubmit(async (values) => {
      await savePost(values);
      form.reset(); // Clears form AND local storage
    })}>
      <input {...form.getFieldProps("title")} placeholder="Post title" />
      <textarea {...form.getFieldProps("body")} placeholder="Write your post..." />
      <button type="submit">Publish</button>
    </form>
  );
}
```

---

## Organizing Custom Hooks

### File Structure

Place custom hooks in their own files, organized in a `hooks` directory:

```
src/
├── hooks/
│   ├── useToggle.js
│   ├── useLocalStorage.js
│   ├── useDebounce.js
│   ├── useFetch.js
│   ├── useForm.js
│   ├── useWindowSize.js
│   ├── useMediaQuery.js
│   ├── useClickOutside.js
│   ├── useInterval.js
│   └── useOnlineStatus.js
├── components/
│   ├── Header.jsx
│   └── Dashboard.jsx
└── App.jsx
```

### Export Pattern

Each hook file exports the hook as a named export:

```jsx
// hooks/useToggle.js
import { useState, useCallback } from "react";

export function useToggle(initialValue = false) {
  // ...
}
```

```jsx
// In a component:
import { useToggle } from "../hooks/useToggle";
```

For projects with many hooks, you can create a barrel export:

```jsx
// hooks/index.js
export { useToggle } from "./useToggle";
export { useLocalStorage } from "./useLocalStorage";
export { useDebounce } from "./useDebounce";
export { useFetch } from "./useFetch";
```

```jsx
// In a component:
import { useToggle, useFetch } from "../hooks";
```

---

## When to Create a Custom Hook

### Create a Hook When:

1. **Two or more components share the same stateful logic.** If you find yourself copying `useState` + `useEffect` patterns between components, extract them.

2. **A component's logic is complex enough to benefit from a clear name.** `useSearchWithDebounce` is more readable than 15 lines of `useState`, `useEffect`, and `useMemo` inline.

3. **You want to test logic independently.** Custom hooks can be tested in isolation without rendering a component.

### Do NOT Create a Hook When:

1. **The logic is used in only one component and is short.** Extracting 3 lines into a separate file adds indirection for no benefit.

2. **The logic does not use any hooks.** If a function does not call `useState`, `useEffect`, `useRef`, or other hooks, it is just a regular function — not a hook.

   ```jsx
   // ❌ Not a hook — does not use any hooks
   function useFormatDate(date) {
     return date.toLocaleDateString("en-US", { year: "numeric", month: "long" });
   }

   // ✅ Just a utility function
   function formatDate(date) {
     return date.toLocaleDateString("en-US", { year: "numeric", month: "long" });
   }
   ```

3. **You are just wrapping a single `useState`.** Unless you need additional behavior, a plain `useState` is clearer.

---

## Common Mistakes

1. **Not starting the name with `use`.**

   ```jsx
   // ❌ React won't enforce hook rules
   function fetchData(url) {
     const [data, setData] = useState(null);
     // ...
   }

   // ✅ Correct naming
   function useFetchData(url) {
     const [data, setData] = useState(null);
     // ...
   }
   ```

2. **Creating a hook that does not use hooks.**

   ```jsx
   // ❌ This is just a utility function, not a hook
   function useCapitalize(str) {
     return str.charAt(0).toUpperCase() + str.slice(1);
   }

   // ✅ Just make it a regular function
   function capitalize(str) {
     return str.charAt(0).toUpperCase() + str.slice(1);
   }
   ```

3. **Assuming two components sharing a hook share state.**

   ```jsx
   // Each component gets its own independent state
   function ComponentA() {
     const toggle = useToggle(false); // toggle.value is independent
     return <p>{toggle.value ? "A is on" : "A is off"}</p>;
   }

   function ComponentB() {
     const toggle = useToggle(false); // Different state!
     return <p>{toggle.value ? "B is on" : "B is off"}</p>;
   }
   ```

4. **Returning too many values.** If your hook returns 10+ values, it is probably doing too much. Split it into smaller hooks.

5. **Not memoizing returned functions.** If a hook returns functions that get passed to `memo`'d children, wrap them in `useCallback`:

   ```jsx
   // ❌ New function on every render of the consuming component
   function useCounter() {
     const [count, setCount] = useState(0);
     function increment() { setCount((c) => c + 1); }
     return { count, increment };
   }

   // ✅ Stable function reference
   function useCounter() {
     const [count, setCount] = useState(0);
     const increment = useCallback(() => setCount((c) => c + 1), []);
     return { count, increment };
   }
   ```

---

## Best Practices

1. **Name hooks descriptively.** `useAuth`, `useCart`, `useSearchResults` — the name should tell you what the hook does without reading the code.

2. **Follow the `useState` return convention when appropriate.** If your hook is a specialized state hook, return `[value, setValue]`. For more complex hooks, return an object `{ data, isLoading, error, refetch }`.

3. **Keep hooks focused.** Each hook should do one thing. If `useFetch` also handles caching, pagination, and retries, consider breaking it into `useFetch`, `useCache`, and `usePagination`.

4. **Document hook parameters and return values.** Other developers (including future you) should understand what the hook accepts and returns without reading the implementation.

5. **Use `useCallback` for returned functions** that consumers might pass to memoized children.

6. **Place hooks in a `hooks/` directory** with one hook per file.

7. **Compose hooks from smaller hooks** rather than creating one giant hook. This makes each piece testable and reusable.

---

## Summary

In this chapter, you learned:

- **Custom hooks** are functions starting with `use` that call other hooks. They extract reusable stateful logic from components.
- Custom hooks share **logic**, not **state**. Each call creates independent state instances.
- **10 practical hooks**: `useToggle`, `useLocalStorage`, `useDebounce`, `useWindowSize`, `useMediaQuery`, `useFetch`, `useForm`, `useOnlineStatus`, `useClickOutside`, `useInterval`.
- Hooks can **compose** — complex hooks can be built from simpler hooks (`useSearchWithDebounce` uses `useDebounce` and `useMemo`).
- **When to create a hook**: when logic is reused, when it simplifies a complex component, or when you need testable logic.
- **When NOT to**: when the function does not use hooks (make it a utility), when logic is trivial, or when used in only one place.
- **Organization**: one hook per file in a `hooks/` directory, with barrel exports.

---

## Interview Questions

**Q1: What is a custom hook in React?**

A custom hook is a JavaScript function whose name starts with `use` and that calls one or more built-in hooks (like `useState`, `useEffect`, `useRef`) or other custom hooks. It allows you to extract and reuse stateful logic across multiple components without duplicating code. Custom hooks follow the same rules as built-in hooks — they must be called at the top level, not inside conditions or loops.

**Q2: Do components that use the same custom hook share state?**

No. Each call to a custom hook creates completely independent state. If `ComponentA` and `ComponentB` both call `useCounter()`, each has its own `count` state variable. Custom hooks share logic (the code that manages state), not state itself. To share state between components, you would use Context, props, or a state management library.

**Q3: What are the rules for creating a custom hook?**

Three rules: (1) The name must start with `use` — this tells React and its linter to enforce hook rules. (2) It must follow the rules of hooks — only call hooks at the top level, not inside conditions or loops. (3) It can only be called from React function components or other custom hooks, not from regular JavaScript functions.

**Q4: How do you decide what to return from a custom hook?**

If the hook manages a single value (like `useLocalStorage`), return a tuple `[value, setValue]` matching the `useState` convention. If the hook returns multiple pieces of related data (like `useFetch`), return an object `{ data, isLoading, error, refetch }` — this allows consumers to destructure only what they need and is easier to extend. Avoid returning more than 5-7 values; if you need more, the hook may be doing too much.

**Q5: When should you NOT create a custom hook?**

Don't create a hook when: the function doesn't call any hooks (it should be a regular utility function), the logic is only used in one component and is simple enough to understand inline, you're just wrapping a single `useState` without adding behavior, or the hook does too many things (split it into multiple focused hooks instead).

**Q6: How do custom hooks enable composition?**

Custom hooks can call other custom hooks, allowing you to build complex behavior from simple building blocks. For example, `useSearchWithDebounce` can internally use `useDebounce` for delayed search and `useMemo` for caching results. `usePersistedForm` can combine `useLocalStorage` and `useForm`. This composition model lets you create a library of small, focused, tested hooks that snap together like building blocks.

---

## Practice Exercises

**Exercise 1: usePrevious**

Create a `usePrevious` hook that:
- Takes any value as input
- Returns the value from the previous render
- Returns `undefined` on the first render
- Works with any data type (number, string, object)

**Exercise 2: useHover**

Create a `useHover` hook that:
- Returns a ref and a boolean `isHovered`
- Attach the ref to any element to track hover state
- Uses `mouseenter` and `mouseleave` events
- Properly cleans up event listeners

**Exercise 3: useAsync**

Create a `useAsync` hook that:
- Takes an async function
- Returns `{ execute, data, error, status }`
- Does not execute automatically — the consumer calls `execute()`
- Handles loading, success, and error states
- Prevents state updates after unmount

**Exercise 4: useKeyPress**

Create a `useKeyPress` hook that:
- Takes a key name (e.g., "Enter", "Escape", "a")
- Returns a boolean indicating if that key is currently pressed
- Handles both `keydown` and `keyup`
- Supports modifier keys (Ctrl, Shift, Alt)
- Cleans up listeners on unmount

**Exercise 5: usePagination**

Create a `usePagination` hook that:
- Takes total items and items per page
- Returns `{ currentPage, totalPages, nextPage, prevPage, goToPage, startIndex, endIndex }`
- Has bounds checking (cannot go below 1 or above total pages)
- Resets to page 1 when total items change

**Exercise 6: useCountdown**

Create a `useCountdown` hook that:
- Takes a target date or number of seconds
- Returns `{ days, hours, minutes, seconds, isExpired }`
- Updates every second
- Stops updating when the countdown reaches zero
- Properly cleans up the interval

---

## What Is Next?

You now have a powerful toolkit of reusable custom hooks and the knowledge to create your own. Custom hooks are one of the features that makes React truly scalable — they let you share complex behavior without duplicating code.

In Chapter 13, we will explore the **Context API and Prop Drilling Solutions** — learning how to share data across many levels of your component tree without passing props through every intermediate component.
