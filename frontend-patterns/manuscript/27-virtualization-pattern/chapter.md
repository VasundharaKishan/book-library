# Chapter 27: The Virtualization Pattern

## What You Will Learn

- Why rendering thousands of DOM elements kills performance
- How virtualization works (the "window" concept)
- The math behind window calculation
- How to use `react-window` for list and grid virtualization
- Combining infinite scroll with virtualization
- Variable-height item handling
- When virtualization is overkill

## Why This Chapter Matters

Open your email inbox. You might have 10,000 emails, but Gmail does not create 10,000 DOM elements. Open Twitter. You might scroll through hundreds of tweets, but your browser is not rendering them all at once. Open a spreadsheet with 100,000 rows. Your browser would crash if it tried to render every cell.

These applications all use the same trick: **virtualization**. They only render the items you can actually see on screen, plus a small buffer above and below. As you scroll, items that leave the viewport are destroyed, and new items entering the viewport are created.

Without virtualization, a list of 10,000 items creates 10,000 DOM nodes. Each one consumes memory, triggers layout calculations, and slows down every interaction. With virtualization, that same list might only have 20 DOM nodes at any time, recycled as you scroll.

The difference is not subtle. It is the difference between an app that freezes and an app that feels butter-smooth.

---

## The Problem: Too Many DOM Nodes

### What Happens Without Virtualization

```jsx
// Rendering 10,000 items naively
function ProductList({ products }) {
  return (
    <div className="product-list">
      {products.map(product => (
        <div key={product.id} className="product-card">
          <img src={product.image} alt={product.name} />
          <h3>{product.name}</h3>
          <p>${product.price}</p>
          <button>Add to Cart</button>
        </div>
      ))}
    </div>
  );
}

// With 10,000 products:
// - Creates 10,000 <div> containers
// - Creates 10,000 <img> elements (all start loading!)
// - Creates 10,000 <h3> elements
// - Creates 10,000 <p> elements
// - Creates 10,000 <button> elements
// = 50,000+ DOM nodes
//
// Result:
// - Initial render: 3-5 seconds
// - Memory usage: 500+ MB
// - Scrolling: janky, laggy
// - Page becomes unresponsive
```

```
Without Virtualization:

Viewport (what user sees):
+------------------------+
|  Item 45               |  <-- Visible
|  Item 46               |  <-- Visible
|  Item 47               |  <-- Visible
|  Item 48               |  <-- Visible
|  Item 49               |  <-- Visible
+------------------------+

But the DOM contains ALL items:
  Item 1     <-- Rendered but invisible (above viewport)
  Item 2     <-- Rendered but invisible
  ...
  Item 44    <-- Rendered but invisible
  Item 45    <-- VISIBLE
  Item 46    <-- VISIBLE
  Item 47    <-- VISIBLE
  Item 48    <-- VISIBLE
  Item 49    <-- VISIBLE
  Item 50    <-- Rendered but invisible (below viewport)
  ...
  Item 9,999 <-- Rendered but invisible
  Item 10,000<-- Rendered but invisible

DOM nodes: 10,000 (but only 5 are visible!)
```

---

## The Solution: Only Render What Is Visible

### How Virtualization Works

```
With Virtualization:

                    Overscan (buffer above)
                    +------------------------+
                    |  Item 43               |  <-- In DOM but not visible
                    |  Item 44               |  <-- In DOM but not visible
                    +------------------------+
Viewport:           +------------------------+
                    |  Item 45               |  <-- Visible
                    |  Item 46               |  <-- Visible
                    |  Item 47               |  <-- Visible
                    |  Item 48               |  <-- Visible
                    |  Item 49               |  <-- Visible
                    +------------------------+
                    +------------------------+
                    |  Item 50               |  <-- In DOM but not visible
                    |  Item 51               |  <-- In DOM but not visible
                    +------------------------+
                    Overscan (buffer below)

DOM nodes: 9 (instead of 10,000!)
Items 1-42 and 52-10,000 do NOT exist in the DOM.

The container div has a calculated total height to
maintain correct scrollbar behavior.
```

### The Window Calculation

