# Chapter 15: useEffect — Doing Things at the Right Time

---

## What You Will Learn

- What side effects are in React
- How the useEffect hook works
- How to run code once when a component first appears
- How to run code when specific values change
- How to clean up after your effects (cancel timers, remove listeners)
- How to change the document title based on state
- How to set up a timer with setInterval
- Common mistakes with useEffect and how to avoid them
- How to read the dependency array diagram

## Why This Chapter Matters

So far, your components have been doing one thing: rendering what the user sees on the screen. But real applications need to do more than just show things. They need to:

- Fetch data from the internet when a page loads
- Start a timer that counts down
- Change the title of the browser tab
- Listen for keyboard shortcuts
- Save data to the browser's storage

These are all things that happen **outside** of rendering. React calls them **side effects**. The `useEffect` hook is how you tell React: "After you finish rendering, also do this other thing." It is one of the most important hooks in React, and understanding it well will make you a much stronger developer.

---

## What Are Side Effects?

Let us start with a simple idea. A React component has one main job: take some data (state, props) and return some JSX (what to show on the screen). That is **rendering**.

A **side effect** is anything else your component does that is not about returning JSX. It is anything that reaches outside of the component to interact with the outside world.

Here are examples of side effects:

- **Fetching data** from an API (talking to a server on the internet)
- **Setting a timer** (like `setTimeout` or `setInterval`)
- **Changing the document title** (the text in the browser tab)
- **Writing to the browser's local storage** (saving data locally)
- **Adding an event listener** to the window (like listening for key presses)
- **Logging something** to the console

### A Real-Life Analogy

Think of a waiter at a restaurant.

The waiter's main job is to take your order and bring you food. That is like rendering. Take the data (your order) and show the result (your food).

But the waiter also does other things:
- Turns on the restaurant's music when they arrive (setup)
- Wipes the tables between customers (cleanup)
- Checks the weather to decide if the patio is open (external data)

These are side effects. They are not the main job, but they are necessary.

In React, we use `useEffect` to handle these side effects.

---

## The useEffect Hook

Here is the basic shape of `useEffect`:

```jsx
import { useEffect } from 'react';

useEffect(() => {
  // Your side effect code goes here
});
```

You pass a function to `useEffect`. React will run that function **after** the component renders. Not before, not during. After.

Think of it as telling React: "Hey React, after you finish showing stuff on the screen, please also do this thing for me."

### Your First useEffect

Let us start with a simple example: changing the document title.

```jsx
import { useState, useEffect } from 'react';

function Counter() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    document.title = 'Count: ' + count;
  });

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Add 1</button>
    </div>
  );
}

export default Counter;
```

**What happens:**

When you open this page, the browser tab title changes to "Count: 0". Every time you click the button, the tab title updates: "Count: 1", "Count: 2", and so on.

### Line-by-Line Explanation

```jsx
import { useState, useEffect } from 'react';
```

We import both `useState` and `useEffect` from React.

```jsx
useEffect(() => {
  document.title = 'Count: ' + count;
});
```

After every render, React runs this function. It changes the browser tab title to show the current count. `document.title` is a built-in browser feature that lets you change the text in the browser tab.

Without the second argument (the dependency array, which we will learn about next), this effect runs **after every single render**. That is often more than we need.

---

## The Dependency Array

The dependency array is the second argument to `useEffect`. It is an array that tells React: "Only run this effect when these specific values change."

There are three ways to use the dependency array:

### 1. No Dependency Array — Runs After Every Render

```jsx
useEffect(() => {
  console.log('I run after every render');
});
```

This runs after the first render, and again after every re-render. Use this rarely. It can cause performance problems.

### 2. Empty Dependency Array `[]` — Runs Once

```jsx
useEffect(() => {
  console.log('I run only once, when the component first appears');
}, []);
```

The empty array `[]` tells React: "There is nothing I depend on. Run me once when the component first appears, and never again."

This is perfect for:
- Fetching data when a page loads
- Setting up something one time
- Logging that a component has appeared

Think of it like setting up a new apartment. You unpack your boxes once when you move in. You do not unpack them again every time you walk through the door.

### 3. Dependency Array with Values — Runs When Those Values Change

```jsx
useEffect(() => {
  console.log('Count changed to:', count);
}, [count]);
```

This tells React: "Run this effect when `count` changes." It runs once when the component first appears, and then again every time `count` gets a new value. It does NOT run when other state values change.

```jsx
useEffect(() => {
  document.title = 'Count: ' + count;
}, [count]);
```

This is better than our earlier example. The document title only updates when `count` changes, not on every render.

