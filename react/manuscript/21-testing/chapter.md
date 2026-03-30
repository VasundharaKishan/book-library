# Chapter 21: Testing React Applications

## Learning Goals

By the end of this chapter, you will be able to:

- Understand the types of tests and when to use each
- Set up Vitest and React Testing Library in a React project
- Write unit tests for utility functions and custom hooks
- Write component tests that simulate user interactions
- Query elements the way screen readers and users find them
- Test forms, events, conditional rendering, and lists
- Test async behavior (data fetching, loading states, timers)
- Mock API calls and modules
- Follow testing best practices that make tests maintainable
- Know what to test and what not to test

---

## Why Test?

Tests give you confidence that your code works as intended — and continues to work as you make changes. Without tests:

- Every code change is a risk — you might break something without knowing
- Refactoring is scary — you avoid improving code because you might introduce bugs
- Bugs reach users — manual testing misses edge cases
- Onboarding is slow — new team members cannot verify their changes

With tests:

- You catch regressions immediately — broken tests tell you exactly what broke
- Refactoring is safe — change the implementation, run the tests, confirm nothing broke
- Edge cases are covered — tests exercise paths you would not think to click through
- Documentation — tests describe how your code is supposed to behave

### Types of Tests

| Type | What It Tests | Speed | Confidence | Example |
|------|-------------|-------|------------|---------|
| **Unit tests** | Individual functions, hooks | Very fast | Low-medium | `formatCurrency(1234)` returns `"$1,234.00"` |
| **Component tests** | A component's behavior from the user's perspective | Fast | Medium-high | Clicking "Add to Cart" shows the item in the cart |
| **Integration tests** | Multiple components working together | Medium | High | Submitting a form navigates to the success page |
| **End-to-end tests** | The entire application in a real browser | Slow | Very high | Complete checkout flow from browsing to payment |

This chapter focuses on **unit tests** and **component tests** — the tests you write most often as a React developer. End-to-end tests are typically handled by tools like Playwright or Cypress, which are beyond our scope.

---

## Setting Up the Test Environment

### Vitest + React Testing Library

**Vitest** is a fast test runner built for Vite projects. It is compatible with the Jest API, so if you know Jest, you already know Vitest.

**React Testing Library (RTL)** provides utilities for rendering React components and interacting with them the way a user would — by finding elements by their text, label, or role, not by CSS class names or component internals.

### Installation

```bash
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

### Configuration

```js
// vite.config.js
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./src/test/setup.js",
  },
});
```

```js
// src/test/setup.js
import "@testing-library/jest-dom";
```

The `@testing-library/jest-dom` import adds custom matchers like `toBeInTheDocument()`, `toHaveTextContent()`, and `toBeDisabled()`.

### Running Tests

```bash
# Run all tests
npx vitest

# Run tests in watch mode (re-runs on file changes)
npx vitest --watch

# Run a specific test file
npx vitest src/components/Button.test.jsx

# Run tests with coverage
npx vitest --coverage
```

Add scripts to your `package.json`:

```json
{
  "scripts": {
    "test": "vitest",
    "test:watch": "vitest --watch",
    "test:coverage": "vitest --coverage"
  }
}
```

---

## Your First Test

### Testing a Utility Function

```js
// utils/formatCurrency.js
export function formatCurrency(amount) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);
}
```

```js
// utils/formatCurrency.test.js
import { describe, it, expect } from "vitest";
import { formatCurrency } from "./formatCurrency";

describe("formatCurrency", () => {
  it("formats a positive number as USD", () => {
    expect(formatCurrency(1234.5)).toBe("$1,234.50");
  });

  it("formats zero", () => {
    expect(formatCurrency(0)).toBe("$0.00");
  });

  it("formats a negative number", () => {
    expect(formatCurrency(-99.99)).toBe("-$99.99");
  });

  it("formats a large number with commas", () => {
    expect(formatCurrency(1000000)).toBe("$1,000,000.00");
  });
});
```

### Anatomy of a Test

```js
describe("formatCurrency", () => {   // Group related tests
  it("formats a positive number", () => { // Describe expected behavior
    expect(formatCurrency(1234.5))    // Actual value
      .toBe("$1,234.50");            // Expected value
  });
});
```

- **`describe`** — Groups related tests (optional but recommended for organization)
- **`it`** (or `test`) — Defines a single test case
- **`expect`** — Creates an assertion
- **`.toBe`** — A matcher that checks strict equality

### Common Matchers

```js
// Equality
expect(value).toBe(5);                    // Strict equality (===)
expect(obj).toEqual({ a: 1, b: 2 });     // Deep equality for objects/arrays

// Truthiness
expect(value).toBeTruthy();               // Not false, 0, null, undefined, ""
expect(value).toBeFalsy();
expect(value).toBeNull();
expect(value).toBeUndefined();
expect(value).toBeDefined();

// Numbers
expect(value).toBeGreaterThan(3);
expect(value).toBeLessThanOrEqual(10);
expect(0.1 + 0.2).toBeCloseTo(0.3);      // Floating point comparison

// Strings
expect(str).toMatch(/regex/);
expect(str).toContain("substring");

// Arrays
expect(arr).toContain("item");
expect(arr).toHaveLength(3);

// Objects
expect(obj).toHaveProperty("key");
expect(obj).toMatchObject({ a: 1 });      // Partial match

// Exceptions
expect(() => badFunction()).toThrow();
expect(() => badFunction()).toThrow("error message");

// DOM matchers (from @testing-library/jest-dom)
expect(element).toBeInTheDocument();
expect(element).toBeVisible();
expect(element).toBeDisabled();
expect(element).toHaveTextContent("Hello");
expect(element).toHaveAttribute("href", "/about");
expect(element).toHaveClass("active");
expect(input).toHaveValue("test@email.com");
```

---

## Testing React Components

### Rendering a Component

```jsx
// components/Greeting.jsx
function Greeting({ name }) {
  return <h1>Hello, {name}!</h1>;
}
```

```jsx
// components/Greeting.test.jsx
import { render, screen } from "@testing-library/react";
import Greeting from "./Greeting";

