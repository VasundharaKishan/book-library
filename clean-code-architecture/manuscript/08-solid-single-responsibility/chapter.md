# Chapter 8: The Single Responsibility Principle (SRP)

---

## What You Will Learn

By the end of this chapter, you will be able to:

- Define the Single Responsibility Principle using Uncle Bob's actor-based definition
- Distinguish between "a class should do one thing" and "a class should have one reason to change"
- Identify the actors (stakeholders) that drive changes to a class
- Recognize the symptoms of SRP violations in real-world code
- Refactor classes that violate SRP into focused, maintainable components
- Apply SRP at the method, class, and module level
- Understand how SRP relates to cohesion from the previous chapter

---

## Why This Chapter Matters

The Single Responsibility Principle is the most frequently cited and most frequently misunderstood principle in software design. Many developers think it means "a class should do one thing." That definition is too vague to be useful. Does "one thing" mean one method? One algorithm? One feature?

Uncle Bob (Robert C. Martin) refined the definition to something far more actionable: **"A module should be responsible to one, and only one, actor."** An actor is a person, team, or stakeholder who might request changes to the code.

This distinction matters because it shifts your thinking from "what does this code do" to "who would ask me to change this code." When a class serves multiple actors, changes requested by one actor can accidentally break functionality needed by another. SRP prevents this by ensuring that each class has exactly one reason to change.

---

## The Definition: Getting It Right

### The Common (Incomplete) Definition

> "A class should have only one responsibility."

This is the version most developers learn first. It is not wrong, but it is imprecise. What counts as "one responsibility"? Different developers will draw the line in different places.

### Uncle Bob's Actor-Based Definition

> "A module should be responsible to one, and only one, actor."

An **actor** is a group of users or stakeholders who want the system to change in the same way. The Chief Financial Officer (CFO) cares about financial reports. The Chief Technology Officer (CTO) cares about system architecture. The Chief Operating Officer (COO) cares about operational workflows. Each is a different actor.

### Putting the Two Definitions Together

```
┌──────────────────────────────────────────────────────┐
│            SRP: Two Perspectives                     │
├──────────────────────────────────────────────────────┤
│                                                      │
│  VERSION 1: "One reason to change"                   │
│  Focus: What triggers a modification to this class?  │
│                                                      │
│  VERSION 2: "Responsible to one actor"               │
│  Focus: Who requests changes to this class?          │
│                                                      │
│  Both say the same thing from different angles.      │
│  Version 2 is more actionable because it gives       │
│  you a concrete question to ask:                     │
│  "Who would ask me to change this code?"             │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## The Classic Example: The Employee Class

Uncle Bob uses this example in *Clean Architecture* to illustrate why SRP matters at a deep level.

### BEFORE: Three Actors, One Class

```java
public class Employee {
    private String name;
    private double baseSalary;
    private int hoursWorked;

    // Used by the CFO's team (accounting/payroll)
    public double calculatePay() {
        double regularPay = baseSalary;
        double overtimePay = calculateOvertimeHours() * (baseSalary / 160) * 1.5;
        return regularPay + overtimePay;
    }

    // Used by the COO's team (operations/HR)
    public void reportHours() {
        System.out.println(name + " worked " + hoursWorked + " hours");
        System.out.println("Regular: " + calculateRegularHours());
        System.out.println("Overtime: " + calculateOvertimeHours());
    }

    // Used by the CTO's team (database/technical)
    public void save() {
        // Save employee data to the database
        Database.execute("INSERT INTO employees ...", this);
    }

    // Shared helper method -- this is the danger zone
    private int calculateOvertimeHours() {
        return Math.max(0, hoursWorked - 40);
    }

    private int calculateRegularHours() {
        return Math.min(hoursWorked, 40);
    }
}
```

### Why This Is Dangerous

Three different actors depend on this class:

```
          ┌─────────┐
          │   CFO   │ -- cares about calculatePay()
          └────┬────┘
               │
          ┌────▼────────────────┐
          │                     │
          │     Employee        │
          │                     │
          │  calculatePay()     │◄── CFO's team
          │  reportHours()      │◄── COO's team
          │  save()             │◄── CTO's team
          │                     │
          │  calculateOvertime()│◄── shared helper!
          │                     │
          └─────────────────────┘
               ▲           ▲
          ┌────┴────┐ ┌────┴────┐
          │   COO   │ │   CTO   │
          └─────────┘ └─────────┘
