# Chapter 25: Sending Emails

## What You Will Learn

- How email works behind the scenes (SMTP protocol basics).
- How to add email support to a Spring Boot application.
- How to configure SMTP settings for Gmail.
- How to send simple text emails using JavaMailSender.
- How to send HTML emails using MimeMessage.
- How to create beautiful email templates with Thymeleaf.
- How to send emails asynchronously so users do not wait.
- How to build a complete email verification flow for user registration.

## Why This Chapter Matters

Think about the last time you signed up for a website. What happened? You got an email. Maybe it said "Verify your email address" or "Welcome to our platform." Emails are everywhere in modern applications.

Your banking app sends transaction alerts. Your favorite online store sends order confirmations. Your project management tool sends daily digests. Email is the backbone of application-to-user communication.

If you are building a real application, you will need to send emails. Whether it is password resets, welcome messages, order confirmations, or notification alerts, email is not optional. It is expected.

This chapter teaches you how to send emails from your Spring Boot application. You will start with simple text emails, move to beautiful HTML emails, and finish with a complete email verification system that real applications use.

---

## 25.1 How Email Works: The Postal Service Analogy

Before we write code, let us understand how email works. It is a lot like the postal service.

When you send a physical letter:

1. You write the letter (compose the email).
2. You put it in an envelope with a "to" address and a "from" address (set email headers).
3. You drop it at the post office (send it to the SMTP server).
4. The post office routes it to the recipient's local post office (SMTP server routes to recipient's email server).
5. The recipient picks up the letter from their mailbox (they read the email).

```
+----------+       +-----------+       +------------+       +----------+
|   Your   | SMTP  |   Gmail   |       | Recipient  |       |  User's  |
|   App    |------>|   Server  |------>|   Email     |------>|  Inbox   |
| (Sender) |       | (Post     |       |   Server   |       | (Reader) |
|          |       |  Office)  |       | (Delivery) |       |          |
+----------+       +-----------+       +------------+       +----------+

   Step 1:           Step 2:            Step 3:            Step 4:
   Compose           Route              Deliver            Read
   & Send            Email              Email              Email
```

### What Is SMTP?

**SMTP** stands for Simple Mail Transfer Protocol. It is the standard way computers send emails to each other.

Think of SMTP as the postal service's rule book. It defines:

- How to address the envelope (headers like To, From, Subject).
- How to hand the letter to the post office (connect to port 587).
- How to prove you are who you say you are (authentication).
- How to seal the envelope so nobody reads it in transit (TLS encryption).

| SMTP Term | Postal Analogy | Description |
|---|---|---|
| SMTP Server | Post Office | The server that accepts and routes emails |
| Port 587 | Mail Slot | The door where you drop off the email |
| TLS | Sealed Envelope | Encryption to protect the email content |
| Authentication | ID Check | Proving you are allowed to send from this address |

---

## 25.2 Adding Email Support to Spring Boot

Spring Boot makes sending emails easy with the `spring-boot-starter-mail` dependency.

### Step 1: Add the Dependency

Open your `pom.xml` and add:

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-mail</artifactId>
</dependency>
```

This single dependency brings in everything you need:

- JavaMail API (the standard Java email library).
- Spring's email abstraction layer.
- Auto-configuration for mail settings.

### Step 2: What You Get Automatically

When Spring Boot sees this dependency, it automatically:

1. Creates a `JavaMailSender` bean.
2. Reads your SMTP configuration from `application.properties`.
3. Sets up connection pooling for efficiency.

```
+---------------------+       +------------------+       +-------------+
| spring-boot-starter |       | Auto-             |       | JavaMail    |
| -mail (pom.xml)     |------>| Configuration     |------>| Sender Bean |
|                     |       | reads properties  |       | (Ready!)    |
+---------------------+       +------------------+       +-------------+
                                      |
                               +------+------+
                               | application |
                               | .properties |
                               +-------------+
```

---

## 25.3 Configuring SMTP for Gmail

Let us configure our application to send emails through Gmail. Gmail is free and perfect for development and small applications.

### Step 1: Create an App Password in Gmail

Gmail does not allow regular passwords for third-party apps. You need an **App Password**.

1. Go to your Google Account settings.
2. Navigate to Security.
3. Enable 2-Step Verification (if not already enabled).
4. Go to App passwords.
5. Select "Mail" and "Other (Custom name)".
6. Enter "Spring Boot App" as the name.
7. Click Generate.
8. Copy the 16-character password.

> **Important**: An App Password is a special password that lets your Spring Boot app access Gmail without needing your main Google password. Never share it or commit it to version control.

### Step 2: Configure application.properties

```properties
# application.properties

# SMTP Server Settings
spring.mail.host=smtp.gmail.com
spring.mail.port=587
spring.mail.username=your.email@gmail.com
spring.mail.password=your-app-password

# TLS Encryption Settings
spring.mail.properties.mail.smtp.auth=true
spring.mail.properties.mail.smtp.starttls.enable=true
spring.mail.properties.mail.smtp.starttls.required=true

