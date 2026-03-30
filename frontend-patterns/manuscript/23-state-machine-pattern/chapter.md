# Chapter 23: The State Machine Pattern

## What You Will Learn

- What finite state machines are and why they prevent impossible states
- How "boolean soup" creates bugs and how state machines eliminate them
- How to implement state machines with `useReducer`
- How to model multi-step flows (forms, wizards, checkout processes)
- An introduction to XState for complex state machines
- How to visualize and reason about your application's states

## Why This Chapter Matters

Consider a data-fetching component. You might model its state with three booleans:

```jsx
const [isLoading, setIsLoading] = useState(false);
const [isError, setIsError] = useState(false);
const [isSuccess, setIsSuccess] = useState(false);
```

Three booleans means eight possible combinations. But how many are *valid*? Only four:

- Idle: `loading=false, error=false, success=false`
- Loading: `loading=true, error=false, success=false`
- Error: `loading=false, error=true, success=false`
- Success: `loading=false, error=false, success=true`

The other four combinations (like `loading=true, error=true, success=true`) should be impossible, but your code allows them. If you forget to set `isLoading` to `false` before setting `isError` to `true`, you end up in an invalid state: loading and errored at the same time. The UI shows a spinner and an error message simultaneously.

State machines solve this by making impossible states *unrepresentable*. Instead of multiple booleans, you have one state variable that can only hold valid values, and explicit transitions that define which state can follow which.

This is not just theory. Every multi-step form, every authentication flow, every media player, and every checkout process is a state machine -- whether you model it as one or not. When you do not model it explicitly, you get bugs. When you do, you get clarity.

---

## The Problem: Boolean Soup

"Boolean soup" is what happens when you model complex state with multiple independent boolean flags:

```jsx
function DataFetcher({ url }) {
  const [isIdle, setIsIdle] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [isError, setIsError] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setIsIdle(false);
    setIsLoading(true);
    setIsError(false);   // Did I forget any?
    setIsSuccess(false); // What if I miss one?

    try {
      const response = await fetch(url);
      const result = await response.json();
      setData(result);
      setIsLoading(false);  // Must remember to set this
      setIsSuccess(true);
    } catch (err) {
      setError(err);
      setIsLoading(false);  // Must remember here too
      setIsError(true);
    }
  };

  // Which combination of booleans is active RIGHT NOW?
  // Can you be sure isLoading and isError are never both true?
}
```

Each `setState` call is a separate update. If you forget one, you have an invalid state. If React batches updates differently than you expect, you might see a flash of an invalid combination.

```
Boolean soup: 2^4 = 16 possible combinations
Valid states: only 4

+----------+----------+----------+----------+--------+
| isIdle   | isLoading| isError  | isSuccess| Valid? |
+----------+----------+----------+----------+--------+
| true     | false    | false    | false    | YES    |
| false    | true     | false    | false    | YES    |
| false    | false    | true     | false    | YES    |
| false    | false    | false    | true     | YES    |
| true     | true     | false    | false    | NO     |
| false    | true     | true     | false    | NO     |
| false    | true     | false    | true     | NO     |
| ... 9 more invalid combinations ...        | NO     |
+----------+----------+----------+----------+--------+
```

---

## The Solution: Finite State Machines

A finite state machine has:

1. **A finite set of states** -- the valid states your system can be in
2. **An initial state** -- where the system starts
3. **Events (actions)** -- things that happen that might cause a transition
4. **Transitions** -- rules that say "when in state X and event Y happens, move to state Z"

```jsx
// State machine approach: ONE variable, only valid values
function DataFetcher({ url }) {
  const [state, setState] = useState('idle');
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setState('loading');  // ONE update, always valid

    try {
      const result = await fetch(url).then(r => r.json());
      setData(result);
      setState('success');  // ONE update, always valid
    } catch (err) {
      setError(err);
      setState('error');  // ONE update, always valid
    }
  };

  // The state is ALWAYS one of: 'idle', 'loading', 'success', 'error'
  // No invalid combinations possible
}
```

