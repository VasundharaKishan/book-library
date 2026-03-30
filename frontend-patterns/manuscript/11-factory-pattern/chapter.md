# Chapter 11: The Factory Pattern

## What You Will Learn

- What the Factory pattern is and why centralized creation matters
- How factory functions simplify object and component creation
- How to build a component factory for dynamic UIs
- How to build a notification factory that handles different channels
- How to build a chart factory that creates the right visualization
- How to build a form field factory for dynamic forms
- When to use factories and when simpler approaches work better

## Why This Chapter Matters

Imagine a pizza restaurant. You, the customer, do not walk into the kitchen, find the flour, knead the dough, prepare the sauce, grate the cheese, and fire up the oven. You just say "margherita" and the kitchen does the rest.

The kitchen is a **factory**. You tell it what you want. It knows how to make it. The creation details are hidden from you.

In frontend development, you constantly create things: UI components, form fields, notification toasts, chart visualizations, API response handlers. Without the Factory pattern, the creation logic is scattered everywhere. Every part of the codebase needs to know which class to use, what options to set, and how to configure the result.

The Factory pattern centralizes this. You say "give me a bar chart" and the factory handles everything -- choosing the right library, setting the right defaults, configuring the right options. Change how charts are created? Change one factory, not fifty components.

---

## The Problem

You need to create different types of objects based on some input, and the creation logic is complex or varies by type.

```javascript
// Creating notifications -- the hard way
function showNotification(type, message, options) {
  if (type === "success") {
    const el = document.createElement("div");
    el.className = "toast toast-success";
    el.innerHTML = `<span class="icon">✓</span><span>${message}</span>`;
    el.style.backgroundColor = "#10b981";
    el.style.color = "white";
    document.body.appendChild(el);
    setTimeout(() => el.remove(), options.duration || 3000);
  } else if (type === "error") {
    const el = document.createElement("div");
    el.className = "toast toast-error";
    el.innerHTML = `<span class="icon">✗</span><span>${message}</span>`;
    el.style.backgroundColor = "#ef4444";
    el.style.color = "white";
    document.body.appendChild(el);
    // Errors should stay longer
    setTimeout(() => el.remove(), options.duration || 5000);
  } else if (type === "warning") {
    // More copy-pasted code...
  } else if (type === "info") {
    // Even more copy-pasted code...
  }
}
```

Every notification type has similar code with slight variations. Adding a new type means adding another `if` branch. The creation logic is tangled with the rendering logic.

---

## The Solution: Factory Pattern

The Factory pattern encapsulates object creation. A factory function takes input (usually a type or configuration) and returns the right object, fully constructed and ready to use.

```
Without a Factory:

  Component A --> new BarChart(...)
  Component B --> new LineChart(...)
  Component C --> new PieChart(...)

  Each component knows about every chart type.

With a Factory:

  Component A --> chartFactory("bar")  --> BarChart
  Component B --> chartFactory("line") --> LineChart
  Component C --> chartFactory("pie")  --> PieChart

  Components only know about the factory.
  The factory knows about the chart types.
```

---

## Basic Factory Function

The simplest factory is just a function that returns different objects based on input:

```javascript
function createButton(type) {
  const base = {
    padding: "8px 16px",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
    fontSize: "14px"
  };

  switch (type) {
    case "primary":
      return {
        ...base,
        backgroundColor: "#3b82f6",
        color: "white"
      };
    case "secondary":
      return {
        ...base,
        backgroundColor: "transparent",
        color: "#3b82f6",
        border: "1px solid #3b82f6"
      };
    case "danger":
      return {
        ...base,
        backgroundColor: "#ef4444",
        color: "white"
      };
    default:
      return {
        ...base,
        backgroundColor: "#e5e7eb",
        color: "#374151"
      };
  }
}

console.log(createButton("primary"));
// Output: { padding: '8px 16px', border: 'none', borderRadius: '4px',
//           cursor: 'pointer', fontSize: '14px',
//           backgroundColor: '#3b82f6', color: 'white' }

console.log(createButton("danger"));
// Output: { padding: '8px 16px', border: 'none', borderRadius: '4px',
//           cursor: 'pointer', fontSize: '14px',
//           backgroundColor: '#ef4444', color: 'white' }
```

