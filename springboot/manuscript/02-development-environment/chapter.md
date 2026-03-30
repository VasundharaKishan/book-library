# Chapter 2: Setting Up Your Development Environment

## What You Will Learn

- What Java 17 is and how to install it on your computer
- The difference between JDK and JRE
- How to pick and install an IDE (IntelliJ IDEA or VS Code)
- How to install Maven, the build tool for Java projects
- How to verify that everything is installed correctly
- How to fix the most common setup errors

## Why This Chapter Matters

Imagine you want to build a wooden table. Before you cut a single piece of wood, you need a workbench, a saw, a hammer, and a ruler. Without the right tools, you cannot build anything.

Software development works the same way. Before you write a single line of Spring Boot code, you need the right tools installed on your computer. This chapter walks you through every tool, step by step.

If you skip this chapter and jump to coding, you will hit confusing errors. Spend 30 minutes here now. Save hours of frustration later.

---

## 2.1 The Tools You Need

Here is the full list of tools. Do not worry. We will install each one together.

```
+------------------------------------------------------+
|            Your Development Toolbox                   |
+------------------------------------------------------+
|                                                       |
|   1. Java 17+ (JDK)  --  The language and compiler   |
|   2. IDE              --  The code editor             |
|   3. Maven            --  The build tool              |
|                                                       |
+------------------------------------------------------+
```

**Java 17+ (JDK)** is the programming language. Spring Boot 3.4 requires Java 17 or newer.

**IDE** stands for Integrated Development Environment. It is a smart text editor built for writing code. Think of it as Microsoft Word, but for programmers.

**Maven** is a build tool. It downloads libraries, compiles your code, and packages your application. Think of it as a kitchen assistant that fetches ingredients, mixes them, and serves the dish.

---

## 2.2 Understanding JDK vs JRE

Before you install Java, you need to understand two terms: JDK and JRE.

**JRE** stands for Java Runtime Environment. It can **run** Java programs, but it cannot **build** them. Think of a JRE as a DVD player. It plays movies, but it cannot record them.

**JDK** stands for Java Development Kit. It includes the JRE **plus** tools to compile and debug code. Think of a JDK as a movie studio. It can both record and play movies.

```
+-----------------------------------------------+
|                    JDK                         |
|                                                |
|   +---------------------------------------+   |
|   |               JRE                     |   |
|   |                                       |   |
|   |   Java Virtual Machine (JVM)          |   |
|   |   Core Libraries                      |   |
|   |   (runs your programs)                |   |
|   |                                       |   |
|   +---------------------------------------+   |
|                                                |
|   + javac  (compiler - turns code into        |
|             bytecode)                          |
|   + jdb    (debugger - finds bugs)            |
|   + jar    (packager - bundles your app)      |
|                                                |
+-----------------------------------------------+
```

**Key takeaway:** Always install the JDK, not just the JRE. You are a developer. You need the full toolkit.

---

## 2.3 Installing Java 17+

### Step 1: Check If Java Is Already Installed

Open a terminal (Mac/Linux) or Command Prompt (Windows). Type this command:

```bash
java -version
```

**If Java is installed**, you will see output like this:

```
openjdk version "17.0.10" 2024-01-16
OpenJDK Runtime Environment (build 17.0.10+7)
OpenJDK 64-Bit Server VM (build 17.0.10+7, mixed mode)
```

The first number matters. It must be **17 or higher**. If you see `17`, `21`, or `22`, you are good. If you see `11`, `8`, or `1.8`, you need to upgrade.

**If Java is not installed**, you will see an error:

```
'java' is not recognized as an internal or external command
```

or

```
-bash: java: command not found
```

This means Java is not on your computer yet. Follow the next step.

### Step 2: Download and Install the JDK

There are several JDK distributions. They all contain the same core Java. Think of them like different brands of bottled water. The water is the same. The label is different.

We recommend **Eclipse Temurin** (by Adoptium). It is free, open source, and well-maintained.

