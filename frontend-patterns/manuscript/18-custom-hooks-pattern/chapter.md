# Chapter 18: Custom Hooks Pattern

## What You Will Learn

- Why duplicated stateful logic is a problem and how custom hooks solve it
- The rules of hooks and why they exist
- How to build practical custom hooks: `useToggle`, `useLocalStorage`, `useFetch`, `useDebounce`, `useMediaQuery`, and `useOnClickOutside`
- How to compose hooks together to build more powerful abstractions
- How to test custom hooks
- When to extract a hook and when not to bother
- The critical insight: hooks share logic, NOT state

## Why This Chapter Matters

Imagine you are a chef in a busy restaurant. Every time you make a salad, you wash the lettuce, chop the vegetables, mix the dressing, and plate it. Now imagine doing that exact same process for every single salad order, writing out the full recipe from scratch each time. That would be madness. Instead, you develop a routine -- a repeatable process you can follow without thinking about the steps.

Custom hooks are your reusable recipes for React components. When you find yourself writing the same `useState` + `useEffect` combination in three different components, you are copy-pasting a recipe. Custom hooks let you extract that recipe into a single function you can call anywhere.

Without custom hooks, teams end up with:
- Copy-pasted logic that drifts apart over time
- Bug fixes applied in one place but forgotten in others
- Components bloated with logic that hides the actual UI concerns
- Testing nightmares because logic is tangled with rendering

This chapter teaches you to spot duplicated logic, extract it cleanly, and build a toolkit of hooks that make your entire codebase simpler.

---

## The Problem: Duplicated Stateful Logic

Consider two components that both need to track window width for responsive behavior:

```jsx
// Component A: Navigation
function Navigation() {
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);

  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <nav>
      {windowWidth > 768 ? <DesktopMenu /> : <MobileMenu />}
    </nav>
  );
}

// Component B: Sidebar
function Sidebar() {
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);

  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <aside>
      {windowWidth > 1024 ? <FullSidebar /> : <CollapsedSidebar />}
    </aside>
  );
}
```

The window-tracking logic is identical in both components. If you discover a bug (say, you need to debounce the resize handler for performance), you need to fix it in every single component that uses this pattern. With five components doing this, you have five places to update.

## The Solution: Extract a Custom Hook

A custom hook is simply a JavaScript function whose name starts with `use`. It can call other hooks inside it.

```jsx
// useWindowWidth.js
function useWindowWidth() {
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);

  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return windowWidth;
}
```

Now both components become clean:

```jsx
function Navigation() {
  const windowWidth = useWindowWidth();
  return (
    <nav>
      {windowWidth > 768 ? <DesktopMenu /> : <MobileMenu />}
    </nav>
  );
}

function Sidebar() {
  const windowWidth = useWindowWidth();
  return (
    <aside>
      {windowWidth > 1024 ? <FullSidebar /> : <CollapsedSidebar />}
    </aside>
  );
}
```

Bug fix in one place. Clean components. Testable logic.

---

## Rules of Hooks

Before building custom hooks, you must understand the rules that all hooks follow. These are not suggestions -- React will break if you violate them.

### Rule 1: Only Call Hooks at the Top Level

Hooks must always be called in the same order. Never put them inside conditions, loops, or nested functions.

```jsx
// WRONG - hook inside a condition
function Profile({ userId }) {
  if (userId) {
    const [user, setUser] = useState(null);  // React loses track!
  }
}

// CORRECT - always call, conditionally use
function Profile({ userId }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (userId) {
      fetchUser(userId).then(setUser);
    }
  }, [userId]);
}
```

**Why?** React identifies hooks by their call order. If a hook is sometimes called and sometimes skipped, the order shifts and React pairs the wrong hook with the wrong state.

Think of it like a row of lockers numbered 1, 2, 3. React opens locker 1 for the first `useState`, locker 2 for the second, and so on. If you skip locker 1 sometimes, everything shifts and locker 2 gets locker 1's data.

