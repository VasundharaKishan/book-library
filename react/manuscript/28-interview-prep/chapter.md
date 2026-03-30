# Chapter 28: Interview Preparation

## Learning Goals

By the end of this chapter, you will be able to:

- Answer fundamental React interview questions with confidence and depth
- Explain advanced React concepts clearly to interviewers
- Solve common React coding challenges under time pressure
- Approach system design questions with a structured framework
- Demonstrate practical experience through your explanations
- Avoid common interview pitfalls that trip up even experienced developers
- Prepare effectively with a structured study plan

---

## How React Interviews Work

React interviews typically cover four areas:

1. **Conceptual questions** — testing your understanding of how React works
2. **Coding challenges** — building components or features live
3. **Debugging scenarios** — finding and fixing bugs in provided code
4. **System design** — architecting React applications or features

Most interviews last 45-60 minutes and combine 2-3 of these areas. Senior roles emphasize system design and architecture. Junior roles focus on fundamentals and coding.

The biggest mistake candidates make is memorizing answers. Interviewers can tell. Instead, focus on understanding *why* things work the way they do. If you understand the reasoning, you can answer any variation of a question.

---

## Part 1: Fundamental Questions

These questions appear in nearly every React interview. Master them completely.

### Q1: What is React and why would you use it?

**Strong answer:**

React is a JavaScript library for building user interfaces. It solves the problem of keeping the UI in sync with data by using a declarative approach — you describe what the UI should look like for a given state, and React handles updating the DOM efficiently.

Three key advantages:

- **Component-based architecture** — you build UIs from reusable, self-contained pieces. A Button component works the same everywhere.
- **Virtual DOM** — React compares a virtual representation of the DOM with the actual DOM and applies only the minimum necessary changes. This makes updates fast.
- **Unidirectional data flow** — data flows from parent to child through props, making applications predictable and easier to debug.

*Interview tip:* Mention a specific project where React's benefits helped. "On our e-commerce project, the component model let us build a product card once and reuse it across search results, recommendations, and wishlist pages."

### Q2: What is JSX?

**Strong answer:**

JSX is a syntax extension that lets you write HTML-like code in JavaScript. It is not valid JavaScript — a compiler like Babel transforms it into `React.createElement()` calls before the browser runs it.

```jsx
// What you write:
const element = <h1 className="title">Hello</h1>;

// What the compiler produces:
const element = React.createElement('h1', { className: 'title' }, 'Hello');
```

Key differences from HTML: `className` instead of `class`, `htmlFor` instead of `for`, camelCase attributes, expressions in curly braces, and self-closing tags are required for elements without children.

JSX is optional — you can use `React.createElement` directly — but JSX makes component structure visually clear and is universally used in practice.

### Q3: What is the difference between state and props?

**Strong answer:**

Props are data passed from a parent component to a child. They are read-only — a child cannot modify its props. Think of them as function arguments.

State is data that a component manages internally. It can change over time, typically in response to user actions or API responses. When state changes, the component re-renders.

Key differences:

| | Props | State |
|-|-------|-------|
| Who controls it | Parent component | The component itself |
| Mutable | No (read-only) | Yes (via setter function) |
| Purpose | Configure a component | Track changing data |
| Triggers re-render | When parent re-renders with new props | When setter is called with new value |

```jsx
// count is state in Counter, label is a prop
function Counter({ label }) {
  const [count, setCount] = useState(0);
  return (
    <button onClick={() => setCount(c => c + 1)}>
      {label}: {count}
    </button>
  );
}

// Parent passes the prop
<Counter label="Clicks" />
```

### Q4: What are React hooks? Name the most important ones.

**Strong answer:**

Hooks are functions that let functional components use React features that were previously only available in class components. They follow two rules: only call hooks at the top level (not inside conditions or loops), and only call them from React function components or custom hooks.

The core hooks:

- **`useState`** — adds local state to a component. Returns a value and a setter function.
- **`useEffect`** — runs side effects (data fetching, subscriptions, DOM manipulation) after render. Replaces lifecycle methods.
- **`useRef`** — holds a mutable reference that persists across renders without causing re-renders. Used for DOM access and storing values.
- **`useContext`** — accesses context values without nesting consumers.
- **`useReducer`** — manages complex state with a reducer function. Alternative to useState for state with many transitions.
- **`useMemo`** — memoizes expensive calculations. Recalculates only when dependencies change.
- **`useCallback`** — memoizes functions. Returns the same function reference unless dependencies change.

*Follow-up preparation:* Be ready to explain when you would choose `useReducer` over `useState`, or when `useMemo` is actually worth using.

### Q5: What is the Virtual DOM and how does it work?

**Strong answer:**

The Virtual DOM is a lightweight JavaScript representation of the real DOM. When state changes, React creates a new Virtual DOM tree, compares it with the previous one (a process called "reconciliation" or "diffing"), and calculates the minimum set of DOM operations needed to update the real DOM.

