# Chapter 11: Conditional Rendering — Showing Different Things

## What You Will Learn

- What conditional rendering means
- How to use `if/else` outside JSX to pick what to show
- How to use the ternary operator `? :` inside JSX
- How to use `&&` to show something only when a condition is true
- How to show and hide components
- How to build a Login/Logout button
- How to display loading messages while waiting for data

## Why This Chapter Matters

Imagine a store with a sign on the door. When the store is open, the sign says "OPEN." When the store is closed, it says "CLOSED." The sign changes based on a **condition** (is the store open or not?).

```
+------------------+        +------------------+
|                  |        |                  |
|      OPEN        |        |     CLOSED       |
|                  |        |                  |
+------------------+        +------------------+
   Store is open               Store is closed
```

Your React components need to do the same thing. Sometimes you want to show one thing, and other times you want to show something else. A "Log In" button should appear when the user is not logged in. A "Log Out" button should appear when they are logged in. A loading message should appear while data is being fetched.

This is called **conditional rendering** — showing different things based on a condition. It is one of the most useful skills in React.

---

## What Is Conditional Rendering?

Let us break down the term:

- **Conditional** means "based on a condition." A condition is something that is either true or false. "Is it raining?" is a condition. The answer is either yes (true) or no (false).
- **Rendering** means "showing on the screen."

So **conditional rendering** means: showing different things on the screen based on whether something is true or false.

You use conditional rendering all the time in real life:

- **If** it is raining, **bring** an umbrella. **Otherwise**, leave it at home.
- **If** you have a ticket, **enter** the movie theater. **Otherwise**, buy a ticket first.
- **If** the battery is low, **show** a warning. **Otherwise**, show the battery percentage.

React gives you three main ways to do conditional rendering:

1. `if/else` statements (outside JSX)
2. The ternary operator `? :` (inside JSX)
3. The `&&` operator (inside JSX)

Let us learn each one.

---

## Method 1: Using if/else Outside JSX

The simplest way to conditionally render is to use a regular `if/else` statement before the `return`.

```jsx
function Greeting({ isLoggedIn }) {
  if (isLoggedIn) {
    return <h1>Welcome back!</h1>;
  } else {
    return <h1>Please log in.</h1>;
  }
}
```

### Expected Output

If `isLoggedIn` is `true`:

```
Welcome back!
```

If `isLoggedIn` is `false`:

```
Please log in.
```

### Line-by-Line Explanation

**Line 1:** `function Greeting({ isLoggedIn }) {`
The component receives a prop called `isLoggedIn`. This prop is a boolean — it is either `true` or `false`.

**Line 2:** `if (isLoggedIn) {`
We check the condition. If `isLoggedIn` is `true`, we go into this block.

**Line 3:** `return <h1>Welcome back!</h1>;`
If logged in, return a heading that says "Welcome back!" The `return` statement ends the function here. Nothing below this line runs.

**Line 4-5:** `} else {`
If `isLoggedIn` is `false`, we go into the `else` block.

**Line 5:** `return <h1>Please log in.</h1>;`
If not logged in, return a heading that says "Please log in."

### When to Use if/else

Use `if/else` when:
- The two options look very different (completely different layouts)
- You need to do some extra work before returning (like calculations)
- You want to return early from a component

---

## Method 2: The Ternary Operator Inside JSX

The **ternary operator** is a shortcut for `if/else` that you can use right inside your JSX. It has three parts (that is why it is called "ternary" — it means "three parts"):

```
condition ? showIfTrue : showIfFalse
```

Read it like this: "Is the condition true? **Then** show this. **Otherwise**, show that."

Here is an example:

```jsx
function Greeting({ isLoggedIn }) {
  return (
    <h1>
      {isLoggedIn ? 'Welcome back!' : 'Please log in.'}
    </h1>
  );
}
```

This does exactly the same thing as the `if/else` example above, but in fewer lines.

### How to Read the Ternary Operator

```
{isLoggedIn ? 'Welcome back!' : 'Please log in.'}
 ---------   ----------------   ----------------
     |              |                   |
 condition     if TRUE            if FALSE
               show this          show this
```

The `?` means "then" and the `:` means "otherwise."

