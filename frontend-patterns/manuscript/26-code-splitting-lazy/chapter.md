# Chapter 26: Code Splitting and Lazy Loading

## What You Will Learn

- Why large JavaScript bundles hurt performance
- How `React.lazy` and `Suspense` work together for component-level splitting
- Route-based code splitting strategies
- How `dynamic import()` works under the hood
- Prefetching techniques to make lazy loading invisible to users
- How to analyze your bundle and find what to split
- Practical patterns for real applications

## Why This Chapter Matters

Imagine you walk into a library to read one specific book. But instead of handing you that book, the librarian says, "Hold on, let me load every single book in the building onto this cart first. Then you can pick yours." That is what happens when you ship a single massive JavaScript bundle to the browser.

Your users came for one page. But you are forcing them to download JavaScript for every page, every feature, every component in your entire application before they can interact with anything.

Code splitting fixes this. It breaks your application into smaller chunks that load on demand. Users download only the code they need right now. The rest loads later, in the background, when they actually need it.

The difference is dramatic. A well-split application can reduce initial load time by 50-70%. For users on slow connections or low-end devices, it can mean the difference between your app being usable or abandoned.

---

## The Bundle Size Problem

### Before Code Splitting

```
Your Application:
+---------------------------------------------------------------+
|                    main.bundle.js (2.4 MB)                    |
|                                                               |
|  HomePage     ProductPage    AdminDashboard    UserSettings   |
|  ChartLib     MarkdownLib    DatePickerLib     PDFGenerator   |
|  LoginForm    SignupFlow     PaymentForm       ReportViewer   |
+---------------------------------------------------------------+

User visits homepage:
  Downloads: 2.4 MB of JavaScript
  Uses: ~200 KB of it
  Wasted: ~2.2 MB downloaded for nothing

Timeline:
|-------- Download 2.4 MB --------|--- Parse ---|-- Execute --|-- Interactive --|
0s                                2s            3s            4s               4.5s
```

### After Code Splitting

```
Your Application:
+-------------------+  +-------------------+  +-------------------+
| main.chunk.js     |  | products.chunk.js |  | admin.chunk.js    |
| (150 KB)          |  | (300 KB)          |  | (800 KB)          |
| Core + HomePage   |  | ProductPage       |  | AdminDashboard    |
|                   |  | ChartLib          |  | ReportViewer      |
+-------------------+  +-------------------+  +-------------------+

User visits homepage:
  Downloads: 150 KB of JavaScript
  Uses: 150 KB of it
  Wasted: 0 KB

Timeline:
|-- Download 150KB --|-- Parse --|-- Interactive --|
0s                  0.3s        0.5s              0.8s
```

---

## React.lazy and Suspense

### The Problem

You have a component that is heavy (it imports a large library) or rarely used (like an admin panel). You do not want it in your main bundle.

### The Solution

Use `React.lazy` to defer loading a component until it is actually rendered. Use `Suspense` to show a fallback while it loads.

### Before (Eager Loading)

```jsx
// All imports are bundled together, loaded upfront
import HomePage from './pages/HomePage';
import ProductPage from './pages/ProductPage';
import AdminDashboard from './pages/AdminDashboard'; // Heavy! 800KB
import UserSettings from './pages/UserSettings';

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/products" element={<ProductPage />} />
      <Route path="/admin" element={<AdminDashboard />} />
      <Route path="/settings" element={<UserSettings />} />
    </Routes>
  );
}

// Bundle: ONE file containing ALL pages
// main.bundle.js: 2.4 MB
// User downloading admin code even if they never visit /admin
```

### After (Lazy Loading)

