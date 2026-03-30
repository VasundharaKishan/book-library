# Chapter 29: useReducer — Managing Complex State

---

## What You Will Learn

- When `useState` is not enough for managing state
- What a reducer is and how it works
- The three parts of useReducer: state, action, and the reducer function
- How `dispatch` works (sending messages to your reducer)
- How to build a counter with `useReducer` (and compare it to `useState`)
- How to build a to-do list with `useReducer`
- When to use `useReducer` vs `useState`

## Why This Chapter Matters

You have been using `useState` for all your state management so far. It works great for simple things like a counter, a text input, or a boolean toggle.

But what happens when your state gets more complex? Imagine a shopping cart. You need to add items, remove items, change quantities, apply discounts, and clear the cart. That is five different ways to update state, and they all work on the same data.

With `useState`, you end up with many setter functions and scattered update logic. It becomes hard to read and easy to make mistakes.

`useReducer` gives you a better way. It puts all your update logic in one place. It makes complex state changes predictable and organized.

Think of it this way. If `useState` is like a light switch (on or off), `useReducer` is like a remote control with many buttons. Each button does something different, but they all control the same TV.

---

## When useState Is Not Enough

Let us look at a problem. Imagine you are building a simple form that tracks a user's profile.

```jsx
function ProfileForm() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [age, setAge] = useState(0);
  const [isEditing, setIsEditing] = useState(false);
  const [error, setError] = useState('');

  function handleSave() {
    if (name === '') {
      setError('Name is required');
      return;
    }
    setIsEditing(false);
    setError('');
  }

  function handleReset() {
    setName('');
    setEmail('');
    setAge(0);
    setIsEditing(false);
    setError('');
  }

  // ... more code
}
```

Do you see the problem? We have five pieces of state. They are all related to the same thing (the profile form). When we reset, we have to call five setter functions. When we save, we update two pieces of state. It is easy to forget one.

This is where `useReducer` helps. It lets you manage all these related pieces of state together, in one place.

---

## What Is a Reducer?

A **reducer** is a function that takes two things:

1. The **current state** (what things look like right now)
2. An **action** (what the user wants to do)

It returns the **new state** (what things should look like after the action).

### The Cashier Analogy

Think of a reducer like a cashier at a restaurant.

```
You (the customer) say:       "I want to add a burger."
The cashier (the reducer):     Looks at your current order.
                               Adds a burger to it.
                               Gives you the updated order.

You say:                       "Remove the fries."
The cashier:                   Looks at your current order.
                               Removes the fries.
                               Gives you the updated order.

You say:                       "Clear everything."
The cashier:                   Gives you an empty order.
```

You do not reach behind the counter and change your order yourself. You tell the cashier what you want. The cashier handles the details.

In React:
- **You** are the component
- **The cashier** is the reducer function
- **What you say** is the action
- **The order** is the state

---

## The Three Parts of useReducer

Every `useReducer` setup has three parts. Let us learn each one.

### Part 1: State

This is your data. It can be a single value, or an object with many fields.

```jsx
// Simple state: just a number
const initialState = 0;

// Complex state: an object with multiple fields
const initialState = {
  name: '',
  email: '',
  age: 0,
  isEditing: false,
  error: ''
};
```

### Part 2: Actions

An **action** is a plain object that describes what happened. It has a `type` property that tells the reducer what to do.

```jsx
// "The user clicked the add button"
{ type: 'add' }

// "The user wants to set the name to 'Alice'"
{ type: 'set_name', value: 'Alice' }

// "The user clicked reset"
{ type: 'reset' }
```

Think of the `type` as a label. It is like a sticky note that says "do this thing."

The action can also carry extra data. In the example above, the `set_name` action carries a `value` of `'Alice'`. This extra data is often called the **payload** (the package of information the action carries with it).

### Part 3: The Reducer Function

The reducer function reads the action type and decides what the new state should be.

