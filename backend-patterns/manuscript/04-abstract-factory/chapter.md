# Chapter 4: The Abstract Factory Pattern

## What You Will Learn

- What the Abstract Factory pattern is and how it differs from Factory Method
- How to create families of related objects that must stay consistent
- How to implement Abstract Factory in Java with a database driver system
- How to implement Abstract Factory in Python with a cloud provider system
- When to use Abstract Factory and when it is overkill
- How Abstract Factory works with dependency injection in real frameworks

## Why This Chapter Matters

In the previous chapter, you learned the Factory Method pattern, which creates a single product. But real backend systems rarely deal with isolated objects. A database layer needs a connection, a query builder, and a migration tool -- and they must all be for the same database engine. A cloud integration needs storage, compute, and queue services -- and they must all be from the same provider.

Mixing a PostgreSQL connection with a MySQL query builder would be a disaster. The Abstract Factory pattern prevents this by ensuring that families of related objects are always created together, consistently.

This pattern appears in database drivers, cloud SDKs, UI toolkits, and any system where objects must come from the same family.

---

## The Problem

Imagine you are building a backend service that supports multiple databases. You need to create connections, execute queries, and run migrations. Each database has its own implementation of each component.

**Before (Inconsistent Families) - The Pain:**

```java
public class DatabaseService {

    public void setupDatabase(String dbType) {
        Connection connection;
        QueryBuilder queryBuilder;
        MigrationRunner migrationRunner;

        if ("postgres".equals(dbType)) {
            connection = new PostgresConnection();
            queryBuilder = new PostgresQueryBuilder();
            migrationRunner = new PostgresMigrationRunner();
        } else if ("mysql".equals(dbType)) {
            connection = new MySQLConnection();
            queryBuilder = new MySQLQueryBuilder();
            migrationRunner = new MySQLMigrationRunner();
        } else if ("sqlite".equals(dbType)) {
            connection = new SQLiteConnection();
            // BUG! Using MySQL query builder with SQLite connection!
            queryBuilder = new MySQLQueryBuilder();
            migrationRunner = new SQLiteMigrationRunner();
        }

        // ... use the components
    }
}
```

```
THE CONSISTENCY PROBLEM:

  PostgreSQL family:
  +-------------+  +------------------+  +-------------------+
  | PgConnection|  | PgQueryBuilder   |  | PgMigrationRunner |
  +-------------+  +------------------+  +-------------------+
       OK               OK                     OK

  MySQL family:
  +---------------+  +--------------------+  +---------------------+
  | MySQLConnection|  | MySQLQueryBuilder  |  | MySQLMigrationRunner|
  +---------------+  +--------------------+  +---------------------+
       OK                  OK                       OK

  MIXED (BUG!):
  +---------------+  +--------------------+  +---------------------+
  | SQLiteConnect |  | MySQLQueryBuilder  |  | SQLiteMigrationRun  |
  +---------------+  +--------------------+  +---------------------+
       SQLite            MySQL!                    SQLite
                     ^^^^^^^^^^^^
                     WRONG FAMILY!
                     MySQL syntax will fail
                     on a SQLite database.
```

The if/else approach lets developers accidentally mix components from different families. The Abstract Factory pattern makes this impossible.

---

## The Solution: Abstract Factory Pattern

The Abstract Factory provides an interface for creating families of related objects without specifying their concrete classes.

```
+---------------------------------------------------------------+
|              ABSTRACT FACTORY PATTERN                         |
+---------------------------------------------------------------+
|                                                               |
|  INTENT: Provide an interface for creating families of        |
|          related or dependent objects without specifying       |
|          their concrete classes.                              |
|                                                               |
|  CATEGORY: Creational                                         |
|                                                               |
+---------------------------------------------------------------+

  UML-like Structure:

  +---------------------------+
  |   AbstractFactory         |
  |   (interface)             |
  +---------------------------+
  | + createConnection()      |
  | + createQueryBuilder()    |
  | + createMigrationRunner() |
  +---------------------------+
        ^             ^
        |             |
  +-----+-----+ +----+------+
  | PostgresDB | | MySQLDB   |
  | Factory    | | Factory   |
  +-----+-----+ +----+------+
        |             |
        |             |
  Creates:       Creates:
  - PgConnection    - MySQLConnection
  - PgQueryBuilder  - MySQLQueryBuilder
  - PgMigration     - MySQLMigration

  KEY GUARANTEE: Each factory only creates
  objects from the SAME family. You cannot
  accidentally mix PostgreSQL and MySQL.

  +-----------------------------------------------+
  |  Client code                                  |
  |                                               |
  |  DatabaseFactory factory = getFactory(config);|
  |  Connection conn = factory.createConnection();|
  |  QueryBuilder qb = factory.createQueryBuilder();
  |                                               |
  |  Client never knows if it is Postgres or MySQL|
  +-----------------------------------------------+
```

