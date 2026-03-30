# Chapter 22: Best Practices for Clean React Code

In the last chapter, we learned what NOT to do. Now let us learn what TO do. This chapter is about habits that will make your React code clean, readable, and professional.

"Clean code" does not mean fancy code. It means code that is easy to read, easy to understand, and easy to change. Clean code is like a well-organized kitchen. Everything has a place. You can find what you need quickly. Someone new can walk in and understand where things are.

These best practices come from years of experience from thousands of React developers. You do not need to follow every single one from day one. Start with a few that make sense to you. Over time, they will become natural habits.

---

## What You Will Learn

- How to keep your components small and focused
- How to name things clearly
- How to organize your files and folders
- How to write code that other people (and future you) can understand
- Habits that separate beginners from professionals

## Why This Chapter Matters

Writing code that works is the first step. Writing code that is clean and organized is the next step. Clean code is easier to fix when bugs appear. Clean code is easier to add new features to. And if you ever work on a team, clean code is a gift to your teammates. It says, "I care about making this easy for everyone."

---

## Best Practice 1: Keep Components Small

### The Problem

Beginners often put everything into one big component. The component grows and grows until it is hundreds of lines long. It becomes hard to read, hard to understand, and hard to fix.

### The Rule

If your component is longer than about 50 to 100 lines, it is probably doing too much. Split it into smaller components.

### Example: A Big Component

```jsx
// This component is doing too many things
function UserDashboard() {
  const [user, setUser] = useState(null);
  const [posts, setPosts] = useState([]);
  const [notifications, setNotifications] = useState([]);

  // ... lots of useEffect calls, handlers, and logic ...

  return (
    <div>
      <div className="header">
        <img src={user.avatar} alt="Avatar" />
        <h1>{user.name}</h1>
        <p>{user.bio}</p>
      </div>
      <div className="posts">
        <h2>Recent Posts</h2>
        {posts.map((post) => (
          <div key={post.id}>
            <h3>{post.title}</h3>
            <p>{post.content}</p>
          </div>
        ))}
      </div>
      <div className="notifications">
        <h2>Notifications</h2>
        {notifications.map((notif) => (
          <div key={notif.id}>
            <p>{notif.message}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### Better: Split Into Smaller Components

```jsx
function UserDashboard() {
  const [user, setUser] = useState(null);
  const [posts, setPosts] = useState([]);
  const [notifications, setNotifications] = useState([]);

  return (
    <div>
      <UserHeader user={user} />
      <PostList posts={posts} />
      <NotificationList notifications={notifications} />
    </div>
  );
}

function UserHeader({ user }) {
  return (
    <div className="header">
      <img src={user.avatar} alt="Avatar" />
      <h1>{user.name}</h1>
      <p>{user.bio}</p>
    </div>
  );
}

function PostList({ posts }) {
  return (
    <div className="posts">
      <h2>Recent Posts</h2>
      {posts.map((post) => (
        <PostItem key={post.id} post={post} />
      ))}
    </div>
  );
}

function PostItem({ post }) {
  return (
    <div>
      <h3>{post.title}</h3>
      <p>{post.content}</p>
    </div>
  );
}
```

Each component now has one job. `UserHeader` shows the user's information. `PostList` shows the list of posts. `PostItem` shows a single post. This is much easier to read and maintain.

### How to Know When to Split

Ask yourself: "Can I describe what this component does in one sentence?" If you need the word "and" in your description, the component might be doing too much.

- "This component shows the user profile." (Good -- one job.)
- "This component shows the user profile AND lists their posts AND shows notifications." (Too many jobs. Split it.)

---

## Best Practice 2: Name Components Clearly

### The Rule

Name your components based on **what they are**, not what they do. Use nouns, not verbs.

### Examples

| Bad Name | Good Name | Why |
|----------|-----------|-----|
| `ShowUser` | `UserCard` | It is a card that shows user info |
| `DoSearch` | `SearchBar` | It is a search bar |
| `HandleLogin` | `LoginForm` | It is a login form |
| `FetchData` | `ProductList` | It is a list of products |
| `RenderItem` | `TodoItem` | It is a single todo item |

### Why This Matters

When you read JSX that uses well-named components, it reads almost like a description of the page:

```jsx
<div>
  <NavigationBar />
  <UserProfile />
  <RecentOrders />
  <Footer />
