# Chapter 5: Understanding Project Structure

## What You Will Learn

In this chapter, you will learn:

- What each file and folder in your React project does
- Why each file exists and when you will use it
- Which files you will edit and which ones you should leave alone
- How all the pieces fit together to make your app work

## Why This Chapter Matters

When you open your React project for the first time, you see many files and folders. It can feel overwhelming. You might think, "What are all these files? Do I need to understand all of them?"

The good news is: you only need to work with a few of them. But knowing what each file does will help you feel confident. It is like moving into a new house. You want to know where the kitchen is, where the bathroom is, and where the light switches are. You do not need to understand the plumbing on day one, but knowing the layout makes everything easier.

This chapter is your tour of the house.

---

## The Big Picture: Your Project Folder

When you created your React project with Vite in the previous chapter, it made a folder with several files inside. Let us look at the full structure.

Here is what your project looks like:

```
my-first-react-app/
├── node_modules/        <-- The library shelf (never touch this)
├── public/              <-- Static files (things that do not change)
│   └── vite.svg
├── src/                 <-- YOUR code lives here (you work here most)
│   ├── assets/
│   │   └── react.svg
│   ├── App.css
│   ├── App.jsx
│   ├── index.css
│   └── main.jsx
├── .eslintrc.cjs        <-- Code quality checker settings
├── .gitignore           <-- Tells Git which files to ignore
├── index.html           <-- The one and only HTML page
├── package.json         <-- The recipe card for your project
├── package-lock.json    <-- Exact version list (auto-generated)
├── README.md            <-- Notes about your project
└── vite.config.js       <-- Vite settings
```

Do not worry. We will go through each one, step by step.

---

## The `src` Folder — Where You Do Your Work

The `src` folder is the most important folder. The name `src` is short for "source." This is where your source code lives. Source code means the code that YOU write.

Think of it this way:

- The `src` folder is your **kitchen**. This is where you cook (write code).
- Everything else in the project is like the pantry, the recipe book, or the delivery truck. They help, but you do your main work in the kitchen.

When you are building your app, you will spend almost all of your time inside the `src` folder.

### `main.jsx` — Where React Starts

This file is the **front door** of your app. When your app starts, this is the very first file that runs.

Let us look at what is inside:

```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

Let us go through this line by line.

**Line 1:** `import React from 'react'`
This line brings in the React library. It is like saying, "I need my toolbox."

**Line 2:** `import ReactDOM from 'react-dom/client'`
This line brings in ReactDOM. "DOM" stands for Document Object Model. It is how the browser organizes everything on a web page. ReactDOM connects React to the browser's web page.

**Line 3:** `import App from './App.jsx'`
This line brings in your App component. A component is a piece of your page. We will learn about components in Chapter 7. For now, think of it as the main content of your app.

**Line 4:** `import './index.css'`
This line brings in your main CSS file. CSS controls how things look — colors, sizes, spacing.

**Lines 6-9:** These lines tell React: "Find the HTML element with the id of 'root', and put the App component inside it."

Think of it like this: React finds an empty box on the page (the `root` element) and fills it with your app.

You will rarely need to change this file. It is set up once and then left alone.

### `App.jsx` — Your First Component

This is the main component of your app. When you first open it, it has some starter code:

```jsx
import './App.css'

function App() {
  return (
    <div>
      <h1>Hello React!</h1>
    </div>
  )
}

