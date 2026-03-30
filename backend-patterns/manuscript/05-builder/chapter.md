# Chapter 5: The Builder Pattern

## What You Will Learn

- What the Builder pattern is and the "telescoping constructor" problem it solves
- How to implement Builder in Java with a QueryBuilder and HttpRequestBuilder
- How to implement Builder in Python with a ReportBuilder
- What a fluent interface is and how Builder enables it
- The Director pattern and when to use it
- How Lombok's `@Builder` annotation generates builders automatically
- When NOT to use Builder (simple objects with few parameters)

## Why This Chapter Matters

Every backend developer has encountered a class with too many constructor parameters. A database query might need a table, columns, conditions, sorting, limits, joins, and grouping. An HTTP request needs a URL, method, headers, body, timeout, retry policy, and authentication. A report needs a title, date range, format, filters, sorting, and pagination.

When a constructor has 10 or 15 parameters, the code becomes unreadable and error-prone. Which parameter was the timeout again -- the seventh or the eighth? The Builder pattern solves this by letting you construct complex objects step by step, with clear, readable code that makes mistakes nearly impossible.

This pattern is everywhere in backend development: SQL query builders, HTTP client libraries, test data factories, and configuration objects all use it.

---

## The Problem: Telescoping Constructor

The "telescoping constructor" anti-pattern happens when you create multiple constructors with increasing numbers of parameters to handle optional values.

**Before (Telescoping Constructor) - Java:**

```java
public class HttpRequest {

    private final String url;
    private final String method;
    private final Map<String, String> headers;
    private final String body;
    private final int timeoutMs;
    private final int maxRetries;
    private final boolean followRedirects;
    private final String authToken;
    private final String contentType;
    private final boolean verifySsl;
    private final String proxyHost;
    private final int proxyPort;

    // Constructor with ALL parameters - who can read this?
    public HttpRequest(String url, String method,
                       Map<String, String> headers,
                       String body, int timeoutMs,
                       int maxRetries, boolean followRedirects,
                       String authToken, String contentType,
                       boolean verifySsl, String proxyHost,
                       int proxyPort) {
        this.url = url;
        this.method = method;
        this.headers = headers;
        this.body = body;
        this.timeoutMs = timeoutMs;
        this.maxRetries = maxRetries;
        this.followRedirects = followRedirects;
        this.authToken = authToken;
        this.contentType = contentType;
        this.verifySsl = verifySsl;
        this.proxyHost = proxyHost;
        this.proxyPort = proxyPort;
    }
}

// Usage - can you tell what each parameter means?
HttpRequest request = new HttpRequest(
    "https://api.example.com/users",  // url
    "POST",                            // method
    null,                              // headers
    "{\"name\": \"John\"}",           // body
    5000,                              // timeout? retries?
    3,                                 // retries? timeout?
    true,                              // follow redirects?
    "Bearer abc123",                   // auth token
    "application/json",                // content type
    true,                              // verify SSL?
    null,                              // proxy host
    0                                  // proxy port
);
```

**Before (Telescoping Constructor) - Python:**

```python
class HttpRequest:
    def __init__(self, url, method="GET", headers=None,
                 body=None, timeout_ms=30000, max_retries=0,
                 follow_redirects=True, auth_token=None,
                 content_type=None, verify_ssl=True,
                 proxy_host=None, proxy_port=None):
        self.url = url
        self.method = method
        self.headers = headers or {}
        self.body = body
        self.timeout_ms = timeout_ms
        self.max_retries = max_retries
        self.follow_redirects = follow_redirects
        self.auth_token = auth_token
        self.content_type = content_type
        self.verify_ssl = verify_ssl
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port

# Usage - slightly better with keyword args, but still messy
request = HttpRequest(
    "https://api.example.com/users",
    method="POST",
    body='{"name": "John"}',
    timeout_ms=5000,
    max_retries=3,
    auth_token="Bearer abc123",
    content_type="application/json",
)
```

```
THE TELESCOPING CONSTRUCTOR PROBLEMS:

  1. READABILITY
     new HttpRequest("url", "POST", null, body, 5000, 3, true, ...)
     Which parameter is which? You have to count positions.

  2. PARAMETER CONFUSION
     Was 5000 the timeout or the max retries?
     Easy to swap adjacent parameters of the same type.

  3. NULL FILLER
     You must pass null for optional parameters you do not need.
     new HttpRequest("url", "GET", null, null, 5000, 0, true,
                     null, null, true, null, 0)

  4. IMMUTABILITY
     Setters solve readability but sacrifice immutability.
     A half-built mutable object is a bug waiting to happen.

  5. VALIDATION
     When do you validate? In the constructor? What if
     required parameters are missing? With 12 parameters,
     validation logic becomes a mess.
```