---

## Factory 1: Component Factory

### Problem

You have a dashboard where users can add widgets. Each widget type is a different React component. You need to render the right component based on the widget type stored in a configuration.

### Before: Giant Switch Statement in JSX

```javascript
function Dashboard({ widgets }) {
  return (
    <div className="dashboard">
      {widgets.map((widget) => {
        switch (widget.type) {
          case "chart":
            return (
              <ChartWidget
                key={widget.id}
                data={widget.data}
                chartType={widget.chartType}
                title={widget.title}
              />
            );
          case "table":
            return (
              <TableWidget
                key={widget.id}
                columns={widget.columns}
                data={widget.data}
                sortable={widget.sortable}
              />
            );
          case "metric":
            return (
              <MetricWidget
                key={widget.id}
                value={widget.value}
                label={widget.label}
                trend={widget.trend}
              />
            );
          case "text":
            return (
              <TextWidget
                key={widget.id}
                content={widget.content}
                format={widget.format}
              />
            );
          default:
            return <div key={widget.id}>Unknown widget type</div>;
        }
      })}
    </div>
  );
}
```

### After: Component Factory

```javascript
// widgetFactory.js

import ChartWidget from "./widgets/ChartWidget";
import TableWidget from "./widgets/TableWidget";
import MetricWidget from "./widgets/MetricWidget";
import TextWidget from "./widgets/TextWidget";
import UnknownWidget from "./widgets/UnknownWidget";

// Registry of widget types
const widgetRegistry = {
  chart: ChartWidget,
  table: TableWidget,
  metric: MetricWidget,
  text: TextWidget
};

function createWidget(config) {
  const Component = widgetRegistry[config.type] || UnknownWidget;
  return <Component key={config.id} {...config} />;
}

// Allow registering new widget types at runtime
function registerWidget(type, component) {
  widgetRegistry[type] = component;
}

export { createWidget, registerWidget };
```

Now the dashboard is clean:

```javascript
function Dashboard({ widgets }) {
  return (
    <div className="dashboard">
      {widgets.map((widget) => createWidget(widget))}
    </div>
  );
}
```

Adding a new widget type requires zero changes to the Dashboard:

```javascript
// Some other module adds a new widget type
import { registerWidget } from "./widgetFactory";
import MapWidget from "./widgets/MapWidget";

registerWidget("map", MapWidget);

// Now any dashboard config with type: "map" will work automatically
```

```
Before (tight coupling):
  Dashboard knows about:
    ChartWidget, TableWidget, MetricWidget,
    TextWidget, MapWidget, ImageWidget...

After (factory):
  Dashboard knows about:
    createWidget(config)

  Factory knows about:
    ChartWidget, TableWidget, MetricWidget,
    TextWidget, MapWidget, ImageWidget...

Adding a new type:
  Before: Edit Dashboard + import new component
  After:  registerWidget("new", NewComponent) -- done
```

---

## Factory 2: Notification Factory

### Problem

Your app sends notifications through multiple channels: toast popups, browser notifications, email, and in-app messages. Each channel has a different API and different options.

### Before: Channel-Specific Code Everywhere

```javascript
// In CheckoutPage
if (Notification.permission === "granted") {
  new Notification("Order placed!", {
    body: "Your order #1234 has been confirmed.",
    icon: "/icons/success.png"
  });
}

// In SettingsPage
const toast = document.createElement("div");
toast.className = "toast toast-info";
toast.textContent = "Settings saved";
document.body.appendChild(toast);
setTimeout(() => toast.remove(), 3000);

// In ErrorBoundary
fetch("/api/notify", {
  method: "POST",
  body: JSON.stringify({
    channel: "email",
    to: adminEmail,
    subject: "App Error",
    body: errorDetails
  })
});
```

