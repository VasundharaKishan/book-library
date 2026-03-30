# Chapter 23: Interview-Style Beginner Questions

Whether you are preparing for a job interview or just want to check your own understanding, this chapter will help. We have collected 30 common questions that interviewers ask about React. Each question has a clear, simple answer.

Do not worry about memorizing these word for word. The goal is to understand the ideas behind each answer. If you understand the "why," you can explain it in your own words. That is what interviewers want to see.

---

## What You Will Learn

- Answers to 30 common React interview questions
- How to explain React concepts in simple language
- The core ideas that every React developer should know

## Why This Chapter Matters

Interview questions test whether you truly understand something, or whether you only memorized code. Going through these questions is a great way to find gaps in your knowledge. If you cannot answer a question, that is a sign that you need to review that topic. Think of this chapter as a self-test.

---

## The Questions

### Question 1: What is React?

**Answer:** React is a JavaScript library for building user interfaces. A "user interface" is what people see and interact with on a website or app -- buttons, text, forms, images, and so on. React was created by Facebook (now called Meta) and is free to use. It helps you build web pages by breaking them into small, reusable pieces called "components."

---

### Question 2: What is JSX?

**Answer:** JSX stands for JavaScript XML. It is a special way of writing code that looks like HTML but lives inside JavaScript. JSX lets you describe what your page should look like. For example, `<h1>Hello</h1>` looks like HTML, but it is actually JSX. The browser cannot understand JSX directly. A tool called a "compiler" (like Babel) converts JSX into regular JavaScript that the browser can run.

---

### Question 3: What are components?

**Answer:** Components are the building blocks of a React app. A component is a piece of your user interface that you can reuse. Think of components like LEGO bricks. Each brick is a small piece. You put them together to build something bigger. A `Button` component can be used in many places. A `Header` component appears at the top of every page. Components can be as small as a button or as large as an entire page.

---

### Question 4: What is the difference between props and state?

**Answer:** Props and state are both ways to store data in React, but they work differently.

**Props** (short for "properties") are data passed from a parent component to a child component. They flow in one direction: down. A child cannot change its own props. Think of props like a gift -- you receive it, but you do not get to choose what is inside.

**State** is data that a component manages itself. The component can read it and change it. Think of state like your personal notebook -- you can write in it and erase things whenever you want.

| | Props | State |
|--|-------|-------|
| Who controls it? | Parent component | The component itself |
| Can the component change it? | No | Yes |
| Direction | Parent to child (down) | Internal |

---

### Question 5: What is the Virtual DOM?

**Answer:** The DOM (Document Object Model) is the browser's version of your web page. It is like a tree of all the elements on the page. Changing the real DOM is slow. React solves this by keeping a "virtual" copy of the DOM in memory. When something changes, React first updates the virtual copy. Then it compares the virtual copy with the real DOM and only updates the parts that actually changed. This is faster than replacing everything.

Think of it like editing a document. Instead of reprinting the whole document every time you fix a typo, you just correct the one word that changed.

---

### Question 6: What are hooks?

**Answer:** Hooks are special functions that let you use React features (like state and side effects) inside function components. Before hooks existed, you had to use "class components" to use state. Hooks made React simpler. The two most common hooks are `useState` (for managing state) and `useEffect` (for side effects like fetching data). Hooks always start with the word "use."

---

### Question 7: What does useState do?

**Answer:** `useState` is a hook that lets you add state to a function component. It takes one argument: the initial value. It gives you back two things: the current value and a function to update it.

```jsx
const [count, setCount] = useState(0);
```

Here, `count` starts at 0. When you call `setCount(1)`, React updates `count` to 1 and re-renders the component to show the new value.

---

### Question 8: What does useEffect do?

**Answer:** `useEffect` is a hook that lets you run code after your component renders. It is used for "side effects" -- things that happen outside of just showing content on the screen. Common side effects include fetching data from an API, setting up a timer, or updating the page title. The dependency array (second argument) controls when the effect runs.

