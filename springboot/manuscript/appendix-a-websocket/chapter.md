# Appendix A: Real-Time Communication with WebSocket

## What You Will Learn

- What WebSocket is and how it differs from HTTP.
- Why WebSocket matters for real-time applications.
- What the STOMP protocol is and why Spring uses it.
- How to enable WebSocket support in Spring Boot.
- How to use @MessageMapping and @SendTo to handle messages.
- How to use SimpMessagingTemplate to send messages from anywhere in your code.
- How to build an HTML and JavaScript client that connects to your WebSocket server.
- How to build a live notification system.

## Why This Chapter Matters

Imagine you are waiting for an important package. You have two choices. You could call the delivery company every five minutes and ask, "Is my package here yet?" That would be exhausting and wasteful. Or you could give them your phone number and say, "Call me when it arrives." That is much better.

Traditional HTTP works like the first approach. The browser keeps asking the server, "Any updates?" over and over. WebSocket works like the second approach. The server can call the browser whenever something happens. No repeated asking. No wasted effort.

If you want to build chat applications, live dashboards, real-time notifications, or collaborative tools, you need WebSocket. This appendix teaches you how to use WebSocket with Spring Boot so your applications can communicate in real time.

---

## A.1 The Problem with HTTP for Real-Time Communication

In Chapters 9 and 10, you learned about REST APIs. The browser sends a request, and the server sends back a response. This is called the **request-response** model.

```
HTTP Request-Response Model:

Browser                          Server
  |                                |
  |--- GET /api/notifications ---->|
  |<--- Response: [] --------------|
  |                                |
  |   (5 seconds later)            |
  |--- GET /api/notifications ---->|
  |<--- Response: [] --------------|
  |                                |
  |   (5 seconds later)            |
  |--- GET /api/notifications ---->|
  |<--- Response: [1 new] ---------|
  |                                |
```

This approach is called **polling**. The browser asks the server repeatedly. There are two problems with polling:

1. **Wasted resources.** Most of the time, the server has nothing new. But the browser keeps asking anyway. This wastes bandwidth, server processing power, and battery life on mobile devices.

2. **Delays.** If you poll every 5 seconds, a notification that arrives 1 second after a poll will not reach the user for another 4 seconds. For a chat app, that delay is unacceptable.

Think of polling like a child in the back seat asking, "Are we there yet?" every 30 seconds. It is annoying for everyone, and the answer is usually "No."

---

## A.2 What Is WebSocket?

**WebSocket** is a communication protocol that provides a **persistent, two-way connection** between the browser and the server.

> **Protocol**: A set of rules that two systems follow to communicate with each other. HTTP is a protocol. WebSocket is a different protocol.

With WebSocket, the browser and server open a connection once, and that connection stays open. Either side can send messages at any time without waiting for the other to ask.

```
WebSocket Model:

Browser                          Server
  |                                |
  |--- WebSocket Handshake ------->|
  |<--- Connection Established ----|
  |                                |
  |   (connection stays open)      |
  |                                |
  |<--- Message: "New order!" -----|
  |                                |
  |--- Message: "Got it" --------->|
  |                                |
  |<--- Message: "User joined" ----|
  |                                |
```

### HTTP vs WebSocket: A Comparison

| Feature | HTTP | WebSocket |
|---|---|---|
| Connection | Opens and closes for each request | Opens once, stays open |
| Direction | Client asks, server answers | Both can send anytime |
| Overhead | Headers sent with every request | Headers only during handshake |
| Best for | Loading pages, REST APIs | Chat, live updates, games |
| Analogy | Sending letters back and forth | Having a phone call |

### The Phone Call Analogy

HTTP is like sending letters. You write a letter (request), put it in the mailbox, wait for a reply, read the reply, and repeat. Every letter needs an envelope, a stamp, and an address. That is a lot of overhead.

WebSocket is like a phone call. You dial once (handshake), the connection opens, and then you can talk back and forth freely. No envelopes, no stamps, no waiting for the mail carrier. When you are done, you hang up.

```
Letters (HTTP):
  You ----[envelope + letter]----> Friend
  You <---[envelope + reply]------ Friend
  You ----[envelope + letter]----> Friend
  You <---[envelope + reply]------ Friend
  (each exchange needs a new envelope)

Phone Call (WebSocket):
  You ----[dial]----> Friend
  You: "Hey!"
  Friend: "Hi there!"
  You: "What's up?"
  Friend: "Not much."
  (one connection, many messages)
```

