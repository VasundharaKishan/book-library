# Chapter 4: Components and Props

---

## Learning Goals

By the end of this chapter, you will be able to:

- Understand what components are and why they are the building blocks of React
- Create functional components and use them in your application
- Pass data to components using props
- Destructure props for cleaner code
- Set default values for props
- Pass different types of data as props (strings, numbers, objects, arrays, functions, JSX)
- Understand the children prop and component composition
- Know the difference between props and state at a conceptual level
- Apply the one-way data flow principle
- Break a user interface into a component tree
- Follow naming conventions and best practices for components

---

## What Are Components?

Think of components as **building blocks** — like LEGO bricks. Each brick has a specific shape and purpose. You can combine small bricks to build bigger structures. In React, each component is a small, independent, reusable piece of UI.

Consider a typical web page: a navigation bar at the top, a sidebar on the left, a list of articles in the middle, and a footer at the bottom. In traditional HTML, this would be one large file with hundreds of lines. In React, each of these sections becomes its own component:

```
┌──────────────────────────────────────────┐
│              <Navbar />                  │
├──────────┬───────────────────────────────┤
│          │                               │
│          │     <ArticleList />           │
│ <Sidebar │                               │
│   />     │   ┌───────────────────────┐   │
│          │   │   <ArticleCard />     │   │
│          │   ├───────────────────────┤   │
│          │   │   <ArticleCard />     │   │
│          │   ├───────────────────────┤   │
│          │   │   <ArticleCard />     │   │
│          │   └───────────────────────┘   │
│          │                               │
├──────────┴───────────────────────────────┤
│              <Footer />                  │
└──────────────────────────────────────────┘
```

Each box in this diagram is a React component. The page is made up of components nested inside other components.

### Why Use Components?

Here are the practical benefits:

1. **Reusability.** Write a `Button` component once, use it everywhere in your app. Need 50 buttons on different pages? You write the button code once.

2. **Maintainability.** If the navigation bar needs to change, you edit one file (`Navbar.jsx`), not every page that has a navigation bar.

3. **Separation of concerns.** Each component handles its own logic, styling, and rendering. A `SearchBar` component handles search logic; a `UserProfile` component handles user display logic.

4. **Readability.** Instead of reading 500 lines of HTML, you read:

   ```jsx
   <Navbar />
   <Sidebar />
   <ArticleList />
   <Footer />
   ```

   Each line tells you exactly what that section is.

5. **Team collaboration.** One developer can work on `Navbar` while another works on `ArticleList`. They do not need to edit the same file.

6. **Testability.** You can test each component independently. Does the `LoginForm` submit correctly? Test just that component without loading the entire application.

---

## Creating Your First Component

A React component is a JavaScript function that returns JSX. That is it. At its simplest:

```jsx
function Greeting() {
  return <h1>Hello, World!</h1>;
}
```

This is a complete, valid React component. Let us break down the rules:

### Component Rules

**Rule 1: The function name must start with a capital letter.**

```jsx
// ✅ Correct: starts with uppercase
function Greeting() {
  return <h1>Hello</h1>;
}

// ❌ Wrong: starts with lowercase
function greeting() {
  return <h1>Hello</h1>;
}
```

**Why?** React uses the capitalization to distinguish between your custom components and regular HTML elements. When React sees `<Greeting />`, it knows it is a component. When it sees `<div>`, it knows it is a regular HTML element. If your component starts with a lowercase letter, React treats it as an HTML element and it will not work correctly.

**Rule 2: The function must return JSX (or `null`).**

```jsx
// ✅ Returns JSX
function Welcome() {
  return <p>Welcome to our app!</p>;
}

// ✅ Returns null (renders nothing)
function HiddenComponent() {
  return null;
}

// ❌ Wrong: returns a plain string without JSX context
// (This technically works, but it is unconventional and limits what you can do)
function NotIdeal() {
  return "Hello";
}
```

**Rule 3: The function must return a single root element (or use a Fragment).**

We covered this in Chapter 3, but it applies to every component:

```jsx
// ✅ Single root element
function Card() {
  return (
    <div>
      <h2>Title</h2>
      <p>Content</p>
    </div>
  );
}

// ✅ Fragment as root
function Card() {
  return (
    <>
      <h2>Title</h2>
      <p>Content</p>
    </>
  );
}
```

### Using a Component

Once you create a component, you use it as if it were a custom HTML tag:

```jsx
function Greeting() {
  return <h1>Hello, World!</h1>;
}

function App() {
  return (
    <div>
      <Greeting />
      <Greeting />
      <Greeting />
    </div>
  );
}
```

**What this code does:** The `App` component renders three `Greeting` components. Each `<Greeting />` is replaced with the JSX that the `Greeting` function returns. The final HTML output would be:

```html
<div>
  <h1>Hello, World!</h1>
  <h1>Hello, World!</h1>
  <h1>Hello, World!</h1>
</div>
```

Notice that `<Greeting />` uses a self-closing tag. You can also write it as `<Greeting></Greeting>`, but when a component has no children (no content between the tags), the self-closing form is preferred.

### Function Declarations vs Arrow Functions

You can define components using either function declarations or arrow functions. Both work the same way:

```jsx
// Function declaration
function Greeting() {
  return <h1>Hello!</h1>;
}

// Arrow function assigned to a variable
const Greeting = () => {
  return <h1>Hello!</h1>;
};

// Arrow function with implicit return
const Greeting = () => <h1>Hello!</h1>;
```

All three produce identical results. This book uses function declarations because they are easier to read and do not need to be defined before they are used (JavaScript "hoists" function declarations). But in practice, both styles are common in React projects. Pick one and be consistent across your codebase.

---

## Organizing Components in Files

In a real project, each component lives in its own file. This keeps your code organized and makes components easy to find.

### One Component Per File

```
src/
├── App.jsx
├── Navbar.jsx
├── Footer.jsx
├── Greeting.jsx
└── main.jsx
```

**Greeting.jsx:**

```jsx
function Greeting() {
  return <h1>Hello, World!</h1>;
}

export default Greeting;
```

**App.jsx:**

```jsx
import Greeting from "./Greeting";

function App() {
  return (
    <div>
      <Greeting />
    </div>
  );
}

export default App;
```

**Key points:**
- `export default Greeting` makes the component available to other files.
- `import Greeting from "./Greeting"` brings the component into the file where you want to use it.
- The `./` means "the current directory." The `.jsx` extension is usually optional in the import (Vite resolves it automatically).
- The import name does not technically need to match the function name when using default exports, but it **should** for clarity and consistency.

