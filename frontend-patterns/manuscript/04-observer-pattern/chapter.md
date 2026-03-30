# Chapter 4: Observer Pattern

## What You Will Learn

- What the Observer Pattern is and how it models real-world subscriptions
- The two roles: Subject (the thing being watched) and Observer (the watcher)
- How to implement the Observer Pattern from scratch in JavaScript
- How `addEventListener` is the Observer Pattern in disguise
- Why unsubscribing is critical for preventing memory leaks
- How the Observer Pattern powers React state management
- Real-world applications: form validation, real-time data, and component communication

## Why This Chapter Matters

Think about a YouTube channel. When a creator uploads a new video, you do not have to check their page every five minutes to see if something new is available. Instead, you hit the **Subscribe** button. Now YouTube automatically notifies you whenever a new video drops.

You are the **observer**. The YouTube channel is the **subject**. You subscribed to changes. When a change happens, you get notified. When you no longer care, you unsubscribe.

This is the Observer Pattern, and it is everywhere in frontend development. Every time you write `addEventListener`, you are using the Observer Pattern. Every time a React component re-renders because state changed, the Observer Pattern is working behind the scenes. Every time a Redux store notifies connected components, that is the Observer Pattern.

Understanding this pattern deeply will change how you think about communication between parts of your application. Instead of one piece of code directly calling another, the Observer Pattern lets pieces of code say "tell me when something happens" and react accordingly.

---

## The Problem: Tight Coupling and Polling

Imagine you have a weather station that measures temperature. Several displays need to show the current temperature: a dashboard widget, a mobile notification, and an analytics logger.

### The Painful Way (Before the Pattern)

```javascript
// weather-station.js -- tightly coupled version

class WeatherStation {
  constructor() {
    this.temperature = 0;
    // The station has to KNOW about every display
    this.dashboard = null;
    this.mobileNotifier = null;
    this.analyticsLogger = null;
  }

  setTemperature(temp) {
    this.temperature = temp;
    console.log(`Temperature updated to ${temp}°C`);

    // Manually update each display
    if (this.dashboard) {
      this.dashboard.update(temp);
    }
    if (this.mobileNotifier) {
      this.mobileNotifier.notify(temp);
    }
    if (this.analyticsLogger) {
      this.analyticsLogger.log(temp);
    }
    // What if we add 10 more displays? 20 more?
    // This function grows forever.
  }
}

class Dashboard {
  update(temp) {
    console.log(`Dashboard: Displaying ${temp}°C`);
  }
}

class MobileNotifier {
  notify(temp) {
    console.log(`Mobile: Push notification - ${temp}°C`);
  }
}

const station = new WeatherStation();
station.dashboard = new Dashboard();
station.mobileNotifier = new MobileNotifier();
station.setTemperature(22);
```

**Output:**
```
Temperature updated to 22°C
Dashboard: Displaying 22°C
Mobile: Push notification - 22°C
```

### What Is Wrong Here?

```
  ┌─────────────────────────────────────────────┐
  │            WeatherStation                    │
  │                                              │
  │  setTemperature() {                          │
  │    if (this.dashboard) {...}     ◄── KNOWS   │
  │    if (this.mobileNotifier) {...} ◄── ABOUT  │
  │    if (this.analyticsLogger) {...} ◄── EACH  │
  │    if (this.newThing1) {...}     ◄── SINGLE  │
  │    if (this.newThing2) {...}     ◄── ONE     │
  │  }                                           │
  │                                              │
  │  The station is tightly coupled              │
  │  to every consumer.                          │
  │                                              │
  │  Adding a new consumer means                 │
  │  modifying the station code.                 │
  └─────────────────────────────────────────────┘
```

Problems:
1. **Tight coupling**: The `WeatherStation` must know about every display class and its method names
2. **Violation of Open/Closed Principle**: Adding a new display requires modifying `WeatherStation`
3. **Different interfaces**: Each display has a different method name (`update`, `notify`, `log`), making the code inconsistent
4. **Hard to remove displays**: No clean way to stop notifying a display

---

## The Solution: Observer Pattern

The Observer Pattern defines a one-to-many relationship between objects. When the **subject** (the thing being watched) changes state, all its **observers** (the watchers) are notified automatically.

