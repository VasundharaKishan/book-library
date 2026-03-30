# Chapter 23: Scheduling

## What You Will Learn

- What scheduling is and when to use it.
- How to enable scheduling with @EnableScheduling.
- How to run tasks at fixed intervals with @Scheduled(fixedRate).
- How to run tasks with delays between executions using @Scheduled(fixedDelay).
- How to use cron expressions for complex schedules.
- How cron expression fields work (second, minute, hour, day, month, weekday).
- How to set an initial delay before the first execution.
- How to handle errors in scheduled tasks.

## Why This Chapter Matters

Think about your daily routine. Your alarm clock goes off at 7 AM every morning. Your coffee maker starts brewing at 6:50 AM. Your sprinkler system waters the lawn every Tuesday and Thursday at 6 PM. These are all scheduled tasks. You set them up once, and they run automatically.

Applications need the same thing. You might want to:
- Clean up expired sessions every hour.
- Send a daily email report at 8 AM.
- Check for new orders every 30 seconds.
- Back up the database every night at midnight.
- Remove temporary files every Sunday.

Without scheduling, someone would have to manually trigger these tasks. That is not practical. Spring Boot's scheduling support lets you automate tasks with just a few annotations.

---

## 23.1 Enabling Scheduling

Scheduling is disabled by default in Spring Boot. You enable it by adding `@EnableScheduling` to a configuration class or your main application class:

```java
// src/main/java/com/example/scheduling/SchedulingApplication.java
package com.example.scheduling;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling  // Enables scheduling support
public class SchedulingApplication {

    public static void main(String[] args) {
        SpringApplication.run(SchedulingApplication.class, args);
    }
}
```

**Line-by-line explanation:**

- `@EnableScheduling` -- This annotation tells Spring Boot to look for methods annotated with `@Scheduled` and run them according to their schedule. Without this, `@Scheduled` annotations are silently ignored.

That is it. One annotation enables the entire scheduling system.

---

## 23.2 Fixed Rate Scheduling

The simplest type of scheduling runs a task at a fixed interval. The task runs every N milliseconds, regardless of how long the previous execution took:

```java
// src/main/java/com/example/scheduling/task/FixedRateTask.java
package com.example.scheduling.task;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@Component
public class FixedRateTask {

    private static final Logger log =
        LoggerFactory.getLogger(FixedRateTask.class);

    private static final DateTimeFormatter FORMATTER =
        DateTimeFormatter.ofPattern("HH:mm:ss");

    @Scheduled(fixedRate = 5000)  // Run every 5 seconds
    public void reportCurrentTime() {
        String time = LocalDateTime.now().format(FORMATTER);
        log.info("Fixed Rate Task - Current time: {}", time);
    }
}
```

**Line-by-line explanation:**

- `@Component` -- The class must be a Spring bean for `@Scheduled` to work.
- `@Scheduled(fixedRate = 5000)` -- Run this method every 5000 milliseconds (5 seconds). The value is in milliseconds.
- The method must have `void` return type and no parameters.

**Output:**

```
10:30:00.001 INFO  FixedRateTask - Fixed Rate Task - Current time: 10:30:00
10:30:05.001 INFO  FixedRateTask - Fixed Rate Task - Current time: 10:30:05
10:30:10.002 INFO  FixedRateTask - Fixed Rate Task - Current time: 10:30:10
10:30:15.001 INFO  FixedRateTask - Fixed Rate Task - Current time: 10:30:15
```

### How fixedRate Works

```
+--------------------------------------------------+
|  fixedRate = 5000 (5 seconds)                     |
+--------------------------------------------------+
|                                                   |
|  Time: 0s    5s    10s   15s   20s                |
|        |     |     |     |     |                  |
|        v     v     v     v     v                  |
|       [T1]  [T2]  [T3]  [T4]  [T5]               |
|                                                   |
|  Tasks start every 5 seconds regardless of        |
|  how long each task takes.                        |
|                                                   |
|  If a task takes longer than the interval:        |
|  Time: 0s    5s    10s   15s                      |
|        |     |     |     |                        |
|        v     v     v     v                        |
|       [T1-----7s]                                 |
|              [T2--]                               |
|                    [T3--]                         |
|                                                   |
|  T2 starts as soon as T1 finishes (not at 5s      |
|  because T1 was still running at 5s).             |
+--------------------------------------------------+
```