### Named Exports vs Default Exports

There are two ways to export components:

**Default export** — one per file, imported without curly braces:

```jsx
// Greeting.jsx
function Greeting() {
  return <h1>Hello!</h1>;
}
export default Greeting;

// App.jsx
import Greeting from "./Greeting"; // No curly braces
```

**Named export** — can have multiple per file, imported with curly braces:

```jsx
// buttons.jsx
export function PrimaryButton() {
  return <button style={{ backgroundColor: "blue", color: "white" }}>Click me</button>;
}

export function SecondaryButton() {
  return <button style={{ backgroundColor: "gray", color: "white" }}>Click me</button>;
}

// App.jsx
import { PrimaryButton, SecondaryButton } from "./buttons"; // Curly braces required
```

**When to use which:**
- **Default export**: When a file contains one main component. This is the most common pattern — one component per file with a default export.
- **Named export**: When a file contains multiple related components, utilities, or constants. Also useful when you want to enforce that the import name matches the export name.

Most React projects use default exports for components, but many style guides (including some popular ones at large companies) prefer named exports because they prevent accidental renaming during import.

---

## What Are Props?

Right now, our `Greeting` component always says "Hello, World!" — it is static. But what if we want it to greet different people? That is what **props** are for.

Props (short for "properties") are inputs to a component. They let you pass data from a parent component to a child component, making the child dynamic and reusable.

**Real-life analogy:** Think of a component as a greeting card template. The template defines the layout — where the name goes, where the message goes. Props are the information you fill in: the recipient's name and the message. The same template can create different cards for different people.

```
┌─────────────────────────────┐
│     Greeting Card Template  │  ← Component
│                             │
│   Dear {name},              │  ← Props fill in
│                             │     the blanks
│   {message}                 │
│                             │
│   From, {sender}            │
│                             │
└─────────────────────────────┘
```

### Passing Props

Props are passed to a component the same way you add attributes to an HTML element:

```jsx
// Parent component passes props
function App() {
  return (
    <div>
      <Greeting name="Alice" />
      <Greeting name="Bob" />
      <Greeting name="Charlie" />
    </div>
  );
}
```

### Receiving Props

The component receives all its props as a single object — the first parameter of the function:

```jsx
// Child component receives props
function Greeting(props) {
  return <h1>Hello, {props.name}!</h1>;
}
```

**What this code does:**
1. `App` renders three `Greeting` components, each with a different `name` prop.
2. Each `Greeting` receives a `props` object. For the first one, `props` is `{ name: "Alice" }`.
3. `{props.name}` accesses the value and inserts it into the JSX.

**The output:**

```html
<div>
  <h1>Hello, Alice!</h1>
  <h1>Hello, Bob!</h1>
  <h1>Hello, Charlie!</h1>
</div>
```

One component template, three different results. This is the power of props.

### Multiple Props

You can pass as many props as you need:

```jsx
function App() {
  return (
    <UserCard
      name="Alice Johnson"
      role="Senior Developer"
      email="alice@example.com"
      yearsOfExperience={8}
      isActive={true}
    />
  );
}

function UserCard(props) {
  return (
    <div style={{ border: "1px solid #ddd", padding: "1rem", borderRadius: "8px" }}>
      <h2>{props.name}</h2>
      <p>Role: {props.role}</p>
      <p>Email: {props.email}</p>
      <p>Experience: {props.yearsOfExperience} years</p>
      <p>Status: {props.isActive ? "Active" : "Inactive"}</p>
    </div>
  );
}
```

**Notice the curly braces** around `{8}` and `{true}`. String props can use quotes: `name="Alice"`. But non-string values — numbers, booleans, objects, arrays, functions — must be wrapped in curly braces.

```jsx
// Strings: quotes
<Component title="Hello" />

// Numbers: curly braces
<Component count={42} />

// Booleans: curly braces
<Component isVisible={true} />

// Boolean shorthand: just the prop name means true
<Component isVisible />    // same as isVisible={true}

// Objects: curly braces (double braces because {} is an object literal)
<Component style={{ color: "red" }} />

// Arrays: curly braces
<Component items={["apple", "banana"]} />

// Variables: curly braces
<Component data={userData} />

// Functions: curly braces
<Component onClick={handleClick} />
```

---

## Destructuring Props

Accessing every prop through `props.name`, `props.role`, `props.email` gets repetitive. **Destructuring** lets you extract the values directly.

### What Is Destructuring?

Destructuring is a JavaScript feature (not a React feature) that lets you unpack values from objects or arrays into individual variables:

```javascript
// Without destructuring
const props = { name: "Alice", age: 28, role: "Developer" };
const name = props.name;
const age = props.age;
const role = props.role;

// With destructuring
const { name, age, role } = props;
// name is "Alice", age is 28, role is "Developer"
```

Both approaches give you the same variables with the same values. Destructuring is just shorter.

### Destructuring Props in the Function Parameter

The most common pattern in React is to destructure props directly in the function parameter:

```jsx
// Before: using props object
function UserCard(props) {
  return (
    <div>
      <h2>{props.name}</h2>
      <p>{props.role}</p>
      <p>{props.email}</p>
    </div>
  );
}

// After: destructuring in the parameter
function UserCard({ name, role, email }) {
  return (
    <div>
      <h2>{name}</h2>
      <p>{role}</p>
      <p>{email}</p>
    </div>
  );
}
```

**Why this is better:**
1. It is immediately clear what props the component expects — just look at the parameter list.
2. The JSX is cleaner: `{name}` instead of `{props.name}`.
3. You do not need to repeatedly type `props.` throughout the component.

You can also destructure inside the function body if you prefer:

```jsx
function UserCard(props) {
  const { name, role, email } = props;

  return (
    <div>
      <h2>{name}</h2>
      <p>{role}</p>
      <p>{email}</p>
    </div>
  );
}
```

Both approaches are valid. Destructuring in the parameter is more common and is the style this book uses.

### Destructuring with Renaming

Sometimes a prop name might conflict with a variable you are already using, or you want a more descriptive name inside the component:

```jsx
function Comment({ text: commentText, author: authorName }) {
  // Inside this function, commentText has the value of the "text" prop
  // and authorName has the value of the "author" prop
  return (
    <div>
      <p>{commentText}</p>
      <small>— {authorName}</small>
    </div>
  );
}

// Usage is the same — prop names don't change
<Comment text="Great article!" author="Alice" />
```

---

## Default Props