```
  ┌──────────────┐         ┌──────────────┐
  │              │ subscribe│              │
  │              │◄─────────│  Observer A   │
  │              │         │  (Dashboard)  │
  │              │         └──────────────┘
  │              │
  │   Subject    │         ┌──────────────┐
  │  (Weather    │ subscribe│              │
  │   Station)   │◄─────────│  Observer B   │
  │              │         │  (Mobile)    │
  │              │         └──────────────┘
  │              │
  │   When state │         ┌──────────────┐
  │   changes,   │ subscribe│              │
  │   notify all │◄─────────│  Observer C   │
  │              │         │  (Logger)    │
  └──────┬───────┘         └──────────────┘
         │
         │ notify("temperature changed!")
         │
         ├──────────────────► Observer A gets notified
         ├──────────────────► Observer B gets notified
         └──────────────────► Observer C gets notified
```

The subject does not know or care what its observers are. It just maintains a list and notifies everyone on that list.

---

## Building the Observer Pattern from Scratch

### Step 1: The Subject (Observable)

```javascript
// observable.js

class Observable {
  constructor() {
    this.observers = [];
  }

  subscribe(observer) {
    this.observers.push(observer);
    console.log(`New observer subscribed. Total: ${this.observers.length}`);
  }

  unsubscribe(observer) {
    this.observers = this.observers.filter(obs => obs !== observer);
    console.log(`Observer unsubscribed. Total: ${this.observers.length}`);
  }

  notify(data) {
    console.log(`Notifying ${this.observers.length} observer(s)`);
    this.observers.forEach(observer => observer(data));
  }
}

export default Observable;
```

### Step 2: Using the Observable

```javascript
// weather-station.js -- Observer Pattern version
import Observable from './observable.js';

class WeatherStation extends Observable {
  constructor() {
    super();
    this.temperature = 0;
    this.humidity = 0;
  }

  setMeasurements(temperature, humidity) {
    this.temperature = temperature;
    this.humidity = humidity;
    console.log(`\nMeasurements: ${temperature}°C, ${humidity}% humidity`);

    // Notify all observers with the new data
    this.notify({
      temperature: this.temperature,
      humidity: this.humidity,
      timestamp: Date.now()
    });
  }
}

// Create the station
const station = new WeatherStation();

// Create observers (just functions!)
function dashboardDisplay(data) {
  console.log(`Dashboard: ${data.temperature}°C | ${data.humidity}% humidity`);
}

function mobileAlert(data) {
  if (data.temperature > 35) {
    console.log(`MOBILE ALERT: High temperature warning! ${data.temperature}°C`);
  } else {
    console.log(`Mobile: Temperature is ${data.temperature}°C -- normal`);
  }
}

function analyticsLogger(data) {
  console.log(`Analytics: Logged temp=${data.temperature}, humidity=${data.humidity}`);
}

// Subscribe observers
station.subscribe(dashboardDisplay);
station.subscribe(mobileAlert);
station.subscribe(analyticsLogger);

// Update measurements -- all observers get notified
station.setMeasurements(22, 65);
station.setMeasurements(38, 40);

// Unsubscribe the mobile alert
station.unsubscribe(mobileAlert);

// Only dashboard and analytics get notified now
station.setMeasurements(15, 80);
```

**Output:**
```
New observer subscribed. Total: 1
New observer subscribed. Total: 2
New observer subscribed. Total: 3

Measurements: 22°C, 65% humidity
Notifying 3 observer(s)
Dashboard: 22°C | 65% humidity
Mobile: Temperature is 22°C -- normal
Analytics: Logged temp=22, humidity=65

Measurements: 38°C, 40% humidity
Notifying 3 observer(s)
Dashboard: 38°C | 40% humidity
MOBILE ALERT: High temperature warning! 38°C
Analytics: Logged temp=38, humidity=40
Observer unsubscribed. Total: 2

Measurements: 15°C, 80% humidity
Notifying 2 observer(s)
Dashboard: 15°C | 80% humidity
Analytics: Logged temp=15, humidity=80
```

### Before vs After

```
  BEFORE (Tight Coupling)           AFTER (Observer Pattern)
  ────────────────────────          ────────────────────────

  WeatherStation knows about:      WeatherStation knows about:
  - Dashboard                      - A list of functions
  - MobileNotifier                 - That is all
  - AnalyticsLogger
  - FutureDisplay1                 Adding a new observer:
  - FutureDisplay2                 station.subscribe(newFn)
                                   Zero changes to WeatherStation
  Adding a new display:
  1. Create the class               Removing an observer:
  2. Add property to station         station.unsubscribe(fn)
  3. Add if-check in notify          Zero changes to WeatherStation
  4. Modify WeatherStation code
```

