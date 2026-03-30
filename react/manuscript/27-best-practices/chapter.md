# Chapter 27: React Best Practices and Common Mistakes

## Learning Goals

By the end of this chapter, you will be able to:

- Apply proven component design principles that keep code maintainable
- Avoid the most common React mistakes that cause bugs and performance problems
- Write clean, readable JSX that other developers can understand quickly
- Manage state effectively using the right tool for each situation
- Handle side effects safely without introducing memory leaks or race conditions
- Structure hooks and components for maximum reusability
- Recognize and fix anti-patterns before they become problems
- Follow conventions that scale from small projects to large codebases

---

## Why Best Practices Matter

Every concept in this book has been taught in isolation — hooks, state, effects, routing, and more. But real applications combine all of them, and that is where things get messy. A component that works in a tutorial might cause subtle bugs in production. Code that is easy to write today might be impossible to maintain in six months.

Best practices are not arbitrary rules. They are lessons learned from real projects, real bugs, and real production incidents. Following them does not make your code perfect, but it does make it predictable, debuggable, and maintainable.

This chapter collects the most important guidelines into one place. Some you have seen in earlier chapters. Others are new. Together, they form a practical reference you can return to throughout your career.

---

## Component Design Principles

### Keep Components Small and Focused

A component should do one thing well. If you find yourself scrolling through a component, it is too big.

```jsx
// Bad — this component does too much
function UserDashboard() {
  const [user, setUser] = useState(null);
  const [orders, setOrders] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [activeTab, setActiveTab] = useState('orders');
  const [isEditing, setIsEditing] = useState(false);
  // ... 15 more state variables, 10 handler functions, 200 lines of JSX
}

// Good — broken into focused pieces
function UserDashboard() {
  const [activeTab, setActiveTab] = useState('orders');

  return (
    <div className="dashboard">
      <UserHeader />
      <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />
      {activeTab === 'orders' && <OrderHistory />}
      {activeTab === 'profile' && <ProfileEditor />}
      {activeTab === 'notifications' && <NotificationList />}
    </div>
  );
}
```

**The 100-line guideline:** If a component exceeds roughly 100-150 lines (including JSX), consider splitting it. This is not a hard rule — some complex components legitimately need more lines — but it is a useful signal.

### Separate Logic from Presentation

Components that mix data fetching, state management, and rendering are hard to test and reuse. Extract logic into custom hooks:

```jsx
// Bad — logic and rendering mixed together
function ProductList() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortBy, setSortBy] = useState('name');
  const [filterCategory, setFilterCategory] = useState('all');

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    fetch(`/api/products?sort=${sortBy}&category=${filterCategory}`, {
      signal: controller.signal,
    })
      .then(res => res.json())
      .then(data => {
        setProducts(data);
        setLoading(false);
      })
      .catch(err => {
        if (err.name !== 'AbortError') {
          setError(err.message);
          setLoading(false);
        }
      });
    return () => controller.abort();
  }, [sortBy, filterCategory]);

  if (loading) return <Spinner />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div>
      <SortControls value={sortBy} onChange={setSortBy} />
      <CategoryFilter value={filterCategory} onChange={setFilterCategory} />
      <div className="product-grid">
        {products.map(p => <ProductCard key={p.id} product={p} />)}
      </div>
    </div>
  );
}

// Good — logic extracted to a hook
function useProducts(sortBy, filterCategory) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);

    fetch(`/api/products?sort=${sortBy}&category=${filterCategory}`, {
      signal: controller.signal,
    })
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(data => {
        setProducts(data);
        setLoading(false);
      })
      .catch(err => {
        if (err.name !== 'AbortError') {
          setError(err.message);
          setLoading(false);
        }
      });

    return () => controller.abort();
  }, [sortBy, filterCategory]);

  return { products, loading, error };
}

function ProductList() {
  const [sortBy, setSortBy] = useState('name');
  const [filterCategory, setFilterCategory] = useState('all');
  const { products, loading, error } = useProducts(sortBy, filterCategory);

  if (loading) return <Spinner />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div>
      <SortControls value={sortBy} onChange={setSortBy} />
      <CategoryFilter value={filterCategory} onChange={setFilterCategory} />
      <div className="product-grid">
        {products.map(p => <ProductCard key={p.id} product={p} />)}
      </div>
    </div>
  );
}
```

The hook can now be tested independently, reused in other components, and the component itself is pure rendering logic.

### Design Components for Composition

Build components that work together like building blocks, not monoliths:

```jsx
// Bad — rigid, one-size-fits-all component
function Card({ title, subtitle, image, body, footer, onClick, variant }) {
  return (
    <div className={`card card-${variant}`} onClick={onClick}>
      {image && <img src={image} alt="" className="card-image" />}
      <div className="card-header">
        <h3>{title}</h3>
        {subtitle && <p>{subtitle}</p>}
      </div>
      <div className="card-body">{body}</div>
      {footer && <div className="card-footer">{footer}</div>}
    </div>
  );
}

// Good — composable parts
function Card({ children, className = '', ...props }) {
  return (
    <div className={`card ${className}`} {...props}>
      {children}
    </div>
  );
}

function CardHeader({ children }) {
  return <div className="card-header">{children}</div>;
}

function CardBody({ children }) {
  return <div className="card-body">{children}</div>;
}

function CardFooter({ children }) {
  return <div className="card-footer">{children}</div>;
}

// Usage — flexible and clear
function ProductCard({ product }) {
  return (
    <Card>
      <img src={product.image} alt={product.name} />
      <CardHeader>
        <h3>{product.name}</h3>
        <span className="price">${product.price}</span>
      </CardHeader>
      <CardBody>
        <p>{product.description}</p>
      </CardBody>
      <CardFooter>
        <button>Add to Cart</button>
      </CardFooter>
    </Card>
  );
}
```

### Use Sensible Defaults

Components should work with minimal configuration. Required props should be few:

```jsx
// Bad — too many required props for basic usage
<Button
  type="button"
  variant="primary"
  size="medium"
  disabled={false}
  loading={false}
  fullWidth={false}
  onClick={handleClick}
>
  Save
</Button>

// Good — sensible defaults, only pass what differs
function Button({
  children,
  variant = 'primary',
  size = 'medium',
  type = 'button',
  disabled = false,
  loading = false,
  fullWidth = false,
  onClick,
  ...props
}) {
  return (
    <button
      type={type}
      disabled={disabled || loading}
      className={`btn btn-${variant} btn-${size} ${fullWidth ? 'btn-full' : ''}`}
      onClick={onClick}
      {...props}
    >
      {loading ? <Spinner size="small" /> : children}
    </button>
  );
}

// Now basic usage is simple
<Button onClick={handleClick}>Save</Button>
<Button variant="danger" onClick={handleDelete}>Delete</Button>
<Button loading>Saving...</Button>
```

### Avoid Prop Drilling Beyond Two Levels

If you are passing a prop through three or more components that do not use it, that is prop drilling. Use Context or restructure your component tree:

```jsx
// Bad — prop drilling
function App() {
  const [user, setUser] = useState(null);
  return <Layout user={user} />;
}

function Layout({ user }) {
  return <Sidebar user={user} />;  // Layout doesn't use user
}

function Sidebar({ user }) {
  return <UserMenu user={user} />;  // Sidebar doesn't use user
}

function UserMenu({ user }) {
  return <span>{user?.name}</span>;  // Only UserMenu needs user
}

// Good — use Context for deeply shared state
function App() {
  return (
    <AuthProvider>
      <Layout />
    </AuthProvider>
  );
}

function Layout() {
  return <Sidebar />;
}

function Sidebar() {
  return <UserMenu />;
}

function UserMenu() {
  const { user } = useAuth();  // Access directly where needed
  return <span>{user?.name}</span>;
}
```

---

## State Management Rules

### Choose the Right State Location

Not all state belongs in the same place. Here is a decision framework:

| Question | Answer | Location |
|----------|--------|----------|
| Is it used by only one component? | Yes | Local `useState` |
| Is it shared by a parent and its children? | Yes | Lift to parent |
| Is it used by many unrelated components? | Yes | Context or state library |
| Does it come from a URL? | Yes | URL search params / route params |
| Does it come from a server? | Yes | Server state (TanStack Query, SWR) |
| Is it complex with many transitions? | Yes | `useReducer` |

### Keep State as Close as Possible

Do not hoist state higher than necessary:

```jsx
// Bad — state lives too high
function App() {
  const [searchQuery, setSearchQuery] = useState('');
  // searchQuery is only used in SearchPage, not anywhere else

  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route
        path="/search"
        element={<SearchPage query={searchQuery} setQuery={setSearchQuery} />}
      />
      <Route path="/about" element={<AboutPage />} />
    </Routes>
  );
}

// Good — state lives where it's used
function SearchPage() {
  const [searchQuery, setSearchQuery] = useState('');
  // ...
}
```

### Derive State Instead of Syncing State

If you can calculate a value from existing state, do not store it as separate state:

```jsx
// Bad — duplicated state that must stay in sync
function ShoppingCart({ items }) {
  const [total, setTotal] = useState(0);
  const [itemCount, setItemCount] = useState(0);

  useEffect(() => {
    setTotal(items.reduce((sum, item) => sum + item.price * item.quantity, 0));
    setItemCount(items.reduce((sum, item) => sum + item.quantity, 0));
  }, [items]);

  return (
    <div>
      <p>{itemCount} items</p>
      <p>Total: ${total.toFixed(2)}</p>
    </div>
  );
}

// Good — derive values during render
function ShoppingCart({ items }) {
  const total = items.reduce(
    (sum, item) => sum + item.price * item.quantity, 0
  );
  const itemCount = items.reduce(
    (sum, item) => sum + item.quantity, 0
  );

  return (
    <div>
      <p>{itemCount} items</p>
      <p>Total: ${total.toFixed(2)}</p>
    </div>
  );
}
```

The derived approach is simpler, has no timing issues, and cannot get out of sync.

### Never Mutate State Directly

React detects state changes by reference comparison. Mutating objects or arrays directly means React will not re-render:

```jsx
// Bad — mutating state directly
function TodoList() {
  const [todos, setTodos] = useState([]);

  function addTodo(text) {
    todos.push({ id: Date.now(), text, done: false });  // Mutation!
    setTodos(todos);  // Same reference — React ignores this
  }

  function toggleTodo(id) {
    const todo = todos.find(t => t.id === id);
    todo.done = !todo.done;  // Mutation!
    setTodos([...todos]);    // Spread doesn't fix the mutated object
  }

  // ...
}

// Good — create new references
function TodoList() {
  const [todos, setTodos] = useState([]);

  function addTodo(text) {
    setTodos(prev => [
      ...prev,
      { id: Date.now(), text, done: false },
    ]);
  }

  function toggleTodo(id) {
    setTodos(prev =>
      prev.map(todo =>
        todo.id === id ? { ...todo, done: !todo.done } : todo
      )
    );
  }

  // ...
}
```

### Use Functional Updates When New State Depends on Previous State

```jsx
// Bad — may use stale state
function Counter() {
  const [count, setCount] = useState(0);

  function incrementThree() {
    setCount(count + 1);  // All three use the same stale `count`
    setCount(count + 1);
    setCount(count + 1);
    // Result: count increases by 1, not 3
  }
}

// Good — functional update always uses latest state
function Counter() {
  const [count, setCount] = useState(0);

  function incrementThree() {
    setCount(prev => prev + 1);
    setCount(prev => prev + 1);
    setCount(prev => prev + 1);
    // Result: count increases by 3
  }
}
```

### Use useReducer for Complex State Logic

When state updates involve multiple related values or complex transitions, `useReducer` is clearer than multiple `useState` calls:

```jsx
// Bad — related state spread across multiple useState calls
function FormWizard() {
  const [step, setStep] = useState(0);
  const [formData, setFormData] = useState({});
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isComplete, setIsComplete] = useState(false);

  function nextStep() {
    const stepErrors = validateStep(step, formData);
    if (Object.keys(stepErrors).length > 0) {
      setErrors(stepErrors);
      return;
    }
    setErrors({});
    setStep(prev => prev + 1);
  }

  async function submit() {
    setIsSubmitting(true);
    setErrors({});
    try {
      await saveForm(formData);
      setIsComplete(true);
    } catch (err) {
      setErrors({ submit: err.message });
    } finally {
      setIsSubmitting(false);
    }
  }
  // State transitions are scattered and hard to follow
}

// Good — useReducer makes state transitions explicit
function formReducer(state, action) {
  switch (action.type) {
    case 'SET_FIELD':
      return {
        ...state,
        formData: { ...state.formData, [action.field]: action.value },
        errors: { ...state.errors, [action.field]: undefined },
      };
    case 'NEXT_STEP':
      return { ...state, step: state.step + 1, errors: {} };
    case 'PREV_STEP':
      return { ...state, step: state.step - 1 };
    case 'VALIDATION_ERROR':
      return { ...state, errors: action.errors };
    case 'SUBMIT_START':
      return { ...state, isSubmitting: true, errors: {} };
    case 'SUBMIT_SUCCESS':
      return { ...state, isSubmitting: false, isComplete: true };
    case 'SUBMIT_ERROR':
      return {
        ...state,
        isSubmitting: false,
        errors: { submit: action.error },
      };
    default:
      return state;
  }
}

function FormWizard() {
  const [state, dispatch] = useReducer(formReducer, {
    step: 0,
    formData: {},
    errors: {},
    isSubmitting: false,
    isComplete: false,
  });

  // Every state transition is now a clear, testable action
}
```

---

## useEffect Best Practices

Effects are the most error-prone part of React. Most bugs in React applications involve effects.

### Every Effect Needs a Clear Purpose

An effect should do exactly one thing. If your effect has multiple unrelated responsibilities, split it:

```jsx
// Bad — one effect doing two unrelated things
useEffect(() => {
  document.title = `${user.name}'s Profile`;

  const controller = new AbortController();
  fetch(`/api/users/${user.id}/activity`, { signal: controller.signal })
    .then(res => res.json())
    .then(setActivity);

  return () => controller.abort();
}, [user.id, user.name]);

// Good — separate effects for separate concerns
useEffect(() => {
  document.title = `${user.name}'s Profile`;
}, [user.name]);

useEffect(() => {
  const controller = new AbortController();
  fetch(`/api/users/${user.id}/activity`, { signal: controller.signal })
    .then(res => res.json())
    .then(setActivity);

  return () => controller.abort();
}, [user.id]);
```

### Always Clean Up

If your effect creates a subscription, timer, or async operation, clean it up:

```jsx
// Bad — no cleanup
useEffect(() => {
  const interval = setInterval(() => {
    setTime(Date.now());
  }, 1000);
  // Interval runs forever, even after component unmounts
}, []);

// Good — proper cleanup
useEffect(() => {
  const interval = setInterval(() => {
    setTime(Date.now());
  }, 1000);

  return () => clearInterval(interval);
}, []);
```

```jsx
// Bad — no abort for async operations
useEffect(() => {
  fetch(`/api/users/${userId}`)
    .then(res => res.json())
    .then(setUser);
  // If userId changes quickly, responses arrive out of order
}, [userId]);

// Good — abort controller prevents race conditions
useEffect(() => {
  const controller = new AbortController();

  fetch(`/api/users/${userId}`, { signal: controller.signal })
    .then(res => res.json())
    .then(setUser)
    .catch(err => {
      if (err.name !== 'AbortError') {
        setError(err.message);
      }
    });

  return () => controller.abort();
}, [userId]);
```

### Do Not Lie About Dependencies

Include every value from the component scope that the effect uses. Never suppress the exhaustive-deps lint rule without a good reason:

```jsx
// Bad — missing dependency
useEffect(() => {
  fetchData(userId);  // userId is used but not in deps
}, []);  // This only runs on mount, not when userId changes

// Bad — suppressing the lint rule
useEffect(() => {
  fetchData(userId);
  // eslint-disable-next-line react-hooks/exhaustive-deps
}, []);  // Hiding a real bug with a comment

// Good — all dependencies listed
useEffect(() => {
  fetchData(userId);
}, [userId]);
```

### Avoid Effects for State Synchronization

If you are using an effect to update state based on other state or props, you probably do not need an effect:

```jsx
// Bad — unnecessary effect for derived state
function FilteredList({ items, query }) {
  const [filtered, setFiltered] = useState(items);

  useEffect(() => {
    setFiltered(items.filter(item =>
      item.name.toLowerCase().includes(query.toLowerCase())
    ));
  }, [items, query]);

  return <List items={filtered} />;
}

// Good — calculate during render
function FilteredList({ items, query }) {
  const filtered = items.filter(item =>
    item.name.toLowerCase().includes(query.toLowerCase())
  );

  return <List items={filtered} />;
}
```

```jsx
// Bad — effect to sync state with props
function UserForm({ user }) {
  const [name, setName] = useState(user.name);

  useEffect(() => {
    setName(user.name);
  }, [user.name]);

  // ...
}

// Good — use a key to reset the form when the user changes
function UserProfile({ userId }) {
  return <UserForm key={userId} user={users[userId]} />;
}

function UserForm({ user }) {
  const [name, setName] = useState(user.name);
  // Form resets naturally when key changes
}
```

### Know When You Do Not Need an Effect

React's documentation emphasizes that effects are an "escape hatch." Many things that beginners put in effects should be handled differently:

| Task | Wrong (useEffect) | Right |
|------|-------------------|-------|
| Compute derived data | Effect that updates state | Calculate during render |
| Respond to user action | Effect watching a flag | Event handler |
| Initialize on mount only | Effect with API call | Effect (this one is correct) |
| Reset state when prop changes | Effect setting state | Use a `key` prop |
| Transform data from props | Effect → setState | Calculate during render |
| Send analytics on click | Effect watching state | Event handler |

---

## Performance Guidelines

### Do Not Optimize Prematurely

React is fast by default. Do not add `React.memo`, `useMemo`, or `useCallback` everywhere "just in case":

```jsx
// Bad — unnecessary memoization everywhere
const UserCard = React.memo(function UserCard({ name, email }) {
  const displayName = useMemo(() => name.toUpperCase(), [name]);
  const handleClick = useCallback(() => {
    console.log(`Clicked ${name}`);
  }, [name]);

  return (
    <div onClick={handleClick}>
      <h3>{displayName}</h3>
      <p>{email}</p>
    </div>
  );
});

