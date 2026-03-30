# Chapter 13: Context API and Prop Drilling Solutions

---

## Learning Goals

By the end of this chapter, you will be able to:

- Explain what prop drilling is and why it is a problem
- Create, provide, and consume React Context
- Use the `useContext` hook to access context values
- Build practical contexts for themes, authentication, and notifications
- Update context values from deeply nested components
- Split context into separate read and write contexts for performance
- Compose multiple contexts together
- Know when to use Context and when other solutions are better
- Avoid common Context performance pitfalls

---

## The Prop Drilling Problem

As applications grow, you often need to pass data from a top-level component to a deeply nested one. With props, every component in between must receive and forward the data — even if those intermediate components do not use it.

```jsx
function App() {
  const [user, setUser] = useState({ name: "Alice", role: "admin" });
  const [theme, setTheme] = useState("dark");

  return (
    <Layout user={user} theme={theme}>
      <Sidebar user={user} theme={theme}>
        <Navigation user={user} theme={theme}>
          <UserMenu user={user} theme={theme} />
        </Navigation>
      </Sidebar>
      <MainContent theme={theme}>
        <Dashboard user={user} theme={theme}>
          <WelcomeMessage user={user} />
        </Dashboard>
      </MainContent>
    </Layout>
  );
}
```

**Problems with this approach:**

1. **Boilerplate.** Every intermediate component must accept and forward props it does not use.
2. **Fragile.** Adding a new prop means updating every component in the chain.
3. **Hard to read.** It is difficult to trace where data comes from when it passes through 5+ levels.
4. **Tight coupling.** Intermediate components are coupled to data they do not care about.

```
App (owns user and theme)
  │
  ├── Layout (passes through user, theme) ← does not use them
  │   ├── Sidebar (passes through user, theme) ← does not use them
  │   │   └── Navigation (passes through user, theme) ← does not use them
  │   │       └── UserMenu (USES user, theme) ← finally uses them!
  │   └── MainContent (passes through theme) ← does not use it
  │       └── Dashboard (passes through user, theme) ← does not use them
  │           └── WelcomeMessage (USES user) ← finally uses it!
```

Only `UserMenu` and `WelcomeMessage` need the data, but six components have to know about it.

---

## What Is Context?

React Context provides a way to pass data through the component tree without manually passing props at every level. It creates a "broadcast channel" — a component at the top provides data, and any component below can consume it directly, no matter how deep it is.

```
App (provides user and theme via Context)
  │
  ├── Layout ← no props needed
  │   ├── Sidebar ← no props needed
  │   │   └── Navigation ← no props needed
  │   │       └── UserMenu ← reads from Context directly
  │   └── MainContent ← no props needed
  │       └── Dashboard ← no props needed
  │           └── WelcomeMessage ← reads from Context directly
```

---

## Creating and Using Context

There are three steps:

1. **Create** the context with `createContext()`
2. **Provide** the context value with a `<Provider>` component
3. **Consume** the context value with the `useContext()` hook

### Step 1: Create

```jsx
import { createContext } from "react";

const ThemeContext = createContext("light"); // "light" is the default value
```

The argument to `createContext` is the default value — used when a component reads the context but there is no Provider above it in the tree. In practice, you almost always have a Provider, so the default is mainly for TypeScript types or as a fallback.

### Step 2: Provide

```jsx
function App() {
  const [theme, setTheme] = useState("dark");

  return (
    <ThemeContext.Provider value={theme}>
      <Layout />
    </ThemeContext.Provider>
  );
}
```

The `Provider` wraps the part of the tree that needs access to the value. Every component inside the Provider can read the value.

### Step 3: Consume

```jsx
import { useContext } from "react";

function Button({ children }) {
  const theme = useContext(ThemeContext);

  return (
    <button
      style={{
        backgroundColor: theme === "dark" ? "#2d3748" : "#ffffff",
        color: theme === "dark" ? "#ffffff" : "#2d3748",
        border: `1px solid ${theme === "dark" ? "#4a5568" : "#e2e8f0"}`,
        padding: "0.5rem 1rem",
        borderRadius: "4px",
        cursor: "pointer",
      }}
    >
      {children}
    </button>
  );
}
```

`useContext(ThemeContext)` returns whatever value was passed to the nearest `ThemeContext.Provider` above this component. If there is no Provider, it returns the default value from `createContext`.

### Complete Example

