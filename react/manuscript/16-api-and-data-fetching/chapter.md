# Chapter 16: API Integration and Data Fetching Patterns

## Learning Goals

By the end of this chapter, you will be able to:

- Understand how React applications communicate with APIs
- Fetch data with the Fetch API and handle all response states
- Build a reusable data fetching pattern with loading, error, and success states
- Implement POST, PUT, PATCH, and DELETE requests
- Handle race conditions with AbortController
- Build pagination (page-based and infinite scroll)
- Implement optimistic updates for instant UI feedback
- Cache API responses to avoid redundant network requests
- Create a reusable `useFetch` hook and an API service layer
- Handle authentication tokens in API requests
- Retry failed requests and implement error recovery

---

## How React Applications Talk to APIs

React is a frontend library — it renders UI in the browser. It does not have a built-in way to talk to a database or run server-side logic. Instead, React applications communicate with a backend server through HTTP requests, typically using a REST API or GraphQL endpoint.

The typical flow:

1. A React component needs data (e.g., a list of users)
2. The component sends an HTTP request to the server (`GET /api/users`)
3. The server processes the request, queries the database, and returns JSON
4. The component receives the JSON and stores it in state
5. React re-renders the component with the data

This chapter focuses on the client side of this flow — how to send requests, handle responses, and manage the data lifecycle in your React components.

---

## The Fetch API

Modern browsers provide the `fetch` function for making HTTP requests. It returns a Promise that resolves to a `Response` object.

### Basic GET Request

```jsx
fetch("https://api.example.com/users")
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error(error));
```

### Using async/await

```jsx
async function fetchUsers() {
  try {
    const response = await fetch("https://api.example.com/users");
    const data = await response.json();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}
```

### Important: fetch Does Not Throw on HTTP Errors

This is the most common source of bugs when using `fetch`. The `fetch` function only throws an error for network failures (no internet, DNS resolution failed, etc.). An HTTP error like 404 or 500 does **not** throw — it resolves normally with `response.ok` set to `false`.

```jsx
// WRONG — this does not catch 404 or 500 errors
try {
  const response = await fetch("/api/users");
  const data = await response.json(); // Might parse an error response
} catch (error) {
  // Only catches network failures, not HTTP errors
}

// CORRECT — explicitly check response.ok
try {
  const response = await fetch("/api/users");

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  const data = await response.json();
} catch (error) {
  // Now catches both network errors AND HTTP errors
}
```

You must always check `response.ok` (or `response.status`) before parsing the body. This is so important that we will build it into every pattern in this chapter.

---

## The Standard Data Fetching Pattern

Every component that fetches data needs to handle three states: loading, error, and success. Here is the pattern you will use throughout your React applications:

```jsx
import { useState, useEffect } from "react";

function UserList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchUsers() {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch("/api/users");

        if (!response.ok) {
          throw new Error(`Failed to fetch users (${response.status})`);
        }

        const data = await response.json();
        setUsers(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchUsers();
  }, []);

  if (loading) return <p>Loading users...</p>;
  if (error) return <p>Error: {error}</p>;
  if (users.length === 0) return <p>No users found.</p>;

  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

### Breaking Down the Pattern

**State declarations:**

- `users` — the fetched data, initialized to an empty array
- `loading` — whether a request is in progress, starts `true` because we fetch immediately
- `error` — any error message, starts `null`

**The effect:**

- Defines an async function inside the effect (effects cannot be async directly)
- Sets `loading(true)` and clears any previous error
- Checks `response.ok` before parsing
- Uses `try/catch/finally` to handle all outcomes
- `finally` ensures loading is set to `false` whether the request succeeds or fails

**The render:**

- Checks states in order: loading → error → empty → data
- Returns early for each state so the rendering logic stays flat and readable

### The Status Pattern (Alternative)

Instead of three separate state variables, you can use a single `status` variable:

```jsx
function UserList() {
  const [users, setUsers] = useState([]);
  const [status, setStatus] = useState("idle"); // idle | loading | error | success
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchUsers() {
      try {
        setStatus("loading");
        setError(null);

        const response = await fetch("/api/users");
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        setUsers(data);
        setStatus("success");
      } catch (err) {
        setError(err.message);
        setStatus("error");
      }
    }

    fetchUsers();
  }, []);

  if (status === "idle" || status === "loading") return <p>Loading...</p>;
  if (status === "error") return <p>Error: {error}</p>;
  if (users.length === 0) return <p>No users found.</p>;

  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

The status pattern is cleaner when you have complex state machines — it prevents impossible states like `{ loading: true, error: "something" }`.

---

## Fetching Data Based on Parameters

Often you need to fetch data based on a prop, route parameter, or user input. The key is adding the parameter to the dependency array:

```jsx
import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

function UserProfile() {
  const { userId } = useParams();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchUser() {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch(`/api/users/${userId}`);
        if (!response.ok) {
          if (response.status === 404) {
            throw new Error("User not found");
          }
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        setUser(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchUser();
  }, [userId]); // Re-fetch when userId changes

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;
  if (!user) return <p>User not found.</p>;

  return (
    <div>
      <h2>{user.name}</h2>
      <p>Email: {user.email}</p>
    </div>
  );
}
```

When the user navigates from `/users/1` to `/users/2`, `userId` changes, the effect runs again, and the component fetches the new user's data.

---

## Handling Race Conditions

Race conditions occur when multiple fetch requests are in flight and responses arrive out of order. This is a real problem when fetching based on changing parameters.

### The Problem

Imagine a user types "re" in a search box, then quickly changes it to "react":

1. Request 1 fires: `GET /search?q=re`
2. Request 2 fires: `GET /search?q=react`
3. Request 2 returns first (fast server response)
4. Request 1 returns second (slow server response)
5. The UI now shows results for "re" even though the search box says "react"

### Solution: AbortController