---

## The Solution: Builder Pattern

The Builder pattern separates the construction of a complex object from its representation, allowing the same construction process to create different representations.

```
+---------------------------------------------------------------+
|                    BUILDER PATTERN                             |
+---------------------------------------------------------------+
|                                                               |
|  INTENT: Separate the construction of a complex object        |
|          from its representation so that the same              |
|          construction process can create different             |
|          representations.                                     |
|                                                               |
|  CATEGORY: Creational                                         |
|                                                               |
+---------------------------------------------------------------+

  UML-like Structure:

  +-------------------+        +-------------------+
  |    Director       |------->|    Builder         |
  | (optional)        |        |    (interface)     |
  +-------------------+        +-------------------+
  | + construct()     |        | + setPartA()      |
  +-------------------+        | + setPartB()      |
                               | + build(): Product |
                               +-------------------+
                                       ^
                                       |
                               +-------------------+
                               | ConcreteBuilder    |
                               +-------------------+
                               | - product          |
                               | + setPartA()       |
                               | + setPartB()       |
                               | + build(): Product |
                               +-------------------+
                                       |
                                       | creates
                                       v
                               +-------------------+
                               |    Product         |
                               +-------------------+

  How the fluent interface works:

  Product product = new Builder()
      .setPartA("value")     // returns Builder (this)
      .setPartB("value")     // returns Builder (this)
      .setPartC("value")     // returns Builder (this)
      .build();              // returns Product

  Each method returns the builder itself,
  enabling method chaining.
```

---

## Java Implementation 1: HttpRequestBuilder

### The Product Class

```java
/**
 * The product: an immutable HTTP request.
 * All fields are final. No setters. Once built, it cannot change.
 */
public class HttpRequest {

    private final String url;
    private final String method;
    private final Map<String, String> headers;
    private final String body;
    private final int timeoutMs;
    private final int maxRetries;
    private final boolean followRedirects;
    private final String authToken;
    private final String contentType;
    private final boolean verifySsl;

    // Package-private constructor - only the Builder can call this
    HttpRequest(Builder builder) {
        this.url = builder.url;
        this.method = builder.method;
        this.headers = Collections.unmodifiableMap(
            new HashMap<>(builder.headers)
        );
        this.body = builder.body;
        this.timeoutMs = builder.timeoutMs;
        this.maxRetries = builder.maxRetries;
        this.followRedirects = builder.followRedirects;
        this.authToken = builder.authToken;
        this.contentType = builder.contentType;
        this.verifySsl = builder.verifySsl;
    }

    // Getters only - no setters
    public String getUrl() { return url; }
    public String getMethod() { return method; }
    public Map<String, String> getHeaders() { return headers; }
    public String getBody() { return body; }
    public int getTimeoutMs() { return timeoutMs; }
    public int getMaxRetries() { return maxRetries; }
    public boolean isFollowRedirects() { return followRedirects; }
    public String getAuthToken() { return authToken; }
    public String getContentType() { return contentType; }
    public boolean isVerifySsl() { return verifySsl; }

    @Override
    public String toString() {
        return method + " " + url + "\n"
            + "Content-Type: " + contentType + "\n"
            + "Authorization: " + (authToken != null
                ? authToken.substring(0, 10) + "..." : "none")
            + "\n"
            + "Timeout: " + timeoutMs + "ms, "
            + "Retries: " + maxRetries + "\n"
            + "Body: " + (body != null
                ? body.substring(0, Math.min(50, body.length()))
                : "none");
    }

    /**
     * The Builder - a static inner class.
     */
    public static class Builder {

        // Required parameters
        private final String url;

        // Optional parameters with defaults
        private String method = "GET";
        private Map<String, String> headers = new HashMap<>();
        private String body = null;
        private int timeoutMs = 30000;
        private int maxRetries = 0;
        private boolean followRedirects = true;
        private String authToken = null;
        private String contentType = "application/json";
        private boolean verifySsl = true;

        /**
         * Constructor takes ONLY required parameters.
         */
        public Builder(String url) {
            if (url == null || url.isEmpty()) {
                throw new IllegalArgumentException("URL is required");
            }
            this.url = url;
        }

        /**
         * Each setter returns 'this' for method chaining.
         */
        public Builder method(String method) {
            this.method = method;
            return this;                 // <-- returns Builder
        }

        public Builder header(String key, String value) {
            this.headers.put(key, value);
            return this;
        }

        public Builder body(String body) {
            this.body = body;
            return this;
        }

        public Builder timeoutMs(int timeoutMs) {
            if (timeoutMs <= 0) {
                throw new IllegalArgumentException(
                    "Timeout must be positive"
                );
            }
            this.timeoutMs = timeoutMs;
            return this;
        }

        public Builder maxRetries(int maxRetries) {
            if (maxRetries < 0) {
                throw new IllegalArgumentException(
                    "Retries cannot be negative"
                );
            }
            this.maxRetries = maxRetries;
            return this;
        }

        public Builder followRedirects(boolean followRedirects) {
            this.followRedirects = followRedirects;
            return this;
        }

        public Builder authToken(String authToken) {
            this.authToken = authToken;
            return this;
        }

        public Builder contentType(String contentType) {
            this.contentType = contentType;
            return this;
        }

        public Builder verifySsl(boolean verifySsl) {
            this.verifySsl = verifySsl;
            return this;
        }

        /**
         * Build the final immutable HttpRequest.
         * Validation happens here.
         */
        public HttpRequest build() {
            // Validate the complete state
            if ("POST".equals(method) || "PUT".equals(method)) {
                if (body == null) {
                    throw new IllegalStateException(
                        method + " requests require a body"
                    );
                }
            }
            return new HttpRequest(this);
        }
    }
}
```

