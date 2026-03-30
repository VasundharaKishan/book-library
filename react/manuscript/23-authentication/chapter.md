# Chapter 23: Authentication Flow and Protected Routes

## Learning Goals

By the end of this chapter, you will be able to:

- Understand how authentication works in single-page applications
- Implement login and registration forms with validation
- Store and manage authentication tokens (JWT)
- Build an AuthContext that provides user data and auth functions to the entire app
- Create protected routes that redirect unauthenticated users
- Implement role-based access control (admin, user, editor)
- Handle token expiration and automatic refresh
- Build persistent sessions that survive page refresh
- Implement logout with proper cleanup
- Secure your React application against common auth vulnerabilities

---

## How Authentication Works in SPAs

In a traditional server-rendered application, the server manages sessions with cookies. Every request includes the session cookie, and the server checks it before sending back a page.

In a single-page application (SPA), authentication works differently:

1. **User submits credentials** (email and password) to the server
2. **Server validates credentials** and returns a **token** (usually a JWT)
3. **Client stores the token** (in memory, localStorage, or a cookie)
4. **Every subsequent API request** includes the token in the `Authorization` header
5. **Server verifies the token** before responding to protected API endpoints
6. **Client-side routing** checks the token's existence to show or hide protected pages

The token replaces the session. Instead of the server remembering who is logged in, the client sends proof of identity with every request.

### What Is a JWT?

A JSON Web Token (JWT) is a string with three parts separated by dots:

```
eyJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOjEsImVtYWlsIjoiYWxpY2VAZXhhbXBsZS5jb20iLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3MDk1MDAwMDB9.signature
```

- **Header** — Algorithm and token type
- **Payload** — User data (userId, email, role, expiration time)
- **Signature** — Ensures the token was not tampered with

The payload is Base64-encoded (not encrypted). Anyone can read it. The signature is what makes it secure — only the server can create a valid signature.

**Important:** Never store sensitive data (passwords, credit card numbers) in a JWT payload. The payload is readable by anyone.

### Access Tokens and Refresh Tokens

Most authentication systems use two tokens:

- **Access token** — Short-lived (15 minutes to 1 hour). Sent with every API request. If stolen, it expires quickly.
- **Refresh token** — Long-lived (days to weeks). Used only to get a new access token. Stored more securely.

When the access token expires, the client uses the refresh token to get a new access token without requiring the user to log in again.

---

## Building the Authentication System

### The Auth Context

The AuthContext is the central piece. It holds the current user, provides login/logout functions, and manages token storage.

```jsx
// contexts/AuthContext.jsx
import { createContext, useContext, useState, useEffect, useCallback } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [loading, setLoading] = useState(true);

  // On mount, if we have a token, validate it and load the user
  useEffect(() => {
    async function loadUser() {
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const response = await fetch("/api/auth/me", {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!response.ok) {
          throw new Error("Token invalid");
        }

        const userData = await response.json();
        setUser(userData);
      } catch (err) {
        // Token is invalid or expired — clear it
        localStorage.removeItem("token");
        setToken(null);
        setUser(null);
      } finally {
        setLoading(false);
      }
    }

    loadUser();
  }, [token]);

  const login = useCallback(async (email, password) => {
    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || "Login failed");
    }

    const data = await response.json();
    localStorage.setItem("token", data.token);
    setToken(data.token);
    setUser(data.user);

    return data.user;
  }, []);

  const register = useCallback(async (userData) => {
    const response = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || "Registration failed");
    }

    const data = await response.json();
    localStorage.setItem("token", data.token);
    setToken(data.token);
    setUser(data.user);

    return data.user;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
  }, []);

  const value = {
    user,
    token,
    loading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
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

Key design decisions:

- **Loading state** — While validating the token on mount, `loading` is true. This prevents a flash of the login page before the user data loads.
- **Token in localStorage** — Persists across page refreshes and browser restarts.
- **Validate on mount** — The `/api/auth/me` endpoint verifies the token and returns the current user. This catches expired tokens.
- **useCallback** — Memoized functions prevent unnecessary re-renders in consumers.

### The Login Page

```jsx
// pages/LoginPage.jsx
import { useState } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Where to redirect after login
  const from = location.state?.from?.pathname || "/dashboard";

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div style={{ maxWidth: 400, margin: "4rem auto", padding: "0 1rem" }}>
      <h1>Log In</h1>

      {location.state?.message && (
        <p style={{ color: "#059669", marginBottom: "1rem" }}>
          {location.state.message}
        </p>
      )}

      {error && (
        <div
          role="alert"
          style={{
            padding: "0.75rem",
            backgroundColor: "#fef2f2",
            color: "#dc2626",
            borderRadius: 4,
            marginBottom: "1rem",
          }}
        >
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={submitting}
            autoComplete="email"
            style={{ display: "block", width: "100%", padding: "0.5rem" }}
          />
        </div>

        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={submitting}
            autoComplete="current-password"
            style={{ display: "block", width: "100%", padding: "0.5rem" }}
          />
        </div>

        <button
          type="submit"
          disabled={submitting}
          style={{
            width: "100%",
            padding: "0.75rem",
            backgroundColor: "#3b82f6",
            color: "white",
            border: "none",
            borderRadius: 4,
            cursor: submitting ? "not-allowed" : "pointer",
          }}
        >
          {submitting ? "Logging in..." : "Log In"}
        </button>
      </form>

      <p style={{ marginTop: "1rem", textAlign: "center" }}>
        Don't have an account? <Link to="/register">Sign up</Link>
      </p>
    </div>
  );
}
```

Important details:

- **`location.state?.from`** — If the user was redirected from a protected route, this contains where they were trying to go. After login, we send them there.
- **`replace: true`** — Replaces the login page in browser history. The user cannot press "back" to return to the login form.
- **`autoComplete`** — Tells the browser to offer saved credentials. Use `"email"`, `"current-password"`, and `"new-password"` for proper autofill behavior.
- **`location.state?.message`** — Shows a message like "Please log in to continue" when redirected from a protected route.

### The Registration Page

```jsx
// pages/RegisterPage.jsx
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

