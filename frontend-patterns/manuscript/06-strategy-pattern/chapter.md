# Chapter 6: Strategy Pattern

## What You Will Learn

- What the Strategy Pattern is and why it exists
- How to replace messy if/else chains with interchangeable behaviors
- How to implement strategies as plain functions in JavaScript
- How to use the Strategy Pattern with React components
- Real-world applications: form validation, pricing, sorting, and API requests

## Why This Chapter Matters

Picture a GPS navigation app. You type in a destination and it gives you a route. But what kind of route? The fastest route avoids traffic. The shortest route saves fuel. The scenic route goes past beautiful views. The walking route avoids highways entirely.

Each routing method is a **strategy**. The app does not care which one you pick. It just says, "Give me a strategy, and I will follow it." You can swap strategies at any time without rewriting the navigation engine.

That is the Strategy Pattern. It takes a chunk of behavior -- an algorithm, a rule, a method of doing something -- and packages it so you can swap it in and out like changing a battery. No giant if/else chains. No rewriting your core logic. Just clean, interchangeable pieces.

In frontend development, you run into this constantly. Payment processing with multiple methods. Form validation with different rules for different fields. Sorting data in different orders. Fetching data from REST or GraphQL. Every one of these is a perfect fit for the Strategy Pattern.

---

## The Problem: if/else Chains That Never Stop Growing

Let us start with a real scenario. You are building an e-commerce checkout page. Customers can pay with a credit card, PayPal, or cryptocurrency.

### The Painful Way (Before the Pattern)

```javascript
// payment-processor.js -- the messy version

function processPayment(method, amount, details) {
  if (method === 'credit-card') {
    // Validate card number
    if (!details.cardNumber || details.cardNumber.length !== 16) {
      throw new Error('Invalid card number');
    }
    // Validate expiry
    if (!details.expiry) {
      throw new Error('Expiry date required');
    }
    // Process credit card payment
    console.log(`Charging $${amount} to card ending in ${details.cardNumber.slice(-4)}`);
    // ... credit card API call logic
    return { success: true, transactionId: 'CC-' + Date.now() };

  } else if (method === 'paypal') {
    // Validate PayPal email
    if (!details.email || !details.email.includes('@')) {
      throw new Error('Invalid PayPal email');
    }
    // Process PayPal payment
    console.log(`Charging $${amount} via PayPal to ${details.email}`);
    // ... PayPal API call logic
    return { success: true, transactionId: 'PP-' + Date.now() };

  } else if (method === 'crypto') {
    // Validate wallet address
    if (!details.walletAddress || details.walletAddress.length < 26) {
      throw new Error('Invalid wallet address');
    }
    // Process crypto payment
    console.log(`Sending $${amount} to wallet ${details.walletAddress.slice(0, 8)}...`);
    // ... crypto API call logic
    return { success: true, transactionId: 'CR-' + Date.now() };

  } else {
    throw new Error(`Unknown payment method: ${method}`);
  }
}
```

**Output when calling `processPayment('credit-card', 49.99, { cardNumber: '4111111111111234', expiry: '12/25' })`:**
```
Charging $49.99 to card ending in 1234
// Returns: { success: true, transactionId: 'CC-1698765432100' }
```

### What Is Wrong Here?

Look at that function. It is already 40 lines long and it only handles three payment methods. What happens when the business says:

- "Add Apple Pay"
- "Add bank transfer"
- "Add gift cards"
- "Add buy-now-pay-later"

Every new method means diving into this function, adding another `else if` block, and hoping you do not break the existing ones. This violates the **Open/Closed Principle**: software should be open for extension but closed for modification.

```
  ┌─────────────────────────────────────────────┐
  │          processPayment() Function           │
  │                                              │
  │  if (credit-card) {                          │
  │    ... 15 lines of credit card logic ...     │
  │  } else if (paypal) {                        │
  │    ... 12 lines of PayPal logic ...          │
  │  } else if (crypto) {                        │
  │    ... 13 lines of crypto logic ...          │
  │  } else if (apple-pay) {     <── NEW         │
  │    ... more lines ...                        │
  │  } else if (bank-transfer) { <── NEW         │
  │    ... more lines ...                        │
  │  } else if (gift-card) {     <── NEW         │
  │    ... more lines ...                        │
  │  }                                           │
  │                                              │
  │  This function grows FOREVER                 │
  └─────────────────────────────────────────────┘
```

