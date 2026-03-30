# Chapter 14: useReducer — Managing Complex State

## Learning Goals

By the end of this chapter, you will be able to:

- Understand when useState is not enough and why useReducer exists
- Write reducer functions that handle multiple action types
- Dispatch actions with and without payloads
- Refactor complex useState logic into useReducer
- Combine useReducer with useContext for scalable state management
- Handle async operations alongside useReducer
- Apply the reducer pattern to real-world scenarios

---

## The Problem with Complex State

In earlier chapters, you managed state with `useState`. For simple values — a counter, a toggle, a form field — `useState` is perfect. But as your components grow, you will encounter state logic that starts to feel messy.

Consider a shopping cart. You need to:

- Add items
- Remove items
- Update quantities
- Apply discount codes
- Clear the cart
- Calculate totals

With `useState`, you might end up with something like this:

```jsx
function ShoppingCart() {
  const [items, setItems] = useState([]);
  const [discount, setDiscount] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  function addItem(product) {
    setItems(prev => {
      const existing = prev.find(item => item.id === product.id);
      if (existing) {
        return prev.map(item =>
          item.id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      }
      return [...prev, { ...product, quantity: 1 }];
    });
  }

  function removeItem(productId) {
    setItems(prev => prev.filter(item => item.id !== productId));
  }

  function updateQuantity(productId, quantity) {
    if (quantity <= 0) {
      removeItem(productId);
      return;
    }
    setItems(prev =>
      prev.map(item =>
        item.id === productId ? { ...item, quantity } : item
      )
    );
  }

  function applyDiscount(code) {
    setIsLoading(true);
    setError(null);
    // validate code, update discount, handle errors...
  }

  function clearCart() {
    setItems([]);
    setDiscount(null);
    setError(null);
  }

  // ... more functions, more state updates scattered everywhere
}
```

Notice the problems:

1. **State updates are scattered** across many functions
2. **Related state changes happen in multiple places** — clearing the cart touches three different state variables
3. **Logic is hard to test** — each function is embedded inside the component
4. **It is easy to forget a state update** — what if you add a new state variable and forget to reset it in `clearCart`?

This is exactly the kind of problem `useReducer` solves.

---

## What Is useReducer?

`useReducer` is a React hook that manages state through a pattern borrowed from Redux and, before that, from the `reduce` function in functional programming. The idea is simple:

> **Current state + Action = New state**

Instead of calling multiple setter functions, you **dispatch an action** that describes what happened. A **reducer function** takes the current state and that action, then returns the new state.

```
dispatch({ type: "ADD_ITEM", payload: product })
         ↓
reducer(currentState, action)
         ↓
returns newState
```

### The useReducer Signature

```jsx
const [state, dispatch] = useReducer(reducer, initialState);
```

- **`reducer`** — A pure function: `(state, action) => newState`
- **`initialState`** — The starting value of your state
- **`state`** — The current state value (just like with `useState`)
- **`dispatch`** — A function you call to send actions to the reducer

### A First Example: Counter

Let us start with the simplest possible example to see the mechanics:

```jsx
import { useReducer } from "react";

// Step 1: Define the initial state
const initialState = { count: 0 };

// Step 2: Define the reducer function
function reducer(state, action) {
  switch (action.type) {
    case "INCREMENT":
      return { count: state.count + 1 };
    case "DECREMENT":
      return { count: state.count - 1 };
    case "RESET":
      return initialState;
    default:
      throw new Error(`Unknown action type: ${action.type}`);
  }
}

// Step 3: Use it in a component
function Counter() {
  const [state, dispatch] = useReducer(reducer, initialState);

  return (
    <div>
      <p>Count: {state.count}</p>
      <button onClick={() => dispatch({ type: "INCREMENT" })}>+</button>
      <button onClick={() => dispatch({ type: "DECREMENT" })}>-</button>
      <button onClick={() => dispatch({ type: "RESET" })}>Reset</button>
    </div>
  );
}
```

Compare this with useState:

```jsx
function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(c => c + 1)}>+</button>
      <button onClick={() => setCount(c => c - 1)}>-</button>
      <button onClick={() => setCount(0)}>Reset</button>
    </div>
  );
}
```

For a counter, `useState` is clearly simpler. So when does `useReducer` start to shine? When the state transitions get more complex and when multiple values need to change together.

---

## Anatomy of a Reducer

### The Reducer Function

A reducer is a **pure function** that takes two arguments and returns new state:

```jsx
function reducer(state, action) {
  // Based on the action, compute and return new state
  // NEVER modify `state` directly — always return a new object
}
```

Rules for reducers:

1. **Must be pure** — same inputs always produce the same output, no side effects
2. **Must return new state** — never mutate the existing state object
3. **Must handle every action type** — throw an error for unknown types to catch typos
4. **Should be defined outside the component** — it does not need access to props or hooks

### Actions

An action is a plain object that describes what happened. By convention, it has a `type` property (a string that names the action) and an optional `payload` (the data needed to perform the update):

```jsx
// Action without payload
{ type: "RESET" }

// Action with payload
{ type: "ADD_ITEM", payload: { id: 1, name: "Book", price: 29.99 } }

// Action with simple payload
{ type: "SET_QUANTITY", payload: { id: 1, quantity: 3 } }
```

The `type` string is entirely up to you. Common conventions:

- **SCREAMING_SNAKE_CASE**: `"ADD_ITEM"`, `"REMOVE_ITEM"` (Redux convention)
- **camelCase with prefix**: `"items/add"`, `"items/remove"`
- **Past tense describing what happened**: `"itemAdded"`, `"itemRemoved"`

Pick one convention and stick with it throughout your project.

### The dispatch Function

`dispatch` sends an action to the reducer. React then:

1. Calls `reducer(currentState, action)`
2. Compares the returned state with the current state
3. If they differ, re-renders the component with the new state

```jsx
// Dispatching actions
dispatch({ type: "INCREMENT" });
dispatch({ type: "ADD_ITEM", payload: product });
dispatch({ type: "SET_FILTER", payload: "completed" });
```

One important property: **dispatch is stable**. Its identity never changes between re-renders. This means you can safely pass it to child components or include it in dependency arrays without causing unnecessary effects or re-renders.

---

## useReducer with Complex State

Now let us see where `useReducer` truly earns its keep. Consider a todo list with filtering, editing, and bulk operations.

### Todo List with useReducer

