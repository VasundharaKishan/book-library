# Chapter 2: Module Pattern

## What You Will Learn

- Why global variables are dangerous in JavaScript
- How the Immediately Invoked Function Expression (IIFE) solves the global pollution problem
- How closures enable private and public members
- The Revealing Module Pattern and when to use it
- ES6 modules with import and export
- How barrel files organize your codebase
- Real-world module patterns in React projects

## Why This Chapter Matters

Imagine you live in a house with no rooms. No walls, no doors, no separation at all. Your bedroom is your kitchen is your bathroom. Everything is in one open space. Your toothbrush is next to the frying pan. Your bed is next to the toilet. Every person in the house can see and touch everything.

That is what JavaScript code looks like without modules. Every variable, every function, every piece of data lives in one giant shared space called the **global scope**. Any piece of code can read or overwrite anything else. One careless variable name and your entire application breaks.

The Module Pattern fixes this. It gives your code walls, doors, and rooms. It lets you decide what is private (hidden inside a room) and what is public (available through the door). It is one of the most fundamental patterns in JavaScript, and understanding it is essential before learning any other pattern in this book.

Every modern JavaScript application uses modules. Every React project, every Node.js server, every npm package relies on modules to stay organized. This chapter takes you from the problem (global chaos) to the solution (clean, isolated, organized code).

---

## The Problem: Global Scope Pollution

JavaScript was originally designed for small scripts on web pages. Early JavaScript ran in a single global scope. Every variable you declared with `var` became a property of the `window` object in browsers.

```javascript
// file1.js
var userName = 'Alice';
var count = 0;

function greet() {
  console.log('Hello, ' + userName);
}

// file2.js -- written by a different developer
var userName = 'ProductDB';  // Oops! Overwrites Alice
var count = 42;              // Oops! Overwrites the counter

function greet() {           // Oops! Overwrites the greeting function
  console.log('Connecting to ' + userName);
}
```

**Output when file2.js loads after file1.js:**
```
// Calling greet() now runs file2's version
Connecting to ProductDB
// The original greet() is gone forever
```

This is called **global scope pollution** or **namespace collision**. It is not a theoretical problem. It happened constantly in the early days of JavaScript.

```
  ┌─────────────────────────────────────────────────────────┐
  │                    Global Scope (window)                │
  │                                                         │
  │  userName = ???     <── Who set this? file1? file2?     │
  │  count = ???        <── 0 or 42? No way to tell         │
  │  greet = ???        <── Which greet? Last one wins       │
  │                                                         │
  │  Every script dumps variables here.                     │
  │  Every script can overwrite every other script.         │
  │  Pure chaos.                                            │
  └─────────────────────────────────────────────────────────┘
```

### Why This Breaks Real Applications

Consider loading multiple scripts in an HTML file:

```html
<!-- index.html -->
<script src="jquery.js"></script>
<script src="analytics.js"></script>
<script src="chat-widget.js"></script>
<script src="your-app.js"></script>
```

Each of these scripts shares the same global scope. If `analytics.js` defines a function called `track`, and `chat-widget.js` also defines a function called `track`, the second one silently overwrites the first. No error. No warning. Just broken analytics.

The real-world impact:

- **Silent bugs**: Variables get overwritten with no error message
- **Naming fear**: Developers resort to absurdly long names like `myCompany_analytics_track_event_v2` to avoid collisions
- **Dependency nightmares**: Script loading order matters and one wrong order breaks everything
- **Untestable code**: You cannot isolate and test pieces independently

---

## Solution 1: The IIFE (Immediately Invoked Function Expression)

Before ES6 modules existed, JavaScript developers found a clever solution: wrap your code in a function and call it immediately. This creates a private scope.

### How a Regular Function Creates Scope

In JavaScript, variables declared inside a function are not visible outside that function.

```javascript
function myModule() {
  var secret = 'hidden';
  console.log(secret); // 'hidden' -- works inside
}

myModule();
console.log(secret); // ReferenceError: secret is not defined
```

**Output:**
```
hidden
ReferenceError: secret is not defined
```

This is useful, but the function name `myModule` itself is a global variable. We still pollute the global scope with that name.

### The IIFE Removes Even the Function Name