### Dependency Array Diagram

Here is a visual summary:

```
useEffect(() => { ... });           No array → Runs after EVERY render
                                    ┌────────────────────────────────┐
                                    │ Render 1: runs                 │
                                    │ Render 2: runs                 │
                                    │ Render 3: runs                 │
                                    │ Every render: runs             │
                                    └────────────────────────────────┘

useEffect(() => { ... }, []);       Empty array → Runs ONCE
                                    ┌────────────────────────────────┐
                                    │ Render 1: runs                 │
                                    │ Render 2: does NOT run         │
                                    │ Render 3: does NOT run         │
                                    │ Only first render              │
                                    └────────────────────────────────┘

useEffect(() => { ... }, [count]);  With values → Runs when value CHANGES
                                    ┌────────────────────────────────┐
                                    │ Render 1: runs (initial)       │
                                    │ Render 2: runs IF count changed│
                                    │ Render 3: skips if count same  │
                                    │ Only when count changes        │
                                    └────────────────────────────────┘
```

---

## useEffect with an Empty Dependency Array

This is one of the most common patterns. Let us see a clear example.

```jsx
import { useState, useEffect } from 'react';

function WelcomeMessage() {
  const [message, setMessage] = useState('');

  useEffect(() => {
    console.log('Component appeared on the screen!');
    setMessage('Welcome! This page loaded at ' + new Date().toLocaleTimeString());
  }, []);

  return <p>{message}</p>;
}

export default WelcomeMessage;
```

**What you will see:**

```
Welcome! This page loaded at 2:30:45 PM
```

The time is set once when the component first appears. No matter how many times the component re-renders (because of other state changes), this effect does not run again. The time stays the same.

---

## useEffect with Dependencies

Let us build a component that shows a message based on a count, but only recalculates the message when the count changes.

```jsx
import { useState, useEffect } from 'react';

function CountMessage() {
  const [count, setCount] = useState(0);
  const [name, setName] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    console.log('Count changed! Updating message...');
    if (count === 0) {
      setMessage('You have not clicked yet.');
    } else if (count < 5) {
      setMessage('Keep clicking!');
    } else if (count < 10) {
      setMessage('You are doing great!');
    } else {
      setMessage('You are a clicking champion!');
    }
  }, [count]);

  return (
    <div>
      <input
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Type your name"
      />
      <p>Hello, {name}!</p>

      <p>Count: {count}</p>
      <p>{message}</p>
      <button onClick={() => setCount(prev => prev + 1)}>Click Me</button>
    </div>
  );
}

export default CountMessage;
```

**What you will see:**

```
[Type your name___]
Hello, Sara!

Count: 3
Keep clicking!
[Click Me]
```

The important thing to notice: when you type in the name input, the component re-renders, but the `useEffect` does NOT run. It only runs when `count` changes. You can check the console — you will only see "Count changed!" when you click the button, not when you type.

---

## The Cleanup Function

Sometimes your side effects create things that need to be cleaned up. For example:

- You start a timer. When the component disappears, you should stop the timer.
- You add a keyboard listener. When the component disappears, you should remove it.
- You open a connection. When the component disappears, you should close it.

If you do not clean up, you can have **memory leaks** (the program keeps using memory for things that are no longer needed) or **bugs** (old timers still running in the background).

### A Real-Life Analogy

Think of throwing a party at your house.

- **The effect**: You set up decorations, play music, and prepare food.
- **The cleanup**: After the party, you take down the decorations, stop the music, and clean up the food.

If you never clean up, your house gets messier and messier with each party. The same thing happens in your app if you do not clean up side effects.

### How Cleanup Works

To add cleanup, you return a function from your effect. React will call this function before the effect runs again, and also when the component is removed from the screen.

```jsx
useEffect(() => {
  // Setup: do something
  console.log('Effect runs');

  return () => {
    // Cleanup: undo what you did
    console.log('Cleanup runs');
  };
}, []);
```

The flow looks like this:

```
1. Component appears → Effect runs (setup)
2. Component disappears → Cleanup runs
```

For effects with dependencies:

```
1. Component appears → Effect runs (setup)
2. Dependency changes → Cleanup runs (for the old effect), then Effect runs again (new setup)
3. Component disappears → Cleanup runs (final cleanup)
```

---

## Example: Changing the Document Title

Let us combine what we have learned into a clean example:

```jsx
import { useState, useEffect } from 'react';

function PageTitle() {
  const [title, setTitle] = useState('My App');

  useEffect(() => {
    document.title = title;
  }, [title]);

  return (
    <div>
      <label>Page title: </label>
      <input
        type="text"
        value={title}
        onChange={(event) => setTitle(event.target.value)}
      />
      <p>Look at the browser tab to see the title change!</p>
    </div>
  );
}

export default PageTitle;
```

