# Chapter 12: Composite Pattern -- Tree Structures with a Uniform Interface

## What You Will Learn

- What the Composite pattern is and when to use it
- How to model tree structures where leaves and branches share the same interface
- The file system analogy that makes Composite click
- How to implement Composite in Java with menus and submenus
- How to implement Composite in Python with departments and employees
- The difference between Leaf and Composite nodes
- How to traverse, search, and aggregate across tree structures

## Why This Chapter Matters

Backend systems are full of hierarchical data: organization charts, menu systems, file
directories, permission trees, category taxonomies, and UI component trees. Without a
clean pattern, you end up writing different code for "things that contain other things"
versus "things that do not." That means if-else chains everywhere, constantly checking
types before performing operations.

The Composite pattern eliminates this problem. It lets you treat individual objects and
groups of objects through the same interface. Whether you are calculating the total cost
of a single item or an entire shopping cart with nested bundles, the code looks the same.

---

## The Problem

You are building an admin dashboard with a nested menu system. Some items are simple
links (like "Dashboard" or "Settings"). Others are submenus that contain more items,
and those items might contain even more submenus.

**Without Composite**, your rendering code looks like this:

```java
for (Object item : menuItems) {
    if (item instanceof MenuItem) {
        render((MenuItem) item);
    } else if (item instanceof SubMenu) {
        SubMenu sub = (SubMenu) item;
        renderSubMenuHeader(sub);
        for (Object child : sub.getChildren()) {
            if (child instanceof MenuItem) {
                render((MenuItem) child);
            } else if (child instanceof SubMenu) {
                // nested again... how deep does this go?
                SubMenu sub2 = (SubMenu) child;
                renderSubMenuHeader(sub2);
                // ... more nesting ...
            }
        }
    }
}
```

This code is fragile. Every new level of nesting requires more if-else blocks. Adding a
new type of menu element means changing every place that handles menus.

---

## The Solution: Composite Pattern

The Composite pattern defines a common interface for both individual items (leaves) and
containers (composites). The container holds children that share the same interface, and
operations cascade down the tree automatically.

```
+------------------------+
|    <<interface>>       |
|    MenuComponent       |
+------------------------+
| + render(indent)       |
| + getTitle(): String   |
| + search(query): List  |
+------------------------+
        ^           ^
        |           |
+-------------+  +----------------+
|  MenuItem   |  |    SubMenu     |
|   (Leaf)    |  |  (Composite)   |
+-------------+  +----------------+
| - title     |  | - title        |
| - url       |  | - children[]   |
+-------------+  +----------------+
| + render()  |  | + render()     |
| + search()  |  | + add(comp)    |
+-------------+  | + remove(comp) |
                 | + search()     |
                 +----------------+
                       |
                 children can be
                 MenuItem OR SubMenu
```

**Key insight:** SubMenu's `children` list holds `MenuComponent` objects. Each child
could be a simple MenuItem or another SubMenu. The SubMenu does not need to know which
type it contains. It just calls `render()` on each child and lets polymorphism handle
the rest.

---

## The File System Analogy

The most intuitive example of Composite is a file system.

```
root/
+-- documents/
|   +-- resume.pdf        (Leaf)
|   +-- cover-letter.docx (Leaf)
|   +-- projects/          (Composite)
|       +-- project-a.md   (Leaf)
|       +-- project-b.md   (Leaf)
+-- photos/
|   +-- vacation.jpg       (Leaf)
+-- notes.txt              (Leaf)
```

When you ask for the total size of `root/`, it adds up:
- Size of `documents/` (which adds up its children, including `projects/`)
- Size of `photos/`
- Size of `notes.txt`

The operation is the same at every level: if you are a file, return your size. If you
are a directory, sum the sizes of your children. That is Composite in action.

---

## Java Implementation: Menu System

### The Component Interface

