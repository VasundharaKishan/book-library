# Chapter 3: JSX In Depth

---

## Learning Goals

By the end of this chapter, you will be able to:

- Explain what JSX is and how it differs from HTML
- Understand how JSX transforms into JavaScript function calls
- Use JavaScript expressions inside JSX
- Apply all JSX rules correctly (single root, closing tags, attribute names)
- Use Fragments to avoid unnecessary wrapper elements
- Render content conditionally using multiple techniques
- Render lists of items from arrays
- Write comments in JSX
- Avoid the most common JSX mistakes
- Feel confident writing any UI structure with JSX

---

## What Is JSX?

JSX stands for **JavaScript XML**. It is a syntax extension for JavaScript that lets you write HTML-like code inside JavaScript files. It was created by the React team to make it easier to describe what the UI should look like.

Here is a simple example:

```jsx
const element = <h1>Hello, World!</h1>;
```

This looks like HTML, but it is actually JavaScript. It is JSX. The browser cannot understand this line directly. Before this code runs in the browser, a build tool (Vite, in our case) transforms it into regular JavaScript.

### JSX Is Not HTML

This is one of the most important things to understand early. JSX looks very similar to HTML, and that similarity is intentional — it makes JSX easy to read and write. But JSX is not HTML. It is a syntax that gets converted into JavaScript function calls.

Let us see what JSX actually becomes after transformation.

### What JSX Compiles To

When Vite processes your JSX, it transforms it into `React.createElement()` function calls. Here is the before and after:

**What you write (JSX):**

```jsx
const element = <h1 className="title">Hello, World!</h1>;
```

**What the browser receives (JavaScript):**

```javascript
const element = React.createElement("h1", { className: "title" }, "Hello, World!");
```

A more complex example:

**JSX:**

```jsx
const card = (
  <div className="card">
    <h2>React</h2>
    <p>A JavaScript library for building UIs</p>
  </div>
);
```

**Compiled JavaScript:**

```javascript
const card = React.createElement(
  "div",
  { className: "card" },
  React.createElement("h2", null, "React"),
  React.createElement("p", null, "A JavaScript library for building UIs")
);
```

As you can see, writing JSX is much cleaner and more readable than writing `React.createElement()` calls manually. That is the entire purpose of JSX — it is syntactic sugar that makes your life easier.

The `React.createElement()` function takes three types of arguments:

1. **The element type** — a string like `"div"`, `"h1"`, `"p"`, or a React component
2. **The props** — an object of attributes (or `null` if there are none)
3. **The children** — the content inside the element (text, other elements, or both)

```
React.createElement(type, props, ...children)

React.createElement(
  "div",                      ← type: what element to create
  { className: "card" },      ← props: attributes/properties
  React.createElement(        ← children: what goes inside
    "h2",
    null,
    "React"
  ),
  React.createElement(
    "p",
    null,
    "A JavaScript library"
  )
)
```

You will almost never write `React.createElement()` directly — JSX handles it for you. But understanding this transformation helps you debug errors and understand why JSX has certain rules.

### Why Not Just Use HTML?

You might wonder: "If JSX is so similar to HTML, why not just use actual HTML?"

The reason is that JSX lives inside JavaScript, which gives it superpowers that HTML does not have:

1. **Dynamic content**: You can embed any JavaScript expression inside JSX.
2. **Conditional rendering**: You can show or hide content based on conditions.
3. **List generation**: You can generate UI from arrays of data.
4. **Component composition**: You can use your own components just like HTML tags.

HTML is static — what you write is what appears on the screen. JSX is dynamic — it can change based on data, user actions, and application state.

---

## JSX Rules

JSX has a set of rules that differ from HTML. Let us go through each one carefully.

### Rule 1: Return a Single Root Element

A component must return a single root element. You cannot return multiple elements side by side.

**This is wrong:**

```jsx
// ❌ Error: Adjacent JSX elements must be wrapped in an enclosing tag
function Greeting() {
  return (
    <h1>Hello</h1>
    <p>Welcome to React</p>
  );
}
```

**This is correct:**

```jsx
// ✅ Wrapped in a single parent element
function Greeting() {
  return (
    <div>
      <h1>Hello</h1>
      <p>Welcome to React</p>
    </div>
  );
}
```

**Why this rule exists:**

Remember that JSX compiles to `React.createElement()` calls. A function can only return one value. The JSX `<h1>` and `<p>` would each become separate `React.createElement()` calls, and you cannot return two values from a function without wrapping them.

```javascript
// This is what returning two elements would look like in JavaScript:
return React.createElement("h1", null, "Hello")  // ← first value
       React.createElement("p", null, "Welcome") // ← second value???

// JavaScript cannot return two values. You need a wrapper:
return React.createElement("div", null,
  React.createElement("h1", null, "Hello"),
  React.createElement("p", null, "Welcome")
);
```

But what if you do not want an extra `<div>` in your HTML output? That is where Fragments come in (we will cover those shortly).

### Rule 2: Close All Tags

In HTML, some tags are self-closing — you can write `<img src="photo.jpg">` or `<br>` or `<input type="text">` without a closing tag.

In JSX, **every tag must be closed**. Self-closing tags must end with `/>`.

**HTML (valid):**

```html
<img src="photo.jpg">
<br>
<input type="text">
<hr>
```

**JSX (must close all tags):**

```jsx
<img src="photo.jpg" />
<br />
<input type="text" />
<hr />
```

If you forget the closing slash, you will get an error:

```
// ❌ Error: Expected corresponding JSX closing tag for <img>
<img src="photo.jpg">
```

Tags with content must have both opening and closing tags:

```jsx
// ✅ Correct
<div>Content</div>
<p>Text here</p>

// ❌ Wrong: missing closing tag
<div>Content
```

### Rule 3: Use camelCase for Most Attributes

HTML attributes use lowercase or hyphenated names. JSX uses **camelCase** because JSX attributes become JavaScript object properties, and JavaScript properties are conventionally camelCase.

Here are the most common differences:

| HTML Attribute | JSX Attribute | Why |
|---------------|--------------|-----|
| `class` | `className` | `class` is a reserved word in JavaScript |
| `for` | `htmlFor` | `for` is a reserved word in JavaScript |
| `tabindex` | `tabIndex` | camelCase convention |
| `onclick` | `onClick` | camelCase convention |
| `onchange` | `onChange` | camelCase convention |
| `onsubmit` | `onSubmit` | camelCase convention |
| `maxlength` | `maxLength` | camelCase convention |
| `readonly` | `readOnly` | camelCase convention |
| `autofocus` | `autoFocus` | camelCase convention |
| `autocomplete` | `autoComplete` | camelCase convention |

The two most important ones to remember are `className` (instead of `class`) and `htmlFor` (instead of `for`), because `class` and `for` are reserved keywords in JavaScript.

```jsx
// ❌ Wrong: using HTML attributes
<div class="container">
  <label for="email">Email</label>
  <input id="email" tabindex="1" readonly>
</div>

// ✅ Correct: using JSX attributes
<div className="container">
  <label htmlFor="email">Email</label>
  <input id="email" tabIndex="1" readOnly />
</div>
```

**Exception: `data-*` and `aria-*` attributes**

Custom data attributes (`data-id`, `data-testid`) and accessibility attributes (`aria-label`, `aria-hidden`) keep their hyphenated format in JSX:

```jsx
<div data-testid="user-card" aria-label="User profile card">
  Content
</div>
```

### Rule 4: Use the `style` Attribute with a JavaScript Object

In HTML, the `style` attribute takes a CSS string. In JSX, it takes a JavaScript object with camelCase property names.

**HTML:**

```html
<div style="background-color: blue; font-size: 16px; margin-top: 20px;">
  Styled content
</div>
```

**JSX:**

```jsx
<div style={{ backgroundColor: "blue", fontSize: "16px", marginTop: "20px" }}>
  Styled content
</div>
```

Notice the **double curly braces** `{{ }}`. This is not special syntax — it is two things:
1. The outer `{}` means "here is a JavaScript expression" (which we will cover next).
2. The inner `{}` is a regular JavaScript object literal.

```jsx
// These are equivalent:
<div style={{ color: "red" }}>Text</div>

// Breaking it down:
const myStyles = { color: "red" };
<div style={myStyles}>Text</div>
```

**CSS property name conversion rules:**
- Hyphenated names become camelCase: `background-color` → `backgroundColor`
- Vendor prefixes are also camelCase: `-webkit-transform` → `WebkitTransform`
- Numeric values for pixel-based properties can be numbers: `fontSize: 16` (React adds "px" automatically)
- Non-pixel numeric values must be strings: `lineHeight: "1.5"`, `opacity: 0.5` (opacity is unitless, so a number works)

```jsx
// React automatically adds "px" to numeric values for most properties
<div style={{
  fontSize: 16,      // becomes "16px"
  padding: 20,       // becomes "20px"
  lineHeight: 1.5,   // stays 1.5 (unitless property)
  opacity: 0.8,      // stays 0.8 (unitless property)
  zIndex: 10         // stays 10 (unitless property)
}}>
  Content
</div>
```

---

## JavaScript Expressions in JSX

One of JSX's most powerful features is the ability to embed JavaScript expressions directly in your markup using curly braces `{}`.

### The Curly Brace Rule

Whenever you see `{}` inside JSX, it means "evaluate this as JavaScript." You can put any valid JavaScript **expression** inside the curly braces.

**What is an expression?** An expression is any piece of code that produces a value. Examples:

- `2 + 2` → produces `4`
- `name` → produces the value of the variable `name`
- `user.firstName` → produces a property value
- `items.length` → produces a number
- `isLoggedIn ? "Welcome" : "Please log in"` → produces a string
- `formatDate(new Date())` → produces the return value of a function

**What is NOT an expression?** Statements do not produce values and cannot be used inside `{}`:

- `if (condition) { ... }` — use ternary operator instead
- `for (let i = 0; ...) { ... }` — use `.map()` instead
- `let x = 5` — variable declarations are not expressions
- `switch (value) { ... }` — use ternary or object lookup instead

### Using Variables

```jsx
function UserGreeting() {
  const userName = "Alice";
  const userAge = 28;

  return (
    <div>
      <h1>Hello, {userName}!</h1>
      <p>You are {userAge} years old.</p>
    </div>
  );
}
```

**What this code does:** The `{userName}` and `{userAge}` expressions are replaced with the values of those variables when the component renders. The output would be "Hello, Alice!" and "You are 28 years old."

**What would happen if done incorrectly:** If you wrote `userName` without curly braces, React would display the literal text "userName" instead of "Alice":

```jsx
// ❌ This renders the text "userName", not the value of the variable
<h1>Hello, userName!</h1>

// ✅ This renders "Alice"
<h1>Hello, {userName}!</h1>
```

### Using Object Properties

```jsx
function ProductCard() {
  const product = {
    name: "Wireless Headphones",
    price: 79.99,
    inStock: true,
  };

  return (
    <div>
      <h2>{product.name}</h2>
      <p>Price: ${product.price}</p>
      <p>Status: {product.inStock ? "In Stock" : "Out of Stock"}</p>
    </div>
  );
}
```

**What this code does:** Each `{}` expression accesses a property of the `product` object. The `$` before `{product.price}` is just a literal dollar sign character — it is not part of the JSX syntax. The ternary expression `product.inStock ? "In Stock" : "Out of Stock"` evaluates to one of two strings based on the boolean value.

### Using Function Calls

```jsx
function FormattedDate() {
  const now = new Date();

  function formatDate(date) {
    return date.toLocaleDateString("en-US", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  }

  return (
    <div>
      <p>Today is {formatDate(now)}</p>
      <p>The time is {now.toLocaleTimeString()}</p>
    </div>
  );
}
```

**What this code does:** The `{formatDate(now)}` expression calls the `formatDate` function and inserts its return value. The `{now.toLocaleTimeString()}` calls a method on the Date object. Any function that returns a renderable value (string, number, JSX) can be called inside curly braces.

### Using Math and String Operations

