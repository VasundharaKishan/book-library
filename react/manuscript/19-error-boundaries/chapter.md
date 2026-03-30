# Chapter 19: Error Boundaries

## Learning Goals

By the end of this chapter, you will be able to:

- Understand what happens when a React component throws an error
- Explain why error boundaries must be class components
- Build an error boundary component from scratch
- Use error boundaries to protect different sections of your application
- Display user-friendly fallback UI when errors occur
- Implement error recovery with retry mechanisms
- Log errors for monitoring and debugging
- Use the react-error-boundary library for a modern, hooks-friendly approach
- Know what errors boundaries can and cannot catch

---

## What Happens When a Component Crashes

In a typical React application, if a component throws an error during rendering, the entire application crashes. The screen goes white, and the user sees nothing.

```jsx
function UserProfile({ user }) {
  // If user is null, this throws: "Cannot read properties of null"
  return <h2>{user.name}</h2>;
}
```

Before React 16, there was no way to handle this gracefully. A single error in one small component would unmount the entire React tree — the header, the sidebar, the navigation, everything. The user's only option was to refresh the page.

React 16 introduced **error boundaries** — components that catch JavaScript errors in their child component tree and display a fallback UI instead of crashing the entire application.

Think of error boundaries like `try/catch` blocks, but for React components. Just as a `try/catch` prevents one error from crashing your entire Node.js server, an error boundary prevents one broken component from crashing your entire UI.

---

## Building an Error Boundary

Error boundaries are one of the very few cases in modern React where you **must** use a class component. There is no hook equivalent for `componentDidCatch` or `static getDerivedStateFromError`. This is a deliberate design decision by the React team — these lifecycle methods have not been migrated to hooks.

### The Minimal Error Boundary

```jsx
import { Component } from "react";

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render shows the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error for debugging
    console.error("Error caught by boundary:", error);
    console.error("Component stack:", errorInfo.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return <h2>Something went wrong.</h2>;
    }

    return this.props.children;
  }
}
```

### How It Works

Two lifecycle methods make error boundaries work:

**`static getDerivedStateFromError(error)`**

- Called during the render phase when a descendant component throws
- Must return an object to update state (typically `{ hasError: true }`)
- Used to switch from the normal UI to the fallback UI
- Must be a pure function — no side effects

**`componentDidCatch(error, errorInfo)`**

- Called during the commit phase after the error has been handled
- Receives the error object and an `errorInfo` object with a `componentStack` property
- Used for side effects like logging errors to a monitoring service
- Not called during server-side rendering

### Using the Error Boundary

Wrap any part of your component tree with the error boundary:

```jsx
function App() {
  return (
    <div>
      <h1>My Application</h1>
      <ErrorBoundary>
        <UserProfile userId={42} />
      </ErrorBoundary>
    </div>
  );
}
```

If `UserProfile` throws during rendering, the error boundary catches it and shows "Something went wrong." instead of crashing the entire app. The `<h1>My Application</h1>` remains visible.

---

## A Better Error Boundary with Fallback UI

The minimal example shows plain text. A production error boundary should display a helpful, well-designed fallback:

```jsx
import { Component } from "react";

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Log to an error monitoring service
    console.error("Error boundary caught an error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      // If a custom fallback was provided, use it
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div
          style={{
            padding: "2rem",
            textAlign: "center",
            backgroundColor: "#fef2f2",
            border: "1px solid #fecaca",
            borderRadius: 8,
            margin: "1rem",
          }}
        >
          <h2 style={{ color: "#991b1b", marginBottom: "0.5rem" }}>
            Something went wrong
          </h2>
          <p style={{ color: "#b91c1c", marginBottom: "1rem" }}>
            This section encountered an error and could not be displayed.
          </p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            style={{
              padding: "0.5rem 1rem",
              backgroundColor: "#ef4444",
              color: "white",
              border: "none",
              borderRadius: 4,
              cursor: "pointer",
            }}
          >
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### Custom Fallback UI

The `fallback` prop lets each usage of the error boundary specify its own fallback:

```jsx
function App() {
  return (
    <div>
      <ErrorBoundary fallback={<p>Could not load the header.</p>}>
        <Header />
      </ErrorBoundary>

      <ErrorBoundary fallback={<p>Could not load the sidebar.</p>}>
        <Sidebar />
      </ErrorBoundary>

      <ErrorBoundary
        fallback={
          <div style={{ padding: "2rem", textAlign: "center" }}>
            <h2>Content failed to load</h2>
            <p>Please try refreshing the page.</p>
          </div>
        }
      >
        <MainContent />
      </ErrorBoundary>
    </div>
  );
}
```

If `Sidebar` crashes, the sidebar area shows "Could not load the sidebar." while the header and main content continue working normally.

### Fallback as a Render Prop

For even more flexibility, pass a function that receives the error:

```jsx
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  resetError = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      // If fallback is a function, call it with error and reset function
      if (typeof this.props.fallback === "function") {
        return this.props.fallback({
          error: this.state.error,
          resetError: this.resetError,
        });
      }

      // If fallback is a React element, render it
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback
      return (
        <div style={{ padding: "2rem", textAlign: "center" }}>
          <h2>Something went wrong</h2>
          <button onClick={this.resetError}>Try Again</button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

```jsx
<ErrorBoundary
  fallback={({ error, resetError }) => (
    <div>
      <h2>Error</h2>
      <p>{error.message}</p>
      <button onClick={resetError}>Retry</button>
    </div>
  )}
  onError={(error, info) => {
    // Send to error monitoring service
    logErrorToService(error, info);
  }}
>
  <DashboardWidget />
</ErrorBoundary>
```

---

## Where to Place Error Boundaries

The placement of error boundaries determines the granularity of error handling. You control how much of the UI is replaced by a fallback when something goes wrong.

### Strategy 1: Top-Level Boundary (Catch-All)

```jsx
function App() {
  return (
    <ErrorBoundary fallback={<FullPageError />}>
      <Router>
        <Layout>
          <Routes>{/* ... */}</Routes>
        </Layout>
      </Router>
    </ErrorBoundary>
  );
}

function FullPageError() {
  return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}>
      <div style={{ textAlign: "center" }}>
        <h1>Oops!</h1>
        <p>Something unexpected happened.</p>
        <button onClick={() => window.location.reload()}>
          Reload Page
        </button>
      </div>
    </div>
  );
}
```

This is the last line of defense. It catches any error that slips through more specific boundaries. Every application should have one.

### Strategy 2: Route-Level Boundaries

```jsx
function App() {
  return (
    <ErrorBoundary fallback={<FullPageError />}>
      <Layout>
        <Routes>
          <Route
            path="/"
            element={
              <ErrorBoundary fallback={<p>Could not load home page.</p>}>
                <HomePage />
              </ErrorBoundary>
            }
          />
          <Route
            path="/dashboard"
            element={
              <ErrorBoundary fallback={<p>Could not load dashboard.</p>}>
                <Dashboard />
              </ErrorBoundary>
            }
          />
          <Route
            path="/settings"
            element={
              <ErrorBoundary fallback={<p>Could not load settings.</p>}>
                <Settings />
              </ErrorBoundary>
            }
          />
        </Routes>
      </Layout>
    </ErrorBoundary>
  );
}
```

If the Dashboard crashes, the layout (header, sidebar) remains intact and only the content area shows the error fallback. The user can navigate to other pages using the intact navigation.

### Strategy 3: Section-Level Boundaries

```jsx
function Dashboard() {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
      <ErrorBoundary fallback={<WidgetError name="Revenue" />}>
        <RevenueChart />
      </ErrorBoundary>

      <ErrorBoundary fallback={<WidgetError name="Users" />}>
        <UserGrowthChart />
      </ErrorBoundary>

      <ErrorBoundary fallback={<WidgetError name="Orders" />}>
        <RecentOrders />
      </ErrorBoundary>

      <ErrorBoundary fallback={<WidgetError name="Activity" />}>
        <ActivityFeed />
      </ErrorBoundary>
    </div>
  );
}

function WidgetError({ name }) {
  return (
    <div style={{
      padding: "2rem",
      textAlign: "center",
      backgroundColor: "#f9fafb",
      borderRadius: 8,
      border: "1px dashed #d1d5db",
    }}>
      <p style={{ color: "#6b7280" }}>
        {name} widget could not be loaded.
      </p>
    </div>
  );
}
```

This is the most granular approach. If the revenue chart crashes, the other three widgets continue working. This is ideal for dashboards, feeds, and any page with independent sections.

### The Recommended Approach: Multiple Layers

Use all three strategies together:

```jsx
function App() {
  return (
    // Layer 1: Catch-all for unexpected errors
    <ErrorBoundary fallback={<FullPageError />}>
      <Layout>
        <Routes>
          {/* Layer 2: Per-route boundaries */}
          <Route
            path="/dashboard"
            element={
              <ErrorBoundary fallback={<PageError />}>
                <Dashboard />
              </ErrorBoundary>
            }
          />
        </Routes>
      </Layout>
    </ErrorBoundary>
  );
}

function Dashboard() {
  return (
    <div>
      {/* Layer 3: Per-widget boundaries */}
      <ErrorBoundary fallback={<WidgetError />}>
        <RevenueChart />
      </ErrorBoundary>
      <ErrorBoundary fallback={<WidgetError />}>
        <UserTable />
      </ErrorBoundary>
    </div>
  );
}
```

Errors bubble up through the layers. A chart error is caught at layer 3 (widget level). If something bigger breaks, layer 2 (route level) catches it. If everything fails, layer 1 (top level) catches it.

---

## Error Recovery

### Reset on Retry

The simplest recovery is resetting the error state and re-rendering the children:

```jsx
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  resetError = () => {
    this.setState({ hasError: false });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div>
          <p>Something went wrong.</p>
          <button onClick={this.resetError}>Try Again</button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

When the user clicks "Try Again," the error boundary resets its state and attempts to render the children again. If the error was transient (a network glitch, a race condition), this might succeed.

### Reset on Navigation

When a user navigates to a different page, the error boundary should reset automatically. Otherwise, the error fallback stays visible even on a new route:

```jsx
import { Component } from "react";

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidUpdate(prevProps) {
    // Reset the boundary when the resetKey changes
    if (this.state.hasError && prevProps.resetKey !== this.props.resetKey) {
      this.setState({ hasError: false });
    }
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || <p>Something went wrong.</p>;
    }
    return this.props.children;
  }
}
```

```jsx
import { useLocation } from "react-router-dom";