```

Now imagine this scenario:

1. The CFO's team asks you to change how overtime is calculated for payroll purposes. They want overtime to start after 45 hours instead of 40.

2. You modify `calculateOvertimeHours()` to use 45.

3. The COO's team runs their hours report the next day. The report now shows overtime starting at 45 hours. But the COO's team still uses the 40-hour threshold for operational planning. Their reports are now wrong.

4. Nobody notices the bug until the end of the month when operational reports do not match expectations.

This is the core danger of SRP violations: **changes requested by one actor accidentally affect another actor.** The shared `calculateOvertimeHours()` method is used by both `calculatePay()` and `reportHours()`, but each actor has different rules for what counts as overtime.

### AFTER: One Class Per Actor

**Java:**

```java
// Responsible to: CFO's team (payroll/accounting)
public class PayCalculator {
    private static final int PAYROLL_OVERTIME_THRESHOLD = 45;

    public double calculatePay(Employee employee) {
        double regularPay = employee.getBaseSalary();
        int overtimeHours = Math.max(0,
            employee.getHoursWorked() - PAYROLL_OVERTIME_THRESHOLD);
        double overtimePay = overtimeHours
            * (employee.getBaseSalary() / 160) * 1.5;
        return regularPay + overtimePay;
    }
}

// Responsible to: COO's team (operations/HR)
public class HoursReporter {
    private static final int OPERATIONS_OVERTIME_THRESHOLD = 40;

    public HoursReport generateReport(Employee employee) {
        int regular = Math.min(employee.getHoursWorked(),
            OPERATIONS_OVERTIME_THRESHOLD);
        int overtime = Math.max(0,
            employee.getHoursWorked() - OPERATIONS_OVERTIME_THRESHOLD);
        return new HoursReport(employee.getName(), regular, overtime);
    }
}

// Responsible to: CTO's team (technical/infrastructure)
public class EmployeeRepository {
    private final Database database;

    public EmployeeRepository(Database database) {
        this.database = database;
    }

    public void save(Employee employee) {
        database.execute("INSERT INTO employees ...", employee);
    }

    public Employee findById(int id) {
        return database.query("SELECT * FROM employees WHERE id = ?", id);
    }
}

// The Employee class is now just a data holder
public class Employee {
    private String name;
    private double baseSalary;
    private int hoursWorked;

    public Employee(String name, double baseSalary, int hoursWorked) {
        this.name = name;
        this.baseSalary = baseSalary;
        this.hoursWorked = hoursWorked;
    }

    public String getName() { return name; }
    public double getBaseSalary() { return baseSalary; }
    public int getHoursWorked() { return hoursWorked; }
}
```

**Python:**

```python
# Responsible to: CFO's team (payroll/accounting)
class PayCalculator:
    PAYROLL_OVERTIME_THRESHOLD = 45

    def calculate_pay(self, employee: Employee) -> float:
        regular_pay = employee.base_salary
        overtime_hours = max(0,
            employee.hours_worked - self.PAYROLL_OVERTIME_THRESHOLD)
        overtime_pay = overtime_hours * (employee.base_salary / 160) * 1.5
        return regular_pay + overtime_pay


# Responsible to: COO's team (operations/HR)
class HoursReporter:
    OPERATIONS_OVERTIME_THRESHOLD = 40

    def generate_report(self, employee: Employee) -> HoursReport:
        regular = min(employee.hours_worked,
                      self.OPERATIONS_OVERTIME_THRESHOLD)
        overtime = max(0,
            employee.hours_worked - self.OPERATIONS_OVERTIME_THRESHOLD)
        return HoursReport(employee.name, regular, overtime)


# Responsible to: CTO's team (technical/infrastructure)
class EmployeeRepository:
    def __init__(self, database):
        self._database = database

    def save(self, employee: Employee) -> None:
        self._database.execute("INSERT INTO employees ...", employee)

    def find_by_id(self, employee_id: int) -> Employee:
        return self._database.query(
            "SELECT * FROM employees WHERE id = ?", employee_id
        )


# Data holder -- no business logic
class Employee:
    def __init__(self, name: str, base_salary: float, hours_worked: int):
        self.name = name
        self.base_salary = base_salary
        self.hours_worked = hours_worked
