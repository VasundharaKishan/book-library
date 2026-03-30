# Chapter 9: The Decorator Pattern

## What You Will Learn

- What the Decorator pattern is and how it differs from the Proxy pattern
- How higher-order functions act as decorators in JavaScript
- How to build practical decorators: `withLogging`, `withRetry`, `withCache`
- How to compose multiple decorators together
- How decorators apply to React components and hooks
- When decorators help and when they add unnecessary complexity

## Why This Chapter Matters

Think of a plain donut. It tastes fine on its own. Now add chocolate glaze. Still a donut, but with extra behavior (chocolate). Add sprinkles on top of the glaze. Still a donut, still has chocolate, now with even more decoration.

You never changed the original donut. You **wrapped** it with additional layers. Each layer adds something new, and you can mix and match layers however you like.

The Decorator pattern works exactly this way. You take an existing function or object and wrap it with new behavior. The original stays unchanged. The wrapping is reusable. And you can stack decorators like layers on a donut.

This is one of the most practical patterns in frontend development. Need to add logging to a function? Decorate it. Need retry logic for an API call? Decorate it. Need caching? Decorate it. Need all three? Stack them.

---

## The Problem

You have a function that works well. Now you need to add cross-cutting concerns -- logging, error handling, caching, timing, authentication checks -- without modifying the original function.

```javascript
// A simple API function
async function fetchUser(id) {
  const response = await fetch(`/api/users/${id}`);
  return response.json();
}

// Now you need:
// - Logging of every call
// - Retry on failure
// - Caching of results
// - Timing of how long it takes

// Do you add all of this inside fetchUser?
// That turns 3 lines into 30 lines.
// And every other API function needs the same treatment.
```

---

## The Solution: Decorator Pattern

The Decorator pattern wraps an existing function or object with additional behavior. The wrapper has the same interface as the original, so callers do not know (or care) about the decoration.

```
Without decorators:
+--------------------+
| fetchUser          |
| - fetch logic      |
| - logging logic    |
| - retry logic      |
| - caching logic    |
| - timing logic     |
+--------------------+
Everything jammed into one function.

With decorators:
+---------------------------+
| withTiming                |
|  +----------------------+ |
|  | withCache             | |
|  |  +-----------------+  | |
|  |  | withRetry       |  | |
|  |  |  +------------+ |  | |
|  |  |  | withLogging| |  | |
|  |  |  |  +-------+ | |  | |
|  |  |  |  | fetch  | | |  | |
|  |  |  |  | User   | | |  | |
|  |  |  |  +-------+ | |  | |
|  |  |  +------------+ |  | |
|  |  +-----------------+  | |
|  +----------------------+ |
+---------------------------+
Each concern is a separate, reusable layer.
```

---

## Higher-Order Functions as Decorators

In JavaScript, functions are first-class citizens. A **higher-order function** (HOF) takes a function as an argument and returns a new function. This is the foundation of the Decorator pattern in JavaScript.

```javascript
// The simplest decorator
function shout(fn) {
  return function (...args) {
    const result = fn(...args);
    return typeof result === "string" ? result.toUpperCase() : result;
  };
}

function greet(name) {
  return `Hello, ${name}`;
}

const shoutGreet = shout(greet);

console.log(greet("Alice"));
// Output: Hello, Alice

console.log(shoutGreet("Alice"));
// Output: HELLO, ALICE
```

The original `greet` function is unchanged. `shoutGreet` is a decorated version. Same input, enhanced output.

---

## Decorator 1: withLogging

### Problem

You want to log every function call for debugging, but you do not want logging code inside your business logic.

### Before: Logging Inside Business Logic

```javascript
function calculateTotal(items) {
  console.log("[calculateTotal] called with:", items);
  const start = Date.now();

  const total = items.reduce((sum, item) => sum + item.price * item.qty, 0);

  console.log("[calculateTotal] returned:", total);
  console.log("[calculateTotal] took:", Date.now() - start, "ms");
  return total;
}
```

### After: Logging Decorator

```javascript
function withLogging(fn, label) {
  const name = label || fn.name || "anonymous";

  return function (...args) {
    console.log(`[${name}] called with:`, ...args);

    const result = fn.apply(this, args);

    if (result instanceof Promise) {
      return result.then((resolved) => {
        console.log(`[${name}] resolved:`, resolved);
        return resolved;
      }).catch((error) => {
        console.log(`[${name}] rejected:`, error.message);
        throw error;
      });
    }

    console.log(`[${name}] returned:`, result);
    return result;
  };
}

// Usage
function calculateTotal(items) {
  return items.reduce((sum, item) => sum + item.price * item.qty, 0);
}

const loggedCalculate = withLogging(calculateTotal);

loggedCalculate([
  { price: 10, qty: 2 },
  { price: 5, qty: 3 }
]);
// Output:
// [calculateTotal] called with: [{price: 10, qty: 2}, {price: 5, qty: 3}]
// [calculateTotal] returned: 35
```

