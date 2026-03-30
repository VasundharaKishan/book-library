# Chapter 10: Events — Making Things Happen

## What You Will Learn

- What events are and why they matter
- How to use `onClick` to respond to button clicks
- How to write event handler functions
- Why we write `onClick={handleClick}` and NOT `onClick={handleClick()}`
- How to pass information with events
- How to use `onChange` for input fields
- How to use `onSubmit` for forms
- The most common events in React

## Why This Chapter Matters

In the last chapter, you learned how to give your components memory with state. But memory alone is not enough. You need a way to **trigger** changes. You need something to happen.

Think about your phone. It has lots of information stored inside it. But nothing happens until you **do** something — you tap the screen, you swipe, you type. These actions are called **events**.

Events are the bridge between the user and your app. Without events, your app would just sit there, doing nothing. Events are what make your app interactive and alive.

---

## What Are Events?

An **event** is something that happens. That is it. It is really that simple.

In everyday life, events happen all the time:
- You **knock** on a door (event: knock)
- The door **opens** (response to the event)

In a web app:
- A user **clicks** a button (event: click)
- The app **shows** a message (response to the event)

Here are some common events in web apps:

```
+------------------+------------------------------------+
| Event            | When It Happens                    |
+------------------+------------------------------------+
| Click            | User clicks on something           |
| Change           | User types in an input field       |
| Submit           | User submits a form                |
| Mouse Enter      | User moves the mouse over something|
| Key Down         | User presses a key on the keyboard |
+------------------+------------------------------------+
```

In React, we respond to events by attaching **event handlers** to our elements. An **event handler** is just a function that runs when the event happens.

---

## onClick — The Most Common Event

The most common event is the **click**. You already used it in the last chapter. Let us look at it more closely.

```jsx
function ClickExample() {
  function handleClick() {
    alert('You clicked the button!');
  }

  return (
    <button onClick={handleClick}>Click me</button>
  );
}
```

### Expected Output

When you click the button, a pop-up box appears that says: "You clicked the button!"

### Line-by-Line Explanation

**Line 2-4:** `function handleClick() { alert('You clicked the button!'); }`
We create a function called `handleClick`. This is the **event handler**. It contains the code that should run when the button is clicked. The `alert()` function shows a pop-up message in the browser.

