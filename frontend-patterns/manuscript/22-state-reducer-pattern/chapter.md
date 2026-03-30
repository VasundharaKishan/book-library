# Chapter 22: The State Reducer Pattern

## What You Will Learn

- What the state reducer pattern is and why it exists
- How to implement customizable state transitions by accepting a user-supplied reducer
- The principle of inversion of control and how it applies to component state
- How to build a `useToggle` hook with a state reducer
- How to provide sensible defaults while letting consumers override any transition
- Real-world examples where this pattern shines

## Why This Chapter Matters

Imagine you build a light switch component for a smart home app. It works perfectly: click to toggle on and off. Then a customer says, "I want the light to turn off automatically after 5 seconds." Another says, "I want to prevent turning it off while a security alarm is active." A third says, "I want clicking to cycle through brightness levels instead of just on/off."

You could add props for each request: `autoOff`, `preventOff`, `cycleBrightness`. But the requests keep coming, and each new prop adds complexity. Eventually, your component has 20 boolean props controlling every possible behavior, and the code is a tangled mess of conditional logic.

The state reducer pattern takes a different approach. Instead of anticipating every possible customization, you let the consumer *replace* your state transition logic with their own. You provide sensible defaults, and the consumer can override any transition for any action. It is like giving someone the light switch but saying, "Here is how the switch normally works. If you want it to work differently, just tell me what to do instead."

This is a powerful application of inversion of control: the component defines *what* actions exist, and the consumer defines *how* those actions affect state.

---

## The Core Concept

A state reducer is a function that determines how state changes in response to actions. The pattern works like this:

1. Your component/hook has an internal reducer with default behavior
2. You accept an optional `reducer` (or `stateReducer`) from the consumer
3. When an action happens, the consumer's reducer runs instead of (or alongside) the default one
4. The consumer can modify, override, or extend any state transition

```
+-------------------------------------------------------------+
|  Without State Reducer:                                     |
|                                                             |
|  Action --> Internal Reducer --> New State                   |
|             (fixed behavior)                                |
|                                                             |
+-------------------------------------------------------------+
|  With State Reducer:                                        |
|                                                             |
|  Action --> Consumer's Reducer --> New State                 |
|             (customizable)                                  |
|             |                                               |
|             v                                               |
|             Can call the internal                           |
|             reducer for defaults                            |
+-------------------------------------------------------------+
```

---

## Building useToggle with a State Reducer

Let us start with a simple `useToggle` hook and evolve it step by step.

### Step 1: Basic useToggle (No Customization)

```jsx
function useToggle({ initialOn = false } = {}) {
  const [on, setOn] = useState(initialOn);

  const toggle = () => setOn(prev => !prev);
  const setOff = () => setOn(false);
  const setOnTrue = () => setOn(true);

  return { on, toggle, setOff, setOn: setOnTrue };
}

// Usage
function LightSwitch() {
  const { on, toggle } = useToggle();
  return (
    <button onClick={toggle}>
      Light is {on ? 'ON' : 'OFF'}
    </button>
  );
}
```

This works fine until someone needs custom behavior. What if they want to prevent toggling off? They cannot -- the logic is locked inside the hook.

### Step 2: Convert to useReducer

First, refactor to use `useReducer` so we have a reducer function to customize:

```jsx
// Action types
const TOGGLE = 'TOGGLE';
const SET_ON = 'SET_ON';
const SET_OFF = 'SET_OFF';

// Default reducer -- the "normal" behavior
function toggleReducer(state, action) {
  switch (action.type) {
    case TOGGLE:
      return { on: !state.on };
    case SET_ON:
      return { on: true };
    case SET_OFF:
      return { on: false };
    default:
      throw new Error(`Unknown action type: ${action.type}`);
  }
}

function useToggle({ initialOn = false } = {}) {
  const [state, dispatch] = useReducer(toggleReducer, { on: initialOn });

  const toggle = () => dispatch({ type: TOGGLE });
  const setOff = () => dispatch({ type: SET_OFF });
  const setOn = () => dispatch({ type: SET_ON });

  return { on: state.on, toggle, setOff, setOn };
}
```

Same behavior, but now the state transitions are handled by a reducer function that we can make replaceable.

### Step 3: Accept a Custom Reducer

Now the key step: let the consumer provide their own reducer:

```jsx
function useToggle({ initialOn = false, reducer = toggleReducer } = {}) {
  const [state, dispatch] = useReducer(reducer, { on: initialOn });

  const toggle = () => dispatch({ type: TOGGLE });
  const setOff = () => dispatch({ type: SET_OFF });
  const setOn = () => dispatch({ type: SET_ON });

  return { on: state.on, toggle, setOff, setOn };
}

// Export action types so consumers can reference them
useToggle.types = { TOGGLE, SET_ON, SET_OFF };

// Export the default reducer so consumers can call it for defaults
useToggle.reducer = toggleReducer;
```

