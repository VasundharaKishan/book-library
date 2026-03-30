# Chapter 32: Glossary

## What You Will Learn

- Quick definitions for 60+ key terms used throughout this book
- Which chapters cover each concept in depth
- A reference you can return to whenever you encounter an unfamiliar term

## Why This Chapter Matters

Design patterns come with a lot of vocabulary. When you are reading code, reviewing pull requests, or discussing architecture with your team, having precise definitions at your fingertips saves time and prevents miscommunication. This glossary is your quick-reference companion to the rest of the book.

Terms are organized alphabetically. Each entry includes a concise definition and a reference to the chapter where the concept is covered in detail.

---

## A

**Abstract Factory** -- A pattern that provides an interface for creating families of related objects without specifying their concrete classes. Related to the Factory Pattern. See Chapter 11.

**Anti-pattern** -- A common approach that appears to solve a problem but actually creates more problems than it solves. Examples include prop drilling, god components, and premature optimization. See Chapter 1.

**App Shell** -- The minimal HTML, CSS, and JavaScript needed to render the layout of an application (header, sidebar, navigation) before content loads. Used in combination with code splitting and lazy loading. See Chapters 25, 26.

**Async Component** -- A React Server Component that uses `async/await` directly in the component body. Only available in Server Components (Next.js App Router). See Chapter 25.

## B

**Boundary (Error Boundary)** -- A React component that catches JavaScript errors in its child component tree, logs the error, and displays a fallback UI instead of crashing the entire application. See Chapter 29.

**Bundle** -- The combined JavaScript file(s) produced by a build tool (Webpack, Vite, Rollup) from your source code and dependencies. Smaller bundles lead to faster page loads. See Chapter 26.

**Bundle Analysis** -- The process of inspecting what is inside your JavaScript bundle to identify large dependencies, unused code, and code splitting opportunities. Tools include `webpack-bundle-analyzer` and `rollup-plugin-visualizer`. See Chapter 26.

## C

**Client Component** -- In the React Server Components model, a component marked with `'use client'` that runs in the browser. Can use hooks (`useState`, `useEffect`), event handlers, and browser APIs. Ships JavaScript to the client. See Chapter 25.

**Client-Side Rendering (CSR)** -- A rendering strategy where the browser downloads an empty HTML page and JavaScript builds the entire UI on the client. Simple to set up but has slower initial load and poor SEO. See Chapter 25.

**Code Splitting** -- The technique of breaking a JavaScript bundle into smaller chunks that load on demand, reducing initial page load time. Implemented with `React.lazy`, `Suspense`, and dynamic `import()`. See Chapter 26.

**Compound Components** -- A pattern where a parent component and its children share implicit state through React Context, providing a flexible and declarative API. Example: `<Select>`, `<Select.Option>`. See Chapter 19.

**Composition** -- Building complex components by combining simpler ones, as opposed to inheritance. The primary method of code reuse in React. See Chapter 14.

**Container Component** -- A component that handles data fetching, state management, and business logic, passing data to presentational components for rendering. See Chapter 15.

**Controlled Component** -- A form element whose value is controlled by React state. The component's value is set by a state variable and updated via an `onChange` handler. See Chapter 20.

**Context (React Context)** -- A React API that allows passing data through the component tree without manually threading props at every level. Used by the Provider Pattern. See Chapters 14, 21.

**Custom Hook** -- A JavaScript function whose name starts with `use` that encapsulates reusable stateful logic by composing built-in React hooks. See Chapter 18.

## D

**Decorator Pattern** -- A pattern that wraps a component to add behavior or modify its output without changing the original component's code. Higher-Order Components are a React implementation. See Chapter 9.

**Dependency Array** -- The second argument to hooks like `useEffect`, `useMemo`, and `useCallback`. React re-runs the hook only when values in this array change. See Chapters 18, 28.

**Dependency Injection** -- A technique where a component receives its dependencies (services, utilities) from the outside rather than creating them internally. The Provider Pattern is a form of dependency injection. See Chapter 21.

**Dynamic Import** -- The `import()` expression that loads a JavaScript module at runtime rather than at build time. Returns a Promise. The foundation of code splitting. See Chapter 26.

## E

**Eager Loading** -- Loading all code upfront when the page loads, before it is needed. The opposite of lazy loading. See Chapter 26.

