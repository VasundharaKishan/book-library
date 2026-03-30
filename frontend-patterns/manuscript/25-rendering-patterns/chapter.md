# Chapter 25: Rendering Patterns -- CSR, SSR, SSG, ISR, and Beyond

## What You Will Learn

- The four core rendering strategies: CSR, SSR, SSG, and ISR
- How hydration works and why it matters
- What streaming SSR brings to the table
- How React Server Components change the game
- A decision flowchart for choosing the right rendering pattern
- Trade-offs of each approach with real performance data

## Why This Chapter Matters

When you build a React application, one of the most impactful architectural decisions you make is **how and where your HTML gets generated**. This single choice affects:

- How fast users see content (First Contentful Paint)
- How fast they can interact with it (Time to Interactive)
- How well search engines find your pages (SEO)
- How much your servers cost to run
- How complex your deployment is

Most tutorials teach you Client-Side Rendering (CSR) first because it is the simplest. But in production, CSR is often the wrong default. Understanding all the rendering patterns lets you pick the right tool for each page in your application.

Think of it like cooking methods. You could microwave everything, but sometimes you need to grill, sometimes bake, and sometimes serve it raw. Each method exists because it solves a different problem best.

---

## Pattern 1: Client-Side Rendering (CSR)

### The Problem

You want to build a highly interactive application like a dashboard, a chat app, or an internal tool. The content is dynamic and personalized. SEO does not matter much.

### The Solution

Ship an almost-empty HTML file to the browser. Let JavaScript download, execute, and build the entire UI on the client.

### How CSR Works

```
+------------------+     +------------------+     +------------------+
|   Browser asks   |     |  Server sends    |     | Browser runs JS  |
|   for page       | --> |  empty HTML +    | --> | and builds the   |
|                  |     |  JS bundle       |     | entire DOM       |
+------------------+     +------------------+     +------------------+
                                                         |
                                                         v
                                               +------------------+
                                               | User finally     |
                                               | sees content     |
                                               +------------------+

Timeline:
|-- HTML downloaded --|-- JS downloaded --|-- JS executes --|-- Content visible --|
0s                   0.2s                1.5s               2.5s
                                                    (example times)
```

### Code Example

A typical CSR setup with React and Vite:

```html
<!-- index.html - This is ALL the server sends -->
<!DOCTYPE html>
<html>
<head>
  <title>My App</title>
</head>
<body>
  <div id="root"></div>
  <!-- The entire app is in this JS bundle -->
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>
```

```jsx
// src/main.jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
```

```jsx
// src/App.jsx
import { useState, useEffect } from 'react';

function App() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Data fetching happens AFTER JavaScript loads and runs
    fetch('/api/products')
      .then(res => res.json())
      .then(data => {
        setProducts(data);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading products...</div>;

  return (
    <div>
      <h1>Products</h1>
      {products.map(p => (
        <div key={p.id}>{p.name} - ${p.price}</div>
      ))}
    </div>
  );
}

// Output (what the user sees):
// First: "Loading products..." (after JS downloads and executes)
// Then:  "Products"
//        "Widget A - $29.99"
//        "Widget B - $49.99"
```

### What Crawlers See

```
View Source (what Google's crawler initially sees):

<html>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>

// Almost nothing! No product names, no prices, no content.
// Google CAN execute JavaScript, but it is slower and less reliable.
```

---

## Pattern 2: Server-Side Rendering (SSR)

### The Problem

You need good SEO. You want users to see content immediately, not wait for JavaScript to download and execute. But the content is dynamic and changes per request.

### The Solution

Run React on the server for every request. Generate the full HTML there, send it to the browser, then "hydrate" it with JavaScript to make it interactive.

### How SSR Works

```
+------------------+     +------------------+     +------------------+
|   Browser asks   |     | Server runs React|     | Browser receives |
|   for page       | --> | and generates    | --> | FULL HTML with   |
|                  |     | complete HTML    |     | all content      |
+------------------+     +------------------+     +------------------+
                                                         |
                                                         v
                                               +------------------+
                                               | User sees content|
                                               | IMMEDIATELY      |
                                               +------------------+
                                                         |
                                                         v
                                               +------------------+
                                               | JS downloads and |
                                               | "hydrates" the   |
                                               | page (adds       |
                                               | interactivity)   |
                                               +------------------+

Timeline:
|-- Server renders --|-- HTML arrives --|-- Content visible --|-- JS hydrates --|
0s                  0.3s               0.5s                  2.0s
                                   (user sees content!)
```

