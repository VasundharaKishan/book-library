# Chapter 18: State Management at Scale

## Learning Goals

By the end of this chapter, you will be able to:

- Identify when React's built-in state tools are no longer sufficient
- Understand the spectrum of state management options
- Categorize state by type (local, shared, server, URL)
- Use Zustand for lightweight global state management
- Understand Redux Toolkit's core concepts (store, slices, actions, selectors)
- Build a feature using Redux Toolkit with createSlice and configureStore
- Compare Zustand, Redux Toolkit, and Context for different use cases
- Apply the right state management tool for the right problem
- Avoid common over-engineering mistakes

---

## When Context Is Not Enough

In Chapters 13 and 14, you learned to use Context with useReducer for sharing state across components. This works well for many cases — theme preferences, authentication, a shopping cart with a few dozen items. But as applications grow, you start running into problems.

### The Scaling Problems with Context

**Problem 1: Performance — Any Change Re-Renders All Consumers**

When a Context value changes, every component that calls `useContext` for that Context re-renders — even if it only uses a small piece of the value.

```jsx
const AppContext = createContext();

function AppProvider({ children }) {
  const [user, setUser] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [theme, setTheme] = useState("light");
  const [cart, setCart] = useState([]);

  return (
    <AppContext.Provider value={{ user, notifications, theme, cart, setUser, setNotifications, setTheme, setCart }}>
      {children}
    </AppContext.Provider>
  );
}
```

When a new notification arrives, the `Header` component that only uses `user` re-renders. The `ProductCard` that only uses `cart` re-renders. Every consumer re-renders, regardless of which part of the value changed.

We discussed mitigations in Chapter 13 — splitting contexts, memoizing values, separating state from dispatch. These help, but they add complexity and have limits. With 10 different pieces of global state, managing 10 separate contexts becomes unwieldy.

**Problem 2: No Built-In DevTools**

React DevTools show Context values, but there is no way to see a history of state changes, time-travel through previous states, or replay actions. For complex state, this makes debugging painful.

**Problem 3: No Middleware**

Context has no concept of middleware — code that runs between an action being dispatched and the state being updated. Middleware is useful for logging, analytics, async operations, and error tracking.

**Problem 4: Boilerplate for Complex State**

As you add more features, the combination of Context + useReducer requires significant boilerplate: a context file, a provider component, a reducer function, action types, a custom hook — for every piece of shared state.

### When to Reach for External State Management

You need external state management when:

- Multiple unrelated features share state (beyond 3-4 contexts)
- You need state change history and time-travel debugging
- You need middleware for logging, analytics, or async flows
- Performance is degrading due to unnecessary re-renders
- Your team needs strict, predictable state update patterns
- The application has complex state interactions between features

You do **not** need external state management when:

- State is local to a component or a small component tree
- You have 1-3 pieces of shared state
- Context with split providers handles your needs
- The application is small to medium in size

Most applications fall somewhere in between. The key is choosing the right tool for each type of state.

---

## Types of State

Before choosing a state management solution, classify your state:

### Local State (Component State)

State that belongs to a single component and does not need to be shared.

**Examples:** Form input values, toggle visibility, dropdown open/closed, animation state

**Tool:** `useState` or `useReducer`

```jsx
function SearchBar() {
  const [query, setQuery] = useState(""); // Local — only this component needs it
  return <input value={query} onChange={e => setQuery(e.target.value)} />;
}
```

### Shared State (Cross-Component State)

State that multiple components need to read or update.

**Examples:** Current user, theme preference, shopping cart, notification list

**Tool:** Context (for simple cases), Zustand or Redux (for complex cases)

### Server State

Data that originates on the server and is cached on the client.

**Examples:** API responses, user profiles, product listings, comments

**Tool:** React Query (TanStack Query) or SWR — specialized libraries for server state that handle caching, refetching, pagination, and synchronization. We will discuss these briefly later.

### URL State

State that lives in the URL — route parameters, query strings, hash.

**Examples:** Current page, search filters, sort order, selected tab

**Tool:** React Router (`useParams`, `useSearchParams`)

### The Common Mistake

The most common mistake is putting everything in global state. If a form's input value is only used by that form, it does not belong in Redux or Zustand. If data comes from an API and just needs caching, it does not belong in Redux either — it belongs in a server state library.

**Rule of thumb:** Keep state as local as possible. Only lift it to shared/global state when multiple unrelated components need it.

---

## Zustand: Lightweight State Management

Zustand (German for "state") is a small, fast state management library with a minimal API. It is the most popular alternative to Redux for new React projects.

### Installation

```bash
npm install zustand
```

### Creating a Store

```jsx
import { create } from "zustand";

const useCounterStore = create((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set((state) => ({ count: state.count - 1 })),
  reset: () => set({ count: 0 }),
}));
```

That is it. No Provider, no Context, no boilerplate. The `create` function takes a callback that receives a `set` function. You return an object with your state and actions.

### Using the Store in Components

```jsx
function Counter() {
  const count = useCounterStore((state) => state.count);
  const increment = useCounterStore((state) => state.increment);
  const decrement = useCounterStore((state) => state.decrement);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={increment}>+</button>
      <button onClick={decrement}>-</button>
    </div>
  );
}
```

The selector function `(state) => state.count` tells Zustand which part of the state this component cares about. The component only re-renders when `count` changes — not when other parts of the store change. This solves the Context re-rendering problem.

### A Practical Example: Shopping Cart

