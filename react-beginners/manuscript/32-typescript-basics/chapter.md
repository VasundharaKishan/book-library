# Chapter 32: TypeScript Basics with React

---

## What You Will Learn

- What TypeScript is and why it exists
- How TypeScript helps you catch mistakes early
- How to set up a React project with TypeScript
- Basic types: string, number, boolean, and arrays
- How to type component props
- How to type `useState`
- How to type events
- How to type function return values
- Common TypeScript errors and how to fix them

## Why This Chapter Matters

Imagine you have a box in your kitchen. Sometimes you put flour in it. Sometimes you put sugar in it. They look the same. One day, you grab what you think is sugar and put it in your coffee. It is flour. Your coffee is ruined.

Now imagine every box has a clear label: "FLOUR", "SUGAR", "SALT". You never mix them up again.

That is what TypeScript does for your code. JavaScript lets you put anything anywhere, and sometimes things go wrong in surprising ways. TypeScript adds labels (called **types**) to your data, so you always know what is what. And if you try to put flour in the sugar box, TypeScript tells you before you even run your code.

TypeScript is used in most professional React projects today. Learning the basics now will prepare you for real-world jobs and larger projects.

---

## What Is TypeScript?

**TypeScript** is JavaScript with types. That is really all it is.

Every piece of TypeScript is valid JavaScript with extra information added. TypeScript files end in `.ts` (for regular files) or `.tsx` (for files with JSX, which is what you use in React).

Here is the difference:

```javascript
// JavaScript — no types
let name = 'Alice';
let age = 25;
let isStudent = true;
```

```typescript
// TypeScript — same code, but with type labels
let name: string = 'Alice';
let age: number = 25;
let isStudent: boolean = true;
```

The `: string`, `: number`, and `: boolean` are **type annotations** (labels). They tell TypeScript what kind of data each variable holds.

### What Happens If You Make a Mistake?

```typescript
let age: number = 25;
age = 'twenty-five'; // ERROR! TypeScript says: "You cannot put a string in a number box."
```

TypeScript catches this mistake before you run your code. It underlines the error in your editor with a red squiggly line, just like a spell checker.

Without TypeScript, this mistake would silently break your app at runtime (when the code is running). With TypeScript, you see it immediately.

---

## Setting Up a React + TypeScript Project

Creating a React project with TypeScript is simple. You use the same tool (Vite) but choose a TypeScript template.

Open your terminal and run:

```bash
npm create vite@latest my-app -- --template react-ts
```

Then:

```bash
cd my-app
npm install
npm run dev
```

That is it. The project is set up with TypeScript. You will notice the files end in `.tsx` instead of `.jsx`.

### What Is Different?

Your project now has a file called `tsconfig.json`. This is the TypeScript configuration file. You do not need to change it. The defaults work great.

Your component files are `.tsx` instead of `.jsx`. Inside them, you write the same React code you already know, but with type annotations added.

---

## Basic Types

TypeScript has a few basic types that you will use all the time. Let us learn each one.

### string

For text.

```typescript
let firstName: string = 'Alice';
let greeting: string = "Hello, world!";
let message: string = `Welcome, ${firstName}`;
```

### number

For all numbers (whole numbers, decimals, negatives).

```typescript
let age: number = 25;
let price: number = 9.99;
let temperature: number = -5;
```

### boolean

For true or false values.

```typescript
let isLoggedIn: boolean = true;
let hasError: boolean = false;
```

### Arrays

For lists of items. You write the type of the items, then add `[]`.

```typescript
let names: string[] = ['Alice', 'Bob', 'Charlie'];
let scores: number[] = [95, 87, 73, 100];
let flags: boolean[] = [true, false, true];
```

If you try to put the wrong type in an array, TypeScript catches it:

```typescript
let names: string[] = ['Alice', 'Bob'];
names.push(42); // ERROR! 42 is a number, not a string.
```

### Objects

For data with named fields. You define the shape with an **interface** (a description of what the object looks like).

```typescript
interface User {
  name: string;
  age: number;
  email: string;
}

let user: User = {
  name: 'Alice',
  age: 25,
  email: 'alice@example.com'
};
```

An **interface** is like a blueprint. It says: "A User must have a `name` that is a string, an `age` that is a number, and an `email` that is a string."

If you forget a field or use the wrong type, TypeScript tells you:

```typescript
let user: User = {
  name: 'Alice',
  age: 'twenty-five' // ERROR! age should be a number.
};
```

### Optional Properties

Sometimes a field might or might not exist. Add a `?` after the name:

