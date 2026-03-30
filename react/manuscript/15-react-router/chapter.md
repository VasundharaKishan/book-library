# Chapter 15: React Router — Navigation and Routing

## Learning Goals

By the end of this chapter, you will be able to:

- Understand the difference between server-side and client-side routing
- Set up React Router in a project
- Create routes that map URLs to components
- Navigate between pages using Link and NavLink
- Use route parameters and query strings
- Build nested routes with shared layouts
- Redirect users programmatically with useNavigate
- Implement protected routes that require authentication
- Handle 404 (not found) pages
- Organize routes for a real-world application

---

## Why Routing Matters

Every application you have built so far has been a single page. When a user clicks a button, the UI changes — but the URL in the browser stays the same. This creates several problems:

- **Users cannot bookmark a specific view** — refreshing always goes back to the starting page
- **The browser's back and forward buttons do not work** — there is no navigation history
- **Users cannot share a link to a specific page** — every link goes to the same place
- **Search engines cannot index different pages** — there is only one URL

Routing solves all of these problems by mapping URLs to different views in your application.

### Server-Side vs Client-Side Routing

In traditional web applications, routing happens on the server:

1. User clicks a link to `/about`
2. Browser sends a request to the server
3. Server processes the request and returns a full HTML page
4. Browser replaces the entire page with the new HTML

This works but it is slow — every navigation requires a full page reload.

In a React single-page application (SPA), routing happens on the client:

1. User clicks a link to `/about`
2. JavaScript intercepts the click and prevents the browser default
3. JavaScript updates the URL using the History API
4. React renders the component associated with `/about`
5. No server request, no page reload — the transition is instant

React Router is the standard library that makes client-side routing work in React.

---

## Setting Up React Router

### Installation

React Router v6 (the current version) is installed as a separate package:

```bash
npm install react-router-dom
```

The package is called `react-router-dom` because it is the version for web applications (the DOM). There is also `react-router-native` for React Native mobile apps, but we will focus on the web version.

### Basic Setup

Wrap your application in a `BrowserRouter` to enable routing:

```jsx
// main.jsx (or index.jsx)
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>
);
```

`BrowserRouter` uses the browser's History API to keep the URL in sync with your UI. It must wrap your entire application (or at least the part that uses routing).

---

## Defining Routes

### The Routes and Route Components

Use `Routes` and `Route` to define which components render at which URLs:

```jsx
// App.jsx
import { Routes, Route } from "react-router-dom";

function App() {
  return (
    <div>
      <h1>My App</h1>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />
      </Routes>
    </div>
  );
}

function Home() {
  return <h2>Welcome to the Home Page</h2>;
}

function About() {
  return <h2>About Us</h2>;
}

function Contact() {
  return <h2>Contact Us</h2>;
}
```

How this works:

- When the URL is `/`, React renders `<Home />`
- When the URL is `/about`, React renders `<About />`
- When the URL is `/contact`, React renders `<Contact />`
- The `<h1>My App</h1>` renders on every page because it is outside `<Routes>`

### Route Matching

React Router v6 uses **exact matching by default**. The path `/about` matches only `/about`, not `/about/team` or `/about/history`. This is different from older versions of React Router where you had to add an `exact` prop.

Routes are also **ranked by specificity**. If multiple routes could match, React Router picks the most specific one:

```jsx
<Routes>
  <Route path="/users" element={<UserList />} />
  <Route path="/users/new" element={<NewUser />} />
  <Route path="/users/:id" element={<UserProfile />} />
</Routes>
```

Visiting `/users/new` renders `<NewUser />`, not `<UserProfile />` with `id` equal to `"new"`. React Router knows that a static segment (`new`) is more specific than a dynamic parameter (`:id`).

---

## Navigation

### The Link Component

Never use regular `<a>` tags for internal navigation in a React app. An `<a>` tag triggers a full page reload, which defeats the purpose of a SPA. Instead, use `Link`:

```jsx
import { Link } from "react-router-dom";

function Navigation() {
  return (
    <nav>
      <Link to="/">Home</Link>
      <Link to="/about">About</Link>
      <Link to="/contact">Contact</Link>
    </nav>
  );
}
```

`Link` renders an `<a>` tag in the DOM but intercepts the click event, prevents the page reload, and uses the History API to update the URL. The user sees the URL change, the browser history updates, and React renders the new route — all without a server request.

### The NavLink Component

`NavLink` is like `Link` but it knows whether it is "active" — meaning its `to` prop matches the current URL. This is perfect for navigation menus where you want to highlight the current page:

```jsx
import { NavLink } from "react-router-dom";

function Navigation() {
  return (
    <nav>
      <NavLink
        to="/"
        style={({ isActive }) => ({
          fontWeight: isActive ? "bold" : "normal",
          color: isActive ? "blue" : "gray",
        })}
      >
        Home
      </NavLink>

      <NavLink
        to="/about"
        className={({ isActive }) => (isActive ? "nav-active" : "")}
      >
        About
      </NavLink>

      <NavLink
        to="/contact"
        className={({ isActive }) => (isActive ? "nav-active" : "")}
      >
        Contact
      </NavLink>
    </nav>
  );
}
```

`NavLink` passes `{ isActive, isPending }` to the `style` and `className` props when they are functions. This lets you dynamically style the active link.

By default, `NavLink` also adds an `active` class to the rendered `<a>` tag when it matches the current URL, so you can style it with CSS:

```css
a.active {
  font-weight: bold;
  color: blue;
}
```

### Programmatic Navigation with useNavigate

Sometimes you need to navigate in response to an event that is not a link click — for example, after a form submission or after a timer:

```jsx
import { useNavigate } from "react-router-dom";

function LoginForm() {
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    const success = await login(username, password);

    if (success) {
      navigate("/dashboard");
    }
  }

  return <form onSubmit={handleSubmit}>{/* form fields */}</form>;
}
```

`useNavigate` returns a function that you call with the target path. You can also:

```jsx
const navigate = useNavigate();

// Go to a specific path
navigate("/dashboard");

// Go back (like pressing the browser back button)
navigate(-1);

// Go forward
navigate(1);

// Replace the current history entry (no back button)
navigate("/dashboard", { replace: true });

// Pass state to the destination
navigate("/dashboard", { state: { fromLogin: true } });
```

The `replace: true` option is useful after login — you do not want the user to press "back" and land on the login form again.

---

## Route Parameters

Route parameters let you create dynamic routes that match a pattern. They are defined with a colon prefix:

```jsx
<Route path="/users/:userId" element={<UserProfile />} />
```

This route matches `/users/1`, `/users/42`, `/users/abc`, and any other path that starts with `/users/` followed by one segment.

### Reading Parameters with useParams

```jsx
import { useParams } from "react-router-dom";

function UserProfile() {
  const { userId } = useParams();

  return <h2>User Profile: {userId}</h2>;
}

// URL: /users/42
// Renders: <h2>User Profile: 42</h2>
```

### Multiple Parameters

```jsx
<Route path="/posts/:year/:month/:slug" element={<BlogPost />} />
```

```jsx
function BlogPost() {
  const { year, month, slug } = useParams();

  return (
    <div>
      <p>Year: {year}, Month: {month}</p>
      <h2>{slug}</h2>
    </div>
  );
}

// URL: /posts/2025/03/learning-react
// year = "2025", month = "03", slug = "learning-react"
```

Note that route parameters are always strings. If you need a number, convert it:

```jsx
function UserProfile() {
  const { userId } = useParams();
  const numericId = Number(userId);

  // Use numericId for API calls, comparisons, etc.
}
```

### Practical Example: Product Pages

```jsx
import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";

function ProductList() {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    fetch("/api/products")
      .then(res => res.json())
      .then(setProducts);
  }, []);

  return (
    <div>
      <h2>Products</h2>
      <ul>
        {products.map(product => (
          <li key={product.id}>
            <Link to={`/products/${product.id}`}>{product.name}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

function ProductDetail() {
  const { productId } = useParams();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    fetch(`/api/products/${productId}`)
      .then(res => {
        if (!res.ok) throw new Error("Product not found");
        return res.json();
      })
      .then(data => {
        setProduct(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [productId]);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;
  if (!product) return <p>Product not found.</p>;

  return (
    <div>
      <h2>{product.name}</h2>
      <p>{product.description}</p>
      <p>Price: ${product.price}</p>
      <Link to="/products">Back to Products</Link>
    </div>
  );
}
```

```jsx
// Routes
<Routes>
  <Route path="/products" element={<ProductList />} />
  <Route path="/products/:productId" element={<ProductDetail />} />
</Routes>
```

---

## Query Strings (Search Parameters)

Query strings are the key-value pairs after the `?` in a URL: `/search?q=react&page=2`. They are useful for filters, search terms, pagination, and other non-hierarchical data.

### Reading Query Strings with useSearchParams

```jsx
import { useSearchParams } from "react-router-dom";

function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();

  const query = searchParams.get("q") || "";
  const page = Number(searchParams.get("page")) || 1;
  const sort = searchParams.get("sort") || "relevance";

  return (
    <div>
      <h2>Search Results for: {query}</h2>
      <p>Page: {page}, Sort: {sort}</p>
    </div>
  );
}

// URL: /search?q=react&page=2&sort=date
// query = "react", page = 2, sort = "date"
```

### Updating Query Strings

```jsx
function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const query = searchParams.get("q") || "";
  const page = Number(searchParams.get("page")) || 1;

  function handleSearch(newQuery) {
    setSearchParams({ q: newQuery, page: "1" });
  }

  function handlePageChange(newPage) {
    setSearchParams(prev => {
      prev.set("page", String(newPage));
      return prev;
    });
  }

  return (
    <div>
      <input
        value={query}
        onChange={e => handleSearch(e.target.value)}
        placeholder="Search..."
      />

      <div>
        <button
          disabled={page <= 1}
          onClick={() => handlePageChange(page - 1)}
        >
          Previous
        </button>
        <span>Page {page}</span>
        <button onClick={() => handlePageChange(page + 1)}>Next</button>
      </div>
    </div>
  );
}
```

### When to Use Route Parameters vs Query Strings

| Use Case | Route Parameters | Query Strings |
|----------|-----------------|---------------|
| Identifies a specific resource | `/users/42` | No |
| Filtering or sorting | No | `/products?sort=price&category=books` |
| Search terms | No | `/search?q=react` |
| Pagination | No | `/products?page=3` |
| Required for the page to work | `/posts/:id` | No |
| Optional, modifies how data is shown | No | `?view=grid` |

**Rule of thumb:** If the value identifies *what* to show, use a route parameter. If it modifies *how* to show it, use a query string.

---

## Nested Routes and Layouts

Real applications have shared layouts — a navigation bar, a sidebar, a footer that persist across pages. Nested routes let you define layouts that wrap groups of routes.

### The Outlet Component

`Outlet` is a placeholder that renders the matched child route:

```jsx
import { Outlet, NavLink } from "react-router-dom";

function Layout() {
  return (
    <div>
      <header>
        <nav>
          <NavLink to="/">Home</NavLink>
          <NavLink to="/about">About</NavLink>
          <NavLink to="/dashboard">Dashboard</NavLink>
        </nav>
      </header>

      <main>
        <Outlet />
      </main>

      <footer>
        <p>My App Footer</p>
      </footer>
    </div>
  );
}
```

### Defining Nested Routes

```jsx
function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="about" element={<About />} />
        <Route path="dashboard" element={<Dashboard />} />
      </Route>
    </Routes>
  );
}
```

How this works:

- The parent `<Route path="/" element={<Layout />}>` renders `Layout` for all paths starting with `/`
- `<Route index>` renders `Home` when the path is exactly `/` (the index route)
- `<Route path="about">` renders `About` when the path is `/about`
- The child route's element renders inside `<Outlet />` in the `Layout` component

The result: `Layout` renders on every page, and the content area (where `<Outlet />` is) changes based on the URL.

### Multi-Level Nesting

You can nest routes multiple levels deep. This is common for dashboard-style applications:

```jsx
function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="about" element={<About />} />

        <Route path="dashboard" element={<DashboardLayout />}>
          <Route index element={<DashboardHome />} />
          <Route path="profile" element={<Profile />} />
          <Route path="settings" element={<Settings />} />
          <Route path="orders" element={<Orders />} />
          <Route path="orders/:orderId" element={<OrderDetail />} />
        </Route>
      </Route>
    </Routes>
  );
}
```

```jsx
function DashboardLayout() {
  return (
    <div style={{ display: "flex" }}>
      <aside>
        <nav>
          <NavLink to="/dashboard">Overview</NavLink>
          <NavLink to="/dashboard/profile">Profile</NavLink>
          <NavLink to="/dashboard/settings">Settings</NavLink>
          <NavLink to="/dashboard/orders">Orders</NavLink>
        </nav>
      </aside>

      <section style={{ flex: 1 }}>
        <Outlet />
      </section>
    </div>
  );
}
```

The URL `/dashboard/orders/42` renders:

1. `Layout` (the outer layout with the main nav)
2. Inside its `<Outlet />`: `DashboardLayout` (the dashboard sidebar)
3. Inside its `<Outlet />`: `OrderDetail` (the specific order)

Each layout layer renders, and the `Outlet` at each level renders the next level down.

---

## Handling 404 Pages

Use a catch-all route with `path="*"` to handle URLs that do not match any defined route:

```jsx
function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="about" element={<About />} />
        <Route path="contact" element={<Contact />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}

function NotFound() {
  return (
    <div>
      <h2>404 — Page Not Found</h2>
      <p>The page you are looking for does not exist.</p>
      <Link to="/">Go back to Home</Link>
    </div>
  );
}
```

The `*` path matches anything that was not matched by a more specific route. Place it as the last route inside `<Routes>`.

---

## Protected Routes

Many applications have pages that should only be accessible to logged-in users. Protected routes check the user's authentication status and redirect to a login page if needed.

### Building a Protected Route Component

```jsx
import { Navigate, useLocation } from "react-router-dom";

function ProtectedRoute({ children }) {
  const { user } = useAuth(); // Your auth context hook
  const location = useLocation();

  if (!user) {
    // Redirect to login, but save where we came from
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}
```

`Navigate` is a component that redirects immediately when rendered. The `state` prop passes the current location so the login page can redirect back after successful login. The `replace` prop prevents the protected route from appearing in the browser history.

### Using Protected Routes

```jsx
function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="about" element={<About />} />
        <Route path="login" element={<LoginPage />} />

        {/* Protected routes */}
        <Route
          path="dashboard"
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<DashboardHome />} />
          <Route path="profile" element={<Profile />} />
          <Route path="settings" element={<Settings />} />
        </Route>

        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}
```

### The Auth Context

Here is how the auth context that powers protected routes might look:

```jsx
import { createContext, useContext, useState } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("user");
    return saved ? JSON.parse(saved) : null;
  });

  function login(userData) {
    setUser(userData);
    localStorage.setItem("user", JSON.stringify(userData));
  }

  function logout() {
    setUser(null);
    localStorage.removeItem("user");
  }

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
```

### The Login Page with Redirect

```jsx
import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "./AuthContext";

function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Where the user was trying to go before being redirected to login
  const from = location.state?.from?.pathname || "/dashboard";

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);

    try {
      const response = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) throw new Error("Invalid credentials");

      const userData = await response.json();
      login(userData);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div>
      <h2>Login</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          placeholder="Email"
          required
        />
        <input
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          placeholder="Password"
          required
        />
        <button type="submit">Log In</button>
      </form>
    </div>
  );
}
```

The key piece: after login succeeds, `navigate(from, { replace: true })` sends the user back to the page they were originally trying to visit.

### Role-Based Protection

You can extend the pattern for role-based access:

```jsx
function ProtectedRoute({ children, requiredRole }) {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requiredRole && user.role !== requiredRole) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
}

// Usage
<Route
  path="admin"
  element={
    <ProtectedRoute requiredRole="admin">
      <AdminPanel />
    </ProtectedRoute>
  }
/>
```

---

## useLocation — Reading the Current Location

`useLocation` returns the current location object, which contains information about the current URL:

```jsx
import { useLocation } from "react-router-dom";

function CurrentPage() {
  const location = useLocation();

  console.log(location);
  // {
  //   pathname: "/dashboard/settings",
  //   search: "?tab=security",
  //   hash: "#password",
  //   state: { fromLogin: true },
  //   key: "default"
  // }

  return <p>You are at: {location.pathname}</p>;
}
```

### Practical Use: Scroll to Top on Navigation

By default, React Router does not scroll to the top of the page when navigating. Here is a component that fixes this:

```jsx
import { useEffect } from "react";
import { useLocation } from "react-router-dom";

function ScrollToTop() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return null;
}

// Add it inside BrowserRouter
function App() {
  return (
    <>
      <ScrollToTop />
      <Routes>{/* ... */}</Routes>
    </>
  );
}
```

### Practical Use: Analytics Tracking

```jsx
function usePageTracking() {
  const location = useLocation();

  useEffect(() => {
    // Send page view to analytics
    analytics.pageView(location.pathname + location.search);
  }, [location]);
}

function App() {
  usePageTracking();

  return <Routes>{/* ... */}</Routes>;
}
```

---

## Route Organization Patterns

As your application grows, you will want to organize routes in a maintainable way.

### Pattern 1: Route Configuration Array

```jsx
const routes = [
  { path: "/", element: <Home /> },
  { path: "/about", element: <About /> },
  { path: "/products", element: <ProductList /> },
  { path: "/products/:id", element: <ProductDetail /> },
  { path: "/login", element: <LoginPage /> },
  {
    path: "/dashboard",
    element: (
      <ProtectedRoute>
        <DashboardLayout />
      </ProtectedRoute>
    ),
    children: [
      { index: true, element: <DashboardHome /> },
      { path: "profile", element: <Profile /> },
      { path: "settings", element: <Settings /> },
    ],
  },
  { path: "*", element: <NotFound /> },
];
```

You can use `useRoutes` to render a route configuration object instead of JSX:

```jsx
import { useRoutes } from "react-router-dom";

function App() {
  const element = useRoutes(routes);
  return element;
}
```

### Pattern 2: Feature-Based Route Files

For larger applications, define routes alongside the features they belong to:

```
src/
  features/
    auth/
      LoginPage.jsx
      RegisterPage.jsx
      routes.jsx          ← auth routes
    dashboard/
      DashboardHome.jsx
      Profile.jsx
      Settings.jsx
      routes.jsx          ← dashboard routes
    products/
      ProductList.jsx
      ProductDetail.jsx
      routes.jsx          ← product routes
  App.jsx                 ← combines all routes
```

```jsx
// features/dashboard/routes.jsx
import DashboardLayout from "./DashboardLayout";
import DashboardHome from "./DashboardHome";
import Profile from "./Profile";
import Settings from "./Settings";
import ProtectedRoute from "../../components/ProtectedRoute";

export const dashboardRoutes = {
  path: "dashboard",
  element: (
    <ProtectedRoute>
      <DashboardLayout />
    </ProtectedRoute>
  ),
  children: [
    { index: true, element: <DashboardHome /> },
    { path: "profile", element: <Profile /> },
    { path: "settings", element: <Settings /> },
  ],
};
```

```jsx
// App.jsx
import { useRoutes } from "react-router-dom";
import { dashboardRoutes } from "./features/dashboard/routes";
import { productRoutes } from "./features/products/routes";
import { authRoutes } from "./features/auth/routes";
import Layout from "./components/Layout";
import Home from "./pages/Home";
import NotFound from "./pages/NotFound";

const routes = [
  {
    path: "/",
    element: <Layout />,
    children: [
      { index: true, element: <Home /> },
      dashboardRoutes,
      productRoutes,
      ...authRoutes,
      { path: "*", element: <NotFound /> },
    ],
  },
];

function App() {
  return useRoutes(routes);
}
```

This pattern scales well because each feature owns its routes. Adding a new feature means creating a new routes file and adding one import.

---

## Lazy Loading Routes

For large applications, you do not want to load every page's JavaScript upfront. React's `lazy` function combined with `Suspense` lets you load route components on demand:

```jsx
import { lazy, Suspense } from "react";
import { Routes, Route } from "react-router-dom";

// These components are loaded only when their route is visited
const Dashboard = lazy(() => import("./pages/Dashboard"));
const Settings = lazy(() => import("./pages/Settings"));
const AdminPanel = lazy(() => import("./pages/AdminPanel"));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/admin" element={<AdminPanel />} />
      </Routes>
    </Suspense>
  );
}
```

When a user visits `/dashboard` for the first time, React loads the Dashboard component's JavaScript bundle, shows the `Suspense` fallback while loading, and then renders the component. Subsequent visits use the cached bundle.

This significantly improves initial load time for large applications because users only download the code they actually need.

---

## Mini Project: Blog Application

Let us build a complete blog application that demonstrates all the routing concepts covered in this chapter.

```jsx
// App.jsx
import { Routes, Route } from "react-router-dom";
import Layout from "./Layout";
import Home from "./Home";
import BlogList from "./BlogList";
import BlogPost from "./BlogPost";
import About from "./About";
import LoginPage from "./LoginPage";
import DashboardLayout from "./DashboardLayout";
import DashboardHome from "./DashboardHome";
import NewPost from "./NewPost";
import EditPost from "./EditPost";
import NotFound from "./NotFound";
import ProtectedRoute from "./ProtectedRoute";
import ScrollToTop from "./ScrollToTop";
import { AuthProvider } from "./AuthContext";

function App() {
  return (
    <AuthProvider>
      <ScrollToTop />
      <Routes>
        <Route path="/" element={<Layout />}>
          {/* Public routes */}
          <Route index element={<Home />} />
          <Route path="blog" element={<BlogList />} />
          <Route path="blog/:slug" element={<BlogPost />} />
          <Route path="about" element={<About />} />
          <Route path="login" element={<LoginPage />} />

          {/* Protected dashboard routes */}
          <Route
            path="dashboard"
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<DashboardHome />} />
            <Route path="new-post" element={<NewPost />} />
            <Route path="edit/:postId" element={<EditPost />} />
          </Route>

          {/* 404 */}
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </AuthProvider>
  );
}
```