The business logic stays clean. Logging is added from the outside.

### Real-World Use Case: Debugging API Calls

```javascript
async function fetchUser(id) {
  const response = await fetch(`/api/users/${id}`);
  if (!response.ok) throw new Error(`User ${id} not found`);
  return response.json();
}

async function fetchPosts(userId) {
  const response = await fetch(`/api/users/${userId}/posts`);
  return response.json();
}

// During development, add logging to all API calls
const api = {
  fetchUser: withLogging(fetchUser),
  fetchPosts: withLogging(fetchPosts)
};

// In production, use the originals
const api = {
  fetchUser,
  fetchPosts
};
```

---

## Decorator 2: withRetry

### Problem

Network requests fail. Servers return 500 errors. Connections drop. You need to retry failed operations, but retry logic is complex and should not be mixed into every function.

### Before: Retry Inside Business Logic

```javascript
async function fetchData(url) {
  let lastError;
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      lastError = error;
      console.log(`Attempt ${attempt} failed: ${error.message}`);
      if (attempt < 3) {
        await new Promise((r) => setTimeout(r, 1000 * attempt));
      }
    }
  }
  throw lastError;
}
```

### After: Retry Decorator

```javascript
function withRetry(fn, options = {}) {
  const {
    maxAttempts = 3,
    delay = 1000,
    backoff = "exponential", // "fixed" or "exponential"
    onRetry = () => {}
  } = options;

  return async function (...args) {
    let lastError;

    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        return await fn.apply(this, args);
      } catch (error) {
        lastError = error;

        if (attempt === maxAttempts) break;

        const waitTime =
          backoff === "exponential"
            ? delay * Math.pow(2, attempt - 1)
            : delay;

        onRetry({
          attempt,
          maxAttempts,
          error,
          waitTime
        });

        await new Promise((r) => setTimeout(r, waitTime));
      }
    }

    throw lastError;
  };
}

// Usage
async function fetchUser(id) {
  const response = await fetch(`/api/users/${id}`);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

const resilientFetchUser = withRetry(fetchUser, {
  maxAttempts: 3,
  delay: 1000,
  backoff: "exponential",
  onRetry: ({ attempt, maxAttempts, error, waitTime }) => {
    console.log(
      `Attempt ${attempt}/${maxAttempts} failed: ${error.message}. ` +
      `Retrying in ${waitTime}ms...`
    );
  }
});

// This will automatically retry up to 3 times
const user = await resilientFetchUser(42);
```

```
Retry with exponential backoff:

Attempt 1 --> FAIL --> wait 1s
Attempt 2 --> FAIL --> wait 2s
Attempt 3 --> FAIL --> throw error

                  time -->
    |-----|
    Att 1  1s wait
               |-----|
               Att 2  2s wait
                           |-----|
                           Att 3  give up
```

---

## Decorator 3: withCache

### Problem

The same function is called with the same arguments multiple times. Each call is expensive (network request, heavy computation). You want to cache results.

### Before: Caching Inside Function

```javascript
const cache = new Map();

async function fetchUserProfile(userId) {
  if (cache.has(userId)) {
    const entry = cache.get(userId);
    if (Date.now() - entry.timestamp < 60000) {
      return entry.data;
    }
  }

  const response = await fetch(`/api/users/${userId}`);
  const data = await response.json();
  cache.set(userId, { data, timestamp: Date.now() });
  return data;
}
```

### After: Caching Decorator

