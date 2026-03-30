# Chapter 5: Publish/Subscribe Pattern

## What You Will Learn

- What the Pub/Sub Pattern is and how it differs from the Observer Pattern
- How to build an EventBus class from scratch
- How components communicate without knowing each other
- Cross-component communication in frontend applications
- Real-world uses: analytics tracking, notification systems, and micro-frontends
- How to avoid common Pub/Sub pitfalls like event storms and debugging nightmares

## Why This Chapter Matters

Think about a post office. When you mail a letter, you do not walk to the recipient's house and hand it to them. You drop it in the mailbox, and the postal service handles delivery. You do not know the recipient's schedule, their exact address layout, or whether they are home. The postal service is the middleman that decouples sender from receiver.

The Pub/Sub Pattern works exactly like this. Components **publish** messages (drop letters in the mailbox) and other components **subscribe** to messages (get mail delivered to them). The key difference from the Observer Pattern is the middleman -- the **event bus** -- which sits between publishers and subscribers.

In the Observer Pattern from Chapter 4, observers subscribe directly to the subject. They know about each other. In Pub/Sub, publishers and subscribers have zero knowledge of each other. They only know about the event bus.

This distinction matters a great deal in large applications. When you have dozens of components that need to communicate, the Pub/Sub Pattern keeps them loosely coupled. A shopping cart component does not need to know that an analytics tracker is listening. A notification panel does not need to know where notifications come from. Each component does its own job and communicates through the event bus.

---

## Observer vs Pub/Sub: The Key Difference

Before diving into implementation, let us clearly distinguish these two patterns.

### Observer Pattern (Chapter 4)

```
  Observer Pattern: DIRECT relationship

  ┌──────────┐   subscribe()   ┌────────────┐
  │ Observer  │───────────────►│  Subject    │
  │ (knows    │                │  (knows its │
  │  subject) │◄───────────────│   observers)│
  └──────────┘   notify()      └────────────┘

  - Observer subscribes directly to the subject
  - Subject maintains its own observer list
  - They know about each other
```

### Pub/Sub Pattern

```
  Pub/Sub Pattern: INDIRECT relationship via middleman

  ┌───────────┐                              ┌────────────┐
  │ Publisher  │   publish('event', data)     │ Subscriber │
  │ (does NOT  │───────────┐                 │ (does NOT  │
  │  know who  │           │                 │  know who  │
  │  listens)  │           ▼                 │  publishes)│
  └───────────┘    ┌──────────────┐          └────────────┘
                   │              │  deliver        ▲
                   │  Event Bus   │────────────────┘
                   │  (middleman) │
                   │              │          ┌────────────┐
                   │              │  deliver  │ Subscriber │
                   │              │──────────►│  2         │
                   └──────────────┘          └────────────┘

  - Publishers and subscribers never interact directly
  - The event bus handles all routing
  - Complete decoupling
```

### Side-by-Side Comparison

```
  Feature              Observer Pattern         Pub/Sub Pattern
  ─────────            ────────────────         ───────────────

  Coupling             Subject knows its        Publishers and subscribers
                       observers                are completely decoupled

  Middleman            None                     Event bus / message broker

  Subscribe to         The subject directly     An event name/topic on
                                                the event bus

  Communication        Synchronous              Can be sync or async

  Best for             One source, many         Many sources, many
                       listeners                listeners, no dependencies

  Debugging            Easier (direct link)     Harder (indirect link)
```

---

## Building an EventBus

The EventBus is the heart of the Pub/Sub Pattern. It manages subscriptions and routes messages.