```
Key Variables:
  containerHeight = 500px    (visible area height)
  itemHeight      = 50px     (each item's height)
  scrollTop       = 2200px   (how far user has scrolled)
  totalItems      = 10,000
  overscan        = 2        (extra items above and below)

Calculations:
  startIndex = floor(scrollTop / itemHeight)
             = floor(2200 / 50)
             = 44

  visibleCount = ceil(containerHeight / itemHeight)
               = ceil(500 / 50)
               = 10

  endIndex = startIndex + visibleCount
           = 44 + 10
           = 54

  With overscan:
    renderStart = max(0, startIndex - overscan)
                = max(0, 44 - 2)
                = 42

    renderEnd = min(totalItems - 1, endIndex + overscan)
              = min(9999, 54 + 2)
              = 56

  Items rendered: 42 through 56 = 15 items
  Total height of container: 10,000 * 50 = 500,000px
  (This makes the scrollbar look correct)

  Each rendered item is positioned absolutely:
    Item 42: top = 42 * 50 = 2100px
    Item 43: top = 43 * 50 = 2150px
    ...and so on
```

---

## Building a Simple Virtual List from Scratch

Understanding the concept by building it ourselves:

```jsx
import { useState, useRef, useCallback } from 'react';

function SimpleVirtualList({ items, itemHeight, containerHeight }) {
  const [scrollTop, setScrollTop] = useState(0);
  const containerRef = useRef(null);

  // Calculate which items are visible
  const startIndex = Math.max(
    0,
    Math.floor(scrollTop / itemHeight) - 2 // 2 items overscan
  );
  const endIndex = Math.min(
    items.length,
    Math.ceil((scrollTop + containerHeight) / itemHeight) + 2
  );

  // Total height to make scrollbar work correctly
  const totalHeight = items.length * itemHeight;

  // Only the visible items (plus overscan)
  const visibleItems = items.slice(startIndex, endIndex);

  const handleScroll = useCallback((e) => {
    setScrollTop(e.target.scrollTop);
  }, []);

  return (
    <div
      ref={containerRef}
      onScroll={handleScroll}
      style={{
        height: containerHeight,
        overflow: 'auto',
        position: 'relative',
      }}
    >
      {/* Spacer div creates correct total scroll height */}
      <div style={{ height: totalHeight }}>
        {visibleItems.map((item, index) => (
          <div
            key={startIndex + index}
            style={{
              position: 'absolute',
              top: (startIndex + index) * itemHeight,
              height: itemHeight,
              width: '100%',
            }}
          >
            {item.name} - ${item.price}
          </div>
        ))}
      </div>
    </div>
  );
}

// Usage:
function App() {
  // Generate 10,000 items
  const items = Array.from({ length: 10000 }, (_, i) => ({
    id: i,
    name: `Product ${i + 1}`,
    price: (Math.random() * 100).toFixed(2),
  }));

  return (
    <SimpleVirtualList
      items={items}
      itemHeight={50}
      containerHeight={500}
    />
  );
}

// Output:
// A scrollable list showing ~14 items at a time
// Scrollbar indicates 10,000 items
// Only ~14 DOM nodes exist at any moment
// Scrolling is smooth because React only updates ~14 elements
```

---

## Using react-window

Building virtualization from scratch is educational, but for production use a battle-tested library. `react-window` is the standard choice.

### Fixed-Size List

```jsx
import { FixedSizeList } from 'react-window';

// Row component receives index and style
function ProductRow({ index, style, data }) {
  const product = data[index];

  return (
    <div style={style} className="product-row">
      <span className="product-name">{product.name}</span>
      <span className="product-price">${product.price}</span>
      <button className="add-btn">Add to Cart</button>
    </div>
  );
}

function ProductList({ products }) {
  return (
    <FixedSizeList
      height={600}          // Viewport height
      width="100%"           // Full width
      itemCount={products.length}  // Total items
      itemSize={60}          // Each row height in pixels
      itemData={products}    // Passed to each Row as 'data' prop
      overscanCount={5}      // Render 5 extra items above/below
    >
      {ProductRow}
    </FixedSizeList>
  );
}

// Output:
// A 600px tall scrollable area
// Shows ~10 product rows at a time
// Smooth scrolling through all 10,000 products
// Only ~20 DOM nodes (10 visible + 5 overscan top + 5 bottom)
```

