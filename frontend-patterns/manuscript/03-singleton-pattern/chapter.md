# Chapter 3: Singleton Pattern

## What You Will Learn

- What the Singleton Pattern is and why "one instance only" matters
- How ES modules naturally create singletons
- How to use `Object.freeze` to make singletons immutable
- When the Singleton Pattern hurts (especially in testing)
- Real-world singletons: auth store, logger, theme manager
- How to implement singletons with and without classes

## Why This Chapter Matters

Think about a restaurant kitchen. There is one head chef. Not two, not three -- exactly one. Every waiter delivers orders to the same head chef. Every sous-chef reports to the same head chef. If there were two head chefs giving contradictory instructions, the kitchen would descend into chaos. Two people seasoning the same dish. Two people deciding the menu. Two sources of truth.

The Singleton Pattern works the same way. Some things in your application should exist exactly once. One authentication state. One logger writing to the console. One theme configuration. One database connection pool. If you accidentally create two of these, you get inconsistent state, duplicated connections, and bugs that are incredibly hard to track down.

This pattern is both powerful and controversial. It solves real problems, but it can also create new ones when misused. By the end of this chapter, you will know exactly when to use it, when to avoid it, and how to implement it correctly in modern JavaScript.

---

## The Problem: Accidental Multiple Instances

Imagine you build an authentication service for your app. It tracks whether the user is logged in and stores their token.

```javascript
// auth-service.js -- a plain class

class AuthService {
  constructor() {
    this.user = null;
    this.token = null;
    this.isAuthenticated = false;
    console.log('AuthService created');
  }

  login(user, token) {
    this.user = user;
    this.token = token;
    this.isAuthenticated = true;
    console.log(`Logged in as ${user.name}`);
  }

  logout() {
    this.user = null;
    this.token = null;
    this.isAuthenticated = false;
    console.log('Logged out');
  }

  getToken() {
    return this.token;
  }
}

export default AuthService;
```

Now different parts of your app use it:

```javascript
// navbar.js
import AuthService from './auth-service.js';
const auth = new AuthService(); // Creates instance #1

function showUserName() {
  if (auth.isAuthenticated) {
    console.log('Welcome, ' + auth.user.name);
  } else {
    console.log('Please log in');
  }
}

// api-client.js
import AuthService from './auth-service.js';
const auth = new AuthService(); // Creates instance #2 !!

function makeRequest(url) {
  const token = auth.getToken();
  console.log('Using token:', token);
  // fetch(url, { headers: { Authorization: `Bearer ${token}` } });
}
```

**Output:**
```
AuthService created
AuthService created
```

Two instances! When `navbar.js` logs the user in, `api-client.js` still thinks nobody is logged in. Its `auth` is a completely separate object with its own state.

```
  ┌──────────────────┐      ┌──────────────────┐
  │    navbar.js     │      │   api-client.js   │
  │                  │      │                   │
  │  const auth =    │      │  const auth =     │
  │    new Auth()    │      │    new Auth()     │
  │                  │      │                   │
  │  auth.user =     │      │  auth.user =      │
  │    'Alice'       │      │    null           │
  │  auth.token =    │      │  auth.token =     │
  │    'abc123'      │      │    null           │
  └──────────────────┘      └──────────────────┘
       Instance #1               Instance #2

  Two instances = two sources of truth = BUGS
```

---

## The Solution: Singleton Pattern

The Singleton Pattern ensures a class or module has only one instance and provides a global point of access to it.

```
  ┌──────────────────┐      ┌──────────────────┐
  │    navbar.js     │      │   api-client.js   │
  │                  │      │                   │
  │  auth.user =     │      │  auth.token =     │
  │    'Alice'  ─────┼──┐   │    'abc123' ──────┼──┐
  └──────────────────┘  │   └──────────────────┘  │
                        │                          │
                        ▼                          ▼
                   ┌─────────────────────────┐
                   │   Single Auth Instance   │
                   │                          │
                   │   user: 'Alice'          │
                   │   token: 'abc123'        │
                   │   isAuthenticated: true   │
                   └─────────────────────────┘

  One instance = one source of truth = consistency
```