**What happens:**

As you type in the input, the browser tab title updates in real time. If you type "Hello World", the browser tab will say "Hello World".

This is a side effect because changing the document title is something outside of what React renders. React draws the input and the paragraph. The document title is part of the browser, not part of your component's JSX.

---

## Example: Setting Up a Timer

Timers are a classic use case for `useEffect`. Let us build a simple stopwatch.

```jsx
import { useState, useEffect } from 'react';

function Stopwatch() {
  const [seconds, setSeconds] = useState(0);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    if (!isRunning) return;

    const intervalId = setInterval(() => {
      setSeconds(prev => prev + 1);
    }, 1000);

    return () => {
      clearInterval(intervalId);
    };
  }, [isRunning]);

  function reset() {
    setIsRunning(false);
    setSeconds(0);
  }

  return (
    <div>
      <p>Time: {seconds} seconds</p>
      <button onClick={() => setIsRunning(true)}>Start</button>
      <button onClick={() => setIsRunning(false)}>Stop</button>
      <button onClick={reset}>Reset</button>
    </div>
  );
}

export default Stopwatch;
```

**What you will see:**

```
Time: 7 seconds
[Start]  [Stop]  [Reset]
```

### Line-by-Line Explanation

```jsx
useEffect(() => {
  if (!isRunning) return;
```

If the stopwatch is not running, we do nothing. We exit the effect early.

```jsx
const intervalId = setInterval(() => {
  setSeconds(prev => prev + 1);
}, 1000);
```

`setInterval` is a built-in JavaScript function. It runs the given function every 1000 milliseconds (1 second). Each second, it adds 1 to the seconds count. We use the updater function (`prev => prev + 1`) to always get the latest value.

`setInterval` returns an ID number. We store this ID so we can stop the timer later.

```jsx
return () => {
  clearInterval(intervalId);
};
```

This is the cleanup function. `clearInterval` stops the timer. This runs when:
- The component disappears from the screen
- The `isRunning` value changes (React cleans up the old effect before running the new one)

```jsx
}, [isRunning]);
```

This effect depends on `isRunning`. When `isRunning` changes from `false` to `true`, the effect runs and starts the timer. When `isRunning` changes from `true` to `false`, the cleanup runs and stops the timer.

### Why Cleanup Is Critical Here

Without the cleanup function, every time `isRunning` changes to `true`, a new timer would start. But the old timer would still be running. You would have two timers, then three, then four. The seconds would increase faster and faster. The cleanup ensures only one timer runs at a time.

---

## Common Mistakes with useEffect

### Mistake 1: Infinite Loop (Missing or Wrong Dependencies)

This is the most common mistake. It can freeze your browser.

```jsx
// DANGER — INFINITE LOOP
useEffect(() => {
  setCount(count + 1);
}, [count]);
```

What happens here:
1. Component renders. `count` is 0.
2. Effect runs. Sets `count` to 1.
3. `count` changed, so the component re-renders.
4. Effect runs again. Sets `count` to 2.
5. `count` changed again, so the component re-renders.
6. This never stops!

The effect depends on `count`, and it also changes `count`. That creates an infinite loop.

**How to avoid it**: Be careful about updating a state variable inside an effect that depends on that same variable. Ask yourself: "Will this update trigger the effect again?" If yes, you probably have a problem.

### Mistake 2: Missing Dependencies

```jsx
// WARNING — Stale value
useEffect(() => {
  const intervalId = setInterval(() => {
    console.log('Count is:', count);  // This will always show the old value!
  }, 1000);

  return () => clearInterval(intervalId);
}, []);  // Empty array means this effect never re-runs
```

Because the dependency array is empty, this effect runs once with the initial value of `count`. The interval will always log the initial value, even as `count` changes.

**Fix**: Either add `count` to the dependency array, or use the updater function form if you are setting state.

### Mistake 3: Forgetting Cleanup

```jsx
// BAD — No cleanup!
useEffect(() => {
  setInterval(() => {
    console.log('tick');
  }, 1000);
}, []);
```

This starts a timer but never stops it. If this component appears and disappears multiple times (which happens often in React), you will have multiple timers running, all logging "tick" forever.

**Fix**: Always return a cleanup function when you set up timers, listeners, or subscriptions.

```jsx
// GOOD — With cleanup
useEffect(() => {
  const id = setInterval(() => {
    console.log('tick');
  }, 1000);

  return () => clearInterval(id);  // Stop the timer when cleaning up
}, []);
```