### Fixed-Size Grid

```jsx
import { FixedSizeGrid } from 'react-window';

function ProductCard({ columnIndex, rowIndex, style, data }) {
  const index = rowIndex * data.columnCount + columnIndex;

  if (index >= data.items.length) {
    return <div style={style} />; // Empty cell
  }

  const product = data.items[index];

  return (
    <div style={style} className="product-card">
      <div className="card-inner">
        <img
          src={product.thumbnail}
          alt={product.name}
          loading="lazy"
        />
        <h3>{product.name}</h3>
        <p>${product.price}</p>
      </div>
    </div>
  );
}

function ProductGrid({ products }) {
  const columnCount = 4;
  const rowCount = Math.ceil(products.length / columnCount);

  return (
    <FixedSizeGrid
      height={800}
      width={1200}
      columnCount={columnCount}
      columnWidth={300}
      rowCount={rowCount}
      rowHeight={350}
      itemData={{ items: products, columnCount }}
      overscanRowCount={2}
      overscanColumnCount={1}
    >
      {ProductCard}
    </FixedSizeGrid>
  );
}

// Output:
// A 4-column grid of product cards
// Each card is 300x350 pixels
// Only visible cards (plus overscan) exist in the DOM
// Scrolling through 2,500 rows (10,000 products / 4 columns)
```

### Variable-Size List

When items have different heights:

```jsx
import { VariableSizeList } from 'react-window';
import { useRef, useCallback } from 'react';

function MessageList({ messages }) {
  const listRef = useRef(null);

  // Calculate height for each message based on content
  const getItemSize = useCallback(
    (index) => {
      const message = messages[index];
      const baseHeight = 60; // padding + metadata
      const textLines = Math.ceil(message.text.length / 50);
      const textHeight = textLines * 20;
      const imageHeight = message.hasImage ? 200 : 0;
      return baseHeight + textHeight + imageHeight;
    },
    [messages]
  );

  return (
    <VariableSizeList
      ref={listRef}
      height={600}
      width="100%"
      itemCount={messages.length}
      itemSize={getItemSize}    // Function instead of fixed number
      estimatedItemSize={100}   // Helps with scrollbar accuracy
      overscanCount={3}
    >
      {({ index, style }) => {
        const message = messages[index];
        return (
          <div style={style} className="message">
            <div className="message-header">
              <strong>{message.author}</strong>
              <span>{message.time}</span>
            </div>
            <p>{message.text}</p>
            {message.hasImage && (
              <img src={message.imageUrl} alt="attachment" />
            )}
          </div>
        );
      }}
    </VariableSizeList>
  );
}

// Output:
// Chat-like message list
// Each message has different height based on text length
// Long messages take more space, short ones take less
// Still only renders visible messages
```

---

## Infinite Scroll + Virtualization

The real power comes from combining infinite scroll (loading more data as you scroll) with virtualization (only rendering visible items).

```jsx
import { FixedSizeList } from 'react-window';
import InfiniteLoader from 'react-window-infinite-loader';
import { useState, useCallback, useRef } from 'react';

function InfiniteProductList() {
  const [products, setProducts] = useState([]);
  const [hasMore, setHasMore] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const pageRef = useRef(1);

  // Total count: loaded items + 1 placeholder for "loading" row
  const itemCount = hasMore ? products.length + 1 : products.length;

  // Check if a specific item has been loaded
  const isItemLoaded = useCallback(
    (index) => !hasMore || index < products.length,
    [hasMore, products.length]
  );

  // Load more items when user scrolls near the end
  const loadMoreItems = useCallback(async () => {
    if (isLoading) return;
    setIsLoading(true);

    const response = await fetch(
      `/api/products?page=${pageRef.current}&limit=50`
    );
    const newProducts = await response.json();

    if (newProducts.length < 50) {
      setHasMore(false);
    }

    setProducts(prev => [...prev, ...newProducts]);
    pageRef.current += 1;
    setIsLoading(false);
  }, [isLoading]);

  // Row renderer
  const Row = useCallback(
    ({ index, style }) => {
      if (!isItemLoaded(index)) {
        return (
          <div style={style} className="loading-row">
            Loading more products...
          </div>
        );
      }

      const product = products[index];
      return (
        <div style={style} className="product-row">
          <span>{product.name}</span>
          <span>${product.price}</span>
        </div>
      );
    },
    [products, isItemLoaded]
  );

  return (
    <InfiniteLoader
      isItemLoaded={isItemLoaded}
      itemCount={itemCount}
      loadMoreItems={loadMoreItems}
      threshold={10}  // Start loading when 10 items from the end
    >
      {({ onItemsRendered, ref }) => (
        <FixedSizeList
          ref={ref}
          height={600}
          width="100%"
          itemCount={itemCount}
          itemSize={60}
          onItemsRendered={onItemsRendered}
          overscanCount={5}
        >
          {Row}
        </FixedSizeList>
      )}
    </InfiniteLoader>
  );
}

// Output behavior:
// 1. Initial load: fetches first 50 products, renders ~15 visible
// 2. User scrolls down to item 40
// 3. InfiniteLoader triggers loadMoreItems (threshold=10)
// 4. Next 50 products load while user keeps scrolling
// 5. Only ~25 DOM nodes exist at any time
// 6. User can scroll through 100,000+ products smoothly
```

