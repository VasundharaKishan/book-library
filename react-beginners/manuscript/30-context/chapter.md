# Chapter 30: Context — Sharing Data Without Passing Props

---

## What You Will Learn

- What the prop drilling problem is and why it is painful
- What Context is and how it solves prop drilling
- The three steps to using Context: `createContext`, `Provider`, and `useContext`
- How to share a theme (light/dark mode) across components
- How to share the current user across components
- When to use Context and when NOT to use it
- How to combine Context with `useReducer` for mini state management

## Why This Chapter Matters

Imagine you live in an apartment building. You receive a package, but it is for someone on the 5th floor. You cannot just teleport it there. You hand it to the person on the 2nd floor, who hands it to the 3rd floor, who hands it to the 4th floor, who finally gives it to the 5th floor.

That is what passing props through many levels of components feels like. It is tedious. Everyone in the chain has to handle the package, even though they do not need it.

React Context solves this. It is like an elevator that takes the package directly to the 5th floor. No middlemen needed.

This is one of the most useful features in React. It will change how you structure your applications.

---

## The Prop Drilling Problem

**Prop drilling** is when you pass data through many levels of components, even though only the deepest component needs it.

Let us see an example. Imagine you have a user's name that you want to display in a deeply nested component.

```
App (has the user's name)
  └── Layout
        └── Sidebar
              └── UserPanel
                    └── UserGreeting (needs the user's name)
```

Without Context, you would have to pass the name through every level:

```jsx
function App() {
  const userName = 'Alice';
  return <Layout userName={userName} />;
}

function Layout({ userName }) {
  // Layout does not use userName. It just passes it along.
  return <Sidebar userName={userName} />;
}

function Sidebar({ userName }) {
  // Sidebar does not use userName either. Just passing it along.
  return <UserPanel userName={userName} />;
}

function UserPanel({ userName }) {
  // Still just passing it along...
  return <UserGreeting userName={userName} />;
}

function UserGreeting({ userName }) {
  // Finally! This is the component that actually uses it.
  return <p>Hello, {userName}!</p>;
}
```

This is prop drilling. Four components receive `userName` as a prop, but only one actually uses it. The other three are just middlemen.

### Why Prop Drilling Is a Problem

1. **It is tedious.** You have to add the prop to every component in the chain.
2. **It is fragile.** If you rename the prop, you have to rename it everywhere.
3. **It clutters your code.** Components receive props they do not use.
4. **It makes refactoring hard.** Moving a component means rewiring all the props.

Here is what prop drilling looks like as a diagram:

```
  Prop Drilling (without Context):

  +--------+
  |  App   |  userName="Alice"
  +---+----+
      |
      | passes userName
      v
  +--------+
  | Layout |  userName="Alice"  (does not use it)
  +---+----+
      |
      | passes userName
      v
  +----------+
  | Sidebar  |  userName="Alice"  (does not use it)
  +---+------+
      |
      | passes userName
      v
  +-----------+
  | UserPanel |  userName="Alice"  (does not use it)
  +---+-------+
      |
      | passes userName
      v
  +--------------+
  | UserGreeting |  userName="Alice"  (USES it!)
  +--------------+
```

---

## What Is Context?

**Context** is like a radio station. One component broadcasts data, and any component anywhere in the tree can tune in and receive it. No passing through middlemen.

```
  Context (like a radio broadcast):

  +--------+
  |  App   |  Broadcasts: userName="Alice"
  +---+----+        |
      |             |  (broadcast signal)
      v             |
  +--------+        |
  | Layout |        |  (does NOT need to receive userName)
  +---+----+        |
      |             |
      v             |
  +----------+      |
  | Sidebar  |      |  (does NOT need to receive userName)
  +---+------+      |
      |             |
      v             |
  +-----------+     |
  | UserPanel |     |  (does NOT need to receive userName)
  +---+-------+     |
      |             |
      v             |
  +--------------+  |
  | UserGreeting |<-+  Tunes in: receives userName="Alice"
  +--------------+
```

The middle components (Layout, Sidebar, UserPanel) do not need to know about `userName` at all. Only the component that actually needs the data tunes in.

---

## The Three Steps to Using Context

Using Context involves three steps. Think of it as setting up a radio system.

### Step 1: Create the Context (Build the Radio Station)

```jsx
import { createContext } from 'react';

const UserContext = createContext('Guest');
```

