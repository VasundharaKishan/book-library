# Chapter 12: Lists and Keys — Showing Many Items

## What You Will Learn

- Why lists are important in apps
- How the `map()` function works
- How to render a list of items in React
- What keys are and why React needs them
- The rules for choosing good keys
- The common mistake of forgetting keys (and how to fix the warning)
- How to display a list of objects
- How to build a simple shopping list display

## Why This Chapter Matters

Think about the apps you use every day. Almost all of them show lists:

- A to-do app shows a **list** of tasks
- An email app shows a **list** of messages
- A store shows a **list** of products
- A social media app shows a **list** of posts

```
+---------------------+
| My Shopping List    |
|---------------------|
| - Milk              |
| - Eggs              |
| - Bread             |
| - Butter            |
| - Apples            |
+---------------------+
```

You could write each item by hand:

```jsx
<li>Milk</li>
<li>Eggs</li>
<li>Bread</li>
<li>Butter</li>
<li>Apples</li>
```

But what if you have 100 items? Or what if the items come from a database and you do not know how many there will be? You cannot write them all by hand. You need a way to say: "Take this list of data and create one component for each item." That is what this chapter teaches you.

---

## The map() Function Explained Simply

Before we use lists in React, you need to understand one JavaScript function: **`map()`**.

`map()` means: **do the same thing to every item in a list and give me a new list with the results.**

Think of it like a factory assembly line:

```
Raw materials go in:     [apple, banana, cherry]
                            |       |       |
                            v       v       v
Machine does the      (add "juice" to each name)
same thing to each:
                            |       |       |
                            v       v       v
Finished products:   [apple juice, banana juice, cherry juice]
```

Here is a simple JavaScript example:

```jsx
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(function(number) {
  return number * 2;
});
// doubled is now [2, 4, 6, 8, 10]
```

Let us break this down:
- We have a list of numbers: `[1, 2, 3, 4, 5]`.
- We call `.map()` on the list.
- Inside `map()`, we write a function that takes one item (we call it `number`) and does something with it (multiply by 2).
- `map()` runs this function once for each item: `1*2=2`, `2*2=4`, `3*2=6`, `4*2=8`, `5*2=10`.
- We get a new list with the results: `[2, 4, 6, 8, 10]`.

The original list is not changed. `map()` always creates a new list.

### Shorter Way with Arrow Functions

Most React developers write `map()` with an arrow function:

```jsx
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(number => number * 2);
// doubled is now [2, 4, 6, 8, 10]
```

This does exactly the same thing, just in one line. The arrow `=>` means "do this." So `number => number * 2` means "take a number, multiply it by 2, and return the result."

---

## Rendering a List of Items

Now let us use `map()` in React to show a list on the screen.

```jsx
function FruitList() {
  const fruits = ['Apple', 'Banana', 'Cherry', 'Date', 'Elderberry'];

  return (
    <ul>
      {fruits.map(fruit => (
        <li key={fruit}>{fruit}</li>
      ))}
    </ul>
  );
}
```

### Expected Output

```
- Apple
- Banana
- Cherry
- Date
- Elderberry
```

### Line-by-Line Explanation

**Line 2:** `const fruits = ['Apple', 'Banana', 'Cherry', 'Date', 'Elderberry'];`
We create an array (a list) of fruit names.

**Line 5:** `<ul>`
We start an unordered list. This is a regular HTML element that shows bullet points.

**Line 6:** `{fruits.map(fruit => (`
Inside curly braces `{ }` (because we are writing JavaScript inside JSX), we call `map()` on the `fruits` array. For each fruit in the array, the function runs.

**Line 7:** `<li key={fruit}>{fruit}</li>`
For each fruit, we create a list item (`<li>`) that shows the fruit's name. The `key={fruit}` part is something new — we will explain it in the next section.

**Line 8:** `))}`
Close the arrow function, close the `map()`, and close the curly braces.

**Line 9:** `</ul>`
Close the unordered list.

### What map() Does Here

```
fruits array:        ['Apple', 'Banana', 'Cherry']
                        |         |         |
                        v         v         v
map() creates:    <li>Apple</li>  <li>Banana</li>  <li>Cherry</li>
                        |         |         |
                        v         v         v
React shows:         - Apple
                     - Banana
                     - Cherry
```