```

Now each class changes for exactly one reason, requested by exactly one actor:

```
┌──────────┐        ┌───────────────────┐
│   CFO    │───────►│  PayCalculator    │
└──────────┘        └───────────────────┘

┌──────────┐        ┌───────────────────┐
│   COO    │───────►│  HoursReporter    │
└──────────┘        └───────────────────┘

┌──────────┐        ┌───────────────────┐
│   CTO    │───────►│ EmployeeRepository│
└──────────┘        └───────────────────┘
```

The CFO's overtime rule change no longer affects the COO's reports. Each actor's logic is isolated.

---

## Identifying Responsibilities: A Practical Method

Here is a step-by-step method for finding SRP violations in your code:

### Step 1: List the Methods

Write down every public method in the class.

### Step 2: Group by Actor

For each method, ask: "Who would request a change to this method?" Group methods by their actor.

### Step 3: Check for Multiple Groups

If you find two or more groups, the class violates SRP. Each group should become its own class.

### Worked Example

```
UserService class methods:
  - registerUser()          --> Product team
  - authenticateUser()      --> Security team
  - sendVerificationEmail() --> Marketing team
  - generateApiToken()      --> Security team
  - updateUserProfile()     --> Product team
  - logUserActivity()       --> Operations team
  - exportUserData()        --> Compliance team

Groups found:
  Product team:    registerUser(), updateUserProfile()
  Security team:   authenticateUser(), generateApiToken()
  Marketing team:  sendVerificationEmail()
  Operations team: logUserActivity()
  Compliance team: exportUserData()

Result: 5 actors = 5 classes needed
```

The refactored classes:

```
┌─────────────────────────┐
│   UserRegistration      │  <-- Product team
│   Service               │
├─────────────────────────┤
│ + registerUser()        │
│ + updateUserProfile()   │
└─────────────────────────┘

┌─────────────────────────┐
│   Authentication        │  <-- Security team
│   Service               │
├─────────────────────────┤
│ + authenticateUser()    │
│ + generateApiToken()    │
└─────────────────────────┘

┌─────────────────────────┐
│   UserNotification      │  <-- Marketing team
│   Service               │
├─────────────────────────┤
│ + sendVerificationEmail()│
└─────────────────────────┘

┌─────────────────────────┐
│   ActivityLogger        │  <-- Operations team
├─────────────────────────┤
│ + logUserActivity()     │
└─────────────────────────┘

┌─────────────────────────┐
│   UserDataExporter      │  <-- Compliance team
├─────────────────────────┤
│ + exportUserData()      │
└─────────────────────────┘
```

---

## Before and After: UserService Refactoring

### BEFORE: UserService That Does Everything

**Java:**

```java
public class UserService {
    private final UserRepository userRepo;
    private final PasswordEncoder encoder;
    private final JavaMailSender mailSender;
    private final Logger logger;
    private final JwtTokenProvider tokenProvider;
    private final TemplateEngine templateEngine;

    public UserService(UserRepository userRepo, PasswordEncoder encoder,
                       JavaMailSender mailSender, Logger logger,
                       JwtTokenProvider tokenProvider,
                       TemplateEngine templateEngine) {
        this.userRepo = userRepo;
        this.encoder = encoder;
        this.mailSender = mailSender;
        this.logger = logger;
        this.tokenProvider = tokenProvider;
        this.templateEngine = templateEngine;
    }

    // --- Authentication (Security team) ---
    public AuthResult authenticate(String email, String password) {
        User user = userRepo.findByEmail(email);
        if (user == null) {
            logger.warn("Login attempt for unknown email: " + email);
            return AuthResult.failure("Invalid credentials");
        }
        if (!encoder.matches(password, user.getPasswordHash())) {
            user.incrementFailedLogins();
            userRepo.save(user);
            logger.warn("Failed login for: " + email);
            return AuthResult.failure("Invalid credentials");
        }
        String token = tokenProvider.generateToken(user);
        logger.info("Successful login for: " + email);
        return AuthResult.success(token);
    }

    // --- Registration (Product team) ---
    public User register(String name, String email, String password) {
        if (userRepo.findByEmail(email) != null) {
            throw new DuplicateEmailException("Email already registered");
        }
        String hashedPassword = encoder.encode(password);
        User user = new User(name, email, hashedPassword);
        userRepo.save(user);

        // Send welcome email (Marketing team concern!)
        String body = templateEngine.render("welcome-email",
            Map.of("name", name));
        mailSender.send(email, "Welcome!", body);

        logger.info("New user registered: " + email);
        return user;
    }

