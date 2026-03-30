# Chapter 18: Lifting State Up

## What You Will Learn

In this chapter, you will learn:

- Why two components sometimes need to share the same data
- What "lifting state up" means
- How to move state to a parent component so children can share it
- How to pass state down as props and functions as props
- The parent-holds-state pattern
- How data flows in React (down through props, up through functions)
- When to lift state up vs. when to keep state local
- How to build a simple shopping cart where two components share state

## Why This Chapter Matters

Imagine you have two thermometers in your house. One is in the kitchen, and one is in the living room. Now imagine they are both connected to the same heating system. When you turn up the heat, both thermometers should show the same temperature.

But what if each thermometer tracked its own temperature separately? The kitchen might say 72 degrees while the living room says 68. They would be out of sync. That is confusing and wrong.

In React, the same problem happens. Sometimes two components need to show the same data. If each component keeps its own copy of that data, they can get out of sync. The solution is to move the data to a place where both components can access it: their shared parent.

This idea is called **lifting state up**. It is one of the most important patterns in React. Once you understand it, you will know how to share data between any two components in your app.

---

## The Problem: Two Components Need the Same Data

Let us look at a simple example. Imagine you have two text inputs. One shows a temperature in Celsius, and the other shows the same temperature in Fahrenheit. When you type in the Celsius input, the Fahrenheit input should update automatically, and vice versa.

### The Wrong Approach: Each Component Has Its Own State

```jsx
function CelsiusInput() {
  const [celsius, setCelsius] = React.useState('');

  return (
    <div>
      <label>Celsius: </label>
      <input
        value={celsius}
        onChange={function (event) {
          setCelsius(event.target.value);
        }}
      />
    </div>
  );
}

function FahrenheitInput() {
  const [fahrenheit, setFahrenheit] = React.useState('');

  return (
    <div>
      <label>Fahrenheit: </label>
      <input
        value={fahrenheit}
        onChange={function (event) {
          setFahrenheit(event.target.value);
        }}
      />
    </div>
  );
}
```

The problem here is clear: `CelsiusInput` and `FahrenheitInput` each have their own state. They do not know about each other. Typing in one input does not affect the other. They are completely disconnected.

This is like those two thermometers tracking temperature separately. They will never agree.

---

## What "Lifting State Up" Means

**Lifting state up** means moving the state from a child component to the nearest parent component that both children share.

Think of it this way. You have two children who each have their own piggy bank. They keep arguing about how much money the family has. The solution? Give the money to the parent. Now the parent holds the money and tells each child how much there is. If one child earns money, they give it to the parent, and the parent updates everyone.

In React terms:

1. **Remove state from the child components.**
2. **Add state to the parent component.**
3. **Pass the state down to children as props.**
4. **Pass functions down so children can request changes.**

The parent becomes the "single source of truth." There is only one copy of the data, and everyone gets it from the same place.

---

## Step-by-Step Example: Temperature Converter

Let us fix our temperature converter by lifting state up.

### Step 1: Create the Parent Component with State

```jsx
function TemperatureConverter() {
  const [temperature, setTemperature] = React.useState('');
  const [scale, setScale] = React.useState('celsius');

  function handleCelsiusChange(value) {
    setTemperature(value);
    setScale('celsius');
  }

  function handleFahrenheitChange(value) {
    setTemperature(value);
    setScale('fahrenheit');
  }

  let celsius;
  let fahrenheit;

  if (scale === 'celsius') {
    celsius = temperature;
    fahrenheit = temperature ? String(Number(temperature) * 9 / 5 + 32) : '';
  } else {
    fahrenheit = temperature;
    celsius = temperature ? String((Number(temperature) - 32) * 5 / 9) : '';
  }

  return (
    <div>
      <h1>Temperature Converter</h1>
      <TemperatureInput
        label="Celsius"
        value={celsius}
        onChange={handleCelsiusChange}
      />
      <TemperatureInput
        label="Fahrenheit"
        value={fahrenheit}
        onChange={handleFahrenheitChange}
      />
    </div>
  );
}
```

Let us go through this line by line:

- **`const [temperature, setTemperature] = React.useState('');`** — The parent holds the temperature value. This is the state that was "lifted up" from the children.
- **`const [scale, setScale] = React.useState('celsius');`** — The parent also tracks which input the user typed in last. `scale` remembers whether the user typed in Celsius or Fahrenheit.
- **`handleCelsiusChange(value)`** — When the user types in the Celsius input, this function saves the value and marks the scale as Celsius.
- **`handleFahrenheitChange(value)`** — When the user types in the Fahrenheit input, this function saves the value and marks the scale as Fahrenheit.
- **The conversion math** — If the user typed Celsius, we calculate Fahrenheit. If the user typed Fahrenheit, we calculate Celsius. The formula `C * 9/5 + 32` converts Celsius to Fahrenheit. The formula `(F - 32) * 5/9` converts Fahrenheit to Celsius.
- **`temperature ? String(...) : ''`** — If the temperature is empty, show an empty string. Otherwise, do the conversion. The `?` and `:` form a **ternary operator**, which is like a short if-else statement.

