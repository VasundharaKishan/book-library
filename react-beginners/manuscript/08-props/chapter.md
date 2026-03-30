# Chapter 8: Props

## What You Will Learn

In this chapter, you will learn:

- What props are and why they are essential
- How to pass different types of data to a component
- How to read props inside a component
- The shortcut way to read props (destructuring)
- Why props are read-only and cannot be changed
- How to set default values for props
- How to pass props to multiple components
- What the special `children` prop is

## Why This Chapter Matters

In the last chapter, you learned how to create components. But those components were static. They always showed the same thing. A `Greeting` component always said "Hello, welcome!" no matter what.

In real apps, components need to be flexible. A name tag component should show different names. A product card should show different products. A button should show different text.

Props make this possible. Props are how you **pass information to a component** so it can show different things each time you use it.

Think of a component like a greeting card **template** at a store. The template has spaces for a name and a message. When you buy the card, you fill in the blanks. Props are the blanks you fill in.

---

## What Are Props?

Props is short for **properties**. Props are pieces of information that you pass to a component from the outside.

Think of props like **passing a note to someone**. You write information on the note and hand it over. The person reads the note and uses that information.

```
You (parent component)          Greeting (child component)
+------------------+           +------------------------+
|                  |           |                        |
| "Hey Greeting,   |  props   | "I received the note.  |
|  the name is     | -------> |  The name is Sarah.    |
|  Sarah."         |           |  I will show it."      |
|                  |           |                        |
+------------------+           +------------------------+
```

The parent component passes data. The child component receives and uses it.

---

## Passing Your First Prop

Let us start with a simple example. We will make a `Greeting` component that shows a personalized message.

### Step 1: Pass the Prop

When you use a component, you pass props like HTML attributes:

```jsx
function App() {
  return (
    <div>
      <Greeting name="Sarah" />
      <Greeting name="James" />
      <Greeting name="Maria" />
    </div>
  )
}
```

**Lines 4-6:** We use the `Greeting` component three times. Each time, we pass a different `name` prop. It looks just like an HTML attribute.

### Step 2: Receive the Prop

The component receives all props as a single object (a collection of key-value pairs). This object is passed as the first parameter of the function:

```jsx
function Greeting(props) {
  return <h1>Hello, {props.name}!</h1>
}
```

**Line 1:** The function takes one parameter called `props`. This is an object that contains all the props that were passed.

**Line 2:** We access the name by writing `props.name`.

### The Complete Example

```jsx
function Greeting(props) {
  return <h1>Hello, {props.name}!</h1>
}

function App() {
  return (
    <div>
      <Greeting name="Sarah" />
      <Greeting name="James" />
      <Greeting name="Maria" />
    </div>
  )
}
```

**Expected output:**

```
Hello, Sarah!
Hello, James!
Hello, Maria!
```

One component, three different results. That is the power of props.

---

## Passing Different Types of Data

You can pass many types of data as props. Let us see each one.

### Strings

For text, use quotes:

```jsx
<UserCard name="Alice" city="Tokyo" />
```

### Numbers

For numbers, use curly braces:

```jsx
<UserCard age={25} score={98.5} />
```

Why curly braces? Because in JSX, curly braces mean "this is a JavaScript value." The number `25` is a JavaScript value, not text.

If you write `age="25"`, it becomes the text string "25," not the number 25. This matters if you want to do math with it later.

### Booleans

A boolean is a value that is either `true` or `false`. Think of it like a light switch: on or off.

```jsx
<UserCard isOnline={true} isPremium={false} />
```

There is a shortcut for `true`. If you write just the prop name without a value, it defaults to `true`:

```jsx
// These two are the same:
<UserCard isOnline={true} />
<UserCard isOnline />
```

### A Complete Example with Multiple Types

```jsx
function ProductCard(props) {
  return (
    <div>
      <h2>{props.name}</h2>
      <p>Price: ${props.price}</p>
      <p>{props.inStock ? "In Stock" : "Sold Out"}</p>
    </div>
  )
}

function App() {
  return (
    <div>
      <ProductCard name="Notebook" price={4.99} inStock={true} />
      <ProductCard name="Pen Set" price={12.50} inStock={false} />
    </div>
  )
}
```