```jsx
import { lazy, Suspense } from 'react';

// These imports happen ONLY when the component is first rendered
const HomePage = lazy(() => import('./pages/HomePage'));
const ProductPage = lazy(() => import('./pages/ProductPage'));
const AdminDashboard = lazy(() => import('./pages/AdminDashboard'));
const UserSettings = lazy(() => import('./pages/UserSettings'));

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/products" element={<ProductPage />} />
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/settings" element={<UserSettings />} />
      </Routes>
    </Suspense>
  );
}

function LoadingSpinner() {
  return (
    <div className="loading">
      <div className="spinner" />
      <p>Loading...</p>
    </div>
  );
}

// Output when user navigates to /admin:
// 1. Shows <LoadingSpinner /> immediately
// 2. Downloads admin.chunk.js in the background
// 3. Replaces spinner with <AdminDashboard /> when ready
```

### How It Works Under the Hood

```
React.lazy(() => import('./AdminDashboard'))

Step 1: React encounters <AdminDashboard /> in the tree
Step 2: Calls the factory function: () => import('./AdminDashboard')
Step 3: import() returns a Promise
Step 4: React "suspends" - throws a Promise up to nearest Suspense
Step 5: Suspense catches it, shows fallback
Step 6: When Promise resolves, React re-renders with the real component

+------------------+        +------------------+
|   Suspense       |        |   Suspense       |
|   +-----------+  |  -->   |   +-----------+  |
|   | Loading...|  |        |   | Dashboard |  |
|   +-----------+  |        |   +-----------+  |
|   (fallback)     |        |   (resolved)     |
+------------------+        +------------------+
```

---

## Route-Based Code Splitting

### The Pattern

The most natural place to split code is at route boundaries. Each page becomes its own chunk.

```jsx
// routes.jsx
import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout'; // Keep in main bundle

// Lazy load all page components
const Home = lazy(() => import('./pages/Home'));
const Products = lazy(() => import('./pages/Products'));
const ProductDetail = lazy(() => import('./pages/ProductDetail'));
const Cart = lazy(() => import('./pages/Cart'));
const Checkout = lazy(() => import('./pages/Checkout'));
const Account = lazy(() => import('./pages/Account'));

function PageLoader() {
  return (
    <div className="page-loader">
      <div className="skeleton-header" />
      <div className="skeleton-body" />
    </div>
  );
}

export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Layout>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/products" element={<Products />} />
            <Route path="/products/:id" element={<ProductDetail />} />
            <Route path="/cart" element={<Cart />} />
            <Route path="/checkout" element={<Checkout />} />
            <Route path="/account" element={<Account />} />
          </Routes>
        </Suspense>
      </Layout>
    </BrowserRouter>
  );
}

// Generated chunks:
//   main.js          - Layout, Router, core utils (always loaded)
//   home.chunk.js    - Home page (loaded on /)
//   products.chunk.js - Products page (loaded on /products)
//   detail.chunk.js  - Product detail (loaded on /products/:id)
//   cart.chunk.js    - Cart page (loaded on /cart)
//   checkout.chunk.js - Checkout (loaded on /checkout)
//   account.chunk.js - Account (loaded on /account)
```

### Per-Route Suspense Boundaries

```jsx
// More granular: different loading states per route
export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route
            path="/"
            element={
              <Suspense fallback={<HeroSkeleton />}>
                <Home />
              </Suspense>
            }
          />
          <Route
            path="/products"
            element={
              <Suspense fallback={<ProductGridSkeleton />}>
                <Products />
              </Suspense>
            }
          />
          <Route
            path="/checkout"
            element={
              <Suspense fallback={<CheckoutSkeleton />}>
                <Checkout />
              </Suspense>
            }
          />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

// Each route gets a contextual loading skeleton instead
// of a generic spinner. Better user experience!
```

---

## Dynamic import() Deep Dive

`import()` is the JavaScript feature that makes code splitting possible. It is not React-specific.

### Basic Dynamic Import

```jsx
// Static import (bundled together, loaded immediately)
import { calculateTax } from './tax-calculator';

// Dynamic import (separate chunk, loaded on demand)
async function handleCheckout(cart) {
  // tax-calculator.js is only downloaded when checkout happens
  const { calculateTax } = await import('./tax-calculator');
  const tax = calculateTax(cart.subtotal, cart.state);
  return cart.subtotal + tax;
}

// Output:
// 1. User browses products - tax-calculator.js NOT downloaded
// 2. User clicks "Checkout"
// 3. tax-calculator.chunk.js downloads (e.g., 45 KB)
// 4. Tax is calculated
// 5. Checkout continues
```

