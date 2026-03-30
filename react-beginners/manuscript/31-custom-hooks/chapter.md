# Chapter 31: Custom Hooks — Making Your Own Hooks

---

## What You Will Learn

- What a custom hook is and why you would create one
- The one rule: custom hooks must start with "use"
- How to build `useToggle` — a simple boolean toggle hook
- How to build `useLocalStorage` — a hook that saves state to the browser
- How to build `useFetch` — a reusable data fetching hook
- When to extract a custom hook from your component
- That custom hooks share logic, not state

## Why This Chapter Matters

Have you ever written the same code in two different components? Maybe both components need to fetch data from an API. Or both need to toggle something on and off. Or both need to save something to local storage.

Copying and pasting code is bad. If you find a bug, you have to fix it in every place you copied it. If you want to improve the logic, you have to update it everywhere.

Custom hooks solve this problem. They let you take a piece of logic — any combination of `useState`, `useEffect`, or other hooks — and wrap it up in a reusable function. Then any component can use that logic by calling your hook.

Think of it this way. React gives you built-in tools like `useState` and `useEffect`. Custom hooks let you build **your own tools** from those built-in ones. It is like combining a hammer and nails into a "hang a picture" tool.

---

## What Is a Custom Hook?

A **custom hook** is a regular JavaScript function that:

1. Starts with the word `use` (like `useToggle`, `useFetch`, `useWindowSize`)
2. Uses other hooks inside it (like `useState`, `useEffect`, `useContext`)

That is it. There is nothing magical about it. It is just a function.

Here is the simplest possible custom hook:

```jsx
function useMyName() {
  const [name, setName] = useState('');
  return [name, setName];
}
```

This is not very useful, but it shows the idea. It is a function that starts with `use` and uses `useState` inside.

### Why the "use" Prefix?

React has one important rule: **hooks must start with "use."**

This is not just a suggestion. React uses this naming convention to check that you follow the rules of hooks (like not calling hooks inside loops or conditions). If your function starts with "use", React knows it is a hook and will check it.

Good names:
- `useToggle`
- `useFetch`
- `useLocalStorage`
- `useWindowSize`

Bad names (React will not treat these as hooks):
- `toggle`
- `fetchData`
- `getFromStorage`

---

## Example 1: useToggle

Let us start with something simple. Many components need a boolean value that flips between `true` and `false`. Think of: showing/hiding a modal, opening/closing a menu, expanding/collapsing a section.

### The Problem: Repeated Code

Without a custom hook, every component writes the same pattern:

```jsx
function Modal() {
  const [isOpen, setIsOpen] = useState(false);
  const toggle = () => setIsOpen(!isOpen);
  // ...
}

function Menu() {
  const [isOpen, setIsOpen] = useState(false);
  const toggle = () => setIsOpen(!isOpen);
  // ...
}

function Accordion() {
  const [isExpanded, setIsExpanded] = useState(false);
  const toggle = () => setIsExpanded(!isExpanded);
  // ...
}
```

The same two lines are repeated three times. Let us fix that.

### The Solution: useToggle

```jsx
// useToggle.js
import { useState } from 'react';

function useToggle(initialValue = false) {
  const [value, setValue] = useState(initialValue);

  function toggle() {
    setValue(!value);
  }

  return [value, toggle];
}

export default useToggle;
```

### Line-by-Line Explanation

```jsx
function useToggle(initialValue = false) {
```
Our custom hook is a function. It starts with `use`. It accepts an optional initial value (defaults to `false`).

```jsx
  const [value, setValue] = useState(initialValue);
```
Inside, it uses `useState` just like you would in a component.

```jsx
  function toggle() {
    setValue(!value);
  }
```
It creates a `toggle` function that flips the value.

```jsx
  return [value, toggle];
```
It returns the current value and the toggle function as an array. This follows the same pattern as `useState` returning `[value, setter]`.

### Using useToggle

Now any component can use it:

```jsx
import useToggle from './useToggle';

function Navbar() {
  const [menuOpen, toggleMenu] = useToggle(false);

  return (
    <nav>
      <button onClick={toggleMenu}>
        {menuOpen ? 'Close Menu' : 'Open Menu'}
      </button>
      {menuOpen && (
        <ul>
          <li>Home</li>
          <li>About</li>
          <li>Contact</li>
        </ul>
      )}
    </nav>
  );
}
```

```jsx
import useToggle from './useToggle';

function FAQ() {
  const [showAnswer, toggleAnswer] = useToggle(false);

  return (
    <div>
      <h3 onClick={toggleAnswer}>What is React?</h3>
      {showAnswer && <p>React is a JavaScript library for building UIs.</p>}
    </div>
  );
}
```

**Expected output (Navbar, menu closed):**

```
[Open Menu]
```

**Expected output (Navbar, after clicking):**

```
[Close Menu]
- Home
- About
- Contact
```

Both components use the same toggle logic, but each has its own independent state. We will talk more about this important point later in the chapter.

---

## Example 2: useLocalStorage

**Local storage** is a feature built into every web browser. It lets you save small amounts of data that persist even when the user closes the browser and comes back later. Think of it like a tiny notebook the browser keeps.

Many components need to save their state to local storage. Let us build a hook for that.

### The Hook

```jsx
// useLocalStorage.js
import { useState, useEffect } from 'react';

function useLocalStorage(key, initialValue) {
  // Step 1: Get the saved value, or use the initial value
  const [value, setValue] = useState(() => {
    const saved = localStorage.getItem(key);
    if (saved !== null) {
      return JSON.parse(saved);
    }
    return initialValue;
  });

  // Step 2: Save to local storage whenever the value changes
  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue];
}

export default useLocalStorage;
```

### Line-by-Line Explanation

```jsx
function useLocalStorage(key, initialValue) {
```
The hook takes two arguments: a `key` (the name to save under, like `'theme'` or `'username'`) and an `initialValue` (what to use if nothing is saved yet).

```jsx
  const [value, setValue] = useState(() => {
    const saved = localStorage.getItem(key);
    if (saved !== null) {
      return JSON.parse(saved);
    }
    return initialValue;
  });
```
We use the function form of `useState` (lazy initialization). This runs only once when the component first renders. It checks local storage for a saved value. If one exists, it parses it from a string back into JavaScript data. If not, it uses the initial value.

`JSON.parse` converts a string like `'"dark"'` back to a JavaScript value like `'dark'`. `JSON.stringify` does the opposite — it converts JavaScript values to strings for storage.

```jsx
  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);
```
Whenever the value changes, this effect saves it to local storage. `JSON.stringify` converts the value to a string (local storage only stores strings).

```jsx
  return [value, setValue];
```
It returns the same thing as `useState`: the current value and a function to update it. The component using this hook does not even know that local storage is involved.

### Using useLocalStorage

```jsx
import useLocalStorage from './useLocalStorage';

function Settings() {
  const [theme, setTheme] = useLocalStorage('theme', 'light');
  const [fontSize, setFontSize] = useLocalStorage('fontSize', 16);

  return (
    <div>
      <h2>Settings</h2>

      <label>
        Theme:
        <select
          value={theme}
          onChange={(e) => setTheme(e.target.value)}
        >
          <option value="light">Light</option>
          <option value="dark">Dark</option>
        </select>
      </label>

      <label>
        Font Size:
        <input
          type="number"
          value={fontSize}
          onChange={(e) => setFontSize(Number(e.target.value))}
        />
      </label>

      <p>Current theme: {theme}</p>
      <p>Current font size: {fontSize}px</p>
    </div>
  );
}

export default Settings;
```

**Expected output:**

```
Settings

Theme:     [Light  v]
Font Size: [16]

Current theme: light
Current font size: 16px
```

The magic: if the user picks "dark" and closes the browser, when they come back, the theme will still be "dark". The `useLocalStorage` hook handles all the saving and loading automatically.

