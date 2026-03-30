# Chapter 19: Compound Components

## What You Will Learn

- What compound components are and the problem they solve
- How to build compound components using `React.Children` and `cloneElement`
- How to build compound components using React Context (the modern approach)
- How to implement real-world patterns: `Select`/`Option`, `Tabs`/`Tab`/`TabPanel`
- How to validate that only allowed children are used
- How to balance flexibility with guardrails in component APIs

## Why This Chapter Matters

Think about an HTML `<select>` element. You do not write `<select items={['Red', 'Blue', 'Green']} />`. Instead, you write:

```html
<select>
  <option value="red">Red</option>
  <option value="blue">Blue</option>
  <option value="green">Green</option>
</select>
```

The `<select>` and `<option>` work together. The `<select>` manages which option is selected, and the `<option>` elements know how to render themselves and respond to clicks -- all without you manually wiring up state between them. They share state *implicitly*.

This is the compound components pattern: a set of components that work together to form a complete UI element, sharing state behind the scenes so the consumer gets a clean, declarative API.

Without this pattern, component APIs tend to become unwieldy. You end up with components that accept dozens of props -- arrays of items, custom render functions for each slot, callback props for every possible interaction. Compound components flip this around: instead of one monolithic component, you provide a family of smaller components that compose naturally.

---

## The Problem: Monolithic Component APIs

Consider building a Tabs component. The monolithic approach might look like this:

```jsx
// Monolithic API -- everything through props
<Tabs
  tabs={[
    { label: 'Profile', content: <ProfilePanel /> },
    { label: 'Settings', content: <SettingsPanel /> },
    { label: 'Billing', content: <BillingPanel />, disabled: true },
  ]}
  defaultActiveIndex={0}
  onChange={(index) => console.log(index)}
  tabClassName="custom-tab"
  panelClassName="custom-panel"
  renderTab={(tab, isActive) => (
    <span className={isActive ? 'active' : ''}>{tab.label}</span>
  )}
/>
```

This has problems:

- The API surface is huge -- many props to learn and document
- Customization requires render props or special prop shapes
- Adding a new feature (like an icon in one tab) requires changing the data structure
- TypeScript types become complex nested objects

### The Compound Component Solution

```jsx
// Compound API -- natural, declarative, flexible
<Tabs defaultIndex={0} onChange={(index) => console.log(index)}>
  <TabList>
    <Tab>Profile</Tab>
    <Tab>Settings</Tab>
    <Tab disabled>Billing</Tab>
  </TabList>
  <TabPanels>
    <TabPanel><ProfilePanel /></TabPanel>
    <TabPanel><SettingsPanel /></TabPanel>
    <TabPanel><BillingPanel /></TabPanel>
  </TabPanels>
</Tabs>
```

This reads like HTML. Each piece is a separate component that you can style, extend, or customize independently. Want an icon in one tab? Just add it:

```jsx
<Tab><Icon name="user" /> Profile</Tab>
```

No API change needed.

```
Monolithic:                     Compound:
+-------------------------+    +-------------------------+
|  <Tabs                  |    |  <Tabs>                 |
|    tabs={[...]}         |    |    <TabList>             |
|    renderTab={fn}       |    |      <Tab>Profile</Tab> |
|    renderPanel={fn}     |    |      <Tab>Settings</Tab>|
|    onChange={fn}        |    |    </TabList>            |
|    tabClassName="..."   |    |    <TabPanels>           |
|    panelClassName="..." |    |      <TabPanel>...</TabPanel>
|    ...20 more props     |    |      <TabPanel>...</TabPanel>
|  />                     |    |    </TabPanels>          |
+-------------------------+    |  </Tabs>                 |
                               +-------------------------+
```

---

## Approach 1: cloneElement (Legacy)

The original way to share state between parent and children was `React.Children` and `React.cloneElement`. The parent iterates over its children and injects props into them.

### Simple Select/Option Example

