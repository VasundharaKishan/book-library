# Chapter 17: Styling in React

## Learning Goals

By the end of this chapter, you will be able to:

- Understand the different approaches to styling React components
- Use plain CSS with className and external stylesheets
- Apply inline styles with the style prop and JavaScript objects
- Scope styles to components with CSS Modules
- Build utility-first interfaces with Tailwind CSS
- Handle dynamic and conditional styling
- Implement responsive design patterns
- Create theme systems with CSS variables and Context
- Build reusable styled components
- Choose the right styling approach for your project

---

## Why Styling in React Is Different

In traditional HTML, you write CSS in a stylesheet and reference classes in your markup. React changes this in several important ways:

1. **Components, not pages** — You think in terms of isolated, reusable components, so styles should be scoped to components too
2. **JavaScript controls everything** — Styles often need to change based on state, props, or user interaction
3. **The `class` keyword is reserved** — You use `className` instead of `class`
4. **Build tools transform your CSS** — Tools like Vite process your CSS, enabling features like CSS Modules, PostCSS, and automatic vendor prefixes

There is no single "correct" way to style React apps. The community has developed many approaches, each with trade-offs. This chapter covers the most practical and widely used options.

---

## Approach 1: Plain CSS with className

The simplest approach — write CSS in a `.css` file and import it into your component.

### Basic Usage

```css
/* Button.css */
.button {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.button-primary {
  background-color: #3b82f6;
  color: white;
}

.button-primary:hover {
  background-color: #2563eb;
}

.button-secondary {
  background-color: #e5e7eb;
  color: #1f2937;
}

.button-secondary:hover {
  background-color: #d1d5db;
}

.button-danger {
  background-color: #ef4444;
  color: white;
}

.button-danger:hover {
  background-color: #dc2626;
}

.button-large {
  padding: 14px 28px;
  font-size: 18px;
}

.button-small {
  padding: 6px 12px;
  font-size: 14px;
}
```

```jsx
// Button.jsx
import "./Button.css";

function Button({ variant = "primary", size, children, ...props }) {
  const classes = [
    "button",
    `button-${variant}`,
    size && `button-${size}`,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <button className={classes} {...props}>
      {children}
    </button>
  );
}

// Usage
<Button variant="primary">Save</Button>
<Button variant="danger" size="small">Delete</Button>
<Button variant="secondary" size="large">Cancel</Button>
```

### Dynamic className with Template Literals

```jsx
function Alert({ type = "info", children }) {
  return (
    <div className={`alert alert-${type}`}>
      {children}
    </div>
  );
}
```

### Conditional Classes

```jsx
function NavLink({ to, children }) {
  const isActive = useIsActive(to);

  return (
    <a
      href={to}
      className={`nav-link ${isActive ? "nav-link-active" : ""}`}
    >
      {children}
    </a>
  );
}
```

### The clsx Utility

Manually concatenating class names gets messy with many conditions. The `clsx` library (or its alternative `classnames`) makes this cleaner:

```bash
npm install clsx
```

```jsx
import clsx from "clsx";

function Button({ variant, size, disabled, fullWidth, children }) {
  return (
    <button
      className={clsx(
        "button",
        `button-${variant}`,
        {
          "button-large": size === "large",
          "button-small": size === "small",
          "button-disabled": disabled,
          "button-full-width": fullWidth,
        }
      )}
      disabled={disabled}
    >
      {children}
    </button>
  );
}
```

`clsx` accepts strings, objects (where truthy values include the key as a class), and arrays. It ignores falsy values automatically:

```jsx
clsx("foo", "bar");              // "foo bar"
clsx("foo", false, "bar");       // "foo bar"
clsx({ active: true });          // "active"
clsx({ active: false });         // ""
clsx("btn", { active: isActive, large: isLarge }); // "btn active large"
```

### Pros and Cons of Plain CSS

**Pros:**
- No learning curve — standard CSS
- Full access to CSS features (animations, media queries, pseudo-selectors)
- Easy to migrate existing CSS
- No runtime overhead

**Cons:**
- **Global scope** — class names can collide across components
- Naming conventions (BEM, etc.) required to avoid collisions
- Dead CSS is hard to detect — unused styles accumulate over time
- No automatic connection between components and their styles

---

## Approach 2: Inline Styles

React supports inline styles through the `style` prop, which accepts a JavaScript object:

```jsx
function Card({ highlighted }) {
  return (
    <div
      style={{
        padding: "20px",
        borderRadius: "8px",
        backgroundColor: highlighted ? "#fffbeb" : "white",
        border: "1px solid #e5e7eb",
        boxShadow: "0 1px 3px rgba(0, 0, 0, 0.1)",
      }}
    >
      Card content
    </div>
  );
}
```

### Key Differences from CSS

| CSS | React Inline Style |
|-----|-------------------|
| `background-color` | `backgroundColor` |
| `font-size` | `fontSize` |
| `border-radius` | `borderRadius` |
| `z-index` | `zIndex` |
| `10px` | `"10px"` or `10` (for px values) |
| `2rem` | `"2rem"` |

CSS property names are written in camelCase. Numeric values default to pixels for most properties:

```jsx
// These are equivalent
style={{ fontSize: 16 }}
style={{ fontSize: "16px" }}

// But units other than px must be strings
style={{ fontSize: "2rem" }}
style={{ width: "50%" }}
```

### Style Objects as Variables

Extract style objects to keep JSX clean:

```jsx
const styles = {
  container: {
    display: "flex",
    gap: "1rem",
    padding: "2rem",
  },
  sidebar: {
    width: 250,
    backgroundColor: "#f9fafb",
    padding: "1rem",
    borderRadius: 8,
  },
  content: {
    flex: 1,
    padding: "1rem",
  },
};

function Layout({ children }) {
  return (
    <div style={styles.container}>
      <aside style={styles.sidebar}>Sidebar</aside>
      <main style={styles.content}>{children}</main>
    </div>
  );
}
```