The process:

1. State changes in a component
2. React re-renders the component (calls the function again)
3. React produces a new Virtual DOM tree
4. React compares ("diffs") the new tree with the previous tree
5. React calculates the minimal set of DOM changes
6. React applies only those changes to the real DOM ("commits")

This is faster than naive DOM manipulation because: DOM operations are expensive (they trigger layout and paint), batching multiple changes into one update is more efficient, and React can skip unchanged subtrees entirely.

*Important nuance:* The Virtual DOM is not inherently faster than hand-optimized direct DOM manipulation. Its advantage is that it lets you write declarative code (describe what the UI should look like) while React handles the imperative DOM updates efficiently.

### Q6: Explain the component lifecycle in functional components.

**Strong answer:**

Functional components do not have lifecycle methods like class components. Instead, they use `useEffect` to handle lifecycle events:

```jsx
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);

  // Mounting and updating (replaces componentDidMount + componentDidUpdate)
  useEffect(() => {
    fetchUser(userId).then(setUser);

    // Cleanup (replaces componentWillUnmount)
    return () => {
      // Cancel subscriptions, abort requests, etc.
    };
  }, [userId]);  // Dependency array controls when effect re-runs

  return user ? <h1>{user.name}</h1> : <p>Loading...</p>;
}
```

The lifecycle mapping:

- **Mount** — the component function runs for the first time. Effects with `[]` dependency run after the first render.
- **Update** — the component function runs again when state or props change. Effects run again if their dependencies changed.
- **Unmount** — cleanup functions from effects run. This is where you cancel subscriptions and abort requests.

The key conceptual shift from class components: instead of thinking in lifecycle methods ("do X when the component mounts"), think in synchronization ("keep this effect in sync with these values").

### Q7: What is the difference between controlled and uncontrolled components?

**Strong answer:**

In a **controlled component**, React state drives the form value. The input's value is always set by state, and changes go through an onChange handler:

```jsx
function Controlled() {
  const [value, setValue] = useState('');
  return (
    <input value={value} onChange={e => setValue(e.target.value)} />
  );
}
```

In an **uncontrolled component**, the DOM itself holds the value. You read it when needed using a ref:

```jsx
function Uncontrolled() {
  const inputRef = useRef();
  function handleSubmit() {
    console.log(inputRef.current.value);
  }
  return <input ref={inputRef} defaultValue="" />;
}
```

**When to use each:**

- Controlled: most forms, especially when you need real-time validation, conditional disabling, or formatted input
- Uncontrolled: simple forms where you only need the value on submit, file inputs (`<input type="file">`), or integrating with non-React code

The React recommendation is to use controlled components for most cases because they give you full control over the form data at every moment.

---

## Part 2: Intermediate Questions

These questions test deeper understanding and practical experience.

### Q8: How do you handle side effects in React?

**Strong answer:**

Side effects — data fetching, subscriptions, DOM manipulation, timers — are handled with `useEffect`. The key is getting the dependency array and cleanup right.

```jsx
useEffect(() => {
  // The effect
  const controller = new AbortController();

  async function fetchData() {
    try {
      const response = await fetch(`/api/data/${id}`, {
        signal: controller.signal,
      });
      const data = await response.json();
      setData(data);
    } catch (err) {
      if (err.name !== 'AbortError') {
        setError(err.message);
      }
    }
  }

  fetchData();

  // Cleanup function
  return () => controller.abort();
}, [id]);  // Re-run when id changes
```

Three rules I follow:

1. **One effect per concern** — do not mix unrelated side effects in one useEffect
2. **Always clean up** — abort requests, clear timers, unsubscribe from events
3. **List all dependencies** — never lie about what the effect depends on

For data fetching specifically, in production apps I prefer using a library like TanStack Query because it handles caching, deduplication, background refetching, and error retries — concerns that are complex to implement correctly with raw useEffect.

### Q9: What is Context API and when should you use it?

**Strong answer:**

Context provides a way to pass data through the component tree without passing props through every level. It solves prop drilling — when intermediate components pass props they do not use.

```jsx
const ThemeContext = createContext('light');

function App() {
  const [theme, setTheme] = useState('light');
  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      <Page />
    </ThemeContext.Provider>
  );
}

function DeepChild() {
  const { theme, setTheme } = useContext(ThemeContext);
  // Access theme directly, no prop drilling
}
```

**When to use Context:**
- Theme, locale, and authentication state — data used throughout the app
- Avoiding prop drilling beyond 2-3 levels

**When NOT to use Context:**
- Frequently changing data (like mouse position or real-time input) — every context update re-renders all consumers
- Complex state management — use Zustand, Redux Toolkit, or similar
- Data needed by only a few nearby components — just pass props

*Performance note:* When a context value changes, every component that uses `useContext` for that context re-renders. To minimize unnecessary renders, split contexts by change frequency and memoize the context value if it is an object.