---

## Java Implementation: Database Driver System

### Step 1: Define Abstract Product Interfaces

```java
/**
 * Abstract Product A: Database Connection
 */
public interface DatabaseConnection {
    void connect(String host, int port, String database);
    void disconnect();
    boolean isConnected();
    String getDatabaseType();
}

/**
 * Abstract Product B: Query Builder
 */
public interface QueryBuilder {
    QueryBuilder select(String... columns);
    QueryBuilder from(String table);
    QueryBuilder where(String condition);
    QueryBuilder limit(int count);
    String build();
}

/**
 * Abstract Product C: Migration Runner
 */
public interface MigrationRunner {
    void createTable(String name, Map<String, String> columns);
    void addColumn(String table, String column, String type);
    void runMigration(String migrationSql);
    List<String> getPendingMigrations();
}
```

### Step 2: Create Concrete Products for PostgreSQL

```java
// ---- PostgreSQL Family ----

public class PostgresConnection implements DatabaseConnection {
    private boolean connected = false;

    @Override
    public void connect(String host, int port, String database) {
        System.out.println("PostgreSQL: Connecting to "
            + host + ":" + port + "/" + database);
        System.out.println("PostgreSQL: Using libpq protocol v3");
        this.connected = true;
    }

    @Override
    public void disconnect() {
        System.out.println("PostgreSQL: Closing connection");
        this.connected = false;
    }

    @Override
    public boolean isConnected() {
        return connected;
    }

    @Override
    public String getDatabaseType() {
        return "PostgreSQL";
    }
}

public class PostgresQueryBuilder implements QueryBuilder {
    private final StringBuilder query = new StringBuilder();
    private final List<String> parts = new ArrayList<>();

    @Override
    public QueryBuilder select(String... columns) {
        query.append("SELECT ").append(String.join(", ", columns));
        return this;
    }

    @Override
    public QueryBuilder from(String table) {
        // PostgreSQL uses schema-qualified names
        query.append(" FROM public.").append(table);
        return this;
    }

    @Override
    public QueryBuilder where(String condition) {
        query.append(" WHERE ").append(condition);
        return this;
    }

    @Override
    public QueryBuilder limit(int count) {
        // PostgreSQL LIMIT syntax
        query.append(" LIMIT ").append(count);
        return this;
    }

    @Override
    public String build() {
        return query.toString() + ";";
    }
}

public class PostgresMigrationRunner implements MigrationRunner {
    @Override
    public void createTable(String name, Map<String, String> columns) {
        StringBuilder sql = new StringBuilder();
        sql.append("CREATE TABLE IF NOT EXISTS public.")
           .append(name).append(" (\n");

        List<String> colDefs = new ArrayList<>();
        for (Map.Entry<String, String> col : columns.entrySet()) {
            // PostgreSQL uses SERIAL for auto-increment
            String type = col.getValue()
                .replace("AUTO_INCREMENT", "SERIAL");
            colDefs.add("  " + col.getKey() + " " + type);
        }
        sql.append(String.join(",\n", colDefs));
        sql.append("\n);");

        System.out.println("PostgreSQL Migration:\n" + sql);
    }

    @Override
    public void addColumn(String table, String column, String type) {
        System.out.println("PostgreSQL: ALTER TABLE public." + table
            + " ADD COLUMN " + column + " " + type + ";");
    }

    @Override
    public void runMigration(String migrationSql) {
        System.out.println("PostgreSQL: Running migration within "
            + "transaction...");
        System.out.println("PostgreSQL: BEGIN;");
        System.out.println("PostgreSQL: " + migrationSql);
        System.out.println("PostgreSQL: COMMIT;");
    }

    @Override
    public List<String> getPendingMigrations() {
        return List.of("001_create_users", "002_add_email_index");
    }
}
```