```jsx
// Layout.jsx
import { Outlet, NavLink } from "react-router-dom";
import { useAuth } from "./AuthContext";

function Layout() {
  const { user, logout } = useAuth();

  return (
    <div>
      <header style={{ padding: "1rem", borderBottom: "1px solid #ddd" }}>
        <nav style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
          <NavLink to="/" style={linkStyle}>Home</NavLink>
          <NavLink to="/blog" style={linkStyle}>Blog</NavLink>
          <NavLink to="/about" style={linkStyle}>About</NavLink>

          <span style={{ marginLeft: "auto" }}>
            {user ? (
              <>
                <NavLink to="/dashboard" style={linkStyle}>Dashboard</NavLink>
                <button onClick={logout} style={{ marginLeft: "1rem" }}>
                  Logout
                </button>
              </>
            ) : (
              <NavLink to="/login" style={linkStyle}>Login</NavLink>
            )}
          </span>
        </nav>
      </header>

      <main style={{ padding: "2rem", maxWidth: 800, margin: "0 auto" }}>
        <Outlet />
      </main>

      <footer style={{ padding: "1rem", borderTop: "1px solid #ddd", textAlign: "center" }}>
        <p>Blog App — Built with React Router</p>
      </footer>
    </div>
  );
}

function linkStyle({ isActive }) {
  return {
    fontWeight: isActive ? "bold" : "normal",
    textDecoration: "none",
    color: isActive ? "#333" : "#666",
  };
}
```

```jsx
// Home.jsx
import { Link } from "react-router-dom";

function Home() {
  return (
    <div>
      <h1>Welcome to the Blog</h1>
      <p>A simple blog application built with React and React Router.</p>
      <Link to="/blog">Read the latest posts</Link>
    </div>
  );
}
```

```jsx
// blogData.js — simulated blog data
let posts = [
  {
    id: 1,
    slug: "getting-started-with-react",
    title: "Getting Started with React",
    excerpt: "Learn the basics of React and build your first component.",
    content: "React is a JavaScript library for building user interfaces. It was created by Facebook and has become one of the most popular frontend frameworks...",
    author: "Jane Smith",
    date: "2025-01-15",
    tags: ["react", "javascript", "tutorial"],
  },
  {
    id: 2,
    slug: "understanding-hooks",
    title: "Understanding React Hooks",
    excerpt: "A deep dive into useState, useEffect, and custom hooks.",
    content: "Hooks were introduced in React 16.8 and fundamentally changed how we write React components. Instead of class components with lifecycle methods...",
    author: "Jane Smith",
    date: "2025-02-01",
    tags: ["react", "hooks", "tutorial"],
  },
  {
    id: 3,
    slug: "react-router-guide",
    title: "Complete Guide to React Router",
    excerpt: "Everything you need to know about routing in React applications.",
    content: "React Router is the standard routing library for React. It enables navigation between different views in your single-page application...",
    author: "John Doe",
    date: "2025-02-20",
    tags: ["react", "routing", "guide"],
  },
];

export function getAllPosts() {
  return posts;
}

export function getPostBySlug(slug) {
  return posts.find(p => p.slug === slug) || null;
}

export function getPostById(id) {
  return posts.find(p => p.id === id) || null;
}

export function createPost(postData) {
  const newPost = {
    id: posts.length + 1,
    slug: postData.title.toLowerCase().replace(/\s+/g, "-"),
    date: new Date().toISOString().split("T")[0],
    ...postData,
  };
  posts = [...posts, newPost];
  return newPost;
}

export function updatePost(id, updates) {
  posts = posts.map(p => (p.id === id ? { ...p, ...updates } : p));
  return getPostById(id);
}
```

```jsx
// BlogList.jsx
import { Link, useSearchParams } from "react-router-dom";
import { getAllPosts } from "./blogData";

function BlogList() {
  const [searchParams, setSearchParams] = useSearchParams();
  const tagFilter = searchParams.get("tag");

  const allPosts = getAllPosts();
  const posts = tagFilter
    ? allPosts.filter(post => post.tags.includes(tagFilter))
    : allPosts;

  const allTags = [...new Set(allPosts.flatMap(post => post.tags))];

  return (
    <div>
      <h2>Blog Posts</h2>

      <div style={{ marginBottom: "1rem" }}>
        <strong>Filter by tag: </strong>
        <button
          onClick={() => setSearchParams({})}
          style={{ fontWeight: !tagFilter ? "bold" : "normal" }}
        >
          All
        </button>
        {allTags.map(tag => (
          <button
            key={tag}
            onClick={() => setSearchParams({ tag })}
            style={{
              marginLeft: "0.5rem",
              fontWeight: tagFilter === tag ? "bold" : "normal",
            }}
          >
            {tag}
          </button>
        ))}
      </div>

      {tagFilter && (
        <p>
          Showing posts tagged with "{tagFilter}" ({posts.length} result
          {posts.length !== 1 ? "s" : ""})
        </p>
      )}

      {posts.length === 0 ? (
        <p>No posts found.</p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {posts.map(post => (
            <li
              key={post.id}
              style={{
                marginBottom: "1.5rem",
                padding: "1rem",
                border: "1px solid #eee",
                borderRadius: 4,
              }}
            >
              <Link to={`/blog/${post.slug}`}>
                <h3 style={{ margin: 0 }}>{post.title}</h3>
              </Link>
              <p style={{ color: "#666", fontSize: "0.9em" }}>
                {post.author} — {post.date}
              </p>
              <p>{post.excerpt}</p>
              <div>
                {post.tags.map(tag => (
                  <Link
                    key={tag}
                    to={`/blog?tag=${tag}`}
                    style={{
                      marginRight: "0.5rem",
                      fontSize: "0.8em",
                      color: "#0066cc",
                    }}
                  >
                    #{tag}
                  </Link>
                ))}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

```jsx
// BlogPost.jsx
import { useParams, Link } from "react-router-dom";
import { getPostBySlug } from "./blogData";