An IIFE wraps a function in parentheses and calls it immediately. No name, no global variable.

```javascript
// An IIFE -- Immediately Invoked Function Expression
(function () {
  var secret = 'hidden';
  var count = 0;

  function increment() {
    count++;
    console.log('Count is now: ' + count);
  }

  increment();
  increment();

  console.log('Secret inside: ' + secret);
})();

// Outside the IIFE, nothing is accessible
// console.log(secret);  // ReferenceError
// console.log(count);   // ReferenceError
// increment();          // ReferenceError
```

**Output:**
```
Count is now: 1
Count is now: 2
Secret inside: hidden
```

### Anatomy of an IIFE

```
  (function () {        <── Wrapping in ( ) makes it an expression
    // Your code here   <── Everything in here is PRIVATE
  })();                 <── The () at the end CALLS it immediately
   │
   └── This is why it is "Immediately Invoked"
```

You can also write IIFEs with arrow functions:

```javascript
(() => {
  const secret = 'also hidden';
  console.log(secret);
})();
```

**Output:**
```
also hidden
```

### IIFE with Parameters

IIFEs can accept arguments, which is useful for injecting dependencies:

```javascript
(function (window, document) {
  // Use window and document safely here
  // Even if someone overwrites the global window variable,
  // this code still has the original references

  const button = document.createElement('button');
  button.textContent = 'Click me';
  console.log('Button created:', button.textContent);
})(window, document);
```

**Output:**
```
Button created: Click me
```

---

## Solution 2: The Classic Module Pattern (IIFE + Closures)

The IIFE hides everything. But what if you want to hide *some* things and expose *others*? That is where closures come in.

### Quick Refresher: What Is a Closure?

A closure is when a function "remembers" the variables from the scope where it was created, even after that scope has finished executing.

```javascript
function createCounter() {
  let count = 0; // This variable is "closed over"

  return function () {
    count++;
    return count;
  };
}

const counter = createCounter();
console.log(counter()); // 1
console.log(counter()); // 2
console.log(counter()); // 3
// count is not accessible directly
// console.log(count); // ReferenceError
```

**Output:**
```
1
2
3
```

The returned function "closes over" the `count` variable. It remembers `count` even though `createCounter` has already finished running. The variable `count` is effectively **private** -- nothing outside can access it except through the returned function.

### The Module Pattern: Private and Public Members

Combine the IIFE with closures, and you get the Module Pattern. Return an object whose methods have access to the private variables via closure.

```javascript
const CounterModule = (function () {
  // PRIVATE -- not accessible from outside
  let count = 0;
  const MAX_COUNT = 100;

  function validateCount(newCount) {
    return newCount >= 0 && newCount <= MAX_COUNT;
  }

  // PUBLIC -- returned object is the module's public API
  return {
    increment() {
      if (validateCount(count + 1)) {
        count++;
      }
      return count;
    },

    decrement() {
      if (validateCount(count - 1)) {
        count--;
      }
      return count;
    },

    getCount() {
      return count;
    },

    reset() {
      count = 0;
      return count;
    }
  };
})();

console.log(CounterModule.getCount());   // 0
console.log(CounterModule.increment());  // 1
console.log(CounterModule.increment());  // 2
console.log(CounterModule.decrement());  // 1
console.log(CounterModule.reset());      // 0

// Trying to access private members
console.log(CounterModule.count);          // undefined
console.log(CounterModule.MAX_COUNT);      // undefined
console.log(CounterModule.validateCount);  // undefined
```

**Output:**
```
0
1
2
1
0
undefined
undefined
undefined
```

### How It Works: A Visual Map

```
  ┌─────────────────────────────────────────────────────┐
  │              CounterModule (IIFE)                   │
  │                                                     │
  │   PRIVATE (hidden by closure):                      │
  │   ┌───────────────────────────────────┐             │
  │   │  let count = 0                    │             │
  │   │  const MAX_COUNT = 100            │             │
  │   │  function validateCount() {...}   │             │
  │   └───────────────────────────────────┘             │
  │                    │                                │
  │                    │ closure (remembers these)      │
  │                    ▼                                │
  │   PUBLIC (returned object):                         │
  │   ┌───────────────────────────────────┐             │
  │   │  increment()  -- can read/write   │◄── Outside  │
  │   │  decrement()     count via        │    code     │
  │   │  getCount()      closure          │    uses     │
  │   │  reset()                          │    these    │
  │   └───────────────────────────────────┘             │
  └─────────────────────────────────────────────────────┘
```