### Code Example

Using Next.js (the most popular SSR framework for React):

```jsx
// pages/products.jsx (Next.js Pages Router)

// This function runs on the SERVER for every request
export async function getServerSideProps() {
  // Fetch data on the server - fast because server is close to database
  const res = await fetch('https://api.example.com/products');
  const products = await res.json();

  return {
    props: { products }, // Passed to the component as props
  };
}

function ProductsPage({ products }) {
  // This component renders on BOTH server and client
  return (
    <div>
      <h1>Products</h1>
      {products.map(p => (
        <div key={p.id}>
          <h2>{p.name}</h2>
          <p>${p.price}</p>
          <button onClick={() => addToCart(p.id)}>
            Add to Cart
          </button>
        </div>
      ))}
    </div>
  );
}

export default ProductsPage;

// Output (what the user sees):
// IMMEDIATELY (before JS loads):
//   "Products"
//   "Widget A"
//   "$29.99"
//   [Add to Cart] (button visible but NOT clickable yet)
//
// AFTER hydration (JS loads):
//   [Add to Cart] (button NOW clickable)
```

### What Crawlers See

```
View Source (what Google's crawler sees):

<html>
<body>
  <div id="root">
    <div>
      <h1>Products</h1>
      <div>
        <h2>Widget A</h2>
        <p>$29.99</p>
        <button>Add to Cart</button>
      </div>
      <div>
        <h2>Widget B</h2>
        <p>$49.99</p>
        <button>Add to Cart</button>
      </div>
    </div>
  </div>
</body>
</html>

// Full content is right there in the HTML. Perfect for SEO.
```

---

## Understanding Hydration

Hydration is one of the most misunderstood concepts in modern React. Let us break it down.

### What Is Hydration?

When the server sends pre-rendered HTML, the browser displays it instantly. But it is just static HTML. Buttons do not work. Forms do not submit. Nothing is interactive.

**Hydration** is the process where React takes over that static HTML, attaches event listeners, and makes everything interactive.

```
Before Hydration:                    After Hydration:
+------------------------+          +------------------------+
|  <button>Add to Cart   |          |  <button>Add to Cart   |
|                        |          |                        |
|  Status: DEAD HTML     |          |  Status: ALIVE React   |
|  Click? Nothing happens|          |  Click? Adds to cart!  |
+------------------------+          +------------------------+

The HTML looks the same. But now React "owns" it.
```

### How Hydration Works Under the Hood

```jsx
// Step 1: Server renders React to HTML string
import { renderToString } from 'react-dom/server';
const html = renderToString(<App />);
// Result: '<div><h1>Hello</h1><button>Click me</button></div>'

// Step 2: Server sends that HTML to the browser
// Browser displays it immediately (fast!)

// Step 3: Client-side React "hydrates" the existing HTML
import { hydrateRoot } from 'react-dom/client';
hydrateRoot(document.getElementById('root'), <App />);

// React walks through the existing DOM
// It attaches event listeners
// It sets up state and effects
// The HTML MUST match what React would render
```

### The Hydration Mismatch Problem

```jsx
// BAD: This will cause a hydration mismatch
function Greeting() {
  // On server: renders "Hello" at 3:00 PM server time
  // On client: renders "Hello" at 3:01 PM user time
  return <p>Current time: {new Date().toLocaleTimeString()}</p>;
}
// React will warn: "Text content did not match"

// GOOD: Defer client-only values to useEffect
function Greeting() {
  const [time, setTime] = useState(null);

  useEffect(() => {
    // useEffect only runs on the client, after hydration
    setTime(new Date().toLocaleTimeString());
  }, []);

  return <p>Current time: {time ?? 'Loading...'}</p>;
}
```

---

## Pattern 3: Static Site Generation (SSG)

### The Problem

You have content that does not change often. Blog posts, documentation, marketing pages. You want maximum performance and minimal server costs.

### The Solution

Generate all HTML at **build time**. Every page becomes a static file. Serve them from a CDN. No server needed at runtime.

### How SSG Works