---

## Example 3: useFetch

Fetching data from an API is one of the most common things you do in React. And the pattern is always the same:

1. Set up loading, error, and data states
2. Fetch the data in `useEffect`
3. Handle loading and error states
4. Display the data

Let us wrap this pattern in a reusable hook.

### The Hook

```jsx
// useFetch.js
import { useState, useEffect } from 'react';

function useFetch(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    fetch(url)
      .then(response => {
        if (!response.ok) {
          throw new Error('Something went wrong');
        }
        return response.json();
      })
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(error => {
        setError(error.message);
        setLoading(false);
      });
  }, [url]);

  return { data, loading, error };
}

export default useFetch;
```

### Line-by-Line Explanation

```jsx
function useFetch(url) {
```
The hook takes a URL as its argument. This is the API endpoint (web address) to fetch data from.

```jsx
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
```
Three pieces of state: the fetched `data`, a `loading` flag, and any `error` message. Loading starts as `true` because we start fetching right away.

```jsx
  useEffect(() => {
    setLoading(true);
    setError(null);
```
When the URL changes, we start a new fetch. We set loading to `true` and clear any previous error.

```jsx
    fetch(url)
      .then(response => {
        if (!response.ok) {
          throw new Error('Something went wrong');
        }
        return response.json();
      })
```
We call `fetch` with the URL. If the response is not OK (for example, a 404 error), we throw an error. Otherwise, we convert the response to JSON data.

```jsx
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(error => {
        setError(error.message);
        setLoading(false);
      });
```
If the fetch succeeds, we save the data and stop loading. If it fails, we save the error message and stop loading.

```jsx
  return { data, loading, error };
```
We return an object with all three values. The component can use whichever ones it needs.

### Using useFetch

```jsx
import useFetch from './useFetch';

function UserList() {
  const { data, loading, error } = useFetch(
    'https://jsonplaceholder.typicode.com/users'
  );

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <ul>
      {data.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

```jsx
import useFetch from './useFetch';