### After: Notification Factory

```javascript
// notificationFactory.js

const notificationCreators = {
  toast(config) {
    return {
      show() {
        const el = document.createElement("div");
        el.className = `toast toast-${config.variant || "info"}`;
        el.setAttribute("role", "alert");

        el.innerHTML = `
          <div class="toast-content">
            <span class="toast-icon">${getIcon(config.variant)}</span>
            <div>
              <strong>${config.title || ""}</strong>
              <p>${config.message}</p>
            </div>
            <button class="toast-close" onclick="this.parentElement.parentElement.remove()">
              x
            </button>
          </div>
        `;

        document.getElementById("toast-container").appendChild(el);

        const duration = config.duration || (config.variant === "error" ? 8000 : 4000);
        setTimeout(() => el.remove(), duration);
      }
    };
  },

  browser(config) {
    return {
      async show() {
        if (Notification.permission !== "granted") {
          const permission = await Notification.requestPermission();
          if (permission !== "granted") {
            // Fallback to toast
            return notificationCreators.toast(config).show();
          }
        }
        new Notification(config.title || "Notification", {
          body: config.message,
          icon: config.icon || "/icons/default.png"
        });
      }
    };
  },

  inApp(config) {
    return {
      show() {
        // Dispatch to in-app notification center
        window.dispatchEvent(
          new CustomEvent("app:notification", {
            detail: {
              id: Date.now(),
              title: config.title,
              message: config.message,
              variant: config.variant,
              read: false,
              timestamp: new Date().toISOString()
            }
          })
        );
      }
    };
  }
};

function getIcon(variant) {
  const icons = {
    success: "&#10003;",
    error: "&#10007;",
    warning: "&#9888;",
    info: "&#8505;"
  };
  return icons[variant] || icons.info;
}

function createNotification(channel, config) {
  const creator = notificationCreators[channel];
  if (!creator) {
    throw new Error(`Unknown notification channel: ${channel}`);
  }
  return creator(config);
}

// Convenience function: create and show immediately
function notify(channel, config) {
  const notification = createNotification(channel, config);
  notification.show();
  return notification;
}

export { createNotification, notify };
```

Usage is now clean and consistent:

```javascript
// Show a toast
notify("toast", {
  variant: "success",
  title: "Order placed!",
  message: "Your order #1234 has been confirmed."
});

// Show a browser notification
notify("browser", {
  title: "New message",
  message: "Alice sent you a message."
});

// Add to in-app notification center
notify("inApp", {
  variant: "info",
  title: "System update",
  message: "A new version is available."
});
```

---

## Factory 3: Chart Factory

### Problem

Your analytics dashboard shows different chart types. Each chart type needs different libraries, options, and data transformations.