### Step 3: Create Concrete Products for MySQL

```java
// ---- MySQL Family ----

public class MySQLConnection implements DatabaseConnection {
    private boolean connected = false;

    @Override
    public void connect(String host, int port, String database) {
        System.out.println("MySQL: Connecting to "
            + host + ":" + port + "/" + database);
        System.out.println("MySQL: Using MySQL protocol v10");
        this.connected = true;
    }

    @Override
    public void disconnect() {
        System.out.println("MySQL: Closing connection");
        this.connected = false;
    }

    @Override
    public boolean isConnected() {
        return connected;
    }

    @Override
    public String getDatabaseType() {
        return "MySQL";
    }
}

public class MySQLQueryBuilder implements QueryBuilder {
    private final StringBuilder query = new StringBuilder();

    @Override
    public QueryBuilder select(String... columns) {
        query.append("SELECT ").append(String.join(", ", columns));
        return this;
    }

    @Override
    public QueryBuilder from(String table) {
        // MySQL uses backtick quoting
        query.append(" FROM `").append(table).append("`");
        return this;
    }

    @Override
    public QueryBuilder where(String condition) {
        query.append(" WHERE ").append(condition);
        return this;
    }

    @Override
    public QueryBuilder limit(int count) {
        // MySQL LIMIT syntax (same as PostgreSQL in this case)
        query.append(" LIMIT ").append(count);
        return this;
    }

    @Override
    public String build() {
        return query.toString() + ";";
    }
}

public class MySQLMigrationRunner implements MigrationRunner {
    @Override
    public void createTable(String name, Map<String, String> columns) {
        StringBuilder sql = new StringBuilder();
        sql.append("CREATE TABLE IF NOT EXISTS `")
           .append(name).append("` (\n");

        List<String> colDefs = new ArrayList<>();
        for (Map.Entry<String, String> col : columns.entrySet()) {
            // MySQL uses AUTO_INCREMENT directly
            colDefs.add("  `" + col.getKey() + "` " + col.getValue());
        }
        sql.append(String.join(",\n", colDefs));
        sql.append("\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;");

        System.out.println("MySQL Migration:\n" + sql);
    }

    @Override
    public void addColumn(String table, String column, String type) {
        System.out.println("MySQL: ALTER TABLE `" + table
            + "` ADD COLUMN `" + column + "` " + type + ";");
    }

    @Override
    public void runMigration(String migrationSql) {
        System.out.println("MySQL: Running migration...");
        System.out.println("MySQL: " + migrationSql);
    }

    @Override
    public List<String> getPendingMigrations() {
        return List.of("001_create_users", "002_add_email_index");
    }
}
```

### Step 4: Define the Abstract Factory

```java
/**
 * The Abstract Factory interface.
 *
 * Each method creates one product from the family.
 * Concrete factories implement ALL methods, ensuring
 * that all products come from the same family.
 */
public interface DatabaseFactory {
    DatabaseConnection createConnection();
    QueryBuilder createQueryBuilder();
    MigrationRunner createMigrationRunner();
}
```

### Step 5: Create Concrete Factories

```java
/**
 * Concrete Factory: creates PostgreSQL family of products.
 */
public class PostgresFactory implements DatabaseFactory {

    @Override
    public DatabaseConnection createConnection() {
        return new PostgresConnection();
    }

    @Override
    public QueryBuilder createQueryBuilder() {
        return new PostgresQueryBuilder();
    }

    @Override
    public MigrationRunner createMigrationRunner() {
        return new PostgresMigrationRunner();
    }
}

/**
 * Concrete Factory: creates MySQL family of products.
 */
public class MySQLFactory implements DatabaseFactory {

    @Override
    public DatabaseConnection createConnection() {
        return new MySQLConnection();
    }

