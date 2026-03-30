# Chapter 1: What Is React?

---

## What You Will Learn

- What React is, explained in plain words
- Where React came from
- What React is used to build
- The difference between a website and a web application
- Why React is one of the most popular tools for building websites today

## Why This Chapter Matters

Before you start learning any tool, it helps to understand what it is and what it does. Think of it this way: before you learn to drive a car, you should know what a car is and what it is used for. This chapter gives you that basic understanding of React. No code yet. Just clear ideas.

---

## Let Us Start from the Very Beginning

### What Is a Website?

You use websites every day. When you open Google to search for something, you are using a website. When you scroll through Instagram, watch videos on YouTube, or read the news online, you are using websites.

A website is simply a page (or a collection of pages) that you can view in a browser. A browser is the app you use to visit websites. Google Chrome, Safari, Firefox, and Microsoft Edge are all browsers.

Every website is built using code. The code tells the browser what to show and how to show it.

### What Are Web Applications?

Some websites are simple. A blog that shows articles is simple. You read the article, and that is it.

But some websites are more complex. Think about Gmail. You can read emails, write emails, search through emails, delete emails, and organize them into folders. Gmail is not just a page you read. It is more like an app you use.

When a website behaves like an app, we call it a **web application** (or **web app** for short). Web apps are interactive. They respond to what you do. They update without reloading the entire page.

Here are some examples of web applications:

- **Gmail** - You read, write, and manage emails
- **Facebook** - You post, like, comment, and chat
- **Google Maps** - You search, zoom, and get directions
- **Netflix** - You browse, search, and watch videos
- **Spotify** - You search, play, and create playlists

Building these kinds of web apps is complex. There is a lot of code to write, a lot of things to keep track of, and a lot of things that can go wrong. This is where React helps.

---

## So, What Is React?

**React is a tool that helps you build web applications.** That is it. That is the simplest explanation.

More specifically, React is a **JavaScript library** for building **user interfaces**.

Let us break that down into plain language:

- **JavaScript** is a programming language. It is the language that makes websites interactive. When you click a button and something happens, that is JavaScript at work.

- **Library** means a collection of pre-written code that you can use. Instead of writing everything from scratch, you use the code that React gives you. Think of a library like a toolbox. You do not build your own hammer. You take the hammer from the toolbox and use it.

- **User interface** (often shortened to **UI**) is everything the user sees and interacts with on the screen. Buttons, text, images, forms, menus, pop-ups, lists. All of that is the user interface.

So, putting it all together:

**React is a collection of pre-written JavaScript code that helps you build the things users see and interact with on a website.**

### A Real-Life Analogy

Imagine you want to build a house. You could cut down trees, make your own bricks, forge your own nails, and do everything from scratch. That would take forever.

Or you could go to a hardware store, buy pre-made bricks, nails, doors, and windows, and put them together. Much faster.

React is like that hardware store. It gives you ready-made pieces (called **components**, which we will learn about later) that you can put together to build your website.

---

## Where Did React Come From?

React was created by **Facebook** (now called Meta) in 2013. Facebook had a problem. Their website was getting very big and very complex. Millions of people were using it at the same time. The code was becoming hard to manage.

Facebook's engineers needed a better way to build and update the user interface. So they created React. It worked so well that they shared it with the world for free. Today, React is **open source**, which means anyone can use it, study it, and contribute to it without paying anything.

Since 2013, React has grown to become one of the most popular tools for building websites. Thousands of companies use it, including:

- Facebook and Instagram
- Netflix
- Airbnb
- Uber
- Twitter (now X)
- WhatsApp Web
- Dropbox

---

## What Can You Build with React?

You can build almost any kind of web application with React:

- **Social media apps** (like Facebook or Twitter)
- **Online stores** (like Amazon or Shopify)
- **Dashboards** (admin panels with charts and tables)
- **Chat applications** (like WhatsApp Web)
- **Video streaming apps** (like Netflix)
- **Blogs and news sites**
- **Portfolio websites**
- **To-do lists and note-taking apps**
- **Weather apps**
- **Calculator apps**

In this book, we will build some of these together, step by step.

---

## React Is Not the Whole Website

This is an important thing to understand early on. React only handles the **user interface** (what people see and click on). It does not handle things like:

- Storing data in a database
- Sending emails
- Processing payments
- User login on the server

Those things are handled by other tools and technologies on the **back end** (the part of the application that runs on a server, not in the browser).

React runs in the **front end** (the part that runs in the browser, the part users see).