Each string in the array becomes an `<li>` element on the screen. If you add more fruits to the array, more list items appear automatically.

---

## What Are Keys and Why React Needs Them

You probably noticed the `key={fruit}` in the previous example. Let us explain what that is.

A **key** is a special label that helps React tell items apart. Think of keys like **name tags at a party**.

```
Party without name tags:           Party with name tags:
+--------+--------+--------+      +--------+--------+--------+
| Person | Person | Person |      |  ALEX  |  BETH  | CHRIS  |
|   ?    |   ?    |   ?    |      |        |        |        |
+--------+--------+--------+      +--------+--------+--------+

"Who left? Who's new?              "Alex left, Dana joined,
 I have no idea!"                   Beth and Chris stayed."
```

Without name tags, if someone leaves and someone new arrives, you cannot tell what happened. With name tags, you can track exactly who is who.

React works the same way. When your list changes (items added, removed, or moved), React uses keys to figure out:
- Which items are new?
- Which items were removed?
- Which items just moved to a different position?

Without keys, React has to guess, and it might make mistakes that cause bugs or slow down your app.

### How to Add Keys

You add a `key` to each item inside `map()`:

```jsx
{fruits.map(fruit => (
  <li key={fruit}>{fruit}</li>
))}
```

The `key` goes on the outermost element that `map()` returns.

---

## Rules for Keys

Not any value works well as a key. Here are the rules:

### Rule 1: Keys Must Be Unique

Each key must be different from all other keys in the same list. No two items should have the same key.

```jsx
// GOOD - each key is unique
{['Apple', 'Banana', 'Cherry'].map(fruit => (
  <li key={fruit}>{fruit}</li>
))}

// BAD - what if you had two 'Apple' entries?
// Two items would have the same key!
```

### Rule 2: Keys Should Be Stable

A "stable" key means it does not change over time. The same item should always have the same key.

```jsx
// GOOD - IDs from your data are stable
{users.map(user => (
  <li key={user.id}>{user.name}</li>
))}

// BAD - Math.random() gives a different key every render!
{users.map(user => (
  <li key={Math.random()}>{user.name}</li>
))}
```

### Rule 3: Avoid Using Index If the List Can Change

The **index** is the position number of an item in the array (0, 1, 2, 3...). You can use it as a key, but it has problems when items are added, removed, or reordered.

```jsx
// OK for lists that NEVER change
{fruits.map((fruit, index) => (
  <li key={index}>{fruit}</li>
))}

// BAD for lists that can change order or have items added/removed
```

Why is index bad for changing lists? Because the index is based on position, not identity:

```
Before removing "Banana":
  index 0 = Apple      key=0
  index 1 = Banana     key=1
  index 2 = Cherry     key=2

After removing "Banana":
  index 0 = Apple      key=0
  index 1 = Cherry     key=1  ← Cherry now has Banana's old key!
```

React sees that `key=1` changed from "Banana" to "Cherry" and thinks the item was edited, not that "Banana" was removed. This can cause confusing bugs.

### What Makes a Good Key?

The best keys come from your data:
- **Database IDs** (like `user.id` or `product.id`) — these are perfect
- **Unique strings** (like usernames or email addresses)
- Any value that is unique and does not change

---

## Common Mistake: Forgetting Keys

If you forget to add keys, React will show a warning in the browser console (the developer tools area):

```
Warning: Each child in a list should have a unique "key" prop.
```

Here is the code that causes this warning:

```jsx
// MISSING KEYS - React will show a warning
function BadList() {
  const items = ['First', 'Second', 'Third'];

  return (
    <ul>
      {items.map(item => (
        <li>{item}</li>  // No key! React warns you.
      ))}
    </ul>
  );
}
```

### How to Fix It

Add a `key` prop to the element inside `map()`:

```jsx
// FIXED - keys added
function GoodList() {
  const items = ['First', 'Second', 'Third'];

  return (
    <ul>
      {items.map(item => (
        <li key={item}>{item}</li>  // Key added!
      ))}
    </ul>
  );
}
```

