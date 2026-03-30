# Chapter 20: Accessibility in React

## Learning Goals

By the end of this chapter, you will be able to:

- Understand why accessibility matters and who benefits from it
- Use semantic HTML elements instead of generic divs and spans
- Add ARIA attributes correctly in JSX
- Build keyboard-navigable interactive components
- Manage focus programmatically with refs
- Create accessible forms with proper labels and error messages
- Handle dynamic content announcements for screen readers
- Build accessible modals, dropdown menus, and tabs
- Test your application for accessibility issues
- Follow the most impactful accessibility practices

---

## Why Accessibility Matters

Accessibility (often abbreviated as **a11y** — "a" + 11 letters + "y") means building applications that everyone can use, including people with disabilities. This includes:

- **Visual impairments** — blindness, low vision, color blindness (screen reader users, magnifier users)
- **Motor impairments** — limited dexterity, tremors, paralysis (keyboard-only users, switch device users)
- **Hearing impairments** — deafness, hard of hearing (captions, visual indicators)
- **Cognitive impairments** — dyslexia, ADHD, autism (clear language, consistent navigation)
- **Temporary impairments** — broken arm, eye infection, bright sunlight on screen

Accessibility is not just about helping a small group. According to the WHO, over 1 billion people — 16% of the world's population — live with some form of disability. And everyone benefits from good accessibility: keyboard shortcuts help power users, captions help people in noisy environments, and clear structure helps everyone navigate faster.

Accessibility is also a legal requirement in many countries. The Americans with Disabilities Act (ADA), the European Accessibility Act, and Section 508 of the Rehabilitation Act all mandate accessible digital products. Companies have faced lawsuits for inaccessible websites.

### The Good News for React Developers

Most accessibility comes from writing good HTML. If you use the right HTML elements, the browser and assistive technologies handle the heavy lifting. The biggest accessibility failures come from using `<div>` and `<span>` for everything instead of semantic elements like `<button>`, `<nav>`, `<main>`, and `<label>`.

---

## Semantic HTML: The Foundation

Semantic HTML means using HTML elements that carry meaning, not just visual appearance. A `<button>` is not just a styled clickable area — it communicates to the browser, screen readers, and keyboard navigation that this element is interactive and triggerable.

### The Problem with Div-Everything

```jsx
// WRONG — looks like a button but is not accessible
<div
  className="button"
  onClick={handleClick}
  style={{ cursor: "pointer", padding: "8px 16px", backgroundColor: "#3b82f6", color: "white", borderRadius: 4 }}
>
  Save Changes
</div>
```

This div-button looks right visually, but it is broken for accessibility:

- **Keyboard users cannot reach it** — divs are not in the tab order
- **Screen readers do not announce it as a button** — they read it as plain text
- **Enter and Space keys do not trigger it** — only clicks work
- **No focus indicator** — users cannot see when it is selected

To "fix" the div, you would need to add `tabIndex`, `role`, `onKeyDown` for Enter and Space, focus styles, and ARIA attributes. Or you could just use a `<button>`:

```jsx
// CORRECT — accessible by default
<button onClick={handleClick}>Save Changes</button>
```

The `<button>` element provides all of this for free: keyboard focusable, announced as "button" by screen readers, triggered by Enter and Space, and shows a focus outline.

### Semantic Elements You Should Use

| Instead of | Use | Why |
|------------|-----|-----|
| `<div onClick>` | `<button>` | Interactive, focusable, keyboard-accessible |
| `<div>` for navigation | `<nav>` | Screen readers identify it as navigation |
| `<div>` for main content | `<main>` | Screen readers can jump to it |
| `<div>` for header | `<header>` | Defines the page or section header |
| `<div>` for footer | `<footer>` | Defines the page or section footer |
| `<div>` for sidebar | `<aside>` | Identifies complementary content |
| `<div>` for sections | `<section>` | Groups related content with a heading |
| `<span onClick>` | `<a href>` or `<button>` | Links navigate, buttons perform actions |
| `<div>` for a list | `<ul>` / `<ol>` | Screen readers announce "list, 5 items" |
| `<b>` | `<strong>` | Semantic emphasis, not just visual boldness |
| `<i>` | `<em>` | Semantic emphasis, not just visual italics |

### A Semantic Page Layout

```jsx
function App() {
  return (
    <>
      <header>
        <nav aria-label="Main navigation">
          <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/about">About</a></li>
            <li><a href="/contact">Contact</a></li>
          </ul>
        </nav>
      </header>

      <main>
        <h1>Welcome to Our Site</h1>
        <section aria-labelledby="featured-heading">
          <h2 id="featured-heading">Featured Articles</h2>
          <article>
            <h3>Understanding React Accessibility</h3>
            <p>Learn how to build accessible React applications...</p>
          </article>
        </section>
      </main>

      <aside aria-label="Related links">
        <h2>Related Resources</h2>
        <ul>
          <li><a href="/docs">Documentation</a></li>
          <li><a href="/tutorials">Tutorials</a></li>
        </ul>
      </aside>

      <footer>
        <p>&copy; 2025 Our Company</p>
      </footer>
    </>
  );
}
```

Screen reader users can jump directly to `<main>`, `<nav>`, or `<aside>` using landmark navigation. This is impossible with a page built entirely from `<div>` elements.

---

## ARIA Attributes in React

ARIA (Accessible Rich Internet Applications) attributes provide additional context to assistive technologies when HTML alone is not enough. In JSX, ARIA attributes use the same hyphenated names as in HTML:

```jsx
// ARIA attributes work directly in JSX
<button aria-label="Close dialog">×</button>
<div role="alert">Your changes have been saved.</div>
<input aria-describedby="password-hint" type="password" />
<nav aria-label="Breadcrumb">...</nav>
```

### The First Rule of ARIA

> **No ARIA is better than bad ARIA.**

ARIA does not add behavior — it only adds metadata for assistive technologies. Using ARIA incorrectly is worse than not using it at all, because it can mislead screen reader users. Always prefer native HTML elements before reaching for ARIA.