```jsx
function Select({ children, value, onChange }) {
  return (
    <div className="select" role="listbox">
      {React.Children.map(children, (child) => {
        // Clone each child and inject extra props
        return React.cloneElement(child, {
          isSelected: child.props.value === value,
          onSelect: () => onChange(child.props.value),
        });
      })}
    </div>
  );
}

function Option({ value, children, isSelected, onSelect }) {
  return (
    <div
      className={`option ${isSelected ? 'selected' : ''}`}
      onClick={onSelect}
      role="option"
      aria-selected={isSelected}
    >
      {children}
    </div>
  );
}

// Usage
function ColorPicker() {
  const [color, setColor] = useState('red');

  return (
    <Select value={color} onChange={setColor}>
      <Option value="red">Red</Option>
      <Option value="blue">Blue</Option>
      <Option value="green">Green</Option>
    </Select>
  );
}

// Output (when "red" is selected):
// [Red]  (highlighted)
//  Blue
//  Green
```

### How cloneElement Works

```
1. Parent receives children:
   <Select>
     <Option value="red">Red</Option>    <-- original child
     <Option value="blue">Blue</Option>  <-- original child
   </Select>

2. Parent clones each child with extra props:
   React.cloneElement(child, {
     isSelected: true,    <-- injected
     onSelect: fn         <-- injected
   })

3. Resulting element:
   <Option value="red" isSelected={true} onSelect={fn}>Red</Option>
```

### Problems with cloneElement

This approach has significant limitations:

1. **Only works with direct children** -- if you wrap an `<Option>` in a `<div>`, the parent cannot find it
2. **Fragile** -- it relies on the children being specific component types
3. **Implicit prop injection** -- the child receives props it did not declare, which is confusing
4. **No nesting flexibility** -- adding intermediate wrapper components breaks the pattern

```jsx
// This breaks with cloneElement:
<Select value={color} onChange={setColor}>
  <div className="group">          {/* <-- wrapper breaks it */}
    <Option value="red">Red</Option>
  </div>
  <Option value="blue">Blue</Option>
</Select>
```

---

## Approach 2: Context (Modern)

The modern approach uses React Context to share state. The parent provides state through context, and children consume it. This works regardless of nesting depth.

### Select/Option with Context

```jsx
// Create a context for the Select state
const SelectContext = React.createContext();

function Select({ children, value, onChange }) {
  return (
    <SelectContext.Provider value={{ selectedValue: value, onChange }}>
      <div className="select" role="listbox">
        {children}
      </div>
    </SelectContext.Provider>
  );
}

function Option({ value, children }) {
  const { selectedValue, onChange } = useContext(SelectContext);
  const isSelected = value === selectedValue;

  return (
    <div
      className={`option ${isSelected ? 'selected' : ''}`}
      onClick={() => onChange(value)}
      role="option"
      aria-selected={isSelected}
    >
      {children}
    </div>
  );
}

// Usage -- exactly the same API
function ColorPicker() {
  const [color, setColor] = useState('red');

  return (
    <Select value={color} onChange={setColor}>
      <Option value="red">Red</Option>
      <Option value="blue">Blue</Option>
      <Option value="green">Green</Option>
    </Select>
  );
}
```

Now nesting works perfectly:

```jsx
// This works with Context approach:
<Select value={color} onChange={setColor}>
  <div className="primary-colors">
    <Option value="red">Red</Option>
    <Option value="blue">Blue</Option>
  </div>
  <div className="secondary-colors">
    <Option value="green">Green</Option>
    <Option value="purple">Purple</Option>
  </div>
</Select>
```

```
cloneElement approach:           Context approach:

Select                           Select (provides context)
  |-- cloneElement(Option)         |-- <div> (any wrapper)
  |-- cloneElement(Option)         |     |-- Option (reads context)
  |-- cloneElement(Option)         |     |-- Option (reads context)
                                   |-- <div>
Can only inject into                    |-- Option (reads context)
DIRECT children
                                 Works at ANY depth
```

---

## Full Example: Tabs Component

Here is a complete Tabs implementation using context-based compound components:

```jsx
// --- Context ---
const TabsContext = React.createContext();

// --- Parent: Tabs ---
function Tabs({ children, defaultIndex = 0, onChange }) {
  const [activeIndex, setActiveIndex] = useState(defaultIndex);

  const selectTab = (index) => {
    setActiveIndex(index);
    onChange?.(index);
  };

  return (
    <TabsContext.Provider value={{ activeIndex, selectTab }}>
      <div className="tabs">{children}</div>
    </TabsContext.Provider>
  );
}

// --- TabList ---
function TabList({ children }) {
  return (
    <div className="tab-list" role="tablist">
      {React.Children.map(children, (child, index) =>
        React.cloneElement(child, { index })
      )}
    </div>
  );
}

// --- Tab ---
function Tab({ children, index, disabled = false }) {
  const { activeIndex, selectTab } = useContext(TabsContext);
  const isActive = index === activeIndex;

  return (
    <button
      className={`tab ${isActive ? 'tab--active' : ''}`}
      onClick={() => !disabled && selectTab(index)}
      disabled={disabled}
      role="tab"
      aria-selected={isActive}
    >
      {children}
    </button>
  );
}

// --- TabPanels ---
function TabPanels({ children }) {
  const { activeIndex } = useContext(TabsContext);
  return (
    <div className="tab-panels">
      {React.Children.toArray(children)[activeIndex]}
    </div>
  );
}

// --- TabPanel ---
function TabPanel({ children }) {
  return (
    <div className="tab-panel" role="tabpanel">
      {children}
    </div>
  );
}

// --- Attach sub-components to parent ---
Tabs.TabList = TabList;
Tabs.Tab = Tab;
Tabs.TabPanels = TabPanels;
Tabs.TabPanel = TabPanel;
```

Usage:

```jsx
function SettingsPage() {
  return (
    <Tabs defaultIndex={0} onChange={(i) => console.log('Tab:', i)}>
      <Tabs.TabList>
        <Tabs.Tab>General</Tabs.Tab>
        <Tabs.Tab>Security</Tabs.Tab>
        <Tabs.Tab disabled>Advanced</Tabs.Tab>
      </Tabs.TabList>
      <Tabs.TabPanels>
        <Tabs.TabPanel>
          <GeneralSettings />
        </Tabs.TabPanel>
        <Tabs.TabPanel>
          <SecuritySettings />
        </Tabs.TabPanel>
        <Tabs.TabPanel>
          <AdvancedSettings />
        </Tabs.TabPanel>
      </Tabs.TabPanels>
    </Tabs>
  );
}

// Output (when "General" tab is active):
// [General]  Security  Advanced(disabled)
// +---------------------------------+
// |  General settings content...    |
// +---------------------------------+
```

Notice the hybrid approach: `TabList` uses `cloneElement` to inject the `index` prop (since tabs must know their position), while `Tab` and `TabPanels` use context for the shared state. This is a common real-world pattern -- use whatever works best for each sub-component.

---

## Attaching Sub-Components as Static Properties

A clean API convention is to attach sub-components as properties of the parent:

```jsx
// Definition
Tabs.TabList = TabList;
Tabs.Tab = Tab;
Tabs.TabPanels = TabPanels;
Tabs.TabPanel = TabPanel;

// Usage -- single import gives you everything
import { Tabs } from './Tabs';

<Tabs>
  <Tabs.TabList>
    <Tabs.Tab>...</Tabs.Tab>
  </Tabs.TabList>
  <Tabs.TabPanels>
    <Tabs.TabPanel>...</Tabs.TabPanel>
  </Tabs.TabPanels>
</Tabs>
```

This pattern has two benefits:

1. **Discoverability** -- consumers type `Tabs.` and see all available sub-components
2. **Single import** -- no need to import `Tab`, `TabList`, `TabPanel` separately

Libraries like Radix UI, Reach UI, and Chakra UI use this approach extensively.

---

## Validating Children

You can add guardrails to ensure consumers use the right sub-components:

```jsx
function Select({ children, value, onChange }) {
  // Validate that all direct children are Option components
  React.Children.forEach(children, (child) => {
    if (child.type !== Option) {
      console.warn(
        `Select expects Option children, but received ${
          child.type?.name || child.type || typeof child
        }`
      );
    }
  });

  return (
    <SelectContext.Provider value={{ selectedValue: value, onChange }}>
      <div className="select" role="listbox">
        {children}
      </div>
    </SelectContext.Provider>
  );
}
```

A more robust approach is to use context and throw if the context is missing:

```jsx
function useSelectContext() {
  const context = useContext(SelectContext);
  if (!context) {
    throw new Error(
      'Option must be used within a Select component. ' +
      'Wrap your Option components inside <Select>.'
    );
  }
  return context;
}

function Option({ value, children }) {
  const { selectedValue, onChange } = useSelectContext();
  // ...
}
```

This gives a clear error message if someone uses `<Option>` outside of a `<Select>`.

---

## Real-World Use Case: Accordion

```jsx
const AccordionContext = React.createContext();

function Accordion({ children, allowMultiple = false }) {
  const [openItems, setOpenItems] = useState(new Set());

  const toggleItem = (id) => {
    setOpenItems((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        if (!allowMultiple) next.clear();
        next.add(id);
      }
      return next;
    });
  };

  const isOpen = (id) => openItems.has(id);

  return (
    <AccordionContext.Provider value={{ toggleItem, isOpen }}>
      <div className="accordion">{children}</div>
    </AccordionContext.Provider>
  );
}

function AccordionItem({ children, id }) {
  return <div className="accordion-item">{children}</div>;
}

function AccordionHeader({ children, itemId }) {
  const { toggleItem, isOpen } = useContext(AccordionContext);

  return (
    <button
      className="accordion-header"
      onClick={() => toggleItem(itemId)}
      aria-expanded={isOpen(itemId)}
    >
      {children}
      <span>{isOpen(itemId) ? '▼' : '▶'}</span>
    </button>
  );
}

function AccordionPanel({ children, itemId }) {
  const { isOpen } = useContext(AccordionContext);

  if (!isOpen(itemId)) return null;

  return <div className="accordion-panel">{children}</div>;
}

// Usage
function FAQ() {
  return (
    <Accordion allowMultiple={false}>
      <AccordionItem id="q1">
        <AccordionHeader itemId="q1">
          What is React?
        </AccordionHeader>
        <AccordionPanel itemId="q1">
          React is a JavaScript library for building user interfaces.
        </AccordionPanel>
      </AccordionItem>

      <AccordionItem id="q2">
        <AccordionHeader itemId="q2">
          What are hooks?
        </AccordionHeader>
        <AccordionPanel itemId="q2">
          Hooks let you use state and other features in function components.
        </AccordionPanel>
      </AccordionItem>
    </Accordion>
  );
}

// Output (when "What is React?" is expanded):
// [v] What is React?
//     React is a JavaScript library for building user interfaces.
// [>] What are hooks?
```

---

## When to Use / When NOT to Use

### Use Compound Components When

- You have a set of components that only make sense together (tabs, accordions, selects)
- The monolithic prop-based API is becoming unwieldy
- Consumers need flexibility in the structure and layout of sub-components
- You want a declarative, HTML-like API

### Do NOT Use Compound Components When

- The component is simple enough for a single component with a few props
- There is only one logical way to compose the children (no flexibility needed)
- The components do not share state -- they are independent
- The overhead of context and multiple components is not justified by the flexibility gained

---

## Common Mistakes

### Mistake 1: Relying Only on cloneElement

```jsx
// FRAGILE -- breaks with wrapper elements
<Select>
  <div className="group">
    <Option value="a">A</Option>   {/* cloneElement cannot reach this */}
  </div>
</Select>

// ROBUST -- use Context instead
// Option reads from SelectContext regardless of nesting depth
```

### Mistake 2: Not Providing Error Messages for Misuse

```jsx
// BAD -- silent failure when used outside parent
function Tab({ index }) {
  const ctx = useContext(TabsContext);
  // ctx is undefined if used outside Tabs -- silent bugs
}

// GOOD -- explicit error
function Tab({ index }) {
  const ctx = useContext(TabsContext);
  if (!ctx) {
    throw new Error('Tab must be rendered inside a Tabs component');
  }
}
```

### Mistake 3: Putting Too Much in Context

```jsx
// BAD -- entire parent state in context causes all children to re-render
<TabsContext.Provider value={{
  activeIndex,
  selectTab,
  tabs,          // array that changes reference
  animating,     // changes frequently
  history,       // grows over time
}}>

// BETTER -- only the minimum needed state
<TabsContext.Provider value={{ activeIndex, selectTab }}>
```

### Mistake 4: Forgetting to Memoize Context Value