```
What the user sees:          What happens behind the scenes:
+-------------------+        +----------------------------+
|                   |        |                            |
|  React handles    |        |  Other tools handle this   |
|  this part        |  <-->  |  (servers, databases,      |
|  (the screen)     |        |   payment systems, etc.)   |
|                   |        |                            |
+-------------------+        +----------------------------+
    Front End                        Back End
    (Browser)                        (Server)
```

You do not need to know anything about the back end to learn React. We will focus entirely on what happens in the browser.

---

## How Is React Different from HTML and CSS?

If you have heard of HTML and CSS, you might wonder: "Do I still need them if I use React?"

Yes! React works **with** HTML and CSS, not instead of them. Let us understand what each one does:

- **HTML** (HyperText Markup Language) defines the **structure** of a page. It says "here is a heading, here is a paragraph, here is an image, here is a button."

- **CSS** (Cascading Style Sheets) defines the **look** of a page. It says "this heading should be blue, this button should be round, this text should be large."

- **JavaScript** defines the **behavior** of a page. It says "when the user clicks this button, show a message."

- **React** is built on top of JavaScript. It gives you a smarter, easier way to combine HTML, CSS, and JavaScript together to build interactive pages.

```
Building a Website:
+-----------------------------------------------+
|                                                |
|  HTML  = The skeleton (structure)              |
|  CSS   = The clothes (appearance)              |
|  JS    = The brain (behavior)                  |
|  React = A smarter brain (better behavior)     |
|                                                |
+-----------------------------------------------+
```

You do not need to be an expert in HTML, CSS, or JavaScript before learning React. But knowing the basics will help. If you know what a heading is, what a button is, and what it means to "click something," you are ready.

---

## A Very Quick Peek at React Code

Do not worry about understanding this code right now. We will explain every piece later. This is just to give you a tiny preview of what React code looks like:

```jsx
function Welcome() {
  return <h1>Hello! Welcome to React.</h1>;
}
```

That is a React **component**. It is a small piece of code that shows a heading on the screen that says "Hello! Welcome to React."

See how short it is? Just three lines. That is one of the nice things about React. You can build small pieces like this and then combine them to build bigger things.

We will learn exactly how this works in the coming chapters. For now, just notice that it looks almost like a mix of JavaScript and HTML. That is by design. React lets you write HTML-like code inside JavaScript. This makes it easy to describe what should appear on the screen.

---

## Key Words You Will Hear Often

Here are some words that will come up a lot in this book. Do not memorize them now. Just read them so they feel familiar later:

| Word | Simple Meaning |
|------|----------------|
| **Component** | A small, reusable piece of a website (like a button, a card, or a menu) |
| **JSX** | The special way React lets you write HTML-like code inside JavaScript |
| **Props** | Information you pass to a component (like giving instructions to someone) |
| **State** | Information that a component remembers and can change (like a counter that goes up when you click) |
| **Hook** | A special React function that lets you add features to your components |
| **Render** | The process of showing something on the screen |

We will learn each of these in detail in later chapters. For now, just know they exist.

---

## Quick Summary

Let us recap what we learned in this chapter:

- A **website** is a page you view in a browser. A **web application** is a website that works like an app.
- **React** is a JavaScript library that helps you build user interfaces (the things users see and interact with).
- React was created by Facebook in 2013 and is free to use.
- React handles only the **front end** (what users see), not the back end (servers and databases).
- React works **with** HTML and CSS, not instead of them.
- React lets you build small pieces called **components** and combine them to build complete web pages.

## Key Points to Remember

1. React is a tool for building what users see on screen.
2. React is a JavaScript library, not a programming language.
3. React is free, open source, and used by thousands of companies.
4. You write React code using a mix of JavaScript and HTML-like syntax.
5. React focuses on the front end only.

## Practice Questions

1. In your own words, what is React?
2. What is the difference between a website and a web application? Give one example of each.
3. React handles the front end. What does "front end" mean?
4. Name three web applications that are built with React.
5. What is a "component" in simple terms?

## Exercises

1. Open your browser and visit three websites. For each one, decide: is it a simple website or a web application? Write down why you think so.

2. Look at the screen of any app you use daily (Instagram, YouTube, Gmail, etc.). Try to identify different parts of the screen: the header, the buttons, the text areas, the images. Each of those could be a React component. Write down at least five parts you notice.

3. In a notebook or document, write one paragraph explaining React to a friend who has never heard of it. Use your own words. Keep it simple.

---

## What Is Coming Next?

In the next chapter, we will answer the question: **Why do people use React instead of just writing plain JavaScript?** You will understand the specific problems React solves and why it has become so popular. This will give you motivation to keep learning!