function App() {
  const location = useLocation();

  return (
    <ErrorBoundary resetKey={location.pathname}>
      <Routes>{/* ... */}</Routes>
    </ErrorBoundary>
  );
}
```

When the user navigates (changing `location.pathname`), `resetKey` changes, `componentDidUpdate` detects it, and the boundary resets. The new page gets a clean slate.

### Reset on Prop Changes

The same pattern works for any changing value:

```jsx
function UserProfile({ userId }) {
  return (
    <ErrorBoundary resetKey={userId}>
      <UserData userId={userId} />
    </ErrorBoundary>
  );
}
```

If `UserData` crashes for user 42, clicking on user 43 resets the boundary and tries again with the new user.

---

## Error Logging

In production, you need to know when errors happen. Logging to the console is not enough — you need errors sent to a monitoring service.

### Logging to an External Service

```jsx
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorId: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Generate a unique error ID for support reference
    const errorId = `ERR-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`;

    this.setState({ errorId });

    // Log to your error monitoring service
    logError({
      errorId,
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      url: window.location.href,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: "2rem", textAlign: "center" }}>
          <h2>Something went wrong</h2>
          <p>Our team has been notified and is working on a fix.</p>
          {this.state.errorId && (
            <p style={{ fontSize: "0.85rem", color: "#666" }}>
              Reference: {this.state.errorId}
            </p>
          )}
          <button onClick={() => this.setState({ hasError: false })}>
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Simulated error logging function
function logError(errorData) {
  // In production, send to Sentry, LogRocket, Datadog, etc.
  // Example with fetch:
  fetch("/api/errors", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(errorData),
  }).catch(() => {
    // If error logging fails, at least log to console
    console.error("Failed to log error:", errorData);
  });
}
```

### The Component Stack

The `errorInfo.componentStack` is invaluable for debugging. It shows the React component hierarchy that led to the error:

```
The above error occurred in the <UserAvatar> component:
    at UserAvatar (src/components/UserAvatar.jsx:12)
    at div
    at UserCard (src/components/UserCard.jsx:8)
    at ErrorBoundary (src/components/ErrorBoundary.jsx:5)
    at div
    at Dashboard (src/pages/Dashboard.jsx:15)
    at Route
    at Routes
    at App (src/App.jsx:10)
```

This tells you exactly which component threw, and the full path of parent components above it. Combined with the error message and stack trace, this is usually enough to identify and fix the bug.

---

## Using react-error-boundary

Writing class components for error boundaries is verbose, and the class API feels out of place in a modern hooks-based codebase. The **react-error-boundary** library provides a production-ready error boundary with a hooks-friendly API.

### Installation

```bash
npm install react-error-boundary
```

### Basic Usage

```jsx
import { ErrorBoundary } from "react-error-boundary";

function ErrorFallback({ error, resetErrorBoundary }) {
  return (
    <div style={{ padding: "2rem", textAlign: "center" }}>
      <h2>Something went wrong</h2>
      <p style={{ color: "red" }}>{error.message}</p>
      <button onClick={resetErrorBoundary}>Try Again</button>
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary
      FallbackComponent={ErrorFallback}
      onError={(error, info) => {
        // Log to error monitoring service
        logError(error, info);
      }}
      onReset={() => {
        // Optional: clear cache, reset state, etc.
      }}
    >
      <Dashboard />
    </ErrorBoundary>
  );
}
```

### Reset Keys

```jsx
function App() {
  const location = useLocation();

  return (
    <ErrorBoundary
      FallbackComponent={ErrorFallback}
      resetKeys={[location.pathname]}
    >
      <Routes>{/* ... */}</Routes>
    </ErrorBoundary>
  );
}
```

The `resetKeys` prop accepts an array. When any value in the array changes, the boundary resets automatically.

### The useErrorBoundary Hook

The library provides a hook for triggering error boundaries from event handlers and async code:

```jsx
import { useErrorBoundary } from "react-error-boundary";