```jsx
function reducer(state, action) {
  switch (action.type) {
    case 'add':
      return state + 1;
    case 'subtract':
      return state - 1;
    case 'reset':
      return 0;
    default:
      return state;
  }
}
```

Here is what is happening:

- The function receives the current `state` and the `action`.
- It uses a `switch` statement to check `action.type`.
- For each type, it returns the new state.
- The `default` case returns the current state unchanged (in case of an unknown action).

**Important rule:** The reducer must return a **new** state value. It should never change (mutate) the existing state directly. This is the same rule you learned with `useState`.

### How They Work Together

Here is a picture of how the three parts connect:

```
                         +------------------+
  Component calls        |                  |
  dispatch({ type })  -->|  Reducer Function |
                         |                  |
  Current State -------->|  Reads action    |
                         |  Returns new     |
                         |  state           |
                         +--------+---------+
                                  |
                                  v
                           New State
                           (Component re-renders)
```

---

## Using useReducer: A Simple Counter

Let us start with the simplest possible example: a counter. We will build it with `useState` first, then rebuild it with `useReducer` so you can compare.

### Counter with useState

```jsx
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Add</button>
      <button onClick={() => setCount(count - 1)}>Subtract</button>
      <button onClick={() => setCount(0)}>Reset</button>
    </div>
  );
}

export default Counter;
```

This works fine. It is simple and clear.

### Counter with useReducer

Now let us build the same counter with `useReducer`.

```jsx
import { useReducer } from 'react';

// Step 1: Define the reducer function
function counterReducer(state, action) {
  switch (action.type) {
    case 'add':
      return state + 1;
    case 'subtract':
      return state - 1;
    case 'reset':
      return 0;
    default:
      return state;
  }
}

// Step 2: Use it in the component
function Counter() {
  const [count, dispatch] = useReducer(counterReducer, 0);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => dispatch({ type: 'add' })}>Add</button>
      <button onClick={() => dispatch({ type: 'subtract' })}>Subtract</button>
      <button onClick={() => dispatch({ type: 'reset' })}>Reset</button>
    </div>
  );
}

export default Counter;
```

**Expected output:** The same counter as before. Three buttons. Clicking "Add" increases the count by 1. Clicking "Subtract" decreases it by 1. Clicking "Reset" sets it back to 0.

### Line-by-Line Explanation

```jsx
import { useReducer } from 'react';
```
We import `useReducer` from React, just like we import `useState`.

```jsx
function counterReducer(state, action) {
```
We define the reducer function. It takes two parameters: the current `state` and the `action` that was dispatched.

```jsx
  switch (action.type) {
```
We use a `switch` statement to check what type of action was sent. A `switch` is like a series of `if/else` checks, but cleaner when you have many cases.

```jsx
    case 'add':
      return state + 1;
```
If the action type is `'add'`, return the current state plus 1.

```jsx
    case 'subtract':
      return state - 1;
```
If the action type is `'subtract'`, return the current state minus 1.

```jsx
    case 'reset':
      return 0;
```
If the action type is `'reset'`, return 0 (ignore the current state entirely).

```jsx
    default:
      return state;
```
If the action type is something we do not recognize, return the state unchanged.

```jsx
  const [count, dispatch] = useReducer(counterReducer, 0);
```
This is how we use `useReducer`. It takes two arguments:
1. The reducer function (`counterReducer`)
2. The initial state (`0`)

It gives us back two things:
1. `count` — the current state value
2. `dispatch` — a function to send actions to the reducer

```jsx
  <button onClick={() => dispatch({ type: 'add' })}>Add</button>
```
When the user clicks the button, we call `dispatch` with an action object. The action has a `type` of `'add'`. React will call our reducer with the current state and this action.

---

## What Is Dispatch?

**Dispatch** means "to send." When you call `dispatch`, you are sending a message to the reducer.

Think of it like sending a text message:

```
You send:     dispatch({ type: 'add' })
Message:      "Hey reducer, the user clicked Add."
Reducer:      "Got it. Current count is 3. Adding 1. New count is 4."
React:        Re-renders the component with count = 4.
```

You can also send extra information with the message:

```jsx
dispatch({ type: 'add_amount', amount: 5 });
```

The reducer can then read `action.amount`:

```jsx
case 'add_amount':
  return state + action.amount;
```

This is like telling the cashier: "Add 5 burgers" instead of just "Add a burger."

---

## A Real Example: To-Do List with useReducer

Now let us build something more practical. A to-do list where you can add tasks, mark them as done, and delete them.

This is where `useReducer` really shines. We have three different actions, all working on the same list of tasks.

```jsx
import { useReducer, useState } from 'react';

// The initial state: an empty list of todos
const initialTodos = [];

// The reducer: handles all the ways we can change our todos
function todoReducer(state, action) {
  switch (action.type) {
    case 'add':
      return [
        ...state,
        {
          id: Date.now(),
          text: action.text,
          done: false
        }
      ];

    case 'toggle':
      return state.map(todo => {
        if (todo.id === action.id) {
          return { ...todo, done: !todo.done };
        }
        return todo;
      });

    case 'delete':
      return state.filter(todo => todo.id !== action.id);

    default:
      return state;
  }
}

function TodoApp() {
  const [todos, dispatch] = useReducer(todoReducer, initialTodos);
  const [text, setText] = useState('');

  function handleAdd() {
    if (text.trim() === '') return;
    dispatch({ type: 'add', text: text });
    setText('');
  }

  return (
    <div>
      <h1>My To-Do List</h1>

      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Add a task..."
      />
      <button onClick={handleAdd}>Add</button>

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

      <p>{todos.filter(t => !t.done).length} tasks remaining</p>
    </div>
  );
}

export default TodoApp;
```

**Expected output:**

```
My To-Do List

[Add a task...    ] [Add]

- Buy groceries    [Done] [Delete]
- Walk the dog     [Done] [Delete]
- Read a book      [Done] [Delete]

3 tasks remaining
```

After clicking "Done" on "Walk the dog":

```
- Buy groceries        [Done] [Delete]
- ~~Walk the dog~~     [Undo] [Delete]
- Read a book          [Done] [Delete]

2 tasks remaining
```

### Line-by-Line Explanation of the Reducer

```jsx
case 'add':
  return [
    ...state,
    {
      id: Date.now(),
      text: action.text,
      done: false
    }
  ];
```
When we add a to-do, we create a new array. It has all the existing items (`...state`) plus a new item at the end. The new item has:
- `id`: A unique number (we use the current time in milliseconds)
- `text`: The text from the action (`action.text`)
- `done`: Starts as `false` (not completed yet)

```jsx
case 'toggle':
  return state.map(todo => {
    if (todo.id === action.id) {
      return { ...todo, done: !todo.done };
    }
    return todo;
  });
```
When we toggle a to-do, we go through every item. If we find the one with the matching `id`, we create a copy with `done` flipped. All other items stay the same.

```jsx
case 'delete':
  return state.filter(todo => todo.id !== action.id);
```
When we delete a to-do, we filter out the item with the matching `id`. This creates a new array without that item.

### Why This Is Better Than useState

If we used `useState`, our add, toggle, and delete logic would be spread across three different functions in the component. With `useReducer`, all the state update logic lives in one place: the reducer function.

This makes it easier to:
- **Find bugs**: All your logic is in one function
- **Add new features**: Just add a new case to the switch
- **Test**: You can test the reducer function separately from the component

---

## When to Use useReducer vs useState

Here is a simple rule:

| Situation | Use |
|---|---|
| One or two simple state values | `useState` |
| A boolean, string, or number | `useState` |
| Three or more related state values | `useReducer` |
| Multiple actions on the same data | `useReducer` |
| Complex update logic | `useReducer` |

### The Simple Rule

> If you have three or more pieces of state that are related to each other, consider using `useReducer`.

