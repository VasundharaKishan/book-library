# Chapter 2: Setting Up Your Development Environment

---

## Learning Goals

By the end of this chapter, you will be able to:

- Install Node.js and npm on your computer
- Understand what Node.js and npm are and why React needs them
- Create a new React project using Vite
- Understand every file and folder in a React project
- Run a React development server and see your app in the browser
- Set up Visual Studio Code with useful extensions for React development
- Make your first change to a React application and see it update instantly
- Understand what hot module replacement (HMR) is

---

## Why Do You Need More Than Just a Browser?

In Chapter 1, we saw a plain HTML file with a `<script>` tag that ran JavaScript directly in the browser. You might be wondering: "Can I just write React code the same way — in an HTML file and open it in Chrome?"

Technically, you can — but you should not. Here is why.

Modern React code uses features that browsers do not understand natively:

1. **JSX**: That HTML-like syntax inside JavaScript (`<h1>Hello</h1>`) is not valid JavaScript. Browsers cannot run it directly. It needs to be transformed into regular JavaScript before the browser can execute it.

2. **ES Modules with npm packages**: When you write `import { useState } from "react"`, the browser does not know where to find the `react` package. You need a tool that resolves these imports and bundles everything together.

3. **Modern JavaScript features**: Some cutting-edge JavaScript features may not be supported in all browsers. A build tool can convert your code into a version that works everywhere.

You need a **development environment** — a set of tools that:
- Transforms your JSX into regular JavaScript
- Resolves and bundles your imports
- Serves your app locally so you can test it in a browser
- Automatically refreshes the browser when you change code
- Optimizes your code for production when you are ready to deploy

Let us set up that environment now.

---

## Installing Node.js and npm

### What Is Node.js?

Node.js is a JavaScript runtime that lets you run JavaScript outside of a browser — on your computer's command line. You will not write Node.js server code in this book, but you need Node.js installed because:

1. It runs the development tools (like Vite) that build and serve your React app.
2. It comes with **npm** (Node Package Manager), which you use to install React and other libraries.

Think of Node.js as the engine that powers your development tools, and npm as the app store where you download the packages (libraries) your project needs.

### What Is npm?

**npm** stands for Node Package Manager. It does two things:

1. **It is an online registry** — a massive collection of JavaScript packages (over 2 million) that developers have published for others to use. React itself is an npm package.

2. **It is a command-line tool** — a program you run in your terminal to install, update, and manage packages in your project.

When you run `npm install react`, npm goes to the online registry, downloads the React package, and puts it in your project's `node_modules` folder. It also records the dependency in a file called `package.json` so that anyone else working on your project can install the same packages.

### Installing Node.js

Node.js includes npm, so you only need to install Node.js.

**Step 1: Check if Node.js is already installed**

Open your terminal (Terminal on macOS/Linux, Command Prompt or PowerShell on Windows) and run:

```bash
node --version
```

If you see a version number like `v20.11.0` or higher, you already have Node.js installed. Skip to the next section.

If you see "command not found" or an error, you need to install it.

**Step 2: Download and install Node.js**

Go to the official Node.js website:

```
https://nodejs.org
```

You will see two download options:

- **LTS (Long Term Support)**: The stable, recommended version. **Choose this one.**
- **Current**: The latest version with newest features, but potentially less stable.

Download the LTS version for your operating system and run the installer. Accept the default settings.

**Step 3: Verify the installation**

After installation, close and reopen your terminal, then run:

```bash
node --version
```

You should see something like:

```
v20.11.0
```

Also check npm:

```bash
npm --version
```

You should see something like:

```
10.2.4
```

If both commands show version numbers, you are ready to go.

### A Note About Package Managers

npm is the default package manager that comes with Node.js, and it is what we will use in this book. You may hear about alternatives like **yarn** or **pnpm**. They do the same job as npm but with slight differences in speed and features. If you encounter a project that uses yarn or pnpm, the commands are similar:

| npm command           | yarn equivalent      | pnpm equivalent       |
|-----------------------|---------------------|-----------------------|
| `npm install`         | `yarn`              | `pnpm install`        |
| `npm install react`   | `yarn add react`    | `pnpm add react`      |
| `npm run dev`         | `yarn dev`          | `pnpm dev`            |

For this book, stick with npm. You can switch later if you prefer.

---

## What Is a Build Tool?

Before we create a React project, let us understand what a build tool does. This is important because it removes the mystery from what happens when you run your project.

A **build tool** is a program that takes your source code (what you write) and transforms it into code that the browser can actually run. Think of it as a translator between you and the browser.

Here is what a build tool does for a React project:

```
What You Write                    What the Browser Gets
─────────────────                 ─────────────────────

JSX:                              Regular JavaScript:
<h1>Hello</h1>           ──▶     React.createElement("h1", null, "Hello")

ES Modules:                       Bundled single file:
import { useState }       ──▶     (all code combined into one
from "react"                       or a few optimized files)

Modern JS:                        Compatible JS:
const x = arr?.length     ──▶     var x = arr ? arr.length : undefined
```