```jsx
function MathExample() {
  const width = 200;
  const height = 150;
  const firstName = "Alice";
  const lastName = "Johnson";

  return (
    <div>
      <p>Area: {width * height} square pixels</p>
      <p>Perimeter: {2 * (width + height)} pixels</p>
      <p>Full name: {firstName + " " + lastName}</p>
      <p>Uppercase: {firstName.toUpperCase()}</p>
      <p>Name length: {firstName.length} characters</p>
    </div>
  );
}
```

### Using Template Literals

You can use JavaScript template literals (backtick strings) inside JSX:

```jsx
function Welcome() {
  const name = "Alice";
  const role = "developer";

  return (
    <div>
      <p>{`Welcome, ${name}! You are a ${role}.`}</p>
      <img
        src={`https://api.example.com/avatar/${name.toLowerCase()}`}
        alt={`${name}'s avatar`}
      />
    </div>
  );
}
```

**What this code does:** Template literals are useful when you need to combine variables with strings, especially for dynamic attributes like `src` and `alt`. The outer `{}` tells JSX "this is JavaScript," and the backtick string with `${}` is standard JavaScript template literal syntax.

### What You Cannot Render in JSX

Not everything can be placed inside JSX. Here is what works and what does not:

```jsx
function RenderExamples() {
  const text = "Hello";           // ✅ Strings render as text
  const number = 42;              // ✅ Numbers render as text
  const decimal = 3.14;           // ✅ Numbers render as text
  const boolTrue = true;          // ⚠️ Booleans render NOTHING
  const boolFalse = false;        // ⚠️ Booleans render NOTHING
  const nothing = null;           // ⚠️ Null renders NOTHING
  const undef = undefined;        // ⚠️ Undefined renders NOTHING
  const arr = [1, 2, 3];          // ✅ Arrays render each item
  const obj = { key: "value" };   // ❌ Objects CANNOT be rendered

  return (
    <div>
      <p>{text}</p>          {/* Shows: Hello */}
      <p>{number}</p>        {/* Shows: 42 */}
      <p>{decimal}</p>       {/* Shows: 3.14 */}
      <p>{boolTrue}</p>      {/* Shows: (nothing) */}
      <p>{boolFalse}</p>     {/* Shows: (nothing) */}
      <p>{nothing}</p>       {/* Shows: (nothing) */}
      <p>{undef}</p>         {/* Shows: (nothing) */}
      <p>{arr}</p>           {/* Shows: 123 */}
      {/* <p>{obj}</p> */}   {/* ERROR: Objects are not valid as a React child */}
    </div>
  );
}
```

The fact that `false`, `null`, and `undefined` render nothing is actually very useful — it is the foundation of conditional rendering, which we will cover shortly.

**The object error** is a common mistake. If you try to render a plain JavaScript object, you will see:

```
Error: Objects are not valid as a React child
```

To display object data, access its individual properties:

```jsx
const user = { name: "Alice", age: 28 };

// ❌ This crashes
<p>{user}</p>

// ✅ Access individual properties
<p>{user.name} is {user.age} years old</p>

// ✅ Or convert to a string (useful for debugging)
<p>{JSON.stringify(user)}</p>
```

---

## Fragments

Earlier, we learned that JSX must return a single root element. This often leads to wrapping everything in a `<div>`:

```jsx
function UserInfo() {
  return (
    <div>    {/* This div exists only to satisfy the single-root rule */}
      <h1>Alice</h1>
      <p>Software Developer</p>
    </div>
  );
}
```

But sometimes that extra `<div>` causes problems — it adds an unnecessary node to the DOM, can break CSS layouts (especially Flexbox and Grid), and creates an inaccurate semantic structure.

**Fragments** solve this problem. A Fragment lets you group elements without adding an extra node to the DOM.

### Fragment Syntax

There are two ways to write Fragments:

**Long form:**

```jsx
import { Fragment } from "react";

function UserInfo() {
  return (
    <Fragment>
      <h1>Alice</h1>
      <p>Software Developer</p>
    </Fragment>
  );
}
```

**Short form (empty tags):**

```jsx
function UserInfo() {
  return (
    <>
      <h1>Alice</h1>
      <p>Software Developer</p>
    </>
  );
}
```

The short form `<>...</>` is used most of the time because it is cleaner. It produces the same result — the `<h1>` and `<p>` are rendered without any wrapper element.

### When to Use the Long Form

The long form `<Fragment>` is needed when you need to add a `key` attribute (which you will need when rendering lists):

```jsx
import { Fragment } from "react";

function Glossary({ terms }) {
  return (
    <dl>
      {terms.map(function (term) {
        return (
          <Fragment key={term.id}>
            <dt>{term.word}</dt>
            <dd>{term.definition}</dd>
          </Fragment>
        );
      })}
    </dl>
  );
}
```

The short form `<>` does not support attributes, so you must use `<Fragment key={...}>` when a key is needed.

### When Fragments Matter

Here is a practical example where a `<div>` wrapper would cause problems:

```jsx
// Component used inside a table
function TableRow({ name, email }) {
  // ❌ Wrong: <div> inside <tr> creates invalid HTML
  return (
    <div>
      <td>{name}</td>
      <td>{email}</td>
    </div>
  );

  // ✅ Correct: Fragment adds no extra element
  return (
    <>
      <td>{name}</td>
      <td>{email}</td>
    </>
  );
}

function UserTable() {
  return (
    <table>
      <tbody>
        <tr>
          <TableRow name="Alice" email="alice@example.com" />
        </tr>
      </tbody>
    </table>
  );
}
```

If `TableRow` used a `<div>` wrapper, the rendered HTML would be `<tr><div><td>...</td><td>...</td></div></tr>`, which is invalid HTML (a `<div>` cannot be a direct child of `<tr>`). Using a Fragment avoids this problem entirely.

Another common case is with Flexbox or CSS Grid layouts:

```jsx
// Parent uses display: flex
function FlexContainer() {
  return (
    <div style={{ display: "flex", gap: "1rem" }}>
      <Sidebar />
      <MainContent />
    </div>
  );
}

// If Sidebar wraps its children in a <div>, that <div> becomes
// a flex item instead of the actual children.

// ❌ Extra div disrupts the flex layout
function Sidebar() {
  return (
    <div>
      <nav>Navigation</nav>
      <aside>Sidebar</aside>
    </div>
  );
}