```jsx
// WRONG — using ARIA to recreate what a <button> already provides
<div role="button" tabIndex={0} aria-pressed="false" onClick={handleClick} onKeyDown={handleKeyDown}>
  Click me
</div>

// CORRECT — the <button> handles everything
<button onClick={handleClick}>Click me</button>
```

### Common ARIA Attributes

**`aria-label`** — Provides an accessible name when there is no visible text:

```jsx
// The button only has an icon — screen readers need a text alternative
<button aria-label="Search" onClick={openSearch}>
  🔍
</button>

// Navigation sections need labels to distinguish them
<nav aria-label="Main navigation">...</nav>
<nav aria-label="Footer navigation">...</nav>
```

**`aria-labelledby`** — Points to another element that serves as the label:

```jsx
<section aria-labelledby="section-title">
  <h2 id="section-title">Recent Orders</h2>
  {/* section content */}
</section>
```

**`aria-describedby`** — Points to an element that provides additional description:

```jsx
<input
  type="password"
  aria-describedby="password-requirements"
/>
<p id="password-requirements">
  Password must be at least 8 characters with one number.
</p>
```

**`aria-hidden`** — Hides an element from screen readers while keeping it visually present:

```jsx
// Decorative icon — screen readers should ignore it
<span aria-hidden="true">🎨</span>

// The text next to it provides the meaning
<span>Design Tools</span>
```

**`aria-live`** — Announces dynamic content changes to screen readers:

```jsx
// "polite" waits for the user to finish, "assertive" interrupts immediately
<div aria-live="polite">
  {notification && <p>{notification}</p>}
</div>
```

**`aria-expanded`** — Indicates whether a collapsible section is open:

```jsx
<button
  aria-expanded={isOpen}
  aria-controls="dropdown-menu"
  onClick={() => setIsOpen(!isOpen)}
>
  Menu
</button>
<div id="dropdown-menu" hidden={!isOpen}>
  {/* dropdown content */}
</div>
```

**`role`** — Defines the purpose of an element when the HTML element does not convey it:

```jsx
// Alert messages
<div role="alert">Error: Invalid email address.</div>

// Status updates
<div role="status">3 items in your cart.</div>

// Tab interfaces
<div role="tablist">
  <button role="tab" aria-selected={activeTab === 0}>Tab 1</button>
  <button role="tab" aria-selected={activeTab === 1}>Tab 2</button>
</div>
```

---

## Keyboard Navigation

Many users navigate with a keyboard instead of a mouse. Some use a keyboard because of motor impairments, others prefer keyboard shortcuts for speed, and screen reader users rely on keyboard navigation entirely.

### The Tab Order

Interactive elements are focusable and reachable via the Tab key in the order they appear in the DOM. This is the **tab order**. Non-interactive elements (`<div>`, `<span>`, `<p>`) are not in the tab order.

```jsx
// These elements are in the tab order automatically:
<a href="/about">About</a>        {/* tabIndex: 0 by default */}
<button>Click me</button>         {/* tabIndex: 0 by default */}
<input type="text" />             {/* tabIndex: 0 by default */}
<select>...</select>              {/* tabIndex: 0 by default */}
<textarea />                      {/* tabIndex: 0 by default */}
```

### tabIndex Values

| Value | Behavior |
|-------|----------|
| `tabIndex={0}` | Element is focusable and in the normal tab order |
| `tabIndex={-1}` | Element is focusable programmatically (`element.focus()`) but not via Tab |
| `tabIndex={1+}` | Element gets priority focus order — **avoid this**, it creates confusing navigation |

```jsx
// Make a non-interactive element focusable (for programmatic focus)
<div tabIndex={-1} ref={sectionRef}>
  <h2>Search Results</h2>
  {/* content */}
</div>

// After search, focus the results section
sectionRef.current.focus();
```

### Keyboard Event Handling

Interactive custom components must respond to keyboard events:

```jsx
function CustomButton({ onClick, children }) {
  function handleKeyDown(e) {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      onClick();
    }
  }

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={handleKeyDown}
    >
      {children}
    </div>
  );
}

// But again — just use <button> and get this for free
```

### Focus Trap for Modals

When a modal is open, pressing Tab should cycle through the modal's interactive elements only — not escape to elements behind the modal. This is called a **focus trap**.

```jsx
import { useEffect, useRef } from "react";

function useFocusTrap(isOpen) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!isOpen || !containerRef.current) return;

    const container = containerRef.current;
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    // Focus the first element when the modal opens
    firstElement?.focus();

    function handleKeyDown(e) {
      if (e.key !== "Tab") return;

      if (e.shiftKey) {
        // Shift+Tab — if on first element, wrap to last
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement?.focus();
        }
      } else {
        // Tab — if on last element, wrap to first
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement?.focus();
        }
      }
    }

    container.addEventListener("keydown", handleKeyDown);
    return () => container.removeEventListener("keydown", handleKeyDown);
  }, [isOpen]);

  return containerRef;
}
```

```jsx
function Modal({ open, onClose, title, children }) {
  const trapRef = useFocusTrap(open);
  const previousFocusRef = useRef(null);

  useEffect(() => {
    if (open) {
      // Remember what was focused before the modal opened
      previousFocusRef.current = document.activeElement;
    } else if (previousFocusRef.current) {
      // Restore focus when the modal closes
      previousFocusRef.current.focus();
    }
  }, [open]);

  if (!open) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      ref={trapRef}
      style={{
        position: "fixed",
        inset: 0,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "rgba(0,0,0,0.5)",
        zIndex: 50,
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: "white",
          borderRadius: 8,
          padding: "1.5rem",
          maxWidth: 500,
          width: "90%",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 id="modal-title">{title}</h2>
        {children}
        <button onClick={onClose}>Close</button>
      </div>
    </div>
  );
}
```

Key accessibility features of this modal:

- `role="dialog"` tells screen readers this is a dialog
- `aria-modal="true"` indicates the background is inert
- `aria-labelledby` connects the dialog to its title
- Focus traps inside the modal — Tab cannot escape
- Focus restores to the previously focused element when the modal closes
- Escape key closes the modal (add an `onKeyDown` handler for this)

---

## Accessible Forms

Forms are one of the most critical areas for accessibility. Poorly built forms are the biggest barrier for screen reader users.

### Labels

