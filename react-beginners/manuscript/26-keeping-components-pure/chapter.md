# Chapter 26: Keeping Components Pure

---

## What You Will Learn

- What a "pure" function is, in simple everyday words
- Why React components should be pure
- What side effects are and where they belong
- How to spot and fix impure components
- What StrictMode does and why React renders twice in development
- The rules for keeping your components pure

## Why This Chapter Matters

Imagine you go to a bakery and order a chocolate cake. You expect a chocolate cake every time you order one. But what if sometimes you got vanilla, sometimes strawberry, and sometimes the baker ate half of it before giving it to you? That bakery would be chaos.

React components are like recipes. When you give them the same ingredients (props), they should always produce the same result. This is called being **pure**. When your components are pure, your app is predictable, easy to understand, and has fewer bugs.

This chapter teaches you the rules for writing pure components and shows you what happens when you break those rules.

---

## What Does "Pure" Mean?

### Pure Functions in Everyday Life

A **pure function** is like a math formula.

Think about the formula: **double(x) = x times 2**

- If you give it 3, you always get 6.
- If you give it 5, you always get 10.
- If you give it 3 again, you still get 6. Always.

It does not matter what day it is. It does not matter how many times you call it. It does not matter what other formulas you used before. Same input, same output. Every single time.

A pure function follows two rules:

1. **Same input, same output.** Given the same inputs, it always returns the same result.
2. **No side effects.** It does not change anything outside of itself. It minds its own business.

### Pure Functions in Code

Here is a pure function:

```jsx
function double(number) {
  return number * 2;
}
```

**Line-by-line explanation:**

- **Line 1:** The function takes a number as input.
- **Line 2:** It returns that number multiplied by 2. Nothing else happens.

If you call `double(3)`, you get 6. Always. It does not change any other variable. It does not modify anything outside of itself. It just takes input and returns output.

### What Are Side Effects?

A **side effect** is when a function changes something outside of itself. Think of it as a "side action" that happens in addition to returning a result.

Here are examples of side effects in everyday life:

- You go to a restaurant to eat (main action), but you also rearrange the furniture (side effect).
- You borrow a book from a friend (main action), but you write notes in it (side effect).
- You ask someone what time it is (main action), but you also change their watch (side effect).

In code, side effects include:

- Changing a variable that exists outside the function
- Changing the content on the screen directly
- Writing to a file
- Sending a network request
- Setting a timer

Side effects are not bad. They are necessary. Your app needs to do things like show data, save information, and talk to servers. But there is a right place and a wrong place for them.

---

## React Components Should Be Pure

React expects your components to behave like pure functions. Given the same props and state, a component should always return the same JSX.

### A Pure Component

```jsx
function Greeting({ name }) {
  return <h1>Hello, {name}!</h1>;
}
```

**Line-by-line explanation:**

- **Line 1:** The component receives a `name` prop.
- **Line 2:** It returns a heading that says "Hello" followed by the name.

If you pass `name="Sara"`, you always get `<h1>Hello, Sara!</h1>`. Every time. No surprises.

**Expected output:**

```
Hello, Sara!
```

### A Pure Component Is Like a Recipe

Think of a component as a recipe:

```
+---------------------------------------------+
|  Recipe: Greeting                            |
|                                              |
|  Ingredients (props):                        |
|    - name                                    |
|                                              |
|  Instructions:                               |
|    1. Take the name                          |
|    2. Put "Hello, " before it                |
|    3. Put "!" after it                       |
|    4. Serve in an <h1> tag                   |
|                                              |
|  Same ingredients = Same dish. Always.       |
+---------------------------------------------+
```

---

## Examples of Impure Components (And How to Fix Them)

### Problem 1: Changing a Variable Outside the Component

Here is an impure component:

```jsx
let guestCount = 0;

function GuestGreeting() {
  guestCount = guestCount + 1;
  return <h2>Guest number {guestCount}</h2>;
}
```

**Why this is impure:** Every time this component renders, it changes `guestCount`. That variable lives outside the component. If React renders this component three times, you get "Guest number 1", "Guest number 2", "Guest number 3". Same component, different results. That is not pure.

Even worse, if another component also uses `guestCount`, it will get unexpected values. One component is secretly changing a value that others depend on.

**The fix:** Use a prop or compute the value inside:

```jsx
function GuestGreeting({ guestNumber }) {
  return <h2>Guest number {guestNumber}</h2>;
}
```

**Line-by-line explanation:**

- **Line 1:** Now the guest number comes in as a prop.
- **Line 2:** We just display it. We do not change anything outside.

Now you use it like this:

```jsx
<GuestGreeting guestNumber={1} />
<GuestGreeting guestNumber={2} />
<GuestGreeting guestNumber={3} />
```

**Expected output:**

