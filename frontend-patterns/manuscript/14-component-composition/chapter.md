# Chapter 14: Component Composition

## What You Will Learn

- What component composition is and why React favors it over inheritance
- How the `children` prop enables flexible, reusable components
- How the slot pattern gives you named insertion points
- Why composition beats inheritance for building UIs
- How specialization and containment patterns work
- How to build layout components that compose cleanly
- When composition is the right choice and when it is not

## Why This Chapter Matters

Think about building a house. You do not forge a single giant piece of metal in the shape of a house. Instead, you compose the house from smaller pieces: bricks, beams, windows, doors, pipes. Each piece does one thing well. The combination creates something complex.

React components work the same way. The React team explicitly recommends composition over inheritance. In fact, the React documentation states that they have not found any use cases where they would recommend creating component inheritance hierarchies.

Yet many developers coming from object-oriented backgrounds instinctively reach for inheritance. They create `BaseButton` and then extend it to make `PrimaryButton`, `DangerButton`, and `IconButton`. This leads to rigid, fragile hierarchies.

Composition is the alternative. Instead of extending components, you combine them. A button contains an icon. A card contains a header, body, and footer. A page contains a sidebar and a main area. Each piece is independent. The combination is flexible.

This chapter teaches you the composition patterns that make React powerful.

---

## The Problem

You need to build a variety of related components. They share some behavior or structure but differ in specific ways.

```javascript
// The inheritance temptation:
class BaseDialog extends React.Component {
  render() {
    return (
      <div className="dialog-overlay">
        <div className="dialog">
          <div className="dialog-header">{this.renderHeader()}</div>
          <div className="dialog-body">{this.renderBody()}</div>
          <div className="dialog-footer">{this.renderFooter()}</div>
        </div>
      </div>
    );
  }
}

class ConfirmDialog extends BaseDialog {
  renderHeader() { return <h2>Are you sure?</h2>; }
  renderBody() { return <p>{this.props.message}</p>; }
  renderFooter() {
    return (
      <>
        <button onClick={this.props.onCancel}>Cancel</button>
        <button onClick={this.props.onConfirm}>Confirm</button>
      </>
    );
  }
}

class AlertDialog extends BaseDialog {
  renderHeader() { return <h2>Alert</h2>; }
  renderBody() { return <p>{this.props.message}</p>; }
  renderFooter() {
    return <button onClick={this.props.onClose}>OK</button>;
  }
}

// Problems:
// 1. Deep coupling to BaseDialog
// 2. What if you need a dialog without a header?
// 3. What if you need a dialog with two body sections?
// 4. Every variation requires a new subclass
```

---

## The Solution: Composition

Instead of inheriting structure, you compose it from independent pieces:

```javascript
function Dialog({ children }) {
  return (
    <div className="dialog-overlay">
      <div className="dialog">
        {children}
      </div>
    </div>
  );
}

function DialogHeader({ children }) {
  return <div className="dialog-header">{children}</div>;
}

function DialogBody({ children }) {
  return <div className="dialog-body">{children}</div>;
}

function DialogFooter({ children }) {
  return <div className="dialog-footer">{children}</div>;
}
```

Now you compose any dialog you need:

```javascript
// Confirm dialog
function ConfirmDialog({ message, onConfirm, onCancel }) {
  return (
    <Dialog>
      <DialogHeader>
        <h2>Are you sure?</h2>
      </DialogHeader>
      <DialogBody>
        <p>{message}</p>
      </DialogBody>
      <DialogFooter>
        <button onClick={onCancel}>Cancel</button>
        <button onClick={onConfirm}>Confirm</button>
      </DialogFooter>
    </Dialog>
  );
}

// Alert dialog
function AlertDialog({ message, onClose }) {
  return (
    <Dialog>
      <DialogHeader>
        <h2>Alert</h2>
      </DialogHeader>
      <DialogBody>
        <p>{message}</p>
      </DialogBody>
      <DialogFooter>
        <button onClick={onClose}>OK</button>
      </DialogFooter>
    </Dialog>
  );
}

// Dialog without a header -- no problem!
function SimpleDialog({ children, onClose }) {
  return (
    <Dialog>
      <DialogBody>{children}</DialogBody>
      <DialogFooter>
        <button onClick={onClose}>Close</button>
      </DialogFooter>
    </Dialog>
  );
}
```

