# Chapter 2: Meaningful Names

---

## What You Will Learn

- How to choose names that reveal the intention behind your code
- Why misleading names are worse than unclear names
- The difference between meaningful distinctions and noise words
- Rules for naming classes, methods, variables, and constants
- How to avoid common naming traps that confuse other developers
- Over ten real before/after naming transformations

---

## Why This Chapter Matters

Naming is the most frequent activity in programming. You name variables, functions, classes, packages, files, directories, parameters, and constants. You do it so often that you might not think much about it. But names are the primary way code communicates with human readers.

A good name eliminates the need for a comment. A bad name creates confusion that comments cannot fully repair. Since you spend 10 times more time reading code than writing it (as we learned in Chapter 1), every good name you choose saves reading time for every developer who encounters it -- including your future self.

Naming is hard. It is acknowledged as one of the two hardest problems in computer science (along with cache invalidation and off-by-one errors). But it gets easier with practice and a set of clear rules. This chapter gives you those rules.

---

## Rule 1: Use Intention-Revealing Names

The name of a variable, function, or class should tell you three things:
1. **Why it exists**
2. **What it does**
3. **How it is used**

If a name requires a comment to explain it, the name is not good enough.

**BEFORE: Names that hide intention**

Java:
```java
int d; // elapsed time in days
```

Python:
```python
d = 0  # elapsed time in days
```

**AFTER: Names that reveal intention**

Java:
```java
int elapsedTimeInDays;
int daysSinceCreation;
int daysSinceModification;
int fileAgeInDays;
```

Python:
```python
elapsed_time_in_days = 0
days_since_creation = 0
days_since_modification = 0
file_age_in_days = 0
```

The comment is gone because the name carries all the information. Notice that each alternative name carries a slightly different meaning. The right choice depends on the specific context, and that precision is exactly the point.

### A Complete Example

Here is a larger example that shows how intention-revealing names transform unreadable code into clear code.

**BEFORE: What does this do?**

Java:
```java
public List<int[]> getThem() {
    List<int[]> list1 = new ArrayList<>();
    for (int[] x : theList) {
        if (x[0] == 4) {
            list1.add(x);
        }
    }
    return list1;
}
```

Python:
```python
def get_them(self):
    list1 = []
    for x in the_list:
        if x[0] == 4:
            list1.append(x)
    return list1
```

This code is simple -- just a filtered list. But you cannot tell what it does without knowing:
- What is `theList`?
- What is the significance of `x[0]`?
- What does `4` mean?
- What do you do with the returned list?

Now imagine this is a minesweeper game:

**AFTER: Intention revealed through names**

Java:
```java
public List<Cell> getFlaggedCells() {
    List<Cell> flaggedCells = new ArrayList<>();
    for (Cell cell : gameBoard) {
        if (cell.isFlagged()) {
            flaggedCells.add(cell);
        }
    }
    return flaggedCells;
}
```

Python:
```python
def get_flagged_cells(self) -> list[Cell]:
    flagged_cells = []
    for cell in self.game_board:
        if cell.is_flagged():
            flagged_cells.append(cell)
    return flagged_cells
```

The code has not become more complex. It has become clear. Every name tells you what it represents and why it matters.

---

## Rule 2: Avoid Disinformation

Do not use names that mean something different from what they actually represent. This is worse than unclear names because they actively mislead.

**BEFORE: Disinforming names**

Java:
```java
// BAD: It is not a List, it is a Map
Map<String, Account> accountList = new HashMap<>();

// BAD: hp could mean hit points, horsepower, or Hewlett-Packard
int hp = calculateValue();

// BAD: looks like the letter O or the number 0
int O = calculateWeight();
int l = 1;  // looks like the number 1
if (O == l) { ... }
```

Python:
```python
# BAD: It is not a list, it is a dictionary
account_list = {}

# BAD: hp is ambiguous
hp = calculate_value()

# BAD: O looks like 0, l looks like 1
O = calculate_weight()
l = 1
if O == l: ...
```

**AFTER: Honest names**

Java:
```java
Map<String, Account> accountsByName = new HashMap<>();
int horsePower = calculateHorsePower();
int outputWeight = calculateWeight();
int lineCount = 1;
```

Python:
```python
accounts_by_name = {}
horse_power = calculate_horse_power()
output_weight = calculate_weight()
line_count = 1
```