function UserProfile({ userId }) {
  const { showBoundary } = useErrorBoundary();
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetch(`/api/users/${userId}`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch user");
        return res.json();
      })
      .then(setUser)
      .catch((error) => {
        // This sends the error to the nearest error boundary
        showBoundary(error);
      });
  }, [userId, showBoundary]);

  if (!user) return <p>Loading...</p>;
  return <h2>{user.name}</h2>;
}
```

This is significant because error boundaries normally cannot catch errors in event handlers or async code. The `showBoundary` function bridges that gap — it programmatically triggers the nearest error boundary, letting you use the same fallback UI for all types of errors.

### Inline Fallback

For simple cases, pass JSX directly:

```jsx
<ErrorBoundary fallback={<p>Something went wrong.</p>}>
  <Widget />
</ErrorBoundary>
```

### Fallback Render Prop

```jsx
<ErrorBoundary
  fallbackRender={({ error, resetErrorBoundary }) => (
    <div>
      <p>Error: {error.message}</p>
      <button onClick={resetErrorBoundary}>Retry</button>
    </div>
  )}
>
  <Widget />
</ErrorBoundary>
```

---

## What Error Boundaries Can and Cannot Catch

Understanding the scope of error boundaries is critical. They do not catch everything.

### Error Boundaries CATCH:

- Errors during **rendering** (in the `return` statement or render logic)
- Errors in **lifecycle methods** (`componentDidMount`, `componentDidUpdate`, etc.)
- Errors in **constructors** of child components
- Errors in `static getDerivedStateFromError` and `componentDidCatch` of child boundaries

```jsx
// These errors ARE caught by error boundaries

function BrokenComponent() {
  // Error during rendering
  const user = null;
  return <h2>{user.name}</h2>; // TypeError: Cannot read properties of null

  // Error from bad data
  const data = JSON.parse("invalid json"); // SyntaxError
}
```

### Error Boundaries DO NOT CATCH:

**1. Event handler errors**

```jsx
function Button() {
  function handleClick() {
    throw new Error("Crash!"); // NOT caught by error boundary
  }

  return <button onClick={handleClick}>Click me</button>;
}
```

Event handlers run outside the React rendering lifecycle. Use regular `try/catch` or the `useErrorBoundary` hook from react-error-boundary.

**2. Async code (setTimeout, Promises, async/await)**

```jsx
function Component() {
  useEffect(() => {
    setTimeout(() => {
      throw new Error("Async crash!"); // NOT caught
    }, 1000);
  }, []);

  return <div>Content</div>;
}
```

Async errors happen after rendering is complete. Handle them with `try/catch` in async functions, or use `showBoundary` from react-error-boundary.

**3. Server-side rendering (SSR)**

Error boundaries only work on the client side. Server-side errors need separate handling.

**4. Errors thrown in the error boundary itself**

If the error boundary's own render method throws, it cannot catch its own error. Only a parent error boundary can catch it.

### Handling the Gaps

```jsx
import { useErrorBoundary } from "react-error-boundary";

function UserActions({ userId }) {
  const { showBoundary } = useErrorBoundary();

  // Event handler errors — use try/catch + showBoundary
  async function handleDelete() {
    try {
      const response = await fetch(`/api/users/${userId}`, {
        method: "DELETE",
      });
      if (!response.ok) throw new Error("Delete failed");
    } catch (error) {
      showBoundary(error); // Triggers the nearest error boundary
    }
  }

  // Async errors in effects — use try/catch + showBoundary
  useEffect(() => {
    async function loadData() {
      try {
        const response = await fetch(`/api/users/${userId}`);
        if (!response.ok) throw new Error("Fetch failed");
        // ...
      } catch (error) {
        showBoundary(error);
      }
    }

    loadData();
  }, [userId, showBoundary]);

  return <button onClick={handleDelete}>Delete User</button>;
}
```

---

## Error Boundaries in Development vs Production

### Development Mode

In development, React intentionally shows errors in a full-screen overlay — even when error boundaries catch them. This is by design to make sure you notice and fix errors during development. The error boundary's fallback UI renders behind the overlay. Dismissing the overlay reveals the fallback.

### Production Mode

In production, there is no overlay. Error boundaries work silently — they catch the error, show the fallback, and log via `componentDidCatch`. Users see a clean fallback instead of a crashed application.

### Strict Mode Behavior

React's Strict Mode (in development) renders components twice to help detect side effects. This means `componentDidCatch` might fire more than once for the same error. This is normal and only happens in development.

---

## Practical Error Boundary Patterns

### Pattern 1: Suspense-Like Error Handling

Combine error boundaries with loading states for a complete data fetching pattern:

```jsx
function DataSection({ url, renderData }) {
  return (
    <ErrorBoundary
      fallbackRender={({ error, resetErrorBoundary }) => (
        <div>
          <p>Failed to load data: {error.message}</p>
          <button onClick={resetErrorBoundary}>Retry</button>
        </div>
      )}
    >
      <DataLoader url={url} renderData={renderData} />
    </ErrorBoundary>
  );
}