### Mistake 4: Putting Too Much in One Effect

```jsx
// Not ideal — too many responsibilities
useEffect(() => {
  document.title = 'Count: ' + count;
  fetchData();
  setupTimer();
  trackAnalytics();
}, [count]);
```

If only the document title depends on `count`, but the other functions do not, they will all run every time `count` changes unnecessarily.

**Fix**: Use multiple `useEffect` calls. Each one handles one concern.

```jsx
useEffect(() => {
  document.title = 'Count: ' + count;
}, [count]);

useEffect(() => {
  fetchData();
}, []);

useEffect(() => {
  const id = setupTimer();
  return () => clearInterval(id);
}, []);
```

It is perfectly fine and even recommended to have multiple `useEffect` calls in one component.

---

## A Complete Example: Window Width Tracker

Here is a practical example that uses setup, cleanup, and dependencies:

```jsx
import { useState, useEffect } from 'react';

function WindowWidth() {
  const [width, setWidth] = useState(window.innerWidth);

  useEffect(() => {
    function handleResize() {
      setWidth(window.innerWidth);
    }

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <div>
      <p>Window width: {width}px</p>
      <p>
        {width > 768 ? 'Desktop view' : 'Mobile view'}
      </p>
    </div>
  );
}

export default WindowWidth;
```

**What you will see:**

```
Window width: 1024px
Desktop view
```

When you resize the browser window, the width updates in real time.

### How It Works

- **Setup**: We add a "resize" event listener to the window. This listener updates our state whenever the window size changes.
- **Cleanup**: We remove the event listener. This prevents memory leaks if the component disappears.
- **Empty dependency array**: We only need to set up the listener once. The listener itself will keep working until we remove it.

---

## Quick Summary

| Concept | What It Does |
|---|---|
| Side effect | Anything outside of rendering (fetching data, timers, changing the title) |
| `useEffect(() => {})` | Runs after every render |
| `useEffect(() => {}, [])` | Runs once when the component first appears |
| `useEffect(() => {}, [x])` | Runs when the value `x` changes |
| Cleanup function | Returned from the effect; runs before next effect and on unmount |
| `clearInterval` | Stops a timer created by `setInterval` |
| `removeEventListener` | Removes a listener added by `addEventListener` |

---

## Key Points to Remember

1. **useEffect runs after rendering.** React first updates the screen, then runs your effects. Your effects never block the screen from updating.

2. **The dependency array controls when the effect runs.** No array means every render. Empty array means once. Array with values means when those values change.

3. **Always clean up timers and listeners.** Return a cleanup function from your effect to stop timers (`clearInterval`), remove listeners (`removeEventListener`), or cancel any ongoing work.

4. **Do not update state that is in your own dependency array.** This creates an infinite loop. If you see your app freeze or your browser slow down, check for this mistake.

5. **Use multiple effects for separate concerns.** It is better to have three small, focused effects than one large effect that does everything.

---

## Practice Questions

1. What is a side effect in React? Give three examples.

2. What is the difference between `useEffect(() => { ... })` with no second argument and `useEffect(() => { ... }, [])` with an empty array?

3. Why do we need a cleanup function? What happens if we forget to clean up a timer?

4. Look at this code: `useEffect(() => { setName(name + '!'); }, [name]);`. What will happen? Why?

5. Can you have multiple `useEffect` calls in one component? Is that a good practice or a bad practice?

---

## Exercises

### Exercise 1: Dynamic Page Title

Create a component with a text input. As the user types, the browser tab title should update to show what they typed. When the input is empty, the tab title should say "Untitled Page".

### Exercise 2: Countdown Timer

Create a countdown timer that:
- Starts at 10 seconds
- Counts down by 1 every second
- Shows "Time is up!" when it reaches 0 and stops the timer
- Has a "Reset" button that restarts the countdown from 10

Remember to clean up the interval properly.

### Exercise 3: Online Status

Create a component that:
- Tracks if the browser is online or offline
- Shows "You are online" (in green) or "You are offline" (in red)
- Uses `window.addEventListener('online', ...)` and `window.addEventListener('offline', ...)`
- Properly cleans up the event listeners

Hint: `navigator.onLine` gives you the initial online/offline status.

---

## What Is Next?

Now you know how to do things at the right time with `useEffect`. You can run code when a component appears, when values change, and clean up when a component disappears.

In the next chapter, we will use `useEffect` for one of its most important jobs: fetching data from the internet. You will learn what APIs are, how to ask them for data, and how to display that data in your React components. This is where your apps start feeling like real applications.