# Connection Timeout Settings (in milliseconds)
spring.mail.properties.mail.smtp.connectiontimeout=5000
spring.mail.properties.mail.smtp.timeout=5000
spring.mail.properties.mail.smtp.writetimeout=5000
```

Let us break down each setting:

| Property | Value | What It Does |
|---|---|---|
| `spring.mail.host` | `smtp.gmail.com` | Gmail's SMTP server address |
| `spring.mail.port` | `587` | Port for TLS-encrypted email |
| `spring.mail.username` | Your Gmail address | The "from" email address |
| `spring.mail.password` | App Password | The 16-character app password |
| `mail.smtp.auth` | `true` | Enable authentication |
| `mail.smtp.starttls.enable` | `true` | Enable TLS encryption |
| `mail.smtp.starttls.required` | `true` | Require TLS (reject unencrypted) |

> **Security Warning**: Never hardcode your password in `application.properties` for production. Use environment variables instead. We will cover this in Chapter 29 (Externalized Configuration).

### Using Environment Variables (Recommended)

```properties
# application.properties (safer approach)
spring.mail.host=smtp.gmail.com
spring.mail.port=587
spring.mail.username=${MAIL_USERNAME}
spring.mail.password=${MAIL_PASSWORD}
spring.mail.properties.mail.smtp.auth=true
spring.mail.properties.mail.smtp.starttls.enable=true
spring.mail.properties.mail.smtp.starttls.required=true
```

Set the environment variables before running your application:

```bash
export MAIL_USERNAME=your.email@gmail.com
export MAIL_PASSWORD=your-app-password
```

---

## 25.4 Sending Simple Text Emails

Now let us send our first email. We will start with a simple plain-text email.

### Creating an Email Service

```java
// src/main/java/com/example/emaildemo/service/EmailService.java

package com.example.emaildemo.service;

import org.springframework.mail.SimpleMailMessage;       // 1
import org.springframework.mail.javamail.JavaMailSender;  // 2
import org.springframework.stereotype.Service;            // 3

@Service                                                  // 4
public class EmailService {

    private final JavaMailSender mailSender;               // 5

    public EmailService(JavaMailSender mailSender) {       // 6
        this.mailSender = mailSender;
    }

    public void sendSimpleEmail(String to,                 // 7
                                String subject,
                                String body) {

        SimpleMailMessage message = new SimpleMailMessage(); // 8
        message.setFrom("your.email@gmail.com");             // 9
        message.setTo(to);                                   // 10
        message.setSubject(subject);                         // 11
        message.setText(body);                               // 12

        mailSender.send(message);                            // 13

        System.out.println("Email sent to: " + to);         // 14
    }
}
```

**Line-by-line explanation:**

- **Line 1**: Import `SimpleMailMessage`, a class for plain-text emails.
- **Line 2**: Import `JavaMailSender`, the main interface for sending emails.
- **Line 3**: Import the `@Service` annotation.
- **Line 4**: `@Service` tells Spring this is a service component. Spring creates and manages it.
- **Line 5**: Declare the `JavaMailSender` field. Spring Boot auto-configured this for us.
- **Line 6**: Constructor injection. Spring gives us the `JavaMailSender` automatically.
- **Line 7**: Our method takes three parameters: recipient, subject, and body.
- **Line 8**: Create a new `SimpleMailMessage` object. Think of this as creating a new letter.
- **Line 9**: Set the sender's email address (the "From" field).
- **Line 10**: Set the recipient's email address (the "To" field).
- **Line 11**: Set the email subject line.
- **Line 12**: Set the email body text.
- **Line 13**: Send the email. This connects to Gmail's SMTP server and delivers the message.
- **Line 14**: Print a confirmation message to the console.

### Creating a Controller to Trigger Emails

```java
// src/main/java/com/example/emaildemo/controller/EmailController.java

package com.example.emaildemo.controller;

import com.example.emaildemo.service.EmailService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/emails")
public class EmailController {

    private final EmailService emailService;

    public EmailController(EmailService emailService) {
        this.emailService = emailService;
    }

    @PostMapping("/send")
    public ResponseEntity<Map<String, String>> sendEmail(
            @RequestParam String to,
            @RequestParam String subject,
            @RequestParam String body) {

        emailService.sendSimpleEmail(to, subject, body);

        return ResponseEntity.ok(
            Map.of("message", "Email sent successfully",
                   "to", to)
        );
    }
}
```

### Testing with curl

```bash
curl -X POST "http://localhost:8080/api/emails/send?\
to=friend@example.com&\
subject=Hello%20from%20Spring%20Boot&\
body=This%20is%20my%20first%20email%20from%20Spring%20Boot!"
```

**Output:**

```json
{
  "message": "Email sent successfully",
  "to": "friend@example.com"
}
```

**Console Output:**

```
Email sent to: friend@example.com
```

### Sending to Multiple Recipients

```java
public void sendToMultiple(String[] recipients,
                           String subject,
                           String body) {

    SimpleMailMessage message = new SimpleMailMessage();
    message.setFrom("your.email@gmail.com");
    message.setTo(recipients);           // Pass an array of addresses
    message.setSubject(subject);
    message.setText(body);

    mailSender.send(message);
}
```

### Adding CC and BCC

```java
public void sendWithCcBcc(String to, String subject, String body) {

    SimpleMailMessage message = new SimpleMailMessage();
    message.setFrom("your.email@gmail.com");
    message.setTo(to);
    message.setCc("manager@example.com");         // CC: visible copy
    message.setBcc("archive@example.com");        // BCC: hidden copy
    message.setSubject(subject);
    message.setText(body);

    mailSender.send(message);
}
```

---

## 25.5 Sending HTML Emails with MimeMessage

Plain text emails are functional, but they look boring. Real applications send HTML emails with formatting, images, and buttons. Think about emails you get from Amazon or Netflix. They look like mini web pages. That is because they are HTML.

### HTML Email vs Plain Text Email

```
Plain Text Email:                    HTML Email:
+-------------------------+         +---------------------------+
| Hello John,             |         | +---------------------+  |
|                         |         | |    WELCOME, JOHN!   |  |
| Welcome to our app.     |         | +---------------------+  |
| Click this link to      |         |                           |
| verify: http://...      |         | Welcome to our app.       |
|                         |         |                           |
| Thanks,                 |         | +---------------------+  |
| The Team                |         | | VERIFY YOUR EMAIL   |  |
+-------------------------+         | +---------------------+  |
                                    |                           |
                                    | Thanks, The Team          |
                                    +---------------------------+