---

## addEventListener: The Observer Pattern in Your Browser

You have been using the Observer Pattern since your first `addEventListener` call.

```javascript
// The DOM element is the SUBJECT
const button = document.querySelector('#myButton');

// Each event listener is an OBSERVER
function handleClick(event) {
  console.log('Button clicked!', event.target);
}

function trackClick(event) {
  console.log('Analytics: button_click event tracked');
}

function animateClick(event) {
  console.log('Animation: ripple effect triggered');
}

// SUBSCRIBE observers to the subject
button.addEventListener('click', handleClick);
button.addEventListener('click', trackClick);
button.addEventListener('click', animateClick);

// When the button is clicked, ALL observers are notified
// Just like our Observable.notify() method!

// UNSUBSCRIBE an observer
button.removeEventListener('click', trackClick);
// Now only handleClick and animateClick will fire on click
```

```
  DOM Event System = Observer Pattern

  ┌────────────┐           ┌────────────────────┐
  │  <button>   │           │  addEventListener   │
  │  (Subject)  │           │  = subscribe()      │
  │             │           │                     │
  │  Has a list │           │  removeEventListener│
  │  of event   │           │  = unsubscribe()    │
  │  listeners  │           │                     │
  │             │           │  Event fires        │
  │             │           │  = notify()          │
  └────────────┘           └────────────────────┘
```

### Custom Events: Building Your Own DOM Events

You can create custom events using the same Observer Pattern mechanism built into the browser.

```javascript
// Create a custom event target
const appEvents = new EventTarget();

// Subscribe to custom events
appEvents.addEventListener('user:login', (e) => {
  console.log(`User logged in: ${e.detail.name}`);
});

appEvents.addEventListener('user:login', (e) => {
  console.log(`Updating navbar for ${e.detail.name}`);
});

// Fire the event -- notifies all listeners
appEvents.dispatchEvent(new CustomEvent('user:login', {
  detail: { name: 'Alice', email: 'alice@example.com' }
}));
```

**Output:**
```
User logged in: Alice
Updating navbar for Alice
```

---

## A More Complete Observable Implementation

Let us build a production-quality Observable with useful features.

```javascript
// observable.js -- production version

class Observable {
  constructor() {
    this._observers = new Map(); // event -> Set of callbacks
  }

  /**
   * Subscribe to a specific event
   * Returns an unsubscribe function
   */
  on(event, callback) {
    if (!this._observers.has(event)) {
      this._observers.set(event, new Set());
    }
    this._observers.get(event).add(callback);

    // Return unsubscribe function (like React useEffect cleanup)
    return () => {
      this._observers.get(event)?.delete(callback);
      // Clean up empty sets
      if (this._observers.get(event)?.size === 0) {
        this._observers.delete(event);
      }
    };
  }

  /**
   * Subscribe to an event, but only fire once
   */
  once(event, callback) {
    const unsubscribe = this.on(event, (data) => {
      callback(data);
      unsubscribe(); // Auto-remove after first call
    });
    return unsubscribe;
  }

  /**
   * Emit an event with data
   */
  emit(event, data) {
    const callbacks = this._observers.get(event);
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in observer for "${event}":`, error);
        }
      });
    }
  }

  /**
   * Remove all observers for a specific event, or all events
   */
  removeAll(event) {
    if (event) {
      this._observers.delete(event);
    } else {
      this._observers.clear();
    }
  }

  /**
   * Get the count of observers for an event
   */
  listenerCount(event) {
    return this._observers.get(event)?.size || 0;
  }
}

export default Observable;
```

### Using the Production Observable

```javascript
import Observable from './observable.js';

const store = new Observable();

// Subscribe to 'change' events
const unsubName = store.on('change', (data) => {
  console.log('Name observer:', data);
});

store.on('change', (data) => {
  console.log('Logger:', JSON.stringify(data));
});

// Subscribe to 'error' event, but only fire once
store.once('error', (err) => {
  console.log('One-time error handler:', err.message);
});

console.log('Change listeners:', store.listenerCount('change'));
console.log('Error listeners:', store.listenerCount('error'));