</div>
```

You can immediately understand what this page shows, even without looking at the component code.

---

## Best Practice 3: One Component Per File

### The Rule

Put each component in its own file. Name the file the same as the component.

### Example

```
src/
  components/
    Header.js        (contains the Header component)
    Footer.js        (contains the Footer component)
    UserCard.js      (contains the UserCard component)
    SearchBar.js     (contains the SearchBar component)
```

### Why This Matters

When you need to find a component, you know exactly which file to open. If `UserCard` has a bug, you open `UserCard.js`. Simple.

### Exception

Very small, closely related components can share a file. For example, an `Icon` component that is only used inside a `Button` component could live in the same file as `Button`. But when in doubt, use separate files.

---

## Best Practice 4: Destructure Props

### The Rule

Instead of using `props.name` and `props.age`, pull out the values at the top of your component. This is called "destructuring." It means taking things out of a container and giving them their own names.

### Example

```jsx
// Without destructuring - harder to read
function UserCard(props) {
  return (
    <div>
      <h2>{props.name}</h2>
      <p>Age: {props.age}</p>
      <p>Email: {props.email}</p>
    </div>
  );
}

// With destructuring - cleaner
function UserCard({ name, age, email }) {
  return (
    <div>
      <h2>{name}</h2>
      <p>Age: {age}</p>
      <p>Email: {email}</p>
    </div>
  );
}
```

### Why This Matters

Destructuring gives you two benefits:

1. **Less typing.** You write `name` instead of `props.name` throughout the component.
2. **Quick understanding.** By looking at the function signature `{ name, age, email }`, you immediately know what props this component needs.

---

## Best Practice 5: Keep State as Simple as Possible

### The Rule

Store the minimum amount of information in state. Do not store things that can be calculated from other state values.

### Example

```jsx
// BAD - storing things that can be calculated
function ShoppingCart() {
  const [items, setItems] = useState([]);
  const [itemCount, setItemCount] = useState(0);   // Can be calculated!
  const [totalPrice, setTotalPrice] = useState(0);  // Can be calculated!

  function addItem(item) {
    const newItems = [...items, item];
    setItems(newItems);
    setItemCount(newItems.length);              // Extra work
    setTotalPrice(newItems.reduce((sum, i) => sum + i.price, 0)); // Extra work
  }
}

// GOOD - calculate values from state
function ShoppingCart() {
  const [items, setItems] = useState([]);

  const itemCount = items.length;                            // Calculated
  const totalPrice = items.reduce((sum, i) => sum + i.price, 0); // Calculated

  function addItem(item) {
    setItems([...items, item]); // Only update one thing
  }
}
```

### Why This Matters

When you store values that can be calculated, you need to keep them in sync. If you update `items` but forget to update `itemCount`, your app shows wrong information. By calculating values from state, they are always correct.

Think of it like a clock. You only need to store the current time. You do not need to store "is it morning?" separately. You can always figure that out from the time.

---

## Best Practice 6: Lift State Only When Needed

### The Rule

Keep state in the lowest component that needs it. Only move state up to a parent component when two or more children need to share it.

### Example

If only the `SearchBar` needs to know what the user typed, keep the state in `SearchBar`.

```jsx
// Good - state stays where it is needed
function SearchBar() {
  const [query, setQuery] = useState("");

  return (
    <input
      value={query}
      onChange={(e) => setQuery(e.target.value)}
      placeholder="Search..."
    />
  );
}
```

If both `SearchBar` and `ResultsList` need the search query, then lift the state up to the parent.

```jsx
// Lift state to parent because two children need it
function SearchPage() {
  const [query, setQuery] = useState("");

  return (
    <div>
      <SearchBar query={query} onQueryChange={setQuery} />
      <ResultsList query={query} />
    </div>
  );
}
```

### Why This Matters

If you put all your state at the top of your app, every state change causes the entire app to re-render. This is slow and unnecessary. Keep state close to where it is used.

---

## Best Practice 7: Use Meaningful Variable Names

### The Rule

Variable names should describe what the variable holds. Someone reading your code should understand it without guessing.

### Examples

```jsx
// BAD - unclear names
const [d, setD] = useState([]);
const [flag, setFlag] = useState(false);
const [val, setVal] = useState("");
const [x, setX] = useState(0);