---

## The Solution: Strategy Pattern

The Strategy Pattern says: **extract each algorithm into its own function (or class), and let the caller pick which one to use.**

Think of it like a toolbox. Instead of one giant multi-tool that tries to be a hammer, screwdriver, and wrench all at once, you have separate tools. You pick the right one for the job.

```
  ┌─────────────────────────────────────────────────┐
  │                PaymentProcessor                  │
  │                                                  │
  │  "I don't know HOW to process payments.          │
  │   I just call whatever strategy you give me."    │
  │                                                  │
  │  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
  │  │ Credit   │  │ PayPal   │  │ Crypto   │       │
  │  │ Card     │  │ Strategy │  │ Strategy │       │
  │  │ Strategy │  │          │  │          │       │
  │  └──────────┘  └──────────┘  └──────────┘       │
  │                                                  │
  │  Want to add Apple Pay?                          │
  │  Just create a new strategy. Done.               │
  └─────────────────────────────────────────────────┘
```

### The Strategy Interface

In TypeScript, you would define an interface. In plain JavaScript, you follow a convention: every strategy function has the same signature.

```javascript
// The "interface" -- every strategy must follow this shape:
//
// function strategyName(amount, details) {
//   // 1. Validate the details
//   // 2. Process the payment
//   // 3. Return { success, transactionId }
// }
```

### The Clean Way (After the Pattern)

```javascript
// strategies/credit-card.js
function creditCardStrategy(amount, details) {
  // Line 1: Validate the card number exists and is 16 digits
  if (!details.cardNumber || details.cardNumber.length !== 16) {
    throw new Error('Invalid card number');
  }
  // Line 2: Validate the expiry date exists
  if (!details.expiry) {
    throw new Error('Expiry date required');
  }
  // Line 3: Process the payment
  console.log(`Charging $${amount} to card ending in ${details.cardNumber.slice(-4)}`);
  // Line 4: Return a result with a unique transaction ID
  return { success: true, transactionId: 'CC-' + Date.now() };
}

// strategies/paypal.js
function paypalStrategy(amount, details) {
  if (!details.email || !details.email.includes('@')) {
    throw new Error('Invalid PayPal email');
  }
  console.log(`Charging $${amount} via PayPal to ${details.email}`);
  return { success: true, transactionId: 'PP-' + Date.now() };
}

// strategies/crypto.js
function cryptoStrategy(amount, details) {
  if (!details.walletAddress || details.walletAddress.length < 26) {
    throw new Error('Invalid wallet address');
  }
  console.log(`Sending $${amount} to wallet ${details.walletAddress.slice(0, 8)}...`);
  return { success: true, transactionId: 'CR-' + Date.now() };
}
```

Now the processor is tiny:

```javascript
// payment-processor.js -- the clean version

// Line 1: A map that connects method names to their strategy functions
const paymentStrategies = {
  'credit-card': creditCardStrategy,
  'paypal': paypalStrategy,
  'crypto': cryptoStrategy,
};

// Line 2: The processor just looks up and calls the right strategy
function processPayment(method, amount, details) {
  // Line 3: Find the strategy for this payment method
  const strategy = paymentStrategies[method];

  // Line 4: If no strategy exists, throw a clear error
  if (!strategy) {
    throw new Error(`Unknown payment method: ${method}`);
  }

  // Line 5: Delegate to the strategy -- the processor does not care HOW it works
  return strategy(amount, details);
}
```

**Output is identical:**
```
processPayment('credit-card', 49.99, { cardNumber: '4111111111111234', expiry: '12/25' });
// Charging $49.99 to card ending in 1234
// Returns: { success: true, transactionId: 'CC-1698765432100' }

processPayment('paypal', 29.99, { email: 'user@example.com' });
// Charging $29.99 via PayPal to user@example.com
// Returns: { success: true, transactionId: 'PP-1698765432200' }
```

### Adding a New Payment Method

Now the magic. Your boss says "Add Apple Pay." Watch how easy this is:

```javascript
// strategies/apple-pay.js -- a brand new file, no existing code touched

function applePayStrategy(amount, details) {
  if (!details.deviceToken) {
    throw new Error('Apple Pay device token required');
  }
  console.log(`Processing $${amount} via Apple Pay`);
  return { success: true, transactionId: 'AP-' + Date.now() };
}

// Just register it:
paymentStrategies['apple-pay'] = applePayStrategy;
```

That is it. No modifying the processor. No touching credit card logic. No risk of breaking PayPal. You **extended** the system without **modifying** it.

---

## Before vs After: Side by Side

```
  BEFORE (if/else)                    AFTER (Strategy Pattern)
  ─────────────────                   ──────────────────────────

  processPayment()                    processPayment()
  ┌──────────────────┐                ┌──────────────────┐
  │ if credit-card   │                │ strategy = lookup │
  │   ... 15 lines   │                │ return strategy() │
  │ else if paypal   │                └──────────────────┘
  │   ... 12 lines   │                        │
  │ else if crypto   │                ┌───────┼───────┐
  │   ... 13 lines   │                │       │       │
  │ else if new...   │                ▼       ▼       ▼
  │   ... more lines │              CC()   PayPal() Crypto()
  └──────────────────┘              (own    (own     (own
                                    file)   file)    file)
  Adding new method:
  - Edit the big function            Adding new method:
  - Risk breaking others             - Create new file
  - Hard to test                     - Register it
                                     - Nothing else changes
```

---

## Function-Based Strategies in JavaScript

JavaScript makes the Strategy Pattern incredibly natural because functions are first-class citizens. You can store them in variables, pass them as arguments, and put them in objects.

### Pattern 1: Strategy Map (Object Lookup)

This is the most common approach.

```javascript
// Define strategies as an object map
const sortStrategies = {
  // Each key is a strategy name, each value is a comparison function
  'price-low-high': (a, b) => a.price - b.price,
  'price-high-low': (a, b) => b.price - a.price,
  'name-a-z': (a, b) => a.name.localeCompare(b.name),
  'name-z-a': (a, b) => b.name.localeCompare(a.name),
  'newest': (a, b) => new Date(b.createdAt) - new Date(a.createdAt),
};

// The context function that uses a strategy
function sortProducts(products, strategyName) {
  const strategy = sortStrategies[strategyName];
  if (!strategy) {
    throw new Error(`Unknown sort strategy: ${strategyName}`);
  }
  // .slice() creates a copy so we don't mutate the original array
  return products.slice().sort(strategy);
}

// Usage
const products = [
  { name: 'Laptop', price: 999, createdAt: '2024-01-15' },
  { name: 'Mouse', price: 29, createdAt: '2024-03-01' },
  { name: 'Keyboard', price: 79, createdAt: '2024-02-10' },
];

console.log(sortProducts(products, 'price-low-high'));
// Output:
// [
//   { name: 'Mouse', price: 29, createdAt: '2024-03-01' },
//   { name: 'Keyboard', price: 79, createdAt: '2024-02-10' },
//   { name: 'Laptop', price: 999, createdAt: '2024-01-15' }
// ]

console.log(sortProducts(products, 'name-a-z'));
// Output:
// [
//   { name: 'Keyboard', price: 79, createdAt: '2024-02-10' },
//   { name: 'Laptop', price: 999, createdAt: '2024-01-15' },
//   { name: 'Mouse', price: 29, createdAt: '2024-03-01' }
// ]
```

**Line-by-line breakdown:**

- **Line 1-7**: Each sorting strategy is a comparison function. JavaScript's `.sort()` method expects a function that takes two items and returns a number (negative, zero, or positive).
- **`price-low-high`**: Subtracting `a.price - b.price` puts smaller prices first.
- **`name-a-z`**: `localeCompare` compares strings alphabetically, respecting locale rules.
- **`sortProducts` function**: It looks up the strategy by name, copies the array with `.slice()`, and sorts the copy.

### Pattern 2: Strategy as a Function Argument

Sometimes you do not need a map. Just pass the strategy directly.

