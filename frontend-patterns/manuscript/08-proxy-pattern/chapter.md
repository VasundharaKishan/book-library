# Chapter 8: The Proxy Pattern

## What You Will Learn

- What the Proxy pattern is and why it exists
- How to use the ES6 `Proxy` object and its traps
- How to build validation proxies that protect your data
- How to build logging proxies for debugging
- How to build caching proxies for performance
- How Vue.js uses proxies for reactivity
- When the Proxy pattern helps and when it hurts

## Why This Chapter Matters

Imagine you live in an apartment building with a doorman. You do not interact with every delivery person, solicitor, or visitor directly. The doorman stands between you and the outside world. He checks IDs, accepts packages, turns away salespeople, and logs who comes and goes.

You still get everything you need. But the doorman adds a layer of **control** between you and the world.

The Proxy pattern works exactly the same way. It places an object between the caller and the real object. This "middleman" can validate input, log access, cache results, control permissions, or add any behavior you want -- all without changing the original object.

In frontend development, proxies are everywhere. Vue 3 is built on them. State management libraries use them. Form validation, API wrappers, and lazy-loading systems all benefit from proxies.

This chapter teaches you to build and use proxies confidently.

---

## The Problem

You have an object. You want to control what happens when someone reads from it, writes to it, or interacts with it in any way. But you do not want to modify the object itself.

```javascript
// A simple user object
const user = {
  name: "Alice",
  age: 28,
  email: "alice@example.com",
  role: "admin"
};

// Anyone can do anything to this object
user.age = -5;        // Nonsense, but JavaScript allows it
user.name = "";       // Empty name? Sure, why not
user.role = "superadmin"; // Security? What security?
delete user.email;    // Gone forever

console.log(user);
// { name: '', age: -5, role: 'superadmin' }
```

You need a gatekeeper.

---

## The Solution: Proxy Pattern

The Proxy pattern creates a stand-in for another object. The proxy intercepts operations on the target object and can modify, validate, or extend the behavior.

```
+--------+     +-----------+     +--------+
| Caller | --> |   Proxy   | --> | Target |
+--------+     +-----------+     +--------+
                    |
              Intercepts:
              - get (reading)
              - set (writing)
              - delete
              - has (in operator)
              - apply (function call)
              - and more...
```

The caller talks to the proxy as if it were the real object. The proxy decides what actually happens.

---

## ES6 Proxy: The Built-in Gatekeeper

JavaScript has a built-in `Proxy` constructor since ES6. It takes two arguments:

1. **target** -- the real object you want to proxy
2. **handler** -- an object containing "traps" (interceptor functions)

### Your First Proxy

```javascript
const target = {
  greeting: "Hello",
  farewell: "Goodbye"
};

const handler = {
  get(target, property, receiver) {
    console.log(`Someone read "${property}"`);
    return target[property];
  }
};

const proxy = new Proxy(target, handler);

console.log(proxy.greeting);
// Output:
// Someone read "greeting"
// "Hello"

console.log(proxy.farewell);
// Output:
// Someone read "farewell"
// "Goodbye"

// The proxy looks and feels like the real object
console.log(proxy.greeting === target.greeting);
// Output: true
```

The `get` trap fires every time someone reads a property. The proxy is invisible to the caller -- it behaves like the real object.

---

## Common Proxy Traps

The `Proxy` handler supports many traps. Here are the ones you will use most:

```
+------------------+-----------------------------+----------------------------+
| Trap             | Intercepts                  | Example Use                |
+------------------+-----------------------------+----------------------------+
| get              | Reading a property          | Logging, defaults, caching |
| set              | Writing a property          | Validation, reactivity     |
| has              | The "in" operator           | Hiding private properties  |
| deleteProperty   | The "delete" operator       | Preventing deletion        |
| apply            | Function calls              | Timing, memoization        |
| construct        | The "new" operator          | Singletons, pooling        |
| ownKeys          | Object.keys(), for...in     | Filtering properties       |
+------------------+-----------------------------+----------------------------+
```