**Line-by-line explanation of key concepts:**

- The `HttpRequest` constructor is package-private and takes a `Builder`. External code cannot construct it directly.
- Every field in `HttpRequest` is `final`. The object is immutable after construction.
- The `Builder` constructor takes only required parameters (`url`). Everything else is optional with sensible defaults.
- Each setter method returns `this` (the Builder itself). This enables the fluent interface: method chaining.
- `build()` validates the complete state and creates the immutable product.

### Usage and Output

```java
public class Main {
    public static void main(String[] args) {

        // Simple GET request - just the URL
        HttpRequest getRequest = new HttpRequest.Builder(
                "https://api.example.com/users"
            )
            .build();

        System.out.println(getRequest);
        System.out.println();

        // Complex POST request - readable and self-documenting
        HttpRequest postRequest = new HttpRequest.Builder(
                "https://api.example.com/users"
            )
            .method("POST")
            .body("{\"name\": \"John\", \"email\": \"john@example.com\"}")
            .contentType("application/json")
            .authToken("Bearer eyJhbGciOiJIUzI1NiJ9.abc123")
            .timeoutMs(5000)
            .maxRetries(3)
            .header("X-Request-ID", "req-12345")
            .header("X-Client-Version", "2.1.0")
            .build();

        System.out.println(postRequest);
    }
}
```

```
Output:
GET https://api.example.com/users
Content-Type: application/json
Authorization: none
Timeout: 30000ms, Retries: 0
Body: none

POST https://api.example.com/users
Content-Type: application/json
Authorization: Bearer eyJ...
Timeout: 5000ms, Retries: 3
Body: {"name": "John", "email": "john@example.com"}
```

Compare the readability:

```
BEFORE (telescoping constructor):
  new HttpRequest("url", "POST", null, body, 5000, 3,
                  true, "Bearer abc", "application/json",
                  true, null, 0);

AFTER (builder):
  new HttpRequest.Builder("url")
      .method("POST")
      .body(body)
      .timeoutMs(5000)
      .maxRetries(3)
      .authToken("Bearer abc")
      .contentType("application/json")
      .build();

  Every parameter is labeled. No nulls. No counting.
```

---

## Java Implementation 2: QueryBuilder