```
First render:              Second render (if skipped):
+--------+--------+       +--------+--------+
|  Hook  | Locker |       |  Hook  | Locker |
+--------+--------+       +--------+--------+
| state1 |   1    |       | state2 |   1    |  <-- WRONG! state2 gets
| state2 |   2    |       | effect |   2    |      state1's value
| effect |   3    |       +--------+--------+
+--------+--------+
```

### Rule 2: Only Call Hooks from React Functions

Call hooks from React function components or from other custom hooks. Never from regular JavaScript functions, class components, or event handlers.

```jsx
// WRONG - regular function
function getUser() {
  const [user, setUser] = useState(null);  // Not a component or hook!
}

// CORRECT - custom hook (starts with "use")
function useUser() {
  const [user, setUser] = useState(null);
  return user;
}
```

### Rule 3: Custom Hooks Must Start with "use"

This is not just a naming convention. React's linter uses this prefix to check that you follow the other rules.

```jsx
// React linter will NOT check rules for this:
function getToggle() { ... }

// React linter WILL check rules for this:
function useToggle() { ... }
```

---

## Building Practical Custom Hooks

Let us build six hooks that solve real problems you will encounter in production applications.

### Hook 1: useToggle

**Problem:** Many components need a boolean that flips between true and false -- modals, dropdowns, dark mode, show/hide sections.

**Before:**
```jsx
function FAQ() {
  const [isOpen1, setIsOpen1] = useState(false);
  const [isOpen2, setIsOpen2] = useState(false);
  const [isOpen3, setIsOpen3] = useState(false);

  return (
    <div>
      <button onClick={() => setIsOpen1(!isOpen1)}>Question 1</button>
      {isOpen1 && <p>Answer 1</p>}

      <button onClick={() => setIsOpen2(!isOpen2)}>Question 2</button>
      {isOpen2 && <p>Answer 2</p>}

      <button onClick={() => setIsOpen3(!isOpen3)}>Question 3</button>
      {isOpen3 && <p>Answer 3</p>}
    </div>
  );
}
```

**The Hook:**
```jsx
function useToggle(initialValue = false) {
  const [value, setValue] = useState(initialValue);

  const toggle = useCallback(() => setValue(v => !v), []);
  const setTrue = useCallback(() => setValue(true), []);
  const setFalse = useCallback(() => setValue(false), []);

  return [value, toggle, { setTrue, setFalse }];
}
```

**Line-by-line explanation:**
- `function useToggle(initialValue = false)` -- accepts an optional starting value, defaults to false.
- `const [value, setValue] = useState(initialValue)` -- creates the boolean state.
- `const toggle = useCallback(() => setValue(v => !v), [])` -- creates a stable function that flips the value. `useCallback` prevents unnecessary re-renders in child components.
- `const setTrue / setFalse` -- convenience methods for explicit control.
- Returns an array with the value, toggle function, and an object of helpers.

**After:**
```jsx
function FAQ() {
  const [isOpen1, toggleOpen1] = useToggle();
  const [isOpen2, toggleOpen2] = useToggle();
  const [isOpen3, toggleOpen3] = useToggle();

  return (
    <div>
      <button onClick={toggleOpen1}>Question 1</button>
      {isOpen1 && <p>Answer 1</p>}

      <button onClick={toggleOpen2}>Question 2</button>
      {isOpen2 && <p>Answer 2</p>}

      <button onClick={toggleOpen3}>Question 3</button>
      {isOpen3 && <p>Answer 3</p>}
    </div>
  );
}
```

**Output (when user clicks "Question 1"):**
```
Before click:  isOpen1 = false, Question 1 answer hidden
After click:   isOpen1 = true,  Question 1 answer visible
After click:   isOpen1 = false, Question 1 answer hidden again
```

---

### Hook 2: useLocalStorage

**Problem:** You want state that persists across page refreshes. Think user preferences, saved form drafts, or shopping cart items.

**Before:**
```jsx
function Settings() {
  const [theme, setTheme] = useState(() => {
    try {
      const saved = localStorage.getItem('theme');
      return saved ? JSON.parse(saved) : 'light';
    } catch {
      return 'light';
    }
  });

  useEffect(() => {
    localStorage.setItem('theme', JSON.stringify(theme));
  }, [theme]);

  return (
    <button onClick={() => setTheme(t => t === 'light' ? 'dark' : 'light')}>
      Current: {theme}
    </button>
  );
}
```