```javascript
// chartFactory.js

const chartDefaults = {
  bar: {
    responsive: true,
    borderRadius: 4,
    categoryPercentage: 0.8
  },
  line: {
    responsive: true,
    tension: 0.4,
    fill: false,
    pointRadius: 4
  },
  pie: {
    responsive: true,
    cutout: "0%"
  },
  doughnut: {
    responsive: true,
    cutout: "60%"
  }
};

const colorPalettes = {
  default: ["#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#8b5cf6"],
  pastel: ["#93c5fd", "#fca5a5", "#6ee7b7", "#fcd34d", "#c4b5fd"],
  monochrome: ["#111827", "#374151", "#6b7280", "#9ca3af", "#d1d5db"]
};

function createChartConfig(type, data, options = {}) {
  const {
    title,
    palette = "default",
    animate = true,
    legend = true,
    ...restOptions
  } = options;

  // Validate type
  if (!chartDefaults[type]) {
    throw new Error(
      `Unknown chart type: "${type}". ` +
      `Available: ${Object.keys(chartDefaults).join(", ")}`
    );
  }

  // Apply colors from palette
  const colors = colorPalettes[palette] || colorPalettes.default;
  const coloredDatasets = data.datasets.map((dataset, i) => ({
    ...dataset,
    backgroundColor: dataset.backgroundColor || colors[i % colors.length],
    borderColor: dataset.borderColor || colors[i % colors.length]
  }));

  return {
    type,
    data: {
      ...data,
      datasets: coloredDatasets
    },
    options: {
      ...chartDefaults[type],
      ...restOptions,
      animation: animate ? { duration: 750 } : false,
      plugins: {
        legend: { display: legend },
        title: title
          ? { display: true, text: title, font: { size: 16 } }
          : { display: false }
      }
    }
  };
}

export { createChartConfig };
```

Usage:

```javascript
// Simple bar chart
const barConfig = createChartConfig("bar", {
  labels: ["Jan", "Feb", "Mar", "Apr"],
  datasets: [{ label: "Revenue", data: [12, 19, 3, 5] }]
}, {
  title: "Monthly Revenue",
  palette: "default"
});

// Line chart with custom options
const lineConfig = createChartConfig("line", {
  labels: ["Mon", "Tue", "Wed", "Thu", "Fri"],
  datasets: [
    { label: "This week", data: [65, 59, 80, 81, 56] },
    { label: "Last week", data: [28, 48, 40, 19, 86] }
  ]
}, {
  title: "Daily Active Users",
  palette: "pastel",
  legend: true
});

// Use with Chart.js
new Chart(canvasElement, barConfig);
new Chart(canvasElement, lineConfig);
```

---

## Factory 4: Form Field Factory

### Problem

Your app has dynamic forms where the fields are defined by a configuration (from a CMS, API, or admin panel). You need to render the right input component for each field type.

```javascript
// formFieldFactory.jsx

import React from "react";

const fieldComponents = {
  text({ name, label, value, onChange, placeholder, required }) {
    return (
      <div className="form-field">
        <label htmlFor={name}>
          {label} {required && <span className="required">*</span>}
        </label>
        <input
          id={name}
          name={name}
          type="text"
          value={value}
          onChange={onChange}
          placeholder={placeholder}
        />
      </div>
    );
  },

  textarea({ name, label, value, onChange, placeholder, rows = 4 }) {
    return (
      <div className="form-field">
        <label htmlFor={name}>{label}</label>
        <textarea
          id={name}
          name={name}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          rows={rows}
        />
      </div>
    );
  },

  select({ name, label, value, onChange, options = [] }) {
    return (
      <div className="form-field">
        <label htmlFor={name}>{label}</label>
        <select id={name} name={name} value={value} onChange={onChange}>
          <option value="">Select...</option>
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>
    );
  },

  checkbox({ name, label, value, onChange }) {
    return (
      <div className="form-field form-field-checkbox">
        <label>
          <input
            name={name}
            type="checkbox"
            checked={value}
            onChange={onChange}
          />
          {label}
        </label>
      </div>
    );
  },

  date({ name, label, value, onChange, min, max }) {
    return (
      <div className="form-field">
        <label htmlFor={name}>{label}</label>
        <input
          id={name}
          name={name}
          type="date"
          value={value}
          onChange={onChange}
          min={min}
          max={max}
        />
      </div>
    );
  }
};

function createFormField(fieldConfig, value, onChange) {
  const Component = fieldComponents[fieldConfig.type];

  if (!Component) {
    console.warn(`Unknown field type: "${fieldConfig.type}"`);
    return null;
  }

  return (
    <Component
      key={fieldConfig.name}
      {...fieldConfig}
      value={value}
      onChange={onChange}
    />
  );
}

export { createFormField };
```

