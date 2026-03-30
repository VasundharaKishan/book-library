# Chapter 17: Render Props

## What You Will Learn

- What the render props pattern is and why it exists
- How to build practical render prop components: mouse tracker, toggle, fetch wrapper
- The "children as a function" variation and when to prefer it
- How render props compare to HOCs and hooks
- Performance considerations and how to avoid unnecessary re-renders
- When render props remain useful in a hooks-first world

## Why This Chapter Matters

Picture a vending machine. You put in your money (input), and the machine gives you a snack (output). Now imagine a more flexible machine: you put in your money, and instead of giving you a fixed snack, it gives you a *token* that you can exchange at any counter for whatever you want -- a sandwich, a drink, a salad. The machine handles the payment logic, but *you* decide what you get.

Render props work the same way. A component handles the logic (tracking the mouse, managing a toggle, fetching data), but instead of deciding what to render, it calls a function you provide and lets *you* decide. The component supplies the data; you supply the UI.

This pattern was the second major approach to code reuse in React (after HOCs) and solved several of the problems that HOCs created. While hooks have since simplified most of these use cases, render props remain the clearest way to understand the principle of *inversion of control* -- letting consumers decide how shared logic manifests visually.

---

## The Core Concept

A render prop is a prop whose value is a function that returns JSX. The component calls this function, passing it some data, and renders whatever the function returns.

```jsx
// The component with shared logic
function MouseTracker({ render }) {
  const [position, setPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (event) => {
      setPosition({ x: event.clientX, y: event.clientY });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Call the render prop with the data
  return render(position);
}

// Consumer decides what to render
function App() {
  return (
    <MouseTracker
      render={(position) => (
        <p>
          Mouse is at ({position.x}, {position.y})
        </p>
      )}
    />
  );
}

// Output (as mouse moves):
// Mouse is at (245, 182)
```

```
+--------------------------------------------------+
|  MouseTracker Component                          |
|                                                  |
|  State: { x: 245, y: 182 }                      |
|                                                  |
|  Logic: addEventListener('mousemove', ...)       |
|                                                  |
|  Rendering:                                      |
|    return render({ x: 245, y: 182 })             |
|            |                                     |
|            v                                     |
|    Consumer's function decides                   |
|    what JSX to produce                           |
+--------------------------------------------------+
```

The same `MouseTracker` can render completely different UIs:

```jsx
// As a tooltip that follows the cursor
<MouseTracker
  render={({ x, y }) => (
    <div style={{ position: 'fixed', left: x + 10, top: y + 10 }}>
      Tooltip content here
    </div>
  )}
/>

// As a coordinate display in a debug panel
<MouseTracker
  render={({ x, y }) => (
    <div className="debug-panel">
      <strong>X:</strong> {x} | <strong>Y:</strong> {y}
    </div>
  )}
/>

// As a heat map dot
<MouseTracker
  render={({ x, y }) => (
    <svg width="100%" height="100%">
      <circle cx={x} cy={y} r={20} fill="rgba(255,0,0,0.3)" />
    </svg>
  )}
/>
```

One component, three completely different visual outputs. The logic is reused; the presentation is flexible.

---

## Children as a Function

Instead of passing the function through a prop called `render`, you can pass it as the component's `children`. This reads more naturally in JSX:

```jsx
// Component accepts children as a function
function MouseTracker({ children }) {
  const [position, setPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (event) => {
      setPosition({ x: event.clientX, y: event.clientY });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return children(position);
}

// Usage -- looks cleaner
function App() {
  return (
    <MouseTracker>
      {(position) => (
        <p>Mouse is at ({position.x}, {position.y})</p>
      )}
    </MouseTracker>
  );
}
```

Both approaches are functionally identical. The community generally prefers `children` as a function because:

- It avoids inventing a prop name (`render`, `renderItem`, `renderHeader`)
- It visually nests content inside the component tags, which feels natural
- It is consistent with how `children` works elsewhere in React

However, if the component needs *multiple* render functions, named props are better:

```jsx
<DataTable
  data={users}
  renderHeader={(columns) => (
    <tr>{columns.map(col => <th key={col}>{col}</th>)}</tr>
  )}
  renderRow={(user) => (
    <tr key={user.id}>
      <td>{user.name}</td>
      <td>{user.email}</td>
    </tr>
  )}
  renderEmpty={() => <p>No users found.</p>}
/>
```

---

## Pattern 1: Toggle with Render Props

### The Problem

You need toggle behavior (show/hide, expand/collapse, on/off) in many places, each with different UI:

```jsx
// A modal toggle
function ModalExample() {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <>
      <button onClick={() => setIsOpen(true)}>Open Modal</button>
      {isOpen && <Modal onClose={() => setIsOpen(false)} />}
    </>
  );
}

// A dropdown toggle -- same logic, different UI
function DropdownExample() {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <>
      <button onClick={() => setIsOpen(!isOpen)}>Menu</button>
      {isOpen && <DropdownMenu />}
    </>
  );
}
```

### The Solution

```jsx
function Toggle({ children, initialOn = false }) {
  const [on, setOn] = useState(initialOn);

  const toggle = () => setOn(prev => !prev);
  const setOff = () => setOn(false);
  const setOnTrue = () => setOn(true);

  return children({ on, toggle, setOn: setOnTrue, setOff });
}

// Modal usage
function ModalExample() {
  return (
    <Toggle>
      {({ on, setOn, setOff }) => (
        <>
          <button onClick={setOn}>Open Modal</button>
          {on && <Modal onClose={setOff} />}
        </>
      )}
    </Toggle>
  );
}

// Dropdown usage
function DropdownExample() {
  return (
    <Toggle>
      {({ on, toggle }) => (
        <>
          <button onClick={toggle}>Menu</button>
          {on && <DropdownMenu />}
        </>
      )}
    </Toggle>
  );
}

// Accordion usage
function AccordionItem({ title, content }) {
  return (
    <Toggle>
      {({ on, toggle }) => (
        <div className="accordion-item">
          <button onClick={toggle}>
            {title} {on ? '▼' : '▶'}
          </button>
          {on && <div className="accordion-content">{content}</div>}
        </div>
      )}
    </Toggle>
  );
}
```

---

## Pattern 2: Fetch with Render Props

```jsx
function Fetch({ url, children }) {
  const [state, setState] = useState({
    data: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    setState({ data: null, loading: true, error: null });

    fetch(url)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(data => setState({ data, loading: false, error: null }))
      .catch(error => setState({ data: null, loading: false, error }));
  }, [url]);

  return children(state);
}

// Usage
function UserProfile({ userId }) {
  return (
    <Fetch url={`/api/users/${userId}`}>
      {({ data, loading, error }) => {
        if (loading) return <Spinner />;
        if (error) return <ErrorMessage error={error} />;
        return (
          <div>
            <h2>{data.name}</h2>
            <p>{data.email}</p>
          </div>
        );
      }}
    </Fetch>
  );
}
```

You can even compose multiple `Fetch` components:

```jsx
function Dashboard({ userId }) {
  return (
    <Fetch url={`/api/users/${userId}`}>
      {({ data: user, loading: loadingUser }) => (
        <Fetch url={`/api/users/${userId}/posts`}>
          {({ data: posts, loading: loadingPosts }) => {
            if (loadingUser || loadingPosts) return <Spinner />;
            return (
              <div>
                <h1>{user.name}'s Dashboard</h1>
                <PostList posts={posts} />
              </div>
            );
          }}
        </Fetch>
      )}
    </Fetch>
  );
}
```

This nesting illustrates both the power and the main weakness of render props. The logic composition works, but deep nesting hurts readability. This problem is sometimes called the "callback pyramid" or "render prop hell."

---

## Render Props vs HOCs vs Hooks

All three patterns solve the same problem: sharing stateful logic between components. Here is how they compare:

```
+-------------------------------------------------------------+
|                    Code Reuse Approaches                    |
+-------------------------------------------------------------+
|                                                             |
|  HOC:              Wraps from outside, injects props        |
|  withMouse(Comp)   Static composition at definition time    |
|                                                             |
|  Render Prop:      Consumer provides rendering function     |
|  <Mouse>{fn}</Mouse>  Dynamic composition at render time    |
|                                                             |
|  Hook:             Directly call in function body           |
|  useMouse()        No wrapper, no nesting, cleanest API     |
|                                                             |
+-------------------------------------------------------------+
```

