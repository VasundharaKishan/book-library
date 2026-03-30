# Chapter 20: Building a Simple Project

## What You Will Learn

In this chapter, you will learn:

- How to plan a project before writing any code
- How to build a complete Todo App step by step
- How to add, complete, delete, and filter todo items
- How to show a count of remaining items
- How to structure your project files and folders
- How to add simple CSS styling
- What to do when you get stuck (debugging tips)

## Why This Chapter Matters

You have learned many individual skills throughout this book: components, state, props, events, lists, conditional rendering, and routing. Each one is like a single tool in a toolbox. You know what a hammer does. You know what a screwdriver does. You know what a saw does.

But knowing individual tools is not the same as building a house. To build something real, you need to use many tools together. You need a plan. You need to know which tool to use and when.

This chapter is where it all comes together. We will build a complete **Todo App** from scratch. Along the way, you will see how all the concepts you learned work together to create a real, working application.

A Todo App is the perfect first project because it covers the most important skills:

- Creating and organizing components
- Managing state with `useState`
- Handling user input and events
- Working with lists and keys
- Conditional rendering
- Passing data between components with props

Take your time with this chapter. Type the code yourself instead of copying it. When something does not work, try to figure out why before looking at the solution. That is how real learning happens.

---

## Planning Before Coding

Professional developers do not just start typing code. They plan first. Even for a small project, a few minutes of planning saves hours of confusion later.

Let us plan our Todo App by asking three questions:

### Question 1: What Should the App Do?

Our Todo App needs to:

1. Let the user type a new todo and add it to the list.
2. Show all the todos in a list.
3. Let the user mark a todo as complete (done).
4. Let the user delete a todo.
5. Let the user filter todos: show All, only Active (not done), or only Completed (done).
6. Show a count of how many items are left to do.

### Question 2: What Components Do We Need?

Let us break the app into pieces:

- **`App`** — The main component. Holds the state and puts everything together.
- **`TodoForm`** — The input field and "Add" button for creating new todos.
- **`TodoList`** — The list of todo items.
- **`TodoItem`** — A single todo item with a checkbox, text, and delete button.
- **`TodoFilter`** — The filter buttons (All, Active, Completed) and the item count.

### Question 3: What State Do We Need?

We need to track:

- **`todos`** — An array of todo objects. Each todo has an `id`, `text`, and `completed` status.
- **`filter`** — A string that says which filter is active: `"all"`, `"active"`, or `"completed"`.

Both pieces of state will live in the `App` component because multiple children need access to them.

### The Plan Summary

```
App (holds todos and filter state)
├── TodoForm (adds new todos)
├── TodoFilter (filter buttons + item count)
└── TodoList (displays filtered todos)
    └── TodoItem (single todo with checkbox and delete)
```

Now we know what to build. Let us start coding.

---

## Setting Up the Project

If you already have a React project from earlier chapters, you can use it. Otherwise, create a new one:

```
npx create-react-app todo-app
cd todo-app
npm start
```

### Folder Structure

Here is how we will organize our files:

```
src/
  components/
    TodoForm.jsx
    TodoList.jsx
    TodoItem.jsx
    TodoFilter.jsx
  App.jsx
  App.css
  index.js
```

We put our reusable components in a `components` folder, just like we learned in Chapter 17.

---

## Step 1: Building the TodoItem Component

We start with the smallest piece and work our way up. This is called **bottom-up development** — building the small parts first, then assembling them.

```jsx
// src/components/TodoItem.jsx

function TodoItem({ todo, onToggle, onDelete }) {
  const itemStyle = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '12px 16px',
    borderBottom: '1px solid #eee',
    backgroundColor: todo.completed ? '#f0f0f0' : 'white'
  };

  const textStyle = {
    textDecoration: todo.completed ? 'line-through' : 'none',
    color: todo.completed ? '#999' : '#333',
    flex: 1,
    marginLeft: '10px'
  };

  const deleteButtonStyle = {
    backgroundColor: '#e74c3c',
    color: 'white',
    border: 'none',
    padding: '4px 10px',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '12px'
  };

  return (
    <div style={itemStyle}>
      <input
        type="checkbox"
        checked={todo.completed}
        onChange={function () {
          onToggle(todo.id);
        }}
      />
      <span style={textStyle}>{todo.text}</span>
      <button
        style={deleteButtonStyle}
        onClick={function () {
          onDelete(todo.id);
        }}
      >
        Delete
      </button>
    </div>
  );
}

export default TodoItem;
```

