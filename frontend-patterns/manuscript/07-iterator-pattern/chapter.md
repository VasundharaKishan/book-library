# Chapter 7: Iterator Pattern

## What You Will Learn

- What the Iterator Pattern is and why uniform traversal matters
- How JavaScript's `Symbol.iterator` protocol works under the hood
- How to make any object iterable with `for...of`
- How generators (`function*`) simplify iterator creation
- How to iterate over paginated API results transparently
- Lazy evaluation and why it saves memory and time
- Real-world iterators in React: virtualized lists and infinite scroll

## Why This Chapter Matters

Think about a remote control for your TV. You press "Next Channel" and the TV moves to the next channel. You do not need to know how channels are stored internally -- maybe in a list, maybe in a tree, maybe in a hash table. You do not need to know the total number of channels. You just press "Next" and get the next one.

That is the Iterator Pattern. It provides a standard way to access elements of a collection one by one, without exposing how the collection is structured internally.

In frontend development, you deal with collections constantly. Arrays from API responses. Paginated search results that span many pages. Tree structures of nested comments or file systems. Infinite feeds of social media posts. Each of these has a different internal structure, but you want to process their items the same way: one at a time, in order.

JavaScript has this pattern built directly into the language with the **iteration protocol** and **generators**. Understanding how they work gives you the power to create clean, memory-efficient data pipelines and handle complex data sources with elegant code.

---

## The Problem: Different Collections, Different Traversal Code

Imagine you have data stored in different structures and you need to process each item.

### The Painful Way (Before the Pattern)

```javascript
// Three different data structures, three different traversal methods

// 1. Array -- use index
const arrayItems = ['Apple', 'Banana', 'Cherry'];
for (let i = 0; i < arrayItems.length; i++) {
  console.log(arrayItems[i]);
}

// 2. Set -- cannot use index!
const setItems = new Set(['Dog', 'Cat', 'Bird']);
// setItems[0] does not work!
setItems.forEach(item => {
  console.log(item);
});

// 3. Map -- use entries
const mapItems = new Map([
  ['name', 'Alice'],
  ['age', '30'],
  ['city', 'Portland']
]);
for (const [key, value] of mapItems.entries()) {
  console.log(`${key}: ${value}`);
}

// 4. Custom tree structure -- completely different
const tree = {
  value: 'root',
  children: [
    {
      value: 'A',
      children: [
        { value: 'A1', children: [] },
        { value: 'A2', children: [] }
      ]
    },
    {
      value: 'B',
      children: [
        { value: 'B1', children: [] }
      ]
    }
  ]
};

// Need a recursive function just to visit every node
function traverseTree(node) {
  console.log(node.value);
  node.children.forEach(child => traverseTree(child));
}
traverseTree(tree);
```

**Output:**
```
Apple
Banana
Cherry
Dog
Cat
Bird
name: Alice
age: 30
city: Portland
root
A
A1
A2
B
B1
```

Each data structure requires completely different code to traverse. What if you had a function that processes items regardless of where they come from?

```
  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │  Array   │  │   Set    │  │   Map    │  │  Tree    │
  │          │  │          │  │          │  │          │
  │ for(i=0; │  │ .forEach │  │ .entries │  │ recursive│
  │  i<len;  │  │          │  │          │  │ function │
  │  i++)    │  │          │  │          │  │          │
  └──────────┘  └──────────┘  └──────────┘  └──────────┘

  Four different structures = four different traversal methods
  Every new structure = another custom traversal

  What if they all worked the same way?
```

---

## The Solution: JavaScript's Iteration Protocol

JavaScript solved this with the **Iterable Protocol** and the **Iterator Protocol**. Any object that follows these protocols can be used with `for...of`, the spread operator (`...`), destructuring, and more.

### How It Works

```
  Iterable Protocol:
  ──────────────────

  An object is ITERABLE if it has a [Symbol.iterator]() method
  that returns an ITERATOR.

  Iterator Protocol:
  ──────────────────

  An ITERATOR is an object with a next() method that returns:
  { value: <nextValue>, done: false }   ← still has items
  { value: undefined, done: true }      ← no more items

  ┌────────────────────────────┐
  │     Iterable Object        │
  │                            │
  │  [Symbol.iterator]() {     │
  │    return {                │
  │      next() {              │
  │        return {            │
  │          value: ...,       │
  │          done: false/true  │
  │        };                  │
  │      }                     │
  │    };                      │
  │  }                         │
  └────────────────────────────┘
           │
           ▼
  for (const item of iterable) {
    // Gets each value automatically
  }
```