```
┌─────────────────────────────────────────────────────────┐
│                     BUILD TOOL                          │
│                                                         │
│   Source Code ──▶ Transform ──▶ Bundle ──▶ Output       │
│                                                         │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐           │
│   │ App.jsx  │   │Transform │   │ Bundle   │   .js     │
│   │ Home.jsx │──▶│ JSX to   │──▶│ into     │──▶files   │
│   │ About.jsx│   │ plain JS │   │ fewer    │   for     │
│   │ styles.css│  │          │   │ files    │   browser │
│   └──────────┘   └──────────┘   └──────────┘           │
│                                                         │
│   During development:                                   │
│   • Runs a local server (localhost:5173)                 │
│   • Watches for file changes                            │
│   • Updates the browser automatically (HMR)             │
│                                                         │
│   For production:                                       │
│   • Minifies code (removes whitespace, shortens names)  │
│   • Splits code into optimized chunks                   │
│   • Generates hashed filenames for caching              │
└─────────────────────────────────────────────────────────┘
```

### Why Vite?

There are several build tools for React. The most common ones are:

- **Vite** (pronounced "veet," French for "fast") — Modern, extremely fast, and simple to set up. Created by Evan You (creator of Vue.js) but works great with React.
- **Create React App (CRA)** — The old official tool for creating React projects. It is now **deprecated** (no longer maintained) and should not be used for new projects.
- **Next.js** — A full React framework that includes routing, server-side rendering, and more. Great for production apps but adds complexity. We will explore it briefly later in the book.

**We will use Vite** because:
1. It is the fastest option — development server starts in milliseconds.
2. It is simple — minimal configuration needed.
3. It is the current recommendation for starting new React projects.
4. It uses native ES modules during development, which means instant updates when you change code.

---

## Creating Your First React Project

Let us create a React project. Open your terminal and navigate to the folder where you want to keep your projects. For example:

```bash
cd ~/projects
```

If the `projects` folder does not exist, create it first:

```bash
mkdir ~/projects
cd ~/projects
```

Now run the Vite project creation command:

```bash
npm create vite@latest my-first-react-app -- --template react
```

Let us break down this command:

| Part | Meaning |
|------|---------|
| `npm create` | A shortcut for running a package's creation script |
| `vite@latest` | Use the latest version of Vite |
| `my-first-react-app` | The name of your project (also becomes the folder name) |
| `--` | Separates npm arguments from Vite arguments |
| `--template react` | Use the React template (plain JavaScript, not TypeScript) |

After running this command, you will see output like:

```
Scaffolding project in ./my-first-react-app...

Done. Now run:

  cd my-first-react-app
  npm install
  npm run dev
```

Follow those instructions:

```bash
cd my-first-react-app
npm install
```

The `npm install` command reads the `package.json` file and downloads all the packages your project depends on (React, React DOM, Vite, etc.) into a `node_modules` folder. This may take a minute the first time.

Now start the development server:

```bash
npm run dev
```

You will see:

```
  VITE v5.x.x  ready in 300 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

Open your browser and go to `http://localhost:5173/`. You should see the default Vite + React welcome page with a counter button and the Vite and React logos.

Congratulations — you are running your first React application!

### What Is localhost?

If you are new to web development, `localhost` might seem unfamiliar. It simply means "this computer." When you run `npm run dev`, Vite starts a small web server on your machine. `localhost:5173` tells your browser to connect to that server on port 5173. It is like having a mini web hosting service running on your own computer.

Nobody else can see your app — it is only running locally for development.

---

## Understanding the Project Structure

Let us look at every file and folder that Vite created. Open the project in Visual Studio Code:

```bash
code .
```

If the `code` command does not work, open VS Code manually and use File → Open Folder to open the `my-first-react-app` folder.

Here is the complete project structure:

```
my-first-react-app/
├── node_modules/          ← Downloaded packages (do not edit)
├── public/                ← Static assets served as-is
│   └── vite.svg           ← Vite logo (favicon)
├── src/                   ← Your application code lives here
│   ├── assets/            ← Images and other assets
│   │   └── react.svg      ← React logo
│   ├── App.css            ← Styles for the App component
│   ├── App.jsx            ← The main App component
│   ├── index.css           ← Global styles
│   └── main.jsx           ← The entry point of your application
├── .eslintrc.cjs          ← ESLint configuration (code quality tool)
├── .gitignore             ← Files that Git should ignore
├── index.html             ← The single HTML page
├── package-lock.json      ← Exact versions of installed packages
├── package.json           ← Project configuration and dependencies
└── vite.config.js         ← Vite configuration
```

Let us go through each important file in detail.

