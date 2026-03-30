# Chapter 9: State — Remembering Things

## What You Will Learn

- What "state" means in React
- How state is different from props
- How to use the `useState` tool to give your component a memory
- How to build a simple counter that goes up when you click a button
- Why React updates the screen automatically when state changes
- Why regular variables do not work for remembering things in React

## Why This Chapter Matters

So far, your components have been like printed posters. They show information, but they cannot change. A poster on the wall always says the same thing. You cannot tap it and watch the text update.

But real apps change all the time. You click a heart button and the like count goes up. You type in a search box and results appear. You press "Add to Cart" and the cart number increases.

To make any of this happen, your components need a **memory** — a way to remember things and update the screen when those things change. In React, this memory is called **state**.

---

## What Is State?

**State** is a component's personal memory. It is information that the component keeps track of and can change over time.

Think of state like a **whiteboard in a classroom**.

```
+---------------------------+
|                           |
|   Score: 5                |  <-- You can erase and rewrite this
|                           |
+---------------------------+
        WHITEBOARD
```

- A teacher writes "Score: 5" on the whiteboard.
- A student answers a question correctly.
- The teacher erases "5" and writes "6".
- Everyone in the room sees the new score instantly.

State works the same way in React:

1. Your component has a piece of information (like a score).
2. Something happens (like a button click).
3. The information changes (score goes from 5 to 6).
4. React **automatically** updates the screen to show the new information.

The key word here is **automatically**. You do not have to tell React to update the screen. When state changes, React does it for you.

---

## Props vs State

You already know about props from earlier chapters. Let us compare props and state so you can see how they are different.

**Props** are like a **gift someone gives you**. You receive them, but you cannot change them. If someone gives you a red shirt, you cannot magically turn it into a blue shirt.

**State** is like **your own notebook**. You own it. You can write in it, erase things, and change whatever you want.

Here is a simple comparison:

```
+------------------+----------------------------------+
|                  |  Props           |  State         |
+------------------+----------------------------------+
| Who controls it? |  The parent      |  The component |
|                  |  component       |  itself        |
+------------------+------------------+----------------+
| Can it change?   |  No (read-only)  |  Yes           |
+------------------+------------------+----------------+
| Where does it    |  Passed in from  |  Created       |
| come from?       |  outside         |  inside        |
+------------------+------------------+----------------+
```

Think of it this way:

- **Props** = information given TO you (you cannot change it)
- **State** = information YOU control (you can change it)

A component can have both props and state at the same time. For example, a `LikeButton` component might receive a `username` prop (who posted the content) and have a `likeCount` state (how many likes it has).

---

## Introduction to useState

To give a component state, React provides a special tool called **`useState`**.

The word `useState` literally means "use state." It is a **hook** — a special function that React provides so your components can do extra things. We will learn more about hooks in Chapter 14. For now, just think of `useState` as a tool that gives your component a memory.

Here is how you use it:

```jsx
const [count, setCount] = useState(0);
```

This one line does a lot. Let us break it down piece by piece.

### Breaking Down useState

```
const [count, setCount] = useState(0);
       -----  --------           -
         |       |                |
         |       |                +-- Starting value (begin at 0)
         |       |
         |       +-- Function to UPDATE the value
         |
         +-- The CURRENT value
```

- **`count`** — This is the current value. It starts at `0` because we wrote `useState(0)`. You can read this value anytime.
- **`setCount`** — This is a special function that lets you change the value. When you call `setCount(5)`, the count becomes `5` and React updates the screen.
- **`useState(0)`** — The `0` inside the parentheses is the **starting value** (also called the **initial value**). This is what `count` will be when the component first appears on the screen.

The square brackets `[ ]` around `count, setCount` are called **array destructuring**. That is a fancy term. It just means "take the two things that `useState` gives back and put them into two separate variables." Do not worry about this term too much right now.

### Naming Convention

You can name the two parts anything you want, but there is a common pattern:

- The first name describes **what** the value is: `count`, `name`, `isOpen`
- The second name starts with **`set`** followed by the same word: `setCount`, `setName`, `setIsOpen`

This pattern makes your code easy to read. When you see `setCount`, you immediately know it changes the `count`.

---

## A Simple Counter

Let us build a counter. When you click a button, the number goes up by one.

```jsx
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);

  function handleClick() {
    setCount(count + 1);
  }

  return (
    <div>
      <p>You clicked {count} times</p>
      <button onClick={handleClick}>Click me</button>
    </div>
  );
}

export default Counter;
```

### Expected Output

When the page first loads:

```
You clicked 0 times
[ Click me ]
```

After clicking the button three times:

```
You clicked 3 times
[ Click me ]
```