```javascript
// event-bus.js

class EventBus {
  constructor() {
    this._events = new Map();
  }

  /**
   * Subscribe to an event topic
   * Returns an unsubscribe function
   */
  subscribe(event, callback) {
    if (!this._events.has(event)) {
      this._events.set(event, new Set());
    }

    this._events.get(event).add(callback);

    // Return unsubscribe function
    return () => {
      this._events.get(event)?.delete(callback);
      if (this._events.get(event)?.size === 0) {
        this._events.delete(event);
      }
    };
  }

  /**
   * Subscribe to an event, fire callback only once
   */
  subscribeOnce(event, callback) {
    const unsubscribe = this.subscribe(event, (data) => {
      callback(data);
      unsubscribe();
    });
    return unsubscribe;
  }

  /**
   * Publish an event with data to all subscribers
   */
  publish(event, data) {
    const subscribers = this._events.get(event);
    if (!subscribers || subscribers.size === 0) {
      return;
    }

    // Iterate over a copy to avoid issues if subscribers
    // unsubscribe during notification
    const subscribersCopy = new Set(subscribers);
    subscribersCopy.forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error(`Error in subscriber for "${event}":`, error);
      }
    });
  }

  /**
   * Remove all subscribers for a specific event
   */
  clear(event) {
    if (event) {
      this._events.delete(event);
    } else {
      this._events.clear();
    }
  }

  /**
   * Check if an event has any subscribers
   */
  hasSubscribers(event) {
    return (this._events.get(event)?.size || 0) > 0;
  }

  /**
   * Get subscriber count for an event
   */
  subscriberCount(event) {
    return this._events.get(event)?.size || 0;
  }

  /**
   * List all active event names
   */
  getEventNames() {
    return [...this._events.keys()];
  }
}

// Export a single EventBus instance (singleton)
const eventBus = new EventBus();
export { EventBus }; // Export class for creating separate buses
export default eventBus;
```

---

## Using the EventBus: Components That Do Not Know Each Other

Let us build a scenario where three features communicate through the EventBus without importing each other.

### The Shopping Cart

```javascript
// features/cart/cart.js
import eventBus from '../../event-bus.js';

const cart = {
  items: [],

  addItem(product) {
    const existing = this.items.find(item => item.id === product.id);
    if (existing) {
      existing.quantity++;
    } else {
      this.items.push({ ...product, quantity: 1 });
    }

    console.log(`Cart: Added "${product.name}"`);

    // Publish event -- cart does NOT know who listens
    eventBus.publish('cart:itemAdded', {
      product,
      cartTotal: this.getTotal(),
      itemCount: this.getItemCount()
    });
  },

  removeItem(productId) {
    const index = this.items.findIndex(item => item.id === productId);
    if (index > -1) {
      const removed = this.items.splice(index, 1)[0];
      console.log(`Cart: Removed "${removed.name}"`);

      eventBus.publish('cart:itemRemoved', {
        product: removed,
        cartTotal: this.getTotal(),
        itemCount: this.getItemCount()
      });
    }
  },

  getTotal() {
    return this.items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  },

  getItemCount() {
    return this.items.reduce((sum, item) => sum + item.quantity, 0);
  }
};

export default cart;
```

### The Analytics Tracker

```javascript
// features/analytics/analytics.js
import eventBus from '../../event-bus.js';

// Analytics subscribes to events it cares about
// It has NO idea where these events come from

eventBus.subscribe('cart:itemAdded', (data) => {
  console.log(`Analytics: track "add_to_cart" - ${data.product.name} ($${data.product.price})`);
  // sendToAnalyticsService('add_to_cart', data);
});

eventBus.subscribe('cart:itemRemoved', (data) => {
  console.log(`Analytics: track "remove_from_cart" - ${data.product.name}`);
  // sendToAnalyticsService('remove_from_cart', data);
});

eventBus.subscribe('user:login', (data) => {
  console.log(`Analytics: track "login" - ${data.email}`);
});

eventBus.subscribe('user:logout', () => {
  console.log('Analytics: track "logout"');
});

console.log('Analytics tracker initialized');
```

### The Notification Panel

```javascript
// features/notifications/notifications.js
import eventBus from '../../event-bus.js';

const notifications = {
  list: [],

  init() {
    // Subscribe to events that should show notifications
    eventBus.subscribe('cart:itemAdded', (data) => {
      this.show(`"${data.product.name}" added to cart. Total: $${data.cartTotal.toFixed(2)}`);
    });

    eventBus.subscribe('user:login', (data) => {
      this.show(`Welcome back, ${data.name}!`);
    });

    eventBus.subscribe('order:placed', (data) => {
      this.show(`Order #${data.orderId} confirmed! Estimated delivery: ${data.deliveryDate}`);
    });

    console.log('Notification panel initialized');
  },

  show(message) {
    this.list.push({ message, timestamp: Date.now() });
    console.log(`Notification: ${message}`);
  }
};