```
Inheritance:                    Composition:

     BaseDialog                 Dialog
     /    |    \                  +-- DialogHeader (optional)
  Confirm Alert Form             +-- DialogBody
                                 +-- DialogFooter (optional)

  Fixed structure.              Flexible structure.
  New type = new subclass.      New type = new arrangement.
```

---

## Pattern 1: The `children` Prop

The `children` prop is the foundation of composition in React. Any JSX placed between a component's opening and closing tags becomes `props.children`.

```javascript
// A Card component that accepts any content
function Card({ children }) {
  return <div className="card">{children}</div>;
}

// Use it with anything
<Card>
  <h2>Simple text</h2>
  <p>Just a paragraph inside a card.</p>
</Card>

<Card>
  <img src="photo.jpg" alt="A photo" />
  <p>A card with an image.</p>
</Card>

<Card>
  <UserProfile user={currentUser} />
  <ActivityFeed userId={currentUser.id} />
</Card>
```

The `Card` component does not know or care what its children are. It provides the wrapper. The caller provides the content. This is **containment**.

### Children Can Be Anything

```javascript
// String
<Card>Hello World</Card>

// Elements
<Card><h1>Title</h1></Card>

// Components
<Card><UserAvatar user={user} /></Card>

// Multiple items
<Card>
  <Header />
  <Body />
  <Footer />
</Card>

// Even functions (render props -- covered in a later chapter)
<Card>{(cardState) => <p>Card is {cardState}</p>}</Card>

// Nothing
<Card />
// children is undefined
```

---

## Pattern 2: Named Slots

Sometimes `children` is not enough. You need to pass different content to different parts of a component. This is the **slot pattern**.

### Before: Props for Everything

```javascript
// Messy -- too many content props
function Page({
  headerContent,
  sidebarContent,
  mainContent,
  footerContent
}) {
  return (
    <div className="page">
      <header>{headerContent}</header>
      <aside>{sidebarContent}</aside>
      <main>{mainContent}</main>
      <footer>{footerContent}</footer>
    </div>
  );
}

// Usage is clunky
<Page
  headerContent={<NavBar />}
  sidebarContent={<SideMenu items={menuItems} />}
  mainContent={<ArticleList articles={articles} />}
  footerContent={<Copyright />}
/>
```

### After: Named Slot Props

```javascript
function PageLayout({ header, sidebar, children, footer }) {
  return (
    <div className="page-layout">
      {header && <header className="page-header">{header}</header>}
      <div className="page-content">
        {sidebar && <aside className="page-sidebar">{sidebar}</aside>}
        <main className="page-main">{children}</main>
      </div>
      {footer && <footer className="page-footer">{footer}</footer>}
    </div>
  );
}

// Usage -- clean and readable
<PageLayout
  header={<NavBar />}
  sidebar={<SideMenu items={menuItems} />}
  footer={<Copyright />}
>
  <ArticleList articles={articles} />
</PageLayout>
```

The `children` prop is used for the "main" content. Named props (`header`, `sidebar`, `footer`) serve as named slots for secondary content.

### A More Complete Example: Card with Slots

```javascript
function Card({ header, footer, children, variant = "default" }) {
  return (
    <div className={`card card-${variant}`}>
      {header && (
        <div className="card-header">{header}</div>
      )}
      <div className="card-body">{children}</div>
      {footer && (
        <div className="card-footer">{footer}</div>
      )}
    </div>
  );
}

// Product card
<Card
  variant="product"
  header={<img src={product.image} alt={product.name} />}
  footer={
    <div className="card-actions">
      <span className="price">${product.price}</span>
      <button>Add to Cart</button>
    </div>
  }
>
  <h3>{product.name}</h3>
  <p>{product.description}</p>
  <StarRating rating={product.rating} />
</Card>

// User profile card
<Card
  header={<Avatar user={user} size="large" />}
  footer={<button>Send Message</button>}
>
  <h3>{user.name}</h3>
  <p>{user.bio}</p>
</Card>

// Simple card (no header or footer)
<Card>
  <p>Just some text in a card.</p>
</Card>
```