```java
public class SqlQuery {

    private final String sql;

    private SqlQuery(String sql) {
        this.sql = sql;
    }

    public String getSql() {
        return sql;
    }

    @Override
    public String toString() {
        return sql;
    }

    public static class Builder {

        private String table;
        private List<String> columns = new ArrayList<>();
        private List<String> conditions = new ArrayList<>();
        private List<String> joins = new ArrayList<>();
        private String orderBy;
        private String orderDirection = "ASC";
        private Integer limit;
        private Integer offset;
        private List<String> groupBy = new ArrayList<>();
        private String having;

        public Builder select(String... columns) {
            this.columns.addAll(Arrays.asList(columns));
            return this;
        }

        public Builder from(String table) {
            this.table = table;
            return this;
        }

        public Builder where(String condition) {
            this.conditions.add(condition);
            return this;
        }

        public Builder innerJoin(String table, String on) {
            this.joins.add("INNER JOIN " + table + " ON " + on);
            return this;
        }

        public Builder leftJoin(String table, String on) {
            this.joins.add("LEFT JOIN " + table + " ON " + on);
            return this;
        }

        public Builder orderBy(String column, String direction) {
            this.orderBy = column;
            this.orderDirection = direction;
            return this;
        }

        public Builder limit(int limit) {
            this.limit = limit;
            return this;
        }

        public Builder offset(int offset) {
            this.offset = offset;
            return this;
        }

        public Builder groupBy(String... columns) {
            this.groupBy.addAll(Arrays.asList(columns));
            return this;
        }

        public Builder having(String condition) {
            this.having = condition;
            return this;
        }

        public SqlQuery build() {
            if (table == null) {
                throw new IllegalStateException(
                    "Table (FROM) is required"
                );
            }

            StringBuilder sql = new StringBuilder();

            // SELECT
            sql.append("SELECT ");
            if (columns.isEmpty()) {
                sql.append("*");
            } else {
                sql.append(String.join(", ", columns));
            }

            // FROM
            sql.append("\nFROM ").append(table);

            // JOINs
            for (String join : joins) {
                sql.append("\n").append(join);
            }

            // WHERE
            if (!conditions.isEmpty()) {
                sql.append("\nWHERE ")
                   .append(String.join(" AND ", conditions));
            }

            // GROUP BY
            if (!groupBy.isEmpty()) {
                sql.append("\nGROUP BY ")
                   .append(String.join(", ", groupBy));
            }

            // HAVING
            if (having != null) {
                sql.append("\nHAVING ").append(having);
            }

            // ORDER BY
            if (orderBy != null) {
                sql.append("\nORDER BY ")
                   .append(orderBy)
                   .append(" ")
                   .append(orderDirection);
            }

            // LIMIT & OFFSET
            if (limit != null) {
                sql.append("\nLIMIT ").append(limit);
            }
            if (offset != null) {
                sql.append("\nOFFSET ").append(offset);
            }

            sql.append(";");
            return new SqlQuery(sql.toString());
        }
    }
}
```

**Usage and output:**

```java
// Simple query
SqlQuery simple = new SqlQuery.Builder()
    .select("id", "name", "email")
    .from("users")
    .where("active = true")
    .limit(10)
    .build();

System.out.println(simple);
```

```
Output:
SELECT id, name, email
FROM users
WHERE active = true
LIMIT 10;
```

```java
// Complex query with joins, grouping, and pagination
SqlQuery complex = new SqlQuery.Builder()
    .select("u.name", "COUNT(o.id) AS order_count",
            "SUM(o.total) AS total_spent")
    .from("users u")
    .innerJoin("orders o", "u.id = o.user_id")
    .leftJoin("discounts d", "o.discount_id = d.id")
    .where("u.active = true")
    .where("o.created_at > '2024-01-01'")
    .groupBy("u.id", "u.name")
    .having("COUNT(o.id) > 5")
    .orderBy("total_spent", "DESC")
    .limit(20)
    .offset(40)
    .build();

System.out.println(complex);
```

```
Output:
SELECT u.name, COUNT(o.id) AS order_count, SUM(o.total) AS total_spent
FROM users u
INNER JOIN orders o ON u.id = o.user_id
LEFT JOIN discounts d ON o.discount_id = d.id
WHERE u.active = true AND o.created_at > '2024-01-01'
GROUP BY u.id, u.name
HAVING COUNT(o.id) > 5
ORDER BY total_spent DESC
LIMIT 20
OFFSET 40;
```

---

## Python Implementation: ReportBuilder