```

### Creating an HTML Email Service

```java
// src/main/java/com/example/emaildemo/service/HtmlEmailService.java

package com.example.emaildemo.service;

import jakarta.mail.MessagingException;                          // 1
import jakarta.mail.internet.MimeMessage;                        // 2
import org.springframework.mail.javamail.JavaMailSender;         // 3
import org.springframework.mail.javamail.MimeMessageHelper;      // 4
import org.springframework.stereotype.Service;

@Service
public class HtmlEmailService {

    private final JavaMailSender mailSender;

    public HtmlEmailService(JavaMailSender mailSender) {
        this.mailSender = mailSender;
    }

    public void sendHtmlEmail(String to,                         // 5
                              String subject,
                              String htmlContent)
                              throws MessagingException {        // 6

        MimeMessage message = mailSender.createMimeMessage();    // 7

        MimeMessageHelper helper =
            new MimeMessageHelper(message, true, "UTF-8");       // 8

        helper.setFrom("your.email@gmail.com");                  // 9
        helper.setTo(to);                                        // 10
        helper.setSubject(subject);                              // 11
        helper.setText(htmlContent, true);                       // 12

        mailSender.send(message);                                // 13
    }
}
```

**Line-by-line explanation:**

- **Line 1**: Import `MessagingException` from Jakarta Mail (the checked exception for mail errors).
- **Line 2**: Import `MimeMessage`, which supports HTML content, attachments, and more.
- **Line 3**: Import `JavaMailSender` to send the message.
- **Line 4**: Import `MimeMessageHelper`, a Spring utility that makes working with `MimeMessage` easier.
- **Line 5**: Method accepts recipient, subject, and HTML content as strings.
- **Line 6**: Declare that this method might throw a `MessagingException`.
- **Line 7**: Create a new `MimeMessage` using the mail sender. Unlike `SimpleMailMessage`, this supports rich content.
- **Line 8**: Create a `MimeMessageHelper`. The `true` parameter enables multipart mode (needed for HTML and attachments). `"UTF-8"` sets the character encoding.
- **Line 9-11**: Set from, to, and subject just like before.
- **Line 12**: Set the email body. The `true` parameter tells Spring this is HTML, not plain text.
- **Line 13**: Send the email.

### Sending an HTML Email

```java
// In your controller or wherever you want to trigger the email

String html = """
    <html>
    <body style="font-family: Arial, sans-serif;">
        <div style="max-width: 600px; margin: 0 auto;
                    padding: 20px; background-color: #f9f9f9;">

            <h1 style="color: #333;">Welcome to Our App!</h1>

            <p>Hello <strong>John</strong>,</p>

            <p>Thank you for signing up. We are excited to
               have you on board.</p>

            <a href="https://example.com/verify?token=abc123"
               style="display: inline-block; padding: 12px 24px;
                      background-color: #007bff; color: white;
                      text-decoration: none; border-radius: 4px;">
                Verify Your Email
            </a>

            <p style="color: #666; margin-top: 20px;">
                If you did not create this account, please
                ignore this email.
            </p>

        </div>
    </body>
    </html>
    """;

htmlEmailService.sendHtmlEmail(
    "john@example.com",
    "Welcome to Our App!",
    html
);
```

### Sending Emails with Attachments

```java
public void sendEmailWithAttachment(String to,
                                    String subject,
                                    String htmlContent,
                                    String attachmentPath)
                                    throws MessagingException {

    MimeMessage message = mailSender.createMimeMessage();

    MimeMessageHelper helper =
        new MimeMessageHelper(message, true, "UTF-8");    // true = multipart

    helper.setFrom("your.email@gmail.com");
    helper.setTo(to);
    helper.setSubject(subject);
    helper.setText(htmlContent, true);

    // Add the attachment
    FileSystemResource file =
        new FileSystemResource(new File(attachmentPath));

    helper.addAttachment(
        file.getFilename(),   // Name shown in the email
        file                  // The actual file
    );

    mailSender.send(message);
}
```

### Embedding Images in HTML Emails

Sometimes you want images to appear inside the email body, not as attachments.

```java
public void sendEmailWithInlineImage(String to,
                                     String subject)
                                     throws MessagingException {

    MimeMessage message = mailSender.createMimeMessage();

    MimeMessageHelper helper =
        new MimeMessageHelper(message, true, "UTF-8");

    helper.setFrom("your.email@gmail.com");
    helper.setTo(to);
    helper.setSubject(subject);

    // Reference the image with cid:logoImage
    String html = """
        <html>
        <body>
            <img src="cid:logoImage" width="200" />
            <h1>Welcome!</h1>
            <p>Thanks for joining us.</p>
        </body>
        </html>
        """;

    helper.setText(html, true);

    // Add the inline image
    ClassPathResource image =
        new ClassPathResource("static/images/logo.png");

    helper.addInline("logoImage", image);   // ID must match cid:

    mailSender.send(message);
}
```

```
How Inline Images Work:
+-----------------------+
|  HTML Email           |
|  <img src="cid:logo"> |---+
|                       |   |    +------------+
|  Welcome!             |   +--->| logo.png   |
|  Thanks for joining.  |       | (embedded)  |
+-----------------------+       +------------+

