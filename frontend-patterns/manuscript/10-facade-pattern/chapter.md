# Chapter 10: The Facade Pattern

## What You Will Learn

- What the Facade pattern is and why simplicity matters
- How to hide complex subsystems behind simple interfaces
- How to build an API facade that unifies multiple endpoints
- How to build SDK wrappers that tame third-party complexity
- How to build a form submission facade that handles validation, formatting, and API calls
- When to use a facade and when direct access is better

## Why This Chapter Matters

Think about driving a car. You turn the steering wheel, press the gas pedal, and hit the brakes. Three simple controls.

Behind those controls, hundreds of systems work together: the engine management computer, fuel injection, transmission, power steering pump, brake hydraulics, ABS sensors, traction control. You do not need to know about any of them. The steering wheel, gas pedal, and brake pedal form a **facade** -- a simple interface that hides enormous complexity.

In frontend development, complexity hides everywhere. A "simple" form submission might involve validation, data transformation, file uploads, API calls, error handling, retry logic, and analytics tracking. A "simple" analytics event might require initializing three different SDKs, formatting data differently for each, and handling failures silently.

The Facade pattern gives your code a steering wheel. It provides one simple function that handles all the complexity underneath so callers do not need to think about it.

---

## The Problem

You need to interact with a complex system -- multiple APIs, third-party libraries, or intricate business logic -- and the complexity is leaking into every part of your codebase.

```javascript
// A developer wants to submit a contact form.
// Here is what they have to deal with:

async function handleSubmit(formData) {
  // 1. Validate every field manually
  if (!formData.name || formData.name.trim().length < 2) {
    throw new Error("Name is required");
  }
  if (!formData.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
    throw new Error("Valid email is required");
  }
  if (!formData.message || formData.message.trim().length < 10) {
    throw new Error("Message must be at least 10 characters");
  }

  // 2. Sanitize the data
  const sanitized = {
    name: formData.name.trim(),
    email: formData.email.toLowerCase().trim(),
    message: formData.message.trim(),
    submittedAt: new Date().toISOString()
  };

  // 3. Get auth token
  const token = localStorage.getItem("auth_token");
  if (!token) {
    throw new Error("Not authenticated");
  }

  // 4. Make the API call with proper headers
  const response = await fetch("https://api.example.com/contact", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
      "X-Request-ID": crypto.randomUUID()
    },
    body: JSON.stringify(sanitized)
  });

  // 5. Handle different error codes
  if (response.status === 401) {
    localStorage.removeItem("auth_token");
    throw new Error("Session expired. Please log in again.");
  }
  if (response.status === 429) {
    throw new Error("Too many requests. Please wait.");
  }
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || "Submission failed");
  }

  // 6. Track analytics
  if (window.gtag) {
    window.gtag("event", "form_submit", {
      event_category: "contact",
      event_label: "success"
    });
  }

  return response.json();
}
```

Every form in the app repeats similar patterns. Different developers do it differently. Bugs hide in the details.

---

## The Solution: Facade Pattern

The Facade pattern provides a unified, simple interface to a complex subsystem. It does not eliminate the complexity -- it organizes and hides it.

```
Without a Facade:

+--------+     +-- Validator
|        | --> +-- Sanitizer
| Caller | --> +-- Auth Service
|        | --> +-- HTTP Client
+--------+     +-- Error Handler
               +-- Analytics

The caller must know about EVERY subsystem.

With a Facade:

+--------+     +-----------+     +-- Validator
|        |     |           | --> +-- Sanitizer
| Caller | --> |  Facade   | --> +-- Auth Service
|        |     |           | --> +-- HTTP Client
+--------+     +-----------+     +-- Error Handler
                                 +-- Analytics

The caller only knows about the Facade.
```

---

## Facade 1: API Facade

### Problem

Your app talks to a REST API with many endpoints. Each endpoint has different URL patterns, HTTP methods, headers, and data formats. This complexity is spread across your entire codebase.

### Before: Raw API Calls Everywhere