export default notifications;
```

### Putting It All Together

```javascript
// app.js
import cart from './features/cart/cart.js';
import './features/analytics/analytics.js';    // Just importing initializes it
import notifications from './features/notifications/notifications.js';
import eventBus from './event-bus.js';

notifications.init();

console.log('\n--- Adding items to cart ---');
cart.addItem({ id: 'P001', name: 'Wireless Headphones', price: 79.99 });
cart.addItem({ id: 'P002', name: 'Phone Case', price: 19.99 });

console.log('\n--- User logs in ---');
eventBus.publish('user:login', { name: 'Alice', email: 'alice@example.com' });

console.log('\n--- Removing item from cart ---');
cart.removeItem('P001');
```

**Output:**
```
Analytics tracker initialized
Notification panel initialized

--- Adding items to cart ---
Cart: Added "Wireless Headphones"
Analytics: track "add_to_cart" - Wireless Headphones ($79.99)
Notification: "Wireless Headphones" added to cart. Total: $79.99

Cart: Added "Phone Case"
Analytics: track "add_to_cart" - Phone Case ($19.99)
Notification: "Phone Case" added to cart. Total: $99.98

--- User logs in ---
Analytics: track "login" - alice@example.com
Notification: Welcome back, Alice!

--- Removing item from cart ---
Cart: Removed "Wireless Headphones"
Analytics: track "remove_from_cart" - Wireless Headphones
```

### The Dependency Map

```
  WITHOUT Pub/Sub:                    WITH Pub/Sub:

  ┌────────┐   ┌───────────┐         ┌────────┐   ┌───────────┐
  │  Cart   │──►│ Analytics │         │  Cart   │   │ Analytics │
  │        │──►│           │         │        │   │           │
  └────┬───┘   └───────────┘         └────┬───┘   └─────┬─────┘
       │                                   │             │
       │       ┌───────────┐               │  publish    │ subscribe
       └──────►│ Notific.  │               ▼             ▼
               │           │          ┌──────────────────────┐
               └───────────┘          │      Event Bus       │
                                      └──────────────────────┘
  Cart imports Analytics                        ▲
  Cart imports Notifications              subscribe │
  Cart imports anything that                        │
  cares about cart changes             ┌─────┴─────┐
                                       │ Notific.  │
  Tight coupling.                      └───────────┘
  Cart knows too much.
                                       Loose coupling.
                                       Nobody knows each other.
```

---

## Advanced EventBus: Wildcard Subscriptions

Sometimes you want to listen to all events in a category.

```javascript
// event-bus-advanced.js

class AdvancedEventBus {
  constructor() {
    this._events = new Map();
    this._wildcardSubscribers = new Map(); // pattern -> Set of callbacks
  }

  subscribe(event, callback) {
    // Check if this is a wildcard pattern
    if (event.includes('*')) {
      if (!this._wildcardSubscribers.has(event)) {
        this._wildcardSubscribers.set(event, new Set());
      }
      this._wildcardSubscribers.get(event).add(callback);
    } else {
      if (!this._events.has(event)) {
        this._events.set(event, new Set());
      }
      this._events.get(event).add(callback);
    }

    return () => {
      if (event.includes('*')) {
        this._wildcardSubscribers.get(event)?.delete(callback);
      } else {
        this._events.get(event)?.delete(callback);
      }
    };
  }

  publish(event, data) {
    // Notify exact matches
    const exact = this._events.get(event);
    if (exact) {
      exact.forEach(cb => {
        try { cb(data, event); } catch (e) { console.error(e); }
      });
    }

    // Notify wildcard matches
    this._wildcardSubscribers.forEach((callbacks, pattern) => {
      if (this._matchWildcard(event, pattern)) {
        callbacks.forEach(cb => {
          try { cb(data, event); } catch (e) { console.error(e); }
        });
      }
    });
  }

  _matchWildcard(event, pattern) {
    const regex = new RegExp('^' + pattern.replace(/\*/g, '.*') + '$');
    return regex.test(event);
  }
}

// Usage
const bus = new AdvancedEventBus();

// Subscribe to ALL cart events
bus.subscribe('cart:*', (data, eventName) => {
  console.log(`[Cart Logger] Event: ${eventName}`, data);
});