```
+-----------------------------------------------------------+
|              Common Disinformation Traps                  |
+-----------------------------------------------------------+
|                                                           |
|  accountList     -->  Use when it IS a List/list          |
|                       Otherwise: accounts, accountMap,    |
|                       accountsByName                      |
|                                                           |
|  userGroup       -->  Is it a UI group? Permission group? |
|                       Team? Be specific.                  |
|                                                           |
|  controller      -->  MVC controller? Game controller?    |
|                       Hardware controller? Name it fully. |
|                                                           |
|  XYZController       Avoid names that differ in only      |
|  XYZControllerFor    small ways -- they are easy to       |
|  XYZHandlerController  confuse at a glance.               |
|                                                           |
+-----------------------------------------------------------+
```

---

## Rule 3: Make Meaningful Distinctions

If names must be different, they must also mean something different. Do not add noise words just to satisfy the compiler.

**BEFORE: Noise word distinctions**

Java:
```java
// What is the difference between these?
public void copyChars(char[] a1, char[] a2) {
    for (int i = 0; i < a1.length; i++) {
        a2[i] = a1[i];
    }
}

// What is the difference between these classes?
class ProductInfo { }
class ProductData { }
class ProductDetails { }

// What is the difference between these methods?
String getName();
String getNameString();  // What else would it be? An integer?

// What is the difference between these variables?
String customerName;
String customerNameVariable;
```

Python:
```python
# What is the difference between a1 and a2?
def copy_chars(a1, a2):
    for i in range(len(a1)):
        a2[i] = a1[i]

# What is the difference?
class ProductInfo: ...
class ProductData: ...
class ProductDetails: ...
```

**AFTER: Meaningful distinctions**

Java:
```java
public void copyChars(char[] source, char[] destination) {
    for (int i = 0; i < source.length; i++) {
        destination[i] = source[i];
    }
}
```

Python:
```python
def copy_chars(source: list[str], destination: list[str]):
    for i in range(len(source)):
        destination[i] = source[i]
```

The rule is simple: if you cannot explain the difference between two names without looking at their implementations, at least one of the names is wrong.

```
Noise Words That Add No Meaning
=================================

  "Info"     -->  ProductInfo vs Product? No real difference.
  "Data"     -->  UserData vs User? No real difference.
  "Object"   -->  ConfigObject vs Config? No real difference.
  "Variable" -->  nameVariable vs name? Obvious padding.
  "String"   -->  nameString vs name? Type is already clear.
  "Manager"  -->  Sometimes useful, but often a sign that the
                  class does too many things.
```

---

## Rule 4: Use Pronounceable Names

If you cannot pronounce a name, you cannot discuss it without sounding foolish. This matters more than you might think, because programming is a social activity. You discuss code in reviews, pair programming, and meetings.

**BEFORE: Unpronounceable names**

Java:
```java
class DtaRcrd102 {
    private Date genymdhms;    // generation year month day hour minute second
    private Date modymdhms;    // modification timestamp
    private String pszqint;    // what?
}
```

Python:
```python
class DtaRcrd102:
    def __init__(self):
        self.genymdhms = None    # generation date
        self.modymdhms = None    # modification date
        self.pszqint = None      # ???
```

Try saying this in a code review: "Hey, look at the gen-why-em-dee-aitch-em-ess field on the dee-tee-ay-arr-see-arr-dee-one-oh-two class." Nobody wants to have that conversation.

**AFTER: Pronounceable names**

Java:
```java
class CustomerRecord {
    private Date generationTimestamp;
    private Date modificationTimestamp;
    private String recordId;
}
```

Python:
```python
class CustomerRecord:
    def __init__(self):
        self.generation_timestamp = None
        self.modification_timestamp = None
        self.record_id = None
```

Now you can say: "Hey, look at the generation timestamp on the customer record." Natural conversation.

---

## Rule 5: Use Searchable Names

Single-letter names and numeric constants are impossible to search for in a codebase.

**BEFORE: Unsearchable names**

Java:
```java
for (int j = 0; j < 34; j++) {
    s += (t[j] * 4) / 5;
}
```

Python:
```python
for j in range(34):
    s += (t[j] * 4) / 5
```

Try searching for `j` in a project. You will find thousands of matches. Try searching for `34`. What does it mean? Why is it 34?