```python
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from enum import Enum


class ReportFormat(Enum):
    PDF = "pdf"
    CSV = "csv"
    EXCEL = "excel"
    HTML = "html"


@dataclass(frozen=True)
class Report:
    """
    Immutable report object. The frozen=True makes it immutable.
    Only the Builder can create instances.
    """
    title: str
    description: str
    format: ReportFormat
    start_date: date
    end_date: date
    columns: List[str]
    filters: Dict[str, Any]
    sort_by: Optional[str]
    sort_order: str
    page_size: int
    include_totals: bool
    include_charts: bool
    header_text: Optional[str]
    footer_text: Optional[str]

    def __str__(self) -> str:
        lines = [
            f"=== Report: {self.title} ===",
            f"Description: {self.description}",
            f"Format: {self.format.value.upper()}",
            f"Date Range: {self.start_date} to {self.end_date}",
            f"Columns: {', '.join(self.columns)}",
            f"Filters: {self.filters}",
            f"Sort: {self.sort_by} {self.sort_order}"
            if self.sort_by else "Sort: none",
            f"Page Size: {self.page_size}",
            f"Totals: {'Yes' if self.include_totals else 'No'}",
            f"Charts: {'Yes' if self.include_charts else 'No'}",
        ]
        if self.header_text:
            lines.append(f"Header: {self.header_text}")
        if self.footer_text:
            lines.append(f"Footer: {self.footer_text}")
        return "\n".join(lines)


class ReportBuilder:
    """
    Builder for the Report object.
    Provides a fluent interface for step-by-step construction.
    """

    def __init__(self, title: str):
        """Constructor takes only the required parameter."""
        if not title:
            raise ValueError("Title is required")
        self._title = title
        self._description = ""
        self._format = ReportFormat.PDF
        self._start_date = date.today()
        self._end_date = date.today()
        self._columns: List[str] = []
        self._filters: Dict[str, Any] = {}
        self._sort_by: Optional[str] = None
        self._sort_order = "ASC"
        self._page_size = 50
        self._include_totals = False
        self._include_charts = False
        self._header_text: Optional[str] = None
        self._footer_text: Optional[str] = None

    def description(self, description: str) -> "ReportBuilder":
        self._description = description
        return self

    def format(self, fmt: ReportFormat) -> "ReportBuilder":
        self._format = fmt
        return self

    def date_range(self, start: date,
                   end: date) -> "ReportBuilder":
        if start > end:
            raise ValueError("Start date must be before end date")
        self._start_date = start
        self._end_date = end
        return self

    def columns(self, *cols: str) -> "ReportBuilder":
        self._columns.extend(cols)
        return self

    def filter(self, key: str, value: Any) -> "ReportBuilder":
        self._filters[key] = value
        return self

    def sort_by(self, column: str,
                order: str = "ASC") -> "ReportBuilder":
        if order not in ("ASC", "DESC"):
            raise ValueError("Order must be ASC or DESC")
        self._sort_by = column
        self._sort_order = order
        return self

    def page_size(self, size: int) -> "ReportBuilder":
        if size <= 0:
            raise ValueError("Page size must be positive")
        self._page_size = size
        return self

    def with_totals(self) -> "ReportBuilder":
        self._include_totals = True
        return self

    def with_charts(self) -> "ReportBuilder":
        self._include_charts = True
        return self

    def header(self, text: str) -> "ReportBuilder":
        self._header_text = text
        return self

    def footer(self, text: str) -> "ReportBuilder":
        self._footer_text = text
        return self

    def build(self) -> Report:
        """Validate and create the immutable Report."""
        if not self._columns:
            raise ValueError("At least one column is required")

        return Report(
            title=self._title,
            description=self._description,
            format=self._format,
            start_date=self._start_date,
            end_date=self._end_date,
            columns=list(self._columns),
            filters=dict(self._filters),
            sort_by=self._sort_by,
            sort_order=self._sort_order,
            page_size=self._page_size,
            include_totals=self._include_totals,
            include_charts=self._include_charts,
            header_text=self._header_text,
            footer_text=self._footer_text,
        )
```

**Usage and output:**

```python
# Simple report
simple_report = (
    ReportBuilder("Monthly Sales")
    .description("Sales summary for March 2024")
    .columns("product", "quantity", "revenue")
    .date_range(date(2024, 3, 1), date(2024, 3, 31))
    .build()
)

print(simple_report)
print()

# Complex report
detailed_report = (
    ReportBuilder("Customer Analytics")
    .description("Detailed customer behavior analysis")
    .format(ReportFormat.EXCEL)
    .date_range(date(2024, 1, 1), date(2024, 3, 31))
    .columns("customer_name", "total_orders",
             "total_spent", "avg_order_value",
             "last_order_date")
    .filter("region", "North America")
    .filter("min_orders", 5)
    .filter("status", "active")
    .sort_by("total_spent", "DESC")
    .page_size(100)
    .with_totals()
    .with_charts()
    .header("CONFIDENTIAL - Internal Use Only")
    .footer("Generated by Analytics Engine v2.1")
    .build()
)

print(detailed_report)
```

```
Output:
=== Report: Monthly Sales ===
Description: Sales summary for March 2024
Format: PDF
Date Range: 2024-03-01 to 2024-03-31
Columns: product, quantity, revenue
Filters: {}
Sort: none
Page Size: 50
Totals: No
Charts: No

=== Report: Customer Analytics ===
Description: Detailed customer behavior analysis
Format: EXCEL
Date Range: 2024-01-01 to 2024-03-31
Columns: customer_name, total_orders, total_spent, avg_order_value, last_order_date
Filters: {'region': 'North America', 'min_orders': 5, 'status': 'active'}
Sort: total_spent DESC
Page Size: 100
Totals: Yes
Charts: Yes
Header: CONFIDENTIAL - Internal Use Only
Footer: Generated by Analytics Engine v2.1
```

---

## The Fluent Interface

The fluent interface is what makes builders readable. Each method returns `this` (or `self`), enabling method chaining.

```
WITHOUT fluent interface:

  Builder builder = new Builder("Report");
  builder.setTitle("Sales");
  builder.setFormat("PDF");
  builder.addColumn("name");
  builder.addColumn("revenue");
  builder.setLimit(100);
  Report report = builder.build();

  Seven statements. Repetitive "builder." prefix.

WITH fluent interface:

  Report report = new Builder("Sales")
      .format("PDF")
      .columns("name", "revenue")
      .limit(100)
      .build();

  One statement. Reads like English.
```