### Q10: How does React handle reconciliation and keys?

**Strong answer:**

Reconciliation is React's process of comparing the old Virtual DOM tree with the new one to determine what changed. React makes two assumptions to keep this fast:

1. Elements of different types produce different trees (a `<div>` becoming a `<span>` means destroy and rebuild)
2. Keys tell React which children in a list are the same between renders

Keys are critical for lists:

```jsx
// Without keys (or with index keys), React matches by position
// If you insert an item at the beginning, every item appears to change

// With stable keys, React matches by key
// It knows which items moved, which are new, which were removed
{users.map(user => (
  <UserCard key={user.id} user={user} />
))}
```

When a key changes, React destroys the old component instance and creates a new one. This is why you can use keys to reset component state:

```jsx
// When userId changes, the entire form resets
<EditUserForm key={userId} user={user} />
```

Index keys are only safe when the list is static and never reordered. For any dynamic list, use a stable unique identifier.

### Q11: How do you optimize React application performance?

**Strong answer:**

I follow a specific approach: measure first, optimize where it matters, and verify the improvement.

**Measuring:**
- React DevTools Profiler to identify slow renders
- Highlight Updates to see what re-renders
- Chrome Performance tab for overall metrics

**Common optimizations:**

1. **Code splitting** — use `React.lazy` and `Suspense` to load routes on demand:
   ```jsx
   const AdminPage = lazy(() => import('./AdminPage'));
   ```

2. **Memoization** (only when measured as needed):
   - `React.memo` for components that re-render with unchanged props
   - `useMemo` for expensive calculations
   - `useCallback` for stable function references passed to memoized children

3. **Virtualization** — for long lists, render only visible items using libraries like `react-window`

4. **State colocation** — keep state as close to where it is used as possible to avoid unnecessary re-renders in unrelated components

5. **Image optimization** — lazy loading, proper sizing, modern formats (WebP, AVIF)

The most impactful optimization is usually code splitting, because it directly reduces the initial bundle size. The least impactful (but most commonly applied) is wrapping everything in `React.memo`.

### Q12: Explain custom hooks. When and why do you create them?

**Strong answer:**

Custom hooks are functions that start with `use` and can call other hooks. They extract reusable stateful logic from components.

```jsx
function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => {
    const stored = localStorage.getItem(key);
    return stored ? JSON.parse(stored) : initialValue;
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue];
}

// Used anywhere:
const [theme, setTheme] = useLocalStorage('theme', 'light');
const [lang, setLang] = useLocalStorage('language', 'en');
```

**When to create a custom hook:**

- The same stateful logic is used in multiple components
- A component's logic is complex enough to benefit from extraction
- You want to make logic independently testable

**Key principles:**

- A custom hook shares *logic*, not *state*. Each component calling `useLocalStorage` gets its own independent state.
- Name hooks descriptively: `useProducts`, `useDebounce`, `useWindowSize` — not `useData` or `useStuff`
- Return consistent shapes: `{ data, loading, error }` or `[value, setValue]`

### Q13: What are error boundaries and how do you use them?

**Strong answer:**

Error boundaries are React components that catch JavaScript errors in their child component tree during rendering, lifecycle methods, and constructors. They prevent one component's crash from taking down the entire application.

Error boundaries must be class components because `componentDidCatch` and `getDerivedStateFromError` have no hook equivalents:

```jsx
class ErrorBoundary extends Component {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    logErrorToService(error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || <h1>Something went wrong.</h1>;
    }
    return this.props.children;
  }
}
```

**What they catch:** Errors during rendering, in lifecycle methods, and in constructors of the whole tree below them.

**What they do NOT catch:** Event handlers (use try/catch), async code (use .catch or try/catch), server-side rendering errors, and errors in the boundary itself.

**Strategy:** Place boundaries at multiple levels — a top-level boundary as a last resort, route-level boundaries so one page does not crash others, and section-level boundaries around independent widgets.

In practice, I use the `react-error-boundary` library which provides a functional API with hooks for resetting and retry logic.

---

## Part 3: Advanced Questions

These questions separate senior candidates from intermediate ones.

### Q14: How would you manage state in a large React application?

**Strong answer:**

I categorize state into four types, each with its own solution:

1. **Local UI state** (form inputs, dropdowns, toggles) → `useState` or `useReducer` in the component

2. **Shared application state** (theme, user preferences, shopping cart) → Context for infrequently changing data, Zustand or Redux Toolkit for frequently changing or complex state

3. **Server state** (data from APIs) → TanStack Query or SWR — these handle caching, background refetching, deduplication, optimistic updates, and error retries. This is the category most developers get wrong by managing server data in client state.

4. **URL state** (search filters, pagination, selected tab) → React Router's `useSearchParams` — the URL is the source of truth, making the state shareable and bookmarkable.