```java
import java.util.List;

public interface MenuComponent {
    String getTitle();
    void render(int indent);
    List<MenuComponent> search(String query);
    int countItems();
}
```

### The Leaf: MenuItem

```java
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class MenuItem implements MenuComponent {
    private final String title;
    private final String url;
    private final String icon;

    public MenuItem(String title, String url, String icon) {
        this.title = title;
        this.url = url;
        this.icon = icon;
    }

    @Override
    public String getTitle() {
        return title;
    }

    @Override
    public void render(int indent) {
        String padding = " ".repeat(indent);
        System.out.printf("%s[%s] %s -> %s%n", padding, icon, title, url);
    }

    @Override
    public List<MenuComponent> search(String query) {
        if (title.toLowerCase().contains(query.toLowerCase())) {
            return List.of(this);
        }
        return Collections.emptyList();
    }

    @Override
    public int countItems() {
        return 1;
    }

    @Override
    public String toString() {
        return title;
    }
}
```

### The Composite: SubMenu

```java
import java.util.ArrayList;
import java.util.List;

public class SubMenu implements MenuComponent {
    private final String title;
    private final String icon;
    private final List<MenuComponent> children;

    public SubMenu(String title, String icon) {
        this.title = title;
        this.icon = icon;
        this.children = new ArrayList<>();
    }

    public void add(MenuComponent component) {
        children.add(component);
    }

    public void remove(MenuComponent component) {
        children.remove(component);
    }

    @Override
    public String getTitle() {
        return title;
    }

    @Override
    public void render(int indent) {
        String padding = " ".repeat(indent);
        System.out.printf("%s[%s] %s%n", padding, icon, title);
        for (MenuComponent child : children) {
            child.render(indent + 4);
        }
    }

    @Override
    public List<MenuComponent> search(String query) {
        List<MenuComponent> results = new ArrayList<>();

        // Check if this submenu matches
        if (title.toLowerCase().contains(query.toLowerCase())) {
            results.add(this);
        }

        // Search children recursively
        for (MenuComponent child : children) {
            results.addAll(child.search(query));
        }

        return results;
    }

    @Override
    public int countItems() {
        int count = 0;
        for (MenuComponent child : children) {
            count += child.countItems();
        }
        return count;
    }

    @Override
    public String toString() {
        return title + " (" + children.size() + " children)";
    }
}
```

### Building and Using the Menu

```java
public class MenuDemo {
    public static void main(String[] args) {
        // Build the menu tree
        SubMenu root = new SubMenu("Main Menu", "#");

        // Top-level items
        root.add(new MenuItem("Dashboard", "/dashboard", "D"));
        root.add(new MenuItem("Profile", "/profile", "P"));

        // Products submenu
        SubMenu products = new SubMenu("Products", ">");
        products.add(new MenuItem("All Products", "/products", "-"));
        products.add(new MenuItem("Add Product", "/products/new", "+"));

        // Nested: Product Categories
        SubMenu categories = new SubMenu("Categories", ">");
        categories.add(new MenuItem("Electronics", "/categories/electronics", "-"));
        categories.add(new MenuItem("Books", "/categories/books", "-"));
        categories.add(new MenuItem("Clothing", "/categories/clothing", "-"));
        products.add(categories);

        root.add(products);

        // Settings submenu
        SubMenu settings = new SubMenu("Settings", ">");
        settings.add(new MenuItem("General", "/settings/general", "-"));
        settings.add(new MenuItem("Security", "/settings/security", "-"));
        settings.add(new MenuItem("Notifications", "/settings/notif", "-"));
        root.add(settings);

        // Render entire menu tree
        System.out.println("=== Full Menu ===");
        root.render(0);

        // Count all items
        System.out.println("\nTotal menu items: " + root.countItems());

        // Search
        System.out.println("\n=== Search: 'product' ===");
        List<MenuComponent> results = root.search("product");
        for (MenuComponent result : results) {
            System.out.println("  Found: " + result);
        }
    }
}
```

