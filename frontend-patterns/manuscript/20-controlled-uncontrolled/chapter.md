# Chapter 20: Controlled and Uncontrolled Components

## What You Will Learn

- The fundamental question behind this pattern: who owns the state?
- How controlled components work: parent owns state via `value` + `onChange`
- How uncontrolled components work: component owns state internally, accessed via `ref`
- How to build components that support both modes
- When to use each approach and why
- How `useImperativeHandle` lets you expose custom APIs through refs

## Why This Chapter Matters

Imagine a thermostat. In one mode, you set the temperature manually -- you have full control, and the system does exactly what you tell it. In another mode, the thermostat runs on a schedule it manages internally -- you can read the current temperature, but you are not actively controlling every change.

This is the core tension in React component design: should the parent control the component's state (like the manual thermostat), or should the component manage its own state internally (like the scheduled one)?

Getting this wrong leads to real bugs:

- A form input that ignores what the user types because `value` is set but `onChange` is missing
- A modal that cannot be closed programmatically because it manages its own open/closed state
- A date picker whose state gets out of sync with the form data because neither side has clear ownership

This chapter teaches you to reason about state ownership, build components that work in either mode, and choose the right approach for each situation.

---

## Controlled Components

A controlled component does not manage its own state. Its parent provides the current value and a callback to change it. The component is a "puppet" -- it displays what it is told and reports user interactions back.

```jsx
function ControlledInput() {
  const [name, setName] = useState('');

  return (
    <input
      type="text"
      value={name}                         // Parent says what to show
      onChange={(e) => setName(e.target.value)}  // Parent decides what to do
    />
  );
}
```

```
+---------------------------------------------------+
|  Parent Component (owns state)                    |
|                                                   |
|  state: name = "Alice"                            |
|                                                   |
|  +---------------------------------------------+ |
|  |  <input>                                     | |
|  |                                              | |
|  |  value="Alice"  (what to display)            | |
|  |  onChange={fn}   (what to report)             | |
|  |                                              | |
|  |  User types "B" --> calls onChange("AliceB") | |
|  |  Parent updates state to "AliceB"            | |
|  |  Input re-renders with value="AliceB"        | |
|  +---------------------------------------------+ |
+---------------------------------------------------+
```

The data flows in a single direction:

1. Parent passes `value` down
2. User interacts with the input
3. Input calls `onChange` with the new value
4. Parent updates its state
5. New state flows back down as `value`

### Why Controlled?

Controlled components give you complete power over the value at every moment:

```jsx
function PhoneInput() {
  const [phone, setPhone] = useState('');

  const handleChange = (e) => {
    // Only allow digits
    const digits = e.target.value.replace(/\D/g, '');

    // Format as (XXX) XXX-XXXX
    let formatted = digits;
    if (digits.length > 3) {
      formatted = `(${digits.slice(0, 3)}) ${digits.slice(3)}`;
    }
    if (digits.length > 6) {
      formatted = `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6, 10)}`;
    }

    setPhone(formatted);
  };

  return <input value={phone} onChange={handleChange} />;
}

// User types: 5551234567
// Input shows: (555) 123-4567
```

You can validate, transform, or reject input at every keystroke. This is impossible with an uncontrolled component.

---

## Uncontrolled Components

An uncontrolled component manages its own internal state. The parent does not pass `value` -- instead, it reads the value when needed using a `ref`.

```jsx
function UncontrolledInput() {
  const inputRef = useRef();

  const handleSubmit = () => {
    // Read the value only when needed
    console.log('Name:', inputRef.current.value);
  };

  return (
    <div>
      <input
        type="text"
        defaultValue=""     // Initial value only, not continuously controlled
        ref={inputRef}      // Gives parent access to read the DOM value
      />
      <button onClick={handleSubmit}>Submit</button>
    </div>
  );
}
```

```
+---------------------------------------------------+
|  Parent Component (does NOT own input state)      |
|                                                   |
|  ref ----> points to the <input> DOM node         |
|                                                   |
|  +---------------------------------------------+ |
|  |  <input>                                     | |
|  |                                              | |
|  |  defaultValue=""  (initial value only)       | |
|  |  The DOM manages its own current value       | |
|  |                                              | |
|  |  User types "Alice" --> DOM updates itself   | |
|  |  Parent reads ref.current.value when needed  | |
|  +---------------------------------------------+ |
+---------------------------------------------------+
```

Notice the key differences:

| Controlled | Uncontrolled |
|---|---|
| `value` prop | `defaultValue` prop |
| `onChange` handler required | `onChange` optional |
| React state is the source of truth | DOM is the source of truth |
| Re-renders on every change | No re-render on input changes |
| Full control at every keystroke | Read value only when needed |

