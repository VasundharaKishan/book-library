# Chapter 27: How React Renders — State as a Snapshot

---

## What You Will Learn

- The three steps React follows to update the screen: Trigger, Render, Commit
- What causes a render to happen
- Why state behaves like a snapshot (a frozen photo of that moment)
- Why console.log after setState shows the old value
- What batching is and why React does it
- How to queue multiple state updates using the updater function

## Why This Chapter Matters

Have you ever changed state in your code and then immediately tried to use the new value, only to find it is still the old value? Have you ever called `setCount` three times in a row and expected the count to go up by three, but it only went up by one?

These are some of the most common confusions beginners face in React. They happen because of how React renders. Once you understand the three steps and the snapshot concept, these confusing moments will make perfect sense.

---

## The Three Steps: Trigger, Render, Commit

Think of React like a restaurant:

```
+---------------------------------------------------+
|  The Restaurant Analogy                           |
|                                                    |
|  Step 1: TRIGGER  =  The customer places an order  |
|  Step 2: RENDER   =  The kitchen cooks the food    |
|  Step 3: COMMIT   =  The waiter serves the food    |
+---------------------------------------------------+
```

Let us look at each step.

### Step 1: Trigger (Placing the Order)

A render is **triggered** in two situations:

1. **Initial render:** When your app first starts, React renders all your components for the first time. This is like a new customer sitting down and placing their first order.

2. **State update:** When you call a state setter function (like `setCount`), React knows something changed and it needs to update the screen. This is like the customer saying, "Actually, I would like to change my order."

```jsx
import { useState } from "react";

function Counter() {
  const [count, setCount] = useState(0);

  function handleClick() {
    setCount(count + 1);  // This TRIGGERS a re-render
  }

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={handleClick}>Add one</button>
    </div>
  );
}
```

**Line-by-line explanation:**

- **Line 4:** We create a state variable `count` starting at 0.
- **Line 7:** When the button is clicked, we call `setCount`. This is the trigger. React says, "The state changed. I need to re-render this component."

### Step 2: Render (Cooking the Food)

After a trigger, React **calls your component function** to figure out what should be on the screen.

This is the "cooking" step. React runs your function, and the function returns JSX. That JSX tells React what the screen should look like.

- On the **initial render**, React calls your component for the first time.
- On a **re-render**, React calls your component again with the updated state.

**Important:** "Rendering" in React means calling your function. It does NOT mean updating the screen yet. The screen update happens in the next step.

```
Render 1 (count = 0):
  Your function runs.
  It returns: <p>Count: 0</p> <button>Add one</button>

  User clicks the button. setCount(1) is called. Trigger!

Render 2 (count = 1):
  Your function runs AGAIN.
  It returns: <p>Count: 1</p> <button>Add one</button>
```

### Step 3: Commit (Serving the Food)

After rendering, React compares the new result with what is currently on the screen. If anything is different, React updates the actual screen (the DOM).

- On the **initial render**, React adds all the elements to the screen for the first time.
- On a **re-render**, React only changes the parts that are different. If only the count changed, React only updates that one number on screen. It does not rebuild the whole page.

This is like a waiter who only brings you the new dish. They do not take away all your food and re-serve everything. They just swap the one thing that changed.

```
+---------------------------------------------------+
|  The Three Steps in Action                        |
|                                                    |
|  1. TRIGGER: setCount(1) is called                |
|     "New order: count should be 1"                |
|                                                    |
|  2. RENDER: React calls Counter()                 |
|     Function returns <p>Count: 1</p>              |
|     "The food is cooked"                           |
|                                                    |
|  3. COMMIT: React updates the <p> on screen       |
|     Changes "0" to "1"                             |
|     "The food is served"                           |
+---------------------------------------------------+
```

---

## State as a Snapshot

This is the most important concept in this chapter. Read it carefully.

When you call a state setter function, React does not change the state variable immediately. Instead, React schedules a new render. And each render gets its own "snapshot" of the state.

### What Is a Snapshot?

