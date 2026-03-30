# Chapter 14: useState In Depth

---

## What You Will Learn

- A quick recap of how useState works
- How to use state with different types of data: strings, numbers, booleans, arrays, and objects
- How to update arrays in state correctly (adding, removing, and filtering items)
- How to update objects in state correctly using the spread operator
- How to use multiple useState calls in one component
- What the updater function form is and why it matters
- Common mistakes beginners make with state
- How to build a to-do list application

## Why This Chapter Matters

You have been using `useState` since Chapter 9. You know how to create a piece of state and update it. But so far, you have mostly used it with simple values like strings and numbers.

Real applications need more. A to-do list is an array. A user profile is an object. A shopping cart is an array of objects. To build real things, you need to know how to work with these more complex types of state.

This chapter will also help you avoid bugs that trip up many beginners. Some of these bugs are sneaky. Your code might look correct but behave in unexpected ways. By the end of this chapter, you will understand why, and you will know how to avoid these problems.

---

## Quick Recap: How useState Works

Let us quickly review what you already know.

```jsx
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Add 1</button>
    </div>
  );
}
```

Here is what is happening:

1. `useState(0)` creates a state variable with an initial value of `0`.
2. It gives us two things: `count` (the current value) and `setCount` (a function to update it).
3. When we call `setCount(count + 1)`, React updates the state and re-renders the component.
4. On re-render, `count` has the new value.

That is the foundation. Now let us build on it.

---

## State with Different Data Types

State can hold any type of data. Let us look at examples of each type.

### String State

You have seen this many times. Perfect for text inputs.

```jsx
const [name, setName] = useState('');
const [greeting, setGreeting] = useState('Hello, world!');
```

### Number State

Great for counters, scores, quantities, and prices.

```jsx
const [score, setScore] = useState(0);
const [temperature, setTemperature] = useState(72);
```

### Boolean State

Perfect for on/off, show/hide, yes/no situations.

```jsx
const [isVisible, setIsVisible] = useState(false);
const [isDarkMode, setIsDarkMode] = useState(true);
```

To toggle a boolean (flip it from true to false or false to true):

```jsx
<button onClick={() => setIsDarkMode(!isDarkMode)}>
  Toggle Dark Mode
</button>
```

The `!` operator flips the value. If `isDarkMode` is `true`, `!isDarkMode` is `false`, and vice versa.

### Array State

For lists of items: to-do lists, shopping carts, search results.

```jsx
const [fruits, setFruits] = useState(['Apple', 'Banana', 'Cherry']);
```

### Object State

For grouped related data: a user profile, a form, settings.

```jsx
const [user, setUser] = useState({
  name: 'Sara',
  age: 28,
  city: 'New York',
});
```

---

## Updating Arrays in State

This is where things get interesting and where beginners often make mistakes. There is one very important rule:

**Never change (mutate) state directly. Always create a new array.**

Think of it like this: your state array is a signed document. You should never erase and rewrite parts of the signed document. Instead, you should make a photocopy, make your changes on the copy, and then replace the original with the new copy.

Why? Because React needs to know that something changed. When you create a new array, React can compare the old one and the new one and say, "These are different. I need to re-render." If you just change the old array, React does not notice the change.

### Adding an Item to an Array

```jsx
import { useState } from 'react';

function FruitList() {
  const [fruits, setFruits] = useState(['Apple', 'Banana']);
  const [newFruit, setNewFruit] = useState('');

  function addFruit() {
    if (newFruit.trim() === '') return;
    setFruits([...fruits, newFruit]);
    setNewFruit('');
  }

  return (
    <div>
      <input
        type="text"
        value={newFruit}
        onChange={(event) => setNewFruit(event.target.value)}
        placeholder="Enter a fruit"
      />
      <button onClick={addFruit}>Add Fruit</button>

      <ul>
        {fruits.map((fruit, index) => (
          <li key={index}>{fruit}</li>
        ))}
      </ul>
    </div>
  );
}

export default FruitList;
```

**What you will see after adding "Cherry":**

```
[Cherry____]  [Add Fruit]

- Apple
- Banana
- Cherry
```

### How Adding Works

```jsx
setFruits([...fruits, newFruit]);
```