**Remember:** The `key` does not appear on the screen. It is only used by React internally to keep track of items. Users never see the keys.

---

## Displaying a List of Objects

So far, we have worked with simple lists of strings. But in real apps, your data often comes as a list of **objects** — items that have multiple pieces of information like a name, an age, or a price.

```jsx
function StudentList() {
  const students = [
    { id: 1, name: 'Alice', age: 20 },
    { id: 2, name: 'Bob', age: 22 },
    { id: 3, name: 'Charlie', age: 19 },
  ];

  return (
    <div>
      <h2>Students</h2>
      <ul>
        {students.map(student => (
          <li key={student.id}>
            {student.name} — Age: {student.age}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### Expected Output

```
Students
- Alice — Age: 20
- Bob — Age: 22
- Charlie — Age: 19
```

### Line-by-Line Explanation

**Line 2-6:** We create an array of objects. Each object has three properties: `id`, `name`, and `age`. The `id` is a unique number for each student.

**Line 12:** `{students.map(student => (`
We use `map()` on the `students` array. Each `student` is one object from the array.

**Line 13:** `<li key={student.id}>`
We use `student.id` as the key. This is the ideal key because each student has a unique ID that never changes.

**Line 14:** `{student.name} — Age: {student.age}`
We access the properties of each student object using dot notation: `student.name` gives us the name, `student.age` gives us the age.

---

## Extracting a List Item Into Its Own Component

When each item in your list gets more complex, it is a good idea to create a separate component for it. This keeps your code clean and organized.

```jsx
function StudentCard({ student }) {
  return (
    <div style={{
      border: '1px solid gray',
      padding: '10px',
      margin: '5px',
    }}>
      <h3>{student.name}</h3>
      <p>Age: {student.age}</p>
    </div>
  );
}

function StudentList() {
  const students = [
    { id: 1, name: 'Alice', age: 20 },
    { id: 2, name: 'Bob', age: 22 },
    { id: 3, name: 'Charlie', age: 19 },
  ];

  return (
    <div>
      <h2>Students</h2>
      {students.map(student => (
        <StudentCard key={student.id} student={student} />
      ))}
    </div>
  );
}
```

### Key Placement

Notice that the `key` goes on `<StudentCard>`, not inside the `StudentCard` component. The key always goes on the element that `map()` directly returns.

```
CORRECT:
  {students.map(student => (
    <StudentCard key={student.id} student={student} />
  ))}                 ↑
                      key goes HERE (on the component in map)

WRONG:
  // Inside StudentCard:
  <div key={student.id}>   ← key should NOT be inside the component
```

---

## Mini Project: Simple Shopping List Display

Let us build a shopping list that displays items with their names, quantities, and a "purchased" status.

```jsx
import { useState } from 'react';

function ShoppingItem({ item }) {
  const style = {
    textDecoration: item.purchased ? 'line-through' : 'none',
    color: item.purchased ? 'gray' : 'black',
    padding: '5px 0',
  };

  return (
    <li style={style}>
      {item.name} — Qty: {item.quantity}
      {item.purchased && ' (Purchased)'}
    </li>
  );
}

function ShoppingList() {
  const [items] = useState([
    { id: 1, name: 'Milk', quantity: 2, purchased: false },
    { id: 2, name: 'Eggs', quantity: 12, purchased: true },
    { id: 3, name: 'Bread', quantity: 1, purchased: false },
    { id: 4, name: 'Butter', quantity: 1, purchased: true },
    { id: 5, name: 'Apples', quantity: 6, purchased: false },
  ]);

  const purchasedCount = items.filter(item => item.purchased).length;

  return (
    <div>
      <h2>Shopping List</h2>
      <p>
        {purchasedCount} of {items.length} items purchased
      </p>
      <ul>
        {items.map(item => (
          <ShoppingItem key={item.id} item={item} />
        ))}
      </ul>
    </div>
  );
}

export default ShoppingList;
```

### Expected Output

```
Shopping List
2 of 5 items purchased

- Milk — Qty: 2
- Eggs — Qty: 12 (Purchased)     ← this text has a line through it
- Bread — Qty: 1
- Butter — Qty: 1 (Purchased)    ← this text has a line through it
- Apples — Qty: 6
```

### Line-by-Line Explanation

**ShoppingItem Component (Lines 3-16):**

**Line 3:** `function ShoppingItem({ item }) {`
This component receives one shopping item as a prop.

**Line 4-8:** The `style` object.
- `textDecoration`: if the item is purchased, show a line through the text. Otherwise, show normal text. "Line-through" is the CSS property that draws a line through text.
- `color`: purchased items appear in gray, unpurchased items in black.

**Line 12:** `{item.name} — Qty: {item.quantity}`
Show the item name and quantity.

**Line 13:** `{item.purchased && ' (Purchased)'}`
If the item is purchased, show the text "(Purchased)." If not, show nothing. This uses the `&&` operator you learned in Chapter 11.

**ShoppingList Component (Lines 18-43):**

**Line 19-26:** We create a state variable with an array of shopping items. Each item has an `id`, `name`, `quantity`, and `purchased` status. We write `const [items]` without `setItems` because we are not changing the list in this example. (We will learn how to add and remove items from lists in a later chapter.)

**Line 28:** `const purchasedCount = items.filter(item => item.purchased).length;`
This line counts how many items are purchased. The `filter()` function creates a new list containing only items where `item.purchased` is `true`. Then `.length` gives us how many items are in that new list.

**Line 37-39:** We use `map()` to create a `ShoppingItem` component for each item. Each one gets a `key` (the item's `id`) and the item data as a prop.

---

## Quick Summary

- Use **`map()`** to create a list of elements from an array of data.
- Every item in a list needs a **`key`** prop so React can track it.
- Keys should be **unique** and **stable** (they should not change).
- Use **IDs from your data** as keys when possible.
- Avoid using **array index** as a key if the list can change.
- When list items get complex, **extract them into their own component**.
- The `key` goes on the element that `map()` directly returns, not inside the child component.

---

## Key Points to Remember

1. `map()` takes an array and creates a new array by running a function on each item.
2. Always add `key` to list items — React will warn you if you forget.
3. Good keys: database IDs, unique strings. Bad keys: `Math.random()`, array index (for dynamic lists).
4. Keys are not shown on screen — React uses them internally.
5. The `key` prop goes on the outermost element returned by `map()`.
6. The `filter()` function creates a new array with only the items that pass a test.

---

## Practice Questions

1. In your own words, what does the `map()` function do?

2. What is the purpose of the `key` prop in React lists?

3. Why is using `Math.random()` as a key a bad idea?

4. What warning will React show if you forget to add keys to list items?

5. Given this array, write the `map()` call to create a `<p>` element for each color:
   ```jsx
   const colors = ['Red', 'Green', 'Blue'];
   ```

---

## Practice Exercises

### Exercise 1: Number List

Build a component called `NumberList` that:
- Has an array of numbers: `[10, 20, 30, 40, 50]`
- Shows each number in a list item
- Adds the text "is even" or "is odd" after each number

Expected output:
```
- 10 is even
- 20 is even
- 30 is even
- 40 is even
- 50 is even
```

Hint: You can check if a number is even with `number % 2 === 0`. The `%` symbol gives the remainder when dividing. If the remainder is 0, the number is even.

### Exercise 2: Contact List

Build a component called `ContactList` that:
- Has an array of contact objects, each with `id`, `name`, and `email`
- Shows each contact's name and email in a styled list
- Uses the `id` as the key

### Exercise 3: Movie List with Ratings

Build a component called `MovieList` that:
- Has an array of movie objects with `id`, `title`, and `rating` (a number from 1 to 5)
- Shows each movie title and its rating
- Movies with a rating of 4 or higher should have their text in bold
- Show the total number of movies at the top

Hint: Use the `fontWeight` CSS property: `fontWeight: movie.rating >= 4 ? 'bold' : 'normal'`.

---

## What Is Next?

You now know how to display lists of items, which is one of the most common things you will do in React apps. You have learned about state, events, conditional rendering, and lists — the four core skills for building interactive user interfaces. In the next chapter, you will learn about **forms** in more detail, combining everything you have learned so far into practical, real-world patterns.
