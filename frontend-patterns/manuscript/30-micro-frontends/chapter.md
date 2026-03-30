# Chapter 30: Micro-Frontends

## What You Will Learn

- What micro-frontends are and why large organizations adopt them
- How Module Federation enables sharing code between independently deployed apps
- Using Web Components for framework-agnostic composition
- Routing-based composition strategies
- Communication patterns between micro-frontends
- The real trade-offs: what you gain and what you pay
- When micro-frontends are the right (and wrong) choice

## Why This Chapter Matters

You work at a growing company. Two years ago, your React app was built and maintained by a single team of five developers. Now the company has fifty frontend developers organized into eight teams: checkout, product catalog, search, user accounts, analytics dashboard, marketing pages, admin tools, and design system.

All fifty developers push code to the same repository. A bug in the checkout flow blocks a deploy of new search features. The analytics team wants to use a charting library that conflicts with one the product team uses. Every pull request touches shared code, causing merge conflicts. Deploys take 45 minutes because the entire monolith must be built and tested.

Micro-frontends solve this problem by splitting the monolithic frontend into independent applications, each owned and deployed by a separate team. The checkout team ships checkout. The search team ships search. They compose into one seamless experience for the user.

Think of it like a shopping mall. Each store (micro-frontend) is independently owned, decorated, and staffed. But to the shopper (user), it feels like one cohesive experience. The mall (shell application) provides the shared infrastructure: hallways, parking, security.

---

## What Are Micro-Frontends?

### The Core Idea

```
Monolithic Frontend:
+------------------------------------------------------------------+
|                    One Application                               |
|                    One Repository                                |
|                    One Deploy Pipeline                           |
|                    One Team (or many teams stepping on each other)|
|                                                                  |
|  [Header] [Search] [Products] [Cart] [Checkout] [Account]       |
|  [Admin]  [Analytics] [Marketing]                                |
+------------------------------------------------------------------+

Micro-Frontend Architecture:
+------------------------------------------------------------------+
|  Shell Application (routing, shared layout, authentication)      |
+------------------------------------------------------------------+
|                    |                    |                         |
|  +--------------+  |  +--------------+ |  +--------------+       |
|  | Search MFE   |  |  | Product MFE  | |  | Cart MFE     |       |
|  | Team: Search |  |  | Team: Catalog| |  | Team: Checkout|      |
|  | Deploy: Own  |  |  | Deploy: Own  | |  | Deploy: Own  |       |
|  | React 18     |  |  | React 18     | |  | React 18     |       |
|  +--------------+  |  +--------------+ |  +--------------+       |
|                    |                    |                         |
|  +--------------+  |  +--------------+ |  +--------------+       |
|  | Account MFE  |  |  | Admin MFE    | |  | Analytics MFE|       |
|  | Team: Users  |  |  | Team: Admin  | |  | Team: Data   |       |
|  | Deploy: Own  |  |  | Deploy: Own  | |  | Deploy: Own  |       |
|  | React 18     |  |  | Vue 3        | |  | React 18     |       |
|  +--------------+  |  +--------------+ |  +--------------+       |
+------------------------------------------------------------------+

Each micro-frontend:
  - Has its own repository
  - Has its own CI/CD pipeline
  - Can be deployed independently
  - Is owned by one team
  - Can even use a different framework (but usually does not)
```

---

## Composition Approach 1: Module Federation (Webpack 5)

Module Federation lets independently built and deployed applications share code at runtime. One application can dynamically load components from another application that is running on a different server.

### How Module Federation Works

```
Build Time:
  App A builds and deploys to https://products.example.com
  App B builds and deploys to https://cart.example.com
  Shell builds and deploys to https://www.example.com

Runtime:
  User visits https://www.example.com
  Shell loads
  Shell needs ProductList --> fetches module from products.example.com
  Shell needs CartWidget  --> fetches module from cart.example.com

+-------------------+         +-------------------+
|  Shell App        |         | Products App      |
|  (Host)           |  <---   | (Remote)          |
|                   |  loads  |                   |
|  Uses:            |         |  Exposes:         |
|  - ProductList    |         |  - ProductList    |
|  - CartWidget     |         |  - ProductDetail  |
+-------------------+         +-------------------+
         |
         |  loads
         v
+-------------------+
| Cart App          |
| (Remote)          |
|                   |
|  Exposes:         |
|  - CartWidget     |
|  - CartPage       |
+-------------------+
```