### Conditional Dynamic Imports

```jsx
// Load different modules based on conditions
async function loadEditor(format) {
  let editor;

  if (format === 'markdown') {
    // Only loads markdown editor when needed
    editor = await import('./editors/MarkdownEditor');
  } else if (format === 'richtext') {
    // Only loads rich text editor when needed
    editor = await import('./editors/RichTextEditor');
  } else {
    editor = await import('./editors/PlainTextEditor');
  }

  return editor.default;
}

// Usage in a component
function DocumentEditor({ format }) {
  const [Editor, setEditor] = useState(null);

  useEffect(() => {
    loadEditor(format).then(EditorComponent => {
      setEditor(() => EditorComponent);
    });
  }, [format]);

  if (!Editor) return <p>Loading editor...</p>;
  return <Editor />;
}
```

### Named Exports with Dynamic Import

```jsx
// The module exports multiple things
// utils/charts.js
export function BarChart() { /* ... */ }
export function LineChart() { /* ... */ }
export function PieChart() { /* ... */ }

// Dynamic import with named exports
const ChartComponent = lazy(() =>
  import('./utils/charts').then(module => ({
    // React.lazy expects a default export
    // This trick converts a named export to default
    default: module.BarChart,
  }))
);

// Or create a wrapper for cleaner syntax
function lazyNamed(importFn, name) {
  return lazy(() =>
    importFn().then(module => ({ default: module[name] }))
  );
}

const BarChart = lazyNamed(
  () => import('./utils/charts'),
  'BarChart'
);
const PieChart = lazyNamed(
  () => import('./utils/charts'),
  'PieChart'
);
```

---

## Prefetching: Making Lazy Loading Invisible

### The Problem with Naive Lazy Loading

```
Without prefetching:

User hovers over "Products" link
User clicks "Products" link
  |--- Download products.chunk.js (300ms) ---|
  |--- Parse and execute (100ms) ---|
  |--- Render (50ms) ---|
                                              User sees page (450ms later)

The user sees a loading spinner for almost half a second.
On slow connections, it could be 2-3 seconds.
```

### Solution: Prefetch on Hover

```jsx
import { lazy, Suspense, useCallback } from 'react';

// Store the import function so we can call it early
const importProducts = () => import('./pages/Products');

// Create the lazy component
const Products = lazy(importProducts);

function Navigation() {
  const prefetchProducts = useCallback(() => {
    // Start loading the chunk when user hovers over the link
    importProducts();
  }, []);

  return (
    <nav>
      <Link to="/">Home</Link>
      <Link
        to="/products"
        onMouseEnter={prefetchProducts}  // Prefetch on hover!
        onFocus={prefetchProducts}        // Also on keyboard focus
      >
        Products
      </Link>
    </nav>
  );
}

// Timeline WITH prefetching:
//
// User hovers over "Products" (starts download)
//   |--- Download products.chunk.js (300ms) ---|
// User clicks 200ms later (chunk already downloading!)
//   |--- Remaining download (100ms) ---|
//   |--- Parse + Render (150ms) ---|
//                                       User sees page (250ms)
//
// vs WITHOUT prefetching: 450ms
// Savings: ~200ms (feels instant)
```

### Prefetch with Intersection Observer

```jsx
// Prefetch when a component scrolls into view
import { useEffect, useRef, lazy, Suspense } from 'react';

const HeavyChart = lazy(() => import('./components/HeavyChart'));

function Dashboard() {
  const chartRef = useRef(null);
  const prefetched = useRef(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !prefetched.current) {
          // User is scrolling toward the chart area
          import('./components/HeavyChart');
          prefetched.current = true;
          observer.disconnect();
        }
      },
      { rootMargin: '200px' } // Start loading 200px before visible
    );

    if (chartRef.current) {
      observer.observe(chartRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <div>
      <h1>Dashboard</h1>
      <div>...other content...</div>

      {/* Sentinel element triggers prefetch */}
      <div ref={chartRef}>
        <Suspense fallback={<ChartSkeleton />}>
          <HeavyChart />
        </Suspense>
      </div>
    </div>
  );
}
```