Every form input must have a label. There are several ways to associate a label with an input:

```jsx
// Method 1: Wrapping (implicit association)
<label>
  Email
  <input type="email" name="email" />
</label>

// Method 2: htmlFor (explicit association) — preferred in React
<label htmlFor="email">Email</label>
<input type="email" id="email" name="email" />

// Method 3: aria-label (when there is no visible label)
<input type="search" aria-label="Search products" placeholder="Search..." />

// Method 4: aria-labelledby (when the label is another element)
<h3 id="billing-section">Billing Address</h3>
<input aria-labelledby="billing-section" />
```

Note: In React, the `for` attribute is written as `htmlFor` because `for` is a reserved word in JavaScript.

**Never use placeholder as the only label:**

```jsx
// WRONG — placeholder disappears when the user starts typing
<input type="email" placeholder="Email" />

// CORRECT — visible label persists
<label htmlFor="email">Email</label>
<input type="email" id="email" placeholder="you@example.com" />
```

### Error Messages

Error messages must be associated with their input so screen readers announce them:

```jsx
function EmailField() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState(null);

  function validate() {
    if (!email.includes("@")) {
      setError("Please enter a valid email address");
    } else {
      setError(null);
    }
  }

  return (
    <div>
      <label htmlFor="email">Email</label>
      <input
        type="email"
        id="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        onBlur={validate}
        aria-invalid={error ? "true" : undefined}
        aria-describedby={error ? "email-error" : undefined}
      />
      {error && (
        <p id="email-error" role="alert" style={{ color: "red", fontSize: "0.85rem" }}>
          {error}
        </p>
      )}
    </div>
  );
}
```

- `aria-invalid="true"` tells screen readers the field has an error
- `aria-describedby="email-error"` associates the error message with the input
- `role="alert"` causes the error to be announced immediately when it appears

### Required Fields

```jsx
<label htmlFor="name">
  Name <span aria-hidden="true" style={{ color: "red" }}>*</span>
</label>
<input
  type="text"
  id="name"
  required
  aria-required="true"
/>
```

The `required` attribute and `aria-required` tell assistive technologies this field is mandatory. The visual asterisk `*` is hidden from screen readers with `aria-hidden` because the screen reader already announces "required" from the attribute.

### Accessible Form Example

```jsx
function RegistrationForm() {
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [errors, setErrors] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const errorSummaryRef = useRef(null);

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    // Clear error when user starts fixing it
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: null }));
    }
  }

  function validate() {
    const newErrors = {};
    if (!form.name.trim()) newErrors.name = "Name is required";
    if (!form.email.includes("@")) newErrors.email = "Enter a valid email";
    if (form.password.length < 8) newErrors.password = "Password must be at least 8 characters";
    return newErrors;
  }

  function handleSubmit(e) {
    e.preventDefault();
    const newErrors = validate();

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      // Focus the error summary so screen readers announce it
      setTimeout(() => errorSummaryRef.current?.focus(), 0);
      return;
    }

    setSubmitted(true);
  }

  if (submitted) {
    return (
      <div role="status">
        <h2>Registration Successful</h2>
        <p>Welcome, {form.name}!</p>
      </div>
    );
  }

  const errorList = Object.entries(errors).filter(([, msg]) => msg);

  return (
    <form onSubmit={handleSubmit} noValidate>
      <h2>Create Account</h2>

      {/* Error summary — announced by screen readers */}
      {errorList.length > 0 && (
        <div
          ref={errorSummaryRef}
          tabIndex={-1}
          role="alert"
          style={{
            padding: "1rem",
            backgroundColor: "#fef2f2",
            border: "1px solid #fca5a5",
            borderRadius: 4,
            marginBottom: "1rem",
          }}
        >
          <h3 style={{ margin: "0 0 0.5rem" }}>
            Please fix {errorList.length} error{errorList.length > 1 ? "s" : ""}:
          </h3>
          <ul>
            {errorList.map(([field, message]) => (
              <li key={field}>
                <a href={`#${field}`} style={{ color: "#dc2626" }}>
                  {message}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="name">
          Name <span aria-hidden="true" style={{ color: "red" }}>*</span>
        </label>
        <input
          type="text"
          id="name"
          name="name"
          value={form.name}
          onChange={handleChange}
          aria-required="true"
          aria-invalid={errors.name ? "true" : undefined}
          aria-describedby={errors.name ? "name-error" : undefined}
          style={{ display: "block", width: "100%", padding: "0.5rem" }}
        />
        {errors.name && (
          <p id="name-error" style={{ color: "red", fontSize: "0.85rem" }}>
            {errors.name}
          </p>
        )}
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="email">
          Email <span aria-hidden="true" style={{ color: "red" }}>*</span>
        </label>
        <input
          type="email"
          id="email"
          name="email"
          value={form.email}
          onChange={handleChange}
          aria-required="true"
          aria-invalid={errors.email ? "true" : undefined}
          aria-describedby={errors.email ? "email-error" : undefined}
          style={{ display: "block", width: "100%", padding: "0.5rem" }}
        />
        {errors.email && (
          <p id="email-error" style={{ color: "red", fontSize: "0.85rem" }}>
            {errors.email}
          </p>
        )}
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="password">
          Password <span aria-hidden="true" style={{ color: "red" }}>*</span>
        </label>
        <input
          type="password"
          id="password"
          name="password"
          value={form.password}
          onChange={handleChange}
          aria-required="true"
          aria-invalid={errors.password ? "true" : undefined}
          aria-describedby="password-hint password-error"
          style={{ display: "block", width: "100%", padding: "0.5rem" }}
        />
        <p id="password-hint" style={{ fontSize: "0.8rem", color: "#666" }}>
          Must be at least 8 characters
        </p>
        {errors.password && (
          <p id="password-error" style={{ color: "red", fontSize: "0.85rem" }}>
            {errors.password}
          </p>
        )}
      </div>

      <button type="submit">Create Account</button>
    </form>
  );
}
```

Accessibility features of this form:

- Every input has a visible `<label>` with `htmlFor`
- `aria-required` marks required fields
- `aria-invalid` marks fields with errors
- `aria-describedby` connects inputs to their error messages and hints
- Error summary at the top is focused on validation failure, so screen readers read it
- Error summary links jump to the specific field
- `role="status"` on the success message announces it to screen readers

---

## Announcing Dynamic Content

Single-page applications change content without page loads. Screen readers do not automatically notice these changes. You need to explicitly announce dynamic content.

### Live Regions

```jsx
function SearchResults({ query }) {
  const [results, setResults] = useState([]);
  const [status, setStatus] = useState("");

  useEffect(() => {
    if (!query) return;

    setStatus("Searching...");

    fetch(`/api/search?q=${query}`)
      .then((r) => r.json())
      .then((data) => {
        setResults(data);
        setStatus(`${data.length} result${data.length !== 1 ? "s" : ""} found for "${query}"`);
      })
      .catch(() => {
        setStatus("Search failed. Please try again.");
      });
  }, [query]);

  return (
    <div>
      {/* This live region announces status changes */}
      <div aria-live="polite" className="sr-only">
        {status}
      </div>

      <h2>Search Results</h2>
      <ul>
        {results.map((result) => (
          <li key={result.id}>{result.title}</li>
        ))}
      </ul>
    </div>
  );
}
```

The `aria-live="polite"` region announces its content changes after the screen reader finishes its current announcement. Use `aria-live="assertive"` for urgent messages that should interrupt (errors, timeouts).

### The Visually Hidden Utility

Sometimes you need text for screen readers that should not be visible. The `.sr-only` class makes content accessible but invisible:

```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