```javascript
// In UserProfile component
const response = await fetch("https://api.example.com/v2/users/42", {
  headers: { "Authorization": `Bearer ${getToken()}` }
});
const user = await response.json();

// In Settings component
const response = await fetch("https://api.example.com/v2/users/42", {
  method: "PATCH",
  headers: {
    "Authorization": `Bearer ${getToken()}`,
    "Content-Type": "application/json"
  },
  body: JSON.stringify({ theme: "dark" })
});

// In Admin component
const response = await fetch("https://api.example.com/v2/users?role=admin", {
  headers: { "Authorization": `Bearer ${getToken()}` }
});
const admins = await response.json();
```

### After: API Facade

```javascript
// api.js -- The Facade

const BASE_URL = "https://api.example.com/v2";

function getHeaders() {
  const headers = { "Content-Type": "application/json" };
  const token = localStorage.getItem("auth_token");
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

async function handleResponse(response) {
  if (response.status === 401) {
    localStorage.removeItem("auth_token");
    window.location.href = "/login";
    throw new Error("Session expired");
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.message || `HTTP Error ${response.status}`);
  }

  // Handle 204 No Content
  if (response.status === 204) return null;

  return response.json();
}

async function request(endpoint, options = {}) {
  const { method = "GET", body, params } = options;

  let url = `${BASE_URL}${endpoint}`;
  if (params) {
    const searchParams = new URLSearchParams(params);
    url += `?${searchParams}`;
  }

  const response = await fetch(url, {
    method,
    headers: getHeaders(),
    body: body ? JSON.stringify(body) : undefined
  });

  return handleResponse(response);
}

// Public API -- clean, simple, consistent
const api = {
  users: {
    getById: (id) => request(`/users/${id}`),

    list: (filters) => request("/users", { params: filters }),

    update: (id, data) =>
      request(`/users/${id}`, { method: "PATCH", body: data }),

    delete: (id) =>
      request(`/users/${id}`, { method: "DELETE" }),

    create: (data) =>
      request("/users", { method: "POST", body: data })
  },

  posts: {
    getByUser: (userId) => request(`/users/${userId}/posts`),

    create: (userId, data) =>
      request(`/users/${userId}/posts`, { method: "POST", body: data }),

    delete: (userId, postId) =>
      request(`/users/${userId}/posts/${postId}`, { method: "DELETE" })
  }
};

export default api;
```

Now every component uses the same clean interface:

```javascript
// In UserProfile component
const user = await api.users.getById(42);

// In Settings component
await api.users.update(42, { theme: "dark" });

// In Admin component
const admins = await api.users.list({ role: "admin" });
```

No more remembering URLs, headers, methods, or error handling. The facade handles all of it.

---

## Facade 2: SDK Wrapper

### Problem

You use a third-party analytics SDK. Its API is verbose and complex. You also want the ability to swap it out later without rewriting your entire app.

### Before: SDK Calls Scattered Everywhere

```javascript
// In CheckoutPage.jsx
import amplitude from "amplitude-js";

function handlePurchase(cart) {
  amplitude.getInstance().logEvent("purchase_completed", {
    total: cart.total,
    itemCount: cart.items.length,
    currency: "USD",
    items: cart.items.map((i) => ({
      id: i.id,
      name: i.name,
      price: i.price,
      quantity: i.quantity
    }))
  });
}

// In SearchPage.jsx
import amplitude from "amplitude-js";

function handleSearch(query, results) {
  amplitude.getInstance().logEvent("search_performed", {
    query: query,
    resultCount: results.length,
    timestamp: Date.now()
  });
}

// Amplitude is referenced directly in 50+ files.
// Want to switch to Mixpanel? Rewrite everything.
```

### After: Analytics Facade

