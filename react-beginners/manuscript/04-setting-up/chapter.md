# Chapter 4: Setting Up a React Project

## What You Will Learn

In this chapter, you will learn:

- What tools you need to start building with React
- How to install Node.js on your computer
- What npm is and why you need it
- How to create your first React project using Vite
- How to start your project and see it in the browser
- What each file and folder in your new project does
- How to fix common errors that beginners run into

## Why This Chapter Matters

Imagine you just bought a new toolkit. Before you can build anything, you need to open the box, lay out the tools, and learn what each one does. This chapter is that moment. We are opening the box, setting everything up, and making sure it all works. By the end, you will have a working React project running on your computer. That is a real achievement, and everything you learn from this point forward will build on it.

---

## What You Need: Two Essential Tools

To work with React, you need two things installed on your computer:

1. **Node.js** — A program that lets you run JavaScript outside of a web browser
2. **A code editor** — A program where you write your code (we recommend Visual Studio Code)

Let us look at each one.

### What Is Node.js?

In the early days of the web, JavaScript could only run inside a browser. You could not use it anywhere else. Node.js changed that. It lets you run JavaScript on your computer, outside the browser.

Think of it this way. JavaScript is like a fish. In the old days, the fish could only live in one pond (the browser). Node.js is a second pond. Now the fish can live in both places.

You might wonder: "If React runs in the browser, why do I need Node.js?" Good question. You need Node.js because the tools that *help you build* React projects run on your computer, not in the browser. These tools turn your code into files that the browser can understand. Node.js also comes with a tool called **npm**, which we will talk about shortly.

### What Is a Code Editor?

A code editor is a program for writing code. You *could* write code in Notepad (Windows) or TextEdit (Mac), but a proper code editor gives you helpful features:

- **Syntax highlighting** — Different parts of your code show in different colors, making it easier to read.
- **Auto-complete** — The editor suggests code as you type, like predictive text on your phone.
- **Error detection** — The editor underlines mistakes before you even run your code.
- **Built-in terminal** — You can type commands without leaving the editor.

We recommend **Visual Studio Code** (often called "VS Code"). It is free, works on Windows, Mac, and Linux, and almost every React developer uses it.

---

## Step 1: Install Node.js

### On Windows

1. Open your web browser.
2. Go to the website: **https://nodejs.org**
3. You will see two big green download buttons. Click the one that says **"LTS"** (this stands for Long Term Support — it is the most stable version).
4. A file will download. It will be called something like `node-v20.x.x-x64.msi`.
5. Double-click the downloaded file.
6. A setup wizard will appear. Click "Next" on each screen. You can keep all the default settings.
7. Click "Install" when you reach the final screen.
8. Wait for the installation to finish, then click "Finish".

### On Mac

1. Open your web browser.
2. Go to the website: **https://nodejs.org**
3. Click the **"LTS"** download button.
4. A file will download. It will be called something like `node-v20.x.x.pkg`.
5. Double-click the downloaded file.
6. Follow the steps in the installer. Click "Continue" and "Agree" until the installation completes.

### On Linux

Open a terminal and type:

```bash
sudo apt update
sudo apt install nodejs npm
```

Type your password when asked, and press Enter.

### How to Check If Node.js Is Installed Correctly

Now let us make sure it worked. This is an important step. Do not skip it.

1. **Open a terminal** (also called "command prompt" or "command line"):
   - **Windows**: Press the Windows key, type "cmd", and press Enter.
   - **Mac**: Press Command + Space, type "Terminal", and press Enter.
   - **Linux**: Press Ctrl + Alt + T.

2. Type this command and press Enter:

```bash
node --version
```

**What you should see:**

```
v20.11.0
```

The exact number might be different. That is fine. As long as you see a version number starting with `v`, Node.js is installed correctly.

3. Now type this command and press Enter:

```bash
npm --version
```

**What you should see:**

```
10.2.4
```

Again, the exact number might be different. As long as you see a number, npm is installed.

**If you see an error** like "command not found" or "'node' is not recognized", Node.js did not install correctly. Try these steps:
- Close your terminal and open a new one (sometimes the terminal needs a fresh start).
- If that does not work, restart your computer and try again.
- If it still does not work, go back to the Node.js website and reinstall.

---

## Step 2: Install Visual Studio Code

1. Go to **https://code.visualstudio.com** in your browser.
2. Click the big download button. The website will detect your operating system and give you the right version.
3. Run the downloaded file and follow the installation steps.
4. Open VS Code after installation.

**What you should see:** A welcome screen with a dark (or light) background. There will be tabs like "Get Started" or "Welcome". You are ready to go.

VS Code is your new workspace. You will spend a lot of time here, so take a moment to look around. Do not worry about all the buttons and menus. We will only use a few of them.

---

## What Is npm?

