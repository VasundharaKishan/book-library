# Chapter 17: Component Reuse

## What You Will Learn

In this chapter, you will learn:

- Why reusing components saves you time and effort
- How to build a reusable Button component with props
- How to build a reusable Card component
- What composition means and how to put components inside other components
- How to use the special `children` prop for flexible content
- When to turn something into its own component
- How to organize reusable components in a folder
- How to build a product card grid using one reusable component

## Why This Chapter Matters

Imagine you are baking cookies. You have a cookie cutter shaped like a star. You press it into the dough once, and you get a star cookie. You press it again, and you get another star cookie. You did not have to carve each star by hand. The cookie cutter lets you make the same shape over and over, quickly and perfectly.

Components in React work the same way. You write a component once, and then you use it as many times as you want. Each time, you can change small details (like the text or color), but the basic shape stays the same.

This idea is called **reuse**. Reuse means using something again instead of building it from scratch. It is one of the most powerful ideas in programming. It saves time. It reduces mistakes. It makes your code easier to fix, because you only need to fix one place instead of many.

This chapter teaches you how to think in reusable pieces. Once you learn this skill, you will build apps much faster.

---

## Why Reuse Matters

Let us say you are building a website. The website has three buttons:

- A "Save" button
- A "Delete" button
- A "Cancel" button

Without reuse, you might write the code for each button separately. That means writing similar code three times. If you later want to change how buttons look, you have to change all three places. That is slow and easy to mess up.

With reuse, you write one Button component. Then you use it three times with different labels. If you want to change how buttons look, you change one file. All three buttons update automatically.

Think of it like a stamp. You create the stamp once. Then you press it onto paper as many times as you like. The stamp stays the same, but you can use different colored ink each time.

### The Benefits of Reuse

1. **Less code to write.** You write the component once.
2. **Fewer bugs.** One component means one place to fix.
3. **Consistent look.** All buttons (or cards, or forms) look the same.
4. **Faster development.** You build new pages by combining existing pieces.

---

## Making a Reusable Button Component

Let us build a simple, reusable Button component. This button will accept props so we can customize it each time we use it.

### Step 1: Create the Button Component

```jsx
function Button({ label, onClick, color }) {
  const style = {
    backgroundColor: color,
    color: 'white',
    padding: '10px 20px',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    fontSize: '16px'
  };

  return (
    <button style={style} onClick={onClick}>
      {label}
    </button>
  );
}
```

Let us go through this line by line:

- **`function Button({ label, onClick, color })`** — This creates a component called Button. It receives three props: `label` (the text on the button), `onClick` (what happens when you click it), and `color` (the background color).
- **`const style = { ... }`** — This creates a style object. It sets the background color, text color, padding (space inside the button), and other visual properties.
- **`backgroundColor: color`** — This uses the `color` prop to set the background. Each button can have a different color.
- **`<button style={style} onClick={onClick}>`** — This renders an HTML button with our custom style and click behavior.
- **`{label}`** — This shows the text that was passed in as a prop.

### Step 2: Use the Button Component

```jsx
function App() {
  function handleSave() {
    alert('Saved!');
  }

  function handleDelete() {
    alert('Deleted!');
  }

  function handleCancel() {
    alert('Cancelled!');
  }

  return (
    <div>
      <h1>My App</h1>
      <Button label="Save" onClick={handleSave} color="green" />
      <Button label="Delete" onClick={handleDelete} color="red" />
      <Button label="Cancel" onClick={handleCancel} color="gray" />
    </div>
  );
}
```

Let us go through the important parts:

- **`<Button label="Save" onClick={handleSave} color="green" />`** — This uses our Button component. We pass "Save" as the label, the `handleSave` function as the click handler, and "green" as the color.
- We use the same Button component three times, but each one looks and behaves differently because we pass different props.

### Expected Output

You will see three buttons on the screen:

- A green button that says "Save"
- A red button that says "Delete"
- A gray button that says "Cancel"

When you click each button, a different alert message appears.

### Adding Default Props

What if someone forgets to pass a color? We can set a default value:

```jsx
function Button({ label, onClick, color = 'blue' }) {
  // ... same code as before
}
```