### Setting Up Module Federation

**Remote App (Products Team):**

```js
// products-app/webpack.config.js
const { ModuleFederationPlugin } = require('webpack').container;

module.exports = {
  // ...other webpack config
  plugins: [
    new ModuleFederationPlugin({
      name: 'productsApp',          // Unique name for this app
      filename: 'remoteEntry.js',    // Entry point file for consumers

      // Components this app shares with others
      exposes: {
        './ProductList': './src/components/ProductList',
        './ProductDetail': './src/components/ProductDetail',
      },

      // Shared dependencies (avoid loading React twice)
      shared: {
        react: { singleton: true, requiredVersion: '^18.0.0' },
        'react-dom': { singleton: true, requiredVersion: '^18.0.0' },
      },
    }),
  ],
};
```

```jsx
// products-app/src/components/ProductList.jsx
// This component is developed and tested independently
import { useState, useEffect } from 'react';

export default function ProductList({ onProductClick }) {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    fetch('/api/products')
      .then(res => res.json())
      .then(setProducts);
  }, []);

  return (
    <div className="product-grid">
      {products.map(product => (
        <div
          key={product.id}
          className="product-card"
          onClick={() => onProductClick(product.id)}
        >
          <img src={product.image} alt={product.name} />
          <h3>{product.name}</h3>
          <p>${product.price}</p>
        </div>
      ))}
    </div>
  );
}
```

**Shell App (Host):**

```js
// shell-app/webpack.config.js
const { ModuleFederationPlugin } = require('webpack').container;

module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: 'shell',

      // Remote apps to load from
      remotes: {
        productsApp: 'productsApp@https://products.example.com/remoteEntry.js',
        cartApp: 'cartApp@https://cart.example.com/remoteEntry.js',
      },

      shared: {
        react: { singleton: true, requiredVersion: '^18.0.0' },
        'react-dom': { singleton: true, requiredVersion: '^18.0.0' },
      },
    }),
  ],
};
```

```jsx
// shell-app/src/App.jsx
import React, { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ErrorBoundary } from 'react-error-boundary';
import Header from './components/Header';

// Load components from remote apps at RUNTIME
const ProductList = lazy(() => import('productsApp/ProductList'));
const ProductDetail = lazy(() => import('productsApp/ProductDetail'));
const CartPage = lazy(() => import('cartApp/CartPage'));

function MicroFrontendError({ error, resetErrorBoundary }) {
  return (
    <div className="mfe-error">
      <p>This section is temporarily unavailable.</p>
      <button onClick={resetErrorBoundary}>Retry</button>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Header />
      <main>
        <ErrorBoundary FallbackComponent={MicroFrontendError}>
          <Suspense fallback={<div>Loading...</div>}>
            <Routes>
              <Route path="/" element={<ProductList />} />
              <Route path="/products/:id" element={<ProductDetail />} />
              <Route path="/cart" element={<CartPage />} />
            </Routes>
          </Suspense>
        </ErrorBoundary>
      </main>
    </BrowserRouter>
  );
}

export default App;

// How it works at runtime:
// 1. User visits https://www.example.com/
// 2. Shell app loads (Header + Router)
// 3. Route "/" matches --> React.lazy triggers
// 4. Browser fetches https://products.example.com/remoteEntry.js
// 5. ProductList component loads and renders
// 6. User navigates to /cart
// 7. Browser fetches https://cart.example.com/remoteEntry.js
// 8. CartPage component loads and renders
//
// Products team can deploy new ProductList without touching the shell!
```

---

## Composition Approach 2: Web Components

Web Components are a browser-native way to create custom HTML elements. They work with any framework (or no framework), making them a natural boundary for micro-frontends.

### Creating a Micro-Frontend as a Web Component