---

## The Revealing Module Pattern

The Revealing Module Pattern is a cleaner variation of the Module Pattern. Instead of defining methods inline in the returned object, you define all functions as private first, then "reveal" selected ones in the return statement.

### Before: Classic Module Pattern

```javascript
const UserModule = (function () {
  let users = [];

  return {
    addUser(name) {
      users.push({ name, id: Date.now() });
      console.log(`Added user: ${name}`);
    },
    getUsers() {
      return [...users]; // Return a copy
    },
    getUserCount() {
      return users.length;
    }
  };
})();
```

### After: Revealing Module Pattern

```javascript
const UserModule = (function () {
  // ALL variables and functions defined as private
  let users = [];

  function addUser(name) {
    users.push({ name, id: Date.now() });
    console.log(`Added user: ${name}`);
  }

  function getUsers() {
    return [...users];
  }

  function getUserCount() {
    return users.length;
  }

  function clearUsers() {
    users = [];
    console.log('All users cleared');
  }

  // "Reveal" only the public API
  return {
    addUser,
    getUsers,
    getUserCount
    // clearUsers is NOT revealed -- stays private
  };
})();

UserModule.addUser('Alice');
UserModule.addUser('Bob');
console.log('User count:', UserModule.getUserCount());
console.log('Users:', UserModule.getUsers());

// clearUsers is private, cannot be called
console.log(UserModule.clearUsers); // undefined
```

**Output:**
```
Added user: Alice
Added user: Bob
User count: 2
Users: [ { name: 'Alice', id: 1698765432100 }, { name: 'Bob', id: 1698765432101 } ]
undefined
```

### Why Revealing Is Better

```
  Classic Module Pattern          Revealing Module Pattern
  ─────────────────────           ────────────────────────

  return {                        function addUser() {...}
    addUser(name) {               function getUsers() {...}
      // definition here          function getUserCount() {...}
    },                            function clearUsers() {...}
    getUsers() {
      // definition here          return {
    },                              addUser,      // just names
    getUserCount() {                getUsers,
      // definition here            getUserCount
    }                             };
  };

  Methods defined INSIDE          Methods defined OUTSIDE
  the return object               then mapped in return

  Harder to see what              Easy to see what is
  is public vs private            public (in the return)
```

**Advantages of the Revealing Module Pattern:**

1. **Consistent style**: All functions are defined the same way
2. **Easy to see the API**: The return statement is a clean list of public names
3. **Easy to change**: Moving a function from public to private means removing one line from the return
4. **Named functions**: Better stack traces for debugging

---

## Real-World Module Pattern: Shopping Cart

Here is a practical example that combines everything you have learned.

### The Problem

You need a shopping cart that:
- Keeps items private (no direct manipulation)
- Validates before adding items
- Calculates totals
- Tracks discount codes
- Provides a clean API

### The Solution