```javascript
// Instead of looking up from a map, accept the function directly
function processData(data, transformStrategy) {
  return data.map(transformStrategy);
}

// Define strategies
const toUpperCase = (item) => ({ ...item, name: item.name.toUpperCase() });
const addTax = (item) => ({ ...item, price: item.price * 1.1 });
const formatCurrency = (item) => ({ ...item, display: `$${item.price.toFixed(2)}` });

// Use whichever strategy you need
const items = [
  { name: 'Widget', price: 10 },
  { name: 'Gadget', price: 25 },
];

console.log(processData(items, toUpperCase));
// Output:
// [
//   { name: 'WIDGET', price: 10 },
//   { name: 'GADGET', price: 25 }
// ]

console.log(processData(items, addTax));
// Output:
// [
//   { name: 'Widget', price: 11 },
//   { name: 'Gadget', price: 27.5 }
// ]
```

### Pattern 3: Class-Based Strategies

When strategies need internal state or multiple methods, classes work well.

```javascript
// Base "interface" -- not enforced in JS, but documents the contract
// Every strategy must have: validate(details), process(amount, details)

class CreditCardStrategy {
  constructor() {
    this.name = 'Credit Card';
    this.fee = 0.029; // 2.9% processing fee
  }

  validate(details) {
    if (!details.cardNumber || details.cardNumber.length !== 16) {
      return { valid: false, error: 'Card number must be 16 digits' };
    }
    return { valid: true };
  }

  process(amount, details) {
    const totalWithFee = amount + (amount * this.fee);
    console.log(`Charging $${totalWithFee.toFixed(2)} (includes $${(amount * this.fee).toFixed(2)} fee)`);
    return { success: true, charged: totalWithFee };
  }
}

class PayPalStrategy {
  constructor() {
    this.name = 'PayPal';
    this.fee = 0.035; // 3.5% processing fee
  }

  validate(details) {
    if (!details.email || !details.email.includes('@')) {
      return { valid: false, error: 'Valid email required' };
    }
    return { valid: true };
  }

  process(amount, details) {
    const totalWithFee = amount + (amount * this.fee);
    console.log(`Sending $${totalWithFee.toFixed(2)} via PayPal to ${details.email}`);
    return { success: true, charged: totalWithFee };
  }
}

// The context class
class PaymentProcessor {
  constructor(strategy) {
    this.strategy = strategy; // Store the current strategy
  }

  setStrategy(strategy) {
    this.strategy = strategy; // Swap strategy at runtime
  }

  checkout(amount, details) {
    // Step 1: Validate using the strategy's own rules
    const validation = this.strategy.validate(details);
    if (!validation.valid) {
      throw new Error(validation.error);
    }

    // Step 2: Process using the strategy
    return this.strategy.process(amount, details);
  }
}

// Usage
const processor = new PaymentProcessor(new CreditCardStrategy());
processor.checkout(100, { cardNumber: '4111111111111234', expiry: '12/25' });
// Output: Charging $102.90 (includes $2.90 fee)

// Swap strategy at runtime -- no new processor needed
processor.setStrategy(new PayPalStrategy());
processor.checkout(100, { email: 'user@example.com' });
// Output: Sending $103.50 via PayPal to user@example.com
```

---

## Real-World Use Case 1: Form Validation Strategies

Forms have different validation rules for different fields. An email field needs an `@` sign. A password needs a minimum length. A phone number needs only digits.