```jsx
import { useReducer } from "react";

const initialState = {
  todos: [],
  filter: "all", // "all" | "active" | "completed"
  nextId: 1,
};

function todoReducer(state, action) {
  switch (action.type) {
    case "ADD_TODO":
      return {
        ...state,
        todos: [
          ...state.todos,
          {
            id: state.nextId,
            text: action.payload,
            completed: false,
          },
        ],
        nextId: state.nextId + 1,
      };

    case "TOGGLE_TODO":
      return {
        ...state,
        todos: state.todos.map(todo =>
          todo.id === action.payload
            ? { ...todo, completed: !todo.completed }
            : todo
        ),
      };

    case "DELETE_TODO":
      return {
        ...state,
        todos: state.todos.filter(todo => todo.id !== action.payload),
      };

    case "EDIT_TODO":
      return {
        ...state,
        todos: state.todos.map(todo =>
          todo.id === action.payload.id
            ? { ...todo, text: action.payload.text }
            : todo
        ),
      };

    case "SET_FILTER":
      return {
        ...state,
        filter: action.payload,
      };

    case "CLEAR_COMPLETED":
      return {
        ...state,
        todos: state.todos.filter(todo => !todo.completed),
      };

    case "TOGGLE_ALL": {
      const allCompleted = state.todos.every(todo => todo.completed);
      return {
        ...state,
        todos: state.todos.map(todo => ({
          ...todo,
          completed: !allCompleted,
        })),
      };
    }

    default:
      throw new Error(`Unknown action type: ${action.type}`);
  }
}
```

Now the component becomes clean and declarative:

```jsx
function TodoApp() {
  const [state, dispatch] = useReducer(todoReducer, initialState);
  const { todos, filter } = state;

  const filteredTodos = todos.filter(todo => {
    if (filter === "active") return !todo.completed;
    if (filter === "completed") return todo.completed;
    return true;
  });

  const activeTodoCount = todos.filter(todo => !todo.completed).length;

  return (
    <div>
      <h1>Todo List</h1>

      <TodoInput onAdd={text => dispatch({ type: "ADD_TODO", payload: text })} />

      {todos.length > 0 && (
        <button onClick={() => dispatch({ type: "TOGGLE_ALL" })}>
          Toggle All
        </button>
      )}

      <ul>
        {filteredTodos.map(todo => (
          <TodoItem
            key={todo.id}
            todo={todo}
            onToggle={() => dispatch({ type: "TOGGLE_TODO", payload: todo.id })}
            onDelete={() => dispatch({ type: "DELETE_TODO", payload: todo.id })}
            onEdit={text =>
              dispatch({
                type: "EDIT_TODO",
                payload: { id: todo.id, text },
              })
            }
          />
        ))}
      </ul>

      <div>
        <span>{activeTodoCount} items left</span>

        {["all", "active", "completed"].map(f => (
          <button
            key={f}
            onClick={() => dispatch({ type: "SET_FILTER", payload: f })}
            style={{ fontWeight: filter === f ? "bold" : "normal" }}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}

        <button onClick={() => dispatch({ type: "CLEAR_COMPLETED" })}>
          Clear Completed
        </button>
      </div>
    </div>
  );
}
```

```jsx
function TodoInput({ onAdd }) {
  const [text, setText] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    const trimmed = text.trim();
    if (!trimmed) return;
    onAdd(trimmed);
    setText("");
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={text}
        onChange={e => setText(e.target.value)}
        placeholder="What needs to be done?"
      />
      <button type="submit">Add</button>
    </form>
  );
}
```

```jsx
function TodoItem({ todo, onToggle, onDelete, onEdit }) {
  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState(todo.text);

  function handleSave() {
    const trimmed = editText.trim();
    if (trimmed) {
      onEdit(trimmed);
      setIsEditing(false);
    }
  }

  if (isEditing) {
    return (
      <li>
        <input
          value={editText}
          onChange={e => setEditText(e.target.value)}
          onBlur={handleSave}
          onKeyDown={e => {
            if (e.key === "Enter") handleSave();
            if (e.key === "Escape") {
              setEditText(todo.text);
              setIsEditing(false);
            }
          }}
          autoFocus
        />
      </li>
    );
  }

  return (
    <li>
      <input
        type="checkbox"
        checked={todo.completed}
        onChange={onToggle}
      />
      <span
        style={{
          textDecoration: todo.completed ? "line-through" : "none",
        }}
        onDoubleClick={() => setIsEditing(true)}
      >
        {todo.text}
      </span>
      <button onClick={onDelete}>Delete</button>
    </li>
  );
}
```

Notice something important: the `TodoInput` and `TodoItem` components still use `useState` for their own local UI state (the input text, the editing mode). **useReducer and useState are not mutually exclusive** — use each where it fits best.

---

## useState vs useReducer: When to Choose Which

This is one of the most common questions React developers ask. Here is a practical decision framework:

### Use useState When:

- State is a single primitive value (string, number, boolean)
- State transitions are simple (set to a new value)
- There are few state variables that change independently
- The next state does not depend on complex logic

```jsx
// Good fit for useState
const [isOpen, setIsOpen] = useState(false);
const [name, setName] = useState("");
const [count, setCount] = useState(0);
```

### Use useReducer When:

- State is an object or array with multiple sub-values
- Multiple state values change together in response to one event
- The next state depends on the previous state in complex ways
- You want to centralize and test state logic outside the component
- You have many event handlers that update state similarly

```jsx
// Good fit for useReducer
const [formState, dispatch] = useReducer(formReducer, initialFormState);
const [cartState, dispatch] = useReducer(cartReducer, initialCartState);
```

### The Rule of Thumb

> If you find yourself writing `setState` calls that reference the previous state and involve conditional logic, or if you have multiple `setState` calls that must happen together, consider `useReducer`.

Here is a side-by-side comparison for a data fetching scenario:

**With useState:**

```jsx
function useFetchData(url) {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  async function fetchData() {
    setIsLoading(true);
    setError(null);     // Must remember to clear error
    setData(null);      // Must remember to clear data

    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error("Failed to fetch");
      const result = await response.json();
      setData(result);
      setIsLoading(false);  // Must remember to set loading false
    } catch (err) {
      setError(err.message);
      setIsLoading(false);  // Must remember here too
    }
  }

  return { data, isLoading, error, fetchData };
}
```

**With useReducer:**

```jsx
const initialState = {
  data: null,
  isLoading: false,
  error: null,
};

function fetchReducer(state, action) {
  switch (action.type) {
    case "FETCH_START":
      return { data: null, isLoading: true, error: null };
    case "FETCH_SUCCESS":
      return { data: action.payload, isLoading: false, error: null };
    case "FETCH_ERROR":
      return { data: null, isLoading: false, error: action.payload };
    default:
      throw new Error(`Unknown action type: ${action.type}`);
  }
}

function useFetchData(url) {
  const [state, dispatch] = useReducer(fetchReducer, initialState);

  async function fetchData() {
    dispatch({ type: "FETCH_START" });

    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error("Failed to fetch");
      const result = await response.json();
      dispatch({ type: "FETCH_SUCCESS", payload: result });
    } catch (err) {
      dispatch({ type: "FETCH_ERROR", payload: err.message });
    }
  }

  return { ...state, fetchData };
}
```