### Step 2: Create the Reusable Child Component

```jsx
function TemperatureInput({ label, value, onChange }) {
  return (
    <div style={{ margin: '10px 0' }}>
      <label>{label}: </label>
      <input
        value={value}
        onChange={function (event) {
          onChange(event.target.value);
        }}
      />
    </div>
  );
}
```

Line by line:

- **`function TemperatureInput({ label, value, onChange })`** — This component does NOT have its own state. It receives everything from its parent through props.
- **`value={value}`** — The input shows whatever value the parent passed down.
- **`onChange(event.target.value)`** — When the user types, the component calls the `onChange` function from the parent. It does not update any state itself. Instead, it tells the parent: "Hey, the user typed something new!"

### Expected Output

You will see two inputs on the screen: one labeled "Celsius" and one labeled "Fahrenheit." When you type `100` in the Celsius input, the Fahrenheit input automatically shows `212`. When you type `32` in the Fahrenheit input, the Celsius input automatically shows `0`.

Both inputs always stay in sync because they share the same state in the parent.

---

## Passing State Down and Functions Up

This pattern is so important that it deserves its own section. Here is the pattern in plain English:

1. **The parent holds the state.** It is the single source of truth.
2. **The parent passes state down as props.** Children receive the data they need to display.
3. **The parent passes functions down as props.** Children receive functions they can call to request changes.
4. **Children call the parent's functions when something happens.** For example, when the user types in an input.
5. **The parent updates the state.** This causes a re-render, and all children receive the updated data.

### The Data Flow Diagram

Here is how data flows in our temperature converter:

```
        TemperatureConverter (Parent)
        ┌─────────────────────────────────┐
        │  State: temperature, scale      │
        │                                 │
        │  Calculates celsius & fahrenheit│
        └───────┬───────────────┬─────────┘
                │               │
        Props   │               │  Props
        (value, │               │  (value,
        onChange)│               │  onChange)
                │               │
                ▼               ▼
        ┌───────────┐   ┌───────────────┐
        │ Celsius   │   │ Fahrenheit    │
        │ Input     │   │ Input         │
        └─────┬─────┘   └──────┬────────┘
              │                │
              │  User types    │  User types
              │  → calls       │  → calls
              │  onChange()     │  onChange()
              │                │
              └───────┬────────┘
                      │
                      ▼
              Parent updates state
              Both children re-render
```

Data flows **down** through props (parent to children). Events flow **up** through functions (children to parent). This is called **one-way data flow**, and it is a key concept in React.

---

## A Simpler Example: Shared Counter

The temperature converter has some math that might distract from the pattern. Let us see the same pattern with a simpler example: two buttons that share a counter.

```jsx
function CounterDisplay({ count }) {
  return <h2>Count: {count}</h2>;
}

function CounterButtons({ onIncrement, onDecrement }) {
  return (
    <div>
      <button onClick={onDecrement}>- Subtract</button>
      <button onClick={onIncrement}>+ Add</button>
    </div>
  );
}

function Counter() {
  const [count, setCount] = React.useState(0);

  function handleIncrement() {
    setCount(count + 1);
  }

  function handleDecrement() {
    setCount(count - 1);
  }

  return (
    <div>
      <CounterDisplay count={count} />
      <CounterButtons
        onIncrement={handleIncrement}
        onDecrement={handleDecrement}
      />
    </div>
  );
}
```

Line by line:

- **`CounterDisplay`** only receives `count` as a prop and displays it. It has no state.
- **`CounterButtons`** only receives two functions as props. It has no state. It just calls the functions when buttons are clicked.
- **`Counter`** (the parent) holds the state (`count`). It passes the count down to `CounterDisplay` and the functions down to `CounterButtons`.
- When a button is clicked, the function runs in the parent, updates the state, and both children re-render with the new data.

### Expected Output

You see the text "Count: 0" and two buttons: "- Subtract" and "+ Add." Clicking "+ Add" changes the display to "Count: 1." Clicking "- Subtract" changes it to "Count: -1." The display and buttons are separate components, but they stay in sync because they share state through the parent.

---

## When to Lift State Up vs. Keep State Local

Not all state needs to be lifted up. Here is a simple guide:

### Keep State Local When:

- **Only one component uses it.** If a search input only needs to track what the user is typing, and no other component cares about that text, keep the state in the search input component.
- **It is temporary.** For example, whether a dropdown menu is open or closed. Other components do not need to know this.
- **It is about the UI, not the data.** For example, whether a tooltip is visible.