```
Infinite Scroll + Virtualization Flow:

Products loaded:    [1-50]
DOM nodes:          [Items 1-15] (visible + overscan)
Scrollbar:          |||                                  (short)

User scrolls to item 40:
Products loaded:    [1-50]  --> triggers load --> [1-100]
DOM nodes:          [Items 35-55] (recycled)
Scrollbar:          ||||||||                             (growing)

User scrolls to item 90:
Products loaded:    [1-100] --> triggers load --> [1-150]
DOM nodes:          [Items 85-105] (recycled)
Scrollbar:          |||||||||||||                        (growing)

Key insight: DOM always has ~20 nodes regardless of total items!
```

---

## Real-World Use Case: Data Table with 100K Rows

```jsx
import { FixedSizeList } from 'react-window';
import { useState, useMemo, useCallback } from 'react';

function VirtualDataTable({ data, columns }) {
  const [sortColumn, setSortColumn] = useState(null);
  const [sortDirection, setSortDirection] = useState('asc');
  const [filter, setFilter] = useState('');

  // Filter and sort data (memoized for performance)
  const processedData = useMemo(() => {
    let result = data;

    // Apply filter
    if (filter) {
      const lowerFilter = filter.toLowerCase();
      result = result.filter(row =>
        columns.some(col =>
          String(row[col.key]).toLowerCase().includes(lowerFilter)
        )
      );
    }

    // Apply sort
    if (sortColumn) {
      result = [...result].sort((a, b) => {
        const aVal = a[sortColumn];
        const bVal = b[sortColumn];
        const modifier = sortDirection === 'asc' ? 1 : -1;
        if (aVal < bVal) return -1 * modifier;
        if (aVal > bVal) return 1 * modifier;
        return 0;
      });
    }

    return result;
  }, [data, filter, sortColumn, sortDirection, columns]);

  const handleSort = useCallback((column) => {
    setSortColumn(prev => {
      if (prev === column) {
        setSortDirection(d => (d === 'asc' ? 'desc' : 'asc'));
        return column;
      }
      setSortDirection('asc');
      return column;
    });
  }, []);

  // Table header (not virtualized - always visible)
  const Header = () => (
    <div className="table-header">
      {columns.map(col => (
        <div
          key={col.key}
          className="header-cell"
          onClick={() => handleSort(col.key)}
          style={{ width: col.width }}
        >
          {col.label}
          {sortColumn === col.key && (
            <span>{sortDirection === 'asc' ? ' ^' : ' v'}</span>
          )}
        </div>
      ))}
    </div>
  );

  // Virtualized row
  const Row = useCallback(
    ({ index, style }) => {
      const row = processedData[index];
      return (
        <div style={style} className="table-row">
          {columns.map(col => (
            <div
              key={col.key}
              className="table-cell"
              style={{ width: col.width }}
            >
              {row[col.key]}
            </div>
          ))}
        </div>
      );
    },
    [processedData, columns]
  );

  return (
    <div className="virtual-table">
      <div className="table-toolbar">
        <input
          type="text"
          placeholder="Filter..."
          value={filter}
          onChange={e => setFilter(e.target.value)}
        />
        <span>{processedData.length.toLocaleString()} rows</span>
      </div>

      <Header />

      <FixedSizeList
        height={600}
        width="100%"
        itemCount={processedData.length}
        itemSize={40}
        overscanCount={10}
      >
        {Row}
      </FixedSizeList>
    </div>
  );
}

// Usage:
const columns = [
  { key: 'id', label: 'ID', width: 80 },
  { key: 'name', label: 'Name', width: 200 },
  { key: 'email', label: 'Email', width: 250 },
  { key: 'department', label: 'Department', width: 150 },
  { key: 'salary', label: 'Salary', width: 120 },
];

// 100,000 rows, but DOM only has ~25 at any time
<VirtualDataTable data={hundredThousandRows} columns={columns} />

// Output:
// +------+----------------+--------------------+-----------+--------+
// | ID   | Name           | Email              | Dept      | Salary |
// +------+----------------+--------------------+-----------+--------+
// | 1    | Alice Johnson  | alice@example.com  | Eng       | 95000  |
// | 2    | Bob Smith      | bob@example.com    | Sales     | 72000  |
// | ...  | ...            | ...                | ...       | ...    |
// +------+----------------+--------------------+-----------+--------+
// Filter, sort, and scroll through 100K rows instantly
```