```
Named slots:

  +------------------------------+
  |  header slot (optional)      |  <-- props.header
  +------------------------------+
  |                              |
  |  children (main content)     |  <-- props.children
  |                              |
  +------------------------------+
  |  footer slot (optional)      |  <-- props.footer
  +------------------------------+

  Each slot is independent.
  You can fill any combination.
```

---

## Pattern 3: Composition vs Inheritance

React explicitly recommends composition over inheritance. Here is why, with concrete examples.

### Inheritance Approach (Avoid This)

```javascript
// Base component
class Button extends React.Component {
  render() {
    return (
      <button
        className={`btn btn-${this.getVariant()}`}
        onClick={this.props.onClick}
      >
        {this.renderIcon()}
        {this.props.label}
      </button>
    );
  }

  getVariant() { return "default"; }
  renderIcon() { return null; }
}

// Subclasses for variations
class PrimaryButton extends Button {
  getVariant() { return "primary"; }
}

class DangerButton extends Button {
  getVariant() { return "danger"; }
}

class IconButton extends Button {
  renderIcon() {
    return <span className="icon">{this.props.icon}</span>;
  }
}

// What about a primary icon button?
// PrimaryIconButton extends... what? PrimaryButton or IconButton?
// JavaScript only allows single inheritance!
```

### Composition Approach (Do This)

```javascript
function Button({ variant = "default", icon, children, onClick }) {
  return (
    <button className={`btn btn-${variant}`} onClick={onClick}>
      {icon && <span className="btn-icon">{icon}</span>}
      {children}
    </button>
  );
}

// Every variation is just a different set of props:
<Button variant="primary">Save</Button>
<Button variant="danger">Delete</Button>
<Button variant="primary" icon={<SaveIcon />}>Save</Button>
<Button variant="danger" icon={<TrashIcon />}>Delete</Button>
```

Need a specialized button? Compose, do not extend:

```javascript
// Specialization through composition
function SubmitButton({ children = "Submit", ...props }) {
  return (
    <Button variant="primary" type="submit" {...props}>
      {children}
    </Button>
  );
}

function DeleteButton({ onDelete, itemName, ...props }) {
  return (
    <Button
      variant="danger"
      icon={<TrashIcon />}
      onClick={() => {
        if (confirm(`Delete ${itemName}?`)) {
          onDelete();
        }
      }}
      {...props}
    >
      Delete {itemName}
    </Button>
  );
}

// Usage
<SubmitButton onClick={handleSubmit} />
<DeleteButton itemName="this post" onDelete={handleDelete} />
```

---

## Pattern 4: Specialization

Specialization is when a "specific" component renders a "general" component with specific props. It is composition for creating variations.

```javascript
// General component
function Alert({ type, title, children, onDismiss }) {
  const icons = {
    success: "✓",
    error: "✗",
    warning: "⚠",
    info: "ℹ"
  };

  return (
    <div className={`alert alert-${type}`} role="alert">
      <span className="alert-icon">{icons[type]}</span>
      <div className="alert-content">
        {title && <strong className="alert-title">{title}</strong>}
        <div className="alert-message">{children}</div>
      </div>
      {onDismiss && (
        <button className="alert-dismiss" onClick={onDismiss}>
          x
        </button>
      )}
    </div>
  );
}

// Specialized versions
function SuccessAlert({ title = "Success", children, ...props }) {
  return (
    <Alert type="success" title={title} {...props}>
      {children}
    </Alert>
  );
}

function ErrorAlert({ title = "Error", children, ...props }) {
  return (
    <Alert type="error" title={title} {...props}>
      {children}
    </Alert>
  );
}

function ValidationError({ errors }) {
  if (errors.length === 0) return null;
  return (
    <ErrorAlert title="Please fix the following errors:">
      <ul>
        {errors.map((error, i) => (
          <li key={i}>{error}</li>
        ))}
      </ul>
    </ErrorAlert>
  );
}

// Usage
<SuccessAlert>Your profile has been updated.</SuccessAlert>

<ValidationError errors={["Name is required", "Email is invalid"]} />
```