```javascript
const ShoppingCart = (function () {
  // Private state
  let items = [];
  let discountCode = null;

  const discountCodes = {
    'SAVE10': 0.10,
    'SAVE20': 0.20,
    'HALF': 0.50
  };

  // Private functions
  function calculateSubtotal() {
    return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  }

  function calculateDiscount(subtotal) {
    if (discountCode && discountCodes[discountCode]) {
      return subtotal * discountCodes[discountCode];
    }
    return 0;
  }

  function findItemIndex(productId) {
    return items.findIndex(item => item.productId === productId);
  }

  // Public API
  function addItem(productId, name, price, quantity = 1) {
    if (price <= 0) {
      console.log('Error: Price must be positive');
      return false;
    }
    if (quantity <= 0) {
      console.log('Error: Quantity must be positive');
      return false;
    }

    const existingIndex = findItemIndex(productId);
    if (existingIndex > -1) {
      items[existingIndex].quantity += quantity;
      console.log(`Updated ${name}: quantity is now ${items[existingIndex].quantity}`);
    } else {
      items.push({ productId, name, price, quantity });
      console.log(`Added ${name} to cart`);
    }
    return true;
  }

  function removeItem(productId) {
    const index = findItemIndex(productId);
    if (index > -1) {
      const removed = items.splice(index, 1)[0];
      console.log(`Removed ${removed.name} from cart`);
      return true;
    }
    console.log('Item not found in cart');
    return false;
  }

  function applyDiscount(code) {
    if (discountCodes[code]) {
      discountCode = code;
      console.log(`Discount code ${code} applied: ${discountCodes[code] * 100}% off`);
      return true;
    }
    console.log('Invalid discount code');
    return false;
  }

  function getTotal() {
    const subtotal = calculateSubtotal();
    const discount = calculateDiscount(subtotal);
    return {
      subtotal: subtotal.toFixed(2),
      discount: discount.toFixed(2),
      total: (subtotal - discount).toFixed(2),
      itemCount: items.reduce((sum, item) => sum + item.quantity, 0)
    };
  }

  function getItems() {
    return items.map(item => ({ ...item })); // Return copies
  }

  // Reveal public API
  return {
    addItem,
    removeItem,
    applyDiscount,
    getTotal,
    getItems
  };
})();

// Usage
ShoppingCart.addItem('SKU001', 'Wireless Mouse', 29.99);
ShoppingCart.addItem('SKU002', 'USB Keyboard', 49.99);
ShoppingCart.addItem('SKU001', 'Wireless Mouse', 29.99); // Adds to quantity
ShoppingCart.applyDiscount('SAVE10');
console.log(ShoppingCart.getTotal());

// Cannot access internals
console.log(ShoppingCart.items);         // undefined
console.log(ShoppingCart.discountCodes); // undefined
```

**Output:**
```
Added Wireless Mouse to cart
Added USB Keyboard to cart
Updated Wireless Mouse: quantity is now 2
Discount code SAVE10 applied: 10% off
{ subtotal: '109.97', discount: '11.00', total: '98.97', itemCount: 3 }
undefined
undefined
```

---

## ES6 Modules: The Modern Standard

In 2015, JavaScript got native module support with ES6. This is now the standard way to write modules in JavaScript. No more IIFE tricks needed.

### Named Exports

```javascript
// math-utils.js
export function add(a, b) {
  return a + b;
}

export function multiply(a, b) {
  return a * b;
}

export const PI = 3.14159;

// Private -- not exported, not accessible from outside
function internalHelper(x) {
  return x * x;
}
```

```javascript
// app.js
import { add, multiply, PI } from './math-utils.js';

console.log(add(2, 3));        // 5
console.log(multiply(4, 5));   // 20
console.log(PI);               // 3.14159
// internalHelper is not accessible -- it is private to math-utils.js
```

**Output:**
```
5
20
3.14159
```

### Default Exports

Each module can have one default export. This is useful when a module has one main thing to export.

```javascript
// Logger.js
class Logger {
  constructor(prefix) {
    this.prefix = prefix;
  }

  log(message) {
    console.log(`[${this.prefix}] ${message}`);
  }

  error(message) {
    console.error(`[${this.prefix}] ERROR: ${message}`);
  }

  warn(message) {
    console.warn(`[${this.prefix}] WARN: ${message}`);
  }
}

export default Logger;
```

```javascript
// app.js
import Logger from './Logger.js';
// You can name default imports anything you want
// import MyLogger from './Logger.js'; // Also works!

const logger = new Logger('App');
logger.log('Application started');
logger.error('Something went wrong');
```

**Output:**
```
[App] Application started
[App] ERROR: Something went wrong
```

### Named vs Default Exports

```
  Named Exports                    Default Exports
  ──────────────                   ────────────────

  export function add() {}         export default function add() {}

  import { add } from './math';    import add from './math';
  import { add, multiply }         import whateverName from './math';
    from './math';

  Must use exact names             Can use any name on import
  Can have many per file           Only ONE per file
  Use { } in import                No { } in import

  Best for utility files           Best for single-purpose files
  with multiple exports             (a class, a component, etc.)
```

### Mixing Named and Default Exports