**Expected output:**

```
Notebook
Price: $4.99
In Stock

Pen Set
Price: $12.5
Sold Out
```

**Line 6:** The ternary expression `props.inStock ? "In Stock" : "Sold Out"` checks if the product is in stock. If `true`, it shows "In Stock." If `false`, it shows "Sold Out."

---

## Destructuring Props (The Shortcut Way)

Writing `props.name`, `props.age`, and `props.city` everywhere can feel repetitive. There is a shortcut called **destructuring**. Destructuring means pulling out specific values from an object and giving them their own names.

### Without Destructuring

```jsx
function Greeting(props) {
  return <h1>Hello, {props.name}! You are {props.age} years old.</h1>
}
```

### With Destructuring

```jsx
function Greeting({ name, age }) {
  return <h1>Hello, {name}! You are {age} years old.</h1>
}
```

**Line 1:** Instead of writing `props`, we write `{ name, age }`. This pulls `name` and `age` directly out of the props object.

**Line 2:** Now we can write `{name}` instead of `{props.name}`. Shorter and cleaner.

Both ways do exactly the same thing. Destructuring is just a shortcut. Most React developers prefer it because it is easier to read.

Think of it like receiving a package. Without destructuring, you get the whole box and reach inside for each item. With destructuring, the items are unpacked and laid out on the table for you.

```
Without destructuring:        With destructuring:
+------------------+          name = "Sarah"
| props            |   -->    age = 25
|   name: "Sarah"  |          city = "Paris"
|   age: 25        |
|   city: "Paris"  |
+------------------+
```

---

## Props Are Read-Only

This is a very important rule: **you cannot change props inside a component.**

Props are like a **letter you received**. You can read the letter. You can use the information in the letter. But you cannot change what the letter says. The sender wrote it, and you just receive it.

```jsx
// WRONG — This will cause an error!
function Greeting({ name }) {
  name = "Someone Else"  // DO NOT do this!
  return <h1>Hello, {name}!</h1>
}
```

React will show an error or unexpected behavior if you try to change props. This rule exists for a good reason: it keeps your app predictable. If a parent passes `name="Sarah"`, the component should always show "Sarah." If components could change their own props, it would be very hard to understand what your app is doing.

If you need a value that can change, you will learn about **state** in a later chapter. State is like a whiteboard inside your component: you can write on it, erase it, and write something new.

---

## Default Props

Sometimes a prop is optional. If the parent does not pass it, you want a fallback value. This is called a **default prop**.

You set default values using the `=` sign in the destructuring:

```jsx
function Greeting({ name = "Friend", color = "blue" }) {
  return (
    <h1 style={{ color: color }}>
      Hello, {name}!
    </h1>
  )
}
```

**Line 1:** If `name` is not provided, it will be `"Friend"`. If `color` is not provided, it will be `"blue"`.

Now you can use the component with or without those props:

```jsx
function App() {
  return (
    <div>
      <Greeting name="Sarah" color="red" />
      <Greeting name="James" />
      <Greeting />
    </div>
  )
}
```

**Expected output:**

```
Hello, Sarah!       (in red)
Hello, James!       (in blue — default color)
Hello, Friend!      (in blue — both defaults used)
```

- **Line 4:** Both props are provided. Shows "Sarah" in red.
- **Line 5:** Only `name` is provided. `color` uses the default value "blue."
- **Line 6:** No props are provided. Both default values are used.

Default props are like the pre-printed text on a form. If you do not fill in the blank, the default text is used.

---

## Passing Props to Multiple Components

In real apps, you often pass props through several layers of components. The data flows downward, from parent to child to grandchild.