The image travels WITH the email, not loaded from a URL.
```

---

## 25.6 Email Templates with Thymeleaf

Hardcoding HTML strings in Java is messy and hard to maintain. Imagine changing a button color and having to dig through Java files. That is like keeping your recipes written on napkins instead of in a cookbook.

Thymeleaf is a template engine that lets you create HTML templates as separate files. You fill in the dynamic parts (like the user's name) at runtime.

### Step 1: Add Thymeleaf Dependency

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-thymeleaf</artifactId>
</dependency>
```

### Step 2: Create an Email Template

```html
<!-- src/main/resources/templates/email/welcome.html -->

<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8"/>
</head>
<body style="font-family: Arial, sans-serif;
             background-color: #f4f4f4;
             margin: 0; padding: 20px;">

    <div style="max-width: 600px; margin: 0 auto;
                background-color: #ffffff;
                border-radius: 8px; padding: 30px;">

        <!-- Dynamic greeting -->
        <h1 style="color: #2c3e50;">
            Welcome, <span th:text="${userName}">User</span>!
        </h1>

        <p style="color: #555; line-height: 1.6;">
            Thank you for joining
            <strong th:text="${appName}">Our App</strong>.
            We are glad to have you!
        </p>

        <!-- Dynamic verification link -->
        <div style="text-align: center; margin: 30px 0;">
            <a th:href="${verificationUrl}"
               style="display: inline-block;
                      padding: 14px 28px;
                      background-color: #3498db;
                      color: #ffffff;
                      text-decoration: none;
                      border-radius: 6px;
                      font-size: 16px;">
                Verify Your Email
            </a>
        </div>

        <p style="color: #999; font-size: 12px;">
            This link expires in
            <span th:text="${expirationHours}">24</span> hours.
        </p>

        <hr style="border: 1px solid #eee;"/>

        <p style="color: #999; font-size: 12px;">
            If you did not create an account, ignore this email.
        </p>
    </div>

</body>
</html>
```

### Step 3: Create a Template Email Service

```java
// src/main/java/com/example/emaildemo/service/TemplateEmailService.java

package com.example.emaildemo.service;

import jakarta.mail.MessagingException;
import jakarta.mail.internet.MimeMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.stereotype.Service;
import org.thymeleaf.TemplateEngine;                            // 1
import org.thymeleaf.context.Context;                           // 2

@Service
public class TemplateEmailService {

    private final JavaMailSender mailSender;
    private final TemplateEngine templateEngine;                // 3

    public TemplateEmailService(JavaMailSender mailSender,
                                TemplateEngine templateEngine) {
        this.mailSender = mailSender;
        this.templateEngine = templateEngine;                   // 4
    }

    public void sendWelcomeEmail(String to,                     // 5
                                 String userName)
                                 throws MessagingException {

        // Create the Thymeleaf context with variables
        Context context = new Context();                        // 6
        context.setVariable("userName", userName);              // 7
        context.setVariable("appName", "BookStore");            // 8
        context.setVariable("verificationUrl",                  // 9
            "https://example.com/verify?email=" + to);
        context.setVariable("expirationHours", 24);             // 10

        // Process the template into an HTML string
        String htmlContent = templateEngine.process(            // 11
            "email/welcome",                                    // 12
            context                                             // 13
        );

        // Send the HTML email
        MimeMessage message = mailSender.createMimeMessage();
        MimeMessageHelper helper =
            new MimeMessageHelper(message, true, "UTF-8");

        helper.setFrom("your.email@gmail.com");
        helper.setTo(to);
        helper.setSubject("Welcome to BookStore!");
        helper.setText(htmlContent, true);                      // 14

        mailSender.send(message);
    }
}
```

**Line-by-line explanation:**

- **Line 1**: Import Thymeleaf's `TemplateEngine`. This processes HTML templates.
- **Line 2**: Import `Context`, which holds the variables to inject into the template.
- **Line 3**: Declare the `TemplateEngine` field.
- **Line 4**: Spring injects the `TemplateEngine` automatically (thanks to the Thymeleaf starter).
- **Line 5**: Method takes the recipient email and user name.
- **Line 6**: Create a new Thymeleaf context. Think of this as a bag of variables.
- **Line 7**: Put the `userName` variable in the bag. In the template, `${userName}` will be replaced.
- **Line 8**: Set the app name. `${appName}` in the template becomes "BookStore".
- **Line 9**: Set the verification URL.
- **Line 10**: Set the expiration hours.
- **Line 11**: Process the template. This takes the HTML file and replaces all `${...}` placeholders.
- **Line 12**: The template path is relative to `src/main/resources/templates/`.
- **Line 13**: Pass the context with all our variables.
- **Line 14**: Set the processed HTML as the email body.

```
How Thymeleaf Email Templates Work:

+------------------+      +------------------+      +------------------+
| Template File    |      | Thymeleaf        |      | Final HTML       |
| (welcome.html)   |      | Engine           |      | (sent as email)  |
|                  |      |                  |      |                  |
| Welcome,         |      | Replaces:        |      | Welcome,         |
| ${userName}!     |----->| ${userName}      |----->| John!            |
|                  |      | -> "John"        |      |                  |
| ${appName}       |      | ${appName}       |      | BookStore        |
|                  |      | -> "BookStore"   |      |                  |
+------------------+      +------------------+      +------------------+
```

### Creating Multiple Templates

You can create different templates for different email types:

```
src/main/resources/templates/email/
    welcome.html              <- Welcome email
    password-reset.html       <- Password reset email
    order-confirmation.html   <- Order confirmation
    newsletter.html           <- Weekly newsletter
```

Here is a password reset template:

```html
<!-- src/main/resources/templates/email/password-reset.html -->

<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8"/>
</head>
<body style="font-family: Arial, sans-serif;
             background-color: #f4f4f4;
             margin: 0; padding: 20px;">

    <div style="max-width: 600px; margin: 0 auto;
                background-color: #ffffff;
                border-radius: 8px; padding: 30px;">

        <h1 style="color: #e74c3c;">Password Reset</h1>

        <p>Hello <span th:text="${userName}">User</span>,</p>

        <p>We received a request to reset your password.
           Click the button below to create a new password.</p>

        <div style="text-align: center; margin: 30px 0;">
            <a th:href="${resetUrl}"
               style="display: inline-block;
                      padding: 14px 28px;
                      background-color: #e74c3c;
                      color: #ffffff;
                      text-decoration: none;
                      border-radius: 6px;">
                Reset Password
            </a>
        </div>

        <p style="color: #999;">
            This link expires in
            <span th:text="${expirationMinutes}">30</span>
            minutes.
        </p>

        <p style="color: #999;">
            If you did not request this, ignore this email.
            Your password will remain unchanged.
        </p>
    </div>

</body>
</html>
```

---

## 25.7 Sending Emails Asynchronously with @Async

Sending an email takes time. Your application connects to Gmail's server, authenticates, sends the data, and waits for confirmation. This can take 1 to 5 seconds.

If you send emails synchronously (the default), your user has to wait:

```
Synchronous (User Waits):

User clicks       Email is         Response sent
"Register"        being sent       to user
    |                |                  |
    v                v                  v
----[=====WAIT=====][===SENDING===]---->
         500ms           3000ms

Total: 3500ms  (User waits 3.5 seconds!)
```

With `@Async`, the email is sent in a background thread:

```
Asynchronous (User Does NOT Wait):

User clicks       Response sent
"Register"        to user (fast!)
    |                |
    v                v
----[=====WAIT=====]---->
         500ms
                   Email sent in background
                   [===SENDING===]
                        3000ms
                   (User does not notice)

Total for user: 500ms  (Much better!)
```

### Step 1: Enable Async Support

```java
// src/main/java/com/example/emaildemo/EmailDemoApplication.java

package com.example.emaildemo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;    // 1

@SpringBootApplication
@EnableAsync                                                     // 2
public class EmailDemoApplication {

    public static void main(String[] args) {
        SpringApplication.run(EmailDemoApplication.class, args);
    }
}
```

- **Line 1**: Import the `@EnableAsync` annotation.
- **Line 2**: `@EnableAsync` tells Spring to enable asynchronous method execution. Without this, `@Async` does nothing.

### Step 2: Configure the Thread Pool (Optional but Recommended)

```java
// src/main/java/com/example/emaildemo/config/AsyncConfig.java

package com.example.emaildemo.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;

import java.util.concurrent.Executor;

@Configuration
@EnableAsync
public class AsyncConfig {

    @Bean(name = "emailExecutor")
    public Executor emailExecutor() {
        ThreadPoolTaskExecutor executor =
            new ThreadPoolTaskExecutor();

        executor.setCorePoolSize(2);         // Minimum 2 threads
        executor.setMaxPoolSize(5);          // Maximum 5 threads
        executor.setQueueCapacity(100);      // Queue up to 100 emails
        executor.setThreadNamePrefix("email-");
        executor.initialize();

        return executor;
    }
}
```

Think of the thread pool like a team of mail carriers:

- **Core Pool Size (2)**: You always have 2 mail carriers working.
- **Max Pool Size (5)**: If things get busy, you can hire up to 5.
- **Queue Capacity (100)**: If all carriers are busy, up to 100 letters can wait in line.

### Step 3: Make the Email Method Async

```java
// Updated EmailService with @Async

@Service
public class EmailService {

    private final JavaMailSender mailSender;

    public EmailService(JavaMailSender mailSender) {
        this.mailSender = mailSender;
    }

    @Async("emailExecutor")                                    // 1
    public void sendSimpleEmail(String to,
                                String subject,
                                String body) {

        try {
            SimpleMailMessage message = new SimpleMailMessage();
            message.setFrom("your.email@gmail.com");
            message.setTo(to);
            message.setSubject(subject);
            message.setText(body);

            mailSender.send(message);

            System.out.println(
                Thread.currentThread().getName()               // 2
                + " - Email sent to: " + to
            );

        } catch (Exception e) {                                // 3
            System.err.println(
                "Failed to send email to " + to
                + ": " + e.getMessage()
            );
        }
    }
}
```

**Line-by-line explanation:**

- **Line 1**: `@Async("emailExecutor")` tells Spring to run this method in a separate thread from the "emailExecutor" pool. The caller will not wait for it to finish.
- **Line 2**: Print the thread name to verify it runs on a background thread (e.g., "email-1").
- **Line 3**: Important! Since this runs in the background, exceptions will not propagate to the caller. You must catch and handle them here.

**Console Output:**

```
email-1 - Email sent to: john@example.com
email-2 - Email sent to: jane@example.com
```

Notice the thread names (`email-1`, `email-2`) instead of the main thread.

> **Important Rule**: `@Async` only works when the method is called from a different class. If you call an `@Async` method from within the same class, it runs synchronously. This is because Spring uses proxies to intercept the call, and self-calls bypass the proxy.

```
Works (different class calls async method):
+------------------+       +------------------+
| EmailController  |------>| EmailService     |
| (calls method)   |       | @Async method    |
+------------------+       | (runs in bg)     |
                           +------------------+

Does NOT work (same class calls async method):
+------------------+
| EmailService     |
| method A() ------+---> @Async method B()
| (same class!)    |     (runs synchronously!)
+------------------+
```