```jsx
useEffect(() => {
  document.title = "My App";
}, []); // Empty array = runs once after the first render
```

---

### Question 9: What is conditional rendering?

**Answer:** Conditional rendering means showing different content based on a condition. Just like an `if` statement in regular programming, you can choose what to display depending on the situation.

```jsx
function Greeting({ isLoggedIn }) {
  if (isLoggedIn) {
    return <h1>Welcome back!</h1>;
  }
  return <h1>Please sign in.</h1>;
}
```

You can also use the ternary operator for shorter conditions:

```jsx
return <h1>{isLoggedIn ? "Welcome back!" : "Please sign in."}</h1>;
```

---

### Question 10: Why do we need keys in lists?

**Answer:** Keys help React identify which items in a list have changed, been added, or been removed. Each key should be unique among siblings. Without keys, React has to guess which items changed, and it might make mistakes. This can cause bugs, especially with inputs or checkboxes.

Good keys come from your data (like an `id` field). Avoid using the array index as a key if the list can be reordered.

---

### Question 11: What is lifting state up?

**Answer:** Lifting state up means moving state from a child component to a parent component so that multiple children can share it. If two components need the same data, you put that data in their closest common parent. The parent passes the data down as props.

For example, if a `SearchBar` and a `ResultsList` both need the search query, you put the `query` state in their parent component and pass it down to both children.

---

### Question 12: What is a controlled component?

**Answer:** A controlled component is a form element (like an input or select) whose value is controlled by React state. The input does not manage its own value. Instead, React tells the input what to show, and when the user types, React updates the state.

```jsx
function NameInput() {
  const [name, setName] = useState("");

  return (
    <input
      value={name}
      onChange={(e) => setName(e.target.value)}
    />
  );
}
```

The opposite is an "uncontrolled component," where the input manages its own value and you read it only when needed (using a ref).

---

### Question 13: How do you fetch data in React?

**Answer:** You fetch data inside a `useEffect` hook. The most common way is to use the `fetch` function built into browsers. You call the API, wait for the response, convert it to JSON, and save it in state. You should also handle loading and error states.

```jsx
useEffect(() => {
  fetch("https://api.example.com/data")
    .then((response) => response.json())
    .then((data) => setData(data))
    .catch((error) => setError(error.message));
}, []);
```

---

### Question 14: What is React Router?

**Answer:** React Router is a library that lets you add navigation to your React app. It allows you to have different "pages" without actually reloading the browser. When you click a link, React Router shows a different component, but the page never fully refreshes. This creates a smooth experience, similar to a mobile app.

---

### Question 15: What is the difference between a library and a framework?

**Answer:** A library gives you tools that you choose when to use. You are in control. React is a library. You decide how to structure your app and which parts of React to use.

A framework gives you a structure and tells you where to put your code. The framework is in control. Angular is a framework.

Think of it this way: a library is like a set of tools. You pick the tool you need and use it. A framework is like a blueprint. You build inside its structure.

---

### Question 16: What is a single-page application (SPA)?

**Answer:** A single-page application is a website that loads one HTML page and then updates the content dynamically without full page reloads. When you click a link, instead of loading an entirely new page from the server, JavaScript updates what you see on the screen. React apps are typically SPAs. This makes them feel faster and smoother because there is no "flash" between page changes.

---

### Question 17: What is the difference between a function component and a class component?

**Answer:** Both are ways to create React components. Function components are simpler. They are just JavaScript functions that return JSX. Class components use the `class` keyword and have more complex syntax.

Modern React uses function components almost exclusively. Class components are older and rarely used in new code. Hooks (like `useState` and `useEffect`) made function components just as powerful as class components, but easier to write.

---

### Question 18: What is the children prop?

**Answer:** The `children` prop is a special prop that contains whatever you put between the opening and closing tags of a component. It lets you create "wrapper" components.

```jsx
function Card({ children }) {
  return <div className="card">{children}</div>;
}

// Using it:
<Card>
  <h2>Title</h2>
  <p>Some content here.</p>
</Card>
```