```typescript
interface User {
  name: string;
  age: number;
  email?: string; // email is optional
}

let user1: User = { name: 'Alice', age: 25 }; // OK, no email
let user2: User = { name: 'Bob', age: 30, email: 'bob@example.com' }; // Also OK
```

---

## Typing Component Props

This is where TypeScript really shines in React. You can define exactly what props a component accepts.

### Without TypeScript

```jsx
// JavaScript — no type checking on props
function Greeting({ name, age }) {
  return <p>Hello, {name}! You are {age} years old.</p>;
}

// Oops, we passed a string for age. No error until something breaks.
<Greeting name="Alice" age="twenty-five" />
```

### With TypeScript

```tsx
// TypeScript — props are type-checked
interface GreetingProps {
  name: string;
  age: number;
}

function Greeting({ name, age }: GreetingProps) {
  return <p>Hello, {name}! You are {age} years old.</p>;
}

// TypeScript catches the mistake immediately
<Greeting name="Alice" age="twenty-five" /> // ERROR! age should be a number.
<Greeting name="Alice" age={25} /> // OK!
```

### Line-by-Line Explanation

```tsx
interface GreetingProps {
  name: string;
  age: number;
}
```
We define an interface called `GreetingProps`. It describes the shape of the props object. The component expects a `name` (string) and an `age` (number).

```tsx
function Greeting({ name, age }: GreetingProps) {
```
We add `: GreetingProps` after the props destructuring. This tells TypeScript that the props must match the `GreetingProps` interface.

### Props with Optional Values

```tsx
interface CardProps {
  title: string;
  subtitle?: string; // optional
  color?: string;    // optional
}

function Card({ title, subtitle, color = 'blue' }: CardProps) {
  return (
    <div style={{ borderColor: color }}>
      <h2>{title}</h2>
      {subtitle && <p>{subtitle}</p>}
    </div>
  );
}

// All of these work:
<Card title="Hello" />
<Card title="Hello" subtitle="World" />
<Card title="Hello" subtitle="World" color="red" />
```

### Props with Functions

```tsx
interface ButtonProps {
  label: string;
  onClick: () => void;
}

function Button({ label, onClick }: ButtonProps) {
  return <button onClick={onClick}>{label}</button>;
}
```

The type `() => void` means "a function that takes no arguments and returns nothing." The word **void** means "no return value."

### Props with Children

If your component accepts children (content placed between opening and closing tags), type it like this:

```tsx
interface ContainerProps {
  children: React.ReactNode;
}

function Container({ children }: ContainerProps) {
  return <div className="container">{children}</div>;
}

// Usage:
<Container>
  <h1>Hello!</h1>
  <p>This is inside the container.</p>
</Container>
```

`React.ReactNode` is a special type that means "anything that React can render." This includes strings, numbers, JSX elements, arrays, and more.

---

## Typing useState

When you use `useState`, TypeScript can usually figure out the type automatically:

```tsx
const [count, setCount] = useState(0); // TypeScript knows count is a number
const [name, setName] = useState('');   // TypeScript knows name is a string
```

But sometimes you need to tell TypeScript the type explicitly. Use angle brackets `<>` after `useState`:

```tsx
// When the initial value does not tell the full story
const [user, setUser] = useState<User | null>(null);
```

Here, `User | null` means "the value is either a User object or null." The `|` symbol means "or." This is common when you fetch data: the value starts as `null` and becomes a `User` after loading.

### More Examples

```tsx
// An array that starts empty
const [items, setItems] = useState<string[]>([]);

// A number that could be undefined
const [selectedId, setSelectedId] = useState<number | undefined>(undefined);

// An object with a specific shape
interface Todo {
  id: number;
  text: string;
  done: boolean;
}

const [todos, setTodos] = useState<Todo[]>([]);
```

**Why is this needed?** When you write `useState([])`, TypeScript sees an empty array and thinks the type is `never[]` (an array that can never have anything in it). By writing `useState<string[]>([])`, you tell TypeScript that this array will hold strings.

---

## Typing Events

When you handle events like clicks, form submissions, or input changes, TypeScript needs to know the type of the event.

### Typing Input Change Events

```tsx
function SearchBox() {
  const [query, setQuery] = useState('');

  function handleChange(event: React.ChangeEvent<HTMLInputElement>) {
    setQuery(event.target.value);
  }

  return <input value={query} onChange={handleChange} />;
}
```

`React.ChangeEvent<HTMLInputElement>` means "a change event from an HTML input element." It is a long type, but here is how to read it:

- `React.ChangeEvent` — this is a change event (the value changed)
- `<HTMLInputElement>` — it happened on an input element

### Typing Form Submit Events