Let us explore the most important ones.

### The `get` Trap

Intercepts property reads.

```javascript
const defaults = {
  theme: "light",
  language: "en",
  fontSize: 16
};

const settings = {};

const settingsWithDefaults = new Proxy(settings, {
  get(target, property) {
    if (property in target) {
      return target[property];
    }
    return defaults[property];
  }
});

console.log(settingsWithDefaults.theme);
// Output: "light" (from defaults)

settingsWithDefaults.theme = "dark";
console.log(settingsWithDefaults.theme);
// Output: "dark" (from settings, overrides default)

console.log(settingsWithDefaults.language);
// Output: "en" (still from defaults)
```

### The `set` Trap

Intercepts property writes. Must return `true` for success or `false` (which throws a `TypeError` in strict mode).

```javascript
const user = { name: "Alice", age: 28 };

const validatedUser = new Proxy(user, {
  set(target, property, value) {
    if (property === "age") {
      if (typeof value !== "number") {
        throw new TypeError("Age must be a number");
      }
      if (value < 0 || value > 150) {
        throw new RangeError("Age must be between 0 and 150");
      }
    }

    if (property === "name") {
      if (typeof value !== "string" || value.trim().length === 0) {
        throw new TypeError("Name must be a non-empty string");
      }
    }

    target[property] = value;
    return true;
  }
});

validatedUser.name = "Bob";       // Works fine
console.log(validatedUser.name);
// Output: "Bob"

try {
  validatedUser.age = -5;
} catch (error) {
  console.log(error.message);
  // Output: "Age must be between 0 and 150"
}

try {
  validatedUser.name = "";
} catch (error) {
  console.log(error.message);
  // Output: "Name must be a non-empty string"
}
```

### The `has` Trap

Intercepts the `in` operator. Useful for hiding "private" properties.

```javascript
const user = {
  name: "Alice",
  _password: "secret123",
  _token: "abc-xyz"
};

const safeUser = new Proxy(user, {
  has(target, property) {
    if (property.startsWith("_")) {
      return false; // Hide private properties
    }
    return property in target;
  }
});

console.log("name" in safeUser);
// Output: true

console.log("_password" in safeUser);
// Output: false (hidden!)

console.log("_token" in safeUser);
// Output: false (hidden!)
```

### The `deleteProperty` Trap

Prevents properties from being deleted.

```javascript
const config = {
  apiUrl: "https://api.example.com",
  timeout: 5000,
  retries: 3
};

const protectedConfig = new Proxy(config, {
  deleteProperty(target, property) {
    throw new Error(
      `Cannot delete config property "${property}". ` +
      `Configuration is immutable.`
    );
  }
});

try {
  delete protectedConfig.apiUrl;
} catch (error) {
  console.log(error.message);
  // Output: Cannot delete config property "apiUrl".
  //         Configuration is immutable.
}
```

---

## Pattern 1: Validation Proxy

### Problem

You receive data from user forms, API responses, or third-party libraries. You need to ensure the data meets your requirements before it enters your system.

### Before: Validation Scattered Everywhere

```javascript
// Validation logic is repeated everywhere
function updateUserName(user, newName) {
  if (typeof newName !== "string" || newName.trim() === "") {
    throw new Error("Invalid name");
  }
  user.name = newName;
}

function updateUserAge(user, newAge) {
  if (typeof newAge !== "number" || newAge < 0 || newAge > 150) {
    throw new Error("Invalid age");
  }
  user.age = newAge;
}

function updateUserEmail(user, newEmail) {
  if (!newEmail.includes("@")) {
    throw new Error("Invalid email");
  }
  user.email = newEmail;
}
```

### After: Centralized Validation Proxy