function RegisterPage() {
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: null }));
    }
  }

  function validate() {
    const newErrors = {};

    if (!form.name.trim()) {
      newErrors.name = "Name is required";
    }

    if (!form.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(form.email)) {
      newErrors.email = "Enter a valid email address";
    }

    if (!form.password) {
      newErrors.password = "Password is required";
    } else if (form.password.length < 8) {
      newErrors.password = "Password must be at least 8 characters";
    }

    if (form.password !== form.confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match";
    }

    return newErrors;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setServerError(null);

    const newErrors = validate();
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setSubmitting(true);

    try {
      await register({
        name: form.name,
        email: form.email,
        password: form.password,
      });
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setServerError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div style={{ maxWidth: 400, margin: "4rem auto", padding: "0 1rem" }}>
      <h1>Create Account</h1>

      {serverError && (
        <div role="alert" style={{ padding: "0.75rem", backgroundColor: "#fef2f2", color: "#dc2626", borderRadius: 4, marginBottom: "1rem" }}>
          {serverError}
        </div>
      )}

      <form onSubmit={handleSubmit} noValidate>
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="name">Full Name</label>
          <input
            id="name"
            name="name"
            value={form.name}
            onChange={handleChange}
            disabled={submitting}
            autoComplete="name"
            style={{ display: "block", width: "100%", padding: "0.5rem" }}
          />
          {errors.name && <p style={{ color: "red", fontSize: "0.85rem" }}>{errors.name}</p>}
        </div>

        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="reg-email">Email</label>
          <input
            id="reg-email"
            name="email"
            type="email"
            value={form.email}
            onChange={handleChange}
            disabled={submitting}
            autoComplete="email"
            style={{ display: "block", width: "100%", padding: "0.5rem" }}
          />
          {errors.email && <p style={{ color: "red", fontSize: "0.85rem" }}>{errors.email}</p>}
        </div>

        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="reg-password">Password</label>
          <input
            id="reg-password"
            name="password"
            type="password"
            value={form.password}
            onChange={handleChange}
            disabled={submitting}
            autoComplete="new-password"
            style={{ display: "block", width: "100%", padding: "0.5rem" }}
          />
          {errors.password && <p style={{ color: "red", fontSize: "0.85rem" }}>{errors.password}</p>}
        </div>

        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="confirm-password">Confirm Password</label>
          <input
            id="confirm-password"
            name="confirmPassword"
            type="password"
            value={form.confirmPassword}
            onChange={handleChange}
            disabled={submitting}
            autoComplete="new-password"
            style={{ display: "block", width: "100%", padding: "0.5rem" }}
          />
          {errors.confirmPassword && <p style={{ color: "red", fontSize: "0.85rem" }}>{errors.confirmPassword}</p>}
        </div>

        <button
          type="submit"
          disabled={submitting}
          style={{
            width: "100%",
            padding: "0.75rem",
            backgroundColor: "#3b82f6",
            color: "white",
            border: "none",
            borderRadius: 4,
            cursor: submitting ? "not-allowed" : "pointer",
          }}
        >
          {submitting ? "Creating account..." : "Create Account"}
        </button>
      </form>

      <p style={{ marginTop: "1rem", textAlign: "center" }}>
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </div>
  );
}
```

---

## Protected Routes

Protected routes check if the user is authenticated before rendering the page. If not, they redirect to the login page.

### The ProtectedRoute Component

```jsx
// components/ProtectedRoute.jsx
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