// Good — simple component, no memoization needed
function UserCard({ name, email }) {
  return (
    <div onClick={() => console.log(`Clicked ${name}`)}>
      <h3>{name.toUpperCase()}</h3>
      <p>{email}</p>
    </div>
  );
}
```

### When to Optimize

Add optimization when you observe a real performance problem:

1. **`React.memo`** — when a component re-renders frequently but its props rarely change (verified with React DevTools Profiler)

2. **`useMemo`** — when a calculation is genuinely expensive (sorting/filtering thousands of items, complex transformations)

3. **`useCallback`** — when passing a function to a memoized child component, or as a dependency of another hook

```jsx
// Justified useMemo — expensive calculation with large dataset
function AnalyticsDashboard({ transactions }) {
  const summary = useMemo(() => {
    // Processing 100,000+ transactions
    return transactions.reduce((acc, t) => {
      acc.total += t.amount;
      acc.byCategory[t.category] = (acc.byCategory[t.category] || 0) + t.amount;
      acc.byMonth[t.month] = (acc.byMonth[t.month] || 0) + t.amount;
      return acc;
    }, { total: 0, byCategory: {}, byMonth: {} });
  }, [transactions]);

  return <Charts data={summary} />;
}
```

### Use Keys Correctly in Lists

Keys help React identify which items changed, were added, or were removed:

```jsx
// Bad — using index as key
{items.map((item, index) => (
  <ListItem key={index} item={item} />
))}
// If items are reordered, React reuses the wrong DOM nodes

// Bad — generating random keys
{items.map(item => (
  <ListItem key={Math.random()} item={item} />
))}
// Every render creates new keys, destroying all DOM state

// Good — stable, unique identifier
{items.map(item => (
  <ListItem key={item.id} item={item} />
))}
```

Index keys are acceptable **only** when: the list is static (never reordered, filtered, or modified), items have no state, and you have no unique ID.

### Avoid Creating Objects and Functions in JSX

New objects and arrays created in JSX break `React.memo` and effect dependencies:

```jsx
// Bad — new object created every render
<MapComponent center={{ lat: 40.7, lng: -74.0 }} />

// Bad — new array created every render
<Select options={['small', 'medium', 'large']} />

// Good — stable references
const CENTER = { lat: 40.7, lng: -74.0 };
const SIZE_OPTIONS = ['small', 'medium', 'large'];

function MyComponent() {
  return (
    <>
      <MapComponent center={CENTER} />
      <Select options={SIZE_OPTIONS} />
    </>
  );
}
```

For dynamic values, use `useMemo`:

```jsx
function MyComponent({ lat, lng }) {
  const center = useMemo(() => ({ lat, lng }), [lat, lng]);
  return <MapComponent center={center} />;
}
```

---

## JSX Best Practices

### Keep JSX Readable

Complex conditional rendering should be extracted:

```jsx
// Bad — deeply nested ternaries
function UserStatus({ user }) {
  return (
    <div>
      {user ? (
        user.isAdmin ? (
          user.isSuspended ? (
            <SuspendedAdminBanner user={user} />
          ) : (
            <AdminDashboard user={user} />
          )
        ) : user.isVerified ? (
          <UserDashboard user={user} />
        ) : (
          <VerificationPrompt user={user} />
        )
      ) : (
        <LoginPrompt />
      )}
    </div>
  );
}

// Good — extract into clear logic
function UserStatus({ user }) {
  if (!user) return <LoginPrompt />;
  if (user.isAdmin && user.isSuspended) return <SuspendedAdminBanner user={user} />;
  if (user.isAdmin) return <AdminDashboard user={user} />;
  if (!user.isVerified) return <VerificationPrompt user={user} />;
  return <UserDashboard user={user} />;
}
```

### Use Fragments to Avoid Unnecessary Divs

```jsx
// Bad — wrapper div that serves no purpose
function UserInfo({ user }) {
  return (
    <div>
      <h2>{user.name}</h2>
      <p>{user.email}</p>
    </div>
  );
}

// Good — fragment avoids extra DOM node
function UserInfo({ user }) {
  return (
    <>
      <h2>{user.name}</h2>
      <p>{user.email}</p>
    </>
  );
}
```

Use a `div` or `section` when you need it for styling or semantics. Use a fragment when you just need to group elements.

### Handle Empty States and Loading States

Never assume data exists. Always handle loading, error, and empty states:

```jsx
// Bad — crashes if products is undefined or empty
function ProductList({ products }) {
  return (
    <div>
      {products.map(p => <ProductCard key={p.id} product={p} />)}
    </div>
  );
}