```jsx
function App() {
  return <UserProfile name="Sarah" age={28} />
}

function UserProfile({ name, age }) {
  return (
    <div>
      <UserName name={name} />
      <UserAge age={age} />
    </div>
  )
}

function UserName({ name }) {
  return <h2>{name}</h2>
}

function UserAge({ age }) {
  return <p>Age: {age}</p>
}
```

**Expected output:**

```
Sarah
Age: 28
```

Here is how the data flows:

```
App
 |  passes name="Sarah" and age={28}
 v
UserProfile
 |  passes name to UserName
 |  passes age to UserAge
 v              v
UserName      UserAge
shows "Sarah" shows "Age: 28"
```

Data in React flows in **one direction**: from parent to child. This is called **one-way data flow**. It makes your app easier to understand because you always know where the data comes from.

---

## The Children Prop

There is a special prop called `children`. It represents whatever you put **between** the opening and closing tags of a component.

### Regular Props (Self-Closing)

```jsx
<Greeting name="Sarah" />
```

### Using Children (Opening and Closing Tags)

```jsx
<Card>
  <h2>Hello!</h2>
  <p>This is inside the card.</p>
</Card>
```

Everything between `<Card>` and `</Card>` becomes the `children` prop.

### How to Use Children Inside a Component

```jsx
function Card({ children }) {
  return (
    <div style={{
      border: "1px solid gray",
      padding: "16px",
      borderRadius: "8px"
    }}>
      {children}
    </div>
  )
}
```

**Line 1:** We destructure `children` from the props.

**Line 8:** We place `{children}` where we want the content to appear.

### Using the Card Component

```jsx
function App() {
  return (
    <div>
      <Card>
        <h2>Welcome</h2>
        <p>This is my first card.</p>
      </Card>

      <Card>
        <h2>About Me</h2>
        <p>I am learning React!</p>
      </Card>
    </div>
  )
}
```

**Expected output:**

```
+---------------------------+
| Welcome                   |
| This is my first card.    |
+---------------------------+

+---------------------------+
| About Me                  |
| I am learning React!      |
+---------------------------+
```

Each `Card` shows different content, but they all have the same border and padding. The `children` prop lets you create **wrapper components** — components that provide a common look while accepting any content inside.

Think of `children` like a picture frame. The frame is always the same (the `Card` component with its border and padding). But you can put any picture inside it (the `children`).

---

## Mini Project: Greeting Card Component

Let us put everything together and build a greeting card component that accepts a name and a message.

```jsx
function GreetingCard({ name, message, color = "black" }) {
  return (
    <div style={{
      border: "2px solid " + color,
      padding: "20px",
      margin: "10px",
      borderRadius: "10px"
    }}>
      <h2 style={{ color: color }}>Dear {name},</h2>
      <p>{message}</p>
      <p style={{ fontStyle: "italic" }}>With love</p>
    </div>
  )
}

function App() {
  return (
    <div>
      <h1>Greeting Cards</h1>

      <GreetingCard
        name="Mom"
        message="Thank you for everything you do!"
        color="red"
      />

      <GreetingCard
        name="Best Friend"
        message="You always make me laugh. Never change!"
        color="blue"
      />

      <GreetingCard
        name="Teacher"
        message="Thank you for your patience and wisdom."
      />
    </div>
  )
}
```

**Expected output:**

```
Greeting Cards

+--- red border -------------------+
| Dear Mom,                        |
| Thank you for everything you do! |
| With love                        |
+----------------------------------+

+--- blue border ------------------+
| Dear Best Friend,                |
| You always make me laugh.        |
| Never change!                    |
| With love                        |
+----------------------------------+

+--- black border (default) -------+
| Dear Teacher,                    |
| Thank you for your patience      |
| and wisdom.                      |
| With love                        |
+----------------------------------+
```

Let us break down the `GreetingCard` component:

**Line 1:** It accepts three props: `name`, `message`, and `color` (with a default of `"black"`).

**Line 3-8:** The outer `div` creates a bordered card. The border color comes from the `color` prop.

**Line 9:** The greeting uses the `name` prop.

**Line 10:** The body uses the `message` prop.