Let us go through this line by line:

- **`function TodoItem({ todo, onToggle, onDelete })`** — This component receives three props: the todo object itself, a function to toggle its completed status, and a function to delete it.
- **`backgroundColor: todo.completed ? '#f0f0f0' : 'white'`** — If the todo is completed, the background is light gray. Otherwise, it is white. This gives visual feedback to the user.
- **`textDecoration: todo.completed ? 'line-through' : 'none'`** — If the todo is completed, the text has a line through it. This is the classic "crossed off" look for done items.
- **`<input type="checkbox" checked={todo.completed} ...>`** — A checkbox that is checked when the todo is completed.
- **`onChange={function () { onToggle(todo.id); }}`** — When the checkbox changes (checked or unchecked), it calls the `onToggle` function with the todo's ID. The parent will handle the actual state change.
- **`onClick={function () { onDelete(todo.id); }}`** — When the Delete button is clicked, it calls the `onDelete` function with the todo's ID.

---

## Step 2: Building the TodoList Component

This component receives an array of todos and renders a `TodoItem` for each one.

```jsx
// src/components/TodoList.jsx

import TodoItem from './TodoItem';

function TodoList({ todos, onToggle, onDelete }) {
  if (todos.length === 0) {
    return (
      <p style={{ textAlign: 'center', color: '#999', padding: '20px' }}>
        No todos to show. Add one above!
      </p>
    );
  }

  return (
    <div>
      {todos.map(function (todo) {
        return (
          <TodoItem
            key={todo.id}
            todo={todo}
            onToggle={onToggle}
            onDelete={onDelete}
          />
        );
      })}
    </div>
  );
}

export default TodoList;
```

Line by line:

- **`import TodoItem from './TodoItem';`** — We import the TodoItem component we just created.
- **`if (todos.length === 0)`** — If there are no todos to show, display a friendly message instead of an empty list.
- **`todos.map(function (todo) { ... })`** — This loops through the array of todos and creates one `TodoItem` for each.
- **`key={todo.id}`** — Each item in a list needs a unique key so React can track it properly.
- We pass `onToggle` and `onDelete` down to each `TodoItem`. These functions came from the parent (`App`) and are just being passed through.

---

## Step 3: Building the TodoForm Component

This component has an input field and a button for adding new todos.

```jsx
// src/components/TodoForm.jsx

import React from 'react';

function TodoForm({ onAdd }) {
  const [text, setText] = React.useState('');

  function handleSubmit(event) {
    event.preventDefault();

    const trimmedText = text.trim();

    if (trimmedText === '') {
      return;
    }

    onAdd(trimmedText);
    setText('');
  }

  const formStyle = {
    display: 'flex',
    gap: '10px',
    padding: '20px',
    borderBottom: '2px solid #eee'
  };

  const inputStyle = {
    flex: 1,
    padding: '10px',
    fontSize: '16px',
    border: '1px solid #ddd',
    borderRadius: '4px'
  };

  const buttonStyle = {
    padding: '10px 20px',
    fontSize: '16px',
    backgroundColor: '#3498db',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer'
  };

  return (
    <form onSubmit={handleSubmit} style={formStyle}>
      <input
        type="text"
        placeholder="What do you need to do?"
        value={text}
        onChange={function (event) {
          setText(event.target.value);
        }}
        style={inputStyle}
      />
      <button type="submit" style={buttonStyle}>
        Add
      </button>
    </form>
  );
}

export default TodoForm;
```

Line by line:

- **`const [text, setText] = React.useState('');`** — This component has its own local state for the text input. This state does NOT need to be lifted up because no other component needs to know what the user is typing before they press "Add."
- **`function handleSubmit(event)`** — This runs when the form is submitted (either by clicking "Add" or pressing Enter).
- **`event.preventDefault();`** — This stops the browser from reloading the page when the form is submitted. By default, forms cause a page reload. We prevent that.
- **`const trimmedText = text.trim();`** — `trim()` removes spaces from the beginning and end of the text. This prevents adding empty or whitespace-only todos.
- **`if (trimmedText === '') { return; }`** — If the text is empty after trimming, do nothing. Just stop here.
- **`onAdd(trimmedText);`** — Call the parent's function to add the new todo.
- **`setText('');`** — Clear the input field so the user can type the next todo.
- **`<form onSubmit={handleSubmit}>`** — We use a `<form>` element instead of just a button. This lets the user press Enter to add a todo, which is a nicer experience.
- **`placeholder="What do you need to do?"`** — This shows gray hint text in the input when it is empty.

---

## Step 4: Building the TodoFilter Component

This component shows filter buttons and the count of remaining items.

```jsx
// src/components/TodoFilter.jsx

function TodoFilter({ filter, onFilterChange, remainingCount }) {
  const containerStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '12px 16px',
    backgroundColor: '#f8f9fa',
    borderTop: '2px solid #eee'
  };

  function getButtonStyle(buttonFilter) {
    const isActive = filter === buttonFilter;

    return {
      padding: '6px 14px',
      border: isActive ? '2px solid #3498db' : '2px solid transparent',
      backgroundColor: isActive ? '#3498db' : 'transparent',
      color: isActive ? 'white' : '#555',
      borderRadius: '4px',
      cursor: 'pointer',
      fontSize: '14px'
    };
  }

  return (
    <div style={containerStyle}>
      <span style={{ color: '#888', fontSize: '14px' }}>
        {remainingCount} {remainingCount === 1 ? 'item' : 'items'} left
      </span>
      <div style={{ display: 'flex', gap: '5px' }}>
        <button
          style={getButtonStyle('all')}
          onClick={function () { onFilterChange('all'); }}
        >
          All
        </button>
        <button
          style={getButtonStyle('active')}
          onClick={function () { onFilterChange('active'); }}
        >
          Active
        </button>
        <button
          style={getButtonStyle('completed')}
          onClick={function () { onFilterChange('completed'); }}
        >
          Completed
        </button>
      </div>
    </div>
  );
}

export default TodoFilter;
```

Line by line:

- **`function TodoFilter({ filter, onFilterChange, remainingCount })`** — This component receives three props: the current filter value, a function to change the filter, and the number of remaining (not completed) items.
- **`function getButtonStyle(buttonFilter)`** — This function creates the style for each filter button. It checks if this button's filter matches the current active filter.
- **`const isActive = filter === buttonFilter;`** — This is `true` if this button represents the currently selected filter.
- **`border: isActive ? '2px solid #3498db' : '2px solid transparent'`** — The active button has a visible blue border. Other buttons have a transparent border (invisible, but it keeps the size consistent).
- **`{remainingCount} {remainingCount === 1 ? 'item' : 'items'} left`** — This shows "1 item left" or "3 items left." The ternary operator picks the right word: singular "item" when there is exactly 1, plural "items" otherwise.

---

## Step 5: Building the App Component

This is the main component that holds all the state and brings everything together.