### Why Uncontrolled?

Uncontrolled components are simpler for cases where you do not need to intercept or transform every change:

```jsx
function SimpleSearchForm() {
  const searchRef = useRef();

  const handleSubmit = (e) => {
    e.preventDefault();
    const query = searchRef.current.value;
    // Search only happens on submit, not on every keystroke
    performSearch(query);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input ref={searchRef} defaultValue="" placeholder="Search..." />
      <button type="submit">Search</button>
    </form>
  );
}
```

This form does not need to know the value on every keystroke. It only cares about the value when the user submits. Using controlled state here would cause unnecessary re-renders on every character typed.

---

## File Inputs: Always Uncontrolled

Some inputs can only be uncontrolled. File inputs are the classic example -- you cannot programmatically set their value for security reasons:

```jsx
function FileUpload() {
  const fileRef = useRef();

  const handleUpload = () => {
    const file = fileRef.current.files[0];
    if (file) {
      console.log('Uploading:', file.name, file.size, 'bytes');
    }
  };

  return (
    <div>
      {/* File inputs are ALWAYS uncontrolled */}
      <input type="file" ref={fileRef} />
      <button onClick={handleUpload}>Upload</button>
    </div>
  );
}
```

---

## Building Components That Support Both Modes

The most flexible custom components support both controlled and uncontrolled modes. The consumer decides which mode to use based on whether they pass a `value` prop.

```jsx
function useControllableState({ value, defaultValue, onChange }) {
  // If value is provided, the component is controlled
  const isControlled = value !== undefined;

  // Internal state for uncontrolled mode
  const [internalValue, setInternalValue] = useState(defaultValue);

  // Use the controlled value if provided, otherwise internal
  const currentValue = isControlled ? value : internalValue;

  const setValue = (nextValue) => {
    if (!isControlled) {
      setInternalValue(nextValue);
    }
    onChange?.(nextValue);
  };

  return [currentValue, setValue];
}
```

Now use this hook to build a reusable Toggle:

```jsx
function Toggle({ value, defaultValue = false, onChange, children }) {
  const [on, setOn] = useControllableState({
    value,
    defaultValue,
    onChange,
  });

  return (
    <button onClick={() => setOn(!on)}>
      {children}: {on ? 'ON' : 'OFF'}
    </button>
  );
}

// Uncontrolled usage -- Toggle manages its own state
function Example1() {
  return <Toggle defaultValue={false}>WiFi</Toggle>;
  // Click toggles internally. No parent state needed.
}

// Controlled usage -- parent owns the state
function Example2() {
  const [wifiOn, setWifiOn] = useState(true);

  return (
    <div>
      <Toggle value={wifiOn} onChange={setWifiOn}>WiFi</Toggle>
      <p>WiFi is {wifiOn ? 'enabled' : 'disabled'}</p>
      <button onClick={() => setWifiOn(false)}>Force Off</button>
    </div>
  );
}
```

```
Uncontrolled mode:                Controlled mode:

<Toggle defaultValue={false}>    <Toggle value={wifiOn} onChange={setWifiOn}>
  Internal state: on = false       No internal state
  Click -> setOn(true)             Click -> onChange(true)
  Internal state: on = true        Parent: setWifiOn(true)
  Re-renders itself                Parent re-renders Toggle
                                   with value={true}
```

---

## useImperativeHandle: Custom Ref APIs

Sometimes you want an uncontrolled component but need to expose specific methods to the parent -- not the raw DOM node, but a curated API. `useImperativeHandle` lets you define exactly what a `ref` exposes.

### The Problem

```jsx
// Parent wants to focus, clear, and validate the input
// but ref.current gives the raw DOM node with 100+ properties
const inputRef = useRef();

// This works but exposes everything:
inputRef.current.value = '';      // direct DOM mutation
inputRef.current.focus();
inputRef.current.style.border = 'red';  // dangerous!
```

### The Solution