    // --- Email notifications (Marketing team) ---
    public void sendPasswordResetEmail(String email) {
        User user = userRepo.findByEmail(email);
        if (user == null) return;

        String token = tokenProvider.generateResetToken(user);
        String body = templateEngine.render("password-reset",
            Map.of("token", token, "name", user.getName()));
        mailSender.send(email, "Password Reset", body);

        logger.info("Password reset email sent to: " + email);
    }

    // --- Logging (Operations team) ---
    public void logUserActivity(int userId, String activity) {
        logger.info("User " + userId + ": " + activity);
        userRepo.saveActivityLog(userId, activity, LocalDateTime.now());
    }
}
```

This class has four actors: the security team, the product team, the marketing team, and the operations team. It changes for four different reasons.

### AFTER: Focused Classes

**Java:**

```java
// Actor: Security team
// Reason to change: authentication rules, token policies, lockout policies
public class AuthenticationService {
    private final UserRepository userRepo;
    private final PasswordEncoder encoder;
    private final JwtTokenProvider tokenProvider;
    private final Logger logger;

    public AuthenticationService(UserRepository userRepo,
                                  PasswordEncoder encoder,
                                  JwtTokenProvider tokenProvider,
                                  Logger logger) {
        this.userRepo = userRepo;
        this.encoder = encoder;
        this.tokenProvider = tokenProvider;
        this.logger = logger;
    }

    public AuthResult authenticate(String email, String password) {
        User user = userRepo.findByEmail(email);
        if (user == null) {
            logger.warn("Login attempt for unknown email: " + email);
            return AuthResult.failure("Invalid credentials");
        }
        if (!encoder.matches(password, user.getPasswordHash())) {
            user.incrementFailedLogins();
            userRepo.save(user);
            logger.warn("Failed login for: " + email);
            return AuthResult.failure("Invalid credentials");
        }
        String token = tokenProvider.generateToken(user);
        logger.info("Successful login for: " + email);
        return AuthResult.success(token);
    }
}
```

```java
// Actor: Product team
// Reason to change: registration requirements, profile fields, validation rules
public class UserRegistrationService {
    private final UserRepository userRepo;
    private final PasswordEncoder encoder;
    private final UserNotificationService notifications;
    private final Logger logger;

    public UserRegistrationService(UserRepository userRepo,
                                    PasswordEncoder encoder,
                                    UserNotificationService notifications,
                                    Logger logger) {
        this.userRepo = userRepo;
        this.encoder = encoder;
        this.notifications = notifications;
        this.logger = logger;
    }

    public User register(String name, String email, String password) {
        if (userRepo.findByEmail(email) != null) {
            throw new DuplicateEmailException("Email already registered");
        }
        String hashedPassword = encoder.encode(password);
        User user = new User(name, email, hashedPassword);
        userRepo.save(user);

        notifications.sendWelcomeEmail(user);

        logger.info("New user registered: " + email);
        return user;
    }
}
```

```java
// Actor: Marketing team
// Reason to change: email templates, email providers, notification channels
public class UserNotificationService {
    private final JavaMailSender mailSender;
    private final TemplateEngine templateEngine;
    private final JwtTokenProvider tokenProvider;

    public UserNotificationService(JavaMailSender mailSender,
                                    TemplateEngine templateEngine,
                                    JwtTokenProvider tokenProvider) {
        this.mailSender = mailSender;
        this.templateEngine = templateEngine;
        this.tokenProvider = tokenProvider;
    }

    public void sendWelcomeEmail(User user) {
        String body = templateEngine.render("welcome-email",
            Map.of("name", user.getName()));
        mailSender.send(user.getEmail(), "Welcome!", body);
    }

    public void sendPasswordResetEmail(User user) {
        String token = tokenProvider.generateResetToken(user);
        String body = templateEngine.render("password-reset",
            Map.of("token", token, "name", user.getName()));
        mailSender.send(user.getEmail(), "Password Reset", body);
    }
}
```

```java
// Actor: Operations team
// Reason to change: logging format, audit requirements, monitoring needs
public class UserActivityLogger {
    private final Logger logger;
    private final UserRepository userRepo;

    public UserActivityLogger(Logger logger, UserRepository userRepo) {
        this.logger = logger;
        this.userRepo = userRepo;
    }