```javascript
function withCache(fn, options = {}) {
  const {
    ttl = 60000,      // Time to live in milliseconds
    maxSize = 100,    // Maximum cache entries
    keyFn = (...args) => JSON.stringify(args)
  } = options;

  const cache = new Map();

  function decorated(...args) {
    const key = keyFn(...args);

    // Check cache
    if (cache.has(key)) {
      const entry = cache.get(key);
      if (Date.now() - entry.timestamp < ttl) {
        return entry.value;
      }
      cache.delete(key); // Expired
    }

    // Call original function
    const result = fn.apply(this, args);

    // Handle async results
    if (result instanceof Promise) {
      return result.then((resolved) => {
        storeInCache(key, resolved);
        return resolved;
      });
    }

    storeInCache(key, result);
    return result;
  }

  function storeInCache(key, value) {
    // Evict oldest if at max size
    if (cache.size >= maxSize) {
      const firstKey = cache.keys().next().value;
      cache.delete(firstKey);
    }
    cache.set(key, { value, timestamp: Date.now() });
  }

  // Expose cache controls
  decorated.clearCache = () => cache.clear();
  decorated.cacheSize = () => cache.size;

  return decorated;
}

// Usage
async function fetchUser(id) {
  console.log(`Fetching user ${id} from API...`);
  const response = await fetch(`/api/users/${id}`);
  return response.json();
}

const cachedFetchUser = withCache(fetchUser, { ttl: 30000 });

await cachedFetchUser(1);
// Output: Fetching user 1 from API...

await cachedFetchUser(1);
// No output -- served from cache!

await cachedFetchUser(2);
// Output: Fetching user 2 from API...

console.log(cachedFetchUser.cacheSize());
// Output: 2

cachedFetchUser.clearCache();
```

---

## Composing Decorators

The real power of decorators is **composition**. You can stack multiple decorators to build complex behavior from simple pieces.

```javascript
// Each decorator does one thing
const resilientCachedLoggedFetchUser =
  withLogging(
    withRetry(
      withCache(fetchUser, { ttl: 30000 }),
      { maxAttempts: 3 }
    ),
    "fetchUser"
  );

// When called:
// 1. withLogging logs the call
// 2. withRetry handles failures
// 3. withCache checks the cache first
// 4. fetchUser makes the actual request (if not cached)
```

### A Compose Utility

Reading nested function calls is hard. A `compose` utility makes it cleaner:

```javascript
function compose(...decorators) {
  return function (fn) {
    return decorators.reduceRight(
      (decorated, decorator) => decorator(decorated),
      fn
    );
  };
}

// Usage
const enhance = compose(
  (fn) => withLogging(fn, "fetchUser"),
  (fn) => withRetry(fn, { maxAttempts: 3 }),
  (fn) => withCache(fn, { ttl: 30000 })
);

const enhancedFetchUser = enhance(fetchUser);
```

### A Pipeline Utility (Left to Right)

Some people prefer reading left to right:

```javascript
function pipe(...decorators) {
  return function (fn) {
    return decorators.reduce(
      (decorated, decorator) => decorator(decorated),
      fn
    );
  };
}

const enhance = pipe(
  (fn) => withCache(fn, { ttl: 30000 }),
  (fn) => withRetry(fn, { maxAttempts: 3 }),
  (fn) => withLogging(fn, "fetchUser")
);

const enhancedFetchUser = enhance(fetchUser);
```

```
Decorator composition (reading from inside out):

  withLogging( withRetry( withCache( fetchUser ) ) )
       |            |          |         |
       |            |          |    Original function
       |            |          |
       |            |    Adds caching layer
       |            |
       |      Adds retry layer
       |
  Adds logging layer

Call flow:
  caller --> logging --> retry --> cache --> fetchUser
  caller <-- logging <-- retry <-- cache <-- fetchUser
```

---

## Decorator 4: withTiming

A quick and useful decorator for performance monitoring:

```javascript
function withTiming(fn, label) {
  const name = label || fn.name || "anonymous";

  return async function (...args) {
    const start = performance.now();

    try {
      const result = await fn.apply(this, args);
      const duration = (performance.now() - start).toFixed(2);
      console.log(`[Timer] ${name} completed in ${duration}ms`);
      return result;
    } catch (error) {
      const duration = (performance.now() - start).toFixed(2);
      console.log(`[Timer] ${name} failed after ${duration}ms`);
      throw error;
    }
  };
}

// Usage
const timedFetch = withTiming(fetch, "fetch");
await timedFetch("https://api.example.com/data");
// Output: [Timer] fetch completed in 234.56ms
```

---

## Decorator 5: withDebounce

Prevent a function from being called too frequently:

```javascript
function withDebounce(fn, delay = 300) {
  let timeoutId;

  return function (...args) {
    clearTimeout(timeoutId);

    return new Promise((resolve) => {
      timeoutId = setTimeout(() => {
        resolve(fn.apply(this, args));
      }, delay);
    });
  };
}

// Usage: Search input that only fires after user stops typing
async function searchAPI(query) {
  const response = await fetch(`/api/search?q=${query}`);
  return response.json();
}

const debouncedSearch = withDebounce(searchAPI, 300);

// Called rapidly (e.g., user typing "react")
debouncedSearch("r");
debouncedSearch("re");
debouncedSearch("rea");
debouncedSearch("reac");
debouncedSearch("react");
// Only the last call ("react") actually fires, after 300ms of silence
```

