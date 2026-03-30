# Chapter 24: Flux/Redux Pattern

## What You Will Learn

- What unidirectional data flow means and why it matters
- The Flux architecture: Actions, Dispatcher, Store, and View
- How Redux simplifies Flux with a single store and pure reducers
- Writing Redux code with Redux Toolkit (createSlice, configureStore)
- When Redux is overkill and what lighter alternatives exist
- How Zustand and Jotai compare to Redux
- Building a real-world e-commerce cart and multi-step wizard

## Why This Chapter Matters

Imagine a busy restaurant kitchen. Orders come in from multiple waiters, cooks work on different dishes, and food goes out to various tables. Without a clear system, chaos happens: wrong dishes, missed orders, cold food.

Now imagine the same kitchen with a single order ticket system. Every order goes through one window, gets processed in order, and comes out predictably. That is what Flux and Redux do for your application state.

As frontend applications grow, state management becomes the hardest problem. You have user data, UI state, server responses, form inputs, and navigation state all tangled together. When a bug appears, you cannot tell which piece of code changed which piece of state. Redux gives you a strict, predictable system where every state change is traceable.

---

## The Problem

Consider a social media dashboard. You have:
- A notification counter in the header
- A message list in the sidebar
- A post feed in the main area
- A user profile panel

When a new message arrives, the counter updates, the sidebar refreshes, and maybe the feed changes too. With two-way data binding, any component can change any state, and state changes can trigger more state changes:

```
TWO-WAY DATA FLOW (CHAOS)

  ┌──────────┐     ┌──────────┐     ┌──────────┐
  │  Model A │◄───►│  Model B │◄───►│  Model C │
  └────┬─────┘     └────┬─────┘     └────┬─────┘
       │▲               │▲               │▲
       ▼│               ▼│               ▼│
  ┌────┴─────┐     ┌────┴─────┐     ┌────┴─────┐
  │  View A  │◄───►│  View B  │◄───►│  View C  │
  └──────────┘     └──────────┘     └──────────┘

  Any view can change any model.
  Any model can change any other model.
  Result: unpredictable cascading updates.
```

```javascript
// Before: scattered state management
// Header.js
function Header() {
  const [notifications, setNotifications] = useState(0);

  // How does this sync with Sidebar?
  // Who updates this? Multiple places!
  useEffect(() => {
    api.onNewMessage(() => {
      setNotifications(n => n + 1);
    });
  }, []);

  return <div>Notifications: {notifications}</div>;
}

// Sidebar.js
function Sidebar() {
  const [messages, setMessages] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  // This count might disagree with Header's count!
  useEffect(() => {
    api.onNewMessage((msg) => {
      setMessages(prev => [...prev, msg]);
      setUnreadCount(c => c + 1);
    });
  }, []);

  return <div>Unread: {unreadCount}</div>;
}

// Both components listen independently.
// Counts can get out of sync.
// No single source of truth.
```

**Output (the bug):**
```
Header shows: Notifications: 5
Sidebar shows: Unread: 4
// They disagree! Which is correct?
```

---

## The Solution: Unidirectional Data Flow

### Flux Architecture

Facebook created Flux to solve this exact problem. The rule is simple: data flows in one direction only.

```
FLUX: UNIDIRECTIONAL DATA FLOW

  ┌──────────┐    ┌────────────┐    ┌─────────┐    ┌──────────┐
  │  Action  │───►│ Dispatcher │───►│  Store  │───►│   View   │
  └──────────┘    └────────────┘    └─────────┘    └────┬─────┘
       ▲                                                │
       │                                                │
       └────────────────────────────────────────────────┘
                    User interaction creates
                       a new Action
```

Think of it like an assembly line:

1. **Action**: A description of what happened. "User clicked Add to Cart" or "Server returned new messages." It is just a plain object with a `type` and some data.

2. **Dispatcher**: The traffic cop. It receives every action and sends it to every store. There is only one dispatcher per app.

3. **Store**: Holds the state and the logic to update it. When it gets an action from the dispatcher, it decides how to change its state.

4. **View**: React components. They read from stores and render UI. When a user clicks something, the view creates a new action, and the cycle repeats.

```javascript
// Flux Action
const addToCartAction = {
  type: 'ADD_TO_CART',
  payload: {
    productId: 42,
    name: 'Wireless Headphones',
    price: 79.99
  }
};

// Flux Dispatcher (simplified)
class Dispatcher {
  constructor() {
    this.callbacks = [];        // Line 1: Array of registered store callbacks
  }

  register(callback) {
    this.callbacks.push(callback); // Line 2: Stores register themselves
  }

  dispatch(action) {
    this.callbacks.forEach(cb => cb(action)); // Line 3: Send action to ALL stores
  }
}

const AppDispatcher = new Dispatcher();

// Flux Store (simplified)
class CartStore {
  constructor() {
    this.items = [];            // Line 4: Internal state
    this.listeners = [];        // Line 5: View callbacks

    AppDispatcher.register((action) => {  // Line 6: Register with dispatcher
      switch (action.type) {
        case 'ADD_TO_CART':
          this.items = [...this.items, action.payload]; // Line 7: Update state
          this.emitChange();    // Line 8: Notify views
          break;
        case 'REMOVE_FROM_CART':
          this.items = this.items.filter(
            item => item.productId !== action.payload.productId
          );
          this.emitChange();
          break;
      }
    });
  }

  getItems() {
    return this.items;          // Line 9: Views read state through methods
  }

  emitChange() {
    this.listeners.forEach(fn => fn()); // Line 10: Tell views to re-render
  }

  addChangeListener(fn) {
    this.listeners.push(fn);   // Line 11: Views subscribe to changes
  }
}
```