```
BUILD TIME (once):
+------------------+     +------------------+     +------------------+
|  Developer runs  |     | Build process    |     | Static HTML      |
|  "npm run build" | --> | renders EVERY    | --> | files ready to   |
|                  |     | page to HTML     |     | deploy           |
+------------------+     +------------------+     +------------------+

RUNTIME (every request):
+------------------+     +------------------+     +------------------+
|   Browser asks   |     | CDN serves       |     | User sees page   |
|   for page       | --> | pre-built HTML   | --> | INSTANTLY         |
|                  |     | (no computation) |     | (fastest possible)|
+------------------+     +------------------+     +------------------+

Timeline:
|-- CDN responds --|-- Content visible --|
0s                0.1s                  0.2s
                (blazing fast!)
```

### Code Example

```jsx
// pages/blog/[slug].jsx (Next.js Pages Router)

// Runs at BUILD TIME - tells Next.js which pages to generate
export async function getStaticPaths() {
  const res = await fetch('https://api.example.com/posts');
  const posts = await res.json();

  // Generate a page for each blog post
  const paths = posts.map(post => ({
    params: { slug: post.slug },
  }));

  return { paths, fallback: false };
}

// Runs at BUILD TIME for each path
export async function getStaticProps({ params }) {
  const res = await fetch(
    `https://api.example.com/posts/${params.slug}`
  );
  const post = await res.json();

  return {
    props: { post },
  };
}

function BlogPost({ post }) {
  return (
    <article>
      <h1>{post.title}</h1>
      <p>Published: {post.date}</p>
      <div dangerouslySetInnerHTML={{ __html: post.content }} />
    </article>
  );
}

export default BlogPost;

// At build time, this generates files like:
//   /blog/my-first-post.html
//   /blog/react-patterns.html
//   /blog/javascript-tips.html
// Each is a complete HTML file served from CDN
```

### The Stale Content Problem

```
SSG Problem:

Build at 9:00 AM --> HTML generated with current data
User visits at 3:00 PM --> sees 9:00 AM data
Author fixes typo at 3:30 PM --> still old data
Need to rebuild and redeploy --> 5 minute build process

For a blog with 10,000 posts, rebuilding everything
for a single typo fix is wasteful.
```

This leads us to the next pattern.

---

## Pattern 4: Incremental Static Regeneration (ISR)

### The Problem

SSG is fast but stale. SSR is fresh but slow. You want both: the speed of static files with the freshness of server rendering.

### The Solution

Serve static pages, but **regenerate them in the background** after a specified time period. Users always get fast static responses. The content stays reasonably fresh.

### How ISR Works

```
Initial Build:
  Same as SSG - generate all pages as static HTML

First Request (within revalidation window):
+------------------+     +------------------+
|   Browser asks   |     | CDN serves       |
|   for page       | --> | cached static    |  (fast, possibly stale)
|                  |     | HTML             |
+------------------+     +------------------+

First Request AFTER revalidation window:
+------------------+     +------------------+     +------------------+
|   Browser asks   |     | CDN serves       |     | Server rebuilds  |
|   for page       | --> | STALE cached     | --> | page in the      |
|                  |     | HTML (still fast) |     | BACKGROUND       |
+------------------+     +------------------+     +------------------+
                                                         |
                                                         v
                                               +------------------+
                                               | Next request     |
                                               | gets FRESH page  |
                                               +------------------+

This is called "stale-while-revalidate" strategy.
```

### Code Example

```jsx
// pages/products/[id].jsx

export async function getStaticPaths() {
  const res = await fetch('https://api.example.com/products');
  const products = await res.json();

  const paths = products.map(p => ({
    params: { id: p.id.toString() },
  }));

  return {
    paths,
    fallback: 'blocking', // Generate new pages on-demand
  };
}

export async function getStaticProps({ params }) {
  const res = await fetch(
    `https://api.example.com/products/${params.id}`
  );
  const product = await res.json();

  return {
    props: { product },
    revalidate: 60, // Regenerate this page every 60 seconds
  };
}

function ProductPage({ product }) {
  return (
    <div>
      <h1>{product.name}</h1>
      <p>${product.price}</p>
      <p>In Stock: {product.inStock ? 'Yes' : 'No'}</p>
    </div>
  );
}

export default ProductPage;