Now if you write `<Button label="Click Me" onClick={handleClick} />` without a color, the button will be blue by default. The `= 'blue'` part sets the default. This is called a **default parameter** — a value that is used when nothing else is provided.

---

## Making a Reusable Card Component

A **card** is a common design pattern. It is a box that holds some content, like a title, an image, and a description. You see cards everywhere on the web: product listings, blog posts, user profiles.

Let us build a reusable Card component:

```jsx
function Card({ title, description, imageUrl }) {
  const style = {
    border: '1px solid #ddd',
    borderRadius: '8px',
    padding: '16px',
    maxWidth: '300px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
  };

  const imageStyle = {
    width: '100%',
    borderRadius: '4px'
  };

  return (
    <div style={style}>
      {imageUrl && <img src={imageUrl} alt={title} style={imageStyle} />}
      <h2>{title}</h2>
      <p>{description}</p>
    </div>
  );
}
```

Line by line:

- **`function Card({ title, description, imageUrl })`** — Our Card accepts three props: a title, a description, and an optional image URL.
- **`const style = { ... }`** — This creates a box with a light border, rounded corners, padding, a maximum width, and a subtle shadow.
- **`{imageUrl && <img ... />}`** — This is a neat trick. It says: "If `imageUrl` exists, show the image. If it does not exist, show nothing." The `&&` operator works like "and" — both sides must be true. If `imageUrl` is empty, React skips the image.
- **`<h2>{title}</h2>`** — This shows the title in a heading.
- **`<p>{description}</p>`** — This shows the description in a paragraph.

### Using the Card Component

```jsx
function App() {
  return (
    <div>
      <Card
        title="Beautiful Sunset"
        description="A photo of the sunset over the ocean."
        imageUrl="https://example.com/sunset.jpg"
      />
      <Card
        title="Mountain View"
        description="Snow-covered peaks in the morning light."
        imageUrl="https://example.com/mountain.jpg"
      />
      <Card
        title="Simple Note"
        description="This card has no image, and that is okay!"
      />
    </div>
  );
}
```

### Expected Output

You will see three cards stacked on the page:

- The first card shows a sunset image, the title "Beautiful Sunset", and its description.
- The second card shows a mountain image, the title "Mountain View", and its description.
- The third card has no image (because we did not pass `imageUrl`), just the title "Simple Note" and its description.

---

## Composition: Putting Components Inside Other Components

**Composition** is a big word that means a simple thing: building something by combining smaller parts. Think of building with LEGO bricks. Each brick is simple on its own, but when you put them together, you can build houses, cars, or castles.

In React, composition means putting components inside other components. You have already been doing this! Every time you put a `<Button />` inside an `<App />`, you were using composition.

Let us see a clear example:

```jsx
function Header() {
  return (
    <header>
      <h1>My Website</h1>
      <nav>
        <Button label="Home" onClick={() => {}} color="blue" />
        <Button label="About" onClick={() => {}} color="blue" />
        <Button label="Contact" onClick={() => {}} color="blue" />
      </nav>
    </header>
  );
}

function Footer() {
  return (
    <footer>
      <p>Copyright 2025. All rights reserved.</p>
    </footer>
  );
}

function App() {
  return (
    <div>
      <Header />
      <main>
        <h2>Welcome to my website!</h2>
        <p>This is the main content area.</p>
      </main>
      <Footer />
    </div>
  );
}
```

Here, `App` is composed of `Header`, some content, and `Footer`. The `Header` is composed of a heading and three `Button` components. Each piece is small and easy to understand on its own.

This is the power of composition: **small, simple pieces that combine into something bigger.**

---

## The `children` Prop for Flexible Content

So far, our components receive data through props like `label`, `title`, and `color`. But what if you want to put anything inside a component? Maybe sometimes you want text inside a card, and other times you want buttons, or images, or even other components.

This is where the special **`children` prop** comes in.

The `children` prop is whatever you put between the opening and closing tags of a component. It is like a container that can hold anything.

### Example: A Container Component

```jsx
function Container({ children }) {
  const style = {
    border: '2px solid blue',
    borderRadius: '8px',
    padding: '20px',
    margin: '10px'
  };

  return <div style={style}>{children}</div>;
}
```

