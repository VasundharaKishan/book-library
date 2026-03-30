# Chapter 16: Simple API Calling

---

## What You Will Learn

- What an API is and why it matters
- What JSON is and how to read it
- How to use the `fetch()` function to ask for data
- What `async` and `await` mean and how to use them
- How to handle loading, success, and error states
- How to fetch data when a component loads using `useEffect`
- How to display API data in a list
- How to handle errors gracefully
- How to build an app that fetches and displays random user profiles

## Why This Chapter Matters

Up until now, all the data in your apps has come from you, the developer. You typed the to-do items. You typed the names. You typed the fruits. But real applications get their data from the internet. When you open a weather app, it fetches the weather from a server. When you open Instagram, it fetches posts from a server. When you search on Google, it fetches results from a server.

This chapter teaches you how to connect your React app to the outside world. You will learn how to ask a server for data and display it. This is a huge step. After this chapter, your apps will feel like real applications.

---

## What Is an API?

API stands for **Application Programming Interface**. That is a big name, but the idea is simple.

### The Restaurant Analogy

Think of a restaurant. You (the customer) are sitting at a table. The kitchen is in the back, preparing food. You cannot go into the kitchen and cook your own food. You need someone in between.

That someone is the **waiter**.

- You look at the menu and tell the waiter what you want.
- The waiter goes to the kitchen and places your order.
- The kitchen prepares your food.
- The waiter brings the food back to you.

An API is like the waiter:

- **You** are the React app (the front end).
- **The kitchen** is the server (the back end), where data is stored.
- **The waiter** is the API. It takes your request to the server and brings back the data.

You do not need to know how the kitchen works. You just need to know how to talk to the waiter (the API). You make a request, and you get a response.

### What Kind of Data Do APIs Provide?

APIs can provide all kinds of data:

- Weather information
- News articles
- User profiles
- Product listings
- Movie information
- Stock prices
- Cat pictures (yes, there is an API for that)

There are thousands of free APIs on the internet that you can use to practice.

---

## What Is JSON?

When an API sends you data, it sends it in a specific format. The most common format is **JSON**, which stands for **JavaScript Object Notation**.

JSON looks a lot like JavaScript objects and arrays. Here is an example:

```json
{
  "name": "Sara",
  "age": 28,
  "city": "New York",
  "hobbies": ["reading", "coding", "hiking"]
}
```

You can read this easily, right? It has a name, an age, a city, and a list of hobbies. That is the beauty of JSON. It is structured in a way that both humans and computers can understand.

### JSON Rules

JSON has a few simple rules:

- **Keys must be in double quotes**: `"name"`, not `name` or `'name'`.
- **Strings must be in double quotes**: `"Sara"`, not `'Sara'`.
- **Numbers do not have quotes**: `28`, not `"28"`.
- **Booleans are `true` or `false`**: no quotes.
- **Arrays use square brackets**: `["a", "b", "c"]`.
- **Objects use curly braces**: `{ "key": "value" }`.

When your React app receives JSON from an API, JavaScript can easily turn it into a regular JavaScript object that you can work with.

---

## The fetch() Function

JavaScript has a built-in function called `fetch()` that lets you make requests to APIs. You give it a URL (the address of the API), and it goes out to the internet, asks for the data, and brings it back.

Here is the simplest possible fetch:

```jsx
fetch('https://jsonplaceholder.typicode.com/users/1')
  .then(response => response.json())
  .then(data => console.log(data));
```

This asks a free practice API for user number 1, converts the response to JSON, and logs it to the console.

But this syntax with `.then()` can get confusing, especially when you have many steps. There is a cleaner way to write it.

---

## async and await — A Simpler Way to Fetch

`async` and `await` are JavaScript features that make it easier to work with operations that take time (like fetching data from the internet).

### The Analogy

Imagine you order a coffee at a coffee shop.

- You place your order.
- You **wait** for the barista to make it.
- When it is ready, you take your coffee and move on.

That is exactly how `async/await` works:

- You make a request (fetch).
- You **await** the response (wait for the server to reply).
- When the response arrives, you use the data.

### How It Looks in Code

```jsx
async function getUser() {
  const response = await fetch('https://jsonplaceholder.typicode.com/users/1');
  const data = await response.json();
  console.log(data);
}
```

### Line-by-Line Explanation

```jsx
async function getUser() {
```

The `async` keyword before the function tells JavaScript: "This function will do something that takes time. It will use `await` inside."

```jsx
const response = await fetch('https://jsonplaceholder.typicode.com/users/1');
```