```javascript
// validation-strategies.js

// Each strategy takes a value and returns { valid, error? }
const validationStrategies = {
  required: (value) => ({
    valid: value !== null && value !== undefined && value.trim() !== '',
    error: 'This field is required',
  }),

  email: (value) => ({
    valid: /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
    error: 'Please enter a valid email address',
  }),

  minLength: (min) => (value) => ({
    // This is a factory that returns a strategy
    valid: value.length >= min,
    error: `Must be at least ${min} characters`,
  }),

  maxLength: (max) => (value) => ({
    valid: value.length <= max,
    error: `Must be no more than ${max} characters`,
  }),

  pattern: (regex, message) => (value) => ({
    valid: regex.test(value),
    error: message,
  }),

  matchField: (fieldName, formValues) => (value) => ({
    valid: value === formValues[fieldName],
    error: `Must match ${fieldName}`,
  }),
};

// A validator that runs multiple strategies on a single field
function validateField(value, strategies) {
  for (const strategy of strategies) {
    const result = strategy(value);
    if (!result.valid) {
      return result; // Return the first error found
    }
  }
  return { valid: true };
}

// Define validation rules for a signup form
const signupRules = {
  username: [
    validationStrategies.required,
    validationStrategies.minLength(3),
    validationStrategies.maxLength(20),
    validationStrategies.pattern(/^[a-zA-Z0-9_]+$/, 'Only letters, numbers, and underscores'),
  ],
  email: [
    validationStrategies.required,
    validationStrategies.email,
  ],
  password: [
    validationStrategies.required,
    validationStrategies.minLength(8),
    validationStrategies.pattern(/[A-Z]/, 'Must contain at least one uppercase letter'),
    validationStrategies.pattern(/[0-9]/, 'Must contain at least one number'),
  ],
};

// Validate the form
function validateForm(formValues, rules) {
  const errors = {};

  for (const [field, strategies] of Object.entries(rules)) {
    const result = validateField(formValues[field] || '', strategies);
    if (!result.valid) {
      errors[field] = result.error;
    }
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors,
  };
}

// Usage
const formData = {
  username: 'jo',
  email: 'not-an-email',
  password: 'short',
};

console.log(validateForm(formData, signupRules));
// Output:
// {
//   valid: false,
//   errors: {
//     username: 'Must be at least 3 characters',
//     email: 'Please enter a valid email address',
//     password: 'Must be at least 8 characters'
//   }
// }

const goodData = {
  username: 'john_doe',
  email: 'john@example.com',
  password: 'SecurePass1',
};

console.log(validateForm(goodData, signupRules));
// Output:
// { valid: true, errors: {} }
```

### Using Validation Strategies in React

```jsx
// useFormValidation.js -- a custom hook
import { useState, useCallback } from 'react';

function useFormValidation(rules) {
  const [errors, setErrors] = useState({});

  const validate = useCallback((fieldName, value) => {
    const fieldRules = rules[fieldName];
    if (!fieldRules) return true;

    for (const strategy of fieldRules) {
      const result = strategy(value);
      if (!result.valid) {
        setErrors(prev => ({ ...prev, [fieldName]: result.error }));
        return false;
      }
    }

    // Clear error if validation passes
    setErrors(prev => {
      const next = { ...prev };
      delete next[fieldName];
      return next;
    });
    return true;
  }, [rules]);

  const validateAll = useCallback((formValues) => {
    const newErrors = {};
    let isValid = true;

    for (const [field, strategies] of Object.entries(rules)) {
      for (const strategy of strategies) {
        const result = strategy(formValues[field] || '');
        if (!result.valid) {
          newErrors[field] = result.error;
          isValid = false;
          break; // Stop at first error per field
        }
      }
    }

    setErrors(newErrors);
    return isValid;
  }, [rules]);

  return { errors, validate, validateAll };
}

// SignupForm.jsx
function SignupForm() {
  const [values, setValues] = useState({
    username: '',
    email: '',
    password: '',
  });

  const { errors, validate, validateAll } = useFormValidation(signupRules);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setValues(prev => ({ ...prev, [name]: value }));
    validate(name, value); // Validate on change using the strategies
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateAll(values)) {
      console.log('Form is valid! Submitting...', values);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <input
          name="username"
          value={values.username}
          onChange={handleChange}
          placeholder="Username"
        />
        {errors.username && <span className="error">{errors.username}</span>}
      </div>
      <div>
        <input
          name="email"
          value={values.email}
          onChange={handleChange}
          placeholder="Email"
        />
        {errors.email && <span className="error">{errors.email}</span>}
      </div>
      <div>
        <input
          name="password"
          type="password"
          value={values.password}
          onChange={handleChange}
          placeholder="Password"
        />
        {errors.password && <span className="error">{errors.password}</span>}
      </div>
      <button type="submit">Sign Up</button>
    </form>
  );
}
```

---

## Real-World Use Case 2: Pricing Calculator

Different pricing models need different calculation strategies.