**AFTER: Searchable names**

Java:
```java
int realDaysPerIdealDay = 4;
int WORK_DAYS_PER_WEEK = 5;
int NUMBER_OF_TASKS = 34;

for (int taskIndex = 0; taskIndex < NUMBER_OF_TASKS; taskIndex++) {
    int realTaskDays = taskEstimate[taskIndex] * realDaysPerIdealDay;
    int realTaskWeeks = realTaskDays / WORK_DAYS_PER_WEEK;
    totalWeeks += realTaskWeeks;
}
```

Python:
```python
REAL_DAYS_PER_IDEAL_DAY = 4
WORK_DAYS_PER_WEEK = 5
NUMBER_OF_TASKS = 34

for task_index in range(NUMBER_OF_TASKS):
    real_task_days = task_estimate[task_index] * REAL_DAYS_PER_IDEAL_DAY
    real_task_weeks = real_task_days // WORK_DAYS_PER_WEEK
    total_weeks += real_task_weeks
```

Now you can search for `WORK_DAYS_PER_WEEK` and find every place it is used. If the value changes, you change it in one place.

```
Searchability Rule of Thumb
============================

  Single-letter variables  -->  ONLY acceptable as loop
                                counters in very short loops
                                (i, j in a 3-line loop)

  Magic numbers (7, 86400) -->  ALWAYS use named constants
                                SECONDS_PER_DAY = 86400
                                MAX_RETRY_COUNT = 7

  Short abbreviations      -->  Use full words unless the
                                abbreviation is universally
                                understood (url, html, id)
```

---

## Rule 6: Class Names Should Be Nouns

Classes represent things, so they should be named with nouns or noun phrases. Avoid verbs in class names.

**BEFORE: Bad class names**

Java:
```java
class ProcessOrders { }      // Verb -- sounds like a function
class ManageData { }         // Verb -- sounds like a function
class Calculate { }          // Verb -- sounds like a function
class Info { }               // Too vague -- info about what?
class Processor { }          // Too vague -- processes what?
class Data { }               // Too vague -- what data?
```

**AFTER: Good class names**

Java:
```java
class Order { }              // Clear noun
class OrderProcessor { }     // Noun phrase (the thing that processes)
class Customer { }           // Clear noun
class ShippingCalculator { } // Noun phrase
class PaymentGateway { }     // Noun phrase
class InvoiceRepository { }  // Noun phrase
```

Python:
```python
class Order: ...
class OrderProcessor: ...
class Customer: ...
class ShippingCalculator: ...
class PaymentGateway: ...
class InvoiceRepository: ...
```

---

## Rule 7: Method Names Should Be Verbs

Methods represent actions, so they should be named with verbs or verb phrases.

**BEFORE: Bad method names**

Java:
```java
public double calculation();       // Noun -- what calculation?
public void data();                // Noun -- what about data?
public boolean valid();            // Adjective -- validate? is valid?
public User user(int id);          // Noun -- get user? create user?
```

**AFTER: Good method names**

Java:
```java
public double calculateTotal();
public void saveData();
public boolean isValid();
public User findUserById(int id);
```

Python:
```python
def calculate_total(self) -> float: ...
def save_data(self): ...
def is_valid(self) -> bool: ...
def find_user_by_id(self, user_id: int) -> User: ...
```

```
Method Naming Conventions
==========================

  Getters:     getName()  / get_name()
  Setters:     setName()  / set_name()
  Booleans:    isActive() / is_active()
               hasPermission() / has_permission()
               canExecute() / can_execute()
  Actions:     save(), delete(), send(), calculate()
  Conversions: toString() / to_string()
               toJson() / to_json()
  Factories:   createOrder() / create_order()
               fromJson() / from_json()
```

---

## Rule 8: Do Not Be Cute

Resist the temptation to use clever, funny, or culturally specific names. Not everyone shares your sense of humor, and jokes get stale fast.

**BEFORE: "Clever" names**

Java:
```java
public void whack() { }          // means delete
public void eatMyShorts() { }    // means abort
public void nuke(List items) { } // means clear all
public int getCheeseburger() { } // means... what?
public void rockAndRoll() { }    // means start processing
```

**AFTER: Professional names**

Java:
```java
public void delete() { }
public void abort() { }
public void clearAll(List items) { }
public int getMenuItemCount() { }
public void startProcessing() { }
```