export default App
```

Let us go through this line by line.

**Line 1:** `import './App.css'`
This brings in the styles (colors, sizes, etc.) for this component.

**Line 3:** `function App() {`
This creates a function called `App`. In React, a component is just a function. This function describes what should appear on the screen.

**Lines 4-8:** The `return` part tells React what to show. Here, it shows a heading that says "Hello React!" inside a `div`. A `div` is like a container or a box that holds other things.

**Line 11:** `export default App`
This line makes the `App` component available to other files. Remember how `main.jsx` imported `App`? This is the line that allows that to happen. It is like putting a label on a box so someone can find it and use it.

This is the file you will edit the most when you are starting out.

### `index.css` and `App.css` — Styling Files

These are CSS files. CSS stands for Cascading Style Sheets. CSS controls how things look on your page.

- **`index.css`** has styles that apply to your entire app. Things like the background color of the page or the default font.
- **`App.css`** has styles that are specific to the App component.

Think of it this way:
- `index.css` is like painting the walls of your entire house.
- `App.css` is like decorating one specific room.

### `assets` Folder

This folder holds images, icons, and other media files that your app uses. Right now, it just has `react.svg`, which is the React logo.

When you want to add images to your app, you can put them here.

---

## `index.html` — The One HTML Page

React apps are called "single-page applications" (often shortened to SPA). This means your entire app runs inside **one single HTML page**.

Here is what `index.html` looks like:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Vite + React</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

The most important line is this one:

```html
<div id="root"></div>
```

This is the empty box we talked about. React takes this empty box and fills it with your entire app. Everything you build in React will appear inside this one `div`.

The other important line is:

```html
<script type="module" src="/src/main.jsx"></script>
```

This tells the browser to run `main.jsx`, which starts your React app.

Here is the flow:

```
Browser opens index.html
        |
        v
index.html loads main.jsx
        |
        v
main.jsx loads App component
        |
        v
App component shows on the page
```

You will almost never need to edit `index.html`. Maybe you will change the title of your app, but that is about it.

---

## `package.json` — The Recipe Card

Think of `package.json` as a **recipe card** for your project. A recipe card tells you:

- What the dish is called
- What ingredients you need
- What steps to follow

Similarly, `package.json` tells your computer:

- What your project is called
- What libraries (ingredients) it needs
- What commands (steps) are available

Here is what it looks like:

```json
{
  "name": "my-first-react-app",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "vite": "^5.0.0"
  }
}
```

Let us break this down:

**`"name"`** — The name of your project. Like the title on a recipe card.

**`"scripts"`** — These are commands you can run. Remember `npm run dev`? That works because `"dev": "vite"` is listed here. It is a shortcut. Instead of typing a long command, you just type `npm run dev`.

Here is what each script does:
- `"dev"` — Starts your app for development (what you use while building)
- `"build"` — Creates a final version of your app ready for the real internet
- `"preview"` — Lets you preview the final version before putting it online

**`"dependencies"`** — These are the libraries your app needs to run. Right now, you need `react` and `react-dom`. These are your main ingredients.

**`"devDependencies"`** — These are tools you need only while building your app, not when it is running on the internet. `vite` is here because it is a development tool. Think of it like an oven. You need an oven to bake a cake, but you do not deliver the oven with the cake.

---

## `node_modules` — The Library Shelf

The `node_modules` folder is a big folder that contains all the libraries your project uses. When you ran `npm install`, this folder was created automatically.

Think of it as a **library shelf**. When your recipe (`package.json`) says you need React, the computer goes and gets React and puts it on this shelf.

### Important Rules About `node_modules`

1. **Never edit files inside `node_modules`.** These files are managed by npm. If you change them, things will break.
2. **Never share this folder.** It is very large (sometimes thousands of files). When you share your project, you share the recipe (`package.json`), not the ingredients. Other people can run `npm install` to fill their own shelf.
3. **You can delete it and get it back.** If something goes wrong, you can delete the entire `node_modules` folder and run `npm install` again. It will rebuild everything.

```
You edit these:          You do NOT edit these:
--------------           ----------------------
src/App.jsx              node_modules/ (anything)
src/main.jsx             package-lock.json
src/index.css
src/App.css
```

---

## `public` Folder — Static Files

The `public` folder holds files that do not change and do not need to be processed by Vite. Right now, it just has `vite.svg` (the Vite logo that shows as the browser tab icon).

Things you might put in the `public` folder:

- A favicon (the small icon in the browser tab)
- Images that you want to reference directly
- A `robots.txt` file (tells search engines about your site)

Most of the time, you will put your images in `src/assets/` instead. But the `public` folder is there when you need it.

---

## Other Files

### `.gitignore`

Git is a tool that tracks changes to your code (we will talk about it later). The `.gitignore` file tells Git which files to ignore. For example, it tells Git to ignore the `node_modules` folder because that folder is too large to track.

### `.eslintrc.cjs`

ESLint is a tool that checks your code for common mistakes. This file tells ESLint what rules to follow. You do not need to worry about this file right now.

### `package-lock.json`

This file is auto-generated. It records the exact version of every library installed. You never edit this file directly.

### `vite.config.js`

This file has settings for Vite. The default settings work fine for beginners. You do not need to change it.

### `README.md`

This is a notes file about your project. The `.md` stands for Markdown, which is a simple way to format text. You can write notes about your project here.

---

## Which Files Will You Edit?

Here is a simple guide:

```
+---------------------------------------------------+
|              Files You Will Edit Often             |
+---------------------------------------------------+
| src/App.jsx       Your main component             |
| src/App.css       Styles for your main component  |
| src/index.css     Global styles                   |
| Files you create inside src/                      |
+---------------------------------------------------+