Everything between `<Card>` and `</Card>` becomes the `children` prop. This makes components flexible because you can put anything inside them.

---

### Question 19: What happens when state changes in React?

**Answer:** When state changes, React re-renders the component. "Re-render" means React runs the component function again to see what the new output should look like. React then compares the new output with the old output (using the Virtual DOM) and updates only the parts of the screen that changed. This process is fast because React only touches what is necessary.

---

### Question 20: What is prop drilling?

**Answer:** Prop drilling is when you pass data through many layers of components just to get it to a deeply nested child. For example, if the `App` component has data that a deeply nested `Button` component needs, you might pass it through 5 or 6 components in between, even though those middle components do not use the data themselves.

Prop drilling makes code harder to maintain. Solutions include React Context or state management libraries.

---

### Question 21: What is React Context?

**Answer:** React Context is a way to share data across many components without passing props through every level. You create a "context" and wrap your app (or part of it) with a "Provider." Any component inside that Provider can access the shared data directly, no matter how deep it is.

Common uses include sharing the current theme (dark mode or light mode), the logged-in user, or the selected language.

---

### Question 22: What is the useRef hook?

**Answer:** `useRef` creates a "reference" that persists across renders without causing re-renders when it changes. It is commonly used for two things:

1. **Accessing DOM elements directly** (like focusing an input field).
2. **Storing values that should not trigger re-renders** (like a timer ID).

```jsx
const inputRef = useRef(null);

// Later, to focus the input:
inputRef.current.focus();
```

The key difference from state: changing a ref does NOT cause the component to re-render.

---

### Question 23: What is the difference between `==` and `===` in JavaScript?

**Answer:** `==` is "loose equality." It converts the values to the same type before comparing. This can cause surprising results. For example, `5 == "5"` is `true` because JavaScript converts the string `"5"` to the number `5` before comparing.

`===` is "strict equality." It does NOT convert types. `5 === "5"` is `false` because one is a number and the other is a string. They are different types.

In React (and in most modern JavaScript), always use `===`. It is safer and more predictable.

---

### Question 24: What is the spread operator?

**Answer:** The spread operator (`...`) copies all the elements from an array or all the properties from an object into a new array or object. It is widely used in React for updating state without mutating the original value.

```jsx
// Copying an array and adding a new item
const newItems = [...oldItems, "New Item"];

// Copying an object and changing one property
const newUser = { ...oldUser, name: "Alice" };
```

Think of it like photocopying a document and then writing on the copy. The original stays the same.

---

### Question 25: What is destructuring?

**Answer:** Destructuring is a way to pull values out of an array or object and assign them to variables in one step.

```jsx
// Array destructuring
const [count, setCount] = useState(0);

// Object destructuring
const { name, age, email } = user;
```

Without destructuring, you would write `user.name`, `user.age`, and `user.email` every time. Destructuring saves typing and makes code cleaner.

---

### Question 26: What is an event handler in React?

**Answer:** An event handler is a function that runs when something happens, like a button click, a key press, or a form submission. In React, you attach event handlers to elements using camelCase props like `onClick`, `onChange`, and `onSubmit`.

```jsx
function handleClick() {
  alert("Button was clicked!");
}

<button onClick={handleClick}>Click Me</button>
```

Important: pass the function reference (`handleClick`), not the function call (`handleClick()`).

---

### Question 27: What is a fragment in React?

**Answer:** A fragment is an invisible wrapper that lets you group multiple elements without adding an extra HTML element to the page. You write it as `<> </>` (short syntax) or `<React.Fragment>`.

```jsx
return (
  <>
    <h1>Title</h1>
    <p>Paragraph</p>
  </>
);
```

This renders just the `<h1>` and `<p>` in the HTML, with no extra `<div>` around them. Fragments are useful when you want to return multiple elements from a component without adding unnecessary wrappers.

---

### Question 28: What is the difference between map and forEach in React?

**Answer:** Both `map` and `forEach` loop through an array. The difference is that `map` returns a new array, while `forEach` does not return anything.

