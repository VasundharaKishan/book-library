# Chapter 32: Project -- Build a Complete E-Commerce Database

## What You Will Learn

In this chapter, you will build a complete e-commerce database from scratch. You will walk through every step of a real database project: gathering requirements, designing an ER diagram, creating normalized tables, inserting sample data, writing essential queries, building views, adding indexes, implementing triggers, and creating functions. By the end, you will have a fully functional database that could power an online store.

## Why This Chapter Matters

Throughout this book, you have learned SQL concepts one at a time. Now it is time to combine them all into a single, cohesive project. This is how real database work happens -- you do not just write one query in isolation. You design a system where tables, constraints, indexes, views, triggers, and functions all work together.

Building an e-commerce database is the perfect project because it touches almost every concept you have learned: data types, relationships, joins, aggregations, window functions, normalization, constraints, indexes, views, triggers, and stored functions.

Think of this chapter as your graduation project. When you finish it, you will have real, portfolio-worthy work.

---

## Step 1: Gathering Requirements

Before writing any SQL, we need to understand what we are building. Let us talk to our imaginary client.

**The client says:**

"We are building an online store. Customers need to create accounts, browse products organized by categories, add items to their cart, place orders, leave reviews, and make payments. We need to track inventory, calculate totals, and generate reports."

From this conversation, we extract the main entities:

```
+------------------+----------------------------------------------+
| Entity           | What It Represents                           |
+------------------+----------------------------------------------+
| Users            | Customer accounts                            |
| Categories       | Product groupings (Electronics, Books, etc.) |
| Products         | Items for sale                                |
| Orders           | Customer purchases                           |
| Order Items      | Individual items within an order              |
| Reviews          | Customer feedback on products                 |
| Payments         | Payment records for orders                   |
| Addresses        | Shipping and billing addresses               |
+------------------+----------------------------------------------+
```

### Key Business Rules

Before designing tables, we document the rules that govern the data:

1. A user can have multiple addresses (home, work, etc.).
2. A product belongs to exactly one category.
3. A product can have many reviews, but a user can review a product only once.
4. An order contains one or more items.
5. Each order item refers to a specific product with a quantity and price at the time of purchase.
6. An order has exactly one payment.
7. Products have a stock quantity that decreases when ordered.
8. We store the price on the order item (not just the product) because prices change over time.

---

## Step 2: ER Diagram

Here is the Entity-Relationship diagram for our e-commerce database:

```
+----------------+          +----------------+
|   categories   |          |    users       |
+----------------+          +----------------+
| id        (PK) |          | id        (PK) |
| name           |          | email          |
| description    |          | username       |
| created_at     |          | password_hash  |
+-------+--------+          | first_name     |
        |                   | last_name      |
        | 1                 | phone          |
        |                   | created_at     |
        | M                 | updated_at     |
+-------+--------+          +---+-----+------+
|   products     |              |     |
+----------------+              |     |
| id        (PK) |              |     |
| category_id(FK)|              |     |
| name           |         1    |     | 1
| description    |         |    |     |
| price          |         M    |     M
| stock_quantity |   +-----+----+-+  ++------------+
| image_url      |   |   addresses |  |   orders    |
| is_active      |   +-----------+   +-------------+
| created_at     |   | id    (PK)|   | id      (PK)|
| updated_at     |   | user_id(FK)|   | user_id (FK)|
+--+----------+--+   | type      |   | address_id  |
   |          |       | street    |   | status      |
   |          |       | city      |   | total_amount|
   |          |       | state     |   | created_at  |
   |          |       | zip_code  |   | updated_at  |
   | 1        | 1     | country   |   +---+-----+---+
   |          |       +-----------+       |     |
   | M        | M                         |     |
   |    +-----+------+             1     |     | 1
   |    |   reviews   |             |     |     |
   |    +-------------+             M     |     M
   |    | id      (PK)|    +--------+--+  |  +--+----------+
   |    | product_id  |    | order_items|  |  |  payments   |
   |    | user_id (FK)|    +--------+--+  |  +-------------+
   |    | rating      |    | id    (PK)|  |  | id      (PK)|
   |    | comment     |    | order_id  +--+  | order_id(FK)|
   |    | created_at  |    | product_id+-----+ amount      |
   |    +-------------+    | quantity  |     | method      |
   |                       | unit_price|     | status      |
   +----------+            | subtotal  |     | paid_at     |
              |            +-----------+     +-------------+
              |                  |
              +------------------+
                  (FK to products)
```

### Relationships Summary

```
+-------------------+---------------+---------------------------+
| Relationship      | Type          | Description               |
+-------------------+---------------+---------------------------+
| users-addresses   | One-to-Many   | User has many addresses   |
| users-orders      | One-to-Many   | User places many orders   |
| users-reviews     | One-to-Many   | User writes many reviews  |
| categories-products| One-to-Many  | Category has many products|
| products-reviews  | One-to-Many   | Product has many reviews  |
| orders-order_items| One-to-Many   | Order has many items      |
| products-order_items| One-to-Many | Product in many order items|
| orders-payments   | One-to-One    | Order has one payment     |
+-------------------+---------------+---------------------------+
```

---

## Step 3: Schema Design

Now let us create the actual tables. Each table is carefully designed with proper data types, constraints, and relationships.

### Users Table

```sql
CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(255) UNIQUE NOT NULL,
    username        VARCHAR(50) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    first_name      VARCHAR(100) NOT NULL,
    last_name       VARCHAR(100) NOT NULL,
    phone           VARCHAR(20),
    is_active       BOOLEAN DEFAULT true,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Line-by-line explanation:

- `id SERIAL PRIMARY KEY` -- Auto-incrementing unique identifier for each user.
- `email VARCHAR(255) UNIQUE NOT NULL` -- Email must be unique and cannot be empty. 255 characters covers any valid email.
- `username VARCHAR(50) UNIQUE NOT NULL` -- Short, unique display name.
- `password_hash VARCHAR(255) NOT NULL` -- We never store plain passwords. The application hashes them before insertion.
- `first_name`, `last_name` -- Real name for shipping and display.
- `phone VARCHAR(20)` -- Optional phone number. We use VARCHAR because phone numbers can have dashes, spaces, or country codes.
- `is_active BOOLEAN DEFAULT true` -- Allows soft-deleting users instead of removing their data.
- `created_at`, `updated_at` -- Track when the record was created and last modified.

### Categories Table

```sql
CREATE TABLE categories (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) UNIQUE NOT NULL,
    description     TEXT,
    parent_id       INTEGER REFERENCES categories(id),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

- `parent_id INTEGER REFERENCES categories(id)` -- This is a self-referencing foreign key. It allows categories to have subcategories. For example, "Laptops" could be a child of "Electronics."

### Products Table