function ProtectedRoute({ children, requiredRole }) {
  const { user, isAuthenticated, loading } = useAuth();
  const location = useLocation();

  // While checking auth status, show nothing (or a loading spinner)
  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "50vh" }}>
        <p>Loading...</p>
      </div>
    );
  }

  // Not authenticated — redirect to login
  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        state={{
          from: location,
          message: "Please log in to access this page.",
        }}
        replace
      />
    );
  }

  // Authenticated but wrong role — redirect to unauthorized page
  if (requiredRole && user.role !== requiredRole) {
    return <Navigate to="/unauthorized" replace />;
  }

  // Authenticated and authorized — render the page
  return children;
}
```

The `loading` check is critical. Without it, the app briefly shows the login page on refresh while the token is being validated, then redirects to the dashboard — a jarring flash.

### Setting Up Routes

```jsx
// App.jsx
import { Routes, Route } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import ProfilePage from "./pages/ProfilePage";
import AdminPage from "./pages/AdminPage";
import UnauthorizedPage from "./pages/UnauthorizedPage";
import NotFoundPage from "./pages/NotFoundPage";

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<Layout />}>
          {/* Public routes */}
          <Route index element={<HomePage />} />
          <Route path="login" element={<LoginPage />} />
          <Route path="register" element={<RegisterPage />} />
          <Route path="unauthorized" element={<UnauthorizedPage />} />

          {/* Protected routes — any authenticated user */}
          <Route
            path="dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="profile"
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            }
          />

          {/* Protected routes — admin only */}
          <Route
            path="admin"
            element={
              <ProtectedRoute requiredRole="admin">
                <AdminPage />
              </ProtectedRoute>
            }
          />

          {/* 404 */}
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </AuthProvider>
  );
}
```

### The Layout with Auth-Aware Navigation

```jsx
// components/Layout.jsx
import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

function Layout() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/", { replace: true });
  }

  return (
    <div>
      <header style={{ padding: "1rem", borderBottom: "1px solid #e5e7eb" }}>
        <nav style={{ display: "flex", alignItems: "center", gap: "1rem", maxWidth: 1200, margin: "0 auto" }}>
          <NavLink to="/" style={{ fontWeight: "bold", fontSize: "1.2rem", textDecoration: "none", color: "#333" }}>
            MyApp
          </NavLink>

          <div style={{ flex: 1 }} />

          {isAuthenticated ? (
            <>
              <NavLink to="/dashboard">Dashboard</NavLink>
              <NavLink to="/profile">Profile</NavLink>
              {user.role === "admin" && (
                <NavLink to="/admin">Admin</NavLink>
              )}
              <span style={{ color: "#666" }}>Hi, {user.name}</span>
              <button
                onClick={handleLogout}
                style={{
                  padding: "0.375rem 0.75rem",
                  backgroundColor: "transparent",
                  border: "1px solid #d1d5db",
                  borderRadius: 4,
                  cursor: "pointer",
                }}
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login">Log In</NavLink>
              <NavLink
                to="/register"
                style={{
                  padding: "0.375rem 0.75rem",
                  backgroundColor: "#3b82f6",
                  color: "white",
                  borderRadius: 4,
                  textDecoration: "none",
                }}
              >
                Sign Up
              </NavLink>
            </>
          )}
        </nav>
      </header>

      <main style={{ maxWidth: 1200, margin: "0 auto", padding: "2rem 1rem" }}>
        <Outlet />
      </main>
    </div>
  );
}
```

The navigation adapts based on authentication state:

- **Not logged in** — Shows Login and Sign Up links
- **Logged in** — Shows Dashboard, Profile, user name, and Logout button
- **Admin user** — Additionally shows the Admin link

### Redirect Authenticated Users Away from Login

Authenticated users should not see the login page. Redirect them to the dashboard:

```jsx
// pages/LoginPage.jsx — add at the top of the component
function LoginPage() {
  const { isAuthenticated, loading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // If already logged in, redirect to dashboard
  useEffect(() => {
    if (!loading && isAuthenticated) {
      navigate("/dashboard", { replace: true });
    }
  }, [isAuthenticated, loading, navigate]);

  if (loading || isAuthenticated) return null;

  // ... rest of the component
}
```

---

## Token Management

### Authenticated API Requests

Create a utility that automatically adds the token to every request:

```jsx
// utils/api.js
export async function authFetch(url, options = {}) {
  const token = localStorage.getItem("token");

  const config = {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
      ...(token && { Authorization: `Bearer ${token}` }),
    },
  };

  const response = await fetch(url, config);

  // If the server returns 401, the token is invalid or expired
  if (response.status === 401) {
    localStorage.removeItem("token");
    window.location.href = "/login";
    throw new Error("Session expired. Please log in again.");
  }

  return response;
}