```jsx
import { createContext, useContext, useState } from "react";

// 1. Create
const ThemeContext = createContext("light");

// 2. Provide
function App() {
  const [theme, setTheme] = useState("light");

  function toggleTheme() {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  }

  return (
    <ThemeContext.Provider value={theme}>
      <div style={{
        minHeight: "100vh",
        backgroundColor: theme === "dark" ? "#1a202c" : "#ffffff",
        color: theme === "dark" ? "#e2e8f0" : "#1a202c",
        padding: "2rem",
        transition: "all 0.3s ease",
      }}>
        <h1>Theme Demo</h1>
        <button onClick={toggleTheme}>
          Switch to {theme === "light" ? "Dark" : "Light"} Mode
        </button>
        <Toolbar />
        <Content />
      </div>
    </ThemeContext.Provider>
  );
}

function Toolbar() {
  return (
    <nav style={{ margin: "1rem 0", display: "flex", gap: "0.5rem" }}>
      <ThemedButton>Home</ThemedButton>
      <ThemedButton>About</ThemedButton>
      <ThemedButton>Contact</ThemedButton>
    </nav>
  );
}

function Content() {
  return (
    <main>
      <Card title="Welcome">
        <p>This card adapts to the current theme.</p>
      </Card>
    </main>
  );
}

// 3. Consume
function ThemedButton({ children }) {
  const theme = useContext(ThemeContext);

  return (
    <button style={{
      backgroundColor: theme === "dark" ? "#4a5568" : "#edf2f7",
      color: theme === "dark" ? "#e2e8f0" : "#2d3748",
      border: "none",
      padding: "0.5rem 1rem",
      borderRadius: "6px",
      cursor: "pointer",
    }}>
      {children}
    </button>
  );
}

function Card({ title, children }) {
  const theme = useContext(ThemeContext);

  return (
    <div style={{
      backgroundColor: theme === "dark" ? "#2d3748" : "#f7fafc",
      border: `1px solid ${theme === "dark" ? "#4a5568" : "#e2e8f0"}`,
      borderRadius: "8px",
      padding: "1.5rem",
      marginTop: "1rem",
    }}>
      <h2>{title}</h2>
      {children}
    </div>
  );
}

export default App;
```

**Notice:** `Toolbar` and `Content` do not receive any theme prop. `ThemedButton` and `Card` read the theme directly from Context. The intermediate components are completely unaware of the theme.

---

## Passing Functions Through Context (Updating Context)

Often, child components need to not only read context values but also update them. The solution is to include the update function in the context value:

```jsx
import { createContext, useContext, useState } from "react";

// Create context with both value and updater
const ThemeContext = createContext({
  theme: "light",
  toggleTheme: () => {},
});

function ThemeProvider({ children }) {
  const [theme, setTheme] = useState("light");

  function toggleTheme() {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  }

  // Pass both value and updater
  const value = { theme, toggleTheme };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

// Custom hook for convenience
function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
}

// Usage — any nested component can toggle the theme
function ThemeToggleButton() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button onClick={toggleTheme}>
      Current: {theme} — Click to switch
    </button>
  );
}

// App setup
function App() {
  return (
    <ThemeProvider>
      <div>
        <h1>App</h1>
        <Toolbar />
      </div>
    </ThemeProvider>
  );
}

function Toolbar() {
  return <ThemeToggleButton />;
}
```

**The Provider pattern:**

1. Create a `ThemeProvider` component that manages the state and provides the value.
2. Create a `useTheme` custom hook that consumes the context (with an error check).
3. Consumers call `useTheme()` to read and update the theme.

This pattern encapsulates all theme logic in one place. Components do not need to know about `createContext` or `ThemeContext` — they just call `useTheme()`.

---

## Real-World Context: Authentication

A practical authentication context:

```jsx
import { createContext, useContext, useState, useCallback } from "react";

const AuthContext = createContext(null);

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const login = useCallback(async (email, password) => {
    setIsLoading(true);
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      if (email === "user@example.com" && password === "password") {
        const userData = { id: 1, name: "Alice", email, role: "admin" };
        setUser(userData);
        localStorage.setItem("user", JSON.stringify(userData));
        return { success: true };
      }
      return { success: false, error: "Invalid credentials" };
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    localStorage.removeItem("user");
  }, []);

  const value = {
    user,
    isAuthenticated: user !== null,
    isLoading,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

// ── Components that use auth ──────────────────────

function LoginForm() {
  const { login, isLoading } = useAuth();
  const [email, setEmail] = useState("user@example.com");
  const [password, setPassword] = useState("password");
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    const result = await login(email, password);
    if (!result.success) {
      setError(result.error);
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: "300px", margin: "2rem auto" }}>
      <h2>Login</h2>
      {error && <p style={{ color: "#e53e3e" }}>{error}</p>}
      <div style={{ marginBottom: "0.75rem" }}>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          disabled={isLoading}
          style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
        />
      </div>
      <div style={{ marginBottom: "0.75rem" }}>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          disabled={isLoading}
          style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
        />
      </div>
      <button type="submit" disabled={isLoading} style={{ width: "100%", padding: "0.5rem" }}>
        {isLoading ? "Logging in..." : "Log In"}
      </button>
    </form>
  );
}

function UserHeader() {
  const { user, logout } = useAuth();

  return (
    <div style={{
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      padding: "0.75rem 1rem",
      backgroundColor: "#f7fafc",
      borderBottom: "1px solid #e2e8f0",
    }}>
      <span>Welcome, <strong>{user.name}</strong> ({user.role})</span>
      <button onClick={logout} style={{ padding: "0.25rem 0.75rem" }}>
        Logout
      </button>
    </div>
  );
}

function ProtectedContent() {
  const { user } = useAuth();

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Dashboard</h1>
      <p>You are logged in as {user.email}.</p>
      {user.role === "admin" && (
        <div style={{ marginTop: "1rem", padding: "1rem", backgroundColor: "#ebf8ff", borderRadius: "8px" }}>
          <h3>Admin Panel</h3>
          <p>You have admin access.</p>
        </div>
      )}
    </div>
  );
}

// ── Root App ──────────────────────

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

function AppContent() {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <LoginForm />;
  }

  return (
    <div>
      <UserHeader />
      <ProtectedContent />
    </div>
  );
}

export default App;
```

**The auth flow:**

```
App
└── AuthProvider (manages user state, login, logout)
    └── AppContent
        ├── Not authenticated → LoginForm
        │   └── Calls login() from useAuth()
        │   └── On success → user state updates → AppContent re-renders
        │
        └── Authenticated → UserHeader + ProtectedContent
            ├── UserHeader reads user, calls logout()
            └── ProtectedContent reads user for role-based content
```

---

## Real-World Context: Notification System

```jsx
import { createContext, useContext, useState, useCallback } from "react";

const NotificationContext = createContext(null);

function NotificationProvider({ children }) {
  const [notifications, setNotifications] = useState([]);

  const addNotification = useCallback((message, type = "info", duration = 5000) => {
    const id = Date.now() + Math.random();
    const notification = { id, message, type };

    setNotifications((prev) => [...prev, notification]);

    // Auto-remove after duration
    if (duration > 0) {
      setTimeout(() => {
        setNotifications((prev) => prev.filter((n) => n.id !== id));
      }, duration);
    }

    return id;
  }, []);

  const removeNotification = useCallback((id) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  }, []);

  // Convenience methods
  const success = useCallback((msg) => addNotification(msg, "success"), [addNotification]);
  const error = useCallback((msg) => addNotification(msg, "error", 8000), [addNotification]);
  const warning = useCallback((msg) => addNotification(msg, "warning"), [addNotification]);
  const info = useCallback((msg) => addNotification(msg, "info"), [addNotification]);

  const value = {
    notifications,
    addNotification,
    removeNotification,
    success,
    error,
    warning,
    info,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
      <NotificationList />
    </NotificationContext.Provider>
  );
}

function useNotifications() {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error("useNotifications must be used within a NotificationProvider");
  }
  return context;
}

function NotificationList() {
  const { notifications, removeNotification } = useNotifications();

  if (notifications.length === 0) return null;

  const colors = {
    success: { bg: "#c6f6d5", border: "#38a169", text: "#22543d" },
    error: { bg: "#fed7d7", border: "#e53e3e", text: "#742a2a" },
    warning: { bg: "#fefcbf", border: "#d69e2e", text: "#744210" },
    info: { bg: "#bee3f8", border: "#3182ce", text: "#2a4365" },
  };

  return (
    <div style={{
      position: "fixed",
      top: "1rem",
      right: "1rem",
      width: "320px",
      display: "flex",
      flexDirection: "column",
      gap: "0.5rem",
      zIndex: 1000,
    }}>
      {notifications.map((notification) => {
        const color = colors[notification.type] || colors.info;
        return (
          <div
            key={notification.id}
            style={{
              backgroundColor: color.bg,
              border: `1px solid ${color.border}`,
              color: color.text,
              padding: "0.75rem 1rem",
              borderRadius: "8px",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
              animation: "slideIn 0.3s ease",
            }}
          >
            <span>{notification.message}</span>
            <button
              onClick={() => removeNotification(notification.id)}
              style={{
                backgroundColor: "transparent",
                border: "none",
                color: color.text,
                cursor: "pointer",
                fontSize: "1.25rem",
                lineHeight: 1,
                padding: "0 0 0 0.5rem",
              }}
            >
              x
            </button>
          </div>
        );
      })}
      <style>{`@keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }`}</style>
    </div>
  );
}

// ── Usage ──────────────────────

function App() {
  return (
    <NotificationProvider>
      <DemoPage />
    </NotificationProvider>
  );
}

function DemoPage() {
  const notify = useNotifications();

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Notification Demo</h1>
      <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
        <button onClick={() => notify.success("File saved successfully!")}>
          Success
        </button>
        <button onClick={() => notify.error("Failed to delete item.")}>
          Error
        </button>
        <button onClick={() => notify.warning("Your session will expire in 5 minutes.")}>
          Warning
        </button>
        <button onClick={() => notify.info("New update available.")}>
          Info
        </button>
      </div>
    </div>
  );
}

export default App;
```