describe("Greeting", () => {
  it("renders the greeting with the provided name", () => {
    render(<Greeting name="Alice" />);

    expect(screen.getByText("Hello, Alice!")).toBeInTheDocument();
  });

  it("renders with a different name", () => {
    render(<Greeting name="Bob" />);

    expect(screen.getByText("Hello, Bob!")).toBeInTheDocument();
  });
});
```

- **`render`** — Renders the component into a virtual DOM
- **`screen`** — Provides query methods to find elements in the rendered output
- **`getByText`** — Finds an element by its text content

### The screen Queries

React Testing Library provides queries that mirror how users and assistive technologies find elements. Use them in this priority order:

**1. Accessible queries (preferred)**

| Query | When to Use |
|-------|------------|
| `getByRole` | Interactive elements: buttons, links, headings, checkboxes |
| `getByLabelText` | Form inputs with labels |
| `getByPlaceholderText` | Inputs with placeholder text (when no label) |
| `getByText` | Non-interactive elements by their text content |
| `getByDisplayValue` | Inputs by their current value |
| `getByAltText` | Images by their alt text |
| `getByTitle` | Elements with a title attribute |

**2. Semantic queries**

| Query | When to Use |
|-------|------------|
| `getByTestId` | Last resort — when no accessible query works |

```jsx
// BEST — queries that users and screen readers use
screen.getByRole("button", { name: "Save" });
screen.getByLabelText("Email");
screen.getByText("Welcome back!");

// GOOD — for specific cases
screen.getByPlaceholderText("Search...");
screen.getByAltText("User avatar");

// LAST RESORT — when nothing else works
screen.getByTestId("complex-widget");
```

### Query Variants

Each query has three variants:

| Variant | Returns | Throws if not found? | Use for |
|---------|---------|---------------------|---------|
| `getBy` | Element | Yes | Elements that should exist |
| `queryBy` | Element or `null` | No | Asserting something does NOT exist |
| `findBy` | Promise\<Element\> | Yes (rejects) | Elements that appear asynchronously |

```jsx
// Element SHOULD be there
const button = screen.getByRole("button", { name: "Save" });

// Element should NOT be there
expect(screen.queryByText("Error")).not.toBeInTheDocument();

// Element will appear after an async operation
const message = await screen.findByText("Saved successfully!");
```

Each variant also has an `All` version (`getAllByRole`, `queryAllByText`, `findAllByRole`) that returns all matching elements as an array.

---

## Testing User Interactions

### userEvent

`@testing-library/user-event` simulates real user interactions more accurately than the basic `fireEvent`:

```jsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

describe("Counter", () => {
  it("increments when the button is clicked", async () => {
    const user = userEvent.setup();
    render(<Counter />);

    expect(screen.getByText("Count: 0")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Increment" }));

    expect(screen.getByText("Count: 1")).toBeInTheDocument();
  });

  it("decrements when the button is clicked", async () => {
    const user = userEvent.setup();
    render(<Counter />);

    await user.click(screen.getByRole("button", { name: "Decrement" }));

    expect(screen.getByText("Count: -1")).toBeInTheDocument();
  });
});
```

Always use `userEvent.setup()` at the start of your test, then `await` each interaction. This is the recommended approach in modern React Testing Library.

### Common User Interactions

```jsx
const user = userEvent.setup();

// Click
await user.click(element);

// Double click
await user.dblClick(element);

// Type text
await user.type(screen.getByLabelText("Email"), "test@example.com");

// Clear and type
await user.clear(screen.getByLabelText("Email"));
await user.type(screen.getByLabelText("Email"), "new@example.com");

// Select option
await user.selectOptions(screen.getByLabelText("Country"), "US");

// Check/uncheck checkbox
await user.click(screen.getByRole("checkbox", { name: "Accept terms" }));

// Keyboard
await user.keyboard("{Enter}");
await user.keyboard("{Escape}");
await user.tab();

// Hover
await user.hover(element);
await user.unhover(element);
```

---

## Testing Component Patterns

### Testing Conditional Rendering

```jsx
// ToggleContent.jsx
function ToggleContent({ title, children }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div>
      <button onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? "Hide" : "Show"} {title}
      </button>
      {isOpen && <div>{children}</div>}
    </div>
  );
}
```

```jsx
// ToggleContent.test.jsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ToggleContent from "./ToggleContent";