```jsx
// search-mfe/src/SearchWidget.jsx
import React, { useState } from 'react';

function SearchWidget() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  async function handleSearch(e) {
    e.preventDefault();
    const res = await fetch(`/api/search?q=${query}`);
    const data = await res.json();
    setResults(data);
  }

  return (
    <div className="search-widget">
      <form onSubmit={handleSearch}>
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Search products..."
        />
        <button type="submit">Search</button>
      </form>
      <ul>
        {results.map(r => (
          <li key={r.id}>{r.name} - ${r.price}</li>
        ))}
      </ul>
    </div>
  );
}
```

```jsx
// search-mfe/src/web-component.jsx
// Wrap the React component as a Web Component
import React from 'react';
import ReactDOM from 'react-dom/client';
import SearchWidget from './SearchWidget';

class SearchWidgetElement extends HTMLElement {
  connectedCallback() {
    // Called when element is added to the DOM
    const mountPoint = document.createElement('div');
    this.attachShadow({ mode: 'open' }).appendChild(mountPoint);

    // Mount React inside the Shadow DOM
    this.root = ReactDOM.createRoot(mountPoint);
    this.root.render(<SearchWidget />);
  }

  disconnectedCallback() {
    // Called when element is removed from the DOM
    this.root.unmount();
  }
}

// Register the custom element
customElements.define('search-widget', SearchWidgetElement);

// Now ANY page can use it:
// <search-widget></search-widget>
// Works in React, Vue, Angular, or plain HTML!
```

### Using Web Component Micro-Frontends

```html
<!-- Shell application (could be plain HTML, React, Vue, anything) -->
<!DOCTYPE html>
<html>
<head>
  <title>Our Store</title>
  <!-- Load micro-frontend scripts -->
  <script src="https://search.example.com/search-widget.js" async></script>
  <script src="https://cart.example.com/cart-icon.js" async></script>
</head>
<body>
  <header>
    <h1>Our Store</h1>
    <!-- Use micro-frontends as custom HTML elements -->
    <search-widget></search-widget>
    <cart-icon user-id="123"></cart-icon>
  </header>
  <main id="content">
    <!-- Main content loaded based on route -->
  </main>
</body>
</html>
```

```
Web Component Isolation:

+----------------------------------------------------------+
|  Host Page DOM                                           |
|  +----------------------------------------------------+  |
|  |  <search-widget>                                   |  |
|  |    #shadow-root (isolates CSS and DOM)              |  |
|  |    +----------------------------------------------+ |  |
|  |    |  React app running inside                    | |  |
|  |    |  Own styles, own state, own lifecycle        | |  |
|  |    |  Cannot be affected by host page CSS         | |  |
|  |    +----------------------------------------------+ |  |
|  +----------------------------------------------------+  |
|                                                          |
|  Host page styles do NOT leak into shadow DOM            |
|  Shadow DOM styles do NOT leak into host page            |
+----------------------------------------------------------+
```

---

## Composition Approach 3: Routing-Based Composition

The simplest approach: different URLs load entirely different applications. A reverse proxy or CDN routes requests to the correct app.

```
Routing-Based Composition:

User visits:                    Served by:
www.example.com/               --> Marketing App (Next.js)
www.example.com/products/*     --> Products App (React)
www.example.com/cart           --> Cart App (React)
www.example.com/account/*      --> Account App (React)
www.example.com/admin/*        --> Admin App (Vue)

+------------------+
|  Reverse Proxy   |     (Nginx, Cloudflare, or CDN)
|  / Load Balancer |
+--------+---------+
         |
    +----+----+----+----+
    |    |    |    |    |
    v    v    v    v    v
  Mktg Prod  Cart Acct Admin
  App  App   App  App  App
```

### Nginx Configuration Example