> **Important**: If a task takes longer than the fixedRate interval, the next execution waits until the current one finishes. Tasks do not overlap by default.

### Using Readable Time Units

Instead of counting milliseconds, you can use time unit strings:

```java
// These are all equivalent
@Scheduled(fixedRate = 60000)             // 60,000 milliseconds
@Scheduled(fixedRateString = "60000")     // Same, but as a string
@Scheduled(fixedRateString = "PT1M")      // ISO-8601 duration: 1 minute
@Scheduled(fixedRateString = "PT30S")     // 30 seconds
@Scheduled(fixedRateString = "PT1H")      // 1 hour
```

You can also read the value from application.properties:

```properties
# application.properties
scheduling.fixed-rate=5000
```

```java
@Scheduled(fixedRateString = "${scheduling.fixed-rate}")
public void configurableTask() {
    log.info("Running with configurable rate");
}
```

---

## 23.3 Fixed Delay Scheduling

`fixedDelay` waits for N milliseconds **after the previous execution finishes** before starting the next one:

```java
@Component
public class FixedDelayTask {

    private static final Logger log =
        LoggerFactory.getLogger(FixedDelayTask.class);

    @Scheduled(fixedDelay = 5000)  // Wait 5s after completion
    public void processQueue() {
        log.info("Processing message queue...");

        // Simulate work that takes 3 seconds
        try {
            Thread.sleep(3000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        log.info("Queue processing complete");
    }
}
```

### How fixedDelay Works

```
+--------------------------------------------------+
|  fixedDelay = 5000 (5 seconds)                    |
+--------------------------------------------------+
|                                                   |
|  Time: 0s       3s   8s      11s  16s             |
|        |        |    |       |    |               |
|        v        v    v       v    v               |
|       [T1--3s--]    [T2--3s]    [T3--3s]          |
|                 |        |           |            |
|                 5s delay 5s delay    5s delay     |
|                                                   |
|  Each task starts 5 seconds after the             |
|  previous task FINISHES.                          |
|                                                   |
|  Total cycle: 3s (work) + 5s (delay) = 8s        |
+--------------------------------------------------+
```

### fixedRate vs fixedDelay

| Feature | fixedRate | fixedDelay |
|---------|-----------|------------|
| Timer starts from | Start of previous execution | End of previous execution |
| Use when | You need consistent intervals | You need a gap between executions |
| Example | "Check every 30 seconds" | "Wait 10 seconds after finishing" |
| Risk | Tasks can pile up if slow | Interval varies with task duration |

**When to use which:**

- Use `fixedRate` when you want the task to run at regular intervals (like checking for new emails every 30 seconds). The timing is predictable.
- Use `fixedDelay` when you want to ensure a gap between executions (like processing a queue where you need to finish one batch before starting the next).

---

## 23.4 Initial Delay

Sometimes you do not want a scheduled task to run immediately when the application starts. Use `initialDelay` to wait before the first execution:

```java
@Scheduled(fixedRate = 10000, initialDelay = 30000)
public void delayedTask() {
    log.info("This task waits 30 seconds before the first run, " +
        "then runs every 10 seconds");
}
```

```
+--------------------------------------------------+
|  fixedRate = 10s, initialDelay = 30s              |
+--------------------------------------------------+
|                                                   |
|  App starts                                       |
|  |                                               |
|  |--- 30 seconds (initial delay) ---|            |
|                                     |            |
|                                    [T1]          |
|                                     |--10s--|    |
|                                             [T2] |
|                                              |   |
+--------------------------------------------------+
```

This is useful when:
- You want the application to fully start up before running tasks.
- You need to wait for external services to become available.
- You want to stagger multiple tasks so they do not all start at the same time.

---

## 23.5 Cron Expressions

For more complex schedules (like "every weekday at 9 AM" or "the first day of every month"), use cron expressions:

```java
@Scheduled(cron = "0 0 9 * * MON-FRI")
public void weekdayMorningReport() {
    log.info("Generating weekday morning report");
}
```

### Cron Expression Format

A Spring cron expression has **six fields**:

```
 ┌───────────── second (0-59)
 │ ┌───────────── minute (0-59)
 │ │ ┌───────────── hour (0-23)
 │ │ │ ┌───────────── day of month (1-31)
 │ │ │ │ ┌───────────── month (1-12 or JAN-DEC)
 │ │ │ │ │ ┌───────────── day of week (0-7 or MON-SUN, 0 and 7 = Sunday)
 │ │ │ │ │ │
 * * * * * *
```

> **Note**: Standard Unix cron has five fields (no seconds). Spring cron has six fields because it adds seconds. This is a common source of confusion.

### Special Characters

| Character | Meaning | Example |
|-----------|---------|---------|
| `*` | Every value | `*` in hour = every hour |
| `,` | List of values | `1,15` in day = 1st and 15th |
| `-` | Range | `MON-FRI` = Monday to Friday |
| `/` | Increment | `0/15` in minutes = every 15 minutes |
| `?` | No specific value | Used for day-of-month or day-of-week |

### Common Cron Examples

```java
// Every day at midnight
@Scheduled(cron = "0 0 0 * * *")

// Every day at 9:00 AM
@Scheduled(cron = "0 0 9 * * *")

// Every weekday (Mon-Fri) at 8:30 AM
@Scheduled(cron = "0 30 8 * * MON-FRI")

// Every 15 minutes
@Scheduled(cron = "0 0/15 * * * *")

// Every hour on the hour
@Scheduled(cron = "0 0 * * * *")

// First day of every month at midnight
@Scheduled(cron = "0 0 0 1 * *")

// Every Sunday at 2:00 AM
@Scheduled(cron = "0 0 2 * * SUN")

// Every 30 seconds
@Scheduled(cron = "0/30 * * * * *")

// At 10:15 AM on the 15th of every month
@Scheduled(cron = "0 15 10 15 * *")
```

### Cron Expression Cheat Sheet

```
+-----------------------------------------------------+
|           CRON EXPRESSION CHEAT SHEET                |
+-----------------------------------------------------+
|                                                      |
|  "0 0 9 * * *"                                       |
|   | | | | | |                                        |
|   | | | | | +-- Day of week: * (every day)            |
|   | | | | +---- Month: * (every month)                |
|   | | | +------ Day of month: * (every day)           |
|   | | +-------- Hour: 9 (9 AM)                        |
|   | +---------- Minute: 0 (on the hour)               |
|   +------------ Second: 0 (on the second)             |
|                                                      |
|  Translation: "At 9:00:00 AM every day"              |
|                                                      |
|  "0 30 8 * * MON-FRI"                                |
|   | |  | | |    |                                    |
|   | |  | | |    +-- Mon through Fri only              |
|   | |  | | +------- Every month                       |
|   | |  | +--------- Every day of month                |
|   | |  +----------- Hour: 8                           |
|   | +-------------- Minute: 30                         |
|   +---------------- Second: 0                         |
|                                                      |
|  Translation: "At 8:30:00 AM, Mon through Fri"       |
|                                                      |
|  "0 0/15 * * * *"                                    |
|   | |    | | | |                                     |
|   | |    | | | +-- Every day of week                  |
|   | |    | | +---- Every month                        |
|   | |    | +------ Every day                          |
|   | |    +-------- Every hour                         |
|   | +------------- Every 15 min (0, 15, 30, 45)      |
|   +--------------- Second: 0                         |
|                                                      |
|  Translation: "Every 15 minutes"                     |
|                                                      |
+-----------------------------------------------------+
```

### Using Cron from Properties

```properties
# application.properties
scheduling.cron.cleanup=0 0 2 * * *
scheduling.cron.report=0 0 9 * * MON-FRI
```

```java
@Scheduled(cron = "${scheduling.cron.cleanup}")
public void cleanup() {
    log.info("Running cleanup task");
}

@Scheduled(cron = "${scheduling.cron.report}")
public void generateReport() {
    log.info("Generating daily report");
}
```

This is very useful because you can change schedules without modifying code.

---

## 23.6 A Complete Scheduled Task Example

Let us build a practical example: a task that cleans up expired temporary files:

```java
// src/main/java/com/example/scheduling/task/CleanupTask.java
package com.example.scheduling.task;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.concurrent.atomic.AtomicInteger;

@Component
public class CleanupTask {

    private static final Logger log =
        LoggerFactory.getLogger(CleanupTask.class);

    @Value("${file.upload-dir:uploads}")
    private String uploadDir;

    @Value("${cleanup.max-age-hours:24}")
    private int maxAgeHours;

    // Run every day at 2:00 AM
    @Scheduled(cron = "0 0 2 * * *")
    public void cleanupOldFiles() {
        log.info("Starting file cleanup task. " +
            "Removing files older than {} hours", maxAgeHours);

        Path uploadPath = Paths.get(uploadDir);

        if (!Files.exists(uploadPath)) {
            log.warn("Upload directory does not exist: {}", uploadPath);
            return;
        }

        Instant cutoff = Instant.now()
            .minus(maxAgeHours, ChronoUnit.HOURS);

        AtomicInteger deletedCount = new AtomicInteger(0);
        AtomicInteger errorCount = new AtomicInteger(0);

        try {
            Files.list(uploadPath).forEach(file -> {
                try {
                    Instant lastModified = Files
                        .getLastModifiedTime(file).toInstant();

                    if (lastModified.isBefore(cutoff)) {
                        Files.delete(file);
                        deletedCount.incrementAndGet();
                        log.debug("Deleted old file: {}", file);
                    }
                } catch (IOException e) {
                    errorCount.incrementAndGet();
                    log.error("Failed to process file: {}", file, e);
                }
            });
        } catch (IOException e) {
            log.error("Failed to list files in {}", uploadPath, e);
        }

        log.info("Cleanup complete. Deleted: {}, Errors: {}",
            deletedCount.get(), errorCount.get());
    }
}
```

**Line-by-line explanation:**

- `@Value("${cleanup.max-age-hours:24}")` -- Reads the max age from properties, with a default of 24 hours.
- `Instant.now().minus(maxAgeHours, ChronoUnit.HOURS)` -- Calculates the cutoff time. Files older than this are deleted.
- `AtomicInteger` -- Thread-safe counter. We use it inside a lambda where regular variables would need to be effectively final.
- `Files.getLastModifiedTime(file).toInstant()` -- Gets the last modification time of each file.
- The method logs a summary at the end (how many files deleted, how many errors).

**Output at 2:00 AM:**

```
02:00:00.001 INFO  CleanupTask - Starting file cleanup task. Removing files older than 24 hours
02:00:00.015 DEBUG CleanupTask - Deleted old file: uploads/a1b2c3d4_old.jpg
02:00:00.016 DEBUG CleanupTask - Deleted old file: uploads/e5f6a7b8_expired.pdf
02:00:00.020 INFO  CleanupTask - Cleanup complete. Deleted: 2, Errors: 0
```

---

## 23.7 Error Handling in Scheduled Tasks

By default, if a scheduled task throws an exception, the exception is logged but the task continues to run on schedule. However, you should handle errors explicitly:

```java
// src/main/java/com/example/scheduling/task/ResilientTask.java
package com.example.scheduling.task;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class ResilientTask {

    private static final Logger log =
        LoggerFactory.getLogger(ResilientTask.class);

    private int consecutiveFailures = 0;
    private static final int MAX_FAILURES = 5;

    @Scheduled(fixedRate = 60000)  // Every minute
    public void processWithErrorHandling() {
        try {
            log.info("Starting scheduled processing");

            // Your business logic here
            doWork();

            // Reset failure counter on success
            consecutiveFailures = 0;
            log.info("Scheduled processing completed successfully");

        } catch (Exception e) {
            consecutiveFailures++;
            log.error("Scheduled task failed. " +
                "Consecutive failures: {}/{}",
                consecutiveFailures, MAX_FAILURES, e);

            if (consecutiveFailures >= MAX_FAILURES) {
                log.error("Task has failed {} consecutive times. " +
                    "Manual intervention may be needed.",
                    consecutiveFailures);
                // Optionally: send alert, disable task, etc.
            }
        }
    }

    private void doWork() {
        // Simulate work that might fail
        if (Math.random() < 0.3) {
            throw new RuntimeException("Simulated failure");
        }
    }
}
```

### Custom Error Handler for All Scheduled Tasks

You can configure a global error handler:

```java
// src/main/java/com/example/scheduling/config/SchedulingConfig.java
package com.example.scheduling.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.scheduling.annotation.SchedulingConfigurer;
import org.springframework.scheduling.concurrent.ThreadPoolTaskScheduler;
import org.springframework.scheduling.config.ScheduledTaskRegistrar;

@Configuration
@EnableScheduling
public class SchedulingConfig implements SchedulingConfigurer {

    private static final Logger log =
        LoggerFactory.getLogger(SchedulingConfig.class);

    @Override
    public void configureTasks(ScheduledTaskRegistrar taskRegistrar) {
        ThreadPoolTaskScheduler scheduler = new ThreadPoolTaskScheduler();
        scheduler.setPoolSize(5);  // Allow 5 concurrent tasks
        scheduler.setThreadNamePrefix("scheduled-");
        scheduler.setErrorHandler(throwable -> {
            log.error("Scheduled task error: {}",
                throwable.getMessage(), throwable);
        });
        scheduler.initialize();
        taskRegistrar.setTaskScheduler(scheduler);
    }
}
```

**Line-by-line explanation:**

- `ThreadPoolTaskScheduler` -- Replaces the default single-threaded scheduler with a thread pool.
- `setPoolSize(5)` -- Allows up to 5 scheduled tasks to run simultaneously. The default is 1, which means all tasks share a single thread.
- `setThreadNamePrefix("scheduled-")` -- Makes it easy to identify scheduled task threads in logs.
- `setErrorHandler(...)` -- A global error handler that catches any unhandled exception from any scheduled task.

> **Why is the pool size important?** With the default pool size of 1, if one scheduled task blocks (takes too long or hangs), all other scheduled tasks are delayed. Setting the pool size to a higher value allows multiple tasks to run in parallel.

```
+----------------------------------------------------+
|  DEFAULT: Pool Size = 1                             |
+----------------------------------------------------+
|                                                     |
|  Task A (runs every 5s): [AAAA]   [AAAA]   [AAAA]  |
|  Task B (runs every 5s):       [BB]   [BB]   [BB]  |
|                                                     |
|  Task B has to wait for Task A to finish!           |
|                                                     |
+----------------------------------------------------+
|  CONFIGURED: Pool Size = 5                          |
+----------------------------------------------------+
|                                                     |
|  Task A (runs every 5s): [AAAA]   [AAAA]   [AAAA]  |
|  Task B (runs every 5s): [BB]     [BB]     [BB]    |
|                                                     |
|  Both tasks run independently!                      |
+----------------------------------------------------+
```

---

## 23.8 Conditional Scheduling

Sometimes you want a scheduled task to run only in certain environments (like production but not development):

```java
@Component
@Profile("prod")  // Only runs in the prod profile
public class ProductionOnlyTask {

    private static final Logger log =
        LoggerFactory.getLogger(ProductionOnlyTask.class);

    @Scheduled(cron = "0 0 0 * * *")
    public void nightlyBackup() {
        log.info("Running nightly backup (production only)");
    }
}
```

You can also use `@ConditionalOnProperty`:

```java
@Component
@ConditionalOnProperty(
    name = "scheduling.cleanup.enabled",
    havingValue = "true",
    matchIfMissing = false
)
public class ConditionalCleanupTask {

    @Scheduled(fixedRate = 60000)
    public void cleanup() {
        // Only runs if scheduling.cleanup.enabled=true in properties
    }
}
```

```properties
# Enable or disable the cleanup task
scheduling.cleanup.enabled=true
```

---

## 23.9 Scheduling Summary Table

| Attribute | Behavior | Example |
|-----------|----------|---------|
| `fixedRate` | Run every N ms from start | `@Scheduled(fixedRate = 5000)` |
| `fixedDelay` | Wait N ms after completion | `@Scheduled(fixedDelay = 5000)` |
| `cron` | Run on a schedule | `@Scheduled(cron = "0 0 9 * * *")` |
| `initialDelay` | Wait before first run | `@Scheduled(fixedRate = 5000, initialDelay = 10000)` |
| `fixedRateString` | Rate from property | `@Scheduled(fixedRateString = "${rate}")` |
| `fixedDelayString` | Delay from property | `@Scheduled(fixedDelayString = "${delay}")` |

---

## Common Mistakes

1. **Forgetting @EnableScheduling.** Without this annotation, all @Scheduled methods are silently ignored. Nothing happens, and there is no error message.

2. **Forgetting @Component on the task class.** The class must be a Spring bean. If it is not in the Spring context, the scheduled method will never run.

3. **Using five-field cron expressions.** Spring cron expressions have six fields (including seconds). Unix cron has five fields. A five-field expression will cause an error.