function BlogPost() {
  const { slug } = useParams();
  const post = getPostBySlug(slug);

  if (!post) {
    return (
      <div>
        <h2>Post Not Found</h2>
        <p>The blog post you are looking for does not exist.</p>
        <Link to="/blog">Back to all posts</Link>
      </div>
    );
  }

  return (
    <article>
      <Link to="/blog" style={{ fontSize: "0.9em" }}>
        ← Back to all posts
      </Link>

      <h1 style={{ marginTop: "1rem" }}>{post.title}</h1>
      <p style={{ color: "#666" }}>
        By {post.author} — {post.date}
      </p>

      <div style={{ marginBottom: "1rem" }}>
        {post.tags.map(tag => (
          <Link
            key={tag}
            to={`/blog?tag=${tag}`}
            style={{ marginRight: "0.5rem", fontSize: "0.85em" }}
          >
            #{tag}
          </Link>
        ))}
      </div>

      <div style={{ lineHeight: 1.8 }}>
        <p>{post.content}</p>
      </div>
    </article>
  );
}
```

```jsx
// DashboardLayout.jsx
import { Outlet, NavLink } from "react-router-dom";

function DashboardLayout() {
  return (
    <div>
      <h2>Dashboard</h2>
      <nav style={{ marginBottom: "1rem", display: "flex", gap: "1rem" }}>
        <NavLink to="/dashboard" end style={dashLinkStyle}>
          Overview
        </NavLink>
        <NavLink to="/dashboard/new-post" style={dashLinkStyle}>
          New Post
        </NavLink>
      </nav>
      <Outlet />
    </div>
  );
}

function dashLinkStyle({ isActive }) {
  return {
    padding: "0.5rem 1rem",
    backgroundColor: isActive ? "#333" : "#eee",
    color: isActive ? "#fff" : "#333",
    textDecoration: "none",
    borderRadius: 4,
  };
}
```

Note the `end` prop on the first `NavLink`. Without `end`, the `/dashboard` link would always be active because every dashboard URL starts with `/dashboard`. The `end` prop makes it active only when the path is exactly `/dashboard`.

```jsx
// DashboardHome.jsx
import { Link } from "react-router-dom";
import { getAllPosts } from "./blogData";
import { useAuth } from "./AuthContext";

function DashboardHome() {
  const { user } = useAuth();
  const posts = getAllPosts();

  return (
    <div>
      <p>Welcome back, {user.name}!</p>
      <h3>Your Posts ({posts.length})</h3>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th style={thStyle}>Title</th>
            <th style={thStyle}>Date</th>
            <th style={thStyle}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {posts.map(post => (
            <tr key={post.id}>
              <td style={tdStyle}>
                <Link to={`/blog/${post.slug}`}>{post.title}</Link>
              </td>
              <td style={tdStyle}>{post.date}</td>
              <td style={tdStyle}>
                <Link to={`/dashboard/edit/${post.id}`}>Edit</Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const thStyle = {
  textAlign: "left",
  padding: "0.5rem",
  borderBottom: "2px solid #ddd",
};

const tdStyle = {
  padding: "0.5rem",
  borderBottom: "1px solid #eee",
};
```

```jsx
// NewPost.jsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createPost } from "./blogData";
import { useAuth } from "./AuthContext";

function NewPost() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [form, setForm] = useState({
    title: "",
    excerpt: "",
    content: "",
    tags: "",
  });

  function handleChange(e) {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  }

  function handleSubmit(e) {
    e.preventDefault();

    const newPost = createPost({
      ...form,
      author: user.name,
      tags: form.tags
        .split(",")
        .map(tag => tag.trim().toLowerCase())
        .filter(Boolean),
    });

    navigate(`/blog/${newPost.slug}`);
  }

  return (
    <div>
      <h3>Create New Post</h3>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "1rem" }}>
          <label>
            Title
            <br />
            <input
              name="title"
              value={form.title}
              onChange={handleChange}
              style={{ width: "100%", padding: "0.5rem" }}
              required
            />
          </label>
        </div>

        <div style={{ marginBottom: "1rem" }}>
          <label>
            Excerpt
            <br />
            <input
              name="excerpt"
              value={form.excerpt}
              onChange={handleChange}
              style={{ width: "100%", padding: "0.5rem" }}
              required
            />
          </label>
        </div>

        <div style={{ marginBottom: "1rem" }}>
          <label>
            Content
            <br />
            <textarea
              name="content"
              value={form.content}
              onChange={handleChange}
              style={{ width: "100%", padding: "0.5rem", minHeight: 200 }}
              required
            />
          </label>
        </div>

        <div style={{ marginBottom: "1rem" }}>
          <label>
            Tags (comma-separated)
            <br />
            <input
              name="tags"
              value={form.tags}
              onChange={handleChange}
              placeholder="react, tutorial, hooks"
              style={{ width: "100%", padding: "0.5rem" }}
            />
          </label>
        </div>

        <button type="submit" style={{ padding: "0.5rem 1rem" }}>
          Publish Post
        </button>
      </form>
    </div>
  );
}
```

```jsx
// EditPost.jsx
import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getPostById, updatePost } from "./blogData";

function EditPost() {
  const { postId } = useParams();
  const navigate = useNavigate();
  const post = getPostById(Number(postId));

  const [form, setForm] = useState(() => {
    if (!post) return null;
    return {
      title: post.title,
      excerpt: post.excerpt,
      content: post.content,
      tags: post.tags.join(", "),
    };
  });

  if (!post || !form) {
    return (
      <div>
        <h3>Post Not Found</h3>
        <Link to="/dashboard">Back to Dashboard</Link>
      </div>
    );
  }

  function handleChange(e) {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  }

  function handleSubmit(e) {
    e.preventDefault();

    updatePost(post.id, {
      ...form,
      tags: form.tags
        .split(",")
        .map(tag => tag.trim().toLowerCase())
        .filter(Boolean),
    });

    navigate(`/blog/${post.slug}`);
  }

  return (
    <div>
      <h3>Edit Post</h3>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "1rem" }}>
          <label>
            Title
            <br />
            <input
              name="title"
              value={form.title}
              onChange={handleChange}
              style={{ width: "100%", padding: "0.5rem" }}
              required
            />
          </label>
        </div>

        <div style={{ marginBottom: "1rem" }}>
          <label>
            Excerpt
            <br />
            <input
              name="excerpt"
              value={form.excerpt}
              onChange={handleChange}
              style={{ width: "100%", padding: "0.5rem" }}
              required
            />
          </label>
        </div>

        <div style={{ marginBottom: "1rem" }}>
          <label>
            Content
            <br />
            <textarea
              name="content"
              value={form.content}
              onChange={handleChange}
              style={{ width: "100%", padding: "0.5rem", minHeight: 200 }}
              required
            />
          </label>
        </div>

        <div style={{ marginBottom: "1rem" }}>
          <label>
            Tags (comma-separated)
            <br />
            <input
              name="tags"
              value={form.tags}
              onChange={handleChange}
              style={{ width: "100%", padding: "0.5rem" }}
            />
          </label>
        </div>

        <button type="submit" style={{ padding: "0.5rem 1rem" }}>
          Save Changes
        </button>
        <button
          type="button"
          onClick={() => navigate("/dashboard")}
          style={{ marginLeft: "0.5rem", padding: "0.5rem 1rem" }}
        >
          Cancel
        </button>
      </form>
    </div>
  );
}
```

```jsx
// ScrollToTop.jsx
import { useEffect } from "react";
import { useLocation } from "react-router-dom";