```
Guest number 1
Guest number 2
Guest number 3
```

Same input, same output. Every time. And nothing outside the component changes.

### Problem 2: Changing Props Directly

Here is another impure component:

```jsx
function ShoppingItem({ item }) {
  item.quantity = item.quantity + 1;  // DO NOT do this!
  return <p>{item.name}: {item.quantity}</p>;
}
```

**Why this is impure:** This component reaches into the `item` object and changes it. The `item` was passed in as a prop. Props are like a package someone gives you. You should not open it and rearrange the contents. The sender might not expect that.

**The fix:** Do not change props. If you need a different value, create a new variable:

```jsx
function ShoppingItem({ item }) {
  const displayQuantity = item.quantity + 1;
  return <p>{item.name}: {displayQuantity}</p>;
}
```

**Line-by-line explanation:**

- **Line 2:** We create a new variable `displayQuantity` instead of changing the original. The original `item` stays the same.
- **Line 3:** We use our new variable for display.

### Problem 3: Using Random Values in Render

```jsx
function Dice() {
  const roll = Math.floor(Math.random() * 6) + 1;
  return <p>You rolled: {roll}</p>;
}
```

**Why this is a problem:** Every time this component renders, it gives a different result. Same input (no props), different output. This is technically impure because it is unpredictable.

If you need random values, generate them outside the component and pass them in as props, or generate them in an event handler (like when the user clicks a "Roll" button).

**The fix:**

```jsx
function Dice({ value }) {
  return <p>You rolled: {value}</p>;
}

// In a parent component:
function DiceGame() {
  const [roll, setRoll] = useState(1);

  function handleRoll() {
    setRoll(Math.floor(Math.random() * 6) + 1);
  }

  return (
    <div>
      <Dice value={roll} />
      <button onClick={handleRoll}>Roll dice</button>
    </div>
  );
}
```

**Expected output (after clicking the button):**

```
You rolled: 4
[Roll dice]
```

Now the randomness happens in an event handler (when the user clicks), not during rendering.

---

## The Rules for Pure Components

Here are the rules, stated simply:

```
+--------------------------------------------------+
|  Rules for Pure Components                        |
|                                                   |
|  1. Do NOT change variables that existed          |
|     before your function was called.              |
|                                                   |
|  2. Do NOT change your props.                     |
|                                                   |
|  3. Do NOT change another component's state.      |
|                                                   |
|  4. Same inputs should ALWAYS produce             |
|     the same output.                              |
+--------------------------------------------------+
```

### What You CAN Do Inside a Component

You can create and change **local variables**. Variables you create inside the component are fine to change because they are brand new each time the component renders:

```jsx
function ShoppingList({ items }) {
  const rows = [];  // Created fresh every render

  items.forEach((item) => {
    rows.push(<li key={item.id}>{item.name}</li>);
  });

  return <ul>{rows}</ul>;
}
```

**Line-by-line explanation:**

- **Line 2:** We create a new empty array. This is fine because we created it right here, right now. We are not changing something that existed before.
- **Lines 4-6:** We add items to our new array. Still fine. It is our array. We just made it.
- **Line 8:** We return the list. Everything that happened stayed inside this function.

This is called **local mutation** (mutation means "change"). Changing something you just created inside your function is perfectly fine.

---

## StrictMode: React's Helper for Finding Impure Components

React has a tool called **StrictMode** that helps you find impure components during development.

When StrictMode is on, React **renders every component twice**. Why? Because if a component is pure, rendering it twice should give the same result. If rendering it twice gives different results, you have a bug.

Remember our impure example?

```jsx
let guestCount = 0;

function GuestGreeting() {
  guestCount = guestCount + 1;
  return <h2>Guest number {guestCount}</h2>;
}
```

With StrictMode, React renders this component twice:

- First render: `guestCount` becomes 1. Shows "Guest number 1".
- Second render: `guestCount` becomes 2. Shows "Guest number 2".

Different results! StrictMode helps you notice this problem.

StrictMode is usually already set up in your app:

```jsx
import { StrictMode } from "react";

function App() {
  return (
    <StrictMode>
      <MyApp />
    </StrictMode>
  );
}
```

**Important:** StrictMode only runs in development. When you build your app for real users (production), it does not render twice. It does not slow down your live app.

### Do Not Panic About Double Rendering

When you see console.log messages appearing twice during development, it is usually StrictMode doing its job. This is normal and expected. It helps you catch bugs early.

---

## Where Do Side Effects Belong?

If components should be pure, where do you put code that changes the outside world? Code that:

- Saves data to a server
- Changes the page title
- Starts a timer
- Focuses an input field

These side effects belong in two places:

### 1. Event Handlers

An **event handler** is a function that runs when the user does something (clicks a button, types in a field, submits a form).