+---------------------------------------------------+
|           Files You Will Edit Sometimes            |
+---------------------------------------------------+
| index.html        Maybe change the page title     |
| package.json      When adding new libraries       |
+---------------------------------------------------+

+---------------------------------------------------+
|             Files You Will NOT Edit                |
+---------------------------------------------------+
| node_modules/     Managed by npm                  |
| package-lock.json Auto-generated                  |
| vite.config.js    Default settings are fine       |
+---------------------------------------------------+
```

---

## How Everything Connects

Let us see the full picture of how your app starts:

```
1. You type: npm run dev

2. Vite starts a development server

3. Your browser opens index.html

4. index.html has <div id="root"></div>
   and loads main.jsx

5. main.jsx tells React:
   "Put the App component inside the root div"

6. App.jsx returns JSX
   (the content to show on the page)

7. You see your app in the browser!
```

Here is another way to see it:

```
index.html  -->  main.jsx  -->  App.jsx  -->  What you see
(the page)      (the start)    (the content)  (in browser)
```

Every React app follows this same pattern. Once you understand it, you will feel at home in any React project.

---

## Quick Summary

- Your React project has a clear structure. Each file has a job.
- The `src` folder is where you do most of your work.
- `main.jsx` is the starting point. It connects React to the page.
- `App.jsx` is your main component. You will edit this the most.
- `index.html` is the one HTML page. React fills it with content.
- `package.json` is like a recipe card. It lists what your project needs.
- `node_modules` is the library shelf. Never edit it.
- The `public` folder holds static files that do not change.

---

## Key Points to Remember

1. **You work inside the `src` folder** almost all the time.
2. **Never edit files in `node_modules`.** If something goes wrong, delete the folder and run `npm install`.
3. **`package.json` is your recipe card.** It lists dependencies (ingredients) and scripts (cooking steps).
4. **React is a single-page app.** Everything runs inside one HTML page with a `<div id="root">`.
5. **The flow is: `index.html` loads `main.jsx`, which loads `App.jsx`.** This chain is how your app starts.

---

## Practice Questions

1. What is the purpose of the `src` folder? Why is it called `src`?

2. You want to change what your app shows on the screen. Which file do you edit?

3. A friend wants to try your project on their computer. Should you send them the `node_modules` folder? Why or why not?

4. What does `package.json` do? What real-life thing is it similar to?

5. Your app is not starting. You think a library might be broken. What can you try? (Hint: it involves `node_modules` and `npm install`.)

---

## Exercises

### Exercise 1: Change the Page Title

Open `index.html` and find this line:

```html
<title>Vite + React</title>
```

Change it to:

```html
<title>My First React App</title>
```

Save the file. Look at your browser tab. The title should change.

### Exercise 2: Edit the App Component

Open `src/App.jsx`. Replace everything inside the `return` statement with your own content:

```jsx
function App() {
  return (
    <div>
      <h1>Welcome to My App</h1>
      <p>I am learning React!</p>
    </div>
  )
}

export default App
```

Save the file. Your browser should update automatically and show your new content.

### Exercise 3: Explore `package.json`

Open `package.json` and answer these questions:

1. What is the name of your project?
2. How many dependencies does it have? What are they?
3. What command does the `"dev"` script run?

Write your answers down. Checking your own understanding is a great way to learn.

---

## What Is Next?

You now know your way around a React project. You know where to find things and which files to edit. You have a map of the house.

In the next chapter, we will learn about **JSX** — the special way React lets you write what your app looks like. It looks a lot like HTML, but it has some important differences. JSX is one of the things that makes React special and fun to use. Let us go learn about it!