### Prefetch with Webpack Magic Comments

```jsx
// Webpack-specific prefetch hints
const AdminPanel = lazy(() =>
  import(
    /* webpackPrefetch: true */
    './pages/AdminPanel'
  )
);
// Webpack adds <link rel="prefetch"> to the HTML
// Browser downloads in idle time, lowest priority

const Checkout = lazy(() =>
  import(
    /* webpackPreload: true */
    './pages/Checkout'
  )
);
// Webpack adds <link rel="preload"> to the HTML
// Browser downloads immediately, high priority

// You can also name your chunks for easier debugging
const Products = lazy(() =>
  import(
    /* webpackChunkName: "products-page" */
    './pages/Products'
  )
);
// Creates: products-page.chunk.js (instead of random hash)
```

---

## Component-Level Code Splitting

Not all splitting needs to happen at the route level. Heavy components within a page are great candidates too.

```jsx
import { lazy, Suspense, useState } from 'react';

// Heavy components loaded on demand
const MarkdownPreview = lazy(() => import('./MarkdownPreview'));
const CodeEditor = lazy(() => import('./CodeEditor'));
const ImageCropper = lazy(() => import('./ImageCropper'));

function PostEditor() {
  const [showPreview, setShowPreview] = useState(false);
  const [showImageCrop, setShowImageCrop] = useState(false);

  return (
    <div>
      <h2>Write a Post</h2>

      {/* Code editor loads when PostEditor mounts */}
      <Suspense fallback={<div>Loading editor...</div>}>
        <CodeEditor language="markdown" />
      </Suspense>

      {/* Preview only loads when user clicks the button */}
      <button onClick={() => setShowPreview(!showPreview)}>
        {showPreview ? 'Hide Preview' : 'Show Preview'}
      </button>

      {showPreview && (
        <Suspense fallback={<div>Loading preview...</div>}>
          <MarkdownPreview />
        </Suspense>
      )}

      {/* Image cropper loads only when user adds an image */}
      <button onClick={() => setShowImageCrop(true)}>
        Add Image
      </button>

      {showImageCrop && (
        <Suspense fallback={<div>Loading image tools...</div>}>
          <ImageCropper onCrop={handleCrop} />
        </Suspense>
      )}
    </div>
  );
}

// Bundle result:
// main.js            - PostEditor shell (~5 KB)
// code-editor.chunk  - CodeEditor + dependencies (~200 KB)
// md-preview.chunk   - MarkdownPreview + parser (~150 KB)
// image-crop.chunk   - ImageCropper + canvas lib (~100 KB)
//
// Users who never preview or crop images save 250 KB!
```

---

## Bundle Analysis

Before you split code, you need to know what is in your bundle.

### Using webpack-bundle-analyzer

```bash
# Install
npm install --save-dev webpack-bundle-analyzer

# For Create React App (using source-map-explorer)
npm install --save-dev source-map-explorer

# Add to package.json scripts
# "analyze": "source-map-explorer 'build/static/js/*.js'"

# Run
npm run build
npm run analyze
```

### Reading the Analysis