### index.html — The Single HTML Page

```html
<!doctype html>
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

This is the **only HTML file** in the entire project. Remember from Chapter 1 — React builds Single Page Applications. This one HTML file is the "single page."

Notice two critical things:

1. **`<div id="root"></div>`** — This is an empty div. React will inject your entire application into this div. Everything you build — every component, every page, every button — will live inside this single div.

2. **`<script type="module" src="/src/main.jsx">`** — This tells the browser to load and run the `main.jsx` file, which is the starting point of your React application. The `type="module"` attribute enables ES module syntax (import/export).

### src/main.jsx — The Entry Point

```jsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

This small file does something very important — it **connects React to the HTML page**. Let us break it down line by line:

**Line 1: `import { StrictMode } from 'react'`**

This imports `StrictMode` from the React library. Strict Mode is a development tool that helps you find potential problems in your code. It runs extra checks and shows warnings in the console. It does not affect the production build — it only activates during development.

What does StrictMode do specifically?
- It renders components twice during development to catch side effects that might cause bugs.
- It warns about deprecated features.
- It warns about unsafe practices.

You might notice your components rendering twice in development mode. That is StrictMode doing its job — do not be alarmed.

**Line 2: `import { createRoot } from 'react-dom/client'`**

This imports the `createRoot` function from `react-dom`. React itself is just the library for building components. `react-dom` is the bridge between React and the browser's DOM. `createRoot` creates a "root" — the connection point where React takes control of a DOM element.

Why are React and ReactDOM separate? Because React can render to different targets — the browser DOM (react-dom), mobile apps (react-native), and even terminal UIs. The core React library handles components and logic, while the renderer (react-dom, react-native) handles the specific platform.

**Line 3: `import './index.css'`**

This imports a CSS file. In a normal HTML page, you would use a `<link>` tag. In a Vite-powered React project, you can import CSS files directly in JavaScript. Vite handles adding these styles to the page.

**Line 4: `import App from './App.jsx'`**

This imports the `App` component — the root component of your application. Every React app has one top-level component that contains everything else.

**Lines 6–9: The render call**

```jsx
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

This does three things:
1. `document.getElementById('root')` — finds the empty `<div id="root">` in index.html
2. `createRoot(...)` — creates a React root connected to that div
3. `.render(...)` — tells React to render the `App` component inside that root

After this line runs, React takes control of the `#root` div and everything inside it is managed by React.

```
index.html                          React
┌─────────────────────┐             ┌─────────────────────┐
│ <html>              │             │                     │
│   <body>            │             │     App             │
│     <div id="root"> │◀── React ──▶│     ├── Header      │
│       (empty)       │   renders   │     ├── Main        │
│     </div>          │   into      │     └── Footer      │
│   </body>           │   this div  │                     │
│ </html>             │             │                     │
└─────────────────────┘             └─────────────────────┘
```

### src/App.jsx — The Root Component

Open `App.jsx` and you will see the default content Vite provides. It contains a counter example with logos and links. We will replace this with our own code shortly, but for now, notice:

- The file extension is `.jsx`, which means it contains JSX (HTML-like syntax in JavaScript).
- The file exports a function called `App` — this is a React component.
- The function returns JSX that describes what should appear on the screen.

### src/App.css and src/index.css — Style Files

- `index.css` contains global styles that apply to the entire application.
- `App.css` contains styles specific to the App component.

We will explore styling in depth in Chapter 18.

### package.json — The Project Configuration

```json
{
  "name": "my-first-react-app",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "eslint .",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  },
  "devDependencies": {
    "@eslint/js": "^9.17.0",
    "@types/react": "^19.0.2",
    "@types/react-dom": "^19.0.2",
    "@vitejs/plugin-react": "^4.3.4",
    "eslint": "^9.17.0",
    "eslint-plugin-react-hooks": "^5.0.0",
    "eslint-plugin-react-refresh": "^0.4.16",
    "globals": "^15.14.0",
    "vite": "^6.0.5"
  }
}
```

The important sections are:

**`scripts`** — Commands you can run with `npm run <script-name>`:
- `npm run dev` — Starts the development server
- `npm run build` — Creates an optimized production build
- `npm run lint` — Checks your code for potential errors
- `npm run preview` — Previews the production build locally

**`dependencies`** — Packages your app needs to run:
- `react` — The core React library
- `react-dom` — The React renderer for browsers

**`devDependencies`** — Packages needed only during development:
- `vite` — The build tool
- `eslint` — A code quality checker
- Various plugins for Vite and ESLint

The `^` symbol before version numbers means "compatible with." For example, `^19.0.0` means "any version from 19.0.0 up to (but not including) 20.0.0."

### node_modules/ — The Packages Folder

This folder contains all the downloaded packages and their dependencies. It is typically very large (hundreds of megabytes) and is **never** committed to version control. The `.gitignore` file already excludes it.

