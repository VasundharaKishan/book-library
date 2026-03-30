# Chapter 15: The Container/Presentational Pattern

## What You Will Learn

- What the Container/Presentational pattern is and what problem it solves
- How to separate data-fetching logic from rendering logic
- How container components fetch, transform, and manage state
- How presentational components focus purely on displaying data
- How React Hooks changed this pattern and when the separation is still valuable
- When to use this pattern and when it adds unnecessary complexity

## Why This Chapter Matters

Think about a restaurant. The kitchen prepares the food. The waiter presents it to you. These are two different roles with different responsibilities.

The kitchen (container) handles all the complex work: sourcing ingredients, cooking, managing orders, handling timing. The waiter (presentational) handles presentation: carrying the plate, describing the dish, refilling your water. Neither does the other's job.

Now imagine a restaurant where the waiter also cooks your food at your table. Chaotic, right? That is what happens when a React component both fetches data AND renders complex UI. It becomes hard to test, hard to reuse, and hard to understand.

The Container/Presentational pattern (also called Smart/Dumb components) splits components into two categories:
- **Container components** handle data, state, and logic
- **Presentational components** handle rendering and styling

This pattern was introduced by Dan Abramov (co-creator of Redux) in 2015. It became one of the most influential patterns in React. Years later, Dan himself updated his guidance, noting that Hooks can replace much of the need for this separation. This chapter covers both the original pattern and the modern perspective.

---

## The Problem

Components that mix data logic and rendering become messy, untestable, and unreusable.

```javascript
// This component does EVERYTHING:
function UserDashboard() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortBy, setSortBy] = useState("name");
  const [filterRole, setFilterRole] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    async function fetchUsers() {
      try {
        setLoading(true);
        const response = await fetch("/api/users");
        if (!response.ok) throw new Error("Failed to fetch");
        const data = await response.json();
        setUsers(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchUsers();
  }, []);

  const filteredUsers = users
    .filter((u) => filterRole === "all" || u.role === filterRole)
    .filter((u) =>
      u.name.toLowerCase().includes(searchQuery.toLowerCase())
    )
    .sort((a, b) => a[sortBy].localeCompare(b[sortBy]));

  if (loading) {
    return (
      <div className="dashboard">
        <div className="spinner-container">
          <div className="spinner" />
          <p>Loading users...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard">
        <div className="error-container">
          <h2>Something went wrong</h2>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Users ({filteredUsers.length})</h1>
        <input
          type="search"
          placeholder="Search users..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      <div className="dashboard-filters">
        <select
          value={filterRole}
          onChange={(e) => setFilterRole(e.target.value)}
        >
          <option value="all">All Roles</option>
          <option value="admin">Admin</option>
          <option value="editor">Editor</option>
          <option value="viewer">Viewer</option>
        </select>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
        >
          <option value="name">Sort by Name</option>
          <option value="email">Sort by Email</option>
          <option value="role">Sort by Role</option>
        </select>
      </div>

      <table className="user-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {filteredUsers.map((user) => (
            <tr key={user.id}>
              <td>{user.name}</td>
              <td>{user.email}</td>
              <td>
                <span className={`badge badge-${user.role}`}>
                  {user.role}
                </span>
              </td>
              <td>
                <button onClick={() => handleEdit(user.id)}>Edit</button>
                <button onClick={() => handleDelete(user.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

This 100+ line component:
- Fetches data from an API
- Manages loading and error states
- Filters, searches, and sorts data
- Renders the entire UI including loading and error states
- Cannot be reused with different data sources
- Cannot be tested without mocking the API
- Cannot be displayed in a design system (Storybook) without a running API

---

## The Solution: Container/Presentational Split

Split the monolith into two components:

```
+--------------------+         +----------------------+
| Container          |         | Presentational       |
| (UserDashboard     |  props  | (UserDashboard       |
|  Container)        | ------> |  View)               |
|                    |         |                      |
| - Fetches data     |         | - Receives data      |
| - Manages state    |         | - Renders UI         |
| - Handles errors   |         | - Handles styling    |
| - Transforms data  |         | - Calls callbacks    |
| - Business logic   |         | - No side effects    |
+--------------------+         +----------------------+
```

### Presentational Component

The presentational component receives all data through props and renders the UI. It has no side effects, no API calls, no state management (except UI state like "is dropdown open").

```javascript
// UserDashboardView.jsx -- Presentational

