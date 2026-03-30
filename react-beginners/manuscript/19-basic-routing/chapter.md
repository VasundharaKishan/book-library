# Chapter 19: Basic Routing

## What You Will Learn

In this chapter, you will learn:

- What routing means and why it matters
- How to install React Router
- How to use `BrowserRouter`, `Routes`, and `Route`
- How to create page components
- How to use `Link` for navigation without page reloads
- How to use `NavLink` for active navigation styling
- How to use `useNavigate` for going to a page with code
- How to handle "Page Not Found" (404) errors
- How to build a simple multi-page website with a navigation bar

## Why This Chapter Matters

Think about how you use a website. You click on "Home" and you see the home page. You click on "About" and you see the about page. You click on "Contact" and you see the contact page. Each page has its own address in the browser's address bar.

On a traditional website, every time you click a link, the browser loads a completely new page from the server. This causes a brief flash. The entire page disappears and a new one loads. It works, but it can feel slow.

React apps work differently. A React app is a **single-page application** (often called an **SPA**). This means the browser loads one HTML page, and then React swaps out the content without reloading the whole page. It is like changing the picture in a picture frame instead of buying a new frame every time.

But here is the problem: if everything happens on one page, how do you handle different URLs? How do you make the "Back" button work? How do you let users bookmark a specific page?

That is where **routing** comes in. A **router** is a tool that watches the URL in the address bar and shows the right content for that URL. It makes a single-page app feel like a multi-page website.

In this chapter, you will learn how to add routing to your React app using a popular library called **React Router**.

---

## What Routing Means

**Routing** is the process of deciding what to show based on the URL.

Think of routing like a hotel front desk. When a guest arrives and says "Room 204," the front desk directs them to the second floor, fourth door on the right. The hotel has many rooms, and the front desk knows which guest goes where.

In a React app, routing works the same way:

- The URL is like the room number. For example, `/about` or `/contact`.
- The router is like the front desk. It looks at the URL and decides which component to show.
- The components are like the rooms. Each one has different content.

When the URL changes, the router swaps out the old component and shows the new one. The browser does not reload. The switch is instant and smooth.

---

## Installing React Router

React Router is not built into React. It is a separate library that you need to install. A **library** is a collection of pre-written code that you can use in your project.

To install it, open your terminal (the command-line tool) and run this command in your project folder:

```
npm install react-router-dom
```

Let us break this command down:

- **`npm`** — This is the Node Package Manager. It downloads and installs libraries for your project.
- **`install`** — This tells npm to install something.
- **`react-router-dom`** — This is the name of the React Router library for web browsers. The "dom" part stands for **Document Object Model**, which is the browser's way of representing a web page.

After running this command, React Router is ready to use in your project.

---

## BrowserRouter, Routes, and Route

React Router gives you three main building blocks. Let us learn each one.

### BrowserRouter

`BrowserRouter` is a wrapper that you put around your entire app. It enables routing. Without it, none of the other routing features work.

Think of `BrowserRouter` as turning on the routing system. It is like flipping the switch that powers the hotel front desk.

```jsx
import { BrowserRouter } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      {/* Your app content goes here */}
    </BrowserRouter>
  );
}
```

You usually only use `BrowserRouter` once, at the very top of your app.

### Routes and Route

`Routes` is a container that holds all your individual `Route` components. Each `Route` maps a URL path to a specific component.

```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />
      </Routes>
    </BrowserRouter>
  );
}
```

Let us go through this:

- **`<Routes>`** — This component looks at the current URL and finds the matching `Route` to display. Only one `Route` is shown at a time.
- **`<Route path="/" element={<Home />} />`** — This says: "When the URL is `/` (the root, or home page), show the `Home` component."
- **`<Route path="/about" element={<About />} />`** — This says: "When the URL is `/about`, show the `About` component."
- **`<Route path="/contact" element={<Contact />} />`** — This says: "When the URL is `/contact`, show the `Contact` component."

The `path` prop is the URL pattern to match. The `element` prop is the component to display.

---

## Creating Page Components

Each "page" in your app is just a regular React component. There is nothing special about them. Here are simple examples:

```jsx
function Home() {
  return (
    <div>
      <h1>Home</h1>
      <p>Welcome to our website! This is the home page.</p>
    </div>
  );
}

function About() {
  return (
    <div>
      <h1>About Us</h1>
      <p>We are a small team that loves building things with React.</p>
    </div>
  );
}

function Contact() {
  return (
    <div>
      <h1>Contact</h1>
      <p>Email us at hello@example.com</p>
    </div>
  );
}
```

These are normal components. They return JSX just like any other component you have written. The only difference is that React Router controls when they appear on the screen.

---

## The Link Component

In regular HTML, you use `<a href="/about">About</a>` to create a link. But in a React app with routing, you should NOT use regular `<a>` tags for internal navigation. Why? Because `<a>` tags cause the browser to reload the entire page. That defeats the purpose of a single-page app.

Instead, React Router provides the `Link` component. It looks and works like a link, but it does not reload the page. It just tells the router to show a different component.

```jsx
import { Link } from 'react-router-dom';

function Navigation() {
  return (
    <nav>
      <Link to="/">Home</Link>
      <Link to="/about">About</Link>
      <Link to="/contact">Contact</Link>
    </nav>
  );
}
```

- **`import { Link } from 'react-router-dom';`** — This brings the `Link` component from React Router.
- **`<Link to="/">Home</Link>`** — The `to` prop tells the link which URL to go to. It works like `href` in a regular `<a>` tag, but without the page reload.

When you click a `Link`, the URL in the address bar changes, and React Router swaps the content. The page does not reload. It is instant.

### Link vs. Regular `<a>` Tag

| Feature | `<a href="...">` | `<Link to="...">` |
|---------|------------------|--------------------|
| Page reload | Yes, full reload | No reload |
| Speed | Slower | Instant |
| Use for | External links | Internal navigation |

**Use `Link` for navigation within your app.** Use regular `<a>` tags only for links to other websites.

---

## NavLink for Active Navigation Styling

`NavLink` is a special version of `Link` that knows whether it is currently active. An **active** link is one that matches the current URL.

Why is this useful? Because you usually want to highlight the current page in your navigation bar. For example, if you are on the About page, the "About" link should look different from the others.

```jsx
import { NavLink } from 'react-router-dom';

function Navigation() {
  const linkStyle = {
    padding: '10px 15px',
    textDecoration: 'none',
    color: '#333'
  };

  const activeLinkStyle = {
    padding: '10px 15px',
    textDecoration: 'none',
    color: 'white',
    backgroundColor: '#007bff',
    borderRadius: '4px'
  };

  return (
    <nav style={{ display: 'flex', gap: '5px', padding: '10px' }}>
      <NavLink
        to="/"
        style={function ({ isActive }) {
          return isActive ? activeLinkStyle : linkStyle;
        }}
      >
        Home
      </NavLink>
      <NavLink
        to="/about"
        style={function ({ isActive }) {
          return isActive ? activeLinkStyle : linkStyle;
        }}
      >
        About
      </NavLink>
      <NavLink
        to="/contact"
        style={function ({ isActive }) {
          return isActive ? activeLinkStyle : linkStyle;
        }}
      >
        Contact
      </NavLink>
    </nav>
  );
}
```

Let us go through the key parts:

- **`<NavLink to="/">`** — Works like `Link`, but it also tracks whether it is the active link.
- **`style={function ({ isActive }) { ... }}`** — `NavLink` passes an object with an `isActive` property to the style function. This property is `true` if the current URL matches the link's `to` prop.
- **`isActive ? activeLinkStyle : linkStyle`** — If the link is active, use the active style (blue background, white text). Otherwise, use the normal style.

### Expected Output

The navigation bar shows three links: Home, About, and Contact. The link for the current page has a blue background and white text. The other links have dark text and no background. When you click a different link, the highlight moves to the new link.

---

## useNavigate for Programmatic Navigation

Sometimes you want to go to a different page using code, not by clicking a link. For example, after the user submits a form, you might want to redirect them to a "Thank You" page. Or after they log in, you might want to send them to the dashboard.

React Router provides a **hook** called `useNavigate` for this purpose. A hook, as you learned earlier, is a special function that gives your component extra abilities.