// Good — handles all states
function ProductList({ products, loading, error }) {
  if (loading) {
    return <Spinner />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  if (!products || products.length === 0) {
    return (
      <EmptyState
        title="No products found"
        description="Try adjusting your search or filters."
      />
    );
  }

  return (
    <div className="product-grid">
      {products.map(p => <ProductCard key={p.id} product={p} />)}
    </div>
  );
}
```

### Spread Props Carefully

Spreading props is convenient but can pass unintended attributes to DOM elements:

```jsx
// Bad — spreading unknown props to a div
function Card({ title, ...props }) {
  return <div {...props}>{title}</div>;
  // If someone passes onClick, className, style — that's fine
  // But what about isActive, onDataLoad? Those become invalid HTML attributes
}

// Good — separate HTML props from custom props
function Card({ title, isActive, onDataLoad, className = '', ...htmlProps }) {
  return (
    <div
      className={`card ${isActive ? 'active' : ''} ${className}`}
      {...htmlProps}
    >
      {title}
    </div>
  );
}
```

---

## Event Handler Best Practices

### Name Handlers Consistently

Use the `handle` prefix for functions and `on` prefix for props:

```jsx
// Convention: handler functions start with "handle"
function SearchForm() {
  function handleSubmit(e) {
    e.preventDefault();
    // ...
  }

  function handleInputChange(e) {
    // ...
  }

  return (
    <form onSubmit={handleSubmit}>
      <input onChange={handleInputChange} />
    </form>
  );
}

// Convention: callback props start with "on"
function SearchForm({ onSearch }) {
  function handleSubmit(e) {
    e.preventDefault();
    onSearch(query);
  }
  // ...
}
```

### Avoid Inline Functions in Loops

Defining functions inside a loop creates a new function per iteration on every render:

```jsx
// Bad — new function per item per render
function TodoList({ todos, onToggle }) {
  return (
    <ul>
      {todos.map(todo => (
        <li key={todo.id}>
          <button onClick={() => onToggle(todo.id)}>
            {todo.text}
          </button>
        </li>
      ))}
    </ul>
  );
}
```

For simple cases like above, this is actually fine — the performance cost is negligible. But if the list is large and the child component is expensive, extract a component:

```jsx
// Better for large lists with expensive children
function TodoItem({ todo, onToggle }) {
  return (
    <li>
      <button onClick={() => onToggle(todo.id)}>
        {todo.text}
      </button>
    </li>
  );
}

const MemoizedTodoItem = React.memo(TodoItem);

function TodoList({ todos, onToggle }) {
  const handleToggle = useCallback((id) => {
    onToggle(id);
  }, [onToggle]);

  return (
    <ul>
      {todos.map(todo => (
        <MemoizedTodoItem key={todo.id} todo={todo} onToggle={handleToggle} />
      ))}
    </ul>
  );
}
```

### Prevent Default and Stop Propagation Explicitly

```jsx
// Good — clear about preventing default behavior
function LoginForm({ onLogin }) {
  function handleSubmit(e) {
    e.preventDefault();  // Prevent form from reloading the page
    onLogin({ username, password });
  }

  return <form onSubmit={handleSubmit}>...</form>;
}

// Good — stopping propagation when needed
function DropdownItem({ onClick }) {
  function handleClick(e) {
    e.stopPropagation();  // Prevent dropdown from closing
    onClick();
  }

  return <button onClick={handleClick}>...</button>;
}
```

---

## Custom Hook Guidelines

### Name Hooks Descriptively

The name should tell you what the hook provides:

```jsx
// Bad — vague names
function useData() { ... }
function useStuff() { ... }
function useFetch() { ... }  // Fetch what?

// Good — specific names
function useProducts(category) { ... }
function useWindowSize() { ... }
function useDebounce(value, delay) { ... }
function useLocalStorage(key, initialValue) { ... }
```

### Return Consistent Shapes

Hooks should return consistent, predictable shapes:

```jsx
// Bad — inconsistent return types
function useUser(id) {
  // Sometimes returns an object, sometimes an array
  if (loading) return null;
  return [user, error];
}

// Good — always returns the same shape
function useUser(id) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // ... fetch logic

  return { user, loading, error };
}
```

### Do Not Mix Levels of Abstraction

A hook should work at one level of abstraction:

```jsx
// Bad — mixing API calls with UI logic
function useSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);  // UI concern!

  useEffect(() => {
    fetch(`/api/search?q=${query}`).then(/* ... */);
  }, [query]);

  return { query, setQuery, results, isDropdownOpen, setIsDropdownOpen };
}

// Good — separate data from UI
function useSearch(query) {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!query) { setResults([]); return; }
    // ... fetch logic
  }, [query]);

  return { results, loading };
}

// UI state stays in the component
function SearchDropdown() {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const debouncedQuery = useDebounce(query, 300);
  const { results, loading } = useSearch(debouncedQuery);

  // ...
}
```

### Compose Hooks from Smaller Hooks

Build complex hooks by composing simpler ones:

```jsx
function usePaginatedProducts(category) {
  const [page, setPage] = useState(1);
  const debouncedCategory = useDebounce(category, 300);

  const { data, loading, error } = useFetch(
    `/api/products?category=${debouncedCategory}&page=${page}`
  );

  const nextPage = useCallback(() => setPage(p => p + 1), []);
  const prevPage = useCallback(() => setPage(p => Math.max(1, p - 1)), []);

  // Reset to page 1 when category changes
  useEffect(() => {
    setPage(1);
  }, [debouncedCategory]);

  return {
    products: data?.products ?? [],
    totalPages: data?.totalPages ?? 0,
    page,
    loading,
    error,
    nextPage,
    prevPage,
  };
}
```

---

## Error Handling Best Practices

### Use Error Boundaries at Multiple Levels

Do not rely on a single top-level error boundary. Place them strategically:

```jsx
function App() {
  return (
    <ErrorBoundary fallback={<FullPageError />}>
      <Header />
      <main>
        <ErrorBoundary fallback={<SectionError />}>
          <Routes>
            <Route path="/" element={
              <ErrorBoundary fallback={<WidgetError name="Dashboard" />}>
                <Dashboard />
              </ErrorBoundary>
            } />
          </Routes>
        </ErrorBoundary>
      </main>
      <Footer />
    </ErrorBoundary>
  );
}
```

This way, a crash in the Dashboard does not take down the entire application.

### Handle Async Errors Properly

Never ignore errors from async operations:

```jsx
// Bad — swallowing errors
async function handleSave() {
  try {
    await saveData(formData);
    showSuccess('Saved!');
  } catch {
    // Error silently ignored — user has no idea what happened
  }
}

// Good — always inform the user
async function handleSave() {
  try {
    await saveData(formData);
    showSuccess('Saved!');
  } catch (err) {
    showError(err.message || 'Failed to save. Please try again.');
    console.error('Save failed:', err);
  }
}
```

### Provide Actionable Error Messages

Users need to know what happened and what they can do about it:

```jsx
// Bad — generic error
function ErrorMessage() {
  return <p>Something went wrong.</p>;
}