With `useReducer`, each action sets **all related state at once**. You cannot forget to reset `isLoading` or clear `error` because each action handler returns the complete new state. The state transitions are **impossible to get into an invalid combination** — you will never have `isLoading: true` and `error: "something"` at the same time.

---

## Lazy Initialization

Sometimes computing the initial state is expensive — for example, reading from localStorage or parsing a large dataset. `useReducer` accepts a third argument, an **initializer function**, that lets you compute the initial state lazily:

```jsx
function init(initialCount) {
  // This function runs only once, during the first render
  const saved = localStorage.getItem("count");
  return { count: saved ? JSON.parse(saved) : initialCount };
}

function Counter({ startingCount }) {
  const [state, dispatch] = useReducer(reducer, startingCount, init);
  // ...
}
```

The three-argument form is: `useReducer(reducer, initArg, init)`. React calls `init(initArg)` once to compute the initial state. This avoids running the expensive computation on every render.

This is analogous to the lazy initializer pattern with `useState`:

```jsx
const [state, setState] = useState(() => {
  const saved = localStorage.getItem("count");
  return saved ? JSON.parse(saved) : 0;
});
```

---

## Patterns and Techniques

### Action Creators

As your reducer grows, you might want to create helper functions that build action objects. These are called **action creators**:

```jsx
// Action creators
const actions = {
  addTodo: (text) => ({ type: "ADD_TODO", payload: text }),
  toggleTodo: (id) => ({ type: "TOGGLE_TODO", payload: id }),
  deleteTodo: (id) => ({ type: "DELETE_TODO", payload: id }),
  editTodo: (id, text) => ({ type: "EDIT_TODO", payload: { id, text } }),
  setFilter: (filter) => ({ type: "SET_FILTER", payload: filter }),
  clearCompleted: () => ({ type: "CLEAR_COMPLETED" }),
};

// Usage in component
dispatch(actions.addTodo("Learn useReducer"));
dispatch(actions.toggleTodo(1));
dispatch(actions.setFilter("active"));
```

Action creators give you:

- **Autocomplete** — your editor can suggest available actions
- **Consistency** — the payload shape is defined in one place
- **Refactoring safety** — change the action type string in one place

### Multiple Reducers

For complex applications, you might split state into multiple reducers rather than one giant one:

```jsx
function App() {
  const [todos, dispatchTodos] = useReducer(todoReducer, initialTodos);
  const [user, dispatchUser] = useReducer(userReducer, initialUser);
  const [ui, dispatchUI] = useReducer(uiReducer, initialUI);

  // Each reducer manages its own slice of state
}
```

This keeps each reducer focused and easy to understand. If you find yourself needing coordination between multiple reducers (an action in one should trigger changes in another), that is a sign you might need to combine them into a single reducer or use a different state management approach.

### Reducer Composition

You can break a large reducer into smaller functions:

```jsx
function todoItemReducer(todo, action) {
  switch (action.type) {
    case "TOGGLE":
      return { ...todo, completed: !todo.completed };
    case "EDIT":
      return { ...todo, text: action.payload };
    default:
      return todo;
  }
}

function todosReducer(state, action) {
  switch (action.type) {
    case "ADD_TODO":
      return {
        ...state,
        todos: [
          ...state.todos,
          { id: state.nextId, text: action.payload, completed: false },
        ],
        nextId: state.nextId + 1,
      };

    case "TOGGLE_TODO":
      return {
        ...state,
        todos: state.todos.map(todo =>
          todo.id === action.payload.id
            ? todoItemReducer(todo, { type: "TOGGLE" })
            : todo
        ),
      };

    case "EDIT_TODO":
      return {
        ...state,
        todos: state.todos.map(todo =>
          todo.id === action.payload.id
            ? todoItemReducer(todo, {
                type: "EDIT",
                payload: action.payload.text,
              })
            : todo
        ),
      };

    default:
      throw new Error(`Unknown action type: ${action.type}`);
  }
}
```

This pattern keeps individual reducers small and testable.

---

## useReducer + useContext: Scalable State Management

In Chapter 13, you learned that Context solves prop drilling. When you combine Context with `useReducer`, you get a powerful pattern for managing application-wide state — similar to what libraries like Redux provide, but built into React.

### The Pattern

The idea is:

1. Create a context for state and a context for dispatch
2. Use `useReducer` in a provider component
3. Provide both state and dispatch through context
4. Components consume whichever they need

### Building a Task Manager

Let us build a complete example: a task management system where multiple components need to read and update tasks.

**Step 1: Define the reducer and initial state**

```jsx
// taskReducer.js

export const initialState = {
  tasks: [],
  nextId: 1,
  filter: "all",
  searchQuery: "",
};

export function taskReducer(state, action) {
  switch (action.type) {
    case "ADD_TASK":
      return {
        ...state,
        tasks: [
          ...state.tasks,
          {
            id: state.nextId,
            title: action.payload.title,
            priority: action.payload.priority || "medium",
            completed: false,
            createdAt: new Date().toISOString(),
          },
        ],
        nextId: state.nextId + 1,
      };

    case "TOGGLE_TASK":
      return {
        ...state,
        tasks: state.tasks.map(task =>
          task.id === action.payload
            ? { ...task, completed: !task.completed }
            : task
        ),
      };

    case "DELETE_TASK":
      return {
        ...state,
        tasks: state.tasks.filter(task => task.id !== action.payload),
      };

    case "SET_PRIORITY":
      return {
        ...state,
        tasks: state.tasks.map(task =>
          task.id === action.payload.id
            ? { ...task, priority: action.payload.priority }
            : task
        ),
      };

    case "SET_FILTER":
      return { ...state, filter: action.payload };

    case "SET_SEARCH":
      return { ...state, searchQuery: action.payload };

    case "CLEAR_COMPLETED":
      return {
        ...state,
        tasks: state.tasks.filter(task => !task.completed),
      };

    default:
      throw new Error(`Unknown action type: ${action.type}`);
  }
}
```

**Step 2: Create the context and provider**

```jsx
// TaskContext.jsx
import { createContext, useContext, useReducer } from "react";
import { taskReducer, initialState } from "./taskReducer";

const TaskStateContext = createContext(null);
const TaskDispatchContext = createContext(null);

export function TaskProvider({ children }) {
  const [state, dispatch] = useReducer(taskReducer, initialState);

  return (
    <TaskStateContext.Provider value={state}>
      <TaskDispatchContext.Provider value={dispatch}>
        {children}
      </TaskDispatchContext.Provider>
    </TaskStateContext.Provider>
  );
}

export function useTaskState() {
  const context = useContext(TaskStateContext);
  if (context === null) {
    throw new Error("useTaskState must be used within a TaskProvider");
  }
  return context;
}

export function useTaskDispatch() {
  const context = useContext(TaskDispatchContext);
  if (context === null) {
    throw new Error("useTaskDispatch must be used within a TaskProvider");
  }
  return context;
}
```

