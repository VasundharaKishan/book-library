# Chapter 16: Higher-Order Components

## What You Will Learn

- What a Higher-Order Component (HOC) is and how it works mechanically
- How to build practical HOCs like `withAuth`, `withLoading`, and `withLogger`
- How to forward refs through HOCs correctly
- How to compose multiple HOCs together
- Why React hooks have replaced most HOC use cases
- When HOCs still make sense in modern codebases

## Why This Chapter Matters

Imagine you run a delivery company. Every driver needs a GPS tracker, a fuel card, and a uniform before they can start working. You could equip each driver individually, filling out paperwork from scratch every time. Or you could create an onboarding process -- a function that takes a new driver and returns an equipped, ready-to-go driver.

Higher-Order Components work the same way. They are functions that take a component and return a new, enhanced component -- one that has been "equipped" with extra behavior like authentication checks, loading states, or logging. The original component does not need to know about any of this. It just does its job while the HOC handles the cross-cutting concern.

HOCs were the dominant pattern for code reuse in React before hooks arrived. Understanding them matters for three reasons:

- Many production codebases still use them heavily
- Some problems (like decorating class components) are still best solved with HOCs
- The concept of wrapping and enhancing functions is fundamental to programming beyond React

---

## The Core Concept: Functions That Return Components

A Higher-Order Component is a function that takes a component as an argument and returns a new component.

```
+------------------------------------------------------+
|                  Higher-Order Component               |
|                                                       |
|   Input:              Output:                         |
|   +------------+      +-------------------------+    |
|   | Component  | ---> | Enhanced Component      |    |
|   | (original) |      | (original + new powers) |    |
|   +------------+      +-------------------------+    |
|                                                       |
+------------------------------------------------------+
```

Here is the simplest possible HOC:

```jsx
// A HOC is just a function
function withGreeting(WrappedComponent) {
  // It returns a new component
  return function EnhancedComponent(props) {
    return (
      <div>
        <p>Hello! Here is the wrapped component:</p>
        <WrappedComponent {...props} />
      </div>
    );
  };
}

// Original component
function UserProfile({ name }) {
  return <h2>{name}</h2>;
}

// Enhanced component
const UserProfileWithGreeting = withGreeting(UserProfile);

// Usage
function App() {
  return <UserProfileWithGreeting name="Alice" />;
}

// Output:
// Hello! Here is the wrapped component:
// Alice
```

The key insight: `withGreeting` does not modify `UserProfile`. It creates a brand new component that renders `UserProfile` inside it and passes all props through.

---

## Pattern 1: withAuth -- Protecting Routes

### The Problem

Multiple pages need authentication checks. Without a HOC, every component repeats the same logic:

```jsx
// Dashboard.jsx
function Dashboard({ user }) {
  if (!user) {
    return <Navigate to="/login" />;
  }
  return <h1>Welcome to Dashboard</h1>;
}

// Settings.jsx
function Settings({ user }) {
  if (!user) {
    return <Navigate to="/login" />;
  }
  return <h1>Settings Page</h1>;
}

// Profile.jsx
function Profile({ user }) {
  if (!user) {
    return <Navigate to="/login" />;
  }
  return <h1>Profile Page</h1>;
}
```

Three components, three identical auth checks. If you change the redirect path, you need to update all three.

### The Solution

```jsx
function withAuth(WrappedComponent) {
  return function AuthenticatedComponent(props) {
    const { user } = useContext(AuthContext);

    if (!user) {
      return <Navigate to="/login" />;
    }

    return <WrappedComponent {...props} user={user} />;
  };
}
```

Now the original components are clean:

```jsx
// Dashboard.jsx -- no auth logic here
function Dashboard({ user }) {
  return <h1>Welcome, {user.name}!</h1>;
}

export default withAuth(Dashboard);

// Settings.jsx -- no auth logic here
function Settings({ user }) {
  return <h1>Settings for {user.email}</h1>;
}

export default withAuth(Settings);
```

```
+------------------------------------------+
|  withAuth(Dashboard)                     |
|                                          |
|  Is user logged in?                      |
|    NO  --> <Navigate to="/login" />      |
|    YES --> +------------------------+    |
|            |  Dashboard             |    |
|            |  (receives user prop)  |    |
|            +------------------------+    |
+------------------------------------------+
```

### Before vs After

**Before:** Every protected page has its own auth check. Bug fixes require updating N files.

**After:** Auth logic lives in one place. Adding protection to a new page is a single line: `export default withAuth(NewPage)`.

### Real-World Use Case

In a SaaS application with 40+ routes, 30 of them need authentication. Without `withAuth`, that is 30 files with identical if-not-authenticated-redirect logic. With the HOC, each file just wraps its export.

---