    public void logActivity(int userId, String activity) {
        logger.info("User " + userId + ": " + activity);
        userRepo.saveActivityLog(userId, activity, LocalDateTime.now());
    }
}
```

**Python version:**

```python
# Actor: Security team
class AuthenticationService:
    def __init__(self, user_repo, password_encoder, token_provider, logger):
        self._user_repo = user_repo
        self._encoder = password_encoder
        self._token_provider = token_provider
        self._logger = logger

    def authenticate(self, email: str, password: str) -> AuthResult:
        user = self._user_repo.find_by_email(email)
        if user is None:
            self._logger.warning(f"Login attempt for unknown email: {email}")
            return AuthResult.failure("Invalid credentials")

        if not self._encoder.matches(password, user.password_hash):
            user.increment_failed_logins()
            self._user_repo.save(user)
            self._logger.warning(f"Failed login for: {email}")
            return AuthResult.failure("Invalid credentials")

        token = self._token_provider.generate_token(user)
        self._logger.info(f"Successful login for: {email}")
        return AuthResult.success(token)


# Actor: Product team
class UserRegistrationService:
    def __init__(self, user_repo, password_encoder, notifications, logger):
        self._user_repo = user_repo
        self._encoder = password_encoder
        self._notifications = notifications
        self._logger = logger

    def register(self, name: str, email: str, password: str) -> User:
        if self._user_repo.find_by_email(email) is not None:
            raise DuplicateEmailError("Email already registered")

        hashed_password = self._encoder.encode(password)
        user = User(name, email, hashed_password)
        self._user_repo.save(user)

        self._notifications.send_welcome_email(user)

        self._logger.info(f"New user registered: {email}")
        return user


# Actor: Marketing team
class UserNotificationService:
    def __init__(self, mail_sender, template_engine, token_provider):
        self._mail_sender = mail_sender
        self._template_engine = template_engine
        self._token_provider = token_provider

    def send_welcome_email(self, user: User) -> None:
        body = self._template_engine.render(
            "welcome-email", {"name": user.name}
        )
        self._mail_sender.send(user.email, "Welcome!", body)

    def send_password_reset_email(self, user: User) -> None:
        token = self._token_provider.generate_reset_token(user)
        body = self._template_engine.render(
            "password-reset", {"token": token, "name": user.name}
        )
        self._mail_sender.send(user.email, "Password Reset", body)


# Actor: Operations team
class UserActivityLogger:
    def __init__(self, logger, user_repo):
        self._logger = logger
        self._user_repo = user_repo

    def log_activity(self, user_id: int, activity: str) -> None:
        self._logger.info(f"User {user_id}: {activity}")
        self._user_repo.save_activity_log(
            user_id, activity, datetime.now()
        )
```

---

## Symptoms of SRP Violation

How do you know when a class violates SRP without doing a full actor analysis? Look for these symptoms:

### Symptom 1: The Class Has Many Unrelated Import Statements

```java
import java.sql.*;              // database
import javax.mail.*;            // email
import com.itextpdf.*;          // PDF generation
import org.apache.poi.*;        // Excel export
import com.stripe.api.*;        // payment processing
import org.slf4j.*;             // logging
```

If your class imports libraries for databases, email, PDFs, and payment processing, it is doing too many things.

### Symptom 2: The Class Changes Frequently for Different Reasons

Look at your version control history. If the commit messages for a single file include:

- "Fix tax calculation bug"
- "Update email template"
- "Change database query for performance"
- "Add new report format"

Four different kinds of changes to one file means four responsibilities.

### Symptom 3: Hard to Name the Class

If you struggle to name a class without using vague words like "Manager," "Processor," "Handler," or "Service," it probably does too much. A class with a clear responsibility has a clear name.

```
Vague names (red flag):     Specific names (good sign):
  DataManager                 OrderRepository
  RequestHandler              PasswordHasher
  UserProcessor               InvoiceGenerator
  SystemService               ShippingCalculator
  ApplicationHelper           EmailTemplateRenderer