### Merging Styles

You can merge style objects with the spread operator:

```jsx
function Box({ style, highlighted, children }) {
  return (
    <div
      style={{
        padding: "1rem",
        borderRadius: 8,
        backgroundColor: highlighted ? "#fef3c7" : "white",
        ...style, // Allow parent to override styles
      }}
    >
      {children}
    </div>
  );
}

// Usage — the parent overrides the padding
<Box highlighted style={{ padding: "2rem" }}>
  Custom padded box
</Box>
```

### When Inline Styles Make Sense

Inline styles are useful for:

- **Truly dynamic values** — positions, dimensions, colors calculated from props or state
- **Animation values** — transform, opacity, etc. driven by JavaScript
- **One-off overrides** — when a component instance needs a unique style

```jsx
// Good use of inline styles — values are truly dynamic
function ProgressBar({ percent }) {
  return (
    <div style={{ width: "100%", backgroundColor: "#e5e7eb", borderRadius: 4 }}>
      <div
        style={{
          width: `${percent}%`,
          height: 8,
          backgroundColor: percent === 100 ? "#10b981" : "#3b82f6",
          borderRadius: 4,
          transition: "width 0.3s ease",
        }}
      />
    </div>
  );
}
```

### Pros and Cons of Inline Styles

**Pros:**
- Scoped to the element — no naming collisions
- Dynamic values are natural — just JavaScript expressions
- No separate file needed
- Easy to understand — styles are right next to the markup

**Cons:**
- **No pseudo-selectors** — cannot do `:hover`, `:focus`, `::before`
- **No media queries** — cannot handle responsive design
- **No keyframe animations** — must use CSS for `@keyframes`
- **No cascading** — cannot style child elements or use selectors
- **Performance** — creates a new object on every render (minor issue in practice)
- Verbose for complex styling

The limitations are significant. Inline styles are best reserved for dynamic values that change based on state or props. For everything else, use CSS-based approaches.

---

## Approach 3: CSS Modules

CSS Modules solve the biggest problem with plain CSS — global scope. They automatically generate unique class names, so your styles never collide with other components.

### How CSS Modules Work

Name your CSS file with the `.module.css` extension:

```css
/* Button.module.css */
.button {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}

.primary {
  background-color: #3b82f6;
  color: white;
}

.primary:hover {
  background-color: #2563eb;
}

.secondary {
  background-color: #e5e7eb;
  color: #1f2937;
}

.large {
  padding: 14px 28px;
  font-size: 18px;
}

.fullWidth {
  width: 100%;
}
```

```jsx
// Button.jsx
import styles from "./Button.module.css";

function Button({ variant = "primary", size, fullWidth, children, ...props }) {
  return (
    <button
      className={`${styles.button} ${styles[variant]} ${
        size === "large" ? styles.large : ""
      } ${fullWidth ? styles.fullWidth : ""}`}
      {...props}
    >
      {children}
    </button>
  );
}
```

When you import a CSS Module, you get an object where the keys are the class names you defined and the values are unique, auto-generated names:

```jsx
console.log(styles);
// {
//   button: "Button_button_x7ht3",
//   primary: "Button_primary_a9f2k",
//   secondary: "Button_secondary_j3m1p",
//   large: "Button_large_k8n2q",
//   fullWidth: "Button_fullWidth_w4r5t",
// }
```

The generated names include the file name and a hash, making collisions virtually impossible. Two different components can both have a `.button` class without any conflict.

### CSS Modules with clsx

CSS Modules pair perfectly with `clsx`:

```jsx
import clsx from "clsx";
import styles from "./Button.module.css";

function Button({ variant = "primary", size, fullWidth, disabled, children, ...props }) {
  return (
    <button
      className={clsx(
        styles.button,
        styles[variant],
        {
          [styles.large]: size === "large",
          [styles.small]: size === "small",
          [styles.fullWidth]: fullWidth,
          [styles.disabled]: disabled,
        }
      )}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
}
```

### Composition in CSS Modules

CSS Modules support `composes` to inherit styles from other classes:

```css
/* base.module.css */
.text {
  font-family: -apple-system, BlinkMacSystemFont, sans-serif;
  line-height: 1.5;
}

.heading {
  composes: text;
  font-weight: 700;
  color: #111827;
}
```

```css
/* Card.module.css */
.card {
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: white;
}

.cardHeader {
  composes: heading from "./base.module.css";
  margin-bottom: 1rem;
  font-size: 1.25rem;
}
```

### Building a Component Library with CSS Modules

```css
/* Card.module.css */
.card {
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: white;
  overflow: hidden;
}

.elevated {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border: none;
}

.header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #f3f4f6;
  font-weight: 600;
  font-size: 1.1rem;
}

.body {
  padding: 1.5rem;
}

.footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #f3f4f6;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}
```

```jsx
// Card.jsx
import clsx from "clsx";
import styles from "./Card.module.css";

function Card({ elevated, className, children }) {
  return (
    <div className={clsx(styles.card, elevated && styles.elevated, className)}>
      {children}
    </div>
  );
}

function CardHeader({ children }) {
  return <div className={styles.header}>{children}</div>;
}

function CardBody({ children }) {
  return <div className={styles.body}>{children}</div>;
}

function CardFooter({ children }) {
  return <div className={styles.footer}>{children}</div>;
}

// Usage
<Card elevated>
  <CardHeader>User Profile</CardHeader>
  <CardBody>
    <p>Name: Jane Smith</p>
    <p>Email: jane@example.com</p>
  </CardBody>
  <CardFooter>
    <Button variant="secondary">Cancel</Button>
    <Button variant="primary">Save</Button>
  </CardFooter>
</Card>
```

