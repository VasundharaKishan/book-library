# Chapter 21: The Provider Pattern

## What You Will Learn

- What the Provider pattern is and the problem it solves (prop drilling)
- How React Context works: `createContext`, `Provider`, and `useContext`
- How to compose multiple providers cleanly
- Performance pitfalls of Context and how to avoid them
- When and how to split contexts for better performance
- How to combine Context with useReducer for complex state

## Why This Chapter Matters

Imagine a large office building. The CEO makes a decision that every employee needs to know. Without an intercom system, the CEO tells the VP, the VP tells each director, each director tells each manager, each manager tells each team lead, and each team lead tells each employee. The message passes through every level, even if the people in the middle do not care about it at all.

This is prop drilling in React. A piece of state lives at the top of the component tree, and you pass it down through every intermediate component until it reaches the one that actually needs it. The intermediate components receive props they do not use, their signatures become cluttered, and refactoring is painful because renaming a prop requires changes at every level.

The Provider pattern solves this with the equivalent of an intercom system: React Context. You "broadcast" state from a provider, and any component in the tree can tune in and receive it directly -- no matter how deep it sits. No intermediaries needed.

---

## The Problem: Prop Drilling

```jsx
// Top-level App has the theme
function App() {
  const [theme, setTheme] = useState('light');

  return (
    <Layout theme={theme}>
      <Sidebar theme={theme}>
        <Navigation theme={theme}>
          <NavItem theme={theme}>Home</NavItem>  {/* Finally uses theme */}
        </Navigation>
      </Sidebar>
    </Layout>
  );
}

// Layout does NOT use theme -- just passes it down
function Layout({ theme, children }) {
  return <div className="layout">{children}</div>;
  // theme is received but never used!
}

// Sidebar does NOT use theme -- just passes it down
function Sidebar({ theme, children }) {
  return <aside className="sidebar">{children}</aside>;
  // theme is received but never used!
}
```

```
Prop Drilling:                        Provider Pattern:

App (theme)                          App
  |                                    |
  v  passes theme                    ThemeProvider (theme)
Layout (theme) -- does not use!        |
  |                                    |  context "broadcast"
  v  passes theme                      |
Sidebar (theme) -- does not use!       v
  |                                  Layout -- no theme prop
  v  passes theme                      |
Navigation (theme) -- does not use!    v
  |                                  Sidebar -- no theme prop
  v  passes theme                      |
NavItem (theme) -- USES IT             v
                                     Navigation -- no theme prop
                                       |
                                       v
                                     NavItem -- useContext(ThemeContext)
```

With prop drilling, four components receive `theme` but only one uses it. With context, only the consumer accesses it.

---

## The Solution: Context + Provider

### Step 1: Create a Context

```jsx
const ThemeContext = React.createContext('light');  // default value
```

The default value is used only when a component reads the context without a provider above it in the tree. Think of it as a fallback.

### Step 2: Create a Provider Component

```jsx
function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  const value = { theme, toggleTheme };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}
```

### Step 3: Create a Custom Hook for Consumption

```jsx
function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
```

### Step 4: Use It

```jsx
function App() {
  return (
    <ThemeProvider>
      <Layout>
        <Sidebar>
          <Navigation>
            <NavItem>Home</NavItem>
          </Navigation>
        </Sidebar>
      </Layout>
    </ThemeProvider>
  );
}

// NavItem consumes the context directly -- no drilling
function NavItem({ children }) {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      className={`nav-item nav-item--${theme}`}
      onClick={toggleTheme}
    >
      {children}
    </button>
  );
}

// Layout, Sidebar, Navigation -- no theme prop at all!
function Layout({ children }) {
  return <div className="layout">{children}</div>;
}
```

Layout, Sidebar, and Navigation are now completely unaware of theme. They do not receive it, pass it, or care about it.

---

## Complete Provider Pattern Implementation

Here is a full, production-quality provider setup:

```jsx
// auth-context.js

const AuthContext = React.createContext();

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing session on mount
    checkAuthSession()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  const login = async (email, password) => {
    const user = await loginAPI(email, password);
    setUser(user);
    return user;
  };

  const logout = async () => {
    await logoutAPI();
    setUser(null);
  };

  const value = useMemo(
    () => ({ user, loading, login, logout }),
    [user, loading]
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export { AuthProvider, useAuth };
```

Usage across the app:

```jsx
// index.jsx
function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes />
      </Router>
    </AuthProvider>
  );
}

// Any component, at any depth
function UserMenu() {
  const { user, logout } = useAuth();

  if (!user) return <LoginButton />;

  return (
    <div>
      <span>{user.name}</span>
      <button onClick={logout}>Log out</button>
    </div>
  );
}

// Another component, completely different part of the tree
function WelcomeBanner() {
  const { user, loading } = useAuth();

  if (loading) return <Spinner />;
  if (!user) return null;

  return <h1>Welcome back, {user.name}!</h1>;
}
```