```jsx
function SearchResults({ query }) {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!query) {
      setResults([]);
      return;
    }

    const controller = new AbortController();

    async function search() {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`, {
          signal: controller.signal,
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        setResults(data);
      } catch (err) {
        if (err.name === "AbortError") {
          // Request was cancelled — ignore
          return;
        }
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    search();

    return () => controller.abort();
  }, [query]);

  // render...
}
```

How this works:

1. Each time `query` changes, the cleanup function from the previous effect runs
2. The cleanup calls `controller.abort()`, which cancels the previous request
3. The cancelled request throws an `AbortError`, which we ignore
4. Only the latest request's response updates state

This pattern is essential for any fetch that depends on rapidly changing values (search inputs, autocomplete, filters).

---

## Sending Data: POST, PUT, PATCH, DELETE

### POST — Creating a Resource

```jsx
async function createUser(userData) {
  const response = await fetch("/api/users", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(userData),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || "Failed to create user");
  }

  return response.json();
}
```

### Using POST in a Component

```jsx
function CreateUserForm() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    setSuccess(false);

    try {
      await createUser({ name, email });
      setSuccess(true);
      setName("");
      setEmail("");
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {success && <p style={{ color: "green" }}>User created!</p>}

      <input
        value={name}
        onChange={e => setName(e.target.value)}
        placeholder="Name"
        required
        disabled={submitting}
      />
      <input
        type="email"
        value={email}
        onChange={e => setEmail(e.target.value)}
        placeholder="Email"
        required
        disabled={submitting}
      />
      <button type="submit" disabled={submitting}>
        {submitting ? "Creating..." : "Create User"}
      </button>
    </form>
  );
}
```

### PUT — Replacing a Resource

```jsx
async function updateUser(userId, userData) {
  const response = await fetch(`/api/users/${userId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(userData),
  });

  if (!response.ok) {
    throw new Error("Failed to update user");
  }

  return response.json();
}
```

### PATCH — Partially Updating a Resource

```jsx
async function patchUser(userId, updates) {
  const response = await fetch(`/api/users/${userId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(updates), // Only the changed fields
  });

  if (!response.ok) {
    throw new Error("Failed to update user");
  }

  return response.json();
}

// Usage: only send what changed
await patchUser(42, { email: "new@email.com" });
```

### DELETE — Removing a Resource

```jsx
async function deleteUser(userId) {
  const response = await fetch(`/api/users/${userId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error("Failed to delete user");
  }

  // DELETE often returns 204 No Content — no body to parse
  return true;
}
```

### PUT vs PATCH

- **PUT** replaces the entire resource. You must send all fields, even unchanged ones. If you omit a field, it may be set to null.
- **PATCH** updates only the fields you send. Other fields remain unchanged.

In practice, most applications use PATCH for updates because it is more forgiving and sends less data.

---

## Building an API Service Layer

As your application grows, scattering `fetch` calls throughout components becomes messy. Instead, create a centralized API service:

```jsx
// api.js
const BASE_URL = "/api";

async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;

  const config = {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  };

  // Add auth token if available
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(url, config);

  if (response.status === 401) {
    // Token expired — redirect to login
    localStorage.removeItem("token");
    window.location.href = "/login";
    return;
  }

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    const error = new Error(errorBody.message || `HTTP ${response.status}`);
    error.status = response.status;
    error.data = errorBody;
    throw error;
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return null;
  }

  return response.json();
}

// Convenience methods
export const api = {
  get: (endpoint, options) =>
    request(endpoint, { ...options, method: "GET" }),

  post: (endpoint, data, options) =>
    request(endpoint, {
      ...options,
      method: "POST",
      body: JSON.stringify(data),
    }),

  put: (endpoint, data, options) =>
    request(endpoint, {
      ...options,
      method: "PUT",
      body: JSON.stringify(data),
    }),

  patch: (endpoint, data, options) =>
    request(endpoint, {
      ...options,
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  delete: (endpoint, options) =>
    request(endpoint, { ...options, method: "DELETE" }),
};
```

### Using the API Service

```jsx
// userService.js
import { api } from "./api";

export const userService = {
  getAll: () => api.get("/users"),
  getById: (id) => api.get(`/users/${id}`),
  create: (data) => api.post("/users", data),
  update: (id, data) => api.patch(`/users/${id}`, data),
  delete: (id) => api.delete(`/users/${id}`),
  search: (query) => api.get(`/users/search?q=${encodeURIComponent(query)}`),
};
```

```jsx
// In a component
import { userService } from "./userService";

function UserList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    userService
      .getAll()
      .then(setUsers)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  // render...
}
```

The benefits of this approach:

- **Single place to configure base URL, headers, and auth**
- **Consistent error handling** — every request checks `response.ok`
- **Easy to add interceptors** — logging, token refresh, retry logic
- **Components stay clean** — they call `userService.getAll()` instead of managing fetch details

---

## Building a Reusable useFetch Hook

The loading/error/data pattern repeats in every component. Extract it into a custom hook:

```jsx
// useFetch.js
import { useState, useEffect, useCallback } from "react";

export function useFetch(url, options = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const { enabled = true } = options;

  const fetchData = useCallback(async () => {
    if (!url || !enabled) return;

    const controller = new AbortController();

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(url, { signal: controller.signal });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const json = await response.json();
      setData(json);
    } catch (err) {
      if (err.name !== "AbortError") {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }

    return () => controller.abort();
  }, [url, enabled]);

  useEffect(() => {
    const cleanup = fetchData();
    return () => {
      if (cleanup instanceof Promise) {
        cleanup.then(fn => fn && fn());
      }
    };
  }, [fetchData]);

  const refetch = useCallback(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch };
}
```

### A Cleaner Version with AbortController

```jsx
// useFetch.js — clean version
import { useState, useEffect, useRef, useCallback } from "react";

export function useFetch(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const abortControllerRef = useRef(null);

  const fetchData = useCallback(async () => {
    // Cancel any in-flight request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(url, { signal: controller.signal });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const json = await response.json();
      setData(json);
    } catch (err) {
      if (err.name !== "AbortError") {
        setError(err.message);
      }
    } finally {
      if (!controller.signal.aborted) {
        setLoading(false);
      }
    }
  }, [url]);

  useEffect(() => {
    fetchData();

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}
```

### Using the Hook

```jsx
function UserList() {
  const { data: users, loading, error, refetch } = useFetch("/api/users");

  if (loading) return <p>Loading...</p>;
  if (error) return (
    <div>
      <p>Error: {error}</p>
      <button onClick={refetch}>Try Again</button>
    </div>
  );
  if (!users || users.length === 0) return <p>No users found.</p>;

  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

```jsx
function UserProfile({ userId }) {
  const { data: user, loading, error } = useFetch(`/api/users/${userId}`);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;
  if (!user) return <p>User not found.</p>;

  return <h2>{user.name}</h2>;
}
```

The hook handles loading states, error handling, race conditions, and cleanup — all in one line of code in the component.

---

## Pagination

### Page-Based Pagination

```jsx
function PaginatedUserList() {
  const [users, setUsers] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const ITEMS_PER_PAGE = 10;

  useEffect(() => {
    const controller = new AbortController();

    async function fetchPage() {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch(
          `/api/users?page=${page}&limit=${ITEMS_PER_PAGE}`,
          { signal: controller.signal }
        );

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        setUsers(data.users);
        setTotalPages(data.totalPages);
      } catch (err) {
        if (err.name !== "AbortError") {
          setError(err.message);
        }
      } finally {
        setLoading(false);
      }
    }

    fetchPage();
    return () => controller.abort();
  }, [page]);

  if (error) return <p>Error: {error}</p>;

  return (
    <div>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <ul>
          {users.map(user => (
            <li key={user.id}>{user.name}</li>
          ))}
        </ul>
      )}

      <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
        <button
          onClick={() => setPage(p => p - 1)}
          disabled={page <= 1 || loading}
        >
          Previous
        </button>

        <span>
          Page {page} of {totalPages}
        </span>

        <button
          onClick={() => setPage(p => p + 1)}
          disabled={page >= totalPages || loading}
        >
          Next
        </button>
      </div>
    </div>
  );
}
```

### Infinite Scroll

Infinite scroll loads more data as the user scrolls down, appending to the existing list:

```jsx
import { useState, useEffect, useRef, useCallback } from "react";