```
Specialization:

  Alert (general)
    |
    +-- SuccessAlert (Alert with type="success")
    |
    +-- ErrorAlert (Alert with type="error")
    |     |
    |     +-- ValidationError (ErrorAlert with error list)
    |
    +-- WarningAlert (Alert with type="warning")

  Each specialized version WRAPS the general version.
  No inheritance involved.
```

---

## Pattern 5: Containment

Containment is when a component does not know its children ahead of time. It provides a visual container, and the caller fills it with whatever content they need.

```javascript
// Pure containment: the component is just a box
function Panel({ title, children }) {
  return (
    <section className="panel">
      <div className="panel-header">
        <h3>{title}</h3>
      </div>
      <div className="panel-content">{children}</div>
    </section>
  );
}

// The Panel knows nothing about what goes inside it
<Panel title="User Settings">
  <ToggleSetting label="Dark Mode" value={darkMode} onChange={setDarkMode} />
  <ToggleSetting label="Notifications" value={notifs} onChange={setNotifs} />
  <SelectSetting label="Language" options={languages} value={lang} onChange={setLang} />
</Panel>

<Panel title="Recent Orders">
  <OrderTable orders={recentOrders} />
</Panel>

<Panel title="Quick Stats">
  <StatGrid stats={dashboardStats} />
</Panel>
```

### Containment with Multiple Slots

```javascript
function SplitPane({ left, right, ratio = "1:1" }) {
  const [leftFlex, rightFlex] = ratio.split(":").map(Number);

  return (
    <div className="split-pane">
      <div className="split-pane-left" style={{ flex: leftFlex }}>
        {left}
      </div>
      <div className="split-pane-right" style={{ flex: rightFlex }}>
        {right}
      </div>
    </div>
  );
}

// Usage
<SplitPane
  ratio="1:3"
  left={<Navigation items={navItems} />}
  right={<MainContent />}
/>
```

---

## Pattern 6: Layout Components

Layout components are a specific application of containment. They handle positioning and spacing, while content components handle what is displayed.

```javascript
// Stack: vertical layout with consistent spacing
function Stack({ gap = 16, children }) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: `${gap}px`
      }}
    >
      {children}
    </div>
  );
}

// Row: horizontal layout
function Row({ gap = 16, align = "center", justify = "flex-start", children }) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "row",
        gap: `${gap}px`,
        alignItems: align,
        justifyContent: justify
      }}
    >
      {children}
    </div>
  );
}

// Center: center content both ways
function Center({ children }) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        height: "100%"
      }}
    >
      {children}
    </div>
  );
}

// Container: constrain width and center horizontally
function Container({ maxWidth = 1200, children }) {
  return (
    <div
      style={{
        maxWidth: `${maxWidth}px`,
        margin: "0 auto",
        padding: "0 16px"
      }}
    >
      {children}
    </div>
  );
}
```

Composing layout components:

```javascript
function SettingsPage() {
  return (
    <Container maxWidth={800}>
      <Stack gap={32}>
        <h1>Settings</h1>

        <Stack gap={16}>
          <h2>Profile</h2>
          <Row gap={16} align="center">
            <Avatar user={currentUser} size={64} />
            <Stack gap={4}>
              <span className="name">{currentUser.name}</span>
              <span className="email">{currentUser.email}</span>
            </Stack>
            <button style={{ marginLeft: "auto" }}>Edit</button>
          </Row>
        </Stack>

        <Stack gap={16}>
          <h2>Preferences</h2>
          <Row justify="space-between">
            <span>Dark Mode</span>
            <Toggle value={darkMode} onChange={setDarkMode} />
          </Row>
          <Row justify="space-between">
            <span>Notifications</span>
            <Toggle value={notifications} onChange={setNotifications} />
          </Row>
        </Stack>
      </Stack>
    </Container>
  );
}
```