### More Ternary Examples

**Showing different buttons:**

```jsx
function ActionButton({ isSaved }) {
  return (
    <button>
      {isSaved ? 'Edit' : 'Save'}
    </button>
  );
}
```

If `isSaved` is true, the button says "Edit." If false, it says "Save."

**Showing different components:**

```jsx
function StatusMessage({ isOnline }) {
  return (
    <div>
      {isOnline ? (
        <p style={{ color: 'green' }}>User is online</p>
      ) : (
        <p style={{ color: 'gray' }}>User is offline</p>
      )}
    </div>
  );
}
```

When the parts after `?` and `:` are longer, put them on separate lines and wrap them in parentheses `( )` for readability.

### When to Use the Ternary Operator

Use the ternary operator when:
- You want to choose between two options inside JSX
- Both options are short and simple
- You want compact, readable code

---

## Method 3: Using && for "Show Only If True"

Sometimes you do not have an "otherwise." You just want to show something when a condition is true, and show nothing when it is false.

The `&&` operator (called "and") is perfect for this:

```jsx
function Notification({ hasMessages }) {
  return (
    <div>
      <h1>Dashboard</h1>
      {hasMessages && <p>You have new messages!</p>}
    </div>
  );
}
```

### Expected Output

If `hasMessages` is `true`:

```
Dashboard
You have new messages!
```

If `hasMessages` is `false`:

```
Dashboard
```

The paragraph simply does not appear. No error, no blank space — it is just not there.

### How && Works

Think of `&&` like a bouncer at a club door:

```
{hasMessages && <p>You have new messages!</p>}

→ "Is hasMessages true? If yes, let the paragraph through.
   If no, show nothing."
```

The rule is simple:
- If the left side is **true**, show what is on the right side.
- If the left side is **false**, show nothing.

### More && Examples

**Show a badge only if there are items:**

```jsx
function CartIcon({ itemCount }) {
  return (
    <div>
      Cart
      {itemCount > 0 && <span> ({itemCount})</span>}
    </div>
  );
}
```

If `itemCount` is `3`, it shows: `Cart (3)`
If `itemCount` is `0`, it shows: `Cart`

**Show a warning only if needed:**

```jsx
function PasswordField({ password }) {
  return (
    <div>
      <input type="password" />
      {password.length < 8 && (
        <p style={{ color: 'red' }}>
          Password must be at least 8 characters
        </p>
      )}
    </div>
  );
}
```

### A Common Trap with &&

Be careful with numbers. Look at this code:

```jsx
// CAREFUL with this!
{count && <p>You have {count} items</p>}
```

If `count` is `0`, you might expect nothing to appear. But instead, React will show the number `0` on the screen. This is because `0` is a "falsy" value in JavaScript, and React renders `0` as text.

The fix is to use a comparison that gives a true boolean:

```jsx
// BETTER - use a comparison
{count > 0 && <p>You have {count} items</p>}
```

Now React checks "Is count greater than 0?" The answer is `true` or `false` — and `false` shows nothing.

### When to Use &&

Use `&&` when:
- You want to show something OR show nothing
- There is no "else" case
- The condition is simple

---

## Showing and Hiding Components

A very common pattern is showing and hiding parts of your app. Let us build a component that shows and hides a message when you click a button.

```jsx
import { useState } from 'react';

function ToggleDetails() {
  const [showDetails, setShowDetails] = useState(false);

  function handleClick() {
    setShowDetails(!showDetails);
  }

  return (
    <div>
      <h2>Product</h2>
      <p>A wonderful widget.</p>
      <button onClick={handleClick}>
        {showDetails ? 'Hide Details' : 'Show Details'}
      </button>
      {showDetails && (
        <div>
          <p>Weight: 2kg</p>
          <p>Color: Blue</p>
          <p>Material: Aluminum</p>
        </div>
      )}
    </div>
  );
}
```

### Expected Output

When the page loads:

```
Product
A wonderful widget.
[ Show Details ]
```

After clicking "Show Details":

```
Product
A wonderful widget.
[ Hide Details ]
Weight: 2kg
Color: Blue
Material: Aluminum
```

After clicking "Hide Details":