### Lift State Up When:

- **Two or more components need the same data.** Like our temperature inputs.
- **A child needs to change something that affects its sibling.** For example, clicking a button in one component should update a display in another component.
- **The parent needs to know about the child's state.** For example, a form parent needs to know all the input values to submit them.

### A Quick Test

Ask yourself: "Does any other component need this piece of data?" If the answer is yes, lift the state up to the nearest shared parent. If the answer is no, keep it local.

---

## Mini Project: Simple Shopping Cart

Let us build a shopping cart where an item list and a cart summary share the same state. This is a real-world example of lifting state up.

### The Plan

We need three components:

1. **`ProductList`** — Shows the products and "Add to Cart" buttons.
2. **`CartSummary`** — Shows what is in the cart and the total price.
3. **`ShoppingApp`** — The parent that holds the cart state.

### Step 1: The Product Data

```jsx
const products = [
  { id: 1, name: 'Apple', price: 1.50 },
  { id: 2, name: 'Bread', price: 3.00 },
  { id: 3, name: 'Milk', price: 2.50 },
  { id: 4, name: 'Cheese', price: 5.00 }
];
```

### Step 2: The ProductList Component

```jsx
function ProductList({ products, onAddToCart }) {
  const listStyle = {
    listStyle: 'none',
    padding: 0
  };

  const itemStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '10px',
    borderBottom: '1px solid #eee'
  };

  const buttonStyle = {
    backgroundColor: '#28a745',
    color: 'white',
    border: 'none',
    padding: '5px 15px',
    borderRadius: '4px',
    cursor: 'pointer'
  };

  return (
    <div>
      <h2>Products</h2>
      <ul style={listStyle}>
        {products.map(function (product) {
          return (
            <li key={product.id} style={itemStyle}>
              <span>{product.name} - ${product.price.toFixed(2)}</span>
              <button
                style={buttonStyle}
                onClick={function () {
                  onAddToCart(product);
                }}
              >
                Add to Cart
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
```

Line by line:

- **`function ProductList({ products, onAddToCart })`** — This component receives the product list and a function to add items to the cart. It does NOT hold any state.
- **`products.map(function (product) { ... })`** — This loops through each product and creates a list item for it.
- **`product.price.toFixed(2)`** — This formats the price to always show two decimal places. So `1.5` becomes `1.50`.
- **`onClick={function () { onAddToCart(product); }}`** — When the "Add to Cart" button is clicked, it calls the parent's function and passes the entire product object.

### Step 3: The CartSummary Component

```jsx
function CartSummary({ cartItems, onRemoveFromCart }) {
  const total = cartItems.reduce(function (sum, item) {
    return sum + item.price * item.quantity;
  }, 0);

  if (cartItems.length === 0) {
    return (
      <div>
        <h2>Cart</h2>
        <p>Your cart is empty.</p>
      </div>
    );
  }

  return (
    <div>
      <h2>Cart</h2>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {cartItems.map(function (item) {
          return (
            <li key={item.id} style={{ padding: '5px 0' }}>
              {item.name} x {item.quantity} = ${(item.price * item.quantity).toFixed(2)}
              <button
                onClick={function () {
                  onRemoveFromCart(item.id);
                }}
                style={{ marginLeft: '10px', color: 'red', cursor: 'pointer' }}
              >
                Remove
              </button>
            </li>
          );
        })}
      </ul>
      <hr />
      <p><strong>Total: ${total.toFixed(2)}</strong></p>
    </div>
  );
}
```

Line by line:

- **`function CartSummary({ cartItems, onRemoveFromCart })`** — This component receives the cart items and a function to remove items. Again, no state of its own.
- **`cartItems.reduce(...)`** — `reduce` is a way to calculate a single value from an array. Here, it adds up the price times quantity of every item to get the total. The `0` at the end is the starting value for the sum.
- **`if (cartItems.length === 0)`** — If the cart is empty, show a simple message instead of the item list.
- **`item.name} x {item.quantity}`** — Shows how many of each item are in the cart.
- **The "Remove" button** — Calls the parent's `onRemoveFromCart` function with the item's ID.

### Step 4: The Parent Component (ShoppingApp)