```
Bundle Analysis Output (simplified):

+---------------------------------------------------------------+
|                    main.bundle.js (2.4 MB)                    |
+---------------------------------------------------------------+
|                                                               |
|  +------------------+  +------------------+  +--------------+ |
|  | node_modules     |  | src/pages        |  | src/utils    | |
|  | (1.8 MB - 75%)   |  | (400 KB - 17%)   |  | (200 KB)    | |
|  |                  |  |                  |  |              | |
|  | moment.js  500KB |  | Admin    300KB   |  |              | |
|  | lodash     200KB |  | Products 50KB    |  |              | |
|  | chart.js   400KB |  | Home     30KB    |  |              | |
|  | react-pdf  300KB |  | Settings 20KB    |  |              | |
|  | others     400KB |  |                  |  |              | |
|  +------------------+  +------------------+  +--------------+ |
+---------------------------------------------------------------+

Findings:
1. moment.js (500KB) - Replace with date-fns (30KB) or dayjs (7KB)
2. lodash (200KB) - Import individual functions: import get from 'lodash/get'
3. chart.js (400KB) - Lazy load, only used on Admin page
4. react-pdf (300KB) - Lazy load, only used in Reports
5. Admin page (300KB) - Lazy load, only 5% of users are admins
```

### Actionable Steps After Analysis

```jsx
// BEFORE: Everything in main bundle
import moment from 'moment';           // 500 KB!
import _ from 'lodash';                 // 200 KB!
import { Chart } from 'chart.js';       // 400 KB!

// AFTER: Optimized imports + lazy loading

// Step 1: Replace heavy libraries with lighter alternatives
import { format, parseISO } from 'date-fns'; // 30 KB (tree-shakable)

// Step 2: Import only what you need from lodash
import get from 'lodash/get';           // 2 KB instead of 200 KB
import debounce from 'lodash/debounce'; // 1 KB

// Step 3: Lazy load heavy components
const ChartDashboard = lazy(() => import('./ChartDashboard'));
// chart.js only downloads when ChartDashboard renders

// Result: Main bundle went from 2.4 MB to 350 KB
```

### Vite Bundle Analysis

```bash
# For Vite projects
npm install --save-dev rollup-plugin-visualizer

# vite.config.js
import { visualizer } from 'rollup-plugin-visualizer';

export default {
  plugins: [
    visualizer({
      open: true,           // Auto-open in browser
      gzipSize: true,       // Show gzipped sizes
      brotliSize: true,     // Show brotli sizes
    }),
  ],
};

# Run build to generate report
npm run build
# Opens an interactive treemap in your browser
```

---

## Real-World Use Case: SaaS Dashboard

```jsx
// A SaaS app with many features, but users only use a few at a time

import { lazy, Suspense } from 'react';
import { Routes, Route, NavLink } from 'react-router-dom';

// Core: always loaded (small)
import AppShell from './components/AppShell';
import Sidebar from './components/Sidebar';

// Features: lazy loaded
const Dashboard = lazy(() => import('./features/Dashboard'));
const Analytics = lazy(() =>
  import(/* webpackChunkName: "analytics" */ './features/Analytics')
);
const Reports = lazy(() =>
  import(/* webpackChunkName: "reports" */ './features/Reports')
);
const TeamManagement = lazy(() =>
  import(/* webpackChunkName: "team" */ './features/TeamManagement')
);
const BillingSettings = lazy(() =>
  import(/* webpackChunkName: "billing" */ './features/BillingSettings')
);
const Integrations = lazy(() =>
  import(/* webpackChunkName: "integrations" */ './features/Integrations')
);

// Loading component with skeleton matching each feature
function FeatureLoader({ feature }) {
  return (
    <div className="feature-loader">
      <div className="skeleton-nav" />
      <div className="skeleton-content" />
      <p>Loading {feature}...</p>
    </div>
  );
}

// Wrapper that adds Suspense to lazy routes
function LazyRoute({ component: Component, name }) {
  return (
    <Suspense fallback={<FeatureLoader feature={name} />}>
      <Component />
    </Suspense>
  );
}

export default function App() {
  return (
    <AppShell>
      <Sidebar
        links={[
          { to: '/', label: 'Dashboard', prefetch: Dashboard },
          { to: '/analytics', label: 'Analytics', prefetch: Analytics },
          { to: '/reports', label: 'Reports', prefetch: Reports },
          { to: '/team', label: 'Team', prefetch: TeamManagement },
          { to: '/billing', label: 'Billing', prefetch: BillingSettings },
        ]}
      />
      <main>
        <Routes>
          <Route
            path="/"
            element={<LazyRoute component={Dashboard} name="Dashboard" />}
          />
          <Route
            path="/analytics"
            element={<LazyRoute component={Analytics} name="Analytics" />}
          />
          <Route
            path="/reports"
            element={<LazyRoute component={Reports} name="Reports" />}
          />
          <Route
            path="/team"
            element={<LazyRoute component={TeamManagement} name="Team" />}
          />
          <Route
            path="/billing"
            element={<LazyRoute component={BillingSettings} name="Billing" />}
          />
        </Routes>
      </main>
    </AppShell>
  );
}

// Bundle output:
//   main.js         - 120 KB (AppShell + Sidebar + Router)
//   analytics.js    - 280 KB (Chart.js + analytics components)
//   reports.js      - 350 KB (PDF generation + report templates)
//   team.js         - 80 KB  (team management UI)
//   billing.js      - 95 KB  (Stripe integration + forms)
//   integrations.js - 60 KB  (webhook config UI)
//
// Total: 985 KB, but user downloads only ~200 KB initially
```