```jsx
// Visually hidden text for context
<button>
  <span aria-hidden="true">×</span>
  <span className="sr-only">Close dialog</span>
</button>

// Or more simply
<button aria-label="Close dialog">×</button>
```

### Notification Announcements

```jsx
function useAnnounce() {
  const [message, setMessage] = useState("");

  function announce(text) {
    // Clear first to ensure re-announcement of the same text
    setMessage("");
    setTimeout(() => setMessage(text), 100);
  }

  const AnnouncerRegion = () => (
    <div
      aria-live="polite"
      aria-atomic="true"
      className="sr-only"
    >
      {message}
    </div>
  );

  return { announce, AnnouncerRegion };
}

// Usage
function App() {
  const { announce, AnnouncerRegion } = useAnnounce();

  async function handleSave() {
    await saveData();
    announce("Changes saved successfully");
  }

  return (
    <div>
      <AnnouncerRegion />
      <button onClick={handleSave}>Save</button>
    </div>
  );
}
```

---

## Accessible Interactive Components

### Accessible Dropdown Menu

```jsx
import { useState, useRef, useEffect } from "react";

function Dropdown({ label, items, onSelect }) {
  const [isOpen, setIsOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const menuRef = useRef(null);
  const buttonRef = useRef(null);
  const menuId = "dropdown-menu";

  // Close on Escape
  useEffect(() => {
    if (!isOpen) return;

    function handleKeyDown(e) {
      if (e.key === "Escape") {
        setIsOpen(false);
        buttonRef.current?.focus();
      }
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isOpen]);

  // Close when clicking outside
  useEffect(() => {
    if (!isOpen) return;

    function handleClickOutside(e) {
      if (menuRef.current && !menuRef.current.contains(e.target) &&
          buttonRef.current && !buttonRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isOpen]);

  function handleButtonKeyDown(e) {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setIsOpen(true);
      setActiveIndex(0);
    }
    if (e.key === "ArrowUp") {
      e.preventDefault();
      setIsOpen(true);
      setActiveIndex(items.length - 1);
    }
  }

  function handleMenuKeyDown(e) {
    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        setActiveIndex((prev) => (prev + 1) % items.length);
        break;
      case "ArrowUp":
        e.preventDefault();
        setActiveIndex((prev) => (prev - 1 + items.length) % items.length);
        break;
      case "Enter":
      case " ":
        e.preventDefault();
        if (activeIndex >= 0) {
          onSelect(items[activeIndex]);
          setIsOpen(false);
          buttonRef.current?.focus();
        }
        break;
      case "Home":
        e.preventDefault();
        setActiveIndex(0);
        break;
      case "End":
        e.preventDefault();
        setActiveIndex(items.length - 1);
        break;
    }
  }

  // Focus the active item when it changes
  useEffect(() => {
    if (isOpen && activeIndex >= 0) {
      const items = menuRef.current?.querySelectorAll('[role="menuitem"]');
      items?.[activeIndex]?.focus();
    }
  }, [activeIndex, isOpen]);

  return (
    <div style={{ position: "relative", display: "inline-block" }}>
      <button
        ref={buttonRef}
        aria-haspopup="true"
        aria-expanded={isOpen}
        aria-controls={menuId}
        onClick={() => setIsOpen(!isOpen)}
        onKeyDown={handleButtonKeyDown}
      >
        {label} ▾
      </button>

      {isOpen && (
        <ul
          ref={menuRef}
          id={menuId}
          role="menu"
          aria-label={label}
          onKeyDown={handleMenuKeyDown}
          style={{
            position: "absolute",
            top: "100%",
            left: 0,
            listStyle: "none",
            padding: "0.25rem 0",
            margin: 0,
            backgroundColor: "white",
            border: "1px solid #ddd",
            borderRadius: 4,
            boxShadow: "0 4px 6px rgba(0,0,0,0.1)",
            minWidth: 160,
            zIndex: 10,
          }}
        >
          {items.map((item, index) => (
            <li
              key={item.id || index}
              role="menuitem"
              tabIndex={-1}
              onClick={() => {
                onSelect(item);
                setIsOpen(false);
                buttonRef.current?.focus();
              }}
              style={{
                padding: "0.5rem 1rem",
                cursor: "pointer",
                backgroundColor: index === activeIndex ? "#f3f4f6" : "transparent",
              }}
            >
              {item.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

Accessibility features:
- `aria-haspopup` and `aria-expanded` describe the button's state
- `role="menu"` and `role="menuitem"` define the dropdown structure
- Arrow keys navigate between items
- Enter/Space selects an item
- Escape closes the menu and returns focus to the button
- Home/End jump to the first/last item
- Focus returns to the trigger when the menu closes

### Accessible Tabs

```jsx
import { useState, useRef } from "react";