Notice that `Card` accepts a `className` prop. This is a best practice — it lets the parent component add additional styles (like margin or positioning) without breaking the component's internal styles.

### Global Styles in CSS Modules

Sometimes you need to target global classes or third-party styles:

```css
/* Component.module.css */

/* This class is scoped (default) */
.wrapper {
  padding: 1rem;
}

/* This targets a global class (not scoped) */
:global(.some-library-class) {
  color: red;
}

/* Mix scoped and global */
.wrapper :global(.highlight) {
  background-color: yellow;
}
```

### Pros and Cons of CSS Modules

**Pros:**
- **Scoped by default** — no naming collisions, no BEM conventions needed
- Standard CSS — all features work (hover, media queries, animations)
- No runtime overhead — styles are extracted at build time
- Dead code detection — unused imports are easy to spot
- Built into Vite, Create React App, and Next.js — no extra setup

**Cons:**
- Class names are referenced as object properties, which is slightly more verbose
- Cannot share styles as easily as global CSS (but `composes` helps)
- Dynamic values still require inline styles or CSS variables

---

## Approach 4: Tailwind CSS

Tailwind CSS is a utility-first CSS framework. Instead of writing custom CSS, you compose styles from predefined utility classes directly in your markup.

### Setup with Vite

```bash
npm install tailwindcss @tailwindcss/vite
```

```js
// vite.config.js
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
});
```

```css
/* src/index.css */
@import "tailwindcss";
```

### Basic Usage

```jsx
function Button({ children }) {
  return (
    <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors">
      {children}
    </button>
  );
}
```

Every class does one thing:

| Class | CSS Property |
|-------|-------------|
| `px-4` | `padding-left: 1rem; padding-right: 1rem` |
| `py-2` | `padding-top: 0.5rem; padding-bottom: 0.5rem` |
| `bg-blue-500` | `background-color: #3b82f6` |
| `text-white` | `color: white` |
| `rounded` | `border-radius: 0.25rem` |
| `hover:bg-blue-600` | On hover: `background-color: #2563eb` |
| `transition-colors` | `transition-property: color, background-color...` |

### Building Components with Tailwind

```jsx
function Card({ children }) {
  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden">
      {children}
    </div>
  );
}

function CardHeader({ children }) {
  return (
    <div className="px-6 py-4 border-b border-gray-100 font-semibold text-lg">
      {children}
    </div>
  );
}

function CardBody({ children }) {
  return <div className="px-6 py-4">{children}</div>;
}

function Badge({ variant = "default", children }) {
  const variants = {
    default: "bg-gray-100 text-gray-800",
    success: "bg-green-100 text-green-800",
    warning: "bg-yellow-100 text-yellow-800",
    danger: "bg-red-100 text-red-800",
    info: "bg-blue-100 text-blue-800",
  };

  return (
    <span
      className={`inline-block px-2 py-1 text-xs font-medium rounded-full ${variants[variant]}`}
    >
      {children}
    </span>
  );
}
```

### Responsive Design with Tailwind

Tailwind uses mobile-first breakpoint prefixes:

| Prefix | Min Width | CSS |
|--------|-----------|-----|
| (none) | 0px | Default (mobile) |
| `sm:` | 640px | `@media (min-width: 640px)` |
| `md:` | 768px | `@media (min-width: 768px)` |
| `lg:` | 1024px | `@media (min-width: 1024px)` |
| `xl:` | 1280px | `@media (min-width: 1280px)` |

```jsx
function ProductGrid({ products }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 p-4">
      {products.map(product => (
        <div
          key={product.id}
          className="bg-white rounded-lg shadow p-4 hover:shadow-lg transition-shadow"
        >
          <img
            src={product.image}
            alt={product.name}
            className="w-full h-48 object-cover rounded mb-3"
          />
          <h3 className="font-semibold text-lg">{product.name}</h3>
          <p className="text-gray-600 text-sm mt-1">{product.description}</p>
          <p className="text-blue-600 font-bold mt-2">${product.price}</p>
        </div>
      ))}
    </div>
  );
}
```

This renders:
- **Mobile**: 1 column
- **Small screens (640px+)**: 2 columns
- **Large screens (1024px+)**: 3 columns
- **Extra large (1280px+)**: 4 columns

### Conditional Classes with Tailwind

```jsx
function Button({ variant = "primary", size = "md", disabled, children, ...props }) {
  const baseClasses = "font-medium rounded transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2";

  const variants = {
    primary: "bg-blue-500 text-white hover:bg-blue-600 focus:ring-blue-500",
    secondary: "bg-gray-200 text-gray-800 hover:bg-gray-300 focus:ring-gray-500",
    danger: "bg-red-500 text-white hover:bg-red-600 focus:ring-red-500",
    ghost: "bg-transparent text-gray-700 hover:bg-gray-100 focus:ring-gray-500",
  };

  const sizes = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-4 py-2 text-base",
    lg: "px-6 py-3 text-lg",
  };

  return (
    <button
      className={clsx(
        baseClasses,
        variants[variant],
        sizes[size],
        disabled && "opacity-50 cursor-not-allowed"
      )}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
}
```

### A Complete Page Layout

```jsx
function DashboardLayout({ children }) {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-xl font-bold text-gray-900">Dashboard</h1>
            <nav className="hidden md:flex space-x-8">
              <a href="/" className="text-gray-500 hover:text-gray-900">Home</a>
              <a href="/analytics" className="text-gray-500 hover:text-gray-900">Analytics</a>
              <a href="/settings" className="text-gray-500 hover:text-gray-900">Settings</a>
            </nav>
            <button className="md:hidden p-2">
              <span className="sr-only">Open menu</span>
              ☰
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar — hidden on mobile */}
          <aside className="hidden lg:block w-64 shrink-0">
            <nav className="bg-white rounded-lg shadow p-4 space-y-2">
              <a
                href="/dashboard"
                className="block px-3 py-2 rounded bg-blue-50 text-blue-700 font-medium"
              >
                Overview
              </a>
              <a
                href="/dashboard/users"
                className="block px-3 py-2 rounded text-gray-700 hover:bg-gray-50"
              >
                Users
              </a>
              <a
                href="/dashboard/products"
                className="block px-3 py-2 rounded text-gray-700 hover:bg-gray-50"
              >
                Products
              </a>
            </nav>
          </aside>

          {/* Content */}
          <main className="flex-1">{children}</main>
        </div>
      </div>
    </div>
  );
}
```

