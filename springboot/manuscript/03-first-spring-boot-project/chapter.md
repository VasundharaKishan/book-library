# Chapter 3: Your First Spring Boot Project

## What You Will Learn

- How to use Spring Initializr to generate a project
- What each option on Spring Initializr means
- How to add the Spring Web dependency
- How to import the project into your IDE
- What the `@SpringBootApplication` annotation does
- How to run your application and see it in a browser
- How to create a `/hello` endpoint that returns a message
- How to fix the most common startup errors

## Why This Chapter Matters

You have your tools ready. Now it is time to build something real.

In this chapter, you will create a Spring Boot application from scratch. By the end, you will have a web server running on your computer. You will type a URL in your browser and see a response. That response comes from code you wrote.

This is your first taste of Spring Boot. It takes less than 10 minutes.

---

## 3.1 What Is Spring Initializr?

Spring Initializr is a website that generates a starter project for you. Think of it as a pizza ordering form. You pick your crust (Java version), your size (packaging), your toppings (dependencies), and it gives you a ready-made project to download.

You can find it at [https://start.spring.io](https://start.spring.io).

```
+---------------------------------------------------+
|              Spring Initializr                     |
|              (start.spring.io)                     |
+---------------------------------------------------+
|                                                    |
|   You choose:                                      |
|     - Project type (Maven or Gradle)               |
|     - Language (Java, Kotlin, Groovy)              |
|     - Spring Boot version                          |
|     - Project metadata (name, package)             |
|     - Dependencies (the libraries you need)        |
|                                                    |
|   You get:                                         |
|     - A .zip file with a complete project          |
|     - Ready to import into your IDE                |
|     - Ready to run                                 |
|                                                    |
+---------------------------------------------------+
```

---

## 3.2 Creating the Project Step by Step

Open your browser and go to [https://start.spring.io](https://start.spring.io).

You will see a form with several options. Let us go through each one.

### Option 1: Project

Choose **Maven**. Maven is the build tool we installed in the previous chapter.

> **Gradle** is another build tool. It is also popular. But Maven is easier for beginners and more common in tutorials. We will use Maven throughout this book.

### Option 2: Language

Choose **Java**. This book uses Java.

### Option 3: Spring Boot Version

Choose the latest **stable** version. At the time of writing, that is **3.4.x**. Do not pick versions marked with "SNAPSHOT" or "M1". Those are pre-release versions. They may have bugs.

```
+-------------------------------------------+
|     Picking the Right Version             |
+-------------------------------------------+
|                                           |
|   3.4.4          <-- Pick this (stable)   |
|   3.4.5-SNAPSHOT <-- Skip (pre-release)   |
|   3.5.0-M1       <-- Skip (milestone)    |
|   3.5.0-SNAPSHOT <-- Skip (pre-release)   |
|                                           |
+-------------------------------------------+
```

> **SNAPSHOT** means the version is still being built. It changes every day. **M1** means "Milestone 1". It is a preview of an upcoming release. Both are unstable.

### Option 4: Project Metadata

Fill in these fields:

| Field        | Value                      | What It Means                              |
|-------------|----------------------------|--------------------------------------------|
| Group       | `com.example`              | Your organization's domain, reversed       |
| Artifact    | `hello-spring-boot`        | The name of your project                   |
| Name        | `hello-spring-boot`        | Same as artifact (auto-filled)             |
| Description | `My first Spring Boot app` | A short description                        |
| Package     | `com.example.hellospringboot` | The base Java package for your code     |
| Packaging   | `Jar`                      | How Maven packages the app                 |
| Java        | `17`                       | The Java version                           |

> **Group** is usually your company's domain name in reverse. For example, if your company is `acme.com`, the group is `com.acme`. For personal projects, `com.example` is fine.

> **Artifact** is the name of your project. It becomes the name of the `.jar` file Maven creates.

> **Package** is the Java package where your code lives. Java uses packages to organize code, like folders organize files.

### Option 5: Dependencies

Click the "ADD DEPENDENCIES" button. Search for **Spring Web**. Click it to add it.

**Spring Web** gives you everything you need to build a web application:

- An embedded web server (Tomcat)
- Tools to handle HTTP requests (GET, POST, etc.)
- Tools to return responses (HTML, JSON, plain text)

```
+-------------------------------------------+
|     What Spring Web Gives You             |
+-------------------------------------------+
|                                           |
|   Embedded Tomcat server                  |
|     (no need to install a server)         |
|                                           |
|   @RestController annotation              |
|     (marks a class as a web controller)   |
|                                           |
|   @GetMapping annotation                  |
|     (maps a URL to a method)              |
|                                           |
|   JSON support (Jackson library)          |
|     (converts Java objects to JSON)       |
|                                           |
+-------------------------------------------+
```

### Generate and Download

Click the **GENERATE** button. A `.zip` file will download. Extract it to a folder you will remember, such as `~/projects/hello-spring-boot`.

---

## 3.3 Importing the Project into Your IDE

### IntelliJ IDEA

1. Open IntelliJ IDEA
2. Click **Open** (not "New Project")
3. Navigate to the extracted folder
4. Select the `pom.xml` file
5. IntelliJ will ask: "Open as Project?" Click **Yes**
6. Wait for IntelliJ to download dependencies (you will see a progress bar at the bottom)

### VS Code

1. Open VS Code
2. Click **File > Open Folder**
3. Navigate to the extracted folder and open it
4. VS Code will detect the Java project and start downloading dependencies
5. Wait for the Java extension to finish loading (check the bottom status bar)

> **Tip:** The first time you open the project, your IDE will download many files. This is normal. Maven is fetching all the libraries Spring Boot needs. It can take a few minutes on a slow connection.

---

## 3.4 Understanding @SpringBootApplication

Open the main class. It is in:

```
src/main/java/com/example/hellospringboot/HelloSpringBootApplication.java
```

Here is what the file looks like:

```java
package com.example.hellospringboot;              // 1

import org.springframework.boot.SpringApplication; // 2
import org.springframework.boot.autoconfigure.SpringBootApplication; // 3

@SpringBootApplication                             // 4
public class HelloSpringBootApplication {          // 5

    public static void main(String[] args) {       // 6
        SpringApplication.run(                     // 7
            HelloSpringBootApplication.class,      // 8
            args                                   // 9
        );
    }
}
```

**Line-by-line explanation:**

- **Line 1:** `package com.example.hellospringboot;` -- This declares the package. Packages are like folders for your Java classes. Every class must belong to a package.

- **Lines 2-3:** `import ...` -- These lines import classes from the Spring Boot library. Java needs to know where each class comes from.

- **Line 4:** `@SpringBootApplication` -- This is an **annotation**. An annotation is a label you attach to code. It tells Spring Boot: "This class is the starting point of the application." We will explore what this annotation does internally in Chapter 5.

- **Line 5:** `public class HelloSpringBootApplication` -- This is the main class of your application. The name matches the file name.

- **Line 6:** `public static void main(String[] args)` -- This is the entry point. When you run the application, Java looks for a `main` method and starts there. Every Java application has one.

- **Lines 7-9:** `SpringApplication.run(...)` -- This line starts Spring Boot. It does a lot behind the scenes: it starts the web server, scans for components, loads configuration, and more. Think of it as turning the key in the ignition of a car.

```
+------------------------------------------------------+
|     What SpringApplication.run() Does                |
+------------------------------------------------------+
|                                                       |
|   1. Creates the Spring application context           |
|      (the container that holds all your beans)        |
|                                                       |
|   2. Scans for annotated classes                      |
|      (@Controller, @Service, @Repository, etc.)       |
|                                                       |
|   3. Configures everything automatically              |
|      (database connections, web server, etc.)         |
|                                                       |
|   4. Starts the embedded web server (Tomcat)          |
|      on port 8080 by default                          |
|                                                       |
+------------------------------------------------------+
```

---

## 3.5 Running the Application

### From the IDE

**IntelliJ IDEA:**
- Click the green play button next to the `main` method
- Or right-click the file and choose "Run"

**VS Code:**
- Click the "Run" link that appears above the `main` method
- Or open the Command Palette (Ctrl+Shift+P) and type "Spring Boot: Run"

### From the Terminal

Navigate to your project folder and run:

```bash
./mvnw spring-boot:run
```

On Windows:

```bash
mvnw.cmd spring-boot:run
```

### What You Should See

The console will show many lines of output. Look for these important lines:

```
  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/

 :: Spring Boot ::                (v3.4.4)

2024-01-15T10:30:00.123  INFO --- Starting HelloSpringBootApplication
2024-01-15T10:30:01.456  INFO --- Tomcat initialized with port 8080 (http)
2024-01-15T10:30:02.789  INFO --- Started HelloSpringBootApplication in 2.5 seconds
```

The banner (the Spring logo made of text) tells you Spring Boot is running. The last line says "Started" with a time. Your application is live.

### Opening It in the Browser

Open your web browser. Type this URL in the address bar:

```
http://localhost:8080
```

**localhost** means "this computer." **8080** is the port number. Together, they mean: "Connect to the web server running on this computer, on port 8080."

You will see an error page that says "Whitelabel Error Page." This is normal. We have not created any web pages yet. The error page means the server is running. It just has nothing to show.

```
+---------------------------------------------------+
|              What Is localhost?                    |
+---------------------------------------------------+
|                                                    |
|   Your computer has an address: 127.0.0.1          |
|   "localhost" is a shortcut for that address.      |
|                                                    |
|   When you type localhost:8080, your browser       |
|   talks to the web server running on your own      |
|   computer, on port 8080.                          |
|                                                    |
|   Browser ---request---> localhost:8080             |
|   Browser <--response--- Tomcat (Spring Boot)      |
|                                                    |
+---------------------------------------------------+
```

---

## 3.6 Creating Your First Endpoint: /hello

Now let us make the application do something useful. We will create an endpoint that responds with "Hello, Spring Boot!" when you visit `/hello` in your browser.

Create a new file called `HelloController.java` in the same package as the main class:

```
src/main/java/com/example/hellospringboot/HelloController.java
```

Type this code:

```java
package com.example.hellospringboot;                    // 1

import org.springframework.web.bind.annotation.GetMapping;     // 2
import org.springframework.web.bind.annotation.RestController;  // 3

@RestController                                         // 4
public class HelloController {                          // 5

    @GetMapping("/hello")                               // 6
    public String sayHello() {                          // 7
        return "Hello, Spring Boot!";                   // 8
    }
}
```

**Line-by-line explanation:**

- **Line 1:** `package com.example.hellospringboot;` -- Same package as the main class. This is important. Spring Boot scans this package for components.

- **Lines 2-3:** Import the annotations we need.

- **Line 4:** `@RestController` -- This annotation tells Spring Boot: "This class handles web requests." The word "Rest" refers to REST, a style of building web APIs. The word "Controller" means this class controls what happens when someone visits a URL.

- **Line 5:** The class declaration. The name `HelloController` is just a convention. You can name it anything.

- **Line 6:** `@GetMapping("/hello")` -- This annotation tells Spring Boot: "When someone sends a GET request to `/hello`, run this method." A GET request is what your browser sends when you type a URL and press Enter.

- **Line 7:** `public String sayHello()` -- This method returns a `String`. Whatever string it returns will be sent back to the browser.

- **Line 8:** `return "Hello, Spring Boot!";` -- The response. The browser will display this text.

```
+---------------------------------------------------+
|           How the Request Flows                    |
+---------------------------------------------------+
|                                                    |
|   Browser types: http://localhost:8080/hello        |
|        |                                           |
|        v                                           |
|   Browser sends GET request to /hello              |
|        |                                           |
|        v                                           |
|   Tomcat receives the request                      |
|        |                                           |
|        v                                           |
|   Spring finds @GetMapping("/hello")               |
|        |                                           |
|        v                                           |
|   Spring calls sayHello() method                   |
|        |                                           |
|        v                                           |
|   Method returns "Hello, Spring Boot!"             |
|        |                                           |
|        v                                           |
|   Tomcat sends the string back to the browser      |
|        |                                           |
|        v                                           |
|   Browser displays: Hello, Spring Boot!            |
|                                                    |
+---------------------------------------------------+
```

### Run and Test

1. Stop the application if it is still running (press Ctrl+C in the terminal, or click the stop button in the IDE).
2. Start it again (so it picks up the new class).
3. Open your browser and go to:

```
http://localhost:8080/hello
```

**Expected output in the browser:**

```
Hello, Spring Boot!
```

Congratulations! You just built a web endpoint. Your browser sent a request. Spring Boot handled it. Your method returned a response. The browser displayed it.

---

## 3.7 Adding Another Endpoint

Let us add one more endpoint to practice. Add this method inside the `HelloController` class, after the `sayHello()` method:

```java
@GetMapping("/goodbye")                              // 1
public String sayGoodbye() {                         // 2
    return "Goodbye! Thanks for visiting.";          // 3
}
```

The complete `HelloController.java` now looks like this:

```java
package com.example.hellospringboot;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {

    @GetMapping("/hello")
    public String sayHello() {
        return "Hello, Spring Boot!";
    }

    @GetMapping("/goodbye")
    public String sayGoodbye() {
        return "Goodbye! Thanks for visiting.";
    }
}
```

Restart the application. Visit:

- `http://localhost:8080/hello` -- shows "Hello, Spring Boot!"
- `http://localhost:8080/goodbye` -- shows "Goodbye! Thanks for visiting."

Each `@GetMapping` maps a URL path to a method. You can add as many endpoints as you want.

---

## 3.8 Common Startup Errors

### Error 1: Port 8080 Already in Use

```
Web server failed to start. Port 8080 was already in use.
```

**Cause:** Another application is already using port 8080. This could be another Spring Boot app you forgot to stop, or a different program.

**Fix (Option A):** Find and stop the other application.

On Mac/Linux:

```bash
lsof -i :8080
```

This shows the process using port 8080. Note the PID (process ID) and kill it:

```bash
kill -9 <PID>
```

On Windows:

```cmd
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

**Fix (Option B):** Change the port. Open `src/main/resources/application.properties` and add:

```properties
server.port=8081
```

Now the app runs on port 8081. Visit `http://localhost:8081/hello` instead.

### Error 2: No Compiler Is Provided

```
No compiler is provided in this environment.
Perhaps you are running on a JRE rather than a JDK?
```

**Cause:** Maven found a JRE, not a JDK. The JRE cannot compile code.

**Fix:** Install the JDK and set `JAVA_HOME` to point to the JDK folder. See Chapter 2.

### Error 3: Class Not Found or Bean Not Created

Your `/hello` endpoint returns a 404 (not found) error.

**Cause:** The controller class is in the wrong package. Spring Boot scans the package of the main class and all sub-packages. If your controller is in a different package tree, Spring Boot will not find it.

```
CORRECT:
  com.example.hellospringboot
    ├── HelloSpringBootApplication.java   (main class)
    └── HelloController.java             (same package - found!)

  com.example.hellospringboot.controller
    └── HelloController.java             (sub-package - also found!)

WRONG:
  com.example.hellospringboot
    └── HelloSpringBootApplication.java   (main class)
  com.example.controller
    └── HelloController.java             (different package tree - NOT found!)
```

**Fix:** Move the controller class into the same package as the main class, or into a sub-package.

### Error 4: Application Starts but Stops Immediately

```
Started HelloSpringBootApplication in 1.2 seconds
```

Then the application exits.

**Cause:** You did not add the Spring Web dependency. Without it, there is no web server. The application starts, finds nothing to do, and stops.

**Fix:** Add Spring Web to your `pom.xml`:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

Or regenerate the project from Spring Initializr with the Spring Web dependency selected.

### Error 5: Whitelabel Error Page (404) at localhost:8080

**Cause:** The server is running, but there is no endpoint mapped to `/`. This is normal if you only created a `/hello` endpoint.

**Fix:** Either visit `/hello` instead, or add a mapping for `/`:

```java
@GetMapping("/")
public String home() {
    return "Welcome to my Spring Boot app!";
}
```

---

## Common Mistakes

1. **Forgetting to add Spring Web.** Without it, the application has no web server. It starts and stops immediately.
2. **Putting the controller in the wrong package.** The controller must be in the same package as `@SpringBootApplication`, or in a sub-package.
3. **Not restarting the application after code changes.** Spring Boot does not pick up changes automatically (unless you add DevTools). Stop and restart.
4. **Using a SNAPSHOT version of Spring Boot.** Snapshots are unstable. Use the latest stable release.
5. **Typing `localhost:8080` without `http://`.** Some browsers handle this. Others do not. Always use the full URL: `http://localhost:8080`.

---

## Best Practices

1. **Start with Spring Initializr.** Never create a Spring Boot project from scratch. The Initializr generates the correct structure and configuration.
2. **Add only the dependencies you need.** Each dependency adds complexity. Start small. Add more later.
3. **Keep controllers in the same package tree as the main class.** This ensures Spring Boot can find them.
4. **Use `@RestController` for API endpoints.** It combines `@Controller` and `@ResponseBody`, which means methods return data directly (not view names).
5. **Test endpoints in the browser or with curl.** Verify each endpoint works before building the next one.

---

## Quick Summary

In this chapter, you:

1. Used **Spring Initializr** (start.spring.io) to generate a project with **Maven**, **Java 17**, and the **Spring Web** dependency.
2. Imported the project into your IDE.
3. Explored the main class and understood `@SpringBootApplication` and `SpringApplication.run()`.
4. Ran the application and accessed `http://localhost:8080`.
5. Created a `HelloController` with a `@GetMapping("/hello")` endpoint.
6. Saw "Hello, Spring Boot!" in your browser.

---

## Key Points

- **Spring Initializr** (start.spring.io) generates ready-to-run Spring Boot projects.
- The **Spring Web** dependency gives you an embedded Tomcat server and web annotations.
- `@SpringBootApplication` marks the main class. It is the entry point of the application.
- `SpringApplication.run()` starts the Spring Boot application, including the web server.
- `@RestController` marks a class as a web request handler.
- `@GetMapping("/path")` maps a URL path to a method.
- The default port is **8080**. Change it with `server.port` in `application.properties`.
- Controllers must be in the same package (or a sub-package) as the main class.

---

## Practice Questions

1. What is Spring Initializr and why should you use it instead of creating a project manually?

2. What does the `@RestController` annotation tell Spring Boot about a class?

3. You create a controller in the package `com.other.controllers`, but your main class is in `com.example.hellospringboot`. The endpoint returns a 404 error. Why?

4. You start your application but it stops immediately after printing "Started." What is the most likely cause?

5. What is the difference between `localhost` and a regular website URL? What does port `8080` mean?

---

## Exercises

### Exercise 1: Personalized Greeting

Add a new endpoint `/greet` that returns "Hello! Welcome to [your name]'s Spring Boot application!" Replace `[your name]` with your actual name.

**Expected result:** Visiting `http://localhost:8080/greet` shows your personalized greeting.

### Exercise 2: Multiple Endpoints

Create a new controller called `InfoController.java` with these endpoints:

- `/info/app` -- returns "Hello Spring Boot App v1.0"
- `/info/author` -- returns your name
- `/info/java` -- returns the string "Java 17"

Verify all three endpoints work in the browser.

### Exercise 3: Change the Port

Modify `application.properties` to run the application on port **9090** instead of 8080. Start the application and verify you can access your endpoints at `http://localhost:9090/hello`.

---

## What Is Next?

You have a running Spring Boot application. But what are all those files and folders that Spring Initializr created? In the next chapter, we will explore the project structure. You will learn what every file and folder does, and how Maven's `pom.xml` works.
