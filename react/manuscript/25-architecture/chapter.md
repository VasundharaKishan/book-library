# Chapter 25: React App Architecture and Folder Structure

## Learning Goals

By the end of this chapter, you will be able to:

- Organize a React project with a scalable folder structure
- Choose between flat, layer-based, and feature-based architectures
- Separate concerns effectively across components, hooks, services, and utilities
- Implement the barrel export pattern for clean imports
- Structure shared and feature-specific code
- Apply naming conventions consistently across a codebase
- Recognize when to restructure and how to migrate incrementally
- Set up path aliases for cleaner import paths

---

## Why Architecture Matters

When you first create a React app with Vite, you get a minimal structure:

```
my-app/
├── public/
├── src/
│   ├── App.jsx
│   ├── App.css
│   └── main.jsx
├── index.html
├── package.json
└── vite.config.js
```

This works beautifully for small projects. But as your application grows to 50, 100, or 200+ files, the flat `src/` directory becomes chaotic. You waste time searching for files. Teammates conflict on where to put things. Code duplication creeps in because nobody realized a utility already existed.

Architecture is not about following a trendy folder structure. It is about establishing conventions that make your codebase predictable. When any developer on your team needs to find, add, or modify code, they should know exactly where to look.

Good architecture provides three things:

1. **Discoverability** — can you find a file without searching?
2. **Scalability** — does the structure still work with 10x more files?
3. **Separation of concerns** — is business logic separate from UI logic?

There is no single "correct" architecture for React. The best structure depends on your project size, team size, and complexity. In this chapter, we will explore the most common patterns and help you choose the right one.

---

## The Flat Structure: Where Everyone Starts

Most projects begin with files organized by type in a flat structure:

```
src/
├── components/
│   ├── Button.jsx
│   ├── Header.jsx
│   ├── Footer.jsx
│   ├── Sidebar.jsx
│   ├── LoginForm.jsx
│   ├── RegisterForm.jsx
│   ├── ProductCard.jsx
│   ├── ProductList.jsx
│   ├── CartItem.jsx
│   ├── CartSummary.jsx
│   ├── UserProfile.jsx
│   └── UserAvatar.jsx
├── hooks/
│   ├── useAuth.js
│   ├── useCart.js
│   ├── useProducts.js
│   └── useLocalStorage.js
├── utils/
│   ├── formatCurrency.js
│   ├── validateEmail.js
│   └── api.js
├── App.jsx
└── main.jsx
```

**When this works:** Projects with fewer than 20-30 components. Solo developers or small teams. Prototypes and MVPs.

**When this breaks:** Look at the `components/` folder. It contains UI components (Button, Header), feature components (LoginForm, ProductCard), and layout components (Sidebar, Footer) all mixed together. With 12 files, you can still scan the list. With 60 files, it becomes unmanageable.

The flat structure breaks down because it groups by *what things are* (components, hooks, utils) rather than *what they do* (authentication, products, cart).

---

## The Layer-Based Structure

The layer-based structure (sometimes called "type-based" or "role-based") takes the flat approach and adds more layers:

```
src/
├── components/
│   ├── common/
│   │   ├── Button.jsx
│   │   ├── Input.jsx
│   │   ├── Modal.jsx
│   │   └── Spinner.jsx
│   ├── layout/
│   │   ├── Header.jsx
│   │   ├── Footer.jsx
│   │   ├── Sidebar.jsx
│   │   └── PageLayout.jsx
│   └── forms/
│       ├── LoginForm.jsx
│       ├── RegisterForm.jsx
│       └── SearchForm.jsx
├── hooks/
│   ├── useAuth.js
│   ├── useCart.js
│   ├── useProducts.js
│   ├── useDebounce.js
│   └── useLocalStorage.js
├── services/
│   ├── authService.js
│   ├── productService.js
│   └── cartService.js
├── context/
│   ├── AuthContext.jsx
│   ├── CartContext.jsx
│   └── ThemeContext.jsx
├── utils/
│   ├── formatCurrency.js
│   ├── validateEmail.js
│   ├── constants.js
│   └── helpers.js
├── pages/
│   ├── HomePage.jsx
│   ├── ProductPage.jsx
│   ├── CartPage.jsx
│   ├── LoginPage.jsx
│   └── ProfilePage.jsx
├── assets/
│   ├── images/
│   └── styles/
├── App.jsx
└── main.jsx
```

This is better. Common components are separated from feature components. Services handle API calls. Context providers have their own directory. Pages represent route-level components.

**When this works:** Small to medium projects (30-80 components). Teams of 2-4 developers. Applications with moderate complexity.

**When this breaks:** To understand the authentication feature, you need to look in five different directories: `pages/LoginPage.jsx`, `components/forms/LoginForm.jsx`, `hooks/useAuth.js`, `services/authService.js`, and `context/AuthContext.jsx`. Related code is scattered across the entire project. When you want to remove a feature, you must hunt through every layer to find all its pieces.

---

## The Feature-Based Structure

The feature-based structure (also called "domain-based" or "module-based") groups code by what it does rather than what it is:

```
src/
├── features/
│   ├── auth/
│   │   ├── components/
│   │   │   ├── LoginForm.jsx
│   │   │   ├── RegisterForm.jsx
│   │   │   └── ProtectedRoute.jsx
│   │   ├── hooks/
│   │   │   └── useAuth.js
│   │   ├── services/
│   │   │   └── authService.js
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   └── index.js
│   ├── products/
│   │   ├── components/
│   │   │   ├── ProductCard.jsx
│   │   │   ├── ProductList.jsx
│   │   │   ├── ProductDetail.jsx
│   │   │   └── ProductFilters.jsx
│   │   ├── hooks/
│   │   │   ├── useProducts.js
│   │   │   └── useProductSearch.js
│   │   ├── services/
│   │   │   └── productService.js
│   │   └── index.js
│   └── cart/
│       ├── components/
│       │   ├── CartItem.jsx
│       │   ├── CartSummary.jsx
│       │   └── CartIcon.jsx
│       ├── hooks/
│       │   └── useCart.js
│       ├── services/
│       │   └── cartService.js
│       ├── context/
│       │   └── CartContext.jsx
│       └── index.js
├── shared/
│   ├── components/
│   │   ├── Button.jsx
│   │   ├── Input.jsx
│   │   ├── Modal.jsx
│   │   └── Spinner.jsx
│   ├── hooks/
│   │   ├── useDebounce.js
│   │   ├── useLocalStorage.js
│   │   └── useMediaQuery.js
│   ├── utils/
│   │   ├── formatCurrency.js
│   │   ├── validateEmail.js
│   │   └── constants.js
│   └── layouts/
│       ├── Header.jsx
│       ├── Footer.jsx
│       ├── Sidebar.jsx
│       └── PageLayout.jsx
├── pages/
│   ├── HomePage.jsx
│   ├── ProductPage.jsx
│   ├── CartPage.jsx
│   ├── LoginPage.jsx
│   └── ProfilePage.jsx
├── App.jsx
└── main.jsx
```

Now everything related to authentication lives in `features/auth/`. If you need to modify the login flow, you know exactly where to look. If you decide to remove the cart feature entirely, you delete one directory and clean up the imports.

**When this works:** Medium to large projects (50+ components). Teams of 3+ developers. Applications with clearly separable features.

**When this breaks:** It can feel like overkill for small projects. And sometimes features share so much code that the boundaries become blurry. Should a "product review" component live in `features/products/` or `features/reviews/`?

---

## The Recommended Hybrid Approach

In practice, the most effective architecture combines elements from both approaches. Here is the structure we recommend for most React applications:

```
src/
├── app/
│   ├── App.jsx
│   ├── AppProviders.jsx
│   └── routes.jsx
├── features/
│   ├── auth/
│   ├── products/
│   ├── cart/
│   └── orders/
├── shared/
│   ├── components/
│   ├── hooks/
│   ├── utils/
│   ├── services/
│   └── constants/
├── pages/
├── assets/
│   ├── images/
│   ├── fonts/
│   └── styles/
└── main.jsx
```

Let us build this out piece by piece.

### The `app/` Directory

This contains your application shell — the entry point, global providers, and route configuration:

```jsx
// src/app/AppProviders.jsx
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../features/auth';
import { CartProvider } from '../features/cart';
import { ThemeProvider } from '../shared/context/ThemeContext';
import { ErrorBoundary } from '../shared/components/ErrorBoundary';

export function AppProviders({ children }) {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <ThemeProvider>
          <AuthProvider>
            <CartProvider>
              {children}
            </CartProvider>
          </AuthProvider>
        </ThemeProvider>
      </BrowserRouter>
    </ErrorBoundary>
  );
}
```

```jsx
// src/app/routes.jsx
import { Routes, Route } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import { ProtectedRoute } from '../features/auth';
import { PageLayout } from '../shared/layouts/PageLayout';
import { Spinner } from '../shared/components/Spinner';

const HomePage = lazy(() => import('../pages/HomePage'));
const ProductPage = lazy(() => import('../pages/ProductPage'));
const CartPage = lazy(() => import('../pages/CartPage'));
const LoginPage = lazy(() => import('../pages/LoginPage'));
const ProfilePage = lazy(() => import('../pages/ProfilePage'));

export function AppRoutes() {
  return (
    <Suspense fallback={<Spinner />}>
      <Routes>
        <Route element={<PageLayout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/products/:id" element={<ProductPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/cart"
            element={
              <ProtectedRoute>
                <CartPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            }
          />
        </Route>
      </Routes>
    </Suspense>
  );
}
```

```jsx
// src/app/App.jsx
import { AppProviders } from './AppProviders';
import { AppRoutes } from './routes';

export default function App() {
  return (
    <AppProviders>
      <AppRoutes />
    </AppProviders>
  );
}
```

### The `features/` Directory

Each feature is a self-contained module with its own components, hooks, services, and public API:

```
src/features/auth/
├── components/
│   ├── LoginForm.jsx
│   ├── LoginForm.module.css
│   ├── RegisterForm.jsx
│   ├── RegisterForm.module.css
│   ├── ProtectedRoute.jsx
│   └── AuthStatus.jsx
├── hooks/
│   ├── useAuth.js
│   └── usePermissions.js
├── services/
│   └── authService.js
├── context/
│   └── AuthContext.jsx
├── utils/
│   └── tokenHelpers.js
└── index.js
```

The key insight is the `index.js` file. It defines the feature's **public API** — the parts that other features and pages are allowed to import:

```jsx
// src/features/auth/index.js

// Components
export { LoginForm } from './components/LoginForm';
export { RegisterForm } from './components/RegisterForm';
export { ProtectedRoute } from './components/ProtectedRoute';
export { AuthStatus } from './components/AuthStatus';

// Hooks
export { useAuth } from './hooks/useAuth';
export { usePermissions } from './hooks/usePermissions';

// Context Provider
export { AuthProvider } from './context/AuthContext';
```