```javascript
// api-client.js
export default class ApiClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
  }

  async get(endpoint) {
    const response = await fetch(`${this.baseUrl}${endpoint}`);
    return response.json();
  }
}

// Named exports alongside the default
export const DEFAULT_BASE_URL = 'https://api.example.com';
export const TIMEOUT = 5000;
```

```javascript
// app.js
import ApiClient, { DEFAULT_BASE_URL, TIMEOUT } from './api-client.js';

const client = new ApiClient(DEFAULT_BASE_URL);
console.log('Base URL:', DEFAULT_BASE_URL);
console.log('Timeout:', TIMEOUT);
```

**Output:**
```
Base URL: https://api.example.com
Timeout: 5000
```

---

## ES Modules vs IIFE: How Privacy Works

Both approaches give you private and public members. The mechanism is different, but the result is the same.

```
  IIFE Module                        ES Module
  ───────────                        ─────────

  const Mod = (function () {         // utils.js
    // Private                       // Private (not exported)
    let secret = 42;                 let secret = 42;

    function helper() {              function helper() {
      return secret;                   return secret;
    }                                }

    // Public                        // Public (exported)
    return {                         export function getSecret() {
      getSecret() {                    return helper();
        return helper();             }
      }
    };
  })();

  Privacy via: closure               Privacy via: module scope
  Works in: any JS environment        Works in: modern browsers, bundlers
  Created at: runtime                Created at: parse time
```

In ES modules, anything you do not export is private by default. You do not need closures or IIFEs. The module system handles scoping for you.

---

## Barrel Files: Organizing Exports

As your project grows, you end up with many modules. Importing from deep paths gets messy.

### The Problem: Deep Import Paths

```javascript
// Without barrel files, imports are messy and fragile
import { validateEmail } from '../utils/validation/email.js';
import { validatePhone } from '../utils/validation/phone.js';
import { formatDate } from '../utils/formatting/date.js';
import { formatCurrency } from '../utils/formatting/currency.js';
import { fetchUser } from '../services/api/user.js';
import { fetchProducts } from '../services/api/products.js';
```

### The Solution: Barrel Files (index.js)

A barrel file is an `index.js` file that re-exports from multiple modules. It acts as a single entry point for a folder.

```javascript
// utils/validation/index.js (barrel file)
export { validateEmail } from './email.js';
export { validatePhone } from './phone.js';
export { validatePassword } from './password.js';
export { validateUsername } from './username.js';
```

```javascript
// utils/formatting/index.js (barrel file)
export { formatDate } from './date.js';
export { formatCurrency } from './currency.js';
export { formatNumber } from './number.js';
```

```javascript
// utils/index.js (top-level barrel)
export * from './validation/index.js';
export * from './formatting/index.js';
```

```javascript
// Now importing is clean and simple
import { validateEmail, validatePhone, formatDate, formatCurrency } from '../utils';
```

### Barrel File Structure

```
  src/
  ├── utils/
  │   ├── index.js           <── Top-level barrel
  │   ├── validation/
  │   │   ├── index.js       <── Barrel for validation
  │   │   ├── email.js
  │   │   ├── phone.js
  │   │   └── password.js
  │   └── formatting/
  │       ├── index.js       <── Barrel for formatting
  │       ├── date.js
  │       ├── currency.js
  │       └── number.js
  ├── components/
  │   ├── index.js           <── Barrel for components
  │   ├── Button.jsx
  │   ├── Input.jsx
  │   └── Modal.jsx
  └── hooks/
      ├── index.js           <── Barrel for hooks
      ├── useAuth.js
      ├── useLocalStorage.js
      └── useDebounce.js
```

### React Component Barrel File

```javascript
// components/index.js
export { default as Button } from './Button';
export { default as Input } from './Input';
export { default as Modal } from './Modal';
export { default as Card } from './Card';
export { default as Spinner } from './Spinner';
```

```javascript
// pages/Dashboard.jsx
import { Button, Card, Spinner } from '../components';
// Instead of:
// import Button from '../components/Button';
// import Card from '../components/Card';
// import Spinner from '../components/Spinner';
```

### Barrel File Warning: Tree Shaking

Barrel files can hurt performance if your bundler cannot tree-shake properly. When you import one thing from a barrel file, the bundler might load everything the barrel re-exports.