`fetch()` goes to the internet and asks the API for data. This takes time (maybe half a second, maybe a few seconds). The `await` keyword says: "Wait here until the data comes back. Do not move to the next line until it is ready."

The `response` is what the server sends back. It contains the data, but we need to extract it.

```jsx
const data = await response.json();
```

`response.json()` reads the response and converts it from raw text into a JavaScript object we can use. This also takes a moment, so we `await` it too.

```jsx
console.log(data);
```

Now `data` is a regular JavaScript object. We can access its properties like `data.name`, `data.email`, and so on.

---

## The Three States of Fetching Data

When your app fetches data, it goes through three stages. Think of ordering a package online:

1. **Loading**: You placed the order. The package is on its way. You see "Your order is being delivered."
2. **Success**: The package arrived! You open it and see your items.
3. **Error**: Something went wrong. The package got lost. You see "Delivery failed."

In your React app, you need to handle all three states:

```
Loading → Show "Loading..." or a spinner
Success → Show the data
Error   → Show an error message
```

Here is how to do this with state:

```jsx
const [data, setData] = useState(null);        // The fetched data
const [isLoading, setIsLoading] = useState(true);  // Are we still waiting?
const [error, setError] = useState(null);      // Did something go wrong?
```

---

## Fetching Data When a Component Loads

This is where `useEffect` meets `fetch`. We want to fetch data as soon as the component appears on the screen. That is a side effect, and we run it with `useEffect` and an empty dependency array.

```jsx
import { useState, useEffect } from 'react';

function UserProfile() {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchUser() {
      try {
        const response = await fetch(
          'https://jsonplaceholder.typicode.com/users/1'
        );

        if (!response.ok) {
          throw new Error('Something went wrong!');
        }

        const data = await response.json();
        setUser(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    }

    fetchUser();
  }, []);

  if (isLoading) {
    return <p>Loading...</p>;
  }

  if (error) {
    return <p>Error: {error}</p>;
  }

  return (
    <div>
      <h2>{user.name}</h2>
      <p>Email: {user.email}</p>
      <p>Phone: {user.phone}</p>
      <p>City: {user.address.city}</p>
    </div>
  );
}

export default UserProfile;
```

**What you will see while loading:**

```
Loading...
```

**What you will see after the data arrives:**

```
Leanne Graham
Email: Sincere@april.biz
Phone: 1-770-736-8031 x56442
City: Gwenborough
```

### Line-by-Line Explanation

```jsx
useEffect(() => {
  async function fetchUser() {
```

We cannot make the `useEffect` callback itself `async`. React does not allow that. Instead, we create an `async` function inside the effect and then call it.

```jsx
try {
```

`try` means "try to do the following code. If anything goes wrong, jump to the `catch` block." This is how we handle errors.

```jsx
const response = await fetch('https://jsonplaceholder.typicode.com/users/1');
```

We ask the API for user number 1. We wait for the response.

```jsx
if (!response.ok) {
  throw new Error('Something went wrong!');
}
```

`response.ok` is `true` if the server responded successfully (status code 200). If the server returned an error (like 404 Not Found or 500 Server Error), `response.ok` is `false`. In that case, we `throw` an error, which jumps to the `catch` block.

```jsx
const data = await response.json();
setUser(data);
```

We convert the response to JSON and store it in state.

```jsx
} catch (err) {
  setError(err.message);
}
```

If anything went wrong (network error, server error, bad JSON), we land here. We save the error message in state.

```jsx
} finally {
  setIsLoading(false);
}
```

`finally` runs no matter what, whether the fetch succeeded or failed. We set loading to `false` because either way, we are done waiting.

```jsx
fetchUser();
```

We call the function we just defined. This starts the fetch.

```jsx
}, []);
```

Empty dependency array. Fetch once when the component appears.

### Why We Check Three States in the Return

```jsx
if (isLoading) return <p>Loading...</p>;
if (error) return <p>Error: {error}</p>;
```

These are called **early returns**. They check the state before trying to display the data. If we did not check and tried to show `user.name` while `user` is still `null` (because the data has not arrived yet), we would get a crash.

---

## Displaying a List of Data from an API

Let us fetch a list of users and display them.

```jsx
import { useState, useEffect } from 'react';

function UserList() {
  const [users, setUsers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchUsers() {
      try {
        const response = await fetch(
          'https://jsonplaceholder.typicode.com/users'
        );

        if (!response.ok) {
          throw new Error('Failed to fetch users.');
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

  if (isLoading) return <p>Loading users...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div>
      <h2>User Directory</h2>
      <ul>
        {users.map(user => (
          <li key={user.id}>
            <strong>{user.name}</strong> — {user.email}
          </li>
        ))}
      </ul>
      <p>Total users: {users.length}</p>
    </div>
  );
}

export default UserList;
```