// Good — specific and actionable
function ErrorMessage({ error, onRetry }) {
  return (
    <div className="error-container" role="alert">
      <h3>Unable to load products</h3>
      <p>{error.message}</p>
      {onRetry && (
        <button onClick={onRetry}>Try Again</button>
      )}
    </div>
  );
}
```

---

## Form Best Practices

### Always Use Controlled Components for Complex Forms

```jsx
// Good — controlled component
function ContactForm() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: '',
  });

  function handleChange(e) {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    // formData contains all current values
    submitForm(formData);
  }

  return (
    <form onSubmit={handleSubmit}>
      <input name="name" value={formData.name} onChange={handleChange} />
      <input name="email" value={formData.email} onChange={handleChange} />
      <textarea name="message" value={formData.message} onChange={handleChange} />
      <button type="submit">Send</button>
    </form>
  );
}
```

### Validate on Submit, Show Errors on Blur

Do not validate while the user is typing — it is annoying. Validate when they leave a field or submit:

```jsx
function SignupForm() {
  const [values, setValues] = useState({ email: '', password: '' });
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});

  function validate(field, value) {
    switch (field) {
      case 'email':
        if (!value) return 'Email is required';
        if (!/\S+@\S+\.\S+/.test(value)) return 'Invalid email';
        return '';
      case 'password':
        if (!value) return 'Password is required';
        if (value.length < 8) return 'Password must be at least 8 characters';
        return '';
      default:
        return '';
    }
  }

  function handleBlur(e) {
    const { name, value } = e.target;
    setTouched(prev => ({ ...prev, [name]: true }));
    setErrors(prev => ({ ...prev, [name]: validate(name, value) }));
  }

  function handleSubmit(e) {
    e.preventDefault();

    // Validate all fields on submit
    const newErrors = {};
    Object.keys(values).forEach(field => {
      const error = validate(field, values[field]);
      if (error) newErrors[field] = error;
    });

    setErrors(newErrors);
    setTouched({ email: true, password: true });

    if (Object.keys(newErrors).length === 0) {
      submitForm(values);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          name="email"
          value={values.email}
          onChange={handleChange}
          onBlur={handleBlur}
          aria-invalid={touched.email && errors.email ? 'true' : undefined}
          aria-describedby={errors.email ? 'email-error' : undefined}
        />
        {touched.email && errors.email && (
          <p id="email-error" className="error">{errors.email}</p>
        )}
      </div>
      {/* ... */}
    </form>
  );
}
```

### Disable Submit Buttons During Submission

Prevent double submissions:

```jsx
function OrderForm({ onSubmit }) {
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    if (submitting) return;  // Extra safety

    setSubmitting(true);
    try {
      await onSubmit(formData);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {/* ... fields ... */}
      <button type="submit" disabled={submitting}>
        {submitting ? 'Placing Order...' : 'Place Order'}
      </button>
    </form>
  );
}
```

---

## Accessibility Habits

Accessibility is not an afterthought. These habits should be automatic:

### Use Semantic HTML

```jsx
// Bad — div soup
<div class="nav">
  <div class="nav-item" onClick={...}>Home</div>
  <div class="nav-item" onClick={...}>About</div>
</div>

// Good — semantic elements
<nav>
  <a href="/">Home</a>
  <a href="/about">About</a>
</nav>
```

### Always Label Form Inputs

```jsx
// Bad — no label
<input type="email" placeholder="Email" />

// Good — proper label association
<label htmlFor="email">Email</label>
<input id="email" type="email" />

// Also good — wrapping label
<label>
  Email
  <input type="email" />
</label>
```

### Use `button` for Actions, `a` for Navigation

```jsx
// Bad — using the wrong element
<a href="#" onClick={handleDelete}>Delete</a>
<div onClick={handleSubmit} className="button">Submit</div>

// Good — correct elements
<button onClick={handleDelete}>Delete</button>
<a href="/products">View Products</a>
```

### Provide Alt Text for Images

```jsx
// Meaningful image — describe the content
<img src={product.image} alt="Red running shoes, side view" />

// Decorative image — empty alt
<img src={decorativeBorder} alt="" />

// Icon with text — icon is decorative
<button>
  <SearchIcon aria-hidden="true" />
  Search
</button>

// Icon-only button — needs a label
<button aria-label="Close dialog">
  <CloseIcon aria-hidden="true" />
</button>
```

---

## Code Organization Habits

### Group Related Code Together

Within a component file, organize code in a consistent order:

```jsx
function ProductPage() {
  // 1. Hooks — router, context, state
  const { id } = useParams();
  const { user } = useAuth();
  const [quantity, setQuantity] = useState(1);

  // 2. Derived values
  const { product, loading, error } = useProduct(id);
  const isInStock = product?.stock > 0;
  const totalPrice = product ? product.price * quantity : 0;

  // 3. Effects
  useEffect(() => {
    document.title = product?.name ?? 'Loading...';
  }, [product?.name]);

  // 4. Event handlers
  function handleAddToCart() {
    addToCart(product.id, quantity);
  }

  function handleQuantityChange(e) {
    setQuantity(Number(e.target.value));
  }

  // 5. Early returns (loading, error, empty states)
  if (loading) return <Spinner />;
  if (error) return <ErrorMessage message={error} />;
  if (!product) return <NotFound />;

  // 6. Main render
  return (
    <div className="product-page">
      {/* ... */}
    </div>
  );
}
```

### One Component Per File

Do not put multiple exported components in one file. Helper components that are only used internally are fine:

```jsx
// Bad — multiple exported components
// ProductComponents.jsx
export function ProductCard() { ... }
export function ProductList() { ... }
export function ProductDetail() { ... }

// Good — one per file
// ProductCard.jsx
export function ProductCard() { ... }

// ProductList.jsx
export function ProductList() { ... }

// OK — internal helper in the same file
// ProductCard.jsx
function PriceBadge({ price, salePrice }) {
  // Small helper only used by ProductCard
  return <span>{salePrice ? salePrice : price}</span>;
}

export function ProductCard({ product }) {
  return (
    <div>
      <PriceBadge price={product.price} salePrice={product.salePrice} />
      {/* ... */}
    </div>
  );
}
```

### Keep Imports Organized

Group imports by category:

```jsx
// 1. React and framework imports
import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';

// 2. Third-party libraries
import clsx from 'clsx';

// 3. Internal absolute imports (features, shared)
import { useAuth } from '@features/auth';
import { Button, Spinner } from '@shared/components';
import { formatCurrency } from '@shared/utils';

// 4. Relative imports
import { ProductCard } from './ProductCard';
import styles from './ProductList.module.css';
```

---

## Testing Habits

### Test Behavior, Not Implementation

```jsx
// Bad — testing implementation details
test('sets isLoading state to true', () => {
  const { result } = renderHook(() => useProducts());
  expect(result.current.loading).toBe(true);
});

// Good — testing user-visible behavior
test('shows loading spinner while fetching products', () => {
  render(<ProductList />);
  expect(screen.getByRole('status')).toBeInTheDocument();
});

