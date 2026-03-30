# Chapter 25: Thinking in React

---

## What You Will Learn

- How to look at a design and break it into React components
- The five steps to building any React application
- How to decide what should be state and what should be props
- How to figure out where state should live
- How data flows in a React app (down through props, up through events)

## Why This Chapter Matters

So far, you have learned how to write components, use props, manage state, and handle events. You know the individual tools. But knowing the tools is not the same as knowing how to build something with them.

Imagine someone gives you a hammer, nails, wood, and a saw. You know what each tool does. But if someone shows you a picture of a bookshelf and says "build this," you might not know where to start.

This chapter teaches you the **thinking process**. It gives you a step-by-step plan for turning any design into a working React app. This is one of the most important skills a React developer can have.

---

## Building with Lego: A Helpful Analogy

Think about building something with Lego blocks. You do not just grab random pieces and start clicking them together. You follow a process:

1. **Look at the picture** on the box. What are you building?
2. **Find the main sections.** The house has a roof, walls, a door, and windows.
3. **Build each section** with simple blocks first. No moving parts yet.
4. **Figure out which parts move.** The door opens. The window slides.
5. **Connect everything** so the parts work together.

Building a React app follows a very similar process. Let us walk through it with a real example.

---

## Our Example: A Simple Product List

Imagine your friend has a small online shop. They show you this design and say, "Can you build this in React?"

Here is what the page should look like:

```
+--------------------------------------------------+
|  Fruit Shop                                      |
|                                                  |
|  Search: [_______________]                       |
|                                                  |
|  [x] Only show fruits in stock                   |
|                                                  |
|  Name                          Price             |
|  ----------------------------------------        |
|  Fruits                                          |
|  ----------------------------------------        |
|  Apple                         $1.00             |
|  Banana                        $0.50             |
|  ~~Passion Fruit~~             ~~$2.00~~         |
|  ----------------------------------------        |
|  Vegetables                                      |
|  ----------------------------------------        |
|  Spinach                       $1.50             |
|  ~~Pumpkin~~                   ~~$3.00~~         |
|  Peas                          $0.80             |
+--------------------------------------------------+
```

Items with a line through them (like ~~Passion Fruit~~) are out of stock. The search box filters the list. The checkbox hides items that are out of stock.

Here is the data we will work with:

```jsx
const PRODUCTS = [
  { category: "Fruits", name: "Apple", price: "$1.00", inStock: true },
  { category: "Fruits", name: "Banana", price: "$0.50", inStock: true },
  { category: "Fruits", name: "Passion Fruit", price: "$2.00", inStock: false },
  { category: "Vegetables", name: "Spinach", price: "$1.50", inStock: true },
  { category: "Vegetables", name: "Pumpkin", price: "$3.00", inStock: false },
  { category: "Vegetables", name: "Peas", price: "$0.80", inStock: true },
];
```

Now, let us apply the five steps.

---

## Step 1: Break the UI into a Component Hierarchy

The first step is to look at the design and draw boxes around every piece. Each box becomes a component.

Think of it like looking at the Lego bookshelf and identifying the separate sections.

Let us draw boxes around our product list:

```
+--------------------------------------------------+
| [A] FilterableProductTable                       |
|                                                  |
|  +--------------------------------------------+  |
|  | [B] SearchBar                               |  |
|  |  Search: [_______________]                  |  |
|  |  [x] Only show fruits in stock              |  |
|  +--------------------------------------------+  |
|                                                  |
|  +--------------------------------------------+  |
|  | [C] ProductTable                            |  |
|  |                                             |  |
|  |  Name                        Price          |  |
|  |  ----------------------------------------   |  |
|  |  +----------------------------------------+ |  |
|  |  | [D] ProductCategoryRow                 | |  |
|  |  |  Fruits                                | |  |
|  |  +----------------------------------------+ |  |
|  |  +----------------------------------------+ |  |
|  |  | [E] ProductRow                         | |  |
|  |  |  Apple                    $1.00        | |  |
|  |  +----------------------------------------+ |  |
|  |  +----------------------------------------+ |  |
|  |  | [E] ProductRow                         | |  |
|  |  |  Banana                   $0.50        | |  |
|  |  +----------------------------------------+ |  |
|  +--------------------------------------------+  |
+--------------------------------------------------+
```

Here are our components:

| Letter | Component Name | What It Does |
|--------|---------------|-------------|
| A | FilterableProductTable | The whole thing. Holds everything together. |
| B | SearchBar | The search input and the checkbox. |
| C | ProductTable | The table that shows products. |
| D | ProductCategoryRow | The category heading (like "Fruits"). |
| E | ProductRow | One row showing a single product. |

And here is how they fit together (this is called a **hierarchy**, which means "which component is inside which"):

```
FilterableProductTable
  |-- SearchBar
  |-- ProductTable
        |-- ProductCategoryRow
        |-- ProductRow
```

### How Do You Decide What Should Be a Component?

A good rule is: **each component should do one thing.** If a component does too much, break it into smaller components.

Think about it like organizing your desk. You do not put everything into one giant drawer. You put pens in one cup, papers in one tray, and books on a shelf. Each container has one purpose.

---

## Step 2: Build a Static Version First

Now we build the components, but with **no interactivity** yet. No state. No event handlers. Just show the data on the screen using props.

Why? Because it is easier to build something that looks right first, and then add behavior later. Like drawing a sketch before painting.

Let us build each component from the bottom up.

### ProductRow Component

This shows one product:

```jsx
function ProductRow({ product }) {
  const name = product.inStock ? (
    product.name
  ) : (
    <span style={{ color: "red" }}>{product.name}</span>
  );

  return (
    <tr>
      <td>{name}</td>
      <td>{product.price}</td>
    </tr>
  );
}
```

**Line-by-line explanation:**

- **Line 1:** We create a component that receives a `product` object as a prop.
- **Lines 2-6:** If the product is in stock, we show the name normally. If it is not in stock, we show the name in red.
- **Lines 8-12:** We return a table row with two cells: the name and the price.

### ProductCategoryRow Component

This shows a category heading:

```jsx
function ProductCategoryRow({ category }) {
  return (
    <tr>
      <th colSpan="2">{category}</th>
    </tr>
  );
}
```

**Line-by-line explanation:**

- **Line 1:** This component receives a `category` string as a prop.
- **Line 4:** It shows the category name in a header cell that spans both columns. The word `colSpan` means "stretch across this many columns."

### ProductTable Component

This shows the full table:

```jsx
function ProductTable({ products }) {
  const rows = [];
  let lastCategory = null;

  products.forEach((product) => {
    if (product.category !== lastCategory) {
      rows.push(
        <ProductCategoryRow
          category={product.category}
          key={product.category}
        />
      );
    }
    rows.push(<ProductRow product={product} key={product.name} />);
    lastCategory = product.category;
  });

  return (
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Price</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
  );
}
```

**Line-by-line explanation:**

- **Line 1:** This component receives the full list of products.
- **Line 2:** We create an empty array to hold the rows we will build.
- **Line 3:** We track the last category we saw. This helps us know when to add a new category heading.
- **Lines 5-16:** We loop through each product. If the category changed, we add a category heading row. Then we add the product row.
- **Lines 18-28:** We return a table with a header row (Name, Price) and the body rows we built.

### SearchBar Component

For the static version, this just shows the form without any behavior:

```jsx
function SearchBar() {
  return (
    <form>
      <input type="text" placeholder="Search..." />
      <label>
        <input type="checkbox" />
        {" "}Only show products in stock
      </label>
    </form>
  );
}
```

### FilterableProductTable Component

This is the top-level component that puts everything together:

```jsx
function FilterableProductTable({ products }) {
  return (
    <div>
      <h1>Fruit Shop</h1>
      <SearchBar />
      <ProductTable products={products} />
    </div>
  );
}
```

### Running the Static Version

```jsx
function App() {
  return <FilterableProductTable products={PRODUCTS} />;
}
```

**Expected output:** You will see the full product table on screen with the search box and checkbox. But nothing happens when you type or click. That is fine. We will add that next.

At this point, data flows in **one direction only**: from the top (FilterableProductTable) down to the children through props. This is called **one-way data flow**.

```
FilterableProductTable (has the data)
    |
    |--- passes products ---> ProductTable
    |                             |
    |                             |--- passes product ---> ProductRow
    |                             |--- passes category --> ProductCategoryRow
    |
    |--- (nothing yet) --------> SearchBar
```

---

## Step 3: Figure Out the Minimal State

Now we need to add interactivity. To do that, we need **state** (data that changes over time).

But we do not want too much state. More state means more things to keep track of, and more chances for bugs. We want the **minimum** amount of state.