// Subscribe to ALL events (global logger)
bus.subscribe('*', (data, eventName) => {
  console.log(`[Global] ${eventName}`);
});

bus.publish('cart:itemAdded', { name: 'Mouse' });
bus.publish('cart:itemRemoved', { name: 'Keyboard' });
bus.publish('user:login', { email: 'alice@example.com' });
```

**Output:**
```
[Cart Logger] Event: cart:itemAdded { name: 'Mouse' }
[Global] cart:itemAdded
[Cart Logger] Event: cart:itemRemoved { name: 'Keyboard' }
[Global] cart:itemRemoved
[Global] user:login
```

---

## Real-World Use Case: Analytics Tracking System

Analytics is one of the most natural use cases for Pub/Sub. Many different user actions need to be tracked, and the tracking logic should not be sprinkled across every component.

```javascript
// analytics/tracker.js
import eventBus from '../event-bus.js';

class AnalyticsTracker {
  constructor() {
    this.queue = [];
    this.batchSize = 5;
    this.batchInterval = 10000; // 10 seconds
  }

  init() {
    // Page views
    eventBus.subscribe('page:view', (data) => {
      this._track('page_view', {
        path: data.path,
        title: data.title,
        referrer: data.referrer
      });
    });

    // User actions
    eventBus.subscribe('user:signup', (data) => {
      this._track('sign_up', { method: data.method });
    });

    eventBus.subscribe('user:login', (data) => {
      this._track('login', { method: data.method });
    });

    // E-commerce
    eventBus.subscribe('cart:itemAdded', (data) => {
      this._track('add_to_cart', {
        item_id: data.product.id,
        item_name: data.product.name,
        value: data.product.price
      });
    });

    eventBus.subscribe('checkout:started', (data) => {
      this._track('begin_checkout', {
        value: data.total,
        item_count: data.itemCount
      });
    });

    eventBus.subscribe('order:placed', (data) => {
      this._track('purchase', {
        transaction_id: data.orderId,
        value: data.total
      });
    });

    // Start batch sending
    this._startBatchTimer();
    console.log('Analytics tracker initialized');
  }

  _track(eventName, params) {
    const event = {
      name: eventName,
      params,
      timestamp: Date.now(),
      sessionId: this._getSessionId()
    };

    this.queue.push(event);
    console.log(`Analytics: Queued "${eventName}"`, params);

    // Flush immediately if batch is full
    if (this.queue.length >= this.batchSize) {
      this._flush();
    }
  }

  _flush() {
    if (this.queue.length === 0) return;

    const batch = [...this.queue];
    this.queue = [];
    console.log(`Analytics: Sending batch of ${batch.length} events`);
    // In real code: fetch('/api/analytics', { method: 'POST', body: JSON.stringify(batch) })
  }

  _startBatchTimer() {
    setInterval(() => this._flush(), this.batchInterval);
  }

  _getSessionId() {
    return 'session-' + Math.random().toString(36).slice(2, 10);
  }
}

const tracker = new AnalyticsTracker();
export default tracker;
```

```javascript
// app.js
import tracker from './analytics/tracker.js';
import eventBus from './event-bus.js';

tracker.init();

// These events can come from ANYWHERE in the app
// The analytics tracker picks them up automatically
eventBus.publish('page:view', { path: '/products', title: 'Products' });
eventBus.publish('cart:itemAdded', { product: { id: 'P1', name: 'Laptop', price: 999 } });
eventBus.publish('cart:itemAdded', { product: { id: 'P2', name: 'Mouse', price: 29 } });
eventBus.publish('checkout:started', { total: 1028, itemCount: 2 });
eventBus.publish('order:placed', { orderId: 'ORD-1234', total: 1028 });
```

**Output:**
```
Analytics tracker initialized
Analytics: Queued "page_view" { path: '/products', title: 'Products' }
Analytics: Queued "add_to_cart" { item_id: 'P1', item_name: 'Laptop', value: 999 }
Analytics: Queued "add_to_cart" { item_id: 'P2', item_name: 'Mouse', value: 29 }
Analytics: Queued "begin_checkout" { value: 1028, item_count: 2 }
Analytics: Queued "purchase" { transaction_id: 'ORD-1234', value: 1028 }
Analytics: Sending batch of 5 events
```

---

## Cross-Component Communication in React

Pub/Sub can bridge React components that are far apart in the component tree without prop drilling.

```javascript
// hooks/useEventBus.js
import { useEffect, useCallback } from 'react';
import eventBus from '../event-bus';