    @Override
    public QueryBuilder createQueryBuilder() {
        return new MySQLQueryBuilder();
    }

    @Override
    public MigrationRunner createMigrationRunner() {
        return new MySQLMigrationRunner();
    }
}
```

### Step 6: Client Code

```java
/**
 * The client works ONLY with the abstract interfaces.
 * It never references PostgreSQL or MySQL classes directly.
 */
public class DatabaseService {

    private final DatabaseFactory factory;

    // The factory is injected - client does not choose it
    public DatabaseService(DatabaseFactory factory) {
        this.factory = factory;
    }

    public void initialize(String host, int port, String database) {
        // Create all components from the SAME family
        DatabaseConnection connection = factory.createConnection();
        QueryBuilder queryBuilder = factory.createQueryBuilder();
        MigrationRunner migrationRunner = factory.createMigrationRunner();

        // Connect
        connection.connect(host, port, database);

        // Run pending migrations
        List<String> pending = migrationRunner.getPendingMigrations();
        System.out.println("Pending migrations: " + pending);

        migrationRunner.createTable("users", Map.of(
            "id", "INT AUTO_INCREMENT PRIMARY KEY",
            "name", "VARCHAR(255) NOT NULL",
            "email", "VARCHAR(255) NOT NULL"
        ));

        // Build a query
        String query = queryBuilder
            .select("id", "name", "email")
            .from("users")
            .where("active = true")
            .limit(10)
            .build();

        System.out.println("Generated query: " + query);

        // Disconnect
        connection.disconnect();
    }
}
```

### Step 7: Usage and Output

```java
public class Main {
    public static void main(String[] args) {
        // Choose factory based on configuration
        String dbType = System.getenv().getOrDefault("DB_TYPE", "postgres");

        DatabaseFactory factory;
        if ("mysql".equals(dbType)) {
            factory = new MySQLFactory();
        } else {
            factory = new PostgresFactory();
        }

        // Client code is identical regardless of which database
        DatabaseService service = new DatabaseService(factory);
        service.initialize("localhost", 5432, "myapp");
    }
}
```

**Output with PostgreSQL factory:**

```
PostgreSQL: Connecting to localhost:5432/myapp
PostgreSQL: Using libpq protocol v3
Pending migrations: [001_create_users, 002_add_email_index]
PostgreSQL Migration:
CREATE TABLE IF NOT EXISTS public.users (
  id INT SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL
);
Generated query: SELECT id, name, email FROM public.users WHERE active = true LIMIT 10;
PostgreSQL: Closing connection
```

**Output with MySQL factory:**

```
MySQL: Connecting to localhost:5432/myapp
MySQL: Using MySQL protocol v10
Pending migrations: [001_create_users, 002_add_email_index]
MySQL Migration:
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
Generated query: SELECT id, name, email FROM `users` WHERE active = true LIMIT 10;
MySQL: Closing connection
```

Notice how the client code (`DatabaseService`) is identical in both cases. The factory ensures every component belongs to the same database family.

---

## Python Implementation: Cloud Provider System

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any


# ---- Abstract Products ----

class CloudStorage(ABC):
    """Abstract Product A: Object storage service."""

    @abstractmethod
    def create_bucket(self, name: str) -> str:
        pass

    @abstractmethod
    def upload(self, bucket: str, key: str, data: bytes) -> str:
        pass

    @abstractmethod
    def download(self, bucket: str, key: str) -> bytes:
        pass

    @abstractmethod
    def get_provider(self) -> str:
        pass


class CloudCompute(ABC):
    """Abstract Product B: Compute/VM service."""

    @abstractmethod
    def launch_instance(self, instance_type: str,
                        image: str) -> str:
        pass

    @abstractmethod
    def stop_instance(self, instance_id: str) -> None:
        pass

    @abstractmethod
    def list_instances(self) -> List[str]:
        pass

    @abstractmethod
    def get_provider(self) -> str:
        pass


class CloudQueue(ABC):
    """Abstract Product C: Message queue service."""

    @abstractmethod
    def create_queue(self, name: str) -> str:
        pass

    @abstractmethod
    def send_message(self, queue_url: str,
                     message: str) -> str:
        pass

    @abstractmethod
    def receive_messages(self, queue_url: str,
                         max_count: int = 10) -> List[str]:
        pass

    @abstractmethod
    def get_provider(self) -> str:
        pass


# ---- AWS Concrete Products ----

class S3Storage(CloudStorage):
    def create_bucket(self, name: str) -> str:
        url = f"s3://{name}"
        print(f"AWS S3: Created bucket {url}")
        return url

    def upload(self, bucket: str, key: str, data: bytes) -> str:
        url = f"s3://{bucket}/{key}"
        print(f"AWS S3: Uploaded {len(data)} bytes to {url}")
        return url

    def download(self, bucket: str, key: str) -> bytes:
        print(f"AWS S3: Downloading s3://{bucket}/{key}")
        return b"mock-data"

    def get_provider(self) -> str:
        return "AWS S3"


class EC2Compute(CloudCompute):
    def launch_instance(self, instance_type: str,
                        image: str) -> str:
        instance_id = "i-0abc123def456"
        print(f"AWS EC2: Launching {instance_type} "
              f"with AMI {image}")
        print(f"AWS EC2: Instance {instance_id} is running")
        return instance_id

    def stop_instance(self, instance_id: str) -> None:
        print(f"AWS EC2: Stopping instance {instance_id}")

    def list_instances(self) -> List[str]:
        return ["i-0abc123def456", "i-0xyz789ghi012"]

    def get_provider(self) -> str:
        return "AWS EC2"


class SQSQueue(CloudQueue):
    def create_queue(self, name: str) -> str:
        url = f"https://sqs.us-east-1.amazonaws.com/123456/{name}"
        print(f"AWS SQS: Created queue {name}")
        return url

    def send_message(self, queue_url: str,
                     message: str) -> str:
        msg_id = "sqs-msg-001"
        print(f"AWS SQS: Sent message to {queue_url}")
        return msg_id

    def receive_messages(self, queue_url: str,
                         max_count: int = 10) -> List[str]:
        print(f"AWS SQS: Polling {queue_url} "
              f"(max {max_count})")
        return ["message-1", "message-2"]

    def get_provider(self) -> str:
        return "AWS SQS"


# ---- GCP Concrete Products ----

class GCSStorage(CloudStorage):
    def create_bucket(self, name: str) -> str:
        url = f"gs://{name}"
        print(f"GCP GCS: Created bucket {url}")
        return url

    def upload(self, bucket: str, key: str, data: bytes) -> str:
        url = f"gs://{bucket}/{key}"
        print(f"GCP GCS: Uploaded {len(data)} bytes to {url}")
        return url

    def download(self, bucket: str, key: str) -> bytes:
        print(f"GCP GCS: Downloading gs://{bucket}/{key}")
        return b"mock-data"

    def get_provider(self) -> str:
        return "GCP Cloud Storage"


class GCECompute(CloudCompute):
    def launch_instance(self, instance_type: str,
                        image: str) -> str:
        instance_id = "gce-vm-abc123"
        print(f"GCP GCE: Launching {instance_type} "
              f"with image {image}")
        print(f"GCP GCE: Instance {instance_id} is running")
        return instance_id

    def stop_instance(self, instance_id: str) -> None:
        print(f"GCP GCE: Stopping instance {instance_id}")

    def list_instances(self) -> List[str]:
        return ["gce-vm-abc123", "gce-vm-def456"]

    def get_provider(self) -> str:
        return "GCP Compute Engine"


class PubSubQueue(CloudQueue):
    def create_queue(self, name: str) -> str:
        topic = f"projects/my-project/topics/{name}"
        print(f"GCP Pub/Sub: Created topic {name}")
        return topic

    def send_message(self, queue_url: str,
                     message: str) -> str:
        msg_id = "pubsub-msg-001"
        print(f"GCP Pub/Sub: Published message to {queue_url}")
        return msg_id

    def receive_messages(self, queue_url: str,
                         max_count: int = 10) -> List[str]:
        print(f"GCP Pub/Sub: Pulling from {queue_url} "
              f"(max {max_count})")
        return ["message-1", "message-2"]

    def get_provider(self) -> str:
        return "GCP Pub/Sub"


# ---- Abstract Factory ----

class CloudProviderFactory(ABC):
    """
    Abstract Factory: creates a family of cloud services.

    Each concrete factory creates Storage, Compute, and Queue
    services from the SAME cloud provider.
    """

    @abstractmethod
    def create_storage(self) -> CloudStorage:
        pass

    @abstractmethod
    def create_compute(self) -> CloudCompute:
        pass

    @abstractmethod
    def create_queue(self) -> CloudQueue:
        pass


# ---- Concrete Factories ----

class AWSFactory(CloudProviderFactory):
    def create_storage(self) -> CloudStorage:
        return S3Storage()

    def create_compute(self) -> CloudCompute:
        return EC2Compute()

    def create_queue(self) -> CloudQueue:
        return SQSQueue()


class GCPFactory(CloudProviderFactory):
    def create_storage(self) -> CloudStorage:
        return GCSStorage()

    def create_compute(self) -> CloudCompute:
        return GCECompute()

    def create_queue(self) -> CloudQueue:
        return PubSubQueue()


# ---- Client Code ----

class InfrastructureManager:
    """
    Client class that works with any cloud provider.
    It only depends on abstract interfaces.
    """

    def __init__(self, factory: CloudProviderFactory):
        self.storage = factory.create_storage()
        self.compute = factory.create_compute()
        self.queue = factory.create_queue()

    def deploy_application(self):
        print(f"\n=== Deploying with {self.storage.get_provider()} "
              f"/ {self.compute.get_provider()} "
              f"/ {self.queue.get_provider()} ===\n")

        # Step 1: Create storage
        bucket = self.storage.create_bucket("my-app-assets")
        self.storage.upload(
            "my-app-assets",
            "config/app.yaml",
            b"database_url: postgres://..."
        )

        # Step 2: Launch compute
        instance_id = self.compute.launch_instance(
            instance_type="medium",
            image="ubuntu-22.04"
        )

        # Step 3: Create message queue
        queue_url = self.queue.create_queue("task-queue")
        self.queue.send_message(queue_url, "deploy:v1.2.3")

        print("\nDeployment complete!")
```