// GOOD - descriptive names
const [users, setUsers] = useState([]);
const [isMenuOpen, setIsMenuOpen] = useState(false);
const [searchQuery, setSearchQuery] = useState("");
const [cartItemCount, setCartItemCount] = useState(0);
```

### Naming Conventions

| Type | Convention | Examples |
|------|-----------|----------|
| Boolean state | Start with `is`, `has`, or `should` | `isLoading`, `hasError`, `shouldRefresh` |
| Arrays | Use plural nouns | `users`, `products`, `messages` |
| Single items | Use singular nouns | `user`, `product`, `message` |
| Event handlers | Start with `handle` | `handleClick`, `handleSubmit`, `handleChange` |
| Functions passed as props | Start with `on` | `onClick`, `onSubmit`, `onChange` |

---

## Best Practice 8: Keep JSX Clean

### The Rule

If your JSX has complex logic, extract it into variables above the return statement.

### Example

```jsx
// MESSY - logic mixed into JSX
function UserGreeting({ user, notifications }) {
  return (
    <div>
      <h1>
        Hello, {user.firstName} {user.lastName}
        {user.role === "admin" ? " (Administrator)" : ""}!
      </h1>
      <p>
        You have {notifications.filter((n) => !n.read).length} unread
        {notifications.filter((n) => !n.read).length === 1
          ? " notification"
          : " notifications"}
      </p>
    </div>
  );
}

// CLEAN - logic extracted into variables
function UserGreeting({ user, notifications }) {
  const fullName = `${user.firstName} ${user.lastName}`;
  const roleLabel = user.role === "admin" ? " (Administrator)" : "";
  const unreadCount = notifications.filter((n) => !n.read).length;
  const notificationWord = unreadCount === 1 ? "notification" : "notifications";

  return (
    <div>
      <h1>Hello, {fullName}{roleLabel}!</h1>
      <p>You have {unreadCount} unread {notificationWord}</p>
    </div>
  );
}
```

### Why This Matters

The second version is much easier to read. Each variable has a clear name. The JSX is simple and focused on structure, not logic.

---

## Best Practice 9: Use Constants for Magic Numbers and Strings

### The Rule

A "magic number" is a number in your code with no explanation. A "magic string" is the same idea but with text. Replace them with named constants.

### Example

```jsx
// BAD - what does 5 mean? What does "admin" mean here?
function UserList({ users }) {
  const displayedUsers = users.slice(0, 5);
  const isAdmin = user.role === "admin";
}

// GOOD - constants explain the meaning
const MAX_DISPLAYED_USERS = 5;
const ROLE_ADMIN = "admin";

function UserList({ users }) {
  const displayedUsers = users.slice(0, MAX_DISPLAYED_USERS);
  const isAdmin = user.role === ROLE_ADMIN;
}
```

### Why This Matters

If you need to change the maximum number of displayed users, you change it in one place. You do not have to search your entire codebase for the number 5. The constant name also tells you WHY the number 5 is there.

---

## Best Practice 10: Write Comments for Tricky Parts

### The Rule

You do not need to comment every line. But when you do something that might confuse someone (or future you), add a short comment explaining WHY.

### Example

```jsx
function PriceDisplay({ price, discount }) {
  // We round to 2 decimal places to avoid floating-point issues
  // like 19.99 * 0.1 = 1.9990000000000002
  const discountAmount = Math.round(price * discount * 100) / 100;

  const finalPrice = price - discountAmount;

  return <p>Final price: ${finalPrice.toFixed(2)}</p>;
}
```

### Comments to Avoid

Do not write comments that just repeat what the code says.

```jsx
// BAD comments - they add no value
const [count, setCount] = useState(0); // Set count to 0
setCount(count + 1); // Add 1 to count
return <p>Hello</p>; // Return a paragraph
```

### Good Comments Explain "Why," Not "What"

```jsx
// GOOD comments
// Using index as key here because items never reorder or delete
{staticItems.map((item, index) => (
  <li key={index}>{item}</li>
))}

// Debounce search to avoid too many API calls while user types
useEffect(() => {
  const timer = setTimeout(() => searchAPI(query), 300);
  return () => clearTimeout(timer);
}, [query]);
```

---

## Best Practice 11: Organize Your Folder Structure

### The Rule

As your project grows, organize your files into folders that make sense. There is no single "correct" structure, but here is a simple one that works well for beginners.

### Recommended Structure

```
src/
  components/          (Reusable UI pieces)
    Header.js
    Footer.js
    Button.js
  pages/               (Full pages of your app)
    HomePage.js
    AboutPage.js
    ProfilePage.js
  hooks/               (Custom hooks)
    useLocalStorage.js
  utils/               (Helper functions)
    formatDate.js
    calculateTotal.js
  constants/           (Constants and config)
    apiUrls.js
    roles.js
  App.js
  index.js