### Built-In Iterables

Arrays, Strings, Maps, Sets, and TypedArrays are all iterable by default.

```javascript
// All of these work with for...of because they implement Symbol.iterator

// Array
for (const item of ['a', 'b', 'c']) {
  process.stdout.write(item + ' ');
}
console.log();

// String (iterates over characters)
for (const char of 'Hello') {
  process.stdout.write(char + ' ');
}
console.log();

// Set
for (const item of new Set([1, 2, 3])) {
  process.stdout.write(item + ' ');
}
console.log();

// Map
for (const [key, value] of new Map([['x', 1], ['y', 2]])) {
  process.stdout.write(`${key}=${value} `);
}
console.log();
```

**Output:**
```
a b c
H e l l o
1 2 3
x=1 y=2
```

### The Spread Operator and Destructuring Use Iterators Too

```javascript
const mySet = new Set([10, 20, 30]);

// Spread: converts iterable to array
const arr = [...mySet];
console.log(arr); // [10, 20, 30]

// Destructuring: pulls values from iterable
const [first, second] = mySet;
console.log(first, second); // 10 20

// Array.from: creates array from iterable
const arr2 = Array.from(mySet);
console.log(arr2); // [10, 20, 30]
```

**Output:**
```
[ 10, 20, 30 ]
10 20
[ 10, 20, 30 ]
```

---

## Building a Custom Iterator with Symbol.iterator

Let us make the tree structure from earlier iterable.

```javascript
// tree-node.js

class TreeNode {
  constructor(value, children = []) {
    this.value = value;
    this.children = children;
  }

  // Make TreeNode iterable using depth-first traversal
  [Symbol.iterator]() {
    let stack = [this]; // Start with the root node

    return {
      next() {
        if (stack.length === 0) {
          return { value: undefined, done: true };
        }

        const current = stack.pop();
        // Add children in reverse order so left children are processed first
        for (let i = current.children.length - 1; i >= 0; i--) {
          stack.push(current.children[i]);
        }

        return { value: current.value, done: false };
      }
    };
  }
}

// Build the same tree from before
const tree = new TreeNode('root', [
  new TreeNode('A', [
    new TreeNode('A1'),
    new TreeNode('A2')
  ]),
  new TreeNode('B', [
    new TreeNode('B1')
  ])
]);

// Now we can use for...of!
console.log('Depth-first traversal:');
for (const value of tree) {
  console.log(' ', value);
}

// And spread!
const allValues = [...tree];
console.log('\nAll values:', allValues);

// And destructuring!
const [root, firstChild, ...rest] = tree;
console.log('\nRoot:', root);
console.log('First child:', firstChild);
console.log('Rest:', rest);
```

**Output:**
```
Depth-first traversal:
  root
  A
  A1
  A2
  B
  B1

All values: [ 'root', 'A', 'A1', 'A2', 'B', 'B1' ]

Root: root
First child: A
Rest: [ 'A1', 'A2', 'B', 'B1' ]
```

The tree now works exactly like an array with `for...of`, spread, and destructuring. The consumer does not need to know anything about the tree's internal structure.

```
  BEFORE (custom traversal):        AFTER (Symbol.iterator):

  function traverseTree(node) {     for (const value of tree) {
    console.log(node.value);          console.log(value);
    node.children.forEach(child =>  }
      traverseTree(child)
    );                               // Same code works for
  }                                  // arrays, sets, maps,
  traverseTree(tree);               // trees, and anything
                                     // that implements
  // Only works for this             // Symbol.iterator
  // specific tree structure
```

---

## Generators: The Easy Way to Build Iterators

Writing `Symbol.iterator` by hand with a `next()` method and stack management is tedious. JavaScript generators make it dramatically simpler.

### Generator Basics

A generator is a function declared with `function*` that can pause and resume using `yield`.