```jsx
// stores/cartStore.js
import { create } from "zustand";

const useCartStore = create((set, get) => ({
  items: [],

  addItem: (product) => {
    set((state) => {
      const existing = state.items.find((item) => item.id === product.id);

      if (existing) {
        return {
          items: state.items.map((item) =>
            item.id === product.id
              ? { ...item, quantity: item.quantity + 1 }
              : item
          ),
        };
      }

      return {
        items: [...state.items, { ...product, quantity: 1 }],
      };
    });
  },

  removeItem: (productId) => {
    set((state) => ({
      items: state.items.filter((item) => item.id !== productId),
    }));
  },

  updateQuantity: (productId, quantity) => {
    set((state) => ({
      items: quantity <= 0
        ? state.items.filter((item) => item.id !== productId)
        : state.items.map((item) =>
            item.id === productId ? { ...item, quantity } : item
          ),
    }));
  },

  clearCart: () => set({ items: [] }),

  // Derived values using get()
  getTotalItems: () => {
    return get().items.reduce((total, item) => total + item.quantity, 0);
  },

  getTotalPrice: () => {
    return get().items.reduce(
      (total, item) => total + item.price * item.quantity,
      0
    );
  },
}));

export default useCartStore;
```

```jsx
// components/ProductCard.jsx
import useCartStore from "../stores/cartStore";

function ProductCard({ product }) {
  const addItem = useCartStore((state) => state.addItem);

  return (
    <div>
      <h3>{product.name}</h3>
      <p>${product.price}</p>
      <button onClick={() => addItem(product)}>Add to Cart</button>
    </div>
  );
}
```

```jsx
// components/CartIcon.jsx
import useCartStore from "../stores/cartStore";

function CartIcon() {
  const totalItems = useCartStore((state) => state.getTotalItems());

  return (
    <div>
      🛒 Cart ({totalItems})
    </div>
  );
}
```

```jsx
// components/CartPage.jsx
import useCartStore from "../stores/cartStore";

function CartPage() {
  const items = useCartStore((state) => state.items);
  const updateQuantity = useCartStore((state) => state.updateQuantity);
  const removeItem = useCartStore((state) => state.removeItem);
  const clearCart = useCartStore((state) => state.clearCart);
  const totalPrice = useCartStore((state) => state.getTotalPrice());

  if (items.length === 0) {
    return <p>Your cart is empty.</p>;
  }

  return (
    <div>
      <h2>Shopping Cart</h2>

      {items.map((item) => (
        <div key={item.id} style={{ display: "flex", gap: "1rem", padding: "1rem", borderBottom: "1px solid #eee" }}>
          <div style={{ flex: 1 }}>
            <h3>{item.name}</h3>
            <p>${item.price}</p>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <button onClick={() => updateQuantity(item.id, item.quantity - 1)}>
              -
            </button>
            <span>{item.quantity}</span>
            <button onClick={() => updateQuantity(item.id, item.quantity + 1)}>
              +
            </button>
          </div>

          <button onClick={() => removeItem(item.id)}>Remove</button>
        </div>
      ))}

      <div style={{ marginTop: "1rem", fontWeight: "bold" }}>
        Total: ${totalPrice.toFixed(2)}
      </div>

      <div style={{ marginTop: "1rem", display: "flex", gap: "1rem" }}>
        <button onClick={clearCart}>Clear Cart</button>
        <button>Checkout</button>
      </div>
    </div>
  );
}
```

### Zustand with Persistence

Zustand has built-in middleware for persisting state to localStorage:

```jsx
import { create } from "zustand";
import { persist } from "zustand/middleware";

const useCartStore = create(
  persist(
    (set, get) => ({
      items: [],
      addItem: (product) => { /* ... */ },
      removeItem: (productId) => { /* ... */ },
      clearCart: () => set({ items: [] }),
    }),
    {
      name: "shopping-cart", // localStorage key
    }
  )
);
```

Now the cart survives page refreshes and browser restarts — automatically.

### Zustand with Async Actions

```jsx
const useProductStore = create((set) => ({
  products: [],
  loading: false,
  error: null,

  fetchProducts: async () => {
    set({ loading: true, error: null });

    try {
      const response = await fetch("/api/products");
      if (!response.ok) throw new Error("Failed to fetch");
      const data = await response.json();
      set({ products: data, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },
}));

// In a component
function ProductList() {
  const { products, loading, error, fetchProducts } = useProductStore();

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <ul>
      {products.map((p) => (
        <li key={p.id}>{p.name}</li>
      ))}
    </ul>
  );
}
```

Async actions in Zustand are just regular async functions — no thunks, no sagas, no extra concepts.

### Zustand with Multiple Stores

Unlike Redux (which uses a single store), Zustand encourages multiple small stores organized by feature:

```jsx
// stores/authStore.js
export const useAuthStore = create((set) => ({
  user: null,
  token: null,
  login: async (email, password) => { /* ... */ },
  logout: () => set({ user: null, token: null }),
}));

// stores/cartStore.js
export const useCartStore = create((set) => ({
  items: [],
  addItem: (product) => { /* ... */ },
  // ...
}));

// stores/notificationStore.js
export const useNotificationStore = create((set) => ({
  notifications: [],
  addNotification: (message, type) => { /* ... */ },
  dismiss: (id) => { /* ... */ },
}));
```

Each store is independent. Components subscribe to only the stores they need.

### Zustand Best Practices

```jsx
// 1. Use selectors to prevent unnecessary re-renders
// WRONG — subscribes to the entire store
const state = useCartStore();

// CORRECT — subscribes only to items
const items = useCartStore((state) => state.items);

// 2. Select multiple values with shallow comparison
import { useShallow } from "zustand/react/shallow";

const { items, totalPrice } = useCartStore(
  useShallow((state) => ({
    items: state.items,
    totalPrice: state.getTotalPrice(),
  }))
);

// 3. Access state outside React components
// Zustand stores work outside React too
const currentItems = useCartStore.getState().items;
useCartStore.getState().addItem(product);
```

---

## Redux Toolkit: Predictable State Container

