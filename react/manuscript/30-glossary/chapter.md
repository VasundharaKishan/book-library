# Glossary of React Terms

A comprehensive reference of every important concept, function, and pattern covered in this book. Terms are organized alphabetically for quick lookup.

---

### AbortController

A browser API used to cancel fetch requests. In React, you create an AbortController in a `useEffect`, pass its signal to `fetch`, and call `abort()` in the cleanup function to prevent race conditions when the component unmounts or dependencies change.

```jsx
useEffect(() => {
  const controller = new AbortController();
  fetch(url, { signal: controller.signal }).then(/* ... */);
  return () => controller.abort();
}, [url]);
```

*Chapter 8, Chapter 16*

---

### Accessibility (a11y)

The practice of making web applications usable by everyone, including people who use screen readers, keyboard navigation, or other assistive technologies. Key practices include semantic HTML, ARIA attributes, proper focus management, and alt text for images.

*Chapter 20*

---

### ARIA (Accessible Rich Internet Applications)

A set of HTML attributes that provide additional semantics for assistive technologies. Common attributes include `aria-label`, `aria-labelledby`, `aria-describedby`, `aria-hidden`, `aria-live`, `aria-expanded`, `aria-pressed`, and `role`.

*Chapter 20*

---

### Barrel Export

An `index.js` file that re-exports from other files in a directory, creating a clean public API. Barrel exports simplify imports and define which parts of a module are meant to be used externally.

```jsx
// features/auth/index.js
export { LoginForm } from './components/LoginForm';
export { useAuth } from './hooks/useAuth';
export { AuthProvider } from './context/AuthContext';
```

*Chapter 25*

---

### Batching

React's optimization of grouping multiple state updates into a single re-render. In React 18+, batching happens automatically for all state updates, including those inside promises, timeouts, and event handlers.

*Chapter 5*

---

### BrowserRouter

A React Router component that uses the HTML5 History API to keep the URL in sync with the UI. Wraps the application to enable client-side routing.

```jsx
<BrowserRouter>
  <App />
</BrowserRouter>
```

*Chapter 15*

---

### Bundle

The compiled JavaScript file(s) produced by a build tool like Vite. Bundling combines your source files, resolves imports, and produces optimized output for production. Code splitting breaks the bundle into smaller chunks loaded on demand.

*Chapter 24*

---

### Cache Busting

A technique where filenames include a content hash (e.g., `app-abc123.js`) so browsers always load the latest version. Vite handles this automatically for imported assets.

*Chapter 26*

---

### Children (props.children)

A special prop that contains the content placed between a component's opening and closing tags. Used for composition and building flexible container components.

```jsx
function Card({ children }) {
  return <div className="card">{children}</div>;
}

<Card>
  <h2>Title</h2>
  <p>Content goes here</p>
</Card>
```

*Chapter 4*

---

### Class Component

The older style of React component using ES6 classes. Class components extend `React.Component`, use `this.state` and `this.setState()` for state, and lifecycle methods like `componentDidMount`. Largely replaced by functional components with hooks, but still required for error boundaries.

*Chapter 19*

---

### Client-Side Routing

Navigation that happens entirely in the browser without full page reloads. React Router intercepts link clicks, updates the URL, and renders the appropriate component — making navigation feel instant.

*Chapter 15*

---

### clsx / cn

A utility library for conditionally joining CSS class names. Often wrapped in a `cn()` helper function for convenience.

```jsx
import clsx from 'clsx';
className={clsx('btn', isActive && 'active', size === 'large' && 'btn-lg')}
```

*Chapter 17*

---

### Code Splitting

Breaking your JavaScript bundle into smaller chunks that are loaded on demand. In React, this is done with `React.lazy()` and `Suspense`. Route-based splitting is the most impactful approach.

```jsx
const Dashboard = lazy(() => import('./pages/Dashboard'));
```

*Chapter 24*

---

### Compound Component

A pattern where a parent component shares state with its children through Context, allowing flexible composition. Components like `<Tabs>`, `<Tab>`, and `<TabPanel>` work together as a unit.

*Chapter 28*

---