Notice that `tokenHelpers.js` and `authService.js` are not exported. They are internal to the feature. Other parts of the application should not import them directly.

This creates a clear contract:

```jsx
// Good — importing from the public API
import { useAuth, ProtectedRoute } from '../features/auth';

// Bad — reaching into internal implementation
import { authService } from '../features/auth/services/authService';
```

### The `shared/` Directory

Shared code is anything used by multiple features:

```
src/shared/
├── components/
│   ├── Button/
│   │   ├── Button.jsx
│   │   ├── Button.module.css
│   │   ├── Button.test.jsx
│   │   └── index.js
│   ├── Input/
│   │   ├── Input.jsx
│   │   ├── Input.module.css
│   │   └── index.js
│   ├── Modal/
│   │   ├── Modal.jsx
│   │   ├── Modal.module.css
│   │   └── index.js
│   ├── Spinner/
│   │   ├── Spinner.jsx
│   │   └── index.js
│   ├── ErrorBoundary/
│   │   ├── ErrorBoundary.jsx
│   │   └── index.js
│   └── index.js
├── hooks/
│   ├── useDebounce.js
│   ├── useLocalStorage.js
│   ├── useMediaQuery.js
│   └── index.js
├── utils/
│   ├── formatCurrency.js
│   ├── formatDate.js
│   ├── validation.js
│   └── index.js
├── services/
│   ├── apiClient.js
│   └── index.js
├── constants/
│   ├── routes.js
│   ├── queryKeys.js
│   └── index.js
├── context/
│   ├── ThemeContext.jsx
│   └── index.js
└── layouts/
    ├── PageLayout.jsx
    ├── AuthLayout.jsx
    └── index.js
```

Each subdirectory in `shared/` has its own `index.js` for barrel exports:

```jsx
// src/shared/components/index.js
export { Button } from './Button';
export { Input } from './Input';
export { Modal } from './Modal';
export { Spinner } from './Spinner';
export { ErrorBoundary } from './ErrorBoundary';
```

```jsx
// src/shared/hooks/index.js
export { useDebounce } from './useDebounce';
export { useLocalStorage } from './useLocalStorage';
export { useMediaQuery } from './useMediaQuery';
```

### The `pages/` Directory

Pages are thin components that compose features together. They should contain minimal logic:

```jsx
// src/pages/ProductPage.jsx
import { useParams } from 'react-router-dom';
import { ProductDetail, ProductReviews } from '../features/products';
import { AddToCartButton } from '../features/cart';
import { useAuth } from '../features/auth';

export default function ProductPage() {
  const { id } = useParams();
  const { user } = useAuth();

  return (
    <div>
      <ProductDetail productId={id} />
      {user && <AddToCartButton productId={id} />}
      <ProductReviews productId={id} />
    </div>
  );
}
```

Notice how the page itself has no business logic. It does not fetch data, manage state, or handle complex interactions. It simply composes features together. This keeps pages easy to understand and modify.

---

## Component Organization Patterns

As individual components grow, you need a strategy for organizing their associated files.

### Single-File Components

For simple components, a single file is sufficient:

```
shared/components/Spinner.jsx
```

### Component Folders

When a component has styles, tests, or sub-components, use a folder:

```
shared/components/Button/
├── Button.jsx          // Main component
├── Button.module.css   // Styles
├── Button.test.jsx     // Tests
├── ButtonGroup.jsx     // Related sub-component
└── index.js            // Re-export
```

The `index.js` keeps imports clean:

```jsx
// src/shared/components/Button/index.js
export { Button } from './Button';
export { ButtonGroup } from './ButtonGroup';
```

```jsx
// Now you can import like this:
import { Button, ButtonGroup } from '../shared/components/Button';

// Instead of:
import { Button } from '../shared/components/Button/Button';
```

### When to Create a Component Folder

Use a simple rule:

- **Single file** — component with no styles, tests, or sub-components
- **Folder** — component with any associated files (styles, tests, types, sub-components)

Do not create folders preemptively. Start with a single file and promote to a folder when needed.

---

## The Barrel Export Pattern

Barrel exports (index.js files that re-export from other files) are a powerful organization tool, but they require care.

### How Barrel Exports Work

```jsx
// src/shared/utils/index.js
export { formatCurrency } from './formatCurrency';
export { formatDate } from './formatDate';
export { validateEmail, validatePassword } from './validation';
```

This lets consumers import from the directory:

```jsx
// Clean import from barrel
import { formatCurrency, formatDate } from '../shared/utils';

// Without barrel, you need separate imports
import { formatCurrency } from '../shared/utils/formatCurrency';
import { formatDate } from '../shared/utils/formatDate';
```

### Barrel Export Guidelines

**Do use barrels for:**
- Feature public APIs (`features/auth/index.js`)
- Shared directories (`shared/components/index.js`)
- Component folders (`Button/index.js`)

**Be cautious with:**
- Deep nesting of barrels (barrels importing from barrels)
- Very large barrels (50+ exports) — this can hurt tree-shaking

**Avoid:**
- Re-exporting everything with `export *` — it makes it hard to track what comes from where

```jsx
// Prefer named re-exports
export { Button } from './Button';
export { Input } from './Input';

// Avoid wildcard re-exports
export * from './Button';
export * from './Input';
```