That is a lot of boilerplate. And you need it for every piece of state you want to persist.

**The Hook:**
```jsx
function useLocalStorage(key, initialValue) {
  // 1. Initialize state from localStorage or fallback
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  // 2. Update localStorage whenever state changes
  useEffect(() => {
    try {
      window.localStorage.setItem(key, JSON.stringify(storedValue));
    } catch (error) {
      console.warn(`Error setting localStorage key "${key}":`, error);
    }
  }, [key, storedValue]);

  // 3. Listen for changes from other tabs
  useEffect(() => {
    const handleStorageChange = (e) => {
      if (e.key === key && e.newValue !== null) {
        setStoredValue(JSON.parse(e.newValue));
      }
    };
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [key]);

  return [storedValue, setStoredValue];
}
```

**Line-by-line explanation:**
- `useState(() => {...})` -- lazy initializer reads from localStorage once on mount.
- `try/catch` -- localStorage can fail (private browsing, storage full, etc.).
- `JSON.parse/stringify` -- handles any serializable value, not just strings.
- The first `useEffect` syncs state changes back to localStorage.
- The second `useEffect` listens for the `storage` event, which fires when another tab changes the same key. This keeps tabs in sync.
- Returns the same `[value, setter]` API as `useState`, making it a drop-in replacement.

**After:**
```jsx
function Settings() {
  const [theme, setTheme] = useLocalStorage('theme', 'light');

  return (
    <button onClick={() => setTheme(t => t === 'light' ? 'dark' : 'light')}>
      Current: {theme}
    </button>
  );
}
```

**Output:**
```
Page load (first time):     theme = "light"    (uses initialValue)
Click button:               theme = "dark"     (saved to localStorage)
Refresh page:               theme = "dark"     (read from localStorage)
```

---

### Hook 3: useFetch

**Problem:** Almost every component that talks to an API needs loading state, error state, and data state. Writing that trio everywhere is tedious and error-prone.

**Before:**
```jsx
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    fetch(`/api/users/${userId}`)
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch');
        return res.json();
      })
      .then(data => {
        setUser(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [userId]);

  if (loading) return <Spinner />;
  if (error) return <Error message={error} />;
  return <div>{user.name}</div>;
}
```

**The Hook:**
```jsx
function useFetch(url, options = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Serialize options to detect real changes
  const optionsKey = JSON.stringify(options);

  useEffect(() => {
    const controller = new AbortController();

    async function fetchData() {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(url, {
          ...options,
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const json = await response.json();
        setData(json);
      } catch (err) {
        if (err.name !== 'AbortError') {
          setError(err.message);
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    fetchData();

    return () => controller.abort();
  }, [url, optionsKey]);

  return { data, loading, error };
}
```

**Line-by-line explanation:**
- `AbortController` -- cancels the fetch if the component unmounts or the URL changes before the request finishes. This prevents the "update state on unmounted component" warning.
- `if (err.name !== 'AbortError')` -- when we abort intentionally, we do not treat it as an error.
- `if (!controller.signal.aborted)` -- only set loading to false if the request was not aborted.
- Returns an object `{ data, loading, error }` so callers can destructure what they need.

**After:**
```jsx
function UserProfile({ userId }) {
  const { data: user, loading, error } = useFetch(`/api/users/${userId}`);

  if (loading) return <Spinner />;
  if (error) return <Error message={error} />;
  return <div>{user.name}</div>;
}
```

**Output (happy path):**
```
Mount:        { data: null,   loading: true,  error: null }
Fetch done:   { data: {name: "Alice"}, loading: false, error: null }
```

**Output (error):**
```
Mount:        { data: null,   loading: true,  error: null }
Fetch fails:  { data: null,   loading: false, error: "HTTP 404: Not Found" }
```