```jsx
// src/App.jsx

import React from 'react';
import TodoForm from './components/TodoForm';
import TodoList from './components/TodoList';
import TodoFilter from './components/TodoFilter';

function App() {
  const [todos, setTodos] = React.useState([
    { id: 1, text: 'Learn React basics', completed: true },
    { id: 2, text: 'Build a todo app', completed: false },
    { id: 3, text: 'Practice every day', completed: false }
  ]);

  const [filter, setFilter] = React.useState('all');

  // --- Adding a todo ---
  function handleAddTodo(text) {
    const newTodo = {
      id: Date.now(),
      text: text,
      completed: false
    };

    setTodos(function (currentTodos) {
      return [...currentTodos, newTodo];
    });
  }

  // --- Toggling a todo (complete / not complete) ---
  function handleToggleTodo(id) {
    setTodos(function (currentTodos) {
      return currentTodos.map(function (todo) {
        if (todo.id === id) {
          return { ...todo, completed: !todo.completed };
        }
        return todo;
      });
    });
  }

  // --- Deleting a todo ---
  function handleDeleteTodo(id) {
    setTodos(function (currentTodos) {
      return currentTodos.filter(function (todo) {
        return todo.id !== id;
      });
    });
  }

  // --- Filtering ---
  let filteredTodos;

  if (filter === 'active') {
    filteredTodos = todos.filter(function (todo) {
      return !todo.completed;
    });
  } else if (filter === 'completed') {
    filteredTodos = todos.filter(function (todo) {
      return todo.completed;
    });
  } else {
    filteredTodos = todos;
  }

  // --- Counting remaining items ---
  const remainingCount = todos.filter(function (todo) {
    return !todo.completed;
  }).length;

  // --- Styles ---
  const appStyle = {
    maxWidth: '500px',
    margin: '40px auto',
    backgroundColor: 'white',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
    overflow: 'hidden'
  };

  const headerStyle = {
    textAlign: 'center',
    padding: '20px',
    backgroundColor: '#3498db',
    color: 'white',
    margin: 0
  };

  return (
    <div style={{ backgroundColor: '#ecf0f1', minHeight: '100vh', padding: '20px' }}>
      <div style={appStyle}>
        <h1 style={headerStyle}>My Todo List</h1>
        <TodoForm onAdd={handleAddTodo} />
        <TodoList
          todos={filteredTodos}
          onToggle={handleToggleTodo}
          onDelete={handleDeleteTodo}
        />
        <TodoFilter
          filter={filter}
          onFilterChange={setFilter}
          remainingCount={remainingCount}
        />
      </div>
    </div>
  );
}

export default App;
```

Let us go through the most important parts:

### The State

- **`const [todos, setTodos] = React.useState([...])`** — We start with three example todos. Each todo is an object with `id`, `text`, and `completed`. In a real app, this would probably start as an empty array.
- **`const [filter, setFilter] = React.useState('all')`** — The filter starts as "all," meaning all todos are shown.

### Adding a Todo

```jsx
function handleAddTodo(text) {
  const newTodo = {
    id: Date.now(),
    text: text,
    completed: false
  };

  setTodos(function (currentTodos) {
    return [...currentTodos, newTodo];
  });
}
```

- **`id: Date.now()`** — We use the current timestamp as a unique ID. `Date.now()` returns the number of milliseconds since January 1, 1970. Since this number is always increasing, each todo gets a unique ID. (In a real app, the server would usually provide IDs.)
- **`completed: false`** — New todos start as not completed.
- **`[...currentTodos, newTodo]`** — We create a new array that contains all existing todos plus the new one. The `...` (spread operator) copies all items from the current array.

### Toggling a Todo

```jsx
function handleToggleTodo(id) {
  setTodos(function (currentTodos) {
    return currentTodos.map(function (todo) {
      if (todo.id === id) {
        return { ...todo, completed: !todo.completed };
      }
      return todo;
    });
  });
}
```

- **`currentTodos.map(...)`** — We loop through all todos and create a new array.
- **`if (todo.id === id)`** — We find the todo that was toggled.
- **`{ ...todo, completed: !todo.completed }`** — We create a copy of that todo but flip its `completed` status. `!todo.completed` turns `true` into `false` and `false` into `true`. The `!` is the **not operator** — it flips a boolean value.
- **`return todo;`** — All other todos stay the same.

### Deleting a Todo

```jsx
function handleDeleteTodo(id) {
  setTodos(function (currentTodos) {
    return currentTodos.filter(function (todo) {
      return todo.id !== id;
    });
  });
}
```

