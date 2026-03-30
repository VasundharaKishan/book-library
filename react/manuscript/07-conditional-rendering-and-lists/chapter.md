# Chapter 7: Conditional Rendering and Lists in Practice

---

## Learning Goals

By the end of this chapter, you will be able to:

- Handle loading, error, and empty states in your components
- Build data-driven UIs that respond to different application states
- Create sophisticated list components with sorting, filtering, and searching
- Understand and implement the "status pattern" for managing async UI states
- Use enums and object maps for multi-condition rendering
- Build tabbed interfaces, accordions, and other state-driven UI patterns
- Render nested lists and hierarchical data
- Handle edge cases gracefully (empty arrays, null data, undefined fields)
- Combine conditional rendering with lists in real-world scenarios
- Apply best practices for organizing conditional logic in components

---

## Why This Chapter Exists

In Chapter 3, we introduced the basics of conditional rendering (`&&`, ternary, if/else) and list rendering (`map()`, keys). In Chapter 5, we learned state. In Chapter 6, we learned event handling.

Now it is time to combine all of these skills to build components that look and feel like real applications. Real-world components rarely just display static data — they need to:

- Show a spinner while data loads
- Display an error message if something fails
- Show a "no results" message when a list is empty
- Let users filter, sort, and search through data
- Switch between different views based on user selections

This chapter focuses on the **practical patterns** that make React applications feel polished and professional.

---

## The Three States of Data

Almost every component that displays data goes through three states:

```
┌─────────────────────────────────────────┐
│                                         │
│   1. LOADING     →  "Fetching data..."  │
│                                         │
│   2. ERROR       →  "Something broke"   │
│                                         │
│   3. SUCCESS     →  Show the data       │
│      ├── Data exists → Render list      │
│      └── Data empty  → "No items"       │
│                                         │
└─────────────────────────────────────────┘
```

Handling all three states is what separates amateur UIs from professional ones. A component that does not handle loading shows a blank screen. A component that does not handle errors leaves the user confused. A component that does not handle empty data shows... nothing.

### The Loading-Error-Data Pattern

Here is a pattern you will use in almost every data-driven component:

```jsx
import { useState, useEffect } from "react";

function UserList() {
  const [users, setUsers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchUsers() {
      try {
        setIsLoading(true);
        setError(null);

        const response = await fetch("https://jsonplaceholder.typicode.com/users");

        if (!response.ok) {
          throw new Error(`Server responded with ${response.status}`);
        }

        const data = await response.json();
        setUsers(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    }

    fetchUsers();
  }, []);

  // State 1: Loading
  if (isLoading) {
    return (
      <div style={{ textAlign: "center", padding: "2rem" }}>
        <p>Loading users...</p>
      </div>
    );
  }

  // State 2: Error
  if (error) {
    return (
      <div style={{ textAlign: "center", padding: "2rem", color: "#e53e3e" }}>
        <h2>Something went wrong</h2>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>Try Again</button>
      </div>
    );
  }

  // State 3: Empty
  if (users.length === 0) {
    return (
      <div style={{ textAlign: "center", padding: "2rem", color: "#718096" }}>
        <h2>No users found</h2>
        <p>There are no users to display at this time.</p>
      </div>
    );
  }

  // State 4: Success with data
  return (
    <div>
      <h2>Users ({users.length})</h2>
      <ul>
        {users.map((user) => (
          <li key={user.id}>
            <strong>{user.name}</strong> — {user.email}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

**What this code does:**

1. **Three pieces of state**: `users` (the data), `isLoading` (whether we are fetching), and `error` (any error message).
2. **`useEffect`** fetches data when the component first renders. (We will learn `useEffect` in depth in Chapter 8 — for now, understand that it runs code after the component appears on screen.)
3. **Four conditional returns**: Loading → Error → Empty → Data. The order matters — we check loading first, then error, then empty, then finally render the data.

**Why the order matters:**

```
Check isLoading first:
  → If true, show spinner (we don't know if there's data or an error yet)

Check error second:
  → If there's an error, show error message (even if there might be stale data)

Check empty third:
  → If the array is empty, show "no results" (don't render an empty list)

Otherwise:
  → We have data! Render it.
```

If you checked for empty data before loading, you would briefly show "No users found" before the data arrives.

---

## The Status Pattern

Managing three separate boolean/string variables (`isLoading`, `error`, `data`) works but can lead to impossible states. For example, what does it mean if `isLoading` is `true` AND `error` has a value? That should never happen, but nothing prevents it.

A cleaner approach is to use a single `status` variable:

```jsx
import { useState, useEffect } from "react";

function ProductList() {
  const [status, setStatus] = useState("idle"); // "idle" | "loading" | "error" | "success"
  const [products, setProducts] = useState([]);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    async function fetchProducts() {
      setStatus("loading");

      try {
        const response = await fetch("https://fakestoreapi.com/products");

        if (!response.ok) {
          throw new Error("Failed to fetch products");
        }

        const data = await response.json();
        setProducts(data);
        setStatus("success");
      } catch (err) {
        setErrorMessage(err.message);
        setStatus("error");
      }
    }

    fetchProducts();
  }, []);

  function renderContent() {
    switch (status) {
      case "idle":
      case "loading":
        return <LoadingSpinner />;

      case "error":
        return <ErrorMessage message={errorMessage} />;

      case "success":
        if (products.length === 0) {
          return <EmptyState message="No products available." />;
        }
        return (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1rem" }}>
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        );

      default:
        return null;
    }
  }

  return (
    <div style={{ maxWidth: "900px", margin: "0 auto", padding: "2rem" }}>
      <h1>Products</h1>
      {renderContent()}
    </div>
  );
}