**What you will see:**

```
User Directory

- Leanne Graham — Sincere@april.biz
- Ervin Howell — Shanna@melissa.tv
- Clementine Bauch — Nathan@yesenia.net
  ... (10 users total)

Total users: 10
```

The pattern is the same as fetching a single user. The only difference is that the API returns an array instead of a single object, so we use `map` to render each user as a list item.

---

## Handling Errors Gracefully

Things can go wrong when fetching data. The internet might be slow. The server might be down. The API might have moved. Good applications handle these situations gracefully instead of crashing.

Here is a more user-friendly error handling approach:

```jsx
import { useState, useEffect } from 'react';

function PostViewer() {
  const [post, setPost] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  async function fetchPost() {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(
        'https://jsonplaceholder.typicode.com/posts/1'
      );

      if (!response.ok) {
        throw new Error('Could not load the post. Please try again.');
      }

      const data = await response.json();
      setPost(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    fetchPost();
  }, []);

  if (isLoading) {
    return <p>Loading post...</p>;
  }

  if (error) {
    return (
      <div>
        <p style={{ color: 'red' }}>Error: {error}</p>
        <button onClick={fetchPost}>Try Again</button>
      </div>
    );
  }

  return (
    <div>
      <h2>{post.title}</h2>
      <p>{post.body}</p>
    </div>
  );
}

export default PostViewer;
```

**What you will see if the fetch fails:**

```
Error: Could not load the post. Please try again.
[Try Again]
```

The "Try Again" button calls `fetchPost` again. This gives the user a way to retry without refreshing the entire page. Notice that we reset `isLoading` to `true` and `error` to `null` before retrying so the loading state shows again.

---

## Understanding the Full Fetch Pattern

Here is the pattern you will use over and over again. It is worth memorizing:

```
1. Set up three state variables: data, isLoading, error
2. Create an async function that fetches data
3. Inside the function:
   a. try to fetch
   b. check if the response is ok
   c. convert to JSON
   d. store in state
   e. catch any errors
   f. finally, set loading to false
4. Call the function inside useEffect with []
5. In the JSX:
   a. If loading, show a loading message
   b. If error, show an error message
   c. If data is ready, show the data
```

```
┌──────────────────────────────────────────┐
│         Component Renders                │
│                                          │
│  isLoading: true                         │
│  → Shows "Loading..."                   │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│      useEffect runs fetch()              │
│                                          │
│  Asks the API for data...               │
└──────────────┬───────────────────────────┘
               │
        ┌──────┴──────┐
        ▼             ▼
   ┌─────────┐  ┌──────────┐
   │ Success │  │  Error   │
   │         │  │          │
   │ setData │  │ setError │
   │ setLoad │  │ setLoad  │
   │  false  │  │  false   │
   └────┬────┘  └────┬─────┘
        │             │
        ▼             ▼
   ┌─────────┐  ┌──────────┐
   │ Shows   │  │ Shows    │
   │ the     │  │ error    │
   │ data    │  │ message  │
   └─────────┘  └──────────┘
```

---

## Mini Project: Random User Profiles

Let us build an app that fetches random user profiles from an API and displays them. You can click a button to load a new random user.

We will use the Random User API (`https://randomuser.me/api/`), which provides randomly generated user profiles including names, photos, locations, and more.

```jsx
import { useState, useEffect } from 'react';

function RandomUser() {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  async function fetchRandomUser() {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('https://randomuser.me/api/');

      if (!response.ok) {
        throw new Error('Failed to fetch user.');
      }

      const data = await response.json();
      setUser(data.results[0]);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    fetchRandomUser();
  }, []);

  if (isLoading) {
    return <p>Loading user profile...</p>;
  }

  if (error) {
    return (
      <div>
        <p style={{ color: 'red' }}>Error: {error}</p>
        <button onClick={fetchRandomUser}>Try Again</button>
      </div>
    );
  }

  return (
    <div style={{ textAlign: 'center', maxWidth: '400px', margin: '0 auto' }}>
      <h2>Random User Profile</h2>

      <img
        src={user.picture.large}
        alt={user.name.first}
        style={{ borderRadius: '50%', width: '150px', height: '150px' }}
      />

      <h3>
        {user.name.first} {user.name.last}
      </h3>

      <p>Email: {user.email}</p>
      <p>
        Location: {user.location.city}, {user.location.country}
      </p>
      <p>Phone: {user.phone}</p>

      <button onClick={fetchRandomUser} style={{ marginTop: '10px' }}>
        Load Another User
      </button>
    </div>
  );
}

export default RandomUser;
```