**Error Boundary** -- A React class component that implements `getDerivedStateFromError` and/or `componentDidCatch` to catch rendering errors in child components and display a fallback UI. See Chapter 29.

**Event Bus** -- An implementation of the Observer Pattern that provides a central hub for publishing and subscribing to events, enabling decoupled communication between components. See Chapters 4, 5.

**Event Delegation** -- A technique where a single event listener on a parent element handles events from multiple child elements, reducing the number of event listeners in the DOM.

## F

**Facade Pattern** -- A pattern that provides a simplified interface to a complex subsystem. In frontend development, an API service module is a common facade. See Chapter 10.

**Factory Pattern** -- A pattern that creates objects without specifying their exact class or constructor. Useful for creating consistent data structures with defaults and validation. See Chapter 11.

**Fallback UI** -- The user interface displayed when a component fails (Error Boundary fallback) or while a component is loading (Suspense fallback). See Chapters 26, 29.

**First Contentful Paint (FCP)** -- A performance metric measuring the time from page load to when the first piece of content (text, image) appears on screen. Affected by rendering pattern choice. See Chapter 25.

**Flux** -- An application architecture for managing state with unidirectional data flow: Action, Dispatcher, Store, View. The precursor to Redux. See Chapter 24.

## G

**Gang of Four (GoF)** -- The four authors (Gamma, Helm, Johnson, Vlissides) of the seminal 1994 book on design patterns. They documented 23 object-oriented patterns. See Chapter 1.

**getDerivedStateFromError** -- A static lifecycle method in React class components that returns updated state when a child component throws an error. Used by Error Boundaries. See Chapter 29.

## H

**Higher-Order Component (HOC)** -- A function that takes a component and returns a new component with additional behavior or props. Example: `withAuth(Component)`. Largely replaced by Custom Hooks. See Chapter 16.

**Hydration** -- The process where client-side React attaches event listeners and state to server-rendered HTML, making it interactive. Occurs after SSR delivers static HTML to the browser. See Chapter 25.

**Hydration Mismatch** -- A warning (or error) that occurs when the HTML rendered on the server does not match what React would render on the client. Common causes include using `Date`, `Math.random()`, or `window` in render. See Chapter 25.

## I

**Incremental Static Regeneration (ISR)** -- A rendering strategy that serves statically generated pages but regenerates them in the background after a configurable time interval. Combines SSG speed with SSR freshness. See Chapter 25.

**Infinite Scroll** -- A UI pattern where more content loads automatically as the user scrolls toward the bottom of the page. Often combined with virtualization for performance. See Chapter 27.

**Intersection Observer** -- A browser API that detects when an element enters or exits the viewport. Used for lazy loading images, infinite scroll triggers, and prefetching. See Chapters 26, 27.

**Iterator Pattern** -- A pattern that provides a way to access elements of a collection sequentially without exposing the underlying data structure. In JavaScript, implemented via the iterable protocol (`Symbol.iterator`). See Chapter 7.

## K

**Key (React Key)** -- A special string attribute used when rendering lists of elements. Helps React identify which items changed, were added, or were removed. Must be stable and unique among siblings.

## L

**Lazy Loading** -- Deferring the loading of resources (code, images, data) until they are actually needed. Reduces initial page load time. See Chapter 26.

## M

**Mediator Pattern** -- A pattern where a central object coordinates communication between multiple components, preventing direct references between them. Reduces coupling in complex UIs. See Chapter 12.

**Memoization** -- Caching the result of a function call based on its arguments. In React, implemented via `React.memo` (components), `useMemo` (values), and `useCallback` (functions). See Chapter 28.

**Micro-Frontend** -- An architectural pattern where a frontend application is composed of independently developed, tested, and deployed smaller applications, each owned by a separate team. See Chapter 30.

**Mixin Pattern** -- A pattern that adds functionality to a class or object by copying properties from another object. In modern React, replaced by Custom Hooks and composition. See Chapter 13.

**Module Federation** -- A Webpack 5 feature that allows independently built applications to share code at runtime. Used in micro-frontend architectures to load remote components dynamically. See Chapter 30.

**Module Pattern** -- A pattern that encapsulates related code (variables, functions) into a single unit with a clear public API, hiding internal implementation details. In JavaScript, implemented via ES Modules. See Chapter 2.

## O

**Observer Pattern** -- A pattern where an object (subject) maintains a list of dependents (observers) and notifies them of state changes. Foundation for event systems and reactive programming. See Chapter 4.