---

## Multiple Providers: Composition

Real applications need multiple contexts: auth, theme, locale, notifications, feature flags. You compose them by nesting providers:

```jsx
function App() {
  return (
    <AuthProvider>
      <ThemeProvider>
        <LocaleProvider>
          <NotificationProvider>
            <Router>
              <Routes />
            </Router>
          </NotificationProvider>
        </LocaleProvider>
      </ThemeProvider>
    </AuthProvider>
  );
}
```

This nesting is purely visual -- it does not affect performance. Each provider is independent. But if the indentation bothers you, extract a utility:

```jsx
// Compose providers to avoid deep nesting
function ComposeProviders({ providers, children }) {
  return providers.reduceRight(
    (kids, Parent) => <Parent>{kids}</Parent>,
    children
  );
}

function App() {
  return (
    <ComposeProviders
      providers={[
        AuthProvider,
        ThemeProvider,
        LocaleProvider,
        NotificationProvider,
      ]}
    >
      <Router>
        <Routes />
      </Router>
    </ComposeProviders>
  );
}
```

```
Provider composition (nesting):

+-------------------------------------------+
|  AuthProvider                             |
|  +---------------------------------------+|
|  |  ThemeProvider                        ||
|  |  +-----------------------------------+||
|  |  |  LocaleProvider                  |||
|  |  |  +-------------------------------+|||
|  |  |  |  NotificationProvider         ||||
|  |  |  |  +---------------------------+|||||
|  |  |  |  |  <App />                  ||||||
|  |  |  |  +---------------------------+|||||
|  |  |  +-------------------------------+|||
|  |  +-----------------------------------+||
|  +---------------------------------------+|
+-------------------------------------------+

Each component can useAuth(), useTheme(),
useLocale(), or useNotifications() independently.
```

---

## Performance Pitfalls

Context has a critical performance characteristic: **when a context value changes, every component that consumes that context re-renders**. This is by design, but it can cause problems if you are not careful.

### Pitfall 1: Object References Change Every Render

```jsx
// BAD -- new object every render, ALL consumers re-render
function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');

  return (
    <ThemeContext.Provider
      value={{ theme, setTheme }}  // New object every render!
    >
      {children}
    </ThemeContext.Provider>
  );
}
```

Even if `theme` has not changed, every render creates a new `{ theme, setTheme }` object. React sees a different reference and re-renders all consumers.

```jsx
// GOOD -- memoize the value
function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');

  const value = useMemo(
    () => ({ theme, setTheme }),
    [theme]  // Only create a new object when theme actually changes
  );

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}
```

### Pitfall 2: One Fat Context for Everything

```jsx
// BAD -- one context with everything
const AppContext = React.createContext();

function AppProvider({ children }) {
  const [user, setUser] = useState(null);
  const [theme, setTheme] = useState('light');
  const [notifications, setNotifications] = useState([]);
  const [locale, setLocale] = useState('en');

  const value = useMemo(() => ({
    user, setUser,
    theme, setTheme,
    notifications, setNotifications,
    locale, setLocale,
  }), [user, theme, notifications, locale]);

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
}
```

When a new notification arrives, `notifications` changes, which changes the context value, which re-renders **every consumer** -- even components that only use `theme` and never touch notifications.

---

## Splitting Contexts for Performance

The solution is to split unrelated state into separate contexts:

```jsx
// Separate contexts for separate concerns
const AuthContext = React.createContext();
const ThemeContext = React.createContext();
const NotificationContext = React.createContext();

// Each provider manages only its own state
function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const value = useMemo(() => ({ user, setUser }), [user]);
  return (
    <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
  );
}

function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');
  const value = useMemo(() => ({ theme, setTheme }), [theme]);
  return (
    <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
  );
}
```

Now a notification change only re-renders notification consumers. Theme consumers are unaffected.

### Advanced: Splitting State and Dispatch

For a single concern, you can split state (the current value) from dispatch (the updater function) into two contexts:

```jsx
const CountStateContext = React.createContext();
const CountDispatchContext = React.createContext();

function CountProvider({ children }) {
  const [count, setCount] = useState(0);

  return (
    <CountStateContext.Provider value={count}>
      <CountDispatchContext.Provider value={setCount}>
        {children}
      </CountDispatchContext.Provider>
    </CountStateContext.Provider>
  );
}

function useCountState() {
  const context = useContext(CountStateContext);
  if (context === undefined) {
    throw new Error('useCountState must be used within CountProvider');
  }
  return context;
}

function useCountDispatch() {
  const context = useContext(CountDispatchContext);
  if (context === undefined) {
    throw new Error('useCountDispatch must be used within CountProvider');
  }
  return context;
}
```