**Usage and output:**

```python
def main():
    import os
    provider = os.getenv("CLOUD_PROVIDER", "aws")

    factories = {
        "aws": AWSFactory,
        "gcp": GCPFactory,
    }

    factory_class = factories.get(provider, AWSFactory)
    factory = factory_class()

    manager = InfrastructureManager(factory)
    manager.deploy_application()


if __name__ == "__main__":
    main()
```

**Output with AWS factory:**

```
=== Deploying with AWS S3 / AWS EC2 / AWS SQS ===

AWS S3: Created bucket s3://my-app-assets
AWS S3: Uploaded 25 bytes to s3://my-app-assets/config/app.yaml
AWS EC2: Launching medium with AMI ubuntu-22.04
AWS EC2: Instance i-0abc123def456 is running
AWS SQS: Created queue task-queue
AWS SQS: Sent message to https://sqs.us-east-1.amazonaws.com/123456/task-queue

Deployment complete!
```

**Output with GCP factory:**

```
=== Deploying with GCP Cloud Storage / GCP Compute Engine / GCP Pub/Sub ===

GCP GCS: Created bucket gs://my-app-assets
GCP GCS: Uploaded 25 bytes to gs://my-app-assets/config/app.yaml
GCP GCE: Launching medium with image ubuntu-22.04
GCP GCE: Instance gce-vm-abc123 is running
GCP Pub/Sub: Created topic task-queue
GCP Pub/Sub: Published message to projects/my-project/topics/task-queue

Deployment complete!
```