If you delete `node_modules/`, you can always recreate it by running `npm install`, which reads `package.json` and downloads everything again.

### vite.config.js — Vite Configuration

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
```

This file tells Vite to use the React plugin, which enables JSX transformation and React Fast Refresh (hot module replacement). For most projects, you do not need to change this file. We will revisit it when we add features like environment variables or path aliases later in the book.

### .gitignore — Files to Exclude from Git

This file tells Git which files and folders to ignore when tracking changes. The default includes:

- `node_modules/` — Too large, can be regenerated with `npm install`
- `dist/` — The production build output, can be regenerated with `npm run build`

---

## Making Your First Change

Let us replace the default Vite template with something of our own. This will prove that the development environment is working and introduce you to the development workflow.

### Step 1: Clear the Default Content

Open `src/App.jsx` and replace its entire content with:

```jsx
function App() {
  return (
    <div>
      <h1>Hello, React!</h1>
      <p>This is my first React application.</p>
    </div>
  );
}

export default App;
```

**What this code does:**
- We define a function called `App`. This is a React component.
- The function returns JSX — that HTML-like syntax. It describes a `<div>` containing an `<h1>` heading and a `<p>` paragraph.
- We export the component so `main.jsx` can import and use it.

**Why it is written this way:**
- Every React component is a function that returns JSX.
- The JSX must have a single root element (the outer `<div>`). You cannot return two sibling elements without wrapping them.
- We use `export default` so this component can be imported by name in other files.

**What would happen if done incorrectly:**
- If you removed the outer `<div>` and returned `<h1>` and `<p>` side by side, React would throw an error: "JSX expressions must have one parent element." We will learn a cleaner solution (Fragments) in Chapter 3.
- If you forgot `export default`, `main.jsx` would not be able to import the component and you would see an error.

### Step 2: Clean Up the Styles

Open `src/App.css` and delete all its content. We will add our own styles later.

Open `src/index.css` and replace it with a minimal reset:

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
  line-height: 1.6;
  color: #333;
  padding: 2rem;
}
```