4. **Not increasing the thread pool size.** The default scheduler uses a single thread. If you have multiple scheduled tasks, they will block each other. Configure a ThreadPoolTaskScheduler with an appropriate pool size.

5. **Ignoring exceptions in scheduled tasks.** If a scheduled method throws an uncaught exception, it will be logged but the task will continue running on schedule. Always wrap your logic in try-catch and log errors properly.

6. **Making scheduled methods return a value.** Scheduled methods must return void and take no parameters. If you add a return type or parameters, Spring will not recognize it as a scheduled method.

---

## Best Practices

1. **Externalize schedules in application.properties.** Use `fixedRateString = "${property.name}"` or `cron = "${cron.expression}"` so you can change schedules without redeploying.

2. **Log the start and end of every scheduled task.** Include how long the task took and whether it succeeded or failed. This makes troubleshooting much easier.

3. **Use a thread pool for multiple tasks.** Configure a `ThreadPoolTaskScheduler` with a pool size greater than 1 to prevent tasks from blocking each other.

4. **Handle errors gracefully.** Wrap scheduled task logic in try-catch. Track consecutive failures and alert if a task keeps failing.

5. **Use @Profile or @ConditionalOnProperty for environment-specific tasks.** Do not run production cleanup tasks in your development environment.

6. **Keep scheduled tasks lightweight.** If a task does heavy processing, make sure the interval is long enough for it to complete. Or use `fixedDelay` instead of `fixedRate`.

---

## Quick Summary

Spring Boot scheduling lets you run tasks automatically at fixed intervals or on specific schedules. Enable it with @EnableScheduling on your application class. Use @Scheduled(fixedRate) to run a task every N milliseconds from the start of the previous run. Use @Scheduled(fixedDelay) to wait N milliseconds after the previous run finishes. For complex schedules like "every weekday at 9 AM," use cron expressions with six fields: second, minute, hour, day-of-month, month, day-of-week. Configure a ThreadPoolTaskScheduler to allow multiple tasks to run in parallel. Always handle errors in scheduled tasks and externalize schedules in application properties so you can change them without redeploying.

---

## Key Points

- @EnableScheduling activates the scheduling system.
- @Scheduled methods must return void and have no parameters.
- fixedRate: interval between the START of executions.
- fixedDelay: interval between the END of one execution and the START of the next.
- Spring cron expressions have 6 fields (including seconds). Unix cron has 5.
- Use initialDelay to postpone the first execution after application startup.
- The default scheduler has a single thread. Use ThreadPoolTaskScheduler for multiple concurrent tasks.
- Externalize cron expressions and intervals in application.properties.
- Always handle exceptions in scheduled tasks with try-catch.
- Use @Profile to restrict tasks to specific environments.

---

## Practice Questions

1. What is the difference between `fixedRate = 5000` and `fixedDelay = 5000` when a task takes 3 seconds to complete?

2. How many fields does a Spring cron expression have, and what does each field represent?

3. What happens if you use @Scheduled on a method but forget to add @EnableScheduling to your application?

4. Why should you configure a ThreadPoolTaskScheduler with a pool size greater than 1?

5. Write a cron expression that runs at 3:30 PM every Monday and Wednesday.

---

## Exercises

### Exercise 1: Heartbeat Logger

Create a scheduled task that logs a "heartbeat" message every 10 seconds. Include the current timestamp and the application uptime (how long since the application started).

### Exercise 2: Database Cleanup Task

Create a scheduled task that runs at 3:00 AM every day to delete records from a "session" table where the "expires_at" column is in the past. Use JPA. Log how many expired sessions were removed.

### Exercise 3: Multiple Tasks with Thread Pool

Create three scheduled tasks with different intervals (5 seconds, 10 seconds, 30 seconds). Each task should simulate work by sleeping for 2 seconds. Configure a ThreadPoolTaskScheduler with a pool size of 3. Verify that all three tasks run concurrently by checking the thread names in the logs.

---

## What Is Next?

Your application can now run tasks automatically on any schedule. But some tasks, like looking up product data or computing reports, are slow because they hit the database every single time. What if you could remember the result and return it instantly the next time someone asks? That is caching. In Chapter 24, you will learn how to use Spring Boot's caching annotations to dramatically speed up your application by storing frequently accessed data in memory.