`createContext` creates a new Context. The argument (`'Guest'`) is the **default value**. This is used only if a component tries to read the Context but there is no Provider above it.

You usually put this in its own file so multiple components can import it.

### Step 2: Provide the Context (Start Broadcasting)

```jsx
import { UserContext } from './UserContext';

function App() {
  const userName = 'Alice';

  return (
    <UserContext.Provider value={userName}>
      <Layout />
    </UserContext.Provider>
  );
}
```

The `Provider` wraps your component tree. It broadcasts the `value` to every component inside it. Any component inside `<UserContext.Provider>` can access `userName`.

### Step 3: Use the Context (Tune In)

```jsx
import { useContext } from 'react';
import { UserContext } from './UserContext';

function UserGreeting() {
  const userName = useContext(UserContext);

  return <p>Hello, {userName}!</p>;
}
```

`useContext` reads the value from the nearest Provider above it. That is it. No props needed. The component gets the data directly.

---

## Complete Example: Theme Switching

Let us build a real example. We will create a light/dark theme that any component can access.

### Step 1: Create the Context

```jsx
// ThemeContext.js
import { createContext } from 'react';

export const ThemeContext = createContext('light');
```

### Step 2: Provide the Context in App

```jsx
// App.jsx
import { useState } from 'react';
import { ThemeContext } from './ThemeContext';
import Page from './Page';

function App() {
  const [theme, setTheme] = useState('light');

  function toggleTheme() {
    setTheme(theme === 'light' ? 'dark' : 'light');
  }

  return (
    <ThemeContext.Provider value={theme}>
      <div>
        <button onClick={toggleTheme}>
          Switch to {theme === 'light' ? 'Dark' : 'Light'} Mode
        </button>
        <Page />
      </div>
    </ThemeContext.Provider>
  );
}

export default App;
```

### Step 3: Use the Context in Any Component

```jsx
// Page.jsx
import Header from './Header';
import Content from './Content';

function Page() {
  // Page does not need to know about the theme!
  return (
    <div>
      <Header />
      <Content />
    </div>
  );
}

export default Page;
```

```jsx
// Header.jsx
import { useContext } from 'react';
import { ThemeContext } from './ThemeContext';

function Header() {
  const theme = useContext(ThemeContext);

  const style = {
    backgroundColor: theme === 'dark' ? '#333' : '#fff',
    color: theme === 'dark' ? '#fff' : '#333',
    padding: '20px'
  };

  return (
    <header style={style}>
      <h1>My Website</h1>
    </header>
  );
}

export default Header;
```

```jsx
// Content.jsx
import { useContext } from 'react';
import { ThemeContext } from './ThemeContext';

function Content() {
  const theme = useContext(ThemeContext);

  const style = {
    backgroundColor: theme === 'dark' ? '#222' : '#f9f9f9',
    color: theme === 'dark' ? '#ddd' : '#333',
    padding: '20px'
  };

  return (
    <main style={style}>
      <p>This content changes with the theme.</p>
      <p>Current theme: {theme}</p>
    </main>
  );
}

export default Content;
```

**Expected output (light mode):**

```
[Switch to Dark Mode]

My Website
-----------------------
This content changes with the theme.
Current theme: light
```

**Expected output (after clicking the button, dark mode):**

```
[Switch to Light Mode]

My Website                    (white text on dark background)
-----------------------
This content changes           (light gray text on very dark background)
with the theme.
Current theme: dark
```

Notice how `Page` does not receive or pass the theme. `Header` and `Content` get the theme directly from Context. No prop drilling.

---

## Complete Example: Current User

Here is another common use case: sharing the current user's information across your app.

```jsx
// UserContext.js
import { createContext } from 'react';

export const UserContext = createContext(null);
```

```jsx
// App.jsx
import { useState } from 'react';
import { UserContext } from './UserContext';
import Dashboard from './Dashboard';

function App() {
  const [user, setUser] = useState({
    name: 'Alice',
    email: 'alice@example.com',
    role: 'admin'
  });

  return (
    <UserContext.Provider value={user}>
      <Dashboard />
    </UserContext.Provider>
  );
}

export default App;
```

```jsx
// Dashboard.jsx
import Navbar from './Navbar';
import MainContent from './MainContent';

function Dashboard() {
  // Dashboard does not need to know about the user
  return (
    <div>
      <Navbar />
      <MainContent />
    </div>
  );
}

export default Dashboard;
```