// ✅ Fragment preserves the intended flex layout
function Sidebar() {
  return (
    <>
      <nav>Navigation</nav>
      <aside>Sidebar</aside>
    </>
  );
}
```

---

## Conditional Rendering

One of JSX's most useful capabilities is showing or hiding content based on conditions. Since JSX is JavaScript, you can use JavaScript logic to control what renders.

### Technique 1: if/else Before the Return

The simplest approach — use a regular `if` statement before the `return`:

```jsx
function Greeting({ isLoggedIn }) {
  if (isLoggedIn) {
    return (
      <div>
        <h1>Welcome back!</h1>
        <p>You are logged in.</p>
      </div>
    );
  }

  return (
    <div>
      <h1>Please sign in</h1>
      <p>You need to log in to continue.</p>
    </div>
  );
}
```

**What this code does:** The component receives an `isLoggedIn` prop (we will learn about props in Chapter 4). If it is `true`, the component returns the welcome message. If it is `false`, it returns the sign-in prompt. The component always returns one or the other — never both.

**When to use this:** When the entire return is different based on a condition. This is the clearest approach when two completely different UIs are needed.

### Technique 2: Ternary Operator

The ternary operator (`condition ? valueIfTrue : valueIfFalse`) works inside JSX because it is an expression:

```jsx
function Greeting({ isLoggedIn }) {
  return (
    <div>
      <h1>{isLoggedIn ? "Welcome back!" : "Please sign in"}</h1>
      <p>
        {isLoggedIn
          ? "You are logged in."
          : "You need to log in to continue."}
      </p>
    </div>
  );
}
```

**What this code does:** Both the heading and paragraph use ternary expressions. If `isLoggedIn` is `true`, the first value after `?` is used. If `false`, the value after `:` is used.

**When to use this:** When a small part of the UI changes based on a condition, but the overall structure stays the same. The ternary operator keeps related markup together.

You can also use ternaries to render different elements:

```jsx
function StatusBadge({ status }) {
  return (
    <div>
      {status === "active" ? (
        <span style={{ color: "green" }}>Active</span>
      ) : (
        <span style={{ color: "red" }}>Inactive</span>
      )}
    </div>
  );
}
```

**Note the parentheses**: When a ternary branch contains JSX elements, wrap them in parentheses for readability. This is not required but is a widely followed convention.

### Technique 3: Logical AND (&&)

The `&&` operator is perfect when you want to show something or nothing:

```jsx
function Notification({ count }) {
  return (
    <div>
      <h1>Messages</h1>
      {count > 0 && <p>You have {count} new messages.</p>}
    </div>
  );
}
```

**What this code does:** If `count > 0` is `true`, the `<p>` element is rendered. If `count > 0` is `false`, nothing is rendered (because `false && anything` evaluates to `false`, and React does not render `false`).

**How `&&` works in JavaScript:**
- If the left side is falsy (`false`, `0`, `""`, `null`, `undefined`), the whole expression evaluates to the left side's value.
- If the left side is truthy, the whole expression evaluates to the right side's value.

```
true  && <p>Show me</p>   → <p>Show me</p>     (renders)
false && <p>Show me</p>   → false               (renders nothing)
```

**When to use this:** When you want to show something or show nothing — there is no "else" case.

### The Dangerous Pitfall with &&

There is a very important gotcha with the `&&` operator:

```jsx
function MessageCount({ count }) {
  return (
    <div>
      {/* ⚠️ DANGER: When count is 0, this renders "0" on screen! */}
      {count && <p>You have {count} messages.</p>}
    </div>
  );
}
```

When `count` is `0`, the expression `0 && <p>...</p>` evaluates to `0` (because `0` is falsy, JavaScript returns the left side). React **does** render the number `0`, so you will see a "0" appear on screen.

**The fix — always use a comparison that produces a boolean:**

```jsx
function MessageCount({ count }) {
  return (
    <div>
      {/* ✅ Safe: count > 0 is either true or false, never 0 */}
      {count > 0 && <p>You have {count} messages.</p>}
    </div>
  );
}
```

The rule is: **the left side of `&&` should always evaluate to `true` or `false`, never to a number or string.**

### Technique 4: Storing JSX in Variables

You can assign JSX to variables and use those variables in your return:

```jsx
function Dashboard({ user, notifications }) {
  let content;

  if (!user) {
    content = <p>Please log in to view your dashboard.</p>;
  } else if (notifications.length === 0) {
    content = <p>No new notifications. All caught up!</p>;
  } else {
    content = (
      <ul>
        {notifications.map(function (note) {
          return <li key={note.id}>{note.text}</li>;
        })}
      </ul>
    );
  }

  return (
    <div>
      <h1>Dashboard</h1>
      {content}
    </div>
  );
}
```

**What this code does:** A `content` variable is set to different JSX based on conditions. Then `{content}` renders whatever was assigned. This is useful for complex conditional logic that would be messy with nested ternaries.

**When to use this:** When you have more than two conditions (if/else if/else), storing JSX in a variable keeps the return statement clean.

### Technique 5: Returning null

A component can return `null` to render nothing at all:

```jsx
function WarningBanner({ show }) {
  if (!show) {
    return null;
  }

  return (
    <div style={{ backgroundColor: "#fff3cd", padding: "1rem", borderRadius: "4px" }}>
      <strong>Warning:</strong> Please check your input.
    </div>
  );
}
```

**What this code does:** If `show` is `false`, the component returns `null` and nothing is rendered — not even an empty element. The component is completely invisible in the DOM.

### Choosing the Right Technique

```
Do you need to show something or nothing?
├── Yes → Use && (with boolean left side)
│         {isVisible && <Modal />}
│
├── Do you need an either/or?
│   ├── Small change → Use ternary
│   │   {isAdmin ? <AdminPanel /> : <UserPanel />}
│   │
│   └── Entirely different returns → Use if/else
│       if (isAdmin) return <AdminDashboard />;
│       return <UserDashboard />;
│
└── Multiple conditions?
    └── Use variables with if/else if
        let view;
        if (status === "loading") view = <Spinner />;
        else if (status === "error") view = <Error />;
        else view = <Data />;