Notice that we split state and dispatch into **two separate contexts**. This is the same performance optimization from Chapter 13 — components that only dispatch actions (like a form) will not re-render when state changes, because the `dispatch` function is stable.

**Step 3: Build components that consume context**

```jsx
// AddTaskForm.jsx
import { useState } from "react";
import { useTaskDispatch } from "./TaskContext";

function AddTaskForm() {
  const dispatch = useTaskDispatch();
  const [title, setTitle] = useState("");
  const [priority, setPriority] = useState("medium");

  function handleSubmit(e) {
    e.preventDefault();
    const trimmed = title.trim();
    if (!trimmed) return;

    dispatch({
      type: "ADD_TASK",
      payload: { title: trimmed, priority },
    });

    setTitle("");
    setPriority("medium");
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={title}
        onChange={e => setTitle(e.target.value)}
        placeholder="New task..."
      />
      <select value={priority} onChange={e => setPriority(e.target.value)}>
        <option value="low">Low</option>
        <option value="medium">Medium</option>
        <option value="high">High</option>
      </select>
      <button type="submit">Add Task</button>
    </form>
  );
}
```

```jsx
// TaskFilters.jsx
import { useTaskState, useTaskDispatch } from "./TaskContext";

function TaskFilters() {
  const { filter, searchQuery } = useTaskState();
  const dispatch = useTaskDispatch();

  return (
    <div>
      <input
        value={searchQuery}
        onChange={e => dispatch({ type: "SET_SEARCH", payload: e.target.value })}
        placeholder="Search tasks..."
      />
      <div>
        {["all", "active", "completed"].map(f => (
          <button
            key={f}
            onClick={() => dispatch({ type: "SET_FILTER", payload: f })}
            style={{ fontWeight: filter === f ? "bold" : "normal" }}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>
    </div>
  );
}
```

```jsx
// TaskList.jsx
import { useTaskState, useTaskDispatch } from "./TaskContext";

function TaskList() {
  const { tasks, filter, searchQuery } = useTaskState();
  const dispatch = useTaskDispatch();

  const filteredTasks = tasks
    .filter(task => {
      if (filter === "active") return !task.completed;
      if (filter === "completed") return task.completed;
      return true;
    })
    .filter(task =>
      task.title.toLowerCase().includes(searchQuery.toLowerCase())
    );

  if (filteredTasks.length === 0) {
    return <p>No tasks found.</p>;
  }

  return (
    <ul>
      {filteredTasks.map(task => (
        <li key={task.id}>
          <input
            type="checkbox"
            checked={task.completed}
            onChange={() =>
              dispatch({ type: "TOGGLE_TASK", payload: task.id })
            }
          />
          <span
            style={{
              textDecoration: task.completed ? "line-through" : "none",
            }}
          >
            {task.title}
          </span>
          <span style={{ marginLeft: 8, fontSize: "0.8em" }}>
            [{task.priority}]
          </span>
          <select
            value={task.priority}
            onChange={e =>
              dispatch({
                type: "SET_PRIORITY",
                payload: { id: task.id, priority: e.target.value },
              })
            }
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
          <button
            onClick={() =>
              dispatch({ type: "DELETE_TASK", payload: task.id })
            }
          >
            Delete
          </button>
        </li>
      ))}
    </ul>
  );
}
```

```jsx
// TaskStats.jsx
import { useTaskState } from "./TaskContext";

function TaskStats() {
  const { tasks } = useTaskState();

  const total = tasks.length;
  const completed = tasks.filter(t => t.completed).length;
  const active = total - completed;
  const highPriority = tasks.filter(
    t => t.priority === "high" && !t.completed
  ).length;

  return (
    <div>
      <p>Total: {total} | Active: {active} | Completed: {completed}</p>
      {highPriority > 0 && (
        <p style={{ color: "red" }}>
          {highPriority} high-priority task{highPriority > 1 ? "s" : ""} remaining
        </p>
      )}
    </div>
  );
}
```

**Step 4: Compose everything**

```jsx
// App.jsx
import { TaskProvider } from "./TaskContext";

function App() {
  return (
    <TaskProvider>
      <h1>Task Manager</h1>
      <AddTaskForm />
      <TaskFilters />
      <TaskStats />
      <TaskList />
    </TaskProvider>
  );
}
```

Any component within `TaskProvider` can read state or dispatch actions without props being passed through intermediate components. The reducer guarantees that all state transitions follow the same rules, no matter which component triggers them.

---

## Handling Side Effects with useReducer

Reducers must be pure — they cannot make API calls, write to localStorage, or perform any other side effects. So where do side effects go?

The answer: **side effects happen where you dispatch**, not inside the reducer.

### Pattern: Async Actions

```jsx
function TaskManager() {
  const [state, dispatch] = useReducer(taskReducer, initialState);

  async function loadTasks() {
    dispatch({ type: "FETCH_START" });

    try {
      const response = await fetch("/api/tasks");
      const tasks = await response.json();
      dispatch({ type: "FETCH_SUCCESS", payload: tasks });
    } catch (err) {
      dispatch({ type: "FETCH_ERROR", payload: err.message });
    }
  }

  async function saveTask(taskData) {
    dispatch({ type: "SAVE_START" });

    try {
      const response = await fetch("/api/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(taskData),
      });
      const savedTask = await response.json();
      dispatch({ type: "SAVE_SUCCESS", payload: savedTask });
    } catch (err) {
      dispatch({ type: "SAVE_ERROR", payload: err.message });
    }
  }

  // ...
}
```

The reducer handles the state transitions:

```jsx
function taskReducer(state, action) {
  switch (action.type) {
    case "FETCH_START":
      return { ...state, isLoading: true, error: null };

    case "FETCH_SUCCESS":
      return { ...state, isLoading: false, tasks: action.payload };

    case "FETCH_ERROR":
      return { ...state, isLoading: false, error: action.payload };

    case "SAVE_START":
      return { ...state, isSaving: true };

    case "SAVE_SUCCESS":
      return {
        ...state,
        isSaving: false,
        tasks: [...state.tasks, action.payload],
      };

    case "SAVE_ERROR":
      return { ...state, isSaving: false, error: action.payload };

    // ... other cases
  }
}
```

### Pattern: Syncing with localStorage

Use `useEffect` to sync reducer state with localStorage:

```jsx
function App() {
  const [state, dispatch] = useReducer(todoReducer, null, () => {
    const saved = localStorage.getItem("todos");
    return saved ? JSON.parse(saved) : initialState;
  });

  // Sync to localStorage whenever state changes
  useEffect(() => {
    localStorage.setItem("todos", JSON.stringify(state));
  }, [state]);

  // ...
}
```

---

## Refactoring from useState to useReducer

Let us walk through a realistic refactoring. Here is a form component with complex validation state managed by `useState`:

### Before: Multiple useState Calls

```jsx
function RegistrationForm() {
  const [values, setValues] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  function handleChange(e) {
    const { name, value } = e.target;
    setValues(prev => ({ ...prev, [name]: value }));
    // Clear error when user types
    if (errors[name]) {
      setErrors(prev => {
        const next = { ...prev };
        delete next[name];
        return next;
      });
    }
  }

  function handleBlur(e) {
    const { name } = e.target;
    setTouched(prev => ({ ...prev, [name]: true }));
    validateField(name);
  }

  function validateField(name) {
    // ... validation logic that calls setErrors
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitError(null);
    setSubmitSuccess(false);

    try {
      await submitForm(values);
      setSubmitSuccess(true);
      setValues({ username: "", email: "", password: "", confirmPassword: "" });
      setErrors({});
      setTouched({});
    } catch (err) {
      setSubmitError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  // Lots of state updates scattered across many functions...
}
```

### After: Consolidated with useReducer

```jsx
const initialFormState = {
  values: {
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  },
  errors: {},
  touched: {},
  isSubmitting: false,
  submitError: null,
  submitSuccess: false,
};

function formReducer(state, action) {
  switch (action.type) {
    case "FIELD_CHANGE": {
      const newErrors = { ...state.errors };
      delete newErrors[action.payload.name];
      return {
        ...state,
        values: {
          ...state.values,
          [action.payload.name]: action.payload.value,
        },
        errors: newErrors,
        submitError: null,
      };
    }

    case "FIELD_BLUR":
      return {
        ...state,
        touched: {
          ...state.touched,
          [action.payload]: true,
        },
      };

    case "SET_FIELD_ERROR":
      return {
        ...state,
        errors: {
          ...state.errors,
          [action.payload.name]: action.payload.error,
        },
      };

    case "SET_ERRORS":
      return {
        ...state,
        errors: action.payload,
      };

    case "SUBMIT_START":
      return {
        ...state,
        isSubmitting: true,
        submitError: null,
        submitSuccess: false,
      };

    case "SUBMIT_SUCCESS":
      return {
        ...initialFormState,
        submitSuccess: true,
      };

    case "SUBMIT_ERROR":
      return {
        ...state,
        isSubmitting: false,
        submitError: action.payload,
      };

    case "RESET":
      return initialFormState;

    default:
      throw new Error(`Unknown action type: ${action.type}`);
  }
}
```

Now the component is clean:

```jsx
function RegistrationForm() {
  const [state, dispatch] = useReducer(formReducer, initialFormState);
  const { values, errors, touched, isSubmitting, submitError, submitSuccess } = state;

  function handleChange(e) {
    const { name, value } = e.target;
    dispatch({ type: "FIELD_CHANGE", payload: { name, value } });
  }

  function handleBlur(e) {
    const { name } = e.target;
    dispatch({ type: "FIELD_BLUR", payload: name });
    validateField(name);
  }

  function validateField(name) {
    const value = values[name];
    let error = null;

    switch (name) {
      case "username":
        if (value.length < 3) error = "Username must be at least 3 characters";
        break;
      case "email":
        if (!value.includes("@")) error = "Invalid email address";
        break;
      case "password":
        if (value.length < 8) error = "Password must be at least 8 characters";
        break;
      case "confirmPassword":
        if (value !== values.password) error = "Passwords do not match";
        break;
    }

    if (error) {
      dispatch({ type: "SET_FIELD_ERROR", payload: { name, error } });
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    dispatch({ type: "SUBMIT_START" });

    try {
      await submitForm(values);
      dispatch({ type: "SUBMIT_SUCCESS" });
    } catch (err) {
      dispatch({ type: "SUBMIT_ERROR", payload: err.message });
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {submitSuccess && <p style={{ color: "green" }}>Registration successful!</p>}
      {submitError && <p style={{ color: "red" }}>{submitError}</p>}

      <div>
        <input
          name="username"
          value={values.username}
          onChange={handleChange}
          onBlur={handleBlur}
          placeholder="Username"
        />
        {touched.username && errors.username && (
          <span style={{ color: "red" }}>{errors.username}</span>
        )}
      </div>

      <div>
        <input
          name="email"
          type="email"
          value={values.email}
          onChange={handleChange}
          onBlur={handleBlur}
          placeholder="Email"
        />
        {touched.email && errors.email && (
          <span style={{ color: "red" }}>{errors.email}</span>
        )}
      </div>

      <div>
        <input
          name="password"
          type="password"
          value={values.password}
          onChange={handleChange}
          onBlur={handleBlur}
          placeholder="Password"
        />
        {touched.password && errors.password && (
          <span style={{ color: "red" }}>{errors.password}</span>
        )}
      </div>

      <div>
        <input
          name="confirmPassword"
          type="password"
          value={values.confirmPassword}
          onChange={handleChange}
          onBlur={handleBlur}
          placeholder="Confirm password"
        />
        {touched.confirmPassword && errors.confirmPassword && (
          <span style={{ color: "red" }}>{errors.confirmPassword}</span>
        )}
      </div>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Registering..." : "Register"}
      </button>
      <button type="button" onClick={() => dispatch({ type: "RESET" })}>
        Reset
      </button>
    </form>
  );
}
```

The benefits after refactoring:

- **SUBMIT_SUCCESS resets everything at once** — no risk of forgetting a field
- **State transitions are explicit and named** — reading the reducer tells you every possible state change
- **The reducer is testable in isolation** — no component rendering needed
- **Adding new state is safe** — just add it to `initialFormState` and the relevant action cases

---

## Testing Reducers

One of the biggest advantages of `useReducer` is that the reducer function is a pure function that can be tested without rendering any components:

```jsx
// taskReducer.test.js
import { taskReducer, initialState } from "./taskReducer";

describe("taskReducer", () => {
  test("ADD_TASK adds a new task with correct defaults", () => {
    const action = {
      type: "ADD_TASK",
      payload: { title: "Learn testing" },
    };

    const newState = taskReducer(initialState, action);

    expect(newState.tasks).toHaveLength(1);
    expect(newState.tasks[0]).toEqual({
      id: 1,
      title: "Learn testing",
      priority: "medium",
      completed: false,
      createdAt: expect.any(String),
    });
    expect(newState.nextId).toBe(2);
  });

  test("TOGGLE_TASK toggles completion status", () => {
    const stateWithTask = {
      ...initialState,
      tasks: [{ id: 1, title: "Test", completed: false }],
    };

    const newState = taskReducer(stateWithTask, {
      type: "TOGGLE_TASK",
      payload: 1,
    });

    expect(newState.tasks[0].completed).toBe(true);

    // Toggle again
    const toggledBack = taskReducer(newState, {
      type: "TOGGLE_TASK",
      payload: 1,
    });

    expect(toggledBack.tasks[0].completed).toBe(false);
  });

  test("DELETE_TASK removes the correct task", () => {
    const stateWithTasks = {
      ...initialState,
      tasks: [
        { id: 1, title: "First" },
        { id: 2, title: "Second" },
        { id: 3, title: "Third" },
      ],
    };

    const newState = taskReducer(stateWithTasks, {
      type: "DELETE_TASK",
      payload: 2,
    });

    expect(newState.tasks).toHaveLength(2);
    expect(newState.tasks.map(t => t.id)).toEqual([1, 3]);
  });

  test("CLEAR_COMPLETED removes only completed tasks", () => {
    const stateWithTasks = {
      ...initialState,
      tasks: [
        { id: 1, title: "Done", completed: true },
        { id: 2, title: "Not done", completed: false },
        { id: 3, title: "Also done", completed: true },
      ],
    };

    const newState = taskReducer(stateWithTasks, {
      type: "CLEAR_COMPLETED",
    });

    expect(newState.tasks).toHaveLength(1);
    expect(newState.tasks[0].title).toBe("Not done");
  });

  test("throws error for unknown action type", () => {
    expect(() => {
      taskReducer(initialState, { type: "UNKNOWN" });
    }).toThrow("Unknown action type: UNKNOWN");
  });
});
```

Notice how clean these tests are — no mocking, no rendering, no async. Just input, output, and assertions.

---

## Mini Project: Expense Tracker

Let us build a complete expense tracker that demonstrates `useReducer` with Context, filtering, computed values, and localStorage persistence.

```jsx
// expenseReducer.js

export const initialState = {
  transactions: [],
  nextId: 1,
  filter: {
    type: "all", // "all" | "income" | "expense"
    startDate: "",
    endDate: "",
    category: "all",
  },
};

export function expenseReducer(state, action) {
  switch (action.type) {
    case "ADD_TRANSACTION":
      return {
        ...state,
        transactions: [
          ...state.transactions,
          {
            id: state.nextId,
            description: action.payload.description,
            amount: action.payload.amount,
            type: action.payload.transactionType,
            category: action.payload.category,
            date: action.payload.date || new Date().toISOString().split("T")[0],
          },
        ],
        nextId: state.nextId + 1,
      };

    case "DELETE_TRANSACTION":
      return {
        ...state,
        transactions: state.transactions.filter(
          t => t.id !== action.payload
        ),
      };

    case "EDIT_TRANSACTION":
      return {
        ...state,
        transactions: state.transactions.map(t =>
          t.id === action.payload.id ? { ...t, ...action.payload.updates } : t
        ),
      };

    case "SET_FILTER":
      return {
        ...state,
        filter: { ...state.filter, ...action.payload },
      };

    case "RESET_FILTERS":
      return {
        ...state,
        filter: initialState.filter,
      };

    case "LOAD_DATA":
      return {
        ...action.payload,
      };

    default:
      throw new Error(`Unknown action type: ${action.type}`);
  }
}
```

```jsx
// ExpenseContext.jsx
import { createContext, useContext, useReducer, useEffect } from "react";
import { expenseReducer, initialState } from "./expenseReducer";

const ExpenseStateContext = createContext(null);
const ExpenseDispatchContext = createContext(null);

function loadFromStorage() {
  try {
    const saved = localStorage.getItem("expenseTracker");
    return saved ? JSON.parse(saved) : initialState;
  } catch {
    return initialState;
  }
}

export function ExpenseProvider({ children }) {
  const [state, dispatch] = useReducer(expenseReducer, null, loadFromStorage);

  useEffect(() => {
    localStorage.setItem("expenseTracker", JSON.stringify(state));
  }, [state]);

  return (
    <ExpenseStateContext.Provider value={state}>
      <ExpenseDispatchContext.Provider value={dispatch}>
        {children}
      </ExpenseDispatchContext.Provider>
    </ExpenseStateContext.Provider>
  );
}

export function useExpenseState() {
  const context = useContext(ExpenseStateContext);
  if (context === null) {
    throw new Error("useExpenseState must be used within ExpenseProvider");
  }
  return context;
}

export function useExpenseDispatch() {
  const context = useContext(ExpenseDispatchContext);
  if (context === null) {
    throw new Error("useExpenseDispatch must be used within ExpenseProvider");
  }
  return context;
}
```

```jsx
// AddTransactionForm.jsx
import { useState } from "react";
import { useExpenseDispatch } from "./ExpenseContext";

const categories = [
  "Food", "Transport", "Housing", "Entertainment",
  "Utilities", "Healthcare", "Salary", "Freelance", "Other",
];

function AddTransactionForm() {
  const dispatch = useExpenseDispatch();
  const [form, setForm] = useState({
    description: "",
    amount: "",
    transactionType: "expense",
    category: "Other",
    date: new Date().toISOString().split("T")[0],
  });

  function handleChange(e) {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (!form.description.trim() || !form.amount) return;

    dispatch({
      type: "ADD_TRANSACTION",
      payload: {
        ...form,
        amount: parseFloat(form.amount),
      },
    });

    setForm(prev => ({
      ...prev,
      description: "",
      amount: "",
    }));
  }

  return (
    <form onSubmit={handleSubmit}>
      <h3>Add Transaction</h3>

      <div>
        <label>
          <input
            type="radio"
            name="transactionType"
            value="income"
            checked={form.transactionType === "income"}
            onChange={handleChange}
          />
          Income
        </label>
        <label>
          <input
            type="radio"
            name="transactionType"
            value="expense"
            checked={form.transactionType === "expense"}
            onChange={handleChange}
          />
          Expense
        </label>
      </div>

      <input
        name="description"
        value={form.description}
        onChange={handleChange}
        placeholder="Description"
        required
      />

      <input
        name="amount"
        type="number"
        step="0.01"
        min="0.01"
        value={form.amount}
        onChange={handleChange}
        placeholder="Amount"
        required
      />

      <select name="category" value={form.category} onChange={handleChange}>
        {categories.map(cat => (
          <option key={cat} value={cat}>{cat}</option>
        ))}
      </select>

      <input
        name="date"
        type="date"
        value={form.date}
        onChange={handleChange}
      />

      <button type="submit">
        Add {form.transactionType === "income" ? "Income" : "Expense"}
      </button>
    </form>
  );
}
```