```

### Symptom 4: Large Constructor

If the constructor takes more than three or four dependencies, the class probably has too many responsibilities. Each dependency often corresponds to a different concern.

```java
// Red flag: 7 dependencies = likely 3-4 responsibilities
public UserService(UserRepository repo,
                   PasswordEncoder encoder,
                   EmailSender emailSender,
                   SmsService smsService,
                   PaymentGateway paymentGateway,
                   AuditLogger auditLogger,
                   CacheManager cacheManager) {
    // ...
}
```

### Symptom 5: Methods That Do Not Use Each Other

In a class with a single responsibility, methods tend to call each other or operate on the same data. If a class has clusters of methods that never interact, those clusters are separate responsibilities.

```
┌───────────────────────────────────┐
│         UserService               │
│                                   │
│  Cluster A:         Cluster B:    │
│  ┌─────────────┐  ┌────────────┐ │
│  │ register()  │  │ sendEmail()│ │
│  │ validate()  │  │ formatMsg()│ │
│  │ saveUser()  │  │ getTempl() │ │
│  └─────────────┘  └────────────┘ │
│                                   │
│  These clusters never interact.   │
│  They should be separate classes. │
└───────────────────────────────────┘
```

---

## SRP at Different Levels

SRP applies not just to classes, but to methods and modules as well.

### SRP at the Method Level

A method should do one thing. If a method name requires "and" to describe what it does, it should be split.

**BEFORE:**

```python
def create_user_and_send_email(name, email, password):
    # Validate input
    if not email or "@" not in email:
        raise ValueError("Invalid email")
    if len(password) < 8:
        raise ValueError("Password too short")

    # Create user
    hashed = hash_password(password)
    user = User(name, email, hashed)
    db.save(user)

    # Send email
    body = f"Welcome {name}!"
    email_client.send(email, "Welcome", body)

    return user
```

**AFTER:**

```python
def create_user(name: str, email: str, password: str) -> User:
    validate_registration_input(email, password)
    hashed = hash_password(password)
    user = User(name, email, hashed)
    db.save(user)
    return user

def validate_registration_input(email: str, password: str) -> None:
    if not email or "@" not in email:
        raise ValueError("Invalid email")
    if len(password) < 8:
        raise ValueError("Password too short")

def send_welcome_email(user: User) -> None:
    body = f"Welcome {user.name}!"
    email_client.send(user.email, "Welcome", body)

# The caller coordinates:
user = create_user(name, email, password)
send_welcome_email(user)
```

### SRP at the Module/Package Level

At a larger scale, SRP means that a module or package should serve one purpose.

```
project/
  auth/                 # Authentication module
    authentication.py
    token_manager.py
    password_hasher.py

  notifications/        # Notification module
    email_sender.py
    sms_sender.py
    templates.py

  billing/              # Billing module
    invoice_generator.py
    payment_processor.py
    tax_calculator.py

  users/                # User management module
    user_repository.py
    user_validator.py
    profile_service.py
```

Each package has a clear purpose. The auth package changes when authentication requirements change. The billing package changes when billing requirements change. They do not interfere with each other.

---

## Real-World Scenario: The Report Generator

You inherit a `ReportGenerator` class that creates reports for three departments:

```python
class ReportGenerator:
    def __init__(self, db, pdf_engine, email_sender):
        self.db = db
        self.pdf_engine = pdf_engine
        self.email_sender = email_sender

    def generate_sales_report(self, month, year):
        """Sales team wants: revenue by region, top products."""
        data = self.db.query(
            "SELECT region, SUM(amount) FROM sales "
            "WHERE month = ? AND year = ? GROUP BY region",
            month, year
        )
        pdf = self.pdf_engine.create_report(
            title=f"Sales Report - {month}/{year}",
            data=data,
            chart_type="bar"
        )
        self.email_sender.send("sales@company.com",
                               "Monthly Sales Report", pdf)
        return pdf

    def generate_inventory_report(self, warehouse_id):
        """Operations team wants: stock levels, reorder alerts."""
        data = self.db.query(
            "SELECT product, quantity, reorder_level FROM inventory "
            "WHERE warehouse_id = ?", warehouse_id
        )
        alerts = [row for row in data if row["quantity"] < row["reorder_level"]]
        pdf = self.pdf_engine.create_report(
            title=f"Inventory Report - Warehouse {warehouse_id}",
            data=data,
            alerts=alerts
        )
        self.email_sender.send("ops@company.com",
                               "Inventory Report", pdf)
        return pdf

    def generate_hr_report(self, department):
        """HR team wants: headcount, turnover rate, open positions."""
        data = self.db.query(
            "SELECT * FROM employees WHERE department = ?", department
        )
        turnover = self.db.query(
            "SELECT COUNT(*) FROM departures WHERE department = ? "
            "AND year = YEAR(CURDATE())", department
        )
        pdf = self.pdf_engine.create_report(
            title=f"HR Report - {department}",
            data=data,
            turnover_rate=turnover
        )
        self.email_sender.send("hr@company.com", "HR Report", pdf)
        return pdf