function UserDashboardView({
  users,
  loading,
  error,
  searchQuery,
  onSearchChange,
  filterRole,
  onFilterChange,
  sortBy,
  onSortChange,
  onEdit,
  onDelete,
  onRetry
}) {
  if (loading) {
    return (
      <div className="dashboard">
        <LoadingSpinner message="Loading users..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard">
        <ErrorMessage message={error} onRetry={onRetry} />
      </div>
    );
  }

  return (
    <div className="dashboard">
      <DashboardHeader
        count={users.length}
        searchQuery={searchQuery}
        onSearchChange={onSearchChange}
      />
      <DashboardFilters
        filterRole={filterRole}
        onFilterChange={onFilterChange}
        sortBy={sortBy}
        onSortChange={onSortChange}
      />
      <UserTable
        users={users}
        onEdit={onEdit}
        onDelete={onDelete}
      />
    </div>
  );
}

function DashboardHeader({ count, searchQuery, onSearchChange }) {
  return (
    <div className="dashboard-header">
      <h1>Users ({count})</h1>
      <input
        type="search"
        placeholder="Search users..."
        value={searchQuery}
        onChange={(e) => onSearchChange(e.target.value)}
      />
    </div>
  );
}

function DashboardFilters({ filterRole, onFilterChange, sortBy, onSortChange }) {
  return (
    <div className="dashboard-filters">
      <select value={filterRole} onChange={(e) => onFilterChange(e.target.value)}>
        <option value="all">All Roles</option>
        <option value="admin">Admin</option>
        <option value="editor">Editor</option>
        <option value="viewer">Viewer</option>
      </select>
      <select value={sortBy} onChange={(e) => onSortChange(e.target.value)}>
        <option value="name">Sort by Name</option>
        <option value="email">Sort by Email</option>
        <option value="role">Sort by Role</option>
      </select>
    </div>
  );
}

function UserTable({ users, onEdit, onDelete }) {
  return (
    <table className="user-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Email</th>
          <th>Role</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {users.map((user) => (
          <UserRow
            key={user.id}
            user={user}
            onEdit={onEdit}
            onDelete={onDelete}
          />
        ))}
      </tbody>
    </table>
  );
}

function UserRow({ user, onEdit, onDelete }) {
  return (
    <tr>
      <td>{user.name}</td>
      <td>{user.email}</td>
      <td>
        <span className={`badge badge-${user.role}`}>{user.role}</span>
      </td>
      <td>
        <button onClick={() => onEdit(user.id)}>Edit</button>
        <button onClick={() => onDelete(user.id)}>Delete</button>
      </td>
    </tr>
  );
}
```

### Container Component

The container component handles all logic and passes data down to the presentational component:

```javascript
// UserDashboardContainer.jsx -- Container