This creates a **new array**. Let us break it down:

- `[...]` — We are creating a new array.
- `...fruits` — The spread operator copies all the items from the old `fruits` array into the new one.
- `newFruit` — We add the new fruit at the end.

So if `fruits` is `['Apple', 'Banana']` and `newFruit` is `'Cherry'`, the result is `['Apple', 'Banana', 'Cherry']`.

**Wrong way (do not do this):**

```jsx
// DO NOT DO THIS
fruits.push(newFruit);
setFruits(fruits);
```

This modifies the original array with `push` and then passes the same array to `setFruits`. React sees the same array reference and might not re-render. Always create a new array.

### Removing an Item from an Array

To remove an item, we use `filter`. The `filter` method creates a new array that only includes items that pass a test.

```jsx
import { useState } from 'react';

function FruitList() {
  const [fruits, setFruits] = useState(['Apple', 'Banana', 'Cherry', 'Date']);

  function removeFruit(indexToRemove) {
    setFruits(fruits.filter((fruit, index) => index !== indexToRemove));
  }

  return (
    <ul>
      {fruits.map((fruit, index) => (
        <li key={index}>
          {fruit}
          <button onClick={() => removeFruit(index)}> Remove</button>
        </li>
      ))}
    </ul>
  );
}

export default FruitList;
```

**What you will see:**

```
- Apple [Remove]
- Banana [Remove]
- Cherry [Remove]
- Date [Remove]
```

After clicking Remove next to "Cherry":

```
- Apple [Remove]
- Banana [Remove]
- Date [Remove]
```

### How Removing Works

```jsx
fruits.filter((fruit, index) => index !== indexToRemove)
```

`filter` goes through each item in the array. For each item, it asks: "Is this item's index different from the one we want to remove?" If yes, keep it. If no, leave it out.

So if we want to remove index 2 (Cherry):
- Index 0 (Apple): `0 !== 2` is true. Keep it.
- Index 1 (Banana): `1 !== 2` is true. Keep it.
- Index 2 (Cherry): `2 !== 2` is false. Remove it.
- Index 3 (Date): `3 !== 2` is true. Keep it.

Result: `['Apple', 'Banana', 'Date']`. A new array without Cherry.

### Updating an Item in an Array

To change one item in an array, we use `map`. The `map` method creates a new array where each item is transformed.

```jsx
function toggleFruit(indexToToggle) {
  setFruits(
    fruits.map((fruit, index) => {
      if (index === indexToToggle) {
        return fruit.toUpperCase();
      }
      return fruit;
    })
  );
}
```

This finds the item at the given index and converts it to uppercase. All other items stay the same.

---

## Updating Objects in State

Just like arrays, you should **never change an object directly**. Always create a new object.

The spread operator (`...`) is your best friend here.

### The Spread Operator with Objects — A Simple Analogy

Imagine you have a form filled out with your personal information:

```
Name: Sara
Age: 28
City: New York
```

Now you move to a new city. You do not erase "New York" and write "Boston" on the same form. Instead, you:

1. Make a photocopy of the form (everything stays the same).
2. On the copy, cross out "New York" and write "Boston."
3. Throw away the old form and keep the new one.

That is exactly what the spread operator does.

```jsx
import { useState } from 'react';

function UserProfile() {
  const [user, setUser] = useState({
    name: 'Sara',
    age: 28,
    city: 'New York',
  });

  function updateCity() {
    setUser({
      ...user,
      city: 'Boston',
    });
  }

  return (
    <div>
      <p>Name: {user.name}</p>
      <p>Age: {user.age}</p>
      <p>City: {user.city}</p>
      <button onClick={updateCity}>Move to Boston</button>
    </div>
  );
}

export default UserProfile;
```

**Before clicking the button:**

```
Name: Sara
Age: 28
City: New York
[Move to Boston]
```

**After clicking the button:**

```
Name: Sara
Age: 28
City: Boston
[Move to Boston]
```

### How It Works

```jsx
setUser({
  ...user,       // copy everything: name, age, city
  city: 'Boston', // then override city with the new value
});
```

The spread operator copies all properties from the `user` object. Then `city: 'Boston'` overrides the `city` property. The result is a brand new object with the updated city.