---

## 25.8 Building an Email Verification Flow

Now let us put everything together and build a real email verification system. This is the flow you see when you sign up for almost any website.

### The Complete Flow

```
+--------+    +----------+    +----------+    +---------+    +--------+
|  User  |    |  Spring  |    |  Save    |    |  Send   |    |  User  |
|  Signs |    |  Boot    |    |  Token   |    |  Email  |    |  Clicks|
|  Up    |--->|  App     |--->|  to DB   |--->|  with   |--->|  Link  |
|        |    |          |    |          |    |  Link   |    |        |
+--------+    +----------+    +----------+    +---------+    +---+----+
                                                                 |
                                                                 v
+--------+    +----------+    +----------+    +---------+        |
|  User  |    |  Mark    |    |  Verify  |    |  User   |        |
|  Can   |<---|  User as |<---|  Token   |<---|  Hits   |<-------+
|  Login |    |  Verified|    |  Valid?  |    |  /verify|
+--------+    +----------+    +----------+    +---------+
```

### Step 1: Create the User Entity

```java
// src/main/java/com/example/emaildemo/entity/User.java

package com.example.emaildemo.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "users")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false, unique = true)
    private String email;

    @Column(nullable = false)
    private String password;

    @Column(nullable = false)
    private boolean emailVerified = false;           // 1

    @Column(unique = true)
    private String verificationToken;                // 2

    private LocalDateTime tokenExpiryDate;           // 3

    // Constructors
    public User() {}

    public User(String name, String email, String password) {
        this.name = name;
        this.email = email;
        this.password = password;
    }

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getPassword() { return password; }
    public void setPassword(String password) {
        this.password = password;
    }

    public boolean isEmailVerified() { return emailVerified; }
    public void setEmailVerified(boolean emailVerified) {
        this.emailVerified = emailVerified;
    }

    public String getVerificationToken() {
        return verificationToken;
    }
    public void setVerificationToken(String verificationToken) {
        this.verificationToken = verificationToken;
    }

    public LocalDateTime getTokenExpiryDate() {
        return tokenExpiryDate;
    }
    public void setTokenExpiryDate(LocalDateTime tokenExpiryDate) {
        this.tokenExpiryDate = tokenExpiryDate;
    }
}
```

- **Line 1**: Tracks whether the user has verified their email. Defaults to `false`.
- **Line 2**: A unique random token sent in the verification email.
- **Line 3**: When the token expires (e.g., 24 hours after registration).

### Step 2: Create the Repository

```java
// src/main/java/com/example/emaildemo/repository/UserRepository.java

package com.example.emaildemo.repository;

import com.example.emaildemo.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {

    Optional<User> findByEmail(String email);

    Optional<User> findByVerificationToken(String token);
}
```

### Step 3: Create the Verification Email Service

```java
// src/main/java/com/example/emaildemo/service/VerificationEmailService.java

package com.example.emaildemo.service;

import jakarta.mail.MessagingException;
import jakarta.mail.internet.MimeMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.thymeleaf.TemplateEngine;
import org.thymeleaf.context.Context;

@Service
public class VerificationEmailService {

    private final JavaMailSender mailSender;
    private final TemplateEngine templateEngine;

    public VerificationEmailService(JavaMailSender mailSender,
                                    TemplateEngine templateEngine) {
        this.mailSender = mailSender;
        this.templateEngine = templateEngine;
    }

    @Async("emailExecutor")
    public void sendVerificationEmail(String to,
                                      String name,
                                      String token) {
        try {
            Context context = new Context();
            context.setVariable("userName", name);
            context.setVariable("verificationUrl",
                "http://localhost:8080/api/auth/verify?token="
                + token);
            context.setVariable("appName", "BookStore");
            context.setVariable("expirationHours", 24);

            String html = templateEngine.process(
                "email/welcome", context);

            MimeMessage message = mailSender.createMimeMessage();
            MimeMessageHelper helper =
                new MimeMessageHelper(message, true, "UTF-8");

            helper.setFrom("your.email@gmail.com");
            helper.setTo(to);
            helper.setSubject("Verify Your Email - BookStore");
            helper.setText(html, true);

            mailSender.send(message);

            System.out.println("Verification email sent to: " + to);

        } catch (MessagingException e) {
            System.err.println(
                "Failed to send verification email: "
                + e.getMessage()
            );
        }
    }
}
```

### Step 4: Create the Registration Service

```java
// src/main/java/com/example/emaildemo/service/RegistrationService.java

package com.example.emaildemo.service;

import com.example.emaildemo.entity.User;
import com.example.emaildemo.repository.UserRepository;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.UUID;

@Service
public class RegistrationService {

    private final UserRepository userRepository;
    private final VerificationEmailService emailService;

    public RegistrationService(
            UserRepository userRepository,
            VerificationEmailService emailService) {
        this.userRepository = userRepository;
        this.emailService = emailService;
    }

    public User registerUser(String name,
                             String email,
                             String password) {

        // Check if email already exists
        if (userRepository.findByEmail(email).isPresent()) {      // 1
            throw new RuntimeException(
                "Email already registered: " + email);
        }

        // Create the user
        User user = new User(name, email, password);              // 2

        // Generate a verification token
        String token = UUID.randomUUID().toString();              // 3
        user.setVerificationToken(token);
        user.setTokenExpiryDate(
            LocalDateTime.now().plusHours(24));                    // 4

        // Save to database
        User savedUser = userRepository.save(user);               // 5

        // Send verification email (async - does not block)
        emailService.sendVerificationEmail(                       // 6
            email, name, token);

        return savedUser;
    }

    public String verifyEmail(String token) {

        // Find user by token
        User user = userRepository                                // 7
            .findByVerificationToken(token)
            .orElseThrow(() -> new RuntimeException(
                "Invalid verification token"));

        // Check if token has expired
        if (user.getTokenExpiryDate()
                .isBefore(LocalDateTime.now())) {                 // 8
            throw new RuntimeException(
                "Verification token has expired");
        }

        // Mark user as verified
        user.setEmailVerified(true);                              // 9
        user.setVerificationToken(null);                          // 10
        user.setTokenExpiryDate(null);
        userRepository.save(user);

        return "Email verified successfully!";
    }
}
```

