# Chapter 6: JSX Explained Simply

## What You Will Learn

In this chapter, you will learn:

- What JSX is and why React uses it
- The rules you must follow when writing JSX
- How to put JavaScript values inside your JSX using curly braces `{}`
- Common mistakes beginners make with JSX and how to fix them
- The key differences between JSX and HTML

## Why This Chapter Matters

JSX is one of the first things you see when you open a React file. It looks like HTML, but it is not exactly HTML. If you try to write regular HTML in React, you will run into errors.

Think of JSX like a different dialect of a language. If you speak English, you can mostly understand Australian English. But some words are different. "Boot" means the trunk of a car. "Arvo" means afternoon. You need to learn the differences, or you will get confused.

JSX is React's dialect. Once you learn its rules, everything will feel natural.

---

## What Is JSX?

JSX stands for **JavaScript XML**. XML is a way of writing structured data using tags, similar to HTML.

In simple terms: **JSX lets you write HTML-like code inside your JavaScript files.**

Here is a simple example:

```jsx
function Greeting() {
  return <h1>Hello, World!</h1>
}
```

That `<h1>Hello, World!</h1>` part is JSX. It looks like HTML, but it is actually inside a JavaScript function.

### Why Does React Use JSX?

In traditional web development, you keep your HTML, CSS, and JavaScript in separate files:

```
Traditional way:
  index.html    (structure — what is on the page)
  styles.css    (appearance — how it looks)
  script.js     (behavior — what it does)
```

React does things differently. It puts the structure and behavior together in the same file using JSX.

Why? Because in modern apps, the structure and behavior of a piece of the page are closely connected. If you have a button, the way it looks and what it does when you click it are related. Keeping them in the same file makes it easier to understand and change.

Think of it like a recipe. Imagine if someone gave you a recipe where the ingredients were in one book, the cooking steps were in another book, and the serving instructions were in a third book. That would be hard to follow. It is much easier when everything for one recipe is on one card.

JSX is like putting the recipe on one card.

---

## Your First JSX

Let us write a simple component with JSX:

```jsx
function Welcome() {
  return (
    <div>
      <h1>Welcome to React</h1>
      <p>This is my first JSX code.</p>
    </div>
  )
}
```

**Line 1:** We create a function called `Welcome`. This is a React component.

**Line 2:** The `return` keyword tells React what to show on the screen.

**Lines 3-6:** This is JSX. It describes what the page should look like. It has a `div` container with a heading and a paragraph inside it.

**Expected output in the browser:**

```
Welcome to React
This is my first JSX code.
```

The JSX looks like HTML, but React converts it into real HTML behind the scenes.

---

## The Rules of JSX

JSX has rules. If you break them, your app will show an error. Let us learn each rule with examples.

### Rule 1: You Must Return One Parent Element

In JSX, everything you return must be wrapped inside **one single parent element**. You cannot return two elements side by side without a wrapper.

**This is WRONG:**

```jsx
// This will cause an error!
function Broken() {
  return (
    <h1>Hello</h1>
    <p>World</p>
  )
}
```

React will show an error: **"Adjacent JSX elements must be wrapped in an enclosing tag."**

**This is CORRECT:**

```jsx
function Fixed() {
  return (
    <div>
      <h1>Hello</h1>
      <p>World</p>
    </div>
  )
}
```

We wrapped both elements inside a `<div>`. Now there is one parent element.

**Another correct way — using a Fragment:**

```jsx
function AlsoFixed() {
  return (
    <>
      <h1>Hello</h1>
      <p>World</p>
    </>
  )
}
```

The `<>` and `</>` are called a **Fragment**. A Fragment is an invisible wrapper. It groups elements together without adding an extra `div` to your page. Think of it like a clear plastic bag. It holds things together, but you cannot see it.

### Rule 2: Close All Tags

In HTML, some tags do not need a closing tag. For example, `<br>` and `<img>` can stand alone in HTML.