**Line-by-line explanation:**
- **Line 1**: The dispatcher keeps a list of all store callbacks
- **Line 2**: Each store registers itself with the dispatcher
- **Line 3**: When an action is dispatched, EVERY store gets notified
- **Lines 4-5**: Store holds both state and a list of subscribed views
- **Line 6**: Store registers its handler with the global dispatcher
- **Line 7**: State updates are immutable (new array, not push)
- **Line 8**: After updating, store tells all views to re-check
- **Line 9**: Views never access internal state directly; they call getter methods
- **Lines 10-11**: Simple pub/sub for view updates

---

## Redux: Flux Simplified

Redux took the Flux ideas and made three important simplifications:

1. **Single Store**: Instead of many stores, one store holds ALL state
2. **Pure Reducers**: Instead of store methods, pure functions handle state changes
3. **No Dispatcher**: The store itself handles dispatching

```
REDUX ARCHITECTURE

  ┌──────────────────────────────────────────────┐
  │                   STORE                       │
  │                                               │
  │   ┌─────────┐    dispatch    ┌────────────┐  │
  │   │  State  │◄──────────────│   Reducer   │  │
  │   │ (Tree)  │               │  (Pure Fn)  │  │
  │   └────┬────┘               └──────▲─────┘  │
  │        │                           │         │
  └────────┼───────────────────────────┼─────────┘
           │                           │
      subscribe                    dispatch
           │                           │
           ▼                           │
  ┌────────────────┐          ┌────────┴───────┐
  │   View (React) │─────────►│    Action       │
  │   Components   │  user    │  { type, data } │
  └────────────────┘  event   └────────────────┘
```

### Three Principles of Redux

```
┌─────────────────────────────────────────────────────┐
│           THE THREE PRINCIPLES OF REDUX              │
├─────────────────────────────────────────────────────┤
│                                                      │
│  1. SINGLE SOURCE OF TRUTH                           │
│     The entire app state lives in one object          │
│     in one store.                                     │
│                                                      │
│  2. STATE IS READ-ONLY                                │
│     The only way to change state is to dispatch       │
│     an action (a plain object describing what          │
│     happened).                                        │
│                                                      │
│  3. CHANGES ARE MADE WITH PURE FUNCTIONS              │
│     Reducers are pure functions that take              │
│     (previousState, action) and return newState.       │
│     No side effects. No mutations.                     │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Redux from Scratch (Plain JavaScript)

Before using any library, let us build a tiny Redux to understand the concept:

```javascript
// A minimal Redux implementation (about 25 lines)

function createStore(reducer, initialState) {
  let state = initialState;           // Line 1: Current state
  let listeners = [];                 // Line 2: Subscriber functions

  function getState() {
    return state;                     // Line 3: Read current state
  }

  function dispatch(action) {
    state = reducer(state, action);   // Line 4: Run reducer to get new state
    listeners.forEach(fn => fn());    // Line 5: Notify all subscribers
  }

  function subscribe(listener) {
    listeners.push(listener);         // Line 6: Add subscriber
    return () => {                    // Line 7: Return unsubscribe function
      listeners = listeners.filter(l => l !== listener);
    };
  }

  dispatch({ type: '@@INIT' });      // Line 8: Initialize with default state

  return { getState, dispatch, subscribe };
}
```

**Line-by-line explanation:**
- **Line 1**: State is just a variable inside a closure. Nobody can access it directly.
- **Line 2**: Array of functions to call when state changes.
- **Line 3**: `getState` is the ONLY way to read state.
- **Line 4**: The reducer receives current state and action, returns NEW state. The old state is never modified.
- **Line 5**: After state changes, every subscriber gets notified.
- **Line 6**: Components subscribe to know when to re-render.
- **Line 7**: Returns a cleanup function (like React's useEffect cleanup).
- **Line 8**: Dispatching a dummy action makes the reducer return its default state.

Now let us use it:

```javascript
// Step 1: Define a reducer (pure function)
function cartReducer(state = { items: [], total: 0 }, action) {
  switch (action.type) {
    case 'ADD_ITEM':
      const newItems = [...state.items, action.payload];
      const newTotal = newItems.reduce((sum, item) => sum + item.price, 0);
      return { items: newItems, total: newTotal };

    case 'REMOVE_ITEM':
      const filtered = state.items.filter(
        item => item.id !== action.payload.id
      );
      const filteredTotal = filtered.reduce(
        (sum, item) => sum + item.price, 0
      );
      return { items: filtered, total: filteredTotal };

    case 'CLEAR_CART':
      return { items: [], total: 0 };

    default:
      return state;  // Always return current state for unknown actions
  }
}

// Step 2: Create the store
const store = createStore(cartReducer);

// Step 3: Subscribe to changes
store.subscribe(() => {
  console.log('State changed:', store.getState());
});

// Step 4: Dispatch actions
store.dispatch({
  type: 'ADD_ITEM',
  payload: { id: 1, name: 'Laptop', price: 999 }
});
// Output: State changed: { items: [{ id: 1, name: 'Laptop', price: 999 }], total: 999 }

store.dispatch({
  type: 'ADD_ITEM',
  payload: { id: 2, name: 'Mouse', price: 29 }
});
// Output: State changed: { items: [...], total: 1028 }

store.dispatch({ type: 'CLEAR_CART' });
// Output: State changed: { items: [], total: 0 }
```

---

## Redux Toolkit: The Modern Way

Writing raw Redux involves a lot of boilerplate: action types as constants, action creator functions, switch statements in reducers, immutable update logic. Redux Toolkit (RTK) eliminates all of that.

### createSlice: Actions + Reducer in One

```javascript
// Before Redux Toolkit: verbose and error-prone