```nginx
# nginx.conf
server {
    listen 80;
    server_name www.example.com;

    # Marketing pages (Next.js on port 3000)
    location / {
        proxy_pass http://marketing-app:3000;
    }

    # Product catalog (React on port 3001)
    location /products {
        proxy_pass http://products-app:3001;
    }

    # Shopping cart (React on port 3002)
    location /cart {
        proxy_pass http://cart-app:3002;
    }

    # Account management (React on port 3003)
    location /account {
        proxy_pass http://account-app:3003;
    }

    # Admin panel (Vue on port 3004)
    location /admin {
        proxy_pass http://admin-app:3004;
    }
}
```

### Shared Header via Server-Side Includes

```html
<!-- Each micro-frontend includes the shared header -->
<!-- products-app/index.html -->
<!DOCTYPE html>
<html>
<head>
  <title>Products</title>
  <link rel="stylesheet" href="/shared/header.css" />
</head>
<body>
  <!-- Shared header loaded from CDN -->
  <div id="shared-header"></div>
  <script src="https://cdn.example.com/shared-header.js"></script>

  <!-- This app's content -->
  <div id="root"></div>
  <script src="/products-bundle.js"></script>
</body>
</html>
```

---

## Communication Between Micro-Frontends

Micro-frontends need to communicate sometimes. A product being added to the cart needs to update the cart icon. Here are the main patterns:

### Pattern 1: Custom Events

```jsx
// Product MFE: dispatches event when product is added to cart
function ProductCard({ product }) {
  function handleAddToCart() {
    // Add to cart via API
    fetch('/api/cart', {
      method: 'POST',
      body: JSON.stringify({ productId: product.id }),
    });

    // Notify other micro-frontends via custom event
    window.dispatchEvent(
      new CustomEvent('cart:item-added', {
        detail: {
          productId: product.id,
          name: product.name,
          price: product.price,
        },
      })
    );
  }

  return (
    <div className="product-card">
      <h3>{product.name}</h3>
      <button onClick={handleAddToCart}>Add to Cart</button>
    </div>
  );
}

// Cart MFE: listens for cart events
function CartIcon() {
  const [itemCount, setItemCount] = useState(0);

  useEffect(() => {
    function handleItemAdded(event) {
      console.log('Item added:', event.detail.name);
      setItemCount(prev => prev + 1);
    }

    window.addEventListener('cart:item-added', handleItemAdded);
    return () => {
      window.removeEventListener('cart:item-added', handleItemAdded);
    };
  }, []);

  return (
    <div className="cart-icon">
      Cart ({itemCount})
    </div>
  );
}
```

### Pattern 2: Shared State via URL

```jsx
// Search MFE: puts search query in URL
function SearchBar() {
  const [searchParams, setSearchParams] = useSearchParams();
  const query = searchParams.get('q') || '';

  function handleSearch(newQuery) {
    setSearchParams({ q: newQuery });
    // URL changes to /products?q=shoes
    // Product MFE reads the query from URL
  }

  return (
    <input
      value={query}
      onChange={e => handleSearch(e.target.value)}
      placeholder="Search..."
    />
  );
}

// Product MFE: reads search query from URL
function ProductList() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';

  const products = useProducts(query);

  return (
    <div>
      {query && <p>Results for: {query}</p>}
      {products.map(p => <ProductCard key={p.id} product={p} />)}
    </div>
  );
}
```

### Pattern 3: Shared API/Service Layer

```jsx
// shared-services/cart-service.js
// Deployed as a shared npm package or loaded from CDN

class CartService {
  constructor() {
    this.listeners = new Set();
  }

  async addItem(productId) {
    const response = await fetch('/api/cart', {
      method: 'POST',
      body: JSON.stringify({ productId }),
    });
    const cart = await response.json();
    this.notify(cart);
    return cart;
  }

  subscribe(callback) {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  notify(cart) {
    this.listeners.forEach(cb => cb(cart));
  }
}

// Singleton instance shared across micro-frontends
export const cartService = new CartService();

// Product MFE uses it:
import { cartService } from '@shared/cart-service';
function AddToCartButton({ productId }) {
  return (
    <button onClick={() => cartService.addItem(productId)}>
      Add to Cart
    </button>
  );
}

// Cart MFE uses it:
import { cartService } from '@shared/cart-service';
function CartBadge() {
  const [count, setCount] = useState(0);
  useEffect(() => {
    return cartService.subscribe(cart => setCount(cart.items.length));
  }, []);
  return <span className="badge">{count}</span>;
}
```