Python:
```python
def delete(self): ...
def abort(self): ...
def clear_all(self, items: list): ...
def get_menu_item_count(self) -> int: ...
def start_processing(self): ...
```

The rule: **say what you mean. Mean what you say.** Code is not the place for inside jokes.

---

## Rule 9: One Word Per Concept

Pick one word for one abstract concept and stick with it throughout the codebase. Do not use `fetch`, `retrieve`, and `get` to mean the same thing in different classes.

**BEFORE: Inconsistent terminology**

Java:
```java
class UserController {
    public User fetchUser(int id) { ... }
}

class OrderController {
    public Order retrieveOrder(int id) { ... }
}

class ProductController {
    public Product getProduct(int id) { ... }
}

class InvoiceController {
    public Invoice obtainInvoice(int id) { ... }
}
```

A developer looking at this codebase will wonder: Is there a difference between fetch, retrieve, get, and obtain? Do they have different semantics? Different error handling? The answer is usually no -- they all mean the same thing, and the inconsistency creates unnecessary confusion.

**AFTER: Consistent terminology**

Java:
```java
class UserController {
    public User getUser(int id) { ... }
}

class OrderController {
    public Order getOrder(int id) { ... }
}

class ProductController {
    public Product getProduct(int id) { ... }
}

class InvoiceController {
    public Invoice getInvoice(int id) { ... }
}
```

Python:
```python
class UserController:
    def get_user(self, user_id: int) -> User: ...

class OrderController:
    def get_order(self, order_id: int) -> Order: ...

class ProductController:
    def get_product(self, product_id: int) -> Product: ...

class InvoiceController:
    def get_invoice(self, invoice_id: int) -> Invoice: ...
```

```
Establish a Project Vocabulary
================================

  Pick ONE word for each concept:

  +-------------------+---------------------+
  | Concept           | Chosen Word         |
  +-------------------+---------------------+
  | Get single item   | get                 |
  | Get multiple items| list / findAll      |
  | Create new        | create              |
  | Modify existing   | update              |
  | Remove            | delete              |
  | Check existence   | exists              |
  | Validate          | validate            |
  | Convert           | toX / fromX         |
  +-------------------+---------------------+

  Document this in your team's style guide.
```

---

## Rule 10: Use Solution Domain Names When Appropriate

Your readers are programmers. Use computer science terms when they are the clearest option. Do not invent new names for well-known patterns.

Java:
```java
// GOOD: Programmers know what these terms mean
class AccountRepository { }     // Repository pattern
class OrderFactory { }          // Factory pattern
class EventQueue { }            // Queue data structure
class UserObserver { }          // Observer pattern
class JobScheduler { }          // Scheduler concept
class RequestVisitor { }        // Visitor pattern
```

Python:
```python
class AccountRepository: ...    # Repository pattern
class OrderFactory: ...         # Factory pattern
class EventQueue: ...           # Queue data structure
class UserObserver: ...         # Observer pattern
class JobScheduler: ...         # Scheduler concept
```

If there is no programmer term that fits, use a name from the business domain. If the users call it a "shopping cart," call it `ShoppingCart`, not `ItemAccumulator`.

---

## The Big Before/After: Ten Naming Fixes

Here is a comprehensive example showing ten bad naming choices fixed in a single class.

**BEFORE: A naming disaster**

Java:
```java
public class Mgr {                                    // 1. Abbreviated class name
    private List<String[]> lst;                        // 2. Cryptic variable name
    private int cnt;                                   // 3. Unnecessary abbreviation

    public void proc(String[] a) {                     // 4. Verb abbreviation, unclear param
        String n = a[0];                               // 5. Single letter variable
        String val = a[1];                             // 6. Abbreviated, ambiguous
        int flag = Integer.parseInt(a[2]);             // 7. "flag" means nothing

        if (flag == 1) {                               // 8. Magic number
            for (int j = 0; j < lst.size(); j++) {    // 9. Generic loop variable is OK here
                String[] tmp = lst.get(j);             // 10. "tmp" is lazy
                if (tmp[0].equals(n)) {
                    tmp[1] = val;
                    cnt++;
                    return;
                }
            }
        }
    }
}
```