```javascript
// analytics.js -- The Facade

class Analytics {
  constructor() {
    this.providers = [];
    this.initialized = false;
  }

  init(config = {}) {
    // Initialize all providers behind the facade
    if (config.amplitude) {
      const amplitude = require("amplitude-js");
      amplitude.getInstance().init(config.amplitude.apiKey);
      this.providers.push({
        name: "amplitude",
        track: (event, props) => {
          amplitude.getInstance().logEvent(event, props);
        },
        identify: (userId, traits) => {
          amplitude.getInstance().setUserId(userId);
          amplitude.getInstance().setUserProperties(traits);
        }
      });
    }

    if (config.mixpanel) {
      const mixpanel = require("mixpanel-browser");
      mixpanel.init(config.mixpanel.token);
      this.providers.push({
        name: "mixpanel",
        track: (event, props) => mixpanel.track(event, props),
        identify: (userId, traits) => {
          mixpanel.identify(userId);
          mixpanel.people.set(traits);
        }
      });
    }

    this.initialized = true;
  }

  track(event, properties = {}) {
    if (!this.initialized) {
      console.warn("Analytics not initialized");
      return;
    }

    const enrichedProps = {
      ...properties,
      timestamp: Date.now(),
      page: window.location.pathname
    };

    this.providers.forEach((provider) => {
      try {
        provider.track(event, enrichedProps);
      } catch (error) {
        console.error(
          `Analytics error (${provider.name}):`,
          error.message
        );
      }
    });
  }

  identify(userId, traits = {}) {
    this.providers.forEach((provider) => {
      try {
        provider.identify(userId, traits);
      } catch (error) {
        console.error(
          `Analytics identify error (${provider.name}):`,
          error.message
        );
      }
    });
  }
}

// Export a singleton instance
const analytics = new Analytics();
export default analytics;
```

Now the entire app uses one simple interface:

```javascript
// Initialize once at app startup
analytics.init({
  amplitude: { apiKey: "amp-key-123" },
  mixpanel: { token: "mp-token-456" }
});

// In CheckoutPage.jsx
analytics.track("purchase_completed", {
  total: cart.total,
  itemCount: cart.items.length
});

// In SearchPage.jsx
analytics.track("search_performed", {
  query: query,
  resultCount: results.length
});

// Want to switch from Amplitude to Mixpanel?
// Change ONE file: analytics.js
// Zero changes in your 50+ components.
```

---

## Facade 3: Complex Form Submission

### Problem

Submitting a form involves many steps: validation, sanitization, file uploads, API calls, optimistic UI updates, error handling, and analytics. You do not want every form to handle all of this.

### Before: Every Step Handled Manually

```javascript
async function handleContactSubmit(formData) {
  // 30+ lines of validation, sanitization,
  // API calls, error handling...
  // (See the "Problem" section above)
}

async function handleProfileSubmit(formData) {
  // Another 30+ lines of similar logic
  // with slight differences...
}

async function handleFeedbackSubmit(formData) {
  // And another 30+ lines...
}
```

### After: Form Submission Facade