---

## When to Use / When NOT to Use

### Use Virtualization When

- Rendering lists with 100+ items that cause visible lag
- Building data tables with thousands of rows
- Creating infinite-scroll feeds (social media, news)
- Displaying large datasets (logs, analytics, search results)
- Mobile apps where memory is constrained

### Do NOT Use Virtualization When

- Lists have fewer than 50 items (the overhead is not worth it)
- All items must be in the DOM for accessibility or SEO (search engines cannot scroll)
- Items need to be measured by the browser for complex layouts (CSS Grid)
- You need `Ctrl+F` browser search to find text in the list
- Printing the page requires all items visible

---

## Common Mistakes

### Mistake 1: Creating Components Inside the Render Function

```jsx
// WRONG: Row component created on every render
function ProductList({ products }) {
  return (
    <FixedSizeList
      height={600}
      itemCount={products.length}
      itemSize={50}
    >
      {/* This creates a NEW function on every render */}
      {({ index, style }) => (
        <div style={style}>{products[index].name}</div>
      )}
    </FixedSizeList>
  );
  // Every scroll event re-creates ALL visible row components!
}

// RIGHT: Stable Row component defined outside or memoized
const Row = React.memo(({ index, style, data }) => (
  <div style={style}>{data[index].name}</div>
));

function ProductList({ products }) {
  return (
    <FixedSizeList
      height={600}
      itemCount={products.length}
      itemSize={50}
      itemData={products}
    >
      {Row}
    </FixedSizeList>
  );
}
```

### Mistake 2: Forgetting the `style` Prop

```jsx
// WRONG: Not applying the style prop
function Row({ index, style, data }) {
  return (
    <div className="row">
      {/* Missing style prop! Items stack on top of each other */}
      {data[index].name}
    </div>
  );
}

// RIGHT: Always spread the style prop
function Row({ index, style, data }) {
  return (
    <div style={style} className="row">
      {data[index].name}
    </div>
  );
}
// The style prop contains position: absolute, top, left, width, height
// It is how react-window positions each item correctly
```

### Mistake 3: Not Using `itemData` for External Data

```jsx
// WRONG: Closing over external data in the Row component
function ProductList({ products, onSelect }) {
  return (
    <FixedSizeList
      height={600}
      itemCount={products.length}
      itemSize={50}
    >
      {({ index, style }) => (
        <div style={style} onClick={() => onSelect(products[index])}>
          {products[index].name}
        </div>
      )}
    </FixedSizeList>
  );
  // products and onSelect changes cause ALL rows to re-render
}

// RIGHT: Pass through itemData
const Row = React.memo(({ index, style, data }) => (
  <div style={style} onClick={() => data.onSelect(data.products[index])}>
    {data.products[index].name}
  </div>
));

function ProductList({ products, onSelect }) {
  const itemData = useMemo(
    () => ({ products, onSelect }),
    [products, onSelect]
  );

  return (
    <FixedSizeList
      height={600}
      itemCount={products.length}
      itemSize={50}
      itemData={itemData}
    >
      {Row}
    </FixedSizeList>
  );
}
```

