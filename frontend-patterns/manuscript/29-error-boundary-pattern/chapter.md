# Chapter 29: The Error Boundary Pattern

## What You Will Learn

- Why JavaScript errors in one component can crash your entire React app
- How Error Boundaries catch errors at component boundaries
- How to build fallback UIs that keep the app usable
- Strategic placement of Error Boundaries in your component tree
- Recovery and retry patterns
- Using the `react-error-boundary` library for production apps
- Error logging and monitoring integration

## Why This Chapter Matters

Imagine you are browsing an e-commerce site. You click on a product. The product's review section has a bug -- maybe a reviewer left a malformed emoji that breaks the text parser. Without error handling, the entire page crashes. The product image, the price, the "Add to Cart" button -- everything gone. You see a blank white screen.

Now imagine the same scenario with Error Boundaries. The review section shows a friendly message: "Could not load reviews. Click to retry." But the product image, price, and "Add to Cart" button all work perfectly. You can still buy the product.

Error Boundaries are the difference between "our site crashed" and "one small section had an issue." In the real world, errors happen. APIs return unexpected data. Third-party scripts fail. Edge cases slip through testing. The question is not whether errors will happen, but how gracefully your application handles them.

---

## The Problem: One Error Crashes Everything

### Without Error Boundaries

```jsx
function App() {
  return (
    <div>
      <Header />
      <ProductDetails />
      <ReviewSection />    {/* BUG: crashes here */}
      <Recommendations />
      <Footer />
    </div>
  );
}

function ReviewSection() {
  const reviews = getReviews();
  // Oops! reviews is null because API failed
  return (
    <div>
      <h2>Reviews ({reviews.length})</h2>  {/* TypeError: null.length */}
      {reviews.map(r => <Review key={r.id} {...r} />)}
    </div>
  );
}
```

```
What the user sees WITHOUT Error Boundaries:

+--------------------------------------------------+
|                                                  |
|              BLANK WHITE SCREEN                  |
|                                                  |
|     (or React's error overlay in development)    |
|                                                  |
|     The ENTIRE app is gone.                      |
|     Header? Gone. Product? Gone. Footer? Gone.   |
|     All because of one null reference in reviews.|
|                                                  |
+--------------------------------------------------+
```

```
What the user sees WITH Error Boundaries:

+--------------------------------------------------+
|  [Logo]  Home  Products  Cart                    |  <-- Header works!
+--------------------------------------------------+
|  Product Name                    $49.99           |  <-- Product works!
|  [Product Image]                 [Add to Cart]   |
|                                                  |
+--------------------------------------------------+
|  +----------------------------------------------+|
|  |  Could not load reviews.                      ||  <-- Graceful fallback
|  |  [Try Again]                                  ||
|  +----------------------------------------------+|
+--------------------------------------------------+
|  You might also like:                            |  <-- Recommendations work!
|  [Item 1] [Item 2] [Item 3]                     |
+--------------------------------------------------+
|  Footer  |  Contact  |  Terms                    |  <-- Footer works!
+--------------------------------------------------+
```

---

## How Error Boundaries Work

Error Boundaries are React components that catch JavaScript errors in their child component tree, log those errors, and display a fallback UI instead of crashing the entire app.

### The Class Component Approach

Error Boundaries MUST be class components. This is one of the few remaining cases where React requires a class component (as of React 18, there is no hook equivalent).

```jsx
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  // Called when a child throws an error during rendering
  static getDerivedStateFromError(error) {
    // Update state so next render shows fallback UI
    return { hasError: true, error };
  }

  // Called after an error is caught - for logging
  componentDidCatch(error, errorInfo) {
    // Log to error reporting service
    console.error('Error caught by boundary:', error);
    console.error('Component stack:', errorInfo.componentStack);

    // In production, send to monitoring service:
    // logErrorToService(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      // Render fallback UI
      return (
        <div className="error-fallback">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message}</p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
          >
            Try Again
          </button>
        </div>
      );
    }

    // No error: render children normally
    return this.props.children;
  }
}

// Usage:
function App() {
  return (
    <div>
      <Header />
      <ErrorBoundary>
        <ProductDetails />
      </ErrorBoundary>
      <ErrorBoundary>
        <ReviewSection />
      </ErrorBoundary>
      <Footer />
    </div>
  );
}

// If ReviewSection crashes:
// - ErrorBoundary catches the error
// - Shows "Something went wrong" ONLY in the review area
// - Header, ProductDetails, and Footer keep working
```

