# Chapter 21: Common Mistakes Beginners Make

Every programmer makes mistakes. Even experienced developers make mistakes every day. The difference is that experienced developers know how to recognize mistakes quickly and fix them.

In this chapter, we will look at the most common mistakes that beginners make when learning React. For each mistake, you will see what the mistake looks like, why it happens, what error message you might see, and how to fix it.

Think of this chapter like a troubleshooting guide. When something goes wrong in your code, come back here. There is a good chance the answer is in this chapter.

---

## What You Will Learn

- 15 common mistakes that React beginners make
- Why each mistake happens
- What error messages to look for
- How to fix each mistake quickly

## Why This Chapter Matters

When you are learning, mistakes can be frustrating. You might spend hours trying to figure out why your code is not working. This chapter will save you time. It will help you recognize problems quickly. It will also help you understand React better. Every mistake teaches you something about how React works.

---

## Mistake 1: Forgetting to Return JSX

### What the Mistake Looks Like

```jsx
function Greeting() {
  const name = "Alice";
  // Oops! No return statement
  <h1>Hello, {name}!</h1>
}
```

### Why It Happens

In JavaScript, a function does not give anything back unless you use the `return` keyword. The word "return" means "give this back to whoever asked." Without it, your component gives back `undefined`. That means "nothing." React does not know what to show on the screen.

### What You See

Your component shows nothing on the screen. No error message appears. This makes it hard to find the problem.

### The Fix

Always use the `return` keyword before your JSX.

```jsx
function Greeting() {
  const name = "Alice";
  return <h1>Hello, {name}!</h1>;
}
```

### Another Version of This Mistake

Sometimes this happens with curly braces `{}` instead of parentheses `()` after an arrow function.

```jsx
// WRONG - curly braces create a function body, so you need return
const Greeting = () => {
  <h1>Hello!</h1>
};

// RIGHT - option 1: add return
const Greeting = () => {
  return <h1>Hello!</h1>;
};

// RIGHT - option 2: use parentheses for implicit return
const Greeting = () => (
  <h1>Hello!</h1>
);
```

The word "implicit" means "without saying it directly." When you use parentheses with an arrow function, JavaScript automatically returns what is inside them. When you use curly braces, you must write `return` yourself.

---

## Mistake 2: Using `class` Instead of `className`

### What the Mistake Looks Like

```jsx
function Button() {
  return <button class="primary-btn">Click Me</button>;
}
```

### Why It Happens

In regular HTML, you use `class` to add CSS styles to an element. But in React, you write JSX, not HTML. JSX is JavaScript. In JavaScript, `class` is a reserved word. A "reserved word" is a word that JavaScript already uses for something else. So React uses `className` instead.

### What You See

React shows a warning in the browser console:

```
Warning: Invalid DOM property `class`. Did you mean `className`?
```

### The Fix

Use `className` instead of `class`.

```jsx
function Button() {
  return <button className="primary-btn">Click Me</button>;
}
```

### Quick Tip

This is easy to forget. If your CSS styles are not working, check if you used `class` instead of `className`.

---

## Mistake 3: Not Wrapping Multiple Elements in a Parent

### What the Mistake Looks Like

```jsx
function UserInfo() {
  return (
    <h1>Alice</h1>
    <p>Age: 25</p>
  );
}
```

### Why It Happens

A React component can only return one element. Think of it like a gift box. You can put many things inside one box, but you can only hand someone one box at a time. If you try to return two elements side by side, React does not know how to handle it.

### What You See

You see an error message like this:

```
SyntaxError: Adjacent JSX elements must be wrapped in an enclosing tag.
```

The word "adjacent" means "next to each other." The word "enclosing" means "surrounding."

### The Fix

Wrap your elements in a parent element. You have three options.

**Option 1: Use a `<div>`**

```jsx
function UserInfo() {
  return (
    <div>
      <h1>Alice</h1>
      <p>Age: 25</p>
    </div>
  );
}
```

**Option 2: Use a Fragment `<> </>`**

A Fragment is an invisible wrapper. It groups elements together without adding an extra HTML element to your page.