// Usage
const response = await authFetch("/api/profile");
const profile = await response.json();
```

### Token Expiration and Refresh

A robust auth system refreshes expired tokens automatically:

```jsx
// contexts/AuthContext.jsx — enhanced with token refresh
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [refreshToken, setRefreshToken] = useState(
    () => localStorage.getItem("refreshToken")
  );
  const [loading, setLoading] = useState(true);

  // Check if token is expired by decoding the JWT payload
  function isTokenExpired(jwt) {
    try {
      const payload = JSON.parse(atob(jwt.split(".")[1]));
      // exp is in seconds, Date.now() is in milliseconds
      return payload.exp * 1000 < Date.now();
    } catch {
      return true;
    }
  }

  // Refresh the access token using the refresh token
  async function refreshAccessToken() {
    if (!refreshToken) {
      throw new Error("No refresh token");
    }

    const response = await fetch("/api/auth/refresh", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refreshToken }),
    });

    if (!response.ok) {
      throw new Error("Refresh failed");
    }

    const data = await response.json();

    localStorage.setItem("token", data.token);
    localStorage.setItem("refreshToken", data.refreshToken);
    setToken(data.token);
    setRefreshToken(data.refreshToken);

    return data.token;
  }

  // Get a valid token — refresh if expired
  const getValidToken = useCallback(async () => {
    if (!token) return null;

    if (!isTokenExpired(token)) {
      return token;
    }

    // Token expired — try to refresh
    try {
      return await refreshAccessToken();
    } catch {
      // Refresh failed — clear everything
      logout();
      return null;
    }
  }, [token, refreshToken]);

  const login = useCallback(async (email, password) => {
    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || "Login failed");
    }

    const data = await response.json();

    localStorage.setItem("token", data.token);
    localStorage.setItem("refreshToken", data.refreshToken);
    setToken(data.token);
    setRefreshToken(data.refreshToken);
    setUser(data.user);

    return data.user;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("refreshToken");
    setToken(null);
    setRefreshToken(null);
    setUser(null);
  }, []);

  // ... rest of provider

  const value = {
    user,
    token,
    loading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    getValidToken, // Components use this for authenticated API calls
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
```

### Using the Auth Token in Components

```jsx
function ProfilePage() {
  const { user, getValidToken, logout } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadProfile() {
      try {
        const token = await getValidToken();
        if (!token) return;

        const response = await fetch("/api/profile", {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!response.ok) throw new Error("Failed to load profile");

        const data = await response.json();
        setProfile(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    loadProfile();
  }, [getValidToken]);

  if (loading) return <p>Loading profile...</p>;

  return (
    <div>
      <h1>Profile</h1>
      <p>Name: {profile?.name}</p>
      <p>Email: {profile?.email}</p>
      <p>Role: {profile?.role}</p>
      <p>Member since: {new Date(profile?.createdAt).toLocaleDateString()}</p>
    </div>
  );
}
```

---

## Role-Based Access Control

### Multiple Role Levels

```jsx
// components/ProtectedRoute.jsx — enhanced with multiple roles
function ProtectedRoute({ children, allowedRoles }) {
  const { user, isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <div style={{ textAlign: "center", padding: "4rem" }}>Loading...</div>;
  }

  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        state={{ from: location, message: "Please log in to continue." }}
        replace
      />
    );
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
}
```

```jsx
// Usage with multiple roles
<Route
  path="dashboard"
  element={
    <ProtectedRoute allowedRoles={["user", "admin", "editor"]}>
      <DashboardPage />
    </ProtectedRoute>
  }
/>

<Route
  path="admin"
  element={
    <ProtectedRoute allowedRoles={["admin"]}>
      <AdminPage />
    </ProtectedRoute>
  }
/>

<Route
  path="editor"
  element={
    <ProtectedRoute allowedRoles={["admin", "editor"]}>
      <EditorPage />
    </ProtectedRoute>
  }
/>
```

### Conditional UI Based on Roles

```jsx
function DashboardPage() {
  const { user } = useAuth();

  return (
    <div>
      <h1>Dashboard</h1>

      {/* Everyone sees this */}
      <section>
        <h2>My Tasks</h2>
        <TaskList userId={user.id} />
      </section>

      {/* Only editors and admins see this */}
      {(user.role === "editor" || user.role === "admin") && (
        <section>
          <h2>Content Management</h2>
          <ContentEditor />
        </section>
      )}

      {/* Only admins see this */}
      {user.role === "admin" && (
        <section>
          <h2>User Management</h2>
          <UserManagement />
        </section>
      )}
    </div>
  );
}
```

### Permission-Based Access (Fine-Grained)

For complex applications, role-based access is too coarse. Use permissions instead:

```jsx
// The user object from the server includes permissions
const user = {
  id: 1,
  name: "Alice",
  role: "editor",
  permissions: ["posts:read", "posts:write", "posts:delete", "users:read"],
};

// A hook to check permissions
function usePermission(permission) {
  const { user } = useAuth();

  if (!user) return false;

  // Admin has all permissions
  if (user.role === "admin") return true;

  return user.permissions?.includes(permission) ?? false;
}

// Usage in components
function PostActions({ post }) {
  const canEdit = usePermission("posts:write");
  const canDelete = usePermission("posts:delete");

  return (
    <div>
      {canEdit && <button onClick={() => editPost(post.id)}>Edit</button>}
      {canDelete && <button onClick={() => deletePost(post.id)}>Delete</button>}
    </div>
  );
}

// Usage in routes
function PermissionRoute({ children, permission }) {
  const hasPermission = usePermission(permission);
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) return <p>Loading...</p>;
  if (!isAuthenticated) return <Navigate to="/login" state={{ from: location }} replace />;
  if (!hasPermission) return <Navigate to="/unauthorized" replace />;

  return children;
}

<Route
  path="posts/new"
  element={
    <PermissionRoute permission="posts:write">
      <CreatePostPage />
    </PermissionRoute>
  }
/>
```

---

## Security Considerations

### Where to Store Tokens

| Storage | Pros | Cons |
|---------|------|------|
| **localStorage** | Persists across tabs, simple API | Vulnerable to XSS attacks |
| **sessionStorage** | Cleared when tab closes | Lost on refresh in some cases, XSS vulnerable |
| **Memory (useState)** | Safest from XSS | Lost on refresh, must re-authenticate |
| **HttpOnly Cookie** | Not accessible by JS (XSS-proof) | Requires server configuration, CSRF protection needed |

**For most applications:** localStorage is practical and sufficient if you follow XSS prevention practices. For high-security applications (banking, healthcare), use HttpOnly cookies set by the server.

### Preventing XSS

Cross-Site Scripting (XSS) attacks inject malicious JavaScript that can steal tokens from localStorage. React helps prevent XSS by escaping values in JSX:

```jsx
// React automatically escapes this — safe from XSS
const userInput = '<script>steal(localStorage.token)</script>';
return <p>{userInput}</p>;
// Renders as text, not as a script tag
```

**Never use `dangerouslySetInnerHTML` with user input:**

```jsx
// DANGEROUS — never do this with untrusted content
<div dangerouslySetInnerHTML={{ __html: userContent }} />
```

### Validating Tokens on the Server

**Important:** Client-side route protection is a UX feature, not a security feature. It prevents authenticated users from seeing pages they should not see, but it does not protect data. A malicious user can bypass client-side checks by opening the browser console.

**All real security must happen on the server.** Every API endpoint must validate the token and check permissions before returning data:

```
Client-side protection = UX (nice for the user)
Server-side protection = Security (prevents actual data access)
```

### Logout Cleanup

A proper logout should:

1. Clear the token from storage
2. Clear user data from state
3. Optionally invalidate the token on the server (revoke it)
4. Clear any cached data that might contain sensitive information
5. Redirect to a public page

```jsx
const logout = useCallback(async () => {
  // Optionally tell the server to invalidate the token
  try {
    const currentToken = localStorage.getItem("token");
    if (currentToken) {
      await fetch("/api/auth/logout", {
        method: "POST",
        headers: { Authorization: `Bearer ${currentToken}` },
      });
    }
  } catch {
    // Ignore errors — we are logging out anyway
  }

  // Clear all auth data
  localStorage.removeItem("token");
  localStorage.removeItem("refreshToken");
  setToken(null);
  setRefreshToken(null);
  setUser(null);

  // Clear any cached sensitive data
  // queryClient.clear() if using TanStack Query
}, []);
```

---

## Mini Project: Complete Auth System

Let us build a complete authentication system with all the patterns covered in this chapter. This project uses a simulated API to demonstrate the full flow.

```jsx
// api/authApi.js — simulated auth API
const USERS_KEY = "auth_demo_users";
const TOKEN_SECRET = "demo-secret";

// Simulated user database in localStorage
function getUsers() {
  const stored = localStorage.getItem(USERS_KEY);
  return stored ? JSON.parse(stored) : [];
}

function saveUsers(users) {
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
}

// Simple token generation (in production, this happens on the server)
function createToken(user) {
  const payload = {
    userId: user.id,
    email: user.email,
    role: user.role,
    exp: Math.floor(Date.now() / 1000) + 3600, // 1 hour
  };
  // This is NOT secure — real tokens are signed by the server
  return btoa(JSON.stringify({ alg: "none" })) +
    "." + btoa(JSON.stringify(payload)) +
    "." + btoa("demo-signature");
}

function decodeToken(token) {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    if (payload.exp * 1000 < Date.now()) {
      return null; // Expired
    }
    return payload;
  } catch {
    return null;
  }
}