The key insight is that different types of state have different requirements. Server data needs caching and synchronization. UI state needs to be fast and local. Putting everything in one global store creates unnecessary complexity.

For a medium-sized application, my stack would be:
- `useState`/`useReducer` for local state
- Context for auth and theme
- TanStack Query for all API data
- URL search params for filter/sort/pagination state

### Q15: Explain React's rendering behavior. When does a component re-render?

**Strong answer:**

A component re-renders when:

1. Its state changes (via `setState` or `dispatch`)
2. Its parent re-renders (even if props did not change)
3. A context it consumes changes

A component does NOT re-render when:

- Its props change but its parent did not re-render (this cannot happen — props come from the parent)
- A sibling component's state changes
- An unrelated context changes

The re-rendering process:

1. React calls the component function
2. The function returns new JSX
3. React compares this with the previous output (reconciliation)
4. React applies only the differences to the real DOM

**Important nuance:** Re-rendering is NOT the same as re-painting the DOM. React can re-render a component (call its function) and find nothing changed, resulting in zero DOM updates. Re-renders are usually cheap. DOM updates are expensive.

To prevent unnecessary re-renders:
- `React.memo` — skips re-render if props are the same (shallow comparison)
- Proper state colocation — keep state close to where it is used
- Context splitting — separate frequently and infrequently changing context

### Q16: How do you handle authentication in a React SPA?

**Strong answer:**

The standard approach for SPAs:

1. **Auth Context** provides user state, login, logout, and token management to the entire app:

```jsx
function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing token on mount
    const token = localStorage.getItem('token');
    if (token) {
      validateToken(token)
        .then(setUser)
        .catch(() => localStorage.removeItem('token'))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  async function login(credentials) {
    const { user, token } = await authService.login(credentials);
    localStorage.setItem('token', token);
    setUser(user);
  }

  function logout() {
    localStorage.removeItem('token');
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
```

2. **Protected Route** component redirects unauthenticated users:

```jsx
function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) return <Spinner />;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}
```

3. **Token management** — attach tokens to API requests, handle expiration:

```jsx
async function authFetch(url, options = {}) {
  const token = localStorage.getItem('token');
  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${token}`,
    },
  });

  if (response.status === 401) {
    // Token expired — try refresh or redirect to login
    await refreshToken();
    return authFetch(url, options);  // Retry
  }

  return response;
}
```

**Security considerations:** Never store sensitive data in localStorage for high-security apps (XSS risk). Use httpOnly cookies set by the server for the most secure approach. Always validate tokens on the server — client-side checks are for UX, not security.

### Q17: How would you implement code splitting in a React application?

**Strong answer:**

Code splitting breaks your bundle into smaller chunks loaded on demand. In React, the primary tool is `React.lazy` with `Suspense`:

```jsx
// Route-based splitting (most impactful)
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));
const AdminPanel = lazy(() => import('./pages/AdminPanel'));

function App() {
  return (
    <Suspense fallback={<PageSpinner />}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/admin" element={<AdminPanel />} />
      </Routes>
    </Suspense>
  );
}
```

**Other splitting strategies:**

- **Component-based splitting** — lazy load heavy components (rich text editors, chart libraries, modals):
  ```jsx
  const RichEditor = lazy(() => import('./RichEditor'));
  // Only loaded when user clicks "Write Post"
  ```

- **Library-based splitting** — Vite's `manualChunks` to separate vendor code:
  ```jsx
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
        },
      },
    },
  }
  ```

**Measuring impact:** Use `npx vite-bundle-visualizer` to see what is in your bundle. The biggest wins come from splitting routes that most users never visit (admin panels, settings pages, rarely used features).

### Q18: Compare class components and functional components.

**Strong answer:**

Modern React uses functional components with hooks almost exclusively. Here is the comparison:

| Aspect | Class Components | Functional Components |
|--------|-----------------|----------------------|
| Syntax | ES6 class with render() | Plain function returning JSX |
| State | this.state + this.setState | useState hook |
| Lifecycle | componentDidMount, etc. | useEffect |
| Logic reuse | HOCs, render props | Custom hooks |
| Error boundaries | Supported (only option) | Not supported (yet) |
| Performance | Similar | Similar |
| Code volume | More boilerplate | More concise |

Functional components with hooks won because:

1. **Custom hooks** are a better abstraction than HOCs and render props — they compose naturally, avoid wrapper hell, and share logic without sharing JSX
2. **Simpler mental model** — functions are easier to reason about than class instances with `this` binding
3. **Easier to test** — no need to deal with `this`, class instantiation, or lifecycle timing

The one thing class components still provide: error boundaries. There is no hook equivalent for `componentDidCatch`. In practice, you write one error boundary class (or use `react-error-boundary`) and use functional components for everything else.

---

## Part 4: Coding Challenges

These are common challenges you might face in a live coding interview.

### Challenge 1: Debounced Search Input

**Prompt:** Build a search input that calls an API after the user stops typing for 300ms.

```jsx
function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