```jsx
function UserInfo() {
  return (
    <>
      <h1>Alice</h1>
      <p>Age: 25</p>
    </>
  );
}
```

**Option 3: Use `<React.Fragment>`**

This does the same thing as `<>`, but you can add a `key` prop to it. We will explain keys later in this chapter.

```jsx
function UserInfo() {
  return (
    <React.Fragment>
      <h1>Alice</h1>
      <p>Age: 25</p>
    </React.Fragment>
  );
}
```

---

## Mistake 4: Mutating State Directly

### What the Mistake Looks Like

```jsx
function ShoppingList() {
  const [items, setItems] = useState(["Milk", "Bread"]);

  function addItem() {
    items.push("Eggs"); // WRONG! This changes the array directly
    setItems(items);
  }

  return (
    <div>
      <button onClick={addItem}>Add Eggs</button>
      <ul>
        {items.map((item, index) => (
          <li key={index}>{item}</li>
        ))}
      </ul>
    </div>
  );
}
```

### Why It Happens

The word "mutate" means "to change something directly." When you use `push()`, you are changing the original array. React does not notice this change. React only re-renders (shows updates on the screen) when it sees a completely new value. Since you pushed to the same array and then passed the same array to `setItems`, React thinks nothing changed.

Think of it like this. Imagine you have a whiteboard with a grocery list. If you erase an item and write a new one on the same whiteboard, someone looking from far away might not notice the change. But if you throw away the old whiteboard and hold up a brand new one, everyone will notice.

### What You See

The screen does not update. No error message appears. The button seems to do nothing.

### The Fix

Create a new array with the spread operator `...` and add the new item to it.

```jsx
function ShoppingList() {
  const [items, setItems] = useState(["Milk", "Bread"]);

  function addItem() {
    setItems([...items, "Eggs"]); // RIGHT! Creates a new array
  }

  return (
    <div>
      <button onClick={addItem}>Add Eggs</button>
      <ul>
        {items.map((item, index) => (
          <li key={index}>{item}</li>
        ))}
      </ul>
    </div>
  );
}
```

The `...items` part means "copy everything from the old array." Then `"Eggs"` is added at the end. This creates a brand new array. React sees the new array and updates the screen.

### The Same Rule Applies to Objects

```jsx
// WRONG
const [user, setUser] = useState({ name: "Alice", age: 25 });
user.age = 26; // Mutating directly
setUser(user);

// RIGHT
setUser({ ...user, age: 26 }); // Create a new object
```

---

## Mistake 5: Infinite Loops in useEffect

### What the Mistake Looks Like

```jsx
function Counter() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    setCount(count + 1); // This runs, updates state, which triggers useEffect again...
  }); // No dependency array!

  return <p>Count: {count}</p>;
}
```

### Why It Happens

`useEffect` runs after your component renders. When there is no dependency array (the square brackets `[]` at the end), `useEffect` runs after every single render. Inside the effect, `setCount` updates the state. Updating state causes the component to render again. After the render, `useEffect` runs again. This creates an endless loop.

Think of it like a dog chasing its own tail. The effect updates the state. The state update causes a re-render. The re-render triggers the effect. The effect updates the state again. It never stops.

### What You See

Your browser becomes very slow or freezes. You might see this error in the console:

```
Error: Too many re-renders. React limits the number of renders to prevent an infinite loop.
```

### The Fix

Add a dependency array to control when `useEffect` runs.

```jsx
// Run only once, when the component first appears
useEffect(() => {
  setCount(count + 1);
}, []); // Empty array = run once

// Run only when "count" changes
useEffect(() => {
  document.title = `Count: ${count}`;
}, [count]); // Runs when count changes
```

The dependency array tells React: "Only run this effect when these values change." An empty array `[]` means "run this effect only once, when the component first appears on the screen."

---

## Mistake 6: Forgetting Keys in Lists

### What the Mistake Looks Like

```jsx
function FruitList() {
  const fruits = ["Apple", "Banana", "Cherry"];

  return (
    <ul>
      {fruits.map((fruit) => (
        <li>{fruit}</li>
      ))}
    </ul>
  );
}
```

### Why It Happens