### Component

A reusable, self-contained piece of UI. In modern React, components are functions that accept props and return JSX. Components can manage their own state and compose with other components.

*Chapter 4*

---

### Composition

Building complex UIs by combining simpler components. Preferred over inheritance in React. The `children` prop is the primary mechanism for composition.

*Chapter 4, Chapter 25*

---

### Conditional Rendering

Showing or hiding parts of the UI based on conditions. Common patterns include `if/else` with early returns, ternary operators (`condition ? <A /> : <B />`), and logical AND (`condition && <Component />`).

*Chapter 7*

---

### Context API

A React feature for passing data through the component tree without prop drilling. Consists of `createContext`, a `Provider` component, and `useContext` hook. Best for infrequently changing data like theme, locale, or auth state.

```jsx
const ThemeContext = createContext('light');
// Provider: <ThemeContext.Provider value={theme}>
// Consumer: const theme = useContext(ThemeContext);
```

*Chapter 13*

---

### Controlled Component

A form element whose value is driven by React state. The component's displayed value always matches state, and changes go through an `onChange` handler.

```jsx
<input value={name} onChange={e => setName(e.target.value)} />
```

*Chapter 9*

---

### createContext

A React function that creates a Context object. Takes a default value used when no Provider is found above the consuming component.

*Chapter 13*

---

### createPortal

A React DOM function that renders children into a DOM node outside the parent component's hierarchy. Used for modals, tooltips, and overlays.

```jsx
createPortal(<Modal />, document.body)
```

*Chapter 19, Chapter 28*

---

### createRoot

The React 18+ API for rendering the root component. Replaces the older `ReactDOM.render`.

```jsx
createRoot(document.getElementById('root')).render(<App />);
```

*Chapter 2*

---

### CSS Modules

A CSS approach where class names are automatically scoped to the component. Files use the `.module.css` extension, and classes are imported as a JavaScript object.

```jsx
import styles from './Button.module.css';
<button className={styles.primary}>Click</button>
```

*Chapter 17*

---

### Custom Hook

A JavaScript function that starts with `use` and calls other hooks. Custom hooks extract reusable stateful logic from components. They share logic, not state — each component calling the hook gets its own independent state.

```jsx
function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => {
    const stored = localStorage.getItem(key);
    return stored ? JSON.parse(stored) : initialValue;
  });
  useEffect(() => localStorage.setItem(key, JSON.stringify(value)), [key, value]);
  return [value, setValue];
}
```

*Chapter 12*

---

### Dark Mode

A UI theme with a dark background and light text. Typically implemented with CSS custom properties and a `data-theme` attribute on the root element, toggled via React context.

*Chapter 17, Chapter 26*

---

### Debouncing

Delaying execution of a function until after a pause in events. Commonly used for search inputs to avoid making API calls on every keystroke.

```jsx
function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return debouncedValue;
}
```

*Chapter 12, Chapter 16*

---

### Dependency Array

The second argument to `useEffect`, `useMemo`, and `useCallback`. It tells React when to re-run the function. An empty array (`[]`) means "run once on mount." Omitting it means "run after every render."

*Chapter 8*

---

### Derived State

A value calculated from existing state during render, rather than stored as separate state. Always preferred over synchronizing state in effects.

```jsx
// Good: derived during render
const total = items.reduce((sum, item) => sum + item.price, 0);

// Bad: synchronized in effect
useEffect(() => setTotal(items.reduce(...)), [items]);
```

*Chapter 5, Chapter 27*

---

### Destructuring

A JavaScript syntax for extracting values from objects or arrays. Commonly used for props and hook return values.

```jsx
function UserCard({ name, email }) { ... }  // Object destructuring
const [count, setCount] = useState(0);       // Array destructuring
```

*Chapter 3*

---

### DevTools (React)

A browser extension for debugging React applications. The Components tab shows the component tree with props and state. The Profiler tab measures rendering performance.

*Chapter 22*

---

### DOM (Document Object Model)

The browser's tree representation of an HTML document. React uses a Virtual DOM to efficiently update the real DOM.

*Chapter 1*

---