---

## Trade-Offs: What You Gain and What You Pay

```
+-------------------------------+-------------------------------+
|         GAINS                 |         COSTS                 |
+-------------------------------+-------------------------------+
| Independent deployments       | More infrastructure to manage |
| Team autonomy                 | Cross-team coordination       |
| Smaller, focused codebases    | Duplicated dependencies       |
| Isolated failures             | Harder debugging across MFEs  |
| Tech stack flexibility        | Inconsistent UX if not careful|
| Faster CI/CD per team         | Complex routing and state     |
| Parallel development          | Performance overhead (multiple|
|                               |  frameworks, extra JS loaded) |
| Scale teams independently     | Shared design system needed   |
+-------------------------------+-------------------------------+
```

### The Dependency Duplication Problem

```
Monolith:
  react: loaded ONCE (42 KB)
  react-dom: loaded ONCE (130 KB)
  Total React cost: 172 KB

Naive Micro-Frontends (3 MFEs, each bundles React):
  MFE 1: react + react-dom (172 KB)
  MFE 2: react + react-dom (172 KB)
  MFE 3: react + react-dom (172 KB)
  Total React cost: 516 KB  (3x the monolith!)

Module Federation with shared dependencies:
  Shared: react + react-dom (172 KB, loaded ONCE)
  MFE 1: own code only (50 KB)
  MFE 2: own code only (80 KB)
  MFE 3: own code only (60 KB)
  Total: 362 KB (much better, some overhead remains)
```

### The Consistency Challenge

```
Without a shared design system:

  Search MFE:    [  Search  ]   (blue button, 14px font)
  Product MFE:   [Add to Cart]  (green button, 16px font)
  Cart MFE:      [ Checkout ]   (blue button, 15px font)

  Users notice the inconsistency. It feels broken.

With a shared design system:

  All MFEs import from @company/design-system
  Search MFE:    [  Search  ]   (same button style)
  Product MFE:   [Add to Cart]  (same button style)
  Cart MFE:      [ Checkout ]   (same button style)

  The design system is versioned. Teams can upgrade
  at their own pace, but all buttons look the same.
```

---

## Real-World Use Case: E-Commerce Platform

```
Architecture for a large e-commerce company:

+------------------------------------------------------------------+
|  Shell Application                                               |
|  - Authentication                                                |
|  - Routing                                                       |
|  - Shared Header/Footer                                          |
|  - Design System CSS                                             |
|  - Analytics SDK                                                 |
+------------------------------------------------------------------+
         |              |              |              |
         v              v              v              v
+------------+  +------------+  +------------+  +------------+
| Search MFE |  | Catalog MFE|  | Cart MFE   |  | Account MFE|
|            |  |            |  |            |  |            |
| Features:  |  | Features:  |  | Features:  |  | Features:  |
| - Search   |  | - Browse   |  | - Cart     |  | - Profile  |
| - Autocmpl |  | - Filters  |  | - Checkout |  | - Orders   |
| - Filters  |  | - Detail   |  | - Payment  |  | - Wishlist |
|            |  | - Compare  |  |            |  |            |
| Team: 4 dev|  | Team: 6 dev|  | Team: 5 dev|  | Team: 3 dev|
| Deploy: 5x |  | Deploy: 3x |  | Deploy: 2x |  | Deploy: 1x |
| /day       |  | /day       |  | /day       |  | /week      |
+------------+  +------------+  +------------+  +------------+

Communication:
  Search --> Catalog: URL params (?q=shoes&category=running)
  Catalog --> Cart: Custom Event (cart:item-added)
  Cart --> Account: Shared Auth Token
  All --> Shell: Custom Events for header badge updates
```