- **`function Container({ children })`** — The component receives `children` as a prop. You do not pass `children` like `children={...}`. Instead, React automatically collects whatever is between the opening `<Container>` and closing `</Container>` tags.
- **`{children}`** — This renders whatever was placed inside the component.

### Using the Container

```jsx
function App() {
  return (
    <div>
      <Container>
        <h2>Hello!</h2>
        <p>This text is inside the container.</p>
      </Container>

      <Container>
        <Button label="Click Me" onClick={() => alert('Hi!')} color="green" />
      </Container>

      <Container>
        <img src="https://example.com/photo.jpg" alt="A photo" />
        <p>A photo with a caption.</p>
      </Container>
    </div>
  );
}
```

### Expected Output

You will see three blue-bordered boxes on the page:

- The first box contains a heading and a paragraph.
- The second box contains a green button.
- The third box contains an image and a caption.

The Container component does not care what is inside it. It just wraps its content in a styled box. This makes it very flexible and reusable.

### Combining Props and Children

You can use both regular props and `children` together:

```jsx
function Panel({ title, children }) {
  return (
    <div style={{ border: '1px solid #ccc', padding: '16px', margin: '10px' }}>
      <h3>{title}</h3>
      <div>{children}</div>
    </div>
  );
}

function App() {
  return (
    <div>
      <Panel title="Welcome">
        <p>Thank you for visiting our website.</p>
      </Panel>

      <Panel title="Settings">
        <Button label="Save" onClick={() => {}} color="green" />
        <Button label="Reset" onClick={() => {}} color="gray" />
      </Panel>
    </div>
  );
}
```

The `Panel` component uses the `title` prop for the heading and `children` for everything else inside it. This is a very common and useful pattern.

---

## When to Make Something a Separate Component

A common question beginners ask is: "When should I create a new component?" Here is a simple rule to follow:

### The "Used More Than Once" Rule

**If you use something more than once, make it a component.**

That is the simplest rule. If you find yourself copying and pasting similar code, stop. Turn that code into a component instead.

### Other Signs You Should Create a Component

1. **The code is getting long.** If your component has more than 50-80 lines, consider breaking it into smaller pieces.
2. **It has a clear purpose.** If a piece of your code does one specific thing (like showing a navigation bar), it can be its own component.
3. **You want to test it separately.** Smaller components are easier to test.
4. **It makes the code easier to read.** If naming a piece of code would make the parent component clearer, create a component.

### Example: Before and After

**Before (everything in one component):**

```jsx
function App() {
  return (
    <div>
      <div style={{ backgroundColor: 'blue', color: 'white', padding: '10px' }}>
        <h1>My Store</h1>
      </div>

      <div style={{ border: '1px solid #ddd', padding: '16px', margin: '10px' }}>
        <h2>Product A</h2>
        <p>$10.00</p>
        <button>Add to Cart</button>
      </div>

      <div style={{ border: '1px solid #ddd', padding: '16px', margin: '10px' }}>
        <h2>Product B</h2>
        <p>$20.00</p>
        <button>Add to Cart</button>
      </div>

      <div style={{ border: '1px solid #ddd', padding: '16px', margin: '10px' }}>
        <h2>Product C</h2>
        <p>$15.00</p>
        <button>Add to Cart</button>
      </div>
    </div>
  );
}
```

Notice how the product blocks look almost identical. This is a sign that we should create a component.

**After (with reusable components):**

```jsx
function StoreHeader() {
  return (
    <div style={{ backgroundColor: 'blue', color: 'white', padding: '10px' }}>
      <h1>My Store</h1>
    </div>
  );
}

function ProductCard({ name, price }) {
  return (
    <div style={{ border: '1px solid #ddd', padding: '16px', margin: '10px' }}>
      <h2>{name}</h2>
      <p>${price}</p>
      <button>Add to Cart</button>
    </div>
  );
}

function App() {
  return (
    <div>
      <StoreHeader />
      <ProductCard name="Product A" price="10.00" />
      <ProductCard name="Product B" price="20.00" />
      <ProductCard name="Product C" price="15.00" />
    </div>
  );
}
```