// action-types.js
const ADD_TO_CART = 'cart/addToCart';
const REMOVE_FROM_CART = 'cart/removeFromCart';
const UPDATE_QUANTITY = 'cart/updateQuantity';
const CLEAR_CART = 'cart/clearCart';

// action-creators.js
function addToCart(product) {
  return { type: ADD_TO_CART, payload: product };
}
function removeFromCart(productId) {
  return { type: REMOVE_FROM_CART, payload: productId };
}
function updateQuantity(productId, quantity) {
  return { type: UPDATE_QUANTITY, payload: { productId, quantity } };
}
function clearCart() {
  return { type: CLEAR_CART };
}

// reducer.js
function cartReducer(state = initialState, action) {
  switch (action.type) {
    case ADD_TO_CART:
      const existing = state.items.find(
        item => item.id === action.payload.id
      );
      if (existing) {
        return {
          ...state,
          items: state.items.map(item =>
            item.id === action.payload.id
              ? { ...item, quantity: item.quantity + 1 }
              : item
          )
        };
      }
      return {
        ...state,
        items: [...state.items, { ...action.payload, quantity: 1 }]
      };
    // ... more cases, each with careful spread operators
    default:
      return state;
  }
}

// That is THREE files and about 60 lines for basic cart logic.
```

```javascript
// After Redux Toolkit: clean and concise

import { createSlice } from '@reduxjs/toolkit';

const cartSlice = createSlice({
  name: 'cart',                    // Line 1: Prefix for action types
  initialState: {                  // Line 2: Starting state
    items: [],
    total: 0,
    itemCount: 0,
  },
  reducers: {                      // Line 3: Define reducers (and auto-create actions)
    addToCart(state, action) {      // Line 4: Looks like mutation, but is safe!
      const product = action.payload;
      const existingItem = state.items.find(item => item.id === product.id);

      if (existingItem) {
        existingItem.quantity += 1; // Line 5: Direct "mutation" — Immer handles it
      } else {
        state.items.push({         // Line 6: push() is fine here — Immer!
          ...product,
          quantity: 1
        });
      }

      // Line 7: Recalculate derived values
      state.total = state.items.reduce(
        (sum, item) => sum + item.price * item.quantity, 0
      );
      state.itemCount = state.items.reduce(
        (sum, item) => sum + item.quantity, 0
      );
    },

    removeFromCart(state, action) {
      const productId = action.payload;
      state.items = state.items.filter(item => item.id !== productId);
      state.total = state.items.reduce(
        (sum, item) => sum + item.price * item.quantity, 0
      );
      state.itemCount = state.items.reduce(
        (sum, item) => sum + item.quantity, 0
      );
    },

    updateQuantity(state, action) {
      const { productId, quantity } = action.payload;
      const item = state.items.find(item => item.id === productId);
      if (item) {
        item.quantity = quantity;   // Line 8: Direct assignment, safe with Immer
      }
      state.total = state.items.reduce(
        (sum, item) => sum + item.price * item.quantity, 0
      );
      state.itemCount = state.items.reduce(
        (sum, item) => sum + item.quantity, 0
      );
    },

    clearCart(state) {
      state.items = [];
      state.total = 0;
      state.itemCount = 0;
    },
  },
});

// Line 9: Auto-generated action creators
export const { addToCart, removeFromCart, updateQuantity, clearCart } =
  cartSlice.actions;

// Line 10: The reducer to give to the store
export default cartSlice.reducer;
```

**Line-by-line explanation:**
- **Line 1**: `name: 'cart'` means action types will be `'cart/addToCart'`, `'cart/removeFromCart'`, etc. You never type these strings yourself.
- **Line 2**: Initial state is defined right where the reducer lives.
- **Line 3**: Each key in `reducers` becomes both a reducer case AND an action creator.
- **Lines 4-6**: This looks like you are mutating state (push, direct assignment). But Redux Toolkit uses a library called Immer under the hood. Immer tracks your "mutations" and produces a new immutable state behind the scenes.
- **Line 7**: You can compute derived values right in the reducer.
- **Line 8**: `item.quantity = quantity` looks like mutation but Immer makes it safe.
- **Line 9**: `createSlice` auto-generates action creator functions.
- **Line 10**: Export the reducer to combine it into the store.

### configureStore: Setting Up the Store

```javascript
import { configureStore } from '@reduxjs/toolkit';
import cartReducer from './cartSlice';
import userReducer from './userSlice';
import productsReducer from './productsSlice';

const store = configureStore({
  reducer: {                       // Line 1: Combine multiple slices
    cart: cartReducer,             // state.cart
    user: userReducer,             // state.user
    products: productsReducer,     // state.products
  },
  // Line 2: Redux Toolkit automatically adds:
  //   - Redux DevTools integration
  //   - redux-thunk middleware (for async actions)
  //   - Serializable state check (catches common mistakes)
  //   - Immutability check (catches accidental mutations)
});

export default store;
```

**What configureStore does automatically:**

```
┌────────────────────────────────────────────────────┐
│           configureStore AUTO-SETUP                  │
├────────────────────────────────────────────────────┤
│                                                     │
│  Without RTK, you need:          RTK does it for    │
│                                  you:               │
│  ├─ combineReducers()      ──►  ✓ Automatic         │
│  ├─ applyMiddleware()      ──►  ✓ Automatic         │
│  ├─ Redux DevTools setup   ──►  ✓ Automatic         │
│  ├─ redux-thunk            ──►  ✓ Included          │
│  ├─ Immutability checks    ──►  ✓ Dev mode          │
│  └─ Serializability checks ──►  ✓ Dev mode          │
│                                                     │
└────────────────────────────────────────────────────┘
```

### Using Redux in React Components

```javascript
import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { addToCart, removeFromCart } from './cartSlice';