```javascript
function createValidatedObject(target, schema) {
  return new Proxy(target, {
    set(target, property, value) {
      const validator = schema[property];

      if (validator) {
        const result = validator(value);
        if (!result.valid) {
          throw new Error(
            `Invalid value for "${property}": ${result.message}`
          );
        }
      }

      target[property] = value;
      return true;
    }
  });
}

// Define validation rules in one place
const userSchema = {
  name: (value) => {
    if (typeof value !== "string" || value.trim() === "") {
      return { valid: false, message: "Must be a non-empty string" };
    }
    return { valid: true };
  },
  age: (value) => {
    if (typeof value !== "number" || value < 0 || value > 150) {
      return { valid: false, message: "Must be a number between 0 and 150" };
    }
    return { valid: true };
  },
  email: (value) => {
    if (typeof value !== "string" || !value.includes("@")) {
      return { valid: false, message: "Must be a valid email address" };
    }
    return { valid: true };
  }
};

const user = createValidatedObject({}, userSchema);

user.name = "Alice";   // Works
user.age = 28;         // Works
user.email = "a@b.com"; // Works

console.log(user);
// Output: { name: 'Alice', age: 28, email: 'a@b.com' }

try {
  user.age = -5;
} catch (e) {
  console.log(e.message);
  // Output: Invalid value for "age": Must be a number between 0 and 150
}
```

### Real-World Use Case: Form State Validation

```javascript
function createFormState(initialValues, validators) {
  const errors = {};
  const touched = {};

  const state = new Proxy(
    { ...initialValues },
    {
      set(target, field, value) {
        target[field] = value;
        touched[field] = true;

        // Run validation on every change
        if (validators[field]) {
          const error = validators[field](value);
          if (error) {
            errors[field] = error;
          } else {
            delete errors[field];
          }
        }

        return true;
      },
      get(target, property) {
        if (property === "$errors") return { ...errors };
        if (property === "$touched") return { ...touched };
        if (property === "$isValid") return Object.keys(errors).length === 0;
        return target[property];
      }
    }
  );

  return state;
}

// Usage
const form = createFormState(
  { username: "", password: "" },
  {
    username: (val) =>
      val.length < 3 ? "Username must be at least 3 characters" : null,
    password: (val) =>
      val.length < 8 ? "Password must be at least 8 characters" : null
  }
);

form.username = "ab";
console.log(form.$errors);
// Output: { username: 'Username must be at least 3 characters' }
console.log(form.$isValid);
// Output: false

form.username = "alice";
form.password = "secure1234";
console.log(form.$errors);
// Output: {}
console.log(form.$isValid);
// Output: true
```

---

## Pattern 2: Logging Proxy

### Problem

You need to debug which properties are being read or written, and when. Adding `console.log` everywhere clutters your code and is hard to clean up.

### Before: Manual Logging

```javascript
class UserService {
  getUser(id) {
    console.log(`[LOG] getUser called with id: ${id}`);
    const result = database.findUser(id);
    console.log(`[LOG] getUser returned:`, result);
    return result;
  }

  updateUser(id, data) {
    console.log(`[LOG] updateUser called with:`, id, data);
    const result = database.updateUser(id, data);
    console.log(`[LOG] updateUser returned:`, result);
    return result;
  }

  // Every method has the same logging boilerplate...
}
```

### After: Logging Proxy