```

### What Each Folder Means

- **components/**: Small, reusable pieces. A `Button` can be used on many pages.
- **pages/**: Bigger components that represent entire pages. A `HomePage` is only used once.
- **hooks/**: Custom hooks that you create to reuse logic.
- **utils/**: Helper functions that are not React components. Things like formatting dates or doing math.
- **constants/**: Values that never change, like API URLs or role names.

### Why This Matters

When your project has 5 files, organization does not matter much. When your project has 50 or 100 files, good organization saves you a lot of time. You always know where to find things.

---

## Best Practice 12: Follow the DRY Principle

### The Rule

DRY stands for "Don't Repeat Yourself." If you find yourself writing the same code in multiple places, extract it into a reusable component or function.

### Example

```jsx
// REPETITIVE - the same card structure appears three times
function Dashboard() {
  return (
    <div>
      <div className="card">
        <h2>Users</h2>
        <p className="stat">1,234</p>
      </div>
      <div className="card">
        <h2>Orders</h2>
        <p className="stat">567</p>
      </div>
      <div className="card">
        <h2>Revenue</h2>
        <p className="stat">$89,012</p>
      </div>
    </div>
  );
}

// DRY - extract the repeated pattern into a component
function StatCard({ title, value }) {
  return (
    <div className="card">
      <h2>{title}</h2>
      <p className="stat">{value}</p>
    </div>
  );
}

function Dashboard() {
  return (
    <div>
      <StatCard title="Users" value="1,234" />
      <StatCard title="Orders" value="567" />
      <StatCard title="Revenue" value="$89,012" />
    </div>
  );
}
```

### Why This Matters

If you need to change the card design, you change it in one place (`StatCard`), and every card updates. Without DRY, you would have to change every single card by hand.

---

## Best Practice 13: Format Your Code Consistently

### The Rule

Use the same formatting style everywhere. This includes indentation (spaces or tabs), where you put curly braces, and how you write your imports.

### Use a Code Formatter

The easiest way to format code consistently is to use a tool called **Prettier**. Prettier automatically formats your code when you save a file.

### How to Set Up Prettier

1. Install it in your project:

```bash
npm install --save-dev prettier
```

2. Create a `.prettierrc` file in your project root:

```json
{
  "semi": true,
  "singleQuote": false,
  "tabWidth": 2,
  "trailingComma": "es5"
}
```

This tells Prettier:
- `semi: true` -- Add semicolons at the end of lines.
- `singleQuote: false` -- Use double quotes for strings.
- `tabWidth: 2` -- Use 2 spaces for indentation.
- `trailingComma: "es5"` -- Add commas after the last item in lists.

3. Most code editors (like VS Code) can run Prettier automatically when you save a file. Search for "Prettier" in your editor's extensions and install it.

### Why This Matters

Consistent formatting makes code easier to read. When everyone on a team uses the same formatting, you spend time thinking about logic, not about where to put spaces.

---

## Best Practice 14: Learn to Read Error Messages

### The Rule

Error messages are your friends, not your enemies. They tell you exactly what went wrong and where. Learning to read them is one of the most valuable skills you can develop.

### How to Read a React Error Message

Most error messages have three parts:

1. **The type of error** (what kind of problem)
2. **The description** (what happened)
3. **The stack trace** (where it happened)

### Example

```
TypeError: Cannot read properties of undefined (reading 'name')
    at UserCard (UserCard.js:8:22)
    at App (App.js:12:5)