**Key design:** The `NotificationList` component is rendered inside the Provider itself. This means any component that wraps with `NotificationProvider` automatically gets the notification UI. Components just call `notify.success("Message")` — they never think about where notifications are displayed.

---

## Multiple Contexts

An application typically has several contexts. Nest the providers at the top level:

```jsx
function App() {
  return (
    <AuthProvider>
      <ThemeProvider>
        <NotificationProvider>
          <Router>
            <AppContent />
          </Router>
        </NotificationProvider>
      </ThemeProvider>
    </AuthProvider>
  );
}
```

Each provider is independent. Components consume only the contexts they need:

```jsx
function UserSettings() {
  const { user } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const notify = useNotifications();

  function handleSave() {
    // Save settings...
    notify.success("Settings saved!");
  }

  return (
    <div>
      <h2>Settings for {user.name}</h2>
      <button onClick={toggleTheme}>
        Theme: {theme}
      </button>
      <button onClick={handleSave}>Save</button>
    </div>
  );
}
```

### Reducing Provider Nesting

If you have many providers, the nesting can get deep. A common pattern is a `Providers` component:

```jsx
function Providers({ children }) {
  return (
    <AuthProvider>
      <ThemeProvider>
        <NotificationProvider>
          {children}
        </NotificationProvider>
      </ThemeProvider>
    </AuthProvider>
  );
}

function App() {
  return (
    <Providers>
      <AppContent />
    </Providers>
  );
}
```

Or a utility that composes providers:

```jsx
function ComposeProviders({ providers, children }) {
  return providers.reduceRight(
    (child, Provider) => <Provider>{child}</Provider>,
    children
  );
}

function App() {
  return (
    <ComposeProviders providers={[AuthProvider, ThemeProvider, NotificationProvider]}>
      <AppContent />
    </ComposeProviders>
  );
}
```

---

## Context Performance Considerations

### The Re-Render Problem

When a context value changes, **every component** that calls `useContext` for that context re-renders — even if it only uses a part of the value that did not change.

```jsx
const AppContext = createContext(null);

function AppProvider({ children }) {
  const [user, setUser] = useState(null);
  const [theme, setTheme] = useState("light");
  const [notifications, setNotifications] = useState([]);

  // ❌ Every change to user, theme, OR notifications re-renders ALL consumers
  const value = { user, setUser, theme, setTheme, notifications, setNotifications };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

function ThemeToggle() {
  // This component only uses theme, but re-renders when user or notifications change too!
  const { theme, setTheme } = useContext(AppContext);
  return <button onClick={() => setTheme(t => t === "light" ? "dark" : "light")}>{theme}</button>;
}
```

### Solution 1: Split Into Separate Contexts

The simplest fix — split unrelated data into separate contexts:

```jsx
// Each context manages one concern
const AuthContext = createContext(null);
const ThemeContext = createContext(null);
const NotificationContext = createContext(null);

// Now ThemeToggle only re-renders when theme changes
function ThemeToggle() {
  const { theme, toggleTheme } = useContext(ThemeContext);
  return <button onClick={toggleTheme}>{theme}</button>;
}
```