```javascript
// If you only need formatDate, but the barrel exports 50 functions,
// a poorly configured bundler loads all 50
import { formatDate } from '../utils';

// Direct import is always safe for tree shaking
import { formatDate } from '../utils/formatting/date.js';
```

**Rule of thumb**: Use barrel files for convenience during development. If bundle size becomes an issue, profile and switch to direct imports where needed.

---

## Module Pattern in React

React components are already modules (each `.jsx` file is an ES module). But the Module Pattern thinking still applies when you organize state, utilities, and custom hooks.

### Example: A Feature Module

```javascript
// features/auth/auth-service.js

// Private state (module-scoped, not exported)
let cachedToken = null;
let tokenExpiry = null;

// Private helper
function isTokenExpired() {
  return !tokenExpiry || Date.now() > tokenExpiry;
}

// Public API
export async function login(email, password) {
  const response = await fetch('/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });

  const data = await response.json();
  cachedToken = data.token;
  tokenExpiry = Date.now() + data.expiresIn * 1000;
  return data.user;
}

export function getToken() {
  if (isTokenExpired()) {
    cachedToken = null;
    tokenExpiry = null;
    return null;
  }
  return cachedToken;
}

export function logout() {
  cachedToken = null;
  tokenExpiry = null;
}

export function isAuthenticated() {
  return !isTokenExpired() && cachedToken !== null;
}
```

```javascript
// components/LoginForm.jsx
import { useState } from 'react';
import { login } from '../features/auth/auth-service';

export default function LoginForm({ onSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      const user = await login(email, password);
      onSuccess(user);
    } catch (err) {
      setError('Login failed. Please try again.');
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <button type="submit">Log In</button>
    </form>
  );
}
```

---

## When to Use / When NOT to Use

### When to Use the Module Pattern

- **Organizing utility functions**: Group related helpers into a module with a clean API
- **Encapsulating state**: When you need private variables that should not be directly modified
- **Library/SDK development**: Expose a public API while hiding implementation details
- **Legacy codebases**: IIFEs work without a build system -- great for adding structure to old projects
- **Configuration management**: Store config values privately, expose getters

### When NOT to Use the Module Pattern

- **Simple, stateless functions**: If you just have pure utility functions, a plain ES module with exports is enough. No need for IIFEs or the Revealing Module Pattern
- **React component state**: Use `useState` and `useReducer`, not module-level variables, for UI state
- **Shared mutable state across components**: Use Context, Redux, or Zustand instead of module-scoped variables
- **When you need multiple instances**: The module pattern creates a single instance. If you need multiple instances, use a class or factory function instead

---

## Common Mistakes

### Mistake 1: Using Module-Scoped Variables for React UI State

```javascript
// BAD -- module variable does not trigger re-renders
let count = 0;

export default function Counter() {
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => count++}>Increment</button>
      {/* The UI will NOT update because React does not know count changed */}
    </div>
  );
}
```

```javascript
// GOOD -- useState triggers re-renders
import { useState } from 'react';

export default function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(c => c + 1)}>Increment</button>
    </div>
  );
}
```

### Mistake 2: Circular Dependencies in Barrel Files

```javascript
// utils/index.js
export * from './a.js';
export * from './b.js';

// a.js
import { helperB } from './index.js'; // Imports from barrel
export function helperA() { return helperB(); }

// b.js
import { helperA } from './index.js'; // Circular!
export function helperB() { return helperA(); }

// This creates an infinite loop or undefined imports
```

**Fix**: Import directly from the source file, not the barrel, when you have cross-dependencies.

```javascript
// a.js
import { helperB } from './b.js'; // Direct import, no circular issue
```

### Mistake 3: Forgetting That Module Variables Are Shared

```javascript
// counter-module.js
let count = 0;
export function increment() { return ++count; }
export function getCount() { return count; }

// component-a.js
import { increment, getCount } from './counter-module.js';
increment(); // count is now 1

// component-b.js
import { getCount } from './counter-module.js';
console.log(getCount()); // 1 -- NOT 0!
// Both files share the SAME module instance
```

This is a feature, not a bug, but it surprises beginners. ES modules are singletons -- they execute once and every import gets the same instance.