```javascript
// formFacade.js

const validators = {
  required: (value, fieldName) =>
    !value || (typeof value === "string" && !value.trim())
      ? `${fieldName} is required`
      : null,

  email: (value) =>
    value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)
      ? "Invalid email address"
      : null,

  minLength: (min) => (value, fieldName) =>
    value && value.length < min
      ? `${fieldName} must be at least ${min} characters`
      : null,

  maxLength: (max) => (value, fieldName) =>
    value && value.length > max
      ? `${fieldName} must be at most ${max} characters`
      : null
};

function createFormFacade(config) {
  const {
    endpoint,
    method = "POST",
    fieldRules = {},
    transform = (data) => data,
    onSuccess = () => {},
    onError = () => {},
    analyticsEvent = null
  } = config;

  return async function submitForm(formData) {
    // Step 1: Validate
    const errors = {};
    for (const [field, rules] of Object.entries(fieldRules)) {
      for (const rule of rules) {
        const error = rule(formData[field], field);
        if (error) {
          errors[field] = error;
          break;
        }
      }
    }

    if (Object.keys(errors).length > 0) {
      const error = new Error("Validation failed");
      error.fieldErrors = errors;
      onError(error);
      throw error;
    }

    // Step 2: Transform data
    const transformed = transform(formData);

    // Step 3: Submit
    try {
      const response = await api.request(endpoint, {
        method,
        body: transformed
      });

      // Step 4: Track analytics
      if (analyticsEvent) {
        analytics.track(analyticsEvent, {
          success: true,
          fields: Object.keys(formData)
        });
      }

      // Step 5: Call success handler
      onSuccess(response);
      return response;
    } catch (error) {
      if (analyticsEvent) {
        analytics.track(analyticsEvent, {
          success: false,
          error: error.message
        });
      }

      onError(error);
      throw error;
    }
  };
}

// Usage -- define forms declaratively
const submitContactForm = createFormFacade({
  endpoint: "/contact",
  fieldRules: {
    name: [validators.required, validators.minLength(2)],
    email: [validators.required, validators.email],
    message: [validators.required, validators.minLength(10)]
  },
  transform: (data) => ({
    ...data,
    name: data.name.trim(),
    email: data.email.toLowerCase().trim(),
    message: data.message.trim()
  }),
  analyticsEvent: "contact_form_submitted",
  onSuccess: () => showToast("Message sent!"),
  onError: (err) => showToast(err.message, "error")
});

const submitFeedbackForm = createFormFacade({
  endpoint: "/feedback",
  fieldRules: {
    rating: [validators.required],
    comment: [validators.minLength(5)]
  },
  analyticsEvent: "feedback_submitted"
});
```

Now each form component is clean:

```javascript
function ContactForm() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    message: ""
  });
  const [errors, setErrors] = useState({});

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      await submitContactForm(formData);
    } catch (error) {
      if (error.fieldErrors) {
        setErrors(error.fieldErrors);
      }
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={formData.name}
        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
      />
      {errors.name && <span className="error">{errors.name}</span>}
      {/* ... other fields ... */}
      <button type="submit">Send</button>
    </form>
  );
}
```

---

## Facade 4: Storage Facade

Abstract away the differences between `localStorage`, `sessionStorage`, and cookies:

```javascript
const storage = {
  get(key, defaultValue = null) {
    try {
      const item = localStorage.getItem(key);
      if (item === null) return defaultValue;
      return JSON.parse(item);
    } catch {
      return defaultValue;
    }
  },

  set(key, value, options = {}) {
    try {
      const serialized = JSON.stringify(value);
      localStorage.setItem(key, serialized);

      // Optionally set expiry
      if (options.ttl) {
        const expiresAt = Date.now() + options.ttl;
        localStorage.setItem(`${key}__expires`, expiresAt.toString());
      }
    } catch (error) {
      console.warn("Storage write failed:", error.message);
    }
  },

  remove(key) {
    localStorage.removeItem(key);
    localStorage.removeItem(`${key}__expires`);
  },

  isExpired(key) {
    const expiresAt = localStorage.getItem(`${key}__expires`);
    if (!expiresAt) return false;
    return Date.now() > Number(expiresAt);
  }
};

// Usage -- simple and consistent
storage.set("user", { name: "Alice", role: "admin" }, { ttl: 3600000 });

const user = storage.get("user");
console.log(user);
// Output: { name: 'Alice', role: 'admin' }

storage.get("nonexistent", "fallback");
// Output: "fallback"
```

---

## Facade in React: Custom Hooks as Facades

In React, custom hooks often serve as facades. They hide complexity behind a simple interface:

```javascript
// This hook is a facade over:
// - fetch API
// - loading state
// - error handling
// - caching
// - retry logic
// - abort controller

function useAPI(endpoint) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const controller = new AbortController();
    let retries = 0;

    async function fetchData() {
      setLoading(true);
      setError(null);

      while (retries < 3) {
        try {
          const response = await fetch(endpoint, {
            signal: controller.signal,
            headers: { Authorization: `Bearer ${getToken()}` }
          });

          if (!response.ok) throw new Error(`HTTP ${response.status}`);
          const json = await response.json();
          setData(json);
          setLoading(false);
          return;
        } catch (err) {
          if (err.name === "AbortError") return;
          retries++;
          if (retries >= 3) {
            setError(err);
            setLoading(false);
          } else {
            await new Promise((r) => setTimeout(r, 1000 * retries));
          }
        }
      }
    }

    fetchData();
    return () => controller.abort();
  }, [endpoint]);

  return { data, loading, error };
}

// Components see only the simple interface:
function UserProfile({ userId }) {
  const { data: user, loading, error } = useAPI(`/api/users/${userId}`);

  if (loading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;
  return <div>{user.name}</div>;
}
```