```tsx
function LoginForm() {
  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    // handle the form submission
  }

  return (
    <form onSubmit={handleSubmit}>
      <button type="submit">Log In</button>
    </form>
  );
}
```

### Typing Click Events

```tsx
function MyButton() {
  function handleClick(event: React.MouseEvent<HTMLButtonElement>) {
    console.log('Button clicked!');
  }

  return <button onClick={handleClick}>Click me</button>;
}
```

### The Easy Way: Inline Handlers

Here is a tip. When you write the event handler inline (directly in the JSX), TypeScript figures out the type automatically:

```tsx
function SearchBox() {
  const [query, setQuery] = useState('');

  return (
    <input
      value={query}
      onChange={(e) => setQuery(e.target.value)} // TypeScript knows e is a ChangeEvent!
    />
  );
}
```

You only need to type events manually when you define the handler as a separate function.

---

## Typing Function Return Values

You can tell TypeScript what a function returns:

```tsx
function add(a: number, b: number): number {
  return a + b;
}

function greet(name: string): string {
  return `Hello, ${name}!`;
}

function logMessage(message: string): void {
  console.log(message);
  // returns nothing, so the return type is void
}
```

For React components, the return type is usually `JSX.Element`:

```tsx
function Greeting({ name }: { name: string }): JSX.Element {
  return <p>Hello, {name}!</p>;
}
```

However, you usually do not need to write the return type for components. TypeScript figures it out automatically. It is fine to leave it off.

---

## A Complete TypeScript React Component

Let us put everything together. Here is a complete component with full TypeScript types:

```tsx
import { useState } from 'react';

interface Todo {
  id: number;
  text: string;
  done: boolean;
}

interface TodoItemProps {
  todo: Todo;
  onToggle: (id: number) => void;
  onDelete: (id: number) => void;
}

function TodoItem({ todo, onToggle, onDelete }: TodoItemProps) {
  return (
    <li>
      <span
        style={{ textDecoration: todo.done ? 'line-through' : 'none' }}
        onClick={() => onToggle(todo.id)}
      >
        {todo.text}
      </span>
      <button onClick={() => onDelete(todo.id)}>Delete</button>
    </li>
  );
}

function TodoApp() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [text, setText] = useState('');

  function handleAdd() {
    if (text.trim() === '') return;
    const newTodo: Todo = {
      id: Date.now(),
      text: text,
      done: false
    };
    setTodos([...todos, newTodo]);
    setText('');
  }

  function handleToggle(id: number) {
    setTodos(todos.map(todo =>
      todo.id === id ? { ...todo, done: !todo.done } : todo
    ));
  }

  function handleDelete(id: number) {
    setTodos(todos.filter(todo => todo.id !== id));
  }

  return (
    <div>
      <h1>My Todos</h1>
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Add a task..."
      />
      <button onClick={handleAdd}>Add</button>
      <ul>
        {todos.map(todo => (
          <TodoItem
            key={todo.id}
            todo={todo}
            onToggle={handleToggle}
            onDelete={handleDelete}
          />
        ))}
      </ul>
    </div>
  );
}

export default TodoApp;
```

**Expected output:**

```
My Todos

[Add a task...    ] [Add]

- Buy groceries    [Delete]
- Walk the dog     [Delete]
```

This is the same to-do list you have built before. The only difference is the type annotations. TypeScript will now catch mistakes like passing a string where a number is expected, forgetting a required prop, or misspelling a property name.

---

## Common TypeScript Errors and How to Fix Them

Here are errors you will see often as a beginner. Do not worry — they are all easy to fix.

### Error 1: Type 'string' is not assignable to type 'number'

```tsx
let age: number = 'twenty-five';
// Fix: use a number
let age: number = 25;
```

**What it means:** You tried to put a string where a number belongs.

### Error 2: Property 'X' does not exist on type 'Y'

```tsx
interface User {
  name: string;
}

const user: User = { name: 'Alice' };
console.log(user.age); // ERROR: Property 'age' does not exist on type 'User'
```

**Fix:** Either add `age` to the interface, or remove the line that uses it.

### Error 3: Argument of type 'X' is not assignable to parameter of type 'Y'

```tsx
function greet(name: string) {
  return `Hello, ${name}`;
}

greet(42); // ERROR: Argument of type 'number' is not assignable to parameter of type 'string'
```

**Fix:** Pass the correct type: `greet('Alice')`.

### Error 4: Object is possibly 'null'

```tsx
const [user, setUser] = useState<User | null>(null);

return <p>{user.name}</p>; // ERROR: user might be null!
```

**Fix:** Check for null before using the value:

```tsx
if (user === null) return <p>Loading...</p>;
return <p>{user.name}</p>; // TypeScript now knows user is not null
```