**Overscan** -- In virtualization, the extra items rendered above and below the visible viewport to prevent blank flashes during fast scrolling. See Chapter 27.

## P

**Prefetching** -- Loading resources before they are needed, typically during idle time or on user hover, so they are available instantly when requested. See Chapter 26.

**Presentational Component** -- A component that is purely concerned with how things look. Receives data via props and has no direct data fetching or complex state logic. See Chapter 15.

**Prop Drilling** -- Passing props through multiple levels of components that do not use them, just to reach a deeply nested child. Solved by the Provider Pattern (Context). See Chapter 21.

**Provider Pattern** -- A pattern that uses React Context to make values available to any component in the tree without prop drilling. Common for themes, authentication, and localization. See Chapter 21.

**Proxy Pattern** -- A pattern that provides a surrogate or placeholder for another object to control access to it. In JavaScript, implemented with the `Proxy` built-in object. See Chapter 8.

**Publish/Subscribe (Pub/Sub)** -- A messaging pattern where publishers emit events without knowing who will receive them, and subscribers listen for events without knowing who sent them. A decoupled variant of the Observer Pattern. See Chapter 5.

## R

**React.lazy** -- A React function that lets you define a component loaded via dynamic import. Used with `Suspense` for code splitting. See Chapter 26.

**React.memo** -- A higher-order component that memoizes a component, preventing re-renders when props have not changed (shallow comparison). See Chapter 28.

**React Server Components (RSC)** -- A React feature where components run exclusively on the server, sending zero JavaScript to the client. Can directly access databases and file systems. See Chapter 25.

**Reducer** -- A pure function that takes the current state and an action, and returns the new state. Used with `useReducer` and in Redux/Flux architectures. See Chapters 22, 24.

**Redux** -- A state management library implementing the Flux architecture with a single store, pure reducer functions, and middleware. See Chapter 24.

**Render Props** -- A pattern where a component receives a function as a prop (or as `children`) that returns React elements, giving the parent control over what is rendered. See Chapter 17.

**Rendering Pattern** -- A strategy for generating HTML: Client-Side Rendering (CSR), Server-Side Rendering (SSR), Static Site Generation (SSG), or Incremental Static Regeneration (ISR). See Chapter 25.

**Revalidation** -- In ISR, the process of regenerating a static page in the background after a specified time period or on-demand trigger. See Chapter 25.

## S

**Server Component** -- A React component that runs only on the server by default (in the App Router). Cannot use hooks or event handlers. Ships zero JavaScript to the client. See Chapter 25.

**Server-Side Rendering (SSR)** -- A rendering strategy where the server generates complete HTML for each request and sends it to the browser. Provides fast initial content and good SEO. See Chapter 25.

**Shadow DOM** -- A browser API that encapsulates a component's DOM and styles, preventing them from leaking into or being affected by the rest of the page. Used with Web Components. See Chapter 30.

**Shallow Comparison** -- Comparing object properties only one level deep (by reference for objects, by value for primitives). Used by `React.memo`, `useMemo`, and `useCallback`. See Chapter 28.

**Singleton Pattern** -- A pattern that restricts a class or module to a single instance. In JavaScript modules, every `import` returns the same reference, making modules natural singletons. See Chapter 3.

**Skeleton Screen** -- A placeholder UI that mimics the layout of the actual content while it loads, providing a better perceived performance than a spinner. Used as Suspense fallbacks. See Chapters 25, 26.

**Stale-While-Revalidate** -- A caching strategy that returns cached (potentially stale) data immediately while fetching fresh data in the background. The basis for ISR. See Chapter 25.

**State Machine** -- A model of computation where a system can be in exactly one of a finite number of states at any time, with defined transitions between states triggered by events. See Chapter 23.

**State Reducer Pattern** -- A pattern where a component accepts a custom reducer function from the parent, allowing the parent to control or modify state transitions. See Chapter 22.

**Static Site Generation (SSG)** -- A rendering strategy where HTML pages are generated at build time and served as static files from a CDN. The fastest delivery method for content that does not change often. See Chapter 25.

**Strategy Pattern** -- A pattern that defines a family of algorithms, encapsulates each one, and makes them interchangeable. The client can choose which algorithm to use at runtime. See Chapter 6.