1. Go to [https://adoptium.net](https://adoptium.net)
2. Select **Java 17 (LTS)** or **Java 21 (LTS)**
3. Choose your operating system (Windows, Mac, or Linux)
4. Download the installer
5. Run the installer. Accept the defaults.

> **LTS** stands for Long-Term Support. These versions receive security updates for many years. Always pick an LTS version for learning.

### Step 3: Verify the Installation

Close your terminal and open a new one. This is important. The old terminal does not know about the new installation.

```bash
java -version
```

Expected output:

```
openjdk version "17.0.10" 2024-01-16
OpenJDK Runtime Environment Temurin-17.0.10+7 (build 17.0.10+7)
OpenJDK 64-Bit Server VM Temurin-17.0.10+7 (build 17.0.10+7, mixed mode)
```

Also check the compiler:

```bash
javac -version
```

Expected output:

```
javac 17.0.10
```

If `java` works but `javac` does not, you installed the JRE instead of the JDK. Go back and install the JDK.

### Step 4: Check the JAVA_HOME Variable

Many tools need a variable called `JAVA_HOME`. This variable tells other programs where Java lives on your computer.

**On Mac/Linux:**

```bash
echo $JAVA_HOME
```

**On Windows (Command Prompt):**

```cmd
echo %JAVA_HOME%
```

You should see a path like:

```
/usr/lib/jvm/temurin-17-jdk       (Linux)
/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home  (Mac)
C:\Program Files\Eclipse Adoptium\jdk-17.0.10.7-hotspot        (Windows)
```

If it is empty, you need to set it. Here is how:

**Mac/Linux (add to ~/.bashrc or ~/.zshrc):**

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
export PATH=$JAVA_HOME/bin:$PATH
```

Then reload:

```bash
source ~/.zshrc
```

**Windows:**

1. Open System Properties > Environment Variables
2. Click "New" under System Variables
3. Variable name: `JAVA_HOME`
4. Variable value: the path to your JDK folder (e.g., `C:\Program Files\Eclipse Adoptium\jdk-17.0.10.7-hotspot`)
5. Click OK
6. Edit the `Path` variable and add `%JAVA_HOME%\bin`

---

## 2.4 Choosing and Installing an IDE

You can write Java in Notepad. But that is like eating soup with a fork. It works, but it is painful.

An IDE gives you:

- **Syntax highlighting** -- colors different parts of your code so it is easy to read
- **Auto-complete** -- suggests code as you type
- **Error detection** -- underlines mistakes before you even run the code
- **Debugging** -- lets you pause your program and inspect its state
- **Built-in terminal** -- run commands without leaving the editor

### Option A: IntelliJ IDEA (Recommended)

IntelliJ IDEA is the most popular IDE for Java. The **Community Edition** is free and has everything you need for this book.

1. Go to [https://www.jetbrains.com/idea/download](https://www.jetbrains.com/idea/download)
2. Download the **Community Edition** (free)
3. Run the installer
4. Open IntelliJ IDEA
5. On the Welcome screen, click "New Project" to verify it detects your JDK

```
+------------------------------------------+
|         IntelliJ IDEA Editions           |
+------------------------------------------+
|                                          |
|  Community Edition (Free)                |
|    - Java, Kotlin, Groovy               |
|    - Maven, Gradle                       |
|    - Git integration                     |
|    - Good enough for this book!          |
|                                          |
|  Ultimate Edition (Paid)                 |
|    - Everything in Community             |
|    - Spring Boot support                 |
|    - Database tools                      |
|    - Web frameworks                      |
|                                          |
+------------------------------------------+
```

> **Tip:** The Community Edition does not have built-in Spring Boot support, but it works perfectly fine. You just will not get the Spring-specific auto-complete. For learning, this is not a problem.

### Option B: Visual Studio Code

VS Code is a lightweight, free editor made by Microsoft. It works well with Java when you add the right extensions.

1. Go to [https://code.visualstudio.com](https://code.visualstudio.com)
2. Download and install
3. Open VS Code
4. Install these extensions (click the square icon on the left sidebar):
   - **Extension Pack for Java** (by Microsoft)
   - **Spring Boot Extension Pack** (by VMware)

```
+------------------------------------------+
|     VS Code Extensions to Install        |
+------------------------------------------+
|                                          |
|  1. Extension Pack for Java              |
|     - Language support                   |
|     - Debugger                           |
|     - Test runner                        |
|     - Maven support                      |
|                                          |
|  2. Spring Boot Extension Pack           |
|     - Spring Initializr integration      |
|     - Spring Boot dashboard              |
|     - Spring Boot property editor        |
|                                          |
+------------------------------------------+
```

### Which IDE Should You Pick?

| Feature            | IntelliJ Community | VS Code        |
|--------------------|-------------------|----------------|
| Java Support       | Excellent         | Good           |
| Setup Effort       | Low               | Medium         |
| Memory Usage       | Higher            | Lower          |
| Spring Support     | Basic (free)      | Good (plugins) |
| Learning Curve     | Easy              | Easy           |
| Best For           | Java-focused work | Multi-language |

**Our recommendation:** If you only write Java, pick IntelliJ IDEA. If you work with multiple languages (JavaScript, Python, etc.), pick VS Code.

Both work. Pick one and move on. Do not spend hours deciding.

---

## 2.5 Installing Maven

### What Is Maven?

Maven is a build tool for Java. It does three main jobs:

1. **Downloads libraries** -- You tell Maven what libraries you need. It downloads them for you.
2. **Compiles code** -- It turns your `.java` files into `.class` files (bytecode).
3. **Packages your app** -- It bundles everything into a single `.jar` file you can run.

Think of Maven as a recipe manager in a kitchen. You write a recipe (the `pom.xml` file). Maven reads the recipe, fetches the ingredients (libraries), and cooks the dish (builds your app).

```
+--------------------------------------------------+
|              How Maven Works                      |
+--------------------------------------------------+
|                                                   |
|   You write:   pom.xml  (the recipe)              |
|                  |                                 |
|                  v                                 |
|   Maven reads the recipe                          |
|                  |                                 |
|                  v                                 |
|   Maven downloads libraries from the internet     |
|   (called "dependencies")                         |
|                  |                                 |
|                  v                                 |
|   Maven compiles your Java code                   |
|                  |                                 |
|                  v                                 |
|   Maven packages everything into a .jar file      |
|                                                   |
+--------------------------------------------------+
```

### Do You Need to Install Maven Separately?

**Short answer:** No, if you use Spring Boot. Spring Boot projects include a file called `mvnw` (Maven Wrapper). This file downloads and uses the correct Maven version automatically.

**But** it is still good to have Maven installed globally. Some tutorials assume it. Some commands are easier to type with `mvn` instead of `./mvnw`.

### Installing Maven

**On Mac (using Homebrew):**

```bash
brew install maven
```

**On Linux (Ubuntu/Debian):**

```bash
sudo apt update
sudo apt install maven
```

**On Windows:**

1. Go to [https://maven.apache.org/download.cgi](https://maven.apache.org/download.cgi)
2. Download the **Binary zip archive**
3. Extract to `C:\Program Files\Maven`
4. Add `C:\Program Files\Maven\bin` to your `Path` environment variable

### Verify Maven

```bash
mvn -version
```

Expected output:

```
Apache Maven 3.9.6 (bc0240f3c744dd6b6ec2920b3cd08dcc295161ae)
Maven home: /usr/local/Cellar/maven/3.9.6/libexec
Java version: 17.0.10, vendor: Eclipse Adoptium
Default locale: en_US, platform encoding: UTF-8
OS name: "mac os x", version: "14.3", arch: "aarch64", family: "mac"
```

Notice that Maven also shows the Java version it is using. Make sure this matches the Java 17+ you installed.

---

## 2.6 Verifying Your Complete Setup

Let us run all three checks in one go. Open a terminal and type:

```bash
java -version
javac -version
mvn -version
```

If all three commands produce output (no errors), your setup is complete.

```
+--------------------------------------------------+
|         Setup Verification Checklist              |
+--------------------------------------------------+
|                                                   |
|  [x]  java -version    -->  17 or higher          |
|  [x]  javac -version   -->  17 or higher          |
|  [x]  mvn -version     -->  3.8 or higher         |
|  [x]  JAVA_HOME set    -->  points to JDK         |
|  [x]  IDE installed    -->  IntelliJ or VS Code   |
|                                                   |
+--------------------------------------------------+
```

---

## 2.7 Common Setup Errors and Fixes

### Error 1: "java is not recognized" or "command not found"

**Cause:** Java is not in your system PATH.

**Fix:**
- Make sure you installed the JDK (not just downloaded it).
- Add the JDK `bin` folder to your PATH variable.
- Close and reopen your terminal after making changes.

### Error 2: java -version shows Java 8 or 11

**Cause:** An older version of Java is installed, and your system is using that one.

**Fix:**
- Install Java 17+ alongside the old version.
- Set `JAVA_HOME` to point to the new JDK.
- On Mac, use `/usr/libexec/java_home -V` to see all installed versions.
- On Windows, move the new JDK path **above** the old one in the PATH variable.

### Error 3: javac works but java does not (or vice versa)

**Cause:** You have mismatched JDK/JRE installations. The `java` command points to one installation. The `javac` command points to another.

**Fix:**
- Use `which java` (Mac/Linux) or `where java` (Windows) to find where each command lives.
- Make sure both point to the same JDK folder.

### Error 4: Maven uses the wrong Java version

**Cause:** Maven looks at the `JAVA_HOME` variable. If `JAVA_HOME` points to an old JDK, Maven will use that one.

**Fix:**
- Set `JAVA_HOME` to point to your Java 17+ JDK.
- Run `mvn -version` again. Check the "Java version" line.

### Error 5: IntelliJ does not detect the JDK

**Cause:** IntelliJ cannot find the JDK on your system.

**Fix:**
1. Open IntelliJ IDEA
2. Go to File > Project Structure > SDKs
3. Click the "+" button
4. Choose "JDK"
5. Browse to your JDK installation folder
6. Click OK

### Error 6: "Permission denied" when running mvnw

**Cause:** On Mac/Linux, the Maven Wrapper script does not have execute permission.

**Fix:**

```bash
chmod +x mvnw
```

This command gives the file permission to run as a program.

---

## Common Mistakes

1. **Installing JRE instead of JDK.** You need the JDK. The JRE cannot compile code.
2. **Not restarting the terminal.** After installing Java or setting environment variables, you must open a new terminal window.
3. **Forgetting JAVA_HOME.** Many tools (Maven, IntelliJ, Gradle) depend on this variable. Always set it.
4. **Using Java 8 or 11 with Spring Boot 3.4.** Spring Boot 3.4 requires Java 17 at minimum. It will not start with older versions.
5. **Spending too long choosing an IDE.** Pick IntelliJ or VS Code. Either one works. Move on.

---

## Best Practices

1. **Use an LTS version of Java.** Java 17 and Java 21 are LTS. They receive updates for years. Avoid non-LTS versions like Java 18 or 19.
2. **Set JAVA_HOME immediately.** Do this right after installing Java. It prevents problems later.
3. **Use the Maven Wrapper (mvnw) in projects.** It ensures every developer on a team uses the same Maven version.
4. **Keep your IDE updated.** IDE updates include bug fixes and better Java support.
5. **Learn keyboard shortcuts.** Speed comes from knowing your IDE. Learn five shortcuts this week. Learn five more next week.

---

## Quick Summary

In this chapter, you installed three essential tools:

- **JDK 17+** -- The Java compiler and runtime. You verified it with `java -version` and `javac -version`.
- **An IDE** -- IntelliJ IDEA Community Edition or Visual Studio Code. Your smart code editor.
- **Maven** -- The build tool that manages libraries and compiles code. You verified it with `mvn -version`.

You also learned the difference between JDK and JRE. The JDK is the full toolkit for developers. The JRE is just the player.

---

## Key Points

- Spring Boot 3.4 requires Java 17 or higher.
- Always install the JDK, not the JRE. The JDK includes the compiler (`javac`).
- Set the `JAVA_HOME` environment variable. Many tools depend on it.
- Maven is a build tool. It downloads libraries, compiles code, and packages applications.
- Spring Boot projects include `mvnw` (Maven Wrapper) so you do not strictly need Maven installed globally.
- IntelliJ IDEA Community Edition and VS Code are both good choices for Java development.

---

## Practice Questions

1. What is the difference between JDK and JRE? Why do developers need the JDK?

2. You run `java -version` and see `openjdk version "11.0.2"`. Can you use this version with Spring Boot 3.4? What should you do?

3. After installing Java 17, you open a terminal and type `java -version`, but it still shows Java 11. What is the most likely cause? How do you fix it?

4. What does the `JAVA_HOME` environment variable do? Name two tools that depend on it.

5. What is the purpose of the Maven Wrapper (`mvnw`) file in a Spring Boot project?

---

## Exercises

### Exercise 1: Verify Your Setup

Open a terminal and run these commands. Write down the output of each one:

```bash
java -version
javac -version
mvn -version
echo $JAVA_HOME    # Mac/Linux
echo %JAVA_HOME%   # Windows
```

Confirm that:
- Java version is 17 or higher
- `javac` version matches the `java` version
- Maven uses the same Java version
- `JAVA_HOME` points to your JDK folder

### Exercise 2: Explore the JDK

Navigate to your JDK installation folder. Find the `bin` directory. List the files inside it. You will see tools like `java`, `javac`, `jar`, `jdb`, and many more. Write down what three of these tools do. (Hint: run any tool with `--help` to see its description.)

### Exercise 3: Create a Simple Java Program

Create a file called `Hello.java` with this content:

```java
public class Hello {
    public static void main(String[] args) {
        System.out.println("My tools are ready!");
    }
}
```

Compile and run it from the terminal:

```bash
javac Hello.java
java Hello
```

Expected output:

```
My tools are ready!
```

If this works, your Java setup is correct.

---

## What Is Next?

Your workbench is ready. Your tools are sharp. In the next chapter, you will use these tools to create your first Spring Boot project. You will visit Spring Initializr, generate a project, import it into your IDE, and see your first web application running in the browser.