// Simulate API delay
function delay(ms = 500) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export const authApi = {
  async register({ name, email, password }) {
    await delay();
    const users = getUsers();

    if (users.find((u) => u.email === email)) {
      throw new Error("An account with this email already exists");
    }

    const user = {
      id: Date.now(),
      name,
      email,
      role: users.length === 0 ? "admin" : "user", // First user is admin
      createdAt: new Date().toISOString(),
    };

    // In production, password is hashed on the server
    users.push({ ...user, password });
    saveUsers(users);

    const token = createToken(user);
    return { user, token };
  },

  async login(email, password) {
    await delay();
    const users = getUsers();
    const user = users.find((u) => u.email === email && u.password === password);

    if (!user) {
      throw new Error("Invalid email or password");
    }

    const { password: _, ...userWithoutPassword } = user;
    const token = createToken(userWithoutPassword);
    return { user: userWithoutPassword, token };
  },

  async getMe(token) {
    await delay(200);
    const payload = decodeToken(token);

    if (!payload) {
      throw new Error("Invalid or expired token");
    }

    const users = getUsers();
    const user = users.find((u) => u.id === payload.userId);

    if (!user) {
      throw new Error("User not found");
    }

    const { password: _, ...userWithoutPassword } = user;
    return userWithoutPassword;
  },

  async updateProfile(token, updates) {
    await delay();
    const payload = decodeToken(token);
    if (!payload) throw new Error("Invalid token");

    const users = getUsers();
    const index = users.findIndex((u) => u.id === payload.userId);
    if (index === -1) throw new Error("User not found");

    users[index] = { ...users[index], ...updates };
    saveUsers(users);

    const { password: _, ...userWithoutPassword } = users[index];
    return userWithoutPassword;
  },

  async getAllUsers(token) {
    await delay();
    const payload = decodeToken(token);
    if (!payload) throw new Error("Invalid token");
    if (payload.role !== "admin") throw new Error("Unauthorized");

    return getUsers().map(({ password: _, ...user }) => user);
  },
};
```

```jsx
// contexts/AuthContext.jsx — using the simulated API
import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { authApi } from "../api/authApi";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadUser() {
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const userData = await authApi.getMe(token);
        setUser(userData);
      } catch {
        localStorage.removeItem("token");
        setToken(null);
        setUser(null);
      } finally {
        setLoading(false);
      }
    }

    loadUser();
  }, [token]);

  const login = useCallback(async (email, password) => {
    const data = await authApi.login(email, password);
    localStorage.setItem("token", data.token);
    setToken(data.token);
    setUser(data.user);
    return data.user;
  }, []);

  const register = useCallback(async (userData) => {
    const data = await authApi.register(userData);
    localStorage.setItem("token", data.token);
    setToken(data.token);
    setUser(data.user);
    return data.user;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
  }, []);

  const updateProfile = useCallback(async (updates) => {
    if (!token) throw new Error("Not authenticated");
    const updatedUser = await authApi.updateProfile(token, updates);
    setUser(updatedUser);
    return updatedUser;
  }, [token]);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        updateProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}