- **`currentTodos.filter(...)`** — `filter` creates a new array that only includes items where the condition is `true`.
- **`todo.id !== id`** — Keep every todo whose ID does NOT match the one we want to delete. The deleted todo is simply left out of the new array.

### Filtering the List

```jsx
let filteredTodos;

if (filter === 'active') {
  filteredTodos = todos.filter(function (todo) {
    return !todo.completed;
  });
} else if (filter === 'completed') {
  filteredTodos = todos.filter(function (todo) {
    return todo.completed;
  });
} else {
  filteredTodos = todos;
}
```

- If the filter is "active," we only show todos that are NOT completed.
- If the filter is "completed," we only show todos that ARE completed.
- Otherwise (filter is "all"), we show all todos.
- We pass `filteredTodos` (not `todos`) to the `TodoList` component. The original `todos` array is never changed by filtering — we just create a new view of it.

### Counting Remaining Items

```jsx
const remainingCount = todos.filter(function (todo) {
  return !todo.completed;
}).length;
```

- We filter the todos to get only the ones that are not completed, then count them using `.length`.
- We always count from the full `todos` array, not from `filteredTodos`. This way, the count is always accurate regardless of which filter is active.

---

## Expected Output

When the app loads, you see:

1. A blue header that says "My Todo List."
2. An input field with the placeholder "What do you need to do?" and an "Add" button.
3. Three todo items:
   - "Learn React basics" — checked, with gray text and a line through it.
   - "Build a todo app" — unchecked, with normal black text.
   - "Practice every day" — unchecked, with normal black text.
4. A footer showing "2 items left" and three filter buttons: All, Active, Completed.

You can:
- Type "Read a book" in the input and click "Add" (or press Enter). A new todo appears at the bottom.
- Click the checkbox next to "Build a todo app." It becomes crossed out and gray.
- Click "Delete" next to any todo to remove it.
- Click "Active" to see only uncompleted todos.
- Click "Completed" to see only completed todos.
- Click "All" to see everything again.
- The item count updates automatically as you complete or delete todos.

---

## Adding Simple CSS

So far, we used inline styles (styles written directly in JavaScript). For a small project, inline styles work fine. But as your project grows, a separate CSS file is cleaner.

Here is a CSS file you can use instead of (or alongside) inline styles:

```css
/* src/App.css */

body {
  margin: 0;
  font-family: Arial, sans-serif;
  background-color: #ecf0f1;
}

.app-container {
  max-width: 500px;
  margin: 40px auto;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.app-header {
  text-align: center;
  padding: 20px;
  background-color: #3498db;
  color: white;
  margin: 0;
}

.todo-form {
  display: flex;
  gap: 10px;
  padding: 20px;
  border-bottom: 2px solid #eee;
}

.todo-input {
  flex: 1;
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.todo-input:focus {
  outline: none;
  border-color: #3498db;
}

.add-button {
  padding: 10px 20px;
  font-size: 16px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.add-button:hover {
  background-color: #2980b9;
}

.todo-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
}

.todo-item.completed {
  background-color: #f0f0f0;
}

.todo-text {
  flex: 1;
  margin-left: 10px;
}

.todo-text.completed {
  text-decoration: line-through;
  color: #999;
}

.delete-button {
  background-color: #e74c3c;
  color: white;
  border: none;
  padding: 4px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.delete-button:hover {
  background-color: #c0392b;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #f8f9fa;
  border-top: 2px solid #eee;
}

.filter-button {
  padding: 6px 14px;
  border: 2px solid transparent;
  background-color: transparent;
  color: #555;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.filter-button.active {
  border-color: #3498db;
  background-color: #3498db;
  color: white;
}

.remaining-count {
  color: #888;
  font-size: 14px;
}

.empty-message {
  text-align: center;
  color: #999;
  padding: 20px;
}
```

To use this CSS file, import it at the top of your App component:

```jsx
import './App.css';
```