---

## A.3 How WebSocket Works Under the Hood

WebSocket starts with an HTTP request. The browser sends a special HTTP request called an **upgrade request** that says, "I want to switch from HTTP to WebSocket." If the server supports WebSocket, it agrees, and the connection upgrades.

```
WebSocket Connection Lifecycle:

1. HANDSHAKE (uses HTTP)
   Browser: "Hey server, can we switch to WebSocket?"
   Server:  "Sure, switching now."

2. OPEN CONNECTION
   Both sides can send messages freely.
   Messages are small frames, not full HTTP requests.

3. COMMUNICATION
   Browser --> Server: messages
   Server --> Browser: messages
   (no headers, no overhead, just data)

4. CLOSE
   Either side: "I'm done. Closing connection."
   Connection closes cleanly.
```

The handshake uses HTTP, so WebSocket works with existing web infrastructure like firewalls and proxies. After the handshake, the protocol switches to WebSocket, which is much lighter than HTTP.

---

## A.4 What Is STOMP?

Raw WebSocket is like a blank phone call. You can say anything, but there are no rules about the format of your messages. In a real application, you need structure.

**STOMP** stands for **Simple Text Oriented Messaging Protocol**. It adds structure to WebSocket messages, like adding a topic and format to a conversation.

> **STOMP**: A simple messaging protocol that works on top of WebSocket. It defines commands like CONNECT, SEND, SUBSCRIBE, and MESSAGE.

Think of STOMP like this. Raw WebSocket is like an open phone line where anyone can say anything. STOMP is like a walkie-talkie system with channels. You tune into channel 5 to hear weather updates, channel 7 for traffic updates, and channel 10 for emergency alerts. Each message has a clear destination and purpose.

```
Without STOMP (raw WebSocket):
  "new notification for user 42"
  (What does this mean? Who should get it? What format?)

With STOMP:
  DESTINATION: /topic/notifications
  CONTENT-TYPE: application/json
  BODY: {"message": "New order received", "userId": 42}
  (Clear destination, clear format, easy to handle)
```

Spring Boot uses STOMP because it provides:

1. **Destinations** - Messages go to specific topics (like channels).
2. **Subscriptions** - Clients subscribe to topics they care about.
3. **Message format** - Messages have headers and a body, just like HTTP.
4. **Built-in support** - Spring has excellent STOMP integration.

---

## A.5 Setting Up WebSocket in Spring Boot

Let us build a real-time notification system step by step. First, create a new Spring Boot project or add WebSocket to an existing one.

### Step 1: Add the Dependency

Open your `pom.xml` and add the WebSocket starter:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-websocket</artifactId>
</dependency>
```

This single dependency brings in everything you need for WebSocket support with STOMP.

### Step 2: Configure WebSocket

Create a configuration class that enables WebSocket messaging:

```java
package com.example.websocketdemo.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.messaging.simp.config.MessageBrokerRegistry;
import org.springframework.web.socket.config.annotation.EnableWebSocketMessageBroker;
import org.springframework.web.socket.config.annotation.StompEndpointRegistry;
import org.springframework.web.socket.config.annotation.WebSocketMessageBrokerConfigurer;

@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {

    @Override
    public void configureMessageBroker(MessageBrokerRegistry config) {
        config.enableSimpleBroker("/topic");
        config.setApplicationDestinationPrefixes("/app");
    }

    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        registry.addEndpoint("/ws").withSockJS();
    }
}
```

**Output when the application starts:**

```
INFO  --- WebSocket STOMP endpoint registered: /ws
INFO  --- Simple message broker started: [/topic]
```

**Line-by-line explanation:**

- `@Configuration` tells Spring this class contains configuration settings.
- `@EnableWebSocketMessageBroker` enables WebSocket message handling with STOMP support. This is the key annotation that activates the entire WebSocket infrastructure.
- `WebSocketMessageBrokerConfigurer` is an interface that provides methods to customize WebSocket behavior.
- `configureMessageBroker(MessageBrokerRegistry config)` sets up the message routing rules.
- `config.enableSimpleBroker("/topic")` creates an in-memory message broker. Any message sent to a destination starting with `/topic` will be forwarded to all subscribed clients. Think of this as creating a bulletin board that anyone can read.
- `config.setApplicationDestinationPrefixes("/app")` sets a prefix for messages that go to your controller methods. When a client sends a message to `/app/something`, Spring routes it to a `@MessageMapping("/something")` method.
- `registerStompEndpoints(StompEndpointRegistry registry)` registers the URL where clients connect.
- `registry.addEndpoint("/ws")` creates a WebSocket endpoint at `/ws`. Clients will connect to `ws://localhost:8080/ws`.
- `.withSockJS()` enables SockJS fallback. If a browser does not support WebSocket (rare today), SockJS uses HTTP polling as a backup.