**What this CSS does:**
- The `*` selector resets margins and padding on all elements, giving us a clean starting point.
- `box-sizing: border-box` makes width/height calculations more intuitive (padding is included in the element's width).
- The `body` styles set a clean, readable font, comfortable line height, dark gray text color, and some padding around the edges.

### Step 3: See the Result

If your development server is still running (from when you ran `npm run dev`), look at your browser. **The page should have already updated automatically.** You should see "Hello, React!" as a heading and "This is my first React application." as a paragraph, on a clean white page.

If the server is not running, start it:

```bash
npm run dev
```

Then open `http://localhost:5173/` in your browser.

### What Just Happened?

When you saved the file, Vite detected the change and updated the browser instantly — without you pressing refresh. This is called **Hot Module Replacement (HMR)**.

```
You save App.jsx
       │
       ▼
Vite detects the change
       │
       ▼
Vite recompiles only the changed module
       │
       ▼
Vite sends the update to the browser via WebSocket
       │
       ▼
Browser swaps the old module for the new one
       │
       ▼
Screen updates — no full page reload!
```

HMR is one of the biggest quality-of-life features in modern development. In the old days, you had to manually refresh the browser every time you made a change. With HMR:

- Changes appear instantly (usually in under 100 milliseconds)
- The application state is preserved (if you had typed something in a form, it stays)
- Only the changed component is updated, not the entire page

This tight feedback loop — change code, see result, change code, see result — makes development much faster and more enjoyable.

---

## Adding More Content

Let us expand our App component to practice the development workflow. Replace `src/App.jsx` with:

```jsx
function App() {
  return (
    <div>
      <header>
        <h1>My React Learning Journal</h1>
        <p>Documenting my journey with React</p>
      </header>

      <main>
        <section>
          <h2>What I Learned Today</h2>
          <ul>
            <li>React is a JavaScript library for building UIs</li>
            <li>React uses a Virtual DOM for efficient updates</li>
            <li>Vite is a fast build tool for React projects</li>
            <li>Components are the building blocks of React apps</li>
          </ul>
        </section>

        <section>
          <h2>Next Steps</h2>
          <p>In the next chapter, I will learn about JSX in depth.</p>
        </section>
      </main>

      <footer>
        <p>Built with React and Vite</p>
      </footer>
    </div>
  );
}

export default App;
```

Save the file and watch the browser update. You should see a simple page with a header, a list of things you learned, a "Next Steps" section, and a footer.

**What this code demonstrates:**
- A component can return complex, nested JSX.
- You can use standard HTML elements like `header`, `main`, `section`, `footer`, `ul`, and `li`.
- The JSX looks and behaves very much like HTML (with a few differences we will cover in Chapter 3).
- Everything is still wrapped in a single root `<div>`.

---

## Setting Up Visual Studio Code

Visual Studio Code (VS Code) is the most popular code editor for React development. If you have not installed it yet, download it from `https://code.visualstudio.com/`.

### Essential Extensions

Install these extensions to make your React development experience smoother. In VS Code, click the Extensions icon in the sidebar (or press `Ctrl+Shift+X` on Windows/Linux, `Cmd+Shift+X` on macOS) and search for each one:

**1. ES7+ React/Redux/React-Native snippets**

This extension provides shortcuts for common React patterns. For example:
- Type `rafce` and press Tab to generate a React Arrow Function Component with Export.
- Type `rfc` and press Tab to generate a React Function Component.

These snippets save you from typing boilerplate code repeatedly.

**2. Prettier — Code Formatter**

Prettier automatically formats your code when you save a file. It handles indentation, spacing, line breaks, and more, so your code always looks consistent.

After installing, enable "Format on Save":
1. Open VS Code Settings (`Ctrl+,` or `Cmd+,`)
2. Search for "Format On Save"
3. Check the box for "Editor: Format On Save"
4. Search for "Default Formatter"
5. Select "Prettier - Code formatter"

**3. ESLint**

ESLint checks your code for potential errors and bad practices. Vite already included ESLint in your project — this extension shows ESLint warnings and errors directly in your editor as you type, highlighted with squiggly underlines.

**4. Auto Rename Tag**

When you rename an opening HTML/JSX tag, this extension automatically renames the matching closing tag. For example, if you change `<div>` to `<section>`, the closing `</div>` becomes `</section>` automatically.

**5. Simple React Snippets** (alternative to ES7+ snippets)

A lighter alternative to the ES7+ extension. It provides fewer snippets but covers the essential ones.

You only need one snippet extension — either ES7+ or Simple React Snippets. Do not install both.

### Recommended VS Code Settings for React

Open your VS Code settings JSON file (`Ctrl+Shift+P` → "Open User Settings (JSON)") and consider adding these settings:

```json
{
  "editor.tabSize": 2,
  "editor.wordWrap": "on",
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "emmet.includeLanguages": {
    "javascript": "javascriptreact"
  }
}
```

**What each setting does:**
- `tabSize: 2` — React projects conventionally use 2-space indentation.
- `wordWrap: "on"` — Long lines wrap instead of requiring horizontal scrolling.
- `formatOnSave: true` — Automatically format code when you save.
- `defaultFormatter` — Use Prettier as the formatter.
- `emmet.includeLanguages` — Enables Emmet abbreviations in JSX files. Emmet lets you type shortcuts like `div.container>h1+p` and expand them into full HTML/JSX.

---

## Browser Developer Tools

Your browser's developer tools are essential for React development. Let us make sure you know how to access them and introduce one React-specific tool.

### Opening Developer Tools

- **Chrome**: Press `F12` or `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Option+I` (macOS)
- **Firefox**: Press `F12` or `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Option+I` (macOS)

The most useful tabs for React development are:

- **Console**: Shows errors, warnings, and `console.log()` output. You will use this constantly for debugging.
- **Elements/Inspector**: Shows the DOM tree. Useful for inspecting what React rendered.
- **Network**: Shows HTTP requests. Useful when your app fetches data from APIs.

### React Developer Tools

React Developer Tools is a browser extension created by the React team. It adds two new tabs to your browser's developer tools:

- **Components**: Shows your React component tree (not the DOM tree). You can inspect props, state, and hooks for any component. This is incredibly useful for debugging.
- **Profiler**: Shows how long each component takes to render. Useful for performance optimization.

**To install React Developer Tools:**

1. Open the Chrome Web Store (search "Chrome Web Store" in your browser)
2. Search for "React Developer Tools"
3. Click "Add to Chrome"

Or for Firefox:
1. Go to Firefox Add-ons
2. Search for "React Developer Tools"
3. Click "Add to Firefox"

After installing, open your React app, open developer tools, and you should see a "Components" tab. We will use this tool extensively in later chapters.

---

## Understanding the Development Workflow

Now that everything is set up, let us establish the workflow you will use throughout this book:

```
┌──────────────────────────────────────────────────────┐
│                Development Workflow                   │
│                                                       │
│   1. Start the dev server                             │
│      $ npm run dev                                    │
│          │                                            │
│          ▼                                            │
│   2. Open browser to localhost:5173                   │
│          │                                            │
│          ▼                                            │
│   3. Edit code in VS Code                             │
│          │                                            │
│          ▼                                            │
│   4. Save the file (Ctrl+S / Cmd+S)                  │
│          │                                            │
│          ▼                                            │
│   5. Browser updates automatically (HMR)              │
│          │                                            │
│          ▼                                            │
│   6. Check for errors in:                             │
│      • Browser (visual result)                        │
│      • Browser console (error messages)               │
│      • Terminal (build errors)                         │
│      • VS Code (ESLint warnings)                      │
│          │                                            │
│          ▼                                            │
│   7. Repeat steps 3–6                                 │
│                                                       │
│   8. Stop the server when done:                       │
│      Press Ctrl+C in the terminal                     │
└──────────────────────────────────────────────────────┘
```

**Tip**: Keep three things visible while developing:
1. VS Code (your code)
2. The browser (your app)
3. The browser console (for errors)

If you have a large monitor, split your screen. If you have two monitors, put VS Code on one and the browser on the other. This eliminates the constant switching between windows.

---

## Common Project Commands

Here is a reference of commands you will use frequently:

| Command | What it does |
|---------|-------------|
| `npm run dev` | Start the development server |
| `npm run build` | Create an optimized production build in the `dist/` folder |
| `npm run preview` | Preview the production build locally |
| `npm install <package>` | Install a new package and add it to `dependencies` |
| `npm install -D <package>` | Install a new package and add it to `devDependencies` |
| `npm run lint` | Check code for errors with ESLint |
| `Ctrl+C` (in terminal) | Stop the development server |

### The Difference Between dependencies and devDependencies

When installing a package, you choose where it goes:

- **`dependencies`** (`npm install react`): Packages your app needs to run. These are included in the production build. Examples: React, React Router, Axios.

- **`devDependencies`** (`npm install -D vite`): Packages needed only during development. These are NOT included in the production build. Examples: Vite, ESLint, testing libraries.

The distinction matters because it affects the size of your production build. Only `dependencies` are bundled into the final JavaScript files that users download.

---

## Mini Project: Customizing the Welcome Page

Let us build something slightly more substantial to solidify the workflow. We will create a personal "About Me" card.

Replace the content of `src/App.jsx` with:

```jsx
function App() {
  const name = "Your Name";
  const role = "Aspiring React Developer";
  const skills = ["HTML", "CSS", "JavaScript", "React (learning!)"];
  const currentYear = new Date().getFullYear();

  return (
    <div style={{ maxWidth: "600px", margin: "0 auto", textAlign: "center" }}>
      <div
        style={{
          backgroundColor: "#f0f4f8",
          borderRadius: "12px",
          padding: "2rem",
          marginTop: "2rem",
        }}
      >
        <div
          style={{
            width: "100px",
            height: "100px",
            borderRadius: "50%",
            backgroundColor: "#4a90d9",
            margin: "0 auto 1rem",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "white",
            fontSize: "2.5rem",
            fontWeight: "bold",
          }}
        >
          {name.charAt(0)}
        </div>

        <h1 style={{ marginBottom: "0.5rem", color: "#1a202c" }}>{name}</h1>
        <p style={{ color: "#718096", marginBottom: "1.5rem" }}>{role}</p>

        <h3 style={{ marginBottom: "0.75rem", color: "#2d3748" }}>
          My Skills
        </h3>
        <div
          style={{
            display: "flex",
            gap: "0.5rem",
            justifyContent: "center",
            flexWrap: "wrap",
          }}
        >
          {skills.map(function (skill) {
            return (
              <span
                key={skill}
                style={{
                  backgroundColor: "#4a90d9",
                  color: "white",
                  padding: "0.25rem 0.75rem",
                  borderRadius: "9999px",
                  fontSize: "0.875rem",
                }}
              >
                {skill}
              </span>
            );
          })}
        </div>
      </div>

      <p style={{ marginTop: "2rem", color: "#a0aec0", fontSize: "0.875rem" }}>
        © {currentYear} — Built with React and Vite
      </p>
    </div>
  );
}

export default App;
```

Save the file and look at your browser. You should see a centered card with:
- A blue circle showing the first letter of the name
- The name and role
- A row of skill badges
- A footer with the current year

**What this code teaches you (preview of coming chapters):**

1. **JavaScript variables in JSX**: The `name`, `role`, `skills`, and `currentYear` variables are used inside the JSX with curly braces `{}`. Anything inside `{}` is evaluated as JavaScript.

2. **Inline styles**: React uses a JavaScript object for inline styles instead of a CSS string. Notice `style={{ backgroundColor: "#f0f4f8" }}` — the outer `{}` means "this is JavaScript," and the inner `{}` is the style object. CSS property names use camelCase (`backgroundColor` instead of `background-color`).

3. **Rendering a list**: The `skills.map(...)` transforms an array of strings into an array of `<span>` elements. We will cover this in detail in Chapter 7.

4. **The `key` prop**: Each `<span>` in the list has a `key={skill}` prop. React uses keys to efficiently track list items. We will explain why in Chapter 7.

5. **Dynamic values**: `{name.charAt(0)}` takes the first character of the name, and `{currentYear}` shows the current year. These are just regular JavaScript expressions.

**Try these changes to practice the workflow:**

1. Change the `name` variable to your actual name. Save and watch the card update.
2. Add a new skill to the `skills` array. Save and watch a new badge appear.
3. Change the `backgroundColor` of the circle from `#4a90d9` to `#e53e3e` (red) or `#38a169` (green).
4. Try removing the `key={skill}` from the `<span>` and check your browser console — you should see a warning from React.

Each of these changes demonstrates the instant feedback loop of the development workflow.

---

## Stopping and Restarting the Server

When you are done developing, stop the server by pressing `Ctrl+C` in the terminal where `npm run dev` is running.

The next time you want to work on your project:

```bash
cd my-first-react-app
npm run dev
```

You do not need to run `npm install` again unless you have deleted `node_modules/` or added new packages to `package.json`.

**When do you need to restart the server?**

Most of the time, you do not. HMR handles code changes automatically. However, you need to restart the server if you:

- Change `vite.config.js` (Vite configuration)
- Install a new npm package (the server usually detects this, but a restart ensures it works)
- Change environment variables (we will cover this later)

To restart, press `Ctrl+C` and then run `npm run dev` again.

---

## Common Mistakes

1. **Running `npm run dev` in the wrong directory.**
   You must be inside the project folder (where `package.json` is) when running npm commands. If you see "Missing script: dev" or similar errors, check that you are in the right folder with `pwd` (print working directory).

2. **Editing files inside `node_modules/`.**
   Never edit files in `node_modules/`. Your changes will be lost the next time someone runs `npm install`. If you need to change a package's behavior, there are proper ways to do it (we will not need to in this book).

3. **Committing `node_modules/` to Git.**
   The `node_modules` folder can contain hundreds of thousands of files. The `.gitignore` file already excludes it, but if you set up Git manually, make sure `node_modules/` is listed in `.gitignore`.

4. **Forgetting to run `npm install` after cloning a project.**
   When you download or clone a project from GitHub, it does not include `node_modules/`. You must run `npm install` first to download the dependencies.

5. **Using Create React App (CRA).**
   If you find tutorials using `npx create-react-app`, know that CRA is deprecated. It is no longer maintained and produces slower, larger projects. Always use Vite for new React projects.

6. **Port already in use.**
   If you see "Port 5173 is already in use," it means another process is using that port. Either stop the other process (maybe you have another `npm run dev` running in a different terminal) or Vite will automatically try the next port (5174, 5175, etc.).

7. **Not saving the file before expecting changes.**
   HMR only triggers when you save the file. If you edit code but do not see changes in the browser, make sure you actually saved (`Ctrl+S` / `Cmd+S`).

---

## Best Practices

1. **Keep the terminal visible.** Build errors and warnings appear in the terminal. If your app is not updating or looks broken, check the terminal output first.

2. **Use the browser console.** React warnings and errors appear in the browser console. Keep it open while developing (`F12` → Console tab).

3. **Install React Developer Tools early.** Having the Components tab in your developer tools is invaluable, even at this early stage. It helps you see how React "sees" your application.

4. **Set up Prettier and enable Format on Save.** Consistent formatting makes code easier to read and prevents formatting-related merge conflicts when working in a team.

5. **Use a `.jsx` extension for files containing JSX.** While Vite can handle JSX in `.js` files, using `.jsx` makes it clear which files contain JSX and helps your editor provide better support (syntax highlighting, auto-complete).

6. **Keep one terminal dedicated to `npm run dev`.** Do not close it or use it for other commands. If you need to run other commands (like `npm install`), open a second terminal tab or window.

7. **Create a `.prettierrc` file in your project root** to ensure consistent formatting across your team. A simple starting configuration:

```json
{
  "semi": true,
  "singleQuote": false,
  "tabWidth": 2,
  "trailingComma": "es5"
}
```

This tells Prettier to use semicolons, double quotes, 2-space indentation, and trailing commas where valid in ES5.

---

## Summary

In this chapter, you learned:

- **Node.js** is a JavaScript runtime needed to run development tools. **npm** is the package manager used to install libraries like React.
- **Vite** is a modern, fast build tool that transforms your JSX and modern JavaScript into code browsers can run. It replaces the deprecated Create React App.
- You created a React project with `npm create vite@latest`, installed dependencies with `npm install`, and started the dev server with `npm run dev`.
- The **project structure** includes `index.html` (the single page), `main.jsx` (the entry point that connects React to the DOM), `App.jsx` (the root component), and `package.json` (project configuration).
- **Hot Module Replacement (HMR)** automatically updates the browser when you save a file, without losing application state.
- **VS Code extensions** like Prettier, ESLint, and React snippets improve the development experience.
- **React Developer Tools** is a browser extension that lets you inspect your React component tree.
- The development workflow is: edit code → save → see result → check for errors → repeat.

---

## Interview Questions

**Q1: What is the difference between `npm install` and `npm run dev`?**

`npm install` reads the `package.json` file and downloads all listed dependencies into the `node_modules` folder. You run it once after cloning a project or when adding new packages. `npm run dev` starts the development server (Vite), which serves your application locally, watches for file changes, and provides hot module replacement. You run it every time you want to work on your project.

**Q2: Why is Vite preferred over Create React App for new projects?**

Create React App (CRA) is deprecated and no longer maintained. Vite is preferred because it starts faster (milliseconds vs seconds), uses native ES modules during development for instant hot module replacement, produces smaller production builds, has a simpler configuration, and is actively maintained with a strong community. CRA used Webpack under the hood, which bundles the entire application before serving — Vite only transforms files when they are requested, making it significantly faster.

**Q3: What is the purpose of the `<div id="root">` in index.html?**

It is the mount point for the React application. The `createRoot` function in `main.jsx` connects React to this div element. React then renders the entire component tree inside this div and manages all DOM updates within it. Everything you see on screen in a React app lives inside this single div element.

**Q4: What is Hot Module Replacement (HMR)?**

HMR is a development feature that updates the browser in real-time when you change and save a source file, without performing a full page reload. Only the changed module is swapped out, which means application state (like form inputs, scroll position) is preserved. This creates a faster feedback loop during development compared to manually refreshing the browser.

**Q5: What is the difference between `dependencies` and `devDependencies` in `package.json`?**

`dependencies` are packages required for the application to run in production — they are included in the final build that users download. Examples: React, React Router, Axios. `devDependencies` are packages needed only during development — they are NOT included in the production build. Examples: Vite, ESLint, testing libraries, TypeScript. The distinction helps keep the production bundle size small.

**Q6: Why are React and ReactDOM separate packages?**

React (the `react` package) contains the core library for defining components, hooks, and the component model. ReactDOM (`react-dom`) is the renderer that knows how to put React components into the browser's DOM. They are separated because React can target different platforms — `react-dom` renders to the browser, `react-native` renders to iOS/Android, and other renderers exist for terminals, PDFs, and more. The core React library is platform-agnostic.

**Q7: What is StrictMode and should you keep it in production?**

StrictMode is a development-only tool that wraps your component tree and enables extra checks: it double-renders components to detect side effects, warns about deprecated APIs, and flags unsafe practices. It has zero impact on production — React automatically strips it out from production builds. You should keep it enabled during development because it catches bugs early. The double-rendering behavior it causes only happens in development mode.

---

## Practice Exercises

**Exercise 1: Create a New Vite Project**

Create a brand-new Vite React project from scratch. Practice the entire flow:
1. Run the creation command
2. Install dependencies
3. Start the development server
4. Open it in the browser
5. Open it in VS Code
6. Make a change and confirm HMR works
7. Stop the server

Do this without looking at the instructions above. If you get stuck, check the chapter, but try from memory first.

**Exercise 2: Explore the Package**

Open `package.json` and answer these questions:
1. What version of React is installed?
2. How many `dependencies` are there? What are they?
3. How many `devDependencies` are there? List three of them.
4. What are the four scripts you can run? What does each one do?

**Exercise 3: Break It on Purpose**

Try each of these and observe what happens (error messages, behavior). After each one, undo the change:

1. Delete the `<div id="root">` from `index.html`. What error do you see?
2. Remove the `export default App` line from `App.jsx`. What happens?
3. In App.jsx, return two sibling elements without a wrapper (remove the outer `<div>` and return `<h1>` and `<p>` next to each other). What does the error say?
4. Rename `App.jsx` to `App.js`. Does the project still work?
5. Delete `node_modules/` and try running `npm run dev`. What happens? How do you fix it?

Breaking things on purpose teaches you to recognize error messages and fix them quickly. This is one of the most valuable skills in development.

**Exercise 4: Build Your Own About Page**

Create a personal about page that includes:
- Your name as a heading
- A short paragraph about yourself
- A list of your hobbies (at least 3)
- A link to your favorite website (use an `<a>` tag)
- A footer with the text "Made while learning React"

Use only the concepts from this chapter — a single `App.jsx` component with JSX. Do not worry about styling beyond what looks readable.

**Exercise 5: Explore React Developer Tools**

Install React Developer Tools in your browser. Open your React app, then open developer tools and find the Components tab. Answer these questions:
1. What component(s) do you see in the tree?
2. Click on the App component — what information does the panel show?
3. If you used the mini project code with `skills.map(...)`, can you see the rendered list items in the Components tab?

---

## What Is Next?

You now have a fully working React development environment. You can create projects, write components, save files, and see changes instantly in the browser. This workflow will carry you through the entire book.

In Chapter 3, we will take a deep dive into **JSX** — the HTML-like syntax you have been writing inside your components. You will learn exactly what JSX is, how it differs from HTML, all the rules you need to follow, and how to write dynamic, expressive UI descriptions. JSX is the foundation of everything you build in React, so understanding it deeply is essential.