The key is that every method (except `build()`) returns the builder itself:

```java
public Builder method(String method) {
    this.method = method;
    return this;    // <-- THIS is what enables chaining
}
```

```python
def method(self, method: str) -> "Builder":
    self._method = method
    return self     # <-- THIS is what enables chaining
```

---

## The Director Pattern

The Director is an optional part of the Builder pattern. It encapsulates a specific construction sequence, so you can reuse it.

```
+---------------------------------------------------------------+
|                THE DIRECTOR                                   |
+---------------------------------------------------------------+
|                                                               |
|  Without Director:                                            |
|    Each client must know the exact build steps.               |
|    Duplicated construction code everywhere.                   |
|                                                               |
|  With Director:                                               |
|    Common construction sequences are encapsulated.            |
|    Client says "build me a standard GET request"              |
|    and the Director handles the details.                      |
|                                                               |
+---------------------------------------------------------------+

  +------------------+      +-------------------+
  |    Director      |----->|    Builder         |
  +------------------+      +-------------------+
  | + buildGetReq()  |      | + method()        |
  | + buildPostReq() |      | + header()        |
  | + buildAuthReq() |      | + timeout()       |
  +------------------+      | + build()         |
                            +-------------------+
```

**Java Director:**

```java
public class HttpRequestDirector {

    /**
     * Build a standard API GET request with common defaults.
     */
    public HttpRequest buildStandardGet(String url, String authToken) {
        return new HttpRequest.Builder(url)
            .method("GET")
            .authToken(authToken)
            .contentType("application/json")
            .header("Accept", "application/json")
            .timeoutMs(10000)
            .maxRetries(2)
            .build();
    }

    /**
     * Build a standard JSON POST request.
     */
    public HttpRequest buildJsonPost(String url, String body,
                                     String authToken) {
        return new HttpRequest.Builder(url)
            .method("POST")
            .body(body)
            .authToken(authToken)
            .contentType("application/json")
            .header("Accept", "application/json")
            .timeoutMs(15000)
            .maxRetries(1)
            .build();
    }

    /**
     * Build a file upload request with longer timeout.
     */
    public HttpRequest buildFileUpload(String url, String filePath,
                                       String authToken) {
        return new HttpRequest.Builder(url)
            .method("POST")
            .body("file://" + filePath)
            .authToken(authToken)
            .contentType("multipart/form-data")
            .timeoutMs(60000)    // 60 seconds for uploads
            .maxRetries(3)       // retry on failure
            .build();
    }
}
```

**Usage:**

```java
HttpRequestDirector director = new HttpRequestDirector();

// One line to create a standard GET request
HttpRequest getUsers = director.buildStandardGet(
    "https://api.example.com/users",
    "Bearer token123"
);

// One line to create a JSON POST
HttpRequest createUser = director.buildJsonPost(
    "https://api.example.com/users",
    "{\"name\": \"Jane\"}",
    "Bearer token123"
);
```

**Python Director:**

```python
class ReportDirector:
    """Encapsulates common report construction sequences."""

    @staticmethod
    def build_sales_summary(start: date, end: date) -> Report:
        return (
            ReportBuilder("Sales Summary")
            .description(f"Sales from {start} to {end}")
            .format(ReportFormat.PDF)
            .date_range(start, end)
            .columns("product", "units_sold", "revenue",
                     "profit_margin")
            .sort_by("revenue", "DESC")
            .with_totals()
            .with_charts()
            .footer("Auto-generated report")
            .build()
        )

    @staticmethod
    def build_user_export() -> Report:
        return (
            ReportBuilder("User Export")
            .description("Full user data export")
            .format(ReportFormat.CSV)
            .columns("id", "name", "email", "created_at",
                     "last_login")
            .sort_by("created_at", "DESC")
            .page_size(10000)
            .build()
        )

# Usage
sales = ReportDirector.build_sales_summary(
    date(2024, 1, 1), date(2024, 3, 31)
)
users = ReportDirector.build_user_export()
```

---

## Lombok @Builder

In Java, the Lombok library generates builder code automatically with a single annotation.

```java
import lombok.Builder;
import lombok.Getter;
import lombok.ToString;

@Getter
@Builder
@ToString
public class HttpRequest {

    private final String url;

    @Builder.Default
    private final String method = "GET";

    @Builder.Default
    private final int timeoutMs = 30000;

    @Builder.Default
    private final int maxRetries = 0;

    @Builder.Default
    private final boolean followRedirects = true;

    @Builder.Default
    private final String contentType = "application/json";

    @Builder.Default
    private final boolean verifySsl = true;

    private final String body;
    private final String authToken;

    @Singular
    private final Map<String, String> headers;
}
```