function InfiniteUserList() {
  const [users, setUsers] = useState([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const observerRef = useRef(null);

  // Fetch a page of users
  useEffect(() => {
    const controller = new AbortController();

    async function fetchPage() {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch(
          `/api/users?page=${page}&limit=20`,
          { signal: controller.signal }
        );

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();

        setUsers(prev => [...prev, ...data.users]);
        setHasMore(data.users.length === 20);
      } catch (err) {
        if (err.name !== "AbortError") {
          setError(err.message);
        }
      } finally {
        setLoading(false);
      }
    }

    fetchPage();
    return () => controller.abort();
  }, [page]);

  // IntersectionObserver to detect when the user scrolls to the bottom
  const lastUserRef = useCallback(
    node => {
      if (loading) return;

      if (observerRef.current) {
        observerRef.current.disconnect();
      }

      observerRef.current = new IntersectionObserver(entries => {
        if (entries[0].isIntersecting && hasMore) {
          setPage(prev => prev + 1);
        }
      });

      if (node) {
        observerRef.current.observe(node);
      }
    },
    [loading, hasMore]
  );

  return (
    <div>
      <h2>Users</h2>

      {error && <p style={{ color: "red" }}>Error: {error}</p>}

      <ul>
        {users.map((user, index) => {
          const isLast = index === users.length - 1;
          return (
            <li key={user.id} ref={isLast ? lastUserRef : null}>
              {user.name} — {user.email}
            </li>
          );
        })}
      </ul>

      {loading && <p>Loading more...</p>}
      {!hasMore && <p>You have reached the end.</p>}
    </div>
  );
}
```

How infinite scroll works:

1. We attach an `IntersectionObserver` to the **last item** in the list
2. When that item becomes visible in the viewport, we increment `page`
3. The page change triggers the effect, which fetches the next batch
4. New items are **appended** to the existing array (`[...prev, ...data.users]`)
5. When a fetch returns fewer items than the limit, we know there are no more items

The `useCallback` ref pattern lets us re-attach the observer to the new last element every time the list grows.

---

## Optimistic Updates

Optimistic updates make the UI feel instant by updating state before the server confirms the change. If the server request fails, you roll back to the previous state.

### Without Optimistic Updates (Pessimistic)

```jsx
async function handleDelete(userId) {
  setDeleting(userId);

  try {
    await api.delete(`/users/${userId}`);
    // Only update UI after server confirms
    setUsers(prev => prev.filter(u => u.id !== userId));
  } catch (err) {
    setError("Failed to delete user");
  } finally {
    setDeleting(null);
  }
}
```

The user clicks delete, sees a spinner for 200-500ms, and then the item disappears. Functional, but slow-feeling.

### With Optimistic Updates

```jsx
async function handleDelete(userId) {
  // Save current state for rollback
  const previousUsers = users;

  // Update UI immediately
  setUsers(prev => prev.filter(u => u.id !== userId));

  try {
    await api.delete(`/users/${userId}`);
  } catch (err) {
    // Rollback on failure
    setUsers(previousUsers);
    setError("Failed to delete user. The item has been restored.");
  }
}
```

The user clicks delete, the item disappears instantly, and the server request happens in the background. If the request fails, the item reappears with an error message.

### Optimistic Toggle (Like/Favorite)

```jsx
function PostCard({ post }) {
  const [liked, setLiked] = useState(post.liked);
  const [likeCount, setLikeCount] = useState(post.likeCount);

  async function handleLike() {
    // Save state for rollback
    const previousLiked = liked;
    const previousCount = likeCount;

    // Optimistic update
    setLiked(!liked);
    setLikeCount(prev => (liked ? prev - 1 : prev + 1));

    try {
      if (liked) {
        await api.delete(`/posts/${post.id}/like`);
      } else {
        await api.post(`/posts/${post.id}/like`);
      }
    } catch (err) {
      // Rollback
      setLiked(previousLiked);
      setLikeCount(previousCount);
    }
  }

  return (
    <div>
      <h3>{post.title}</h3>
      <button onClick={handleLike}>
        {liked ? "❤️" : "🤍"} {likeCount}
      </button>
    </div>
  );
}
```

### When to Use Optimistic Updates

| Scenario | Approach |
|----------|----------|
| Delete item from list | Optimistic — easy to rollback |
| Toggle like/favorite | Optimistic — common and expected to be instant |
| Create new item | Pessimistic — you need the server-generated ID |
| Payment/purchase | Pessimistic — never assume success for money |
| Update profile | Either — depends on complexity |

**Rule of thumb:** Use optimistic updates for simple, reversible actions. Use pessimistic updates for irreversible or critical operations.

---

## Caching API Responses

Fetching the same data every time a component mounts wastes bandwidth and makes the UI feel slow. A simple cache stores responses and serves them immediately on subsequent requests.

### Simple In-Memory Cache

```jsx
// cache.js
const cache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

export function getCached(key) {
  const entry = cache.get(key);
  if (!entry) return null;

  if (Date.now() - entry.timestamp > CACHE_DURATION) {
    cache.delete(key);
    return null;
  }

  return entry.data;
}

export function setCache(key, data) {
  cache.set(key, { data, timestamp: Date.now() });
}

export function invalidateCache(keyPattern) {
  for (const key of cache.keys()) {
    if (key.includes(keyPattern)) {
      cache.delete(key);
    }
  }
}
```

### useFetch with Caching

```jsx
import { getCached, setCache } from "./cache";

export function useFetch(url) {
  const [data, setData] = useState(() => getCached(url));
  const [loading, setLoading] = useState(!getCached(url));
  const [error, setError] = useState(null);

  useEffect(() => {
    const controller = new AbortController();

    async function fetchData() {
      // If we have cached data, show it immediately but still revalidate
      const cached = getCached(url);
      if (cached) {
        setData(cached);
        setLoading(false);
      }

      try {
        if (!cached) setLoading(true);
        setError(null);

        const response = await fetch(url, { signal: controller.signal });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const json = await response.json();
        setData(json);
        setCache(url, json);
      } catch (err) {
        if (err.name !== "AbortError") {
          setError(err.message);
        }
      } finally {
        setLoading(false);
      }
    }

    fetchData();
    return () => controller.abort();
  }, [url]);

  return { data, loading, error };
}
```

This implements a "stale-while-revalidate" strategy: show cached data immediately, fetch fresh data in the background, and update when the fresh data arrives. The user sees instant results, with the data quietly refreshing.

### Invalidating the Cache

When you create, update, or delete data, invalidate the relevant cache entries:

```jsx
async function createUser(userData) {
  const newUser = await api.post("/users", userData);

  // Invalidate the users list cache so it refetches
  invalidateCache("/users");

  return newUser;
}
```

---

## Handling Authentication Tokens

Most APIs require authentication. The common pattern is:

1. User logs in and receives a JWT (JSON Web Token)
2. Store the token (in memory, localStorage, or an httpOnly cookie)
3. Send the token with every API request in the `Authorization` header

### Token Storage and Request Interceptor

The API service layer we built earlier already handles this:

```jsx
// In the request function from api.js
const token = localStorage.getItem("token");
if (token) {
  config.headers.Authorization = `Bearer ${token}`;
}
```

### Token Refresh Pattern

Tokens expire. When they do, the server returns a 401 status. A common pattern is to automatically refresh the token and retry the request:

```jsx
// api.js — with token refresh
let isRefreshing = false;
let refreshPromise = null;

async function refreshToken() {
  const refreshToken = localStorage.getItem("refreshToken");

  const response = await fetch("/api/auth/refresh", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refreshToken }),
  });

  if (!response.ok) {
    throw new Error("Token refresh failed");
  }

  const data = await response.json();
  localStorage.setItem("token", data.token);
  localStorage.setItem("refreshToken", data.refreshToken);
  return data.token;
}