**Output:**
```
=== Full Menu ===
[#] Main Menu
    [D] Dashboard -> /dashboard
    [P] Profile -> /profile
    [>] Products
        [-] All Products -> /products
        [+] Add Product -> /products/new
        [>] Categories
            [-] Electronics -> /categories/electronics
            [-] Books -> /categories/books
            [-] Clothing -> /categories/clothing
    [>] Settings
        [-] General -> /settings/general
        [-] Security -> /settings/security
        [-] Notifications -> /settings/notif

Total menu items: 10

=== Search: 'product' ===
  Found: Products (3 children)
  Found: All Products
  Found: Add Product
```

Notice how `render()`, `search()`, and `countItems()` work identically whether called
on a leaf or a composite. The client code does not need to know the difference.

---

## Python Implementation: Organization Tree

### Department and Employee Hierarchy

```python
from abc import ABC, abstractmethod


class OrganizationComponent(ABC):
    """Common interface for both employees and departments."""

    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def get_salary_cost(self):
        pass

    @abstractmethod
    def display(self, indent=0):
        pass

    @abstractmethod
    def count_employees(self):
        pass

    @abstractmethod
    def search(self, query):
        pass


class Employee(OrganizationComponent):
    """Leaf node: an individual employee."""

    def __init__(self, name, role, salary):
        self.name = name
        self.role = role
        self.salary = salary

    def get_name(self):
        return self.name

    def get_salary_cost(self):
        return self.salary

    def display(self, indent=0):
        padding = "  " * indent
        print(f"{padding}- {self.name} ({self.role}) ${self.salary:,.0f}")

    def count_employees(self):
        return 1

    def search(self, query):
        query_lower = query.lower()
        if (query_lower in self.name.lower() or
                query_lower in self.role.lower()):
            return [self]
        return []

    def __repr__(self):
        return f"Employee({self.name})"


class Department(OrganizationComponent):
    """Composite node: a department containing employees or sub-departments."""

    def __init__(self, name):
        self.name = name
        self._children = []

    def add(self, component):
        self._children.append(component)
        return self  # enable chaining

    def remove(self, component):
        self._children.remove(component)

    def get_name(self):
        return self.name

    def get_salary_cost(self):
        return sum(child.get_salary_cost() for child in self._children)

    def display(self, indent=0):
        padding = "  " * indent
        cost = self.get_salary_cost()
        count = self.count_employees()
        print(f"{padding}[{self.name}] ({count} employees, "
              f"${cost:,.0f} total)")
        for child in self._children:
            child.display(indent + 1)

    def count_employees(self):
        return sum(child.count_employees() for child in self._children)

    def search(self, query):
        results = []
        if query.lower() in self.name.lower():
            results.append(self)
        for child in self._children:
            results.extend(child.search(query))
        return results

    def __repr__(self):
        return f"Department({self.name}, {len(self._children)} members)"
```

### Building the Organization

```python
# Build organization tree
company = Department("Acme Corp")

# Engineering department with sub-departments
engineering = Department("Engineering")

backend = Department("Backend Team")
backend.add(Employee("Alice", "Senior Engineer", 150000))
backend.add(Employee("Bob", "Engineer", 120000))
backend.add(Employee("Charlie", "Junior Engineer", 90000))

frontend = Department("Frontend Team")
frontend.add(Employee("Diana", "Senior Engineer", 145000))
frontend.add(Employee("Eve", "Engineer", 115000))

engineering.add(backend)
engineering.add(frontend)
engineering.add(Employee("Frank", "Engineering Manager", 180000))

# Sales department
sales = Department("Sales")
sales.add(Employee("Grace", "Sales Director", 160000))
sales.add(Employee("Hank", "Account Executive", 110000))
sales.add(Employee("Ivy", "Account Executive", 105000))

company.add(engineering)
company.add(sales)
company.add(Employee("Jack", "CEO", 250000))

# Display the entire organization
print("=== Organization Chart ===")
company.display()

print(f"\nTotal employees: {company.count_employees()}")
print(f"Total salary cost: ${company.get_salary_cost():,.0f}")

# Display just engineering
print("\n=== Engineering Only ===")
engineering.display()
print(f"Engineering cost: ${engineering.get_salary_cost():,.0f}")

# Search
print("\n=== Search: 'engineer' ===")
results = company.search("engineer")
for r in results:
    print(f"  Found: {r}")
```