### Environment Variables

Configuration values set outside the code, loaded from `.env` files. In Vite, only variables prefixed with `VITE_` are exposed to client-side code. They are embedded at build time and are always strings.

```bash
VITE_API_URL=https://api.example.com
```

```jsx
const apiUrl = import.meta.env.VITE_API_URL;
```

*Chapter 24, Chapter 26*

---

### Error Boundary

A class component that catches JavaScript errors in its child component tree and displays a fallback UI instead of crashing the entire application. Uses `getDerivedStateFromError` and `componentDidCatch`.

*Chapter 19*

---

### Event Handler

A function called in response to a user action (click, submit, change, etc.). In React, events use camelCase naming (`onClick`, `onChange`) and receive a synthetic event object.

```jsx
function handleClick(e) {
  e.preventDefault();
  // handle the event
}
<button onClick={handleClick}>Click</button>
```

*Chapter 6*

---

### Feature-Based Architecture

A project structure that organizes code by domain/feature (auth, products, cart) rather than by type (components, hooks, services). Each feature is a self-contained module with its own components, hooks, services, and public API.

*Chapter 25*

---

### Fetch API

The browser's built-in API for making HTTP requests. Returns a Promise that resolves to a Response object. Check `response.ok` before parsing JSON.

```jsx
const response = await fetch('/api/data');
if (!response.ok) throw new Error(`HTTP ${response.status}`);
const data = await response.json();
```

*Chapter 16*

---

### Focus Management

Controlling which element has keyboard focus, especially during interactions like opening modals, navigating between pages, or after form submission. Critical for accessibility.

*Chapter 20*

---

### Focus Trap

A technique that constrains keyboard focus within a specific container (like a modal). Tab and Shift+Tab cycle through focusable elements inside the container without escaping to the page behind it.

*Chapter 20, Chapter 28*

---

### forwardRef

A React function that lets a component receive a `ref` and forward it to a child DOM element. Used when building reusable form components or other elements that need to expose their DOM node.

```jsx
const Input = forwardRef(function Input(props, ref) {
  return <input ref={ref} {...props} />;
});
```

*Chapter 10*

---

### Fragment

A React component (`<>...</>` or `<React.Fragment>`) that groups children without adding an extra DOM node. Use when you need to return multiple elements from a component.

```jsx
return (
  <>
    <h1>Title</h1>
    <p>Content</p>
  </>
);
```

*Chapter 3*

---

### Functional Component

A React component written as a JavaScript function. Receives props as an argument and returns JSX. The standard way to write components in modern React.

```jsx
function Greeting({ name }) {
  return <h1>Hello, {name}!</h1>;
}
```

*Chapter 4*

---

### HOC (Higher-Order Component)

A function that takes a component and returns a new enhanced component. An older pattern for reusing logic, largely replaced by custom hooks.

*Chapter 12*

---

### Hook

A function that lets functional components use React features like state, effects, and context. Built-in hooks include `useState`, `useEffect`, `useRef`, `useContext`, `useReducer`, `useMemo`, and `useCallback`. Custom hooks are functions starting with `use` that compose built-in hooks.

*Chapter 5, Chapter 8, Chapter 10, Chapter 11, Chapter 12, Chapter 13, Chapter 14*

---

### Hydration

The process where a server-rendered HTML page is made interactive by attaching React event handlers. Used in SSR/SSG frameworks like Next.js.

*Chapter 24*

---

### Immutability

The practice of never modifying existing objects or arrays directly. Instead, create new copies with the changes. Required for React to detect state changes.

```jsx
// Wrong: mutation
items.push(newItem);

// Right: new array
setItems(prev => [...prev, newItem]);
```

*Chapter 5, Chapter 27*

---

### import.meta.env

The Vite API for accessing environment variables. Provides `VITE_`-prefixed variables, plus built-in values like `DEV`, `PROD`, and `MODE`.

*Chapter 24, Chapter 26*

---

### IntersectionObserver

A browser API that detects when an element enters or leaves the viewport. Used in React for lazy loading images, infinite scroll, and triggering animations on scroll.

*Chapter 16*