```jsx
const FancyInput = React.forwardRef(function FancyInput(
  { label, defaultValue = '' },
  ref
) {
  const inputRef = useRef();
  const [error, setError] = useState('');

  // Expose only specific methods
  useImperativeHandle(ref, () => ({
    focus() {
      inputRef.current.focus();
    },
    clear() {
      inputRef.current.value = '';
      setError('');
    },
    validate() {
      const value = inputRef.current.value;
      if (!value.trim()) {
        setError('This field is required');
        return false;
      }
      setError('');
      return true;
    },
    getValue() {
      return inputRef.current.value;
    },
  }));

  return (
    <div>
      <label>{label}</label>
      <input ref={inputRef} defaultValue={defaultValue} />
      {error && <span className="error">{error}</span>}
    </div>
  );
});

// Parent usage
function RegistrationForm() {
  const nameRef = useRef();
  const emailRef = useRef();

  const handleSubmit = () => {
    const nameValid = nameRef.current.validate();
    const emailValid = emailRef.current.validate();

    if (nameValid && emailValid) {
      const data = {
        name: nameRef.current.getValue(),
        email: emailRef.current.getValue(),
      };
      submitForm(data);
    }
  };

  const handleReset = () => {
    nameRef.current.clear();
    emailRef.current.clear();
    nameRef.current.focus();
  };

  return (
    <form>
      <FancyInput ref={nameRef} label="Name" />
      <FancyInput ref={emailRef} label="Email" />
      <button type="button" onClick={handleSubmit}>Submit</button>
      <button type="button" onClick={handleReset}>Reset</button>
    </form>
  );
}
```

```
Without useImperativeHandle:      With useImperativeHandle:

ref.current = DOM <input>         ref.current = {
  .value                            focus(),
  .focus()                          clear(),
  .blur()                           validate(),
  .style                            getValue()
  .className                      }
  .setAttribute()
  .addEventListener()             Clean, intentional API
  ... 100+ DOM properties         Only what consumers need
```

### When to Use useImperativeHandle

- When a parent needs to trigger actions on a child (focus, scroll, animate)
- When you want to hide the raw DOM API and expose a cleaner interface
- When building library components where consumers should not access internals
- When you need methods that combine DOM access with state updates (like `validate`)

---

## Choosing Between Controlled and Uncontrolled

```
+-----------------------------------------------------+
|  Decision Guide: Controlled vs Uncontrolled         |
+-----------------------------------------------------+
|                                                     |
|  Do you need to validate/transform on every change? |
|    YES --> Controlled                               |
|                                                     |
|  Do you need the value to sync with other UI?       |
|    YES --> Controlled                               |
|                                                     |
|  Do you need to programmatically set the value?     |
|    YES --> Controlled                               |
|                                                     |
|  Is it a simple form submitted on button click?     |
|    YES --> Uncontrolled is fine                      |
|                                                     |
|  Is it a file input?                                |
|    YES --> Must be uncontrolled                     |
|                                                     |
|  Are re-renders on every keystroke a concern?       |
|    YES --> Consider uncontrolled                    |
|                                                     |
|  Not sure?                                          |
|    --> Default to controlled                        |
+-----------------------------------------------------+
```

### Controlled is Best For

- Forms with real-time validation ("password must be 8+ characters" as they type)
- Formatted inputs (phone numbers, credit cards, currency)
- Conditional logic that depends on the current value ("show confirm email if email is filled")
- Two-way binding between multiple inputs (start date must be before end date)

### Uncontrolled is Best For

- Simple forms that only need values on submit
- File inputs (which must be uncontrolled)
- Integration with non-React code that manages its own DOM state
- Performance-sensitive scenarios where you want to avoid re-renders on every keystroke

---

## When to Use / When NOT to Use

### Use Controlled When

- You need to intercept, validate, or transform values in real time
- The value needs to be synchronized with other components or external state
- You need to programmatically reset or set values
- You are building a form with complex validation rules

### Use Uncontrolled When

- You only need the value at submission time
- The input is a file upload
- You are integrating with a third-party DOM library
- Performance matters and you want to avoid per-keystroke re-renders

### Use Both Modes When

- You are building a reusable component library
- Different consumers have different needs
- You want maximum flexibility (the `useControllableState` pattern)

---

## Common Mistakes

### Mistake 1: Controlled Input Without onChange

```jsx
// WRONG -- input is "frozen" and cannot be edited
function Broken() {
  const [name, setName] = useState('Alice');
  return <input value={name} />;
  // React warns: "You provided a `value` prop without an `onChange` handler"
}

// CORRECT
function Working() {
  const [name, setName] = useState('Alice');
  return <input value={name} onChange={(e) => setName(e.target.value)} />;
}

// Also correct -- if you truly want read-only, use readOnly
function ReadOnly() {
  return <input value="Alice" readOnly />;
}
```

### Mistake 2: Switching Between Controlled and Uncontrolled

```jsx
// WRONG -- starts uncontrolled, becomes controlled
function Broken() {
  const [name, setName] = useState(undefined); // undefined = uncontrolled

  return (
    <input
      value={name}  // First render: undefined (uncontrolled)
      onChange={(e) => setName(e.target.value)}  // After typing: "A" (controlled!)
    />
  );
  // React warns: "changing from uncontrolled to controlled"
}

// CORRECT -- always controlled, start with empty string
function Working() {
  const [name, setName] = useState('');  // '' is a controlled value
  return <input value={name} onChange={(e) => setName(e.target.value)} />;
}
```