---

## Decorators in React

### Decorating Event Handlers

```javascript
function preventDoubleClick(handler, delay = 1000) {
  let lastClick = 0;

  return function (...args) {
    const now = Date.now();
    if (now - lastClick < delay) return;
    lastClick = now;
    return handler.apply(this, args);
  };
}

function SubmitButton({ onSubmit }) {
  const safeSubmit = preventDoubleClick(onSubmit);

  return <button onClick={safeSubmit}>Submit Order</button>;
}
```

### Decorating Custom Hooks

```javascript
// A decorator for any async hook to add loading/error states
function withAsyncState(useDataHook) {
  return function (...args) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
      let cancelled = false;
      setLoading(true);

      useDataHook(...args)
        .then((result) => {
          if (!cancelled) {
            setData(result);
            setLoading(false);
          }
        })
        .catch((err) => {
          if (!cancelled) {
            setError(err);
            setLoading(false);
          }
        });

      return () => { cancelled = true; };
    }, args);

    return { data, loading, error };
  };
}
```

---

## Decorator vs Proxy: What Is the Difference?

These two patterns look similar but serve different purposes:

```
+------------------+----------------------------------+----------------------------+
| Aspect           | Proxy                            | Decorator                  |
+------------------+----------------------------------+----------------------------+
| Purpose          | Control ACCESS to an object      | Add BEHAVIOR to a function |
| Mechanism        | Intercepts operations            | Wraps with new function    |
| Interface        | Same as target (transparent)     | Same as original function  |
| Focus            | The object and its properties    | The function and its result|
| JS Support       | ES6 Proxy constructor            | Higher-order functions     |
| Use case         | Validation, access control       | Logging, retry, caching    |
+------------------+----------------------------------+----------------------------+
```

Simple rule: **Proxies control objects. Decorators enhance functions.**

---

## When to Use the Decorator Pattern

```
+-----------------------------------------------+
|           USE DECORATORS WHEN:                |
+-----------------------------------------------+
|                                               |
|  * You need to add cross-cutting concerns     |
|    (logging, timing, retry, caching)          |
|  * The same concern applies to many functions |
|  * You want to compose behaviors flexibly     |
|  * You want to toggle behavior on/off easily  |
|  * You need to keep business logic clean      |
|  * Different environments need different      |
|    behavior (dev vs production)               |
|                                               |
+-----------------------------------------------+

+-----------------------------------------------+
|       DO NOT USE DECORATORS WHEN:             |
+-----------------------------------------------+
|                                               |
|  * The function is only used in one place     |
|  * Adding the behavior inline is clearer      |
|  * The decorator stack gets too deep (3+)     |
|    and becomes hard to debug                  |
|  * The function signature changes with        |
|    decoration (breaks the pattern)            |
|  * Simple conditional logic would suffice     |
|                                               |
+-----------------------------------------------+
```

---

## Common Mistakes

### Mistake 1: Losing `this` Context

```javascript
// WRONG -- "this" is lost
function withLogging(fn) {
  return function (...args) {
    console.log("called");
    return fn(...args); // "this" is undefined!
  };
}

// CORRECT -- preserve "this"
function withLogging(fn) {
  return function (...args) {
    console.log("called");
    return fn.apply(this, args); // "this" is preserved
  };
}
```

### Mistake 2: Hiding the Original Function Name

```javascript
// WRONG -- debugger shows "anonymous"
function withLogging(fn) {
  return function (...args) {
    console.log(`${fn.name} called`);
    return fn.apply(this, args);
  };
}

// BETTER -- preserve the function name
function withLogging(fn) {
  const wrapper = function (...args) {
    console.log(`${fn.name} called`);
    return fn.apply(this, args);
  };
  Object.defineProperty(wrapper, "name", { value: fn.name });
  return wrapper;
}
```

### Mistake 3: Too Many Layers

```javascript
// TOO MANY DECORATORS -- hard to debug
const fn = withAuth(
  withLogging(
    withTiming(
      withRetry(
        withCache(
          withValidation(
            withThrottle(fetchUser)
          )
        )
      )
    )
  )
);

// When something goes wrong, which layer caused it?
// Keep decorator stacks to 2-3 layers maximum
```

### Mistake 4: Not Handling Both Sync and Async