async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const token = localStorage.getItem("token");

  const config = {
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
    ...options,
  };

  let response = await fetch(url, config);

  // If 401, try refreshing the token
  if (response.status === 401) {
    try {
      // Prevent multiple simultaneous refresh requests
      if (!isRefreshing) {
        isRefreshing = true;
        refreshPromise = refreshToken();
      }

      const newToken = await refreshPromise;
      isRefreshing = false;

      // Retry the original request with the new token
      config.headers.Authorization = `Bearer ${newToken}`;
      response = await fetch(url, config);
    } catch (err) {
      isRefreshing = false;
      // Refresh failed — force logout
      localStorage.removeItem("token");
      localStorage.removeItem("refreshToken");
      window.location.href = "/login";
      throw err;
    }
  }

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.message || `HTTP ${response.status}`);
  }

  if (response.status === 204) return null;
  return response.json();
}
```

The `isRefreshing` flag prevents multiple components from triggering simultaneous refresh requests. They all share the same `refreshPromise`.

---

## Retry Logic

Network requests can fail due to temporary issues — flaky connections, server hiccups, rate limiting. Retry logic automatically retries failed requests before giving up:

```jsx
async function fetchWithRetry(url, options = {}, maxRetries = 3) {
  let lastError;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(url, options);

      if (!response.ok) {
        // Only retry on server errors (5xx) or rate limiting (429)
        if (response.status >= 500 || response.status === 429) {
          throw new Error(`HTTP ${response.status}`);
        }
        // Client errors (4xx) should not be retried
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return response;
    } catch (err) {
      lastError = err;

      // Do not retry client errors
      if (err.message.includes("HTTP 4")) {
        throw err;
      }

      if (attempt < maxRetries) {
        // Exponential backoff: wait 1s, 2s, 4s
        const delay = Math.pow(2, attempt) * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError;
}
```

### Using Retry in the API Service

```jsx
// Integrate into the api.js request function
async function request(endpoint, options = {}) {
  const { retries = 3, ...fetchOptions } = options;
  const url = `${BASE_URL}${endpoint}`;

  // ... set up headers, auth, etc.

  const response = await fetchWithRetry(url, fetchOptions, retries);

  if (response.status === 204) return null;
  return response.json();
}
```

### When to Retry

| Scenario | Retry? |
|----------|--------|
| Network error (no internet) | Yes |
| Server error (500, 502, 503) | Yes |
| Rate limited (429) | Yes, with backoff |
| Not found (404) | No |
| Unauthorized (401) | No (refresh token instead) |
| Bad request (400) | No |
| Request timeout | Yes |

---

## Debounced API Calls

When a user types in a search box, you do not want to send a request for every keystroke. Debouncing waits until the user stops typing before making the request:

```jsx
import { useState, useEffect } from "react";

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

function SearchWithDebounce() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const debouncedQuery = useDebounce(query, 300);

  useEffect(() => {
    if (!debouncedQuery) {
      setResults([]);
      return;
    }

    const controller = new AbortController();

    async function search() {
      try {
        setLoading(true);
        const response = await fetch(
          `/api/search?q=${encodeURIComponent(debouncedQuery)}`,
          { signal: controller.signal }
        );
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        setResults(data);
      } catch (err) {
        if (err.name !== "AbortError") {
          console.error(err);
        }
      } finally {
        setLoading(false);
      }
    }

    search();
    return () => controller.abort();
  }, [debouncedQuery]);

  return (
    <div>
      <input
        value={query}
        onChange={e => setQuery(e.target.value)}
        placeholder="Search..."
      />

      {loading && <p>Searching...</p>}

      <ul>
        {results.map(result => (
          <li key={result.id}>{result.title}</li>
        ))}
      </ul>
    </div>
  );
}
```

The user types "react hooks" quickly. Without debouncing, that sends 11 requests. With a 300ms debounce, it sends 1 or 2 requests.

---

## Error Recovery Patterns

### Retry Button

The simplest recovery pattern — show an error with a button to try again:

```jsx
function UserList() {
  const { data, loading, error, refetch } = useFetch("/api/users");

  if (error) {
    return (
      <div>
        <p>Something went wrong: {error}</p>
        <button onClick={refetch}>Try Again</button>
      </div>
    );
  }

  // ...
}
```

### Error with Fallback Content

Show cached or default data when the fetch fails:

```jsx
function Dashboard() {
  const [stats, setStats] = useState(() => {
    // Try to load last known data from localStorage
    const cached = localStorage.getItem("dashboard-stats");
    return cached ? JSON.parse(cached) : null;
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStats() {
      try {
        const response = await fetch("/api/dashboard/stats");
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        setStats(data);
        localStorage.setItem("dashboard-stats", JSON.stringify(data));
      } catch (err) {
        setError(err.message);
        // stats remains as cached data — stale but better than nothing
      } finally {
        setLoading(false);
      }
    }

    fetchStats();
  }, []);

  return (
    <div>
      {error && (
        <p style={{ color: "orange" }}>
          Could not refresh data. Showing last known values.
        </p>
      )}

      {stats ? (
        <div>
          <p>Users: {stats.totalUsers}</p>
          <p>Revenue: ${stats.revenue}</p>
        </div>
      ) : loading ? (
        <p>Loading...</p>
      ) : (
        <p>No data available.</p>
      )}
    </div>
  );
}
```

### Per-Field Error Handling

For forms, show errors next to the specific field that caused them:

```jsx
function RegistrationForm() {
  const [form, setForm] = useState({ email: "", username: "", password: "" });
  const [fieldErrors, setFieldErrors] = useState({});
  const [generalError, setGeneralError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setFieldErrors({});
    setGeneralError(null);

    try {
      const response = await fetch("/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      if (!response.ok) {
        const errorData = await response.json();

        if (response.status === 422 && errorData.errors) {
          // Validation errors — show per field
          // Server returns: { errors: { email: "Already taken", password: "Too short" } }
          setFieldErrors(errorData.errors);
          return;
        }

        throw new Error(errorData.message || "Registration failed");
      }

      // Success — redirect or show success message
    } catch (err) {
      setGeneralError(err.message);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {generalError && <p style={{ color: "red" }}>{generalError}</p>}

      <div>
        <input
          type="email"
          value={form.email}
          onChange={e => setForm(prev => ({ ...prev, email: e.target.value }))}
          placeholder="Email"
        />
        {fieldErrors.email && (
          <p style={{ color: "red", fontSize: "0.85em" }}>{fieldErrors.email}</p>
        )}
      </div>

      <div>
        <input
          value={form.username}
          onChange={e => setForm(prev => ({ ...prev, username: e.target.value }))}
          placeholder="Username"
        />
        {fieldErrors.username && (
          <p style={{ color: "red", fontSize: "0.85em" }}>{fieldErrors.username}</p>
        )}
      </div>

      <div>
        <input
          type="password"
          value={form.password}
          onChange={e => setForm(prev => ({ ...prev, password: e.target.value }))}
          placeholder="Password"
        />
        {fieldErrors.password && (
          <p style={{ color: "red", fontSize: "0.85em" }}>{fieldErrors.password}</p>
        )}
      </div>

      <button type="submit">Register</button>
    </form>
  );
}
```

---

## Mini Project: User Management Dashboard

Let us build a complete user management dashboard that demonstrates all the data fetching patterns from this chapter.

```jsx
// api.js — centralized API service
const BASE_URL = "https://jsonplaceholder.typicode.com";

async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;

  const config = {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  };

  const response = await fetch(url, config);

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    const error = new Error(
      errorBody.message || `Request failed (${response.status})`
    );
    error.status = response.status;
    throw error;
  }

  if (response.status === 204) return null;
  return response.json();
}