---

## Factory Method vs. Abstract Factory

```
+-------------------------------+-------------------------------+
|       FACTORY METHOD          |       ABSTRACT FACTORY        |
+-------------------------------+-------------------------------+
|                               |                               |
| Creates ONE product           | Creates FAMILIES of products  |
|                               |                               |
| Uses inheritance              | Uses composition              |
| (subclass overrides method)   | (factory object is passed in) |
|                               |                               |
| One factory method per        | Multiple factory methods in   |
| creator class                 | one factory interface          |
|                               |                               |
| Example: create a single      | Example: create a matched     |
| Notification                  | set of Connection +            |
|                               | QueryBuilder + Migration       |
|                               |                               |
| Simpler                       | More complex, more powerful    |
|                               |                               |
+-------------------------------+-------------------------------+

  FACTORY METHOD:

  Creator                Product
  +---------------+      +----------+
  | create(): P   |----->| Product  |
  +---------------+      +----------+
        ^                      ^
        |                      |
  EmailCreator          EmailProduct


  ABSTRACT FACTORY:

  Factory                    Product A    Product B    Product C
  +--------------------+    +--------+  +--------+  +--------+
  | createA(): A       |--->|   A    |  |   B    |  |   C    |
  | createB(): B       |--->+--------+  +--------+  +--------+
  | createC(): C       |--->    ^           ^           ^
  +--------------------+        |           |           |
        ^                  Concrete A  Concrete B  Concrete C
        |                  (all from the SAME family)
  ConcreteFactory
```