**What Lombok generates for you:**

```
+----------------------------------------------------------+
|  WHAT @Builder GENERATES                                 |
+----------------------------------------------------------+
|                                                          |
|  - A static Builder inner class                          |
|  - A builder() static method to get a new Builder        |
|  - Setter methods on the Builder for each field          |
|  - A build() method that creates the object              |
|  - @Builder.Default sets default values                  |
|  - @Singular generates add-one-at-a-time methods for     |
|    collections (header() instead of headers())           |
|                                                          |
+----------------------------------------------------------+
```

**Usage with Lombok:**

```java
HttpRequest request = HttpRequest.builder()
    .url("https://api.example.com/users")
    .method("POST")
    .body("{\"name\": \"John\"}")
    .authToken("Bearer abc123")
    .header("X-Request-ID", "req-001")
    .header("X-Client", "backend-v2")
    .timeoutMs(5000)
    .maxRetries(3)
    .build();
```

This is identical to hand-written builder code but with zero boilerplate. Lombok generates hundreds of lines of builder code from a single `@Builder` annotation.

---

## Real-World Backend Use Case: API Response Builder

```java
public class ApiResponse<T> {

    private final int statusCode;
    private final String message;
    private final T data;
    private final Map<String, String> metadata;
    private final List<String> errors;
    private final long timestamp;

    private ApiResponse(Builder<T> builder) {
        this.statusCode = builder.statusCode;
        this.message = builder.message;
        this.data = builder.data;
        this.metadata = Collections.unmodifiableMap(builder.metadata);
        this.errors = Collections.unmodifiableList(builder.errors);
        this.timestamp = builder.timestamp;
    }

    // ... getters ...

    public static class Builder<T> {
        private int statusCode = 200;
        private String message = "OK";
        private T data;
        private Map<String, String> metadata = new HashMap<>();
        private List<String> errors = new ArrayList<>();
        private long timestamp = System.currentTimeMillis();

        public Builder<T> status(int code) {
            this.statusCode = code;
            return this;
        }

        public Builder<T> message(String message) {
            this.message = message;
            return this;
        }

        public Builder<T> data(T data) {
            this.data = data;
            return this;
        }

        public Builder<T> meta(String key, String value) {
            this.metadata.put(key, value);
            return this;
        }

        public Builder<T> error(String error) {
            this.errors.add(error);
            return this;
        }

        public ApiResponse<T> build() {
            return new ApiResponse<>(this);
        }

        // Convenience factory methods
        public static <T> ApiResponse<T> success(T data) {
            return new Builder<T>()
                .status(200)
                .message("OK")
                .data(data)
                .build();
        }

        public static <T> ApiResponse<T> notFound(String msg) {
            return new Builder<T>()
                .status(404)
                .message(msg)
                .build();
        }

        public static <T> ApiResponse<T> serverError(
                String... errors) {
            Builder<T> builder = new Builder<T>()
                .status(500)
                .message("Internal Server Error");
            for (String e : errors) {
                builder.error(e);
            }
            return builder.build();
        }
    }
}
```

**Usage:**

```java
// Success response
ApiResponse<User> response = new ApiResponse.Builder<User>()
    .status(200)
    .message("User found")
    .data(user)
    .meta("cache", "HIT")
    .meta("responseTime", "45ms")
    .build();

// Or use the convenience methods
ApiResponse<User> success = ApiResponse.Builder.success(user);
ApiResponse<User> notFound = ApiResponse.Builder.notFound(
    "User not found"
);
ApiResponse<User> error = ApiResponse.Builder.serverError(
    "Database connection failed",
    "Retry limit exceeded"
);
```

---

## When to Use / When NOT to Use

```
+----------------------------------+----------------------------------+
|  USE BUILDER WHEN                |  DO NOT USE WHEN                 |
+----------------------------------+----------------------------------+
|                                  |                                  |
| - Object has many parameters     | - Object has 3 or fewer          |
|   (more than 4-5)               |   parameters                     |
|                                  |                                  |
| - Many parameters are optional   | - All parameters are required    |
|   with sensible defaults         |   (no optional ones)             |
|                                  |                                  |
| - You want immutable objects     | - Mutability is acceptable       |
|   (no setters after construction)|   (just use setters)             |
|                                  |                                  |
| - Construction involves          | - Construction is straightforward|
|   validation or complex logic    |   (just assign fields)           |
|                                  |                                  |
| - You need a fluent API          | - A simple constructor is        |
|   (query builders, config)       |   readable enough                |
|                                  |                                  |
+----------------------------------+----------------------------------+
```

---

## Common Mistakes

1. **Using Builder for simple objects.** If your class has two or three fields, a constructor is simpler. Builder adds complexity; do not use it where a constructor is clear enough.