Redux has been the most widely used state management library in the React ecosystem for years. **Redux Toolkit (RTK)** is the official, recommended way to write Redux — it eliminates most of the boilerplate that made original Redux verbose.

### Core Concepts

**Store** — A single JavaScript object that holds your entire application state.

**Slice** — A collection of reducer logic and actions for a single feature. Each slice owns a portion of the store.

**Action** — A plain object describing what happened: `{ type: "cart/addItem", payload: product }`.

**Reducer** — A pure function that takes the current state and an action, and returns the next state.

**Dispatch** — The function you call to send an action to the store.

**Selector** — A function that extracts a specific piece of data from the store.

### Installation

```bash
npm install @reduxjs/toolkit react-redux
```

### Creating a Slice

```jsx
// features/counter/counterSlice.js
import { createSlice } from "@reduxjs/toolkit";

const counterSlice = createSlice({
  name: "counter",
  initialState: {
    value: 0,
  },
  reducers: {
    increment: (state) => {
      state.value += 1; // RTK uses Immer — mutating syntax is safe
    },
    decrement: (state) => {
      state.value -= 1;
    },
    incrementByAmount: (state, action) => {
      state.value += action.payload;
    },
    reset: (state) => {
      state.value = 0;
    },
  },
});

export const { increment, decrement, incrementByAmount, reset } = counterSlice.actions;
export default counterSlice.reducer;
```

A key feature of Redux Toolkit: you can write "mutating" code like `state.value += 1`. Under the hood, RTK uses a library called **Immer** that converts these mutations into immutable updates. You are not actually mutating state — Immer creates a new state object. This eliminates the spread-operator gymnastics of traditional Redux.

### Configuring the Store

```jsx
// store.js
import { configureStore } from "@reduxjs/toolkit";
import counterReducer from "./features/counter/counterSlice";
import cartReducer from "./features/cart/cartSlice";
import authReducer from "./features/auth/authSlice";

const store = configureStore({
  reducer: {
    counter: counterReducer,
    cart: cartReducer,
    auth: authReducer,
  },
});

export default store;
```

### Providing the Store

```jsx
// main.jsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Provider } from "react-redux";
import store from "./store";
import App from "./App";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </StrictMode>
);
```

### Using Redux in Components

```jsx
import { useSelector, useDispatch } from "react-redux";
import { increment, decrement, reset } from "./counterSlice";

function Counter() {
  const count = useSelector((state) => state.counter.value);
  const dispatch = useDispatch();

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => dispatch(increment())}>+</button>
      <button onClick={() => dispatch(decrement())}>-</button>
      <button onClick={() => dispatch(reset())}>Reset</button>
    </div>
  );
}
```

- `useSelector` reads data from the store. Like Zustand selectors, the component only re-renders when the selected value changes.
- `useDispatch` returns the dispatch function. You call `dispatch(actionCreator())` to update state.

### A Practical Example: Todo App with Redux Toolkit

```jsx
// features/todos/todosSlice.js
import { createSlice } from "@reduxjs/toolkit";

const todosSlice = createSlice({
  name: "todos",
  initialState: {
    items: [],
    filter: "all", // all | active | completed
  },
  reducers: {
    addTodo: (state, action) => {
      state.items.push({
        id: Date.now(),
        text: action.payload,
        completed: false,
        createdAt: new Date().toISOString(),
      });
    },

    toggleTodo: (state, action) => {
      const todo = state.items.find((t) => t.id === action.payload);
      if (todo) {
        todo.completed = !todo.completed;
      }
    },

    deleteTodo: (state, action) => {
      state.items = state.items.filter((t) => t.id !== action.payload);
    },

    editTodo: (state, action) => {
      const { id, text } = action.payload;
      const todo = state.items.find((t) => t.id === id);
      if (todo) {
        todo.text = text;
      }
    },

    setFilter: (state, action) => {
      state.filter = action.payload;
    },

    clearCompleted: (state) => {
      state.items = state.items.filter((t) => !t.completed);
    },
  },
});

export const {
  addTodo,
  toggleTodo,
  deleteTodo,
  editTodo,
  setFilter,
  clearCompleted,
} = todosSlice.actions;

export default todosSlice.reducer;
```

### Selectors

Selectors extract and derive data from the store. Define them alongside your slice:

```jsx
// features/todos/todosSlice.js (continued)

// Basic selectors
export const selectAllTodos = (state) => state.todos.items;
export const selectFilter = (state) => state.todos.filter;

// Derived selectors
export const selectFilteredTodos = (state) => {
  const items = state.todos.items;
  const filter = state.todos.filter;

  switch (filter) {
    case "active":
      return items.filter((t) => !t.completed);
    case "completed":
      return items.filter((t) => t.completed);
    default:
      return items;
  }
};

export const selectTodoStats = (state) => {
  const items = state.todos.items;
  return {
    total: items.length,
    active: items.filter((t) => !t.completed).length,
    completed: items.filter((t) => t.completed).length,
  };
};
```

```jsx
// components/TodoList.jsx
import { useSelector, useDispatch } from "react-redux";
import {
  toggleTodo,
  deleteTodo,
  selectFilteredTodos,
} from "../features/todos/todosSlice";

function TodoList() {
  const todos = useSelector(selectFilteredTodos);
  const dispatch = useDispatch();

  if (todos.length === 0) {
    return <p>No todos to show.</p>;
  }

  return (
    <ul>
      {todos.map((todo) => (
        <li
          key={todo.id}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "0.75rem",
            padding: "0.75rem 0",
            borderBottom: "1px solid #eee",
          }}
        >
          <input
            type="checkbox"
            checked={todo.completed}
            onChange={() => dispatch(toggleTodo(todo.id))}
          />
          <span
            style={{
              flex: 1,
              textDecoration: todo.completed ? "line-through" : "none",
              color: todo.completed ? "#999" : "inherit",
            }}
          >
            {todo.text}
          </span>
          <button onClick={() => dispatch(deleteTodo(todo.id))}>Delete</button>
        </li>
      ))}
    </ul>
  );
}
```