describe("ToggleContent", () => {
  it("does not show content initially", () => {
    render(<ToggleContent title="Details">Secret content</ToggleContent>);

    expect(screen.queryByText("Secret content")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Show Details" })).toBeInTheDocument();
  });

  it("shows content when the button is clicked", async () => {
    const user = userEvent.setup();
    render(<ToggleContent title="Details">Secret content</ToggleContent>);

    await user.click(screen.getByRole("button", { name: "Show Details" }));

    expect(screen.getByText("Secret content")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Hide Details" })).toBeInTheDocument();
  });

  it("hides content when clicked again", async () => {
    const user = userEvent.setup();
    render(<ToggleContent title="Details">Secret content</ToggleContent>);

    await user.click(screen.getByRole("button", { name: "Show Details" }));
    await user.click(screen.getByRole("button", { name: "Hide Details" }));

    expect(screen.queryByText("Secret content")).not.toBeInTheDocument();
  });
});
```

### Testing Forms

```jsx
// LoginForm.jsx
function LoginForm({ onSubmit }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);

  function handleSubmit(e) {
    e.preventDefault();

    if (!email) {
      setError("Email is required");
      return;
    }
    if (!password) {
      setError("Password is required");
      return;
    }

    setError(null);
    onSubmit({ email, password });
  }

  return (
    <form onSubmit={handleSubmit}>
      {error && <p role="alert">{error}</p>}

      <label htmlFor="email">Email</label>
      <input
        id="email"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />

      <label htmlFor="password">Password</label>
      <input
        id="password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <button type="submit">Log In</button>
    </form>
  );
}
```

```jsx
// LoginForm.test.jsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import LoginForm from "./LoginForm";

describe("LoginForm", () => {
  it("renders the form fields", () => {
    render(<LoginForm onSubmit={() => {}} />);

    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Log In" })).toBeInTheDocument();
  });

  it("shows an error when email is empty", async () => {
    const user = userEvent.setup();
    render(<LoginForm onSubmit={() => {}} />);

    await user.click(screen.getByRole("button", { name: "Log In" }));

    expect(screen.getByRole("alert")).toHaveTextContent("Email is required");
  });

  it("shows an error when password is empty", async () => {
    const user = userEvent.setup();
    render(<LoginForm onSubmit={() => {}} />);

    await user.type(screen.getByLabelText("Email"), "test@example.com");
    await user.click(screen.getByRole("button", { name: "Log In" }));

    expect(screen.getByRole("alert")).toHaveTextContent("Password is required");
  });

  it("calls onSubmit with email and password when form is valid", async () => {
    const user = userEvent.setup();
    const handleSubmit = vi.fn();
    render(<LoginForm onSubmit={handleSubmit} />);

    await user.type(screen.getByLabelText("Email"), "test@example.com");
    await user.type(screen.getByLabelText("Password"), "password123");
    await user.click(screen.getByRole("button", { name: "Log In" }));

    expect(handleSubmit).toHaveBeenCalledOnce();
    expect(handleSubmit).toHaveBeenCalledWith({
      email: "test@example.com",
      password: "password123",
    });
  });

  it("does not show an error when form is valid", async () => {
    const user = userEvent.setup();
    render(<LoginForm onSubmit={() => {}} />);

    await user.type(screen.getByLabelText("Email"), "test@example.com");
    await user.type(screen.getByLabelText("Password"), "password123");
    await user.click(screen.getByRole("button", { name: "Log In" }));

    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });
});
```

### Testing Lists

```jsx
// TodoList.jsx
function TodoList({ todos, onToggle, onDelete }) {
  if (todos.length === 0) {
    return <p>No tasks yet.</p>;
  }

  return (
    <ul>
      {todos.map((todo) => (
        <li key={todo.id}>
          <input
            type="checkbox"
            checked={todo.completed}
            onChange={() => onToggle(todo.id)}
            aria-label={`Mark "${todo.text}" as ${todo.completed ? "not completed" : "completed"}`}
          />
          <span>{todo.text}</span>
          <button onClick={() => onDelete(todo.id)} aria-label={`Delete "${todo.text}"`}>
            Delete
          </button>
        </li>
      ))}
    </ul>
  );
}
```

```jsx
// TodoList.test.jsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import TodoList from "./TodoList";

const mockTodos = [
  { id: 1, text: "Learn React", completed: false },
  { id: 2, text: "Write tests", completed: true },
  { id: 3, text: "Deploy app", completed: false },
];

describe("TodoList", () => {
  it("shows a message when there are no todos", () => {
    render(<TodoList todos={[]} onToggle={() => {}} onDelete={() => {}} />);

    expect(screen.getByText("No tasks yet.")).toBeInTheDocument();
  });

  it("renders all todos", () => {
    render(<TodoList todos={mockTodos} onToggle={() => {}} onDelete={() => {}} />);

    expect(screen.getByText("Learn React")).toBeInTheDocument();
    expect(screen.getByText("Write tests")).toBeInTheDocument();
    expect(screen.getByText("Deploy app")).toBeInTheDocument();
  });

  it("renders checkboxes with correct checked state", () => {
    render(<TodoList todos={mockTodos} onToggle={() => {}} onDelete={() => {}} />);

    const learnCheckbox = screen.getByRole("checkbox", {
      name: /Learn React/,
    });
    const writeCheckbox = screen.getByRole("checkbox", {
      name: /Write tests/,
    });

    expect(learnCheckbox).not.toBeChecked();
    expect(writeCheckbox).toBeChecked();
  });

  it("calls onToggle when a checkbox is clicked", async () => {
    const user = userEvent.setup();
    const handleToggle = vi.fn();
    render(<TodoList todos={mockTodos} onToggle={handleToggle} onDelete={() => {}} />);

    await user.click(screen.getByRole("checkbox", { name: /Learn React/ }));

    expect(handleToggle).toHaveBeenCalledWith(1);
  });

  it("calls onDelete when a delete button is clicked", async () => {
    const user = userEvent.setup();
    const handleDelete = vi.fn();
    render(<TodoList todos={mockTodos} onToggle={() => {}} onDelete={handleDelete} />);

    await user.click(screen.getByRole("button", { name: /Delete "Write tests"/ }));

    expect(handleDelete).toHaveBeenCalledWith(2);
  });
});
```

---

## Mocking

### Mock Functions

Use `vi.fn()` to create mock functions that track how they were called:

```jsx
const mockFn = vi.fn();

mockFn("hello", 42);

expect(mockFn).toHaveBeenCalled();
expect(mockFn).toHaveBeenCalledOnce();
expect(mockFn).toHaveBeenCalledWith("hello", 42);

// Mock return values
const getId = vi.fn().mockReturnValue(42);
expect(getId()).toBe(42);

// Mock implementation
const fetchUser = vi.fn().mockResolvedValue({ name: "Alice" });
const user = await fetchUser();
expect(user).toEqual({ name: "Alice" });
```

### Mocking API Calls

The most common use of mocking in React tests is replacing `fetch` with a controlled version:

```jsx
// UserProfile.jsx
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadUser() {
      try {
        const response = await fetch(`/api/users/${userId}`);
        if (!response.ok) throw new Error("User not found");
        const data = await response.json();
        setUser(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadUser();
  }, [userId]);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;
  if (!user) return null;

  return (
    <div>
      <h2>{user.name}</h2>
      <p>{user.email}</p>
    </div>
  );
}
```

```jsx
// UserProfile.test.jsx
import { render, screen } from "@testing-library/react";
import { vi, beforeEach, afterEach } from "vitest";
import UserProfile from "./UserProfile";

describe("UserProfile", () => {
  beforeEach(() => {
    // Mock the global fetch
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("shows loading state initially", () => {
    fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ name: "Alice", email: "alice@example.com" }),
    });

    render(<UserProfile userId={1} />);

    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("displays user data after loading", async () => {
    fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ name: "Alice", email: "alice@example.com" }),
    });

    render(<UserProfile userId={1} />);

    expect(await screen.findByText("Alice")).toBeInTheDocument();
    expect(screen.getByText("alice@example.com")).toBeInTheDocument();
  });

  it("displays an error when the fetch fails", async () => {
    fetch.mockResolvedValue({
      ok: false,
      status: 404,
    });

    render(<UserProfile userId={999} />);

    expect(await screen.findByText("Error: User not found")).toBeInTheDocument();
  });

  it("fetches the correct user", async () => {
    fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ name: "Bob", email: "bob@example.com" }),
    });

    render(<UserProfile userId={42} />);

    await screen.findByText("Bob");

    expect(fetch).toHaveBeenCalledWith("/api/users/42");
  });
});
```

### Mocking Modules

Sometimes you need to mock an entire module:

```jsx
// Mock a service module
vi.mock("./userService", () => ({
  getUser: vi.fn(),
  updateUser: vi.fn(),
}));