## Pattern 2: withLoading -- Handling Async States

### The Problem

Components that fetch data all need loading and error states:

```jsx
function UserList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/api/users')
      .then(res => res.json())
      .then(data => { setUsers(data); setLoading(false); })
      .catch(err => { setError(err); setLoading(false); });
  }, []);

  if (loading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <ul>
      {users.map(u => <li key={u.id}>{u.name}</li>)}
    </ul>
  );
}
```

### The Solution

```jsx
function withLoading(WrappedComponent, fetchFn) {
  return function LoadingComponent(props) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
      setLoading(true);
      fetchFn(props)
        .then(result => {
          setData(result);
          setLoading(false);
        })
        .catch(err => {
          setError(err);
          setLoading(false);
        });
    }, []);  // eslint-disable-line react-hooks/exhaustive-deps

    if (loading) return <Spinner />;
    if (error) return <ErrorMessage error={error} />;

    return <WrappedComponent {...props} data={data} />;
  };
}

// Usage
function UserList({ data }) {
  return (
    <ul>
      {data.map(u => <li key={u.id}>{u.name}</li>)}
    </ul>
  );
}

const UserListWithLoading = withLoading(
  UserList,
  () => fetch('/api/users').then(r => r.json())
);
```

Now `UserList` only cares about rendering users. It receives `data` and renders it. Loading, error handling, and fetching are all handled by the HOC.

---

## Pattern 3: withLogger -- Cross-Cutting Concerns

This HOC logs when a component mounts, updates, or unmounts:

```jsx
function withLogger(WrappedComponent) {
  const componentName =
    WrappedComponent.displayName ||
    WrappedComponent.name ||
    'Component';

  return function LoggedComponent(props) {
    useEffect(() => {
      console.log(`[${componentName}] Mounted`);
      return () => console.log(`[${componentName}] Unmounted`);
    }, []);

    useEffect(() => {
      console.log(`[${componentName}] Updated`, props);
    });

    return <WrappedComponent {...props} />;
  };
}

// Usage
const LoggedDashboard = withLogger(Dashboard);

// Console output when LoggedDashboard renders:
// [Dashboard] Mounted
// [Dashboard] Updated { user: { name: "Alice" } }
```

---

## Composing Multiple HOCs

You can stack HOCs to combine behaviors:

```jsx
// Apply auth + logging to Dashboard
const EnhancedDashboard = withLogger(withAuth(Dashboard));
```

This reads inside-out: first wrap with auth, then wrap the result with logging.

```
+------------------------------------------+
|  withLogger                              |
|  +------------------------------------+  |
|  |  withAuth                          |  |
|  |  +------------------------------+ |  |
|  |  |  Dashboard                    | |  |
|  |  |  (the actual component)       | |  |
|  |  +------------------------------+ |  |
|  +------------------------------------+  |
+------------------------------------------+
```

For better readability, you can use a `compose` utility:

```jsx
// Simple compose function
function compose(...fns) {
  return function (component) {
    return fns.reduceRight(
      (wrapped, fn) => fn(wrapped),
      component
    );
  };
}

const enhance = compose(
  withLogger,
  withAuth,
  withTheme
);

const EnhancedDashboard = enhance(Dashboard);
```

This is equivalent to `withLogger(withAuth(withTheme(Dashboard)))` but much easier to read.

---

## Forwarding Refs Through HOCs

One critical problem with HOCs: the `ref` prop does not pass through automatically. React treats `ref` specially -- it is not a regular prop.

### The Problem

```jsx
function withTooltip(WrappedComponent) {
  return function TooltipComponent(props) {
    return (
      <div className="tooltip-wrapper">
        <WrappedComponent {...props} />
      </div>
    );
  };
}

const FancyButton = withTooltip(
  function Button(props) {
    return <button {...props}>Click me</button>;
  }
);

// This ref points to TooltipComponent, NOT the inner button!
const ref = useRef();
<FancyButton ref={ref} />
```

### The Solution: React.forwardRef

```jsx
function withTooltip(WrappedComponent) {
  const WithTooltip = React.forwardRef(function TooltipComponent(props, ref) {
    return (
      <div className="tooltip-wrapper">
        <WrappedComponent {...props} ref={ref} />
      </div>
    );
  });

  // Preserve the display name for DevTools
  const name = WrappedComponent.displayName || WrappedComponent.name;
  WithTooltip.displayName = `withTooltip(${name})`;

  return WithTooltip;
}

// Now the ref correctly points to the inner button
const FancyButton = withTooltip(
  React.forwardRef(function Button(props, ref) {
    return <button ref={ref} {...props}>Click me</button>;
  })
);

const ref = useRef();
<FancyButton ref={ref} />
// ref.current === the <button> DOM node
```