---

## Implementation 1: ES Module Singleton (Recommended)

The simplest and most modern way to create a singleton in JavaScript is to use ES modules. Remember from Chapter 2: ES modules are evaluated once and cached. Every file that imports the module gets the same instance.

```javascript
// auth-service.js -- ES module singleton

class AuthService {
  constructor() {
    this.user = null;
    this.token = null;
    this.isAuthenticated = false;
    console.log('AuthService created');
  }

  login(user, token) {
    this.user = user;
    this.token = token;
    this.isAuthenticated = true;
    console.log(`Logged in as ${user.name}`);
  }

  logout() {
    this.user = null;
    this.token = null;
    this.isAuthenticated = false;
    console.log('Logged out');
  }

  getToken() {
    return this.token;
  }
}

// Create ONE instance and export it
// NOT the class -- the instance
const authService = new AuthService();
export default authService;
```

```javascript
// navbar.js
import authService from './auth-service.js';

authService.login({ name: 'Alice' }, 'token-abc-123');
console.log('Navbar - Is authenticated:', authService.isAuthenticated);
```

```javascript
// api-client.js
import authService from './auth-service.js';

// This is the SAME instance that navbar.js imported
console.log('API Client - Is authenticated:', authService.isAuthenticated);
console.log('API Client - Token:', authService.getToken());
```

**Output (when navbar.js runs first):**
```
AuthService created
Logged in as Alice
Navbar - Is authenticated: true
API Client - Is authenticated: true
API Client - Token: token-abc-123
```

Notice: "AuthService created" appears only once. Both files share the same instance.

### Why This Works

```
  ES Module Loading Process:
  ─────────────────────────

  1. navbar.js says: import authService from './auth-service.js'
     └──► Module system checks: "Have I loaded auth-service.js before?"
          └──► No. Load it, execute it, cache the result.
               └──► The cached result includes the authService instance.

  2. api-client.js says: import authService from './auth-service.js'
     └──► Module system checks: "Have I loaded auth-service.js before?"
          └──► Yes! Return the cached result.
               └──► Same authService instance. No new AuthService() call.
```

---

## Implementation 2: Object.freeze for Immutable Singletons

Sometimes you want a singleton whose structure cannot be changed. `Object.freeze` prevents adding, removing, or modifying properties.

```javascript
// config.js -- frozen singleton

const config = Object.freeze({
  apiUrl: 'https://api.example.com',
  apiVersion: 'v2',
  timeout: 5000,
  maxRetries: 3,
  features: Object.freeze({
    darkMode: true,
    betaFeatures: false,
    analytics: true
  })
});

export default config;
```

```javascript
// app.js
import config from './config.js';

console.log(config.apiUrl);     // 'https://api.example.com'
console.log(config.timeout);    // 5000

// Attempting to modify
config.apiUrl = 'https://evil.com';
console.log(config.apiUrl);     // Still 'https://api.example.com'

config.newProp = 'hello';
console.log(config.newProp);    // undefined

// Nested freeze works too
config.features.darkMode = false;
console.log(config.features.darkMode); // Still true
```

**Output:**
```
https://api.example.com
5000
https://api.example.com
undefined
true
```

### Object.freeze Is Shallow by Default

`Object.freeze` only freezes the top level. Nested objects are still mutable unless you freeze them too.

```javascript
// WRONG -- shallow freeze
const settings = Object.freeze({
  theme: {
    primary: '#007bff'
  }
});

settings.theme.primary = '#ff0000'; // This WORKS -- nested object is not frozen!
console.log(settings.theme.primary); // '#ff0000'
```