**What you will see while loading:**

```
Loading user profile...
```

**What you will see after the data arrives:**

```
         Random User Profile

         [Round Photo]

         Emma Johnson

Email: emma.johnson@example.com
Location: Dublin, Ireland
Phone: 041-232-5678

    [Load Another User]
```

Clicking "Load Another User" fetches a brand new random user from the API.

### How It Works

```jsx
const data = await response.json();
setUser(data.results[0]);
```

The Random User API wraps its data in an object with a `results` array. Even though we asked for one user, it comes inside an array. We take the first (and only) item with `[0]`.

```jsx
<img
  src={user.picture.large}
  alt={user.name.first}
  style={{ borderRadius: '50%', width: '150px', height: '150px' }}
/>
```

The API provides a photo URL in `user.picture.large`. We display it as a round image using `borderRadius: '50%'`.

```jsx
<button onClick={fetchRandomUser}>Load Another User</button>
```

This button calls the same `fetchRandomUser` function. It resets the loading state, makes a new request, and displays the new user. The entire flow (loading, success/error) happens again.

### Why We Define fetchRandomUser Outside of useEffect

In the previous examples, we defined the fetch function inside the effect. Here, we defined it outside so that both the `useEffect` and the button's `onClick` can call the same function. This avoids repeating code.

---

## Quick Summary

| Concept | What It Is |
|---|---|
| API | A service that lets your app request data from a server |
| JSON | A text format for structured data (looks like JavaScript objects) |
| `fetch()` | A built-in function to make HTTP requests |
| `async/await` | A way to write asynchronous code that reads like regular code |
| `response.ok` | `true` if the server responded with a success status |
| `response.json()` | Converts the raw response into a JavaScript object |
| `try/catch` | Handles errors gracefully instead of crashing |
| Loading state | Tells the user data is on its way |
| Error state | Tells the user something went wrong |
| `useEffect + fetch` | The standard way to load data when a component appears |

---

## Key Points to Remember

1. **Always handle three states: loading, success, and error.** Never assume the fetch will succeed. The internet is unpredictable.

2. **Use `async/await` inside `useEffect` by creating a separate function.** You cannot make the `useEffect` callback itself `async`. Define an `async` function inside and call it.

3. **Check `response.ok` before reading the data.** A `fetch` call does not throw an error for 404 or 500 responses. You need to check manually.

4. **Use try/catch/finally for error handling.** `try` attempts the fetch. `catch` handles errors. `finally` always runs (good for setting loading to false).

5. **Start with `isLoading: true` and set it to `false` when done.** This way, the loading message shows while the data is being fetched, and it disappears when the data arrives or an error occurs.

---

## Practice Questions

1. What is an API? Explain it using your own analogy (not the restaurant one from this chapter).

2. What is the difference between `response` and `response.json()`? Why do we need to call `.json()`?

3. Why can we not write `useEffect(async () => { ... })`? What do we do instead?

4. What are the three states of fetching data? Why do we need all three?

5. What happens if you forget to check `response.ok`? What kind of bugs could this cause?

---

## Exercises

### Exercise 1: Post Fetcher

Build a component that:
- Fetches a post from `https://jsonplaceholder.typicode.com/posts/1`
- Shows the post's title and body
- Has "Previous" and "Next" buttons that fetch post number 2, 3, 4, etc.
- Shows the current post number
- Handles loading and error states

Hint: Store the post ID in state and use it in the fetch URL. Put the post ID in the dependency array of `useEffect`.

### Exercise 2: User Search

Build a component that:
- Fetches all users from `https://jsonplaceholder.typicode.com/users`
- Displays them in a list
- Has a search input that filters the list by name (client-side filtering, no new fetch needed)
- Shows "No users found" if the search does not match anyone

### Exercise 3: Multi-Resource Viewer

Build a component with three buttons: "Users", "Posts", and "Todos". When the user clicks a button:
- Fetch the corresponding data from `https://jsonplaceholder.typicode.com/users`, `/posts`, or `/todos`
- Display the first 5 items from the result
- Show a loading state while fetching
- Show which category is currently selected

---

## What Is Next?

Congratulations! You have just learned one of the most important skills in modern web development: fetching data from APIs. Your React apps can now connect to the outside world and display real data.

In the next chapter, we will explore how to reuse components effectively. You have already been building components, but you will learn patterns for making them more flexible and reusable so that one component can serve many different purposes across your application.