Usage with a dynamic form:

```javascript
function DynamicForm({ fields, onSubmit }) {
  const [values, setValues] = useState({});

  function handleChange(e) {
    const { name, value, type, checked } = e.target;
    setValues((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value
    }));
  }

  return (
    <form onSubmit={(e) => { e.preventDefault(); onSubmit(values); }}>
      {fields.map((field) =>
        createFormField(field, values[field.name] || "", handleChange)
      )}
      <button type="submit">Submit</button>
    </form>
  );
}

// The fields come from configuration
const contactFields = [
  { type: "text", name: "name", label: "Full Name", required: true },
  { type: "text", name: "email", label: "Email", required: true },
  {
    type: "select",
    name: "subject",
    label: "Subject",
    options: [
      { value: "general", label: "General Inquiry" },
      { value: "support", label: "Technical Support" },
      { value: "billing", label: "Billing Question" }
    ]
  },
  { type: "textarea", name: "message", label: "Message", rows: 6 },
  { type: "checkbox", name: "subscribe", label: "Subscribe to newsletter" }
];

// Render the form
<DynamicForm fields={contactFields} onSubmit={handleSubmit} />
```

```
How the Form Field Factory works:

  Configuration (JSON):               Output (React components):

  { type: "text",                -->   <input type="text" ... />
    name: "email" }

  { type: "select",              -->   <select>
    name: "country",                     <option>US</option>
    options: [...] }                     <option>UK</option>
                                       </select>

  { type: "textarea",           -->   <textarea rows="4" ... />
    name: "bio" }

  { type: "checkbox",           -->   <input type="checkbox" ... />
    name: "agree" }

The factory picks the right component for each type.
```

---

## Factory with Registration Pattern

The most flexible factories allow runtime registration of new types:

```javascript
function createFactory(defaultTypes = {}) {
  const registry = { ...defaultTypes };

  function create(type, ...args) {
    const creator = registry[type];
    if (!creator) {
      throw new Error(
        `Unknown type: "${type}". ` +
        `Registered types: ${Object.keys(registry).join(", ")}`
      );
    }
    return creator(...args);
  }

  function register(type, creator) {
    if (registry[type]) {
      console.warn(`Overwriting existing type: "${type}"`);
    }
    registry[type] = creator;
  }

  function unregister(type) {
    delete registry[type];
  }

  function getTypes() {
    return Object.keys(registry);
  }

  return { create, register, unregister, getTypes };
}

// Usage
const buttonFactory = createFactory({
  primary: (props) => ({ ...props, variant: "primary", color: "blue" }),
  secondary: (props) => ({ ...props, variant: "secondary", color: "gray" }),
  danger: (props) => ({ ...props, variant: "danger", color: "red" })
});

console.log(buttonFactory.getTypes());
// Output: ["primary", "secondary", "danger"]

const btn = buttonFactory.create("primary", { label: "Click me" });
console.log(btn);
// Output: { label: 'Click me', variant: 'primary', color: 'blue' }

// Register a new type at runtime
buttonFactory.register("ghost", (props) => ({
  ...props,
  variant: "ghost",
  color: "transparent",
  border: "none"
}));

const ghostBtn = buttonFactory.create("ghost", { label: "Ghost" });
console.log(ghostBtn);
// Output: { label: 'Ghost', variant: 'ghost',
//           color: 'transparent', border: 'none' }
```

---

## Factory vs Constructor: When to Use Which

```
+------------------+-----------------------------------+----------------------------+
| Aspect           | Constructor (new Class)            | Factory Function           |
+------------------+-----------------------------------+----------------------------+
| Return type      | Always the same class              | Can return different types  |
| Flexibility      | Fixed construction logic           | Dynamic based on input     |
| Naming           | Must be class name                 | Can be descriptive name    |
| Testing          | Harder to mock                     | Easy to mock               |
| When to use      | You always want the same type      | You choose type at runtime |
+------------------+-----------------------------------+----------------------------+
```