**Output:**
```
=== Organization Chart ===
[Acme Corp] (10 employees, $1,425,000 total)
  [Engineering] (6 employees, $800,000 total)
    [Backend Team] (3 employees, $360,000 total)
      - Alice (Senior Engineer) $150,000
      - Bob (Engineer) $120,000
      - Charlie (Junior Engineer) $90,000
    [Frontend Team] (2 employees, $260,000 total)
      - Diana (Senior Engineer) $145,000
      - Eve (Engineer) $115,000
    - Frank (Engineering Manager) $180,000
  [Sales] (3 employees, $375,000 total)
    - Grace (Sales Director) $160,000
    - Hank (Account Executive) $110,000
    - Ivy (Account Executive) $105,000
  - Jack (CEO) $250,000

Total employees: 10
Total salary cost: $1,425,000

=== Engineering Only ===
[Engineering] (6 employees, $800,000 total)
  [Backend Team] (3 employees, $360,000 total)
    - Alice (Senior Engineer) $150,000
    - Bob (Engineer) $120,000
    - Charlie (Junior Engineer) $90,000
  [Frontend Team] (2 employees, $260,000 total)
    - Diana (Senior Engineer) $145,000
    - Eve (Engineer) $115,000
  - Frank (Engineering Manager) $180,000
Engineering cost: $800,000
```

The same `display()`, `get_salary_cost()`, and `count_employees()` methods work at any
level of the tree. The company, a department, and an individual employee all respond to
the same interface.

---

## Real-World Use Case: Permission System

```python
class Permission(ABC):
    @abstractmethod
    def has_access(self, resource):
        pass

    @abstractmethod
    def describe(self, indent=0):
        pass


class SinglePermission(Permission):
    """Leaf: access to one specific resource."""

    def __init__(self, resource, level="read"):
        self.resource = resource
        self.level = level

    def has_access(self, resource):
        return self.resource == resource

    def describe(self, indent=0):
        padding = "  " * indent
        print(f"{padding}[{self.level.upper()}] {self.resource}")


class PermissionGroup(Permission):
    """Composite: a named group of permissions."""

    def __init__(self, name):
        self.name = name
        self._permissions = []

    def add(self, permission):
        self._permissions.append(permission)

    def has_access(self, resource):
        return any(p.has_access(resource) for p in self._permissions)

    def describe(self, indent=0):
        padding = "  " * indent
        print(f"{padding}Group: {self.name}")
        for p in self._permissions:
            p.describe(indent + 1)


# Build permission tree
admin_perms = PermissionGroup("Admin")
admin_perms.add(SinglePermission("users", "write"))
admin_perms.add(SinglePermission("settings", "write"))
admin_perms.add(SinglePermission("logs", "read"))

editor_perms = PermissionGroup("Editor")
editor_perms.add(SinglePermission("articles", "write"))
editor_perms.add(SinglePermission("media", "write"))

super_editor = PermissionGroup("Super Editor")
super_editor.add(editor_perms)       # include all editor perms
super_editor.add(SinglePermission("comments", "write"))  # plus more

print("=== Super Editor Permissions ===")
super_editor.describe()
print(f"\nCan access 'articles'? {super_editor.has_access('articles')}")
print(f"Can access 'users'?    {super_editor.has_access('users')}")
```