### Error 5: Property 'X' is missing in type 'Y'

```tsx
interface ButtonProps {
  label: string;
  onClick: () => void;
}

<Button label="Click me" /> // ERROR: Property 'onClick' is missing
```

**Fix:** Either provide the missing prop or make it optional with `?`:

```tsx
interface ButtonProps {
  label: string;
  onClick?: () => void; // now optional
}
```

---

## Quick Summary

**TypeScript** is JavaScript with type labels. It catches mistakes before you run your code, like a spell-checker for programming.

You add types using the `: type` syntax. For component props, you define an **interface** that describes the shape of the props object.

`useState` usually infers the type automatically, but you can specify it with `useState<Type>()` when needed.

Event types like `React.ChangeEvent<HTMLInputElement>` tell TypeScript what kind of event you are handling. Inline handlers get their types automatically.

---

## Key Points to Remember

1. **TypeScript is JavaScript with types.** Every valid JavaScript is valid TypeScript. You are adding type information, not learning a new language.

2. **Use interfaces to define prop shapes.** Write `interface Props { ... }` and apply it to your component parameters.

3. **TypeScript often infers types automatically.** You do not need to type everything. Let TypeScript figure it out when it can.

4. **Use `useState<Type>()` for complex initial values.** Especially when the initial value is `null`, `undefined`, or an empty array.

5. **Inline event handlers get types for free.** If you write the handler directly in JSX, TypeScript knows the event type.

6. **Read error messages carefully.** TypeScript errors are helpful. They tell you exactly what is wrong and where.

7. **Start simple.** You do not need to type everything perfectly on day one. Add types gradually as you learn.

---

## Practice Questions

1. What is the difference between JavaScript and TypeScript?

2. What is an interface in TypeScript? Why is it useful for React props?

3. What does `useState<string[]>([])` mean?

4. What type would you use for an `onChange` event on an `<input>` element?

5. What does the error "Object is possibly null" mean, and how do you fix it?

---

## Exercises

### Exercise 1: Type a Profile Card

Create a `ProfileCard` component with these typed props:
- `name` (required string)
- `bio` (required string)
- `age` (required number)
- `website` (optional string)

Display all the information. If no website is provided, show "No website."

### Exercise 2: Type a Counter Component

Build a counter component using TypeScript. The state should be typed. Create a `CounterProps` interface with:
- `initialValue` (required number)
- `step` (optional number, defaults to 1)

The counter should increment and decrement by the step value.

### Exercise 3: Type a User List

Create a `User` interface with `id` (number), `name` (string), and `email` (string). Create a component that:
- Uses `useState<User[]>([])` for the users list
- Has an input form to add new users
- Displays the list of users
- Types all event handlers properly

---

## Congratulations and What to Learn Next

You have made it to the end of this book. Take a moment to appreciate how far you have come.

When you started, you did not know what React was. Now you can:

- Build components with JSX
- Manage state with `useState` and `useReducer`
- Handle side effects with `useEffect`
- Fetch data from APIs
- Route between pages
- Share data with Context
- Create your own custom hooks
- Add type safety with TypeScript

That is a lot. You should be proud.

But learning never stops. Here are the most important things to explore next, in order of priority.

### Next.js

**Next.js** is a framework built on top of React. While React handles the user interface, Next.js adds features like:
- Server-side rendering (pages load faster)
- File-based routing (create a file, get a route — no React Router needed)
- API routes (build your backend in the same project)
- Built-in optimizations for images, fonts, and more

Most new React projects today use Next.js. It is the natural next step after learning React.

### State Management Libraries

For large applications, Context + `useReducer` might not be enough. Libraries like **Zustand**, **Jotai**, and **Redux Toolkit** provide more powerful state management. Zustand is the easiest to learn and is a great place to start.

### Testing

Testing ensures your code works correctly and keeps working as you make changes. Learn:
- **Vitest** — a fast test runner for Vite projects
- **React Testing Library** — for testing React components the way users interact with them

### CSS Frameworks

Styling large applications by hand is slow. Popular options include:
- **Tailwind CSS** — utility classes directly in your JSX
- **CSS Modules** — scoped CSS that does not leak between components
- **styled-components** — CSS written inside your JavaScript

### Where to Practice

The best way to learn is to build things. Here are some project ideas:
- A personal blog
- A weather app that fetches real data
- A simple e-commerce store
- A task management app with authentication

### Final Words

Programming is a journey, not a destination. Every expert was once a beginner. Every complex application started as a simple component.

You now have a solid foundation. Build things. Break things. Fix things. That is how you grow.

Good luck, and happy coding.