```

```jsx
// pages/DashboardPage.jsx
import { useAuth } from "../contexts/AuthContext";

function DashboardPage() {
  const { user } = useAuth();

  return (
    <div>
      <h1>Dashboard</h1>
      <div style={{
        padding: "1.5rem",
        backgroundColor: "#f0fdf4",
        borderRadius: 8,
        border: "1px solid #bbf7d0",
        marginBottom: "1.5rem",
      }}>
        <h2 style={{ margin: "0 0 0.5rem" }}>Welcome back, {user.name}!</h2>
        <p style={{ margin: 0, color: "#166534" }}>
          You are logged in as <strong>{user.role}</strong>.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "1rem" }}>
        <DashboardCard title="Profile" description="View and edit your profile" link="/profile" />
        {user.role === "admin" && (
          <DashboardCard title="Admin Panel" description="Manage users and settings" link="/admin" />
        )}
      </div>
    </div>
  );
}

function DashboardCard({ title, description, link }) {
  return (
    <a
      href={link}
      style={{
        display: "block",
        padding: "1.5rem",
        backgroundColor: "white",
        borderRadius: 8,
        border: "1px solid #e5e7eb",
        textDecoration: "none",
        color: "inherit",
      }}
    >
      <h3 style={{ margin: "0 0 0.5rem" }}>{title}</h3>
      <p style={{ margin: 0, color: "#666" }}>{description}</p>
    </a>
  );
}
```

```jsx
// pages/ProfilePage.jsx
import { useState } from "react";
import { useAuth } from "../contexts/AuthContext";

function ProfilePage() {
  const { user, updateProfile } = useAuth();
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState(user.name);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);

  async function handleSave(e) {
    e.preventDefault();
    setSaving(true);
    setMessage(null);

    try {
      await updateProfile({ name });
      setEditing(false);
      setMessage({ type: "success", text: "Profile updated successfully" });
    } catch (err) {
      setMessage({ type: "error", text: err.message });
    } finally {
      setSaving(false);
    }
  }

  return (
    <div style={{ maxWidth: 600 }}>
      <h1>Profile</h1>

      {message && (
        <div
          role="status"
          style={{
            padding: "0.75rem",
            borderRadius: 4,
            marginBottom: "1rem",
            backgroundColor: message.type === "success" ? "#f0fdf4" : "#fef2f2",
            color: message.type === "success" ? "#166534" : "#dc2626",
          }}
        >
          {message.text}
        </div>
      )}

      <div style={{ backgroundColor: "white", padding: "1.5rem", borderRadius: 8, border: "1px solid #e5e7eb" }}>
        {editing ? (
          <form onSubmit={handleSave}>
            <div style={{ marginBottom: "1rem" }}>
              <label htmlFor="profile-name">Name</label>
              <input
                id="profile-name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={saving}
                style={{ display: "block", width: "100%", padding: "0.5rem" }}
              />
            </div>
            <div style={{ display: "flex", gap: "0.5rem" }}>
              <button type="submit" disabled={saving}>
                {saving ? "Saving..." : "Save"}
              </button>
              <button type="button" onClick={() => { setEditing(false); setName(user.name); }}>
                Cancel
              </button>
            </div>
          </form>
        ) : (
          <>
            <div style={{ marginBottom: "1rem" }}>
              <p style={{ color: "#666", fontSize: "0.85rem", margin: "0 0 0.25rem" }}>Name</p>
              <p style={{ margin: 0, fontWeight: 500 }}>{user.name}</p>
            </div>
            <div style={{ marginBottom: "1rem" }}>
              <p style={{ color: "#666", fontSize: "0.85rem", margin: "0 0 0.25rem" }}>Email</p>
              <p style={{ margin: 0 }}>{user.email}</p>
            </div>
            <div style={{ marginBottom: "1rem" }}>
              <p style={{ color: "#666", fontSize: "0.85rem", margin: "0 0 0.25rem" }}>Role</p>
              <p style={{ margin: 0, textTransform: "capitalize" }}>{user.role}</p>
            </div>
            <div style={{ marginBottom: "1rem" }}>
              <p style={{ color: "#666", fontSize: "0.85rem", margin: "0 0 0.25rem" }}>Member Since</p>
              <p style={{ margin: 0 }}>{new Date(user.createdAt).toLocaleDateString()}</p>
            </div>
            <button onClick={() => setEditing(true)}>Edit Profile</button>
          </>
        )}
      </div>
    </div>
  );
}
```

```jsx
// pages/AdminPage.jsx
import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { authApi } from "../api/authApi";