```javascript
// RIGHT -- deep freeze
function deepFreeze(obj) {
  Object.freeze(obj);
  Object.keys(obj).forEach(key => {
    if (typeof obj[key] === 'object' && obj[key] !== null) {
      deepFreeze(obj[key]);
    }
  });
  return obj;
}

const settings = deepFreeze({
  theme: {
    primary: '#007bff',
    fonts: {
      heading: 'Georgia',
      body: 'Arial'
    }
  }
});

settings.theme.primary = '#ff0000';
console.log(settings.theme.primary); // '#007bff' -- stays frozen
```

**Output:**
```
#007bff
```

---

## Implementation 3: Classic Singleton Class

In environments without ES modules, or when you want explicit control, you can implement the Singleton Pattern with a class that manages its own instance.

```javascript
// database-connection.js

class DatabaseConnection {
  constructor(connectionString) {
    if (DatabaseConnection.instance) {
      console.log('Returning existing connection');
      return DatabaseConnection.instance;
    }

    this.connectionString = connectionString;
    this.connected = false;
    this.queryCount = 0;
    console.log('Creating new database connection');

    DatabaseConnection.instance = this;
  }

  connect() {
    this.connected = true;
    console.log(`Connected to ${this.connectionString}`);
  }

  query(sql) {
    if (!this.connected) {
      throw new Error('Not connected to database');
    }
    this.queryCount++;
    console.log(`Query #${this.queryCount}: ${sql}`);
    return { rows: [], queryCount: this.queryCount };
  }

  disconnect() {
    this.connected = false;
    console.log('Disconnected');
  }
}

// Usage
const db1 = new DatabaseConnection('postgres://localhost:5432/mydb');
db1.connect();
db1.query('SELECT * FROM users');

const db2 = new DatabaseConnection('postgres://localhost:5432/otherdb');
// db2 is the SAME instance as db1!
console.log('Same instance?', db1 === db2);
console.log('Connection string:', db2.connectionString);
db2.query('SELECT * FROM products');
```

**Output:**
```
Creating new database connection
Connected to postgres://localhost:5432/mydb
Query #1: SELECT * FROM users
Returning existing connection
Same instance? true
Connection string: postgres://localhost:5432/mydb
Query #2: SELECT * FROM products
```

Notice that `db2` silently received the same instance as `db1`. The second connection string (`otherdb`) was ignored. This can be surprising and is one reason some developers dislike this approach.

---

## Real-World Singleton: Logger

A logger is a classic singleton use case. You want one logger that every part of your application writes to, with consistent formatting and a single configuration.

```javascript
// logger.js

const LOG_LEVELS = Object.freeze({
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3,
  NONE: 4
});

class Logger {
  constructor() {
    this.level = LOG_LEVELS.INFO;
    this.logs = [];
    this.prefix = '';
  }

  setLevel(level) {
    this.level = level;
    console.log(`Log level set to ${Object.keys(LOG_LEVELS).find(k => LOG_LEVELS[k] === level)}`);
  }

  setPrefix(prefix) {
    this.prefix = prefix;
  }

  _formatMessage(level, message) {
    const timestamp = new Date().toISOString().slice(11, 23);
    const label = Object.keys(LOG_LEVELS).find(k => LOG_LEVELS[k] === level);
    const prefixStr = this.prefix ? `[${this.prefix}] ` : '';
    return `${timestamp} [${label}] ${prefixStr}${message}`;
  }

  _log(level, message, ...args) {
    if (level < this.level) return;

    const formatted = this._formatMessage(level, message);
    this.logs.push({ level, message: formatted, timestamp: Date.now() });

    if (level === LOG_LEVELS.ERROR) {
      console.error(formatted, ...args);
    } else if (level === LOG_LEVELS.WARN) {
      console.warn(formatted, ...args);
    } else {
      console.log(formatted, ...args);
    }
  }

  debug(message, ...args) { this._log(LOG_LEVELS.DEBUG, message, ...args); }
  info(message, ...args)  { this._log(LOG_LEVELS.INFO, message, ...args); }
  warn(message, ...args)  { this._log(LOG_LEVELS.WARN, message, ...args); }
  error(message, ...args) { this._log(LOG_LEVELS.ERROR, message, ...args); }