```jsx
// BalanceSummary.jsx
import { useExpenseState } from "./ExpenseContext";

function BalanceSummary() {
  const { transactions } = useExpenseState();

  const income = transactions
    .filter(t => t.type === "income")
    .reduce((sum, t) => sum + t.amount, 0);

  const expenses = transactions
    .filter(t => t.type === "expense")
    .reduce((sum, t) => sum + t.amount, 0);

  const balance = income - expenses;

  return (
    <div>
      <h2>Balance: ${balance.toFixed(2)}</h2>
      <div style={{ display: "flex", gap: "2rem" }}>
        <div>
          <h4>Income</h4>
          <p style={{ color: "green" }}>+${income.toFixed(2)}</p>
        </div>
        <div>
          <h4>Expenses</h4>
          <p style={{ color: "red" }}>-${expenses.toFixed(2)}</p>
        </div>
      </div>
    </div>
  );
}
```

```jsx
// TransactionFilters.jsx
import { useExpenseState, useExpenseDispatch } from "./ExpenseContext";

function TransactionFilters() {
  const { filter } = useExpenseState();
  const dispatch = useExpenseDispatch();

  return (
    <div>
      <h3>Filters</h3>
      <div>
        {["all", "income", "expense"].map(type => (
          <button
            key={type}
            onClick={() => dispatch({ type: "SET_FILTER", payload: { type } })}
            style={{ fontWeight: filter.type === type ? "bold" : "normal" }}
          >
            {type.charAt(0).toUpperCase() + type.slice(1)}
          </button>
        ))}
      </div>

      <div>
        <label>
          From:
          <input
            type="date"
            value={filter.startDate}
            onChange={e =>
              dispatch({
                type: "SET_FILTER",
                payload: { startDate: e.target.value },
              })
            }
          />
        </label>
        <label>
          To:
          <input
            type="date"
            value={filter.endDate}
            onChange={e =>
              dispatch({
                type: "SET_FILTER",
                payload: { endDate: e.target.value },
              })
            }
          />
        </label>
      </div>

      <button onClick={() => dispatch({ type: "RESET_FILTERS" })}>
        Clear Filters
      </button>
    </div>
  );
}
```

```jsx
// TransactionList.jsx
import { useExpenseState, useExpenseDispatch } from "./ExpenseContext";

function TransactionList() {
  const { transactions, filter } = useExpenseState();
  const dispatch = useExpenseDispatch();

  const filteredTransactions = transactions
    .filter(t => {
      if (filter.type !== "all" && t.type !== filter.type) return false;
      if (filter.category !== "all" && t.category !== filter.category) return false;
      if (filter.startDate && t.date < filter.startDate) return false;
      if (filter.endDate && t.date > filter.endDate) return false;
      return true;
    })
    .sort((a, b) => b.date.localeCompare(a.date));

  if (filteredTransactions.length === 0) {
    return <p>No transactions found.</p>;
  }

  return (
    <div>
      <h3>Transactions ({filteredTransactions.length})</h3>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {filteredTransactions.map(t => (
          <li
            key={t.id}
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              padding: "0.5rem",
              borderLeft: `4px solid ${t.type === "income" ? "green" : "red"}`,
              marginBottom: "0.5rem",
              backgroundColor: "#f9f9f9",
            }}
          >
            <div>
              <strong>{t.description}</strong>
              <br />
              <small>
                {t.category} | {t.date}
              </small>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
              <span
                style={{
                  color: t.type === "income" ? "green" : "red",
                  fontWeight: "bold",
                }}
              >
                {t.type === "income" ? "+" : "-"}${t.amount.toFixed(2)}
              </span>
              <button
                onClick={() =>
                  dispatch({ type: "DELETE_TRANSACTION", payload: t.id })
                }
              >
                Delete
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

```jsx
// App.jsx
import { ExpenseProvider } from "./ExpenseContext";

function App() {
  return (
    <ExpenseProvider>
      <div style={{ maxWidth: 600, margin: "0 auto", padding: "1rem" }}>
        <h1>Expense Tracker</h1>
        <BalanceSummary />
        <AddTransactionForm />
        <TransactionFilters />
        <TransactionList />
      </div>
    </ExpenseProvider>
  );
}
```

This mini project demonstrates:

- **useReducer** for centralized state management
- **Context** for providing state to deeply nested components
- **Split contexts** for performance (state vs dispatch)
- **Lazy initialization** from localStorage
- **useEffect** for persisting state
- **Computed values** derived from reducer state (balance, filtered lists)
- **Clean separation** between state logic (reducer) and UI (components)

---

## Common Mistakes

### Mistake 1: Mutating State in the Reducer

```jsx
// WRONG — mutating state directly
function reducer(state, action) {
  switch (action.type) {
    case "ADD_ITEM":
      state.items.push(action.payload); // Mutation!
      return state; // Same reference — React will not re-render
  }
}

// CORRECT — return a new object
function reducer(state, action) {
  switch (action.type) {
    case "ADD_ITEM":
      return {
        ...state,
        items: [...state.items, action.payload],
      };
  }
}
```

### Mistake 2: Side Effects Inside the Reducer

```jsx
// WRONG — side effects in reducer
function reducer(state, action) {
  switch (action.type) {
    case "SAVE":
      localStorage.setItem("data", JSON.stringify(state)); // Side effect!
      fetch("/api/save", { method: "POST", body: JSON.stringify(state) }); // Side effect!
      return state;
  }
}

// CORRECT — side effects happen outside the reducer
function Component() {
  const [state, dispatch] = useReducer(reducer, initialState);

  useEffect(() => {
    localStorage.setItem("data", JSON.stringify(state));
  }, [state]);
}
```

### Mistake 3: Forgetting the Default Case

```jsx
// WRONG — returns undefined for unknown actions
function reducer(state, action) {
  switch (action.type) {
    case "INCREMENT":
      return { count: state.count + 1 };
    // No default — if you dispatch a typo like "INCRMENT",
    // the reducer returns undefined and your app breaks
  }
}

// CORRECT — throw for unknown actions to catch typos early
function reducer(state, action) {
  switch (action.type) {
    case "INCREMENT":
      return { count: state.count + 1 };
    default:
      throw new Error(`Unknown action type: ${action.type}`);
  }
}
```

### Mistake 4: Overusing useReducer

```jsx
// OVERKILL — simple boolean toggle does not need a reducer
const [state, dispatch] = useReducer(
  (state, action) => {
    switch (action.type) {
      case "TOGGLE":
        return { isOpen: !state.isOpen };
      default:
        throw new Error();
    }
  },
  { isOpen: false }
);