---

### JSX

A syntax extension that lets you write HTML-like code in JavaScript. Compiled by tools like Babel into `React.createElement()` calls. Key differences from HTML: `className` instead of `class`, camelCase attributes, expressions in curly braces.

*Chapter 3*

---

### JWT (JSON Web Token)

A compact, self-contained token used for authentication. Contains encoded user information and is typically sent in the `Authorization` header. Consists of three parts: header, payload, and signature.

*Chapter 23*

---

### Key (prop)

A special string prop used when rendering lists. Keys help React identify which items changed, were added, or removed. Must be stable, unique among siblings, and not use array indices for dynamic lists.

```jsx
{items.map(item => <ListItem key={item.id} item={item} />)}
```

*Chapter 7*

---

### Lazy Loading

Loading code or assets only when they are needed. `React.lazy()` loads components on demand. The `loading="lazy"` HTML attribute defers image loading until near the viewport.

*Chapter 24, Chapter 26*

---

### Lifting State Up

Moving state from a child component to a parent when multiple children need to share or synchronize that state. The parent passes state down as props and handlers for updating it.

*Chapter 5*

---

### Memoization

Caching the result of a computation to avoid recalculating it when inputs have not changed. In React: `React.memo` for components, `useMemo` for values, and `useCallback` for functions.

*Chapter 11*

---

### NavLink

A React Router component that works like `Link` but adds styling attributes (like `className` or `style`) based on whether the route matches the current URL.

*Chapter 15*

---

### Optimistic Update

Updating the UI immediately before the server confirms the change, then reverting if the request fails. Provides instant feedback to users.

```jsx
// 1. Update UI immediately
setItems(prev => prev.filter(i => i.id !== id));
// 2. Make API call
try { await api.delete(id); }
catch { fetchItems(); }  // 3. Revert on failure
```

*Chapter 16*

---

### Outlet

A React Router component used in parent routes to render the matched child route's component. Enables nested routing with shared layouts.

*Chapter 15*

---

### Path Alias

A mapping from a short prefix (like `@shared`) to a directory path, configured in the build tool. Replaces deep relative imports with clean absolute-style imports.

```jsx
// Instead of: import { Button } from '../../../../shared/components';
import { Button } from '@shared/components';
```

*Chapter 25*

---

### Portal

See **createPortal**.

---

### Profiler

A React DevTools tool that measures component rendering performance. Shows which components rendered, how long they took, and what triggered the render.

*Chapter 22*

---

### Prop Drilling

Passing props through multiple intermediate components that do not use them, just to reach a deeply nested component. Solved with Context API, composition, or state management libraries.

*Chapter 13*

---

### Props

Short for "properties." Data passed from a parent component to a child component. Props are read-only — a child cannot modify them.

*Chapter 4*

---

### Protected Route

A route component that checks authentication status before rendering its children. Redirects to a login page if the user is not authenticated.

*Chapter 15, Chapter 23*

---

### Provider (Context)

A component that makes a context value available to all descendants. Any component in the tree below the Provider can access the value with `useContext`.

```jsx
<ThemeContext.Provider value={theme}>
  {children}
</ThemeContext.Provider>
```

*Chapter 13*

---

### Race Condition

A bug where the result depends on the timing of asynchronous operations. In React, this commonly occurs when a component unmounts or updates before a fetch completes. Solved with AbortController or cleanup flags.

*Chapter 8, Chapter 16*

---

### React.lazy

A function for dynamic imports of components. The component is loaded only when it is first rendered. Must be used with `Suspense`.

*Chapter 24*

---

### React.memo

A higher-order component that memoizes a functional component. Skips re-rendering if props are the same (shallow comparison). Use only when profiling reveals unnecessary re-renders.

```jsx
const MemoizedCard = React.memo(function Card({ title }) {
  return <div>{title}</div>;
});
```

*Chapter 11*

---

### React.StrictMode

A development-only wrapper that helps find potential problems. It intentionally double-renders components and double-runs effects to expose side effects. Has no effect in production.

*Chapter 2*

---

### Reconciliation