function DataLoader({ url, renderData }) {
  const { showBoundary } = useErrorBoundary();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetch(url)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        setData(data);
        setLoading(false);
      })
      .catch((error) => showBoundary(error));
  }, [url, showBoundary]);

  if (loading) return <p>Loading...</p>;
  return renderData(data);
}

// Usage
<DataSection
  url="/api/stats"
  renderData={(stats) => (
    <div>
      <p>Users: {stats.users}</p>
      <p>Revenue: ${stats.revenue}</p>
    </div>
  )}
/>
```

### Pattern 2: Error Boundary with Different Severity Levels

```jsx
function ErrorFallback({ error, resetErrorBoundary }) {
  // Determine severity based on error type
  const isNetworkError = error.message.includes("fetch") ||
    error.message.includes("network") ||
    error.message.includes("HTTP");

  if (isNetworkError) {
    return (
      <div style={{ padding: "1rem", backgroundColor: "#fffbeb", border: "1px solid #fcd34d", borderRadius: 8 }}>
        <h3 style={{ color: "#92400e" }}>Connection Issue</h3>
        <p>Please check your internet connection and try again.</p>
        <button onClick={resetErrorBoundary}>Retry</button>
      </div>
    );
  }

  return (
    <div style={{ padding: "1rem", backgroundColor: "#fef2f2", border: "1px solid #fca5a5", borderRadius: 8 }}>
      <h3 style={{ color: "#991b1b" }}>Unexpected Error</h3>
      <p>Something went wrong. Our team has been notified.</p>
      <button onClick={resetErrorBoundary}>Try Again</button>
    </div>
  );
}
```

### Pattern 3: Boundary with Auto-Retry

For transient errors, automatically retry a few times before showing the fallback:

```jsx
import { Component } from "react";

class AutoRetryBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, retryCount: 0 };
    this.maxRetries = props.maxRetries || 2;
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    if (this.state.retryCount < this.maxRetries) {
      // Wait a moment and try again
      setTimeout(() => {
        this.setState((prev) => ({
          hasError: false,
          retryCount: prev.retryCount + 1,
        }));
      }, 1000 * (this.state.retryCount + 1)); // Exponential backoff
    } else {
      // Max retries exceeded — log the error
      console.error("Max retries exceeded:", error);
    }
  }

  render() {
    if (this.state.hasError && this.state.retryCount >= this.maxRetries) {
      return this.props.fallback || <p>Failed after multiple attempts.</p>;
    }

    if (this.state.hasError) {
      return <p>Retrying... (attempt {this.state.retryCount + 1})</p>;
    }

    return this.props.children;
  }
}
```

---

## Mini Project: Resilient Dashboard

Let us build a dashboard that uses error boundaries at multiple levels to stay functional even when individual widgets crash.

```jsx
// ErrorBoundary.jsx — reusable error boundary
import { Component } from "react";

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error(`[${this.props.name || "ErrorBoundary"}]`, error.message);
    console.error("Component stack:", errorInfo.componentStack);

    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  componentDidUpdate(prevProps) {
    if (this.state.hasError && prevProps.resetKey !== this.props.resetKey) {
      this.setState({ hasError: false, error: null });
    }
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  render() {
    if (this.state.hasError) {
      if (typeof this.props.fallback === "function") {
        return this.props.fallback({
          error: this.state.error,
          resetError: this.handleReset,
        });
      }
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div style={{ padding: "1.5rem", textAlign: "center", backgroundColor: "#f9fafb", borderRadius: 8, border: "1px dashed #d1d5db" }}>
          <p style={{ color: "#6b7280", marginBottom: "0.5rem" }}>
            This section could not be loaded.
          </p>
          <button
            onClick={this.handleReset}
            style={{ padding: "0.25rem 0.75rem", fontSize: "0.85rem", cursor: "pointer" }}
          >
            Retry
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
```

```jsx
// App.jsx
import { useState } from "react";
import ErrorBoundary from "./ErrorBoundary";

function App() {
  return (
    <ErrorBoundary
      name="App"
      fallback={({ resetError }) => (
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}>
          <div style={{ textAlign: "center" }}>
            <h1>Application Error</h1>
            <p>The application encountered a critical error.</p>
            <button onClick={() => window.location.reload()}>Reload Page</button>
          </div>
        </div>
      )}
    >
      <Dashboard />
    </ErrorBoundary>
  );
}
```

```jsx
// Dashboard.jsx
import { useState } from "react";
import ErrorBoundary from "./ErrorBoundary";

function Dashboard() {
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <div style={{ maxWidth: 1200, margin: "0 auto", padding: "1rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <h1>Dashboard</h1>
        <button onClick={() => setRefreshKey((k) => k + 1)}>
          Refresh All
        </button>
      </div>

      {/* Stats row — each stat is independent */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "1rem", marginBottom: "1.5rem" }}>
        <ErrorBoundary name="TotalUsers" resetKey={refreshKey}>
          <StatCard label="Total Users" fetchUrl="/api/stats/users" />
        </ErrorBoundary>
        <ErrorBoundary name="Revenue" resetKey={refreshKey}>
          <StatCard label="Revenue" fetchUrl="/api/stats/revenue" prefix="$" />
        </ErrorBoundary>
        <ErrorBoundary name="Orders" resetKey={refreshKey}>
          <StatCard label="Orders" fetchUrl="/api/stats/orders" />
        </ErrorBoundary>
        <ErrorBoundary name="Conversion" resetKey={refreshKey}>
          <StatCard label="Conversion" fetchUrl="/api/stats/conversion" suffix="%" />
        </ErrorBoundary>
      </div>

      {/* Main content — two independent panels */}
      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "1.5rem" }}>
        <ErrorBoundary
          name="RecentOrders"
          resetKey={refreshKey}
          fallback={({ error, resetError }) => (
            <div style={{ padding: "2rem", textAlign: "center", backgroundColor: "#fff", borderRadius: 8, border: "1px solid #e5e7eb" }}>
              <h3>Orders Unavailable</h3>
              <p style={{ color: "#666" }}>{error.message}</p>
              <button onClick={resetError}>Retry</button>
            </div>
          )}
        >
          <RecentOrdersTable />
        </ErrorBoundary>

        <ErrorBoundary name="ActivityFeed" resetKey={refreshKey}>
          <ActivityFeed />
        </ErrorBoundary>
      </div>
    </div>
  );
}
```

```jsx
// StatCard.jsx — a widget that might crash
import { useState, useEffect } from "react";