// How it plays out:
//
// 9:00:00 AM - Build generates page with price $29.99
// 9:00:30 AM - User visits, gets cached $29.99 (fast!)
// 9:00:45 AM - Admin changes price to $24.99
// 9:01:00 AM - User visits, gets cached $29.99 (stale but fast!)
//              Background: server regenerates page with $24.99
// 9:01:05 AM - User visits, gets fresh $24.99 page (fast!)
```

### On-Demand Revalidation

Instead of time-based revalidation, you can trigger rebuilds manually:

```jsx
// pages/api/revalidate.js
export default async function handler(req, res) {
  // Verify the request is legitimate
  if (req.query.secret !== process.env.REVALIDATION_SECRET) {
    return res.status(401).json({ message: 'Invalid token' });
  }

  try {
    // Rebuild a specific page immediately
    await res.revalidate(`/products/${req.query.id}`);
    return res.json({ revalidated: true });
  } catch (err) {
    return res.status(500).send('Error revalidating');
  }
}

// Usage: When admin updates a product in the CMS,
// the CMS webhook calls:
// POST /api/revalidate?secret=MY_SECRET&id=42
// And only that product page gets regenerated.
```

---

## Streaming SSR

### The Problem with Traditional SSR

Traditional SSR has a waterfall problem:

```
Traditional SSR Waterfall:

Server:  [---Fetch ALL data---][---Render ALL HTML---]
Network:                                              [---Send ALL HTML---]
Browser:                                                                   [---Show ALL---]

Nothing is shown until EVERYTHING is ready.
If one API call is slow, the entire page is delayed.

Example: Product page needs:
  1. Product details (50ms)
  2. Reviews (2000ms)     <-- Slow API!
  3. Recommendations (100ms)

Total wait: 2150ms before user sees ANYTHING.
```

### The Solution: Streaming SSR

Send HTML in chunks as each part becomes ready.

```
Streaming SSR:

Server:  [Fetch product (50ms)]
         [----------Render product shell----------]
Network:                        [Send shell HTML]
Browser:                                         [Show product!]

Server:  [----------Fetch reviews (2000ms)---------]
         [-----Render reviews-----]
Network:                           [Stream reviews HTML]
Browser:                                                [Show reviews!]

User sees the product in 50ms instead of waiting 2150ms!
```

### Code Example (React 18+ with Next.js App Router)

```jsx
// app/products/[id]/page.jsx
import { Suspense } from 'react';

// This component can be async - it is a Server Component
async function ProductDetails({ id }) {
  const product = await fetch(
    `https://api.example.com/products/${id}`
  ).then(r => r.json());

  return (
    <div>
      <h1>{product.name}</h1>
      <p>${product.price}</p>
    </div>
  );
}

// This slow component will stream in later
async function ProductReviews({ id }) {
  // This API is slow - takes 2 seconds
  const reviews = await fetch(
    `https://api.example.com/products/${id}/reviews`
  ).then(r => r.json());

  return (
    <div>
      <h2>Reviews ({reviews.length})</h2>
      {reviews.map(r => (
        <div key={r.id}>
          <strong>{r.author}</strong>: {r.text}
        </div>
      ))}
    </div>
  );
}

// The page component uses Suspense for streaming
export default function ProductPage({ params }) {
  return (
    <div>
      {/* This renders and sends immediately */}
      <Suspense fallback={<p>Loading product...</p>}>
        <ProductDetails id={params.id} />
      </Suspense>

      {/* This streams in when ready, showing fallback first */}
      <Suspense fallback={<p>Loading reviews...</p>}>
        <ProductReviews id={params.id} />
      </Suspense>
    </div>
  );
}

// Output sequence:
// 1. Browser receives: product details + "Loading reviews..."
// 2. Browser receives: actual reviews (streamed in later)
// User sees useful content almost immediately!
```

---

## React Server Components (RSC)

### The Problem

Even with SSR, we ship all the React component code to the client for hydration. A product page might import a Markdown renderer, a date formatting library, and a syntax highlighter. The user downloads all of that JavaScript even though it only runs once on the server.

### The Solution

React Server Components run **only on the server**. They never ship JavaScript to the client. They can directly access databases, file systems, and APIs. Client Components handle interactivity.

```
Traditional SSR:
+---------------------------+
|  Server renders HTML      |
|  Client downloads ALL JS  |
|  Client hydrates ALL      |
+---------------------------+
JS Bundle: [ProductPage + ReviewList + MarkdownRenderer + DateLib]
           (everything, even non-interactive parts)

React Server Components:
+---------------------------+
|  Server Components stay   |
|  on server (zero JS sent) |
|  Client Components sent   |
|  only for interactive bits|
+---------------------------+
JS Bundle: [AddToCartButton + ReviewForm]
           (only interactive parts!)