When you create a list in React, each item needs a unique `key`. A "key" is like a name tag. It helps React keep track of each item. Without keys, React cannot tell which items changed, which were added, or which were removed.

Think of a classroom. If students do not have name tags, the teacher cannot tell who is who. If a new student joins, the teacher does not know where to seat them.

### What You See

React shows a warning in the console:

```
Warning: Each child in a list should have a unique "key" prop.
```

### The Fix

Add a `key` prop to each item in the list. Use a unique value, like an `id` from your data.

```jsx
function FruitList() {
  const fruits = ["Apple", "Banana", "Cherry"];

  return (
    <ul>
      {fruits.map((fruit) => (
        <li key={fruit}>{fruit}</li>
      ))}
    </ul>
  );
}
```

### Important: Do Not Use Array Index as Key (When Possible)

Using the index (position number) as a key can cause problems if the list order changes.

```jsx
// Not ideal - using index as key
{fruits.map((fruit, index) => (
  <li key={index}>{fruit}</li>
))}

// Better - using a unique value
{users.map((user) => (
  <li key={user.id}>{user.name}</li>
))}
```

Use the array index only as a last resort, when your items do not have a unique identifier and the list never changes order.

---

## Mistake 7: Calling Hooks Inside if Statements or Loops

### What the Mistake Looks Like

```jsx
function Profile({ isLoggedIn }) {
  if (isLoggedIn) {
    const [name, setName] = useState("Alice"); // WRONG!
  }

  return <p>Welcome!</p>;
}
```

Or inside a loop:

```jsx
function UserList({ users }) {
  for (let user of users) {
    const [selected, setSelected] = useState(false); // WRONG!
  }

  return <p>Users</p>;
}
```

### Why It Happens

React needs hooks to run in the same order every time your component renders. If a hook is inside an `if` statement, it might run sometimes and not run other times. This confuses React. React keeps track of hooks by their position (first hook, second hook, third hook...). If the order changes, React gets mixed up.

Think of it like a row of numbered lockers. React puts each hook's value in a specific locker. Hook 1 goes in locker 1. Hook 2 goes in locker 2. If you skip a hook sometimes, the values end up in the wrong lockers.

### What You See

```
Error: React Hook "useState" is called conditionally. React Hooks must be
called in the exact same order in every component render.
```

### The Fix

Always call hooks at the top level of your component. Put the `if` statement inside the hook, not around it.

```jsx
function Profile({ isLoggedIn }) {
  const [name, setName] = useState("Alice"); // Always call the hook

  if (!isLoggedIn) {
    return <p>Please log in.</p>; // Conditional rendering is fine
  }

  return <p>Welcome, {name}!</p>;
}
```

### The Rules of Hooks

1. Only call hooks at the top of your component function.
2. Do not put hooks inside `if` statements.
3. Do not put hooks inside loops.
4. Do not put hooks inside nested functions.

---

## Mistake 8: Calling a Function Instead of Passing a Reference

### What the Mistake Looks Like

```jsx
function App() {
  function handleClick() {
    alert("Button clicked!");
  }

  return <button onClick={handleClick()}>Click Me</button>;
}
```

### Why It Happens

There is a big difference between `handleClick` and `handleClick()`.

- `handleClick` is a reference to the function. It means "here is the function, call it later when the button is clicked."
- `handleClick()` calls the function immediately. The parentheses `()` mean "run this right now."

Think of it like giving someone a phone number versus calling the phone number. `handleClick` is like writing down the number. `handleClick()` is like dialing the number right away.

### What You See

The function runs immediately when the page loads, not when you click the button. If the function updates state, you might get an infinite loop.

### The Fix

Remove the parentheses. Pass the function reference.

```jsx
// WRONG - calls the function immediately
<button onClick={handleClick()}>Click Me</button>

// RIGHT - passes a reference to the function
<button onClick={handleClick}>Click Me</button>
```

### What If You Need to Pass an Argument?

If you need to pass a value to the function, wrap it in an arrow function.

```jsx
// WRONG
<button onClick={deleteItem(5)}>Delete</button>

// RIGHT
<button onClick={() => deleteItem(5)}>Delete</button>
```