In JSX, **every tag must be closed.** No exceptions.

**This is WRONG:**

```jsx
// These will cause errors in JSX!
<br>
<img src="photo.jpg">
<input type="text">
```

**This is CORRECT:**

```jsx
// Self-closing tags — note the / before >
<br />
<img src="photo.jpg" />
<input type="text" />
```

The `/` before the `>` closes the tag. These are called **self-closing tags**.

### Rule 3: Use `className` Instead of `class`

In HTML, you use `class` to give an element a CSS class:

```html
<!-- HTML way -->
<div class="container">Hello</div>
```

In JSX, you use `className` instead:

```jsx
// JSX way
<div className="container">Hello</div>
```

Why? Because `class` is already a reserved word in JavaScript. It means something else in JavaScript (it is used to create objects). To avoid confusion, React uses `className`.

Think of it like this: in a school, "class" might mean a group of students or a classroom. To avoid confusion, you might call one "class-group" and the other "classroom." React does a similar thing.

### Rule 4: Use camelCase for Attributes

HTML uses lowercase attribute names:

```html
<!-- HTML -->
<div onclick="doSomething()" tabindex="1">Click me</div>
```

JSX uses **camelCase** for attribute names. CamelCase means the first word is lowercase, and every next word starts with a capital letter, like the humps of a camel:

```jsx
// JSX
<div onClick={doSomething} tabIndex="1">Click me</div>
```

Here are some common examples:

```
HTML attribute     JSX attribute
--------------     -------------
onclick            onClick
onchange           onChange
tabindex           tabIndex
maxlength          maxLength
for                htmlFor
```

Notice that `for` becomes `htmlFor`. Just like `class`, the word `for` already means something in JavaScript (it is used in loops). So JSX uses `htmlFor`.

### Rule 5: JavaScript Expressions Use Curly Braces

When you want to put JavaScript inside your JSX, you wrap it in curly braces `{}`. We will cover this in detail in the next section.

---

## Curly Braces: Putting JavaScript Inside JSX

This is one of the most useful features of JSX. Curly braces `{}` let you insert JavaScript values into your JSX.

Think of curly braces like **fill-in-the-blank spaces** on a form. The JSX is the form, and the curly braces are the blanks where you fill in dynamic values.

### Showing a Variable

```jsx
function Hello() {
  const name = "Sarah"

  return <h1>Hello, {name}!</h1>
}
```

**Line 2:** We create a variable called `name` and give it the value `"Sarah"`. A variable is like a labeled box that holds a value.

**Line 4:** Inside the JSX, `{name}` gets replaced with the value of the variable.

**Expected output:**

```
Hello, Sarah!
```

### Doing Math

```jsx
function MathExample() {
  const price = 10
  const quantity = 3

  return <p>Total: ${price * quantity}</p>
}
```

**Line 2-3:** We create two variables.

**Line 5:** Inside `{}`, we multiply `price` times `quantity`. React calculates `10 * 3` and shows `30`.

**Expected output:**

```
Total: $30
```

### Showing Today's Date

```jsx
function Today() {
  const today = new Date()
  const day = today.toLocaleDateString()

  return <p>Today is: {day}</p>
}
```

**Line 2:** `new Date()` creates an object that represents the current date and time.

**Line 3:** `.toLocaleDateString()` converts it to a readable format like "3/25/2026".

**Line 5:** We show the date inside the JSX.

**Expected output:**

```
Today is: 3/25/2026
```

### Calling a Function

```jsx
function Shout() {
  const message = "hello"

  return <p>{message.toUpperCase()}</p>
}
```

**Line 4:** `.toUpperCase()` converts text to all capital letters. We can call functions inside curly braces.

**Expected output:**

```
HELLO
```

### What You Can Put Inside Curly Braces

You can put any JavaScript **expression** inside curly braces. An expression is anything that produces a value.