```java
// OVER-ENGINEERED: Builder for a simple class
Point p = new Point.Builder().x(10).y(20).build();

// JUST USE A CONSTRUCTOR:
Point p = new Point(10, 20);
```

2. **Forgetting to validate in `build()`.** The whole point of Builder is controlled construction. If `build()` does not validate, you lose the safety guarantees.

3. **Mutable builder reuse.** Do not reuse a builder instance after calling `build()`. The builder's internal state may leak into the next object.

4. **Not making the product immutable.** If the product has setters, the builder provides no advantage over setters. The power of Builder is creating immutable objects.

5. **Too many required parameters in the builder constructor.** If the Builder constructor takes 5 required parameters, you have the same problem. Keep the builder constructor to 1-2 required fields.

---

## Best Practices

1. **Required parameters go in the Builder constructor.** Optional parameters have setter methods with defaults.

2. **Validate in `build()`, not in individual setters.** Some validations depend on the combination of fields (e.g., POST requires a body). These can only be checked when all fields are set.

3. **Return immutable objects from `build()`.** Use `final` fields, unmodifiable collections, and no setters.

4. **Consider a Director for common configurations.** If the same builder sequence appears in multiple places, extract it into a Director.

5. **In Java, use Lombok `@Builder` for simple cases.** Write a custom builder only when you need custom validation, computed fields, or complex logic.

6. **In Python, consider `dataclasses` with a builder.** Python's `@dataclass(frozen=True)` gives you immutability. Add a builder class when you have many optional parameters.

---

## Quick Summary

| Aspect | Details |
|--------|---------|
| Pattern name | Builder |
| Category | Creational |
| Intent | Construct complex objects step by step |
| Problem it solves | Telescoping constructors, unreadable parameter lists |
| Key feature | Fluent interface with method chaining |
| Director | Optional class that encapsulates common build sequences |
| Lombok | `@Builder` generates builder code automatically in Java |
| Result | Immutable, validated objects with readable construction code |

---

## Key Points

1. Builder solves the telescoping constructor problem by replacing a long parameter list with named, chainable method calls.

2. The fluent interface (each method returns `this`) makes construction code read almost like natural language.

3. Builder produces immutable objects. The product's constructor is private; only the builder can create instances.

4. Validation happens in `build()`, not in individual setters. This allows cross-field validation.

5. The Director pattern encapsulates common build sequences. Use it when the same configuration appears in multiple places.

6. In Java, Lombok's `@Builder` eliminates boilerplate. Use it for straightforward cases; write custom builders for complex validation.

7. Do not use Builder for simple objects. If a class has fewer than 4 parameters and no optional ones, a regular constructor is clearer.

---

## Practice Questions

1. What is the "telescoping constructor" problem? Give an example of how it makes code harder to read and maintain.

2. How does the fluent interface work in the Builder pattern? What does each setter method return, and why?

3. Why should the product object be immutable? What problems can occur if the product has setters?

4. When would you use a Director class? Give a real-world backend example where a Director would be beneficial.

5. Compare hand-written builders with Lombok's `@Builder`. When would you choose one over the other?

---

## Exercises

### Exercise 1: Email Message Builder

Create a Builder for an `EmailMessage` class with the following fields: `to` (required), `from` (required), `subject`, `bodyText`, `bodyHtml`, `cc` (list), `bcc` (list), `attachments` (list), `priority` (LOW/NORMAL/HIGH), `replyTo`. Include validation in `build()`: subject and at least one body (text or HTML) are required. Implement in both Java and Python.

### Exercise 2: Database Connection Config Builder

Create a `DatabaseConfig` builder with: `host` (required), `port` (default 5432), `database` (required), `username`, `password`, `maxPoolSize` (default 10), `minPoolSize` (default 2), `connectionTimeoutMs` (default 5000), `idleTimeoutMs` (default 600000), `sslEnabled` (default false), `sslCertPath`. Validation: if SSL is enabled, `sslCertPath` is required. `maxPoolSize` must be >= `minPoolSize`.

### Exercise 3: Query Builder with Director

Extend the SQL `QueryBuilder` example to support INSERT, UPDATE, and DELETE operations. Then create a `QueryDirector` with methods like `buildPaginatedList(table, page, pageSize)`, `buildCountQuery(table, conditions)`, and `buildSoftDelete(table, id)`.

---

## What Is Next?

In the next and final chapter of Part I, we explore the Prototype pattern. While Builder constructs objects step by step, Prototype creates objects by cloning existing ones. You will learn when cloning is faster and more practical than building from scratch, the critical difference between shallow and deep copies, and how prototype registries let you manage template objects for test data, configuration templates, and cached prototypes.