function AdminPage() {
  const { token } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadUsers() {
      try {
        const data = await authApi.getAllUsers(token);
        setUsers(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadUsers();
  }, [token]);

  if (loading) return <p>Loading users...</p>;
  if (error) return <p style={{ color: "red" }}>Error: {error}</p>;

  return (
    <div>
      <h1>Admin Panel</h1>
      <p style={{ color: "#666", marginBottom: "1.5rem" }}>
        Manage all registered users ({users.length} total)
      </p>

      <table style={{ width: "100%", borderCollapse: "collapse", backgroundColor: "white", borderRadius: 8, overflow: "hidden", border: "1px solid #e5e7eb" }}>
        <thead>
          <tr style={{ backgroundColor: "#f9fafb" }}>
            <th style={{ padding: "0.75rem 1rem", textAlign: "left" }}>Name</th>
            <th style={{ padding: "0.75rem 1rem", textAlign: "left" }}>Email</th>
            <th style={{ padding: "0.75rem 1rem", textAlign: "left" }}>Role</th>
            <th style={{ padding: "0.75rem 1rem", textAlign: "left" }}>Joined</th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id} style={{ borderTop: "1px solid #f3f4f6" }}>
              <td style={{ padding: "0.75rem 1rem" }}>{u.name}</td>
              <td style={{ padding: "0.75rem 1rem" }}>{u.email}</td>
              <td style={{ padding: "0.75rem 1rem" }}>
                <span style={{
                  padding: "0.125rem 0.5rem",
                  borderRadius: 12,
                  fontSize: "0.8rem",
                  backgroundColor: u.role === "admin" ? "#dbeafe" : "#f3f4f6",
                  color: u.role === "admin" ? "#1e40af" : "#374151",
                  textTransform: "capitalize",
                }}>
                  {u.role}
                </span>
              </td>
              <td style={{ padding: "0.75rem 1rem" }}>
                {new Date(u.createdAt).toLocaleDateString()}
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
// pages/UnauthorizedPage.jsx
import { Link } from "react-router-dom";

function UnauthorizedPage() {
  return (
    <div style={{ textAlign: "center", padding: "4rem 1rem" }}>
      <h1>403 — Unauthorized</h1>
      <p style={{ color: "#666", marginBottom: "1.5rem" }}>
        You do not have permission to access this page.
      </p>
      <Link to="/dashboard">Go to Dashboard</Link>
    </div>
  );
}
```

This mini project demonstrates:

- **Complete auth flow** — registration, login, token storage, session persistence
- **AuthContext** with loading state to prevent flash of login page
- **Protected routes** with role-based access control
- **Auth-aware navigation** that adapts to login state
- **Profile management** with authenticated API calls
- **Admin panel** restricted to admin users only
- **Redirect after login** to the originally requested page
- **Simulated API** for standalone demonstration

---

## Common Mistakes

### Mistake 1: Not Handling the Loading State

```jsx
// WRONG — flashes login page on refresh before token is validated
function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

// CORRECT — wait for token validation
function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) return <p>Loading...</p>;
  if (!isAuthenticated) return <Navigate to="/login" replace />;

  return children;
}
```

### Mistake 2: Storing Passwords in the Frontend

```jsx
// NEVER DO THIS
const [user, setUser] = useState({
  email: "alice@example.com",
  password: "secret123", // NEVER store passwords in state
});

// The server should NEVER return the password in API responses
// If it does, that is a server-side bug
```

### Mistake 3: Not Clearing Sensitive Data on Logout

```jsx
// WRONG — only clears token, leaves cached data
function logout() {
  localStorage.removeItem("token");
  setUser(null);
  // But cached API responses still contain user data!
}

// CORRECT — clear everything
function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("refreshToken");
  setUser(null);
  // Clear any query caches, Zustand stores, etc.
}
```

### Mistake 4: Relying Only on Client-Side Protection

```jsx
// Client-side protection is UX, not security
// A user can open DevTools and bypass any client-side check

// ALWAYS validate on the server:
// - Check the token on every API request
// - Verify the user has permission for the requested resource
// - Never trust data from the client
```

### Mistake 5: Not Handling Token Expiration

```jsx
// WRONG — assumes the token is always valid
async function fetchData() {
  const response = await fetch("/api/data", {
    headers: { Authorization: `Bearer ${token}` },
  });
  const data = await response.json(); // Might be a 401 error response!
  setData(data);
}