```javascript
function createLoggingProxy(target, label = "Object") {
  return new Proxy(target, {
    get(target, property, receiver) {
      const value = Reflect.get(target, property, receiver);

      if (typeof value === "function") {
        return function (...args) {
          console.log(
            `[${label}] Called ${String(property)}(${
              args.map(a => JSON.stringify(a)).join(", ")
            })`
          );

          const result = value.apply(target, args);

          // Handle promises
          if (result instanceof Promise) {
            return result.then((resolved) => {
              console.log(
                `[${label}] ${String(property)} resolved:`,
                resolved
              );
              return resolved;
            });
          }

          console.log(`[${label}] ${String(property)} returned:`, result);
          return result;
        };
      }

      console.log(`[${label}] Read ${String(property)}:`, value);
      return value;
    },

    set(target, property, value) {
      console.log(
        `[${label}] Set ${String(property)}:`,
        target[property],
        "->",
        value
      );
      target[property] = value;
      return true;
    }
  });
}

// Usage
const calculator = {
  total: 0,
  add(n) {
    this.total += n;
    return this.total;
  },
  multiply(n) {
    this.total *= n;
    return this.total;
  }
};

const logged = createLoggingProxy(calculator, "Calc");

logged.add(5);
// Output: [Calc] Called add(5)
// Output: [Calc] add returned: 5

logged.multiply(3);
// Output: [Calc] Called multiply(3)
// Output: [Calc] multiply returned: 15

console.log(logged.total);
// Output: [Calc] Read total: 15
// Output: 15
```

You can turn logging on and off simply by swapping the proxy in and out. Zero changes to your actual business logic.

---

## Pattern 3: Caching Proxy

### Problem

You have expensive function calls -- API requests, heavy computations, database queries. The same inputs often produce the same outputs. You want to cache results without polluting the original function.

### Before: Caching Mixed with Logic

```javascript
const cache = {};

async function fetchUserProfile(userId) {
  // Caching logic mixed with business logic
  if (cache[userId] && Date.now() - cache[userId].timestamp < 60000) {
    return cache[userId].data;
  }

  const response = await fetch(`/api/users/${userId}`);
  const data = await response.json();

  cache[userId] = { data, timestamp: Date.now() };
  return data;
}
```

### After: Caching Proxy

```javascript
function createCachingProxy(fn, ttl = 60000) {
  const cache = new Map();

  return new Proxy(fn, {
    apply(target, thisArg, args) {
      const key = JSON.stringify(args);
      const cached = cache.get(key);

      if (cached && Date.now() - cached.timestamp < ttl) {
        console.log(`Cache HIT for args: ${key}`);
        return cached.result;
      }

      console.log(`Cache MISS for args: ${key}`);
      const result = target.apply(thisArg, args);

      // Handle promises
      if (result instanceof Promise) {
        return result.then((resolved) => {
          cache.set(key, { result: resolved, timestamp: Date.now() });
          return resolved;
        });
      }

      cache.set(key, { result, timestamp: Date.now() });
      return result;
    }
  });
}

// Usage with a pure function
function fibonacci(n) {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}

const cachedFib = createCachingProxy(fibonacci);

console.log(cachedFib(10));
// Output: Cache MISS for args: [10]
// Output: 55

console.log(cachedFib(10));
// Output: Cache HIT for args: [10]
// Output: 55

// Usage with an API function
async function fetchUser(id) {
  const res = await fetch(`/api/users/${id}`);
  return res.json();
}

const cachedFetchUser = createCachingProxy(fetchUser, 30000);

// First call hits the network
await cachedFetchUser(42);
// Output: Cache MISS for args: [42]

// Second call (within 30 seconds) uses cache
await cachedFetchUser(42);
// Output: Cache HIT for args: [42]
```

---

## Pattern 4: Access Control Proxy

### Problem

Different users have different permissions. You need to restrict what they can do with certain objects.