import { getUser, updateUser } from "./userService";

beforeEach(() => {
  getUser.mockResolvedValue({ id: 1, name: "Alice" });
  updateUser.mockResolvedValue({ id: 1, name: "Alice Updated" });
});
```

### Mocking Timers

For components that use `setTimeout`, `setInterval`, or `Date`:

```jsx
// Debounced search component
function DebouncedSearch({ onSearch }) {
  const [query, setQuery] = useState("");

  useEffect(() => {
    const timer = setTimeout(() => {
      if (query) onSearch(query);
    }, 300);

    return () => clearTimeout(timer);
  }, [query, onSearch]);

  return (
    <input
      value={query}
      onChange={(e) => setQuery(e.target.value)}
      placeholder="Search..."
    />
  );
}
```

```jsx
// DebouncedSearch.test.jsx
import { render, screen, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import DebouncedSearch from "./DebouncedSearch";

describe("DebouncedSearch", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("calls onSearch after the debounce delay", async () => {
    const handleSearch = vi.fn();
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    render(<DebouncedSearch onSearch={handleSearch} />);

    await user.type(screen.getByPlaceholderText("Search..."), "react");

    // Not called yet — debounce is waiting
    expect(handleSearch).not.toHaveBeenCalled();

    // Advance timers past the debounce delay
    act(() => {
      vi.advanceTimersByTime(300);
    });

    expect(handleSearch).toHaveBeenCalledWith("react");
  });

  it("only calls onSearch once for rapid typing", async () => {
    const handleSearch = vi.fn();
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    render(<DebouncedSearch onSearch={handleSearch} />);

    await user.type(screen.getByPlaceholderText("Search..."), "react hooks");

    act(() => {
      vi.advanceTimersByTime(300);
    });

    // Called only once with the final value
    expect(handleSearch).toHaveBeenCalledOnce();
    expect(handleSearch).toHaveBeenCalledWith("react hooks");
  });
});
```

---

## Testing Custom Hooks

Custom hooks cannot be tested directly — they must be called inside a React component. Use `renderHook` from React Testing Library:

```jsx
// hooks/useCounter.js
import { useState, useCallback } from "react";

export function useCounter(initialValue = 0) {
  const [count, setCount] = useState(initialValue);

  const increment = useCallback(() => setCount((c) => c + 1), []);
  const decrement = useCallback(() => setCount((c) => c - 1), []);
  const reset = useCallback(() => setCount(initialValue), [initialValue]);

  return { count, increment, decrement, reset };
}
```

```jsx
// hooks/useCounter.test.js
import { renderHook, act } from "@testing-library/react";
import { useCounter } from "./useCounter";

describe("useCounter", () => {
  it("starts with the initial value", () => {
    const { result } = renderHook(() => useCounter(10));

    expect(result.current.count).toBe(10);
  });

  it("defaults to 0", () => {
    const { result } = renderHook(() => useCounter());

    expect(result.current.count).toBe(0);
  });

  it("increments the count", () => {
    const { result } = renderHook(() => useCounter());

    act(() => {
      result.current.increment();
    });

    expect(result.current.count).toBe(1);
  });

  it("decrements the count", () => {
    const { result } = renderHook(() => useCounter(5));

    act(() => {
      result.current.decrement();
    });

    expect(result.current.count).toBe(4);
  });

  it("resets to the initial value", () => {
    const { result } = renderHook(() => useCounter(10));

    act(() => {
      result.current.increment();
      result.current.increment();
      result.current.reset();
    });

    expect(result.current.count).toBe(10);
  });
});
```

### Testing a useLocalStorage Hook

```jsx
// hooks/useLocalStorage.js
export function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => {
    try {
      const stored = localStorage.getItem(key);
      return stored !== null ? JSON.parse(stored) : initialValue;
    } catch {
      return initialValue;
    }
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue];
}
```

```jsx
// hooks/useLocalStorage.test.js
import { renderHook, act } from "@testing-library/react";
import { beforeEach } from "vitest";
import { useLocalStorage } from "./useLocalStorage";