Then replace the `style` props in your JSX with `className` props. For example, change:

```jsx
<div style={appStyle}>
```

to:

```jsx
<div className="app-container">
```

The `className` prop in React is the same as the `class` attribute in HTML. We use `className` instead of `class` because `class` is a reserved word in JavaScript.

The CSS gives you extra benefits like `:hover` effects (the button changes color when you move your mouse over it) and `:focus` effects (the input border changes color when you click into it). These are harder to do with inline styles.

---

## What to Do When You Get Stuck

Every developer gets stuck. It is a normal part of programming. Here are some tips for when things do not work:

### Tip 1: Read the Error Message

Error messages look scary, but they are actually trying to help you. Focus on:

- **The first line.** It usually tells you what went wrong.
- **The file name and line number.** It tells you where the problem is.

For example: `TypeError: Cannot read properties of undefined (reading 'map')` — This means you tried to use `.map()` on something that is `undefined`. Check that you are passing the right data.

### Tip 2: Use console.log

When you are not sure what a variable contains, add `console.log` to check:

```jsx
function handleAddTodo(text) {
  console.log('Adding todo:', text);
  // rest of the function
}
```

Open your browser's developer tools (press F12 or right-click and choose "Inspect," then click the "Console" tab) to see the output.

### Tip 3: Check Your Props

A very common bug is passing the wrong prop or forgetting to pass a prop. If a component is not working:

1. Add `console.log(props)` at the top of the component to see what it received.
2. Check the parent component to make sure it is passing the right values.
3. Make sure prop names match exactly (they are case-sensitive).

### Tip 4: Start Small

If something is not working, simplify. Remove parts of the code until the basic version works. Then add features back one at a time. This helps you find exactly where the problem is.

### Tip 5: Compare with Working Code

If you are stuck on this project, compare your code with the examples in this chapter. Look for small differences: a missing comma, a misspelled variable name, a missing `return` statement.

### Tip 6: Take a Break

Sometimes the best debugging tool is walking away for a few minutes. Your brain often solves the problem in the background. Come back with fresh eyes, and the answer might be obvious.

---

## Complete Project Code

Here is the full code for every file in the project. If you got lost at any point, you can refer to this section.

### src/components/TodoItem.jsx

```jsx
function TodoItem({ todo, onToggle, onDelete }) {
  const itemStyle = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '12px 16px',
    borderBottom: '1px solid #eee',
    backgroundColor: todo.completed ? '#f0f0f0' : 'white'
  };

  const textStyle = {
    textDecoration: todo.completed ? 'line-through' : 'none',
    color: todo.completed ? '#999' : '#333',
    flex: 1,
    marginLeft: '10px'
  };

  const deleteButtonStyle = {
    backgroundColor: '#e74c3c',
    color: 'white',
    border: 'none',
    padding: '4px 10px',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '12px'
  };

  return (
    <div style={itemStyle}>
      <input
        type="checkbox"
        checked={todo.completed}
        onChange={function () {
          onToggle(todo.id);
        }}
      />
      <span style={textStyle}>{todo.text}</span>
      <button
        style={deleteButtonStyle}
        onClick={function () {
          onDelete(todo.id);
        }}
      >
        Delete
      </button>
    </div>
  );
}

export default TodoItem;
```

### src/components/TodoList.jsx

```jsx
import TodoItem from './TodoItem';

function TodoList({ todos, onToggle, onDelete }) {
  if (todos.length === 0) {
    return (
      <p style={{ textAlign: 'center', color: '#999', padding: '20px' }}>
        No todos to show. Add one above!
      </p>
    );
  }

  return (
    <div>
      {todos.map(function (todo) {
        return (
          <TodoItem
            key={todo.id}
            todo={todo}
            onToggle={onToggle}
            onDelete={onDelete}
          />
        );
      })}
    </div>
  );
}

export default TodoList;
```

### src/components/TodoForm.jsx