export const userApi = {
  getAll: () => request("/users"),
  getById: (id) => request(`/users/${id}`),
  create: (data) => request("/users", { method: "POST", body: JSON.stringify(data) }),
  update: (id, data) => request(`/users/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  delete: (id) => request(`/users/${id}`, { method: "DELETE" }),
  getPosts: (userId) => request(`/users/${userId}/posts`),
};
```

```jsx
// useAsync.js — hook for any async operation (not just GET)
import { useState, useCallback } from "react";

export function useAsync() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(async (asyncFunction) => {
    try {
      setLoading(true);
      setError(null);
      const result = await asyncFunction();
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const clearError = useCallback(() => setError(null), []);

  return { loading, error, execute, clearError };
}
```

```jsx
// UserManagement.jsx — the main component
import { useState, useEffect } from "react";
import { userApi } from "./api";
import { useAsync } from "./useAsync";

function UserManagement() {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loadingUsers, setLoadingUsers] = useState(true);
  const [fetchError, setFetchError] = useState(null);
  const [notification, setNotification] = useState(null);

  // Fetch all users on mount
  useEffect(() => {
    async function loadUsers() {
      try {
        setLoadingUsers(true);
        const data = await userApi.getAll();
        setUsers(data);
      } catch (err) {
        setFetchError(err.message);
      } finally {
        setLoadingUsers(false);
      }
    }

    loadUsers();
  }, []);

  // Auto-dismiss notifications
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  function showNotification(message, type = "success") {
    setNotification({ message, type });
  }

  // Optimistic delete
  async function handleDelete(userId) {
    const previousUsers = users;
    setUsers(prev => prev.filter(u => u.id !== userId));

    if (selectedUser?.id === userId) {
      setSelectedUser(null);
    }

    try {
      await userApi.delete(userId);
      showNotification("User deleted successfully");
    } catch (err) {
      setUsers(previousUsers);
      showNotification("Failed to delete user. Restored.", "error");
    }
  }

  // Create user
  async function handleCreate(userData) {
    try {
      const newUser = await userApi.create(userData);
      setUsers(prev => [...prev, newUser]);
      setShowCreateForm(false);
      showNotification("User created successfully");
    } catch (err) {
      throw err; // Let the form handle the error
    }
  }

  // Update user
  async function handleUpdate(userId, userData) {
    try {
      const updatedUser = await userApi.update(userId, userData);
      setUsers(prev =>
        prev.map(u => (u.id === userId ? updatedUser : u))
      );
      setSelectedUser(updatedUser);
      showNotification("User updated successfully");
    } catch (err) {
      throw err;
    }
  }

  if (loadingUsers) return <p>Loading users...</p>;

  if (fetchError) {
    return (
      <div>
        <p>Failed to load users: {fetchError}</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", gap: "2rem" }}>
      {/* Notification */}
      {notification && (
        <div
          style={{
            position: "fixed",
            top: "1rem",
            right: "1rem",
            padding: "1rem",
            borderRadius: 4,
            backgroundColor: notification.type === "error" ? "#fee" : "#efe",
            color: notification.type === "error" ? "#c00" : "#060",
            border: `1px solid ${notification.type === "error" ? "#fcc" : "#cec"}`,
          }}
        >
          {notification.message}
        </div>
      )}

      {/* User List */}
      <div style={{ flex: 1 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h2>Users ({users.length})</h2>
          <button onClick={() => {
            setShowCreateForm(true);
            setSelectedUser(null);
          }}>
            + New User
          </button>
        </div>

        <ul style={{ listStyle: "none", padding: 0 }}>
          {users.map(user => (
            <li
              key={user.id}
              style={{
                padding: "0.75rem",
                marginBottom: "0.5rem",
                border: "1px solid #ddd",
                borderRadius: 4,
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                backgroundColor: selectedUser?.id === user.id ? "#f0f0ff" : "white",
                cursor: "pointer",
              }}
              onClick={() => {
                setSelectedUser(user);
                setShowCreateForm(false);
              }}
            >
              <div>
                <strong>{user.name}</strong>
                <br />
                <small>{user.email}</small>
              </div>
              <button
                onClick={e => {
                  e.stopPropagation();
                  handleDelete(user.id);
                }}
                style={{ color: "red", border: "none", background: "none", cursor: "pointer" }}
              >
                Delete
              </button>
            </li>
          ))}
        </ul>
      </div>

      {/* Detail / Form Panel */}
      <div style={{ flex: 1 }}>
        {showCreateForm && (
          <UserForm title="Create User" onSubmit={handleCreate} />
        )}

        {selectedUser && !showCreateForm && (
          <UserDetail
            user={selectedUser}
            onUpdate={handleUpdate}
          />
        )}

        {!selectedUser && !showCreateForm && (
          <p style={{ color: "#999" }}>Select a user or create a new one.</p>
        )}
      </div>
    </div>
  );
}
```

```jsx
// UserForm.jsx
function UserForm({ title, initialData, onSubmit }) {
  const [form, setForm] = useState(
    initialData || { name: "", email: "", phone: "", website: "" }
  );
  const { loading, error, execute, clearError } = useAsync();

  function handleChange(e) {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
    clearError();
  }

  async function handleSubmit(e) {
    e.preventDefault();
    await execute(() => onSubmit(form));
  }

  return (
    <div>
      <h3>{title}</h3>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "0.75rem" }}>
          <label>Name</label>
          <input
            name="name"
            value={form.name}
            onChange={handleChange}
            required
            disabled={loading}
            style={{ display: "block", width: "100%", padding: "0.5rem" }}
          />
        </div>

        <div style={{ marginBottom: "0.75rem" }}>
          <label>Email</label>
          <input
            name="email"
            type="email"
            value={form.email}
            onChange={handleChange}
            required
            disabled={loading}
            style={{ display: "block", width: "100%", padding: "0.5rem" }}
          />
        </div>

        <div style={{ marginBottom: "0.75rem" }}>
          <label>Phone</label>
          <input
            name="phone"
            value={form.phone}
            onChange={handleChange}
            disabled={loading}
            style={{ display: "block", width: "100%", padding: "0.5rem" }}
          />
        </div>

        <div style={{ marginBottom: "0.75rem" }}>
          <label>Website</label>
          <input
            name="website"
            value={form.website}
            onChange={handleChange}
            disabled={loading}
            style={{ display: "block", width: "100%", padding: "0.5rem" }}
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Saving..." : "Save"}
        </button>
      </form>
    </div>
  );
}
```

```jsx
// UserDetail.jsx — shows user info and their posts
import { useState, useEffect } from "react";
import { userApi } from "./api";

function UserDetail({ user, onUpdate }) {
  const [editing, setEditing] = useState(false);
  const [posts, setPosts] = useState([]);
  const [loadingPosts, setLoadingPosts] = useState(true);

  // Fetch user's posts when user changes
  useEffect(() => {
    const controller = new AbortController();

    async function fetchPosts() {
      try {
        setLoadingPosts(true);
        const data = await userApi.getPosts(user.id);
        setPosts(data);
      } catch (err) {
        if (err.name !== "AbortError") {
          console.error("Failed to load posts:", err.message);
        }
      } finally {
        setLoadingPosts(false);
      }
    }

    fetchPosts();
    return () => controller.abort();
  }, [user.id]);

  if (editing) {
    return (
      <UserForm
        title="Edit User"
        initialData={user}
        onSubmit={async (data) => {
          await onUpdate(user.id, data);
          setEditing(false);
        }}
      />
    );
  }

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h3>{user.name}</h3>
        <button onClick={() => setEditing(true)}>Edit</button>
      </div>

      <p>Email: {user.email}</p>
      <p>Phone: {user.phone}</p>
      <p>Website: {user.website}</p>

      <h4>Posts ({posts.length})</h4>
      {loadingPosts ? (
        <p>Loading posts...</p>
      ) : posts.length === 0 ? (
        <p>No posts yet.</p>
      ) : (
        <ul>
          {posts.slice(0, 5).map(post => (
            <li key={post.id} style={{ marginBottom: "0.5rem" }}>
              <strong>{post.title}</strong>
              <p style={{ fontSize: "0.85em", color: "#666" }}>
                {post.body.substring(0, 100)}...
              </p>
            </li>
          ))}
          {posts.length > 5 && (
            <p style={{ color: "#666" }}>
              And {posts.length - 5} more posts...
            </p>
          )}
        </ul>
      )}
    </div>
  );
}
```

This mini project demonstrates:

- **Centralized API service** with consistent error handling
- **Loading, error, and empty states** for data fetching
- **CRUD operations** (Create, Read, Update, Delete)
- **Optimistic delete** with rollback on failure
- **Race condition handling** for user posts
- **Reusable useAsync hook** for mutation operations
- **Notification system** for user feedback
- **Dependent data fetching** (user → posts)

---

## Common Mistakes

### Mistake 1: Not Checking response.ok

```jsx
// WRONG — 404 and 500 responses are silently treated as success
const response = await fetch("/api/users");
const data = await response.json();

// CORRECT
const response = await fetch("/api/users");
if (!response.ok) {
  throw new Error(`HTTP ${response.status}`);
}
const data = await response.json();
```

### Mistake 2: Making the Effect Callback Async

```jsx
// WRONG — useEffect does not support async callbacks
useEffect(async () => {
  const data = await fetchUsers();
  setUsers(data);
}, []);

// CORRECT — define async function inside the effect
useEffect(() => {
  async function loadUsers() {
    const data = await fetchUsers();
    setUsers(data);
  }
  loadUsers();
}, []);
```

React expects the effect callback to return either nothing or a cleanup function. An async function returns a Promise, which React cannot use as a cleanup.

### Mistake 3: Not Handling Race Conditions

```jsx
// WRONG — stale responses can overwrite fresh data
useEffect(() => {
  fetch(`/api/search?q=${query}`)
    .then(r => r.json())
    .then(setResults);
}, [query]);

// CORRECT — cancel previous requests
useEffect(() => {
  const controller = new AbortController();

  fetch(`/api/search?q=${query}`, { signal: controller.signal })
    .then(r => r.json())
    .then(setResults)
    .catch(err => {
      if (err.name !== "AbortError") setError(err.message);
    });

  return () => controller.abort();
}, [query]);
```

### Mistake 4: Forgetting to Reset State When Parameters Change

```jsx
// WRONG — shows stale data while loading new data
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/users/${userId}`)
      .then(r => r.json())
      .then(data => {
        setUser(data);
        setLoading(false);
      });
  }, [userId]);

  // When userId changes, the old user's data shows until the new one loads
}