Think of it like packing for a trip. You do not pack everything you own. You pack only what you need. If you can wear the same shoes with three outfits, you bring one pair of shoes, not three.

Let us look at all the data in our app:

1. The original list of products
2. The search text the user typed
3. The value of the checkbox (checked or not)
4. The filtered list of products

Now, let us ask three questions about each piece of data:

| Question | If yes, it is NOT state |
|----------|----------------------|
| Does it stay the same over time? (Never changes?) | Not state. Just a constant. |
| Is it passed from a parent through props? | Not state. It is a prop. |
| Can you calculate it from other state or props? | Not state. Compute it instead. |

Let us check our data:

| Data | Changes? | Passed as prop? | Can compute? | Is it state? |
|------|----------|----------------|-------------|-------------|
| Product list | No | Yes (from outside) | No | No |
| Search text | Yes | No | No | **Yes** |
| Checkbox value | Yes | No | No | **Yes** |
| Filtered list | Yes | No | Yes (from the other three) | No |

We only need **two pieces of state**:

1. The search text
2. Whether the checkbox is checked

The filtered list is NOT state. We can compute it from the product list, the search text, and the checkbox value. Do not store something in state if you can calculate it.

---

## Step 4: Decide Where State Should Live

Now we know we need two pieces of state: `searchText` and `inStockOnly`. But which component should hold them?

Here is how you decide. For each piece of state:

1. Find every component that **uses** that state to render something.
2. Find their **closest common parent** (the nearest component that is above all of them in the hierarchy).
3. That common parent (or something above it) should hold the state.

Let us figure this out:

- **SearchBar** needs `searchText` and `inStockOnly` (to show them in the form).
- **ProductTable** needs `searchText` and `inStockOnly` (to filter the list).
- Their common parent is **FilterableProductTable**.

So `FilterableProductTable` should hold both pieces of state.

```
FilterableProductTable  <-- state lives here
    |                       (searchText, inStockOnly)
    |
    |--- SearchBar          <-- uses state to show values
    |
    |--- ProductTable       <-- uses state to filter products
```

---

## Step 5: Add Data Flow

This is the last step. We need to:

1. **Pass state down** as props (parent to children).
2. **Pass events up** so children can change the state (children to parent).

Think of it like a restaurant:

- The **menu** goes from the kitchen down to the customers (data flows down).
- The **order** goes from the customers up to the kitchen (events flow up).

### Adding State to FilterableProductTable

```jsx
import { useState } from "react";

function FilterableProductTable({ products }) {
  const [searchText, setSearchText] = useState("");
  const [inStockOnly, setInStockOnly] = useState(false);

  return (
    <div>
      <h1>Fruit Shop</h1>
      <SearchBar
        searchText={searchText}
        inStockOnly={inStockOnly}
        onSearchTextChange={setSearchText}
        onInStockOnlyChange={setInStockOnly}
      />
      <ProductTable
        products={products}
        searchText={searchText}
        inStockOnly={inStockOnly}
      />
    </div>
  );
}
```

**Line-by-line explanation:**

- **Line 1:** We import `useState` so we can create state.
- **Line 4:** We create state for the search text. It starts as an empty string.
- **Line 5:** We create state for the checkbox. It starts as `false` (unchecked).
- **Lines 11-15:** We pass the state values AND the setter functions to SearchBar. The setter functions let SearchBar change the state.
- **Lines 17-20:** We pass the products, search text, and checkbox value to ProductTable so it can filter the list.

### Updating SearchBar to Use Props and Events

```jsx
function SearchBar({
  searchText,
  inStockOnly,
  onSearchTextChange,
  onInStockOnlyChange,
}) {
  return (
    <form>
      <input
        type="text"
        placeholder="Search..."
        value={searchText}
        onChange={(e) => onSearchTextChange(e.target.value)}
      />
      <label>
        <input
          type="checkbox"
          checked={inStockOnly}
          onChange={(e) => onInStockOnlyChange(e.target.checked)}
        />
        {" "}Only show products in stock
      </label>
    </form>
  );
}
```

**Line-by-line explanation:**

- **Lines 1-6:** SearchBar now receives the state values and the functions to update them.
- **Line 12:** The input shows the current search text.
- **Line 13:** When the user types, we call `onSearchTextChange` with the new text. This goes UP to the parent and changes the state.
- **Line 18:** The checkbox shows whether it is checked.
- **Line 19:** When the user clicks the checkbox, we call `onInStockOnlyChange`. This goes UP to the parent.