```jsx
function ContactForm() {
  const [name, setName] = useState("");

  function handleSubmit() {
    // Side effect: sending data to a server
    fetch("/api/contacts", {
      method: "POST",
      body: JSON.stringify({ name }),
    });
    alert("Saved!");  // Side effect: showing an alert
  }

  return (
    <form onSubmit={handleSubmit}>
      <input value={name} onChange={(e) => setName(e.target.value)} />
      <button type="submit">Save</button>
    </form>
  );
}
```

The side effects (sending data and showing an alert) happen inside `handleSubmit`. This function runs only when the user clicks Submit, not during rendering. That is the right place.

### 2. useEffect (for effects that happen after rendering)

Sometimes you need a side effect that is not triggered by the user. For example, you want to fetch data when the component first appears. That is what `useEffect` is for:

```jsx
import { useState, useEffect } from "react";

function UserProfile({ userId }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetch(`/api/users/${userId}`)
      .then((response) => response.json())
      .then((data) => setUser(data));
  }, [userId]);

  if (!user) return <p>Loading...</p>;
  return <h1>{user.name}</h1>;
}
```

The `useEffect` runs AFTER the component renders. It is separate from the render process. The rendering itself stays pure.

Think of it this way:

```
+---------------------------------------------+
|  During rendering:                           |
|    - Calculate what to show (pure!)          |
|    - Return JSX                              |
|                                              |
|  After rendering (event handlers, useEffect):|
|    - Talk to servers                         |
|    - Update the page title                   |
|    - Start timers                            |
|    - Focus input fields                      |
+---------------------------------------------+
```

---

## A Before-and-After Example

Let us fix one more impure component to really cement this concept.

### Before (Impure)

```jsx
let totalOrders = 0;

function OrderSummary({ items }) {
  totalOrders = totalOrders + 1;
  document.title = `Order #${totalOrders}`;

  return (
    <div>
      <h2>Order #{totalOrders}</h2>
      <p>Items: {items.length}</p>
    </div>
  );
}
```

**Problems:**

- It changes `totalOrders`, which lives outside the component.
- It changes `document.title` directly during rendering (side effect).
- Calling it twice gives different results.

### After (Pure)

```jsx
import { useEffect } from "react";

function OrderSummary({ orderNumber, items }) {
  useEffect(() => {
    document.title = `Order #${orderNumber}`;
  }, [orderNumber]);

  return (
    <div>
      <h2>Order #{orderNumber}</h2>
      <p>Items: {items.length}</p>
    </div>
  );
}
```

**What changed:**

- The order number now comes in as a prop. The component does not track it.
- Changing `document.title` moved into `useEffect`, so it happens after rendering, not during.
- Same props will always produce the same JSX. The component is now pure.

**Expected output (with orderNumber={5} and 3 items):**

```
Order #5
Items: 3
```

And the browser tab title will say "Order #5".

---

## Quick Summary

- A **pure function** always gives the same output for the same input and does not change anything outside itself.
- React components should be pure. Same props and state should always produce the same JSX.
- **Do not** change variables outside your component, change props, or change other components' state during rendering.
- You **can** change variables you create inside your component during that render.
- **Side effects** (like saving data, changing the page title, or setting timers) belong in event handlers or `useEffect`, not during rendering.
- **StrictMode** renders components twice in development to help you find impure code.

## Key Points to Remember

1. Pure component = same input, same output. Like a math formula.
2. Never change props. They belong to the parent.
3. Create new variables instead of changing existing ones.
4. Event handlers are the right place for most side effects.
5. StrictMode double-renders only in development, not in production.

## Practice Questions

1. In your own words, what does "pure" mean for a React component?
2. What is a side effect? Give two examples.
3. Why does React render components twice in development when StrictMode is on?
4. A component reads the current time with `new Date()` and displays it. Is this component pure? Why or why not?
5. Where should you put code that sends data to a server: during rendering or in an event handler?

## Exercises

1. Look at this component and explain what makes it impure. Then fix it:

```jsx
let clickCount = 0;

function ClickTracker() {
  clickCount = clickCount + 1;
  return <p>This component rendered {clickCount} times</p>;
}
```

2. Write a pure component called `PriceTag` that receives `price` and `currency` as props and displays them together (like "$25.00" or "EUR 15.00"). Make sure it follows all the purity rules.

3. Take this impure component and move the side effect to the correct place:

```jsx
function PageTitle({ title }) {
  document.title = title;
  return <h1>{title}</h1>;
}
```

---

## What Is Coming Next?

Now that you understand purity, the next chapter dives deeper into **how React actually renders your components**. You will learn about the three steps React follows (trigger, render, commit), why state behaves like a snapshot, and why `console.log` after `setState` shows the old value. Understanding this will clear up many confusing moments you might encounter.