```javascript
function* countToThree() {
  console.log('About to yield 1');
  yield 1;
  console.log('About to yield 2');
  yield 2;
  console.log('About to yield 3');
  yield 3;
  console.log('Generator done');
}

const gen = countToThree();

console.log(gen.next()); // { value: 1, done: false }
console.log(gen.next()); // { value: 2, done: false }
console.log(gen.next()); // { value: 3, done: false }
console.log(gen.next()); // { value: undefined, done: true }
```

**Output:**
```
About to yield 1
{ value: 1, done: false }
About to yield 2
{ value: 2, done: false }
About to yield 3
{ value: 3, done: false }
Generator done
{ value: undefined, done: true }
```

Notice: the generator pauses at each `yield` and only resumes when `next()` is called again. This is **lazy evaluation** -- nothing runs until you ask for the next value.

### Generators Are Iterators

Generators automatically implement the iteration protocol. You can use them with `for...of`.

```javascript
function* fibonacci() {
  let a = 0, b = 1;
  while (true) {  // Infinite sequence!
    yield a;
    [a, b] = [b, a + b];
  }
}

// Take the first 10 Fibonacci numbers
const fib = fibonacci();
for (let i = 0; i < 10; i++) {
  console.log(fib.next().value);
}
```

**Output:**
```
0
1
1
2
3
5
8
13
21
34
```

An **infinite sequence** is possible because generators are lazy. The `while (true)` loop does not run forever -- it pauses at each `yield` and only continues when asked.

### Tree Traversal with Generators (Much Simpler!)

```javascript
class TreeNode {
  constructor(value, children = []) {
    this.value = value;
    this.children = children;
  }

  // Generator-based iterator -- so much simpler!
  *[Symbol.iterator]() {
    yield this.value;
    for (const child of this.children) {
      yield* child; // yield* delegates to child's iterator
    }
  }
}

const tree = new TreeNode('root', [
  new TreeNode('A', [
    new TreeNode('A1'),
    new TreeNode('A2')
  ]),
  new TreeNode('B', [
    new TreeNode('B1')
  ])
]);

for (const value of tree) {
  console.log(value);
}
```

**Output:**
```
root
A
A1
A2
B
B1
```

Compare the generator version to the manual `Symbol.iterator` version from before. The generator is three lines instead of fifteen. The `yield*` keyword delegates to the child node's own iterator, handling the recursion elegantly.

```
  Manual Iterator:                Generator:

  [Symbol.iterator]() {           *[Symbol.iterator]() {
    let stack = [this];             yield this.value;
    return {                        for (const child of this.children) {
      next() {                        yield* child;
        if (stack.length === 0)     }
          return { done: true };  }
        const current = stack.pop();
        for (let i = ...)           3 lines.
          stack.push(child);         Readable.
        return { value, done: f };   Clean.
      }
    };
  }

  15+ lines.
  Manual stack management.
  Error-prone.
```

---

## Iterating Over Paginated API Results

One of the most practical uses of iterators in frontend development is transparently handling paginated API data.

### The Problem: Manual Pagination

```javascript
// Without iterators: manual, repetitive pagination code

async function getAllUsers() {
  const allUsers = [];
  let page = 1;
  let hasMore = true;

  while (hasMore) {
    const response = await fetch(`/api/users?page=${page}&limit=20`);
    const data = await response.json();
    allUsers.push(...data.users);
    hasMore = data.hasNextPage;
    page++;
  }

  return allUsers; // Could be thousands of users loaded in memory at once!
}
```

Problems:
1. Loads **all data into memory** at once
2. Pagination logic is mixed with business logic
3. Every paginated endpoint needs similar boilerplate

### The Solution: Async Generator for Pagination

```javascript
// paginated-fetcher.js

async function* fetchPaginated(baseUrl, pageSize = 20) {
  let page = 1;
  let hasMore = true;

  while (hasMore) {
    console.log(`Fetching page ${page}...`);
    const response = await fetch(`${baseUrl}?page=${page}&limit=${pageSize}`);
    const data = await response.json();

    // Yield each item individually
    for (const item of data.items) {
      yield item;
    }

    hasMore = data.hasNextPage;
    page++;
  }
}

// Usage -- processes items one at a time, page by page
async function processUsers() {
  const users = fetchPaginated('/api/users', 3);

  for await (const user of users) {
    console.log(`Processing user: ${user.name}`);

    // Can stop early! Only fetches pages we need
    if (user.name === 'Target User') {
      console.log('Found target user, stopping.');
      break; // No more pages are fetched!
    }
  }
}
```