```
Layout composition:

  Container (max-width: 800px, centered)
    Stack (gap: 32px, vertical)
      h1
      Stack (gap: 16px)
        h2
        Row (gap: 16px, aligned center)
          Avatar
          Stack (gap: 4px)
            Name
            Email
          Button
      Stack (gap: 16px)
        h2
        Row (space-between)
          Label | Toggle
        Row (space-between)
          Label | Toggle

  Layout = composition of layout primitives.
  Content fills the layout slots.
```

---

## Composing Components with React.Children

Sometimes you need to modify or inspect children. React provides utilities for this:

```javascript
import React from "react";

function Toolbar({ children }) {
  // Add spacing between all children
  return (
    <div className="toolbar">
      {React.Children.map(children, (child, index) => (
        <div
          className="toolbar-item"
          style={{ marginLeft: index > 0 ? "8px" : "0" }}
        >
          {child}
        </div>
      ))}
    </div>
  );
}

// Usage
<Toolbar>
  <Button>Save</Button>
  <Button>Edit</Button>
  <Button variant="danger">Delete</Button>
</Toolbar>
```

**Note**: Manipulating children directly is an advanced technique. Prefer explicit props (like the slot pattern) when possible. `React.Children` is useful for truly generic components like toolbars, lists, and grids.

---

## When to Use Component Composition

```
+-----------------------------------------------+
|           USE COMPOSITION WHEN:               |
+-----------------------------------------------+
|                                               |
|  * Building UI components with variable       |
|    content (cards, dialogs, layouts)           |
|  * Creating specialized versions of a         |
|    general component                          |
|  * Building layout primitives (Stack, Row)    |
|  * You need flexibility in what goes inside   |
|    a component                                |
|  * You are tempted to use inheritance to       |
|    create component variations                |
|  * Components need to be independently        |
|    testable and reusable                      |
|                                               |
+-----------------------------------------------+

+-----------------------------------------------+
|    COMPOSITION MIGHT NOT BE ENOUGH WHEN:      |
+-----------------------------------------------+
|                                               |
|  * Child components need to share state with  |
|    the parent (consider Context or Compound   |
|    Components instead)                        |
|  * You need to intercept and modify child     |
|    behavior (consider Render Props)           |
|  * The composition tree gets very deep with   |
|    many levels of nesting                     |
|  * You need to pass the same prop through     |
|    many levels ("prop drilling")              |
|                                               |
+-----------------------------------------------+
```

---

## Common Mistakes

### Mistake 1: Using Inheritance Instead of Composition

```javascript
// WRONG -- inheritance
class PrimaryButton extends Button { /* ... */ }
class LargeButton extends Button { /* ... */ }
class LargePrimaryButton extends ???  // Impossible!

// CORRECT -- composition via props
<Button variant="primary" size="large">Click Me</Button>
```

### Mistake 2: Prop Drilling Through Composition

```javascript
// WRONG -- passing theme through every level
<App theme={theme}>
  <Layout theme={theme}>
    <Sidebar theme={theme}>
      <NavItem theme={theme}>Home</NavItem>
    </Sidebar>
  </Layout>
</App>

// CORRECT -- use Context for cross-cutting concerns
const ThemeContext = React.createContext("light");

function App() {
  return (
    <ThemeContext.Provider value={theme}>
      <Layout>
        <Sidebar>
          <NavItem>Home</NavItem>
        </Sidebar>
      </Layout>
    </ThemeContext.Provider>
  );
}
```

### Mistake 3: Over-Composing Simple Things

```javascript
// OVER-COMPOSED -- too many tiny components
<Card>
  <CardBorder>
    <CardPadding>
      <CardShadow>
        <CardBackground>
          <CardContent>Hello</CardContent>
        </CardBackground>
      </CardShadow>
    </CardPadding>
  </CardBorder>
</Card>

// BETTER -- one component with props
<Card border shadow padding="16px" background="white">
  Hello
</Card>
```

### Mistake 4: Not Using children

```javascript
// WRONG -- passing content as a prop
<Card content={<p>Hello world</p>} />

// CORRECT -- use children for primary content
<Card>
  <p>Hello world</p>
</Card>
```

---

## Best Practices

1. **Use `children` for primary content** -- it is the most natural and readable pattern.