```
What the component sees:        What the hook hides:

  { data, loading, error }       +-- fetch API calls
                                 +-- AbortController
                                 +-- Authentication headers
                                 +-- Retry logic (3 attempts)
                                 +-- Exponential backoff
                                 +-- Error handling
                                 +-- Loading state management
                                 +-- Cleanup on unmount
```

---

## When to Use the Facade Pattern

```
+-----------------------------------------------+
|           USE FACADE WHEN:                    |
+-----------------------------------------------+
|                                               |
|  * A subsystem has many parts and callers     |
|    only need a subset of functionality        |
|  * You want to decouple your code from a      |
|    third-party library (so you can swap it)   |
|  * The same complex operation is repeated     |
|    across many parts of the codebase          |
|  * You want to provide different interfaces   |
|    for different audiences (simple vs advanced)|
|  * Complex initialization or configuration    |
|    needs to happen before using a system      |
|                                               |
+-----------------------------------------------+

+-----------------------------------------------+
|       DO NOT USE FACADE WHEN:                 |
+-----------------------------------------------+
|                                               |
|  * The subsystem is already simple enough     |
|  * Callers genuinely need fine-grained        |
|    control over the subsystem                 |
|  * The facade would just be a pass-through    |
|    with no added value                        |
|  * You are building a facade "just in case"   |
|    you might swap libraries (YAGNI)           |
|  * The facade hides important behavior that   |
|    callers need to understand                 |
|                                               |
+-----------------------------------------------+
```

---

## Common Mistakes

### Mistake 1: The "God Facade"

```javascript
// WRONG -- facade does too much
const app = {
  login() { /* ... */ },
  logout() { /* ... */ },
  fetchUser() { /* ... */ },
  createPost() { /* ... */ },
  sendEmail() { /* ... */ },
  processPayment() { /* ... */ },
  generateReport() { /* ... */ },
  uploadFile() { /* ... */ },
  // 50 more methods...
};

// CORRECT -- separate facades for separate concerns
const auth = { login, logout, refreshToken };
const users = { get, list, update, create };
const posts = { get, list, create, delete: remove };
```

### Mistake 2: Hiding Errors

```javascript
// WRONG -- swallowing errors silently
const api = {
  async fetchUser(id) {
    try {
      const res = await fetch(`/api/users/${id}`);
      return res.json();
    } catch {
      return null; // Caller has no idea something went wrong
    }
  }
};

// CORRECT -- let errors propagate or surface them clearly
const api = {
  async fetchUser(id) {
    const res = await fetch(`/api/users/${id}`);
    if (!response.ok) {
      throw new APIError(`Failed to fetch user ${id}`, res.status);
    }
    return res.json();
  }
};
```

### Mistake 3: Premature Facade

```javascript
// WRONG -- creating a facade for one use
function sendEmail(to, subject, body) {
  // This just wraps one function call
  return emailService.send({ to, subject, body });
}

// If the facade adds no value, skip it.
// Use emailService.send() directly.
```

### Mistake 4: Leaking Abstractions

```javascript
// WRONG -- facade exposes internal details
const analytics = {
  // Callers should not need to know about Amplitude
  getAmplitudeInstance() {
    return amplitude.getInstance();
  },
  track(event, props) {
    this.getAmplitudeInstance().logEvent(event, props);
  }
};

// CORRECT -- keep internals hidden
const analytics = {
  track(event, props) {
    amplitude.getInstance().logEvent(event, props);
  }
};
```

---

## Best Practices