```

### Code Example

```jsx
// app/products/[id]/page.jsx
// This is a SERVER Component by default in Next.js App Router
// It NEVER runs in the browser. Zero JavaScript sent for this.

import { db } from '@/lib/database';      // Direct DB access!
import { formatDate } from '@/lib/utils';  // Not sent to client
import AddToCartButton from './AddToCartButton'; // Client Component

export default async function ProductPage({ params }) {
  // Query database directly - no API needed!
  const product = await db.products.findById(params.id);

  return (
    <div>
      <h1>{product.name}</h1>
      <p>${product.price}</p>
      <p>Added: {formatDate(product.createdAt)}</p>

      {/* Only THIS component's JS is sent to the browser */}
      <AddToCartButton productId={product.id} />
    </div>
  );
}
```

```jsx
// app/products/[id]/AddToCartButton.jsx
'use client'; // This directive marks it as a Client Component

import { useState } from 'react';

export default function AddToCartButton({ productId }) {
  const [added, setAdded] = useState(false);

  async function handleClick() {
    await fetch('/api/cart', {
      method: 'POST',
      body: JSON.stringify({ productId }),
    });
    setAdded(true);
  }

  return (
    <button onClick={handleClick}>
      {added ? 'Added!' : 'Add to Cart'}
    </button>
  );
}

// Only this small component ships JavaScript to the browser.
// The entire ProductPage, database library, date formatting
// library -- none of that goes to the client.
```

### Server vs Client Component Rules

```
+-------------------------------+-----------------------------------+
|     Server Components         |      Client Components            |
+-------------------------------+-----------------------------------+
| Default in App Router         | Must add 'use client' directive   |
| Can access database/fs        | Cannot access server resources    |
| Can use async/await           | Cannot be async                   |
| Cannot use useState           | Can use useState                  |
| Cannot use useEffect          | Can use useEffect                 |
| Cannot use event handlers     | Can use onClick, onChange, etc.   |
| Cannot use browser APIs       | Can use window, document, etc.   |
| Zero JavaScript to client     | JavaScript sent to client         |
| Can import Client Components  | Cannot import Server Components   |
+-------------------------------+-----------------------------------+
```

---

## Comparing All Rendering Patterns

```
+-------+------------------+-----------------+---------+----------+
|Pattern| When HTML is     | Data Freshness  | Speed   | SEO      |
|       | Generated        |                 |         |          |
+-------+------------------+-----------------+---------+----------+
| CSR   | In browser       | Always fresh    | Slowest | Poor     |
|       | (at runtime)     | (fetches live)  | initial |          |
+-------+------------------+-----------------+---------+----------+
| SSR   | On server        | Always fresh    | Fast    | Great    |
|       | (per request)    | (per request)   | initial |          |
+-------+------------------+-----------------+---------+----------+
| SSG   | At build time    | Stale until     | Fastest | Great    |
|       | (once)           | next build      |         |          |
+-------+------------------+-----------------+---------+----------+
| ISR   | At build time +  | Mostly fresh    | Fast    | Great    |
|       | background regen | (configurable)  |         |          |
+-------+------------------+-----------------+---------+----------+
| Stream| On server        | Always fresh    | Fast    | Great    |
| SSR   | (per request,    | (per request)   | initial |          |
|       |  in chunks)      |                 | (progr.)|          |
+-------+------------------+-----------------+---------+----------+
| RSC   | Server (server   | Fresh for       | Minimal | Great    |
|       | parts) + Client  | server parts    | JS sent |          |
|       | (interactive)    |                 |         |          |
+-------+------------------+-----------------+---------+----------+
```

---

## Decision Flowchart

Use this flowchart to choose the right rendering pattern:

```
                    START
                      |
                      v
              Does SEO matter?
              /             \
           No                Yes
            |                  |
            v                  v
     Is it highly        Does content change
     interactive?        per request?
     (dashboard,         /              \
      internal tool)   Yes               No
            |            |                |
            v            v                v
          CSR          SSR or        Does content change
                    Streaming SSR    frequently?
                                     /          \
                                   Yes           No
                                    |             |
                                    v             v
                                   ISR           SSG


     Additional considerations:

     Large JS bundle?  --> Add React Server Components
     Slow API calls?   --> Use Streaming SSR with Suspense
     Need offline?     --> CSR with Service Worker
     E-commerce?       --> ISR (products) + SSR (cart) + SSG (about)