```jsx
// shell-app/src/App.jsx
import { lazy, Suspense } from 'react';
import { ErrorBoundary } from 'react-error-boundary';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import SharedHeader from './components/SharedHeader';
import SharedFooter from './components/SharedFooter';
import { AuthProvider } from './auth/AuthProvider';

// Remote micro-frontends via Module Federation
const SearchPage = lazy(() => import('searchApp/SearchPage'));
const CatalogPage = lazy(() => import('catalogApp/CatalogPage'));
const ProductPage = lazy(() => import('catalogApp/ProductPage'));
const CartPage = lazy(() => import('cartApp/CartPage'));
const CheckoutPage = lazy(() => import('cartApp/CheckoutPage'));
const AccountPage = lazy(() => import('accountApp/AccountPage'));

function MFEFallback({ name }) {
  return (
    <div className="mfe-loading">
      <div className="skeleton" />
      <p>Loading {name}...</p>
    </div>
  );
}

function MFEError({ error, resetErrorBoundary }) {
  return (
    <div className="mfe-error">
      <p>This section could not be loaded.</p>
      <button onClick={resetErrorBoundary}>Retry</button>
    </div>
  );
}

function MFEWrapper({ children, name }) {
  return (
    <ErrorBoundary FallbackComponent={MFEError}>
      <Suspense fallback={<MFEFallback name={name} />}>
        {children}
      </Suspense>
    </ErrorBoundary>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <SharedHeader />
        <main>
          <Routes>
            <Route path="/search" element={
              <MFEWrapper name="Search">
                <SearchPage />
              </MFEWrapper>
            } />
            <Route path="/products" element={
              <MFEWrapper name="Catalog">
                <CatalogPage />
              </MFEWrapper>
            } />
            <Route path="/products/:id" element={
              <MFEWrapper name="Product">
                <ProductPage />
              </MFEWrapper>
            } />
            <Route path="/cart" element={
              <MFEWrapper name="Cart">
                <CartPage />
              </MFEWrapper>
            } />
            <Route path="/checkout" element={
              <MFEWrapper name="Checkout">
                <CheckoutPage />
              </MFEWrapper>
            } />
            <Route path="/account/*" element={
              <MFEWrapper name="Account">
                <AccountPage />
              </MFEWrapper>
            } />
          </Routes>
        </main>
        <SharedFooter />
      </BrowserRouter>
    </AuthProvider>
  );
}
```

---

## When to Use / When NOT to Use

### Use Micro-Frontends When

- You have multiple teams (3+) working on the same frontend
- Teams are blocked by each other's deploy schedules
- The monolith codebase has become unmanageable (build times, merge conflicts)
- Different parts of the app have very different release cadences
- Your organization is structured around independent product teams

### Do NOT Use Micro-Frontends When

- You have a small team (under 10 developers)
- A single team maintains the entire frontend
- The application is small or medium-sized
- You do not have the infrastructure to support multiple deploy pipelines
- You are using it because it sounds cool (the most common wrong reason)
- Your team does not have experience managing distributed systems

---

## Common Mistakes

### Mistake 1: Adopting Micro-Frontends Too Early

```
WRONG thinking:
"We have 5 developers and one React app. Let us split it into
 micro-frontends so it scales better."

REALITY:
5 developers do not need micro-frontends. The overhead of managing
multiple repositories, deploy pipelines, shared dependencies, and
cross-app communication far outweighs any benefit.

RULE OF THUMB:
If you have fewer than 3 independent teams with different
release schedules, a well-organized monolith is better.
```

### Mistake 2: No Shared Design System

```
WRONG: Each team builds their own buttons, forms, and layouts.
RESULT: The app looks like a Frankenstein monster of different
        UIs stitched together. Users notice immediately.

RIGHT: Invest in a shared design system (component library)
       that all teams consume via npm.
       @company/design-system provides Button, Input, Modal, etc.
       All micro-frontends use the same visual components.
```

### Mistake 3: Tight Coupling Between Micro-Frontends

```
WRONG: Cart MFE imports a function directly from Product MFE.
       Now they cannot deploy independently.

RIGHT: Micro-frontends communicate through:
       - Custom Events (loose coupling)
       - URL parameters (stateless)
       - Shared services with stable APIs

If you cannot deploy one MFE without deploying another,
you do not have micro-frontends. You have a distributed monolith.
That is the worst of both worlds.
```