test('displays products after loading', async () => {
  render(<ProductList />);
  expect(await screen.findByText('Running Shoes')).toBeInTheDocument();
});
```

### Use the Right Query

React Testing Library provides queries in a priority order:

1. **`getByRole`** — accessible name (best for most elements)
2. **`getByLabelText`** — form inputs
3. **`getByPlaceholderText`** — when no label exists
4. **`getByText`** — non-interactive content
5. **`getByTestId`** — last resort

```jsx
// Preferred — queries by role
const submitButton = screen.getByRole('button', { name: /submit/i });
const emailInput = screen.getByRole('textbox', { name: /email/i });
const nav = screen.getByRole('navigation');

// Last resort — test ID
const complexWidget = screen.getByTestId('chart-container');
```

### Write Fewer, More Meaningful Tests

```jsx
// Bad — too many trivial tests
test('renders the component', () => { ... });
test('has a title', () => { ... });
test('has a submit button', () => { ... });
test('submit button has text "Submit"', () => { ... });

// Good — test meaningful user flows
test('submits the form with valid data', async () => {
  const onSubmit = vi.fn();
  render(<ContactForm onSubmit={onSubmit} />);

  await userEvent.type(screen.getByLabelText(/name/i), 'Jane');
  await userEvent.type(screen.getByLabelText(/email/i), 'jane@test.com');
  await userEvent.type(screen.getByLabelText(/message/i), 'Hello');
  await userEvent.click(screen.getByRole('button', { name: /send/i }));

  expect(onSubmit).toHaveBeenCalledWith({
    name: 'Jane',
    email: 'jane@test.com',
    message: 'Hello',
  });
});

test('shows validation errors for empty required fields', async () => {
  render(<ContactForm onSubmit={vi.fn()} />);

  await userEvent.click(screen.getByRole('button', { name: /send/i }));

  expect(screen.getByText(/name is required/i)).toBeInTheDocument();
  expect(screen.getByText(/email is required/i)).toBeInTheDocument();
});
```

---

## Security Best Practices

### Never Use `dangerouslySetInnerHTML` with User Input

```jsx
// DANGEROUS — XSS vulnerability
function Comment({ comment }) {
  return <div dangerouslySetInnerHTML={{ __html: comment.body }} />;
}

// Safe — React escapes text content by default
function Comment({ comment }) {
  return <div>{comment.body}</div>;
}

// If you must render HTML, sanitize it first
import DOMPurify from 'dompurify';

function Comment({ comment }) {
  const sanitized = DOMPurify.sanitize(comment.body);
  return <div dangerouslySetInnerHTML={{ __html: sanitized }} />;
}
```

### Validate and Sanitize All User Inputs

```jsx
function SearchPage() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';

  // Don't trust URL parameters — validate them
  const sanitizedQuery = query.slice(0, 200).trim();

  // Don't interpolate into dangerous contexts
  // Bad: eval(query), element.innerHTML = query
  // Good: use as React text content
  return <SearchResults query={sanitizedQuery} />;
}
```

### Store Tokens Securely

```jsx
// OK for most apps — localStorage
localStorage.setItem('token', token);

// Better for sensitive apps — httpOnly cookies (set by server)
// The token is never accessible to JavaScript