---

## When to Use the Factory Pattern

```
+-----------------------------------------------+
|           USE FACTORY WHEN:                   |
+-----------------------------------------------+
|                                               |
|  * You create different types based on input  |
|  * Creation logic is complex or has many      |
|    configuration options                      |
|  * You want to centralize creation so changes |
|    happen in one place                        |
|  * You need runtime registration of new types |
|  * You want to decouple components from the   |
|    specific classes they use                  |
|  * Configuration-driven UIs (CMS, admin       |
|    panels, form builders)                     |
|                                               |
+-----------------------------------------------+

+-----------------------------------------------+
|       DO NOT USE FACTORY WHEN:                |
+-----------------------------------------------+
|                                               |
|  * You always create the same type of object  |
|  * Creation logic is simple (just "new X()")  |
|  * There are only 1-2 types and they rarely   |
|    change                                     |
|  * A simple if/else or ternary would be       |
|    clearer                                    |
|  * The factory just wraps a constructor with  |
|    no added value                             |
|                                               |
+-----------------------------------------------+
```

---

## Common Mistakes

### Mistake 1: Factory Returns Inconsistent Interfaces

```javascript
// WRONG -- different return shapes
function createShape(type) {
  if (type === "circle") {
    return { radius: 10, getArea: () => Math.PI * 100 };
  }
  if (type === "square") {
    return { sideLength: 10, calculateArea: () => 100 }; // Different method name!
  }
}

// CORRECT -- consistent interface
function createShape(type) {
  if (type === "circle") {
    return { type: "circle", dimensions: { radius: 10 }, getArea: () => Math.PI * 100 };
  }
  if (type === "square") {
    return { type: "square", dimensions: { side: 10 }, getArea: () => 100 };
  }
}
```

### Mistake 2: Factory Does Too Much

```javascript
// WRONG -- factory creates, validates, saves, and notifies
function createUser(data) {
  // Validate
  if (!data.name) throw new Error("Name required");
  // Create
  const user = { id: uuid(), ...data, createdAt: new Date() };
  // Save to database
  database.save("users", user);
  // Send welcome email
  emailService.send(user.email, "Welcome!");
  return user;
}

// CORRECT -- factory only creates
function createUser(data) {
  return {
    id: uuid(),
    name: data.name,
    email: data.email,
    createdAt: new Date(),
    role: data.role || "user"
  };
}

// Other functions handle other concerns
const user = createUser(data);
await userRepository.save(user);
await emailService.sendWelcome(user);
```

### Mistake 3: Hardcoding Types Instead of Using a Registry

```javascript
// WRONG -- adding a type requires editing the factory
function createChart(type, data) {
  switch (type) {
    case "bar": return new BarChart(data);
    case "line": return new LineChart(data);
    case "pie": return new PieChart(data);
    // Adding "radar" means editing this function
  }
}

// BETTER -- registry-based factory
const chartRegistry = {};

function registerChart(type, ChartClass) {
  chartRegistry[type] = ChartClass;
}

function createChart(type, data) {
  const ChartClass = chartRegistry[type];
  if (!ChartClass) throw new Error(`Unknown chart: ${type}`);
  return new ChartClass(data);
}

// Types can be registered from anywhere
registerChart("bar", BarChart);
registerChart("line", LineChart);
registerChart("pie", PieChart);
registerChart("radar", RadarChart); // No factory edit needed
```

---

## Best Practices

1. **Return consistent interfaces** -- all objects from a factory should have the same methods and properties, regardless of type.

2. **Keep factories focused on creation** -- a factory creates objects. It should not save, validate, or send notifications.

3. **Use a registry for extensibility** -- instead of a switch statement, use a map/object so new types can be registered without editing the factory.

4. **Provide sensible defaults** -- factories should fill in reasonable default values so callers do not need to specify everything.