```javascript
// pricing-strategies.js

const pricingStrategies = {
  // Fixed price: everyone pays the same
  fixed: (basePrice, quantity) => {
    return basePrice * quantity;
  },

  // Tiered pricing: price drops as quantity increases
  tiered: (basePrice, quantity) => {
    if (quantity >= 100) return basePrice * 0.7 * quantity;  // 30% off
    if (quantity >= 50) return basePrice * 0.8 * quantity;   // 20% off
    if (quantity >= 10) return basePrice * 0.9 * quantity;   // 10% off
    return basePrice * quantity;                              // Full price
  },

  // Per-seat pricing: common in SaaS
  perSeat: (basePrice, quantity) => {
    const monthlyPerSeat = basePrice;
    return monthlyPerSeat * quantity;
  },

  // Usage-based: pay for what you use (like AWS)
  usageBased: (basePrice, quantity) => {
    const freeAllowance = 100;
    const billableUnits = Math.max(0, quantity - freeAllowance);
    return billableUnits * basePrice;
  },

  // Freemium: free up to a limit, then flat fee
  freemium: (basePrice, quantity) => {
    const freeLimit = 5;
    if (quantity <= freeLimit) return 0;
    return basePrice; // Flat fee for premium
  },
};

function calculatePrice(strategyName, basePrice, quantity) {
  const strategy = pricingStrategies[strategyName];
  if (!strategy) throw new Error(`Unknown pricing strategy: ${strategyName}`);
  return strategy(basePrice, quantity);
}

// Usage
console.log(calculatePrice('fixed', 10, 5));       // Output: 50
console.log(calculatePrice('tiered', 10, 50));      // Output: 400 (20% off)
console.log(calculatePrice('usageBased', 0.05, 250)); // Output: 7.5 (150 billable units)
console.log(calculatePrice('freemium', 29, 3));     // Output: 0 (within free limit)
console.log(calculatePrice('freemium', 29, 10));    // Output: 29 (premium)
```

---

## Real-World Use Case 3: API Request Strategies

Your app might talk to different backends or use different protocols.

```javascript
// api-strategies.js

const apiStrategies = {
  rest: async (endpoint, data) => {
    const response = await fetch(`/api/rest/${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  },

  graphql: async (endpoint, data) => {
    const query = data.query;
    const variables = data.variables || {};
    const response = await fetch('/api/graphql', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, variables }),
    });
    const result = await response.json();
    return result.data;
  },

  mock: async (endpoint, data) => {
    // For development and testing -- returns fake data
    console.log(`[MOCK] ${endpoint}`, data);
    return { id: 1, status: 'mock-response', ...data };
  },
};

class ApiClient {
  constructor(strategyName = 'rest') {
    this.strategy = apiStrategies[strategyName];
  }

  setStrategy(strategyName) {
    this.strategy = apiStrategies[strategyName];
  }

  async request(endpoint, data) {
    return this.strategy(endpoint, data);
  }
}

// Usage
const client = new ApiClient('rest');

// In production, use REST
await client.request('users', { name: 'Alice' });

// During development, switch to mock
client.setStrategy('mock');
await client.request('users', { name: 'Alice' });
// Output: [MOCK] users { name: 'Alice' }
// Returns: { id: 1, status: 'mock-response', name: 'Alice' }
```

---

## Real-World Use Case 4: Sorting Options in React

A product listing page with a sort dropdown.

```jsx
// SortableProductList.jsx
import { useState, useMemo } from 'react';

// Define sort strategies
const sortStrategies = {
  'relevance': (a, b) => b.relevanceScore - a.relevanceScore,
  'price-asc': (a, b) => a.price - b.price,
  'price-desc': (a, b) => b.price - a.price,
  'rating': (a, b) => b.rating - a.rating,
  'newest': (a, b) => new Date(b.createdAt) - new Date(a.createdAt),
  'name': (a, b) => a.name.localeCompare(b.name),
};