---

## Real-World Backend Use Case: Multi-Tenant Configuration

In a SaaS application, different tenants might need different infrastructure: one on AWS, another on GCP, a third on Azure. The Abstract Factory lets you configure each tenant independently.

```java
public class TenantService {

    private final Map<String, CloudProviderFactory> tenantFactories;

    public TenantService() {
        this.tenantFactories = new HashMap<>();
    }

    public void registerTenant(String tenantId,
                               CloudProviderFactory factory) {
        tenantFactories.put(tenantId, factory);
    }

    public void handleRequest(String tenantId, Request request) {
        CloudProviderFactory factory = tenantFactories.get(tenantId);
        if (factory == null) {
            throw new RuntimeException("Unknown tenant: " + tenantId);
        }

        // All services for this tenant come from the same provider
        CloudStorage storage = factory.createStorage();
        CloudQueue queue = factory.createQueue();

        // Process the request using the tenant's cloud provider
        storage.upload(
            tenantId + "-bucket",
            request.getKey(),
            request.getData()
        );
        queue.sendMessage(
            tenantId + "-queue",
            "process:" + request.getKey()
        );
    }
}

// Configuration
TenantService service = new TenantService();
service.registerTenant("acme-corp", new AWSFactory());
service.registerTenant("globex-inc", new GCPFactory());
```

```
MULTI-TENANT ABSTRACT FACTORY:

  Tenant: "acme-corp"           Tenant: "globex-inc"
  +-------------------+        +-------------------+
  | AWSFactory        |        | GCPFactory        |
  +-------------------+        +-------------------+
  | S3Storage         |        | GCSStorage        |
  | EC2Compute        |        | GCECompute        |
  | SQSQueue          |        | PubSubQueue       |
  +-------------------+        +-------------------+

  Each tenant gets a consistent family of services.
  No mixing AWS storage with GCP compute.
```

---

## When to Use / When NOT to Use

```
+----------------------------------+----------------------------------+
|  USE ABSTRACT FACTORY WHEN       |  DO NOT USE WHEN                 |
+----------------------------------+----------------------------------+
|                                  |                                  |
| - You have families of related   | - Objects in the "family" are    |
|   objects that must be used      |   independent and do not need    |
|   together consistently         |   to match                       |
|                                  |                                  |
| - You want to enforce that all   | - You have only one product type |
|   products come from the same    |   (use Factory Method instead)   |
|   family                        |                                  |
|                                  |                                  |
| - You need to support multiple   | - The number of families will    |
|   variants (DB engines, cloud    |   never grow beyond one          |
|   providers, OS platforms)       |                                  |
|                                  |                                  |
| - Client code should be          | - Adding the pattern introduces  |
|   independent of how products    |   more complexity than the       |
|   are created and composed       |   problem warrants               |
|                                  |                                  |
+----------------------------------+----------------------------------+
```

---

## Common Mistakes

1. **Using Abstract Factory when you only have one product type.** If you only create connections (no query builders, no migration runners), Factory Method is simpler and sufficient.

2. **Adding a new product to the family later.** If you add a `createBackupService()` method to the abstract factory, every concrete factory must implement it. This can be a significant change if you have many families. Plan your product interfaces carefully.