**Key lines explained:**

- **Line 1**: Check for duplicate emails before registering.
- **Line 2**: Create a new user (not yet verified).
- **Line 3**: Generate a random UUID token. Example: `"a3b2c1d4-e5f6-7890-abcd-ef1234567890"`.
- **Line 4**: Token expires in 24 hours.
- **Line 5**: Save the user to the database.
- **Line 6**: Send verification email asynchronously. The method returns immediately.
- **Line 7**: When the user clicks the link, find them by the token.
- **Line 8**: Check if the token has expired.
- **Line 9**: Mark the email as verified.
- **Line 10**: Clear the token so it cannot be reused.

### Step 5: Create the Auth Controller

```java
// src/main/java/com/example/emaildemo/controller/AuthController.java

package com.example.emaildemo.controller;

import com.example.emaildemo.entity.User;
import com.example.emaildemo.service.RegistrationService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final RegistrationService registrationService;

    public AuthController(RegistrationService registrationService) {
        this.registrationService = registrationService;
    }

    @PostMapping("/register")
    public ResponseEntity<Map<String, String>> register(
            @RequestParam String name,
            @RequestParam String email,
            @RequestParam String password) {

        User user = registrationService.registerUser(
            name, email, password);

        return ResponseEntity.ok(Map.of(
            "message", "Registration successful! "
                     + "Check your email for verification.",
            "email", user.getEmail()
        ));
    }

    @GetMapping("/verify")
    public ResponseEntity<Map<String, String>> verify(
            @RequestParam String token) {

        String result = registrationService.verifyEmail(token);

        return ResponseEntity.ok(Map.of("message", result));
    }
}
```

### Testing the Complete Flow

**Step 1: Register a new user:**

```bash
curl -X POST "http://localhost:8080/api/auth/register?\
name=John&\
email=john@example.com&\
password=secret123"
```

**Output:**

```json
{
  "message": "Registration successful! Check your email for verification.",
  "email": "john@example.com"
}
```

**Step 2: User receives an email with a verification link.**

**Step 3: User clicks the verification link:**

```bash
curl "http://localhost:8080/api/auth/verify?\
token=a3b2c1d4-e5f6-7890-abcd-ef1234567890"
```

**Output:**

```json
{
  "message": "Email verified successfully!"
}
```

---

## 25.9 Error Handling for Emails

Emails can fail for many reasons. The SMTP server might be down. The recipient address might be invalid. Your credentials might be wrong. Good applications handle these failures gracefully.

### Creating a Custom Email Exception

```java
// src/main/java/com/example/emaildemo/exception/EmailSendException.java

package com.example.emaildemo.exception;

public class EmailSendException extends RuntimeException {

    public EmailSendException(String message) {
        super(message);
    }

    public EmailSendException(String message, Throwable cause) {
        super(message, cause);
    }
}
```

### Adding Retry Logic

```java
// Improved EmailService with retry logic

@Service
public class EmailService {

    private final JavaMailSender mailSender;
    private static final int MAX_RETRIES = 3;

    public EmailService(JavaMailSender mailSender) {
        this.mailSender = mailSender;
    }

    @Async("emailExecutor")
    public void sendEmailWithRetry(String to,
                                   String subject,
                                   String body) {

        int attempts = 0;

        while (attempts < MAX_RETRIES) {
            try {
                SimpleMailMessage message =
                    new SimpleMailMessage();
                message.setFrom("your.email@gmail.com");
                message.setTo(to);
                message.setSubject(subject);
                message.setText(body);

                mailSender.send(message);

                System.out.println("Email sent to: " + to
                    + " (attempt " + (attempts + 1) + ")");
                return;  // Success! Exit the method.

            } catch (Exception e) {
                attempts++;
                System.err.println(
                    "Attempt " + attempts + " failed for "
                    + to + ": " + e.getMessage()
                );

                if (attempts >= MAX_RETRIES) {
                    System.err.println(
                        "All " + MAX_RETRIES
                        + " attempts failed for " + to
                    );
                    // Log to monitoring system, save to
                    // database for manual retry, etc.
                }

                try {
                    // Wait before retrying
                    // (exponential backoff)
                    Thread.sleep(
                        1000L * attempts);  // 1s, 2s, 3s
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    return;
                }
            }
        }
    }
}
```

---

## Common Mistakes

### Mistake 1: Committing Email Credentials to Git

```properties
# WRONG: Never commit real credentials
spring.mail.password=myActualPassword123
```

```properties
# CORRECT: Use environment variables
spring.mail.password=${MAIL_PASSWORD}
```

### Mistake 2: Sending Emails Synchronously in API Endpoints

```java
// WRONG: User waits for email to send
@PostMapping("/register")
public ResponseEntity<String> register(...) {
    userService.save(user);
    emailService.sendEmail(user.getEmail(), ...);  // Blocks!
    return ResponseEntity.ok("Done");
}
```

```java
// CORRECT: Use @Async so user does not wait
@Async("emailExecutor")
public void sendEmail(String to, ...) {
    // Runs in background thread
}
```