The arrow function `() => deleteItem(5)` creates a new function that says "when the button is clicked, call `deleteItem` with the number 5."

---

## Mistake 9: Not Handling Loading and Error States for API Calls

### What the Mistake Looks Like

```jsx
function UserProfile() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetch("https://api.example.com/user/1")
      .then((response) => response.json())
      .then((data) => setUser(data));
  }, []);

  return (
    <div>
      <h1>{user.name}</h1>  {/* CRASH! user is null at first */}
      <p>{user.email}</p>
    </div>
  );
}
```

### Why It Happens

When your component first appears, `user` is `null` because the data has not arrived yet. The API call takes time. But your component tries to show `user.name` right away. You cannot read `.name` from `null`. This causes a crash.

Think of it like opening the oven before the food is cooked. You need to wait for the food to be ready.

### What You See

```
TypeError: Cannot read properties of null (reading 'name')
```

### The Fix

Add loading and error states. Check if the data is ready before showing it.

```jsx
function UserProfile() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("https://api.example.com/user/1")
      .then((response) => response.json())
      .then((data) => {
        setUser(data);
        setLoading(false);
      })
      .catch((err) => {
        setError("Something went wrong.");
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  );
}
```

### Line-by-Line Explanation

- `useState(true)` for loading: The data is loading at first, so we start with `true`.
- `useState(null)` for error: There is no error at first, so we start with `null`.
- `setLoading(false)`: When data arrives (or an error happens), we are no longer loading.
- `if (loading)`: Show a loading message while we wait.
- `if (error)`: Show the error message if something went wrong.
- Only after both checks pass do we show the actual data.

---

## Mistake 10: Typos in State Variable Names

### What the Mistake Looks Like

```jsx
function Counter() {
  const [count, setCount] = useState(0);

  function increment() {
    setCont(count + 1); // Typo! "setCont" instead of "setCount"
  }

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={increment}>Add 1</button>
    </div>
  );
}
```

### Why It Happens

It is easy to make spelling mistakes, especially with longer variable names. JavaScript does not warn you about undefined variables until you try to use them.

### What You See

```
ReferenceError: setCont is not defined
```

Or sometimes your code just does nothing, and you spend a long time trying to figure out why.

### The Fix

Double-check your variable names. Make sure the setter function name matches what you declared.

```jsx
const [count, setCount] = useState(0);
//             ^^^^^^^^
// Make sure you use this exact name everywhere

function increment() {
  setCount(count + 1); // Correct spelling
}
```

### Tip

Many code editors highlight undefined variables. If you see a variable name with a red or yellow underline, check the spelling.

---

## Mistake 11: Importing Components with Lowercase Names

### What the Mistake Looks Like

```jsx
// In the file header.js
function header() {  // lowercase "h"
  return <h1>Welcome to My App</h1>;
}

export default header;

// In App.js
import header from "./header";

function App() {
  return <header />;  // React thinks this is an HTML <header> tag!
}
```

### Why It Happens

React uses a simple rule to tell the difference between HTML tags and your custom components. If the name starts with a lowercase letter, React treats it as an HTML element. If it starts with an uppercase letter, React treats it as a component.

The name `header` starts with a lowercase "h", so React thinks you want the HTML `<header>` tag, not your custom component.

### What You See

Your component does not show the expected content. Instead, React renders an HTML `<header>` element.

### The Fix

Always start component names with an uppercase letter.

```jsx
// In Header.js
function Header() {  // Uppercase "H"
  return <h1>Welcome to My App</h1>;
}

export default Header;

// In App.js
import Header from "./Header";

function App() {
  return <Header />;  // Now React knows this is a component
}
```

---

## Mistake 12: Not Installing Packages Before Importing Them

### What the Mistake Looks Like

```jsx
import axios from "axios"; // You never installed axios!

function App() {
  // ...
}
```

### Why It Happens

When you follow a tutorial, you might copy the import statement but forget to install the package first. A "package" is a piece of code that someone else wrote and shared. You need to download it to your computer before you can use it.

### What You See

```
Module not found: Error: Can't resolve 'axios'
```

Or:

```
Module not found: Can't resolve 'react-router-dom'
```

### The Fix

Install the package using npm (Node Package Manager) in your terminal before importing it.

```bash
npm install axios
```

Then you can import it in your code:

```jsx
import axios from "axios";
```

### How to Know If You Need to Install Something

If your import path does NOT start with `./` or `../`, it is probably an external package that needs to be installed.

```jsx
import Header from "./Header";     // Local file - no install needed
import axios from "axios";          // External package - must install
import { BrowserRouter } from "react-router-dom"; // External - must install
```

---

## Mistake 13: Forgetting to Export Components

### What the Mistake Looks Like

```jsx
// In Greeting.js
function Greeting() {
  return <h1>Hello!</h1>;
}

// Oops! Forgot to export
```

```jsx
// In App.js
import Greeting from "./Greeting"; // This will not work!
```

### Why It Happens

In JavaScript, each file is like a private room. Nothing can get in or out unless you open the door. The `export` keyword opens the door so other files can use your component.

### What You See

```
Attempted import error: './Greeting' does not contain a default export.
```

Or your component shows as `undefined` or does not appear at all.

### The Fix

Add `export default` to your component.

```jsx
// Option 1: Export at the bottom
function Greeting() {
  return <h1>Hello!</h1>;
}

export default Greeting;

// Option 2: Export on the same line
export default function Greeting() {
  return <h1>Hello!</h1>;
}
```

---

## Mistake 14: Using `=` Instead of `===` in Conditions

### What the Mistake Looks Like

```jsx
function StatusMessage({ status }) {
  if (status = "active") {  // WRONG! Single = is assignment, not comparison
    return <p>User is active</p>;
  }
  return <p>User is not active</p>;
}
```

### Why It Happens

In JavaScript, `=` and `===` do very different things:

- `=` means "assign this value" (put a value into a variable)
- `===` means "is this equal to?" (compare two values)

Using `=` in an `if` statement assigns the value instead of comparing it. This means the condition is always true (because the assignment is successful), so your code always takes the first path.

Think of it like this. `=` is like writing on a name tag. `===` is like reading a name tag and checking if it matches.

### What You See

No error message. But your code always behaves as if the condition is true, even when it should be false.

### The Fix

Use `===` for comparisons.

```jsx
function StatusMessage({ status }) {
  if (status === "active") {  // RIGHT! Triple = compares values
    return <p>User is active</p>;
  }
  return <p>User is not active</p>;
}
```

### Quick Reference

| Symbol | Meaning | Example |
|--------|---------|---------|
| `=` | Assign a value | `let x = 5` |
| `==` | Loose comparison (not recommended) | `5 == "5"` is `true` |
| `===` | Strict comparison (recommended) | `5 === "5"` is `false` |

Always use `===` in React. It is safer and more predictable.

---

## Mistake 15: Not Using the Key Prop Correctly

### What the Mistake Looks Like

```jsx
// Using the same key for different items
function TaskList({ tasks }) {
  return (
    <ul>
      {tasks.map((task) => (
        <li key="task">{task.name}</li>  // Same key for every item!
      ))}
    </ul>
  );
}
```

Or using an index when items can be reordered:

```jsx
function TaskList({ tasks }) {
  return (
    <ul>
      {tasks.map((task, index) => (
        <li key={index}>
          <input type="checkbox" />
          {task.name}
        </li>
      ))}
    </ul>
  );
}
```

### Why It Happens

Beginners sometimes set every key to the same value, or always use the array index. Keys must be unique among siblings. If two items have the same key, React cannot tell them apart.

Using the index as a key seems harmless, but it causes problems when items are added, removed, or reordered. React uses keys to match old elements with new elements. If the order changes, the indexes change, and React gets confused about which item is which.

### What You See

With duplicate keys, you might see unexpected behavior. Items might not update correctly. Checkboxes might check the wrong items. Input fields might show the wrong values.

### The Fix

Use a unique identifier from your data as the key.

```jsx
function TaskList({ tasks }) {
  return (
    <ul>
      {tasks.map((task) => (
        <li key={task.id}>
          <input type="checkbox" />
          {task.name}
        </li>
      ))}
    </ul>
  );
}
```