Sometimes a prop is optional — the parent might not always pass it. You can provide default values so the component always has something to work with.

### Using Default Values in Destructuring

The simplest and most modern approach is using JavaScript default values in the destructuring:

```jsx
function Button({ text = "Click me", color = "blue", size = "medium" }) {
  const sizeStyles = {
    small: { padding: "4px 8px", fontSize: "12px" },
    medium: { padding: "8px 16px", fontSize: "14px" },
    large: { padding: "12px 24px", fontSize: "16px" },
  };

  return (
    <button
      style={{
        backgroundColor: color,
        color: "white",
        border: "none",
        borderRadius: "4px",
        cursor: "pointer",
        ...sizeStyles[size],
      }}
    >
      {text}
    </button>
  );
}
```

Now you can use the component with all, some, or none of the props:

```jsx
function App() {
  return (
    <div>
      {/* Uses all defaults: "Click me", blue, medium */}
      <Button />

      {/* Custom text, default color and size */}
      <Button text="Submit" />

      {/* Custom text and color, default size */}
      <Button text="Delete" color="red" />

      {/* All custom */}
      <Button text="Learn More" color="green" size="large" />
    </div>
  );
}
```

**What this code does:** Each `Button` instance fills in any missing props with the default values. The first button gets all defaults because no props are passed. The second gets `text="Submit"` but uses default `color` and `size`. This makes your components flexible — callers only need to specify what differs from the default.

### When Defaults Are Not Applied

Default values only kick in when the prop is `undefined` — meaning it was not passed at all. If you explicitly pass `null` or an empty string, the default is **not** used:

```jsx
function Greeting({ name = "World" }) {
  return <h1>Hello, {name}!</h1>;
}

<Greeting />              // "Hello, World!" — default used
<Greeting name="Alice" /> // "Hello, Alice!" — prop used
<Greeting name="" />      // "Hello, !"     — empty string is NOT undefined
<Greeting name={null} />  // "Hello, !"     — null is NOT undefined
```

This is standard JavaScript behavior — default values only apply for `undefined`, not for other falsy values.

---

## Types of Data You Can Pass as Props

Props are not limited to strings and numbers. You can pass any JavaScript value.

### Strings

```jsx
<PageTitle title="Welcome to React" />
```

### Numbers

```jsx
<ProgressBar percentage={75} />
<Counter initialCount={0} />
```

### Booleans

```jsx
<Modal isOpen={true} />
<Modal isOpen={false} />

// Shorthand: just the prop name means true
<Modal isOpen />     // same as isOpen={true}
```

The boolean shorthand is commonly used. When you write a prop without a value, React sets it to `true`. This is similar to HTML boolean attributes like `<input disabled>`.

### Objects

```jsx
function App() {
  const user = {
    name: "Alice",
    age: 28,
    email: "alice@example.com",
  };

  return <UserProfile user={user} />;
}

function UserProfile({ user }) {
  return (
    <div>
      <h2>{user.name}</h2>
      <p>Age: {user.age}</p>
      <p>Email: {user.email}</p>
    </div>
  );
}
```

You can also spread an object as props (we will cover this later in the chapter).

### Arrays

```jsx
function App() {
  const skills = ["React", "JavaScript", "CSS", "Node.js"];

  return <SkillList skills={skills} />;
}

function SkillList({ skills }) {
  return (
    <ul>
      {skills.map((skill) => (
        <li key={skill}>{skill}</li>
      ))}
    </ul>
  );
}
```

### Functions

Passing functions as props is extremely common in React. It is how child components communicate back to parent components:

```jsx
function App() {
  function handleButtonClick() {
    alert("Button was clicked!");
  }

  return <AlertButton onClick={handleButtonClick} />;
}

function AlertButton({ onClick }) {
  return <button onClick={onClick}>Click me</button>;
}
```