3. **Making factories too granular.** If every tiny object gets its own factory method, the factory interface becomes bloated. Group related objects logically.

4. **Forgetting that Abstract Factory is about consistency.** The whole point is that products come in matched sets. If your products do not need to match, you do not need Abstract Factory.

5. **Creating factories with state.** Factories should ideally be stateless. They create products; they do not manage them. State management belongs in the client or a separate manager.

---

## Best Practices

1. **Keep factory interfaces small.** Three to five creation methods per factory is typical. If you have more, consider splitting into multiple factories.

2. **Use dependency injection for the factory itself.** Pass the factory to client code via the constructor. This makes it easy to switch families via configuration.

3. **Consider combining with Singleton.** Factories are often stateless and can be singletons. In Spring, they are singletons by default.

4. **Name factories after the family, not the pattern.** `PostgresFactory` is better than `AbstractDatabaseFactoryImpl`. The name should communicate which family it creates.

5. **Test with a test/mock factory.** Create an `InMemoryFactory` that returns simple, fast implementations for testing. This is one of the biggest practical benefits of the pattern.

---

## Quick Summary

| Aspect | Details |
|--------|---------|
| Pattern name | Abstract Factory |
| Category | Creational |
| Intent | Create families of related objects without specifying concrete classes |
| Problem it solves | Mixing objects from different families (PostgreSQL connection with MySQL query builder) |
| Key guarantee | All products from one factory belong to the same family |
| vs. Factory Method | Factory Method creates one product; Abstract Factory creates families |
| Participants | AbstractFactory, ConcreteFactory, AbstractProduct, ConcreteProduct, Client |

---

## Key Points

1. Abstract Factory creates families of related objects. The key word is "families" -- objects that must work together.

2. The pattern guarantees consistency. A PostgreSQL factory can only create PostgreSQL products. It is impossible to accidentally mix families.

3. Adding a new family is easy. Create a new concrete factory and new concrete products. No existing code changes.

4. Adding a new product to all families is hard. Every concrete factory must be updated. This is the main trade-off.

5. Client code depends only on abstract interfaces. It never knows whether it is using PostgreSQL or MySQL, AWS or GCP.

---

## Practice Questions

1. What is the key difference between Factory Method and Abstract Factory? When would you choose one over the other?

2. In the database example, what happens if you need to add SQLite support? What new classes do you create? What existing code do you modify?

3. Why is adding a new product type (e.g., `createBackupService()`) to an Abstract Factory more disruptive than adding a new family? How would you mitigate this?

4. A colleague proposes using Abstract Factory for an application that has one database engine (PostgreSQL) and no plans to support others. Is this appropriate? Why or why not?

5. How does Abstract Factory help with testing? Describe how you would create a test factory for the cloud provider example.

---

## Exercises

### Exercise 1: Add Azure Support

Extend the Python cloud provider example to support Microsoft Azure. Create `AzureFactory` with `AzureBlobStorage`, `AzureVMCompute`, and `AzureServiceBusQueue`. The client code (`InfrastructureManager`) should work without any changes.

### Exercise 2: Document Format Factory

Create an Abstract Factory for document generation. The factory should create three products: `HeaderFormatter`, `BodyFormatter`, and `FooterFormatter`. Implement two families: `HTMLDocumentFactory` (produces HTML tags) and `MarkdownDocumentFactory` (produces Markdown syntax). Build a `DocumentGenerator` client that uses the factory to produce a complete document.

### Exercise 3: Test Factory

For the Java database example, create an `InMemoryDatabaseFactory` that returns lightweight in-memory implementations of `DatabaseConnection`, `QueryBuilder`, and `MigrationRunner`. Use this factory to write a unit test for `DatabaseService` that does not require a real database.

---

## What Is Next?

In the next chapter, we tackle the Builder pattern. While Abstract Factory creates entire families of objects, the Builder pattern handles a different problem: constructing a single complex object step by step. You will see how Builder eliminates the "telescoping constructor" anti-pattern, build fluent APIs for query construction and HTTP request building, and learn how Lombok's `@Builder` annotation does the heavy lifting for you in Java.