### What Makes a Good Key?

- It should be **unique** among siblings (no two items in the same list should have the same key).
- It should be **stable** (the same item should always have the same key, even if the list is reordered).
- It should come from your **data** (like an `id` field).

---

## Quick Summary

Here is a quick reference table of all 15 mistakes:

| # | Mistake | Fix |
|---|---------|-----|
| 1 | Forgetting to return JSX | Add `return` before your JSX |
| 2 | Using `class` instead of `className` | Use `className` in JSX |
| 3 | Not wrapping elements in a parent | Use `<div>` or `<> </>` |
| 4 | Mutating state directly | Use spread `...` to create new arrays/objects |
| 5 | Infinite loops in useEffect | Add a dependency array `[]` |
| 6 | Forgetting keys in lists | Add unique `key` prop to list items |
| 7 | Hooks inside if/loops | Call hooks at the top level only |
| 8 | Calling function instead of passing reference | Use `onClick={fn}` not `onClick={fn()}` |
| 9 | Not handling loading/error states | Add loading and error state variables |
| 10 | Typos in state variable names | Double-check spelling |
| 11 | Lowercase component names | Start component names with uppercase |
| 12 | Not installing packages | Run `npm install` first |
| 13 | Forgetting to export | Add `export default` |
| 14 | Using `=` instead of `===` | Use `===` for comparisons |
| 15 | Wrong key prop usage | Use unique, stable identifiers |

---

## Key Points to Remember

1. **Always return JSX** from your components. No return means nothing on the screen.
2. **Use `className`** instead of `class` in JSX.
3. **Wrap multiple elements** in a parent element or Fragment.
4. **Never mutate state directly.** Always create new arrays and objects.
5. **Always add a dependency array** to `useEffect` to avoid infinite loops.
6. **Give each list item a unique key** from your data.
7. **Call hooks at the top level** of your component, never inside conditions or loops.
8. **Pass function references** to event handlers. Do not call the function.
9. **Handle loading and error states** when fetching data.
10. **Read your error messages carefully.** They often tell you exactly what is wrong.

---

## Practice Questions

1. What happens when you forget to add `return` before your JSX?

2. Why does React use `className` instead of `class`?

3. What is the difference between `onClick={handleClick}` and `onClick={handleClick()}`?

4. Why do you need to create a new array (with the spread operator) instead of using `push()` to update state?

5. What does the dependency array in `useEffect` do?

---

## Exercises

### Exercise 1: Find the Bugs

Look at this code. There are 4 mistakes. Can you find and fix all of them?

```jsx
function todoList() {
  const [todos, setTodos] = useState(["Buy milk", "Walk dog"]);

  function addTodo() {
    todos.push("Read book");
    setTodos(todos);
  }

  return (
    <h1>My Todos</h1>
    <button onClick={addTodo()}>Add Todo</button>
    <ul>
      {todos.map((todo) => (
        <li class="todo-item">{todo}</li>
      ))}
    </ul>
  );
}
```

**Hints:** Look for issues with the component name, state mutation, the onClick handler, JSX wrapping, className, and missing keys.

### Exercise 2: Fix the useEffect

This code causes an infinite loop. Fix it so it only runs once.

```jsx
function WelcomeMessage() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    setMessage("Welcome to our app!");
  });

  return <h1>{message}</h1>;
}
```

### Exercise 3: Handle Loading State

This code crashes when the page first loads. Add loading and error handling.

```jsx
function ProductList() {
  const [products, setProducts] = useState(null);

  useEffect(() => {
    fetch("https://api.example.com/products")
      .then((res) => res.json())
      .then((data) => setProducts(data));
  }, []);

  return (
    <ul>
      {products.map((product) => (
        <li key={product.id}>{product.name}</li>
      ))}
    </ul>
  );
}
```

---

## What Is Next?

Now that you know the most common mistakes and how to fix them, let us look at the positive side. In the next chapter, we will learn best practices for writing clean, organized React code. These are the habits that will make your code easier to read, easier to maintain, and more professional. Think of this chapter as learning what NOT to do. The next chapter is about learning what TO do.