// CORRECT — reset state when parameters change
useEffect(() => {
  setUser(null);
  setLoading(true);
  setError(null);

  // ... fetch
}, [userId]);
```

### Mistake 5: Fetching in Event Handlers When You Should Use Effects

```jsx
// WRONG — fetches on every click, no automatic refetch
function UserList() {
  const [users, setUsers] = useState([]);

  function loadUsers() {
    fetch("/api/users")
      .then(r => r.json())
      .then(setUsers);
  }

  return (
    <div>
      <button onClick={loadUsers}>Load Users</button>
      {/* Users list is empty until the button is clicked */}
    </div>
  );
}

// CORRECT — fetch on mount with useEffect
function UserList() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    fetch("/api/users")
      .then(r => r.json())
      .then(setUsers);
  }, []);

  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

Use effects for data that should load when a component appears. Use event handlers for data that loads in response to user actions (form submissions, button clicks).

---

## Best Practices

1. **Always check `response.ok`** — The `fetch` API does not throw on HTTP errors. Check the status before parsing the body.

2. **Handle all three states** — Every data fetching component should handle loading, error, and success (including empty data). Never assume the request will succeed.

3. **Use AbortController for dependent fetches** — Any fetch that depends on a changing value (search query, route parameter, selected item) should use AbortController to cancel stale requests.