We mentioned npm earlier. Let us explain it properly.

**npm** stands for **Node Package Manager**. Think of it as an **app store for code**.

When you install an app on your phone, you go to the App Store or Google Play, find the app, and tap "Install". npm works the same way, but for code libraries. Want to use React? npm installs it for you. Want a tool that helps you format dates? npm installs that too. Want a library that makes animations easier? npm has it.

There are over one million packages (that is what code libraries are called in npm) available for free. When you install Node.js, npm comes with it automatically. That is why we checked for both `node --version` and `npm --version` earlier.

Here is a quick comparison:

| Feature | Phone App Store | npm |
|---|---|---|
| What it installs | Apps for your phone | Code libraries for your projects |
| How you use it | Tap a button | Type a command in the terminal |
| Cost | Some free, some paid | Almost everything is free |
| Number of items | Millions of apps | Over one million packages |

---

## Step 3: Create Your First React Project

Now for the exciting part. We are going to create a real React project. We will use a tool called **Vite** (pronounced "veet", like the French word for "fast"). Vite sets up everything you need to start a React project in just a few seconds.

### Open Your Terminal

You can use the terminal inside VS Code (which is very convenient) or a separate terminal. To open the terminal inside VS Code:

1. Open VS Code.
2. Click on "Terminal" in the top menu.
3. Click "New Terminal".

A panel will appear at the bottom of VS Code. This is your terminal.

### Navigate to Where You Want Your Project

Before creating the project, decide where on your computer you want to store it. We suggest creating a folder for all your coding projects. Let us use the Desktop for now (you can choose anywhere you like).

Type this command and press Enter:

**On Mac or Linux:**
```bash
cd ~/Desktop
```

**On Windows:**
```bash
cd %USERPROFILE%\Desktop
```

The `cd` command stands for "change directory". It moves you to a different folder. You just moved to your Desktop.

### Create the Project

Now type this command and press Enter:

```bash
npm create vite@latest my-first-app -- --template react
```

Let us break down what each part of this command means:

| Part | What It Does |
|---|---|
| `npm` | Use the npm tool |
| `create` | Tell npm to create something new |
| `vite@latest` | Use the latest version of the Vite tool |
| `my-first-app` | The name of your project (also the folder name) |
| `--` | Separates npm's options from Vite's options |
| `--template react` | Tell Vite to set up a React project (not a plain JavaScript project) |

**What you should see:**

The terminal will show some output. It might ask you to install the `create-vite` package. If it does, type `y` and press Enter to confirm.

After a few seconds, you will see a message like this:

```
Scaffolding project in /Users/yourname/Desktop/my-first-app...

Done. Now run:

  cd my-first-app
  npm install
  npm run dev
```

This message tells you three things to do next. Let us do them one at a time.

### Move into the Project Folder

```bash
cd my-first-app
```

This moves you into the folder that Vite just created for your project.

### Install the Dependencies

```bash
npm install
```

This command tells npm to download all the code libraries your project needs. React is one of them. npm reads a file called `package.json` inside your project folder to figure out what to download.

**What you should see:**

```
added 152 packages in 8s
```

The exact number of packages and time might be different. This is normal. npm just downloaded React and all the other tools your project needs.

**What if you see warnings?** You might see yellow warning messages that say things like "deprecated" or "WARN". In most cases, you can safely ignore these. They are not errors. They are just notes about packages that have newer versions available.

### Start the Development Server

```bash
npm run dev
```

This command starts a local **development server**. A development server is a small program that runs on your computer and serves your website to your browser. It is like having a tiny web server right on your machine.

**What you should see:**

```
  VITE v5.0.0  ready in 300 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

The important line is: **http://localhost:5173/**

This is the address where your website is running. Let us open it.

---

## Step 4: See Your App in the Browser

1. Open your web browser (Chrome, Firefox, Safari, or Edge).
2. In the address bar, type: **http://localhost:5173/**
3. Press Enter.

**What you should see:**

A page with the Vite and React logos. The logos might be spinning. There is a heading that says "Vite + React". Below that, there is a button that says "count is 0". If you click the button, the number goes up: "count is 1", "count is 2", and so on.

There is also text that says "Edit src/App.jsx and save to test HMR".

Congratulations! You are looking at your first React application. It is alive and running on your computer.

### What Is "localhost"?

The word **localhost** means "this computer". When you type `http://localhost:5173/` in your browser, you are telling the browser: "Show me the website that is being served from my own computer, on port 5173."

A **port** is like a door number on a building. Your computer has many ports (numbered from 0 to 65535). The development server picked port 5173 as its door. Your browser knocks on that door and the development server answers.

### How to Stop the Server

When you are done working, go back to your terminal and press **Ctrl + C** (on both Windows and Mac). This stops the development server. The website will no longer be available in your browser until you start the server again with `npm run dev`.