```jsx
// BAD -- new object every render, all consumers re-render
function Tabs({ children }) {
  const [activeIndex, setActiveIndex] = useState(0);
  return (
    <TabsContext.Provider value={{ activeIndex, setActiveIndex }}>
      {children}
    </TabsContext.Provider>
  );
}

// GOOD -- stable reference when values have not changed
function Tabs({ children }) {
  const [activeIndex, setActiveIndex] = useState(0);
  const value = useMemo(
    () => ({ activeIndex, setActiveIndex }),
    [activeIndex]
  );
  return (
    <TabsContext.Provider value={value}>
      {children}
    </TabsContext.Provider>
  );
}
```

---

## Best Practices

1. **Use Context over cloneElement** for state sharing. Context works at any nesting depth and does not break with wrapper elements.

2. **Attach sub-components as static properties** of the parent (`Tabs.Tab`, `Tabs.Panel`) for a clean, discoverable API.

3. **Create a custom hook** for consuming the context (like `useTabsContext`) that throws a descriptive error when used outside the provider.

4. **Memoize the context value** to prevent unnecessary re-renders of all consuming children.

5. **Keep the context value minimal** -- only include the state that sub-components actually need.

6. **Add ARIA attributes** to make compound components accessible. Tabs need `role="tablist"`, `role="tab"`, `role="tabpanel"`, and `aria-selected`.

7. **Consider a hybrid approach** -- use `cloneElement` for injecting positional data (like index) and Context for shared state.

---

## Quick Summary

Compound components are a group of related components that share implicit state to form a cohesive UI element. Instead of one component with dozens of props, you provide a family of components that compose declaratively. The modern approach uses React Context so that sub-components can read shared state regardless of nesting depth. This pattern powers tabs, accordions, selects, menus, and many other multi-part UI elements.

---

## Key Points

- Compound components split a complex UI element into collaborating sub-components
- The parent manages state; children consume it implicitly
- `cloneElement` works for direct children but breaks with nesting
- React Context is the modern, robust approach to sharing state
- Attach sub-components as static properties for clean imports: `Tabs.Tab`
- Always create a custom context hook that throws if used outside the provider
- Memoize context values to avoid unnecessary re-renders
- This pattern is used extensively by component libraries: Radix UI, Reach UI, Headless UI, Chakra UI

---

## Practice Questions

1. What are the limitations of using `React.cloneElement` for compound components, and how does React Context solve them?

2. Explain why memoizing the context value in a compound component parent is important for performance. What happens if you do not memoize it?

3. A teammate builds a `<Menu>` compound component but consumers report that `<Menu.Item>` throws errors when they wrap items in a styled `<div>`. What approach was likely used, and how would you fix it?

4. Compare the monolithic API (`<Tabs tabs={[...]} />`) with the compound API (`<Tabs><Tab>...</Tab></Tabs>`). What are two advantages and one disadvantage of the compound approach?

5. How would you prevent a consumer from using `<Option>` outside of a `<Select>` component? Write the code for the error handling.

---

## Exercises

### Exercise 1: Build a Compound Select Component

Build a `Select` / `Option` compound component using Context. Requirements:
- `Select` manages which option is selected
- `Option` highlights itself when selected and calls `onChange` when clicked
- Support wrapping options in `<div>` group containers
- Show a clear error if `Option` is used outside `Select`

### Exercise 2: Build Compound Accordion

Build an `Accordion` with `AccordionItem`, `AccordionHeader`, and `AccordionPanel` sub-components. Requirements:
- Support single-expand mode (only one item open at a time)
- Support multi-expand mode (multiple items can be open)
- Add keyboard navigation (Enter/Space to toggle)
- Add ARIA attributes for accessibility

### Exercise 3: Extend Tabs with Controlled Mode

Take the `Tabs` component from this chapter and add support for *controlled* mode. The consumer should be able to pass an `activeIndex` prop to control which tab is active externally (like a controlled input). When `activeIndex` is provided, the component should use it instead of internal state.

---

## What Is Next?

The Tabs exercise asked you to support both "controlled" and "uncontrolled" modes. This is a fundamental pattern in React: who owns the state? In Chapter 20, you will explore the Controlled and Uncontrolled Components pattern in depth -- understanding when a component should manage its own state versus deferring to its parent, and how to build components that support both modes gracefully.