function LoadingSpinner() {
  return (
    <div style={{ textAlign: "center", padding: "3rem" }}>
      <div
        style={{
          width: "40px",
          height: "40px",
          border: "4px solid #e2e8f0",
          borderTopColor: "#3182ce",
          borderRadius: "50%",
          margin: "0 auto 1rem",
          animation: "spin 1s linear infinite",
        }}
      />
      <p style={{ color: "#718096" }}>Loading products...</p>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

function ErrorMessage({ message }) {
  return (
    <div
      style={{
        backgroundColor: "#fff5f5",
        border: "1px solid #fc8181",
        borderRadius: "8px",
        padding: "1.5rem",
        textAlign: "center",
      }}
    >
      <h3 style={{ color: "#e53e3e", marginBottom: "0.5rem" }}>Error</h3>
      <p style={{ color: "#742a2a" }}>{message}</p>
    </div>
  );
}

function EmptyState({ message }) {
  return (
    <div
      style={{
        backgroundColor: "#f7fafc",
        border: "2px dashed #cbd5e0",
        borderRadius: "8px",
        padding: "3rem",
        textAlign: "center",
      }}
    >
      <p style={{ color: "#718096", fontSize: "1.125rem" }}>{message}</p>
    </div>
  );
}

function ProductCard({ product }) {
  return (
    <div
      style={{
        border: "1px solid #e2e8f0",
        borderRadius: "8px",
        padding: "1rem",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <h3 style={{ fontSize: "1rem", marginBottom: "0.5rem" }}>
        {product.title.length > 50
          ? product.title.substring(0, 50) + "..."
          : product.title}
      </h3>
      <p style={{ color: "#718096", fontSize: "0.875rem", flex: 1 }}>
        {product.category}
      </p>
      <p style={{ fontWeight: "bold", fontSize: "1.25rem", color: "#2d3748" }}>
        ${product.price.toFixed(2)}
      </p>
    </div>
  );
}
```

**Why the status pattern is better:**

| Separate Variables | Status Pattern |
|---|---|
| `isLoading: true, error: "fail"` — impossible state, but possible in code | Status is always one value — impossible states are impossible |
| Three variables to manage and keep in sync | One variable controls the entire flow |
| Easy to forget to reset `error` when retrying | Each status transition is explicit |
| Conditional logic requires checking multiple variables | `switch` statement maps each status to a render |

---

## Enum Pattern for Multiple Views

When a component can display many different views, an enum (or object map) is cleaner than nested ternaries or long if/else chains:

```jsx
import { useState } from "react";

function SettingsPage() {
  const [activeTab, setActiveTab] = useState("profile");

  const tabs = [
    { id: "profile", label: "Profile" },
    { id: "account", label: "Account" },
    { id: "notifications", label: "Notifications" },
    { id: "privacy", label: "Privacy" },
  ];

  // Enum pattern: map status values to components
  const tabContent = {
    profile: <ProfileSettings />,
    account: <AccountSettings />,
    notifications: <NotificationSettings />,
    privacy: <PrivacySettings />,
  };

  return (
    <div style={{ maxWidth: "700px", margin: "0 auto" }}>
      <h1>Settings</h1>

      {/* Tab navigation */}
      <div style={{ display: "flex", gap: "0", borderBottom: "2px solid #e2e8f0" }}>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: "0.75rem 1.5rem",
              border: "none",
              borderBottom: activeTab === tab.id ? "2px solid #3182ce" : "2px solid transparent",
              backgroundColor: "transparent",
              color: activeTab === tab.id ? "#3182ce" : "#718096",
              fontWeight: activeTab === tab.id ? "bold" : "normal",
              cursor: "pointer",
              marginBottom: "-2px",
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab content — rendered from the enum map */}
      <div style={{ padding: "1.5rem 0" }}>
        {tabContent[activeTab]}
      </div>
    </div>
  );
}

function ProfileSettings() {
  return (
    <div>
      <h2>Profile Settings</h2>
      <p>Manage your name, avatar, and bio.</p>
    </div>
  );
}

function AccountSettings() {
  return (
    <div>
      <h2>Account Settings</h2>
      <p>Change your email, password, and linked accounts.</p>
    </div>
  );
}

function NotificationSettings() {
  return (
    <div>
      <h2>Notification Settings</h2>
      <p>Control email, push, and SMS notifications.</p>
    </div>
  );
}

function PrivacySettings() {
  return (
    <div>
      <h2>Privacy Settings</h2>
      <p>Manage data sharing and visibility preferences.</p>
    </div>
  );
}

export default SettingsPage;
```

**Why this is better than nested ternaries:**

```jsx
// ❌ Hard to read — nested ternaries
{activeTab === "profile" ? (
  <ProfileSettings />
) : activeTab === "account" ? (
  <AccountSettings />
) : activeTab === "notifications" ? (
  <NotificationSettings />
) : (
  <PrivacySettings />
)}

// ✅ Clean — enum/object map
const tabContent = {
  profile: <ProfileSettings />,
  account: <AccountSettings />,
  notifications: <NotificationSettings />,
  privacy: <PrivacySettings />,
};

{tabContent[activeTab]}
```

The enum pattern scales well — adding a new tab requires adding one entry to the `tabs` array and one entry to the `tabContent` object. No conditional logic needs to change.

---

## Practical List Patterns

### Searchable List

One of the most common UI patterns — filtering a list based on user input:

```jsx
import { useState } from "react";

function ContactList() {
  const [searchTerm, setSearchTerm] = useState("");

  const contacts = [
    { id: 1, name: "Alice Johnson", email: "alice@example.com", department: "Engineering" },
    { id: 2, name: "Bob Smith", email: "bob@example.com", department: "Design" },
    { id: 3, name: "Charlie Brown", email: "charlie@example.com", department: "Engineering" },
    { id: 4, name: "Diana Prince", email: "diana@example.com", department: "Marketing" },
    { id: 5, name: "Edward Norton", email: "edward@example.com", department: "Design" },
    { id: 6, name: "Fiona Apple", email: "fiona@example.com", department: "Engineering" },
    { id: 7, name: "George Lucas", email: "george@example.com", department: "Marketing" },
    { id: 8, name: "Helen Troy", email: "helen@example.com", department: "Design" },
  ];

  const filteredContacts = contacts.filter((contact) => {
    const term = searchTerm.toLowerCase();
    return (
      contact.name.toLowerCase().includes(term) ||
      contact.email.toLowerCase().includes(term) ||
      contact.department.toLowerCase().includes(term)
    );
  });

  return (
    <div style={{ maxWidth: "500px", margin: "0 auto" }}>
      <h2>Contacts</h2>

      {/* Search input */}
      <input
        type="text"
        value={searchTerm}
        onChange={(event) => setSearchTerm(event.target.value)}
        placeholder="Search by name, email, or department..."
        style={{
          width: "100%",
          padding: "0.75rem",
          border: "1px solid #e2e8f0",
          borderRadius: "8px",
          fontSize: "1rem",
          boxSizing: "border-box",
          marginBottom: "1rem",
        }}
      />

      {/* Result count */}
      <p style={{ color: "#718096", fontSize: "0.875rem", marginBottom: "0.5rem" }}>
        {searchTerm
          ? `${filteredContacts.length} result${filteredContacts.length !== 1 ? "s" : ""} for "${searchTerm}"`
          : `${contacts.length} contacts`}
      </p>

      {/* List or empty state */}
      {filteredContacts.length === 0 ? (
        <div
          style={{
            textAlign: "center",
            padding: "2rem",
            backgroundColor: "#f7fafc",
            borderRadius: "8px",
            border: "2px dashed #cbd5e0",
          }}
        >
          <p style={{ color: "#718096" }}>
            No contacts match "{searchTerm}"
          </p>
          <button
            onClick={() => setSearchTerm("")}
            style={{
              marginTop: "0.5rem",
              padding: "0.5rem 1rem",
              backgroundColor: "#3182ce",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
            }}
          >
            Clear search
          </button>
        </div>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {filteredContacts.map((contact) => (
            <li
              key={contact.id}
              style={{
                padding: "0.75rem",
                borderBottom: "1px solid #e2e8f0",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div>
                <strong>{contact.name}</strong>
                <br />
                <span style={{ color: "#718096", fontSize: "0.875rem" }}>
                  {contact.email}
                </span>
              </div>
              <span
                style={{
                  backgroundColor: "#edf2f7",
                  padding: "0.25rem 0.5rem",
                  borderRadius: "4px",
                  fontSize: "0.75rem",
                  color: "#4a5568",
                }}
              >
                {contact.department}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

**Key points:**

1. **Derived state, not duplicated state.** We do not store the filtered list in state. We compute it from `contacts` and `searchTerm` on every render. This is correct because `filteredContacts` is entirely determined by those two values — there is no reason to store it separately.

2. **Multi-field search.** The filter checks name, email, and department. Searching "eng" would match anyone in Engineering, and searching "alice" matches by name.

3. **Empty state with action.** When no results match, we show a message and a "Clear search" button. Never just show an empty list — always tell the user why it is empty and give them a way to fix it.

### Sortable List

Let users sort data by clicking column headers:

```jsx
import { useState } from "react";

function EmployeeTable() {
  const [sortField, setSortField] = useState("name");
  const [sortDirection, setSortDirection] = useState("asc");

  const employees = [
    { id: 1, name: "Alice Johnson", role: "Senior Developer", salary: 120000, startDate: "2019-03-15" },
    { id: 2, name: "Bob Smith", role: "Designer", salary: 95000, startDate: "2020-07-01" },
    { id: 3, name: "Charlie Brown", role: "Junior Developer", salary: 75000, startDate: "2022-01-10" },
    { id: 4, name: "Diana Prince", role: "Tech Lead", salary: 145000, startDate: "2017-11-20" },
    { id: 5, name: "Edward Norton", role: "Product Manager", salary: 130000, startDate: "2018-06-05" },
    { id: 6, name: "Fiona Apple", role: "Senior Developer", salary: 118000, startDate: "2019-09-12" },
  ];

  function handleSort(field) {
    if (sortField === field) {
      // Same field: toggle direction
      setSortDirection((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      // Different field: sort ascending
      setSortField(field);
      setSortDirection("asc");
    }
  }

  function getSortIndicator(field) {
    if (sortField !== field) return " ↕";
    return sortDirection === "asc" ? " ↑" : " ↓";
  }

  // Sort the employees array (create a copy first — never mutate the original)
  const sortedEmployees = [...employees].sort((a, b) => {
    let valueA = a[sortField];
    let valueB = b[sortField];

    // Handle string comparison
    if (typeof valueA === "string") {
      valueA = valueA.toLowerCase();
      valueB = valueB.toLowerCase();
    }

    if (valueA < valueB) return sortDirection === "asc" ? -1 : 1;
    if (valueA > valueB) return sortDirection === "asc" ? 1 : -1;
    return 0;
  });

  const headerStyle = {
    padding: "0.75rem",
    textAlign: "left",
    cursor: "pointer",
    backgroundColor: "#f7fafc",
    borderBottom: "2px solid #e2e8f0",
    userSelect: "none",
  };

  const cellStyle = {
    padding: "0.75rem",
    borderBottom: "1px solid #e2e8f0",
  };

  return (
    <div style={{ maxWidth: "800px", margin: "0 auto" }}>
      <h2>Employees</h2>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th style={headerStyle} onClick={() => handleSort("name")}>
              Name{getSortIndicator("name")}
            </th>
            <th style={headerStyle} onClick={() => handleSort("role")}>
              Role{getSortIndicator("role")}
            </th>
            <th style={headerStyle} onClick={() => handleSort("salary")}>
              Salary{getSortIndicator("salary")}
            </th>
            <th style={headerStyle} onClick={() => handleSort("startDate")}>
              Start Date{getSortIndicator("startDate")}
            </th>
          </tr>
        </thead>
        <tbody>
          {sortedEmployees.map((employee) => (
            <tr key={employee.id}>
              <td style={cellStyle}>{employee.name}</td>
              <td style={cellStyle}>{employee.role}</td>
              <td style={cellStyle}>${employee.salary.toLocaleString()}</td>
              <td style={cellStyle}>
                {new Date(employee.startDate).toLocaleDateString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

**Key points:**

1. **Never mutate the original array.** We use `[...employees].sort(...)` to create a sorted copy. The `sort()` method mutates the array it is called on, so always spread into a new array first.

2. **Toggle sort direction.** Clicking the same column header toggles between ascending and descending. Clicking a different column resets to ascending.

3. **Sort indicators.** Visual arrows (↑ ↓ ↕) show the current sort state so users know which column is sorted and in which direction.

### Combined: Search + Filter + Sort

Real applications combine all three. Here is a comprehensive example:

```jsx
import { useState } from "react";

function BookCatalog() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedGenre, setSelectedGenre] = useState("all");
  const [sortBy, setSortBy] = useState("title");
  const [sortDirection, setSortDirection] = useState("asc");

  const books = [
    { id: 1, title: "The Great Gatsby", author: "F. Scott Fitzgerald", genre: "Fiction", year: 1925, rating: 4.2 },
    { id: 2, title: "To Kill a Mockingbird", author: "Harper Lee", genre: "Fiction", year: 1960, rating: 4.5 },
    { id: 3, title: "A Brief History of Time", author: "Stephen Hawking", genre: "Science", year: 1988, rating: 4.3 },
    { id: 4, title: "Clean Code", author: "Robert C. Martin", genre: "Technology", year: 2008, rating: 4.4 },
    { id: 5, title: "Sapiens", author: "Yuval Noah Harari", genre: "History", year: 2011, rating: 4.6 },
    { id: 6, title: "Dune", author: "Frank Herbert", genre: "Science Fiction", year: 1965, rating: 4.5 },
    { id: 7, title: "The Pragmatic Programmer", author: "David Thomas", genre: "Technology", year: 1999, rating: 4.3 },
    { id: 8, title: "1984", author: "George Orwell", genre: "Fiction", year: 1949, rating: 4.7 },
    { id: 9, title: "Cosmos", author: "Carl Sagan", genre: "Science", year: 1980, rating: 4.6 },
    { id: 10, title: "The Hobbit", author: "J.R.R. Tolkien", genre: "Fiction", year: 1937, rating: 4.7 },
  ];

  // Get unique genres for the filter dropdown
  const genres = ["all", ...new Set(books.map((book) => book.genre))];

  // Step 1: Filter by genre
  const genreFiltered = selectedGenre === "all"
    ? books
    : books.filter((book) => book.genre === selectedGenre);

  // Step 2: Filter by search term
  const searchFiltered = genreFiltered.filter((book) => {
    const term = searchTerm.toLowerCase();
    return (
      book.title.toLowerCase().includes(term) ||
      book.author.toLowerCase().includes(term)
    );
  });

  // Step 3: Sort
  const sortedBooks = [...searchFiltered].sort((a, b) => {
    let valueA = a[sortBy];
    let valueB = b[sortBy];

    if (typeof valueA === "string") {
      valueA = valueA.toLowerCase();
      valueB = valueB.toLowerCase();
    }

    if (valueA < valueB) return sortDirection === "asc" ? -1 : 1;
    if (valueA > valueB) return sortDirection === "asc" ? 1 : -1;
    return 0;
  });

  function handleSortChange(field) {
    if (sortBy === field) {
      setSortDirection((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortBy(field);
      setSortDirection("asc");
    }
  }

  function clearAllFilters() {
    setSearchTerm("");
    setSelectedGenre("all");
    setSortBy("title");
    setSortDirection("asc");
  }

  const hasActiveFilters = searchTerm !== "" || selectedGenre !== "all";

  return (
    <div style={{ maxWidth: "700px", margin: "0 auto", padding: "1rem" }}>
      <h1>Book Catalog</h1>

      {/* Controls */}
      <div style={{ display: "flex", gap: "0.75rem", marginBottom: "1rem", flexWrap: "wrap" }}>
        <input
          type="text"
          value={searchTerm}
          onChange={(event) => setSearchTerm(event.target.value)}
          placeholder="Search title or author..."
          style={{
            flex: 1,
            minWidth: "200px",
            padding: "0.5rem 0.75rem",
            border: "1px solid #e2e8f0",
            borderRadius: "6px",
          }}
        />
        <select
          value={selectedGenre}
          onChange={(event) => setSelectedGenre(event.target.value)}
          style={{ padding: "0.5rem", borderRadius: "6px", border: "1px solid #e2e8f0" }}
        >
          {genres.map((genre) => (
            <option key={genre} value={genre}>
              {genre === "all" ? "All Genres" : genre}
            </option>
          ))}
        </select>
        <select
          value={`${sortBy}-${sortDirection}`}
          onChange={(event) => {
            const [field, dir] = event.target.value.split("-");
            setSortBy(field);
            setSortDirection(dir);
          }}
          style={{ padding: "0.5rem", borderRadius: "6px", border: "1px solid #e2e8f0" }}
        >
          <option value="title-asc">Title A-Z</option>
          <option value="title-desc">Title Z-A</option>
          <option value="author-asc">Author A-Z</option>
          <option value="author-desc">Author Z-A</option>
          <option value="year-asc">Year (Oldest)</option>
          <option value="year-desc">Year (Newest)</option>
          <option value="rating-asc">Rating (Low to High)</option>
          <option value="rating-desc">Rating (High to Low)</option>
        </select>
      </div>

      {/* Status bar */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <span style={{ color: "#718096", fontSize: "0.875rem" }}>
          Showing {sortedBooks.length} of {books.length} books
        </span>
        {hasActiveFilters && (
          <button
            onClick={clearAllFilters}
            style={{
              padding: "0.25rem 0.75rem",
              backgroundColor: "transparent",
              border: "1px solid #cbd5e0",
              borderRadius: "4px",
              cursor: "pointer",
              fontSize: "0.875rem",
              color: "#718096",
            }}
          >
            Clear filters
          </button>
        )}
      </div>

      {/* Results */}
      {sortedBooks.length === 0 ? (
        <div
          style={{
            textAlign: "center",
            padding: "3rem",
            backgroundColor: "#f7fafc",
            borderRadius: "8px",
            border: "2px dashed #cbd5e0",
          }}
        >
          <p style={{ fontSize: "1.125rem", color: "#718096", marginBottom: "0.5rem" }}>
            No books match your criteria
          </p>
          <p style={{ color: "#a0aec0", fontSize: "0.875rem" }}>
            Try adjusting your search or filters.
          </p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {sortedBooks.map((book) => (
            <div
              key={book.id}
              style={{
                padding: "1rem",
                border: "1px solid #e2e8f0",
                borderRadius: "8px",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div>
                <h3 style={{ margin: "0 0 0.25rem 0", fontSize: "1rem" }}>
                  {book.title}
                </h3>
                <p style={{ margin: 0, color: "#718096", fontSize: "0.875rem" }}>
                  by {book.author} • {book.year}
                </p>
              </div>
              <div style={{ textAlign: "right" }}>
                <span
                  style={{
                    backgroundColor: "#edf2f7",
                    padding: "0.25rem 0.5rem",
                    borderRadius: "4px",
                    fontSize: "0.75rem",
                    display: "block",
                    marginBottom: "0.25rem",
                  }}
                >
                  {book.genre}
                </span>
                <span style={{ color: "#d69e2e", fontSize: "0.875rem" }}>
                  {"★".repeat(Math.floor(book.rating))} {book.rating}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default BookCatalog;
```

**The data pipeline — filter, then search, then sort:**

```
All books (10)
    │
    ├── Genre filter → "Technology" (2 books)
    │
    ├── Search filter → "pragmatic" (1 book)
    │
    └── Sort → by title ascending (1 book)
```

Each step narrows down the data. This pipeline approach is clean and composable — you can add more filter steps without restructuring the logic.

---

## Rendering Nested and Hierarchical Data

Sometimes data is nested — categories with subcategories, comments with replies, file trees. Here is how to handle it:

### Accordion / Collapsible Sections

```jsx
import { useState } from "react";

function AccordionItem({ title, children }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div style={{ borderBottom: "1px solid #e2e8f0" }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          width: "100%",
          padding: "1rem",
          backgroundColor: "transparent",
          border: "none",
          cursor: "pointer",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          fontSize: "1rem",
          fontWeight: "bold",
          textAlign: "left",
        }}
      >
        <span>{title}</span>
        <span style={{ transform: isOpen ? "rotate(180deg)" : "rotate(0)", transition: "transform 0.2s" }}>
          ▼
        </span>
      </button>
      {isOpen && (
        <div style={{ padding: "0 1rem 1rem" }}>
          {children}
        </div>
      )}
    </div>
  );
}

function FAQ() {
  const faqData = [
    {
      id: 1,
      category: "Getting Started",
      questions: [
        { id: "q1", question: "What is React?", answer: "React is a JavaScript library for building user interfaces. It lets you compose complex UIs from small, reusable pieces called components." },
        { id: "q2", question: "Do I need to know JavaScript first?", answer: "Yes, you should have a solid understanding of JavaScript basics including ES6 features like arrow functions, destructuring, and modules." },
      ],
    },
    {
      id: 2,
      category: "Components",
      questions: [
        { id: "q3", question: "What is the difference between a component and an element?", answer: "A component is a function that returns JSX. An element is what a component returns — a description of what should appear on screen." },
        { id: "q4", question: "Can a component return multiple elements?", answer: "Yes, by wrapping them in a Fragment (<>...</>) or a container element like a div." },
      ],
    },
    {
      id: 3,
      category: "State and Props",
      questions: [
        { id: "q5", question: "What is the difference between state and props?", answer: "Props are passed from a parent component and are read-only. State is managed within the component and can be updated with setter functions." },
        { id: "q6", question: "When should I lift state up?", answer: "When two or more sibling components need to share or synchronize the same piece of data, lift the state to their closest common parent." },
      ],
    },
  ];

  return (
    <div style={{ maxWidth: "600px", margin: "0 auto" }}>
      <h1>Frequently Asked Questions</h1>
      {faqData.map((category) => (
        <div key={category.id} style={{ marginBottom: "1.5rem" }}>
          <h2 style={{ fontSize: "1.25rem", color: "#2d3748", marginBottom: "0.5rem" }}>
            {category.category}
          </h2>
          <div style={{ border: "1px solid #e2e8f0", borderRadius: "8px", overflow: "hidden" }}>
            {category.questions.map((item) => (
              <AccordionItem key={item.id} title={item.question}>
                <p style={{ color: "#4a5568", lineHeight: "1.6" }}>{item.answer}</p>
              </AccordionItem>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

export default FAQ;
```

**What this demonstrates:**

1. **Nested data rendering.** The outer `map()` iterates over categories. The inner `map()` iterates over questions within each category. Each level has its own key.

2. **Local state per instance.** Each `AccordionItem` has its own `isOpen` state. Opening one does not affect the others.

3. **Children prop.** The `AccordionItem` uses `{children}` to render whatever is passed between its opening and closing tags. This makes it reusable — the accordion does not care what the content is.

### Nested Comments / Reply Threads

A recursive component for tree-structured data:

```jsx
import { useState } from "react";

function Comment({ comment, depth = 0 }) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const maxDepth = 5;

  const hasReplies = comment.replies && comment.replies.length > 0;

  return (
    <div
      style={{
        marginLeft: depth > 0 ? "1.5rem" : 0,
        borderLeft: depth > 0 ? "2px solid #e2e8f0" : "none",
        paddingLeft: depth > 0 ? "1rem" : 0,
        marginBottom: "0.75rem",
      }}
    >
      {/* Comment header */}
      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.25rem" }}>
        <strong style={{ fontSize: "0.875rem" }}>{comment.author}</strong>
        <span style={{ color: "#a0aec0", fontSize: "0.75rem" }}>{comment.time}</span>
        {hasReplies && (
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            style={{
              backgroundColor: "transparent",
              border: "none",
              color: "#718096",
              cursor: "pointer",
              fontSize: "0.75rem",
              padding: "0",
            }}
          >
            {isCollapsed ? `[+${comment.replies.length} replies]` : "[–]"}
          </button>
        )}
      </div>

      {/* Comment body */}
      <p style={{ margin: "0 0 0.5rem 0", color: "#2d3748", fontSize: "0.9375rem" }}>
        {comment.text}
      </p>

      {/* Nested replies — recursive rendering */}
      {hasReplies && !isCollapsed && (
        <div>
          {comment.replies.map((reply) => (
            <Comment
              key={reply.id}
              comment={reply}
              depth={Math.min(depth + 1, maxDepth)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function CommentThread() {
  const comments = [
    {
      id: 1,
      author: "Alice",
      time: "2 hours ago",
      text: "React hooks completely changed how I write components. So much cleaner than class components!",
      replies: [
        {
          id: 2,
          author: "Bob",
          time: "1 hour ago",
          text: "Agreed! useState and useEffect cover 90% of my use cases.",
          replies: [
            {
              id: 3,
              author: "Charlie",
              time: "45 minutes ago",
              text: "Don't forget useRef — it's incredibly useful for DOM access and storing mutable values.",
              replies: [],
            },
          ],
        },
        {
          id: 4,
          author: "Diana",
          time: "1 hour ago",
          text: "I still think class components were easier to understand for beginners, but hooks are definitely the way forward.",
          replies: [],
        },
      ],
    },
    {
      id: 5,
      author: "Edward",
      time: "3 hours ago",
      text: "Has anyone tried the new React compiler? Curious about the performance improvements.",
      replies: [
        {
          id: 6,
          author: "Fiona",
          time: "2 hours ago",
          text: "I tested it on a large project. The automatic memoization is impressive — removed all my useMemo and useCallback calls.",
          replies: [],
        },
      ],
    },
  ];

  return (
    <div style={{ maxWidth: "600px", margin: "0 auto", padding: "1rem" }}>
      <h1>Discussion</h1>
      {comments.map((comment) => (
        <Comment key={comment.id} comment={comment} />
      ))}
    </div>
  );
}

export default CommentThread;
```

**Recursive rendering explained:**

The `Comment` component renders itself for each reply. This is called **recursion** — the component calls itself with a deeper nesting level:

```
Comment (Alice, depth 0)
├── Comment (Bob, depth 1)
│   └── Comment (Charlie, depth 2)
└── Comment (Diana, depth 1)

Comment (Edward, depth 0)
└── Comment (Fiona, depth 1)
```

The `depth` prop increases with each level, controlling indentation and the left border. A `maxDepth` limit prevents infinitely deep nesting.

---

## Handling Edge Cases

Real data is messy. Here is how to handle common edge cases:

### Null and Undefined Data

```jsx
function UserProfile({ user }) {
  // Guard against null/undefined user
  if (!user) {
    return <p>No user data available.</p>;
  }

  return (
    <div>
      <h2>{user.name || "Unknown User"}</h2>
      <p>Email: {user.email || "Not provided"}</p>
      <p>Phone: {user.phone ?? "N/A"}</p>
      <p>Bio: {user.bio?.trim() || "No bio written yet."}</p>
      <p>
        Location: {user.address?.city || "Unknown city"},{" "}
        {user.address?.country || "Unknown country"}
      </p>
    </div>
  );
}
```

**Defensive patterns used:**

| Pattern | Purpose |
|---------|---------|
| `if (!user)` | Guard clause for missing data |
| `user.name \|\| "Unknown User"` | Fallback for falsy values |
| `user.phone ?? "N/A"` | Nullish coalescing — only falls back on `null` or `undefined`, not `0` or `""` |
| `user.bio?.trim()` | Optional chaining — safely access properties that might not exist |
| `user.address?.city` | Safe nested access — will not throw if `address` is undefined |

**`||` vs `??` — an important distinction:**

```javascript
// || (OR) — falls back for ANY falsy value: false, 0, "", null, undefined
0 || "fallback"    // "fallback" (0 is falsy)
"" || "fallback"   // "fallback" ("" is falsy)
null || "fallback"  // "fallback"

// ?? (Nullish coalescing) — falls back ONLY for null or undefined
0 ?? "fallback"    // 0 (0 is not null or undefined)
"" ?? "fallback"   // "" ("" is not null or undefined)
null ?? "fallback"  // "fallback"
```

Use `??` when `0` or `""` are valid values that should not be replaced with a fallback.

### Safely Rendering Lists That Might Not Exist

```jsx
function TagList({ tags }) {
  // tags might be undefined, null, or an array
  const safeTags = tags || [];

  if (safeTags.length === 0) {
    return <p style={{ color: "#a0aec0" }}>No tags</p>;
  }

  return (
    <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
      {safeTags.map((tag) => (
        <span
          key={tag}
          style={{
            backgroundColor: "#edf2f7",
            padding: "0.25rem 0.75rem",
            borderRadius: "9999px",
            fontSize: "0.875rem",
          }}
        >
          {tag}
        </span>
      ))}
    </div>
  );
}

// Usage:
<TagList tags={["react", "javascript"]} />   // Renders tags
<TagList tags={[]} />                          // "No tags"
<TagList tags={null} />                        // "No tags" (not a crash)
<TagList />                                    // "No tags" (not a crash)
```

**The key principle:** Never call `.map()` on something that might not be an array. Always provide a fallback with `|| []` or use default props.

You can also use a default parameter:

```jsx
function TagList({ tags = [] }) {
  // tags is guaranteed to be an array
  // ...
}
```

---

## Rendering Nothing vs Rendering Empty Elements

There is a difference between rendering nothing and rendering an empty element:

```jsx
// Returns null — absolutely nothing in the DOM
function MaybeAlert({ show }) {
  if (!show) return null;
  return <div className="alert">Warning!</div>;
}

// Returns an empty div — an invisible but present DOM element
function MaybeAlert({ show }) {
  return <div>{show ? "Warning!" : ""}</div>;
}
```

**When to return `null`:**
- When the component should be completely invisible, as if it does not exist.
- When the component's presence would affect layout (even empty, a `<div>` takes up space in Flexbox/Grid).

**When to use an empty render inside an element:**
- When you need the element to exist in the DOM for layout purposes (maintaining a placeholder space).
- When the element has styling that should always be present.

---

## The Pending UI Pattern

Modern applications often need to show that something is happening without blocking the entire interface:

```jsx
import { useState } from "react";

function TodoApp() {
  const [todos, setTodos] = useState([
    { id: 1, text: "Learn React", completed: false },
    { id: 2, text: "Build a project", completed: false },
    { id: 3, text: "Deploy to production", completed: false },
  ]);
  const [newTodo, setNewTodo] = useState("");
  const [deletingId, setDeletingId] = useState(null);

  function handleAdd(event) {
    event.preventDefault();
    if (!newTodo.trim()) return;

    const todo = {
      id: Date.now(),
      text: newTodo.trim(),
      completed: false,
    };

    setTodos([...todos, todo]);
    setNewTodo("");
  }

  function handleToggle(id) {
    setTodos(
      todos.map((todo) =>
        todo.id === id ? { ...todo, completed: !todo.completed } : todo
      )
    );
  }

  async function handleDelete(id) {
    setDeletingId(id);

    // Simulate an API call
    await new Promise((resolve) => setTimeout(resolve, 1000));

    setTodos(todos.filter((todo) => todo.id !== id));
    setDeletingId(null);
  }

  const completedCount = todos.filter((t) => t.completed).length;
  const totalCount = todos.length;

  return (
    <div style={{ maxWidth: "500px", margin: "0 auto", padding: "1rem" }}>
      <h1>Todo App</h1>

      {/* Add form */}
      <form onSubmit={handleAdd} style={{ display: "flex", gap: "0.5rem", marginBottom: "1.5rem" }}>
        <input
          type="text"
          value={newTodo}
          onChange={(event) => setNewTodo(event.target.value)}
          placeholder="What needs to be done?"
          style={{
            flex: 1,
            padding: "0.5rem 0.75rem",
            border: "1px solid #e2e8f0",
            borderRadius: "6px",
          }}
        />
        <button
          type="submit"
          style={{
            padding: "0.5rem 1rem",
            backgroundColor: "#3182ce",
            color: "white",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
          }}
        >
          Add
        </button>
      </form>

      {/* Progress indicator */}
      {totalCount > 0 && (
        <div style={{ marginBottom: "1rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.875rem", color: "#718096", marginBottom: "0.25rem" }}>
            <span>{completedCount} of {totalCount} completed</span>
            <span>{Math.round((completedCount / totalCount) * 100)}%</span>
          </div>
          <div style={{ backgroundColor: "#e2e8f0", borderRadius: "4px", height: "8px" }}>
            <div
              style={{
                backgroundColor: completedCount === totalCount ? "#38a169" : "#3182ce",
                height: "100%",
                borderRadius: "4px",
                width: `${(completedCount / totalCount) * 100}%`,
                transition: "width 0.3s ease, background-color 0.3s ease",
              }}
            />
          </div>
        </div>
      )}

      {/* Todo list */}
      {todos.length === 0 ? (
        <div style={{ textAlign: "center", padding: "2rem", color: "#a0aec0" }}>
          <p>No todos yet. Add one above!</p>
        </div>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {todos.map((todo) => {
            const isDeleting = deletingId === todo.id;

            return (
              <li
                key={todo.id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "0.75rem",
                  padding: "0.75rem",
                  borderBottom: "1px solid #edf2f7",
                  opacity: isDeleting ? 0.5 : 1,
                  transition: "opacity 0.2s",
                }}
              >
                {/* Checkbox */}
                <input
                  type="checkbox"
                  checked={todo.completed}
                  onChange={() => handleToggle(todo.id)}
                  disabled={isDeleting}
                  style={{ cursor: isDeleting ? "default" : "pointer" }}
                />

                {/* Text */}
                <span
                  style={{
                    flex: 1,
                    textDecoration: todo.completed ? "line-through" : "none",
                    color: todo.completed ? "#a0aec0" : "#2d3748",
                  }}
                >
                  {todo.text}
                </span>

                {/* Delete button */}
                <button
                  onClick={() => handleDelete(todo.id)}
                  disabled={isDeleting}
                  style={{
                    padding: "0.25rem 0.5rem",
                    backgroundColor: "transparent",
                    border: "1px solid #e53e3e",
                    color: "#e53e3e",
                    borderRadius: "4px",
                    cursor: isDeleting ? "default" : "pointer",
                    fontSize: "0.75rem",
                    opacity: isDeleting ? 0.5 : 1,
                  }}
                >
                  {isDeleting ? "Deleting..." : "Delete"}
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

export default TodoApp;
```

**Pending state pattern:** The `deletingId` tracks which item is being deleted. While deleting:
- The item is faded (`opacity: 0.5`)
- The button text changes to "Deleting..."
- The checkbox and delete button are disabled
- Other items remain fully interactive

This per-item loading state is much better than disabling the entire list.

---

## Conditional CSS Classes

A common need is applying different CSS classes based on state. Here are several approaches:

### String Concatenation

```jsx
function Button({ variant, size, disabled }) {
  let className = "btn";

  if (variant === "primary") className += " btn-primary";
  else if (variant === "secondary") className += " btn-secondary";
  else if (variant === "danger") className += " btn-danger";

  if (size === "small") className += " btn-sm";
  else if (size === "large") className += " btn-lg";

  if (disabled) className += " btn-disabled";

  return <button className={className} disabled={disabled}>Click</button>;
}
```

### Template Literals

```jsx
function Card({ isSelected, isHovered }) {
  return (
    <div
      className={`card ${isSelected ? "card-selected" : ""} ${isHovered ? "card-hovered" : ""}`}
    >
      Content
    </div>
  );
}
```

### Array Join

```jsx
function NavLink({ to, isActive, isDisabled }) {
  const classes = [
    "nav-link",
    isActive && "nav-link-active",
    isDisabled && "nav-link-disabled",
  ]
    .filter(Boolean)  // Removes false, null, undefined values
    .join(" ");

  return <a href={to} className={classes}>Link</a>;
}
```

**How `.filter(Boolean)` works:**

```javascript
const classes = [
  "nav-link",       // truthy → kept
  false && "active", // false → removed
  true && "disabled" // "disabled" → kept
];
// Before filter: ["nav-link", false, "disabled"]
// After filter:  ["nav-link", "disabled"]
// After join:    "nav-link disabled"
```

This is a clean pattern for conditional class names without a library.

---

## Mini Project: Product Dashboard

Let us combine everything into a realistic dashboard:

```jsx
import { useState, useEffect } from "react";

function ProductDashboard() {
  const [products, setProducts] = useState([]);
  const [status, setStatus] = useState("loading");
  const [errorMessage, setErrorMessage] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [sortBy, setSortBy] = useState("name-asc");
  const [view, setView] = useState("grid"); // "grid" or "list"

  // Simulate data fetching
  useEffect(() => {
    async function loadProducts() {
      setStatus("loading");

      // Simulate API delay
      await new Promise((resolve) => setTimeout(resolve, 1500));

      // Simulate random failure (10% chance)
      if (Math.random() < 0.1) {
        setErrorMessage("Failed to connect to the server. Please try again.");
        setStatus("error");
        return;
      }

      const data = [
        { id: 1, name: "Wireless Headphones", category: "Electronics", price: 79.99, rating: 4.5, inStock: true },
        { id: 2, name: "Running Shoes", category: "Sports", price: 129.99, rating: 4.2, inStock: true },
        { id: 3, name: "Coffee Maker", category: "Kitchen", price: 49.99, rating: 4.7, inStock: false },
        { id: 4, name: "Yoga Mat", category: "Sports", price: 29.99, rating: 4.3, inStock: true },
        { id: 5, name: "Bluetooth Speaker", category: "Electronics", price: 59.99, rating: 4.1, inStock: true },
        { id: 6, name: "Chef's Knife", category: "Kitchen", price: 89.99, rating: 4.8, inStock: true },
        { id: 7, name: "Smart Watch", category: "Electronics", price: 199.99, rating: 4.4, inStock: false },
        { id: 8, name: "Water Bottle", category: "Sports", price: 24.99, rating: 4.0, inStock: true },
        { id: 9, name: "Blender", category: "Kitchen", price: 69.99, rating: 4.6, inStock: true },
        { id: 10, name: "Desk Lamp", category: "Electronics", price: 39.99, rating: 4.3, inStock: true },
        { id: 11, name: "Tennis Racket", category: "Sports", price: 149.99, rating: 4.5, inStock: false },
        { id: 12, name: "Toaster", category: "Kitchen", price: 34.99, rating: 4.1, inStock: true },
      ];

      setProducts(data);
      setStatus("success");
    }

    loadProducts();
  }, []);

  function handleRetry() {
    setProducts([]);
    setStatus("loading");

    // Re-trigger the effect by forcing a re-render
    setTimeout(() => {
      setProducts([
        { id: 1, name: "Wireless Headphones", category: "Electronics", price: 79.99, rating: 4.5, inStock: true },
        { id: 2, name: "Running Shoes", category: "Sports", price: 129.99, rating: 4.2, inStock: true },
        { id: 3, name: "Coffee Maker", category: "Kitchen", price: 49.99, rating: 4.7, inStock: false },
        { id: 4, name: "Yoga Mat", category: "Sports", price: 29.99, rating: 4.3, inStock: true },
        { id: 5, name: "Bluetooth Speaker", category: "Electronics", price: 59.99, rating: 4.1, inStock: true },
        { id: 6, name: "Chef's Knife", category: "Kitchen", price: 89.99, rating: 4.8, inStock: true },
        { id: 7, name: "Smart Watch", category: "Electronics", price: 199.99, rating: 4.4, inStock: false },
        { id: 8, name: "Water Bottle", category: "Sports", price: 24.99, rating: 4.0, inStock: true },
        { id: 9, name: "Blender", category: "Kitchen", price: 69.99, rating: 4.6, inStock: true },
        { id: 10, name: "Desk Lamp", category: "Electronics", price: 39.99, rating: 4.3, inStock: true },
        { id: 11, name: "Tennis Racket", category: "Sports", price: 149.99, rating: 4.5, inStock: false },
        { id: 12, name: "Toaster", category: "Kitchen", price: 34.99, rating: 4.1, inStock: true },
      ]);
      setStatus("success");
    }, 1500);
  }

  // Derived data: categories
  const categories = ["all", ...new Set(products.map((p) => p.category))];

  // Pipeline: filter → search → sort
  const processedProducts = (() => {
    let result = products;

    // Category filter
    if (selectedCategory !== "all") {
      result = result.filter((p) => p.category === selectedCategory);
    }

    // Search
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      result = result.filter(
        (p) =>
          p.name.toLowerCase().includes(term) ||
          p.category.toLowerCase().includes(term)
      );
    }

    // Sort
    const [field, direction] = sortBy.split("-");
    result = [...result].sort((a, b) => {
      let valA = a[field];
      let valB = b[field];
      if (typeof valA === "string") {
        valA = valA.toLowerCase();
        valB = valB.toLowerCase();
      }
      if (valA < valB) return direction === "asc" ? -1 : 1;
      if (valA > valB) return direction === "asc" ? 1 : -1;
      return 0;
    });

    return result;
  })();

  // Statistics
  const stats = {
    total: products.length,
    inStock: products.filter((p) => p.inStock).length,
    outOfStock: products.filter((p) => !p.inStock).length,
    avgPrice: products.length > 0
      ? (products.reduce((sum, p) => sum + p.price, 0) / products.length).toFixed(2)
      : "0.00",
  };

  // ── RENDER ────────────────────────────────────────────────

  if (status === "loading") {
    return (
      <div style={{ textAlign: "center", padding: "4rem" }}>
        <div
          style={{
            width: "50px",
            height: "50px",
            border: "4px solid #e2e8f0",
            borderTopColor: "#3182ce",
            borderRadius: "50%",
            margin: "0 auto 1rem",
            animation: "spin 1s linear infinite",
          }}
        />
        <p style={{ color: "#718096", fontSize: "1.125rem" }}>Loading products...</p>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div style={{ textAlign: "center", padding: "4rem" }}>
        <div style={{
          backgroundColor: "#fff5f5",
          border: "1px solid #fc8181",
          borderRadius: "12px",
          padding: "2rem",
          maxWidth: "400px",
          margin: "0 auto",
        }}>
          <h2 style={{ color: "#e53e3e", marginBottom: "0.5rem" }}>Oops!</h2>
          <p style={{ color: "#742a2a", marginBottom: "1rem" }}>{errorMessage}</p>
          <button
            onClick={handleRetry}
            style={{
              padding: "0.5rem 1.5rem",
              backgroundColor: "#e53e3e",
              color: "white",
              border: "none",
              borderRadius: "6px",
              cursor: "pointer",
              fontSize: "1rem",
            }}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: "960px", margin: "0 auto", padding: "1rem" }}>
      <h1 style={{ marginBottom: "0.5rem" }}>Product Dashboard</h1>

      {/* Stats bar */}
      <div style={{ display: "flex", gap: "1rem", marginBottom: "1.5rem", flexWrap: "wrap" }}>
        {[
          { label: "Total", value: stats.total, color: "#3182ce" },
          { label: "In Stock", value: stats.inStock, color: "#38a169" },
          { label: "Out of Stock", value: stats.outOfStock, color: "#e53e3e" },
          { label: "Avg Price", value: `$${stats.avgPrice}`, color: "#d69e2e" },
        ].map((stat) => (
          <div
            key={stat.label}
            style={{
              flex: 1,
              minWidth: "120px",
              padding: "1rem",
              backgroundColor: "#f7fafc",
              borderRadius: "8px",
              borderLeft: `4px solid ${stat.color}`,
            }}
          >
            <p style={{ color: "#718096", fontSize: "0.75rem", margin: "0 0 0.25rem 0", textTransform: "uppercase" }}>
              {stat.label}
            </p>
            <p style={{ fontSize: "1.5rem", fontWeight: "bold", margin: 0, color: "#2d3748" }}>
              {stat.value}
            </p>
          </div>
        ))}
      </div>

      {/* Controls */}
      <div style={{ display: "flex", gap: "0.75rem", marginBottom: "1rem", flexWrap: "wrap", alignItems: "center" }}>
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search products..."
          style={{ flex: 1, minWidth: "200px", padding: "0.5rem 0.75rem", border: "1px solid #e2e8f0", borderRadius: "6px" }}
        />
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          style={{ padding: "0.5rem", borderRadius: "6px", border: "1px solid #e2e8f0" }}
        >
          {categories.map((cat) => (
            <option key={cat} value={cat}>
              {cat === "all" ? "All Categories" : cat}
            </option>
          ))}
        </select>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          style={{ padding: "0.5rem", borderRadius: "6px", border: "1px solid #e2e8f0" }}
        >
          <option value="name-asc">Name A-Z</option>
          <option value="name-desc">Name Z-A</option>
          <option value="price-asc">Price Low-High</option>
          <option value="price-desc">Price High-Low</option>
          <option value="rating-asc">Rating Low-High</option>
          <option value="rating-desc">Rating High-Low</option>
        </select>

        {/* View toggle */}
        <div style={{ display: "flex", border: "1px solid #e2e8f0", borderRadius: "6px", overflow: "hidden" }}>
          <button
            onClick={() => setView("grid")}
            style={{
              padding: "0.5rem 0.75rem",
              border: "none",
              backgroundColor: view === "grid" ? "#3182ce" : "white",
              color: view === "grid" ? "white" : "#4a5568",
              cursor: "pointer",
            }}
          >
            Grid
          </button>
          <button
            onClick={() => setView("list")}
            style={{
              padding: "0.5rem 0.75rem",
              border: "none",
              borderLeft: "1px solid #e2e8f0",
              backgroundColor: view === "list" ? "#3182ce" : "white",
              color: view === "list" ? "white" : "#4a5568",
              cursor: "pointer",
            }}
          >
            List
          </button>
        </div>
      </div>

      {/* Results count */}
      <p style={{ color: "#718096", fontSize: "0.875rem", marginBottom: "1rem" }}>
        Showing {processedProducts.length} of {products.length} products
        {(searchTerm || selectedCategory !== "all") && (
          <button
            onClick={() => { setSearchTerm(""); setSelectedCategory("all"); }}
            style={{
              marginLeft: "0.5rem",
              padding: "0.125rem 0.5rem",
              backgroundColor: "transparent",
              border: "1px solid #cbd5e0",
              borderRadius: "4px",
              cursor: "pointer",
              fontSize: "0.75rem",
              color: "#718096",
            }}
          >
            Clear filters
          </button>
        )}
      </p>

      {/* Product display */}
      {processedProducts.length === 0 ? (
        <div style={{
          textAlign: "center",
          padding: "3rem",
          backgroundColor: "#f7fafc",
          borderRadius: "8px",
          border: "2px dashed #cbd5e0",
        }}>
          <p style={{ fontSize: "1.125rem", color: "#718096" }}>
            No products match your criteria.
          </p>
        </div>
      ) : view === "grid" ? (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: "1rem" }}>
          {processedProducts.map((product) => (
            <div
              key={product.id}
              style={{
                border: "1px solid #e2e8f0",
                borderRadius: "8px",
                padding: "1rem",
                opacity: product.inStock ? 1 : 0.6,
                position: "relative",
              }}
            >
              {!product.inStock && (
                <span style={{
                  position: "absolute",
                  top: "0.5rem",
                  right: "0.5rem",
                  backgroundColor: "#e53e3e",
                  color: "white",
                  padding: "0.125rem 0.5rem",
                  borderRadius: "4px",
                  fontSize: "0.625rem",
                  textTransform: "uppercase",
                  fontWeight: "bold",
                }}>
                  Out of Stock
                </span>
              )}
              <span style={{ fontSize: "0.75rem", color: "#718096", textTransform: "uppercase" }}>
                {product.category}
              </span>
              <h3 style={{ margin: "0.25rem 0", fontSize: "1rem" }}>{product.name}</h3>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "0.5rem" }}>
                <span style={{ fontWeight: "bold", fontSize: "1.25rem" }}>${product.price.toFixed(2)}</span>
                <span style={{ color: "#d69e2e", fontSize: "0.875rem" }}>
                  {"★".repeat(Math.floor(product.rating))} {product.rating}
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
          {processedProducts.map((product) => (
            <div
              key={product.id}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "1rem",
                padding: "0.75rem 1rem",
                border: "1px solid #e2e8f0",
                borderRadius: "8px",
                opacity: product.inStock ? 1 : 0.6,
              }}
            >
              <div style={{ flex: 1 }}>
                <strong>{product.name}</strong>
                <span style={{ color: "#718096", fontSize: "0.875rem", marginLeft: "0.5rem" }}>
                  {product.category}
                </span>
              </div>
              <span style={{ color: "#d69e2e", fontSize: "0.875rem", minWidth: "70px" }}>
                {"★".repeat(Math.floor(product.rating))} {product.rating}
              </span>
              <span style={{ fontWeight: "bold", minWidth: "80px", textAlign: "right" }}>
                ${product.price.toFixed(2)}
              </span>
              {!product.inStock && (
                <span style={{
                  backgroundColor: "#fed7d7",
                  color: "#e53e3e",
                  padding: "0.125rem 0.5rem",
                  borderRadius: "4px",
                  fontSize: "0.625rem",
                  textTransform: "uppercase",
                  fontWeight: "bold",
                }}>
                  Out of Stock
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ProductDashboard;
```

**Concepts combined in this project:**

| Concept | Where Used |
|---------|------------|
| Status pattern | `loading` → `error` → `success` |
| Error state with retry | Error screen with Retry button |
| Empty state | "No products match" message |
| Search filtering | Text input filtering by name and category |
| Category filtering | Dropdown filter |
| Sorting | Dropdown with field + direction |
| Derived data | Stats, categories, processedProducts |
| Conditional styling | Opacity for out-of-stock, active view button |
| View switching | Grid vs List view (enum pattern) |
| Conditional badges | "Out of Stock" badge with `&&` |
| map() with keys | Product lists in both grid and list views |
| Rendering lists of stats | Stats bar uses map() on an array of objects |

---

## Common Mistakes

1. **Not handling all states — loading, error, empty, and success.**

   ```jsx
   // ❌ Only handles success — blank screen while loading, crash on error
   function UserList() {
     const [users, setUsers] = useState([]);
     return <ul>{users.map(...)}</ul>;
   }

   // ✅ Handle every state
   if (isLoading) return <Spinner />;
   if (error) return <ErrorMessage />;
   if (users.length === 0) return <EmptyState />;
   return <ul>{users.map(...)}</ul>;
   ```

2. **Using deeply nested ternaries instead of early returns or enum patterns.**

   ```jsx
   // ❌ Unreadable
   return isLoading ? <Spinner /> : error ? <Error /> : data.length === 0 ? <Empty /> : <List />;

   // ✅ Clear
   if (isLoading) return <Spinner />;
   if (error) return <Error />;
   if (data.length === 0) return <Empty />;
   return <List />;
   ```

3. **Mutating arrays when sorting or filtering.**

   ```jsx
   // ❌ Mutates the original array
   const sorted = products.sort((a, b) => a.price - b.price);

   // ✅ Creates a copy first
   const sorted = [...products].sort((a, b) => a.price - b.price);
   ```

4. **Storing derived state instead of computing it.**

   ```jsx
   // ❌ Storing filtered results in state (duplicate data)
   const [searchTerm, setSearchTerm] = useState("");
   const [filteredProducts, setFilteredProducts] = useState(products);

   // ✅ Compute it on each render (single source of truth)
   const filteredProducts = products.filter(p => p.name.includes(searchTerm));
   ```

5. **Calling `.map()` on potentially undefined data.**

   ```jsx
   // ❌ Crashes if data is undefined
   {data.map(item => <li key={item.id}>{item.name}</li>)}

   // ✅ Default to empty array
   {(data || []).map(item => <li key={item.id}>{item.name}</li>)}
   // Or use default parameter: function List({ data = [] })
   ```

6. **Showing an empty list instead of an empty state message.**

   ```jsx
   // ❌ Renders an empty <ul> — confusing for users
   <ul>{filteredItems.map(...)}</ul>

   // ✅ Show a message when empty
   {filteredItems.length === 0
     ? <p>No items match your search.</p>
     : <ul>{filteredItems.map(...)}</ul>
   }
   ```

---

## Best Practices

1. **Always handle loading, error, and empty states.** This is non-negotiable for professional UIs. A blank screen is never an acceptable loading state.

2. **Use the status pattern** (`"idle" | "loading" | "error" | "success"`) instead of multiple boolean flags. It prevents impossible states and makes the code easier to reason about.

3. **Use early returns** for status checks. They keep code flat and readable:

   ```jsx
   if (status === "loading") return <Spinner />;
   if (status === "error") return <ErrorMessage />;
   // Main render here
   ```

4. **Compute derived data, do not store it.** If a value can be calculated from existing state, calculate it on each render instead of storing it in a separate state variable.

5. **Never mutate arrays.** Always use `[...array].sort()`, `array.filter()`, `array.map()` — methods that return new arrays.

6. **Use the enum/object map pattern** for multi-view components instead of nested ternaries or long if/else chains.

7. **Provide actionable empty states.** When a list is empty, do not just say "No results" — give the user a way to fix it (clear filters, add an item, try a different search).

8. **Use `??` for nullable values and `||` for falsy defaults.** Know the difference: `0 ?? "fallback"` keeps `0`, but `0 || "fallback"` replaces it.

9. **Show what is happening.** When an async action is in progress (deleting, saving, loading), give visual feedback on the specific item being affected, not just a global spinner.

---

## Summary

In this chapter, you learned:

- The **three states of data** (loading, error, success) and how to handle all of them.
- The **status pattern** — using a single `status` variable instead of multiple booleans to eliminate impossible states.
- The **enum/object map pattern** for cleanly rendering different views based on a state value.
- How to build **searchable lists** with real-time filtering.
- How to build **sortable lists** with toggling sort direction.
- How to **combine search, filter, and sort** in a data pipeline.
- How to render **nested and hierarchical data** using recursive components.
- How to handle **edge cases** with `||`, `??`, optional chaining (`?.`), and guard clauses.
- The **pending UI pattern** — showing per-item loading states instead of global spinners.
- Techniques for **conditional CSS classes** using string concatenation, template literals, and array filtering.
- The difference between **rendering nothing** (`return null`) and rendering an empty element.
- How to build a complete **Product Dashboard** that combines all these patterns.

---

## Interview Questions

**Q1: How do you handle loading, error, and empty states in a React component?**

Use a status pattern with a single variable (`"idle" | "loading" | "error" | "success"`) rather than multiple booleans. In the render, use early returns to handle each state: return a loading spinner for "loading", an error message for "error", and check for empty data before rendering the list. This ensures every possible state has a clear UI and prevents impossible combinations (like being in both loading and error state simultaneously).

**Q2: What is the difference between derived state and duplicated state? Why does it matter?**

Derived state is data that is calculated from existing state on each render (e.g., filtering an array based on a search term). Duplicated state is storing that calculated result in a separate state variable. Duplicated state is problematic because it creates two sources of truth that can get out of sync — you must remember to update both whenever either changes. Derived state is computed fresh on every render, guaranteeing consistency. The rule: if a value can be calculated from existing state and props, do not store it in state.

**Q3: Why should you never call `.sort()` directly on a state array in React?**

The `.sort()` method mutates the original array rather than creating a new one. In React, state should never be mutated directly — React uses reference equality to detect changes, so mutating an array does not trigger a re-render (React does not know the array changed). Always create a copy first with the spread operator (`[...array].sort(...)`) or `array.slice().sort(...)`. This returns a new array, which React recognizes as a state change.

**Q4: What is the enum/object map pattern for conditional rendering?**

Instead of using nested ternaries or long if/else chains, create an object where keys are possible state values and values are the corresponding JSX to render. For example: `const views = { profile: <Profile />, settings: <Settings />, billing: <Billing /> };` Then render with `{views[activeView]}`. This scales cleanly, makes the mapping explicit, and avoids complex conditional logic. It is particularly useful for tabbed interfaces, multi-step forms, and any component with multiple distinct views.

**Q5: What is the difference between `||` and `??` in JavaScript, and when would you use each in React?**

`||` (logical OR) returns the right side for any falsy left side (`false`, `0`, `""`, `null`, `undefined`). `??` (nullish coalescing) returns the right side only for `null` or `undefined`. In React, use `??` when `0` or `""` are valid values that should not trigger the fallback — for example, displaying a user's score where `0` is a legitimate value: `{user.score ?? "No score"}` shows `0` if the score is zero, while `{user.score || "No score"}` would incorrectly show "No score" for a zero score.

**Q6: How would you implement a searchable, filterable, sortable list in React?**

Use a data pipeline approach: start with the full data array, apply filters in sequence, then sort the result. Store only the control values in state (search term, selected filter, sort field/direction) — not the filtered results. On each render, compute: `filteredByCategory → filteredBySearch → sorted`. This keeps state minimal and ensures the displayed data always reflects the current controls. Always create a copy before sorting (`[...filtered].sort(...)`) and handle the empty result case with a message.

**Q7: How do you safely render data that might be null or undefined?**

Use defensive patterns: guard clauses (`if (!data) return <Fallback />`), optional chaining (`data?.property?.nested`), nullish coalescing (`data ?? defaultValue`), and default parameters (`function Component({ items = [] })`). For arrays, ensure the value is an array before calling `.map()` with `(items || []).map(...)`. For deeply nested objects, chain optional access: `user?.address?.city ?? "Unknown"`. Always consider what happens when any piece of data is missing.

**Q8: What is a recursive component? When would you use one?**

A recursive component is a component that renders itself as part of its output. It is used for tree-structured data: comment threads with replies, file directories, nested menus, organizational charts, or any data where items contain children of the same type. The component renders the current item, then maps over its children and renders itself for each child, incrementing a depth counter. Include a termination condition (no children or maximum depth reached) to prevent infinite recursion.

---

## Practice Exercises

**Exercise 1: Status Handler Component**

Create a reusable `StatusHandler` component that:
- Accepts `status` ("idle", "loading", "error", "success"), `error` (string), and `children` props
- Renders a spinner for loading, an error message for error (with a retry button), and the children for success
- Accepts custom messages for each state via props
- Test it with a simulated API call

**Exercise 2: Multi-Column Sortable Table**

Create a table component that:
- Displays an array of objects with at least 5 columns
- Clicking any column header sorts by that column
- Clicking the same column toggles sort direction
- Shows sort direction arrows in the header
- Highlights the currently sorted column
- Works with strings, numbers, and dates

**Exercise 3: Tag Cloud with Filtering**

Build a tag cloud component where:
- Display a set of tags as clickable chips/pills
- Clicking a tag toggles it as a filter
- Show a list of items, filtered by ALL selected tags (items must have all selected tags)
- Show selected tags above the list with "x" buttons to remove them
- Show item count that matches the current filter
- Include a "Clear all filters" button

**Exercise 4: Nested File Tree**

Create a file tree component that:
- Renders a recursive folder/file structure
- Folders can be expanded/collapsed by clicking
- Files and folders have different icons (text-based: 📁 📄)
- Tracks which item is selected (highlighted)
- Shows the full path of the selected item
- Data structure: `{ name: string, type: "file" | "folder", children?: Array }`

**Exercise 5: Data Dashboard with Tabs**

Build a dashboard with:
- Three tabs: "Overview", "Details", "Analytics"
- Use the enum pattern for tab content
- Overview shows summary cards (count, average, min, max)
- Details shows a searchable/sortable table
- Analytics shows a text-based bar chart of the data
- All tabs share the same underlying data
- Handle loading state with a skeleton UI (gray placeholder boxes instead of a spinner)

**Exercise 6: Infinite Scroll Simulation**

Create a component that:
- Initially shows 10 items from a list of 100
- Has a "Load More" button at the bottom
- Each click loads 10 more items
- Shows "Loading more..." state briefly (simulate with setTimeout)
- Disables the button while loading
- Hides the button when all items are loaded
- Shows "Showing X of Y items" counter

---

## What Is Next?

You now have a complete toolkit for building data-driven, stateful, interactive UIs in React. You can handle every state of data, build complex filtered and sorted lists, render hierarchical data, and provide polished user experiences with proper loading, error, and empty states.

In Chapter 8, we will dive into **useEffect and the Component Lifecycle** — understanding how to perform side effects like API calls, subscriptions, timers, and DOM interactions. This is where React starts connecting to the outside world.