```
Data flow through useFetch:

  Component               useFetch               Server
  ---------               --------               ------
      |                       |                      |
      |-- render(url) ------->|                      |
      |                       |-- fetch(url) ------->|
      |<-- {loading: true} ---|                      |
      |                       |<---- JSON data ------|
      |<-- {data, loading: false} ---|               |
      |                       |                      |
      |-- unmount ----------->|                      |
      |                       |-- abort() ---------->|
```

---

### Hook 4: useDebounce

**Problem:** Some operations should not fire on every keystroke. Search inputs, window resize handlers, and save-as-you-type features all need debouncing -- waiting until the user stops doing something before acting.

Think of an elevator door. It does not close the instant someone presses the button. It waits a moment in case someone else is about to step in. If another person arrives, the timer resets and waits again.

**Before:**
```jsx
function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const timeoutRef = useRef(null);

  const handleChange = (e) => {
    const value = e.target.value;
    setQuery(value);

    if (timeoutRef.current) clearTimeout(timeoutRef.current);

    timeoutRef.current = setTimeout(() => {
      fetch(`/api/search?q=${value}`)
        .then(res => res.json())
        .then(setResults);
    }, 300);
  };

  useEffect(() => {
    return () => clearTimeout(timeoutRef.current);
  }, []);

  return (
    <div>
      <input value={query} onChange={handleChange} />
      <ResultsList results={results} />
    </div>
  );
}
```

**The Hook:**
```jsx
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
```

**Line-by-line explanation:**
- Takes any value and a delay in milliseconds.
- Sets up a timer that updates `debouncedValue` after the delay.
- If `value` changes before the timer fires, the cleanup function runs (`clearTimeout`), canceling the old timer, and a new one starts. This is the "elevator door resetting" behavior.
- Returns the debounced value -- it only changes when the input has been stable for `delay` milliseconds.

**After:**
```jsx
function SearchPage() {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 300);
  const { data: results } = useFetch(
    debouncedQuery ? `/api/search?q=${debouncedQuery}` : null
  );

  return (
    <div>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <ResultsList results={results || []} />
    </div>
  );
}
```

**Output (user types "react" quickly):**
```
Keystroke "r":     query = "r",     debouncedQuery = ""       (no fetch)
Keystroke "e":     query = "re",    debouncedQuery = ""       (timer reset)
Keystroke "a":     query = "rea",   debouncedQuery = ""       (timer reset)
Keystroke "c":     query = "reac",  debouncedQuery = ""       (timer reset)
Keystroke "t":     query = "react", debouncedQuery = ""       (timer reset)
300ms passes:      query = "react", debouncedQuery = "react"  (fetch fires!)
```

Without debouncing: 5 API calls. With debouncing: 1 API call.

---

### Hook 5: useMediaQuery

**Problem:** You need to render different content or apply different logic based on screen size, user preferences (dark mode), or other CSS media query conditions.

**The Hook:**
```jsx
function useMediaQuery(query) {
  const [matches, setMatches] = useState(() => {
    if (typeof window === 'undefined') return false;
    return window.matchMedia(query).matches;
  });

  useEffect(() => {
    const mediaQuery = window.matchMedia(query);
    const handler = (event) => setMatches(event.matches);

    // Modern browsers
    mediaQuery.addEventListener('change', handler);
    // Set initial value
    setMatches(mediaQuery.matches);

    return () => mediaQuery.removeEventListener('change', handler);
  }, [query]);

  return matches;
}
```

**Line-by-line explanation:**
- `window.matchMedia(query)` -- creates a MediaQueryList object that tracks whether the document matches the given CSS media query string.
- The `change` event fires whenever the match status changes (e.g., user resizes the browser past a breakpoint).
- SSR safety: `typeof window === 'undefined'` returns false during server-side rendering.
- Returns a simple boolean: does the query match right now?

**Usage:**
```jsx
function App() {
  const isMobile = useMediaQuery('(max-width: 768px)');
  const prefersDark = useMediaQuery('(prefers-color-scheme: dark)');
  const prefersReducedMotion = useMediaQuery('(prefers-reduced-motion: reduce)');

  return (
    <div className={prefersDark ? 'dark' : 'light'}>
      {isMobile ? <MobileLayout /> : <DesktopLayout />}
      {!prefersReducedMotion && <FancyAnimation />}
    </div>
  );
}
```