```jsx
import { useNavigate } from 'react-router-dom';

function LoginPage() {
  const navigate = useNavigate();

  function handleLogin() {
    // Imagine we check the username and password here
    alert('Login successful!');
    navigate('/');
  }

  return (
    <div>
      <h1>Login</h1>
      <button onClick={handleLogin}>Log In</button>
    </div>
  );
}
```

Line by line:

- **`const navigate = useNavigate();`** — This gives you a function called `navigate` that you can use to go to any page.
- **`navigate('/');`** — This tells the router to go to the home page (`/`). The URL changes, and the Home component appears. No page reload.

### Going Back

You can also use `navigate` to go back, like pressing the browser's back button:

```jsx
function SomePage() {
  const navigate = useNavigate();

  return (
    <div>
      <h1>Some Page</h1>
      <button onClick={function () { navigate(-1); }}>
        Go Back
      </button>
    </div>
  );
}
```

- **`navigate(-1)`** — The `-1` means "go back one page in history." It is like pressing the browser's back button. You could use `-2` to go back two pages.

---

## Simple 404 / "Page Not Found" Route

What happens when someone types a URL that does not exist? For example, `/pizza`. Without a catch-all route, React Router shows nothing. That is confusing for the user.

A **404 page** is a special page that appears when no other route matches. The name "404" comes from the HTTP status code that means "Not Found."

```jsx
function NotFound() {
  return (
    <div style={{ textAlign: 'center', padding: '50px' }}>
      <h1>404</h1>
      <h2>Page Not Found</h2>
      <p>Sorry, the page you are looking for does not exist.</p>
      <Link to="/">Go back to Home</Link>
    </div>
  );
}
```

To use this as a catch-all, add it as the last `Route` with `path="*"`:

```jsx
<Routes>
  <Route path="/" element={<Home />} />
  <Route path="/about" element={<About />} />
  <Route path="/contact" element={<Contact />} />
  <Route path="*" element={<NotFound />} />
</Routes>
```

- **`path="*"`** — The asterisk (`*`) means "match anything." It catches all URLs that do not match any of the routes above it.
- **Order matters.** The `*` route should always be last. React Router checks routes from top to bottom and stops at the first match. If `*` were first, it would match everything and no other route would ever work.

### Expected Output

If a user goes to `/pizza` or `/xyz` or any other URL that does not have a route, they will see the "404 - Page Not Found" message with a link to go back home.

---

## Putting It All Together

Let us combine everything into a complete example:

```jsx
import { BrowserRouter, Routes, Route, NavLink, Link, useNavigate } from 'react-router-dom';

function Navigation() {
  const linkStyle = {
    padding: '10px 15px',
    textDecoration: 'none',
    color: '#333'
  };

  const activeLinkStyle = {
    padding: '10px 15px',
    textDecoration: 'none',
    color: 'white',
    backgroundColor: '#007bff',
    borderRadius: '4px'
  };

  function getStyle({ isActive }) {
    return isActive ? activeLinkStyle : linkStyle;
  }

  return (
    <nav style={{
      display: 'flex',
      gap: '5px',
      padding: '15px',
      backgroundColor: '#f8f9fa',
      borderBottom: '1px solid #ddd'
    }}>
      <NavLink to="/" style={getStyle}>Home</NavLink>
      <NavLink to="/about" style={getStyle}>About</NavLink>
      <NavLink to="/contact" style={getStyle}>Contact</NavLink>
    </nav>
  );
}

function Home() {
  return (
    <div style={{ padding: '20px' }}>
      <h1>Welcome Home</h1>
      <p>This is the home page of our website.</p>
      <p>Use the navigation bar above to explore other pages.</p>
    </div>
  );
}

function About() {
  return (
    <div style={{ padding: '20px' }}>
      <h1>About Us</h1>
      <p>We are learning React and building amazing things.</p>
      <p>This page was created using React Router.</p>
    </div>
  );
}

function Contact() {
  const navigate = useNavigate();

  function handleSubmit() {
    alert('Message sent! Redirecting to home page...');
    navigate('/');
  }

  return (
    <div style={{ padding: '20px' }}>
      <h1>Contact Us</h1>
      <p>We would love to hear from you.</p>
      <button onClick={handleSubmit}>Send Message</button>
    </div>
  );
}

function NotFound() {
  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>404</h1>
      <h2>Page Not Found</h2>
      <p>Sorry, this page does not exist.</p>
      <Link to="/">Go back to Home</Link>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Navigation />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}
```