```

---

## Rendering Lists

Web applications frequently display lists of data — product listings, user messages, to-do items, search results. JSX handles this with JavaScript's `map()` method.

### The map() Method

If you are not familiar with `map()`, here is a quick refresher. The `map()` array method creates a new array by calling a function on each item of the original array:

```javascript
const numbers = [1, 2, 3, 4];
const doubled = numbers.map(function (num) {
  return num * 2;
});
// doubled is [2, 4, 6, 8]
```

In JSX, you use `map()` to transform an array of data into an array of JSX elements:

```jsx
function FruitList() {
  const fruits = ["Apple", "Banana", "Cherry", "Date", "Elderberry"];

  return (
    <div>
      <h2>Fruits</h2>
      <ul>
        {fruits.map(function (fruit) {
          return <li key={fruit}>{fruit}</li>;
        })}
      </ul>
    </div>
  );
}
```

**What this code does:**
1. We have an array of fruit names.
2. Inside the JSX, `{fruits.map(...)}` calls `map()` on the array.
3. For each fruit, the function returns an `<li>` element containing the fruit name.
4. The result is an array of `<li>` elements, which React renders as a list.

**The transformation looks like this:**

```
["Apple", "Banana", "Cherry"]
        │
        │  map()
        ▼
[
  <li key="Apple">Apple</li>,
  <li key="Banana">Banana</li>,
  <li key="Cherry">Cherry</li>
]
```

### Using Arrow Functions with map()

You will often see `map()` used with arrow functions for shorter syntax:

```jsx
// Regular function
{fruits.map(function (fruit) {
  return <li key={fruit}>{fruit}</li>;
})}

// Arrow function
{fruits.map((fruit) => {
  return <li key={fruit}>{fruit}</li>;
})}