### What Errors Are Caught (and What Are NOT)

```
Error Boundaries CATCH:
  + Errors during rendering (return statement)
  + Errors in lifecycle methods
  + Errors in constructors of child components

Error Boundaries DO NOT CATCH:
  - Event handler errors (use try/catch instead)
  - Async errors (promises, setTimeout)
  - Server-side rendering errors
  - Errors in the Error Boundary component itself

+-------------------------------+-------------------------------+
|        CAUGHT                 |        NOT CAUGHT             |
+-------------------------------+-------------------------------+
| function Child() {            | function Child() {            |
|   // Error during render      |   function handleClick() {    |
|   const x = null;             |     // Error in event handler |
|   return <p>{x.name}</p>;     |     throw new Error('oops');  |
| }                             |   }                           |
|                               |   return (                    |
|                               |     <button onClick={         |
|                               |       handleClick}>Click      |
|                               |     </button>                 |
|                               |   );                          |
|                               | }                             |
+-------------------------------+-------------------------------+
```

### Handling Event Handler Errors

```jsx
// Error Boundaries do NOT catch event handler errors.
// Use try/catch for those.

function DeleteButton({ itemId, onDelete }) {
  const [error, setError] = useState(null);

  async function handleClick() {
    try {
      await deleteItem(itemId);
      onDelete(itemId);
    } catch (err) {
      // Handle the error in component state
      setError(err.message);
      // Or log it
      logErrorToService(err);
    }
  }

  if (error) {
    return (
      <div className="error-inline">
        <p>Failed to delete: {error}</p>
        <button onClick={() => setError(null)}>Dismiss</button>
      </div>
    );
  }

  return <button onClick={handleClick}>Delete</button>;
}
```

---

## Fallback UI Strategies

### Strategy 1: Simple Error Message

```jsx
function SimpleErrorFallback({ error, resetErrorBoundary }) {
  return (
    <div role="alert" className="error-simple">
      <p>Something went wrong.</p>
      <button onClick={resetErrorBoundary}>Try Again</button>
    </div>
  );
}
```

### Strategy 2: Contextual Fallback

```jsx
// Different fallbacks for different parts of the app
function ReviewErrorFallback() {
  return (
    <div className="review-error">
      <p>Reviews could not be loaded right now.</p>
      <p>You can still purchase this product.</p>
    </div>
  );
}

function ChartErrorFallback() {
  return (
    <div className="chart-error">
      <div className="chart-placeholder">
        <span>Chart unavailable</span>
      </div>
      <p>Data visualization is temporarily unavailable.</p>
    </div>
  );
}

function SidebarErrorFallback() {
  return (
    <div className="sidebar-error">
      <p>Navigation error. <a href="/">Go to homepage</a></p>
    </div>
  );
}
```

### Strategy 3: Full Error Details (Development)

```jsx
function DevelopmentErrorFallback({ error, errorInfo }) {
  if (process.env.NODE_ENV === 'production') {
    return <SimpleErrorFallback />;
  }

  return (
    <div className="error-dev" style={{
      padding: '20px',
      background: '#fff0f0',
      border: '2px solid red',
      borderRadius: '8px',
      margin: '10px',
    }}>
      <h3 style={{ color: 'red' }}>Development Error</h3>
      <pre style={{ fontSize: '14px', overflow: 'auto' }}>
        {error.message}
      </pre>
      <details>
        <summary>Component Stack</summary>
        <pre style={{ fontSize: '12px' }}>
          {errorInfo?.componentStack}
        </pre>
      </details>
    </div>
  );
}
```

---

## Placement Strategies

Where you place Error Boundaries dramatically affects the user experience.

```
Strategy 1: Top-Level Only (minimal protection)

<App>
  <ErrorBoundary>        <-- Catches everything, but replaces EVERYTHING
    <Header />
    <Sidebar />
    <MainContent />
    <Footer />
  </ErrorBoundary>
</App>

Problem: Any error replaces the entire app with a fallback.
Use case: Last resort. Better than a white screen, but not great.


Strategy 2: Section-Level (recommended starting point)

<App>
  <ErrorBoundary>
    <Header />
  </ErrorBoundary>
  <div className="layout">
    <ErrorBoundary>
      <Sidebar />
    </ErrorBoundary>
    <ErrorBoundary>
      <MainContent />            <-- Error here only affects main content
    </ErrorBoundary>
  </div>
  <ErrorBoundary>
    <Footer />
  </ErrorBoundary>
</App>

Better: Error in sidebar does not break main content.


Strategy 3: Feature-Level (best user experience)

<App>
  <Header />
  <ProductPage>
    <ErrorBoundary fallback={<ImagePlaceholder />}>
      <ProductImages />
    </ErrorBoundary>
    <ProductInfo />             <-- No boundary needed (simple, unlikely to error)
    <ErrorBoundary fallback={<ReviewsUnavailable />}>
      <ReviewSection />
    </ErrorBoundary>
    <ErrorBoundary fallback={<RecsUnavailable />}>
      <Recommendations />
    </ErrorBoundary>
  </ProductPage>
  <Footer />
</App>

Best: Each feature fails independently. Users can still buy the product
even if reviews or recommendations break.
```