Let us simulate this with a mock API:

```javascript
// Mock API for demonstration
function createMockApi() {
  const allUsers = [
    { id: 1, name: 'Alice' },
    { id: 2, name: 'Bob' },
    { id: 3, name: 'Charlie' },
    { id: 4, name: 'Diana' },
    { id: 5, name: 'Eve' },
    { id: 6, name: 'Frank' },
    { id: 7, name: 'Grace' },
    { id: 8, name: 'Hank' }
  ];

  return function mockFetch(url) {
    const params = new URL(url, 'http://localhost').searchParams;
    const page = parseInt(params.get('page'));
    const limit = parseInt(params.get('limit'));
    const start = (page - 1) * limit;
    const end = start + limit;

    return Promise.resolve({
      json: () => Promise.resolve({
        items: allUsers.slice(start, end),
        hasNextPage: end < allUsers.length,
        totalPages: Math.ceil(allUsers.length / limit)
      })
    });
  };
}

// Replace global fetch with mock
const originalFetch = globalThis.fetch;
globalThis.fetch = createMockApi();

async function* fetchPaginated(baseUrl, pageSize = 3) {
  let page = 1;
  let hasMore = true;

  while (hasMore) {
    console.log(`\n--- Fetching page ${page} ---`);
    const response = await fetch(`${baseUrl}?page=${page}&limit=${pageSize}`);
    const data = await response.json();

    for (const item of data.items) {
      yield item;
    }

    hasMore = data.hasNextPage;
    page++;
  }
}

// Process users lazily
async function main() {
  console.log('=== Processing all users ===');
  for await (const user of fetchPaginated('/api/users', 3)) {
    console.log(`  User: ${user.name} (id: ${user.id})`);
  }

  console.log('\n=== Stopping early ===');
  for await (const user of fetchPaginated('/api/users', 3)) {
    console.log(`  Checking: ${user.name}`);
    if (user.name === 'Diana') {
      console.log('  Found Diana! Stopping.');
      break; // Page 3 is never fetched!
    }
  }
}

main();
```

**Output:**
```
=== Processing all users ===

--- Fetching page 1 ---
  User: Alice (id: 1)
  User: Bob (id: 2)
  User: Charlie (id: 3)

--- Fetching page 2 ---
  User: Diana (id: 4)
  User: Eve (id: 5)
  User: Frank (id: 6)

--- Fetching page 3 ---
  User: Grace (id: 7)
  User: Hank (id: 8)

=== Stopping early ===

--- Fetching page 1 ---
  Checking: Alice
  Checking: Bob
  Checking: Charlie

--- Fetching page 2 ---
  Checking: Diana
  Found Diana! Stopping.
```

Notice in the "Stopping early" run: page 3 was never fetched. The generator paused, and when we broke out of the loop, it stopped. No wasted network requests.

```
  Without Generator:               With Generator:

  Fetch ALL pages                   Fetch page 1 ──► yield items
  Store ALL items in memory         Fetch page 2 ──► yield items
  Then process them                 break! ──► STOP
                                    Page 3 never fetched!
  Memory: O(all items)
  Network: ALL pages                Memory: O(page size)
                                    Network: only needed pages
```

---

## Lazy Evaluation: Process Only What You Need

Lazy evaluation means values are computed only when requested. Generators enable this naturally.

### Lazy Range

```javascript
// Eager: creates the entire array in memory
function eagerRange(start, end) {
  const result = [];
  for (let i = start; i <= end; i++) {
    result.push(i);
  }
  return result;
}

// Lazy: generates values one at a time
function* lazyRange(start, end) {
  for (let i = start; i <= end; i++) {
    yield i;
  }
}

// Eager: allocates an array of 1,000,000 numbers
console.log('Eager range created'); // Uses ~8 MB of memory
const eager = eagerRange(1, 1000000);
console.log('First 3 eager:', eager[0], eager[1], eager[2]);

// Lazy: allocates almost nothing
console.log('Lazy range created'); // Uses almost no memory
const lazy = lazyRange(1, 1000000);
console.log('First 3 lazy:');
console.log(' ', lazy.next().value);
console.log(' ', lazy.next().value);
console.log(' ', lazy.next().value);
// The remaining 999,997 values are never computed!
```