function Tabs({ tabs }) {
  const [activeTab, setActiveTab] = useState(0);
  const tabRefs = useRef([]);

  function handleKeyDown(e, index) {
    let newIndex;

    switch (e.key) {
      case "ArrowRight":
        e.preventDefault();
        newIndex = (index + 1) % tabs.length;
        break;
      case "ArrowLeft":
        e.preventDefault();
        newIndex = (index - 1 + tabs.length) % tabs.length;
        break;
      case "Home":
        e.preventDefault();
        newIndex = 0;
        break;
      case "End":
        e.preventDefault();
        newIndex = tabs.length - 1;
        break;
      default:
        return;
    }

    setActiveTab(newIndex);
    tabRefs.current[newIndex]?.focus();
  }

  return (
    <div>
      {/* Tab list */}
      <div
        role="tablist"
        aria-label="Content sections"
        style={{ display: "flex", borderBottom: "2px solid #e5e7eb" }}
      >
        {tabs.map((tab, index) => (
          <button
            key={tab.id}
            ref={(el) => (tabRefs.current[index] = el)}
            role="tab"
            id={`tab-${tab.id}`}
            aria-selected={activeTab === index}
            aria-controls={`panel-${tab.id}`}
            tabIndex={activeTab === index ? 0 : -1}
            onClick={() => setActiveTab(index)}
            onKeyDown={(e) => handleKeyDown(e, index)}
            style={{
              padding: "0.75rem 1.5rem",
              border: "none",
              backgroundColor: "transparent",
              borderBottom: activeTab === index ? "2px solid #3b82f6" : "2px solid transparent",
              fontWeight: activeTab === index ? 600 : 400,
              color: activeTab === index ? "#3b82f6" : "#666",
              cursor: "pointer",
              marginBottom: "-2px",
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab panels */}
      {tabs.map((tab, index) => (
        <div
          key={tab.id}
          role="tabpanel"
          id={`panel-${tab.id}`}
          aria-labelledby={`tab-${tab.id}`}
          hidden={activeTab !== index}
          tabIndex={0}
          style={{ padding: "1.5rem" }}
        >
          {tab.content}
        </div>
      ))}
    </div>
  );
}

// Usage
<Tabs
  tabs={[
    { id: "overview", label: "Overview", content: <Overview /> },
    { id: "features", label: "Features", content: <Features /> },
    { id: "pricing", label: "Pricing", content: <Pricing /> },
  ]}
/>
```

Accessibility features:
- `role="tablist"`, `role="tab"`, and `role="tabpanel"` define the structure
- `aria-selected` indicates the active tab
- `aria-controls` and `aria-labelledby` connect tabs to their panels
- Arrow keys move between tabs (Left/Right)
- Only the active tab is in the tab order (`tabIndex={0}`), others have `tabIndex={-1}`
- The active panel has `tabIndex={0}` so it is focusable after selecting a tab
- Home/End jump to the first/last tab

---

## Images and Media

### Alternative Text

Every `<img>` must have an `alt` attribute:

```jsx
// Informative image — describe the content
<img src="/chart.png" alt="Sales grew 42% from January to March 2025" />

// Decorative image — empty alt to hide from screen readers
<img src="/decorative-border.png" alt="" />

// Linked image — describe the link destination, not the image
<a href="/profile">
  <img src={user.avatar} alt={`${user.name}'s profile`} />
</a>

// Image with adjacent text — avoid redundancy
<div>
  <img src={product.image} alt="" /> {/* Empty alt — the heading provides context */}
  <h3>{product.name}</h3>
</div>

// Complex image — provide detailed description
<figure>
  <img
    src="/architecture-diagram.png"
    alt="System architecture showing three layers: frontend React app, Node.js API server, and PostgreSQL database"
  />
  <figcaption>Figure 3: Application architecture overview</figcaption>
</figure>
```

### Icons

Icons often lack text alternatives:

```jsx
// WRONG — no context for screen readers
<button><TrashIcon /></button>

// CORRECT — provide text
<button aria-label="Delete item">
  <TrashIcon aria-hidden="true" />
</button>

// ALSO CORRECT — visible text alongside icon
<button>
  <TrashIcon aria-hidden="true" />
  <span>Delete</span>
</button>
```

When an icon is next to descriptive text, mark the icon as `aria-hidden` so screen readers do not try to announce it.

---

## Color and Contrast

### Color Contrast Requirements

The Web Content Accessibility Guidelines (WCAG) specify minimum contrast ratios:

- **Normal text** (under 18px): minimum contrast ratio of 4.5:1
- **Large text** (18px+ bold or 24px+ regular): minimum contrast ratio of 3:1
- **UI components and graphical objects**: minimum contrast ratio of 3:1

```css
/* FAILS — light gray on white = 2.5:1 contrast */
.low-contrast {
  color: #999;
  background-color: #fff;
}

/* PASSES — dark gray on white = 7:1 contrast */
.good-contrast {
  color: #555;
  background-color: #fff;
}
```

### Never Rely on Color Alone

Color should not be the only way to convey information:

```jsx
// WRONG — only color indicates the error
<input style={{ borderColor: hasError ? "red" : "gray" }} />

// CORRECT — color plus text and icon
<div>
  <input
    style={{ borderColor: hasError ? "red" : "gray" }}
    aria-invalid={hasError ? "true" : undefined}
    aria-describedby={hasError ? "error-msg" : undefined}
  />
  {hasError && (
    <p id="error-msg" style={{ color: "red" }}>
      ⚠ This field is required
    </p>
  )}
</div>
```

---

## Focus Management

### Skip Links

Long navigation menus force keyboard users to Tab through many links before reaching the main content. A skip link lets them jump directly:

```jsx
function Layout({ children }) {
  return (
    <>
      <a
        href="#main-content"
        style={{
          position: "absolute",
          left: "-9999px",
          top: "auto",
          width: "1px",
          height: "1px",
          overflow: "hidden",
        }}
        onFocus={(e) => {
          // Show the link when it receives focus
          e.target.style.position = "fixed";
          e.target.style.top = "10px";
          e.target.style.left = "10px";
          e.target.style.width = "auto";
          e.target.style.height = "auto";
          e.target.style.padding = "0.5rem 1rem";
          e.target.style.backgroundColor = "#333";
          e.target.style.color = "white";
          e.target.style.zIndex = "100";
        }}
        onBlur={(e) => {
          e.target.style.position = "absolute";
          e.target.style.left = "-9999px";
        }}
      >
        Skip to main content
      </a>

      <header>
        <nav>{/* many links */}</nav>
      </header>

      <main id="main-content" tabIndex={-1}>
        {children}
      </main>
    </>
  );
}
```

### Managing Focus After Navigation

In single-page applications, page transitions do not trigger the browser's built-in focus management. After navigation, focus should move to the new page's main content or heading:

```jsx
import { useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";

function useFocusOnNavigate() {
  const location = useLocation();
  const headingRef = useRef(null);

  useEffect(() => {
    // Focus the page heading after navigation
    headingRef.current?.focus();
  }, [location.pathname]);

  return headingRef;
}

// Usage in a page component
function AboutPage() {
  const headingRef = useFocusOnNavigate();

  return (
    <div>
      <h1 ref={headingRef} tabIndex={-1}>
        About Us
      </h1>
      <p>Learn more about our company...</p>
    </div>
  );
}
```

### Focus Visible Styles

The `:focus-visible` pseudo-class shows focus outlines only for keyboard navigation, not for mouse clicks:

```css
/* Remove default outline (be careful — always provide an alternative) */
button:focus {
  outline: none;
}

/* Show outline only for keyboard users */
button:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}
```

**Never do `outline: none` without providing `:focus-visible` styles.** Users who navigate with keyboards need to see which element is focused.

---

## Testing for Accessibility

### Automated Testing with eslint-plugin-jsx-a11y

Install the ESLint plugin to catch common accessibility issues during development:

```bash
npm install --save-dev eslint-plugin-jsx-a11y
```

This plugin catches issues like:
- Missing `alt` attributes on images
- Click handlers on non-interactive elements without keyboard support
- Missing `htmlFor` on labels
- Invalid ARIA attributes

### Browser DevTools

- **Chrome DevTools**: Accessibility tab in Elements shows the accessibility tree, ARIA attributes, and computed accessible name
- **Chrome Lighthouse**: Run an accessibility audit from the Lighthouse tab
- **Firefox Accessibility Inspector**: Shows the full accessibility tree

### Screen Reader Testing

Test with a screen reader to experience your app as a screen reader user does:

- **macOS**: VoiceOver (built-in, Cmd + F5 to toggle)
- **Windows**: NVDA (free, open source) or Narrator (built-in)
- **ChromeOS**: ChromeVox (built-in)

### Keyboard Testing Checklist

Test your application using only the keyboard:

1. Can you reach every interactive element with Tab?
2. Can you activate buttons with Enter and Space?
3. Can you navigate dropdowns with Arrow keys?
4. Can you close modals with Escape?
5. Does focus stay inside modals (focus trap)?
6. Does focus return to the trigger when a modal closes?
7. Is there a visible focus indicator on every focused element?
8. Can you skip the navigation and jump to the main content?

---

## Mini Project: Accessible Task Manager

Let us build a task manager that demonstrates all the accessibility patterns covered in this chapter.

```jsx
// AccessibleTaskManager.jsx
import { useState, useRef, useEffect } from "react";

function AccessibleTaskManager() {
  const [tasks, setTasks] = useState([
    { id: 1, text: "Learn React hooks", completed: false },
    { id: 2, text: "Build a portfolio", completed: false },
    { id: 3, text: "Review accessibility", completed: true },
  ]);
  const [newTask, setNewTask] = useState("");
  const [filter, setFilter] = useState("all");
  const [announcement, setAnnouncement] = useState("");
  const [error, setError] = useState(null);
  const inputRef = useRef(null);
  const nextId = useRef(4);

  function announce(message) {
    setAnnouncement("");
    setTimeout(() => setAnnouncement(message), 100);
  }

  function addTask(e) {
    e.preventDefault();

    if (!newTask.trim()) {
      setError("Please enter a task");
      inputRef.current?.focus();
      return;
    }

    const task = {
      id: nextId.current++,
      text: newTask.trim(),
      completed: false,
    };

    setTasks((prev) => [...prev, task]);
    setNewTask("");
    setError(null);
    announce(`Task "${task.text}" added`);
    inputRef.current?.focus();
  }

  function toggleTask(taskId) {
    setTasks((prev) =>
      prev.map((t) => {
        if (t.id === taskId) {
          const updated = { ...t, completed: !t.completed };
          announce(
            `Task "${t.text}" marked as ${updated.completed ? "completed" : "not completed"}`
          );
          return updated;
        }
        return t;
      })
    );
  }

  function deleteTask(taskId) {
    const task = tasks.find((t) => t.id === taskId);
    setTasks((prev) => prev.filter((t) => t.id !== taskId));
    announce(`Task "${task.text}" deleted`);
  }

  const filteredTasks = tasks.filter((task) => {
    if (filter === "active") return !task.completed;
    if (filter === "completed") return task.completed;
    return true;
  });

  const stats = {
    total: tasks.length,
    active: tasks.filter((t) => !t.completed).length,
    completed: tasks.filter((t) => t.completed).length,
  };

  return (
    <div
      style={{
        maxWidth: 600,
        margin: "2rem auto",
        padding: "0 1rem",
      }}
    >
      {/* Screen reader announcements */}
      <div aria-live="polite" aria-atomic="true" className="sr-only">
        {announcement}
      </div>

      <header>
        <h1>Task Manager</h1>
        <p style={{ color: "#666" }}>
          {stats.active} task{stats.active !== 1 ? "s" : ""} remaining
        </p>
      </header>

      {/* Add task form */}
      <form onSubmit={addTask} style={{ marginTop: "1.5rem" }}>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <div style={{ flex: 1 }}>
            <label htmlFor="new-task" className="sr-only">
              New task
            </label>
            <input
              ref={inputRef}
              type="text"
              id="new-task"
              value={newTask}
              onChange={(e) => {
                setNewTask(e.target.value);
                if (error) setError(null);
              }}
              placeholder="Add a new task..."
              aria-invalid={error ? "true" : undefined}
              aria-describedby={error ? "task-error" : undefined}
              style={{
                width: "100%",
                padding: "0.5rem 0.75rem",
                border: `1px solid ${error ? "#ef4444" : "#d1d5db"}`,
                borderRadius: 4,
              }}
            />
          </div>
          <button
            type="submit"
            style={{
              padding: "0.5rem 1rem",
              backgroundColor: "#3b82f6",
              color: "white",
              border: "none",
              borderRadius: 4,
              cursor: "pointer",
            }}
          >
            Add Task
          </button>
        </div>
        {error && (
          <p
            id="task-error"
            role="alert"
            style={{ color: "#ef4444", fontSize: "0.85rem", marginTop: "0.25rem" }}
          >
            {error}
          </p>
        )}
      </form>

      {/* Filter tabs */}
      <nav aria-label="Task filters" style={{ marginTop: "1.5rem" }}>
        <div
          role="tablist"
          aria-label="Filter tasks"
          style={{ display: "flex", gap: "0.5rem" }}
        >
          {[
            { value: "all", label: `All (${stats.total})` },
            { value: "active", label: `Active (${stats.active})` },
            { value: "completed", label: `Completed (${stats.completed})` },
          ].map((f) => (
            <button
              key={f.value}
              role="tab"
              aria-selected={filter === f.value}
              onClick={() => {
                setFilter(f.value);
                announce(`Showing ${f.value} tasks`);
              }}
              style={{
                padding: "0.375rem 0.75rem",
                border: "1px solid #d1d5db",
                borderRadius: 4,
                backgroundColor: filter === f.value ? "#3b82f6" : "white",
                color: filter === f.value ? "white" : "#333",
                cursor: "pointer",
              }}
            >
              {f.label}
            </button>
          ))}
        </div>
      </nav>

      {/* Task list */}
      <div role="tabpanel" aria-label={`${filter} tasks`}>
        {filteredTasks.length === 0 ? (
          <p style={{ textAlign: "center", color: "#999", padding: "2rem 0" }}>
            {filter === "all"
              ? "No tasks yet. Add one above!"
              : `No ${filter} tasks.`}
          </p>
        ) : (
          <ul
            aria-label={`${filter} task list`}
            style={{ listStyle: "none", padding: 0, marginTop: "1rem" }}
          >
            {filteredTasks.map((task) => (
              <li
                key={task.id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "0.75rem",
                  padding: "0.75rem",
                  borderBottom: "1px solid #f3f4f6",
                }}
              >
                <input
                  type="checkbox"
                  checked={task.completed}
                  onChange={() => toggleTask(task.id)}
                  aria-label={`Mark "${task.text}" as ${
                    task.completed ? "not completed" : "completed"
                  }`}
                  style={{ width: 18, height: 18 }}
                />
                <span
                  style={{
                    flex: 1,
                    textDecoration: task.completed ? "line-through" : "none",
                    color: task.completed ? "#999" : "inherit",
                  }}
                >
                  {task.text}
                </span>
                <button
                  onClick={() => deleteTask(task.id)}
                  aria-label={`Delete task "${task.text}"`}
                  style={{
                    background: "none",
                    border: "none",
                    color: "#999",
                    cursor: "pointer",
                    fontSize: "1.25rem",
                  }}
                >
                  <span aria-hidden="true">×</span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Keyboard shortcut hint */}
      <footer style={{ marginTop: "2rem", fontSize: "0.8rem", color: "#999" }}>
        <p>
          <kbd>Tab</kbd> to navigate • <kbd>Space</kbd> to toggle •{" "}
          <kbd>Enter</kbd> to add
        </p>
      </footer>
    </div>
  );
}
```

```css
/* Add to your global CSS */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

kbd {
  padding: 0.125rem 0.375rem;
  background-color: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 3px;
  font-family: monospace;
  font-size: 0.8rem;
}
```

This mini project demonstrates:

- **Semantic HTML** — `<header>`, `<nav>`, `<form>`, `<ul>`, `<li>`, `<footer>`
- **Labels** — visible and visually-hidden labels for every input
- **ARIA attributes** — `aria-label`, `aria-invalid`, `aria-describedby`, `aria-selected`, `aria-live`
- **Live region** — screen reader announcements for add, toggle, delete, and filter actions
- **Error handling** — `aria-invalid` and `role="alert"` for form validation
- **Keyboard navigation** — all interactions work with Tab, Space, and Enter
- **Focus management** — focus returns to the input after adding a task
- **Descriptive labels** — every button has context: "Delete task 'Learn React hooks'" not just "Delete"

---

## Common Mistakes

### Mistake 1: Using Divs for Interactive Elements

```jsx
// WRONG — not keyboard accessible, not announced as interactive
<div onClick={handleClick} className="button">Save</div>

// CORRECT — accessible by default
<button onClick={handleClick}>Save</button>
```

### Mistake 2: Missing Form Labels

```jsx
// WRONG — no label
<input type="email" placeholder="Email" />

// CORRECT — proper label
<label htmlFor="email">Email</label>
<input type="email" id="email" placeholder="you@example.com" />
```

### Mistake 3: Removing Focus Outlines Without Replacement

```css
/* WRONG — keyboard users cannot see which element is focused */
*:focus {
  outline: none;
}

/* CORRECT — custom focus style for keyboard users only */
*:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}
```

### Mistake 4: Images Without Alt Text

```jsx
// WRONG — screen reader announces the filename
<img src="/DSC_0042.jpg" />

// CORRECT — descriptive alternative text
<img src="/DSC_0042.jpg" alt="Team members celebrating the product launch" />

// CORRECT — decorative image hidden from screen readers
<img src="/decorative-dots.svg" alt="" />
```

### Mistake 5: Not Announcing Dynamic Changes

```jsx
// WRONG — screen reader does not know the list changed
function TodoList() {
  // ... adds/removes items silently
}

// CORRECT — announce changes via aria-live region
<div aria-live="polite" className="sr-only">
  {announcement}
</div>
```

---

## Best Practices

1. **Use semantic HTML first** — Before reaching for ARIA, ask if there is an HTML element that already communicates the meaning. `<button>`, `<nav>`, `<main>`, `<label>`, `<input>` are your best tools.

2. **Every interactive element must be keyboard accessible** — If it is clickable, it must be focusable and activatable with Enter or Space. Use native elements or add `tabIndex`, `role`, and keyboard handlers.

3. **Every form input needs a label** — Use `<label htmlFor="...">`, `aria-label`, or `aria-labelledby`. Never rely on placeholder text alone.

4. **Announce dynamic content** — Use `aria-live` regions to notify screen readers about content changes (search results, notifications, form errors, item additions/removals).

5. **Manage focus thoughtfully** — After opening a modal, focus the first element inside it. After closing, return focus to the trigger. After navigation, focus the page heading.

6. **Never rely on color alone** — Use text, icons, or patterns alongside color to convey meaning. Ensure text meets WCAG contrast ratios (4.5:1 for normal text).

7. **Test with keyboard and screen readers** — Automated tools catch about 30% of accessibility issues. Tab through your entire application and test key flows with a screen reader.

8. **Provide skip links** — Let keyboard users skip past navigation to reach the main content quickly.

---

## Summary

In this chapter, you learned:

- **Semantic HTML** is the foundation of accessibility — use `<button>`, `<nav>`, `<main>`, `<label>`, and other meaningful elements instead of generic divs
- **ARIA attributes** (`aria-label`, `aria-describedby`, `aria-expanded`, `aria-live`, `role`) add context when HTML alone is insufficient — but no ARIA is better than bad ARIA
- **Keyboard navigation** requires that every interactive element is focusable, activatable, and has a visible focus indicator
- **Focus traps** keep keyboard focus inside modals; focus should restore to the trigger when modals close
- **Accessible forms** need proper labels, `aria-invalid` for errors, `aria-describedby` to connect error messages, and error summaries for screen readers
- **Live regions** (`aria-live`) announce dynamic content changes (notifications, search results, list updates) to screen readers
- **Images** need descriptive `alt` text (informative images) or empty `alt=""` (decorative images)
- **Color contrast** must meet WCAG minimums (4.5:1 for normal text), and color should never be the sole indicator of meaning
- **Testing** combines automated tools (eslint-plugin-jsx-a11y, Lighthouse), keyboard testing, and screen reader testing

---

## Interview Questions

1. **What is accessibility in web development and why does it matter?**

   Web accessibility means building applications that everyone can use, including people with visual, motor, hearing, or cognitive impairments. It matters because over 1 billion people worldwide have disabilities, it is a legal requirement in many jurisdictions (ADA, Section 508, European Accessibility Act), and good accessibility benefits all users — keyboard shortcuts help power users, captions help in noisy environments, and clear structure helps everyone navigate faster.

2. **What is the difference between aria-label, aria-labelledby, and aria-describedby?**

   `aria-label` provides a text label directly on an element (used when there is no visible label text). `aria-labelledby` points to another element's `id` that serves as the label — useful when the label already exists visually. `aria-describedby` points to an element that provides supplementary description, like a hint or error message — it does not replace the label but adds to it. Screen readers announce the label first, then the description.

3. **Why should you prefer semantic HTML elements over ARIA roles?**

   Semantic HTML elements like `<button>`, `<nav>`, `<main>`, and `<label>` come with built-in accessibility: keyboard focus, interaction behavior, screen reader announcements, and correct roles. ARIA only adds metadata — it does not add behavior. A `<div role="button">` still needs manual `tabIndex`, keyboard handlers, and focus styles. Using the native element is more reliable, requires less code, and avoids the risk of incorrect ARIA usage, which can make accessibility worse.

4. **How do you make dynamic content accessible to screen reader users?**

   Use `aria-live` regions. Create an element with `aria-live="polite"` (waits for screen reader to finish) or `aria-live="assertive"` (interrupts immediately). When the content inside this region changes, screen readers automatically announce the new content. This is essential for search results, notifications, form validation messages, and any content that updates without a page load. Additionally, use `role="alert"` for error messages and `role="status"` for informational updates.

5. **What is a focus trap and when would you use one?**

   A focus trap restricts keyboard focus to a specific container — pressing Tab cycles through the container's focusable elements without escaping to the rest of the page. Use it for modals, dialog boxes, and any overlay that takes over the screen. Without a focus trap, keyboard users can Tab to elements behind the modal that they cannot see or interact with. Implement by listening for Tab and Shift+Tab on the container, and wrapping focus from the last element to the first (and vice versa). Always provide an escape mechanism (Escape key to close).

---

## Practice Exercises

### Exercise 1: Accessible Navigation

Build a responsive navigation bar with a logo, navigation links, and a mobile hamburger menu. Ensure the mobile menu is keyboard accessible (opens/closes with Enter, traps focus when open, closes with Escape). Add skip links. Use semantic `<nav>`, `<ul>`, and `<a>` elements. Test with keyboard navigation.

### Exercise 2: Accessible Autocomplete

Build a search input with autocomplete suggestions. The suggestion list should be navigable with Arrow Up/Down. Enter selects the highlighted suggestion. Escape closes the list. Use `role="combobox"`, `role="listbox"`, `role="option"`, and `aria-activedescendant`. Announce the number of suggestions to screen readers.

### Exercise 3: Accessible Data Table

Create a data table with sortable columns. Clicking a column header sorts the table. Use `<table>`, `<thead>`, `<th>`, `<tbody>`, `<td>` with proper `scope` attributes. Add `aria-sort` to indicate the current sort direction. Announce sort changes via a live region. Ensure column headers are keyboard-accessible buttons.

### Exercise 4: Full Accessibility Audit

Take the blog application from Chapter 15 and perform a full accessibility audit. Run Lighthouse, test with keyboard only, and test with a screen reader. Document every issue found and fix them. Common issues to look for: missing labels, inaccessible navigation, missing alt text, insufficient color contrast, and missing live region announcements.

---

## What Is Next?

In Chapter 21, we will explore **Testing React Applications** — how to write unit tests, integration tests, and component tests using React Testing Library and Vitest. You will learn to test components, hooks, user interactions, and async behavior with confidence.