```sql
CREATE TABLE products (
    id              SERIAL PRIMARY KEY,
    category_id     INTEGER NOT NULL REFERENCES categories(id),
    name            VARCHAR(200) NOT NULL,
    description     TEXT,
    price           NUMERIC(10, 2) NOT NULL CHECK (price > 0),
    stock_quantity  INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    image_url       VARCHAR(500),
    is_active       BOOLEAN DEFAULT true,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

- `price NUMERIC(10, 2) NOT NULL CHECK (price > 0)` -- Stores prices with exactly 2 decimal places. The CHECK constraint ensures prices are always positive. `NUMERIC(10,2)` supports values up to 99,999,999.99.
- `stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0)` -- Stock cannot go negative. This is a critical business rule enforced at the database level.

### Addresses Table

```sql
CREATE TABLE addresses (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    address_type    VARCHAR(20) NOT NULL CHECK (address_type IN ('shipping', 'billing')),
    street          VARCHAR(255) NOT NULL,
    city            VARCHAR(100) NOT NULL,
    state           VARCHAR(100) NOT NULL,
    zip_code        VARCHAR(20) NOT NULL,
    country         VARCHAR(100) NOT NULL DEFAULT 'United States',
    is_default      BOOLEAN DEFAULT false,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

- `ON DELETE CASCADE` -- If a user is deleted, their addresses are automatically removed.
- `address_type ... CHECK (...)` -- Limits address types to 'shipping' or 'billing'. This prevents invalid data.
- `is_default BOOLEAN DEFAULT false` -- Marks the user's preferred address.

### Orders Table

```sql
CREATE TABLE orders (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id),
    address_id      INTEGER REFERENCES addresses(id),
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'confirmed', 'shipped',
                                      'delivered', 'cancelled', 'refunded')),
    total_amount    NUMERIC(12, 2) NOT NULL DEFAULT 0,
    notes           TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

- `status ... CHECK (...)` -- Only allows valid order statuses. This prevents typos and invalid states.
- `total_amount NUMERIC(12, 2)` -- Supports order totals up to $9,999,999,999.99.

### Order Items Table

```sql
CREATE TABLE order_items (
    id              SERIAL PRIMARY KEY,
    order_id        INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id      INTEGER NOT NULL REFERENCES products(id),
    quantity        INTEGER NOT NULL CHECK (quantity > 0),
    unit_price      NUMERIC(10, 2) NOT NULL CHECK (unit_price > 0),
    subtotal        NUMERIC(12, 2) NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(order_id, product_id)
);
```

- `unit_price` -- We store the price at the time of purchase, not a reference to the product's current price. Prices change, but order history should not.
- `subtotal` -- Pre-calculated as `quantity * unit_price` for performance.
- `UNIQUE(order_id, product_id)` -- A product can appear only once per order (use quantity for multiples).

### Reviews Table

```sql
CREATE TABLE reviews (
    id              SERIAL PRIMARY KEY,
    product_id      INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rating          INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    title           VARCHAR(200),
    comment         TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(product_id, user_id)
);
```

- `rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5)` -- Ratings must be 1 through 5 stars.
- `UNIQUE(product_id, user_id)` -- A user can only review a product once.

### Payments Table

```sql
CREATE TABLE payments (
    id              SERIAL PRIMARY KEY,
    order_id        INTEGER UNIQUE NOT NULL REFERENCES orders(id),
    amount          NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
    payment_method  VARCHAR(50) NOT NULL
                    CHECK (payment_method IN ('credit_card', 'debit_card',
                                               'paypal', 'bank_transfer')),
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
    transaction_id  VARCHAR(100),
    paid_at         TIMESTAMP,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

- `order_id INTEGER UNIQUE NOT NULL` -- The UNIQUE constraint ensures each order has at most one payment, creating a one-to-one relationship.
- `transaction_id VARCHAR(100)` -- Stores the external payment processor's reference number.

---

## Step 4: Seed Data

Let us populate the database with realistic sample data.

### Insert Categories

```sql
INSERT INTO categories (name, description, parent_id) VALUES
    ('Electronics',    'Electronic devices and accessories',         NULL),
    ('Books',          'Physical and digital books',                 NULL),
    ('Clothing',       'Apparel and fashion items',                  NULL),
    ('Home & Garden',  'Home improvement and garden supplies',       NULL),
    ('Laptops',        'Portable computers',                         1),
    ('Smartphones',    'Mobile phones',                              1),
    ('Fiction',        'Fiction books and novels',                   2),
    ('Non-Fiction',    'Educational and informational books',        2),
    ('Men',            'Men clothing',                               3),
    ('Women',          'Women clothing',                             3);
```

```
+----+----------------+-------------------------------------------+-----------+
| id | name           | description                               | parent_id |
+----+----------------+-------------------------------------------+-----------+
|  1 | Electronics    | Electronic devices and accessories        |      NULL |
|  2 | Books          | Physical and digital books                |      NULL |
|  3 | Clothing       | Apparel and fashion items                 |      NULL |
|  4 | Home & Garden  | Home improvement and garden supplies      |      NULL |
|  5 | Laptops        | Portable computers                        |         1 |
|  6 | Smartphones    | Mobile phones                             |         1 |
|  7 | Fiction        | Fiction books and novels                  |         2 |
|  8 | Non-Fiction    | Educational and informational books       |         2 |
|  9 | Men            | Men clothing                              |         3 |
| 10 | Women          | Women clothing                            |         3 |
+----+----------------+-------------------------------------------+-----------+
(10 rows)
```

### Insert Users

```sql
INSERT INTO users (email, username, password_hash, first_name, last_name, phone) VALUES
    ('alice@example.com',   'alice_j',   '$2b$12$hash1...', 'Alice',   'Johnson',  '555-0101'),
    ('bob@example.com',     'bob_smith',  '$2b$12$hash2...', 'Bob',     'Smith',    '555-0102'),
    ('carol@example.com',   'carol_w',    '$2b$12$hash3...', 'Carol',   'Williams', '555-0103'),
    ('david@example.com',   'david_b',    '$2b$12$hash4...', 'David',   'Brown',    '555-0104'),
    ('eve@example.com',     'eve_d',      '$2b$12$hash5...', 'Eve',     'Davis',    '555-0105'),
    ('frank@example.com',   'frank_m',    '$2b$12$hash6...', 'Frank',   'Miller',   '555-0106'),
    ('grace@example.com',   'grace_t',    '$2b$12$hash7...', 'Grace',   'Taylor',   NULL),
    ('henry@example.com',   'henry_a',    '$2b$12$hash8...', 'Henry',   'Anderson', '555-0108');
```

### Insert Addresses

```sql
INSERT INTO addresses (user_id, address_type, street, city, state, zip_code, country, is_default) VALUES
    (1, 'shipping', '123 Oak Street',    'Portland',    'Oregon',       '97201', 'United States', true),
    (1, 'billing',  '123 Oak Street',    'Portland',    'Oregon',       '97201', 'United States', false),
    (2, 'shipping', '456 Maple Avenue',  'Seattle',     'Washington',   '98101', 'United States', true),
    (3, 'shipping', '789 Pine Road',     'San Francisco','California',  '94102', 'United States', true),
    (4, 'shipping', '321 Elm Drive',     'Denver',      'Colorado',     '80201', 'United States', true),
    (5, 'shipping', '654 Cedar Lane',    'Austin',      'Texas',        '73301', 'United States', true),
    (6, 'shipping', '987 Birch Court',   'Chicago',     'Illinois',     '60601', 'United States', true),
    (7, 'shipping', '147 Willow Way',    'Miami',       'Florida',      '33101', 'United States', true),
    (8, 'shipping', '258 Spruce Place',  'New York',    'New York',     '10001', 'United States', true);
```

### Insert Products

```sql
INSERT INTO products (category_id, name, description, price, stock_quantity, is_active) VALUES
    (5,  'ProBook Laptop 15',       'High-performance 15-inch laptop with 16GB RAM',      999.99,  50, true),
    (5,  'UltraSlim Notebook',      'Lightweight 13-inch notebook for everyday use',      699.99,  75, true),
    (6,  'SmartPhone X200',         'Latest smartphone with 128GB storage',                799.99,  100, true),
    (6,  'SmartPhone Lite',         'Budget-friendly smartphone with great camera',        349.99,  200, true),
    (7,  'The Great Adventure',     'A thrilling fiction novel about exploration',           14.99,  500, true),
    (7,  'Mystery at Midnight',     'A page-turning mystery thriller',                      12.99,  300, true),
    (8,  'Learn SQL in 30 Days',    'Complete guide to SQL for beginners',                  29.99,  250, true),
    (8,  'Data Science Handbook',   'Comprehensive reference for data professionals',       39.99,  150, true),
    (9,  'Classic Cotton T-Shirt',  'Comfortable cotton t-shirt in multiple colors',        19.99,  1000, true),
    (9,  'Slim Fit Jeans',          'Modern slim fit denim jeans',                          49.99,  400, true),
    (10, 'Summer Dress',            'Light and breezy summer dress with floral pattern',    59.99,  200, true),
    (10, 'Wool Blend Sweater',      'Warm wool blend sweater for cold weather',             79.99,  150, true),
    (4,  'Garden Tool Set',         '5-piece stainless steel garden tool set',              34.99,  80, true),
    (4,  'Indoor Plant Pot',        'Ceramic indoor plant pot with drainage',               24.99,  120, true),
    (1,  'Wireless Earbuds',        'Bluetooth wireless earbuds with noise cancellation',  129.99,  300, true);
```

### Insert Orders

```sql
INSERT INTO orders (user_id, address_id, status, total_amount, created_at) VALUES
    (1, 1, 'delivered',  1049.98, '2025-01-05 10:30:00'),
    (1, 1, 'delivered',    29.99, '2025-02-14 14:20:00'),
    (2, 3, 'delivered',   849.98, '2025-01-10 09:15:00'),
    (2, 3, 'shipped',     349.99, '2025-03-01 16:45:00'),
    (3, 4, 'delivered',   114.97, '2025-01-20 11:00:00'),
    (3, 4, 'delivered',    59.99, '2025-02-28 13:30:00'),
    (4, 5, 'confirmed',  1029.98, '2025-03-10 08:00:00'),
    (5, 6, 'delivered',    64.98, '2025-01-15 15:00:00'),
    (5, 6, 'pending',     799.99, '2025-03-15 10:00:00'),
    (6, 7, 'delivered',   159.98, '2025-02-01 12:00:00'),
    (7, 8, 'delivered',    39.99, '2025-02-10 09:30:00'),
    (8, 9, 'cancelled',   699.99, '2025-03-05 14:00:00'),
    (1, 1, 'delivered',    79.98, '2025-03-20 11:15:00'),
    (3, 4, 'pending',     129.99, '2025-03-25 16:00:00');
```

### Insert Order Items

```sql
INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal) VALUES
    (1,  1,  1,  999.99,   999.99),
    (1,  9,  1,   49.99,    49.99),
    (2,  7,  1,   29.99,    29.99),
    (3,  3,  1,  799.99,   799.99),
    (3,  9,  1,   49.99,    49.99),
    (4,  4,  1,  349.99,   349.99),
    (5,  5,  3,   14.99,    44.97),
    (5,  6,  2,   12.99,    25.98),
    (5, 13,  1,   34.99,    34.99),
    (5, 14,  1,    9.03,     9.03),
    (6, 11,  1,   59.99,    59.99),
    (7,  1,  1,  999.99,   999.99),
    (7,  7,  1,   29.99,    29.99),
    (8,  9,  2,   19.99,    39.98),
    (8, 14,  1,   24.99,    24.99),
    (9,  3,  1,  799.99,   799.99),
    (10, 12, 2,   79.99,   159.98),
    (11,  8, 1,   39.99,    39.99),
    (12,  2, 1,  699.99,   699.99),
    (13,  9, 2,   19.99,    39.98),
    (13, 10, 1,   49.99,    49.99),
    (13, 14, 1,   24.99,    24.99),
    (14, 15, 1,  129.99,   129.99);
```

### Insert Reviews

```sql
INSERT INTO reviews (product_id, user_id, rating, title, comment, created_at) VALUES
    (1,  1, 5, 'Excellent laptop',          'Fast, reliable, great battery life.',             '2025-01-20'),
    (1,  3, 4, 'Good but heavy',            'Great performance but a bit heavy to carry.',     '2025-02-15'),
    (3,  2, 5, 'Best phone ever',           'Amazing camera and smooth performance.',          '2025-01-25'),
    (3,  5, 4, 'Great phone',               'Love the camera. Battery could be better.',       '2025-02-20'),
    (7,  1, 5, 'Must read!',                'Learned more than I expected. Highly recommend.', '2025-03-01'),
    (7,  3, 4, 'Very helpful',              'Good for beginners. Could use more examples.',    '2025-03-10'),
    (5,  3, 5, 'Couldn''t put it down',     'Read it in one sitting. Amazing story.',          '2025-02-05'),
    (9,  5, 4, 'Comfortable',               'Fits well, comfortable material.',                '2025-01-30'),
    (9,  1, 3, 'Decent quality',            'OK for the price, but shrinks after washing.',    '2025-04-01'),
    (11, 3, 5, 'Beautiful dress',           'Perfect for summer. Love the pattern.',            '2025-03-15'),
    (12, 6, 4, 'Warm and cozy',             'Perfect for winter. Slight pilling after wash.',   '2025-02-25'),
    (15, 5, 5, 'Amazing sound quality',     'Great noise cancellation and battery life.',       '2025-03-20'),
    (8,  7, 4, 'Comprehensive reference',   'Covers everything you need. Well organized.',     '2025-02-28'),
    (4,  2, 4, 'Good budget phone',         'Great value for money. Does everything I need.',  '2025-03-05'),
    (13, 5, 5, 'Built to last',             'Sturdy tools. Great for weekend gardening.',      '2025-02-01');
```

### Insert Payments

```sql
INSERT INTO payments (order_id, amount, payment_method, status, transaction_id, paid_at) VALUES
    (1,  1049.98, 'credit_card',   'completed', 'TXN-001-2025', '2025-01-05 10:31:00'),
    (2,    29.99, 'credit_card',   'completed', 'TXN-002-2025', '2025-02-14 14:21:00'),
    (3,   849.98, 'paypal',        'completed', 'TXN-003-2025', '2025-01-10 09:16:00'),
    (4,   349.99, 'debit_card',    'completed', 'TXN-004-2025', '2025-03-01 16:46:00'),
    (5,   114.97, 'credit_card',   'completed', 'TXN-005-2025', '2025-01-20 11:01:00'),
    (6,    59.99, 'paypal',        'completed', 'TXN-006-2025', '2025-02-28 13:31:00'),
    (7,  1029.98, 'credit_card',   'pending',    NULL,           NULL),
    (8,    64.98, 'bank_transfer', 'completed', 'TXN-008-2025', '2025-01-15 15:01:00'),
    (9,   799.99, 'credit_card',   'pending',    NULL,           NULL),
    (10,  159.98, 'credit_card',   'completed', 'TXN-010-2025', '2025-02-01 12:01:00'),
    (11,   39.99, 'debit_card',    'completed', 'TXN-011-2025', '2025-02-10 09:31:00'),
    (12,  699.99, 'credit_card',   'refunded',  'TXN-012-2025', '2025-03-05 14:01:00'),
    (13,   79.98, 'paypal',        'completed', 'TXN-013-2025', '2025-03-20 11:16:00'),
    (14,  129.99, 'credit_card',   'pending',    NULL,           NULL);
```

---

## Step 5: Essential Queries

Now that we have data, let us write the queries that a real e-commerce application would need.

### Query 1: Top-Selling Products

Which products sell the most?

```sql
SELECT
    p.name                          AS product_name,
    c.name                          AS category,
    SUM(oi.quantity)                AS total_sold,
    SUM(oi.subtotal)                AS total_revenue,
    ROUND(AVG(r.rating), 1)        AS avg_rating
FROM products p
JOIN categories c ON c.id = p.category_id
JOIN order_items oi ON oi.product_id = p.id
JOIN orders o ON o.id = oi.order_id AND o.status != 'cancelled'
LEFT JOIN reviews r ON r.product_id = p.id
GROUP BY p.id, p.name, c.name
ORDER BY total_sold DESC
LIMIT 10;
```

```
+------------------------+--------------+------------+---------------+------------+
| product_name           | category     | total_sold | total_revenue | avg_rating |
+------------------------+--------------+------------+---------------+------------+
| Classic Cotton T-Shirt | Men          |          5 |        149.95 |        3.5 |
| Indoor Plant Pot       | Home & Garden|          3 |         59.01 |       NULL |
| Slim Fit Jeans         | Men          |          2 |         99.98 |       NULL |
| ProBook Laptop 15      | Laptops      |          2 |       1999.98 |        4.5 |
| SmartPhone X200        | Smartphones  |          2 |       1599.98 |        4.5 |
| Learn SQL in 30 Days   | Non-Fiction  |          2 |         59.98 |        4.5 |
| The Great Adventure    | Fiction      |          3 |         44.97 |        5.0 |
| Mystery at Midnight    | Fiction      |          2 |         25.98 |       NULL |
| SmartPhone Lite        | Smartphones  |          1 |        349.99 |        4.0 |
| Summer Dress           | Women        |          1 |         59.99 |        5.0 |
+------------------------+--------------+------------+---------------+------------+
(10 rows)
```

Let us break down this query:

- We join `products` with `categories` to get category names.
- We join with `order_items` to count sales and revenue.
- We filter out cancelled orders with `o.status != 'cancelled'`.
- We LEFT JOIN with `reviews` because not all products have reviews.
- We group by product to aggregate the totals.
- We sort by `total_sold` descending to see top sellers first.

### Query 2: Customer Order History

Show a customer's complete order history:

```sql
SELECT
    o.id                            AS order_id,
    o.created_at::DATE              AS order_date,
    o.status,
    COUNT(oi.id)                    AS item_count,
    o.total_amount,
    p.status                        AS payment_status,
    p.payment_method
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
JOIN payments p ON p.order_id = o.id
WHERE o.user_id = 1
GROUP BY o.id, o.created_at, o.status, o.total_amount, p.status, p.payment_method
ORDER BY o.created_at DESC;
```

```
+----------+------------+-----------+------------+--------------+----------------+----------------+
| order_id | order_date | status    | item_count | total_amount | payment_status | payment_method |
+----------+------------+-----------+------------+--------------+----------------+----------------+
|       13 | 2025-03-20 | delivered |          3 |        79.98 | completed      | paypal         |
|        2 | 2025-02-14 | delivered |          1 |        29.99 | completed      | credit_card    |
|        1 | 2025-01-05 | delivered |          2 |      1049.98 | completed      | credit_card    |
+----------+------------+-----------+------------+--------------+----------------+----------------+
(3 rows)
```

### Query 3: Revenue by Month

How much revenue are we making each month?

```sql
SELECT
    TO_CHAR(o.created_at, 'YYYY-MM')    AS month,
    COUNT(DISTINCT o.id)                 AS order_count,
    SUM(o.total_amount)                  AS gross_revenue,
    SUM(CASE WHEN o.status = 'cancelled' THEN o.total_amount ELSE 0 END)
                                         AS cancelled_amount,
    SUM(CASE WHEN o.status != 'cancelled' THEN o.total_amount ELSE 0 END)
                                         AS net_revenue
FROM orders o
GROUP BY TO_CHAR(o.created_at, 'YYYY-MM')
ORDER BY month;
```

```
+---------+-------------+---------------+------------------+-------------+
| month   | order_count | gross_revenue | cancelled_amount | net_revenue |
+---------+-------------+---------------+------------------+-------------+
| 2025-01 | 4           |       2079.91 |             0.00 |     2079.91 |
| 2025-02 | 3           |        229.96 |             0.00 |      229.96 |
| 2025-03 | 7           |       3169.91 |           699.99 |     2469.92 |
+---------+-------------+---------------+------------------+-------------+
(3 rows)
```

This query uses `CASE` expressions to separate cancelled orders from net revenue.

### Query 4: Inventory Check -- Low Stock Products

Which products are running low on stock?

```sql
SELECT
    p.name,
    p.stock_quantity,
    c.name AS category,
    CASE
        WHEN p.stock_quantity = 0 THEN 'OUT OF STOCK'
        WHEN p.stock_quantity < 20 THEN 'CRITICAL'
        WHEN p.stock_quantity < 50 THEN 'LOW'
        WHEN p.stock_quantity < 100 THEN 'MODERATE'
        ELSE 'GOOD'
    END AS stock_status
FROM products p
JOIN categories c ON c.id = p.category_id
WHERE p.is_active = true
ORDER BY p.stock_quantity ASC;
```

```
+------------------------+----------------+---------------+--------------+
| name                   | stock_quantity | category      | stock_status |
+------------------------+----------------+---------------+--------------+
| ProBook Laptop 15      |             50 | Laptops       | MODERATE     |
| UltraSlim Notebook     |             75 | Laptops       | MODERATE     |
| Garden Tool Set        |             80 | Home & Garden | MODERATE     |
| SmartPhone X200        |            100 | Smartphones   | GOOD         |
| Indoor Plant Pot       |            120 | Home & Garden | GOOD         |
| Data Science Handbook  |            150 | Non-Fiction   | GOOD         |
| Wool Blend Sweater     |            150 | Women         | GOOD         |
| SmartPhone Lite        |            200 | Smartphones   | GOOD         |
| Summer Dress           |            200 | Women         | GOOD         |
| Learn SQL in 30 Days   |            250 | Non-Fiction   | GOOD         |
| Wireless Earbuds       |            300 | Electronics   | GOOD         |
| Mystery at Midnight    |            300 | Fiction       | GOOD         |
| Slim Fit Jeans         |            400 | Men           | GOOD         |
| The Great Adventure    |            500 | Fiction       | GOOD         |
| Classic Cotton T-Shirt |           1000 | Men           | GOOD         |
+------------------------+----------------+---------------+--------------+
(15 rows)
```

### Query 5: Product Search with Reviews

A query that powers the product search page with average ratings:

```sql
SELECT
    p.id,
    p.name,
    p.price,
    p.stock_quantity,
    c.name                                      AS category,
    COALESCE(ROUND(AVG(r.rating), 1), 0)        AS avg_rating,
    COUNT(r.id)                                  AS review_count
FROM products p
JOIN categories c ON c.id = p.category_id
LEFT JOIN reviews r ON r.product_id = p.id
WHERE p.is_active = true
  AND p.name ILIKE '%phone%'
GROUP BY p.id, p.name, p.price, p.stock_quantity, c.name
ORDER BY avg_rating DESC, review_count DESC;
```

```
+----+------------------+--------+----------------+-------------+------------+--------------+
| id | name             | price  | stock_quantity | category    | avg_rating | review_count |
+----+------------------+--------+----------------+-------------+------------+--------------+
|  3 | SmartPhone X200  | 799.99 |            100 | Smartphones |        4.5 |            2 |
|  4 | SmartPhone Lite  | 349.99 |            200 | Smartphones |        4.0 |            1 |
+----+------------------+--------+----------------+-------------+------------+--------------+
(2 rows)
```

Notice the use of `ILIKE` for case-insensitive search and `COALESCE` to show 0 instead of NULL for products with no reviews.

---

## Step 6: Views

Views simplify complex queries and provide a clean interface for your application.

### Product Catalog View

This view powers the main product listing page:

```sql
CREATE VIEW product_catalog AS
SELECT
    p.id                                        AS product_id,
    p.name                                      AS product_name,
    p.description,
    p.price,
    p.stock_quantity,
    p.image_url,
    c.name                                      AS category_name,
    parent_cat.name                             AS parent_category,
    CASE
        WHEN p.stock_quantity > 0 THEN true
        ELSE false
    END                                         AS in_stock,
    COALESCE(ROUND(AVG(r.rating), 1), 0)        AS avg_rating,
    COUNT(r.id)                                 AS review_count
FROM products p
JOIN categories c ON c.id = p.category_id
LEFT JOIN categories parent_cat ON parent_cat.id = c.parent_id
LEFT JOIN reviews r ON r.product_id = p.id
WHERE p.is_active = true
GROUP BY p.id, p.name, p.description, p.price, p.stock_quantity,
         p.image_url, c.name, parent_cat.name;
```

Now the application can simply query:

```sql
SELECT * FROM product_catalog
WHERE category_name = 'Laptops'
ORDER BY avg_rating DESC;
```

```
+------------+---------------------+-------------------------------+--------+----------+-----------+----------+-------------+---------+--------+--------+
| product_id | product_name        | description                   | price  | stock_qty| image_url | category | parent_cat  | in_stock| rating | reviews|
+------------+---------------------+-------------------------------+--------+----------+-----------+----------+-------------+---------+--------+--------+
|          1 | ProBook Laptop 15   | High-performance 15-inch...   | 999.99 |       50 | NULL      | Laptops  | Electronics | t       |    4.5 |      2 |
|          2 | UltraSlim Notebook  | Lightweight 13-inch...        | 699.99 |       75 | NULL      | Laptops  | Electronics | t       |    0.0 |      0 |
+------------+---------------------+-------------------------------+--------+----------+-----------+----------+-------------+---------+--------+--------+
(2 rows)
```

### Order Summary View

This view provides a complete order overview:

```sql
CREATE VIEW order_summary AS
SELECT
    o.id                            AS order_id,
    o.created_at                    AS order_date,
    o.status                        AS order_status,
    u.id                            AS customer_id,
    u.first_name || ' ' || u.last_name AS customer_name,
    u.email                         AS customer_email,
    COUNT(oi.id)                    AS item_count,
    SUM(oi.quantity)                AS total_items,
    o.total_amount,
    p.payment_method,
    p.status                        AS payment_status,
    a.city || ', ' || a.state       AS shipping_location
FROM orders o
JOIN users u ON u.id = o.user_id
JOIN order_items oi ON oi.order_id = o.id
LEFT JOIN payments p ON p.order_id = o.id
LEFT JOIN addresses a ON a.id = o.address_id
GROUP BY o.id, o.created_at, o.status, u.id, u.first_name, u.last_name,
         u.email, o.total_amount, p.payment_method, p.status, a.city, a.state;
```

```sql
SELECT order_id, order_date::DATE, order_status, customer_name,
       item_count, total_amount, payment_status
FROM order_summary
ORDER BY order_date DESC
LIMIT 5;
```

```
+----------+------------+--------------+-----------------+------------+--------------+----------------+
| order_id | order_date | order_status | customer_name   | item_count | total_amount | payment_status |
+----------+------------+--------------+-----------------+------------+--------------+----------------+
|       14 | 2025-03-25 | pending      | Carol Williams  |          1 |       129.99 | pending        |
|       13 | 2025-03-20 | delivered    | Alice Johnson   |          3 |        79.98 | completed      |
|        9 | 2025-03-15 | pending      | Eve Davis       |          1 |       799.99 | pending        |
|        7 | 2025-03-10 | confirmed    | David Brown     |          2 |      1029.98 | pending        |
|       12 | 2025-03-05 | cancelled    | Henry Anderson  |          1 |       699.99 | refunded       |
+----------+------------+--------------+-----------------+------------+--------------+----------------+
(5 rows)
```

### Customer Dashboard View

Everything a customer needs to see on their dashboard:

```sql
CREATE VIEW customer_dashboard AS
SELECT
    u.id                                AS user_id,
    u.first_name,
    u.last_name,
    u.email,
    u.created_at                        AS member_since,
    COUNT(DISTINCT o.id)                AS total_orders,
    COALESCE(SUM(
        CASE WHEN o.status != 'cancelled' THEN o.total_amount ELSE 0 END
    ), 0)                               AS total_spent,
    COALESCE(AVG(
        CASE WHEN o.status != 'cancelled' THEN o.total_amount END
    ), 0)                               AS avg_order_value,
    MAX(o.created_at)                   AS last_order_date,
    COUNT(DISTINCT rv.id)               AS reviews_written
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
LEFT JOIN reviews rv ON rv.user_id = u.id
GROUP BY u.id, u.first_name, u.last_name, u.email, u.created_at;
```

```sql
SELECT first_name, last_name, total_orders,
       ROUND(total_spent, 2) AS total_spent,
       ROUND(avg_order_value, 2) AS avg_order,
       reviews_written
FROM customer_dashboard
ORDER BY total_spent DESC;
```

```
+------------+-----------+--------------+-------------+-----------+-----------------+
| first_name | last_name | total_orders | total_spent | avg_order | reviews_written |
+------------+-----------+--------------+-------------+-----------+-----------------+
| Alice      | Johnson   |            3 |     1159.95 |    386.65 |               3 |
| Carol      | Williams  |            3 |      304.95 |    101.65 |               3 |
| David      | Brown     |            1 |     1029.98 |   1029.98 |               0 |
| Bob        | Smith     |            2 |     1199.97 |    599.99 |               2 |
| Eve        | Davis     |            2 |      864.97 |    432.49 |               3 |
| Frank      | Miller    |            1 |      159.98 |    159.98 |               1 |
| Grace      | Taylor    |            1 |       39.99 |     39.99 |               1 |
| Henry      | Anderson  |            1 |        0.00 |      0.00 |               0 |
+------------+-----------+--------------+-------------+-----------+-----------------+
(8 rows)
```

---

## Step 7: Indexes for Performance

Without indexes, the database scans every row in a table to find matches. As your data grows, this becomes slow. Indexes are like the table of contents in a book -- they help the database jump directly to the right page.

### Primary Key and Unique Indexes

PostgreSQL automatically creates indexes for primary keys and unique constraints. We already have those. Let us add indexes for the columns we frequently search and join on.

```sql
-- Users: search by email (login), username
CREATE INDEX idx_users_email ON users (email);
-- Already covered by UNIQUE constraint, but explicit for clarity

-- Products: filter by category, search by name, filter active products
CREATE INDEX idx_products_category ON products (category_id);
CREATE INDEX idx_products_name ON products USING gin (to_tsvector('english', name));
CREATE INDEX idx_products_active ON products (is_active) WHERE is_active = true;

-- Orders: find orders by user, filter by status, sort by date
CREATE INDEX idx_orders_user ON orders (user_id);
CREATE INDEX idx_orders_status ON orders (status);
CREATE INDEX idx_orders_created ON orders (created_at DESC);

-- Order Items: lookup by order and product
CREATE INDEX idx_order_items_order ON order_items (order_id);
CREATE INDEX idx_order_items_product ON order_items (product_id);

-- Reviews: find reviews for a product, reviews by a user
CREATE INDEX idx_reviews_product ON reviews (product_id);
CREATE INDEX idx_reviews_user ON reviews (user_id);

-- Payments: lookup by order
CREATE INDEX idx_payments_order ON payments (order_id);

-- Addresses: find addresses for a user
CREATE INDEX idx_addresses_user ON addresses (user_id);
```

Let us explain a few interesting ones:

- `USING gin (to_tsvector('english', name))` -- This is a full-text search index. It allows fast searches like "find products with 'laptop' in the name" using PostgreSQL's text search features.
- `WHERE is_active = true` -- This is a partial index. It only indexes active products, making it smaller and faster because we rarely query inactive products.
- `(created_at DESC)` -- The index is sorted in descending order, which matches our most common query pattern (newest orders first).

### Verifying Indexes Are Used

```sql
EXPLAIN ANALYZE
SELECT * FROM orders
WHERE user_id = 1
ORDER BY created_at DESC;
```

```
                                                    QUERY PLAN
-------------------------------------------------------------------------------------------------------------------
 Sort  (cost=8.18..8.19 rows=3 width=52) (actual time=0.045..0.046 rows=3 loops=1)
   Sort Key: created_at DESC
   Sort Method: quicksort  Memory: 25kB
   ->  Index Scan using idx_orders_user on orders  (cost=0.14..8.16 rows=3 width=52)
         (actual time=0.020..0.025 rows=3 loops=1)
         Index Cond: (user_id = 1)
 Planning Time: 0.112 ms
 Execution Time: 0.072 ms
```

The output shows "Index Scan using idx_orders_user" which means PostgreSQL used our index instead of scanning every row.

---

## Step 8: Triggers

Triggers automatically run code when certain events happen. They enforce business rules that cannot be expressed with simple constraints.

### Trigger 1: Auto-Update updated_at Timestamp

Every time a row is modified, we want the `updated_at` column to reflect the current time:

```sql
-- Step 1: Create the trigger function
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

Line-by-line explanation:

- `CREATE OR REPLACE FUNCTION` -- Creates the function or replaces it if it exists.
- `RETURNS TRIGGER` -- This function is designed to be called by a trigger.
- `NEW.updated_at = CURRENT_TIMESTAMP` -- `NEW` refers to the row being inserted or updated. We set its `updated_at` to the current time.
- `RETURN NEW` -- Returns the modified row. If we returned NULL, the operation would be cancelled.

```sql
-- Step 2: Attach the trigger to tables
CREATE TRIGGER trigger_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
```

Now let us test it:

```sql
-- Check current timestamp
SELECT id, name, updated_at FROM products WHERE id = 1;
```

```
+----+-------------------+---------------------+
| id | name              | updated_at          |
+----+-------------------+---------------------+
|  1 | ProBook Laptop 15 | 2025-01-01 00:00:00 |
+----+-------------------+---------------------+
```

```sql
-- Update the product
UPDATE products SET price = 949.99 WHERE id = 1;

-- Check again
SELECT id, name, price, updated_at FROM products WHERE id = 1;
```

```
+----+-------------------+--------+---------------------+
| id | name              | price  | updated_at          |
+----+-------------------+--------+---------------------+
|  1 | ProBook Laptop 15 | 949.99 | 2025-03-29 14:35:22 |
+----+-------------------+--------+---------------------+
```

The `updated_at` column was automatically set to the current timestamp without us explicitly updating it.

### Trigger 2: Reduce Stock When Order Is Placed

When an order item is inserted, reduce the product's stock quantity:

```sql
CREATE OR REPLACE FUNCTION reduce_stock_on_order()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if enough stock is available
    IF (SELECT stock_quantity FROM products WHERE id = NEW.product_id) < NEW.quantity THEN
        RAISE EXCEPTION 'Insufficient stock for product ID %. Requested: %, Available: %',
            NEW.product_id,
            NEW.quantity,
            (SELECT stock_quantity FROM products WHERE id = NEW.product_id);
    END IF;

    -- Reduce the stock
    UPDATE products
    SET stock_quantity = stock_quantity - NEW.quantity
    WHERE id = NEW.product_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_reduce_stock
    AFTER INSERT ON order_items
    FOR EACH ROW
    EXECUTE FUNCTION reduce_stock_on_order();
```

Let us break down the logic:

1. First, we check if the product has enough stock. If not, we raise an exception, which cancels the INSERT and rolls back the transaction.
2. If stock is available, we subtract the ordered quantity from the product's `stock_quantity`.
3. We use `AFTER INSERT` because we want the order item to be saved first, then reduce stock.

Let us test it:

```sql
-- Check current stock
SELECT id, name, stock_quantity FROM products WHERE id = 1;
```

```
+----+-------------------+----------------+
| id | name              | stock_quantity |
+----+-------------------+----------------+
|  1 | ProBook Laptop 15 |             50 |
+----+-------------------+----------------+
```

```sql
-- Insert a new order item (this triggers stock reduction)
INSERT INTO orders (user_id, address_id, status, total_amount)
VALUES (1, 1, 'pending', 949.99);

INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
VALUES (15, 1, 2, 949.99, 1899.98);

-- Check stock again
SELECT id, name, stock_quantity FROM products WHERE id = 1;
```

```
+----+-------------------+----------------+
| id | name              | stock_quantity |
+----+-------------------+----------------+
|  1 | ProBook Laptop 15 |             48 |
+----+-------------------+----------------+
```

The stock dropped from 50 to 48 automatically.

### Trigger 3: Restore Stock When Order Is Cancelled

```sql
CREATE OR REPLACE FUNCTION restore_stock_on_cancel()
RETURNS TRIGGER AS $$
BEGIN
    -- Only restore if status changes to 'cancelled'
    IF NEW.status = 'cancelled' AND OLD.status != 'cancelled' THEN
        UPDATE products p
        SET stock_quantity = p.stock_quantity + oi.quantity
        FROM order_items oi
        WHERE oi.order_id = NEW.id
          AND p.id = oi.product_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_restore_stock_on_cancel
    AFTER UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION restore_stock_on_cancel();
```

This trigger fires when an order is updated. It checks if the status changed to 'cancelled' (and was not already cancelled), then adds the quantities back to the products.

---

## Step 9: Functions

Functions encapsulate complex logic that you use repeatedly. They keep your application code clean and ensure consistency.

### Function 1: Calculate Order Total

This function recalculates the total for an order based on its items:

```sql
CREATE OR REPLACE FUNCTION calculate_order_total(p_order_id INTEGER)
RETURNS NUMERIC AS $$
DECLARE
    v_total NUMERIC(12, 2);
BEGIN
    -- Sum all order item subtotals
    SELECT COALESCE(SUM(subtotal), 0)
    INTO v_total
    FROM order_items
    WHERE order_id = p_order_id;

    -- Update the order's total_amount
    UPDATE orders
    SET total_amount = v_total
    WHERE id = p_order_id;

    RETURN v_total;
END;
$$ LANGUAGE plpgsql;
```

Line-by-line explanation:

- `p_order_id INTEGER` -- The function takes an order ID as input.
- `RETURNS NUMERIC` -- It returns the calculated total.
- `DECLARE v_total NUMERIC(12, 2)` -- We declare a variable to hold the total.
- `SELECT ... INTO v_total` -- The query result is stored in our variable.
- `COALESCE(SUM(subtotal), 0)` -- If there are no items, return 0 instead of NULL.
- `UPDATE orders SET total_amount = v_total` -- Also update the order record.
- `RETURN v_total` -- Return the calculated total to the caller.

Using it:

```sql
SELECT calculate_order_total(1);
```

```
+--------------------------+
| calculate_order_total    |
+--------------------------+
|                  1049.98 |
+--------------------------+
(1 row)
```

### Function 2: Apply Discount

This function applies a percentage discount to an order:

```sql
CREATE OR REPLACE FUNCTION apply_discount(
    p_order_id      INTEGER,
    p_discount_pct  NUMERIC
)
RETURNS TABLE (
    original_total  NUMERIC,
    discount_amount NUMERIC,
    final_total     NUMERIC
) AS $$
DECLARE
    v_original  NUMERIC(12, 2);
    v_discount  NUMERIC(12, 2);
    v_final     NUMERIC(12, 2);
BEGIN
    -- Validate discount percentage
    IF p_discount_pct < 0 OR p_discount_pct > 100 THEN
        RAISE EXCEPTION 'Discount must be between 0 and 100. Got: %', p_discount_pct;
    END IF;

    -- Get current total
    SELECT total_amount INTO v_original
    FROM orders
    WHERE id = p_order_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Order % not found', p_order_id;
    END IF;

    -- Calculate discount
    v_discount := ROUND(v_original * p_discount_pct / 100, 2);
    v_final := v_original - v_discount;

    -- Update the order
    UPDATE orders
    SET total_amount = v_final
    WHERE id = p_order_id;

    -- Return the details
    RETURN QUERY SELECT v_original, v_discount, v_final;
END;
$$ LANGUAGE plpgsql;
```

This function:

1. Validates that the discount percentage is between 0 and 100.
2. Looks up the current order total.
3. Raises an error if the order does not exist.
4. Calculates the discount amount and new total.
5. Updates the order record.
6. Returns a table with the original total, discount amount, and final total.

Using it:

```sql
SELECT * FROM apply_discount(5, 10);
```

```
+----------------+-----------------+-------------+
| original_total | discount_amount | final_total |
+----------------+-----------------+-------------+
|         114.97 |           11.50 |      103.47 |
+----------------+-----------------+-------------+
(1 row)
```

### Function 3: Get Product Recommendations

Find products frequently bought together:

```sql
CREATE OR REPLACE FUNCTION get_recommendations(p_product_id INTEGER, p_limit INTEGER DEFAULT 5)
RETURNS TABLE (
    recommended_product_id   INTEGER,
    product_name             VARCHAR,
    category                 VARCHAR,
    price                    NUMERIC,
    times_bought_together    BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.id,
        p.name,
        c.name,
        p.price,
        COUNT(*) AS times_together
    FROM order_items oi1
    JOIN order_items oi2 ON oi2.order_id = oi1.order_id
                         AND oi2.product_id != oi1.product_id
    JOIN products p ON p.id = oi2.product_id
    JOIN categories c ON c.id = p.category_id
    WHERE oi1.product_id = p_product_id
      AND p.is_active = true
    GROUP BY p.id, p.name, c.name, p.price
    ORDER BY times_together DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;
```

Using it:

```sql
SELECT * FROM get_recommendations(1);
```

```
+------------------------+-----------------------+-----------+--------+-------------------------+
| recommended_product_id | product_name          | category  | price  | times_bought_together   |
+------------------------+-----------------------+-----------+--------+-------------------------+
|                      9 | Classic Cotton T-Shirt | Men      |  19.99 |                       1 |
|                      7 | Learn SQL in 30 Days  | Non-Fic. |  29.99 |                       1 |
+------------------------+-----------------------+-----------+--------+-------------------------+
(2 rows)
```

This query finds products that appear in the same orders as the given product. This is the "Customers who bought this also bought..." feature you see on e-commerce sites.

---

## Complete Code Reference

Here is the complete setup script for the entire e-commerce database. You can run this from start to finish to create everything:

```sql
-- ============================================================
-- E-COMMERCE DATABASE - COMPLETE SETUP SCRIPT
-- ============================================================

-- 1. CREATE TABLES
-- (All CREATE TABLE statements from Step 3 above)

-- 2. INSERT SEED DATA
-- (All INSERT statements from Step 4 above)

-- 3. CREATE VIEWS
-- (All CREATE VIEW statements from Step 6 above)

-- 4. CREATE INDEXES
-- (All CREATE INDEX statements from Step 7 above)

-- 5. CREATE TRIGGER FUNCTIONS AND TRIGGERS
-- (All trigger code from Step 8 above)

-- 6. CREATE FUNCTIONS
-- (All function code from Step 9 above)

-- 7. VERIFY EVERYTHING WORKS
SELECT 'Users:      ' || COUNT(*) FROM users
UNION ALL
SELECT 'Categories: ' || COUNT(*) FROM categories
UNION ALL
SELECT 'Products:   ' || COUNT(*) FROM products
UNION ALL
SELECT 'Orders:     ' || COUNT(*) FROM orders
UNION ALL
SELECT 'Order Items:' || COUNT(*) FROM order_items
UNION ALL
SELECT 'Reviews:    ' || COUNT(*) FROM reviews
UNION ALL
SELECT 'Payments:   ' || COUNT(*) FROM payments
UNION ALL
SELECT 'Addresses:  ' || COUNT(*) FROM addresses;
```

```
+-----------------------+
| ?column?              |
+-----------------------+
| Users:      8         |
| Categories: 10        |
| Products:   15        |
| Orders:     14        |
| Order Items:23        |
| Reviews:    15        |
| Payments:   14        |
| Addresses:  9         |
+-----------------------+
(8 rows)
```

---

## Common Mistakes

1. **Storing current product price in order items.** Always store the price at the time of purchase. Prices change, but order history should not.

2. **Not using CHECK constraints for enums.** Without `CHECK (status IN (...))`, someone could insert an order with status 'banana'. Use constraints to enforce valid values.

3. **Forgetting ON DELETE CASCADE or ON DELETE SET NULL.** Without these, deleting a user would fail if they have orders. Plan your delete behavior during design.

4. **Using FLOAT for money.** Always use `NUMERIC(precision, scale)` for financial data. FLOAT introduces rounding errors (try `0.1 + 0.2` in floating point).

5. **Not indexing foreign key columns.** Joins are the most common queries. Without indexes on foreign key columns, joins become slow as data grows.

6. **Creating too many indexes.** Each index speeds up reads but slows down writes. Only index columns you actually query on.

---

## Best Practices

1. **Design before coding.** Create the ER diagram and document business rules before writing any SQL.

2. **Use NUMERIC for money.** Never use FLOAT or REAL for financial values. NUMERIC provides exact decimal arithmetic.

3. **Add constraints at the database level.** Do not rely only on application code to validate data. Use CHECK, NOT NULL, UNIQUE, and FOREIGN KEY constraints.

4. **Store prices on order items.** Always capture the price at the time of purchase, not a reference to the product table.

5. **Use views for complex queries.** If your application frequently runs the same complex query, create a view. It simplifies code and centralizes logic.

6. **Index foreign keys and frequently filtered columns.** Focus on columns used in WHERE clauses, JOIN conditions, and ORDER BY.

7. **Use triggers for automatic updates.** The `updated_at` trigger pattern is standard practice. It ensures timestamps are always accurate.

8. **Test with realistic data.** Seed your database with enough data to test performance and edge cases.

---

## Quick Summary

You built a complete e-commerce database from scratch:

- **Requirements** defined 8 entities and their business rules.
- **ER diagram** mapped the relationships between entities.
- **Schema** created 8 normalized tables with proper constraints.
- **Seed data** populated the database with realistic sample data.
- **Queries** answered real business questions (top products, revenue, inventory).
- **Views** simplified complex queries for the application layer.
- **Indexes** optimized performance for common query patterns.
- **Triggers** automated stock management and timestamp updates.
- **Functions** encapsulated reusable business logic.

---

## Key Points

- Always start a database project by gathering requirements and documenting business rules.
- Draw an ER diagram before creating tables. It catches design problems early.
- Use proper data types and constraints to enforce data integrity at the database level.
- Store historical values (like prices) on transactional records, not just references.
- Views abstract complex queries and provide a clean API for applications.
- Index columns that appear in WHERE, JOIN, and ORDER BY clauses.
- Use triggers to enforce business rules that constraints cannot express.
- Functions encapsulate reusable logic and keep application code clean.

---

## Practice Questions

1. A customer wants to see all products they have ever purchased with quantities and prices. Write the query.

2. The business team asks: "Which category generates the most revenue?" Write a query that shows revenue by category, sorted from highest to lowest.

3. Why do we store `unit_price` on the `order_items` table instead of just joining to the `products` table for the price?

4. What would happen if we used `ON DELETE CASCADE` on the `orders.user_id` foreign key? Is that a good idea? Why or why not?

5. How would you modify the schema to support products that belong to multiple categories? What changes would be needed?

---

## Exercises

### Exercise 1: Add a Wishlist Feature

Design and implement a wishlist feature:

1. Create a `wishlists` table where users can save products they want to buy later.
2. Each user can have only one entry per product in their wishlist.
3. Write a query to show a user's wishlist with product details, current price, and stock status.
4. Write a query to find the most-wishlisted products.

### Exercise 2: Add a Coupon System

Extend the database with a coupon system:

1. Create a `coupons` table with fields for code, discount type (percentage or fixed amount), discount value, minimum order amount, expiry date, and usage limit.
2. Create an `order_coupons` junction table to track which coupons were applied to which orders.
3. Write a function that validates and applies a coupon to an order.

### Exercise 3: Build a Reporting Dashboard

Write these dashboard queries:

1. Daily revenue for the last 30 days (including days with zero revenue).
2. Customer lifetime value ranking (total spent by each customer, with rank).
3. Product performance report: for each product, show total sold, revenue, average rating, return rate (cancelled orders / total orders), and a performance score.

---

## What Is Next?

Congratulations! You have just built a production-quality database. In the next chapter, you will use similar data to write advanced analytics queries: revenue trends, year-over-year growth, customer cohort analysis, RFM segmentation, and more. These are the queries that turn raw data into business insights.