```
Message Routing:

Client sends to /app/notify
       |
       v
  +--------------------+
  | @MessageMapping    |
  | ("/notify")        |
  | Controller method  |
  +--------------------+
       |
       v
  Sends to /topic/notifications
       |
       v
  +--------------------+
  | Simple Broker      |
  | /topic/*           |
  +--------------------+
       |
       v
  All subscribed clients receive the message
```

---

## A.6 Creating a WebSocket Controller

Now create a controller that handles incoming WebSocket messages:

```java
package com.example.websocketdemo.controller;

import com.example.websocketdemo.model.Notification;
import com.example.websocketdemo.model.NotificationRequest;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.SendTo;
import org.springframework.stereotype.Controller;

import java.time.LocalDateTime;

@Controller
public class NotificationController {

    @MessageMapping("/notify")
    @SendTo("/topic/notifications")
    public Notification sendNotification(NotificationRequest request) {
        return new Notification(
            request.getMessage(),
            request.getSender(),
            LocalDateTime.now().toString()
        );
    }
}
```

**Line-by-line explanation:**

- `@Controller` marks this as a Spring controller. Note that we use `@Controller` here, not `@RestController`. WebSocket controllers use `@Controller`.
- `@MessageMapping("/notify")` maps this method to receive messages sent to `/app/notify`. Remember, the `/app` prefix was set in our configuration. The client sends to `/app/notify`, and Spring strips the prefix and matches `/notify`.
- `@SendTo("/topic/notifications")` sends the return value of this method to `/topic/notifications`. All clients subscribed to that topic will receive the message.
- `NotificationRequest request` is the incoming message from the client. Spring automatically converts the JSON message to this Java object using Jackson (just like REST controllers).
- The method creates a new `Notification` object with the message, sender, and current timestamp, then returns it. The returned object is automatically converted to JSON and broadcast to all subscribers.

### The Model Classes

Create the request and response classes:

```java
package com.example.websocketdemo.model;

public class NotificationRequest {

    private String message;
    private String sender;

    public NotificationRequest() {
    }

    public NotificationRequest(String message, String sender) {
        this.message = message;
        this.sender = sender;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public String getSender() {
        return sender;
    }

    public void setSender(String sender) {
        this.sender = sender;
    }
}
```

```java
package com.example.websocketdemo.model;

public class Notification {

    private String message;
    private String sender;
    private String timestamp;

    public Notification() {
    }

    public Notification(String message, String sender, String timestamp) {
        this.message = message;
        this.sender = sender;
        this.timestamp = timestamp;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public String getSender() {
        return sender;
    }

    public void setSender(String sender) {
        this.sender = sender;
    }

    public String getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(String timestamp) {
        this.timestamp = timestamp;
    }
}
```

---

## A.7 Using SimpMessagingTemplate

`@SendTo` is great when you want to broadcast the result of a message handler. But what if you want to send a message from a service class, a scheduled task, or a REST controller? That is where `SimpMessagingTemplate` comes in.

`SimpMessagingTemplate` lets you send WebSocket messages from **anywhere** in your application.

```java
package com.example.websocketdemo.service;

import com.example.websocketdemo.model.Notification;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Service
public class NotificationService {

    private final SimpMessagingTemplate messagingTemplate;

    public NotificationService(SimpMessagingTemplate messagingTemplate) {
        this.messagingTemplate = messagingTemplate;
    }

    public void sendGlobalNotification(String message) {
        Notification notification = new Notification(
            message,
            "System",
            LocalDateTime.now().toString()
        );
        messagingTemplate.convertAndSend(
            "/topic/notifications", notification
        );
    }

    public void sendToUser(String username, String message) {
        Notification notification = new Notification(
            message,
            "System",
            LocalDateTime.now().toString()
        );
        messagingTemplate.convertAndSendToUser(
            username,
            "/queue/private",
            notification
        );
    }
}
```