**Output:**
```
=== Super Editor Permissions ===
Group: Super Editor
  Group: Editor
    [WRITE] articles
    [WRITE] media
  [WRITE] comments

Can access 'articles'? True
Can access 'users'?    False
```

---

## Before vs After Comparison

### Before: Without Composite

```python
def calculate_cost(item):
    if isinstance(item, Product):
        return item.price
    elif isinstance(item, Bundle):
        total = 0
        for sub_item in item.items:
            if isinstance(sub_item, Product):
                total += sub_item.price
            elif isinstance(sub_item, Bundle):
                # Recursion with type checking at every level
                for sub_sub in sub_item.items:
                    if isinstance(sub_sub, Product):
                        total += sub_sub.price
                    # How deep do we go?
        return total
```

### After: With Composite

```python
def calculate_cost(component):
    return component.get_cost()  # works for Product AND Bundle
```

Both `Product.get_cost()` and `Bundle.get_cost()` implement the same interface. The
Bundle version sums its children's costs. No type checking needed anywhere.

---

## Leaf vs Composite: Key Differences

```
+------------------+-----------------------------+-----------------------------+
| Aspect           | Leaf                        | Composite                   |
+------------------+-----------------------------+-----------------------------+
| Children         | None                        | Holds a list of components  |
| add/remove       | Not applicable              | Adds/removes children       |
| Operation        | Performs work directly       | Delegates to children       |
| Termination      | Base case of recursion      | Recursive case              |
| Example          | File, MenuItem, Employee    | Directory, SubMenu, Dept    |
+------------------+-----------------------------+-----------------------------+
```

**Design decision:** Should add/remove be in the base interface?

- **Transparency approach**: Put add/remove in the interface. Leaves throw
  UnsupportedOperationException. Client code is simpler but less safe.
- **Safety approach**: Only composites have add/remove. Client must cast to add
  children. Safer but requires type awareness.

Most modern implementations prefer the **safety approach**.

---

## When to Use / When NOT to Use

### Use Composite When

- You have tree or hierarchy structures (menus, org charts, file systems)
- You want clients to treat individual objects and groups uniformly
- Operations should cascade through the hierarchy (render, calculate, search)
- You need recursive data structures with varying depth
- New leaf or composite types should be addable without changing existing code

### Do NOT Use Composite When

- The data is flat, not hierarchical (use a simple list instead)
- Leaves and composites have very different operations (forced uniformity hurts)
- The hierarchy has a fixed, known depth (simpler approaches work fine)
- Performance is critical and the tree is very deep (recursion overhead adds up)
- You need strict type safety about what can contain what

---

## Common Mistakes

### Mistake 1: Allowing Cycles

```python
# WRONG: this creates an infinite loop
dept_a = Department("A")
dept_b = Department("B")
dept_a.add(dept_b)
dept_b.add(dept_a)  # cycle!

dept_a.display()  # infinite recursion -> stack overflow
```

**Fix:** Check for cycles when adding children.

```python
def add(self, component):
    if self._creates_cycle(component):
        raise ValueError("Adding this component would create a cycle")
    self._children.append(component)

def _creates_cycle(self, component):
    if component is self:
        return True
    if isinstance(component, Department):
        for child in component._children:
            if self._creates_cycle(child):
                return True
    return False
```

### Mistake 2: Inconsistent Interface

```java
// WRONG: treating leaves differently
if (component instanceof SubMenu) {
    ((SubMenu) component).add(newItem);
}
// This defeats the purpose of Composite!
```

### Mistake 3: No Base Case

```java
// WRONG: composite that never terminates
public int countItems() {
    int count = 1; // counts itself AND children
    for (MenuComponent child : children) {
        count += child.countItems();
    }
    return count; // should it count itself? Be consistent!
}
```

Be clear about whether composites count themselves or only their leaves.

---

## Best Practices