React's process of comparing the new Virtual DOM tree with the previous one to determine the minimum DOM changes needed. Also called "diffing."

*Chapter 1, Chapter 28*

---

### Reducer

A pure function that takes the current state and an action, and returns the new state. Used with `useReducer` for complex state logic.

```jsx
function reducer(state, action) {
  switch (action.type) {
    case 'INCREMENT': return { count: state.count + 1 };
    case 'DECREMENT': return { count: state.count - 1 };
    default: return state;
  }
}
```

*Chapter 14*

---

### Ref

A mutable container that persists across renders without causing re-renders. Created with `useRef`. Used for DOM element access, storing previous values, and holding mutable values like timers.

```jsx
const inputRef = useRef(null);
inputRef.current.focus();  // Access DOM element
```

*Chapter 10*

---

### Render

The process of React calling a component function to produce JSX. Rendering does not necessarily mean the DOM changes — React may render and find nothing needs updating. A component renders when its state changes, its parent re-renders, or a consumed context changes.

*Chapter 5, Chapter 28*

---

### Render Props

A pattern where a component receives a function as a prop and calls it to determine what to render. Largely replaced by custom hooks.

*Chapter 12*

---

### Route

A React Router component that defines a URL path and the component to render when the path matches.

```jsx
<Route path="/products/:id" element={<ProductPage />} />
```

*Chapter 15*

---

### Server-Side Rendering (SSR)

Rendering React components on the server and sending the HTML to the browser. Improves initial load time and SEO. Frameworks like Next.js provide SSR out of the box.

*Chapter 24*

---

### Side Effect

Any operation that affects something outside the component's rendering: API calls, subscriptions, DOM manipulation, timers, or logging. Managed with `useEffect` in React.

*Chapter 8*

---

### SPA (Single-Page Application)

A web application that loads a single HTML page and dynamically updates content as the user navigates. React applications are typically SPAs with client-side routing.

*Chapter 15*

---

### Spread Operator

JavaScript's `...` syntax for expanding objects or arrays. Used extensively in React for passing props and creating new state objects.

```jsx
const newUser = { ...user, name: 'New Name' };
<Button {...props} />
```

*Chapter 3, Chapter 4*

---

### State

Data managed within a component that can change over time. When state changes, the component re-renders. Created with `useState` or `useReducer`.

*Chapter 5*

---

### Stale Closure

A bug where a function captures an outdated value from a previous render. Common in effects and event handlers. Solved with functional state updates, refs, or correct dependency arrays.

```jsx
// Stale: uses old count
setCount(count + 1);

// Fresh: always uses latest
setCount(prev => prev + 1);
```

*Chapter 22, Chapter 27*

---

### Static Site Generation (SSG)

Pre-rendering pages at build time as static HTML. Provides fast load times and works well for content that does not change frequently. Supported by frameworks like Next.js and Astro.

*Chapter 24*

---

### Suspense

A React component that displays a fallback UI while waiting for lazy-loaded components or async operations to complete.

```jsx
<Suspense fallback={<Spinner />}>
  <LazyComponent />
</Suspense>
```

*Chapter 24*

---

### Synthetic Event

React's cross-browser wrapper around native browser events. Provides a consistent API regardless of browser. Includes methods like `preventDefault()` and `stopPropagation()`.

*Chapter 6*

---

### Tailwind CSS

A utility-first CSS framework that provides pre-built classes for styling directly in JSX. Classes like `flex`, `p-4`, `text-lg`, and `bg-blue-500` compose to build any design.

*Chapter 17*

---

### TanStack Query (React Query)

A library for managing server state (data from APIs). Handles caching, background refetching, deduplication, pagination, optimistic updates, and error retries.

*Chapter 18*

---

### Tree Shaking

A build optimization that removes unused code from the final bundle. Works with ES module `import`/`export` syntax. Vite and other modern build tools perform tree shaking automatically.

*Chapter 24*

---

### Uncontrolled Component

A form element that manages its own state internally through the DOM. Values are read with refs rather than controlled by React state. Used for simple forms or file inputs.

```jsx
const inputRef = useRef();
<input ref={inputRef} defaultValue="initial" />
// Read: inputRef.current.value
```