Here are some real-life examples:

**Use useState:**
- A counter (one number)
- A text input (one string)
- A show/hide toggle (one boolean)
- Dark mode on/off (one boolean)

**Use useReducer:**
- A to-do list (add, toggle, delete, filter)
- A shopping cart (add item, remove item, change quantity, apply coupon)
- A form with validation (set field, validate, submit, reset)
- A multi-step wizard (next step, previous step, set data, reset)

### You Can Always Start with useState

Here is some good news. You can always start with `useState`. If your component gets complex and you have too many setter functions, you can refactor to `useReducer` later. They are interchangeable.

Do not feel pressure to use `useReducer` everywhere. It is a tool for when things get complex. Use `useState` for simple things. That is perfectly fine.

---

## Quick Summary

A **reducer** is a function that takes the current state and an action, and returns the new state. It puts all your update logic in one place.

`useReducer` gives you two things: the current state and a `dispatch` function. You call `dispatch` with an action object to tell the reducer what to do.

An **action** is a simple object with a `type` property (and optionally extra data).

`useReducer` is most useful when you have multiple related pieces of state or several different ways to update the same state.

---

## Key Points to Remember

1. **A reducer takes state and an action, and returns new state.** That is its entire job.

2. **Actions are plain objects with a `type` property.** The type tells the reducer which update to perform.

3. **`dispatch` sends actions to the reducer.** Think of it as sending a message: "Hey, this happened."

4. **The reducer must return a new state value.** Never change (mutate) the existing state directly.

5. **Define the reducer function outside the component.** This keeps your component clean and makes the reducer easy to test.

6. **Use `useState` for simple state, `useReducer` for complex state.** A good rule of thumb: if you have three or more related state variables, consider `useReducer`.

7. **You can use `useState` and `useReducer` together.** In our to-do example, we used `useReducer` for the to-do list and `useState` for the input text. Use the right tool for each job.

---

## Practice Questions

1. What are the two arguments that a reducer function receives?

2. What does the `dispatch` function do?

3. Look at this reducer. What will the state be after dispatching `{ type: 'double' }`?

```jsx
function reducer(state, action) {
  switch (action.type) {
    case 'add':
      return state + 1;
    case 'double':
      return state * 2;
    case 'reset':
      return 0;
    default:
      return state;
  }
}

// Initial state is 5
const [count, dispatch] = useReducer(reducer, 5);
dispatch({ type: 'double' });
```

4. Why should you define the reducer function outside the component?

5. Name two situations where `useReducer` is a better choice than `useState`.

---

## Exercises

### Exercise 1: Add a "Set To" Feature

Take the counter example from this chapter. Add a new action type called `'set'` that sets the counter to a specific number. You will need to pass the number in the action.

Hint: The dispatch call would look like `dispatch({ type: 'set', value: 10 })`.

### Exercise 2: Add a "Clear Completed" Button

Take the to-do list example. Add a "Clear Completed" button that removes all to-do items where `done` is `true`.

Hint: Add a new case in the reducer that uses `.filter()` to keep only items where `done` is `false`.

### Exercise 3: Build a Simple Score Tracker

Build a game score tracker using `useReducer`. It should support these actions:
- `'score'`: Add points (the action carries a `points` value)
- `'penalty'`: Subtract points (the action carries a `points` value)
- `'reset'`: Reset the score to 0

The state should be an object: `{ score: 0, highScore: 0 }`. When the score goes above the high score, update the high score too.

---

## What Is Next?

You now know how to manage complex state with `useReducer`. But what happens when multiple components need to share that state?

Right now, if you want to share state between components, you have to pass it through props. Sometimes you need to pass props through five levels of components just to get data where it needs to go. This is called "prop drilling," and it is not fun.

In the next chapter, you will learn about **Context** — React's built-in way to share data with any component in your tree, without passing props through every level. Combined with `useReducer`, it gives you a powerful state management system built right into React.