Python:
```python
class Mgr:                                            # 1. Abbreviated class name
    def __init__(self):
        self.lst = []                                  # 2. Cryptic variable name
        self.cnt = 0                                   # 3. Unnecessary abbreviation

    def proc(self, a):                                 # 4. Verb abbreviation, unclear param
        n = a[0]                                       # 5. Single letter variable
        val = a[1]                                     # 6. Abbreviated, ambiguous
        flag = int(a[2])                               # 7. "flag" means nothing

        if flag == 1:                                  # 8. Magic number
            for j in range(len(self.lst)):             # 9. Generic loop variable
                tmp = self.lst[j]                      # 10. "tmp" is lazy
                if tmp[0] == n:
                    tmp[1] = val
                    self.cnt += 1
                    return
```

**AFTER: Every name tells a story**

Java:
```java
public class EmployeeManager {                                    // 1. Full descriptive name
    private List<Employee> employees;                             // 2. Clear collection name
    private int updateCount;                                      // 3. Full word, clear purpose

    private static final int UPDATE_OPERATION = 1;                // 8. Named constant

    public void processEmployeeUpdate(String[] rawRecord) {       // 4. Full verb phrase, clear param
        String employeeName = rawRecord[0];                       // 5. Descriptive variable
        String newDepartment = rawRecord[1];                      // 6. Specific and clear
        int operationType = Integer.parseInt(rawRecord[2]);       // 7. Meaningful name

        if (operationType == UPDATE_OPERATION) {                  // 8. Reads like English
            for (Employee employee : employees) {                 // 9+10. Proper type, clear name
                if (employee.getName().equals(employeeName)) {
                    employee.setDepartment(newDepartment);
                    updateCount++;
                    return;
                }
            }
        }
    }
}
```

Python:
```python
class EmployeeManager:                                            # 1. Full descriptive name
    UPDATE_OPERATION = 1                                          # 8. Named constant

    def __init__(self):
        self.employees: list[Employee] = []                       # 2. Clear collection name
        self.update_count: int = 0                                # 3. Full word, clear purpose

    def process_employee_update(self, raw_record: list[str]):     # 4. Full verb phrase
        employee_name = raw_record[0]                             # 5. Descriptive variable
        new_department = raw_record[1]                            # 6. Specific and clear
        operation_type = int(raw_record[2])                       # 7. Meaningful name

        if operation_type == self.UPDATE_OPERATION:                # 8. Reads like English
            for employee in self.employees:                       # 9+10. Clear loop variable
                if employee.name == employee_name:
                    employee.department = new_department
                    self.update_count += 1
                    return
```

Here is a summary of all ten fixes:

```
+----+------------------------+-------------------------+
| #  | Before                 | After                   |
+----+------------------------+-------------------------+
|  1 | Mgr                    | EmployeeManager         |
|  2 | lst                    | employees               |
|  3 | cnt                    | updateCount             |
|  4 | proc(String[] a)       | processEmployeeUpdate() |
|  5 | n                      | employeeName            |
|  6 | val                    | newDepartment           |
|  7 | flag                   | operationType           |
|  8 | 1 (magic number)       | UPDATE_OPERATION        |
|  9 | j (loop counter)       | (enhanced for loop)     |
| 10 | tmp                    | employee                |
+----+------------------------+-------------------------+
```

---

## Real-World Scenario: Naming in a REST API

Here is a realistic scenario showing how naming affects an entire layer of an application.

**BEFORE: An API controller with poor names**

Java:
```java
@RestController
public class UC {

    @Autowired
    private Svc s;

    @GetMapping("/u")
    public Resp g(@RequestParam int i) {
        Obj o = s.f(i);
        if (o == null) {
            return new Resp(404, "nf");
        }
        return new Resp(200, o.conv());
    }

    @PostMapping("/u")
    public Resp c(@RequestBody Map<String, Object> d) {
        int r = s.mk(d);
        return new Resp(201, String.valueOf(r));
    }

    @DeleteMapping("/u")
    public Resp d(@RequestParam int i) {
        boolean ok = s.rm(i);
        return ok ? new Resp(200, "ok") : new Resp(404, "nf");
    }
}
```

Python (Flask):
```python
class UC:
    def __init__(self, s):
        self.s = s

    def g(self, i):
        o = self.s.f(i)
        if o is None:
            return {"status": 404, "msg": "nf"}
        return {"status": 200, "data": o.conv()}

    def c(self, d):
        r = self.s.mk(d)
        return {"status": 201, "id": str(r)}

    def d(self, i):
        ok = self.s.rm(i)
        return {"status": 200} if ok else {"status": 404, "msg": "nf"}
```