/**
 * Subscribe to an event bus event within a React component
 * Automatically cleans up on unmount
 */
export function useSubscribe(event, callback) {
  useEffect(() => {
    const unsubscribe = eventBus.subscribe(event, callback);
    return unsubscribe;
  }, [event, callback]);
}

/**
 * Get a publish function for use in React components
 */
export function usePublish() {
  return useCallback((event, data) => {
    eventBus.publish(event, data);
  }, []);
}
```

```javascript
// components/ProductCard.jsx
import { usePublish } from '../hooks/useEventBus';

export default function ProductCard({ product }) {
  const publish = usePublish();

  function handleAddToCart() {
    // Just publish the event -- ProductCard does not know who listens
    publish('cart:itemAdded', { product });
  }

  return (
    <div className="product-card">
      <h3>{product.name}</h3>
      <p>${product.price}</p>
      <button onClick={handleAddToCart}>Add to Cart</button>
    </div>
  );
}
```

```javascript
// components/CartBadge.jsx
import { useState, useCallback } from 'react';
import { useSubscribe } from '../hooks/useEventBus';

export default function CartBadge() {
  const [count, setCount] = useState(0);

  // Subscribe to cart events
  useSubscribe('cart:itemAdded', useCallback(() => {
    setCount(c => c + 1);
  }, []));

  useSubscribe('cart:itemRemoved', useCallback(() => {
    setCount(c => Math.max(0, c - 1));
  }, []));

  return (
    <div className="cart-badge">
      Cart ({count})
    </div>
  );
}
```

```javascript
// components/ToastNotification.jsx
import { useState, useCallback } from 'react';
import { useSubscribe } from '../hooks/useEventBus';

export default function ToastNotification() {
  const [toasts, setToasts] = useState([]);

  useSubscribe('cart:itemAdded', useCallback((data) => {
    const toast = {
      id: Date.now(),
      message: `"${data.product.name}" added to cart`
    };
    setToasts(prev => [...prev, toast]);

    // Auto-remove after 3 seconds
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== toast.id));
    }, 3000);
  }, []));

  return (
    <div className="toast-container">
      {toasts.map(toast => (
        <div key={toast.id} className="toast">{toast.message}</div>
      ))}
    </div>
  );
}
```

```
  Component Tree:

  <App>
  ├── <Header>
  │   └── <CartBadge />      ◄── subscribes to 'cart:itemAdded'
  ├── <ProductList>
  │   ├── <ProductCard />     ◄── publishes 'cart:itemAdded'
  │   ├── <ProductCard />     ◄── publishes 'cart:itemAdded'
  │   └── <ProductCard />     ◄── publishes 'cart:itemAdded'
  └── <ToastNotification />   ◄── subscribes to 'cart:itemAdded'

  ProductCard, CartBadge, and ToastNotification
  have ZERO knowledge of each other.
  They communicate entirely through the event bus.
```

---

## Pub/Sub with Typed Events (Preventing Typos)

A common bug with Pub/Sub is typos in event names. If you publish `'cart:itmAdded'` but subscribe to `'cart:itemAdded'`, nothing happens and there is no error.

```javascript
// events.js -- Define event names as constants

export const EVENTS = Object.freeze({
  CART: Object.freeze({
    ITEM_ADDED: 'cart:itemAdded',
    ITEM_REMOVED: 'cart:itemRemoved',
    CLEARED: 'cart:cleared'
  }),
  USER: Object.freeze({
    LOGIN: 'user:login',
    LOGOUT: 'user:logout',
    PROFILE_UPDATED: 'user:profileUpdated'
  }),
  ORDER: Object.freeze({
    PLACED: 'order:placed',
    SHIPPED: 'order:shipped',
    DELIVERED: 'order:delivered'
  }),
  PAGE: Object.freeze({
    VIEW: 'page:view',
    SCROLL: 'page:scroll'
  })
});
```

```javascript
// Now use constants instead of strings
import { EVENTS } from './events.js';
import eventBus from './event-bus.js';

