# Chapter 7: Components

## What You Will Learn

In this chapter, you will learn:

- What a component is and why components are the heart of React
- How to create your own component
- Why component names must start with a capital letter
- How to use one component inside another
- How to put multiple components on one page
- How to organize components in separate files
- How a component tree works

## Why This Chapter Matters

Components are the most important idea in React. Everything in React is a component. The header of a website is a component. A button is a component. A search bar is a component. Even the entire page is a component.

Think of components like **Lego bricks**. Each brick is small and simple on its own. But when you connect many bricks together, you can build a house, a car, or a spaceship. In React, you build small components and connect them together to create your full app.

Once you understand components, you understand React. This chapter is the foundation for everything that comes after it.

---

## What Is a Component?

A component is a **reusable piece of your page**. It is a small, independent unit that shows something on the screen.

Here are some examples of components on a typical website:

```
+--------------------------------------------------+
|  [ Logo ]     [ Home ] [ About ] [ Contact ]     |  <-- Header component
+--------------------------------------------------+
|                                                    |
|   +--------------------------------------------+  |
|   |  Welcome to My Website!                    |  |  <-- Hero component
|   |  We make great things.                     |  |
|   +--------------------------------------------+  |
|                                                    |
|   +----------+  +----------+  +----------+       |
|   |  Card 1  |  |  Card 2  |  |  Card 3  |       |  <-- Card components
|   |          |  |          |  |          |       |
|   +----------+  +----------+  +----------+       |
|                                                    |
+--------------------------------------------------+
|  Copyright 2026 | Privacy | Terms                 |  <-- Footer component
+--------------------------------------------------+
```

Each section is a component. The three cards are all the **same** component used three times with different content. That is the power of reusability.

---

## Creating Your First Component

A component in React is simply a **function that returns JSX**. That is it. Let us create one.

```jsx
function Greeting() {
  return <h1>Hello, welcome to my app!</h1>
}
```

**Line 1:** We create a function called `Greeting`. This is our component.

**Line 2:** The function returns JSX — the content that will appear on the screen.

That is a complete component. Just a function that returns what to show.

### Using Your Component

To use a component, you write it like an HTML tag:

```jsx
function App() {
  return (
    <div>
      <Greeting />
    </div>
  )
}
```

**Line 4:** `<Greeting />` tells React to run the `Greeting` function and show its result here.

**Expected output:**

```
Hello, welcome to my app!
```

Notice how we write `<Greeting />` with a capital G and a self-closing slash. This is how you "call" a component in JSX.

---

## The Capital Letter Rule

Component names **must start with a capital letter**. This is not optional. It is a strict rule.

```jsx
// CORRECT — starts with a capital letter
function Greeting() {
  return <h1>Hello!</h1>
}

// WRONG — starts with a lowercase letter
function greeting() {
  return <h1>Hello!</h1>
}
```

Why does this rule exist? Because React uses the first letter to tell the difference between a component and a regular HTML tag.

```jsx
<div>       // lowercase = HTML tag (a regular div)
<Greeting>  // uppercase = React component (your custom piece)
```

If you write `<greeting>`, React thinks you mean an HTML tag called "greeting." Since no such HTML tag exists, things will not work correctly.

Think of it like proper nouns in English. Regular words are lowercase: "table," "chair," "door." But names are capitalized: "Sarah," "Tokyo," "Monday." Components are like names. They are special, so they get a capital letter.

---

## A Component with More Content

Components can return as much JSX as you need. Just remember to wrap everything in one parent element.

```jsx
function UserCard() {
  return (
    <div>
      <h2>Jane Smith</h2>
      <p>Age: 30</p>
      <p>Job: Designer</p>
    </div>
  )
}
```

**Expected output:**

```
Jane Smith
Age: 30
Job: Designer
```

---

## Using a Component Inside Another Component

This is where things get exciting. You can put components inside other components. This is called **composition**. Composition means building something by combining smaller pieces.