```
State machine: only 4 valid states, explicit transitions

  +--------+     FETCH      +-----------+
  |  idle  | -------------> |  loading  |
  +--------+                +-----------+
                              /         \
                    SUCCESS  /           \  FAILURE
                            v             v
                    +-----------+   +-----------+
                    |  success  |   |   error   |
                    +-----------+   +-----------+
                            \             /
                     FETCH   \           /  FETCH
                              v         v
                            +-----------+
                            |  loading  |
                            +-----------+
```

---

## Implementing State Machines with useReducer

`useReducer` is a natural fit for state machines because the reducer function maps directly to the transition table.

### Basic Fetch State Machine

```jsx
function fetchReducer(state, event) {
  switch (state.status) {
    case 'idle':
      switch (event.type) {
        case 'FETCH':
          return { status: 'loading', data: null, error: null };
        default:
          return state; // Ignore events that do not apply in this state
      }

    case 'loading':
      switch (event.type) {
        case 'SUCCESS':
          return { status: 'success', data: event.data, error: null };
        case 'FAILURE':
          return { status: 'error', data: null, error: event.error };
        default:
          return state;
      }

    case 'success':
      switch (event.type) {
        case 'FETCH':
          return { status: 'loading', data: null, error: null };
        default:
          return state;
      }

    case 'error':
      switch (event.type) {
        case 'FETCH':
          return { status: 'loading', data: null, error: null };
        default:
          return state;
      }

    default:
      throw new Error(`Unknown state: ${state.status}`);
  }
}

function useFetch(url) {
  const [state, send] = useReducer(fetchReducer, {
    status: 'idle',
    data: null,
    error: null,
  });

  const fetchData = async () => {
    send({ type: 'FETCH' });
    try {
      const response = await fetch(url);
      const data = await response.json();
      send({ type: 'SUCCESS', data });
    } catch (error) {
      send({ type: 'FAILURE', error });
    }
  };

  return { ...state, fetchData };
}

// Usage
function UserProfile({ userId }) {
  const { status, data, error, fetchData } = useFetch(`/api/users/${userId}`);

  useEffect(() => {
    fetchData();
  }, [userId]);

  switch (status) {
    case 'idle':
      return <p>Ready to fetch</p>;
    case 'loading':
      return <Spinner />;
    case 'success':
      return <h1>{data.name}</h1>;
    case 'error':
      return (
        <div>
          <p>Error: {error.message}</p>
          <button onClick={fetchData}>Retry</button>
        </div>
      );
  }
}
```

Notice how the switch on `status` in the render covers exactly four cases. There are no impossible states to worry about.

### Key Insight: Events Are Ignored in Wrong States

This is one of the most powerful features. If you dispatch `SUCCESS` while in the `idle` state, nothing happens -- the reducer returns the current state unchanged. No crash, no invalid state, just a graceful no-op.

```jsx
// In boolean soup, this causes a bug:
setIsSuccess(true);  // Oops, forgot to check if we are loading

// In a state machine, this is harmless:
send({ type: 'SUCCESS', data });
// If we are in 'idle', the reducer ignores this event
```

---

## Modeling State Machines as Data

Instead of a large switch statement, you can represent the machine as a configuration object:

```jsx
const fetchMachine = {
  initial: 'idle',
  states: {
    idle: {
      on: {
        FETCH: 'loading',
      },
    },
    loading: {
      on: {
        SUCCESS: 'success',
        FAILURE: 'error',
      },
    },
    success: {
      on: {
        FETCH: 'loading',
      },
    },
    error: {
      on: {
        FETCH: 'loading',
      },
    },
  },
};

// Generic reducer that works with any machine config
function createMachineReducer(machine) {
  return function reducer(state, event) {
    const currentState = machine.states[state.status];
    const nextStatus = currentState?.on?.[event.type];

    if (!nextStatus) {
      return state; // Event not handled in this state
    }

    return {
      ...state,
      status: nextStatus,
      ...(event.data !== undefined && { data: event.data }),
      ...(event.error !== undefined && { error: event.error }),
    };
  };
}

// Usage
function useFetch(url) {
  const [state, send] = useReducer(
    createMachineReducer(fetchMachine),
    { status: fetchMachine.initial, data: null, error: null }
  );

  // ...same as before
}
```