```jsx
function ShoppingApp() {
  const [cartItems, setCartItems] = React.useState([]);

  function handleAddToCart(product) {
    setCartItems(function (currentItems) {
      const existingItem = currentItems.find(function (item) {
        return item.id === product.id;
      });

      if (existingItem) {
        return currentItems.map(function (item) {
          if (item.id === product.id) {
            return { ...item, quantity: item.quantity + 1 };
          }
          return item;
        });
      }

      return [...currentItems, { ...product, quantity: 1 }];
    });
  }

  function handleRemoveFromCart(productId) {
    setCartItems(function (currentItems) {
      return currentItems.filter(function (item) {
        return item.id !== productId;
      });
    });
  }

  const appStyle = {
    display: 'flex',
    gap: '40px',
    padding: '20px',
    maxWidth: '800px',
    margin: '0 auto'
  };

  return (
    <div>
      <h1 style={{ textAlign: 'center' }}>Simple Shop</h1>
      <div style={appStyle}>
        <div style={{ flex: 1 }}>
          <ProductList products={products} onAddToCart={handleAddToCart} />
        </div>
        <div style={{ flex: 1 }}>
          <CartSummary
            cartItems={cartItems}
            onRemoveFromCart={handleRemoveFromCart}
          />
        </div>
      </div>
    </div>
  );
}
```

Line by line:

- **`const [cartItems, setCartItems] = React.useState([]);`** — The parent holds the cart state. It starts as an empty array.
- **`handleAddToCart(product)`** — This function checks if the product is already in the cart. If yes, it increases the quantity. If no, it adds the product with quantity 1.
- **`currentItems.find(...)`** — `find` looks through the array and returns the first item that matches the condition. Here, it checks if an item with the same ID already exists.
- **`{ ...item, quantity: item.quantity + 1 }`** — This creates a copy of the item with the quantity increased by 1. The `...item` part copies all existing properties. This is called the **spread operator**.
- **`[...currentItems, { ...product, quantity: 1 }]`** — This creates a new array with all current items plus the new product (with quantity set to 1).
- **`handleRemoveFromCart(productId)`** — This function creates a new array that includes everything except the item with the matching ID. `filter` keeps only items where the condition is true.
- The parent passes `cartItems` and functions to both `ProductList` and `CartSummary`.

### Expected Output

You will see a page with two columns. The left column shows a list of products (Apple, Bread, Milk, Cheese) with prices and "Add to Cart" buttons. The right column shows the cart, which starts as "Your cart is empty."

When you click "Add to Cart" on Apple, the cart shows "Apple x 1 = $1.50" and "Total: $1.50." Click it again, and it shows "Apple x 2 = $3.00." Click "Add to Cart" on Bread, and the cart shows both items. Click "Remove" next to an item to remove it from the cart.

The product list and the cart summary are completely separate components, but they always show consistent data because they share state through the parent.

---

## Quick Summary

- **Lifting state up** means moving state from child components to their shared parent.
- The parent becomes the **single source of truth** for the shared data.
- **Props** carry data from parent to children (downward flow).
- **Functions passed as props** let children communicate changes back to the parent (upward flow).
- This is called **one-way data flow**: data goes down, events go up.
- Keep state local when only one component needs it. Lift state up when multiple components need the same data.

---

## Key Points to Remember

1. If two components need the same data, neither one should own it. Their closest shared parent should own it.
2. Children never modify props directly. They call functions provided by the parent to request changes.
3. One-way data flow makes your app predictable. You always know where data comes from (the parent) and how it changes (through specific functions).
4. Lifting state up does not mean putting ALL state in the top-level component. Only lift state when it needs to be shared.
5. The pattern is always the same: parent holds state, passes it down as props, and passes updater functions down as props.
6. When state is lifted up, the child components become simpler because they do not manage their own state.

---

## Practice Questions

1. What problem does lifting state up solve?
2. In the temperature converter example, why does the parent hold the temperature state instead of each input holding its own?
3. What is one-way data flow? Describe how data moves in a React app.
4. Give an example of when you should keep state local instead of lifting it up.
5. In the shopping cart example, what would go wrong if both `ProductList` and `CartSummary` each had their own copy of the cart state?

---

## Exercises

### Exercise 1: Synced Text Inputs

Create two text inputs. Whatever you type in one input should appear in the other, and vice versa. They should always show the same text. (Hint: Lift the text state up to a parent component.)

### Exercise 2: Color Picker

Create a component with three buttons: "Red," "Green," and "Blue." Create another component that displays a colored box. When you click a color button, the box should change to that color. The two components should share the selected color through a parent.

### Exercise 3: Vote Counter

Create a simple voting app. There should be a list of options (like "Pizza," "Tacos," "Sushi") with a "Vote" button next to each. Below the list, show a summary of the vote counts. The vote list and the summary should be separate components that share the vote data through a parent.

---

## What Is Next?

You now know how to share data between components by lifting state up to their parent. This works great for small apps and for components that are close together in the component tree.

But what about navigation? What if you want your app to have multiple "pages" — like a Home page, an About page, and a Contact page — without actually reloading the browser?

In the next chapter, you will learn about **routing** in React. Routing lets you show different components based on the URL, just like a real multi-page website, but faster and smoother.