function SearchInput({ onSearch }) {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 300);

  useEffect(() => {
    if (debouncedQuery) {
      onSearch(debouncedQuery);
    }
  }, [debouncedQuery, onSearch]);

  return (
    <input
      type="search"
      value={query}
      onChange={(e) => setQuery(e.target.value)}
      placeholder="Search..."
      aria-label="Search"
    />
  );
}
```

**What interviewers look for:** Custom hook extraction, proper cleanup with clearTimeout, understanding of closures, accessible markup.

### Challenge 2: Toggle Component with Compound Pattern

**Prompt:** Build a reusable Toggle component using the compound component pattern.

```jsx
const ToggleContext = createContext();

function Toggle({ children, defaultOn = false }) {
  const [on, setOn] = useState(defaultOn);
  const toggle = useCallback(() => setOn(prev => !prev), []);

  return (
    <ToggleContext.Provider value={{ on, toggle }}>
      {children}
    </ToggleContext.Provider>
  );
}

function useToggle() {
  const context = useContext(ToggleContext);
  if (!context) {
    throw new Error('Toggle compound components must be used within <Toggle>');
  }
  return context;
}

Toggle.Button = function ToggleButton({ children, ...props }) {
  const { on, toggle } = useToggle();
  return (
    <button onClick={toggle} aria-pressed={on} {...props}>
      {children || (on ? 'ON' : 'OFF')}
    </button>
  );
};

Toggle.On = function ToggleOn({ children }) {
  const { on } = useToggle();
  return on ? children : null;
};

Toggle.Off = function ToggleOff({ children }) {
  const { on } = useToggle();
  return on ? null : children;
};

// Usage
function App() {
  return (
    <Toggle>
      <Toggle.Button />
      <Toggle.On>
        <p>The toggle is on! Content is visible.</p>
      </Toggle.On>
      <Toggle.Off>
        <p>The toggle is off. Click to reveal content.</p>
      </Toggle.Off>
    </Toggle>
  );
}
```

**What interviewers look for:** Compound component pattern, Context usage, error handling for missing provider, accessible aria-pressed attribute.

### Challenge 3: Infinite Scroll List

**Prompt:** Build a list that loads more items when the user scrolls to the bottom.

```jsx
function useInfiniteScroll(fetchMore, hasMore) {
  const observerRef = useRef(null);
  const sentinelRef = useRef(null);

  useEffect(() => {
    if (!hasMore) return;

    observerRef.current = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          fetchMore();
        }
      },
      { threshold: 0.1 }
    );

    if (sentinelRef.current) {
      observerRef.current.observe(sentinelRef.current);
    }

    return () => observerRef.current?.disconnect();
  }, [fetchMore, hasMore]);

  return sentinelRef;
}