A **snapshot** is like a photograph. When you take a photo, it captures that exact moment in time. If things change after you take the photo, the photo stays the same. It shows what things looked like at that moment.

State works the same way. When your component renders, it takes a "snapshot" of the state at that moment. All the code inside that render uses that snapshot. Even if you call setState, the current render still uses the old snapshot.

### A Diagram to Make This Clear

```
+-----------------------------------------+
|  RENDER 1 (snapshot: count = 0)         |
|                                          |
|  Everything in this render sees          |
|  count as 0. Like a photo taken          |
|  when count was 0.                       |
|                                          |
|  setCount(1) is called.                  |
|  But count is STILL 0 in this render.    |
|  The new value (1) will be used in       |
|  the NEXT render.                        |
+-----------------------------------------+
         |
         | React schedules a new render
         v
+-----------------------------------------+
|  RENDER 2 (snapshot: count = 1)         |
|                                          |
|  Everything in this render sees          |
|  count as 1. Like a new photo taken      |
|  when count was 1.                       |
+-----------------------------------------+
```

### Why console.log Shows the Old Value

This is one of the most asked questions by beginners. Look at this code:

```jsx
function Counter() {
  const [count, setCount] = useState(0);

  function handleClick() {
    setCount(count + 1);
    console.log(count);  // What does this print?
  }

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={handleClick}>Add one</button>
    </div>
  );
}
```

When you click the button, `console.log(count)` prints **0**, not 1.

Why? Because this entire function is running inside Render 1, where the snapshot says `count = 0`. Calling `setCount(1)` does not change `count` right now. It schedules a new render where `count` will be 1.

Think of it like sending a letter. When you put a letter in the mailbox, the recipient does not immediately get it. They will get it later. Similarly, `setCount(1)` tells React "next render should have count = 1." But the current render still has the old value.

```
+---------------------------------------------------+
|  Inside handleClick (during Render 1):            |
|                                                    |
|  count = 0  (this is the snapshot)                |
|                                                    |
|  setCount(0 + 1)  --> schedules count = 1         |
|                       for the NEXT render          |
|                                                    |
|  console.log(count)  --> prints 0                 |
|  Because count is still 0 in THIS render.          |
+---------------------------------------------------+
```

### Another Example to Drive It Home

```jsx
function Counter() {
  const [count, setCount] = useState(0);

  function handleClick() {
    setCount(count + 5);
    alert(count);
  }

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={handleClick}>Add five</button>
    </div>
  );
}
```

**Expected behavior:**

1. You click the button.
2. The alert shows **0** (the snapshot value).
3. After you close the alert, the screen shows **Count: 5** (the new render).

The alert uses the snapshot from when the click happened. The screen update happens in the next render.

---

## Batching: React Groups Updates Together

What happens when you call setState multiple times in the same event handler?

```jsx
function Counter() {
  const [count, setCount] = useState(0);

  function handleClick() {
    setCount(count + 1);
    setCount(count + 1);
    setCount(count + 1);
  }

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={handleClick}>Add three?</button>
    </div>
  );
}
```

You might expect `count` to go from 0 to 3. But it only goes to **1**.

Why? Remember the snapshot. All three `setCount` calls happen inside the same render where `count = 0`.

```
All three calls use the same snapshot (count = 0):

  setCount(0 + 1)  --> schedules count = 1
  setCount(0 + 1)  --> schedules count = 1
  setCount(0 + 1)  --> schedules count = 1

All three say "set count to 1." So count becomes 1.
```

It is like telling a waiter three times, "I want a coffee." You do not get three coffees. You get one coffee.

### Why Does React Batch?

**Batching** means React waits until all the code in an event handler finishes before processing the state updates. React does not re-render after each `setCount` call. It waits, collects all the updates, and then does one single re-render.

This is like a waiter who takes your complete order before going to the kitchen. They do not run to the kitchen after every item you say. They write down everything, then go once. This is more efficient.