```jsx
function Header() {
  return <h1>My Website</h1>
}

function MainContent() {
  return <p>Welcome to the best website ever!</p>
}

function Footer() {
  return <p>Copyright 2026</p>
}

function App() {
  return (
    <div>
      <Header />
      <MainContent />
      <Footer />
    </div>
  )
}
```

**Line 14-20:** The `App` component uses three other components: `Header`, `MainContent`, and `Footer`.

**Expected output:**

```
My Website
Welcome to the best website ever!
Copyright 2026
```

Each component handles its own part of the page. This keeps your code organized. If you want to change the footer, you go to the `Footer` component. You do not have to search through hundreds of lines of code.

---

## Multiple Components on One Page

You can use the same component more than once:

```jsx
function Divider() {
  return <hr />
}

function App() {
  return (
    <div>
      <h1>My Page</h1>
      <Divider />
      <p>First section of content.</p>
      <Divider />
      <p>Second section of content.</p>
      <Divider />
      <p>Third section of content.</p>
    </div>
  )
}
```

We used the `Divider` component three times. The `<hr />` tag creates a horizontal line. Each `<Divider />` shows a line on the page.

**Expected output:**

```
My Page
___________________
First section of content.
___________________
Second section of content.
___________________
Third section of content.
```

Write once, use many times. That is the beauty of components.

---

## The Component Tree

When you put components inside other components, you create a **component tree**. It looks like a family tree. The top component is the parent, and the components inside it are the children.

Here is the tree for our earlier example:

```
         App
        / | \
       /  |  \
  Header  |  Footer
          |
     MainContent
```

`App` is the parent. It has three children: `Header`, `MainContent`, and `Footer`.

Here is a more complex example:

```
              App
             / | \
            /  |  \
      Header  Main  Footer
       / \      |
      /   \     |
   Logo  Nav  ArticleList
              /    \
             /      \
        Article   Article
```

The tree can go as deep as you need. Each level is a component that contains smaller components. This is how real React apps are built.

React always starts from the top of the tree (the `App` component) and works its way down, rendering each component.

---

## Organizing Components in Separate Files

So far, we have written all our components in one file. In real projects, each component gets its own file. This keeps things organized.

Here is how you do it:

### Step 1: Create a New File

Create a file called `Header.jsx` inside your `src` folder:

```
src/
├── App.jsx
├── Header.jsx      <-- new file
├── Footer.jsx      <-- new file
├── main.jsx
└── index.css
```

### Step 2: Write the Component and Export It

In `Header.jsx`:

```jsx
function Header() {
  return (
    <header>
      <h1>My Website</h1>
      <p>The best website on the internet</p>
    </header>
  )
}

export default Header
```

**Line 10:** `export default Header` makes this component available to other files. Without this line, other files cannot use it.

Think of `export` like putting a label on a package. The label says, "This is the Header. Other files can request it."

In `Footer.jsx`:

```jsx
function Footer() {
  return (
    <footer>
      <p>Copyright 2026. All rights reserved.</p>
    </footer>
  )
}

export default Footer
```

### Step 3: Import the Component Where You Need It

In `App.jsx`:

```jsx
import Header from './Header.jsx'
import Footer from './Footer.jsx'

function App() {
  return (
    <div>
      <Header />
      <p>This is the main content of my app.</p>
      <Footer />
    </div>
  )
}

export default App
```

**Line 1:** `import Header from './Header.jsx'` brings the Header component into this file. The `./` means "in the same folder."

**Line 2:** Same thing for Footer.

**Lines 7-9:** Now we use them just like before.

**Expected output:**

```
My Website
The best website on the internet
This is the main content of my app.
Copyright 2026. All rights reserved.
```

### Understanding Import and Export

Think of import and export like a mail system:

- **`export`** is like putting a package in the mailbox. You are sending it out.
- **`import`** is like receiving a package. You are bringing it in.

A file can only **export** something if it has something to share. A file can **import** something only if the other file has exported it.

```
Header.jsx                        App.jsx
+--------------------+            +--------------------+
|                    |            |                    |
| function Header()  |  export   | import Header      |
| { ... }           | -------->  | from './Header'    |
|                    |            |                    |
| export default     |            | <Header />         |
|   Header           |            |                    |
+--------------------+            +--------------------+
```