```
Without forwardRef:          With forwardRef:
ref --> TooltipComponent      ref --> <button> DOM node
        |                             ^
        v                             |
        <div>                         forwarded through
          <button> (lost!)            TooltipComponent
```

### Setting displayName

Always set `displayName` on HOC-returned components. Without it, React DevTools shows a tree of anonymous components that is impossible to debug:

```
// Bad DevTools tree:
<Anonymous>
  <Anonymous>
    <Anonymous>

// Good DevTools tree (with displayName):
<withLogger(withAuth(Dashboard))>
  <withAuth(Dashboard)>
    <Dashboard>
```

---

## Why Hooks Replaced Most HOCs

React 16.8 introduced hooks, and most HOC use cases can now be handled more cleanly with custom hooks.

### HOC Approach (Before)

```jsx
function withWindowWidth(WrappedComponent) {
  return function WithWindowWidth(props) {
    const [width, setWidth] = useState(window.innerWidth);

    useEffect(() => {
      const handle = () => setWidth(window.innerWidth);
      window.addEventListener('resize', handle);
      return () => window.removeEventListener('resize', handle);
    }, []);

    return <WrappedComponent {...props} windowWidth={width} />;
  };
}

const ResponsiveNav = withWindowWidth(function Nav({ windowWidth }) {
  return windowWidth > 768 ? <DesktopNav /> : <MobileNav />;
});
```

### Hook Approach (After)

```jsx
function useWindowWidth() {
  const [width, setWidth] = useState(window.innerWidth);

  useEffect(() => {
    const handle = () => setWidth(window.innerWidth);
    window.addEventListener('resize', handle);
    return () => window.removeEventListener('resize', handle);
  }, []);

  return width;
}

function Nav() {
  const windowWidth = useWindowWidth();
  return windowWidth > 768 ? <DesktopNav /> : <MobileNav />;
}
```

### Why Hooks Win

| Problem with HOCs | How Hooks Solve It |
|---|---|
| **Wrapper hell** -- stacking 5 HOCs creates 5 extra layers in the component tree | Hooks add zero extra components |
| **Prop collisions** -- two HOCs might inject a prop with the same name | Hooks return values you name yourself |
| **Indirection** -- hard to trace where a prop comes from | Hooks are called directly in the component |
| **Static composition** -- HOCs are applied at definition time, not render time | Hooks run at render time and can use conditions (via early returns) |

```
HOC wrapper hell:                    Hooks -- flat tree:
<withAuth>                           <Dashboard>
  <withTheme>                          (uses useAuth hook)
    <withLogger>                       (uses useTheme hook)
      <withWindowWidth>                (uses useLogger hook)
        <Dashboard />                  (uses useWindowWidth hook)
      </withWindowWidth>
    </withLogger>
  </withTheme>
</withAuth>
```

### When HOCs Still Make Sense

Hooks solved most problems, but HOCs remain useful in specific situations:

1. **Wrapping class components** -- class components cannot use hooks
2. **Adding wrapper DOM elements** -- a HOC can insert a `<div>` with specific styles around any component
3. **Route-level decorators** -- frameworks like Next.js sometimes use HOC-like patterns for layout wrapping
4. **Third-party library integration** -- some libraries (like Redux's legacy `connect`) are built on HOCs

---

## When to Use / When NOT to Use

### Use HOCs When

- You need to add behavior to class components that cannot use hooks
- You need to wrap a component with additional DOM elements
- You are working in a codebase that already uses HOCs consistently
- You need to enhance components from a third-party library you cannot modify

### Do NOT Use HOCs When

- You can use a custom hook instead (most cases in modern React)
- The logic does not need to wrap the component tree (use hooks)
- You are creating a new project with only function components
- The HOC would only pass down a single prop (a hook returning that value is simpler)

---

## Common Mistakes

### Mistake 1: Creating HOCs Inside render

```jsx
// WRONG -- creates a new component type every render
function App() {
  // This causes the entire subtree to unmount/remount!
  const Enhanced = withAuth(Dashboard);
  return <Enhanced />;
}

// CORRECT -- create HOC outside the component
const EnhancedDashboard = withAuth(Dashboard);

function App() {
  return <EnhancedDashboard />;
}
```

When you create a HOC inside render, React sees a different component type on each render and destroys the entire subtree, losing all state.

### Mistake 2: Not Passing Props Through

```jsx
// WRONG -- swallows all original props
function withAuth(WrappedComponent) {
  return function(props) {
    const user = useAuth();
    // Forgot {...props}!
    return <WrappedComponent user={user} />;
  };
}

// CORRECT -- spread all props
function withAuth(WrappedComponent) {
  return function(props) {
    const user = useAuth();
    return <WrappedComponent {...props} user={user} />;
  };
}
```

### Mistake 3: Not Copying Static Methods

```jsx
// Original component has static methods
Dashboard.navigationOptions = { title: 'Home' };

// HOC loses them!
const Enhanced = withAuth(Dashboard);
console.log(Enhanced.navigationOptions); // undefined

// Fix: copy static methods
function withAuth(WrappedComponent) {
  function Enhanced(props) { /* ... */ }

  // Manually copy statics
  Enhanced.navigationOptions = WrappedComponent.navigationOptions;

  // Or use hoist-non-react-statics library
  // hoistNonReactStatics(Enhanced, WrappedComponent);

  return Enhanced;
}
```

### Mistake 4: Mutating the Original Component

```jsx
// WRONG -- mutates the input
function withAuth(WrappedComponent) {
  WrappedComponent.prototype.checkAuth = function() { /* ... */ };
  return WrappedComponent;
}

// CORRECT -- composition, not mutation
function withAuth(WrappedComponent) {
  return function Enhanced(props) {
    // Add behavior through composition
    return <WrappedComponent {...props} />;
  };
}
```

---

## Best Practices

1. **Name your HOCs with the `with` prefix** -- `withAuth`, `withLoading`, `withTheme`. This convention immediately signals what the function does.

2. **Always set displayName** -- makes debugging in React DevTools possible.

3. **Pass through all unrelated props** -- use `{...props}` to ensure the wrapped component receives everything it expects.

4. **Use forwardRef when the wrapped component needs a ref** -- otherwise consumers cannot get a reference to the inner component.

5. **Create HOCs outside of components** -- never inside render methods or function component bodies.

6. **Prefer hooks for new code** -- only reach for HOCs when hooks cannot solve the problem.

7. **Keep HOCs focused** -- each HOC should do one thing. Compose them for complex behavior rather than building one giant HOC.

---

## Quick Summary

A Higher-Order Component is a function that takes a component and returns a new, enhanced component. HOCs inject props, wrap rendering, and add behavior without modifying the original component. They were the primary code-reuse pattern before hooks and remain relevant for class components, DOM wrapping, and legacy codebases. In modern React, prefer custom hooks for most cross-cutting concerns.

---

## Key Points

- A HOC is a function: `(Component) => EnhancedComponent`
- HOCs do not modify the input component -- they compose it
- Always spread props through: `<WrappedComponent {...props} />`
- Use `React.forwardRef` to pass refs through HOCs
- Set `displayName` for debuggability
- Never create HOCs inside render -- it destroys component state
- Hooks have replaced most HOC use cases since React 16.8
- HOCs still shine for class components, DOM wrappers, and third-party library integration
- Compose multiple HOCs with a `compose` utility for readability

---

## Practice Questions

1. What is the difference between a Higher-Order Component and a Higher-Order Function? How does the concept from functional programming apply to React components?

2. You have a HOC `withTheme` that injects a `theme` prop and a HOC `withUser` that also injects a prop called `theme` (containing user theme preferences). What happens when you compose them? How would you fix it?

3. Explain why creating a HOC inside a component's render method causes all state in the wrapped component tree to be lost on every render.

4. A teammate argues that all HOCs should be rewritten as hooks immediately. Give two concrete examples where a HOC is a better choice than a hook.

5. How does `React.forwardRef` solve the ref-forwarding problem in HOCs? What would happen if you tried to pass `ref` as a regular prop named `innerRef` instead?

---

## Exercises

### Exercise 1: Build withPermission

Create a `withPermission` HOC that checks if the current user has a specific permission before rendering a component. If the user lacks the permission, show an "Access Denied" message.

```jsx
// Your HOC should work like this:
const AdminPanel = withPermission('admin')(AdminPanelBase);
const EditorPanel = withPermission('editor')(EditorPanelBase);
```

Hint: This is a HOC factory -- a function that returns a HOC. The pattern is `withPermission(config)(Component)`.

### Exercise 2: Build withRetry

Create a `withRetry` HOC that wraps a component performing data fetching. If the fetch fails, show a "Retry" button. When clicked, it should attempt the fetch again up to 3 times.

### Exercise 3: Convert a HOC to a Hook

Take the `withWindowWidth` HOC from this chapter and convert it to a `useWindowWidth` hook. Then refactor a component that used the HOC to use the hook instead. Compare the before and after code in terms of readability, component tree depth, and flexibility.

---

## What Is Next?

Higher-Order Components wrap a component from the outside. But what if you want to share behavior by passing a function *into* a component that controls what gets rendered? That is the Render Props pattern -- a technique where a component receives a function as a prop and calls it to determine its output. In Chapter 17, you will learn how render props offer an alternative to HOCs and why hooks ultimately simplified both approaches.