```
Product
A wonderful widget.
[ Show Details ]
```

### How It Works

- `showDetails` starts as `false`.
- The button text uses a ternary: if `showDetails` is true, say "Hide Details." Otherwise, say "Show Details."
- The details section uses `&&`: only show the details div when `showDetails` is true.
- `!showDetails` flips the value. If it is `false`, it becomes `true`. If it is `true`, it becomes `false`. The `!` symbol means "not" or "the opposite."

---

## Login/Logout Button Example

Let us build a practical example: a button that switches between "Log In" and "Log Out."

```jsx
import { useState } from 'react';

function LoginControl() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  function handleLogin() {
    setIsLoggedIn(true);
  }

  function handleLogout() {
    setIsLoggedIn(false);
  }

  return (
    <div>
      {isLoggedIn ? (
        <div>
          <p>Welcome! You are logged in.</p>
          <button onClick={handleLogout}>Log Out</button>
        </div>
      ) : (
        <div>
          <p>You are not logged in.</p>
          <button onClick={handleLogin}>Log In</button>
        </div>
      )}
    </div>
  );
}
```

### Expected Output

When the page loads (not logged in):

```
You are not logged in.
[ Log In ]
```

After clicking "Log In":

```
Welcome! You are logged in.
[ Log Out ]
```

After clicking "Log Out":

```
You are not logged in.
[ Log In ]
```

### What Is Happening

The ternary operator checks `isLoggedIn`:
- If `true`: show the welcome message and a Log Out button.
- If `false`: show the "not logged in" message and a Log In button.

The Log In button sets `isLoggedIn` to `true`. The Log Out button sets it to `false`. Each change triggers a re-render, and the correct content appears.

---

## Displaying Loading Messages

When your app waits for data (like loading information from the internet), you should show a loading message so the user knows something is happening.

```jsx
import { useState } from 'react';

function DataLoader() {
  const [isLoading, setIsLoading] = useState(false);
  const [data, setData] = useState(null);

  function handleLoad() {
    setIsLoading(true);

    // Simulate waiting 2 seconds for data to load
    setTimeout(() => {
      setData('Here is your data!');
      setIsLoading(false);
    }, 2000);
  }

  if (isLoading) {
    return <p>Loading... Please wait.</p>;
  }

  if (data) {
    return <p>{data}</p>;
  }

  return <button onClick={handleLoad}>Load Data</button>;
}
```

### Expected Output

When the page loads:

```
[ Load Data ]
```

After clicking (for 2 seconds):

```
Loading... Please wait.
```

After the data loads:

```
Here is your data!
```

### What Is Happening

This example uses multiple `if` statements with early returns:
1. First, check if we are loading. If yes, show "Loading..."
2. Then, check if we have data. If yes, show the data.
3. If neither, show the "Load Data" button.

The `setTimeout` function waits for a certain number of milliseconds before running the code inside it. 2000 milliseconds = 2 seconds. This simulates waiting for data from the internet. In real apps, you would use a real data-fetching tool, but the loading pattern is the same.

---

## Mini Project: Toggle Dark Mode / Light Mode Message

Let us build a fun component that switches between a "dark mode" and "light mode" message, changing the background and text colors.

```jsx
import { useState } from 'react';

function ThemeToggle() {
  const [isDark, setIsDark] = useState(false);

  function handleToggle() {
    setIsDark(!isDark);
  }

  const style = {
    backgroundColor: isDark ? '#333333' : '#ffffff',
    color: isDark ? '#ffffff' : '#333333',
    padding: '20px',
    textAlign: 'center',
    minHeight: '150px',
  };

  return (
    <div style={style}>
      <h2>{isDark ? 'Dark Mode' : 'Light Mode'}</h2>
      <p>
        {isDark
          ? 'Easy on the eyes at night.'
          : 'Bright and clear for daytime.'}
      </p>
      <button onClick={handleToggle}>
        Switch to {isDark ? 'Light' : 'Dark'} Mode
      </button>
    </div>
  );
}

export default ThemeToggle;
```

### Expected Output

When the page loads (light mode):

```
+-------------------------------------------+
|                                           |
|           Light Mode                      |
|   Bright and clear for daytime.           |
|                                           |
|     [ Switch to Dark Mode ]               |
|                                           |
+-------------------------------------------+
  (white background, dark text)
```