```

Let us break this down:

- **TypeError**: The type of error. A `TypeError` means you tried to use a value in a way that does not work for its type.
- **Cannot read properties of undefined (reading 'name')**: You tried to read `.name` from something that is `undefined`. In other words, the variable does not have a value yet.
- **at UserCard (UserCard.js:8:22)**: The problem is in the `UserCard` component, in the file `UserCard.js`, on line 8, at position 22.

### Common Error Messages and What They Mean

| Error Message | What It Means |
|--------------|---------------|
| `X is not defined` | You used a variable name that does not exist. Check spelling. |
| `X is not a function` | You tried to call something that is not a function. Check the variable type. |
| `Cannot read properties of null` | You tried to read a property from `null`. The value is empty. |
| `Cannot read properties of undefined` | You tried to read a property from something that was never set. |
| `Invalid hook call` | You called a hook in the wrong place (not inside a component). |
| `Each child in a list should have a unique "key" prop` | You forgot to add keys to your list items. |

### What to Do When You See an Error

1. **Read the first line.** It tells you the type and description.
2. **Look at the file name and line number.** Go to that exact line in your code.
3. **Read the code on that line.** Think about what could be wrong.
4. **If you do not understand, copy the error message and search for it online.** Someone else has probably had the same problem.

---

## Quick Summary

| # | Best Practice | Key Idea |
|---|--------------|----------|
| 1 | Keep components small | Split when a component does too much |
| 2 | Name clearly | Use nouns that describe what it IS |
| 3 | One component per file | Easy to find, easy to manage |
| 4 | Destructure props | Cleaner code, clear expectations |
| 5 | Simple state | Do not store what you can calculate |
| 6 | Lift state only when needed | Keep state close to where it is used |
| 7 | Meaningful names | Names should describe the value |
| 8 | Clean JSX | Extract complex logic into variables |
| 9 | Named constants | Replace magic numbers and strings |
| 10 | Helpful comments | Explain why, not what |
| 11 | Organized folders | Group files by purpose |
| 12 | DRY | Do not repeat yourself |
| 13 | Consistent formatting | Use Prettier or similar tools |
| 14 | Read error messages | They are helpers, not enemies |

---

## Key Points to Remember

1. **Small components are easier to understand, test, and fix.** If your component needs the word "and" to describe it, split it.
2. **Good names save you time.** You will spend more time reading code than writing it. Clear names make reading faster.
3. **State should be minimal.** Store only what you must. Calculate everything else.
4. **Consistency matters more than perfection.** Pick a style and stick with it.
5. **Error messages are helpful clues.** Read them carefully. They usually point you to the exact problem.

---

## Practice Questions

1. How do you decide when a component is too big and needs to be split?

2. What is the difference between naming a component `ShowUser` and naming it `UserCard`? Which is better and why?

3. Why is it better to calculate `itemCount` from `items.length` instead of storing it as a separate state variable?

4. What is a "magic number" and why should you avoid using them?

5. What are the three parts of a typical error message?

---

## Exercises

### Exercise 1: Refactor a Big Component

Take this big component and split it into smaller ones.

```jsx
function ProductPage({ product }) {
  return (
    <div>
      <div className="product-image">
        <img src={product.image} alt={product.name} />
      </div>
      <div className="product-info">
        <h1>{product.name}</h1>
        <p className="price">${product.price}</p>
        <p className="description">{product.description}</p>
      </div>
      <div className="reviews">
        <h2>Reviews</h2>
        {product.reviews.map((review) => (
          <div key={review.id} className="review">
            <strong>{review.author}</strong>
            <p>{review.text}</p>
            <p>Rating: {review.rating}/5</p>
          </div>
        ))}
      </div>
    </div>
  );
}
```

Create `ProductImage`, `ProductInfo`, `ReviewList`, and `ReviewItem` components.

### Exercise 2: Clean Up Messy Code

Rewrite this code using the best practices from this chapter.

```jsx
function x({ d }) {
  const [f, setF] = useState(false);
  const [l, setL] = useState([]);
  const [c, setC] = useState(0);

  function z() {
    setF(!f);
  }

  return (
    <div>
      <h1>{d.n}</h1>
      <p>{d.items.length > 0 ? d.items.length + " items" : "No items"}</p>
      <button onClick={z}>{f ? "Hide" : "Show"} Details</button>
    </div>
  );
}
```

Rename the component and all variables to have clear, meaningful names.

### Exercise 3: Add Constants and Comments

Take this code and replace the magic numbers with named constants. Add helpful comments where appropriate.

```jsx
function PasswordValidator({ password }) {
  const isLongEnough = password.length >= 8;
  const hasNumber = /[0-9]/.test(password);

  if (password.length > 128) {
    return <p>Password is too long</p>;
  }

  return (
    <div>
      <p style={{ color: isLongEnough ? "green" : "red" }}>
        {isLongEnough ? "Length OK" : "Too short"}
      </p>
      <p style={{ color: hasNumber ? "green" : "red" }}>
        {hasNumber ? "Has a number" : "Needs a number"}
      </p>
    </div>
  );
}
```

---

## What Is Next?

You now know the common mistakes to avoid and the best practices to follow. In the next chapter, we will test your knowledge with interview-style questions. These are the kinds of questions that come up when you are applying for a job as a React developer. Even if you are not looking for a job, they are a great way to make sure you truly understand React.