This data-driven approach is easy to visualize, test, and modify. Adding a new state or transition is a one-line change in the config.

---

## Real-World Example: Multi-Step Form

Multi-step forms are classic state machines. Each step is a state, and navigation between steps is a transition.

```
+-------+   NEXT   +----------+   NEXT   +---------+   SUBMIT   +---------+
| step1 | -------> |  step2   | -------> |  step3  | ---------> | submitting|
+-------+          +----------+          +---------+            +---------+
                     |                      |                     |      |
                     | BACK                 | BACK         SUCCESS|      |FAILURE
                     v                      v                     v      v
                   +-------+             +----------+     +--------+ +-------+
                   | step1 |             |  step2   |     |complete| | error |
                   +-------+             +----------+     +--------+ +-------+
                                                                       |
                                                                       | RETRY
                                                                       v
                                                                  +---------+
                                                                  |submitting|
                                                                  +---------+
```

```jsx
const formMachine = {
  initial: 'step1',
  states: {
    step1: {
      on: { NEXT: 'step2' },
    },
    step2: {
      on: { NEXT: 'step3', BACK: 'step1' },
    },
    step3: {
      on: { SUBMIT: 'submitting', BACK: 'step2' },
    },
    submitting: {
      on: { SUCCESS: 'complete', FAILURE: 'error' },
    },
    complete: {
      on: {}, // Terminal state -- no transitions out
    },
    error: {
      on: { RETRY: 'submitting', BACK: 'step3' },
    },
  },
};

function formReducer(state, event) {
  const currentStateConfig = formMachine.states[state.step];
  const nextStep = currentStateConfig?.on?.[event.type];

  if (!nextStep) return state;

  // Merge form data on NEXT transitions
  const formData =
    event.type === 'NEXT' || event.type === 'SUBMIT'
      ? { ...state.formData, ...event.data }
      : state.formData;

  return {
    ...state,
    step: nextStep,
    formData,
    error: event.error || null,
  };
}

function useMultiStepForm() {
  const [state, send] = useReducer(formReducer, {
    step: formMachine.initial,
    formData: {},
    error: null,
  });

  return {
    step: state.step,
    formData: state.formData,
    error: state.error,
    next: (data) => send({ type: 'NEXT', data }),
    back: () => send({ type: 'BACK' }),
    submit: (data) => send({ type: 'SUBMIT', data }),
    success: () => send({ type: 'SUCCESS' }),
    failure: (error) => send({ type: 'FAILURE', error }),
    retry: () => send({ type: 'RETRY' }),
  };
}
```

Usage:

```jsx
function CheckoutForm() {
  const { step, formData, error, next, back, submit, success, failure, retry } =
    useMultiStepForm();

  switch (step) {
    case 'step1':
      return (
        <ShippingForm
          defaultValues={formData}
          onNext={(data) => next(data)}
        />
      );

    case 'step2':
      return (
        <PaymentForm
          defaultValues={formData}
          onNext={(data) => next(data)}
          onBack={back}
        />
      );

    case 'step3':
      return (
        <ReviewForm
          formData={formData}
          onSubmit={() => {
            submit(formData);
            submitOrder(formData).then(success).catch(failure);
          }}
          onBack={back}
        />
      );

    case 'submitting':
      return <Spinner message="Placing your order..." />;

    case 'complete':
      return <SuccessMessage orderId={formData.orderId} />;

    case 'error':
      return (
        <div>
          <p>Something went wrong: {error?.message}</p>
          <button onClick={retry}>Try Again</button>
          <button onClick={back}>Go Back</button>
        </div>
      );
  }
}
```

Every step renders exactly one view. There is no ambiguity about what the user sees. Going back from step 3 always goes to step 2. Submitting is only possible from step 3. These rules are enforced by the machine, not by developer discipline.

---

## Introduction to XState

For complex state machines with nested states, parallel states, guards, and side effects, the XState library provides a complete solution.

### Why XState?

Our `useReducer` approach works well for simple machines, but it lacks:

- **Guards** -- conditions that must be true for a transition to happen
- **Actions** -- side effects that run on transitions
- **Nested states** -- sub-states within a state (e.g., "authenticated" has sub-states "idle" and "fetching")
- **Parallel states** -- multiple independent state machines running simultaneously
- **Visualization** -- XState has tools that generate diagrams from your machine definition

### Basic XState Example

```jsx
import { createMachine, assign } from 'xstate';
import { useMachine } from '@xstate/react';

const fetchMachine = createMachine({
  id: 'fetch',
  initial: 'idle',
  context: {
    data: null,
    error: null,
    retries: 0,
  },
  states: {
    idle: {
      on: {
        FETCH: 'loading',
      },
    },
    loading: {
      on: {
        SUCCESS: {
          target: 'success',
          actions: assign({ data: (_, event) => event.data }),
        },
        FAILURE: [
          {
            target: 'loading',
            guard: (context) => context.retries < 3,
            actions: assign({
              retries: (context) => context.retries + 1,
            }),
          },
          {
            target: 'error',
            actions: assign({ error: (_, event) => event.error }),
          },
        ],
      },
    },
    success: {
      on: {
        FETCH: {
          target: 'loading',
          actions: assign({ data: null, error: null, retries: 0 }),
        },
      },
    },
    error: {
      on: {
        RETRY: {
          target: 'loading',
          actions: assign({ error: null }),
        },
      },
    },
  },
});

function DataFetcher({ url }) {
  const [state, send] = useMachine(fetchMachine);

  useEffect(() => {
    if (state.matches('loading')) {
      fetch(url)
        .then(r => r.json())
        .then(data => send({ type: 'SUCCESS', data }))
        .catch(error => send({ type: 'FAILURE', error }));
    }
  }, [state, url, send]);

  if (state.matches('idle')) {
    return <button onClick={() => send({ type: 'FETCH' })}>Load</button>;
  }
  if (state.matches('loading')) {
    return <Spinner />;
  }
  if (state.matches('success')) {
    return <pre>{JSON.stringify(state.context.data, null, 2)}</pre>;
  }
  if (state.matches('error')) {
    return (
      <div>
        <p>Error: {state.context.error?.message}</p>
        <button onClick={() => send({ type: 'RETRY' })}>Retry</button>
      </div>
    );
  }
}
```

### Key XState Features

```
+---------------------------------------------+
|  Feature          | useReducer | XState     |
+---------------------------------------------+
|  Basic states     |    Yes     |   Yes      |
|  Transitions      |    Yes     |   Yes      |
|  Guards           |    Manual  |   Built-in |
|  Side effects     |    Manual  |   Built-in |
|  Nested states    |    Hard    |   Built-in |
|  Parallel states  |    Hard    |   Built-in |
|  Visualization    |    No      |   Yes      |
|  DevTools         |    No      |   Yes      |
|  Serializable     |    No      |   Yes      |
|  Bundle size      |    0 KB    |   ~15 KB   |
+---------------------------------------------+
```

### When to Use XState vs useReducer

- **useReducer**: simple machines with 3-6 states, no guards, no side effects. Good enough for most UI components.
- **XState**: complex workflows with 10+ states, conditional transitions, nested sub-states, or when you need visualization and DevTools. Good for checkout flows, authentication, multi-step wizards, and video players.

---

## Avoiding Boolean Soup: Before vs After

### Before (Boolean Soup)

```jsx
function MediaPlayer() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [isBuffering, setIsBuffering] = useState(false);
  const [isSeeking, setIsSeeking] = useState(false);
  const [hasEnded, setHasEnded] = useState(false);
  const [hasError, setHasError] = useState(false);

  const play = () => {
    setIsPlaying(true);
    setIsPaused(false);
    setHasEnded(false);
    setHasError(false);
    // Did I forget anything?
  };

  // What does the UI look like when isPlaying=true AND isBuffering=true?
  // What about isPlaying=true AND hasEnded=true?
  // How many combinations do I need to handle?
  // 2^6 = 64 possible combinations!
}
```

### After (State Machine)