// Bad — storing in global variable or React state only
// Token is lost on page refresh
window.authToken = token;  // Don't do this
```

---

## The Complete Anti-Pattern Checklist

Here is a quick reference of patterns to avoid:

| Anti-Pattern | Why It Is Bad | What to Do Instead |
|-------------|--------------|-------------------|
| Mutating state directly | React does not detect the change | Create new objects/arrays |
| Using index as key (dynamic lists) | Causes incorrect renders on reorder | Use stable, unique IDs |
| Missing useEffect cleanup | Memory leaks, race conditions | Return a cleanup function |
| Lying about effect dependencies | Stale data, missed updates | List all dependencies honestly |
| useEffect for derived state | Extra renders, sync issues | Calculate during render |
| Prop drilling 3+ levels | Fragile, verbose code | Use Context or composition |
| Giant components | Hard to understand and test | Split into smaller pieces |
| Premature optimization | Added complexity without benefit | Optimize when measured |
| `dangerouslySetInnerHTML` with user data | XSS vulnerability | Sanitize or use text content |
| Ignoring async errors | Silent failures | Always catch and display errors |
| No loading or error states | Broken UI, confused users | Handle all states explicitly |
| Inline object/array props | Breaks memoization | Extract to constants or useMemo |
| No form validation | Bad data, poor UX | Validate on blur and submit |
| Missing alt text | Inaccessible to screen readers | Provide meaningful alt or `alt=""` |
| Console.log in production | Exposes internals, clutter | Remove or use a logging library |

---

## Summary

Best practices in React come down to a few core principles:

**Simplicity.** Choose the simplest solution that works. Do not add abstractions, optimizations, or libraries until you need them. Start with `useState` before reaching for `useReducer`. Start with prop passing before adding Context. Start without memoization and add it when profiling shows a problem.

**Clarity.** Write code that explains itself. Name components after what they render. Name hooks after what they provide. Name handlers after what they handle. Organize files so related code lives together.

**Correctness.** Handle all states — loading, error, empty, and success. Clean up effects. Validate user input. Never mutate state. Include all effect dependencies. Use the right key for lists.

**Separation.** Keep UI separate from logic. Keep features separate from each other. Keep shared code in shared directories. Keep pages thin. One component per file, one responsibility per hook.

These are not rules to memorize. They are habits to build. The more you practice them, the more natural they become, and the fewer bugs you will write.

---

## Interview Questions

1. **What are the most important principles for writing maintainable React components?**

   *Keep components small and focused — each should do one thing. Separate logic from presentation by extracting business logic into custom hooks. Design components for composition using children and slots rather than building monolithic components with many props. Use sensible defaults so components work with minimal configuration. Handle all states (loading, error, empty) explicitly.*

2. **When should you use `useMemo` and `useCallback`, and when should you avoid them?**

   *Use `useMemo` when a calculation is genuinely expensive — like processing thousands of items. Use `useCallback` when passing functions to memoized child components or when the function is a dependency of another hook. Avoid them for simple calculations, small component trees, or when you have not measured an actual performance problem. Every `useMemo` and `useCallback` adds memory overhead and code complexity, so the optimization should be justified by real performance data from the React DevTools Profiler.*

3. **What are the most common mistakes developers make with `useEffect`?**

   *Five common mistakes: (1) Missing cleanup — not aborting fetch requests or clearing timers leads to memory leaks and race conditions. (2) Missing dependencies — not listing all values from the component scope that the effect uses, causing stale data. (3) Using effects for derived state — computing values that could be calculated during render. (4) Using effects to sync state with props — this should be handled with a key prop or during render. (5) Combining unrelated logic in one effect — each effect should have a single responsibility.*

4. **How do you decide where to put state in a React application?**

   *Start with the principle of locality: state should live as close to where it is used as possible. If only one component needs it, use local useState. If a parent and its children share it, lift it to the parent. If many unrelated components need it, use Context or a state management library. Server data belongs in a server state solution like TanStack Query. URL-derived state belongs in search params or route params. Complex state with many transitions benefits from useReducer.*

5. **What is the difference between derived state and synchronized state? Why does it matter?**

   *Derived state is calculated from existing state during render — like filtering a list or computing a total. Synchronized state is when you use useEffect to update one piece of state whenever another changes. Derived state is always consistent because it is computed fresh each render. Synchronized state can become inconsistent because the update happens asynchronously in an effect, causing an extra render and a brief moment where the states are out of sync. Always prefer deriving state during render over synchronizing state in effects.*

6. **What accessibility practices should be automatic for every React developer?**

   *Use semantic HTML elements (nav, main, article, button) instead of styled divs. Always associate labels with form inputs using htmlFor or wrapping. Use button for actions and anchor tags for navigation. Provide meaningful alt text for images (or empty alt for decorative ones). Ensure all interactive elements are keyboard accessible. Use ARIA attributes when semantic HTML is not sufficient. Test with keyboard-only navigation and a screen reader.*

7. **How do you handle errors effectively in a React application?**

   *Use error boundaries at multiple levels — a top-level boundary for catastrophic failures, route-level boundaries so one page crash does not affect others, and section-level boundaries for independent widgets. For async operations, always catch errors in try/catch blocks and display user-friendly messages with a retry option. Never silently swallow errors. Log errors to a monitoring service in production. Provide actionable error messages that tell users what happened and what they can do.*

---

## Practice Exercises

### Exercise 1: Refactor a Messy Component

Take this bloated component and refactor it following the best practices from this chapter:

```jsx
function UserDashboard() {
  const [user, setUser] = useState(null);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('orders');
  const [editingProfile, setEditingProfile] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    fetch('/api/user')
      .then(r => r.json())
      .then(data => {
        setUser(data);
        setName(data.name);
        setEmail(data.email);
        setLoading(false);
      });
    fetch('/api/orders')
      .then(r => r.json())
      .then(setOrders);
    fetch('/api/notifications')
      .then(r => r.json())
      .then(data => {
        setNotifications(data);
        setUnreadCount(data.filter(n => !n.read).length);
      });
  }, []);

  // ... imagine 200 more lines of handlers and JSX
}
```

Your refactored version should:
- Extract data fetching into custom hooks
- Split into smaller components
- Derive unread count instead of storing it
- Handle loading and error states
- Clean up effects properly

### Exercise 2: Fix the Anti-Patterns

Find and fix all the anti-patterns in this code:

```jsx
function TodoApp() {
  const [todos, setTodos] = useState([]);
  const [filter, setFilter] = useState('all');
  const [filteredTodos, setFilteredTodos] = useState([]);
  const [todoCount, setTodoCount] = useState(0);

  useEffect(() => {
    if (filter === 'all') {
      setFilteredTodos(todos);
    } else if (filter === 'active') {
      setFilteredTodos(todos.filter(t => !t.done));
    } else {
      setFilteredTodos(todos.filter(t => t.done));
    }
    setTodoCount(todos.length);
  }, [todos, filter]);

  function addTodo(text) {
    todos.push({ id: Math.random(), text, done: false });
    setTodos(todos);
  }

  function toggleTodo(id) {
    const todo = todos.find(t => t.id === id);
    todo.done = !todo.done;
    setTodos([...todos]);
  }

  return (
    <div>
      <h1>Todos ({todoCount})</h1>
      <input onKeyDown={(e) => {
        if (e.key === 'Enter') addTodo(e.target.value);
      }} />
      <div>
        <a href="#" onClick={() => setFilter('all')}>All</a>
        <a href="#" onClick={() => setFilter('active')}>Active</a>
        <a href="#" onClick={() => setFilter('done')}>Done</a>
      </div>
      {filteredTodos.map((todo, index) => (
        <div key={index} onClick={() => toggleTodo(todo.id)}>
          {todo.done ? '✓' : '○'} {todo.text}
        </div>
      ))}
    </div>
  );
}
```

Issues to find and fix: state mutation, unnecessary effect for derived state, index keys, using anchors instead of buttons, Math.random for IDs, missing input clearing.

### Exercise 3: Build a Component with All Best Practices

Build a `CommentSection` component that follows every best practice from this chapter:

- Custom hook for fetching and adding comments (`useComments`)
- Separate presentation and container components
- Proper loading, error, and empty states
- Form with validation (on blur and submit)
- Optimistic updates when adding a comment
- Error recovery with retry
- Accessible markup (labels, ARIA, keyboard navigation)
- Consistent naming conventions
- Clean, organized code structure

### Exercise 4: Performance Audit

Create a deliberately unoptimized component and then fix it:

1. Build a `SearchableProductList` with 1000 items
2. Add a search input that filters items
3. Include a sort dropdown
4. Measure render performance with React DevTools Profiler
5. Identify unnecessary re-renders
6. Apply targeted optimizations (memo, useMemo, useCallback)
7. Measure again and document the improvement

### Exercise 5: Code Review Checklist

Create a code review checklist based on this chapter. For each item, include:

- The check (what to look for)
- Why it matters
- A bad example and a good example

Cover at least 15 items across: component design, state management, effects, performance, accessibility, error handling, and code organization. Use this checklist on a past project to identify areas for improvement.

---

## What Is Next?

In Chapter 28, we will explore **Interview Preparation** — a comprehensive guide to React interview questions covering all difficulty levels, from fundamental concepts to advanced patterns. We will cover behavioral questions, coding challenges, system design questions, and strategies for demonstrating your React expertise in technical interviews.