```javascript
function createAccessControlProxy(target, currentUser) {
  const permissions = {
    admin: ["read", "write", "delete"],
    editor: ["read", "write"],
    viewer: ["read"]
  };

  return new Proxy(target, {
    get(target, property) {
      const userPerms = permissions[currentUser.role] || [];

      if (!userPerms.includes("read")) {
        throw new Error(
          `User "${currentUser.name}" does not have read access`
        );
      }

      return target[property];
    },

    set(target, property, value) {
      const userPerms = permissions[currentUser.role] || [];

      if (!userPerms.includes("write")) {
        throw new Error(
          `User "${currentUser.name}" does not have write access`
        );
      }

      target[property] = value;
      return true;
    },

    deleteProperty(target, property) {
      const userPerms = permissions[currentUser.role] || [];

      if (!userPerms.includes("delete")) {
        throw new Error(
          `User "${currentUser.name}" does not have delete access`
        );
      }

      delete target[property];
      return true;
    }
  });
}

// Usage
const document = { title: "Secret Report", content: "Top secret..." };

const adminView = createAccessControlProxy(
  document,
  { name: "Alice", role: "admin" }
);

const viewerView = createAccessControlProxy(
  document,
  { name: "Bob", role: "viewer" }
);

console.log(viewerView.title);
// Output: "Secret Report" (read is allowed)

try {
  viewerView.title = "Changed!";
} catch (e) {
  console.log(e.message);
  // Output: User "Bob" does not have write access
}

adminView.title = "Updated Report";
// Works fine -- admin has write access
```

---

## How Vue 3 Uses Proxies for Reactivity

Vue 3's reactivity system is built entirely on ES6 Proxies. When you call `reactive()`, Vue wraps your object in a Proxy that tracks which properties are read (dependencies) and triggers re-renders when they change.

Here is a simplified version of how it works:

```javascript
// Simplified Vue 3 reactivity (conceptual)
let activeEffect = null;

function reactive(target) {
  const deps = new Map(); // property -> Set of effects

  return new Proxy(target, {
    get(target, property, receiver) {
      // Track: record which effect depends on this property
      if (activeEffect) {
        if (!deps.has(property)) {
          deps.set(property, new Set());
        }
        deps.get(property).add(activeEffect);
      }

      return Reflect.get(target, property, receiver);
    },

    set(target, property, value, receiver) {
      const oldValue = target[property];
      const result = Reflect.set(target, property, value, receiver);

      // Trigger: notify all effects that depend on this property
      if (oldValue !== value && deps.has(property)) {
        deps.get(property).forEach((effect) => effect());
      }

      return result;
    }
  });
}

function watchEffect(fn) {
  activeEffect = fn;
  fn(); // Run once to collect dependencies
  activeEffect = null;
}

// Usage (similar to Vue 3)
const state = reactive({ count: 0, message: "Hello" });

watchEffect(() => {
  console.log(`Count is: ${state.count}`);
});
// Output: Count is: 0

state.count = 1;
// Output: Count is: 1

state.count = 2;
// Output: Count is: 2

state.message = "World";
// No output! The effect only depends on "count"
```

```
How Vue 3 Reactivity Works (Simplified):

1. SETUP: Component uses reactive({count: 0})
              |
              v
2. PROXY: Wraps the object with get/set traps
              |
              v
3. RENDER: Component renders, reading state.count
              |
              v
4. TRACK: get trap records "render depends on count"
              |
              v
5. UPDATE: User clicks button, state.count = 1
              |
              v
6. TRIGGER: set trap sees count changed,
            re-runs the render function
              |
              v
7. RE-RENDER: Component updates in the DOM
```

This is why Vue 3 requires you to use `reactive()` or `ref()` -- without the Proxy wrapper, Vue cannot track changes.

---

## Proxy Pattern in React

React does not use proxies internally, but you can use them in your own code:

```javascript
import { useState, useCallback } from "react";

function useValidatedState(initialValue, validator) {
  const [value, setValue] = useState(initialValue);
  const [error, setError] = useState(null);

  const setValidatedValue = useCallback(
    (newValue) => {
      const validationError = validator(newValue);
      if (validationError) {
        setError(validationError);
        return false;
      }
      setError(null);
      setValue(newValue);
      return true;
    },
    [validator]
  );

  return [value, setValidatedValue, error];
}

// Usage in a component
function AgeInput() {
  const [age, setAge, error] = useValidatedState(0, (value) => {
    if (typeof value !== "number") return "Must be a number";
    if (value < 0 || value > 150) return "Must be between 0 and 150";
    return null;
  });

  return (
    <div>
      <input
        type="number"
        value={age}
        onChange={(e) => setAge(Number(e.target.value))}
      />
      {error && <span className="error">{error}</span>}
    </div>
  );
}
```