1. **Keep the facade interface minimal** -- expose only what callers actually need. You can always add methods later.

2. **Do not replace access to the subsystem** -- facades should simplify access, not prevent direct access when it is genuinely needed.

3. **Handle errors appropriately** -- facades should translate low-level errors into meaningful errors, not swallow them.

4. **Make facades testable** -- accept dependencies through constructor or configuration rather than hardcoding them.

5. **One facade per concern** -- do not build a "mega facade" that covers everything. Have separate facades for auth, analytics, API, etc.

6. **Document what is hidden** -- since the facade hides complexity, document what it does under the hood so future developers can understand it.

---

## Quick Summary

The Facade pattern provides a simple interface to a complex subsystem. It does not change how the subsystem works -- it just provides an easier way to use it. Common uses include API facades, SDK wrappers, form submission handlers, and storage abstractions. In React, custom hooks often serve as facades that hide complex state management, side effects, and API interactions behind a simple return value.

```
Complex subsystem:        Facade:
  Validator                submitForm(data)
  Sanitizer                  --> validates
  Auth Service               --> sanitizes
  HTTP Client                --> authenticates
  Error Handler              --> submits
  Analytics                  --> tracks
                             --> handles errors
```

---

## Key Points

- The Facade pattern hides complexity behind a simple interface
- Facades do not add new behavior -- they organize existing behavior
- API facades centralize endpoint URLs, headers, auth, and error handling
- SDK wrappers let you swap third-party libraries without rewriting your app
- Form submission facades unify validation, transformation, and API calls
- In React, custom hooks are natural facades
- Keep facades minimal and focused on one concern
- Do not swallow errors inside facades -- translate and surface them

---

## Practice Questions

1. How does the Facade pattern differ from the Decorator pattern? Both involve wrapping -- what is the key distinction?

2. Your team uses three different analytics providers. Explain how a facade would help, and what interface you would expose.

3. A colleague argues that facades create an unnecessary layer of abstraction. When is this argument valid? When is it wrong?

4. You are building a facade for a payment processing system. What methods would you expose? What would you hide?

5. How do React custom hooks act as facades? Give an example of a hook that hides at least three sources of complexity.

---

## Exercises

### Exercise 1: Notification Facade

Build a facade that unifies email, SMS, and push notifications behind a single `notify()` function. The facade should route to the correct service based on the notification type.

```javascript
function createNotificationFacade(services) {
  // Your code here
}

const notify = createNotificationFacade({
  email: emailService,
  sms: smsService,
  push: pushService
});

await notify({
  type: "email",
  to: "alice@example.com",
  subject: "Welcome!",
  body: "Thanks for signing up."
});
```

### Exercise 2: Media Player Facade

Create a facade for a media player that supports audio and video. The facade should handle initialization, playback controls, volume, and cleanup behind simple methods like `play()`, `pause()`, `setVolume()`, and `destroy()`.

```javascript
function createMediaPlayer(element, source) {
  // Your code here
  // Hint: Handle different source types (mp3, mp4, stream URL)
  // Hint: Normalize the browser APIs
}

const player = createMediaPlayer("#player", "song.mp3");
player.play();
player.setVolume(0.5);
player.pause();
player.destroy();
```

### Exercise 3: React Data Fetching Facade Hook

Build a `useResource` hook that serves as a facade over data fetching. It should handle loading, error, refetching, pagination, and caching behind a simple API.

```javascript
function useResource(endpoint, options = {}) {
  // Your code here
  // Return: { data, loading, error, refetch, nextPage, prevPage }
}

function UserList() {
  const { data, loading, error, refetch, nextPage } =
    useResource("/api/users", { pageSize: 10 });

  // Clean component, all complexity hidden in the hook
}
```

---

## What Is Next?

The Facade pattern simplifies how you use complex systems. The next chapter introduces the **Factory pattern**, which simplifies how you create objects and components. Instead of using `new` everywhere and knowing which class to instantiate, a factory function decides for you based on input. You will learn how to build component factories, notification factories, and more.