| Aspect | HOC | Render Props | Hooks |
|---|---|---|---|
| Extra components in tree | Yes (wrapper) | Yes (provider) | No |
| Prop collision risk | Yes | No | No |
| Nesting problem | Wrapper hell | Callback pyramid | None |
| Works with class components | Yes | Yes | No |
| Dynamic composition | No (definition-time) | Yes (render-time) | Yes |
| Readability | Moderate | Can degrade with nesting | Best |

### The Same Logic in All Three Styles

**HOC:**
```jsx
function withMouse(Component) {
  return function WithMouse(props) {
    const [pos, setPos] = useState({ x: 0, y: 0 });
    useEffect(() => { /* ... listener setup ... */ }, []);
    return <Component {...props} mouse={pos} />;
  };
}

const App = withMouse(function App({ mouse }) {
  return <p>{mouse.x}, {mouse.y}</p>;
});
```

**Render Props:**
```jsx
function Mouse({ children }) {
  const [pos, setPos] = useState({ x: 0, y: 0 });
  useEffect(() => { /* ... listener setup ... */ }, []);
  return children(pos);
}

function App() {
  return (
    <Mouse>
      {(mouse) => <p>{mouse.x}, {mouse.y}</p>}
    </Mouse>
  );
}
```

**Hook:**
```jsx
function useMouse() {
  const [pos, setPos] = useState({ x: 0, y: 0 });
  useEffect(() => { /* ... listener setup ... */ }, []);
  return pos;
}

function App() {
  const mouse = useMouse();
  return <p>{mouse.x}, {mouse.y}</p>;
}
```

The hook version is the simplest. No extra components, no nesting, no indirection.

---

## Performance Considerations

### The Inline Function Problem

Every render creates a new inline function, which means the render prop component's children are always "different":

```jsx
// This creates a new function every render
<MouseTracker>
  {(pos) => <Cursor x={pos.x} y={pos.y} />}
</MouseTracker>
```

If `MouseTracker` uses `React.memo` or `shouldComponentUpdate`, the new function reference defeats the optimization.

### The Fix: Extract the Render Function

```jsx
// Define the function outside the render
function renderCursor(pos) {
  return <Cursor x={pos.x} y={pos.y} />;
}

function App() {
  return <MouseTracker>{renderCursor}</MouseTracker>;
}
```

Or use `useCallback`:

```jsx
function App() {
  const renderCursor = useCallback(
    (pos) => <Cursor x={pos.x} y={pos.y} />,
    []
  );
  return <MouseTracker>{renderCursor}</MouseTracker>;
}
```

---

## When to Use / When NOT to Use

### Use Render Props When