### Line-by-Line Explanation

Let us walk through every line of this code.

**Line 1:** `import { useState } from 'react';`
We import the `useState` tool from React. We need this to give our component a memory. The curly braces `{ }` are needed because `useState` is a **named export** from the React library.

**Line 3:** `function Counter() {`
We create a component called `Counter`. Remember, components are just functions that return what should appear on the screen.

**Line 4:** `const [count, setCount] = useState(0);`
We create a piece of state. `count` starts at `0`. We get `setCount` to change it later.

**Line 6:** `function handleClick() {`
We create a regular function called `handleClick`. This function describes what should happen when the button is clicked.

**Line 7:** `setCount(count + 1);`
When called, this takes the current count, adds 1 to it, and sets that as the new count. If `count` is `3`, then `count + 1` is `4`, so the count becomes `4`.

**Line 10-15:** The `return` block.
This is what appears on the screen:
- A paragraph showing `You clicked {count} times`. The `{count}` part will be replaced with the actual number.
- A button that calls `handleClick` when clicked.

**Line 18:** `export default Counter;`
We export the component so other files can use it.

---

## How React Re-Renders When State Changes

When you call `setCount`, something magical happens behind the scenes. Let us follow the steps:

```
Step 1: You click the button
         |
         v
Step 2: handleClick() runs
         |
         v
Step 3: setCount(count + 1) is called
         |
         v
Step 4: React sees the state changed
         |
         v
Step 5: React calls the Counter function again (re-render)
         |
         v
Step 6: The new count value is used
         |
         v
Step 7: The screen updates with the new number
```

This process is called a **re-render**. The word "render" means "to draw on the screen." A **re-render** means React draws the component on the screen again with the new information.

The important thing to understand is: **you do not update the screen yourself.** You just change the state, and React takes care of updating the screen. This is one of the biggest reasons React is so popular. It handles all the screen-updating work for you.

---

## Why Regular Variables Do Not Work

You might wonder: "Why do I need `useState`? Why not just use a regular variable?"

Great question. Let us try it and see what happens.

```jsx
function BrokenCounter() {
  let count = 0;  // regular variable

  function handleClick() {
    count = count + 1;
    console.log(count);  // This WILL show the new number in the console
  }

  return (
    <div>
      <p>You clicked {count} times</p>
      <button onClick={handleClick}>Click me</button>
    </div>
  );
}
```

### What Happens

If you click the button, the screen will **always** say "You clicked 0 times." It never changes. But if you look at the console (the developer tool in your browser), you will see the number going up: 1, 2, 3...

### Why?

Two reasons:

1. **Regular variables do not trigger a re-render.** When you change a regular variable, React does not know anything changed. It does not update the screen. The `useState` function is special because it tells React: "Hey, something changed! Please update the screen."

2. **Regular variables reset every render.** Even if React did re-render, the line `let count = 0` runs every time the component function runs. So `count` would go back to `0` on every render.

Think of it this way:

```
Regular variable = Writing on a piece of paper, then throwing
                   the paper away and starting with a new one
                   every time.

State variable   = Writing on a whiteboard. It stays there
                   until you erase it and write something new.
```

This is why we need `useState`. It is the only way to:
- Tell React to update the screen
- Keep the value between renders

---

## More State Examples

### Example: Toggle a Message

State does not have to be a number. It can be a **boolean** (true or false), a **string** (text), or many other things.

Here is an example that shows or hides a message:

```jsx
import { useState } from 'react';

function ToggleMessage() {
  const [isVisible, setIsVisible] = useState(false);

  function handleClick() {
    setIsVisible(!isVisible);
  }

  return (
    <div>
      <button onClick={handleClick}>
        {isVisible ? 'Hide' : 'Show'} Message
      </button>
      {isVisible && <p>Hello! Now you can see me!</p>}
    </div>
  );
}
```

**What is happening here:**

- `isVisible` starts as `false` (the message is hidden).
- When you click the button, `!isVisible` flips the value. If it was `false`, it becomes `true`. If it was `true`, it becomes `false`. The `!` symbol means "the opposite of."
- When `isVisible` is `true`, the paragraph appears. When it is `false`, it disappears.
- The button text also changes: it says "Show Message" when hidden and "Hide Message" when visible.

Do not worry about the `? :` and `&&` syntax too much right now. We will cover those in Chapter 11 on conditional rendering.

### Example: Name Display

Here is an example with a text string as state:

```jsx
import { useState } from 'react';

function NameDisplay() {
  const [name, setName] = useState('World');

  function changeName() {
    setName('React Learner');
  }

  return (
    <div>
      <p>Hello, {name}!</p>
      <button onClick={changeName}>Change Name</button>
    </div>
  );
}
```