The "after" version is shorter, cleaner, and easier to change. If you want to redesign the product cards, you change one component and all three cards update.

---

## Organizing Reusable Components in a Folder

As your project grows, you will have many components. It helps to organize them. A common approach is to put reusable components in a `components` folder.

Here is a typical folder structure:

```
src/
  components/
    Button.jsx
    Card.jsx
    Container.jsx
    Panel.jsx
  pages/
    Home.jsx
    About.jsx
  App.jsx
```

- The **`components`** folder holds reusable pieces that can be used anywhere in your app.
- The **`pages`** folder holds components that represent full pages.
- **`App.jsx`** is the main component that puts everything together.

### How to Import Components

When your components are in separate files, you import them:

```jsx
// Inside Button.jsx
function Button({ label, onClick, color = 'blue' }) {
  const style = {
    backgroundColor: color,
    color: 'white',
    padding: '10px 20px',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    fontSize: '16px'
  };

  return (
    <button style={style} onClick={onClick}>
      {label}
    </button>
  );
}

export default Button;
```

```jsx
// Inside App.jsx
import Button from './components/Button';

function App() {
  return (
    <div>
      <Button label="Save" onClick={() => alert('Saved!')} color="green" />
    </div>
  );
}

export default App;
```

- **`export default Button;`** — This makes the Button component available to other files. Think of it like putting a book on a library shelf so others can borrow it.
- **`import Button from './components/Button';`** — This brings the Button component into App.jsx. Think of it like borrowing that book from the shelf.

---

## Mini Project: Product Card Grid

Let us put everything together and build a product card grid. We will create one reusable `ProductCard` component and use it to display several products.

### Step 1: The ProductCard Component

```jsx
function ProductCard({ name, price, description, imageUrl, onAddToCart }) {
  const cardStyle = {
    border: '1px solid #ddd',
    borderRadius: '8px',
    padding: '16px',
    width: '250px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
  };

  const imageStyle = {
    width: '100%',
    height: '150px',
    objectFit: 'cover',
    borderRadius: '4px'
  };

  const buttonStyle = {
    backgroundColor: '#007bff',
    color: 'white',
    padding: '8px 16px',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    width: '100%',
    fontSize: '14px'
  };

  return (
    <div style={cardStyle}>
      <img src={imageUrl} alt={name} style={imageStyle} />
      <h3>{name}</h3>
      <p>{description}</p>
      <p><strong>${price}</strong></p>
      <button style={buttonStyle} onClick={onAddToCart}>
        Add to Cart
      </button>
    </div>
  );
}
```

Line by line:

- **`function ProductCard({ name, price, description, imageUrl, onAddToCart })`** — This component accepts five props: the product name, price, description, image URL, and a function to call when the user clicks "Add to Cart."
- **`objectFit: 'cover'`** — This makes the image fill its space without stretching. It might crop the edges, but the image always looks good.
- **`width: '100%'`** on the button — This makes the button stretch to fill the full width of the card.
- **`onClick={onAddToCart}`** — When the button is clicked, it calls the function that was passed in as a prop.

### Step 2: The Product Data

```jsx
const products = [
  {
    id: 1,
    name: 'Wireless Headphones',
    price: 49.99,
    description: 'Great sound quality with noise cancellation.',
    imageUrl: 'https://example.com/headphones.jpg'
  },
  {
    id: 2,
    name: 'Coffee Mug',
    price: 12.99,
    description: 'Keeps your coffee warm for hours.',
    imageUrl: 'https://example.com/mug.jpg'
  },
  {
    id: 3,
    name: 'Notebook',
    price: 8.99,
    description: 'Lined pages, perfect for notes and ideas.',
    imageUrl: 'https://example.com/notebook.jpg'
  },
  {
    id: 4,
    name: 'Desk Lamp',
    price: 29.99,
    description: 'Adjustable brightness for comfortable reading.',
    imageUrl: 'https://example.com/lamp.jpg'
  }
];
```

This is an array (a list) of product objects. Each product has an `id`, `name`, `price`, `description`, and `imageUrl`.

### Step 3: The App Component