### Recommended Approach: Layered Boundaries

```jsx
function App() {
  return (
    // Layer 1: App-level boundary (last resort)
    <ErrorBoundary fallback={<FullPageError />}>
      <Layout>
        {/* Layer 2: Page-level boundary */}
        <ErrorBoundary fallback={<PageError />}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/products/:id" element={
              // Layer 3: Feature-level boundaries
              <ProductPage />
            } />
          </Routes>
        </ErrorBoundary>
      </Layout>
    </ErrorBoundary>
  );
}

function ProductPage({ productId }) {
  return (
    <div>
      <ProductInfo productId={productId} />

      <ErrorBoundary fallback={<p>Reviews unavailable</p>}>
        <ReviewSection productId={productId} />
      </ErrorBoundary>

      <ErrorBoundary fallback={<p>Recommendations unavailable</p>}>
        <Recommendations productId={productId} />
      </ErrorBoundary>
    </div>
  );
}
```

---

## Recovery and Retry Patterns

### Basic Retry with Key Reset

```jsx
class ErrorBoundaryWithRetry extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Boundary caught:', error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return this.props.fallback({
        error: this.state.error,
        retry: this.handleRetry,
      });
    }
    return this.props.children;
  }
}

// Usage:
<ErrorBoundaryWithRetry
  fallback={({ error, retry }) => (
    <div className="error-panel">
      <h3>Something went wrong</h3>
      <p>{error.message}</p>
      <button onClick={retry}>Retry</button>
    </div>
  )}
>
  <ReviewSection />
</ErrorBoundaryWithRetry>

// When user clicks "Retry":
// 1. State resets to hasError: false
// 2. React attempts to render ReviewSection again
// 3. If the error was transient (network hiccup), it works
// 4. If the error persists, boundary catches it again
```

### Retry with Automatic Fallback Escalation

```jsx
function RetryableSection({ children, maxRetries = 3 }) {
  const [retryCount, setRetryCount] = useState(0);

  // Changing the key forces React to remount the ErrorBoundary
  // and its children, giving them a fresh start
  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
  };

  if (retryCount >= maxRetries) {
    return (
      <div className="max-retries">
        <p>This section is currently unavailable.</p>
        <p>Please try refreshing the page.</p>
        <button onClick={() => window.location.reload()}>
          Refresh Page
        </button>
      </div>
    );
  }

  return (
    <ErrorBoundaryWithRetry
      key={retryCount}  // Fresh boundary on each retry
      fallback={({ error, retry }) => (
        <div>
          <p>Error: {error.message}</p>
          <p>Attempt {retryCount + 1} of {maxRetries}</p>
          <button onClick={() => { handleRetry(); retry(); }}>
            Retry ({maxRetries - retryCount - 1} attempts left)
          </button>
        </div>
      )}
    >
      {children}
    </ErrorBoundaryWithRetry>
  );
}

// Usage:
<RetryableSection maxRetries={3}>
  <ReviewSection />
</RetryableSection>

// Behavior:
// Error occurs --> "Retry (2 attempts left)"
// User clicks --> Retries. If error again:
// "Retry (1 attempt left)"
// User clicks --> Retries. If error again:
// "Retry (0 attempts left)"
// User clicks --> "This section is currently unavailable. Refresh Page"
```

---

## Using react-error-boundary Library

The `react-error-boundary` library provides a production-ready Error Boundary with built-in retry, reset, and logging features.

### Installation and Basic Usage

```bash
npm install react-error-boundary
```