  getHistory() {
    return [...this.logs];
  }

  clear() {
    this.logs = [];
  }
}

// Export a single instance
const logger = new Logger();
export { LOG_LEVELS };
export default logger;
```

```javascript
// auth.js
import logger from './logger.js';

function login(email) {
  logger.info(`Login attempt for ${email}`);
  // ... authentication logic
  logger.info(`Login successful for ${email}`);
}

login('alice@example.com');
```

```javascript
// api-client.js
import logger from './logger.js';

function fetchData(url) {
  logger.info(`Fetching ${url}`);
  // ... fetch logic
  logger.warn('Response was slow (> 2s)');
}

fetchData('/api/users');
```

```javascript
// app.js
import logger from './logger.js';

// All modules wrote to the SAME logger
console.log('Total log entries:', logger.getHistory().length);
```

**Output:**
```
14:32:01.234 [INFO] Login attempt for alice@example.com
14:32:01.235 [INFO] Login successful for alice@example.com
14:32:01.236 [INFO] Fetching /api/users
14:32:01.237 [WARN] Response was slow (> 2s)
Total log entries: 4
```

Every module imported the same `logger` instance. All four messages ended up in the same log history.

---

## Real-World Singleton: Theme Manager

```javascript
// theme-manager.js

const THEMES = {
  light: Object.freeze({
    name: 'light',
    background: '#ffffff',
    text: '#1a1a1a',
    primary: '#007bff',
    secondary: '#6c757d',
    border: '#dee2e6'
  }),
  dark: Object.freeze({
    name: 'dark',
    background: '#1a1a1a',
    text: '#f8f9fa',
    primary: '#4dabf7',
    secondary: '#adb5bd',
    border: '#495057'
  })
};

class ThemeManager {
  constructor() {
    this.currentTheme = THEMES.light;
    this.listeners = [];
  }

  getTheme() {
    return this.currentTheme;
  }

  setTheme(themeName) {
    if (!THEMES[themeName]) {
      console.error(`Theme "${themeName}" not found`);
      return;
    }

    this.currentTheme = THEMES[themeName];
    console.log(`Theme changed to: ${themeName}`);

    // Notify all listeners
    this.listeners.forEach(listener => listener(this.currentTheme));
  }

  toggle() {
    const next = this.currentTheme.name === 'light' ? 'dark' : 'light';
    this.setTheme(next);
  }

  subscribe(listener) {
    this.listeners.push(listener);
    // Return unsubscribe function
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }
}

const themeManager = new ThemeManager();
export { THEMES };
export default themeManager;
```

```javascript
// header.js
import themeManager from './theme-manager.js';

// Subscribe to theme changes
themeManager.subscribe((theme) => {
  console.log(`Header updating to ${theme.name} theme`);
  console.log(`  Background: ${theme.background}`);
  console.log(`  Text: ${theme.text}`);
});

// sidebar.js
import themeManager from './theme-manager.js';

themeManager.subscribe((theme) => {
  console.log(`Sidebar updating to ${theme.name} theme`);
});

// Toggle the theme -- both subscribers get notified
themeManager.toggle();
```

**Output:**
```
Theme changed to: dark
Header updating to dark theme
  Background: #1a1a1a
  Text: #f8f9fa
Sidebar updating to dark theme
```

One `themeManager` instance. All components listen to the same source of truth.

---

## Real-World Singleton: Auth Store

```javascript
// auth-store.js

class AuthStore {
  constructor() {
    this.user = null;
    this.token = null;
    this.listeners = new Set();
  }

  getState() {
    return {
      user: this.user,
      token: this.token,
      isAuthenticated: this.token !== null
    };
  }

  login(user, token) {
    this.user = user;
    this.token = token;
    this._notify();
    console.log(`Auth: Logged in as ${user.name}`);
  }