```jsx
import React from 'react';

function TodoForm({ onAdd }) {
  const [text, setText] = React.useState('');

  function handleSubmit(event) {
    event.preventDefault();

    const trimmedText = text.trim();

    if (trimmedText === '') {
      return;
    }

    onAdd(trimmedText);
    setText('');
  }

  const formStyle = {
    display: 'flex',
    gap: '10px',
    padding: '20px',
    borderBottom: '2px solid #eee'
  };

  const inputStyle = {
    flex: 1,
    padding: '10px',
    fontSize: '16px',
    border: '1px solid #ddd',
    borderRadius: '4px'
  };

  const buttonStyle = {
    padding: '10px 20px',
    fontSize: '16px',
    backgroundColor: '#3498db',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer'
  };

  return (
    <form onSubmit={handleSubmit} style={formStyle}>
      <input
        type="text"
        placeholder="What do you need to do?"
        value={text}
        onChange={function (event) {
          setText(event.target.value);
        }}
        style={inputStyle}
      />
      <button type="submit" style={buttonStyle}>
        Add
      </button>
    </form>
  );
}

export default TodoForm;
```

### src/components/TodoFilter.jsx

```jsx
function TodoFilter({ filter, onFilterChange, remainingCount }) {
  const containerStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '12px 16px',
    backgroundColor: '#f8f9fa',
    borderTop: '2px solid #eee'
  };

  function getButtonStyle(buttonFilter) {
    const isActive = filter === buttonFilter;

    return {
      padding: '6px 14px',
      border: isActive ? '2px solid #3498db' : '2px solid transparent',
      backgroundColor: isActive ? '#3498db' : 'transparent',
      color: isActive ? 'white' : '#555',
      borderRadius: '4px',
      cursor: 'pointer',
      fontSize: '14px'
    };
  }

  return (
    <div style={containerStyle}>
      <span style={{ color: '#888', fontSize: '14px' }}>
        {remainingCount} {remainingCount === 1 ? 'item' : 'items'} left
      </span>
      <div style={{ display: 'flex', gap: '5px' }}>
        <button
          style={getButtonStyle('all')}
          onClick={function () { onFilterChange('all'); }}
        >
          All
        </button>
        <button
          style={getButtonStyle('active')}
          onClick={function () { onFilterChange('active'); }}
        >
          Active
        </button>
        <button
          style={getButtonStyle('completed')}
          onClick={function () { onFilterChange('completed'); }}
        >
          Completed
        </button>
      </div>
    </div>
  );
}

export default TodoFilter;
```

### src/App.jsx

```jsx
import React from 'react';
import TodoForm from './components/TodoForm';
import TodoList from './components/TodoList';
import TodoFilter from './components/TodoFilter';

function App() {
  const [todos, setTodos] = React.useState([
    { id: 1, text: 'Learn React basics', completed: true },
    { id: 2, text: 'Build a todo app', completed: false },
    { id: 3, text: 'Practice every day', completed: false }
  ]);

  const [filter, setFilter] = React.useState('all');

  function handleAddTodo(text) {
    const newTodo = {
      id: Date.now(),
      text: text,
      completed: false
    };

    setTodos(function (currentTodos) {
      return [...currentTodos, newTodo];
    });
  }

  function handleToggleTodo(id) {
    setTodos(function (currentTodos) {
      return currentTodos.map(function (todo) {
        if (todo.id === id) {
          return { ...todo, completed: !todo.completed };
        }
        return todo;
      });
    });
  }

  function handleDeleteTodo(id) {
    setTodos(function (currentTodos) {
      return currentTodos.filter(function (todo) {
        return todo.id !== id;
      });
    });
  }

  let filteredTodos;

  if (filter === 'active') {
    filteredTodos = todos.filter(function (todo) {
      return !todo.completed;
    });
  } else if (filter === 'completed') {
    filteredTodos = todos.filter(function (todo) {
      return todo.completed;
    });
  } else {
    filteredTodos = todos;
  }

  const remainingCount = todos.filter(function (todo) {
    return !todo.completed;
  }).length;

  const appStyle = {
    maxWidth: '500px',
    margin: '40px auto',
    backgroundColor: 'white',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
    overflow: 'hidden'
  };

  const headerStyle = {
    textAlign: 'center',
    padding: '20px',
    backgroundColor: '#3498db',
    color: 'white',
    margin: 0
  };

  return (
    <div style={{ backgroundColor: '#ecf0f1', minHeight: '100vh', padding: '20px' }}>
      <div style={appStyle}>
        <h1 style={headerStyle}>My Todo List</h1>
        <TodoForm onAdd={handleAddTodo} />
        <TodoList
          todos={filteredTodos}
          onToggle={handleToggleTodo}
          onDelete={handleDeleteTodo}
        />
        <TodoFilter
          filter={filter}
          onFilterChange={setFilter}
          remainingCount={remainingCount}
        />
      </div>
    </div>
  );
}

export default App;
```