---

## What Is Inside Your Project?

Let us look at the files and folders that Vite created. Open the `my-first-app` folder in VS Code:

1. In VS Code, click "File" in the top menu.
2. Click "Open Folder".
3. Navigate to your Desktop, select the `my-first-app` folder, and click "Open".

You will see something like this in the file explorer on the left side:

```
my-first-app/
  |-- node_modules/       (a big folder — do not touch it)
  |-- public/              (files that go directly to the browser)
  |-- src/                 (your code lives here)
  |   |-- assets/          (images and other files)
  |   |-- App.css          (styling for the App component)
  |   |-- App.jsx          (the main component — this is important!)
  |   |-- index.css        (global styles)
  |   |-- main.jsx         (the starting point of your app)
  |-- .gitignore           (tells Git which files to ignore)
  |-- index.html           (the one HTML file for your app)
  |-- package.json         (lists your project's dependencies)
  |-- package-lock.json    (locks dependency versions)
  |-- vite.config.js       (settings for Vite)
```

Let us explain the important ones:

### node_modules/

This folder contains all the code libraries that npm downloaded when you ran `npm install`. It has thousands of files. **You should never edit anything in this folder.** If you delete it by accident, just run `npm install` again and it will come back.

### src/ (Source)

This is where **your** code lives. When you write React components, you will put them here. The most important file right now is `App.jsx`.

### App.jsx

This is the main component of your application. The `.jsx` extension stands for "JavaScript XML". It is a special type of JavaScript file that lets you write something that looks like HTML inside your JavaScript code. We will learn all about this in a later chapter.

### main.jsx

This is the **starting point** of your React application. It is the first file that runs. It loads the `App` component and puts it on the page.

### index.html

This is the one and only HTML file in your project. Yes, just one. React is a "single-page application" tool. It uses JavaScript to change what you see on the page instead of loading separate HTML files.

### package.json

This file lists all the code libraries your project depends on and includes scripts (commands) you can run. When you type `npm run dev`, npm looks in this file to find out what that command means.

---

## Let Us Make a Small Change

Let us prove that everything is connected. We will change one line of code and see the result in the browser instantly.

1. Make sure your development server is running (run `npm run dev` if it is not).
2. Open the file `src/App.jsx` in VS Code.
3. Find the line that says:

```jsx
<h1>Vite + React</h1>
```

4. Change it to:

```jsx
<h1>Hello World</h1>
```

5. Save the file (Ctrl + S on Windows, Command + S on Mac).

**What you should see:** Go back to your browser. The page will update automatically, without you pressing refresh. The heading will now say "Hello World" instead of "Vite + React".

This automatic updating feature is called **HMR**, which stands for **Hot Module Replacement**. It means that when you save a file, the browser shows the change instantly. No manual refreshing needed. This makes development fast and enjoyable.

---

## Understanding the Code in App.jsx

Let us look at the code inside `App.jsx` step by step. Do not worry if it looks unfamiliar. We will explain every line.

```jsx
import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.jsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  )
}

export default App
```

Here is a line-by-line explanation:

**Line 1:** `import { useState } from 'react'`
This loads a tool called `useState` from the React library. We will learn about `useState` in a later chapter. For now, just know it lets your component remember things (like the current count).

**Line 2:** `import reactLogo from './assets/react.svg'`
This loads the React logo image so we can show it on the page.

**Line 3:** `import viteLogo from '/vite.svg'`
This loads the Vite logo image.

**Line 4:** `import './App.css'`
This loads the CSS styling file for this component.

**Line 6:** `function App() {`
This creates a component called `App`. In React, a component is just a JavaScript function that returns what should appear on the screen.

**Line 7:** `const [count, setCount] = useState(0)`
This creates a piece of data called `count` that starts at 0. `setCount` is a function that changes the count. We will explain this fully in a later chapter.

**Line 9:** `return (`
Everything inside the parentheses after `return` is what will appear on the page. This is called **JSX** — it looks like HTML but it is written inside JavaScript.

**Lines 10-28:** The JSX code that describes the page. It includes logos, a heading, a button, and some text. Notice how it looks like HTML with tags like `<div>`, `<h1>`, `<button>`, and `<p>`.

**Line 19:** `<button onClick={() => setCount((count) => count + 1)}>`
When the user clicks this button, the count goes up by one. `onClick` is how React handles button clicks.

**Line 20:** `count is {count}`
The curly braces `{}` let you put JavaScript values inside JSX. Here it shows the current value of `count`.

**Line 31:** `export default App`
This makes the `App` component available to other files. The `main.jsx` file imports `App` and puts it on the page.

---

## Common Errors and How to Fix Them

Here are problems that beginners often run into, along with solutions.

### Error: "command not found: node" or "'node' is not recognized"