// Emit events
store.emit('change', { field: 'name', value: 'Alice' });
store.emit('error', { message: 'Network timeout' });
store.emit('error', { message: 'Second error' }); // once() already removed, no handler

// Unsubscribe name observer
unsubName();
console.log('\nAfter unsubscribing name observer:');
console.log('Change listeners:', store.listenerCount('change'));

store.emit('change', { field: 'email', value: 'alice@example.com' });
```

**Output:**
```
Change listeners: 2
Error listeners: 1
Name observer: { field: 'name', value: 'Alice' }
Logger: {"field":"name","value":"Alice"}
One-time error handler: Network timeout

After unsubscribing name observer:
Change listeners: 1
Logger: {"field":"email","value":"alice@example.com"}
```

---

## Memory Leaks: The Silent Killer

The most dangerous mistake with the Observer Pattern is forgetting to unsubscribe. If an observer subscribes but never unsubscribes, it stays in memory forever.

### The Problem

```javascript
// MEMORY LEAK EXAMPLE

class UserProfile {
  constructor(userId) {
    this.userId = userId;

    // Subscribe to auth changes
    authStore.on('change', (state) => {
      console.log(`Profile ${this.userId}: auth state changed`);
      // This callback holds a reference to `this` (the UserProfile instance)
    });
  }

  destroy() {
    // Oops! We forgot to unsubscribe!
    // The callback is still in authStore's observer list
    // The garbage collector cannot clean up this UserProfile
    console.log(`Profile ${this.userId} destroyed... or is it?`);
  }
}

// Create and destroy 1000 profiles
for (let i = 0; i < 1000; i++) {
  const profile = new UserProfile(i);
  profile.destroy();
}

// authStore now has 1000 callbacks!
// Each callback holds a reference to a UserProfile
// None of them can be garbage collected
// This is a memory leak
```

```
  ┌──────────────────────────────────────────────────┐
  │                  Memory Over Time                │
  │                                                  │
  │  Memory                                          │
  │  Usage     ╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱  ← Leaked    │
  │    ▲      ╱                          observers   │
  │    │     ╱                           keep        │
  │    │    ╱                            growing     │
  │    │   ╱                                         │
  │    │  ╱                                          │
  │    │ ╱                                           │
  │    │╱                                            │
  │    └──────────────────────────────► Time          │
  │                                                  │
  │    Without unsubscribe, memory usage only goes   │
  │    UP. Never down. Eventually: crash.            │
  └──────────────────────────────────────────────────┘
```

### The Fix: Always Unsubscribe

```javascript
class UserProfile {
  constructor(userId) {
    this.userId = userId;

    // Store the unsubscribe function
    this._unsubscribeAuth = authStore.on('change', (state) => {
      console.log(`Profile ${this.userId}: auth state changed`);
    });
  }

  destroy() {
    // Clean up the subscription!
    this._unsubscribeAuth();
    console.log(`Profile ${this.userId} properly destroyed`);
  }
}
```

### Memory Leaks in React: The useEffect Cleanup

React components face the same problem. When a component unmounts, its subscriptions must be cleaned up.

```javascript
// BAD -- memory leak
import { useEffect, useState } from 'react';
import chatService from './chat-service';

function ChatMessages() {
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    // Subscribe but never unsubscribe!
    chatService.on('message', (msg) => {
      setMessages(prev => [...prev, msg]);
    });
    // When this component unmounts, the callback stays registered
    // It will try to call setMessages on an unmounted component
  }, []);

  return (
    <ul>
      {messages.map((msg, i) => <li key={i}>{msg.text}</li>)}
    </ul>
  );
}
```

```javascript
// GOOD -- cleanup on unmount
import { useEffect, useState } from 'react';
import chatService from './chat-service';

function ChatMessages() {
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    const unsubscribe = chatService.on('message', (msg) => {
      setMessages(prev => [...prev, msg]);
    });

    // Return cleanup function -- React calls this on unmount
    return () => {
      unsubscribe();
    };
  }, []);

  return (
    <ul>
      {messages.map((msg, i) => <li key={i}>{msg.text}</li>)}
    </ul>
  );
}
```

```
  React Component Lifecycle + Observer Pattern:
  ──────────────────────────────────────────────

  Mount ──► useEffect runs ──► subscribe to observable
                                    │
  Live  ──► Receives notifications ─┘
                                    │
  Unmount ► cleanup function runs ──► unsubscribe from observable
                                    │
  Result: No memory leak. Clean. ───┘