**Output (on a phone):**
```
isMobile = true
prefersDark = false  (depends on user's OS setting)
prefersReducedMotion = false

Rendered: <MobileLayout /> with light theme and animations
```

---

### Hook 6: useOnClickOutside

**Problem:** Dropdown menus, modals, and popovers need to close when the user clicks anywhere outside of them.

**The Hook:**
```jsx
function useOnClickOutside(ref, handler) {
  useEffect(() => {
    const listener = (event) => {
      // Do nothing if clicking ref's element or its children
      if (!ref.current || ref.current.contains(event.target)) {
        return;
      }
      handler(event);
    };

    document.addEventListener('mousedown', listener);
    document.addEventListener('touchstart', listener);

    return () => {
      document.removeEventListener('mousedown', listener);
      document.removeEventListener('touchstart', listener);
    };
  }, [ref, handler]);
}
```

**Line-by-line explanation:**
- `ref.current.contains(event.target)` -- checks if the click happened inside the referenced element or any of its children. If it did, we ignore it.
- We listen for both `mousedown` (desktop) and `touchstart` (mobile) to cover all devices.
- We use `mousedown` instead of `click` because `click` fires after `mouseup`, which can cause timing issues where the dropdown opens and immediately closes.

**Usage:**
```jsx
function Dropdown() {
  const [isOpen, toggle, { setFalse: close }] = useToggle();
  const dropdownRef = useRef(null);

  useOnClickOutside(dropdownRef, close);

  return (
    <div ref={dropdownRef}>
      <button onClick={toggle}>Menu</button>
      {isOpen && (
        <ul className="dropdown-menu">
          <li>Profile</li>
          <li>Settings</li>
          <li>Logout</li>
        </ul>
      )}
    </div>
  );
}
```

```
Click behavior:

  +------------------+
  |  [Menu Button]   |  <-- clicking here toggles menu
  |  +------------+  |
  |  | Profile    |  |
  |  | Settings   |  |  <-- clicking inside: menu stays open
  |  | Logout     |  |
  |  +------------+  |
  +------------------+
                          <-- clicking OUTSIDE: menu closes
  Any click out here
  triggers the handler
```

---

## Composing Hooks: Building Bigger From Smaller

One of the most powerful ideas behind custom hooks is composition. You can build complex hooks by combining simpler ones, just like building with LEGO bricks.

### Example: usePaginatedFetch

```jsx
function usePagination(initialPage = 1, pageSize = 10) {
  const [page, setPage] = useState(initialPage);

  const nextPage = useCallback(() => setPage(p => p + 1), []);
  const prevPage = useCallback(() => setPage(p => Math.max(1, p - 1)), []);
  const goToPage = useCallback((p) => setPage(p), []);

  return {
    page,
    pageSize,
    offset: (page - 1) * pageSize,
    nextPage,
    prevPage,
    goToPage,
  };
}
```

Now compose `useFetch` and `usePagination`:

```jsx
function usePaginatedFetch(baseUrl, pageSize = 10) {
  const pagination = usePagination(1, pageSize);
  const url = `${baseUrl}?page=${pagination.page}&limit=${pagination.pageSize}`;
  const { data, loading, error } = useFetch(url);

  return {
    data,
    loading,
    error,
    ...pagination,
  };
}
```

**Usage:**
```jsx
function UserList() {
  const {
    data: users,
    loading,
    error,
    page,
    nextPage,
    prevPage,
  } = usePaginatedFetch('/api/users', 20);

  if (loading) return <Spinner />;
  if (error) return <Error message={error} />;

  return (
    <div>
      <ul>
        {users.map(user => <li key={user.id}>{user.name}</li>)}
      </ul>
      <button onClick={prevPage} disabled={page === 1}>Previous</button>
      <span>Page {page}</span>
      <button onClick={nextPage}>Next</button>
    </div>
  );
}
```