```jsx
import { ErrorBoundary } from 'react-error-boundary';

// Fallback component receives error and reset function
function ErrorFallback({ error, resetErrorBoundary }) {
  return (
    <div role="alert" className="error-fallback">
      <h3>Something went wrong</h3>
      <pre>{error.message}</pre>
      <button onClick={resetErrorBoundary}>Try Again</button>
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary
      FallbackComponent={ErrorFallback}
      onError={(error, errorInfo) => {
        // Log to monitoring service
        console.error('Logged error:', error, errorInfo);
      }}
      onReset={() => {
        // Reset any state that might have caused the error
        // e.g., clear a cache, reset a query
        console.log('Error boundary reset');
      }}
    >
      <Dashboard />
    </ErrorBoundary>
  );
}
```

### Reset on Prop Change

```jsx
import { ErrorBoundary } from 'react-error-boundary';

function ProductPage() {
  const { productId } = useParams();

  return (
    <ErrorBoundary
      FallbackComponent={ErrorFallback}
      resetKeys={[productId]}
      // When productId changes, automatically reset the boundary
      // This is useful when navigating between products
    >
      <ProductDetails id={productId} />
      <Reviews productId={productId} />
    </ErrorBoundary>
  );
}

// Behavior:
// User visits /products/1 --> Reviews crash
// User sees error fallback
// User navigates to /products/2 --> productId changes
// ErrorBoundary auto-resets --> tries rendering Reviews for product 2
// If product 2's reviews work fine, user never sees the error again
```

### useErrorBoundary Hook

```jsx
import { useErrorBoundary } from 'react-error-boundary';

function ReviewSection({ productId }) {
  const { showBoundary } = useErrorBoundary();
  const [reviews, setReviews] = useState([]);

  useEffect(() => {
    fetchReviews(productId)
      .then(setReviews)
      .catch(error => {
        // This catches ASYNC errors and sends them
        // to the nearest Error Boundary!
        showBoundary(error);
      });
  }, [productId, showBoundary]);

  return (
    <div>
      {reviews.map(r => (
        <div key={r.id}>
          <strong>{r.author}</strong>: {r.text}
        </div>
      ))}
    </div>
  );
}

// Now async errors (which Error Boundaries normally miss)
// are properly caught and display the fallback UI.

// Usage:
<ErrorBoundary FallbackComponent={ErrorFallback}>
  <ReviewSection productId={42} />
</ErrorBoundary>
```

### Inline Fallback

```jsx
import { ErrorBoundary } from 'react-error-boundary';

function Dashboard() {
  return (
    <div className="dashboard-grid">
      <ErrorBoundary fallback={<div>Revenue chart unavailable</div>}>
        <RevenueChart />
      </ErrorBoundary>

      <ErrorBoundary fallback={<div>User stats unavailable</div>}>
        <UserStats />
      </ErrorBoundary>

      <ErrorBoundary
        fallback={<div>Activity feed unavailable</div>}
      >
        <ActivityFeed />
      </ErrorBoundary>
    </div>
  );
}

// Each widget fails independently.
// If RevenueChart crashes, UserStats and ActivityFeed keep working.
```

---

## Error Boundary + Code Splitting

Error Boundaries pair perfectly with lazy-loaded components (Chapter 26):

```jsx
import { lazy, Suspense } from 'react';
import { ErrorBoundary } from 'react-error-boundary';

const AdminPanel = lazy(() => import('./AdminPanel'));

function AdminRoute() {
  return (
    <ErrorBoundary
      FallbackComponent={({ error, resetErrorBoundary }) => (
        <div>
          <h2>Failed to load Admin Panel</h2>
          <p>
            {error.message.includes('Loading chunk')
              ? 'Network error. Check your connection.'
              : error.message}
          </p>
          <button onClick={resetErrorBoundary}>Retry</button>
        </div>
      )}
    >
      <Suspense fallback={<div>Loading admin panel...</div>}>
        <AdminPanel />
      </Suspense>
    </ErrorBoundary>
  );
}

// Flow:
// 1. User navigates to /admin
// 2. Suspense shows "Loading admin panel..."
// 3a. Chunk loads successfully --> AdminPanel renders
// 3b. Network fails --> ErrorBoundary catches --> shows retry button
// 4. User clicks retry --> ErrorBoundary resets --> Suspense tries again
```

---

## Real-World Use Case: Error Monitoring Integration