**What it means:** Node.js is not installed, or your terminal cannot find it.

**How to fix it:**
- Close your terminal and open a new one.
- If that does not work, restart your computer.
- If it still does not work, reinstall Node.js from https://nodejs.org.

### Error: "npm ERR! code EACCES" (Permission denied)

**What it means:** Your computer is not letting npm write files.

**How to fix it (Mac/Linux):**
- Add `sudo` before the command: `sudo npm create vite@latest my-first-app -- --template react`
- Type your password when asked.

**How to fix it (Windows):**
- Right-click on your terminal program and select "Run as Administrator".

### Error: "ENOENT: no such file or directory"

**What it means:** You are in the wrong folder.

**How to fix it:**
- Make sure you ran `cd my-first-app` after creating the project.
- Use `ls` (Mac/Linux) or `dir` (Windows) to see what files are in your current folder.

### Error: "Port 5173 is already in use"

**What it means:** Another program is already using port 5173, or you have another development server still running.

**How to fix it:**
- Check if you have another terminal running `npm run dev`. If so, stop it with Ctrl + C.
- If no other server is running, Vite will usually pick the next available port (like 5174). Look at the terminal output for the correct URL.

### The Page Is Blank

**What it means:** There might be an error in your code.

**How to fix it:**
- Open your browser's developer tools (press F12 or right-click the page and select "Inspect").
- Click on the "Console" tab.
- Look for red error messages. They will usually tell you which file and line number has the problem.
- Go back to VS Code and check that file.

### Nothing Happens When I Save

**What it means:** The development server might have stopped, or there is a syntax error in your code.

**How to fix it:**
- Check your terminal. If the server stopped, run `npm run dev` again.
- Check for syntax errors. A common one is forgetting to close a tag. Every opening tag like `<div>` needs a closing tag like `</div>`.

---

## Quick Summary

In this chapter, you installed Node.js and Visual Studio Code, the two essential tools for React development. You learned that npm is like an app store for code. You created your first React project using the command `npm create vite@latest my-first-app -- --template react`. You installed the project's dependencies with `npm install`, started the development server with `npm run dev`, and saw your app running in the browser. You made a small change to `App.jsx` and watched the browser update automatically. You also learned what each file and folder in your project does and how to fix common errors.

---

## Key Points to Remember

1. **Node.js** lets you run JavaScript outside the browser. You need it for the tools that build your React project.
2. **npm** is the Node Package Manager. It downloads and manages code libraries for your projects.
3. **VS Code** is the recommended code editor. It is free and has many helpful features.
4. The command **`npm create vite@latest my-first-app -- --template react`** creates a new React project.
5. **`npm install`** downloads all the code libraries your project needs.
6. **`npm run dev`** starts a local development server so you can see your app in the browser.
7. Your code lives in the **`src/`** folder. The main file is **`App.jsx`**.
8. **HMR (Hot Module Replacement)** automatically updates the browser when you save a file.
9. **`localhost`** means "this computer". Your development server runs locally.
10. If something goes wrong, **check the terminal and browser console** for error messages.

---

## Practice Questions

1. What is Node.js, and why do you need it for React development?

2. What does npm stand for, and what does it do? Use the "app store" analogy to explain it.

3. What does the command `npm run dev` do?

4. What is the purpose of the `node_modules` folder? Should you edit files inside it?

5. What is HMR, and why is it useful when developing a React app?

---

## Exercises

### Exercise 1: Personalize Your App

Open `src/App.jsx` and make these changes:
- Change the heading from "Vite + React" to your name (for example, "Sarah's First App").
- Change the button text from "count is {count}" to "Clicked {count} times".
- Save the file and check that the changes appear in your browser.

### Exercise 2: Explore the Terminal

Without looking at the instructions above, try to answer these questions by typing commands in your terminal:
- What version of Node.js do you have? (Hint: `node --version`)
- What version of npm do you have? (Hint: `npm --version`)
- What files are in your project folder? (Hint: `ls` on Mac/Linux or `dir` on Windows)

### Exercise 3: Break It and Fix It

This exercise is about learning from mistakes. In `src/App.jsx`:
1. Delete one closing tag (for example, delete a `</div>`).
2. Save the file.
3. Look at your terminal and browser. What error messages do you see?
4. Now fix the error by adding the closing tag back. Save and check that the app works again.

Making mistakes and fixing them is one of the best ways to learn. Do not be afraid to break things. You can always undo your changes.

---

## What Is Next?

Your development environment is ready. You have a working React project. You have already changed some code and seen the result. You are officially a React developer (a beginner one, but that still counts!).

In the next chapter, we will take a closer look at JSX, the special syntax that lets you write HTML-like code inside JavaScript. You will learn why React uses it, what the rules are, and how to write your own JSX from scratch. Things are about to get really fun. Let us keep going!