```

---

## Real-World Use Case: E-Commerce Site

A real e-commerce site uses **multiple rendering patterns** on different pages:

```jsx
// PATTERN MIX for an e-commerce site:

// Landing page --> SSG (rarely changes, must be fast)
// app/page.jsx (Server Component, built at deploy time)

// Product listing --> ISR (products change, but not every second)
// app/products/page.jsx with revalidate: 300

// Product detail --> ISR + Streaming SSR
// app/products/[id]/page.jsx
//   - Product info: ISR (revalidate: 60)
//   - Reviews: Streamed in with Suspense
//   - "Add to Cart": Client Component

// Shopping cart --> CSR (user-specific, no SEO needed)
// app/cart/page.jsx with 'use client'

// Checkout --> SSR (must be fresh, needs auth)
// app/checkout/page.jsx (Server Component with auth check)

// Blog posts --> SSG (content does not change)
// app/blog/[slug]/page.jsx (built at deploy time)
```

```jsx
// Example: Product page mixing patterns
// app/products/[id]/page.jsx

import { Suspense } from 'react';
import { db } from '@/lib/database';
import AddToCart from './AddToCart';         // Client Component
import Reviews from './Reviews';             // Server Component (async)
import Recommendations from './Recommendations';

// ISR: Regenerate every 60 seconds
export const revalidate = 60;

export default async function ProductPage({ params }) {
  // Server Component: direct DB access, zero client JS
  const product = await db.products.findById(params.id);

  return (
    <main>
      {/* Rendered immediately */}
      <section>
        <h1>{product.name}</h1>
        <p className="price">${product.price}</p>
        <p>{product.description}</p>

        {/* Only interactive part ships JS */}
        <AddToCart product={product} />
      </section>

      {/* Streams in when ready */}
      <Suspense fallback={<ReviewsSkeleton />}>
        <Reviews productId={product.id} />
      </Suspense>

      {/* Also streams independently */}
      <Suspense fallback={<RecommendationsSkeleton />}>
        <Recommendations category={product.category} />
      </Suspense>
    </main>
  );
}
```

---

## When to Use / When NOT to Use

### Use CSR When

- Building dashboards and admin panels
- Internal tools behind authentication
- Highly interactive apps (chat, collaborative editors)
- SEO does not matter

### Do NOT Use CSR When

- SEO matters (blog, e-commerce, marketing pages)
- First load performance is critical
- Users are on slow connections or devices

### Use SSR When

- Content is personalized per user (logged-in pages)
- Data must be fresh on every request
- SEO matters and content changes frequently

### Do NOT Use SSR When

- Content rarely changes (use SSG or ISR instead)
- You cannot afford server costs for every request
- Pages are simple and static

### Use SSG When

- Content rarely changes (docs, blog, marketing)
- Maximum performance is needed
- You want minimal hosting costs (static hosting)

### Do NOT Use SSG When

- Content changes frequently
- You have thousands of pages that rebuild slowly
- Content is personalized per user

### Use ISR When

- Content changes but not on every request
- You have many pages (e-commerce catalogs)
- You want static performance with reasonable freshness

---

## Common Mistakes

### Mistake 1: Using CSR for Everything

```
WRONG thinking:
"Create React App uses CSR and it works fine for development,
 so I will use it for production too."

PROBLEM:
- Users stare at a blank screen for 2-3 seconds
- Search engines may not index your content
- Performance scores tank on Lighthouse

FIX:
Evaluate each page. Most public-facing pages benefit from
SSR, SSG, or ISR. Reserve CSR for interactive authenticated pages.
```

### Mistake 2: Using SSR When SSG Would Work

```
WRONG:
export async function getServerSideProps() {
  const aboutContent = await fetchCMSContent('about-page');
  return { props: { aboutContent } };
}
// The about page renders on every request, even though
// it changes once a month.

RIGHT:
export async function getStaticProps() {
  const aboutContent = await fetchCMSContent('about-page');
  return {
    props: { aboutContent },
    revalidate: 3600, // Check for updates hourly
  };
}
// Static page, regenerated hourly. Much faster.
```

### Mistake 3: Ignoring Hydration Mismatches

```jsx
// WRONG: Different output on server vs client
function Component() {
  return <p>Window width: {window.innerWidth}</p>;
  // Crashes on server! window does not exist there.
}