### Pros and Cons of Tailwind

**Pros:**
- **No naming decisions** — no class names to invent
- **No dead CSS** — unused utilities are excluded from the build
- **Consistent design system** — spacing, colors, typography are predefined
- **Rapid development** — style directly in JSX without switching files
- **Responsive design built in** — breakpoint prefixes are intuitive
- **Small production bundles** — only used utilities are included

**Cons:**
- **Long class strings** — components with many styles have verbose className attributes
- **Learning curve** — you need to learn the utility class names
- **Readability** — dense class strings can be hard to scan
- **Non-standard** — teammates who know CSS still need to learn Tailwind

---

## Responsive Design Patterns

Regardless of which styling approach you use, responsive design follows the same patterns in React.

### CSS Media Queries (Any Approach)

```css
/* Card.module.css */
.container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  padding: 1rem;
}

@media (min-width: 640px) {
  .container {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .container {
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
    padding: 2rem;
  }
}
```

### JavaScript-Based Responsive Logic

Sometimes you need to render different components (not just styles) based on screen size. Use a custom hook:

```jsx
import { useState, useEffect } from "react";

function useMediaQuery(query) {
  const [matches, setMatches] = useState(
    () => window.matchMedia(query).matches
  );

  useEffect(() => {
    const mediaQuery = window.matchMedia(query);

    function handleChange(e) {
      setMatches(e.matches);
    }

    mediaQuery.addEventListener("change", handleChange);
    return () => mediaQuery.removeEventListener("change", handleChange);
  }, [query]);

  return matches;
}

// Usage
function Navigation() {
  const isMobile = useMediaQuery("(max-width: 768px)");

  if (isMobile) {
    return <MobileNav />;
  }

  return <DesktopNav />;
}
```

### Responsive Component Pattern

```jsx
function DataDisplay({ data }) {
  const isMobile = useMediaQuery("(max-width: 768px)");

  // Show cards on mobile, table on desktop
  if (isMobile) {
    return (
      <div className="space-y-3">
        {data.map(item => (
          <div key={item.id} className="p-4 bg-white rounded shadow">
            <h3 className="font-bold">{item.name}</h3>
            <p>{item.email}</p>
            <p className="text-sm text-gray-500">{item.role}</p>
          </div>
        ))}
      </div>
    );
  }

  return (
    <table className="w-full bg-white rounded shadow">
      <thead>
        <tr>
          <th className="p-3 text-left">Name</th>
          <th className="p-3 text-left">Email</th>
          <th className="p-3 text-left">Role</th>
        </tr>
      </thead>
      <tbody>
        {data.map(item => (
          <tr key={item.id} className="border-t">
            <td className="p-3">{item.name}</td>
            <td className="p-3">{item.email}</td>
            <td className="p-3">{item.role}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

**Important:** Prefer CSS-based responsive design (media queries, flexbox, grid) whenever possible. Only use JavaScript-based responsive logic when you need to render entirely different component trees — CSS cannot add or remove elements from the DOM.

---

## Theme Systems

### Theming with CSS Variables

CSS custom properties (variables) provide a powerful way to build themes:

```css
/* themes.css */
:root {
  --color-primary: #3b82f6;
  --color-primary-hover: #2563eb;
  --color-background: #ffffff;
  --color-surface: #f9fafb;
  --color-text: #111827;
  --color-text-secondary: #6b7280;
  --color-border: #e5e7eb;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --radius: 8px;
  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

[data-theme="dark"] {
  --color-primary: #60a5fa;
  --color-primary-hover: #93bbfd;
  --color-background: #111827;
  --color-surface: #1f2937;
  --color-text: #f9fafb;
  --color-text-secondary: #9ca3af;
  --color-border: #374151;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
}
```

```css
/* Components use the variables */
.card {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  color: var(--color-text);
}

.button-primary {
  background-color: var(--color-primary);
  color: white;
}

.button-primary:hover {
  background-color: var(--color-primary-hover);
}
```

### Theme Toggle with React

```jsx
import { createContext, useContext, useState, useEffect } from "react";

const ThemeContext = createContext();

function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem("theme") || "light";
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  function toggleTheme() {
    setTheme(prev => (prev === "light" ? "dark" : "light"));
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within ThemeProvider");
  }
  return context;
}
```

```jsx
function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button onClick={toggleTheme}>
      {theme === "light" ? "🌙 Dark Mode" : "☀️ Light Mode"}
    </button>
  );
}