1. **Keep the component interface focused.** Only include operations that genuinely make
   sense for both leaves and composites.

2. **Use the safety approach for add/remove.** Putting child management only on the
   composite class prevents runtime errors from trying to add children to leaves.

3. **Prevent cycles.** Validate on add that you are not creating circular references
   that would cause infinite recursion.

4. **Consider caching.** If operations like `count()` or `totalCost()` are called
   frequently, cache the result and invalidate when children change.

5. **Use iterators for traversal.** Instead of exposing the internal children list,
   provide an iterator. This allows different traversal orders (depth-first,
   breadth-first) without changing the composite.

6. **Keep leaves simple.** Leaves should not have unused methods. If your interface has
   many methods that leaves need to stub out, your interface is too broad.

---

## Quick Summary

The Composite pattern models tree structures where individual objects (leaves) and
containers (composites) share the same interface. Operations cascade through the tree
via recursion. Clients interact with the tree uniformly without needing to know whether
they are dealing with a leaf or a composite.

```
Problem:  Client code must distinguish between single items and groups,
          leading to complex type-checking logic.
Solution: Define a common interface for both, with composites delegating
          operations to their children recursively.
Key:      Leaves do the work; composites delegate to children.
```

---

## Key Points

- **Composite** lets you treat individual objects and groups uniformly through a shared
  interface
- **Leaves** perform operations directly; **composites** delegate to their children
- The pattern naturally models tree/hierarchy structures like file systems, menus, and
  org charts
- Operations cascade through the tree via recursion: render, count, sum, search
- Prevent cycles when building the tree to avoid infinite recursion
- Choose between transparency (add/remove in base interface) and safety (add/remove
  only on composites)
- Composite works well with Iterator for traversal and Visitor for operations

---

## Practice Questions

1. In the file system analogy, what is the leaf and what is the composite? How does
   calculating total directory size demonstrate the pattern?

2. What is the difference between the transparency approach and the safety approach for
   handling add/remove operations? Which would you choose for a production system and
   why?

3. How would you modify the menu example to support a `getUrl()` method on MenuItems
   but not on SubMenus? Does this break the Composite pattern?

4. Explain how Composite and Iterator patterns can work together. What are the benefits?

5. A company has a product catalog where a "Bundle" contains products and other bundles.
   Describe how Composite would model this, including how to calculate the total price.

---

## Exercises

### Exercise 1: File System Implementation

Build a file system model with these requirements:

- `File` (leaf) with name, size in bytes, and extension
- `Directory` (composite) with name and children
- Operations: `get_total_size()`, `display(indent)`, `find_by_extension(ext)`
- Create a tree representing: `/home/user/` with `documents/`, `photos/`, nested
  subdirectories, and at least 8 files
- Demonstrate that `get_total_size()` on root equals the sum of all individual files

### Exercise 2: E-Commerce Category Tree

Create a product category system:

- `Product` (leaf) with name, price, and stock count
- `Category` (composite) with name and children (products or subcategories)
- Operations: `total_products()`, `total_value()` (price * stock for all products),
  `find_out_of_stock()`
- Build: Electronics > Phones > (iPhone, Samsung), Laptops > (MacBook, ThinkPad)
- Each product should have realistic prices and stock values

### Exercise 3: Expression Tree

Build a mathematical expression evaluator using Composite:

- `NumberNode` (leaf) holds a numeric value
- `OperationNode` (composite) holds an operator (+, -, *, /) and two children
- `evaluate()` method returns the computed result
- Build and evaluate: `(3 + 5) * (10 - 2)` which should equal 64
- Add a `to_string()` method that prints the expression with parentheses

---

## What Is Next?

The next chapter introduces the **Flyweight Pattern**, which takes the opposite approach
to Composite. Where Composite creates tree structures by combining objects, Flyweight
reduces memory usage by sharing common data across many objects. Together, they give you
tools for both structuring and optimizing your object hierarchies.