### Expected Output

You will see a navigation bar at the top with three links: Home, About, and Contact. The current page's link is highlighted in blue.

- Clicking "Home" shows the welcome message.
- Clicking "About" shows information about the team.
- Clicking "Contact" shows a contact page with a "Send Message" button. Clicking the button shows an alert and redirects you to the home page.
- Typing a random URL like `/pizza` shows the 404 page with a link back to home.

Notice that the navigation bar stays at the top of every page. It is outside the `<Routes>` component, so it is always visible. Only the content below it changes.

---

## Mini Project: Simple Multi-Page Website

Let us build a more complete website with a proper navigation bar, multiple pages, and some styling.

### The Complete Code

```jsx
import { BrowserRouter, Routes, Route, NavLink, Link } from 'react-router-dom';

function Navbar() {
  const navStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '10px 30px',
    backgroundColor: '#2c3e50',
    color: 'white'
  };

  const linksStyle = {
    display: 'flex',
    gap: '10px',
    listStyle: 'none',
    margin: 0,
    padding: 0
  };

  const linkStyle = {
    color: '#bdc3c7',
    textDecoration: 'none',
    padding: '8px 16px',
    borderRadius: '4px'
  };

  const activeLinkStyle = {
    color: 'white',
    textDecoration: 'none',
    padding: '8px 16px',
    borderRadius: '4px',
    backgroundColor: '#3498db'
  };

  function getStyle({ isActive }) {
    return isActive ? activeLinkStyle : linkStyle;
  }

  return (
    <nav style={navStyle}>
      <h2 style={{ margin: 0 }}>MyWebsite</h2>
      <ul style={linksStyle}>
        <li><NavLink to="/" style={getStyle}>Home</NavLink></li>
        <li><NavLink to="/about" style={getStyle}>About</NavLink></li>
        <li><NavLink to="/services" style={getStyle}>Services</NavLink></li>
        <li><NavLink to="/contact" style={getStyle}>Contact</NavLink></li>
      </ul>
    </nav>
  );
}

function HomePage() {
  const heroStyle = {
    textAlign: 'center',
    padding: '60px 20px',
    backgroundColor: '#ecf0f1'
  };

  return (
    <div>
      <div style={heroStyle}>
        <h1>Welcome to MyWebsite</h1>
        <p>We help you learn React, one step at a time.</p>
        <Link
          to="/about"
          style={{
            display: 'inline-block',
            padding: '12px 24px',
            backgroundColor: '#3498db',
            color: 'white',
            textDecoration: 'none',
            borderRadius: '4px',
            marginTop: '10px'
          }}
        >
          Learn More About Us
        </Link>
      </div>
    </div>
  );
}

function AboutPage() {
  return (
    <div style={{ padding: '40px', maxWidth: '600px', margin: '0 auto' }}>
      <h1>About Us</h1>
      <p>
        We are a team of developers who believe that anyone can learn
        to code. Our mission is to make programming accessible to everyone.
      </p>
      <h2>Our Story</h2>
      <p>
        We started in 2024 with a simple idea: create the most
        beginner-friendly React book in the world.
      </p>
    </div>
  );
}

function ServicesPage() {
  const services = [
    { title: 'Web Development', description: 'We build modern websites using React.' },
    { title: 'Training', description: 'We teach beginners how to code.' },
    { title: 'Consulting', description: 'We help teams adopt React.' }
  ];

  return (
    <div style={{ padding: '40px', maxWidth: '600px', margin: '0 auto' }}>
      <h1>Our Services</h1>
      {services.map(function (service, index) {
        return (
          <div
            key={index}
            style={{
              border: '1px solid #ddd',
              padding: '20px',
              marginBottom: '15px',
              borderRadius: '8px'
            }}
          >
            <h3>{service.title}</h3>
            <p>{service.description}</p>
          </div>
        );
      })}
    </div>
  );
}

function ContactPage() {
  return (
    <div style={{ padding: '40px', maxWidth: '600px', margin: '0 auto' }}>
      <h1>Contact Us</h1>
      <p>We would love to hear from you! Here is how to reach us:</p>
      <ul>
        <li>Email: hello@mywebsite.com</li>
        <li>Phone: (555) 123-4567</li>
        <li>Address: 123 React Street</li>
      </ul>
    </div>
  );
}

function NotFoundPage() {
  return (
    <div style={{ textAlign: 'center', padding: '60px' }}>
      <h1 style={{ fontSize: '72px', color: '#e74c3c' }}>404</h1>
      <h2>Oops! Page Not Found</h2>
      <p>The page you are looking for does not exist.</p>
      <Link
        to="/"
        style={{
          display: 'inline-block',
          padding: '10px 20px',
          backgroundColor: '#3498db',
          color: 'white',
          textDecoration: 'none',
          borderRadius: '4px',
          marginTop: '15px'
        }}
      >
        Go Back Home
      </Link>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/services" element={<ServicesPage />} />
        <Route path="/contact" element={<ContactPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

### Expected Output

You will see a dark navigation bar at the top with "MyWebsite" on the left and four links on the right: Home, About, Services, and Contact. The active link is highlighted in blue.

- **Home page:** A centered welcome section with a heading, a description, and a "Learn More About Us" button that links to the About page.
- **About page:** Text about the team and their story.
- **Services page:** Three service cards listed vertically.
- **Contact page:** Contact information displayed in a list.
- **Any other URL:** A large red "404" with a message and a link back home.

The navigation bar is always visible. Only the content below it changes. Every transition is instant with no page reload.

---

## Quick Summary

- **Routing** shows different content based on the URL without reloading the page.
- **React Router** is a library you install with `npm install react-router-dom`.
- **`BrowserRouter`** wraps your app and enables routing.
- **`Routes`** contains your route definitions. **`Route`** maps a URL path to a component.
- **`Link`** navigates without reloading the page. Use it instead of `<a>` for internal links.
- **`NavLink`** is like `Link` but knows when it is active. Use it for navigation bars.
- **`useNavigate`** lets you navigate with code (for example, after a form submission).
- **`path="*"`** catches all unmatched URLs for a 404 page.

---

## Key Points to Remember

1. Always wrap your app with `BrowserRouter` at the top level. Without it, routing does not work.
2. Use `Link` for internal navigation, not `<a>` tags. Regular links cause a full page reload.
3. Use `NavLink` when you need to highlight the active link in a navigation bar.
4. Put the `path="*"` route last. It is a catch-all and should only match when nothing else does.
5. `useNavigate` is for programmatic navigation — going to a page using code instead of a click.
6. Components outside of `<Routes>` (like a navigation bar) appear on every page. Components inside `<Route>` only appear when their URL matches.

---

## Practice Questions

1. What is the difference between a single-page application and a traditional website?
2. Why should you use `Link` instead of `<a>` for internal navigation in a React app?
3. What does `path="*"` do in a `Route` component?
4. What is the difference between `Link` and `NavLink`?
5. When would you use `useNavigate` instead of `Link`?

---

## Exercises

### Exercise 1: Add a New Page

Add a "Blog" page to the mini project. Create a `BlogPage` component that shows a list of three blog post titles. Add a "Blog" link to the navigation bar.

### Exercise 2: Navigation with useNavigate

Create a simple quiz app with two pages: a "Question" page and a "Result" page. The Question page has a question and two buttons. When the user clicks either button, use `useNavigate` to go to the Result page.

### Exercise 3: Active Styling with CSS Classes

Instead of using inline styles with `NavLink`, try using the `className` prop. `NavLink` can accept a function for `className` just like it does for `style`. Create a navigation bar where the active link gets a CSS class called `active-link`.

---

## What Is Next?

You now know how to build multi-page React apps with routing. You can create navigation bars, handle different pages, and even redirect users with code.

In the next chapter, we will combine everything you have learned in this book into one complete project: a **Todo App**. You will use components, state, props, event handling, lists, conditional rendering, and routing to build a real, working application from scratch. It is time to put all the pieces together.