```jsx
import { ErrorBoundary } from 'react-error-boundary';

// Error logging service (e.g., Sentry, LogRocket, Datadog)
function logError(error, errorInfo) {
  // In production, send to your error monitoring service
  if (process.env.NODE_ENV === 'production') {
    // Example: Sentry
    // Sentry.captureException(error, {
    //   extra: { componentStack: errorInfo.componentStack }
    // });

    // Example: Custom API
    fetch('/api/errors', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: error.message,
        stack: error.stack,
        componentStack: errorInfo.componentStack,
        url: window.location.href,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
      }),
    }).catch(() => {
      // Silently fail - do not crash the error handler!
    });
  } else {
    console.error('Error Boundary caught:', error);
    console.error('Component stack:', errorInfo.componentStack);
  }
}

function AppErrorFallback({ error, resetErrorBoundary }) {
  return (
    <div className="app-error" role="alert">
      <h1>Something went wrong</h1>
      <p>
        We have been notified and are looking into it.
        Please try again or contact support if the problem persists.
      </p>
      <div className="error-actions">
        <button onClick={resetErrorBoundary}>
          Try Again
        </button>
        <button onClick={() => window.location.href = '/'}>
          Go to Homepage
        </button>
      </div>
      {process.env.NODE_ENV !== 'production' && (
        <details>
          <summary>Error Details</summary>
          <pre>{error.message}</pre>
          <pre>{error.stack}</pre>
        </details>
      )}
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary
      FallbackComponent={AppErrorFallback}
      onError={logError}
      onReset={() => {
        // Clear any cached state that might cause the error again
        // queryClient.clear(); // React Query
        // store.dispatch(resetState()); // Redux
      }}
    >
      <Router>
        <Layout>
          <ErrorBoundary
            FallbackComponent={PageErrorFallback}
            onError={logError}
          >
            <AppRoutes />
          </ErrorBoundary>
        </Layout>
      </Router>
    </ErrorBoundary>
  );
}
```

---

## When to Use / When NOT to Use

### Use Error Boundaries When

- Wrapping route-level page components
- Around third-party components you do not control
- Around data-dependent sections (API responses, user-generated content)
- Around complex components with many edge cases
- With lazy-loaded components (Suspense + ErrorBoundary)
- At the app root as a last-resort catch-all

### Do NOT Use Error Boundaries When

- For event handler errors (use try/catch)
- For async errors in useEffect (use try/catch + state, or `useErrorBoundary`)
- Around simple, static components that are unlikely to error
- As a replacement for proper input validation
- As a substitute for fixing the actual bug

---

## Common Mistakes

### Mistake 1: Only Using One Top-Level Boundary

```jsx
// WRONG: One boundary replaces the ENTIRE app on any error
function App() {
  return (
    <ErrorBoundary fallback={<h1>App crashed</h1>}>
      <Header />
      <Sidebar />
      <MainContent />
      <Footer />
    </ErrorBoundary>
  );
}
// A bug in Sidebar kills Header, MainContent, and Footer too!

// RIGHT: Granular boundaries
function App() {
  return (
    <ErrorBoundary fallback={<h1>App crashed</h1>}>
      <Header />
      <div className="layout">
        <ErrorBoundary fallback={<p>Sidebar error</p>}>
          <Sidebar />
        </ErrorBoundary>
        <ErrorBoundary fallback={<p>Content error</p>}>
          <MainContent />
        </ErrorBoundary>
      </div>
      <Footer />
    </ErrorBoundary>
  );
}
```

### Mistake 2: Assuming Async Errors Are Caught

```jsx
// WRONG: Error Boundary will NOT catch this
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetch(`/api/users/${userId}`)
      .then(res => res.json())
      .then(setUser);
    // If fetch fails, error is swallowed! No boundary catches it.
  }, [userId]);

  return <div>{user?.name}</div>;
}

// RIGHT: Use useErrorBoundary hook or state-based error handling
import { useErrorBoundary } from 'react-error-boundary';

function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const { showBoundary } = useErrorBoundary();

  useEffect(() => {
    fetch(`/api/users/${userId}`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(setUser)
      .catch(showBoundary); // Sends error to nearest ErrorBoundary
  }, [userId, showBoundary]);

  return <div>{user?.name}</div>;
}
```

### Mistake 3: Not Providing a Reset Mechanism

```jsx
// WRONG: User is stuck on the error screen forever
<ErrorBoundary fallback={<p>Error occurred</p>}>
  <Widget />
</ErrorBoundary>
// The user has no way to recover!

// RIGHT: Always provide a way to retry or navigate away
<ErrorBoundary
  FallbackComponent={({ resetErrorBoundary }) => (
    <div>
      <p>Something went wrong</p>
      <button onClick={resetErrorBoundary}>Retry</button>
      <a href="/">Go Home</a>
    </div>
  )}
>
  <Widget />
</ErrorBoundary>
```