When `user` changes, only `AuthContext` consumers re-render. `ThemeContext` and `NotificationContext` consumers are unaffected.

### Solution 2: Stabilize the Value Object

When you pass an object as the context value, a new object is created on every render — causing all consumers to re-render:

```jsx
// ❌ New object on every render of AuthProvider
function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  return (
    <AuthContext.Provider value={{ user, setUser }}>
      {children}
    </AuthContext.Provider>
  );
}
```

Fix with `useMemo`:

```jsx
// ✅ Same object unless user actually changes
function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  const value = useMemo(() => ({ user, setUser }), [user]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
```

### Solution 3: Split State and Dispatch Contexts

For contexts where many components update but few read (or vice versa):

```jsx
const TodoStateContext = createContext(null);
const TodoDispatchContext = createContext(null);

function TodoProvider({ children }) {
  const [todos, setTodos] = useState([]);

  const dispatch = useMemo(() => ({
    add: (text) => setTodos((prev) => [...prev, { id: Date.now(), text, done: false }]),
    toggle: (id) => setTodos((prev) => prev.map((t) => t.id === id ? { ...t, done: !t.done } : t)),
    remove: (id) => setTodos((prev) => prev.filter((t) => t.id !== id)),
  }), []); // dispatch functions never change

  return (
    <TodoStateContext.Provider value={todos}>
      <TodoDispatchContext.Provider value={dispatch}>
        {children}
      </TodoDispatchContext.Provider>
    </TodoStateContext.Provider>
  );
}

function useTodoState() {
  return useContext(TodoStateContext);
}

function useTodoDispatch() {
  return useContext(TodoDispatchContext);
}

// Component that only adds — does NOT re-render when todos change
function AddTodoForm() {
  const { add } = useTodoDispatch();
  const [text, setText] = useState("");

  function handleSubmit(event) {
    event.preventDefault();
    if (text.trim()) {
      add(text.trim());
      setText("");
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input value={text} onChange={(e) => setText(e.target.value)} />
      <button type="submit">Add</button>
    </form>
  );
}

// Component that reads todos — re-renders when todos change
function TodoList() {
  const todos = useTodoState();
  const { toggle, remove } = useTodoDispatch();

  return (
    <ul>
      {todos.map((todo) => (
        <li key={todo.id}>
          <input type="checkbox" checked={todo.done} onChange={() => toggle(todo.id)} />
          <span style={{ textDecoration: todo.done ? "line-through" : "none" }}>
            {todo.text}
          </span>
          <button onClick={() => remove(todo.id)}>x</button>
        </li>
      ))}
    </ul>
  );
}
```

**Why this works:** `AddTodoForm` only uses `useTodoDispatch()`. The dispatch functions are memoized and never change, so `AddTodoForm` never re-renders when todos update. Only `TodoList` (which reads `useTodoState()`) re-renders when todos change.

---

## Context vs Other Solutions

### When to Use Context

- **Theme data** (dark/light mode, brand colors)
- **Authentication state** (current user, login/logout)
- **Locale/language** preferences
- **UI state** that many components need (sidebar open/closed, modal state)
- **Data that changes infrequently** and is needed by many components

### When NOT to Use Context

- **Frequently changing data** (mouse position, animation frames) — every change re-renders all consumers.
- **Complex state logic** with many actions — use `useReducer` with Context, or a state management library.
- **Server data caching** — use a data fetching library (TanStack Query, SWR) instead.
- **Data that only a parent and child need** — props are simpler and more explicit.

### Context vs Props

```
Use Props when:
├── Data flows 1-2 levels deep
├── The receiving component directly uses the data
├── You want explicit, traceable data flow
└── Only a few components need the data

Use Context when:
├── Data flows 3+ levels deep
├── Many components at different levels need the data
├── Intermediate components should not know about the data
└── The data changes infrequently
```

### Context vs State Management Libraries

Context is not a replacement for Redux, Zustand, or other state management libraries. Context is a **dependency injection mechanism** — it solves where data comes from, not how complex state is managed.

```
Context alone:           Good for simple, app-wide state (theme, auth, locale)
Context + useReducer:    Good for moderately complex state with clear actions
Redux / Zustand:         Good for complex state with many updates, middleware, dev tools
TanStack Query / SWR:    Good for server state (API data caching, syncing)
```