2. **Use named props for secondary slots** -- `header`, `footer`, `sidebar`, `icon` are common slot names.

3. **Prefer composition over inheritance** -- always. The React team recommends this, and years of practice have proven it.

4. **Keep layout and content separate** -- layout components handle positioning; content components handle data.

5. **Make components flexible by default** -- accept `children` and optional slots rather than hardcoding content.

6. **Use specialization for common variants** -- create `SuccessAlert`, `ErrorAlert` wrappers instead of requiring callers to remember `type="error"` every time.

---

## Quick Summary

Component composition is React's primary strategy for building complex UIs from simple pieces. Instead of inheriting behavior, components are combined using `children`, named slots, specialization, and containment. Layout components handle positioning while content components fill the slots. This approach is more flexible, more testable, and more maintainable than class inheritance.

```
Composition recipe:

  1. Build small, focused components
  2. Use children for primary content
  3. Use named props for secondary slots
  4. Specialize general components by wrapping them
  5. Compose layout with Stack, Row, Container
  6. Let callers decide what goes inside
```

---

## Key Points

- Component composition combines simple components to build complex UIs
- The `children` prop is the foundation -- it lets callers put anything inside a component
- Named slot props (`header`, `footer`, `sidebar`) provide multiple insertion points
- Specialization creates specific versions by wrapping general components with preset props
- Containment creates visual containers that accept any content
- Layout components (Stack, Row, Container) handle positioning separately from content
- React explicitly recommends composition over inheritance
- Avoid prop drilling through composition -- use Context for cross-cutting data

---

## Practice Questions

1. What is the difference between containment and specialization? Give an example of each.

2. Why does React recommend composition over inheritance? What problems does inheritance cause?

3. A colleague has built `BaseInput`, `TextInput extends BaseInput`, and `EmailInput extends TextInput`. How would you refactor this to use composition?

4. When would you use named slot props instead of just `children`? Give a specific example.

5. What is the difference between a layout component and a content component? Why is this separation useful?

---

## Exercises

### Exercise 1: Composable Modal System

Build a modal system using composition. Create `Modal`, `ModalHeader`, `ModalBody`, and `ModalFooter` components. Then compose three different modals: a confirmation modal, a form modal, and a success modal.

```javascript
// Build these components:
function Modal({ isOpen, onClose, size, children }) { /* ... */ }
function ModalHeader({ children }) { /* ... */ }
function ModalBody({ children }) { /* ... */ }
function ModalFooter({ children }) { /* ... */ }

// Then compose:
// 1. ConfirmDeleteModal
// 2. EditProfileModal (with a form)
// 3. SuccessModal (just a message and close button)
```

### Exercise 2: Layout System

Build a complete layout system with `PageLayout`, `Stack`, `Row`, `Grid`, `Container`, and `Spacer` components. Then use them to build a dashboard page layout.

```javascript
// Build these layout primitives:
function Stack({ gap, children }) { /* ... */ }
function Row({ gap, align, justify, children }) { /* ... */ }
function Grid({ columns, gap, children }) { /* ... */ }
function Container({ maxWidth, children }) { /* ... */ }
function Spacer({ size }) { /* ... */ }

// Then compose a dashboard layout
function DashboardPage() {
  // Use your layout primitives to create a
  // responsive dashboard with sidebar, header,
  // stat cards, and a data table
}
```

### Exercise 3: Composable Form

Build a form system where `Form`, `FormSection`, `FormField`, and `FormActions` are composable. Different pages can create different forms by composing these pieces differently.

```javascript
function Form({ onSubmit, children }) { /* ... */ }
function FormSection({ title, description, children }) { /* ... */ }
function FormField({ label, error, required, children }) { /* ... */ }
function FormActions({ children }) { /* ... */ }

// Compose a registration form and a settings form
// using the same building blocks
```

---

## What Is Next?

You have learned how to compose components to build flexible UIs. The next chapter introduces the **Container/Presentational pattern**, which takes composition a step further by separating components into two categories: containers (which handle data and logic) and presentational components (which handle rendering). This separation makes components more reusable and easier to test.