**What this code does:**
1. `App` defines a function `handleButtonClick`.
2. `App` passes that function to `AlertButton` through the `onClick` prop.
3. `AlertButton` receives the function and attaches it to the button's `onClick` event.
4. When the user clicks the button, `handleButtonClick` runs (in the `App` component's context).

We will explore this pattern in depth in Chapter 6 (Event Handling) and Chapter 8 (State and Lifting State Up).

### JSX as Props

You can pass JSX elements as props — components as data:

```jsx
function App() {
  return (
    <Card
      header={<h2>Featured Article</h2>}
      footer={<button>Read More</button>}
    >
      <p>This is the card content.</p>
    </Card>
  );
}

function Card({ header, footer, children }) {
  return (
    <div style={{ border: "1px solid #ddd", borderRadius: "8px", overflow: "hidden" }}>
      <div style={{ padding: "1rem", backgroundColor: "#f5f5f5" }}>
        {header}
      </div>
      <div style={{ padding: "1rem" }}>
        {children}
      </div>
      <div style={{ padding: "1rem", backgroundColor: "#f5f5f5" }}>
        {footer}
      </div>
    </div>
  );
}
```

This pattern is incredibly powerful and is the foundation of **composition** — one of React's core principles, which we will explore later in this chapter.

---

## The `children` Prop

The `children` prop is a special, built-in prop in React. It represents whatever you put **between** the opening and closing tags of a component.

### How Children Works

```jsx
function Wrapper({ children }) {
  return (
    <div style={{ border: "2px solid blue", padding: "1rem" }}>
      {children}
    </div>
  );
}

function App() {
  return (
    <Wrapper>
      <h1>This is inside the Wrapper</h1>
      <p>So is this paragraph.</p>
    </Wrapper>
  );
}
```

**What this code does:**
1. `Wrapper` receives a `children` prop — React automatically assigns the content between `<Wrapper>` and `</Wrapper>` to `children`.
2. Inside `Wrapper`, `{children}` renders that content inside a styled `<div>`.
3. The result is the `<h1>` and `<p>` wrapped in a bordered, padded div.

**Output HTML:**

```html
<div style="border: 2px solid blue; padding: 1rem;">
  <h1>This is inside the Wrapper</h1>
  <p>So is this paragraph.</p>
</div>
```

### Children Can Be Anything

The `children` prop can be a string, a number, JSX elements, multiple elements, or even nothing:

```jsx
// Children is a string
<Wrapper>Hello</Wrapper>

// Children is a single element
<Wrapper><p>Content</p></Wrapper>

// Children is multiple elements
<Wrapper>
  <h1>Title</h1>
  <p>Description</p>
</Wrapper>

// No children (children is undefined)
<Wrapper />
<Wrapper></Wrapper>
```

### Practical Use: Layout Components

The `children` prop is commonly used for layout components — components that provide structure or styling without knowing what content will go inside:

```jsx
function PageLayout({ children }) {
  return (
    <div style={{ maxWidth: "1200px", margin: "0 auto", padding: "0 1rem" }}>
      {children}
    </div>
  );
}

function Section({ title, children }) {
  return (
    <section style={{ marginBottom: "2rem" }}>
      <h2 style={{ borderBottom: "2px solid #333", paddingBottom: "0.5rem" }}>
        {title}
      </h2>
      {children}
    </section>
  );
}

function App() {
  return (
    <PageLayout>
      <Section title="About Us">
        <p>We are a software company.</p>
        <p>We build great products.</p>
      </Section>

      <Section title="Our Services">
        <ul>
          <li>Web Development</li>
          <li>Mobile Apps</li>
          <li>Cloud Solutions</li>
        </ul>
      </Section>
    </PageLayout>
  );
}
```

**What this code does:**
- `PageLayout` centers and constrains content to a maximum width.
- `Section` adds a title with a bottom border and groups related content.
- `App` composes these layout components together, passing different content as children.
- Neither `PageLayout` nor `Section` knows or cares what content goes inside — they just provide the structure.

This is **composition** — building complex UIs by combining simple, focused components. It is one of React's most important patterns.

---

## Props Are Read-Only

This is a fundamental rule in React: **a component must never modify its own props.**

```jsx
function Greeting({ name }) {
  // ❌ NEVER DO THIS — do not modify props
  name = name.toUpperCase();

  return <h1>Hello, {name}!</h1>;
}
```

**Why?** Props come from the parent component. If a child modifies them, the parent would not know about the change, leading to bugs where the parent and child disagree about what the data is. React depends on predictable data flow — data always flows down from parent to child, and children never modify what they receive.

**The correct approach:** If you need a modified version of a prop, create a new variable:

```jsx
function Greeting({ name }) {
  // ✅ Create a new variable — don't modify the original prop
  const displayName = name.toUpperCase();

  return <h1>Hello, {displayName}!</h1>;
}
```

**Real-life analogy:** Props are like a letter you receive in the mail. You can read it, you can use the information in it, but you should not change what the letter says. If you need to respond, you write a new letter (which in React means calling a function that was passed to you via props — we will learn about this pattern soon).

### Props vs State (Preview)

You might wonder: if props are read-only, how does anything change in a React app? That is where **state** comes in (covered in Chapter 5).

Here is the difference in brief:

| Props | State |
|-------|-------|
| Passed from parent | Managed internally |
| Read-only in the component | Can be updated by the component |
| Changing props causes re-render | Changing state causes re-render |
| Like function parameters | Like local variables that persist |

A component's props are decided by its parent. A component's state is decided by itself. When either props or state change, the component re-renders with the new values.

---

## One-Way Data Flow

React uses a **one-way data flow** model, also called "unidirectional data flow." Data flows in only one direction: from parent to child, through props.

```
     App (data lives here)
      │
      │ passes data via props
      ▼
    Parent Component
      │
      │ passes data via props
      ▼
    Child Component
```

A child component cannot directly send data up to a parent. If a child needs to communicate with its parent, the parent passes a **function** as a prop, and the child calls that function:

```
     App
      │
      │ passes data DOWN via props
      │ passes function DOWN via props
      ▼
    Child Component
      │
      │ calls function to send data UP
      ▲
```

Here is a concrete example:

```jsx
function App() {
  function handleMessage(message) {
    alert("Message from child: " + message);
  }

  return <Child onSendMessage={handleMessage} />;
}

function Child({ onSendMessage }) {
  return (
    <button onClick={() => onSendMessage("Hello from the child!")}>
      Send Message to Parent
    </button>
  );
}
```

**What this code does:**
1. `App` defines `handleMessage` — a function that shows an alert.
2. `App` passes this function to `Child` via the `onSendMessage` prop.
3. `Child` calls `onSendMessage("Hello from the child!")` when the button is clicked.
4. This triggers `handleMessage` in `App`, which shows the alert.

The child does not directly modify anything in the parent. It calls a function that the parent provided. The parent stays in control.

**Why one-way flow?**

- **Predictability**: You can trace where any piece of data comes from by following the props chain upward.
- **Debugging**: If something displays incorrectly, you check the component that owns the data and the props it passes.
- **No surprises**: A component cannot be changed unexpectedly by its children — it controls what data goes down.

---

## Spreading Props

Sometimes you have an object whose properties match the props a component expects. Instead of passing each property individually, you can **spread** the object:

```jsx
function App() {
  const userProps = {
    name: "Alice",
    role: "Developer",
    email: "alice@example.com",
    isActive: true,
  };

  // Without spread — passing each prop individually
  return (
    <UserCard
      name={userProps.name}
      role={userProps.role}
      email={userProps.email}
      isActive={userProps.isActive}
    />
  );

  // With spread — much shorter
  return <UserCard {...userProps} />;
}

function UserCard({ name, role, email, isActive }) {
  return (
    <div>
      <h2>{name} {isActive && "✓"}</h2>
      <p>{role}</p>
      <p>{email}</p>
    </div>
  );
}
```

**What `{...userProps}` does:** The spread operator `...` unpacks the object so each key-value pair becomes a separate prop. `{...userProps}` is the same as writing `name="Alice" role="Developer" email="alice@example.com" isActive={true}`.

### Spread with Overrides

You can spread an object and override specific properties:

```jsx
const defaultStyles = {
  color: "blue",
  size: "medium",
  variant: "outlined",
};

// Spread defaults, then override color
<Button {...defaultStyles} color="red" />
// Result: color="red", size="medium", variant="outlined"
```

Props listed after the spread override the spread values. Props listed before the spread get overridden by the spread values. Order matters:

```jsx
// color="red" is overridden by {...defaultStyles} which has color="blue"
<Button color="red" {...defaultStyles} />
// Result: color="blue", size="medium", variant="outlined"

// {...defaultStyles} provides color="blue", then color="red" overrides it
<Button {...defaultStyles} color="red" />
// Result: color="red", size="medium", variant="outlined"
```

### A Word of Caution About Spread

While spreading is convenient, overusing it can make your code harder to understand:

```jsx
// ❌ Hard to tell what props Component receives
<Component {...objectA} {...objectB} {...objectC} />

// ✅ Better: be explicit about what you pass
<Component
  name={objectA.name}
  email={objectB.email}
  role={objectC.role}
/>
```

Use spread when it genuinely simplifies your code (like passing through props to a child). Avoid it when it obscures what data is being passed.

---

## Building a Component Tree

Real applications are trees of components. Each component can contain other components, which can contain other components, and so on. Understanding this tree structure is essential.

### Thinking in Components

Let us look at a product listing page and break it down:

```
Product Page
├── Navbar
│   ├── Logo
│   ├── SearchBar
│   └── NavLinks
├── FilterBar
│   ├── CategoryFilter
│   └── PriceFilter
├── ProductGrid
│   ├── ProductCard
│   │   ├── ProductImage
│   │   ├── ProductInfo
│   │   └── AddToCartButton
│   ├── ProductCard
│   │   ├── ProductImage
│   │   ├── ProductInfo
│   │   └── AddToCartButton
│   └── ProductCard
│       ├── ProductImage
│       ├── ProductInfo
│       └── AddToCartButton
└── Footer
```

Each item in this tree is a component. The top-level component (`ProductPage`) contains all the others. Each component can be developed, tested, and reused independently.

### How to Decide What Should Be a Component

Use these guidelines:

1. **Single Responsibility**: A component should do one thing. If it is doing too many things, split it.

2. **Reusability**: If a piece of UI appears in multiple places, it should be its own component. A `Button` used across pages should be a component.

3. **Complexity**: If a section of JSX is getting long and hard to read, extract it into a component — even if it is used only once.

4. **Data boundaries**: If a section of UI uses a distinct set of data, it might be a good candidate for its own component.

Here is a practical example. This component is too large:

```jsx
// ❌ Too much in one component
function App() {
  const user = { name: "Alice", avatar: "alice.jpg" };
  const menuItems = ["Home", "About", "Contact"];

  return (
    <div>
      {/* Navigation section */}
      <nav style={{ display: "flex", justifyContent: "space-between", padding: "1rem" }}>
        <img src="logo.png" alt="Logo" style={{ height: "40px" }} />
        <ul style={{ display: "flex", listStyle: "none", gap: "1rem" }}>
          {menuItems.map((item) => (
            <li key={item}>
              <a href={`/${item.toLowerCase()}`}>{item}</a>
            </li>
          ))}
        </ul>
        <div>
          <img src={user.avatar} alt={user.name} style={{ height: "32px", borderRadius: "50%" }} />
          <span>{user.name}</span>
        </div>
      </nav>

      {/* Hero section */}
      <section style={{ textAlign: "center", padding: "4rem 2rem" }}>
        <h1>Welcome to Our Platform</h1>
        <p>Build amazing things with React</p>
        <button style={{ padding: "0.75rem 2rem", fontSize: "1rem" }}>Get Started</button>
      </section>

      {/* Footer */}
      <footer style={{ textAlign: "center", padding: "2rem", backgroundColor: "#333", color: "white" }}>
        <p>© 2024 Our Company. All rights reserved.</p>
      </footer>
    </div>
  );
}
```

Let us refactor it into smaller, focused components:

```jsx
// ✅ Broken into focused components

function Logo() {
  return <img src="logo.png" alt="Logo" style={{ height: "40px" }} />;
}

function NavMenu({ items }) {
  return (
    <ul style={{ display: "flex", listStyle: "none", gap: "1rem" }}>
      {items.map((item) => (
        <li key={item}>
          <a href={`/${item.toLowerCase()}`}>{item}</a>
        </li>
      ))}
    </ul>
  );
}

function UserAvatar({ name, avatar }) {
  return (
    <div>
      <img src={avatar} alt={name} style={{ height: "32px", borderRadius: "50%" }} />
      <span>{name}</span>
    </div>
  );
}

function Navbar({ user, menuItems }) {
  return (
    <nav style={{ display: "flex", justifyContent: "space-between", padding: "1rem" }}>
      <Logo />
      <NavMenu items={menuItems} />
      <UserAvatar name={user.name} avatar={user.avatar} />
    </nav>
  );
}

function Hero() {
  return (
    <section style={{ textAlign: "center", padding: "4rem 2rem" }}>
      <h1>Welcome to Our Platform</h1>
      <p>Build amazing things with React</p>
      <button style={{ padding: "0.75rem 2rem", fontSize: "1rem" }}>Get Started</button>
    </section>
  );
}

function Footer() {
  return (
    <footer style={{ textAlign: "center", padding: "2rem", backgroundColor: "#333", color: "white" }}>
      <p>© 2024 Our Company. All rights reserved.</p>
    </footer>
  );
}

function App() {
  const user = { name: "Alice", avatar: "alice.jpg" };
  const menuItems = ["Home", "About", "Contact"];

  return (
    <div>
      <Navbar user={user} menuItems={menuItems} />
      <Hero />
      <Footer />
    </div>
  );
}
```

**What changed and why:**
- The `App` component went from 30+ lines of mixed HTML to 5 clear lines that read like a description of the page.
- Each component has one job: `Logo` shows the logo, `NavMenu` renders navigation links, `UserAvatar` displays the user info.
- `Navbar` composes smaller components together. It passes data down through props.
- If you need to change the footer, you go to `Footer`. If the navigation menu needs a new style, you edit `NavMenu`. Nothing else is affected.

---

## Composition Over Inheritance

In some programming languages and frameworks, you extend (inherit from) base components to create specialized versions. React does not use this approach. Instead, React uses **composition** — building complex components by combining simpler ones.

### What Composition Looks Like

```jsx
function Dialog({ title, children }) {
  return (
    <div style={{
      position: "fixed",
      top: "50%",
      left: "50%",
      transform: "translate(-50%, -50%)",
      backgroundColor: "white",
      padding: "2rem",
      borderRadius: "8px",
      boxShadow: "0 4px 20px rgba(0,0,0,0.3)",
      minWidth: "300px",
    }}>
      <h2>{title}</h2>
      <div>{children}</div>
    </div>
  );
}

// Specialized version: a confirmation dialog
function ConfirmDialog({ title, message, onConfirm, onCancel }) {
  return (
    <Dialog title={title}>
      <p>{message}</p>
      <div style={{ display: "flex", gap: "0.5rem", marginTop: "1rem" }}>
        <button onClick={onCancel}>Cancel</button>
        <button onClick={onConfirm} style={{ backgroundColor: "blue", color: "white" }}>
          Confirm
        </button>
      </div>
    </Dialog>
  );
}

// Specialized version: an alert dialog
function AlertDialog({ title, message, onClose }) {
  return (
    <Dialog title={title}>
      <p>{message}</p>
      <button onClick={onClose} style={{ marginTop: "1rem" }}>
        OK
      </button>
    </Dialog>
  );
}
```

**What this code does:** `Dialog` is a generic component that provides the visual container (positioning, styling, shadow). `ConfirmDialog` and `AlertDialog` are not created by inheriting from `Dialog` — they are created by **using** `Dialog` and passing it specific content through `children` and props.

This is composition: simple components combined to create more complex ones. You will see this pattern throughout React.

---

## A Complete Practical Example

Let us build a contact card list using everything from this chapter:

```jsx
// Avatar.jsx
function Avatar({ src, name, size = 64 }) {
  return (
    <img
      src={src}
      alt={`${name}'s avatar`}
      style={{
        width: size,
        height: size,
        borderRadius: "50%",
        objectFit: "cover",
      }}
    />
  );
}