---

## When to Use / When NOT to Use

### Use Code Splitting When

- Your bundle exceeds 200 KB (gzipped)
- You have features only some users access (admin panels)
- You have heavy dependencies used on specific pages (chart libraries, PDF generators)
- Your app has many routes
- Initial load time is a priority

### Do NOT Use Code Splitting When

- Your entire app is small (under 50 KB gzipped)
- The overhead of loading spinners would hurt UX more than the bundle size
- You are building a single-page tool with no navigation
- Every feature is used on every page load

---

## Common Mistakes

### Mistake 1: Splitting Too Aggressively

```jsx
// WRONG: Splitting a tiny 2KB component
const Button = lazy(() => import('./Button'));
// The chunk loading overhead (HTTP request, parsing)
// is MORE expensive than just including 2KB in the main bundle.

// RIGHT: Only split substantial components (50KB+)
const ChartDashboard = lazy(() => import('./ChartDashboard'));
// This component pulls in chart.js (400KB). Worth splitting!
```

### Mistake 2: No Fallback or Poor Fallback

```jsx
// WRONG: No Suspense wrapper
const Page = lazy(() => import('./Page'));
function App() {
  return <Page />; // CRASHES! "A component suspended while rendering,
                   //  but no Suspense boundary was found"
}

// WRONG: Generic, unhelpful fallback
<Suspense fallback={<div>...</div>}>
  <Page />
</Suspense>

// RIGHT: Contextual skeleton fallback
<Suspense fallback={<PageSkeleton />}>
  <Page />
</Suspense>
```

### Mistake 3: No Error Handling for Failed Chunks

```jsx
// Network can fail! Chunks might not load.
// WRONG: No error handling
const Page = lazy(() => import('./Page'));
// If network fails, user sees blank screen or crash

// RIGHT: Combine with Error Boundary (Chapter 29)
import { ErrorBoundary } from 'react-error-boundary';

function ChunkErrorFallback({ error, resetErrorBoundary }) {
  return (
    <div>
      <p>Failed to load this section.</p>
      <button onClick={resetErrorBoundary}>Try Again</button>
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary FallbackComponent={ChunkErrorFallback}>
      <Suspense fallback={<PageSkeleton />}>
        <Page />
      </Suspense>
    </ErrorBoundary>
  );
}
```

### Mistake 4: Not Handling Stale Chunks After Deployment

```
Problem: User has tab open for hours. You deploy new code.
Old chunk URLs no longer exist on the server.
User navigates to a lazy-loaded route --> 404 on chunk file!

Solution: Catch chunk load errors and prompt refresh.
```

```jsx
// Retry logic for chunk loading failures
function lazyWithRetry(importFn) {
  return lazy(() =>
    importFn().catch(error => {
      // If chunk fails to load (likely stale deployment)
      console.error('Chunk load failed:', error);

      // Option 1: Retry once
      return importFn().catch(() => {
        // Option 2: Force reload on second failure
        window.location.reload();
        // Return a dummy component to prevent crash
        return { default: () => null };
      });
    })
  );
}

const Products = lazyWithRetry(() => import('./pages/Products'));
```