// Publishing
eventBus.publish(EVENTS.CART.ITEM_ADDED, { product });

// Subscribing
eventBus.subscribe(EVENTS.CART.ITEM_ADDED, (data) => {
  console.log('Item added:', data.product.name);
});

// If you typo the constant name, your IDE catches it immediately
// eventBus.publish(EVENTS.CART.ITM_ADDED, data);
// TypeError: Cannot read property 'ITM_ADDED' of undefined
```

---

## When to Use / When NOT to Use

### When to Use the Pub/Sub Pattern

- **Analytics and telemetry**: Track user actions without polluting component code
- **Cross-feature communication**: When features in different parts of the app need to react to each other's events
- **Plugin/extension systems**: Let third-party code hook into your application via events
- **Micro-frontends**: Communication between independently deployed frontend apps
- **Toast notifications**: Any component can trigger a notification without knowing the notification system
- **Logging and debugging**: Subscribe to events to log them without modifying source components

### When NOT to Use the Pub/Sub Pattern

- **Parent-child React communication**: Use props and callbacks. Pub/Sub is overkill for direct relationships
- **When you need guaranteed delivery**: Pub/Sub is fire-and-forget. If no one subscribes, the message is lost
- **When debugging matters most**: Pub/Sub makes it hard to trace where an event originated. If your team frequently debugs event flow, consider more explicit patterns
- **State management**: Do not replace Redux, Zustand, or React Context with Pub/Sub for state management. State management libraries provide predictable state updates, dev tools, and time-travel debugging. Pub/Sub provides none of that
- **Two components talking directly**: If Component A always and only talks to Component B, just import and call directly. Pub/Sub adds indirection for no benefit

---

## Common Mistakes

### Mistake 1: Event Name Typos (The Silent Failure)

```javascript
// Publisher
eventBus.publish('cart:itemAdded', data);

// Subscriber -- typo in event name!
eventBus.subscribe('cart:itemAdd', (data) => {
  // This NEVER fires. No error. No warning. Silent failure.
  console.log(data);
});
```

**Fix**: Use constant event names as shown above. Your IDE will catch the typo.

### Mistake 2: Forgetting to Unsubscribe in React

```javascript
// BAD -- subscribes on every render, never unsubscribes
function BadComponent() {
  const [count, setCount] = useState(0);

  // This runs on every render!
  eventBus.subscribe('cart:itemAdded', () => {
    setCount(c => c + 1);
  });

  return <span>{count}</span>;
}
```

```javascript
// GOOD -- subscribe in useEffect, cleanup on unmount
function GoodComponent() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const unsubscribe = eventBus.subscribe('cart:itemAdded', () => {
      setCount(c => c + 1);
    });
    return unsubscribe; // Cleanup!
  }, []);

  return <span>{count}</span>;
}
```

### Mistake 3: Event Storms (Cascading Events)

```javascript
// Event A triggers Event B, which triggers Event C,
// which triggers Event A again = infinite loop

eventBus.subscribe('data:updated', () => {
  eventBus.publish('ui:refresh');  // Triggers next subscriber
});

eventBus.subscribe('ui:refresh', () => {
  eventBus.publish('data:validate'); // Triggers next subscriber
});

eventBus.subscribe('data:validate', () => {
  eventBus.publish('data:updated'); // Goes back to the start!
  // Infinite loop!
});
```

**Fix**: Never publish an event in response to an event that could circle back. If you need chains, use a clear, linear flow with distinct event names.

### Mistake 4: Passing Mutable Data

```javascript
// BAD -- subscribers can modify shared data
const product = { name: 'Mouse', price: 29.99 };
eventBus.publish('cart:itemAdded', { product });