export default Avatar;
```

```jsx
// Badge.jsx
function Badge({ children, color = "#3182ce" }) {
  return (
    <span
      style={{
        display: "inline-block",
        backgroundColor: color,
        color: "white",
        padding: "2px 8px",
        borderRadius: "12px",
        fontSize: "12px",
        fontWeight: "bold",
      }}
    >
      {children}
    </span>
  );
}

export default Badge;
```

```jsx
// ContactCard.jsx
import Avatar from "./Avatar";
import Badge from "./Badge";

function ContactCard({ contact }) {
  const { name, email, phone, avatar, department, isOnline } = contact;

  return (
    <div
      style={{
        display: "flex",
        gap: "1rem",
        padding: "1rem",
        border: "1px solid #e2e8f0",
        borderRadius: "8px",
        alignItems: "center",
      }}
    >
      <div style={{ position: "relative" }}>
        <Avatar src={avatar} name={name} />
        {isOnline && (
          <span
            style={{
              position: "absolute",
              bottom: 2,
              right: 2,
              width: 12,
              height: 12,
              backgroundColor: "#38a169",
              borderRadius: "50%",
              border: "2px solid white",
            }}
          />
        )}
      </div>

      <div style={{ flex: 1 }}>
        <h3 style={{ margin: "0 0 4px 0" }}>
          {name} <Badge>{department}</Badge>
        </h3>
        <p style={{ margin: "0 0 2px 0", color: "#718096", fontSize: "14px" }}>
          {email}
        </p>
        <p style={{ margin: 0, color: "#718096", fontSize: "14px" }}>
          {phone}
        </p>
      </div>
    </div>
  );
}

