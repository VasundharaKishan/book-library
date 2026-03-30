# Chapter 2: Why Do People Use React?

## What You Will Learn

In this chapter, you will learn:

- Why building big websites with plain HTML, CSS, and JavaScript gets hard
- How React makes building websites easier
- What "reusable components" means and why they save time
- Famous websites that use React
- What the word "library" means in programming
- When React is a good choice and when you do not need it

## Why This Chapter Matters

Before you learn any tool, it helps to know *why* that tool exists. Imagine someone hands you a power drill. If you do not know what problems a power drill solves, you will not know when to use it. This chapter shows you the problems that web developers faced before React. Once you see those problems, React will make a lot more sense.

---

## The Problem: Building Big Websites Is Hard

Let us start with something you already know. You have visited websites like Facebook, Instagram, or Netflix. These websites have thousands of buttons, menus, images, and moving parts. Everything updates instantly. You click a "like" button and the number changes right away. You type in a search box and results appear as you type.

Now imagine building all of that with just HTML, CSS, and JavaScript. Let us see why that gets difficult.

### Problem 1: Repeating Yourself Over and Over

Think about Instagram. Every post on your feed looks the same. It has a user photo, a username, an image, a like button, and a comment section. If you have 100 posts on the screen, do you write the same HTML 100 times?

With plain HTML, you would have to copy and paste the same block of code again and again. If you later decide to change the design of a post (maybe you want to add a "share" button), you would need to find and update all 100 copies. That is slow, boring, and easy to mess up.

### Problem 2: Keeping the Page Up to Date

Imagine you click the "like" button on a post. The number should go from 42 to 43. With plain JavaScript, you have to:

1. Find the right number on the page
2. Read its current value
3. Add one to it
4. Put the new number back on the page

That sounds simple for one button. But what if clicking that button also changes a notification counter at the top of the page? And updates a "liked posts" list in the sidebar? Now you have to find and update three different places. On a big website, one action might need to update ten or twenty different parts of the page. Keeping track of all those updates is where most mistakes happen.

### Problem 3: Speed

Every time you change something on a web page, the browser has to do a lot of work. It has to recalculate where everything goes, repaint the screen, and check if anything else moved. If you change many things one at a time, the browser does all that work again and again. This makes the page feel slow.

---

## How React Solves These Problems

React was created by a team at Facebook in 2013. They were facing exactly the problems above. Their website was getting bigger and harder to manage. So they built a tool to help. That tool is React.

Let us see how React fixes each problem.

### Solution 1: Reusable Pieces (Components)

React lets you build your website from small, reusable pieces. These pieces are called **components**. A component is like a Lego block.

Think about Lego blocks. Each block is small and simple on its own. But you can snap them together to build a house, a car, or a spaceship. If you want to change the wheels on your Lego car, you just swap out the wheel pieces. You do not rebuild the whole car.

React works the same way. You build a small piece once (like a "Post" component) and then use it as many times as you want. If you need 100 posts, you use the same component 100 times. If you want to add a "share" button to every post, you change the component in one place, and every post on the page updates automatically.

Here is what that looks like as an idea (do not worry about the code yet):

```
Post component:
  - User photo
  - Username
  - Image
  - Like button
  - Comment section

Page:
  - Post (Alice's photo)
  - Post (Bob's photo)
  - Post (Carol's photo)
  ... reuse the same Post block 100 times
```

One component. Used many times. Changed in one place.

### Solution 2: Automatic Updates

With React, you do not tell the browser *how* to update the page. Instead, you tell React *what* the page should look like. React figures out how to make it happen.

Think of it like ordering food at a restaurant. With plain JavaScript, you are going into the kitchen yourself. You find the pan, turn on the stove, cook the food, and put it on the plate. With React, you just tell the waiter what you want. The kitchen handles the rest.

When data changes (like a "like" count going from 42 to 43), React automatically finds every place on the page that uses that data and updates it. You do not have to track anything yourself. This means fewer mistakes and less stress.

### Solution 3: Speed (The Virtual DOM)

React uses a clever trick to keep things fast. It does not change the real web page every time something updates. Instead, it keeps a lightweight copy of the page in memory. This copy is called the **Virtual DOM** (we will explain this in detail in the next chapter).

When something changes, React first updates the lightweight copy. Then it compares the copy to the real page. It finds the smallest number of changes needed and applies only those changes. This is much faster than updating the whole page.

Think of it like editing a document. Instead of rewriting the entire document every time you fix a typo, you just fix the one word that changed. React does the same thing with your web page.

---

## Real Websites That Use React

React is not just a learning exercise. Some of the biggest websites in the world use it every day:

- **Facebook** — React was born here. The entire Facebook website is built with React.
- **Instagram** — The web version of Instagram uses React to show your feed, stories, and messages.
- **Netflix** — The Netflix website uses React to show you movie and TV show listings.
- **Airbnb** — The Airbnb website uses React for searching listings, viewing photos, and booking stays.
- **WhatsApp Web** — The browser version of WhatsApp uses React.
- **Dropbox** — The Dropbox file management interface uses React.

These are websites used by billions of people. The fact that they trust React tells you it is a reliable and powerful tool.

---

## Lego Blocks vs. Carving from Wood

Let us compare two ways of building things.

### Approach 1: Carving from One Piece of Wood

Imagine you want to make a toy house. You take a large block of wood and start carving. You carve the walls, the roof, the windows, and the door — all from one piece. It looks beautiful.

But what if you want to change the door? You cannot just pull it off. It is part of the whole block. You might have to carve the entire house again.

This is what building a big website with plain HTML and JavaScript feels like. Everything is connected. Changing one part can break other parts.

### Approach 2: Building with Lego Blocks