  logout() {
    this.user = null;
    this.token = null;
    this._notify();
    console.log('Auth: Logged out');
  }

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  _notify() {
    const state = this.getState();
    this.listeners.forEach(listener => listener(state));
  }
}

const authStore = new AuthStore();
export default authStore;
```

```javascript
// Usage across your app
import authStore from './auth-store.js';

// Component A subscribes
const unsubscribe = authStore.subscribe((state) => {
  console.log('Component A:', state.isAuthenticated ? 'Show dashboard' : 'Show login');
});

// Component B subscribes
authStore.subscribe((state) => {
  console.log('Component B:', state.isAuthenticated ? `Welcome ${state.user.name}` : 'Guest');
});

// Login triggers both components
authStore.login({ name: 'Alice', email: 'alice@example.com' }, 'jwt-token-xyz');

// Logout triggers both components
authStore.logout();

// Unsubscribe Component A
unsubscribe();

// Only Component B reacts now
authStore.login({ name: 'Bob', email: 'bob@example.com' }, 'jwt-token-abc');
```

**Output:**
```
Component A: Show dashboard
Component B: Welcome Alice
Auth: Logged in as Alice
Component A: Show login
Component B: Guest
Auth: Logged out
Component B: Welcome Bob
Auth: Logged in as Bob
```

---

## When the Singleton Pattern Is Bad: Testing

The biggest criticism of the Singleton Pattern is that it makes testing difficult. Because every test shares the same instance, state leaks between tests.

### The Problem

```javascript
// auth-store.test.js

import authStore from './auth-store.js';

// Test 1
test('login sets user', () => {
  authStore.login({ name: 'Alice' }, 'token-1');
  expect(authStore.getState().isAuthenticated).toBe(true); // PASS
});

// Test 2
test('starts logged out', () => {
  // FAIL! authStore still has Alice from Test 1
  expect(authStore.getState().isAuthenticated).toBe(false); // OOPS
});
```

```
  Test 1 runs:                    Test 2 runs:
  ┌──────────────┐               ┌──────────────┐
  │  Login Alice  │               │  Expects     │
  │  token: xyz   │──── SAME ────►│  empty state │
  │               │   INSTANCE    │  but gets    │
  │               │               │  Alice!      │
  └──────────────┘               └──────────────┘

  Singleton state leaks between tests
```

### The Fix: Add a Reset Method

```javascript
// auth-store.js -- with reset for testing

class AuthStore {
  constructor() {
    this._reset();
  }

  _reset() {
    this.user = null;
    this.token = null;
    this.listeners = new Set();
  }

  // ... other methods ...

  // Only for testing!
  __resetForTesting() {
    this._reset();
  }
}

const authStore = new AuthStore();
export default authStore;
```

```javascript
// auth-store.test.js -- fixed

import authStore from './auth-store.js';

beforeEach(() => {
  authStore.__resetForTesting(); // Clean state before each test
});

test('login sets user', () => {
  authStore.login({ name: 'Alice' }, 'token-1');
  expect(authStore.getState().isAuthenticated).toBe(true); // PASS
});

test('starts logged out', () => {
  expect(authStore.getState().isAuthenticated).toBe(false); // PASS
});
```

### The Alternative: Dependency Injection

Instead of importing the singleton directly, pass it as a parameter. This makes testing easy because you can pass a mock.

```javascript
// api-client.js -- dependency injection version

export function createApiClient(authStore) {
  return {
    async fetchData(url) {
      const { token } = authStore.getState();
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      console.log('Fetching with token:', token);
      // return fetch(url, { headers });
    }
  };
}
```

```javascript
// In production
import authStore from './auth-store.js';
import { createApiClient } from './api-client.js';

const api = createApiClient(authStore);
```

```javascript
// In tests -- easy to mock!
import { createApiClient } from './api-client.js';