// ALSO WRONG: Conditional rendering based on typeof window
function Component() {
  if (typeof window !== 'undefined') {
    return <p>Client: {window.innerWidth}</p>;
  }
  return <p>Server</p>;
  // Different HTML on server vs client = hydration mismatch
}

// RIGHT: Use useEffect for client-only values
function Component() {
  const [width, setWidth] = useState(0);

  useEffect(() => {
    setWidth(window.innerWidth);
    const handleResize = () => setWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return <p>Window width: {width || 'Loading...'}</p>;
}
```

---

## Best Practices

1. **Mix rendering patterns per page** -- Use the right strategy for each page, not one strategy for the entire app.

2. **Default to Server Components** -- In the App Router, keep components as Server Components unless they need interactivity. This minimizes client JavaScript.

3. **Push 'use client' down the tree** -- Mark the smallest possible component as a Client Component, not entire pages.

4. **Use Suspense boundaries strategically** -- Wrap slow data fetches in Suspense to stream content progressively.

5. **Set appropriate revalidation intervals** -- For ISR, match the revalidation time to how often your data actually changes.

6. **Monitor hydration errors in development** -- React shows hydration mismatch warnings in the console. Fix them immediately.

7. **Use `loading.jsx` in App Router** -- Next.js App Router automatically wraps pages in Suspense when you add a `loading.jsx` file.

8. **Profile before optimizing** -- Use Lighthouse, Web Vitals, and your framework's built-in analytics to measure actual performance.

---

## Quick Summary

Rendering patterns determine where and when your HTML is generated. CSR builds everything in the browser (simple but slow). SSR generates HTML on the server per request (fresh but server-intensive). SSG pre-builds pages at deploy time (fastest but stale). ISR combines static speed with background regeneration. Streaming SSR sends HTML in chunks as data becomes available. React Server Components keep non-interactive code on the server, dramatically reducing client JavaScript. Most production apps mix multiple patterns based on each page's needs.

---

## Key Points

- **CSR**: Browser builds HTML. Simple setup. Poor initial load and SEO.
- **SSR**: Server builds HTML per request. Great SEO. Server cost per request.
- **SSG**: Build step generates HTML. Fastest delivery. Content can go stale.
- **ISR**: Static + background regeneration. Fast with configurable freshness.
- **Hydration**: Process of making server-rendered HTML interactive on the client.
- **Streaming SSR**: Send HTML in chunks. Users see content progressively.
- **React Server Components**: Server-only components that ship zero JavaScript.
- **Mix patterns**: Use the right rendering strategy for each page in your app.

---

## Practice Questions

1. You are building a news website. The homepage shows trending articles that update every few minutes. Individual articles rarely change after publication. Which rendering patterns would you use for the homepage and for article pages? Why?

2. A developer uses `getServerSideProps` for their company's "About Us" page that changes once a year. What is wrong with this approach, and what would you recommend instead?

3. Explain the concept of hydration to a non-technical person. Why does a page sometimes look loaded but not respond to clicks?

4. A React component renders `Math.random()` in its JSX. What problem will this cause with SSR, and how would you fix it?

5. You have a product page where the product details load in 50ms but customer reviews take 3 seconds. How would streaming SSR improve the user experience compared to traditional SSR?

---

## Exercises

### Exercise 1: Rendering Pattern Audit

Take a website you use regularly (Amazon, Wikipedia, your company's site). For each major page type (homepage, listing, detail, cart, account), identify which rendering pattern would be ideal. Create a table showing:
- Page type
- Recommended rendering pattern
- Reasoning (SEO needs, data freshness, interactivity)

### Exercise 2: Convert CSR to SSR

Take a simple CSR React component that fetches data in `useEffect` and convert it to use `getServerSideProps` in Next.js. Then convert it again to use `getStaticProps` with ISR. Compare the three approaches by measuring First Contentful Paint.

### Exercise 3: Server and Client Component Split

You have a blog post page with: a header (static), article content (from CMS), a "like" button (interactive), and a comment section (interactive with form). Draw a component tree and mark each component as Server or Client. Explain why you made each choice.

---

## What Is Next?

Now that you understand how to render your pages efficiently, the next challenge is making sure you do not send too much JavaScript to the browser in the first place. In Chapter 26, we will explore **Code Splitting and Lazy Loading** -- techniques that break your JavaScript bundle into smaller pieces and load them only when needed.