After clicking the button (dark mode):

```
+-------------------------------------------+
|///////////////////////////////////////////|
|///////////////////////////////////////////|
|///////////  Dark Mode  ///////////////////|
|///  Easy on the eyes at night.  //////////|
|///////////////////////////////////////////|
|/////  [ Switch to Light Mode ]  //////////|
|///////////////////////////////////////////|
+-------------------------------------------+
  (dark background, white text)
```

### Line-by-Line Explanation

**Line 4:** `const [isDark, setIsDark] = useState(false);`
We start in light mode (`false` means "not dark").

**Line 6-8:** `function handleToggle() { setIsDark(!isDark); }`
Flip between dark and light. `!isDark` gives us the opposite value.

**Line 10-16:** The `style` object.
We create a style object with different colors depending on `isDark`:
- `backgroundColor`: dark gray for dark mode, white for light mode
- `color`: white text for dark mode, dark text for light mode
- Other properties control spacing and size

**Line 20:** `<h2>{isDark ? 'Dark Mode' : 'Light Mode'}</h2>`
Show the current mode name.

**Line 22-25:** The description text changes based on the mode.

**Line 27:** `Switch to {isDark ? 'Light' : 'Dark'} Mode`
The button text tells you what mode you will switch TO, not what mode you are currently in.

---

## Quick Summary

- **Conditional rendering** means showing different things based on a condition.
- Use **`if/else`** outside the return when the two options are very different.
- Use the **ternary operator `? :`** inside JSX when you need to choose between two things.
- Use **`&&`** inside JSX when you want to show something or nothing.
- Be careful with `&&` and the number `0` — use `count > 0 &&` instead of `count &&`.
- These three methods are the building blocks for making your app respond to different situations.

---

## Key Points to Remember

1. The ternary operator has three parts: `condition ? ifTrue : ifFalse`
2. The `&&` operator shows the right side only if the left side is true.
3. You can use `if/else` with multiple `return` statements — whichever `return` runs first wins.
4. The `!` symbol flips a boolean: `!true` is `false`, `!false` is `true`.
5. Always show loading messages when your app is waiting for something.
6. Conditional rendering is just a fancy way of saying "show different things depending on the situation."

---

## Practice Questions

1. What does "conditional rendering" mean in simple words?

2. What is the difference between the ternary operator and the `&&` operator? When would you use each one?

3. What will this code display if `age` is `20`?
   ```jsx
   <p>{age >= 18 ? 'Adult' : 'Minor'}</p>
   ```

4. What will this code display if `hasNotification` is `false`?
   ```jsx
   {hasNotification && <p>You have a notification!</p>}
   ```

5. Why should you write `count > 0 && <p>Items</p>` instead of `count && <p>Items</p>`?

---

## Practice Exercises

### Exercise 1: Weather Message

Build a component called `WeatherMessage` that:
- Has a state variable `isRaining` that starts as `false`
- Shows "Bring an umbrella!" when `isRaining` is true
- Shows "Enjoy the sunshine!" when `isRaining` is false
- Has a button to toggle between the two states

### Exercise 2: Age Checker

Build a component called `AgeChecker` that:
- Has an input field where the user types their age
- Below the input, shows "You can vote!" if the age is 18 or more
- Shows "You are too young to vote." if the age is less than 18
- Shows nothing if the input is empty

Hint: Use `onChange` to capture the input and `parseInt()` to convert the text to a number.

### Exercise 3: Password Strength

Build a component called `PasswordChecker` that:
- Has an input field for a password
- Shows "Weak" (in red) if the password is less than 6 characters
- Shows "Medium" (in orange) if the password is 6-9 characters
- Shows "Strong" (in green) if the password is 10 or more characters

Hint: Use `if/else` to check `password.length` and set a message and color.

---

## What Is Next?

You can now show different things based on conditions. But what about showing many similar things? What if you have a list of 10 products and want to show them all? You would not write 10 separate components by hand. In the next chapter, **Chapter 12: Lists and Keys**, you will learn how to take a list of data and turn it into a list of components — automatically.