export default ContactCard;
```

```jsx
// ContactList.jsx
import ContactCard from "./ContactCard";

function ContactList({ contacts, title = "Contacts" }) {
  return (
    <div>
      <h2>
        {title} ({contacts.length})
      </h2>

      {contacts.length === 0 ? (
        <p style={{ color: "#a0aec0", fontStyle: "italic" }}>
          No contacts to display.
        </p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {contacts.map((contact) => (
            <ContactCard key={contact.id} contact={contact} />
          ))}
        </div>
      )}
    </div>
  );
}

export default ContactList;
```

```jsx
// App.jsx
import ContactList from "./ContactList";

function App() {
  const contacts = [
    {
      id: 1,
      name: "Alice Johnson",
      email: "alice@company.com",
      phone: "+1 (555) 123-4567",
      avatar: "https://i.pravatar.cc/150?img=1",
      department: "Engineering",
      isOnline: true,
    },
    {
      id: 2,
      name: "Bob Smith",
      email: "bob@company.com",
      phone: "+1 (555) 234-5678",
      avatar: "https://i.pravatar.cc/150?img=3",
      department: "Design",
      isOnline: false,
    },
    {
      id: 3,
      name: "Charlie Brown",
      email: "charlie@company.com",
      phone: "+1 (555) 345-6789",
      avatar: "https://i.pravatar.cc/150?img=5",
      department: "Marketing",
      isOnline: true,
    },
    {
      id: 4,
      name: "Diana Ross",
      email: "diana@company.com",
      phone: "+1 (555) 456-7890",
      avatar: "https://i.pravatar.cc/150?img=9",
      department: "Engineering",
      isOnline: false,
    },
  ];

  return (
    <div style={{ maxWidth: "600px", margin: "2rem auto", padding: "0 1rem" }}>
      <h1>Company Directory</h1>
      <ContactList contacts={contacts} title="Team Members" />
    </div>
  );
}

export default App;
```

**Component tree for this example:**

```
App
└── ContactList
    ├── ContactCard (Alice)
    │   ├── Avatar
    │   └── Badge
    ├── ContactCard (Bob)
    │   ├── Avatar
    │   └── Badge
    ├── ContactCard (Charlie)
    │   ├── Avatar
    │   └── Badge
    └── ContactCard (Diana)
        ├── Avatar
        └── Badge
```

**Data flow:**

```
App (owns the contacts data)
 │
 │ passes contacts array + title
 ▼
ContactList
 │
 │ passes individual contact object
 ▼
ContactCard
 │
 │ passes src, name, size     passes children (text)
 ▼                            ▼