Now imagine building that same toy house with Lego blocks. The walls are separate pieces. The roof is a separate piece. The door is a separate piece.

Want to change the door? Pull it off and snap on a new one. Want to add a second floor? Stack more blocks on top. Want to build a second house? You already have all the block designs. Just assemble another one.

This is how React works. Each component is a separate block. You can change, remove, or add blocks without breaking the rest of the house.

| Feature | Carving (Plain HTML/JS) | Lego Blocks (React) |
|---|---|---|
| Making changes | Hard — might break other parts | Easy — change one block |
| Reusing designs | Start from scratch each time | Reuse the same block |
| Finding problems | Hard — everything is tangled | Easy — check one block |
| Working in a team | Difficult — people get in each other's way | Easy — each person works on their own blocks |

---

## What Is a "Library"?

You might hear people call React a **library**. What does that word mean?

In everyday life, a library is a place where you borrow books. You pick the books you need and leave the rest on the shelves. You are in control. You decide which books to read and when.

A programming **library** works the same way. It is a collection of tools that someone else wrote. You pick the tools you need and use them in your project. You are still in control of your project. You decide when and where to use the library.

React is a library. It gives you tools for building user interfaces (the part of a website that people see and interact with). You decide how to use those tools. You can use React for your entire website, or just for one small part of it.

### Library vs. Framework

You might also hear the word **framework**. A framework is different from a library. Think of it this way:

- **Library**: You are the chef. The library is a set of kitchen tools (a blender, a mixer, a knife set). You decide what to cook and which tools to use.
- **Framework**: The framework is a meal kit delivery service. It gives you a recipe, the ingredients, and step-by-step instructions. You follow the plan it gives you.

A framework controls the flow of your project. A library lets you control the flow yourself.

React is a library, not a framework. This means you have more freedom in how you use it. But it also means you sometimes need to pick additional tools yourself (for example, a tool for navigating between pages). We will talk about those additional tools later in the book.

---

## When Is React a Good Choice?

React is great for many projects, but it is not always the best choice. Let us look at when to use it and when not to.

### Use React When:

- **Your website has many interactive parts.** If users click buttons, fill forms, see live updates, or interact with the page a lot, React is a great fit.
- **Your website reuses similar pieces.** If your page shows a list of products, a feed of posts, or a grid of cards, React components save you time.
- **Your website is big and will keep growing.** React helps you organize large projects so they do not become a tangled mess.
- **You work in a team.** Different team members can work on different components without stepping on each other's toes.

### You Might Not Need React When:

- **Your website is simple and mostly static.** If you are building a personal blog or a single landing page with no interactive features, plain HTML and CSS might be all you need.
- **Your website is a small project with one or two pages.** The setup time for React might be more than the time you save.
- **You just want to display information.** If your page does not change after it loads and users do not interact with it much, React adds complexity you do not need.

Think of it this way: you would not use a power drill to hang a single picture frame. A hammer and a nail are enough. But if you are building a bookshelf with 50 screws, the power drill saves you a lot of time and effort.

---

## Quick Summary

In this chapter, you learned that building big websites with plain HTML, CSS, and JavaScript is hard because you repeat yourself, tracking updates is tricky, and performance can suffer. React solves these problems by giving you reusable components (like Lego blocks), automatic updates (tell React what you want, not how to do it), and fast performance through the Virtual DOM.

React is a library, which means it is a set of tools you control. It is used by some of the biggest websites in the world, including Facebook, Instagram, Netflix, and Airbnb. React is a great choice for interactive, growing websites, but simple static pages may not need it.

---

## Key Points to Remember

1. **Reusable components** save time. Build once, use many times, update in one place.
2. **Automatic updates** reduce mistakes. You describe what the page should look like, and React handles the rest.
3. **The Virtual DOM** makes React fast by only changing what actually needs to change.
4. **React is a library**, not a framework. You are in control.
5. React is best for **interactive websites** that have many moving parts.
6. Simple, static websites **do not need React**.
7. Major companies like Facebook, Instagram, Netflix, and Airbnb trust React for their websites.

---

## Practice Questions

1. Name two problems that developers face when building big websites with plain HTML and JavaScript.

2. What is a React component? Describe it using your own analogy (you can use Lego blocks or any other analogy you like).

3. What is the difference between a library and a framework? Which one is React?

4. Give an example of a website where React would be a good choice. Explain why.

5. Give an example of a website where React would NOT be needed. Explain why.

---

## Exercises

### Exercise 1: Spot the Repetition

Go to any social media website (like Twitter, Instagram, or Reddit). Look at the feed. Find one piece of the design that repeats over and over (for example, each post or each comment). Write down all the parts that piece contains (like profile picture, username, text, like button, etc.). This is what a React component would represent.

### Exercise 2: Think Like a Component Designer

Imagine you are building an online store. The store shows a list of products. Each product has:
- A product image
- A product name
- A price
- An "Add to Cart" button

Draw a simple sketch (on paper or in a notes app) of what one product card would look like. Now imagine you have 20 products. How many times would you reuse your product card component? If you wanted to add a "star rating" to every product, how many places would you need to change?

### Exercise 3: Library or Framework?

For each description below, decide if it sounds more like a library or a framework:

a) "Here is a recipe. Follow steps 1 through 10 in order."
b) "Here is a set of paintbrushes. Paint whatever you like."
c) "Put your code in these specific folders and name your files this way."

---

## What Is Next?

Now you know *why* React exists and what problems it solves. But how does it actually work behind the scenes? In the next chapter, we will look at how your browser shows web pages, what the DOM is, and how React's Virtual DOM makes everything fast. Do not worry — there will be no code yet. Just clear explanations and simple analogies. Let us keep going!