function SortableProductList({ products }) {
  const [sortBy, setSortBy] = useState('relevance');

  // useMemo so we only re-sort when products or sortBy changes
  const sortedProducts = useMemo(() => {
    const strategy = sortStrategies[sortBy];
    return [...products].sort(strategy);
  }, [products, sortBy]);

  return (
    <div>
      <div className="sort-controls">
        <label htmlFor="sort-select">Sort by: </label>
        <select
          id="sort-select"
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
        >
          <option value="relevance">Relevance</option>
          <option value="price-asc">Price: Low to High</option>
          <option value="price-desc">Price: High to Low</option>
          <option value="rating">Highest Rated</option>
          <option value="newest">Newest First</option>
          <option value="name">Name (A-Z)</option>
        </select>
      </div>

      <ul className="product-list">
        {sortedProducts.map(product => (
          <li key={product.id}>
            {product.name} - ${product.price} ({product.rating} stars)
          </li>
        ))}
      </ul>
    </div>
  );
}
```

**How it works:**
1. The `sortStrategies` object holds all sorting algorithms.
2. The `sortBy` state tracks which strategy is active.
3. When the user picks a different sort option, React re-renders with the new strategy.
4. `useMemo` prevents unnecessary re-sorting if nothing changed.

---

## When to Use the Strategy Pattern

| Situation | Use Strategy Pattern? |
|---|---|
| Multiple algorithms that do the same type of job | Yes |
| if/else or switch chains that pick behavior based on a type | Yes |
| Behavior needs to change at runtime (user picks a sort option) | Yes |
| You want to test each algorithm independently | Yes |
| You need to add new behaviors without modifying existing code | Yes |
| You only have one algorithm and it will never change | No |
| The logic is simple enough for a ternary or one-line if | No |
| The variations share almost all their code | Maybe -- consider template method |

---

## When NOT to Use the Strategy Pattern

1. **Only two simple cases**: If you just have `if (premium) { ... } else { ... }`, a strategy pattern is overkill.

2. **Strategies that are identical except for one value**: Use a parameter instead.

```javascript
// DON'T create separate strategies for this:
const add5 = (x) => x + 5;
const add10 = (x) => x + 10;
const add15 = (x) => x + 15;

// DO use a parameter:
const addN = (n) => (x) => x + n;
```

3. **Strategies need deep access to internal state**: If the strategy needs to reach inside the context object and poke around, you have a coupling problem that strategy alone will not fix.

---

## Common Mistakes

### Mistake 1: Strategies with Different Interfaces

```javascript
// WRONG -- these strategies have different signatures
const strategies = {
  email: (value) => { /* validates email */ },
  password: (value, minLength) => { /* needs extra param */ },
  phone: (value, countryCode, format) => { /* even more params */ },
};

// RIGHT -- use a consistent interface
const strategies = {
  email: (value, options) => { /* uses options if needed */ },
  password: (value, options) => { /* options.minLength */ },
  phone: (value, options) => { /* options.countryCode, options.format */ },
};
```

### Mistake 2: Forgetting the Fallback

```javascript
// WRONG -- crashes if strategy doesn't exist
function sort(items, strategyName) {
  return items.sort(strategies[strategyName]); // undefined if not found!
}

// RIGHT -- handle missing strategies
function sort(items, strategyName) {
  const strategy = strategies[strategyName];
  if (!strategy) {
    console.warn(`Unknown strategy "${strategyName}", using default`);
    return items.sort(strategies['default']);
  }
  return items.sort(strategy);
}
```

### Mistake 3: Too Many Strategies for Simple Differences

```javascript
// WRONG -- three strategies that only differ by one number
const smallDiscount = (price) => price * 0.95;
const mediumDiscount = (price) => price * 0.90;
const largeDiscount = (price) => price * 0.85;

// RIGHT -- one function with a parameter
const applyDiscount = (percentage) => (price) => price * (1 - percentage / 100);
// Usage: applyDiscount(5)(100) => 95
```

---

## Best Practices

1. **Keep strategies pure when possible.** Strategies that take input and return output (no side effects) are easiest to test and reason about.

2. **Give strategies a consistent interface.** Every strategy for the same job should accept the same arguments and return the same shape.

3. **Use a default strategy.** Always have a fallback so your code does not crash when an unknown strategy name appears.

4. **Name strategies clearly.** `priceLowToHigh` is better than `sort1`. `creditCardStrategy` is better than `strategy1`.

5. **Store strategies in a map for runtime selection.** This lets users (or configs) pick a strategy by name without if/else chains.

6. **Use factories for configurable strategies.** If a strategy needs configuration, return a function from a factory function.

```javascript
// Factory that creates a configured strategy
function createRetryStrategy(maxRetries, delayMs) {
  return async function retryStrategy(fn) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await fn();
      } catch (error) {
        if (attempt === maxRetries) throw error;
        await new Promise(r => setTimeout(r, delayMs * attempt));
      }
    }
  };
}