### Mistake 3: Calling @Async from the Same Class

```java
// WRONG: @Async is ignored when called from same class
@Service
public class EmailService {

    public void sendWelcome(String email) {
        sendEmail(email, "Welcome", "Hello!");  // NOT async!
    }

    @Async
    public void sendEmail(String to, String subject, String body) {
        // This runs synchronously because it is called
        // from the same class!
    }
}
```

```java
// CORRECT: Call @Async method from a different class
@Service
public class RegistrationService {

    private final EmailService emailService;  // Different class

    public void register(String email) {
        emailService.sendEmail(email, "Welcome", "Hello!");
        // Now it runs asynchronously!
    }
}
```

### Mistake 4: Not Handling Email Failures

```java
// WRONG: Exception crashes the background thread silently
@Async
public void sendEmail(String to, String subject, String body) {
    mailSender.send(message);  // If this fails, nobody knows
}
```

```java
// CORRECT: Catch and handle exceptions
@Async
public void sendEmail(String to, String subject, String body) {
    try {
        mailSender.send(message);
    } catch (Exception e) {
        log.error("Email failed for {}: {}", to, e.getMessage());
        // Save to a retry queue or alert monitoring
    }
}
```

### Mistake 5: Using Port 25 Instead of 587

```properties
# WRONG: Port 25 is unencrypted and often blocked
spring.mail.port=25
```

```properties
# CORRECT: Port 587 uses TLS encryption
spring.mail.port=587
```

---

## Best Practices

1. **Always use environment variables for credentials.** Never hardcode email passwords in your source code or configuration files.

2. **Send emails asynchronously.** Users should never wait for emails to be sent. Use `@Async` with a dedicated thread pool.

3. **Use Thymeleaf templates for HTML emails.** Keep your HTML separate from your Java code. It is easier to maintain and designers can edit templates without touching Java.

4. **Implement retry logic.** SMTP servers can have temporary failures. Retry 2 to 3 times with exponential backoff before giving up.

5. **Set timeouts on SMTP connections.** Without timeouts, a hung SMTP server can block your thread forever. Always configure `connectiontimeout`, `timeout`, and `writetimeout`.

6. **Log email failures.** Since async emails run in background threads, failures can go unnoticed. Always log errors and consider alerting your monitoring system.

7. **Use a dedicated email service in production.** Gmail has sending limits (500 emails per day). For production, use services like SendGrid, Amazon SES, or Mailgun.

8. **Validate email addresses before sending.** Use a simple regex or a library to check that the email format is valid before attempting to send.

---

## Quick Summary

In this chapter, you learned how to send emails from a Spring Boot application. You started with the basics of SMTP and configured Gmail as your email provider. You sent plain text emails using `SimpleMailMessage` and rich HTML emails using `MimeMessage`. You used Thymeleaf templates to separate your email designs from your Java code. You made email sending asynchronous with `@Async` so users do not have to wait. Finally, you built a complete email verification flow that real applications use.

---

## Key Points

| Concept | Description |
|---|---|
| `spring-boot-starter-mail` | Adds email support to your Spring Boot application |
| SMTP | The protocol used to send emails (port 587 with TLS) |
| `JavaMailSender` | Spring's main interface for sending emails |
| `SimpleMailMessage` | For plain text emails |
| `MimeMessage` | For HTML emails, attachments, and inline images |
| `MimeMessageHelper` | Utility class that simplifies working with MimeMessage |
| Thymeleaf Templates | HTML files with placeholders for dynamic content |
| `@Async` | Runs a method in a background thread |
| `@EnableAsync` | Enables async processing in the application |
| Verification Token | A random UUID sent in the email to verify ownership |
| App Password | A special Gmail password for third-party applications |

---

## Practice Questions

1. What is the difference between `SimpleMailMessage` and `MimeMessage`? When would you use each one?

2. Why should you send emails asynchronously instead of synchronously? What happens to the user experience if you send emails synchronously?

3. What does the `@Async` annotation do, and why does it not work when you call the annotated method from the same class?

4. Explain the purpose of each SMTP configuration property: `spring.mail.host`, `spring.mail.port`, `spring.mail.properties.mail.smtp.starttls.enable`.

5. In the email verification flow, why do we set an expiration time on the verification token? What security problem would occur without it?

---

## Exercises

### Exercise 1: Order Confirmation Email

Create a Thymeleaf email template for an order confirmation. The template should display:
- Customer name
- Order number
- A list of ordered items with quantities and prices
- The total price
- An estimated delivery date

Create a service that populates this template and sends it.

### Exercise 2: Password Reset Flow

Build a complete password reset flow:
1. User submits their email to `/api/auth/forgot-password`.
2. The app generates a token, saves it, and sends a reset email.
3. User clicks the link and submits a new password to `/api/auth/reset-password`.
4. The app verifies the token, updates the password, and invalidates the token.

Make sure the token expires after 30 minutes.

### Exercise 3: Email Sending Dashboard

Create a REST endpoint that tracks all sent emails. Store each sent email's recipient, subject, status (sent/failed), timestamp, and number of retry attempts in the H2 database. Create endpoints to:
- GET `/api/emails/history` - List all sent emails with pagination.
- GET `/api/emails/stats` - Return counts of sent and failed emails.

---

## What Is Next?

You can now send emails from your Spring Boot application. But how do you know your code actually works? How do you make sure it keeps working as you add new features? In the next chapter, we will learn about **Testing**. You will discover how to write unit tests, integration tests, and API tests that give you confidence your application works correctly. Testing is not optional in professional development. It is what separates hobby projects from production-ready applications.