```jsx
function App() {
  function handleAddToCart(productName) {
    alert(productName + ' added to cart!');
  }

  const gridStyle = {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '20px',
    padding: '20px',
    justifyContent: 'center'
  };

  return (
    <div>
      <h1 style={{ textAlign: 'center' }}>Our Products</h1>
      <div style={gridStyle}>
        {products.map(function (product) {
          return (
            <ProductCard
              key={product.id}
              name={product.name}
              price={product.price}
              description={product.description}
              imageUrl={product.imageUrl}
              onAddToCart={function () {
                handleAddToCart(product.name);
              }}
            />
          );
        })}
      </div>
    </div>
  );
}
```

Line by line:

- **`handleAddToCart(productName)`** — A function that shows an alert when a product is added to the cart.
- **`display: 'flex'`** — This puts the cards in a row. Flex is a layout system that arranges items side by side.
- **`flexWrap: 'wrap'`** — This tells the browser to wrap cards to the next line if they do not fit.
- **`gap: '20px'`** — This adds space between the cards.
- **`products.map(function (product) { ... })`** — This loops through the products array and creates one `ProductCard` for each product.
- **`key={product.id}`** — React needs a unique key for each item in a list so it can track them properly.
- **`onAddToCart={function () { handleAddToCart(product.name); }}`** — We wrap the function call so that it passes the right product name when clicked.

### Expected Output

You will see a centered heading "Our Products" and four product cards arranged in a grid. Each card shows an image, a product name, a description, a price, and an "Add to Cart" button. Clicking any "Add to Cart" button shows an alert with the product name.

---

## Quick Summary

- **Reuse** means writing a component once and using it many times.
- **Props** let you customize each use of a component.
- **Composition** means building big things from small components.
- The **`children` prop** lets you put any content inside a component.
- Create a new component when you use something more than once.
- Organize reusable components in a **`components` folder**.
- Use **`map`** to create many instances of a component from data.

---

## Key Points to Remember

1. A reusable component is like a cookie cutter. You design it once, then use it many times with small differences.
2. Props make components flexible. The same Button component can be green, red, or gray depending on what props you pass.
3. The `children` prop is special. It automatically receives whatever you put between the opening and closing tags of a component.
4. Composition is how React apps are built. Small components combine into bigger ones, which combine into pages, which combine into apps.
5. The "used more than once" rule is a simple guide: if you copy-paste code, turn it into a component instead.
6. Default props (like `color = 'blue'`) prevent errors when someone forgets to pass a prop.

---

## Practice Questions

1. What does "reuse" mean in the context of React components?
2. How does the `children` prop work? How is it different from other props?
3. You have a website with 10 pages, and each page has the same footer. Should you create a Footer component? Why?
4. What is the difference between passing `label="Save"` as a prop and putting content between `<Component>` and `</Component>`?
5. Why is it a good idea to organize reusable components in a `components` folder?

---

## Exercises

### Exercise 1: Reusable Alert Box

Create a reusable `AlertBox` component that shows a colored message box. It should accept a `type` prop that can be `"success"`, `"warning"`, or `"error"`. Each type should have a different background color (green, yellow, red). It should use the `children` prop for the message text.

Use it like this:

```jsx
<AlertBox type="success">Your file was saved!</AlertBox>
<AlertBox type="warning">Your session will expire soon.</AlertBox>
<AlertBox type="error">Something went wrong.</AlertBox>
```

### Exercise 2: User Profile Card

Create a reusable `ProfileCard` component that shows a user's name, email, and avatar image. Then display three different profile cards using the same component with different data.

### Exercise 3: Reusable Layout

Create a `PageLayout` component that uses `children`. It should include a header at the top (with a title), the children content in the middle, and a footer at the bottom. Use this layout to wrap two different pages of content.

---

## What Is Next?

You now know how to build reusable components and combine them together. But what happens when two separate components need to share the same piece of data? For example, what if a product list and a shopping cart both need to know what items the user has selected?

In the next chapter, you will learn about **lifting state up** — a technique for sharing data between components by moving the state to their common parent. This is one of the most important patterns in React, and it builds directly on what you learned here about props and composition.