test('sends auth header when logged in', async () => {
  const mockAuthStore = {
    getState: () => ({ token: 'test-token-123', isAuthenticated: true })
  };

  const api = createApiClient(mockAuthStore);
  await api.fetchData('/api/users'); // Uses mock, not real singleton
});
```

**Output:**
```
Fetching with token: test-token-123
```

---

## Singleton vs Module-Level Object: What Is the Difference?

You might wonder: "If I just export a plain object, is that a singleton?"

Yes, effectively. In ES modules, exporting an object literal gives you a singleton for free.

```javascript
// Simple object singleton -- works perfectly for many cases
export const analytics = {
  events: [],

  track(event, data) {
    this.events.push({ event, data, timestamp: Date.now() });
    console.log(`Tracked: ${event}`);
  },

  getEvents() {
    return [...this.events];
  }
};
```

This is simpler than a class-based singleton and works in most cases. Use a class when you need:
- Constructor logic
- Private methods (with `#private` syntax)
- Inheritance
- A reset method for testing

```
  When to Use What:
  ─────────────────

  Plain Object Export        Class Instance Export
  ──────────────────         ────────────────────

  Simple key-value config    Has initialization logic
  Stateless utilities        Manages internal state
  Small, simple API          Needs private methods
  No constructor needed      Needs a reset for testing

  const config = {           const logger = new Logger();
    apiUrl: '...',           export default logger;
    timeout: 5000
  };
  export default config;
```

---

## When to Use / When NOT to Use

### When to Use the Singleton Pattern

- **Configuration objects**: App-wide settings that should not be duplicated
- **Loggers**: One log destination for the entire application
- **Caches**: A shared cache that all modules read from and write to
- **Connection pools**: Database or WebSocket connections
- **Theme managers**: One source of truth for the current theme
- **Auth state**: One place that knows if the user is logged in
- **Feature flags**: One object that tells every component which features are enabled

### When NOT to Use the Singleton Pattern

- **React component state**: Use `useState`, Context, or a state management library. Singletons do not trigger re-renders
- **When you need multiple instances**: If you might ever need two loggers or two themes simultaneously, a singleton is the wrong choice
- **When testability is critical**: Singletons make unit testing harder. If your module needs heavy testing, prefer dependency injection
- **When the "single instance" constraint is artificial**: If you are making something a singleton just because you currently only need one, you are over-constraining your design
- **Server-side rendering (SSR)**: Singletons persist across requests on the server, leaking one user's data to another. This is a serious security issue in Next.js and similar frameworks

---

## Common Mistakes

### Mistake 1: Singleton State in Server-Side Rendering

```javascript
// DANGEROUS in Next.js or any SSR framework
// auth-store.js
const authStore = new AuthStore();
export default authStore;

// On the server, this singleton is shared across ALL requests.
// User A logs in, then User B's request sees User A's auth state!
```

**Fix**: In SSR, create instances per request or use framework-provided state management.

### Mistake 2: Hidden Coupling

```javascript
// Every file that imports the singleton is now coupled to it
import logger from './logger.js';

// If you ever want to replace the logger (say, for a different
// logging service), you have to change every file that imports it.
```

**Fix**: Use dependency injection for critical dependencies, especially in libraries.

### Mistake 3: Using Singletons for Everything

```javascript
// Do NOT make everything a singleton
const StringUtils = new StringUtilsClass();     // No! Just export functions
const MathHelper = new MathHelperClass();       // No! Just export functions
const Formatter = new FormatterClass();          // No! Just export functions
```

Stateless utility functions do not need to be singletons. Just export them as regular functions.

### Mistake 4: Forgetting That Singletons Are Mutable by Default

```javascript
// config.js
const config = { apiUrl: 'https://api.example.com', timeout: 5000 };
export default config;

// some-module.js
import config from './config.js';
config.apiUrl = 'https://evil.com'; // Silently changes it for everyone!
```

**Fix**: Use `Object.freeze` for configuration singletons.

---

## Best Practices

1. **Prefer ES module singletons** over class-based singletons with static instance checking. They are simpler and idiomatic in modern JavaScript.

2. **Freeze configuration singletons** with `Object.freeze` (deeply if needed) to prevent accidental mutations.