```jsx
const playerMachine = {
  initial: 'idle',
  states: {
    idle:      { on: { PLAY: 'playing' } },
    playing:   { on: { PAUSE: 'paused', BUFFER: 'buffering', END: 'ended', ERROR: 'error' } },
    paused:    { on: { PLAY: 'playing', SEEK: 'seeking' } },
    buffering: { on: { LOADED: 'playing', ERROR: 'error' } },
    seeking:   { on: { SEEKED: 'playing', ERROR: 'error' } },
    ended:     { on: { PLAY: 'playing' } },
    error:     { on: { RETRY: 'idle' } },
  },
};

function MediaPlayer() {
  const [state, send] = useReducer(
    createMachineReducer(playerMachine),
    { status: 'idle' }
  );

  // Exactly 7 possible states. Each one is clear.
  switch (state.status) {
    case 'idle':      return <PlayButton onClick={() => send({ type: 'PLAY' })} />;
    case 'playing':   return <PauseButton onClick={() => send({ type: 'PAUSE' })} />;
    case 'paused':    return <PlayButton onClick={() => send({ type: 'PLAY' })} />;
    case 'buffering': return <Spinner />;
    case 'seeking':   return <SeekIndicator />;
    case 'ended':     return <ReplayButton onClick={() => send({ type: 'PLAY' })} />;
    case 'error':     return <RetryButton onClick={() => send({ type: 'RETRY' })} />;
  }
}
```

---

## When to Use / When NOT to Use

### Use State Machines When

- Your component has 3 or more distinct modes or steps
- You catch yourself using multiple booleans to track related states
- You need to prevent invalid state combinations
- The flow has clear sequential steps (wizard, checkout, onboarding)
- You want to visualize the entire flow for documentation or debugging
- Edge cases keep causing bugs because state transitions are not well-defined

### Do NOT Use State Machines When

- The state is truly independent booleans (isOpen and isFullscreen are genuinely independent)
- There are only two states (a simple boolean toggle is fine)
- The overhead of defining a machine exceeds the complexity of the problem
- The state changes do not have meaningful transitions -- it is just data that updates

---

## Common Mistakes

### Mistake 1: Using Booleans When You Have Modes

```jsx
// BAD -- these are mutually exclusive modes, not independent flags
const [isViewing, setIsViewing] = useState(true);
const [isEditing, setIsEditing] = useState(false);
const [isSaving, setIsSaving] = useState(false);

// GOOD -- one variable for the current mode
const [mode, setMode] = useState('viewing');
// mode is 'viewing' | 'editing' | 'saving'
```

### Mistake 2: Not Handling All States in the UI

```jsx
// BAD -- what if status is 'error'? Nothing renders.
function Display({ status, data }) {
  if (status === 'loading') return <Spinner />;
  if (status === 'success') return <Data data={data} />;
  // 'idle' and 'error' silently render nothing!
}

// GOOD -- explicit handling of every state
function Display({ status, data, error }) {
  switch (status) {
    case 'idle':    return <p>Click to load</p>;
    case 'loading': return <Spinner />;
    case 'success': return <Data data={data} />;
    case 'error':   return <Error error={error} />;
    default:
      throw new Error(`Unhandled status: ${status}`);
  }
}
```

### Mistake 3: Transitions That Skip States

```jsx
// BAD -- jumping directly to 'success' from 'idle' skips 'loading'
function reducer(state, event) {
  if (event.type === 'SUCCESS') {
    return { status: 'success', data: event.data };
    // This allows idle -> success, which should require loading first
  }
}

// GOOD -- check current state before transitioning
function reducer(state, event) {
  if (state.status === 'loading' && event.type === 'SUCCESS') {
    return { status: 'success', data: event.data };
  }
  // SUCCESS in 'idle' state does nothing
}
```

### Mistake 4: Trying to Set State Directly

```jsx
// BAD -- bypasses the state machine
const [state, send] = useReducer(reducer, initialState);
// Later:
state.status = 'error';  // Direct mutation! Bypasses transitions!

// GOOD -- always go through events
send({ type: 'FAILURE', error: new Error('timeout') });
```

---

## Best Practices

1. **Start by drawing the state diagram** on paper or a whiteboard before writing code. List all states, then draw arrows for transitions.

2. **Name states as nouns or adjectives**, not verbs: `'idle'`, `'loading'`, `'error'` -- not `'load'`, `'fail'`.