---

## Best Practices

1. **Start with a monolith** -- Build your app as a monolith first. Split into micro-frontends only when organizational pain demands it.

2. **Split by business domain** -- Each micro-frontend should own a complete business capability (search, checkout, account), not a technical layer (header, sidebar).

3. **Share a design system** -- Invest in a versioned component library that all teams consume. Visual consistency is non-negotiable.

4. **Use Module Federation for React-to-React** -- When all micro-frontends use React, Module Federation provides the smoothest experience with shared dependencies.

5. **Communicate loosely** -- Use Custom Events, URL params, or a shared event bus. Never import code directly between micro-frontends.

6. **Each MFE must work in isolation** -- Every micro-frontend should be runnable as a standalone app for development and testing.

7. **Monitor bundle sizes** -- Track the total JavaScript loaded. Micro-frontends can accidentally increase the total bundle if shared dependencies are duplicated.

8. **Establish clear contracts** -- Define APIs between micro-frontends (event names, URL param formats) and version them.

---

## Quick Summary

Micro-frontends split a monolithic frontend into independent applications, each owned and deployed by a separate team. The three main composition approaches are Module Federation (Webpack 5 runtime module sharing), Web Components (framework-agnostic custom elements), and routing-based composition (reverse proxy routing to separate apps). Communication between micro-frontends uses Custom Events, URL parameters, or shared services. The pattern provides independent deployments and team autonomy but adds infrastructure complexity, potential dependency duplication, and coordination overhead. Micro-frontends are the right choice for large organizations with multiple independent teams; they are overkill for small teams.

---

## Key Points

- **Micro-frontends** split one big frontend into independently deployable applications.
- **Module Federation** (Webpack 5) shares code between apps at runtime with dependency deduplication.
- **Web Components** provide framework-agnostic composition with Shadow DOM isolation.
- **Routing-based composition** uses a reverse proxy to route URLs to different apps (simplest approach).
- **Communication** between micro-frontends should be loose: Custom Events, URL params, or shared services.
- **Shared design system** is mandatory for visual consistency across teams.
- **Do not adopt too early** -- The overhead is only justified for large organizations with multiple independent teams.
- **Distributed monolith** is worse than a real monolith. If MFEs cannot deploy independently, you have the worst of both worlds.

---

## Practice Questions

1. Your company has 8 frontend developers on one team. The CTO wants to adopt micro-frontends because a competitor uses them. What would you advise, and why?

2. Explain the difference between Module Federation and routing-based micro-frontends. When would you choose one over the other?

3. Two micro-frontends need to share the user's authentication status. Describe three different ways they could communicate this, and which you would recommend.

4. A micro-frontend architecture is loading React three times (once per MFE). How does Module Federation's `shared` configuration solve this, and what is the `singleton` option?

5. Your micro-frontend architecture works well, but users complain that the search page looks different from the product page (different button styles, font sizes). What architectural solution would you implement?

---

## Exercises

### Exercise 1: Module Federation Setup

Create two separate React applications using Webpack 5:
- App A (Host): A shell with navigation
- App B (Remote): A simple widget (counter or todo list)

Configure Module Federation so App A loads the widget from App B at runtime. Verify that you can update App B's widget and see the changes in App A without rebuilding App A.

### Exercise 2: Web Component Wrapper

Take an existing React component and wrap it as a Web Component using `customElements.define`. Verify that it works when inserted into a plain HTML page with no React. Pass attributes to the Web Component and map them to React props.

### Exercise 3: Communication Protocol

Build two micro-frontends on one page (use iframes or Module Federation):
- A "Product Picker" that lets users select products
- A "Cart Summary" that shows selected products

Implement communication between them using Custom Events. Define a clear event contract (event names, payload shapes) and handle cases where one MFE loads before the other.

---

## What Is Next?

You now understand patterns from individual components to entire application architectures. In Chapter 31, we bring everything together in a **Project Pattern Library** -- a complete React application that applies 10+ design patterns from this book, showing how they work in concert in a real codebase.