Why split? Because `setCount` is a stable reference (it never changes), the dispatch context never triggers re-renders. Components that only need to update the count (like a button) do not re-render when the count changes:

```jsx
// This component only dispatches -- it never re-renders when count changes
function IncrementButton() {
  const setCount = useCountDispatch();
  return <button onClick={() => setCount(c => c + 1)}>+1</button>;
}

// This component only reads -- it re-renders when count changes
function CountDisplay() {
  const count = useCountState();
  return <p>Count: {count}</p>;
}
```

---

## Context + useReducer

For complex state with multiple actions, combine Context with `useReducer`:

```jsx
const TodoContext = React.createContext();

function todoReducer(state, action) {
  switch (action.type) {
    case 'ADD_TODO':
      return {
        ...state,
        todos: [...state.todos, {
          id: Date.now(),
          text: action.text,
          completed: false,
        }],
      };
    case 'TOGGLE_TODO':
      return {
        ...state,
        todos: state.todos.map(todo =>
          todo.id === action.id
            ? { ...todo, completed: !todo.completed }
            : todo
        ),
      };
    case 'DELETE_TODO':
      return {
        ...state,
        todos: state.todos.filter(todo => todo.id !== action.id),
      };
    case 'SET_FILTER':
      return { ...state, filter: action.filter };
    default:
      throw new Error(`Unknown action: ${action.type}`);
  }
}

function TodoProvider({ children }) {
  const [state, dispatch] = useReducer(todoReducer, {
    todos: [],
    filter: 'all',
  });

  const value = useMemo(() => ({ state, dispatch }), [state]);

  return (
    <TodoContext.Provider value={value}>
      {children}
    </TodoContext.Provider>
  );
}

function useTodos() {
  const context = useContext(TodoContext);
  if (!context) {
    throw new Error('useTodos must be used within a TodoProvider');
  }
  return context;
}

// Usage
function AddTodo() {
  const { dispatch } = useTodos();
  const [text, setText] = useState('');

  const handleAdd = () => {
    if (text.trim()) {
      dispatch({ type: 'ADD_TODO', text });
      setText('');
    }
  };

  return (
    <div>
      <input value={text} onChange={(e) => setText(e.target.value)} />
      <button onClick={handleAdd}>Add</button>
    </div>
  );
}

function TodoList() {
  const { state, dispatch } = useTodos();

  const filteredTodos = state.todos.filter(todo => {
    if (state.filter === 'active') return !todo.completed;
    if (state.filter === 'completed') return todo.completed;
    return true;
  });

  return (
    <ul>
      {filteredTodos.map(todo => (
        <li key={todo.id}>
          <span
            style={{
              textDecoration: todo.completed ? 'line-through' : 'none'
            }}
            onClick={() => dispatch({ type: 'TOGGLE_TODO', id: todo.id })}
          >
            {todo.text}
          </span>
          <button onClick={() => dispatch({ type: 'DELETE_TODO', id: todo.id })}>
            Delete
          </button>
        </li>
      ))}
    </ul>
  );
}
```

---

## When to Use / When NOT to Use

### Use the Provider Pattern When

- Multiple components at different tree levels need the same data
- Prop drilling through 3+ levels of components that do not use the data
- The data is "global" to a subtree: theme, auth, locale, feature flags
- You are building a component library with compound components (Tabs, Accordions)

### Do NOT Use the Provider Pattern When

- Only one or two components need the data -- just pass props
- The data changes very frequently (like mouse position at 60fps) -- context re-renders too many consumers
- You need to share data across different React roots or between React and non-React code -- use external state management
- You reach for it just to avoid passing props through one level -- that is not prop drilling, that is normal React

---

## Common Mistakes

### Mistake 1: Using Context for Frequently Changing Values

```jsx
// BAD -- mouse position changes 60 times per second
// Every consumer re-renders on every mouse move
function MouseProvider({ children }) {
  const [pos, setPos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handle = (e) => setPos({ x: e.clientX, y: e.clientY });
    window.addEventListener('mousemove', handle);
    return () => window.removeEventListener('mousemove', handle);
  }, []);

  return (
    <MouseContext.Provider value={pos}>
      {children}
    </MouseContext.Provider>
  );
}

// BETTER -- use a ref + subscription pattern, or a state management library
```

### Mistake 2: Not Providing a Custom Hook

```jsx
// BAD -- consumers directly use useContext
function UserMenu() {
  const value = useContext(AuthContext);
  // No error if used outside provider -- just gets undefined
}

// GOOD -- custom hook with error boundary
function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
```