4. **Centralize API logic** — Create an API service layer with a base `request` function that handles headers, authentication, and error parsing consistently.

5. **Separate fetching from rendering** — Extract data fetching into custom hooks. Components should call `useFetch` or `useUsers`, not manage fetch state directly.

6. **Debounce user-driven fetches** — Search inputs, autocomplete, and filter changes should be debounced to avoid excessive API calls.

7. **Use optimistic updates for simple actions** — Toggles, deletes, and other reversible actions should update the UI immediately and roll back on failure.

8. **Show meaningful error messages** — "Something went wrong" is not helpful. Show what went wrong and give the user a way to recover (retry button, fallback content).

9. **Invalidate caches after mutations** — When you create, update, or delete data, invalidate related cache entries so subsequent reads get fresh data.

---

## Summary

In this chapter, you learned:

- **The Fetch API** sends HTTP requests and returns Promises — but does not throw on HTTP errors, so you must check `response.ok`
- **The standard pattern** uses `loading`, `error`, and data state variables, with `try/catch/finally` in an async function inside `useEffect`
- **Race conditions** occur when responses arrive out of order — use `AbortController` to cancel stale requests
- **CRUD operations** use different HTTP methods: GET (read), POST (create), PUT/PATCH (update), DELETE (remove)
- **An API service layer** centralizes configuration, authentication, and error handling in one place
- **A reusable `useFetch` hook** eliminates boilerplate by encapsulating the loading/error/data pattern
- **Pagination** can be page-based (replace content) or infinite scroll (append content with IntersectionObserver)
- **Optimistic updates** make the UI feel instant by updating state before the server responds, with rollback on failure
- **Caching** avoids redundant network requests — stale-while-revalidate shows cached data immediately while refreshing in the background
- **Retry logic** with exponential backoff handles transient failures gracefully
- **Debouncing** prevents excessive API calls from rapid user input