Now a consumer can override behavior:

```jsx
// Custom reducer: prevent turning off
function preventOffReducer(state, action) {
  if (action.type === useToggle.types.SET_OFF) {
    return state; // Ignore the SET_OFF action
  }
  if (action.type === useToggle.types.TOGGLE && state.on) {
    return state; // Ignore toggle when already on
  }
  // For everything else, use default behavior
  return useToggle.reducer(state, action);
}

function AlarmLight() {
  const { on, toggle, setOn, setOff } = useToggle({
    reducer: preventOffReducer,
  });

  return (
    <div>
      <button onClick={toggle}>Toggle</button>
      <button onClick={setOn}>Force On</button>
      <button onClick={setOff}>Force Off (blocked!)</button>
      <p>Alarm light is {on ? 'ON' : 'OFF'}</p>
    </div>
  );
}
```

```
Default reducer:                     Custom reducer:

TOGGLE: on=true  -> on=false         TOGGLE: on=true  -> on=true (blocked!)
TOGGLE: on=false -> on=true          TOGGLE: on=false -> on=true
SET_ON:          -> on=true          SET_ON:          -> on=true
SET_OFF:         -> on=false         SET_OFF:         -> on=false (blocked!)
```

---

## Real-World Example: useToggle with Maximum Click Count

A more practical example: a toggle that can only be toggled a certain number of times.

```jsx
function clickLimitReducer(state, action) {
  // Allow all default behavior, but track clicks
  if (action.type === useToggle.types.TOGGLE) {
    if (state.clickCount >= 4) {
      return state; // No more toggles allowed
    }
    return {
      ...useToggle.reducer(state, action),
      clickCount: (state.clickCount || 0) + 1,
    };
  }
  return useToggle.reducer(state, action);
}

function LimitedToggle() {
  const { on, toggle } = useToggle({
    reducer: clickLimitReducer,
  });

  return (
    <button onClick={toggle}>
      {on ? 'ON' : 'OFF'} (limited clicks)
    </button>
  );
}
```

Notice how the custom reducer *extends* the default behavior by adding `clickCount` to the state. It does not have to replace everything -- it can build on top of the defaults.

---

## Pattern: Providing Both Changes and Action to the Reducer

A more powerful approach gives the consumer's reducer the proposed changes from the default reducer, so they can see what *would* happen and decide whether to allow it:

```jsx
function useToggle({ initialOn = false, reducer: userReducer } = {}) {
  function internalReducer(state, action) {
    // Calculate what the default reducer would produce
    const changes = toggleReducer(state, action);

    // If no custom reducer, use defaults
    if (!userReducer) {
      return changes;
    }

    // Let the consumer decide what to keep
    return userReducer(state, { ...action, changes });
  }

  const [state, dispatch] = useReducer(internalReducer, {
    on: initialOn,
  });

  const toggle = () => dispatch({ type: TOGGLE });
  const setOff = () => dispatch({ type: SET_OFF });
  const setOn = () => dispatch({ type: SET_ON });

  return { on: state.on, toggle, setOff, setOn };
}
```

Now the consumer's reducer receives the *proposed changes* along with the action:

```jsx
function myReducer(state, action) {
  // action.changes contains what the default reducer WOULD return

  if (action.type === TOGGLE && state.on) {
    // When toggling off, ask for confirmation instead
    if (!window.confirm('Are you sure you want to turn off?')) {
      return state; // Cancel the change
    }
  }

  // Accept the default changes
  return action.changes;
}

function ConfirmableSwitch() {
  const { on, toggle } = useToggle({ reducer: myReducer });

  return (
    <button onClick={toggle}>
      {on ? 'ON' : 'OFF'}
    </button>
  );
}
```

```
Flow with proposed changes:

1. User clicks toggle (on=true currently)
2. Internal reducer calculates: changes = { on: false }
3. Consumer's reducer receives:
   state = { on: true }
   action = { type: 'TOGGLE', changes: { on: false } }
4. Consumer decides:
   - Return action.changes to accept ({ on: false })
   - Return state to reject (stay { on: true })
   - Return something else to modify ({ on: false, reason: 'user' })
```

---

## Inversion of Control

The state reducer pattern is a concrete example of *inversion of control* (IoC). In normal component design, the component controls everything:

```
Normal control flow:
Component decides what happens --> Consumer uses it as-is

Inverted control flow:
Component defines what actions exist
Consumer decides what happens for each action
```

Compare this to other IoC patterns you have seen:

| Pattern | What Is Inverted |
|---|---|
| Render Props | Control of what is *rendered* |
| Compound Components | Control of *structure and layout* |
| State Reducer | Control of *state transitions* |