describe("useLocalStorage", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("returns the initial value when localStorage is empty", () => {
    const { result } = renderHook(() => useLocalStorage("key", "default"));

    expect(result.current[0]).toBe("default");
  });

  it("returns the stored value from localStorage", () => {
    localStorage.setItem("key", JSON.stringify("stored value"));

    const { result } = renderHook(() => useLocalStorage("key", "default"));

    expect(result.current[0]).toBe("stored value");
  });

  it("updates the value and localStorage", () => {
    const { result } = renderHook(() => useLocalStorage("key", "initial"));

    act(() => {
      result.current[1]("updated");
    });

    expect(result.current[0]).toBe("updated");
    expect(JSON.parse(localStorage.getItem("key"))).toBe("updated");
  });

  it("handles objects", () => {
    const { result } = renderHook(() =>
      useLocalStorage("user", { name: "Alice" })
    );

    act(() => {
      result.current[1]({ name: "Bob" });
    });

    expect(result.current[0]).toEqual({ name: "Bob" });
  });
});
```

---

## Testing Components with Context

Components that use Context need the Provider in the test:

```jsx
// ThemeContext.jsx
const ThemeContext = createContext();

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState("light");
  const toggleTheme = () => setTheme((t) => (t === "light" ? "dark" : "light"));
  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  return useContext(ThemeContext);
}
```

```jsx
// ThemeToggle.jsx
function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  return (
    <button onClick={toggleTheme}>
      Current theme: {theme}
    </button>
  );
}
```

```jsx
// ThemeToggle.test.jsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ThemeProvider } from "./ThemeContext";
import ThemeToggle from "./ThemeToggle";

// Helper to render with the provider
function renderWithTheme(component) {
  return render(<ThemeProvider>{component}</ThemeProvider>);
}

describe("ThemeToggle", () => {
  it("shows the current theme", () => {
    renderWithTheme(<ThemeToggle />);

    expect(screen.getByRole("button")).toHaveTextContent("Current theme: light");
  });

  it("toggles the theme when clicked", async () => {
    const user = userEvent.setup();
    renderWithTheme(<ThemeToggle />);

    await user.click(screen.getByRole("button"));

    expect(screen.getByRole("button")).toHaveTextContent("Current theme: dark");
  });
});
```

### Custom Render Function

For components that need multiple providers, create a custom render function:

```jsx
// test/utils.jsx
import { render } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { ThemeProvider } from "../ThemeContext";
import { AuthProvider } from "../AuthContext";

export function renderWithProviders(ui, options = {}) {
  function Wrapper({ children }) {
    return (
      <BrowserRouter>
        <AuthProvider>
          <ThemeProvider>{children}</ThemeProvider>
        </AuthProvider>
      </BrowserRouter>
    );
  }

  return render(ui, { wrapper: Wrapper, ...options });
}

// Re-export everything from testing library
export * from "@testing-library/react";
export { default as userEvent } from "@testing-library/user-event";
```

```jsx
// Usage in tests
import { renderWithProviders, screen, userEvent } from "../test/utils";

it("renders the dashboard", () => {
  renderWithProviders(<Dashboard />);
  expect(screen.getByText("Dashboard")).toBeInTheDocument();
});
```

---

## Testing Components with React Router

```jsx
// test helper for router
import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

function renderWithRouter(ui, { route = "/" } = {}) {
  return render(
    <MemoryRouter initialEntries={[route]}>
      {ui}
    </MemoryRouter>
  );
}
```

```jsx
// Navigation.test.jsx
import { renderWithRouter } from "../test/utils";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "./App";

describe("Navigation", () => {
  it("renders the home page by default", () => {
    renderWithRouter(<App />);

    expect(screen.getByText("Welcome to our app")).toBeInTheDocument();
  });

  it("navigates to the about page", async () => {
    const user = userEvent.setup();
    renderWithRouter(<App />);

    await user.click(screen.getByRole("link", { name: "About" }));

    expect(screen.getByText("About Us")).toBeInTheDocument();
  });

  it("shows 404 for unknown routes", () => {
    renderWithRouter(<App />, { route: "/unknown-page" });

    expect(screen.getByText("Page Not Found")).toBeInTheDocument();
  });
});
```

`MemoryRouter` lets you control the initial route without needing a real browser URL.

---

## What to Test (and What Not to Test)

### DO Test

- **User-visible behavior** — What the user sees, clicks, and types
- **Component output** — Given these props, what renders?
- **User interactions** — When I click this button, what happens?
- **Edge cases** — Empty lists, error states, loading states, boundary values
- **Form validation** — Required fields, invalid input, error messages
- **Conditional rendering** — Elements that appear/disappear based on state
- **Callback props** — onSubmit is called with the right data

### DO NOT Test

- **Implementation details** — State variable names, internal method calls, component structure
- **Styling** — CSS class names, inline styles (unless they affect functionality)
- **Third-party libraries** — React Router, Zustand, etc. are already tested by their maintainers
- **Trivial rendering** — A component that just returns `<p>{props.text}</p>` does not need a test
- **Constant values** — Testing that a heading says "About" when it is hardcoded is not useful

### The Golden Rule

> **Test behavior, not implementation.**

```jsx
// WRONG — tests implementation details
it("sets isOpen state to true", () => {
  const { result } = renderHook(() => useToggle());

  act(() => result.current.toggle());

  // Testing internal state name — breaks if you rename the state
  expect(result.current.isOpen).toBe(true);
});