---

## Using Reflect with Proxy

The `Reflect` object is the companion to `Proxy`. It provides default behavior for each trap. Always use `Reflect` inside your traps to preserve the original behavior:

```javascript
const proxy = new Proxy(target, {
  get(target, property, receiver) {
    // Do your custom thing
    console.log(`Reading ${String(property)}`);

    // Then use Reflect for the default behavior
    return Reflect.get(target, property, receiver);
  },

  set(target, property, value, receiver) {
    // Do your custom thing
    console.log(`Writing ${String(property)} = ${value}`);

    // Then use Reflect for the default behavior
    return Reflect.set(target, property, value, receiver);
  }
});
```

Why `Reflect` instead of `target[property]`? Because `Reflect` correctly handles:
- Inherited properties
- Getters and setters
- The `receiver` (the correct `this` value)

---

## When to Use the Proxy Pattern

```
+-----------------------------------------------+
|           USE PROXY WHEN:                     |
+-----------------------------------------------+
|                                               |
|  * You need to validate data on assignment    |
|  * You need to log or monitor object access   |
|  * You need to cache expensive operations     |
|  * You need to control access permissions     |
|  * You need to add "virtual" properties       |
|  * You need to make objects reactive           |
|  * You want to intercept without modifying    |
|    the original object                        |
|                                               |
+-----------------------------------------------+

+-----------------------------------------------+
|       DO NOT USE PROXY WHEN:                  |
+-----------------------------------------------+
|                                               |
|  * Simple if/else checks would suffice        |
|  * Performance is critical (proxies add       |
|    overhead to every property access)         |
|  * You need to support IE11 (no polyfill)     |
|  * The object is only used in one place       |
|  * A simple wrapper function would work       |
|  * You are proxying objects in a tight loop   |
|                                               |
+-----------------------------------------------+
```

---

## Common Mistakes

### Mistake 1: Forgetting to Return `true` from `set`

```javascript
// WRONG -- causes TypeError in strict mode
const proxy = new Proxy({}, {
  set(target, prop, value) {
    target[prop] = value;
    // Missing return true!
  }
});

// CORRECT
const proxy = new Proxy({}, {
  set(target, prop, value) {
    target[prop] = value;
    return true; // Always return true from set
  }
});
```

### Mistake 2: Infinite Loops with `set`

```javascript
// WRONG -- infinite loop!
const proxy = new Proxy({}, {
  set(target, prop, value) {
    proxy[prop] = value; // Writing to proxy triggers set again!
    return true;
  }
});

// CORRECT
const proxy = new Proxy({}, {
  set(target, prop, value) {
    target[prop] = value; // Write to target, not proxy
    return true;
  }
});
```

### Mistake 3: Not Using Reflect

```javascript
// FRAGILE -- does not handle getters/setters correctly
const proxy = new Proxy(target, {
  get(target, prop) {
    return target[prop];
  }
});

// ROBUST -- handles all cases correctly
const proxy = new Proxy(target, {
  get(target, prop, receiver) {
    return Reflect.get(target, prop, receiver);
  }
});
```

### Mistake 4: Proxying Everything

```javascript
// OVER-ENGINEERED -- a simple function would be better
const addProxy = new Proxy(
  function add(a, b) { return a + b; },
  {
    apply(target, thisArg, args) {
      return target.apply(thisArg, args);
    }
  }
);

// Just use the function directly!
function add(a, b) { return a + b; }
```

---

## Best Practices

1. **Use `Reflect` in your traps** -- it preserves correct behavior for getters, setters, and inheritance.

2. **Keep traps focused** -- each proxy should do one thing well (validate OR log OR cache, not all three).

3. **Compose proxies if needed** -- wrap a proxy in another proxy for layered behavior.

4. **Be aware of performance** -- every property access through a proxy has overhead. Do not use proxies in performance-critical loops.