- You need to share behavior with class components that cannot use hooks
- A component library exposes render prop APIs (like React Router's older versions, Formik, Downshift)
- You need multiple render customization points (`renderHeader`, `renderRow`, `renderFooter`)
- You want consumers to have full control over what gets rendered with shared data

### Do NOT Use Render Props When

- A custom hook can handle the logic (most cases in modern React)
- The nesting would go deeper than two levels -- switch to hooks
- You are using it just to pass down a single value -- a prop or context is simpler
- Performance is critical and you cannot extract the render function

---

## Common Mistakes

### Mistake 1: Forgetting That children Can Be a Function

```jsx
// WRONG -- treating children as JSX when it is a function
function DataProvider({ children }) {
  const data = useFetchData();
  return <div>{children}</div>;  // children is a function, not JSX!
}

// CORRECT -- call children as a function
function DataProvider({ children }) {
  const data = useFetchData();
  return children(data);
}
```

### Mistake 2: Excessive Nesting

```jsx
// AVOID -- "render prop hell"
<Auth>
  {(user) => (
    <Theme>
      {(theme) => (
        <Locale>
          {(locale) => (
            <Fetch url="/api/data">
              {({ data }) => (
                <Page user={user} theme={theme} locale={locale} data={data} />
              )}
            </Fetch>
          )}
        </Locale>
      )}
    </Theme>
  )}
</Auth>

// BETTER -- use hooks
function Page() {
  const user = useAuth();
  const theme = useTheme();
  const locale = useLocale();
  const { data } = useFetch('/api/data');
  return <div>...</div>;
}
```

### Mistake 3: Not Handling the Case Where children Is Not a Function

```jsx
// Defensive approach
function Toggle({ children }) {
  const [on, setOn] = useState(false);

  if (typeof children !== 'function') {
    throw new Error(
      'Toggle expects children to be a function, ' +
      `but received ${typeof children}`
    );
  }

  return children({ on, toggle: () => setOn(prev => !prev) });
}
```

---

## Best Practices

1. **Prefer children as a function** over a named `render` prop for single-render-function components. It reads more naturally.

2. **Use named render props** when a component needs multiple render customization points.

3. **Extract render functions** to avoid creating new function references on every render.

4. **Type your render props** with TypeScript or PropTypes so consumers know what data they will receive.

5. **Provide sensible defaults** -- if the render prop is optional, render something reasonable when it is not provided.

6. **Consider hooks first** -- if you are writing a new render prop component in a modern codebase, ask whether a hook would be simpler.

7. **Keep the callback data minimal** -- pass only the data the consumer needs, not your entire internal state.

---

## Quick Summary

The render props pattern gives a component its logic while letting consumers control the visual output. A component calls a function (passed as a prop or as children) with its internal data, and the function returns JSX. This inverts control of rendering and enables flexible code reuse. While hooks have become the preferred approach for most logic-sharing, render props remain valuable for multi-slot rendering APIs and class component compatibility.

---

## Key Points

- A render prop is a function passed to a component that returns JSX
- "Children as a function" is the most common variation: `<Comp>{(data) => <UI />}</Comp>`
- Render props solve the same problem as HOCs but with dynamic composition at render time
- Unlike HOCs, render props have no prop collision risk -- consumers name their own variables
- Deep nesting of render props creates readability problems ("callback pyramid")
- Extract render functions or use `useCallback` to prevent unnecessary re-renders
- Hooks have replaced most render prop use cases since React 16.8
- Render props still shine for multi-slot rendering APIs like `renderHeader`, `renderRow`, `renderFooter`

---

## Practice Questions

1. Explain the difference between passing a render prop via a named prop (`render={fn}`) versus via `children`. When would you choose one over the other?

2. A component uses three render prop providers nested inside each other. What readability problem does this create, and what two alternative patterns could flatten it?

3. Why does creating an inline function for a render prop cause performance issues with `React.memo`? How do you fix it?

4. You are building a sortable list component. The sorting logic is reusable, but different consumers need different row layouts. Would you use a render prop, a HOC, or a hook? Justify your choice.

5. How does the render props pattern implement "inversion of control"? Explain using the `MouseTracker` example.

---

## Exercises

### Exercise 1: Build a WindowSize Render Prop Component

Create a `WindowSize` component that tracks the browser window's width and height and exposes them via a children-as-a-function pattern. Use it to build two different consumers: one that shows a responsive layout label ("mobile" / "tablet" / "desktop") and one that shows exact pixel dimensions.

### Exercise 2: Build a Form Field Validator

Create a `FieldValidator` render prop component that accepts a `value` and an array of `rules` (like `required`, `minLength`, `email`). It should expose `{ isValid, errors }` to its children function. Use it to validate a signup form with name, email, and password fields.

### Exercise 3: Convert Render Props to Hooks

Take the `Toggle` and `Fetch` render prop components from this chapter. Convert each into a custom hook (`useToggle`, `useFetch`). Then refactor a consumer component from render props to hooks. Write a short comparison of the two approaches noting lines of code, readability, and nesting depth.

---

## What Is Next?

You have now seen two patterns for sharing logic: HOCs wrap from the outside, and render props inject from within. But what about components that naturally belong together -- like a `<Select>` with its `<Option>` children, or `<Tabs>` with `<Tab>` panels? These related sub-components need to share state implicitly without forcing the consumer to wire everything up manually. That is the Compound Components pattern, which you will learn in Chapter 19.