// Use the factory to create different retry behaviors
const aggressiveRetry = createRetryStrategy(5, 100);
const gentleRetry = createRetryStrategy(2, 1000);
```

---

## Quick Summary

The Strategy Pattern replaces conditional logic with interchangeable functions. Instead of a big if/else chain that picks behavior based on a type, you define each behavior as a separate function and let the caller choose which one to use. This makes your code easier to extend (add new strategies without changing existing code), easier to test (test each strategy in isolation), and easier to read (each strategy is a small, focused function).

```
  ┌─────────────┐       ┌─────────────┐
  │   Context    │       │  Strategy   │
  │              │──────>│  Interface  │
  │ Uses a       │       │             │
  │ strategy     │       │ execute()   │
  └─────────────┘       └──────┬──────┘
                               │
                 ┌─────────────┼─────────────┐
                 │             │             │
           ┌─────────┐  ┌─────────┐  ┌─────────┐
           │Strategy A│  │Strategy B│  │Strategy C│
           │          │  │          │  │          │
           │execute() │  │execute() │  │execute() │
           └──────────┘  └──────────┘  └──────────┘
```

---

## Key Points

- The Strategy Pattern encapsulates a family of algorithms and makes them interchangeable.
- In JavaScript, strategies are often plain functions stored in an object map.
- The "context" (the code that uses a strategy) does not know the details of how each strategy works.
- You can swap strategies at runtime -- the user picks a sort order, the system picks a pricing model.
- Strategies should share a consistent interface (same inputs, same output shape).
- The pattern follows the Open/Closed Principle: open for extension, closed for modification.
- Function-based strategies are preferred in JavaScript over class-based ones for simple cases.

---

## Practice Questions

1. You have a notification system that sends alerts via email, SMS, and push notification. Each channel has different formatting rules. How would you apply the Strategy Pattern? What would your strategy interface look like?

2. A colleague suggests using the Strategy Pattern for a function that calculates shipping cost, but there is only one shipping provider and the rules never change. Is this a good use of the pattern? Why or why not?

3. Look at this code. What problem does it have, and how would you fix it using the Strategy Pattern?

```javascript
function formatDate(date, format) {
  if (format === 'US') {
    return `${date.getMonth()+1}/${date.getDate()}/${date.getFullYear()}`;
  } else if (format === 'EU') {
    return `${date.getDate()}/${date.getMonth()+1}/${date.getFullYear()}`;
  } else if (format === 'ISO') {
    return date.toISOString().split('T')[0];
  } else if (format === 'relative') {
    const diff = Date.now() - date.getTime();
    const days = Math.floor(diff / 86400000);
    if (days === 0) return 'today';
    if (days === 1) return 'yesterday';
    return `${days} days ago`;
  }
}
```

4. What is the difference between the Strategy Pattern and simply passing a callback function? When does a callback become a strategy?

5. How does `Array.prototype.sort()` in JavaScript relate to the Strategy Pattern?

---

## Exercises

### Exercise 1: Text Formatter Strategies

Build a text formatting system with at least four strategies: `uppercase`, `lowercase`, `titleCase`, and `snakeCase`. Create a `formatText(text, strategyName)` function. Then add a fifth strategy (`camelCase`) without modifying any existing code.

**Hints:**
- Title case capitalizes the first letter of each word.
- Snake case replaces spaces with underscores and lowercases everything.
- Camel case removes spaces and capitalizes the first letter of each word except the first.

### Exercise 2: React Filtering Component

Create a React component that displays a list of movies. Add filter strategies: `all` (show everything), `highRated` (rating above 8), `recent` (released after 2020), and `classic` (released before 2000). Use a dropdown to switch between filters. The filter strategies should be defined outside the component.

### Exercise 3: Composable Strategies

Build a discount calculator that supports combining multiple strategies. For example, a customer might get a "loyalty discount" (10% off) AND a "bulk discount" (5% off for 10+ items) applied together. Create a `composeStrategies` function that takes multiple discount strategies and applies them in sequence.

**Hint:** Think about function composition. Each strategy takes a price and returns a new price. Composing them means piping the output of one into the input of the next.

---

## What Is Next?

You have learned how to swap algorithms at runtime with the Strategy Pattern. But what about traversing data? In the next chapter, we will explore the **Iterator Pattern** -- a way to walk through any collection (arrays, trees, paginated API results) with a consistent interface. You will learn about JavaScript's built-in iteration protocol, generators, and how to build custom iterables that make complex data structures feel as simple as a `for...of` loop.