// Product List Component
function ProductList() {
  const products = useSelector(state => state.products.items); // Line 1
  const dispatch = useDispatch();                               // Line 2

  const handleAddToCart = (product) => {
    dispatch(addToCart(product));                                // Line 3
  };

  return (
    <div>
      <h2>Products</h2>
      {products.map(product => (
        <div key={product.id}>
          <span>{product.name} - ${product.price}</span>
          <button onClick={() => handleAddToCart(product)}>
            Add to Cart
          </button>
        </div>
      ))}
    </div>
  );
}

// Cart Component (completely separate, shares same state)
function Cart() {
  const { items, total, itemCount } = useSelector(state => state.cart); // Line 4
  const dispatch = useDispatch();

  return (
    <div>
      <h2>Cart ({itemCount} items)</h2>
      {items.map(item => (
        <div key={item.id}>
          <span>{item.name} x{item.quantity} = ${item.price * item.quantity}</span>
          <button onClick={() => dispatch(removeFromCart(item.id))}>
            Remove
          </button>
        </div>
      ))}
      <p>Total: ${total.toFixed(2)}</p>
    </div>
  );
}

// App setup
import { Provider } from 'react-redux';
import store from './store';

function App() {
  return (
    <Provider store={store}>       {/* Line 5 */}
      <ProductList />
      <Cart />
    </Provider>
  );
}
```

**Line-by-line explanation:**
- **Line 1**: `useSelector` reads a piece of state from the store. The component re-renders ONLY when this specific piece changes.
- **Line 2**: `useDispatch` returns the store's dispatch function.
- **Line 3**: Dispatch an action. `addToCart(product)` creates `{ type: 'cart/addToCart', payload: product }`.
- **Line 4**: Destructure multiple values from the cart state.
- **Line 5**: `Provider` makes the store available to all child components.

### Async Actions with createAsyncThunk

Real apps need to fetch data from servers. Redux Toolkit provides `createAsyncThunk` for this:

```javascript
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

// Line 1: Define an async action
export const fetchProducts = createAsyncThunk(
  'products/fetchAll',            // Line 2: Action type prefix
  async (category, { rejectWithValue }) => {
    try {
      const response = await fetch(`/api/products?category=${category}`);
      if (!response.ok) {
        throw new Error('Failed to fetch products');
      }
      return await response.json(); // Line 3: This becomes action.payload
    } catch (error) {
      return rejectWithValue(error.message); // Line 4: This becomes action.payload on rejection
    }
  }
);