```jsx
// Navbar.jsx
import { useContext } from 'react';
import { UserContext } from './UserContext';

function Navbar() {
  const user = useContext(UserContext);

  return (
    <nav>
      <span>Welcome, {user.name}</span>
      <span>Role: {user.role}</span>
    </nav>
  );
}

export default Navbar;
```

```jsx
// MainContent.jsx
import { useContext } from 'react';
import { UserContext } from './UserContext';

function MainContent() {
  const user = useContext(UserContext);

  return (
    <main>
      <h2>Dashboard</h2>
      <p>Logged in as: {user.email}</p>
    </main>
  );
}

export default MainContent;
```

**Expected output:**

```
Welcome, Alice    Role: admin
---------------------------------
Dashboard
Logged in as: alice@example.com
```

Both `Navbar` and `MainContent` access the user directly. `Dashboard` does not need to pass it along.

---

## When to Use Context

Context is best for data that many components need at different levels of your tree.

**Good uses for Context:**
- Theme (light/dark mode)
- Current user information
- Language/locale setting
- UI preferences (font size, sidebar open/closed)

**When NOT to use Context:**
- Data only needed by one component (just use local state)
- Data only needed by a parent and its direct child (just pass it as a prop)
- Data that changes very frequently (Context re-renders all consumers)

### The Simple Rule

> If you are passing a prop through more than two levels of components, and the middle components do not use it, consider Context.

If only a parent and child need to share data, a prop is simpler and better.

---

## Context + useReducer: Mini State Management

Here is something powerful. You can combine Context and `useReducer` to create a mini state management system. This is like having a simpler version of libraries like Redux, built right into React.

The idea is:
1. Use `useReducer` to manage complex state
2. Use Context to share that state (and the dispatch function) with all components

```jsx
// TodoContext.js
import { createContext } from 'react';

export const TodoContext = createContext(null);
```

```jsx
// App.jsx
import { useReducer } from 'react';
import { TodoContext } from './TodoContext';
import TodoList from './TodoList';
import AddTodo from './AddTodo';
import TodoStats from './TodoStats';

function todoReducer(state, action) {
  switch (action.type) {
    case 'add':
      return [
        ...state,
        { id: Date.now(), text: action.text, done: false }
      ];
    case 'toggle':
      return state.map(todo =>
        todo.id === action.id
          ? { ...todo, done: !todo.done }
          : todo
      );
    case 'delete':
      return state.filter(todo => todo.id !== action.id);
    default:
      return state;
  }
}

function App() {
  const [todos, dispatch] = useReducer(todoReducer, []);

  return (
    <TodoContext.Provider value={{ todos, dispatch }}>
      <h1>My Todos</h1>
      <AddTodo />
      <TodoList />
      <TodoStats />
    </TodoContext.Provider>
  );
}

export default App;
```

Notice that we pass both `todos` and `dispatch` in the Provider value. This way, any component can read the to-do list and also send actions to update it.

```jsx
// AddTodo.jsx
import { useState, useContext } from 'react';
import { TodoContext } from './TodoContext';

function AddTodo() {
  const [text, setText] = useState('');
  const { dispatch } = useContext(TodoContext);

  function handleAdd() {
    if (text.trim() === '') return;
    dispatch({ type: 'add', text });
    setText('');
  }

  return (
    <div>
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Add a task..."
      />
      <button onClick={handleAdd}>Add</button>
    </div>
  );
}

export default AddTodo;
```

```jsx
// TodoList.jsx
import { useContext } from 'react';
import { TodoContext } from './TodoContext';

function TodoList() {
  const { todos, dispatch } = useContext(TodoContext);

  return (
    <ul>
      {todos.map(todo => (
        <li key={todo.id}>
          <span
            style={{
              textDecoration: todo.done ? 'line-through' : 'none'
            }}
          >
            {todo.text}
          </span>
          <button onClick={() => dispatch({ type: 'toggle', id: todo.id })}>
            {todo.done ? 'Undo' : 'Done'}
          </button>
          <button onClick={() => dispatch({ type: 'delete', id: todo.id })}>
            Delete
          </button>
        </li>
      ))}
    </ul>
  );
}

export default TodoList;
```