```
Hook composition:

  usePaginatedFetch
  +-----------------------------+
  |  usePagination              |
  |  +-------------------+      |
  |  | page, pageSize,   |      |
  |  | nextPage, prevPage|------+--- builds URL
  |  +-------------------+      |
  |                             |
  |  useFetch(url)              |
  |  +-------------------+      |
  |  | data, loading,    |------+--- returns data
  |  | error             |      |
  |  +-------------------+      |
  +-----------------------------+
```

---

## Critical Insight: Hooks Share Logic, NOT State

This is the most common misconception about custom hooks. If two components call `useToggle()`, they each get their own independent state. The hook shares the logic (the code), not the state (the data).

```jsx
function ComponentA() {
  const [isOpen, toggle] = useToggle(false);
  // isOpen is independent -- changing it does NOT affect ComponentB
  return <button onClick={toggle}>{isOpen ? 'Open' : 'Closed'}</button>;
}

function ComponentB() {
  const [isOpen, toggle] = useToggle(false);
  // This is a COMPLETELY SEPARATE isOpen
  return <button onClick={toggle}>{isOpen ? 'Open' : 'Closed'}</button>;
}
```

```
Two components using useToggle:

  ComponentA                    ComponentB
  +-------------------+        +-------------------+
  | useToggle()       |        | useToggle()       |
  | state: false      |        | state: false      |
  +-------------------+        +-------------------+
        |                            |
  Click toggleA              Click toggleB
        |                            |
  +-------------------+        +-------------------+
  | state: true       |        | state: false      |  <-- independent!
  +-------------------+        +-------------------+
```

If you need shared state between components, you need Context (Chapter 21) or a state management library, not just a custom hook.

---

## Testing Custom Hooks

You cannot call hooks outside of React components. To test them, use `@testing-library/react`'s `renderHook` utility.

```jsx
import { renderHook, act } from '@testing-library/react';

describe('useToggle', () => {
  test('starts with initial value', () => {
    const { result } = renderHook(() => useToggle(false));
    expect(result.current[0]).toBe(false);
  });

  test('toggles value', () => {
    const { result } = renderHook(() => useToggle(false));

    act(() => {
      result.current[1]();  // call toggle
    });

    expect(result.current[0]).toBe(true);
  });

  test('setTrue forces true', () => {
    const { result } = renderHook(() => useToggle(false));

    act(() => {
      result.current[2].setTrue();
    });

    expect(result.current[0]).toBe(true);
  });
});

describe('useDebounce', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  test('returns initial value immediately', () => {
    const { result } = renderHook(() => useDebounce('hello', 500));
    expect(result.current).toBe('hello');
  });

  test('updates value after delay', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'hello', delay: 500 } }
    );

    // Change the value
    rerender({ value: 'world', delay: 500 });

    // Value should not have changed yet
    expect(result.current).toBe('hello');

    // Fast-forward time
    act(() => {
      jest.advanceTimersByTime(500);
    });

    // Now it should be updated
    expect(result.current).toBe('world');
  });
});
```

**Key points about testing hooks:**
- `renderHook` creates a tiny component that calls your hook.
- `result.current` always holds the latest return value.
- `act()` wraps any state updates so React processes them.
- Use `jest.useFakeTimers()` for time-dependent hooks.
- `rerender` lets you simulate prop changes.

---

## When to Extract a Custom Hook

**Extract when:**
- You see the same `useState + useEffect` pattern in 2+ components
- A component has logic that is not related to its rendering
- You want to test stateful logic independently from UI
- The hook has a clear, descriptive name (`useAuth`, `useCart`, `useForm`)

**Do NOT extract when:**
- The logic is used in only one component and is simple
- You are just wrapping a single `useState` call (that adds no value)
- The "hook" would need 10 parameters to be flexible enough
- You are forcing reuse where none naturally exists

```
Decision flow:

  Is the logic used in multiple components?
  ├── Yes --> Extract a hook
  └── No
       |
       Is the logic complex enough to test separately?
       ├── Yes --> Extract a hook
       └── No
            |
            Is the component getting hard to read?
            ├── Yes --> Extract a hook
            └── No  --> Leave it inline
```

---

## Real-World Use Cases

### Form Handling