**Wrong way (do not do this):**

```jsx
// DO NOT DO THIS
user.city = 'Boston';
setUser(user);
```

This changes the original object directly (mutates it) and passes the same object reference. React might not notice the change.

---

## Multiple useState Calls in One Component

You can use `useState` as many times as you want in a single component. Each call creates a separate, independent piece of state.

```jsx
import { useState } from 'react';

function PlayerCard() {
  const [name, setName] = useState('Hero');
  const [health, setHealth] = useState(100);
  const [level, setLevel] = useState(1);
  const [isAlive, setIsAlive] = useState(true);

  function takeDamage() {
    const newHealth = health - 20;
    if (newHealth <= 0) {
      setHealth(0);
      setIsAlive(false);
    } else {
      setHealth(newHealth);
    }
  }

  function heal() {
    if (isAlive) {
      setHealth(health + 10);
    }
  }

  function levelUp() {
    if (isAlive) {
      setLevel(level + 1);
    }
  }

  return (
    <div>
      <h2>{name}</h2>
      <p>Health: {health}</p>
      <p>Level: {level}</p>
      <p>Status: {isAlive ? 'Alive' : 'Defeated'}</p>

      <button onClick={takeDamage}>Take Damage</button>
      <button onClick={heal}>Heal</button>
      <button onClick={levelUp}>Level Up</button>
    </div>
  );
}

export default PlayerCard;
```

Each piece of state is independent. Changing `health` does not affect `level`. Changing `level` does not affect `name`. They are like separate drawers in a dresser. Opening one drawer does not change what is in the other drawers.

### When to Use One Object vs. Multiple useState Calls

**Use multiple `useState` calls** when the pieces of state are independent. Name, health, and level do not depend on each other.

**Use one state object** when the pieces of state are related and change together. A form where all fields belong to the same form is a good example. We saw this in the previous chapter.

There is no strict rule. Use whatever feels clearer and easier to manage for your situation.

---

## The Updater Function Form

This is an important concept that catches many beginners off guard. Let us look at a problem first.

### The Problem

What happens if you call `setCount` multiple times in the same function?

```jsx
function handleClick() {
  setCount(count + 1);
  setCount(count + 1);
  setCount(count + 1);
}
```

You might expect the count to go up by 3. But it only goes up by 1. Why?

Because all three lines use the **same value** of `count`. When `handleClick` runs, `count` might be `0`. All three lines read `count` as `0`:

```
setCount(0 + 1);  // sets count to 1
setCount(0 + 1);  // sets count to 1 again
setCount(0 + 1);  // sets count to 1 yet again
```

React batches these updates together. The final result is `count = 1`, not `count = 3`.

### The Solution: The Updater Function

Instead of passing a **value** to `setCount`, you can pass a **function**. This function receives the **previous state** as its argument and returns the new state.

```jsx
function handleClick() {
  setCount(prev => prev + 1);
  setCount(prev => prev + 1);
  setCount(prev => prev + 1);
}
```

Now each call uses the result of the previous one:

```
setCount(prev => prev + 1);  // prev is 0, returns 1
setCount(prev => prev + 1);  // prev is 1, returns 2
setCount(prev => prev + 1);  // prev is 2, returns 3
```

The count goes up by 3. Each call gets the most up-to-date value.

### When to Use the Updater Function

Use the updater function form when your **new state depends on the old state**. Here are good times to use it:

```jsx
// Incrementing a counter
setCount(prev => prev + 1);

// Toggling a boolean
setIsOpen(prev => !prev);

// Adding to an array
setItems(prev => [...prev, newItem]);

// Removing from an array
setItems(prev => prev.filter(item => item.id !== idToRemove));
```

The word `prev` is just a name. You can call it anything: `previous`, `old`, `current`, or even just `c`. The name `prev` is a common convention because it clearly says "the previous value."

### A Complete Example

```jsx
import { useState } from 'react';

function BetterCounter() {
  const [count, setCount] = useState(0);

  function addThree() {
    setCount(prev => prev + 1);
    setCount(prev => prev + 1);
    setCount(prev => prev + 1);
  }

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(prev => prev + 1)}>Add 1</button>
      <button onClick={addThree}>Add 3</button>
      <button onClick={() => setCount(0)}>Reset</button>
    </div>
  );
}

export default BetterCounter;
```