function ScrollToTop() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return null;
}
```

```jsx
// NotFound.jsx
import { Link } from "react-router-dom";

function NotFound() {
  return (
    <div style={{ textAlign: "center", padding: "2rem" }}>
      <h1>404</h1>
      <h2>Page Not Found</h2>
      <p>The page you are looking for does not exist.</p>
      <Link to="/">Go back to Home</Link>
    </div>
  );
}
```

This mini project demonstrates:

- **BrowserRouter** for enabling routing
- **Routes and Route** for defining URL-to-component mappings
- **Link and NavLink** for navigation with active styling
- **Route parameters** (`:slug`, `:postId`) for dynamic pages
- **Query strings** (`?tag=react`) for filtering
- **Nested routes** with layouts and Outlet
- **Protected routes** with auth context and redirect
- **Programmatic navigation** after form submission
- **useLocation** for scroll-to-top
- **Catch-all route** for 404 pages

---

## Common Mistakes

### Mistake 1: Using Anchor Tags Instead of Link

```jsx
// WRONG — causes full page reload
<a href="/about">About</a>

// CORRECT — client-side navigation
<Link to="/about">About</Link>
```

Regular `<a>` tags send a request to the server and reload the entire page. `Link` prevents this and uses the History API for instant navigation.

### Mistake 2: Forgetting the Outlet in Layout Routes

```jsx
// WRONG — child routes will not render
function Layout() {
  return (
    <div>
      <nav>{/* navigation */}</nav>
      {/* Missing <Outlet /> — child routes render nowhere */}
    </div>
  );
}

// CORRECT
function Layout() {
  return (
    <div>
      <nav>{/* navigation */}</nav>
      <Outlet /> {/* Child routes render here */}
    </div>
  );
}
```

### Mistake 3: Hardcoding URLs Instead of Using Parameters

```jsx
// WRONG — brittle and not reusable
<Link to="/users/42/posts/15">View Post</Link>

// CORRECT — dynamic based on data
<Link to={`/users/${user.id}/posts/${post.id}`}>View Post</Link>
```

### Mistake 4: Not Handling Loading States for Route Parameters

```jsx
// WRONG — assumes data is available immediately
function UserProfile() {
  const { userId } = useParams();
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetch(`/api/users/${userId}`).then(r => r.json()).then(setUser);
  }, [userId]);

  // Crashes if user is null
  return <h2>{user.name}</h2>;
}

// CORRECT — handle loading and error states
function UserProfile() {
  const { userId } = useParams();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetch(`/api/users/${userId}`)
      .then(r => r.json())
      .then(data => {
        setUser(data);
        setLoading(false);
      });
  }, [userId]);

  if (loading) return <p>Loading...</p>;
  if (!user) return <p>User not found.</p>;

  return <h2>{user.name}</h2>;
}
```

### Mistake 5: Not Using the end Prop on NavLink

```jsx
// WRONG — Home link is always active because "/" matches every path
<NavLink to="/">Home</NavLink>
<NavLink to="/about">About</NavLink>