### Updating ProductTable to Filter

```jsx
function ProductTable({ products, searchText, inStockOnly }) {
  const rows = [];
  let lastCategory = null;

  products.forEach((product) => {
    if (product.name.toLowerCase().indexOf(
      searchText.toLowerCase()) === -1) {
      return;
    }
    if (inStockOnly && !product.inStock) {
      return;
    }

    if (product.category !== lastCategory) {
      rows.push(
        <ProductCategoryRow
          category={product.category}
          key={product.category}
        />
      );
    }
    rows.push(<ProductRow product={product} key={product.name} />);
    lastCategory = product.category;
  });

  return (
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Price</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
  );
}
```

**Line-by-line explanation:**

- **Line 1:** Now we also receive `searchText` and `inStockOnly` as props.
- **Lines 6-8:** If the product name does not contain the search text, we skip it. The `toLowerCase()` makes the search case-insensitive (so "apple" matches "Apple").
- **Lines 10-12:** If the checkbox is checked and the product is out of stock, we skip it.

### The Complete Data Flow

Here is how data flows in our finished app:

```
FilterableProductTable
  |  (holds searchText and inStockOnly state)
  |
  |--- state values flow DOWN as props ----+
  |                                        |
  |--- SearchBar                           |
  |     |  Shows the current values        |
  |     |  When user types or clicks:      |
  |     |  Events flow UP via callbacks    |
  |     +--- calls onSearchTextChange() -->+-- updates state
  |     +--- calls onInStockOnlyChange() ->+-- updates state
  |                                        |
  |--- ProductTable                        |
        |  Receives products + filters     |
        |  Filters the list                |
        |  Shows matching products         |
```

**Expected output:** Now when you type in the search box, the product list filters in real time. When you check the checkbox, out-of-stock items disappear. Everything works together.

---

## The Five Steps Summarized

Here is a quick reference you can use for any React project:

```
+---------------------------------------------------+
|  Step 1: Break UI into components                 |
|          Draw boxes around every piece             |
|                                                    |
|  Step 2: Build a static version                   |
|          Props only. No state. Just display data.  |
|                                                    |
|  Step 3: Find the minimal state                   |
|          What changes? What can be computed?        |
|                                                    |
|  Step 4: Decide where state lives                 |
|          Find the common parent of all users.      |
|                                                    |
|  Step 5: Add data flow                            |
|          State down via props. Events up via       |
|          callback functions.                       |
+---------------------------------------------------+
```

---

## Quick Summary

- Building a React app starts with a plan, just like building with Lego.
- **Step 1:** Look at the design and break it into components. Each component should do one thing.
- **Step 2:** Build a static version with no state. Just pass data down through props.
- **Step 3:** Figure out the smallest amount of state you need. If you can compute it, do not store it.
- **Step 4:** Decide which component should hold each piece of state. Find the common parent of all components that need it.
- **Step 5:** Add interactivity. Pass state down as props. Let children send events up through callback functions.

## Key Points to Remember

1. Always start by breaking the design into components before writing code.
2. Build a static version first. Get it looking right before adding behavior.
3. Keep state minimal. Do not store what you can calculate.
4. State should live in the closest common parent of the components that need it.
5. Data flows down (through props). Events flow up (through callback functions).

## Practice Questions

1. What are the five steps to building a React app?
2. How do you decide if a piece of data should be state or not?
3. If two sibling components both need the same state, where should that state live?
4. What does "one-way data flow" mean?
5. Why should you build a static version before adding state?

## Exercises

1. Look at any website you use daily (like a to-do app, a weather app, or a shopping site). Draw boxes around the parts you see. Write down what components you would create. Think about which one is inside which.

2. Using the five-step process, plan out a simple "Contact List" app. It should show a list of names and phone numbers, and have a search box to filter them. Write down: (a) what components you need, (b) what data is state, and (c) where the state should live.

3. Take the product list example from this chapter and add a new feature: a dropdown that lets the user sort products by name or by price. Think through where the sort state should live and how the data flows before writing any code.

---

## What Is Coming Next?

Now that you know how to think about building a React app, we need to learn some important rules. In the next chapter, we will learn about **keeping components pure**. You will discover why React components should behave like math formulas: the same input should always give the same output. This will help you avoid confusing bugs and write more reliable code.