Named re-exports make it explicit what each module provides. When something breaks, you can trace the export chain easily.

---

## Separation of Concerns

A well-architected React app separates code into clear layers. Let us look at each layer and its responsibilities.

### UI Components (Presentation)

UI components receive data via props and render it. They do not fetch data or manage complex state:

```jsx
// src/features/products/components/ProductCard.jsx
import styles from './ProductCard.module.css';

export function ProductCard({ product, onAddToCart }) {
  return (
    <article className={styles.card}>
      <img
        src={product.image}
        alt={product.name}
        className={styles.image}
      />
      <div className={styles.content}>
        <h3 className={styles.name}>{product.name}</h3>
        <p className={styles.price}>
          ${product.price.toFixed(2)}
        </p>
        <button
          onClick={() => onAddToCart(product.id)}
          className={styles.button}
        >
          Add to Cart
        </button>
      </div>
    </article>
  );
}
```

### Container Components (Logic)

Container components handle data fetching, state management, and pass data down to presentation components:

```jsx
// src/features/products/components/ProductList.jsx
import { useProducts } from '../hooks/useProducts';
import { useCart } from '../../cart/hooks/useCart';
import { ProductCard } from './ProductCard';
import { Spinner } from '../../../shared/components/Spinner';
import { ErrorMessage } from '../../../shared/components/ErrorMessage';

export function ProductList({ category }) {
  const { products, loading, error } = useProducts(category);
  const { addItem } = useCart();

  if (loading) return <Spinner />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div className="product-grid">
      {products.map(product => (
        <ProductCard
          key={product.id}
          product={product}
          onAddToCart={addItem}
        />
      ))}
    </div>
  );
}
```

### Custom Hooks (State and Logic)

Custom hooks encapsulate state management and business logic:

```jsx
// src/features/products/hooks/useProducts.js
import { useState, useEffect } from 'react';
import { productService } from '../services/productService';

export function useProducts(category) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const controller = new AbortController();

    async function fetchProducts() {
      try {
        setLoading(true);
        setError(null);
        const data = await productService.getByCategory(
          category,
          controller.signal
        );
        setProducts(data);
      } catch (err) {
        if (err.name !== 'AbortError') {
          setError(err.message);
        }
      } finally {
        setLoading(false);
      }
    }

    fetchProducts();
    return () => controller.abort();
  }, [category]);

  return { products, loading, error };
}
```

### Services (API Layer)

Services handle communication with external APIs. They know nothing about React:

```jsx
// src/features/products/services/productService.js
import { apiClient } from '../../../shared/services/apiClient';

export const productService = {
  async getAll(signal) {
    return apiClient.get('/products', { signal });
  },

  async getById(id, signal) {
    return apiClient.get(`/products/${id}`, { signal });
  },

  async getByCategory(category, signal) {
    const params = category ? `?category=${category}` : '';
    return apiClient.get(`/products${params}`, { signal });
  },

  async create(productData) {
    return apiClient.post('/products', productData);
  },

  async update(id, productData) {
    return apiClient.put(`/products/${id}`, productData);
  },

  async delete(id) {
    return apiClient.delete(`/products/${id}`);
  },
};
```

### The Shared API Client

A centralized API client handles common concerns like base URL, headers, and error handling:

```jsx
// src/shared/services/apiClient.js
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api';

class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

async function handleResponse(response) {
  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new ApiError(
      data?.message || `HTTP ${response.status}`,
      response.status,
      data
    );
  }

  return data;
}

function getHeaders() {
  const headers = {
    'Content-Type': 'application/json',
  };

  const token = localStorage.getItem('token');
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  return headers;
}

export const apiClient = {
  async get(endpoint, options = {}) {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      headers: getHeaders(),
      signal: options.signal,
    });
    return handleResponse(response);
  },

  async post(endpoint, body) {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(body),
    });
    return handleResponse(response);
  },

  async put(endpoint, body) {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify(body),
    });
    return handleResponse(response);
  },

  async delete(endpoint) {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    return handleResponse(response);
  },
};
```

### Utilities (Pure Functions)

Utilities are pure functions with no dependencies on React or your application state:

```jsx
// src/shared/utils/formatCurrency.js
export function formatCurrency(amount, currency = 'USD') {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount);
}
```

```jsx
// src/shared/utils/formatDate.js
export function formatDate(dateString, options = {}) {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    ...options,
  }).format(date);
}

export function timeAgo(dateString) {
  const seconds = Math.floor(
    (Date.now() - new Date(dateString).getTime()) / 1000
  );

  const intervals = [
    { label: 'year', seconds: 31536000 },
    { label: 'month', seconds: 2592000 },
    { label: 'week', seconds: 604800 },
    { label: 'day', seconds: 86400 },
    { label: 'hour', seconds: 3600 },
    { label: 'minute', seconds: 60 },
  ];

  for (const interval of intervals) {
    const count = Math.floor(seconds / interval.seconds);
    if (count >= 1) {
      return `${count} ${interval.label}${count > 1 ? 's' : ''} ago`;
    }
  }

  return 'just now';
}
```

### Constants

Constants keep magic strings and numbers organized:

```jsx
// src/shared/constants/routes.js
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  PRODUCTS: '/products',
  PRODUCT_DETAIL: '/products/:id',
  CART: '/cart',
  CHECKOUT: '/checkout',
  PROFILE: '/profile',
  ADMIN: '/admin',
};
```