In React, you use `map` to render lists because you need the result (a new array of JSX elements) to show on the screen. `forEach` does not return anything, so React has nothing to display.

```jsx
// Works - map returns an array of elements
{items.map((item) => <li key={item.id}>{item.name}</li>)}

// Does not work - forEach returns nothing
{items.forEach((item) => <li key={item.id}>{item.name}</li>)}
```

---

### Question 29: What is a custom hook?

**Answer:** A custom hook is a regular JavaScript function that uses React hooks inside it. Custom hooks let you extract and reuse logic that would otherwise be repeated in multiple components. By convention, custom hook names start with the word "use."

```jsx
function useWindowWidth() {
  const [width, setWidth] = useState(window.innerWidth);

  useEffect(() => {
    function handleResize() {
      setWidth(window.innerWidth);
    }
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return width;
}

// Using it in any component:
const width = useWindowWidth();
```

Now any component can know the window width without duplicating the resize logic.

---

### Question 30: What should you learn after React basics?

**Answer:** After you are comfortable with React basics, here are some recommended next steps:

1. **TypeScript** -- Adds type safety to your JavaScript code. It helps catch errors before they happen.
2. **React Router** -- Adds navigation and multiple pages to your app.
3. **State management** (like Redux or Zustand) -- Helps manage complex state across large apps.
4. **Next.js** -- A framework built on top of React that adds server-side rendering, routing, and more.
5. **Testing** (like React Testing Library and Jest) -- Helps you write tests to make sure your code works correctly.
6. **CSS-in-JS** (like styled-components or Tailwind CSS) -- Different ways to style your React apps.

You do not need to learn all of these at once. Pick one that interests you and go from there.

---

## Quick Summary

These 30 questions cover the core concepts of React:

- **The basics**: What React is, JSX, components, Virtual DOM
- **Data flow**: Props, state, lifting state, prop drilling, Context
- **Hooks**: useState, useEffect, useRef, custom hooks
- **Patterns**: Controlled components, conditional rendering, lists and keys
- **JavaScript essentials**: Spread operator, destructuring, `===`, map vs forEach
- **Architecture**: SPAs, library vs framework, function vs class components
- **Next steps**: TypeScript, Next.js, state management, testing

---

## Key Points to Remember

1. **React is a library**, not a framework. You are in control.
2. **Props flow down, state lives within.** Props are read-only. State is read-write.
3. **The Virtual DOM** makes React fast by updating only what changed.
4. **Hooks** let you use state and effects in function components.
5. **Keys in lists** help React track items efficiently.

---

## Practice Questions

1. Explain in your own words what the Virtual DOM is and why it is useful.

2. A friend asks you: "What is the difference between props and state?" How would you explain it to them using a real-life analogy?

3. Why do we need to use `useEffect` for fetching data instead of just calling `fetch` at the top of our component?

4. What would happen if you used `forEach` instead of `map` to render a list? Why?

5. When would you use React Context instead of just passing props?

---

## Exercises

### Exercise 1: Explain It Simply

Pick any 5 questions from this chapter and write the answers in your own words. Do not look at the answers while writing. Then compare your answers with the ones in this chapter.

### Exercise 2: Teach a Friend

Find a friend (or a rubber duck -- seriously, programmers often explain code to rubber ducks to think more clearly!) and try to explain these three concepts:
- What a React component is
- The difference between props and state
- What `useState` does

If you can explain something simply, you understand it well.

### Exercise 3: Build a Mini Quiz App

Create a simple React app that shows one question at a time from this chapter. Add a "Show Answer" button that reveals the answer. Add "Next" and "Previous" buttons to navigate between questions.

This is a great way to practice React while also studying the material.

---

## What Is Next?

You have reviewed 30 key React questions. You understand the concepts. Now it is time to put everything together. In the next and final chapter, we will build a complete Weather App from scratch. This project will use components, state, effects, API calls, loading states, error handling, and styling. It is the perfect way to end this book -- by building something real.