```jsx
// components/AddTodo.jsx
import { useState } from "react";
import { useDispatch } from "react-redux";
import { addTodo } from "../features/todos/todosSlice";

function AddTodo() {
  const [text, setText] = useState("");
  const dispatch = useDispatch();

  function handleSubmit(e) {
    e.preventDefault();
    if (!text.trim()) return;
    dispatch(addTodo(text.trim()));
    setText("");
  }

  return (
    <form onSubmit={handleSubmit} style={{ display: "flex", gap: "0.5rem" }}>
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="What needs to be done?"
        style={{ flex: 1, padding: "0.5rem" }}
      />
      <button type="submit">Add</button>
    </form>
  );
}
```

```jsx
// components/TodoFilter.jsx
import { useSelector, useDispatch } from "react-redux";
import {
  setFilter,
  clearCompleted,
  selectFilter,
  selectTodoStats,
} from "../features/todos/todosSlice";

function TodoFilter() {
  const filter = useSelector(selectFilter);
  const stats = useSelector(selectTodoStats);
  const dispatch = useDispatch();

  const filters = ["all", "active", "completed"];

  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.75rem 0" }}>
      <span>{stats.active} items left</span>

      <div style={{ display: "flex", gap: "0.5rem" }}>
        {filters.map((f) => (
          <button
            key={f}
            onClick={() => dispatch(setFilter(f))}
            style={{
              fontWeight: filter === f ? "bold" : "normal",
              textTransform: "capitalize",
            }}
          >
            {f}
          </button>
        ))}
      </div>

      {stats.completed > 0 && (
        <button onClick={() => dispatch(clearCompleted())}>
          Clear completed ({stats.completed})
        </button>
      )}
    </div>
  );
}
```

### Async Operations with createAsyncThunk

Redux Toolkit provides `createAsyncThunk` for handling async operations:

```jsx
// features/posts/postsSlice.js
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// Define the async thunk
export const fetchPosts = createAsyncThunk(
  "posts/fetchPosts",
  async (_, { rejectWithValue }) => {
    try {
      const response = await fetch("/api/posts");
      if (!response.ok) throw new Error("Failed to fetch posts");
      return await response.json();
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const createPost = createAsyncThunk(
  "posts/createPost",
  async (postData, { rejectWithValue }) => {
    try {
      const response = await fetch("/api/posts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(postData),
      });
      if (!response.ok) throw new Error("Failed to create post");
      return await response.json();
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const postsSlice = createSlice({
  name: "posts",
  initialState: {
    items: [],
    loading: false,
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      // fetchPosts
      .addCase(fetchPosts.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPosts.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchPosts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // createPost
      .addCase(createPost.fulfilled, (state, action) => {
        state.items.unshift(action.payload);
      });
  },
});

export default postsSlice.reducer;
```

Each async thunk automatically generates three action types:

- `posts/fetchPosts/pending` — dispatched when the request starts
- `posts/fetchPosts/fulfilled` — dispatched when the request succeeds
- `posts/fetchPosts/rejected` — dispatched when the request fails

The `extraReducers` field handles these generated actions.

```jsx
// Using in a component
function PostList() {
  const { items: posts, loading, error } = useSelector((state) => state.posts);
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(fetchPosts());
  }, [dispatch]);

  if (loading) return <p>Loading posts...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <ul>
      {posts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  );
}
```

### Redux DevTools

One of Redux's biggest advantages is its DevTools browser extension. Install the **Redux DevTools** extension for Chrome or Firefox, and you get:

- **State inspector** — See the entire state tree at any point in time
- **Action log** — Every dispatched action with its payload
- **Time-travel debugging** — Step back and forward through state changes
- **Action replay** — Re-dispatch any previous action
- **State diff** — See exactly what changed with each action

Redux Toolkit's `configureStore` enables DevTools automatically — no setup required.

### Redux Toolkit File Structure

```
src/
  features/
    auth/
      authSlice.js
      LoginForm.jsx
    cart/
      cartSlice.js
      CartPage.jsx
      CartIcon.jsx
    posts/
      postsSlice.js
      PostList.jsx
      PostDetail.jsx
    todos/
      todosSlice.js
      TodoList.jsx
      AddTodo.jsx
  store.js
  App.jsx
  main.jsx
```

Each feature folder contains its slice (state + reducers + actions) alongside its components. The `store.js` file imports all slices and configures the store.

---

## Zustand vs Redux Toolkit: A Comparison

### Code Comparison: Counter

**Zustand:**

```jsx
// store.js — that is the entire setup
const useCounterStore = create((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set((state) => ({ count: state.count - 1 })),
}));

// Component
function Counter() {
  const count = useCounterStore((state) => state.count);
  const increment = useCounterStore((state) => state.increment);
  return <button onClick={increment}>{count}</button>;
}
```

**Redux Toolkit:**

```jsx
// counterSlice.js
const counterSlice = createSlice({
  name: "counter",
  initialState: { value: 0 },
  reducers: {
    increment: (state) => { state.value += 1; },
    decrement: (state) => { state.value -= 1; },
  },
});
export const { increment, decrement } = counterSlice.actions;
export default counterSlice.reducer;

// store.js
const store = configureStore({
  reducer: { counter: counterReducer },
});

// main.jsx — wrap app in Provider
<Provider store={store}><App /></Provider>

// Component
function Counter() {
  const count = useSelector((state) => state.counter.value);
  const dispatch = useDispatch();
  return <button onClick={() => dispatch(increment())}>{count}</button>;
}
```

### Feature Comparison