**AFTER: Clear, professional API controller**

Java:
```java
@RestController
@RequestMapping("/users")
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping("/{userId}")
    public ResponseEntity<UserResponse> getUser(@PathVariable int userId) {
        User user = userService.findById(userId);
        if (user == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(user.toResponse());
    }

    @PostMapping
    public ResponseEntity<UserResponse> createUser(
            @RequestBody CreateUserRequest request) {
        User createdUser = userService.create(request);
        return ResponseEntity
            .status(HttpStatus.CREATED)
            .body(createdUser.toResponse());
    }

    @DeleteMapping("/{userId}")
    public ResponseEntity<Void> deleteUser(@PathVariable int userId) {
        boolean deleted = userService.deleteById(userId);
        if (!deleted) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok().build();
    }
}
```

Python (Flask):
```python
class UserController:

    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def get_user(self, user_id: int) -> dict:
        user = self.user_service.find_by_id(user_id)
        if user is None:
            return {"error": "User not found"}, 404
        return user.to_response(), 200

    def create_user(self, create_request: dict) -> dict:
        created_user = self.user_service.create(create_request)
        return created_user.to_response(), 201

    def delete_user(self, user_id: int) -> dict:
        deleted = self.user_service.delete_by_id(user_id)
        if not deleted:
            return {"error": "User not found"}, 404
        return {}, 200
```

The difference is dramatic. The clean version reads like documentation. Every name tells you exactly what is happening, what the inputs are, and what the outputs mean.

---

## Naming Conventions by Language

Java and Python have different naming conventions. Respecting these conventions makes your code feel natural to developers in each language.

```
+-------------------+-------------------+-------------------+
| Element           | Java Convention   | Python Convention  |
+-------------------+-------------------+-------------------+
| Class             | PascalCase        | PascalCase         |
|                   | OrderProcessor    | OrderProcessor     |
+-------------------+-------------------+-------------------+
| Method/Function   | camelCase         | snake_case         |
|                   | calculateTotal()  | calculate_total()  |
+-------------------+-------------------+-------------------+
| Variable          | camelCase         | snake_case         |
|                   | totalPrice        | total_price        |
+-------------------+-------------------+-------------------+
| Constant          | UPPER_SNAKE_CASE  | UPPER_SNAKE_CASE   |
|                   | MAX_RETRY_COUNT   | MAX_RETRY_COUNT    |
+-------------------+-------------------+-------------------+
| Package/Module    | lowercase         | lowercase          |
|                   | com.app.orders    | orders             |
+-------------------+-------------------+-------------------+
| Boolean variable  | isActive          | is_active          |
|                   | hasPermission     | has_permission     |
+-------------------+-------------------+-------------------+
| Private member    | this.field        | _field (prefix _)  |
|                   | (no prefix)       | self._field        |
+-------------------+-------------------+-------------------+
| Interface (Java)  | Readable          | N/A (use ABC or    |
|                   | Serializable      |  Protocol)         |
+-------------------+-------------------+-------------------+
```

---

## Common Mistakes

1. **Using abbreviations to save typing.** `usr` instead of `user`, `msg` instead of `message`, `btn` instead of `button`. Your IDE has autocomplete. Use full words.

2. **Encoding types in names.** `strName`, `intCount`, `lstItems`. Modern languages and IDEs show you the type. The name should describe the purpose, not the type (this is known as Hungarian notation, and it is outdated).

3. **Using `temp`, `tmp`, `data`, `info`, `stuff`, `thing`.** These names carry zero information. Every variable holds data. Every variable is temporary in some sense.

4. **Using different names for the same concept.** If you call it `customer` in one file and `client` in another and `user` in a third, readers will wonder if these are three different things.

5. **Being afraid to rename.** Modern IDEs have robust refactoring tools. Renaming a variable across an entire project takes seconds. Do not live with a bad name because "it would be too much work to change."

6. **Naming booleans without a question-word prefix.** `active` does not read well in conditions. `isActive` reads like English: `if (isActive)` versus `if (active)`.

---

## Best Practices