---

## Best Practices

1. **Start with route-based splitting** -- It gives the biggest wins with the least effort.

2. **Analyze before splitting** -- Use bundle analysis tools to find the biggest chunks first.

3. **Set a bundle budget** -- Aim for under 150 KB gzipped for the initial bundle.

4. **Prefetch likely next pages** -- Use hover/focus prefetching for navigation links.

5. **Use contextual loading states** -- Skeleton screens that match the incoming content are better than generic spinners.

6. **Handle errors gracefully** -- Wrap lazy components in Error Boundaries for network failures.

7. **Name your chunks** -- Use `webpackChunkName` or Vite's `manualChunks` for readable chunk names in DevTools.

8. **Test on slow connections** -- Throttle your network in DevTools to see what lazy loading actually feels like.

9. **Measure the impact** -- Compare Lighthouse scores before and after code splitting.

---

## Quick Summary

Code splitting breaks your JavaScript bundle into smaller chunks that load on demand. `React.lazy` and `Suspense` make this easy at the component level. Route-based splitting is the most impactful starting point. Dynamic `import()` lets you load any module on demand, not just React components. Prefetching on hover or with Intersection Observer makes lazy loading feel instant. Bundle analysis tools help you find the biggest optimization opportunities. Always handle chunk load errors gracefully and provide meaningful loading states.

---

## Key Points

- **Bundle size matters** -- Large bundles directly increase time-to-interactive.
- **React.lazy + Suspense** -- The standard way to lazy load React components.
- **Route-based splitting** -- Split at page boundaries for maximum impact with minimal effort.
- **dynamic import()** -- JavaScript feature that loads modules on demand (not React-specific).
- **Prefetching** -- Load chunks before the user needs them (on hover, on visible, idle time).
- **Bundle analysis** -- Identify what is large, what is unused, what should be split.
- **Error handling** -- Chunks can fail to load. Always have a recovery strategy.
- **Do not over-split** -- Splitting tiny components adds overhead without benefit.

---

## Practice Questions

1. A developer uses `React.lazy` for every single component in their app, including small 1 KB utility components. What problems will this cause, and what is a better approach?

2. Explain the difference between `webpackPrefetch` and `webpackPreload`. When would you use each one?

3. Your app's main bundle is 1.2 MB. After bundle analysis, you find that 400 KB comes from `moment.js` (used everywhere) and 300 KB comes from `chart.js` (used only on the analytics page). What is your optimization strategy for each?

4. A user reports that navigating between pages in your app shows a loading spinner for 2-3 seconds. The lazy-loaded chunks are only 50 KB each. What could be causing this, and how would you fix it?

5. After deploying a new version of your app, some users report blank screens when navigating. What is happening, and how do you prevent it?

---

## Exercises

### Exercise 1: Split an Existing App

Take a React app (or create a simple one with 4-5 routes). Measure the initial bundle size. Then apply route-based code splitting with `React.lazy` and `Suspense`. Measure again. Document the before and after bundle sizes and loading times.

### Exercise 2: Build a Prefetching System

Create a `PrefetchLink` component that wraps React Router's `Link`. It should prefetch the target page's chunk on hover (with a 100ms debounce to avoid prefetching on quick mouse movements). Test it by adding artificial delay to your chunks and comparing the perceived load time.

### Exercise 3: Bundle Analysis Report

Run a bundle analysis on a project (yours or an open-source one). Create a report listing:
- The 5 largest dependencies and their sizes
- Which of those could be replaced with smaller alternatives
- Which components should be lazy loaded
- Estimated savings from each optimization

---

## What Is Next?

Code splitting helps you send less JavaScript to the browser. But even with a smaller bundle, rendering thousands of items (like a long product list or data table) can bring the browser to its knees. In Chapter 27, we will explore the **Virtualization Pattern** -- a technique that renders only the items currently visible on screen, making lists of any size feel fast.