*Chapter 9*

---

### useCallback

A hook that memoizes a function, returning the same reference unless dependencies change. Use when passing callbacks to memoized child components.

```jsx
const handleClick = useCallback((id) => {
  deleteItem(id);
}, [deleteItem]);
```

*Chapter 11*

---

### useContext

A hook that reads a context value. Returns the current value from the nearest Provider above the component.

```jsx
const theme = useContext(ThemeContext);
```

*Chapter 13*

---

### useEffect

A hook for performing side effects after render. Replaces `componentDidMount`, `componentDidUpdate`, and `componentWillUnmount` from class components.

```jsx
useEffect(() => {
  // Effect code
  return () => { /* cleanup */ };
}, [dependency]);
```

*Chapter 8*

---

### useLayoutEffect

Like `useEffect` but runs synchronously after DOM mutations and before the browser paints. Use for measuring or modifying the DOM before the user sees it. Prefer `useEffect` for most cases.

*Chapter 10*

---

### useMemo

A hook that memoizes a computed value, recalculating only when dependencies change. Use for genuinely expensive calculations.

```jsx
const sorted = useMemo(
  () => items.sort((a, b) => a.name.localeCompare(b.name)),
  [items]
);
```

*Chapter 11*

---

### useNavigate

A React Router hook that returns a function for programmatic navigation. Replaces `useHistory` from older versions.

```jsx
const navigate = useNavigate();
navigate('/dashboard');
navigate(-1);  // Go back
```

*Chapter 15*

---

### useParams

A React Router hook that returns an object of URL parameters from the current route.

```jsx
// Route: /products/:id
const { id } = useParams();
```

*Chapter 15*

---

### useReducer

A hook for managing complex state with a reducer function. Alternative to `useState` when state has many sub-values or transitions depend on the previous state.

```jsx
const [state, dispatch] = useReducer(reducer, initialState);
dispatch({ type: 'ADD_ITEM', payload: newItem });
```

*Chapter 14*

---

### useRef

A hook that returns a mutable ref object with a `.current` property. The ref persists across renders and does not trigger re-renders when changed. Used for DOM access and storing mutable values.

```jsx
const inputRef = useRef(null);
const timerRef = useRef(null);
```

*Chapter 10*

---

### useSearchParams

A React Router hook for reading and modifying URL query parameters.

```jsx
const [searchParams, setSearchParams] = useSearchParams();
const page = searchParams.get('page');
setSearchParams({ page: '2', sort: 'name' });
```

*Chapter 15*

---

### useState

The most fundamental hook. Adds state to a functional component. Returns the current value and a setter function.

```jsx
const [count, setCount] = useState(0);
setCount(5);              // Direct value
setCount(prev => prev + 1);  // Functional update
```

*Chapter 5*

---

### Virtual DOM

A lightweight JavaScript representation of the real DOM. React uses it to efficiently determine what changed between renders and apply only the minimum necessary DOM updates.

*Chapter 1*

---

### Vite

A modern build tool for web development. Provides fast development server with hot module replacement (HMR) and optimized production builds. The recommended tool for new React projects.

*Chapter 2*

---

### WebP / AVIF

Modern image formats that provide better compression than JPEG and PNG. WebP is 25-35% smaller; AVIF is up to 50% smaller. Use the `<picture>` element for format fallbacks.

*Chapter 26*

---

### XSS (Cross-Site Scripting)

A security vulnerability where malicious scripts are injected into web pages. React prevents most XSS by escaping text content by default. The `dangerouslySetInnerHTML` prop bypasses this protection and should only be used with sanitized content.

*Chapter 23, Chapter 27*

---

### Zustand

A lightweight state management library for React. Uses a simple store-based API with hooks. Smaller and simpler than Redux, suitable for most applications.

```jsx
const useStore = create((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
}));

const count = useStore((state) => state.count);
```

*Chapter 18*

---

*This glossary covers the terms and concepts from all 29 chapters of this book. For detailed explanations, code examples, and best practices for any term, refer to the chapter listed after each entry.*