```
Can use inside {}:          Cannot use inside {}:
-------------------         ----------------------
Variables:    {name}        if/else statements
Math:         {2 + 2}      for loops
Functions:    {getName()}   Variable declarations
Strings:      {"hello"}      (const x = 5)
```

If you need to use if/else logic, you can use a **ternary expression** (a short way to write if/else):

```jsx
function Weather() {
  const isSunny = true

  return (
    <p>
      The weather is {isSunny ? "sunny" : "cloudy"}.
    </p>
  )
}
```

**Line 6:** The `?` and `:` create a ternary expression. It reads like this: "Is `isSunny` true? If yes, use 'sunny'. If no, use 'cloudy'."

**Expected output:**

```
The weather is sunny.
```

---

## JSX Is NOT HTML: Key Differences

Here is a quick reference table of the main differences:

```
+--------------------------------------------+
|        HTML              JSX               |
+--------------------------------------------+
| class="..."         className="..."        |
| for="..."           htmlFor="..."          |
| onclick="..."       onClick={...}          |
| tabindex="..."      tabIndex="..."         |
| <br>                <br />                 |
| <img ...>           <img ... />            |
| style="color: red"  style={{color: "red"}} |
| <!-- comment -->    {/* comment */}        |
+--------------------------------------------+
```

Notice two special differences:

**Inline styles** use double curly braces and camelCase property names:

```jsx
// HTML way:
// <p style="background-color: blue; font-size: 20px">Hello</p>

// JSX way:
<p style={{ backgroundColor: "blue", fontSize: "20px" }}>Hello</p>
```

The outer `{}` means "here comes JavaScript." The inner `{}` creates a JavaScript object (a collection of key-value pairs). Style property names use camelCase: `background-color` becomes `backgroundColor`.

**Comments** in JSX use a different format:

```jsx
function Example() {
  return (
    <div>
      {/* This is a comment in JSX */}
      <p>Hello</p>
    </div>
  )
}
```

HTML comments `<!-- -->` do not work in JSX. You must use `{/* */}`.

---

## Common Mistakes and How to Fix Them

### Mistake 1: Forgetting to Close a Tag

```jsx
// WRONG
<img src="cat.jpg">

// RIGHT
<img src="cat.jpg" />
```

**Error you might see:** "Expected corresponding JSX closing tag."

### Mistake 2: Using `class` Instead of `className`

```jsx
// WRONG
<div class="box">Hello</div>

// RIGHT
<div className="box">Hello</div>
```

**What happens:** React will show a warning in the console: "Invalid DOM property 'class'. Did you mean 'className'?"

### Mistake 3: Returning Two Elements Without a Wrapper

```jsx
// WRONG
return (
  <h1>Title</h1>
  <p>Paragraph</p>
)

// RIGHT — use a div or Fragment
return (
  <>
    <h1>Title</h1>
    <p>Paragraph</p>
  </>
)
```

**Error you might see:** "Adjacent JSX elements must be wrapped in an enclosing tag."

### Mistake 4: Forgetting Curly Braces for JavaScript

```jsx
const name = "Alex"

// WRONG — this shows the text "name" literally
<p>Hello, name!</p>

// RIGHT — curly braces tell React to use the variable
<p>Hello, {name}!</p>
```

**What happens:** Without curly braces, React shows the literal word "name" instead of the value "Alex."

### Mistake 5: Using Quotes Around Curly Braces

```jsx
const name = "Alex"

// WRONG — this shows the text "{name}" literally
<p>Hello, "{name}"!</p>

// RIGHT
<p>Hello, {name}!</p>
```

Do not wrap curly braces in quotes. The curly braces ARE the signal to React. Quotes around them turn everything into plain text.

---

## A Complete Example

Let us put it all together in one component:

```jsx
function ProfileCard() {
  const name = "Maria"
  const age = 28
  const hobby = "painting"
  const isMember = true

  return (
    <div className="card">
      <h2>{name}</h2>
      <p>Age: {age}</p>
      <p>Hobby: {hobby}</p>
      <p>Member: {isMember ? "Yes" : "No"}</p>
      <p>Birth year: roughly {2026 - age}</p>
      {/* This line will not show on the page */}
    </div>
  )
}
```

**Expected output:**

```
Maria
Age: 28
Hobby: painting
Member: Yes
Birth year: roughly 1998
```

**Line by line:**

- **Lines 2-5:** We create variables that hold information about a person.
- **Line 9:** `{name}` shows "Maria."
- **Line 10:** `{age}` shows 28.
- **Line 11:** `{hobby}` shows "painting."
- **Line 12:** The ternary expression checks if `isMember` is true. It is, so it shows "Yes."
- **Line 13:** `{2026 - age}` does math and shows 1998.
- **Line 14:** This is a JSX comment. It does not show on the page.

---

## Quick Summary

- JSX is HTML-like code that you write inside JavaScript files.
- React uses JSX so you can keep your structure and behavior together.
- JSX has rules: one parent element, close all tags, use `className`, use camelCase.
- Curly braces `{}` let you put JavaScript values inside JSX, like fill-in-the-blank spaces.
- JSX is not HTML. There are important differences in syntax.
- Common mistakes are easy to fix once you know the rules.

---

## Key Points to Remember

1. **JSX must have one parent element.** Wrap everything in a `<div>` or a Fragment `<>`.
2. **Close every tag.** Self-closing tags need a slash: `<br />`, `<img />`.
3. **Use `className` instead of `class`.** This is one of the most common JSX rules.
4. **Curly braces `{}` insert JavaScript into JSX.** Variables, math, functions — all go inside curly braces.
5. **JSX looks like HTML but is actually JavaScript.** React converts your JSX into real HTML behind the scenes.

---

## Practice Questions

1. What does JSX stand for? In your own words, what is JSX?

2. Why does React use `className` instead of `class`?

3. What are curly braces `{}` used for in JSX? Give an example.

4. What is a Fragment? When would you use one instead of a `div`?

5. You write `<p>Hello, name!</p>` but you want it to show the value of a variable called `name`. What is wrong, and how do you fix it?

---

## Exercises

### Exercise 1: Create a Personal Info Card

Create a component called `AboutMe` that shows your name, your age, and your favorite food. Use variables and curly braces.

```jsx
function AboutMe() {
  const name = "Your Name"
  const age = 25
  const food = "pizza"

  return (
    <div>
      <h1>About Me</h1>
      <p>Name: {name}</p>
      <p>Age: {age}</p>
      <p>Favorite food: {food}</p>
    </div>
  )
}
```

Try changing the variable values and see the output update.

### Exercise 2: Build a Simple Calculator Display

Create a component that shows the results of some math:

```jsx
function Calculator() {
  const a = 15
  const b = 4

  return (
    <div>
      <h2>Calculator</h2>
      <p>{a} + {b} = {a + b}</p>
      <p>{a} - {b} = {a - b}</p>
      <p>{a} x {b} = {a * b}</p>
    </div>
  )
}
```

Change the values of `a` and `b` and check that the results update correctly.

### Exercise 3: Fix the Broken JSX

This code has several mistakes. Find and fix all of them:

```jsx
function Broken() {
  const city = "Tokyo"

  return (
    <h1>My City</h1>
    <p class="info">I live in city.</p>
    <img src="tokyo.jpg">
  )
}
```

Hint: There are at least three mistakes. Look at the rules you learned in this chapter.

---

## What Is Next?

You now know how to write JSX — the language React uses to describe your pages. You know the rules, you know how to put JavaScript inside it, and you know how to avoid common mistakes.

In the next chapter, we will learn about **Components** — the building blocks of every React app. Components are like Lego bricks. Each one is a small, reusable piece. You combine them to build something amazing. Let us go build some!