```

Three actors (sales, operations, HR) means three classes:

```python
class SalesReportGenerator:
    def __init__(self, sales_repo, pdf_engine, email_sender):
        self._repo = sales_repo
        self._pdf = pdf_engine
        self._email = email_sender

    def generate(self, month: int, year: int) -> bytes:
        data = self._repo.get_revenue_by_region(month, year)
        pdf = self._pdf.create_report(
            title=f"Sales Report - {month}/{year}",
            data=data, chart_type="bar"
        )
        self._email.send("sales@company.com",
                         "Monthly Sales Report", pdf)
        return pdf


class InventoryReportGenerator:
    def __init__(self, inventory_repo, pdf_engine, email_sender):
        self._repo = inventory_repo
        self._pdf = pdf_engine
        self._email = email_sender

    def generate(self, warehouse_id: int) -> bytes:
        data = self._repo.get_stock_levels(warehouse_id)
        alerts = [item for item in data
                  if item.quantity < item.reorder_level]
        pdf = self._pdf.create_report(
            title=f"Inventory Report - Warehouse {warehouse_id}",
            data=data, alerts=alerts
        )
        self._email.send("ops@company.com",
                         "Inventory Report", pdf)
        return pdf


class HrReportGenerator:
    def __init__(self, hr_repo, pdf_engine, email_sender):
        self._repo = hr_repo
        self._pdf = pdf_engine
        self._email = email_sender

    def generate(self, department: str) -> bytes:
        data = self._repo.get_employees(department)
        turnover = self._repo.get_turnover_rate(department)
        pdf = self._pdf.create_report(
            title=f"HR Report - {department}",
            data=data, turnover_rate=turnover
        )
        self._email.send("hr@company.com", "HR Report", pdf)
        return pdf
```

Now when the sales team wants a new chart type, only `SalesReportGenerator` changes. When HR wants to add a diversity metric, only `HrReportGenerator` changes.

---

## Common Mistakes

### Mistake 1: Taking SRP Too Far

SRP does not mean "one method per class." A class with a single responsibility can have many methods, as long as they all serve the same actor and change for the same reason.

```java
// This is fine! All methods serve the same actor (tax accountants)
// and change for the same reason (tax rules change)
public class TaxCalculator {
    public double calculateIncomeTax(double income) { ... }
    public double calculateSalesTax(double amount, String state) { ... }
    public double calculatePropertyTax(double value, String county) { ... }
    public double calculateCapitalGainsTax(double gains) { ... }
    public TaxBracket determineBracket(double income) { ... }
}
```

### Mistake 2: Confusing SRP with the Interface Segregation Principle

SRP is about who requests changes (actors). ISP is about what clients depend on (interfaces). A class can satisfy SRP while violating ISP, and vice versa.

### Mistake 3: Splitting by Technical Layer Instead of by Actor

Some developers split by layer (controller, service, repository) but keep all actors in each layer:

```
// WRONG: Split by layer, but UserService still serves 4 actors
UserController  -->  UserService  -->  UserRepository
                     (auth + email + logging + registration)