```

---

## Real-World Example: Form Validation with Observers

```javascript
// form-validator.js
import Observable from './observable.js';

class FormValidator extends Observable {
  constructor() {
    super();
    this.fields = {};
    this.errors = {};
  }

  registerField(name, rules) {
    this.fields[name] = { value: '', rules, touched: false };
    this.errors[name] = [];
  }

  setValue(name, value) {
    if (!this.fields[name]) return;

    this.fields[name].value = value;
    this.fields[name].touched = true;

    // Validate this field
    this.errors[name] = this._validate(name, value);

    // Notify observers with current state
    this.emit('fieldChange', {
      field: name,
      value,
      errors: this.errors[name],
      isValid: this.errors[name].length === 0,
      allValid: this.isFormValid()
    });
  }

  _validate(name, value) {
    const errors = [];
    const rules = this.fields[name].rules;

    if (rules.required && !value.trim()) {
      errors.push(`${name} is required`);
    }
    if (rules.minLength && value.length < rules.minLength) {
      errors.push(`${name} must be at least ${rules.minLength} characters`);
    }
    if (rules.pattern && !rules.pattern.test(value)) {
      errors.push(`${name} format is invalid`);
    }

    return errors;
  }

  isFormValid() {
    return Object.values(this.errors).every(fieldErrors => fieldErrors.length === 0)
      && Object.values(this.fields).every(field => field.touched);
  }
}

// Usage
const form = new FormValidator();

// Register fields with rules
form.registerField('email', {
  required: true,
  pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/
});

form.registerField('password', {
  required: true,
  minLength: 8
});

// Observer: Error display
form.on('fieldChange', ({ field, errors }) => {
  if (errors.length > 0) {
    console.log(`[Error Display] ${field}: ${errors.join(', ')}`);
  } else {
    console.log(`[Error Display] ${field}: valid`);
  }
});

// Observer: Submit button state
form.on('fieldChange', ({ allValid }) => {
  console.log(`[Submit Button] ${allValid ? 'Enabled' : 'Disabled'}`);
});

// Simulate user typing
console.log('--- User types email ---');
form.setValue('email', 'bad');
console.log('\n--- User fixes email ---');
form.setValue('email', 'alice@example.com');
console.log('\n--- User types short password ---');
form.setValue('password', '123');
console.log('\n--- User types valid password ---');
form.setValue('password', 'securepass123');
```

**Output:**
```
--- User types email ---
[Error Display] email: email format is invalid
[Submit Button] Disabled

--- User fixes email ---
[Error Display] email: valid
[Submit Button] Disabled

--- User types short password ---
[Error Display] password: password must be at least 8 characters
[Submit Button] Disabled

--- User types valid password ---
[Error Display] password: valid
[Submit Button] Enabled
```

---

## Real-World Example: Online/Offline Status Monitor

```javascript
// connection-monitor.js
import Observable from './observable.js';

class ConnectionMonitor extends Observable {
  constructor() {
    super();
    this.isOnline = typeof navigator !== 'undefined' ? navigator.onLine : true;

    if (typeof window !== 'undefined') {
      window.addEventListener('online', () => this._setStatus(true));
      window.addEventListener('offline', () => this._setStatus(false));
    }
  }

  _setStatus(online) {
    const wasOnline = this.isOnline;
    this.isOnline = online;

    if (wasOnline !== online) {
      this.emit('statusChange', {
        isOnline: online,
        timestamp: new Date().toISOString()
      });
    }
  }

  getStatus() {
    return this.isOnline;
  }
}

const monitor = new ConnectionMonitor();

// Observer: Show banner
monitor.on('statusChange', ({ isOnline }) => {
  if (isOnline) {
    console.log('Banner: Back online! Syncing data...');
  } else {
    console.log('Banner: You are offline. Changes will be saved locally.');
  }
});

// Observer: Queue or send requests
monitor.on('statusChange', ({ isOnline }) => {
  if (isOnline) {
    console.log('API Client: Flushing queued requests');
  } else {
    console.log('API Client: Switching to offline queue');
  }
});