### Mistake 3: Using value Instead of defaultValue for Uncontrolled

```jsx
// WRONG -- this is controlled (frozen) not uncontrolled
<input value="initial" ref={inputRef} />

// CORRECT -- defaultValue only sets the initial value
<input defaultValue="initial" ref={inputRef} />
```

### Mistake 4: Over-Using useImperativeHandle

```jsx
// BAD -- reimplementing what controlled props already do
useImperativeHandle(ref, () => ({
  setValue(v) { setInternalValue(v); },
  getValue() { return internalValue; },
  setDisabled(d) { setDisabled(d); },
}));

// This should just be controlled props:
<MyInput value={value} onChange={setValue} disabled={disabled} />
```

`useImperativeHandle` is for imperative actions (focus, scroll, animate) not for state that should be props.

---

## Best Practices

1. **Default to controlled components** unless you have a specific reason for uncontrolled. Controlled components are more predictable and easier to debug.

2. **Initialize controlled state with the correct type** -- use `''` for strings, `false` for booleans, `[]` for arrays. Never use `undefined` as initial state for controlled components.

3. **Build reusable components to support both modes** using the `useControllableState` pattern. This gives consumers flexibility.

4. **Use `defaultValue` / `defaultChecked`** for uncontrolled components, never `value` / `checked`.

5. **Reserve `useImperativeHandle` for imperative actions** like `focus()`, `scrollTo()`, and `validate()`. Do not use it to replace controlled props.

6. **Warn on controlled/uncontrolled switches** -- if your custom component detects a change from one mode to the other, log a warning in development.

7. **Use `React.forwardRef` with `useImperativeHandle`** so the ref API is available to parent components.

---

## Quick Summary

Controlled components receive their value from props and notify changes via callbacks -- the parent is the single source of truth. Uncontrolled components manage their own internal state, with the parent reading values imperatively through refs when needed. The best reusable components support both modes, letting the consumer choose based on their needs. `useImperativeHandle` extends the uncontrolled pattern by letting you expose a custom, limited API through refs instead of the raw DOM.

---

## Key Points

- **Controlled**: `value` + `onChange` -- parent owns the state
- **Uncontrolled**: `defaultValue` + `ref` -- component owns the state
- Controlled gives real-time access and transformation; uncontrolled gives simplicity
- Never switch a component between controlled and uncontrolled modes
- File inputs are always uncontrolled
- `useControllableState` lets you build components that support both modes
- `useImperativeHandle` exposes a curated ref API for imperative actions
- When in doubt, choose controlled

---

## Practice Questions

1. A text input has `value={name}` but no `onChange` handler. What happens when the user tries to type, and why?

2. Explain the difference between `value` and `defaultValue` on an `<input>`. What mode does each one activate?

3. You are building a date picker component for a library. Should it be controlled, uncontrolled, or both? Explain your reasoning.

4. What is the purpose of `useImperativeHandle`, and why would you use it instead of exposing the raw DOM node through a ref?

5. A component's state is initialized with `useState(undefined)` and is passed as `value` to an input. The developer then types in the input, and React logs a warning about switching from uncontrolled to controlled. Explain what happened and how to fix it.

---

## Exercises

### Exercise 1: Build a Controllable Rating Component

Build a star rating component (`<Rating />`) that works in both controlled and uncontrolled modes:
- Uncontrolled: `<Rating defaultValue={3} />` -- manages its own state
- Controlled: `<Rating value={rating} onChange={setRating} />` -- parent owns state
- Display 5 clickable stars that highlight based on the current rating

### Exercise 2: Build a Form with useImperativeHandle

Create a `FormField` component that wraps an input and exposes these methods via `useImperativeHandle`:
- `focus()` -- focuses the input
- `validate()` -- returns `true`/`false` and displays an error message
- `reset()` -- clears the input and error state
- `getValue()` -- returns the current value

Build a registration form using three `FormField` components (name, email, password) and a submit button that calls `validate()` on all fields.

### Exercise 3: Controlled/Uncontrolled Accordion

Build an accordion component that supports both modes:
- Uncontrolled: `<Accordion defaultOpenIndex={0}>` -- manages which panel is open internally
- Controlled: `<Accordion openIndex={idx} onToggle={setIdx}>` -- parent controls which panel is open
- Add a "Expand All" button that only works in controlled mode

---

## What Is Next?

Controlled components let a parent manage one component's state. But what about state that needs to be shared across many components at different levels of the tree? Passing props through every intermediate component (prop drilling) becomes painful fast. In Chapter 21, you will learn the Provider pattern -- using React Context to make state available to any component in the tree without drilling props through every level.