### Mistake 3: Putting Everything in One Context

As covered in the performance section: split unrelated state into separate contexts. Auth changes should not cause theme consumers to re-render.

### Mistake 4: Forgetting the Default Value Semantics

```jsx
// The default value is used ONLY when there is no Provider above
const ThemeContext = React.createContext('light');

// This component uses 'light' because there is no provider
function OrphanedComponent() {
  const theme = useContext(ThemeContext); // 'light' (default)
}

// This component uses 'dark' because the provider overrides the default
function ProvidedComponent() {
  return (
    <ThemeContext.Provider value="dark">
      <Child />  {/* useContext returns 'dark' */}
    </ThemeContext.Provider>
  );
}
```

---

## Best Practices

1. **Always create a custom hook** for each context (`useAuth`, `useTheme`). Never expose the raw context object.

2. **Always validate context usage** -- throw an error in the custom hook if the context is undefined (meaning no provider was found).

3. **Memoize the context value** with `useMemo` to prevent unnecessary consumer re-renders.

4. **Split unrelated concerns** into separate contexts. One context per domain: auth, theme, locale.

5. **Consider splitting state from dispatch** for contexts where some consumers only dispatch actions and never read state.

6. **Co-locate the provider, context, and hook** in one file. Export only the provider and hook, not the raw context.

7. **Use Context for low-frequency state** (theme, auth, locale). For high-frequency updates (animations, cursor position, real-time data), use external state management or refs.

8. **Place providers as low as possible** in the tree. If only a subtree needs the context, do not put the provider at the root.

---

## Quick Summary

The Provider pattern uses React Context to make state available to any component in the tree without prop drilling. A provider component wraps a subtree and broadcasts state; any descendant can consume it via `useContext`. Multiple providers compose by nesting. The main performance concern is that all consumers re-render when the context value changes, which you mitigate by memoizing values, splitting contexts, and separating state from dispatch.

---

## Key Points

- Context eliminates prop drilling: data skips intermediate components
- The pattern has three parts: `createContext`, a Provider component, and a `useContext` consumer hook
- Always create a custom hook that throws if used outside the provider
- Always memoize the context value with `useMemo`
- Split unrelated state into separate contexts to avoid unnecessary re-renders
- Splitting state from dispatch contexts prevents render-only consumers from causing update-only consumers to re-render (and vice versa)
- Context is best for low-frequency, "global" state: theme, auth, locale
- Do not use context for high-frequency data -- it re-renders all consumers on every change
- Compose multiple providers by nesting or with a `ComposeProviders` utility

---

## Practice Questions

1. What is prop drilling, and at what point does it become a problem worth solving with Context?

2. Why is it important to memoize the context value with `useMemo`? What happens if you pass a new object literal directly to `Provider value`?

3. You have a single context providing `{ user, theme, notifications }`. Notifications update every 5 seconds. A component that only reads `theme` re-renders every 5 seconds. Why, and how do you fix it?

4. Explain the difference between the default value passed to `createContext` and the value passed to `<Provider value={...}>`. When does each one get used?

5. Why would you split a context into a "state context" and a "dispatch context"? Give a concrete example of two components that benefit from this split.

---

## Exercises

### Exercise 1: Build an Auth Provider

Build a complete `AuthProvider` with:
- `login(email, password)` function
- `logout()` function
- `user` state (null when logged out)
- `loading` state (true while checking session)
- A custom `useAuth` hook that throws if used outside the provider
- Memoized context value

Build two consumer components: a login form and a user profile dropdown.

### Exercise 2: Build a Notification System

Build a `NotificationProvider` that manages a list of toast notifications:
- `addNotification(message, type)` -- adds a notification (types: success, error, warning)
- Notifications auto-dismiss after 5 seconds
- A `NotificationList` component that renders active notifications
- A custom `useNotification` hook

Split the context so that components that only add notifications do not re-render when the notification list changes.

### Exercise 3: Performance Optimization

Start with a single "AppContext" that provides `{ user, theme, locale, sidebarOpen }`. Build four consumer components, one for each piece of state. Then:
1. Add `console.log` to each consumer to track re-renders
2. Change only the theme and observe that ALL consumers re-render
3. Refactor into separate contexts and verify that only the theme consumer re-renders

---

## What Is Next?

The Provider pattern gives components access to shared state, but who decides how that state changes? In most cases, the provider dictates the state transitions -- the consumer calls `dispatch` or a setter, and the provider's reducer decides what happens. But what if you want the *consumer* to customize those transitions? In Chapter 22, you will learn the State Reducer pattern, which lets consumers override state transitions while the provider maintains sensible defaults.