**Output:**
```
Eager range created
First 3 eager: 1 2 3
Lazy range created
First 3 lazy:
  1
  2
  3
```

### Composing Lazy Transformations

You can chain generators to create data processing pipelines where no intermediate arrays are created.

```javascript
// Generator utilities for lazy data processing

function* map(iterable, fn) {
  for (const item of iterable) {
    yield fn(item);
  }
}

function* filter(iterable, predicate) {
  for (const item of iterable) {
    if (predicate(item)) {
      yield item;
    }
  }
}

function* take(iterable, count) {
  let taken = 0;
  for (const item of iterable) {
    if (taken >= count) return;
    yield item;
    taken++;
  }
}

function* skip(iterable, count) {
  let skipped = 0;
  for (const item of iterable) {
    if (skipped < count) {
      skipped++;
      continue;
    }
    yield item;
  }
}

// Build a lazy pipeline
function* range(start, end) {
  for (let i = start; i <= end; i++) {
    yield i;
  }
}

// Pipeline: range 1-100 -> keep even -> square -> take first 5
const pipeline = take(
  map(
    filter(range(1, 100), n => n % 2 === 0),
    n => n * n
  ),
  5
);

console.log('Pipeline results:');
for (const value of pipeline) {
  console.log(' ', value);
}
// Only the first 10 numbers from range(1, 100) are ever evaluated!
// The rest are never generated.
```

**Output:**
```
Pipeline results:
  4
  16
  36
  64
  100
```

```
  Lazy Pipeline Visualization:
  ────────────────────────────

  range(1, 100)     filter(even)     map(n*n)        take(5)
  ─────────────     ────────────     ────────        ───────

  1 ──────────────► skip
  2 ──────────────► pass ──────────► 4 ───────────► output (1/5)
  3 ──────────────► skip
  4 ──────────────► pass ──────────► 16 ──────────► output (2/5)
  5 ──────────────► skip
  6 ──────────────► pass ──────────► 36 ──────────► output (3/5)
  7 ──────────────► skip
  8 ──────────────► pass ──────────► 64 ──────────► output (4/5)
  9 ──────────────► skip
  10 ─────────────► pass ──────────► 100 ─────────► output (5/5)
  11-100 ─────────► NEVER GENERATED (take is satisfied)

  Each item flows through the entire pipeline before the next one starts.
  No intermediate arrays are created.
```

---

## Making Custom Collections Iterable

### Example: A Ring Buffer

A ring buffer is a fixed-size collection that overwrites the oldest items when full. Let us make it iterable.

```javascript
class RingBuffer {
  constructor(capacity) {
    this.capacity = capacity;
    this.buffer = new Array(capacity);
    this.head = 0;    // Where next item goes
    this.count = 0;   // Current number of items
  }

  push(item) {
    this.buffer[this.head] = item;
    this.head = (this.head + 1) % this.capacity;
    if (this.count < this.capacity) {
      this.count++;
    }
  }

  get size() {
    return this.count;
  }

  // Make it iterable -- yields items from oldest to newest
  *[Symbol.iterator]() {
    if (this.count === 0) return;

    const start = this.count < this.capacity
      ? 0
      : this.head; // head points to the oldest item when full

    for (let i = 0; i < this.count; i++) {
      const index = (start + i) % this.capacity;
      yield this.buffer[index];
    }
  }
}

// A ring buffer that holds the last 5 log messages
const recentLogs = new RingBuffer(5);

// Add 8 messages (only last 5 will remain)
recentLogs.push('Log 1: App started');
recentLogs.push('Log 2: User logged in');
recentLogs.push('Log 3: Fetched data');
recentLogs.push('Log 4: Rendered dashboard');
recentLogs.push('Log 5: User clicked button');
recentLogs.push('Log 6: API request sent');   // Overwrites Log 1
recentLogs.push('Log 7: Response received');   // Overwrites Log 2
recentLogs.push('Log 8: Cache updated');       // Overwrites Log 3

console.log(`Recent logs (${recentLogs.size} items):`);
for (const log of recentLogs) {
  console.log(' ', log);
}

// Works with spread too
console.log('\nAs array:', [...recentLogs]);
```