**Line 11:** Every card has "With love" in italics.

Notice how the third card does not pass a `color` prop. It uses the default value `"black"`.

---

## Quick Summary

- Props are how you pass data from a parent component to a child component.
- Props are passed like HTML attributes: `<Greeting name="Sarah" />`.
- Inside the component, you read props from the function parameter.
- Destructuring `{ name, age }` is a shortcut to access props directly.
- Props are read-only. A component cannot change its own props.
- Default props provide fallback values when a prop is not passed.
- The `children` prop represents content placed between a component's opening and closing tags.
- Data flows one way in React: from parent to child.

---

## Key Points to Remember

1. **Props are like notes passed to a component.** They carry information the component needs to do its job.
2. **Use curly braces for non-string values.** Strings get quotes. Numbers, booleans, and expressions get curly braces.
3. **Destructuring makes your code cleaner.** Write `{ name }` instead of `props` and then `props.name`.
4. **Never change props.** They are read-only. If you need something that changes, you will use state (coming in a future chapter).
5. **The `children` prop is special.** It lets you create wrapper components that accept any content inside them.

---

## Practice Questions

1. What are props? Explain them using a real-life analogy.

2. What is the difference between passing `age="25"` and `age={25}`? Why does it matter?

3. Why are props read-only? What should you use instead if you need a value that can change?

4. What is destructuring? Write a component that uses destructuring to receive `title` and `author` props.

5. What is the `children` prop? When would you use it?

---

## Exercises

### Exercise 1: Create a Book Component

Create a `Book` component that accepts `title`, `author`, and `pages` as props. Use it three times in `App` to show three different books.

```jsx
function Book({ title, author, pages }) {
  return (
    <div>
      <h3>{title}</h3>
      <p>by {author}</p>
      <p>{pages} pages</p>
    </div>
  )
}

function App() {
  return (
    <div>
      <h1>My Book Shelf</h1>
      <Book title="The Great Gatsby" author="F. Scott Fitzgerald" pages={180} />
      <Book title="To Kill a Mockingbird" author="Harper Lee" pages={281} />
      <Book title="1984" author="George Orwell" pages={328} />
    </div>
  )
}
```

Try adding a fourth book of your choice.

### Exercise 2: Add Default Props

Create a `Button` component that accepts a `label` and a `color` prop. Give `color` a default value of `"gray"`. Test it with and without the `color` prop.

```jsx
function Button({ label, color = "gray" }) {
  return (
    <button style={{ backgroundColor: color, padding: "10px 20px" }}>
      {label}
    </button>
  )
}

function App() {
  return (
    <div>
      <Button label="Submit" color="green" />
      <Button label="Cancel" color="red" />
      <Button label="Info" />
    </div>
  )
}
```

What color does the "Info" button have?

### Exercise 3: Use the Children Prop

Create a `Container` component that wraps its children in a styled box. Then use it to wrap different content.

```jsx
function Container({ title, children }) {
  return (
    <div style={{
      border: "2px solid navy",
      padding: "15px",
      margin: "10px"
    }}>
      <h2>{title}</h2>
      {children}
    </div>
  )
}

function App() {
  return (
    <div>
      <Container title="Section 1">
        <p>This is the first section.</p>
        <p>It has two paragraphs.</p>
      </Container>

      <Container title="Section 2">
        <p>This section has different content.</p>
        <ul>
          <li>Item one</li>
          <li>Item two</li>
        </ul>
      </Container>
    </div>
  )
}
```

Notice how each `Container` has the same style but different content inside it. That is the `children` prop at work.

---

## What Is Next?

You now know how to create components and pass data to them with props. Your components can show different content depending on what information they receive. This is a huge step!

But what if you want your component to **remember things** and **change over time**? What if you want a counter that goes up when you click a button? What if you want to show or hide something? Props cannot do this because props are read-only.

For that, you need **State** — the component's own personal memory. In the next chapter, you will learn how state works and how to make your components interactive and dynamic. Get ready for things to come alive!