// CORRECT — handle 401 responses
async function fetchData() {
  const response = await fetch("/api/data", {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (response.status === 401) {
    // Token expired — try refresh or redirect to login
    logout();
    return;
  }

  if (!response.ok) throw new Error("Request failed");

  const data = await response.json();
  setData(data);
}
```

---

## Best Practices

1. **Always validate tokens on the server** — Client-side route protection is a UX feature, not a security feature. Every API endpoint must verify the token independently.

2. **Use a loading state during token validation** — Prevent the flash of the login page when a logged-in user refreshes. Show a loading indicator until the token is validated.

3. **Store the redirect destination** — When redirecting to login, pass `location.state.from` so you can redirect back after successful login. Use `replace: true` to keep browser history clean.

4. **Handle token expiration gracefully** — Implement token refresh for seamless session extension. When refresh fails, redirect to login with a clear message.

5. **Clear everything on logout** — Remove tokens, user data, cached API responses, and any sensitive data in stores or caches.

6. **Use HttpOnly cookies for high-security apps** — If your API supports it, HttpOnly cookies are safer than localStorage because JavaScript cannot access them, eliminating XSS token theft.

7. **Never store passwords on the client** — The server should never return passwords in API responses. If you see a password field in your frontend state, something is wrong.

8. **Add `autoComplete` to auth forms** — Use `autoComplete="email"`, `autoComplete="current-password"`, and `autoComplete="new-password"` to enable browser password managers.

---

## Summary

In this chapter, you learned:

- **SPA authentication** works with tokens (JWTs) instead of server sessions — the client stores the token and sends it with every API request
- **AuthContext** provides user data, login/logout functions, and a loading state to the entire application
- **Protected routes** check `isAuthenticated` and `loading` before rendering — redirecting to login when needed and preserving the intended destination
- **Role-based access control** restricts routes and UI elements based on the user's role using `allowedRoles` on ProtectedRoute
- **Permission-based access** provides fine-grained control with a `usePermission` hook
- **Token management** includes storage (localStorage), expiration checking (decoding JWT payload), and automatic refresh (using refresh tokens)
- **Security** requires server-side validation on every request — client-side checks are UX, not security
- **Logout** must clear all auth data: tokens, user state, and cached sensitive data
- **Login/Register forms** need proper validation, error handling, disabled states during submission, and `autoComplete` attributes

---

## Interview Questions

1. **How does authentication work in a React SPA?**

   The user submits credentials to the server, which validates them and returns a JWT (JSON Web Token). The client stores this token (typically in localStorage) and includes it in the `Authorization: Bearer <token>` header of every subsequent API request. The server verifies the token before responding. On the client side, an AuthContext manages the user state, and protected routes check authentication status before rendering pages.

2. **What is the difference between authentication and authorization?**

   Authentication verifies identity — "Who are you?" It confirms that the user is who they claim to be (typically via email/password and a token). Authorization determines permissions — "What are you allowed to do?" It checks whether an authenticated user has the right to access a specific resource or perform a specific action. A user can be authenticated (logged in) but not authorized (lacks the required role or permission) for certain pages or actions.

3. **Why is client-side route protection not sufficient for security?**

   Client-side code runs in the browser, which the user controls. Anyone can open DevTools, modify JavaScript, or call API endpoints directly. Client-side route protection only improves UX by hiding pages the user should not see — it cannot prevent access to data. All security must be enforced on the server: every API endpoint must validate the token, check the user's role/permissions, and only return data the user is authorized to see.

4. **How do you handle token expiration in a React application?**

   Use two tokens: a short-lived access token (sent with every request) and a long-lived refresh token (used to get new access tokens). Before making an API request, check if the access token is expired by decoding the JWT payload and comparing the `exp` field to the current time. If expired, use the refresh token to request a new access token from the server. If the refresh also fails, clear all auth data and redirect to login.

5. **What happens when a user refreshes the page in a React SPA with authentication?**

   On page load, the AuthProvider checks localStorage for a stored token. If found, it sends the token to a validation endpoint (e.g., `/api/auth/me`) to verify it is still valid and load the user data. While this validation is in progress, the `loading` state is `true` — ProtectedRoute components show a loading indicator instead of redirecting to login. This prevents the flash where a logged-in user briefly sees the login page before being redirected to their dashboard.

---

## Practice Exercises

### Exercise 1: Remember Me

Add a "Remember Me" checkbox to the login form. When checked, store the token in localStorage (persists across browser sessions). When unchecked, store the token in sessionStorage (cleared when the tab closes). Verify both behaviors work correctly.

### Exercise 2: Password Change

Add a "Change Password" form to the profile page. It should require the current password and a new password (with confirmation). Validate that the new password meets strength requirements and that the confirmation matches. Show appropriate success/error messages.

### Exercise 3: Session Timeout

Implement a session timeout that logs the user out after 30 minutes of inactivity. Show a warning modal 5 minutes before the timeout: "Your session will expire in 5 minutes. Click to continue." If the user interacts, reset the timer. If they do not, log them out automatically.

### Exercise 4: Social Login UI

Build the UI for social login (Google, GitHub). Add "Continue with Google" and "Continue with GitHub" buttons to the login and registration pages. These buttons do not need to connect to real OAuth providers — focus on the UI, the loading states, and how social auth integrates with your existing AuthContext.

---

## What Is Next?

In Chapter 24, we will explore **Deployment and Production Optimization** — how to build your React application for production, optimize bundle size, configure environment variables, deploy to popular hosting platforms, and handle SEO for single-page applications.