**Line-by-line explanation:**

- `SimpMessagingTemplate messagingTemplate` is injected by Spring. It is automatically available when you enable WebSocket message broker support.
- `messagingTemplate.convertAndSend("/topic/notifications", notification)` converts the `Notification` object to JSON and sends it to all clients subscribed to `/topic/notifications`. Think of this as posting a message on the bulletin board.
- `messagingTemplate.convertAndSendToUser(username, "/queue/private", notification)` sends a message to a specific user only. The actual destination becomes `/user/{username}/queue/private`. Think of this as sending a private note instead of posting on the bulletin board.

### Using SimpMessagingTemplate from a REST Controller

Here is how you might trigger a WebSocket notification from a regular REST endpoint:

```java
package com.example.websocketdemo.controller;

import com.example.websocketdemo.service.NotificationService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/notifications")
public class NotificationRestController {

    private final NotificationService notificationService;

    public NotificationRestController(NotificationService notificationService) {
        this.notificationService = notificationService;
    }

    @PostMapping
    public ResponseEntity<String> triggerNotification(
            @RequestBody Map<String, String> payload) {

        String message = payload.get("message");
        notificationService.sendGlobalNotification(message);

        return ResponseEntity.ok("Notification sent to all connected clients");
    }
}
```

**Output when you call POST /api/notifications:**

```
HTTP/1.1 200 OK
Content-Type: text/plain

Notification sent to all connected clients
```

And every connected WebSocket client receives:

```json
{
    "message": "Server maintenance at 10 PM",
    "sender": "System",
    "timestamp": "2024-01-15T14:30:00.123456"
}
```

```
How SimpMessagingTemplate Works:

  REST Controller          WebSocket Clients
  (POST /api/notifications)
       |
       v
  NotificationService
       |
       | messagingTemplate.convertAndSend(...)
       v
  +-------------------+
  | Message Broker    |
  | /topic/*          |
  +-------------------+
       |         |         |
       v         v         v
  Client A   Client B   Client C
  (browser)  (browser)  (browser)
```

---

## A.8 Building the HTML and JavaScript Client

Now let us build a web page that connects to our WebSocket server. Create this file at `src/main/resources/static/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebSocket Notification Demo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 700px;
            margin: 40px auto;
            padding: 0 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
        }
        .status {
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-weight: bold;
        }
        .connected {
            background-color: #d4edda;
            color: #155724;
        }
        .disconnected {
            background-color: #f8d7da;
            color: #721c24;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"] {
            width: 100%;
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
        }
        button {
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            margin-right: 10px;
        }
        .btn-connect {
            background-color: #28a745;
            color: white;
        }
        .btn-disconnect {
            background-color: #dc3545;
            color: white;
        }
        .btn-send {
            background-color: #007bff;
            color: white;
        }
        .notification-list {
            list-style: none;
            padding: 0;
        }
        .notification-item {
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
            border-left: 4px solid #007bff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .notification-sender {
            font-weight: bold;
            color: #007bff;
        }
        .notification-time {
            color: #999;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <h1>Live Notification System</h1>

    <div id="status" class="status disconnected">
        Disconnected
    </div>

    <div class="form-group">
        <label for="name">Your Name:</label>
        <input type="text" id="name" placeholder="Enter your name">
    </div>

    <div class="form-group">
        <label for="message">Message:</label>
        <input type="text" id="message" placeholder="Enter a notification message">
    </div>

    <div>
        <button class="btn-connect" onclick="connect()">Connect</button>
        <button class="btn-disconnect" onclick="disconnect()">Disconnect</button>
        <button class="btn-send" onclick="sendNotification()">Send</button>
    </div>

    <h2>Notifications</h2>
    <ul id="notifications" class="notification-list"></ul>

    <!-- SockJS and STOMP libraries -->
    <script src="https://cdn.jsdelivr.net/npm/sockjs-client@1/dist/sockjs.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/stomp.js/2.3.3/stomp.min.js"></script>

    <script>
        let stompClient = null;

        function connect() {
            // Step 1: Create a SockJS connection to our /ws endpoint
            const socket = new SockJS('/ws');

            // Step 2: Create a STOMP client over the SockJS connection
            stompClient = Stomp.over(socket);

            // Step 3: Connect to the server
            stompClient.connect({}, function (frame) {
                // This runs when the connection is established
                console.log('Connected: ' + frame);
                updateStatus(true);

                // Step 4: Subscribe to the /topic/notifications topic
                stompClient.subscribe(
                    '/topic/notifications',
                    function (message) {
                        // This runs whenever a notification arrives
                        const notification = JSON.parse(message.body);
                        showNotification(notification);
                    }
                );
            });
        }

        function disconnect() {
            if (stompClient !== null) {
                stompClient.disconnect();
            }
            updateStatus(false);
            console.log('Disconnected');
        }

        function sendNotification() {
            const name = document.getElementById('name').value;
            const message = document.getElementById('message').value;

            if (!name || !message) {
                alert('Please enter both name and message');
                return;
            }

            // Send a message to /app/notify
            stompClient.send(
                '/app/notify',
                {},
                JSON.stringify({
                    'sender': name,
                    'message': message
                })
            );

            // Clear the message input
            document.getElementById('message').value = '';
        }

        function showNotification(notification) {
            const list = document.getElementById('notifications');
            const item = document.createElement('li');
            item.className = 'notification-item';
            item.innerHTML =
                '<span class="notification-sender">'
                + notification.sender + '</span>: '
                + notification.message
                + '<br><span class="notification-time">'
                + notification.timestamp + '</span>';

            // Add new notifications at the top
            list.insertBefore(item, list.firstChild);
        }

        function updateStatus(connected) {
            const status = document.getElementById('status');
            if (connected) {
                status.textContent = 'Connected';
                status.className = 'status connected';
            } else {
                status.textContent = 'Disconnected';
                status.className = 'status disconnected';
            }
        }
    </script>
</body>
</html>
```