---

## Best Practices

1. **Measure first** -- Profile your list with React DevTools or Chrome DevTools before adding virtualization. If 200 items render fine without it, do not add complexity.

2. **Use `overscanCount`** -- A value of 3-5 prevents blank flashes during fast scrolling. Too high defeats the purpose of virtualization.

3. **Memoize row components** -- Wrap row components in `React.memo` to prevent unnecessary re-renders.

4. **Pass data through `itemData`** -- Instead of closing over variables, use the `itemData` prop. It integrates with `react-window`'s optimization.

5. **Use `estimatedItemSize`** -- For `VariableSizeList`, provide a good estimate for accurate scrollbar sizing.

6. **Lazy load images** -- Add `loading="lazy"` to images inside virtualized rows. Even though the row is not visible initially, the image should still load on demand.

7. **Handle window resize** -- If your container is responsive, reset the list cache with `list.resetAfterIndex(0)` when dimensions change.

8. **Test on low-end devices** -- Virtualization benefits are most visible on slower devices. Test there.

---

## Quick Summary

The Virtualization Pattern renders only the items currently visible in the viewport, plus a small buffer. This reduces the DOM from potentially tens of thousands of nodes to just a handful, dramatically improving memory usage and rendering performance. The core math involves calculating which items fall within the scroll window and positioning them absolutely within a container whose total height represents all items. Libraries like `react-window` handle the complexity for you. Combined with infinite scroll, virtualization makes it possible to display datasets of any size without performance degradation.

---

## Key Points

- **The problem**: Rendering thousands of DOM nodes causes lag, high memory use, and jank.
- **The solution**: Only create DOM nodes for visible items plus a small overscan buffer.
- **Window calculation**: `startIndex = floor(scrollTop / itemHeight)`, render from there.
- **react-window**: Production library for list and grid virtualization in React.
- **FixedSizeList**: All items have the same height (simplest, most performant).
- **VariableSizeList**: Items have different heights (needs a size function).
- **Infinite scroll**: Combine with `react-window-infinite-loader` for paginated data.
- **Overscan**: Extra items above/below viewport prevent blank flashes during fast scroll.

---

## Practice Questions

1. You have a list of 500 items. Each item is a simple text row. Should you use virtualization? What factors would influence your decision?

2. Explain why the total container height must equal `itemCount * itemHeight` even though most items are not in the DOM. What would happen if you did not set this height?

3. A developer reports that their virtualized list shows blank rows when scrolling quickly. What is likely causing this, and how would you fix it?

4. Why is it important to define the Row component outside the parent component (or memoize it with `useCallback`/`React.memo`) when using `react-window`?

5. Your virtualized list needs to support keyboard navigation where the user can press arrow keys to move selection up and down. What additional logic would you need to implement?

---

## Exercises

### Exercise 1: Build a Virtual List from Scratch

Without using any library, build a virtualized list component that:
- Accepts an array of items and an item height
- Calculates which items to render based on scroll position
- Positions items with absolute positioning
- Includes an overscan of 3 items above and below
- Handles the scroll event efficiently

### Exercise 2: Product Catalog with react-window

Create a product catalog that displays 5,000 products in a virtualized grid (4 columns). Each product card should show an image, name, price, and an "Add to Cart" button. Implement filtering by name and sorting by price, ensuring the virtualized list updates correctly.

### Exercise 3: Infinite Chat History

Build a chat application interface that loads message history as the user scrolls up (reverse infinite scroll). Use `react-window` with `VariableSizeList` since messages have different lengths. New messages should appear at the bottom and the scroll position should stay stable when older messages load above.

---

## What Is Next?

Virtualization handles the problem of too many items. But even with few items, your components might re-render too often, wasting CPU cycles recalculating values that have not changed. In Chapter 28, we will explore the **Memoization Pattern** -- using `React.memo`, `useMemo`, and `useCallback` to skip unnecessary work and keep your app responsive.