function InfiniteList() {
  const [items, setItems] = useState([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);

  const fetchMore = useCallback(async () => {
    if (loading) return;
    setLoading(true);

    try {
      const response = await fetch(`/api/items?page=${page}`);
      const data = await response.json();

      setItems(prev => [...prev, ...data.items]);
      setHasMore(data.hasMore);
      setPage(prev => prev + 1);
    } catch (err) {
      console.error('Failed to fetch:', err);
    } finally {
      setLoading(false);
    }
  }, [page, loading]);

  const sentinelRef = useInfiniteScroll(fetchMore, hasMore);

  // Load initial data
  useEffect(() => {
    fetchMore();
  }, []);  // Only on mount

  return (
    <div>
      {items.map(item => (
        <div key={item.id} className="list-item">
          <h3>{item.title}</h3>
          <p>{item.description}</p>
        </div>
      ))}

      {loading && <Spinner />}

      {hasMore && <div ref={sentinelRef} style={{ height: 1 }} />}

      {!hasMore && <p>No more items to load.</p>}
    </div>
  );
}
```

**What interviewers look for:** IntersectionObserver knowledge, proper cleanup, preventing duplicate fetches, handling loading and end-of-list states.

### Challenge 4: Multi-Step Form

**Prompt:** Build a multi-step form with validation and the ability to go back.

```jsx
function useMultiStepForm(steps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({});

  function next(stepData) {
    setFormData(prev => ({ ...prev, ...stepData }));
    setCurrentStep(prev => Math.min(prev + 1, steps.length - 1));
  }

  function back() {
    setCurrentStep(prev => Math.max(prev - 1, 0));
  }

  function goTo(step) {
    setCurrentStep(step);
  }

  return {
    currentStep,
    formData,
    next,
    back,
    goTo,
    isFirst: currentStep === 0,
    isLast: currentStep === steps.length - 1,
    StepComponent: steps[currentStep],
  };
}

function RegistrationForm() {
  const steps = [PersonalInfo, AccountInfo, Confirmation];
  const { currentStep, formData, next, back, isFirst, isLast, StepComponent } =
    useMultiStepForm(steps);

  async function handleSubmit(lastStepData) {
    const finalData = { ...formData, ...lastStepData };
    await registerUser(finalData);
  }

  return (
    <div className="form-wizard">
      <ProgressBar current={currentStep} total={steps.length} />
      <StepComponent
        data={formData}
        onNext={isLast ? handleSubmit : next}
        onBack={back}
        isFirst={isFirst}
        isLast={isLast}
      />
    </div>
  );
}

function PersonalInfo({ data, onNext, isFirst }) {
  const [name, setName] = useState(data.name || '');
  const [email, setEmail] = useState(data.email || '');
  const [errors, setErrors] = useState({});

  function handleNext() {
    const newErrors = {};
    if (!name.trim()) newErrors.name = 'Name is required';
    if (!email.trim()) newErrors.email = 'Email is required';
    if (email && !/\S+@\S+\.\S+/.test(email)) newErrors.email = 'Invalid email';

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    onNext({ name, email });
  }

  return (
    <div>
      <h2>Personal Information</h2>
      <div>
        <label htmlFor="name">Name</label>
        <input
          id="name"
          value={name}
          onChange={e => setName(e.target.value)}
          aria-invalid={errors.name ? 'true' : undefined}
        />
        {errors.name && <p className="error">{errors.name}</p>}
      </div>
      <div>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          aria-invalid={errors.email ? 'true' : undefined}
        />
        {errors.email && <p className="error">{errors.email}</p>}
      </div>
      <button onClick={handleNext}>Next</button>
    </div>
  );
}
```

**What interviewers look for:** State management across steps, validation, clean hook API, data preservation when going back.

### Challenge 5: Accessible Modal

**Prompt:** Build an accessible modal dialog.

```jsx
function useFocusTrap(isOpen) {
  const modalRef = useRef(null);

  useEffect(() => {
    if (!isOpen || !modalRef.current) return;

    const modal = modalRef.current;
    const focusableElements = modal.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    // Focus the first element
    firstElement?.focus();

    function handleKeyDown(e) {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement?.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement?.focus();
        }
      }
    }

    modal.addEventListener('keydown', handleKeyDown);
    return () => modal.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  return modalRef;
}

function Modal({ isOpen, onClose, title, children }) {
  const modalRef = useFocusTrap(isOpen);
  const previousFocusRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      previousFocusRef.current = document.activeElement;
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.body.style.overflow = '';
      previousFocusRef.current?.focus();
    };
  }, [isOpen]);

  useEffect(() => {
    function handleEscape(e) {
      if (e.key === 'Escape') onClose();
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return createPortal(
    <div className="modal-overlay" onClick={onClose}>
      <div
        ref={modalRef}
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        onClick={(e) => e.stopPropagation()}
      >
        <header className="modal-header">
          <h2 id="modal-title">{title}</h2>
          <button
            onClick={onClose}
            aria-label="Close dialog"
            className="modal-close"
          >
            ×
          </button>
        </header>
        <div className="modal-body">{children}</div>
      </div>
    </div>,
    document.body
  );
}
```

**What interviewers look for:** Focus trap, focus restoration, Escape key handling, scroll lock, portal rendering, ARIA attributes, click-outside-to-close.

---

## Part 5: System Design Questions

Senior interviews often include system design questions. Here is a framework for answering them.

### Framework: RADIO

Use this structure for any React system design question:

1. **Requirements** — clarify what you are building (features, scale, constraints)
2. **Architecture** — high-level component structure and data flow
3. **Data Model** — state management, API design, caching strategy
4. **Interface** — component API design, props, events
5. **Optimizations** — performance, accessibility, edge cases

### Example: Design a Chat Application

**Requirements:**
- Real-time messaging between users
- Message history with infinite scroll
- Typing indicators
- Online/offline status
- Unread message counts
- Emoji reactions

**Architecture:**

```
App
├── ChatLayout
│   ├── Sidebar
│   │   ├── SearchConversations
│   │   ├── ConversationList
│   │   │   └── ConversationItem (unread badge, last message preview)
│   │   └── UserProfile
│   └── ChatPanel
│       ├── ChatHeader (recipient info, online status)
│       ├── MessageList (virtualized, infinite scroll up)
│       │   └── MessageBubble (text, timestamp, reactions)
│       ├── TypingIndicator
│       └── MessageInput (text, emoji picker, attachments)
```

**Data Model:**

```jsx
// State categories:
// 1. Server state (TanStack Query) — messages, conversations, user profiles
// 2. Real-time state (WebSocket + Zustand) — typing indicators, online status
// 3. Local UI state (useState) — input text, emoji picker open, scroll position

// Zustand store for real-time data
const useChatStore = create((set) => ({
  onlineUsers: new Set(),
  typingUsers: {},  // { conversationId: [userId, ...] }

  setUserOnline: (userId) => set(state => ({
    onlineUsers: new Set([...state.onlineUsers, userId]),
  })),

  setUserOffline: (userId) => set(state => {
    const next = new Set(state.onlineUsers);
    next.delete(userId);
    return { onlineUsers: next };
  }),

  setTyping: (conversationId, userId) => set(state => ({
    typingUsers: {
      ...state.typingUsers,
      [conversationId]: [...(state.typingUsers[conversationId] || []), userId],
    },
  })),
}));
```

**Key Optimizations:**

- **Virtualization** for message list — only render visible messages
- **Optimistic updates** — show sent messages immediately before server confirms
- **WebSocket** for real-time data — typing indicators, new messages, status changes
- **Message pagination** — load older messages on scroll up
- **Debounced typing indicator** — send typing event only while actively typing, with a timeout to stop

**Accessibility:** Announce new messages to screen readers with `aria-live="polite"`, keyboard shortcuts for sending (Enter/Shift+Enter), focus management when switching conversations.

### Example: Design a Dashboard with Widgets

**Requirements:**
- Configurable grid of widgets (charts, stats, tables)
- Drag-and-drop to rearrange
- Each widget fetches its own data
- Widgets can fail independently
- User preferences for layout

**Key Design Decisions:**

1. **Independent error boundaries** per widget — one widget crash does not affect others
2. **Parallel data fetching** — each widget fetches independently, shows its own loading state
3. **Layout stored in user preferences** — saved to API, loaded on mount
4. **Widget registry pattern** — widgets register themselves, dashboard renders dynamically

```jsx
function Dashboard() {
  const { layout, updateLayout } = useDashboardLayout();

  return (
    <DashboardGrid layout={layout} onLayoutChange={updateLayout}>
      {layout.widgets.map(widget => (
        <ErrorBoundary
          key={widget.id}
          fallback={<WidgetError widgetId={widget.id} />}
        >
          <Suspense fallback={<WidgetSkeleton />}>
            <WidgetRenderer type={widget.type} config={widget.config} />
          </Suspense>
        </ErrorBoundary>
      ))}
    </DashboardGrid>
  );
}
```

---

## Part 6: Behavioral and Situational Questions

### "Tell me about a challenging bug you fixed in React."

**Framework:** Situation → Problem → Investigation → Solution → Lesson

**Example answer:**

"We had a checkout form where users reported intermittent data loss. They would fill out shipping information, move to the payment step, go back, and find the shipping fields empty.

The issue was a key prop problem. The form wizard was using the step index as the key on the step components: `<Step key={currentStep} />`. When the user went back from step 2 to step 1, React saw the same key (`1`) and reused the component instance. But the component's `useState` initial values only run once, so the state was stale.

The fix was to remove the key prop entirely and instead use controlled state, keeping the form data in the parent component. Each step read from and wrote to the shared form data object rather than maintaining its own local state.

Lesson: understand what keys do to component lifecycle. A changing key destroys and recreates a component. The same key reuses it — which might not be what you want."

### "How do you approach performance optimization?"

**Example answer:**

"I follow a disciplined process: I only optimize what I can measure. First, I use the React DevTools Profiler to identify which components are slow and why. I look for unnecessary re-renders, expensive computations, and large bundle sizes.

In one project, users complained the product listing page was slow. The Profiler showed that every keystroke in the search input was re-rendering 200 product cards. The fix was three things: debouncing the search input (so we fetched after 300ms of no typing), memoizing the product cards with React.memo (since their props rarely changed), and virtualizing the list so we only rendered the 20 visible cards.

The page went from a 400ms input delay to imperceptible. The key insight was that memoization alone would not have been enough — we needed the debounce to reduce the number of renders, and virtualization to reduce the work per render."

### "How do you handle disagreements about technical decisions?"

**Example answer:**

"I focus on the tradeoffs, not the opinions. When a teammate wanted to use Redux for a new project and I preferred Zustand, I did not argue about which was 'better.' Instead, I listed the specific tradeoffs: Redux has more tooling and a larger community, but requires more boilerplate. Zustand is simpler for our team size and project scope.

We agreed to evaluate both with a small proof-of-concept. After building the same feature with each, the team chose Zustand because our project did not need Redux's middleware ecosystem. If the project had needed complex async workflows or time-travel debugging, Redux would have been the right choice.

The point is not to win the argument — it is to make the best decision for the project with the information available."

---

## Part 7: Quick-Fire Questions and Answers

These short questions often appear in rapid-fire rounds.

**What is the difference between `useEffect` and `useLayoutEffect`?**
`useEffect` runs asynchronously after the browser paints. `useLayoutEffect` runs synchronously after DOM mutations but before the browser paints. Use `useLayoutEffect` when you need to measure or modify the DOM before the user sees it (like measuring element dimensions to position a tooltip). Use `useEffect` for everything else.

**What is `React.StrictMode`?**
A development-only wrapper that helps find potential problems. It renders components twice, runs effects twice, and warns about deprecated APIs. It does not affect production builds. The double-rendering helps catch side effects that should be pure.

**What is prop drilling?**
Passing props through multiple intermediate components that do not use them, just to get data to a deeply nested component. Solve it with Context, composition (children), or a state management library.

**What is the difference between `createElement` and `cloneElement`?**
`createElement` creates a new React element from scratch. `cloneElement` takes an existing element and returns a copy with modified props. `cloneElement` is used in advanced patterns like adding props to children, but it is rare in modern code.

**Can you use hooks in class components?**
No. Hooks can only be used in function components or custom hooks. To use hook-based logic in a class component, you would need to create a wrapper function component.

**What is `React.lazy`?**
A function that lets you dynamically import a component. The component is loaded only when it is first rendered, reducing the initial bundle size. It must be used with `Suspense` which shows a fallback while the component loads.

**What are render props?**
A pattern where a component receives a function as a prop (or as children) and calls that function to determine what to render. Largely replaced by custom hooks, which provide a cleaner API for sharing logic.

**What is `forwardRef`?**
A function that lets a component receive a `ref` and forward it to a child DOM element. Necessary when building reusable components (like custom inputs) that need to expose their internal DOM element to parent components.

**What is the difference between `useMemo` and `useCallback`?**
`useMemo` memoizes a computed value: `useMemo(() => expensiveCalc(a, b), [a, b])`. `useCallback` memoizes a function: `useCallback((x) => doSomething(x, a), [a])`. `useCallback(fn, deps)` is equivalent to `useMemo(() => fn, deps)`.

**What happens if you call `setState` in render?**
It causes an infinite loop — render triggers setState, which triggers render, which triggers setState. React will throw a "Too many re-renders" error. State updates should happen in event handlers or effects, not during render.

---

## Study Plan

### One Week Before the Interview

**Day 1-2: Fundamentals Review**
- Re-read chapters on JSX, components, state, and props
- Practice explaining each concept out loud in 2 minutes
- Build a simple counter and todo list from scratch without looking at references

**Day 3-4: Hooks Deep Dive**
- Review useState, useEffect, useRef, useContext, useReducer
- Build a custom hook (useLocalStorage or useDebounce) from memory
- Practice explaining when to use each hook

**Day 5: Advanced Concepts**
- Review performance optimization, error boundaries, Context
- Practice explaining the rendering process and reconciliation
- Build an accessible modal from scratch

**Day 6: Coding Practice**
- Time yourself solving 3 coding challenges (30 minutes each)
- Practice thinking out loud while coding
- Build a debounced search input, a multi-step form, and an infinite scroll list

**Day 7: Mock Interview**
- Have a friend ask you 5 random questions from this chapter
- Practice the STAR method for behavioral questions
- Review any weak areas

### During the Interview

1. **Listen carefully** — make sure you understand the question before answering
2. **Think out loud** — interviewers want to see your thought process
3. **Start simple** — get a basic solution working, then iterate
4. **Ask clarifying questions** — "Should this handle error states?" "What browsers do we need to support?"
5. **Acknowledge tradeoffs** — "I chose this approach because... The tradeoff is..."
6. **Write clean code** — even under time pressure, use clear variable names and consistent formatting
7. **Test your code** — mentally walk through your solution with a few test cases

### Common Mistakes to Avoid

- **Over-engineering** — keep solutions simple, do not add Redux for a todo list
- **Not handling edge cases** — always mention loading, error, and empty states
- **Forgetting accessibility** — labels, keyboard navigation, ARIA attributes
- **Ignoring performance** — mention when optimization would matter, even if you do not implement it
- **Memorized answers** — understand the *why*, not just the *what*

---

## Summary

React interviews test three things: your understanding of concepts, your ability to write working code, and your judgment in making technical decisions.

For conceptual questions, focus on understanding *why* things work the way they do. If you understand that React re-renders components to keep the UI in sync with state, you can answer any question about rendering, effects, or performance.

For coding challenges, practice building components from scratch under time constraints. The most common challenges — debounced inputs, modals, infinite scroll, multi-step forms — test the same fundamental skills: state management, effects, event handling, and clean component design.

For system design questions, use the RADIO framework (Requirements, Architecture, Data Model, Interface, Optimizations) to structure your answer. The interviewer cares more about your thought process than a perfect solution.

And for behavioral questions, prepare specific examples from your experience. The best answers follow a clear structure: what the situation was, what you did, and what you learned.

The most important preparation is building real things. Every project you build, every bug you fix, and every component you refactor gives you experience that no amount of memorization can replace.

---

## What Is Next?

In Chapter 29, we will build a **Real-World Project from Scratch** — a complete application that combines everything you have learned throughout this book. We will walk through the entire process: planning, architecture, building features, handling authentication, testing, and deploying to production. This capstone project will solidify your skills and give you a portfolio piece you can show in interviews.