**What you will see after clicking "Add 3":**

```
Count: 3
[Add 1]  [Add 3]  [Reset]
```

---

## Common Mistakes with State

Let us look at the mistakes beginners make most often, so you can avoid them.

### Mistake 1: Mutating State Directly

```jsx
// WRONG - Mutating the array
const [items, setItems] = useState(['A', 'B', 'C']);

function removeFirst() {
  items.shift();      // This changes the original array!
  setItems(items);    // React may not re-render!
}
```

```jsx
// CORRECT - Creating a new array
function removeFirst() {
  setItems(items.slice(1));  // slice creates a new array
}
```

**Methods that mutate arrays (do not use these with state):**
- `push()` — adds to the end
- `pop()` — removes from the end
- `shift()` — removes from the beginning
- `unshift()` — adds to the beginning
- `splice()` — adds or removes in the middle
- `sort()` — sorts in place
- `reverse()` — reverses in place

**Methods that create new arrays (safe to use with state):**
- `map()` — transforms each item
- `filter()` — keeps items that pass a test
- `slice()` — copies a portion
- `concat()` — joins arrays together
- `[...array]` — spread into a new array

### Mistake 2: Using State Right After Setting It

```jsx
// WRONG - count is still the old value here
function handleClick() {
  setCount(count + 1);
  console.log(count);  // Still shows the old value!
}
```

State does not update instantly. When you call `setCount`, React schedules an update. The new value is available on the **next render**, not immediately on the next line.

If you need to use the new value, calculate it first:

```jsx
// CORRECT
function handleClick() {
  const newCount = count + 1;
  setCount(newCount);
  console.log(newCount);  // Shows the new value
}
```

### Mistake 3: Forgetting to Spread When Updating Objects

```jsx
// WRONG - Loses name and age!
setUser({ city: 'Boston' });
```

This replaces the entire object with just `{ city: 'Boston' }`. The name and age are gone.

```jsx
// CORRECT - Keeps name and age, updates city
setUser({ ...user, city: 'Boston' });
```

Always spread the existing object first, then override the property you want to change.

---

## Mini Project: To-Do List

Let us put everything together and build a to-do list app. You can add tasks, mark them as complete, and delete them.

```jsx
import { useState } from 'react';

function TodoApp() {
  const [todos, setTodos] = useState([]);
  const [inputText, setInputText] = useState('');

  function addTodo(event) {
    event.preventDefault();

    if (inputText.trim() === '') return;

    const newTodo = {
      id: Date.now(),
      text: inputText,
      completed: false,
    };

    setTodos(prev => [...prev, newTodo]);
    setInputText('');
  }

  function toggleTodo(idToToggle) {
    setTodos(prev =>
      prev.map(todo => {
        if (todo.id === idToToggle) {
          return { ...todo, completed: !todo.completed };
        }
        return todo;
      })
    );
  }

  function deleteTodo(idToDelete) {
    setTodos(prev => prev.filter(todo => todo.id !== idToDelete));
  }

  return (
    <div>
      <h2>My To-Do List</h2>

      <form onSubmit={addTodo}>
        <input
          type="text"
          value={inputText}
          onChange={(event) => setInputText(event.target.value)}
          placeholder="What do you need to do?"
        />
        <button type="submit">Add</button>
      </form>

      {todos.length === 0 && <p>No tasks yet. Add one above!</p>}

      <ul>
        {todos.map(todo => (
          <li key={todo.id}>
            <span
              onClick={() => toggleTodo(todo.id)}
              style={{
                textDecoration: todo.completed ? 'line-through' : 'none',
                cursor: 'pointer',
              }}
            >
              {todo.completed ? '✓ ' : '○ '} {todo.text}
            </span>
            <button onClick={() => deleteTodo(todo.id)}> Delete</button>
          </li>
        ))}
      </ul>

      <p>
        Total: {todos.length} | Done: {todos.filter(t => t.completed).length}
      </p>
    </div>
  );
}

export default TodoApp;
```

**What you will see after adding some tasks and completing one:**