```
+---------------------------------------------------+
|  Without batching (bad):                          |
|                                                    |
|  setCount(1) --> render --> update screen          |
|  setCount(1) --> render --> update screen          |
|  setCount(1) --> render --> update screen          |
|                                                    |
|  Three renders! Slow and wasteful.                |
+---------------------------------------------------+
|  With batching (what React does):                 |
|                                                    |
|  setCount(1)                                       |
|  setCount(1)                                       |
|  setCount(1)                                       |
|  --> ONE render --> ONE screen update              |
|                                                    |
|  One render! Fast and efficient.                  |
+---------------------------------------------------+
```

---

## Queuing State Updates: The Updater Function

So how do you actually add 3 to the count? You use an **updater function**.

Instead of passing a value to `setCount`, you pass a function. This function receives the **previous state** and returns the **new state**.

```jsx
function Counter() {
  const [count, setCount] = useState(0);

  function handleClick() {
    setCount((prev) => prev + 1);
    setCount((prev) => prev + 1);
    setCount((prev) => prev + 1);
  }

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={handleClick}>Add three</button>
    </div>
  );
}
```

**Line-by-line explanation:**

- **Line 5:** Instead of `setCount(count + 1)`, we write `setCount((prev) => prev + 1)`. The `prev` is the most recent state value.
- **Lines 6-7:** Each call gets the latest value from the previous call.

Now the count goes from 0 to 3. Here is why:

```
React processes the updater functions in order:

  Call 1: setCount((prev) => prev + 1)
          prev = 0, returns 1

  Call 2: setCount((prev) => prev + 1)
          prev = 1, returns 2

  Call 3: setCount((prev) => prev + 1)
          prev = 2, returns 3

Final state: count = 3
```

**Expected output (after clicking):**

```
Count: 3
```

### When to Use Each Style

```
+---------------------------------------------------+
|  setCount(count + 1)                              |
|  Use when: You want to set state to a specific    |
|  value based on the current snapshot.              |
|  Example: "Set the count to whatever it is now    |
|  plus one."                                        |
|                                                    |
|  setCount(prev => prev + 1)                       |
|  Use when: You want to update state based on      |
|  the PREVIOUS state, especially when doing         |
|  multiple updates in a row.                        |
|  Example: "Take whatever the latest count is      |
|  and add one."                                     |
+---------------------------------------------------+
```

### Naming the Updater Function Parameter

The parameter name `prev` is just a convention. You can name it anything. Some people use the first letter of the state variable:

```jsx
setCount((c) => c + 1);      // c for count
setAge((a) => a + 1);        // a for age
setItems((items) => [...items, newItem]);
```

Pick whatever makes the code clear.

---

## Mixing Regular Updates and Updater Functions

You can mix both styles. React processes them in order:

```jsx
function Counter() {
  const [count, setCount] = useState(0);

  function handleClick() {
    setCount(count + 5);       // Replace: set to 0 + 5 = 5
    setCount((prev) => prev + 1); // Update: 5 + 1 = 6
  }

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={handleClick}>Update</button>
    </div>
  );
}
```

```
React processes:

  Call 1: setCount(0 + 5)        --> queue says "replace with 5"
  Call 2: setCount(prev => prev + 1) --> queue says "add 1 to previous"

  Step 1: Replace with 5 --> state is 5
  Step 2: 5 + 1 = 6      --> state is 6

Final state: count = 6
```

**Expected output (after clicking):**

```
Count: 6
```

---

## A Complete Example: Understanding Render Flow

Let us trace through a full example to see everything working together.

```jsx
import { useState } from "react";

function TrafficLight() {
  const [color, setColor] = useState("red");

  function handleClick() {
    if (color === "red") {
      setColor("green");
    } else {
      setColor("red");
    }
    console.log("Color in this render:", color);
  }

  return (
    <div>
      <h2>The light is {color}</h2>
      <button onClick={handleClick}>Change</button>
    </div>
  );
}
```

**What happens when you click the button the first time:**