**Expected output when the page loads:**

```
Hello, World!
[ Change Name ]
```

**After clicking the button:**

```
Hello, React Learner!
[ Change Name ]
```

---

## Mini Project: Like Button Counter

Let us build a simple like button, similar to what you see on social media apps. When you click the heart, the like count goes up.

```jsx
import { useState } from 'react';

function LikeButton() {
  const [likes, setLikes] = useState(0);

  function handleLike() {
    setLikes(likes + 1);
  }

  return (
    <div>
      <button onClick={handleLike}>
        ♥ Like
      </button>
      <p>{likes} {likes === 1 ? 'like' : 'likes'}</p>
    </div>
  );
}

export default LikeButton;
```

### Expected Output

When the page loads:

```
[ ♥ Like ]
0 likes
```

After clicking three times:

```
[ ♥ Like ]
3 likes
```

After clicking once:

```
[ ♥ Like ]
1 like     <-- Notice: "like" not "likes" (singular)
```

### Line-by-Line Explanation

**Line 1:** `import { useState } from 'react';`
Import the `useState` tool from React.

**Line 3:** `function LikeButton() {`
Create a component called `LikeButton`.

**Line 4:** `const [likes, setLikes] = useState(0);`
Create state called `likes`, starting at `0`. The function `setLikes` will let us change the number.

**Line 6-8:** `function handleLike() { setLikes(likes + 1); }`
This function adds 1 to the current like count.

**Line 12:** `<button onClick={handleLike}>`
When the button is clicked, run the `handleLike` function.

**Line 13:** `♥ Like`
The text on the button. The `♥` is a heart symbol.

**Line 15:** `<p>{likes} {likes === 1 ? 'like' : 'likes'}</p>`
Show the number of likes. The `likes === 1 ? 'like' : 'likes'` part checks: "Is the number exactly 1?" If yes, show "like" (singular). If no, show "likes" (plural). The `===` symbol means "is exactly equal to."

---

## Quick Summary

- **State** is a component's memory. It stores information that can change.
- **Props** are given to a component from outside. **State** is created and controlled inside the component.
- **`useState`** is a React tool (hook) that gives your component state.
- `useState` returns two things: the **current value** and a **function to change it**.
- When you call the set function (like `setCount`), React **re-renders** the component — it updates the screen automatically.
- Regular variables do not work because they do not trigger re-renders and they reset on every render.

---

## Key Points to Remember

1. Always import `useState` from React: `import { useState } from 'react';`
2. The starting value goes inside the parentheses: `useState(0)`, `useState('')`, `useState(false)`
3. Never change state directly. Always use the set function. Write `setCount(5)`, not `count = 5`.
4. State can hold numbers, strings, booleans, arrays, objects — almost anything.
5. Each component has its own separate state. If you put two `Counter` components on the page, each one has its own count.
6. When state changes, React automatically updates what you see on the screen.

---

## Practice Questions

1. In your own words, what is the difference between props and state?

2. Look at this code. What is the starting value of `temperature`?
   ```jsx
   const [temperature, setTemperature] = useState(72);
   ```

3. Why does this code NOT update the screen when you click the button?
   ```jsx
   function Counter() {
     let count = 0;
     function handleClick() {
       count = count + 1;
     }
     return <button onClick={handleClick}>{count}</button>;
   }
   ```

4. What will the screen show after clicking the button twice in the counter example from this chapter?

5. What does "re-render" mean?

---

## Practice Exercises

### Exercise 1: Score Keeper

Build a component called `ScoreKeeper` that:
- Shows "Score: 0" when the page loads
- Has a button that says "Score!"
- Each click adds 1 to the score

Hint: This is very similar to the counter example. Just change the variable names and the text.

### Exercise 2: Mood Changer

Build a component called `MoodChanger` that:
- Shows a mood emoji (start with "😊")
- Has a button that says "Change Mood"
- When clicked, the emoji changes to "😎"

Hint: Use `useState` with a string value.

### Exercise 3: Step Counter

Build a component called `StepCounter` that:
- Shows "Steps today: 0"
- Has a button that says "Take a Step"
- Each click adds 1 to the step count
- Also shows a message: if steps are 0, show "Let's get moving!" If steps are more than 0, show "Keep going!"

Hint: You can use the same `count` state and check if it is 0 or not.

---

## What Is Next?

Now your components have a memory. They can remember things and change. But right now, the only way to change state is with a button click. In the next chapter, **Chapter 10: Events — Making Things Happen**, you will learn about all the different ways users can interact with your app — clicking, typing, hovering, submitting forms, and more. Events are what make your app come alive!