**Line 7:** `<button onClick={handleClick}>Click me</button>`
We attach the `handleClick` function to the button using `onClick`. Notice:
- `onClick` starts with a lowercase `on` and then a capital `C` for `Click`. This style is called **camelCase** (like a camel's humps: small, big, small, big).
- We put the function name inside curly braces `{ }`.
- We write `handleClick` — just the name, no parentheses after it.

---

## Writing Event Handler Functions

An **event handler** is a function that runs when an event happens. You have already seen one: `handleClick`. There is a common pattern for naming them:

```
handle + EventName = handler function name

handleClick    → runs when something is clicked
handleChange   → runs when an input value changes
handleSubmit   → runs when a form is submitted
```

You can define event handlers in two common ways.

### Way 1: A Named Function (Before the Return)

```jsx
function Greeting() {
  function handleClick() {
    alert('Hello there!');
  }

  return <button onClick={handleClick}>Say Hello</button>;
}
```

### Way 2: An Arrow Function (Inline, Inside the JSX)

```jsx
function Greeting() {
  return (
    <button onClick={() => alert('Hello there!')}>
      Say Hello
    </button>
  );
}
```

Both ways work exactly the same. Way 1 is easier to read when the handler does many things. Way 2 is nice for short, simple actions.

The `() =>` is called an **arrow function**. It is a short way to write a function. Think of the arrow `=>` as saying "do this." So `() => alert('Hello!')` means "do this: show an alert that says Hello."

---

## Why We Write onClick={handleClick} and NOT onClick={handleClick()}

This is a very common mistake for beginners. Let us understand why it matters.

```jsx
// CORRECT - passes the function (React will call it later)
<button onClick={handleClick}>Click me</button>

// WRONG - calls the function immediately when the page loads!
<button onClick={handleClick()}>Click me</button>
```

See the difference? The second version has `()` after `handleClick`. Those parentheses tell JavaScript: "Run this function right now!"

Here is an analogy:

```
CORRECT: onClick={handleClick}
→ "Hey React, here is the function. Call it when someone clicks."
→ Like giving someone your phone number: "Call me when you need me."

WRONG: onClick={handleClick()}
→ "Run this function RIGHT NOW, even though nobody clicked anything."
→ Like calling someone before they even ask you to.
```

With the wrong version:
- The function runs immediately when the page loads.
- The button click does nothing.
- Your app might behave in unexpected ways.

**Remember:** Give React the function. Do not call the function yourself.

```
handleClick   → "Here is the function" (CORRECT)
handleClick() → "Run the function NOW" (WRONG)
```

### When You NEED Parentheses

Sometimes you want to pass information to your handler function. In that case, you wrap it in an arrow function:

```jsx
// Passing information — this is correct!
<button onClick={() => handleClick('hello')}>Click me</button>
```

This creates a small function that says: "When clicked, call `handleClick` with the word 'hello'." The outer arrow function `() =>` waits for the click. The inner `handleClick('hello')` runs only when that click happens.

---

## Passing Information with Events

Sometimes you need your event handler to know some extra information. For example, which button was clicked?

```jsx
import { useState } from 'react';

function FruitPicker() {
  const [fruit, setFruit] = useState('none');

  function handlePick(fruitName) {
    setFruit(fruitName);
  }

  return (
    <div>
      <p>You picked: {fruit}</p>
      <button onClick={() => handlePick('Apple')}>Apple</button>
      <button onClick={() => handlePick('Banana')}>Banana</button>
      <button onClick={() => handlePick('Cherry')}>Cherry</button>
    </div>
  );
}
```

### Expected Output

When the page loads:

```
You picked: none
[ Apple ] [ Banana ] [ Cherry ]
```

After clicking "Banana":

```
You picked: Banana
[ Apple ] [ Banana ] [ Cherry ]
```

### How It Works

Each button uses an arrow function: `() => handlePick('Apple')`. When you click the Apple button:

1. The arrow function runs.
2. It calls `handlePick('Apple')`.
3. `handlePick` receives `'Apple'` as the `fruitName`.
4. `setFruit('Apple')` updates the state.
5. React re-renders the component.
6. The screen now shows "You picked: Apple."

---

## onChange for Input Fields

When a user types in an input field, the `onChange` event fires with every keystroke. This is how you capture what the user is typing.

```jsx
import { useState } from 'react';

function NameInput() {
  const [name, setName] = useState('');

  function handleChange(event) {
    setName(event.target.value);
  }

  return (
    <div>
      <input
        type="text"
        onChange={handleChange}
        placeholder="Type your name"
      />
      <p>Hello, {name}!</p>
    </div>
  );
}
```

### Expected Output

When the page loads:

```
[Type your name          ]
Hello, !
```

As you type "Sam":

```
[Sam                     ]
Hello, Sam!
```

### Line-by-Line Explanation

**Line 4:** `const [name, setName] = useState('');`
We create state called `name` with an empty string `''` as the starting value.

**Line 6:** `function handleChange(event) {`
Our handler function receives an **event** object. When React calls your event handler, it automatically passes this object. It contains information about what happened.

**Line 7:** `setName(event.target.value);`
This line has three parts:
- **`event`** — the event object that React gives us
- **`event.target`** — the element where the event happened (the input field)
- **`event.target.value`** — the current text inside the input field

So if the user types "Sam", `event.target.value` is `"Sam"`. We use that to update our state.

**Line 12-15:** The `<input>` element.
- `type="text"` — this is a text input field.
- `onChange={handleChange}` — every time the user types a character, call `handleChange`.
- `placeholder="Type your name"` — gray hint text that appears when the field is empty.

### The Event Object

When any event happens, React creates an **event object** and passes it to your handler function. This object has useful information. You can name it anything, but most people call it `event` or `e` for short.

```
event object
├── event.target       → the element that triggered the event
├── event.target.value → the current value (for inputs)
├── event.type         → what kind of event ("click", "change", etc.)
└── (many more properties)
```

You do not need to memorize all the properties. Just remember `event.target.value` for inputs — you will use it a lot.

---

## onSubmit for Forms

When a user fills out a form and clicks a submit button, the `onSubmit` event fires. Here is an example:

```jsx
import { useState } from 'react';

function SimpleForm() {
  const [name, setName] = useState('');
  const [submitted, setSubmitted] = useState(false);

  function handleSubmit(event) {
    event.preventDefault();
    setSubmitted(true);
  }

  function handleChange(event) {
    setName(event.target.value);
  }

  return (
    <div>
      {submitted ? (
        <p>Thanks, {name}! Form submitted.</p>
      ) : (
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            onChange={handleChange}
            placeholder="Enter your name"
          />
          <button type="submit">Submit</button>
        </form>
      )}
    </div>
  );
}
```

### Expected Output

When the page loads:

```
[Enter your name        ] [ Submit ]
```

After typing "Alex" and clicking Submit:

```
Thanks, Alex! Form submitted.
```

### Important: event.preventDefault()

**Line 8:** `event.preventDefault();`

This line is very important. By default, when you submit a form in a web browser, the browser refreshes the entire page. This is old behavior from the early days of the internet. In React, we do not want the page to refresh — we want React to handle everything.

`event.preventDefault()` means: "Stop the browser from doing what it normally does." It **prevents** the **default** behavior (page refresh).

Think of it like this: the browser says, "A form was submitted! I should refresh the page!" And `preventDefault` says, "No, do not do that. We will handle it ourselves."

You will almost always use `event.preventDefault()` inside `onSubmit` handlers.

---

## Common Events List

Here are the events you will use most often in React:

```
+--------------------+----------------------------+---------------------------+
| React Event        | When It Fires              | Common Use                |
+--------------------+----------------------------+---------------------------+
| onClick            | User clicks an element     | Buttons, links, cards     |
| onChange           | Input value changes        | Text inputs, checkboxes   |
| onSubmit           | Form is submitted          | Login forms, search bars  |
| onMouseEnter       | Mouse moves over element   | Showing tooltips          |
| onMouseLeave       | Mouse leaves element       | Hiding tooltips           |
| onKeyDown          | User presses a key         | Keyboard shortcuts        |
| onFocus            | Input field is selected    | Showing hints             |
| onBlur             | Input field loses focus    | Validation                |
+--------------------+----------------------------+---------------------------+
```

You do not need to memorize all of these. You will learn them as you need them. The three most important ones are:

1. **`onClick`** — for buttons and clickable things
2. **`onChange`** — for input fields
3. **`onSubmit`** — for forms

---

## Mini Examples

### Example 1: Button That Shows an Alert

```jsx
function AlertButton() {
  function handleClick() {
    alert('Button was clicked!');
  }

  return <button onClick={handleClick}>Show Alert</button>;
}
```

This is the simplest possible event example. Click the button, see a pop-up.

### Example 2: Button That Changes Text

```jsx
import { useState } from 'react';

function TextChanger() {
  const [message, setMessage] = useState('Hello!');

  function handleClick() {
    setMessage('You changed the text!');
  }

  return (
    <div>
      <p>{message}</p>
      <button onClick={handleClick}>Change Text</button>
    </div>
  );
}
```

**Before clicking:**

```
Hello!
[ Change Text ]
```

**After clicking:**

```
You changed the text!
[ Change Text ]
```

### Example 3: Input That Shows What You Type

```jsx
import { useState } from 'react';

function LiveTyping() {
  const [text, setText] = useState('');

  return (
    <div>
      <input
        type="text"
        onChange={(e) => setText(e.target.value)}
        placeholder="Type something..."
      />
      <p>You typed: {text}</p>
    </div>
  );
}
```

**As you type "React is fun":**

```
[React is fun            ]
You typed: React is fun
```

Notice that this example uses an **inline arrow function**: `(e) => setText(e.target.value)`. The `e` is short for `event`. This is a shorter way to write the handler when it only does one thing.

---

## Quick Summary

- **Events** are things that happen — clicks, typing, form submissions, mouse movements.
- You respond to events by writing **event handler** functions.
- Use `onClick` for button clicks, `onChange` for input fields, and `onSubmit` for forms.
- Write `onClick={handleClick}` (no parentheses). Do not write `onClick={handleClick()}`.
- Use arrow functions when you need to pass information: `onClick={() => handleClick('data')}`.
- Event handlers receive an **event object** with information about what happened.
- Use `event.target.value` to get the current value from an input field.
- Use `event.preventDefault()` in form submissions to stop the page from refreshing.

---

## Key Points to Remember

1. Event names in React use camelCase: `onClick`, `onChange`, `onSubmit` (not `onclick` or `on-click`).
2. Pass the function, do not call it: `onClick={handleClick}` not `onClick={handleClick()}`.
3. The event object is automatically passed to your handler function by React.
4. `event.target.value` gives you the text inside an input field.
5. Always use `event.preventDefault()` inside `onSubmit` handlers.
6. You can use named functions (defined before the return) or inline arrow functions — both work.

---

## Practice Questions

1. What is an event? Give two examples from everyday life and two from web apps.

2. What is wrong with this code?
   ```jsx
   <button onClick={handleClick()}>Click me</button>
   ```

3. How do you get the text that a user typed into an input field inside your event handler?

4. Why do we call `event.preventDefault()` in form submit handlers?

5. What is the difference between `onClick={handleClick}` and `onClick={() => handleClick('hello')}`?

---

## Practice Exercises

### Exercise 1: Compliment Button

Build a component called `ComplimentButton` that:
- Has a button that says "Get a Compliment"
- When clicked, shows a nice message below the button (like "You are amazing!")
- Use `useState` to store the message

### Exercise 2: Color Picker

Build a component called `ColorPicker` that:
- Shows the text "Current color: none"
- Has three buttons: "Red", "Green", "Blue"
- When you click a button, the text updates to show that color (for example, "Current color: Red")
- Hint: This is similar to the FruitPicker example

### Exercise 3: Character Counter

Build a component called `CharacterCounter` that:
- Has an input field where you can type text
- Below the input, shows "Characters: 0"
- As you type, the character count updates in real time
- Hint: A string has a `.length` property. If `text` is `"hello"`, then `text.length` is `5`.

---

## What Is Next?

You now know how to make things happen in your app. Users can click buttons, type in fields, and submit forms. But what if you want to show different things depending on a condition? What if you want to show a "Welcome" message to logged-in users and a "Please log in" message to everyone else? In the next chapter, **Chapter 11: Conditional Rendering**, you will learn how to show different content based on conditions — like a traffic light that shows different colors.