1. **Spend time choosing names.** A few minutes spent finding the right name saves hours of confusion later. It is one of the highest-leverage activities in programming.

2. **Read your code out loud.** If you cannot explain what a variable represents in plain English, the name is wrong. "We get the, um, thing from the list" means your names need work.

3. **Use the language of the business domain.** If your users say "invoice," do not call it `BillingDocument`. If they say "shopping cart," do not call it `ItemCollection`.

4. **Establish and document team conventions.** Write down which word your team uses for each concept (get vs fetch, create vs make, delete vs remove). Consistency matters more than any particular choice.

5. **Rename fearlessly and often.** When you find a better name, change it immediately. The cost of renaming is seconds; the cost of a bad name is confusion that lasts forever.

6. **Let the name length match the scope.** A loop counter `i` in a three-line loop is fine. A class-level field or a function parameter should have a descriptive name.

---

## Quick Summary

Names are the primary tool for making code readable. Intention-revealing names eliminate the need for comments. Consistent naming across a codebase reduces cognitive load. The time you invest in choosing good names is repaid every time anyone reads your code.

The core rules are: reveal intention, avoid disinformation, make meaningful distinctions, use pronounceable and searchable names, use nouns for classes and verbs for methods, be consistent, and never be clever at the expense of clarity.

---

## Key Points

- A name should tell you why something exists, what it does, and how it is used -- without requiring a comment
- Misleading names (like `accountList` for a Map) are worse than unclear names because they actively deceive
- Noise words (Info, Data, Object, Variable) add length without adding meaning
- Pronounceable names enable productive conversations about code
- Searchable names (named constants instead of magic numbers) make code navigable
- Classes are nouns, methods are verbs -- this convention makes code read like prose
- Pick one word per concept and use it consistently across the entire codebase
- The time spent choosing a good name pays for itself many times over

---

## Practice Questions

1. You encounter a variable named `d` with a comment `// number of days since last login`. Provide three possible good names for this variable and explain when each would be most appropriate.

2. A codebase has three service classes: `UserManager`, `OrderService`, and `ProductHandler`. All three do similar things (CRUD operations). What is wrong with this naming, and how would you fix it?

3. You find a method called `check()` that returns a boolean. Without seeing the implementation, list three possible things this method might do. Then provide three better names that each remove the ambiguity.

4. Your team uses `get`, `fetch`, `retrieve`, `find`, and `load` interchangeably to mean "get data from the database." Design a naming convention that distinguishes between these operations when there are genuine differences, and consolidates them when there are not.

5. Explain why the name `AbstractBaseFactoryManagerServiceImpl` is problematic, even though each word in it has a clear meaning.

---

## Exercises

### Exercise 1: Name That Variable

For each cryptic variable, provide a clear, intention-revealing replacement:

```
a) int x = 86400;
b) String s = "USD";
c) double r = 0.15;
d) boolean f = true;
e) List<String> l = getItems();
f) int n = employees.size();
g) Map<String, Integer> m = loadData();
h) String t = formatOutput();
```

### Exercise 2: Refactor This Class

Rename every identifier in this class to be clean and clear:

Java:
```java
public class DM {
    private Connection c;

    public List<Map<String, Object>> q(String s) {
        List<Map<String, Object>> r = new ArrayList<>();
        try {
            Statement st = c.createStatement();
            ResultSet rs = st.executeQuery(s);
            while (rs.next()) {
                Map<String, Object> row = new HashMap<>();
                int cc = rs.getMetaData().getColumnCount();
                for (int i = 1; i <= cc; i++) {
                    String cn = rs.getMetaData().getColumnName(i);
                    row.put(cn, rs.getObject(i));
                }
                r.add(row);
            }
        } catch (Exception e) {
            System.out.println(e);
        }
        return r;
    }
}
```

### Exercise 3: Naming Audit

Open any project you have worked on. Find five variables, three methods, and two classes with names that could be improved. For each one:
- Write the current name
- Write a better name
- Explain why the new name is better
- Use your IDE to rename it (if it is your project)

---

## What Is Next?

Now that you know how to name things well, it is time to learn how to structure the code that lives inside those well-named containers. Chapter 3 covers functions -- how to keep them small, focused, and easy to understand. You will see a monster 100-line function broken down into clean, small functions that each do one thing well. The combination of good names and good functions is the foundation of all clean code.