// CORRECT — tests behavior
it("shows the dropdown when the button is clicked", async () => {
  const user = userEvent.setup();
  render(<Dropdown items={items} />);

  await user.click(screen.getByRole("button", { name: "Options" }));

  expect(screen.getByRole("menu")).toBeInTheDocument();
});
```

---

## Organizing Tests

### File Naming Conventions

```
src/
  components/
    Button.jsx
    Button.test.jsx        ← co-located test
  hooks/
    useCounter.js
    useCounter.test.js     ← co-located test
  utils/
    formatCurrency.js
    formatCurrency.test.js ← co-located test
```

Co-locate tests with the code they test. When you delete a component, the test goes with it.

### Test Structure

Follow the **Arrange-Act-Assert** pattern:

```jsx
it("adds item to cart when button is clicked", async () => {
  // Arrange — set up the test
  const user = userEvent.setup();
  const handleAdd = vi.fn();
  render(<ProductCard product={mockProduct} onAddToCart={handleAdd} />);

  // Act — perform the action
  await user.click(screen.getByRole("button", { name: "Add to Cart" }));

  // Assert — verify the result
  expect(handleAdd).toHaveBeenCalledWith(mockProduct);
});
```

### Shared Test Data

```jsx
// test/fixtures.js
export const mockUser = {
  id: 1,
  name: "Alice Johnson",
  email: "alice@example.com",
  role: "admin",
};

export const mockProducts = [
  { id: 1, name: "React Book", price: 29.99, inStock: true },
  { id: 2, name: "JavaScript Guide", price: 24.99, inStock: false },
  { id: 3, name: "CSS Handbook", price: 19.99, inStock: true },
];

export function createMockTodo(overrides = {}) {
  return {
    id: Math.random(),
    text: "Test todo",
    completed: false,
    createdAt: new Date().toISOString(),
    ...overrides,
  };
}
```

---

## Mini Project: Testing a Contact Form

Let us test a complete contact form with validation, submission, and success/error states.

```jsx
// ContactForm.jsx
import { useState } from "react";

function ContactForm({ onSubmit }) {
  const [form, setForm] = useState({ name: "", email: "", message: "" });
  const [errors, setErrors] = useState({});
  const [status, setStatus] = useState("idle"); // idle | submitting | success | error

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: null }));
    }
  }

  function validate() {
    const newErrors = {};
    if (!form.name.trim()) newErrors.name = "Name is required";
    if (!form.email.trim()) newErrors.email = "Email is required";
    else if (!form.email.includes("@")) newErrors.email = "Enter a valid email";
    if (!form.message.trim()) newErrors.message = "Message is required";
    else if (form.message.trim().length < 10) newErrors.message = "Message must be at least 10 characters";
    return newErrors;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const newErrors = validate();

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setStatus("submitting");

    try {
      await onSubmit(form);
      setStatus("success");
      setForm({ name: "", email: "", message: "" });
    } catch (err) {
      setStatus("error");
    }
  }

  if (status === "success") {
    return (
      <div role="status">
        <h2>Thank you!</h2>
        <p>Your message has been sent. We will get back to you soon.</p>
        <button onClick={() => setStatus("idle")}>Send another message</button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} noValidate>
      <h2>Contact Us</h2>

      {status === "error" && (
        <p role="alert" style={{ color: "red" }}>
          Failed to send message. Please try again.
        </p>
      )}

      <div>
        <label htmlFor="name">Name</label>
        <input
          id="name"
          name="name"
          value={form.name}
          onChange={handleChange}
          aria-invalid={errors.name ? "true" : undefined}
          aria-describedby={errors.name ? "name-error" : undefined}
          disabled={status === "submitting"}
        />
        {errors.name && <p id="name-error" role="alert">{errors.name}</p>}
      </div>

      <div>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          name="email"
          type="email"
          value={form.email}
          onChange={handleChange}
          aria-invalid={errors.email ? "true" : undefined}
          aria-describedby={errors.email ? "email-error" : undefined}
          disabled={status === "submitting"}
        />
        {errors.email && <p id="email-error" role="alert">{errors.email}</p>}
      </div>

      <div>
        <label htmlFor="message">Message</label>
        <textarea
          id="message"
          name="message"
          value={form.message}
          onChange={handleChange}
          aria-invalid={errors.message ? "true" : undefined}
          aria-describedby={errors.message ? "message-error" : undefined}
          disabled={status === "submitting"}
        />
        {errors.message && <p id="message-error" role="alert">{errors.message}</p>}
      </div>

      <button type="submit" disabled={status === "submitting"}>
        {status === "submitting" ? "Sending..." : "Send Message"}
      </button>
    </form>
  );
}

export default ContactForm;
```

```jsx
// ContactForm.test.jsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import ContactForm from "./ContactForm";