---

## Quick Summary

- **Plan before you code.** Ask: What should it do? What components do I need? What state do I need?
- **Build bottom-up.** Start with the smallest components and work your way up.
- **Keep state where it is needed.** The `App` component holds shared state (todos, filter). The `TodoForm` keeps its own local state (input text).
- **Pass data down with props, events up with functions.** This is the pattern from Chapter 18 (lifting state up) in action.
- **Use `.map()` to render lists, `.filter()` to filter data, and the spread operator (`...`) to create copies.**
- **Simple CSS** can be added in a separate file for cleaner code and extra features like hover effects.

---

## Key Points to Remember

1. Planning saves time. Even five minutes of thinking before coding prevents hours of confusion.
2. Break your app into small components. Each component should do one thing well.
3. State that multiple components need should live in their shared parent.
4. State that only one component needs (like form input text) can stay local.
5. Never modify state directly. Always create new arrays and objects using spread (`...`), `map`, and `filter`.
6. Error messages are your friends. Read them carefully — they tell you what went wrong and where.
7. Use `console.log` liberally when debugging. It is the simplest and most effective debugging tool.

---

## Practice Questions

1. Why did we put the `todos` state in the `App` component instead of in `TodoList`?
2. Why does `TodoForm` keep its own local state for the input text instead of lifting it up to `App`?
3. What does `Date.now()` do, and why do we use it as an ID?
4. What is the difference between `todos` and `filteredTodos` in the `App` component?
5. Why do we use `event.preventDefault()` in the form submit handler?

---

## Exercises

### Exercise 1: Edit a Todo

Add the ability to edit an existing todo. When the user double-clicks on a todo's text, it should turn into an input field. The user can type a new text and press Enter to save. (Hint: You will need a new piece of state in `TodoItem` to track whether it is being edited.)

### Exercise 2: Clear All Completed

Add a "Clear Completed" button to the filter bar. When clicked, it should remove all completed todos at once. (Hint: Use `filter` to keep only todos where `completed` is `false`.)

### Exercise 3: Save to Local Storage

Make the todos persist even after the browser is closed. Use `localStorage` to save the todos whenever they change, and load them when the app starts. (Hint: `localStorage.setItem('todos', JSON.stringify(todos))` saves data, and `JSON.parse(localStorage.getItem('todos'))` loads it.)

---

## What Is Next?

Congratulations! You have built your first complete React application. You planned it, broke it into components, managed state, handled user interactions, and styled it. These are real skills that professional developers use every day.

This Todo App is just the beginning. Here are some ideas for what to explore next:

- **Add routing** (from Chapter 19) to give your app multiple pages.
- **Learn about `useEffect`** to fetch data from the internet or save data automatically.
- **Explore Context API** to share data across many components without passing props through every level.
- **Try a UI library** like Material UI or Tailwind CSS to make your apps look polished.
- **Build more projects.** The best way to learn is by building. Try a weather app, a note-taking app, or a simple game.

Remember: every expert was once a beginner. You have come a long way, and the most important step is the next one. Keep building, keep learning, and keep having fun with React.