**Line-by-line explanation of the JavaScript:**

- `new SockJS('/ws')` creates a connection to our WebSocket endpoint. SockJS is a library that provides WebSocket-like behavior with fallbacks for older browsers.
- `Stomp.over(socket)` wraps the SockJS connection with the STOMP protocol. Now we can use STOMP commands like SUBSCRIBE and SEND.
- `stompClient.connect({}, callback)` connects to the STOMP server. The first argument `{}` is for headers (empty here). The second argument is a callback that runs when the connection succeeds.
- `stompClient.subscribe('/topic/notifications', callback)` subscribes to the notifications topic. Whenever a message arrives at this topic, the callback function runs.
- `JSON.parse(message.body)` converts the incoming JSON string to a JavaScript object.
- `stompClient.send('/app/notify', {}, JSON.stringify({...}))` sends a STOMP message to the server. The destination `/app/notify` maps to our `@MessageMapping("/notify")` controller method. The second argument `{}` is for headers. The third argument is the JSON message body.
- `stompClient.disconnect()` cleanly closes the WebSocket connection.

### Running the Application

Start your Spring Boot application and open `http://localhost:8080` in two or more browser windows. Here is what happens:

1. Click "Connect" in both windows. The status changes to "Connected."
2. In Window 1, enter your name and a message, then click "Send."
3. Both Window 1 and Window 2 instantly display the notification.

```
How the Live Demo Works:

Window 1 (Browser)                Server                Window 2 (Browser)
     |                              |                        |
     |-- connect to /ws ----------->|                        |
     |<-- connected ----------------|                        |
     |-- subscribe /topic/notif --->|                        |
     |                              |                        |
     |                              |<-- connect to /ws -----|
     |                              |--- connected --------->|
     |                              |<-- subscribe /topic/ --|
     |                              |                        |
     |-- send /app/notify --------->|                        |
     |   {sender: "Alice",          |                        |
     |    message: "Hello!"}        |                        |
     |                              |                        |
     |   @MessageMapping runs       |                        |
     |   @SendTo broadcasts         |                        |
     |                              |                        |
     |<-- notification -------------|--- notification ------>|
     |   {sender: "Alice",          |   {sender: "Alice",    |
     |    message: "Hello!",        |    message: "Hello!",  |
     |    timestamp: "..."}         |    timestamp: "..."}   |
     |                              |                        |
```

---

## A.9 Building a Live Notification Example with Scheduled Updates

Let us make the notification system more interesting. We will add a scheduled task that sends automatic notifications to all connected clients every 30 seconds.