// Simulate going offline and back online
monitor._setStatus(false);
monitor._setStatus(true);
```

**Output:**
```
Banner: You are offline. Changes will be saved locally.
API Client: Switching to offline queue
Banner: Back online! Syncing data...
API Client: Flushing queued requests
```

---

## Observer Pattern in React: A Custom Hook

You can wrap the Observer Pattern in a custom hook so React components automatically subscribe and unsubscribe.

```javascript
// useObservable.js
import { useState, useEffect } from 'react';

export function useObservable(observable, event, initialValue) {
  const [value, setValue] = useState(initialValue);

  useEffect(() => {
    const unsubscribe = observable.on(event, (data) => {
      setValue(data);
    });

    // Cleanup on unmount
    return unsubscribe;
  }, [observable, event]);

  return value;
}
```

```javascript
// TemperatureDisplay.jsx
import { useObservable } from './useObservable';
import weatherStation from './weather-station';

function TemperatureDisplay() {
  const data = useObservable(weatherStation, 'measurement', {
    temperature: 0,
    humidity: 0
  });

  return (
    <div>
      <h2>Current Weather</h2>
      <p>Temperature: {data.temperature}°C</p>
      <p>Humidity: {data.humidity}%</p>
    </div>
  );
}

// Multiple components can use the same observable
function WeatherAlerts() {
  const data = useObservable(weatherStation, 'measurement', {
    temperature: 0
  });

  if (data.temperature > 35) {
    return <div className="alert">High temperature warning!</div>;
  }
  return null;
}
```

When `TemperatureDisplay` or `WeatherAlerts` unmounts, the cleanup function in `useEffect` runs `unsubscribe()`. No memory leaks.

---

## When to Use / When NOT to Use

### When to Use the Observer Pattern

- **DOM event handling**: Any situation where elements emit events (clicks, scrolls, resizes, key presses)
- **Real-time data**: WebSocket messages, server-sent events, live updates
- **Cross-component communication**: When one component's action should affect several other components
- **Form validation**: Changes to form fields trigger validation, error display, and submit button state
- **State management**: Stores that notify UI components of changes
- **Undo/redo systems**: Record changes and notify the UI to update

### When NOT to Use the Observer Pattern

- **Simple parent-child communication**: In React, just pass props. Do not add an observer system for one-way data flow
- **Synchronous one-to-one communication**: If only one thing needs to know about a change, call it directly. The Observer Pattern adds complexity for one-to-one relationships
- **When you forget to unsubscribe**: If your team struggles with cleanup, consider simpler alternatives like React Context or a state management library that handles subscriptions for you
- **Performance-critical hot paths**: Notifying many observers in a tight loop (like during animation frames) can cause performance issues. Profile and optimize

---

## Common Mistakes

### Mistake 1: Subscribing in a Loop Without Unsubscribing

```javascript
// BAD -- creates a new subscription every render cycle
function BadComponent() {
  // This runs on EVERY render
  store.on('change', (data) => {
    console.log(data); // 1 call on first render, 2 on second, 3 on third...
  });

  return <div>...</div>;
}
```

```javascript
// GOOD -- subscribe once in useEffect with cleanup
function GoodComponent() {
  useEffect(() => {
    const unsubscribe = store.on('change', (data) => {
      console.log(data); // Always just 1 call
    });
    return unsubscribe;
  }, []);

  return <div>...</div>;
}
```

### Mistake 2: Modifying the Observer List During Notification

```javascript
// DANGEROUS -- modifying the list while iterating
class BadObservable {
  notify(data) {
    this.observers.forEach(observer => {
      observer(data); // What if this observer calls unsubscribe()?
      // The array changes WHILE we are iterating over it!
    });
  }
}
```

```javascript
// SAFE -- iterate over a copy
class SafeObservable {
  notify(data) {
    const observersCopy = [...this.observers]; // Copy the array
    observersCopy.forEach(observer => observer(data));
  }
}
```

### Mistake 3: Not Handling Errors in Observers

```javascript
// BAD -- one broken observer stops all subsequent observers
class FragileObservable {
  notify(data) {
    this.observers.forEach(observer => observer(data));
    // If observer #2 throws, observers #3, #4, #5 never get called
  }
}
```

```javascript
// GOOD -- catch errors per observer
class RobustObservable {
  notify(data) {
    this.observers.forEach(observer => {
      try {
        observer(data);
      } catch (error) {
        console.error('Observer error:', error);
      }
    });
  }
}
```

---

## Best Practices

1. **Always return an unsubscribe function** from your `subscribe`/`on` method. This makes cleanup easy and follows the pattern used by React's `useEffect`.

2. **Use `useEffect` cleanup** in React components. Every subscription in a `useEffect` should have a corresponding unsubscribe in the returned cleanup function.

3. **Wrap errors in try/catch** inside your notify loop. One broken observer should not prevent others from being notified.

4. **Iterate over a copy** of the observer list during notification. This prevents bugs when observers add or remove themselves during notification.

5. **Name your events clearly**. Use descriptive event names like `'user:login'`, `'cart:itemAdded'`, `'theme:changed'` instead of generic names like `'update'` or `'change'`.

6. **Keep observer callbacks lightweight**. Heavy processing in an observer can block other observers and the UI. Offload expensive work with `requestAnimationFrame` or `setTimeout`.

7. **Consider using a `once` method** for events that should only be handled once (initialization, one-time setup, etc.).

---

## Quick Summary

The Observer Pattern establishes a subscription mechanism where observers register interest in a subject's changes and get notified automatically.

```
  Observer Pattern Flow:
  ──────────────────────

  1. Subject maintains a list of observers
  2. Observers subscribe: subject.on('event', callback)
  3. Subject state changes
  4. Subject notifies all observers: subject.emit('event', data)
  5. Each observer reacts to the data
  6. When done, observer unsubscribes: unsubscribe()

  Built-in Examples:
  ──────────────────
  - addEventListener / removeEventListener
  - React's useState (triggers re-render for all dependent components)
  - Node.js EventEmitter
  - RxJS Observables