function UserDashboardContainer() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortBy, setSortBy] = useState("name");
  const [filterRole, setFilterRole] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");

  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch("/api/users");
      if (!response.ok) throw new Error("Failed to fetch users");
      const data = await response.json();
      setUsers(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  // Data transformation
  const processedUsers = useMemo(() => {
    return users
      .filter((u) => filterRole === "all" || u.role === filterRole)
      .filter((u) =>
        u.name.toLowerCase().includes(searchQuery.toLowerCase())
      )
      .sort((a, b) => {
        const aVal = a[sortBy] || "";
        const bVal = b[sortBy] || "";
        return aVal.localeCompare(bVal);
      });
  }, [users, filterRole, searchQuery, sortBy]);

  // Event handlers
  const handleEdit = useCallback((userId) => {
    // Navigate to edit page or open modal
    console.log("Edit user:", userId);
  }, []);

  const handleDelete = useCallback(async (userId) => {
    if (!window.confirm("Delete this user?")) return;
    try {
      await fetch(`/api/users/${userId}`, { method: "DELETE" });
      setUsers((prev) => prev.filter((u) => u.id !== userId));
    } catch (err) {
      setError("Failed to delete user");
    }
  }, []);

  // Pass everything to the presentational component
  return (
    <UserDashboardView
      users={processedUsers}
      loading={loading}
      error={error}
      searchQuery={searchQuery}
      onSearchChange={setSearchQuery}
      filterRole={filterRole}
      onFilterChange={setFilterRole}
      sortBy={sortBy}
      onSortChange={setSortBy}
      onEdit={handleEdit}
      onDelete={handleDelete}
      onRetry={fetchUsers}
    />
  );
}
```

---

## The Benefits

```
+-----------------------------------------------+
|  BENEFIT                 | HOW                 |
+-----------------------------------------------+
|                          |                     |
|  Reusability             | Presentational      |
|                          | component works     |
|                          | with any data       |
|                          | source              |
|                          |                     |
|  Testability             | Test UI without     |
|                          | API. Test logic     |
|                          | without rendering.  |
|                          |                     |
|  Storybook/Design System | Presentational      |
|                          | components work in  |
|                          | Storybook with      |
|                          | mock data           |
|                          |                     |
|  Team Collaboration      | Designer works on   |
|                          | presentational.     |
|                          | Backend dev works   |
|                          | on container.       |
|                          |                     |
|  Separation of Concerns  | Each file has one   |
|                          | job                 |
+-----------------------------------------------+
```

### Testing Becomes Easy

```javascript
// Testing the presentational component -- no API needed!
describe("UserDashboardView", () => {
  it("renders users in a table", () => {
    const users = [
      { id: 1, name: "Alice", email: "alice@test.com", role: "admin" },
      { id: 2, name: "Bob", email: "bob@test.com", role: "editor" }
    ];

    render(
      <UserDashboardView
        users={users}
        loading={false}
        error={null}
        searchQuery=""
        onSearchChange={jest.fn()}
        filterRole="all"
        onFilterChange={jest.fn()}
        sortBy="name"
        onSortChange={jest.fn()}
        onEdit={jest.fn()}
        onDelete={jest.fn()}
        onRetry={jest.fn()}
      />
    );

    expect(screen.getByText("Alice")).toBeInTheDocument();
    expect(screen.getByText("Bob")).toBeInTheDocument();
  });

  it("shows loading spinner when loading", () => {
    render(
      <UserDashboardView loading={true} users={[]} /* ... */ />
    );

    expect(screen.getByText("Loading users...")).toBeInTheDocument();
  });

  it("shows error message with retry button", () => {
    const onRetry = jest.fn();
    render(
      <UserDashboardView
        loading={false}
        error="Network error"
        users={[]}
        onRetry={onRetry}
        /* ... */
      />
    );

    expect(screen.getByText("Network error")).toBeInTheDocument();
    fireEvent.click(screen.getByText("Retry"));
    expect(onRetry).toHaveBeenCalled();
  });
});
```

### Reuse with Different Data Sources

```javascript
// Same presentational component, different data source!

// From REST API
function UserDashboardFromAPI() {
  const { users, loading, error } = useUsersAPI();
  return <UserDashboardView users={users} loading={loading} error={error} /* ... */ />;
}

// From GraphQL
function UserDashboardFromGraphQL() {
  const { data, loading, error } = useQuery(GET_USERS);
  return <UserDashboardView users={data?.users} loading={loading} error={error} /* ... */ />;
}