function App() {
  return (
    <ThemeProvider>
      <header>
        <ThemeToggle />
      </header>
      <main>
        {/* All components automatically respond to theme changes */}
        {/* because CSS variables cascade down the DOM */}
      </main>
    </ThemeProvider>
  );
}
```

The power of CSS variables: when you toggle `data-theme` on the root element, every component that uses `var(--color-...)` updates automatically. No prop passing, no re-rendering — CSS handles it.

### Theming with Tailwind

Tailwind supports dark mode out of the box:

```jsx
function Card({ children }) {
  return (
    <div className="bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
      {children}
    </div>
  );
}
```

Add the `dark:` prefix to any utility class, and it applies when dark mode is active. Configure Tailwind to use a class-based dark mode strategy so your theme toggle controls it:

```js
// tailwind.config.js
export default {
  darkMode: "class", // or "selector" in v4
  // ...
};
```

Then toggle the `dark` class on the `<html>` element:

```jsx
function toggleTheme() {
  document.documentElement.classList.toggle("dark");
}
```

---

## Animation and Transitions

### CSS Transitions

```css
/* Button.module.css */
.button {
  padding: 10px 20px;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.button:hover {
  background-color: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.button:active {
  transform: translateY(0);
}
```

### CSS Keyframe Animations

```css
/* Spinner.module.css */
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
```

```jsx
import styles from "./Spinner.module.css";

function Spinner() {
  return <div className={styles.spinner} />;
}
```

### State-Driven Animations

```jsx
import { useState } from "react";
import styles from "./Accordion.module.css";

function Accordion({ title, children }) {
  const [open, setOpen] = useState(false);

  return (
    <div className={styles.accordion}>
      <button
        className={styles.trigger}
        onClick={() => setOpen(!open)}
      >
        {title}
        <span className={`${styles.icon} ${open ? styles.iconOpen : ""}`}>
          ▸
        </span>
      </button>
      <div className={`${styles.content} ${open ? styles.contentOpen : ""}`}>
        <div className={styles.contentInner}>{children}</div>
      </div>
    </div>
  );
}
```

```css
/* Accordion.module.css */
.trigger {
  display: flex;
  justify-content: space-between;
  width: 100%;
  padding: 1rem;
  background: none;
  border: none;
  border-bottom: 1px solid #e5e7eb;
  cursor: pointer;
  font-size: 1rem;
}

.icon {
  transition: transform 0.2s ease;
}

.iconOpen {
  transform: rotate(90deg);
}

.content {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease;
}

.contentOpen {
  max-height: 500px;
}

.contentInner {
  padding: 1rem;
}
```

The trick: we animate `max-height` from `0` to a large value. The `overflow: hidden` clips the content while it transitions.

### Fade In/Out Pattern

```css
/* FadeIn.module.css */
.fadeIn {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

```jsx
import styles from "./FadeIn.module.css";

function Notification({ message, visible }) {
  if (!visible) return null;

  return (
    <div className={styles.fadeIn}>
      {message}
    </div>
  );
}
```

---

## Organizing Styles in a Project

### Co-Located Styles (Recommended)

Place styles next to the component they belong to:

```
src/
  components/
    Button/
      Button.jsx
      Button.module.css
    Card/
      Card.jsx
      Card.module.css
    Modal/
      Modal.jsx
      Modal.module.css
  styles/
    global.css         ← resets, base styles, CSS variables
    themes.css         ← theme definitions
```

This structure makes it obvious which styles belong to which component. When you delete a component, you delete its styles too.

### Global Styles

Some styles are truly global — resets, typography defaults, CSS variables. Keep these in a dedicated global stylesheet:

```css
/* global.css */

/* Reset */
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* Base typography */
body {
  font-family: var(--font-sans);
  color: var(--color-text);
  background-color: var(--color-background);
  line-height: 1.6;
}

/* Links */
a {
  color: var(--color-primary);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

/* Utility classes */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}
```

Import this once in your entry point:

```jsx
// main.jsx
import "./styles/global.css";
```

---

## Mini Project: Component Library

Let us build a small, themeable component library using CSS Modules. This demonstrates how styling approaches work together in practice.

```css
/* theme.css — imported once in main.jsx */
:root {
  --color-primary: #3b82f6;
  --color-primary-hover: #2563eb;
  --color-primary-light: #dbeafe;
  --color-success: #10b981;
  --color-success-light: #d1fae5;
  --color-warning: #f59e0b;
  --color-warning-light: #fef3c7;
  --color-danger: #ef4444;
  --color-danger-hover: #dc2626;
  --color-danger-light: #fee2e2;
  --color-bg: #ffffff;
  --color-surface: #f9fafb;
  --color-text: #111827;
  --color-text-muted: #6b7280;
  --color-border: #e5e7eb;
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --transition: 0.2s ease;
}

[data-theme="dark"] {
  --color-primary: #60a5fa;
  --color-primary-hover: #93c5fd;
  --color-primary-light: #1e3a5f;
  --color-success: #34d399;
  --color-success-light: #064e3b;
  --color-warning: #fbbf24;
  --color-warning-light: #78350f;
  --color-danger: #f87171;
  --color-danger-hover: #fca5a5;
  --color-danger-light: #7f1d1d;
  --color-bg: #0f172a;
  --color-surface: #1e293b;
  --color-text: #f1f5f9;
  --color-text-muted: #94a3b8;
  --color-border: #334155;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background-color: var(--color-bg);
  color: var(--color-text);
  line-height: 1.6;
}
```

```css
/* Button.module.css */
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition);
  line-height: 1;
}

.button:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Sizes */
.sm { padding: 0.375rem 0.75rem; font-size: 0.8125rem; }
.md { padding: 0.5rem 1rem; font-size: 0.875rem; }
.lg { padding: 0.625rem 1.25rem; font-size: 1rem; }

/* Variants */
.primary {
  background-color: var(--color-primary);
  color: white;
}
.primary:hover:not(:disabled) {
  background-color: var(--color-primary-hover);
}

.secondary {
  background-color: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}
.secondary:hover:not(:disabled) {
  background-color: var(--color-border);
}

.danger {
  background-color: var(--color-danger);
  color: white;
}
.danger:hover:not(:disabled) {
  background-color: var(--color-danger-hover);
}

.ghost {
  background-color: transparent;
  color: var(--color-text);
}
.ghost:hover:not(:disabled) {
  background-color: var(--color-surface);
}

.fullWidth {
  width: 100%;
}
```

```jsx
// Button.jsx
import clsx from "clsx";
import styles from "./Button.module.css";

function Button({
  variant = "primary",
  size = "md",
  fullWidth = false,
  disabled = false,
  children,
  className,
  ...props
}) {
  return (
    <button
      className={clsx(
        styles.button,
        styles[variant],
        styles[size],
        fullWidth && styles.fullWidth,
        className
      )}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
}
```

```css
/* Input.module.css */
.wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text);
}

.input {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  color: var(--color-text);
  background-color: var(--color-bg);
  transition: border-color var(--transition), box-shadow var(--transition);
}

.input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

.input::placeholder {
  color: var(--color-text-muted);
}

.error .input {
  border-color: var(--color-danger);
}

.error .input:focus {
  box-shadow: 0 0 0 3px var(--color-danger-light);
}

.errorMessage {
  font-size: 0.8125rem;
  color: var(--color-danger);
}

.hint {
  font-size: 0.8125rem;
  color: var(--color-text-muted);
}
```

```jsx
// Input.jsx
import clsx from "clsx";
import styles from "./Input.module.css";

function Input({
  label,
  error,
  hint,
  id,
  className,
  ...props
}) {
  const inputId = id || label?.toLowerCase().replace(/\s+/g, "-");

  return (
    <div className={clsx(styles.wrapper, error && styles.error, className)}>
      {label && (
        <label htmlFor={inputId} className={styles.label}>
          {label}
        </label>
      )}
      <input id={inputId} className={styles.input} {...props} />
      {error && <p className={styles.errorMessage}>{error}</p>}
      {hint && !error && <p className={styles.hint}>{hint}</p>}
    </div>
  );
}
```

```css
/* Alert.module.css */
.alert {
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.info {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
  border: 1px solid var(--color-primary);
}

.success {
  background-color: var(--color-success-light);
  color: var(--color-success);
  border: 1px solid var(--color-success);
}

.warning {
  background-color: var(--color-warning-light);
  color: var(--color-warning);
  border: 1px solid var(--color-warning);
}

.danger {
  background-color: var(--color-danger-light);
  color: var(--color-danger);
  border: 1px solid var(--color-danger);
}

.content {
  flex: 1;
}

.title {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.dismiss {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.25rem;
  line-height: 1;
  opacity: 0.7;
  color: inherit;
}

.dismiss:hover {
  opacity: 1;
}
```

```jsx
// Alert.jsx
import { useState } from "react";
import clsx from "clsx";
import styles from "./Alert.module.css";

function Alert({ variant = "info", title, dismissible = false, children, className }) {
  const [visible, setVisible] = useState(true);

  if (!visible) return null;

  return (
    <div className={clsx(styles.alert, styles[variant], className)}>
      <div className={styles.content}>
        {title && <div className={styles.title}>{title}</div>}
        {children}
      </div>
      {dismissible && (
        <button className={styles.dismiss} onClick={() => setVisible(false)}>
          ×
        </button>
      )}
    </div>
  );
}
```

```css
/* Modal.module.css */
.overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  animation: fadeIn 0.15s ease;
}

.modal {
  background-color: var(--color-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  width: 90%;
  max-width: 500px;
  max-height: 85vh;
  overflow-y: auto;
  animation: slideUp 0.2s ease;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.title {
  font-size: 1.125rem;
  font-weight: 600;
}

.close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--color-text-muted);
  line-height: 1;
}

.close:hover {
  color: var(--color-text);
}

.body {
  padding: 1.5rem;
}

.footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--color-border);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
```

```jsx
// Modal.jsx
import { useEffect } from "react";
import styles from "./Modal.module.css";

function Modal({ open, onClose, title, children, footer }) {
  // Prevent background scrolling when modal is open
  useEffect(() => {
    if (open) {
      document.body.style.overflow = "hidden";
      return () => {
        document.body.style.overflow = "";
      };
    }
  }, [open]);

  // Close on Escape key
  useEffect(() => {
    if (!open) return;

    function handleKeyDown(e) {
      if (e.key === "Escape") onClose();
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={e => e.stopPropagation()}>
        <div className={styles.header}>
          <h2 className={styles.title}>{title}</h2>
          <button className={styles.close} onClick={onClose}>
            ×
          </button>
        </div>
        <div className={styles.body}>{children}</div>
        {footer && <div className={styles.footer}>{footer}</div>}
      </div>
    </div>
  );
}
```

### Using the Component Library Together

```jsx
// Demo.jsx — showcasing all components
import { useState } from "react";

function ComponentDemo() {
  const [modalOpen, setModalOpen] = useState(false);
  const [formData, setFormData] = useState({ name: "", email: "" });
  const [errors, setErrors] = useState({});

  function handleSubmit(e) {
    e.preventDefault();
    const newErrors = {};
    if (!formData.name) newErrors.name = "Name is required";
    if (!formData.email) newErrors.email = "Email is required";

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setErrors({});
    setModalOpen(true);
  }

  return (
    <div style={{ maxWidth: 600, margin: "2rem auto", padding: "0 1rem" }}>
      <h1>Component Library Demo</h1>

      {/* Alerts */}
      <section style={{ marginTop: "2rem" }}>
        <h2>Alerts</h2>
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem", marginTop: "1rem" }}>
          <Alert variant="info" title="Information">
            This is an informational message.
          </Alert>
          <Alert variant="success" dismissible>
            Your changes have been saved.
          </Alert>
          <Alert variant="warning" title="Warning">
            Your session will expire in 5 minutes.
          </Alert>
          <Alert variant="danger" title="Error" dismissible>
            Failed to save changes. Please try again.
          </Alert>
        </div>
      </section>

      {/* Form */}
      <section style={{ marginTop: "2rem" }}>
        <h2>Form</h2>
        <form onSubmit={handleSubmit} style={{ marginTop: "1rem" }}>
          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <Input
              label="Full Name"
              value={formData.name}
              onChange={e =>
                setFormData(prev => ({ ...prev, name: e.target.value }))
              }
              error={errors.name}
              placeholder="Enter your name"
            />
            <Input
              label="Email Address"
              type="email"
              value={formData.email}
              onChange={e =>
                setFormData(prev => ({ ...prev, email: e.target.value }))
              }
              error={errors.email}
              hint="We will never share your email"
              placeholder="you@example.com"
            />
          </div>
          <div style={{ display: "flex", gap: "0.75rem", marginTop: "1.5rem" }}>
            <Button type="submit">Submit</Button>
            <Button variant="secondary" type="button">
              Cancel
            </Button>
            <Button variant="danger" type="button">
              Delete
            </Button>
            <Button variant="ghost" type="button">
              Ghost
            </Button>
          </div>
        </form>
      </section>

      {/* Button sizes */}
      <section style={{ marginTop: "2rem" }}>
        <h2>Button Sizes</h2>
        <div style={{ display: "flex", gap: "0.75rem", alignItems: "center", marginTop: "1rem" }}>
          <Button size="sm">Small</Button>
          <Button size="md">Medium</Button>
          <Button size="lg">Large</Button>
          <Button disabled>Disabled</Button>
        </div>
      </section>

      {/* Modal */}
      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Confirm Submission"
        footer={
          <>
            <Button variant="secondary" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => setModalOpen(false)}>Confirm</Button>
          </>
        }
      >
        <p>Are you sure you want to submit this form?</p>
        <div style={{ marginTop: "1rem", padding: "1rem", backgroundColor: "var(--color-surface)", borderRadius: "var(--radius-sm)" }}>
          <p><strong>Name:</strong> {formData.name}</p>
          <p><strong>Email:</strong> {formData.email}</p>
        </div>
      </Modal>
    </div>
  );
}
```

This mini project demonstrates:

- **CSS Modules** for scoped, collision-free styles
- **CSS Variables** for theming (light and dark mode)
- **clsx** for clean conditional class application
- **Animations** with CSS keyframes and transitions
- **Reusable components** with variant and size props
- **Accessible patterns** — focus styles, keyboard handling, ARIA attributes
- **Component composition** — Modal with header, body, and footer slots

---

## Choosing the Right Approach

| Factor | Plain CSS | CSS Modules | Tailwind | Inline Styles |
|--------|-----------|-------------|----------|---------------|
| Learning curve | Low | Low | Medium | Low |
| Scoping | Global | Scoped | Scoped (utility) | Scoped |
| Dynamic values | CSS variables | CSS variables | Class toggling | Natural |
| Pseudo-selectors | Yes | Yes | Yes | No |
| Media queries | Yes | Yes | Yes (prefixes) | No |
| Animations | Yes | Yes | Yes | Limited |
| Bundle size | Medium | Small | Small | Zero |
| Team onboarding | Easy | Easy | Requires learning | Easy |
| Tooling required | None | Build tool | Build tool + config | None |

### Recommendations

- **Small project, solo developer**: Plain CSS or Tailwind
- **Medium project, small team**: CSS Modules — best balance of simplicity and safety
- **Large project, many developers**: CSS Modules or Tailwind — scoping prevents conflicts
- **Component library**: CSS Modules with CSS variables for theming
- **Rapid prototyping**: Tailwind — fastest to build with
- **Dynamic values from state**: Inline styles for the dynamic parts, CSS for everything else

### Mixing Approaches

You can combine approaches. Many projects use:

- **Global CSS** for resets, typography, and CSS variables
- **CSS Modules** for component-specific styles
- **Inline styles** for truly dynamic values (positions, calculated colors)

```jsx
import styles from "./ProgressBar.module.css";

function ProgressBar({ percent, color }) {
  return (
    <div className={styles.track}>
      <div
        className={styles.fill}
        style={{
          width: `${percent}%`,           // Dynamic — inline style
          backgroundColor: color,          // Dynamic — inline style
        }}
      />
    </div>
  );
}
```

The static styles (border-radius, height, transition) live in the CSS Module. The dynamic values (width, color) are inline. Each approach handles what it does best.

---

## Common Mistakes

### Mistake 1: Using class Instead of className

```jsx
// WRONG — "class" is a reserved word in JavaScript
<div class="container">Content</div>

// CORRECT
<div className="container">Content</div>
```

### Mistake 2: Passing a String to the style Prop

```jsx
// WRONG — style expects an object, not a string
<div style="color: red; font-size: 16px">Content</div>

// CORRECT — use an object with camelCase properties
<div style={{ color: "red", fontSize: 16 }}>Content</div>
```

### Mistake 3: Creating New Style Objects on Every Render

```jsx
// WASTEFUL — creates a new object every render
function Card() {
  return <div style={{ padding: "1rem", border: "1px solid #ddd" }}>...</div>;
}

// BETTER — define outside the component
const cardStyle = { padding: "1rem", border: "1px solid #ddd" };

function Card() {
  return <div style={cardStyle}>...</div>;
}
```

For static styles, this is a minor optimization. For styles passed to memoized children, it prevents unnecessary re-renders.

### Mistake 4: Not Accepting className from Parent

```jsx
// WRONG — parent cannot add margin, positioning, etc.
function Card({ children }) {
  return <div className={styles.card}>{children}</div>;
}

// CORRECT — allow parent to extend styles
function Card({ children, className }) {
  return (
    <div className={clsx(styles.card, className)}>
      {children}
    </div>
  );
}

// Now parent can add spacing
<Card className="mt-4">Content</Card>
```

### Mistake 5: Overusing Inline Styles

```jsx
// WRONG — inline styles for everything
function Card() {
  return (
    <div
      style={{
        padding: "1.5rem",
        borderRadius: 8,
        border: "1px solid #e5e7eb",
        backgroundColor: "white",
        boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
      }}
    >
      <h3 style={{ fontSize: "1.25rem", fontWeight: 600, marginBottom: "0.5rem" }}>
        Title
      </h3>
      <p style={{ color: "#666", lineHeight: 1.6 }}>
        Description text here.
      </p>
    </div>
  );
}

// CORRECT — use CSS for static styles
// Card.module.css has .card, .title, .description
function Card() {
  return (
    <div className={styles.card}>
      <h3 className={styles.title}>Title</h3>
      <p className={styles.description}>Description text here.</p>
    </div>
  );
}
```

---

## Best Practices

1. **Choose one primary approach and be consistent** — Mixing too many styling approaches creates confusion. Pick CSS Modules or Tailwind as your primary method and use inline styles only for truly dynamic values.

2. **Co-locate styles with components** — Place `Button.module.css` next to `Button.jsx`. When you delete the component, the styles go with it.

3. **Accept className as a prop** — Reusable components should let parents add classes for positioning and spacing.

4. **Use CSS variables for theming** — CSS variables cascade naturally, require no re-renders, and work with any styling approach.

5. **Prefer CSS for responsive design** — Media queries and CSS Grid/Flexbox handle most responsive layouts. Only use JavaScript (`useMediaQuery`) when you need to render different component structures.

6. **Use clsx for conditional classes** — It is cleaner and more readable than manual string concatenation with ternaries.

7. **Add focus-visible styles** — Every interactive element should have a visible focus indicator for keyboard users. Never set `outline: none` without providing an alternative.

8. **Avoid magic numbers** — Use CSS variables or a design system's spacing scale instead of hardcoded pixel values scattered throughout your code.

---

## Summary

In this chapter, you learned:

- **Plain CSS** with `className` is simple but has global scope — class names can collide across components
- **Inline styles** use JavaScript objects and are scoped to elements, but cannot handle pseudo-selectors, media queries, or keyframe animations
- **CSS Modules** (`.module.css`) automatically generate unique class names, preventing collisions while using standard CSS
- **Tailwind CSS** uses utility classes directly in JSX for rapid development with a consistent design system
- **clsx** simplifies conditional class name logic
- **CSS variables** enable powerful theming that works across all styling approaches
- **Theme toggling** combines CSS variables with React Context for dark/light mode
- **Responsive design** is best handled with CSS media queries; use JavaScript only when you need to change the component tree
- **Animations** work with CSS transitions and keyframes, toggled by adding/removing classes based on state
- **Component libraries** benefit from CSS Modules with CSS variables for consistent, themeable, scoped styles

---

## Interview Questions

1. **What is the difference between className and class in React?**

   In React, you use `className` instead of `class` because `class` is a reserved keyword in JavaScript (used for class declarations). When JSX compiles to `React.createElement`, properties are JavaScript identifiers, so `class` would cause a syntax conflict. React translates `className` to the `class` attribute in the rendered HTML.

2. **What are CSS Modules and what problem do they solve?**

   CSS Modules are CSS files (named with `.module.css`) where class names are automatically scoped to the component that imports them. The build tool generates unique class names (like `Button_primary_x7ht3`) that prevent naming collisions between components. This solves the global scope problem of plain CSS — two components can both define a `.button` class without conflicting.

3. **When would you use inline styles vs CSS in React?**

   Use inline styles for truly dynamic values that change based on state or props — calculated positions, widths from percentages, colors from data. Use CSS (Modules, plain CSS, or Tailwind) for everything else. Inline styles cannot handle pseudo-selectors (`:hover`, `:focus`), media queries, keyframe animations, or style inheritance, so they should complement CSS rather than replace it.

4. **How do CSS variables enable theming in React?**

   CSS variables (custom properties like `--color-primary`) are defined on a parent element (usually `:root`) and cascade down to all children. To implement themes, define different variable values under different selectors (e.g., `[data-theme="dark"]`). When you toggle the `data-theme` attribute via React state, all components using those variables update automatically through CSS cascade — no prop drilling, no re-rendering required.

5. **What is the advantage of Tailwind CSS over writing custom CSS?**

   Tailwind eliminates the need to invent class names and switch between files. Styles are applied directly in JSX using predefined utility classes. Its purge system removes unused utilities, resulting in small production bundles. It enforces a consistent design system (spacing, colors, typography) out of the box. Responsive design uses intuitive breakpoint prefixes (`sm:`, `md:`, `lg:`). However, it requires learning the utility class names and can make JSX verbose with long class strings.

---

## Practice Exercises

### Exercise 1: Design System Tokens

Create a design system with CSS variables for spacing (4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px), a color palette (primary, secondary, success, warning, danger — each with light, default, and dark variants), and typography (headings, body, small, caption). Build components that use only these tokens — no hardcoded values.

### Exercise 2: Responsive Navigation

Build a navigation bar that shows horizontal links on desktop and a hamburger menu with a slide-out drawer on mobile. Use CSS for the responsive layout and JavaScript only for toggling the mobile menu open/closed. Add smooth transitions for the drawer.

### Exercise 3: Theme Switcher

Build a theme system with at least three themes (light, dark, and a custom "ocean" theme). Store the user's preference in localStorage. Add a theme picker component that shows a preview of each theme. All components should respond to theme changes through CSS variables.

### Exercise 4: Animated Card Grid

Create a grid of cards that fade in with a staggered animation when the page loads (each card appears 100ms after the previous one). Cards should lift with a shadow on hover. Clicking a card expands it to show more content with a smooth height transition. Use CSS Modules for scoped styles and inline styles for the stagger delay.

---

## What Is Next?

In Chapter 18, we will explore **State Management at Scale** — understanding when Context is not enough, and how external state management libraries like Redux Toolkit and Zustand help manage complex application state with predictable patterns.