**Streaming SSR** -- A Server-Side Rendering technique where HTML is sent to the browser in chunks as each section becomes ready, rather than waiting for the entire page. Uses React's `Suspense` for boundaries. See Chapter 25.

**Suspense** -- A React component that lets you specify a loading fallback while child components are not yet ready to render (loading lazy components or fetching data in Server Components). See Chapters 25, 26.

## T

**Time to Interactive (TTI)** -- A performance metric measuring how long it takes from page load until the page is fully interactive (event handlers are attached, UI responds to input). See Chapter 25.

**Tree Shaking** -- A build optimization that removes unused code (dead code) from the final bundle. Relies on ES Module static import/export syntax. See Chapter 26.

## U

**Uncontrolled Component** -- A form element that manages its own internal state via the DOM. Values are read using `ref` rather than React state. Simpler but less flexible than controlled components. See Chapter 20.

**useCallback** -- A React hook that returns a memoized version of a callback function. The function only changes when its dependencies change. See Chapter 28.

**useEffect** -- A React hook that runs side effects (data fetching, subscriptions, DOM manipulation) after render. Replaces lifecycle methods like `componentDidMount` and `componentDidUpdate`.

**useMemo** -- A React hook that memoizes a computed value. The value is only recalculated when its dependencies change. See Chapter 28.

**useReducer** -- A React hook for managing complex state logic using a reducer function. An alternative to `useState` when state updates depend on previous state or involve multiple sub-values. See Chapters 22, 24.

**useState** -- A React hook that adds state to functional components. Returns a state value and a setter function.

## V

**Virtual DOM** -- React's in-memory representation of the real DOM. React compares the virtual DOM before and after state changes (reconciliation) and updates only the parts of the real DOM that changed.

**Virtual List** -- A list component that only renders the items currently visible in the viewport (plus a small buffer), dramatically reducing DOM nodes for large datasets. See Chapter 27.

**Virtualization** -- The technique of rendering only the visible portion of a large dataset, creating and destroying DOM elements as the user scrolls. Implemented by libraries like `react-window`. See Chapter 27.

## W

**Web Component** -- A set of browser-native APIs (Custom Elements, Shadow DOM, HTML Templates) for creating reusable, encapsulated custom HTML elements. Framework-agnostic. See Chapter 30.

**Webpack** -- A module bundler that compiles JavaScript modules and their dependencies into static assets (bundles). Supports code splitting, Module Federation, and various optimizations. See Chapters 26, 30.

**Window (Virtualization)** -- The visible portion of a virtualized list. The "window" determines which items to render based on the scroll position, container height, and item size. See Chapter 27.

---

## Quick Reference by Chapter

| Chapter | Key Terms |
|---------|-----------|
| 1 | Design Pattern, Anti-pattern, Gang of Four |
| 2 | Module Pattern, Encapsulation, ES Modules |
| 3 | Singleton Pattern |
| 4 | Observer Pattern |
| 5 | Publish/Subscribe, Event Bus |
| 6 | Strategy Pattern |
| 7 | Iterator Pattern |
| 8 | Proxy Pattern |
| 9 | Decorator Pattern |
| 10 | Facade Pattern |
| 11 | Factory Pattern |
| 12 | Mediator Pattern |
| 13 | Mixin Pattern |
| 14 | Composition, Component Composition |
| 15 | Container Component, Presentational Component |
| 16 | Higher-Order Component (HOC) |
| 17 | Render Props |
| 18 | Custom Hook |
| 19 | Compound Components |
| 20 | Controlled Component, Uncontrolled Component |
| 21 | Provider Pattern, Context, Prop Drilling |
| 22 | State Reducer Pattern |
| 23 | State Machine |
| 24 | Flux, Redux, Reducer |
| 25 | CSR, SSR, SSG, ISR, Hydration, Streaming SSR, RSC, Server Component, Client Component |
| 26 | Code Splitting, Lazy Loading, React.lazy, Suspense, Dynamic Import, Prefetching, Bundle Analysis |
| 27 | Virtualization, Virtual List, Overscan, Window, Infinite Scroll |
| 28 | Memoization, React.memo, useMemo, useCallback, Shallow Comparison |
| 29 | Error Boundary, Fallback UI, getDerivedStateFromError, componentDidCatch |
| 30 | Micro-Frontend, Module Federation, Web Component, Shadow DOM |
| 31 | Project Pattern Library (all patterns combined) |