---

## Interview Questions

1. **Why does `fetch` not throw an error for HTTP status codes like 404 or 500?**

   The `fetch` API only rejects its Promise for network-level failures (no internet, DNS failure, CORS error). HTTP error status codes (4xx, 5xx) are considered valid server responses — the server received the request and responded. You must check `response.ok` or `response.status` to detect HTTP errors and throw manually if needed.

2. **How do you prevent race conditions when fetching data based on a changing input?**

   Use `AbortController`. Create a new controller for each fetch, pass its `signal` to the fetch options, and call `controller.abort()` in the effect's cleanup function. When the input changes, React runs the cleanup (aborting the previous request) before starting the new effect. Aborted requests throw an `AbortError` which should be caught and ignored.

3. **What is the difference between optimistic and pessimistic updates?**

   Pessimistic updates wait for the server to confirm the change before updating the UI — the user sees a loading state. Optimistic updates change the UI immediately and send the request in the background. If the server request fails, the UI rolls back to the previous state. Optimistic updates feel faster and are appropriate for simple, reversible actions. Pessimistic updates are safer for critical operations like payments.

4. **What is stale-while-revalidate?**

   A caching strategy where cached data is served immediately (even if stale) while a fresh request is made in the background. When the fresh data arrives, it replaces the stale data and updates the cache. The user sees content instantly instead of a loading spinner, and the data silently refreshes. This balances speed (instant display) with freshness (background update).

5. **Why should you create an API service layer instead of using fetch directly in components?**

   A centralized API service provides a single place to configure base URLs, default headers, authentication tokens, and error handling. It prevents code duplication, ensures consistent behavior across all API calls, and makes it easy to add cross-cutting concerns like logging, retry logic, or token refresh. Components call clean methods like `userApi.getById(id)` instead of managing fetch details.

6. **How does the IntersectionObserver pattern work for infinite scroll?**

   An `IntersectionObserver` watches when a target element (the last item in the list) enters the viewport. You attach the observer to the last rendered item using a callback ref. When the observer fires (the item is visible), you increment the page number, triggering a fetch for the next batch of data. The new items are appended to the existing array, and the observer is re-attached to the new last item.

---

## Practice Exercises

### Exercise 1: GitHub Repository Explorer

Build a component that searches GitHub repositories using the public API (`https://api.github.com/search/repositories?q={query}`). Include debounced search, loading states, error handling, and paginated results. Display the repository name, stars, description, and language.

### Exercise 2: Shopping Cart with Optimistic Updates

Create a product list with an "Add to Cart" button for each item. When clicked, optimistically add the item to a cart state and show a success toast. Simulate a failed API call for one specific product to demonstrate rollback. Show the cart contents with quantities and a total price.

### Exercise 3: Data Table with Server-Side Operations

Build a data table that supports server-side pagination, sorting, and filtering. The sort column, sort direction, filter values, and page number should all be stored in the URL as query parameters (using `useSearchParams`). Changing any parameter should fetch new data. Use debouncing for the filter input.

### Exercise 4: Offline-First Notes App

Create a notes application that works offline. Save notes to localStorage immediately and sync to the server when online. Use `navigator.onLine` and the `online`/`offline` events to detect connectivity. Show a banner when offline. Queue failed requests and retry them when the connection is restored.

---

## What Is Next?

In Chapter 17, we will explore **Styling in React** — from CSS Modules and CSS-in-JS to utility-first CSS with Tailwind, and how to choose the right styling approach for your application.