describe("ContactForm", () => {
  function setup() {
    const handleSubmit = vi.fn();
    const user = userEvent.setup();
    render(<ContactForm onSubmit={handleSubmit} />);
    return { handleSubmit, user };
  }

  async function fillForm(user, data = {}) {
    const {
      name = "Alice Smith",
      email = "alice@example.com",
      message = "This is a test message for the form.",
    } = data;

    if (name) await user.type(screen.getByLabelText("Name"), name);
    if (email) await user.type(screen.getByLabelText("Email"), email);
    if (message) await user.type(screen.getByLabelText("Message"), message);
  }

  // --- Rendering ---

  it("renders the form with all fields", () => {
    setup();

    expect(screen.getByLabelText("Name")).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText("Message")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Send Message" })).toBeInTheDocument();
  });

  // --- Validation ---

  it("shows error when name is empty", async () => {
    const { user } = setup();

    await user.click(screen.getByRole("button", { name: "Send Message" }));

    expect(screen.getByText("Name is required")).toBeInTheDocument();
  });

  it("shows error for invalid email", async () => {
    const { user } = setup();

    await user.type(screen.getByLabelText("Name"), "Alice");
    await user.type(screen.getByLabelText("Email"), "not-an-email");
    await user.type(screen.getByLabelText("Message"), "Hello, this is a test message");
    await user.click(screen.getByRole("button", { name: "Send Message" }));

    expect(screen.getByText("Enter a valid email")).toBeInTheDocument();
  });

  it("shows error when message is too short", async () => {
    const { user } = setup();

    await user.type(screen.getByLabelText("Name"), "Alice");
    await user.type(screen.getByLabelText("Email"), "alice@test.com");
    await user.type(screen.getByLabelText("Message"), "Hi");
    await user.click(screen.getByRole("button", { name: "Send Message" }));

    expect(screen.getByText("Message must be at least 10 characters")).toBeInTheDocument();
  });

  it("clears field error when user starts typing", async () => {
    const { user } = setup();

    // Trigger validation errors
    await user.click(screen.getByRole("button", { name: "Send Message" }));
    expect(screen.getByText("Name is required")).toBeInTheDocument();

    // Start typing in the name field
    await user.type(screen.getByLabelText("Name"), "A");

    // Name error should be cleared
    expect(screen.queryByText("Name is required")).not.toBeInTheDocument();
  });

  // --- Submission ---

  it("calls onSubmit with form data when valid", async () => {
    const { handleSubmit, user } = setup();
    handleSubmit.mockResolvedValue(undefined);

    await fillForm(user);
    await user.click(screen.getByRole("button", { name: "Send Message" }));

    expect(handleSubmit).toHaveBeenCalledWith({
      name: "Alice Smith",
      email: "alice@example.com",
      message: "This is a test message for the form.",
    });
  });

  it("does not call onSubmit when form is invalid", async () => {
    const { handleSubmit, user } = setup();

    await user.click(screen.getByRole("button", { name: "Send Message" }));

    expect(handleSubmit).not.toHaveBeenCalled();
  });

  it("disables the form while submitting", async () => {
    const { handleSubmit, user } = setup();
    // Create a promise that does not resolve immediately
    handleSubmit.mockReturnValue(new Promise(() => {}));

    await fillForm(user);
    await user.click(screen.getByRole("button", { name: "Send Message" }));

    expect(screen.getByRole("button", { name: "Sending..." })).toBeDisabled();
    expect(screen.getByLabelText("Name")).toBeDisabled();
    expect(screen.getByLabelText("Email")).toBeDisabled();
    expect(screen.getByLabelText("Message")).toBeDisabled();
  });

  // --- Success ---

  it("shows success message after successful submission", async () => {
    const { handleSubmit, user } = setup();
    handleSubmit.mockResolvedValue(undefined);

    await fillForm(user);
    await user.click(screen.getByRole("button", { name: "Send Message" }));

    expect(await screen.findByText("Thank you!")).toBeInTheDocument();
    expect(screen.getByText(/Your message has been sent/)).toBeInTheDocument();
  });

  it("allows sending another message after success", async () => {
    const { handleSubmit, user } = setup();
    handleSubmit.mockResolvedValue(undefined);

    await fillForm(user);
    await user.click(screen.getByRole("button", { name: "Send Message" }));

    await user.click(screen.getByRole("button", { name: "Send another message" }));

    expect(screen.getByLabelText("Name")).toBeInTheDocument();
    expect(screen.getByLabelText("Name")).toHaveValue("");
  });

  // --- Error ---

  it("shows error message when submission fails", async () => {
    const { handleSubmit, user } = setup();
    handleSubmit.mockRejectedValue(new Error("Network error"));

    await fillForm(user);
    await user.click(screen.getByRole("button", { name: "Send Message" }));

    expect(await screen.findByText(/Failed to send message/)).toBeInTheDocument();
  });
});
```

This test suite demonstrates:

- **Setup helper** — reduces duplication across tests
- **Form fill helper** — reusable function for filling the form
- **Rendering tests** — verify the form renders correctly
- **Validation tests** — empty fields, invalid email, short message, error clearing
- **Submission tests** — callback with correct data, not called when invalid
- **Loading state** — disabled inputs and button text change
- **Success flow** — success message, send another
- **Error flow** — error message on rejection
- **Accessible queries** — `getByLabelText`, `getByRole`, `getByText`

---

## Common Mistakes

### Mistake 1: Testing Implementation Details

```jsx
// WRONG — testing internal state
it("sets loading to true", () => {
  const { result } = renderHook(() => useFetch("/api/data"));
  expect(result.current.loading).toBe(true);
});

// CORRECT — testing what the user sees
it("shows a loading indicator", () => {
  render(<UserList />);
  expect(screen.getByText("Loading...")).toBeInTheDocument();
});
```

### Mistake 2: Using getByTestId as the Default Query

```jsx
// WRONG — uses test IDs when accessible queries work
<button data-testid="save-btn">Save</button>
screen.getByTestId("save-btn");

// CORRECT — use role-based queries
screen.getByRole("button", { name: "Save" });
```

### Mistake 3: Not Awaiting userEvent

```jsx
// WRONG — userEvent methods are async
user.click(button);
expect(result).toBeInTheDocument(); // Might fail — click has not happened yet

// CORRECT — await every interaction
await user.click(button);
expect(result).toBeInTheDocument();
```

### Mistake 4: Snapshot Testing as the Primary Strategy

```jsx
// WRONG — snapshot tests are brittle and tell you nothing about behavior
it("renders correctly", () => {
  const { container } = render(<UserProfile user={mockUser} />);
  expect(container).toMatchSnapshot();
});

// CORRECT — test specific behavior
it("displays the user's name and email", () => {
  render(<UserProfile user={mockUser} />);
  expect(screen.getByText("Alice Johnson")).toBeInTheDocument();
  expect(screen.getByText("alice@example.com")).toBeInTheDocument();
});
```

Snapshot tests fail whenever anything in the rendered output changes — even whitespace. They produce noise, get updated blindly, and do not actually verify behavior.

### Mistake 5: Not Cleaning Up Between Tests

```jsx
// WRONG — tests share state and affect each other
let user;