function PostList() {
  const { data, loading, error } = useFetch(
    'https://jsonplaceholder.typicode.com/posts'
  );

  if (loading) return <p>Loading posts...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <ul>
      {data.slice(0, 5).map(post => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  );
}
```

**Expected output (UserList, while loading):**

```
Loading...
```

**Expected output (UserList, after loading):**

```
- Leanne Graham
- Ervin Howell
- Clementine Bauch
- ...
```

Both `UserList` and `PostList` fetch data from different URLs, but they use the exact same hook. No duplicated loading/error logic. If you want to improve error handling, you change it in one place.

---

## When to Extract a Custom Hook

Here is a simple guideline:

> If you copy and paste the same `useState` + `useEffect` (or similar hook combination) pattern into more than one component, it is time to make a custom hook.

Signs that you should create a custom hook:

1. **Two or more components have the same hook pattern.** They use `useState` and `useEffect` in the same way.
2. **A component has complex hook logic that distracts from its main purpose.** Moving the logic to a hook makes the component easier to read.
3. **You want to test the logic separately.** Custom hooks can be tested independently from any component.

Signs that you should NOT create a custom hook:

1. **The logic is only used in one component.** Wait until you need it in a second place.
2. **The "hook" would just wrap a single `useState`.** That does not add value.
3. **You are doing it just to reduce lines of code.** Hooks should improve clarity, not just reduce line count.

---

## Custom Hooks Share Logic, Not State

This is a very important concept that trips up many beginners.

When two components use the same custom hook, they share the **logic** (the code). They do NOT share the **state** (the data). Each component gets its own independent copy of the state.

Let us see this clearly:

```jsx
function ComponentA() {
  const [isOn, toggle] = useToggle(false);
  return <button onClick={toggle}>{isOn ? 'ON' : 'OFF'}</button>;
}

function ComponentB() {
  const [isOn, toggle] = useToggle(false);
  return <button onClick={toggle}>{isOn ? 'ON' : 'OFF'}</button>;
}
```

If you click the button in `ComponentA`, only `ComponentA` changes. `ComponentB` is not affected. They each have their own `isOn` state.

Think of it like a cookie recipe. If you and your friend both use the same recipe, you each bake your own batch of cookies. Eating one of your cookies does not affect your friend's cookies.

```
  Custom Hook: useToggle

  ComponentA                    ComponentB
  +--------------+              +--------------+
  | isOn = false |              | isOn = false |
  | toggle()     |              | toggle()     |
  +--------------+              +--------------+
       |                             |
       | (click toggle)              |
       v                             |
  +--------------+              +--------------+
  | isOn = true  |              | isOn = false |  (unchanged!)
  | toggle()     |              | toggle()     |
  +--------------+              +--------------+

  Same logic. Different state.
```

If you want components to share the same state, you need Context (which you learned in the previous chapter).

---

## Quick Summary

A **custom hook** is a function that starts with `use` and uses other hooks inside. It lets you package reusable logic into a single function that any component can call.

Custom hooks share **logic**, not **state**. Each component that calls a hook gets its own independent copy of the state.

Create a custom hook when you see the same hook pattern repeated in multiple components.

---

## Key Points to Remember

1. **Custom hooks must start with "use".** This is a rule, not a suggestion. React uses this to enforce hook rules.

2. **A custom hook is just a function.** There is nothing special about it. It is a regular function that happens to use hooks inside.

3. **Custom hooks can use any other hooks.** You can use `useState`, `useEffect`, `useContext`, `useReducer`, or even other custom hooks inside your custom hook.

4. **Each call to a custom hook creates independent state.** Two components using the same hook do not share state.

5. **Custom hooks can return anything.** Return an array (`[value, setter]`), an object (`{ data, loading, error }`), or even a single value. Choose whatever makes sense for your hook.

6. **Extract a hook when you see a pattern repeated.** If you copy-paste the same hooks logic into a second component, it is time to create a custom hook.

7. **Name your hooks clearly.** The name should describe what the hook does: `useToggle`, `useLocalStorage`, `useFetch`, `useWindowSize`.

---

## Practice Questions

1. What two things make a function a "custom hook"?

2. If two components both use `useToggle`, do they share the same state? Why or why not?

3. What is wrong with this custom hook name?

```jsx
function getWindowSize() {
  const [width, setWidth] = useState(window.innerWidth);
  // ...
  return width;
}
```

4. When should you create a custom hook? When should you NOT?

5. What does `useLocalStorage` do differently from `useState`?

---

## Exercises

### Exercise 1: useCounter

Create a custom hook called `useCounter` that manages a counter. It should accept an `initialValue` (default `0`) and return:
- `count` — the current count
- `increment` — a function to add 1
- `decrement` — a function to subtract 1
- `reset` — a function to reset to the initial value

Then use it in two separate components to verify that they have independent state.

### Exercise 2: useDocumentTitle

Create a custom hook called `useDocumentTitle` that updates the browser tab title. It should accept a string and set `document.title` to that string using `useEffect`.

Use it in a component where the user can type in an input, and the browser tab title updates as they type.

### Exercise 3: useOnlineStatus

Create a custom hook called `useOnlineStatus` that tracks whether the user is online or offline. Use `window.addEventListener` to listen for `'online'` and `'offline'` events. Return a boolean: `true` if online, `false` if offline.

Hint: Use `navigator.onLine` for the initial value, and `useEffect` to add and remove event listeners.

---

## What Is Next?

You now know how to create your own reusable hooks. This is a skill that separates beginners from intermediate React developers. As you build more projects, you will create hooks that are specific to your application, like `useAuth`, `useCart`, or `useTheme`.

In the next and final chapter, you will learn about **TypeScript** — a tool that adds type safety to your React code. TypeScript helps you catch bugs before you even run your code, like a spell-checker for your programming. It is used by most professional React projects today, and knowing the basics will make you a stronger developer.