Avatar                       Badge
```

Each component receives only the data it needs. `Avatar` does not know about emails or phone numbers — it only knows about image source, name, and size. `Badge` does not know what kind of label it displays — it just renders whatever children it receives in a styled pill shape.

---

## Component Naming Conventions

Following consistent naming conventions makes your code predictable and easy to navigate:

1. **Component names**: PascalCase (first letter of each word capitalized).

   ```
   ✅ UserProfile, ShoppingCart, LoginForm, NavBar
   ❌ userProfile, shopping_cart, loginform
   ```

2. **File names**: Match the component name. Use PascalCase or kebab-case (both are common).

   ```
   ✅ UserProfile.jsx (PascalCase — most common)
   ✅ user-profile.jsx (kebab-case — also popular)
   ❌ userprofile.jsx, user_profile.jsx
   ```

3. **Props names**: camelCase, like regular JavaScript variables.

   ```jsx
   ✅ <Card userName="Alice" onClick={handleClick} isVisible={true} />
   ❌ <Card UserName="Alice" on-click={handleClick} is_visible={true} />
   ```

4. **Event handler props**: Start with `on` (to describe the event).

   ```jsx
   ✅ onClick, onSubmit, onChange, onDelete, onToggle
   ```

5. **Event handler functions**: Start with `handle` (to describe the action).

   ```jsx
   ✅ handleClick, handleSubmit, handleChange, handleDelete
   ```

   The convention pairs nicely:

   ```jsx
   <Button onClick={handleClick} />
   <Form onSubmit={handleSubmit} />
   <Input onChange={handleChange} />
   ```

6. **Boolean props**: Start with `is`, `has`, `should`, or `can`.

   ```jsx
   ✅ isOpen, isActive, hasError, shouldRender, canEdit
   ❌ open, active, error, render, edit
   ```

---

## Common Mistakes

1. **Forgetting to capitalize component names.**

   ```jsx
   // ❌ React treats lowercase as HTML element
   function greeting() {
     return <h1>Hello</h1>;
   }
   <greeting /> // Renders nothing useful — treated as unknown HTML tag

   // ✅ Capitalize it
   function Greeting() {
     return <h1>Hello</h1>;
   }
   <Greeting /> // Works correctly
   ```

2. **Modifying props directly.**

   ```jsx
   // ❌ Never mutate props
   function UserCard({ user }) {
     user.name = user.name.toUpperCase(); // Mutates the original object!
     return <h2>{user.name}</h2>;
   }

   // ✅ Create a new value
   function UserCard({ user }) {
     const displayName = user.name.toUpperCase();
     return <h2>{displayName}</h2>;
   }
   ```

3. **Passing the wrong type and not noticing.**

   ```jsx
   // ❌ Passing a string where a number is expected
   <ProgressBar percentage="75" />

   // Inside ProgressBar: percentage + 10 gives "7510" instead of 85!

   // ✅ Pass the correct type
   <ProgressBar percentage={75} />
   ```

4. **Destructuring a prop that was not passed.**

   ```jsx
   // ❌ If "items" is not passed, items.map() will crash
   function ItemList({ items }) {
     return items.map((item) => <li key={item.id}>{item.name}</li>);
   }

   // ✅ Use a default value
   function ItemList({ items = [] }) {
     return items.map((item) => <li key={item.id}>{item.name}</li>);
   }
   ```

5. **Creating components inside other components.**

   ```jsx
   // ❌ BAD: Component defined inside another component
   function App() {
     function Button() {  // This is recreated on every render!
       return <button>Click me</button>;
     }

     return <Button />;
   }

   // ✅ GOOD: Define components at the top level
   function Button() {
     return <button>Click me</button>;
   }

   function App() {
     return <Button />;
   }
   ```

   **Why this matters:** When a component is defined inside another component, it is recreated as a new function on every render. React sees it as a completely new component each time, so it unmounts and remounts it — losing all state and causing performance issues. Always define components at the top level of a file.

6. **Not providing a key when rendering a list of components.**

   ```jsx
   // ❌ Missing key
   {users.map((user) => (
     <UserCard name={user.name} />
   ))}

   // ✅ Always include key on the outermost element
   {users.map((user) => (
     <UserCard key={user.id} name={user.name} />
   ))}
   ```

---

## Best Practices

1. **Keep components small and focused.** A component that does one thing is easier to understand, test, and reuse than one that does ten things. If a component exceeds 100-150 lines, consider splitting it.

2. **Use destructuring for props.** It makes your component signatures clear and your JSX cleaner.

   ```jsx
   // ✅ Clear what props this component accepts
   function UserCard({ name, email, role, isActive }) { ... }
   ```

3. **Provide default values for optional props.** This prevents undefined errors and makes components more robust.

   ```jsx
   function Avatar({ src, size = 48, alt = "User avatar" }) { ... }
   ```

4. **Use composition over complex conditional rendering.** Instead of one component with many conditions, create specialized components that compose a shared base.

5. **Keep the component tree reasonably shallow.** If you have more than 5-6 levels of nesting, you might be over-componentizing. Not every `<div>` needs to be its own component.

6. **Put shared components in a `components` folder.** Components used across multiple pages go in `src/components/`. Page-specific components can live near their page.

   ```
   src/
   ├── components/         # Shared, reusable components
   │   ├── Button.jsx
   │   ├── Avatar.jsx
   │   └── Badge.jsx
   ├── pages/              # Page-level components
   │   ├── Home.jsx
   │   └── Profile.jsx
   └── App.jsx
   ```

7. **Name event handler props with `on` and handler functions with `handle`.** This creates a consistent, predictable pattern throughout your codebase.

8. **Use the `children` prop for wrapper/layout components.** If a component provides structure or decoration around content, `children` is the right pattern.

---

## Summary

In this chapter, you learned:

- **Components** are reusable, independent pieces of UI defined as JavaScript functions that return JSX. They are the fundamental building blocks of React applications.
- Component names **must start with a capital letter** so React can distinguish them from HTML elements.
- **Props** are inputs to a component — data passed from a parent to a child through attributes. They make components dynamic and reusable.
- **Props are read-only.** A component must never modify the props it receives.
- **Destructuring** props in the function parameter makes code cleaner and immediately reveals what props a component expects.
- **Default values** can be set in the destructuring pattern for optional props.
- You can pass any JavaScript value as a prop: strings, numbers, booleans, objects, arrays, functions, and even JSX.
- The **`children` prop** is a special prop that represents the content placed between a component's opening and closing tags.
- React uses **one-way data flow** — data flows from parent to child through props. Children communicate upward by calling functions that parents pass down as props.
- **Composition** (combining components) is React's preferred pattern over inheritance for creating specialized or complex components.
- Components should be **small, focused, and defined at the top level** of a file — never inside another component.

---

## Interview Questions

**Q1: What is a React component?**

A React component is a reusable, self-contained piece of UI. In modern React, it is a JavaScript function that accepts an optional props object and returns JSX describing what should appear on screen. Components let you split the UI into independent, modular pieces that can be developed, tested, and reasoned about in isolation. Components can be composed together to build complex interfaces.

**Q2: What are props in React?**

Props (short for properties) are the mechanism for passing data from a parent component to a child component. They are read-only inputs that the child component uses to determine what to render. Props are passed as attributes in JSX (`<Component name="Alice" />`) and received as a single object parameter in the component function. The child must not modify its props — they are owned by the parent.

**Q3: Why must component names start with a capital letter?**

React uses the casing of the tag name to determine whether it is a built-in HTML element or a custom component. Lowercase names like `<div>` and `<span>` are treated as native HTML elements and rendered as DOM nodes. Names starting with an uppercase letter like `<Greeting>` and `<UserCard>` are treated as React components — React calls the corresponding function and renders the JSX it returns. If you name a component with a lowercase letter, React will try to render it as an HTML element, which will not work correctly.

**Q4: What is the difference between props and state?**

Props are external — passed to a component by its parent. They are read-only and the component cannot modify them. State is internal — created and managed within the component itself. The component can update its own state. Both cause a re-render when they change, but they serve different purposes: props make components configurable from outside, while state lets components track and respond to changes internally (like user input, API responses, or toggle states).

**Q5: Explain one-way data flow in React.**

React follows a unidirectional data flow pattern where data flows only in one direction: from parent components to child components through props. A child cannot directly modify data in its parent. If a child needs to communicate upward, the parent passes a callback function as a prop, and the child calls that function with the relevant data. This makes data flow predictable and debugging easier because you can always trace where a piece of data came from by following the props chain upward.

**Q6: What is the `children` prop and when would you use it?**

The `children` prop is a special, built-in prop that contains whatever JSX is placed between a component's opening and closing tags. For example, in `<Card><p>Hello</p></Card>`, the `<p>Hello</p>` is passed as `children` to `Card`. You use the `children` prop when building wrapper or layout components that need to render arbitrary content without knowing what that content will be — things like modals, cards, sidebars, page layouts, and error boundaries.

**Q7: What does it mean that props are read-only?**

When React says props are read-only, it means a component must treat its props as immutable — it must never change, reassign, or mutate them. This is a fundamental rule because props are owned by the parent component. If a child modifies a prop (especially an object or array), it could change the data in the parent without the parent knowing, leading to bugs and unpredictable behavior. If a component needs a modified version of a prop value, it should create a new variable derived from the prop.

**Q8: Why should you not define a component inside another component?**

When a component is defined inside another component's function body, it is recreated as a brand-new function every time the outer component re-renders. React compares component types between renders using reference equality — since it is a new function each time, React treats it as a completely different component. This means React unmounts the old instance (destroying its state and DOM) and mounts a new one, every single render. This causes state loss, DOM thrashing, loss of focus in inputs, and poor performance. Always define components at the module level (top level of the file).

**Q9: What is composition in React and why is it preferred over inheritance?**

Composition means building complex components by combining simpler ones — typically by passing components or JSX as props (including `children`). For example, a `Dialog` component takes content through `children`, and a `ConfirmDialog` is built by using `Dialog` and passing it specific content. React prefers composition over inheritance because it is more flexible: any component can be used inside any other component, props can be any type including JSX, and you do not end up with rigid class hierarchies. The React team explicitly recommends composition and states they have not found use cases where inheritance would be better.

---

## Practice Exercises

**Exercise 1: Create a Reusable Button Component**

Create a `Button` component that accepts these props:
- `text` — the button label (default: "Click")
- `variant` — "primary", "secondary", or "danger" (default: "primary")
- `size` — "small", "medium", or "large" (default: "medium")
- `disabled` — boolean (default: false)
- `onClick` — function to call when clicked

Use the variant to determine the background color (blue, gray, red). Use the size to determine padding and font size. Render several buttons in `App` with different combinations of props.

**Exercise 2: Build a Testimonial Card**

Create a `TestimonialCard` component that displays:
- A profile avatar (use a placeholder image)
- The person's name
- Their job title and company
- A star rating (1-5)
- The testimonial text

Render at least 3 testimonial cards with different data in `App`.

**Exercise 3: Component Decomposition**

Take this single-component code and break it into at least 5 smaller components. Identify what props each component needs:

```jsx
function App() {
  const recipe = {
    title: "Chocolate Chip Cookies",
    prepTime: "15 min",
    cookTime: "12 min",
    servings: 24,
    difficulty: "Easy",
    rating: 4.8,
    ingredients: [
      "2 cups flour",
      "1 cup butter",
      "3/4 cup sugar",
      "2 eggs",
      "1 tsp vanilla",
      "2 cups chocolate chips",
    ],
    steps: [
      "Preheat oven to 375°F",
      "Mix flour, butter, and sugar",
      "Add eggs and vanilla",
      "Fold in chocolate chips",
      "Drop spoonfuls onto baking sheet",
      "Bake for 10-12 minutes",
    ],
  };

  return (
    <div>
      <h1>{recipe.title}</h1>
      <div>
        <span>Prep: {recipe.prepTime}</span>
        <span>Cook: {recipe.cookTime}</span>
        <span>Servings: {recipe.servings}</span>
        <span>Difficulty: {recipe.difficulty}</span>
        <span>Rating: {recipe.rating}/5</span>
      </div>
      <h2>Ingredients</h2>
      <ul>
        {recipe.ingredients.map((item, index) => (
          <li key={index}>{item}</li>
        ))}
      </ul>
      <h2>Instructions</h2>
      <ol>
        {recipe.steps.map((step, index) => (
          <li key={index}>{step}</li>
        ))}
      </ol>
    </div>
  );
}
```

Suggested components: `RecipeHeader`, `RecipeMetadata`, `IngredientList`, `InstructionList`, `RecipePage`

**Exercise 4: Composition Practice**

Create a `Card` component that uses `children` for its content. Then create three specialized card components using composition (not by modifying `Card`):
- `InfoCard` — has a blue left border and an info icon
- `WarningCard` — has a yellow left border and a warning icon
- `ErrorCard` — has a red left border and an error icon

Each specialized card should use `Card` internally and add its own styling and icon.

**Exercise 5: Building a Navigation Bar**

Create a navigation bar with the following components:
- `Navbar` — the container
- `NavBrand` — shows the logo/site name
- `NavLinks` — renders a list of navigation links
- `NavLink` — a single navigation link (receives `href` and `label` as props, and an `isActive` boolean)

Pass an array of link objects to `NavLinks`. Highlight the active link with a different color. Use the `children` prop where it makes sense.

**Exercise 6: Props Drilling Visualization**

Create a component tree that is 4 levels deep:
- `App` → `Dashboard` → `UserSection` → `UserGreeting`
- `App` has the user data
- `UserGreeting` (at the bottom) needs to display the user's name

Pass the data through each level using props. Notice how every intermediate component must accept and forward the prop, even though `Dashboard` and `UserSection` do not use the user data themselves. This is called "prop drilling" — we will learn how to solve it in Chapter 14 (Context API).

---

## What Is Next?

You now understand the two most fundamental concepts in React: components and props. You can create reusable UI pieces and pass data between them.

But our components are still static — once they render, they cannot change. In Chapter 5, we will learn about **State and the useState Hook**, which lets components remember and update information. This is where your applications start becoming truly interactive.