```javascript
// WRONG -- only works for sync functions
function withLogging(fn) {
  return function (...args) {
    const result = fn.apply(this, args);
    console.log("Result:", result); // Logs a Promise object!
    return result;
  };
}

// CORRECT -- handles both sync and async
function withLogging(fn) {
  return function (...args) {
    const result = fn.apply(this, args);
    if (result instanceof Promise) {
      return result.then((val) => {
        console.log("Result:", val);
        return val;
      });
    }
    console.log("Result:", result);
    return result;
  };
}
```

---

## Best Practices

1. **Preserve the function interface** -- the decorated function should accept the same arguments and return the same type as the original.

2. **Preserve `this` context** -- always use `fn.apply(this, args)` or `fn.call(this, ...args)` inside decorators.

3. **Handle both sync and async** -- check if the result is a Promise and handle both cases.

4. **Keep decorators focused** -- one decorator, one concern. Do not build a "super decorator" that does everything.

5. **Limit decorator depth** -- stacking more than 3 decorators makes debugging difficult. If you need more, consider a different approach.

6. **Make decorators configurable** -- accept options objects so users can customize behavior.

---

## Quick Summary

The Decorator pattern wraps functions with additional behavior without modifying the original. Higher-order functions are the natural way to implement decorators in JavaScript. Common decorators include `withLogging`, `withRetry`, `withCache`, `withTiming`, and `withDebounce`. Decorators can be composed together, and the order of composition matters.

```
Original:     fetchUser(id)
Decorated:    withLogging(withRetry(withCache(fetchUser)))(id)

Same input, same output, extra behavior.
```

---

## Key Points

- The Decorator pattern adds behavior to functions without modifying them
- Higher-order functions are the JavaScript way to implement decorators
- Common decorators: `withLogging`, `withRetry`, `withCache`, `withTiming`, `withDebounce`
- Decorators can be composed (stacked) for complex behavior
- Always preserve `this` context with `fn.apply(this, args)`
- Handle both synchronous and asynchronous functions
- Keep decorator stacks shallow (2-3 layers) for debuggability
- Proxy controls access to objects; Decorator adds behavior to functions

---

## Practice Questions

1. What is the difference between the Decorator pattern and the Proxy pattern? When would you choose one over the other?

2. Why is it important to use `fn.apply(this, args)` inside a decorator instead of `fn(...args)`?

3. You have a `withRetry` decorator with exponential backoff. Explain the delay sequence for `maxAttempts: 4` with `delay: 1000`.

4. How would you compose `withLogging`, `withCache`, and `withRetry` so that logging happens on the outermost layer and caching on the innermost layer? Why does this order matter?

5. A colleague wants to add a decorator that changes the return type of a function (e.g., wraps the result in an object). Is this a good use of the Decorator pattern? Why or why not?

---

## Exercises

### Exercise 1: withThrottle Decorator

Create a `withThrottle` decorator that ensures a function is called at most once every N milliseconds. Unlike debounce (which waits for silence), throttle runs immediately and then ignores calls for the next N ms.

```javascript
function withThrottle(fn, interval = 300) {
  // Your code here
}

const throttledLog = withThrottle(console.log, 1000);
throttledLog("first");  // Logs immediately
throttledLog("second"); // Ignored (within 1000ms)
throttledLog("third");  // Ignored (within 1000ms)
// After 1000ms...
throttledLog("fourth"); // Logs
```

### Exercise 2: withAuth Decorator

Create a `withAuth` decorator that checks if a user is authenticated before calling the function. If not authenticated, it should throw an error or redirect.

```javascript
function withAuth(fn, getUser) {
  // Your code here
  // Hint: getUser() returns the current user or null
}

const getUser = () => ({ name: "Alice", role: "admin" }); // or null
const protectedFetch = withAuth(fetchSensitiveData, getUser);
```

### Exercise 3: Composing Decorators

Build a `createAPI` function that takes a base fetcher function and an options object, then applies the appropriate decorators based on the options.

```javascript
function createAPI(baseFetcher, options = {}) {
  // Your code here
  // Hint: Conditionally apply decorators based on options
}

const api = createAPI(fetchUser, {
  cache: { ttl: 30000 },
  retry: { maxAttempts: 3 },
  logging: true,
  timing: true
});
```

---

## What Is Next?

You now know how to add behavior to functions by wrapping them in decorators. The next chapter introduces the **Facade pattern**, which takes the opposite approach. Instead of adding complexity layer by layer, the Facade hides complexity behind a simple interface. You will learn how to build clean, simple APIs that shield callers from the messy details underneath.