---

## Putting It All Together: A Mini Website

Let us build a small website with multiple components in separate files.

### `Header.jsx`

```jsx
function Header() {
  return (
    <header>
      <h1>Book Store</h1>
      <nav>
        <a href="#">Home</a> | <a href="#">Books</a> | <a href="#">Contact</a>
      </nav>
    </header>
  )
}

export default Header
```

### `Main.jsx`

```jsx
function Main() {
  return (
    <main>
      <h2>Featured Books</h2>
      <p>Check out our top picks for this month!</p>
    </main>
  )
}

export default Main
```

### `Footer.jsx`

```jsx
function Footer() {
  return (
    <footer>
      <p>Book Store - Helping you find great reads since 2024</p>
    </footer>
  )
}

export default Footer
```

### `App.jsx`

```jsx
import Header from './Header.jsx'
import Main from './Main.jsx'
import Footer from './Footer.jsx'

function App() {
  return (
    <div>
      <Header />
      <Main />
      <Footer />
    </div>
  )
}

export default App
```

**Expected output:**

```
Book Store
Home | Books | Contact

Featured Books
Check out our top picks for this month!

Book Store - Helping you find great reads since 2024
```

The component tree for this app:

```
        App
       / | \
      /  |  \
 Header Main Footer
```

Each component has one job. The `Header` shows the top of the page. `Main` shows the content. `Footer` shows the bottom. If you want to change the navigation links, you only edit `Header.jsx`. Everything else stays the same.

---

## Quick Summary

- A component is a function that returns JSX. It is a reusable piece of your page.
- Component names must start with a capital letter.
- You use a component by writing it like a tag: `<MyComponent />`.
- Components can be placed inside other components. This is called composition.
- You can use the same component multiple times.
- In real projects, each component goes in its own file.
- `export default` makes a component available. `import` brings it into another file.
- Components form a tree, with `App` at the top.

---

## Key Points to Remember

1. **A component is just a function** that returns JSX. Nothing more, nothing less.
2. **Capital first letter** is required. `<Header />` is a component. `<header>` is an HTML tag.
3. **One component, one job.** Each component should do one thing well.
4. **export and import** connect components across files. Export sends it out. Import brings it in.
5. **The component tree** starts at `App` and branches downward. React renders from top to bottom.

---

## Practice Questions

1. What is a component in React? Describe it in your own words.

2. Why must component names start with a capital letter? What happens if they do not?

3. What is the difference between `export default` and `import`? Use the mail analogy to explain.

4. Can you use the same component more than once on a page? Give an example of when that would be useful.

5. What is a component tree? Draw the component tree for an app that has an `App` component containing a `Sidebar`, a `Content` area, and a `Footer`.

---

## Exercises

### Exercise 1: Create a Greeting Component

Create a component called `Greeting` that shows a friendly welcome message. Use it inside the `App` component.

Your component should display:

```
Welcome, Friend!
We are glad you are here.
```

### Exercise 2: Build a Page with Three Components

Create three separate components:

1. `Header` — shows the title "My Blog"
2. `Article` — shows a paragraph of text about any topic you like
3. `Footer` — shows "Thanks for reading!"

Use all three inside the `App` component. If you feel comfortable, put each one in its own file.

### Exercise 3: Reuse a Component

Create a `Star` component that simply shows the text "* * * * *" (five stars). Use this component three times inside your `App` to create a rating display:

```
Food Quality:
* * * * *
Service:
* * * * *
Atmosphere:
* * * * *
```

---

## What Is Next?

You now know how to create and use components. But right now, our components always show the same thing. A `Greeting` component always says the same message. A `UserCard` always shows the same person.

What if you could make a component that shows different content depending on what you tell it? What if you could pass information to a component, like handing it a note that says "show this name" or "use this color"?

That is exactly what **Props** are. In the next chapter, you will learn how to pass data to your components and make them truly flexible and reusable. Let us go!