The state reducer is the most powerful form of IoC because state drives everything in a UI. If you control how state changes, you control the entire behavior of the component.

---

## A More Complete Example: useSelect

Here is a more complex hook that manages a select/dropdown component:

```jsx
const SELECT_ACTIONS = {
  OPEN: 'OPEN',
  CLOSE: 'CLOSE',
  SELECT_ITEM: 'SELECT_ITEM',
  HIGHLIGHT_ITEM: 'HIGHLIGHT_ITEM',
  CLEAR: 'CLEAR',
};

function selectReducer(state, action) {
  switch (action.type) {
    case SELECT_ACTIONS.OPEN:
      return { ...state, isOpen: true };
    case SELECT_ACTIONS.CLOSE:
      return { ...state, isOpen: false, highlightedIndex: -1 };
    case SELECT_ACTIONS.SELECT_ITEM:
      return {
        ...state,
        selectedItem: action.item,
        isOpen: false,
        highlightedIndex: -1,
      };
    case SELECT_ACTIONS.HIGHLIGHT_ITEM:
      return { ...state, highlightedIndex: action.index };
    case SELECT_ACTIONS.CLEAR:
      return { ...state, selectedItem: null };
    default:
      throw new Error(`Unknown action: ${action.type}`);
  }
}

function useSelect({ items, reducer: userReducer } = {}) {
  function internalReducer(state, action) {
    const changes = selectReducer(state, action);
    if (!userReducer) return changes;
    return userReducer(state, { ...action, changes });
  }

  const [state, dispatch] = useReducer(internalReducer, {
    isOpen: false,
    selectedItem: null,
    highlightedIndex: -1,
  });

  return {
    ...state,
    open: () => dispatch({ type: SELECT_ACTIONS.OPEN }),
    close: () => dispatch({ type: SELECT_ACTIONS.CLOSE }),
    selectItem: (item) =>
      dispatch({ type: SELECT_ACTIONS.SELECT_ITEM, item }),
    highlightItem: (index) =>
      dispatch({ type: SELECT_ACTIONS.HIGHLIGHT_ITEM, index }),
    clear: () => dispatch({ type: SELECT_ACTIONS.CLEAR }),
  };
}

useSelect.types = SELECT_ACTIONS;
useSelect.reducer = selectReducer;
```

Consumer customization: keep the dropdown open after selection (for multi-select behavior):

```jsx
function keepOpenReducer(state, action) {
  if (action.type === useSelect.types.SELECT_ITEM) {
    // Accept the selection but override isOpen to stay true
    return {
      ...action.changes,
      isOpen: true,  // Override: keep it open
    };
  }
  return action.changes;
}

function MultiSelect({ items }) {
  const { isOpen, selectedItem, open, selectItem } = useSelect({
    items,
    reducer: keepOpenReducer,
  });

  return (
    <div>
      <button onClick={open}>Select...</button>
      {isOpen && (
        <ul>
          {items.map(item => (
            <li key={item} onClick={() => selectItem(item)}>
              {item}
            </li>
          ))}
        </ul>
      )}
      <p>Selected: {selectedItem}</p>
    </div>
  );
}
```

---

## When to Use / When NOT to Use

### Use the State Reducer Pattern When

- You are building a reusable component or hook that different consumers need to customize
- You cannot predict all the ways consumers will want to modify behavior
- The component has well-defined actions but consumers need different responses to those actions
- You want to give consumers full control without sacrificing sensible defaults

### Do NOT Use the State Reducer Pattern When

- The component is application-specific, not reusable -- just write the reducer you need
- The customization needs are simple enough for a prop (like `disabled` or `maxLength`)
- There are only one or two possible customizations -- props or callbacks are simpler
- Your team is not comfortable with reducers -- the pattern adds conceptual overhead

---

## Common Mistakes

### Mistake 1: Not Exposing the Default Reducer

```jsx
// BAD -- consumer has to reimplement all default behavior
function useToggle({ reducer }) {
  const [state, dispatch] = useReducer(reducer, { on: false });
  // ...
}

// Consumer must handle EVERY action type, even for default behavior
function myReducer(state, action) {
  switch (action.type) {
    case 'TOGGLE': return { on: !state.on };
    case 'SET_ON': return { on: true };
    case 'SET_OFF': return { on: false };
    // Must implement ALL defaults manually
  }
}

// GOOD -- export the default reducer so consumers can delegate
useToggle.reducer = toggleReducer;

function myReducer(state, action) {
  if (action.type === 'SET_OFF') return state; // Custom: block SET_OFF
  return useToggle.reducer(state, action);      // Default for everything else
}
```

### Mistake 2: Not Exposing Action Types