// Arrow function with implicit return (no curly braces)
{fruits.map((fruit) => (
  <li key={fruit}>{fruit}</li>
))}
```

All three produce the same result. The arrow function with implicit return (using parentheses instead of curly braces) is the most common style in React codebases.

### Rendering Lists of Objects

Real-world data is usually more complex than an array of strings:

```jsx
function UserList() {
  const users = [
    { id: 1, name: "Alice", role: "Developer" },
    { id: 2, name: "Bob", role: "Designer" },
    { id: 3, name: "Charlie", role: "Manager" },
  ];

  return (
    <div>
      <h2>Team Members</h2>
      <ul>
        {users.map((user) => (
          <li key={user.id}>
            <strong>{user.name}</strong> — {user.role}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

**What this code does:** Each `user` object has an `id`, `name`, and `role`. The `map()` callback receives each user object and returns an `<li>` that displays the user's name and role. We use `user.id` as the key (more on keys below).

### The Key Prop

Every element in a list must have a unique `key` prop. React uses keys to identify which items have changed, been added, or been removed. Without keys, React would have to re-render the entire list whenever anything changes.

```jsx
// ✅ Good: unique, stable key
{users.map((user) => (
  <li key={user.id}>{user.name}</li>
))}
```

**Rules for keys:**

1. **Keys must be unique among siblings.** Two list items in the same list cannot have the same key.

2. **Keys should be stable.** A key should not change between renders. Use IDs from your data, not randomly generated values.

3. **Keys should be assigned to the outermost element** returned by the `map()` callback.

```jsx
// ✅ Key on the outermost element
{users.map((user) => (
  <div key={user.id}>
    <h3>{user.name}</h3>
    <p>{user.role}</p>
  </div>
))}

// ❌ Key on an inner element (wrong)
{users.map((user) => (
  <div>
    <h3 key={user.id}>{user.name}</h3>
    <p>{user.role}</p>
  </div>
))}
```

### What to Use as a Key

**Best choice: An ID from your data.**

```jsx
// Data from an API usually has an id field
{posts.map((post) => (
  <article key={post.id}>{post.title}</article>
))}
```

**Acceptable: A unique string property.**

```jsx
// If items have a unique name or slug
{countries.map((country) => (
  <li key={country.code}>{country.name}</li>
))}
```

**Last resort: The array index.**

```jsx
// Only use index when items will NEVER be reordered, added, or removed
{staticItems.map((item, index) => (
  <li key={index}>{item}</li>
))}
```

### Why Not to Use Index as Key

Using the array index as a key is problematic when the list can change (items added, removed, or reordered). Here is why:

```
Initial render:
  Index 0 → "Apple"    (key=0)
  Index 1 → "Banana"   (key=1)
  Index 2 → "Cherry"   (key=2)

After removing "Apple":
  Index 0 → "Banana"   (key=0)  ← React thinks this is "Apple" updated
  Index 1 → "Cherry"   (key=1)  ← React thinks this is "Banana" updated

React sees key=0 changed from "Apple" to "Banana" and re-renders it.
React sees key=1 changed from "Banana" to "Cherry" and re-renders it.
React sees key=2 is gone, so it removes it.

The result looks correct, but React did MORE work than necessary.
Worse: if list items have state (like checkboxes), the state gets mixed up.
```

With proper IDs:

```
Initial render:
  "Apple"  (key="apple-1")
  "Banana" (key="banana-2")
  "Cherry" (key="cherry-3")

After removing "Apple":
  "Banana" (key="banana-2")  ← React knows this existed before, keeps it
  "Cherry" (key="cherry-3")  ← React knows this existed before, keeps it

React sees key="apple-1" is gone, so it removes only that one element.
No unnecessary re-renders. State stays with the correct items.
```

**Rule of thumb:** If your list items will never be reordered, filtered, or have items added/removed, index is fine. In all other cases, use a unique identifier from your data.

### Filtering Lists

You can combine `filter()` and `map()` to show a subset of items:

```jsx
function ActiveUsers() {
  const users = [
    { id: 1, name: "Alice", active: true },
    { id: 2, name: "Bob", active: false },
    { id: 3, name: "Charlie", active: true },
    { id: 4, name: "Diana", active: false },
  ];

  const activeUsers = users.filter((user) => user.active);

  return (
    <div>
      <h2>Active Users ({activeUsers.length})</h2>
      <ul>
        {activeUsers.map((user) => (
          <li key={user.id}>{user.name}</li>
        ))}
      </ul>
    </div>
  );
}
```

**What this code does:** First, `filter()` creates a new array containing only users where `active` is `true`. Then, `map()` transforms those users into `<li>` elements. The heading also shows the count using `activeUsers.length`.

It is good practice to do the filtering before the return statement (as shown above) rather than chaining inside the JSX:

```jsx
// ✅ Cleaner: filter first, then map in JSX
const activeUsers = users.filter((user) => user.active);
return <ul>{activeUsers.map(...)}</ul>;

// ⚠️ Works but harder to read: chaining inside JSX
return <ul>{users.filter((user) => user.active).map(...)}</ul>;
```

---

## Comments in JSX

Writing comments in JSX is different from regular HTML or JavaScript comments.

**Outside of JSX (regular JavaScript comments work):**

```jsx
function App() {
  // This is a regular JavaScript comment
  /* This also works */

  return <h1>Hello</h1>;
}
```

**Inside JSX (use JavaScript block comments wrapped in curly braces):**

```jsx
function App() {
  return (
    <div>
      {/* This is a comment inside JSX */}
      <h1>Hello</h1>

      {/*
        Multi-line comments
        also work like this
      */}
      <p>World</p>
    </div>
  );
}
```

**What does NOT work inside JSX:**

```jsx
// ❌ HTML comments do not work in JSX
<div>
  <!-- This will cause an error -->
  <h1>Hello</h1>
</div>

// ❌ Regular JavaScript comments break the JSX
<div>
  // This will be rendered as text
  <h1>Hello</h1>
</div>
```

The reason you need `{/* */}` inside JSX is that you are in a "JSX zone" where only JSX and JavaScript expressions are valid. The `{}` enters JavaScript mode, and `/* */` is a standard JavaScript block comment.

---

## JSX and HTML Differences — Complete Reference

Here is a comprehensive table of differences between HTML and JSX:

| Feature | HTML | JSX |
|---------|------|-----|
| Class attribute | `class="box"` | `className="box"` |
| For attribute | `for="email"` | `htmlFor="email"` |
| Event handlers | `onclick="fn()"` | `onClick={fn}` |
| Style attribute | `style="color: red"` | `style={{ color: "red" }}` |
| Self-closing tags | `<br>` `<img>` | `<br />` `<img />` |
| Boolean attributes | `<input disabled>` | `<input disabled />` or `<input disabled={true} />` |
| Comments | `<!-- comment -->` | `{/* comment */}` |
| Multi-word attributes | `tabindex` | `tabIndex` (camelCase) |
| Data attributes | `data-id="5"` | `data-id="5"` (same) |
| ARIA attributes | `aria-label="x"` | `aria-label="x"` (same) |
| Dynamic values | Not possible | `{expression}` |
| Conditional rendering | Not possible | `{condition && <El />}` |

---

## Putting It All Together — A Practical Example

Let us build a component that uses everything we have learned in this chapter:

```jsx
function BookList() {
  const storeName = "React Bookshop";
  const books = [
    {
      id: 1,
      title: "Learning React",
      author: "Alex Banks",
      price: 39.99,
      inStock: true,
      rating: 4.5,
    },
    {
      id: 2,
      title: "JavaScript: The Good Parts",
      author: "Douglas Crockford",
      price: 29.99,
      inStock: false,
      rating: 4.2,
    },
    {
      id: 3,
      title: "Eloquent JavaScript",
      author: "Marijn Haverbeke",
      price: 0,
      inStock: true,
      rating: 4.7,
    },
    {
      id: 4,
      title: "You Don't Know JS",
      author: "Kyle Simpson",
      price: 34.99,
      inStock: true,
      rating: 4.6,
    },
  ];

  const availableBooks = books.filter((book) => book.inStock);
  const currentYear = new Date().getFullYear();

  function formatPrice(price) {
    if (price === 0) return "Free";
    return `$${price.toFixed(2)}`;
  }

  function renderStars(rating) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    let stars = "★".repeat(fullStars);
    if (hasHalfStar) stars += "½";
    return stars;
  }

  return (
    <>
      <header style={{ borderBottom: "2px solid #333", paddingBottom: "1rem", marginBottom: "1.5rem" }}>
        <h1>{storeName}</h1>
        <p>
          {availableBooks.length} of {books.length} books available
        </p>
      </header>

      <main>
        {availableBooks.length === 0 ? (
          <p>No books are currently available. Check back soon!</p>
        ) : (
          <div>
            {availableBooks.map((book) => (
              <div
                key={book.id}
                style={{
                  border: "1px solid #ddd",
                  borderRadius: "8px",
                  padding: "1rem",
                  marginBottom: "1rem",
                }}
              >
                <h2 style={{ marginBottom: "0.25rem" }}>{book.title}</h2>
                <p style={{ color: "#666", marginBottom: "0.5rem" }}>
                  by {book.author}
                </p>
                <p>
                  <span style={{ fontWeight: "bold", fontSize: "1.25rem" }}>
                    {formatPrice(book.price)}
                  </span>
                  {book.price === 0 && (
                    <span
                      style={{
                        backgroundColor: "#38a169",
                        color: "white",
                        padding: "0.125rem 0.5rem",
                        borderRadius: "4px",
                        fontSize: "0.75rem",
                        marginLeft: "0.5rem",
                      }}
                    >
                      FREE
                    </span>
                  )}
                </p>
                <p style={{ color: "#d69e2e" }}>
                  {renderStars(book.rating)} ({book.rating})
                </p>
              </div>
            ))}
          </div>
        )}
      </main>

      <footer style={{ marginTop: "2rem", color: "#999", fontSize: "0.875rem" }}>
        <p>© {currentYear} {storeName}. All rights reserved.</p>
      </footer>
    </>
  );
}

export default BookList;
```

**Concepts used in this example:**

1. **Variables in JSX**: `{storeName}`, `{currentYear}`, `{book.title}`, etc.
2. **Fragment**: The outermost `<>...</>` avoids an extra wrapper div.
3. **Function calls**: `{formatPrice(book.price)}` and `{renderStars(book.rating)}`.
4. **Filtering**: `books.filter((book) => book.inStock)` before rendering.
5. **map()**: Rendering the list of available books.
6. **Keys**: Each book card uses `key={book.id}`.
7. **Ternary operator**: Showing "no books" message or the book list.
8. **Logical &&**: The "FREE" badge only appears when `book.price === 0`.
9. **Inline styles**: JavaScript object syntax for styling.
10. **Template literals**: `` `$${price.toFixed(2)}` `` for formatting the price.

To use this component, update your `App.jsx`:

```jsx
import BookList from "./BookList";

function App() {
  return <BookList />;
}

export default App;
```

And create the file `src/BookList.jsx` with the component code above. Save both files and see the result in your browser.

---

## Common Mistakes

1. **Using `class` instead of `className`.**

   ```jsx
   // ❌ React will warn you
   <div class="container">

   // ✅ Correct
   <div className="container">
   ```

   React will display a warning in the console: "Invalid DOM property `class`. Did you mean `className`?" Always use `className`.

2. **Forgetting curly braces for JavaScript expressions.**

   ```jsx
   const name = "Alice";

   // ❌ Renders the literal text "name"
   <h1>Hello, name!</h1>

   // ✅ Renders "Hello, Alice!"
   <h1>Hello, {name}!</h1>
   ```

3. **Trying to use `if` statements inside JSX.**

   ```jsx
   // ❌ if is a statement, not an expression
   <div>
     {if (isLoggedIn) { return <p>Welcome</p>; }}
   </div>

   // ✅ Use a ternary operator
   <div>
     {isLoggedIn ? <p>Welcome</p> : null}
   </div>
   ```

4. **Using `0` as the left side of `&&`.**

   ```jsx
   // ❌ Renders "0" when count is 0
   {count && <p>{count} items</p>}

   // ✅ Use a boolean comparison
   {count > 0 && <p>{count} items</p>}
   ```

5. **Forgetting the `key` prop in lists.**

   React will show a warning: "Each child in a list should have a unique 'key' prop." Always add a key to the outermost element inside `map()`.

6. **Using style as a string instead of an object.**

   ```jsx
   // ❌ This will throw an error
   <div style="color: red; font-size: 16px">

   // ✅ Use a JavaScript object
   <div style={{ color: "red", fontSize: "16px" }}>
   ```

7. **Forgetting to close self-closing tags.**

   ```jsx
   // ❌ Error in JSX
   <img src="photo.jpg">
   <br>
   <input type="text">

   // ✅ Must close with />
   <img src="photo.jpg" />
   <br />
   <input type="text" />
   ```

8. **Trying to render an object.**

   ```jsx
   const user = { name: "Alice" };

   // ❌ Error: Objects are not valid as a React child
   <p>{user}</p>

   // ✅ Access specific properties
   <p>{user.name}</p>
   ```

---

## Best Practices

1. **Use Fragments over unnecessary divs.** If you do not need the wrapper for styling or structure, use `<>...</>` instead of `<div>`.

2. **Keep JSX readable.** Break long JSX across multiple lines and use proper indentation. If a JSX block is getting too large, extract it into a separate component.

3. **Extract complex logic out of JSX.** Instead of writing complex expressions inline, compute values above the return statement:

   ```jsx
   // ❌ Hard to read
   <p>{user.scores.reduce((a, b) => a + b, 0) / user.scores.length}</p>

   // ✅ Clearer
   const average = user.scores.reduce((a, b) => a + b, 0) / user.scores.length;
   <p>{average}</p>
   ```

4. **Always use unique, stable keys in lists.** Prefer database IDs or other natural identifiers over array indices.

5. **Use parentheses around multi-line JSX returns.** This prevents issues with JavaScript's automatic semicolon insertion:

   ```jsx
   // ✅ Always wrap multi-line JSX in parentheses
   return (
     <div>
       <h1>Title</h1>
     </div>
   );

   // ⚠️ This actually returns undefined!
   return
     <div>
       <h1>Title</h1>
     </div>;
   // JavaScript inserts a semicolon after "return", so the JSX is unreachable
   ```

6. **Use boolean checks with &&.** Never let a potentially falsy non-boolean value (like `0` or `""`) be the left side of `&&`.

7. **Use meaningful variable names for conditional JSX.** When storing JSX in variables, name them after what they represent:

   ```jsx
   // ❌ Vague
   const stuff = isAdmin ? <AdminPanel /> : <UserPanel />;

   // ✅ Descriptive
   const dashboardPanel = isAdmin ? <AdminPanel /> : <UserPanel />;
   ```

---

## Summary

In this chapter, you learned:

- **JSX** is a syntax extension that lets you write HTML-like code in JavaScript. It compiles to `React.createElement()` function calls.
- JSX has specific **rules**: single root element, all tags must be closed, `className` instead of `class`, camelCase attributes, and style as a JavaScript object.
- **Curly braces `{}`** let you embed any JavaScript expression in JSX — variables, function calls, math, template literals, and more.
- **Fragments** (`<>...</>`) let you group elements without adding extra DOM nodes.
- **Conditional rendering** can be done with if/else, ternary operators, `&&`, variable assignment, or returning `null`.
- **Lists** are rendered with `map()`, and every list item needs a unique, stable `key` prop.
- **Comments in JSX** use `{/* comment */}` syntax.
- `false`, `null`, `undefined`, and `true` render nothing in JSX, which is useful for conditional rendering.
- Objects cannot be rendered directly — access their individual properties instead.

---

## Interview Questions

**Q1: What is JSX, and is it required to use React?**

JSX is a syntax extension for JavaScript that allows you to write HTML-like markup inside JavaScript. It compiles to `React.createElement()` calls. JSX is not strictly required — you can write `React.createElement()` calls directly — but it is the standard and recommended approach because it is more readable and easier to work with. Virtually all React projects use JSX.

**Q2: Why does JSX use `className` instead of `class`?**

Because `class` is a reserved keyword in JavaScript (used for ES6 class declarations). Since JSX is JavaScript (not HTML), using `class` would create a conflict with the JavaScript parser. The React team chose `className` because it maps directly to the DOM property `element.className` that JavaScript already uses to set CSS classes on DOM elements.

**Q3: What are React Fragments, and when would you use them?**

Fragments (`<>...</>` or `<Fragment>...</Fragment>`) let you group multiple elements without adding an extra node to the DOM. You would use them when a component needs to return multiple sibling elements but wrapping them in a `<div>` would break CSS layouts (like Flexbox or Grid), create invalid HTML (like inside a `<table>`), or add unnecessary DOM depth. The long-form `<Fragment>` is needed when you need to attach a `key` prop, such as in list rendering.

**Q4: Why do elements in a list need a `key` prop?**

Keys help React identify which items in a list have changed, been added, or been removed during re-renders. Without keys, React must re-render the entire list when any item changes. With keys, React can match items between the old and new list, update only what changed, and preserve the state and DOM elements for items that did not change. Keys should be unique among siblings and stable across renders — typically database IDs or natural identifiers.

**Q5: What is the difference between an expression and a statement in the context of JSX?**

An expression produces a value — `2 + 2`, `user.name`, `isLoggedIn ? "Yes" : "No"`. A statement performs an action without producing a value — `if/else`, `for`, `switch`, variable declarations. Only expressions can be used inside JSX curly braces `{}` because JSX needs a value to render. This is why you use ternary operators instead of `if/else` and `map()` instead of `for` loops inside JSX.

**Q6: What happens when you render `false`, `null`, `undefined`, or `true` in JSX?**

They all render nothing — no visible output is produced. React intentionally skips these values. This behavior is the foundation of conditional rendering: `{isVisible && <Modal />}` works because when `isVisible` is `false`, the expression evaluates to `false`, and React renders nothing. However, the number `0` and empty string `""` are NOT skipped — they are rendered as visible text, which is a common source of bugs.

**Q7: Why is it problematic to use array index as a key when list items can be reordered?**

When items are reordered, the index-to-item mapping changes. For example, if item A was at index 0 and item B was at index 1, and they are swapped, React sees key=0 still exists and key=1 still exists — it does not know items moved. It thinks the content at key=0 changed from A to B, so it updates the DOM content. This causes unnecessary re-renders and, critically, can cause state bugs — if each item has local state (like a checkbox or input value), that state stays at the same index instead of following the item.

**Q8: How does the `style` attribute in JSX differ from HTML?**

In HTML, `style` takes a CSS string: `style="color: red; font-size: 16px"`. In JSX, `style` takes a JavaScript object with camelCase property names: `style={{ color: "red", fontSize: "16px" }}`. CSS property names with hyphens are converted to camelCase (`background-color` → `backgroundColor`). Numeric values for pixel-based properties can be plain numbers (`fontSize: 16` equals `"16px"`). The double curly braces are not special syntax — the outer ones denote a JavaScript expression, and the inner ones are the object literal.

---

## Practice Exercises

**Exercise 1: Convert HTML to JSX**

Convert this HTML into valid JSX. Make sure every attribute and syntax rule is correct:

```html
<div class="profile">
  <img src="avatar.png" alt="User avatar">
  <label for="username">Username:</label>
  <input type="text" id="username" tabindex="1" maxlength="30" readonly>
  <p style="color: blue; font-size: 14px; margin-top: 10px;">
    Welcome to the site!
  </p>
  <!-- This is a comment -->
  <br>
  <hr>
</div>
```

**Exercise 2: Dynamic Information Card**

Create a component called `InfoCard` that:
- Defines a JavaScript object with properties: `name`, `email`, `age`, `country`, `isVerified`
- Displays all the information in a nicely formatted card
- Shows a green "Verified" badge next to the name if `isVerified` is true (use `&&`)
- Shows "Minor" or "Adult" based on whether `age` is below 18 (use ternary)
- Uses template literals for the email display: `"Contact: name@example.com"`

**Exercise 3: Filtered List**

Create a component called `TaskList` that:
- Has an array of task objects with: `id`, `title`, `completed` (boolean), `priority` ("high", "medium", "low")
- Create at least 6 tasks with different combinations of completed and priority
- Show only incomplete tasks
- Display the priority next to each task name
- Use different text colors for different priorities (red for high, orange for medium, green for low)
- Show a count: "X tasks remaining"

**Exercise 4: No Unnecessary Divs**

Refactor this component to remove all unnecessary wrapper `<div>` elements using Fragments:

```jsx
function PageLayout() {
  return (
    <div>
      <div>
        <h1>Page Title</h1>
        <p>Subtitle text</p>
      </div>
      <div>
        <nav>
          <div>
            <a href="/">Home</a>
            <a href="/about">About</a>
          </div>
        </nav>
      </div>
    </div>
  );
}
```

Think about which `<div>` elements are needed for structure and which exist only to satisfy the single-root rule.

**Exercise 5: Conditional Rendering Practice**

Create a component called `WeatherDisplay` that takes these variables:
- `temperature` (number)
- `condition` (string: "sunny", "rainy", "cloudy", "snowy")
- `isDay` (boolean)

Use conditional rendering to:
- Show different text emoji based on condition (e.g., "sunny" → "☀️", "rainy" → "🌧️")
- Show "Day" or "Night" based on `isDay`
- Show a "Cold warning!" message if temperature is below 0
- Show a "Heat warning!" message if temperature is above 35
- Change the background color based on the condition (yellow for sunny, gray for cloudy, etc.)

**Exercise 6: JSX Compilation Exercise**

Without running any code, write what the following JSX would compile to in plain JavaScript (`React.createElement` calls). Then verify by checking the React documentation:

```jsx
<div className="wrapper">
  <h1>Title</h1>
  <p>Paragraph with <strong>bold</strong> text</p>
</div>
```

---

## What Is Next?

You now have a deep understanding of JSX — the language you use to describe React UIs. You know the rules, how to embed dynamic content, how to render conditionally, and how to work with lists.

In Chapter 4, we will learn about **Components and Props** — the two concepts that make React truly powerful. You will learn how to break your UI into reusable pieces and pass data between them. This is where React starts to feel genuinely different from plain HTML and JavaScript.