function StatCard({ label, fetchUrl, prefix = "", suffix = "" }) {
  const [value, setValue] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate API call — randomly fails to demonstrate error boundaries
    const timer = setTimeout(() => {
      if (Math.random() < 0.3) {
        throw new Error(`Failed to load ${label}`);
      }
      setValue(Math.floor(Math.random() * 10000));
      setLoading(false);
    }, 500 + Math.random() * 1000);

    return () => clearTimeout(timer);
  }, [label]);

  if (loading) {
    return (
      <div style={{ padding: "1.5rem", backgroundColor: "#f9fafb", borderRadius: 8, textAlign: "center" }}>
        <p style={{ color: "#999" }}>Loading...</p>
      </div>
    );
  }

  return (
    <div style={{ padding: "1.5rem", backgroundColor: "white", borderRadius: 8, border: "1px solid #e5e7eb" }}>
      <p style={{ color: "#666", fontSize: "0.85rem", marginBottom: "0.25rem" }}>{label}</p>
      <p style={{ fontSize: "1.75rem", fontWeight: "bold" }}>
        {prefix}{value?.toLocaleString()}{suffix}
      </p>
    </div>
  );
}
```

```jsx
// RecentOrdersTable.jsx
import { useState, useEffect } from "react";

function RecentOrdersTable() {
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    // Simulate data
    setOrders([
      { id: 1001, customer: "Alice Johnson", total: 89.99, status: "Shipped" },
      { id: 1002, customer: "Bob Williams", total: 149.50, status: "Processing" },
      { id: 1003, customer: "Carol Davis", total: 32.00, status: "Delivered" },
      { id: 1004, customer: "Dan Brown", total: 267.80, status: "Processing" },
      { id: 1005, customer: "Eve Wilson", total: 54.25, status: "Shipped" },
    ]);
  }, []);

  return (
    <div style={{ backgroundColor: "white", borderRadius: 8, border: "1px solid #e5e7eb", overflow: "hidden" }}>
      <div style={{ padding: "1rem 1.5rem", borderBottom: "1px solid #e5e7eb" }}>
        <h2 style={{ margin: 0, fontSize: "1.1rem" }}>Recent Orders</h2>
      </div>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ backgroundColor: "#f9fafb" }}>
            <th style={{ padding: "0.75rem 1.5rem", textAlign: "left", fontSize: "0.85rem" }}>Order ID</th>
            <th style={{ padding: "0.75rem 1.5rem", textAlign: "left", fontSize: "0.85rem" }}>Customer</th>
            <th style={{ padding: "0.75rem 1.5rem", textAlign: "right", fontSize: "0.85rem" }}>Total</th>
            <th style={{ padding: "0.75rem 1.5rem", textAlign: "left", fontSize: "0.85rem" }}>Status</th>
          </tr>
        </thead>
        <tbody>
          {orders.map((order) => (
            <tr key={order.id} style={{ borderTop: "1px solid #f3f4f6" }}>
              <td style={{ padding: "0.75rem 1.5rem" }}>#{order.id}</td>
              <td style={{ padding: "0.75rem 1.5rem" }}>{order.customer}</td>
              <td style={{ padding: "0.75rem 1.5rem", textAlign: "right" }}>${order.total.toFixed(2)}</td>
              <td style={{ padding: "0.75rem 1.5rem" }}>
                <span style={{
                  padding: "0.125rem 0.5rem",
                  borderRadius: 12,
                  fontSize: "0.8rem",
                  backgroundColor:
                    order.status === "Delivered" ? "#d1fae5" :
                    order.status === "Shipped" ? "#dbeafe" : "#fef3c7",
                  color:
                    order.status === "Delivered" ? "#065f46" :
                    order.status === "Shipped" ? "#1e40af" : "#92400e",
                }}>
                  {order.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

```jsx
// ActivityFeed.jsx
import { useState, useEffect } from "react";

function ActivityFeed() {
  const [activities, setActivities] = useState([]);

  useEffect(() => {
    setActivities([
      { id: 1, text: "New user registered: Eve Wilson", time: "2 minutes ago" },
      { id: 2, text: "Order #1004 payment received", time: "15 minutes ago" },
      { id: 3, text: "Product 'React Book' is low on stock", time: "1 hour ago" },
      { id: 4, text: "Order #1001 shipped via FedEx", time: "2 hours ago" },
      { id: 5, text: "New review on 'JavaScript Guide'", time: "3 hours ago" },
    ]);
  }, []);

  return (
    <div style={{ backgroundColor: "white", borderRadius: 8, border: "1px solid #e5e7eb" }}>
      <div style={{ padding: "1rem 1.5rem", borderBottom: "1px solid #e5e7eb" }}>
        <h2 style={{ margin: 0, fontSize: "1.1rem" }}>Recent Activity</h2>
      </div>
      <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
        {activities.map((activity) => (
          <li
            key={activity.id}
            style={{
              padding: "0.75rem 1.5rem",
              borderBottom: "1px solid #f3f4f6",
              fontSize: "0.9rem",
            }}
          >
            <p style={{ margin: 0 }}>{activity.text}</p>
            <p style={{ margin: "0.25rem 0 0", fontSize: "0.8rem", color: "#999" }}>
              {activity.time}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

This mini project demonstrates:

- **Three layers of error boundaries** — app level, dashboard level, and widget level
- **Independent failure isolation** — a broken stat card does not affect the orders table
- **Reset via key** — the "Refresh All" button resets all boundaries by changing `refreshKey`
- **Custom fallbacks** — each boundary can have its own error display
- **Error logging** — errors are logged with the boundary name for easy identification

---

## Common Mistakes

### Mistake 1: Not Having Any Error Boundaries

```jsx
// WRONG — the entire app crashes on any error
function App() {
  return (
    <div>
      <Header />
      <Sidebar />
      <MainContent />
    </div>
  );
}

// CORRECT — at least a top-level boundary
function App() {
  return (
    <ErrorBoundary>
      <Header />
      <Sidebar />
      <MainContent />
    </ErrorBoundary>
  );
}
```

### Mistake 2: Expecting Error Boundaries to Catch Event Handler Errors

```jsx
// This error will NOT be caught by an error boundary
function Button() {
  function handleClick() {
    throw new Error("Clicked the broken button");
  }

  return <button onClick={handleClick}>Click me</button>;
}

// CORRECT — use try/catch in event handlers
function Button() {
  function handleClick() {
    try {
      riskyOperation();
    } catch (error) {
      // Handle locally or use showBoundary from react-error-boundary
      console.error(error);
    }
  }

  return <button onClick={handleClick}>Click me</button>;
}
```

### Mistake 3: Using One Giant Error Boundary

```jsx
// WRONG — one boundary replaces everything on any error
function App() {
  return (
    <ErrorBoundary>
      <Header />
      <Sidebar />
      <Dashboard />
      <Footer />
    </ErrorBoundary>
  );
}

// CORRECT — granular boundaries keep working sections intact
function App() {
  return (
    <ErrorBoundary fallback={<FullPageError />}>
      <Header />
      <div style={{ display: "flex" }}>
        <ErrorBoundary fallback={<p>Sidebar unavailable</p>}>
          <Sidebar />
        </ErrorBoundary>
        <ErrorBoundary fallback={<p>Content could not load</p>}>
          <Dashboard />
        </ErrorBoundary>
      </div>
      <Footer />
    </ErrorBoundary>
  );
}
```

### Mistake 4: Not Resetting on Navigation

```jsx
// WRONG — error persists even after navigating away and back
<ErrorBoundary>
  <Routes>
    <Route path="/dashboard" element={<Dashboard />} />
  </Routes>
</ErrorBoundary>

// CORRECT — reset when the route changes
function App() {
  const location = useLocation();

  return (
    <ErrorBoundary resetKey={location.pathname}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </ErrorBoundary>
  );
}
```

---

## Best Practices

1. **Always have a top-level error boundary** — This is your safety net. Even if you forget boundaries elsewhere, the app will not go completely blank.

2. **Add boundaries around independent sections** — Dashboard widgets, sidebar, feed sections, and any component that fetches its own data should have its own boundary.

3. **Provide useful fallback UI** — "Something went wrong" is better than a white screen, but a retry button and context-specific message is better still.

4. **Reset boundaries on navigation** — Pass `location.pathname` as a `resetKey` so boundaries clear when users navigate to a new page.

5. **Log errors to a monitoring service** — Use `componentDidCatch` or the `onError` prop to send errors to Sentry, LogRocket, Datadog, or a similar service. Console.error is not enough for production.

6. **Use react-error-boundary for new projects** — It provides a cleaner API, hooks support (`useErrorBoundary`), and handles common patterns like reset keys out of the box.

7. **Test your error boundaries** — Deliberately throw errors in development to verify your fallbacks look right and your logging works.

---

## Summary

In this chapter, you learned:

- **Without error boundaries**, a single component error crashes the entire React application
- **Error boundaries** are class components that use `getDerivedStateFromError` and `componentDidCatch` to catch rendering errors and display fallback UI
- **Placement matters** — use multiple layers: top-level (catch-all), route-level, and section-level boundaries
- **Error recovery** uses a reset mechanism — either a retry button or automatic reset when a `resetKey` changes (e.g., on navigation)
- **Error logging** in `componentDidCatch` sends errors to monitoring services with component stacks for debugging
- **react-error-boundary** provides a modern, hooks-friendly API with `FallbackComponent`, `resetKeys`, and the `useErrorBoundary` hook
- **Error boundaries cannot catch** event handler errors, async errors, or errors in the boundary itself — use `try/catch` and `showBoundary` for those cases
- **Development vs production** — React shows an error overlay in development; in production, only the fallback renders

---

## Interview Questions

1. **What are error boundaries in React?**

   Error boundaries are React components that catch JavaScript errors in their child component tree during rendering, lifecycle methods, and constructors. When an error is caught, they display a fallback UI instead of crashing the entire application. They are implemented as class components using two lifecycle methods: `static getDerivedStateFromError` (to update state and trigger a fallback render) and `componentDidCatch` (to log error information).

2. **Why must error boundaries be class components?**

   Error boundaries rely on the `static getDerivedStateFromError` and `componentDidCatch` lifecycle methods, which have no hook equivalents. The React team has not introduced hook-based error boundary APIs. This is one of the few remaining use cases for class components in modern React. The `react-error-boundary` library wraps this class component internally and exposes a hooks-friendly API.

3. **What types of errors do error boundaries NOT catch?**

   Error boundaries do not catch: (1) errors in event handlers — these run outside the rendering lifecycle; (2) errors in asynchronous code — setTimeout, Promises, async/await; (3) errors during server-side rendering; (4) errors thrown in the error boundary itself — only a parent boundary can catch those. For event handler and async errors, use `try/catch` blocks or the `useErrorBoundary` hook from react-error-boundary.

4. **Where should you place error boundaries in an application?**

   Use a layered approach. Place a top-level boundary around the entire app as a safety net. Add route-level boundaries so a crash on one page does not affect navigation to other pages. Add section-level boundaries around independent widgets, feeds, or data sections so a single failing component does not take down the entire page. The granularity depends on how independent the sections are.

5. **How do you handle error recovery in error boundaries?**

   Provide a "Try Again" button that resets the boundary's error state, causing it to re-render its children. For automatic recovery on navigation, pass a `resetKey` prop (like `location.pathname`) — when the key changes, the boundary resets automatically. Some implementations also support auto-retry with exponential backoff for transient errors.

---

## Practice Exercises

### Exercise 1: Full Application Error Handling

Add error boundaries to an existing multi-page application. Include a top-level boundary with a full-page error screen, route-level boundaries that preserve navigation, and section-level boundaries for independent widgets. Each level should have a visually distinct fallback. Test by adding deliberate errors to different components.

### Exercise 2: Error Monitoring Integration

Build an error boundary that sends errors to a simulated monitoring API endpoint. Include the error message, component stack, URL, timestamp, and user information. Create a simple admin page that displays the logged errors with timestamps and stack traces.

### Exercise 3: Resilient Data Dashboard

Build a dashboard with six widgets, each fetching data from a different API endpoint. Use error boundaries so that each widget fails independently. Implement a "Refresh" button that resets all failed widgets. Add a status bar at the top showing how many widgets loaded successfully vs failed.

### Exercise 4: Error Boundary with react-error-boundary

Refactor a custom error boundary implementation to use the `react-error-boundary` library. Use `FallbackComponent` for custom fallbacks, `resetKeys` for automatic recovery, `onError` for logging, and the `useErrorBoundary` hook to catch errors in event handlers and async code.

---

## What Is Next?

In Chapter 20, we will explore **Accessibility in React** — how to build applications that everyone can use, including people who navigate with keyboards, use screen readers, or have other accessibility needs. You will learn about semantic HTML, ARIA attributes, focus management, and testing for accessibility.