```java
package com.example.websocketdemo.service;

import com.example.websocketdemo.model.Notification;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.concurrent.atomic.AtomicInteger;

@Service
public class ScheduledNotificationService {

    private final SimpMessagingTemplate messagingTemplate;
    private final AtomicInteger activeUsers = new AtomicInteger(0);

    public ScheduledNotificationService(
            SimpMessagingTemplate messagingTemplate) {
        this.messagingTemplate = messagingTemplate;
    }

    @Scheduled(fixedRate = 30000)
    public void sendPeriodicUpdate() {
        String time = LocalDateTime.now()
            .format(DateTimeFormatter.ofPattern("HH:mm:ss"));

        Notification notification = new Notification(
            "Server heartbeat at " + time
                + ". Active connections: " + activeUsers.get(),
            "System",
            LocalDateTime.now().toString()
        );

        messagingTemplate.convertAndSend(
            "/topic/notifications", notification
        );
    }

    public void userConnected() {
        activeUsers.incrementAndGet();
    }

    public void userDisconnected() {
        activeUsers.decrementAndGet();
    }
}
```

To track connections and disconnections, add an event listener:

```java
package com.example.websocketdemo.config;

import com.example.websocketdemo.service.ScheduledNotificationService;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.messaging.SessionConnectedEvent;
import org.springframework.web.socket.messaging.SessionDisconnectEvent;

@Component
public class WebSocketEventListener {

    private final ScheduledNotificationService notificationService;

    public WebSocketEventListener(
            ScheduledNotificationService notificationService) {
        this.notificationService = notificationService;
    }

    @EventListener
    public void handleWebSocketConnect(SessionConnectedEvent event) {
        System.out.println("New WebSocket connection established");
        notificationService.userConnected();
    }

    @EventListener
    public void handleWebSocketDisconnect(SessionDisconnectEvent event) {
        System.out.println("WebSocket connection closed");
        notificationService.userDisconnected();
    }
}
```

**Output in the server console when clients connect and disconnect:**

```
New WebSocket connection established
New WebSocket connection established
WebSocket connection closed
```

**Line-by-line explanation:**

- `@EventListener` tells Spring to call this method when a specific event occurs. Spring's WebSocket support publishes events when clients connect and disconnect.
- `SessionConnectedEvent` is fired when a WebSocket client successfully connects via STOMP.
- `SessionDisconnectEvent` is fired when a WebSocket client disconnects (closes browser, loses network, or calls disconnect).
- `AtomicInteger` is used for thread-safe counting because multiple clients can connect and disconnect at the same time.

Do not forget to enable scheduling in your main application class:

```java
package com.example.websocketdemo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class WebSocketDemoApplication {

    public static void main(String[] args) {
        SpringApplication.run(WebSocketDemoApplication.class, args);
    }
}
```

---

## A.10 Complete Project Structure

Here is the final project structure:

```
websocket-demo/
+-- src/
|   +-- main/
|   |   +-- java/com/example/websocketdemo/
|   |   |   +-- WebSocketDemoApplication.java
|   |   |   +-- config/
|   |   |   |   +-- WebSocketConfig.java
|   |   |   |   +-- WebSocketEventListener.java
|   |   |   +-- controller/
|   |   |   |   +-- NotificationController.java
|   |   |   |   +-- NotificationRestController.java
|   |   |   +-- model/
|   |   |   |   +-- Notification.java
|   |   |   |   +-- NotificationRequest.java
|   |   |   +-- service/
|   |   |       +-- NotificationService.java
|   |   |       +-- ScheduledNotificationService.java
|   |   +-- resources/
|   |       +-- static/
|   |       |   +-- index.html
|   |       +-- application.properties
|   +-- test/
|       +-- java/com/example/websocketdemo/
|           +-- WebSocketDemoApplicationTests.java
+-- pom.xml
```

Your `application.properties` can remain simple:

```properties
spring.application.name=websocket-demo
```

---

## Common Mistakes

1. **Using @RestController instead of @Controller for WebSocket handlers.** WebSocket message-handling methods with `@MessageMapping` should be in a class annotated with `@Controller`, not `@RestController`. The `@RestController` annotation adds `@ResponseBody`, which interferes with WebSocket message handling.

2. **Forgetting the /app prefix when sending from the client.** If your application destination prefix is `/app`, the client must send to `/app/notify`, not just `/notify`. But in `@MessageMapping`, you use `/notify` without the prefix.

3. **Not including SockJS and STOMP JavaScript libraries.** The HTML client needs both the SockJS and STOMP.js libraries to connect. Without them, the connection will fail.