3. **Name events as verbs or past-tense**: `'FETCH'`, `'SUCCESS'`, `'FAILURE'` -- representing things that happen.

4. **Handle the default case** in your switch: throw an error for unknown states so bugs surface immediately.

5. **Use TypeScript** to enforce valid states and events at compile time.

6. **Ignore invalid events** rather than throwing -- return the current state unchanged. This makes the system robust.

7. **Start with useReducer** and only move to XState when you need guards, nested states, or visualization.

8. **Test the state machine independently** from the UI. Feed it events and assert the resulting states. This is much easier than testing with rendered components.

---

## Quick Summary

State machines model your system as a finite set of valid states with explicit transitions between them. Instead of multiple booleans that can combine into invalid states, you have one status variable that is always valid. `useReducer` is the natural tool for implementing state machines in React. For complex machines with guards, nested states, and side effects, XState provides a full-featured solution. The pattern eliminates entire categories of bugs by making impossible states unrepresentable.

---

## Key Points

- Boolean soup (multiple flags) creates exponentially more state combinations, most of which are invalid
- State machines restrict state to a finite set of valid values
- Transitions define which events are allowed in which states
- Invalid events in a state machine are silently ignored, preventing bugs
- `useReducer` is the simplest way to implement state machines in React
- Machine configurations as data objects are easier to understand and modify than large switch statements
- XState extends the concept with guards, actions, nested states, parallel states, and DevTools
- Use `useReducer` for simple machines (3-6 states), XState for complex ones (10+ states)
- Multi-step forms, authentication flows, media players, and checkout processes are all state machines
- Always draw the state diagram first -- it serves as both design and documentation

---

## Practice Questions

1. You have a component with `isLoading`, `isRetrying`, and `hasData` booleans. How many possible combinations exist? How many are valid? Rewrite the state as a state machine.

2. Explain why ignoring invalid events (returning current state) is better than throwing an error in a state machine reducer.

3. A multi-step form allows the user to navigate from step 3 directly to step 1. In a boolean approach (`currentStep` variable with free assignment), what bugs could this cause? How does a state machine prevent them?

4. Compare the `useReducer` state machine approach with XState. At what level of complexity would you switch from one to the other?

5. Draw a state diagram for a traffic light with states: `green`, `yellow`, `red`. What events trigger each transition? Is there a state that can transition to any other state, or are all transitions sequential?

---

## Exercises

### Exercise 1: Authentication State Machine

Model a user authentication flow as a state machine with these states:
- `loggedOut` -- user is not authenticated
- `loggingIn` -- credentials submitted, waiting for server
- `loggedIn` -- user is authenticated
- `loggingOut` -- logout request submitted
- `error` -- authentication failed

Define the transitions, implement it with `useReducer`, and build a simple login/logout UI that renders the correct view for each state.

### Exercise 2: Multi-Step Signup Wizard

Build a 4-step signup wizard as a state machine:
1. **Account** -- email and password
2. **Profile** -- name and avatar
3. **Preferences** -- notification settings
4. **Confirmation** -- review and submit

Requirements:
- Users can go forward and backward between steps 1-3
- Step 4 (confirmation) transitions to `submitting`, then `success` or `error`
- Collect and preserve form data across all steps
- Prevent skipping steps (e.g., cannot go from step 1 to step 3 directly)

### Exercise 3: Convert Boolean Soup to a State Machine

Take this boolean-soup component and refactor it into a state machine:

```jsx
function Upload() {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [isFailed, setIsFailed] = useState(false);
  const [progress, setProgress] = useState(0);

  // Refactor this into states: idle, selected, uploading, complete, failed
  // Define valid transitions between each state
}
```

Draw the state diagram, then implement it with `useReducer`. Verify that impossible states (like `isUploading=true` and `isComplete=true`) can no longer occur.

---

## What Is Next?

State machines give you control over your component's state transitions. But components do not exist in isolation -- in real applications, many components need to share and coordinate state. In Chapter 24, you will learn the Flux and Redux pattern, which applies the reducer concept at the application level, managing global state through a single store with predictable, traceable updates.