// From local state (Storybook, testing)
function UserDashboardStory() {
  return (
    <UserDashboardView
      users={mockUsers}
      loading={false}
      error={null}
      /* ... */
    />
  );
}
```

---

## How Hooks Changed This Pattern

In 2019, Dan Abramov updated his original article to say he no longer recommends splitting components into containers and presentational components as a strict rule. Why? Because **Hooks** can extract the logic without needing a separate container component.

### Before Hooks: Container Component Required

```javascript
// Container component exists just to provide data
function UserListContainer() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/users")
      .then((r) => r.json())
      .then((data) => {
        setUsers(data);
        setLoading(false);
      });
  }, []);

  return <UserList users={users} loading={loading} />;
}
```

### After Hooks: Custom Hook Replaces Container

```javascript
// Custom hook extracts the logic
function useUsers() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/api/users")
      .then((r) => r.json())
      .then(setUsers)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return { users, loading, error };
}

// Component uses the hook directly -- no container needed
function UserList() {
  const { users, loading, error } = useUsers();

  if (loading) return <Spinner />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

```
Evolution:

  2015: Container + Presentational (two components)

    UserListContainer --> UserList
         (data)            (UI)

  2019+: Hook + Component (one component + one hook)

    useUsers() hook --> UserList
       (data)            (UI + uses hook)

  The separation still exists,
  but it moved from components to hooks.
```

### When Hooks Are Enough

For simple cases, a custom hook is cleaner than a separate container:

```javascript
// Simple case -- hook is enough
function ProductCard({ productId }) {
  const { product, loading } = useProduct(productId);

  if (loading) return <CardSkeleton />;
  return (
    <div className="product-card">
      <img src={product.image} alt={product.name} />
      <h3>{product.name}</h3>
      <p>${product.price}</p>
    </div>
  );
}
```

### When You Still Want the Full Split

For complex cases, the container/presentational split is still valuable:

```javascript
// Complex case -- full split still helps
// When:
// 1. The presentational component is reused with different data sources
// 2. You need the component in Storybook without a real backend
// 3. The data logic is complex (filters, sorting, pagination, caching)
// 4. Different team members work on logic vs UI

function DataTable({ columns, rows, loading, error, onSort, onFilter, onPageChange }) {
  // This presentational component is used by:
  // - UserListContainer (fetches from /api/users)
  // - ProductListContainer (fetches from /api/products)
  // - OrderListContainer (fetches from /api/orders)
  // - Storybook stories (uses mock data)
  // - Tests (uses fixture data)
}
```

---

## The Modern Approach: Hooks + Presentational When Needed

The modern recommendation is:

1. **Start with hooks** to extract data logic
2. **Split into presentational only when you need reuse** across different data sources
3. **Do not split just because "the pattern says so"**

```javascript
// Step 1: Start simple with a hook
function useUserDashboard() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    role: "all",
    search: "",
    sortBy: "name"
  });

  useEffect(() => {
    fetchUsers().then(setUsers).finally(() => setLoading(false));
  }, []);

  const filteredUsers = useMemo(() => {
    return users
      .filter((u) => filters.role === "all" || u.role === filters.role)
      .filter((u) => u.name.toLowerCase().includes(filters.search.toLowerCase()))
      .sort((a, b) => a[filters.sortBy].localeCompare(b[filters.sortBy]));
  }, [users, filters]);

  return {
    users: filteredUsers,
    loading,
    error,
    filters,
    setFilters,
    refetch: () => fetchUsers().then(setUsers)
  };
}

// Step 2: Use the hook in your component
function UserDashboard() {
  const { users, loading, error, filters, setFilters, refetch } =
    useUserDashboard();

  // Render...
}

// Step 3: ONLY IF NEEDED -- extract a presentational component
// for Storybook, reuse, or testing purposes
```

---

## Identifying Container vs Presentational

Here is a quick reference:

```
+----------------------------+----------------------------+
| Container                  | Presentational             |
+----------------------------+----------------------------+
| Fetches data               | Receives data via props    |
| Manages state              | Minimal state (UI only)    |
| Calls APIs                 | Calls callbacks via props  |
| Handles side effects       | No side effects            |
| Often has no DOM markup    | Full of DOM/JSX            |
| Connects to stores/context | No store/context access    |
| Not reusable (specific)    | Highly reusable (generic)  |
| Tested with integration    | Tested with unit tests     |
+----------------------------+----------------------------+
```

### More Examples

```javascript
// CONTAINER: handles all the data logic
function CommentSectionContainer({ postId }) {
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newComment, setNewComment] = useState("");

  useEffect(() => {
    api.comments.getByPost(postId).then((data) => {
      setComments(data);
      setLoading(false);
    });
  }, [postId]);

  async function handleSubmit() {
    const comment = await api.comments.create(postId, {
      body: newComment
    });
    setComments((prev) => [...prev, comment]);
    setNewComment("");
  }

  async function handleDelete(commentId) {
    await api.comments.delete(commentId);
    setComments((prev) => prev.filter((c) => c.id !== commentId));
  }

  return (
    <CommentSection
      comments={comments}
      loading={loading}
      newComment={newComment}
      onNewCommentChange={setNewComment}
      onSubmit={handleSubmit}
      onDelete={handleDelete}
    />
  );
}

// PRESENTATIONAL: pure rendering
function CommentSection({
  comments,
  loading,
  newComment,
  onNewCommentChange,
  onSubmit,
  onDelete
}) {
  if (loading) return <Spinner />;

  return (
    <div className="comments">
      <h3>Comments ({comments.length})</h3>

      <div className="comment-list">
        {comments.map((comment) => (
          <Comment
            key={comment.id}
            comment={comment}
            onDelete={onDelete}
          />
        ))}
      </div>

      <div className="comment-form">
        <textarea
          value={newComment}
          onChange={(e) => onNewCommentChange(e.target.value)}
          placeholder="Write a comment..."
        />
        <button
          onClick={onSubmit}
          disabled={!newComment.trim()}
        >
          Post Comment
        </button>
      </div>
    </div>
  );
}

function Comment({ comment, onDelete }) {
  return (
    <div className="comment">
      <div className="comment-header">
        <strong>{comment.author.name}</strong>
        <span className="comment-date">
          {new Date(comment.createdAt).toLocaleDateString()}
        </span>
      </div>
      <p className="comment-body">{comment.body}</p>
      <button
        className="comment-delete"
        onClick={() => onDelete(comment.id)}
      >
        Delete
      </button>
    </div>
  );
}
```

---

## When to Use the Container/Presentational Pattern

```
+-----------------------------------------------+
|           USE THIS PATTERN WHEN:              |
+-----------------------------------------------+
|                                               |
|  * The presentational component is reused     |
|    across different data sources              |
|  * You need components in Storybook or a      |
|    design system without real backends        |
|  * The data logic is complex enough to        |
|    warrant isolation                          |
|  * Different team members handle data vs UI   |
|  * You want to test UI rendering separately   |
|    from data fetching                         |
|                                               |
+-----------------------------------------------+

+-----------------------------------------------+
|       DO NOT USE THIS PATTERN WHEN:           |
+-----------------------------------------------+
|                                               |
|  * A custom hook extracts the logic cleanly   |
|  * The component is simple and only used once |
|  * The split would create two trivial files   |
|    that are harder to navigate than one file  |
|  * You are splitting "just because" without   |
|    a concrete benefit                         |
|  * The presentational component would have    |
|    20+ props (too much prop passing)          |
|                                               |
+-----------------------------------------------+
```

---

## Common Mistakes

### Mistake 1: Splitting Too Early

```javascript
// WRONG -- premature split for a simple component
// UserNameContainer.jsx
function UserNameContainer({ userId }) {
  const user = useUser(userId);
  return <UserName name={user.name} />;
}

// UserName.jsx
function UserName({ name }) {
  return <span className="user-name">{name}</span>;
}

// CORRECT -- just use a hook, no split needed
function UserName({ userId }) {
  const user = useUser(userId);
  return <span className="user-name">{user.name}</span>;
}
```

### Mistake 2: Too Many Props

```javascript
// WRONG -- the presentational component has too many props
<UserDashboardView
  users={users}
  loading={loading}
  error={error}
  searchQuery={searchQuery}
  onSearchChange={onSearchChange}
  filterRole={filterRole}
  onFilterChange={onFilterChange}
  sortBy={sortBy}
  onSortChange={onSortChange}
  selectedUsers={selectedUsers}
  onSelectUser={onSelectUser}
  onSelectAll={onSelectAll}
  page={page}
  pageSize={pageSize}
  totalPages={totalPages}
  onPageChange={onPageChange}
  onPageSizeChange={onPageSizeChange}
  onEdit={onEdit}
  onDelete={onDelete}
  onExport={onExport}
  onRetry={onRetry}
/>

// BETTER -- group related props into objects
<UserDashboardView
  data={{ users, loading, error }}
  filters={{ searchQuery, filterRole, sortBy }}
  pagination={{ page, pageSize, totalPages }}
  selection={{ selectedUsers }}
  onFilterChange={handleFilterChange}
  onPageChange={handlePageChange}
  onSelectionChange={handleSelectionChange}
  actions={{ onEdit, onDelete, onExport, onRetry }}
/>
```

### Mistake 3: Presentational Components with Side Effects

```javascript
// WRONG -- presentational component fetches data
function UserCard({ userId }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetch(`/api/users/${userId}`).then(r => r.json()).then(setUser);
  }, [userId]);

  return <div>{user?.name}</div>;
}

// CORRECT -- presentational receives data
function UserCard({ user }) {
  return <div>{user.name}</div>;
}
```

### Mistake 4: Container Components with Markup

```javascript
// WRONG -- container has styling and layout
function UserListContainer() {
  const users = useUsers();

  return (
    <div className="fancy-layout with-gradient">
      <div className="animated-border">
        <UserList users={users} />
      </div>
    </div>
  );
}

// CORRECT -- container only passes data, no styling
function UserListContainer() {
  const users = useUsers();
  return <UserList users={users} />;
}
```

---

## Best Practices

1. **Start with hooks** -- extract data logic into custom hooks first. Only split into container/presentational if you have a concrete reason (reuse, Storybook, team split).

2. **Presentational components should be pure** -- given the same props, they render the same output. No API calls, no side effects.

3. **Container components should have minimal markup** -- ideally just a single presentational component. Layout and styling belong in the presentational component.

4. **Use TypeScript or PropTypes** -- the props interface between container and presentational is a contract. Type it clearly.

5. **Group related props** -- if you have 15+ props, group them into objects (data, filters, actions, etc.).

6. **Name clearly** -- use suffixes like `Container`, `View`, or `Presentation` to make the role obvious. Or use a `hooks/` folder for the data logic and keep the component file for rendering.

---

## Quick Summary

The Container/Presentational pattern separates data logic from rendering. Container components fetch data, manage state, and handle side effects. Presentational components receive data through props and render the UI. React Hooks shifted the pattern: instead of a separate container component, a custom hook can extract the data logic while the component handles both the hook call and the rendering. The full split is still valuable when presentational components need to be reused across different data sources, displayed in Storybook, or tested in isolation.

```
2015 approach:                    2019+ approach:

  Container Component             Custom Hook
    (fetches data)                  (fetches data)
         |                              |
         v                              v
  Presentational Component         Component
    (renders UI)                    (calls hook + renders UI)

                    OR when reuse is needed:

                    Custom Hook
                        |
                        v
                  Container Component
                        |
                        v
                  Presentational Component
                    (reusable across data sources)
```

---

## Key Points

- Container components handle data, state, and side effects
- Presentational components handle rendering and receive everything via props
- This separation improves testability, reusability, and Storybook support
- React Hooks can replace container components with custom hooks
- The full container/presentational split is still useful when presentational components need reuse
- Do not split prematurely -- start with hooks and split only when needed
- Keep presentational components pure (no side effects, no API calls)
- Keep container components minimal (no styling, no layout markup)

---

## Practice Questions

1. What is the main difference between a container component and a presentational component? Give one example of each.

2. How did React Hooks change the Container/Presentational pattern? When is a custom hook sufficient, and when do you still need the full split?

3. A presentational component has 18 props. What are two strategies to reduce this complexity?

4. Your team uses Storybook for UI development. How does the Container/Presentational pattern help with this?

5. A junior developer suggests that every component should be split into container and presentational. Why is this advice too rigid?

---

## Exercises

### Exercise 1: Refactor a Monolith Component

Take this monolith component and refactor it into a custom hook and a presentational component:

```javascript
function TodoList() {
  const [todos, setTodos] = useState([]);
  const [newTodo, setNewTodo] = useState("");
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    fetch("/api/todos")
      .then((r) => r.json())
      .then(setTodos);
  }, []);

  function addTodo() {
    fetch("/api/todos", {
      method: "POST",
      body: JSON.stringify({ text: newTodo, done: false })
    })
      .then((r) => r.json())
      .then((todo) => {
        setTodos([...todos, todo]);
        setNewTodo("");
      });
  }

  function toggleTodo(id) {
    const todo = todos.find((t) => t.id === id);
    fetch(`/api/todos/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ done: !todo.done })
    }).then(() => {
      setTodos(todos.map((t) =>
        t.id === id ? { ...t, done: !t.done } : t
      ));
    });
  }

  const filtered = todos.filter((t) => {
    if (filter === "active") return !t.done;
    if (filter === "done") return t.done;
    return true;
  });

  return (
    <div>
      <h1>Todos</h1>
      <input value={newTodo} onChange={(e) => setNewTodo(e.target.value)} />
      <button onClick={addTodo}>Add</button>
      <div>
        <button onClick={() => setFilter("all")}>All</button>
        <button onClick={() => setFilter("active")}>Active</button>
        <button onClick={() => setFilter("done")}>Done</button>
      </div>
      <ul>
        {filtered.map((todo) => (
          <li
            key={todo.id}
            onClick={() => toggleTodo(todo.id)}
            style={{ textDecoration: todo.done ? "line-through" : "none" }}
          >
            {todo.text}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### Exercise 2: Reusable Data Table

Build a presentational `DataTable` component that can display any tabular data. Then create two different container components (or hooks) that feed it user data and product data respectively.

```javascript
// Presentational -- works with any data
function DataTable({ columns, rows, onRowClick, sortBy, onSort }) {
  // Your code here
}

// Container 1: Users
function UserTable() {
  // Fetch users, transform into rows, render DataTable
}

// Container 2: Products
function ProductTable() {
  // Fetch products, transform into rows, render DataTable
}
```

### Exercise 3: Storybook-Ready Components

Take a component you have built previously (or the UserDashboard from this chapter) and create a version that works in Storybook. Write three stories: default state, loading state, and error state.

```javascript
// UserDashboard.stories.jsx

export default { title: "UserDashboard" };

export const Default = () => (
  <UserDashboardView
    users={mockUsers}
    loading={false}
    error={null}
    /* ... mock all props */
  />
);

export const Loading = () => (
  <UserDashboardView loading={true} users={[]} /* ... */ />
);

export const Error = () => (
  <UserDashboardView
    loading={false}
    error="Failed to fetch users"
    users={[]}
    /* ... */
  />
);
```

---

## What Is Next?

You have learned how to separate data logic from UI rendering. The next chapter introduces **Higher-Order Components (HOCs)**, another way to share behavior across components. HOCs wrap a component with additional functionality -- similar to how decorators wrap functions. You will learn when HOCs are useful, how they compare to hooks, and the common pitfalls to avoid.