```
My To-Do List

[Buy groceries______]  [Add]

✓  Buy milk (with line-through) [Delete]
○  Clean the house [Delete]
○  Call mom [Delete]

Total: 3 | Done: 1
```

### How the To-Do List Works

**Adding a task:**

```jsx
const newTodo = {
  id: Date.now(),
  text: inputText,
  completed: false,
};
setTodos(prev => [...prev, newTodo]);
```

We create a new object for the task. `Date.now()` gives us a unique number (the current time in milliseconds) to use as an ID. We spread the previous todos and add the new one at the end.

**Toggling a task (marking it complete or incomplete):**

```jsx
setTodos(prev =>
  prev.map(todo => {
    if (todo.id === idToToggle) {
      return { ...todo, completed: !todo.completed };
    }
    return todo;
  })
);
```

We use `map` to go through every todo. When we find the one we want to toggle, we create a new object with the spread operator and flip the `completed` value. All other todos are returned unchanged.

**Deleting a task:**

```jsx
setTodos(prev => prev.filter(todo => todo.id !== idToDelete));
```

We use `filter` to create a new array that excludes the todo with the matching ID.

Notice that all three operations use the updater function form (`prev => ...`). This is a good habit. It ensures we always work with the most current state.

---

## Quick Summary

| Concept | What to Remember |
|---|---|
| State types | State can hold strings, numbers, booleans, arrays, and objects |
| Adding to an array | `setItems(prev => [...prev, newItem])` |
| Removing from an array | `setItems(prev => prev.filter(...))` |
| Updating an item in an array | `setItems(prev => prev.map(...))` |
| Updating an object | `setObj(prev => ({ ...prev, key: newValue }))` |
| Multiple useState | Each call creates independent state |
| Updater function | `setState(prev => newValue)` for state that depends on old state |
| Never mutate | Always create new arrays and objects |

---

## Key Points to Remember

1. **Never mutate state directly.** Do not use `push`, `pop`, `shift`, `splice`, `sort`, or `reverse` on state arrays. Always create a new array with `map`, `filter`, `slice`, or the spread operator.

2. **Use the spread operator to update objects.** Copy everything first, then override what you want to change: `{ ...oldObject, key: newValue }`.

3. **State updates are not instant.** The new value is available on the next render, not on the next line of code.

4. **Use the updater function** (`prev => ...`) when your new state depends on the previous state. This avoids bugs with stale values.

5. **Use `Date.now()` or a counter for unique IDs.** Every item in a list needs a unique `key`, and using the array index is not ideal when items can be added or removed.

---

## Practice Questions

1. Why should you never use `push()` to add an item to a state array? What should you do instead?

2. What is the difference between `setCount(count + 1)` and `setCount(prev => prev + 1)`? When does the difference matter?

3. If your state is `{ name: 'Sara', age: 28 }` and you call `setUser({ age: 29 })`, what happens to the `name` property? How do you fix this?

4. When should you use multiple `useState` calls versus a single state object? Give an example of each.

5. What are three array methods that are safe to use with state and three that are not safe? Why?

---

## Exercises

### Exercise 1: Shopping List

Build a shopping list app where you can:
- Type an item name and click "Add" to add it to the list
- Click "Remove" next to an item to delete it
- Show the total number of items

### Exercise 2: Score Tracker

Build a score tracker for two players:
- Show each player's name and score (start at 0)
- Have "+1" and "-1" buttons for each player
- Have a "Reset" button that sets both scores back to 0
- Display who is winning or if it is a tie

### Exercise 3: Enhanced To-Do List

Extend the to-do list from this chapter:
- Add a "Clear Completed" button that removes all completed tasks at once
- Add a count showing "3 of 5 tasks completed"
- Add an "Edit" button next to each task that lets you change the task text

---

## What Is Next?

You now have a solid understanding of `useState`. You can manage strings, numbers, booleans, arrays, and objects. You know how to add, remove, and update items. You know about the updater function and common mistakes to avoid.

In the next chapter, we will learn about `useEffect`, React's other most important hook. While `useState` lets you remember things, `useEffect` lets you do things at the right time, like fetching data when a page loads, setting up timers, or changing the page title. It is the key to making your components interact with the outside world.