**Output:**
```
Recent logs (5 items):
  Log 4: Rendered dashboard
  Log 5: User clicked button
  Log 6: API request sent
  Log 7: Response received
  Log 8: Cache updated

As array: [
  'Log 4: Rendered dashboard',
  'Log 5: User clicked button',
  'Log 6: API request sent',
  'Log 7: Response received',
  'Log 8: Cache updated'
]
```

### Example: A Date Range Iterator

```javascript
class DateRange {
  constructor(start, end) {
    this.start = new Date(start);
    this.end = new Date(end);
  }

  *[Symbol.iterator]() {
    const current = new Date(this.start);
    while (current <= this.end) {
      yield new Date(current); // Yield a copy
      current.setDate(current.getDate() + 1);
    }
  }
}

const vacation = new DateRange('2025-07-01', '2025-07-05');

console.log('Vacation days:');
for (const day of vacation) {
  const formatted = day.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric'
  });
  console.log(' ', formatted);
}

// Destructure the first and last days
const days = [...vacation];
console.log(`\n${days.length} days total`);
```

**Output:**
```
Vacation days:
  Tue, Jul 1
  Wed, Jul 2
  Thu, Jul 3
  Fri, Jul 4
  Sat, Jul 5

5 days total
```

---

## Iterators in React: Infinite Scroll with Async Generators

```javascript
// hooks/usePaginatedData.js
import { useState, useCallback, useRef } from 'react';

/**
 * Custom hook that wraps an async generator for use in React components
 */
export function usePaginatedData(fetchGeneratorFn) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const generatorRef = useRef(null);

  const loadMore = useCallback(async () => {
    if (loading || !hasMore) return;

    // Create generator on first call
    if (!generatorRef.current) {
      generatorRef.current = fetchGeneratorFn();
    }

    setLoading(true);

    // Pull the next batch from the generator
    const batch = [];
    const BATCH_SIZE = 10;

    for (let i = 0; i < BATCH_SIZE; i++) {
      const result = await generatorRef.current.next();
      if (result.done) {
        setHasMore(false);
        break;
      }
      batch.push(result.value);
    }

    setItems(prev => [...prev, ...batch]);
    setLoading(false);
  }, [fetchGeneratorFn, loading, hasMore]);

  const reset = useCallback(() => {
    generatorRef.current = null;
    setItems([]);
    setHasMore(true);
    setLoading(false);
  }, []);

  return { items, loading, hasMore, loadMore, reset };
}
```

```javascript
// components/InfiniteUserList.jsx
import { useEffect, useRef, useCallback } from 'react';
import { usePaginatedData } from '../hooks/usePaginatedData';

// Async generator that fetches users page by page
async function* fetchAllUsers() {
  let page = 1;
  while (true) {
    const response = await fetch(`/api/users?page=${page}&limit=20`);
    const data = await response.json();

    for (const user of data.users) {
      yield user;
    }

    if (!data.hasNextPage) return; // Generator ends
    page++;
  }
}

export default function InfiniteUserList() {
  const { items: users, loading, hasMore, loadMore } = usePaginatedData(
    useCallback(() => fetchAllUsers(), [])
  );

  // Intersection Observer for infinite scroll
  const sentinelRef = useRef(null);

  useEffect(() => {
    const sentinel = sentinelRef.current;
    if (!sentinel) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore && !loading) {
          loadMore();
        }
      },
      { threshold: 0.1 }
    );

    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [hasMore, loading, loadMore]);

  // Load initial data
  useEffect(() => { loadMore(); }, []);

  return (
    <div>
      <h2>Users ({users.length})</h2>
      <ul>
        {users.map(user => (
          <li key={user.id}>{user.name} - {user.email}</li>
        ))}
      </ul>

      {/* Sentinel element -- when it becomes visible, load more */}
      <div ref={sentinelRef} style={{ height: 1 }} />

      {loading && <p>Loading more...</p>}
      {!hasMore && <p>No more users to load.</p>}
    </div>
  );
}
```