// Subscriber A modifies the data
eventBus.subscribe('cart:itemAdded', (data) => {
  data.product.price = 0; // FREE STUFF!
  // This affects ALL other subscribers that receive the same object
});
```

**Fix**: Publish copies of data, or freeze the published data.

```javascript
// GOOD -- publish a frozen copy
eventBus.publish('cart:itemAdded', Object.freeze({
  product: { ...product }
}));
```

---

## Best Practices

1. **Use a naming convention for events**. Adopt a consistent pattern like `domain:action` (e.g., `cart:itemAdded`, `user:login`, `page:scroll`). This makes events discoverable and groupable.

2. **Define event names as constants** in a central file. This prevents typos and makes it easy to see all events in the system.

3. **Always unsubscribe** when a component unmounts or a feature is disabled. Use the returned unsubscribe function.

4. **Do not use Pub/Sub for state management**. It is great for notifications and side effects, but terrible for managing application state that the UI depends on.

5. **Keep event payloads small and serializable**. Avoid publishing DOM elements, class instances, or functions in event data.

6. **Document your events**. Maintain a list of all event names, their payload shapes, and who publishes/subscribes to each. Without documentation, Pub/Sub systems become impossible to maintain.

7. **Avoid event chains that can loop**. If event A triggers event B, make sure B cannot trigger A (directly or indirectly).

8. **Consider using multiple event buses** for different domains (one for UI events, one for data events) to reduce noise and improve separation.

---

## Quick Summary

The Pub/Sub Pattern decouples communication between components by routing messages through an intermediary event bus.

```
  Pub/Sub vs Observer:
  ────────────────────

  Observer:  Subject ◄──── Observer (direct link)
  Pub/Sub:   Publisher ──► EventBus ──► Subscriber (no direct link)

  When to use which:
  ──────────────────
  Observer:  When the "what changed" matters and there is one clear source
  Pub/Sub:   When "something happened" and many unrelated parts need to react
```

---

## Key Points

- The **Pub/Sub Pattern** uses a middleman (event bus) so publishers and subscribers never interact directly
- The key difference from Observer is the **complete decoupling** -- publishers do not know about subscribers and vice versa
- An **EventBus** manages subscriptions and routes messages between publishers and subscribers
- **Always unsubscribe** when a component or feature is destroyed to prevent memory leaks
- Use **constant event names** to avoid typos and silent failures
- Pub/Sub is ideal for **analytics, notifications, logging, and cross-feature communication**
- Do **not** use Pub/Sub for **state management** -- use proper state management tools instead
- Watch out for **event storms** (cascading events that create infinite loops)
- **Document your events** -- without documentation, Pub/Sub systems are very hard to debug

---

## Practice Questions

1. What is the key structural difference between the Observer Pattern and the Pub/Sub Pattern? Draw the relationship between the objects in each.

2. Why is Pub/Sub considered "fire-and-forget"? What happens if an event is published but nobody has subscribed to it?

3. How do wildcard subscriptions work? Give an example where subscribing to `'cart:*'` would be useful.

4. Why is Pub/Sub a poor choice for state management in a React application? What problems arise from using it that way?

5. Explain the "event storm" problem. How can you design your event system to prevent cascading event loops?

---

## Exercises

### Exercise 1: Build a Chat Application Event System

Create a Pub/Sub-based chat system with these events:
- `chat:messageSent` -- when a user sends a message
- `chat:messageReceived` -- when a message arrives from another user
- `chat:userJoined` -- when a user enters the chat room
- `chat:userLeft` -- when a user leaves the chat room

Build three subscribers:
1. A message list that displays messages
2. A user count display that tracks online users
3. A notification sound player that logs "DING!" for every new message

Test by simulating several users joining, chatting, and leaving.

### Exercise 2: EventBus with Middleware

Extend the EventBus to support middleware -- functions that run before every event is delivered to subscribers. Use cases:
- A logging middleware that logs every event
- A filter middleware that blocks certain events in production
- A transform middleware that adds a timestamp to every event payload

### Exercise 3: Scoped Event Buses

Create a factory function that produces separate EventBus instances for different domains:

```javascript
const uiBus = createEventBus('ui');
const dataBus = createEventBus('data');
const analyticsBus = createEventBus('analytics');
```

Each bus should:
- Prefix all event names with its domain (so `uiBus.publish('click')` actually publishes `'ui:click'`)
- Have its own independent subscriber list
- Optionally forward events to a global bus for debugging

---

## What Is Next?

You now understand two powerful communication patterns: Observer (direct) and Pub/Sub (indirect). But communication is just one challenge in frontend development. Another common challenge is working with data collections -- arrays of items from APIs, paginated results, tree structures.

How do you traverse these data structures uniformly, without caring about their internal shape? How do you lazily load pages of data from a server? That is the Iterator Pattern, covered in Chapter 7.