5. **Document proxy behavior** -- since proxies are invisible, other developers may not realize an object is proxied. Add comments or use clear naming conventions.

6. **Test proxy edge cases** -- test with `undefined` values, prototype chain lookups, `Symbol` properties, and `JSON.stringify`.

---

## Quick Summary

The Proxy pattern places a middleman between the caller and the real object. This middleman intercepts operations and can add validation, logging, caching, access control, or any other behavior without modifying the original object.

```
                           +-- Validation Proxy
                           |
Object  -->  Proxy  -->  --+-- Logging Proxy
                           |
                           +-- Caching Proxy
                           |
                           +-- Access Control Proxy
```

ES6 gave us a native `Proxy` constructor with traps for every operation. Vue 3 uses this for its entire reactivity system. The `Reflect` object provides default implementations for each trap.

---

## Key Points

- The Proxy pattern creates a stand-in that intercepts operations on a target object
- ES6 `Proxy` provides built-in support with traps for `get`, `set`, `has`, `deleteProperty`, `apply`, and more
- Validation proxies centralize data validation in one place
- Logging proxies add debugging without touching business logic
- Caching proxies store results of expensive operations
- Vue 3 reactivity is built on ES6 Proxies
- Always use `Reflect` inside trap handlers for correct behavior
- Proxies add overhead -- do not use them in performance-critical paths

---

## Practice Questions

1. What is the difference between a Proxy's `target` and `handler`? What role does each play?

2. Why should you return `true` from the `set` trap? What happens if you forget?

3. Explain how Vue 3 uses Proxies for reactivity. What happens in the `get` and `set` traps?

4. What is `Reflect` and why should you use it inside proxy traps instead of directly accessing `target[property]`?

5. A colleague suggests using a Proxy to validate a single form field that is only used in one component. Is this a good idea? Why or why not?

---

## Exercises

### Exercise 1: Negative Array Indexing

Create a proxy that allows negative indexing for arrays, like Python. `arr[-1]` should return the last element, `arr[-2]` the second-to-last, and so on.

```javascript
function createNegativeArray(arr) {
  // Your code here
  // Hint: Use the get trap
  // Hint: Check if the property is a negative number
}

const arr = createNegativeArray([10, 20, 30, 40, 50]);
console.log(arr[-1]); // Should output: 50
console.log(arr[-2]); // Should output: 40
console.log(arr[0]);  // Should output: 10
```

### Exercise 2: Read-Only Proxy

Create a proxy that makes any object completely read-only. It should throw an error if someone tries to write, delete, or define properties.

```javascript
function createReadOnly(target) {
  // Your code here
  // Hint: Use set, deleteProperty, and defineProperty traps
}

const config = createReadOnly({ apiKey: "abc123", timeout: 5000 });
console.log(config.apiKey);     // Should work: "abc123"
config.apiKey = "new";          // Should throw: "Cannot modify..."
delete config.timeout;          // Should throw: "Cannot delete..."
```

### Exercise 3: Observable Object

Create a proxy that lets you register "watchers" on specific properties. When those properties change, the watchers are called with the old and new values.

```javascript
function createObservable(target) {
  // Your code here
  // Hint: Store watchers in a Map
  // Hint: Add a $watch method via the get trap
}

const user = createObservable({ name: "Alice", age: 28 });

user.$watch("name", (oldVal, newVal) => {
  console.log(`Name changed from "${oldVal}" to "${newVal}"`);
});

user.name = "Bob";
// Should output: Name changed from "Alice" to "Bob"
```

---

## What Is Next?

Now that you know how to intercept and control access to objects with the Proxy pattern, the next chapter introduces the **Decorator pattern**. While the Proxy controls access to an existing object, the Decorator adds new behavior by wrapping functions or objects with additional functionality. You will learn how to build composable decorators like `withLogging`, `withRetry`, and `withCache` that stack on top of each other like layers of armor.