```
  Infinite Scroll with Async Generator:
  ──────────────────────────────────────

  ┌────────────────────────────────┐
  │  Async Generator               │
  │  fetchAllUsers()               │
  │                                │
  │  Page 1: yield user1..user20   │──► React State: [user1..user20]
  │          (pause)               │    Render list
  │                                │
  │  Page 2: yield user21..user40  │──► React State: [..., user21..user40]
  │          (pause)               │    Render more
  │                                │
  │  User scrolls to bottom        │
  │  IntersectionObserver fires    │
  │  loadMore() calls next()       │
  │                                │
  │  Page 3: yield user41..user60  │──► React State: [..., user41..user60]
  │          (pause)               │    Render even more
  │                                │
  │  No more pages: return         │──► hasMore = false
  └────────────────────────────────┘    Show "No more users"
```

---

## When to Use / When NOT to Use

### When to Use the Iterator Pattern

- **Paginated API data**: Fetch pages lazily, process items one at a time
- **Large datasets**: When you cannot fit all data in memory at once
- **Custom data structures**: Trees, graphs, linked lists -- make them work with `for...of`
- **Data processing pipelines**: Chain transformations without creating intermediate arrays
- **Infinite sequences**: Fibonacci, random numbers, sensor readings -- things with no fixed end
- **Streaming data**: Processing CSV files, log lines, or WebSocket messages line by line
- **Abstraction**: Hide how data is stored while exposing how it is accessed

### When NOT to Use the Iterator Pattern

- **Small arrays**: If your data fits comfortably in memory and is already an array, just use `.map()`, `.filter()`, and `.reduce()`. Do not add complexity with generators
- **When you need random access**: Iterators are sequential (forward-only). If you need to access item #500 directly, use an array
- **Performance-critical inner loops**: Generator function calls have overhead compared to a plain `for` loop. In tight loops running millions of times, this overhead adds up
- **When the whole dataset is needed at once**: If your algorithm needs all items in memory simultaneously (like sorting), lazy evaluation does not help

---

## Common Mistakes

### Mistake 1: Trying to Reuse an Exhausted Iterator

```javascript
function* numbers() {
  yield 1;
  yield 2;
  yield 3;
}

const gen = numbers();

// First loop: works
for (const n of gen) {
  console.log(n); // 1, 2, 3
}

// Second loop: NOTHING! Generator is exhausted
for (const n of gen) {
  console.log(n); // Never runs
}
```

**Fix**: Create a new generator for each loop, or use an iterable object that creates a fresh iterator each time `[Symbol.iterator]` is called.

```javascript
// Iterable object -- fresh iterator every time
const numbers = {
  *[Symbol.iterator]() {
    yield 1;
    yield 2;
    yield 3;
  }
};

for (const n of numbers) { console.log(n); } // 1, 2, 3
for (const n of numbers) { console.log(n); } // 1, 2, 3 (works again!)
```

### Mistake 2: Forgetting `yield*` for Delegation

```javascript
function* inner() {
  yield 'a';
  yield 'b';
}

// WRONG -- yields the generator OBJECT, not its values
function* outerWrong() {
  yield inner(); // yields Generator {}, not 'a' and 'b'
}

// RIGHT -- delegates to inner generator
function* outerRight() {
  yield* inner(); // yields 'a', then 'b'
}

console.log([...outerWrong()]); // [ Generator {} ]
console.log([...outerRight()]); // [ 'a', 'b' ]
```

**Output:**
```
[ Object [Generator] {} ]
[ 'a', 'b' ]
```

### Mistake 3: Not Using `for await...of` with Async Generators

```javascript
async function* asyncNumbers() {
  yield 1;
  yield 2;
  yield 3;
}

// WRONG -- regular for...of with async generator
// for (const n of asyncNumbers()) { } // Fails or gives Promise objects

// RIGHT -- use for await...of
for await (const n of asyncNumbers()) {
  console.log(n); // 1, 2, 3
}
```

---

## Best Practices

1. **Use generators over manual iterators**. They are shorter, clearer, and less error-prone than manually implementing `next()`.

2. **Make your iterable objects return fresh iterators**. Implement `[Symbol.iterator]` on the object (not the prototype) so each `for...of` loop gets a new traversal.

3. **Use `yield*` for delegation**. When one generator needs to yield values from another, use `yield*` to delegate rather than manually iterating.