```

```
// RIGHT: Split by actor within each layer
AuthController  -->  AuthService     -->  UserRepository
RegController   -->  RegistrationSvc -->  UserRepository
```

### Mistake 4: Ignoring SRP Because "It Works"

Code that violates SRP works fine... until it does not. The problems emerge over time: merge conflicts, accidental side effects, difficulty testing. By the time the pain is obvious, the code is much harder to fix.

---

## Best Practices

1. **Ask "who would request a change?"** for every class you write. If the answer is more than one actor, consider splitting.

2. **Watch for classes with many unrelated dependencies.** A constructor with six parameters from different domains (database, email, PDF, payments) is a red flag.

3. **Check your version control history.** If a file changes frequently for different reasons, it violates SRP.

4. **Name classes precisely.** A good name like `ShippingCostCalculator` makes SRP violations obvious. A vague name like `OrderHelper` hides them.

5. **Apply SRP at the method level first.** Methods that do one thing naturally lead to classes that have one responsibility.

6. **Use a facade or coordinator when needed.** After splitting a class, you may need a thin coordinator class that delegates to the focused classes. This is fine; the coordinator itself has one responsibility: orchestration.

7. **Do not split prematurely.** If a class is small, has few methods, and is unlikely to attract new responsibilities, leave it alone. Split when you feel the pain.

---

## Quick Summary

The Single Responsibility Principle states that a class should be responsible to one, and only one, actor. An actor is a stakeholder who would request changes to the code. When a class serves multiple actors, changes requested by one can accidentally break functionality needed by another. You identify SRP violations by listing a class's methods, grouping them by actor, and checking whether multiple groups exist. Symptoms include many unrelated imports, frequent changes for different reasons, vague class names, large constructors, and clusters of methods that do not interact. SRP applies at the method, class, and module levels.

---

## Key Points

- SRP means **one actor, one reason to change** -- not "one method per class."
- Uncle Bob's definition: "A module should be responsible to one, and only one, actor."
- **Actors** are stakeholders (people, teams, roles) who request changes to the system.
- The danger of SRP violations: changes for one actor **accidentally break** functionality for another actor.
- **Symptoms** of SRP violations: many unrelated imports, vague class names, large constructors, clusters of non-interacting methods, and frequent changes for different reasons.
- Apply SRP at **three levels**: method, class, and module/package.
- **Do not over-apply SRP.** A class with 10 methods can still have one responsibility if all methods serve the same actor.

---

## Practice Questions

1. A class called `PaymentProcessor` has these methods: `chargeCard()`, `refund()`, `generateReceipt()`, `sendReceiptEmail()`, and `logTransaction()`. Identify the actors and suggest how to split this class.

2. Your colleague says: "SRP means every class should have exactly one method." How would you correct this misunderstanding?

3. Look at your current project. Find one class that serves multiple actors. Which actors does it serve? How would you refactor it?

4. A `NotificationService` handles email, SMS, and push notifications. Does this violate SRP? It depends. Explain under what circumstances it does and does not violate SRP.

5. Why is "a class should do one thing" an incomplete definition of SRP? Give an example where this definition leads to a wrong conclusion.

---

## Exercises

### Exercise 1: Actor Analysis

Analyze the following class. Identify each actor, which methods they own, and how you would split the class.

```java
public class ProductService {
    public Product createProduct(String name, double price) { ... }
    public void updatePrice(int productId, double newPrice) { ... }
    public List<Product> searchProducts(String query) { ... }
    public byte[] generateProductCatalog() { ... }
    public void syncWithWarehouse(int productId) { ... }
    public void applyBulkDiscount(List<Integer> productIds, double pct) { ... }
    public ProductAnalytics getAnalytics(int productId) { ... }
}
```

### Exercise 2: Refactor a Python Class

Refactor this class to follow SRP. Create separate classes for each responsibility.

```python
class DocumentManager:
    def __init__(self, storage, converter, notifier, logger):
        self.storage = storage
        self.converter = converter
        self.notifier = notifier
        self.logger = logger

    def upload(self, file_path, user_id):
        content = open(file_path, 'rb').read()
        doc_id = self.storage.save(content, user_id)
        self.logger.info(f"Document {doc_id} uploaded by {user_id}")
        self.notifier.notify(user_id, f"Document {doc_id} uploaded")
        return doc_id

    def convert_to_pdf(self, doc_id):
        content = self.storage.load(doc_id)
        pdf = self.converter.to_pdf(content)
        self.storage.save(pdf, doc_id + "_pdf")
        return doc_id + "_pdf"

    def share(self, doc_id, recipient_email):
        link = self.storage.generate_link(doc_id)
        self.notifier.send_email(recipient_email, "Shared doc", link)
        self.logger.info(f"Document {doc_id} shared with {recipient_email}")
```

### Exercise 3: Commit History Analysis

Look at the git log for a file in your project that changes frequently. Categorize each commit message by the type of change (bug fix, feature, UI change, database change, etc.). If you find more than two categories, the file likely violates SRP. Propose how you would split it.

---

## What Is Next?

With SRP in your toolkit, you can ensure that each class changes for exactly one reason. The next chapter explores the **Open-Closed Principle (OCP)** -- the idea that software should be open for extension but closed for modification. You will learn how to design classes that can gain new behavior without changing existing code, using techniques like the Strategy pattern and polymorphism.