4. **Mixing up /topic and /queue.** Use `/topic` for broadcasting messages to all subscribers (like a radio station). Use `/queue` for sending messages to a specific user (like a private message).

5. **Forgetting @EnableWebSocketMessageBroker.** Without this annotation, Spring will not set up the WebSocket infrastructure, and nothing will work.

6. **Forgetting @EnableScheduling when using scheduled notifications.** The `@Scheduled` annotation does nothing unless you add `@EnableScheduling` to your configuration or main application class.

---

## Best Practices

1. **Use SockJS fallback.** Always add `.withSockJS()` to your endpoint registration. This ensures your application works even in environments where raw WebSocket connections are blocked.

2. **Keep WebSocket messages small.** WebSocket is designed for lightweight, frequent messages. If you need to transfer large files, use HTTP instead.

3. **Handle disconnections gracefully.** Clients can disconnect unexpectedly (browser crash, network loss). Use event listeners to clean up resources when clients disconnect.

4. **Use SimpMessagingTemplate for server-initiated messages.** When you need to push messages from background tasks, services, or scheduled jobs, use `SimpMessagingTemplate` instead of trying to use `@SendTo`.

5. **Consider security.** In production, secure your WebSocket endpoints with authentication. Spring Security integrates with WebSocket to protect your connections.

6. **Use an external message broker for production.** The simple in-memory broker is fine for development and small applications. For production with many users, consider using RabbitMQ or ActiveMQ as the message broker.

---

## Quick Summary

WebSocket provides a persistent, two-way connection between the browser and server. Unlike HTTP (which is like sending letters), WebSocket is like a phone call where both sides can talk at any time. Spring Boot uses the STOMP protocol on top of WebSocket to add structure to messages with topics and subscriptions. You enable WebSocket with `@EnableWebSocketMessageBroker`, handle incoming messages with `@MessageMapping`, broadcast results with `@SendTo`, and send messages from anywhere using `SimpMessagingTemplate`. The JavaScript client uses the SockJS and STOMP.js libraries to connect, subscribe to topics, and send and receive messages.

---

## Key Points

- HTTP is request-response (one-way at a time). WebSocket is full-duplex (both ways simultaneously).
- WebSocket starts with an HTTP handshake, then upgrades to the WebSocket protocol.
- STOMP adds structure (destinations, subscriptions, headers) on top of raw WebSocket.
- `@EnableWebSocketMessageBroker` activates WebSocket support in Spring Boot.
- `@MessageMapping` handles incoming WebSocket messages (like `@RequestMapping` for HTTP).
- `@SendTo` broadcasts the return value to a topic.
- `SimpMessagingTemplate` sends WebSocket messages from any part of your application.
- SockJS provides a fallback when WebSocket is not available.
- Use `/topic` for broadcasting and `/queue` for private messages.

---

## Practice Questions

1. What is the main difference between HTTP and WebSocket communication? Give a real-life analogy.

2. Why does Spring Boot use the STOMP protocol on top of WebSocket instead of using raw WebSocket?

3. What is the purpose of `@EnableWebSocketMessageBroker` and what happens if you forget it?

4. Explain the difference between `@SendTo` and `SimpMessagingTemplate`. When would you use each one?

5. A developer sends a message from the JavaScript client to `/notify` but the server never receives it. The `@MessageMapping` method is mapped to `/notify` and the application prefix is `/app`. What is wrong?

---

## Exercises

### Exercise 1: Build a Chat Room

Modify the notification example to build a simple chat room. Add a "room" field to the message so users can join different rooms. Use `@DestinationVariable` to route messages to room-specific topics like `/topic/chat/{roomName}`. Test with two browser windows in the same room and two in a different room.

### Exercise 2: Add a Typing Indicator

Add a "typing indicator" feature. When a user starts typing in the message field, send a WebSocket message to notify other users. Display "User X is typing..." below the notification list. The indicator should disappear after 3 seconds of no typing.

### Exercise 3: Server-Sent Notifications from REST

Create a REST endpoint `POST /api/admin/broadcast` that accepts a JSON body with a `message` field. When called (for example, from Postman), it should send the message to all connected WebSocket clients. This simulates an admin sending a system-wide announcement.

---

## What Is Next?

Now that you understand real-time communication with WebSocket, you are ready for Appendix B where you will build a complete project from scratch. The TaskTracker API combines everything you have learned in this book into one comprehensive application.