```jsx
// BAD -- consumer uses magic strings
function myReducer(state, action) {
  if (action.type === 'TOGGLE') { ... }  // What if the type name changes?
}

// GOOD -- export action types as constants
useToggle.types = { TOGGLE, SET_ON, SET_OFF };

function myReducer(state, action) {
  if (action.type === useToggle.types.TOGGLE) { ... }
}
```

### Mistake 3: Mutating State in the Reducer

```jsx
// WRONG -- mutates state directly
function myReducer(state, action) {
  state.on = !state.on;  // Mutation!
  return state;           // Same reference -- React does not re-render
}

// CORRECT -- return a new object
function myReducer(state, action) {
  return { ...state, on: !state.on };
}
```

### Mistake 4: Overcomplicating Simple Cases

```jsx
// OVER-ENGINEERED -- a state reducer for a simple disabled toggle
function useToggle({ disabled, ...rest }) {
  // Just use a prop!
  return useToggle({
    ...rest,
    reducer: (state, action) => {
      if (disabled) return state;
      return toggleReducer(state, action);
    },
  });
}

// SIMPLER -- just check the prop
function useToggle({ initialOn = false, disabled = false } = {}) {
  const [on, setOn] = useState(initialOn);
  const toggle = () => { if (!disabled) setOn(prev => !prev); };
  return { on, toggle };
}
```

Use the state reducer pattern for *open-ended* customization, not for specific, predictable features.

---

## Best Practices

1. **Export the default reducer** so consumers can delegate to it for actions they do not want to customize.

2. **Export action type constants** so consumers reference stable identifiers rather than magic strings.

3. **Pass proposed changes** to the consumer's reducer so they can see what would happen and selectively override.

4. **Keep the action types stable** -- they are your public API. Changing them is a breaking change.

5. **Document each action type** with what it does by default, so consumers know what they are overriding.

6. **Make the reducer optional** -- the hook should work with sensible defaults when no custom reducer is provided.

7. **Do not mix state reducer with too many config props** -- if you have a state reducer, let it handle behavioral customization rather than adding more boolean props.

---

## Quick Summary

The state reducer pattern lets consumers customize how a component's state transitions work by providing their own reducer function. The component defines the actions; the consumer controls the responses. This gives maximum flexibility without the component needing to anticipate every possible use case. The consumer's reducer can accept defaults, reject changes, or modify transitions -- achieving true inversion of control over component behavior.

---

## Key Points

- The state reducer pattern accepts a custom reducer from the consumer
- The component provides default behavior; the consumer overrides what they need
- Always export the default reducer and action types so consumers can build on top of defaults
- Passing proposed `changes` to the consumer's reducer lets them selectively override
- This is inversion of control applied to state transitions
- Use this for reusable hooks/components with unpredictable customization needs
- Do not use it for simple, predictable customization -- props are simpler
- Libraries like Downshift pioneered this pattern in the React ecosystem

---

## Practice Questions

1. Explain the difference between adding a `disabled` prop to `useToggle` versus using the state reducer pattern to prevent toggling. When would you choose each approach?

2. Why is it important to export both the default reducer and the action type constants? What happens if a consumer does not have access to them?

3. What does "inversion of control" mean in the context of the state reducer pattern? How does it differ from inversion of control in render props?

4. A consumer's reducer always returns `action.changes` without modification. Is this any different from not providing a custom reducer at all? Explain.

5. You are building a `useForm` hook. What action types would you define, and how would the state reducer pattern let consumers customize form behavior?

---

## Exercises

### Exercise 1: useToggle with Confirmation

Build a `useToggle` hook using the state reducer pattern. Then create a consumer that:
- Allows toggling ON freely
- Requires `window.confirm()` before toggling OFF
- Tracks the total number of toggles in the state

### Exercise 2: useCounter with Boundaries

Build a `useCounter` hook with `INCREMENT`, `DECREMENT`, and `RESET` actions. Export the default reducer and action types. Then:
1. Create a consumer that prevents the counter from going below 0
2. Create a consumer that limits the counter to a maximum of 10
3. Create a consumer that increments by 5 instead of 1

### Exercise 3: useAccordion with Custom Rules

Build a `useAccordion` hook that manages which panels are open/closed, with actions like `TOGGLE_PANEL`, `OPEN_PANEL`, `CLOSE_PANEL`, `OPEN_ALL`, `CLOSE_ALL`. Then use the state reducer pattern to create:
1. An accordion where at most one panel can be open at a time
2. An accordion where the first panel can never be closed
3. An accordion with a "lock" feature that prevents any changes when locked

---

## What Is Next?

The state reducer pattern lets consumers customize *how* state changes, but it still allows any state value. What if certain states should be impossible? What if going from "loading" to "success" requires passing through a specific transition, and jumping directly from "idle" to "error" is never valid? In Chapter 23, you will learn the State Machine pattern -- a way to define exactly which states exist and which transitions are allowed, eliminating entire categories of impossible bugs.