5. **Validate input early** -- throw clear errors if the requested type does not exist or required configuration is missing.

6. **Make factories testable** -- accept dependencies as parameters rather than importing them internally.

---

## Quick Summary

The Factory pattern centralizes object creation. Instead of each part of the codebase knowing how to construct different types, a factory function takes a type or configuration and returns the right object. This makes adding new types easy, keeps creation logic consistent, and decouples the rest of the code from specific implementations.

```
Caller: "I need a bar chart"
          |
Factory:  (looks up "bar" in registry)
          (creates BarChart with defaults)
          (applies user config)
          (returns ready-to-use chart)
          |
Caller:  (uses chart -- does not care how it was made)
```

---

## Key Points

- The Factory pattern centralizes and simplifies object creation
- Factories return different objects based on input type or configuration
- Component factories are ideal for configuration-driven UIs (dashboards, form builders)
- Registry-based factories allow runtime registration of new types
- All factory products should share a consistent interface
- Factories should focus only on creation -- not validation, saving, or side effects
- Use factories when types are dynamic; skip them when you always create the same thing

---

## Practice Questions

1. What is the main difference between using a factory function and calling `new ClassName()` directly?

2. A dashboard supports 5 widget types. A new requirement adds 3 more. How does a factory-based approach make this easier than a switch statement in the component?

3. Why should all objects returned by a factory share a consistent interface? What problems arise if they do not?

4. Your form field factory currently supports `text`, `select`, and `checkbox`. How would you add a new `dateRange` field type using a registry pattern?

5. A colleague suggests creating a factory for user objects that also validates data and saves to the database. Why is this problematic?

---

## Exercises

### Exercise 1: HTTP Client Factory

Create a factory that builds pre-configured HTTP clients for different APIs. Each client should have `get`, `post`, `put`, and `delete` methods with the base URL, headers, and error handling baked in.

```javascript
function createAPIClient(config) {
  // Your code here
}

const githubAPI = createAPIClient({
  baseURL: "https://api.github.com",
  headers: { Accept: "application/vnd.github.v3+json" }
});

const internalAPI = createAPIClient({
  baseURL: "https://api.myapp.com/v2",
  headers: { Authorization: `Bearer ${token}` }
});

const repos = await githubAPI.get("/users/octocat/repos");
const users = await internalAPI.get("/users");
```

### Exercise 2: Theme Factory

Build a factory that creates complete theme objects from a minimal configuration (just a primary color and mode). The factory should generate complementary colors, typography scales, spacing, and shadows.

```javascript
function createTheme(config) {
  // Your code here
  // Hint: Derive secondary/accent colors from primary
  // Hint: Generate a type scale (12px, 14px, 16px, ...)
}

const lightTheme = createTheme({ primary: "#3b82f6", mode: "light" });
const darkTheme = createTheme({ primary: "#3b82f6", mode: "dark" });
```

### Exercise 3: Validation Rule Factory

Create a factory that builds validation functions from a declarative schema. The factory should support common rules (required, minLength, maxLength, email, pattern) and allow custom rules.

```javascript
function createValidator(schema) {
  // Your code here
}

const validateUser = createValidator({
  name: [{ rule: "required" }, { rule: "minLength", value: 2 }],
  email: [{ rule: "required" }, { rule: "email" }],
  age: [{ rule: "required" }, { rule: "min", value: 18 }]
});

const errors = validateUser({ name: "A", email: "bad", age: 15 });
// Output: { name: "Must be at least 2 characters",
//           email: "Invalid email",
//           age: "Must be at least 18" }
```

---

## What Is Next?

The Factory pattern centralizes how you create things. The next chapter covers the **Mediator pattern**, which centralizes how things communicate. Instead of objects talking directly to each other (creating a tangled web of dependencies), a mediator sits in the middle and coordinates all communication. You will see how this pattern simplifies complex component interactions.