```jsx
// src/shared/constants/queryKeys.js
export const QUERY_KEYS = {
  PRODUCTS: 'products',
  PRODUCT_DETAIL: 'product-detail',
  CART: 'cart',
  USER: 'user',
  ORDERS: 'orders',
};
```

---

## Path Aliases

As your project grows, relative imports become unwieldy:

```jsx
// Deep relative imports are hard to read and fragile
import { Button } from '../../../../shared/components/Button';
import { useAuth } from '../../../features/auth/hooks/useAuth';
```

Path aliases solve this problem. Configure them in `vite.config.js`:

```jsx
// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@features': path.resolve(__dirname, './src/features'),
      '@shared': path.resolve(__dirname, './src/shared'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@assets': path.resolve(__dirname, './src/assets'),
    },
  },
});
```

Now imports become clean and absolute:

```jsx
import { Button } from '@shared/components';
import { useAuth } from '@features/auth';
import { formatCurrency } from '@shared/utils';
```

If you use VS Code, add a `jsconfig.json` for autocomplete support:

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@features/*": ["src/features/*"],
      "@shared/*": ["src/shared/*"],
      "@pages/*": ["src/pages/*"],
      "@assets/*": ["src/assets/*"]
    }
  }
}
```

---

## Naming Conventions

Consistent naming removes decision fatigue and makes the codebase scannable.

### File Naming

```
Components:     PascalCase.jsx     →  ProductCard.jsx
Hooks:          camelCase.js       →  useProducts.js
Services:       camelCase.js       →  productService.js
Utilities:      camelCase.js       →  formatCurrency.js
Constants:      camelCase.js       →  routes.js
Styles:         PascalCase.module.css  →  ProductCard.module.css
Tests:          PascalCase.test.jsx    →  ProductCard.test.jsx
```

### Component Naming

Name components after what they render, not what they do:

```jsx
// Good — describes what it renders
function ProductCard({ product }) { ... }
function UserAvatar({ user }) { ... }
function OrderSummary({ order }) { ... }

// Bad — vague or action-based names
function Card({ data }) { ... }
function Display({ info }) { ... }
function Handler({ item }) { ... }
```

### Hook Naming

Hooks always start with `use` and describe what they provide:

```jsx
// Good — clear purpose
function useProducts(category) { ... }
function useAuth() { ... }
function useDebounce(value, delay) { ... }
function useLocalStorage(key, initialValue) { ... }

// Bad — vague or misleading
function useData() { ... }       // What data?
function useStuff() { ... }      // What stuff?
function useHandler() { ... }    // What does it handle?
```

### Service Naming

Services describe the resource they manage:

```jsx
// Good — resource-based
const productService = { ... };
const authService = { ... };
const orderService = { ... };

// Bad — generic
const api = { ... };
const service = { ... };
const helper = { ... };
```

### Directory Naming

Use lowercase with hyphens for multi-word directories:

```
features/user-profile/
features/order-history/
shared/components/date-picker/
```

Some teams prefer camelCase directories. Either is fine — just be consistent.

---

## Feature Boundaries and Dependencies

A critical aspect of feature-based architecture is managing dependencies between features.

### The Dependency Rule

Features should be as independent as possible. Here is the dependency hierarchy:

```
pages/ → can import from features/ and shared/
features/ → can import from shared/ and other features (carefully)
shared/ → can only import from other shared/ modules
```

### Cross-Feature Communication

When features need to interact, avoid importing internal implementation details. Instead, use one of these patterns:

**Pattern 1: Import from Public API**

```jsx
// features/cart/components/AddToCartButton.jsx
import { useAuth } from '@features/auth';  // Using public API

export function AddToCartButton({ productId }) {
  const { user } = useAuth();

  if (!user) {
    return <p>Please log in to add items to cart</p>;
  }

  return <button onClick={() => addToCart(productId)}>Add to Cart</button>;
}
```

**Pattern 2: Props and Composition**

Instead of features importing from each other, let pages compose them:

```jsx
// pages/ProductPage.jsx
import { ProductDetail } from '@features/products';
import { AddToCartButton } from '@features/cart';
import { ReviewSection } from '@features/reviews';

export default function ProductPage() {
  const { id } = useParams();

  return (
    <div>
      <ProductDetail
        productId={id}
        renderActions={(product) => (
          <AddToCartButton product={product} />
        )}
      />
      <ReviewSection productId={id} />
    </div>
  );
}
```

**Pattern 3: Shared Context or Event Bus**

For truly decoupled communication, use context or events:

```jsx
// shared/context/NotificationContext.jsx
import { createContext, useContext, useState, useCallback } from 'react';

const NotificationContext = createContext(null);

export function NotificationProvider({ children }) {
  const [notifications, setNotifications] = useState([]);

  const addNotification = useCallback((message, type = 'info') => {
    const id = Date.now();
    setNotifications(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 5000);
  }, []);

  return (
    <NotificationContext.Provider value={{ notifications, addNotification }}>
      {children}
    </NotificationContext.Provider>
  );
}

export function useNotification() {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification must be used within NotificationProvider');
  }
  return context;
}
```

Now any feature can show notifications without knowing about other features:

```jsx
// features/cart/hooks/useCart.js
import { useNotification } from '@shared/context/NotificationContext';

export function useCart() {
  const { addNotification } = useNotification();

  const addItem = async (productId) => {
    await cartService.addItem(productId);
    addNotification('Item added to cart!', 'success');
  };

  return { addItem };
}
```

---

## Scaling Patterns

As your application grows, you will encounter common scaling challenges. Here are patterns to handle them.

### Shared Component Library

When shared components multiply, organize them by category:

```
shared/components/
├── data-display/
│   ├── Table/
│   ├── Card/
│   ├── Badge/
│   ├── Avatar/
│   └── index.js
├── feedback/
│   ├── Spinner/
│   ├── Alert/
│   ├── Toast/
│   ├── Progress/
│   └── index.js
├── forms/
│   ├── Input/
│   ├── Select/
│   ├── Checkbox/
│   ├── Radio/
│   ├── TextArea/
│   └── index.js
├── layout/
│   ├── Stack/
│   ├── Grid/
│   ├── Container/
│   ├── Divider/
│   └── index.js
├── navigation/
│   ├── Tabs/
│   ├── Breadcrumb/
│   ├── Pagination/
│   └── index.js
└── overlay/
    ├── Modal/
    ├── Dropdown/
    ├── Tooltip/
    └── index.js
```

### Feature Submodules

When a feature grows very large, split it into submodules:

```
features/products/
├── catalog/
│   ├── components/
│   ├── hooks/
│   └── index.js
├── search/
│   ├── components/
│   ├── hooks/
│   └── index.js
├── reviews/
│   ├── components/
│   ├── hooks/
│   └── index.js
├── shared/
│   ├── services/
│   ├── utils/
│   └── types/
└── index.js
```

### Configuration Management

Keep configuration centralized:

```jsx
// src/shared/config/index.js
export const config = {
  api: {
    baseUrl: import.meta.env.VITE_API_URL || 'http://localhost:3001/api',
    timeout: 10000,
  },
  auth: {
    tokenKey: 'auth_token',
    refreshKey: 'refresh_token',
  },
  pagination: {
    defaultPageSize: 20,
    maxPageSize: 100,
  },
  features: {
    enableDarkMode: true,
    enableNotifications: true,
    enableAnalytics: import.meta.env.PROD,
  },
};
```

---

## When and How to Restructure

### Signs You Need to Restructure

1. **You cannot find files** — developers waste time searching for components
2. **Features are tangled** — changing one feature breaks another unexpectedly
3. **Circular dependencies** — module A imports from B which imports from A
4. **Huge directories** — a single folder has 30+ files
5. **Inconsistent patterns** — similar features are organized differently
6. **Duplicate code** — the same utility exists in multiple places

### How to Restructure Incrementally

Never do a big-bang restructure. Instead, migrate one feature at a time:

**Step 1: Create the new structure alongside the old one**

```
src/
├── components/          ← Old flat structure (still works)
├── features/            ← New feature structure
│   └── auth/            ← Start with one feature
│       ├── components/
│       ├── hooks/
│       ├── services/
│       └── index.js
├── shared/              ← Move shared code here
└── ...
```

**Step 2: Move one feature at a time**

```bash
# Move auth-related files to the new feature directory
# Update imports in all files that reference them
# Run tests to verify nothing broke
# Commit the changes
```

**Step 3: Update imports gradually**

If you have path aliases set up, updating imports is straightforward. Without aliases, use your IDE's "Find and Replace" to update import paths.

**Step 4: Delete the old directories when they are empty**

Only remove old directories once all their contents have been migrated.

### A Practical Migration Script

You can use a checklist approach:

```
Migration Checklist: Authentication Feature
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[x] Create features/auth/ directory structure
[x] Move LoginForm.jsx → features/auth/components/
[x] Move RegisterForm.jsx → features/auth/components/
[x] Move ProtectedRoute.jsx → features/auth/components/
[x] Move useAuth.js → features/auth/hooks/
[x] Move authService.js → features/auth/services/
[x] Move AuthContext.jsx → features/auth/context/
[x] Create features/auth/index.js barrel export
[x] Update all import paths across the project
[x] Run full test suite
[x] Delete old files from components/ and hooks/
```

---

## Real-World Architecture Example

Let us put everything together with a complete e-commerce application structure:

```
src/
├── app/
│   ├── App.jsx
│   ├── AppProviders.jsx
│   └── routes.jsx
│
├── features/
│   ├── auth/
│   │   ├── components/
│   │   │   ├── LoginForm.jsx
│   │   │   ├── RegisterForm.jsx
│   │   │   ├── ProtectedRoute.jsx
│   │   │   ├── RoleGuard.jsx
│   │   │   └── AuthStatus.jsx
│   │   ├── hooks/
│   │   │   ├── useAuth.js
│   │   │   └── usePermissions.js
│   │   ├── services/
│   │   │   └── authService.js
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   ├── utils/
│   │   │   └── tokenHelpers.js
│   │   └── index.js
│   │
│   ├── products/
│   │   ├── components/
│   │   │   ├── ProductCard.jsx
│   │   │   ├── ProductCard.module.css
│   │   │   ├── ProductList.jsx
│   │   │   ├── ProductDetail.jsx
│   │   │   ├── ProductFilters.jsx
│   │   │   └── ProductSearch.jsx
│   │   ├── hooks/
│   │   │   ├── useProducts.js
│   │   │   ├── useProduct.js
│   │   │   └── useProductSearch.js
│   │   ├── services/
│   │   │   └── productService.js
│   │   └── index.js
│   │
│   ├── cart/
│   │   ├── components/
│   │   │   ├── CartItem.jsx
│   │   │   ├── CartSummary.jsx
│   │   │   ├── CartIcon.jsx
│   │   │   └── CartDrawer.jsx
│   │   ├── hooks/
│   │   │   └── useCart.js
│   │   ├── services/
│   │   │   └── cartService.js
│   │   ├── context/
│   │   │   └── CartContext.jsx
│   │   └── index.js
│   │
│   ├── checkout/
│   │   ├── components/
│   │   │   ├── CheckoutForm.jsx
│   │   │   ├── ShippingForm.jsx
│   │   │   ├── PaymentForm.jsx
│   │   │   ├── OrderConfirmation.jsx
│   │   │   └── CheckoutStepper.jsx
│   │   ├── hooks/
│   │   │   └── useCheckout.js
│   │   ├── services/
│   │   │   └── checkoutService.js
│   │   └── index.js
│   │
│   └── orders/
│       ├── components/
│       │   ├── OrderList.jsx
│       │   ├── OrderDetail.jsx
│       │   └── OrderStatus.jsx
│       ├── hooks/
│       │   ├── useOrders.js
│       │   └── useOrder.js
│       ├── services/
│       │   └── orderService.js
│       └── index.js
│
├── shared/
│   ├── components/
│   │   ├── Button/
│   │   │   ├── Button.jsx
│   │   │   ├── Button.module.css
│   │   │   └── index.js
│   │   ├── Input/
│   │   ├── Modal/
│   │   ├── Spinner/
│   │   ├── ErrorBoundary/
│   │   ├── ErrorMessage/
│   │   ├── EmptyState/
│   │   └── index.js
│   ├── hooks/
│   │   ├── useDebounce.js
│   │   ├── useLocalStorage.js
│   │   ├── useMediaQuery.js
│   │   ├── useIntersectionObserver.js
│   │   └── index.js
│   ├── utils/
│   │   ├── formatCurrency.js
│   │   ├── formatDate.js
│   │   ├── validation.js
│   │   ├── cn.js
│   │   └── index.js
│   ├── services/
│   │   ├── apiClient.js
│   │   └── index.js
│   ├── constants/
│   │   ├── routes.js
│   │   └── index.js
│   ├── context/
│   │   ├── ThemeContext.jsx
│   │   ├── NotificationContext.jsx
│   │   └── index.js
│   └── layouts/
│       ├── PageLayout.jsx
│       ├── AuthLayout.jsx
│       ├── AdminLayout.jsx
│       └── index.js
│
├── pages/
│   ├── HomePage.jsx
│   ├── ProductsPage.jsx
│   ├── ProductDetailPage.jsx
│   ├── CartPage.jsx
│   ├── CheckoutPage.jsx
│   ├── OrdersPage.jsx
│   ├── OrderDetailPage.jsx
│   ├── LoginPage.jsx
│   ├── RegisterPage.jsx
│   ├── ProfilePage.jsx
│   └── NotFoundPage.jsx
│
├── assets/
│   ├── images/
│   ├── fonts/
│   └── styles/
│       └── global.css
│
└── main.jsx
```

---

## Common Mistakes

### Mistake 1: Over-Engineering Early

```
// Don't create this structure for a 3-page app:
src/
├── features/
│   └── todos/
│       ├── components/
│       │   └── TodoItem.jsx    ← Only file in the folder
│       ├── hooks/
│       │   └── useTodos.js     ← Only file in the folder
│       ├── services/
│       │   └── todoService.js  ← Only file in the folder
│       └── index.js
```

Start simple. A flat structure is perfectly fine until you have 20-30 files. Restructure when you feel pain, not before.

### Mistake 2: Circular Dependencies

```jsx
// features/auth/hooks/useAuth.js
import { useCart } from '../../cart/hooks/useCart';  // Auth depends on Cart

// features/cart/hooks/useCart.js
import { useAuth } from '../../auth/hooks/useAuth';  // Cart depends on Auth
```

If feature A imports from feature B and feature B imports from feature A, you have a circular dependency. Fix it by extracting the shared logic into `shared/` or restructuring the dependency to flow in one direction.

### Mistake 3: God Components

```jsx
// Bad — one component doing everything
function ProductPage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cart, setCart] = useState([]);
  const [filters, setFilters] = useState({});
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('name');
  const [currentPage, setCurrentPage] = useState(1);
  // ... 200 more lines of state and handlers

  return (
    // ... 300 lines of JSX
  );
}
```

Split it up. Extract hooks for state management. Extract components for each UI section. A component should ideally be 50-150 lines.

### Mistake 4: Inconsistent Patterns

```
features/
├── auth/
│   ├── components/     ← Organized one way
│   │   └── LoginForm.jsx
│   └── hooks/
│       └── useAuth.js
├── products/
│   ├── ProductCard.jsx  ← Different organization
│   ├── ProductList.jsx
│   └── productService.js
└── cart/
    └── Cart.jsx         ← Yet another approach
```

Every feature should follow the same internal structure. Consistency matters more than any specific pattern.

### Mistake 5: Putting Everything in Shared

```
shared/components/
├── Button.jsx
├── Input.jsx
├── ProductCard.jsx      ← This is product-specific!
├── CartSummary.jsx      ← This is cart-specific!
├── LoginForm.jsx        ← This is auth-specific!
```

Shared should only contain truly reusable code. If a component is used by only one feature, it belongs in that feature's directory.

---

## Best Practices

1. **Start simple, restructure when needed.** A flat structure is fine for small projects. Adopt feature-based architecture when you feel pain with the current approach.

2. **Use barrel exports for public APIs.** Each feature should expose a clear public interface through its `index.js` file.

3. **Keep pages thin.** Pages should compose features, not contain business logic. Move complex logic into feature hooks and components.

4. **Separate UI from logic.** Presentation components receive props and render. Container components and hooks handle data and state.

5. **Set up path aliases early.** They make imports cleaner and refactoring easier. Configure them in both Vite and your editor.

6. **Follow consistent naming conventions.** Pick a convention and stick to it. Consistency is more important than any specific style.

7. **Minimize cross-feature imports.** Use shared context, props, or events for cross-feature communication. If two features are tightly coupled, they might be one feature.

8. **Colocate related files.** Keep styles, tests, and sub-components next to the components they belong to. Do not put all tests in a separate top-level `__tests__/` directory.

9. **Document your architecture.** A short README explaining the project structure saves every new developer time. Even a few lines describing the conventions is valuable.

10. **Review structure in code reviews.** When reviewing PRs, check not just the code but where the code lives. Catch misplaced files before they become habits.

---

## Summary

React does not enforce any particular file structure, which gives you freedom but also responsibility. The right architecture depends on your project size and team needs.

For small projects (under 20-30 files), a flat structure with `components/`, `hooks/`, and `utils/` folders works well. For medium to large projects, a feature-based structure keeps related code together, making features easier to find, modify, and delete.

The hybrid approach — features for domain-specific code, shared for reusable code, pages as thin composers — strikes the best balance for most applications. Combined with barrel exports, path aliases, and consistent naming, it creates a codebase that scales from 10 to 500+ files without chaos.

The most important principles are: start simple and evolve, keep features independent, separate UI from logic, and above all, be consistent. A mediocre structure followed consistently is better than a perfect structure followed inconsistently.

---

## Interview Questions

1. **How would you organize a large React application? What folder structure would you recommend?**

   *I would use a feature-based architecture with a shared directory for reusable code. Each feature (like authentication, products, or cart) gets its own directory containing its components, hooks, services, and a barrel export index.js that defines its public API. Shared code lives in a separate directory organized by type (components, hooks, utils). Pages are thin components that compose features together. This structure keeps related code colocated, making features easy to find and modify.*

2. **What are barrel exports and what problems do they solve?**

   *Barrel exports are index.js files that re-export from other files in a directory. They solve two problems: they create cleaner import paths (import from a directory instead of specific files), and they define a public API for a module, making it clear which parts are meant to be used externally. You should use named re-exports rather than wildcard exports to maintain explicitness.*

3. **How do you handle dependencies between features?**

   *Features should be as independent as possible. When they need to interact, there are three approaches: import from the feature's public API (barrel exports), use composition through pages (let pages wire features together via props), or use shared context for decoupled communication (like a notification system). Circular dependencies between features indicate a design problem — extract the shared logic into the shared directory.*

4. **What is the difference between a presentation component and a container component?**

   *A presentation component receives data through props and renders UI. It has no knowledge of where the data comes from. A container component manages data fetching, state, and business logic, then passes data to presentation components. In modern React, hooks have blurred this line — custom hooks often take on the container role, letting components be more presentational while hooks handle the logic.*

5. **When would you restructure a React project and how?**

   *Signs that restructuring is needed include: difficulty finding files, features tangled together, circular dependencies, huge directories, or inconsistent patterns. The approach should be incremental: create the new structure alongside the old, migrate one feature at a time, update all imports, run tests, and only delete old directories when empty. Never attempt a big-bang restructure — it is too risky and blocks other work.*

---

## Practice Exercises

### Exercise 1: Architecture Audit

Take any React project you have built (or find one on GitHub). Analyze its structure and answer:

- How many files are in the largest directory?
- Can you identify which files belong to which feature?
- Are there any circular dependencies?
- Is naming consistent throughout?

Write a migration plan that would move the project to a feature-based architecture.

### Exercise 2: Feature Module

Create a complete feature module for a "notifications" feature with:

- A `NotificationList` component that displays notifications
- A `NotificationItem` component for individual notifications
- A `useNotifications` hook that manages notification state
- A `notificationService` with CRUD operations
- A barrel export that exposes only the public API
- CSS Modules for styling

The feature should follow all the patterns described in this chapter.

### Exercise 3: Shared Component Library

Build a mini component library in `shared/components/` with these components, each in its own folder with styles and a barrel export:

- `Button` — with variants (primary, secondary, danger) and sizes (small, medium, large)
- `Input` — with label, error message, and helper text
- `Card` — with header, body, and footer slots
- `Alert` — with types (info, success, warning, error) and dismissible option

Create a root `shared/components/index.js` that exports everything.

### Exercise 4: Path Alias Setup

Set up path aliases in a Vite project:

1. Configure `vite.config.js` with aliases for `@`, `@features`, `@shared`, and `@pages`
2. Create a matching `jsconfig.json` for editor support
3. Refactor at least 10 imports in an existing project to use the new aliases
4. Verify everything still works by running the development server

### Exercise 5: Dependency Diagram

For the e-commerce application structure shown in this chapter, draw a dependency diagram showing:

- Which features import from other features
- Which features import from shared
- Which pages import from which features

Identify any potential circular dependencies and suggest how to eliminate them.

---

## What Is Next?

In Chapter 26, we will explore **Handling Images, Assets, and Environment Variables** — how to manage static assets like images, fonts, and SVGs in a React project, use environment variables effectively across different deployment environments, and optimize assets for performance.