---

## The Complete Context Pattern

Here is the recommended pattern for building a context module:

```jsx
// contexts/CartContext.jsx
import { createContext, useContext, useState, useMemo, useCallback } from "react";

// 1. Create context
const CartContext = createContext(null);

// 2. Provider component
export function CartProvider({ children }) {
  const [items, setItems] = useState([]);

  const addItem = useCallback((product) => {
    setItems((prev) => {
      const existing = prev.find((item) => item.id === product.id);
      if (existing) {
        return prev.map((item) =>
          item.id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      }
      return [...prev, { ...product, quantity: 1 }];
    });
  }, []);

  const removeItem = useCallback((productId) => {
    setItems((prev) => prev.filter((item) => item.id !== productId));
  }, []);

  const updateQuantity = useCallback((productId, quantity) => {
    if (quantity <= 0) {
      setItems((prev) => prev.filter((item) => item.id !== productId));
    } else {
      setItems((prev) =>
        prev.map((item) =>
          item.id === productId ? { ...item, quantity } : item
        )
      );
    }
  }, []);

  const clearCart = useCallback(() => setItems([]), []);

  const totalItems = items.reduce((sum, item) => sum + item.quantity, 0);
  const totalPrice = items.reduce((sum, item) => sum + item.price * item.quantity, 0);

  const value = useMemo(() => ({
    items,
    addItem,
    removeItem,
    updateQuantity,
    clearCart,
    totalItems,
    totalPrice,
  }), [items, addItem, removeItem, updateQuantity, clearCart, totalItems, totalPrice]);

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
}

// 3. Custom hook with error boundary
export function useCart() {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error("useCart must be used within a CartProvider");
  }
  return context;
}
```

**The pattern checklist:**

1. Context created in its own file
2. Provider component manages all state and logic
3. Functions memoized with `useCallback`
4. Value object memoized with `useMemo`
5. Custom hook with descriptive name
6. Error thrown if used outside Provider
7. Only the hook and Provider are exported (context itself is private)

---

## Common Mistakes

1. **Putting too much in one context.**

   ```jsx
   // ❌ One giant context — everything re-renders when anything changes
   const AppContext = createContext({ user, theme, cart, notifications, settings });

   // ✅ Separate contexts for separate concerns
   const AuthContext = createContext(null);
   const ThemeContext = createContext(null);
   const CartContext = createContext(null);
   ```

2. **Creating a new value object on every render.**

   ```jsx
   // ❌ New object every render — all consumers re-render
   <MyContext.Provider value={{ user, theme }}>

   // ✅ Memoize the value
   const value = useMemo(() => ({ user, theme }), [user, theme]);
   <MyContext.Provider value={value}>
   ```

3. **Using context for data that changes very frequently.**

   ```jsx
   // ❌ Mouse position updates 60+ times per second — all consumers re-render
   <MouseContext.Provider value={{ x: mouseX, y: mouseY }}>

   // ✅ Use state in the component that needs it, or use a ref
   ```

4. **Not creating a custom hook.**

   ```jsx
   // ❌ Consuming directly — no error check, verbose
   const value = useContext(ThemeContext);

   // ✅ Custom hook — error check, clean API
   const { theme, toggleTheme } = useTheme();
   ```

5. **Using context when props would be simpler.**

   Context is not needed for passing data one or two levels. Props are more explicit and easier to trace.

---

## Best Practices

1. **One context per concern.** Theme, auth, cart, notifications — each gets its own context.

2. **Always create a custom hook** (`useTheme`, `useAuth`, `useCart`) that wraps `useContext` with an error check. This is your public API — consumers never import the raw context.

3. **Memoize the context value** with `useMemo` to prevent unnecessary re-renders.

4. **Memoize callback functions** with `useCallback` so consumers that pass them to `memo`'d children get stable references.

5. **Keep context values small.** Include only what consumers need. Derived values are fine, but avoid huge objects.

6. **Co-locate the Provider with the custom hook** in the same file. Export only the Provider and the hook.

7. **Split state and dispatch** for contexts where some components only write and others only read. This prevents write-only components from re-rendering on state changes.

---

## Summary

In this chapter, you learned:

- **Prop drilling** is passing props through intermediate components that do not use them — it creates boilerplate and tight coupling.
- **Context** provides a way to broadcast data to any descendant component without passing props through every level.
- Three steps: **create** with `createContext()`, **provide** with `<Context.Provider value={...}>`, **consume** with `useContext()`.
- The **Provider pattern** — wrap state, updater functions, and derived values in a Provider component with a matching custom hook.
- **Passing functions** through context lets deeply nested components update shared state.
- **Multiple contexts** can be nested at the app level — each component consumes only what it needs.
- **Performance pitfalls**: every consumer re-renders when the context value changes. Fix with split contexts, `useMemo`, and state/dispatch separation.
- Context is best for **infrequently changing, widely needed data** (theme, auth, locale). For complex or frequently changing state, consider state management libraries.

---

## Interview Questions

**Q1: What is prop drilling, and how does Context solve it?**

Prop drilling is passing data through multiple component levels via props, even when intermediate components do not use the data — they just forward it. This creates boilerplate, tight coupling, and makes refactoring difficult. Context solves this by providing a way to broadcast values from a Provider component to any descendant, regardless of depth. Components in between do not need to know about or pass the data.

**Q2: What are the three steps to use React Context?**

(1) Create a context with `createContext(defaultValue)`. (2) Provide the value by wrapping part of your component tree with `<Context.Provider value={...}>`. (3) Consume the value in any descendant component using `useContext(Context)`. Best practice adds a custom hook that wraps `useContext` with an error check.

**Q3: When a context value changes, which components re-render?**

Every component that calls `useContext` for that specific context re-renders, regardless of whether it uses the part of the value that changed. This is why it is important to split unrelated data into separate contexts — changing the theme should not re-render components that only use auth data.

**Q4: How do you optimize Context to prevent unnecessary re-renders?**

Three strategies: (1) Split unrelated data into separate contexts so changes to one do not affect consumers of another. (2) Memoize the value object with `useMemo` so it has a stable reference when its contents have not changed. (3) Split state and dispatch into separate contexts so components that only dispatch actions (write-only) do not re-render when state changes.

**Q5: Is Context a state management solution?**

Context itself is a dependency injection mechanism — it solves the problem of getting data from point A to point B without prop drilling. It does not manage state — you still use `useState` or `useReducer` for that. Context + state hooks can serve as a simple state management solution for small to medium apps, but for complex state with many actions, middleware needs, or devtools requirements, dedicated state management libraries (Redux, Zustand) are more appropriate.

**Q6: Why should you create a custom hook for each context?**

A custom hook provides three benefits: (1) Error detection — it can throw a clear error if used outside a Provider, rather than silently returning undefined. (2) Clean API — consumers call `useAuth()` instead of `useContext(AuthContext)`, hiding the implementation detail. (3) Encapsulation — the raw context object stays private to the module, preventing misuse and making refactoring easier.

---

## Practice Exercises

**Exercise 1: Multi-Language Support**

Create a `LanguageProvider` and `useLanguage` hook that:
- Stores the current language ("en", "es", "fr")
- Provides a `t()` function that translates keys to the current language
- Has a language switcher component
- Persists the language choice to localStorage
- Translates at least 10 strings used across 3+ components

**Exercise 2: Shopping Cart Context**

Build a complete shopping cart with:
- `CartProvider` that manages items array
- `useCart` hook returning: items, addItem, removeItem, updateQuantity, clearCart, totalItems, totalPrice
- Product listing page that adds items
- Cart page showing items with quantity controls
- Cart badge in the header showing item count
- Persist cart to localStorage

**Exercise 3: Toast/Notification System**

Create a notification system with:
- Multiple notification types (success, error, warning, info)
- Auto-dismiss after configurable duration
- Stacking (multiple notifications visible at once)
- Manual dismiss with close button
- Position options (top-right, top-left, bottom-right, bottom-left)
- Slide-in animation
- Maximum notification limit (dismiss oldest when limit reached)

**Exercise 4: Multi-Context Application**

Build an application that uses three separate contexts:
- `AuthContext` — user login/logout
- `ThemeContext` — light/dark mode
- `PreferencesContext` — font size, compact mode, sidebar visibility
- Each context has its own Provider, custom hook, and related UI
- Show that changing one context does not re-render consumers of other contexts (add console.log to prove it)

---

## What Is Next?

You now understand how to share data across your component tree efficiently using Context. Combined with custom hooks, this gives you a powerful pattern for managing application-wide state.

In Chapter 14, we will explore **useReducer** — React's hook for managing complex state with predictable state transitions, and how it pairs with Context for scalable state management.