// CORRECT — Home link is active only on exact match
<NavLink to="/" end>Home</NavLink>
<NavLink to="/about">About</NavLink>
```

---

## Best Practices

1. **Use NavLink for navigation menus** — It automatically handles active state styling, saving you from manually tracking the current route.

2. **Use `replace: true` after login** — After successful authentication, use `navigate(destination, { replace: true })` so users do not land back on the login page when pressing the back button.

3. **Scroll to top on navigation** — React Router does not do this automatically. Add a `ScrollToTop` component that reacts to `pathname` changes.

4. **Handle 404 at every nesting level** — Add a `path="*"` catch-all inside each `Routes` block, not just at the top level.

5. **Keep route definitions readable** — As your app grows, use route configuration arrays or feature-based route files instead of one giant JSX tree.

6. **Lazy load heavy routes** — Use `React.lazy` and `Suspense` for routes that are rarely visited or load large dependencies.

7. **Protect routes at the route level, not inside components** — Wrapping the route element with `ProtectedRoute` is cleaner than putting auth checks inside every protected component.

8. **Use route parameters for identity, query strings for filters** — `/products/42` identifies a product; `/products?sort=price&category=books` filters the list.

---

## Summary

In this chapter, you learned:

- **Client-side routing** keeps the URL in sync with the UI without page reloads
- **BrowserRouter** wraps your app to enable routing
- **Routes and Route** map URL paths to React components
- **Link and NavLink** provide navigation without page reloads, with NavLink adding active state
- **useParams** reads dynamic segments from the URL (route parameters)
- **useSearchParams** reads and writes query strings for filtering and search
- **Nested routes with Outlet** create shared layouts that persist across pages
- **useNavigate** enables programmatic navigation (after form submission, login, etc.)
- **useLocation** provides the current URL information for analytics, scroll management, and more
- **Protected routes** check authentication and redirect to login, preserving the intended destination
- **Catch-all routes** (`path="*"`) handle 404 pages
- **Lazy loading** with `React.lazy` and `Suspense` improves initial load performance

---

## Interview Questions

1. **What is the difference between server-side routing and client-side routing?**

   Server-side routing sends a new HTTP request to the server for every page navigation, and the server returns a complete HTML page. Client-side routing uses JavaScript to intercept navigation, update the URL using the History API, and render the appropriate component — all without a server request or page reload. Client-side routing provides a faster, more app-like experience.

2. **Why should you use Link instead of anchor tags in a React Router application?**

   Regular `<a>` tags trigger a full page reload — the browser sends a request to the server and replaces the entire page. `Link` prevents this default behavior and instead uses the History API to update the URL, then React renders the appropriate component. This preserves application state, avoids unnecessary network requests, and provides instant navigation.

3. **What is the difference between Link and NavLink?**

   `NavLink` is an extended version of `Link` that knows whether its `to` path matches the current URL. It accepts `className` and `style` as functions that receive `{ isActive }`, letting you style the active link differently. It also adds an `active` class by default. Use `NavLink` for navigation menus and `Link` for general-purpose links.

4. **Explain nested routes and the Outlet component.**

   Nested routes define a parent-child relationship between routes. The parent route renders a layout component, and the `Outlet` component inside that layout acts as a placeholder where the matched child route renders. This pattern lets you create persistent layouts (navigation bars, sidebars) that wrap multiple pages without remounting on navigation. You can nest routes multiple levels deep, each with its own `Outlet`.

5. **How do you implement protected routes in React Router?**

   Create a `ProtectedRoute` component that checks authentication status (typically from a Context). If the user is authenticated, render the children. If not, render `<Navigate to="/login" state={{ from: location }} replace />`. The `state` preserves where the user was trying to go, and `replace` prevents the protected URL from appearing in browser history. After login, use `navigate(from, { replace: true })` to redirect back.

6. **What is the difference between route parameters and query strings? When would you use each?**

   Route parameters (`:id` in `/users/:id`) are part of the URL path and identify a specific resource. They are required — the route will not match without them. Query strings (`?sort=price&page=2`) are optional key-value pairs that modify how data is displayed — sorting, filtering, pagination, search terms. Use route parameters when the value is essential to identify what to show, and query strings when the value modifies how to show it.

---

## Practice Exercises

### Exercise 1: E-Commerce Store Routes

Build the routing structure for an e-commerce store with the following pages: Home, Product List (with category filter via query string), Product Detail, Shopping Cart, Checkout (protected), Order Confirmation (protected), and User Account (protected with nested routes for Profile, Orders, and Addresses). Include a 404 page and proper navigation with active link highlighting.

### Exercise 2: Multi-Level Dashboard

Create a dashboard with three levels of nesting. The top level has a sidebar with links to Users, Products, and Analytics. Each of those sections has its own sub-navigation. For example, Users has List, Create New, and Roles. Products has Inventory, Categories, and Reviews. Each sub-page should render inside the correct layout. Use the `end` prop appropriately on NavLinks.

### Exercise 3: Search with URL State

Build a search page where the search query, selected filters (category, price range, sort order), and current page number are all stored in the URL as query parameters. When the user shares the URL, the recipient should see the same search results with the same filters applied. Implement a "Clear All Filters" button that resets the query string.

### Exercise 4: Authentication Flow

Build a complete authentication flow with Login, Register, and Forgot Password pages. After login, redirect users to where they were trying to go (or to the dashboard if they navigated to login directly). Add a "Remember Me" checkbox that persists the session in localStorage. Implement a logout button that clears auth state and redirects to the home page.

---

## What Is Next?

In Chapter 16, we will explore **API Integration and Data Fetching Patterns** — how to properly fetch data from APIs, handle loading and error states, implement caching strategies, work with pagination, and build reusable data fetching hooks for real-world applications.