beforeAll(() => {
  user = { name: "Alice" };
});

it("modifies user", () => {
  user.name = "Bob";
  expect(user.name).toBe("Bob");
});

it("expects original user", () => {
  expect(user.name).toBe("Alice"); // FAILS — previous test modified it
});

// CORRECT — reset state in beforeEach
beforeEach(() => {
  user = { name: "Alice" };
});
```

---

## Best Practices

1. **Test behavior, not implementation** — Test what the user sees and does, not internal state, method names, or component structure. If you refactor the implementation and the behavior is unchanged, no tests should break.

2. **Use accessible queries** — Prefer `getByRole`, `getByLabelText`, and `getByText` over `getByTestId`. This encourages accessible markup and tests that mirror real user behavior.

3. **One assertion focus per test** — Each test should verify one behavior. Multiple related assertions are fine (checking name AND email), but testing unrelated things in one test makes failures hard to diagnose.

4. **Use userEvent, not fireEvent** — `userEvent` simulates real user interactions more accurately (typing triggers focus, keydown, keypress, input, and keyup events, not just a change event).

5. **Mock at the boundary** — Mock API calls (fetch) and external services, not internal functions. This keeps tests resilient to refactoring.

6. **Create setup helpers** — Extract common render logic, provider wrappers, and form fill functions to reduce duplication.

7. **Keep tests fast** — Use `vi.useFakeTimers()` for debounce/timer tests. Mock fetch instead of making real network requests. Fast tests encourage running them often.

8. **Test the unhappy paths** — Error states, empty lists, failed submissions, and edge cases are where bugs live. Do not only test the happy path.

---

## Summary

In this chapter, you learned:

- **Vitest** is a fast test runner for Vite projects with a Jest-compatible API
- **React Testing Library** renders components and provides queries that mirror user behavior (`getByRole`, `getByLabelText`, `getByText`)
- **userEvent** simulates realistic user interactions (clicks, typing, keyboard events)
- **Query variants** — `getBy` (must exist), `queryBy` (might not exist), `findBy` (appears async)
- **Component tests** verify rendering, conditional display, user interactions, form validation, and callback props
- **Mocking** — `vi.fn()` for functions, `vi.stubGlobal("fetch")` for API calls, `vi.mock()` for modules, `vi.useFakeTimers()` for timers
- **Custom hooks** are tested with `renderHook` and `act`
- **Context and Router** — provide wrappers in tests using custom render functions
- **Test behavior, not implementation** — tests should not break when you refactor internals
- **The testing priority** — accessible queries first, test IDs as a last resort

---

## Interview Questions

1. **What is React Testing Library and how does it differ from Enzyme?**

   React Testing Library tests components from the user's perspective — finding elements by their role, label, or text content, and simulating real user interactions. It discourages testing implementation details. Enzyme (now largely deprecated) gave access to component internals — state, props, lifecycle methods, and shallow rendering. RTL's philosophy is that tests should resemble how users interact with the app, making tests more resilient to refactoring.

2. **What is the difference between getBy, queryBy, and findBy queries?**

   `getBy` returns the element or throws if not found — use it for elements that should exist. `queryBy` returns the element or `null` — use it to assert something does NOT exist (`expect(queryByText("Error")).not.toBeInTheDocument()`). `findBy` returns a Promise that resolves when the element appears — use it for elements that appear after async operations (API calls, state updates). Each has an `All` variant for multiple matches.

3. **Why should you prefer getByRole over getByTestId?**

   `getByRole` queries elements the way screen readers do, which tests accessibility alongside functionality. If `getByRole("button", { name: "Save" })` fails, it means a screen reader user also cannot find that button. `getByTestId` only tests that an element exists — it says nothing about accessibility. Using accessible queries encourages writing accessible markup and produces more meaningful tests.

4. **How do you test a component that fetches data from an API?**

   Mock the `fetch` function using `vi.stubGlobal("fetch", vi.fn())` and configure it to return controlled responses. Test the loading state (check for "Loading..." text), the success state (use `findByText` to wait for data to appear), and the error state (mock a failed response and check for the error message). Always clean up mocks in `afterEach` with `vi.restoreAllMocks()`.

5. **What does "test behavior, not implementation" mean?**

   It means tests should verify what the user sees and experiences, not how the code works internally. Test that clicking a button shows a success message, not that `setState` was called with a specific value. Test that a list renders 5 items, not that the component's `items` state has length 5. This makes tests resilient to refactoring — you can rewrite the component's internals without breaking tests, as long as the behavior stays the same.

---

## Practice Exercises

### Exercise 1: Test a Counter Component

Build and test a counter component with increment, decrement, and reset buttons. Test the initial render, each button's behavior, and that the count cannot go below zero. Add a "count by" input that changes the increment/decrement step — test that it works with different step values.

### Exercise 2: Test a Search with Filtering

Build and test a product search component. It should render a list of products, filter them as the user types in a search input, and show "No products found" when nothing matches. Test the initial render, filtering behavior, case-insensitive search, and the empty state.

### Exercise 3: Test Async Data Loading

Build and test a component that fetches and displays a list of posts. Test the loading state, successful data display, error state, empty data state, and the retry button. Mock `fetch` for each scenario. Test that the correct API URL is called.

### Exercise 4: Test a Multi-Step Form

Build and test a two-step form wizard. Step 1 collects name and email, step 2 collects address. Test navigation between steps (Next/Back buttons), that data persists when going back, validation on each step, and that the final submission includes all data from both steps.

---

## What Is Next?

In Chapter 22, we will explore **Debugging React Applications** — how to use React DevTools, browser DevTools, and systematic debugging strategies to find and fix bugs efficiently in your React applications.