const productsSlice = createSlice({
  name: 'products',
  initialState: {
    items: [],
    status: 'idle',    // 'idle' | 'loading' | 'succeeded' | 'failed'
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {    // Line 5: Handle async action states
    builder
      .addCase(fetchProducts.pending, (state) => {
        state.status = 'loading';  // Line 6: Request started
        state.error = null;
      })
      .addCase(fetchProducts.fulfilled, (state, action) => {
        state.status = 'succeeded'; // Line 7: Request succeeded
        state.items = action.payload;
      })
      .addCase(fetchProducts.rejected, (state, action) => {
        state.status = 'failed';    // Line 8: Request failed
        state.error = action.payload;
      });
  },
});
```

**Line-by-line explanation:**
- **Line 1**: `createAsyncThunk` wraps an async function and auto-dispatches pending/fulfilled/rejected actions.
- **Line 2**: This prefix generates three action types: `products/fetchAll/pending`, `products/fetchAll/fulfilled`, `products/fetchAll/rejected`.
- **Line 3**: Whatever you return from the async function becomes `action.payload` in the fulfilled case.
- **Line 4**: `rejectWithValue` lets you pass custom error data to the rejected case.
- **Line 5**: `extraReducers` handles actions defined outside the slice (like async thunks).
- **Lines 6-8**: Each async state gets its own handler. This pattern (status + error) is very common.

```javascript
// Using async thunk in a component
function ProductCatalog() {
  const dispatch = useDispatch();
  const { items, status, error } = useSelector(state => state.products);

  useEffect(() => {
    if (status === 'idle') {
      dispatch(fetchProducts('electronics'));
    }
  }, [status, dispatch]);

  if (status === 'loading') return <div>Loading products...</div>;
  if (status === 'failed') return <div>Error: {error}</div>;

  return (
    <div>
      {items.map(product => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}
```

**Output flow:**
```
1. Component mounts
   → status is 'idle'
   → dispatch(fetchProducts('electronics'))
   → status becomes 'loading'
   → UI shows "Loading products..."

2. API responds successfully
   → status becomes 'succeeded'
   → items populated with product data
   → UI shows product cards

3. If API fails
   → status becomes 'failed'
   → error contains error message
   → UI shows "Error: Failed to fetch products"
```

---

## Real-World Example 1: E-Commerce Cart

Let us build a complete e-commerce cart with Redux Toolkit:

```javascript
// features/cart/cartSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

// Async thunk to apply a coupon code
export const applyCoupon = createAsyncThunk(
  'cart/applyCoupon',
  async (couponCode, { getState, rejectWithValue }) => {
    const { cart } = getState();
    const response = await fetch('/api/coupons/validate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        code: couponCode,
        cartTotal: cart.subtotal,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      return rejectWithValue(error.message);
    }

    return await response.json(); // { discount: 15, type: 'percentage' }
  }
);

const cartSlice = createSlice({
  name: 'cart',
  initialState: {
    items: [],
    subtotal: 0,
    discount: 0,
    tax: 0,
    total: 0,
    couponCode: null,
    couponStatus: 'idle', // 'idle' | 'loading' | 'valid' | 'invalid'
    couponError: null,
  },
  reducers: {
    addItem(state, action) {
      const product = action.payload;
      const existing = state.items.find(item => item.id === product.id);

      if (existing) {
        existing.quantity += 1;
      } else {
        state.items.push({ ...product, quantity: 1 });
      }
      recalculateTotals(state);
    },

    removeItem(state, action) {
      state.items = state.items.filter(item => item.id !== action.payload);
      recalculateTotals(state);
    },

    updateQuantity(state, action) {
      const { id, quantity } = action.payload;
      const item = state.items.find(item => item.id === id);
      if (item && quantity > 0) {
        item.quantity = quantity;
      } else if (item && quantity === 0) {
        state.items = state.items.filter(i => i.id !== id);
      }
      recalculateTotals(state);
    },

    clearCart(state) {
      state.items = [];
      state.subtotal = 0;
      state.discount = 0;
      state.tax = 0;
      state.total = 0;
      state.couponCode = null;
      state.couponStatus = 'idle';
    },
  },

  extraReducers: (builder) => {
    builder
      .addCase(applyCoupon.pending, (state) => {
        state.couponStatus = 'loading';
        state.couponError = null;
      })
      .addCase(applyCoupon.fulfilled, (state, action) => {
        state.couponStatus = 'valid';
        state.couponCode = action.meta.arg; // The coupon code string
        const { discount, type } = action.payload;

        if (type === 'percentage') {
          state.discount = state.subtotal * (discount / 100);
        } else {
          state.discount = discount;
        }
        recalculateTotals(state);
      })
      .addCase(applyCoupon.rejected, (state, action) => {
        state.couponStatus = 'invalid';
        state.couponError = action.payload;
        state.discount = 0;
        recalculateTotals(state);
      });
  },
});

// Helper function (not a reducer, just a utility)
function recalculateTotals(state) {
  state.subtotal = state.items.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  );
  const TAX_RATE = 0.08;
  const afterDiscount = state.subtotal - state.discount;
  state.tax = afterDiscount * TAX_RATE;
  state.total = afterDiscount + state.tax;
}

export const { addItem, removeItem, updateQuantity, clearCart } =
  cartSlice.actions;
export default cartSlice.reducer;
```

```javascript
// components/CartSummary.jsx
import { useSelector, useDispatch } from 'react-redux';
import { removeItem, updateQuantity, clearCart, applyCoupon } from './cartSlice';

function CartSummary() {
  const cart = useSelector(state => state.cart);
  const dispatch = useDispatch();
  const [couponInput, setCouponInput] = useState('');

  return (
    <div className="cart-summary">
      <h2>Your Cart</h2>

      {cart.items.length === 0 ? (
        <p>Your cart is empty</p>
      ) : (
        <>
          {cart.items.map(item => (
            <div key={item.id} className="cart-item">
              <span>{item.name}</span>
              <input
                type="number"
                value={item.quantity}
                min="0"
                onChange={(e) =>
                  dispatch(updateQuantity({
                    id: item.id,
                    quantity: parseInt(e.target.value) || 0,
                  }))
                }
              />
              <span>${(item.price * item.quantity).toFixed(2)}</span>
              <button onClick={() => dispatch(removeItem(item.id))}>
                Remove
              </button>
            </div>
          ))}

          <div className="coupon-section">
            <input
              value={couponInput}
              onChange={(e) => setCouponInput(e.target.value)}
              placeholder="Enter coupon code"
            />
            <button
              onClick={() => dispatch(applyCoupon(couponInput))}
              disabled={cart.couponStatus === 'loading'}
            >
              {cart.couponStatus === 'loading' ? 'Checking...' : 'Apply'}
            </button>
            {cart.couponStatus === 'valid' && (
              <span className="success">Coupon applied!</span>
            )}
            {cart.couponStatus === 'invalid' && (
              <span className="error">{cart.couponError}</span>
            )}
          </div>

          <div className="totals">
            <div>Subtotal: ${cart.subtotal.toFixed(2)}</div>
            {cart.discount > 0 && (
              <div>Discount: -${cart.discount.toFixed(2)}</div>
            )}
            <div>Tax: ${cart.tax.toFixed(2)}</div>
            <div className="total">Total: ${cart.total.toFixed(2)}</div>
          </div>

          <button onClick={() => dispatch(clearCart())}>Clear Cart</button>
        </>
      )}
    </div>
  );
}
```

---

## Real-World Example 2: Multi-Step Wizard

A checkout wizard with multiple steps, where each step's data needs to persist:

```javascript
// features/checkout/checkoutSlice.js
import { createSlice } from '@reduxjs/toolkit';

const checkoutSlice = createSlice({
  name: 'checkout',
  initialState: {
    currentStep: 0,
    steps: ['shipping', 'payment', 'review', 'confirmation'],
    data: {
      shipping: {
        firstName: '',
        lastName: '',
        address: '',
        city: '',
        zipCode: '',
        country: '',
      },
      payment: {
        method: 'credit-card', // 'credit-card' | 'paypal' | 'bank-transfer'
        cardLastFour: '',
        isValid: false,
      },
    },
    isComplete: false,
    errors: {},
  },

  reducers: {
    nextStep(state) {
      if (state.currentStep < state.steps.length - 1) {
        state.currentStep += 1;
      }
    },

    prevStep(state) {
      if (state.currentStep > 0) {
        state.currentStep -= 1;
      }
    },

    goToStep(state, action) {
      const step = action.payload;
      if (step >= 0 && step < state.steps.length) {
        state.currentStep = step;
      }
    },

    updateShipping(state, action) {
      state.data.shipping = { ...state.data.shipping, ...action.payload };
      // Clear errors for updated fields
      Object.keys(action.payload).forEach(key => {
        delete state.errors[`shipping.${key}`];
      });
    },

    updatePayment(state, action) {
      state.data.payment = { ...state.data.payment, ...action.payload };
    },

    setErrors(state, action) {
      state.errors = action.payload;
    },

    completeCheckout(state) {
      state.isComplete = true;
      state.currentStep = state.steps.length - 1;
    },

    resetCheckout(state) {
      return checkoutSlice.getInitialState();
    },
  },
});

export const {
  nextStep,
  prevStep,
  goToStep,
  updateShipping,
  updatePayment,
  setErrors,
  completeCheckout,
  resetCheckout,
} = checkoutSlice.actions;

export default checkoutSlice.reducer;
```

```javascript
// components/CheckoutWizard.jsx
function CheckoutWizard() {
  const { currentStep, steps, data, errors, isComplete } = useSelector(
    state => state.checkout
  );
  const dispatch = useDispatch();

  // Step indicator
  const StepIndicator = () => (
    <div className="steps">
      {steps.map((step, index) => (
        <div
          key={step}
          className={`step ${index === currentStep ? 'active' : ''}
                     ${index < currentStep ? 'completed' : ''}`}
          onClick={() => index < currentStep && dispatch(goToStep(index))}
        >
          {index + 1}. {step}
        </div>
      ))}
    </div>
  );

  // Render current step
  const renderStep = () => {
    switch (steps[currentStep]) {
      case 'shipping':
        return <ShippingForm data={data.shipping} errors={errors} />;
      case 'payment':
        return <PaymentForm data={data.payment} />;
      case 'review':
        return <ReviewOrder data={data} />;
      case 'confirmation':
        return <Confirmation />;
      default:
        return null;
    }
  };

  return (
    <div className="checkout-wizard">
      <StepIndicator />
      {renderStep()}
      <div className="navigation">
        {currentStep > 0 && !isComplete && (
          <button onClick={() => dispatch(prevStep())}>Back</button>
        )}
        {currentStep < steps.length - 2 && (
          <button onClick={() => dispatch(nextStep())}>Next</button>
        )}
      </div>
    </div>
  );
}
```

```
WIZARD STATE FLOW

  Step 0: Shipping     Step 1: Payment     Step 2: Review     Step 3: Done
  ┌─────────────┐    ┌─────────────┐    ┌────────────┐    ┌────────────┐
  │ First Name  │    │ Card / PP   │    │ Show all   │    │  Order     │
  │ Last Name   │───►│ Validation  │───►│ data from  │───►│  Confirmed │
  │ Address     │    │ Selection   │    │ steps 0-1  │    │  Thank you │
  │ City / Zip  │    │             │    │ Edit links │    │            │
  └─────────────┘    └─────────────┘    └────────────┘    └────────────┘
        │                  │                  │
        ▼                  ▼                  ▼
   updateShipping()   updatePayment()   completeCheckout()
        │                  │                  │
        └──────────────────┴──────────────────┘
                           │
                    All stored in ONE
                    Redux store slice
```

---

## When Redux Is Overkill

Redux adds structure, but structure has a cost. Not every app needs it.

```
SHOULD YOU USE REDUX? (Decision Guide)

  Is your state shared across many components
  that are NOT in a parent-child relationship?
         │
    YES  │  NO ──► Use useState/useReducer + Context
         │
         ▼
  Do you need to track EVERY state change
  for debugging or undo/redo?
         │
    YES  │  NO ──► Consider Zustand or Context
         │
         ▼
  Is your team large (5+ frontend devs)?
         │
    YES  │  NO ──► Zustand or Jotai may be simpler
         │
         ▼
  Does your app have complex data flows
  (e.g., real-time updates, offline sync)?
         │
    YES  │  NO ──► Reconsider if you really need Redux
         │
         ▼
  USE REDUX (with Redux Toolkit)
```

### Signs Redux is Overkill

- Your app has 5-10 components total
- State is mostly local (form inputs, toggles, modals)
- Only 2-3 pieces of state need to be shared
- You are the only developer
- You are building a prototype or MVP

### Signs You Need Redux (or similar)

- Multiple unrelated components need the same data
- State changes need to be logged and debugged
- Complex state transitions (dependent updates)
- Undo/redo functionality
- Offline support and state persistence
- Large team needing clear state management patterns

---

## Lighter Alternatives

### Zustand: Bear Minimum State Management

Zustand is much simpler than Redux while keeping a similar single-store approach:

```javascript
// Zustand: entire cart store in about 30 lines
import { create } from 'zustand';

const useCartStore = create((set, get) => ({
  // State
  items: [],
  total: 0,

  // Actions (just functions that call set)
  addItem: (product) => {
    set((state) => {
      const existing = state.items.find(item => item.id === product.id);
      let newItems;

      if (existing) {
        newItems = state.items.map(item =>
          item.id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      } else {
        newItems = [...state.items, { ...product, quantity: 1 }];
      }

      return {
        items: newItems,
        total: newItems.reduce(
          (sum, item) => sum + item.price * item.quantity, 0
        ),
      };
    });
  },

  removeItem: (productId) => {
    set((state) => {
      const newItems = state.items.filter(item => item.id !== productId);
      return {
        items: newItems,
        total: newItems.reduce(
          (sum, item) => sum + item.price * item.quantity, 0
        ),
      };
    });
  },

  clearCart: () => set({ items: [], total: 0 }),

  // Computed value using get()
  getItemCount: () => {
    return get().items.reduce((sum, item) => sum + item.quantity, 0);
  },
}));

// Using in a component — no Provider needed!
function Cart() {
  const items = useCartStore(state => state.items);
  const total = useCartStore(state => state.total);
  const removeItem = useCartStore(state => state.removeItem);

  return (
    <div>
      {items.map(item => (
        <div key={item.id}>
          {item.name} x{item.quantity}
          <button onClick={() => removeItem(item.id)}>Remove</button>
        </div>
      ))}
      <p>Total: ${total}</p>
    </div>
  );
}
```

### Jotai: Atomic State Management

Jotai takes a completely different approach. Instead of one big store, you create small atoms of state:

```javascript
import { atom, useAtom } from 'jotai';

// Define atoms (individual pieces of state)
const cartItemsAtom = atom([]);

// Derived atom (computed from other atoms)
const cartTotalAtom = atom((get) => {
  const items = get(cartItemsAtom);
  return items.reduce(
    (sum, item) => sum + item.price * item.quantity, 0
  );
});

const cartCountAtom = atom((get) => {
  const items = get(cartItemsAtom);
  return items.reduce((sum, item) => sum + item.quantity, 0);
});

// Write atom (action)
const addToCartAtom = atom(
  null, // no read value
  (get, set, product) => {
    const items = get(cartItemsAtom);
    const existing = items.find(item => item.id === product.id);

    if (existing) {
      set(cartItemsAtom, items.map(item =>
        item.id === product.id
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ));
    } else {
      set(cartItemsAtom, [...items, { ...product, quantity: 1 }]);
    }
  }
);

// Using in components
function CartCount() {
  const [count] = useAtom(cartCountAtom);
  return <span>Cart ({count})</span>;
}

function AddButton({ product }) {
  const [, addToCart] = useAtom(addToCartAtom);
  return <button onClick={() => addToCart(product)}>Add</button>;
}
```

### Comparison Table

```
┌─────────────────┬───────────┬───────────┬──────────┬──────────┐
│ Feature         │ Redux TK  │ Zustand   │ Jotai    │ Context  │
├─────────────────┼───────────┼───────────┼──────────┼──────────┤
│ Bundle Size     │ ~11 kB    │ ~1.5 kB   │ ~3 kB    │ 0 kB     │
│ Boilerplate     │ Medium    │ Low       │ Low      │ Low      │
│ Learning Curve  │ High      │ Low       │ Medium   │ Low      │
│ DevTools        │ Excellent │ Good      │ Good     │ Basic    │
│ Middleware      │ Built-in  │ Plugin    │ None     │ Manual   │
│ Async Support   │ Thunks    │ Built-in  │ Built-in │ Manual   │
│ Provider Needed │ Yes       │ No        │ Yes      │ Yes      │
│ Re-render Perf  │ Good      │ Great     │ Great    │ Poor*    │
│ Team Scale      │ Large     │ Any       │ Any      │ Small    │
│ Undo/Redo       │ Easy      │ Possible  │ Hard     │ Hard     │
│ Time Travel     │ Yes       │ No        │ No       │ No       │
│ Best For        │ Large     │ Medium    │ Small-   │ Simple   │
│                 │ apps      │ apps      │ Medium   │ sharing  │
└─────────────────┴───────────┴───────────┴──────────┴──────────┘

* Context causes all consumers to re-render on any change.
  The others can do selective subscriptions.
```

---

## When to Use / When NOT to Use

### Use Flux/Redux When

- Multiple unrelated components share state
- You need time-travel debugging
- State changes are complex and depend on each other
- Team is large and needs clear conventions
- You need middleware for logging, analytics, or error tracking
- Undo/redo is a requirement

### Do NOT Use When

- State is mostly local to components
- Your app is small (less than 10 routes)
- You can solve the problem with useReducer + Context
- You are prototyping and need to move fast
- Server state is your main concern (use React Query instead)

---

## Common Mistakes

### Mistake 1: Putting Everything in Redux

```javascript
// BAD: UI state does not belong in Redux
const uiSlice = createSlice({
  name: 'ui',
  initialState: {
    isModalOpen: false,        // This is local state!
    tooltipText: '',           // This is local state!
    inputValue: '',            // This is definitely local state!
    isDropdownExpanded: false,  // Local state!
  },
  // ...
});

// GOOD: Only shared, app-wide state goes in Redux
// Use useState for UI state that belongs to one component
function Modal() {
  const [isOpen, setIsOpen] = useState(false); // Local is fine
  return (/* ... */);
}
```

### Mistake 2: Mutating State Without Immer

```javascript
// BAD: Mutating state in a plain reducer (outside RTK)
function reducer(state, action) {
  state.items.push(action.payload); // MUTATION! Redux will not detect the change
  return state; // Same reference, no re-render
}

// GOOD: Return a new object
function reducer(state, action) {
  return {
    ...state,
    items: [...state.items, action.payload],
  };
}

// ALSO GOOD: Use RTK createSlice (Immer handles it)
// state.items.push(action.payload) IS safe inside createSlice
```

### Mistake 3: Deriving State Incorrectly

```javascript
// BAD: Storing derived values that can get out of sync
const slice = createSlice({
  name: 'cart',
  initialState: {
    items: [],
    totalPrice: 0,    // Derived from items — risk of getting out of sync
    totalCount: 0,    // Also derived
  },
  reducers: {
    addItem(state, action) {
      state.items.push(action.payload);
      // Forgot to update totalPrice! Now it is wrong.
    },
  },
});

// GOOD: Use selectors to derive values
const selectCartTotal = (state) =>
  state.cart.items.reduce(
    (sum, item) => sum + item.price * item.quantity, 0
  );

// Or if the calculation is expensive, use createSelector (memoized)
import { createSelector } from '@reduxjs/toolkit';

const selectCartItems = (state) => state.cart.items;
const selectCartTotal = createSelector(
  [selectCartItems],
  (items) => items.reduce(
    (sum, item) => sum + item.price * item.quantity, 0
  )
);
```

### Mistake 4: Not Using Selectors

```javascript
// BAD: Accessing deep state paths everywhere
function Component() {
  const name = useSelector(
    state => state.user.profile.settings.display.name
  );
  // If state shape changes, you must update EVERY component
}

// GOOD: Centralize selectors near the slice
// userSlice.js
export const selectDisplayName = (state) =>
  state.user.profile.settings.display.name;

// Component.js
function Component() {
  const name = useSelector(selectDisplayName);
  // If state shape changes, update ONE selector
}
```

---

## Best Practices

1. **Use Redux Toolkit**: Never write raw Redux in new projects. RTK eliminates boilerplate and prevents common bugs.

2. **Normalize State Shape**: Store data like a database. Use IDs as keys, not nested arrays.
   ```javascript
   // Instead of: { users: [{ id: 1, name: 'Alice' }, { id: 2, name: 'Bob' }] }
   // Use: { users: { byId: { 1: { name: 'Alice' }, 2: { name: 'Bob' } }, allIds: [1, 2] } }
   ```

3. **Keep Reducers Pure**: No API calls, no random numbers, no Date.now() inside reducers. Use thunks for side effects.

4. **Write Selectors**: Put selectors next to the slice. Use `createSelector` for expensive computations.

5. **One Slice Per Feature**: Organize by feature (cart, user, products), not by type (actions, reducers, selectors).

6. **Do Not Over-Subscribe**: Select only the data you need. Selecting too much causes unnecessary re-renders.
   ```javascript
   // BAD: re-renders on ANY cart change
   const cart = useSelector(state => state.cart);

   // GOOD: re-renders only when itemCount changes
   const itemCount = useSelector(state => state.cart.itemCount);
   ```

7. **Use TypeScript**: Redux Toolkit has excellent TypeScript support. Type your state, actions, and selectors.

---

## Quick Summary

Flux introduced unidirectional data flow: Actions describe events, the Dispatcher routes them, Stores update state, and Views render it. Redux simplified this to one store, pure reducer functions, and dispatched actions. Redux Toolkit (RTK) is the modern way to write Redux, eliminating boilerplate with createSlice and configureStore while using Immer for safe "mutations." For smaller apps, Zustand offers a simpler API with no boilerplate, and Jotai provides atomic state management. Choose based on app size, team size, and debugging needs.

---

## Key Points

- **Unidirectional data flow** means data moves in one direction: Action -> Reducer -> Store -> View -> Action. This makes state changes predictable and debuggable.
- **Actions** are plain objects that describe what happened (`{ type: 'cart/addItem', payload: product }`). They never contain logic.
- **Reducers** are pure functions: `(state, action) => newState`. Same input always produces same output, no side effects.
- **Redux Toolkit** is the standard way to write Redux today. It includes Immer (safe mutations), auto-generated action creators, and DevTools integration.
- **createSlice** combines action types, action creators, and reducer logic in one place.
- **configureStore** automatically sets up middleware, DevTools, and development checks.
- **createAsyncThunk** handles async operations with automatic pending/fulfilled/rejected states.
- **Not every app needs Redux**. Consider Zustand for medium apps or Jotai for atomic state. Use plain Context for simple state sharing.

---

## Practice Questions

1. What are the three principles of Redux? Explain each one in your own words.

2. Why does Redux require reducers to be pure functions? What would happen if a reducer called an API or used `Math.random()`?

3. You have a component that only needs the cart item count, but it re-renders whenever any cart state changes. How would you fix this?

4. Compare Redux Toolkit's `createSlice` with writing raw Redux. What three things does `createSlice` generate automatically?

5. Your team is building a small marketing website with 5 pages, a contact form, and a newsletter signup. Someone suggests using Redux. What would you recommend instead, and why?

---

## Exercises

### Exercise 1: Todo App with Redux Toolkit

Build a todo application using Redux Toolkit. Requirements:
- Add, toggle complete, and delete todos
- Filter by: All, Active, Completed
- Show count of remaining todos
- Use createSlice for the todo logic
- Use selectors for filtered todos and counts

**Hints**: Create a `todosSlice` with an items array and a filter string. Use `createSelector` for the filtered list.

### Exercise 2: Multi-Step Registration Wizard

Build a 3-step registration form (Personal Info, Preferences, Review) where:
- Each step's data persists in Redux when moving between steps
- Users can go back and edit previous steps
- The Review step shows all data from previous steps
- A "Submit" button on Review dispatches an async thunk
- Handle loading and error states

**Hints**: Create a `registrationSlice` similar to the checkout example. Use `extraReducers` for the async submission.

### Exercise 3: Redux vs Zustand Comparison

Implement the same feature (a simple shopping cart with add/remove/clear) using:
1. Redux Toolkit
2. Zustand

Compare: lines of code, number of files, ease of setup, and developer experience. Write a short paragraph explaining which you preferred and why.

---

## What Is Next?

Now that you understand how to manage application state predictably, the next chapter explores **Rendering Patterns**. You will learn how CSR, SSR, SSG, and ISR work, when to use each one, and how modern frameworks like Next.js decide how to render your pages. State management and rendering strategy together determine how your app feels to users.