```jsx
// TodoStats.jsx
import { useContext } from 'react';
import { TodoContext } from './TodoContext';

function TodoStats() {
  const { todos } = useContext(TodoContext);

  const total = todos.length;
  const completed = todos.filter(t => t.done).length;
  const remaining = total - completed;

  return (
    <p>
      Total: {total} | Completed: {completed} | Remaining: {remaining}
    </p>
  );
}

export default TodoStats;
```

**Expected output:**

```
My Todos

[Add a task...    ] [Add]

- Buy groceries     [Done] [Delete]
- Walk the dog      [Done] [Delete]

Total: 2 | Completed: 0 | Remaining: 2
```

### Why This Is Powerful

Look at the component tree:

```
App (has the reducer)
  ├── AddTodo      (uses dispatch to add)
  ├── TodoList     (uses todos and dispatch)
  └── TodoStats    (uses todos)
```

Every component gets exactly what it needs directly from Context. No prop drilling. All state update logic is in one reducer function. This is a clean, organized pattern that works well for medium-sized applications.

---

## Quick Summary

**Prop drilling** is passing data through many component levels. It is tedious and messy.

**Context** lets you broadcast data so any component can access it directly. No middlemen needed.

Context has three steps: **create** the context, **provide** it (wrap your tree), and **consume** it (use `useContext`).

Combining **Context + useReducer** gives you a mini state management system. Share both the state and the dispatch function through Context.

Use Context for data that many components need. Use regular props for data shared between a parent and its direct children.

---

## Key Points to Remember

1. **Context solves prop drilling.** It lets you share data without passing props through every level.

2. **Three steps: create, provide, consume.** Use `createContext`, wrap with `Provider`, read with `useContext`.

3. **The Provider sets the value.** Every component inside the Provider can access that value.

4. **`useContext` reads from the nearest Provider above.** If there are multiple Providers for the same Context, the component uses the closest one.

5. **Context is not for everything.** Use it for data that many components need at different levels. For simple parent-to-child data, use props.

6. **You can put objects in Context.** Pass `value={{ todos, dispatch }}` to share both data and functions.

7. **Context + useReducer is a powerful combo.** It gives you centralized state management without installing extra libraries.

---

## Practice Questions

1. What is prop drilling? Why is it a problem?

2. What are the three steps to use Context in React?

3. What is the default value in `createContext` used for?

4. Look at this code. What will `UserGreeting` display?

```jsx
const NameContext = createContext('Guest');

function App() {
  return (
    <NameContext.Provider value="Bob">
      <UserGreeting />
    </NameContext.Provider>
  );
}

function UserGreeting() {
  const name = useContext(NameContext);
  return <p>Hello, {name}!</p>;
}
```

5. When should you use Context instead of props? When should you stick with props?

---

## Exercises

### Exercise 1: Language Switcher

Create a `LanguageContext` that stores the current language (`'en'` or `'es'`). Build:
- A `LanguageSwitcher` component with a button to toggle between English and Spanish
- A `Greeting` component that displays "Hello" (in English) or "Hola" (in Spanish)
- Both components should use Context to get and change the language

### Exercise 2: Theme with Multiple Properties

Expand the theme example from this chapter. Instead of just `'light'` or `'dark'`, make the theme an object:

```jsx
const lightTheme = {
  background: '#ffffff',
  text: '#333333',
  primary: '#0066cc'
};
```

Create a `Card` component and a `Button` component that both read from this theme Context.

### Exercise 3: Counter with Context + useReducer

Build a counter that uses `useReducer` for the logic and Context to share it. Create three separate components:
- `CounterDisplay` — shows the current count
- `CounterButtons` — has Add, Subtract, and Reset buttons
- `CounterHistory` — shows the highest count reached

All three components should access the same state through Context.

---

## What Is Next?

You now know how to share data across your app with Context and manage complex state with `useReducer`. These are built-in React tools that cover many real-world needs.

But have you noticed something? In our examples, we keep writing similar patterns. The `useFetch` logic (loading, error, data) appears in many components. A toggle (true/false) with a flip function appears in many places. The local storage read/write pattern keeps repeating.

In the next chapter, you will learn how to create **custom hooks** — your own reusable hooks that package up common logic. Instead of copying and pasting the same `useState` + `useEffect` pattern, you will wrap it in a custom hook and reuse it everywhere.