| Feature | Zustand | Redux Toolkit |
|---------|---------|---------------|
| Bundle size | ~1 KB | ~11 KB |
| Boilerplate | Minimal | Moderate |
| Learning curve | Low | Medium |
| DevTools | Basic (via middleware) | Excellent (time-travel, action log) |
| Middleware | Composable | Built-in (thunk, listener) |
| Provider needed | No | Yes |
| Multiple stores | Yes (encouraged) | No (single store) |
| TypeScript | Good | Excellent |
| Ecosystem | Growing | Massive |
| Async patterns | Plain async/await | createAsyncThunk |
| Persistence | persist middleware | Manual or redux-persist |
| Community | Large, growing | Very large, established |

### When to Use Each

**Choose Zustand when:**
- You want minimal boilerplate and fast setup
- Your state management needs are moderate
- You prefer multiple small stores over one large store
- You do not need time-travel debugging
- You are building a small-to-medium application

**Choose Redux Toolkit when:**
- You need powerful DevTools and time-travel debugging
- Your team is already familiar with Redux
- You have complex async flows with many loading/error states
- You need a strict, predictable pattern for a large team
- You are building a large, enterprise application
- You need the extensive Redux ecosystem (middleware, libraries)

**Choose Context + useReducer when:**
- You have simple shared state (theme, auth, locale)
- State updates are infrequent
- You do not want any additional dependencies
- The application is small

---

## Server State: A Brief Introduction to TanStack Query

Server state (data from APIs) has different needs than client state. It needs caching, background refetching, pagination, retry logic, and stale data handling. These are concerns that Redux and Zustand can handle but are not designed for.

**TanStack Query** (formerly React Query) is a library specifically built for server state:

```bash
npm install @tanstack/react-query
```

```jsx
// Setup
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <MyApp />
    </QueryClientProvider>
  );
}
```

```jsx
// Fetching data
import { useQuery } from "@tanstack/react-query";

function UserList() {
  const { data: users, isLoading, error } = useQuery({
    queryKey: ["users"],
    queryFn: () => fetch("/api/users").then((r) => r.json()),
  });

  if (isLoading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;

  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

```jsx
// Mutations (create, update, delete)
import { useMutation, useQueryClient } from "@tanstack/react-query";

function CreateUser() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (newUser) =>
      fetch("/api/users", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newUser),
      }).then((r) => r.json()),

    onSuccess: () => {
      // Invalidate and refetch the users list
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });

  // mutation.mutate({ name: "Jane", email: "jane@example.com" })
}
```

TanStack Query automatically handles:

- **Caching** — responses are cached and served instantly on subsequent requests
- **Background refetching** — stale data is shown while fresh data loads
- **Retry** — failed requests are retried automatically
- **Deduplication** — multiple components requesting the same data trigger only one request
- **Pagination and infinite queries** — built-in hooks for paginated data
- **Optimistic updates** — update the cache before the server responds

### Combining TanStack Query with Zustand or Redux

The recommended modern approach is:

- **TanStack Query** for server state (API data)
- **Zustand or Redux** for client state (UI state, user preferences, form state)
- **URL state** (React Router) for navigation state

This separation means your Redux/Zustand store is lean — it only holds truly client-side state, not cached API responses.

---

## Mini Project: Task Management Board

Let us build a Kanban-style task board using Zustand, demonstrating real-world state management patterns.

```jsx
// stores/boardStore.js
import { create } from "zustand";
import { persist } from "zustand/middleware";

const useBoardStore = create(
  persist(
    (set, get) => ({
      columns: {
        todo: { id: "todo", title: "To Do", taskIds: [] },
        inProgress: { id: "inProgress", title: "In Progress", taskIds: [] },
        done: { id: "done", title: "Done", taskIds: [] },
      },
      tasks: {},
      nextId: 1,

      // Add a new task to the "todo" column
      addTask: (title, description = "") => {
        const id = `task-${get().nextId}`;

        set((state) => ({
          tasks: {
            ...state.tasks,
            [id]: {
              id,
              title,
              description,
              priority: "medium",
              createdAt: new Date().toISOString(),
            },
          },
          columns: {
            ...state.columns,
            todo: {
              ...state.columns.todo,
              taskIds: [...state.columns.todo.taskIds, id],
            },
          },
          nextId: state.nextId + 1,
        }));
      },

      // Update a task's properties
      updateTask: (taskId, updates) => {
        set((state) => ({
          tasks: {
            ...state.tasks,
            [taskId]: { ...state.tasks[taskId], ...updates },
          },
        }));
      },

      // Delete a task
      deleteTask: (taskId) => {
        set((state) => {
          const newTasks = { ...state.tasks };
          delete newTasks[taskId];

          const newColumns = {};
          for (const [key, column] of Object.entries(state.columns)) {
            newColumns[key] = {
              ...column,
              taskIds: column.taskIds.filter((id) => id !== taskId),
            };
          }

          return { tasks: newTasks, columns: newColumns };
        });
      },

      // Move a task between columns
      moveTask: (taskId, fromColumnId, toColumnId) => {
        if (fromColumnId === toColumnId) return;

        set((state) => ({
          columns: {
            ...state.columns,
            [fromColumnId]: {
              ...state.columns[fromColumnId],
              taskIds: state.columns[fromColumnId].taskIds.filter(
                (id) => id !== taskId
              ),
            },
            [toColumnId]: {
              ...state.columns[toColumnId],
              taskIds: [...state.columns[toColumnId].taskIds, taskId],
            },
          },
        }));
      },

      // Set task priority
      setPriority: (taskId, priority) => {
        set((state) => ({
          tasks: {
            ...state.tasks,
            [taskId]: { ...state.tasks[taskId], priority },
          },
        }));
      },

      // Get stats
      getStats: () => {
        const state = get();
        const totalTasks = Object.keys(state.tasks).length;
        const todoCount = state.columns.todo.taskIds.length;
        const inProgressCount = state.columns.inProgress.taskIds.length;
        const doneCount = state.columns.done.taskIds.length;
        return { totalTasks, todoCount, inProgressCount, doneCount };
      },
    }),
    {
      name: "kanban-board",
    }
  )
);