```jsx
function useForm(initialValues) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});

  const handleChange = useCallback((e) => {
    const { name, value } = e.target;
    setValues(prev => ({ ...prev, [name]: value }));
  }, []);

  const handleBlur = useCallback((e) => {
    const { name } = e.target;
    setTouched(prev => ({ ...prev, [name]: true }));
  }, []);

  const reset = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
  }, [initialValues]);

  return { values, errors, touched, handleChange, handleBlur, reset, setErrors };
}

// Usage
function SignupForm() {
  const { values, errors, handleChange, handleBlur } = useForm({
    email: '',
    password: '',
    name: '',
  });

  return (
    <form>
      <input name="email" value={values.email} onChange={handleChange} onBlur={handleBlur} />
      {errors.email && <span>{errors.email}</span>}
      {/* ... more fields */}
    </form>
  );
}
```

### API State Management

```jsx
function useApiState() {
  const [state, dispatch] = useReducer(apiReducer, {
    data: null,
    loading: false,
    error: null,
  });

  const execute = useCallback(async (apiCall) => {
    dispatch({ type: 'LOADING' });
    try {
      const data = await apiCall();
      dispatch({ type: 'SUCCESS', payload: data });
      return data;
    } catch (error) {
      dispatch({ type: 'ERROR', payload: error.message });
      throw error;
    }
  }, []);

  return { ...state, execute };
}

function apiReducer(state, action) {
  switch (action.type) {
    case 'LOADING':
      return { ...state, loading: true, error: null };
    case 'SUCCESS':
      return { data: action.payload, loading: false, error: null };
    case 'ERROR':
      return { ...state, loading: false, error: action.payload };
    default:
      return state;
  }
}
```

### Responsive Design

```jsx
function useBreakpoint() {
  const isMobile = useMediaQuery('(max-width: 639px)');
  const isTablet = useMediaQuery('(min-width: 640px) and (max-width: 1023px)');
  const isDesktop = useMediaQuery('(min-width: 1024px)');

  if (isMobile) return 'mobile';
  if (isTablet) return 'tablet';
  return 'desktop';
}

// Usage
function Navigation() {
  const breakpoint = useBreakpoint();

  switch (breakpoint) {
    case 'mobile':
      return <HamburgerMenu />;
    case 'tablet':
      return <CompactMenu />;
    case 'desktop':
      return <FullMenu />;
  }
}
```

---

## When to Use / When NOT to Use

### Use Custom Hooks When:
- Multiple components share the same stateful logic
- You want to keep components focused on rendering
- You need to test stateful logic in isolation
- The logic involves `useState`, `useEffect`, or other hooks

### Do NOT Use Custom Hooks When:
- You just need a pure utility function (no hooks inside)
- The abstraction is used only once and is trivial
- You would need too many parameters to make it flexible
- A simple helper function would do the job

---

## Common Mistakes

**1. Not following the naming convention:**
```jsx
// WRONG - React's linter will not enforce hook rules
function fetchData() {
  const [data, setData] = useState(null);
  // ...
}

// CORRECT
function useFetchData() {
  const [data, setData] = useState(null);
  // ...
}
```

**2. Thinking hooks share state:**
```jsx
// WRONG assumption
function ComponentA() {
  const [count, setCount] = useCounter();
  // Changing count here does NOT change it in ComponentB
}
```

**3. Creating hooks that are too specific:**
```jsx
// TOO SPECIFIC - only works for users
function useFetchUsers() {
  return useFetch('/api/users');
}

// BETTER - works for anything
function useFetch(url) {
  // ...
}
```

**4. Not cleaning up effects:**
```jsx
// WRONG - event listener leaks
function useWindowScroll() {
  const [scrollY, setScrollY] = useState(0);
  useEffect(() => {
    window.addEventListener('scroll', () => setScrollY(window.scrollY));
    // Missing cleanup!
  }, []);
  return scrollY;
}

// CORRECT
function useWindowScroll() {
  const [scrollY, setScrollY] = useState(0);
  useEffect(() => {
    const handler = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handler);
    return () => window.removeEventListener('scroll', handler);
  }, []);
  return scrollY;
}
```