```

---

## Key Points

- The **Observer Pattern** defines a one-to-many dependency so that when the subject changes, all observers are notified
- The **subject** (observable) maintains a list of observers and notifies them of changes
- **Observers** are callbacks that react to the subject's changes
- **addEventListener** is the Observer Pattern built into the browser's DOM API
- **Unsubscribing is critical** -- failing to remove observers causes memory leaks
- In React, use **useEffect cleanup functions** to unsubscribe when components unmount
- Always **handle errors** in observer callbacks to prevent one broken observer from blocking others
- The Observer Pattern decouples the subject from its observers -- the subject never needs to know what its observers are

---

## Practice Questions

1. What is the difference between tight coupling (calling observers directly) and the Observer Pattern? What advantage does loose coupling provide?

2. Why does `addEventListener` qualify as an implementation of the Observer Pattern? Identify the subject, observer, subscribe, and notify operations.

3. What causes memory leaks with the Observer Pattern? How does React's `useEffect` cleanup function prevent them?

4. Why should you iterate over a copy of the observer list during notification? What bug can occur if you iterate over the original list?

5. What is the difference between `on` (subscribe) and `once` (subscribe once)? Give a real-world scenario where `once` is more appropriate.

---

## Exercises

### Exercise 1: Build a Stock Price Ticker

Create a `StockTicker` observable that:
- Tracks the price of multiple stocks (e.g., AAPL, GOOGL, MSFT)
- Allows observers to subscribe to specific stocks by name
- Notifies only the relevant observers when a specific stock price changes
- Has a `once` feature for one-time price alerts (e.g., "notify me when AAPL hits $200")

Test it with at least three observers watching different stocks.

### Exercise 2: Observable with History

Extend the `Observable` class to include:
- A history buffer that stores the last N emitted values (configurable)
- A `replay` method that immediately sends all buffered values to a new subscriber
- This is useful when a component subscribes after events have already been emitted

This pattern is similar to RxJS `ReplaySubject`.

### Exercise 3: React useObservable Hook with Selector

Build a custom React hook `useObservable(observable, event, selector)` where:
- `selector` is a function that extracts only the data the component needs
- The hook only triggers a re-render if the selected data actually changed (shallow comparison)
- Include proper cleanup on unmount

Example usage:
```javascript
// Only re-renders when temperature changes, ignores humidity changes
const temp = useObservable(weatherStation, 'measurement', data => data.temperature);
```

---

## What Is Next?

The Observer Pattern creates a direct relationship between subjects and observers. The observer subscribes directly to the subject. But what if two parts of your application need to communicate without knowing each other at all?

That is where the Publish/Subscribe (Pub/Sub) Pattern comes in. Chapter 5 introduces an intermediary -- an event bus -- that lets components communicate without any direct connection.