export default useBoardStore;
```

```jsx
// components/Board.jsx
import { useState } from "react";
import useBoardStore from "../stores/boardStore";

function Board() {
  const columns = useBoardStore((state) => state.columns);

  return (
    <div>
      <BoardHeader />
      <div style={{ display: "flex", gap: "1rem", padding: "1rem", overflowX: "auto" }}>
        {Object.values(columns).map((column) => (
          <Column key={column.id} column={column} />
        ))}
      </div>
    </div>
  );
}

function BoardHeader() {
  const stats = useBoardStore((state) => state.getStats());
  const [showForm, setShowForm] = useState(false);

  return (
    <div style={{ padding: "1rem", borderBottom: "1px solid #e5e7eb" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1 style={{ margin: 0 }}>Task Board</h1>
          <p style={{ color: "#666", margin: "0.25rem 0 0" }}>
            {stats.totalTasks} tasks — {stats.todoCount} todo, {stats.inProgressCount} in progress, {stats.doneCount} done
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          style={{
            padding: "0.5rem 1rem",
            backgroundColor: "#3b82f6",
            color: "white",
            border: "none",
            borderRadius: 4,
            cursor: "pointer",
          }}
        >
          + New Task
        </button>
      </div>

      {showForm && <AddTaskForm onClose={() => setShowForm(false)} />}
    </div>
  );
}

function AddTaskForm({ onClose }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const addTask = useBoardStore((state) => state.addTask);

  function handleSubmit(e) {
    e.preventDefault();
    if (!title.trim()) return;
    addTask(title.trim(), description.trim());
    setTitle("");
    setDescription("");
    onClose();
  }

  return (
    <form
      onSubmit={handleSubmit}
      style={{
        marginTop: "1rem",
        padding: "1rem",
        backgroundColor: "#f9fafb",
        borderRadius: 8,
      }}
    >
      <input
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Task title"
        required
        autoFocus
        style={{ display: "block", width: "100%", padding: "0.5rem", marginBottom: "0.5rem" }}
      />
      <textarea
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Description (optional)"
        rows={2}
        style={{ display: "block", width: "100%", padding: "0.5rem", marginBottom: "0.5rem" }}
      />
      <div style={{ display: "flex", gap: "0.5rem" }}>
        <button type="submit">Add Task</button>
        <button type="button" onClick={onClose}>Cancel</button>
      </div>
    </form>
  );
}
```

```jsx
// components/Column.jsx
import useBoardStore from "../stores/boardStore";

function Column({ column }) {
  const tasks = useBoardStore((state) =>
    column.taskIds.map((id) => state.tasks[id]).filter(Boolean)
  );

  return (
    <div
      style={{
        flex: "1 1 300px",
        minWidth: 280,
        backgroundColor: "#f3f4f6",
        borderRadius: 8,
        padding: "0.75rem",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
        <h2 style={{ margin: 0, fontSize: "1rem" }}>
          {column.title}
        </h2>
        <span
          style={{
            backgroundColor: "#e5e7eb",
            padding: "0.125rem 0.5rem",
            borderRadius: 12,
            fontSize: "0.8rem",
          }}
        >
          {tasks.length}
        </span>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
        {tasks.map((task) => (
          <TaskCard key={task.id} task={task} columnId={column.id} />
        ))}

        {tasks.length === 0 && (
          <p style={{ color: "#999", textAlign: "center", padding: "2rem 0", fontSize: "0.9rem" }}>
            No tasks
          </p>
        )}
      </div>
    </div>
  );
}
```

```jsx
// components/TaskCard.jsx
import { useState } from "react";
import useBoardStore from "../stores/boardStore";

const priorityColors = {
  low: "#10b981",
  medium: "#f59e0b",
  high: "#ef4444",
};

function TaskCard({ task, columnId }) {
  const [expanded, setExpanded] = useState(false);
  const moveTask = useBoardStore((state) => state.moveTask);
  const deleteTask = useBoardStore((state) => state.deleteTask);
  const setPriority = useBoardStore((state) => state.setPriority);
  const columns = useBoardStore((state) => state.columns);

  const otherColumns = Object.values(columns).filter(
    (col) => col.id !== columnId
  );

  return (
    <div
      style={{
        backgroundColor: "white",
        borderRadius: 6,
        padding: "0.75rem",
        borderLeft: `3px solid ${priorityColors[task.priority]}`,
        boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
        cursor: "pointer",
      }}
      onClick={() => setExpanded(!expanded)}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <h3 style={{ margin: 0, fontSize: "0.9rem", fontWeight: 500 }}>
          {task.title}
        </h3>
        <button
          onClick={(e) => {
            e.stopPropagation();
            deleteTask(task.id);
          }}
          style={{
            background: "none",
            border: "none",
            color: "#999",
            cursor: "pointer",
            fontSize: "1rem",
          }}
        >
          ×
        </button>
      </div>

      {task.description && (
        <p style={{ margin: "0.5rem 0 0", fontSize: "0.8rem", color: "#666" }}>
          {expanded ? task.description : task.description.substring(0, 60) + (task.description.length > 60 ? "..." : "")}
        </p>
      )}

      {expanded && (
        <div style={{ marginTop: "0.75rem", borderTop: "1px solid #eee", paddingTop: "0.75rem" }}>
          {/* Priority selector */}
          <div style={{ marginBottom: "0.5rem" }}>
            <span style={{ fontSize: "0.8rem", color: "#666" }}>Priority: </span>
            {["low", "medium", "high"].map((p) => (
              <button
                key={p}
                onClick={(e) => {
                  e.stopPropagation();
                  setPriority(task.id, p);
                }}
                style={{
                  marginLeft: "0.25rem",
                  padding: "0.125rem 0.5rem",
                  fontSize: "0.75rem",
                  borderRadius: 4,
                  border: "1px solid #ddd",
                  backgroundColor: task.priority === p ? priorityColors[p] : "white",
                  color: task.priority === p ? "white" : "#333",
                  cursor: "pointer",
                  textTransform: "capitalize",
                }}
              >
                {p}
              </button>
            ))}
          </div>

          {/* Move buttons */}
          <div>
            <span style={{ fontSize: "0.8rem", color: "#666" }}>Move to: </span>
            {otherColumns.map((col) => (
              <button
                key={col.id}
                onClick={(e) => {
                  e.stopPropagation();
                  moveTask(task.id, columnId, col.id);
                }}
                style={{
                  marginLeft: "0.25rem",
                  padding: "0.125rem 0.5rem",
                  fontSize: "0.75rem",
                  borderRadius: 4,
                  border: "1px solid #ddd",
                  cursor: "pointer",
                }}
              >
                {col.title}
              </button>
            ))}
          </div>

          <p style={{ marginTop: "0.5rem", fontSize: "0.7rem", color: "#999" }}>
            Created: {new Date(task.createdAt).toLocaleDateString()}
          </p>
        </div>
      )}
    </div>
  );
}
```

This mini project demonstrates:

- **Zustand store** with complex state shape (normalized data with columns and tasks)
- **Persistence** with the `persist` middleware (survives page refresh)
- **Selectors** for derived data (stats, filtered task lists)
- **Multiple actions** (add, update, delete, move, set priority)
- **Component composition** — Board, Column, TaskCard, AddTaskForm each select only the state they need
- **No Provider needed** — components import and use the store directly

---

## The State Management Decision Framework

When deciding how to manage state, ask these questions in order:

### Question 1: Can this state stay local?

If only one component (or a parent and its direct children) needs the state, use `useState` or `useReducer`. Do not lift it higher than necessary.

### Question 2: Is this server data?

If the state is data fetched from an API, consider TanStack Query or SWR. These handle caching, refetching, loading states, and error handling out of the box — problems that Redux and Zustand can handle but are not optimized for.

### Question 3: Is this URL state?

If the state should be reflected in the URL (current page, search query, filters, sort order), use React Router's `useParams` and `useSearchParams`. URL state is shareable, bookmarkable, and survives refresh.

### Question 4: How many components need this shared state?

- **2-5 components in the same tree** → Lift state up to a common parent, or use Context
- **Many components across the tree, simple state** → Context + useReducer
- **Many components, complex state, performance matters** → Zustand or Redux Toolkit

### Question 5: What does your team know?

- Team knows Redux → Use Redux Toolkit
- Team is small and prefers simplicity → Use Zustand
- Team does not want dependencies → Use Context + useReducer

### The Pragmatic Mix

Most real-world applications use a combination:

```
Local state (useState/useReducer)
  ↓ Only if state needs to be shared
Context (useContext)
  ↓ Only if Context has performance issues or too many providers
Zustand or Redux Toolkit
  ↓ Separately, for server data
TanStack Query / SWR
  ↓ Separately, for URL state
React Router (useParams, useSearchParams)
```

---

## Common Mistakes

### Mistake 1: Putting Everything in Global State

```jsx
// WRONG — form input values do not belong in global state
const useStore = create((set) => ({
  searchQuery: "",
  setSearchQuery: (query) => set({ searchQuery: query }),
  isModalOpen: false,
  setIsModalOpen: (open) => set({ isModalOpen: open }),
  // ... dozens of UI-only values
}));

// CORRECT — keep local state local
function SearchBar() {
  const [query, setQuery] = useState(""); // Local — only this component needs it
  // ...
}
```

### Mistake 2: Storing Server Data in Redux

```jsx
// WRONG — using Redux for API cache management
const postsSlice = createSlice({
  name: "posts",
  initialState: { data: [], loading: false, error: null, lastFetched: null },
  // ... managing cache invalidation, refetching, stale data manually
});

// BETTER — use TanStack Query for server state
const { data: posts, isLoading, error } = useQuery({
  queryKey: ["posts"],
  queryFn: fetchPosts,
  staleTime: 5 * 60 * 1000, // 5 minutes
});
```

### Mistake 3: Not Using Selectors (Subscribing to the Entire Store)

```jsx
// WRONG — re-renders on ANY store change
function CartIcon() {
  const store = useCartStore(); // Subscribes to everything
  return <span>{store.items.length}</span>;
}

// CORRECT — re-renders only when items changes
function CartIcon() {
  const itemCount = useCartStore((state) => state.items.length);
  return <span>{itemCount}</span>;
}
```

### Mistake 4: Premature State Management Adoption

```jsx
// WRONG — reaching for Redux before you need it
// "We might need it later" is not a reason

// CORRECT — start with the simplest solution
// 1. useState for local state
// 2. Lift state up when children need it
// 3. Context when prop drilling gets painful
// 4. Zustand/Redux when Context hits limits
```

### Mistake 5: Mutating State Outside RTK

```jsx
// WRONG — directly mutating state outside Redux Toolkit's Immer wrapper
const [users, setUsers] = useState([{ id: 1, name: "Alice" }]);
users[0].name = "Bob"; // Mutation! React does not see this change
setUsers(users);       // Same reference — no re-render

// CORRECT
setUsers(prev =>
  prev.map(user =>
    user.id === 1 ? { ...user, name: "Bob" } : user
  )
);
```

Remember: the "mutation" syntax is only safe inside Redux Toolkit's `createSlice` reducers, where Immer handles immutability. Everywhere else in React, you must create new objects and arrays.

---

## Best Practices

1. **Start simple, add complexity only when needed** — Begin with `useState`. Move to Context when state needs sharing. Move to Zustand/Redux when Context shows its limits. Premature optimization is the root of all evil.

2. **Categorize your state** — Local state stays in components. Server state uses TanStack Query. URL state uses React Router. Only truly shared client state goes in Zustand or Redux.

3. **Use selectors everywhere** — Never subscribe to an entire store. Always select the minimum data a component needs. This prevents unnecessary re-renders.

4. **Normalize complex data** — Store entities by ID in an object, not in nested arrays. This makes updates, lookups, and deletions O(1) instead of O(n).

5. **Co-locate state logic with features** — Keep slices/stores next to the components that use them. A feature's state, components, and API calls should live in the same folder.

6. **Keep actions descriptive** — Name actions after what happened, not what should happen: `orderPlaced` instead of `clearCart`. This makes the action log in DevTools meaningful.

7. **Do not duplicate state** — If a value can be derived from other state, compute it with a selector instead of storing it separately. Duplicated state gets out of sync.

---

## Summary

In this chapter, you learned:

- **Context limitations** — all consumers re-render on any change, no DevTools, no middleware, verbose boilerplate for many features
- **State categories** — local (useState), shared (Context/Zustand/Redux), server (TanStack Query), URL (React Router)
- **Zustand** provides lightweight global state with minimal boilerplate — no Provider, simple API, built-in persistence, selector-based subscriptions
- **Redux Toolkit** provides predictable state management with createSlice (Immer-powered reducers), configureStore, powerful DevTools, and createAsyncThunk for async operations
- **Zustand is ideal** for small-to-medium apps wanting simplicity; **Redux Toolkit is ideal** for large apps needing DevTools and strict patterns
- **TanStack Query** handles server state (API caching, refetching, pagination) better than general-purpose state managers
- **The decision framework** — keep state as local as possible, use the right tool for each state category, and resist the urge to put everything in global state

---

## Interview Questions

1. **When would you choose Zustand over Redux for state management?**

   Zustand is a good choice when you want minimal boilerplate, fast setup, and a simple API. It does not require a Provider wrapper, supports multiple small stores, and handles async operations with plain async/await. Choose Zustand for small-to-medium applications, when you prefer simplicity over strict patterns, or when you do not need Redux's advanced DevTools (time-travel debugging, action replay). Redux Toolkit is better for large team projects that need predictable patterns, extensive DevTools, and a mature ecosystem.

2. **What problem does Redux Toolkit's Immer integration solve?**

   In React, state must be updated immutably — you must create new objects and arrays instead of modifying existing ones. For deeply nested state, this requires verbose spread operator chains. RTK's Immer integration lets you write "mutating" code inside reducers (`state.user.address.city = "NYC"`) that Immer automatically converts to immutable updates. This makes reducers shorter, more readable, and less error-prone — without actually mutating state.

3. **What is the difference between server state and client state? Why does it matter?**

   Client state originates in the browser — user preferences, UI toggles, form data, selected items. It is synchronous, fully controlled by the application, and has one source of truth (the client). Server state originates on the server — user profiles, product lists, comments. It is asynchronous, shared with other clients, and can become stale. Server state needs caching, background refetching, retry logic, and invalidation — concerns that general state managers like Redux handle poorly. Libraries like TanStack Query are purpose-built for server state and handle these concerns automatically.

4. **What are selectors and why are they important in state management?**

   Selectors are functions that extract specific pieces of data from a store. They serve two purposes: (1) they decouple components from the store's internal structure — if you restructure the store, you update selectors, not components; (2) they prevent unnecessary re-renders — a component subscribed to `state.cart.items.length` only re-renders when that count changes, not when unrelated state changes. In Redux, selectors can be memoized with `createSelector` to avoid recomputing derived data on every render.

5. **Explain the state management decision framework you would use for a new project.**

   Start with the simplest solution and add complexity only when needed. Use `useState` for component-local state. Lift state up to common parents when a few siblings need it. Use Context for truly global, infrequently-changing state like theme or auth. Use TanStack Query for API data (server state). Use React Router for URL state. Only reach for Zustand or Redux when you have complex shared client state that Context cannot handle efficiently — either due to performance (too many re-renders) or organization (too many contexts). Never put everything in global state — keep state as close to where it is used as possible.

---

## Practice Exercises

### Exercise 1: Multi-Feature Store with Zustand

Create a Zustand store that manages a note-taking application with the following features: notes CRUD, tags/labels with color coding, a favorites system, and search/filter. Each feature should be a separate store. Components should subscribe only to the state they need.

### Exercise 2: Redux Toolkit Async Flow

Build a blog reader using Redux Toolkit with `createAsyncThunk`. It should fetch a list of posts, fetch individual posts with comments, handle loading and error states for each request independently, and cache previously fetched posts so navigating back to a post does not refetch.

### Exercise 3: State Architecture Design

Design the state architecture for an e-commerce application. Categorize each piece of state (product catalog, user profile, shopping cart, order history, search filters, theme, notifications) into the appropriate category (local, shared, server, URL). Justify each choice. Implement the shopping cart using both Zustand and Redux Toolkit, then compare the code.

### Exercise 4: Migration from Context to Zustand

Take the authentication and cart contexts from Chapters 13-14 and migrate them to Zustand stores. Add persistence so the cart survives page refreshes. Compare the before and after code — count the lines, measure the re-renders with React DevTools Profiler, and document the differences.

---

## What Is Next?

In Chapter 19, we will explore **Error Boundaries** — React's mechanism for catching JavaScript errors in the component tree, displaying fallback UI, and preventing a single broken component from crashing the entire application.