**5. Using stale closures:**
```jsx
// WRONG - handler captures stale value
function useInterval(callback, delay) {
  useEffect(() => {
    const id = setInterval(callback, delay);  // callback is stale!
    return () => clearInterval(id);
  }, [delay]);  // callback not in deps
}

// CORRECT - use a ref for the latest callback
function useInterval(callback, delay) {
  const savedCallback = useRef(callback);

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    const id = setInterval(() => savedCallback.current(), delay);
    return () => clearInterval(id);
  }, [delay]);
}
```

---

## Best Practices

1. **Start with the API you want.** Write how you want to use the hook first, then implement it.
2. **Return consistent shapes.** If you return an object, always include the same keys. If you return an array, keep the same order.
3. **Accept configuration, return state and actions.** Hooks take in parameters and return values and functions.
4. **Use `useCallback` for returned functions.** This prevents unnecessary re-renders in components that receive these functions as props.
5. **Handle edge cases.** Think about SSR, initial render, unmounting, rapid state changes.
6. **Write TypeScript types.** Even if you use JavaScript, JSDoc types help.
7. **Keep hooks focused.** One hook, one responsibility. Compose for complexity.

---

## Quick Summary

Custom hooks extract reusable stateful logic from components into standalone functions. They follow the naming convention `useXxx`, obey the rules of hooks (top-level calls only, React functions only), and share logic but not state. You can compose simple hooks into complex ones, test them with `renderHook`, and use them to keep components clean and focused on rendering.

---

## Key Points

- A custom hook is a function starting with `use` that calls other hooks
- Hooks must be called at the top level, never inside conditions or loops
- Each component calling a hook gets its own independent state
- Compose hooks by calling simpler hooks inside more complex ones
- Extract a hook when you see the same stateful pattern in multiple components
- Always clean up effects (event listeners, timers, subscriptions)
- Test hooks with `renderHook` and `act` from testing library

---

## Practice Questions

1. You have three components that all track whether the user is online or offline using `navigator.onLine` and the `online`/`offline` window events. How would you extract this into a custom hook called `useOnlineStatus`? What would it return?

2. Why does calling `useToggle()` in two different components give each component its own independent boolean? What would you need to do if you wanted both components to share the same toggle state?

3. A junior developer wrote a custom hook that calls `useState` inside an `if` statement. The app works on the first render but crashes when the condition changes. Explain why this happens using the "lockers" analogy.

4. You have a `useFetch` hook and a `useDebounce` hook. How would you compose them to create a `useSearch` hook that debounces the search query before making an API call?

5. Your `useLocalStorage` hook works fine when the user changes values in one tab, but the other tab does not update. What browser API would you use to fix this, and how does it work?

---

## Exercises

### Exercise 1: Build useHover

Create a `useHover` hook that returns `[ref, isHovered]`. The caller attaches the `ref` to an element, and `isHovered` becomes `true` when the mouse is over that element.

**Requirements:**
- Returns a ref and a boolean
- Works with any HTML element
- Cleans up event listeners on unmount

**Hint:** Use `useRef` for the element reference and `useState` for the hover state. Set up `mouseenter` and `mouseleave` listeners in a `useEffect`.

### Exercise 2: Build useCountdown

Create a `useCountdown(targetDate)` hook that returns the time remaining until a target date.

**Requirements:**
- Returns `{ days, hours, minutes, seconds }`
- Updates every second
- Returns all zeros when the target date has passed
- Clears the interval when the countdown reaches zero

### Exercise 3: Build usePrevious

Create a `usePrevious(value)` hook that returns the value from the previous render.

**Requirements:**
- Returns `undefined` on the first render
- Returns the previous value on subsequent renders
- Works with any type of value

**Hint:** Use `useRef` to store the previous value and `useEffect` to update it after each render.

---

## What Is Next?

Now that you know how to extract reusable logic into custom hooks, the next chapter explores **Compound Components** -- a pattern for building flexible UI components that work together as a team. You will learn how to create components like `Select/Option` and `Tabs/Tab/TabPanel` that share state implicitly, giving users of your components a clean and flexible API.