---

## Best Practices

1. **Prefer ES modules over IIFEs** in modern projects. IIFEs are for legacy code or environments without a module system.

2. **Export the minimum necessary API**. The less you expose, the easier your module is to maintain and the harder it is to misuse.

3. **Use named exports for most things**. They enable auto-import in IDEs and make refactoring safer (renaming is caught by the editor).

4. **Use default exports for single-purpose modules** like React components or classes.

5. **Keep barrel files shallow**. Re-export from the immediate children only, not from deeply nested modules.

6. **Avoid mutable module-scoped state for UI**. Use React state management for anything that should trigger re-renders.

7. **Name your files after what they export**. `formatDate.js` should export `formatDate`. `UserService.js` should export `UserService`. Predictability matters.

---

## Quick Summary

The Module Pattern solves global scope pollution by creating isolated, private scopes with controlled public APIs.

```
  Evolution of Modules in JavaScript:
  ─────────────────────────────────────

  1. Global Scope (chaos)
     └──► 2. IIFE (private scope, single expression)
           └──► 3. Module Pattern (IIFE + closures, private/public)
                 └──► 4. Revealing Module (cleaner return object)
                       └──► 5. ES6 Modules (native, standard, best)
```

---

## Key Points

- **Global scope pollution** is when multiple scripts share and overwrite variables in the global namespace
- **IIFEs** create a private scope by wrapping code in a function that runs immediately
- **Closures** let inner functions access outer variables, enabling private state
- **The Module Pattern** combines IIFEs and closures to create modules with private internals and a public API
- **The Revealing Module Pattern** defines all members privately first, then reveals selected ones in the return statement
- **ES6 modules** use `export` and `import` keywords. They are the modern standard and should be preferred
- **Barrel files** (`index.js`) re-export from multiple modules to simplify import paths
- **ES modules are singletons** -- every import of the same module gets the same instance
- **Module-scoped variables** are shared across all importers. Do not use them for React UI state

---

## Practice Questions

1. What is the difference between a regular function and an IIFE? Why does wrapping a function in parentheses and calling it immediately prevent global scope pollution?

2. Explain how closures enable private variables in the Module Pattern. Why can outside code not access the private variables directly?

3. What is the difference between the classic Module Pattern and the Revealing Module Pattern? When would you choose one over the other?

4. Why are ES modules considered singletons? If two different files import the same module, do they each get a separate copy or the same instance?

5. What are the potential downsides of barrel files? How can they affect bundle size and tree shaking?

---

## Exercises

### Exercise 1: Build a Temperature Converter Module

Create a module (using either the Revealing Module Pattern or ES6 exports) that:
- Converts Celsius to Fahrenheit
- Converts Fahrenheit to Celsius
- Keeps a private history of all conversions performed
- Has a public method to retrieve the conversion history
- Has a public method to clear the history

Test it by performing several conversions and then checking the history.

### Exercise 2: Refactor Global Code into Modules

Take this global code and refactor it into a clean module:

```javascript
var todos = [];
var nextId = 1;

function addTodo(text) {
  todos.push({ id: nextId++, text: text, done: false });
}

function toggleTodo(id) {
  var todo = todos.find(function(t) { return t.id === id; });
  if (todo) todo.done = !todo.done;
}

function getTodos() {
  return todos;
}
```

Make `todos` and `nextId` private. Expose `addTodo`, `toggleTodo`, `getTodos`, and add a new `removeTodo` function. Ensure `getTodos` returns copies, not the original array.

### Exercise 3: Create a Barrel File Structure

Create a file structure for a React project with the following:
- A `hooks/` folder with `useAuth.js`, `useLocalStorage.js`, and `useDebounce.js`
- A `utils/` folder with `formatDate.js`, `formatCurrency.js`, and `validateEmail.js`
- Barrel files (`index.js`) for both folders
- A component that imports from both barrel files in a single clean import line

---

## What Is Next?

Now that you understand how to organize code into isolated modules with private and public members, you are ready for the next question: what if you need exactly **one instance** of something across your entire application? One configuration object. One logger. One authentication store.

That is the Singleton Pattern, and it is the focus of Chapter 3.