```
+---------------------------------------------------+
|  RENDER 1 (snapshot: color = "red")               |
|                                                    |
|  Screen shows: "The light is red"                 |
|                                                    |
|  User clicks the button.                          |
|  handleClick runs with color = "red" (snapshot).  |
|                                                    |
|  color === "red" is true.                         |
|  setColor("green") --> schedules next render.     |
|                                                    |
|  console.log prints: "Color in this render: red"  |
|  (Still the snapshot! Not "green" yet.)            |
+---------------------------------------------------+
         |
         | React triggers a new render
         v
+---------------------------------------------------+
|  RENDER 2 (snapshot: color = "green")             |
|                                                    |
|  Screen shows: "The light is green"               |
|                                                    |
|  The console.log already ran in Render 1.          |
|  Nothing else happens until the next click.        |
+---------------------------------------------------+
```

---

## State Updates with Objects

The snapshot concept also applies to objects. When you update state that is an object, you must create a new object instead of changing the old one.

```jsx
function UserProfile() {
  const [user, setUser] = useState({ name: "Sara", age: 25 });

  function handleBirthday() {
    setUser({
      ...user,        // Copy all existing properties
      age: user.age + 1,  // Override the age
    });
    console.log(user.age);  // Still prints 25 (snapshot!)
  }

  return (
    <div>
      <p>{user.name} is {user.age} years old</p>
      <button onClick={handleBirthday}>Happy Birthday!</button>
    </div>
  );
}
```

**Line-by-line explanation:**

- **Line 2:** The state is an object with `name` and `age`.
- **Lines 5-8:** We create a NEW object with the spread operator (`...user`). We do not change the old object.
- **Line 9:** The console still shows the old age (25) because of the snapshot.

**Expected output (after one click):**

Screen: `Sara is 26 years old`
Console: `25`

---

## Quick Summary

- React updates the screen in three steps: **Trigger** (something changed), **Render** (React calls your component), **Commit** (React updates the screen).
- A render is triggered by the initial load or by calling a state setter function.
- Each render gets its own **snapshot** of the state. All code in that render uses that snapshot.
- `console.log` after `setState` shows the old value because it uses the current snapshot. The new value appears in the next render.
- React **batches** state updates. It collects all updates in an event handler and then does one re-render. This is efficient.
- To update state based on the previous value (especially multiple times in a row), use an **updater function**: `setState(prev => prev + 1)`.

## Key Points to Remember

1. Trigger, Render, Commit. Like ordering food: order, cook, serve.
2. State is a snapshot. Each render has its own frozen copy of the state.
3. setState does not change state instantly. It schedules a new render.
4. React batches updates for efficiency. Multiple setStates result in one re-render.
5. Use updater functions (`prev => prev + 1`) when you need the latest value.

## Practice Questions

1. What are the three steps React follows to update the screen?
2. Why does `console.log` after `setCount(count + 1)` show the old value of count?
3. If `count` is 0 and you call `setCount(count + 1)` three times in a row, what will `count` be after the re-render? Why?
4. How would you fix the above to make `count` go from 0 to 3?
5. What is batching, and why does React do it?

## Exercises

1. Create a component with a `score` state that starts at 0. Add a button that calls `setScore(score + 10)` twice. Click the button and observe the result. Then change it to use updater functions (`prev => prev + 10`) and observe the difference.

2. Create a `TrafficLight` component that cycles through three colors: red, yellow, green. Use state and a button. After calling `setColor`, add a `console.log` to verify that the snapshot concept works (the log should show the old color, not the new one).

3. Build a simple form with a `name` and `email` stored as an object in state. Add a button that updates the name. Add a `console.log` after the update. Verify that the log shows the old name (the snapshot), while the screen shows the new name.

---

## What Is Coming Next?

Now you understand how state and rendering work. But sometimes you need to remember a value WITHOUT causing a re-render. In the next chapter, you will learn about **refs** -- a special tool that lets your component remember things without re-rendering. This is useful for things like storing timer IDs, tracking previous values, and directly accessing DOM elements like input fields.