3. **Add a reset method** for testing. Name it obviously (like `__resetForTesting`) so it is not called in production.

4. **Use dependency injection** alongside singletons. Import the singleton in your entry point and pass it to modules that need it.

5. **Be careful with SSR**. In server-side rendering, singletons persist across requests. Use per-request state instead.

6. **Keep singletons small**. A singleton should have a focused responsibility. If it is growing beyond one concern, split it into multiple singletons.

7. **Document that something is a singleton**. Future developers need to know they are sharing state.

---

## Quick Summary

The Singleton Pattern ensures exactly one instance of an object exists across your application.

```
  Singleton Creation Methods:
  ───────────────────────────

  1. ES Module Export (simplest, recommended)
     const instance = new MyClass();
     export default instance;

  2. Object.freeze (for immutable config)
     export default Object.freeze({ key: 'value' });

  3. Class with Static Instance (explicit control)
     class MyClass {
       constructor() {
         if (MyClass.instance) return MyClass.instance;
         MyClass.instance = this;
       }
     }

  Biggest Pitfall: Testing
  ─────────────────────────
  Solution: Reset methods + dependency injection
```

---

## Key Points

- The **Singleton Pattern** restricts a class or module to exactly one instance
- **ES modules are natural singletons** because they are evaluated once and cached by the module system
- **Object.freeze** makes a singleton immutable, but it is shallow -- use deep freeze for nested objects
- **Singletons make testing harder** because state leaks between tests. Always add a reset method
- **Dependency injection** is the antidote to tight singleton coupling -- pass the instance instead of importing it directly
- Real-world singletons include **loggers**, **auth stores**, **theme managers**, **config objects**, and **caches**
- **Do not use singletons in SSR** without per-request isolation
- **Stateless utility functions** do not need to be singletons -- just export them normally

---

## Practice Questions

1. What happens if two files both call `new AuthService()` instead of importing a shared instance? How does the Singleton Pattern prevent this?

2. Why does `Object.freeze` only freeze the top level of an object? Write a function that deeply freezes an object.

3. Explain why singletons are problematic in server-side rendering. What happens when two different users' requests share the same singleton?

4. How does dependency injection help solve the testing problem with singletons? Give a concrete example.

5. When should you use a plain exported object versus a class-based singleton? What are the trade-offs?

---

## Exercises

### Exercise 1: Build a Feature Flags Singleton

Create a `FeatureFlags` singleton that:
- Stores a set of feature flags (key-value pairs where values are booleans)
- Has a method to check if a feature is enabled
- Has a method to enable or disable a feature
- Uses `Object.freeze` on the initial default flags
- Allows overrides at runtime (hint: keep defaults frozen but store overrides separately)
- Includes a `__resetForTesting` method

Test it by enabling a feature in one file and checking it from another.

### Exercise 2: Singleton with Lazy Initialization

Sometimes you do not want to create the singleton until it is first needed (lazy initialization). Build a `DatabasePool` singleton where:
- The connection pool is not created until `getPool()` is called for the first time
- Subsequent calls to `getPool()` return the same pool
- The pool has `connect()`, `query()`, and `disconnect()` methods
- Track and display the total number of queries across the application

### Exercise 3: Convert Singleton to Dependency Injection

Take this tightly coupled code and refactor it to use dependency injection:

```javascript
import logger from './logger.js';
import authStore from './auth-store.js';

function fetchUserProfile(userId) {
  logger.info(`Fetching profile for ${userId}`);
  const token = authStore.getToken();
  // ... fetch logic
}
```

Make `fetchUserProfile` testable without importing any singletons.

---

## What Is Next?

You now know how to ensure exactly one instance exists. But here is the next question: what happens when that single instance changes, and other parts of your application need to know about it?

The theme manager and auth store examples in this chapter already hinted at the answer: subscribers that listen for changes. That is the Observer Pattern, and it is one of the most important patterns in all of frontend development. Chapter 4 dives deep into it.