4. **Prefer `for await...of`** for async generators instead of manually calling `.next()`. It handles the Promise unwrapping and done-checking for you.

5. **Use lazy pipelines for large data**. Chain `filter`, `map`, and `take` generators to process large datasets without creating intermediate arrays.

6. **Clean up generators with `return()`**. When you break out of a `for...of` loop, the generator's `return()` method is called automatically. If you are iterating manually, call `gen.return()` when done.

7. **Keep generators pure when possible**. Generators that do not depend on external mutable state are easier to test and reason about.

---

## Quick Summary

The Iterator Pattern provides a uniform way to traverse any collection without knowing its internal structure.

```
  JavaScript Iteration Ecosystem:
  ────────────────────────────────

  Iterable Protocol         for...of, spread(...), destructuring
  [Symbol.iterator]()       Array.from(), Promise.all()
        │
        ▼
  Iterator Protocol         { next() → { value, done } }
        │
        ▼
  Generators               function* + yield
  (easiest way to          yield* (delegation)
   create iterators)       Lazy evaluation built-in
        │
        ▼
  Async Generators         async function* + yield
  for await...of           Perfect for paginated APIs
```

---

## Key Points

- The **Iterator Pattern** provides a standard way to traverse collections one element at a time
- JavaScript's **Symbol.iterator** protocol makes any object work with `for...of`, spread, and destructuring
- **Generators** (`function*` + `yield`) are the simplest way to create custom iterators
- **`yield*`** delegates to another iterable, essential for recursive structures like trees
- **Async generators** (`async function*`) combined with `for await...of` are perfect for paginated API data
- **Lazy evaluation** means values are computed only when needed, saving memory and enabling infinite sequences
- Iterators are **forward-only and single-use** by default -- make objects return fresh iterators for reuse
- **Lazy pipelines** (chained generators for map, filter, take) process data without intermediate arrays

---

## Practice Questions

1. What is the difference between the Iterable Protocol and the Iterator Protocol? What method does each require?

2. Why can you only iterate through a generator once? How do you create an object that can be iterated multiple times?

3. Explain how `yield*` works. What happens if you use `yield` instead of `yield*` when delegating to another generator?

4. How do async generators solve the paginated API problem? What advantage does `break` inside `for await...of` give you?

5. What is lazy evaluation? Give a concrete example where lazy evaluation saves significant memory or computation.

---

## Exercises

### Exercise 1: Build a Paginated Table Component

Create an async generator that fetches product data from a mock API in pages of 10. Build a React component that:
- Shows a table of products
- Has "Load More" and "Load All" buttons
- Displays the current count vs total
- Uses the generator to fetch pages on demand

### Exercise 2: Lazy Data Pipeline

Build a set of composable generator functions:
- `range(start, end)` -- generates numbers in range
- `map(iterable, fn)` -- transforms each item
- `filter(iterable, fn)` -- keeps items matching predicate
- `take(iterable, n)` -- takes first n items
- `chunk(iterable, size)` -- groups items into arrays of given size

Use these to build a pipeline that:
1. Generates numbers 1 through 1000
2. Keeps only multiples of 3
3. Squares each number
4. Groups them into chunks of 5
5. Takes the first 3 chunks

Verify that only about 45 numbers from the range are actually generated.

### Exercise 3: Tree Iterator with Multiple Traversal Orders

Create a `TreeNode` class that supports three different iteration strategies:
- **Depth-first pre-order**: parent, then children (default `[Symbol.iterator]`)
- **Depth-first post-order**: children, then parent
- **Breadth-first (level order)**: level by level, left to right

Implement each as a generator method:
```javascript
tree[Symbol.iterator]()    // pre-order (default)
tree.postOrder()           // post-order
tree.breadthFirst()        // level order
```

Test with a tree that has at least 3 levels and verify the output order for each traversal.

---

## What Is Next?

You now have a powerful tool for traversing any data structure uniformly and efficiently. The Iterator Pattern, combined with generators and lazy evaluation, lets you handle paginated APIs, infinite data streams, and custom collections with clean, readable code.

The next chapter covers the Proxy Pattern, where you learn how to intercept and customize operations on objects -- reading properties, writing values, calling functions, and more. This is the foundation for reactivity systems like Vue.js and for building powerful debugging and validation tools.