---

## Best Practices

1. **Layer your boundaries** -- Use a top-level boundary as a last resort, section-level boundaries for major areas, and feature-level boundaries for independent widgets.

2. **Match fallback UI to context** -- A review section error should show "Reviews unavailable," not a generic "Something went wrong."

3. **Always provide recovery** -- Give users a "Retry" button, a link to the homepage, or a way to refresh.

4. **Log errors to a monitoring service** -- Use the `onError` callback to send errors to Sentry, Datadog, LogRocket, or a custom endpoint.

5. **Use `resetKeys` for navigation** -- When route params change, auto-reset the boundary so stale errors do not persist.

6. **Pair with Suspense** -- Error Boundaries and Suspense work together for lazy-loaded components: Suspense handles the loading state, Error Boundary handles failures.

7. **Handle async errors explicitly** -- Use `useErrorBoundary` from `react-error-boundary` to send async errors to the nearest boundary.

8. **Test your error boundaries** -- Intentionally throw errors in development to verify fallback UIs look correct and recovery works.

---

## Quick Summary

Error Boundaries are React components that catch JavaScript errors anywhere in their child component tree. They prevent one broken component from crashing the entire application. Built with `getDerivedStateFromError` and `componentDidCatch` lifecycle methods (class components only), they display a fallback UI while the rest of the app continues working. The `react-error-boundary` library provides a production-ready implementation with retry, reset, and async error support. Strategic placement at app, page, and feature levels provides layered protection. Always pair Error Boundaries with error logging, meaningful fallback UIs, and recovery mechanisms.

---

## Key Points

- **Error Boundaries catch render errors** in child components, not event handlers or async code.
- **Class components only** -- React has no hook equivalent for Error Boundaries (use `react-error-boundary` library).
- **Granular placement** -- More boundaries = more resilient UI. Each section fails independently.
- **Fallback UI should be contextual** -- Tell users what failed and what they can still do.
- **Recovery matters** -- Always provide retry, navigation, or refresh options.
- **react-error-boundary** -- Production library with `resetKeys`, `useErrorBoundary`, and `onError` logging.
- **Pair with Suspense** -- Handle both loading and error states for lazy-loaded components.
- **Async errors need special handling** -- Use `useErrorBoundary` hook or try/catch with state.

---

## Practice Questions

1. Why must Error Boundaries be class components? What would a hypothetical `useErrorBoundary` hook need to do to work?

2. A developer puts one Error Boundary at the root of their app and considers error handling "done." What are the problems with this approach?

3. You have a dashboard with 6 independent widgets. One widget crashes. With no Error Boundaries, what happens? With one boundary around all widgets? With one boundary per widget?

4. An Error Boundary does not catch an error thrown inside a `useEffect` callback. Why? How would you handle this using the `react-error-boundary` library?

5. Your app uses code splitting with `React.lazy`. A user on a flaky network connection cannot download a chunk. How would you combine Error Boundaries and Suspense to handle this gracefully?

---

## Exercises

### Exercise 1: Build an Error Boundary from Scratch

Create a reusable Error Boundary class component that:
- Catches errors and shows a customizable fallback
- Provides a retry button that resets the error state
- Logs errors to the console with the component stack trace
- Accepts a `fallback` prop (either a React element or a render function)

Test it by creating a component that intentionally throws an error.

### Exercise 2: Granular Error Boundaries

Build a dashboard page with 4 widgets (Stats, Chart, Activity Feed, Notifications). Each widget should have its own Error Boundary with a contextual fallback. Add a "Chaos Mode" button that randomly breaks one widget. Verify that the other 3 keep working when one fails.

### Exercise 3: Async Error Recovery

Using `react-error-boundary`, build a data-fetching component that:
- Fetches data from a simulated API (use `setTimeout` + `Math.random()` for failures)
- Sends fetch errors to the nearest Error Boundary using `useErrorBoundary`
- Shows a fallback with "Retry" button on failure
- Automatically resets when the fetch URL changes (use `resetKeys`)
- Limits retries to 3 attempts, then shows a "Contact Support" message

---

## What Is Next?

Error Boundaries protect individual applications from crashing. But what happens when your application grows so large that one team cannot manage it all? In Chapter 30, we will explore **Micro-Frontends** -- an architectural pattern where independent teams build, deploy, and maintain separate pieces of a frontend application, composing them into a seamless whole.