// JUST USE useState
const [isOpen, setIsOpen] = useState(false);
```

### Mistake 5: Putting Derived State in the Reducer

```jsx
// WRONG — storing computed values in state
function reducer(state, action) {
  switch (action.type) {
    case "ADD_ITEM":
      const newItems = [...state.items, action.payload];
      return {
        ...state,
        items: newItems,
        totalPrice: newItems.reduce((sum, item) => sum + item.price, 0),
        itemCount: newItems.length,
      };
  }
}

// CORRECT — compute derived values during render
function Component() {
  const [state, dispatch] = useReducer(reducer, initialState);
  const totalPrice = state.items.reduce((sum, item) => sum + item.price, 0);
  const itemCount = state.items.length;
}
```

---

## Best Practices

1. **Keep reducers pure** — No API calls, no localStorage, no random values, no `Date.now()` inside reducers. Pass those values in through the action payload.

2. **Name actions after what happened, not what should change** — Use `"ORDER_PLACED"` instead of `"SET_ORDER_STATUS_TO_CONFIRMED"`. The reducer decides what state changes result from an event.

3. **Use a single state object** — Group related state into one reducer state object rather than using multiple `useReducer` calls for tightly coupled state.

4. **Throw on unknown action types** — This catches typos immediately during development rather than causing silent bugs.

5. **Define reducers outside components** — Reducers do not need component scope. Defining them outside keeps the component clean and makes the reducer reusable and testable.

6. **Split contexts for performance** — When using `useReducer` with Context, create separate state and dispatch contexts so components that only dispatch do not re-render on state changes.

7. **Start with useState, upgrade when needed** — Do not reach for `useReducer` by default. Start with `useState` and refactor to `useReducer` when you notice the patterns described earlier (scattered state updates, multiple values changing together, complex transitions).

---

## Summary

In this chapter, you learned:

- **useReducer** centralizes state transitions into a single, pure reducer function
- **Actions** describe what happened; the **reducer** decides how state changes
- **dispatch** is stable across renders, making it safe to pass through Context or to child components
- **useState vs useReducer** is a spectrum — use `useState` for simple state, `useReducer` for complex state with many transitions
- **useReducer + Context** creates a scalable state management system similar to Redux
- **Split contexts** (state and dispatch) prevent unnecessary re-renders
- **Reducers are testable** as pure functions — no component rendering needed
- **Side effects** belong outside the reducer — use `useEffect` or event handlers
- **Lazy initialization** lets you compute initial state from expensive operations like localStorage

The reducer pattern is one of the most important patterns in React development. It scales from simple todo lists to complex application state. Understanding it well will also prepare you for state management libraries like Redux and Zustand, which are built on the same principles.

---

## Interview Questions

1. **What is the difference between useState and useReducer? When would you choose one over the other?**

   `useState` is best for simple, independent state values. `useReducer` is better when you have complex state objects where multiple values need to change together, when state transitions involve logic, or when you want to centralize and test state updates. The key advantage of `useReducer` is that all state transitions are defined in one place (the reducer), making them explicit, testable, and impossible to get into invalid combinations.

2. **What are the rules for writing a reducer function?**

   A reducer must be a pure function — same inputs always produce the same output, no side effects (no API calls, no localStorage, no random values). It must never mutate the existing state; instead, it must return a new state object. It should handle every possible action type and throw an error for unknown types to catch bugs early. It should be defined outside the component since it does not need access to props or hooks.

3. **Why is the dispatch function stable across renders, and why does that matter?**

   React guarantees that `dispatch` maintains the same identity across re-renders (referential stability). This matters because you can safely pass `dispatch` to child components wrapped in `React.memo` without causing unnecessary re-renders, include it in `useEffect` dependency arrays without triggering the effect, and provide it through Context without performance concerns.

4. **How do you handle asynchronous operations with useReducer?**

   Since reducers must be pure, async operations happen outside the reducer. You dispatch an action before the async operation starts (e.g., `FETCH_START`), perform the async work in an event handler or effect, then dispatch a success or error action when it completes. The reducer handles each action synchronously, updating loading, data, and error state accordingly.

5. **Explain the pattern of combining useReducer with Context. Why split state and dispatch into separate contexts?**

   You create a provider component that uses `useReducer`, then provides state and dispatch through Context so any descendant can read state or dispatch actions. Splitting into two contexts is a performance optimization: components that only dispatch (like forms) subscribe only to the dispatch context, which is stable and never triggers re-renders. Components that only read state subscribe only to the state context. This prevents unnecessary re-renders across the component tree.

6. **What is lazy initialization in useReducer, and when would you use it?**

   Lazy initialization uses the third argument of `useReducer`: `useReducer(reducer, initArg, initFunction)`. React calls `initFunction(initArg)` only once during the first render to compute the initial state. Use it when computing the initial state is expensive — for example, reading from localStorage or parsing a large data structure — so the computation does not run on every render.

---

## Practice Exercises

### Exercise 1: Undo/Redo System

Build a drawing tool state manager that supports undo and redo. The reducer should track a history of states. Implement these actions: `DRAW` (adds a shape), `UNDO` (goes back one step), `REDO` (goes forward one step), and `CLEAR` (resets everything). The state should contain `past` (array of previous states), `present` (current shapes), and `future` (array of undone states).

**Hints:**
- On `DRAW`: push current `present` to `past`, update `present`, clear `future`
- On `UNDO`: push `present` to `future`, pop from `past` into `present`
- On `REDO`: push `present` to `past`, pop from `future` into `present`

### Exercise 2: Multi-Step Wizard with Validation

Build a multi-step form wizard using `useReducer`. The form should have three steps: Personal Info, Address, and Review. The reducer should manage the current step, form values for each step, validation errors, and whether each step has been completed. Include actions for: `NEXT_STEP`, `PREV_STEP`, `UPDATE_FIELD`, `VALIDATE_STEP`, and `SUBMIT`.

### Exercise 3: Shopping Cart with Discounts

Build a shopping cart using `useReducer` and Context. Support adding items, removing items, updating quantities, applying discount codes (percentage or fixed amount), and calculating totals with discounts. The reducer should manage the items array, applied discount, and derived totals. Include a `CHECKOUT` action that resets the cart.

### Exercise 4: Chat Application State

Build the state management for a chat application using `useReducer`. Support multiple conversations, sending and receiving messages, marking messages as read, and typing indicators. The state should track: an array of conversations, the active conversation ID, and a map of typing users. Test your reducer with at least five different scenarios.

---

## What Is Next?

In Chapter 15, we will explore **React Router** — how to add navigation and multiple pages to your React application. You will learn about client-side routing, route parameters, nested routes, and protecting routes that require authentication.
